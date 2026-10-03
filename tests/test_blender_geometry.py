"""CPU tests of the bpy-free parts of wenart.blender: solid primitives, proxy
geometry, wall overlap trimming, opening defaults, camera placement, the
manifest schemas and the Blender-binary lookup. No Blender needed.

Milestone 7 (docs/milestone7.md §6.4, §11 L): the stair plan (risers from the
drawn lines, climbing order, landing, void, rails, assumptions), polygons
with holes for the cut ceiling, the void shaft and cap, doorless openings,
virtual separators, dining / prayer slots and the site summary. The real01
stair fixture (``real01_stair_piece``, ``HALL_WALLS``, ``HALL``) is shared
with tests/test_blender_build.py and tests/test_blender_furniture.py."""
import json
import math
import stat
from pathlib import Path

import pytest
from shapely.geometry import Point, Polygon, box as shapely_box
from shapely.ops import unary_union

from wenart import geometry as G
from wenart.blender import build as B
from wenart.blender import cameras, cli, geom2d, lighting, proxies, schemas, shell
from wenart.blender import parametric as P
from wenart.blender.materials import FLAT_COLOURS, ROUGHNESS

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "projects" / "synthetic-01" / "truth" / "building.json"
STYLE_FIXTURE = ROOT / "tests" / "fixtures" / "blender_style.json"


@pytest.fixture(scope="module")
def building():
    return json.loads(TRUTH.read_text(encoding="utf-8"))


def _outward(verts, faces, centre):
    for f in faces:
        n = geom2d.face_normal(verts, f)
        c = geom2d.face_center(verts, f)
        yield (c[0] - centre[0]) * n[0] + (c[1] - centre[1]) * n[1] + (c[2] - centre[2]) * n[2]


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rotation", [0.0, 37.0, 90.0, 270.0])
def test_box_faces_point_outwards(rotation):
    centre = (2.0, -1.0, 0.5)
    verts, faces = geom2d.box(centre, (2.0, 0.5, 1.0), rotation)
    assert len(verts) == 8 and len(faces) == 6
    assert all(d > 0 for d in _outward(verts, faces, centre))
    xs = [v[2] for v in verts]
    assert min(xs) == pytest.approx(0.0) and max(xs) == pytest.approx(1.0)


def test_wedge_apex_direction_and_normals():
    verts, faces = geom2d.wedge((0.0, 0.0, 0.0), 0.2, 0.1, 0.06, 0.0)
    apex = verts[2]
    assert apex[1] == pytest.approx(-0.1) and apex[0] == pytest.approx(0.0)
    centre = (0.0, -0.03, 0.0)
    assert all(d > 0 for d in _outward(verts, faces, centre))
    # Rotated so the apex points along +X (front_deg 0 -> rotation 0 - 270).
    verts, _ = geom2d.wedge((0.0, 0.0, 0.0), 0.2, 0.1, 0.06, -270.0)
    assert verts[2][0] == pytest.approx(0.1) and abs(verts[2][1]) < 1e-9


def test_polygon_face_orientation():
    poly = [(0, 0), (2, 0), (2, 1), (0, 1)]
    verts, faces = geom2d.polygon_face(poly, 3.0, facing_up=True)
    assert geom2d.face_normal(verts, faces[0])[2] > 0
    verts, faces = geom2d.polygon_face(poly, 3.0, facing_up=False)
    assert geom2d.face_normal(verts, faces[0])[2] < 0
    verts, faces = geom2d.polygon_face(poly[::-1], 0.0)  # clockwise input is fixed
    assert geom2d.face_normal(verts, faces[0])[2] > 0


def test_box_uv_uses_the_two_non_dominant_axes():
    assert geom2d.box_uv((1.0, 2.0, 3.0), (0, 0, 1)) == (1.0, 2.0)
    assert geom2d.box_uv((1.0, 2.0, 3.0), (1, 0, 0)) == (2.0, 3.0)
    assert geom2d.box_uv((1.0, 2.0, 3.0), (0, -1, 0)) == (1.0, 3.0)


# --------------------------------------------------------------------------
# Proxies
# --------------------------------------------------------------------------

def test_proxy_height_table_matches_the_spec():
    expected = {"sofa": 0.85, "armchair": 0.85, "table_dining": 0.75, "table_coffee": 0.45, "desk": 0.75,
                "chair": 0.9, "wardrobe": 2.1, "bookshelf": 1.8, "tv_unit": 0.5, "nightstand": 0.5,
                "dresser": 0.8, "kitchen_counter": 0.9, "kitchen_island": 0.9, "fridge": 1.8, "stove": 0.9,
                "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.4, "shower": 2.0, "bathtub": 0.55,
                "washing_machine": 0.85, "unknown": 0.8, "bed_single": 0.55, "bed_double": 0.55}
    for k, v in expected.items():
        assert proxies.PROXY_HEIGHTS[k] == v
    assert proxies.proxy_height("sofa", None) == (0.85, True)
    assert proxies.proxy_height("sofa", 0.7) == (0.7, False)
    assert proxies.proxy_height("something_new", None) == (0.8, True)


@pytest.mark.parametrize("rotation,front,expected_apex", [
    (0.0, 270.0, (2.0, 3.0 - 0.3 - 0.1)),      # front = local -Y
    (180.0, 90.0, (2.0, 3.0 + 0.3 + 0.1)),     # tv unit turned around
    (90.0, 0.0, (2.0 + 0.3 + 0.1, 3.0)),       # rotated 90: depth now along X
    (270.0, 180.0, (2.0 - 0.3 - 0.1, 3.0)),
])
def test_proxy_geometry_box_and_wedge(rotation, front, expected_apex):
    piece = {"id": "f", "type": "sofa", "footprint": {"center": [2.0, 3.0], "size": [1.0, 0.6], "rotation_deg": rotation},
             "front_deg": front, "height": None}
    geo = proxies.proxy_geometry(piece, floor_z=1.0)
    assert geo["height"] == 0.85 and geo["height_assumed"]
    verts, _faces = geo["box"]
    zs = [v[2] for v in verts]
    assert min(zs) == pytest.approx(1.0) and max(zs) == pytest.approx(1.85)
    # The box corners are the rotated footprint corners.
    corners = {(round(x, 6), round(y, 6)) for x, y in G.rotated_rectangle([2.0, 3.0], [1.0, 0.6], rotation)}
    assert {(round(v[0], 6), round(v[1], 6)) for v in verts} == corners
    apex = geo["wedge"][0][2]
    assert apex[0] == pytest.approx(expected_apex[0]) and apex[1] == pytest.approx(expected_apex[1])


def test_proxy_without_front_has_no_wedge():
    piece = {"id": "f", "type": "unknown", "footprint": {"center": [0, 0], "size": [1, 1], "rotation_deg": 0},
             "front_deg": None}
    assert proxies.proxy_geometry(piece, 0.0)["wedge"] is None


def test_footprints_overlap():
    a = {"center": [0, 0], "size": [2, 1], "rotation_deg": 0}
    assert proxies.footprints_overlap(a, {"center": [0.5, 0.2], "size": [0.6, 0.6], "rotation_deg": 0})
    assert not proxies.footprints_overlap(a, {"center": [1.5, 0], "size": [0.9, 0.9], "rotation_deg": 0})
    assert not proxies.footprints_overlap(a, {"center": [0, 1.0], "size": [2, 0.9], "rotation_deg": 0})
    assert proxies.footprints_overlap(a, {"center": [1.2, 0], "size": [0.2, 1.0], "rotation_deg": 45})


# --------------------------------------------------------------------------
# Walls and openings
# --------------------------------------------------------------------------

def _union(walls, trims=None):
    polys = []
    for w in walls:
        s, e = (trims[w["id"]]["start"], trims[w["id"]]["end"]) if trims else (w["start"], w["end"])
        polys.append(Polygon(G.centerline_to_rectangle(s, e, w["thickness"])))
    return unary_union(polys)


def test_trim_wall_overlaps_keeps_the_union_and_removes_overlaps(building):
    walls = [w for w in building["walls"] if w["level_id"] == "L0"]
    trims = shell.trim_wall_overlaps(walls)
    before, after = _union(walls), _union(walls, trims)
    assert after.area == pytest.approx(before.area, abs=1e-6)
    assert after.symmetric_difference(before).area < 1e-6
    trimmed = [i for i, t in trims.items() if t["trimmed"]]
    assert trimmed, "exterior corners should be trimmed"
    assert all(not trims[w["id"]]["trimmed"] for w in walls if not w.get("exterior"))
    # No two trimmed rectangles overlap in area any more.
    rects = [Polygon(G.centerline_to_rectangle(trims[w["id"]]["start"], trims[w["id"]]["end"], w["thickness"]))
             for w in walls]
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            assert a.intersection(b).area < 1e-6


def test_opening_defaults_are_recorded_as_assumed():
    level = {"elevation": 3.0, "ceiling_height": 2.7}
    b, t, a = shell.opening_vertical({"type": "door", "width": 0.9, "height": None, "sill_height": None}, level, True)
    assert (b, t) == (3.0, pytest.approx(5.1)) and a == {"height": 2.1}
    b, t, a = shell.opening_vertical({"type": "window", "width": 1.2, "height": None, "sill_height": None}, level, False)
    assert (b, t) == (pytest.approx(3.9), pytest.approx(5.1)) and a == {"sill_height": 0.9, "height": 1.2}
    _b, t, a = shell.opening_vertical({"type": "window", "width": 1.8, "height": None, "sill_height": None}, level, False)
    assert t == pytest.approx(5.3) and a["height"] == 1.4
    b, t, a = shell.opening_vertical({"type": "opening", "width": 1.0, "height": None, "sill_height": None}, level, False)
    assert b == 3.0 and t == pytest.approx(5.7) and a == {"height": pytest.approx(2.7)}  # full wall height
    # Doors and windows taller than the ceiling are clamped just below it.
    _b, t, a = shell.opening_vertical({"type": "door", "width": 0.9, "height": 3.0, "sill_height": 0.0}, level, False)
    assert t == pytest.approx(5.699) and a == {}
    _b, t, a = shell.opening_vertical({"type": "door", "width": 0.9, "height": 2.0, "sill_height": 0.0}, level, False)
    assert t == pytest.approx(5.0) and a == {}
    h, a = shell.wall_height({"height": None}, level, True)
    assert h == pytest.approx(3.0) and a == {"height": 2.7, "slab_thickness": 0.3}
    h, a = shell.wall_height({"height": 2.5}, level, False)
    assert h == 2.5 and a == {}


def test_opening_centre_is_projected_onto_the_wall_line():
    wall = {"id": "w", "start": [0.0, 7.075], "end": [9.6, 7.075], "thickness": 0.25}
    # A door block inserted on the wall face (y = 7.2): the cutter must still sit on the centre line.
    cx, cy, shift = shell.opening_centre_on_wall({"center": [6.15, 7.195]}, wall)
    assert (cx, cy) == (pytest.approx(6.15), pytest.approx(7.075)) and shift == pytest.approx(0.12)
    cx, cy, shift = shell.opening_centre_on_wall({"center": [6.15, 7.075]}, wall)
    assert (cx, cy) == (pytest.approx(6.15), pytest.approx(7.075)) and shift == pytest.approx(0.0)
    # Diagonal wall: the projection keeps the position along the wall.
    wall = {"id": "w", "start": [0.0, 0.0], "end": [4.0, 4.0], "thickness": 0.1}
    cx, cy, shift = shell.opening_centre_on_wall({"center": [2.0 + 0.05, 2.0 - 0.05]}, wall)
    assert (cx, cy) == (pytest.approx(2.0), pytest.approx(2.0)) and shift == pytest.approx(0.05 * math.sqrt(2))


def test_wall_outward_side_on_an_l_shaped_footprint():
    """10 x 10 m envelope with the quadrant x 3..10, y 3..10 cut out: the bbox
    centre (5, 5) lies outside the building, so the old centre rule flipped
    the two re-entrant exterior walls. Probing the room polygons decides."""
    t = 0.25
    rooms = [{"id": "a", "polygon": [[t, t], [3.0 - t, t], [3.0 - t, 10.0 - t], [t, 10.0 - t]]},
             {"id": "b", "polygon": [[3.0 - t, t], [10.0 - t, t], [10.0 - t, 3.0 - t], [3.0 - t, 3.0 - t]]}]
    # Re-entrant walls on the centre lines y = 2.875 (x 3..10) and x = 2.875 (y 3..10), both drawing directions.
    for start, end, expected in (([3.0, 2.875], [10.0, 2.875], (0.0, 1.0)), ([10.0, 2.875], [3.0, 2.875], (0.0, 1.0)),
                                 ([2.875, 3.0], [2.875, 10.0], (1.0, 0.0)), ([2.875, 10.0], [2.875, 3.0], (1.0, 0.0)),
                                 ([0.0, 0.125], [10.0, 0.125], (0.0, -1.0))):
        wall = {"id": "w", "start": start, "end": end, "thickness": t, "exterior": True}
        outward, ambiguous = shell.wall_outward_normal(wall, rooms, (5.0, 5.0))
        assert not ambiguous
        assert outward[0] == pytest.approx(expected[0]) and outward[1] == pytest.approx(expected[1]), (start, end)
    # No room on either side: fall back to the centre rule and say so.
    wall = {"id": "w", "start": [3.0, 2.875], "end": [10.0, 2.875], "thickness": t, "exterior": True}
    outward, ambiguous = shell.wall_outward_normal(wall, [], (5.0, 5.0))
    assert ambiguous and outward[1] == pytest.approx(-1.0)


# --------------------------------------------------------------------------
# Cameras
# --------------------------------------------------------------------------

def test_three_cameras_per_room_inside_the_room(building):
    plans = cameras.plan_cameras(building, "L0")
    rooms = {r["id"]: r for r in building["rooms"] if r["level_id"] == "L0"}
    assert len(plans) == 3 * len(rooms)
    per_room = {}
    for plan in plans:
        per_room.setdefault(plan["room_id"], []).append(plan["index"])
        room = rooms[plan["room_id"]]
        assert plan["name"] == f"cam_{room['id']}_{plan['index']}"
        assert plan["position"][2] == pytest.approx(1.4) and plan["lens_mm"] == 24 and plan["sensor_mm"] == 36
        assert plan["resolution"] == [1920, 1080]
        assert Polygon(room["polygon"]).buffer(1e-6).contains(
            __import__("shapely.geometry", fromlist=["Point"]).Point(plan["position"][:2]))
    assert all(sorted(v) == [1, 2, 3] for v in per_room.values())


def test_free_area_camera_keeps_clearances(building):
    plans = cameras.plan_cameras(building, "L0")
    rooms = {r["id"]: r for r in building["rooms"]}
    furniture = building["furniture"]
    for plan in plans:
        if plan["index"] != 1 or plan["warning"]:
            continue
        room = Polygon(rooms[plan["room_id"]]["polygon"])
        pt = __import__("shapely.geometry", fromlist=["Point"]).Point(plan["position"][:2])
        assert room.exterior.distance(pt) >= 0.5 - 1e-6
        for f in furniture:
            if f["room_id"] != plan["room_id"]:
                continue
            fp = f["footprint"]
            box = Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))
            assert box.distance(pt) >= 0.3 - 1e-6


def test_door_and_window_cameras_use_the_room_openings(building):
    plans = {p["name"]: p for p in cameras.plan_cameras(building, "L0")}
    openings = {o["id"]: o for o in building["openings"]}
    salon_door = plans["cam_r_L0_salon_2"]
    assert salon_door["anchor"] in openings and openings[salon_door["anchor"]]["type"] == "door"
    assert G.distance(salon_door["position"][:2], openings[salon_door["anchor"]]["center"]) < 0.6
    salon_win = plans["cam_r_L0_salon_3"]
    assert openings[salon_win["anchor"]]["type"] == "window"
    assert salon_win["warning"] is None
    # The hall has no window: fallback at the centroid with a warning.
    hol = plans["cam_r_L0_hol_3"]
    assert hol["warning"] and "window" in hol["warning"]
    centroid = G.polygon_centroid([r for r in building["rooms"] if r["id"] == "r_L0_hol"][0]["polygon"])
    assert G.distance(hol["position"][:2], centroid) < 1e-6


def test_frustum_lists_are_subsets_of_the_room(building):
    plans = cameras.plan_cameras(building, "L0")
    by_room_f = {}
    for f in building["furniture"]:
        by_room_f.setdefault(f["room_id"], set()).add(f["id"])
    for plan in plans:
        assert set(plan["visible_furniture"]) <= by_room_f.get(plan["room_id"], set())
    # The window camera of the salon looks across the room and sees the sofa.
    salon_3 = next(p for p in plans if p["name"] == "cam_r_L0_salon_3")
    assert "f_L0_001" in salon_3["visible_furniture"]


def test_point_in_frustum():
    tangents = geom2d.frustum_tangents(24.0, 36.0, (1920, 1080))
    assert tangents[0] == pytest.approx(0.75) and tangents[1] == pytest.approx(0.75 * 1080 / 1920)
    pos, tgt = (0, 0, 1.4), (5, 0, 1.3)
    assert geom2d.point_in_frustum((3, 1, 1.0), pos, tgt, tangents)
    assert not geom2d.point_in_frustum((-1, 0, 1.0), pos, tgt, tangents)      # behind
    assert not geom2d.point_in_frustum((2, 3, 1.0), pos, tgt, tangents)       # outside horizontally
    assert not geom2d.point_in_frustum((2, 0, 3.5), pos, tgt, tangents)       # outside vertically


def test_point_in_frustum_with_lens_shift():
    """docs/milestone6.md §1.3: shift_y -0.10 moves the frame down by 2 tan(h/2) 0.10 = 0.15 in slope,
    shift_x > 0 moves it to the right; the frustum tangents themselves do not change."""
    tangents = geom2d.frustum_tangents(24.0, 36.0, (1920, 1080))
    pos, tgt = (0.0, 0.0, 1.25), (5.0, 0.0, 1.25)                 # level camera looking +X (right = -Y)
    low = (4.0, 0.0, 1.25 - 1.9)                                   # slope -0.475: below the plain frame
    assert not geom2d.point_in_frustum(low, pos, tgt, tangents)
    assert geom2d.point_in_frustum(low, pos, tgt, tangents, shift_y=-0.10)          # frame -0.572 .. 0.272
    high = (4.0, 0.0, 1.25 + 1.4)                                  # slope 0.35
    assert geom2d.point_in_frustum(high, pos, tgt, tangents)
    assert not geom2d.point_in_frustum(high, pos, tgt, tangents, shift_y=-0.10)
    right = (4.0, -3.5, 1.25)                                      # slope 0.875 to the right
    assert not geom2d.point_in_frustum(right, pos, tgt, tangents)
    assert geom2d.point_in_frustum(right, pos, tgt, tangents, shift_x=0.10)         # frame -0.6 .. 0.9
    assert not geom2d.point_in_frustum((-1.0, 0.0, 1.25), pos, tgt, tangents, shift_y=-0.10)   # behind


@pytest.mark.parametrize("shift", [(0.0, 0.0), (0.0, -0.10), (0.07, -0.10)])
def test_frustum_agrees_with_the_pixel_projection(shift):
    """A point is in the shifted frustum exactly when ``expected.project_points`` puts it in the frame."""
    import numpy as np

    from wenart.vision_check import expected

    rng = np.random.default_rng(3)
    tangents = geom2d.frustum_tangents(24.0, 36.0, (1920, 1080))
    camera = {"position": [1.0, 2.0, 1.4], "target": [4.0, 3.0, 1.3], "lens_mm": 24.0, "sensor_mm": 36.0,
              "shift_x": shift[0], "shift_y": shift[1]}
    pts = rng.uniform([-3, -3, -1], [9, 9, 4], size=(4000, 3))
    uv, z = expected.project_points(pts, camera, (1920, 1080))
    inside_px = (z > 0.05) & (uv[:, 0] >= 0) & (uv[:, 0] <= 1920) & (uv[:, 1] >= 0) & (uv[:, 1] <= 1080)
    inside = [geom2d.point_in_frustum(tuple(p), camera["position"], camera["target"], tangents,
                                      shift_x=shift[0], shift_y=shift[1]) for p in pts]
    assert inside_px.sum() > 300
    assert list(inside_px) == inside


def test_sun_direction():
    x, y, z = lighting.sun_direction(90.0, 0.0)
    assert z == pytest.approx(1.0) and abs(x) < 1e-9 and abs(y) < 1e-9
    x, y, z = lighting.sun_direction(0.0, 90.0)   # east
    assert x == pytest.approx(1.0) and abs(y) < 1e-9 and abs(z) < 1e-9
    x, y, z = lighting.sun_direction(35.0, 210.0)  # south-south-west, above the horizon
    assert x < 0 and y < 0 and z == pytest.approx(math.sin(math.radians(35)))


# --------------------------------------------------------------------------
# Schemas, style fixture, binary lookup
# --------------------------------------------------------------------------

def test_scene_manifest_schema_accepts_minimal_and_rejects_bad():
    manifest = {
        "schema_version": "0.1", "project": "p", "building": "b.json", "style": None, "blender_version": "5.2.2",
        "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
        "objects": [{"name": "w_L0_001", "wenart_id": "w_L0_001", "kind": "wall", "status": "verified",
                     "evidence": [{"file": "a.dxf", "method": "vector", "confidence": 1.0}], "material": "plaster_white",
                     "textured": False, "pass_index": None, "assumed": {}}],
        "cameras": [{"name": "cam_r_1", "room_id": "r", "level_id": "L0", "index": 1, "position": [0, 0, 1.4],
                     "target": [1, 0, 1.3], "lens_mm": 24, "sensor_mm": 36, "resolution": [1920, 1080],
                     "visible_openings": [], "visible_furniture": [], "warning": None}],
        "materials": {"plaster_white": {"textured": False, "asset": None, "reason": "flat"}},
        "pass_index": {"proxy:f_L0_001": 1}, "assumed": [], "warnings": [], "checks": {"door_rays": []}, "previews": {},
        "preview_maps": {}, "build_fingerprint": "0" * 64,
    }
    schemas.validate_scene_manifest(manifest)
    bad = dict(manifest)
    bad["objects"] = [dict(manifest["objects"][0], kind="sofa")]
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(bad)
    # Milestone 5: preview_maps and build_fingerprint are required; doors/windows carry room_ids,
    # furniture/proxies/decor carry box3d.
    for key in ("preview_maps", "build_fingerprint"):
        with pytest.raises(Exception):
            schemas.validate_scene_manifest({k: v for k, v in manifest.items() if k != key})
    obj = manifest["objects"][0]
    door = dict(obj, name="d_frame", wenart_id="d", kind="door", pass_index=2)
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(dict(manifest, objects=[door]))
    schemas.validate_scene_manifest(dict(manifest, objects=[dict(door, room_ids=["r"])]))
    piece = dict(obj, name="furn_f", wenart_id="f", kind="furniture", pass_index=3)
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(dict(manifest, objects=[piece]))
    box = {"center": [1.0, 2.0, 0.4], "size": [2.0, 0.9, 0.8], "rotation_deg": 0.0}
    schemas.validate_scene_manifest(dict(manifest, objects=[dict(piece, box3d=box)]))
    schemas.validate_scene_manifest(dict(manifest, preview_maps={"L0": {
        "png": "level_L0_top.png", "bbox_m": [-0.5, -0.5, 10.1, 7.7], "m_per_px": 0.01, "resolution": [1060, 820]}}))
    exposure = {"mode": "auto", "ev": 3.5, "ev_raw": 3.52, "at_limit": False, "target": 0.9, "incident_p50": 0.08,
                "whitepoint": [1.05, 0.99, 0.95], "wb_temperature": 5600.0, "wb_tint": 10.0, "residual": 0.35,
                "window_clip_frac": 0.4, "meter_seconds": 0.9, "source": None}
    entry = {"camera": "cam", "png": "cam.png", "exr": "cam_passes.exr", "preview": "cam_preview.jpg",
             "seconds": 1.0, "samples": 16, "resolution": [320, 180],
             "depth": {"min": 1.0, "max": 5.0, "mean": 2.0}, "index_values": [1],
             "index_stats": {"1": {"pixels": 10, "box": [0, 0, 5, 2]}},
             "files": {"index": "cam_index.png", "depth_mm": "cam_depth_mm.png", "normal": "cam_normal.png"},
             "render_key": "0123456789abcdef", "exposure": exposure, "hidden": [], "plugged": []}
    render = {"schema_version": "0.1", "scene": "../scene/scene.blend", "device": "CPU", "device_requested": "auto",
              "blender_version": "5.2.2", "samples": 16, "resolution": [320, 180], "denoiser": "OPENIMAGEDENOISE",
              "pass_index": {"proxy_f": 1}, "renders": [entry]}
    schemas.validate_render_manifest(render)
    with pytest.raises(Exception):
        schemas.validate_render_manifest(dict(render, device="TPU"))
    # A Milestone 4 entry (no render_key, index_stats, files) is not an M5 render entry.
    for key in ("render_key", "index_stats", "files", "exposure", "hidden", "plugged"):
        with pytest.raises(Exception):
            schemas.validate_render_manifest(dict(render, renders=[{k: v for k, v in entry.items() if k != key}]))
    with pytest.raises(Exception):
        schemas.validate_render_manifest(dict(render, renders=[dict(entry, exposure=dict(exposure, mode="magic"))]))


def test_style_fixture_slugs_have_flat_colours():
    style = json.loads(STYLE_FIXTURE.read_text(encoding="utf-8"))
    for key in ("floor", "walls", "ceiling", "wet_floor", "wet_walls", "trim", "door", "window_frame"):
        slug = style[key]["material"]
        assert slug in FLAT_COLOURS and slug in ROUGHNESS, slug
    assert set(style["lighting"]) >= {"hdri", "sun_elevation_deg", "sun_azimuth_deg", "sun_strength",
                                      "colour_temperature_k", "mood"}


def test_find_blender_prefers_env(tmp_path, monkeypatch):
    fake = tmp_path / "blender"
    fake.write_text("#!/bin/sh\necho fake\n")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("WENART_BLENDER", str(fake))
    assert cli.find_blender() == str(fake)
    # A missing env path is ignored: the candidates decide, in order, then PATH.
    monkeypatch.setenv("WENART_BLENDER", str(tmp_path / "missing"))
    first, second, on_path = tmp_path / "ws" / "blender", tmp_path / "opt" / "blender", tmp_path / "bin" / "blender"
    for exe in (first, second, on_path):
        exe.parent.mkdir()
        exe.write_text("#!/bin/sh\necho fake\n")
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setattr(cli, "CANDIDATES", (str(first), str(second)))
    monkeypatch.setenv("PATH", str(on_path.parent))
    assert cli.find_blender() == str(first)
    first.unlink()
    assert cli.find_blender() == str(second)
    second.unlink()
    assert cli.find_blender() == str(on_path)
    on_path.unlink()
    assert cli.find_blender() is None


# --------------------------------------------------------------------------
# Milestone 7: stairs, ceiling openings, doorless openings, separators, site (docs/milestone7.md §6.4)
# --------------------------------------------------------------------------

FT = 0.3048


def _ft(x: float, y: float) -> list[float]:
    return [x * FT, y * FT]


def real01_stair_piece(direction=(0.0, 1.0), **stair_extra) -> dict:
    """The stair F19 of tests/fixtures/real01_reference.yaml as the recognition core writes it
    (``details.stair``, docs/milestone7.md §2.8): two flights of 8 tread lines side by side
    (x 11.252-13.751 and 13.751-16.26 ft, lines y 15.257-21.085 ft, 0.833 ft apart), the landing
    y 21.085-23.257 ft, direction assumed (flight 1 start to end)."""
    flights = [{"start": _ft(12.5015, 15.257), "end": _ft(12.5015, 21.085), "width": 2.499 * FT, "lines": 8,
                "spacing": 0.833 * FT},
               {"start": _ft(15.0055, 15.257), "end": _ft(15.0055, 21.085), "width": 2.509 * FT, "lines": 8,
                "spacing": 0.833 * FT}]
    stair = {"flights": flights,
             "landing": {"polygon": [_ft(11.252, 21.085), _ft(16.26, 21.085), _ft(16.26, 23.257),
                                     _ft(11.252, 23.257)], "depth": 2.172 * FT},
             "direction": None if direction is None else list(direction), "direction_assumed": True, "turn": "U",
             "turn_assumed": True, "void_assumed": True, "riser_m": None, "riser_source": None,
             "reason": "no UP arrow, break line or riser text drawn"}
    stair.update(stair_extra)
    return {"id": "f_L0_019", "level_id": "L0", "room_id": "r_L0_hall", "type": "stair", "type_method": "rule",
            "source": "from_documents", "status": "verified", "front_deg": None, "height": None,
            "footprint": {"center": _ft(13.756, 19.257), "size": [8.0 * FT, 5.008 * FT], "rotation_deg": 90.0},
            "evidence": [{"file": "real01.pdf", "page": 1, "method": "vector", "confidence": 0.9}],
            "details": {"stair": stair}}


# The stair hall's walls (centre lines, 9 inch) and the hall face of the reference (one merged face).
HALL_WALLS = [
    {"id": "w_L0_w", "level_id": "L0", "start": _ft(11.006, 8.005), "end": _ft(11.006, 23.503), "thickness": 0.492 * FT},
    {"id": "w_L0_e", "level_id": "L0", "start": _ft(16.506, 8.005), "end": _ft(16.506, 23.503), "thickness": 0.492 * FT},
    {"id": "w_L0_n", "level_id": "L0", "start": _ft(10.76, 23.503), "end": _ft(16.752, 23.503), "thickness": 0.492 * FT},
    {"id": "w_L0_s", "level_id": "L0", "start": _ft(10.76, 8.005), "end": _ft(16.752, 8.005), "thickness": 0.492 * FT},
]
HALL = {"id": "r_L0_hall", "level_id": "L0", "label": "Room", "room_type": "hall", "status": "unverified",
        "polygon": [_ft(11.252, 8.251), _ft(16.26, 8.251), _ft(16.26, 23.257), _ft(11.252, 23.257)],
        "evidence": [{"file": "real01.pdf", "method": "derived", "confidence": 0.7}]}
LEVEL0 = {"id": "L0", "label": "Ground floor", "elevation": 0.0, "ceiling_height": 2.7,
          "ceiling_height_source": "assumed_default"}
TREAD_LINES_FT = [15.257, 16.087, 16.916, 17.756, 18.586, 19.416, 20.255, 21.085]   # the reference's tread lines


def _real01_plan(**kw):
    return P.stair_plan(real01_stair_piece(**kw), 2.85, 2.70, walls=HALL_WALLS)


def _closed_and_outward(part) -> bool:
    verts, faces = part["verts"], part["faces"]
    n = float(len(verts))
    centre = tuple(sum(v[i] for v in verts) / n for i in range(3))
    edges = {}
    for f in faces:
        nrm, c = geom2d.face_normal(verts, f), geom2d.face_center(verts, f)
        if nrm == (0.0, 0.0, 0.0) or sum(nrm[i] * (c[i] - centre[i]) for i in range(3)) <= 0:
            return False
        for i in range(len(f)):
            edges[(f[i], f[(i + 1) % len(f)])] = edges.get((f[i], f[(i + 1) % len(f)]), 0) + 1
    return all(k == 1 and edges.get((b, a)) == 1 for (a, b), k in edges.items())


def test_stair_risers_are_the_drawn_lines():
    """Every drawn tread line is a nosing: 8 lines = 8 risers and 7 treads per flight, never one more or less;
    riser = (ceiling 2.70 + assumed slab 0.15) / 16, recorded with its source."""
    plan = _real01_plan()
    rh = 2.85 / 16
    assert plan["risers"] == 16 and plan["riser_m"] == pytest.approx(rh)
    assert plan["riser_source"] == "derived from assumed ceiling and slab"
    assert not [w for w in plan["warnings"] if "outside" in w]
    parts = P.stair_parts(plan)
    assert all(_closed_and_outward(p) for p in parts)
    for f in plan["flights"]:
        steps = [p for p in parts if p["role"] == "step" and p["flight"] == f["index"]]
        plates = [p for p in parts if p["role"] == "riser" and p["flight"] == f["index"]]
        assert len(steps) == f["lines"] - 1 == 7 and len(plates) == 1
        tops = sorted(max(v[2] for v in p["verts"]) for p in steps + plates)
        assert tops == pytest.approx([f["base_z"] + k * rh for k in range(1, f["lines"] + 1)])
        # The nosings are the drawn lines (the flight record keeps the first and last line and the count; the
        # stair rule only accepts evenly spaced lines, real01's within 2 mm), each tread runs from one to the next.
        assert sorted(round(y / FT, 3) for _, y in f["nosings"]) == pytest.approx(TREAD_LINES_FT, abs=0.01)
        assert f["nosings"][0][1] / FT in (pytest.approx(15.257), pytest.approx(21.085))
        for p in steps:
            top = max(v[2] for v in p["verts"])
            along = [v[0] * f["rise_dir"][0] + v[1] * f["rise_dir"][1] for v in p["verts"] if abs(v[2] - top) < 1e-9]
            assert max(along) - min(along) == pytest.approx(f["going"], abs=1e-9)
            assert min(v[2] for v in p["verts"]) >= -1e-12                     # never below the floor
    # Rule of thumb for the derived riser: outside 0.15-0.20 m is a warning, never a silent change.
    short = real01_stair_piece()
    for fl in short["details"]["stair"]["flights"]:
        fl["lines"] = 5
    plan = P.stair_plan(short, 2.85, 2.70)
    assert plan["risers"] == 10 and plan["riser_m"] == pytest.approx(0.285)
    assert [w for w in plan["warnings"] if "riser 0.285 m outside 0.15-0.20 m" in w]


def test_stair_flights_rise_in_turn_towards_and_from_the_landing():
    plan = _real01_plan()
    rh = 2.85 / 16
    a, b = plan["flights"]
    assert a["index"] == 0 and a["rise_dir"] == pytest.approx((0.0, 1.0)) and a["base_z"] == 0.0
    assert a["top_z"] == pytest.approx(8 * rh)
    assert b["index"] == 1 and b["rise_dir"] == pytest.approx((0.0, -1.0))
    assert b["base_z"] == pytest.approx(a["top_z"]) and b["top_z"] == pytest.approx(2.85)
    assert plan["landing"]["role"] == "mid" and plan["landing"]["z"] == pytest.approx(8 * rh)
    assert plan["direction"] == [0.0, 1.0] and plan["turn"] == "U"
    by_kind = {e["kind"]: e for e in plan["assumed"]}
    assert set(by_kind) == {"stair_direction", "stair_turn", "stair_riser", "stair_void", "stair_handrail",
                            "stair_structure"}
    assert by_kind["stair_direction"]["reason"] == "no UP arrow, break line or riser text drawn"
    assert all(set(e) == {"field", "kind", "value", "reason"} for e in plan["assumed"])
    # The other reading: flight 1 rises south, away from the landing, so flight 2 climbs first.
    other = _real01_plan(direction=(0.0, -1.0))
    assert [f["index"] for f in other["flights"]] == [1, 0]
    assert other["flights"][0]["rise_dir"] == pytest.approx((0.0, 1.0))
    assert other["flights"][1]["rise_dir"] == pytest.approx((0.0, -1.0)) and other["flights"][1]["top_z"] == 2.85
    # A drawn direction is not an assumption.
    drawn = _real01_plan(direction_assumed=False)
    assert "stair_direction" not in {e["kind"] for e in drawn["assumed"]}


def test_stair_without_a_direction_rises_along_local_y():
    piece = {"id": "f_s", "type": "stair", "footprint": {"center": [2.0, 1.5], "size": [1.0, 2.8], "rotation_deg": 0.0},
             "stair": {"flights": [{"start": [2.0, 0.15], "end": [2.0, 2.85], "width": 1.0, "lines": 16}],
                       "landing": None, "direction": None}}
    plan = P.stair_plan(piece, 2.85)
    assert plan["flights"][0]["rise_dir"] == pytest.approx((0.0, 1.0))
    entry = next(e for e in plan["assumed"] if e["kind"] == "stair_direction")
    assert "+local Y" in entry["reason"]
    piece["footprint"]["rotation_deg"] = 180.0                       # local +Y is world -Y
    plan = P.stair_plan(piece, 2.85)
    assert plan["flights"][0]["rise_dir"] == pytest.approx((0.0, -1.0))
    assert plan["flights"][0]["nosings"][0] == pytest.approx((2.0, 2.85))
    assert plan["landing"] is None and plan["turn"] == "straight"


def test_stair_without_drawn_flights_is_one_assumed_flight():
    piece = {"id": "f_ai", "type": "stair", "footprint": {"center": [2.0, 3.0], "size": [1.0, 3.0], "rotation_deg": 0.0}}
    plan = P.stair_plan(piece, 2.85)
    assert plan["generic"] and len(plan["flights"]) == 1 and plan["risers"] == round(2.85 / P.STAIR_GENERIC_RISER_M)
    assert [w for w in plan["warnings"] if "no drawn flights" in w]
    assert "stair_flights" in {e["kind"] for e in plan["assumed"]}
    assert any("(assumed count)" in e["reason"] for e in plan["assumed"] if e["kind"] == "stair_riser")
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(P.stair_parts(plan))
    assert (x0, y0, x1, y1) == pytest.approx((1.5, 1.5, 2.5, 4.5)) and z0 == 0.0


def test_single_flight_landing_at_the_top_or_at_the_foot():
    flight = {"start": [0.0, 0.0], "end": [0.0, 2.5], "width": 1.0, "lines": 11}
    landing = [[-0.5, 2.5], [0.5, 2.5], [0.5, 3.4], [-0.5, 3.4]]
    piece = {"id": "f", "type": "stair", "footprint": {"center": [0.0, 1.7], "size": [1.0, 3.4], "rotation_deg": 0.0},
             "stair": {"flights": [flight], "landing": {"polygon": landing}, "direction": [0.0, 1.0]}}
    plan = P.stair_plan(piece, 2.85, 2.70)
    assert plan["landing"]["role"] == "top" and plan["landing"]["z"] == pytest.approx(2.85)
    assert Polygon(plan["void_raw"][0]).area == pytest.approx(1.0 * 3.4)        # the flight and the landing
    piece["stair"]["direction"] = [0.0, -1.0]                                    # rising away from the landing
    plan = P.stair_plan(piece, 2.85, 2.70)
    assert plan["landing"]["role"] == "floor" and plan["landing"]["z"] == 0.0
    assert not [p for p in P.stair_parts(plan) if p["role"] == "landing"]      # the floor is the landing
    assert Polygon(plan["void_raw"][0]).area == pytest.approx(1.0 * 2.5)        # the flight only


def test_stair_void_covers_the_last_flight_and_the_landing_only():
    plan = _real01_plan()
    void = Polygon(plan["void_raw"][0])
    flight_b = shapely_box(13.751 * FT, 15.257 * FT, 16.26 * FT, 21.085 * FT)
    landing = shapely_box(11.252 * FT, 21.085 * FT, 16.26 * FT, 23.257 * FT)
    assert len(plan["void_raw"]) == 1 and void.symmetric_difference(unary_union([flight_b, landing])).area < 1e-6
    assert not void.contains(Point(12.5 * FT, 18.0 * FT))                       # flight A stays under the ceiling
    grown = Polygon(plan["void"][0])
    assert grown.symmetric_difference(void.buffer(P.STAIR_SHAFT_GAP, join_style=2)).area < 1e-7
    assert plan["ceiling_z"] == 2.70 and plan["cap_z"] == pytest.approx(2.70 + P.STAIR_SHAFT_CAP_M)
    void_entry = next(e for e in plan["assumed"] if e["kind"] == "stair_void")
    assert "last flight and the landing" in void_entry["value"] and "0.50 m above the ceiling" in void_entry["value"]
    # Flight A under the ceiling: its top leaves 1.28 m of headroom, reported, nothing moved.
    assert [w for w in plan["warnings"] if w.startswith("flight 1: 1.28 m under the ceiling")]


def test_stair_handrails_on_free_sides_under_the_cap():
    plan = _real01_plan()
    # Flight A rises north: its left (west) side is against the hall wall; flight B rises south: its left
    # (east) side is against the wall. Both rails run along the divider between the flights.
    assert [(r["flight"], r["side"]) for r in plan["rails"]] == [(0, "right"), (1, "right")]
    parts = P.stair_parts(plan)
    rails = [p for p in parts if p["key"] == "steel"]
    assert {p["role"] for p in rails} == {"rail", "post"}
    for p in rails:
        xs = [v[0] / FT for v in p["verts"]]
        assert 13.751 - 0.25 < min(xs) and max(xs) < 13.751 + 0.25
        assert max(v[2] for v in p["verts"]) <= plan["cap_z"] - P.STAIR_CAP_CLEARANCE + 1e-9
    upper = [p for p in rails if p["role"] == "rail" and p["flight"] == 1]
    assert upper and max(v[2] for v in upper[0]["verts"]) == pytest.approx(plan["cap_z"] - P.STAIR_CAP_CLEARANCE)
    assert len(P.stair_plan(real01_stair_piece(), 2.85, 2.70)["rails"]) == 4     # no walls given: every side


def test_stair_face_slots_and_the_void_shaft():
    plan = _real01_plan()
    parts = P.stair_parts(plan)
    slots = P.stair_face_slots(parts)
    assert len(slots) == sum(len(p["faces"]) for p in parts)
    i = 0
    for p in parts:
        for f in p["faces"]:
            n = geom2d.face_normal(p["verts"], f)
            if p["key"] == "steel":
                assert slots[i] == 2
            elif n[2] > 0.5:
                assert slots[i] == 0                                            # treads, landing top
            elif n[2] < -0.5:
                assert slots[i] == 1                                            # soffit
            i += 1
    step = next(p for p in parts if p["role"] == "step")
    r = step["rise_dir"]
    fronts = [f for f in step["faces"] if -(geom2d.face_normal(step["verts"], f)[0] * r[0]
                                            + geom2d.face_normal(step["verts"], f)[1] * r[1]) > 0.5]
    assert len(fronts) == 1                                                     # the riser faces the climber
    verts, faces = P.void_shaft(plan)
    void = Polygon(plan["void"][0])
    walls = [f for f in faces if abs(geom2d.face_normal(verts, f)[2]) < 0.5]
    caps = [f for f in faces if geom2d.face_normal(verts, f)[2] < -0.5]
    assert len(walls) == len(plan["void"][0]) and caps
    for f in walls:                                                             # every shaft face looks into the void
        n, c = geom2d.face_normal(verts, f), geom2d.face_center(verts, f)
        assert void.contains(Point(c[0] + n[0] * 0.01, c[1] + n[1] * 0.01))
    assert min(v[2] for v in verts) == pytest.approx(2.70 - P.STAIR_SHAFT_LIP)
    assert max(v[2] for v in verts) == pytest.approx(plan["cap_z"])
    assert geom2d.faces_area(verts, caps) == pytest.approx(void.area)


def test_rect_union_outline_and_polygon_faces():
    loops = geom2d.rect_union_outline([(0, 0, 2, 1), (1, 1, 2, 3)])
    assert len(loops) == 1 and len(loops[0]) == 6 and G.polygon_signed_area(loops[0]) == pytest.approx(4.0)
    assert len(geom2d.rect_union_outline([(0, 0, 1, 1), (2, 0, 3, 1)])) == 2
    frame = geom2d.rect_union_outline([(0, 0, 3, 1), (0, 2, 3, 3), (0, 1, 1, 2), (2, 1, 3, 2)])
    assert sorted(round(G.polygon_signed_area(lp), 6) for lp in frame) == [-1.0, 9.0]   # outer ccw, hole cw
    outer = [[0, 0], [6, 0], [6, 4], [0, 4]]
    for holes, expected in (([], 24.0), ([[[1, 1], [2, 1], [2, 2], [1, 2]]], 23.0),
                            ([[[5, 3], [7, 3], [7, 5], [5, 5]]], 23.0),                    # half outside
                            ([[[1, 1], [2, 1], [2, 2], [1, 2]], [[3, 1], [5, 1], [5, 3], [3, 3]]], 19.0)):
        verts, faces = geom2d.polygon_faces(outer, holes, 2.7, facing_up=False)
        assert geom2d.faces_area(verts, faces) == pytest.approx(expected)
        assert all(geom2d.face_normal(verts, f)[2] == pytest.approx(-1.0) for f in faces)
        assert all(v[2] == 2.7 for v in verts)
        for f in faces:
            c = geom2d.face_center(verts, f)
            assert not any(Polygon(h).contains(Point(c[:2])) for h in holes)
    # A rotated outer and a rotated hole: the bands still give the exact difference.
    tri = [(0.0, 0.0), (5.0, 1.0), (1.0, 4.0)]
    diamond = [(2.0, 1.2), (2.6, 1.8), (2.0, 2.4), (1.4, 1.8)]
    verts, faces = geom2d.polygon_faces(tri, [diamond], 0.0)
    assert geom2d.faces_area(verts, faces) == pytest.approx(Polygon(tri).difference(Polygon(diamond)).area)
    assert all(geom2d.face_normal(verts, f)[2] == pytest.approx(1.0) for f in faces)
    for mesh in (geom2d.extrude_profile([(0, 0), (1, 0), (1, 1), (0, 0.5)], (2.0, 3.0), (0.6, 0.8), 0.5),
                 geom2d.prism([(0, 0), (1, 0), (1.5, 1), (0, 1)], 1.0, 1.2)):
        assert _closed_and_outward({"verts": mesh[0], "faces": mesh[1]})


def test_stair_rise_and_the_ceiling_cut():
    rise, cap, source, warning = shell.stair_rise({"levels": [LEVEL0]}, LEVEL0)
    assert (rise, cap, source, warning) == (pytest.approx(2.85), pytest.approx(3.2),
                                            "derived from assumed ceiling and slab", None)
    documented = dict(LEVEL0, ceiling_height_source="section")
    assert shell.stair_rise({"levels": [documented]}, documented)[2] == "derived from the documented ceiling and assumed slab"
    upper = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.7, "ceiling_height_source": "section"}
    rise, cap, source, warning = shell.stair_rise({"levels": [LEVEL0, upper]}, LEVEL0)
    assert rise == 3.0 and cap == pytest.approx(3.0 - shell.STAIR_UPPER_FLOOR_GAP) and "elevations" in source
    assert "not cut" in warning
    building = {"levels": [LEVEL0, upper], "walls": HALL_WALLS, "rooms": [HALL], "openings": [],
                "furniture": [real01_stair_piece()]}
    plan = shell.plan_stairs(building, LEVEL0)[0]["plan"]
    assert plan["riser_m"] == pytest.approx(3.0 / 16) and plan["warnings"][-1] == warning
    assert max(v[2] for p in P.stair_parts(plan) for v in p["verts"]) < cap        # nothing through the cap
    # The hall ceiling loses the opening (and only that); a room the opening does not cross keeps one n-gon.
    building["levels"] = [LEVEL0]
    stairs = shell.plan_stairs(building, LEVEL0)
    void = [s["plan"]["void"] for s in stairs]
    verts, faces, cut = shell.ceiling_faces(HALL["polygon"], void, 2.7)
    expected = Polygon(HALL["polygon"]).difference(Polygon(void[0][0])).area
    assert cut == [0] and geom2d.faces_area(verts, faces) == pytest.approx(expected)
    assert all(geom2d.face_normal(verts, f)[2] == pytest.approx(-1.0) for f in faces)
    raw = Polygon(stairs[0]["plan"]["void_raw"][0])
    assert not any(raw.contains(Point(geom2d.face_center(verts, f)[:2])) for f in faces)
    other = [[0.0, 0.0], [3.0, 0.0], [3.0, 2.0], [0.0, 2.0]]
    assert shell.ceiling_faces(other, void, 2.7) == (*geom2d.polygon_face(other, 2.7, facing_up=False), [])


def test_build_false_stairs_and_site_are_not_built():
    site = {"boundary_walls": [{"id": "sw_L0_001", "start": [-1, -1], "end": [20, -1], "thickness": 0.15,
                                "kind": "plot"}],
            "areas": [{"id": "sa_L0_parking", "label": "Parking", "polygon": None}],
            "decor": [{"id": f"sd_L0_{i:03d}", "kind": "plant", "center": [i, -2], "size": [0.5, 0.5]}
                      for i in range(1, 10)], "openings": []}
    building = {"levels": [LEVEL0], "walls": HALL_WALLS, "rooms": [HALL], "openings": [], "site": site,
                "furniture": [real01_stair_piece(), dict(real01_stair_piece(), id="f_L0_020", build=False),
                              {"id": "f_L0_001", "level_id": "L0", "type": "sofa", "footprint": {}}]}
    stairs = shell.plan_stairs(building, LEVEL0)
    assert [(s["piece"]["id"], s["plan"] is None) for s in stairs] == [("f_L0_019", False), ("f_L0_020", True)]
    assert stairs[1]["reason"] == shell.STAIR_NOT_BUILT_REASON
    # furniture.py never sees a stair: the shell builds them (once).
    loose = B.furniture_building(building)
    assert [p["id"] for p in loose["furniture"]] == ["f_L0_001"] and loose["site"] is site
    assert len(building["furniture"]) == 3
    summary = B.site_summary(building)
    assert summary["built"] is False and "never built" in summary["reason"]
    assert summary["boundary_walls"] == {"count": 1, "ids": ["sw_L0_001"]} and summary["decor"]["count"] == 9
    assert summary["areas"]["ids"] == ["sa_L0_parking"] and summary["openings"]["count"] == 0
    assert B.site_summary({"walls": []}) is None
    total = {"pieces": 0, "by_method": {}, "fallbacks": [], "proxies": 0, "decor": 0, "not_built": [], "stairs": []}
    B.add_furniture_summary(total, {"pieces": 2, "by_method": {"parametric": 1, "proxy": 1}, "fallbacks": [],
                                    "proxies": 1, "decor": 3, "not_built": [{"id": "f_x", "type": "unknown",
                                                                             "reason": "build false"}]})
    B.add_furniture_summary(total, {"pieces": 1, "ids": ["f_L0_019"], "not_built": [
        {"id": "f_L0_020", "type": "stair", "reason": shell.STAIR_NOT_BUILT_REASON}]})
    assert total["pieces"] == 3 and total["by_method"] == {"parametric": 2, "proxy": 1} and total["decor"] == 3
    assert [r["id"] for r in total["not_built"]] == ["f_x", "f_L0_020"] and total["stairs"] == ["f_L0_019"]


def test_doorless_opening_is_cut_to_its_assumed_height():
    level = {"elevation": 0.0, "ceiling_height": 2.7}
    gap = {"type": "opening", "width": 1.6, "height": 2.1, "sill_height": None, "assumed": ["height"]}
    bottom, top, assumed = shell.opening_vertical(gap, level, False)
    assert (bottom, top) == (0.0, pytest.approx(2.1)) and assumed == {"height": 2.1}
    assert not shell.cut_full_height(top, 0.0, 2.7)                              # a lintel stays: no soffit
    door = {"type": "door", "width": 0.9, "height": 2.1, "sill_height": 0.0, "assumed": ["height"]}
    assert shell.opening_vertical(door, level, False)[2] == {"height": 2.1}
    window = {"type": "window", "width": 1.2, "height": 1.2, "sill_height": 0.9, "assumed": ["height", "sill_height"]}
    assert shell.opening_vertical(window, level, False) == (pytest.approx(0.9), pytest.approx(2.1),
                                                            {"height": 1.2, "sill_height": 0.9})
    # Without a height a plain opening still runs to the wall top (Milestone 3, pinned above).
    assert shell.opening_vertical(dict(gap, height=None, assumed=[]), level, False)[1] == pytest.approx(2.7)


def test_virtual_separator_has_no_geometry_and_breaks_nothing():
    sep = {"id": "o_L0_002", "type": "opening", "level_id": "L0", "wall_id": None, "virtual": True,
           "line": [[4.0, 0.0], [4.0, 1.29]], "center": [4.0, 0.645], "width": 1.29, "height": None,
           "sill_height": None, "status": "verified",
           "evidence": [{"file": "real01.pdf", "method": "derived", "confidence": 0.8}]}
    assert shell.is_virtual(sep) and not shell.is_virtual(dict(sep, wall_id="w_L0_001"))
    assert not shell.is_virtual(dict(sep, virtual=False))
    entry = shell.separator_entry(sep, "L0")
    assert entry["kind"] == "opening" and entry["has_geometry"] is False and entry["wall_id"] is None
    assert entry["virtual"] is True and entry["line"] == sep["line"] and entry["pass_index"] is None
    # The skirting of both rooms stops along the whole line (no wall there).
    level = {"elevation": 0.0, "ceiling_height": 2.7}
    assert shell.skirting_gaps([sep], level, False) == [([4.0, 0.645], pytest.approx(1.29))]
    room = [(0.0, 0.0), (4.0, 0.0), (4.0, 1.29), (0.0, 1.29)]
    spans = shell.skirting_spans(room, shell.skirting_gaps([sep], level, False))
    assert [s for s in spans if s[0] == 1] == []
    # Code that looks up an opening's wall copes with wall_id null.
    rooms = [{"id": "r_a", "level_id": "L0", "polygon": [list(p) for p in room]},
             {"id": "r_b", "level_id": "L0", "polygon": [[4.0, 0.0], [6.0, 0.0], [6.0, 1.29], [4.0, 1.29]]}]
    building = {"levels": [dict(level, id="L0")], "walls": [], "rooms": rooms, "openings": [sep], "furniture": []}
    assert cameras.opening_rooms(building, "L0") == {"o_L0_002": ["r_a", "r_b"]}
    assert shell.plan_stairs(building, dict(level, id="L0")) == []


def test_dining_and_prayer_rooms_use_the_living_slots():
    style = json.loads(STYLE_FIXTURE.read_text(encoding="utf-8"))
    living = shell.floor_style({"room_type": "living"}, style)
    for room_type in ("dining", "prayer"):
        assert shell.slot_room_type(room_type) == "living"
        assert shell.floor_style({"room_type": room_type}, style) == living == (style["floor"], False)
        assert shell.slot_room_type(room_type) not in shell.NO_SKIRTING_TYPES | shell.WET_ROOM_TYPES
    assert shell.slot_room_type("kitchen") == "kitchen" and shell.floor_style({"room_type": "kitchen"}, style)[1]
    assert shell.slot_room_type(None) is None


def test_scene_manifest_schema_takes_the_milestone_7_fields():
    sep = shell.separator_entry({"id": "o_L0_002", "type": "opening", "level_id": "L0", "wall_id": None,
                                 "virtual": True, "line": [[4.0, 0.0], [4.0, 1.29]], "center": [4.0, 0.645],
                                 "width": 1.29, "status": "verified",
                                 "evidence": [{"file": "real01.pdf", "method": "derived", "confidence": 0.8}]}, "L0")
    plan = _real01_plan()
    stair = {"name": "furn_f_L0_019", "wenart_id": "f_L0_019", "kind": "furniture", "status": "verified",
             "evidence": [{"file": "real01.pdf", "method": "vector", "confidence": 0.9}], "material": "m",
             "textured": False, "pass_index": 1, "assumed": {},
             "box3d": {"center": [4.2, 5.9, 1.5], "size": [2.4, 1.5, 3.2], "rotation_deg": 90.0},
             "stair": shell.stair_record(plan, P.stair_parts(plan))}
    assert [f["treads"] for f in stair["stair"]["flights"]] == [7, 7]
    manifest = {
        "schema_version": "0.1", "project": "real01", "building": "b.json", "style": None,
        "blender_version": "5.2.2", "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
        "objects": [dict(sep, room_ids=["r_a", "r_b"]), stair], "cameras": [], "materials": {},
        "pass_index": {"f_L0_019": 1},
        "assumed": [{"object": "furn_f_L0_019", "field": e["field"], "value": e["value"], "reason": e["reason"],
                     "parent": "f_L0_019", "kind": e["kind"]} for e in plan["assumed"]],
        "warnings": [], "checks": {"door_rays": []}, "previews": {}, "preview_maps": {},
        "build_fingerprint": "0" * 64,
        "furniture": {"pieces": 1, "by_method": {"parametric": 1}, "fallbacks": [], "proxies": 0, "decor": 0,
                      "not_built": [{"id": "f_L0_020", "type": "stair", "reason": shell.STAIR_NOT_BUILT_REASON}],
                      "stairs": ["f_L0_019"]},
        "site": B.site_summary({"site": {"boundary_walls": [{"id": "sw_L0_001"}], "areas": [], "decor": []}}),
    }
    schemas.validate_scene_manifest(manifest)
    schemas.validate_scene_manifest(dict(manifest, site=None))
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(dict(manifest, site=dict(manifest["site"], built=True)))
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(dict(manifest, furniture=dict(manifest["furniture"], not_built=[{"id": "x"}])))


def test_ceiling_light_stays_under_the_ceiling_left_by_the_stair_opening():
    building = {"levels": [LEVEL0], "walls": HALL_WALLS, "rooms": [HALL], "openings": [],
                "furniture": [real01_stair_piece()]}
    voids = lighting.stair_openings(building, LEVEL0)
    assert len(voids) == 1
    before = lighting.area_light_plan(HALL["polygon"])
    assert Polygon(voids[0]).contains(Point(before["center"]))           # the old pole lies in the opening
    plan = lighting.area_light_plan(HALL["polygon"], holes=voids)
    half = plan["size"] / 2.0
    square = shapely_box(plan["center"][0] - half, plan["center"][1] - half,
                         plan["center"][0] + half, plan["center"][1] + half)
    assert Polygon(HALL["polygon"]).contains(square) and not square.intersects(Polygon(voids[0]))
    assert plan["boundary_distance"] == pytest.approx(2.504 * FT, abs=0.01)
    assert lighting.area_light_plan(HALL["polygon"], holes=()) == before   # no opening: unchanged
