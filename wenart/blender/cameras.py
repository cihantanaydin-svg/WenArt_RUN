"""Camera placement: three cameras per room (docs/milestone3.md §3, cameras.py).

All placement maths is pure Python (``plan_cameras``) so the CPU tests check
it without Blender; ``create_cameras`` only turns the plans into camera
objects.

Per room, at 1.4 m above the floor, 24 mm lens on a 36 mm sensor, 1920x1080:
1. ``cam_<room>_1``: a point of the free area (room polygon shrunk by 0.5 m,
   minus proxy footprints grown by 0.3 m) looking at the centre of the
   longest wall of the room; the free point farthest from that wall wins so
   the view covers as much of the room as possible.
2. ``cam_<room>_2``: 0.4 m inside the room from the centre of its door
   opening, looking at the room centroid.
3. ``cam_<room>_3``: next to the largest window of the room, looking across
   the room (through the centroid to the far side).
When a placement has no usable point it falls back to the room centroid and
records a warning. Each plan lists the openings and furniture of the room
whose centre is inside the camera frustum (used by the final vision check
later; pieces of other rooms are hidden by walls and are left out).
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.proxies import proxy_height

CAMERA_HEIGHT = 1.4
TARGET_HEIGHT = 1.3
LENS_MM = 24.0
SENSOR_MM = 36.0
RESOLUTION = (1920, 1080)
DOOR_INSET = 0.4
WINDOW_INSET = 0.6
WINDOW_SIDE_STEP = 0.5
# An opening belongs to a room when its centre (on the wall centre line) is
# within this distance of a room polygon edge: half the thickest wall plus slack.
OPENING_EDGE_TOLERANCE = 0.2


def plan_cameras(building: dict, level_id: str) -> list[dict]:
    """Camera plans for every room of ``level_id``."""
    level = next(lv for lv in building["levels"] if lv["id"] == level_id)
    floor_z = float(level["elevation"])
    plans = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        plans.extend(plan_room_cameras(room, building, floor_z))
    return plans


def plan_room_cameras(room: dict, building: dict, floor_z: float) -> list[dict]:
    polygon = [tuple(p[:2]) for p in room["polygon"]]
    if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
        polygon = polygon[:-1]
    furniture = [f for f in building["furniture"] if f.get("room_id") == room["id"]]
    obstacles = [f["footprint"] for f in furniture]
    openings = room_openings(room, polygon, building)
    centroid = G.polygon_centroid(polygon)
    free = geom2d.free_points(polygon, obstacles)

    plans = []
    # 1. Free area, looking at the centre of the longest wall.
    a, b = geom2d.longest_edge(polygon)
    wall_mid = G.segment_midpoint(a, b)
    warning = None
    candidates = [p for p in free if G.distance(p, wall_mid) >= 1.0] or free
    if candidates:
        pos2 = max(candidates, key=lambda p: G.distance(p, wall_mid))
    else:
        pos2, warning = centroid, "no free point in the room; camera at the centroid"
    plans.append(_plan(room, 1, pos2, wall_mid, floor_z, warning, "free area -> longest wall"))

    # 2. From the door opening, looking at the centroid.
    doors = [o for o in openings if o["type"] in ("door", "opening")]
    warning = None
    if doors:
        door = max(doors, key=lambda o: (o["type"] == "door", o["width"]))
        pos2 = _inset_point(door["center"], polygon, DOOR_INSET)
        target = centroid
        if G.distance(pos2, centroid) < 0.3:
            target = wall_mid
        plans.append(_plan(room, 2, pos2, target, floor_z, None, f"door {door['id']} -> centroid",
                           anchor=door["id"]))
    else:
        warning = "room has no door opening on its edges; camera at the centroid"
        plans.append(_plan(room, 2, centroid, wall_mid, floor_z, warning, "centroid fallback"))

    # 3. Next to the largest window, looking across the room.
    windows = [o for o in openings if o["type"] == "window"]
    if windows:
        win = max(windows, key=lambda o: o["width"])
        edge = geom2d.nearest_edge(win["center"], polygon)[1]
        inward = geom2d.inward_normal(edge[0], edge[1], polygon)
        along = _unit(edge[0], edge[1])
        base = (win["center"][0] + inward[0] * WINDOW_INSET, win["center"][1] + inward[1] * WINDOW_INSET)
        options = [
            (base[0] + along[0] * WINDOW_SIDE_STEP, base[1] + along[1] * WINDOW_SIDE_STEP),
            (base[0] - along[0] * WINDOW_SIDE_STEP, base[1] - along[1] * WINDOW_SIDE_STEP),
            base,
        ]
        warning = None
        pos2 = next((p for p in options if geom2d.point_is_free(p, polygon, obstacles, 0.3, 0.2)), None)
        if pos2 is None:
            pos2 = next((p for p in options if G.point_in_polygon(p, polygon)), None)
            if pos2 is not None:
                warning = "window camera stands in a proxy footprint or close to a wall"
        if pos2 is None:
            pos2, warning = centroid, "no usable point next to the window; camera at the centroid"
        # Look through the centroid to the far side of the room.
        far = (centroid[0] + (centroid[0] - pos2[0]) * 0.75, centroid[1] + (centroid[1] - pos2[1]) * 0.75)
        if G.distance(far, pos2) < 0.5:
            far = wall_mid
        plans.append(_plan(room, 3, pos2, far, floor_z, warning, f"window {win['id']} -> across",
                           anchor=win["id"]))
    else:
        warning = "room has no window on its edges; camera at the centroid"
        plans.append(_plan(room, 3, centroid, wall_mid, floor_z, warning, "centroid fallback"))

    # Frustum lists are limited to the camera's own room (its openings and its
    # furniture): walls hide everything else, so other rooms' pieces inside the
    # frustum would only mislead the final check.
    tangents = geom2d.frustum_tangents(LENS_MM, SENSOR_MM, RESOLUTION)
    for plan in plans:
        pos, tgt = plan["position"], plan["target"]
        plan["visible_openings"] = [
            o["id"] for o in openings
            if geom2d.point_in_frustum((o["center"][0], o["center"][1], floor_z + 1.0), pos, tgt, tangents)
        ]
        plan["visible_furniture"] = [
            f["id"] for f in furniture
            if geom2d.point_in_frustum(
                (f["footprint"]["center"][0], f["footprint"]["center"][1],
                 floor_z + proxy_height(f["type"], f.get("height"))[0] / 2.0), pos, tgt, tangents)
        ]
    return plans


def room_openings(room: dict, polygon, building: dict) -> list[dict]:
    """Openings whose centre lies on an edge of the room polygon."""
    out = []
    for o in building["openings"]:
        if o["level_id"] != room["level_id"]:
            continue
        d, _edge = geom2d.nearest_edge(o["center"], polygon)
        if d <= OPENING_EDGE_TOLERANCE:
            out.append(o)
    return out


def _inset_point(center, polygon, inset: float) -> tuple[float, float]:
    """Point ``inset`` metres into the room from an opening centre."""
    edge = geom2d.nearest_edge(center, polygon)[1]
    nx, ny = geom2d.inward_normal(edge[0], edge[1], polygon)
    # The opening centre sits on the wall centre line, half a wall outside the
    # room edge; project it onto the edge first so the inset is measured from
    # the room boundary.
    d = G.point_segment_distance(center, edge[0], edge[1])
    return (center[0] + nx * (d + inset), center[1] + ny * (d + inset))


def _unit(a, b) -> tuple[float, float]:
    length = G.distance(a, b)
    if length == 0:
        return (1.0, 0.0)
    return ((b[0] - a[0]) / length, (b[1] - a[1]) / length)


def _plan(room: dict, index: int, pos2, target2, floor_z: float, warning, how: str, anchor=None) -> dict:
    return {
        "name": f"cam_{room['id']}_{index}",
        "room_id": room["id"], "level_id": room["level_id"], "index": index,
        "position": [float(pos2[0]), float(pos2[1]), floor_z + CAMERA_HEIGHT],
        "target": [float(target2[0]), float(target2[1]), floor_z + TARGET_HEIGHT],
        "lens_mm": LENS_MM, "sensor_mm": SENSOR_MM, "resolution": list(RESOLUTION),
        "placement": how, "anchor": anchor, "warning": warning,
        "visible_openings": [], "visible_furniture": [],
    }


def create_cameras(plans: list[dict], collection, manifest_objects: list) -> list:
    """Create a Blender camera object per plan (needs bpy)."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common

    created = []
    for plan in plans:
        cam = bpy.data.cameras.new(plan["name"])
        cam.lens = plan["lens_mm"]
        cam.sensor_width = plan["sensor_mm"]
        cam.sensor_fit = "HORIZONTAL"
        cam.clip_start = 0.05
        cam.clip_end = 200.0
        ob = bpy.data.objects.new(plan["name"], cam)
        ob.location = Vector(plan["position"])
        direction = Vector(plan["target"]) - Vector(plan["position"])
        ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        collection.objects.link(ob)
        common.set_props(ob, wenart_id=plan["name"], kind="camera", status="assumed")
        ob["wenart_room"] = plan["room_id"]
        manifest_objects.append({
            "name": plan["name"], "wenart_id": plan["name"], "kind": "camera", "status": "assumed",
            "level_id": plan["level_id"], "element_id": plan["room_id"], "evidence": [],
            "material": None, "textured": False, "pass_index": None, "assumed": {},
        })
        created.append(ob)
    return created
