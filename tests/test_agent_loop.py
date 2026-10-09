"""The feedback loop (docs/milestone11.md §8, §10 "loop", "log"): stop rules (no finding, no accepted edit, max rounds,
deadline), the router (earliest stage, changed views), the planner's budgets, the vision critic's screening by code,
and a complete, schema-valid decision log. Everything is driven on the CPU: MockModel, a scripted code critic, the
fake edit validator and a fake re-run."""
from __future__ import annotations

import json

import pytest

from test_agent_helpers import FakeEdits, ScriptedCritic, fake_validators, project, violation
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import model as M
from wenart.agent import overrides as OV


class Clock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class Rerun:
    def __init__(self, clock=None, advance=0.0, status="ok"):
        self.calls = []
        self.clock, self.advance, self.status = clock, advance, status

    def __call__(self, stage, views, round_no, final):
        self.calls.append((stage, list(views), round_no, final))
        if self.clock is not None:
            self.clock.t += self.advance
        return {"status": self.status, "views": list(views), "seconds": self.advance}


def rotate(pid, front, reason="the headboard belongs on the wall"):
    return {"tool_calls": [{"name": "rotate_piece", "arguments": {"piece_id": pid, "front_deg": front,
                                                                   "reason": reason}}]}


FINISH = {"tool_calls": [{"name": "finish", "arguments": {"verdict": "done"}}]}
F3 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")


def make(tmp_path, chat, critic_rounds, **kw):
    out = project(tmp_path)
    model = M.MockModel(chat=chat, critic=kw.pop("critic", []))
    clock = kw.pop("clock", Clock())
    loop = LP.AgentLoop(out, model, rerun=kw.pop("rerun", Rerun()), clock=clock, code_critic=ScriptedCritic(critic_rounds),
                        vision=kw.pop("vision", False), apply_edit=FakeEdits(), validators=fake_validators(), out=lambda s: None,
                        **kw)
    return loop, out, model


def log_of(out) -> dict:
    return json.loads((out / "orchestrator" / "log.json").read_text())


def test_one_fix_then_no_finding_left(tmp_path):
    loop, out, model = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3], []])
    summary = loop.run()
    assert summary["stop"] == {"round": 2, "reason": "no_finding"} and summary["accepted"] == 1
    assert loop.rerun.calls == [("refit", ["cam_r1_1"], 1, False)]
    data = log_of(out)
    assert LG.validate_log(data) == []
    kinds = [e["kind"] for e in data["events"]]
    assert kinds.count("edit") == 1 and kinds[-1] == "stop" and "rerun" in kinds
    edit = next(e for e in data["events"] if e["kind"] == "edit")
    assert edit["validation"] == {"accepted": True, "failed_checks": [], "score_before": 50.0, "score_after": 70.0}
    assert edit["reason"] and edit["model"] == "mock/agent" and edit["round"] == 1 and edit["revision"] == "mock-rev"
    assert edit["checklist"] == "F3" and edit["target"] == "f1" and edit["label"] == "adjusted_by_ai"
    assert edit["rerun_from"] == "refit" and edit["overrides_id"] == 1 and edit["call_id"] == "r1-p1-t1"
    assert edit["before"].startswith("images/") and (out / "orchestrator" / edit["after"]).is_file()
    finding = next(e for e in data["events"] if e["kind"] == "finding")
    assert finding["source"] == "code" and finding["severity"] == "critical" and finding["evidence"]["metrics"]
    render = [e for e in data["events"] if e["kind"] == "render"]
    assert render and render[0]["before"] == "images/r1_cam_r1_1_before.jpg" and render[0]["after"]
    # every model call is logged with id, revision, tokens and seconds
    assert data["calls"] and all(c["model"] == "mock/agent" and c["revision"] == "mock-rev" and
                                 c["prompt_tokens"] is not None and c["seconds"] is not None for c in data["calls"])
    md = (out / "orchestrator" / "log.md").read_text()
    assert "## Round 1" in md and "rotate_piece" in md and "Stopped in round 2" in md
    # the planner saw the tools and the finding
    first = model.chat_requests()[0]
    assert first["tool_choice"] == "auto" and "f1" in first["messages"][1]["content"]
    assert json.loads(OV.overrides_path(out).read_text())["edits"][0]["tool"] == "rotate_piece"


def test_stops_at_max_rounds(tmp_path):
    chat = [rotate("f1", 90.0), FINISH, rotate("f1", 180.0), FINISH, rotate("f1", 0.0), FINISH]
    loop, out, _ = make(tmp_path, chat, [[F3]], max_rounds=2)
    summary = loop.run()
    assert summary["stop"]["reason"] == "max_rounds" and len(summary["rounds"]) == 2
    assert [c[2] for c in loop.rerun.calls] == [1, 2]
    assert LG.validate_log(log_of(out)) == []


def test_stops_when_no_edit_is_accepted(tmp_path):
    loop, out, _ = make(tmp_path, [rotate("f1", 355.0), {"content": "I cannot fix it"}], [[F3]])
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_edit" and loop.rerun.calls == []
    rej = [e for e in log_of(out)["events"] if e["kind"] == "rejected_edit"]
    assert rej[0]["validation"]["failed_checks"] == ["front_into_wall"] and rej[0]["validation"]["accepted"] is False
    assert not OV.overrides_path(out).exists()


def test_stops_at_the_deadline(tmp_path):
    clock = Clock()
    # 30 min left, the final stages need 15: 30 - 15 < 20 min margin -> no round at all
    loop, out, _ = make(tmp_path, [rotate("f1", 90.0)], [[F3]], clock=clock, deadline=clock.t + 1800,
                        final_estimate=900.0)
    summary = loop.run()
    assert summary["stop"] == {"round": 0, "reason": "deadline"} and summary["rounds"] == []
    stop = log_of(out)["events"][-1]
    assert stop["kind"] == "stop" and "time budget" in stop["reason"]
    # enough time for round 1, but its re-run takes the rest: round 2 does not start
    clock2 = Clock()
    rerun = Rerun(clock2, advance=3500.0)
    loop2, out2, _ = make(tmp_path / "b", [rotate("f1", 90.0), FINISH, rotate("f1", 0.0)], [[F3]], clock=clock2,
                          deadline=clock2.t + 5000, final_estimate=600.0, rerun=rerun)
    summary = loop2.run()
    assert summary["stop"] == {"round": 1, "reason": "deadline"} and len(rerun.calls) == 1


def test_a_round_cut_before_its_rerun_keeps_its_edits(tmp_path):
    clock = Clock()
    estimate = {"s": 0.0}

    def grow():
        return estimate["s"]

    def slow_finish(body):
        estimate["s"] = 10_000.0           # the planner used the time: the final stages no longer fit
        return FINISH

    loop, out, _ = make(tmp_path, [rotate("f1", 90.0), slow_finish], [[F3]], clock=clock, deadline=clock.t + 7200,
                        final_estimate=grow)
    summary = loop.run()
    assert summary["rounds"][0]["stop"] == "deadline" and loop.rerun.calls == []
    rerun = next(e for e in log_of(out)["events"] if e["kind"] == "rerun")
    assert rerun["status"] == "skipped" and "final renders" in rerun["note"]
    assert OV.Overrides(out).accepted()                         # the edit reaches the final chain


def test_rerun_failure_stops_the_loop(tmp_path):
    loop, _out, _ = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3]], rerun=Rerun(status="failed"))
    assert loop.run()["stop"]["reason"] == "rerun_failed"


def test_routing_picks_the_earliest_stage_and_the_changed_views():
    def acc(tool, args, **res):
        return {"tool": tool, "args": args, "result": dict({"accepted": True}, **res)}

    edits = [acc("set_camera", {"view_id": "cam_r2_1"}, rerun_from="build"),
             acc("rotate_piece", {"piece_id": "f1"}, rerun_from="refit", changed_ids=["f1"]),
             acc("set_room_type", {"room_id": "r2"}, rerun_from="layout")]
    assert LP.route(edits) == "layout"
    assert LP.route(edits[:2]) == "refit" and LP.route(edits[:1]) == "build"
    geo = acc("correct_geometry", {}, rerun_from="pipeline_final", applied=False)
    assert LP.route([geo]) is None and LP.route([geo] + edits[:1]) == "build"
    assert LP.route([acc("rerun_stage", {"stage": "polish"}, rerun_from="polish")]) == "polish"
    from test_agent_helpers import CAMERAS
    rooms = {"f1": "r1", "f3": "r2"}
    assert LP.changed_views(CAMERAS, edits[1:2], rooms.get) == ["cam_r1_1"]
    assert LP.changed_views(CAMERAS, edits, rooms.get) == ["cam_r1_1", "cam_r2_1"]
    assert LP.changed_views(CAMERAS, [acc("set_exterior", {})], rooms.get) == ["ext_1"]
    assert LP.changed_views(CAMERAS, [acc("set_material", {})], rooms.get) == ["cam_r1_1", "cam_r2_1", "ext_1"]
    assert LP.changed_views(CAMERAS, [acc("remove_camera", {"view_id": "ext_1"})], rooms.get) == []


def test_the_planner_budget_and_bad_calls(tmp_path):
    many = {"tool_calls": [{"name": "rotate_piece", "arguments": {"piece_id": "f2", "front_deg": a,
                                                                   "reason": "try it"}} for a in (0, 90, 180, 270)]
            + [{"name": "move_piece", "arguments": {"piece_id": "f2", "center": "here", "reason": "x x x"}}]}
    loop, out, model = make(tmp_path, [many, FINISH], [[F3]], max_calls=3, max_rounds=1)
    summary = loop.run()
    r = summary["rounds"][0]
    assert r["calls"] == 3 and r["accepted"] == 3
    assert len(model.chat_requests()) == 1               # the budget is used up: no further call this round
    assert [e["kind"] for e in log_of(out)["events"]].count("edit") == 3
    loop2, out2, _ = make(tmp_path / "b", [{"tool_calls": [{"name": "move_piece", "arguments": {
        "piece_id": "f2", "center": "here", "reason": "x x x"}}]}, FINISH], [[F3]], max_rounds=1)
    s2 = loop2.run()
    assert s2["rounds"][0]["schema_errors"] == 1 and s2["stop"]["reason"] == "no_edit"
    rej = next(e for e in log_of(out2)["events"] if e["kind"] == "rejected_edit")
    assert "schema" in rej["validation"]["failed_checks"][0] and LG.validate_log(log_of(out2)) == []


def test_the_vision_critic_is_screened_by_code(tmp_path):
    answer = {"findings": [
        {"check": "F4", "severity": "major", "target": "f1", "message": "the bed faces the window", "evidence_image": 2},
        {"check": "F9", "severity": "critical", "target": "f99", "message": "a giant box", "evidence_image": 1},
        {"check": "F3", "severity": "major", "target": "f2", "message": "not on the wall", "evidence_image": 1},
        {"check": "F3", "severity": "critical", "target": "f1", "message": "same as the code", "evidence_image": 1},
        {"check": "F9", "severity": "minor", "target": "r1", "message": "odd", "evidence_image": 4}]}
    critic = [answer, {"findings": []}, {"findings": []}]       # r1, r2, ext_1
    loop, out, model = make(tmp_path, [FINISH], [[F3]], critic=critic, vision=True, max_rounds=1)
    loop.run()
    reqs = model.critic_requests()
    assert len(reqs) == 3
    for r in reqs:
        assert M.count_images(r["messages"]) <= 4 and r["response_format"]["json_schema"]["strict"] is True
    first = reqs[0]["messages"][1]["content"]
    labels = [p["text"] for p in first if p["type"] == "text"]
    assert labels[0].startswith("Image 1: top-down") and labels[1].startswith("Image 2: render of view cam_r1_1")
    findings = [e for e in log_of(out)["events"] if e["kind"] == "finding" and e["source"] == "vision"]
    kept = [e for e in findings if not e.get("dropped")]
    dropped = {e["target"] + ":" + e["checklist"]: e["dropped"] for e in findings if e.get("dropped")}
    assert [(e["checklist"], e["target"]) for e in kept] == [("F4", "f1")]
    assert "not an id" in dropped["f99:F9"] and "code contradicts" in dropped["f2:F3"]
    assert "duplicate" in dropped["f1:F3"] and "does not exist" in dropped["r1:F9"]
    assert kept[0]["model"] == "mock/agent" and kept[0]["call_id"] == "r1-v1"


def test_the_vision_critic_asks_only_changed_rooms_again(tmp_path):
    critic = [{"findings": []}, {"findings": [{"check": "F4", "severity": "major", "target": "f3",
                                               "message": "sofa faces the wall", "evidence_image": 1}]},
              {"findings": []}, {"findings": []}]                  # r1, r2, ext_1; round 2: r1
    chat = [{"tool_calls": [{"name": "rotate_piece", "arguments": {"piece_id": "f1", "front_deg": 90.0,
                                                                   "reason": "head on the wall"}}]}, FINISH,
            {"content": "nothing more"}]
    loop, out, model = make(tmp_path, chat, [[F3], []], critic=critic, vision=True, max_rounds=2)
    summary = loop.run()
    # round 1: r1, r2, ext_1; round 2: only r1 (changed); r2's F4 is carried over, so the loop goes on
    assert len(model.critic_requests()) == 4
    assert summary["rounds"][1]["findings"]["major"] == 1 and summary["stop"]["reason"] == "no_edit"


def test_final_round_takes_critical_findings_only(tmp_path):
    loop, out, model = make(tmp_path, [rotate("f1", 90.0), FINISH],
                            [[], [violation("F4", "major", "f3", "r2"), F3]])
    assert loop.run()["stop"]["reason"] == "no_finding" and model.chat_requests() == []
    res = loop.final_round(2)
    assert res["final"] is True and res["accepted"] == 1
    assert loop.rerun.calls == [("refit", ["cam_r1_1"], 2, True)]
    task = model.chat_requests()[0]["messages"][1]["content"]
    assert "critical findings" in task and '"f1"' in task and '"f3"' not in task
    data = log_of(out)
    assert data["finished_utc"] and LG.validate_log(data) == []


def test_prune_images_keeps_the_newest_four(tmp_path):
    img = {"type": "image_url", "image_url": {"url": "data:image/png;base64,AA"}}
    msgs = [{"role": "user", "content": [img, img, {"type": "text", "text": "a"}]},
            {"role": "user", "content": [img, img, img]}]
    LP.prune_images(msgs)
    assert M.count_images(msgs) == 4 and msgs[0]["content"][0]["type"] == "text"


@pytest.mark.parametrize("bad", [{"seq": 1, "round": 1, "t": "x", "kind": "edit"},
                                 {"seq": 1, "round": 1, "t": "x", "kind": "finding", "source": "code"},
                                 {"seq": 1, "round": 1, "t": "x", "kind": "magic"}])
def test_the_log_schema_refuses_incomplete_entries(bad):
    data = {"schema_version": "0.1", "kind": "agent_log", "project": "p", "model": "m", "revision": "r",
            "events": [bad], "calls": []}
    assert LG.validate_log(data)


def test_the_planner_works_room_by_room_worst_room_first(tmp_path):
    """Pod G2 (real02): one planner session for 252 findings fixed one room and called finish. Now each room gets its
    own session (the room with the most critical findings first), so a finish in one room does not end the round."""
    major_r1 = violation("F4", "major", "f1", "r1", "the bed faces the wall")
    crit_r2 = violation("F3", "critical", "f3", "r2", "the sofa stands in the middle")
    chat = [rotate("f3", 90.0, "the sofa back on the wall"), FINISH, rotate("f1", 90.0), FINISH]
    loop, out, model = make(tmp_path, chat, [[major_r1, crit_r2], []])
    summary = loop.run()
    assert summary["accepted"] == 2
    edits = [e["target"] for e in log_of(out)["events"] if e["kind"] == "edit"]
    assert edits == ["f3", "f1"]                                     # r2 (critical) first, then r1
    first_tasks = [m["messages"][1]["content"] for m in model.requests if m.get("tools")
                   and len(m["messages"]) == 2]
    assert "in r2" in first_tasks[0] and "in r1" in first_tasks[1]
