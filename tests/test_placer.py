"""Placer checks and repairs on hand-made proposals (docs/milestone4.md section 3).

Test room: 4 x 3 m, walls 0.1 m thick around it, a door on the south wall at
x = 1 (0.9 m, opens into the room), a door on the north wall at x = 3 (0.8 m,
opens out) and a window on the east wall at y = 1.5 (1.2 m, sill unknown).
"""
import json

import pytest
from shapely.geometry import Polygon

from wenart.furniture import placer as P
from wenart.furniture import schemas

ROOM_ID = "r_L0_oda"


def make_building(windows=None, sill=None, doors=None):
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [0.0, -0.05], "end": [4.0, -0.05], "thickness": 0.1, "exterior": True},
        {"id": "w_e", "level_id": "L0", "start": [4.05, 0.0], "end": [4.05, 3.0], "thickness": 0.1, "exterior": True},
        {"id": "w_n", "level_id": "L0", "start": [0.0, 3.05], "end": [4.0, 3.05], "thickness": 0.1, "exterior": False},
        {"id": "w_w", "level_id": "L0", "start": [-0.05, 0.0], "end": [-0.05, 3.0], "thickness": 0.1, "exterior": True},
    ]
    if doors is None:
        doors = [
            {"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [1.0, -0.05], "width": 0.9,
             "swing_side": ROOM_ID},
            {"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [3.0, 3.05], "width": 0.8,
             "swing_side": "r_L0_other"},
        ]
    if windows is None:
        windows = [{"id": "win1", "type": "window", "level_id": "L0", "wall_id": "w_e", "center": [4.05, 1.5],
                    "width": 1.2, "sill_height": sill}]
    room = {"id": ROOM_ID, "level_id": "L0", "label": "Oda", "room_type": "bedroom",
            "polygon": [[0.0, 0.0], [4.0, 0.0], [4.0, 3.0], [0.0, 3.0]], "area_computed": 12.0,
            "has_documented_furniture": False, "status": "verified", "evidence": []}
    return {"walls": walls, "openings": doors + windows, "rooms": [room]}, room


def piece(ftype, center, rotation=0.0, size=None, against_wall=False):
    return {"type": ftype, "center": list(center), "rotation_deg": rotation,
            "size": list(size or schemas.default_size(ftype)), "against_wall": against_wall, "reason": "test"}


@pytest.fixture
def ctx():
    building, room = make_building()
    return P.room_context(building, room)


def checks_of(ctx, items):
    pieces = [P.Piece.from_proposal(it, i) for i, it in enumerate(items)]
    return P.check_all(pieces, ctx)


# --------------------------------------------------------------------------
# Context
# --------------------------------------------------------------------------

def test_room_context_openings_and_baseline(ctx):
    assert [d.id for d in ctx.doors] == ["d1", "d2"]
    assert [w.id for w in ctx.windows] == ["win1"]
    d1 = ctx.doors[0]
    assert d1.inner_point == pytest.approx((1.0, 0.0))
    assert d1.approach_point == pytest.approx((1.0, 0.46))
    assert d1.swing is not None and not d1.swing.is_empty          # opens into this room
    assert ctx.doors[1].swing is None                                # opens into the other room
    assert ctx.windows[0].sill == P.DEFAULT_SILL_M and ctx.windows[0].sill_assumed
    assert ctx.windows[0].band.bounds == pytest.approx((3.7, 0.9, 4.0, 2.1))
    assert len(ctx.baseline_pairs) == 3   # d1-d2, d1-win1, d2-win1 all reachable in the empty room
    assert len(ctx.segments) == 4


def test_openings_of_another_room_are_ignored():
    building, room = make_building()
    building["openings"].append({"id": "d9", "type": "door", "level_id": "L0", "wall_id": "w_e",
                                 "center": [7.0, 1.0], "width": 0.9, "swing_side": None})
    doors, windows = P.room_openings(building, room)
    assert [d["id"] for d in doors] == ["d1", "d2"] and [w["id"] for w in windows] == ["win1"]


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def test_inside_room_uses_the_2cm_shrink(ctx):
    outside, touching, inside = checks_of(ctx, [
        piece("table_coffee", (0.3, 1.5)), piece("table_coffee", (0.5, 2.5)), piece("table_coffee", (2.0, 1.5))])
    assert outside["inside_room"] is False
    assert touching["inside_room"] is False      # x from 0.0: on the wall face, inside the 2 cm margin
    assert inside["inside_room"] is True


def test_overlap_but_touching_is_fine(ctx):
    a, b = checks_of(ctx, [piece("chair", (2.0, 1.5)), piece("chair", (2.2, 1.5))])
    assert a["no_overlap"] is False and b["no_overlap"] is False
    a, b = checks_of(ctx, [piece("chair", (2.0, 1.5)), piece("chair", (2.45, 1.5))])
    assert a["no_overlap"] is True and b["no_overlap"] is True


def test_door_approach_strip_and_swing_arc(ctx):
    on_strip, = checks_of(ctx, [piece("chair", (1.0, 0.3))])
    assert on_strip["doors_free"] is False
    # Beside the strip but inside the 0.9 m half disc of the door that opens into the room.
    in_swing, = checks_of(ctx, [piece("chair", (1.7, 0.5))])
    assert in_swing["doors_free"] is False
    # Same position relative to the north door, which opens into the other room: only the strip counts.
    near_out_door, = checks_of(ctx, [piece("chair", (3.7, 2.5))])
    assert near_out_door["doors_free"] is True
    # Straight in front of a door but past the strip: the 0.9 m walkway start is blocked.
    on_walkway, = checks_of(ctx, [piece("chair", (3.0, 2.1))])
    assert on_walkway["doors_free"] is False
    far, = checks_of(ctx, [piece("chair", (2.0, 1.5))])
    assert far["doors_free"] is True


def test_walkway_between_doors_is_kept(ctx):
    # A 3.0 m counter across the room leaves 0.7 m at the east end: no 0.9 m walkway from d1 to d2.
    blocked, = checks_of(ctx, [piece("kitchen_counter", (1.8, 1.5), size=(3.0, 0.6))])
    assert blocked["doors_free"] is False
    pieces = [P.Piece.from_proposal(piece("kitchen_counter", (1.8, 1.5), size=(3.0, 0.6)), 0)]
    blamed, failures = P.walkway_blame(pieces, ctx)
    assert blamed == {0} and ("door", "d1", "door", "d2") in failures
    # 2.4 m leaves 1.3 m: fine.
    ok, = checks_of(ctx, [piece("kitchen_counter", (1.5, 1.5), size=(2.4, 0.6))])
    assert ok["doors_free"] is True


def test_walkway_to_a_window_may_be_served_by_a_bed(ctx):
    # A wardrobe row in front of the window band (not in it) cuts the window off: fails ...
    blocked = checks_of(ctx, [piece("bookshelf", (3.3, 0.6), 270, size=(1.2, 0.4)),
                              piece("bookshelf", (3.3, 1.8), 270, size=(1.2, 0.4)),
                              piece("bookshelf", (3.3, 2.6), 270, size=(0.8, 0.4))])
    assert any(c["doors_free"] is False for c in blocked)
    # ... but a bed under the window serves it, and the doors stay connected.
    served, = checks_of(ctx, [piece("bed_double", (2.979, 1.2), 270, against_wall=True)])
    assert served["doors_free"] is True and served["windows_free"] is True


def test_window_rule_height_vs_sill():
    building, room = make_building()
    ctx = P.room_context(building, room)
    tall, bed, low = checks_of(ctx, [piece("wardrobe", (3.679, 1.5), 270, size=(1.2, 0.6)),
                                     piece("bed_double", (1.5, 1.5), 270),
                                     piece("nightstand", (3.75, 1.5), 270)])
    assert tall["windows_free"] is False          # 2.1 m tall inside the 0.3 m band
    assert bed["windows_free"] is True            # beds may stand under a window
    assert low["windows_free"] is True            # 0.5 m < 0.9 m sill
    building, room = make_building(sill=0.3)
    ctx = P.room_context(building, room)
    low, bed = checks_of(ctx, [piece("nightstand", (3.75, 1.5), 270), piece("bed_double", (1.5, 1.5), 270)])
    assert low["windows_free"] is False and bed["windows_free"] is True


def test_wall_contact_within_5cm(ctx):
    away, = checks_of(ctx, [piece("bed_double", (2.0, 1.7), against_wall=True)])     # back at y = 2.7
    assert away["wall_contact"] is False
    close, = checks_of(ctx, [piece("bed_double", (2.0, 1.979), against_wall=True)])  # back at y = 2.979
    assert close["wall_contact"] is True
    free, = checks_of(ctx, [piece("bed_double", (2.0, 1.7), against_wall=False)])
    assert free["wall_contact"] is True


def test_clearance_in_front_of_a_sofa(ctx):
    sofa, table = checks_of(ctx, [piece("sofa", (1.5, 2.529), against_wall=True), piece("table_coffee", (1.5, 1.8))])
    assert sofa["clearance_ok"] is False and table["clearance_ok"] is True
    sofa, table = checks_of(ctx, [piece("sofa", (1.5, 2.529), against_wall=True), piece("table_coffee", (1.5, 1.1))])
    assert sofa["clearance_ok"] is True
    # A desk facing a wall 0.3 m away has no room for a chair.
    desk, = checks_of(ctx, [piece("desk", (2.0, 0.65), 0.0)])
    assert desk["clearance_ok"] is False


# --------------------------------------------------------------------------
# Repairs
# --------------------------------------------------------------------------

def steps(result):
    return [e["step"] for e in result.log]


def test_repair_snap_to_the_nearest_wall(ctx):
    result = P.place([piece("bed_double", (1.5, 1.7), against_wall=True)], ctx)
    assert steps(result) == ["snap"] and result.iterations == 1 and result.all_ok
    bed = result.pieces[0]
    assert bed.center == pytest.approx((1.5, 3.0 - P.SNAP_GAP_M - 1.0), abs=1e-3)
    assert bed.rotation_deg == 0.0 and not result.dropped
    # Before the snap the bed also reached into the swing of the south door.
    assert result.log[0]["failed"] == ["doors_free", "wall_contact"] and result.log[0]["ok"] is True


def test_repair_slide_along_the_wall_off_the_door(ctx):
    result = P.place([piece("wardrobe", (3.0, 2.679), against_wall=True)], ctx)
    assert steps(result) == ["slide"] and result.all_ok and not result.dropped
    assert result.pieces[0].center == pytest.approx((1.7, 2.679), abs=1e-3)
    assert result.log[0]["failed"] == ["doors_free"]


def test_repair_shrink_to_the_next_size_option():
    extra = {"id": "win2", "type": "window", "level_id": "L0", "wall_id": "w_n", "center": [0.6, 3.05],
             "width": 1.2, "sill_height": None}
    building, room = make_building()
    building["openings"].append(extra)
    ctx = P.room_context(building, room)
    # Between the north window (x 0..1.2) and the door strip (x 2.6..3.4) only 1.4 m of wall is free.
    result = P.place([piece("wardrobe", (1.9, 2.679), against_wall=True)], ctx)
    assert "shrink" in steps(result) and result.all_ok and not result.dropped
    assert result.pieces[0].size == (1.2, 0.6)
    assert 1.2 <= result.pieces[0].center[0] - 0.6 and result.pieces[0].center[0] + 0.6 <= 2.6


def test_repair_relocate_to_another_wall(ctx):
    # A wardrobe (2.1 m tall) on the east wall always hits the window band at every size: it moves to
    # another wall at its proposed size instead of being dropped.
    result = P.place([piece("wardrobe", (3.679, 1.5), 270, against_wall=True)], ctx)
    assert steps(result) == ["slide", "shrink", "slide", "relocate"]   # 1.8 -> 1.2 is the only smaller option
    assert result.all_ok and not result.dropped
    w = result.pieces[0]
    assert w.size == (1.8, 0.6) and w.center[0] < 3.5
    assert result.log[-1]["failed"] == ["windows_free"] and result.log[-1]["ok"] is True


def make_tiny_building():
    """2.0 x 1.5 m room with one door: no bed fits at any size or on any wall."""
    building, room = make_building(doors=[
        {"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [1.0, -0.05], "width": 0.8,
         "swing_side": ROOM_ID}], windows=[])
    building["walls"] = [
        {"id": "w_s", "level_id": "L0", "start": [0.0, -0.05], "end": [2.0, -0.05], "thickness": 0.1},
        {"id": "w_e", "level_id": "L0", "start": [2.05, 0.0], "end": [2.05, 1.5], "thickness": 0.1},
        {"id": "w_n", "level_id": "L0", "start": [0.0, 1.55], "end": [2.0, 1.55], "thickness": 0.1},
        {"id": "w_w", "level_id": "L0", "start": [-0.05, 0.0], "end": [-0.05, 1.5], "thickness": 0.1},
    ]
    room["polygon"] = [[0.0, 0.0], [2.0, 0.0], [2.0, 1.5], [0.0, 1.5]]
    room["area_computed"] = 3.0
    return building, room


def test_repair_drop_when_nothing_fits():
    building, room = make_tiny_building()
    ctx = P.room_context(building, room)
    result = P.place([piece("bed_double", (1.0, 0.5), against_wall=True)], ctx)
    st = steps(result)
    assert st[-1] == "drop" and "shrink" in st and "relocate" in st and "slide" in st
    assert not result.pieces and result.dropped[0]["reason"] == "no repair left"
    assert result.dropped[0]["type"] == "bed_double" and "inside_room" in result.dropped[0]["failed"]
    assert result.iterations == len([e for e in result.log if e["step"] != "size_snapped"])


def test_iteration_cap_drops_the_rest():
    building, room = make_tiny_building()
    ctx = P.room_context(building, room)
    proposal = [piece("bed_double", (1.0, 0.5), against_wall=True), piece("bed_single", (1.0, 0.5), against_wall=True)]
    result = P.place(proposal, ctx, max_iterations=2)
    assert result.iterations == 2 and not result.pieces
    reasons = {d["type"]: d["reason"] for d in result.dropped}
    assert reasons["bed_double"] == "iteration cap"
    assert all(e["iteration"] <= 2 for e in result.log)


def test_later_pieces_give_way_first(ctx):
    bed = piece("bed_double", (1.5, 1.979), against_wall=True)
    chair = piece("chair", (1.5, 1.2))                      # inside the bed
    result = P.place([bed, chair], ctx)
    assert result.all_ok
    assert result.pieces[0].center == pytest.approx((1.5, 1.979), abs=1e-3)   # the bed did not move
    assert result.log[0]["type"] == "chair"


def test_size_not_an_option_is_snapped(ctx):
    result = P.place([piece("sofa", (1.5, 2.529), size=(1.55, 0.9), against_wall=True)], ctx)
    assert result.log[0]["step"] == "size_snapped" and result.log[0]["after"]["size"] == [1.6, 0.9]
    assert result.pieces[0].size == (1.6, 0.9)


def test_place_is_deterministic(ctx):
    proposal = [piece("bed_double", (1.5, 1.7), against_wall=True), piece("wardrobe", (3.0, 2.679), against_wall=True),
                piece("nightstand", (0.5, 2.7), against_wall=True), piece("chair", (1.0, 0.8))]
    a = P.place(proposal, ctx).to_dict()
    b = P.place(proposal, ctx).to_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_placed_pieces_satisfy_every_check(ctx):
    proposal = [piece("bed_double", (1.5, 1.7), against_wall=True), piece("wardrobe", (3.0, 2.679), against_wall=True),
                piece("nightstand", (0.5, 2.7), against_wall=True), piece("chair", (1.0, 0.8)),
                piece("desk", (3.5, 0.5), 180.0, against_wall=True)]
    result = P.place(proposal, ctx)
    assert result.all_ok
    for p in result.pieces:
        assert Polygon(ctx.room["polygon"]).buffer(-0.019).contains(p.polygon())
        for door in ctx.doors:
            assert p.polygon().intersection(door.zone).area < P.AREA_EPS
    assert not P.walkway_failures(result.pieces, ctx)


def test_piece_from_furniture_roundtrip():
    item = {"type": "sofa", "footprint": {"center": [2.75, 4.65], "size": [2.2, 0.9], "rotation_deg": 0.0}}
    p = P.piece_from_furniture(item)
    assert p.type == "sofa" and p.center == (2.75, 4.65) and p.size == (2.2, 0.9)
    assert p.polygon().bounds == pytest.approx((1.65, 4.2, 3.85, 5.1))
