"""CPU tests of the camera placement (wenart.blender.cameras): openings are
assigned to rooms by the thickness of their wall, every camera (free area,
door, window) stands outside the furniture proxies and records a warning
whenever it had to move, on hand-made rooms and on all synthetic projects;
the same for the ``search`` policy (docs/milestone6.md §4; the search itself
is tested in tests/test_camsearch.py). No Blender needed, except for the
check that ``create_cameras`` sets the lens shift (skipped without it)."""
import json
import math
import subprocess
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import cameras, cli, geom2d
from wenart.blender.proxies import proxy_height

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
SYNTHETIC = ("synthetic-01", "synthetic-02", "synthetic-03")
BLENDER = cli.find_blender()


# --------------------------------------------------------------------------
# A square room with four exterior walls, one window (south) and one door (east)
# --------------------------------------------------------------------------

def _room(thickness: float = 0.25, size: float = 4.0, furniture=(), window_center=None, door_center=None) -> dict:
    """One room whose inner faces lie on x, y in [0, size]; the wall centre
    lines run ``thickness / 2`` outside. Opening centres sit on the centre
    lines unless given."""
    t = thickness
    h = t / 2.0
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-t, -h], "end": [size + t, -h], "thickness": t},
        {"id": "w_e", "level_id": "L0", "start": [size + h, -t], "end": [size + h, size + t], "thickness": t},
        {"id": "w_n", "level_id": "L0", "start": [size + t, size + h], "end": [-t, size + h], "thickness": t},
        {"id": "w_w", "level_id": "L0", "start": [-h, size + t], "end": [-h, -t], "thickness": t},
    ]
    openings = [
        {"id": "win", "level_id": "L0", "type": "window", "wall_id": "w_s", "width": 1.5,
         "center": list(window_center or [size / 2.0, -h])},
        {"id": "door", "level_id": "L0", "type": "door", "wall_id": "w_e", "width": 0.9,
         "center": list(door_center or [size + h, 1.0])},
    ]
    return {
        "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
        "walls": walls, "openings": openings,
        "rooms": [{"id": "r", "level_id": "L0", "polygon": [[0, 0], [size, 0], [size, size], [0, size]]}],
        "furniture": list(furniture),
    }


def _piece(fid: str, ftype: str, center, size, rotation: float = 0.0) -> dict:
    return {"id": fid, "type": ftype, "room_id": "r", "level_id": "L0", "front_deg": 0.0,
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}}


def _plans(building: dict) -> dict:
    return {p["index"]: p for p in cameras.plan_cameras(building, "L0")}


def _distance_to_piece(plan: dict, piece: dict) -> float:
    fp = piece["footprint"]
    return geom2d.distance_to_rect(plan["position"][:2], fp["center"], fp["size"], fp["rotation_deg"])


# --------------------------------------------------------------------------
# room_openings: tolerance from the wall thickness
# --------------------------------------------------------------------------

@pytest.mark.parametrize("thickness", [0.1, 0.25, 0.4, 0.5])
def test_room_openings_follow_the_wall_thickness(thickness):
    building = _room(thickness)
    room = building["rooms"][0]
    ids = {o["id"] for o in cameras.room_openings(room, [tuple(p) for p in room["polygon"]], building)}
    assert ids == {"win", "door"}, thickness
    plans = _plans(building)
    assert plans[2]["anchor"] == "door" and plans[3]["anchor"] == "win"
    assert plans[2]["warning"] is None and plans[3]["warning"] is None


def test_opening_centre_on_a_wall_face_is_still_assigned():
    # The pipeline accepts centres up to thickness / 2 off the centre line
    # (a door block inserted on the wall face): both faces must still match.
    for y in (0.0, -0.5):
        building = _room(0.5, window_center=[2.0, y])
        room = building["rooms"][0]
        ids = {o["id"] for o in cameras.room_openings(room, [tuple(p) for p in room["polygon"]], building)}
        assert "win" in ids, y


def test_opening_beyond_the_room_edge_is_not_assigned():
    # Same wall, same distance to the edge line, but the centre lies past the
    # end of the room edge (another room's window along the same wall).
    building = _room(0.5, window_center=[5.0, -0.25])
    room = building["rooms"][0]
    assert cameras.room_openings(room, [tuple(p) for p in room["polygon"]], building) == [
        o for o in building["openings"] if o["id"] == "door"]


def test_opening_without_a_known_wall_uses_the_fallback_tolerance():
    building = _room(0.25)
    building["openings"][0]["wall_id"] = "w_missing"
    room = building["rooms"][0]
    polygon = [tuple(p) for p in room["polygon"]]
    assert {o["id"] for o in cameras.room_openings(room, polygon, building)} == {"win", "door"}
    building["openings"][0]["center"] = [2.0, -cameras.OPENING_EDGE_TOLERANCE - 0.1]
    assert {o["id"] for o in cameras.room_openings(room, polygon, building)} == {"door"}


# --------------------------------------------------------------------------
# Cameras vs proxies
# --------------------------------------------------------------------------

def _assert_outside(plan: dict, pieces, clearance: float = cameras.CAMERA_OBSTACLE_CLEARANCE) -> None:
    for piece in pieces:
        assert _distance_to_piece(plan, piece) >= clearance - 1e-6, (plan["name"], piece["id"], plan["position"])


def test_door_camera_moves_out_of_a_wardrobe_in_front_of_the_door():
    wardrobe = _piece("wardrobe", "wardrobe", center=[3.5, 1.0], size=[0.6, 1.2])  # 2.1 m tall, 0.2 m inside the door
    building = _room(0.25, furniture=[wardrobe])
    plan = _plans(building)[2]
    assert plan["anchor"] == "door"
    assert G.point_in_polygon(plan["position"][:2], building["rooms"][0]["polygon"])
    _assert_outside(plan, [wardrobe])
    assert plan["warning"] and "moved" in plan["warning"] and "door" in plan["warning"]


def test_window_camera_moves_out_of_a_wardrobe_under_the_window():
    wardrobe = _piece("wardrobe", "wardrobe", center=[2.0, 0.4], size=[3.0, 0.8])
    building = _room(0.25, furniture=[wardrobe])
    plan = _plans(building)[3]
    assert plan["anchor"] == "win"
    assert G.point_in_polygon(plan["position"][:2], building["rooms"][0]["polygon"])
    _assert_outside(plan, [wardrobe])
    assert plan["warning"] and "moved" in plan["warning"] and "window" in plan["warning"]
    # The camera still stands near its window, not at the centroid.
    assert G.distance(plan["position"][:2], (2.0, 2.0)) > 0.3


def test_low_furniture_is_avoided_too():
    counter = _piece("counter", "kitchen_counter", center=[2.0, 0.3], size=[3.0, 0.6])  # 0.9 m tall
    building = _room(0.25, furniture=[counter])
    plan = _plans(building)[3]
    _assert_outside(plan, [counter])
    assert plan["warning"] and "moved" in plan["warning"]


def test_cameras_never_stand_inside_a_tall_proxy_even_when_the_room_is_full():
    # The wardrobe leaves no free point with the regular clearances and the
    # centroid is inside it: every camera must still end up outside the box.
    wardrobe = _piece("wardrobe", "wardrobe", center=[2.0, 2.0], size=[3.0, 3.0])
    building = _room(0.25, furniture=[wardrobe])
    for plan in _plans(building).values():
        assert G.point_in_polygon(plan["position"][:2], building["rooms"][0]["polygon"])
        _assert_outside(plan, [wardrobe])
        assert plan["warning"], plan["name"]


def test_unmoved_cameras_carry_no_warning():
    building = _room(0.25, furniture=[_piece("bed", "bed_double", center=[2.0, 3.0], size=[1.6, 2.0])])
    plans = _plans(building)
    assert plans[1]["warning"] is None and plans[2]["warning"] is None and plans[3]["warning"] is None
    assert G.distance(plans[2]["position"][:2], (4.0 - cameras.DOOR_INSET, 1.0)) < 1e-6


@pytest.mark.parametrize("name", SYNTHETIC)
def test_synthetic_cameras_are_inside_the_room_and_outside_every_proxy(name):
    building = json.loads((PROJECTS / name / "truth" / "building.json").read_text(encoding="utf-8"))
    rooms = {r["id"]: r for r in building["rooms"]}
    openings = {o["id"]: o for o in building["openings"]}
    for level in building["levels"]:
        plans = cameras.plan_cameras(building, level["id"])
        assert len(plans) == 3 * len([r for r in rooms.values() if r["level_id"] == level["id"]])
        for plan in plans:
            room = rooms[plan["room_id"]]
            assert G.point_in_polygon(plan["position"][:2], room["polygon"]), plan["name"]
            pieces = [f for f in building["furniture"] if f.get("room_id") == room["id"]]
            for piece in pieces:
                d = _distance_to_piece(plan, piece)
                tall = proxy_height(piece["type"], piece.get("height"))[0] >= cameras.CAMERA_HEIGHT
                assert d > 1e-6, (name, plan["name"], piece["id"], "camera inside a footprint")
                if tall:
                    assert d >= cameras.CAMERA_OBSTACLE_CLEARANCE - 1e-6, (name, plan["name"], piece["id"])
            # A door camera that is not at its nominal inset point was moved: say so.
            if plan["index"] == 2 and plan["anchor"]:
                door = openings[plan["anchor"]]
                if G.distance(plan["position"][:2], door["center"]) > cameras.DOOR_INSET + 0.3:
                    assert plan["warning"] and "moved" in plan["warning"], plan["name"]


# --------------------------------------------------------------------------
# Policy "search" (docs/milestone6.md §4): the same rooms, the same clearances
# --------------------------------------------------------------------------

def _search(building: dict, level: str = "L0") -> list[dict]:
    return cameras.plan_cameras(building, level, policy="search")


def test_search_policy_on_the_hand_made_room():
    building = _room(0.25, furniture=[_piece("bed", "bed_double", center=[2.0, 3.0], size=[1.6, 2.0])])
    plans = _search(building)
    assert [p["name"] for p in plans] == ["cam_r_1", "cam_r_2", "cam_r_3"]          # 16 m2: three views
    for p in plans:
        assert p["policy"] == "search" and p["shift_y"] == -0.10 and p["shift_x"] == 0.0
        assert p["position"][2] == pytest.approx(1.25) and p["target"][2] == pytest.approx(1.25)
        assert G.point_in_polygon(p["position"][:2], building["rooms"][0]["polygon"])
        assert p["warning"] is None and p["anchor"] is None
        _assert_outside(p, building["furniture"])
        assert set(p["visible_openings"]) <= {"win", "door"} and set(p["visible_furniture"]) <= {"bed"}
    # The default policy still gives the M5 plans of the same room.
    m5 = cameras.plan_cameras(building, "L0")
    assert [p["anchor"] for p in m5] == [None, "door", "win"]
    assert m5[0]["position"][2] == pytest.approx(cameras.CAMERA_HEIGHT)


def test_search_policy_avoids_a_wardrobe_in_front_of_the_door():
    wardrobe = _piece("wardrobe", "wardrobe", center=[3.5, 1.0], size=[0.6, 1.2])
    building = _room(0.25, furniture=[wardrobe])
    for p in _search(building):
        _assert_outside(p, [wardrobe])
        assert p["warning"] is None


@pytest.mark.parametrize("name", SYNTHETIC)
def test_synthetic_search_cameras_are_inside_the_room_and_outside_every_proxy(name):
    building = json.loads((PROJECTS / name / "truth" / "building.json").read_text(encoding="utf-8"))
    rooms = {r["id"]: r for r in building["rooms"]}
    for level in building["levels"]:
        plans = _search(building, level["id"])
        assert {p["room_id"] for p in plans} == {r["id"] for r in rooms.values() if r["level_id"] == level["id"]}
        for plan in plans:
            room = rooms[plan["room_id"]]
            assert G.point_in_polygon(plan["position"][:2], room["polygon"]), plan["name"]
            if plan["warning"]:
                continue
            for piece in [f for f in building["furniture"] if f.get("room_id") == room["id"]]:
                assert _distance_to_piece(plan, piece) >= cameras.CAMERA_OBSTACLE_CLEARANCE - 1e-6, plan["name"]


# --------------------------------------------------------------------------
# Milestone 8 (docs/milestone8.md §5): the lens of every camera
# --------------------------------------------------------------------------

def test_lens_constants_and_fields_of_view():
    assert (cameras.LENS_MM, cameras.NARROW_LENS_MM, cameras.NARROW_ROOM_M, cameras.M5_LENS_MM) == \
        (18.0, 16.0, 2.2, 24.0)
    assert cameras.LENS_RANGE_MM == (14.0, 35.0) and cameras.SENSOR_MM == 36.0
    hfov = {lens: 2 * math.degrees(math.atan(cameras.SENSOR_MM / 2 / lens)) for lens in (24.0, 18.0, 16.0)}
    assert hfov[24.0] == pytest.approx(73.74, abs=0.01) and hfov[18.0] == pytest.approx(90.0)
    assert hfov[16.0] == pytest.approx(96.73, abs=0.01)
    th, _ = geom2d.frustum_tangents(18.0, 36.0, (1920, 1080))
    assert th == pytest.approx(1.0)                               # 45 degrees each side of the view axis


def _poly_room(polygon) -> dict:
    return {"id": "r", "level_id": "L0", "polygon": [list(p) for p in polygon]}


@pytest.mark.parametrize("polygon, width, lens", [
    ([(0, 0), (4, 0), (4, 3), (0, 3)], 3.0, 18.0),                          # bedroom
    ([(0, 0), (2.2, 0), (2.2, 5), (0, 5), (0, 0)], 2.2, 18.0),              # exactly 2.2 m (closed ring): 18 mm
    ([(0, 0), (2.19, 0), (2.19, 5), (0, 5)], 2.19, 16.0),                   # galley kitchen just under 2.2 m
    ([(0, 0), (1.53, 0), (1.53, 4.57), (0, 4.57)], 1.53, 16.0),             # real01's hall
    ([(1, 1), (2.5, 2.5), (1.8, 3.2), (0.3, 1.7)], 0.99, 16.0),             # a turned 2.12 x 0.99 m bath
    # An L-shaped hall with 1.7 m arms: its minimum-area rectangle is 4.4 x 3.1 m, its width 1.7 m.
    ([(0, 0), (4.4, 0), (4.4, 1.7), (1.7, 1.7), (1.7, 3.1), (0, 3.1)], None, 16.0),
])
def test_room_lens_by_the_room_width(polygon, width, lens):
    room = _poly_room(polygon)
    got, rule = cameras.room_lens(room)
    assert got == lens
    if width is not None:
        assert cameras.room_width(room) == pytest.approx(width, abs=0.011)
    w = cameras.room_width(room)
    assert rule == (f"room width {w:.2f} m < 2.2 m" if lens == 16.0 else f"room width {w:.2f} m >= 2.2 m")
    assert cameras.room_width(_poly_room([(0, 0), (1, 0)])) == 0.0


def test_room_lens_of_the_l_shaped_hall_is_its_arm_not_its_bounding_box():
    """Why the inscribed width (twice the polylabel distance) and not the minimum-area rectangle: synthetic-04's
    L-shaped hall is 1.68 m wide in both arms; its rectangle is 3.10 x 4.40 m. It gets the 16 mm lens."""
    building = json.loads((ROOT / "results" / "furniture" / "synthetic-04" / "building_final.json")
                          .read_text(encoding="utf-8"))
    hall = next(r for r in building["rooms"] if r["id"] == "r_L3_hol")
    assert len(hall["polygon"]) >= 6
    assert cameras.room_width(hall) == pytest.approx(1.68, abs=0.011) and cameras.room_lens(hall)[0] == 16.0


@pytest.mark.parametrize("value", [14, 14.0, 22.5, 35])
def test_brief_lens_replaces_the_rule_for_every_room(value):
    for polygon in ([(0, 0), (4, 0), (4, 3), (0, 3)], [(0, 0), (1.5, 0), (1.5, 4), (0, 4)]):
        assert cameras.room_lens(_poly_room(polygon), value) == (float(value), "brief render.lens_mm")
    building = _room(0.25, furniture=[_piece("bed", "bed_double", center=[2.0, 3.0], size=[1.6, 2.0])])
    plans = cameras.plan_cameras(building, "L0", policy="search", lens_mm=value)
    assert plans and all(p["lens_mm"] == float(value) and p["lens_rule"] == "brief render.lens_mm" for p in plans)


@pytest.mark.parametrize("value", [13.9, 35.5, 0, -18, float("nan"), "18", True, None])
def test_lens_outside_14_to_35_mm_is_refused(value):
    with pytest.raises(ValueError, match="14 to 35 mm"):
        cameras.check_lens(value)
    if value is not None:
        with pytest.raises(ValueError, match="14 to 35 mm"):
            cameras.room_lens(_poly_room([(0, 0), (4, 0), (4, 3), (0, 3)]), value)
        with pytest.raises(ValueError, match="14 to 35 mm"):
            cameras.plan_cameras(_room(), "L0", policy="search", lens_mm=value)


def test_every_plan_carries_its_own_lens_and_m5_keeps_24_mm():
    narrow = _room(0.25, size=2.0, furniture=[_piece("wb", "washbasin", center=[1.0, 1.75], size=[0.6, 0.4])])
    wide = _room(0.25, furniture=[_piece("bed", "bed_double", center=[2.0, 3.0], size=[1.6, 2.0])])
    assert {p["lens_mm"] for p in cameras.plan_cameras(narrow, "L0", policy="search")} == {16.0}
    assert {p["lens_mm"] for p in cameras.plan_cameras(wide, "L0", policy="search")} == {18.0}
    for b in (narrow, wide):
        assert {p["lens_mm"] for p in cameras.plan_cameras(b, "L0")} == {24.0}   # m5: the committed M5 cameras
    with pytest.raises(ValueError, match="m5 camera policy keeps its 24 mm lens"):
        cameras.plan_cameras(wide, "L0", policy="m5", lens_mm=18.0)


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_create_cameras_sets_the_lens_shift_and_keeps_verticals_straight(tmp_path):
    """Blender: a searched plan gets shift_y -0.10 and a level camera (pitch 0: its view axis is
    horizontal and its up axis is world +Z); an M5 plan keeps shift 0 and its 1.4 -> 1.3 m tilt."""
    building = _room(0.25, furniture=[_piece("bed", "bed_double", center=[2.0, 3.0], size=[1.6, 2.0])])
    narrow = _room(0.25, size=2.0, furniture=[_piece("wb", "washbasin", center=[1.0, 1.75], size=[0.6, 0.4])])
    plans = _search(building)[:2] + [dict(cameras.plan_cameras(building, "L0")[0], name="cam_m5_1")] + \
        [dict(_search(narrow)[0], name="cam_narrow_1")]
    src, out = tmp_path / "plans.json", tmp_path / "cams.json"
    src.write_text(json.dumps(plans), encoding="utf-8")
    expr = (f"import sys, json; sys.path.insert(0, {str(ROOT)!r})\n"
            "import bpy\n"
            "from wenart.blender import cameras\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            "col = bpy.data.collections.new('c'); bpy.context.scene.collection.children.link(col)\n"
            f"plans = json.load(open({str(src)!r}))\n"
            "objs = cameras.create_cameras(plans, col, [])\n"
            "bpy.context.view_layer.update()\n"
            "res = {}\n"
            "for ob in objs:\n"
            "    m = ob.matrix_world.to_3x3()\n"
            "    res[ob.name] = {'shift': [ob.data.shift_x, ob.data.shift_y], 'fit': ob.data.sensor_fit,\n"
            "                    'lens': ob.data.lens, 'forward': list(-m.col[2]), 'up': list(m.col[1]),\n"
            "                    'location': list(ob.location)}\n"
            f"json.dump(res, open({str(out)!r}, 'w'))\n")
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", expr],
                          capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    res = json.loads(out.read_text(encoding="utf-8"))
    for plan in plans[:2]:
        cam = res[plan["name"]]
        assert cam["shift"] == pytest.approx([0.0, -0.10], abs=1e-6) and cam["fit"] == "HORIZONTAL"
        # Milestone 8: the plan's own lens (18 mm in this 4 x 4 m room; 24 mm before).
        assert cam["lens"] == pytest.approx(18.0) and cam["location"] == pytest.approx(plan["position"], abs=1e-6)
        assert cam["forward"][2] == pytest.approx(0.0, abs=1e-6) and cam["up"] == pytest.approx([0, 0, 1], abs=1e-6)
        yaw = math.radians(plan["score"]["yaw_deg"])
        assert cam["forward"][:2] == pytest.approx([math.cos(yaw), math.sin(yaw)], abs=1e-5)
    m5 = res["cam_m5_1"]
    assert m5["shift"] == [0.0, 0.0] and m5["forward"][2] < 0 and m5["lens"] == pytest.approx(24.0)
    assert res["cam_narrow_1"]["lens"] == pytest.approx(16.0) and res["cam_narrow_1"]["fit"] == "HORIZONTAL"
