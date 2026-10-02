"""CPU tests of the camera placement (wenart.blender.cameras): openings are
assigned to rooms by the thickness of their wall, every camera (free area,
door, window) stands outside the furniture proxies and records a warning
whenever it had to move, on hand-made rooms and on all synthetic projects.
No Blender needed."""
import json
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import cameras, geom2d
from wenart.blender.proxies import proxy_height

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
SYNTHETIC = ("synthetic-01", "synthetic-02", "synthetic-03")


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
