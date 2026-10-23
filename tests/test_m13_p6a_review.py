"""Fix round after P6a (23 Oct 2026), review: the reviewers' findings on the fix round after P6a (620997b).

Checked, each against BASE a0a1a2e (the tests fail there: a missing name, the old verdict or a mutation named in the
docstring):

1. the F3 of a drawn sofa the drawn lock holds off every wall while no coffee table or TV unit stands in reach is its
   missing group member (``causes.drawn_layout_state`` ``MISSING_FRONT``, cause ``missing_member``), not the drawn
   layout (P6a's f_L-1b_041 / 042: a coffee table in front clears their F3);
2. the round marks its code findings (``loop.AgentLoop.round`` calls ``causes.mark_drawn_layout`` before the causes are
   taken): the mutation that drops the call (or moves it after the ``cause_of`` loop) plans a room session for a drawn
   sofa no move can clear;
3. the builder keeps a curtain or blind the decor stage sized under the slope to the millimetre
   (``build.WINDOW_DECOR_ROUND_TOL_M``): P6a's dec_L1_005 / 014 and P4a's dec_L1_005 / 018 were "made 0.00 m shorter";
4. ``infer.duplicate_symbols`` leaves drawn potted plants alone (a corner group overlaps by design) and never leaves
   out a piece without its plan crop.

The acceptance's new / net in log.json (the third agent finding) is covered by the fix round after P6b's
``test_m13_p6b_agent.test_the_edit_event_logs_new_net_changed_fitted_and_kept`` (``loop.ACCEPTANCE_LOG_KEYS``).
The P6a / P4a run folders (``runs/...``) are not in git; the tests that read them skip without them.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from test_agent_helpers import piece, violation, write_json
from test_agent_loop_p4a import make
from test_m13_agent import FINISH, log_of
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import loop as LP
from wenart.blender import build as B
from wenart.furniture import infer as INF
from wenart.furniture import placer
from wenart.furniture import plausibility as PL

ROOT = Path(__file__).resolve().parents[1]
P6A = ROOT / "runs" / "20261022-135644-m13_p6" / "results" / "furniture" / "real04" / "building_final.json"
P4A = ROOT / "runs" / "20261017-072801-full" / "results" / "furniture" / "real02" / "building_final.json"
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"
needs_p6a = pytest.mark.skipif(not P6A.is_file(), reason="the P6a run folder runs/20261022-135644-m13_p6 is not here")
needs_p4a = pytest.mark.skipif(not P4A.is_file(), reason="the P4a run folder runs/20261017-072801-full is not here")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finding(check, target, room="h1", source="code", **metrics) -> dict:
    return {"check": check, "severity": "major", "target": target, "room_id": room, "message": "wrong",
            "source": source, "evidence": {"metrics": dict(metrics)}}


# --------------------------------------------------------------------------
# 1. a drawn sofa without a piece it may face: the missing member
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


FAR = piece("s1", "h1", "sofa", (5.0, 4.0), (2.0, 0.9), 0.0, 270.0)            # 3.55 m off every wall, faces -y
BEHIND_TV = piece("t1", "h1", "tv_unit", (5.0, 7.8), (1.8, 0.4), 0.0, 270.0)     # in reach, behind its back
FRONT_TABLE = piece("c1", "h1", "table_coffee", (5.0, 2.85), (1.1, 0.5), 0.0, 270.0)   # 0.45 m in front of it


def test_a_drawn_sofa_without_a_piece_it_may_face_is_the_missing_member():
    """Fails on BASE (no ``drawn_layout_state`` / ``MISSING_FRONT``; the F3 was ``drawn_layout``, no tool): a sofa may
    stand free when it faces its coffee table or TV unit (orientation rule ``wall_or_group``), so its F3 with neither
    in reach goes once the member is added; the drawn lock still holds a sofa that has one in reach (it does not face
    it) and every sofa of a kept room (no member is added there)."""
    alone = _hall(copy.deepcopy(FAR))
    assert CS.drawn_layout_state(alone, FAR, "F3") == CS.MISSING_FRONT
    assert not CS.drawn_layout_blocked(alone, FAR, "F3")
    assert CS.front_missing(alone, FAR) and not CS.front_missing(_hall(FAR, BEHIND_TV), FAR)
    fs = CS.mark_drawn_layout([finding("F3", "s1")], alone)
    assert CS._metrics(fs[0])[CS.DRAWN_LAYOUT_FLAG] == CS.MISSING_FRONT
    assert CS.cause_of(fs[0], alone) == "missing_member"
    assert CS.tools_for_finding(dict(fs[0], cause="missing_member"))[:2] == ["complete_group", "place_group"]
    # a TV unit in reach behind its back: the drawn layout, as before
    tv = CS.mark_drawn_layout([finding("F3", "s1")], _hall(FAR, BEHIND_TV))
    assert CS._metrics(tv[0])[CS.DRAWN_LAYOUT_FLAG] is True and CS.cause_of(tv[0]) == "drawn_layout"
    # a kept room adds nothing: the drawn layout
    kept = dict(alone, project={"id": "hall", "brief": {"furnished_rooms": "keep"}})
    assert CS.drawn_layout_state(kept, FAR, "F3") is True
    # the F8 of a free piece is not about a front: unchanged
    plant = piece("p1", "h1", "potted_plant", (5.0, 4.0), (0.5, 0.5), 0.0, 270.0)
    assert CS.drawn_layout_state(_hall(plant), plant, "F8") is True
    # the cause is right: the coffee table in front clears the F3 (and the G2) for the code's own check
    room = alone["rooms"][0]
    before = {v["check"] for v in PL.room_violations(alone, room) if v["target"] == "s1"}
    after = {v["check"] for v in PL.room_violations(_hall(FAR, FRONT_TABLE), room) if v["target"] == "s1"}
    assert {"F3", "G2"} <= before and not {"F3", "G2"} & after


def test_the_dry_re_check_keeps_the_missing_member_of_an_unchanged_sofa():
    """The flag's value is carried like the others (``loop.carry_drawn_layout``): a complete_group that adds a member
    elsewhere keeps the sofa's F3 the missing member; a move of the sofa takes the cause again."""
    before = CS.mark_drawn_layout([finding("F3", "s1")], _hall(FAR))
    kept = LP.after_findings([finding("F3", "s1")], before, changed={"c9"})
    assert kept[0]["cause"] == "missing_member" and CS._metrics(kept[0])[CS.DRAWN_LAYOUT_FLAG] == CS.MISSING_FRONT
    assert LP.after_findings([finding("F3", "s1")], before, changed={"s1"})[0]["cause"] == "off_wall"


@needs_p6a
def test_p6a_salon_sofas_without_a_coffee_table_are_the_missing_member():
    """P6a's f_L-1b_041 / 042 (2 m off every wall, no coffee table or TV unit in their rooms): a coffee table 1 m in
    front of f_L-1b_041 clears its F3 on the code's own check, so the cause is the missing member. Fix round after P6b
    (``test_m13_p6b_integration``): the sofas are typed by code from the drawing (group_member / twin), so the brief
    offers complete_group for the F3 (it reported complete_group's lock "unverified: retype_piece first" before, a
    deadlock with the acceptance's refusal of a same-type confirm)."""
    b = read(P6A)
    sofa = next(f for f in b["furniture"] if f["id"] == "f_L-1b_041")
    assert CS.drawn_layout_state(b, sofa, "F3") == CS.MISSING_FRONT
    room = next(r for r in b["rooms"] if r["id"] == sofa["room_id"])
    assert "F3" in {v["check"] for v in PL.room_violations(b, room) if v["target"] == "f_L-1b_041"}
    front = PL._front_deg(placer.drawn_piece(sofa))
    assert front == 0.0                                                      # it faces +x
    cx, cy = sofa["footprint"]["center"]
    table = {"id": "f_L-1b_999", "type": "table_coffee", "room_id": sofa["room_id"], "level_id": sofa["level_id"],
             "source": "added_by_ai", "status": "verified", "front_deg": 0.0, "height": 0.4,
             "footprint": {"center": [cx + 0.45 + 1.0 + 0.25, cy], "size": [1.1, 0.5], "rotation_deg": 90.0}}
    with_table = dict(b, furniture=b["furniture"] + [table])
    assert "F3" not in {v["check"] for v in PL.room_violations(with_table, room) if v["target"] == "f_L-1b_041"}
    twin = next(f for f in b["furniture"] if f["id"] == "f_L-1b_042")
    f3 = CS.mark_drawn_layout([finding("F3", "f_L-1b_042", room=twin["room_id"])], b)[0]
    brief = BR.room_brief(b, twin["room_id"], findings=[dict(f3, id="c1", cause=CS.cause_of(f3, b))])
    fixable = brief["findings"]["fixable"]
    assert brief["findings"]["not_yours"] == [] and fixable[0]["cause"] == "missing_member"
    assert fixable[0]["tools"] == ["complete_group"]


# --------------------------------------------------------------------------
# 2. the round marks its findings (the pod path of mark_drawn_layout)
# --------------------------------------------------------------------------

def _round(tmp_path, pieces_):
    f3 = violation("F3", "major", "f3", "r2", "sofa: its back is not on a wall (1.10 m off)")
    loop, out, _ = make(tmp_path, [FINISH], [[f3]], max_rounds=1)
    for name in ("building_decor.json", "building_final.json", "building.json"):
        b = read(out / name)
        b["furniture"] = [f for f in b["furniture"] if f["id"] != "f3"] + [copy.deepcopy(p) for p in pieces_]
        write_json(out / name, b)
    loop.run()
    events = log_of(out)["events"]
    return [e for e in events if e["kind"] == "finding" and e["checklist"] == "F3"], \
        [e for e in events if e["kind"] == "plan"]


ROUND_SOFA = piece("f3", "r2", "sofa", (6.0, 1.75), (2.0, 0.9), 0.0, 270.0)    # 1.10 m off w7, 1.3 m from a wall place
ROUND_TV = piece("f4", "r2", "tv_unit", (6.0, 3.3), (1.6, 0.4), 0.0, 270.0)     # behind its back


def test_the_round_reports_a_drawn_sofa_no_move_clears(tmp_path):
    """Mutation (review of 620997b): without ``CS.mark_drawn_layout(...)`` in ``AgentLoop.round`` (or with it after the
    ``cause_of`` loop) the F3 is ``off_wall`` and a session for r2 is planned (P6a's 60 refused moves of drawn
    pieces); the round logs it ``drawn_layout`` with the reason and plans nothing."""
    f3, plans = _round(tmp_path, [ROUND_SOFA, ROUND_TV])
    assert len(f3) == 1 and f3[0]["cause"] == "drawn_layout", f3
    assert f3[0]["evidence"]["metrics"][CS.DRAWN_LAYOUT_FLAG] is True
    assert "drawn furniture is kept" in f3[0]["not_yours"]
    assert [p for p in plans if p.get("room_id") == "r2"] == []


def test_the_round_names_the_missing_member_of_a_drawn_sofa(tmp_path):
    f3, _plans = _round(tmp_path, [ROUND_SOFA])
    assert len(f3) == 1 and f3[0]["cause"] == "missing_member" and not f3[0].get("not_yours"), f3
    assert f3[0]["evidence"]["metrics"][CS.DRAWN_LAYOUT_FLAG] == CS.MISSING_FRONT


# --------------------------------------------------------------------------
# 3. curtains the decor stage sized under the slope are kept as placed
# --------------------------------------------------------------------------

def _attic():
    prep = B.prepare(read(EXAMPLE), "base")      # the example's attic: knee wall 0.87 m at y 0.6, slope to 2.23 m
    return prep, prep["building"]["levels"][-1]


def test_a_curtain_within_the_decor_stages_rounding_is_kept_as_placed():
    """Fails on BASE (1e-6): a curtain 0.4 mm over the bound (the decor stage writes size[2] to the millimetre from a
    ceiling read to 0.1 mm) was "made 0.00 m shorter" with a warning, and a short blind sized right was not built. One
    1.5 mm over is still made shorter."""
    from wenart.blender import furniture as F
    from wenart.blender import parametric as P

    prep, attic = _attic()
    ceiling = F.ceiling_above(attic, (3.0, 1.2), (1.6, 0.08), 0.0)[0]
    bound = ceiling - B.WINDOW_DECOR_CEILING_CLEAR_M - 0.8
    assert B.WINDOW_DECOR_ROUND_TOL_M == 1e-3 and bound < 1.45
    room = "r_L1_oyun_odasi"
    item = {"id": "dec_c", "type": "curtain", "level_id": "L1", "room_id": room, "host_id": None,
            "center": [3.0, 1.2, 0.8], "size": [1.6, 0.08, round(bound + 0.0004, 4)], "rotation_deg": 0.0}
    assert B._window_decor_under_roof(item, attic, F, P) == (item, None, None)
    over = dict(item, size=[1.6, 0.08, round(bound + 0.0015, 4)])
    kept, warning, dropped = B._window_decor_under_roof(over, attic, F, P)
    assert dropped is None and "shorter from the top" in warning and kept["size"][2] == pytest.approx(bound, abs=1e-4)
    # a roller blind of 0.3 m or less, sized right to the millimetre: built as placed, not "not built"
    knee = F.ceiling_above(attic, (3.0, 0.3), (1.6, 0.06), 0.0)[0]
    top = knee - B.WINDOW_DECOR_CEILING_CLEAR_M
    blind = {"id": "dec_b", "type": "blind", "level_id": "L1", "room_id": room, "host_id": None,
             "center": [3.0, 0.3, round(top - 0.25 + 0.0004, 4)], "size": [1.6, 0.06, 0.25], "rotation_deg": 0.0}
    assert blind["center"][2] + 0.25 > top + 1e-6                                  # over the bound by its rounding
    assert B._window_decor_under_roof(blind, attic, F, P) == (blind, None, None)
    b = dict(copy.deepcopy(prep["building"]), decor=[item, blind])
    assert B.decor_under_roof(b, attic) == ([item, blind], [], [])


@pytest.mark.parametrize("path, ids", [pytest.param(P6A, ("dec_L1_005", "dec_L1_014"), marks=needs_p6a),
                                       pytest.param(P4A, ("dec_L1_005", "dec_L1_018"), marks=needs_p4a)])
def test_the_attic_curtains_the_decor_stage_sizes_get_no_warning(path, ids):
    """The review's simulation: the attic curtains as the decor stage sizes them since this round (rod = the ceiling
    over them - 0.02 m, size[2] to the millimetre) pass the builder's bound without a "made 0.00 m shorter"."""
    from wenart.blender import furniture as F
    from wenart.blender import parametric as P
    from wenart.furniture import decor as D

    prep = B.prepare(read(path), "base")
    b = prep["building"]
    level = next(lv for lv in b["levels"] if lv["id"] == "L1")
    for did in ids:
        item = next(d for d in b["decor"] if d["id"] == did)
        here = D.ceiling_over(b, "L1", item["center"][:2], tuple(item["size"][:2]), float(item["rotation_deg"]))
        bottom = float(item["center"][2])
        sized = dict(item, size=list(item["size"][:2]) + [round(here - D.WINDOW_DECOR_CEILING_CLEAR_M - bottom, 3)])
        assert bottom + sized["size"][2] > here - D.WINDOW_DECOR_CEILING_CLEAR_M + 1e-6, did   # the rounding's 0.1 mm
        assert B._window_decor_under_roof(sized, level, F, P) == (sized, None, None), did


# --------------------------------------------------------------------------
# 4. duplicate symbols: floor lamps only, never without the plan crop
# --------------------------------------------------------------------------

def _crop(item: dict, key: str) -> dict:
    item["evidence"].append({"file": "deneme.dwg", "method": "ai", "entity": f"recognition:{key}", "confidence": 0.9})
    return item


def test_a_corner_group_of_drawn_plants_stays_three_plants():
    """Fails on BASE: 0.60 / 0.45 / 0.40 m plant canopies 0.45 m apart (a corner group) lost the two smaller plants as
    "one potted plant drawn twice" (shares 0.167 and 0.125)."""
    plants = [_crop(M.fp("p1", "potted_plant", (4.4, 3.4), (0.6, 0.6)), "sym_L0_001"),
              _crop(M.fp("p2", "potted_plant", (3.95, 3.4), (0.45, 0.45)), "sym_L0_002"),
              _crop(M.fp("p3", "potted_plant", (4.4, 2.95), (0.4, 0.4)), "sym_L0_003")]
    assert INF.duplicate_symbols(M.building(room_type="living", furniture=plants)) == []
    assert INF.DUPLICATE_SYMBOL_TYPES == ("floor_lamp",)


def test_a_duplicate_lamp_without_its_plan_crop_is_kept():
    """Fails on BASE: a block-named lamp (no question, no crop) was left out with no plan crop as evidence."""
    lamps = [M.fp("l1", "floor_lamp", (4.3, 0.74), (0.59, 0.59)), M.fp("l2", "floor_lamp", (4.68, 1.02), (0.44, 0.44))]
    b = M.building(room_type="living", furniture=lamps)
    assert INF.duplicate_symbols(b) == []
    _crop(lamps[1], "sym_L0_012")
    props = INF.duplicate_symbols(b)
    assert [(p["piece_id"], p["kept_id"], p["crop"]) for p in props] == [
        ("l2", "l1", "recognition/crops/sym_L0_012_ctx.png")]
