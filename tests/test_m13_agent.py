"""Milestone 13 agent loop (docs/milestone13.md §1.5, §3.0 K4, §13.2 rows ``loop.py`` and ``edit_ops.py``; track T4).

Acceptance by finding removal (``causes.accept_edit`` = ``loop.accept_edit``: the targeted finding gone in the dry
re-check, no new critical finding, the old score rule as a second condition; rejected edits logged with both finding
lists; ``findings_removed`` as the success number), tools by cause (``loop.tools_for_finding``: F8 around an unbuilt
anchor, S2 within tolerance, X2 under the roof), building-wide tools only in the building session, an idempotent
``set_exterior``, ``retype_piece`` that builds the piece through the fit in the project's licence mode (a mock
catalogue), ``swap_model`` refusing an S2 cut below 0.03 m, ``place_group`` re-solving the drawn group,
``MAX_ROUNDS`` = 3, the brief's licence mode / drawn groups / below-library list in the critic's prompt, and the
vision critic's findings dropped where no tool exists. CPU only: MockModel, the fakes of ``test_agent_helpers``, the
fake vLLM server for the critic's strict schema."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import _m11_room as M
from fakes.fake_vlm import FakeVLM
from test_agent_helpers import (FakeEdits, FixesWhatItTouched, ScriptedCritic, building, fake_validators, project,
                                violation)
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import metrics as MX
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.furniture import edit_ops as E
from wenart.furniture import groups as GR
from wenart.furniture import locked as LK

ROOT = Path(__file__).resolve().parents[1]
FINISH = {"tool_calls": [{"name": "finish", "arguments": {"verdict": "done"}}]}
F3 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")
META = {"reason": "test", "round": 2, "log_seq": 3, "model": "mock"}


def finding(check, severity, target, room_id=None, message="wrong", **metrics):
    return CC.finding(violation(check, severity, target, room_id, message) | {"metrics": metrics})


def rotate(pid, front, reason="the headboard belongs on the wall"):
    return {"tool_calls": [{"name": "rotate_piece", "arguments": {"piece_id": pid, "front_deg": front,
                                                                   "reason": reason}}]}


def edit(op, **args):
    return dict({"op": op}, **META, **args)


class Clock:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


def make(tmp_path, chat, critic_rounds, **kw):
    out = project(tmp_path)
    model = MM.MockModel(chat=chat, critic=kw.pop("critic", []))
    critic = ScriptedCritic(critic_rounds)
    kw.setdefault("recheck", FixesWhatItTouched(critic))
    kw.setdefault("workers", 1)
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)}, clock=Clock(),
                        code_critic=critic, vision=kw.pop("vision", False), apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, **kw)
    return loop, out, model


def log_of(out) -> dict:
    return json.loads((out / "orchestrator" / "log.json").read_text())


def ctx_for(tmp_path, **kw):
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    kw.setdefault("apply_edit", FakeEdits())
    kw.setdefault("validators", fake_validators())
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out), **kw)


# --------------------------------------------------------------------------
# accept_edit (pure) and findings_removed
# --------------------------------------------------------------------------

def test_accept_edit_needs_the_target_finding_gone_and_no_new_critical():
    before = [finding("F3", "critical", "f1", "r1", "headboard off the wall"), finding("F6", "major", "f2", "r1")]
    target = {"target_finding": {"check": "F3", "target": "f1"}}
    ok, why = LP.accept_edit(before, [finding("F6", "major", "f2", "r1")], target)
    assert ok and "F3:f1 gone" in why and "1 critical/major finding(s) removed" in why
    kept, why = LP.accept_edit(before, before, target)
    assert not kept and why.startswith("finding F3:f1 is still there")
    new_crit, why = LP.accept_edit(before, [finding("S2", "critical", "f9", "r1", "cuts the wall")], target)
    assert not new_crit and why.startswith("new critical finding S2:f9")
    # a new MAJOR finding does not reject (a misread stove removed leaves "kitchen has no stove")
    ok2, _ = LP.accept_edit(before, [finding("G9", "major", "r1", "r1", "kitchen has no stove")], target)
    assert ok2
    # several targets (a checklist step): every one must be gone
    both = {"target_finding": [{"check": "F3", "target": "f1"}, {"check": "F6", "target": "f2"}]}
    assert LP.accept_edit(before, [finding("F6", "major", "f2", "r1")], both)[0] is False
    assert LP.accept_edit(before, [], both)[0] is True
    assert LP.accept_edit is CS.accept_edit and LP.tools_for_finding is CS.tools_for_finding


def test_accept_edit_keeps_the_old_score_rule_as_the_second_condition():
    before = [finding("F3", "critical", "f1", "r1")]
    edit_ = {"target_finding": {"check": "F3", "target": "f1"}, "penalty_before": 10.0, "penalty_after": 16.0}
    ok, why = LP.accept_edit(before, [], edit_)
    assert not ok and "penalty rose 10 -> 16" in why
    assert LP.accept_edit(before, [], dict(edit_, penalty_after=10.0))[0]
    # without penalties the scores decide (a higher score is better)
    assert not LP.accept_edit(before, [], {"target_finding": {"check": "F3", "target": "f1"}, "score_before": 60,
                                           "score_after": 54})[0]


def test_accept_edit_refuses_an_edit_without_a_target_finding():
    before = [finding("F3", "critical", "f1", "r1")]
    ok, why = LP.accept_edit(before, [], {})
    assert not ok and why.startswith("no target finding")
    ok, why = LP.accept_edit(before, [], {"target_finding": {"check": "F4", "target": "f7"}})
    assert not ok and "not among the findings before the edit" in why


def test_findings_removed_counts_critical_and_major_keys_only():
    before = [finding("F3", "critical", "f1"), finding("F6", "major", "f2"), finding("LG", "minor", "f3"),
              finding("F3", "critical", "f1", message="twice")]
    assert LP.findings_removed(before, []) == 2
    assert LP.findings_removed(before, [finding("F3", "critical", "f1")]) == 1
    assert CS.key_list(before) == ["F3:f1", "F6:f2"]


# --------------------------------------------------------------------------
# tools by cause
# --------------------------------------------------------------------------

@pytest.mark.parametrize("fnd,cause,first,never", [
    # round 2: an F8 around an unbuilt anchor goes to the tools that build the ANCHOR (never the chair's move)
    (finding("F8", "major", "f_1", "r", "chair stands around table_dining f_2, which is not built (library gap)",
             cause="anchor_not_built", missing_anchor="f_2", anchor_type="table_dining"), "missing_anchor",
     "place_group", "move_piece"),
    (finding("F8", "major", "f_1", "r", "nightstand stands around unknown u_2, which is not built (untyped)",
             cause="anchor_not_built", missing_anchor="u_2", anchor_type="unknown"), "anchor_untyped",
     "retype_piece", "move_piece"),
    # round 2: a G8 of a tiered minimum (small kitchen, drawn run) is a scored term: reported only, no tool
    (finding("G8", "minor", "f_1", "r", "kitchen aisle 0.75 m in front of kitchen_counter f_1, needs ≥ 0.90 m",
             aisle_m=0.75, needs_m=0.9, tier="small_kitchen"), "soft_minimum", None, "fix_fixture"),
    (finding("G8", "major", "f_1", "r", "kitchen aisle 0.75 m in front of kitchen_counter f_1, needs ≥ 1.07 m",
             aisle_m=0.75, needs_m=1.07), "fixture_clearance", "fix_fixture", "move_piece"),
    (finding("F8", "major", "f_1", "r", "chair stands alone in the room (no wall, no table within 0.8 m)"),
     "floating", "move_piece", "set_exterior"),
    (finding("S2", "major", "f_1", "r", "toilet cuts wall w_1 by 0.013 m", depth_m=0.0127), "within_tolerance",
     None, "swap_model"),
    (finding("S2", "major", "f_1", "r", "desk cuts wall w_1 by 0.095 m", depth_m=0.095), "collision", "move_piece",
     "set_exterior"),
    (finding("X2", "critical", "f_L1_046", "r_L1", "shoe cabinet 1.90 m under the sloped ceiling"), "under_roof",
     "move_piece", "set_exterior"),
    (finding("X2", "major", "ro_001", None, "the roof leaves 2 corners uncovered"), "roof", "set_exterior",
     "move_piece"),
    (finding("D2", "major", "f_1", "r", "a crude low-poly toilet"), "wrong_model", "swap_model", "move_piece"),
    (finding("F3", "critical", "f_1", "r", "its back is not on a wall (0.94 m off)"), "off_wall", "move_piece",
     "rotate_piece"),
    (finding("X3", "major", "building", None, "9.7 m of blank facade"), "facade", None, "set_exterior"),
    (finding("G10", "major", "r_1", "r_1", "bathroom without a shower", missing="shower"), "missing_member",
     "complete_group", "fix_fixture"),
    (finding("G10", "major", "f_1", "r_1", "toilet f_1: centre 0.33 m from the side wall, needs ≥ 0.38 m",
             part="side"), "fixture_clearance", "fix_fixture", "move_piece"),
    (finding("V1", "major", "ext_5", None, "camera too high"), "exterior_camera", "set_camera", "move_piece"),
    (finding("V1", "major", "cam_r1_1", "r1", "camera inside a piece"), "interior_camera", "set_camera", "add_camera"),
    (finding("NR", "major", "f_9", "r", "untyped drawn piece left for review"), "untyped", "retype_piece",
     "move_piece"),
])
def test_tools_for_finding_by_cause(fnd, cause, first, never):
    assert LP.cause_of(fnd) == cause
    tools = LP.tools_for_finding(fnd)
    if first is None:
        assert tools == [] and CS.no_tool_reason(fnd)
    else:
        assert tools[0] == first
    assert never not in tools


def test_the_cause_uses_the_building_to_tell_a_piece_from_the_roof():
    b = {"furniture": [{"id": "x9", "room_id": "r1"}], "decor": []}
    assert LP.cause_of(finding("X2", "major", "x9"), b) == "under_roof"
    assert LP.cause_of(finding("X2", "major", "x9")) == "roof"          # no prefix, no building: the roof
    unbuilt = {"furniture": [{"id": "f_2", "type": "bed_double", "build": False}]}
    assert LP.cause_of(finding("LG", "minor", "f_2"), unbuilt) == "missing_anchor"
    # round 2: the building says whether the unbuilt anchor is untyped (retype builds it) or typed (re-solve / fit)
    f8 = finding("F8", "major", "f_1", "r", "around f_2, which is not built", cause="anchor_not_built",
                 missing_anchor="f_2")
    assert LP.cause_of(f8, unbuilt) == "missing_anchor" and LP.cause_of(f8) == "missing_anchor"
    assert LP.cause_of(f8, {"furniture": [{"id": "f_2", "type": "unknown", "build": False}]}) == "anchor_untyped"
    assert CS.anchor_of(f8) == "f_2" and CS.anchor_of(finding("F8", "major", "f_1", "r", "alone")) is None
    assert CS.anchor_of(dict(f8, target="f_2")) is None                     # the finding is on the anchor itself
    assert LP.tools_for_finding(dict(f8, cause="anchor_untyped"))[0] == "retype_piece"
    assert set(LP.tools_for_finding(f8)) >= {"place_group", "swap_model", "retype_piece"}
    assert "soft_minimum" in CS.NO_TOOL_REASON and "tier" in CS.NO_TOOL_REASON["soft_minimum"]


def test_is_building_wide():
    assert CS.is_building_wide("set_exterior") and CS.is_building_wide("set_terrain")
    assert CS.is_building_wide("set_camera", {"view_id": "ext_1"}) and not CS.is_building_wide("set_camera",
                                                                                              {"view_id": "cam_r1_1"})
    assert not CS.is_building_wide("move_piece") and not CS.is_building_wide("place_group")
    assert set(CS.BUILDING_WIDE_TOOLS) <= set(TL.PLANNER_BUILDING)


def test_the_brief_classifies_by_cause_and_offers_place_group_for_an_unbuilt_drawn_anchor():
    b = building()
    bed = next(f for f in b["furniture"] if f["id"] == "f1")
    bed["asset"] = {"method": "none", "asset_id": "none:bed_double"}
    bed["library_gap"] = {"type": "bed_double", "step": "none"}
    f8 = finding("F8", "major", "f2", "r1", "nightstand stands around bed_double f1, which is not built",
                 cause="anchor_not_built", missing_anchor="f1")
    out = BR.room_brief(b, "r1", findings=[f8], allowed_fn=lambda b_, pid: {})
    fixable = {f["id"]: f for f in out["findings"]["fixable"]}
    assert fixable["c:F8:f2"]["cause"] == "missing_anchor" and fixable["c:F8:f2"]["tools"][0] == "place_group"
    assert out["drawn_groups"][0]["anchor_id"] == "f1" and out["drawn_groups"][0]["anchor_built"] is False
    assert out["licence_mode"] in ("commercial", "relaxed")
    # the vision critic's findings are "not yours" where no tool exists for the cause
    x3 = dict(finding("X3", "major", "r1", "r1", "a blank wall"), source="vision")
    out2 = BR.room_brief(b, "r1", findings=[x3], allowed_fn=lambda b_, pid: {})
    assert out2["findings"]["fixable"] == [] and "no agent tool" in out2["findings"]["not_yours"][0]["why"]
    # review (T4): a finding whose only tools are building-wide (R4: set_material) is "not yours" in a room session
    # (never offered there, refused at call time) and fixable in the building session
    r4 = finding("R4", "major", "r1", "r1", "the floor look does not match the brief")
    out3 = BR.room_brief(b, "r1", findings=[r4], allowed_fn=lambda b_, pid: {})
    assert out3["findings"]["fixable"] == [] and out3["findings"]["not_yours"][0]["why"].startswith("building-wide: set_material")
    fixable_b, _ = BR.classify([r4], b, None, {}, {}, {})
    assert fixable_b and fixable_b[0]["tools"] == ["set_material"]


def test_an_f8_around_an_unbuilt_anchor_is_fixed_on_the_anchor_through_the_whole_chain():
    """Round 2: the brief names the unbuilt anchor as ``edit_target`` with the tools that build it (checked against
    the anchor's locks, ``edit_ops.allowed_edits``), the default checklist and ``check_plan`` act on the anchor
    although it is not built, and ``tools.target_findings`` hands the F8 to the acceptance of an edit on the anchor."""
    # an untyped anchor: retype_piece types and builds it (the fit's ladder)
    stand = M.fp("n1", "nightstand", (0.22, 3.7), (0.4, 0.4), rotation=90.0, front=0.0)
    box = dict(M.fp("u1", "unknown", (1.02, 2.5), (1.6, 2.0), rotation=90.0, front=None, status="unverified"),
               build=False, not_built_reason="untyped (CLAUDE.md: no untyped piece is built)")
    b = M.building(w=4.5, h=5.0, furniture=[box, stand])
    f8 = finding("F8", "major", "n1", M.ROOM_ID, "nightstand n1 stands around unknown u1, which is not built",
                 cause="anchor_not_built", missing_anchor="u1", anchor_type="unknown")
    brief = BR.room_brief(b, M.ROOM_ID, findings=[f8], allowed_fn=E.allowed_edits)
    (fx,) = brief["findings"]["fixable"]
    assert fx["cause"] == "anchor_untyped" and fx["target"] == "n1" and fx["edit_target"] == "u1"
    assert fx["tools"][0] == "retype_piece" and "move_piece" not in fx["tools"]
    assert "u1" in {p["id"] for p in brief["not_built"]} and "u1" not in {p["id"] for p in brief["pieces"]}
    steps = LP.default_checklist(brief)
    assert steps == [{"finding_ids": [fx["id"]], "tool": "retype_piece", "target": "u1", "why": fx["message"]}]
    plan = {"room_id": M.ROOM_ID, "program": {"keep": True},
            "steps": [{"finding_ids": [fx["id"]], "tool": "retype_piece", "target": "u1", "why": "type the anchor"},
                      {"finding_ids": [fx["id"]], "tool": "move_piece", "target": "n1", "why": "move the stand"},
                      {"finding_ids": [], "tool": "retype_piece", "target": "n1", "why": "no finding names it"}]}
    checked, problems = LP.check_plan(plan, brief, ["retype_piece", "move_piece", "place_group"])
    # the step on the unbuilt anchor stays (the finding names it); the chair's move does not fix the finding; a
    # step without findings on a built piece that allows the tool stays, as before
    assert [s_["target"] for s_ in checked] == ["u1", "n1"] and len(problems) == 1
    assert "move_piece does not fix" in problems[0]
    unnamed = {"room_id": M.ROOM_ID, "program": {"keep": True},
               "steps": [{"finding_ids": [], "tool": "retype_piece", "target": "u1", "why": "no finding names it"}]}
    assert LP.check_plan(unnamed, brief, ["retype_piece"])[1] == ["step 1 (retype_piece on u1): u1 is not built"]
    ctx = TL.ToolContext(project_out=Path("."), building=b)
    ctx.findings = [f8]
    assert TL.target_findings(ctx, "retype_piece", {"piece_id": "u1"}) == [f8]
    assert TL.target_findings(ctx, "move_piece", {"piece_id": "n1"}) == [f8]    # still the only finding on n1
    assert "edit_target" in P.PLANNER_SYSTEM_M12
    # a typed anchor the fit left unbuilt: place_group re-solves the group (the refit builds it); swap_model is not
    # offered on an unbuilt piece (allowed_edits), retype never comes first
    gap = dict(M.fp("b1", "bed_double", (1.02, 2.5), (1.6, 2.0), rotation=90.0, front=0.0),
               asset={"method": "none", "asset_id": "none:bed_double"}, library_gap={"type": "bed_double", "step": "none"})
    b2 = M.building(w=4.5, h=5.0, furniture=[gap, stand])
    f8b = finding("F8", "major", "n1", M.ROOM_ID, "nightstand n1 stands around bed_double b1, which is not built",
                  cause="anchor_not_built", missing_anchor="b1", anchor_type="bed_double")
    brief2 = BR.room_brief(b2, M.ROOM_ID, findings=[f8b], allowed_fn=E.allowed_edits)
    (fx2,) = brief2["findings"]["fixable"]
    assert fx2["cause"] == "missing_anchor" and fx2["edit_target"] == "b1" and fx2["tools"][0] == "place_group"
    assert "swap_model" not in fx2["tools"] and "move_piece" not in fx2["tools"]
    assert LP.default_checklist(brief2)[0]["target"] == "b1"


def test_a_g8_of_a_tiered_minimum_is_report_only():
    b = building()
    g8 = finding("G8", "minor", "f3", "r2", "kitchen aisle 0.75 m in front of kitchen_counter f3, needs ≥ 0.90 m",
                 aisle_m=0.75, needs_m=0.9, tier="small_kitchen")
    out = BR.room_brief(b, "r2", findings=[g8], allowed_fn=lambda b_, pid: {})
    assert out["findings"]["fixable"] == []
    (ny,) = out["findings"]["not_yours"]
    assert ny["cause"] == "soft_minimum" and ny["why"].startswith("a tiered minimum") and "reported only" in ny["why"]
    hard = finding("G8", "major", "f3", "r2", "kitchen aisle 0.75 m in front of kitchen_counter f3, needs ≥ 1.07 m",
                   aisle_m=0.75, needs_m=1.07)
    assert LP.cause_of(hard) == "fixture_clearance" and LP.tools_for_finding(hard) == ["fix_fixture"]


def test_the_exterior_critic_is_told_that_an_allowed_aerial_view_is_no_finding(tmp_path):
    aerial = {"name": "ext_5", "kind": "exterior", "view": "aerial", "aerial_allowed": True,
              "position": [-20, -20, 18], "target": [4, 2, 1.6], "lens_mm": 28.0}
    site = {"name": "ext_7", "kind": "exterior", "view": "aerial", "site_view": True, "aerial_allowed": True,
            "position": [-30, -30, 9], "target": [4, 2, 1.6], "lens_mm": 24.0, "horizon_frac": 0.42}
    corner = {"name": "ext_1", "kind": "exterior", "view": "corner", "position": [-8, -8, 1.6],
              "target": [4, 2, 1.6], "lens_mm": 28.0}
    assert P.camera_note(None) == "" and P.camera_note(corner) == ""
    assert "NOT a finding" in P.camera_note(aerial) and "aerial view" in P.camera_note(aerial)
    assert "site view" in P.camera_note(site) and "X6" in P.camera_note(site)
    assert P.camera_note({"view": "aerial"}).startswith("This view is the aerial view")
    model = MM.MockModel(critic=[{"findings": []}, {"findings": []}])
    b = building()
    preview = Path(tmp_path / "ext_5_preview.jpg")
    from test_agent_helpers import jpg
    jpg(preview)
    code = {"findings": [], "ran": []}
    res = CV.critique_exterior(model, b, "ext_5", preview=preview, plan_crop=None, code=code, call_id="t1",
                               camera=aerial)
    assert res["error"] is None and "NOT a finding" in json.dumps(model.critic_requests()[0])
    CV.critique_exterior(model, b, "ext_1", preview=preview, plan_crop=None, code=code, call_id="t2", camera=corner)
    assert "NOT a finding" not in json.dumps(model.critic_requests()[1])
    # the loop hands the view's camera record of the scene manifest to the critic
    loop, out, model2 = make(tmp_path, [{"content": "nothing"}], [[]], critic=[{"findings": []}] * 3, vision=True,
                             max_rounds=1)
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text())
    scene["cameras"][2] = dict(scene["cameras"][2], view="aerial", aerial_allowed=True)        # ext_1 as the aerial
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene))
    loop.run()
    ext = [r for r in model2.critic_requests() if "exterior view ext_1" in json.dumps(r)]
    assert ext and "NOT a finding" in json.dumps(ext[0])


def test_a_failing_refit_rejects_the_retype_instead_of_crashing():
    # review (T4): fit_piece raising (a broken catalogue entry) is a rejected edit with its reason, not a crash
    class Broken(Cat):
        def candidates(self, ftype):
            raise KeyError("bbox_m")

    b = room_with_review("relaxed")
    res = E.apply_edit(b, edit("retype_piece", piece_id="u1", type="nightstand"), catalog=Broken())
    assert not res["accepted"] and res["failed_checks"][0].startswith("refit:") and "KeyError" in res["failed_checks"][0]
    assert b["needs_review"] and next(f for f in b["furniture"] if f["id"] == "u1")["type"] == "unknown"   # pure


# --------------------------------------------------------------------------
# the loop: acceptance, logging, metrics, rounds
# --------------------------------------------------------------------------

def test_an_edit_whose_finding_stays_is_rejected_and_logged_with_both_lists(tmp_path):
    still = lambda b, s, m: [CC.finding(F3)]                                       # noqa: E731
    loop, out, model = make(tmp_path, [rotate("f1", 90.0), {"content": "I give up"}], [[F3]], recheck=still)
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_edit" and summary["accepted"] == 0 and summary["findings_removed"] == 0
    rej = [e for e in log_of(out)["events"] if e["kind"] == "rejected_edit"]
    assert len(rej) == 1 and rej[0]["validation"]["failed_checks"][0].startswith("acceptance: finding F3:f1 is still")
    acc = rej[0]["evidence"]["acceptance"]
    assert acc["before"] == ["F3:f1"] and acc["after"] == ["F3:f1"] and acc["target"] == ["F3:f1"]
    assert acc["accepted"] is False and acc["removed"] == 0
    assert not OV.Overrides(out).accepted() and loop.rerun is not None
    assert MEM.Memory(out).repeat_of("r1", "rotate_piece", rotate("f1", 90.0)["tool_calls"][0]["arguments"])
    assert LG.validate_log(log_of(out)) == []


def test_an_edit_that_removes_its_finding_is_accepted_and_findings_removed_is_the_number(tmp_path):
    loop, out, model = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3], []])
    summary = loop.run()
    assert summary["stop"]["reason"] == "no_finding" and summary["accepted"] == 1 and summary["findings_removed"] == 1
    events = log_of(out)["events"]
    ed = next(e for e in events if e["kind"] == "edit")
    assert ed["evidence"]["acceptance"]["removed"] == 1 and ed["evidence"]["acceptance"]["after"] == []
    assert ed["checklist"] == "F3" and ed["target"] == "f1"
    rnd = next(e for e in events if e["kind"] == "round")
    assert rnd["counts"]["findings_removed"] == 1
    stop = next(e for e in events if e["kind"] == "stop")
    assert stop["note"].startswith("1 findings removed by 1 accepted edits") and stop["counts"]["findings_removed"] == 1
    assert OV.Overrides(out).accepted()[0]["result"]["acceptance"]["removed"] == 1
    m = json.loads((out / "orchestrator" / "metrics.json").read_text())
    assert m["findings_removed"]["dry_recheck"] == {"1": 1, "2": 0} and m["findings_removed"]["per_round"] == {"1": 1}
    assert m["findings_removed"]["total"] == 1 and m["findings_removed"]["edits_removing_finding"] == 1
    assert LG.validate_log(log_of(out)) == []


def test_a_new_critical_finding_rejects_the_edit(tmp_path):
    # (review of 16 Oct 2026: a check the dry re-check measures on the changed building, F9; the scene checks S1-S6
    # come from the build's files and cannot be new in a dry re-check, ``test_a_finding_an_earlier_edit_removed_...``)
    worse = lambda b, s, m: [CC.finding(violation("F9", "critical", "f2", "r1", "the nightstand cuts the wall"))]  # noqa: E731
    loop, out, _ = make(tmp_path, [rotate("f1", 90.0), {"content": "stop"}], [[F3]], recheck=worse)
    summary = loop.run()
    rej = next(e for e in log_of(out)["events"] if e["kind"] == "rejected_edit")
    assert summary["accepted"] == 0 and "new critical finding F9:f2" in rej["validation"]["failed_checks"][0]
    assert rej["evidence"]["acceptance"]["after"] == ["F9:f2"]


def test_a_finding_an_earlier_edit_removed_does_not_come_back_from_the_stale_manifests():
    """Fails on the old code (review of 16 Oct 2026): the dry re-check rebuilds the scene, view, look and lighting
    findings from the round's manifests, which no edit changes; after an edit had removed S2:f1 (it moved f1), the next
    edit's re-check listed S2:f1 again, as a NEW critical finding, and rejected an edit on another piece. Now those
    findings come from the round's list (``before``): unchanged targets keep theirs, changed ones count as gone."""
    s2_f1 = finding("S2", "critical", "f1", "r1", "the bed cuts the wall", depth_m=0.12)
    v1 = finding("V1", "major", "cam_r1_1", "r1", "the view looks at a wall")
    f3_f2 = finding("F3", "critical", "f2", "r1", "the nightstand faces the wall")
    stale = [s2_f1, v1]                                    # what the scene and render files say all round long
    # edit 1 moved f1: S2:f1 gone, V1 kept
    after1 = LP.after_findings([dict(f) for f in stale + [f3_f2]], [s2_f1, v1, f3_f2], {"f1"}, {})
    assert {(f["check"], f["target"]) for f in after1} == {("V1", "cam_r1_1"), ("F3", "f2")}
    # edit 2 rotates f2 (its F3 gone in the re-measured checks): S2:f1 must not come back from the stale files
    after2 = LP.after_findings([dict(f) for f in stale], after1, {"f2"}, {})
    assert {(f["check"], f["target"]) for f in after2} == {("V1", "cam_r1_1")}
    ok, why = LP.accept_edit(after1, after2, {"target_finding": {"check": "F3", "target": "f2"}})
    assert ok, why
    # a re-measured finding on an unchanged target still comes from the re-check (it may be new)
    f9 = finding("F9", "critical", "f3", "r1", "the chair is through a wall")
    after3 = LP.after_findings([dict(f) for f in stale] + [f9], after1, {"f2"}, {})
    assert ("F9", "f3") in {(f["check"], f["target"]) for f in after3}


def test_max_rounds_is_three(tmp_path):
    assert LP.MAX_ROUNDS == 3
    chat = [rotate("f1", 90.0), FINISH, rotate("f1", 180.0), FINISH, rotate("f1", 0.0), FINISH, rotate("f1", 90.0)]
    loop, out, _ = make(tmp_path, chat, [[F3]])
    assert loop.max_rounds == 3
    summary = loop.run()
    assert summary["stop"]["reason"] == "max_rounds" and len(summary["rounds"]) == 3


def test_the_vision_critics_findings_are_kept_only_where_a_tool_exists(tmp_path):
    # r1: nothing; r2: a crude sofa model (D2 -> swap_model: kept); ext_1: a blank facade (X3: no tool -> dropped)
    critic = [{"findings": []},
              {"findings": [{"check": "D2", "severity": "major", "target": "f3",
                             "message": "the sofa is a crude low-poly model", "evidence_image": 1}]},
              {"findings": [{"check": "X3", "severity": "major", "target": "building",
                             "message": "9.7 m of blank facade", "evidence_image": 1}]}]
    loop, out, model = make(tmp_path, [{"content": "nothing"}], [[]], critic=critic, vision=True, max_rounds=1)
    summary = loop.run()
    events = log_of(out)["events"]
    kept = [e for e in events if e["kind"] == "finding" and not e.get("dropped")]
    dropped = [e for e in events if e["kind"] == "finding" and e.get("dropped")]
    assert [e["checklist"] for e in kept] == ["D2"] and summary["rounds"][0]["findings"]["major"] == 1
    assert len(dropped) == 1 and dropped[0]["checklist"] == "X3" and "no agent tool for the cause facade" in dropped[0]["dropped"]


# --------------------------------------------------------------------------
# tools: building-wide refusal, idempotent set_exterior, the dry run's acceptance
# --------------------------------------------------------------------------

def test_building_wide_tools_are_refused_from_a_room_session(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    roof = {"roof": {"type": "hip", "pitch_deg": 30}, "reason": "close the roof"}
    ctx.begin_session("r1")
    res = reg.call(ctx, "set_exterior", roof)
    assert not res["accepted"] and res["failed_checks"][0].startswith("building_wide:") and "r1" in res["failed_checks"][0]
    cam = {"view_id": "ext_1", "kind": "exterior", "position": [-9, -9, 1.6], "target": [4, 2, 1.6], "lens_mm": 28,
           "reason": "lower"}
    assert reg.call(ctx, "set_camera", cam)["failed_checks"][0].startswith("building_wide:")
    inside = {"view_id": "cam_r1_1", "kind": "interior", "room_id": "r1", "position": [3.0, 0.5, 1.3],
              "target": [1.0, 3.0, 1.2], "lens_mm": 18, "reason": "step back"}
    assert reg.call(ctx, "set_camera", inside)["accepted"]            # an interior camera is the room's
    ctx.end_session()
    ctx.begin_session(LP.BUILDING)
    assert reg.call(ctx, "set_exterior", roof)["accepted"]
    assert len(ctx.rejected) == 2 and len(ctx.accepted) == 2


def test_a_room_session_is_never_offered_a_building_wide_tool():
    reg = TL.build_registry()
    brief = {"room": {"id": "r1"}, "findings": {"fixable": [{"id": "c:X2:f1", "tools": ["set_exterior",
                                                                                         "set_terrain", "move_piece"]}]}}
    offered = LP.offered_tools(reg, brief)
    assert "move_piece" in offered and not set(CS.BUILDING_WIDE_TOOLS) & set(offered)
    assert "set_exterior" in LP.offered_tools(reg, dict(brief, room={"id": LP.BUILDING}))


def test_set_exterior_is_idempotent(tmp_path):
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    roof = {"roof": {"type": "hip", "pitch_deg": 30}, "reason": "close the roof"}
    first = reg.call(ctx, "set_exterior", roof)
    assert first["accepted"] and first["rerun_from"] == "build"
    again = reg.call(ctx, "set_exterior", dict(roof, reason="the roof once more"))
    assert not again["accepted"] and again["failed_checks"][0].startswith("no_change:") and again.get("no_op") is True
    assert len(OV.Overrides(ctx.project_out).accepted()) == 1
    # a value the building already carries is a no-op too; a different one is a change
    ctx.building["site"] = {"fence": "hedge", "trees": 2}
    same = reg.call(ctx, "set_exterior", {"site": {"trees": 2}, "reason": "two trees"})
    assert not same["accepted"] and same["failed_checks"][0].startswith("no_change:")
    more = reg.call(ctx, "set_exterior", {"site": {"trees": 4}, "reason": "four trees"})
    assert more["accepted"]
    assert TL._target("set_exterior", roof) == "exterior:roof" and TL._target("set_exterior", {"reason": "x"}) == "set_exterior"


def test_the_dry_run_answers_with_the_acceptance(tmp_path):
    ctx = ctx_for(tmp_path)
    ctx.findings = [CC.finding(F3)]
    seen = []

    def acceptance(ctx_, tool, args, result, building_after):
        seen.append((tool, args.get("piece_id"), building_after["furniture"][0]["front_deg"]))
        return {"accepted": False, "reason": "finding F3:f1 is still there after the edit", "target": ["F3:f1"],
                "before": ["F3:f1"], "after": ["F3:f1"], "removed": 0, "target_findings": [CC.finding(F3)],
                "after_findings": [CC.finding(F3)]}

    ctx.acceptance = acceptance
    reg = TL.build_registry()
    dry = reg.call(ctx, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f1", "front_deg": 90.0}})
    assert dry["would_accept"] is False and dry["failed_checks"] == ["acceptance: finding F3:f1 is still there after "
                                                                       "the edit"]
    assert seen == [("rotate_piece", "f1", 90.0)] and ctx.building["furniture"][0]["front_deg"] == 270.0
    real = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "turn it"})
    assert not real["accepted"] and real["acceptance"]["reason"].startswith("finding F3:f1 is still")
    assert ctx.building["furniture"][0]["front_deg"] == 270.0 and ctx.rejected and not ctx.accepted


def test_target_findings_follow_the_checklist_then_the_target():
    ctx = TL.ToolContext(project_out=Path("."), building=building())
    f3, f6 = CC.finding(F3), CC.finding(violation("F6", "major", "f1", "r1", "no room beside the bed"))
    ctx.findings = [f6, f3]
    assert [f["check"] for f in TL.target_findings(ctx, "rotate_piece", {"piece_id": "f1"})] == ["F3"]  # worst first
    ctx.begin_session("r1").checklist = [{"tool": "move_piece", "target": "f1", "finding_ids": [f6["id"]]}]
    assert [f["check"] for f in TL.target_findings(ctx, "move_piece", {"piece_id": "f1"})] == ["F6"]
    assert TL.target_findings(ctx, "rotate_piece", {"piece_id": "f3"}) == []
    assert TL.changed_targets("set_exterior", {"roof": {}}, {}, []) == {LP.BUILDING}
    assert TL.changed_targets("move_piece", {"piece_id": "f1"}, {"changed_ids": ["f1", "f2"]}, [f3]) == {"f1", "f2"}


# --------------------------------------------------------------------------
# edit_ops: retype builds, swap refuses, place_group re-solves the drawn group
# --------------------------------------------------------------------------

class Cat:
    """A mock catalogue: one non-commercial nightstand model (usable in relaxed mode only)."""
    parametric_types: list = []

    def __init__(self, entries=None):
        self.entries = list(entries or [NC_NIGHTSTAND])

    def candidates(self, ftype):
        return [e for e in self.entries if e["type"] == ftype]

    def entry(self, asset_id):
        return next((e for e in self.entries if e["id"] == asset_id), None)


NC_NIGHTSTAND = {"id": "ns_nc", "type": "nightstand", "bbox_m": [0.45, 0.42, 0.55], "licence": "CC BY-NC 4.0",
                 "licence_flag": "non_commercial", "styles": ["modern"], "source": "hssd", "name": "ns",
                 "front_axis": "-Y", "front_axis_confidence": 0.9, "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
                 "gltf": "ns.glb"}


def bed():
    return M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)


def untyped_box():
    return dict(M.fp("u1", "unknown", (0.221, 0.93), (0.4, 0.4), rotation=90.0, front=0.0, status="unverified"),
                build=False)


def room_with_review(mode="relaxed"):
    b = M.building(furniture=[bed(), untyped_box()])
    b["project"]["licence_mode"] = mode
    b["needs_review"] = [{"id": "u1", "kind": "untyped_piece", "reason": "drawn piece 0.40 x 0.40 m has no type",
                          "crop": None, "room_id": M.ROOM_ID, "level_id": "L0"}]
    return b


def test_retype_piece_builds_the_piece_in_the_projects_licence_mode():
    b = room_with_review("relaxed")
    res = E.apply_edit(b, edit("retype_piece", piece_id="u1", type="nightstand"), catalog=Cat())
    assert res["accepted"], res["failed_checks"]
    u1 = next(f for f in res["building"]["furniture"] if f["id"] == "u1")
    assert u1["type"] == "nightstand" and u1["drawn_type"] == "unknown" and u1["status"] == "verified"
    assert u1.get("build", True) is True and GR.piece_is_built(u1) and u1["inferred"] is True
    assert u1["asset"]["method"] == "library" and u1["asset"]["asset_id"] == "ns_nc"
    assert u1["asset"]["licence_mode"] == "relaxed" and u1["asset"]["licence_flag"] == "non_commercial"
    assert res["building"]["needs_review"] == [] and u1["adjusted_by_ai"]["retype"]["licence_mode"] == "relaxed"
    assert u1["adjusted_by_ai"]["retype"]["method"] == "library" and u1["adjusted_by_ai"]["reason"] == "test"
    assert LK.check(b, res["building"], "complete") == []
    assert b["needs_review"] and next(f for f in b["furniture"] if f["id"] == "u1")["status"] == "unverified"  # pure
    # commercial mode: the NC model is refused, the ladder builds the piece anyway (never an unbuilt box)
    c = E.apply_edit(room_with_review("commercial"), edit("retype_piece", piece_id="u1", type="nightstand"),
                     catalog=Cat())
    u1c = next(f for f in c["building"]["furniture"] if f["id"] == "u1")
    assert c["accepted"] and u1c["asset"]["method"] in ("module", "parametric") and GR.piece_is_built(u1c)
    assert u1c["asset"]["licence_mode"] == "commercial" and u1c["library_gap"]["step"] == u1c["asset"]["method"]
    assert any(x["id"] == "ns_nc" for x in u1c["asset"]["excluded"])
    # the code critic no longer lists the piece for review
    assert all(v["target"] != "u1" for v in CC.reading_items(c["building"]))


def test_swap_model_refuses_a_cut_within_tolerance_and_the_model_the_piece_has():
    b = M.building(furniture=[bed()])
    cat = Cat([{"id": "bed_a", "type": "bed_double"}, {"id": "bed_b", "type": "bed_double"}])
    small = {"check": "S2", "target": "b1", "severity": "major", "message": "bed cuts wall w_n by 0.013 m",
             "metrics": {"depth_m": 0.0127, "wall_id": "w_n"}, "cause": "within_tolerance"}
    res = E.apply_edit(b, edit("swap_model", piece_id="b1", asset_id="bed_a", target_finding=small), catalog=cat)
    assert not res["accepted"] and res["failed_checks"][0].startswith("within_tolerance:") and "0.013 m" in res["message"]
    big = dict(small, message="bed cuts wall w_n by 0.095 m", metrics={"depth_m": 0.095}, cause="collision")
    ok = E.apply_edit(b, edit("swap_model", piece_id="b1", asset_id="bed_a", target_finding=big), catalog=cat)
    assert ok["accepted"] and ok["building"]["furniture"][0]["asset_pin"] == "bed_a"
    same = E.apply_edit(ok["building"], edit("swap_model", piece_id="b1", asset_id="bed_a"), catalog=cat)
    assert not same["accepted"] and same["failed_checks"][0].startswith("no_change:")
    _op, args = E.normalise_edit(dict(edit("swap_model", piece_id="b1", asset_id="bed_a"), target_finding=small))
    assert E.schema_errors("swap_model", args) == []                  # the strict schema takes target_finding
    assert "target_finding" in TL.EDIT_META and "target_finding" not in TL.build_registry().tools["swap_model"].parameters["properties"]


def test_place_group_re_solves_the_drawn_group_of_an_unbuilt_anchor():
    gap = dict(bed(), asset={"method": "none", "asset_id": "none:bed_double"},
               library_gap={"type": "bed_double", "step": "none", "used": "nothing (not built)"})
    b = M.building(furniture=[gap])
    assert not GR.piece_is_built(gap) and GR.drawn_groups(b, M.ROOM_ID)[0]["built"] == {"b1": False}
    res = E.apply_edit(b, edit("place_group", room_id=M.ROOM_ID, group="sleeping_double"))
    assert res["accepted"], res["failed_checks"]
    beds = [f for f in res["building"]["furniture"] if f["type"] == "bed_double"]
    assert [f["id"] for f in beds] == ["b1"] and beds[0]["drawn_group"]["moved_m"] <= GR.GROUP_MEMBER_MOVE_MAX_M
    assert "b1" in res["changed_ids"] and beds[0]["adjusted_by_ai"]["reason"]
    assert [f["type"] for f in res["building"]["furniture"] if f["source"] == "added_by_ai"][:2] == ["nightstand",
                                                                                                     "nightstand"]
    assert LK.check(b, res["building"], "complete") == []


# --------------------------------------------------------------------------
# the brief and the critic's prompt
# --------------------------------------------------------------------------

def test_the_brief_and_the_critic_prompt_state_the_licence_mode_drawn_groups_and_below_library():
    b = building()
    b["project"]["licence_mode"] = "relaxed"
    bed_ = next(f for f in b["furniture"] if f["id"] == "f1")
    bed_["asset"] = {"method": "parametric", "asset_id": "parametric:bed_double", "fallback_reason": "no model"}
    bed_["library_gap"] = {"type": "bed_double", "step": "parametric", "used": "parametric family"}
    out = BR.room_brief(b, "r1", findings=[], allowed_fn=lambda b_, pid: {})
    assert out["licence_mode"] == "relaxed"
    assert out["below_library"] == [{"id": "f1", "type": "bed_double", "method": "parametric",
                                     "builder": "parametric family"}]
    assert out["drawn_groups"][0]["anchor_id"] == "f1" and out["drawn_groups"][0]["members"] == ["f2"]
    assert next(p for p in out["pieces"] if p["id"] == "f1")["built_as"] == "parametric"
    ctx = CV.room_context(b, "r1", [f for f in b["furniture"] if f["room_id"] == "r1"])
    text = P.room_look_prompt(b["rooms"][0], [f for f in b["furniture"] if f["room_id"] == "r1"], ["cam_r1_1"],
                              ["render of view cam_r1_1"], [], context=ctx)
    assert "Library licence mode: relaxed" in text and "f1 bed_double (parametric: parametric family)" in text
    assert "Drawn groups" in text and "bed_double f1 with f2" in text and "built by our parametric family" in text
    assert "below_library" in P.PLANNER_SYSTEM_M12 and "drawn_groups" in P.PLANNER_SYSTEM_M12


def test_the_critic_schema_is_strict_and_the_fake_vlm_accepts_it_at_temperature_zero():
    schema = CV.LOOK_SCHEMA
    assert schema["additionalProperties"] is False and schema["properties"]["findings"]["items"]["additionalProperties"] is False
    body = MM.critic_body("m", [{"role": "user", "content": "x"}], schema)
    assert body["temperature"] == 0.0
    with FakeVLM(models=["fake/agent"]) as url:
        model = MM.AgentModel(url, "fake/agent", "rev", sleep=lambda s: None, retries=1)
        reply = model.critic([{"role": "system", "content": P.CRITIC_SYSTEM},
                              {"role": "user", "content": "Room r1."}], schema, call_id="t1")
    assert reply.data == {"findings": []}


def test_storeys_do_not_count_level_variants():
    assert CV.storeys_of({"levels": [{"id": "L-1"}, {"id": "L-1b"}, {"id": "L0"}, {"id": "L1"}]}) == 3
    assert CV.storeys_of({"levels": [{"id": "L0"}, {"id": "L1"}]}) == 2


# --------------------------------------------------------------------------
# metrics on the committed real04 log (M12): the numbers behind the diagnosis
# --------------------------------------------------------------------------

def test_findings_removed_on_the_committed_real04_log():
    log = json.loads((ROOT / "results" / "agent" / "real04" / "log.json").read_text())
    m = MX.compute(log)
    fr = m["findings_removed"]
    assert fr["accepted_edits"] == 183 and fr["edits_removing_finding"] == 20          # §1.5: 20 of 183
    assert fr["dry_recheck"] == {} and set(fr["per_round"]) == {"1", "2", "3", "4", "5", "6"}
    assert MX.COMPARE_HEADER[-1] == "findings removed" and MX.compare_row("x", m)[-1] == fr["total"]


def test_the_default_checklist_names_the_kitchen_group_a_g9_completes():
    """CPU pre-flight of 16 Oct 2026 (real04): a G9 names the kitchen (the room, or its kitchen zone
    ``r_L-1b_salon_kitchen``), not a group, so the default step was ``complete_group on r_L-1b_salon_kitchen`` and
    always failed "no group". The step now names the brief's group of that kitchen that misses something; a target
    that is a group id, and a kitchen without such a group, stay as they are."""
    def brief(target, groups):
        return {"room": {"id": "r_L-1b_salon"}, "groups": groups,
                "findings": {"fixable": [{"id": f"c:G9:{target}", "check": "G9", "severity": "major",
                                          "target": target, "message": "kitchen has no fridge (fridge)",
                                          "tools": ["complete_group"]}]}}
    groups = [{"group_id": "r_L-1b_salon.dining", "missing": ["chair"]},
              {"group_id": "r_L-1b_salon_kitchen.island", "missing": []},
              {"group_id": "r_L-1b_salon_kitchen.kitchen_run", "missing": ["fridge"]}]
    assert LP.default_checklist(brief("r_L-1b_salon_kitchen", groups))[0]["target"] == \
        "r_L-1b_salon_kitchen.kitchen_run"
    assert LP.default_checklist(brief("r_L-1b_salon.dining", groups))[0]["target"] == "r_L-1b_salon.dining"
    assert LP.default_checklist(brief("r_L-1b_salon_kitchen", groups[:2]))[0]["target"] == "r_L-1b_salon_kitchen"
    # Review: a G9 on a kitchen room (no zone) shares the prefix with the room's other groups; the group that misses
    # what the finding names is chosen, not the first group that misses anything (an eat-in kitchen's dining chair).
    eat_in = [{"group_id": "r_mutfak.dining", "missing": ["chair"]},
              {"group_id": "r_mutfak.kitchen_run", "missing": ["fridge"]}]
    b = brief("r_mutfak", eat_in)
    b["room"]["id"] = "r_mutfak"
    assert LP.default_checklist(b)[0]["target"] == "r_mutfak.kitchen_run"


# --------------------------------------------------------------------------
# Round 4 (before pod P3's second attempt): lighting_dark findings for the lighting tool; fixed equipment and the
# room-set rule of the acceptance
# --------------------------------------------------------------------------

def dark_manifest():
    """A render manifest with the render's own ``lighting_dark`` records (``render.lighting_dark_entry``): the CPU
    pre-flight's real04 basement salon (wanted +6.37 EV at incident p50 0.010868, critical), a real02-like bedroom
    (+3.87, major) in the same room r1 here, a view within the cap and an exterior view above it."""
    from wenart.blender import render as R
    lim = (-10.3808, 3.0)
    salon = R.lighting_dark_entry("cam_r1_1", "r1", 6.3718, 3.0, lim, 0.010868)
    bed_ = R.lighting_dark_entry("cam_r1_2", "r1", 3.8672, 3.0, lim, 0.05)
    ext = R.lighting_dark_entry("ext_1", None, 4.2, 3.0, lim, 0.01)
    return {"exposure_limits": [-2.0, 3.0],
            "renders": [{"camera": "cam_r1_1", "room_id": "r1", "lighting_dark": salon,
                         "exposure": {"ev": 3.0, "ev_raw": 6.3718, "lighting_dark": salon}},
                        {"camera": "cam_r1_2", "room_id": "r1", "exposure": {"ev": 3.0, "lighting_dark": bed_}},
                        {"camera": "cam_r2_1", "room_id": "r2", "exposure": {"ev": 1.2, "lighting_dark": None}},
                        {"camera": "ext_1", "room_id": None, "exposure": {"ev": 3.0, "lighting_dark": ext}}],
            "lighting_dark": [salon, bed_, ext]}


def quiet_critic(**kw):
    return dict(dict(plausibility_fn=lambda x: {"rooms": {}}, exterior_fn=lambda *a: {"violations": []},
                     views_fn=lambda *a: {"views": {}}, groups_fn=lambda x: {"rooms": {}}, levels_fn=lambda *a: []),
                **kw)


def test_lighting_dark_entries_become_findings_routed_to_set_lighting():
    """Fails on the old code: render.py writes lighting_dark per view (a view whose metered EV passed the +3 cap; P1
    decision §14.3: "a capped view is a lighting_dark finding routed to the lighting tools"), but no agent code read
    them (CPU pre-flight of 16 Oct 2026: grep found only blender/ and run/ab.py)."""
    from wenart.blender import render as R
    assert CC.LIGHTING_DARK_CHECK == CS.LIGHTING_DARK_CHECK == R.LIGHTING_DARK_CHECK
    res = CC.run(building(), {}, dark_manifest(), **quiet_critic())
    assert {c["source"]: c["status"] for c in res["checks"]}["lighting"] == "ok"
    dark = {f["target"]: f for f in res["findings"] if f["check"] == "lighting_dark"}
    assert sorted(dark) == ["cam_r1_1", "cam_r1_2", "ext_1"]          # one per view (entries and list are the same)
    salon, bed_, ext = dark["cam_r1_1"], dark["cam_r1_2"], dark["ext_1"]
    assert salon["id"] == "c:lighting_dark:cam_r1_1" and salon["severity"] == "critical" and salon["room_id"] == "r1"
    m = salon["evidence"]["metrics"]
    assert m["ev_wanted"] == 6.3718 and m["ev_cap"] == 3.0 and m["factor_needed"] == round(2 ** 3.3718, 2) == 10.35
    assert "the room needs about x10.35 its light, set_lighting gives up to x3" in salon["message"]
    assert bed_["severity"] == "major" and "set_lighting factor about x1.82 on r1" in bed_["message"]
    # routing: the lighting cause and set_lighting; an exterior view is report-only with the reason
    assert CS.cause_of(bed_) == "lighting" and CS.tools_for_finding(bed_) == ["set_lighting"]
    assert CS.cause_of(ext) == "lighting_exterior" and CS.tools_for_finding(ext) == []
    assert "no agent tool sets their strength" in CS.no_tool_reason(ext)
    # review of 16 Oct 2026: a view no factor clears (the salon needs x10.35, set_lighting gives up to x3) has no tool:
    # an edit counts only when its finding is gone (CLAUDE.md), so the view is report-only with the reason
    assert CS.cause_of(salon) == "lighting_beyond_cap" and CS.tools_for_finding(salon) == []
    assert "no add-lamp tool" in CS.no_tool_reason(salon)
    fixable, not_yours = BR.classify([salon, bed_], building(), "r1", {}, {}, {})
    assert [(f["target"], f["tools"], f["cause"]) for f in fixable] == [("cam_r1_2", ["set_lighting"], "lighting")]
    assert [(f["target"], f["cause"]) for f in not_yours] == [("cam_r1_1", "lighting_beyond_cap")]
    # review of round 4: set_lighting takes a room id, so the step acts on the view's room (``edit_target``), and the
    # room's accepted set_lighting closes the step (before, the checklist said "set_lighting on cam_r1_2" and the
    # step stayed open into the next round)
    assert [f["edit_target"] for f in fixable] == ["r1"]
    steps = LP.default_checklist({"room": {"id": "r1"}, "groups": [], "findings": {"fixable": fixable}})
    assert [(s["tool"], s["target"], s["finding_ids"]) for s in steps] == [
        ("set_lighting", "r1", ["c:lighting_dark:cam_r1_2"])]
    assert all(LP.step_done(s, "set_lighting", {"room_id": "r1", "factor": 3.0}, {}) for s in steps)
    assert "or the room set_lighting acts on for a view too dark for the EV cap" in P.PLANNER_SYSTEM_M12
    fixable, not_yours = BR.classify([ext], building(), None, {}, {}, {})
    assert fixable == [] and not_yours[0]["cause"] == "lighting_exterior"
    # no render manifest: the family is unavailable, never a silent "ok, nothing dark"
    none = CC.run(building(), {}, None, **quiet_critic())
    assert {c["source"]: c["status"] for c in none["checks"]}["lighting"] == "unavailable"
    assert CC.FAMILY_OF["lighting_dark"] == "lighting" and "lighting_dark" in LP.NOT_REMEASURED
    # review of round 4: set_lighting's factor is absolute and the render metered the room at the factor it has, so
    # the factor to ask for is that factor x factor_needed (before: a room at x1.5, 0.87 stops over, was told "about
    # x1.82", hardly brighter; at x2 it was told a darker x1.82)
    assert bed_["evidence"]["metrics"]["lighting_factor_now"] == 1.0
    assert bed_["evidence"]["metrics"]["set_lighting_factor"] == 1.82
    lit = building()
    for factor, text, want in ((1.5, "set_lighting factor about x2.74 on r1 (it has x1.5 now)", 2.74),
                               (2.0, "the room needs about x1.82 its light, set_lighting gives up to x3 (it has x2 "
                                     "now)", 3.65)):
        lit["agent_overrides"] = {"lighting": {"r1": {"factor": factor, "reason": "dark"}}}
        got = next(f for f in CC.run(lit, {}, dark_manifest(), **quiet_critic())["findings"]
                   if f["target"] == "cam_r1_2")
        assert text in got["message"], got["message"]
        assert got["evidence"]["metrics"]["set_lighting_factor"] == want
        assert got["evidence"]["metrics"]["factor_needed"] == 1.82


def test_set_lighting_clears_the_dark_views_of_its_room_in_the_dry_recheck(tmp_path):
    """Fails on the old code: the dry re-check cannot re-render, so the render's lighting_dark stayed in the after
    list and the acceptance refused every set_lighting ("finding ... is still there"). Now a dark view of the room
    counts as gone after set_lighting on the room when the new factor reaches the factor it needs, and the next round
    re-meters it; the edit re-renders the room's views. Review of 16 Oct 2026: the salon view needs x10.35, more than
    the x3 the edit gives, so it stays (predicted, not re-rendered) and is no target; before, both views counted as
    removed (the metrics were read from the wrong key and the re-check saw the building without the new factor)."""
    found = [f for f in CC.run(building(), {}, dark_manifest(), **quiet_critic())["findings"]
             if f["check"] == "lighting_dark" and f["room_id"] == "r1"]
    violations = [{k: f[k] for k in ("check", "severity", "target", "room_id", "message")}
                  | {"metrics": f["evidence"]["metrics"]} for f in found]
    light = {"tool_calls": [{"name": "set_lighting", "arguments": {"room_id": "r1", "factor": 3.0,
                                                                    "reason": "the basement room is too dark"}}]}
    loop, out, _ = make(tmp_path, [light, FINISH], [violations, []],
                        recheck=lambda b, s, m: [CC.finding(v) for v in violations])     # the render did not change
    summary = loop.run()
    assert summary["accepted"] == 1 and summary["findings_removed"] == 1, summary
    ed = next(e for e in log_of(out)["events"] if e["kind"] == "edit")
    assert ed["tool"] == "set_lighting" and ed["evidence"]["acceptance"]["removed"] == 1
    assert ed["evidence"]["acceptance"]["target"] == ["lighting_dark:cam_r1_2"]           # the view x3 can clear
    assert "lighting_dark:cam_r1_1" in ed["evidence"]["acceptance"]["after"]
    assert OV.Overrides(out).agent_overrides()["lighting"]["r1"]["factor"] == 3.0
    assert TL.changed_targets("set_lighting", {"room_id": "r1"}, {}, [], findings=found) == {"r1", "cam_r1_1",
                                                                                          "cam_r1_2"}


def test_accept_edit_refuses_an_edit_that_removed_the_fixture_a_new_room_set_finding_asks_for():
    """Fails on the old code: only a new CRITICAL finding refused an edit, and the room-set findings of one room share
    the key (G10, room id). The CPU pre-flight's scripted round marked 5 real03 toilets as not furniture: 5 major
    G10 "bathroom without a toilet", accepted (102 findings "removed")."""
    shower = finding("G10", "major", "r_bath", "r_bath", "bathroom without a shower or a bathtub",
                     missing="shower|bathtub")
    before = [finding("F7", "critical", "t1", "r_bath", "toilet blocks door d1"), shower]
    no_toilet = finding("G10", "major", "r_bath", "r_bath", "bathroom without a toilet", missing="toilet")
    after = [shower, no_toilet]
    edit_ = {"target_finding": {"check": "F7", "target": "t1"},
             "removed": [{"id": "t1", "type": "toilet", "room_id": "r_bath"}]}
    ok, why = LP.accept_edit(before, after, edit_)
    assert not ok and why == ("new major finding G10:r_bath (bathroom without a toilet): the edit removed toilet t1, "
                              "the fixture the room needs; fixed equipment is treated like walls (CLAUDE.md furniture "
                              "rules)")
    # what stays accepted: the finding was there before; another fixture kind; another room; a minor one (a WC
    # without a washbasin); an edit that removed nothing (no ``removed``: the M13 round-3 callers)
    assert LP.accept_edit(before + [no_toilet], after, edit_)[0]
    assert LP.accept_edit(before, after, dict(edit_, removed=[{"id": "t1", "type": "unknown", "room_id": "r_bath"}]))[0]
    assert LP.accept_edit(before, after, dict(edit_, removed=[{"id": "t1", "type": "toilet", "room_id": "r_wc"}]))[0]
    minor = finding("G10", "minor", "r_bath", "r_bath", "wc without a washbasin", missing="washbasin")
    assert LP.accept_edit(before, [minor], dict(edit_, removed=[{"id": "t1", "type": "washbasin",
                                                                  "room_id": "r_bath"}]))[0]
    assert LP.accept_edit(before, after, {"target_finding": {"check": "F7", "target": "t1"}})[0]
    # G9: the kitchen's hob is a stove; a finding without metrics.missing is read from its words
    k_before = [finding("F7", "critical", "s1", "r_k", "stove blocks door d2")]
    hob = finding("G9", "major", "r_k_kitchen", "r_k", "kitchen r_k_kitchen has no hob (stove)", missing="hob")
    stove = {"target_finding": {"check": "F7", "target": "s1"}, "removed": [{"id": "s1", "type": "stove",
                                                                             "room_id": "r_k"}]}
    assert not LP.accept_edit(k_before, [hob], stove)[0]
    assert not LP.accept_edit(k_before, [finding("G9", "major", "r_k", "r_k", "kitchen has no stove")], stove)[0]
    # the kinds are group_checks' own
    from wenart.furniture import group_checks as GC
    assert {k: CS.SET_KIND_TYPES[k] for k in GC.KITCHEN_FIXTURES} == GC.KITCHEN_FIXTURES
    assert set(CS.SET_KIND_TYPES) >= {"toilet", "washbasin", "shower|bathtub"}


def test_removed_pieces_are_the_pieces_an_edit_took_out_of_the_scene():
    keep = M.fp("k1", "chair", (1.0, 1.0), (0.45, 0.45))
    gone_ = M.fp("g1", "toilet", (2.0, 1.0), (0.4, 0.7), source="added_by_ai")
    marked = M.fp("m1", "washbasin", (3.0, 1.0), (0.6, 0.45))
    retyped = M.fp("r1", "unknown", (4.0, 1.0), (0.5, 0.5))
    unbuilt = dict(M.fp("u1", "stove", (4.0, 3.0), (0.6, 0.6)), build=False)
    before = M.building(furniture=[keep, gone_, marked, retyped, unbuilt])
    after = M.building(furniture=[keep, dict(marked, build=False), dict(retyped, type="nightstand"), unbuilt])
    assert CS.removed_pieces(before, after) == [{"id": "g1", "type": "toilet", "room_id": M.ROOM_ID},
                                                {"id": "m1", "type": "washbasin", "room_id": M.ROOM_ID},
                                                {"id": "r1", "type": "unknown", "room_id": M.ROOM_ID}]
    assert CS.removed_pieces(before, before) == [] and CS.removed_pieces(None, after) == []


def bath_project(tmp_path):
    """A bathroom whose added toilet stands in the door swing (F7 critical, R3 critical) with its drawn washbasin and
    shower: removing the toilet clears F7 and leaves "bathroom without a toilet" (G10 major, the real critic)."""
    from test_agent_helpers import write_json
    basin = M.fp("f_b", "washbasin", (3.0, 3.775), (0.6, 0.45), front=270.0)
    shower = M.fp("f_s", "shower", (4.55, 3.55), (0.9, 0.9), front=270.0)
    toilet = M.fp("a_t", "toilet", (1.0, 0.5), (0.4, 0.7), front=90.0, source="added_by_ai")
    b = M.building(room_type="bathroom", furniture=[basin, shower, toilet])
    out = tmp_path / "bath"
    for name in ("building_decor.json", "building_final.json", "building.json"):
        write_json(out / name, b)
    write_json(out / "style.json", {"palette": {}})
    write_json(out / "scene" / "scene_manifest.json", {"cameras": []})
    return out, b


def test_the_loop_refuses_removing_the_toilet_a_bathroom_needs(tmp_path):
    """End to end with the real edit_ops and the real code critic as the dry re-check. Fails on the old code: the
    removal clears the critical F7 (the toilet in the door swing) and only a MAJOR G10 "bathroom without a toilet" is
    new, so it was accepted. Now the loop passes the removed pieces to the acceptance and the edit is refused with
    the reason; a move of the toilet stays possible."""
    out, b = bath_project(tmp_path)
    loop = LP.AgentLoop(out, MM.MockModel(chat=[]), vision=False, out=lambda s: None, workers=1)
    ctx = loop.context(1)
    ctx.findings = CC.run(b, {}, None)["findings"]
    assert {(f["check"], f["target"]) for f in ctx.findings} >= {("F7", "a_t"), ("R3", "d1")}
    res = loop.registry.call(ctx, "remove_piece", {"piece_id": "a_t", "reason": "the toilet blocks the door"})
    assert not res["accepted"], res
    reason = res["acceptance"]["reason"]
    assert reason.startswith("new major finding G10:r_L0_oda (bathroom without a toilet): the edit removed toilet a_t")
    assert any(f["id"] == "a_t" for f in ctx.building["furniture"])                     # nothing changed
    # the planner's tool for the same F7: mark_not_furniture is never offered on fixed equipment (allowed_edits)
    drawn = dict(b, furniture=[dict(f, source="from_documents") for f in b["furniture"]])
    assert not E.allowed_edits(drawn, "a_t")["mark_not_furniture"]["allowed"]
    # review of round 4: the planner's rules say the same (rule 2 offered mark_not_furniture for any "clear reading
    # error"; rule 7 named only new critical findings)
    assert "It is never marked as not furniture otherwise" in P.PLANNER_SYSTEM_M12
    assert "nor a G9 / G10 for a fixture the edit removed" in P.PLANNER_SYSTEM_M12


def test_set_lighting_is_idempotent_and_a_room_at_the_maximum_is_report_only(tmp_path):
    """Fails on the old code: set_lighting with the factor the room already has was accepted again (the dry re-check
    counts the room's dark views as gone, only a render re-meters them), so a room that needs more than the maximum
    x3 (the CPU pre-flight's real04 basement salon: about x10) got the same edit and a re-render every round. Now the
    repeat is a no-op with the reason, and the brief of a room at the maximum gives its dark views as "not yours"."""
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    first = reg.call(ctx, "set_lighting", {"room_id": "r1", "factor": 3.0, "reason": "the room is too dark"})
    assert first["accepted"], first
    again = reg.call(ctx, "set_lighting", {"room_id": "r1", "factor": 3.0, "reason": "still too dark"})
    assert not again["accepted"] and again["failed_checks"] == ["no_change: r1 has room lights x 3 already (the "
                                                                "maximum, 3)"]
    assert TL.lighting_state(ctx) == {"r1": 3.0}
    assert reg.call(ctx, "set_lighting", {"room_id": "r1", "factor": 2.0, "reason": "a bit less"})["accepted"]
    # the next round: the building carries the factor (overrides.apply); the brief knows it
    b = building()
    b["agent_overrides"] = {"lighting": {"r1": {"factor": 3.0, "reason": "dark"}}}
    salon = next(f for f in CC.run(b, {}, dark_manifest(), **quiet_critic())["findings"]
                 if f["target"] == "cam_r1_1")
    out = BR.room_brief(b, "r1", findings=[salon], members_fn=lambda b_, r: [], group_checks_fn=lambda b_, r: [],
                        program_fn=lambda b_, r: {}, solver_fn=lambda b_, r, k=3: [], allowed_fn=lambda b_, p: {})
    assert out["lighting_factor"] == 3.0 and out["findings"]["fixable"] == []
    # (review of 16 Oct 2026: at the maximum every dark view needs more than x3, so its cause says why)
    assert "no factor clears it and there is no add-lamp tool" in out["findings"]["not_yours"][0]["why"]
    bed_ = next(f for f in CC.run(b, {}, dark_manifest(), **quiet_critic())["findings"] if f["target"] == "cam_r1_2")
    assert CS.cause_of(bed_) == "lighting_beyond_cap"              # x3 x 1.82 needed
    # review of round 4: the lock is for the views too dark for the cap; a vision R5 (a blown-out window) of the same
    # room keeps set_lighting (a lower factor is still possible)
    r5 = {"id": "v:R5:r1", "check": "R5", "severity": "major", "target": "r1", "room_id": "r1", "source": "vision",
          "message": "the window is blown out"}
    out_r5 = BR.room_brief(b, "r1", findings=[salon, r5], members_fn=lambda b_, r: [],
                           group_checks_fn=lambda b_, r: [], program_fn=lambda b_, r: {},
                           solver_fn=lambda b_, r, k=3: [], allowed_fn=lambda b_, p: {})
    assert [(f["check"], f["tools"]) for f in out_r5["findings"]["fixable"]] == [("R5", ["set_lighting"])]
    assert [f["check"] for f in out_r5["findings"]["not_yours"]] == ["lighting_dark"]
    b["agent_overrides"]["lighting"]["r1"]["factor"] = 1.5
    bed_ = next(f for f in CC.run(b, {}, dark_manifest(), **quiet_critic())["findings"] if f["target"] == "cam_r1_2")
    out2 = BR.room_brief(b, "r1", findings=[bed_], members_fn=lambda b_, r: [], group_checks_fn=lambda b_, r: [],
                         program_fn=lambda b_, r: {}, solver_fn=lambda b_, r, k=3: [], allowed_fn=lambda b_, p: {})
    assert [f["tools"] for f in out2["findings"]["fixable"]] == [["set_lighting"]]     # x1.5 x 1.82 = x2.74 needed


def test_a_lighting_edit_too_weak_for_its_view_keeps_the_finding():
    """16 Oct 2026, before pod P3 attempt 2: a lighting_dark view counted as gone after any accepted set_lighting
    (only a render re-meters it). real04's basement salon needs about x10 and set_lighting gives up to x3: the x3 edit
    must not count as a removed finding; an edit that reaches the factor the view needs does. Review of the same day:
    the round's findings carry their metrics in ``evidence.metrics`` (``critic_code.finding``), so the test uses that
    shape (the first version read a top-level ``metrics`` only the test had)."""
    violation_ = {"check": "lighting_dark", "severity": "critical", "target": "cam_r_L-1_salon_1",
                  "room_id": "r_L-1_salon", "message": "too dark",
                  "metrics": {"stops_over_cap": 3.37, "factor_needed": 10.34, "lighting_factor_now": 1.0,
                              "set_lighting_factor": 10.34}}
    found = CC.finding(violation_)
    assert "metrics" not in found and found["evidence"]["metrics"]["set_lighting_factor"] == 10.34
    after = {"agent_overrides": {"lighting": {"r_L-1_salon": {"factor": 3.0, "reason": "x3"}}}}
    kept = LP.after_findings([dict(found)], [found], {"cam_r_L-1_salon_1", "r_L-1_salon"}, after)
    assert [f["target"] for f in kept] == ["cam_r_L-1_salon_1"]
    assert kept[0]["evidence"]["metrics"]["predicted_factor_after"] == 3.0 and "predicted" in kept[0]["message"]
    enough = CC.finding(dict(violation_, metrics=dict(violation_["metrics"], set_lighting_factor=2.5,
                                                      factor_needed=2.5)))
    assert LP.after_findings([dict(enough)], [enough], {"cam_r_L-1_salon_1"}, after) == []
    # no building after the edit: nothing can be predicted, the Round 4 rule (re-measured next round) holds
    assert LP.after_findings([dict(found)], [found], {"cam_r_L-1_salon_1"}, None) == []


def test_set_lighting_is_accepted_when_its_factor_reaches_the_view_and_refused_below(tmp_path):
    """Review of 16 Oct 2026 (fails on the first version): the set_lighting acceptance received the building without
    the edit's factor (the override goes to overrides.json), so the dry re-check predicted the old factor and, with
    the metrics read fixed, refused every set_lighting. Now the tool passes a trial building with the new factor:
    x2 clears a view that needs x1.82; x1.5 does not and is refused with the predicted factor."""
    out = project(tmp_path)
    loop = LP.AgentLoop(out, MM.MockModel(chat=[]), vision=False, out=lambda s: None, workers=1,
                        recheck=lambda b, s, m: [], apply_edit=FakeEdits(), validators=fake_validators())
    ctx = loop.context(1)
    ctx.findings = [f for f in CC.run(building(), {}, dark_manifest(), **quiet_critic())["findings"]
                    if f["target"] == "cam_r1_2"]                                  # needs x1.82
    assert ctx.findings[0]["evidence"]["metrics"]["set_lighting_factor"] == 1.82
    weak = loop.registry.call(ctx, "set_lighting", {"room_id": "r1", "factor": 1.5, "reason": "a bit darker room"})
    assert not weak["accepted"], weak
    assert "lighting_dark:cam_r1_2 is still there" in weak["acceptance"]["reason"]
    assert "x1.5 of the x1.82 the view needs" in weak["acceptance"]["reason"]
    assert TL.lighting_state(ctx) == {}                                            # nothing stored
    ok = loop.registry.call(ctx, "set_lighting", {"room_id": "r1", "factor": 2.0, "reason": "the room is too dark"})
    assert ok["accepted"], ok
    assert ok["acceptance"]["removed"] == 1 and TL.lighting_state(ctx) == {"r1": 2.0}
    assert ctx.findings == []
