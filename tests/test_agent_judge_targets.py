"""The AI judge's and the inspector's findings are targets of the edits on them in every edit of a round (Argus P10,
"the agent tried N times and code refused every try"; the big loop's round 4 of real06, run 20261026-183115-full).

Checked against the code before the fix (the tests fail there):

1. the big loop's final round: after the round's first accepted edit the dry re-check's list (the round's list from
   then on) had dropped every judge finding (``source: judge``; only ``source: vision`` was kept), so the
   ``swap_model`` on the piece of the judge's critical Q5 was refused "no target finding" (seq 4214);
2. the dry re-check keeps a judge finding on an unchanged target and counts it as re-judged on a changed one; a judge's
   "the room is empty" stays through a set_room_type (seq 4197 set r_L1_soyunma_odasi to "hall" and counted 56
   findings "removed"); a gone judge critical is no code measure (``critical_cleared``);
3. a Q5 "the two armchairs are a mismatched set" is a model's look (``wrong_model``: swap_model), not one piece too
   many (``wrong_type``);
4. ``target_findings`` reads the finding ids the edit's reason names (seq 4215: a move of the plant f_L0_013 for the
   walkway finding "c:G11:d_L0_001" on the door it blocks), never a look on another target;
5. the memory refuses the repeat of a "no target finding" only while the round's list has no target for it (seq 4216:
   the repeat naming "j:judge_cam_r_L1_ebeveyn_y_odasi_2:1" was refused without validation);
6. Argus AI's work (no id) gets an id, and a judge problem without a tool or a stage is dropped with the reason in the
   log, never silently.

CPU only: MockModel scripted answers and the fakes of ``test_agent_helpers``."""
from __future__ import annotations

import json

from PIL import Image

from test_agent_helpers import FakeEdits, FixesWhatItTouched, ScriptedCritic, building, fake_validators, project
from test_agent_helpers import violation
from test_m13_agent import FINISH, Clock, ctx_for, log_of, rotate
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import tools as TL

F3 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")
Q5_TEXT = ("The two nightstands are a mismatched set. f2 is a low-poly, faceted model in a pinkish tone, while its "
           "twin is a smooth oak one. They are different models, styles and colours.")


def judge(check, severity, target, message, view="cam_r1_1", n=1, room="r1") -> dict:
    """A finding as ``judge.judge_view`` makes it."""
    call = f"judge_{view}"
    return {"id": f"j:{call}:{n}", "source": "judge", "check": check, "severity": severity, "target": target,
            "room_id": room, "message": message, "evidence": {"view": view, "image": 1, "call_id": call}}


def swap(pid, asset, reason):
    return {"tool_calls": [{"name": "swap_model", "arguments": {"piece_id": pid, "asset_id": asset,
                                                                 "reason": reason}}]}


def make(tmp_path, chat, critic_rounds, critic=()):
    out = project(tmp_path)
    model = MM.MockModel(chat=chat, critic=list(critic))
    code = ScriptedCritic(critic_rounds)
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)}, clock=Clock(),
                        code_critic=code, recheck=FixesWhatItTouched(code), vision=False, apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, workers=1,
                        catalog_loader=lambda: object())
    return loop, out, model


# --------------------------------------------------------------------------
# 1. the big loop's final round: the judge's Q5 is the swap's target after another accepted edit
# --------------------------------------------------------------------------

def test_the_judges_finding_is_the_target_of_its_swap_after_the_rounds_first_accepted_edit(tmp_path):
    """real06 round 4 (seq 4197 then 4214): the measure hands the judge's problems to the final round; the session
    first fixes a code finding (accepted), then swaps the model of the judge's Q5 piece: accepted, its target is the
    judge's Q5, and the judge's finding on a piece no edit touched is still in the round's list."""
    loop, out, model = make(tmp_path, [rotate("f1", 90.0),
                                       swap("f2", "ns_oak", "replace the low-poly pinkish nightstand with the oak "
                                                            "model of its twin"), FINISH],
                            [[F3], [F3]])
    final = out / TL.FINAL_RENDER_DIR
    ctx = loop.context(4, TL.FINAL_RENDER_DIR)
    for cam in ctx.cameras():
        final.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 48), (180, 170, 160)).save(final / f"{cam['name']}_preview.jpg")

    def reply(body):
        text = json.dumps(body["messages"][-1]["content"])
        if "Room r1" in text:
            return {"client_ready_score": 2, "tags": ["mismatched_set"], "note": "the nightstands do not match",
                    "problems": [{"check": "Q5", "severity": "critical", "target": "f2", "message": Q5_TEXT}]}
        if "Room r2" in text:
            return {"client_ready_score": 3, "tags": ["looks_acceptable"], "note": "a plain sofa",
                    "problems": [{"check": "D2", "severity": "minor", "target": "f3",
                                  "message": "the sofa f3 is a crude low-poly model"}]}
        return {"client_ready_score": 4, "tags": ["looks_acceptable"], "note": "fine", "problems": []}

    model.critic_script = [reply] * 3
    loop.measure(4)
    assert {(f["source"], f["check"], f["target"]) for f in loop.extra_findings} >= {("judge", "Q5", "f2"),
                                                                                      ("judge", "D2", "f3")}
    res = loop.final_round(4)
    events = [e for e in log_of(out)["events"] if e.get("round") == 4]
    edits = [e for e in events if e["kind"] == "edit"]
    rejected = [e for e in events if e["kind"] == "rejected_edit"]
    assert [e["tool"] for e in edits] == ["rotate_piece", "swap_model"], [e["validation"] for e in rejected]
    sw = edits[1]
    assert sw["target"] == "f2" and sw["checklist"] == "Q5" and sw["severity"] == "critical"
    acc = sw["evidence"]["acceptance"]
    assert acc["target"] == ["Q5:f2"] and acc["accepted"] is True and acc["before"] == ["Q5:f2"]
    assert acc["reason"].startswith("finding Q5:f2 gone") and "re-measured by the next round" in acc["note"]
    assert edits[0]["evidence"]["acceptance"]["after"] == ["Q5:f2"]     # the rotate kept the judge's finding
    assert not rejected and res["accepted"] == 2
    # the judge's finding on f3 (no edit touched f3) stayed in the round's list: never counted as removed
    assert acc["removed"] == 1, acc                   # Q5:f2 only (the first edit's F3 was already gone)
    first = edits[0]["evidence"]["acceptance"]
    assert first["removed"] == 1, first               # F3:f1 only: the judge's Q5 on f2 is no removal of a rotate
    assert LG.validate_log(log_of(out)) == []


# --------------------------------------------------------------------------
# 2. the dry re-check: a judge finding is a vision finding
# --------------------------------------------------------------------------

def test_the_dry_recheck_keeps_a_judge_finding_on_an_unchanged_target_and_re_judges_it_on_a_changed_one():
    q5 = judge("Q5", "critical", "f2", Q5_TEXT)
    d2 = judge("D2", "minor", "f3", "the sofa f3 is a crude low-poly model", view="cam_r2_1", room="r2")
    argus = {"id": "a:AI1:f3", "source": "argus", "check": "D2", "severity": "major", "target": "f3",
             "message": "Argus: the sofa's model is a placeholder"}
    f3 = CC.finding(F3)
    before = [f3, q5, d2, argus]
    # an edit of f1 (its F3 gone in the code re-check): every judge / Argus finding stays where nothing changed
    after = LP.after_findings([], before, {"f1"}, building())
    assert {(f["source"], f["check"], f["target"]) for f in after} == {("judge", "Q5", "f2"), ("judge", "D2", "f3"),
                                                                       ("argus", "D2", "f3")}
    ok, why = LP.accept_edit(before, after, {"target_finding": {"check": "F3", "target": "f1"}})
    assert ok and "1 critical/major finding(s) removed" in why, why
    # an edit of f2: the judge's Q5 on it is re-judged after the re-render (gone in the dry re-check): accepted
    after2 = LP.after_findings([dict(f3)], before, {"f2"}, building())
    assert {CS.finding_key(f) for f in after2} == {("F3", "f1"), ("D2", "f3")}
    ok, why = LP.accept_edit(before, after2, {"target_finding": {"check": "Q5", "target": "f2"}})
    assert ok and why.startswith("finding Q5:f2 gone"), why
    assert CS.is_vision(q5) and CS.is_vision(argus) and CS.is_vision({"source": "vision"})
    assert not CS.is_vision(f3) and not CS.is_vision({}) and not CS.is_vision(None)


def test_a_judges_empty_room_stays_through_a_set_room_type_and_a_gone_judge_critical_is_no_code_measure():
    """real06 seq 4197: set_room_type of the empty dressing room r_L1_soyunma_odasi to "hall" was accepted for the
    judge's "the dressing room is completely empty" (a set_room_type re-solves no layout)."""
    empty = judge("Q4", "critical", "r1", "The dressing room is completely empty, with no wardrobe or bench.")
    assert CS.cause_of(empty, building()) == "empty_room"
    kept = LP.room_type_kept("set_room_type", {"room_id": "r1", "room_type": "hall"}, [empty], building())
    assert [CS.finding_key(f) for f in kept] == [("Q4", "r1")]
    # critical_cleared: the critical target gone is the judge's (unmeasured), the major kept: no exception
    g11 = CC.finding(violation("G11", "major", "f2", "r1", "its front use zone is not reached by a walkway"))
    q5 = judge("Q5", "critical", "f2", Q5_TEXT)
    before_by = {CS.finding_key(f): f for f in (q5, g11)}
    after_by = {CS.finding_key(g11): g11}
    assert CS.critical_cleared([("Q5", "f2"), ("G11", "f2")], [("G11", "f2")], before_by, after_by) is None


# --------------------------------------------------------------------------
# 3. a Q5 mismatch is a model's look
# --------------------------------------------------------------------------

def test_a_q5_mismatched_set_is_a_wrong_model_and_an_extra_piece_stays_a_wrong_type():
    b = {"furniture": [{"id": "f_L1_017", "type": "armchair", "room_id": "r1"},
                       {"id": "f_L0_017", "type": "table_dining", "room_id": "r1"}], "rooms": [{"id": "r1"}]}

    def cause(target, message, source="judge"):
        return CS.cause_of({"check": "Q5", "target": target, "message": message, "source": source}, b)

    real06 = ("The two armchairs are a mismatched set. f_L1_017 is a low-poly, faceted chair in a pinkish tone, while "
              "f_L1_018 is a smooth, classic 'Egg' chair in brown.")
    assert cause("f_L1_017", real06) == "wrong_model"
    assert "swap_model" in CS.tools_for_finding({"check": "Q5", "target": "f_L1_017", "message": real06})
    assert cause("f_L1_017", "the same shape in two different colours: a pair should match") == "wrong_model"
    assert cause("f_L0_017", "three tables where one belongs: an extra table") == "wrong_type"


# --------------------------------------------------------------------------
# 4. the reason names the finding
# --------------------------------------------------------------------------

def test_target_findings_read_the_finding_ids_the_reason_names(tmp_path):
    ctx = ctx_for(tmp_path)
    g11 = CC.finding(violation("G11", "critical", "d1", "r1", "no 0.60 m walkway from door d1 to door d2"))
    look = judge("D2", "major", "f3", "the sofa is a crude low-poly model", view="cam_r2_1", room="r2")
    q5 = judge("Q5", "critical", "f2", Q5_TEXT)
    ctx.findings = [g11, look, q5]
    move = {"piece_id": "f2", "center": [0.9, 3.0],
            "reason": f"nudge the nightstand to clear the walkway ({g11['id']})"}
    assert [f["id"] for f in TL.target_findings(ctx, "move_piece", move)] == [g11["id"]]
    # a look on another target is no target of this edit; the finding on the edit's own target is
    other = dict(move, reason=f"also fixes {look['id']}")
    assert [f["id"] for f in TL.target_findings(ctx, "move_piece", other)] == [q5["id"]]
    # a finding the tool does not fix is never taken from the reason
    assert TL.reason_findings(ctx.findings, "rotate_piece", dict(move, reason=f"{g11['id']}")) == []
    # whole ids only
    assert TL.names_id(f"fixes {q5['id']} (Q5, f2).", q5["id"])
    assert not TL.names_id(f"fixes {q5['id']}0", q5["id"]) and not TL.names_id(f"{g11['id']}#2", g11["id"])


# --------------------------------------------------------------------------
# 5. the memory and a "no target finding"
# --------------------------------------------------------------------------

def test_the_repeat_of_a_no_target_finding_naming_its_finding_is_validated_again(tmp_path):
    """real06 seq 4214 / 4216: the memory refused the repeat whose reason named the judge's finding."""
    ctx = ctx_for(tmp_path, memory=MEM.Memory(project(tmp_path)))
    ctx.round = 4
    args = {"piece_id": "f2", "asset_id": "ns_oak", "reason": "replace the pinkish nightstand"}
    ctx.memory.record("r1", 4, "swap_model", args,
                      {"accepted": False, "failed_checks": ["acceptance: no target finding: an edit must name the "
                                                            "finding it fixes (check id and target id)"]})
    assert TL._repeat_of(ctx, "r1", "swap_model", args) is not None        # still no target: refused
    q5 = judge("Q5", "critical", "f2", Q5_TEXT)
    ctx.findings = [q5]
    named = dict(args, reason=f"Fixes {q5['id']} (Q5, f2)")
    assert TL._repeat_of(ctx, "r1", "swap_model", named) is None           # a target now: validated again
    assert ctx.memory.repeat_of("r1", "swap_model", named, round_no=4) is not None
    assert ctx.memory.repeat_of("r1", "swap_model", named, round_no=4, skip_bookkeeping=True) is None


# --------------------------------------------------------------------------
# 6. Argus AI's work gets an id; a judge problem without a tool is logged as dropped
# --------------------------------------------------------------------------

def test_the_extra_work_gets_ids_and_a_judge_problem_without_a_tool_is_logged_as_dropped(tmp_path):
    loop, out, _ = make(tmp_path, [FINISH], [[]])
    q7 = judge("Q7", "major", "d1", "a plain slab door", n=2)
    unknown = judge("ZZ", "major", "f1", "something no tool fixes", n=3)
    loop.extra_findings = [judge("Q5", "critical", "f2", Q5_TEXT),
                           {"check": "D2", "severity": "major", "target": "f3", "source": "argus", "room": None,
                            "message": "Argus: a placeholder sofa"},
                           {"check": "D2", "severity": "major", "target": "f3", "source": "argus", "room": None,
                            "message": "Argus: a placeholder sofa, again"}, q7, unknown]
    work = loop.extra_work()
    assert [f["id"] for f in work] == ["j:judge_cam_r1_1:1", "a:D2:f3", "a:D2:f3#2", "j:judge_cam_r1_1:2",
                                       "j:judge_cam_r1_1:3"]
    assert "id" not in loop.extra_findings[1] and all("cause" not in f for f in work)
    loop.round(1)
    found = [e for e in log_of(out)["events"] if e["kind"] == "finding" and e.get("source") in ("judge", "argus")]
    by = {e["checklist"]: e for e in found}
    assert by["Q7"].get("report_to") == "openings" and not by["Q7"].get("dropped")
    assert "no agent tool" in str(by["ZZ"].get("dropped"))
