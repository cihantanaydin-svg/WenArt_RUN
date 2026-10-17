"""Fix round after pod P4a (17 Oct 2026; real02 with the M11 cameras replayed), track A_agent.

What the P4a analysis found and these tests pin (CPU only: MockModel, the fakes of ``test_agent_helpers``, the
committed real02 building for the roof checks):

- the critical X2 "pokes through the roof" is measured on the round's scene manifest; the dry re-check rebuilt it
  from that stale box, so every remove or move of the bookshelf f_L1_058 was rejected for 3 rounds. Now it carries
  ``source: scene_manifest`` and is left out on a changed target; the major X2 re-measured on the building after the
  edit keeps a piece still under the slope rejected;
- S2 wall cuts: a move along the wall was "accepted blind" (S2 is not re-measured); the cut is now predicted from
  the footprint (``loop.s2_wall_kept``); pair cuts, buried kitchen members and swaps still count as gone;
- S2 keys name their cut (``causes.finding_key``); an S2 cut below 0.03 m is minor (``critic_code``);
- a door clipped under the roof ("needs a dormer: review") is report-only, not a set_exterior;
- a vision finding about a light fixture put on a piece (the desk) is re-routed to the lighting stage;
- plans: the plan event's status (ok / empty / refused / default) and the planner's skip list are logged;
- set_lighting steps come first; the final round lights a too-dark view when a re-render follows;
- memory refusals count as tries and the second identical refusal closes the step;
- metrics: an edit counts by the finding keys it targeted (set_lighting targets camera findings);
- camera overrides: a pose the view has already is a no-op (``no_change``); after a re-run, a camera edit whose view
  is not at the override's pose is logged ``no_effect``.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from test_agent_helpers import (FakeEdits, FixesWhatItTouched, ScriptedCritic, building, fake_validators, project,
                                violation, write_json)
from test_m13_agent import FINISH, Clock, ctx_for, finding, log_of, quiet_critic
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import metrics as MX
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.blender import exterior_checks as X

ROOT = Path(__file__).resolve().parents[1]
REAL02 = ROOT / "results" / "furniture" / "real02" / "building_final.json"


def make(tmp_path, chat, critic_rounds, *, plan=(), **kw):
    """``test_m13_agent.make`` with the planner's scripted answers (``plan``)."""
    out = project(tmp_path)
    model = MM.MockModel(chat=chat, plan=list(plan), critic=kw.pop("critic", []))
    critic = ScriptedCritic(critic_rounds)
    kw.setdefault("recheck", FixesWhatItTouched(critic))
    kw.setdefault("workers", 1)
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)}, clock=Clock(),
                        code_critic=critic, vision=kw.pop("vision", False), apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, **kw)
    return loop, out, model


# --------------------------------------------------------------------------
# X2: the stale built box under the roof (real02's attic, P4a's bookshelf f_L1_058)
# --------------------------------------------------------------------------

P4A_BOOKSHELF = {"id": "f_L1_058", "type": "bookshelf", "level_id": "L1",
                 "room_id": "r_L1_oyun_aktivite_ve_dinlenme_odasi_2", "source": "added_by_ai",
                 "footprint": {"center": [13.2015, 0.622], "size": [0.8, 0.3], "rotation_deg": 270.0},
                 "front_deg": 180.0, "height": 1.8, "status": "verified",
                 "asset": {"method": "library", "asset_id": "hssd_4ff59e80", "bbox_m": [0.8, 0.3289, 2.02],
                           "fit_scale": [1.0, 1.0, 1.0]}}
# the round's scene manifest box of P4a (renders/real02/scene_manifest.json): top 4.16 + 2.02 / 2 = 5.17 m
P4A_MANIFEST = {"objects": [{"name": "furn_f_L1_058", "wenart_id": "f_L1_058", "kind": "furniture",
                             "box3d": {"center": [13.1871, 0.622, 4.16], "size": [0.8, 0.3289, 2.02],
                                       "rotation_deg": 270.0}}]}


def real02_with_bookshelf() -> dict:
    b = json.loads(REAL02.read_text(encoding="utf-8"))
    b["furniture"] = [f for f in b["furniture"] if f.get("id") != "f_L1_058"] + [copy.deepcopy(P4A_BOOKSHELF)]
    return b


def x2_findings(b: dict) -> list[dict]:
    return [CC.finding(v) for v in X.check_exterior(b, P4A_MANIFEST, None)["violations"]]


@pytest.mark.skipif(not REAL02.is_file(), reason="results/furniture/real02 not committed")
def test_the_stale_manifest_box_no_longer_blocks_a_remove_or_a_move_to_full_height():
    """Fails on 03881bc: the critical X2 from the round's scene manifest came back in every dry re-check, so the
    remove of f_L1_058 (P4a seq 665) and its move onto w_L1_012 where the ceiling is full height (seq 675/975/1256)
    were rejected "X2:f_L1_058 is still there". A move that stays under the slope is still rejected (the major X2
    re-measured on the building after the edit has the same key)."""
    b = real02_with_bookshelf()
    before = x2_findings(b)
    mine = [f for f in before if f["check"] == "X2" and f["target"] == "f_L1_058"]
    assert sorted(f["severity"] for f in mine) == ["critical", "major"]
    crit = next(f for f in mine if f["severity"] == "critical")
    assert crit["evidence"]["metrics"]["source"] == X.SCENE_MANIFEST_SOURCE == LP.MANIFEST_SOURCE
    assert LP.manifest_measured(crit) and not LP.manifest_measured(next(f for f in mine if f["severity"] == "major"))
    room = P4A_BOOKSHELF["room_id"]
    target = {"target_finding": [{"check": "X2", "target": "f_L1_058"}]}

    def edit(change):
        after_b = copy.deepcopy(b)
        change(after_b)
        after = LP.after_findings(x2_findings(after_b), before, {"f_L1_058", room}, after_b, building_before=b)
        return LP.accept_edit(before, after, target)

    def remove(bb):
        bb["furniture"] = [f for f in bb["furniture"] if f["id"] != "f_L1_058"]

    def move_to(center, rotation):
        def change(bb):
            p = next(f for f in bb["furniture"] if f["id"] == "f_L1_058")
            p["footprint"] = dict(p["footprint"], center=list(center), rotation_deg=rotation)
        return change

    ok, why = edit(remove)
    assert ok, why
    ok, why = edit(move_to((7.958, 3.622), 90.0))       # snap onto w_L1_012 at offset 3.0 (edit_ops._move)
    assert ok, why
    kept, why = edit(move_to((13.2, 2.0), 270.0))        # still under the slope (1.87 m there)
    assert not kept and why.startswith("finding X2:f_L1_058 is still there") and "sloped ceiling" in why
    # an unchanged target keeps the manifest finding (the next build re-measures the changed ones only)
    after = LP.after_findings(x2_findings(b), before, {"f_L1_050"}, b, building_before=b)
    assert any(f["target"] == "f_L1_058" and f["severity"] == "critical" for f in after)


@pytest.mark.skipif(not REAL02.is_file(), reason="results/furniture/real02 not committed")
def test_a_door_clipped_under_the_roof_is_reported_not_sent_to_set_exterior():
    """Fails on 03881bc: X2 d_L1_004 / d_L1_005 ("still lower than a usable door (needs a dormer: review)") had the
    cause ``roof`` and the building session sent 5 set_exterior edits (one a 70 degree gable) that could not fix it."""
    clips = [f for f in x2_findings(real02_with_bookshelf()) if f["target"] in ("d_L1_004", "d_L1_005")]
    assert len(clips) == 2 and all(f["evidence"]["metrics"]["kind"] == X.OPENING_CLIP_KIND == CS.OPENING_CLIP_KIND
                                   for f in clips)
    for f in clips:
        assert CS.cause_of(f) == "opening_under_roof" and CS.tools_for_finding(f) == []
        assert "dormer" in CS.no_tool_reason(f)
    # an older finding without the kind, from its message; the roof itself keeps set_exterior
    old = finding("X2", "major", "d_L1_004", None, clips[0]["message"])
    assert CS.cause_of(old) == "opening_under_roof"
    assert CS.cause_of(finding("X2", "critical", "roof", None, "no roof over the top level")) == "roof"
    fixable, not_yours = BR.classify(clips, real02_with_bookshelf(), None, {}, {}, {})
    assert fixable == [] and {f["cause"] for f in not_yours} == {"opening_under_roof"}


# --------------------------------------------------------------------------
# S2: wall cuts predicted from the footprint, keys that name the cut, cuts within tolerance minor
# --------------------------------------------------------------------------

def corridor_with_table(center=(12.39, 9.9)) -> dict:
    """real02's r_L1_koridor_2 shape: the coffee table f_L1_024 (1.2 x 0.7 m) cuts wall w_L1_006 (along x at
    y = 10.246, 0.11 m thick) by 0.052 m."""
    return {"levels": [{"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r_L1_koridor_2", "level_id": "L1",
                       "polygon": [[10.0, 8.0], [16.0, 8.0], [16.0, 10.19], [10.0, 10.19]]}],
            "walls": [{"id": "w_L1_006", "level_id": "L1", "start": [10.0, 10.246], "end": [16.0, 10.246],
                       "thickness": 0.11, "height": 2.7}],
            "furniture": [{"id": "f_L1_024", "type": "table_coffee", "level_id": "L1", "room_id": "r_L1_koridor_2",
                           "footprint": {"center": list(center), "size": [1.2, 0.7], "rotation_deg": 0.0}},
                          {"id": "f_L1_023", "type": "chair", "level_id": "L1", "room_id": "r_L1_koridor_2",
                           "footprint": {"center": [11.4, 9.9], "size": [0.45, 0.5], "rotation_deg": 0.0}}]}


WALL_CUT = finding("S2", "major", "f_L1_024", "r_L1_koridor_2",
                   "table_coffee f_L1_024 cuts wall w_L1_006 by 0.052 m (allowed 0.010 m for a default piece)",
                   depth_m=0.0516, tolerance_m=0.01, wall_id="w_L1_006", **{"class": "default"})
CHAIR_CUT = finding("S2", "major", "f_L1_024", "r_L1_koridor_2",
                    "table_coffee f_L1_024 and chair f_L1_023 cut each other by 0.039 m (allowed 0.010 m)",
                    depth_m=0.039, other="f_L1_023", tolerance_m=0.01)


def test_an_s2_wall_cut_is_predicted_from_the_footprint_not_dropped():
    """Fails on 03881bc: S2 is not re-measured, so P4a's edit 332 (f_L1_024 moved 0.11 m ALONG wall w_L1_006) was
    accepted and the next round measured 0.055 m (10 of 10 such wall moves in P3 and P4a were still over tolerance).
    Now the cut after the edit is the measured cut plus the change of the footprint's depth in that wall."""
    before_b = corridor_with_table()
    along = corridor_with_table((12.50, 9.9))
    kept = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, along, building_before=before_b)
    assert [CS.finding_key(f) for f in kept] == [("S2", "f_L1_024/w_L1_006")]
    m = kept[0]["evidence"]["metrics"]
    assert m["predicted_depth_after"] == pytest.approx(0.0516, abs=1e-3) and "predicted" in kept[0]["message"]
    ok, why = LP.accept_edit([WALL_CUT], kept, {"target_finding": [dict(WALL_CUT, metrics=m)]})
    assert not ok and why.startswith("finding S2:f_L1_024/w_L1_006 is still there")
    # 0.07 m away from the wall: the predicted cut is under the tolerance, the finding counts as gone
    away = corridor_with_table((12.39, 9.83))
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, away, building_before=before_b) == []
    # half way: still over 0.010 m
    half = corridor_with_table((12.39, 9.88))
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, half, building_before=before_b)
    # a footprint that stands off the wall face to begin with (only the mesh cuts): moving further off clears it
    off_before, off_after = corridor_with_table((12.39, 9.80)), corridor_with_table((12.39, 9.75))
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, off_after, building_before=off_before) == []
    # a pair cut, a buried kitchen member, a removed piece: as before, gone. (Fix round after P4b, changed on
    # purpose: an edit that keeps the footprint, swap_model, now KEEPS the wall cut: test_agent_loop_p4b.py)
    assert LP.after_findings([], [CHAIR_CUT], {"f_L1_024"}, along, building_before=before_b) == []
    buried = finding("S2", "major", "f_L1_024", None, "buried", depth_m=0.2, other="f9", kitchen_run=True,
                     wall_id="w_L1_006")
    assert LP.after_findings([], [buried], {"f_L1_024"}, along, building_before=before_b) == []
    gone = copy.deepcopy(before_b)
    gone["furniture"][0]["build"] = False
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, gone, building_before=before_b) == []
    # without the building before the edit: nothing to predict (the old rule)
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, along) == []


def test_s2_keys_name_the_cut_so_a_wall_cut_and_a_chair_cut_are_two_findings():
    """Fails on 03881bc: P4a's S2:f_L1_021 held a 0.055 m wall cut and a 0.011 m chair cut under one key."""
    assert CS.finding_key(WALL_CUT) == ("S2", "f_L1_024/w_L1_006")
    assert CS.finding_key(CHAIR_CUT) == ("S2", "f_L1_024/f_L1_023")
    assert CS.finding_key(finding("S2", "major", "f9", None, "cuts")) == ("S2", "f9")       # no cut named
    assert CS.finding_key(finding("F9", "major", "f9", None, "x", wall_id="w1")) == ("F9", "f9")
    assert CS.base_key(("S2", "f_L1_024/w_L1_006")) == ("S2", "f_L1_024")
    assert CS.parse_key("S2:f_L1_024/w_L1_006") == ("S2", "f_L1_024/w_L1_006")
    # the chair cut targeted, the wall cut left: accepted; the wall cut targeted and kept: rejected
    target = {"target_finding": [{"check": "S2", "target": "f_L1_024", "metrics": {"other": "f_L1_023"}}]}
    assert LP.accept_edit([WALL_CUT, CHAIR_CUT], [WALL_CUT], target)[0]
    assert CS.key_list([WALL_CUT, CHAIR_CUT]) == ["S2:f_L1_024/f_L1_023", "S2:f_L1_024/w_L1_006"]
    assert CS.findings_removed([WALL_CUT, CHAIR_CUT], [WALL_CUT]) == 1
    # a caller that names the S2 without its cut targets every cut of the piece (the old key)
    old_style = {"target_finding": {"check": "S2", "target": "f_L1_024"}}
    ok, why = LP.accept_edit([WALL_CUT, CHAIR_CUT], [WALL_CUT], old_style)
    assert not ok and why.startswith("finding S2:f_L1_024/w_L1_006 is still there")
    assert LP.accept_edit([WALL_CUT, CHAIR_CUT], [], old_style)[0]


def test_an_s2_cut_within_tolerance_is_a_minor_finding():
    """Fails on 03881bc: the build's default S2 tolerance is 0.010 m, so P4a logged 6-7 cuts of 0.011-0.026 m per
    round as MAJOR findings with the cause within_tolerance (no tool)."""
    cuts = [{"check": "S2", "severity": "major", "target": "f_L-1_023", "room_id": "r1", "message": "cuts wall",
             "metrics": {"depth_m": 0.0204, "tolerance_m": 0.01, "wall_id": "w_L-1_004"}},
            {"check": "S2", "severity": "major", "target": "f_L-1_038", "room_id": "r1", "message": "cuts a chair",
             "metrics": {"depth_m": 0.0393, "other": "f_L-1_039", "tolerance_m": 0.01}},
            {"check": "S1", "severity": "major", "target": "f1", "room_id": "r1", "message": "floats",
             "metrics": {"floor_gap_m": 0.02}}]
    res = CC.run(building(), {}, None, scene_fn=lambda: [dict(c) for c in cuts], **quiet_critic())
    got = {(f["check"], f["target"]): f for f in res["findings"]}
    small = got[("S2", "f_L-1_023")]
    assert small["severity"] == "minor" and small["evidence"]["metrics"]["severity_was"] == "major"
    assert CS.cause_of(small) == "within_tolerance"
    assert got[("S2", "f_L-1_038")]["severity"] == "major" and got[("S1", "f1")]["severity"] == "major"


# --------------------------------------------------------------------------
# the vision critic: a light fixture's look is the lighting stage's
# --------------------------------------------------------------------------

P4A_LAMP = "The wall-mounted lamp next to the nightstand is rendered as a crude, flat rectangular box, which looks " \
           "like a placeholder or a wrong object model."


def test_a_light_fixture_finding_on_a_piece_goes_to_the_lighting_stage(tmp_path):
    """Fails on 03881bc: P4a's "wall-mounted lamp next to the desk" (a rig wall light) was put on the desk f_L0_029;
    swap_model on the desk was accepted and the finding came back in rounds 3 and 4. Now it is re-routed to the room
    as ``light_fixture`` (no tool, report_to lighting); a finding about the piece itself stays."""
    nightstand = {"id": "f2", "type": "nightstand"}
    assert CV.light_subject(P4A_LAMP, nightstand) == "lamp"
    assert CV.light_subject("The wall-mounted light fixture next to the desk is a crude slab rather than a proper "
                            "lamp model.", {"id": "f_L0_029", "type": "desk"}) == "wall-mounted light"
    assert CV.light_subject("The desk is positioned with its back against the wall.", {"id": "d", "type": "desk"}) \
        is None
    assert CV.light_subject("A light grey sofa with a crude shape", {"id": "s", "type": "sofa"}) is None
    assert CV.light_subject("The coat rack is rendered as a street lamp", {"id": "c", "type": "coat_rack"}) is None
    assert CV.light_subject("The floor lamp looks wrong", {"id": "l", "type": "floor_lamp"}) is None
    critic = [{"findings": [{"check": "D2", "severity": "major", "target": "f2", "message": P4A_LAMP,
                             "evidence_image": 1}]},
              {"findings": [{"check": "D2", "severity": "major", "target": "f3",
                             "message": "the sofa is a crude low-poly model", "evidence_image": 1}]},
              {"findings": []}]
    loop, out, _ = make(tmp_path, [{"content": "nothing"}], [[]], critic=critic, vision=True, max_rounds=1)
    loop.run()
    events = [e for e in log_of(out)["events"] if e["kind"] == "finding" and e["checklist"] == "D2"]
    lamp = next(e for e in events if e["room_id"] == "r1")
    assert lamp["target"] == "r1" and not lamp.get("dropped") and lamp["cause"] == "light_fixture"
    assert lamp["report_to"] == "lighting" and "lighting stage" in lamp["not_yours"]
    assert lamp["evidence"]["metrics"]["target_was"] == "f2" and lamp["evidence"]["metrics"]["named"] == "lamp"
    sofa = next(e for e in events if e["room_id"] == "r2")
    assert sofa["target"] == "f3" and sofa["cause"] == "wrong_model"


# --------------------------------------------------------------------------
# plans: the status says why the default checklist ran, the skip list is logged
# --------------------------------------------------------------------------

F3 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")
MOVE = {"tool_calls": [{"name": "move_piece", "arguments": {"piece_id": "f1", "center": [2.0, 2.5],
                                                            "reason": "the bed head onto the north wall"}}]}


@pytest.mark.parametrize("plan,status,skip", [
    ({"room_id": "r1", "program": {"keep": True}, "steps": [],
      "skip": [{"finding_id": "c:F3:f1", "why": "the bed is drawn there"}]}, "empty",
     [{"finding_id": "c:F3:f1", "why": "the bed is drawn there"}]),
    ({"room_id": "r1", "program": {"keep": True},
      "steps": [{"finding_ids": ["c:F3:f1"], "tool": "teleport", "target": "f1", "why": "fast"}]}, "refused", []),
    ({"__raw__": "{}"}, "default", []),
    ({"room_id": "r1", "program": {"keep": True},
      "steps": [{"finding_ids": ["c:F3:f1"], "tool": "move_piece", "target": "f1", "why": "onto the wall"}]},
     "ok", []),
])
def test_the_plan_event_says_why_the_default_checklist_ran_and_logs_the_skip_list(tmp_path, plan, status, skip):
    """Fails on 03881bc: 25 of P4a's 54 plans were logged "default" (21 of them valid empty plans, 4 with every
    step refused) and the planner's skip list was never read. Behaviour is unchanged: the default checklist runs."""
    loop, out, _ = make(tmp_path, [MOVE, FINISH], [[F3], []], plan=[plan], max_rounds=1)
    loop.run()
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "plan")
    assert ev["status"] == status and ev["evidence"]["skip"] == skip
    assert [s["tool"] for s in ev["evidence"]["steps"]] == ["move_piece"]       # the default checklist when not ok
    rec = MEM.Memory(out).room("r1")["plans"][0]
    assert rec["status"] == status and rec["skip"] == skip and rec["ok"] is (status == "ok")
    mem = MX.compute(log_of(out))["memory"]
    assert mem["plans_valid"] == (status == "ok")
    assert (mem["plans_empty"], mem["plans_refused"], mem["plans_default"]) == tuple(
        int(status == s) for s in ("empty", "refused", "default"))
    assert LP.plan_status(None, []) == "default" and LP.PLAN_STATUSES == ("ok", "empty", "refused", "default")


# --------------------------------------------------------------------------
# set_lighting first; the final round lights a too-dark view
# --------------------------------------------------------------------------

DARK = {"check": "lighting_dark", "severity": "major", "target": "cam_r1_1", "room_id": "r1",
        "message": "cam_r1_1 is 0.42 stops over the EV cap",
        "metrics": {"stops_over_cap": 0.42, "factor_needed": 1.34, "lighting_factor_now": 1.0,
                    "set_lighting_factor": 1.34}}
LIGHT = {"tool_calls": [{"name": "set_lighting", "arguments": {"room_id": "r1", "factor": 1.9,
                                                               "reason": "the view is too dark for the EV cap"}}]}


def test_set_lighting_steps_come_first_in_every_checklist():
    """Fails on 03881bc: P4a's salon set_lighting was the last of 14 default steps; the session's 12 calls ran out on
    rotations and moves before it, and the final salon views stayed 0.42 and 0.07 stops over the cap."""
    fixable = [{"id": "c:F4:f1", "check": "F4", "severity": "major", "target": "f1", "message": "faces the wall",
                "cause": "orientation", "tools": ["rotate_piece"]},
               {"id": "c:lighting_dark:cam_r1_1", "check": "lighting_dark", "severity": "major",
                "target": "cam_r1_1", "edit_target": "r1", "message": "too dark", "cause": "lighting",
                "tools": ["set_lighting"]}]
    brief = {"room": {"id": "r1"}, "groups": [], "findings": {"fixable": fixable}}
    assert [s["tool"] for s in LP.default_checklist(brief)] == ["set_lighting", "rotate_piece"]
    planned = [{"tool": "rotate_piece", "target": "f1"}, {"tool": "set_lighting", "target": "r1"}]
    assert [s["tool"] for s in LP.lighting_first(planned)] == ["set_lighting", "rotate_piece"]
    task = P.session_task(1, {"room": {"id": "r1"}}, LP.lighting_first(planned), [], 12, False)
    assert "Do the set_lighting steps first" in task and task.index("1. set_lighting") < task.index("2. rotate")
    # the final round (critical only) takes the major dark view only with ``lighting``
    assert LP.default_checklist(brief, ("critical",)) == []
    assert [s["tool"] for s in LP.default_checklist(brief, ("critical",), lighting=True)] == ["set_lighting"]
    assert "too dark for the EV cap" in P.plan_prompt(4, {"room": {"id": "r1"}}, ["set_lighting"], True, lighting=True)


def test_the_final_round_lights_a_major_dark_view_when_a_rerender_follows(tmp_path, monkeypatch):
    """Fails on 03881bc: the final round is critical-only, so P4a's salon views (major lighting_dark, x1.88 and
    x1.48 fixable) were never lit. A final round without a re-render function stays critical-only. Fix round after
    P4b: ``FINAL_ROUND_LIGHTING`` is off (decision 6 of 17 Oct 2026); the mechanism is tested with the switch on
    (test_agent_loop_p4b.py pins the default)."""
    monkeypatch.setattr(LP, "FINAL_ROUND_LIGHTING", True)
    loop, out, model = make(tmp_path, [LIGHT, FINISH], [[DARK], []], recheck=lambda b, s, m: [])
    res = loop.final_round(4)
    assert res["accepted"] == 1 and res["rerun_from"] and "cam_r1_1" in res["views"]
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "edit")
    assert ev["tool"] == "set_lighting" and ev["evidence"]["acceptance"]["target"] == ["lighting_dark:cam_r1_1"]
    loop2, out2, _ = make(tmp_path / "b", [LIGHT, FINISH], [[DARK], []], recheck=lambda b, s, m: [])
    loop2.rerun = None
    assert loop2.final_round(4)["stop"] == "no_finding"
    # a critical finding still comes alone in a round that is not final
    assert not LP.is_wanted(CC.finding(DARK), ("critical",)) and LP.is_wanted(CC.finding(DARK), ("critical",), True)


# --------------------------------------------------------------------------
# memory refusals count as tries; the second identical refusal closes the step
# --------------------------------------------------------------------------

def test_a_step_whose_edit_the_memory_refused_twice_is_closed(tmp_path):
    """Fails on 03881bc: P4a's session r1-s19 sent one refused move 7 times (7 of its 12 calls): the memory
    refusal returned before the try count and the session went on to the call cap."""
    rejected = {"tool_calls": [{"name": "move_piece", "arguments": {"piece_id": "f1", "center": [2.0, 2.5],
                                                                    "reason": "reject: the bed onto the wall"}}]}
    loop, out, model = make(tmp_path, [copy.deepcopy(rejected) for _ in range(6)], [[F3], [F3]], max_rounds=1)
    loop.run()
    rej = [e for e in log_of(out)["events"] if e["kind"] == "rejected_edit"]
    assert len(rej) == 3 and len(model.chat_requests()) == 3                      # 1 validated + 2 refusals
    assert [e["validation"]["failed_checks"][0].split(":")[0] for e in rej] == ["score_drop", "memory", "memory"]
    assert "[closed: the memory refused its edit twice]" in MEM.Memory(out).room("r1")["open"][0]
    # the refusal counts as a try of its target
    ctx = loop.context(2)
    ctx.begin_session("r1")
    ctx.findings = [CC.finding(F3)]
    args = rejected["tool_calls"][0]["arguments"]
    first = loop.registry.call(ctx, "move_piece", dict(args))
    assert first.get("refused_by_memory") and not first.get("step_closed") and ctx.tries["f1"] == 1
    second = loop.registry.call(ctx, "move_piece", dict(args))
    assert second.get("step_closed") and "checklist step is closed" in second["message"] and ctx.tries["f1"] == 2


# --------------------------------------------------------------------------
# metrics: an edit counts by the findings it targeted
# --------------------------------------------------------------------------

def _f(seq, rnd, check, target, severity="major", **metrics):
    return {"seq": seq, "round": rnd, "kind": "finding", "source": "code", "checklist": check, "severity": severity,
            "target": target, "finding": "x", "evidence": {"metrics": metrics}}


def test_edits_removing_finding_counts_the_findings_an_edit_targeted():
    """Fails on 03881bc: P4a's 4 set_lighting edits log the room as target and lighting_dark as checklist while
    their findings are on cameras, so the metric said 13 of 25; it is 17 of 24 (the library gap has no target)."""
    events = [_f(1, 1, "lighting_dark", "cam_a"), _f(2, 1, "lighting_dark", "cam_b"), _f(3, 1, "F4", "f1"),
              _f(4, 1, "S2", "f2", wall_id="w1", depth_m=0.05), _f(5, 1, "S2", "f2", other="f3", depth_m=0.04),
              {"seq": 6, "round": 1, "kind": "edit", "tool": "set_lighting", "checklist": "lighting_dark",
               "target": "r1", "evidence": {"acceptance": {"target": ["lighting_dark:cam_a", "lighting_dark:cam_b"]}}},
              {"seq": 7, "round": 1, "kind": "edit", "tool": "report_library_gap", "checklist": "F4", "target": "f1"},
              {"seq": 8, "round": 1, "kind": "edit", "tool": "move_piece", "checklist": "S2", "target": "f2",
               "evidence": {"acceptance": {"target": ["S2:f2/w1"]}}},
              {"seq": 9, "round": 1, "kind": "edit", "tool": "move_piece", "checklist": "S2", "target": "f2"},
              {"seq": 10, "round": 1, "kind": "round", "counts": {"findings_removed": 3}},
              _f(11, 2, "F4", "f1", severity="minor"), _f(12, 2, "S2", "f2", other="f3", depth_m=0.04),
              {"seq": 13, "round": 2, "kind": "round", "counts": {"findings_removed": 0}}]
    fr = MX.findings_removed_metrics(events, [1, 2])
    # set_lighting (both cameras gone) and the wall-cut move count; the library gap has no target; the older
    # edit without acceptance names S2:f2, whose chair cut is still there
    assert fr["edits_removing_finding"] == 2 and fr["edits_with_target"] == 3 and fr["accepted_edits"] == 4
    assert fr["per_round"] == {"1": 4} and fr["total"] == 4      # 2 views, F4, the wall cut (keys name the cut)


# --------------------------------------------------------------------------
# cameras: an override that changes nothing is a no-op; a camera edit without effect is logged
# --------------------------------------------------------------------------

P4A_EXT6 = {"view_id": "ext_1", "kind": "exterior", "position": [24.0, 22.0, 1.6], "target": [7.5865, 6.0, 1.6],
            "lens_mm": 26, "reason": "a 3/4 corner view with two facades"}


def test_a_camera_override_that_changes_nothing_is_not_accepted(tmp_path):
    """Fails on 03881bc: P4a accepted the same set_camera ext_6 in rounds 2 and 3 (the dry re-check counts X6 as
    gone on a changed view); a pose the view already has is now a no-op with the reason, like set_exterior."""
    ctx = ctx_for(tmp_path)
    reg = TL.build_registry()
    first = reg.call(ctx, "set_camera", dict(P4A_EXT6))
    assert first["accepted"], first
    again = reg.call(ctx, "set_camera", dict(P4A_EXT6, reason="the same corner view once more"))
    assert not again["accepted"] and again["failed_checks"][0].startswith("no_change: ext_1 has this pose already")
    assert "accepted override" in again["failed_checks"][0] and again.get("no_op")
    assert len(OV.Overrides(ctx.project_out).accepted()) == 1
    # within 1 cm and the same lens is the same pose; another lens is a change
    near = dict(P4A_EXT6, position=[24.004, 22.0, 1.6])
    assert not reg.call(ctx, "set_camera", near)["accepted"]
    assert reg.call(ctx, "set_camera", dict(P4A_EXT6, lens_mm=28))["accepted"]
    # the scene camera's own pose (no override yet) is no change either
    cam = ctx.camera("cam_r1_1")
    same = {"view_id": "cam_r1_1", "kind": "interior", "room_id": "r1", "position": list(cam["position"]),
            "target": list(cam["target"]), "reason": "keep it"}
    res = reg.call(ctx, "set_camera", same)
    assert not res["accepted"] and "its camera in the scene manifest" in res["failed_checks"][0]


def test_a_camera_edit_whose_view_did_not_change_after_the_rerun_is_logged_no_effect(tmp_path):
    """Fails on 03881bc (no such check): P4a's set_camera ext_6 added a second camera named ext_6 (Blender renamed it
    ext_6.001), so the view ext_6 never changed while the edit counted as applied."""
    edit = {"tool": "set_camera", "args": dict(P4A_EXT6, view_id="ext_6")}
    frontal = {"name": "ext_6", "kind": "exterior", "position": [7.59, 29.5, 1.6], "target": [7.59, 6.0, 1.6],
               "lens_mm": 26}
    agent = dict(frontal, position=[24.0, 22.0, 1.6], target=[7.5865, 6.0, 1.6])
    dup = LP.camera_effects({"cameras": [frontal, agent]}, [edit])
    assert dup[0]["status"] == "no_effect" and dup[0]["cameras"] == 2 and "ext_6.001" in dup[0]["note"]
    assert LP.camera_effects({"cameras": [agent]}, [edit])[0]["status"] == "ok"
    assert LP.camera_effects({"cameras": [frontal]}, [edit])[0]["status"] == "no_effect"
    assert LP.camera_effects({"cameras": []}, [edit])[0]["status"] == "no_effect"
    assert LP.camera_effects({"cameras": [frontal]}, [{"tool": "set_lighting", "args": {}}]) == []
    # two edits of one view in a round: the last one counts
    first = {"tool": "set_camera", "args": dict(edit["args"], position=[18.5, 24.0, 1.6])}
    assert [r["status"] for r in LP.camera_effects({"cameras": [agent]}, [first, edit])] == ["ok"]
    # the loop logs one check per camera edit after the re-run
    out = project(tmp_path)
    write_json(out / "scene" / "scene_manifest.json", {"cameras": [frontal, agent]})
    loop = LP.AgentLoop(out, MM.MockModel(), vision=False, out=lambda s: None, workers=1)
    assert loop.check_camera_effects(2, [edit]) == 1
    ev = next(e for e in log_of_saved(loop) if e["kind"] == "check" and e.get("tool") == LP.CAMERA_EFFECT_CHECK)
    assert ev["status"] == "no_effect" and ev["target"] == "ext_6" and ev["counts"] == {"cameras": 2}


def log_of_saved(loop) -> list[dict]:
    loop.save()
    return log_of(loop.project_out)["events"]
