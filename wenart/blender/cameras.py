"""Camera placement: three cameras per room (docs/milestone3.md §3, cameras.py).

All placement maths is pure Python (``plan_cameras``) so the CPU tests check
it without Blender; ``create_cameras`` only turns the plans into camera
objects (with the plan's lens shift).

Two policies (docs/milestone6.md §4): ``m5`` (the default, below, unchanged
since Milestone 5) and ``search`` (``camsearch.py``: ray-cast scored views,
1-3 per room by area, pitch 0 with lens shift; Milestone 7: one view for a
room with nothing to show, none below 2.5 m2, listed by
``rooms_without_view``).

Milestone 7 (docs/milestone7.md §3.3): pieces with ``build: false`` (drawn
symbols the scene does not build) are neither obstacles nor frustum entries
for either policy: the scene has nothing there.

Milestone 8 (docs/milestone8.md §5, user decision 6 of 4 Oct 2026: wider
lenses): every camera plan carries its own ``lens_mm`` and every reader
(camera search, frustum lists, expected elements, plan crops, polish prompt)
uses it. ``room_lens`` picks the lens of a ``search`` room: ``LENS_MM`` =
18 mm (90 degrees horizontal field of view on the 36 mm sensor; 24 mm gave
73.7 degrees), ``NARROW_LENS_MM`` = 16 mm (96.7 degrees) when the room's
width (``room_width``: twice the distance from its pole of inaccessibility,
``lighting.polylabel``, to the nearest wall: the diameter of the largest
circle inside the polygon, which is the shorter side of a rectangular room
and the width of the widest part of an L-shaped or angled one) is below
``NARROW_ROOM_M`` = 2.2 m, or the brief's ``render.lens_mm`` (14-35 mm,
``LENS_RANGE_MM``) for every room when the brief sets it. The ``m5`` policy
keeps ``M5_LENS_MM`` = 24 mm: it reproduces the committed M5 cameras byte for
byte for the realism A/B, whose A images are the committed 24 mm M5 renders.

Policy ``m5``, per room, at 1.4 m above the floor, 24 mm lens on a 36 mm sensor, 1920x1080:
1. ``cam_<room>_1``: a point of the free area (room polygon shrunk by 0.5 m,
   minus the furniture boxes grown by 0.3 m) looking at the centre of the
   longest wall of the room; the free point farthest from that wall wins so
   the view covers as much of the room as possible.
Furniture boxes are the fitted ones of Milestone 4 (``parametric.piece_bbox``:
library bbox times the fit scale, the parametric box, or the proxy box),
never smaller than the drawn footprint; decor is ignored.
2. ``cam_<room>_2``: 0.4 m inside the room from the centre of its door
   opening, looking at the room centroid.
3. ``cam_<room>_3``: next to the largest window of the room, looking across
   the room (through the centroid to the far side).
Every camera position must be free: inside the room polygon with
``CAMERA_WALL_CLEARANCE`` to the walls and ``CAMERA_OBSTACLE_CLEARANCE`` to
every furniture footprint of the room (a camera at 1.4 m inside a 2.1 m
wardrobe proxy renders the inside of a grey box). When the nominal point of
a door or window camera is not free, the search tries larger insets and side
steps along the wall, then the free-area grid point nearest to the opening,
then the room centroid, and as a last resort a point that is only clear of
the proxies at least as tall as the camera. Every move away from the nominal
point is recorded in the plan's ``warning`` (nothing is moved silently).
Each plan lists the openings and furniture of the room whose centre is
inside the camera frustum (used by the final vision check later; pieces of
other rooms are hidden by walls and are left out).

Milestone 10 (docs/milestone10.md §1.6b row 15): a wall-hung piece
(``mount_bottom_m``, ``mount_bottom``) is no floor obstacle; its centre for
the frustum lists is at its hanging height.
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.parametric import obstacle_rect, piece_bbox

CAMERA_HEIGHT = 1.4
TARGET_HEIGHT = 1.3
# Milestone 8 (§5): the lens of a searched camera, 18 mm, or 16 mm in a room narrower than 2.2 m; the
# brief's render.lens_mm (14-35 mm) replaces both. The m5 policy keeps the 24 mm of Milestones 3-7.
LENS_MM = 18.0
NARROW_LENS_MM = 16.0
NARROW_ROOM_M = 2.2
LENS_RANGE_MM = (14.0, 35.0)
M5_LENS_MM = 24.0
SENSOR_MM = 36.0
RESOLUTION = (1920, 1080)
DOOR_INSET = 0.4
WINDOW_INSET = 0.6
WINDOW_SIDE_STEP = 0.5
# Alternatives tried when the nominal door / window point is not free:
# further into the room and sideways along the wall (metres).
DOOR_INSETS = (DOOR_INSET, 0.6, 0.8, 1.0, 1.2)
DOOR_SIDE_STEPS = (0.0, 0.3, -0.3, 0.6, -0.6)
WINDOW_INSETS = (WINDOW_INSET, 0.9, 1.2, 1.5)
WINDOW_SIDE_STEPS = (WINDOW_SIDE_STEP, -WINDOW_SIDE_STEP, 0.0, 1.0, -1.0)
# Minimum clearances of a camera to the walls and to furniture footprints.
CAMERA_WALL_CLEARANCE = 0.3
CAMERA_OBSTACLE_CLEARANCE = 0.2
# An opening belongs to a room when its centre is within half its wall's
# thickness (plus its offset from the wall centre line and this slack) of a
# room polygon edge, measured along the edge normal with the foot on the edge.
OPENING_EDGE_SLACK = 0.05
# Tolerance when the opening's wall is unknown (no wall_id match).
OPENING_EDGE_TOLERANCE = 0.2


CAMERA_POLICIES = ("search", "m5")


def plan_cameras(building: dict, level_id: str, policy: str = "m5", lens_mm: float | None = None) -> list[dict]:
    """Camera plans for every room of ``level_id``.

    ``policy`` (docs/milestone6.md §1.3, §4): ``"m5"`` = the three fixed rules
    of Milestone 3-5 below (kept byte for byte: the realism A/B renders the
    M6 look from these cameras; the plans carry no ``shift``/``policy``
    fields, readers treat them as shift 0 and policy ``m5``; their lens is
    ``M5_LENS_MM``); ``"search"`` =
    the ray-cast camera search of ``camsearch.plan_level`` (1-3 views per
    room at 1.25 m, pitch 0, ``shift_y = -0.10``, with ``score`` and
    ``search_seconds``) with the lens of ``room_lens`` per room.

    ``lens_mm`` (Milestone 8): the brief's ``render.lens_mm`` for every
    searched room (None: the 18 / 16 mm rule of ``room_lens``); the ``m5``
    policy takes none (ValueError), its cameras are the committed M5 ones.
    """
    if policy not in CAMERA_POLICIES:
        raise ValueError(f"unknown camera policy {policy!r} (expected one of {CAMERA_POLICIES})")
    if lens_mm is not None:
        check_lens(lens_mm)
    if policy == "search":
        from wenart.blender import camsearch  # camsearch imports this module

        return camsearch.plan_level(building, level_id, lens_mm=lens_mm)
    if lens_mm is not None:
        raise ValueError(f"the m5 camera policy keeps its {M5_LENS_MM:g} mm lens; lens_mm {lens_mm!r} is for the "
                         f"search policy")
    level = next(lv for lv in building["levels"] if lv["id"] == level_id)
    floor_z = float(level["elevation"])
    plans = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        plans.extend(plan_room_cameras(room, building, floor_z))
    return plans


def rooms_without_view(building: dict, level_id: str, policy: str = "m5") -> list[dict]:
    """Rooms of ``level_id`` the policy gives no camera, with the reason (the scene manifest's
    ``rooms_without_view``): none for ``m5`` (three cameras per room), ``camsearch.rooms_without_view``
    for ``search`` (docs/milestone7.md §6.2)."""
    if policy not in CAMERA_POLICIES:
        raise ValueError(f"unknown camera policy {policy!r} (expected one of {CAMERA_POLICIES})")
    if policy != "search":
        return []
    from wenart.blender import camsearch  # camsearch imports this module

    return camsearch.rooms_without_view(building, level_id)


def check_lens(lens_mm) -> float:
    """``lens_mm`` as a float when it is a number in ``LENS_RANGE_MM`` (14-35 mm), else ValueError."""
    lo, hi = LENS_RANGE_MM
    if isinstance(lens_mm, bool) or not isinstance(lens_mm, (int, float)) or not math.isfinite(float(lens_mm)) \
            or not lo <= float(lens_mm) <= hi:
        raise ValueError(f"lens_mm must be a number from {lo:g} to {hi:g} mm, got {lens_mm!r}")
    return float(lens_mm)


def room_width(room: dict) -> float:
    """The room's width (metres): the diameter of the largest circle inside its polygon (twice the
    distance from ``lighting.polylabel``'s pole of inaccessibility to the nearest edge, to 1 cm; exact
    for a rectangle, whose width is its shorter side). An L-shaped or angled room is as wide as its
    widest part, not as its bounding rectangle: a narrow L hall is narrow."""
    from wenart.blender import lighting  # lighting imports this module

    polygon = [(float(p[0]), float(p[1])) for p in room["polygon"]]
    if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
        polygon = polygon[:-1]
    if len(polygon) < 3:
        return 0.0
    return 2.0 * max(0.0, float(lighting.polylabel(polygon)[2]))


def room_lens(room: dict, lens_mm: float | None = None) -> tuple[float, str]:
    """``(lens_mm, rule)`` of the searched cameras of ``room`` (docs/milestone8.md §5): the brief's
    ``lens_mm`` when given, else ``NARROW_LENS_MM`` (16 mm) for a room narrower than ``NARROW_ROOM_M``
    (2.2 m, ``room_width``), else ``LENS_MM`` (18 mm). ``rule`` says which (the plan's ``lens_rule``)."""
    if lens_mm is not None:
        return check_lens(lens_mm), "brief render.lens_mm"
    width = room_width(room)
    if width < NARROW_ROOM_M - 1e-9:
        return NARROW_LENS_MM, f"room width {width:.2f} m < {NARROW_ROOM_M:g} m"
    return LENS_MM, f"room width {width:.2f} m >= {NARROW_ROOM_M:g} m"


def mount_bottom(piece: dict) -> float:
    """How high a wall-hung piece hangs above the floor (``mount_bottom_m``, docs/milestone10.md §1.6b row 15:
    wall cabinets at 1.45 m); 0 for a piece standing on the floor. Wall-hung pieces are no floor obstacles."""
    v = piece.get("mount_bottom_m")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 else 0.0


def plan_room_cameras(room: dict, building: dict, floor_z: float) -> list[dict]:
    polygon = [tuple(p[:2]) for p in room["polygon"]]
    if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
        polygon = polygon[:-1]
    # Decor items (kind decor, when a stage lists them among the furniture)
    # are ignored: they sit on their hosts and never block a camera. Pieces
    # with build: false are not in the scene (Milestone 7).
    furniture = [f for f in building["furniture"] if f.get("room_id") == room["id"] and f.get("kind") != "decor"
                 and f.get("build", True) is not False]
    # Obstacles are the fitted boxes (library bbox x fit scale, parametric
    # box, proxy box), never smaller than the drawn footprint (milestone 4 §2).
    # Wall-hung pieces (mount_bottom_m, Milestone 10) are no floor obstacles.
    obstacles = [obstacle_rect(f) for f in furniture if mount_bottom(f) <= 0.0]
    # Boxes a camera at CAMERA_HEIGHT would be inside of: never allowed.
    tall = [obstacle_rect(f) for f in furniture if mount_bottom(f) <= 0.0 and piece_bbox(f)[2] >= CAMERA_HEIGHT]
    openings = room_openings(room, polygon, building)
    centroid = G.polygon_centroid(polygon)
    free = geom2d.free_points(polygon, obstacles)
    search = _Search(polygon, obstacles, tall, free, centroid)

    plans = []
    # 1. Free area, looking at the centre of the longest wall.
    a, b = geom2d.longest_edge(polygon)
    wall_mid = G.segment_midpoint(a, b)
    candidates = [p for p in free if G.distance(p, wall_mid) >= 1.0] or free
    if candidates:
        pos2, warning = max(candidates, key=lambda p: G.distance(p, wall_mid)), None
    else:
        pos2, warning = search.fallback(centroid, "no free point in the room")
    plans.append(_plan(room, 1, pos2, wall_mid, floor_z, warning, "free area -> longest wall"))

    # 2. From the door opening, looking at the centroid.
    doors = [o for o in openings if o["type"] in ("door", "opening")]
    if doors:
        door = max(doors, key=lambda o: (o["type"] == "door", o["width"]))
        options = _opening_points(door["center"], polygon, DOOR_INSETS, DOOR_SIDE_STEPS)
        pos2, warning = search.place(options, primary=1, anchor=door["center"], what=f"door camera {door['id']}")
        target = centroid
        if G.distance(pos2, centroid) < 0.3:
            target = wall_mid
        plans.append(_plan(room, 2, pos2, target, floor_z, warning, f"door {door['id']} -> centroid",
                           anchor=door["id"]))
    else:
        pos2, warning = search.fallback(centroid, "room has no door opening on its edges")
        plans.append(_plan(room, 2, pos2, wall_mid, floor_z, warning, "centroid fallback"))

    # 3. Next to the largest window, looking across the room.
    windows = [o for o in openings if o["type"] == "window"]
    if windows:
        win = max(windows, key=lambda o: o["width"])
        options = _opening_points(win["center"], polygon, WINDOW_INSETS, WINDOW_SIDE_STEPS)
        # Any of the three points at the nominal inset counts as the nominal placement.
        pos2, warning = search.place(options, primary=3, anchor=win["center"], what=f"window camera {win['id']}")
        # Look through the centroid to the far side of the room.
        far = (centroid[0] + (centroid[0] - pos2[0]) * 0.75, centroid[1] + (centroid[1] - pos2[1]) * 0.75)
        if G.distance(far, pos2) < 0.5:
            far = wall_mid
        plans.append(_plan(room, 3, pos2, far, floor_z, warning, f"window {win['id']} -> across",
                           anchor=win["id"]))
    else:
        pos2, warning = search.fallback(centroid, "room has no window on its edges")
        plans.append(_plan(room, 3, pos2, wall_mid, floor_z, warning, "centroid fallback"))

    # Frustum lists are limited to the camera's own room (its openings and its
    # furniture): walls hide everything else, so other rooms' pieces inside the
    # frustum would only mislead the final check.
    tangents = geom2d.frustum_tangents(M5_LENS_MM, SENSOR_MM, RESOLUTION)
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
                 floor_z + mount_bottom(f) + piece_bbox(f)[2] / 2.0),
                pos, tgt, tangents)
        ]
    return plans


class _Search:
    """Free-point search of one room: the candidates of a camera in order of
    preference, then the free-area grid, then the centroid, then any point
    clear of the tall proxies. Returns ``(point, warning)``; the warning is
    None only when a primary candidate was free."""

    def __init__(self, polygon, obstacles, tall, free, centroid):
        self.polygon, self.obstacles, self.tall, self.free, self.centroid = polygon, obstacles, tall, free, centroid

    def is_free(self, p, obstacles=None) -> bool:
        return geom2d.point_is_free(p, self.polygon, self.obstacles if obstacles is None else obstacles,
                                    CAMERA_WALL_CLEARANCE, CAMERA_OBSTACLE_CLEARANCE)

    def place(self, options, primary: int, anchor, what: str) -> tuple[tuple[float, float], str | None]:
        """First free option; the first ``primary`` options count as the
        nominal placement (no warning), later ones as a move."""
        for i, p in enumerate(options):
            if self.is_free(p):
                if i < primary:
                    return p, None
                return p, f"{what} moved: the nominal point is in a proxy footprint or too close to a wall"
        if self.free:
            p = min(self.free, key=lambda q: G.distance(q, anchor))
            return p, f"{what} moved to the nearest free point: no free point next to the opening"
        return self.fallback(self.centroid, f"{what}: no free point in the room")

    def fallback(self, point, reason: str) -> tuple[tuple[float, float], str]:
        """``point`` (the centroid) when it is clear of the tall proxies, else
        the nearest grid point that is; the warning says what happened."""
        if self.is_free(point, self.tall):
            return point, f"{reason}; camera at the centroid"
        clear = geom2d.free_points(self.polygon, self.tall, wall_clearance=CAMERA_WALL_CLEARANCE,
                                   obstacle_clearance=CAMERA_OBSTACLE_CLEARANCE)
        if clear:
            p = min(clear, key=lambda q: G.distance(q, point))
            return p, f"{reason}; centroid inside a tall proxy, camera at the nearest point clear of tall proxies"
        return point, f"{reason}; no point clear of the tall proxies, camera at the centroid INSIDE a proxy"


def room_openings(room: dict, polygon, building: dict) -> list[dict]:
    """Openings whose centre lies on an edge of the room polygon.

    The centre sits on (or, by the pipeline's tolerance, up to half a wall
    off) the wall centre line, i.e. up to ``thickness / 2`` plus that offset
    from the room edge on the inner wall face; the tolerance is derived per
    opening from its wall so thick walls keep their doors and windows.
    """
    walls = {w["id"]: w for w in building.get("walls", []) if w["level_id"] == room["level_id"]}
    out = []
    for o in building["openings"]:
        if o["level_id"] != room["level_id"]:
            continue
        tolerance = opening_edge_tolerance(o, walls)
        if _distance_to_edge_line(o["center"], polygon, tolerance) is not None:
            out.append(o)
    return out


def door_segments(room: dict, building: dict) -> list[tuple[str, tuple, tuple]]:
    """``[(door id, a, b)]``: the doors on the room's edges as segments on their wall's centre line, as wide as the
    door (pure; Milestone 11 §4.4 V1: a camera stays ``DOOR_CLEARANCE_M`` from a door leaf)."""
    from wenart.blender.shell import opening_centre_on_wall

    walls = {w["id"]: w for w in building.get("walls", []) if w["level_id"] == room["level_id"]}
    out = []
    for o in room_openings(room, [tuple(p[:2]) for p in room["polygon"]], building):
        wall = walls.get(o.get("wall_id"))
        if o.get("type") != "door" or wall is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        ux, uy = _unit(wall["start"], wall["end"])
        h = float(o["width"]) / 2.0
        out.append((o["id"], (cx - ux * h, cy - uy * h), (cx + ux * h, cy + uy * h)))
    return out


# Milestone 11 (docs/milestone11.md §4.4 V1): a camera stands at least this far from a door leaf.
DOOR_CLEARANCE_M = 0.6


def opening_rooms(building: dict, level_id: str | None = None) -> dict[str, list[str]]:
    """``{opening_id: [room_id, ...]}``: the rooms whose polygon edge carries
    each opening (``room_openings``), in building order; an opening between
    two rooms lists both, an opening no room carries gets ``[]``. Used for
    the ``room_ids`` of door and window entries (docs/milestone5.md §2.7)."""
    out: dict[str, list[str]] = {o["id"]: [] for o in building["openings"]
                                 if level_id is None or o["level_id"] == level_id}
    for room in building["rooms"]:
        if level_id is not None and room["level_id"] != level_id:
            continue
        polygon = [tuple(p[:2]) for p in room["polygon"]]
        if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
            polygon = polygon[:-1]
        if len(polygon) < 3:
            continue
        for o in room_openings(room, polygon, building):
            if o["id"] in out and room["id"] not in out[o["id"]]:
                out[o["id"]].append(room["id"])
    return out


def opening_edge_tolerance(opening: dict, walls: dict) -> float:
    """How far an opening centre may lie from a room edge: half its wall's
    thickness plus its offset from the wall centre line plus slack."""
    wall = walls.get(opening.get("wall_id"))
    if wall is None:
        return OPENING_EDGE_TOLERANCE
    offset = G.point_segment_distance(opening["center"], wall["start"], wall["end"])
    return float(wall["thickness"]) / 2.0 + offset + OPENING_EDGE_SLACK


def _distance_to_edge_line(p, polygon, tolerance: float) -> float | None:
    """Distance from ``p`` to the nearest polygon edge whose line is within
    ``tolerance`` and whose span (extended by the slack) covers the foot of
    the perpendicular; None when no edge qualifies. The span test keeps an
    opening of the next room, past the end of this room's edge, out."""
    best = None
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        along = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
        across = abs((p[0] - a[0]) * -uy + (p[1] - a[1]) * ux)
        if across <= tolerance and -OPENING_EDGE_SLACK <= along <= length + OPENING_EDGE_SLACK:
            if best is None or across < best:
                best = across
    return best


def _opening_points(center, polygon, insets, side_steps) -> list[tuple[float, float]]:
    """Candidate camera points in front of an opening: for each inset (into
    the room from the room edge) every side step along the edge, in the
    given order. The opening centre sits on the wall centre line, half a wall
    outside the room edge; the inset is measured from the room boundary."""
    edge = geom2d.nearest_edge(center, polygon)[1]
    nx, ny = geom2d.inward_normal(edge[0], edge[1], polygon)
    ax, ay = _unit(edge[0], edge[1])
    d = G.point_segment_distance(center, edge[0], edge[1])
    points = []
    for inset in insets:
        base = (center[0] + nx * (d + inset), center[1] + ny * (d + inset))
        for step in side_steps:
            points.append((base[0] + ax * step, base[1] + ay * step))
    return points


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
        "lens_mm": M5_LENS_MM, "sensor_mm": SENSOR_MM, "resolution": list(RESOLUTION),
        "placement": how, "anchor": anchor, "warning": warning,
        "visible_openings": [], "visible_furniture": [],
    }


def create_cameras(plans: list[dict], collection, manifest_objects: list) -> list:
    """Create a Blender camera object per plan (needs bpy).

    The lens shift of a plan (``shift_x``/``shift_y``, in units of the image
    width; absent = 0 for the M5 plans) goes to ``Camera.shift_x/shift_y``;
    the projection readers use the same convention (docs/milestone6.md §1.3)."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common

    created = []
    for plan in plans:
        cam = bpy.data.cameras.new(plan["name"])
        cam.lens = plan["lens_mm"]
        cam.sensor_width = plan["sensor_mm"]
        cam.sensor_fit = "HORIZONTAL"
        cam.shift_x = float(plan.get("shift_x") or 0.0)
        cam.shift_y = float(plan.get("shift_y") or 0.0)
        cam.clip_start = 0.05
        cam.clip_end = 200.0
        ob = bpy.data.objects.new(plan["name"], cam)
        ob.location = Vector(plan["position"])
        direction = Vector(plan["target"]) - Vector(plan["position"])
        ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        collection.objects.link(ob)
        common.set_props(ob, wenart_id=plan["name"], kind="camera", status="assumed")
        ob["wenart_room"] = plan["room_id"]
        ob["wenart_level"] = plan["level_id"]
        manifest_objects.append({
            "name": plan["name"], "wenart_id": plan["name"], "kind": "camera", "status": "assumed",
            "level_id": plan["level_id"], "element_id": plan["room_id"], "evidence": [],
            "material": None, "textured": False, "pass_index": None, "assumed": {},
        })
        created.append(ob)
    return created
