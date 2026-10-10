"""Scene checks S1–S6 on the built Blender scene (docs/milestone12.md §4.6, §4.7, contract §13.2; owner: track S).

Contract (frozen 10 Oct 2026):

- ``CHECKS``: ``("S1", ..., "S6")``; ``TOLERANCES``: the numbers of §4.6/§4.7 (metres, degrees).
- ``run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict``: runs inside Blender after the
  furniture and decor are built (``build.py`` calls it once per level); ``scene_objects``: ``{piece or decor id:
  bpy object}``; writes ``checks/scene.json`` (``out_path``) and returns ``{"violations": [Violation],
  "counts": {...}, "measured": {id: {...}}}``. A decor item that fails S5 after one re-placement is not built
  (``decor_not_rested``); a built item that fails S5 fails the build.
- ``measure_pure(meshes: dict, building: dict) -> dict``: the same measurements on plain triangle meshes (pure
  Python ray caster) for the CPU tests.
"""
from __future__ import annotations

CHECKS: tuple[str, ...] = ("S1", "S2", "S3", "S4", "S5", "S6")
TOLERANCES: dict[str, float] = {"floor_gap_m": 0.010, "floor_sink_m": 0.005, "overlap_m": 0.010, "front_deg": 10.0,
                                "size_rel": 0.15, "decor_gap_m": 0.010, "decor_pen_hard_m": 0.010,
                                "decor_pen_soft_m": 0.030, "decor_support_share": 0.80}


def run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict:
    return {"violations": [], "counts": {}, "measured": {}}      # stub (lead)


def measure_pure(meshes: dict, building: dict) -> dict:
    return {}                                                     # stub (lead)
