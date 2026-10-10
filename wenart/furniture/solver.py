"""The deterministic group solver (docs/milestone12.md §4.4, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026); deterministic (same input, same output: no random, no wall clock), pure:

- ``solve_room(building: dict, room_id: str, program: dict | None = None, *, k: int = 3,
  fixed_ids: list[str] | None = None) -> list[Candidate]`` (best first, at most ``k``). ``program`` defaults to
  ``program.room_program(building, room_id)``; ``fixed_ids``: pieces that must not move (drawn pieces always are).
  ``Candidate = {"rank": int, "score": float, "terms": {name: float}, "pieces": [furniture dicts, added_by_ai],
  "groups": [{"group_id", "group", "anchor_id", "member_ids"}], "hard_failures": [], "group_violations":
  [Violation]}``.
- ``apply_candidate(building: dict, room_id: str, candidate: dict) -> dict``: a new building with the room's
  ``added_by_ai`` pieces replaced by the candidate's pieces (drawn pieces untouched), each piece carrying
  ``group = {"group_id", "group", "role": "anchor" | "partner"}``.

Extra candidate keys: ``options`` ({group_id: option}), ``placed`` / ``not_placed`` (group ids, the latter with the
reason), ``kept_ids`` (the fixed added pieces ``apply_candidate`` keeps), ``nodes`` (search effort). Each piece's
``group`` also names the group's ``anchor_id`` (a drawn anchor's id for the partners of a completed group).

What and why: the layout and the completion placed single pieces from model coordinates and repaired them one by
one (§1.2). Here whole groups (``groups.yaml``) are placed by code; the vision model only picks among the top
candidates (``layout.py``).

How (one room):

1. **Free space** (``Space``): the room on a 5 cm raster in its own axis frame (``group_checks.RoomRaster``), minus
   the fixed pieces (drawn pieces, built or not, unless recorded as not furniture; ``fixed_ids``), the door approach
   strips and swings, and, per piece height, the window bands (sill + 0.05 m; a TV unit counts with its TV, a hob
   never stands in a window band). Use zones may cover door swings but never fixed pieces or the outside. Pieces and
   zones are boxes in their own frame; their raster cells come from arithmetic (no geometry objects) and are tested
   with integral images in O(1); the exact shapely tests run once per kept group candidate.
2. **Group candidates**: wall anchors on every outline segment every 0.10 m from both ends (both chaise sides of a
   corner sofa); free anchors on a 0.10 m grid turned to the room's axes; anchors are tried best pre-score first,
   one per 0.5 m first, until ``PER_LEVEL`` x 3 candidates are found. Partners stand at their template places
   (``groups.yaml`` ``place``: a TV unit on the wall the sofa faces, centred on its axis within 0.30 m, ≥ 1.50 m
   away; the coffee table at the recommended gap first; armchairs beside the coffee table facing it; nightstands at
   the head; chairs around the table by its length, a long side without chairs only where the table touches a wall;
   ...); a required partner that does not fit drops the candidate, an optional one is left out. Sets (bathroom, WC,
   entrance) place each member on a wall as its own search level; kitchen runs lay fridge - sink - hob along an I,
   L or U path or a galley with the NKBA landings and work-triangle legs as hard limits. Drawn anchors are not moved:
   their group gets only its missing partners.
3. **Soft terms** per candidate (0..1, weights in ``groups.yaml``; names after Merrell et al. 2011 and Yu et al.
   2011): wall_use, sight_tv, bed_sees_door, desk_side_light, daylight, related_near, recommended, partners,
   drawn_distance, sink_window; per full layout circulation, seating_crossed and balance.
4. **Beam search** (``BEAM_WIDTH`` 32) over the groups in priority order (drawn anchors first); per node every kept
   candidate of the level is tried (overlap and use zones against the node's pieces on the raster, exact shapely
   tests where two pieces come within 5 cm), then the walkways are checked on the raster (every door reaches every
   door at ≥ 0.60 m and the entrance door every door at ≥ 0.80 m where the room with its fixed pieces allows it;
   every use zone reached at ≥ 0.60 m). A group that fits nowhere may be skipped (a placed required group scores
   ``REQUIRED_BONUS``, an optional one ``OPTIONAL_BONUS``). At most ``PER_PARENT`` children per node in a first pass
   (the beam keeps different earlier choices); ties break by score, then the rounded positions; near-duplicates
   (same option and turn, anchor within 0.5 m) are merged; ``NODE_BUDGET`` caps the work.
5. **Top k**: the final nodes are scored with the layout terms, verified exactly (``verify``: the placer's geometry
   and the group checks G1–G14 on the room with the new pieces; only violations the fixed pieces alone do not cause
   count as ``hard_failures``) and returned best first, diverse (the main group differs first, then any group: another
   option or turn, or an anchor ≥ 1 m away).
"""
from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from wenart import geometry as G
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import placer, schemas

BEAM_WIDTH = 32
PER_LEVEL = 40                 # group candidates of one level kept after the free-space checks
PER_PARENT = 4                 # children per beam node in the first pass
ANCHOR_TRIES = 900             # anchor positions tried per group (best pre-score first)
NODE_BUDGET = 60000            # anchor positions generated / candidate expansions per room
GRID_M = 0.10
REQUIRED_BONUS = 10.0
OPTIONAL_BONUS = 3.0
MERGE_M = 0.5                  # same option and turn, anchor within this: one candidate (the better one)
DIVERSE_M = 1.0                # the top k differ by an option, a turn or an anchor this far apart
ZONE_INFLATE_M = 0.02          # use zones are tested 2 cm larger on the raster (sub-cell safety)
CLOSE_M = 0.05                 # pieces closer than this get an exact shapely overlap test
GAP = placer.SNAP_GAP_M        # back edge to wall face
EVIDENCE_FILE = "building.json"
SINK_WINDOW_M = 0.4


# --------------------------------------------------------------------------
# Pieces and boxes
# --------------------------------------------------------------------------

@dataclass
class Spot:
    """One piece of a group candidate (world frame; the block frame of ``schemas``)."""
    type: str
    center: tuple
    rotation: float
    size: tuple
    role: str
    against_wall: bool = False
    shape: Optional[str] = None
    chaise_side: Optional[str] = None
    existing_id: Optional[str] = None          # a drawn (or fixed) piece used as the anchor: not new

    def piece(self) -> placer.Piece:
        extra = {}
        if self.shape == "L":
            extra = {"shape": "L", "chaise_side": self.chaise_side, "chaise_depth": float(self.size[1]),
                     "seat_depth": schemas.L_SEAT_DEPTH_M, "chaise_width": schemas.L_CHAISE_WIDTH_M}
        return placer.Piece(self.type, (float(self.center[0]), float(self.center[1])), float(self.rotation),
                            (float(self.size[0]), float(self.size[1])), self.against_wall, **extra)

    def boxes(self) -> list[tuple]:
        """Its footprint as boxes ``(x0, x1, y0, y1)`` in its own frame (two for a corner sofa)."""
        if self.shape == "L":
            return [tuple(b) for b in schemas.l_parts(self.size, self.chaise_side, float(self.size[1]),
                                                      schemas.L_SEAT_DEPTH_M, schemas.L_CHAISE_WIDTH_M)]
        w, d = float(self.size[0]) / 2.0, float(self.size[1]) / 2.0
        return [(-w, w, -d, d)]

    def zones(self, rec: bool = False) -> list[tuple]:
        """Its use zones ``(name, centre, rotation, box)``."""
        return [(name, self.center, self.rotation, box) for name, box in GC.use_zone_boxes(
            self.size, self.type, self.shape, self.chaise_side, float(self.size[1]), rec)]

    def world(self, local) -> tuple[float, float]:
        r = math.radians(self.rotation)
        c, s = math.cos(r), math.sin(r)
        return (self.center[0] + local[0] * c - local[1] * s, self.center[1] + local[0] * s + local[1] * c)


def _spot_from(f: dict, role: str = "anchor") -> Spot:
    p = placer.drawn_piece(f)
    return Spot(f["type"], p.center, p.rotation_deg, p.size, role, False, p.shape, p.chaise_side, existing_id=f["id"])


def _local_spot(anchor: Spot, ftype: str, local, turn: float, size, role: str, wall: bool = False) -> Spot:
    c = anchor.world(local)
    return Spot(ftype, (round(c[0], 4), round(c[1], 4)), G.normalise_angle(anchor.rotation + turn),
                (float(size[0]), float(size[1])), role, wall)


@dataclass
class Cand:
    """A group candidate: its new spots, use zones (boxes that stay free), soft terms and raster footprints."""
    level: int
    group_id: str
    group: str
    option: str
    anchor: Spot
    spots: list                        # new spots (the anchor first when it is new)
    zones: list                        # [(name, centre, rotation, box)]
    terms: dict
    local: float = 0.0
    sig: tuple = ()
    fps: list = field(default_factory=list)
    zfps: list = field(default_factory=list)
    rfps: list = field(default_factory=list)       # the zones a person walks into (reached by a walkway)
    polys: list = field(default_factory=list)
    bboxes: list = field(default_factory=list)


def _reached(zone) -> bool:
    """A use zone a person walks into (a side clearance beside a toilet or washbasin, a sofa's view of its TV and a
    drawn table's pull-out room are kept free, not walked into)."""
    return not str(zone[0]).startswith(("side_", "sight", "pullout_drawn"))


# --------------------------------------------------------------------------
# Free space
# --------------------------------------------------------------------------

def _integral(mask: np.ndarray) -> np.ndarray:
    s = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), dtype=np.int32)
    s[1:, 1:] = mask.astype(np.int32).cumsum(0).cumsum(1)
    return s


class Layer:
    """A blocked-cell mask with its integral image."""

    def __init__(self, mask: np.ndarray):
        self.mask = mask
        self.s = _integral(mask)

    def hit(self, fp) -> bool:
        if fp[0] == "r":
            _k, j0, j1, i0, i1 = fp
            if j1 <= j0 or i1 <= i0:
                return True
            s = self.s
            return int(s[j1, i1] - s[j0, i1] - s[j1, i0] + s[j0, i0]) > 0
        idx = fp[1]
        return idx.size == 0 or bool(self.mask.ravel()[idx].any())


def paint(mask: np.ndarray, fp) -> None:
    if fp[0] == "r":
        _k, j0, j1, i0, i1 = fp
        if j1 > j0 and i1 > i0:
            mask[j0:j1, i0:i1] = True
    else:
        mask.ravel()[fp[1]] = True


def _close(a, b, m: float = CLOSE_M) -> bool:
    return not (a[2] + m < b[0] or b[2] + m < a[0] or a[3] + m < b[1] or b[3] + m < a[1])


class Space:
    """The room's free space for the solver (see the module docstring, step 1)."""

    def __init__(self, building: dict, room: dict, fixed: list[dict]):
        self.building, self.room = building, room
        self.ctx = placer.room_context(building, room)
        self.R = GC.RoomRaster(self.ctx.polygon)
        R = self.R
        self.fixed_items = fixed
        self.fixed_pieces = []
        for i, f in enumerate(fixed):
            try:
                self.fixed_pieces.append(placer.drawn_piece(f, i))
            except (KeyError, TypeError, ValueError):
                continue
        self.fixed_polys = [p.polygon() for p in self.fixed_pieces]
        self.fixed_bounds = [p.bounds for p in self.fixed_polys]
        self.shrunk_tol = self.ctx.shrunk.buffer(1e-3, join_style="mitre")
        fixed_mask = np.zeros_like(R.inside)
        for poly in self.fixed_polys:
            fixed_mask |= R.polygon_mask(poly)
        self.fixed_mask = fixed_mask
        door_mask = np.zeros_like(R.inside)
        for door in self.ctx.doors:
            for geom in (door.zone, door.swing):
                if geom is not None and not geom.is_empty:
                    door_mask |= R.polygon_mask(geom)
        self.door_mask = door_mask
        self.inside_shrunk = R.polygon_mask(self.ctx.shrunk)
        self.windows = [(w, R.polygon_mask(w.band)) for w in self.ctx.windows]
        self.base = ~self.inside_shrunk | fixed_mask | door_mask
        self.zone_layer = Layer(~R.inside | fixed_mask)
        self._layers: dict = {}
        self.area = float(room.get("area_computed") or self.ctx.polygon.area)
        self.centroid = (self.ctx.polygon.centroid.x, self.ctx.polygon.centroid.y)
        self.doors_by_id = {d["id"]: d for d in placer.room_openings(building, room)[0]}
        self._allowed_room = GC.allowed_types_at(building, dict(room, zones=[]), None)
        self._zones = [(Polygon(z["polygon"]).buffer(0.05), GC.allowed_types_at(building, dict(room, zones=[z]), None))
                       for z in room.get("zones") or [] if len(z.get("polygon") or []) >= 3]
        self.margin = GR.rule("window_band")["sill_margin"]

    # ----- what may stand where -------------------------------------------------------------------------------------

    def allowed(self, ftype: str, point) -> bool:
        """``group_checks.allowed_types_at`` (cached): the room's types, plus a zone's types at a point inside it
        (anywhere in a zone when ``point`` is None)."""
        if ftype in self._allowed_room:
            return True
        for poly, types in self._zones:
            if ftype in types and (point is None or poly.contains(Point(point))):
                return True
        return False

    def layer_for(self, ftype: str) -> Layer:
        """Blocked cells for a piece of ``ftype``: outside, fixed, doors, and the window bands its height reaches."""
        h = GC.effective_height({"type": ftype})
        key = (round(h, 3), ftype == "stove")
        if key not in self._layers:
            mask = self.base.copy()
            for win, band in self.windows:
                if ftype == "stove" or h > win.sill + self.margin + 1e-9:
                    mask |= band
            self._layers[key] = Layer(mask)
        return self._layers[key]

    def exact_ok(self, spot: Spot, poly: Polygon) -> bool:
        """The exact (shapely) tests the 5 cm raster may miss by less than a cell: inside the room shrunk by 2 cm, off
        every fixed piece, door strip and swing, and (for its height) off every window band."""
        if not self.shrunk_tol.contains(poly):
            return False
        b = poly.bounds
        for q, qb in zip(self.fixed_polys, self.fixed_bounds):
            if _close(b, qb, 0.0) and poly.intersection(q).area > placer.AREA_EPS:
                return False
        for door in self.ctx.doors:
            for geom in (door.zone, door.swing):
                if geom is not None and not geom.is_empty and poly.intersection(geom).area > placer.AREA_EPS:
                    return False
        h = GC.effective_height({"type": spot.type})
        for win, _band in self.windows:
            if (spot.type == "stove" or h > win.sill + self.margin + 1e-9) and \
                    poly.intersection(win.band).area > placer.AREA_EPS:
                return False
        return True

    # ----- raster footprints ---------------------------------------------------------------------------------------

    def _rect(self, X0: float, X1: float, Y0: float, Y1: float):
        R = self.R
        i0 = int(math.ceil((X0 - R.x0) / R.res - 0.5 - 1e-9))
        i1 = int(math.floor((X1 - R.x0) / R.res - 0.5 + 1e-9)) + 1
        j0 = int(math.ceil((Y0 - R.y0) / R.res - 0.5 - 1e-9))
        j1 = int(math.floor((Y1 - R.y0) / R.res - 0.5 + 1e-9)) + 1
        if i1 <= i0:                           # thinner than a cell: the cell under its centre line
            i0 = int(math.floor(((X0 + X1) / 2.0 - R.x0) / R.res))
            i1 = i0 + 1
        if j1 <= j0:
            j0 = int(math.floor(((Y0 + Y1) / 2.0 - R.y0) / R.res))
            j1 = j0 + 1
        if i0 < 0 or j0 < 0 or i1 > R.nx or j1 > R.ny:
            return ("r", 0, 0, 0, 0)           # leaves the raster: outside the room
        return ("r", j0, j1, i0, i1)

    def box_fp(self, center, rotation: float, box, inflate: float = 0.0):
        """Raster cells of a box ``(x0, x1, y0, y1)`` in the frame (``center``, ``rotation``): a rectangle of cells
        when it lies along the raster axes (arithmetic only), else the cells of its polygon."""
        x0, x1, y0, y1 = box[0] - inflate, box[1] + inflate, box[2] - inflate, box[3] + inflate
        R = self.R
        phi = (float(rotation) - R.angle) % 360.0
        q = int(round(phi / 90.0))
        if abs(phi - 90.0 * q) < 0.5:
            CX, CY = R.local(center)
            q %= 4
            if q == 0:
                return self._rect(CX + x0, CX + x1, CY + y0, CY + y1)
            if q == 1:
                return self._rect(CX - y1, CX - y0, CY + x0, CY + x1)
            if q == 2:
                return self._rect(CX - x1, CX - x0, CY - y1, CY - y0)
            return self._rect(CX + y0, CX + y1, CY - x1, CY - x0)
        poly = placer._local_box(center, rotation, x0, x1, y0, y1)
        return ("m", np.flatnonzero(R.polygon_mask(poly)))

    def spot_fps(self, spot: Spot) -> list:
        return [self.box_fp(spot.center, spot.rotation, b) for b in spot.boxes()]

    def zone_fp(self, zone, inflate: float = ZONE_INFLATE_M):
        _name, center, rotation, box = zone
        return self.box_fp(center, rotation, box, inflate)

    def rect_idx(self, fp) -> np.ndarray:
        _k, j0, j1, i0, i1 = fp
        if j1 <= j0 or i1 <= i0:
            return np.zeros(0, dtype=np.int64)
        jj, ii = np.meshgrid(np.arange(j0, j1), np.arange(i0, i1), indexing="ij")
        return (jj * self.R.nx + ii).ravel()

    def overlap(self, a, b) -> bool:
        if a[0] == "r" and b[0] == "r":
            return a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]
        ia = a[1] if a[0] == "m" else self.rect_idx(a)
        ib = b[1] if b[0] == "m" else self.rect_idx(b)
        return bool(np.intersect1d(ia, ib).size)

    def spot_free(self, spot: Spot, fps=None) -> bool:
        """The spot's cells are free for its type (raster only)."""
        layer = self.layer_for(spot.type)
        return not any(layer.hit(fp) for fp in (fps or self.spot_fps(spot)))

    def zones_free(self, zones) -> bool:
        return not any(self.zone_layer.hit(self.zone_fp(z)) for z in zones)


# --------------------------------------------------------------------------
# Candidate checks against the free space
# --------------------------------------------------------------------------

def _finish(space: Space, cand: Cand) -> bool:
    """Footprints of the new spots and zones; True when every spot passes its layer and the exact tests, the spots
    do not overlap each other and every zone is inside the room and off the fixed pieces."""
    cand.fps, cand.zfps, cand.rfps, cand.polys, cand.bboxes = [], [], [], [], []
    for s in cand.spots:
        fps = space.spot_fps(s)
        if not space.spot_free(s, fps):
            return False
        poly = s.piece().polygon()
        if not space.exact_ok(s, poly):
            return False
        cand.fps += fps
        cand.polys.append(poly)
        cand.bboxes.append(poly.bounds)
    for i in range(len(cand.spots)):
        for j in range(i + 1, len(cand.spots)):
            if _close(cand.bboxes[i], cand.bboxes[j], 0.0) and \
                    cand.polys[i].intersection(cand.polys[j]).area > placer.AREA_EPS:
                return False
    for z in cand.zones:
        zfp = space.zone_fp(z)
        if space.zone_layer.hit(zfp):
            return False
        cand.zfps.append(zfp)
        if _reached(z):
            cand.rfps.append(zfp)
    return True


def _fits(space: Space, spot: Spot, others: list, zones=()) -> bool:
    """A partner spot on free cells for its type, off the group's other spots (raster), its zones free, its type
    allowed where it stands."""
    fps = space.spot_fps(spot)
    if not space.spot_free(spot, fps):
        return False
    if any(space.overlap(a, b) for a in fps for b in others):
        return False
    if zones and not space.zones_free(zones):
        return False
    return space.allowed(spot.type, spot.center)


# --------------------------------------------------------------------------
# Soft terms of one group candidate
# --------------------------------------------------------------------------

def _term_daylight(space: Space, p) -> float:
    if not space.ctx.windows:
        return 0.0
    d = min(G.distance(p, w.inner_point) for w in space.ctx.windows)
    return round(max(0.0, 1.0 - d / 4.0), 4)


def _term_desk_light(space: Space, desk: Spot) -> float:
    if not space.ctx.windows:
        return 0.3
    front = G.front_direction_deg(desk.rotation)
    best = 0.0
    for w in space.ctx.windows:
        pt = w.inner_point
        ang = G.angle_difference_deg(math.degrees(math.atan2(pt[1] - desk.center[1], pt[0] - desk.center[0])), front)
        best = max(best, 1.0 if 50.0 <= ang <= 130.0 else 0.6 if ang < 50.0 else 0.1)
    return best


def _term_bed_door(space: Space, bed: Spot, entrance: Optional[str]) -> float:
    doors = [d for d in space.ctx.doors if entrance is None or d.id == entrance] or space.ctx.doors
    if not doors:
        return 0.5
    p = bed.piece()
    w, d = p.size[0] / 2.0, p.size[1] / 2.0
    lx, ly = GC.to_local(p, doors[0].inner_point)
    if ly >= d - 0.3:
        return 0.2                                   # behind or beside the headboard: not seen from the bed
    if abs(lx) <= w and ly < -d:
        return 0.6                                   # straight beyond the foot
    return 1.0


def _term_sight(anchor: Spot, tv: Optional[Spot]) -> float:
    if tv is None:
        return 0.0
    geo = GC.tv_geometry(anchor.piece(), tv.piece())
    rule = GR.rule("tv_distance")
    lo, hi = (f * rule["screen_diagonal"] for f in rule["rec_factor"])
    dev = 0.0 if lo <= geo["distance_m"] <= hi else min(abs(geo["distance_m"] - lo), abs(geo["distance_m"] - hi))
    return round(max(0.0, 1.0 - dev) * (1.0 - geo["axis_offset_m"] / 0.6), 4)


def _term_recommended(space: Space, spot: Spot) -> Optional[float]:
    rec = spot.zones(rec=True)
    if not rec:
        return None
    ok = sum(1 for z in rec if not space.zone_layer.hit(space.zone_fp(z, 0.0)))
    return round(ok / len(rec), 4)


def _kitchen_targets(space: Space) -> list:
    """Points the dining group likes to be near: the room's kitchen zones and the doors to kitchens."""
    out = []
    for z in space.room.get("zones") or []:
        if z.get("kind") == "kitchen" and len(z.get("polygon") or []) >= 3:
            c = Polygon(z["polygon"]).centroid
            out.append((c.x, c.y))
    for door in space.ctx.doors:
        op = space.doors_by_id.get(door.id)
        other = GC.other_room_of_door(space.building, space.room, op) if op else None
        if other is not None and other.get("room_type") == "kitchen":
            out.append(door.inner_point)
    if space.room.get("room_type") == "kitchen":
        out.append(space.centroid)
    return out


def _score(terms: dict) -> float:
    w = GR.weights()
    return round(sum(w.get(k, 0.0) * v for k, v in terms.items() if v is not None), 6)


def _align_term(t: float, lo: float, hi: float, align: str) -> float:
    half = max((hi - lo) / 2.0, 0.05)
    if align == "centre":
        return round(max(0.0, 1.0 - abs(t - (lo + hi) / 2.0) / half), 4)
    if align == "corner":
        return round(max(0.0, 1.0 - min(t - lo, hi - t) / half), 4)
    return 0.5


# --------------------------------------------------------------------------
# Anchor positions
# --------------------------------------------------------------------------

def _wall_positions(space: Space, size):
    """``(segment, t, centre, rotation, t_lo, t_hi)``: a back-to-wall footprint of ``size`` on every outline segment
    every 0.10 m from both ends (``t`` along the segment; ``t_lo..t_hi`` the stretch it may slide on)."""
    w, d = float(size[0]), float(size[1])
    for k, (a, b) in enumerate(space.ctx.segments):
        length = G.distance(a, b)
        if length < w + 2 * GAP - 1e-6:
            continue
        n = space.ctx.segment_normal(k)
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        rot = placer._rotation_for_normal(n)
        t_min, t_max = w / 2.0 + GAP, length - w / 2.0 - GAP
        steps = int((t_max - t_min) / GRID_M + 1e-6)
        ts = sorted({round(t_min + i * GRID_M, 3) for i in range(steps + 1)} |
                    {round(t_max - i * GRID_M, 3) for i in range(steps + 1)})
        for t in ts:
            c = (a[0] + u[0] * t + n[0] * (d / 2.0 + GAP), a[1] + u[1] * t + n[1] * (d / 2.0 + GAP))
            yield k, t, (round(c[0], 4), round(c[1], 4)), rot, t_min, t_max


def _free_positions(space: Space, size, turns: tuple = (0.0, 90.0)):
    """``(centre, rotation)`` on a 0.10 m grid of the room's axis frame (only where the centre cell is free)."""
    R = space.R
    w, d = size
    reach = max(w, d) / 2.0
    xs = np.arange(R.x0 + reach, R.x0 + R.nx * R.res - reach + 1e-9, GRID_M)
    ys = np.arange(R.y0 + reach, R.y0 + R.ny * R.res - reach + 1e-9, GRID_M)
    for turn in turns:
        for y in ys:
            for x in xs:
                j, i = int(math.floor((float(y) - R.y0) / R.res)), int(math.floor((float(x) - R.x0) / R.res))
                if not (0 <= j < R.ny and 0 <= i < R.nx) or space.base[j, i]:
                    continue
                c = R.world((float(x), float(y)))
                yield (round(c[0], 4), round(c[1], 4)), G.normalise_angle(R.angle + turn)


def _ordered(items: list[tuple]) -> list[tuple]:
    """``(prescore, bucket, key, payload)`` best first, one per bucket first, then the rest (deterministic)."""
    items = sorted(items, key=lambda x: (-x[0], x[1], x[2]))
    first, rest, seen = [], [], set()
    for it in items:
        (rest if it[1] in seen else first).append(it)
        seen.add(it[1])
    return first + rest


# --------------------------------------------------------------------------
# Partners
# --------------------------------------------------------------------------

def _tv_spots(space: Space, anchor: Spot, sizes, offsets=(0.0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3)) -> list[Spot]:
    """TV units on the wall the sofa faces, centred on its axis (offsets along that wall), facing it; only where
    the TV front is ≥ the minimum viewing distance from the seat front and the wall is square to the axis."""
    a = anchor.piece()
    fx, fy = GC.front_vec(a)
    seat = anchor.world((0.0, -a.size[1] / 2.0))
    if a.shape == "L":
        x0, x1, yf = schemas.l_seat_front(a.size, a.chaise_side, a.chaise_depth, a.seat_depth, a.chaise_width)
        seat = anchor.world(((x0 + x1) / 2.0, yf))
    ray = LineString([seat, (seat[0] + fx * 12.0, seat[1] + fy * 12.0)])
    hit = ray.intersection(space.ctx.ring)
    if hit.is_empty:
        return []
    pts = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point"]
    if not pts:
        return []
    p = min(pts, key=lambda q: Point(seat).distance(q))
    k = space.ctx.nearest_segment((p.x, p.y))
    n = space.ctx.segment_normal(k)
    if G.angle_difference_deg(math.degrees(math.atan2(-n[1], -n[0])), math.degrees(math.atan2(fy, fx))) > 2.0:
        return []                                      # the wall is not square to the sofa's axis
    sa, sb = space.ctx.segments[k]
    seg_len = G.distance(sa, sb)
    u = ((sb[0] - sa[0]) / seg_len, (sb[1] - sa[1]) / seg_len)
    t0 = (p.x - sa[0]) * u[0] + (p.y - sa[1]) * u[1]
    rot = placer._rotation_for_normal(n)
    tv_min = GR.rule_min("tv_distance")
    out = []
    for size in sizes:
        w, d = size
        dist = Point(seat).distance(p) - d - GAP
        if dist < tv_min - 1e-9:
            continue
        for off in offsets:
            t = t0 + off
            if t - w / 2.0 < GAP - 1e-6 or t + w / 2.0 > seg_len - GAP + 1e-6:
                continue
            c = (sa[0] + u[0] * t + n[0] * (d / 2.0 + GAP), sa[1] + u[1] * t + n[1] * (d / 2.0 + GAP))
            out.append(Spot("tv_unit", (round(c[0], 4), round(c[1], 4)), rot, (float(w), float(d)), "tv", True))
    return out


def chair_members(size, chair) -> list[tuple[str, tuple, float]]:
    """``(side, local centre, turn)`` of the chairs around a table (``groups.dining_members``: as many per long side
    as fit at 0.55 m, the rest at the ends; each facing the table, 0.02 m off its edge)."""
    out = []
    w, d = float(size[0]), float(size[1])
    for m in GR.dining_members((w, d)):
        x, y = m.local
        if abs(y) > d / 2.0 - 1e-6 and abs(x) < w / 2.0:
            side = "front" if y < 0 else "back"
            y = (-1 if side == "front" else 1) * (d / 2.0 + chair[1] / 2.0 + GR.CHAIR_GAP_M)
        else:
            side = "left" if x < 0 else "right"
            x = (-1 if side == "left" else 1) * (w / 2.0 + chair[1] / 2.0 + GR.CHAIR_GAP_M)
        out.append((side, (x, y), m.turn))
    return out


def _pullout_zones(table: Spot, sides) -> dict[str, tuple]:
    """One pull-out zone (``diner_pullout`` deep from the table edge) per side that holds chairs."""
    w, d = table.size[0] / 2.0, table.size[1] / 2.0
    depth = GR.rule_min("diner_pullout")
    boxes = {"front": (-w, w, -d - depth, -d), "back": (-w, w, d, d + depth),
             "left": (-w - depth, -w, -d, d), "right": (w, w + depth, -d, d)}
    return {s: (f"pullout_{s}", table.center, table.rotation, boxes[s]) for s in sorted(set(sides))}


def _touches(space: Space, table: Spot, side: str) -> bool:
    """The table's side stands within 0.05 m of a wall or a fixed piece (a table against a wall)."""
    w, d = table.size[0] / 2.0, table.size[1] / 2.0
    strips = {"front": (-w, w, -d - 0.06, -d), "back": (-w, w, d, d + 0.06), "left": (-w - 0.06, -w, -d, d),
              "right": (w, w + 0.06, -d, d)}
    return space.zone_layer.hit(space.box_fp(table.center, table.rotation, strips[side], 0.0))


def _partners(space: Space, template: dict, option: dict, anchor: Spot, filled: dict) -> Optional[tuple]:
    """(new partner spots, zones, terms, spots by role) around ``anchor``, or None when a required partner does not
    fit. ``filled``: role -> count of drawn partners already there (``nightstand_sides``: the sides taken)."""
    w, d = float(anchor.size[0]), float(anchor.size[1])
    placed: list[Spot] = []
    placed_fps: list = space.spot_fps(anchor)
    zones: list = []
    counts = option.get("counts") or {}
    optional_total, optional_placed = 0, 0
    by_role: dict[str, list[Spot]] = {}
    seat_front, seat_x, seat_w = -d / 2.0, 0.0, w
    if anchor.shape == "L":
        x0, x1, seat_front = schemas.l_seat_front(anchor.size, anchor.chaise_side, d)
        seat_x, seat_w = (x0 + x1) / 2.0, x1 - x0

    def with_found(found: list[Spot]) -> list:
        return placed_fps + [fp for f in found for fp in space.spot_fps(f)]

    for spec in template["partners"]:
        role, ftype = spec["role"], spec["type"]
        want = counts.get(ftype, spec.get("max", 1))
        want = max(0, want - int(filled.get(role, 0)))
        if role == "nightstand":
            want = min(want, schemas.NIGHTSTANDS_PER_BED.get(anchor.type, 1) - len(filled.get("nightstand_sides", ())))
        if want <= 0:
            continue
        if not spec["required"]:
            optional_total += want
        if not space.allowed(ftype, anchor.center):
            alt = spec.get("alt_type")
            if alt and space.allowed(alt, anchor.center):
                ftype = alt
            else:
                continue                       # the room cannot hold it: the group goes without it
        found: list[Spot] = []
        place = spec["place"]
        sizes = [tuple(s) for s in spec["sizes"]]
        if place == "facing_wall":
            for s in _tv_spots(space, anchor, sizes):
                dist = GC.tv_geometry(anchor.piece(), s.piece())["distance_m"]
                half = min(s.size[0], seat_w) / 2.0
                sight = ("sight", anchor.center, anchor.rotation, (seat_x - half, seat_x + half, seat_front - dist,
                                                                    seat_front))
                if _fits(space, s, placed_fps) and space.zones_free([sight]):
                    found = [s]
                    zones.append(sight)
                    break
        elif place == "front":
            rule = GR.rule(spec["gap"]) if isinstance(spec.get("gap"), str) else {"min": float(spec.get("gap", 0.3))}
            rec_lo = rule.get("rec", rule["min"])
            gaps = list(dict.fromkeys([round((rec_lo + rule.get("rec_max", rec_lo)) / 2.0, 3), rec_lo, rule["min"]]))
            tv = (by_role.get("tv") or [None])[0]
            limit = GC.tv_geometry(anchor.piece(), tv.piece())["distance_m"] if tv is not None else None
            for size in sizes:
                if size[0] > seat_w - 0.3:
                    continue
                for g in gaps:
                    if limit is not None and g + size[1] + 0.40 > limit:
                        continue
                    s = _local_spot(anchor, ftype, (seat_x, seat_front - g - size[1] / 2.0), 0.0, size, role)
                    if _fits(space, s, placed_fps):
                        found = [s]
                        break
                if found:
                    break
        elif place == "flank":
            of = (by_role.get(spec.get("of") or "") or [None])[0]
            if of is None:
                continue
            ol = GC.to_local(anchor.piece(), of.center)
            gap = float(spec.get("gap", 0.35))
            for size in sizes:
                found = []
                for side in (1.0, -1.0):
                    if len(found) >= want:
                        break
                    x = ol[0] + side * (of.size[0] / 2.0 + gap + size[1] / 2.0)
                    s = _local_spot(anchor, ftype, (x, ol[1]), 270.0 if side > 0 else 90.0, size, role)
                    if _fits(space, s, with_found(found), s.zones()):
                        found.append(s)
                if found:
                    break
        elif place == "beside_head":
            gap = float(spec.get("gap", 0.02))
            taken = set(filled.get("nightstand_sides", ()))
            sides = [s for s in ("right", "left") if s not in taken]
            for size in sizes:
                found = []
                for side in sides:
                    if len(found) >= want:
                        break
                    sx = 1.0 if side == "right" else -1.0
                    # Back on the anchor's back line; a drawn headboard flush on the wall line leaves no 2 cm gap, so
                    # the nightstand may step up to 5 cm forward (G4 allows 0.10 m).
                    for step in (0.0, 0.025, 0.05):
                        s = _local_spot(anchor, ftype, (sx * (w / 2.0 + gap + size[0] / 2.0),
                                                        d / 2.0 - size[1] / 2.0 - step), 0.0, size, role, True)
                        if _fits(space, s, with_found(found)) and space.exact_ok(s, s.piece().polygon()):
                            found.append(s)
                            break
                if len(found) >= want:
                    break
        elif place == "foot":
            gap = float(spec.get("gap", 0.05))
            for size in sizes:
                if size[0] > w + 1e-6:
                    continue
                s = _local_spot(anchor, ftype, (0.0, -d / 2.0 - gap - size[1] / 2.0), 0.0, size, role)
                if _fits(space, s, placed_fps):
                    found = [s]
                    break
        elif place == "chair":
            gap = float(spec.get("gap", 0.05))
            for size in sizes:
                s = _local_spot(anchor, ftype, (0.0, -d / 2.0 - gap - size[1] / 2.0), 180.0, size, role)
                if _fits(space, s, placed_fps):
                    found = [s]
                    break
        elif place == "around":
            if filled.get(role):
                continue                       # drawn chairs: none added
            members = chair_members((w, d), sizes[0])
            pull = _pullout_zones(anchor, [m[0] for m in members])
            sides = set()
            for side, z in pull.items():
                if not space.zone_layer.hit(space.zone_fp(z)):
                    sides.add(side)
                elif not _touches(space, anchor, side):
                    return None                # a side without room behind its chairs that does not touch a wall
            zones += [pull[s] for s in sorted(sides)]
            for side, local, turn in members:
                if side not in sides:
                    continue
                s = _local_spot(anchor, ftype, local, turn, sizes[0], role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
            if spec["required"] and members and len(found) < 2:
                return None
        elif place == "stools":
            n = min(schemas.count_by_length(w, schemas.BAR_STOOLS_BY_ISLAND_LENGTH), want)
            size = sizes[0]
            gap = float(spec.get("gap", 0.05))
            for k in range(n):
                x = -w / 2.0 + w * (k + 0.5) / n
                s = _local_spot(anchor, ftype, (x, d / 2.0 + gap + size[1] / 2.0), 0.0, size, role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
        elif place == "pair":
            size = sizes[0]
            for y, turn in ((-(d / 2.0 + 0.05 + size[1] / 2.0), 180.0), (d / 2.0 + 0.05 + size[1] / 2.0, 0.0)):
                s = _local_spot(anchor, ftype, (0.0, y), turn, size, role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
            if spec["required"] and len(found) < 2:
                return None
        if spec["required"] and not found and place != "around":
            return None
        if place not in ("around", "pair"):
            found = found[:want]
        if not spec["required"]:
            optional_placed += len(found)
        for s in found:
            zones += s.zones()
        placed_fps = with_found(found)
        placed += found
        by_role.setdefault(role, []).extend(found)
    terms = {}
    if optional_total:
        terms["partners"] = round(optional_placed / optional_total, 4)
    return placed, zones, terms, by_role


def _anchor_terms(space: Space, group: str, anchor: Spot, by_role: dict, info: dict) -> dict:
    terms: dict = {}
    if group == "seating":
        terms["sight_tv"] = _term_sight(anchor, (by_role.get("tv") or [None])[0])
    if group in ("sleeping_double", "sleeping_single"):
        terms["bed_sees_door"] = _term_bed_door(space, anchor, info["entrance"])
    if group == "work":
        terms["desk_side_light"] = _term_desk_light(space, anchor)
        terms["daylight"] = _term_daylight(space, anchor.center)
    if group in ("dining", "balcony"):
        terms["daylight"] = _term_daylight(space, anchor.center)
        if info["kitchen_points"] and group == "dining":
            dist = min(G.distance(anchor.center, p) for p in info["kitchen_points"])
            terms["related_near"] = round(max(0.0, 1.0 - dist / 6.0), 4)
    return terms


def _prescore(space: Space, group: str, spot: Spot, wall, align: str, info: dict) -> float:
    """A cheap score of an anchor alone (alignment, daylight, the bed's view of the door) to order the tries."""
    terms = {}
    if wall is not None:
        terms["wall_use"] = _align_term(wall[1], wall[2], wall[3], align)
    if group in ("dining", "work", "balcony"):
        terms["daylight"] = _term_daylight(space, spot.center)
    if group in ("sleeping_double", "sleeping_single"):
        terms["bed_sees_door"] = _term_bed_door(space, spot, info["entrance"])
    if group == "work":
        terms["desk_side_light"] = _term_desk_light(space, spot)
    return _score(terms)


# --------------------------------------------------------------------------
# Group candidates
# --------------------------------------------------------------------------

def anchored_candidates(space: Space, entry: dict, level: int, info: dict) -> list[Cand]:
    template = GR.load_groups()[entry["group"]]
    options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
    anchor_spec = template["anchor"]
    align = anchor_spec.get("align", "any")
    zone_poly = info["zones"].get(entry.get("zone_id"))
    drawn = info["by_id"].get(entry.get("anchor_id")) if entry.get("drawn") else None
    filled = info["filled"].get(entry["group_id"], {})
    budget = info["budget"]
    out: list[Cand] = []
    tries: list[tuple] = []
    for oname in options:
        opt = template["options"][oname]
        atype = opt["anchor"]
        if drawn is not None:
            if drawn.get("status") == "unverified" or drawn.get("build") is False or drawn["type"] != atype:
                continue
            tries.append((1.0, ("drawn", oname), (oname,), (oname, _spot_from(drawn), None)))
            continue
        if not space.allowed(atype, None) and zone_poly is None:
            continue
        sizes = [tuple(s) for s in (opt.get("sizes") or {}).get(atype, [])] or \
            GR.sizes_for(template, atype, float(entry.get("area") or space.area))
        for si, size in enumerate(sizes):
            if anchor_spec["place"] == "wall":
                sides = ("right", "left") if atype == "sofa_corner" else (None,)
                for k, t, c, rot, lo, hi in _wall_positions(space, size):
                    for side in sides:
                        if budget["used"] >= budget["generate"]:
                            break
                        budget["used"] += 1
                        s = Spot(atype, c, rot, size, "anchor", True, "L" if side else None, side)
                        if not space.spot_free(s):
                            continue
                        pre = _prescore(space, entry["group"], s, (k, t, lo, hi), align, info) - 0.01 * si
                        tries.append((pre, (oname, k, int(round(t / MERGE_M)), side or ""), (round(t, 3), si),
                                      (oname, s, (k, t, lo, hi))))
            else:
                for c, rot in _free_positions(space, size):
                    if budget["used"] >= budget["generate"]:
                        break
                    budget["used"] += 1
                    s = Spot(atype, c, rot, size, "anchor", False)
                    if not space.spot_free(s):
                        continue
                    pre = _prescore(space, entry["group"], s, None, align, info) - 0.01 * si
                    tries.append((pre, (oname, round(rot) % 180, int(round(c[0] / MERGE_M)),
                                        int(round(c[1] / MERGE_M))), (c, si), (oname, s, None)))
    valid = 0
    for n_try, (_pre, _bucket, _key, (oname, spot, wall)) in enumerate(_ordered(tries)):
        if n_try >= ANCHOR_TRIES or valid >= 3 * PER_LEVEL:
            break
        opt = template["options"][oname]
        if spot.existing_id is None:
            if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(spot.center)):
                continue
            zones = _one_side(space, spot, spot.zones())
            if zones is None or not space.zones_free(zones) or not space.allowed(spot.type, spot.center):
                continue
        else:
            zones = [z for z in spot.zones() if not space.zone_layer.hit(space.zone_fp(z))]
        res = _partners(space, template, opt, spot, filled)
        if res is None:
            continue
        partners, pzones, terms, by_role = res
        if spot.existing_id is not None and not partners:
            continue                                   # a drawn group with nothing to add
        if spot.existing_id is None:
            rec = _term_recommended(space, spot)
            if rec is not None:
                terms["recommended"] = rec
            if wall is not None:
                terms["wall_use"] = _align_term(wall[1], wall[2], wall[3], align)
        else:
            ds = [G.distance(p.center, spot.center) for p in partners]
            terms["drawn_distance"] = round(max(0.0, 1.0 - (sum(ds) / len(ds)) / 4.0), 4) if ds else 1.0
        terms.update(_anchor_terms(space, entry["group"], spot, by_role, info))
        _previous_term(terms, partners if spot.existing_id else [spot] + partners, info)
        new = ([spot] if spot.existing_id is None else []) + partners
        cand = Cand(level, entry["group_id"], entry["group"], oname, spot, new, zones + pzones, terms)
        if not _finish(space, cand):
            continue
        valid += 1
        cand.local = _score(terms)
        key = (wall[0], int(round(wall[1] / MERGE_M))) if wall else \
            (int(round(spot.center[0] / MERGE_M)), int(round(spot.center[1] / MERGE_M)))
        cand.sig = (oname, round(spot.rotation) % 360, key, spot.chaise_side or "", len(new))
        out.append(cand)
    return _keep(out, PER_LEVEL)


def _one_side(space: Space, spot: Spot, zones: list) -> Optional[list]:
    """A bed that needs one free long side (``sides_needed: 1``, a single bed) keeps the side zones that are free
    (the other side may touch a wall); None when neither is."""
    if int(GR.use_zone(spot.type).get("sides_needed", 2)) != 1:
        return zones
    sides = [z for z in zones if z[0] in ("left", "right")]
    free = [z for z in sides if not space.zone_layer.hit(space.zone_fp(z))]
    if sides and not free:
        return None
    return [z for z in zones if z[0] not in ("left", "right")] + free[:1]


def _previous_term(terms: dict, spots: list[Spot], info: dict) -> None:
    """``drawn_distance`` of a re-layout: new pieces near the room's earlier added pieces of their type."""
    prev = info.get("previous") or []
    if not prev or not spots:
        return
    ds = []
    for s in spots:
        same = [c for t, c in prev if t == s.type]
        if same:
            ds.append(min(G.distance(s.center, c) for c in same))
    if ds:
        terms["drawn_distance"] = round(max(0.0, 1.0 - (sum(ds) / len(ds)) / 3.0), 4)


def _keep(cands: list[Cand], n: int) -> list[Cand]:
    """The best ``n`` candidates, one per signature (score, then position, deterministic)."""
    cands = sorted(cands, key=lambda c: (-c.local, c.sig, _pos_key(c)))
    out, seen = [], set()
    for c in cands:
        if c.sig in seen:
            continue
        seen.add(c.sig)
        out.append(c)
        if len(out) >= n:
            break
    return out


def _pos_key(c: Cand) -> tuple:
    return tuple((s.type, round(s.center[0], 2), round(s.center[1], 2), round(s.rotation, 1)) for s in c.spots)


def member_candidates(space: Space, entry: dict, members: list[dict], level: int, info: dict) -> list[Cand]:
    """Wall places of one member level of a set (or one missing piece of a drawn group): every member spec of the
    level (a bathtub or a shower for the ``bath`` role) at its sizes on every wall."""
    out = []
    budget = info["budget"]
    zone_poly = info["zones"].get(entry.get("zone_id"))
    near = info["near"].get(entry["group_id"])
    for member in members:
        ftype = member["type"]
        if not space.allowed(ftype, None) and zone_poly is None:
            continue
        align = member.get("align", "any")
        for size in [tuple(s) for s in member["sizes"]]:
            for k, t, c, rot, lo, hi in _wall_positions(space, size):
                if budget["used"] >= budget["generate"]:
                    break
                budget["used"] += 1
                spot = Spot(ftype, c, rot, size, member["role"], True)
                if not space.spot_free(spot):
                    continue
                if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(spot.center)):
                    continue
                zones = spot.zones()
                if not space.zones_free(zones):
                    continue
                terms = {"wall_use": _align_term(t, lo, hi, align)}
                rec = _term_recommended(space, spot)
                if rec is not None:
                    terms["recommended"] = rec
                if near:
                    dist = min(G.distance(spot.center, p) for p in near)
                    terms["drawn_distance"] = round(max(0.0, 1.0 - dist / 4.0), 4)
                _previous_term(terms, [spot], info)
                cand = Cand(level, entry["group_id"], entry["group"], ftype, spot, [spot], zones, terms)
                if not space.allowed(ftype, spot.center) or not _finish(space, cand):
                    continue
                cand.local = _score(terms)
                cand.sig = (member["role"], ftype, k, int(round(t / MERGE_M)))
                out.append(cand)
    return _keep(out, PER_LEVEL)


# --------------------------------------------------------------------------
# Kitchen runs
# --------------------------------------------------------------------------

BIN_M = 0.05


class Leg:
    """One outline segment as a kitchen leg: 0.05 m bins along it saying what may stand there (a counter, the
    fridge, the hob), each with its aisle in front inside the room and off the fixed pieces."""

    def __init__(self, space: Space, k: int, depth: float, aisle: float):
        self.k = k
        a, b = space.ctx.segments[k]
        self.a = a
        self.length = G.distance(a, b)
        self.u = ((b[0] - a[0]) / self.length, (b[1] - a[1]) / self.length)
        self.n = space.ctx.segment_normal(k)
        self.rot = placer._rotation_for_normal(self.n)
        self.depth = depth
        self.nb = max(0, int(self.length / BIN_M))
        ok: dict[str, list] = {"kitchen_counter": [], "fridge": [], "stove": []}
        for i in range(self.nb):
            t0, t1 = i * BIN_M, (i + 1) * BIN_M
            fp = self.fp(space, t0, t1, GAP, depth + GAP)
            aisle_ok = not space.zone_layer.hit(self.fp(space, t0, t1, depth + GAP, depth + GAP + aisle))
            for t in ok:
                ok[t].append(aisle_ok and not space.layer_for(t).hit(fp))
        self.flags = ok
        self.bad = {t: np.concatenate([[0], np.cumsum([0 if v else 1 for v in vals])]) for t, vals in ok.items()}

    def fp(self, space: Space, t0: float, t1: float, s0: float, s1: float):
        c = self.point((t0 + t1) / 2.0, (s0 + s1) / 2.0)
        hx, hy = (t1 - t0) / 2.0, (s1 - s0) / 2.0
        return space.box_fp(c, self.rot, (-hx, hx, -hy, hy))

    def ok(self, ftype: str, t0: float, t1: float) -> bool:
        if t0 < -1e-6 or t1 > self.length + 1e-6:
            return False
        i0 = max(0, int(math.floor(t0 / BIN_M + 1e-6)))
        i1 = min(self.nb, int(math.ceil(t1 / BIN_M - 1e-6)))
        if i1 <= i0:
            return False
        bad = self.bad[ftype]
        return int(bad[i1] - bad[i0]) == 0

    def intervals(self) -> list[tuple[float, float]]:
        """Maximal stretches (t) where a counter may stand, within the segment's ends."""
        out, start = [], None
        flags = self.flags["kitchen_counter"] + [False]
        for i, ok in enumerate(flags):
            if ok and start is None:
                start = i
            elif not ok and start is not None:
                t0, t1 = max(GAP, start * BIN_M), min(self.length - GAP, i * BIN_M)
                if t1 - t0 > 0.3:
                    out.append((round(t0, 3), round(t1, 3)))
                start = None
        return out

    def point(self, t: float, s: float) -> tuple[float, float]:
        return self.a[0] + self.u[0] * t + self.n[0] * s, self.a[1] + self.u[1] * t + self.n[1] * s

    def spot(self, ftype: str, t0: float, t1: float, role: str) -> Spot:
        c = self.point((t0 + t1) / 2.0, self.depth / 2.0 + GAP)
        return Spot(ftype, (round(c[0], 4), round(c[1], 4)), self.rot, (round(t1 - t0, 3), self.depth), role, True)


def _convex_turn(space: Space, k: int) -> bool:
    """The corner between segment k and the next turns left by about 90 degrees (an inner corner of the room)."""
    segs = space.ctx.segments
    a, b = segs[k]
    c, d = segs[(k + 1) % len(segs)]
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (d[0] - c[0], d[1] - c[1])
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    ang = G.angle_difference_deg(math.degrees(math.atan2(v1[1], v1[0])), math.degrees(math.atan2(v2[1], v2[0])))
    return cross > 0 and abs(ang - 90.0) < 3.0


class Path:
    """A run along one or more legs, walked from its start (the fridge's end). ``parts``: ``[(leg, t0, t1)]`` in the
    outline's order; ``forward`` walks them in that order with t going up, else backwards with t going down. The
    corner square of an L or U (the dead corner) belongs to the leg that ends at the corner in the outline's order."""

    def __init__(self, legs: dict, parts: list, forward: bool, depth: float):
        self.L = legs
        self.parts = list(parts) if forward else list(reversed(parts))
        self.forward = forward
        self.offsets = []
        q = 0.0
        for k, t0, t1 in self.parts:
            self.offsets.append((q, q + (t1 - t0), k, t0, t1))
            q += t1 - t0
        self.total = q
        sq = depth + GAP
        self.corners = []
        for j in range(len(self.offsets) - 1):
            if forward:
                end = self.offsets[j][1]
                self.corners.append((end - sq, end))
            else:
                start = self.offsets[j + 1][0]
                self.corners.append((start, start + sq))

    def where(self, q0: float, q1: float) -> Optional[tuple[int, float, float]]:
        for s0, s1, k, t0, t1 in self.offsets:
            if s0 - 1e-6 <= q0 and q1 <= s1 + 1e-6:
                if self.forward:
                    return k, t0 + (q0 - s0), t0 + (q1 - s0)
                return k, t1 - (q1 - s0), t1 - (q0 - s0)
        return None

    def module_ok(self, ftype: str, q0: float, q1: float) -> Optional[tuple[int, float, float]]:
        w = self.where(q0, q1)
        if w is None or not all(q1 <= c0 + 1e-6 or q0 >= c1 - 1e-6 for c0, c1 in self.corners):
            return None
        if not self.L[w[0]].ok(ftype, w[1], w[2]):
            return None
        return w

    def front_mid(self, w: tuple[int, float, float]) -> tuple[float, float]:
        leg = self.L[w[0]]
        return leg.point((w[1] + w[2]) / 2.0, leg.depth + GAP)

    def spots(self, appliances: list[tuple[float, float, str, str]]) -> list[Spot]:
        """The appliances and one counter per free stretch of each leg."""
        out = []
        for s0, s1, k, _t0, _t1 in self.offsets:
            cuts = sorted((max(a0, s0), min(a1, s1), t, role) for a0, a1, t, role in appliances
                          if a0 < s1 - 1e-6 and a1 > s0 + 1e-6)
            cursor = s0
            for a0, a1, t, role in cuts:
                if a0 - cursor > 0.05:
                    w = self.where(cursor, a0)
                    out.append(self.L[k].spot("kitchen_counter", w[1], w[2], "counter"))
                w = self.where(a0, a1)
                out.append(self.L[k].spot(t, w[1], w[2], role))
                cursor = a1
            if s1 - cursor > 0.05:
                w = self.where(cursor, s1)
                out.append(self.L[k].spot("kitchen_counter", w[1], w[2], "counter"))
        return out


def _lengths(available: float, wanted: tuple) -> list[float]:
    return sorted({round(min(available, x), 3) for x in wanted if x <= available + 1e-6} | {round(available, 3)},
                  reverse=True)


def _run_paths(space: Space, legs: dict, shape: str, depth: float, max_leg: float) -> list[list[tuple]]:
    """The parts ``[(leg, t0, t1)]`` of every run of one shape (outline order)."""
    n = len(space.ctx.segments)
    d2 = round(depth + 2 * GAP, 3)
    out = []
    if shape == "I":
        for k, leg in sorted(legs.items()):
            for i0, i1 in leg.intervals():
                for length in _lengths(min(i1 - i0, max_leg), (3.6, 3.0)):
                    if length < 2.99:
                        continue
                    for start in sorted({i0, round(i1 - length, 3)}):
                        out.append([(k, start, round(start + length, 3))])
    elif shape in ("L", "U"):
        for k in sorted(legs):
            chain = [k, (k + 1) % n] if shape == "L" else [k, (k + 1) % n, (k + 2) % n]
            if len(set(chain)) < len(chain) or any(c not in legs for c in chain) or \
                    not all(_convex_turn(space, c) for c in chain[:-1]):
                continue
            first, last = legs[chain[0]], legs[chain[-1]]
            end_a = round(first.length - GAP, 3)
            ia = next(((i0, i1) for i0, i1 in first.intervals() if i1 >= end_a - 1e-6), None)
            ib = next(((i0, i1) for i0, i1 in last.intervals() if i0 <= d2 + 1e-6), None)
            if ia is None or ib is None:
                continue
            mids = []
            for mid in chain[1:-1]:
                m = legs[mid]
                if any(i0 <= d2 + 1e-6 and i1 >= m.length - GAP - 1e-6 for i0, i1 in m.intervals()):
                    mids.append((mid, d2, round(m.length - GAP, 3)))
            if len(mids) != len(chain) - 2:
                continue
            for la in _lengths(min(end_a - ia[0], max_leg), (2.4, 1.8)):
                for lb in _lengths(min(ib[1] - d2, max_leg), (2.4, 1.8)):
                    if la < 1.2 or lb < 1.2:
                        continue
                    out.append([(chain[0], round(end_a - la, 3), end_a)] + mids + [(chain[-1], d2, round(d2 + lb, 3))])
    return out


def _run_layouts(path: Path, run: dict, space: Space) -> list[tuple]:
    """Module layouts of one path, best first: ``(spots, terms, key)``. The fridge stands at the path start, the sink
    and the hob after it; the minimum landings and the work-triangle legs are hard, the recommended landings, a
    compact triangle and the sink under a window score."""
    mods = run["modules"]
    fr_w = float(mods["fridge"]["sizes"][0][0])
    hob_w = float(mods["hob"]["sizes"][0][0])
    land = {k: GR.rule_min(mods[k]["landing"]) for k in mods}
    c1_min, c2_min = max(land["fridge"], 0.40), max(land["sink"], 0.50)
    leg_rule, sum_rule = GR.rule("triangle_leg"), GR.rule("triangle_sum")
    total = path.total
    fr = path.module_ok("fridge", 0.0, fr_w)
    if fr is None:
        return []
    f_pt = path.front_mid(fr)
    wins = [w.inner_point for w in space.ctx.windows]
    results = []
    for sink_size in mods["sink"]["sizes"]:
        sw = float(sink_size[0])
        q_s = fr_w + c1_min
        while q_s + sw + c2_min + hob_w <= total + 1e-6:
            sk = path.module_ok("kitchen_counter", q_s, q_s + sw)
            if sk is not None:
                s_pt = path.front_mid(sk)
                hobs = {round(q_s + sw + c, 3) for c in (c2_min, 0.6, 0.9, 1.2)}
                hobs |= {round(total - hob_w - c, 3) for c in (0.0, 0.3, 0.4, 0.6)}
                for q_h in sorted(hobs):
                    c2, c3 = q_h - (q_s + sw), total - (q_h + hob_w)
                    if c2 < c2_min - 1e-6 or c3 < -1e-6 or (1e-6 < c3 < 0.30 - 1e-6):
                        continue
                    hb = path.module_ok("stove", q_h, q_h + hob_w)
                    if hb is None:
                        continue
                    h_pt = path.front_mid(hb)
                    legs_m = (G.distance(f_pt, s_pt), G.distance(s_pt, h_pt), G.distance(h_pt, f_pt))
                    if not all(leg_rule["min"] - 1e-9 <= v <= leg_rule["max"] + 1e-9 for v in legs_m) or \
                            sum(legs_m) > sum_rule["max"] + 1e-9:
                        continue
                    c1 = q_s - fr_w
                    rec = (c1 >= GR.rule_rec("fridge_landing"),
                           c2 >= GR.rule_rec("sink_landing") + GR.rule_min("hob_landing"),
                           c3 >= GR.rule_rec("hob_landing"))
                    sink_c = path.L[sk[0]].point((sk[1] + sk[2]) / 2.0, 0.0)
                    terms = {"recommended": round(sum(rec) / 3.0, 4),
                             "wall_use": round(max(0.0, 1.0 - abs(sum(legs_m) - 4.5) / 4.5), 4),
                             "sink_window": 1.0 if any(G.distance(sink_c, w) <= SINK_WINDOW_M + sw / 2.0
                                                       for w in wins) else 0.0}
                    results.append((_score(terms), (round(q_s, 2), round(q_h, 2), sw), terms))
            q_s = round(q_s + 0.1, 3)
    results.sort(key=lambda r: (-r[0], r[1]))
    out = []
    for _sc, key, terms in results[:2]:
        q_s, q_h, sw = key
        spots = path.spots([(0.0, fr_w, "fridge", "fridge"), (q_s, q_s + sw, "sink_kitchen", "sink"),
                            (q_h, q_h + hob_w, "stove", "hob")])
        out.append((spots, terms, key))
    return out


def _galley_paths(legs: dict, depth: float, aisle: float) -> list:
    """Two opposite legs ``(leg A part, leg B part)``: fridge and sink on A, the hob on B, the aisle between."""
    out = []
    keys = sorted(legs)
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            A, B = legs[ka], legs[kb]
            if G.angle_difference_deg(math.degrees(math.atan2(A.n[1], A.n[0])),
                                      math.degrees(math.atan2(-B.n[1], -B.n[0]))) > 2.0:
                continue
            gap = abs((B.a[0] - A.a[0]) * A.n[0] + (B.a[1] - A.a[1]) * A.n[1])
            if gap < 2 * (depth + GAP) + aisle - 1e-6 or gap > 2 * (depth + GAP) + 1.8:
                continue
            for ia in A.intervals():
                for ib in B.intervals():
                    for la in _lengths(min(ia[1] - ia[0], 3.6), (2.4, 1.8)):
                        for lb in _lengths(min(ib[1] - ib[0], 2.4), (1.2,)):
                            if la < 1.79 or lb < 1.19:
                                continue
                            pa, pb = (ka, ia[0], round(ia[0] + la, 3)), (kb, ib[0], round(ib[0] + lb, 3))
                            out += [(pa, pb), (pb, pa)]
    return out


def _galley_layouts(legs: dict, parts: tuple, forward: bool, run: dict) -> list[tuple]:
    """Fridge and sink on the first leg (from its start in the walk direction), the hob on the second."""
    mods = run["modules"]
    depth = float(run["depth"])
    fr_w, hob_w = float(mods["fridge"]["sizes"][0][0]), float(mods["hob"]["sizes"][0][0])
    land = {k: GR.rule_min(mods[k]["landing"]) for k in mods}
    leg_rule, sum_rule = GR.rule("triangle_leg"), GR.rule("triangle_sum")
    pa, pb = Path(legs, [parts[0]], forward, depth), Path(legs, [parts[1]], forward, depth)
    fr = pa.module_ok("fridge", 0.0, fr_w)
    if fr is None:
        return []
    f_pt = pa.front_mid(fr)
    results = []
    for sink_size in mods["sink"]["sizes"]:
        sw = float(sink_size[0])
        q_s = fr_w + max(land["fridge"], 0.40)
        while q_s + sw + max(land["sink"], 0.5) <= pa.total + 1e-6:
            sk = pa.module_ok("kitchen_counter", q_s, q_s + sw)
            if sk is not None:
                s_pt = pa.front_mid(sk)
                q_h = max(land["hob"], 0.3)
                while q_h + hob_w <= pb.total + 1e-6:
                    c3 = pb.total - (q_h + hob_w)
                    hb = pb.module_ok("stove", q_h, q_h + hob_w)
                    if hb is not None and not (1e-6 < c3 < 0.30 - 1e-6):
                        h_pt = pb.front_mid(hb)
                        lm = (G.distance(f_pt, s_pt), G.distance(s_pt, h_pt), G.distance(h_pt, f_pt))
                        if all(leg_rule["min"] - 1e-9 <= v <= leg_rule["max"] + 1e-9 for v in lm) and \
                                sum(lm) <= sum_rule["max"] + 1e-9:
                            terms = {"recommended": 1.0 if (q_s - fr_w) >= 0.6 and c3 >= 0.38 else 0.5,
                                     "wall_use": round(max(0.0, 1.0 - abs(sum(lm) - 4.5) / 4.5), 4),
                                     "sink_window": 0.0}
                            results.append((_score(terms), (round(q_s, 2), round(q_h, 2), sw), terms))
                    q_h = round(q_h + 0.1, 3)
            q_s = round(q_s + 0.1, 3)
    results.sort(key=lambda r: (-r[0], r[1]))
    out = []
    for _sc, key, terms in results[:2]:
        q_s, q_h, sw = key
        spots = pa.spots([(0.0, fr_w, "fridge", "fridge"), (q_s, q_s + sw, "sink_kitchen", "sink")])
        spots += pb.spots([(q_h, q_h + hob_w, "stove", "hob")])
        out.append((spots, terms, key))
    return out


def run_candidates(space: Space, entry: dict, level: int, info: dict) -> list[Cand]:
    template = GR.load_groups()[entry["group"]]
    run = template["run"]
    depth = float(run["depth"])
    aisle = GR.rule_min("kitchen_aisle")
    zone_poly = info["zones"].get(entry.get("zone_id"))
    legs = {k: Leg(space, k, depth, aisle) for k, (a, b) in enumerate(space.ctx.segments) if G.distance(a, b) >= 1.2}
    options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
    out = []
    budget = info["budget"]
    for oname in options:
        shape = template["options"][oname]["shape"]
        if shape == "galley":
            jobs = [(parts, fw) for parts in _galley_paths(legs, depth, aisle) for fw in (True, False)]
        else:
            jobs = [(parts, fw) for parts in _run_paths(space, legs, shape, depth, float(run["max_leg"]))
                    for fw in (True, False)]
        for parts, forward in jobs:
            if budget["used"] >= budget["generate"]:
                break
            budget["used"] += 1
            if shape == "galley":
                layouts = _galley_layouts(legs, parts, forward, run)
            else:
                layouts = _run_layouts(Path(legs, parts, forward, depth), run, space)
            for spots, terms, key in layouts:
                if zone_poly is not None and not all(zone_poly.buffer(0.1).contains(Point(s.center)) for s in spots):
                    continue
                anchor = next((s for s in spots if s.type == "kitchen_counter"), spots[0])
                zones = [z for s in spots for z in s.zones()]
                cand = Cand(level, entry["group_id"], entry["group"], oname, anchor, spots, zones, dict(terms))
                if not all(space.allowed(s.type, s.center) for s in spots) or not _finish(space, cand):
                    continue
                cand.local = _score(cand.terms)
                cand.sig = (oname, tuple((p[0], int(round(p[1] / MERGE_M)), int(round(p[2] / MERGE_M)))
                                         for p in parts), forward, key)
                out.append(cand)
    return _keep(out, PER_LEVEL)


# --------------------------------------------------------------------------
# The search
# --------------------------------------------------------------------------

@dataclass
class Node:
    cands: tuple
    occ: np.ndarray
    res: np.ndarray
    score: float
    sig: tuple
    polys: list = field(default_factory=list)
    zfps: list = field(default_factory=list)


class Walk:
    """Walkways on the raster for the beam's nodes (see the module docstring, step 4)."""

    def __init__(self, space: Space):
        self.space = space
        R = space.R
        self.seeds = {}
        for door in space.ctx.doors:
            if door.zone is not None and not door.zone.is_empty:
                m = R.polygon_mask(door.zone) & R.inside
                if m.any():
                    self.seeds[door.id] = m
        self.entrance = GC.entrance_door(space.building, space.room, space.ctx)
        self.main, self.sec = GR.rule_min("walkway_main"), GR.rule_min("walkway")
        self.base_cover = None
        base = self.state(space.fixed_mask)
        # Required: every door pair (at its width) the room with its fixed pieces connects.
        self.required = [(a, b, w) for a, b, w, ok in base["pairs"] if ok]
        self.base_cover = base["cover"]

    def state(self, occ: np.ndarray, zfps=()) -> dict:
        R = self.space.R
        free = R.inside & ~occ
        dist = R.clearance(free)
        labels = {w: R.components(dist >= w / 2.0 - 1e-6)[1] for w in (self.sec, self.main)}
        comps = {w: {d: set(int(v) for v in np.unique(labels[w][m]) if v > 0) for d, m in self.seeds.items()}
                 for w in labels}
        pairs = []
        ids = sorted(self.seeds)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                w = self.main if self.entrance in (a, b) else self.sec
                pairs.append((a, b, w, bool(comps[w][a] & comps[w][b])))
                if w == self.main:
                    pairs.append((a, b, self.sec, bool(comps[self.sec][a] & comps[self.sec][b])))
        zones_ok = True
        cover = None
        if self.entrance in self.seeds and (zfps or self.base_cover is None):
            reach_ids = list(comps[self.sec][self.entrance])
            reach = np.isin(labels[self.sec], reach_ids) if reach_ids else np.zeros_like(free)
            cover = Layer(R.dilate(reach, self.sec / 2.0) & free)
            for zfp in zfps:
                sub = free[zfp[1]:zfp[2], zfp[3]:zfp[4]] if zfp[0] == "r" else free.ravel()[zfp[1]]
                if not sub.any():
                    continue
                if not cover.hit(zfp):
                    zones_ok = False             # a new piece's use zone no walkway reaches (G11)
                    break
        return {"pairs": pairs, "zones_ok": zones_ok, "cover": cover}

    def ok(self, occ: np.ndarray, zfps) -> bool:
        st = self.state(occ, zfps)
        have = {(a, b, w): ok for a, b, w, ok in st["pairs"]}
        if any(not have.get((a, b, w), False) for a, b, w in self.required):
            return False
        return st["zones_ok"]


def _expand(node: Node, cand: Cand, layers: tuple) -> bool:
    occres, occ = layers
    for fp in cand.fps:
        if occres.hit(fp):
            return False
    for zfp in cand.zfps:
        if occ.hit(zfp):
            return False
    for poly, bb in zip(cand.polys, cand.bboxes):
        for q in node.polys:
            if _close(bb, q.bounds) and poly.intersection(q).area > placer.AREA_EPS:
                return False
    return True


def _levels(space: Space, prog: dict, info: dict) -> list[tuple[dict, list[Cand], bool]]:
    """One search level per anchored group or run, one per set member; with their candidates."""
    levels = []
    for entry in prog["groups"]:
        template = GR.load_groups()[entry["group"]]
        if entry.get("note", "").startswith(("unverified", "no completion")):
            continue
        if template["layout"] == "anchored":
            if entry.get("drawn") and (not template["partners"] or not entry.get("missing")):
                continue                               # a drawn wardrobe, a drawn table with its chairs: nothing to add
            levels.append((entry, anchored_candidates(space, entry, len(levels), info), entry["required"]))
        elif template["layout"] == "run":
            if entry.get("drawn"):
                if "fridge" not in (entry.get("missing") or []):
                    continue                           # a drawn run: only a missing fridge is added beside it
                member = {"role": "fridge", "type": "fridge", "sizes": [[0.6, 0.65], [0.7, 0.7]], "align": "any"}
                levels.append((entry, member_candidates(space, entry, [member], len(levels), info), False))
            else:
                levels.append((entry, run_candidates(space, entry, len(levels), info), entry["required"]))
        else:
            options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
            have = {info["by_id"][m]["type"] for m in entry.get("members") or [] if m in info["by_id"]}
            if entry.get("drawn") and entry.get("anchor_id") in info["by_id"]:
                have.add(info["by_id"][entry["anchor_id"]]["type"])
            roles = []
            for oname in options:
                for role in template["options"][oname].get("members", []):
                    if role not in roles:
                        roles.append(role)
            for role in roles:
                types = [m for m in template["members"] if m["role"] == role and (
                    not m.get("option") or any(template["options"][o].get(role) == m["type"] for o in options))]
                if not types:
                    continue
                if any(m["type"] in have for m in types) or (role == "bath" and have & {"shower", "bathtub"}):
                    continue                           # drawn already: only what is missing is added
                if entry.get("drawn") and not any(m.get("required") for m in types):
                    continue                           # a drawn set gets only its missing required members
                required = entry["required"] and any(m.get("required") for m in types)
                levels.append((entry, member_candidates(space, entry, types, len(levels), info), required))
    return levels


ROLE_OF_TYPE = {"tv_unit": "tv", "table_coffee": "coffee", "ottoman": "coffee", "armchair": "armchair",
                "nightstand": "nightstand", "bench": "bench", "chair": "chair", "office_chair": "chair",
                "bar_stool": "stool"}


def _info(space: Space, building: dict, room_id: str, prog: dict, budget: dict) -> dict:
    by_id = {f["id"]: f for f in building.get("furniture") or [] if f.get("room_id") == room_id}
    filled: dict = {}
    near: dict = {}
    for entry in prog["groups"]:
        if not entry.get("drawn") or entry.get("anchor_id") not in by_id:
            continue
        roles: dict = {}
        anchor = by_id[entry["anchor_id"]]
        members = [by_id[m] for m in entry.get("members") or [] if m in by_id]
        for m in members:
            role = ROLE_OF_TYPE.get(m["type"])
            if role:
                roles[role] = roles.get(role, 0) + 1
        if any(m["type"] == "nightstand" for m in members) and anchor.get("type") in GC.BED_TYPES:
            bed = placer.drawn_piece(anchor)
            roles["nightstand_sides"] = sorted({GC.nightstand_place(bed, placer.drawn_piece(m))["side"]
                                                for m in members if m["type"] == "nightstand"})
            roles.pop("nightstand", None)
        filled[entry["group_id"]] = roles
        near[entry["group_id"]] = [tuple(placer.drawn_piece(m).center) for m in [anchor] + members]
    zones = {z["zone_id"]: Polygon(z["polygon"]).buffer(0) for z in prog.get("zones") or []}
    previous = [(f["type"], tuple(placer.drawn_piece(f).center)) for f in by_id.values()
                if f.get("source") == "added_by_ai" and f.get("type") not in schemas.MOUNTED_TYPES
                and f.get("footprint")]
    return {"by_id": by_id, "filled": filled, "near": near, "zones": zones, "budget": budget,
            "entrance": GC.entrance_door(building, space.room, space.ctx),
            "kitchen_points": _kitchen_targets(space), "previous": previous}


def fixed_zones(space: Space) -> list:
    """The use zones of the fixed (drawn) built pieces that are free with the fixed pieces alone: no new piece may
    stand there (a wardrobe in a drawn bed's side clearance), and the walkways must keep reaching them."""
    out = []
    chairs = [(f, p) for f, p in zip(space.fixed_items, space.fixed_pieces) if f.get("type") in GC.SEAT_TYPES
              and f.get("build") is not False]
    for f, p in zip(space.fixed_items, space.fixed_pieces):
        if f.get("build") is False or f.get("type") == "unknown":
            continue
        spot = Spot(f["type"], p.center, p.rotation_deg, p.size, "fixed", False, p.shape, p.chaise_side,
                    existing_id=f["id"])
        zones = _one_side(space, spot, spot.zones())
        if zones is None:
            zones = [z for z in spot.zones() if z[0] not in ("left", "right")]
        out += [z for z in zones if not space.zone_layer.hit(space.zone_fp(z))]
        if f["type"] == "table_dining":
            # A drawn table keeps the pull-out room behind its drawn chairs (they stand in it, so it is not tested).
            poly = p.polygon()
            sides = {GC._side_of(p, c.center) for _cf, c in chairs if c.polygon().distance(poly) <= 0.6}
            out += [(f"pullout_drawn_{s}",) + z[1:] for s, z in _pullout_zones(spot, sides).items()]
    return out


def _search(space: Space, levels: list, walk: Walk, budget: dict) -> list[Node]:
    res = np.zeros_like(space.fixed_mask)
    reach = []
    for z in fixed_zones(space):
        zfp = space.zone_fp(z)
        paint(res, zfp)
        if _reached(z) and (walk.base_cover is None or walk.base_cover.hit(zfp)):
            reach.append(zfp)                    # a drawn piece's zone the walkways reach now must stay reached
    root = Node((), space.fixed_mask.copy(), res, 0.0, (), [], reach)
    beam = [root]
    for _entry, cands, required in levels:
        bonus = REQUIRED_BONUS if required else OPTIONAL_BONUS
        children = []
        for node in beam:
            layers = (Layer(node.occ | node.res), Layer(node.occ))
            for cand in cands:
                if budget["nodes"] >= budget["expand"]:
                    break
                budget["nodes"] += 1
                if _expand(node, cand, layers):
                    children.append((node, cand, node.score + bonus + cand.local))
            children.append((node, None, node.score))          # the level skipped
        children.sort(key=lambda c: (-round(c[2], 6), c[0].sig, c[1].sig if c[1] is not None else ()))
        nxt, seen, per_parent, rejected = [], set(), {}, set()
        # Two passes: first at most PER_PARENT children per parent (the beam keeps different earlier choices),
        # then the best of the rest.
        for cap in (PER_PARENT, BEAM_WIDTH):
            for node, cand, score in children:
                if len(nxt) >= BEAM_WIDTH:
                    break
                sig = node.sig + ((cand.sig if cand is not None else ("skip",)),)
                if sig in seen or sig in rejected or per_parent.get(node.sig, 0) >= cap:
                    continue
                if cand is None:
                    child = Node(node.cands + (None,), node.occ, node.res, score, sig, node.polys, node.zfps)
                else:
                    occ = node.occ.copy()
                    res = node.res.copy()
                    for fp in cand.fps:
                        paint(occ, fp)
                    for zfp in cand.zfps:
                        paint(res, zfp)
                    zfps = node.zfps + cand.rfps           # the zones the walkways must reach
                    budget["walks"] += 1
                    if not walk.ok(occ, zfps):
                        rejected.add(sig)
                        continue
                    child = Node(node.cands + (cand,), occ, res, score, sig, node.polys + cand.polys, zfps)
                seen.add(sig)
                per_parent[node.sig] = per_parent.get(node.sig, 0) + 1
                nxt.append(child)
        beam = sorted(nxt, key=lambda n: (-round(n.score, 6), n.sig)) or beam
    return beam


# --------------------------------------------------------------------------
# Final scoring, verification and the candidates
# --------------------------------------------------------------------------

def _balance(space: Space, node: Node) -> float:
    polys = space.fixed_polys + node.polys
    if not polys:
        return 1.0
    area = sum(p.area for p in polys)
    cx = sum(p.centroid.x * p.area for p in polys) / area
    cy = sum(p.centroid.y * p.area for p in polys) / area
    minx, miny, maxx, maxy = space.ctx.polygon.bounds
    diag = math.hypot(maxx - minx, maxy - miny)
    return round(max(0.0, 1.0 - G.distance((cx, cy), space.centroid) / (0.5 * diag)), 4)


def _seating_crossed(space: Space, node: Node, walk: Walk) -> Optional[float]:
    """1 when the doors stay connected without walking through a seating area (between the sofa's front and its
    TV), else 0; None without a seating group with a TV."""
    occ = None
    for cand in node.cands:
        if cand is None or cand.group != "seating":
            continue
        tv = next((s for s in cand.spots if s.type == "tv_unit"), None)
        if tv is None:
            continue
        a = cand.anchor
        geo = GC.tv_geometry(a.piece(), tv.piece())
        w, d = a.size[0] / 2.0, a.size[1] / 2.0
        if occ is None:
            occ = node.occ.copy()
        paint(occ, space.box_fp(a.center, a.rotation, (-w, w, -d - max(0.0, geo["distance_m"]), -d)))
    if occ is None:
        return None
    return 1.0 if walk.ok(occ, ()) else 0.0


def _circulation(space: Space, node: Node, walk: Walk) -> Optional[float]:
    """The open floor a 0.60 m walkway can use, against the room with its fixed pieces only (a stand-in for the
    circulation term of Merrell et al.: free floor between the doors)."""
    R = space.R
    base = int((R.clearance(R.inside & ~space.fixed_mask) >= walk.sec / 2.0).sum())
    if base == 0:
        return None
    now = int((R.clearance(R.inside & ~node.occ) >= walk.sec / 2.0).sum())
    return round(now / base, 4)


def _final_terms(space: Space, node: Node, walk: Walk) -> dict:
    sums: dict[str, list] = {}
    for cand in node.cands:
        if cand is None:
            continue
        for k, v in cand.terms.items():
            if v is not None:
                sums.setdefault(k, []).append(v)
    terms = {k: round(sum(v) / len(v), 4) for k, v in sorted(sums.items())}
    terms["balance"] = _balance(space, node)
    for name, fn in (("circulation", _circulation), ("seating_crossed", _seating_crossed)):
        value = fn(space, node, walk)
        if value is not None:
            terms[name] = value
    return terms


def _next_number(building: dict, level_id: str) -> int:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in building.get("furniture") or [] for m in [pattern.match(f.get("id", ""))] if m]
    return max(numbers, default=0) + 1


def _piece_dicts(room: dict, node: Node, start: int, levels: list) -> tuple[list[dict], list[dict]]:
    """The candidate's new pieces as furniture dicts (ids from ``start``) and its groups (one per group id: a set's
    members share theirs; a drawn anchor stays the group's anchor)."""
    pieces = []
    groups: dict[str, dict] = {}
    number = start
    for (entry, _cands, _req), cand in zip(levels, node.cands):
        if cand is None:
            continue
        g = groups.setdefault(cand.group_id, {"group_id": cand.group_id, "group": cand.group, "member_ids": [],
                                              "anchor_id": entry.get("anchor_id") if entry.get("drawn") else None,
                                              "option": cand.option})
        sets = GR.load_groups()[cand.group]["layout"] == "set"
        for s in cand.spots:
            pid = f"f_{room['level_id']}_{number:03d}"
            number += 1
            role = "anchor" if (s is cand.anchor and s.existing_id is None and not entry.get("drawn")
                                and not sets and g["anchor_id"] is None) else "partner"
            if role == "anchor":
                g["anchor_id"] = pid
            else:
                g["member_ids"].append(pid)
            pieces.append(_piece_dict(s, room, pid, cand, role))
    for p in pieces:
        p["group"]["anchor_id"] = groups[p["group"]["group_id"]]["anchor_id"]
    return pieces, list(groups.values())


def _piece_dict(s: Spot, room: dict, pid: str, cand: Cand, role: str) -> dict:
    rotation = round(G.normalise_angle(s.rotation), 3)
    f = {"id": pid, "level_id": room["level_id"], "room_id": room["id"], "type": s.type, "type_raw": None,
         "source": "added_by_ai",
         "footprint": {"center": [round(s.center[0], 4), round(s.center[1], 4)],
                       "size": [round(float(s.size[0]), 4), round(float(s.size[1]), 4)], "rotation_deg": rotation},
         "front_deg": round(G.front_direction_deg(rotation), 3), "height": schemas.HEIGHTS.get(s.type), "asset": None,
         "status": "verified", "method": "rule",
         "evidence": [{"file": EVIDENCE_FILE, "method": "derived", "confidence": 0.9, "rule": f"group {cand.group}",
                       "text": f"{s.type} ({s.role}) of the {cand.group} group, option {cand.option}, placed by the "
                               f"group solver"}],
         "group": {"group_id": cand.group_id, "group": cand.group, "role": role, "anchor_id": None},
         "layout": {"against_wall": bool(s.against_wall), "solver_role": s.role, "option": cand.option}}
    if s.shape == "L":
        f.update({"shape": "L", "chaise_side": s.chaise_side, "chaise_depth": float(s.size[1]),
                  "seat_depth": schemas.L_SEAT_DEPTH_M, "chaise_width": schemas.L_CHAISE_WIDTH_M})
    return f


def _violation_key(v: dict) -> tuple:
    m = v.get("metrics") or {}
    return (v["check"], str(v["target"]), str(m.get("part") or m.get("zone") or m.get("side") or m.get("to") or ""),
            v["message"] if v["check"] in ("G9", "G10") and v["target"] == v["room_id"] else "")


def verify(base_building: dict, room_id: str, pieces: list[dict]) -> tuple[list[str], list[dict]]:
    """(hard failures, group violations) of the room with ``pieces`` added: the placer's geometry (inside, overlap,
    doors, windows) of every new piece and every critical or major group-check violation (G14 aside: a drawn
    piece's type is not the solver's) the fixed pieces alone do not cause."""
    trial = copy.deepcopy(base_building)
    trial["furniture"] = list(trial.get("furniture") or []) + pieces
    room = next(r for r in trial["rooms"] if r["id"] == room_id)
    ctx = placer.room_context(trial, room)
    new_ids = {p["id"] for p in pieces}
    floor = [f for f in trial["furniture"] if f.get("room_id") == room_id and f.get("build") is not False
             and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None
             and f.get("type") != "unknown" and f.get("footprint")]
    plist = [placer.drawn_piece(f, i) for i, f in enumerate(floor)]
    hard = []
    shrunk = ctx.shrunk.buffer(1e-3, join_style="mitre")
    for f, p in zip(floor, plist):
        if f["id"] not in new_ids:
            continue
        poly = p.polygon()
        if not shrunk.contains(poly):
            hard.append(f"{f['id']}: inside_room ({poly.difference(shrunk).area:.3f} m² outside)")
        for g, q in zip(floor, plist):
            if g["id"] == f["id"] or (g["id"] in new_ids and g["id"] < f["id"]):
                continue
            area = poly.intersection(q.polygon()).area
            if area > placer.AREA_EPS:
                hard.append(f"{f['id']}: no_overlap with {g['id']} ({area:.3f} m²)")
        if placer._opening_blocked(p, ctx):
            hard.append(f"{f['id']}: doors_free / windows_free (on a door strip, a door swing or a window band)")
    base_v = {_violation_key(v) for v in GC.check_room(base_building, room_id)}
    after = GC.check_room(trial, room_id)
    hard += [f"{v['check']} {v['target']}: {v['message']}" for v in after
             if _violation_key(v) not in base_v and v["severity"] in ("critical", "major") and v["check"] != "G14"]
    return hard, after


def _fixed_items(building: dict, room_id: str, fixed_ids: set) -> list[dict]:
    """The pieces the solver never moves: drawn pieces (built or not; not a rug outline, not one recorded as not
    furniture) and the ``fixed_ids``; wall-hung pieces stand above the floor."""
    out = []
    not_furniture = {s.get("former_piece_id") for s in building.get("symbols") or [] if s.get("former_piece_id")}
    for f in building.get("furniture") or []:
        if f.get("room_id") != room_id or not f.get("footprint"):
            continue
        if f.get("type") in schemas.MOUNTED_TYPES or f.get("mount_bottom_m") is not None:
            continue
        if f["id"] in not_furniture or f.get("not_furniture") or f.get("inferred_as") == "rug":
            continue
        if f.get("source") == "from_documents" or f["id"] in fixed_ids:
            out.append(f)
    return out


def solve_room(building: dict, room_id: str, program: Optional[dict] = None, *, k: int = 3,
               fixed_ids: Optional[list[str]] = None) -> list[dict]:
    from wenart.furniture import program as PR

    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    if len(room.get("polygon") or []) < 3:
        return []
    prog = program if program is not None else PR.room_program(building, room_id)
    if not prog.get("groups"):
        return []
    fixed = set(fixed_ids or ())
    space = Space(building, room, _fixed_items(building, room_id, fixed))
    budget = {"used": 0, "generate": NODE_BUDGET, "nodes": 0, "expand": NODE_BUDGET, "walks": 0}
    info = _info(space, building, room_id, prog, budget)
    levels = _levels(space, prog, info)
    if not levels:
        return []
    walk = Walk(space)
    beam = _search(space, levels, walk, budget)
    # The base of the verification: the room without its replaceable added pieces.
    base = copy.deepcopy(building)
    kept = sorted(fid for fid in fixed if any(f["id"] == fid for f in base.get("furniture") or []))
    base["furniture"] = [f for f in base.get("furniture") or [] if not (
        f.get("room_id") == room_id and f.get("source") == "added_by_ai" and f["id"] not in fixed
        and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None)]
    start = _next_number(building, room["level_id"])
    weights = GR.weights()
    finals = []
    for node in beam:
        terms = _final_terms(space, node, walk)
        bonus = sum(REQUIRED_BONUS if req else OPTIONAL_BONUS for (_e, _c, req), c in zip(levels, node.cands)
                    if c is not None)
        score = round(bonus + sum(c.local for c in node.cands if c is not None)
                      + sum(weights.get(t, 0.0) * terms[t] for t in ("balance", "circulation", "seating_crossed")
                            if t in terms), 4)
        finals.append((score, node, terms))
    finals.sort(key=lambda x: (-x[0], x[1].sig))
    # A layout that leaves out a required group never stands beside one that places them all.
    req = [sum(1 for (_e, _c, r), c in zip(levels, node.cands) if r and c is not None) for _s, node, _t in finals]
    finals = [f for f, n in zip(finals, req) if n == max(req)]
    out: list[dict] = []
    failed: list[dict] = []
    picked: list = []
    verified: dict = {}
    limit = max(4 * k, 10)
    # Pass 1: the main group (the first placed level) differs; pass 2: any group differs.
    for primary in (True, False):
        for score, node, terms in finals:
            if len(out) >= k or len(verified) >= limit:
                break
            coarse = _coarse_sig(node)
            if any(_similar(coarse, s, primary) for s in picked):
                continue
            if node.sig not in verified:
                pieces, groups = _piece_dicts(room, node, start, levels)
                hard, violations = verify(base, room_id, pieces)
                verified[node.sig] = _candidate(score, terms, pieces, groups, hard, violations, levels, node, kept,
                                                budget)
                if hard:
                    failed.append(verified[node.sig])
            cand = verified[node.sig]
            if cand["hard_failures"] or any(c is cand for c in out):
                continue
            picked.append(coarse)
            out.append(cand)
    if len(out) < k:
        out += failed[:k - len(out)]
    for i, c in enumerate(out):
        c["rank"] = i + 1
    return out


def _coarse_sig(node: Node) -> tuple:
    out = []
    for c in node.cands:
        if c is None:
            out.append(None)
        else:
            a = c.anchor
            out.append((c.option, round(a.rotation) % 360, a.center, a.type))
    return tuple(out)


def _similar(a: tuple, b: tuple, primary: bool = False) -> bool:
    """Two layouts are alike when every group (``primary``: the first group placed in both) has the same option,
    turn and type and an anchor less than ``DIVERSE_M`` apart."""
    pairs = list(zip(a, b))
    if primary:
        pairs = [next(((x, y) for x, y in pairs if x is not None and y is not None), (None, None))]
    for x, y in pairs:
        if (x is None) != (y is None):
            return False
        if x is None:
            continue
        if x[0] != y[0] or x[1] != y[1] or x[3] != y[3] or G.distance(x[2], y[2]) >= DIVERSE_M:
            return False
    return True


def _candidate(score, terms, pieces, groups, hard, violations, levels, node, kept, budget) -> dict:
    not_placed = []
    for (entry, cands, required), c in zip(levels, node.cands):
        if c is None:
            why = "no place passes the checks" if cands else "no candidate position fits the room"
            not_placed.append({"group_id": entry["group_id"], "group": entry["group"], "required": required,
                               "reason": why})
    options = {}
    for c in node.cands:
        if c is not None:
            options.setdefault(c.group_id, c.option)
    return {"rank": 0, "score": score, "terms": terms, "pieces": pieces,
            "groups": [{k: g[k] for k in ("group_id", "group", "anchor_id", "member_ids")} for g in groups],
            "hard_failures": hard, "group_violations": violations, "options": options,
            "placed": [g["group_id"] for g in groups], "not_placed": not_placed, "kept_ids": list(kept),
            "nodes": {"generated": budget["used"], "expanded": budget["nodes"], "walkway_checks": budget["walks"]}}


def apply_candidate(building: dict, room_id: str, candidate: dict) -> dict:
    out = copy.deepcopy(building)
    room = next((r for r in out.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    kept = set(candidate.get("kept_ids") or [])
    gone = {f["id"] for f in out.get("furniture") or [] if f.get("room_id") == room_id
            and f.get("source") == "added_by_ai" and f["id"] not in kept
            and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None}
    out["furniture"] = [f for f in out.get("furniture") or [] if f["id"] not in gone]
    if gone and out.get("decor"):
        out["decor"] = [d for d in out["decor"] if d.get("host_id") not in gone]
    number = _next_number(out, room["level_id"])
    taken = {f["id"] for f in out["furniture"]}
    ids = {}
    for p in candidate.get("pieces") or []:
        pid = p["id"]
        if pid in taken:
            pid = f"f_{room['level_id']}_{number:03d}"
            number += 1
        ids[p["id"]] = pid
        taken.add(pid)
    for p in candidate.get("pieces") or []:
        q = copy.deepcopy(p)
        q["id"] = ids[p["id"]]
        g = dict(q.get("group") or {})
        if g.get("anchor_id") in ids:
            g["anchor_id"] = ids[g["anchor_id"]]
        g.setdefault("role", "partner")
        q["group"] = g
        out["furniture"].append(q)
    return out
