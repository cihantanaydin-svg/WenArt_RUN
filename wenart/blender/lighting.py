"""Lighting from the style profile (docs/milestone3.md §3, lighting.py).

- World: HDRI from the assets manifest when available, else a physical sky
  (materials.world_nodes); strength from the mood.
- Sun lamp at the style's elevation / azimuth; colour through the lamp's
  blackbody temperature (SunLight.use_temperature / temperature, Blender 5.2),
  strength in W/m2 from ``sun_strength``.
- One soft area light at the ceiling of every room that has no window on its
  edges, recorded as ``assumed`` in the manifest. Rooms with windows get their
  light from the sun and the sky only (no fill light: per-camera exposure
  makes dark rooms readable, and the documents say nothing about lamps).
- One light portal per window (docs/milestone5.md §2.3): an AREA light,
  shape RECTANGLE, ``size = width - 2 * frame``, ``size_y = height - 2 *
  frame``, centred in the opening just inside the inner wall face, local -Z
  into the room, ``light.cycles.is_portal = True``. A portal emits nothing;
  it tells Cycles where the sky comes in, which cut the noise of the world
  light by 21-46 % at equal samples in the Milestone 5 test room. Manifest
  entry ``kind: light, status: assumed, reason: portal``. Portals are only
  unbiased with the camera-only window glass of materials.py.

Azimuth is compass degrees clockwise from north (+Y); elevation above the
horizon. Blender lamps shine along their local -Z.

Milestone 6 (docs/milestone6.md §5 rows 5 and 6):

- the ceiling light of a room sits at the polygon's pole of inaccessibility
  (``polylabel``, pure Python, 1 cm precision: the inside point farthest
  from the boundary; an L-shaped hall's centroid can lie outside it) and its
  square is at most ``sqrt(2) * distance`` wide, so all of it is inside the
  room (``area_light_plan``);
- dim rooms (window area / floor area < ``DIM_ROOM_RATIO``) get the same
  ceiling light at half the power per m2 (6 W/m2), invisible to the camera,
  recorded ``assumed`` with the ratio as the reason (lighting mood: the
  documents say nothing about lamps).

Milestone 7 (docs/milestone7.md §6.4): the stair openings of a level
(``shell.plan_stairs``) are holes for ``polylabel``, so a ceiling light never
hangs in an opening, among the steps of the last flight.
"""
from __future__ import annotations

import heapq
import math

from wenart import geometry as G
from wenart.blender.cameras import room_openings

# The portal sits this far inside the inner wall face (in the reveal, in front of the frame).
PORTAL_INSET_M = 0.01


def portal_plan(opening: dict, wall: dict, level: dict, levels_above: bool, rooms: list[dict]) -> dict:
    """Where the portal of one window goes (pure; no bpy).

    Returns ``{"center": [x, y, z], "size": [w, h], "inward": [nx, ny],
    "room_id": id | None, "note": str | None}``: the rectangle is the glass
    area (opening minus the frame on every side), centred on the opening
    projected onto the wall centre line and moved ``thickness / 2 -
    PORTAL_INSET_M`` towards the room. ``inward`` points into the room the
    window lights: the side of the wall that lies in a room polygon; when
    both or neither side does (an interior window, a broken plan) the side
    away from the outside of the wall is taken and ``note`` says so."""
    from wenart.blender.shell import DEFAULTS, opening_centre_on_wall, opening_vertical

    bottom, top, _ = opening_vertical(opening, level, levels_above)
    frame = DEFAULTS["frame_width"]
    width = float(opening["width"])
    cx, cy, _shift = opening_centre_on_wall(opening, wall)
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    thickness = float(wall["thickness"])
    reach = thickness / 2.0 + DEFAULTS["face_probe"]
    sides = {}
    for side in (1, -1):
        probe = (cx + side * nx * reach, cy + side * ny * reach)
        sides[side] = next((r for r in rooms if len(r["polygon"]) >= 3 and G.point_in_polygon(probe, r["polygon"])),
                           None)
    note = None
    if (sides[1] is None) != (sides[-1] is None):
        side = 1 if sides[1] is not None else -1
    else:
        side = 1
        note = ("rooms on both sides of the window: portal faces the left side of the wall"
                if sides[1] is not None else "no room on either side of the window: portal faces the left side")
    inward = (side * nx, side * ny)
    depth = thickness / 2.0 - PORTAL_INSET_M
    return {
        "center": [cx + inward[0] * depth, cy + inward[1] * depth, (bottom + top) / 2.0],
        "size": [max(0.01, width - 2.0 * frame), max(0.01, (top - bottom) - 2.0 * frame)],
        "inward": [inward[0], inward[1]],
        "room_id": sides[side]["id"] if sides[side] is not None else None,
        "note": note,
    }

# Area light power scales with the floor area (a fixed 120 W washed out a 3 m2 WC).
AREA_LIGHT_W_PER_M2 = 12.0
AREA_LIGHT_MIN_W = 10.0
AREA_LIGHT_MAX_W = 150.0
AREA_LIGHT_MAX_SIZE = 1.5
AREA_LIGHT_MIN_SIZE = 0.3
AREA_LIGHT_CEILING_GAP = 0.05
# Dim rooms (Milestone 6): window area / floor area below this gets the ceiling light at DIM_POWER_FACTOR.
DIM_ROOM_RATIO = 0.08
DIM_POWER_FACTOR = 0.5
POLYLABEL_PRECISION_M = 0.01


# --------------------------------------------------------------------------
# Pole of inaccessibility (pure Python; Blender's Python has no shapely)
# --------------------------------------------------------------------------

def _signed_distance(x: float, y: float, polygon, holes=()) -> float:
    """Distance from (x, y) to the polygon boundary, negative outside.
    ``holes`` (Milestone 7: stair openings in the ceiling) count as outside,
    and their edges as boundary (even-odd over all rings, as Mapbox's polylabel)."""
    inside = False
    best = math.inf
    for ring in (polygon, *holes):
        n = len(ring)
        for i in range(n):
            ax, ay = ring[i]
            bx, by = ring[(i + 1) % n]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                inside = not inside
            dx, dy = bx - ax, by - ay
            length_sq = dx * dx + dy * dy
            t = 0.0 if length_sq == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / length_sq))
            px, py = ax + t * dx - x, ay + t * dy - y
            best = min(best, px * px + py * py)
    d = math.sqrt(best)
    return d if inside else -d


def polylabel(polygon, precision: float = POLYLABEL_PRECISION_M, holes=()) -> tuple[float, float, float]:
    """``(x, y, distance)``: the pole of inaccessibility of a simple polygon,
    the inside point farthest from its boundary, to within ``precision``
    (Mapbox's polylabel: square cells over the bounding box in a priority
    queue by the best distance a cell could still hold; cells that cannot
    beat the best found by more than ``precision`` are dropped). The
    centroid and the bounding-box centre seed the search. Deterministic.
    ``holes``: polygons inside it that are not part of it (each lying
    inside ``polygon`` or beyond its edges; Milestone 7 stair openings)."""
    poly = [(float(p[0]), float(p[1])) for p in polygon]
    if len(poly) > 1 and poly[0] == poly[-1]:
        poly = poly[:-1]
    if len(poly) < 3:
        raise ValueError("polylabel needs a polygon with at least 3 points")
    rings = [[(float(p[0]), float(p[1])) for p in h] for h in holes if len(h) >= 3]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    width, height = x1 - x0, y1 - y0
    cell = min(width, height)
    if cell <= 0:
        return x0, y0, 0.0
    h = cell / 2.0
    queue: list = []
    counter = 0

    def push(cx: float, cy: float, half: float) -> None:
        nonlocal counter
        d = _signed_distance(cx, cy, poly, rings)
        heapq.heappush(queue, (-(d + half * math.sqrt(2.0)), counter, cx, cy, half, d))
        counter += 1

    y = y0
    while y < y1:
        x = x0
        while x < x1:
            push(x + h, y + h, h)
            x += cell
        y += cell
    cx, cy = G.polygon_centroid(poly)
    best = (cx, cy, _signed_distance(cx, cy, poly, rings))
    bx, by = x0 + width / 2.0, y0 + height / 2.0
    d = _signed_distance(bx, by, poly, rings)
    if d > best[2]:
        best = (bx, by, d)
    while queue:
        neg_max, _, cx, cy, half, d = heapq.heappop(queue)
        if d > best[2]:
            best = (cx, cy, d)
        if -neg_max - best[2] <= precision:
            continue
        half /= 2.0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                push(cx + sx * half, cy + sy * half, half)
    return best


def area_light_plan(polygon, holes=()) -> dict:
    """Where a room's square ceiling light goes (pure): ``{"center": [x, y],
    "size", "boundary_distance"}``. Centre = ``polylabel``; size = half the
    smaller bounding-box side, between ``AREA_LIGHT_MIN_SIZE`` and
    ``AREA_LIGHT_MAX_SIZE``, and never above ``sqrt(2) * distance`` so the
    whole square (half-diagonal = size / sqrt(2)) lies inside the room.
    ``holes`` (Milestone 7): the stair openings of the level; the light stays
    under the ceiling that is left, never in an opening."""
    x, y, d = polylabel(polygon, holes=holes)
    d = math.floor(d * 1e4) / 1e4                      # recorded to 0.1 mm, never more than the real distance
    bx0, by0, bx1, by1 = G.bbox(polygon)
    size = min(AREA_LIGHT_MAX_SIZE, max(AREA_LIGHT_MIN_SIZE, min(bx1 - bx0, by1 - by0) * 0.5))
    size = min(size, math.floor(math.sqrt(2.0) * d * 1e4) / 1e4)
    return {"center": [round(x, 4), round(y, 4)], "size": round(size, 4), "boundary_distance": d}


def window_floor_ratio(windows: list[dict], level: dict, levels_above: bool, floor_area: float) -> float:
    """Window opening area (width x height, ``shell.opening_vertical``) over the floor area."""
    from wenart.blender.shell import opening_vertical

    glass = 0.0
    for o in windows:
        bottom, top, _ = opening_vertical(o, level, levels_above)
        glass += float(o["width"]) * max(0.0, top - bottom)
    return glass / max(float(floor_area), 1e-6)


def fill_light_reason(windows: list[dict], ratio: float | None) -> str | None:
    """Why a room gets the assumed ceiling light, or None: no window, or a
    window area below ``DIM_ROOM_RATIO`` of the floor area."""
    if not windows:
        return "room has no window"
    if ratio is not None and ratio < DIM_ROOM_RATIO:
        return f"room has little daylight (window/floor {ratio:.3f} < {DIM_ROOM_RATIO})"
    return None


def stair_openings(building: dict, level: dict) -> list[list[tuple[float, float]]]:
    """The ceiling openings of the stairs of a level (pure, ``shell.plan_stairs``): every void loop."""
    from wenart.blender.shell import plan_stairs

    return [loop for s in plan_stairs(building, level) if s["plan"] is not None for loop in s["plan"]["void"]]


def sun_direction(elevation_deg: float, azimuth_deg: float) -> tuple[float, float, float]:
    """Unit vector from the scene towards the sun."""
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    return (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))


def building_azimuth(compass_azimuth_deg: float, north_deg: float = 0.0) -> float:
    """The sun's azimuth in the building frame (clockwise from the building's +Y) of a compass azimuth
    (clockwise from north), when the building's +Y axis points to the compass bearing ``north_deg``
    (``site.north_deg``, Milestone 10; 0 = +Y is north, the M3-M9 convention)."""
    return (float(compass_azimuth_deg) - float(north_deg)) % 360.0


def build_lighting(building: dict, levels: list[dict], style: dict, hdri_path: str | None, collection,
                   manifest_objects: list, assumed: list, north_deg: float | None = None,
                   north_source: str | None = None, ceiling_at=None) -> dict:
    """World + sun + area lights for the windowless rooms of ``levels``.

    Milestone 10: ``north_deg`` (the compass bearing of the building's +Y axis, ``site.north_deg``) turns
    the style's compass sun azimuth into the building frame (``building_azimuth``); ``ceiling_at(level,
    x, y)`` gives the ceiling height of a room under the roof (sloped), so its ceiling light hangs under it."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common
    from wenart.blender.materials import world_nodes

    scene = bpy.context.scene
    lighting = style.get("lighting") or {}
    elevation = float(lighting.get("sun_elevation_deg", 35.0))
    azimuth = float(lighting.get("sun_azimuth_deg", 210.0))
    strength = float(lighting.get("sun_strength", 3.0))
    temperature = float(lighting.get("colour_temperature_k", 5200))
    in_building = building_azimuth(azimuth, north_deg or 0.0)

    world = world_nodes(scene, lighting, hdri_path)

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = strength
    sun.angle = math.radians(0.53)
    try:
        sun.use_temperature = True
        sun.temperature = temperature
    except AttributeError:  # older API: fall back to a plain colour
        sun.color = _blackbody_rgb(temperature)
    ob = bpy.data.objects.new("sun", sun)
    d = Vector(sun_direction(elevation, in_building))
    ob.location = d * 30.0
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(ob)
    common.set_props(ob, wenart_id="sun", kind="light", status="assumed")
    manifest_objects.append({
        "name": "sun", "wenart_id": "sun", "kind": "light", "status": "assumed", "level_id": None,
        "element_id": None, "evidence": [], "material": None, "textured": False, "pass_index": None,
        "assumed": {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength,
                    "temperature_k": temperature},
    })
    if north_deg is not None:
        manifest_objects[-1]["assumed"].update(azimuth_building_deg=round(in_building, 3), north_deg=north_deg,
                                               north_source=north_source)

    portals = build_portals(building, levels, collection, manifest_objects)

    area_lights = []
    for level in levels:
        floor_z = float(level["elevation"])
        ceil_z = floor_z + float(level["ceiling_height"])
        levels_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
        voids = stair_openings(building, level)
        for room in building["rooms"]:
            if room["level_id"] != level["id"]:
                continue
            polygon = [tuple(p[:2]) for p in room["polygon"]]
            if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
                polygon = polygon[:-1]
            if len(polygon) < 3:
                continue
            windows = [o for o in room_openings(room, polygon, building) if o["type"] == "window"]
            area = G.polygon_area(polygon)
            ratio = window_floor_ratio(windows, level, levels_above, area) if windows else None
            why = fill_light_reason(windows, ratio)
            if why is None:
                continue
            dim = bool(windows)
            plan = area_light_plan(polygon, holes=voids)
            size = plan["size"]
            per_m2 = AREA_LIGHT_W_PER_M2 * (DIM_POWER_FACTOR if dim else 1.0)
            power = min(AREA_LIGHT_MAX_W, max(AREA_LIGHT_MIN_W, per_m2 * area))
            light = bpy.data.lights.new(f"light_{room['id']}", "AREA")
            light.shape = "SQUARE"
            light.size = size
            light.energy = power
            try:
                light.use_temperature = True
                light.temperature = temperature
            except AttributeError:
                light.color = _blackbody_rgb(temperature)
            lob = bpy.data.objects.new(f"light_{room['id']}", light)
            if ceiling_at is not None:
                ceil_z = min(ceil_z, ceiling_at(level, plan["center"][0], plan["center"][1]))
            lob.location = (plan["center"][0], plan["center"][1], ceil_z - AREA_LIGHT_CEILING_GAP)
            lob.visible_camera = False      # lighting mood only: no lamp in the picture
            collection.objects.link(lob)
            common.set_props(lob, wenart_id=f"light_{room['id']}", kind="light", status="assumed")
            lob["wenart_room"] = room["id"]
            kind = "dim_room_light" if dim else "windowless_room_light"
            manifest_objects.append({
                "name": lob.name, "wenart_id": lob.name, "kind": "light", "status": "assumed",
                "level_id": level["id"], "element_id": room["id"], "parent": room["id"], "evidence": [],
                "material": None, "textured": False, "pass_index": None,
                "center": [plan["center"][0], plan["center"][1], round(ceil_z - AREA_LIGHT_CEILING_GAP, 4)],
                "size": size,
                "assumed": {"power_w": power, "w_per_m2": per_m2, "size_m": size,
                            "boundary_distance_m": plan["boundary_distance"], "window_floor_ratio":
                                None if ratio is None else round(ratio, 4), "visible_camera": False, "reason": why},
            })
            assumed.append({"object": lob.name, "field": "area_light", "value": power,
                            "reason": f"{room['id']}: {why}; soft ceiling light added (lighting mood, invisible "
                                      f"to the camera)",
                            "parent": room["id"], "kind": kind})
            area_lights.append(lob)
    sun_info = {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength, "temperature_k": temperature}
    if north_deg is not None:
        sun_info.update(azimuth_building_deg=round(in_building, 3), north_deg=north_deg, north_source=north_source)
    return {"world": world, "sun": sun_info,
            "area_lights": [o.name for o in area_lights], "portals": [o.name for o in portals]}


def build_portals(building: dict, levels: list[dict], collection, manifest_objects: list) -> list:
    """One portal AREA light per window of ``levels`` (see ``portal_plan``)."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common

    created = []
    for level in levels:
        floor_z = float(level["elevation"])
        levels_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
        walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level["id"]}
        rooms = [r for r in building["rooms"] if r["level_id"] == level["id"]]
        for opening in building["openings"]:
            if opening["level_id"] != level["id"] or opening["type"] != "window":
                continue
            wall = walls.get(opening.get("wall_id"))
            if wall is None:
                continue  # build_openings already warned: no window object either
            plan = portal_plan(opening, wall, level, levels_above, rooms)
            name = f"portal_{opening['id']}"
            light = bpy.data.lights.new(name, "AREA")
            light.shape = "RECTANGLE"
            light.size, light.size_y = plan["size"]
            light.cycles.is_portal = True
            ob = bpy.data.objects.new(name, light)
            ob.location = Vector(plan["center"])
            # Local -Z (the light direction) into the room, local Y up: size along the wall, size_y vertical.
            ob.rotation_euler = Vector((plan["inward"][0], plan["inward"][1], 0.0)).to_track_quat("-Z", "Y").to_euler()
            collection.objects.link(ob)
            common.set_props(ob, wenart_id=name, kind="light", status="assumed")
            ob["wenart_opening"] = opening["id"]
            ob["wenart_room"] = plan["room_id"] or ""
            assumed = {"reason": "portal", "size_m": [round(v, 4) for v in plan["size"]], "faces_room": plan["room_id"]}
            if plan["note"]:
                assumed["note"] = plan["note"]
            manifest_objects.append({
                "name": name, "wenart_id": name, "kind": "light", "status": "assumed", "level_id": level["id"],
                "element_id": opening["id"], "evidence": [], "material": None, "textured": False, "pass_index": None,
                "reason": "portal", "center": [round(v, 4) for v in plan["center"]],
                "size": [round(v, 4) for v in plan["size"]], "inward": [round(v, 4) for v in plan["inward"]],
                "assumed": assumed,
            })
            created.append(ob)
    return created


def _blackbody_rgb(kelvin: float) -> tuple[float, float, float]:
    """Rough blackbody colour (only used when the lamp has no temperature input)."""
    t = kelvin / 100.0
    r = 1.0 if t <= 66 else min(1.0, 1.2929 * (t - 60) ** -0.1332)
    g = min(1.0, 0.3900 * math.log(t) - 0.6318) if t <= 66 else min(1.0, 1.1299 * (t - 60) ** -0.0755)
    b = 1.0 if t >= 66 else (0.0 if t <= 19 else min(1.0, 0.5432 * math.log(t - 10) - 1.1963))
    return (max(0.0, r), max(0.0, g), max(0.0, b))
