"""The way up: every stair leads into its floors (27 Oct 2026, user on real06's first floor: "Needs a pathway here,
how will the people go up to 2nd floor otherwise?" and "Make argus catch these kind of things before me").

The rules are general (wenart/blender/stair_access.py): a synthetic two-storey house whose U stair, read with its half
landing at the wrong end, arrives on a strip its floor opening cuts off from the hall; the real06 case as a small
fixture (tests/fixtures/real06_stair_20261027.json: the stair as read, the same stair on the upper plan, the floor
opening derived from the whole footprint, the rooms, walls and doors around them).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from wenart.agent import causes as C
from wenart.agent import critic_code as CC
from wenart.agent import judge as JD
from wenart.audit import kinds as K
from wenart.audit import report as AR
from wenart.audit import sense as SN
from wenart.blender import architect_details as AD
from wenart.blender import model_review as MR
from wenart.blender import stair_access as SA
from wenart.sheets import to_building as TB

FIXTURE = Path(__file__).parent / "fixtures" / "real06_stair_20261027.json"


# --------------------------------------------------------------------------
# A synthetic house: L0 one living room, L1 a hall (west) and a bedroom (east); a U stair in the hall's well
# --------------------------------------------------------------------------

def _wall(wid, lid, a, b, t=0.2):
    return {"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "exterior": False}


def _room(rid, lid, x0, y0, x1, y1, rtype):
    return {"id": rid, "level_id": lid, "room_type": rtype, "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}


def _stair_data(direction=(0.0, 1.0), assumed=True, landing_assumed=None):
    """Two flights side by side (x 0.6 and 1.8, 1.0 m wide, 9 lines from y 2.0 to 4.0); the reading took the 0.3 m
    strip at the south end for the half landing."""
    flights = [{"start": [x, 2.0], "end": [x, 4.0], "width": 1.0, "lines": 9, "spacing": 0.25} for x in (0.6, 1.8)]
    data = {"flights": flights, "landing": {"polygon": [[0.1, 1.7], [2.3, 1.7], [2.3, 2.0], [0.1, 2.0]], "depth": 0.3},
            "direction": list(direction), "direction_assumed": assumed, "turn": "U", "turn_assumed": assumed,
            "void_assumed": True, "riser_m": None, "riser_source": None, "reason": "test"}
    if landing_assumed is not None:
        data["landing_assumed"] = landing_assumed
    return data


def _house(data=None, opening_source="derived", upper_stair=False):
    outer = []
    for lid in ("L0", "L1"):
        outer += [_wall(f"w_{lid}_s", lid, (-0.1, -0.1), (6.1, -0.1)), _wall(f"w_{lid}_e", lid, (6.1, -0.1), (6.1, 5.1)),
                  _wall(f"w_{lid}_n", lid, (6.1, 5.1), (-0.1, 5.1)), _wall(f"w_{lid}_w", lid, (-0.1, 5.1), (-0.1, -0.1))]
    walls = outer + [_wall("w_L1_mid", "L1", (2.6, 0.0), (2.6, 5.0))]
    openings = [{"id": "d_in", "type": "door", "level_id": "L0", "wall_id": "w_L0_s", "center": [4.0, -0.1],
                 "width": 0.9},
                {"id": "d_hb", "type": "door", "level_id": "L1", "wall_id": "w_L1_mid", "center": [2.6, 1.0],
                 "width": 0.9}]
    stair = {"id": "st0", "level_id": "L0", "room_id": "r0", "type": "stair", "source": "from_documents",
             "footprint": {"center": [1.2, 2.85], "size": [2.2, 2.3], "rotation_deg": 0.0}, "build": True,
             "stair": data or _stair_data()}
    furniture = [stair]
    if upper_stair:                        # the same stair on the L1 plan: the arriving flight and the north landing
        furniture.append({"id": "st1", "level_id": "L1", "room_id": "h1", "type": "stair", "source": "from_documents",
                          "footprint": {"center": [0.6, 3.5], "size": [1.0, 3.0], "rotation_deg": 0.0}, "build": True,
                          "stair": {"flights": [{"start": [0.6, 2.0], "end": [0.6, 4.0], "width": 1.0, "lines": 9,
                                                 "spacing": 0.25}],
                                    "landing": {"polygon": [[0.1, 4.0], [1.1, 4.0], [1.1, 5.0], [0.1, 5.0]],
                                                "depth": 1.0},
                                    "direction": [0.0, 1.0], "direction_assumed": True, "turn": "straight",
                                    "turn_assumed": True}})
    slab_l1 = {"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "z_top": 3.0, "thickness": 0.2,
               "outline": [[-0.2, -0.2], [6.2, -0.2], [6.2, 5.2], [-0.2, 5.2]], "variants": [],
               "openings": [{"id": "sv_1", "kind": "stair_void", "furniture_id": "st0", "source": opening_source,
                             "polygon": [[0.1, 1.7], [2.3, 1.7], [2.3, 4.0], [0.1, 4.0]]}]}
    return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.8},
                       {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.8}],
            "rooms": [_room("r0", "L0", 0.0, 0.0, 6.0, 5.0, "living"), _room("h1", "L1", 0.0, 0.0, 2.5, 5.0, "hall"),
                      _room("b1", "L1", 2.7, 0.0, 6.0, 5.0, "bedroom")],
            "walls": walls, "openings": openings, "furniture": furniture,
            "slabs": [{"id": "sl_L0", "below_level_id": None, "above_level_id": "L0", "z_top": 0.0, "thickness": 0.2,
                       "outline": [[-0.2, -0.2], [6.2, -0.2], [6.2, 5.2], [-0.2, 5.2]], "openings": [],
                       "variants": []}, slab_l1]}


def _piece(b, pid="st0"):
    return next(f for f in b["furniture"] if f["id"] == pid)


def _opening(b, sid="sl_L1"):
    s = next(s for s in b["slabs"] if s["id"] == sid)
    return Polygon(s["openings"][0]["polygon"])


def test_a_u_stair_read_with_its_half_landing_at_the_wrong_end_is_cut_off():
    b = _house()
    rec = SA.assess(b, _piece(b))
    assert rec["judged"] and rec["ok"] is False
    assert rec["arrival"]["ok"] is False and rec["arrival"]["pocket"] is True        # a strip no way joins to a room
    assert rec["arrival"]["room"] == "h1" and rec["arrival"]["rooms"] == []
    assert rec["start"]["ok"] is True                                                # L0: the living room goes round
    assert "arrives on L1" in SA.cut_off_text(rec) and "no 0.80 m way joins to any room of L1" in SA.cut_off_text(rec)
    # the sense line no longer joins the floors at the stair's centre: the start room and the arrival floor's room
    assert SA.stair_rooms(b, _piece(b)) == {"start": "r0", "arrival": "h1", "level_id": "L0", "up_level_id": "L1"}
    assert SN.graph(b)[1][("r0", "h1")] == "st0"


def test_the_architect_moves_the_assumed_half_landing_and_cuts_the_opening_again():
    b = _house()
    old = _opening(b)
    out = SA.fix_arrivals(b)
    (row,) = out["stairs"]
    assert out["fixed"] == 1 and row["status"] == "fixed"
    assert row["change"].startswith("the assumed half landing at the other end")
    tried = [t["reading"] for t in row["tried"]]
    assert tried[0].startswith("the same reading, its opening cut") and not row["tried"][0]["ok"]
    assert "the assumed rise direction flipped" in tried
    st = _piece(b)["stair"]
    assert SA.landing_end(st) == "hi" and st["landing"]["depth"] == pytest.approx(1.0, abs=0.01)   # to the wall face
    assert st["landing_assumed"] is True and st["direction_assumed"] is True       # still no drawing says it
    assert st["access_fix"]["by"] == "architect" and _piece(b)["adjusted_by_ai"]["rule"] == "architect K4"
    assert _piece(b)["drawn_footprint"] == {"center": [1.2, 2.85], "size": [2.2, 2.3], "rotation_deg": 0.0}
    assert row["before"]["opening"] == [[0.1, 1.7], [2.3, 1.7], [2.3, 4.0], [0.1, 4.0]]
    new = _opening(b)
    rec = SA.assess(b, _piece(b))
    assert rec["ok"] and rec["arrival"]["rooms"] == ["b1", "h1"] and rec["arrival"]["room"] == "h1"
    arrival = rec["ends"]["arrival"]
    assert new.intersection(arrival).area < 0.01                     # never over the arrival floor
    assert old.intersection(arrival).area > 0.2                     # the drawn footprint's opening was
    # the floor over the first flight's low steps (headroom >= 2 m under the slab) stays: the opening starts one going
    # before the first step that needs it (riser 3.0 / 18 m, fifth step), not at the first riser
    first = Polygon([(0.1, 2.0), (1.1, 2.0), (1.1, 2.69), (0.1, 2.69)])
    assert new.intersection(first).area < 0.01 and new.bounds[3] == pytest.approx(5.002, abs=1e-3)
    assert SA.fix_arrivals(b)["stairs"][0]["status"] == "ok"        # idempotent: the fixed stair passes


def test_m9_and_argus_see_the_cut_off_stair_and_its_house_score_counts_it():
    b = _house()
    found, n = MR.stair_walks(b)
    assert n > 0
    stair = [f for f in found if f["target"] == "st0"]
    assert len(stair) == 1 and stair[0]["severity"] == "critical" and stair[0]["check"] == "M9"
    assert stair[0]["metrics"]["arrival_ok"] is False and stair[0]["fix"].startswith("flip the assumed stair")
    rec = MR.review(b, None, prep={})
    assert rec["checks"]["M9"]["status"] == "ok" and rec["checks"]["M9"]["failed"] >= 1
    line = AR.model_line(SimpleNamespace(model_review=rec))
    m9 = [f for f in line["findings"] if f["check"] == "M9"]
    assert m9 and all(f["kind"] == "no_sense" for f in m9) and m9[0]["fix"] and m9[0]["owner"] == "architect"
    assert K.kind_of({"check": "M9"}) == "no_sense"
    # the house score: the code critic's model family carries the review (critic_code.model_items)
    items = CC.model_items(b, None)
    assert JD.house_score([], items, [], 0)["counts"]["critical"] >= 1
    assert C.cause_of(stair[0], b) == "stair_access" and C.tools_for_finding(stair[0]) == []
    fixed = copy.deepcopy(b)
    SA.fix_arrivals(fixed)
    assert not [f for f in MR.stair_walks(fixed)[0] if f["severity"] == "critical"]


def test_argus_reads_the_stair_warnings_of_the_build():
    from wenart.audit import process as PR
    fixed = SA.fix_arrivals(_house())["stairs"][0]
    assert PR.classify(f"architect K4: {fixed['change']}")[:3] == ("stair_reading", "info", "other")
    kept = SA.fix_arrivals(_house(_stair_data(assumed=False, landing_assumed=False), opening_source="drawn"))
    row = kept["stairs"][0]
    assert PR.classify(f"architect K4: {row['found']}; {row['reason']}")[:3] == ("stair_cut_off", "major", "no_sense")
    assert PR.classify("stair st0: the plan of L1 draws the same stair (st1) with its landing at the north end")[0] \
        == "stair_reading"


def test_a_drawn_stair_no_reading_connects_stays_and_is_asked():
    b = _house(_stair_data(assumed=False, landing_assumed=False), opening_source="drawn")
    out = SA.fix_arrivals(b)
    (row,) = out["stairs"]
    assert row["status"] == "open" and row["tried"] == [] and out["open"] == 1
    assert _piece(b)["stair"]["direction"] == [0.0, 1.0] and _opening(b).area == pytest.approx(2.2 * 2.3)
    q = AD.stair_walks({"stair_access": out})
    assert q["id"] == "K4" and q["severity"] == "major" and q["status"] == "open"
    assert q["answers"][0]["open"] and "is cut off" in q["answers"][0]["ask"]
    assert "no 0.80 m way joins to any room of L1" in q["answers"][0]["found"]
    fixed = AD.stair_walks({"stair_access": SA.fix_arrivals(_house())})
    assert fixed["status"] == "fixed" and fixed["answers"][0]["change"].startswith("the assumed half landing")


def test_the_upper_plan_names_the_half_landing_and_the_arriving_flight():
    b = _house(upper_stair=True)
    m = SA.upper_match(b, _piece(b))
    assert m["end"] == "hi" and m["arrives"] == 0 and m["depth"] == pytest.approx(1.0)
    recs = SA.read_across_levels(b)
    assert [r["stair"] for r in recs] == ["st0"]
    st = _piece(b)["stair"]
    assert st["direction"] == [0.0, -1.0] and st["direction_assumed"] is False and st["turn_assumed"] is False
    assert st["landing_source"] == "upper plan" and st["upper_plan"]["piece_id"] == "st1"
    assert _piece(b)["footprint"]["size"] == pytest.approx([2.2, 3.0])           # flights + the half landing
    assert _piece(b)["drawn_footprint"]["size"] == [2.2, 2.3]
    assert _piece(b)["adjusted_by_ai"]["rule"] == "stair_upper_plan"
    assert SA.read_across_levels(b) == []                                         # said once
    # the build-time fix takes the upper plan's reading first; the flight the upper plan draws arrives
    b2 = _house(upper_stair=True)
    row = SA.fix_arrivals(b2)["stairs"][0]
    assert row["status"] == "fixed" and row["change"].startswith("the upper plan's reading")
    rec = SA.assess(b2, _piece(b2))
    assert rec["ends"]["arrival_at"] == pytest.approx((0.6, 2.0), abs=1e-3)
    # another stair 10 cm off is no match
    b3 = _house(upper_stair=True)
    for f in _piece(b3, "st1")["stair"]["flights"]:
        f["start"][0] += 0.1
        f["end"][0] += 0.1
    assert SA.upper_match(b3, _piece(b3)) is None


def test_the_slab_opening_is_cut_to_the_flights_half_landing_and_headroom():
    b = _house(upper_stair=True)
    SA.read_across_levels(b)
    poly = SA.derived_opening(_piece(b), 3.0, 2.8)
    p = Polygon(poly)
    assert p.bounds == pytest.approx((0.098, 2.0 - 0.002, 2.302, 5.002), abs=1e-3)
    arrival = Polygon([(0.1, 1.1), (1.1, 1.1), (1.1, 2.0), (0.1, 2.0)])
    assert p.intersection(arrival).area < 0.01
    # sheets.to_building cuts the slab with it (a stair without drawn flights keeps its footprint)
    from shapely.geometry import box
    lv1, lv0 = b["levels"][1], b["levels"][0]
    lv1["evidence"] = []
    slab = TB._slab(lv1, lv0, {"L1": box(-0.2, -0.2, 6.2, 5.2), "L0": box(-0.2, -0.2, 6.2, 5.2)}, b["furniture"],
                    {"thickness": {"value": 0.2, "method": "section", "evidence": []}}, 0.2, "sl_L1")
    assert slab["openings"][0]["polygon"] == poly
    plain = copy.deepcopy(b["furniture"])
    plain[0].pop("stair")
    slab = TB._slab(lv1, lv0, {"L1": box(-0.2, -0.2, 6.2, 5.2), "L0": box(-0.2, -0.2, 6.2, 5.2)}, plain,
                    {"thickness": {"value": 0.2, "method": "section", "evidence": []}}, 0.2, "sl_L1")
    assert Polygon(slab["openings"][0]["polygon"]).area == pytest.approx(2.2 * 3.0, abs=1e-3)


def test_a_door_behind_the_opening_and_a_floor_part_cut_off_are_m9_findings():
    b = _house()
    # a store room north of the hall, entered only across the stair's well
    b["rooms"].append(_room("s1", "L1", 0.0, 5.2, 2.5, 6.5, "storage"))
    b["walls"].append(_wall("w_L1_n2", "L1", (-0.1, 6.6), (2.6, 6.6)))
    b["openings"].append({"id": "d_store", "type": "door", "level_id": "L1", "wall_id": "w_L1_n", "center": [1.7, 5.1],
                          "width": 0.8})
    s = b["slabs"][1]
    s["openings"][0]["polygon"] = [[0.1, 1.7], [2.3, 1.7], [2.3, 5.0], [0.1, 5.0]]   # the well to the north wall
    rec = SA.walk_review(b)
    doors = {(d["door"], d["room"]): d for d in rec["doors"]}
    assert doors[("d_store", "h1")]["kind"] == "opening" and doors[("d_store", "h1")]["blocked_by"] == ["sv_1"]
    (part,) = rec["parts"]
    assert part["rooms"] == ["s1"] and part["openings"] == ["sv_1"] and part["doors"] == ["d_store"]
    found = MR.stair_walks(b)[0]
    sev = {(f["target"], f["metrics"].get("part")): f["severity"] for f in found}
    assert sev[("d_store", "door")] == "major" and sev[("sv_1", "floor")] == "critical"


# --------------------------------------------------------------------------
# The architect action flip_stair (an answer, a decision of the AI architect or of Argus)
# --------------------------------------------------------------------------

def test_flip_stair_reads_an_assumed_stair_the_other_way_and_cuts_its_opening_again():
    from wenart.blender import architect_actions as AA
    b = _house()
    (rec,) = AA.apply_answers(b, {"AI.flip_stair:st0": {"option": "flip_stair", "by": "argus", "params": {}}})
    assert rec["ok"] and "the half landing at the other end" in rec["change"]
    assert "the rise direction flipped:" not in rec["change"]                    # that reading is cut off too
    piece = _piece(b)
    assert piece["adjusted_by_ai"]["answer_key"] == "AI.flip_stair:st0" and piece["stair"]["access_fix"]["rule"]
    assert SA.assess(b, piece)["ok"] and _opening(b).intersection(SA.assess(b, piece)["ends"]["arrival"]).area < 0.01
    # again: the other reading that leads into both floors (the other flight arrives)
    (rec,) = AA.apply_answers(b, {"AI.flip_stair:st0": {"option": "flip_stair", "by": "argus", "params": {}}})
    assert rec["ok"] and SA.assess(b, _piece(b))["ok"]
    # a drawn rise direction is never flipped
    drawn = _house(_stair_data(assumed=False))
    (rec,) = AA.apply_answers(drawn, {"AI.flip_stair:st0": {"option": "flip_stair", "by": "argus", "params": {}}})
    assert rec["ok"] is False and "drawn" in rec["change"] and _piece(drawn)["stair"]["direction"] == [0.0, 1.0]
    (rec,) = AA.apply_answers(drawn, {"AI.flip_stair:r0": {"option": "flip_stair", "by": "argus", "params": {}}})
    assert rec["ok"] is False and rec["change"] == "no stair r0"


def test_argus_decides_flip_stair_by_code_for_a_cut_off_assumed_stair():
    from wenart.agent import architect_ai as AIA
    from wenart.audit import argus_ai as AX
    from wenart.blender import architect_actions as AA
    b = _house()
    rep = {"findings": AR.model_line(SimpleNamespace(model_review=MR.review(b, None, prep={})))["findings"]}
    _a, _w, _r, decisions = AX.code_actions(rep, b)
    assert [(d["action"], d["element"]) for d in decisions] == [("flip_stair", "st0")]
    assert decisions[0]["finding"]["check"] == "M9" and "flip_stair" in AX.FIX_ARCH
    drawn = _house(_stair_data(assumed=False))
    rep = {"findings": AR.model_line(SimpleNamespace(model_review=MR.review(drawn, None, prep={})))["findings"]}
    assert AX.code_actions(rep, drawn)[3] == []                                   # a drawn direction: no decision
    assert "flip_stair" in AIA.LOOK_ACTIONS["piece"]
    key, ans, why = AIA._decision({"action": "flip_stair", "element": "st0"}, AA.Plan(b), b, "L0")
    assert key == "AI.flip_stair:st0" and ans["opt"]["id"] == "flip_stair" and not why


def test_a_flip_stair_answer_is_carried_out_before_the_slabs_are_built():
    from wenart.blender import build as B
    b = _house()
    b["project"] = {"name": "fixture"}
    plain = B.prepare(copy.deepcopy(b), "base", None)
    assert plain["stair_access"]["fixed"] == 1                     # K4: the half landing at the other end
    first = SA.assess(plain["building"], _piece(plain["building"]))["ends"]["arrival_at"]
    brief = {"architect_answers": {"AI.flip_stair:st0": {"option": "flip_stair", "by": "argus"}}}
    prep = B.prepare(copy.deepcopy(b), "base", brief)
    applied = [r for r in prep["architect_applied"] if r["option"] == "flip_stair"]
    assert applied and applied[0]["ok"]
    built = prep["building"]
    rec = SA.assess(built, _piece(built))
    assert rec["ok"] and rec["ends"]["arrival_at"] != pytest.approx(first)       # the other flight arrives
    voids = prep["slabs"]["by_level"]["L1"]["under"]["voids"]
    assert any(Polygon(v).symmetric_difference(_opening(built)).area < 1e-6 for v in voids)


# --------------------------------------------------------------------------
# Under the stair: closed where it is low, carried where it hangs (user on real06's ground floor: "This stairs not
# making any sense": loose slabs seen from below)
# --------------------------------------------------------------------------

def _built_plan(b, level_index=0):
    from wenart.blender import shell
    level = b["levels"][level_index]
    walls = [w for w in b["walls"] if w["level_id"] == level["id"]]
    item = next(i for i in shell.plan_stairs(b, level, slab_void=True) if i["plan"])
    plan = shell.stair_build_plan(item["plan"], walls)
    shell.stair_under_plan(plan, walls)
    return plan


def test_the_space_under_a_stair_is_closed_where_it_is_low():
    from wenart.blender import parametric as P
    from wenart.blender import shell
    b = _house()
    SA.fix_arrivals(b)
    plan = _built_plan(b)
    under = plan["under"]
    assert under["low_m2"] > 1.0 and under["posts"] == []          # the half landing is low: closed, not posted
    of = {p["of"] for p in under["panels"]}
    assert {"flight 1", "flight 2"} <= of
    for p in under["panels"]:                                       # from the floor to the underside, never higher
        assert 0.0 <= p["zp"] <= SA.HEADROOM_M + 1e-6 and 0.0 <= p["zq"] <= SA.HEADROOM_M + 1e-6
    # every open edge of the low space has a panel; the edges along a wall have none (the wall closes them)
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    from shapely.geometry import LineString
    wall_zone = Polygon()
    for w in walls:
        wall_zone = wall_zone.union(SA._wall_poly(w).buffer(SA.WALL_TOUCH_M))
    assert not any(LineString([p["p"], p["q"]]).within(wall_zone) for p in under["panels"])
    # where the flight's soffit reaches 2.0 m a panel closes the space across the flight
    assert any(abs(p["zp"] - SA.HEADROOM_M) < 1e-3 and abs(p["zq"] - SA.HEADROOM_M) < 1e-3 for p in under["panels"])
    parts = P.stair_parts(plan)
    spandrels = [p for p in parts if p["role"] == "spandrel"]
    assert len(spandrels) == len(under["panels"])
    assert all(min(v[2] for v in p["verts"]) == pytest.approx(0.0) for p in spandrels)        # on the floor
    assert len(P.stair_face_slots(parts)) == sum(len(p["faces"]) for p in parts)
    assert set(P.stair_face_slots(spandrels)) == {1}                                          # the structure finish
    rec = shell.stair_record(plan, parts)
    assert rec["under"]["panels"] == len(spandrels) and rec["under"]["posts"] == 0
    assert any(a["kind"] == "stair_under" for a in plan["assumed"])


def test_a_landing_high_enough_to_walk_under_stands_on_posts():
    flights = [{"start": [x, 0.5], "end": [x, 3.5], "width": 1.0, "lines": 13, "spacing": 0.25} for x in (2.0, 3.2)]
    landing = {"polygon": [[1.5, 3.5], [3.7, 3.5], [3.7, 4.5], [1.5, 4.5]], "depth": 1.0}     # free of the walls
    b = _one_stair_house(flights, landing)
    b["levels"][1]["elevation"] = 5.2                           # a tall storey: the half landing at 2.6 m
    b["levels"][0]["ceiling_height"] = 5.0
    b["furniture"][0]["stair"]["turn"] = "U"
    plan = _built_plan(b)
    assert plan["landing"]["z"] - plan["landing"]["thickness"] >= SA.HEADROOM_M
    posts = plan["under"]["posts"]
    assert len(posts) == 2 and all(p["at"][1] > 4.35 for p in posts)         # the two free corners, not the flights'
    from wenart.blender import parametric as P
    assert sum(1 for p in P.stair_parts(plan) if p["role"] == "landing_post") == 2


def test_m9_reports_a_stair_built_with_its_underside_open():
    b = _house()
    SA.fix_arrivals(b)
    plan = _built_plan(b)
    manifest = {"objects": [{"element_id": "st0", "kind": "furniture", "type": "stair",
                             "stair": {"risers": plan["risers"]}}]}                  # an older build: no underside
    found, n = MR.stair_undersides(b, manifest)
    assert n == 1 and len(found) == 1 and found[0]["severity"] == "major"
    assert "loose slabs" in found[0]["message"] and found[0]["metrics"]["part"] == "underside"
    manifest["objects"][0]["stair"]["under"] = {"panels": len(plan["under"]["panels"]), "posts": 0}
    assert MR.stair_undersides(b, manifest)[0] == []
    rec = MR.review(b, {"objects": [dict(manifest["objects"][0], stair={"risers": 18})]}, prep={})
    assert any(f["check"] == "M9" and f["metrics"].get("part") == "underside" for f in rec["findings"])


# --------------------------------------------------------------------------
# K1 for any stair shape: risers too high are fixed in a quarter landing (winders) or by a longer straight run
# --------------------------------------------------------------------------

def _one_stair_house(flights, landing=None, fixed=()):
    """L0 (one 6 x 5 m room) under L1, a 3.0 m storey; one stair with ``flights`` (and ``landing``) on L0."""
    b = _house()
    data = {"flights": flights, "landing": landing, "direction": [0.0, 1.0], "direction_assumed": True,
            "turn": "straight" if len(flights) == 1 else "other", "turn_assumed": True, "void_assumed": True,
            "riser_m": None, "riser_source": None, "reason": "test"}
    b["furniture"] = [{"id": "st0", "level_id": "L0", "room_id": "r0", "type": "stair", "source": "from_documents",
                       "footprint": {"center": [1.0, 2.0], "size": [1.0, 2.0], "rotation_deg": 0.0}, "build": True,
                       "stair": data}] + list(fixed)
    return b


def _k1(b):
    from wenart.blender import shell
    items = shell.plan_stairs(b, b["levels"][0])
    q = AD.stair_details(items, "bars", b)
    return q, next(i["plan"] for i in shell.plan_stairs(b, b["levels"][0]))


def test_k1_a_steep_straight_stair_gets_a_longer_run_where_the_floor_is_free():
    flight = {"start": [1.0, 3.0], "end": [1.0, 5.0], "width": 1.0, "lines": 9, "spacing": 0.25}
    b = _one_stair_house([dict(flight)])                          # 9 risers for 3.0 m: 0.333 m each
    q, plan = _k1(b)
    st = _piece(b)["stair"]
    assert st["extra_treads"] == 8 and plan["risers"] == 17 and plan["riser_m"] == pytest.approx(3.0 / 17)
    assert plan["flights"][0]["nosings"][0] == pytest.approx((1.0, 1.0)) and plan["flights"][0]["extra_treads"] == 8
    assert _piece(b)["adjusted_by_ai"]["rule"] == "architect K1" and "longer at its foot" in \
        _piece(b)["adjusted_by_ai"]["reason"]
    (ans,) = q["answers"]
    assert not ans.get("open") and "a longer run" in ans["change"]
    assert ans["options"][0]["id"] == "stair_run" and ans["options"][0]["params"]["count"] == 0
    # a kitchen run across the floor at its foot: no longer run fits, the question stays open for the architect
    counter = {"id": "kc", "level_id": "L0", "room_id": "r0", "type": "kitchen_counter", "build": True,
               "footprint": {"center": [1.0, 1.2], "size": [2.0, 0.6], "rotation_deg": 0.0}}
    b2 = _one_stair_house([dict(flight)], fixed=[counter])
    q2, plan2 = _k1(b2)
    assert "extra_treads" not in _piece(b2)["stair"] and plan2["risers"] == 9
    (ans2,) = q2["answers"]
    assert ans2["open"] and "does not fit" in ans2["found"]
    assert [o["id"] for o in ans2["options"]] == ["stair_run", "keep"]
    from wenart.blender import architect_actions as AA
    (rec,) = AA.apply_answers(b2, {"K1:st0": {"option": "stair_run", "params": {"count": "auto"}}})
    assert rec["ok"] is False and "does not fit" in rec["change"]


def test_k1_a_steep_l_stair_gets_winders_in_its_quarter_landing():
    flights = [{"start": [1.0, 1.0], "end": [1.0, 2.25], "width": 1.0, "lines": 6, "spacing": 0.25},
               {"start": [1.5, 2.75], "end": [2.75, 2.75], "width": 1.0, "lines": 6, "spacing": 0.25}]
    landing = {"polygon": [[0.5, 2.25], [1.5, 2.25], [1.5, 3.25], [0.5, 3.25]], "depth": 1.0}
    b = _one_stair_house(flights, landing)                       # 12 risers for 3.0 m: 0.25 m each
    q, plan = _k1(b)
    assert _piece(b)["stair"]["winders"] == "auto" and "quarter landing" in _piece(b)["adjusted_by_ai"]["reason"]
    assert plan["winders"] == 4 and plan["riser_m"] == pytest.approx(3.0 / 16)       # at most 4 in a quarter turn
    land = plan["landing"]
    # 28 Oct 2026 (parametric.WINDER_TREADS_NOTE): 4 risers in the turn are 5 treads, the first at the landing's level
    assert land["role"] == "winders" and len(land["winders"]) == 5
    polys = [Polygon(w["polygon"]) for w in land["winders"]]
    assert sum(p.area for p in polys) == pytest.approx(1.0, abs=0.01)                # they fill the landing
    assert all(Polygon(landing["polygon"]).buffer(1e-6).contains(p) for p in polys)
    tops = [w["top"] for w in land["winders"]]
    assert tops == sorted(tops) and tops[0] == pytest.approx(plan["flights"][0]["top_z"])
    assert plan["flights"][1]["base_z"] == pytest.approx(tops[-1])                   # the second flight goes on
    (ans,) = q["answers"]
    assert not ans.get("open") and "winders" in ans["change"] and "quarter landing" in ans["change"]


# --------------------------------------------------------------------------
# The real06 case (fixture: the stair as read, its upper end on the L1 plan, the derived opening)
# --------------------------------------------------------------------------

@pytest.fixture()
def real06():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_real06_the_stair_arrives_on_a_strip_cut_off_from_the_hall(real06):
    rec = SA.assess(real06, _piece(real06, "f_L0_001"))
    assert rec["ok"] is False and rec["arrival"]["pocket"] is True and rec["arrival"]["room"] == "r_L1_hol"
    assert rec["ends"]["arrival_at"][1] == pytest.approx(13.375, abs=0.01)          # past the apron, by the wall
    found = MR.stair_walks(real06)[0]
    assert {(f["target"], f["severity"]) for f in found} >= {("f_L0_001", "critical"), ("d_L1_009", "major")}


def test_real06_the_upper_plan_reading_leads_into_the_hall(real06):
    out = SA.fix_arrivals(real06)
    (row,) = out["stairs"]
    assert row["status"] == "fixed" and row["change"].startswith("the upper plan's reading")
    st = _piece(real06, "f_L0_001")["stair"]
    assert st["direction"] == [0.0, -1.0] and st["direction_assumed"] is False
    assert SA.landing_end(st) == "hi" and st["landing"]["depth"] >= SA.HALF_LANDING_MIN_M     # the north end
    rec = SA.assess(real06, _piece(real06, "f_L0_001"))
    assert rec["ok"] and rec["arrival"]["room"] == "r_L1_hol" and "r_L1_banyo" in rec["arrival"]["rooms"]
    assert rec["ends"]["arrival_at"][1] == pytest.approx(11.575, abs=0.01)          # the hall's south part
    new = _opening(real06)
    assert new.intersection(rec["ends"]["arrival"]).area < 0.01
    assert not [f for f in MR.stair_walks(real06)[0] if f["severity"] == "critical"]


def test_real06_the_build_fixes_it_before_planning_and_the_architect_reports_k4(real06):
    from wenart.blender import build as B
    prep = B.prepare(real06, "base", None)
    assert prep["stair_access"]["fixed"] == 1
    built = prep["building"]
    assert _piece(built, "f_L0_001")["stair"]["access_fix"]["rule"] == "architect K4"
    assert _piece(real06, "f_L0_001")["stair"]["direction_assumed"] is True      # the caller's building is kept
    assert _opening(real06).bounds[1] == pytest.approx(11.2256)
    assert _opening(built).bounds[1] == pytest.approx(11.5732, abs=1e-3)
    q = next(q for q in prep["architect"]["questions"] if q["id"] == "K4")
    assert q["status"] == "fixed" and q["answers"][0]["element"] == "f_L0_001"
    assert any(w.startswith("architect K4: the upper plan's reading") for w in prep["warnings"])


def test_every_dwelling_of_a_building_has_its_main_floor():
    # 27 Oct 2026 (real04: two twin houses; the smaller house's stairs were "not on the main floor")
    lid = "L0"
    b = {"levels": [{"id": lid, "elevation": 0.0, "order": 0}], "openings": [], "furniture": [], "slabs": [],
         "walls": [], "rooms": []}
    for k, x0 in enumerate((0.0, 20.0)):                          # two houses 11 m apart, three open rooms each
        for j in range(3):
            b["rooms"].append(_room(f"r{k}{j}", lid, x0 + 3.0 * j, 0.0, x0 + 3.0 * j + 3.0, 4.0, "bedroom"))
    b["rooms"].append(_room("pocket", lid, 40.0, 0.0, 41.5, 1.5, "storage"))
    g = SA.walk_graph(b, b["levels"][0])
    assert len(g["mains"]) >= 2 and g["main"] in g["mains"]
    pocket_group = g["group"][g["room_main"]["pocket"]] if "pocket" in g["room_main"] else None
    assert pocket_group is None or pocket_group not in g["mains"]           # one room is no dwelling's floor
