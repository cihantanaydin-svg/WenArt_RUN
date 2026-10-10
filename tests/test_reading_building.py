"""Milestone 12 track R (docs/milestone12.md §4.1 D7): the reading step on the building (``reading.read_furniture``).

What: symbols leave the furniture (with a conflict when both AI passes typed one), columns and decor stay not built,
copies of one block drawing share a type, context typing (nightstands, dining chairs, a counter holding a sink, a
fridge closing the counter run, a vanity under a washbasin, two armchairs at a coffee table, a coffee table and a TV
unit facing a sofa), misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026: nearest product size with the back
kept on its wall; out of a wall or a door swing by at most 0.5 m; ``drawn_*`` kept, ``adjusted_by_ai``), inferred
fronts, open-kitchen zones and "never a box" (``build: false`` + ``needs_review``).
Why: before track R ``read_furniture`` did nothing: every rule below fails on the old code.
How: the hand-made rooms of ``tests/_m11_room.py`` in a real ``pipeline.ProjectBuild``; the core's items are stand-ins
that carry ``element_id`` and ``details`` only.
"""
import math
from types import SimpleNamespace

from shapely.geometry import Polygon

import _m11_room as M
from wenart.furniture import sizes
from wenart.ingest.generic import reading as RD
from wenart.ingest.pipeline import ProjectBuild


def _build(furniture, **kw):
    return ProjectBuild(M.building(furniture=furniture, **kw))


def _works(level_id="L0", report=None, **details):
    """One page work whose extraction holds core items (``element_id`` -> ``details``)."""
    items = [SimpleNamespace(element_id=pid, details=dict(det)) for pid, det in details.items()]
    ex = SimpleNamespace(furniture=items, report=dict(report or {}), level_id=level_id)
    return {"page": SimpleNamespace(extraction=ex)}


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def _rules(f):
    return [e.get("rule") for e in f["evidence"]]


def _fp(f):
    return RD.rect(f)


# --------------------------------------------------------------------------
# 1. Symbols, columns, decor, copies
# --------------------------------------------------------------------------

def test_symbols_move_to_the_building_symbols_and_the_drawing_outranks_the_ai():
    tag = M.fp("f1", "unknown", (2.0, 2.0), (0.5, 0.5), front=None)
    lamp = M.fp("f2", "floor_lamp", (3.0, 2.0), (0.5, 0.5), front=None, type_method="ai_two_pass")
    column = M.fp("f3", "unknown", (4.0, 3.0), (0.3, 0.5), front=None)
    bed = M.fp("f4", "bed_double", (2.5, 3.0), (1.6, 2.0), front=270.0)
    build = _build([tag, lamp, column, bed])
    works = _works(f1={"symbol": {"kind": "room_number", "reason": "circle 0.50 m across with the number '5'"}},
                   f2={"symbol": {"kind": "room_number", "reason": "circle 0.50 m across with the number '6'"},
                       "candidate_key": "sym_L0_007"},
                   f3={"not_furniture": {"as": "column", "reason": "drawn on the 'MYD - KOLON' layer(s)"}})
    RD.read_furniture(build, works)
    b = build.building
    assert [f["id"] for f in b["furniture"]] == ["f3", "f4"]
    syms = {s["former_piece_id"]: s for s in b["symbols"]}
    assert set(syms) == {"f1", "f2"} and {s["kind"] for s in syms.values()} == {"room_number"}
    assert syms["f2"]["crop"] == "recognition/crops/sym_L0_007_ctx.png"
    assert "the drawing outranks them" in syms["f2"]["reason"] and syms["f1"]["evidence"][-1]["rule"] == RD.SYMBOL_RULE
    assert [c["kind"] for c in build.raw_conflicts] == ["type_disagreement"]
    col = _piece(b, "f3")
    assert col["build"] is False and col["inferred_as"] == "column" and RD.SYMBOL_RULE in _rules(col)
    assert build.reading["symbols"] == {"room_number": 2, "column": 1}
    assert b["needs_review"] == []                       # a column is explained, not an untyped box


def test_an_untyped_copy_of_a_typed_block_drawing_takes_its_type():
    typed = M.fp("f1", "bathtub", (1.0, 3.6), (1.7, 0.75), front=270.0)
    copy = M.fp("f2", "unknown", (4.0, 3.6), (1.7, 0.75), front=None)
    build = _build([typed, copy], room_type="bathroom")
    RD.read_furniture(build, _works(f1={"copy_keys": ["1:abc"]}, f2={"copy_keys": ["1:abc"]}))
    f = _piece(build.building, "f2")
    assert f["type"] == "bathtub" and "same block entities as f1" in f["inferred_reason"]


# --------------------------------------------------------------------------
# 2. Context typing
# --------------------------------------------------------------------------

def test_small_squares_beside_a_beds_head_are_nightstands_facing_its_way():
    bed = M.fp("bed", "bed_double", (2.5, 3.0), (1.6, 2.0), front=270.0)
    left = M.fp("n1", "unknown", (1.45, 3.75), (0.45, 0.40), front=None)
    right = M.fp("n2", "unknown", (3.55, 3.75), (0.45, 0.40), front=None)
    build = _build([bed, left, right])
    RD.read_furniture(build, {})
    for pid in ("n1", "n2"):
        f = _piece(build.building, pid)
        assert f["type"] == "nightstand" and f["front_deg"] == 270.0 and RD.CONTEXT_RULE in _rules(f)
        assert f["inferred"] is True and "beside the head of bed" in f["inferred_reason"]


def test_seats_around_a_dining_table_are_chairs_facing_it():
    table = M.fp("t", "table_dining", (2.5, 2.0), (1.6, 0.9), front=None)
    south = M.fp("c1", "unknown", (2.0, 1.25), (0.45, 0.45), front=None)
    north = M.fp("c2", "unknown", (3.0, 2.75), (0.45, 0.45), front=None)
    build = _build([table, south, north], room_type="dining")
    RD.read_furniture(build, {})
    assert _piece(build.building, "c1")["type"] == "chair" and _piece(build.building, "c1")["front_deg"] == 90.0
    assert _piece(build.building, "c2")["type"] == "chair" and _piece(build.building, "c2")["front_deg"] == 270.0


def test_a_coffee_table_and_a_tv_unit_face_the_sofa():
    sofa = M.fp("s", "sofa", (2.5, 3.55), (2.2, 0.9), front=270.0)
    coffee = M.fp("ct", "unknown", (2.5, 2.4), (1.0, 0.6), front=None)
    tv = M.fp("tv", "unknown", (3.0, 0.225), (1.6, 0.45), front=None)
    build = _build([sofa, coffee, tv], room_type="living", door_x=0.6, window=None)
    RD.read_furniture(build, {})
    assert _piece(build.building, "ct")["type"] == "table_coffee"
    f = _piece(build.building, "tv")
    assert f["type"] == "tv_unit" and f["front_deg"] == 90.0 and "facing s" in f["inferred_reason"]


def test_two_equal_seats_on_opposite_sides_of_a_coffee_table_are_armchairs_facing_it():
    coffee = M.fp("ct", "table_coffee", (2.5, 2.0), (1.0, 0.6), front=None)
    west = M.fp("a1", "unknown", (1.6, 2.0), (0.8, 0.8), front=None)
    east = M.fp("a2", "unknown", (3.4, 2.0), (0.8, 0.8), front=None)
    build = _build([coffee, west, east], room_type="living", window=None)
    RD.read_furniture(build, {})
    assert (_piece(build.building, "a1")["type"], _piece(build.building, "a1")["front_deg"]) == ("armchair", 0.0)
    assert (_piece(build.building, "a2")["type"], _piece(build.building, "a2")["front_deg"]) == ("armchair", 180.0)


def test_a_strip_along_the_wall_holding_a_sink_is_the_counter_and_a_proud_box_beside_it_the_fridge():
    sink = M.fp("sk", "sink_kitchen", (1.4, 3.72), (0.8, 0.5), front=270.0)
    strip = M.fp("k", "unknown", (1.4, 3.7), (2.4, 0.6), front=None)
    box = M.fp("fr", "unknown", (2.95, 3.65), (0.7, 0.7), front=None)
    build = _build([sink, strip, box], room_type="kitchen", window=None)
    RD.read_furniture(build, {})
    k = _piece(build.building, "k")
    assert k["type"] == "kitchen_counter" and k["front_deg"] == 270.0 and "holding sk" in k["inferred_reason"]
    fr = _piece(build.building, "fr")
    assert fr["type"] == "fridge" and fr["front_deg"] == 270.0 and "proud" in fr["inferred_reason"]


def test_the_counter_under_a_washbasin_is_its_vanity_not_a_piece():
    basin = M.fp("wb", "washbasin", (1.0, 2.25), (0.6, 0.45), front=270.0)
    vanity = M.fp("v", "unknown", (1.1, 2.22), (1.2, 0.55), front=None)
    build = _build([basin, vanity], w=3.0, h=2.5, room_type="bathroom", window=None)
    RD.read_furniture(build, {})
    v = _piece(build.building, "v")
    assert v["build"] is False and v["inferred_as"] == "detail" and "vanity" in v["inferred_reason"]
    assert build.building["needs_review"] == []


# --------------------------------------------------------------------------
# 3. Misread fixed equipment
# --------------------------------------------------------------------------

def test_a_toilet_drawn_far_too_deep_gets_the_nearest_product_size_with_its_back_on_the_wall():
    wc = M.fp("wc", "toilet", (1.5, 1.95), (0.38, 1.10), front=270.0, height=None)
    build = _build([wc], w=3.0, h=2.5, room_type="bathroom", window=None)
    RD.read_furniture(build, _works(wc={"candidate_key": "sym_L0_004"}))
    f = _piece(build.building, "wc")
    w, d = f["footprint"]["size"]
    assert sizes.fits("toilet", (w, d), tolerance=0.0) and d < 1.0
    assert math.isclose(f["footprint"]["center"][1] + d / 2, 2.5, abs_tol=1e-6)        # back still on the wall
    assert f["drawn_footprint"]["size"] == [0.38, 1.10] and f["drawn_type"] == "toilet"
    assert f["drawn_front_deg"] == 270.0 and "drawn_height" in f
    assert "misread fixed equipment" in f["adjusted_by_ai"]["reason"] and RD.FIXED_RULE in _rules(f)
    assert f["adjusted_by_ai"]["crop"] == "recognition/crops/sym_L0_004_ctx.png"
    assert build.reading["fixed"] == ["wc"]


def test_a_washbasin_through_a_wall_moves_back_into_its_room():
    basin = M.fp("wb", "washbasin", (2.9, 1.2), (0.6, 0.45), rotation=90.0, front=180.0)
    build = _build([basin], w=3.0, h=2.5, room_type="bathroom", window=None)
    RD.read_furniture(build, {})
    f = _piece(build.building, "wb")
    room = Polygon(build.building["rooms"][0]["polygon"])
    assert _fp(f).difference(room.buffer(RD.THROUGH_WALL_M)).area < 1e-6
    moved = math.dist(f["footprint"]["center"], f["drawn_footprint"]["center"])
    assert 0 < moved <= RD.MOVE_MAX_M and "through a wall" in f["adjusted_by_ai"]["reason"]


def test_a_toilet_in_the_door_swing_moves_out_of_it():
    wc = M.fp("wc", "toilet", (1.6, 0.35), (0.38, 0.65), rotation=180.0, front=90.0)
    build = _build([wc], w=3.0, h=2.5, room_type="bathroom", window=None)
    room = build.building["rooms"][0]
    swing = RD.swing_polys(build.building, room)
    assert len(swing) == 1 and _fp(wc).intersection(swing[0]).area > RD.SWING_SHARE * _fp(wc).area
    RD.read_furniture(build, {})
    f = _piece(build.building, "wc")
    assert _fp(f).intersection(swing[0]).area <= RD.SWING_SHARE * _fp(f).area
    assert math.dist(f["footprint"]["center"], f["drawn_footprint"]["center"]) <= RD.MOVE_MAX_M
    assert "in a door swing" in f["adjusted_by_ai"]["reason"]


def test_a_piece_beside_the_door_frame_is_not_in_its_swing():
    wc = M.fp("wc", "toilet", (1.75, 0.35), (0.38, 0.65), rotation=180.0, front=90.0)
    build = _build([wc], w=3.0, h=2.5, room_type="bathroom", window=None)
    RD.read_furniture(build, {})
    assert "adjusted_by_ai" not in _piece(build.building, "wc")


# --------------------------------------------------------------------------
# 4. Fronts, kitchen zones, never a box
# --------------------------------------------------------------------------

def test_fronts_are_inferred_from_the_wall_a_drawn_piece_stands_on():
    wardrobe = M.fp("wr", "wardrobe", (0.3, 2.0), (1.8, 0.6), rotation=90.0, front=None)
    bed = M.fp("bed", "bed_double", (4.2, 3.0), (1.6, 2.0), front=None)       # in the north-east corner
    crib = M.fp("cr", "crib", (0.63, 0.33), (1.26, 0.66), front=None)          # in the south-west corner
    build = _build([wardrobe, bed, crib], door_x=2.5, window=None)
    RD.read_furniture(build, {})
    wr, bd, cr = (_piece(build.building, pid) for pid in ("wr", "bed", "cr"))
    assert wr["front_deg"] == 0.0 and RD.FRONT_RULE in _rules(wr) and wr["front_inferred"]
    assert bd["front_deg"] == 270.0                       # a bed's head (a short side) is on the wall
    assert cr["front_deg"] == 90.0                        # a crib's front is a long side (track B's size table)


def test_kitchen_fixtures_in_a_living_room_make_a_kitchen_zone():
    counter = M.fp("k", "kitchen_counter", (1.4, 3.7), (2.4, 0.6), front=270.0)
    stove = M.fp("st", "stove", (1.0, 3.7), (0.6, 0.6), front=270.0)
    sofa = M.fp("s", "sofa", (3.5, 0.6), (2.2, 0.9), rotation=180.0, front=90.0)
    build = _build([counter, stove, sofa], room_type="living", window=None)
    RD.read_furniture(build, {})
    zones = build.building["rooms"][0]["zones"]
    assert [z["kind"] for z in zones] == ["kitchen"] and zones[0]["piece_ids"] == ["k", "st"]
    zone = Polygon(zones[0]["polygon"])
    assert zone.contains(_fp(counter).buffer(-0.01)) and not zone.contains(_fp(sofa))
    assert zones[0]["evidence"][0]["rule"] == RD.ZONE_RULE
    kitchen = _build([M.fp("k", "kitchen_counter", (1.4, 3.7), (2.4, 0.6), front=270.0)], room_type="kitchen")
    RD.read_furniture(kitchen, {})
    assert not kitchen.building["rooms"][0].get("zones")


def test_an_untyped_piece_is_never_built_and_is_listed_for_review():
    box = M.fp("u", "unknown", (2.5, 2.0), (1.9, 1.7), front=None)
    build = _build([box], room_type="storage", window=None)
    works = _works(u={"candidate_key": "sym_L0_x1234abcd", "reason": "re-read part of an untyped cluster"})
    RD.read_furniture(build, works)
    f = _piece(build.building, "u")
    assert f["build"] is False and "untyped" in f["not_built_reason"]
    assert [e["method"] for e in f["evidence"]] == ["vector"]           # the reason is no source
    review = build.building["needs_review"]
    assert [(n["id"], n["kind"]) for n in review] == [("u", "untyped_piece")]
    assert review[0]["crop"] == "recognition/crops/sym_L0_x1234abcd_ctx.png" and "1.90 x 1.70" in review[0]["reason"]


def test_a_piece_whose_question_waits_for_its_answers_is_left_to_them():
    """The size inference would call a 0.12 x 0.05 m piece a drawn mark; while its question waits for the AI answers
    nothing is decided for it: not built, not listed for review (the pipeline lists the open questions)."""
    mark = M.fp("u", "unknown", (2.5, 2.0), (0.12, 0.05), front=None)
    build = _build([dict(mark)])
    RD.read_furniture(build, {})
    assert _piece(build.building, "u")["inferred_as"] == "detail"
    build = _build([dict(mark)])
    RD.read_furniture(build, _works(report={"pending": ["sym_L0_003"]}, u={"candidate_key": "sym_L0_003"}))
    f = _piece(build.building, "u")
    assert f["build"] is False and "inferred_as" not in f and "waits for the answers" in f["not_built_reason"]
    assert build.building["needs_review"] == []
    build = _build([dict(mark)])                         # answers applied this round: nothing waits
    RD.read_furniture(build, _works(report={"pending": ["sym_L0_003"], "answers_applied": 3},
                                    u={"candidate_key": "sym_L0_003"}))
    assert _piece(build.building, "u")["inferred_as"] == "detail"


def test_a_stove_drawn_inside_a_named_stove_block_is_drawn_twice():
    named = M.fp("st1", "stove", (1.0, 3.7), (0.6, 0.6), front=270.0, type_method="block_name")
    hob = M.fp("st2", "stove", (1.0, 3.7), (0.5, 0.5), front=270.0, type_method="ai_two_pass")
    build = _build([named, hob], room_type="kitchen", window=None)
    RD.read_furniture(build, {})
    assert _piece(build.building, "st1").get("build") is not False
    hob = _piece(build.building, "st2")
    assert hob["build"] is False and hob["inferred_as"] == "detail" and "drawn twice" in hob["inferred_reason"]
