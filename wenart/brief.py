"""Project brief with its defaults (docs/milestone5.md §1.1, §6).

What: ``load_brief(project_dir)`` reads ``<project_dir>/brief.yaml`` and
fills every key the brief does not set from the ``brief:`` block of
``wenart/defaults.yaml`` (``empty_rooms``, ``decor``, ``polish``,
``style_photos``, ``ceiling_height``, ``render``; Milestone 10:
``slab_thickness``, ``furnished_rooms``, ``furnished_rooms_keep``,
``furnished_rooms_keep_size``, ``variants``, ``failed_levels``, ``site``,
``exterior``, ``render.exterior_views``, ``render.twin_rooms``). It returns
``{"values": dict, "assumed": [keys], "path": str | None, "warnings": [str]}``:

- ``values``: one dict with every brief key: the brief's own keys (also
  those the defaults do not know, such as ``style`` / ``styles``) and the
  defaults for the rest. Nested blocks (``render:``) are merged key by key.
- ``assumed``: the keys whose value came from the defaults, nested ones as
  dotted paths (``render.samples``), in the order of ``defaults.yaml``.
  Readers that use an assumed value say so in their output (CLAUDE.md:
  nothing silent).
- ``warnings``: a brief value of the wrong type (``polish: "no"``) is not
  used: the default is taken, the key is listed as assumed and the warning
  says why. A missing ``brief.yaml`` gives the defaults and one warning.
  Keys with a value rule of their own (``VALUE_RULES``) are checked by it
  instead of by the default's type: ``render.lens_mm`` (Milestone 8) is
  ``auto`` (the default: 18 mm, 16 mm in narrow rooms) or a number from 14
  to 35 (mm); anything else is reported and the default is used.

Why one loader: the brief stored in ``building.project.brief`` is the brief
at ingest/layout time and can be stale (docs/milestone5.md §1.1), so the
Milestone 5 readers (polish, vision check, report) load ``brief.yaml``
through this module, usually via ``wenart.views.project_paths``.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Optional

DEFAULTS_PATH = Path(__file__).resolve().parent / "defaults.yaml"
BRIEF_FILE = "brief.yaml"
# The brief's lens range (mm): the same as ``wenart.blender.cameras.LENS_RANGE_MM`` (tests/test_brief.py pins it).
# A copy, so the stages that read the brief (sheets, pipeline) do not import the Blender camera code.
LENS_RANGE_MM = (14.0, 35.0)


def brief_defaults(defaults: Optional[dict] = None) -> dict:
    """The ``brief:`` block of ``wenart/defaults.yaml`` (or of the given defaults dict)."""
    if defaults is None:
        import yaml  # lazy: the package imports where PyYAML is missing (Blender)
        defaults = yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8")) or {}
    return copy.deepcopy(defaults.get("brief") or {})


def _kind(value: Any) -> str:
    """Coarse YAML type of a value: bool, number, str, list, dict or none."""
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "str"
    if isinstance(value, (list, tuple)):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def _lens_problem(value: Any) -> Optional[str]:
    """``render.lens_mm``: ``auto`` or a number from 14 to 35 (mm, ``LENS_RANGE_MM``)."""
    if value == "auto":
        return None
    lo, hi = LENS_RANGE_MM
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= float(value) <= hi:
        return f"expected auto or a lens from {lo:g} to {hi:g} mm, got {value!r}"
    return None


def _one_of(*allowed: str):
    """A rule for a key that takes one word of ``allowed``."""
    def rule(value: Any) -> Optional[str]:
        if value in allowed:
            return None
        return f"expected one of {', '.join(allowed)}, got {value!r}"
    return rule


def _variants_problem(value: Any) -> Optional[str]:
    """``variants`` (Milestone 10): ``all``, ``base`` or a list of alternative names as titled."""
    if value in ("all", "base"):
        return None
    if isinstance(value, list) and value and all(isinstance(v, str) and v.strip() for v in value):
        return None
    return f"expected all, base or a list of alternative names, got {value!r}"


def _names_problem(value: Any) -> Optional[str]:
    """``furnished_rooms_keep`` (Milestone 10): a list of room ids or labels."""
    if isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value):
        return None
    return f"expected a list of room ids or labels, got {value!r}"


# Dotted keys whose value has a rule of its own (instead of the default's type): a problem text or None.
VALUE_RULES = {
    "render.lens_mm": _lens_problem,
    # Milestone 10 (docs/milestone10.md §1.3)
    "furnished_rooms": _one_of("keep", "complete"),
    "furnished_rooms_keep": _names_problem,
    "variants": _variants_problem,
    "failed_levels": _one_of("leave_out", "stop"),
    "site": _one_of("full", "ground"),
    "render.twin_rooms": _one_of("one", "all"),
}


def _merge(raw: dict, defaults: dict, prefix: str, assumed: list[str], warnings: list[str]) -> dict:
    """``raw`` over ``defaults``, recursively for dict defaults; records assumed keys and type problems."""
    values: dict = {}
    for key, default in defaults.items():
        path = f"{prefix}{key}"
        if key not in raw or raw[key] is None:
            if key in raw:
                warnings.append(f"brief.yaml {path}: empty; default {default!r} used")
            if isinstance(default, dict):
                values[key] = _merge({}, default, path + ".", assumed, warnings)
            else:
                values[key] = copy.deepcopy(default)
                assumed.append(path)
            continue
        given = raw[key]
        rule = VALUE_RULES.get(path)
        if rule is not None:
            problem = rule(given)
            if problem:
                warnings.append(f"brief.yaml {path}: {problem}; default {default!r} used")
                values[key] = copy.deepcopy(default)
                assumed.append(path)
            else:
                values[key] = copy.deepcopy(given)
            continue
        want, got = _kind(default), _kind(given)
        if want == "dict" and got == "dict":
            values[key] = _merge(given, default, path + ".", assumed, warnings)
            for extra in given:
                if extra not in default:
                    values[key][extra] = copy.deepcopy(given[extra])
            continue
        if want != "none" and want != got:
            warnings.append(f"brief.yaml {path}: expected {want}, got {got} {given!r}; default {default!r} used")
            if isinstance(default, dict):
                values[key] = _merge({}, default, path + ".", assumed, warnings)
            else:
                values[key] = copy.deepcopy(default)
                assumed.append(path)
            continue
        if want == "list" and any(not isinstance(v, str) for v in given) and key == "style_photos":
            warnings.append(f"brief.yaml {path}: expected a list of file names, got {given!r}; default "
                            f"{default!r} used")
            values[key] = copy.deepcopy(default)
            assumed.append(path)
            continue
        values[key] = copy.deepcopy(given)
    for key, given in raw.items():
        if key not in defaults:
            values[key] = copy.deepcopy(given)
    return values


def merge_brief(raw: Optional[dict], defaults: Optional[dict] = None) -> dict:
    """``{"values", "assumed", "warnings"}`` of a raw brief dict (pure; ``defaults`` = the ``brief:`` block)."""
    defaults = brief_defaults() if defaults is None else copy.deepcopy(defaults)
    warnings: list[str] = []
    if raw is not None and not isinstance(raw, dict):
        warnings.append(f"brief.yaml is not a mapping ({type(raw).__name__}); defaults used")
        raw = {}
    assumed: list[str] = []
    values = _merge(raw or {}, defaults, "", assumed, warnings)
    return {"values": values, "assumed": assumed, "warnings": warnings}


def load_brief(project_dir) -> dict:
    """``{"values", "assumed", "path", "warnings"}`` of ``<project_dir>/brief.yaml`` + the defaults.

    A missing folder or ``brief.yaml`` is not an error: every value is
    assumed and ``warnings`` says so. A YAML syntax error raises (a broken
    brief must not be silently replaced by defaults).
    """
    import yaml

    path = Path(project_dir) / BRIEF_FILE
    raw = None
    if path.is_file():
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if raw is None:
            raw = {}
    out = merge_brief(raw)
    if raw is None:
        out["warnings"].insert(0, f"no {BRIEF_FILE} in {project_dir}: every brief value is a default")
    out["path"] = str(path) if path.is_file() else None
    return {"values": out["values"], "assumed": out["assumed"], "path": out["path"], "warnings": out["warnings"]}


def value(brief: Optional[dict], key: str, default: Any = None) -> Any:
    """``brief["values"][key]`` of a ``load_brief`` result (dotted keys reach nested blocks), else ``default``."""
    cur: Any = (brief or {}).get("values") or {}
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def lens_mm(brief: Optional[dict]) -> Optional[float]:
    """The brief's ``render.lens_mm`` as a float (validated by ``load_brief``), or None for ``auto`` (the
    camera rule of ``wenart.blender.cameras.room_lens``: 18 mm, 16 mm in rooms narrower than 2.2 m)."""
    v = value(brief, "render.lens_mm", "auto")
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v)


def is_assumed(brief: Optional[dict], key: str) -> bool:
    """True when ``key`` (dotted for nested keys) came from the defaults, or when there is no brief at all."""
    if not brief:
        return True
    return key in (brief.get("assumed") or [])
