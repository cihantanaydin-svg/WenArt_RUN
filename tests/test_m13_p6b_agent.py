"""Fix round after P6b (23 Oct 2026; pod P6b, real03 on 8e8cc97, the review of its agent log; track A_agent).

Checked, each against BASE 620997b (the tests fail there) or a mutation:

1. ``edit_ops.apply_edit`` refuses an edit after which a piece reaches through the REAL room outline when it did not
   before, or deeper / wider than before (P6b seq 2588: the drawn wardrobe f_L0_098 0.28 m through the front outer
   wall, accepted with a better score); the corner washing machines turned 90 degrees for "front faces a wall" (a cut
   they had, 0.025 m deeper) stay accepted;
2. ``causes.accept_edit`` accepts a step whose critical targets are gone (measured by code) while its majors stay no
   worse (P6b seq 1844 / 1849 / 1850 / 1886 / 2834); all-major steps, a kept critical, a vision-only critical and a
   major that became critical keep the old refusal; no refusal of the P4a, P4b, P5 or P6a logs changes;
3. a retype to the piece's own type (a confirm) and a ``set_room_type`` change nothing in the render: their target's
   vision findings stay in the dry re-check (P6b's 5 confirms and the two room retypes of r_L0_oda_19); a vision F9
   about the rendered model is ``wrong_model`` (swap_model), one about a wall cut ``collision``;
4. a vision F1 "the room is empty" is ``empty_room`` (place_group, relayout_room), never set_room_type;
5. an F7 / G12 / G8 on drawn fixed equipment that fix_fixture's 0.5 m search cannot move is the drawn layout (no tool,
   reported for review);
6. the final critical-only round's steps name critical findings only, the building session's room tools act on rooms,
   an RC on a symbol is resolved by code, an empty plan's default checklist leaves out the edits the code knows are
   futile, and the edit events log the acceptance's new / net / changed / fitted / kept fields.

The P6b / P6a / P5 / P4 run folders (``runs/...``) are not in git; the tests that read them skip without them.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from test_agent_helpers import FakeEdits, fake_validators, project, violation
from test_agent_loop_p4a import make
from test_m13_agent import FINISH, Clock, log_of, rotate
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import tools as TL
from wenart.furniture import edit_ops as E
from wenart.furniture import plausibility as PL

ROOT = Path(__file__).resolve().parents[1]
P6B = ROOT / "runs" / "20261022-235127-fetch_results" / "results"
P6B_FURNITURE = P6B / "furniture" / "real03"
P6B_LOG = P6B / "agent" / "real03" / "log.json"
LOGS = {"p4a_real02": ROOT / "runs" / "20261017-072801-full" / "results" / "agent" / "real02" / "log.json",
        "p4b_real03": ROOT / "runs" / "20261017-091212-full" / "results" / "agent" / "real03" / "log.json",
        "p5_real04": ROOT / "runs" / "20261017-224848-full" / "results" / "agent" / "real04" / "log.json",
        "p6a_real04": ROOT / "runs" / "20261022-135644-m13_p6" / "results" / "agent" / "real04" / "log.json",
        "p6b_real03": P6B_LOG}
needs_p6b = pytest.mark.skipif(not (P6B_FURNITURE / "building_agent.json").is_file() or not P6B_LOG.is_file(),
                               reason="the P6b run folder runs/20261022-235127-fetch_results is not on this machine")
META = {"reason": "test", "round": 1, "log_seq": 1, "model": "mock"}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finding(check, severity, target, room="r1", message="wrong", source="code", **metrics) -> dict:
    return {"check": check, "severity": severity, "target": target, "room_id": room, "message": message,
            "source": source, "evidence": {"metrics": dict(metrics)}}


def p6b_agent(reset: tuple = ()) -> dict:
    """P6b's working building (building_agent.json) with the pieces of ``reset`` put back to their state before the
    agent's edits (``adjusted_by_ai.changed``)."""
    b = read(P6B_FURNITURE / "building_agent.json")
    for f in b["furniture"]:
        if f["id"] in reset and f.get("adjusted_by_ai"):
            ch = f["adjusted_by_ai"]["changed"]
            for k in ("footprint", "front_deg", "status", "type"):
                if k in ch:
                    f[k] = copy.deepcopy(ch[k])
            f.pop("adjusted_by_ai", None)
    return b


def round_findings(round_no: int) -> list[dict]:
    """The findings of a P6b round as the loop held them (the finding events of this run, not dropped)."""
    data = read(P6B_LOG)
    out = []
    for e in data["events"]:
        if e["seq"] < int(data.get("run_first_seq") or 0) or e["kind"] != "finding" or e["round"] != round_no \
                or e.get("dropped"):
            continue
        out.append({"id": f"{e['source'][0]}:{e['checklist']}:{e['target']}", "check": e["checklist"],
                    "severity": e["severity"], "target": e["target"], "room_id": e.get("room_id"),
                    "message": e["finding"], "source": e["source"], "cause": e.get("cause"),
                    "evidence": {"metrics": dict((e.get("evidence") or {}).get("metrics") or {})}})
    return out


def dry_recheck(tool, args, res, building_before, before, targets):
    """The loop's acceptance on logged findings, without the critics: the code findings stay as they were (a confirm
    and a room type change no piece), the vision ones go through ``after_findings`` with the changed targets."""
    same = getattr(LP, "render_unchanged", lambda *a: {})(tool, args, building_before, res["building"])
    changed = TL.changed_targets(tool, args, res, targets, findings=before) - set(same)
    code = [f for f in before if f["source"] == "code"]
    after = LP.after_findings(code, before, changed, res["building"], building_before=building_before)
    # fix round after P6b, review: a set_room_type keeps its room's furnishing claims (the loop's acceptance)
    have = {CS.finding_key(f) for f in after}
    after += [f for f in getattr(LP, "room_type_kept", lambda *a: [])(tool, args, before, res["building"])
              if CS.finding_key(f) not in have]
    edit = {"target_finding": [{"check": t["check"], "target": t["target"], "metrics": CS._metrics(t)}
                               for t in targets]}
    return CS.accept_edit(before, after, edit)


# --------------------------------------------------------------------------
# 1. edit_ops: a cut through the room outline that is new or grows is refused
# --------------------------------------------------------------------------

def _wardrobe_room() -> dict:
    """A drawn wardrobe with its back on the east wall and its south end 6 mm inside the outer wall (it already fails
    the placer's inside_room against the 2 cm shrunk room); the bed stands in front of it (G13, the bed's G5)."""
    ward = M.fp("f_w", "wardrobe", (4.694, 0.606), (1.2, 0.6), rotation=90.0, front=180.0)
    bed = M.fp("f_b", "bed_double", (3.0, 2.0), (1.6, 2.0), rotation=0.0, front=270.0)
    return M.building(w=5.0, h=4.0, window=None, furniture=[ward, bed], door_x=1.0)


def test_a_move_through_the_outer_wall_is_refused_even_when_the_score_improves():
    """Fails on BASE: the move slides the wardrobe 0.30 m along its length through the south outer wall; the placer's
    inside_room failed before already, and the score rose 44 -> 54 (G13 and the bed's G5 gone, one F9 major new), so
    the move was accepted (P6b seq 2588: f_L0_098, 0.168 m² / 0.28 m through w_L0_001)."""
    b = _wardrobe_room()
    res = E.apply_edit(b, dict(op="move_piece", piece_id="f_w", center=[4.694, 0.306], **META))
    assert not res["accepted"] and res["building"] is None
    assert E.outline_cuts(PL.score_room(b, M.ROOM_ID)) == {}
    (why,) = res["failed_checks"]
    assert why.startswith("f_w: inside_room (outline: wardrobe reaches 0.18 m² through the room outline, up to 0.294 m")
    assert "0.00 m² up to 0.000 m deep before" in why
    # a move along the wall that stays inside the outline is no cut
    ok = E.apply_edit(b, dict(op="move_piece", piece_id="f_w", center=[4.694, 0.75], **META))
    assert not any("outline" in f for f in ok["failed_checks"])


def test_a_corner_washer_turned_to_fix_its_front_keeps_the_cut_it_had():
    """P6b seq 1969 / 1971 / 2637 (P4b seq 434 / 437): a drawn washing machine already 0.12 m² through its wall, its
    front into the wall (F4), turned 90 degrees: the cut deepens 0.180 -> 0.205 m and the turn stays accepted. Fails
    on a mutation of ``OUTLINE_DEPTH_GROWTH_M`` to the analyst's 0.02 m."""
    wm = M.fp("f_wm", "washing_machine", (2.88, 0.32), (0.65, 0.6), rotation=90.0, front=0.0)
    b = M.building(w=3.0, h=3.0, room_type="hall", window=None, furniture=[wm], door_x=1.0)
    cut0 = E.outline_cuts(PL.score_room(b, M.ROOM_ID))["f_wm"]
    res = E.apply_edit(b, dict(op="rotate_piece", piece_id="f_wm", front_deg=90.0, **META))
    assert res["accepted"], res["failed_checks"]
    cut1 = E.outline_cuts(PL.score_room(res["building"], M.ROOM_ID))["f_wm"]
    assert cut1[0] - cut0[0] < 0.01 and 0.02 < cut1[1] - cut0[1] < E.OUTLINE_DEPTH_GROWTH_M


def test_outline_growth_is_new_or_grown_cuts_only():
    msg = "wardrobe reaches 0.20 m² through the room outline, up to 0.300 m deep"
    assert E.outline_growth({}, {"a": (0.2, 0.3, msg)}) == [
        f"a: inside_room (outline: {msg}; 0.00 m² up to 0.000 m deep before)"]
    assert E.outline_growth({"a": (0.11, 0.17, "")}, {"a": (0.12, 0.195, "")}) == []          # a washer's turn
    assert E.outline_growth({"a": (0.11, 0.17, "")}, {"a": (0.17, 0.17, "")})                 # 0.06 m² wider
    assert E.outline_growth({"a": (0.11, 0.17, "")}, {"a": (0.11, 0.23, "")})                 # 0.06 m deeper
    assert E.outline_growth({"a": (0.2, 0.3, "")}, {}) == [] and E.outline_growth({}, {}) == []
    score = {"violations": [{"check": "F9", "target": "a", "message": msg, "metrics": {"outside_m2": 0.2,
                                                                                         "depth_m": 0.3}},
                            {"check": "F9", "target": "b", "message": "overlap", "metrics": {"other": "a",
                                                                                              "overlap_m2": 0.3}}]}
    assert E.outline_cuts(score) == {"a": (0.2, 0.3, msg)}


@needs_p6b
def test_p6b_wardrobe_move_is_refused_and_the_washer_turns_stay_accepted():
    """Fails on BASE (the wardrobe move is accepted, score 70 -> 80)."""
    res = E.apply_edit(p6b_agent(("f_L0_098",)), dict(op="move_piece", piece_id="f_L0_098", center=[10.46, 0.42],
                                                        **META))
    assert not res["accepted"]
    assert res["failed_checks"] == ["f_L0_098: inside_room (outline: wardrobe reaches 0.17 m² through the room "
                                    "outline, up to 0.280 m deep; 0.00 m² up to 0.000 m deep before)"]
    for pid, front in (("f_L0_074", 90.0), ("f_L0_076", 270.0), ("f_L0_077", 90.0)):
        res = E.apply_edit(p6b_agent((pid,)), dict(op="rotate_piece", piece_id=pid, front_deg=front, **META))
        assert res["accepted"], (pid, res["failed_checks"])


# --------------------------------------------------------------------------
# 2. accept_edit: a step's critical gone, its majors kept no worse
# --------------------------------------------------------------------------

FRIDGE = [finding("F7", "critical", "fr", message="fridge in the door swing"),
          finding("G12", "major", "fr", message="fridge in front of the window"),
          finding("G8", "major", "fr", message="no landing beside the fridge")]
STEP = {"target_finding": [{"check": f["check"], "target": "fr"} for f in FRIDGE]}


def test_a_step_whose_critical_is_gone_may_keep_a_major_no_worse():
    """Fails on BASE: P6b seq 1844 / 1849 / 1850 (fix_fixture of the fridges: F7 and G8 gone, the window G12 kept, a
    new major G8 on the counter) were refused 'G12 ... is still there' and the criticals stayed to the end."""
    after = [FRIDGE[1], finding("G8", "major", "counter", message="aisle short at the counter")]
    ok, why = CS.accept_edit(FRIDGE, after, STEP)
    assert ok, why
    assert why.startswith("finding F7:fr, G8:fr gone in the dry re-check") and why.endswith("kept: G12:fr (major)")
    assert "1 new (net 1)" in why


@pytest.mark.parametrize("before,after,start", [
    # all-major step, one target gone: the old rule (real02 / real04 logs: 14 refusals it would let through)
    ([finding("G12", "major", "fr"), finding("G8", "major", "fr")], [finding("G12", "major", "fr")],
     "finding G12:fr is still there"),
    # the critical itself kept
    (FRIDGE, [FRIDGE[0]], "finding F7:fr is still there"),
    # a vision critical counts as gone unmeasured on a changed target: it never outweighs a kept code finding
    ([finding("F1", "critical", "fr", source="vision"), FRIDGE[1]], [FRIDGE[1]], "finding G12:fr is still there"),
    # a kept major that became critical
    (FRIDGE, [dict(FRIDGE[1], severity="critical")], "finding G12:fr is still there"),
])
def test_the_critical_exception_keeps_the_old_refusal_otherwise(before, after, start):
    targets = {"target_finding": [{"check": f["check"], "target": f["target"]} for f in before]}
    ok, why = CS.accept_edit(before, after, targets)
    assert not ok and why.startswith(start), why


def test_the_other_checks_still_run_with_the_kept_targets():
    # a new critical elsewhere and the penalty rule still refuse; P6b seq 1886 / 2834 (the bed f_L0_141: F3 gone, F4
    # / G5 / G11 kept, a new major on the nightstand) passes: a critical traded for majors is a downgrade (P6a rule)
    assert CS.accept_edit(FRIDGE, [FRIDGE[1], finding("S2", "critical", "x")], STEP)[1].startswith(
        "new critical finding S2:x")
    assert "penalty rose" in CS.accept_edit(FRIDGE, [FRIDGE[1]], dict(STEP, penalty_before=10, penalty_after=20))[1]
    bed = [finding("F3", "critical", "bed"), finding("F4", "major", "bed"), finding("G5", "major", "bed")]
    after = [finding("F4", "major", "bed"), finding("G5", "major", "bed"), finding("G4", "major", "ns")]
    ok, why = CS.accept_edit(bed, after, {"target_finding": [{"check": f["check"], "target": "bed"} for f in bed]})
    assert ok and why.endswith("kept: F4:bed (major), G5:bed (major)"), why


def replay_refusals(path: Path) -> tuple[int, list[int]]:
    """Every 'still there' refusal of this run of the log that the logged key lists reproduce (a target among the
    logged after-list: minor findings are not logged) through ``accept_edit`` again, with the severities and sources
    of the round's finding events: ``(refusals replayed, seqs accepted now)``."""
    data = read(path)
    events = [e for e in data["events"] if e["seq"] >= int(data.get("run_first_seq") or 0)]
    meta = {}
    for e in events:
        if e["kind"] == "finding" and not e.get("dropped"):
            f = {"check": e.get("checklist"), "target": e.get("target"),
                 "metrics": (e.get("evidence") or {}).get("metrics") or {}}
            meta[(e["round"], CS._fmt(CS.finding_key(f)))] = (e.get("severity"), e.get("source"))

    def fdict(rnd, key):
        check, target = CS.parse_key(key)
        sev, src = meta.get((rnd, key)) or ("major", "code")
        f = {"check": check, "target": target, "severity": sev, "source": src, "message": ""}
        if check == "S2" and CS.S2_KEY_SEP in target:
            f["target"], part = target.split(CS.S2_KEY_SEP, 1)
            f["metrics"] = {"wall_id": part} if part.startswith("w") else {"other": part}
        return f

    n, accepted = 0, []
    for e in events:
        acc = (e.get("evidence") or {}).get("acceptance") or {}
        if e["kind"] != "rejected_edit" or not acc.get("target") or "is still there" not in str(acc.get("reason")) \
                or not set(acc["target"]) & set(acc.get("after") or []):
            continue
        n += 1
        rnd = e["round"]
        before = [fdict(rnd, k) for k in acc.get("before") or []]
        before += [fdict(rnd, k) for k in acc["target"] if k not in (acc.get("before") or [])]
        after = [fdict(rnd, k) for k in acc.get("after") or []]
        ok, _ = CS.accept_edit(before, after, {"target_finding": [dict(fdict(rnd, k), metrics=fdict(rnd, k).get(
            "metrics") or {}) for k in acc["target"]]})
        if ok:
            accepted.append(e["seq"])
    return n, accepted


@pytest.mark.parametrize("run,expected", [("p4a_real02", []), ("p4b_real03", []), ("p5_real04", []),
                                          ("p6a_real04", []), ("p6b_real03", [1844, 1849, 1850, 1886, 2834])])
def test_the_critical_exception_on_the_m13_logs(run, expected):
    """P6b's four criticals at the end (F7 x 3 on the fridges, F3 on the bed f_L0_141) came from the five refusals
    accepted now; no refusal of the real02 / real04 logs changes (BASE accepts none of them)."""
    path = LOGS[run]
    if not path.is_file():
        pytest.skip(f"{path} is not on this machine")
    n, accepted = replay_refusals(path)
    assert n > 0 and accepted == expected


# --------------------------------------------------------------------------
# 3. A confirm and a room type change nothing in the render; vision look claims get swap_model
# --------------------------------------------------------------------------

def _loop(tmp_path, recheck=lambda b, s, m: []):
    out = project(tmp_path)
    loop = LP.AgentLoop(out, MM.MockModel(), clock=Clock(), apply_edit=FakeEdits(), validators=fake_validators(),
                        out=lambda s: None, fit_fn=lambda p, b: None, recheck=recheck)
    return loop, loop.context(1)


HOLE = finding("F9", "major", "f1", message="The bed is rendered with a large hole in its top", source="vision")


def test_a_same_type_confirm_aimed_at_a_vision_finding_is_refused_and_one_aimed_at_rc_is_accepted(tmp_path):
    """Fails on BASE: P6b's seq 1914 / 1917 / 1954 / 2252 / 2283 confirmed unverified pieces (status only, the same
    fitted model) and each counted its vision finding about the model's look as removed."""
    loop, ctx = _loop(tmp_path)
    ctx.building["furniture"][0]["status"] = "unverified"
    after = copy.deepcopy(ctx.building)
    after["furniture"][0]["status"] = "verified"
    ctx.findings = [dict(HOLE, id="v:F9:f1")]
    verdict = loop.acceptance(ctx, "retype_piece", {"piece_id": "f1", "type": "bed_double"}, {"changed_ids": ["f1"]},
                              after)
    assert not verdict["accepted"] and verdict["reason"].startswith("finding F9:f1 is still there")
    assert verdict["reason"].endswith(LP.CONFIRM_NOTE) and "f1" not in verdict["changed"]
    ctx.findings = [dict(finding("RC", "minor", "f1", message="the AI passes typed it sofa"), id="c:RC:f1")]
    verdict = loop.acceptance(ctx, "retype_piece", {"piece_id": "f1", "type": "bed_double"}, {"changed_ids": ["f1"]},
                              after)
    assert verdict["accepted"], verdict["reason"]


def test_a_mark_or_a_new_front_aimed_at_a_vision_finding_still_counts_it_gone(tmp_path):
    loop, ctx = _loop(tmp_path)
    ctx.findings = [dict(HOLE, id="v:F9:f1")]
    marked = copy.deepcopy(ctx.building)
    marked["furniture"][0]["build"] = False
    assert loop.acceptance(ctx, "mark_not_furniture", {"piece_id": "f1", "kind": "other", "evidence": "crop"},
                           {"changed_ids": ["f1"]}, marked)["accepted"]
    turned = copy.deepcopy(ctx.building)
    turned["furniture"][0]["front_deg"] = 90.0
    assert loop.acceptance(ctx, "set_front", {"piece_id": "f1", "front_deg": 90.0}, {"changed_ids": ["f1"]},
                           turned)["accepted"]
    retyped = copy.deepcopy(ctx.building)
    retyped["furniture"][0]["type"] = "bed_single"
    assert LP.render_unchanged("retype_piece", {"piece_id": "f1", "type": "bed_single"}, ctx.building, retyped) == {}


def test_render_unchanged_names_a_confirm_and_a_room_type():
    """Fix round after P6b, review: a set_room_type changes its room's render (floor, walls, light); only its
    furnishing claims stay (``loop.room_type_kept``, tests/test_m13_p6b_review.py)."""
    b = {"furniture": [{"id": "f1", "type": "sofa"}], "rooms": [{"id": "r1", "room_type": "living"}]}
    assert LP.render_unchanged("retype_piece", {"piece_id": "f1", "type": "sofa"}, b, b) == {"f1": LP.CONFIRM_NOTE}
    assert LP.render_unchanged("change_type", {"piece_id": "f1", "type": "sofa"}, b, b) == {"f1": LP.CONFIRM_NOTE}
    assert LP.render_unchanged("set_room_type", {"room_id": "r1", "room_type": "study"}, b, b) == {}
    assert LP.render_unchanged("swap_model", {"piece_id": "f1", "asset_id": "x"}, b, b) == {}


def test_a_vision_f9_about_the_rendered_model_gets_swap_model():
    """Fails on BASE: every vision F9 that is no collision was ``wrong_type`` (retype / mark / remove /
    set_room_type), so P6b's 'large circular hole in the top' of f_L0_153 got retype_piece and no swap_model."""
    b = {"furniture": [{"id": "t1", "type": "table_coffee", "room_id": "r1", "asset": {"method": "library"}},
                       {"id": "u1", "type": "unknown", "room_id": "r1"}], "rooms": [{"id": "r1"}]}

    def cause(text, target="t1", source="vision"):
        return CS.cause_of(finding("F9", "major", target, message=text, source=source), b)

    assert cause("The coffee table has a large, unexplained circular hole in the center of its top") == "wrong_model"
    assert cause("The refrigerator is rendered as a massive, featureless white slab") == "wrong_model"
    assert CS.tools_for_finding(dict(finding("F9", "major", "t1"), cause="wrong_model")) == ["swap_model",
                                                                                          "report_library_gap"]
    # a cut through a wall is a collision; a placement opinion, a duplicate, a floating piece keep their route
    assert cause("The table is rendered intersecting the wall, the model passing through the wall") == "collision"
    assert cause("The refrigerator is rendered as a standalone unit, an odd placement") == "wrong_type"
    assert cause("The bed is placed with its headboard facing a wall") == "wrong_type"
    assert cause("A second table looks like a placeholder or duplicate") == "wrong_type"
    assert cause("The lamp is rendered with a floating shade") == "floating"
    # not built, not vision, no building: as before
    assert cause("rendered as a box", target="u1") == "wrong_type"
    assert cause("rendered as a box", source="code") == "wrong_type"
    assert CS.cause_of(finding("F9", "major", "t1", message="hole", source="vision")) == "wrong_type"


@needs_p6b
def test_p6b_confirms_keep_their_vision_findings_and_the_look_claims_get_swap_model():
    building = read(P6B_FURNITURE / "building_final.json")
    found = {(f["check"], f["target"]): dict(f, cause=None) for r in (1, 2) for f in round_findings(r)}
    assert CS.cause_of(found[("F9", "f_L0_153")], building) == "wrong_model"
    assert CS.cause_of(found[("F9", "f_L0_103")], building) == "wrong_model"
    assert CS.cause_of(found[("F9", "f_L0_141")], building) == "wrong_type"          # an orientation opinion
    # seq 2252: retype_piece f_L0_153 to its own type, replayed on the working building (BASE accepts it)
    b = p6b_agent(("f_L0_153",))
    args = {"piece_id": "f_L0_153", "type": "table_coffee", "reason": "confirm"}
    res = E.apply_edit(b, dict(op="retype_piece", **args, round=2, log_seq=2252, model="m"))
    assert res["accepted"] and LP.render_unchanged("retype_piece", args, b, res["building"]) == {
        "f_L0_153": LP.CONFIRM_NOTE}
    before = round_findings(2)
    targets = [f for f in before if (f["check"], f["target"]) == ("F9", "f_L0_153")]
    ok, why = dry_recheck("retype_piece", args, res, b, before, targets)
    assert not ok and why.startswith("finding F9:f_L0_153 is still there"), why


# --------------------------------------------------------------------------
# 4. An empty room is furnished, never retyped away
# --------------------------------------------------------------------------

def test_a_vision_empty_room_claim_is_furnished_not_retyped():
    """Fails on BASE: P6b's 'The room is completely empty' on r_L0_oda_19 had the cause wrong_type, whose only room
    tool is set_room_type (relayout_room was refused 'its tools: set_room_type')."""
    b = {"furniture": [], "rooms": [{"id": "r_oda", "room_type": "bedroom"}]}
    empty = finding("F1", "critical", "r_oda", room="r_oda", source="vision",
                    message="The room is completely empty; the render shows only bare walls and floor")
    lacking = dict(empty, message="The room is defined as a bedroom but rendered lacking any essential furniture")
    assert CS.cause_of(empty, b) == CS.cause_of(lacking, b) == "empty_room"
    assert CS.tools_for_finding(dict(empty, cause="empty_room")) == ["place_group", "relayout_room"]
    fixable, _ = BR.classify([dict(empty, id="v1")], b, "r_oda", {}, {}, {})
    assert fixable[0]["tools"] == ["place_group", "relayout_room"]
    # the P6a pins: a room's type opinion keeps wrong_type
    assert CS.cause_of(dict(empty, message="a terrace furnished with a dining table"), b) == "wrong_type"
    assert CS.cause_of(dict(empty, message="a desk is not standard for a bedroom"), b) == "wrong_type"
    assert CS.cause_of(dict(empty, source="code"), b) == "wrong_type"


def test_set_room_type_keeps_the_room_vision_findings_but_clears_a_code_one(tmp_path):
    """Fails on BASE: P6b's seq 1905 (bedroom) and 2277 (balcony) each counted the critical 'room completely empty'
    as removed; the re-run replays the overrides after the layout, so the room stayed empty."""
    loop, ctx = _loop(tmp_path)
    empty = dict(finding("F1", "critical", "r1", source="vision", message="The room is completely empty"),
                 id="v:F1:r1", cause="empty_room")
    ctx.findings = [empty]
    after = copy.deepcopy(ctx.building)
    after["rooms"][0]["room_type"] = "balcony"
    verdict = loop.acceptance(ctx, "set_room_type", {"room_id": "r1", "room_type": "balcony"},
                              {"changed_ids": ["r1"]}, after)
    assert not verdict["accepted"] and verdict["reason"].startswith("finding F1:r1 is still there")
    assert LP.ROOM_TYPE_NOTE in verdict["reason"]
    ctx.findings = [dict(finding("R1", "major", "r1", message="too small for a bedroom"), id="c:R1:r1")]
    assert loop.acceptance(ctx, "set_room_type", {"room_id": "r1", "room_type": "study"}, {"changed_ids": ["r1"]},
                           after)["accepted"]


@needs_p6b
def test_p6b_room_type_dodges_are_refused():
    found = {(f["check"], f["target"]): f for f in round_findings(1)}
    building = read(P6B_FURNITURE / "building_final.json")
    assert CS.cause_of(dict(found[("F1", "r_L0_oda_19")], cause=None), building) == "empty_room"
    for rnd, new in ((1, "bedroom"), (2, "balcony")):
        b = p6b_agent()
        room = next(r for r in b["rooms"] if r["id"] == "r_L0_oda_19")
        room["room_type"] = "unknown" if rnd == 1 else "bedroom"
        room.pop("adjusted_by_ai", None)
        args = {"room_id": "r_L0_oda_19", "room_type": new, "reason": "x"}
        res = E.apply_edit(b, dict(op="set_room_type", **args, round=rnd, log_seq=1, model="m"))
        assert res["accepted"], res["failed_checks"]
        before = round_findings(rnd)
        targets = [f for f in before if (f["check"], f["target"]) == ("F1", "r_L0_oda_19")]
        ok, why = dry_recheck("set_room_type", args, res, b, before, targets)
        assert not ok and why.startswith("finding F1:r_L0_oda_19 is still there"), why


# --------------------------------------------------------------------------
# 5. Drawn fixed equipment fix_fixture cannot move is the drawn layout
# --------------------------------------------------------------------------

def _kitchen(w, h, center):
    fridge = M.fp("f_fr", "fridge", center, (0.7, 0.7), rotation=0.0, front=90.0)
    return M.building(w=w, h=h, room_type="kitchen", window=None, furniture=[fridge], door_x=0.7)


def test_a_drawn_fridge_with_no_valid_spot_is_the_drawn_layout():
    """Fails on BASE (no such rule: P6b's agent spent its tries on G12:f_L0_213 and G8:f_L0_010, whose fix_fixture
    found no valid spot)."""
    stuck = _kitchen(1.4, 1.4, (0.7, 0.5))
    fs = [finding("F7", "critical", "f_fr", room=M.ROOM_ID, message="fridge in door d1"),
          finding("G12", "major", "f_fr", room=M.ROOM_ID), finding("F4", "major", "f_fr", room=M.ROOM_ID),
          finding("G12", "major", "f_fr", room=M.ROOM_ID, source="vision")]
    CS.mark_drawn_layout(fs, stuck)
    assert [CS._metrics(f).get(CS.DRAWN_LAYOUT_FLAG) for f in fs] == ["fixture", "fixture", None, None]
    assert E.fixture_problems(stuck, stuck["furniture"][0])["place"] is not None
    assert CS.fixture_layout_blocked(stuck, stuck["furniture"][0])
    assert CS.cause_of(fs[0], stuck) == CS.cause_of(fs[1], stuck) == "drawn_layout"
    assert CS.no_tool_reason(fs[0]) == CS.FIXTURE_LAYOUT_REASON
    fixable, not_yours = BR.classify([dict(fs[0], id="c1")], stuck, M.ROOM_ID, {}, {}, {})
    assert fixable == [] and not_yours[0]["why"] == CS.FIXTURE_LAYOUT_REASON
    # the dry re-check keeps the flag's value for an unchanged piece
    again = LP.after_findings([finding("F7", "critical", "f_fr", room=M.ROOM_ID)], fs, set(), stuck)
    assert CS._metrics(again[0])[CS.DRAWN_LAYOUT_FLAG] == "fixture" and again[0]["cause"] == "drawn_layout"


def test_a_drawn_fridge_with_a_spot_or_without_a_place_problem_keeps_its_tools():
    roomy = _kitchen(4.0, 4.0, (1.5, 0.5))
    assert E.fixture_problems(roomy, roomy["furniture"][0])["place"]["door"] == "d1"
    assert not CS.fixture_layout_blocked(roomy, roomy["furniture"][0])        # a spot within 0.5 m
    free = _kitchen(4.0, 4.0, (3.0, 3.0))
    assert not CS.fixture_layout_blocked(free, free["furniture"][0])          # no place problem: the lock says so
    sofa = M.fp("f_s", "sofa", (0.7, 0.5), (0.7, 0.7))
    assert not CS.fixture_layout_blocked(M.building(w=1.4, h=1.4, window=None, furniture=[sofa], door_x=0.7), sofa)


@needs_p6b
def test_p6b_round1_marks_the_fridge_in_its_door_and_the_counter_through_its_wall():
    b = read(P6B_FURNITURE / "building_final.json")
    fs = [f for f in round_findings(1) if f["source"] == "code" and f["check"] in ("F7", "G12", "G8")]
    for f in fs:
        f.pop("cause", None)
    CS.mark_drawn_layout(fs, b)
    marked = sorted((f["check"], f["target"]) for f in fs if CS._metrics(f).get(CS.DRAWN_LAYOUT_FLAG))
    # fix round after P6b, part J1 (the reading track's ask; ``test_m13_p6b_integration``): the fridges' F7 at the
    # edge of the doorless 1.05 m passages (0.93 m clear) is the drawn layout too (``causes.PASSAGE_CLEAR``)
    assert marked == [("F7", "f_L0_200"), ("F7", "f_L0_202"), ("F7", "f_L0_206"), ("G12", "f_L0_213"),
                      ("G8", "f_L0_010")]
    assert {CS._metrics(f)[CS.DRAWN_LAYOUT_FLAG] for f in fs if f["check"] == "F7" and f["target"] != "f_L0_204"} \
        == {CS.PASSAGE_CLEAR}
    # the fridges in the kitchen-living rooms have a spot 0.15 m away: fix_fixture stays theirs for the window band
    # and the aisle
    assert all(CS.cause_of(f, b) != "drawn_layout" for f in fs if f["target"] in ("f_L0_200", "f_L0_202", "f_L0_206")
               and f["check"] in ("G12", "G8"))


# --------------------------------------------------------------------------
# 6. Plans, RC, empty plans and the logged acceptance
# --------------------------------------------------------------------------

def _brief(fixable, room="r1"):
    return {"room": {"id": room}, "findings": {"fixable": fixable, "not_yours": []}, "pieces": [
        {"id": "bed", "allowed": {"move_piece": True}}, {"id": "ns", "allowed": {"move_piece": True}}],
        "not_built": [], "groups": [],
        "free_wall_spans": [], "program": {"groups": []}}


def test_the_final_round_steps_name_critical_findings_only():
    """Fails on BASE: P6b's round-4 plan of r_L0_ebeveyn_odasi_4 named F3 (critical) with F4 / G5 / G11 (major) in one
    step and G5 of the nightstand f_L0_070 in another; 6 of the round's 17 rejections were edits for majors."""
    fixable = [{"id": "c:F3:bed", "check": "F3", "severity": "critical", "target": "bed", "tools": ["move_piece"]},
               {"id": "c:F4:bed", "check": "F4", "severity": "major", "target": "bed", "tools": ["move_piece"]},
               {"id": "c:G5:ns", "check": "G5", "severity": "major", "target": "ns", "tools": ["move_piece"]}]
    plan = {"room_id": "r1", "steps": [
        {"tool": "move_piece", "target": "bed", "finding_ids": ["c:F3:bed", "c:F4:bed"], "why": "onto the wall"},
        {"tool": "move_piece", "target": "ns", "finding_ids": ["c:G5:ns"], "why": "free the side"}]}
    steps, problems = LP.check_plan(plan, _brief(fixable), ["move_piece"], wanted=("critical",))
    assert [(s["target"], s["finding_ids"]) for s in steps] == [("bed", ["c:F3:bed"])]
    assert any("c:G5:ns not critical" in p for p in problems) and any("c:F4:bed dropped" in p for p in problems)
    steps, _ = LP.check_plan(plan, _brief(fixable), ["move_piece"])                      # the other rounds: as before
    assert [s["finding_ids"] for s in steps] == [["c:F3:bed", "c:F4:bed"], ["c:G5:ns"]]


def test_the_building_session_room_tools_need_a_room_and_an_rc_on_a_symbol_is_resolved():
    """Fails on BASE: P6b's building session planned set_room_type on 11 symbol ids (RC minors whose resolution
    'moved to building.symbols' the reading had already applied)."""
    b = {"furniture": [{"id": "f_1", "type": "table_dining"}], "rooms": [{"id": "r1"}]}
    rc = finding("RC", "minor", "sy_L0_004", room=None, message="the AI passes typed it chair",
                 resolution="moved to building.symbols (trust order: vector geometry > AI)")
    assert CS.cause_of(rc, b) == "resolved_by_code" and CS.tools_for_finding(dict(rc, cause="resolved_by_code")) == []
    assert CS.cause_of(dict(rc, target="f_1"), b) == "wrong_type"                     # a piece's conflict: as before
    fixable = [{"id": "c:R1:r1", "check": "R1", "severity": "major", "target": "r1", "tools": ["set_room_type"]}]
    plan = {"room_id": "building", "steps": [
        {"tool": "set_room_type", "target": "sy_L0_004", "finding_ids": ["c:R1:r1"], "why": "x"},
        {"tool": "set_room_type", "target": "r1", "finding_ids": ["c:R1:r1"], "why": "x"}]}
    steps, problems = LP.check_plan(plan, _brief(fixable, room=LP.BUILDING), ["set_room_type"], rooms={"r1"})
    assert [s["target"] for s in steps] == ["r1"]
    assert problems == ["step 1 (set_room_type on sy_L0_004): set_room_type needs a room of the building as target, "
                        "not 'sy_L0_004'"]


F4 = violation("F4", "major", "f2", "r1", "the nightstand faces the wall")
F3 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")


def test_an_empty_plan_runs_the_default_steps_but_the_futile_ones(tmp_path):
    """Fails on BASE: P6b's empty plans of round 4 (r_L0_yasama_2 / _3) sent the fix_fixture edits the memory had
    refused since round 1 again (seq 2839 / 2840); 10 of the empty plans' 48 default edits were memory refusals."""
    plan = {"room_id": "r1", "program": {"keep": True}, "steps": [],
            "skip": [{"finding_id": "c:F4:f2", "why": "the nightstand is drawn there"}]}
    loop, out, _ = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3, F4], []], plan=[plan], max_rounds=1)
    MEM.Memory(out).record("r1", 1, "rotate_piece", {"piece_id": "f2", "reason": "x"},
                           {"accepted": False, "failed_checks": ["front_into_wall"]})
    loop.memory = MEM.Memory(out)
    loop.run()
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "plan")
    assert ev["status"] == "empty" and [s["target"] for s in ev["evidence"]["steps"]] == ["f1"]
    (dropped,) = ev["evidence"]["dropped"]
    assert dropped["tool"] == "rotate_piece" and dropped["target"] == "f2" and dropped["finding_ids"] == ["c:F4:f2"]
    assert dropped["why"].startswith("the memory refused rotate_piece on f2 (round 1: front_into_wall")
    assert ev["counts"]["dropped"] == 1


def test_an_empty_plan_keeps_a_major_step_the_code_cannot_call_futile(tmp_path):
    """The planner's skip reasons are not trusted: P6a's empty-plan defaults fixed majors it had skipped (seq 5986,
    6064, 6358) and P6b's the fridge's critical F7 (seq 1848)."""
    plan = {"room_id": "r1", "program": {"keep": True}, "steps": [],
            "skip": [{"finding_id": "c:F4:f2", "why": "the nightstand is drawn there"}]}
    loop, out, _ = make(tmp_path, [FINISH], [[F3, F4], []], plan=[plan], max_rounds=1)
    loop.run()
    ev = next(e for e in log_of(out)["events"] if e["kind"] == "plan")
    assert [s["target"] for s in ev["evidence"]["steps"]] == ["f1", "f2"] and "dropped" not in ev["evidence"]


def test_futile_steps_are_the_ones_the_code_knows(tmp_path):
    loop, ctx = _loop(tmp_path)
    step = {"tool": "rotate_piece", "target": "f1", "finding_ids": ["c:F3:f1"]}
    assert LP.futile_step(ctx, step) is None
    ctx.memory.record("r1", 1, "rotate_piece", {"piece_id": "f1", "reason": "x"},
                      {"accepted": False, "failed_checks": ["front_into_wall"]})
    assert LP.futile_step(ctx, step).startswith("the memory refused rotate_piece on f1 (round 1: front_into_wall")
    ctx.tries["f2"] = 3
    assert LP.futile_step(ctx, dict(step, target="f2")) == "f2 used its 3 tries this round"
    ctx.session().no_spot["f1"] = "fixture_place: f1: no valid spot within 0.50 m"
    assert "no valid spot" in LP.futile_step(ctx, {"tool": "fix_fixture", "target": "f1"})
    assert LP.step_args({"tool": "relayout_room", "target": "r1"}) == {"room_id": "r1"}
    assert LP.step_args({"tool": "finish", "target": "x"}) is None


def test_the_edit_event_logs_new_net_changed_fitted_and_kept(tmp_path):
    """Fails on BASE: the logged acceptance kept 8 keys (accepted, reason, target, before, after, removed, note,
    carried); P6b's 219 edit events could not tell whether the dry re-check refit a piece."""
    loop, out, _ = make(tmp_path, [rotate("f1", 90.0), FINISH], [[F3], []])
    loop.run()
    ed = next(e for e in log_of(out)["events"] if e["kind"] == "edit")
    acc = ed["evidence"]["acceptance"]
    assert {"new", "net", "changed", "fitted", "kept"} <= set(acc)
    assert acc["changed"] == ["f1"] and acc["kept"] == [] and acc["fitted"] == {"overlaid": 0, "refit": []}
    assert acc["new"] == 0 and acc["net"] == 1
    assert LP.ACCEPTANCE_LOG_KEYS[:8] == ("accepted", "reason", "target", "before", "after", "removed", "note",
                                          "carried")
    assert MEM.Memory(out).room("r1")["accepted"]
