"""Building shell: walls with boolean-cut openings, door and window geometry,
floors and ceilings (docs/milestone3.md §3, shell.py).

Walls: one object per wall element (named by its id, so every object stays
traceable and the per-kind counts match the JSON), an extruded rectangle from
the centre line, thickness and height, grouped in one collection per level.
Faces get material slots by what they face: interior (style walls), exterior
(``plaster_exterior`` for the outward faces of exterior walls) or wet-room
(``wet_walls`` for faces looking into a bathroom / wc / kitchen).

Openings: a boolean difference per opening with a cutter box of
width x (thickness + 2 cm) x height centred on the wall centre line; doors
start at the floor, windows at the sill. The JSON centre is projected onto
the wall centre line first (a door block inserted on the wall face is the
normal CAD convention and the ingest accepts it); the shift is recorded as
``center_shift`` in the manifest, as ``assumed`` when it exceeds 1 mm and as a
warning when it exceeds half the wall thickness. The cutters are temporary
objects, the modifiers are applied through the depsgraph
(``common.evaluated_mesh``), then the cutters are deleted. The EXACT solver
is the default in Blender 5.2 (solver items: FLOAT, EXACT, MANIFOLD).

Every door and plain opening gets a threshold face (``<id>_threshold``, kind
``floor``, the material of the adjacent room floor) because the room floors
stop at the wall faces and the cutter removes the wall bottom. A plain
opening without a height is cut through the full wall height; on a level
with nothing above it a soffit face (``<id>_soffit``, kind ``ceiling``)
closes the wall top over the opening.

The outward side of an exterior wall is found by probing both sides of the
wall against the room polygons of the level (the side that lies in no room
is outside); when both or neither side is in a room the bounding-box centre
of the level decides and a warning is recorded.

Defaults for ``null`` values are recorded as ``assumed`` in the manifest:
door height 2.10 m, window sill 0.90 m, window height 1.20 m (1.40 m when the
opening is wider than 1.5 m), plain opening full height, wall height = level
ceiling height, slab thickness 0.30 m (walls of a level with a level above
it run up to the next floor so the slab zone is closed).

Milestone 6 (docs/milestone6.md §5 rows 3 and 9):

- before the per-face material probe, every wall mesh is cut with vertical
  planes across the wall (``bmesh.ops.bisect_plane``) at every room corner
  that lies along the wall (``wall_split_positions``), so a wall shared by a
  bathroom and a bedroom gets tiles on the bathroom span only (one face
  used to take the material of its centre);
- wood door leaves take the veneer of their wood (``vocabulary.veneer_for``,
  grain along the box UV v = world Z: vertical) and get a pair of steel
  lever handles at 1.02 m on both faces (``door_handle_parts``; the door's
  wenart id and pass index, so ``--hide`` hides them with the door);
- dry rooms get a painted skirting board 8 cm x 12 mm along their walls,
  interrupted at doors, plain openings and floor-level windows
  (``skirting_spans``), pass index 0;
- handles and skirting are design details: status ``assumed``, a scene
  manifest ``assumed`` entry with ``parent`` (door or room id), ``kind`` and
  ``reason``; nothing is added to the building JSON.

Milestone 7 (docs/milestone7.md §6.4):

- doorless openings (type ``opening``) are cut to their ``height`` (the
  recognition core writes 2.10 m and lists it in the opening's ``assumed``;
  every field listed there is recorded as assumed here too), with the
  threshold face and no frame or leaf; without a height they still run to
  the wall top (Milestone 3);
- virtual separators (``virtual: true``, ``wall_id: null``) have no
  geometry: a manifest entry (``has_geometry: false``, ``virtual``,
  ``line``) and nothing else; the room floors and ceilings meet at the line;
  the skirting stops along it. An opening without a wall that is not
  virtual is a warning, never a crash;
- stairs (``furniture`` of type ``stair``) are fixed equipment built here,
  not by furniture.py: ``plan_stairs`` (pure: rise = ceiling + the assumed
  0.15 m slab, or floor to floor when a level lies above) and
  ``build_stairs`` (steps, landing, rails as ``furn_<id>``: kind
  ``furniture``, the piece's pass index; the shaft and cap that close the
  ceiling opening as ``<id>_void``: kind ``ceiling``, status ``assumed``);
  ``build_floors_ceilings(..., stairs=)`` cuts the opening out of every
  ceiling it crosses (``geom2d.polygon_faces``); pieces with ``build:
  false`` are not built and listed;
- dining and prayer rooms take the living-room slots (``slot_room_type``):
  dry floor, plain walls, skirting.
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import parametric as P

DEFAULTS = {
    "door_height": 2.10,
    "window_sill": 0.90,
    "window_height": 1.20,
    "window_height_wide": 1.40,
    "window_wide_threshold": 1.5,
    "slab_thickness": 0.30,
    "frame_width": 0.05,
    "leaf_thickness": 0.04,
    "glass_thickness": 0.006,
    "cutter_extra": 0.02,
    "face_probe": 0.05,          # distance beyond a wall face for the room probes
    "threshold_lift": 0.001,     # thresholds above a stacked wall top (no coplanar faces)
    "shift_assumed": 0.001,      # centre shift recorded as assumed above this
}
WET_ROOM_TYPES = {"bathroom", "wc", "kitchen"}
# Rooms without skirting: wet rooms keep their tiles to the floor, a balcony is outside.
NO_SKIRTING_TYPES = WET_ROOM_TYPES | {"balcony"}
# Milestone 7 room types that take another type's material slots (docs/milestone7.md §6.4).
ROOM_SLOT_TYPES = {"dining": "living", "prayer": "living"}
SKIRTING_H = 0.08
SKIRTING_T = 0.012
SKIRTING_MIN_SPAN = 0.02
# A room corner splits a wall when it lies within half the wall thickness + this of the centre line
# and this far from the wall's ends.
SPLIT_REACH_EXTRA = 0.1
SPLIT_END_MARGIN = 0.01
# Lever handles (docs/milestone6.md §5 row 9): lever axis this high above the floor, this far
# from the latch-side edge of the leaf; the furthest point stands HANDLE_DEPTH proud of the leaf face.
HANDLE_HEIGHT = 1.02
HANDLE_EDGE_INSET = 0.075
HANDLE_DEPTH = 0.055


def slot_room_type(room_type: str | None) -> str | None:
    """The room type whose material slots a room uses: dining and prayer rooms the living room's."""
    return ROOM_SLOT_TYPES.get(room_type, room_type)


def is_virtual(opening: dict) -> bool:
    """A virtual separator (docs/milestone7.md §2.7.1): ``virtual: true`` with no wall; it has no geometry."""
    return bool(opening.get("virtual")) and opening.get("wall_id") is None


# --------------------------------------------------------------------------
# Opening sizes (pure Python, used by shell and the tests)
# --------------------------------------------------------------------------

def opening_vertical(opening: dict, level: dict, levels_above: bool) -> tuple[float, float, dict]:
    """``(bottom_z, top_z, assumed)`` of an opening in world Z.

    ``assumed`` lists the defaults that filled ``null`` fields of the JSON
    and the values the JSON itself lists as assumed (Milestone 7: the
    opening's ``assumed`` list, e.g. a doorless gap's 2.10 m height)."""
    floor_z = float(level["elevation"])
    ceiling = float(level["ceiling_height"])
    assumed = {}
    kind = opening["type"]
    height = opening.get("height")
    sill = opening.get("sill_height")
    listed = opening.get("assumed") or ()
    for field, value in (("height", height), ("sill_height", sill)):
        if field in listed and value is not None:
            assumed[field] = float(value)
    if kind == "door":
        if sill is None:
            sill = 0.0
        if height is None:
            height = DEFAULTS["door_height"]
            assumed["height"] = height
    elif kind == "window":
        if sill is None:
            sill = DEFAULTS["window_sill"]
            assumed["sill_height"] = sill
        if height is None:
            wide = float(opening["width"]) > DEFAULTS["window_wide_threshold"]
            height = DEFAULTS["window_height_wide"] if wide else DEFAULTS["window_height"]
            assumed["height"] = height
    else:  # plain opening: full height unless the JSON says otherwise
        if sill is None:
            sill = 0.0
        if height is None:
            height = ceiling - float(sill)
            assumed["height"] = height
    bottom = floor_z + float(sill)
    if kind == "opening":
        # Runs up to the ceiling; build_walls cuts through the wall top when the
        # opening reaches it and build_openings closes it with a soffit face.
        top = min(bottom + float(height), floor_z + ceiling)
    else:
        # A door or window taller than the ceiling stops 1 mm below it so the
        # cutter never shares a face with the wall top.
        top = min(bottom + float(height), floor_z + ceiling - 0.001)
    return bottom, top, assumed


def wall_height(wall: dict, level: dict, has_level_above: bool) -> tuple[float, dict]:
    """Wall height and the assumptions used."""
    assumed = {}
    h = wall.get("height")
    if h is None:
        h = float(level["ceiling_height"])
        assumed["height"] = h
    h = float(h)
    if has_level_above:
        h += DEFAULTS["slab_thickness"]
        assumed["slab_thickness"] = DEFAULTS["slab_thickness"]
    return h, assumed


def opening_centre_on_wall(opening: dict, wall: dict) -> tuple[float, float, float]:
    """``(cx, cy, shift)``: the opening centre projected onto the wall centre
    line and the distance it moved. A door block drawn on the wall face sits
    half a thickness off the centre line; the cutter and the frame must still
    be centred in the wall."""
    ax, ay = float(wall["start"][0]), float(wall["start"][1])
    bx, by = float(wall["end"][0]), float(wall["end"][1])
    px, py = float(opening["center"][0]), float(opening["center"][1])
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-12:
        return px, py, 0.0
    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    cx, cy = ax + t * dx, ay + t * dy
    return cx, cy, math.hypot(px - cx, py - cy)


def cut_full_height(top: float, floor_z: float, wall_h: float) -> bool:
    """True when an opening reaches the top of its wall (plain opening on a
    level with nothing above): the cutter then runs through the wall top."""
    return top >= floor_z + wall_h - 1e-6


def wall_outward_normal(wall: dict, rooms: list[dict], level_centre) -> tuple[tuple[float, float], bool]:
    """``((nx, ny), ambiguous)``: unit normal pointing to the outside of a wall.

    Three points along the wall are probed ``face_probe`` beyond each face
    against the room polygons; the side with fewer room hits is outside. When
    both sides score the same (no rooms, or rooms on both sides) the side away
    from ``level_centre`` is used and ``ambiguous`` is True."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    polys = [r["polygon"] for r in rooms if len(r["polygon"]) >= 3]
    hits = {1: 0, -1: 0}
    for t in (0.25, 0.5, 0.75):
        px, py = G.point_along_segment(wall["start"], wall["end"], t)
        for side in (1, -1):
            probe = (px + side * nx * reach, py + side * ny * reach)
            if any(G.point_in_polygon(probe, poly) for poly in polys):
                hits[side] += 1
    if hits[1] != hits[-1]:
        side = 1 if hits[1] < hits[-1] else -1
        return (side * nx, side * ny), False
    mid = G.segment_midpoint(wall["start"], wall["end"])
    side = -1 if (level_centre[0] - mid[0]) * nx + (level_centre[1] - mid[1]) * ny > 0 else 1
    return (side * nx, side * ny), True


def adjacent_room(centre, wall: dict, rooms: list[dict]) -> dict | None:
    """The room next to an opening: the left side of the wall direction is
    probed first, then the right. None when no room polygon is there."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    for side in (1, -1):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        for room in rooms:
            if len(room["polygon"]) >= 3 and G.point_in_polygon(probe, room["polygon"]):
                return room
    return None


# --------------------------------------------------------------------------
# Milestone 6 design details and wall splits (pure Python)
# --------------------------------------------------------------------------

def wall_split_positions(wall: dict, rooms: list[dict], reach_extra: float = SPLIT_REACH_EXTRA,
                         end_margin: float = SPLIT_END_MARGIN) -> list[float]:
    """Distances along the wall (from ``wall["start"]``, metres, sorted, 0.1 mm
    rounded) of the room corners that lie along it: within ``thickness / 2 +
    reach_extra`` of the centre line and more than ``end_margin`` inside its
    ends. The wall mesh is cut across at each (docs/milestone6.md §5 row 3)."""
    a, b = wall["start"], wall["end"]
    length = G.distance(a, b)
    if length < 1e-6:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    reach = float(wall["thickness"]) / 2.0 + reach_extra
    cuts = set()
    for room in rooms:
        for p in room["polygon"]:
            along = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
            across = abs((p[0] - a[0]) * -uy + (p[1] - a[1]) * ux)
            if end_margin < along < length - end_margin and across <= reach:
                cuts.add(round(along, 4))
    return sorted(cuts)


def door_handle_parts(width: float, height: float, sill: float = 0.0,
                      leaf_thickness: float = DEFAULTS["leaf_thickness"],
                      frame_width: float = DEFAULTS["frame_width"]) -> list[tuple[list, list]]:
    """Boxes of a pair of lever handles in the opening's local frame (X along
    the wall, Y across, Z up from the opening bottom; ``geom2d.box`` tuples):
    on both leaf faces a rose plate, a neck and a 13 cm lever whose axis is
    ``HANDLE_HEIGHT`` above the floor (``sill`` = opening bottom above the
    floor), ``HANDLE_EDGE_INSET`` from the latch-side (+X) edge of the leaf.
    The lever's far side stands ``HANDLE_DEPTH`` proud of the leaf face. A
    door lower than 1.3 m gets its handles at half height."""
    lt = float(leaf_thickness)
    hx = width / 2.0 - frame_width - HANDLE_EDGE_INSET
    lever_z = HANDLE_HEIGHT - float(sill) if height >= 1.3 else height / 2.0
    parts = []
    for sgn in (1.0, -1.0):
        parts.append(geom2d.box((hx, sgn * (lt / 2.0 + 0.004), lever_z - 0.04), (0.05, 0.008, 0.16)))   # rose
        parts.append(geom2d.box((hx, sgn * (lt / 2.0 + 0.026), lever_z), (0.018, 0.044, 0.018)))        # neck
        parts.append(geom2d.box((hx - 0.055, sgn * (lt / 2.0 + HANDLE_DEPTH - 0.009), lever_z),
                                (0.13, 0.018, 0.018)))                                                 # lever
    return parts


def skirting_spans(polygon, gaps, min_span: float = SKIRTING_MIN_SPAN) -> list[tuple[int, float, float]]:
    """Where a skirting board runs along a room polygon: ``[(edge index, s0, s1)]``
    with ``s0 < s1`` in metres from the edge's first corner. ``gaps`` are
    ``(centre, width)`` of the doors and openings of the room; each is cut
    from the edge nearest to its centre (centre projected onto the edge,
    +- width / 2). Spans shorter than ``min_span`` are dropped."""
    poly = [tuple(p[:2]) for p in polygon]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    n = len(poly)
    cuts: dict[int, list[tuple[float, float]]] = {i: [] for i in range(n)}
    for centre, width in gaps:
        dists = [G.point_segment_distance(centre[:2], poly[i], poly[(i + 1) % n]) for i in range(n)]
        i = min(range(n), key=lambda k: (dists[k], k))
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        along = ((centre[0] - a[0]) * (b[0] - a[0]) + (centre[1] - a[1]) * (b[1] - a[1])) / length
        cuts[i].append((along - float(width) / 2.0, along + float(width) / 2.0))
    spans = []
    for i in range(n):
        length = G.distance(poly[i], poly[(i + 1) % n])
        start = 0.0
        for c0, c1 in sorted(cuts[i]):
            if c0 - start >= min_span:
                spans.append((i, round(start, 6), round(min(c0, length), 6)))
            start = max(start, c1)
        if length - start >= min_span:
            spans.append((i, round(start, 6), round(length, 6)))
    return spans


def skirting_gaps(openings: list[dict], level: dict, levels_above: bool) -> list[tuple[list, float]]:
    """``(centre, width)`` of the openings that interrupt a room's skirting:
    doors, plain openings and windows reaching below the board; a virtual
    separator by its whole ``line`` (no wall there, so no board along it)."""
    floor_z = float(level["elevation"])
    gaps = []
    for o in openings:
        line = o.get("line")
        if is_virtual(o) and isinstance(line, (list, tuple)) and len(line) == 2:
            (ax, ay), (bx, by) = line[0][:2], line[1][:2]
            gaps.append(([(ax + bx) / 2.0, (ay + by) / 2.0], G.distance((ax, ay), (bx, by))))
            continue
        bottom, _top, _ = opening_vertical(o, level, levels_above)
        if o["type"] in ("door", "opening") or bottom - floor_z < SKIRTING_H:
            gaps.append((o["center"], float(o["width"])))
    return gaps


def skirting_boxes(polygon, spans, floor_z: float, height: float = SKIRTING_H,
                   thickness: float = SKIRTING_T) -> tuple[list, list]:
    """``(verts, faces)`` of the skirting boards of ``spans`` (``skirting_spans``):
    one box per span, ``thickness`` deep into the room from the polygon edge,
    ``height`` tall from ``floor_z``."""
    poly = [tuple(p[:2]) for p in polygon]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    n = len(poly)
    parts = []
    for i, s0, s1 in spans:
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = geom2d.inward_normal(a, b, poly)
        mid = (s0 + s1) / 2.0
        centre = (a[0] + ux * mid + nx * thickness / 2.0, a[1] + uy * mid + ny * thickness / 2.0,
                  floor_z + height / 2.0)
        parts.append(geom2d.box(centre, (s1 - s0, thickness, height), math.degrees(math.atan2(uy, ux))))
    return geom2d.merge(parts)


# --------------------------------------------------------------------------
# Walls
# --------------------------------------------------------------------------

def trim_wall_overlaps(walls: list[dict]) -> dict[str, dict]:
    """Shorten wall centre lines where two wall rectangles overlap in volume
    (L-corners of exterior walls drawn as two full-length rectangles).

    Coincident faces of overlapping boxes self-shadow and z-fight in Cycles.
    Where an end edge of wall B lies entirely inside wall A's rectangle, B's
    centre line is cut back to the point where it enters A, so the union of
    the two boxes is unchanged while no faces coincide. At an L-corner both
    ends lie inside each other; the wall with the larger id is trimmed.
    Returns ``{wall_id: {"start": [..], "end": [..], "trimmed": [notes]}}``
    for every wall (untouched walls keep their JSON points).
    """
    out = {w["id"]: {"start": list(w["start"]), "end": list(w["end"]), "trimmed": []} for w in walls}
    ordered = sorted(walls, key=lambda w: w["id"])
    for b in ordered:
        for a in ordered:
            if a["id"] == b["id"]:
                continue
            if a["id"] > b["id"] and _end_inside(a, b):
                continue  # the pair is handled when the roles are swapped
            rect_a = G.centerline_to_rectangle(a["start"], a["end"], a["thickness"])
            cur = out[b["id"]]
            for which in ("start", "end"):
                other = "end" if which == "start" else "start"
                p, q = cur[which], cur[other]
                corners = _end_edge(p, q, b["thickness"])
                if not all(_in_rect(c, rect_a) for c in corners):
                    continue
                t = _exit_parameter(p, q, rect_a)
                if t is None or t <= 1e-6 or t >= 0.999:
                    continue
                new_p = G.point_along_segment(p, q, t)
                cut = G.distance(p, new_p)
                cur[which] = [G.snap(new_p[0]), G.snap(new_p[1])]
                cur["trimmed"].append(f"{which} cut back {cut:.3f} m at the overlap with {a['id']} (union unchanged)")
    return out


def _end_inside(a: dict, b: dict) -> bool:
    """True when an end edge of wall A lies inside wall B's rectangle."""
    rect_b = G.centerline_to_rectangle(b["start"], b["end"], b["thickness"])
    for p, q in ((a["start"], a["end"]), (a["end"], a["start"])):
        if all(_in_rect(c, rect_b) for c in _end_edge(p, q, a["thickness"])):
            return True
    return False


def _end_edge(p, q, thickness: float) -> list[tuple[float, float]]:
    nx, ny = G.unit_normal_left(p, q)
    h = thickness / 2.0
    return [(p[0] + nx * h, p[1] + ny * h), (p[0] - nx * h, p[1] - ny * h)]


def _in_rect(point, rect, tol: float = 1e-6) -> bool:
    """Point inside a convex quadrilateral (or on its boundary within tol)."""
    sign = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
        if abs(cross) <= tol:
            continue
        s = cross > 0
        if sign is None:
            sign = s
        elif s != sign:
            return False
    return True


def _exit_parameter(p, q, rect) -> float | None:
    """Parameter t along p->q where the segment leaves the convex rect (p inside)."""
    best = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        t = _segment_intersection_t(p, q, a, b)
        if t is not None and t > 1e-9 and (best is None or t < best):
            best = t
    return best


def _segment_intersection_t(p, q, a, b) -> float | None:
    dx, dy = q[0] - p[0], q[1] - p[1]
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-12:
        return None
    t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
    u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
    if -1e-9 <= u <= 1 + 1e-9 and 0 <= t <= 1 + 1e-9:
        return t
    return None


def build_walls(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                assumed: list, warnings: list) -> list:
    """Create the wall objects of a level with their openings cut."""
    import bpy

    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    walls = [w for w in building["walls"] if w["level_id"] == level_id]
    openings = [o for o in building["openings"] if o["level_id"] == level_id]
    rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
    wall_by_id = {w["id"]: w for w in walls}

    # No walls.tint since Milestone 5 (§2.2): the flat albedo mode gives the wall colour;
    # build.load_style warns when an old style file still carries one.
    wall_mat = library.get(style["walls"]["material"], style["walls"].get("asset"))
    ext_mat = library.get("plaster_exterior")
    wet = style.get("wet_walls") or style["walls"]
    wet_mat = library.get(wet["material"], wet.get("asset"))
    slots = [wall_mat, ext_mat, wet_mat]

    footprint_centre = _level_centre(walls)
    trims = trim_wall_overlaps(walls)
    objects = []
    pairs = []  # (object, wall) for the face classification after the booleans
    cutters = []
    for wall in walls:
        height, wall_assumed = wall_height(wall, level, has_above)
        start, end = trims[wall["id"]]["start"], trims[wall["id"]]["end"]
        length = G.distance(start, end)
        if length < 1e-6:
            warnings.append(f"{wall['id']}: zero-length wall skipped")
            continue
        mid = G.segment_midpoint(start, end)
        angle = G.segment_angle_deg(start, end)
        verts, faces = geom2d.box((mid[0], mid[1], floor_z + height / 2.0),
                                  (length, float(wall["thickness"]), height), angle)
        ob = common.new_mesh_object(wall["id"], verts, faces, collection=collection, wenart_id=wall["id"],
                                    kind="wall", status=wall.get("status", "verified"), materials=slots)
        objects.append(ob)
        pairs.append((ob, wall))

        # Cutters for the openings of this wall (a virtual separator has no wall: never cut).
        for opening in openings:
            if opening.get("wall_id") != wall["id"]:
                continue
            bottom, top, _ = opening_vertical(opening, level, has_above)
            extra = DEFAULTS["cutter_extra"]
            # Door cutters start a little below the floor so no coplanar faces
            # remain; an opening that reaches the wall top also runs above it.
            cut_bottom = bottom if opening["type"] == "window" else bottom - extra
            cut_top = top + extra if cut_full_height(top, floor_z, height) else top
            cx, cy, _shift = opening_centre_on_wall(opening, wall)  # shift recorded in build_openings
            cv, cf = geom2d.box((cx, cy, (cut_bottom + cut_top) / 2.0),
                                (float(opening["width"]), float(wall["thickness"]) + extra, cut_top - cut_bottom),
                                angle)
            cutter = common.new_mesh_object(f"cut_{opening['id']}", cv, cf, collection=collection,
                                            wenart_id=opening["id"], kind="opening", status="assumed")
            cutter.hide_render = True
            cutters.append(cutter)
            mod = ob.modifiers.new(name=f"cut_{opening['id']}", type="BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.object = cutter

        manifest_objects.append({
            "name": wall["id"], "wenart_id": wall["id"], "kind": "wall",
            "status": wall.get("status", "verified"), "level_id": level_id, "element_id": wall["id"],
            "evidence": wall.get("evidence", []), "material": wall_mat.name,
            "textured": library.textured(wall_mat),
            "pass_index": None, "assumed": wall_assumed,
            "trimmed": trims[wall["id"]]["trimmed"],
            "start": trims[wall["id"]]["start"], "end": trims[wall["id"]]["end"],
            "thickness": wall["thickness"], "height": height,
        })
        for field, value in wall_assumed.items():
            assumed.append({"object": wall["id"], "field": field, "value": value,
                            "reason": "wall height from the level ceiling height" if field == "height"
                            else "slab between levels"})

    # Apply the booleans through the depsgraph, split at the room corners and classify faces.
    bpy.context.view_layer.update()
    for ob, wall in pairs:
        changed = False
        if ob.modifiers:
            mesh = common.evaluated_mesh(ob)
            common.replace_mesh(ob, mesh)
            # The boolean appends the cutter's (empty) material slot; drop it.
            while len(mesh.materials) > len(slots) or any(m is None for m in mesh.materials):
                idx = next((i for i, m in enumerate(mesh.materials) if m is None), len(mesh.materials) - 1)
                mesh.materials.pop(index=idx)
            changed = True
        cuts = split_wall_at_room_corners(ob, wall, rooms)
        if cuts:
            changed = True
            for entry in manifest_objects:
                if entry.get("kind") == "wall" and entry.get("wenart_id") == wall["id"]:
                    entry["split_at_m"] = cuts
        if changed:
            common.assign_box_uvs(ob.data)
        outward, ambiguous = wall_outward_normal(wall, rooms, footprint_centre)
        if ambiguous and wall.get("exterior"):
            warnings.append(f"{wall['id']}: exterior wall with rooms on both sides or on neither; "
                            f"outward side taken from the level centre")
        _assign_wall_face_materials(ob, wall, rooms, outward)
    for cutter in cutters:
        common.delete_object(cutter)
    bpy.context.view_layer.update()
    return objects


def split_wall_at_room_corners(ob, wall: dict, rooms: list[dict]) -> list[float]:
    """Cut the wall mesh with a vertical plane across the wall at every
    ``wall_split_positions`` distance (``bmesh.ops.bisect_plane``, nothing
    removed), so each face lies along one room and takes that room's material.
    Returns the distances cut (empty when none)."""
    import bmesh
    from mathutils import Vector

    cuts = wall_split_positions(wall, rooms)
    if not cuts:
        return []
    a, b = wall["start"], wall["end"]
    length = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for along in cuts:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((a[0] + ux * along, a[1] + uy * along, 0.0)),
                               plane_no=Vector((ux, uy, 0.0)))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return cuts


def _level_centre(walls: list[dict]) -> tuple[float, float]:
    pts = [w["start"] for w in walls] + [w["end"] for w in walls]
    if not pts:
        return (0.0, 0.0)
    box = G.bbox(pts)
    return G.box_center(box)


def _assign_wall_face_materials(ob, wall: dict, rooms: list[dict], outward) -> None:
    """Slot 0 interior, 1 exterior (faces of exterior walls whose normal
    points ``outward``, see ``wall_outward_normal``), 2 wet-room faces."""
    mesh = ob.data
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    wet_polys = [r["polygon"] for r in rooms if slot_room_type(r.get("room_type")) in WET_ROOM_TYPES]
    for poly in mesh.polygons:
        n = poly.normal
        if abs(n.z) > 0.5 or abs(n.x * nx + n.y * ny) < 0.5:
            poly.material_index = 0  # top, bottom, jambs, end faces
            continue
        if wall.get("exterior") and (n.x * outward[0] + n.y * outward[1]) > 0.5:
            poly.material_index = 1
            continue
        c = poly.center
        probe = (c.x + n.x * 0.05, c.y + n.y * 0.05)
        poly.material_index = 2 if any(G.point_in_polygon(probe, p) for p in wet_polys) else 0


# --------------------------------------------------------------------------
# Doors and windows
# --------------------------------------------------------------------------

def build_openings(building: dict, level: dict, collection, library, style: dict, pass_indices: dict,
                   manifest_objects: list, assumed: list, warnings: list) -> list:
    """Door frame + leaf and window frame + glass per opening (plain openings
    are only the hole in the wall and get no object)."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    has_below = any(float(lv["elevation"]) < floor_z for lv in building["levels"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
    trim = style.get("trim") or {"material": "painted_wood_white"}
    door_style = style.get("door") or {"material": "wood_oak_light"}
    win_style = style.get("window_frame") or {"material": "painted_metal_white"}
    frame_mat = library.get(trim["material"], trim.get("asset"), trim.get("tint"))
    leaf_slug, leaf_asset = door_leaf_material(door_style)
    leaf_mat = library.get(leaf_slug, leaf_asset, door_style.get("tint"))
    win_mat = library.get(win_style["material"], win_style.get("asset"), win_style.get("tint"))
    glass_mat = library.glass()
    steel_mat = library.get("steel_brushed")

    created = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id:
            continue
        if is_virtual(opening):
            # A separator line between two rooms where no wall exists: no geometry at all.
            manifest_objects.append(separator_entry(opening, level_id))
            continue
        wall = walls.get(opening.get("wall_id"))
        if wall is None:
            warnings.append(f"{opening['id']}: wall {opening.get('wall_id')} not found on {level_id}; "
                            f"opening not built")
            continue
        bottom, top, op_assumed = opening_vertical(opening, level, has_above)
        listed = opening.get("assumed") or ()
        for field, value in op_assumed.items():
            assumed.append({"object": opening["id"], "field": field, "value": value,
                            "reason": f"{opening['type']} {field} listed as assumed in the building JSON"
                            if field in listed else f"{opening['type']} {field} not in the JSON; default"})
        angle = G.segment_angle_deg(wall["start"], wall["end"])
        width = float(opening["width"])
        thickness = float(wall["thickness"])
        status = opening.get("status", "verified")
        # The centre is used on the wall centre line; an off-centre JSON centre
        # (block on the wall face) is recorded, never silently moved.
        cx, cy, shift = opening_centre_on_wall(opening, wall)
        if shift > DEFAULTS["shift_assumed"]:
            op_assumed["center_shift"] = round(shift, 4)
            assumed.append({"object": opening["id"], "field": "center_shift", "value": round(shift, 4),
                            "reason": f"opening centre {shift * 1000:.0f} mm off the centre line of "
                                      f"{wall['id']}; projected onto it"})
            if shift > thickness / 2.0:
                warnings.append(f"{opening['id']}: centre {shift:.3f} m off the centre line of {wall['id']}, "
                                f"more than half its thickness ({thickness:.3f} m); projected onto the wall")

        if opening["type"] in ("door", "opening"):
            # Threshold: the room floors stop at the wall faces and the cutter
            # removes the wall bottom, so the footprint needs its own floor face.
            created.append(_threshold(opening, wall, (cx, cy), angle, floor_z, has_below, rooms, style, library,
                                      collection, manifest_objects, warnings, op_assumed, shift))
        if opening["type"] == "opening":
            wall_h, _ = wall_height(wall, level, has_above)
            if cut_full_height(top, floor_z, wall_h):
                # Nothing above the wall: close the wall top over the opening.
                created.append(_soffit(opening, wall, (cx, cy), angle, floor_z + wall_h, style, library,
                                       collection, manifest_objects, op_assumed, shift))
            manifest_objects.append(_opening_entry(opening, None, level_id, None, False, None, op_assumed, shift))
            continue
        fw = DEFAULTS["frame_width"]
        height = top - bottom
        index = len(pass_indices) + 1
        pass_indices[opening["id"]] = index

        if opening["type"] == "door":
            # Frame: two jambs and a head, as deep as the wall.
            parts = [
                geom2d.box((-(width / 2.0 - fw / 2.0), 0.0, height / 2.0), (fw, thickness, height)),
                geom2d.box((width / 2.0 - fw / 2.0, 0.0, height / 2.0), (fw, thickness, height)),
                geom2d.box((0.0, 0.0, height - fw / 2.0), (width - 2 * fw, thickness, fw)),
            ]
            frame = _local_to_world(parts, (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[frame_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, frame_mat.name,
                                                   _textured(library, frame_mat), index, op_assumed, shift))
            # Leaf: closed (0 deg), slightly smaller than the frame opening.
            leaf = _local_to_world([geom2d.box((0.0, 0.0, (height - fw) / 2.0),
                                               (width - 2 * fw - 0.01, DEFAULTS["leaf_thickness"], height - fw - 0.01))],
                                   (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_leaf", *leaf, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[leaf_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, leaf_mat.name,
                                                   _textured(library, leaf_mat), index, op_assumed, shift))
            # Lever handles on both faces: a design detail of the door (its id and pass index).
            handles = _local_to_world(door_handle_parts(width, height, bottom - floor_z), (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_handle", *handles, collection=collection,
                                        wenart_id=opening["id"], kind="door", status="assumed",
                                        materials=[steel_mat])
            ob.pass_index = index
            created.append(ob)
            reason = "design detail of the documented door (lever handles on both faces); not in the documents"
            entry = _opening_entry(opening, ob.name, level_id, steel_mat.name, False, index, {}, shift)
            entry.update(status="assumed", evidence=[], parent=opening["id"],
                         assumed={"detail": "door_handles", "lever_height_m": HANDLE_HEIGHT, "reason": reason})
            manifest_objects.append(entry)
            assumed.append({"object": ob.name, "field": "door_handles",
                            "value": f"steel lever pair at {HANDLE_HEIGHT} m", "reason": reason,
                            "parent": opening["id"], "kind": "door_handles"})
        else:
            depth = min(thickness, 0.08)
            parts = [
                geom2d.box((-(width / 2.0 - fw / 2.0), 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((width / 2.0 - fw / 2.0, 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((0.0, 0.0, height - fw / 2.0), (width - 2 * fw, depth, fw)),
                geom2d.box((0.0, 0.0, fw / 2.0), (width - 2 * fw, depth, fw)),
            ]
            frame = _local_to_world(parts, (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[win_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, win_mat.name,
                                                   _textured(library, win_mat), index, op_assumed, shift))
            pane = _local_to_world([geom2d.box((0.0, 0.0, height / 2.0),
                                               (width - 2 * fw, DEFAULTS["glass_thickness"], height - 2 * fw))],
                                   (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_glass", *pane, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[glass_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, glass_mat.name, False, index, op_assumed, shift))
    return created


def _textured(library, mat) -> bool:
    return library.textured(mat)


def door_leaf_material(door_style: dict) -> tuple[str, str | None]:
    """``(slug, asset id)`` of the door leaves: the veneer of a wood door slug
    (``vocabulary.veneer_for``: the floor planks were on the doors before
    Milestone 6; the veneer's grain runs along the box UV v, world Z on the
    leaf: vertical), else the style's door slug and asset (painted doors)."""
    slug = door_style.get("material") or "wood_oak_light"
    try:
        from wenart.style import vocabulary as V
        veneer = V.veneer_for(slug)
        if veneer is not None:
            return veneer, V.FURNITURE_MATERIALS[veneer].get("asset")
    except Exception:  # noqa: BLE001 - without the vocabulary the style slug stays
        pass
    return slug, door_style.get("asset")


def _opening_entry(opening, name, level_id, material, textured, index, op_assumed, shift) -> dict:
    return {
        "name": name or opening["id"], "wenart_id": opening["id"], "kind": opening["type"],
        "status": opening.get("status", "verified"), "level_id": level_id, "element_id": opening["id"],
        "evidence": opening.get("evidence", []), "material": material, "textured": textured,
        "pass_index": index, "assumed": dict(op_assumed), "wall_id": opening.get("wall_id"),
        "has_geometry": name is not None, "center_shift": round(shift, 4),
    }


def separator_entry(opening: dict, level_id: str) -> dict:
    """Manifest entry of a virtual separator (pure): kind ``opening``, no
    geometry, no wall, its ``line``; floors and ceilings meet there."""
    entry = _opening_entry(opening, None, level_id, None, False, None, {}, 0.0)
    entry.update({"virtual": True, "line": opening.get("line"),
                  "note": "virtual separator: no geometry; the room floors and ceilings meet at the line"})
    return entry


def floor_style(room: dict, style: dict) -> tuple[dict, bool]:
    """``(style slot, wet)`` of a room floor: the wet-room floor for bathroom /
    wc / kitchen, the style floor otherwise (dining and prayer rooms as living
    rooms, ``slot_room_type``)."""
    wet = slot_room_type(room.get("room_type")) in WET_ROOM_TYPES
    return (style.get("wet_floor") if wet else None) or style["floor"], wet


def floor_material(room: dict, style: dict, library):
    """``(material, wet)`` of a room floor: the style floor, the wet-room floor
    for bathroom / wc / kitchen, the dashed-red overlay for unverified rooms."""
    slot, wet = floor_style(room, style)
    mat = library.get(slot["material"], slot.get("asset"), slot.get("tint"),
                      unverified=room.get("status") == "unverified")
    return mat, wet


def _threshold(opening, wall, centre, angle, floor_z, has_below, rooms, style, library, collection,
               manifest_objects, warnings, op_assumed, shift):
    """Floor face of opening width x wall thickness under a door or plain
    opening, with the material of the adjacent room floor. Lifted 1 mm when a
    level lies below so it never shares a face with a stacked wall top."""
    from wenart.blender import common

    room = adjacent_room(centre, wall, rooms)
    if room is None:
        warnings.append(f"{opening['id']}: no room on either side; threshold gets the style floor material")
    mat, wet = floor_material(room or {}, style, library)
    z = floor_z + (DEFAULTS["threshold_lift"] if has_below else 0.0)
    verts, faces = geom2d.polygon_face(
        G.rotated_rectangle(centre, (float(opening["width"]), float(wall["thickness"])), angle), z, facing_up=True)
    ob = common.new_mesh_object(f"{opening['id']}_threshold", verts, faces, collection=collection,
                                wenart_id=opening["id"], kind="floor", status=opening.get("status", "verified"),
                                materials=[mat])
    manifest_objects.append({
        "name": ob.name, "wenart_id": opening["id"], "kind": "floor", "status": opening.get("status", "verified"),
        "level_id": opening["level_id"], "element_id": opening["id"], "evidence": opening.get("evidence", []),
        "material": mat.name, "textured": library.textured(mat), "pass_index": None, "assumed": dict(op_assumed),
        "wall_id": opening.get("wall_id"), "room_id": room["id"] if room else None,
        "room_type": room.get("room_type") if room else None, "wet": wet, "center_shift": round(shift, 4),
        "lifted": z - floor_z,
    })
    return ob


def _soffit(opening, wall, centre, angle, z, style, library, collection, manifest_objects, op_assumed, shift):
    """Downward face closing the wall top over a plain opening that was cut
    through the full wall height (a level with nothing above it)."""
    from wenart.blender import common

    ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
    mat = library.get(ceiling_style["material"], ceiling_style.get("asset"), ceiling_style.get("tint"))
    verts, faces = geom2d.polygon_face(
        G.rotated_rectangle(centre, (float(opening["width"]), float(wall["thickness"])), angle), z, facing_up=False)
    ob = common.new_mesh_object(f"{opening['id']}_soffit", verts, faces, collection=collection,
                                wenart_id=opening["id"], kind="ceiling", status=opening.get("status", "verified"),
                                materials=[mat])
    manifest_objects.append({
        "name": ob.name, "wenart_id": opening["id"], "kind": "ceiling", "status": opening.get("status", "verified"),
        "level_id": opening["level_id"], "element_id": opening["id"], "evidence": opening.get("evidence", []),
        "material": mat.name, "textured": library.textured(mat), "pass_index": None, "assumed": dict(op_assumed),
        "wall_id": opening.get("wall_id"), "room_type": None, "wet": False, "center_shift": round(shift, 4),
    })
    return ob


def _local_to_world(parts, origin, angle_deg):
    """Rotate box parts given in the opening's local frame (X along the wall,
    Y across, Z up from the opening bottom) into world space."""
    verts, faces = geom2d.merge(parts)
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    world = [(origin[0] + c * x - s * y, origin[1] + s * x + c * y, origin[2] + z) for x, y, z in verts]
    return world, faces


# --------------------------------------------------------------------------
# Floors and ceilings
# --------------------------------------------------------------------------

def ceiling_faces(polygon, voids, ceil_z: float) -> tuple[list, list, list[int]]:
    """``(verts, faces, cut)`` of a room ceiling (pure): one n-gon facing down
    as before, or, when stair openings (``voids``: lists of polygons, one
    list per stair) cross the room, the room minus the openings
    (``geom2d.polygon_faces``); ``cut`` = the indices of the stairs whose
    opening took area from the room."""
    verts, faces = geom2d.polygon_face(polygon, ceil_z, facing_up=False)
    area = G.polygon_area([v[:2] for v in verts])
    holes, cut = [], []
    for i, loops in enumerate(voids):
        rest_v, rest_f = geom2d.polygon_faces(polygon, list(loops), ceil_z, facing_up=False)
        if geom2d.faces_area(rest_v, rest_f) < area - 1e-6:
            holes.extend(loops)
            cut.append(i)
    if not cut:
        return verts, faces, []
    verts, faces = geom2d.polygon_faces(polygon, holes, ceil_z, facing_up=False)
    return verts, faces, cut


def build_floors_ceilings(building: dict, level: dict, collection, library, style: dict,
                          manifest_objects: list, warnings: list, stairs: list | None = None) -> list:
    """One floor face and one ceiling face per room, material per style and
    wet-room rule; unverified rooms get the dashed-red overlay on the floor.
    ``stairs`` (``plan_stairs``): their ceiling openings are cut out of the
    ceilings they cross (the shaft and cap come with ``build_stairs``)."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    ceil_z = floor_z + float(level["ceiling_height"])
    planned = [s for s in (stairs or []) if s.get("plan") is not None and s["plan"]["void"]]
    voids = [s["plan"]["void"] for s in planned]
    created = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        floor_mat, wet = floor_material(room, style, library)
        ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
        ceil_mat = library.get(ceiling_style["material"], ceiling_style.get("asset"), ceiling_style.get("tint"))
        if len(room["polygon"]) < 3:
            warnings.append(f"{room['id']}: polygon with fewer than 3 points, no floor")
            continue
        fv, ff = geom2d.polygon_face(room["polygon"], floor_z, facing_up=True)
        ob = common.new_mesh_object(f"{room['id']}_floor", fv, ff, collection=collection, wenart_id=room["id"],
                                    kind="floor", status=room.get("status", "verified"), materials=[floor_mat])
        created.append(ob)
        manifest_objects.append({
            "name": ob.name, "wenart_id": room["id"], "kind": "floor", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": floor_mat.name, "textured": _textured(library, floor_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        })
        cv, cf, cut = ceiling_faces(room["polygon"], voids, ceil_z)
        if not cf:
            warnings.append(f"{room['id']}: the stair opening covers the whole ceiling; no ceiling face")
            continue
        ob = common.new_mesh_object(f"{room['id']}_ceiling", cv, cf, collection=collection, wenart_id=room["id"],
                                    kind="ceiling", status=room.get("status", "verified"), materials=[ceil_mat])
        created.append(ob)
        entry = {
            "name": ob.name, "wenart_id": room["id"], "kind": "ceiling", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": ceil_mat.name, "textured": _textured(library, ceil_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        }
        if cut:
            ids = [planned[i]["piece"]["id"] for i in cut]
            entry["stair_void"] = ids
            entry["assumed"]["stair_void"] = f"ceiling opening of {', '.join(ids)} cut out (assumed)"
        manifest_objects.append(entry)
    return created


def build_skirting(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                   assumed: list) -> list:
    """A painted skirting board (``SKIRTING_H`` x ``SKIRTING_T``, the trim
    material) along the walls of every dry room of the level (not bathroom,
    WC, kitchen or balcony), interrupted at its doors, plain openings and
    windows that reach below the board (``skirting_spans``). One object per
    room (``skirting_<room id>``, kind wall, pass index 0, status assumed)
    and one ``assumed`` entry with the room as ``parent``."""
    from wenart.blender import common
    from wenart.blender.cameras import room_openings

    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    trim = style.get("trim") or {"material": "painted_wood_white"}
    mat = library.get(trim["material"], trim.get("asset"), trim.get("tint"))
    reason = "design detail of the room's documented walls (painted skirting board); not in the documents"
    created = []
    for room in building["rooms"]:
        if room["level_id"] != level["id"] or slot_room_type(room.get("room_type")) in NO_SKIRTING_TYPES:
            continue
        polygon = [tuple(p[:2]) for p in room["polygon"]]
        if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
            polygon = polygon[:-1]
        if len(polygon) < 3:
            continue
        gaps = skirting_gaps(room_openings(room, polygon, building), level, has_above)
        spans = skirting_spans(polygon, gaps)
        if not spans:
            continue
        verts, faces = skirting_boxes(polygon, spans, floor_z)
        name = f"skirting_{room['id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="wall",
                                    status="assumed", materials=[mat])
        ob.pass_index = 0
        created.append(ob)
        length = round(sum(s1 - s0 for _, s0, s1 in spans), 3)
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "wall", "status": "assumed", "level_id": level["id"],
            "element_id": room["id"], "parent": room["id"], "evidence": [], "material": mat.name,
            "textured": library.textured(mat), "pass_index": 0,
            "assumed": {"detail": "skirting", "size_m": [SKIRTING_H, SKIRTING_T], "length_m": length,
                        "runs": len(spans), "reason": reason},
        })
        assumed.append({"object": ob.name, "field": "skirting",
                        "value": f"{SKIRTING_H * 100:g} cm x {SKIRTING_T * 1000:g} mm, {length} m in {len(spans)} runs",
                        "reason": reason, "parent": room["id"], "kind": "skirting"})
    return created


# --------------------------------------------------------------------------
# Stairs (Milestone 7, docs/milestone7.md §6.4): fixed equipment, built with the shell
# --------------------------------------------------------------------------

STAIR_NOT_BUILT_REASON = "build false: kept in the building, not built"
STAIR_METHOD = "parametric (fixed equipment: the drawn flights and landing)"
STAIR_METHOD_GENERIC = "parametric (fixed equipment: one assumed flight, no drawn flights)"
# Above the level the shaft cap stays this far under the next floor (no coplanar faces with it).
STAIR_UPPER_FLOOR_GAP = 0.005


def stair_rise(building: dict, level: dict) -> tuple[float, float, str, str | None]:
    """``(rise, cap_height, riser_source, warning)`` of the stairs of a level
    (pure, metres above its floor): with nothing above, the ceiling height +
    the assumed ``STAIR_SLAB_M`` and the cap ``STAIR_SHAFT_CAP_M`` above the
    ceiling; with a level above, floor to floor and the cap just under its
    floor (whose own floor is not cut: a warning says so)."""
    floor_z = float(level["elevation"])
    ceiling = float(level["ceiling_height"])
    above = sorted(float(lv["elevation"]) for lv in building["levels"] if float(lv["elevation"]) > floor_z + 1e-6)
    if above:
        rise = above[0] - floor_z
        cap = min(ceiling + P.STAIR_SHAFT_CAP_M, rise - STAIR_UPPER_FLOOR_GAP)
        return rise, cap, "derived from the level elevations (floor to floor)", \
            "the floor of the level above is not cut; the stair opening is capped under it"
    if level.get("ceiling_height_source") == "assumed_default":
        source = P.STAIR_RISER_SOURCE
    else:
        source = "derived from the documented ceiling and assumed slab"
    return ceiling + P.STAIR_SLAB_M, ceiling + P.STAIR_SHAFT_CAP_M, source, None


def plan_stairs(building: dict, level: dict) -> list[dict]:
    """The stairs of a level (pure): ``[{"piece", "plan", "reason"}]`` with
    ``plan = parametric.stair_plan(...)`` (rise from ``stair_rise``, the
    level's walls for the handrail sides), or ``plan: None`` and the reason
    for a piece with ``build: false``. Site elements are never read."""
    walls = [w for w in building["walls"] if w["level_id"] == level["id"]]
    rise, cap, source, warning = stair_rise(building, level)
    out = []
    for piece in building.get("furniture") or []:
        if piece.get("level_id") != level["id"] or piece.get("type") not in P.SHELL_TYPES:
            continue
        if piece.get("build", True) is False:
            out.append({"piece": piece, "plan": None, "reason": STAIR_NOT_BUILT_REASON})
            continue
        plan = P.stair_plan(piece, rise, float(level["ceiling_height"]), cap, walls, source)
        if warning:
            plan["warnings"].append(warning)
        out.append({"piece": piece, "plan": plan, "reason": None})
    return out


def stair_mesh(plan: dict, floor_z: float) -> tuple[list, list, list[int], list[dict]]:
    """``(verts, faces, slots, parts)`` of a planned stair in world metres
    (pure): ``parametric.stair_parts`` lifted to the floor, one material slot
    per face (``parametric.STAIR_SLOTS``)."""
    parts = P.stair_parts(plan)
    verts, faces = geom2d.merge([(p["verts"], p["faces"]) for p in parts])
    return [(x, y, z + floor_z) for x, y, z in verts], faces, P.stair_face_slots(parts), parts


def stair_room(piece: dict, rooms: list[dict]) -> dict | None:
    """The room of a stair: its ``room_id``, else the room holding its footprint centre."""
    by_id = {r["id"]: r for r in rooms}
    if piece.get("room_id") in by_id:
        return by_id[piece["room_id"]]
    centre = piece["footprint"]["center"]
    return next((r for r in rooms if len(r["polygon"]) >= 3 and G.point_in_polygon(centre, r["polygon"])), None)


def build_stairs(building: dict, level: dict, collection, library, style: dict, pass_indices: dict,
                 manifest_objects: list, assumed: list, warnings: list, plans: list | None = None) -> dict:
    """Build the stairs of a level (``plan_stairs``): one ``furn_<id>``
    object (kind ``furniture``, the piece's pass index; treads in the room's
    floor finish, structure in the wall finish, steel rails) and one
    ``<id>_void`` object closing the ceiling opening (kind ``ceiling``,
    status ``assumed``, the ceiling finish). Every assumption of the plan
    becomes a scene-manifest ``assumed`` entry (parent = the piece). Returns
    ``{"pieces", "ids", "not_built"}``."""
    from wenart.blender import common

    floor_z = float(level["elevation"])
    plans = plan_stairs(building, level) if plans is None else plans
    rooms = [r for r in building["rooms"] if r["level_id"] == level["id"]]
    summary = {"pieces": 0, "ids": [], "not_built": []}
    walls_style = style.get("walls") or {"material": "plaster_white"}
    ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
    steel = library.get("steel_brushed")
    for item in plans:
        piece, plan = item["piece"], item["plan"]
        if plan is None:
            summary["not_built"].append({"id": piece["id"], "type": piece["type"], "reason": item["reason"]})
            continue
        status = piece.get("status", "verified")
        unverified = status == "unverified"
        room = stair_room(piece, rooms)
        slot, _wet = floor_style(room or {}, style)
        tread = library.get(slot["material"], slot.get("asset"), slot.get("tint"), unverified=unverified)
        structure = library.get(walls_style["material"], walls_style.get("asset"), unverified=unverified)
        verts, faces, slots, parts = stair_mesh(plan, floor_z)
        name = f"furn_{piece['id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=piece["id"],
                                    kind="furniture", status=status, materials=[tread, structure, steel],
                                    face_material_indices=slots)
        index = len(pass_indices) + 1
        pass_indices[piece["id"]] = index
        ob.pass_index = index
        ob["wenart_type"] = piece["type"]
        ob["wenart_room"] = piece.get("room_id") or (room["id"] if room else "")
        ob["wenart_source"] = piece.get("source") or "from_documents"
        ob["wenart_asset"] = "parametric"
        fp = piece["footprint"]
        rot = float(fp["rotation_deg"])
        x0, y0, z0, x1, y1, z1 = P.local_bbox_of_world_points(verts, fp["center"], rot)
        entry = {
            "name": name, "wenart_id": piece["id"], "kind": "furniture", "status": status, "level_id": level["id"],
            "element_id": piece["id"], "room_id": piece.get("room_id"), "type": piece["type"],
            "source": piece.get("source"), "evidence": piece.get("evidence", []), "pass_index": index,
            "assumed": {}, "decor": [],
            "center": [float(fp["center"][0]), float(fp["center"][1]), floor_z + plan["rise_m"] / 2.0],
            "size": [float(fp["size"][0]), float(fp["size"][1]), round(plan["rise_m"], 4)], "rotation_deg": rot,
            "front_deg": None if piece.get("front_deg") is None else float(piece["front_deg"]),
            "asset": piece.get("asset"), "fit_scale": [1.0, 1.0, 1.0],
            "method": STAIR_METHOD_GENERIC if plan["generic"] else STAIR_METHOD,
            "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)], "fallback_reason": None,
            "materials": [m.name for m in (tread, structure, steel)], "material": tread.name,
            "textured": any(library.textured(m) for m in (tread, structure)),
            "stair": stair_record(plan, parts),
        }
        shaft_name = f"{piece['id']}_void"
        for a in plan["assumed"]:
            owner = shaft_name if a["kind"] == "stair_void" else name
            if owner == name:
                entry["assumed"][a["field"]] = a["value"]
            assumed.append({"object": owner, "field": a["field"], "value": a["value"], "reason": a["reason"],
                            "parent": piece["id"], "kind": a["kind"]})
        for w in plan["warnings"]:
            warnings.append(f"{piece['id']}: stair {w}")
        manifest_objects.append(entry)
        summary["pieces"] += 1
        summary["ids"].append(piece["id"])
        sv, sf = P.void_shaft(plan)
        if sf:
            cap_mat = library.get(ceiling_style["material"], ceiling_style.get("asset"), ceiling_style.get("tint"))
            shaft = common.new_mesh_object(shaft_name, [(x, y, z + floor_z) for x, y, z in sv], sf,
                                           collection=collection, wenart_id=shaft_name, kind="ceiling",
                                           status="assumed", materials=[cap_mat])
            void = next((a for a in plan["assumed"] if a["kind"] == "stair_void"), {})
            manifest_objects.append({
                "name": shaft.name, "wenart_id": shaft_name, "kind": "ceiling", "status": "assumed",
                "level_id": level["id"], "element_id": piece["id"], "parent": piece["id"], "evidence": [],
                "material": cap_mat.name, "textured": library.textured(cap_mat), "pass_index": None,
                "room_type": None, "wet": False,
                "assumed": {"detail": "stair_void", "cap_z": round(floor_z + plan["cap_z"], 4),
                            "void": [[[round(x, 4), round(y, 4)] for x, y in loop] for loop in plan["void"]],
                            "reason": void.get("reason", "assumed ceiling opening")},
            })
    return summary


def stair_record(plan: dict, parts: list[dict]) -> dict:
    """The scene manifest's ``stair`` record of a built stair (pure)."""
    return {
        "risers": plan["risers"], "riser_m": round(plan["riser_m"], 4), "riser_source": plan["riser_source"],
        "rise_m": round(plan["rise_m"], 4), "direction": plan["direction"], "turn": plan["turn"],
        "generic": plan["generic"],
        "flights": [{"index": f["index"], "lines": f["lines"], "width": round(f["width"], 4),
                     "going": round(f["going"], 4), "rise_dir": [round(f["rise_dir"][0], 4), round(f["rise_dir"][1], 4)],
                     "base_z": round(f["base_z"], 4), "top_z": round(f["top_z"], 4),
                     "treads": sum(1 for p in parts if p["role"] == "step" and p.get("flight") == f["index"])}
                    for f in plan["flights"]],
        "landing": None if plan["landing"] is None else {"role": plan["landing"]["role"],
                                                         "z": round(plan["landing"]["z"], 4)},
        "rails": plan["rails"], "notes": plan["notes"],
    }


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

RAY_IGNORED_KINDS = ("door", "window")


def door_ray_checks(building: dict, level: dict, scene) -> list[dict]:
    """Cast a ray through every door / plain opening centre (on the wall
    centre line) across its wall at 1 m height and record what it hits.
    Door and window objects (frame, leaf, glass) are stepped over so the ray
    tests the wall itself: after the booleans ``hit`` must be False and
    ``hit_kind`` None; the stepped-over objects are listed in ``passed``."""
    import bpy
    from mathutils import Vector

    level_id = level["id"]
    floor_z = float(level["elevation"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    results = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id or opening["type"] not in ("door", "opening"):
            continue
        wall = walls.get(opening.get("wall_id"))
        if wall is None:
            continue  # a virtual separator (no wall, no geometry) or a missing wall (warned in build_openings)
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        cx, cy, _shift = opening_centre_on_wall(opening, wall)
        reach = float(wall["thickness"]) / 2.0 + 0.3
        origin = Vector((cx + nx * reach, cy + ny * reach, floor_z + 1.0))
        direction = Vector((-nx, -ny, 0.0))
        remaining = 2 * reach
        passed = []
        hit, ob = False, None
        for _ in range(16):  # at most a few door/window parts sit on the ray
            hit, loc, _normal, _index, ob, _matrix = scene.ray_cast(depsgraph, origin, direction, distance=remaining)
            if not hit or ob is None or ob.get("wenart_kind") not in RAY_IGNORED_KINDS:
                break
            passed.append(ob.name)
            # Continue just behind the door/window part that was hit.
            remaining -= (loc - origin).length + 0.002
            origin = loc + direction * 0.002
            if remaining <= 0:
                hit, ob = False, None
                break
        results.append({
            "opening_id": opening["id"], "hit": bool(hit),
            "hit_object": ob.name if hit and ob is not None else None,
            "hit_kind": ob.get("wenart_kind") if hit and ob is not None else None,
            "passed": passed,
        })
    return results
