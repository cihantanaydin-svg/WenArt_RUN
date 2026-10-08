"""Placer behaviour for rooms with drawn furniture (docs/milestone10.md §2.5).

Test room: 5 x 4 m, walls 0.1 m thick around it, a door on the south wall at x = 4.3 (0.9 m, opens into the
room) and a window on the west wall at y = 2.0 (1.2 m, sill 0.9 m). Drawn pieces are building furniture dicts
(``drawn``) turned into placer pieces with ``placer.drawn_piece``; the anchors come from ``locked.anchor_of``.
"""
import pytest
from shapely.geometry import Polygon

from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import schemas

ROOM_ID = "r_L0_oda"


def make_building(room_type="bedroom", furniture=()):
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-0.1, -0.05], "end": [5.1, -0.05], "thickness": 0.1},
        {"id": "w_e", "level_id": "L0", "start": [5.05, -0.1], "end": [5.05, 4.1], "thickness": 0.1},
        {"id": "w_n", "level_id": "L0", "start": [5.1, 4.05], "end": [-0.1, 4.05], "thickness": 0.1},
        {"id": "w_w", "level_id": "L0", "start": [-0.05, 4.1], "end": [-0.05, -0.1], "thickness": 0.1},
    ]
    openings = [
        {"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [4.3, -0.05], "width": 0.9,
         "swing_side": ROOM_ID},
        {"id": "win1", "type": "window", "level_id": "L0", "wall_id": "w_w", "center": [-0.05, 2.0], "width": 1.2,
         "sill_height": 0.9},
    ]
    room = {"id": ROOM_ID, "level_id": "L0", "label": "Oda", "room_type": room_type,
            "polygon": [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]], "area_computed": 20.0,
            "has_documented_furniture": True, "status": "verified", "evidence": []}
    return {"walls": walls, "openings": openings, "rooms": [room], "furniture": list(furniture)}, room


def drawn(pid, ftype, center, size, rotation=0.0, front=270.0, **extra):
    item = {"id": pid, "level_id": "L0", "room_id": ROOM_ID, "type": ftype, "source": "from_documents",
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation},
            "front_deg": front, "status": "verified", "evidence": []}
    item.update(extra)
    return item


def setup(items, room_type="bedroom"):
    building, room = make_building(room_type, items)
    ctx = P.room_context(building, room)
    anchors = [LK.anchor_of(f, building) for f in items]
    pieces = [P.drawn_piece(f, i, against_wall=a["kind"] == "back_edge") for i, (f, a) in enumerate(zip(items, anchors))]
    return building, ctx, pieces, anchors


def prop(ftype, center, rotation=0.0, size=None, wall=False):
    return {"type": ftype, "center": list(center), "rotation_deg": rotation,
            "size": list(size or schemas.default_size(ftype)), "against_wall": wall, "reason": "test"}


# --------------------------------------------------------------------------
# Frames and anchors
# --------------------------------------------------------------------------

def test_front_frame_turns_by_quarter_turns_to_the_front():
    fp = {"center": [1, 1], "size": [0.6, 0.5], "rotation_deg": 90.0}
    assert P.front_frame(fp, 180.0) == (270.0, (0.6, 0.5))         # half turn: same size
    assert P.front_frame(fp, 270.0) == (0.0, (0.5, 0.6))           # quarter turn: size swapped
    assert P.front_frame(fp, 0.0) == (90.0, (0.6, 0.5))            # consistent already
    assert P.front_frame(fp, 90.0) == (180.0, (0.5, 0.6))
    assert P.front_frame(fp, None) == (90.0, (0.6, 0.5))           # no front: as drawn
    for front in (0.0, 180.0, 270.0, 90.0):
        rot, size = P.front_frame(fp, front)
        same = P.Piece("x", (1, 1), rot, size, False).polygon()
        assert same.symmetric_difference(P.Piece("x", (1, 1), 90.0, (0.6, 0.5), False).polygon()).area < 1e-9


def test_anchored_center_keeps_the_back_edge_on_the_wall_line():
    anchor = {"kind": "back_edge", "point": [2.5, 3.98]}
    assert P.anchored_center(anchor, 0.0, (2.6, 0.95)) == pytest.approx((2.5, 3.505))
    assert P.anchored_center(anchor, 0.0, (2.2, 0.9)) == pytest.approx((2.5, 3.53))
    west = {"kind": "back_edge", "point": [0.02, 1.0]}               # back to the west wall: rotation 90
    assert P.anchored_center(west, 90.0, (1.8, 0.6)) == pytest.approx((0.32, 1.0))
    centre = {"kind": "centre", "point": [1.2, 2.3]}
    assert P.anchored_center(centre, 37.0, (2.0, 1.0)) == pytest.approx((1.2, 2.3))
    for size in ((2.2, 0.9), (3.0, 1.7)):
        c = P.anchored_center(anchor, 0.0, size)
        assert P.back_edge_midpoint(c, 0.0, size) == pytest.approx((2.5, 3.98))


# --------------------------------------------------------------------------
# The corner sofa's L
# --------------------------------------------------------------------------

def test_corner_sofa_is_an_l_polygon_with_the_main_seat_front_zone():
    right = P.Piece("sofa_corner", (2.5, 3.0), 0.0, (2.6, 1.6), True, shape="L", chaise_side="right",
                    chaise_depth=1.6)
    assert right.polygon().area == pytest.approx(2.6 * 0.9 + 0.9 * 0.7)
    assert not right.polygon().contains(Polygon([(1.3, 2.3), (1.5, 2.3), (1.5, 2.5), (1.3, 2.5)]))   # inner corner
    assert right.polygon().contains(Polygon([(3.5, 2.3), (3.7, 2.3), (3.7, 2.5), (3.5, 2.5)]))       # chaise, +X
    zone = right.front_zone()
    assert zone.bounds == pytest.approx((1.2, 2.3, 2.9, 2.9))                 # in front of the main seat only
    left = P.Piece("sofa_corner", (2.5, 3.0), 0.0, (2.6, 1.6), True, shape="L", chaise_side="left", chaise_depth=1.6)
    assert left.polygon().contains(Polygon([(1.3, 2.3), (1.5, 2.3), (1.5, 2.5), (1.3, 2.5)]))
    assert left.front_zone().bounds == pytest.approx((2.1, 2.3, 3.8, 2.9))
    item = drawn("f1", "sofa_corner", (2.5, 3.0), (2.6, 1.6), shape="L", chaise_side="left", chaise_depth=1.6)
    assert P.piece_from_furniture(item).polygon().equals(left.polygon())


def test_the_inner_corner_of_a_corner_sofa_can_hold_a_coffee_table():
    """A coffee table inside the L's bounding box but out of the main seat's clearance passes every check."""
    sofa = drawn("f1", "sofa_corner", (2.5, 3.18), (2.6, 1.6), shape="L", chaise_side="right", chaise_depth=1.6)
    _b, ctx, pieces, _a = setup([sofa], "living")
    assert pieces[0].against_wall and pieces[0].polygon().area == pytest.approx(2.97)
    table = P.Piece("table_coffee", (1.9, 2.2), 0.0, (0.8, 0.5), False)       # y 1.95..2.45: inside the box
    assert Polygon([(1.2, 2.38), (3.8, 2.38), (3.8, 3.98), (1.2, 3.98)]).intersects(table.polygon())
    checks = P.check_all([pieces[0], table], ctx)
    assert not P.failed_checks(checks[0]) and not P.failed_checks(checks[1]), checks
    closer = P.Piece("table_coffee", (1.9, 2.6), 0.0, (0.8, 0.5), False)      # in the main seat's 0.6 m
    assert P.check_all([pieces[0], closer], ctx)[0]["clearance_ok"] is False


# --------------------------------------------------------------------------
# Changed drawn pieces: anchored, shrink, revert, the baseline rule
# --------------------------------------------------------------------------

def test_a_changed_piece_grows_from_its_wall_line():
    sofa = drawn("f1", "sofa", (2.5, 3.53), (2.2, 0.9))
    _b, ctx, pieces, anchors = setup([sofa], "living")
    assert anchors[0]["kind"] == "back_edge"
    final, results, baseline = P.place_changes(pieces, [P.ChangeRequest(0, "sofa", (2.6, 0.95), anchors[0])], ctx)
    assert results[0].applied and final[0].size == (2.6, 0.95)
    assert final[0].center == pytest.approx((2.5, 3.505))
    assert P.back_edge_midpoint(final[0].center, 0.0, final[0].size) == pytest.approx(anchors[0]["point"])
    assert baseline == {"pieces": [[]], "walkways": []}


def test_a_corner_sofa_takes_the_free_side():
    sofa = drawn("f1", "sofa", (2.5, 3.53), (2.2, 0.9))
    chair = drawn("f2", "armchair", (3.7, 2.4), (0.8, 0.8), front=180.0, rotation=270.0)   # right, in front
    _b, ctx, pieces, anchors = setup([sofa, chair], "living")
    req = P.ChangeRequest(0, "sofa_corner", (2.6, 1.6), anchors[0])
    final, results, _base = P.place_changes(pieces, [req], ctx)
    steps = results[0].steps
    assert [s.get("chaise_side") for s in steps] == ["right", "left"]
    assert not steps[0]["ok"] and "no_overlap" in steps[0]["failed"]
    assert results[0].applied and final[0].shape == "L" and final[0].chaise_side == "left"
    assert final[0].chaise_depth == 1.6 and final[1] is pieces[1]                # the armchair never moves


def test_shrink_then_revert():
    """A free armchair changed to a sofa at its centre: 2.2 m and 1.6 m stick out of the room, the drawn
    armchair fits: revert, the drawn type and size stay."""
    chair = drawn("f1", "armchair", (4.5, 2.0), (0.8, 0.8))
    _b, ctx, pieces, anchors = setup([chair], "living")
    assert anchors[0]["kind"] == "centre"
    final, results, _base = P.place_changes(pieces, [P.ChangeRequest(0, "sofa", (2.2, 0.9), anchors[0])], ctx)
    res = results[0]
    assert [s["step"] for s in res.steps] == ["place", "shrink", "revert"]
    assert [s["size"] for s in res.steps[:2]] == [[2.2, 0.9], [1.6, 0.9]]
    assert all("inside_room" in s["failed"] for s in res.steps[:2])
    assert not res.applied and final[0] is pieces[0] and "drawn type and size kept" in res.reason
    assert all(s["center"] == [4.5, 2.0] for s in res.steps)                    # never snapped, slid or moved


def test_a_change_may_not_make_another_piece_fail():
    """A drawn chair changed into a dining table at its centre: the 1.6 m table enters the drawn bed's front
    clearance (the bed passed it before) although the table itself passes; the 1.2 m option is clear."""
    bed = drawn("f1", "bed_single", (0.6, 2.98), (0.9, 2.0))
    chair = drawn("f2", "chair", (1.8, 1.2), (0.45, 0.45), front=None)
    _b, ctx, pieces, anchors = setup([bed, chair], "other")
    final, results, base = P.place_changes(pieces, [P.ChangeRequest(1, "table_dining", (1.6, 0.9), anchors[1])], ctx)
    assert base == {"pieces": [[], []], "walkways": []}
    steps = results[0].steps
    assert not steps[0]["ok"] and steps[0]["failed"] == [] and steps[0]["others"] == ["bed_single #0: clearance_ok"]
    assert steps[1]["ok"] and steps[1]["step"] == "shrink" and steps[1]["size"] == [1.2, 0.8]
    assert results[0].applied and final[1].type == "table_dining" and final[1].center == (1.8, 1.2)
    assert final[0] is pieces[0]


def test_a_check_the_drawn_layout_already_fails_is_not_counted_against_the_change():
    """A chair drawn on the door's approach strip fails doors_free as drawn; changing it into an office chair
    at the same anchor keeps that failure (drawn_layout) and is applied."""
    chair = drawn("f1", "chair", (4.3, 0.4), (0.45, 0.45), front=None)
    _b, ctx, pieces, anchors = setup([chair], "bedroom")
    final, results, baseline = P.place_changes(pieces, [P.ChangeRequest(0, "office_chair", (0.6, 0.6), anchors[0])],
                                               ctx)
    assert baseline["pieces"] == [["doors_free"]]
    assert results[0].applied and final[0].type == "office_chair"
    assert results[0].steps[0]["failed"] == []                                  # nothing new


def test_an_unverified_piece_keeps_its_footprint():
    item = drawn("f1", "unknown", (2.0, 2.0), (1.2, 0.5), front=None, status="unverified")
    _b, ctx, pieces, anchors = setup([item], "living")
    req = P.ChangeRequest(0, "sideboard", (1.8, 0.48), anchors[0], footprint_only=True)
    final, results, _base = P.place_changes(pieces, [req], ctx)
    assert results[0].applied and final[0].type == "sideboard"
    assert final[0].size == (1.2, 0.5) and final[0].center == (2.0, 2.0)


def test_a_table_drawn_along_y_keeps_its_direction():
    table = drawn("f1", "table_dining", (2.5, 2.0), (0.8, 1.2), front=None)
    _b, ctx, pieces, anchors = setup([table], "dining")
    req = P.ChangeRequest(0, "table_dining", (1.6, 0.9), anchors[0], transposed=True)
    final, results, _base = P.place_changes(pieces, [req], ctx)
    assert results[0].applied and final[0].size == (0.9, 1.6) and final[0].rotation_deg == 0.0


# --------------------------------------------------------------------------
# Added pieces around the drawn ones (obstacles)
# --------------------------------------------------------------------------

def test_added_pieces_give_way_to_drawn_pieces():
    bed = drawn("f1", "bed_double", (2.5, 3.0), (1.6, 2.0))
    _b, ctx, pieces, _a = setup([bed])
    result = P.place([prop("wardrobe", (2.5, 1.5), 0.0, (1.2, 0.6), wall=False),      # in the bed's clearance
                      prop("nightstand", (1.3, 3.78), 0.0, (0.5, 0.4), wall=True)], ctx, obstacles=pieces)
    assert sorted([p.type for p in result.pieces] + [d["type"] for d in result.dropped]) == ["nightstand", "wardrobe"]
    assert "nightstand" in [p.type for p in result.pieces]
    wardrobe_steps = [e for e in result.log if e["type"] == "wardrobe"]
    assert wardrobe_steps and "clearance_ok" in wardrobe_steps[0]["failed"]     # it stood in the bed's clearance
    bed_piece = pieces[0]
    for p in result.pieces:
        assert p.polygon().intersection(bed_piece.front_zone()).area < P.AREA_EPS, p.type
        assert p.polygon().intersection(bed_piece.polygon()).area < P.AREA_EPS, p.type
    assert all(not any(p is q for q in result.pieces) for p in pieces)           # obstacles not in the result
    assert pieces[0].center == (2.5, 3.0) and pieces[0].size == (1.6, 2.0)      # the drawn bed never moves
    assert all(not P.failed_checks(c) for c in result.checks)


def test_an_added_piece_on_a_drawn_piece_is_repaired_not_the_drawn_one():
    sofa = drawn("f1", "sofa", (2.5, 3.53), (2.2, 0.9))
    _b, ctx, pieces, _a = setup([sofa], "living")
    result = P.place([prop("tv_unit", (2.5, 3.7), 0.0, (1.6, 0.45), wall=True)], ctx, obstacles=pieces)
    assert len(result.pieces) == 1 and result.log
    tv = result.pieces[0]
    assert tv.polygon().intersection(pieces[0].polygon()).area < P.AREA_EPS
    assert not P.failed_checks(result.checks[0])


def test_a_walkway_the_drawn_layout_breaks_is_not_required():
    """A drawn wardrobe across the room cuts the door from the window; an added nightstand is still placed."""
    wall = drawn("f1", "wardrobe", (2.5, 1.0), (5.0, 0.6), front=270.0)
    building, ctx, pieces, _a = setup([wall])
    assert P.walkway_failures(pieces, ctx)                                      # broken as drawn
    result = P.place([prop("nightstand", (3.0, 0.3), 180.0, (0.5, 0.4), wall=True)], ctx, obstacles=pieces)
    assert [p.type for p in result.pieces] == ["nightstand"] and not P.failed_checks(result.checks[0])


def test_an_office_chair_may_stand_at_its_desk():
    desk = drawn("f1", "desk", (2.0, 3.65), (1.4, 0.7))
    _b, ctx, pieces, _a = setup([desk])
    chair = P.Piece("office_chair", (2.0, 3.0), 0.0, (0.6, 0.6), False)
    assert not P.failed_checks(P.obstacle_checks(P.obstacles_for(pieces, ctx) + [chair], ctx)[1])
    other = P.Piece("chair", (2.0, 3.0), 0.0, (0.45, 0.45), False)
    assert P.obstacle_checks(P.obstacles_for(pieces, ctx) + [other], ctx)[1]["clearance_ok"] is False
    result = P.place([prop("office_chair", (2.0, 3.0), 0.0, (0.6, 0.6))], ctx, obstacles=pieces)
    assert result.pieces and result.pieces[0].center == (2.0, 3.0) and not result.log


def test_without_obstacles_place_is_the_milestone_4_placer():
    building, ctx, _pieces, _a = setup([])
    proposal = [prop("bed_double", (2.5, 2.979), 0.0, wall=True), prop("nightstand", (1.4, 3.778), 0.0, wall=True)]
    a = P.place(proposal, ctx).to_dict()
    b = P.place(proposal, ctx, obstacles=None).to_dict()
    assert a == b
