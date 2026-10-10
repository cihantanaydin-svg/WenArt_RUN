"""CPU tests of the agent's level edits (docs/milestone12.md §3.6; wenart/levels/edits.py): strict schemas with a
reason, the five ops accepted and refused, the score rule, purity and the labels."""
import copy

import pytest

from wenart.levels import edits as E
from wenart.levels import model as M
from tests import _levels_fixture as F


def _b(*marks):
    b = F.building()
    b["level_marks"] = list(marks)
    return M.infer_levels(b)


def test_schemas_are_strict_and_need_a_reason():
    assert set(E.LEVEL_EDIT_OPS) == set(E.LEVEL_EDIT_SCHEMAS)
    for op, schema in E.LEVEL_EDIT_SCHEMAS.items():
        assert schema["additionalProperties"] is False and "reason" in schema["required"], op
    assert "evidence" in E.LEVEL_EDIT_SCHEMAS["set_room_floor"]["required"]
    assert "evidence" in E.LEVEL_EDIT_SCHEMAS["set_ground_point"]["required"]
    r = E.apply_level_edit(_b(), {"op": "set_terrain", "args": {"kind": "flat"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("schema:")
    r = E.apply_level_edit(_b(), {"op": "set_terrain", "args": {"kind": "flat", "reason": "x y z", "extra": 1}})
    assert not r["accepted"] and "schema" in r["failed_checks"][0]
    r = E.apply_level_edit(_b(), {"op": "move_ground", "args": {}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("op:")
    assert set(r) == {"accepted", "failed_checks", "score_before", "score_after", "building", "changed_ids",
                      "rerun_from", "message"} and r["rerun_from"] == "build"


def test_set_mark_kind_and_the_section_anchor():
    b = _b(F.mark("lm_001", -0.30, kind="ground_finished", point=(3.0, -4.0)),
           F.mark("lm_002", 0.0, kind="slab_top", level="L0", placement="section"))
    before = copy.deepcopy(b)
    r = E.apply_level_edit(b, {"op": "set_mark_kind", "args": {"mark_id": "lm_001", "kind": "unknown",
                                                               "reason": "a road level, not the plot"},
                               "round": 2})
    assert r["accepted"] and r["changed_ids"] == ["lm_001"] and b == before          # pure
    nb = r["building"]
    m = next(x for x in nb["level_marks"] if x["id"] == "lm_001")
    assert m["kind"] == "unknown" and m["corrected_by_ai"] == {"reason": "a road level, not the plot",
                                                               "before": {"kind": "ground_finished"}, "round": 2}
    assert nb["site"]["ground"]["source"] == "D3a"                                   # the ground follows the kind
    assert nb["level_inference"]["edits"][0]["op"] == "set_mark_kind"
    r = E.apply_level_edit(b, {"op": "set_mark_kind", "args": {"mark_id": "lm_002", "kind": "floor",
                                                               "reason": "try the section"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("anchor:")
    r = E.apply_level_edit(b, {"op": "set_mark_kind", "args": {"mark_id": "lm_009", "kind": "floor", "reason": "x x"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("exists:")


def test_set_room_floor_needs_a_mark_or_a_step_line():
    b = _b(F.mark("lm_001", -0.30, kind="unknown", point=(3.0, 4.0)))
    r = E.apply_level_edit(b, {"op": "set_room_floor", "args": {"room_id": "r_living", "offset_m": -0.30,
                                                                "evidence": {"mark_id": "lm_001"},
                                                                "reason": "the sunken living room mark"}})
    assert r["accepted"]
    room = next(x for x in r["building"]["rooms"] if x["id"] == "r_living")
    assert room["floor_offset_m"] == -0.3 and room["floor_source"] == "agent" and room["floor_evidence"]
    assert next(o for o in r["building"]["openings"] if o["id"] == "d_inner")["threshold_z"] == 0.0
    r = E.apply_level_edit(b, {"op": "set_room_floor", "args": {"room_id": "r_living", "offset_m": -0.15,
                                                                "evidence": {"mark_id": "lm_001"}, "reason": "half"}})
    assert not r["accepted"] and "gives -0.30" in r["failed_checks"][0]
    r = E.apply_level_edit(b, {"op": "set_room_floor", "args": {"room_id": "r_living", "offset_m": -0.15,
                                                                "evidence": {"step_line": "LINE:5A"},
                                                                "reason": "a step line along the arch"}})
    assert r["accepted"] and next(x for x in r["building"]["rooms"]
                                  if x["id"] == "r_living")["floor_evidence"][0]["entity"] == "LINE:5A"
    r = E.apply_level_edit(b, {"op": "set_room_floor", "args": {"room_id": "r_living", "offset_m": -2.0,
                                                                "evidence": {"step_line": "LINE:5A"},
                                                                "reason": "too deep"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("range:")


def test_set_ground_point_and_the_mark_wins():
    b = _b(F.mark("lm_001", -0.30, kind="ground_finished", point=(3.0, -4.0)))
    r = E.apply_level_edit(b, {"op": "set_ground_point", "args": {"x": 3.5, "y": -4.0, "z": -1.0,
                                                                  "evidence": "photo 3", "reason": "looks lower"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("anchor:")
    r = E.apply_level_edit(b, {"op": "set_ground_point", "args": {"x": 8.0, "y": -3.0, "z": -0.30,
                                                                  "evidence": "site photo 2", "reason": "the path"}})
    assert r["accepted"] and r["changed_ids"] == ["lm_ai_001"]
    m = r["building"]["level_marks"][-1]
    assert m["evidence"][0]["method"] == "ai" and m["status"] == "unverified" and m["inferred"]


def test_set_entrance_and_the_score_rule():
    b = _b()
    r = E.apply_level_edit(b, {"op": "set_entrance", "args": {"door_id": "d_front", "solution": "none",
                                                              "reason": "flush is enough"}})
    assert not r["accepted"] and r["score_after"] > r["score_before"] and "L2 d_front" in r["failed_checks"][1]
    r = E.apply_level_edit(b, {"op": "set_entrance", "args": {"door_id": "d_front", "solution": "steps_and_ramp",
                                                              "reason": "an accessible entrance"}})
    assert r["accepted"]
    e = r["building"]["site"]["entrances"][0]
    assert e["solution"] == "steps_and_ramp" and e["ramp"]["ratio"] == "1:12" and e["adjusted_by_ai"]["before"] == "steps"
    r2 = E.apply_level_edit(r["building"], {"op": "set_entrance", "args": {"door_id": "d_inner", "solution": "ramp",
                                                                           "reason": "inner"}})
    assert not r2["accepted"] and r2["failed_checks"][0].startswith("exists:")


def test_set_terrain():
    marks = [F.mark("lm_001", -0.45, kind="ground_finished", point=(8.0, -3.0)),
             F.mark("lm_002", -0.45, kind="ground_finished", point=(-3.0, -3.0)),
             F.mark("lm_003", -0.05, kind="ground_finished", point=(-3.0, 11.0))]
    b = _b(*marks)
    assert b["site"]["ground"]["terrain"] == "planar"
    r = E.apply_level_edit(b, {"op": "set_terrain", "args": {"kind": "flat", "reason": "the site is level"}})
    assert not r["accepted"] and "L4 lm_003" in r["failed_checks"][1]             # a drawn mark says otherwise
    r = E.apply_level_edit(b, {"op": "set_terrain", "args": {"kind": "tin", "reason": "follow the marks"}})
    assert r["accepted"] and r["building"]["site"]["ground"]["terrain"] == "tin"
    level = _b(*[dict(m, value=-0.3, z=-0.3) for m in marks])
    r = E.apply_level_edit(level, {"op": "set_terrain", "args": {"kind": "flat", "reason": "the site is level"}})
    assert r["accepted"] and r["building"]["site"]["ground"]["terrain"] == "flat"
    assert r["building"]["site"]["ground"]["levels"][0]["z"]["value"] == -0.3             # the median of the marks
    r = E.apply_level_edit(_b(), {"op": "set_terrain", "args": {"kind": "planar", "reason": "no points"}})
    assert not r["accepted"] and r["failed_checks"][0].startswith("evidence:")
