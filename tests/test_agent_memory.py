"""The agent's memory across rounds (docs/milestone12.md §5.4 D19 "memory", §1.4: real02 G2d 108 of 177 rejections
were exact repeats; real03 run 3: 11 of 17 rejections of round 2 repeated round 1).

Checked: the canonical edit key (reason ignored, numbers to 3 decimals), the ledger survives a new loop (a resumed
pod), an edit identical to an earlier rejection is refused by the tools WITHOUT a validator call (in a later round
too), a dry run is free (no try counted, nothing stored, logged), and every validated edit is recorded."""
from __future__ import annotations

import json

from test_agent_helpers import FakeEdits, fake_validators, project
from wenart.agent import log as LG
from wenart.agent import memory as MEM
from wenart.agent import overrides as OV
from wenart.agent import tools as TL


def ctx_for(out, round_no=1, memory=None, edits=None):
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    return TL.ToolContext.load(out, round=round_no, model_id="mock/agent", log=log, overrides=OV.Overrides(out),
                               apply_edit=edits or FakeEdits(), validators=fake_validators(),
                               memory=memory or MEM.Memory(out), sync=lambda b: b)


def test_the_edit_key():
    a = MEM.edit_key("move_piece", {"piece_id": "f1", "center": [2.00001, 3], "reason": "one"})
    b = MEM.edit_key("move_piece", {"center": [2.0, 3.0004], "piece_id": "f1", "reason": "another reason"})
    assert a == b and a != MEM.edit_key("move_piece", {"piece_id": "f1", "center": [2.1, 3.0]})
    assert MEM.edit_key("rotate_piece", {"piece_id": "f1", "front_deg": 90}) != MEM.edit_key(
        "set_front", {"piece_id": "f1", "front_deg": 90})


def test_the_ledger_is_kept_across_loops(tmp_path):
    m = MEM.Memory(tmp_path)
    m.visit("r1", 1)
    m.record("r1", 1, "set_front", {"piece_id": "f1", "front_deg": 355, "reason": "x"},
             {"accepted": False, "failed_checks": ["front_into_wall: 0.01 m to the wall"]})
    m.record("r1", 1, "set_front", {"piece_id": "f1", "front_deg": 90, "reason": "x"}, {"accepted": True})
    m.set_open("r1", ["move_group on g1"])
    again = MEM.Memory(tmp_path)
    assert again.visits("r1") == 1 and again.room("r1")["open"] == ["move_group on g1"]
    assert again.repeat_of("r1", "set_front", {"piece_id": "f1", "front_deg": 355.0, "reason": "y"})["reasons"] == [
        "front_into_wall: 0.01 m to the wall"]
    assert again.repeat_of("r1", "set_front", {"piece_id": "f1", "front_deg": 90}) is None      # accepted, not refused
    assert again.repeat_of("r2", "set_front", {"piece_id": "f1", "front_deg": 355}) is None
    data = json.loads(MEM.memory_path(tmp_path).read_text())
    assert data["version"] == 1 and set(data["rooms"]["r1"]) == {"visits", "accepted", "rejected", "candidates_tried",
                                                                 "open", "plans"}


def test_a_repeated_rejected_edit_is_refused_without_validation(tmp_path):
    out = project(tmp_path)
    edits = FakeEdits()
    mem = MEM.Memory(out)
    reg = TL.build_registry()
    ctx = ctx_for(out, 1, mem, edits)
    bad = {"piece_id": "f1", "front_deg": 355, "reason": "into the wall"}
    first = reg.call(ctx, "rotate_piece", bad)
    assert not first["accepted"] and len(edits.calls) == 1
    # round 2, a new context and a new reason: refused by the memory, the validator is not called
    ctx2 = ctx_for(out, 2, MEM.Memory(out), edits)
    again = reg.call(ctx2, "rotate_piece", dict(bad, reason="try once more"))
    assert not again["accepted"] and again["refused_by_memory"] and len(edits.calls) == 1
    assert again["failed_checks"][0].startswith("memory: the same edit was rejected in round 1: front_into_wall")
    assert ctx2.refused_repeats == 1 and MEM.Memory(out).refused_repeats == 1
    # a different edit of the same piece is validated
    assert reg.call(ctx2, "rotate_piece", dict(bad, front_deg=90))["accepted"] and len(edits.calls) == 2
    room = MEM.Memory(out).room("r1")
    assert [e["tool"] for e in room["rejected"]] == ["rotate_piece"] and len(room["accepted"]) == 1


def test_a_dry_run_is_free(tmp_path):
    out = project(tmp_path)
    edits = FakeEdits()
    reg = TL.build_registry()
    ctx = ctx_for(out, 1, MEM.Memory(out), edits)
    for _ in range(5):                                   # more than MAX_TRIES: dry runs count no try
        res = reg.call(ctx, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f2", "front_deg": 90}})
        assert res["would_accept"] and "nothing was applied" in res["note"]
    assert ctx.tries == {} and ctx.accepted == [] and not OV.overrides_path(out).exists()
    assert ctx.piece("f2")["front_deg"] == 270.0 and MEM.Memory(out).room("r1")["accepted"] == []
    bad = reg.call(ctx, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f2", "front_deg": "south"}})
    assert not bad["would_accept"] and bad["failed_checks"][0].startswith("schema")
    assert ctx.dry_runs == 6
    events = [e for e in ctx.log.events if e["kind"] == "dry_run"]
    assert len(events) == 6 and events[0]["status"] == "would_accept" and events[0]["room_id"] == "r1"
    assert LG.validate_log(ctx.log.data()) == []
    # the real edit afterwards is validated and stored
    assert reg.call(ctx, "rotate_piece", {"piece_id": "f2", "front_deg": 90, "reason": "to the room"})["accepted"]


def test_a_dry_run_reports_an_earlier_rejection(tmp_path):
    out = project(tmp_path)
    reg = TL.build_registry()
    ctx = ctx_for(out)
    reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 355, "reason": "x x"})
    res = reg.call(ctx, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f1", "front_deg": 355}})
    assert not res["would_accept"] and res["failed_checks"][0].startswith("memory: rejected in round 1")
