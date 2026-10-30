"""30 Oct 2026 (real04 run 20261029-201533-full): a door or drawer front blocked by another piece is cleared by the
safest move (``wenart.furniture.fixture_use.clear_front``, rule 5; architect F4 ``clear_front``). CPU only.

The case: the drawn wardrobes f_L0_009 (r_L0_yatak_odasi_3) and f_L0_011 (r_L0_yatak_odasi_4) had 0.17 m free in front
of their doors; the drawn desks f_L0_029 / f_L0_028 stood there. The model review's M19 and Argus U16 found it
critical (the GPU test test_the_model_as_built_has_no_critical_finding failed), but no rule fired: the architect's F4
measured the wardrobes with its old 80 % strip (88 % free: "fine"), and its safe default ``free_front`` knew only
appliances and nightstands and only turned the blocked piece itself; the agent's critic had only G13's 0.80 m walking
room (major), so its slides of the wardrobe to 0.62 m (which opened the doors) were refused as G13 stayed.

Now F4 measures door-fronted storage like M19 and U16 and gives a front that cannot open the default ``clear_front``:
the piece slid along its wall or turned, or the piece in front of it slid along its wall or turned with what belongs to
it (its chair), at most 0.5 m, every code check passed, the drawn values kept, ``adjusted_by_ai`` by the architect.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from test_decor_m8 import room_building
from wenart.agent import architect_ai as AAI
from wenart.audit import argus_ai as ARG
from wenart.audit import lessons as LS
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.blender import model_review as MR
from wenart.furniture import fixture_use as FU
from wenart.furniture import schemas

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "tests" / "fixtures" / "real04_bedroom_fronts_20261030.json"

# real04's bedroom r_L0_yatak_odasi_3 moved to the origin (3.02 x 4.66 m): the wardrobe on the south wall 0.20 m off
# the west corner, the desk on the west wall 0.17 m before the wardrobe's doors, its chair, the bed on the west wall,
# the door in the east wall by the wardrobe
WARDROBE = ("wardrobe", (0.927, 0.30), 180.0, (1.4533, 0.6))       # front 90: north, into the room
DESK = ("desk", (0.30, 1.492), 90.0, (1.4471, 0.6))                 # front 0: east
CHAIR = ("office_chair", (0.657, 1.492), 270.0, (0.5, 0.5))
BED = ("bed_double", (0.951, 3.363), 90.0, (1.55, 1.9))
DOOR = ("d1", "e", 0.543, 0.778, True)


def _bedroom(*extra, windows=()) -> dict:
    return room_building(3.018, 4.656, "bedroom", furniture=[WARDROBE, DESK, CHAIR, BED, *extra], doors=(DOOR,),
                         windows=windows)


def _fix(b: dict, fid: str = "f_L0_001"):
    plan = AA.Plan(b)
    f = next(x for x in b["furniture"] if x["id"] == fid)
    return FU.clear_front(f, plan.room[f["room_id"]]["polygon"], AA._room_pieces(plan, f),
                          blocked=AA._door_blocked(plan, f.get("level_id")), openings=list(plan.openings.values()),
                          walls=plan.walls)


def _by_id(b: dict) -> dict:
    return {f["id"]: f for f in b["furniture"]}


# --------------------------------------------------------------------------
# The rule (pure)
# --------------------------------------------------------------------------

def test_the_wardrobe_slides_along_its_wall_and_the_desk_stays_off_the_bed():
    b = _bedroom()
    w = _by_id(b)["f_L0_001"]
    was = FU.piece_access(w, b["rooms"][0]["polygon"], b["furniture"], storage=True)
    assert was["severity"] == "critical" and was["blockers"] == ["f_L0_002"] and abs(was["free_m"] - 0.168) < 0.005
    fix = _fix(b)
    # the safest move: the wardrobe 0.40 m along its wall (no walking room taken); pushing the desk 0.35 m north would
    # leave it 2 cm from the bed
    assert fix["mover"] == "f_L0_001" and fix["how"] == "slid" and abs(fix["moved_m"] - 0.40) < 1e-6
    assert fix["harm_m"] == 0.0 and fix["free_m"] >= FU.STORAGE_OPEN_M["wardrobe"] + FU.CLEAR_MARGIN_M
    assert [m["id"] for m in fix["moves"]] == ["f_L0_001"]
    moved = fix["moves"][0]
    assert moved["footprint"]["center"] == [1.327, 0.3] and moved["front_deg"] == 90.0     # along its wall, back on it
    assert "0.17 m free" in fix["reason"] and "f_L0_002 in the way" in fix["reason"] and "code checks" in fix["reason"]
    # pure: nothing changed
    assert w["footprint"]["center"] == [0.927, 0.30]


def test_the_piece_in_front_gives_way_with_its_chair_when_the_blocked_one_cannot_move():
    # a wardrobe from wall to wall: it cannot slide; the desk on the east wall 0.20 m before its doors slides north with
    # the chair at it (one unit), each 0.35 m
    b = room_building(2.0, 3.0, "bedroom", furniture=[("wardrobe", (1.0, 0.3), 180.0, (2.0, 0.6)),
                                                      ("desk", (1.7, 1.4), 270.0, (1.2, 0.6)),
                                                      ("office_chair", (1.15, 1.4), 90.0, (0.5, 0.5))])
    fix = _fix(b)
    assert fix["mover"] == "f_L0_002" and fix["how"] == "slid"
    got = {m["id"]: m for m in fix["moves"]}
    assert set(got) == {"f_L0_002", "f_L0_003"} and all(m["moved_m"] <= FU.MOVE_MAX_M for m in got.values())
    assert got["f_L0_002"]["footprint"]["center"] == [1.7, 1.75]
    assert got["f_L0_003"]["footprint"]["center"] == [1.15, 1.75]
    assert "desk f_L0_002 stood in front of" in got["f_L0_002"]["reason"]
    assert "moves with desk f_L0_002 (one unit)" in got["f_L0_003"]["reason"]
    # the architect carries it out: both moved, drawn values kept, adjusted_by_ai by the architect
    qs = RR.furniture_rules(AA.Plan(b), [])
    point = next(a for a in next(q for q in qs if q["id"] == "F4")["answers"] if a["element"] == "f_L0_001")
    assert point["open"] and point["default"] == "clear_front"
    done = AA.apply_answers(b, {k: v for k, v in AR.defaults_of({"questions": qs}, {}).items()
                                if k == "F4:f_L0_001"})
    assert done and done[0]["ok"]
    pieces = _by_id(b)
    for fid in ("f_L0_002", "f_L0_003"):
        assert pieces[fid]["adjusted_by_ai"]["by"] == "architect"
        assert pieces[fid]["drawn_footprint"]["center"] != pieces[fid]["footprint"]["center"]
    assert pieces["f_L0_001"]["footprint"]["center"] == [1.0, 0.3] and not FU.blocked_fronts(b)


def test_a_move_that_covers_a_window_or_takes_a_place_nobody_has_is_refused():
    # a window east of the wardrobe on its wall: the 0.40 m slide would stand the 2 m wardrobe before it; the desk
    # gives way instead (no bed here)
    b = room_building(3.018, 4.656, "bedroom", furniture=[WARDROBE, DESK, CHAIR], doors=(DOOR,),
                      windows=(("win1", "s", 2.4, 0.8),))
    fix = _fix(b)
    assert fix["mover"] == "f_L0_002" and {m["id"] for m in fix["moves"]} == {"f_L0_002", "f_L0_003"}
    # a bookshelf beside the wardrobe and the bed behind the desk: no move passes; the architect asks (keep only)
    b = _bedroom(("bookshelf", (2.10, 0.20), 180.0, (0.8, 0.4)))
    assert _fix(b) is None
    point = next(a for a in next(q for q in RR.furniture_rules(AA.Plan(b), []) if q["id"] == "F4")["answers"]
                 if a["element"] == "f_L0_001")
    assert point["open"] and "default" not in point and [o["id"] for o in point["options"]] == ["keep"]


def test_fixed_equipment_never_gives_way():
    # a tall cabinet in a niche (wall to wall), a toilet 0.20 m before its doors: the toilet stays where it is drawn
    b = room_building(1.2, 2.4, "bathroom", furniture=[("tall_cabinet", (0.6, 0.2), 180.0, (1.2, 0.4)),
                                                       ("toilet", (0.6, 0.95), 180.0, (0.4, 0.7))])
    assert not FU.movable(_by_id(b)["f_L0_002"], b["furniture"])
    fix = _fix(b)
    assert fix is None or all(m["id"] != "f_L0_002" for m in fix["moves"])


def test_a_front_that_opens_and_a_piece_in_a_run_are_left_alone():
    b = room_building(3.0, 3.0, "bedroom", furniture=[("wardrobe", (1.5, 0.3), 180.0, (1.2, 0.6))])
    assert _fix(b) is None
    k = room_building(3.0, 1.5, "kitchen", furniture=[("kitchen_counter", (1.5, 1.2), 0.0, (3.0, 0.6)),
                                                      ("stove", (1.5, 1.2), 0.0, (0.6, 0.6)),
                                                      ("tall_cabinet", (1.5, 0.3), 180.0, (1.0, 0.6))])
    assert _fix(k, "f_L0_002") is None                       # the run's front is its aisle (G8)


# --------------------------------------------------------------------------
# real04 (the building JSON of run 20261029-201533-full, the two bedrooms)
# --------------------------------------------------------------------------

def _real04() -> dict:
    return json.loads(REAL04.read_text(encoding="utf-8"))


def test_real04_the_wardrobes_doors_open_after_the_architects_default():
    b = _real04()
    got = {r["piece"]: r["problem"] for r in FU.blocked_fronts(b)}
    assert set(got) == {"f_L0_009", "f_L0_011"}
    assert got["f_L0_009"]["blockers"] == ["f_L0_029"] and got["f_L0_011"]["blockers"] == ["f_L0_028"]
    assert all(p["severity"] == "critical" and abs(p["free_m"] - 0.168) < 0.005 for p in got.values())
    # F4 now asks what M19 reports (one measure for one fault), with the safe default
    qs = RR.furniture_rules(AA.Plan(b), [])
    f4 = {a["element"]: a for a in next(q for q in qs if q["id"] == "F4")["answers"]}
    for fid in ("f_L0_009", "f_L0_011"):
        assert f4[fid]["open"] and f4[fid]["default"] == "clear_front" and "cannot open" in f4[fid]["found"]
    before = copy.deepcopy(_by_id(b))
    answers = {k: v for k, v in AR.defaults_of({"questions": qs}, {}).items() if k.startswith("F4:")}
    assert set(answers) == {"F4:f_L0_009", "F4:f_L0_011"} and all(a["by"] == "architect" for a in answers.values())
    done = AA.apply_answers(b, answers)
    assert all(r["ok"] for r in done)
    after = _by_id(b)
    for fid, sign in (("f_L0_009", 1.0), ("f_L0_011", -1.0)):
        w, w0 = after[fid], before[fid]
        dx = w["footprint"]["center"][0] - w0["footprint"]["center"][0]
        assert abs(dx - sign * 0.40) < 1e-6 and w["footprint"]["center"][1] == w0["footprint"]["center"][1]
        assert w["front_deg"] == w0["front_deg"] and w["drawn_footprint"] == w0["footprint"]
        assert w["drawn_front_deg"] == w0["front_deg"]
        assert w["adjusted_by_ai"]["by"] == "architect" and w["adjusted_by_ai"]["answer_key"] == f"F4:{fid}"
        assert "0.17 m free" in w["adjusted_by_ai"]["reason"] and "along its wall" in w["adjusted_by_ai"]["reason"]
    for fid in ("f_L0_028", "f_L0_029", "f_L0_036", "f_L0_037", "f_L0_021", "f_L0_022"):
        assert after[fid]["footprint"] == before[fid]["footprint"]          # the drawn desks, chairs, beds stay
    # the model review and Argus find nothing left; every other F4 / F5 answer of the two rooms passes
    assert not FU.blocked_fronts(b) and not LS.blocked_fronts(b)
    assert not [f for f in MR.review(b)["findings"] if f["check"] == "M19" and f["metrics"].get("rule") == "access"]
    qs2 = RR.furniture_rules(AA.Plan(b), [])
    for q in qs2:
        if q["id"] in ("F1", "F2", "F4", "F5"):
            assert not [a for a in q["answers"] if a.get("open")], q["id"]


# --------------------------------------------------------------------------
# Unchanged: the washer's turn stays the default; registration
# --------------------------------------------------------------------------

def test_the_washer_keeps_free_front_with_clear_front_as_the_next_safe_fix():
    b = room_building(2.40, 2.85, "bathroom", furniture=[("bathtub", (1.625, 2.475), 0.0, (1.55, 0.75)),
                                                         ("toilet", (2.045, 0.93), 270.0, (0.445, 0.705)),
                                                         ("washing_machine", (2.10, 0.30), 180.0, (0.6, 0.6))],
                      doors=(("d1", "w", 0.43, 0.75, True),))
    qs = RR.furniture_rules(AA.Plan(b), [])
    point = next(a for a in next(q for q in qs if q["id"] == "F4")["answers"] if a["element"] == "f_L0_003")
    assert point["default"] == "free_front" and "clear_front" in point["fallback"]
    assert AR.chain_of(point) == ["free_front", "clear_front"]


def test_clear_front_is_registered_everywhere():
    assert "clear_front" in AA.ACTIONS and "clear_front" in AAI.LOOK_ACTIONS["piece"]
    assert "clear_front" in ARG.FIX_ARCH and "clear_front" in MR.FIX_FRONT
    assert set(schemas.FIXED_TYPES) <= set(FU.FIXED_TYPES)
    assert FU.WINDOW_REACH_M == 0.25 and FU.DEFAULT_HEIGHT_M == 0.8 and FU.WALK_M == 0.60
    assert set(FU.STORAGE_OPEN_M) <= set(FU.DOOR_FRONTED)
