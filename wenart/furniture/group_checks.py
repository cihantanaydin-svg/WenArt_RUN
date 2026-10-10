"""Group checks G1–G14 (docs/milestone12.md §4.6, §4.9, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026); pure, no I/O, the building is never changed:

- ``CHECKS``: ``("G1", ..., "G14")``.
- ``check_room(building: dict, room_id: str) -> list[Violation]`` and ``check_building(building: dict) ->
  {"rooms": {room_id: [Violation]}, "counts": {"critical": n, "major": n, "minor": n}}`` with the M11
  ``Violation = {"check", "severity", "target", "room_id", "message", "metrics"}``; the messages name the numbers
  ("TV unit 52° off the sofa axis, needs ≤ 10°").

What: the arrangement of each functional group is judged, not the count of pieces near an anchor (§1.2: a TV 65° off
its sofa, nightstands at mid-bed, chairs facing away all passed the Milestone 11 checks):

| Check | Rule (minimums of ``groups.yaml`` ``rules``; severity) |
|---|---|
| G1 | TV unit opposite its sofa: centre on the sofa's axis (≤ 0.30 m), facing it (≤ 10°), ≥ 1.50 m from the sofa front (major); no TV unit where the room may hold one (minor) |
| G2 | coffee table between the sofa and its TV, ≥ 0.30 m from the sofa front (major); none (minor) |
| G3 | armchairs face the coffee table or the sofa (≤ 30°) within 2.50 m (major) |
| G4 | one nightstand per free side of the bed head, its back on the headboard line and its side at the bed side (≤ 0.10 m), its front the bed's way (major); a free side without one (minor) |
| G5 | bed: headboard on a wall; ≥ 0.60 m free along each long side that must be free (both for a double bed, one for a single bed) and at the foot (major) |
| G6 | dining: chairs = seats of the table size (none: major, fewer: minor), each facing the table (major), ≥ 0.81 m from the table edge to the wall or piece behind each chair (major), not all chairs on one side when both long sides are free (minor) |
| G7 | desk: a chair in front (minor), ≥ 0.80 m free in front of the desk (major) |
| G8 | kitchen run: sink between fridge and hob along a run (major); landing beside the sink 0.46, the hob 0.30, the fridge 0.38 m (major); hob not in a window band (major); work-triangle legs 1.20–2.70 m, sum ≤ 7.90 m (major); aisle in front of the run ≥ 0.90 m (major) |
| G9 | a sink, a hob and a fridge in every kitchen (room or kitchen zone) (major) |
| G10 | bath: toilet + washbasin (+ shower or bathtub in a bathroom) (major; a WC's washbasin minor); ≥ 0.53 m clear in front of each fixture (major); toilet centre ≥ 0.38 m from a side wall or fixture, washbasin centre ≥ 0.38 m from a side wall (major) |
| G11 | walkways on a 5 cm raster: every door reaches every other door at ≥ 0.60 m (critical) and the entrance door every other door at ≥ 0.80 m (major); every use zone is reached from the entrance at ≥ 0.60 m (major). Only what the empty room allows is required (a narrow corridor never fails by itself) |
| G12 | windows: nothing taller than the sill + 0.05 m within 0.30 m in front of a window (a TV unit counts with its TV, 1.30 m) (major) |
| G13 | wardrobes and other door-fronted storage: ≥ 0.80 m free in front (major) |
| G14 | no piece of a type its room (or the zone it stands in) never holds (major; minor for drawn pieces that are not fixed equipment, as F1) |

Why: one function per check, shared by the solver (``solver.py``), the code critic and the edit validator
(``plausibility``), and the tests.

How: pieces are read in the frame of their fronts (``placer.drawn_piece``; a piece without ``front_deg`` is judged by
the side the builder faces it, ``front_assumed`` in the metrics). Only built floor pieces count (``build: false``,
wall-hung and ``unknown`` pieces are skipped). Groups come from ``groups.group_members`` (the pieces' ``group`` fields,
else the templates). Free distances are measured with rays from a piece's edge to the room outline and the other
pieces (``clear_distance``). ``RoomRaster`` is the 5 cm occupancy raster of a room in its own axis frame (OpenCV
distance transform and connected components); the solver uses it too. An unverified anchor is skipped (as F5).
"""
from __future__ import annotations

import math
from typing import Iterable, Optional

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import geometry as G
from wenart.furniture import groups as GR
from wenart.furniture import placer, schemas

CHECKS: tuple[str, ...] = tuple(f"G{i}" for i in range(1, 15))
SEVERITIES = ("critical", "major", "minor")
WHAT: dict[str, str] = {
    "G1": "TV unit opposite the sofa: on its axis, facing it, at viewing distance",
    "G2": "coffee table between the sofa and the TV, off the sofa front",
    "G3": "armchairs face the coffee table or the sofa",
    "G4": "one nightstand per free side of the bed head",
    "G5": "bed: headboard on a wall, sides and foot free",
    "G6": "dining: chairs by table size, facing it, room to pull out",
    "G7": "desk: chair in front, room behind the desk front",
    "G8": "kitchen run: order, landings, hob off windows, work triangle, aisle",
    "G9": "kitchen completeness: sink, hob, fridge",
    "G10": "bathroom completeness and clearances",
    "G11": "walkways between doors and to every use zone",
    "G12": "nothing taller than the sill in front of a window",
    "G13": "room in front of wardrobes and door-fronted storage",
    "G14": "no piece of a type its room or zone never holds",
}
RASTER_M = 0.05
RAY_M = 6.0
EFFECTIVE_HEIGHT: dict[str, float] = {"tv_unit": 1.30}     # G12: the TV on the unit (assumed 55 inch on a 0.5 m unit)
STORAGE_FRONT_TYPES = ("wardrobe", "tall_cabinet", "display_cabinet", "dresser", "sideboard")
FIXTURE_TYPES = ("toilet", "washbasin", "shower", "bathtub", "washing_machine")
KITCHEN_FIXTURES = {"sink": ("sink_kitchen",), "hob": ("stove",), "fridge": ("fridge",)}
SEAT_TYPES = ("chair", "bench", "bar_stool", "office_chair")
BED_TYPES = ("bed_double", "bed_single", "bunk_bed")
NIGHTSTAND_HEAD_FREE_M = 0.35      # a bed side this free at the head can hold a nightstand (G4)
SEAT_PITCH_M = 0.55                # one seat per 0.55 m of a table side (groups.CHAIR_PITCH_M)
SIDE_BLOCKED_M = 0.45              # a table side closer than this to a wall or piece seats nobody (G6)
FACING_DEG = 45.0
ALWAYS_ALLOWED = ("stair", "floor_lamp", "potted_plant", "side_table", "unknown")


def _violation(check: str, severity: str, target: str, room_id: str, message: str, metrics: Optional[dict] = None
               ) -> dict:
    return {"check": check, "severity": severity, "target": target, "room_id": room_id, "message": message,
            "metrics": dict(metrics or {})}


# --------------------------------------------------------------------------
# Geometry helpers (shared with the solver)
# --------------------------------------------------------------------------

def front_vec(piece: placer.Piece) -> tuple[float, float]:
    a = math.radians(G.front_direction_deg(piece.rotation_deg))
    return math.cos(a), math.sin(a)


def to_local(piece: placer.Piece, point) -> tuple[float, float]:
    """``point`` in the piece's frame: x along the front edge (+x = the right of a person facing it), y towards the
    back (the front is at -depth/2)."""
    dx, dy = float(point[0]) - piece.center[0], float(point[1]) - piece.center[1]
    r = math.radians(piece.rotation_deg)
    c, s = math.cos(r), math.sin(r)
    return dx * c + dy * s, -dx * s + dy * c


def to_world(piece: placer.Piece, local) -> tuple[float, float]:
    return G.rotate_point((piece.center[0] + local[0], piece.center[1] + local[1]), piece.rotation_deg, piece.center)


def local_dir(piece: placer.Piece, v) -> tuple[float, float]:
    """A local direction as a world unit vector."""
    r = math.radians(piece.rotation_deg)
    c, s = math.cos(r), math.sin(r)
    return v[0] * c - v[1] * s, v[0] * s + v[1] * c


def obstacle_lines(ring, polys: Iterable[Polygon]):
    """The room outline and the outlines of ``polys`` as one line geometry (what a ray stops at)."""
    lines = [ring] + [p.exterior for p in polys if p is not None and not p.is_empty]
    return unary_union(lines)


def clear_distance(points, direction, obstacles, max_m: float = RAY_M) -> float:
    """The shortest free distance from ``points`` straight along ``direction`` to ``obstacles`` (lines), capped at
    ``max_m``. Points are moved 1 mm along the direction first (a ray never stops on its own edge)."""
    dx, dy = direction
    best = max_m
    for p in points:
        start = (p[0] + dx * 1e-3, p[1] + dy * 1e-3)
        ray = LineString([start, (start[0] + dx * max_m, start[1] + dy * max_m)])
        hit = ray.intersection(obstacles)
        if hit.is_empty:
            continue
        best = min(best, Point(start).distance(hit) + 1e-3)
    return round(best, 3)


def edge_points(piece: placer.Piece, side: str, y0: Optional[float] = None, y1: Optional[float] = None,
                n: int = 5, inset: float = 0.05) -> list[tuple[float, float]]:
    """Sample points (world) on one edge of the piece: ``front`` (-y), ``back`` (+y), ``left`` (-x), ``right`` (+x);
    for the sides, ``y0..y1`` (local) limits the stretch."""
    w, d = piece.size[0] / 2.0, piece.size[1] / 2.0
    out = []
    for k in range(n):
        t = k / (n - 1) if n > 1 else 0.5
        if side in ("front", "back"):
            x = -w + inset + (2 * w - 2 * inset) * t if w > inset else 0.0
            y = -d if side == "front" else d
        else:
            lo = -d + inset if y0 is None else y0
            hi = d - inset if y1 is None else y1
            y = lo + (hi - lo) * t
            x = -w if side == "left" else w
        out.append(to_world(piece, (x, y)))
    return out


SIDE_NORMALS = {"front": (0.0, -1.0), "back": (0.0, 1.0), "left": (-1.0, 0.0), "right": (1.0, 0.0)}


def side_clear(piece: placer.Piece, side: str, obstacles, y0=None, y1=None) -> float:
    return clear_distance(edge_points(piece, side, y0, y1), local_dir(piece, SIDE_NORMALS[side]), obstacles)


def main_axis_deg(polygon: Polygon) -> float:
    """The room's main axis in [0, 90): the direction (mod 90) of the outline weighted by segment length."""
    coords = list(polygon.exterior.coords)
    weights: dict[float, float] = {}
    for a, b in zip(coords, coords[1:]):
        length = G.distance(a, b)
        if length < 1e-6:
            continue
        ang = round(G.segment_angle_deg(a, b) % 90.0, 1) % 90.0
        weights[ang] = weights.get(ang, 0.0) + length
    if not weights:
        return 0.0
    return max(sorted(weights), key=lambda k: weights[k])


# --------------------------------------------------------------------------
# The room raster (5 cm, in the room's own axis frame)
# --------------------------------------------------------------------------

class RoomRaster:
    """Occupancy raster of a room: cells of ``res`` metres in the frame turned by the room's main axis (so most
    walls and pieces are axis-aligned). Cell (row j, column i) has its centre at local ``(x0 + (i + 0.5) res,
    y0 + (j + 0.5) res)``; ``inside`` = the cell centre lies in the room polygon."""

    def __init__(self, polygon: Polygon, res: float = RASTER_M, angle_deg: Optional[float] = None):
        self.res = float(res)
        self.angle = main_axis_deg(polygon) if angle_deg is None else float(angle_deg)
        c = polygon.centroid
        self.origin = (c.x, c.y)
        self._c, self._s = math.cos(math.radians(-self.angle)), math.sin(math.radians(-self.angle))
        pts = np.array([self.local(p) for p in polygon.exterior.coords])
        self.x0 = float(pts[:, 0].min()) - 2 * self.res
        self.y0 = float(pts[:, 1].min()) - 2 * self.res
        self.nx = int(math.ceil((float(pts[:, 0].max()) - self.x0) / self.res)) + 2
        self.ny = int(math.ceil((float(pts[:, 1].max()) - self.y0) / self.res)) + 2
        xs = self.x0 + (np.arange(self.nx) + 0.5) * self.res
        ys = self.y0 + (np.arange(self.ny) + 0.5) * self.res
        self.cx, self.cy = np.meshgrid(xs, ys)
        self.inside = self.polygon_mask(polygon)

    def local(self, p) -> tuple[float, float]:
        dx, dy = float(p[0]) - self.origin[0], float(p[1]) - self.origin[1]
        return dx * self._c - dy * self._s, dx * self._s + dy * self._c

    def world(self, p) -> tuple[float, float]:
        c, s = self._c, -self._s
        x, y = float(p[0]), float(p[1])
        return x * c - y * s + self.origin[0], x * s + y * c + self.origin[1]

    def cell_of(self, p) -> tuple[int, int]:
        x, y = self.local(p)
        return int(math.floor((y - self.y0) / self.res)), int(math.floor((x - self.x0) / self.res))

    def polygon_mask(self, geom) -> np.ndarray:
        """Cells whose centre lies in ``geom`` (a polygon or a multi-polygon, world coordinates)."""
        from matplotlib.path import Path as MPath

        mask = np.zeros((self.ny, self.nx), dtype=bool)
        for poly in placer.polygon_parts(geom):
            ext = np.array([self.local(p) for p in poly.exterior.coords])
            i0 = max(0, int(math.floor((ext[:, 0].min() - self.x0) / self.res)) - 1)
            i1 = min(self.nx, int(math.ceil((ext[:, 0].max() - self.x0) / self.res)) + 1)
            j0 = max(0, int(math.floor((ext[:, 1].min() - self.y0) / self.res)) - 1)
            j1 = min(self.ny, int(math.ceil((ext[:, 1].max() - self.y0) / self.res)) + 1)
            if i1 <= i0 or j1 <= j0:
                continue
            pts = np.column_stack([self.cx[j0:j1, i0:i1].ravel(), self.cy[j0:j1, i0:i1].ravel()])
            sub = MPath(ext).contains_points(pts).reshape(j1 - j0, i1 - i0)
            for hole in poly.interiors:
                h = np.array([self.local(p) for p in hole.coords])
                sub &= ~MPath(h).contains_points(pts).reshape(j1 - j0, i1 - i0)
            mask[j0:j1, i0:i1] |= sub
        return mask

    def clearance(self, free: np.ndarray) -> np.ndarray:
        """Per cell the distance (metres) to the nearest blocked cell centre (0 on blocked cells)."""
        import cv2

        img = np.ascontiguousarray(free.astype(np.uint8))
        if not img.any():
            return np.zeros(free.shape, dtype=np.float32)
        dist = cv2.distanceTransform(img, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        return dist * self.res

    @staticmethod
    def components(mask: np.ndarray) -> tuple[int, np.ndarray]:
        import cv2

        n, labels = cv2.connectedComponents(np.ascontiguousarray(mask.astype(np.uint8)), connectivity=8)
        return n, labels

    def dilate(self, mask: np.ndarray, radius_m: float) -> np.ndarray:
        import cv2

        r = max(1, int(round(radius_m / self.res)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        return cv2.dilate(np.ascontiguousarray(mask.astype(np.uint8)), kernel).astype(bool)


# --------------------------------------------------------------------------
# The room view
# --------------------------------------------------------------------------

class RoomView:
    """The measured facts of one room for the group checks (read-only views of the building)."""

    def __init__(self, building: dict, room: dict):
        self.building = building
        self.room = room
        self.id = room["id"]
        self.type = room.get("room_type") or "unknown"
        self.ctx = placer.room_context(building, room)
        self.polygon: Polygon = self.ctx.polygon
        self.ring = self.polygon.exterior
        self.items = [f for f in building.get("furniture") or [] if f.get("room_id") == self.id]
        # Built floor pieces only (``groups.piece_is_built``: not ``build: false``, not ``unknown``, not a library
        # gap): what the scene shows is what the group checks judge.
        self.floor = [f for f in self.items if GR.piece_is_built(f) and f.get("footprint")
                      and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None]
        self.by_id = {f["id"]: f for f in self.floor}
        self.pieces: dict[str, placer.Piece] = {}
        for i, f in enumerate(self.floor):
            try:
                self.pieces[f["id"]] = placer.drawn_piece(f, i)
            except (KeyError, TypeError, ValueError):
                continue
        self.polys = {pid: p.polygon() for pid, p in self.pieces.items()}
        self._groups: Optional[list] = None

    @property
    def groups(self) -> list[dict]:
        if self._groups is None:
            self._groups = GR.group_members(self.building, self.id)
        return self._groups

    def typed(self, types) -> list[str]:
        return sorted(pid for pid, f in self.by_id.items() if f["type"] in types and pid in self.pieces)

    def obstacles(self, exclude=()) -> object:
        ex = set(exclude)
        return obstacle_lines(self.ring, [p for pid, p in self.polys.items() if pid not in ex
                                          and self.by_id[pid]["type"] != "unknown"])

    def assumed(self, pid: str) -> dict:
        return {"front_assumed": True} if self.by_id[pid].get("front_deg") is None else {}

    def area(self) -> float:
        return float(self.room.get("area_computed") or self.polygon.area)


def _front_mid(p: placer.Piece) -> tuple[float, float]:
    return to_world(p, (0.0, -p.size[1] / 2.0))


def _deg(v) -> float:
    return round(float(v), 1)


# --------------------------------------------------------------------------
# G1-G3: seating
# --------------------------------------------------------------------------

def tv_geometry(sofa: placer.Piece, tv: placer.Piece) -> dict:
    """``{"axis_offset_m", "angle_deg", "distance_m"}`` of a TV unit seen from a sofa: the TV centre's offset from the
    sofa's axis, the angle between the TV front and the line to the sofa, the distance from the sofa's seat front to
    the TV front along the axis."""
    lx, ly = to_local(sofa, tv.center)
    seat_front = -sofa.size[1] / 2.0
    if sofa.shape == "L":
        x0, x1, seat_front = schemas.l_seat_front(sofa.size, sofa.chaise_side, sofa.chaise_depth, sofa.seat_depth,
                                                  sofa.chaise_width)
        lx -= (x0 + x1) / 2.0
    want = G.normalise_angle(G.front_direction_deg(sofa.rotation_deg) + 180.0)
    angle = G.angle_difference_deg(G.front_direction_deg(tv.rotation_deg), want)
    distance = (seat_front - ly) - tv.size[1] / 2.0
    return {"axis_offset_m": round(abs(lx), 3), "angle_deg": _deg(angle), "distance_m": round(distance, 3),
            "in_front": ly < seat_front}


SIGHT_HEIGHT_M = 0.60           # G1: a piece taller than this between the sofa and its TV blocks the view
SIGHT_FREE_TYPES = ("table_coffee", "ottoman", "side_table")


def sight_blockers(r: RoomView, sid: str, tid: str, geo: dict) -> list[str]:
    """Pieces taller than ``SIGHT_HEIGHT_M`` in the corridor between the sofa's seat front and the TV front (the
    TV's width, at most the seat's)."""
    sofa, tv = r.pieces[sid], r.pieces[tid]
    x0, x1, yf = -sofa.size[0] / 2.0, sofa.size[0] / 2.0, -sofa.size[1] / 2.0
    if sofa.shape == "L":
        x0, x1, yf = schemas.l_seat_front(sofa.size, sofa.chaise_side, sofa.chaise_depth, sofa.seat_depth,
                                          sofa.chaise_width)
    half = min(tv.size[0], x1 - x0) / 2.0
    cx = (x0 + x1) / 2.0
    corridor = placer._local_box(sofa.center, sofa.rotation_deg, cx - half, cx + half, yf - geo["distance_m"], yf)
    out = []
    for pid, poly in sorted(r.polys.items()):
        item = r.by_id[pid]
        if pid in (sid, tid) or item["type"] in SIGHT_FREE_TYPES or item["type"] == "unknown":
            continue
        if effective_height(item) > SIGHT_HEIGHT_M and poly.intersection(corridor).area > 0.02:
            out.append(pid)
    return out


def _g1_g3(r: RoomView) -> list[dict]:
    out = []
    tv_rule, axis = GR.rule("tv_distance"), GR.rule("tv_axis")
    coffee_min = GR.rule_min("coffee_gap")
    allowed = allowed_types_at(r.building, r.room, None)
    for g in r.groups:
        if g["group"] != "seating" or g["anchor_id"] not in r.pieces:
            continue
        sid = g["anchor_id"]
        sofa = r.pieces[sid]
        tvs = [m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") == "tv_unit" and m in r.pieces]
        coffees = sorted((m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") in ("table_coffee", "ottoman")
                          and m in r.pieces), key=lambda m: (r.by_id[m]["type"] != "table_coffee", m))
        arms = [m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") == "armchair" and m in r.pieces]
        geo = None
        if tvs:
            tid = tvs[0]
            geo = tv_geometry(sofa, r.pieces[tid])
            bad = []
            if not geo["in_front"]:
                bad.append("stands behind the sofa's front")
            if geo["axis_offset_m"] > axis["max_offset"] + 1e-9:
                bad.append(f"{geo['axis_offset_m']:.2f} m off the sofa axis, needs ≤ {axis['max_offset']:.2f} m")
            if geo["angle_deg"] > axis["max_angle"] + 1e-9:
                bad.append(f"{geo['angle_deg']:.0f}° off the line to the sofa, needs ≤ {axis['max_angle']:.0f}°")
            if geo["in_front"] and geo["distance_m"] < tv_rule["min"] - 1e-9:
                bad.append(f"{geo['distance_m']:.2f} m from the sofa front, needs ≥ {tv_rule['min']:.2f} m")
            if geo["in_front"] and not bad:
                blockers = sight_blockers(r, sid, tid, geo)
                if blockers:
                    bad.append(f"the view from the sofa is blocked by {', '.join(blockers)} (taller than "
                               f"{SIGHT_HEIGHT_M:.2f} m)")
                    geo = dict(geo, blocked_by=blockers)
            if bad:
                out.append(_violation("G1", "major", tid, r.id, f"TV unit {tid} " + "; ".join(bad),
                                      dict(geo, sofa=sid, **r.assumed(sid))))
        elif "tv_unit" in allowed and r.type in ("living", "other", "dining"):
            out.append(_violation("G1", "minor", sid, r.id, f"{r.by_id[sid]['type']} {sid} has no TV unit opposite",
                                  {"sofa": sid}))
        # G2: the coffee table
        if coffees:
            cid = coffees[0]
            cp = r.pieces[cid]
            lx, ly = to_local(sofa, cp.center)
            seat_front = -sofa.size[1] / 2.0
            half_w = sofa.size[0] / 2.0
            if sofa.shape == "L":
                x0, x1, seat_front = schemas.l_seat_front(sofa.size, sofa.chaise_side, sofa.chaise_depth,
                                                          sofa.seat_depth, sofa.chaise_width)
                lx -= (x0 + x1) / 2.0
                half_w = (x1 - x0) / 2.0
            gap = round(sofa.polygon().distance(r.polys[cid]), 3)
            between = ly < seat_front and abs(lx) <= half_w + 1e-6
            if geo is not None and geo["in_front"]:
                between = between and (seat_front - ly) < geo["distance_m"] + sofa.size[1] * 0.0 + 1e-6
            bad = []
            if not between:
                bad.append("is not between the sofa and its TV" if tvs else "is not in front of the sofa")
            if gap < coffee_min - 1e-9:
                bad.append(f"is {gap:.2f} m from the sofa front, needs ≥ {coffee_min:.2f} m")
            if bad:
                out.append(_violation("G2", "major", cid, r.id, f"coffee table {cid} " + " and ".join(bad),
                                      {"sofa": sid, "gap_m": gap, "axis_offset_m": round(abs(lx), 3),
                                       "ahead_m": round(seat_front - ly, 3)}))
        elif "table_coffee" in allowed and r.type in ("living", "other"):
            out.append(_violation("G2", "minor", sid, r.id, f"{r.by_id[sid]['type']} {sid} has no coffee table",
                                  {"sofa": sid}))
        # G3: armchairs
        fr = GR.rule("armchair_facing")
        targets = coffees + [sid]
        for aid in arms:
            ap = r.pieces[aid]
            best = None
            for t in targets:
                q = _nearest_point(r.polys[t], ap.center)
                dist = round(G.distance(ap.center, q), 3)
                ang = _angle_to(ap, q)
                key = (ang > fr["max_angle"] + 1e-9 or dist > fr["max_distance"] + 1e-9, ang, t)
                if best is None or key < best[0]:
                    best = (key, t, ang, dist)
            _k, t, ang, dist = best
            if ang > fr["max_angle"] + 1e-9 or dist > fr["max_distance"] + 1e-9:
                what = r.by_id[t]["type"]
                out.append(_violation("G3", "major", aid, r.id,
                                      f"armchair {aid} is {ang:.0f}° off the {what} {t} (needs ≤ {fr['max_angle']:.0f}°)"
                                      f" at {dist:.2f} m (needs ≤ {fr['max_distance']:.2f} m)",
                                      dict({"target": t, "angle_deg": ang, "distance_m": dist}, **r.assumed(aid))))
    return out


def _nearest_point(poly: Polygon, p) -> tuple[float, float]:
    if poly.contains(Point(p)):
        return poly.centroid.x, poly.centroid.y
    from shapely.ops import nearest_points

    q = nearest_points(poly, Point(p))[0]
    return q.x, q.y


def _angle_to(piece: placer.Piece, q) -> float:
    dx, dy = q[0] - piece.center[0], q[1] - piece.center[1]
    if math.hypot(dx, dy) < 1e-6:
        return 0.0
    return _deg(G.angle_difference_deg(math.degrees(math.atan2(dy, dx)), G.front_direction_deg(piece.rotation_deg)))


# --------------------------------------------------------------------------
# G4, G5: beds
# --------------------------------------------------------------------------

def head_free_sides(r: RoomView, bid: str, exclude=()) -> dict[str, float]:
    """Per bed side (``left``, ``right``) the free distance at the head (the nightstand's place), nightstands and
    ``exclude`` not counted."""
    bed = r.pieces[bid]
    d = bed.size[1] / 2.0
    ns = set(r.typed(("nightstand",))) | set(exclude) | {bid}
    obstacles = r.obstacles(exclude=ns)
    return {side: side_clear(bed, side, obstacles, d - 0.5, d - 0.05) for side in ("left", "right")}


def nightstand_place(bed: placer.Piece, ns: placer.Piece) -> dict:
    """``{"side", "side_gap_m", "head_offset_m", "front_deg_off"}`` of a nightstand by a bed: which side, the gap to
    the bed side, how far its back line is from the headboard line, its front against the bed's front."""
    lx, ly = to_local(bed, ns.center)
    side = "right" if lx > 0 else "left"
    poly_local = [to_local(bed, p) for p in ns.polygon().exterior.coords]
    near_x = min(abs(abs(x) - bed.size[0] / 2.0) for x, _y in poly_local) if poly_local else 9.0
    inner = min(abs(x) for x, _y in poly_local)
    gap = max(0.0, inner - bed.size[0] / 2.0) if inner >= bed.size[0] / 2.0 - 1e-6 else -near_x
    back = max(y for _x, y in poly_local)
    head_offset = abs(back - bed.size[1] / 2.0)
    off = G.angle_difference_deg(G.front_direction_deg(ns.rotation_deg), G.front_direction_deg(bed.rotation_deg))
    return {"side": side, "side_gap_m": round(gap, 3), "head_offset_m": round(head_offset, 3),
            "front_deg_off": _deg(off)}


def _g4_g5(r: RoomView) -> list[dict]:
    out = []
    gap_max = GR.rule("nightstand_gap")["max"]
    for g in r.groups:
        if g["group"] not in ("sleeping_double", "sleeping_single") or g["anchor_id"] not in r.pieces:
            continue
        bid = g["anchor_id"]
        item = r.by_id[bid]
        btype = item["type"]
        bed = r.pieces[bid]
        if item.get("status") == "unverified" or btype not in BED_TYPES:
            continue
        # G4
        nss = [m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") == "nightstand" and m in r.pieces]
        free = head_free_sides(r, bid)
        free_sides = [s for s, v in free.items() if v >= NIGHTSTAND_HEAD_FREE_M - 1e-9]
        sides_ok: dict[str, str] = {}
        for nid in nss:
            pl = nightstand_place(bed, r.pieces[nid])
            bad = []
            if pl["side_gap_m"] > gap_max + 1e-9 or pl["side_gap_m"] < -0.02:
                bad.append(f"{pl['side_gap_m']:.2f} m from the bed side (needs ≤ {gap_max:.2f} m)")
            if pl["head_offset_m"] > gap_max + 1e-9:
                bad.append(f"its back {pl['head_offset_m']:.2f} m from the headboard line (needs ≤ {gap_max:.2f} m)")
            if pl["front_deg_off"] > FACING_DEG and r.by_id[nid].get("front_deg") is not None:
                bad.append(f"its front {pl['front_deg_off']:.0f}° off the bed's front")
            if not bad and pl["side"] in sides_ok:
                bad.append(f"a second nightstand on the {pl['side']} side ({sides_ok[pl['side']]} is there)")
            if bad:
                out.append(_violation("G4", "major", nid, r.id, f"nightstand {nid} of {btype} {bid}: " + "; ".join(bad),
                                      dict(pl, bed=bid, **r.assumed(nid))))
            else:
                sides_ok[pl["side"]] = nid
        want = schemas.NIGHTSTANDS_PER_BED.get(btype, 1)
        missing = [s for s in free_sides if s not in sides_ok]
        if want >= 2 and missing:
            for s in missing:
                out.append(_violation("G4", "minor", bid, r.id, f"{btype} {bid}: no nightstand on the free {s} side "
                                      f"of the head ({free[s]:.2f} m free)", {"side": s, "free_m": free[s]}))
        elif want == 1 and free_sides and not sides_ok:
            out.append(_violation("G4", "minor", bid, r.id, f"{btype} {bid}: no nightstand at the head",
                                  {"free_sides": free_sides}))
        # G5
        out += _bed_clearances(r, bid)
    return out


def _bed_clearances(r: RoomView, bid: str) -> list[dict]:
    from wenart.furniture import plausibility as PL     # back_on_wall (lazy: plausibility imports this module)

    out = []
    item = r.by_id[bid]
    btype = item["type"]
    bed = r.pieces[bid]
    zone = GR.use_zone(btype)
    ok, metrics = PL.back_on_wall(bed, r)
    if not ok:
        out.append(_violation("G5", "critical", bid, r.id, f"{btype} {bid}: the headboard stands {metrics['back_wall_m']:.2f}"
                              f" m off the wall (needs it on a wall)", dict(metrics, part="headboard", **r.assumed(bid))))
    if not zone:
        return out
    d = bed.size[1] / 2.0
    exclude = set(r.typed(("nightstand",)))
    obstacles = r.obstacles(exclude=exclude | {bid})
    need = zone.get("sides", 0.0)
    head_skip = float(zone.get("head_skip", 0.45))
    sides = {s: side_clear(bed, s, obstacles, -d + 0.05, d - head_skip) for s in ("left", "right")}
    needed = int(zone.get("sides_needed", 2))
    if needed >= 2:
        for s, v in sides.items():
            if v < need - 1e-9:
                out.append(_violation("G5", "major", bid, r.id, f"{btype} {bid}: {v:.2f} m free along the {s} side, "
                                      f"needs ≥ {need:.2f} m", {"part": f"{s}_side", "free_m": v, "needs_m": need}))
    elif max(sides.values()) < need - 1e-9:
        out.append(_violation("G5", "major", bid, r.id, f"{btype} {bid}: {max(sides.values()):.2f} m free along its best "
                              f"side, needs ≥ {need:.2f} m on one side", {"part": "sides", "free_m": max(sides.values()),
                                                                         "needs_m": need}))
    if "foot" in zone:
        foot_ex = exclude | {bid} | {pid for pid in r.typed(("bench", "ottoman"))
                                     if r.polys[pid].distance(r.polys[bid]) <= 0.15}
        foot_obs = r.obstacles(exclude=foot_ex)
        foot = side_clear(bed, "front", foot_obs)
        benches = [pid for pid in foot_ex - exclude - {bid}]
        if benches:      # the free zone is measured past a bench at the foot
            extra = max(r.pieces[b].size[1] for b in benches) + 0.05
            foot = round(foot - extra, 3)
        if foot < zone["foot"] - 1e-9:
            out.append(_violation("G5", "major", bid, r.id, f"{btype} {bid}: {foot:.2f} m free at the foot, needs ≥ "
                                  f"{zone['foot']:.2f} m", {"part": "foot", "free_m": foot, "needs_m": zone["foot"]}))
    return out


# --------------------------------------------------------------------------
# G6, G7: dining, desk
# --------------------------------------------------------------------------

def _table_sides(table: placer.Piece) -> dict[str, tuple]:
    """side -> (outward local normal, edge length)."""
    w, d = table.size
    return {"front": ((0.0, -1.0), w), "back": ((0.0, 1.0), w), "left": ((-1.0, 0.0), d), "right": ((1.0, 0.0), d)}


def _side_of(table: placer.Piece, p) -> str:
    lx, ly = to_local(table, p)
    w, d = table.size[0] / 2.0, table.size[1] / 2.0
    # The side whose outward distance is largest relative to the half size.
    scores = {"front": -ly - d, "back": ly - d, "left": -lx - w, "right": lx - w}
    return max(sorted(scores), key=lambda k: scores[k])


def seats_of(r: RoomView, tid: str, chairs: Iterable[str]) -> dict:
    """``{"want", "sides_free": {side: m}}``: the seats the table size calls for, less the seats of sides that stand
    against a wall or piece (closer than ``SIDE_BLOCKED_M``)."""
    table = r.pieces[tid]
    obstacles = r.obstacles(exclude=set(chairs) | {tid})
    free = {s: side_clear(table, s, obstacles) for s in ("front", "back", "left", "right")}
    want = schemas.count_by_length(max(table.size), schemas.CHAIRS_BY_TABLE_LENGTH)
    w = table.size[0]
    per_long = max(1, min(want // 2, int((w + 0.05) // SEAT_PITCH_M)))
    ends = max(0, min(2, want - 2 * per_long))
    lost = sum(per_long for s in ("front", "back") if free[s] < SIDE_BLOCKED_M - 1e-9)
    lost += sum(1 for k, s in enumerate(("left", "right")) if k < ends and free[s] < SIDE_BLOCKED_M - 1e-9)
    return {"want": max(0, want - lost), "full": want, "sides_free": free, "per_long": per_long}


def _g6(r: RoomView) -> list[dict]:
    out = []
    pull = GR.rule("diner_pullout")["min"]
    for g in r.groups:
        if g["group"] not in ("dining", "balcony") or g["anchor_id"] not in r.pieces:
            continue
        tid = g["anchor_id"]
        if r.by_id[tid].get("status") == "unverified":
            continue
        table = r.pieces[tid]
        chairs = [m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") in SEAT_TYPES and m in r.pieces]
        seats = seats_of(r, tid, chairs)
        want = seats["want"] if g["group"] == "dining" else 2
        if not chairs:
            out.append(_violation("G6", "major", tid, r.id, f"dining table {tid} has no chairs (needs {want})",
                                  {"chairs": 0, "expected": want}))
        elif len(chairs) < want:
            out.append(_violation("G6", "minor", tid, r.id, f"dining table {tid} has {len(chairs)} of {want} chairs",
                                  {"chairs": len(chairs), "expected": want}))
        per_side: dict[str, int] = {}
        for cid in chairs:
            cp = r.pieces[cid]
            if r.by_id[cid]["type"] != "bench":
                q = _nearest_point(r.polys[tid], cp.center)
                ang = _angle_to(cp, q)
                if ang > FACING_DEG + 1e-9:
                    out.append(_violation("G6", "major", cid, r.id, f"chair {cid} is {ang:.0f}° off the table {tid} "
                                          f"(needs ≤ {FACING_DEG:.0f}°)", dict({"table": tid, "angle_deg": ang},
                                                                                 **r.assumed(cid))))
            side = _side_of(table, cp.center)
            per_side[side] = per_side.get(side, 0) + 1
            normal = local_dir(table, SIDE_NORMALS[side])
            lx, ly = to_local(table, cp.center)
            w, d = table.size[0] / 2.0, table.size[1] / 2.0
            if side in ("front", "back"):
                x = min(max(lx, -w + 0.05), w - 0.05)
                starts = [to_world(table, (x + dx, -d if side == "front" else d)) for dx in (-0.15, 0.0, 0.15)]
            else:
                y = min(max(ly, -d + 0.05), d - 0.05)
                starts = [to_world(table, (-w if side == "left" else w, y + dy)) for dy in (-0.15, 0.0, 0.15)]
            others = [m for m in chairs]
            free = clear_distance(starts, normal, r.obstacles(exclude=set(others) | {tid}))
            if free < pull - 1e-9:
                out.append(_violation("G6", "major", cid, r.id, f"chair {cid}: {free:.2f} m from the table edge to the "
                                      f"wall or piece behind, needs ≥ {pull:.2f} m", {"table": tid, "pullout_m": free,
                                                                                      "needs_m": pull}))
        long_free = [s for s in ("front", "back") if seats["sides_free"][s] >= pull - 1e-9]
        if len(chairs) >= 3 and len(long_free) == 2 and min(per_side.get("front", 0), per_side.get("back", 0)) == 0:
            out.append(_violation("G6", "minor", tid, r.id, f"dining table {tid}: all chairs on one long side although "
                                  f"both are free", {"per_side": per_side}))
    return out


def _g7(r: RoomView) -> list[dict]:
    out = []
    need = GR.rule_min("desk_back")
    for g in r.groups:
        if g["group"] != "work" or g["anchor_id"] not in r.pieces:
            continue
        did = g["anchor_id"]
        desk = r.pieces[did]
        chairs = [m for m in g["member_ids"] if r.by_id.get(m, {}).get("type") in ("office_chair", "chair")]
        if not chairs:
            out.append(_violation("G7", "minor", did, r.id, f"desk {did} has no chair", {"chairs": 0}))
        free = side_clear(desk, "front", r.obstacles(exclude=set(chairs) | {did}))
        if free < need - 1e-9:
            out.append(_violation("G7", "major", did, r.id, f"desk {did}: {free:.2f} m free in front, needs ≥ "
                                  f"{need:.2f} m", dict({"free_m": free, "needs_m": need}, **r.assumed(did))))
    return out


# --------------------------------------------------------------------------
# G8, G9: kitchens
# --------------------------------------------------------------------------

def kitchen_contexts(r: RoomView) -> list[tuple[str, Optional[Polygon]]]:
    """``(name, zone polygon or None)`` of the kitchens in this room: the room itself when it is a kitchen (or holds
    the room name of a kitchen, an open kitchen), else its kitchen zones."""
    from wenart.furniture import plausibility as PL

    zones = [z for z in r.room.get("zones") or [] if z.get("kind") == "kitchen" and len(z.get("polygon") or []) >= 3]
    if r.type == "kitchen" or (not zones and "kitchen" in PL.room_types(r.building, r.room)):
        return [(r.id, None)]
    return [(z.get("zone_id") or f"{r.id}.kitchen", Polygon(z["polygon"]).buffer(0)) for z in zones]


def _in_zone(r: RoomView, pid: str, zone: Optional[Polygon]) -> bool:
    if zone is None:
        return True
    return zone.buffer(0.05).contains(Point(r.pieces[pid].center))


def perimeter_param(ctx: placer.RoomContext, p: placer.Piece) -> Optional[tuple[float, float, int]]:
    """``(s0, s1, segment)``: the piece's back edge as an interval of the room outline's length coordinate (the
    outline walked counter-clockwise), or None when its back is not on the outline."""
    mid = p.back_edge().interpolate(0.5, normalized=True)
    if ctx.ring.distance(mid) > 0.10:
        return None
    seg = ctx.nearest_segment((mid.x, mid.y))
    start = sum(G.distance(*ctx.segments[i]) for i in range(seg))
    a, b = ctx.segments[seg]
    d = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    t = (mid.x - a[0]) * ux + (mid.y - a[1]) * uy
    return start + t - p.size[0] / 2.0, start + t + p.size[0] / 2.0, seg


def run_components(r: RoomView, ids: list[str]) -> list[list[str]]:
    """Kitchen run pieces that touch (≤ 0.05 m) in connected groups, in id order."""
    comp: dict[str, int] = {pid: k for k, pid in enumerate(ids)}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if r.polys[a].distance(r.polys[b]) <= 0.05:
                ca, cb = comp[a], comp[b]
                if ca != cb:
                    for k, v in comp.items():
                        if v == cb:
                            comp[k] = ca
    out: dict[int, list[str]] = {}
    for pid in ids:
        out.setdefault(comp[pid], []).append(pid)
    return [sorted(v) for _k, v in sorted(out.items(), key=lambda kv: sorted(kv[1])[0])]


def landings(r: RoomView, comp: list[str]) -> dict[str, dict]:
    """Per appliance of a run (sink, hob, fridge) its free counter on each side along the run: ``{pid: {"left",
    "right", "best", "kind"}}``. The run is walked along the room outline; counters under or beside the appliance
    count, another appliance or a gap > 0.05 m ends a landing."""
    params = {}
    for pid in comp:
        pp = perimeter_param(r.ctx, r.pieces[pid])
        if pp is not None:
            params[pid] = pp
    if not params:
        return {}
    perimeter = r.ring.length
    # Unwrap the outline coordinate at the largest gap between pieces.
    starts = sorted((v[0] % perimeter, pid) for pid, v in params.items())
    cut = 0.0
    if len(starts) > 1:
        gaps = [((starts[(k + 1) % len(starts)][0] - starts[k][0]) % perimeter, k) for k in range(len(starts))]
        _g, k = max(gaps)
        cut = starts[(k + 1) % len(starts)][0]
    iv = {pid: (((v[0] - cut) % perimeter), ((v[0] - cut) % perimeter) + (v[1] - v[0])) for pid, v in params.items()}
    appl = {pid: kind for pid in iv for kind, types in KITCHEN_FIXTURES.items() if r.by_id[pid]["type"] in types}
    counters = [iv[pid] for pid in iv if r.by_id[pid]["type"] == "kitchen_counter"]
    blocks = [iv[pid] for pid in appl] + [iv[pid] for pid in iv if r.by_id[pid]["type"] == "tall_cabinet"]

    def covered(x: float) -> bool:
        return any(a - 1e-6 <= x <= b + 1e-6 for a, b in counters) and not any(a + 1e-6 < x < b - 1e-6
                                                                                  for a, b in blocks)
    out = {}
    step = 0.01
    for pid, kind in appl.items():
        a, b = iv[pid]
        lens = {}
        for side, x0, sgn in (("left", a - step / 2, -1.0), ("right", b + step / 2, 1.0)):
            n = 0
            x = x0
            while covered(x) and n < 600:
                n += 1
                x += sgn * step
            lens[side] = round(n * step, 2)
        out[pid] = {"left": lens["left"], "right": lens["right"], "best": max(lens.values()), "kind": kind}
    return out


def fridge_landing_elsewhere(r: RoomView, pid: str) -> Optional[str]:
    """NKBA's other fridge landings: ``"across"`` (a counter or island at most ``across_max`` in front of the fridge)
    or ``"corner"`` (a counter within ``side_gap`` of a side of the fridge: the run turns the corner beside it);
    None when neither."""
    rule = GR.rule("fridge_landing")
    p = r.pieces[pid]
    w, d = float(p.size[0]), float(p.size[1])
    others = [q for q in r.typed(("kitchen_counter", "kitchen_island")) if q != pid]
    across = placer._local_box(p.center, p.rotation_deg, -w / 2.0, w / 2.0, -d / 2.0 - float(rule.get("across_max", 0.0)),
                               -d / 2.0)
    gap = float(rule.get("side_gap", 0.0))
    sides = [placer._local_box(p.center, p.rotation_deg, x0, x1, -d / 2.0, d / 2.0)
             for x0, x1 in ((w / 2.0, w / 2.0 + gap), (-w / 2.0 - gap, -w / 2.0))]
    if any(r.polys[q].intersection(across).area > 1e-4 for q in others):
        return "across"
    if gap > 0 and any(r.polys[q].intersection(s).area > 1e-4 for q in others if r.by_id[q]["type"] == "kitchen_counter"
                       for s in sides):
        return "corner"
    return None


def _g8_g9(r: RoomView) -> list[dict]:
    out = []
    run_ids = r.typed(GR.KITCHEN_RUN_TYPES)
    for name, zone in kitchen_contexts(r):
        ids = [pid for pid in run_ids if _in_zone(r, pid, zone)]
        islands = [pid for pid in r.typed(("kitchen_island",)) if _in_zone(r, pid, zone)]
        present = {kind: [pid for pid in ids if r.by_id[pid]["type"] in types]
                   for kind, types in KITCHEN_FIXTURES.items()}
        # G9
        for kind, pids in present.items():
            if not pids:
                out.append(_violation("G9", "major", name, r.id, f"kitchen {name} has no {kind} "
                                      f"({' / '.join(KITCHEN_FIXTURES[kind])})", {"missing": kind}))
        if not ids:
            continue
        # G8: order and landings per connected run
        for comp in run_components(r, ids):
            lands = landings(r, comp)
            for pid, land in sorted(lands.items()):
                rule_name = {"sink": "sink_landing", "hob": "hob_landing", "fridge": "fridge_landing"}[land["kind"]]
                need = GR.rule_min(rule_name)
                if land["best"] < need - 1e-9 and land["kind"] == "fridge" and fridge_landing_elsewhere(r, pid):
                    continue
                if land["best"] < need - 1e-9:
                    out.append(_violation("G8", "major", pid, r.id, f"{land['kind']} {pid}: {land['best']:.2f} m of "
                                          f"counter beside it, needs ≥ {need:.2f} m on one side",
                                          {"landing_m": land["best"], "needs_m": need, "left_m": land["left"],
                                           "right_m": land["right"]}))
            kinds = {pid: land["kind"] for pid, land in lands.items()}
            if {"sink", "hob", "fridge"} <= set(kinds.values()):
                params = {pid: perimeter_param(r.ctx, r.pieces[pid]) for pid in kinds}
                pos = {}
                for pid, k in kinds.items():
                    pos.setdefault(k, []).append((params[pid][0] + params[pid][1]) / 2.0)
                f, s, h = min(pos["fridge"]), min(pos["sink"]), min(pos["hob"])
                if not (min(f, h) < s < max(f, h)):
                    sink = next(pid for pid, k in kinds.items() if k == "sink")
                    out.append(_violation("G8", "major", sink, r.id, "the sink is not between the fridge and the hob "
                                          "along the run", {"order": [k for _p, k in sorted(
                                              (min(v), k) for k, v in pos.items())]}))
        for pid in present["hob"]:
            for win in r.ctx.windows:
                if r.polys[pid].intersection(win.band).area > 0.01:
                    out.append(_violation("G8", "major", pid, r.id, f"hob {pid} stands under window {win.id}",
                                          {"window": win.id}))
        if all(present[k] for k in ("sink", "hob", "fridge")):
            pts = {k: _front_mid(r.pieces[present[k][0]]) for k in ("fridge", "sink", "hob")}
            legs = {"fridge-sink": G.distance(pts["fridge"], pts["sink"]), "sink-hob": G.distance(pts["sink"], pts["hob"]),
                    "hob-fridge": G.distance(pts["hob"], pts["fridge"])}
            leg_rule, sum_rule = GR.rule("triangle_leg"), GR.rule("triangle_sum")
            bad = [f"{k} {v:.2f} m" for k, v in legs.items() if v < leg_rule["min"] - 1e-9 or v > leg_rule["max"] + 1e-9]
            total = sum(legs.values())
            if bad or total > sum_rule["max"] + 1e-9:
                out.append(_violation("G8", "major", present["sink"][0], r.id, "work triangle: " + ", ".join(
                    bad or [f"sum {total:.2f} m"]) + f" (legs {leg_rule['min']:.2f}-{leg_rule['max']:.2f} m, sum ≤ "
                    f"{sum_rule['max']:.2f} m)", {"legs_m": {k: round(v, 2) for k, v in legs.items()},
                                                  "sum_m": round(total, 2)}))
        aisle = GR.rule_min("kitchen_aisle")
        worst = None
        for pid in ids + islands:
            if pid in islands:
                continue
            free = side_clear(r.pieces[pid], "front", r.obstacles(exclude={pid}))
            if worst is None or free < worst[0]:
                worst = (free, pid)
        if worst is not None and worst[0] < aisle - 1e-9:
            out.append(_violation("G8", "major", worst[1], r.id, f"kitchen aisle {worst[0]:.2f} m in front of "
                                  f"{r.by_id[worst[1]]['type']} {worst[1]}, needs ≥ {aisle:.2f} m",
                                  {"aisle_m": worst[0], "needs_m": aisle}))
    return out


# --------------------------------------------------------------------------
# G10: baths
# --------------------------------------------------------------------------

def _g10(r: RoomView) -> list[dict]:
    if r.type not in ("bathroom", "wc"):
        return []
    out = []
    types = {r.by_id[pid]["type"] for pid in r.pieces}
    need = [("toilet", "major"), ("washbasin", "major" if r.type == "bathroom" else "minor")]
    for t, sev in need:
        if t not in types:
            out.append(_violation("G10", sev, r.id, r.id, f"{r.type} without a {t}", {"missing": t}))
    if r.type == "bathroom" and not ({"shower", "bathtub"} & types):
        out.append(_violation("G10", "major", r.id, r.id, "bathroom without a shower or a bathtub",
                              {"missing": "shower|bathtub"}))
    front_need = GR.rule_min("fixture_front")
    fixtures = r.typed(FIXTURE_TYPES)
    for pid in fixtures:
        p = r.pieces[pid]
        if r.by_id[pid]["type"] == "washing_machine":
            continue
        free = side_clear(p, "front", r.obstacles(exclude={pid}))
        if free < front_need - 1e-9:
            out.append(_violation("G10", "major", pid, r.id, f"{r.by_id[pid]['type']} {pid}: {free:.2f} m clear in front, "
                                  f"needs ≥ {front_need:.2f} m", dict({"part": "front", "free_m": free,
                                                                       "needs_m": front_need}, **r.assumed(pid))))
    for pid in fixtures:
        t = r.by_id[pid]["type"]
        if t not in ("toilet", "washbasin"):
            continue
        p = r.pieces[pid]
        rule_name = "toilet_side" if t == "toilet" else "washbasin_side"
        need = GR.rule_min(rule_name)
        if t == "toilet":
            obstacles = r.obstacles(exclude={pid} | {q for q in r.pieces if r.by_id[q]["type"] not in FIXTURE_TYPES})
        else:
            obstacles = r.ring
        ys = [0.0, -p.size[1] / 2.0 + 0.05]
        sides = {}
        for side, v in (("left", (-1.0, 0.0)), ("right", (1.0, 0.0))):
            pts = [to_world(p, (0.0, y)) for y in ys]
            sides[side] = clear_distance(pts, local_dir(p, v), obstacles)
        worst = min(sides, key=lambda s: (sides[s], s))
        if sides[worst] < need - 1e-9:
            out.append(_violation("G10", "major", pid, r.id, f"{t} {pid}: centre {sides[worst]:.2f} m from the "
                                  f"{'side wall or fixture' if t == 'toilet' else 'side wall'} on its {worst}, needs ≥ "
                                  f"{need:.2f} m", {"part": "side", "centre_m": sides[worst], "needs_m": need}))
    return out


# --------------------------------------------------------------------------
# G11: walkways (raster)
# --------------------------------------------------------------------------

def other_room_of_door(building: dict, room: dict, door: dict) -> Optional[dict]:
    """The room on the other side of a door (None: outside)."""
    c = Point(door["center"])
    best = None
    for other in building.get("rooms") or []:
        if other.get("id") == room.get("id") or other.get("level_id") != room.get("level_id"):
            continue
        if len(other.get("polygon") or []) < 3:
            continue
        d = Polygon(other["polygon"]).exterior.distance(c)
        if d <= 0.30 and (best is None or (d, other["id"]) < best[0]):
            best = ((d, other["id"]), other)
    return best[1] if best else None


def entrance_door(building: dict, room: dict, ctx: placer.RoomContext) -> Optional[str]:
    """The door a room is entered by: to the outside first, then from a hall or stair, a living or dining room,
    then any; the widest first, then by id."""
    if not ctx.doors:
        return None
    doors = {d["id"]: d for d in placer.room_openings(building, room)[0]}
    rank = {"hall": 1, "stair": 1, "living": 2, "dining": 2}

    def key(dz):
        other = other_room_of_door(building, room, doors[dz.id]) if dz.id in doors else None
        r = 0 if other is None else rank.get(other.get("room_type"), 3)
        return (r, -round(dz.width, 2), dz.id)
    return min(ctx.doors, key=key).id


def use_zone_boxes(size, ftype: str, shape: Optional[str] = None, chaise_side: Optional[str] = None,
                   chaise_depth: Optional[float] = None, rec: bool = False) -> list[tuple[str, tuple]]:
    """The use zones of a piece (``groups.yaml`` ``use_zones``) as boxes ``(name, (x0, x1, y0, y1))`` in the piece's
    frame; ``rec`` = the recommended depths. A bed's sides skip the head (the nightstands' place); a toilet's or a
    washbasin's zone is at least its side clearance wide each way from its centre (and beside its body)."""
    spec = GR.use_zone(ftype)
    if not spec:
        return []
    sfx = "_rec" if rec else ""
    w, d = float(size[0]) / 2.0, float(size[1]) / 2.0
    out = []
    if "front" in spec:
        depth = spec["front" + sfx]
        x0, x1, yf = -w, w, -d
        if shape == "L":
            x0, x1, yf = schemas.l_seat_front(size, chaise_side, chaise_depth)
        if "side_half" in spec:
            half = spec["side_half" + sfx]
            x0, x1 = min(x0, -half), max(x1, half)
            if half > w + 1e-6:
                out.append(("side_left", (-half, -w, -d, d)))
                out.append(("side_right", (w, half, -d, d)))
        out.append(("front", (x0, x1, yf - depth, yf)))
    if "back" in spec:
        out.append(("back", (-w, w, d, d + spec["back" + sfx])))
    if "sides" in spec:
        depth = spec["sides" + sfx]
        y1 = d - float(spec.get("head_skip", 0.45))
        out.append(("left", (-w - depth, -w, -d, y1)))
        out.append(("right", (w, w + depth, -d, y1)))
    if "foot" in spec:
        out.append(("foot", (-w, w, -d - spec["foot" + sfx], -d)))
    return out


def use_zone_polys(piece: placer.Piece, ftype: str, room_poly: Optional[Polygon] = None,
                   rec: bool = False) -> list[tuple[str, Polygon]]:
    """``use_zone_boxes`` of a placed piece as polygons ``(name, polygon)``."""
    return [(name, placer._local_box(piece.center, piece.rotation_deg, *box))
            for name, box in use_zone_boxes(piece.size, ftype, piece.shape, piece.chaise_side, piece.chaise_depth, rec)]


def walkway_report(building: dict, room: dict, ctx: placer.RoomContext, pieces: list[placer.Piece],
                   types: list[str], ids: Optional[list[str]] = None, raster: Optional[RoomRaster] = None,
                   baseline: Optional[dict] = None) -> dict:
    """The walkway facts of a room on the raster: ``{"pairs": [(a, b, needs_m, ok)], "zones": [(piece id, zone name,
    ok)], "entrance"}``. ``baseline`` (the same report of the empty room) limits what is required."""
    raster = raster or RoomRaster(ctx.polygon)
    ids = ids or [f"#{k}" for k in range(len(pieces))]
    occ = np.zeros_like(raster.inside)
    for p in pieces:
        occ |= raster.polygon_mask(p.polygon())
    free = raster.inside & ~occ
    dist = raster.clearance(free)
    main, sec = GR.rule_min("walkway_main"), GR.rule_min("walkway")
    walk = {w: dist >= w / 2.0 - 1e-6 for w in (main, sec)}
    labels = {w: RoomRaster.components(m)[1] for w, m in walk.items()}
    seeds = {}
    for door in ctx.doors:
        strip = raster.polygon_mask(door.zone) if not door.zone.is_empty else np.zeros_like(free)
        seeds[door.id] = strip

    def comps(w, door_id) -> set:
        lab = labels[w][seeds[door_id] & walk[w]]
        return set(int(v) for v in np.unique(lab) if v > 0)

    entrance = entrance_door(building, room, ctx)
    pairs = []
    door_ids = [d.id for d in ctx.doors]
    for i, a in enumerate(door_ids):
        for b in door_ids[i + 1:]:
            need = main if entrance in (a, b) else sec
            ok = bool(comps(need, a) & comps(need, b))
            ok_sec = ok if need == sec else bool(comps(sec, a) & comps(sec, b))
            pairs.append((a, b, need, ok, ok_sec))
    zones = []
    if entrance is not None:
        reach_comps = comps(sec, entrance)
        reach = np.isin(labels[sec], list(reach_comps)) if reach_comps else np.zeros_like(free)
        covered = raster.dilate(reach, sec / 2.0) & free
        for pid, p, t in zip(ids, pieces, types):
            mine = []
            for name, zp in use_zone_polys(p, t, ctx.polygon):
                if name.startswith("side_"):
                    continue                     # a side clearance (toilet, washbasin) is kept free, not walked into
                zm = raster.polygon_mask(zp) & free
                if not zm.any():
                    continue
                mine.append((pid, name, bool((zm & covered).any())))
            if int(GR.use_zone(t).get("sides_needed", 2)) == 1 and any(ok for _p, n, ok in mine if n in ("left",
                                                                                                    "right")):
                mine = [(q, n, True if n in ("left", "right") else ok) for q, n, ok in mine]
            zones += mine
    out = {"pairs": pairs, "zones": zones, "entrance": entrance}
    if baseline is not None:
        allowed = {(a, b): (ok, ok_sec) for a, b, _n, ok, ok_sec in baseline["pairs"]}
        out["pairs"] = [(a, b, n, ok or not allowed.get((a, b), (True, True))[0], ok_sec
                         or not allowed.get((a, b), (True, True))[1]) for a, b, n, ok, ok_sec in pairs]
    return out


def _g11(r: RoomView) -> list[dict]:
    if not r.ctx.doors:
        return []
    raster = RoomRaster(r.polygon)
    ids = [pid for pid in r.pieces if r.by_id[pid]["type"] not in ("unknown",)]
    pieces = [r.pieces[pid] for pid in ids]
    types = [r.by_id[pid]["type"] for pid in ids]
    base = walkway_report(r.building, r.room, r.ctx, [], [], raster=raster)
    rep = walkway_report(r.building, r.room, r.ctx, pieces, types, ids, raster=raster, baseline=base)
    out = []
    for a, b, need, ok, ok_sec in rep["pairs"]:
        if not ok_sec:
            out.append(_violation("G11", "critical", a, r.id, f"no {GR.rule_min('walkway'):.2f} m walkway from door {a} "
                                  f"to door {b}", {"from": a, "to": b, "needs_m": GR.rule_min("walkway")}))
        elif not ok:
            out.append(_violation("G11", "major", a, r.id, f"the main walkway from the entrance door is below "
                                  f"{need:.2f} m between doors {a} and {b}", {"from": a, "to": b, "needs_m": need}))
    for pid, zone, ok in rep["zones"]:
        if not ok:
            out.append(_violation("G11", "major", pid, r.id, f"{r.by_id[pid]['type']} {pid}: its {zone} use zone is not "
                                  f"reached by a {GR.rule_min('walkway'):.2f} m walkway from door {rep['entrance']}",
                                  {"zone": zone, "entrance": rep["entrance"], "needs_m": GR.rule_min("walkway")}))
    return out


# --------------------------------------------------------------------------
# G12-G14
# --------------------------------------------------------------------------

def effective_height(item: dict, piece: Optional[placer.Piece] = None) -> float:
    if item["type"] in EFFECTIVE_HEIGHT:
        return EFFECTIVE_HEIGHT[item["type"]]
    h = item.get("height")
    return float(h) if h is not None else schemas.HEIGHTS.get(item["type"], 1.0)


def _g12(r: RoomView) -> list[dict]:
    out = []
    margin = GR.rule("window_band")["sill_margin"]
    for pid, p in sorted(r.pieces.items()):
        item = r.by_id[pid]
        if item["type"] in ("unknown", "stair"):
            continue
        h = effective_height(item)
        for win in r.ctx.windows:
            if h > win.sill + margin + 1e-9 and r.polys[pid].intersection(win.band).area > 0.01:
                out.append(_violation("G12", "major", pid, r.id, f"{item['type']} {pid} ({h:.2f} m) stands in front of "
                                      f"window {win.id} (sill {win.sill:.2f} m + {margin:.2f})",
                                      {"window": win.id, "height_m": h, "sill_m": win.sill}))
    return out


def _g13(r: RoomView) -> list[dict]:
    out = []
    need = GR.rule_min("storage_front")
    for pid in r.typed(STORAGE_FRONT_TYPES):
        free = side_clear(r.pieces[pid], "front", r.obstacles(exclude={pid}))
        if free < need - 1e-9:
            out.append(_violation("G13", "major", pid, r.id, f"{r.by_id[pid]['type']} {pid}: {free:.2f} m free in front, "
                                  f"needs ≥ {need:.2f} m", dict({"free_m": free, "needs_m": need}, **r.assumed(pid))))
    return out


def allowed_types_at(building: dict, room: dict, point) -> set:
    """Every type a piece may be at ``point`` of the room (None: anywhere in it): the room's types (with the other
    room names its face holds, ``plausibility.room_types``) and lamps, plants, side tables; inside a zone of the room
    (``rooms[].zones``, track R) the zone kind's types too (a kitchen zone of a living room holds kitchen pieces)."""
    from wenart.furniture import plausibility as PL

    out = set(ALWAYS_ALLOWED)
    for t in PL.room_types(building, room):
        out |= set(schemas.allowed_types(t, room.get("room_subtype")))
    zones = [z for z in room.get("zones") or [] if len(z.get("polygon") or []) >= 3]
    for z in zones:
        if point is None or Polygon(z["polygon"]).buffer(0.05).contains(Point(point)):
            kind = {"sleeping": "bedroom", "work": "other"}.get(z.get("kind"), z.get("kind"))
            out |= set(schemas.allowed_types(kind, room.get("room_subtype")))
    return out


def _g14(r: RoomView) -> list[dict]:
    from wenart.furniture import plausibility as PL

    if not any(t in schemas.ALLOWED_TYPES for t in PL.room_types(r.building, r.room)):
        return []
    out = []
    for f in r.floor:
        if f["id"] not in r.pieces:
            continue
        allowed = allowed_types_at(r.building, r.room, r.pieces[f["id"]].center)
        if f["type"] in allowed:
            continue
        drawn = f.get("source") == "from_documents"
        sev = "minor" if drawn and f["type"] not in schemas.FIXED_TYPES else "major"
        out.append(_violation("G14", sev, f["id"], r.id, f"{f['type']} {f['id']} is not a piece of a {r.type} room"
                              + (" (or of the zone it stands in)" if r.room.get("zones") else ""),
                              {"type": f["type"], "room_type": r.type, "drawn": drawn}))
    return out


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

FUNCTIONS = (("G1", _g1_g3), ("G4", _g4_g5), ("G6", _g6), ("G7", _g7), ("G8", _g8_g9), ("G10", _g10),
             ("G11", _g11), ("G12", _g12), ("G13", _g13), ("G14", _g14))


def room_view(building: dict, room_id: str) -> Optional[RoomView]:
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    if len(room.get("polygon") or []) < 3:
        return None
    return RoomView(building, room)


def check_view(r: RoomView, only: Optional[Iterable[str]] = None) -> list[dict]:
    """The violations of a room view, in check order (``only``: the checks to run)."""
    wanted = set(only) if only is not None else set(CHECKS)
    out = []
    for first, fn in FUNCTIONS:
        covers = {"G1": ("G1", "G2", "G3"), "G4": ("G4", "G5"), "G8": ("G8", "G9")}.get(first, (first,))
        if not wanted & set(covers):
            continue
        out.extend(v for v in fn(r) if v["check"] in wanted)
    order = {k: i for i, k in enumerate(CHECKS)}
    return sorted(out, key=lambda v: (order[v["check"]], str(v["target"]), v["message"]))


def check_room(building: dict, room_id: str) -> list[dict]:
    r = room_view(building, room_id)
    return [] if r is None else check_view(r)


def check_building(building: dict) -> dict:
    rooms = {}
    counts = {s: 0 for s in SEVERITIES}
    for room in building.get("rooms") or []:
        vs = check_room(building, room["id"])
        rooms[room["id"]] = vs
        for v in vs:
            counts[v["severity"]] += 1
    return {"rooms": rooms, "counts": counts}


def counts_by_check(result: dict) -> dict[str, int]:
    """``{check: n}`` of a ``check_building`` result (for reports)."""
    out = {k: 0 for k in CHECKS}
    for vs in result["rooms"].values():
        for v in vs:
            out[v["check"]] += 1
    return out
