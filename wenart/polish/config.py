"""Load ``polish.yaml`` (docs/milestone5.md §1.6, §3) and turn its ladder and grids into attempt lists.

Default paths resolve relative to this package, never to the cwd (§1.1).
``models.controlnet.config_dir`` is relative to ``wenart/polish``;
``config_dir(cfg)`` gives the absolute folder.

An attempt is ``{"role", "strength", "control", "scale", "size", "mode"}``:
``role`` ladder (run), grid or presumed_bad (sweep, smoke); ``control`` one of
depth / canny / geometry, or None only for presumed_bad (img2img without
ControlNet, ``scale`` None); ``size`` native or WxH (multiples of 16);
``mode`` plain or anchor (anchor needs a control). ``attempts_from`` checks
every field, so a typo in a grid file stops the run before any GPU work.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

POLISH_DIR = Path(__file__).resolve().parent
CONFIG_PATH = POLISH_DIR / "polish.yaml"
POLISH_CODE_VERSION = "m5.1"            # part of every attempt key; bump when the polish maths change
CONTROL_TYPES = ("depth", "canny", "geometry")
MODES = ("plain", "anchor")
ROLES = ("ladder", "grid", "presumed_bad")
ATTEMPT_FIELDS = ("strength", "control", "scale", "size", "mode")


def load_config(path: Optional[str | Path] = None) -> dict:
    """The polish config as a dict (``polish.yaml`` of this package when ``path`` is None)."""
    import yaml
    with open(CONFIG_PATH if path is None else path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def config_dir(cfg: dict) -> Path:
    """Absolute folder of the vendored ControlNet config (``models.controlnet.config_dir``)."""
    rel = Path(cfg["models"]["controlnet"]["config_dir"])
    return rel if rel.is_absolute() else POLISH_DIR / rel


def controlnet_config_sha256(cfg: dict) -> str:
    """sha256 of the vendored ControlNet ``config.json`` (part of the attempt key)."""
    return hashlib.sha256((config_dir(cfg) / "config.json").read_bytes()).hexdigest()


def check_attempt(entry: dict, default_role: str) -> dict:
    """One normalised attempt dict; ValueError for a bad field."""
    from wenart.polish.sizing import parse_size

    a = {"role": entry.get("role") or default_role}
    for key in ATTEMPT_FIELDS:
        a[key] = entry.get(key)
    if a["role"] not in ROLES:
        raise ValueError(f"attempt {entry}: role must be one of {ROLES}")
    strength = float(a["strength"])
    if not 0.0 < strength <= 1.0:
        raise ValueError(f"attempt {entry}: strength must be in (0, 1]")
    a["strength"] = strength
    if a["control"] is None:
        if a["role"] != "presumed_bad":
            raise ValueError(f"attempt {entry}: only role presumed_bad may run without a control image")
        a["scale"] = None
    else:
        if a["control"] not in CONTROL_TYPES:
            raise ValueError(f"attempt {entry}: control must be one of {CONTROL_TYPES} or null")
        if a["scale"] is None:
            raise ValueError(f"attempt {entry}: a control image needs a scale")
        a["scale"] = float(a["scale"])
    a["size"] = "native" if a["size"] in (None, "native") else str(a["size"])
    parse_size(a["size"])
    a["mode"] = a["mode"] or "plain"
    if a["mode"] not in MODES:
        raise ValueError(f"attempt {entry}: mode must be one of {MODES}")
    if a["mode"] == "anchor" and a["control"] is None:
        raise ValueError(f"attempt {entry}: mode anchor needs a control image")
    return a


def attempts_from(entries, default_role: str) -> list[dict]:
    """Checked attempt dicts from a list of YAML entries."""
    if not isinstance(entries, list) or not entries:
        raise ValueError("an attempt list must be a non-empty list")
    return [check_attempt(e, default_role) for e in entries]


def ladder(cfg: dict) -> list[dict]:
    """The run ladder (``polish.yaml: ladder``), role ``ladder``."""
    return attempts_from(cfg["ladder"], "ladder")


def grid(cfg: dict, name_or_path: str) -> list[dict]:
    """A named grid of ``polish.yaml: grids`` or a YAML/JSON file (a list, or a dict with ``attempts``/``grid``)."""
    grids = cfg.get("grids") or {}
    if name_or_path in grids:
        return attempts_from(grids[name_or_path], "grid")
    path = Path(name_or_path)
    if not path.is_file():
        raise ValueError(f"grid {name_or_path!r}: not a grid of polish.yaml ({', '.join(grids)}) and not a file")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("attempts") or data.get("grid")
    return attempts_from(data, "grid")


def models_record(cfg: dict, gate_models: Optional[dict] = None) -> dict:
    """``{"base", "controlnet", "gate"}`` with ``{repo, revision, licence, files}`` per model (§1.6, §3.6)."""
    base = cfg["models"]["base"]
    cn = cfg["models"]["controlnet"]
    rec = {
        "base": {"repo": base["repo"], "revision": base["revision"], "licence": base["licence"],
                 "files": list(base.get("allow_patterns") or [])},
        "controlnet": {"repo": cn["repo"], "revision": cn["revision"], "licence": cn["licence"],
                       "files": list(cn.get("files") or cn.get("allow_patterns") or []),
                       "config_sha256": controlnet_config_sha256(cfg)},
        "gate": {},
    }
    for key, m in ((gate_models or {}).get("models") or {}).items():
        rec["gate"][key] = {"repo": m["repo"], "revision": m["revision"], "licence": m["licence"]}
    return rec
