"""CPU tests of the bpy-free parts of wenart.blender: solid primitives, proxy
geometry, wall overlap trimming, opening defaults, camera placement, the
manifest schemas and the Blender-binary lookup. No Blender needed."""
import json
import math
import os
import stat
from pathlib import Path

import pytest
from shapely.geometry import Polygon
from shapely.ops import unary_union

from wenart import geometry as G
from wenart.blender import cameras, cli, geom2d, lighting, proxies, schemas, shell
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
    }
    schemas.validate_scene_manifest(manifest)
    bad = dict(manifest)
    bad["objects"] = [dict(manifest["objects"][0], kind="sofa")]
    with pytest.raises(Exception):
        schemas.validate_scene_manifest(bad)
    render = {"schema_version": "0.1", "scene": "s.blend", "device": "CPU", "device_requested": "auto",
              "blender_version": "5.2.2", "samples": 16, "resolution": [320, 180], "denoiser": "OPENIMAGEDENOISE",
              "pass_index": {"proxy_f": 1},
              "renders": [{"camera": "cam", "png": "cam.png", "exr": "cam_passes.exr", "preview": "cam_preview.jpg",
                           "seconds": 1.0, "samples": 16, "resolution": [320, 180],
                           "depth": {"min": 1.0, "max": 5.0, "mean": 2.0}, "index_values": [1]}]}
    schemas.validate_render_manifest(render)
    with pytest.raises(Exception):
        schemas.validate_render_manifest(dict(render, device="TPU"))


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
    monkeypatch.setenv("WENART_BLENDER", str(tmp_path / "missing"))
    found = cli.find_blender()
    assert found is None or os.access(found, os.X_OK)
