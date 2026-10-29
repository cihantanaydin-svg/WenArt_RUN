"""Fixtures you can use: fronts that open, backs on their walls, a solid wall over every basin (29 Oct 2026). Pure
Python, no shapely (``fixture_seat``'s geometry): the reading, the score (``plausibility`` F6), the edit validator
(``edit_ops``), the architect (F4, H2), the model review (M19, M22) and Argus (U10, U16, U20) share it, and the model
review runs where Blender's Python has no shapely.

The user's review of real06 run 20261028-154514-full:

- UL92 "This washing machine would not open": the drawn washer f_L1_019 stands in the corner of the first-floor bathroom
  below the toilet f_L1_022. The reading gave it no front (in its corner it ranked the two free sides by how far the
  room reaches; the toilet 0.11 m in front of one of them was not looked at, so neither side won); the builder faced it
  to its footprint's -Y, into the wall (F4); the agent turned it 90 degrees "into the room" to clear F4, and its door
  then faced the toilet 0.11 m away. Every check passed: F4 knows only walls, F6 only seats, G10 skips the washer, G13 only
  storage, and the rule for turning drawn fixed equipment only asked "back on a wall, front not into a wall".
- UL95 "this sink not making sense there": the drawn basins f_L0_026 / f_L1_023 stand right under a window (a bare gap
  in the outer wall the reading read as a window at the floor's 0.90 m sill) beside the bath: no mirror over them and
  the tap meets the sill.
- UL96 "There is a gap between wall and water faucet not looking good": the kitchen sink unit f_L0_020 stood 0.08 m off
  the wall under the window, its back parallel to it: a drawing gap the build kept.

Rules (general, every project; CLAUDE.md furniture rules):

1. ``access_problem``: a piece with a front door or drawers (``ACCESS_M``: a washing machine or dryer, a dishwasher, an
   oven or cooker, a fridge, a nightstand; ``STORAGE_OPEN_M``: door-fronted storage, whose 0.80 m walking room is G13's)
   keeps its width x its access depth free in front of it: free of the room's walls and of every other piece except the
   light movable ones (``LIGHT_TYPES``) and a piece it is built into. Under ``open_m`` its door or drawers cannot open
   (critical), under ``use_m`` it cannot be loaded or reached (major). Measured with rays from its front edge.
2. ``free_front``: a drawn piece whose door cannot open (a wall or a neighbour within its opening depth) was read with
   the wrong front (CLAUDE.md: "a front that faces the wall", a clear reading error; a tight front that opens stays as
   drawn and is the score's F6 major): it turns in place to the free side with its back on a wall (a
   near-square piece any way round, else half a turn); else it moves at most ``MOVE_MAX_M`` (0.5 m) to a place of its
   room with its back on a wall and its front free. Never a piece of a kitchen run (the run's front is its aisle, G8).
   The caller keeps ``drawn_front_deg`` / ``drawn_footprint`` and labels it ``adjusted_by_ai`` with the reason.
3. ``back_gap`` / ``snap_back``: a piece whose back belongs on a wall (``BACK_TYPES``) and stands parallel to a wall
   segment past the score's own tolerance (F3's 0.05 m: ``BACK_GAP_MIN_M``, 0.055 m) and up to ``BACK_GAP_MAX_M``
   (0.15 m) off it (a drawing gap: a plaster line, an outline drawn off the wall line) goes back onto the wall
   (``SNAP_GAP_M`` off its face, as every snap), with the pieces built into it; never into another piece, never out of
   the room, never into a door swing. A washer, a dryer and a fridge keep theirs (``SERVICE_GAP_TYPES``: hoses and
   ventilation behind them).
4. ``basin_window`` / ``clear_basin``: a basin needs a solid wall over it for its mirror and its tap; a window over it is
   fine only with its sill at ``BASIN_SILL_M`` (1.25 m) or more. Under a lower window a drawn basin moves at most 0.5 m,
   along its wall or onto another wall of its room, to a free stretch (its front kept free); when no such move exists
   the architect asks (H2: the window's sill raised to ``BASIN_SILL_M`` when the documents do not give it, else kept
   with its mirror beside it, ``decor_ai.basin_mirror``).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

from wenart import geometry as G
from wenart.furniture import fixture_seat as FS

Point = tuple[float, float]

# type -> (open_m, use_m): the free depth in front of the piece its door or drawers need to open at all, and to be used
# (loaded, reached, stood at). Typical real products (assumed values from manufacturers' installation guides):
ACCESS_M: dict[str, tuple[float, float]] = {
    "washing_machine": (0.45, 0.60),   # a front loader's porthole door is 0.45-0.50 m across and swings out by about
    "dryer": (0.45, 0.60),             # its width; loading needs about 0.6 m (a basket in front)
    "washer_dryer": (0.45, 0.60),
    "dishwasher": (0.55, 0.70),        # its door drops flat: a 60 cm machine's door reaches 0.55-0.60 m out, the racks
                                       # roll out over it
    "oven": (0.45, 0.60),              # a drop-down oven door reaches about 0.45 m out
    "stove": (0.45, 0.60),             # a cooker: its oven door
    "fridge": (0.50, 0.70),            # a single door 0.55-0.70 m wide swings through 90 degrees in front of it
    "nightstand": (0.30, 0.40),        # a drawer 0.30-0.35 m deep pulls out
}
FRIDGE_ONE_DOOR_M = 0.75               # a fridge wider than this has two doors (each half its width)
# Door-fronted storage: the depth its doors or drawers need to open at all (G13 asks 0.80 m of walking room in front)
STORAGE_OPEN_M: dict[str, float] = {"wardrobe": 0.50, "tall_cabinet": 0.45, "display_cabinet": 0.40, "dresser": 0.45,
                                    "sideboard": 0.40, "shoe_cabinet": 0.35, "tv_unit": 0.35}
DOOR_FRONTED: tuple[str, ...] = tuple(ACCESS_M) + tuple(STORAGE_OPEN_M)
# Pieces a person moves aside by hand: never in the way of a door
LIGHT_TYPES: tuple[str, ...] = ("chair", "office_chair", "bar_stool", "stool", "ottoman", "pouf", "floor_lamp",
                                "potted_plant", "plant", "rug", "cushion", "laundry_basket", "unknown")
RUN_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
RUN_TOUCH_M = 0.05                     # a piece this close to a counter run stands in the run
SQUARE_TOL_M = 0.10                    # a footprint whose sides differ by at most this turns any way round
MOVE_MAX_M = FS.MOVE_MAX_M             # CLAUDE.md: a drawn fixed piece moves at most 0.5 m
STEP_M = FS.STEP_M
RAYS = 5
EDGE_INSET_M = 0.05
RAY_M = 3.0
# = schemas.BACK_WALL_M, plausibility.BACK_SHARE, schemas.BACK_PARALLEL_DEG, schemas.FRONT_WALL_MIN_M (pinned in tests)
BACK_WALL_M = 0.05
BACK_SHARE = 0.6
PARALLEL_DEG = 5.0
FRONT_WALL_MIN_M = 0.3
SNAP_GAP_M = 0.021                     # = placer.SNAP_GAP_M: a back snapped onto a wall stands this far off its face
# Rule 3: the types whose back belongs on a wall (``schemas.ORIENTATION_RULES`` back "wall", pinned in the tests)
BACK_TYPES: tuple[str, ...] = ("bed_double", "bed_single", "bunk_bed", "crib", "desk", "wardrobe", "tv_unit",
                               "bookshelf", "dresser", "sideboard", "console_table", "shoe_cabinet", "display_cabinet",
                               "nightstand", "kitchen_counter", "sink_kitchen", "stove", "fridge", "tall_cabinet",
                               "washing_machine", "washbasin", "toilet", "bathtub", "shower")
# A back up to the score's own tolerance (F3, BACK_WALL_M: 5 cm) stands on its wall: drawings put fixtures and furniture
# that close (the synthetic plans' toilets and counters, a TV unit's cable gap); past it, up to BACK_GAP_MAX_M, the gap
# is a drawing gap the eye sees (real06's sink unit 0.08 m off its wall, behind the tap)
BACK_GAP_MIN_M = BACK_WALL_M + 0.005
BACK_GAP_MAX_M = 0.15                  # a back farther than this is no drawing gap: the piece stands off the wall
# Appliances that stand off their wall on purpose (installation guides: a washer's or dryer's hoses behind it, a
# fridge's ventilation, 0.05-0.10 m): their drawn back gap is kept (the synthetic plans draw the washer 0.10 m off)
SERVICE_GAP_TYPES: tuple[str, ...] = ("washing_machine", "dryer", "washer_dryer", "fridge")
BACK_GAP_EVEN_M = 0.03                 # the back's samples differ by at most this: it is parallel to the wall
# Rule 4: a basin's wall
BASINS: tuple[str, ...] = ("washbasin", "vanity", "bathroom_vanity")
BASIN_SILL_M = 1.25                    # a window over a basin is fine with its sill this high: over the tap, a mirror's
                                       # height beside it and a standing person's eyes
BASIN_UNDER_SHARE = 0.5                # a window over this share of the basin's width is over it
WINDOW_BEHIND_M = 0.15                 # a window whose wall line stands within half the wall + this behind the basin
FIXTURE_FRONT_M = 0.53                 # = groups.yaml fixture_front: a moved basin keeps this much free in front
DEFAULT_SILL_M = 0.90


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------

def frame(fp: dict, front_deg: Optional[float]) -> tuple[float, tuple[float, float]]:
    """``(rotation, (width along the front, depth))`` of a footprint in the frame of its front (``placer.front_frame``:
    the same rectangle turned by quarter turns until its local -Y faces ``front_deg``); without a front its own."""
    rot = G.normalise_angle(float(fp.get("rotation_deg") or 0.0))
    size = (float(fp["size"][0]), float(fp["size"][1]))
    if front_deg is None:
        return rot, size
    k = int(round(G.normalise_angle(float(front_deg) - 270.0 - rot) / 90.0)) % 4
    return G.normalise_angle(rot + 90.0 * k), ((size[1], size[0]) if k % 2 else size)


def front_of(f: dict) -> float:
    """The front a piece is built with: its ``front_deg``, else its footprint's local -Y (the builder's)."""
    if f.get("front_deg") is not None:
        return G.normalise_angle(float(f["front_deg"]))
    return G.front_direction_deg(float((f.get("footprint") or {}).get("rotation_deg") or 0.0))


def _dir(deg: float) -> Point:
    a = math.radians(deg)
    return math.cos(a), math.sin(a)


def _world(center, rot: float, x: float, y: float) -> Point:
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    return float(center[0]) + x * c - y * s, float(center[1]) + x * s + y * c


def edge_points(center, rot: float, size, side: str = "front", n: int = RAYS, inset: float = EDGE_INSET_M
                ) -> list[Point]:
    """``n`` points along the front (local -Y) or back (+Y) edge, ``inset`` from its ends."""
    w, d = float(size[0]) / 2.0, float(size[1]) / 2.0
    y = -d if side == "front" else d
    span = max(0.0, w - inset)
    return [_world(center, rot, -span + 2.0 * span * (k / (n - 1) if n > 1 else 0.5), y) for k in range(n)]


def segments(poly) -> list[tuple[Point, Point]]:
    pts = [(float(p[0]), float(p[1])) for p in poly]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))] if len(pts) >= 2 else []


def _ray_hit(p: Point, u: Point, a: Point, b: Point) -> Optional[float]:
    """The distance along the ray ``p + t u`` (t > 0) to segment ``a b``, None when it misses."""
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = u[0] * ey - u[1] * ex
    if abs(den) < 1e-12:
        return None
    qx, qy = a[0] - p[0], a[1] - p[1]
    t = (qx * ey - qy * ex) / den
    s = (qx * u[1] - qy * u[0]) / den
    if t <= 1e-9 or s < -1e-9 or s > 1.0 + 1e-9:
        return None
    return t


def ray_clear(points: Sequence[Point], u: Point, keyed: Sequence[tuple], max_m: float = RAY_M
              ) -> tuple[float, dict]:
    """``(free, hits)``: the shortest free distance from ``points`` along ``u`` (each moved 1 mm out first) to the keyed
    segments ``(key, a, b)``, capped at ``max_m``, and the nearest hit per key."""
    best = max_m
    hits: dict = {}
    for p in points:
        start = (p[0] + u[0] * 1e-3, p[1] + u[1] * 1e-3)
        for key, a, b in keyed:
            t = _ray_hit(start, u, a, b)
            if t is None or t >= max_m:
                continue
            t += 1e-3
            best = min(best, t)
            if t < hits.get(key, math.inf):
                hits[key] = t
    return round(best, 3), {k: round(v, 3) for k, v in hits.items()}


def poly_distance(a, b) -> float:
    """The distance between two convex polygons (0 when they touch or cut)."""
    if FS.cut_depth(a, b) > 0.0 or any(G.point_in_polygon(p, b) for p in a) or any(G.point_in_polygon(p, a) for p in b):
        return 0.0
    best = math.inf
    for p, q in segments(a):
        for r, s in segments(b):
            best = min(best, G.point_segment_distance(p, r, s), G.point_segment_distance(q, r, s),
                       G.point_segment_distance(r, p, q), G.point_segment_distance(s, p, q))
    return best


def _parallel(deg_a: float, deg_b: float) -> bool:
    diff = G.angle_difference_deg(deg_a % 180.0, deg_b % 180.0)
    return min(diff, 180.0 - diff) <= PARALLEL_DEG + 1e-9


def back_on_wall(center, rot: float, size, room) -> bool:
    """The back edge stands on a wall (``plausibility.back_on_wall``: at least ``BACK_SHARE`` of it within
    ``BACK_WALL_M`` of the room outline, the nearest outline segment parallel within ``PARALLEL_DEG``)."""
    room_pts = FS.ccw(room)
    w, d = float(size[0]) / 2.0, float(size[1]) / 2.0
    pts = [_world(center, rot, -w + 2.0 * w * t, d) for t in (0.05, 0.25, 0.5, 0.75, 0.95)]
    near = [FS._ring_distance(p, room_pts) for p in pts]
    share = sum(1 for d in near if d <= BACK_WALL_M + 0.005) / len(near)
    if share < BACK_SHARE - 1e-9:
        return False
    mid = pts[len(pts) // 2]
    seg = min(segments(room_pts), key=lambda s: G.point_segment_distance(mid, s[0], s[1]))
    return _parallel(G.segment_angle_deg(seg[0], seg[1]), rot)


def _others(f: dict, pieces: Sequence[dict]) -> list[tuple[str, str, list]]:
    """``(id, type, corners)`` of the built pieces of ``f``'s room other than ``f``."""
    out = []
    for g in pieces:
        if g is f or g.get("id") == f.get("id") or g.get("build") is False or not (g.get("footprint") or {}).get("size"):
            continue
        if f.get("room_id") is not None and g.get("room_id") != f.get("room_id"):
            continue
        out.append((str(g.get("id")), str(g.get("type") or "unknown"), FS.footprint_rect(g["footprint"])))
    return out


# --------------------------------------------------------------------------
# Rule 1: the access zone in front of a door or drawer
# --------------------------------------------------------------------------

def access_of(ftype: Optional[str], width: Optional[float] = None, storage: bool = False
              ) -> Optional[tuple[float, float]]:
    """``(open_m, use_m)`` of a door-fronted type (module docstring), None for any other; a fridge's door swing is its
    door's width (half the fridge over ``FRIDGE_ONE_DOOR_M``). ``storage``: door-fronted storage too (its use depth is
    G13's walking room, so here only the depth to open)."""
    t = str(ftype or "")
    if t in ACCESS_M:
        lo, use = ACCESS_M[t]
        if t == "fridge" and width:
            door = float(width) if float(width) <= FRIDGE_ONE_DOOR_M else float(width) / 2.0
            use = max(use, round(door, 3))
        return lo, use
    if storage and t in STORAGE_OPEN_M:
        return STORAGE_OPEN_M[t], STORAGE_OPEN_M[t]
    return None


def access_problem(ftype: str, center, rotation_deg: float, size, room, obstacles: Sequence[tuple] = (), *,
                   storage: bool = False, walls: bool = True) -> Optional[dict]:
    """Rule 1 (module docstring) for a piece in the frame of its front (``frame``): ``{"free_m", "open_m", "use_m",
    "severity": critical (cannot open) | major (cannot be used), "blockers": [ids within the use depth], "wall": the
    room's outline within it}``, None when the front is free (or the type has no door). ``obstacles``: ``(id, type,
    corners)`` of the other pieces. ``walls`` False: only the pieces count (the caller reports a wall itself)."""
    need = access_of(ftype, float(size[0]), storage)
    if need is None:
        return None
    open_m, use_m = need
    own = FS.rect(center, size, rotation_deg)
    keyed = []
    if walls:
        keyed += [("wall", a, b) for a, b in segments(FS.ccw(room))]
    for oid, otype, corners in obstacles:
        if otype in LIGHT_TYPES or not corners or len(corners) < 3:
            continue
        if FS.cut_depth(own, corners) > FS.CUT_EPS_M:
            continue                     # built into it or cut through: its outline is no obstacle in front of it
        keyed += [(oid, a, b) for a, b in segments(corners)]
    u = _dir(G.front_direction_deg(rotation_deg))
    pts = edge_points(center, rotation_deg, size, "front")
    if walls:
        # a point of the front edge outside the room stands through a side wall (its rays leave the room): left out;
        # the whole front edge on the wall line or past it faces that wall
        room_pts = FS.ccw(room)
        pts = [p for p in pts if G.point_in_polygon((p[0] + u[0] * 2e-3, p[1] + u[1] * 2e-3), room_pts)]
    if pts:
        free, hits = ray_clear(pts, u, keyed, max(RAY_M, use_m + 0.1))
    else:
        free, hits = 0.0, {"wall": 0.0}
    if free >= use_m - 1e-9:
        return None
    blockers = sorted((k for k, t in hits.items() if k != "wall" and t < use_m - 1e-9), key=lambda k: (hits[k], k))
    return {"free_m": free, "open_m": open_m, "use_m": use_m,
            "severity": "critical" if free < open_m - 1e-9 else "major", "blockers": blockers,
            "wall": hits.get("wall", math.inf) < use_m - 1e-9}


def piece_access(f: dict, room, pieces: Sequence[dict] = (), *, storage: bool = False, walls: bool = True
                 ) -> Optional[dict]:
    """``access_problem`` of a furniture dict as built (its front, else the builder's) among the room's ``pieces``."""
    fp = f.get("footprint") or {}
    if not fp.get("center") or not fp.get("size") or access_of(f.get("type"), None, storage) is None:
        return None
    rot, size = frame(fp, f.get("front_deg"))
    return access_problem(str(f["type"]), fp["center"], rot, size, room, _others(f, pieces), storage=storage,
                          walls=walls)


def describe(f: dict, problem: dict) -> str:
    """One sentence on a blocked front (the finding's message)."""
    what = []
    if problem.get("blockers"):
        what.append(", ".join(problem["blockers"][:3]))
    if problem.get("wall"):
        what.append("the wall")
    can = "its door or drawers cannot open" if problem["severity"] == "critical" else "it cannot be used"
    return (f"{f.get('type')} {f.get('id')}: {problem['free_m']:.2f} m free in front of it "
            f"({' and '.join(what) or 'blocked'} in the way); {can} (needs {problem['open_m']:.2f} m to open, "
            f"{problem['use_m']:.2f} m to use)")


# --------------------------------------------------------------------------
# Rule 2: a blocked drawn front turned to its free side (or moved at most 0.5 m)
# --------------------------------------------------------------------------

def in_run(f: dict, pieces: Sequence[dict]) -> bool:
    """The piece stands in a kitchen counter run (within ``RUN_TOUCH_M`` of a counter or an island)."""
    fp = f.get("footprint") or {}
    if not fp.get("size") or str(f.get("type")) in RUN_TYPES:
        return str(f.get("type")) in RUN_TYPES
    own = FS.footprint_rect(fp)
    return any(t in RUN_TYPES and poly_distance(own, c) <= RUN_TOUCH_M for _i, t, c in _others(f, pieces))


def _wall_places(size, room_pts, obstacles, near: Point, max_m: float) -> list[tuple[Point, float]]:
    """``(centre, rotation)`` of every place within ``max_m`` of ``near`` where a piece of ``size`` (width along the
    front, depth) stands with its back ``SNAP_GAP_M`` off a wall of the room and its front into the room."""
    out = []
    w, d = float(size[0]), float(size[1])
    for a, b in segments(room_pts):
        length = G.distance(a, b)
        if length < w - 1e-9:
            continue
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        inward = (-u[1], u[0])                     # the room is counter-clockwise: its inside is on the left
        rot = G.normalise_angle(round(math.degrees(math.atan2(-u[1], -u[0])), 6))
        for s0 in FS._starts(length, w, a, u, obstacles, room_pts):
            if s0 < -1e-9 or s0 + w > length + 1e-9:
                continue
            c = (a[0] + u[0] * (s0 + w / 2.0) + inward[0] * (d / 2.0 + SNAP_GAP_M),
                 a[1] + u[1] * (s0 + w / 2.0) + inward[1] * (d / 2.0 + SNAP_GAP_M))
            if G.distance(c, near) <= max_m + 1e-9:
                out.append(((round(c[0], 4), round(c[1], 4)), rot))
    return out


def _clear(ftype: str, center, rot: float, size, room_pts, obstacles, blocked, need_back: bool,
           cut_ok: Optional[dict] = None) -> bool:
    r = FS.rect(center, size, rot)
    if not FS.inside_room(r, room_pts):
        return False
    for oid, otype, corners in obstacles:
        if otype in LIGHT_TYPES:
            continue
        if FS.cut_depth(r, corners) > max(FS.CUT_EPS_M, (cut_ok or {}).get(oid, 0.0) + 1e-6):
            return False
    if blocked is not None and blocked(r):
        return False
    return not need_back or back_on_wall(center, rot, size, room_pts)


def free_front(f: dict, room, pieces: Sequence[dict] = (), *, blocked: Optional[Callable] = None,
               max_move: float = MOVE_MAX_M) -> Optional[dict]:
    """Rule 2 (module docstring): the place of a door-fronted piece whose door cannot open (``piece_access`` critical:
    a wall or a piece within its opening depth; a tight front that opens is the score's F6 major, not a reading
    error): turned in place to its free side with its back on a wall, else moved at most ``max_move`` to a wall
    place with its front free. ``{"footprint": {center, size, rotation_deg} (in the frame of the new front),
    "front_deg", "how": "turned" | "moved", "turn_deg", "moved_m", "free_m", "was": the problem, "reason"}``; None
    when the front is free, the piece stands in a kitchen run, or no such place exists. Pure: ``f`` is unchanged."""
    fp = f.get("footprint") or {}
    ftype = str(f.get("type") or "")
    if access_of(ftype) is None or not fp.get("center") or not fp.get("size"):
        return None
    was = piece_access(f, room, pieces)
    if was is None or was["severity"] != "critical" or in_run(f, pieces):
        return None                      # a door that opens (a tight front) is no reading error: the score reports it
    room_pts = FS.ccw(room)
    if len(room_pts) < 3:
        return None
    obstacles = _others(f, pieces)
    own = FS.footprint_rect(fp)
    cut_ok = {oid: FS.cut_depth(own, c) for oid, _t, c in obstacles}     # a cut it already has is not new
    rot0, (w, d) = frame(fp, f.get("front_deg"))
    center = (float(fp["center"][0]), float(fp["center"][1]))
    turns = (2, 1, 3) if abs(w - d) <= SQUARE_TOL_M + 1e-9 else (2,)
    best = None
    for k in turns:
        # turned in place: the same rectangle (no new cut, no new step into a door swing); its back and its door decide
        rot = G.normalise_angle(rot0 + 90.0 * k)
        size = (d, w) if k % 2 else (w, d)
        if not back_on_wall(center, rot, size, room_pts):
            continue
        prob = access_problem(ftype, center, rot, size, room_pts, obstacles)
        if prob is not None:
            continue
        free, _h = ray_clear(edge_points(center, rot, size, "front"), _dir(G.front_direction_deg(rot)),
                             [("wall", a, b) for a, b in segments(room_pts)])
        key = (-free, k)
        if best is None or key < best[0]:
            best = (key, center, rot, size, "turned", 0.0)
    if best is None and max_move > 0:
        corners = [c for _i, t, c in obstacles if t not in LIGHT_TYPES]
        for c, rot in _wall_places((w, d), room_pts, corners, center, max_move):
            if not _clear(ftype, c, rot, (w, d), room_pts, obstacles, blocked, True, cut_ok):
                continue
            if access_problem(ftype, c, rot, (w, d), room_pts, obstacles) is not None:
                continue
            dist = G.distance(c, center)
            key = (round(dist, 4), G.angle_difference_deg(rot, rot0))
            if best is None or key < best[0]:
                best = (key, c, rot, (w, d), "moved", dist)
    if best is None:
        return None
    _key, c, rot, size, how, dist = best
    front = G.front_direction_deg(rot)
    old_front = G.front_direction_deg(rot0)
    turn = round(G.angle_difference_deg(front, old_front), 1)
    in_way = ", ".join(was["blockers"][:3] + (["the wall"] if was.get("wall") else [])) or "blocked"
    after = (f"turned {turn:.0f} deg in place to its free side ({front:.0f} deg), its back on a wall"
             if how == "turned" else f"moved {dist:.2f} m to a free place on a wall, facing {front:.0f} deg")
    reason = (f"{ftype} {f.get('id')}: its front ({old_front:.0f} deg) had {was['free_m']:.2f} m free ({in_way} in the "
              f"way; its door or drawers need {was['open_m']:.2f} m to open, {was['use_m']:.2f} m to use): a front "
              f"read the wrong way round (a reading error): {after}")
    return {"footprint": {"center": [round(c[0], 4), round(c[1], 4)], "size": [round(size[0], 4), round(size[1], 4)],
                          "rotation_deg": round(rot, 3)},
            "front_deg": round(front, 3), "how": how, "turn_deg": turn, "moved_m": round(dist, 3), "was": was,
            "reason": reason}


# --------------------------------------------------------------------------
# Rule 3: a back parallel to its wall a drawing gap off it
# --------------------------------------------------------------------------

def back_gap(f: dict, room) -> Optional[dict]:
    """Rule 3 (module docstring): ``{"gap_m", "normal": the back's outward direction, "segment": [a, b]}`` of a piece
    with a known front (``front_deg``) whose back belongs on a wall and stands parallel to one wall segment between
    ``BACK_GAP_MIN_M`` and ``BACK_GAP_MAX_M`` off it; None otherwise."""
    fp = f.get("footprint") or {}
    if str(f.get("type") or "") not in BACK_TYPES or str(f.get("type")) in SERVICE_GAP_TYPES \
            or f.get("front_deg") is None or not fp.get("size") or not fp.get("center") or f.get("build") is False:
        return None
    room_pts = FS.ccw(room)
    if len(room_pts) < 3:
        return None
    rot, size = frame(fp, f.get("front_deg"))
    pts = edge_points(fp["center"], rot, size, "back", 5, min(0.05, float(size[0]) / 4.0))
    nrm = _dir(G.normalise_angle(rot + 90.0))           # local +Y: out of the back
    segs = segments(room_pts)
    dists, wall = [], None
    for p in pts:
        # the outline straight behind each point of the back: the nearest hit along the back's normal
        hits = [(t, a, b) for a, b in segs if (t := _ray_hit(p, nrm, a, b)) is not None]
        if not hits:
            return None
        t, a, b = min(hits, key=lambda h: h[0])
        if not _parallel(G.segment_angle_deg(a, b), rot):
            return None                                 # behind this part of the back: a corner or another wall
        dists.append(t)
        if wall is None or t < wall[0]:
            wall = (t, a, b)
    lo, hi = min(dists), max(dists)
    if lo < BACK_GAP_MIN_M - 1e-9 or hi > BACK_GAP_MAX_M + 1e-9 or hi - lo > BACK_GAP_EVEN_M + 1e-9:
        return None
    return {"gap_m": round(sum(dists) / len(dists), 3), "normal": [round(nrm[0], 6), round(nrm[1], 6)],
            "segment": [list(wall[1]), list(wall[2])]}


def _unit(f: dict, pieces: Sequence[dict]) -> list[dict]:
    """``f`` and the pieces built into it (``fixture_seat.hosted_pair``, cutting it)."""
    own = FS.footprint_rect(f["footprint"])
    out = [f]
    for g in pieces:
        if g is f or g.get("id") == f.get("id") or g.get("build") is False or not (g.get("footprint") or {}).get("size"):
            continue
        if str(g.get("type")) in FS.HOSTED and str(f.get("type")) in FS.HOSTS + RUN_TYPES \
                and FS.cut_depth(own, FS.footprint_rect(g["footprint"])) > FS.CUT_EPS_M:
            out.append(g)
    return out


def hosted_in(f: dict, pieces: Sequence[dict]) -> Optional[str]:
    """The id of the counter or vanity ``f`` is built into (it moves with its host), else None."""
    if str(f.get("type")) not in FS.HOSTED or not (f.get("footprint") or {}).get("size"):
        return None
    own = FS.footprint_rect(f["footprint"])
    for g in pieces:
        if g is f or g.get("build") is False or not (g.get("footprint") or {}).get("size"):
            continue
        if str(g.get("type")) in FS.HOSTS + RUN_TYPES and FS.cut_depth(own, FS.footprint_rect(g["footprint"])) \
                > FS.CUT_EPS_M:
            return str(g.get("id"))
    return None


def snap_back(f: dict, room, pieces: Sequence[dict] = (), *, blocked: Optional[Callable] = None) -> Optional[dict]:
    """Rule 3 (module docstring): ``{"shift": [dx, dy], "gap_m", "moved_m", "unit": [ids], "footprints": {id: new
    footprint}, "reason"}`` that puts the back of ``f`` (and the pieces built into it) back onto its wall, None when
    its back has no drawing gap, it is built into a host (it moves with it), or the move would cut another piece,
    leave the room or enter a door swing. Pure."""
    gap = back_gap(f, room)
    if gap is None or hosted_in(f, pieces) is not None:
        return None
    room_pts = FS.ccw(room)
    move = gap["gap_m"] - SNAP_GAP_M
    dx, dy = gap["normal"][0] * move, gap["normal"][1] * move
    unit = _unit(f, pieces)
    ids = {str(u.get("id")) for u in unit}
    others = [(str(g.get("id")), str(g.get("type") or "unknown"), FS.footprint_rect(g["footprint"])) for g in pieces
              if str(g.get("id")) not in ids and g.get("build") is not False and (g.get("footprint") or {}).get("size")
              and (f.get("room_id") is None or g.get("room_id") == f.get("room_id"))]
    out = {}
    for u in unit:
        fp = u["footprint"]
        old = FS.footprint_rect(fp)
        new_fp = dict(fp, center=[round(float(fp["center"][0]) + dx, 4), round(float(fp["center"][1]) + dy, 4)])
        r = FS.footprint_rect(new_fp)
        if not FS.inside_room(r, room_pts):
            return None
        for _oid, otype, corners in others:
            if otype in LIGHT_TYPES:
                continue
            if FS.cut_depth(r, corners) > max(FS.CUT_EPS_M, FS.cut_depth(old, corners) + 1e-6):
                return None
        if blocked is not None and blocked(r):
            return None
        out[str(u.get("id"))] = new_fp
    with_ = [str(u.get("id")) for u in unit[1:]]
    reason = (f"{f.get('type')} {f.get('id')}: its back stood {gap['gap_m']:.2f} m off its wall, parallel to it (a "
              f"drawing gap): moved {abs(move):.2f} m back onto the wall" + (f" with {', '.join(with_)} built into it"
                                                                             if with_ else ""))
    return {"shift": [round(dx, 4), round(dy, 4)], "gap_m": gap["gap_m"], "moved_m": round(abs(move), 3),
            "unit": sorted(ids), "footprints": out, "reason": reason}


# --------------------------------------------------------------------------
# Rule 4: a basin under a window
# --------------------------------------------------------------------------

def sill_of(o: dict) -> float:
    v = o.get("sill_height", o.get("sill"))
    return float(v) if v is not None else DEFAULT_SILL_M


def basin_window(f: dict, openings: Sequence[dict], walls: dict) -> Optional[dict]:
    """Rule 4 (module docstring): ``{"window", "sill_m", "overlap_m", "share"}`` of the window on the wall behind a
    basin that lies over at least ``BASIN_UNDER_SHARE`` of its width with its sill under ``BASIN_SILL_M``; None when
    the wall over the basin is solid (or the window over it is high). ``walls``: wall id -> wall."""
    fp = f.get("footprint") or {}
    if str(f.get("type") or "") not in BASINS or not fp.get("center") or not fp.get("size") or f.get("build") is False:
        return None
    rot, (w, d) = frame(fp, f.get("front_deg"))
    u = _dir(rot)                                    # along the back edge (local +X)
    nrm = _dir(G.normalise_angle(rot + 90.0))        # out of the back (local +Y)
    back = _world(fp["center"], rot, 0.0, d / 2.0)
    best = None
    for o in openings:
        if o.get("type") != "window" or not o.get("center") or (f.get("level_id") is not None and o.get("level_id")
                                                                   not in (None, f.get("level_id"))):
            continue
        sill = sill_of(o)
        if sill >= BASIN_SILL_M - 1e-9:
            continue
        wall = walls.get(o.get("wall_id")) or {}
        if wall.get("start") and wall.get("end") and not _parallel(G.segment_angle_deg(wall["start"], wall["end"]), rot):
            continue
        oc = (float(o["center"][0]), float(o["center"][1]))
        behind = (oc[0] - back[0]) * nrm[0] + (oc[1] - back[1]) * nrm[1]
        half_t = float(wall.get("thickness") or 0.2) / 2.0
        if behind < -0.05 or behind > half_t + WINDOW_BEHIND_M:
            continue
        along = (oc[0] - back[0]) * u[0] + (oc[1] - back[1]) * u[1]
        half = float(o.get("width") or 0.0) / 2.0
        overlap = max(0.0, min(along + half, w / 2.0) - max(along - half, -w / 2.0))
        if w > 0 and overlap >= BASIN_UNDER_SHARE * w - 1e-9 and (best is None or overlap > best["overlap_m"]):
            best = {"window": str(o.get("id")), "sill_m": round(sill, 3), "overlap_m": round(overlap, 3),
                    "share": round(overlap / w, 3)}
    return best


def clear_basin(f: dict, room, pieces: Sequence[dict], openings: Sequence[dict], walls: dict, *,
                blocked: Optional[Callable] = None, max_move: float = MOVE_MAX_M) -> Optional[dict]:
    """Rule 4 (module docstring): the nearest place within ``max_move`` (along its wall or on another wall of its room)
    where the basin stands with its back on a wall, under no low window, inside the room, clear of the other pieces
    and ``blocked``, with ``FIXTURE_FRONT_M`` free in front: ``{"footprint", "front_deg", "how": "moved", "moved_m",
    "was": basin_window, "reason"}``; None when it stands under no low window or no such place exists. Pure."""
    was = basin_window(f, openings, walls)
    if was is None:
        return None
    room_pts = FS.ccw(room)
    if len(room_pts) < 3:
        return None
    fp = f["footprint"]
    rot0, (w, d) = frame(fp, f.get("front_deg"))
    center = (float(fp["center"][0]), float(fp["center"][1]))
    obstacles = _others(f, pieces)
    own = FS.footprint_rect(fp)
    cut_ok = {oid: FS.cut_depth(own, c) for oid, _t, c in obstacles}
    corners = [c for _i, t, c in obstacles if t not in LIGHT_TYPES]
    best = None
    for c, rot in _wall_places((w, d), room_pts, corners, center, max_move):
        if not _clear(str(f["type"]), c, rot, (w, d), room_pts, obstacles, blocked, True, cut_ok):
            continue
        trial = dict(f, footprint={"center": [c[0], c[1]], "size": [w, d], "rotation_deg": rot},
                     front_deg=G.front_direction_deg(rot))
        if basin_window(trial, openings, walls) is not None:
            continue
        keyed = [("wall", a, b) for a, b in segments(room_pts)] + \
            [(oid, a, b) for oid, t, cc in obstacles if t not in LIGHT_TYPES for a, b in segments(cc)]
        free, _h = ray_clear(edge_points(c, rot, (w, d), "front"), _dir(G.front_direction_deg(rot)), keyed)
        if free < FIXTURE_FRONT_M - 1e-9:
            continue
        dist = G.distance(c, center)
        key = (round(dist, 4), G.angle_difference_deg(rot, rot0))
        if best is None or key < best[0]:
            best = (key, c, rot, dist)
    if best is None:
        return None
    _key, c, rot, dist = best
    front = G.front_direction_deg(rot)
    same = G.angle_difference_deg(rot, rot0) < 1.0
    reason = (f"{f.get('type')} {f.get('id')} stood under window {was['window']} (sill {was['sill_m']:.2f} m over "
              f"{was['share']:.0%} of its width: no mirror over it, its tap against the sill): moved {dist:.2f} m "
              + ("along its wall" if same else f"onto another wall of the room (facing {front:.0f} deg)")
              + " to a solid stretch for its mirror")
    return {"footprint": {"center": [round(c[0], 4), round(c[1], 4)], "size": [round(w, 4), round(d, 4)],
                          "rotation_deg": round(rot, 3)},
            "front_deg": round(front, 3), "how": "moved", "moved_m": round(dist, 3), "was": was, "reason": reason}


# --------------------------------------------------------------------------
# The building as built (model review M19 / M22, Argus U10 / U16 / U20)
# --------------------------------------------------------------------------

def _rooms(building: dict) -> dict:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id") and len(r.get("polygon") or []) >= 3}


def _built(building: dict) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("build") is not False
            and (f.get("footprint") or {}).get("size") and str(f.get("type") or "unknown") != "unknown"
            and not (isinstance(f.get("asset"), dict) and f["asset"].get("method") == "none")]


def blocked_fronts(building: dict) -> list[dict]:
    """Every built door-fronted piece (appliances, nightstands, door-fronted storage) whose door or drawers cannot open,
    or an appliance off a kitchen run that cannot be used: ``[{"piece", "room_id", "problem", "message"}]`` (pure)."""
    rooms = _rooms(building)
    pieces = _built(building)
    by_room: dict = {}
    for f in pieces:
        by_room.setdefault(f.get("room_id"), []).append(f)
    out = []
    for f in pieces:
        room = rooms.get(f.get("room_id"))
        if room is None or str(f.get("type")) not in DOOR_FRONTED or f.get("mount_bottom_m"):
            continue
        here = by_room.get(f.get("room_id")) or []
        prob = piece_access(f, room["polygon"], here, storage=True)
        if prob is None:
            continue
        # storage: its walking room is G13's; a kitchen-run piece: its aisle is G8's (soft in a small kitchen): only a
        # door that cannot open at all is reported here
        if prob["severity"] != "critical" and (str(f.get("type")) in STORAGE_OPEN_M or in_run(f, here)):
            continue
        out.append({"piece": f["id"], "room_id": f.get("room_id"), "problem": prob, "message": describe(f, prob)})
    return out


def back_gaps(building: dict) -> list[dict]:
    """Every built piece whose back belongs on a wall and stands a drawing gap off it (rule 3), pure:
    ``[{"piece", "room_id", "gap_m", "message"}]``."""
    rooms = _rooms(building)
    out = []
    for f in _built(building):
        room = rooms.get(f.get("room_id"))
        if room is None or f.get("mount_bottom_m") and str(f.get("type")) not in BASINS:
            continue
        gap = back_gap(f, room["polygon"])
        if gap is None:
            continue
        out.append({"piece": f["id"], "room_id": f.get("room_id"), "gap_m": gap["gap_m"],
                    "message": f"{f.get('type')} {f['id']} stands {gap['gap_m']:.2f} m off its wall, its back parallel "
                               f"to it: a visible gap behind it (a drawing gap; it belongs on the wall)"})
    return out


def basins_under_windows(building: dict) -> list[dict]:
    """Every built basin under a low window (rule 4), pure: ``[{"piece", "room_id", "window", "sill_m", "message"}]``."""
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id")}
    openings = list(building.get("openings") or [])
    out = []
    for f in _built(building):
        got = basin_window(f, openings, walls)
        if got is None:
            continue
        out.append(dict(got, piece=f["id"], room_id=f.get("room_id"),
                        message=f"{f.get('type')} {f['id']} stands under window {got['window']} (sill "
                                f"{got['sill_m']:.2f} m over {got['share']:.0%} of its width): no mirror can hang over "
                                f"it and its tap meets the sill (a window over a basin needs its sill at "
                                f"{BASIN_SILL_M:.2f} m or more)"))
    return out
