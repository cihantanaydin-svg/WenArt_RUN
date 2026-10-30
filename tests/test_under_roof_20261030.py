"""Lessons UL128 and UL132 (30 Oct 2026; the user on real04 run 20261029-201533-full: "Some frames coming out of the
roof it needs fixing", "Door frame needs fixing"): nothing built inside a level under a sloped ceiling crosses the
ceiling or the roof, and a door's opening, leaf, lining, head and architrave share one height that fits there. CPU
tests on a synthetic attic (a ceiling plane z = 6.0 - 0.5 y over a level at 3.0 m with a flat 2.5 m part) and on the
real04 run's records when they are on this machine."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.blender import build as B
from wenart.blender import door_states as DS
from wenart.blender import furniture as F
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import under_roof as UR

RUN = Path("/home/user/WenArt_RUN/runs/20261029-201533-full/results")
PLANES = [[0.0, -0.5, 6.0], [0.0, 0.0, 5.5]]


def attic(rooms=None, walls=None, openings=None) -> dict:
    """The synthetic attic: the wall ``w1`` along y (x = 0) between ``ra`` (x < 0) and ``rb`` (x > 0), the slope falling
    towards +y (2.5 m over the floor up to y = 1, 1.0 m at y = 4)."""
    level = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.5, "ceiling_planes": copy.deepcopy(PLANES)}
    return {"levels": [level],
            "walls": walls or [{"id": "w1", "level_id": "L1", "start": [0.0, 0.0], "end": [0.0, 6.0],
                                "thickness": 0.1}],
            "rooms": rooms or [{"id": "ra", "level_id": "L1", "room_type": "living",
                                "polygon": [[-3, 0], [0, 0], [0, 6], [-3, 6]]},
                               {"id": "rb", "level_id": "L1", "room_type": "living",
                                "polygon": [[0, 0], [3, 0], [3, 6], [0, 6]]}],
            "openings": openings or [], "furniture": [], "decor": []}


def door(y: float, height=2.1, assumed=True, wall="w1", x=0.0, **extra) -> dict:
    return dict({"id": f"d_{y:g}", "type": "door", "level_id": "L1", "wall_id": wall, "center": [x, y], "width": 0.8,
                 "height": height, "assumed": ["height"] if assumed else []}, **extra)


# ------------------------------------------------------------------------------------------------- doors (UL128)

def test_a_door_under_the_slope_is_lowered_to_its_head_room():
    b = attic(openings=[door(1.0), door(2.0)])
    walls, level = {w["id"]: w for w in b["walls"]}, b["levels"][0]
    # its frame reaches y = 2.0 + 0.4 + 0.023: the plane there is 4.7885 m, 0.05 m under it, over the 3.0 m floor
    assert DS.head_room(b["openings"][1], walls["w1"], level) == pytest.approx(1.7385, abs=1e-4)
    changes = {c["id"]: c for c in DS.plan_under_roof(b)}
    assert "d_1" not in changes                                    # 2.24 m of head room: 2.10 m fits
    c = changes["d_2"]
    assert c["fits"] and c["height"] == pytest.approx(1.7385, abs=1e-4) and c["moved_m"] == 0.0
    _ch, assumed, warnings = DS.apply_under_roof(b)
    o = b["openings"][1]
    assert o["height"] == pytest.approx(1.7385, abs=1e-4) and o["drawn_height"] == 2.1 and not warnings
    assert o["under_roof"]["was"] == 2.1 and o["adjusted_by_ai"]["rule"].startswith("UL128")
    assert assumed and assumed[0]["kind"] == "door_under_roof"
    assert not DS.plan_under_roof(b)                                # idempotent


def test_the_role_sizes_never_raise_a_door_over_the_slope():
    """D5 put real04's d_L1_001 / 002 back to 2.10 m under a 1.84 m slope ("a sloped ceiling over the level: 2.10 m
    kept"): under a slope the role's height is held to the head room at the wall."""
    b = attic(openings=[door(2.0, height=1.70)])
    o, wall, level = b["openings"][0], b["walls"][0], b["levels"][0]
    h, why = DS._door_height(b, o, wall, level, None, "a full-height door")
    assert h == pytest.approx(1.7385, abs=1e-4) and "head room" in why
    h, _why = DS._door_height(b, dict(o, center=[0.0, 0.5]), wall, level, DS.STANDARD_HEIGHT_M, "a standard door")
    assert h == DS.STANDARD_HEIGHT_M                                 # fits under the slope: the standard height


def test_a_door_that_does_not_fit_slides_along_its_wall_or_is_a_finding():
    b = attic(openings=[door(2.6)])
    c = DS.plan_under_roof(b)[0]
    assert c["fits"] and c["moved_m"] == pytest.approx(-0.35) and c["height"] == pytest.approx(1.6135, abs=1e-4)
    DS.apply_under_roof(b)
    assert b["openings"][0]["drawn_center"] == [0.0, 2.6] and b["openings"][0]["center"][1] == pytest.approx(2.25)
    # too low everywhere within 0.5 m (and a drawn height): lowered all the same, a finding
    b = attic(openings=[door(3.5, height=2.0, assumed=False)])
    c = DS.plan_under_roof(b)[0]
    assert not c["fits"] and c["drawn"] and c["height"] < DS.MIN_CLEAR_M
    _c, _a, warnings = DS.apply_under_roof(b)
    assert warnings and "dormer" in warnings[0]
    probs = UR.door_problems(b)
    assert [p["target"] for p in probs] == ["d_3.5"] and probs[0]["severity"] == "major"


def test_a_slide_never_passes_a_wall_meeting_the_door_wall():
    rooms = [{"id": "ra", "level_id": "L1", "room_type": "living", "polygon": [[-3, 0], [0, 0], [0, 6], [-3, 6]]},
             {"id": "rb", "level_id": "L1", "room_type": "hall", "polygon": [[0, 0], [3, 0], [3, 2.3], [0, 2.3]]},
             {"id": "rc", "level_id": "L1", "room_type": "living", "polygon": [[0, 2.3], [3, 2.3], [3, 6], [0, 6]]}]
    b = attic(rooms=rooms, openings=[door(2.9)])
    c = DS.plan_under_roof(b)[0]
    assert not c["fits"] and c["moved_m"] == 0.0                     # the fitting spot would open into rb


def test_an_open_leaf_stays_under_the_slope_over_it():
    """A door in a wall square to the slope opening into the low side: its open leaf reaches 0.7 m into the room,
    where the ceiling is lower than its top; it is tried at smaller angles, then closed, never through the ceiling."""
    walls = [{"id": "w2", "level_id": "L1", "start": [0.0, 2.0], "end": [6.0, 2.0], "thickness": 0.1}]
    rooms = [{"id": "low", "level_id": "L1", "room_type": "living", "polygon": [[0, 2], [6, 2], [6, 6], [0, 6]]},
             {"id": "high", "level_id": "L1", "room_type": "living", "polygon": [[0, -2], [6, -2], [6, 2], [0, 2]]}]
    b = attic(rooms=rooms, walls=walls, openings=[door(2.0, wall="w2", x=3.0, swing_side="low")])
    DS.apply_under_roof(b)
    o = b["openings"][0]
    assert o["height"] == pytest.approx(1.925, abs=2e-3)
    states = DS.plan_states(b, {"family": "modern"})
    rec = states[o["id"]]
    level = b["levels"][0]
    head = DS.leaf_head(o, level)
    for poly in rec.get("leaf_polys") or []:
        assert DS.leaf_under_ceiling(poly, head) is None
    # its drawn swing side is the low room: it stays closed, with the reason
    assert rec["state"] == "closed" and "sloped ceiling" in rec["reason"]
    # the same door on a flat level opens wide
    flat = copy.deepcopy(b)
    flat["levels"][0].pop("ceiling_planes")
    assert DS.plan_states(flat, {"family": "modern"})[o["id"]]["state"] == "open"
    # no swing side drawn (the wall drawn the other way: the low room is the default side): its swing turns into
    # the high room, the build hangs it there (``swing_side``)
    walls2 = [dict(walls[0], start=[6.0, 2.0], end=[0.0, 2.0])]
    b2 = attic(rooms=rooms, walls=walls2, openings=[door(2.0, wall="w2", x=3.0)])
    DS.apply_under_roof(b2)
    states2, assumed2 = DS.apply_states(b2, {"family": "modern"})
    rec2 = states2["d_2"]
    assert rec2["state"] == "open" and rec2["into"] == "high" and rec2.get("swing_turned")
    assert b2["openings"][0]["swing_side"] == "high" and any(a["kind"] == "door_swing_under_roof" for a in assumed2)
    for poly in rec2["leaf_polys"]:
        assert DS.leaf_under_ceiling(poly, DS.leaf_head(b2["openings"][0], b2["levels"][0])) is None


# ---------------------------------------------------------------------------------------- one frame (UL132)

def test_the_frame_is_complete_and_as_high_as_its_opening():
    parts = P.door_frame_parts(0.8, 1.8, 0.15, 0.02, 1.0, faces=(-1.0, 1.0))
    census = P.frame_census(parts, 1.8)
    assert census["lining"] == {"jambs": 2, "heads": 1}
    assert census["faces"] == {"-1": {"jambs": 2, "heads": 1}, "1": {"jambs": 2, "heads": 1}}
    assert census["top_m"] == pytest.approx(1.8 + DS.HEAD_RISE_M, abs=1e-3)       # the architrave's head
    assert not DS.census_problems("d", census)
    # pinned: the architrave's rise and reach the door rule leaves room for
    assert DS.HEAD_RISE_M == pytest.approx(P.ARCHITRAVE_W_M + P.ARCHITRAVE_REVEAL_M - P.DOOR_FRAME_W, abs=1e-6)
    tall = P.frame_census(P.door_frame_parts(0.8, 2.1, 0.15, 0.02, 1.0), 1.8)       # built for 2.10 in a 1.80 m door
    kinds = {p["kind"] for p in DS.census_problems("d", tall)}
    assert "frame_taller" in kinds
    no_head = P.frame_census([p for p in parts if not (p["role"] == "frame" and
                                                         max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"])
                                                         < 0.9)], 1.8)
    assert {p["kind"] for p in DS.census_problems("d", no_head)} == {"jamb_without_head"}
    one = dict(census, lining={"jambs": 1, "heads": 1})
    assert {p["kind"] for p in DS.census_problems("d", one)} == {"one_jamb"}
    manifest = {"objects": [{"kind": "door", "element_id": "d", "name": "d_frame",
                             "frame": {"lining": True, "head": True, "architrave": [-1, 1], "indoor_faces": [-1, 1],
                                       "census": tall}}]}
    assert {p["kind"] for p in DS.frame_problems(manifest)} == {"frame_taller"}
    assert MR.M29_KINDS["frame_taller"] == "geometry" and "frame_taller" in MR.M29_FIX


# -------------------------------------------------------------------------------- the crossing check (M31)

def _box(cx, cy, z0, z1, w=0.5, d=0.5, rot=0.0) -> dict:
    return {"center": [cx, cy, (z0 + z1) / 2.0], "size": [w, d, z1 - z0], "rotation_deg": rot}


def test_the_check_flags_every_interior_object_crossing_the_ceiling_or_the_roof():
    b = attic()
    roof = {"outline": [[-5, -5], [5, -5], [5, 7], [-5, 7]], "equations": [[0.0, -0.5, 6.2]]}
    objs = [{"name": "furn_f1", "kind": "furniture", "type": "wardrobe", "element_id": "f1", "level_id": "L1",
             "box3d": _box(1.0, 3.0, 3.0, 5.0)},                    # 2.0 m where the ceiling is 1.5 m, roof 1.7 m
            {"name": "d1_frame", "kind": "door", "element_id": "d1", "level_id": "L1",
             "box3d": _box(0.0, 2.0, 3.0, 4.9, w=0.15, d=0.9)},     # 1.9 m under a 1.77 m ceiling: inside only
            {"name": "d1_leaf", "kind": "door", "element_id": "d1", "level_id": "L1",
             "box3d": _box(0.3, 2.0, 3.0, 4.6, w=0.7, d=0.05)},
            {"name": "decor_dec_1", "kind": "decor", "type": "towel_rail", "decor_id": "dec_1", "level_id": "L1",
             "box3d": _box(1.0, 4.0, 3.15, 4.35, w=0.5, d=0.1)},
            {"name": "decor_dec_2", "kind": "decor", "type": "pendant_light", "decor_id": "dec_2", "level_id": "L1",
             "box3d": _box(1.0, 1.5, 4.8, 5.3)},                     # hung: its canopy meets the slope
            {"name": "furn_f2", "kind": "furniture", "type": "sofa", "element_id": "f2", "level_id": "L1",
             "box3d": _box(1.0, 1.0, 3.0, 3.9)},
            {"name": "furn_f3", "kind": "furniture", "type": "wardrobe", "element_id": "f3", "level_id": "L1",
             "box3d": _box(9.0, 3.0, 3.0, 5.0)}]                    # out of the roof's outline: a terrace
    got = {c["target"]: c for c in UR.crossings(objs, b, roof)}
    assert set(got) == {"f1", "d1", "dec_1"}
    assert got["f1"]["severity"] == "critical" and got["f1"]["through_roof"]
    assert got["d1"]["severity"] == "major" and got["d1"]["name"] == "d1_frame"      # the worst part names it
    assert got["dec_1"]["severity"] == "critical"
    found, n = MR.roof_crossings(b, {"objects": objs}, roof)
    assert n == len(objs) - 0 and {f["target"] for f in found} == {"f1", "d1", "dec_1"}
    assert all(f["check"] == "M31" for f in found) and "M31" in MR.CHECKS


# ------------------------------------------------------------------------------------------------ decor (UL128)

def test_hostless_decor_stays_under_the_slope():
    """real04's towel rails and shelves under a 0.81 m slope and its 2.45 m terrazzo panels under a 1.87 m one were
    built through the roof: the builder's bound now holds every hostless type."""
    b = attic()
    level = b["levels"][0]
    b["decor"] = [
        {"id": "rail", "type": "towel_rail", "level_id": "L1", "host_id": None, "center": [1.0, 4.0, 0.15],
         "size": [0.5, 0.1, 1.2], "rotation_deg": 0.0},
        {"id": "panel", "type": "feature_panel", "level_id": "L1", "host_id": None, "center": [1.0, 2.5, 0.0],
         "size": [1.0, 0.015, 2.446], "rotation_deg": 0.0},
        {"id": "holder", "type": "toilet_paper_holder", "level_id": "L1", "host_id": None,
         "center": [1.0, 1.0, 0.635], "size": [0.16, 0.13, 0.13], "rotation_deg": 0.0},
        {"id": "plant", "type": "plant_large", "level_id": "L1", "host_id": None, "center": [1.0, 4.5],
         "size": [0.5, 0.5, 1.6], "rotation_deg": 0.0},
        {"id": "pend", "type": "pendant_light", "level_id": "L1", "host_id": None, "center": [1.0, 1.0, 1.5],
         "size": [0.4, 0.4, 0.5], "rotation_deg": 0.0}]
    decor, warnings, not_built = B.decor_under_roof(b, level)
    kept = {d["id"]: d for d in decor}
    assert {n["id"] for n in not_built} == {"rail", "plant"}
    # the slope over its far edge (y 2.5075): 4.746 m, 1.746 m over the floor, 2 cm under it
    assert kept["panel"]["size"][2] == pytest.approx(6.0 - 0.5 * 2.5075 - 3.0 - B.WINDOW_DECOR_CEILING_CLEAR_M, abs=1e-3)
    assert kept["holder"] == b["decor"][2] and kept["pend"] == b["decor"][4]
    assert any("shorter from the top" in w for w in warnings)


def test_wall_art_hangs_under_the_slope_over_its_wall():
    b = attic()
    level = b["levels"][0]
    item = {"id": "m", "type": "mirror", "center": [0.1, 3.0], "wall_point": [0.05, 3.0], "rotation_deg": 90.0,
            "gap_m": 0.3}
    ceiling, _how = F.ceiling_above(level, item["wall_point"], (0.55, 0.02), 90.0)
    assert ceiling == pytest.approx(1.36, abs=0.02)                  # the slope over the wall, not the flat 2.5 m
    fp, mount = F.wall_art_placement(item, [0.55, 0.02, 0.7], 0.75, ceiling)
    assert fp is None or mount["top_m"] <= ceiling                   # refused or scaled under it, never through


def test_hosted_decor_takes_a_board_under_the_slope_or_is_not_built():
    """Books on a bookshelf under the slope take a board their top fits under; on a top that leaves no room they are
    not built, with the reason (``rest.plan_decor``'s ``max_top_z``)."""
    def slab(z0, z1, x0=-0.4, x1=0.4, y0=-0.15, y1=0.15):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
             (x0, y1, z1)]
        f = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        return v, f

    verts, faces = [], []
    for z in (0.0, 0.6, 1.2, 1.8):                                   # four boards
        v, f = slab(z, z + 0.02)
        faces += [[i + len(verts) for i in ff] for ff in f]
        verts += v
    caster = R.MeshCaster(verts, faces)
    host = {"id": "shelf", "type": "bookshelf", "footprint": {"center": [0.0, 0.0], "size": [0.8, 0.3],
                                                              "rotation_deg": 0.0}}
    books, bf = slab(0.0, 0.25, -0.1, 0.1, -0.08, 0.08)
    item = {"id": "b1", "type": "book_set", "center": [0.0, 0.0], "rotation_deg": 0.0}
    free = R.plan_decor(item, host, caster, books, bf, "shelf", shelf=3)
    assert free["pose"]["z"] == pytest.approx(1.82, abs=1e-3)
    low = R.plan_decor(item, host, caster, books, bf, "shelf", shelf=3, max_top_z=1.5)
    assert "pose" in low and low["pose"]["z"] + 0.25 <= 1.5 + 1e-6
    top_host = dict(host, type="side_table")
    over = R.plan_decor(item, top_host, caster, books, bf, "top", max_top_z=1.9)
    assert "not_rested" in over and "sloped ceiling" in over["not_rested"]["reason"]
    assert R.under_slope([(0, 0, 1.0)], 1.2) is None and R.under_slope([(0, 0, 1.3)], 1.2)


def test_the_bathroom_details_are_placed_under_the_slope():
    from wenart.furniture import bath_details as BD

    b = attic()
    b["roof"] = None
    room = b["rooms"][1]
    # decor.ceiling_over without a roof model: the level's flat ceiling (2.5 m): a 1.2 m rail at 0.15 m fits
    assert BD.under_slope(b, room, [1.0, 4.0], (0.5, 0.1, 1.2), 0.0, 0.15)
    import wenart.furniture.decor as D
    old = D.ceiling_planes
    try:
        D.ceiling_planes = lambda building, level_id: copy.deepcopy(PLANES)
        assert not BD.under_slope(b, room, [1.0, 4.0], (0.5, 0.1, 1.2), 0.0, 0.15)     # 1.0 m of ceiling there
        assert BD.under_slope(b, room, [1.0, 1.0], (0.5, 0.1, 1.2), 0.0, 0.15)
    finally:
        D.ceiling_planes = old


# ----------------------------------------------------------------------------------------- furniture (UL128)

def test_a_piece_under_the_slope_is_built_no_taller_than_the_slope_leaves():
    level = attic()["levels"][0]
    piece = {"id": "f", "type": "wardrobe", "footprint": {"center": [1.0, 3.0], "size": [1.0, 0.6],
                                                          "rotation_deg": 0.0}}
    cap = F.under_roof_cap(level, piece, 3.0)
    # the lowest ceiling over its footprint: y = 3.3 -> 4.35 m world, 1.35 m over the floor, 2 cm under it
    assert cap == pytest.approx(1.33, abs=1e-3)
    assert F.under_roof_cap({"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}, piece, 0.0) is None
    assert F.under_roof_cap(level, dict(piece, type="stair"), 3.0) is None
    assert F.fitted_height({"method": "library", "bbox_m": [1.0, 0.6, 2.02]}) == 2.02
    assert F.fitted_height({"method": "parametric", "bbox_m": [1.0, 0.6, 2.02]}) is None
    assert F.slope_top_z(level, [([1.0, 1.0], (0.2, 0.2), 0.0)]) == pytest.approx(3.0 + 2.45 - 0.02, abs=1e-3)
    # a room open to the sky (a terrace past the roof: the planes run on over it) has no ceiling to stay under
    terrace = dict(level, open_rooms=["r_terrace"])
    assert F.under_roof_cap(terrace, dict(piece, room_id="r_terrace"), 3.0) is None
    assert F.slope_top_z(terrace, [([1.0, 5.0], (0.2, 0.2), 0.0)], "r_terrace") is None
    b = attic()
    b["levels"][0]["open_rooms"] = ["r_terrace"]
    b["decor"] = [{"id": "pot", "type": "plant_large", "level_id": "L1", "room_id": "r_terrace", "host_id": None,
                   "center": [1.0, 5.5], "size": [0.5, 0.5, 1.6], "rotation_deg": 0.0}]
    decor, _w, not_built = B.decor_under_roof(b, b["levels"][0])
    assert not not_built and decor == b["decor"]


# -------------------------------------------------------------------------- the door parts' boxes (X2, M31)

def test_a_door_part_box_is_tight_at_any_wall_angle():
    import math

    pts = []
    for ang in (0.0, 30.0):
        r = math.radians(ang)
        pts = [(math.cos(r) * x - math.sin(r) * y, math.sin(r) * x + math.cos(r) * y, z)
               for x in (-0.4, 0.4) for y in (-0.05, 0.05) for z in (0.0, 2.0)]
        assert B.tight_rotation(pts) % 90.0 == pytest.approx(ang % 90.0)
    assert "door" in B.BOX3D_OPENING_KINDS


# ------------------------------------------------------------------------------------------- the real04 case

def _real04(name):
    path = RUN / name
    if not path.is_file():
        pytest.skip(f"{path} not on this machine")
    return json.loads(path.read_text(encoding="utf-8"))


def test_real04_doors_and_decor_under_its_roof():
    """real04 run 20261029-201533-full: d_L1_001 / 002 (2.10 m under 1.84 m, D5's "2.10 m kept") and the bathroom doors
    d_L1_004 / 005 (2.10 m under 1.03 m) crossed the roof; the rule lowers the first two to their 1.80 m head room
    and the bathroom doors to theirs with a finding (no spot along their wall leaves 1.60 m); the run's crossing
    decor (towel rails, shelves and panels of both L1 bathrooms) is what the check names."""
    b = _real04("renders/real04/building_built.json")
    changes = {c["id"]: c for c in DS.plan_under_roof(b)}
    assert set(changes) == {"d_L1_001", "d_L1_002", "d_L1_004", "d_L1_005"}
    assert changes["d_L1_001"]["fits"] and changes["d_L1_001"]["height"] == pytest.approx(1.80, abs=0.01)
    assert not changes["d_L1_004"]["fits"] and changes["d_L1_004"]["height"] < 1.1
    manifest = _real04("renders/real04/scene_manifest.json")
    got = {c["target"]: c for c in UR.crossings(manifest["objects"], b)}
    assert {"dec_L1_066", "dec_L1_067", "dec_L1_068", "dec_L1_076", "dec_L1_077", "dec_L1_078"} <= set(got)
    assert all(got[t]["through_roof"] for t in ("dec_L1_066", "dec_L1_067", "dec_L1_068"))
    level = next(lv for lv in b["levels"] if lv["id"] == "L1")
    decor, _w, not_built = B.decor_under_roof(b, level)
    gone = {n["id"] for n in not_built}
    assert {"dec_L1_066", "dec_L1_067", "dec_L1_076", "dec_L1_077"} <= gone
    panel = next(d for d in decor if d.get("id") == "dec_L1_068")
    assert panel["size"][2] < 1.87
