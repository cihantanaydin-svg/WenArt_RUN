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
  tolerances of ``REST_TOLERANCES`` (= ``scene_checks.TOLERANCES``).

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

Fix round after P4b (17 Oct 2026; integration of the furniture track's ask, the P4b verifier's better fix 1 and 4 of
the bed-decor finding): ``place_leaning(bed=True)`` (``plan_decor`` for the ``headboard`` support,
``textiles.duvet_and_pillows``) looks for the headboard in the head half only: the mattress is probed at
``BED_SEAT_PROBE_SHARES`` of the depth from the foot, the back rays start at mid-bed (local y 0) and skip hits closer
than ``BED_BACK_MIN_HIT_M`` (a start inside a duvet bulge), the rays run at least ``BED_PROBE_MIN_Z_M`` above the
mattress (a lying pillow's lowest ray was 3 mm up), and a back that would still leave the item's centre in the foot
half gives way to the footprint's back edge. Why: the rays started 0.2 m in front of the foot and took a footboard
taller than the mattress, or a duvet roll at the foot, for the headboard (P4b real03: 9 of 14 bed cushions not
rested, two at the foot, 7 of 10 beds without bedding). Sofas are unchanged.

28 Oct 2026 (user on real04 run 20261028-005318-full: "still flying pillows all around", "More flying pillows"; the
sofas of r_L1_oyun_aktivite_ve_dinlenme_odasi, the dressed bed f_L0_007): a leaning cushion touches its back in its
upper part, and S5 measures it.

- What: (1) ``measure_back``: horizontal rays through the item's upper part (``BACK_CONTACT_SHARES`` of its height,
  ``BACK_CONTACT_XS`` of its width) along the host's back direction; ``back_gap_m`` = the smallest gap from the item's
  back surface to the host behind it (or to the host footprint's back edge, the wall, when nothing of the host is
  there); ``rest_ok`` fails a leaning item whose gap is over ``decor_back_gap_m`` or that has nothing behind it.
  (2) ``plan_decor`` leans a cushion at least the styled ``LEAN_DEG`` / ``HEADBOARD_LEAN_DEG`` (the decor stage's
  host frame carries Milestone 12's 12 degrees, which made every planned cushion stand almost upright), then steeper
  (``LEAN_STEEPER_DEG``: a cushion with nothing behind its upper part falls back onto it), then the smaller
  fallbacks; a gap up to ``BACK_SLIDE_MAX_M`` behind it is closed by sliding it back onto its back (a round cushion
  meets a back with its bulge, not with the box corner ``place_leaning`` aims). (3) ``place_leaning`` on a seat: the
  back rays run at least ``SEAT_PROBE_MIN_Z_M`` above the seat, and a hit on a face looking up (``BACK_MAX_NZ``) or on
  something that rises less than ``BACK_MIN_RISE_M`` over the seat is the seat itself, never the back. (4)
  ``back_caster``: a dressed bed's back rays see the bed alone (``furniture.BED_CASTER``: the cushion stands on the
  pillows against the headboard), then the bed and its pillows (``furniture.LEAN_CASTER``: it leans back on them); its
  seat rays and S5 see the whole bedding as built (the duvet and its band too). (5) A cloth: ``measure_cloth`` (the
  host poking through it between its grid points, a torn drape; user on f_L0_021: "I did not like this bed") and
  ``own_bedding`` (no throw over a bed model's own made bedding).
- Why (the run's records): both sofas (abo_B075X4F5CS, 0.90 m deep) had their cushions at local y -0.40 (rest
  footprint) of +-0.45, 4-9 cm behind the seat's front edge and some 0.3 m in front of the backrest: the lowest back
  ray, 1.2 cm over the seat measured at 30 % of the depth, met the domed seat cushion and took it for the back; S5
  passed them (gap -0.004 / -0.012 / -0.016 m at one touching point, no measure behind). The bed's cushions were placed
  and measured on the lean caster without the duvet: the scene check on the bedding as built found 4.9 cm in the duvet
  (S5 critical, dec_L0_011 / dec_L0_012), and their back touched only the lying pillows' low foot seam.
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
# 25 Oct 2026 (user: "pillows on top of the beds and sofas seem to be floating"): an upright 12-degree cushion standing
# on the seat read as hovering; a styled cushion leans back 20 degrees on a sofa and 24 on a headboard and sinks a
# little into the soft seat or mattress (within the soft penetration tolerance of S5)
LEAN_DEG = 20.0
HEADBOARD_LEAN_DEG = 24.0
SOFT_SINK_M = 0.02
# a back that leaves no room for the full lean (a parametric sofa's upright back: 20 degrees cut it 0.096 m) takes the
# next smaller lean before the cushion is given up
LEAN_FALLBACK_DEG = (16.0, 12.0)
BACK_PROBE_SHARES = (0.03, 0.15, 0.5, 0.85, 1.0)   # horizontal back rays at these shares of the item's height
ARM_PROBE_SHARES = (0.1, 0.5)     # side rays at these shares of the item's height (an arm lower than its middle)
SEAT_PROBE_SHARES = (0.30, 0.45, 0.60, 0.75)   # the seat is probed at these shares of the host depth from its front
# Fix round after P4b (module docstring): a bed's headboard is searched in its head half.
BED_SEAT_PROBE_SHARES = (0.55, 0.65, 0.75)     # the mattress under the pillows, never the foot
BED_BACK_MIN_HIT_M = 0.02                      # back rays start mid-bed; a closer hit is the start inside a bulge
BED_PROBE_MIN_Z_M = 0.03                       # back rays at least this far above the mattress
# 27 Oct 2026 (user on real06: "flying pillows"): a cushion leaning on a bed stands in its head zone: its centre within
# this of the head edge (a pillow up to 0.5 m deep and a cushion in front of it); a "backrest" further out (the
# duvet's fold mid-bed) is no headboard
BED_HEAD_ZONE_M = 0.65
# 28 Oct 2026 (module docstring): a leaning cushion rests on its back in its upper part.
LEAN_STEEPER_DEG = (30.0, 38.0, 46.0, 55.0)    # a cushion with nothing behind its upper part falls back further
SEAT_PROBE_MIN_Z_M = 0.04         # a seat's back rays at least this above the seat (a domed or tilted seat cushion)
BACK_MAX_NZ = 0.7                 # a hit face whose normal is steeper than this looks up: the seat, not its back
BACK_MIN_RISE_M = 0.15            # a backrest rises at least this above the seat (a seat cushion's crown does not)
BACK_RISE_PROBES_M = (0.03, 0.08)  # ... measured by rays down this far behind the hit (a reclined back too)
BACK_CONTACT_SHARES = (0.4, 0.55, 0.7, 0.85, 0.95)   # measure_back: the item's upper part (shares of its height) ...
BACK_CONTACT_XS = (-0.25, 0.0, 0.25)                 # ... over its width (shares of its width)
BACK_RAY_FROM_M = 1.0             # the rays start this far in front of the item's base centre
BACK_REACH_M = 0.6                # a back further than this behind the item is no back
SETTLE_SHARES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)   # settle_back: rays over the item's whole height ...
SETTLE_XS = (-0.3, 0.0, 0.3)      # ... and width
BACK_SLIDE_MAX_M = 0.12           # a leaning item slides at most this far (back or forward) onto its back
BACK_PRESS_M = 0.005              # ... pressed this far into a soft back
ARM_GAP_M = 0.005                 # a cushion stays this far off an arm
MIN_CUSHION_W = 0.30              # a cushion squeezed narrower than this between the arms is not placed
SHIFT_STEPS = 4                   # a top item tries its spot, then this many steps towards the host centre
# Check S5's tolerances (§4.7; ``scene_checks.TOLERANCES`` takes them from here): gap, penetration on hard and soft
# hosts, the share of the footprint over the support.
REST_TOLERANCES: dict[str, float] = {"decor_gap_m": 0.010, "decor_pen_hard_m": 0.010, "decor_pen_soft_m": 0.030,
                                     "decor_support_share": 0.80,
                                     # 27 Oct 2026 (user on real06's sofa: "something wrong with the render"): a cloth
                                     # sunk deeper into its host than its own thickness (8 mm) shows the host through
                                     # it: a throw over a sofa's seat end and arm, 2.2 cm in, showed leather patches
                                     "decor_pen_cloth_m": 0.007,
                                     # 28 Oct 2026 (module docstring): a leaning item's back on its back (upper part)
                                     "decor_back_gap_m": 0.015,
                                     # 28 Oct 2026 (user on real04's f_L0_021: "I did not like this bed"): a cloth the
                                     # host pokes through (its top under the host's surface) or a torn drape (two
                                     # neighbouring cloth points far apart: the top under it is not one surface)
                                     "decor_cloth_poke_m": 0.002, "decor_cloth_edge_m": 0.25,
                                     # 28 Oct 2026 (user on real04's salon: "Light is flying in the air needs to be
                                     # connected to ceiling"): a hung light's top (cord and canopy included) at most
                                     # this far below the ceiling over it
                                     "decor_hang_gap_m": 0.02}
TOP_BAND_M = 0.12                 # a cloth point whose host hit is this far below the top hangs over the edge
CLOTH_POKE_GRID = 13              # measure_cloth: a 13 x 13 grid of rays down over the cloth's footprint on the top
#                                   (its pitch is not the drape's 5 cm: the rays fall between the cloth's grid points)


# --------------------------------------------------------------------------
# Supports (the host frame's ``support``; ``wenart.furniture.decor`` re-exports them: Blender's Python has no shapely,
# so the scene builder and the scene checks take them from here)
# --------------------------------------------------------------------------

SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard", "top", "shelf", "floor", "wall", "ceiling")
SEAT_BACK_HOSTS: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise")
BED_HOSTS: tuple[str, ...] = ("bed_single", "bed_double", "bunk_bed", "crib")
LYING_SEAT_HOSTS: tuple[str, ...] = ("ottoman", "bench")
SHELF_HOSTS: tuple[str, ...] = ("bookshelf",)
TOP_HOST_TYPES: tuple[str, ...] = ("table_coffee", "table_dining", "side_table", "nightstand", "dresser", "tv_unit",
                                   "desk", "sideboard", "console_table", "shoe_cabinet", "display_cabinet",
                                   "bookshelf", "kitchen_counter", "kitchen_island", "tall_cabinet", "wardrobe")
WALL_SUPPORT_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock", "curtain", "blind",
                                       # 29 Oct 2026 (UL114, UL123, UL124): the bathroom's wall details
                                       "toilet_paper_holder", "towel_rail", "towel_shelf", "towel_bar",
                                       "feature_panel", "cove_light")
CEILING_SUPPORT_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light")
FLOOR_SUPPORT_TYPES: tuple[str, ...] = ("plant", "plant_large", "rug", "toilet_brush")
RAY_SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard", "top", "shelf")


def support_of(dtype: Optional[str], host_type: Optional[str]) -> str:
    """The support of a decor type on a host type (None: no host) (§4.7); a floor plant or a rug beside its piece
    stands on the floor, a picture hangs on the wall, a light from the ceiling, whatever piece it belongs to."""
    if host_type is None or dtype in WALL_SUPPORT_TYPES + CEILING_SUPPORT_TYPES + FLOOR_SUPPORT_TYPES:
        if dtype in WALL_SUPPORT_TYPES:
            return "wall"
        if dtype in CEILING_SUPPORT_TYPES:
            return "ceiling"
        return "floor"
    if dtype == "cushion":
        if host_type in SEAT_BACK_HOSTS:
            return "back"
        if host_type in BED_HOSTS:
            return "headboard"
        return "seat"
    if dtype == "throw":
        return "mattress" if host_type in BED_HOSTS else "seat"
    if dtype == "book_set" and host_type in SHELF_HOSTS:
        return "shelf"
    return "top"


def support_fits(support: str, host_type: Optional[str]) -> bool:
    """Whether a host of ``host_type`` has the support (a retyped host may lose it: a cushion's sofa back on a table)."""
    if support in ("floor", "wall", "ceiling"):
        return True
    if host_type is None:
        return False
    return {"back": host_type in SEAT_BACK_HOSTS,
            "headboard": host_type in BED_HOSTS, "mattress": host_type in BED_HOSTS,
            "seat": host_type in SEAT_BACK_HOSTS + LYING_SEAT_HOSTS,
            "shelf": host_type in SHELF_HOSTS,
            "top": host_type in TOP_HOST_TYPES}.get(support, False)


def item_support(item: dict, host: Optional[dict]) -> str:
    """An item's support: its ``host_frame.support`` when set, else the type rule (``support_of``)."""
    frame = item.get("host_frame") if isinstance(item.get("host_frame"), dict) else {}
    return str(frame.get("support") or support_of(item.get("type"), host.get("type") if host else None))


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


def _horizontal(caster, origin, direction, max_dist: float = 5.0, min_dist: float = 0.0) -> Optional[float]:
    """The distance to the first hit along a ray (``min_dist``: the first hit at least that far; fix round after
    P4b, a bed's back ray that starts inside a duvet bulge), None without one."""
    if min_dist <= 0.0:
        h = caster.ray(origin, direction, max_dist)
        return None if h is None else float(h[0])
    return next((float(t) for t, _p, _n in caster.hits(origin, direction, max_dist) if float(t) >= min_dist), None)


def _back_hit(caster, origin, direction, max_dist: float, min_dist: float = 0.0, seat_z: Optional[float] = None,
              top_z: Optional[float] = None) -> Optional[float]:
    """The distance to the first hit along a back ray that is a back (28 Oct 2026, module docstring); None without
    one. With ``seat_z`` (a seat, not a bed): a hit on a face looking up (``|n_z| > BACK_MAX_NZ``) or on something
    whose top, by rays down ``BACK_RISE_PROBES_M`` behind the hit from ``top_z``, rises less than ``BACK_MIN_RISE_M``
    over the seat is the seat itself (its domed cushion, its front lip) and the ray goes on."""
    if seat_z is None:
        return _horizontal(caster, origin, direction, max_dist, min_dist)
    d = np.asarray(direction, dtype=np.float64)
    d = d / np.linalg.norm(d)
    for t, p, n in caster.hits(origin, direction, max_dist):
        if float(t) < min_dist:
            continue
        if abs(float(n[2])) > BACK_MAX_NZ:
            continue
        rise = None
        for back in BACK_RISE_PROBES_M:
            q = (float(p[0]) + d[0] * back, float(p[1]) + d[1] * back)
            h = caster.ray((q[0], q[1], float(top_z)), (0.0, 0.0, -1.0))
            if h is not None:
                rise = max(rise if rise is not None else -1e9, float(h[1][2]) - float(seat_z))
        if rise is None or rise < BACK_MIN_RISE_M - 1e-9:
            continue
        return float(t)
    return None


def back_face_offset(t: float, s: float, lean_deg: float) -> tuple[float, float]:
    """``(y, z)`` of the back face of a box of thickness ``t`` leaning ``lean_deg`` (top towards +Y) at the height
    parameter ``s`` along the face, in the item frame (origin at the un-leaned bottom centre, lifted onto z = 0)."""
    a = math.radians(lean_deg)
    return (t / 2.0 * math.cos(a) + s * math.sin(a), s * math.cos(a))


def place_leaning(caster, host_fp: dict, item_center, size, lean_deg: float = LEAN_DEG, soft_host: bool = True,
                  turn_deg: float = 0.0, attempt: int = 0, bed: bool = False, back_caster=None) -> Optional[dict]:
    """A cushion against the real back of a seat, or a pillow against the headboard of a bed (§4.7).

    ``host_fp``: the host footprint (``center``, ``size``, ``rotation_deg``); ``item_center``: the item's planned
    plan position (its x along the host's width is kept); ``size`` = (width, thickness, height). Steps: the seat
    height under the item's front half (rays down, median: a soft seat); horizontal rays from the host's front
    towards its back at three heights of the item find the back (none: the footprint's back edge, said in
    ``how``); the item's centre moves so its leaning back face touches the nearest of them; rays to the sides keep
    it ``ARM_GAP_M`` off the arms (shifted, else narrowed, else None); two passes settle the seat height at the
    final spot. ``attempt`` = 1 (the S5 re-placement) moves the planned spot 0.10 m towards the host centre line.
    ``bed`` (fix round after P4b, module docstring): the headboard of a bed, searched in its head half.
    28 Oct 2026 (module docstring): on a seat the back rays run at least ``SEAT_PROBE_MIN_Z_M`` over it and skip the
    seat's own surfaces (``_back_hit``); ``back_caster`` (a dressed bed: the bed and its pillows) takes the back rays,
    ``caster`` (everything built) the rays down."""
    w, t, h = (float(v) for v in size)
    backs_caster = caster if back_caster is None else back_caster
    hc, (hw, hd), rot = host_fp["center"], (float(host_fp["size"][0]), float(host_fp["size"][1])), \
        float(host_fp["rotation_deg"])
    lx, _ly = to_local(hc, rot, float(item_center[0]), float(item_center[1]))
    lx = max(-hw / 2.0 + w / 2.0, min(hw / 2.0 - w / 2.0, lx)) if hw > w else 0.0   # on the host, never beside it
    if attempt:
        lx = lx - math.copysign(min(abs(lx), 0.10 * attempt), lx)
    rot_item = rot + float(turn_deg)
    top = host_top(caster) + TOP_ABOVE_M
    back_dir = direction_world(rot, 0.0, 1.0)
    side_dir = direction_world(rot, 1.0, 0.0)
    # 1. the seat in front of the item (the front part of a sofa or the head part of a bed is seat or mattress)
    seat = None
    for share in (BED_SEAT_PROBE_SHARES if bed else SEAT_PROBE_SHARES):   # front to back: an L sofa's corner is empty
        seat_y = -hd / 2.0 + share * hd
        probe = [to_world(hc, rot, lx + k * w / 4.0, seat_y) for k in (0, -1, 1)]
        hits = _down_hits(caster, probe, top)
        zs = [z for z in hits if z is not None]
        if zs:
            seat = hits[0] if hits[0] is not None else sorted(zs)[len(zs) // 2]   # at the item's own x (no arm top)
            break
    if seat is None:
        return None
    how = []
    cy_local = None
    # fix round after P4b (module docstring): a bed's back rays start mid-bed, skip a bulge and run above the mattress
    start, reach = (0.0, hd / 2.0 + 0.2) if bed else (-hd / 2.0 - 0.2, hd + 0.4)
    min_hit = BED_BACK_MIN_HIT_M if bed else 0.0
    # Milestone 13: the back is probed with the centre ray first; when the item is then squeezed between two things
    # narrower than a cushion (the centre ray passed through the gap between the two pillows of a made bed and found
    # the headboard behind them), three rays over the item's width probe again and the nearest hit is the back.
    for probe_xs in ((0,), (0, -1, 1)):
        for _pass in range(2):
            backs = []
            for f in BACK_PROBE_SHARES:
                s = f * h
                _yb, zb = back_face_offset(t, s, lean_deg)
                z = seat + max(zb, BED_PROBE_MIN_Z_M if bed else SEAT_PROBE_MIN_Z_M)
                dists = []
                for k in probe_xs:
                    ox, oy = to_world(hc, rot, lx + k * w / 4.0, start)
                    dist = _back_hit(backs_caster, (ox, oy, z), (back_dir[0], back_dir[1], 0.0), reach, min_hit,
                                     None if bed else seat, top)
                    if dist is None or (k and start + dist <= seat_y):
                        continue              # a side ray stopped in front of the seat (an arm) is not a back
                    dists.append(dist)
                if dists:
                    backs.append((start + min(dists), s))
            if backs:
                cy_local = min(yb - back_face_offset(t, s, lean_deg)[0] for yb, s in backs)
                what = "the backrest found by horizontal rays"
                if len(probe_xs) > 1:
                    what += " (the nearest of three over the item's width: the centre ray passed between two things)"
            if bed and backs and cy_local < max(0.0, hd / 2.0 - BED_HEAD_ZONE_M):
                backs = []                    # P4b / 27 Oct 2026: a "headboard" that leaves the item out of the head zone
            if not backs:
                cy_local = hd / 2.0 - back_face_offset(t, h * 0.5, lean_deg)[0]
                what = "no backrest hit: against the footprint's back edge (the wall)"
            # the seat under the item's spot (soft: median of the grid over its middle: never an arm's top)
            foot = (min(w * 0.5, 0.2), max(t, 0.05))
            sup = support_height(caster, to_world(hc, rot, lx, cy_local - t * 0.25), foot, rot_item, True, top)
            if sup["z"] is not None:
                seat = sup["z"]
            how = [what]
        # 2. arms: rays to both sides at two heights of the item (the nearest hit counts)
        cxw, cyw = to_world(hc, rot, lx, cy_local)
        right = left = None
        for f in ARM_PROBE_SHARES:
            z = seat + max(0.02, h * f * math.cos(math.radians(lean_deg)))
            r_hit = _horizontal(caster, (cxw, cyw, z), (side_dir[0], side_dir[1], 0.0), hw)
            l_hit = _horizontal(caster, (cxw, cyw, z), (-side_dir[0], -side_dir[1], 0.0), hw)
            right = r_hit if right is None or (r_hit is not None and r_hit < right) else right
            left = l_hit if left is None or (l_hit is not None and l_hit < left) else left
        room_r = (right if right is not None else hw / 2.0 - lx) - ARM_GAP_M
        room_l = (left if left is not None else hw / 2.0 + lx) - ARM_GAP_M
        if room_l + room_r >= MIN_CUSHION_W or len(probe_xs) > 1:
            break
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
    limit = REST_TOLERANCES["decor_pen_soft_m" if soft else "decor_pen_hard_m"] if pen_limit is None else pen_limit
    item = MeshCaster(item_verts, item_faces)
    lo_z = float(item.lo[2]) - 1.0
    top = host_top(host_caster) + TOP_ABOVE_M
    gaps, with_under, supported = [], 0, 0
    lowest = min(item_verts, key=lambda v: (float(v[2]), float(v[0]), float(v[1])))
    below_lowest = [h[1][2] for h in host_caster.hits((float(lowest[0]), float(lowest[1]), top), (0.0, 0.0, -1.0))
                    if h[1][2] <= float(lowest[2]) + limit + 0.02]
    if below_lowest:                              # the touching point of a rounded or leaning item
        gaps.append(float(lowest[2]) - max(below_lowest))
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


def measure_back(item_verts, item_faces, host_caster, footprint: dict, wall: Optional[dict] = None) -> dict:
    """How a leaning item (a cushion on a back or a headboard) touches its back (28 Oct 2026, module docstring; pure):
    horizontal rays along the back direction of ``footprint`` (its ``rotation_deg``: local +Y) at
    ``BACK_CONTACT_SHARES`` of the item's height and ``BACK_CONTACT_XS`` of its width (``footprint.size[0]``) from
    ``BACK_RAY_FROM_M`` in front of its base centre: the item's last hit (its back surface) and the host's first hit
    after the item's front; ``back_gap_m`` = the smallest host - back distance (negative: pressed into it), None when
    nothing of the host is within ``BACK_REACH_M`` behind any of them. ``wall`` (the host's footprint): with no host
    hit, the footprint's back edge (local y = depth / 2: the wall a piece stands against) is the back (``back`` says
    which)."""
    item = MeshCaster(item_verts, item_faces)
    z0, z1 = float(item.lo[2]), float(item.hi[2])
    rot = float(footprint.get("rotation_deg") or 0.0)
    cx, cy = (float(v) for v in footprint["center"][:2])
    w = float(footprint["size"][0])
    bx, by = direction_world(rot, 0.0, 1.0)
    host_gaps, wall_gaps, probes = [], [], 0
    for share in BACK_CONTACT_SHARES:
        z = z0 + share * (z1 - z0)
        for k in BACK_CONTACT_XS:
            ox, oy = to_world((cx, cy), rot, k * w, -BACK_RAY_FROM_M)
            origin = (ox, oy, z)
            on_item = item.hits(origin, (bx, by, 0.0), 2.0 * BACK_RAY_FROM_M + 1.0)
            if not on_item:
                continue
            probes += 1
            t_front, t_back = float(on_item[0][0]), float(on_item[-1][0])
            hit = next((float(t) for t, _p, _n in host_caster.hits(origin, (bx, by, 0.0), t_back + BACK_REACH_M)
                        if float(t) >= t_front - 1e-9), None)
            if hit is not None:
                host_gaps.append(hit - t_back)
                continue
            if wall is not None:
                wrot = float(wall.get("rotation_deg") or 0.0)
                _lx, ly = to_local(wall["center"], wrot, ox, oy)
                _dx, dy = to_local((0.0, 0.0), wrot, bx, by)
                if dy > 1e-6:
                    t_wall = (float(wall["size"][1]) / 2.0 - ly) / dy
                    if t_front - 1e-9 <= t_wall <= t_back + BACK_REACH_M:
                        wall_gaps.append(t_wall - t_back)
    gaps = host_gaps or wall_gaps
    return {"back_gap_m": round(min(gaps), 4) if gaps else None,
            "back": ("host" if host_gaps else "wall (the host footprint's back edge)") if gaps else None,
            "back_probes": probes}


def settle_back(item_verts, item_faces, back_caster, footprint: dict, seat_z: Optional[float], top_z: float,
                min_z: float) -> Optional[float]:
    """How far a leaning item moves along its back direction until its real back surface first meets its back (28 Oct
    2026, module docstring; pure): rays at ``SETTLE_SHARES`` of its height (never under ``min_z``: the seat's own
    surface) and ``SETTLE_XS`` of its width, each the back caster's first back hit (``_back_hit``: with ``seat_z`` a
    seat's own surfaces are skipped) after the item's front minus the item's back; the smallest (positive: move back,
    negative: forward out of it), None when nothing is behind. ``place_leaning`` aims a box's back face; a round
    cushion's bulge or a lying pillow's rounded end meets it elsewhere."""
    item = MeshCaster(item_verts, item_faces)
    z0, z1 = float(item.lo[2]), float(item.hi[2])
    rot = float(footprint.get("rotation_deg") or 0.0)
    cx, cy = (float(v) for v in footprint["center"][:2])
    w = float(footprint["size"][0])
    bx, by = direction_world(rot, 0.0, 1.0)
    best = None
    for share in SETTLE_SHARES:
        z = z0 + share * (z1 - z0)
        if z < min_z:
            continue
        for k in SETTLE_XS:
            ox, oy = to_world((cx, cy), rot, k * w, -BACK_RAY_FROM_M)
            origin = (ox, oy, z)
            on_item = item.hits(origin, (bx, by, 0.0), 2.0 * BACK_RAY_FROM_M + 1.0)
            if not on_item:
                continue
            t_front, t_back = float(on_item[0][0]), float(on_item[-1][0])
            hit = _back_hit(back_caster, origin, (bx, by, 0.0), t_back + BACK_REACH_M, t_front - 1e-9, seat_z, top_z)
            if hit is not None:
                best = hit - t_back if best is None else min(best, hit - t_back)
    return best


def longest_edge(verts, faces) -> float:
    """The longest edge of a mesh (pure; 28 Oct 2026): a draped cloth's neighbouring points stay a grid step apart."""
    arr = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    best = 0.0
    for f in faces or ():
        for a, b in zip(f, list(f[1:]) + [f[0]]):
            best = max(best, float(np.linalg.norm(arr[int(a)] - arr[int(b)])))
    return best


def measure_cloth(item_verts, item_faces, host_caster, footprint: dict, n: int = CLOTH_POKE_GRID) -> dict:
    """How a cloth (a throw) lies on its host (28 Oct 2026, user on real04's f_L0_021: "I did not like this bed"; pure):
    ``poke_m`` = the most the host's surface stands above the cloth's top over an ``n`` x ``n`` grid of rays down
    across ``footprint`` (its part on the top; positive: the host pokes through the cloth there, e.g. the folds of a
    model's own bedding between the 5 cm drape grid), None when no ray meets both; ``cloth_edge_m`` = the cloth's
    longest edge (a torn drape: a grid point thrown off its cell)."""
    item = MeshCaster(item_verts, item_faces)
    top = max(host_top(host_caster), float(item.hi[2])) + TOP_ABOVE_M
    worst = None
    for x, y in grid_points(footprint["center"], footprint["size"], float(footprint.get("rotation_deg") or 0.0), n=n,
                            spread=0.5):
        on_cloth = item.ray((x, y, top), (0.0, 0.0, -1.0))
        on_host = host_caster.ray((x, y, top), (0.0, 0.0, -1.0))
        if on_cloth is None or on_host is None:
            continue
        poke = float(on_host[1][2]) - float(on_cloth[1][2])
        worst = poke if worst is None else max(worst, poke)
    return {"poke_m": None if worst is None else round(worst, 4),
            "cloth_edge_m": round(longest_edge(item_verts, item_faces), 4)}


def rest_ok(m: dict) -> tuple[bool, list[str]]:
    """Whether an S5 measurement passes the tolerances (``REST_TOLERANCES`` = ``scene_checks.TOLERANCES``) and why
    not. 28 Oct 2026: a leaning item's ``back_gap_m`` (``measure_back``; the key present and None: nothing behind
    it), a cloth's ``poke_m`` and ``cloth_edge_m`` (``measure_cloth``)."""
    tol = REST_TOLERANCES
    why = []
    if m.get("gap_m") is None:
        why.append("no host surface under the item")
    elif m["gap_m"] > tol["decor_gap_m"] + 1e-9:
        why.append(f"gap {m['gap_m']:.3f} m > {tol['decor_gap_m']} m")
    limit = tol["decor_pen_cloth_m"] if m.get("cloth") else \
        tol["decor_pen_soft_m"] if m.get("soft") else tol["decor_pen_hard_m"]
    if m.get("penetration_m", 0.0) > limit + 1e-9:
        why.append(f"penetration {m['penetration_m']:.3f} m > {limit} m")
    if m.get("support_share", 0.0) < tol["decor_support_share"] - 1e-9:
        why.append(f"{m.get('support_share', 0.0):.0%} of the footprint over the support < "
                   f"{tol['decor_support_share']:.0%}")
    if "back_gap_m" in m:
        if m["back_gap_m"] is None:
            why.append("nothing behind its upper part: it stands free instead of leaning on its back")
        elif m["back_gap_m"] > tol["decor_back_gap_m"] + 1e-9:
            why.append(f"gap {m['back_gap_m']:.3f} m behind its upper part > {tol['decor_back_gap_m']} m: it does not "
                       "lean on its back")
    if m.get("poke_m") is not None and m["poke_m"] > tol["decor_cloth_poke_m"] + 1e-9:
        why.append(f"the host pokes {m['poke_m']:.3f} m through the cloth")
    if m.get("cloth_edge_m") is not None and m["cloth_edge_m"] > tol["decor_cloth_edge_m"] + 1e-9:
        why.append(f"the cloth tears ({m['cloth_edge_m']:.2f} m between two neighbouring points > "
                   f"{tol['decor_cloth_edge_m']} m: the top under it is not one surface)")
    return (not why), why


def floor_rest(item_verts, floor_z: float) -> dict:
    """S5 for an item on the floor (a rug, a floor plant): its lowest point above the floor."""
    low = min(float(v[2]) for v in item_verts)
    return {"gap_m": round(low - float(floor_z), 4), "penetration_m": round(max(0.0, float(floor_z) - low), 4),
            "support_share": 1.0, "grid_points": 0, "soft": False}


# --------------------------------------------------------------------------
# One decor item: place, build, measure, place once more, or not build (§4.7)
# --------------------------------------------------------------------------

def own_cushions(host: dict) -> bool:
    """Whether a seat's or bed's model already has its cushions (the audit's ``has_cushions`` on a seat,
    ``has_pillows`` / ``has_cushions`` on a bed; pure): decor cushions on it would lie on top of them (25 Oct 2026:
    the decor stage judged the provisional model, the build the final one)."""
    asset = host.get("asset") if isinstance(host.get("asset"), dict) else {}
    if host.get("type") in BED_HOSTS:
        return asset.get("has_pillows") is True or asset.get("has_cushions") is True
    return asset.get("has_cushions") is True


def own_bedding(host: dict) -> bool:
    """Whether a bed's model is already made up with its own duvet or cover (the audit's ``has_bedding``; pure; 28 Oct
    2026, user on real04's f_L0_021: "I did not like this bed"): a decor throw over it lies on modelled cloth folds the
    5 cm drape cannot follow (the model's grey blanket poked through the cream throw and the drape tore), so it gets
    none (``decor.takes_throw``; the build skips one the final model makes wrong)."""
    asset = host.get("asset") if isinstance(host.get("asset"), dict) else {}
    return host.get("type") in BED_HOSTS and asset.get("has_bedding") is True


def lean_steps(support: str, lean_deg: float = 0.0) -> list[float]:
    """The leans a cushion on a back or a headboard is tried at (28 Oct 2026, module docstring; pure): at least the
    styled lean (``HEADBOARD_LEAN_DEG`` / ``LEAN_DEG``; the host frame's ``lean_deg`` when larger), then steeper
    (``LEAN_STEEPER_DEG``: nothing behind its upper part, it falls back onto what is there), then the smaller
    fallbacks (``LEAN_FALLBACK_DEG`` and the frame's own lean: an upright back leaves no room for the full lean)."""
    styled = HEADBOARD_LEAN_DEG if support == "headboard" else LEAN_DEG
    first = max(float(lean_deg or 0.0), styled)
    steeper = [a for a in LEAN_STEEPER_DEG if a > first + 1e-9]
    smaller = sorted({float(a) for a in (styled,) + LEAN_STEEPER_DEG + LEAN_FALLBACK_DEG
                      + ((float(lean_deg),) if lean_deg else ()) if float(a) < first - 1e-9}, reverse=True)
    return [first] + steeper + smaller


SOFT_DECOR: tuple[str, ...] = ("cushion", "throw")      # the median of the ray grid, not the highest hit
SOFT_HOST_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bed_single",
                                    "bed_double", "bunk_bed", "crib")
SOFT_SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard")
ATTEMPTS = 2                      # placed, then placed once more, then not built (``decor_not_rested``)


def place_item(support: str, caster, host_fp: dict, center, size, rotation_deg: float, soft_item: bool,
               lean_deg: float = 0.0, shelf: Optional[int] = None, attempt: int = 0,
               back_caster=None) -> Optional[dict]:
    """The pose of an item on its support (``host_frame.support``): leaning on a back or a headboard, on a shelf
    board, or lying on a top, a seat or a mattress; None when the host offers no support there. Fix round after
    P4b: a ``headboard`` is searched in the bed's head half (``place_leaning(bed=True)``). 28 Oct 2026:
    ``back_caster`` takes the back rays of a leaning item (a dressed bed: the bed and its pillows)."""
    if support in ("back", "headboard"):
        return place_leaning(caster, host_fp, center, size,
                             lean_deg or (HEADBOARD_LEAN_DEG if support == "headboard" else LEAN_DEG),
                             turn_deg=float(rotation_deg) - float(host_fp["rotation_deg"]), attempt=attempt,
                             bed=support == "headboard", back_caster=back_caster)
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
               lean_deg: float = 0.0, shelf: Optional[int] = None, attempts: int = ATTEMPTS,
               back_caster=None) -> dict:
    """Place one hosted decor item on the built host (``caster``) and check it (S5, §4.7).

    ``local_verts`` / ``local_faces``: the item's mesh in its own frame (bottom on z = 0, centred, front -Y): a
    parametric or textile part, or a library model fitted to its box. Returns ``{"verts", "faces", "pose",
    "rest", "footprint", "attempt"}`` (world vertices that pass S5) or ``{"not_rested": {id, type, host_id,
    support, reason, measured, attempts}}`` after ``attempts`` placements (the second one moves the spot).

    28 Oct 2026 (module docstring): an item on a back or a headboard is tried at the leans of ``lean_steps`` (the
    host frame's ``lean_deg`` is the least, never the only one), slid onto its back (``settle_back``, at most
    ``BACK_SLIDE_MAX_M``) and measured behind too (``measure_back``: it leans on its back in its upper part).
    ``back_caster``: what its back rays see (None: ``caster``), or several in order (a dressed bed: the bed alone, so
    the cushion stands on the pillows against the headboard, then the bed and its pillows, so it leans on them);
    ``caster`` (everything built) gives its seat and S5."""
    w, d, h = local_bounds(local_verts)
    fp = host["footprint"]
    host_fp = {"center": [float(fp["center"][0]), float(fp["center"][1])], "size": [float(v) for v in fp["size"][:2]],
               "rotation_deg": float(fp["rotation_deg"])}
    soft_item = item.get("type") in SOFT_DECOR
    soft_host = host.get("type") in SOFT_HOST_TYPES and support in SOFT_SUPPORTS
    leaning = support in ("back", "headboard")
    rot = float(item.get("rotation_deg") if item.get("rotation_deg") is not None else host_fp["rotation_deg"])
    if leaning:
        rot = host_fp["rotation_deg"]                    # a cushion faces the seat's front (B3 left turned items)
    center = item.get("center") or host_fp["center"]
    last = {"reason": "no support under the item", "measured": None}
    leans = lean_steps(support, lean_deg) if leaning else [lean_deg]
    backs = [b for b in (back_caster if isinstance(back_caster, (list, tuple)) else [back_caster])
             if b is not None] or [caster]
    bx, by = direction_world(host_fp["rotation_deg"], 0.0, 1.0)
    top = host_top(caster) + TOP_ABOVE_M
    bed = support == "headboard"
    sink = SOFT_SINK_M if (soft_item and soft_host and item.get("type") == "cushion") else 0.0

    def settled(p: dict, verts_, back) -> dict:
        """The pose slid along the back direction until the item's real back meets its back (``settle_back``),
        at most ``BACK_SLIDE_MAX_M``, and seated again on what is under its new spot (soft: the median)."""
        seat = float(p.get("seat_z", float(p["z"]) + sink))
        foot_ = {"center": list(p["center"]), "size": [p["size"][0], d], "rotation_deg": p["rotation_deg"]}
        delta = settle_back(pose_vertices(verts_, p), local_faces, back, foot_, None if bed else seat, top,
                            seat + (BED_PROBE_MIN_Z_M if bed else SEAT_PROBE_MIN_Z_M))
        if delta is None or abs(delta) > BACK_SLIDE_MAX_M + 1e-9 or abs(delta - BACK_PRESS_M) < 1e-4:
            return p
        move = delta - BACK_PRESS_M
        cx, cy = float(p["center"][0]) + bx * move, float(p["center"][1]) + by * move
        under = support_height(caster, (cx - bx * d * 0.25, cy - by * d * 0.25),
                               (min(float(p["size"][0]) * 0.5, 0.2), max(d, 0.05)), p["rotation_deg"], True, top)
        z = float(p["z"]) if under["z"] is None else float(under["z"]) - sink
        return dict(p, center=[cx, cy], z=z, seat_z=z + sink, settled_m=round(move, 4),
                    how=f"{p.get('how')}; slid {move:+.3f} m onto its back")

    def measured(p: dict, verts_) -> tuple:
        world_ = pose_vertices(verts_, p)
        foot_ = {"center": list(p["center"]), "size": [p["size"][0], d], "rotation_deg": p["rotation_deg"]}
        m_ = measure_rest(world_, local_faces, caster, foot_, soft_host)
        if leaning:
            m_.update(measure_back(world_, local_faces, caster, foot_, wall=host_fp))
        return world_, foot_, m_

    first_why = None
    for attempt in range(attempts):
        for back in backs:
            for lean in leans:
                pose = place_item(support, caster, host_fp, center, (w, d, h), rot, soft_item, lean, shelf, attempt,
                                  back_caster=back)
                if pose is None:
                    last = {"reason": f"no {support} found on the built host (attempt {attempt + 1})",
                            "measured": None}
                    break
                if sink:
                    pose = dict(pose, z=float(pose["z"]) - sink, sink_m=sink)        # into the soft seat
                verts = local_verts
                if pose["size"][0] < w - 1e-9:                       # narrowed between the arms
                    k = pose["size"][0] / w
                    verts = [(x * k, y, z) for x, y, z in local_verts]
                if leaning:
                    pose = settled(pose, verts, back)
                world, foot, m = measured(pose, verts)
                ok, why = rest_ok(m)
                if ok:
                    return {"verts": world, "faces": [list(f) for f in local_faces], "pose": pose, "rest": m,
                            "footprint": foot, "attempt": attempt + 1}
                if first_why is None:
                    first_why = (f"at {lean:g} degrees: " if leaning else "") + "; ".join(why)
                last = {"reason": "; ".join(why), "measured": m}
    reason = last["reason"]
    if leaning and first_why is not None:
        reason = f"{first_why} (leans {', '.join(f'{a:g}' for a in leans)} degrees tried; last: {last['reason']})"
    return {"not_rested": {"id": item.get("id"), "type": item.get("type"), "host_id": host.get("id"),
                           "support": support, "reason": reason, "measured": last["measured"],
                           "attempts": attempts}}


def plan_throw(item: dict, host: dict, caster, floor_z: float) -> dict:
    """A throw draped on its host (``textiles.throw_parts``) and checked (S5 over its rectangle on the top). 28 Oct
    2026 (user on real04's f_L0_021: "I did not like this bed"): also ``measure_cloth`` (the host poking through the
    cloth, a torn drape); the cream throw over that bed model's own bedding was 1.35 m deep for a 0.5 m cloth (grid
    points over its folds were taken for points hanging over an edge and thrown by the side ray)."""
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
    # 27 Oct 2026: a cloth is measured with its own tolerance (``decor_pen_cloth_m``): a host that shows through it is
    # no rest (the throw is not built and the decor stage's not-rested record names it). 28 Oct 2026: also where the
    # host's surface stands above the cloth between its grid points, and a torn drape (``measure_cloth``)
    m = dict(measure_rest(part["verts"], part["faces"], caster, foot, soft), cloth=True)
    m.update(measure_cloth(part["verts"], part["faces"], caster, foot))
    ok, why = rest_ok(m)
    if not ok:
        shows = any(w.startswith("penetration") or w.startswith("the host pokes") for w in why)
        return {"not_rested": {"id": item.get("id"), "type": "throw", "host_id": host.get("id"), "support": "drape",
                               "reason": "; ".join(why) + ("; the host shows through the cloth" if shows else ""),
                               "measured": m, "attempts": 1}}
    # 29 Oct 2026 (UL106): a layered throw's second blanket lies on the first (textiles.layered_runner); S5 measured the
    # first, the built mesh holds both (one face list per part, in the order of ``parts``)
    verts, faces = list(part["verts"]), [list(f) for f in part["faces"]]
    for extra in got["parts"][1:]:
        off = len(verts)
        verts.extend(extra["verts"])
        faces.extend([[i + off for i in f] for f in extra["faces"]])
    return {"verts": verts, "faces": faces, "parts": got["parts"], "rest": m, "footprint": foot,
            "attempt": 1, "pose": {"how": "draped on the host (shrinkwrap, 5 mm)", "share": got["drape"]["share"]},
            **({"runner": got["runner"]} if got.get("runner") else {}),
            # 29 Oct 2026 (UL121): the woven pair's record (pattern, fringe strands)
            **({"weave": got["weave"]} if got.get("weave") else {})}


Placer = Callable[..., Optional[dict]]
