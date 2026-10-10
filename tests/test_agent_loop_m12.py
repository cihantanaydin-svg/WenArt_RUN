"""The M12 loop (docs/milestone12.md §5.3, §5.4 D18/D19; bugs B3, B5, B8): plan first, checked against the brief;
unfixable findings never sent; coverage before second sessions; parallel room sessions; a time cap per round; decor
synced after every accepted edit; level edits and library gaps; track G's new ops validated as their M11 ops while
they are stubs; the code critic's G-, L-, S- and library-gap families. MockModel, fake critics and fake validators."""
from __future__ import annotations

import copy
import json

from test_agent_helpers import FakeEdits, ScriptedCritic, fake_validators, piece, project, violation, write_json
from wenart.agent import critic_code as CC
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as M
from wenart.agent import overrides as OV
from wenart.agent import tools as TL

FINISH = {"tool_calls": [{"name": "finish", "arguments": {"verdict": "done"}}]}
F3 = violation("F3", "critical", "f1", "r1", "the headboard is in the middle of the room")
F9_UNBUILT = violation("F9", "critical", "f5", "r1", "a giant box")
D2_SOFA = violation("F8", "major", "f3", "r2", "the sofa floats in the room")


class Clock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class Edits(FakeEdits):
    """FakeEdits + the M12 ops set_front (as rotate) and complete_group (adds a nightstand)."""

    def __call__(self, building, edit, *, catalog=None):
        if edit["op"] == "set_front":
            edit = dict(edit, op="rotate")
        if edit["op"] == "complete_group":
            self.calls.append(copy.deepcopy(edit))
            b = copy.deepcopy(building)
            b["furniture"].append(piece("f_ai_n", "r1", "nightstand", (3.1, 3.25), (0.4, 0.4), 0.0, 270.0,
                                        "added_by_ai"))
            return {"accepted": True, "failed_checks": [], "score_before": 50.0, "score_after": 80.0, "building": b,
                    "changed_ids": ["f_ai_n"], "rerun_from": "refit", "message": ""}
        return super().__call__(building, edit, catalog=catalog)


def unbuilt(out):
    """Add the unbuilt cluster f5 to r1 (building_decor/final/agent)."""
    for name in ("building_decor.json", "building_final.json"):
        b = json.loads((out / name).read_text())
        b["furniture"].append(dict(piece("f5", "r1", "unknown", (1.0, 1.0), (3.0, 2.0), 0.0, None), build=False))
        write_json(out / name, b)


def make(tmp_path, chat, critic_rounds, *, plan=(), **kw):
    out = project(tmp_path)
    if kw.pop("with_unbuilt", True):
        unbuilt(out)
    model = M.MockModel(chat=chat, plan=list(plan), critic=kw.pop("critic", []))
    syncs = kw.pop("syncs", [])
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": v}, clock=kw.pop("clock", Clock()),
                        code_critic=ScriptedCritic(critic_rounds), vision=False, apply_edit=kw.pop("edits", Edits()),
                        validators=fake_validators(), out=lambda s: None, workers=kw.pop("workers", 1),
                        sync=lambda b: syncs.append(1) or b, **kw)
    return loop, out, model


def log_of(out) -> dict:
    return json.loads((out / "orchestrator" / "log.json").read_text())


def set_front(pid, front, reason="the front towards the room"):
    return {"tool_calls": [{"name": "set_front", "arguments": {"piece_id": pid, "front_deg": front,
                                                                "reason": reason}}]}


def test_unfixable_findings_are_never_sent_as_work(tmp_path):
    """§5.2, §1.4 cause 1 (53 of 73 rejections aimed at locked or unbuilt pieces)."""
    loop, out, model = make(tmp_path, [set_front("f1", 90)], [[F9_UNBUILT]])
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_fixable" and model.requests == []
    rnd = next(e for e in log_of(out)["events"] if e["kind"] == "round")
    assert rnd["status"] == "no_fixable" and rnd["counts"]["unfixable_open"] == 1
    # with a fixable finding next to it, the unfixable one is shown as "not yours" only
    loop2, out2, model2 = make(tmp_path / "b", [set_front("f1", 90)], [[F3, F9_UNBUILT]])
    loop2.run()
    task = model2.chat_requests()[0]["messages"][1]["content"]
    brief = json.loads(task.split("Room brief (JSON):\n", 1)[1].split("\n", 1)[0])
    assert [f["id"] for f in brief["findings"]["fixable"]] == ["c:F3:f1"]
    assert brief["findings"]["not_yours"][0]["target"] == "f5" and "not built" in brief["findings"]["not_yours"][0][
        "why"]
    assert "f5" not in [p["id"] for p in brief["pieces"]] and "1. move_piece on f1" in task


def test_the_plan_comes_first_and_is_checked_against_the_brief(tmp_path):
    plan = {"room_id": "r1", "program": {"keep": True}, "steps": [
        {"finding_ids": ["c:F3:f1"], "tool": "set_front", "target": "f1", "why": "turn the bed to the room"},
        {"finding_ids": ["c:F9:f5"], "tool": "mark_not_furniture", "target": "f5", "why": "a symbol"},
        {"finding_ids": [], "tool": "teleport", "target": "f1", "why": "move it fast"},
        {"finding_ids": ["c:F3:f1"], "tool": "fix_fixture", "target": "f1", "why": "a misread bed"}]}
    loop, out, model = make(tmp_path, [set_front("f1", 90), {"content": "more?"}], [[F3, F9_UNBUILT], []],
                            plan=[plan])
    summary = loop.run()
    assert summary["accepted"] == 1
    first = model.requests[0]
    assert M.MockModel.schema_name(first) == "plan" and "c:F3:f1" in first["messages"][1]["content"]
    # the checklist is the one valid step; the session ends when it is done (no second planner call)
    assert len(model.chat_requests()) == 1
    task = model.chat_requests()[0]["messages"][1]["content"]
    assert "1. set_front on f1 for c:F3:f1" in task and "2." not in task.split("Checklist")[1].split("Plan steps")[0]
    problems = task.split("Plan steps refused by the check (do not do them):\n")[1]
    assert "c:F9:f5 is not yours" in problems and "tool teleport is not offered" in problems
    assert "f1 does not allow fix_fixture" in problems
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "plan")
    assert ev["status"] == "ok" and ev["counts"] == {"steps": 1, "problems": 3} and ev["room_id"] == "r1"
    assert MEM.Memory(out).room("r1")["plans"][0] == {"round": 1, "ok": True, "problems": [
        "step 2 (mark_not_furniture on f5): c:F9:f5 is not yours", "step 3 (teleport on f1): tool teleport is not "
        "offered", "step 4 (fix_fixture on f1): f1 does not allow fix_fixture: fix_fixture is for drawn fixed "
        "equipment"], "steps": 4}
    assert LG.validate_log(log_of(out)) == []


def test_every_room_gets_a_session_before_any_room_gets_a_second(tmp_path):
    """§5.4 coverage (run 3: the same worst-first order every round, rooms #13-#35 never reached). Here the time cap
    lets one session start per round: round 2 takes the unvisited r2 although r1 weighs more."""
    findings = [F3, D2_SOFA]
    chat = [set_front("f1", 90), set_front("f3", 90), set_front("f1", 0)]
    loop, out, model = make(tmp_path, chat, [findings], round_cap_s=-1.0, max_rounds=3)
    summary = loop.run()
    sessions = [r["rooms_planner"] for r in summary["rounds"]]
    assert sessions == [["r1"], ["r2"], ["r1"]]
    assert [e["target"] for e in log_of(out)["events"] if e["kind"] == "edit"] == ["f1", "f3", "f1"]
    assert MEM.Memory(out).visits("r1") == 2 and MEM.Memory(out).visits("r2") == 1


def test_parallel_room_sessions(tmp_path):
    """§5.4: up to ``workers`` sessions at once on one server; each answers by its room."""
    def chat(body):
        task = body["messages"][1]["content"]
        done = any(m.get("role") == "tool" for m in body["messages"])
        if done:
            return FINISH
        return set_front("f1", 90) if "room r1:" in task else set_front("f3", 90)

    loop, out, model = make(tmp_path, [chat] * 6, [[F3, D2_SOFA], []], workers=4)
    summary = loop.run()
    assert summary["accepted"] == 2 and sorted(summary["rounds"][0]["rooms_planner"]) == ["r1", "r2"]
    assert sorted(e["target"] for e in log_of(out)["events"] if e["kind"] == "edit") == ["f1", "f3"]
    assert LG.validate_log(log_of(out)) == [] and len(OV.Overrides(out).accepted()) == 2
    assert sorted(json.loads((out / "orchestrator" / "memory.json").read_text())["rooms"]) == ["r1", "r2"]


def test_decor_follows_every_accepted_edit_and_every_replay(tmp_path):
    """B3: ``decor.sync_to_hosts`` after every accepted edit (tools) and after every replayed edit (apply)."""
    syncs = []
    loop, out, model = make(tmp_path, [{"tool_calls": [
        {"name": "set_front", "arguments": {"piece_id": "f1", "front_deg": 355, "reason": "rejected"}}]},
        set_front("f1", 90)], [[F3], []], syncs=syncs)
    loop.run()
    assert len(syncs) == 1                                  # the rejected edit synced nothing
    replay = []
    OV.apply(out, apply_edit=Edits(), sync=lambda b: replay.append(b["furniture"][0]["front_deg"]) or b)
    assert replay == [90]


def test_the_default_sync_is_track_s(monkeypatch, tmp_path):
    from wenart.furniture import decor
    seen = []
    monkeypatch.setattr(decor, "sync_to_hosts", lambda b: seen.append(1) or b)
    out = project(tmp_path)
    ctx = TL.ToolContext.load(out, round=1, model_id="m", apply_edit=Edits(), validators=fake_validators())
    assert TL.build_registry().call(ctx, "set_front", {"piece_id": "f2", "front_deg": 90, "reason": "x x"})["accepted"]
    assert seen == [1]


def test_level_edits_go_through_track_l_and_rerun_the_build(tmp_path):
    seen = []

    def level_edit(building, edit):
        seen.append(edit)
        b = copy.deepcopy(building)
        b["rooms"][0]["floor_offset_m"] = edit.get("offset_m")
        return {"accepted": True, "failed_checks": [], "score_before": 2.0, "score_after": 1.0, "building": b,
                "changed_ids": ["r1"], "rerun_from": "build", "message": "L1 0.15 m -> 0.00 m"}

    out = project(tmp_path)
    ctx = TL.ToolContext.load(out, round=1, model_id="m", apply_edit=Edits(), validators=fake_validators(),
                              level_edit=level_edit, sync=lambda b: b, overrides=OV.Overrides(out))
    reg = TL.build_registry()
    res = reg.call(ctx, "set_room_floor", {"room_id": "r1", "offset_m": 0.15, "evidence": "KOT +0.15",
                                           "reason": "the mark inside the room"})
    assert res["accepted"] and res["rerun_from"] == "build" and seen[0]["op"] == "set_room_floor"
    assert ctx.room("r1")["floor_offset_m"] == 0.15 and TL.label_for("set_room_floor", ctx, {}) == "corrected_by_ai"
    from test_agent_helpers import CAMERAS
    assert LP.changed_views(CAMERAS, ctx.accepted, lambda pid: None) == ["cam_r1_1", "cam_r2_1", "ext_1"]
    summary = OV.apply(out, apply_edit=Edits(), level_edit=level_edit, sync=lambda b: b)
    assert summary["replayed"] == [1]
    assert json.loads((out / "building_agent.json").read_text())["rooms"][0]["floor_offset_m"] == 0.15


def test_track_g_ops_are_validated_as_their_m11_ops_while_they_are_stubs(tmp_path):
    """``set_front`` / ``retype_piece`` / ``mark_not_furniture`` with the real ``edit_ops`` (whose EDIT_OPS do not list
    them yet): sent as rotate / change_type / remove, never refused as an unknown edit."""
    edit = {"op": "mark_not_furniture", "piece_id": "f9", "kind": "room_number", "evidence": "circle with 5",
            "reason": "a room number", "round": 1, "log_seq": 2, "model": "m"}
    got = OV.resolve_edit(edit, ("rotate", "change_type", "remove"))
    assert got["op"] == "remove" and "kind" not in got and "not furniture (room_number): circle with 5" in got["reason"]
    assert OV.resolve_edit(edit, ("mark_not_furniture", "remove")) is edit
    assert OV.resolve_edit({"op": "set_front", "piece_id": "a"}, ("rotate",))["op"] == "rotate"
    from wenart.furniture import edit_ops
    out = project(tmp_path)
    ctx = TL.ToolContext.load(out, round=1, model_id="m", validators=fake_validators(), sync=lambda b: b)
    res = TL.build_registry().call(ctx, "set_front", {"piece_id": "f3", "front_deg": 90, "reason": "face the room"})
    assert not any("unknown edit" in f for f in res["failed_checks"]), res
    if "set_front" not in edit_ops.EDIT_OPS:
        assert res["accepted"] or res["failed_checks"]


def test_report_library_gap_is_record_only(tmp_path):
    out = project(tmp_path)
    ctx = TL.ToolContext.load(out, round=1, model_id="m", apply_edit=Edits(), validators=fake_validators(),
                              overrides=OV.Overrides(out))
    res = TL.build_registry().call(ctx, "report_library_gap", {"type": "bathtub", "style": "rustic",
                                                               "reason": "no audited rustic bathtub"})
    assert res["accepted"] and res["applied"] is False and LP.route(ctx.accepted) is None
    assert OV.Overrides(out).agent_overrides()["library_gaps"][0]["type"] == "bathtub"


def test_the_code_critic_adds_group_level_scene_and_library_gap_findings(tmp_path):
    b = json.loads((project(tmp_path) / "building_decor.json").read_text())
    b["furniture"][2]["library_gap"] = {"style": "rustic", "used": "related type armchair"}
    write_json(tmp_path / "checks" / "scene_L0.json", {"violations": [
        {"check": "S5", "severity": "major", "target": "f3", "room_id": None, "message": "gap 0.04 m",
         "metrics": {"gap_m": 0.04}}], "counts": {}})
    res = CC.run(b, {}, None, plausibility_fn=lambda x: {"rooms": {}}, exterior_fn=lambda *a: {"violations": []},
                 views_fn=lambda *a: {"views": {}},
                 groups_fn=lambda x: {"rooms": {"r1": [violation("G4", "major", "f2", None, "one side only")]},
                                      "counts": {}},
                 levels_fn=lambda x, s, r: [violation("L2", "critical", "d1", None, "door 0.45 m above the ground")],
                 scene_dir=tmp_path / "checks")
    got = {(f["check"], f["target"], f["room_id"]) for f in res["findings"]}
    assert got == {("G4", "f2", "r1"), ("L2", "d1", None), ("S5", "f3", "r2"), ("LG", "f3", "r2")}
    assert {c["source"]: c["status"] for c in res["checks"]} == {
        "plausibility": "ok", "exterior": "ok", "views": "ok", "groups": "ok", "levels": "ok", "scene": "ok",
        "library": "ok"}
    lg = next(f for f in res["findings"] if f["check"] == "LG")
    assert lg["severity"] == "minor" and "related type armchair" in lg["message"]
    none = CC.run(b, {}, None, plausibility_fn=lambda x: {"rooms": {}}, exterior_fn=lambda *a: {"violations": []},
                  views_fn=lambda *a: {"views": {}}, scene_dir=tmp_path / "nothing")
    assert {c["source"]: c["status"] for c in none["checks"]}["scene"] == "unavailable"
    assert CC.FAMILY_OF["G11"] == "groups" and CC.FAMILY_OF["L7"] == "levels" and CC.FAMILY_OF["S2"] == "scene"


def test_the_loop_docstring_states_the_time_cap(tmp_path):
    """B8: the docstring said 40 calls per round while the code had 120; M12 replaces the call cap by a time cap."""
    import inspect
    assert "= 40" not in LP.__doc__ and "TIME cap" in LP.__doc__ and LP.ROUND_CAP_S == 900.0
    params = inspect.signature(LP.AgentLoop.__init__).parameters
    assert not hasattr(LP, "MAX_CALLS") and params["max_calls"].default is None
    assert params["round_cap_s"].default == LP.ROUND_CAP_S and params["workers"].default == LP.WORKERS == 4


def test_metrics_are_written_after_every_round(tmp_path):
    loop, out, model = make(tmp_path, [set_front("f1", 90)], [[F3], []])
    loop.run()
    m = json.loads((out / "orchestrator" / "metrics.json").read_text())
    assert m["edits"]["accepted"] == 1 and m["rooms"]["fixable_visited_share"] == 1.0
    assert m["findings"]["before_totals"]["critical"] == 1 and m["findings"]["after_totals"]["critical"] == 0
    assert m["memory"]["plans"] == 1 and m["per_room"]["r1"]["calls"] >= 2
    assert m["time"]["first_accepted_edit_s"] is not None
