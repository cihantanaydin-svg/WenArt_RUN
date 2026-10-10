"""The tool API of the agent (docs/milestone11.md §3, §10 "tool schemas"): every schema is valid JSON Schema, a bad
call is rejected with the schema error and counted, every edit tool validates by code before it is accepted and
every accepted edit is one entry of overrides.json."""
from __future__ import annotations

import json

import jsonschema
import pytest

from test_agent_helpers import FakeEdits, fake_validators, project, write_json
from wenart.agent import geometry_fix as GF
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.agent import tools as TL

READ = ["building_summary", "room", "room_topdown", "plan_crop", "plausibility", "view", "exterior_summary",
        "catalog", "stage_status"]
EDIT = ["move_piece", "rotate_piece", "resize_piece", "change_type", "swap_model", "add_piece", "add_group",
        "remove_piece", "relayout_room", "set_room_type", "set_camera", "add_camera", "remove_camera", "set_material",
        "set_exterior", "set_lighting", "correct_geometry", "rerun_stage"]   # set_lighting: real03 follow-up


def ctx_for(tmp_path, **kw):
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    kw.setdefault("apply_edit", FakeEdits())
    kw.setdefault("validators", fake_validators())
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out), **kw)


def test_the_registry_has_every_tool_of_section_3_with_valid_schemas():
    reg = TL.build_registry()
    assert reg.names() == READ + EDIT + ["finish"]
    for tool in reg.tools.values():
        jsonschema.Draft202012Validator.check_schema(tool.parameters)
        spec = tool.spec()
        assert spec["type"] == "function" and spec["function"]["strict"] is True and spec["function"]["description"]
        if tool.kind in TL.EDIT_KINDS:
            assert "reason" in tool.parameters["required"], tool.name
            assert not {"op", "round", "log_seq", "model"} & set(tool.parameters["properties"]), tool.name
    json.dumps(reg.specs())


def test_track_b_edit_schemas_replace_the_fallbacks(monkeypatch):
    from wenart.furniture import edit_ops
    mine = {"type": "object", "required": ["op", "piece_id", "front_deg"], "additionalProperties": False,
            "properties": {"op": {"const": "rotate"}, "piece_id": {"type": "string"},
                           "front_deg": {"type": "number", "minimum": 0, "maximum": 360}, "round": {"type": "integer"}}}
    monkeypatch.setattr(edit_ops, "EDIT_SCHEMAS", {"rotate": mine})
    reg = TL.build_registry()
    params = reg.tools["rotate_piece"].parameters
    assert params["properties"]["front_deg"]["maximum"] == 360 and params["required"] == ["piece_id", "front_deg",
                                                                                          "reason"]
    assert "op" not in params["properties"] and "round" not in params["properties"]
    assert reg.tools["move_piece"].parameters == TL.with_reason(TL.FALLBACK_EDIT_SCHEMAS["move"])


def test_bad_calls_are_rejected_with_the_schema_error_and_counted(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": "south", "reason": "face the door"})
    assert res["schema_error"] and "front_deg" in res["error"]
    assert reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90})["schema_error"]      # no reason
    assert reg.call(ctx, "teleport", {})["schema_error"]
    assert reg.call(ctx, "room", None, "the arguments are not valid JSON")["schema_error"]
    assert reg.call(ctx, "room", {"room_id": "r1", "extra": 1})["schema_error"]
    assert ctx.schema_errors == 5 and ctx.accepted == [] and not OV.overrides_path(ctx.project_out).exists()
    assert ctx.apply_edit.calls == []


def test_read_tools(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    s = reg.call(ctx, "building_summary", {})
    assert [r["id"] for r in s["rooms"]] == ["r1", "r2"] and s["counts"]["furniture"] == {"from_documents": 2,
                                                                                         "added_by_ai": 1}
    room = reg.call(ctx, "room", {"room_id": "r1"})
    assert {p["id"] for p in room["pieces"]} == {"f1", "f2"} and [d["id"] for d in room["doors"]] == ["d1"]
    assert room["doors"][0]["swing_polygon"] and [w["id"] for w in room["windows"]] == ["win1"]
    assert {"w1", "w2", "w3", "w4"} <= {w["id"] for w in room["walls"]}
    top = reg.call(ctx, "room_topdown", {"room_id": "r1"})
    assert top["image"].startswith("images/r1_") and (ctx.project_out / "orchestrator" / top["image"]).is_file()
    assert len(ctx.pending_images) == 1
    assert reg.call(ctx, "room_topdown", {"room_id": "nope"})["error"]
    crop = reg.call(ctx, "plan_crop", {"piece_id": "f1"})
    assert crop["image"] is None and "no plan crop" in crop["note"]
    (ctx.project_out / "final").mkdir()
    (ctx.project_out / "final" / "cam_r1_1_plan.jpg").write_bytes(b"jpg")
    assert reg.call(ctx, "plan_crop", {"room_id": "r1"})["image"] == "final/cam_r1_1_plan.jpg"
    view = reg.call(ctx, "view", {"view_id": "cam_r2_1"})
    assert view["image"] == "agent/previews/cam_r2_1_preview.jpg" and view["room_id"] == "r2"
    assert reg.call(ctx, "view", {"view_id": "cam_x"})["error"]
    ext = reg.call(ctx, "exterior_summary", {})
    assert ext["outline_bbox"] == [0.0, 0.0, 8.0, 3.5] and [c["view_id"] for c in ext["exterior_cameras"]] == ["ext_1"]
    plaus = reg.call(ctx, "plausibility", {"room_id": "r1"})
    assert 0 <= plaus["score"] <= 100 and isinstance(plaus["violations"], list)   # track B's plausibility (merged)
    write_json(ctx.project_out / "run" / "refit.json", {"status": "ok", "seconds": 3.0, "note": None})
    assert reg.call(ctx, "stage_status", {})["stages"] == {"refit": {"status": "ok", "seconds": 3.0, "note": None}}
    cat = reg.call(ctx, "catalog", {"type": "sofa", "size": [2.0, 0.9]})
    assert cat["count"] > 0 and len(cat["models"]) <= 10


def test_furniture_edit_accepted_goes_to_overrides_with_images(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90, "reason": "the headboard on the wall"})
    assert res["accepted"] and res["failed_checks"] == [] and (res["score_before"], res["score_after"]) == (50, 70)
    assert res["overrides_id"] == 1 and res["rerun_from"] == "refit" and res["changed_ids"] == ["f1"]
    assert res["before_image"].startswith("images/") and res["after_image"].startswith("images/")
    assert ctx.piece("f1")["front_deg"] == 90 and ctx.piece("f1")["adjusted_by_ai"]["round"] == 1
    edit = ctx.apply_edit.calls[0]
    assert edit["op"] == "rotate" and edit["model"] == "mock/agent" and edit["round"] == 1 and edit["log_seq"] == 1
    stored = json.loads(OV.overrides_path(ctx.project_out).read_text())
    assert stored["project"] == "toy" and [(e["seq"], e["tool"]) for e in stored["edits"]] == [(1, "rotate_piece")]
    assert stored["edits"][0]["result"]["accepted"] and stored["edits"][0]["model"] == "mock/agent"


def test_rejected_and_unavailable_edits_never_reach_overrides(tmp_path, monkeypatch):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 355, "reason": "into the wall"})
    assert not res["accepted"] and res["failed_checks"] == ["front_into_wall"] and res["overrides_id"] is None
    assert res["rerun_from"] is None and ctx.piece("f1")["front_deg"] == 270.0
    # an edit validator that is not available (the track B stub before the merge): refused, never applied
    from wenart.furniture import edit_ops

    def missing(*a, **k):
        raise NotImplementedError("M11 track B")

    monkeypatch.setattr(edit_ops, "apply_edit", missing)
    ctx2 = ctx_for(tmp_path / "b", apply_edit=None)
    res = reg.call(ctx2, "move_piece", {"piece_id": "f1", "center": [2, 2], "reason": "away from the door"})
    assert not res["accepted"] and res["failed_checks"] == ["validator_unavailable"]
    assert not OV.overrides_path(ctx.project_out).exists() and len(ctx.rejected) == 1


def test_one_target_is_edited_at_most_three_times_per_round(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    for front in (0, 90, 180):
        assert reg.call(ctx, "rotate_piece", {"piece_id": "f2", "front_deg": front, "reason": "try"})["accepted"]
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f2", "front_deg": 270, "reason": "try again"})
    assert not res["accepted"] and res["failed_checks"][0].startswith("max_tries")
    assert len(ctx.apply_edit.calls) == 3


def test_override_tools_use_the_track_c_validators(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    cam = {"view_id": "cam_r1_1", "kind": "interior", "room_id": "r1", "position": [3.0, 0.8, 1.4],
           "target": [1.0, 3.0, 1.2], "lens_mm": 20, "reason": "see the bed"}
    assert reg.call(ctx, "set_camera", cam)["accepted"]
    bad = reg.call(ctx, "set_camera", dict(cam, position=[3.0, 0.8, -1.0]))
    assert not bad["accepted"] and bad["failed_checks"] == ["camera below the floor"]
    assert not reg.call(ctx, "set_camera", dict(cam, view_id="cam_nope"))["accepted"]
    assert reg.call(ctx, "remove_camera", {"view_id": "ext_1", "reason": "a view of a bare wall"})["accepted"]
    assert reg.call(ctx, "set_material", {"slot": "kitchen_walls", "look_id": "plaster_white",
                                          "reason": "backsplash only"})["accepted"]
    assert not reg.call(ctx, "set_material", {"slot": "floor", "look_id": "nope", "reason": "x x"})["accepted"]
    ext = reg.call(ctx, "set_exterior", {"roof": {"type": "hip", "pitch_deg": 30}, "reason": "close the roof"})
    assert ext["accepted"] and ext["rerun_from"] == "build"
    ov = OV.Overrides(ctx.project_out).agent_overrides()
    assert [c["action"] for c in ov["cameras"]] == ["set", "remove"] and ov["cameras"][1]["kind"] == "exterior"
    assert ov["materials"] == {"kitchen_walls": "plaster_white"} and ov["exterior"]["roof"]["type"] == "hip"


def test_correct_geometry_takes_only_clear_errors_and_is_record_only(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    ok = reg.call(ctx, "correct_geometry", {"kind": "fix_opening_on_wall", "opening_id": "win2",
                                            "evidence": "window drawn 6 cm off the wall line", "reason": "off its wall"})
    assert ok["accepted"] and ok["applied"] is False and ok["rerun_from"] == "pipeline_final"
    far = reg.call(ctx, "correct_geometry", {"kind": "merge_duplicate_wall", "wall_ids": ["w1", "w8"],
                                             "evidence": "two lines", "reason": "duplicate"})
    assert not far["accepted"] and any("apart" in f for f in far["failed_checks"])
    assert GF.check(ctx.building, {"kind": "close_gap", "wall_ids": ["w1", "w2"], "evidence": "x"})["failed"]
    near = dict(ctx.building, walls=ctx.building["walls"] + [
        {"id": "w9", "level_id": "L0", "start": [8.1, 0.0], "end": [10.0, 0.0], "thickness": 0.2}])
    assert GF.check(near, {"kind": "close_gap", "wall_ids": ["w5", "w9"], "evidence": "10 cm gap"})["ok"]
    dup = dict(ctx.building, walls=ctx.building["walls"] + [
        {"id": "w10", "level_id": "L0", "start": [0.5, 0.01], "end": [3.0, 0.01], "thickness": 0.2}])
    assert GF.check(dup, {"kind": "merge_duplicate_wall", "wall_ids": ["w1", "w10"], "evidence": "x"})["ok"]
    assert ctx.building["walls"] == json.loads((ctx.project_out / "building_decor.json").read_text())["walls"]
    geo = OV.Overrides(ctx.project_out).agent_overrides()["geometry"]
    assert len(geo) == 1 and geo[0]["applied"] is False and geo[0]["opening_id"] == "win2"


def test_rerun_stage_white_list_and_finish(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    assert reg.call(ctx, "rerun_stage", {"stage": "polish", "settings": {"enabled": False},
                                         "reason": "the polish added a lamp"})["accepted"]
    assert not reg.call(ctx, "rerun_stage", {"stage": "polish", "settings": {"strength": 0.1},
                                             "reason": "lower strength"})["accepted"]
    assert reg.call(ctx, "rerun_stage", {"stage": "pipeline", "reason": "again"})["schema_error"]
    assert OV.Overrides(ctx.project_out).agent_overrides()["reruns"] == {"polish": {"enabled": False}}
    assert reg.call(ctx, "finish", {"verdict": "done"})["round_ends"] and ctx.finished["verdict"] == "done"


@pytest.mark.parametrize("tool,args,label", [("add_piece", {"room_id": "r2", "type": "armchair"}, "added_by_ai"),
                                             ("rotate_piece", {"piece_id": "f3"}, "added_by_ai"),
                                             ("rotate_piece", {"piece_id": "f1"}, "adjusted_by_ai"),
                                             ("correct_geometry", {}, "corrected_by_ai"),
                                             ("set_camera", {}, "agent_override")])
def test_labels(tmp_path, tool, args, label):
    assert TL.label_for(tool, ctx_for(tmp_path), args) == label
