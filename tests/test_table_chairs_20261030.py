"""UL178 (30 Oct 2026): "Table seems to be going through the chairs" (real04 run 20261030-112241-full, the top-floor
play room: the drawing's cafe set, a round table 0.79 m across with two chairs on its diagonal, was built as a square
turned-leg library table, "Ravenna Home Traditional Dining Table", after an agent swap; the square table's corners and
legs stood in both chairs). Three general rules: a round drawn table takes a round model or our round table on a
pedestal (``fit.round_misfit``, also for a pinned model); a seat tucked under a legged table keeps out of its corner
legs (``clashes.leg_zones``, the build's clash rule F5 pulls it out); the score's F9 names a seat in the legs. Pure
tests; real04 is only the test case."""
from __future__ import annotations

import copy

import _m11_room as M
from test_furniture_fit_v2 import FakeCatalog, model
from wenart.blender import clashes as CL
from wenart.blender import parametric as P
from wenart.furniture import fit as F
from wenart.furniture import plausibility as PL

SQUARE_TITLE = "Amazon Brand - Ravenna Home Traditional Dining Table 29\"H, Gray and Rustic Honey Pine"
ROUND_TITLE = "Amazon Brand - Rivet Noah Round Modern Ash Dining Table"


def _piece(pid, ftype, center, size, rotation=0.0, **extra):
    item = {"id": pid, "level_id": "L1", "room_id": "r_L1_oyun", "type": ftype, "source": "from_documents",
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}}
    item.update(extra)
    return item


def _library(title):
    return {"method": "library", "asset_id": "abo_x", "title": title, "name": title, "bbox_m": [0.78, 0.78, 0.77]}


def _cafe_set(asset=None):
    """real04's play room: the drawn round table (a circle, read with a meaningless 78.6 deg turn) and the two chairs
    drawn on its diagonal, each over a corner of the table's square box."""
    table = _piece("f_L1_005", "table_dining", (2.8611, 2.3711), (0.7842, 0.7842), 78.586,
                   circle_fit={"share": 1.0, "radius": 0.3949}, asset=asset)
    east = _piece("f_L1_006", "chair", (3.1999, 2.0429), (0.4246, 0.45), 270.0, front_deg=180.0)
    west = _piece("f_L1_007", "chair", (2.507, 2.6751), (0.4345, 0.45), 90.0, front_deg=0.0)
    room = {"id": "r_L1_oyun", "level_id": "L1", "polygon": [[0.0, 0.0], [8.0, 0.0], [8.0, 6.0], [0.0, 6.0]]}
    return {"rooms": [room], "walls": [], "openings": [], "furniture": [table, east, west], "decor": []}


def test_legs_stand_at_the_corners_of_a_square_table_and_nowhere_on_a_round_one():
    square = _piece("t", "table_dining", (0.0, 0.0), (1.6, 0.9))
    zones = CL.leg_zones(square)
    assert len(zones) == 4 and all(abs(CL._area(z) - CL.LEG_ZONE_M ** 2) < 1e-9 for z in zones)
    corners = sorted((round(x, 3), round(y, 3)) for z in zones for x, y in z if abs(abs(x) - 0.8) < 1e-9
                     and abs(abs(y) - 0.45) < 1e-9)
    assert corners == [(-0.8, -0.45), (-0.8, 0.45), (0.8, -0.45), (0.8, 0.45)]
    drawn_round = _piece("t", "table_dining", (0.0, 0.0), (0.8, 0.8), circle_fit={"share": 0.97})
    assert P.piece_is_round(drawn_round) and CL.leg_zones(drawn_round) == []                 # our pedestal table
    assert CL.leg_zones(dict(drawn_round, asset=_library(ROUND_TITLE))) == []                # a round model
    assert len(CL.leg_zones(dict(drawn_round, asset=_library(SQUARE_TITLE)))) == 4          # a square model: legs
    assert CL.leg_zones(_piece("t", "table_coffee", (0, 0), (1.2, 0.6))) == []               # not a legged type


def test_a_seat_is_tucked_between_the_legs_never_into_them():
    table = _piece("t", "table_dining", (0.0, 0.0), (1.6, 0.9))
    middle = _piece("c1", "chair", (0.0, -0.525), (0.45, 0.45), 0.0)                # centred on the long side
    corner = _piece("c2", "chair", (0.72, -0.525), (0.45, 0.45), 0.0)               # its side over the table's corner
    for chair, ok in ((middle, True), (corner, False)):
        sc, st = CL.shape(chair), CL.shape(table)
        depth = CL.shape_depth(sc, st)
        assert abs(depth - 0.15) < 1e-9                                              # tucked 0.15 m both
        assert (CL.by_design(chair, table, sc, st, depth) is not None) is ok
        assert (CL.on_legs(sc, table) > CL.LEG_TOL_M) is not ok


def test_the_build_pulls_the_cafe_chairs_out_of_a_square_tables_legs():
    b = _cafe_set(asset=_library(SQUARE_TITLE))
    res = CL.resolve(b)
    moved = {x["id"]: x for x in res["fixed"]}
    assert sorted(moved) == ["f_L1_006", "f_L1_007"] and res["left"] == []
    table = b["furniture"][0]
    for chair in b["furniture"][1:]:
        assert CL.on_legs(CL.shape(chair), table) <= CL.LEG_TOL_M
        assert moved[chair["id"]]["distance_m"] <= CL.MAX_MOVE_M
        assert chair["drawn_footprint"]["center"] != chair["footprint"]["center"]
        assert "architect F5" in chair["adjusted_by_ai"]["reason"]
    # built round (a round model, or our pedestal table): the chairs stay tucked as drawn
    for asset in (_library(ROUND_TITLE), None):
        kept = _cafe_set(asset=asset)
        assert CL.resolve(kept)["fixed"] == []


def _tight_corner():
    """A 1.6 x 0.9 table in a room that leaves no leg-free place for the chair on its corner: a second chair beside
    it, the room's walls behind it and past the table's end."""
    table = _piece("t1", "table_dining", (0.0, 0.0), (1.6, 0.9))
    corner = _piece("c1", "chair", (0.72, -0.525), (0.45, 0.45), 0.0, front_deg=90.0)     # 0.15 m under, on a leg
    beside = _piece("c2", "chair", (0.2, -0.525), (0.45, 0.45), 0.0, front_deg=90.0)
    room = {"id": "r_L1_oyun", "level_id": "L1", "polygon": [[-1.0, -0.76], [1.0, -0.76], [1.0, 0.76], [-1.0, 0.76]]}
    return {"rooms": [room], "walls": [], "openings": [], "furniture": [table, corner, beside], "decor": []}


def test_a_seat_with_no_leg_free_place_stays_tucked_and_is_reported():
    from wenart.blender import architect_rules as AR

    b = _tight_corner()
    before = copy.deepcopy(b["furniture"])
    res = CL.resolve(b)
    assert res["fixed"] == [] and res["left"] == [] and b["furniture"] == before          # nothing moves blindly
    assert [(x["id"], x["other"]) for x in res["legs"]] == [("c1", "t1")] and res["legs"][0]["depth_m"] > 0.05
    f5 = AR.clash_rule(b, res)[0]
    found = [a for a in f5["answers"] if a["element"] == "c1"]
    assert f5["status"] == "open" and found[0]["open"] and "corner leg" in found[0]["found"]


def test_a_seat_moves_at_most_half_a_metre_from_its_drawn_place_in_all():
    chair = _piece("c1", "chair", (0.3, 0.0), (0.45, 0.45), drawn_footprint={"center": [0.0, 0.0]})
    assert abs(CL.from_drawn(chair) - 0.3) < 1e-9 and abs(CL.from_drawn(chair, 0.3, 0.0) - 0.6) < 1e-9
    assert abs(CL.from_drawn(chair, -0.3, 0.0)) < 1e-9
    assert abs(CL.from_drawn(_piece("c2", "chair", (1.0, 1.0), (0.45, 0.45)), 0.0, 0.4) - 0.4) < 1e-9


def test_a_round_drawn_table_takes_a_round_model_or_our_round_table():
    square = model("square", "table_dining", 0.78, 0.78, 0.75, title=SQUARE_TITLE)
    roundm = model("round", "table_dining", 0.80, 0.80, 0.75, title=ROUND_TITLE)
    piece = _piece("f_L1_005", "table_dining", (2.86, 2.37), (0.7842, 0.7842), 78.586,
                   circle_fit={"share": 1.0, "radius": 0.3949})
    fit = F.fit_piece(piece, FakeCatalog([square, roundm]))
    assert fit["method"] == "library" and fit["asset_id"] == "abo_round"
    assert any(x["id"] == "abo_square" and x.get("rule") == F.ROUND_TABLE_RULE for x in fit["excluded"])
    only = F.fit_piece(piece, FakeCatalog([square]))
    assert only["method"] == "parametric" and F.ROUND_TABLE_RULE in only["fallback_reason"]
    # a square drawn table keeps every model; a round model fits a round drawn coffee table too
    assert F.fit_piece(_piece("t", "table_dining", (0, 0), (0.78, 0.78)), FakeCatalog([square]))["method"] == "library"
    assert F.round_misfit(square, dict(piece, type="table_coffee")) is not None
    assert F.round_misfit(square, dict(piece, type="desk")) is None


def test_the_agents_pinned_square_model_is_refused_on_a_round_table():
    square = model("square", "table_dining", 0.78, 0.78, 0.75, title=SQUARE_TITLE)
    roundm = model("round", "table_dining", 0.80, 0.80, 0.75, title=ROUND_TITLE)
    piece = _piece("f_L1_005", "table_dining", (2.86, 2.37), (0.7842, 0.7842), 78.586,
                   circle_fit={"share": 1.0}, asset_pin="abo_square")
    fit = F.fit_piece(piece, FakeCatalog([square, roundm]))
    assert fit["asset_id"] == "abo_round" and F.ROUND_TABLE_RULE in fit["pin_refused"]
    assert F.room_rule_refusal(square, piece, "modern") is not None
    assert F.room_rule_refusal(roundm, piece, "modern") is None


def test_our_round_table_stands_on_a_pedestal():
    round_parts = P.build_parts("table_dining", 0.8, 0.8, 0.75, {"shape": "round"})
    roles = [p["role"] for p in round_parts]
    assert roles.count("leg") == 1 and "base" in roles and roles.count("top") == 1
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(round_parts)
    assert abs((x1 - x0) - 0.8) < 1e-6 and abs((y1 - y0) - 0.8) < 1e-6 and abs(z1 - 0.75) < 1e-6 and z0 >= -1e-9
    square_parts = P.build_parts("table_dining", 0.8, 0.8, 0.75, {})
    assert [p["role"] for p in square_parts].count("leg") == 4


def test_the_score_names_a_seat_in_the_tables_legs():
    table = M.fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), front=None)
    middle = M.fp("c1", "chair", (2.5, 1.55), (0.45, 0.45), rotation=0.0, front=90.0)
    corner = M.fp("c2", "chair", (3.22, 1.55), (0.45, 0.45), rotation=0.0, front=90.0)
    b = M.building(w=5.0, h=4.0, room_type="dining", furniture=[table, middle, corner])
    found = [v for v in PL.score_room(b, M.ROOM_ID)["violations"] if v["check"] == "F9"]
    assert [(v["target"], v["metrics"]["other"]) for v in found] == [("c2", "t1")]
    assert found[0]["metrics"]["cause"] == "table_legs" and "corner legs" in found[0]["message"]
    clear = copy.deepcopy(b)
    clear["furniture"] = [f for f in clear["furniture"] if f["id"] != "c2"]
    assert not [v for v in PL.score_room(clear, M.ROOM_ID)["violations"] if v["check"] == "F9"]
