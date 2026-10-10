"""Functional furniture groups (docs/milestone11.md §6; wenart/furniture/groups.py) and the wall snap
(placer.snap_to_wall): each group placed in an empty room as one unit passes every placer check and scores 100; the
members face their anchor; an existing anchor gets its members; an unverified anchor and a second anchor are
refused."""
import json

import pytest
from shapely.geometry import Point
from shapely.ops import nearest_points

import _m11_room as M
from wenart import geometry as G
from wenart.furniture import groups as GR
from wenart.furniture import placer as P
from wenart.furniture import plausibility as PL


@pytest.mark.parametrize("group,rtype,anchor,members", [
    ("bed_set", "bedroom", "bed_double", {"nightstand": 2}),
    ("dining_set", "dining", "table_dining", {"chair": 6}),
    ("living_set", "living", "sofa", {"table_coffee": 1, "tv_unit": 1}),
    ("desk_set", "bedroom", "desk", {"office_chair": 1}),
    ("kitchen_run", "kitchen", "kitchen_counter", {"sink_kitchen": 1, "stove": 1, "fridge": 1}),
])
def test_each_group_is_placed_as_one_unit_and_scores_100(group, rtype, anchor, members):
    b = M.building(room_type=rtype)
    before = json.dumps(b, sort_keys=True)
    res = GR.place_group(b, M.ROOM_ID, group)
    assert json.dumps(b, sort_keys=True) == before                     # never mutates the building
    assert res["ok"] and not res["failed"], res
    types = [p["type"] for p in res["pieces"]]
    assert types[0] == anchor
    assert {t: types.count(t) for t in set(types[1:])} == members
    assert all(p["source"] == "added_by_ai" and p["status"] == "verified" for p in res["pieces"])
    assert all(not P.failed_checks(p["checks"]) for p in res["pieces"])
    b["furniture"] += res["pieces"]
    found = PL.score_room(b, M.ROOM_ID)["violations"]
    assert not [v for v in found if not v["check"].startswith("G")], found
    # Milestone 12: the group checks see what this Milestone 11 placer gets wrong (the TV unit in front of the window,
    # the hob at the end of the run, a work triangle out of range); the group solver (tests/test_solver_*.py) places
    # the same groups without them.
    known = {"living_set": {"G12"}, "kitchen_run": {"G8"}}.get(group, set())
    assert {v["check"] for v in found} == known, found


def test_dining_chairs_face_the_table():
    res = GR.place_group(M.building(room_type="dining"), M.ROOM_ID, "dining_set")
    table, chairs = res["pieces"][0], res["pieces"][1:]
    tpoly = P.piece_from_furniture(table).polygon()
    for c in chairs:
        cc = c["footprint"]["center"]
        near = nearest_points(tpoly, Point(cc))[0]
        assert G.angle_difference_deg(c["front_deg"], G.segment_angle_deg(cc, (near.x, near.y))) < 1.0


def test_members_around_an_existing_table_and_never_for_an_unverified_one():
    table = M.fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), front=None)
    res = GR.place_group(M.building(room_type="dining", furniture=[table]), M.ROOM_ID, "dining_set",
                         {"piece_id": "t1"})
    assert res["ok"] and [p["type"] for p in res["pieces"]] == ["chair"] * 6
    unsure = dict(table, status="unverified")
    res = GR.place_group(M.building(room_type="dining", furniture=[unsure]), M.ROOM_ID, "dining_set",
                         {"piece_id": "t1"})
    assert not res["ok"] and "unverified" in res["reason"]


def test_no_second_anchor_and_no_type_the_room_cannot_hold():
    bed = M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)
    res = GR.place_group(M.building(furniture=[bed]), M.ROOM_ID, "bed_set")
    assert not res["ok"] and "second" in res["reason"]
    res = GR.place_group(M.building(room_type="bathroom"), M.ROOM_ID, "living_set")
    assert not res["ok"]


def test_ids_follow_the_level_numbering():
    b = M.building(room_type="dining", furniture=[M.fp("f_L0_007", "bookshelf", (4.5, 3.8), (0.8, 0.3), front=270.0)])
    res = GR.place_group(b, M.ROOM_ID, "dining_set")
    assert res["pieces"][0]["id"] == "f_L0_008"


def test_snap_to_wall_puts_the_back_on_the_nearest_wall_and_skips_the_door():
    b = M.building()
    ctx = P.room_context(b, b["rooms"][0])
    # A wardrobe 0.3 m off the south wall, half in the swing of the door d1 (x = 1.0, 0.9 m): it slides off it.
    piece = P.Piece("wardrobe", (1.8, 0.65), 180.0, (1.2, 0.6), True)
    center, rotation, seg = P.snap_to_wall(piece, ctx)
    snapped = P.Piece("wardrobe", center, rotation, (1.2, 0.6), True)
    assert snapped.back_edge().distance(ctx.ring) <= P.SNAP_GAP_M + 1e-6
    assert G.angle_difference_deg(G.front_direction_deg(rotation), 90.0) < 1e-6
    assert not P._opening_blocked(snapped, ctx)
    assert P.snap_to_wall(piece, ctx, max_shift=0.05) is None             # too far for a 5 cm snap
