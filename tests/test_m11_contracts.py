"""Milestone 11 contracts (docs/milestone11.md §17): the interface signatures and schema fields the three build
tracks share. Owned by the lead; a track that needs a change asks for it."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SIGNATURES = {
    "wenart.furniture.plausibility": {"score_room": ["building", "room_id"], "score_building": ["building"]},
    "wenart.furniture.edit_ops": {"apply_edit": ["building", "edit", "catalog"]},
    "wenart.furniture.groups": {"place_group": ["building", "room_id", "group", "anchor"]},
    "wenart.furniture.infer": {"infer_types": ["building"], "apply_inferences": ["building", "proposals"]},
    "wenart.blender.exterior_checks": {
        "check_exterior": ["building", "scene_manifest", "render_manifest"],
        "check_views": ["building", "render_manifest"],
        "validate_camera_override": ["building", "camera"],
        "validate_exterior_override": ["building", "override"],
        "validate_material_override": ["style", "override"]},
}
CONSTANTS = {
    "wenart.furniture.plausibility": ["CHECKS", "SEVERITIES"],
    "wenart.furniture.edit_ops": ["EDIT_OPS", "EDIT_SCHEMAS"],
    "wenart.furniture.groups": ["GROUPS"],
    "wenart.blender.exterior_checks": ["CAMERA_OVERRIDE_SCHEMA", "EXTERIOR_OVERRIDE_SCHEMA", "MATERIAL_OVERRIDE_SCHEMA"],
}


@pytest.mark.parametrize("module", sorted(SIGNATURES))
def test_interface_signatures_are_frozen(module):
    mod = __import__(module, fromlist=["_"])
    for name, params in SIGNATURES[module].items():
        assert list(inspect.signature(getattr(mod, name)).parameters) == params, (module, name)
    for name in CONSTANTS.get(module, []):
        assert hasattr(mod, name), (module, name)


def test_edit_ops_and_groups_names():
    from wenart.furniture import edit_ops, groups

    # Milestone 12 (§13.2) adds the group tools after the Milestone 11 ops, which keep their names and order.
    assert edit_ops.EDIT_OPS[:10] == ("move", "rotate", "resize", "change_type", "swap_model", "add", "add_group",
                                      "remove", "relayout_room", "set_room_type")
    assert set(edit_ops.EDIT_OPS[10:]) == {"place_group", "complete_group", "move_group", "retype_piece",
                                           "mark_not_furniture", "fix_fixture", "set_front"}
    assert groups.GROUPS == ("dining_set", "bed_set", "living_set", "desk_set", "kitchen_run")


def test_schema_has_the_m11_fields():
    s = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    d = s["$defs"]
    assert "inferred" in d["evidence"]["properties"]["method"]["enum"]
    for k in ("furniture", "room"):
        assert {"adjusted_by_ai", "inferred"} <= set(d[k]["properties"]), k
    assert "drawn_front_deg" in d["furniture"]["properties"]
    assert "corrected_by_ai" in d["room"]["properties"]
    assert set(s["properties"]["agent_overrides"]["properties"]) == {"cameras", "exterior", "materials", "round"}
