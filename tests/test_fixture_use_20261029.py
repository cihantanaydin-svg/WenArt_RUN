"""29 Oct 2026 (the user's review of real06 run 20261028-154514-full): fixtures you can use
(``wenart.furniture.fixture_use``; CPU only, synthetic rooms copied from real06).

- UL92 "This washing machine would not open": the drawn washer in the corner below the toilet had no front; the agent
  turned it from the wall onto the toilet 0.11 m away and every check passed. Now: the door's access zone is measured
  (plausibility F6, critical when the door cannot open), drawn fixed equipment turns for a blocked door and only to a
  free front (edit_ops), the reading and the architect (F4 free_front) turn it to its free side, the model review M19
  and Argus U16 find it in a built scene.
- UL95 "this sink not making sense there": a basin right under a 0.90 m window sill. Now: moved at most 0.5 m to a solid
  wall (reading, architect H2 clear_basin), else the window over it becomes a bathroom window (H2 basin_sill, only when
  the documents do not give its heights), M19 and Argus U10 find it.
- UL96 "There is a gap between wall and water faucet not looking good": a sink unit 0.08 m off its wall. Now: snapped
  back onto the wall with what is built into it (reading), M22 and Argus U20 find it.
"""
from __future__ import annotations

import copy

from test_decor_m8 import RID, room_building
from wenart.agent import causes as CS
from wenart.agent import loop as LP
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.blender import build as BLD
from wenart.blender import model_review as MR
from wenart.furniture import edit_ops as EO
from wenart.furniture import fixture_use as FU
from wenart.furniture import groups as GR
from wenart.furniture import placer
from wenart.furniture import plausibility as PL
from wenart.furniture import schemas
from wenart.ingest.generic import reading as RD
from wenart.ingest.pipeline import ProjectBuild

# real06's first-floor bathroom (r_L1_banyo) moved to the origin: 2.40 x 2.85 m, the bath on the north wall, the toilet
# on the east wall, the washer in the south-east corner below it, the door in the west wall
W, D = 2.40, 2.85
BATH = ("bathtub", (1.625, 2.475), 0.0, (1.55, 0.75))
TOILET = ("toilet", (2.045, 0.93), 270.0, (0.445, 0.705))           # front 180: into the room
WASHER = ("washing_machine", (2.10, 0.30), 180.0, (0.6, 0.6))        # front 90: the agent's turn, onto the toilet
DOOR = ("d1", "w", 0.43, 0.75, True)


def _bathroom(washer=WASHER, basin=None, windows=()) -> dict:
    pieces = [BATH, TOILET, washer] + ([basin] if basin else [])
    return room_building(W, D, "bathroom", furniture=pieces, doors=(DOOR,), windows=windows)


def _piece(b: dict, ftype: str) -> dict:
    return next(f for f in b["furniture"] if f["type"] == ftype)


def _room(b: dict) -> list:
    return b["rooms"][0]["polygon"]


# --------------------------------------------------------------------------
# UL92: the washer's door
# --------------------------------------------------------------------------

def test_the_washer_facing_the_toilet_cannot_open_and_turns_to_its_free_side():
    b = _bathroom()
    washer, toilet = _piece(b, "washing_machine"), _piece(b, "toilet")
    prob = FU.piece_access(washer, _room(b), b["furniture"])
    assert prob["severity"] == "critical" and prob["blockers"] == [toilet["id"]] and abs(prob["free_m"] - 0.11) < 0.01
    fix = FU.free_front(washer, _room(b), b["furniture"])
    # turned in place: its back on the east wall, its door into the room (west); never onto the toilet or the wall
    assert fix["how"] == "turned" and fix["front_deg"] == 180.0 and fix["moved_m"] == 0.0
    assert fix["footprint"]["center"] == washer["footprint"]["center"] and "reading error" in fix["reason"]
    turned = dict(washer, footprint=fix["footprint"], front_deg=fix["front_deg"])
    assert FU.piece_access(turned, _room(b), b["furniture"]) is None
    # a free front is left alone; a piece of a kitchen run is the run's (its aisle is G8's)
    assert FU.free_front(turned, _room(b), b["furniture"]) is None


def test_the_score_finds_the_blocked_door_and_the_validator_refuses_the_agents_turn():
    b = _bathroom()
    washer = _piece(b, "washing_machine")
    got = [v for v in PL.score_room(b, RID)["violations"] if v["target"] == washer["id"] and v["check"] == "F6"]
    assert got and got[0]["severity"] == "critical" and got[0]["metrics"]["part"] == "access"
    assert "cannot open" in got[0]["message"]
    # the drawn washer as the reading left it: no front, the builder's -Y into the south wall (F4, not F6 twice)
    drawn = copy.deepcopy(b)
    w = _piece(drawn, "washing_machine")
    w["footprint"]["rotation_deg"], w["front_deg"] = 0.0, None
    checks = {v["check"] for v in PL.score_room(drawn, RID)["violations"] if v["target"] == w["id"]}
    assert "F4" in checks and "F6" not in checks
    # the agent's edit of run 154514 (front 90: onto the toilet) is refused; the free front (180) is accepted
    edit = {"op": "rotate_piece", "piece_id": w["id"], "reason": "t", "round": 1, "log_seq": 1, "model": "t"}
    out = EO.apply_edit(drawn, dict(edit, front_deg=90))
    assert not out["accepted"] and "blocked" in out["message"]
    assert EO.apply_edit(drawn, dict(edit, front_deg=180))["accepted"]
    # on the final building the blocked door is a clear error: drawn fixed equipment may turn for it
    assert EO.allowed_edits(b, washer["id"])["rotate_piece"]["allowed"]
    assert EO.apply_edit(b, dict(edit, piece_id=washer["id"], front_deg=180))["accepted"]


def test_a_tight_front_that_opens_is_reported_not_moved():
    """0.55 m in front of a washer (the synthetic plans' bathrooms): its door opens, loading is tight: the score's
    F6 major, no code move (no reading error)."""
    b = _bathroom(washer=("washing_machine", (2.10, 0.30), 270.0, (0.6, 0.6)))
    w = _piece(b, "washing_machine")
    b["furniture"].append(dict(copy.deepcopy(_piece(b, "toilet")), id="f_box", type="tall_cabinet", front_deg=0.0,
                               footprint={"center": [1.05, 0.30], "size": [0.6, 0.4], "rotation_deg": 90.0}))
    prob = FU.piece_access(w, _room(b), b["furniture"])
    assert prob["severity"] == "major" and prob["blockers"] == ["f_box"] and abs(prob["free_m"] - 0.55) < 0.01
    assert FU.free_front(w, _room(b), b["furniture"]) is None
    f6 = [v for v in PL.score_room(b, RID)["violations"] if v["check"] == "F6" and v["target"] == w["id"]]
    assert f6 and f6[0]["severity"] == "major"


def test_a_new_placement_in_front_of_a_door_is_refused():
    """An added piece standing in front of a free washer door makes the room worse (F6 critical): refused (a drawn
    washer in a hall, its back on the east wall, real03's utility halls)."""
    b = room_building(3.0, 3.0, "hall", furniture=[("washing_machine", (2.68, 0.40), 270.0, (0.6, 0.6))],
                      doors=(("d1", "w", 1.5, 0.8, True),))
    assert FU.piece_access(b["furniture"][0], _room(b), b["furniture"]) is None
    out = EO.apply_edit(b, {"op": "add_piece", "room_id": RID, "type": "shoe_cabinet", "center": [2.05, 0.40],
                            "front_deg": 180.0, "reason": "t"})
    assert not out["accepted"] and "F6 f_L0_001" in out["message"] and "cannot open" in out["message"]


def test_the_reading_turns_a_drawn_washer_whose_front_is_blocked():
    b = _bathroom()
    w = _piece(b, "washing_machine")
    w["footprint"]["rotation_deg"], w["front_deg"] = 0.0, None        # as read: no front
    build = ProjectBuild(b)
    got = RD.fixture_use_fixes(build)
    assert w["id"] in got["fronts"]
    assert w["front_deg"] == 180.0 and w["drawn_front_deg"] is None
    assert w["drawn_footprint"]["rotation_deg"] == 0.0 and w["adjusted_by_ai"]["by"] == "code"
    assert w["adjusted_by_ai"]["rule"] == "free_front" and "reading error" in w["adjusted_by_ai"]["reason"]
    assert any(e.get("rule") == RD.USE_RULE for e in w["evidence"])
    assert FU.piece_access(w, _room(b), b["furniture"]) is None


def test_the_architect_turns_a_blocked_door_by_default():
    b = _bathroom()
    w = _piece(b, "washing_machine")
    qs = RR.furniture_rules(AA.Plan(b), [])
    f4 = next(q for q in qs if q["id"] == "F4")
    point = next(a for a in f4["answers"] if a["element"] == w["id"])
    assert point["open"] and point["default"] == "free_front" and "cannot open" in point["found"]
    answers = AR.defaults_of({"questions": qs}, {})
    done = AA.apply_answers(b, {k: v for k, v in answers.items() if k == f"F4:{w['id']}"})
    assert done[0]["ok"] and w["front_deg"] == 180.0 and w["adjusted_by_ai"]["by"] == "architect"
    assert w["drawn_front_deg"] == 90.0


def test_the_model_review_and_argus_find_a_door_that_cannot_open():
    b = _bathroom()
    w = _piece(b, "washing_machine")
    rec = MR.review(b)
    m19 = [f for f in rec["findings"] if f["check"] == "M19"]
    assert m19 and m19[0]["target"] == w["id"] and m19[0]["severity"] == "critical"
    assert m19[0]["metrics"]["rule"] == "access" and rec["checks"]["M19"]["status"] == "ok"
    u16 = LS.blocked_fronts(b)
    assert u16 and u16[0]["check"] == "U16" and u16[0]["evidence"]["lesson"] == "UL92"
    # after the turn nothing is left
    w["footprint"]["rotation_deg"], w["front_deg"] = 270.0, 180.0
    assert not [f for f in MR.review(b)["findings"] if f["check"] == "M19"] and not LS.blocked_fronts(b)


def test_storage_whose_doors_cannot_open_is_found_in_the_built_scene():
    # a wardrobe on the north wall and a dresser 0.10 m in front of it, its back to the wardrobe's doors
    b = room_building(4.0, 3.0, "bedroom", furniture=[("wardrobe", (2.0, 2.7), 0.0, (1.2, 0.6)),
                                                      ("dresser", (2.0, 2.05), 0.0, (1.0, 0.5))])
    got = FU.blocked_fronts(b)
    assert [r["piece"] for r in got] == ["f_L0_001"] and got[0]["problem"]["severity"] == "critical"
    assert got[0]["problem"]["blockers"] == ["f_L0_002"]
    # turned to face each other, both cannot open
    b["furniture"][1]["footprint"]["rotation_deg"], b["furniture"][1]["front_deg"] = 180.0, 90.0
    assert [r["piece"] for r in FU.blocked_fronts(b)] == ["f_L0_001", "f_L0_002"]


def test_a_cooker_in_a_counter_run_is_reported_only_when_its_oven_door_cannot_open():
    """A kitchen run's front is its aisle (G8, soft in a small kitchen): M19 and the score leave a narrow aisle to G8
    and report only an oven door that cannot open at all."""
    def kitchen(cabinet_depth: float) -> dict:
        return room_building(3.0, 1.5, "kitchen", furniture=[
            ("kitchen_counter", (1.5, 1.2), 0.0, (3.0, 0.6)), ("stove", (1.5, 1.2), 0.0, (0.6, 0.6)),
            ("tall_cabinet", (1.5, cabinet_depth / 2.0), 180.0, (1.0, cabinet_depth))])
    narrow = kitchen(0.35)                                  # 0.55 m in front of the oven: under its use depth only
    assert FU.blocked_fronts(narrow) == []
    assert not [v for v in PL.score_room(narrow, RID)["violations"] if v["check"] == "F6"]
    shut = kitchen(0.60)                                    # 0.30 m: neither the oven door nor the cabinet's opens
    got = FU.blocked_fronts(shut)
    assert [r["piece"] for r in got] == ["f_L0_002", "f_L0_003"]
    assert all(r["problem"]["severity"] == "critical" for r in got)


# --------------------------------------------------------------------------
# UL96: a back a drawing gap off its wall
# --------------------------------------------------------------------------

def _kitchen(gap: float = 0.08, behind=None) -> dict:
    sink = ("sink_kitchen", (gap + 0.225, 1.5), 90.0, (1.2, 0.45))   # front 0 (east), its back towards the west wall
    pieces = [sink] + ([behind] if behind else [])
    return room_building(3.0, 3.0, "kitchen", furniture=pieces)


def test_a_sink_unit_off_its_wall_snaps_back_onto_it():
    b = _kitchen()
    sink = _piece(b, "sink_kitchen")
    gap = FU.back_gap(sink, _room(b))
    assert abs(gap["gap_m"] - 0.08) < 1e-3 and gap["normal"] == [-1.0, 0.0]
    snap = FU.snap_back(sink, _room(b), b["furniture"])
    new = snap["footprints"][sink["id"]]
    assert abs(new["center"][0] - (FU.SNAP_GAP_M + 0.225)) < 1e-3 and new["center"][1] == 1.5
    assert MR.backs_on_walls(b)[0][0]["check"] == "M22" and LS.back_gaps(b)[0]["evidence"]["lesson"] == "UL96"
    # the reading carries it out (drawn footprint kept, labelled by code)
    build = ProjectBuild(b)
    got = RD.fixture_use_fixes(build)
    assert got["backs"] == [sink["id"]] and sink["drawn_footprint"]["center"][0] == 0.305
    assert sink["adjusted_by_ai"]["rule"] == "back_gap" and not MR.backs_on_walls(b)[0] and not LS.back_gaps(b)


def test_a_back_gap_is_only_a_drawing_gap():
    assert FU.back_gap(_piece(_kitchen(0.02), "sink_kitchen"), _room(_kitchen(0.02))) is None     # on the wall
    assert FU.back_gap(_piece(_kitchen(0.05), "sink_kitchen"), _room(_kitchen(0.05))) is None     # F3's 5 cm
    assert FU.back_gap(_piece(_kitchen(0.30), "sink_kitchen"), _room(_kitchen(0.30))) is None     # off the wall
    # never into another piece: a radiator-like box behind it stays, so the sink stays
    b = _kitchen(0.12, behind=("tall_cabinet", (0.05, 1.5), 90.0, (0.4, 0.08)))
    assert FU.snap_back(_piece(b, "sink_kitchen"), _room(b), b["furniture"]) is None


def test_a_counter_moves_with_the_sink_built_into_it():
    b = room_building(3.0, 3.0, "kitchen", furniture=[("kitchen_counter", (0.305, 1.5), 90.0, (2.4, 0.6)),
                                                     ("sink_kitchen", (0.305, 1.5), 90.0, (0.8, 0.6))])
    counter, sink = b["furniture"]
    for f in (counter, sink):
        f["footprint"]["center"][0] = 0.08 + 0.3
    assert FU.snap_back(sink, _room(b), b["furniture"]) is None               # built in: it moves with its counter
    snap = FU.snap_back(counter, _room(b), b["furniture"])
    assert sorted(snap["unit"]) == sorted([counter["id"], sink["id"]])
    assert snap["footprints"][sink["id"]]["center"][0] == snap["footprints"][counter["id"]]["center"][0]


# --------------------------------------------------------------------------
# UL95: a basin under a window
# --------------------------------------------------------------------------

BASIN = ("washbasin", (0.45, 2.65), 0.0, (0.5, 0.4))                  # in the corner under the north window


def test_a_basin_under_a_low_window_has_no_mirror_wall():
    b = _bathroom(basin=BASIN, windows=(("win1", "n", 0.45, 1.1),))
    basin = _piece(b, "washbasin")
    walls = {w["id"]: w for w in b["walls"]}
    got = FU.basin_window(basin, b["openings"], walls)
    assert got["window"] == "win1" and got["sill_m"] == 0.9 and got["share"] == 1.0
    # no solid wall within 0.5 m (the bath fills the rest of its wall): the architect asks, raising the sill by default
    assert FU.clear_basin(basin, _room(b), b["furniture"], b["openings"], walls) is None
    m19 = [f for f in MR.review(b)["findings"] if f["check"] == "M19" and f["target"] == basin["id"]]
    assert m19 and m19[0]["metrics"]["rule"] == "basin_window"
    assert CS.cause_of(m19[0], b) == "opening_sense" and CS.REPORT_TO["opening_sense"] == "architect"
    u10 = [f for f in LS.basins_without_mirrors(b) if f["target"] == basin["id"]]
    assert u10 and u10[0]["evidence"]["lesson"] == "UL95"
    win = next(o for o in b["openings"] if o["id"] == "win1")

    def h2_point():
        qs = RR.furniture_rules(AA.Plan(b), [])
        return qs, next(a for q in qs if q["id"] == "H2" for a in q["answers"] if a["element"] == basin["id"])

    # a sill the documents give: no safe default, the AI architect and the user decide (a farther move offered)
    _qs, h2 = h2_point()
    assert h2["open"] and "default" not in h2
    assert {o["id"] for o in h2["options"]} == {"clear_basin", "keep"}
    assert all(o["params"].get("max_move_m", 0) > FU.MOVE_MAX_M for o in h2["options"] if o["id"] == "clear_basin")
    # real06: a bare gap read as a window at the floor's sill (assumed): the default raises it over the basin
    win["assumed"] = ["sill_height", "height"]
    qs, h2 = h2_point()
    assert h2["default"] == "basin_sill"
    answers = {k: v for k, v in AR.defaults_of({"questions": qs}, {}).items() if k.startswith("H2:")}
    done = AA.apply_answers(b, answers)
    assert done[0]["ok"] and win["sill_height"] == FU.BASIN_SILL_M and win["drawn_sill_height"] == 0.9
    assert FU.basin_window(basin, b["openings"], walls) is None


def test_a_basin_moves_along_its_wall_to_a_solid_stretch():
    b = _bathroom(basin=BASIN, windows=(("win1", "n", 0.25, 0.5),))
    b["furniture"] = [f for f in b["furniture"] if f["type"] != "bathtub"]
    basin = _piece(b, "washbasin")
    walls = {w["id"]: w for w in b["walls"]}
    fix = FU.clear_basin(basin, _room(b), b["furniture"], b["openings"], walls)
    assert fix is not None and fix["moved_m"] <= FU.MOVE_MAX_M and fix["front_deg"] == 270.0
    assert fix["footprint"]["center"][0] > basin["footprint"]["center"][0]
    build = ProjectBuild(b)
    got = RD.fixture_use_fixes(build)
    assert got["basins"] == [basin["id"]] and basin["adjusted_by_ai"]["rule"] == "basin_window"
    assert FU.basin_window(basin, b["openings"], walls) is None


def test_a_far_basin_move_needs_the_users_ok():
    b = _bathroom(basin=BASIN, windows=(("win1", "n", 0.45, 1.1),))
    basin = _piece(b, "washbasin")
    ans = {"option": "clear_basin", "params": {"piece_id": basin["id"], "max_move_m": 1.2}}
    ai = AA.apply_answers(copy.deepcopy(b), {f"H2:{basin['id']}": dict(ans, by="ai")})
    assert not ai[0]["ok"] and "user's OK" in ai[0]["change"]
    user = AA.apply_answers(b, {f"H2:{basin['id']}": dict(ans, by="user")})
    assert user[0]["ok"] and basin["adjusted_by_ai"]["answer_by"] == "user"


# --------------------------------------------------------------------------
# Registration: the ids, kinds, causes, the shared constants
# --------------------------------------------------------------------------

def test_the_new_checks_are_registered_everywhere():
    assert {"M19", "M22"} <= set(MR.CHECKS) and {"M19", "M22"} <= LP.NOT_REMEASURED
    assert K.CHECK_KIND["M19"] == "no_sense" and K.CHECK_KIND["M22"] == "misread"
    assert K.kind_of({"check": "U16"}) == "no_sense" and K.kind_of({"check": "U20"}) == "misread"
    assert CS.CHECK_CAUSE["M19"] == "orientation" and CS.CHECK_CAUSE["M22"] == "off_wall"
    assert "rotate_piece" in CS.CAUSE_TOOLS["orientation"] and "move_piece" in CS.CAUSE_TOOLS["off_wall"]
    assert LS.CHECK_LESSONS["U16"] == ("UL92",) and LS.CHECK_LESSONS["U20"] == ("UL96",)
    assert "UL95" in LS.CHECK_LESSONS["U10"]
    assert {"U16", "U20"} <= {c for c, _fn in LS.BUILDING_CHECKS}
    assert {"free_front", "clear_basin", "basin_sill"} <= set(AA.ACTIONS)
    assert any(r["id"] == "H2" for r in RR.RULES) and "H2" in AR.ORDER
    assert "wenart/furniture/fixture_use.py" in BLD.FINGERPRINT_CODE


def test_the_shared_constants_agree():
    assert FU.BACK_WALL_M == schemas.BACK_WALL_M and FU.BACK_SHARE == PL.BACK_SHARE
    assert FU.PARALLEL_DEG == schemas.BACK_PARALLEL_DEG and FU.FRONT_WALL_MIN_M == schemas.FRONT_WALL_MIN_M
    assert abs(FU.SNAP_GAP_M - placer.SNAP_GAP_M) < 1e-9 and FU.MOVE_MAX_M == 0.5
    assert FU.FIXTURE_FRONT_M == GR.rule_min("fixture_front")
    wall_types = {t for t, r in schemas.ORIENTATION_RULES.items() if r["back"] == "wall"}
    assert set(FU.BACK_TYPES) == wall_types
    assert set(FU.ACCESS_M) & set(schemas.ORIENTATION_RULES) <= wall_types
