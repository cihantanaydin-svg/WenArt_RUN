"""Deterministic checks and repairs for a furniture proposal (pure Python + shapely).

The model proposes, this module decides (CLAUDE.md: AI proposes, checks
against the source decide). Every piece of a proposal is checked against the
room polygon, the walls, the doors and the windows of the building JSON:

- ``inside_room``   the footprint lies inside the room polygon shrunk by 2 cm;
- ``no_overlap``    footprints do not overlap (touching is fine);
- ``clearance_ok``  0.6 m free in front of beds, sofas, desks and wardrobes
                    (inside the room, no other piece);
- ``doors_free``    the piece is not on the 0.6 m approach strip of a door, not
                    in the swing arc (a half disc with the door width as radius,
                    in the room the door opens into) and does not break the
                    0.9 m walkway: with the footprints removed from the room and
                    the free area eroded by 0.45 m, the approach point of every
                    door must stay in the same connected part as the approach
                    point of every other door, and that part must come within
                    1.2 m of every window (a window with a bed, sofa or table
                    under it counts as served). Only connections that exist in
                    the empty room are required, so a narrow room never fails
                    by itself. When the walkway breaks, the piece whose removal
                    restores it is blamed (fallback: the pieces on the straight
                    corridor between the two points);
- ``windows_free``  nothing taller than the sill (0.9 m when the sill is not in
                    the documents) within 0.3 m of a window wall segment; beds,
                    sofas and tables may stand under a window;
- ``wall_contact``  an ``against_wall`` piece touches the room boundary with its
                    back edge (three points of the edge within 5 cm).

Repairs run for at most ``MAX_ITERATIONS`` (40) steps per proposal, one step
per iteration on the last failing non-anchor piece (the room's anchor piece, bed
or sofa, is repaired only when nothing else fails and dropped last; the model lists the main piece first,
so later pieces give way): ``snap`` (against-wall pieces onto the nearest wall
with the back to it; free pieces back into the room), ``slide`` (along that
wall in 10 cm steps up to 2.5 m; free pieces on a 10 cm grid within 1 m, also
turned by 90 degrees), ``shrink`` (next smaller size option of
``schemas.SIZE_OPTIONS``, then slide again), for against-wall pieces
``relocate`` (the other walls, nearest first, at every size option from the
proposed size down) and finally ``drop``. A candidate position is accepted
when the piece passes its own checks there, invades no other piece's front
clearance and breaks no walkway that was intact without it. Every step is
logged with the position before and after and the checks that failed. Pieces
still failing at the cap are dropped and logged as such.

Sizes that are not one of the type's options are snapped to the nearest
option before the checks (logged as ``size_snapped``).

Anchor first: when the proposal names the room's anchor piece but the first
attempt dropped it (the other pieces, repaired earlier, took the floor it
needed), the anchor is placed alone, locked, and the rest of the proposal is
placed around it; a piece that still conflicts with the locked anchor gives
way (dropped, ``gives way to the anchor``). The retry is logged as an
``anchor_first`` step and ``PlacementResult.anchor_first`` is set.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points, unary_union

from wenart import geometry as G
from wenart.furniture import schemas

CHECKS: tuple[str, ...] = ("inside_room", "no_overlap", "clearance_ok", "doors_free", "windows_free", "wall_contact")

ROOM_SHRINK_M = 0.02
CLEARANCE_FRONT_M = 0.6
WALKWAY_M = 0.9
DOOR_APPROACH_M = 0.6
WINDOW_BAND_M = 0.3
WINDOW_REACH_M = 1.2
WALL_TOUCH_M = 0.05
SNAP_GAP_M = ROOM_SHRINK_M + 0.001   # back edge to wall face after a snap (see _snap_to_segment)
DEFAULT_SILL_M = 0.9
DEFAULT_WALL_THICKNESS_M = 0.15
MAX_ITERATIONS = 40
SLIDE_STEP_M = 0.1
SLIDE_MAX_M = 2.5
SHIFT_MAX_M = 1.0
AREA_EPS = 1e-4          # m²: intersections below this count as touching
POINT_TOL_M = 0.06       # a walkway point this close to the eroded free area is "in" it
ERODE_M = WALKWAY_M / 2 - 0.01


# --------------------------------------------------------------------------
# Pieces
# --------------------------------------------------------------------------

def _rect(center, size, rotation_deg: float, y0: float, y1: float) -> Polygon:
    """Local rectangle x in [-w/2, w/2], y in [y0, y1], rotated and moved to ``center``."""
    w = size[0] / 2.0
    local = [(-w, y0), (w, y0), (w, y1), (-w, y1)]
    pts = [G.rotate_point((center[0] + x, center[1] + y), rotation_deg, center) for x, y in local]
    return Polygon(pts)


@dataclass
class Piece:
    type: str
    center: tuple[float, float]
    rotation_deg: float
    size: tuple[float, float]
    against_wall: bool
    reason: str = ""
    index: int = 0
    proposed: dict = field(default_factory=dict)
    repairs: list[dict] = field(default_factory=list)
    stage: int = 0            # next repair step: 0 snap, 1 slide, 2 shrink, 3 drop
    locked: bool = False      # placed alone first (anchor first): never repaired or dropped
    proposal_index: int = 0   # position in the model's proposal (the "#n" of the reports)

    @classmethod
    def from_proposal(cls, item: dict, index: int, log: Optional[list] = None) -> "Piece":
        ftype = item["type"]
        size = (float(item["size"][0]), float(item["size"][1]))
        center = (round(float(item["center"][0]), 3), round(float(item["center"][1]), 3))
        rotation = G.normalise_angle(float(item.get("rotation_deg", 0.0)))
        if ftype in schemas.SIZE_OPTIONS and schemas.size_index(ftype, size) is None:
            options = schemas.SIZE_OPTIONS[ftype]
            swapped = (size[1], size[0])
            if schemas.size_index(ftype, swapped) is not None:
                # width and depth given the other way round: the same piece turned by 90 degrees
                nearest, turned = options[schemas.size_index(ftype, swapped)], True
                rotation = G.normalise_angle(rotation + 90.0)
            else:
                nearest, turned = min(options, key=lambda o: abs(o[0] - size[0]) + abs(o[1] - size[1])), False
            if log is not None:
                entry = {"iteration": 0, "piece": index, "type": ftype, "step": "size_snapped",
                         "before": {"size": list(size)}, "after": {"size": list(nearest)}, "failed": [], "ok": True}
                if turned:
                    entry["note"] = "width and depth swapped: size option taken with the rotation turned by 90 degrees"
                log.append(entry)
            size = nearest
        return cls(type=ftype, center=center, rotation_deg=rotation, size=size,
                   against_wall=bool(item.get("against_wall", False)), reason=str(item.get("reason", "")),
                   index=index, proposal_index=index,
                   proposed={"center": list(center), "rotation_deg": rotation, "size": list(size)})

    def polygon(self) -> Polygon:
        return _rect(self.center, self.size, self.rotation_deg, -self.size[1] / 2.0, self.size[1] / 2.0)

    def front_zone(self, depth: float = CLEARANCE_FRONT_M) -> Polygon:
        d = self.size[1] / 2.0
        return _rect(self.center, self.size, self.rotation_deg, -d - depth, -d)

    def back_edge(self) -> LineString:
        w, d = self.size[0] / 2.0, self.size[1] / 2.0
        a = G.rotate_point((self.center[0] - w, self.center[1] + d), self.rotation_deg, self.center)
        b = G.rotate_point((self.center[0] + w, self.center[1] + d), self.rotation_deg, self.center)
        return LineString([a, b])

    def height(self) -> float:
        return schemas.HEIGHTS.get(self.type, 1.0)

    def state(self) -> dict:
        return {"center": [round(self.center[0], 3), round(self.center[1], 3)],
                "rotation_deg": round(self.rotation_deg, 2), "size": [self.size[0], self.size[1]]}

    def to_dict(self) -> dict:
        return {"type": self.type, "center": list(self.state()["center"]), "rotation_deg": round(self.rotation_deg, 2),
                "size": [self.size[0], self.size[1]], "against_wall": self.against_wall, "reason": self.reason,
                "proposed": dict(self.proposed), "repairs": list(self.repairs)}


def piece_from_furniture(item: dict, index: int = 0) -> Piece:
    """A building furniture dict (``footprint`` with center/size/rotation_deg) as a placer piece."""
    fp = item["footprint"]
    return Piece(type=item["type"], center=(float(fp["center"][0]), float(fp["center"][1])),
                 rotation_deg=G.normalise_angle(float(fp["rotation_deg"])),
                 size=(float(fp["size"][0]), float(fp["size"][1])), against_wall=False, index=index)


# --------------------------------------------------------------------------
# Room context: polygon, boundary segments, door and window zones
# --------------------------------------------------------------------------

@dataclass
class DoorZone:
    id: str
    inner_point: tuple[float, float]       # door centre on the inner wall face
    approach_point: tuple[float, float]    # 0.46 m into the room: start of the 0.9 m walkway
    zone: Polygon                           # 0.6 m approach strip
    swing: Optional[Polygon]                # half disc when the door opens into this room
    width: float


@dataclass
class WindowZone:
    id: str
    inner_point: tuple[float, float]
    band: Polygon                            # 0.3 m strip inside the room along the window
    sill: float
    sill_assumed: bool
    width: float


@dataclass
class RoomContext:
    room: dict
    polygon: Polygon
    shrunk: Polygon
    segments: list[tuple[tuple[float, float], tuple[float, float]]]   # CCW boundary, inward normal = left
    doors: list[DoorZone]
    windows: list[WindowZone]
    baseline_pairs: list[tuple] = field(default_factory=list)          # walkway pairs that exist when empty

    @property
    def ring(self) -> LineString:
        return self.polygon.exterior

    def segment_normal(self, i: int) -> tuple[float, float]:
        a, b = self.segments[i]
        return G.unit_normal_left(a, b)

    def nearest_segment(self, point) -> int:
        best, best_d = 0, float("inf")
        for i, (a, b) in enumerate(self.segments):
            d = G.point_segment_distance(point, a, b)
            if d < best_d - 1e-9:
                best, best_d = i, d
        return best


def _unit(v) -> tuple[float, float]:
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n) if n > 1e-12 else (1.0, 0.0)


def _opening_frame(opening: dict, walls_by_id: dict, ctx_polygon: Polygon,
                   segments: list) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """(direction along the wall, inward unit normal, centre on the inner wall face)."""
    c = (float(opening["center"][0]), float(opening["center"][1]))
    wall = walls_by_id.get(opening.get("wall_id") or "")
    if wall is not None:
        d = _unit((wall["end"][0] - wall["start"][0], wall["end"][1] - wall["start"][1]))
        t = float(wall.get("thickness") or DEFAULT_WALL_THICKNESS_M)
    else:
        a, b = min(segments, key=lambda s: G.point_segment_distance(c, s[0], s[1]))
        d = _unit((b[0] - a[0], b[1] - a[1]))
        t = 2.0 * G.point_segment_distance(c, a, b)
    n = (-d[1], d[0])
    probe = (c[0] + n[0] * (t / 2 + 0.05), c[1] + n[1] * (t / 2 + 0.05))
    if not ctx_polygon.contains(Point(probe)):
        n = (-n[0], -n[1])
    inner = (c[0] + n[0] * t / 2, c[1] + n[1] * t / 2)
    return d, n, inner


def _strip(inner, d, n, half_width: float, depth: float) -> Polygon:
    p0 = (inner[0] - d[0] * half_width, inner[1] - d[1] * half_width)
    p1 = (inner[0] + d[0] * half_width, inner[1] + d[1] * half_width)
    p2 = (p1[0] + n[0] * depth, p1[1] + n[1] * depth)
    p3 = (p0[0] + n[0] * depth, p0[1] + n[1] * depth)
    return Polygon([p0, p1, p2, p3])


def room_openings(building: dict, room: dict) -> tuple[list[dict], list[dict]]:
    """Doors and windows of ``room``: openings of its level whose centre lies on its boundary."""
    polygon = Polygon(room["polygon"])
    ring = polygon.exterior
    walls_by_id = {w["id"]: w for w in building.get("walls", []) if w.get("level_id") == room["level_id"]}
    doors, windows = [], []
    for op in building.get("openings", []):
        if op.get("level_id") != room["level_id"] or op.get("type") not in ("door", "window", "opening"):
            continue
        wall = walls_by_id.get(op.get("wall_id") or "")
        t = float(wall["thickness"]) if wall else DEFAULT_WALL_THICKNESS_M
        if ring.distance(Point(op["center"])) <= t / 2 + 0.06:
            (windows if op["type"] == "window" else doors).append(op)
    return doors, windows


def room_context(building: dict, room: dict) -> RoomContext:
    polygon = orient(Polygon(room["polygon"]), 1.0)   # CCW: left normal points inward
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    ring = list(polygon.exterior.coords)
    segments = [(tuple(ring[i]), tuple(ring[i + 1])) for i in range(len(ring) - 1)
                if G.distance(ring[i], ring[i + 1]) > 1e-6]
    walls_by_id = {w["id"]: w for w in building.get("walls", []) if w.get("level_id") == room["level_id"]}
    door_items, window_items = room_openings(building, room)
    doors = []
    for op in door_items:
        d, n, inner = _opening_frame(op, walls_by_id, polygon, segments)
        width = float(op["width"])
        zone = _strip(inner, d, n, width / 2, DOOR_APPROACH_M).intersection(polygon)
        swing = None
        if op.get("swing_side") == room["id"]:
            half_plane = _strip(inner, d, n, width + 0.1, width + 0.1)
            swing = Point(inner).buffer(width, 32).intersection(half_plane).intersection(polygon)
        approach = (inner[0] + n[0] * (WALKWAY_M / 2 + 0.01), inner[1] + n[1] * (WALKWAY_M / 2 + 0.01))
        # A door flush with a corner: the point straight in front of it lies outside the
        # eroded free floor, which would silently drop its walkways. Start at the nearest
        # point of the empty room's walkable region instead.
        eroded = polygon.buffer(-ERODE_M, join_style="mitre")
        if not eroded.is_empty and eroded.distance(Point(approach)) > POINT_TOL_M:
            near = nearest_points(eroded, Point(approach))[0]
            approach = (round(near.x, 3), round(near.y, 3))
        doors.append(DoorZone(op["id"], inner, approach, zone, swing, width))
    windows = []
    for op in window_items:
        d, n, inner = _opening_frame(op, walls_by_id, polygon, segments)
        width = float(op["width"])
        band = _strip(inner, d, n, width / 2, WINDOW_BAND_M).intersection(polygon)
        sill = op.get("sill_height")
        windows.append(WindowZone(op["id"], inner, band, float(sill) if sill is not None else DEFAULT_SILL_M,
                                  sill is None, width))
    ctx = RoomContext(room=room, polygon=polygon, shrunk=polygon.buffer(-ROOM_SHRINK_M, join_style="mitre"),
                      segments=segments, doors=doors, windows=windows)
    ctx.baseline_pairs = [pair for pair in _all_pairs(ctx) if _pair_ok(pair, walkable_region([], ctx), [], ctx)]
    return ctx


# --------------------------------------------------------------------------
# Walkways
# --------------------------------------------------------------------------

def walkable_region(pieces: list[Piece], ctx: RoomContext):
    """The free floor eroded by 0.45 m: where the centre of a 0.9 m wide walkway can be."""
    free = ctx.polygon
    if pieces:
        free = free.difference(unary_union([p.polygon() for p in pieces]))
    return free.buffer(-ERODE_M, join_style="mitre")


def _components(region) -> list:
    if region.is_empty:
        return []
    return list(region.geoms) if hasattr(region, "geoms") else [region]


def _component_at(components: list, point) -> Optional[Polygon]:
    pt = Point(point)
    for comp in components:
        if comp.distance(pt) <= POINT_TOL_M:
            return comp
    return None


def _all_pairs(ctx: RoomContext) -> list[tuple]:
    pairs = []
    for i, door in enumerate(ctx.doors):
        for j, other in enumerate(ctx.doors):
            if j > i:
                pairs.append(("door", door.id, "door", other.id))
        for win in ctx.windows:
            pairs.append(("door", door.id, "window", win.id))
    return pairs


def _door(ctx: RoomContext, door_id: str) -> DoorZone:
    return next(d for d in ctx.doors if d.id == door_id)


def _window(ctx: RoomContext, win_id: str) -> WindowZone:
    return next(w for w in ctx.windows if w.id == win_id)


def _window_served(win: WindowZone, pieces: list[Piece]) -> bool:
    return any(p.type in schemas.UNDER_WINDOW_TYPES and p.polygon().intersection(win.band).area > AREA_EPS
               for p in pieces)


def _pair_ok(pair: tuple, region, pieces: list[Piece], ctx: RoomContext) -> bool:
    comps = _components(region)
    start = _component_at(comps, _door(ctx, pair[1]).approach_point)
    if start is None:
        return False
    if pair[2] == "door":
        return start is _component_at([start], _door(ctx, pair[3]).approach_point)
    win = _window(ctx, pair[3])
    if _window_served(win, pieces):
        return True
    return start.distance(Point(win.inner_point)) <= WINDOW_REACH_M


def walkway_failures(pieces: list[Piece], ctx: RoomContext) -> list[tuple]:
    """Baseline walkway pairs that the pieces break."""
    if not ctx.baseline_pairs:
        return []
    region = walkable_region(pieces, ctx)
    return [pair for pair in ctx.baseline_pairs if not _pair_ok(pair, region, pieces, ctx)]


def _pair_points(pair: tuple, ctx: RoomContext) -> tuple[tuple[float, float], tuple[float, float]]:
    a = _door(ctx, pair[1]).approach_point
    b = _door(ctx, pair[3]).approach_point if pair[2] == "door" else _window(ctx, pair[3]).inner_point
    return a, b


def walkway_blame(pieces: list[Piece], ctx: RoomContext) -> tuple[set[int], list[tuple]]:
    """(indices of the pieces that block a walkway, the broken pairs)."""
    failures = walkway_failures(pieces, ctx)
    if not failures:
        return set(), []
    blamed = set()
    for i in range(len(pieces)):
        others = [p for j, p in enumerate(pieces) if j != i]
        if not walkway_failures(others, ctx):
            blamed.add(i)
    if not blamed:
        for pair in failures:
            a, b = _pair_points(pair, ctx)
            corridor = LineString([a, b]).buffer(WALKWAY_M / 2)
            for i, p in enumerate(pieces):
                if p.polygon().intersection(corridor).area > AREA_EPS:
                    blamed.add(i)
    if not blamed and pieces:
        blamed.add(len(pieces) - 1)
    return blamed, failures


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_piece(piece: Piece, others: list[Piece], ctx: RoomContext, walkway_blamed: Optional[set] = None) -> dict:
    """The six checks of one piece against the room and the other pieces."""
    poly = piece.polygon()
    other_polys = [o.polygon() for o in others]
    # Containment (1 mm tolerance), not a leftover-area test: a rotated corner tip
    # outside the shrunk polygon has almost no area but is still outside.
    inside = ctx.shrunk.buffer(1e-3, join_style="mitre").contains(poly)
    no_overlap = all(poly.intersection(op).area < AREA_EPS for op in other_polys)
    clearance = True
    if piece.type in schemas.CLEARANCE_TYPES:
        zone = piece.front_zone()
        clearance = (zone.difference(ctx.polygon.buffer(0.01, join_style="mitre")).area < AREA_EPS
                     and all(zone.intersection(op).area < AREA_EPS for op in other_polys))
    doors = True
    for door in ctx.doors:
        if poly.intersection(door.zone).area > AREA_EPS:
            doors = False
        if door.swing is not None and poly.intersection(door.swing).area > AREA_EPS:
            doors = False
    if walkway_blamed and piece.index in walkway_blamed:
        doors = False
    windows = True
    if piece.type not in schemas.UNDER_WINDOW_TYPES:
        for win in ctx.windows:
            if piece.height() > win.sill + 1e-9 and poly.intersection(win.band).area > AREA_EPS:
                windows = False
    wall_contact = True
    if piece.against_wall:
        edge = piece.back_edge()
        pts = [edge.interpolate(t, normalized=True) for t in (0.0, 0.5, 1.0)]
        wall_contact = all(ctx.ring.distance(pt) <= WALL_TOUCH_M for pt in pts)
    return {"inside_room": inside, "no_overlap": no_overlap, "clearance_ok": clearance,
            "doors_free": doors, "windows_free": windows, "wall_contact": wall_contact}


def check_all(pieces: list[Piece], ctx: RoomContext) -> list[dict]:
    for i, p in enumerate(pieces):
        p.index = i
    blamed, _failures = walkway_blame(pieces, ctx)
    return [check_piece(p, [o for o in pieces if o is not p], ctx, blamed) for p in pieces]


def failed_checks(checks: dict) -> list[str]:
    return [name for name in CHECKS if not checks.get(name, True)]


# --------------------------------------------------------------------------
# Repairs
# --------------------------------------------------------------------------

def _rotation_for_normal(n_in) -> float:
    """Rotation whose back edge (local +Y) faces the wall with inward normal ``n_in``."""
    return G.normalise_angle(math.degrees(math.atan2(-n_in[1], -n_in[0])) - 90.0)


def _snap_to_segment(piece: Piece, ctx: RoomContext, seg_index: int, offset: float = 0.0) -> tuple:
    """(center, rotation) with the back on boundary segment ``seg_index``, slid by ``offset`` along it."""
    a, b = ctx.segments[seg_index]
    n = ctx.segment_normal(seg_index)
    d = _unit((b[0] - a[0], b[1] - a[1]))
    length = G.distance(a, b)
    t = (piece.center[0] - a[0]) * d[0] + (piece.center[1] - a[1]) * d[1] + offset
    half_w = piece.size[0] / 2.0 + SNAP_GAP_M
    if length >= 2 * half_w:
        t = min(max(t, half_w), length - half_w)
    else:
        t = length / 2.0
    foot = (a[0] + d[0] * t, a[1] + d[1] * t)
    # The back edge sits SNAP_GAP_M (2.1 cm) off the wall face: inside the room polygon
    # shrunk by 2 cm (inside_room) and within the 5 cm wall touch (wall_contact).
    depth = piece.size[1] / 2.0 + SNAP_GAP_M
    center = (round(foot[0] + n[0] * depth, 3), round(foot[1] + n[1] * depth, 3))
    return center, _rotation_for_normal(n)


def _snap_inside(piece: Piece, ctx: RoomContext) -> Optional[tuple[float, float]]:
    """Move a free piece towards the room centroid until it lies inside (None when impossible)."""
    cx, cy = ctx.polygon.centroid.x, ctx.polygon.centroid.y
    v = (cx - piece.center[0], cy - piece.center[1])
    if math.hypot(*v) < 1e-9:
        return None
    u = _unit(v)
    for k in range(1, 121):
        c = (round(piece.center[0] + u[0] * 0.05 * k, 3), round(piece.center[1] + u[1] * 0.05 * k, 3))
        test = Piece(piece.type, c, piece.rotation_deg, piece.size, piece.against_wall)
        if test.polygon().difference(ctx.shrunk).area < AREA_EPS:
            return c
    return None


def _candidate_ok(piece: Piece, pieces: list[Piece], ctx: RoomContext, base_failures: set) -> bool:
    """The piece passes its own checks at its current position, invades no other piece's
    front clearance and breaks no walkway that was intact without it."""
    others = [o for o in pieces if o is not piece]
    if failed_checks(check_piece(piece, others, ctx)):
        return False
    poly = piece.polygon()
    for o in others:
        if o.type in schemas.CLEARANCE_TYPES and poly.intersection(o.front_zone()).area > AREA_EPS:
            return False
    return set(walkway_failures(pieces, ctx)) <= base_failures


def _try_candidates(piece: Piece, pieces: list[Piece], ctx: RoomContext, candidates: list[tuple]) -> Optional[tuple]:
    """First (center, rotation[, size]) of ``candidates`` at which the piece passes (see _candidate_ok)."""
    original = (piece.center, piece.rotation_deg, piece.size)
    base_failures = set(walkway_failures([o for o in pieces if o is not piece], ctx))
    seen = set()
    for cand in candidates:
        center, rotation = cand[0], cand[1]
        size = cand[2] if len(cand) > 2 else original[2]
        key = (round(center[0], 3), round(center[1], 3), round(rotation, 1), size)
        if key in seen or key == (round(original[0][0], 3), round(original[0][1], 3), round(original[1], 1), original[2]):
            continue
        seen.add(key)
        piece.center, piece.rotation_deg, piece.size = center, rotation, size
        if _candidate_ok(piece, pieces, ctx, base_failures):
            return center, rotation, size
    piece.center, piece.rotation_deg, piece.size = original
    return None


def _contact_segment(piece: Piece, ctx: RoomContext) -> int:
    return ctx.nearest_segment(piece.back_edge().interpolate(0.5, normalized=True).coords[0])


def _slide_offsets() -> list[float]:
    steps = int(round(SLIDE_MAX_M / SLIDE_STEP_M))
    out = []
    for k in range(1, steps + 1):
        out += [k * SLIDE_STEP_M, -k * SLIDE_STEP_M]
    return out


def _slide_candidates(piece: Piece, ctx: RoomContext) -> list[tuple]:
    """Along the wall the piece touches (against_wall) or on a 10 cm grid within 1 m (free)."""
    if piece.against_wall:
        seg = _contact_segment(piece, ctx)
        return [_snap_to_segment(piece, ctx, seg, off) for off in [0.0] + _slide_offsets()]
    offsets = []
    steps = int(round(SHIFT_MAX_M / SLIDE_STEP_M))
    for ix in range(-steps, steps + 1):
        for iy in range(-steps, steps + 1):
            if ix == 0 and iy == 0:
                continue
            dx, dy = ix * SLIDE_STEP_M, iy * SLIDE_STEP_M
            if math.hypot(dx, dy) <= SHIFT_MAX_M + 1e-9:
                offsets.append((dx, dy))
    offsets.sort(key=lambda o: (math.hypot(*o), o))
    out = []
    for rot in (piece.rotation_deg, G.normalise_angle(piece.rotation_deg + 90.0)):
        for dx, dy in offsets:
            out.append(((round(piece.center[0] + dx, 3), round(piece.center[1] + dy, 3)), rot))
    return out


def _relocate_candidates(piece: Piece, ctx: RoomContext) -> list[tuple]:
    """Other walls, nearest first, at every size option from the proposed size down, slid along each."""
    seg = _contact_segment(piece, ctx)
    order = sorted((i for i in range(len(ctx.segments)) if i != seg),
                   key=lambda i: G.point_segment_distance(piece.center, *ctx.segments[i]))
    proposed = tuple(piece.proposed.get("size", piece.size))
    options = [s for s in schemas.SIZE_OPTIONS.get(piece.type, [proposed]) if s[0] * s[1] <= proposed[0] * proposed[1] + 1e-9]
    sizes = sorted(set(options or [proposed]), key=lambda s: -s[0] * s[1])
    out = []
    for i in order:
        for size in sizes:
            probe = Piece(piece.type, piece.center, piece.rotation_deg, size, True)
            for off in [0.0] + _slide_offsets():
                center, rotation = _snap_to_segment(probe, ctx, i, off)
                out.append((center, rotation, size))
    return out


@dataclass
class PlacementResult:
    pieces: list[Piece]
    checks: list[dict]
    dropped: list[dict]
    log: list[dict]
    iterations: int
    anchor_first: bool = False

    @property
    def all_ok(self) -> bool:
        return all(not failed_checks(c) for c in self.checks)

    def to_dict(self) -> dict:
        return {"pieces": [dict(p.to_dict(), checks=c) for p, c in zip(self.pieces, self.checks)],
                "dropped": list(self.dropped), "log": list(self.log), "iterations": self.iterations,
                "anchor_first": self.anchor_first}


def _log(log: list, iteration: int, piece: Piece, step: str, before: dict, failed: list[str], ok: bool,
         note: str = "") -> dict:
    entry = {"iteration": iteration, "piece": piece.proposal_index, "type": piece.type, "step": step,
             "before": before, "after": piece.state(), "failed": failed, "ok": ok}
    if note:
        entry["note"] = note
    log.append(entry)
    piece.repairs.append({k: v for k, v in entry.items() if k != "piece"})
    return entry


def place(proposal: list[dict], ctx: RoomContext, max_iterations: int = MAX_ITERATIONS) -> PlacementResult:
    """Check and repair a proposal (list of schema-shaped piece dicts) in ``ctx``.
    If the proposal names the room's anchor piece and the first attempt dropped
    it, the anchor is placed alone and locked and the rest is placed around it."""
    result = _place(proposal, ctx, max_iterations)
    anchors = set(schemas.ANCHOR_TYPES.get(ctx.room.get("room_type", ""), ()))
    first = next((i for i, item in enumerate(proposal) if item["type"] in anchors), None)
    if first is None or any(p.type in anchors for p in result.pieces):
        return result
    alone = _place([proposal[first]], ctx, max_iterations)
    if not alone.pieces:
        return result                                          # the anchor does not fit the room on its own
    anchor = alone.pieces[0]
    anchor.locked = True
    anchor.proposal_index = first
    for entry in alone.log:
        entry["piece"] = first
    rest = [item for i, item in enumerate(proposal) if i != first]
    retry = _place(rest, ctx, max_iterations, locked=[anchor],
                   proposal_indices=[i for i in range(len(proposal)) if i != first])
    if not any(p.type in anchors for p in retry.pieces):      # cannot happen (locked), kept as a guard
        return result
    marker = {"iteration": alone.iterations, "piece": first, "type": anchor.type, "step": "anchor_first",
              "before": dict(anchor.proposed), "after": anchor.state(), "failed": [], "ok": True,
              "note": "the anchor was dropped in the first attempt; placed alone first, the other pieces give way"}
    anchor.repairs.append({k: v for k, v in marker.items() if k != "piece"})
    retry.log = alone.log + [marker] + retry.log
    retry.iterations += alone.iterations
    retry.anchor_first = True
    return retry


def _place(proposal: list[dict], ctx: RoomContext, max_iterations: int = MAX_ITERATIONS,
           locked: Optional[list[Piece]] = None, proposal_indices: Optional[list[int]] = None) -> PlacementResult:
    """One placement attempt; ``locked`` pieces are already placed and never repaired or
    dropped; ``proposal_indices`` are the items' positions in the original proposal."""
    log: list[dict] = []
    indices = proposal_indices or list(range(len(proposal)))
    pieces = list(locked or []) + [Piece.from_proposal(item, i, log) for i, item in zip(indices, proposal)]
    dropped: list[dict] = []
    iterations = 0

    def drop(piece: Piece, failed: list[str], reason: str, count: bool) -> None:
        nonlocal iterations
        if count:
            iterations += 1
        before = piece.state()
        pieces.remove(piece)
        entry = _log(log, iterations, piece, "drop", before, failed, True, reason)
        dropped.append({"type": piece.type, "proposed": piece.proposed, "last": before, "failed": failed,
                        "reason": reason, "repairs": list(piece.repairs), "log_entry": entry})

    def own_ok(piece: Piece) -> bool:
        return not failed_checks(check_all(pieces, ctx)[piece.index])

    anchors = set(schemas.ANCHOR_TYPES.get(ctx.room.get("room_type", ""), ()))
    budget = max_iterations
    anchor_budget_given = False

    def is_anchor(piece: Piece) -> bool:
        return piece.type in anchors

    def give_way(failing: list[int], checks: list[dict], reason: str) -> bool:
        """Only locked pieces fail: drop the last free piece that sits on a failing
        locked piece or its front clearance (else the last free piece)."""
        free = [p for p in pieces if not p.locked]
        if not free:
            return False
        blockers = [pieces[i] for i in failing if pieces[i].locked]
        zones = unary_union([p.polygon() for p in blockers]
                            + [p.front_zone() for p in blockers if p.type in schemas.CLEARANCE_TYPES])
        culprit = next((p for p in reversed(free) if p.polygon().intersection(zones).area > AREA_EPS), free[-1])
        drop(culprit, failed_checks(checks[culprit.index]), reason, False)
        return True

    while True:
        checks = check_all(pieces, ctx)
        failing = [i for i, c in enumerate(checks) if failed_checks(c)]
        if not failing:
            break
        repairable = [i for i in failing if not pieces[i].locked]
        if not repairable:
            if not give_way(failing, checks, "gives way to the anchor"):
                break
            continue
        if iterations >= budget:
            # The room's anchor piece (bed, sofa, ...) goes last: at the cap the other
            # failing pieces are dropped, and the anchor gets one fresh repair budget of
            # its own before it is dropped too.
            for i in reversed(repairable):
                if not is_anchor(pieces[i]):
                    drop(pieces[i], failed_checks(checks[i]), "iteration cap", False)
            still = [i for i, c in enumerate(check_all(pieces, ctx)) if failed_checks(c) and not pieces[i].locked]
            if still and not anchor_budget_given:
                anchor_budget_given = True
                budget = iterations + max_iterations
                continue
            checks = check_all(pieces, ctx)
            for i in reversed([i for i, c in enumerate(checks) if failed_checks(c) and not pieces[i].locked]):
                drop(pieces[i], failed_checks(checks[i]), "iteration cap (anchor still failing alone)", False)
            while True:                                        # a locked anchor never goes: the rest does
                checks = check_all(pieces, ctx)
                failing = [i for i, c in enumerate(checks) if failed_checks(c)]
                if not failing or not give_way(failing, checks, "gives way to the anchor (iteration cap)"):
                    break
            break
        # Repair the last failing non-anchor piece; the anchor itself only when nothing else fails.
        non_anchor = [i for i in repairable if not is_anchor(pieces[i])]
        piece = pieces[(non_anchor or repairable)[-1]]
        failed = failed_checks(checks[piece.index])
        before = piece.state()
        if piece.stage == 0:                                   # snap
            piece.stage = 1
            target = None
            if piece.against_wall:
                target = _snap_to_segment(piece, ctx, _contact_segment(piece, ctx))
            elif "inside_room" in failed:
                c = _snap_inside(piece, ctx)
                target = (c, piece.rotation_deg) if c else None
            if target is None or (target[0] == piece.center and abs(target[1] - piece.rotation_deg) < 1e-6):
                continue                                       # nothing to snap: not an attempt
            iterations += 1
            piece.center, piece.rotation_deg = target
            _log(log, iterations, piece, "snap", before, failed, own_ok(piece))
        elif piece.stage == 1:                                 # slide
            piece.stage = 2
            iterations += 1
            found = _try_candidates(piece, pieces, ctx, _slide_candidates(piece, ctx))
            _log(log, iterations, piece, "slide", before, failed, found is not None,
                 "" if found else "no free position on this wall" if piece.against_wall else "no free position within 1 m")
        elif piece.stage == 2:                                 # shrink, then slide again
            smaller = schemas.smaller_size(piece.type, piece.size)
            if smaller is None:
                piece.stage = 3 if piece.against_wall else 4
                continue
            iterations += 1
            piece.size = smaller
            if piece.against_wall:
                piece.center, piece.rotation_deg = _snap_to_segment(piece, ctx, _contact_segment(piece, ctx))
            piece.stage = 1
            _log(log, iterations, piece, "shrink", before, failed, own_ok(piece))
        elif piece.stage == 3:                                 # relocate to another wall
            piece.stage = 4
            iterations += 1
            found = _try_candidates(piece, pieces, ctx, _relocate_candidates(piece, ctx))
            _log(log, iterations, piece, "relocate", before, failed, found is not None,
                 "" if found else "no free wall")
        else:
            drop(piece, failed, "no repair left", True)
    checks = check_all(pieces, ctx)
    return PlacementResult(pieces=pieces, checks=checks, dropped=dropped, log=log, iterations=iterations)
