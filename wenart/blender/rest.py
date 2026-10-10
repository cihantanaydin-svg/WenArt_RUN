"""Decor resting on the built host mesh, and the contact measurements of check S5 (docs/milestone12.md §4.7, D13;
track S).

What: pure functions (numpy, no ``bpy``) that find where a decor item rests on the built, scaled host piece and
measure how it rests:

- ``MeshCaster``: a ray caster on a triangle mesh (Moller-Trumbore, numpy); ``BVHCaster`` the same interface on
  Blender's ``mathutils.bvhtree.BVHTree`` (only inside Blender). Both answer ``ray`` (first hit) and ``hits``
  (every hit along a ray, sorted).
- ``place_on_top`` (vases, lamps, books on a top; throws and lying cushions on a seat or a mattress): a 3 x 3
  grid of downward rays under the item's footprint; the rest height is the highest hit for a hard item and the
  median for a soft one; at least ``SUPPORT_SHARE`` (80 %) of the grid must hit the host, else the next spot
  towards the host centre is tried.
- ``place_leaning`` (cushions on a sofa or an armchair against its back, pillows on a bed against the headboard):
  the seat (or mattress) height by rays down in front of the item, then horizontal rays from the seat front
  towards the back at three heights of the item find the real backrest (or headboard); the item's back touches it,
  leaning ``lean_deg`` (10-15 degrees), its bottom on the seat; rays to the sides keep it off the arms. No back hit:
  the footprint's back edge (the wall) is the back, said in ``how``.
- ``place_on_shelf`` (books on a bookshelf): one vertical ray through the shelf finds every board top (an upward
  face) and its clearance; the board of the host frame's ``shelf`` index (or the next one with room) gets a ray
  grid of its own.
- ``measure_rest`` (check S5): gap (item underside to the support surface below, over a 3 x 3 grid), penetration
  (depth of the item's sample points inside the host, ray parity in three directions; depth = the shortest of six
  axis rays to the host surface) and the share of the footprint over the support; ``rest_ok`` applies the
  tolerances of ``scene_checks.TOLERANCES``.

Why: Milestone 11 put cushions and throws at a fixed height per host type (``PROXY_HEIGHTS``: a library bed
0.55 m, a sofa seat 0.45 m) and at an x/y from the drawn footprint: they floated above low mattresses, sank into
sofa backs and stood on the model's own pillows (docs/milestone12.md §1.3, 104 hosted items measured). Rays on
the mesh that is really built remove the type table.

How (frames): the host frame is the piece frame of Milestone 2 (origin at the footprint centre on the floor, width
along local X, depth along local Y, front = -Y, back = +Y, turned by ``rotation_deg`` about +Z); every function
takes world-space meshes (the build makes its objects at the world origin with world vertices) and returns world
positions. A pose is ``{"center": [x, y], "z": bottom z (world), "rotation_deg", "lean_deg", "size": [w, d, h],
"how", ...}``; ``pose_vertices`` turns item-local vertices (bottom at z = 0, front -Y) into world vertices: lean
about local X (the top towards +Y), lift so the lowest point is on z = 0, turn, move. Everything is deterministic
(fixed grids, fixed order, no random numbers).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

import numpy as np

GRID = 3                          # a 3 x 3 grid of rays under an item (docs/milestone12.md §4.7)
GRID_SPREAD = 0.35                # grid points at -0.35, 0, +0.35 of each side (the corners stay inside a round item)
SUPPORT_SHARE = 0.80              # at least this share of the grid over the support
TOP_ABOVE_M = 0.5                 # downward rays start this far above the host's highest point
EPS_T = 1e-6
DEDUP_T = 1e-7                    # two hits closer than this along a ray are one (a ray through a shared edge)
PARITY_DIRS = ((0.5773, 0.3141, 0.7536), (-0.4121, 0.6627, 0.6253), (0.2718, -0.7071, 0.6528))
AXIS_DIRS = ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0),
             (0.0, 0.0, -1.0))
MAX_SAMPLES = 300                 # sample points of an item for the penetration test
LEAN_DEG = 12.0                   # cushions lean 10-15 degrees on the back (§4.7)
BACK_PROBE_SHARES = (0.15, 0.5, 0.85)   # horizontal back rays at these shares of the item's height
SEAT_PROBE_SHARE = 0.30           # the seat is probed this share of the host depth behind its front edge
ARM_GAP_M = 0.005                 # a cushion stays this far off an arm
MIN_CUSHION_W = 0.30              # a cushion squeezed narrower than this between the arms is not placed
SHIFT_STEPS = 4                   # a top item tries its spot, then this many steps towards the host centre
TOP_BAND_M = 0.12                 # a cloth point whose host hit is this far below the top hangs over the edge


# --------------------------------------------------------------------------
# Ray casters
# --------------------------------------------------------------------------

def triangles(faces: Sequence[Sequence[int]]) -> list[tuple[int, int, int]]:
    """Fan triangulation of polygon faces (index triples)."""
    out = []
    for f in faces:
        for k in range(1, len(f) - 1):
            out.append((int(f[0]), int(f[k]), int(f[k + 1])))
    return out


class MeshCaster:
    """Ray caster on a world-space triangle mesh (pure numpy). ``hits`` returns every hit ``(t, point, normal)``
    along a ray in distance order (hits closer than ``DEDUP_T`` merged); ``ray`` the first or None. ``normal`` is
    the face normal of the winding (outward for a well-made mesh)."""

    def __init__(self, verts: Sequence[Sequence[float]], faces: Sequence[Sequence[int]]):
        v = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
        tri = np.asarray(triangles(faces), dtype=np.int64).reshape(-1, 3)
        v0 = v[tri[:, 0]] if len(tri) else np.zeros((0, 3))
        e1 = (v[tri[:, 1]] - v0) if len(tri) else np.zeros((0, 3))
        e2 = (v[tri[:, 2]] - v0) if len(tri) else np.zeros((0, 3))
        n = np.cross(e1, e2)
        ln = np.linalg.norm(n, axis=1)
        keep = ln > 1e-14
        self.v0, self.e1, self.e2 = v0[keep], e1[keep], e2[keep]
        self.normals = n[keep] / ln[keep][:, None]
        self.lo = v.min(axis=0) if len(v) else np.zeros(3)
        self.hi = v.max(axis=0) if len(v) else np.zeros(3)

    def _misses_box(self, o: np.ndarray, d: np.ndarray, max_dist: float) -> bool:
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = (self.lo - 1e-6 - o) / d
            t2 = (self.hi + 1e-6 - o) / d
        t1 = np.where(np.isnan(t1), -np.inf, t1)
        t2 = np.where(np.isnan(t2), np.inf, t2)
        tmin = np.max(np.minimum(t1, t2))
        tmax = np.min(np.maximum(t1, t2))
        return bool(tmax < max(tmin, 0.0) or tmin > max_dist)

    def _ts(self, origin, direction, max_dist: float) -> tuple[np.ndarray, np.ndarray]:
        o = np.asarray(origin, dtype=np.float64)
        d = np.asarray(direction, dtype=np.float64)
        d = d / np.linalg.norm(d)
        if not len(self.v0) or self._misses_box(o, d, max_dist):
            return np.zeros(0), np.zeros(0, dtype=np.int64)
        p = np.cross(d, self.e2)
        det = np.einsum("ij,ij->i", self.e1, p)
        ok = np.abs(det) > 1e-14
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        s = o - self.v0
        u = np.einsum("ij,ij->i", s, p) * inv
        q = np.cross(s, self.e1)
        v = (q @ d) * inv
        t = np.einsum("ij,ij->i", self.e2, q) * inv
        ok &= (u >= -1e-9) & (u <= 1.0 + 1e-9) & (v >= -1e-9) & (u + v <= 1.0 + 1e-9) & (t > EPS_T) & (t <= max_dist)
        idx = np.nonzero(ok)[0]
        order = np.argsort(t[idx], kind="stable")
        return t[idx][order], idx[order]

    def hits(self, origin, direction, max_dist: float = 1e9) -> list[tuple[float, tuple, tuple]]:
        ts, idx = self._ts(origin, direction, max_dist)
        o = np.asarray(origin, dtype=np.float64)
        d = np.asarray(direction, dtype=np.float64)
        d = d / np.linalg.norm(d)
        out, last = [], None
        for t, i in zip(ts, idx):
            if last is not None and abs(t - last) < DEDUP_T:
                continue
            last = t
            out.append((float(t), tuple(float(c) for c in o + t * d), tuple(float(c) for c in self.normals[i])))
        return out

    def ray(self, origin, direction, max_dist: float = 1e9):
        h = self.hits(origin, direction, max_dist)
        return h[0] if h else None

    @property
    def bounds(self) -> tuple[tuple, tuple]:
        return tuple(float(c) for c in self.lo), tuple(float(c) for c in self.hi)


class BVHCaster:
    """The ``MeshCaster`` interface on Blender's ``mathutils.bvhtree.BVHTree`` (built from world-space polygons;
    only inside Blender). ``hits`` steps along the ray past each hit."""

    def __init__(self, verts: Sequence[Sequence[float]], faces: Sequence[Sequence[int]]):
        from mathutils.bvhtree import BVHTree

        self.tree = BVHTree.FromPolygons([tuple(map(float, v)) for v in verts], [tuple(int(i) for i in f)
                                                                                  for f in faces])
        arr = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
        self.lo = arr.min(axis=0) if len(arr) else np.zeros(3)
        self.hi = arr.max(axis=0) if len(arr) else np.zeros(3)

    def ray(self, origin, direction, max_dist: float = 1e9):
        from mathutils import Vector

        d = Vector(tuple(map(float, direction))).normalized()
        loc, nor, _index, dist = self.tree.ray_cast(Vector(tuple(map(float, origin))), d, float(max_dist))
        if loc is None:
            return None
        return (float(dist), tuple(loc), tuple(nor))

    def hits(self, origin, direction, max_dist: float = 1e9) -> list[tuple[float, tuple, tuple]]:
        d = np.asarray(direction, dtype=np.float64)
        d = d / np.linalg.norm(d)
        o = np.asarray(origin, dtype=np.float64)
        out, travelled = [], 0.0
        for _ in range(256):
            h = self.ray(o + d * travelled, d, max_dist - travelled)
            if h is None:
                break
            t = travelled + h[0]
            out.append((t, h[1], h[2]))
            travelled = t + 1e-5
        return out

    @property
    def bounds(self) -> tuple[tuple, tuple]:
        return tuple(float(c) for c in self.lo), tuple(float(c) for c in self.hi)


class MultiCaster:
    """Several casters as one (a bed and the bedding the build added on it)."""

    def __init__(self, casters: Sequence):
        self.casters = [c for c in casters if c is not None]

    def hits(self, origin, direction, max_dist: float = 1e9):
        out = [h for c in self.casters for h in c.hits(origin, direction, max_dist)]
        return sorted(out, key=lambda h: h[0])

    def ray(self, origin, direction, max_dist: float = 1e9):
        found = [h for h in (c.ray(origin, direction, max_dist) for c in self.casters) if h is not None]
        return min(found, key=lambda h: h[0]) if found else None

    @property
    def bounds(self):
        bs = [c.bounds for c in self.casters]
        return (tuple(min(b[0][i] for b in bs) for i in range(3)), tuple(max(b[1][i] for b in bs) for i in range(3)))


# --------------------------------------------------------------------------
# Frames and grids
# --------------------------------------------------------------------------

def to_world(center, rotation_deg: float, x: float, y: float) -> tuple[float, float]:
    r = math.radians(float(rotation_deg))
    c, s = math.cos(r), math.sin(r)
    return (float(center[0]) + c * x - s * y, float(center[1]) + s * x + c * y)


def to_local(center, rotation_deg: float, x: float, y: float) -> tuple[float, float]:
    r = math.radians(float(rotation_deg))
    c, s = math.cos(r), math.sin(r)
    dx, dy = x - float(center[0]), y - float(center[1])
    return (c * dx + s * dy, -s * dx + c * dy)


def direction_world(rotation_deg: float, dx: float, dy: float) -> tuple[float, float]:
    r = math.radians(float(rotation_deg))
    return (math.cos(r) * dx - math.sin(r) * dy, math.sin(r) * dx + math.cos(r) * dy)


def grid_points(center, size, rotation_deg: float, n: int = GRID, spread: float = GRID_SPREAD
                ) -> list[tuple[float, float]]:
    """The n x n grid of plan points under a footprint (at -spread .. +spread of each side), world coordinates."""
    w, d = float(size[0]), float(size[1])
    offs = [(-spread + 2.0 * spread * k / (n - 1)) if n > 1 else 0.0 for k in range(n)]
    return [to_world(center, rotation_deg, a * w, b * d) for b in offs for a in offs]


def pose_vertices(verts: Sequence[Sequence[float]], pose: dict) -> list[tuple[float, float, float]]:
    """Item-local vertices (bottom at z = 0, front -Y) placed by ``pose``: lean about local X (top towards +Y),
    lifted so the lowest point stays on z = 0, turned by ``rotation_deg`` and moved to ``center`` / ``z``."""
    a = math.radians(float(pose.get("lean_deg") or 0.0))
    ca, sa = math.cos(a), math.sin(a)
    leaned = [(x, y * ca + z * sa, -y * sa + z * ca) for x, y, z in verts]
    lift = -min((p[2] for p in leaned), default=0.0)
    cx, cy = float(pose["center"][0]), float(pose["center"][1])
    z0 = float(pose["z"])
    r = math.radians(float(pose.get("rotation_deg") or 0.0))
    c, s = math.cos(r), math.sin(r)
    return [(cx + c * x - s * y, cy + s * x + c * y, z0 + z + lift) for x, y, z in leaned]


def _down_hits(caster, points, z_from: float) -> list[Optional[float]]:
    out = []
    for x, y in points:
        h = caster.ray((x, y, z_from), (0.0, 0.0, -1.0))
        out.append(None if h is None else float(h[1][2]))
    return out


def host_top(caster) -> float:
    return float(caster.bounds[1][2])


def support_height(caster, center, size, rotation_deg: float, soft: bool, z_from: Optional[float] = None
                   ) -> dict:
    """The rest height under a footprint (§4.7): a 3 x 3 grid of downward rays from ``z_from`` (default the host's
    top + ``TOP_ABOVE_M``); ``z`` = the highest hit (hard item) or the median (soft item), ``share`` = the hit share,
    ``zs`` the hits (None for a miss)."""
    pts = grid_points(center, size, rotation_deg)
    z0 = host_top(caster) + TOP_ABOVE_M if z_from is None else float(z_from)
    zs = _down_hits(caster, pts, z0)
    got = sorted(z for z in zs if z is not None)
    if not got:
        return {"z": None, "share": 0.0, "zs": zs}
    z = got[-1] if not soft else (got[(len(got) - 1) // 2] + got[len(got) // 2]) / 2.0
    return {"z": float(z), "share": len(got) / len(zs), "zs": zs}


# --------------------------------------------------------------------------
# Placement
# --------------------------------------------------------------------------

def spots_towards(center, host_center, steps: int = SHIFT_STEPS) -> list[tuple[float, float]]:
    cx, cy = float(center[0]), float(center[1])
    hx, hy = float(host_center[0]), float(host_center[1])
    return [(cx + (hx - cx) * k / steps, cy + (hy - cy) * k / steps) for k in range(steps + 1)]


def place_on_top(caster, center, size, rotation_deg: float, soft: bool, host_center=None, attempt: int = 0
                 ) -> Optional[dict]:
    """A lying item on the top under it (a vase on a table, a throw on a seat): the first spot from ``center``
    towards ``host_center`` (``attempt`` skips that many spots: the re-placement of S5) whose ray grid hits the host
    with at least ``SUPPORT_SHARE``; None when no spot does."""
    w, d, h = (float(v) for v in size)
    spots = spots_towards(center, host_center or center)
    for k, spot in enumerate(spots[attempt:], start=attempt):
        sup = support_height(caster, spot, (w, d), rotation_deg, soft)
        if sup["z"] is None or sup["share"] < SUPPORT_SHARE - 1e-9:
            continue
        how = "rays down onto the built top" + (f", moved {k} step(s) towards the host centre" if k else "")
        return {"center": [spot[0], spot[1]], "z": sup["z"], "rotation_deg": float(rotation_deg), "lean_deg": 0.0,
                "size": [w, d, h], "how": how, "share": sup["share"], "support": "top"}
    return None


def _horizontal(caster, origin, direction, max_dist: float = 5.0) -> Optional[float]:
    h = caster.ray(origin, direction, max_dist)
    return None if h is None else float(h[0])


def back_face_offset(t: float, s: float, lean_deg: float) -> tuple[float, float]:
    """``(y, z)`` of the back face of a box of thickness ``t`` leaning ``lean_deg`` (top towards +Y) at the height
    parameter ``s`` along the face, in the item frame (origin at the un-leaned bottom centre, lifted onto z = 0)."""
    a = math.radians(lean_deg)
    return (t / 2.0 * math.cos(a) + s * math.sin(a), s * math.cos(a))


def place_leaning(caster, host_fp: dict, item_center, size, lean_deg: float = LEAN_DEG, soft_host: bool = True,
                  turn_deg: float = 0.0, attempt: int = 0) -> Optional[dict]:
    """A cushion against the real back of a seat, or a pillow against the headboard of a bed (§4.7).

    ``host_fp``: the host footprint (``center``, ``size``, ``rotation_deg``); ``item_center``: the item's planned
    plan position (its x along the host's width is kept); ``size`` = (width, thickness, height). Steps: the seat
    height under the item's front half (rays down, median: a soft seat); horizontal rays from the host's front
    towards its back at three heights of the item find the back (none: the footprint's back edge, said in
    ``how``); the item's centre moves so its leaning back face touches the nearest of them; rays to the sides keep
    it ``ARM_GAP_M`` off the arms (shifted, else narrowed, else None); two passes settle the seat height at the
    final spot. ``attempt`` = 1 (the S5 re-placement) moves the planned spot 0.10 m towards the host centre line."""
    w, t, h = (float(v) for v in size)
    hc, (hw, hd), rot = host_fp["center"], (float(host_fp["size"][0]), float(host_fp["size"][1])), \
        float(host_fp["rotation_deg"])
    lx, _ly = to_local(hc, rot, float(item_center[0]), float(item_center[1]))
    if attempt:
        lx = lx - math.copysign(min(abs(lx), 0.10 * attempt), lx)
    rot_item = rot + float(turn_deg)
    top = host_top(caster) + TOP_ABOVE_M
    back_dir = direction_world(rot, 0.0, 1.0)
    side_dir = direction_world(rot, 1.0, 0.0)
    # 1. the seat in front of the item (the front part of a sofa or the head part of a bed is seat or mattress)
    seat_y = -hd / 2.0 + SEAT_PROBE_SHARE * hd
    probe = [to_world(hc, rot, lx + k * w / 4.0, seat_y) for k in (-1, 0, 1)]
    zs = [z for z in _down_hits(caster, probe, top) if z is not None]
    if not zs:
        return None
    seat = sorted(zs)[len(zs) // 2]
    how = []
    cy_local = None
    for _pass in range(2):
        backs = []
        for f in BACK_PROBE_SHARES:
            s = f * h
            _yb, zb = back_face_offset(t, s, lean_deg)
            z = seat + zb
            ox, oy = to_world(hc, rot, lx, -hd / 2.0 - 0.2)
            dist = _horizontal(caster, (ox, oy, z), (back_dir[0], back_dir[1], 0.0), hd + 0.4)
            if dist is not None:
                backs.append((-hd / 2.0 - 0.2 + dist, s))
        if backs:
            cy_local = min(yb - back_face_offset(t, s, lean_deg)[0] for yb, s in backs)
            what = "the backrest found by horizontal rays"
        else:
            cy_local = hd / 2.0 - back_face_offset(t, h * 0.5, lean_deg)[0]
            what = "no backrest hit: against the footprint's back edge (the wall)"
        # the seat under the item's spot (soft: median of the grid)
        foot = (w, max(t, 0.05))
        sup = support_height(caster, to_world(hc, rot, lx, cy_local - t * 0.25), foot, rot_item, True, top)
        if sup["z"] is not None:
            seat = sup["z"]
        how = [what]
    # 2. arms: rays to both sides at the item's mid height
    mid_z = seat + h * 0.5 * math.cos(math.radians(lean_deg))
    cxw, cyw = to_world(hc, rot, lx, cy_local)
    right = _horizontal(caster, (cxw, cyw, mid_z), (side_dir[0], side_dir[1], 0.0), hw)
    left = _horizontal(caster, (cxw, cyw, mid_z), (-side_dir[0], -side_dir[1], 0.0), hw)
    room_r = (right if right is not None else hw / 2.0 - lx) - ARM_GAP_M
    room_l = (left if left is not None else hw / 2.0 + lx) - ARM_GAP_M
    if room_r < w / 2.0 and room_l > w / 2.0:
        lx -= min(w / 2.0 - room_r, room_l - w / 2.0)
        how.append("shifted off the arm")
    elif room_l < w / 2.0 and room_r > w / 2.0:
        lx += min(w / 2.0 - room_l, room_r - w / 2.0)
        how.append("shifted off the arm")
    total = room_l + room_r
    if total < w:
        if total < MIN_CUSHION_W:
            return None
        lx += (room_r - room_l) / 2.0
        w = total
        how.append(f"narrowed to {w:.2f} m between the arms")
    cx, cy = to_world(hc, rot, lx, cy_local)
    return {"center": [cx, cy], "z": float(seat), "rotation_deg": rot_item, "lean_deg": float(lean_deg),
            "size": [w, t, h], "how": "; ".join(how), "support": "back", "seat_z": float(seat)}


def board_tops(caster, x: float, y: float) -> list[dict]:
    """The board tops under a plan point (a bookshelf): every hit of a downward ray whose face looks up, from the
    lowest, with ``clearance`` = the distance up to the next face looking down (or to the ray's start)."""
    top = host_top(caster) + TOP_ABOVE_M
    hits = caster.hits((x, y, top), (0.0, 0.0, -1.0))
    boards = []
    for i, (_t, p, n) in enumerate(hits):
        if n[2] <= 0.7:
            continue
        above = [q[1][2] for q in hits[:i] if q[2][2] < -0.7]
        ceiling = min(above) if above else top
        boards.append({"z": float(p[2]), "clearance": float(ceiling - p[2])})
    return sorted(boards, key=lambda b: b["z"])


def place_on_shelf(caster, center, size, rotation_deg: float, shelf: Optional[int] = None, attempt: int = 0
                   ) -> Optional[dict]:
    """Books on a shelf board (§4.7: one ray grid per board): the boards under the item's centre
    (``board_tops``); the board ``shelf`` (default 1, the second from the bottom; ``attempt`` takes the next one)
    or the next one up with room for the item's height; then the 3 x 3 grid on that board (highest hit)."""
    w, d, h = (float(v) for v in size)
    boards = [b for b in board_tops(caster, float(center[0]), float(center[1])) if b["clearance"] >= h + 0.005]
    if not boards:
        return None
    want = (1 if shelf is None else int(shelf)) + attempt
    order = boards[min(want, len(boards) - 1):] + boards[:min(want, len(boards) - 1)][::-1]
    for k, b in enumerate(order):
        sup = support_height(caster, center, (w, d), rotation_deg, False, b["z"] + min(b["clearance"], h) - 0.002)
        if sup["z"] is None or sup["share"] < SUPPORT_SHARE - 1e-9 or abs(sup["z"] - b["z"]) > 0.02:
            continue
        index = boards.index(b)
        return {"center": [float(center[0]), float(center[1])], "z": sup["z"], "rotation_deg": float(rotation_deg),
                "lean_deg": 0.0, "size": [w, d, h], "shelf": index, "support": "shelf",
                "how": f"on shelf board {index} of {len(boards)} (z {b['z']:.3f} m, {b['clearance']:.2f} m free)"}
    return None


# --------------------------------------------------------------------------
# Check S5: how an item rests on its host
# --------------------------------------------------------------------------

def sample_points(verts: Sequence[Sequence[float]], limit: int = MAX_SAMPLES) -> np.ndarray:
    arr = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    if len(arr) <= limit:
        return arr
    step = int(math.ceil(len(arr) / limit))
    return arr[::step]


def is_inside(caster, point) -> bool:
    """Ray parity in three oblique directions, majority vote (robust to a ray through an edge)."""
    votes = 0
    for d in PARITY_DIRS:
        votes += len(caster.hits(point, d)) % 2
    return votes >= 2


def depth_inside(caster, point) -> float:
    """The depth of a point inside a mesh: the shortest of the six axis rays to its surface."""
    best = None
    for d in AXIS_DIRS:
        h = caster.ray(point, d)
        if h is not None and (best is None or h[0] < best):
            best = h[0]
    return float(best or 0.0)


def penetration(caster, verts: Sequence[Sequence[float]]) -> float:
    """The deepest sample point of ``verts`` inside the mesh of ``caster`` (0 when none is inside)."""
    lo, hi = (np.asarray(b) for b in caster.bounds)
    worst = 0.0
    for p in sample_points(verts):
        if np.any(p < lo - 1e-9) or np.any(p > hi + 1e-9):
            continue
        if is_inside(caster, tuple(p)):
            worst = max(worst, depth_inside(caster, tuple(p)))
    return worst


def measure_rest(item_verts, item_faces, host_caster, footprint: dict, soft: bool,
                 pen_limit: Optional[float] = None) -> dict:
    """Check S5 of one item (§4.7): over the 3 x 3 grid of ``footprint`` (``center``, ``size``, ``rotation_deg``)
    the item's underside (a ray up into the item) and the host surface below it (the highest host hit at most
    ``pen_limit`` + 0.02 m above the underside); ``gap_m`` = the smallest underside - support (the touching point;
    negative = sunk), ``support_share`` = the share of grid points with an underside that have the host below,
    ``penetration_m`` = the deepest item sample point inside the host (ray parity) or the sunk depth."""
    from wenart.blender import scene_checks as SC

    limit = SC.TOLERANCES["decor_pen_soft_m" if soft else "decor_pen_hard_m"] if pen_limit is None else pen_limit
    item = MeshCaster(item_verts, item_faces)
    lo_z = float(item.lo[2]) - 1.0
    top = host_top(host_caster) + TOP_ABOVE_M
    gaps, with_under, supported = [], 0, 0
    for x, y in grid_points(footprint["center"], footprint["size"], float(footprint.get("rotation_deg") or 0.0)):
        under = item.ray((x, y, lo_z), (0.0, 0.0, 1.0))
        if under is None:
            continue
        with_under += 1
        zu = float(under[1][2])
        below = [h[1][2] for h in host_caster.hits((x, y, max(top, zu + 1.0)), (0.0, 0.0, -1.0))
                 if h[1][2] <= zu + limit + 0.02]
        if not below:
            continue
        supported += 1
        gaps.append(zu - max(below))
    gap = min(gaps) if gaps else None
    pen = penetration(host_caster, item_verts)
    if gap is not None and gap < 0:
        pen = max(pen, -gap)
    return {"gap_m": None if gap is None else round(float(gap), 4), "penetration_m": round(float(pen), 4),
            "support_share": round(supported / with_under, 3) if with_under else 0.0, "grid_points": with_under,
            "soft": bool(soft)}


def rest_ok(m: dict) -> tuple[bool, list[str]]:
    """Whether an S5 measurement passes the tolerances (``scene_checks.TOLERANCES``) and why not."""
    from wenart.blender import scene_checks as SC

    tol = SC.TOLERANCES
    why = []
    if m.get("gap_m") is None:
        why.append("no host surface under the item")
    elif m["gap_m"] > tol["decor_gap_m"] + 1e-9:
        why.append(f"gap {m['gap_m']:.3f} m > {tol['decor_gap_m']} m")
    limit = tol["decor_pen_soft_m"] if m.get("soft") else tol["decor_pen_hard_m"]
    if m.get("penetration_m", 0.0) > limit + 1e-9:
        why.append(f"penetration {m['penetration_m']:.3f} m > {limit} m")
    if m.get("support_share", 0.0) < tol["decor_support_share"] - 1e-9:
        why.append(f"{m.get('support_share', 0.0):.0%} of the footprint over the support < "
                   f"{tol['decor_support_share']:.0%}")
    return (not why), why


def floor_rest(item_verts, floor_z: float) -> dict:
    """S5 for an item on the floor (a rug, a floor plant): its lowest point above the floor."""
    low = min(float(v[2]) for v in item_verts)
    return {"gap_m": round(low - float(floor_z), 4), "penetration_m": round(max(0.0, float(floor_z) - low), 4),
            "support_share": 1.0, "grid_points": 0, "soft": False}


# --------------------------------------------------------------------------
# One decor item: place, build, measure, place once more, or not build (§4.7)
# --------------------------------------------------------------------------

SOFT_DECOR: tuple[str, ...] = ("cushion", "throw")      # the median of the ray grid, not the highest hit
SOFT_HOST_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bed_single",
                                    "bed_double", "bunk_bed", "crib")
SOFT_SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard")
ATTEMPTS = 2                      # placed, then placed once more, then not built (``decor_not_rested``)


def place_item(support: str, caster, host_fp: dict, center, size, rotation_deg: float, soft_item: bool,
               lean_deg: float = 0.0, shelf: Optional[int] = None, attempt: int = 0) -> Optional[dict]:
    """The pose of an item on its support (``host_frame.support``): leaning on a back or a headboard, on a shelf
    board, or lying on a top, a seat or a mattress; None when the host offers no support there."""
    if support in ("back", "headboard"):
        return place_leaning(caster, host_fp, center, size, lean_deg or LEAN_DEG,
                             turn_deg=float(rotation_deg) - float(host_fp["rotation_deg"]), attempt=attempt)
    if support == "shelf":
        return place_on_shelf(caster, center, size, rotation_deg, shelf, attempt)
    if support in ("top", "seat", "mattress"):
        return place_on_top(caster, center, size, rotation_deg, soft_item, host_center=host_fp["center"],
                            attempt=attempt)
    return None


def local_bounds(verts) -> tuple[float, float, float]:
    arr = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    span = arr.max(axis=0) - arr.min(axis=0)
    return float(span[0]), float(span[1]), float(span[2])


def plan_decor(item: dict, host: dict, caster, local_verts, local_faces, support: str,
               lean_deg: float = 0.0, shelf: Optional[int] = None, attempts: int = ATTEMPTS) -> dict:
    """Place one hosted decor item on the built host (``caster``) and check it (S5, §4.7).

    ``local_verts`` / ``local_faces``: the item's mesh in its own frame (bottom on z = 0, centred, front -Y): a
    parametric or textile part, or a library model fitted to its box. Returns ``{"verts", "faces", "pose",
    "rest", "footprint", "attempt"}`` (world vertices that pass S5) or ``{"not_rested": {id, type, host_id,
    support, reason, measured, attempts}}`` after ``attempts`` placements (the second one moves the spot)."""
    w, d, h = local_bounds(local_verts)
    fp = host["footprint"]
    host_fp = {"center": [float(fp["center"][0]), float(fp["center"][1])], "size": [float(v) for v in fp["size"][:2]],
               "rotation_deg": float(fp["rotation_deg"])}
    soft_item = item.get("type") in SOFT_DECOR
    soft_host = host.get("type") in SOFT_HOST_TYPES and support in SOFT_SUPPORTS
    rot = float(item.get("rotation_deg") if item.get("rotation_deg") is not None else host_fp["rotation_deg"])
    center = item.get("center") or host_fp["center"]
    last = {"reason": "no support under the item", "measured": None}
    for attempt in range(attempts):
        pose = place_item(support, caster, host_fp, center, (w, d, h), rot, soft_item, lean_deg, shelf, attempt)
        if pose is None:
            last = {"reason": f"no {support} found on the built host (attempt {attempt + 1})", "measured": None}
            continue
        verts = local_verts
        if pose["size"][0] < w - 1e-9:                       # narrowed between the arms
            k = pose["size"][0] / w
            verts = [(x * k, y, z) for x, y, z in local_verts]
        world = pose_vertices(verts, pose)
        foot = {"center": list(pose["center"]), "size": [pose["size"][0], d], "rotation_deg": pose["rotation_deg"]}
        m = measure_rest(world, local_faces, caster, foot, soft_host)
        ok, why = rest_ok(m)
        if ok:
            return {"verts": world, "faces": [list(f) for f in local_faces], "pose": pose, "rest": m,
                    "footprint": foot, "attempt": attempt + 1}
        last = {"reason": "; ".join(why), "measured": m}
    return {"not_rested": {"id": item.get("id"), "type": item.get("type"), "host_id": host.get("id"),
                           "support": support, "reason": last["reason"], "measured": last["measured"],
                           "attempts": attempts}}


def plan_throw(item: dict, host: dict, caster, floor_z: float) -> dict:
    """A throw draped on its host (``textiles.throw_parts``) and checked (S5 over its rectangle on the top)."""
    from wenart.blender import textiles as T

    fp = host["footprint"]
    host_fp = {"center": [float(fp["center"][0]), float(fp["center"][1])], "size": [float(v) for v in fp["size"][:2]],
               "rotation_deg": float(fp["rotation_deg"])}
    got = T.throw_parts(caster, host_fp, item, floor_z)
    if got is None:
        return {"not_rested": {"id": item.get("id"), "type": "throw", "host_id": host.get("id"), "support": "drape",
                               "reason": "the cloth found no top under it", "measured": None, "attempts": 1}}
    part = got["parts"][0]
    x0, y0, x1, y1 = got["rect"]
    cx, cy = to_world(host_fp["center"], host_fp["rotation_deg"], (x0 + x1) / 2.0, (y0 + y1) / 2.0)
    foot = {"center": [cx, cy], "size": [(x1 - x0) * 0.8, (y1 - y0) * 0.8], "rotation_deg": host_fp["rotation_deg"]}
    soft = host.get("type") in SOFT_HOST_TYPES
    m = measure_rest(part["verts"], part["faces"], caster, foot, soft)
    ok, why = rest_ok(m)
    if not ok:
        return {"not_rested": {"id": item.get("id"), "type": "throw", "host_id": host.get("id"), "support": "drape",
                               "reason": "; ".join(why), "measured": m, "attempts": 1}}
    return {"verts": part["verts"], "faces": part["faces"], "parts": got["parts"], "rest": m, "footprint": foot,
            "attempt": 1, "pose": {"how": "draped on the host (shrinkwrap, 5 mm)", "share": got["drape"]["share"]}}


Placer = Callable[..., Optional[dict]]
