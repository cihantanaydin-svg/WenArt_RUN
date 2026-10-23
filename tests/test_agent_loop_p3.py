"""Fix round after pod P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"), track A_agent.

What the P3 real04 run showed and these tests pin (CPU only: MockModel, the fakes of ``test_agent_helpers``):

- the context: the building session's prompt grew 6,866 -> 17,606 -> 19,745 -> 22,294 -> >=28,673 tokens with its tool
  results and the 5th call passed the 32,768-token context; the client sent the 400 three times and the round
  stopped "the agent model did not answer". Now ``loop.ContextBudget`` budgets the NEXT prompt (old tool results
  become stubs, the last 2 replies stay whole), a refused prompt is cut and sent once more, a second refusal ends
  the session like a used-up budget and the round stops ``context_full``; ``model_error`` stays for real errors;
- measured, not predicted: the dry re-checks counted 56 removed findings, the next rounds' critics measured 38; the
  loop's line, the stop event and ``summary()`` now lead with the measured number and label the other "predicted";
- set_lighting: the message asks for half a stop of headroom (``critic_code.LIGHTING_HEADROOM``) while the
  acceptance still clears a view at the factor it needs;
- a decor piece through the roof (the mirror dec_L1_009) is the decor stage's, not the building session's;
- the vision critic's "not a mansard roof" when the build makes the drawn mansard: a code record outranks AI vision;
- an edit's ``log_seq`` is the seq of its log event, also when a parallel session logs in between;
- fix round after P3, part 2 (17 Oct 2026; §14.9): the planner's answer budget is ``min(DEFAULT_MAX_TOKENS 4096,
  room left)``, never below ``MIN_REPLY_TOKENS``, with thinking off too (part 1 asked for a fixed 1536, which cut the
  M12 real04 answer r3-s4-p6 of 2,740 tokens before its tool call); a "length" stop is still logged and counted.
"""
from __future__ import annotations

import json
import types

from test_agent_helpers import building, jpg, project, violation
from test_agent_model import M12_LONG_ANSWER_CALL, M12_LONG_ANSWER_TOKENS, P3_CONTEXT_400
from test_m13_agent import F3, FINISH, dark_manifest, log_of, make, quiet_critic, rotate
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import tools as TL
from wenart.recognition import vlm_client as VC


def reads(n: int, usage: int = 0) -> dict:
    """One planner reply with ``n`` room_brief calls (each about 4,700 characters of JSON in the toy project)."""
    out = {"tool_calls": [{"name": "room_brief", "arguments": {"room_id": "r1"}} for _ in range(n)]}
    if usage:
        out["usage"] = {"prompt_tokens": usage}
    return out


def refuse(body):
    """The server's context-full 400 of P3's r4-p5."""
    raise VC.VLMError(P3_CONTEXT_400)


def down(body):
    raise VC.VLMError("HTTP 503 from http://127.0.0.1:8001/v1/chat/completions: engine dead")


def tool_texts(body: dict) -> list[str]:
    return [m["content"] for m in body["messages"] if m.get("role") == "tool"]


# --------------------------------------------------------------------------
# the context budget
# --------------------------------------------------------------------------

def _assistant(cid: str) -> dict:
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": cid, "type": "function", "function": {"name": "room_brief", "arguments": "{}"}}]}


def _tool(cid: str, ch: str, n: int = 6000) -> dict:
    return {"role": "tool", "tool_call_id": cid, "content": ch * n}


def test_the_budget_counts_the_text_added_since_the_last_answer_and_stubs_the_old_results_first():
    """Fails on the old code (no budget: every tool result stayed up to 12,000 characters until the server refused
    the prompt). The server reports 100 prompt tokens after every answer (as MockModel does), so only the estimate of
    the ADDED text can push the next prompt over the limit. An explicit answer budget of 1536 (the planner's own is
    ``DEFAULT_MAX_TOKENS``, next test)."""
    budget = LP.ContextBudget(8000, 1536)
    assert budget.limit == 8000 - LP.CONTEXT_MARGIN_TOKENS == 6976
    messages = [{"role": "system", "content": "s" * 100}, {"role": "user", "content": "task"}]
    budget.measured(messages, 100)
    messages += [_assistant("c1"), _tool("c1", "a")]
    added = LP.conversation_chars(messages[2:])
    assert budget.estimate(messages) == int(100 + added / LP.CHARS_PER_TOKEN_ADDED) >= 3100
    assert budget.fit(messages) == 1536 and budget.cuts == []           # fits: nothing cut
    budget.measured(messages, 100)
    messages += [_assistant("c2"), _tool("c2", "b")]
    assert budget.fit(messages) == 1536 and budget.cuts == []
    budget.measured(messages, 100)
    messages += [_assistant("c3"), _tool("c3", "c"), _tool("c4", "d")]
    assert not budget.fits(messages)                                    # 100 + ~6,000 + 1,536 > 6,976
    assert budget.fit(messages) == 1536
    first, second, third, fourth = [m["content"] for m in messages if m["role"] == "tool"]
    # the results older than the last 2 replies are a stub with the tool's name; the last 2 replies stay whole
    assert first.startswith(LP.STUB_NOTE) and "room_brief: " + "a" * LP.TOOL_STUB_CHARS in first
    assert second == "b" * 6000 and third == "c" * 6000 and fourth == "d" * 6000
    assert [c["keep_replies"] for c in budget.cuts] == [LP.KEEP_REPLIES] and budget.fits(messages)
    # after a refusal (force): everything but the latest reply; a cut that is not enough cuts the latest too
    budget.measured(messages, 6500)
    assert budget.fit(messages, force=True) >= LP.MIN_REPLY_TOKENS
    tools = [m["content"] for m in messages if m["role"] == "tool"]
    assert tools[1].startswith(LP.STUB_NOTE) and tools[2] == "c" * 6000
    budget.measured(messages, 20000)                                    # the server says: far too big
    assert budget.fit(messages) == LP.MIN_REPLY_TOKENS                  # never below 1,024 tokens
    tools = [m["content"] for m in messages if m["role"] == "tool"]
    assert tools[2] == "c" * LP.LATEST_RESULT_CHARS + " ... " + LP.CUT_NOTE and tools[3].endswith(LP.CUT_NOTE)
    # no context known: no budget
    free = LP.ContextBudget(None, 1536)
    assert free.fit([_assistant("x"), _tool("x", "z", 50000)]) == 1536 and free.cuts == []
    # a tool result enters the conversation cut to 6,000 characters (was 12,000)
    assert len(LP.tool_result_text({"x": "y" * 20000})) == LP.TOOL_RESULT_CHARS + len(" ... " + LP.CUT_NOTE)
    assert LP.tool_result_text({"x": 1}) == '{"x": 1}'


def test_the_budget_asks_for_4096_or_the_room_left_never_below_1024():
    """Fix round after P3, part 2 (17 Oct 2026): fails on part 1's code, where the budget had no default answer
    budget and the loop gave it the planner's fixed 1536. Now it asks for ``min(DEFAULT_MAX_TOKENS, room left)``,
    never below ``MIN_REPLY_TOKENS``: 4096 while it fits, the room left when less is left and nothing can be cut,
    1,024 when even that is not left (the server then refuses and the loop cuts everything but the latest reply)."""
    budget = LP.ContextBudget(32768)
    assert budget.want == MM.DEFAULT_MAX_TOKENS == 4096 and budget.limit == 32768 - LP.CONTEXT_MARGIN_TOKENS
    messages = [{"role": "system", "content": "s" * 100}, {"role": "user", "content": "task"}]
    budget.measured(messages, 1000)
    assert budget.fit(messages) == 4096
    budget.measured(messages, budget.limit - 4096)                      # just fits
    assert budget.fit(messages) == 4096
    budget.measured(messages, budget.limit - 2740)                      # room for the M12 answer r3-s4-p6, no more
    assert budget.fit(messages) == 2740 and budget.cuts == []           # no tool result to cut: the room left
    budget.measured(messages, budget.limit - 300)
    assert budget.fit(messages) == LP.MIN_REPLY_TOKENS == 1024
    # an old tool result is cut before the answer budget is lowered
    big = messages + [_assistant("c1"), _tool("c1", "a"), _assistant("c2"), _tool("c2", "b"),
                      _assistant("c3"), _tool("c3", "c")]
    budget.measured(big, budget.limit - 3000)
    assert budget.fit(big) == 4096 and [c["keep_replies"] for c in budget.cuts] == [LP.KEEP_REPLIES]
    assert [m["content"].startswith(LP.STUB_NOTE) for m in big if m["role"] == "tool"] == [True, False, False]


def test_a_session_whose_prompt_grows_like_p3_cuts_the_old_tool_results_before_the_server_refuses(tmp_path,
                                                                                                 monkeypatch):
    """Fails on the old code: P3's building session (prompts 6,866 -> 17,606 -> 19,745 -> 22,294 tokens, as the
    server reported them) sent its 5th prompt whole and got the context-full 400. Now the 5th prompt has the results
    of replies 1-2 as stubs, replies 3-4 whole, and asks for the planner's 4,096 tokens (part 2; part 1 asked for a
    fixed 1,536)."""
    # The token numbers are P3's and the toy room's brief (about 5,000 characters) puts the 3rd prompt within 1 % of
    # the cut; the extra group options of 23 Oct 2026 (10x) add their names to the brief's program and a third solver
    # candidate, so they are off here: the brief is the one these numbers were set on
    from wenart.furniture import groups as GR

    monkeypatch.setattr(GR, "extra_options", lambda *a, **kw: [])
    chat = [reads(4, 6866), reads(4, 17606), reads(4, 19745), reads(4, 22294), FINISH]
    loop, out, model = make(tmp_path, chat, [[F3]], calls_per_room=20)
    assert model.max_model_len == 32768
    loop.run()
    fifth = model.chat_requests()[4]
    results = tool_texts(fifth)
    assert len(results) == 16
    assert all(r.startswith(LP.STUB_NOTE) for r in results[:8])        # replies 1 and 2
    assert not any(r.startswith(LP.STUB_NOTE) for r in results[8:])    # replies 3 and 4 stay whole
    assert all(json.loads(r)["room"]["id"] == "r1" for r in results[8:])
    assert fifth["max_tokens"] == MM.DEFAULT_MAX_TOKENS == 4096
    assert [r["max_tokens"] for r in model.chat_requests()] == [4096] * 5
    cut = [e for e in log_of(out)["events"] if e["kind"] == "check" and e.get("tool") == LP.CONTEXT_CHECK]
    assert len(cut) == 1 and cut[0]["status"] == "cut" and cut[0]["counts"]["max_model_len"] == 32768
    assert LG.validate_log(log_of(out)) == []


def m12_long(body):
    """The planner's answer r3-s4-p6 of the M12 real04 log (``test_agent_model.m12_long_answer``) as a MockModel
    answer: cut at "length" before its tool call when ``max_tokens`` is under its 2,740 tokens."""
    if int(body["max_tokens"]) < M12_LONG_ANSWER_TOKENS:
        return {"content": "The bed faces the wall, so ...", "finish_reason": "length",
                "usage": {"completion_tokens": int(body["max_tokens"])}}
    return {"content": "The bed faces the wall, so ...", "tool_calls": [M12_LONG_ANSWER_CALL],
            "usage": {"completion_tokens": M12_LONG_ANSWER_TOKENS}}


def test_a_long_valid_planner_answer_keeps_its_tool_call_and_a_length_stop_is_counted(tmp_path):
    """Fix round after P3, part 2 (17 Oct 2026): fails on part 1's code. The planner asked for a fixed 1536 tokens
    with thinking off, so the 2,740-token answer r3-s4-p6 of the M12 real04 log stopped at "length" before its tool
    call, ``plan_session`` saw no tool call and ended the room session with its budget unused (no edit). Now the
    loop asks for ``min(4096, room left)`` and the edit is made; an answer that is still cut is logged with its
    "length" and counted in ``metrics.json``."""
    loop, out, model = make(tmp_path, [m12_long, FINISH], [[F3], []])
    summary = loop.run()
    assert summary["accepted"] == 1
    first = model.chat_requests()[0]
    assert first["max_tokens"] == MM.DEFAULT_MAX_TOKENS == 4096
    calls = {c["call_id"]: c for c in log_of(out)["calls"]}
    assert (calls["r1-p1"]["finish_reason"], calls["r1-p1"]["completion_tokens"]) == ("tool_calls", 2740)
    # a model given a smaller budget (here 2048): the answer is cut, the session ends, "length" is logged and counted
    loop, out, model = make(tmp_path / "small", [m12_long, FINISH], [[F3], []])
    model.max_tokens = 2048
    summary = loop.run()
    assert summary["accepted"] == 0 and model.chat_requests()[0]["max_tokens"] == 2048
    assert {c["call_id"]: c["finish_reason"] for c in log_of(out)["calls"]}["r1-p1"] == "length"
    m = json.loads((out / "orchestrator" / "metrics.json").read_text())
    assert m["finish_reasons"]["chat"]["length"] == 1
    # a model without its own budget asks for DEFAULT_MAX_TOKENS too (part 1: MIN_REPLY_TOKENS = 1,024)
    loop, out, model = make(tmp_path / "none", [m12_long, FINISH], [[F3], []])
    model.max_tokens = None
    summary = loop.run()
    assert summary["accepted"] == 1 and model.chat_requests()[0]["max_tokens"] == 4096


def test_a_refused_prompt_is_cut_and_sent_once_more_and_a_second_refusal_ends_the_session_not_the_model(tmp_path):
    """Fails on the old code: the 400 was sent 3 times (attempts 3), the session ended with an error and the round
    stopped ``model_error`` ("the agent model did not answer") although the model had answered 4 times (P3 round 4).
    Now: one POST for the refused prompt, one smaller retry after the cut, then the session ends like a used-up
    budget and the round stops ``context_full``."""
    loop, out, model = make(tmp_path, [reads(1), reads(1), reads(1), reads(1), refuse, refuse], [[F3]])
    summary = loop.run()
    assert summary["stop"]["reason"] == "context_full" and summary["accepted"] == 0
    assert "no longer fit the agent model's context" in LP.STOPS["context_full"]
    reqs = model.chat_requests()
    assert len(reqs) == 6                                               # 4 answers + the refused one + one retry
    refused, retry = reqs[4], reqs[5]
    assert LP.conversation_chars(retry["messages"]) < LP.conversation_chars(refused["messages"])
    assert [t.startswith(LP.STUB_NOTE) for t in tool_texts(retry)] == [True, True, True, False]
    calls = {c["call_id"]: c for c in log_of(out)["calls"]}
    assert calls["r1-p5"]["attempts"] == 1 and calls["r1-p5"]["finish_reason"] == "context_full"
    assert calls["r1-p5-cut"]["attempts"] == 1 and "maximum context length" in calls["r1-p5-cut"]["error"]
    events = log_of(out)["events"]
    rnd = next(e for e in events if e["kind"] == "round")
    assert rnd["status"] == "context_full" and rnd["counts"]["context_full"] == 1
    ended = [e for e in events if e["kind"] == "check" and e.get("tool") == LP.CONTEXT_CHECK]
    assert ended[0]["status"] == "context_full" and ended[0]["target"] == "r1"
    assert LG.validate_log(log_of(out)) == []


def test_after_the_cut_the_session_goes_on_and_a_dead_server_is_still_a_model_error(tmp_path):
    loop, out, model = make(tmp_path, [reads(1), reads(1), refuse, FINISH], [[F3]])
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_edit"                       # the retry answered: no error at all
    assert {c["call_id"]: c.get("error") for c in log_of(out)["calls"]}["r1-p3-cut"] is None
    # a server that dies after answering (5xx, retried) is a model error, whatever came before
    loop, out, model = make(tmp_path / "dead", [reads(1), down, down, down], [[F3]])
    summary = loop.run()
    assert summary["stop"]["reason"] == "model_error"
    assert {c["call_id"]: c["attempts"] for c in log_of(out)["calls"]}["r1-p2"] == 3


# --------------------------------------------------------------------------
# measured, not predicted
# --------------------------------------------------------------------------

def test_the_loop_reports_the_measured_number_and_labels_the_dry_recheck_count_predicted(tmp_path):
    """Fails on the old code: the printed line, the stop note and ``summary()["findings_removed"]`` were the dry
    re-checks' count (P3: 56), which the next rounds' critics did not confirm (38)."""
    lines: list[str] = []
    loop, out, model = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3, violation("F6", "major", "f2", "r1")],
                                                                      []])
    loop.out = lines.append
    summary = loop.run()
    assert summary["findings_removed_predicted"] == 1                   # the dry re-check: F3 only
    assert summary["findings_removed"] == 2 and summary["findings_removed_per_round"] == {"1": 2}   # measured
    assert any("findings removed 1 (predicted by the dry re-check)" in line for line in lines)
    stop = next(e for e in log_of(out)["events"] if e["kind"] == "stop")
    # pins changed on purpose at the integration of the fix round after P5 (loop.stop_note): the measured rounds are
    # named, the prediction is the same rounds' only, and the new findings and the net follow
    assert stop["note"] == ("2 critical/major findings removed in round 1 (measured by the next round's critics; the "
                            "dry re-checks of the same rounds predicted 1); 0 new, net 2; 1 accepted edits in 2 rounds")
    assert stop["counts"] == {"findings_removed": 2, "findings_removed_predicted": 1, "accepted": 1,
                              "findings_new": 0, "findings_net": 2, "findings_removed_predicted_same_rounds": 1}
    ed = next(e for e in log_of(out)["events"] if e["kind"] == "edit")
    assert "(predicted; the next round measures)" in ed["evidence"]["acceptance"]["reason"]
    m = json.loads((out / "orchestrator" / "metrics.json").read_text())
    assert m["findings_removed"]["dry_recheck_is"] == "predicted" and m["findings_removed"]["total"] == 2
    assert m["finish_reasons"]["chat"] == {"tool_calls": 2}          # rotate_piece, then finish


# --------------------------------------------------------------------------
# set_lighting: headroom in the message, the acceptance unchanged
# --------------------------------------------------------------------------

def test_a_dark_view_asks_for_headroom_but_is_cleared_at_the_factor_it_needs():
    """Fails on the old code: the message asked for exactly the needed factor (x1.82), the render gained less than
    predicted (P3: 0.1-1.3 stops for x2.8-2.87) and the planner set the room twice (x2.83, then x2.95). The verifier
    of P3 kept the linear acceptance: the view still counts clear at the needed factor."""
    found = {f["target"]: f for f in CC.run(building(), {}, dark_manifest(), **quiet_critic())["findings"]}
    bed_ = found["cam_r1_2"]
    m = bed_["evidence"]["metrics"]
    assert m["set_lighting_factor"] == 1.82 and m["set_lighting_suggested"] == round(1.82 * 2 ** 0.5, 2) == 2.57
    assert CC.LIGHTING_HEADROOM == 2 ** 0.5
    assert "set_lighting factor x2.57 on r1 (the view needs about x1.82" in bed_["message"]
    # capped at x3; a view beyond the cap gets no suggestion (report-only)
    lit = building()
    lit["agent_overrides"] = {"lighting": {"r1": {"factor": 1.5, "reason": "dark"}}}
    again = next(f for f in CC.run(lit, {}, dark_manifest(), **quiet_critic())["findings"] if f["target"] == "cam_r1_2")
    assert again["evidence"]["metrics"]["set_lighting_suggested"] == 3.0
    assert "set_lighting_suggested" not in found["cam_r1_1"]["evidence"]["metrics"]
    # the acceptance: x1.82 clears the view (no headroom needed), x1.8 does not
    at = building()
    at["agent_overrides"] = {"lighting": {"r1": {"factor": 1.82, "reason": "dark"}}}
    assert LP.lighting_kept(bed_, at) is None
    at["agent_overrides"]["lighting"]["r1"]["factor"] = 1.8
    assert LP.lighting_kept(bed_, at) is not None
    assert CS.cause_of(bed_) == "lighting"


# --------------------------------------------------------------------------
# a decor piece through the roof
# --------------------------------------------------------------------------

def decor_building() -> dict:
    b = building()
    b["decor"] = [{"id": "dec_L1_009", "type": "mirror", "room_id": "r1", "host_id": None}]
    return b


def test_a_decor_piece_through_the_roof_is_reported_to_the_decor_stage_not_sent_to_the_building(tmp_path):
    """Fails on the old code: P3's X2 "decor_dec_L1_009 pokes through the roof" had no room (the critic and
    ``sessions_for`` mapped furniture only), its cause was ``under_roof`` with the furniture tools, and the building
    session tried "relayout_room on building" for 4 rounds (refused: no room 'building')."""
    x2 = {"check": "X2", "severity": "critical", "target": "dec_L1_009", "room_id": None,
          "message": "decor_dec_L1_009 pokes through the roof (top 5.26 m)", "metrics": {"top": 5.2556}}
    b = decor_building()
    res = CC.run(b, {}, None, **quiet_critic(exterior_fn=lambda *a: {"violations": [x2]}))
    f = next(f for f in res["findings"] if f["check"] == "X2")
    assert f["room_id"] == "r1"                                         # the decor's room
    assert CS.cause_of(f, b) == "decor_under_roof" == CS.cause_of(f) and CS.tools_for_finding(f) == []
    assert CS.REPORT_TO["decor_under_roof"] == "decor" and "decor stage" in CS.no_tool_reason(f)
    assert CS.cause_of(dict(f, target="f1"), b) == "under_roof"         # a furniture piece keeps its tools
    fixable, not_yours = BR.classify([f], b, "r1", {}, {}, {})
    assert fixable == [] and not_yours[0]["cause"] == "decor_under_roof"
    fixable, not_yours = BR.classify([f], b, None, {}, {}, {})          # the building session neither
    assert fixable == [] and "decor stage" in not_yours[0]["why"]
    # the loop: no session for it, the finding event names the stage it is reported to
    out = project(tmp_path)
    for name in ("building_decor.json", "building_final.json", "building.json"):
        (out / name).write_text(json.dumps(b))
    loop = LP.AgentLoop(out, MM.MockModel(), code_critic=lambda bb, s, m: CC.run(
        bb, s, m, **quiet_critic(exterior_fn=lambda *a: {"violations": [dict(x2)]})), vision=False,
        out=lambda s: None, workers=1)
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_fixable" and summary["rounds"][0]["rooms_fixable"] == []
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "finding" and e["checklist"] == "X2")
    assert ev["room_id"] == "r1" and ev["cause"] == "decor_under_roof" and ev["report_to"] == "decor"
    assert "no agent tool edits decor" in ev["not_yours"]
    # sessions_for maps a decor target without a room to its room too (a vision finding has none)
    ctx = loop.context(1)
    sessions, cov = loop.sessions_for(ctx, [CC.finding(dict(x2, check="F9", message="odd mirror"))], ("critical",))
    assert "building" not in cov["fixable_rooms"]                       # before: ["building"]


# --------------------------------------------------------------------------
# the vision critic and the roof type
# --------------------------------------------------------------------------

P3_ROOF_CLAIM = "The roof is a standard hipped or gable roof, not a mansard roof as specified in the brief."


def roof_building(override=None) -> dict:
    b = building()
    b["roof"] = {"type": "mansard", "type_source": "plan_roof_lines", "pitches_deg": [{"value": 32.5},
                                                                                    {"value": 11.3}],
                 "overhang": {"value": 0.5}}
    if override:
        b["agent_overrides"] = {"exterior": {"roof": override}}
    return b


def test_the_vision_roof_type_claim_is_dropped_when_the_build_makes_the_drawn_roof(tmp_path):
    """Fails on the old code: P3's vision critic called the built mansard "a standard hipped or gable roof, not a
    mansard roof as specified in the brief" (critical in rounds 3-4) and the finding was kept; the prompt said only
    "roof: mansard". A code record outranks AI vision; a roof the agent overrode to another type keeps the claim."""
    preview = jpg(tmp_path / "ext_1_preview.jpg")
    answer = {"findings": [
        {"check": "X2", "severity": "critical", "target": "building", "message": P3_ROOF_CLAIM, "evidence_image": 1},
        {"check": "X2", "severity": "major", "target": "building", "evidence_image": 1,
         "message": "The roof does not cover the entire building outline; the rear facade is exposed."}]}
    code = {"findings": [], "checks": []}
    model = MM.MockModel(critic=[answer, answer])
    p3 = roof_building({"type": "mansard", "pitch_deg": 45, "overhang_m": 0.8})
    res = CV.critique_exterior(model, p3, "ext_1", preview=preview, plan_crop=None, code=code, call_id="r3-v1")
    assert [f["message"] for f in res["kept"]] == [answer["findings"][1]["message"]]     # coverage stays
    assert res["dropped"][0]["message"] == P3_ROOF_CLAIM and "outranks AI vision" in res["dropped"][0]["dropped"]
    prompt = json.dumps(model.critic_requests()[0]["messages"])
    assert "roof as built: mansard (from plan_roof_lines), pitch 45 / 11.3 deg, overhang 0.8 m." in prompt
    # an override to another type: the drawings say mansard, the build makes a flat roof; vision may be right
    flat = roof_building({"type": "flat"})
    res = CV.critique_exterior(model, flat, "ext_1", preview=preview, plan_crop=None, code=code, call_id="r3-v2")
    assert P3_ROOF_CLAIM in [f["message"] for f in res["kept"]]
    assert "roof as built: flat (from agent override)" in CV.roof_note(flat) and "drawings say mansard" in \
        CV.roof_note(flat)
    assert not CV.roof_matches(flat) and CV.roof_matches(p3) and not CV.roof_matches(building())
    # the claims of the P3 / M12 logs: type claims vs coverage and other problems
    assert CV.is_roof_type_claim("The roof is flat, but the building specification requires a mansard roof.")
    assert CV.is_roof_type_claim("The roof is a standard gable (pitched) roof, but the building specification "
                                 "requires a mansard roof.")
    assert not CV.is_roof_type_claim("The roof is not a closed surface; the interior is visible from above, the "
                                     "roof geometry is missing or transparent.")
    assert not CV.is_roof_type_claim("The building is described as having 4 levels, but the render shows 2.")
    assert not CV.is_roof_type_claim("A gable wall rises above the roof.")


# --------------------------------------------------------------------------
# log_seq under parallel sessions
# --------------------------------------------------------------------------

def test_an_edit_log_seq_is_its_event_seq_when_another_session_logs_in_between(tmp_path):
    """Fails on the old code: ``_next_log_seq`` predicted ``next_seq()`` before the edit was logged; with 4 parallel
    sessions another event took that seq first (P3: 7 of 39 edits had a log_seq 1-2 below their event)."""
    from test_agent_helpers import FakeEdits, fake_validators
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    ov = OV.Overrides(out)
    ctx = TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=ov, apply_edit=FakeEdits(),
                              validators=fake_validators())
    log.event("plan", 1, room_id="r1")                                  # seq 1
    reg = TL.build_registry()
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "against the wall"})
    assert res["accepted"] and res["log_seq"] == 2
    other = log.event("dry_run", 1, tool="move_piece")                  # a parallel session logs first
    assert other["seq"] == 3
    edit = log.event("edit", 1, seq=res["log_seq"], tool="rotate_piece")
    assert edit["seq"] == 2 == OV.Overrides(out).edits[-1]["result"]["log_seq"]
    assert [e["seq"] for e in log.events] == [1, 2, 3] and log.next_seq() == 4
    # a seq that was not reserved (or is used already) is ignored: no duplicate
    assert log.event("check", 1, seq=2)["seq"] == 4 and log.event("check", 1, seq=99)["seq"] == 5
    # a reserved seq never logged leaves a gap, never a duplicate
    gap = log.reserve()
    assert gap == 6 and log.event("check", 1)["seq"] == 7
    # the loop logs the edit with the reserved seq
    loop, out2, _ = make(tmp_path / "loop", [rotate("f1", 90.0), FINISH], [[F3], []])
    loop.run()
    data = log_of(out2)
    ed = next(e for e in data["events"] if e["kind"] == "edit")
    assert OV.Overrides(out2).edits[-1]["result"]["log_seq"] == ed["seq"]
    seqs = [e["seq"] for e in data["events"]]
    assert seqs == sorted(seqs) and len(seqs) == len(set(seqs))


# --------------------------------------------------------------------------
# the scheduler's client of the served key
# --------------------------------------------------------------------------

def test_the_scheduler_gives_the_agent_model_the_served_keys_context():
    """Fails on the old code: ``make_agent_model`` built the client without the server's context, so the loop could
    not budget a prompt; a dotted bake-off key was read flat (``models.get("bakeoff.fp8")`` is None)."""
    from wenart.run.scheduler import Orchestrator
    models = {"agent": {"id": "Qwen/Qwen3.8-27B-FP8", "revision": "r1",
                        "server_flags": "--enable-auto-tool-choice --max-model-len 16384 --max-num-seqs 4"},
              "bakeoff": {"fp8": {"id": "org/model-fp8", "revision": "r2", "server_flags": "--max-model-len 32768"}}}

    def fake(key):
        return types.SimpleNamespace(agent_model_factory=None, models=models,
                                     opts=types.SimpleNamespace(agent_key=key))

    m = Orchestrator.make_agent_model(fake("agent"), "http://127.0.0.1:8001/v1", None)
    assert m.model == "Qwen/Qwen3.8-27B-FP8" and m.max_model_len == 16384
    assert m.max_tokens == MM.DEFAULT_MAX_TOKENS == 4096              # part 2: thinking off too (part 1: 1536)
    b = Orchestrator.make_agent_model(fake("bakeoff.fp8"), "http://127.0.0.1:8001/v1", None)
    assert b.model == "org/model-fp8" and b.revision == "r2" and b.max_model_len == 32768
