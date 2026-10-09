"""Code checks of the exterior and of the views, and validation of the agent's camera, exterior and material
overrides (docs/milestone11.md §4.1, §4.4, §7, contract §17.2). Pure Python (no bpy); owner: track C.

``Violation`` as in ``wenart.furniture.plausibility`` (checks X1–X8, V1, V3).
"""
from __future__ import annotations

# JSON schemas of the override entries (the agent's tool parameters); track C fills them in.
CAMERA_OVERRIDE_SCHEMA: dict = {}
EXTERIOR_OVERRIDE_SCHEMA: dict = {}
MATERIAL_OVERRIDE_SCHEMA: dict = {}


def check_exterior(building: dict, scene_manifest: dict | None = None, render_manifest: dict | None = None) -> dict:
    """``{"score": 0..100, "violations": [Violation]}`` (X1–X8)."""
    raise NotImplementedError("M11 track C")


def check_views(building: dict, render_manifest: dict) -> dict:
    """``{"views": {view_id: [Violation]}}`` (V1, V3)."""
    raise NotImplementedError("M11 track C")


def validate_camera_override(building: dict, camera: dict) -> dict:
    """``{"ok": bool, "failed": [str]}``."""
    raise NotImplementedError("M11 track C")


def validate_exterior_override(building: dict, override: dict) -> dict:
    raise NotImplementedError("M11 track C")


def validate_material_override(style: dict, override: dict) -> dict:
    raise NotImplementedError("M11 track C")
