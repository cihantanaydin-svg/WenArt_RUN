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


def _context_only(build) -> dict:
    """The Milestone 12 context rules alone (two passes with the fronts between, as ``read_furniture`` runs them):
    build round 3 (K3) runs ``infer.code_types`` before them, so a piece code can explain (a bed's missing
    nightstands, a sofa's missing TV unit) is code typed first and the rule never sees it; these tests exercise the
    rules themselves (``test_code_types_first_then_the_context_rules_and_both_withdraw`` pins the order)."""
    counts = RD.context_types(build, {})
    RD.infer_fronts(build)
    for k, v in RD.context_types(build, {}).items():
        counts[k] = counts.get(k, 0) + v
    return counts


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
    def pieces():
        return [M.fp("bed", "bed_double", (2.5, 3.0), (1.6, 2.0), front=270.0),
                M.fp("n1", "unknown", (1.45, 3.75), (0.45, 0.40), front=None),
                M.fp("n2", "unknown", (3.55, 3.75), (0.45, 0.40), front=None)]

    build = _build(pieces())
    _context_only(build)
    for pid in ("n1", "n2"):
        f = _piece(build.building, pid)
        assert f["type"] == "nightstand" and f["front_deg"] == 270.0 and RD.CONTEXT_RULE in _rules(f)
        assert f["inferred"] is True and "beside the head of bed" in f["inferred_reason"]
    # Build round 3 (K3): in the reading step the code typing runs first: the squares are the bed's missing
    # nightstands (infer.type_by_code, group_member) before the context rule sees them; the same type and front.
    build = _build(pieces())
    RD.read_furniture(build, {})
    for pid in ("n1", "n2"):
        f = _piece(build.building, pid)
        assert (f["type"], f["type_method"], f["front_deg"]) == ("nightstand", "group_member", 270.0)
        assert RD.CONTEXT_RULE not in _rules(f) and build.reading["typed_by"][pid] == "group_member"


def test_seats_around_a_dining_table_are_chairs_facing_it():
    table = M.fp("t", "table_dining", (2.5, 2.0), (1.6, 0.9), front=None)
    south = M.fp("c1", "unknown", (2.0, 1.25), (0.45, 0.45), front=None)
    north = M.fp("c2", "unknown", (3.0, 2.75), (0.45, 0.45), front=None)
    build = _build([table, south, north], room_type="dining")
    RD.read_furniture(build, {})
    assert _piece(build.building, "c1")["type"] == "chair" and _piece(build.building, "c1")["front_deg"] == 90.0
    assert _piece(build.building, "c2")["type"] == "chair" and _piece(build.building, "c2")["front_deg"] == 270.0


def test_a_table_with_seats_drawn_around_it_is_a_dining_set():
    """real01 --no-ai: the table and its six chairs are asked, nothing answers; the drawing says what they are."""
    table = M.fp("t", "unknown", (2.5, 2.0), (1.24, 0.74), front=None)
    seats = [M.fp(f"c{k}", "unknown", c, (0.46, 0.38), front=None)
             for k, c in enumerate([(2.2, 1.4), (2.8, 1.4), (2.2, 2.6), (2.8, 2.6), (1.65, 2.0)])]
    lone = M.fp("x", "unknown", (4.4, 3.5), (1.24, 0.74), front=None)
    build = _build([table, lone] + seats, room_type="dining", window=None)
    _context_only(build)          # build round 3: read_furniture types the table by code first (the missing anchor)
    t = _piece(build.building, "t")
    # Fix round after P4b (17 Oct 2026, pinned on purpose): a context-typed piece now carries type_method "rule"
    # (reading.CONTEXT_METHOD), a schema value, instead of none.
    assert t["type"] == "table_dining" and t["inferred"] is True and t["type_method"] == RD.CONTEXT_METHOD
    assert "5 seats drawn around it on 3 sides" in t["inferred_reason"]
    fronts = {f["id"]: f["front_deg"] for f in build.building["furniture"] if f["type"] == "chair"}
    assert fronts == {"c0": 90.0, "c1": 90.0, "c2": 270.0, "c3": 270.0, "c4": 0.0}
    assert "seats drawn around it" not in (_piece(build.building, "x").get("inferred_reason") or "")   # none there


def test_a_coffee_table_and_a_tv_unit_face_the_sofa():
    def pieces():
        return [M.fp("s", "sofa", (2.5, 3.55), (2.2, 0.9), front=270.0),
                M.fp("ct", "unknown", (2.5, 2.4), (1.0, 0.6), front=None),
                M.fp("tv", "unknown", (3.0, 0.225), (1.6, 0.45), front=None)]

    build = _build(pieces(), room_type="living", door_x=0.6, window=None)
    _context_only(build)          # build round 3: read_furniture types both by code first (the seating's members)
    assert _piece(build.building, "ct")["type"] == "table_coffee"
    f = _piece(build.building, "tv")
    assert f["type"] == "tv_unit" and f["front_deg"] == 90.0 and "facing s" in f["inferred_reason"]
    build = _build(pieces(), room_type="living", door_x=0.6, window=None)
    RD.read_furniture(build, {})
    assert {_piece(build.building, p)["type_method"] for p in ("ct", "tv")} == {"group_member"}
    assert _piece(build.building, "tv")["type"] == "tv_unit" and _piece(build.building, "ct")["type"] == "table_coffee"


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


def test_unbuilt_pieces_say_why_and_an_oversized_cluster_is_listed():
    detail = M.fp("d", "unknown", (1.0, 3.7), (0.62, 0.6), front=None, build=False)
    big = M.fp("big", "unknown", (2.5, 2.0), (4.8, 0.6), front=None, build=False)
    build = _build([detail, big], room_type="living", window=None)
    works = _works(d={"build": False, "reason": "detail inside a kitchen counter leg (M11 split): not built"},
                   big={"oversize": True, "build": False,
                        "reason": "cluster larger than 4.5 m on a side: a group of drawn pieces, not built"})
    RD.read_furniture(build, works)
    assert _piece(build.building, "d")["not_built_reason"].startswith("detail inside a kitchen counter leg")
    assert _piece(build.building, "big")["not_built_reason"].startswith("cluster larger than 4.5 m")
    assert [n["id"] for n in build.building["needs_review"]] == ["big"]


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
    # Milestone 13 (K3, "code first, the AI types the rest") types the square beside the bed's head as the bed's
    # missing nightstand by code (infer.type_by_code, method group_member) while the question is open, and
    # withdraws the question (build round 3: before the context rules, which type the open questions too).
    bed = M.fp("bed", "bed_double", (2.5, 3.0), (1.6, 2.0), front=270.0)
    square = M.fp("n", "unknown", (1.45, 3.75), (0.45, 0.40), front=None)
    build = _build([bed, square])
    works = _works(report={"pending": ["sym_L0_004"], "questions": [{"key": "sym_L0_004"}]},
                   n={"candidate_key": "sym_L0_004"})
    RD.read_furniture(build, works)
    n = _piece(build.building, "n")
    assert (n["type"], n["type_method"]) == ("nightstand", "group_member") and RD.CONTEXT_RULE not in _rules(n)
    assert n.get("build") is not False and works["page"].extraction.report["pending"] == []
    assert build.code_typed == {"sym_L0_004": "n"} and build.code_typed_methods == {"sym_L0_004": "group_member"}
    assert works["page"].extraction.report["typed_by_code_methods"] == {"sym_L0_004": "group_member"}
    # A square code cannot explain (no bed in the room) stays as asked while its question is open.
    build = _build([dict(square)])
    RD.read_furniture(build, _works(report={"pending": ["sym_L0_004"]}, n={"candidate_key": "sym_L0_004"}))
    assert _piece(build.building, "n")["type"] == "unknown" and _piece(build.building, "n")["front_deg"] is None
    assert build.code_typed == {}


def test_a_piece_code_types_before_the_ai_gets_no_question():
    """Milestone 13 (K3, round 2: "code first, the AI types the rest"): a footprint the twin room's typed piece
    explains (infer.type_by_code, method twin) is typed while its AI question still waits, built, and its question
    is withdrawn: the key leaves the page's ``pending``, goes to ``report["typed_by_code"]`` and ``build.code_typed``,
    and the pipeline leaves it out of ``recognition/requests.json``. A piece code cannot type keeps its question
    and waits for the answers as before."""
    import copy
    from wenart.ingest import pipeline as P

    bed = M.fp("bed", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)
    twin_bed = M.fp("u", "unknown", (7.98, 2.0), (1.6, 2.0), rotation=90.0, front=None, status="unverified",
                    room_id="r_L0_oda_2")
    odd = M.fp("q", "unknown", (3.0, 3.0), (0.3, 0.3), front=None, status="unverified")
    build = _build([bed, twin_bed, odd], w=4.0, h=4.0, window=None)
    a = build.building["rooms"][0]
    second = copy.deepcopy(a)
    second.update(id="r_L0_oda_2", polygon=[[5.0, 0.0], [9.0, 0.0], [9.0, 4.0], [5.0, 4.0]], twin_of=a["id"],
                  twin_transform=[-1.0, 0.0, 9.0, 0.0, 1.0, 0.0])
    build.building["rooms"].append(second)
    sha = "0" * 64
    questions = [{"key": "sym_L0_002", "task": "symbol_type", "images": ["crops/sym_L0_002_ctx.png"],
                  "input_sha256": sha},
                 {"key": "sym_L0_003", "task": "symbol_type", "images": ["crops/sym_L0_003_ctx.png"],
                  "input_sha256": sha}]
    works = _works(report={"questions": questions, "pending": ["sym_L0_002", "sym_L0_003"]},
                   u={"candidate_key": "sym_L0_002"}, q={"candidate_key": "sym_L0_003"})
    RD.read_furniture(build, works)
    u = _piece(build.building, "u")
    assert (u["type"], u["type_method"], u["inferred"]) == ("bed_double", "twin", True)
    assert u.get("build") is not False and u["evidence"][-1]["rule"].endswith("type_by_code:twin")
    q = _piece(build.building, "q")
    assert q["type"] == "unknown" and q["build"] is False and "waits for the answers" in q["not_built_reason"]
    report = works["page"].extraction.report
    assert report["pending"] == ["sym_L0_003"] and report["typed_by_code"] == ["sym_L0_002"]
    assert report["typed_by_code_methods"] == {"sym_L0_002": "twin"}           # build round 3: with the method
    assert build.code_typed == {"sym_L0_002": "u"} and build.reading["code_typed"] == ["u"]
    assert build.code_typed_methods == {"sym_L0_002": "twin"} and build.reading["typed_by"] == {"u": "twin"}
    assert build.reading["questions_withdrawn"] == ["sym_L0_002"]
    assert any("sym_L0_002 withdrawn" in w and "(twin, K3)" in w for w in build.building["warnings"])
    # The pipeline writes the remaining question only; nothing waits for the withdrawn one.
    import tempfile
    from pathlib import Path
    from wenart.recognition import answers as A

    build.furniture_works = [works["page"]]
    build.building["project"]["id"] = "t"
    with tempfile.TemporaryDirectory() as tmp:
        P._write_questions(build, Path(tmp))
        doc = A.read_requests(Path(tmp) / "recognition")
    assert [i["key"] for i in doc["items"]] == ["sym_L0_003"]
    assert build.pending == ["sym_L0_003"] and build.unanswered == ["sym_L0_003"]
    assert [q["key"] for q in build.questions] == ["sym_L0_003"]
    text = "\n".join(P._reading_section(build.building, build))
    assert "typed by code before the AI: 1: u [twin]" in text


def test_code_types_first_then_the_context_rules_and_both_withdraw():
    """Build round 3 (K3, lead decision): ``read_furniture`` runs ``infer.code_types`` before the Milestone 12
    context rules and the context rules type the open questions too; both withdraw the piece's question with its
    method, so the AI is asked the same questions with --no-ai, in the first plain run and in the run with the
    answers. A dining room with an unknown table and seats whose questions are all open: the table is the room's
    missing dining anchor (code, group_member), the seats are chairs at the table (context:chair); a bathroom's
    counter under its basin is the vanity (context:vanity, not built). Nothing is left pending; a piece neither
    code nor the context explains keeps its question."""
    import copy
    from wenart.ingest import pipeline as P

    sha = "0" * 64
    table = M.fp("t", "unknown", (2.5, 2.0), (1.24, 0.74), front=None, status="unverified")
    seats = [M.fp(f"c{k}", "unknown", c, (0.46, 0.38), front=None, status="unverified")
             for k, c in enumerate([(2.2, 1.4), (2.8, 1.4), (2.2, 2.6), (2.8, 2.6), (1.65, 2.0)])]
    odd = M.fp("q", "unknown", (4.4, 3.5), (0.3, 0.3), front=None, status="unverified")
    build = _build([table, odd] + seats, room_type="dining", window=None)
    ids = ["t", "q"] + [s["id"] for s in seats]
    keys = {pid: f"sym_L0_{i + 1:03d}" for i, pid in enumerate(ids)}
    questions = [{"key": keys[pid], "task": "symbol_type", "images": [f"crops/{keys[pid]}_ctx.png"],
                  "input_sha256": sha} for pid in ids]
    works = _works(report={"questions": questions, "pending": [keys[pid] for pid in ids]},
                   **{pid: {"candidate_key": keys[pid]} for pid in ids})
    RD.read_furniture(build, works)
    t = _piece(build.building, "t")
    assert (t["type"], t["type_method"]) == ("table_dining", "group_member") and RD.CONTEXT_RULE not in _rules(t)
    for s in seats:
        c = _piece(build.building, s["id"])
        assert c["type"] == "chair" and RD.CONTEXT_RULE in _rules(c) and c.get("build") is not False
        assert c["front_deg"] is not None
    q = _piece(build.building, "q")
    assert q["type"] == "unknown" and q["build"] is False and "waits for the answers" in q["not_built_reason"]
    report = works["page"].extraction.report
    assert report["pending"] == [keys["q"]]
    assert sorted(report["typed_by_code"]) == sorted(keys[pid] for pid in ids if pid != "q")
    want = {keys["t"]: "group_member", **{keys[s["id"]]: "context:chair" for s in seats}}
    assert report["typed_by_code_methods"] == want and build.code_typed_methods == want
    assert build.code_typed == {keys[pid]: pid for pid in ids if pid != "q"}
    assert build.reading["typed_by"] == {"t": "group_member", **{s["id"]: "context:chair" for s in seats}}
    assert build.reading["code_typed"] == sorted(["t"] + [s["id"] for s in seats])
    assert build.reading["questions_withdrawn"] == sorted(want)
    # The pipeline writes the remaining question only, and the report names both kinds with their method.
    import tempfile
    from pathlib import Path
    from wenart.recognition import answers as A

    build.furniture_works = [works["page"]]
    build.building["project"]["id"] = "t"
    with tempfile.TemporaryDirectory() as tmp:
        P._write_questions(build, Path(tmp))
        doc = A.read_requests(Path(tmp) / "recognition")
    assert [i["key"] for i in doc["items"]] == [keys["q"]] and build.pending == [keys["q"]]
    text = "\n".join(P._reading_section(build.building, build))
    assert "t [group_member]" in text and "c0 [context:chair]" in text
    # The same drawing with no open question (--no-ai, or the run with the answers for q): the same typing.
    again = _build([copy.deepcopy(table), copy.deepcopy(odd)] + [copy.deepcopy(s) for s in seats],
                   room_type="dining", window=None)
    RD.read_furniture(again, _works(**{pid: {"candidate_key": keys[pid]} for pid in ids}))
    assert again.reading["typed_by"] == build.reading["typed_by"]
    assert {f["id"]: f["type"] for f in again.building["furniture"]} == {f["id"]: f["type"]
                                                                          for f in build.building["furniture"]}
    # The counter under a washbasin is its vanity: a context decision too, withdrawn as context:vanity (not built).
    basin = M.fp("wb", "washbasin", (1.0, 2.25), (0.6, 0.45), front=270.0)
    counter = M.fp("v", "unknown", (1.0, 2.2), (1.2, 0.55), front=None, status="unverified")
    bath = _build([basin, counter], room_type="bathroom", window=None)
    works = _works(report={"questions": [{"key": "sym_L0_009", "task": "symbol_type", "images": [],
                                          "input_sha256": sha}], "pending": ["sym_L0_009"]},
                   v={"candidate_key": "sym_L0_009"})
    RD.read_furniture(bath, works)
    v = _piece(bath.building, "v")
    assert v["type"] == "unknown" and v["build"] is False and v["inferred_as"] == "detail"
    assert bath.code_typed_methods == {"sym_L0_009": "context:vanity"} and bath.building["needs_review"] == []
    assert works["page"].extraction.report["pending"] == []


def test_the_questions_withdrawn_are_the_same_in_every_mode_and_an_answered_one_stays():
    """Build round 3 (K3, lead decision): the same dining drawing read as a first plain run (every question pending),
    as --no-ai (the questions written, nothing pending: ``core`` sets ``pending`` to []) and as a run with the answers
    (``answers_applied``; the answered question no longer pending, the others not in the round) withdraws the same
    questions: the table (code, group_member) and the five seats (context:chair); the odd 0.3 m piece keeps its
    question. A question asked and answered in this round is never withdrawn (``answered_keys``): here the AI's
    answer for the table said "unknown", code types the table all the same, the question stays listed and a warning
    says so; the seats' questions (not in that round) are withdrawn as in the first run."""
    import copy

    sha = "0" * 64
    table = M.fp("t", "unknown", (2.5, 2.0), (1.24, 0.74), front=None, status="unverified")
    seats = [M.fp(f"c{k}", "unknown", c, (0.46, 0.38), front=None, status="unverified")
             for k, c in enumerate([(2.2, 1.4), (2.8, 1.4), (2.2, 2.6), (2.8, 2.6), (1.65, 2.0)])]
    odd = M.fp("q", "unknown", (4.4, 3.5), (0.3, 0.3), front=None, status="unverified")
    ids = ["t", "q"] + [s["id"] for s in seats]
    keys = {pid: f"sym_L0_{i + 1:03d}" for i, pid in enumerate(ids)}
    questions = [{"key": keys[pid], "task": "symbol_type", "images": [], "input_sha256": sha} for pid in ids]
    details = {pid: {"candidate_key": keys[pid]} for pid in ids}

    def read(report):
        build = _build([copy.deepcopy(table), copy.deepcopy(odd)] + [copy.deepcopy(s) for s in seats],
                       room_type="dining", window=None)
        works = _works(report=dict(report, questions=copy.deepcopy(questions)), **details)
        RD.read_furniture(build, works)
        return build, works["page"].extraction.report

    plain, plain_report = read({"pending": [keys[pid] for pid in ids]})
    no_ai, no_ai_report = read({"pending": []})
    want = {keys["t"]: "group_member", **{keys[s["id"]]: "context:chair" for s in seats}}
    for build, report in ((plain, plain_report), (no_ai, no_ai_report)):
        assert build.code_typed_methods == want and report["typed_by_code_methods"] == want
        assert sorted(report["typed_by_code"]) == sorted(want)
    assert plain_report["pending"] == [keys["q"]] and no_ai_report["pending"] == []
    assert {f["id"]: f["type"] for f in plain.building["furniture"]} == \
        {f["id"]: f["type"] for f in no_ai.building["furniture"]}
    # the run with the answers: the table's question was asked and answered ("unknown"), the others not in the round
    answers, report = read({"pending": [keys[pid] for pid in ids if pid != "t"], "answers_applied": 1})
    page = {"page": SimpleNamespace(extraction=SimpleNamespace(report=report))}
    assert RD.answered_keys(answers, page) == {keys["t"]}                  # asked, answered, not withdrawn
    assert RD.answered_keys(plain, {"page": SimpleNamespace(extraction=SimpleNamespace(report=plain_report))}) == set()
    t = _piece(answers.building, "t")
    assert (t["type"], t["type_method"]) == ("table_dining", "group_member")
    assert keys["t"] not in answers.code_typed and keys["t"] not in report["typed_by_code"]
    assert answers.code_typed_methods == {k: v for k, v in want.items() if k != keys["t"]}
    assert any(f"recognition question {keys['t']} kept" in w for w in answers.building["warnings"])
    assert keys["q"] in report["pending"]


def test_a_stove_drawn_inside_a_named_stove_block_is_drawn_twice():
    named = M.fp("st1", "stove", (1.0, 3.7), (0.6, 0.6), front=270.0, type_method="block_name")
    hob = M.fp("st2", "stove", (1.0, 3.7), (0.5, 0.5), front=270.0, type_method="ai_two_pass")
    build = _build([named, hob], room_type="kitchen", window=None)
    RD.read_furniture(build, {})
    assert _piece(build.building, "st1").get("build") is not False
    hob = _piece(build.building, "st2")
    assert hob["build"] is False and hob["inferred_as"] == "detail" and "drawn twice" in hob["inferred_reason"]


def test_the_report_lists_symbols_review_items_adjusted_equipment_and_zones():
    from wenart.ingest import pipeline as P

    tag = M.fp("f1", "unknown", (2.0, 2.0), (0.5, 0.5), front=None)
    # Milestone 13 (K3): a 1.9 x 1.7 m box would be the living room's missing corner sofa, typed by code
    # (infer.type_by_code); a 1.3 x 1.3 m box fits no missing member and stays for review.
    box = M.fp("u", "unknown", (3.5, 1.0), (1.3, 1.3), front=None)
    counter = M.fp("k", "kitchen_counter", (1.4, 3.7), (2.4, 0.6), front=270.0)
    wc = M.fp("wc", "toilet", (4.5, 1.0), (0.38, 1.10), front=None)
    build = _build([tag, box, counter, wc], room_type="living", window=None)
    RD.read_furniture(build, _works(f1={"symbol": {"kind": "room_number", "reason": "circle with the number '5'"}},
                                    u={"candidate_key": "sym_L0_x00000001"}))
    text = "\n".join(P._reading_section(build.building, build))
    assert "## Reading (Milestone 12)" in text and "Symbols (not furniture, never built): 1 (room_number 1)" in text
    assert "| sy_L0_001 | room_number | L0 | r_L0_oda | f1 |" in text
    assert "Needs review (untyped drawn pieces, not built): 1." in text and "sym_L0_x00000001_ctx.png" in text
    assert "| wc | toilet | 0.38 x 1.10 |" in text and "| r_L0_oda | r_L0_oda_kitchen (kitchen) | k |" in text
