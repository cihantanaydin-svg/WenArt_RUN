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
    # both pieces are anchors of a bedroom: they get one extra budget of 2, then go
    assert 2 <= result.iterations <= 4 and not result.pieces
    reasons = {d["type"]: d["reason"] for d in result.dropped}
    assert reasons["bed_double"].startswith("iteration cap")
    assert all(e["iteration"] <= 4 for e in result.log)


def test_anchor_piece_survives_the_iteration_cap():
    """A bedroom keeps its bed: at the cap the other failing pieces are dropped first."""
    building, room = make_building()
    ctx = P.room_context(building, room)
    bed = piece("bed_double", (2.0, 1.1), against_wall=True)
    alone = P.place([dict(bed)], ctx)
    assert len(alone.pieces) == 1, alone.dropped          # the bed fits on its own
    proposal = [dict(bed), piece("nightstand", (2.0, 1.1), against_wall=True),
                piece("desk", (2.0, 1.1), against_wall=True), piece("chair", (2.0, 1.1))]
    result = P.place(proposal, ctx, max_iterations=2)
    kept = {pc.type for pc in result.pieces}
    assert "bed_double" in kept, [d["type"] for d in result.dropped]
    assert all(d["type"] != "bed_double" for d in result.dropped)


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


# --------------------------------------------------------------------------
# Anchor first (furnish run 2: both L1 bedrooms lost their bed)
# --------------------------------------------------------------------------

def make_small_bedroom():
    """synthetic-01 L1 'Yatak Odası': 3.3 x 3.7 m, door on the west wall at y = 2.0
    (opens into the room), window on the south wall at x = 7.7 (1.8 m)."""
    walls = [
        {"id": "w_s", "level_id": "L1", "start": [6.05, 0.2], "end": [9.35, 0.2], "thickness": 0.1, "exterior": True},
        {"id": "w_e", "level_id": "L1", "start": [9.4, 0.25], "end": [9.4, 3.95], "thickness": 0.1, "exterior": True},
        {"id": "w_n", "level_id": "L1", "start": [6.05, 4.0], "end": [9.35, 4.0], "thickness": 0.1, "exterior": False},
        {"id": "w_w", "level_id": "L1", "start": [6.0, 0.25], "end": [6.0, 3.95], "thickness": 0.1, "exterior": False},
    ]
    room = {"id": "r_L1_yatak_odasi", "level_id": "L1", "label": "Yatak Odası", "room_type": "bedroom",
            "polygon": [[6.05, 0.25], [9.35, 0.25], [9.35, 3.95], [6.05, 3.95]], "area_computed": 12.21,
            "has_documented_furniture": False, "status": "verified", "evidence": []}
    openings = [
        {"id": "d_L1_003", "type": "door", "level_id": "L1", "wall_id": "w_w", "center": [6.0, 2.0], "width": 0.9,
         "swing_side": room["id"]},
        {"id": "win_L1_002", "type": "window", "level_id": "L1", "wall_id": "w_s", "center": [7.7, 0.2],
         "width": 1.8, "sill_height": None},
    ]
    return {"walls": walls, "openings": openings, "rooms": [room]}, room


# Qwen's pass-1 proposal for that room (furnish run 2): the bed first, as asked.
RUN2_PROPOSAL = [
    piece("bed_double", (7.2, 2.5), size=(1.8, 2.0), against_wall=True),
    piece("nightstand", (6.7, 2.5), size=(0.5, 0.4), against_wall=True),
    piece("nightstand", (7.7, 2.5), size=(0.5, 0.4), against_wall=True),
    piece("wardrobe", (6.0, 1.0), size=(1.8, 0.6), against_wall=True),
    piece("desk", (8.0, 2.0), size=(1.4, 0.7), against_wall=True),
    piece("chair", (8.1, 1.9), size=(0.5, 0.5)),
]


def test_anchor_first_keeps_the_bed_the_first_attempt_dropped():
    building, room = make_small_bedroom()
    ctx = P.room_context(building, room)
    first = P._place(RUN2_PROPOSAL, ctx)
    assert "bed_double" in {d["type"] for d in first.dropped}, "the first attempt should lose the bed here"
    result = P.place(RUN2_PROPOSAL, ctx)
    assert result.anchor_first and result.all_ok
    bed = next(pc for pc in result.pieces if pc.type == "bed_double")
    assert bed.locked and bed.center == pytest.approx((7.9, 2.929), abs=1e-3)   # where it fits alone
    assert bed.proposed["center"] == [7.2, 2.5]                                 # the proposal is kept for the debug image
    marker = [e for e in result.log if e["step"] == "anchor_first"]
    assert len(marker) == 1 and marker[0]["type"] == "bed_double" and marker[0]["after"]["center"] == [7.9, 2.929]
    assert [e["step"] for e in result.log[:3]] == ["snap", "slide", "anchor_first"]
    assert all(d["type"] != "bed_double" for d in result.dropped)
    assert len(result.pieces) >= 3                                               # bed plus at least two others
    assert result.to_dict()["anchor_first"] is True


def test_anchor_first_is_not_used_when_the_anchor_fits_first_time(ctx):
    result = P.place([piece("bed_double", (1.5, 1.979), against_wall=True), piece("chair", (1.5, 1.2))], ctx)
    assert result.all_ok and not result.anchor_first
    assert not [e for e in result.log if e["step"] == "anchor_first"]


def test_anchor_first_gives_up_when_the_anchor_fits_nowhere():
    building, room = make_tiny_building()
    ctx = P.room_context(building, room)
    result = P.place([piece("bed_double", (1.0, 0.5), against_wall=True), piece("chair", (1.0, 0.5))], ctx)
    assert not result.anchor_first and "bed_double" in {d["type"] for d in result.dropped}


def test_a_piece_in_the_locked_anchors_clearance_gives_way():
    building, room = make_building(doors=[], windows=[])      # no walkways: only the clearance can fail
    ctx = P.room_context(building, room)
    bed = P.place([piece("bed_double", (1.5, 1.979), against_wall=True)], ctx).pieces[0]
    bed.locked = True
    # A chair in front of the bed passes its own checks; only the bed's clearance fails.
    chair = piece("chair", (1.5, 0.75))
    result = P._place([chair], ctx, locked=[bed])
    assert [pc.type for pc in result.pieces] == ["bed_double"] and result.all_ok
    assert result.dropped[0]["type"] == "chair" and result.dropped[0]["reason"] == "gives way to the anchor"
    assert "clearance_ok" not in result.dropped[0]["failed"]                     # the chair itself was fine
    assert result.log[-1]["step"] == "drop"


# --------------------------------------------------------------------------
# Review fixes (Milestone 4 review)
# --------------------------------------------------------------------------

def test_a_door_flush_with_a_corner_keeps_its_walkways():
    """The point straight in front of a narrow corner door lies outside the eroded
    free floor; the walkway start moves to the nearest walkable point instead of
    the door losing every walkway pair."""
    corner_door = [{"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [0.36, -0.05],
                    "width": 0.7, "swing_side": "r_L0_other"},
                   {"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [3.0, 3.05],
                    "width": 0.8, "swing_side": "r_L0_other"}]
    building, room = make_building(doors=corner_door)
    ctx = P.room_context(building, room)
    assert len(ctx.baseline_pairs) == 3                       # d1-d2, d1-win1, d2-win1
    d1 = next(d for d in ctx.doors if d.id == "d1")
    assert d1.approach_point[0] >= P.ERODE_M - P.POINT_TOL_M  # moved into the eroded region
    # A wall of storage across the room between the two doors is caught.
    wall = [piece("wardrobe", (1.5, 1.5), 90.0, (2.4, 0.6), against_wall=False),
            piece("dresser", (1.5, 0.4), 90.0, (1.4, 0.5)), piece("dresser", (1.5, 2.6), 90.0, (1.4, 0.5))]
    assert P.walkway_failures([P.Piece.from_proposal(it, i) for i, it in enumerate(wall)], ctx)


def test_inside_room_catches_a_rotated_corner_tip(ctx):
    """A corner tip 5 mm outside the shrunk polygon has almost no area but is outside."""
    tip = P.Piece.from_proposal(piece("washing_machine", (0.40, 1.5), 110.0, (0.6, 0.6)), 0)
    assert tip.polygon().difference(ctx.shrunk).area < P.AREA_EPS      # the old area test let it through
    assert not Polygon(ctx.room["polygon"]).buffer(-0.019).contains(tip.polygon())
    assert P.check_piece(tip, [], ctx)["inside_room"] is False
    ok = P.Piece.from_proposal(piece("washing_machine", (0.6, 1.5), 110.0, (0.6, 0.6)), 0)
    assert P.check_piece(ok, [], ctx)["inside_room"] is True


def test_swapped_size_is_taken_as_the_turned_piece(ctx):
    log = []
    p = P.Piece.from_proposal(piece("bed_double", (2.0, 1.5), 0.0, (2.0, 1.6), against_wall=True), 3, log)
    assert p.size == (1.6, 2.0) and p.rotation_deg == 90.0 and p.proposal_index == 3
    assert log[0]["step"] == "size_snapped" and "swapped" in log[0]["note"] and log[0]["piece"] == 3
    q = P.Piece.from_proposal(piece("bed_double", (2.0, 1.5), 0.0, (1.7, 2.1), against_wall=True), 0, [])
    assert q.size == (1.6, 2.0) and q.rotation_deg == 0.0                # not a swap: nearest option, no turn


def test_log_piece_numbers_are_proposal_positions_in_the_anchor_first_retry():
    building, room = make_small_bedroom()
    ctx = P.room_context(building, room)
    result = P.place(RUN2_PROPOSAL, ctx)
    assert result.anchor_first
    by_type = {}
    for e in result.log:
        by_type.setdefault(e["type"], set()).add(e["piece"])
    assert by_type["bed_double"] == {0} and by_type["chair"] == {5} and by_type["desk"] == {4}
