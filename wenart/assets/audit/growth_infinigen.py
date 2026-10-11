"""The Infinigen fixture test batch of pod P4 (docs/milestone12.md §6.4 D24,
``results/library/growth/plan_infinigen.json``, user OK of 11 Oct 2026; BSD-3-Clause code, the generated models are
ours).

What:

- The pinned code: ``princeton-vl/infinigen`` tag ``v1.19.0`` = commit ``01c39c7f7adcf7363ccbcc57c64410c69f4a4e7c``
  (``git ls-remote --tags``, 11 Oct 2026; a lightweight tag). Why this one: ``main`` is Infinigen 2 (package
  ``infinigen2``, ``procfunc``) where the indoor factories moved; v1.19.0 is the last v1 release and holds them in
  ``infinigen/assets/objects/`` (read at that commit: ``ToiletFactory``, ``BathtubFactory``,
  ``BathroomSinkFactory``, ``SinkFactory`` (kitchen sink with tap), ``OvenFactory``, ``BeverageFridgeFactory``,
  ``DishwasherFactory``, ``MicrowaveFactory``, ``KitchenCabinetFactory``, ``BookStackFactory``, ``BowlFactory``,
  ``PlantContainerFactory`` (a pot with a plant; ``PotFactory`` is a cooking pot)). Its ``pyproject.toml``:
  ``requires-python ==3.11.*``, ``bpy==4.2.0``, licence BSD-3-Clause; ``uv.lock`` pins the rest; docs/Installation.md:
  "Minimal install (No terrain or opengl GT, ok for Infinigen-Indoors or single-object generation)".
- ``jobs_of(plan, approved)``: one job per approved id (``infinigen_<factory>_<seed>``), seeds round robin (every
  factory's seed 0 first), so a time cap still leaves one model of each factory.
- ``factories_of(listing, sources)``: the asset factories of the commit: the official indoor list
  ``tests/assets/list_indoor_meshes.txt`` plus every ``class <Name>Factory(`` under ``infinigen/assets/objects``.
- ``match(name, type, factories)``: the wanted name -> a factory: the preferred class names above first, else the
  factory whose name words hold the wanted words (fewest extra words); none -> missing (recorded, never guessed).
- ``job_state(folder)``: done / failed (twice) / to do, from the job's ``result.json`` on the volume (resume).

Two submodules are needed at import time although the docs' minimal install does not fetch them (found by a trial in
the build session: Python 3.11.17, bpy 4.2.0, ``uv sync --frozen --no-install-project``): ``infinigen/infinigen_gpl``
@``10c1d76f`` (GPL-3.0; ``infinigen/assets/materials/__init__.py`` imports its snow surface) and ``infinigen/OcMesher``
@``bb895a01`` (BSD-3-Clause; ``infinigen/terrain/core.py``, reached through ``core.placement.camera``). They run on the
pod only; nothing of them is copied into the repo or the catalogue.

The generation itself runs in the Infinigen venv (Python 3.11, bpy 4.2.0) through ``infinigen_driver.py``, which
calls Infinigen's own ``generate_individual_assets.build_and_save_asset`` with ``--export obj`` (the documented
exporter: procedural materials baked into textures); our Blender 5.2 turns the OBJ into a GLB
(``convert_blender.py``, axes checked against the size the driver measured in Infinigen's scene).

How: pure (CPU tests); the job script does the setup (uv, Python 3.11, ``uv sync --frozen``) on the container disk.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

REPO_URL = "https://github.com/princeton-vl/infinigen"
TAG = "v1.19.0"
COMMIT = "01c39c7f7adcf7363ccbcc57c64410c69f4a4e7c"
PYTHON = "3.11"
BPY = "4.2.0"
LISTING = "tests/assets/list_indoor_meshes.txt"
OBJECTS = "infinigen/assets/objects"
MAX_ATTEMPTS = 2
# wanted name of plan_infinigen.json -> factory classes in order of preference (read at COMMIT, module docstring)
PREFERRED: dict[str, tuple[str, ...]] = {
    "toilet": ("ToiletFactory",), "bathtub": ("BathtubFactory",),
    "bathroom sink": ("BathroomSinkFactory", "StandingSinkFactory"), "kitchen sink": ("SinkFactory",),
    "oven": ("OvenFactory",), "beverage fridge": ("BeverageFridgeFactory",), "dishwasher": ("DishwasherFactory",),
    "microwave": ("MicrowaveFactory",), "kitchen cabinet": ("KitchenCabinetFactory",),
    "books": ("BookStackFactory", "BookColumnFactory", "BookFactory"), "bowl": ("BowlFactory",),
    "pot": ("PlantContainerFactory", "PlantPotFactory"),
}
_CLASS = re.compile(r"^class\s+([A-Za-z0-9_]+Factory)\s*\(", re.M)
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def words(class_name: str) -> list[str]:
    base = class_name[:-len("Factory")] if class_name.endswith("Factory") else class_name
    return [w.lower() for w in _CAMEL.split(base) if w]


def kind_of(ftype: Optional[str]) -> Optional[str]:
    from wenart.furniture import catalog as C
    if ftype is None:
        return None
    return "decor" if ftype in C.DECOR_TYPES else "furniture"


def jobs_of(plan: dict, approved_ids: list[str]) -> list[dict]:
    """The approved jobs of the plan, seeds round robin; ``type`` None = shown only (no catalogue type)."""
    rows = []
    for b in plan.get("batch") or []:
        for seed in b.get("seeds") or [0]:
            jid = f"infinigen_{slug(b['factory'])}_{int(seed)}"
            if jid in approved_ids:
                rows.append({"id": jid, "factory": b["factory"], "type": b.get("type"), "kind": kind_of(b.get("type")),
                             "seed": int(seed)})
    order = {f: i for i, f in enumerate(dict.fromkeys(r["factory"] for r in rows))}
    rows.sort(key=lambda r: (r["seed"], order[r["factory"]]))
    return rows


def factories_of(listing_text: str, sources: dict) -> dict:
    """``{class: dotted import path}``: the official indoor list (``infinigen.assets.objects.<pkg>.<Class>``) and
    every factory class of ``sources`` (``{repo-relative .py path: text}``) by module path."""
    out: dict = {}
    for line in (listing_text or "").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.setdefault(line.split(".")[-1], line)
    for rel, text in sorted(sources.items()):
        mod = rel[:-3].replace("/", ".") if rel.endswith(".py") else rel
        if mod.endswith(".__init__"):
            continue
        for cls in _CLASS.findall(text or ""):
            out.setdefault(cls, f"{mod}.{cls}")
    return dict(sorted(out.items()))


def match(name: str, factories: dict) -> Optional[dict]:
    """The factory of a wanted name: ``{"class", "dotted", "how"}`` or None."""
    for cls in PREFERRED.get(name, ()):
        if cls in factories:
            return {"class": cls, "dotted": factories[cls], "how": "preferred (read at the pinned commit)"}
    want = set(slug(name).split("_"))
    cands = []
    for cls, dotted in factories.items():
        w = set(words(cls))
        if want <= w:
            cands.append((len(w - want), ".sim_objects." in dotted, cls))
    if not cands:
        return None
    cands.sort()
    cls = cands[0][2]
    return {"class": cls, "dotted": factories[cls], "how": f"name words {sorted(want)} in {cls}"}


def job_state(folder: Path) -> str:
    """``done`` (the OBJ export and its record), ``failed`` (failed ``MAX_ATTEMPTS`` times) or ``todo``."""
    p = Path(folder) / "result.json"
    if not p.is_file():
        return "todo"
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return "todo"
    if rec.get("ok") and rec.get("obj") and Path(rec["obj"]).is_file():
        return "done"
    return "failed" if int(rec.get("attempts", 1)) >= MAX_ATTEMPTS else "todo"


def plan_jobs(plan: dict, approved_ids: list[str], factories: Optional[dict], root: Path) -> dict:
    """The jobs of the batch with their factory (when ``factories`` is given) and their state under ``root``
    (``<root>/<id>/``): ``{"jobs": [...], "todo": [ids], "done": [ids], "failed": [ids], "missing": [names]}``."""
    jobs = jobs_of(plan, approved_ids)
    missing: list = []
    matched: dict = {}
    if factories is not None:
        for name in dict.fromkeys(j["factory"] for j in jobs):
            m = match(name, factories)
            matched[name] = m
            if m is None:
                missing.append(name)
    out = {"tag": TAG, "commit": COMMIT, "jobs": [], "todo": [], "done": [], "failed": [], "missing": missing,
           "matched": matched}
    for j in jobs:
        folder = Path(root) / j["id"]
        state = job_state(folder)
        m = matched.get(j["factory"]) if factories is not None else None
        rec = dict(j, folder=str(folder), state=state)
        if m:
            rec.update({"class": m["class"], "dotted": m["dotted"]})
        out["jobs"].append(rec)
        out[state].append(j["id"])
    return out


def scan_sources(repo: Path) -> dict:
    """``{relative path: text}`` of the Python files under ``infinigen/assets/objects`` of a clone."""
    base = Path(repo)
    out = {}
    for p in sorted((base / OBJECTS).rglob("*.py")):
        try:
            out[p.relative_to(base).as_posix()] = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return out
