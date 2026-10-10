"""The library audit and its growth scaffolding (docs/milestone12.md §6, D21-D24; Milestone 12 track B).

What: ``python -m wenart.assets audit <step>`` checks every furniture and decor model of the library
(``wenart/furniture/catalog_library.json``: ABO, Objaverse, generated; ``catalog.json``: Poly Haven) and decides per
model ``keep`` / ``fix`` / ``removed`` with the reasons; ``python -m wenart.assets growth <source> list`` writes the
lists of candidate models the user approves before anything is downloaded.

Steps (each resumable, results under ``<out>/audit/``, default ``results/library/audit/``):

- ``licences`` (U3, here): NC / SA / ND licences out of the catalogue now (user decision of 10 Oct 2026), files kept.
- ``render`` (pod P2, Blender, ``render.py``): 4 views per model at its catalogue scale with a scale reference and the
  dimensions printed, the mesh measured (``meshstats.py``); texture sets as 1 m samples with a 10 cm grid.
- ``code`` (``checks.py``): size vs the real-size table (``wenart/furniture/sizes.py``), pivot, up axis, front,
  units, mesh, textures, duplicates, licence, title words in any language (``keywords.py``). Without the render it
  checks the catalogue fields only (the CPU "dry audit").
- ``ask`` (pod P3, ``ask.py``): one vision question per model (strict JSON schema, temperature 0, the model of
  check.yaml the bake-off picks); a second pass only where code cannot confirm.
- ``decide`` (``decide.py``): keep / fix / remove with the reasons of §6.1; fixes are catalogue fields.
- ``sheets`` (``sheets.py``): one contact sheet per type with keep / fix / remove marked.
- ``gaps`` (``gaps.py``): per room type and style family the group members needed vs the kept models.
- ``write`` (``write.py``): the catalogue's ``audit`` fields and the flags ``real_product``, ``has_bedding``,
  ``has_cushions``, ``has_pillows``, ``contact`` (contract §13.3; ``catalog.usable`` reads ``audit.status``).

Why: the M8-M10 judges saw a 256 px sheet with no scale and no title; the diagnosis (§1.6) found wrong objects both
judges accepted, wrong sizes and NC/SA licences. Nothing is deleted from the volume: ``removed`` only takes a model
out of the catalogue (D22); a delete list needs the user's OK.

How: pure functions for every check and decision (CPU tests); Blender only renders and measures (``render.py`` writes
the jobs, ``blender_audit.py`` runs inside Blender); the vision step reuses the M8-M10 answer store and worker pool
(``wenart.assets.objaverse.judge_ask``). Settings in ``wenart/assets/audit.yaml``.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CONFIG_PATH = HERE.parent / "audit.yaml"
DEFAULT_OUT = REPO / "results" / "library"
AUDIT_DIR = "audit"
GROWTH_DIR = "growth"
VERSION = "m12"
STATUSES = ("keep", "fix", "removed")
EXIT_OK, EXIT_NOTHING, EXIT_SERVER, EXIT_DEADLINE = 0, 1, 2, 3


def load_config(path=None) -> dict:
    import yaml
    return yaml.safe_load(Path(path or CONFIG_PATH).read_text(encoding="utf-8")) or {}


def audit_dir(out=None) -> Path:
    return Path(out or DEFAULT_OUT) / AUDIT_DIR
