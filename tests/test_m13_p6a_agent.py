"""Fix round after P6a (22 Oct 2026; pod P6a, real04 on 8e8cc97, the review of its agent log; track A_agent).

Checked, each against BASE 52d4bb8 (the tests fail there) or a mutation:

1. a ``swap_model`` whose pin the dry fit refuses (P6a seq 6069 / 6075 / 6076: three generated models while a real
   product fits) is refused "pin_refused" and its piece's vision findings stay (``loop.refused_pin``);
2. ``causes.accept_edit`` refuses a same-piece swap of one major for another (P6a's 6 "new" findings), still accepts
   P5's seq 4643 / 4651 (two majors traded for one) and a critical -> major downgrade; the accepted reason and the
   acceptance record name the new findings and the net;
3. a memory or max-tries refusal counts as a repeat whatever its target, so P6a's r2 session of r_L-1b_salon_2
   (memory refusals on f_L-1b_041 / 045 / 047 / 048 in turn) ends at its second refusal in a row;
4. ``plan_crop`` never hands out a whole-sheet debug image of no level (P6a seq 5968 cited
   ``final/debug/deneme1_dwg_s1.jpg`` as the plan crop of the untyped f_L-1b_002);
5. a vision F1 on a drawn piece whose type the room's types hold (the desk f_L0_026 in a bedroom) is reported for
   review, never offered ``retype_piece`` (cause ``drawn_type``);
6. an F3 / F8 on a drawn piece no move within the drawn lock clears (P6a's sofas f_L-1b_041 / 042, 2 m off every wall)
   is the drawn layout: no tool, reported, kept so through the dry re-check;
7. ``final_round`` returns the agent stage's note on the numbers after the final round (``loop.stage_note``).

The P6a / P5 / P4 run folders (``runs/...``) are not in git; the tests that read them skip without them.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from test_agent_helpers import (FakeEdits, FixesWhatItTouched, ScriptedCritic, fake_validators, piece, project,
                                violation, write_json)
from test_m13_agent import Clock, log_of
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import tools as TL

ROOT = Path(__file__).resolve().parents[1]
P6A = ROOT / "runs" / "20261022-135644-m13_p6" / "results"
P6A_FURNITURE = P6A / "furniture" / "real04"
P6A_LOG = P6A / "agent" / "real04" / "log.json"
LOGS = {"p4a_real02": ROOT / "runs" / "20261017-072801-full" / "results" / "agent" / "real02" / "log.json",
        "p4b_real03": ROOT / "runs" / "20261017-091212-full" / "results" / "agent" / "real03" / "log.json",
        "p5_real04": ROOT / "runs" / "20261017-224848-full" / "results" / "agent" / "real04" / "log.json",
        "p6a_real04": P6A_LOG}
needs_p6a = pytest.mark.skipif(not (P6A_FURNITURE / "building_final.json").is_file() or not P6A_LOG.is_file(),
                               reason="the P6a run folder runs/20261022-135644-m13_p6 is not on this machine")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finding(check, severity, target, room="r1", message="wrong", source="code", **metrics) -> dict:
    return {"check": check, "severity": severity, "target": target, "room_id": room, "message": message,
            "source": source, "evidence": {"metrics": dict(metrics)}}


# --------------------------------------------------------------------------
# 1. swap_model: a pin the dry fit refuses changes nothing
# --------------------------------------------------------------------------

def _fit(piece_, building):
    pin = piece_.get("asset_pin")
    if pin and str(pin).startswith("gen_"):
        return {"method": "library", "asset_id": "hssd_real", "bbox_m": [0.6, 0.65, 1.8],
                "pin_refused": f"{pin}: a generated model (units guessed) while a real product of the type fits "
                               f"within the caps (hssd_real)"}
    return {"method": "library", "asset_id": pin or "hssd_real", "pinned": pin, "bbox_m": [0.6, 0.65, 1.8]}


def _swap_loop(tmp_path):
    out = project(tmp_path)
    final = read(out / "building_final.json")
    for f in final["furniture"]:
        f["asset"] = {"method": "library", "asset_id": f"m_{f['id']}", "bbox_m": [1.0, 1.0, 1.0]}
    write_json(out / "building_final.json", final)
    loop = LP.AgentLoop(out, MM.MockModel(), clock=Clock(), recheck=lambda b, s, m: [], apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, fit_fn=_fit)
    ctx = loop.context(1)
    ctx.findings = [CC.finding(dict(violation("D2", "major", "f1", "r1", "the bed is a crude low-poly model"),
                                    source="vision"))]
    for f in ctx.findings:
        f["source"] = "vision"
    return loop, ctx


def test_a_swap_to_a_model_the_dry_fit_refuses_is_refused_and_keeps_its_vision_finding(tmp_path):
    """Fails on BASE: the vision D2 on the swapped piece counted as gone and the swap was accepted, although the
    refit keeps the real model (P6a seq 6069 / 6075 / 6076)."""
    loop, ctx = _swap_loop(tmp_path)
    after = copy.deepcopy(ctx.building)
    after["furniture"][0]["asset_pin"] = "gen_bed_classic_1"
    verdict = loop.acceptance(ctx, "swap_model", {"piece_id": "f1", "asset_id": "gen_bed_classic_1"},
                              {"changed_ids": ["f1"]}, after)
    assert not verdict["accepted"]
    assert verdict["reason"].startswith("pin_refused: f1: gen_bed_classic_1: a generated model"), verdict["reason"]
    assert "f1" not in verdict["changed"]
    assert any(f.get("check") == "D2" and f.get("target") == "f1" for f in verdict["after_findings"])
    # a pin the dry fit takes is a real change: accepted as before
    ok_after = copy.deepcopy(ctx.building)
    ok_after["furniture"][0]["asset_pin"] = "hssd_other_bed"
    ok = loop.acceptance(ctx, "swap_model", {"piece_id": "f1", "asset_id": "hssd_other_bed"},
                         {"changed_ids": ["f1"]}, ok_after)
    assert ok["accepted"], ok["reason"]


def test_refused_pin_names_only_a_refusal_of_the_new_pin():
    b = {"furniture": [{"id": "f1", "asset_pin": "gen_b", "asset": {"method": "library", "asset_id": "real",
                                                                    "pin_refused": "gen_a: a generated model"}}]}
    assert LP.refused_pin(b, "f1") is None                               # an older pin's refusal
    b["furniture"][0]["asset"]["pin_refused"] = "gen_b: fails the fit rules (caps, height)"
    assert LP.refused_pin(b, "f1") == "gen_b: fails the fit rules (caps, height)"
    b["furniture"][0]["asset_pin"] = None
    assert LP.refused_pin(b, "f1") is None and LP.refused_pin(b, "f9") is None and LP.refused_pin(None, "f1") is None


@needs_p6a
def test_p6a_phantom_swaps_are_refused_by_the_dry_fit_on_the_real_catalogue():
    """P6a seq 6069 / 6075 / 6076 on building_agent.json with the repository's catalogue, in the licence mode and
    style family of building_final.json, as ``AgentLoop.dry_fit`` fits them."""
    from wenart.furniture import catalog as C
    from wenart.furniture import edit_ops as EO
    from wenart.furniture import fit as F
    agent, final = read(P6A_FURNITURE / "building_agent.json"), read(P6A_FURNITURE / "building_final.json")
    pins = {"f_L-1_090": "gen_fridge_classic_3_25281fe9", "f_L0_003": "gen_washbasin_modern_1_833baa60",
            "f_L0_016": "gen_toilet_japandi_1_42fdb46f"}
    for f in final["furniture"]:
        if f["id"] in pins:
            f["asset_pin"] = None                           # the round-1 final building: the swaps came after it
    cat = C.load()

    def fit(p, b):
        return F.fit_piece(dict(p, build=True), cat, mode=EO.licence_mode_of(final),
                           style_family=EO._style_family_of(final))
    for pid, pin in pins.items():
        after = copy.deepcopy(agent)
        next(f for f in after["furniture"] if f["id"] == pid)["asset_pin"] = pin
        measured, note = LP.fitted_view(after, final, fit=fit)
        assert pid in note["refit"]
        why = LP.refused_pin(measured, pid)
        assert why is not None and why.startswith(f"{pin}: a generated model"), (pid, why)


# --------------------------------------------------------------------------
# 2. accept_edit: a same-piece swap removes nothing
# --------------------------------------------------------------------------

def test_a_major_traded_for_another_major_on_the_same_piece_is_refused():
    """Fails on BASE: P6a seq 6326 (F9 -> F4 on the chair f_L-1b_053) was accepted with '1 ... removed'."""
    before = [finding("F9", "major", "c1", message="chair through the table"), finding("F6", "major", "f2")]
    after = [finding("F4", "major", "c1", message="chair does not face its table"), finding("F6", "major", "f2")]
    ok, why = CS.accept_edit(before, after, {"target_finding": {"check": "F9", "target": "c1"}})
    assert not ok and why.startswith("swap: F4:c1 replaces F9:c1 on c1"), why


def test_two_majors_traded_for_one_and_a_downgrade_still_pass():
    """P5 seq 4643: the chair's F9 and its S2 wall cut gone, one F8 'stands alone' new: accepted, net 1."""
    before = [finding("F9", "major", "c1"), finding("S2", "major", "c1", wall_id="w9", depth_m=0.12)]
    after = [finding("F8", "major", "c1", message="chair stands alone")]
    ok, why = CS.accept_edit(before, after, {"target_finding": {"check": "F9", "target": "c1"}})
    assert ok and "2 critical/major finding(s) removed, 1 new (net 1)" in why, why
    crit = [finding("X2", "critical", "b1", message="through the roof")]
    ok, why = CS.accept_edit(crit, [finding("F3", "major", "b1")], {"target_finding": {"check": "X2", "target": "b1"}})
    assert ok, why


def test_a_new_major_elsewhere_passes_but_a_cut_into_the_moved_piece_counts_on_it():
    before = [finding("F9", "major", "c1")]
    elsewhere = [finding("F6", "major", "f2")]
    ok, why = CS.accept_edit(before, elsewhere, {"target_finding": {"check": "F9", "target": "c1"}})
    assert ok and "1 new (net 0)" in why, why
    # the new S2 names the other piece as its target and the moved chair as its partner: a swap on c1
    cut = [finding("S2", "major", "c2", other="c1", depth_m=0.06)]
    ok, why = CS.accept_edit(before, cut, {"target_finding": {"check": "F9", "target": "c1"}})
    assert not ok and why.startswith("swap: S2:c2/c1 replaces F9:c1"), why


def test_the_acceptance_record_names_the_new_findings_and_the_net(tmp_path):
    out = project(tmp_path)
    loop = LP.AgentLoop(out, MM.MockModel(), clock=Clock(), apply_edit=FakeEdits(), validators=fake_validators(),
                        out=lambda s: None, fit_fn=lambda p, b: None,
                        recheck=lambda b, s, m: [CC.finding(violation("F6", "major", "f3", "r2"))])
    ctx = loop.context(1)
    ctx.findings = [CC.finding(violation("F4", "major", "f1", "r1"))]
    after = copy.deepcopy(ctx.building)
    after["furniture"][0]["front_deg"] = 90.0
    verdict = loop.acceptance(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0}, {"changed_ids": ["f1"]},
                              after)
    assert verdict["accepted"] and verdict["removed"] == 1 and verdict["new"] == 1 and verdict["net"] == 0


def _fdict(key: str, severity: str) -> dict:
    check, target = CS.parse_key(key)
    f = {"check": check, "target": target, "severity": severity, "message": ""}
    if check == "S2" and CS.S2_KEY_SEP in target:
        f["target"], part = target.split(CS.S2_KEY_SEP, 1)
        f["metrics"] = {"wall_id": part} if part.startswith("w") else {"other": part}
    return f


def replay_accepted(path: Path) -> tuple[int, list[int]]:
    """Every accepted edit of this run of the log through ``accept_edit`` again (its logged before / after key
    lists; the severities of the round's finding events, a key without one is major: a new critical was refused
    already): ``(accepted edits replayed, seqs refused now)``."""
    data = read(path)
    events = [e for e in data["events"] if e["seq"] >= int(data.get("run_first_seq") or 0)]
    sev = {}
    for e in events:
        if e["kind"] == "finding":
            f = {"check": e.get("checklist"), "target": e.get("target"),
                 "metrics": (e.get("evidence") or {}).get("metrics") or {}}
            sev[(e["round"], CS._fmt(CS.finding_key(f)))] = e.get("severity")
    n, refused = 0, []
    for e in events:
        acc = (e.get("evidence") or {}).get("acceptance") or {}
        if e["kind"] != "edit" or not acc.get("target"):
            continue
        n += 1
        before = [_fdict(k, sev.get((e["round"], k)) or "major") for k in acc.get("before") or []]
        targets = [_fdict(k, sev.get((e["round"], k)) or "major") for k in acc["target"]]
        before += [t for t, k in zip(targets, acc["target"]) if k not in (acc.get("before") or [])]
        after = [_fdict(k, sev.get((e["round"], k)) or "major") for k in acc.get("after") or []]
        ok, _ = CS.accept_edit(before, after, {"target_finding": [dict(t, metrics=t.get("metrics") or {})
                                                                  for t in targets]})
        if not ok:
            refused.append(e["seq"])
    return n, refused


@pytest.mark.parametrize("run,expected", [("p4a_real02", []), ("p4b_real03", []),
                                          ("p5_real04", [4663, 4664, 5037, 5040]),
                                          ("p6a_real04", [6326, 6333, 6608, 6610, 6642, 6653])])
def test_the_swap_rule_on_the_m13_logs(run, expected):
    """real02 / real03 lose no accepted edit; real04 P5 loses its four 1-for-1 chair swaps (seq 4643 / 4651, two
    majors for one, stay); P6a loses exactly the six edits behind its six 'new' findings."""
    path = LOGS[run]
    if not path.is_file():
        pytest.skip(f"{path} is not on this machine")
    n, refused = replay_accepted(path)
    assert n > 0 and refused == expected


# --------------------------------------------------------------------------
# 3. Repeated refusals end the session whatever the target
# --------------------------------------------------------------------------

def test_repeat_refusal_counts_memory_and_max_tries_refusals_whatever_the_target():
    mem = {"accepted": False, "failed_checks": ["memory: the same edit was rejected in round 1"],
           "refused_by_memory": True}
    tries = {"accepted": False, "failed_checks": ["max_tries: f1"], "max_tries_target": "f1"}
    spot = {"accepted": False, "failed_checks": ["no_spot: f1"], "no_spot": True}
    validated = {"accepted": False, "failed_checks": ["drawn_lock: f1"]}
    assert LP.repeat_refusal(mem, "f9", set()) and LP.repeat_refusal(tries, "f9", set())
    assert not LP.repeat_refusal(spot, "f1", set()) and LP.repeat_refusal(spot, "f1", {"f1"})
    assert not LP.repeat_refusal(validated, "f1", {"f1"}) and not LP.repeat_refusal(None, "f1", {"f1"})


def _with_pieces(out: Path) -> None:
    for name in ("building_decor.json", "building_final.json", "building.json"):
        b = read(out / name)
        b["furniture"] += [piece("f4", "r1", "dresser", (3.2, 3.2), (1.0, 0.5), 0.0, 270.0),
                           piece("f5", "r1", "desk", (3.4, 1.0), (1.0, 0.6), 0.0, 90.0)]
        write_json(out / name, b)


def _mv(pid, center, reason="move it onto the wall"):
    return {"tool_calls": [{"name": "move_piece", "arguments": {"piece_id": pid, "center": center,
                                                                "reason": reason}}]}


def test_p6a_r2_salon_session_ends_at_the_second_repeat_in_a_row(tmp_path):
    """Fails on BASE: P6a's r2 session of r_L-1b_salon_2 sent memory-refused moves of f_L-1b_041, 045, 047 and 048
    in turn (seq 6335-6351, after one validated refusal) and the count went back to 0 at every new target, so the
    session never ended; replayed here on four pieces: it ends at the second refusal in a row."""
    out = project(tmp_path)
    _with_pieces(out)
    moves = {"f1": [1.0, 2.0], "f2": [0.5, 3.0], "f4": [3.0, 3.0], "f5": [3.0, 1.0]}
    m = MEM.Memory(out)
    for pid, center in moves.items():
        m.record("r1", 1, "move_piece", {"piece_id": pid, "center": center, "reason": "move it onto the wall"},
                 {"accepted": False, "failed_checks": ["drawn_lock: a drawn piece moves at most 0.3 m"]})
    m.save()
    chat = [_mv("f1", moves["f1"]), _mv("f2", [0.6, 3.0], "reject: the validator refuses it"),
            _mv("f1", moves["f1"]), _mv("f2", moves["f2"]), _mv("f2", moves["f2"]), _mv("f4", moves["f4"]),
            _mv("f4", moves["f4"]), _mv("f5", moves["f5"])]
    model = MM.MockModel(chat=chat)
    found = [violation("F3", "major", pid, "r1", "its back is not on a wall") for pid in moves]
    critic = ScriptedCritic([found, found])
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)}, clock=Clock(),
                        code_critic=critic, recheck=FixesWhatItTouched(critic), vision=False, apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, workers=1, max_rounds=1, max_tries=3)
    loop.run()
    events = log_of(out)["events"]
    rej = [e["validation"]["failed_checks"][0].split(":")[0] for e in events if e["kind"] == "rejected_edit"]
    assert rej == ["memory", "score_drop", "memory", "memory"], rej
    assert len(model.chat_requests()) == 4
    end = [e for e in events if e["kind"] == "check" and e.get("tool") == LP.REFUSALS_CHECK]
    assert len(end) == 1 and end[0]["status"] == "session_end" and "repeats" in end[0]["note"]
    assert LG.validate_log(log_of(out)) == []


# --------------------------------------------------------------------------
# 4. plan_crop: never a whole sheet of no level
# --------------------------------------------------------------------------

def _ctx(tmp_path):
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    from wenart.agent import overrides as OV
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out),
                               apply_edit=FakeEdits(), validators=fake_validators())


def test_plan_crop_gives_no_whole_sheet_of_another_level(tmp_path):
    """Fails on BASE: a room without a camera plan crop got the first debug image of any name (P6a:
    final/debug/deneme1_dwg_s1.jpg for r_L-1b_salon), which the agent then cited as a piece's plan crop."""
    ctx = _ctx(tmp_path)
    ctx.building["rooms"][0]["level_id"] = "L-1b"
    debug = ctx.project_out / "final" / "debug"
    debug.mkdir(parents=True)
    (debug / "deneme1_dwg_s1.jpg").write_bytes(b"jpg")
    (debug / "deneme1_dwg_L-1_p1.jpg").write_bytes(b"jpg")
    assert ctx.plan_crop_path("r1") is None
    res = TL.build_registry().call(ctx, "plan_crop", {"room_id": "r1"})
    assert res["image"] is None and res["note"] == TL.NO_PLAN_CROP_NOTE and not ctx.pending_images
    (debug / "deneme1_dwg_L-1b_p1.jpg").write_bytes(b"jpg")
    assert ctx.plan_crop_path("r1").name == "deneme1_dwg_L-1b_p1.jpg"


def test_level_named_reads_the_level_as_a_word():
    assert TL.level_named("plan_L0.jpg", "L0") and TL.level_named("deneme1_L-1b_p1.jpg", "L-1b")
    assert not TL.level_named("deneme1_L-1b_p1.jpg", "L-1") and not TL.level_named("deneme1_dwg_s1.jpg", "L1")
    assert not TL.level_named("plan_L10.jpg", "L1") and not TL.level_named("x.jpg", "")


# --------------------------------------------------------------------------
# 5. A vision opinion on a drawn piece's type is reported, not retyped
# --------------------------------------------------------------------------

def _bedroom_with_desk() -> dict:
    from test_agent_helpers import building
    b = building()
    b["furniture"].append(piece("f9", "r1", "desk", (3.4, 1.0), (1.2, 0.6), 0.0, 90.0))
    b["furniture"].append(piece("f8", "r1", "desk", (3.4, 2.0), (1.2, 0.6), 0.0, 90.0, "added_by_ai"))
    b["furniture"].append(piece("f7", "r1", "stove", (0.5, 1.5), (0.6, 0.6), 0.0, 90.0))
    return b


def test_a_vision_f1_on_a_drawn_piece_the_room_holds_has_no_tool():
    """Fails on BASE: the vision F1 'a desk is not standard for a bedroom' on the drawn desk f_L0_026 was wrong_type
    and offered retype_piece in all 4 rounds of P6a (seq 5995: a retype to a dresser, refused only by the score)."""
    b = _bedroom_with_desk()
    vision = finding("F1", "major", "f9", message="a desk is not standard for a bedroom", source="vision")
    assert CS.cause_of(vision, b) == "drawn_type" and CS.tools_for_finding(dict(vision, cause="drawn_type")) == []
    assert CS.REPORT_TO["drawn_type"] == "review"
    # the code's F1, an AI piece, a type the room never holds, a room target: unchanged
    assert CS.cause_of(finding("F1", "major", "f9"), b) == "wrong_type"
    assert CS.cause_of(dict(vision, target="f8"), b) == "wrong_type"
    assert CS.cause_of(dict(vision, target="f7"), b) == "wrong_type"
    assert CS.cause_of(dict(vision, target="r1"), b) == "wrong_type"
    fixable, not_yours = BR.classify([dict(vision, id="v1")], b, "r1", {}, {}, {})
    assert fixable == [] and not_yours[0]["cause"] == "drawn_type"


@needs_p6a
def test_p6a_vision_f1_on_the_drawn_desk_is_reported():
    b = read(P6A_FURNITURE / "building_final.json")
    desk = finding("F1", "major", "f_L0_026", room="r_L0_yatak_odasi", source="vision",
                   message="The room is furnished with a desk and office chair, which are not standard for a bedroom")
    assert CS.cause_of(desk, b) == "drawn_type"
    terrace = finding("F1", "major", "r_L1_teras_2", room="r_L1_teras_2", source="vision",
                      message="a terrace furnished with a dining table")
    assert CS.cause_of(terrace, b) == "wrong_type"


# --------------------------------------------------------------------------
# 6. The drawn layout: F3 / F8 no move within the drawn lock clears
# --------------------------------------------------------------------------

def _hall(*pieces_) -> dict:
    from test_agent_helpers import wall
    return {"schema_version": "0.1", "project": {"id": "hall"}, "status": "ok",
            "levels": [{"id": "L0", "label": "Zemin", "elevation": 0.0, "ceiling_height": 2.7}],
            "walls": [wall("w1", (0, 0), (10, 0)), wall("w2", (10, 0), (10, 8)), wall("w3", (10, 8), (0, 8)),
                      wall("w4", (0, 8), (0, 0))],
            "openings": [],
            "rooms": [{"id": "h1", "level_id": "L0", "label": "Salon", "room_type": "living", "area_computed": 80.0,
                       "polygon": [[0, 0], [10, 0], [10, 8], [0, 8]], "status": "verified"}],
            "furniture": list(pieces_), "conflicts": [], "unverified": [], "warnings": []}


# fix round after P6a (23 Oct 2026), review: a TV unit 3.15 m behind the back of the sofa s1 at (5.0, 4.0) (in reach,
# not faced), so s1's F3 stays the drawn layout and is not the missing member (``causes.front_missing``)
BEHIND_TV = piece("t1", "h1", "tv_unit", (5.0, 7.8), (1.8, 0.4), 0.0, 270.0)


def test_a_drawn_sofa_far_from_every_wall_is_the_drawn_layout():
    """Fails on BASE (no drawn_layout cause): P6a's sofas f_L-1b_041 / 042, 2 m off every wall, got move_piece in
    every round and every move was refused by the drawn lock, the wall snap or the memory. Fix round after P6a (23 Oct
    2026), review: the TV unit behind s1's back is in reach but not faced; without a piece it may face in reach the
    cause is missing_member (tests/test_m13_p6a_review.py)."""
    far = piece("s1", "h1", "sofa", (5.0, 4.0), (2.0, 0.9), 0.0, 270.0)
    near = piece("s2", "h1", "sofa", (2.0, 1.0), (2.0, 0.9), 0.0, 90.0)          # 0.55 m off the wall w1
    ai = piece("s3", "h1", "sofa", (8.0, 4.0), (2.0, 0.9), 0.0, 270.0, "added_by_ai")
    b = _hall(far, near, ai, BEHIND_TV)
    assert CS.drawn_layout_blocked(b, far, "F3") and not CS.drawn_layout_blocked(b, near, "F3")
    assert not CS.drawn_layout_blocked(b, ai, "F3")                               # an AI piece moves freely
    fs = [finding("F3", "major", "s1", room="h1"), finding("F3", "major", "s2", room="h1"),
          finding("F3", "major", "s3", room="h1"), finding("F3", "major", "s1", room="h1", source="vision")]
    CS.mark_drawn_layout(fs, b)
    assert [CS.cause_of(f, b) for f in fs] == ["drawn_layout", "off_wall", "off_wall", "off_wall"]
    assert CS.CAUSE_TOOLS["drawn_layout"] == () and "drawn furniture is kept" in CS.NO_TOOL_REASON["drawn_layout"]
    fixable, not_yours = BR.classify([dict(fs[0], id="c1", cause="drawn_layout")], b, "h1", {}, {}, {})
    assert fixable == [] and not_yours[0]["cause"] == "drawn_layout"


def test_a_piece_it_already_cuts_is_no_missing_wall_place():
    """A drawn stove 6 cm off its wall inside its counter run (P6a f_L-1_008 / 017, real03's sinks): the counter it
    already cuts is the S2 / F9's business, so the stove keeps its tools (without the rule: every slide within 1.2 m
    meets the counter, and the stove would be called the drawn layout)."""
    stove = piece("k1", "h1", "stove", (5.0, 0.36), (0.6, 0.6), 180.0, 90.0)
    counter = piece("k2", "h1", "kitchen_counter", (5.0, 0.32), (2.4, 0.6), 180.0, 90.0)
    assert not CS.drawn_layout_blocked(_hall(stove, counter), stove, "F3")
    # a counter it does not cut, standing on the only wall place within reach, does block it
    free = piece("k1", "h1", "stove", (5.0, 1.0), (0.6, 0.6), 180.0, 90.0)
    run = piece("k2", "h1", "kitchen_counter", (5.0, 0.30), (4.4, 0.6), 180.0, 90.0)
    assert CS.drawn_layout_blocked(_hall(free, run), free, "F3")


def test_a_drawn_plant_alone_is_the_drawn_layout_only_without_a_partner_or_wall_in_reach():
    plant = piece("p1", "h1", "potted_plant", (5.0, 4.0), (0.5, 0.5), 0.0, 270.0)
    b = _hall(plant)
    assert CS.drawn_layout_blocked(b, plant, "F8")
    sofa = piece("s1", "h1", "sofa", (5.0, 6.0), (2.0, 0.9), 0.0, 270.0)        # 1.30 m away: a 0.3 m move reaches
    assert not CS.drawn_layout_blocked(_hall(plant, sofa), plant, "F8")
    anchor = finding("F8", "major", "p1", room="h1", missing_anchor="t9")
    CS.mark_drawn_layout([anchor], b)
    assert CS.cause_of(anchor, b) == "missing_anchor"                            # building the anchor is its fix
    kept = dict(b, project={"id": "hall", "brief": {"furnished_rooms": "keep"}})
    assert CS.drawn_layout_blocked(kept, piece("s2", "h1", "sofa", (2.0, 1.0), (2.0, 0.9), 0.0, 90.0), "F3")


def test_the_dry_re_check_keeps_the_drawn_layout_of_an_unchanged_piece():
    before = [CS.mark_drawn_layout([finding("F3", "major", "s1", room="h1")],
                                   _hall(piece("s1", "h1", "sofa", (5.0, 4.0), (2.0, 0.9), 0.0, 270.0),
                                         BEHIND_TV))[0]]
    assert CS._metrics(before[0]).get(CS.DRAWN_LAYOUT_FLAG)
    fresh = finding("F3", "major", "s1", room="h1")
    out = LP.after_findings([fresh], before, changed={"s2"})
    assert out[0]["cause"] == "drawn_layout" and not CS._metrics(fresh).get(CS.DRAWN_LAYOUT_FLAG)
    moved = LP.after_findings([finding("F3", "major", "s1", room="h1")], before, changed={"s1"})
    assert moved[0]["cause"] == "off_wall"


@needs_p6a
def test_p6a_salon_sofas_are_the_missing_member_and_the_snappable_ones_are_not():
    """Fix round after P6a (23 Oct 2026), review: f_L-1b_041 / 042 stand 2 m off every wall with no coffee table or TV
    unit in their rooms: the missing seating member is the cause (``MISSING_FRONT``), no longer the drawn layout."""
    b = read(P6A_FURNITURE / "building_final.json")
    data = read(P6A_LOG)
    fs = [{"check": e["checklist"], "target": e["target"], "severity": e["severity"], "room_id": e.get("room_id"),
           "message": e.get("finding"), "source": e.get("source"),
           "evidence": {"metrics": dict((e.get("evidence") or {}).get("metrics") or {})}}
          for e in data["events"] if e["seq"] >= data["run_first_seq"] and e["kind"] == "finding"
          and e["round"] == 1 and e.get("source") == "code" and e.get("checklist") in ("F3", "F8")]
    CS.mark_drawn_layout(fs, b)
    cause = {f["target"]: CS.cause_of(f, b) for f in fs}
    assert cause["f_L-1b_041"] == cause["f_L-1b_042"] == "missing_member"
    assert {CS._metrics(f)[CS.DRAWN_LAYOUT_FLAG] for f in fs if f["target"] in ("f_L-1b_041", "f_L-1b_042")} == {
        CS.MISSING_FRONT}
    # 0.59 m off: a free wall place lies within 1.2 m; the plants have a sofa within a free move
    assert cause["f_L-1b_045"] == cause["f_L-1b_046"] == "off_wall"
    assert cause["f_L-1b_047"] == cause["f_L-1b_049"] == "floating"


# --------------------------------------------------------------------------
# 7. The agent stage's note after the final round
# --------------------------------------------------------------------------

def test_final_round_returns_the_stage_note_of_the_numbers_after_it(tmp_path):
    """Fails on BASE (no stage_note): P6a's stage record kept round 3's note (net 32, 'max rounds reached') while the
    report and metrics.json said net 34 after the final round."""
    out = project(tmp_path)
    critic = ScriptedCritic([[], [violation("F3", "critical", "f1", "r1", "the headboard is in the room")], []])
    chat = [{"tool_calls": [{"name": "rotate_piece", "arguments": {"piece_id": "f1", "front_deg": 90.0,
                                                                   "reason": "the headboard on the wall"}}]},
            {"tool_calls": [{"name": "finish", "arguments": {"verdict": "done"}}]}]
    loop = LP.AgentLoop(out, MM.MockModel(chat=chat), rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)},
                        clock=Clock(), code_critic=critic, recheck=FixesWhatItTouched(critic), vision=False,
                        apply_edit=FakeEdits(), validators=fake_validators(), out=lambda s: None, workers=1,
                        max_rounds=1)
    first = loop.run()
    assert LP.stage_note(first).startswith("1 round(s), 0 finding(s) removed by 0 accepted edit(s)")
    res = loop.final_round(2)
    assert res["accepted"] == 1
    assert res["stage_note"].startswith("2 round(s), ") and "1 accepted edit(s)" in res["stage_note"]
    # changed on purpose in the fix round after P6a, part 2 (tests/test_m13_p6a_integration.py): the note keeps why
    # the rounds stopped before the final round (the scheduler's records of a failed re-run must still say so)
    assert res["stage_note"].endswith(f"stop: {LP.STOPS[first['stop']['reason']]}; final round for critical findings "
                                      f"done"), res["stage_note"]
    summary = {"rounds": [{}, {}, {}], "findings_removed": 40, "accepted": 34, "rejected": 150,
               "findings_removed_predicted_same_rounds": 42, "findings_new": 6, "findings_net": 34,
               "stop": {"reason": "max_rounds"}}
    assert LP.stage_note(summary) == ("3 round(s), 40 finding(s) removed by 34 accepted edit(s) (measured; 42 "
                                      "predicted by the dry re-checks), 6 new, net 34, 150 rejected; stop: max rounds "
                                      "reached")
