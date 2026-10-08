"""Openings of the generic plan core (docs/milestone7.md §2.6): wall runs, gaps of three kinds, gap classification.

Real plans leave a gap in the wall where a door, window or doorless opening is, and the gap is not always between
two pieces of one wall: real01's bath and store doors lie between a free wall end and the face of a perpendicular
wall, and its two bedroom doors share one run gap that the end of the wall between the bedrooms splits in two. So:

- **Runs**: wall rectangles on one axis line (centre-line offset <= 20 mm, thickness +- 30 mm). Two kinds of odd
  pieces a wall mask gives (real01's photo, P7) are handled first, each logged (``kind "wall_piece"``) with a note:
  a **fused strip** (``join_fused_strips``: a door leaf filled into the mask along a wall face, one face flush, <= a
  leaf's width out, a door swing hinged at it, the strip as long as its leaf) joins its run with the run's faces;
  an **end cap** (``end_caps``: a piece shorter than its thickness at the end of a longer wall, a door frame or a
  nub) is no wall end: no gap is cast from or to it and it keeps no end from being free.
- **Gaps**, all classified the same way:
  (a) *run gap* between consecutive pieces of a run;
  (c) a run gap holding the end of a perpendicular wall inside the run band is *split* at that wall;
  (b) *end gap* from a free wall end (no wall within 50 mm of its end face) along its axis to the first wall face
      hit within 3.0 m.
  Width g < 0.25 m -> closed (warning); 0.25-3.0 m -> classified; > 3.0 m -> open (topology decides).
- **Classifier** (strokes in the gap grown by 0.35 m on both faces; the zone is for classification only):
  *door* = an arc hinged within 0.08 m of a gap end (or inside the wall band at the gap end), radius g +- 12 %,
  sweep 60-100 deg (or two arcs of radius g/2 hinged at both ends), with an optional leaf (a thin shape <= 60 mm
  wide starting within 0.10 m of the hinge, 0.85-1.05 r long, along the arc's start or end radius); *window* = >= 2
  straight strokes parallel to the wall inside the band spanning >= 80 % of g; *doorless* = nothing in the band and
  no door-like arc (hinged within the zone of a gap end, radius 0.4-1.5 g; furniture that is only in the zone does
  not count) (``unverified`` in an exterior wall: "possible undrawn door or window"); anything else is an unverified
  ``opening`` with ``type_raw "unclassified gap content"``.
- A run gap closes inside its run (the run becomes one ``WallItem``); an end gap holding a door or window extends
  the free-end wall to the hit face (evidence method ``derived``); an empty end gap is only logged as a separator
  candidate for ``topology.separators``.
- An opening owns its arc, leaf, hinge pin and the strokes entirely within the gap +- 0.10 m along the wall and inside
  the wall band (faces +- 20 mm) across it (jamb frames, window lines); ``symbols.furniture`` drops exactly those.
- Continuous-wall symbols (the synthetic convention and raster double-line walls) keep working: an arc + leaf
  hinged inside a wall band or within 0.08 m of a face (the end-point rule of ``pdf_extract._door_from_arc``: the leaf
  runs from the hinge to one arc end, the other arc end lies one radius from the hinge; a leaf drawn as a thin
  rectangle passes the classifier's leaf rule instead), radius 0.6-1.2 m, is a door cut into that wall; >= 3
  parallel strokes inside a wall band (one strictly inside it) over >= 0.4 m are a window, and so are >= 2 strictly
  inside it (walls drawn as face lines: the faces are the wall primitive, not strokes here; docs/milestone10.md
  §3.1 item 11).
- Walls drawn as face lines (real02) put two walls of one axis line far apart with perpendicular walls crossing the
  gap between them (the bedroom walls of a semi-detached pair, a corridor and a bathroom between them): a run gap
  that perpendicular walls split is one wall with openings only when every part holds a door or window symbol (or
  is < 0.25 m); a part that is empty or unclassified makes all parts ``open`` (no wall across), and the free ends
  cast their own end gaps.

Everything is in page metres (y up). Walls at other angles than the plan's dominant pair pass through untouched.
"""
from __future__ import annotations

import dataclasses
import math
import statistics
from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.strtree import STRtree

from wenart import building as B
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import DOOR_SWING_PROBE, OpeningItem, WallItem

RUN_OFFSET_M = 0.02
RUN_THICKNESS_M = 0.03
FREE_END_M = 0.05
GAP_MIN_M = 0.25
GAP_MAX_M = 3.0
GAP_IGNORE_M = 0.005
ZONE_M = 0.35
DOOR_LIKE_RADIUS = (0.4, 1.5)  # x gap width: an arc in the zone that keeps a gap from being doorless
BAND_SLACK_M = 0.02
HINGE_M = 0.08
RADIUS_TOL = 0.12
SWEEP_DEG = (60.0, 100.0)
LEAF_WIDTH_M = 0.06
FUSED_STRIP_M = LEAF_WIDTH_M       # a door leaf fused along a wall face in the mask is at most a leaf wide ...
RASTER_EDGE_PX = 1.5               # ... plus the raster mask's edge precision (core.RASTER_JOINT_PX), in pixels
LEAF_CORRIDOR_M = 0.09
LEAF_START_M = 0.10
LEAF_LENGTH = (0.85, 1.05)
WINDOW_COVER = 0.8
WINDOW_ANGLE_DEG = 1.0
OWN_MARGIN_M = 0.10
CONTINUOUS_RADIUS_M = (0.6, 1.2)
CONTINUOUS_WINDOW_M = 0.4
END_POINT_TOL_M = 0.02
AXIS_TOL_DEG = 3.0

DOOR_HEIGHT_M = 2.10
WINDOW_SILL_M = 0.90
WINDOW_HEIGHT_M = 1.20
CONF_DOOR_LEAF, CONF_DOOR, CONF_WINDOW, CONF_DOORLESS = 0.95, 0.85, 0.9, 0.8
CONF_RASTER = 0.7


# --------------------------------------------------------------------------
# Frame and pieces
# --------------------------------------------------------------------------

def _rot(p, deg: float) -> tuple[float, float]:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def dominant_angle(walls: list[WallItem]) -> float:
    """Length-weighted dominant wall direction mod 90, in (-45, 45] deg."""
    bins: dict[int, float] = {}
    for w in walls:
        length = math.dist(w.start, w.end)
        if length <= 0:
            continue
        ang = math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 90.0
        k = int(round(ang * 2.0)) % 180
        bins[k] = bins.get(k, 0.0) + length
    if not bins:
        return 0.0
    k = max(bins, key=bins.get)
    ang = k / 2.0
    return ang - 90.0 if ang > 45.0 else ang


@dataclass
class Piece:
    """A wall rectangle in the plan's aligned frame (rotated by -theta)."""
    k: int                      # index into the input walls
    axis: str                   # "h": along x, "v": along y (aligned frame)
    c: float                    # centre-line offset (y for h, x for v)
    t: float                    # thickness
    a: float                    # extent along the axis, a < b
    b: float
    wall: WallItem
    run: int = -1

    def rect(self) -> tuple[float, float, float, float]:
        h = self.t / 2.0
        if self.axis == "h":
            return (self.a, self.c - h, self.b, self.c + h)
        return (self.c - h, self.a, self.c + h, self.b)

    def end_face(self, which: str) -> tuple[tuple[float, float], tuple[float, float]]:
        pos = self.a if which == "start" else self.b
        h = self.t / 2.0
        if self.axis == "h":
            return ((pos, self.c - h), (pos, self.c + h))
        return ((self.c - h, pos), (self.c + h, pos))


def pieces_of(walls: list[WallItem], theta: float) -> tuple[list[Piece], list[int]]:
    """Axis pieces in the aligned frame and the indices of walls at other angles."""
    out, others = [], []
    for k, w in enumerate(walls):
        s, e = _rot(w.start, -theta), _rot(w.end, -theta)
        ang = math.degrees(math.atan2(e[1] - s[1], e[0] - s[0])) % 180.0
        if min(ang, 180.0 - ang) <= AXIS_TOL_DEG:
            a, b = sorted((s[0], e[0]))
            out.append(Piece(k, "h", (s[1] + e[1]) / 2.0, w.thickness, a, b, w))
        elif abs(ang - 90.0) <= AXIS_TOL_DEG:
            a, b = sorted((s[1], e[1]))
            out.append(Piece(k, "v", (s[0] + e[0]) / 2.0, w.thickness, a, b, w))
        else:
            others.append(k)
    return out, others


def group_runs(pieces: list[Piece]) -> list[list[Piece]]:
    """Pieces on one axis line (offset <= 20 mm, thickness +- 30 mm), sorted along the axis."""
    runs: list[dict] = []
    for p in sorted(pieces, key=lambda p: (p.axis, p.c, p.a)):
        for run in runs:
            if run["axis"] == p.axis and abs(run["c"] - p.c) <= RUN_OFFSET_M and abs(run["t"] - p.t) <= RUN_THICKNESS_M:
                run["pieces"].append(p)
                total = sum(q.b - q.a for q in run["pieces"])
                run["c"] = sum(q.c * (q.b - q.a) for q in run["pieces"]) / total if total > 0 else p.c
                break
        else:
            runs.append({"axis": p.axis, "c": p.c, "t": p.t, "pieces": [p]})
    out = []
    for i, run in enumerate(runs):
        ps = sorted(run["pieces"], key=lambda q: q.a)
        for q in ps:
            q.run = i
        out.append(ps)
    return out


def _touching(p: Piece, others) -> tuple[list[Piece], list[Piece]]:
    """The pieces of ``others`` on p's axis whose end face p's start (``before``) or end (``after``) touches."""
    before = [q for q in others if q is not p and q.axis == p.axis and abs(q.b - p.a) <= GAP_IGNORE_M]
    after = [q for q in others if q is not p and q.axis == p.axis and abs(q.a - p.b) <= GAP_IGNORE_M]
    return before, after


def _outside(p: Piece, touching: list[Piece]) -> tuple[float, float, float, float]:
    """``(out_lo, out_hi, lo, hi)``: how far p's faces lie outside the (mean) faces ``lo``/``hi`` of the touching
    pieces (> 0 outside, < 0 inside)."""
    lo = statistics.mean(q.c - q.t / 2.0 for q in touching)
    hi = statistics.mean(q.c + q.t / 2.0 for q in touching)
    return lo - (p.c - p.t / 2.0), (p.c + p.t / 2.0) - hi, lo, hi


def end_caps(runs: list[list[Piece]], edge_m: float = 0.0) -> tuple[set[int], list[dict]]:
    """Pieces that are a wall end's frame or nub, not a wall end of their own: shorter than their own thickness,
    touching on one side only the end face of a longer piece on their axis that is not in their run (another
    cross-section), their band overlapping that piece's band by >= half their thickness and lying outside it by <=
    ``FUSED_STRIP_M`` + ``edge_m``, and in a run of such pieces only (alone, or the two frames of one opening: a short
    junction piece of a wall run is no cap). A drawn door frame (a jamb nub inside the opening) or a ragged wall end
    gives such pieces in a raster mask (real01's photo: a 0.04 m piece 0.14 m thick at the end of the kitchen-store
    wall kept that wall's end from being free, so the store door's end gap was never cast and its arc became
    furniture; the entrance door's frames, 0.03-0.04 m long inside its run gap, sit there the same way).

    An end cap is no wall end: it neither keeps the end of the wall it caps from being free nor is a free end itself,
    no gap is cast from it or stops at it, it splits no run gap and is in no run (the frame belongs to the opening,
    whose width runs from wall end to wall end as on vector pages). It stays in the walls as drawn. ``runs`` come
    from ``group_runs``. Returns ``(ids, log)``: the ``id()`` of the cap pieces and one log entry each (``kind
    "wall_piece"``, ``how "end_cap"``, with a note)."""
    found: dict[int, tuple[Piece, Piece]] = {}
    pieces = [q for run in runs for q in run]
    for p in pieces:
        length = p.b - p.a
        if length >= p.t:
            continue
        before, after = _touching(p, [q for q in pieces if q.run != p.run])
        touching = before + after
        if bool(before) == bool(after) or max(q.b - q.a for q in touching) <= length:
            continue
        out_lo, out_hi, lo, hi = _outside(p, touching)
        if max(out_lo, out_hi) > FUSED_STRIP_M + edge_m or \
                min(hi, p.c + p.t / 2.0) - max(lo, p.c - p.t / 2.0) < 0.5 * p.t:
            continue
        found[id(p)] = (p, touching[0])
    caps: set[int] = set()
    log: list[dict] = []
    for run in runs:
        if not all(id(q) in found for q in run):
            continue
        for p in run:
            q = found[id(p)][1]
            caps.add(id(p))
            log.append({"kind": "wall_piece", "how": "end_cap", "piece": p.k, "of": q.k,
                        "length": round(p.b - p.a, 4), "thickness": round(p.t, 4),
                        "note": f"a {p.b - p.a:.3f} m piece ({p.t:.3f} m thick) at the end of a {q.t:.3f} m wall is "
                                f"a frame or nub of that wall's end, not a wall end of its own (no gap is cast from "
                                f"or to it)"})
    return caps, log


def join_fused_strips(runs: list[list[Piece]], index: Optional["StrokeIndex"] = None,
                      edge_m: float = 0.0) -> tuple[list[list[Piece]], list[dict]]:
    """A door leaf drawn against a wall face and filled into the wall mask with it makes that stretch of the wall
    thicker on one face, so it leaves its run and the run sees a 'gap' there (real01's photo and scan: the bath
    door's leaf along the drawing room's west wall, 0.05 m; on the photo that gap took the bath door's arc, and the
    end gap of the bath wall stopped 0.05 m short of the wall's face). Such a piece joins the run, with the run's
    centre line and thickness, on this evidence (all needed):

    - it is alone on its axis line and lies between two pieces of the run (touching their end faces);
    - one face is flush with theirs (<= ``RUN_OFFSET_M``), the other lies outside by more than that and by <=
      ``FUSED_STRIP_M`` (a leaf's width) + ``edge_m`` (the raster mask's edge precision; 0 on vector pages);
    - a door swing explains the strip (``_leaf_swing``: an arc hinged at the piece, swinging on the strip's side,
      the strip as long as its leaf).

    The strip is never counted as wall: the run's faces stand. Nothing is silently changed: each join is a log entry
    (``kind "wall_piece"``, ``how "fused_strip"``) with the piece's own thickness and a note that the merged wall's
    evidence carries too. Returns ``(runs, log)``; runs are renumbered."""
    log: list[dict] = []
    for p in sorted((run[0] for run in runs if len(run) == 1), key=lambda p: (p.axis, p.c, p.a)):
        length = p.b - p.a
        if length > GAP_MAX_M:
            continue
        for ri, run in enumerate(runs):
            if len(run) < 2 or run[0].axis != p.axis:
                continue
            before, after = _touching(p, run)
            if not before or not after:
                continue
            out_lo, out_hi, _, _ = _outside(p, before + after)
            strip = max(out_lo, out_hi)
            if min(out_lo, out_hi) < -RUN_OFFSET_M or min(abs(out_lo), abs(out_hi)) > RUN_OFFSET_M or \
                    not RUN_OFFSET_M < strip <= FUSED_STRIP_M + edge_m:
                continue
            swing = _leaf_swing(p, 1.0 if out_hi > out_lo else -1.0, index)
            if swing is None:
                continue
            c, t = _run_c(run), _run_t(run)
            arc_id = swing[0].st.id
            log.append({"kind": "wall_piece", "how": "fused_strip", "piece": p.k, "length": round(length, 4),
                        "thickness": round(p.t, 4), "run_thickness": round(t, 4), "strip": round(strip, 4),
                        "arc": arc_id,
                        "note": f"a {strip:.3f} m strip along one face over {length:.2f} m, where the leaf of door "
                                f"swing {arc_id} rests (a leaf fused to the wall face in the wall mask), is not "
                                f"counted as wall: thickness {t:.3f} m as the rest of the run, not {p.t:.3f} m"})
            p.c, p.t = c, t
            run.append(p)
            run.sort(key=lambda q: q.a)
            runs = [r for r in runs if not (len(r) == 1 and r[0] is p)]
            break
    for i, run in enumerate(runs):
        for q in run:
            q.run = i
    return runs, log


def _leaf_swing(p: Piece, side: float, index: Optional["StrokeIndex"]):
    """``(item, arc)`` of a door swing whose leaf rests along piece ``p`` on its ``side`` (+1: towards larger across
    values), or None: an arc of ``SWEEP_DEG`` hinged within ``HINGE_M`` of the piece's rectangle, its middle on that
    side of the piece's centre line, the piece starting within ``LEAF_START_M`` of the hinge and running on for
    ``LEAF_LENGTH`` x r (+ ``LEAF_START_M``: the hinge pin), the leaf rule of ``_leaf``."""
    if index is None:
        return None
    x0, y0, x1, y1 = p.rect()
    reach = HINGE_M + (p.b - p.a) / LEAF_LENGTH[0]                # the swing lies within one radius of the hinge
    best = None
    for it, arc in _arcs_in(index.query((x0 - reach, y0 - reach, x1 + reach, y1 + reach))):
        hx, hy = arc["center"]
        if not SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1] or \
                not (x0 - HINGE_M <= hx <= x1 + HINGE_M and y0 - HINGE_M <= hy <= y1 + HINGE_M):
            continue
        mid = _arc_mid(arc)
        if ((mid[1] if p.axis == "h" else mid[0]) - p.c) * side <= 0:
            continue
        along = hx if p.axis == "h" else hy
        near, far = sorted((abs(along - p.a), abs(p.b - along)))
        r = arc["radius"]
        if near <= LEAF_START_M and LEAF_LENGTH[0] * r <= far <= LEAF_LENGTH[1] * r + LEAF_START_M \
                and (best is None or near < best[0]):
            best = (near, it, arc)
    return None if best is None else (best[1], best[2])


# --------------------------------------------------------------------------
# Strokes in the aligned frame
# --------------------------------------------------------------------------

@dataclass
class _S:
    st: Stroke
    pts: list[tuple[float, float]]           # aligned frame
    geom: object                             # shapely geometry (aligned frame)


class StrokeIndex:
    """The page's strokes in the aligned frame with an STRtree for box queries."""

    def __init__(self, strokes: list[Stroke], theta: float):
        self.items: list[_S] = []
        for st in strokes:
            if not st.pts:
                continue
            pts = [_rot(p, -theta) for p in st.pts]
            if st.closed and len(pts) > 2:
                ring = pts + [pts[0]]
                geom = LineString(ring)
            elif len(set(pts)) > 1:
                geom = LineString(pts)
            else:
                geom = Point(pts[0])
            self.items.append(_S(st, pts, geom))
        self.tree = STRtree([it.geom for it in self.items]) if self.items else None

    def query(self, rect, predicate: str = "intersects") -> list[_S]:
        if self.tree is None:
            return []
        g = sbox(*rect)
        return [self.items[int(j)] for j in self.tree.query(g, predicate=predicate)]


def arc_of(pts: list[tuple[float, float]]) -> Optional[dict]:
    """Circle fit of a flattened curve: {"center", "radius", "sweep", "start", "end"} or None (residual > 1 % r)."""
    if len(pts) < 4:
        return None
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    u = [p[0] - mx for p in pts]
    v = [p[1] - my for p in pts]
    suu = sum(a * a for a in u)
    svv = sum(b * b for b in v)
    suv = sum(a * b for a, b in zip(u, v))
    det = suu * svv - suv * suv
    if abs(det) < 1e-18:
        return None
    r1 = 0.5 * (sum(a ** 3 for a in u) + sum(a * b * b for a, b in zip(u, v)))
    r2 = 0.5 * (sum(b ** 3 for b in v) + sum(b * a * a for a, b in zip(u, v)))
    uc = (r1 * svv - r2 * suv) / det
    vc = (r2 * suu - r1 * suv) / det
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    cx, cy = uc + mx, vc + my
    if r <= 0 or max(abs(math.dist(p, (cx, cy)) - r) for p in pts) > 0.01 * r:
        return None
    sweep = 0.0
    prev = math.atan2(pts[0][1] - cy, pts[0][0] - cx)
    for p in pts[1:]:
        cur = math.atan2(p[1] - cy, p[0] - cx)
        d = (cur - prev + math.pi) % (2 * math.pi) - math.pi
        sweep += d
        prev = cur
    return {"center": (cx, cy), "radius": r, "sweep": abs(math.degrees(sweep)), "start": pts[0], "end": pts[-1]}


# --------------------------------------------------------------------------
# Gap classification
# --------------------------------------------------------------------------

@dataclass
class Gap:
    kind: str                     # run | split | end
    axis: str
    c: float
    t: float
    a: float
    b: float
    pieces: list[Piece]           # the pieces at the gap ends (end gaps: the free-end piece first)
    free: Optional[tuple[Piece, str]] = None     # end gaps: (piece, "start" | "end")
    hit: Optional[Piece] = None                  # end gaps: the wall hit
    cls: str = ""                 # door | window | opening | unclassified | empty | closed | open
    found: dict = field(default_factory=dict)

    @property
    def width(self) -> float:
        return self.b - self.a

    def rect(self, grow_face: float = 0.0, grow_along: float = 0.0) -> tuple[float, float, float, float]:
        h = self.t / 2.0 + grow_face
        if self.axis == "h":
            return (self.a - grow_along, self.c - h, self.b + grow_along, self.c + h)
        return (self.c - h, self.a - grow_along, self.c + h, self.b + grow_along)

    def along(self, p) -> float:
        return p[0] if self.axis == "h" else p[1]

    def across(self, p) -> float:
        return p[1] - self.c if self.axis == "h" else p[0] - self.c

    def point(self, along: float, across: float = 0.0) -> tuple[float, float]:
        return (along, self.c + across) if self.axis == "h" else (self.c + across, along)


def _jamb_distance(g: Gap, p, end: float) -> float:
    """Distance from p to the jamb segment (across the band) at ``end``."""
    q0, q1 = g.point(end, -g.t / 2.0), g.point(end, g.t / 2.0)
    return LineString([q0, q1]).distance(Point(p))


def _near_gap_end(g: Gap, p) -> Optional[float]:
    for end in (g.a, g.b):
        if _jamb_distance(g, p, end) <= HINGE_M:
            return end
        if abs(g.across(p)) <= g.t / 2.0 and abs(g.along(p) - end) <= HINGE_M:
            return end
    return None


def _leaf(arc: dict, idx_items: list[_S], used: set) -> Optional[list[_S]]:
    """Strokes forming a thin leaf from the hinge along the arc's start or end radius: their minimum rotated
    rectangle is <= 60 mm wide, 0.85-1.05 r long, starts within 0.10 m of the hinge and runs within 10 deg of the
    radius (the arc ends at the leaf's outer corner, so the leaf is a few degrees off the hinge-to-end radius)."""
    from shapely.geometry import MultiPoint

    hinge, r = arc["center"], arc["radius"]
    for tip in (arc["end"], arc["start"]):
        dx, dy = tip[0] - hinge[0], tip[1] - hinge[1]
        n = math.hypot(dx, dy)
        if n <= 0:
            continue
        ux, uy = dx / n, dy / n
        parts = []
        for it in idx_items:
            if id(it) in used:
                continue
            alongs = []
            ok = True
            for p in it.pts:
                qx, qy = p[0] - hinge[0], p[1] - hinge[1]
                al = qx * ux + qy * uy
                ac = -qx * uy + qy * ux
                if al < -LEAF_START_M or al > LEAF_LENGTH[1] * r + 0.02 or abs(ac) > LEAF_CORRIDOR_M:
                    ok = False
                    break
                alongs.append(al)
            if ok:
                parts.append((it, min(alongs), max(alongs)))
        body = [p for p in parts if p[2] - p[1] >= 0.5 * r]
        if not body:
            continue
        pts = [q for p in body for q in p[0].pts]
        rect = MultiPoint(pts).minimum_rotated_rectangle
        if rect.geom_type != "Polygon":
            continue
        c = list(rect.exterior.coords)
        e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
        e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
        long_e, short_len = (e1, math.hypot(*e2)) if math.hypot(*e1) >= math.hypot(*e2) else (e2, math.hypot(*e1))
        long_len = math.hypot(*long_e)
        off = math.degrees(math.acos(min(1.0, abs(long_e[0] * ux + long_e[1] * uy) / max(long_len, 1e-12))))
        lo = min(p[1] for p in body)
        if lo > LEAF_START_M or short_len > LEAF_WIDTH_M or off > 10.0 or \
                not LEAF_LENGTH[0] * r <= long_len <= LEAF_LENGTH[1] * r:
            continue
        pins = [p for p in parts if p not in body and p[2] <= LEAF_START_M + 0.03]
        return [p[0] for p in body + pins]
    return None


def _arcs_in(items: list[_S]) -> list[tuple[_S, dict]]:
    out = []
    for it in items:
        if it.st.kind not in ("arc", "curve", "polyline", "circle") or len(it.pts) < 4:
            continue
        if it.st.arc is None and it.st.kind == "polyline" and len(it.pts) < 8:
            # A few-vertex polyline the adapter did not call an arc (a square chair: 4 corners fit a circle
            # exactly) is not an arc.
            continue
        arc = arc_of(it.pts)
        if arc is not None and arc["sweep"] >= 30.0:
            out.append((it, arc))
    return out


def classify_gap(g: Gap, index: StrokeIndex, owned_global: set) -> None:
    """Fill ``g.cls`` and ``g.found`` (door/window/doorless/unclassified, see the module docstring)."""
    width = g.width
    zone = index.query(g.rect(grow_face=ZONE_M))
    zone = [it for it in zone if it.st.id not in owned_global]
    arcs = _arcs_in(zone)
    # Door: one arc hinged at a gap end with r = g, or two arcs of g/2 hinged at both ends.
    singles, halves = [], []
    for it, arc in arcs:
        end = _near_gap_end(g, arc["center"])
        if end is None or not SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]:
            continue
        if abs(arc["radius"] - width) <= RADIUS_TOL * width:
            singles.append((it, arc, end))
        elif abs(arc["radius"] - width / 2.0) <= RADIUS_TOL * width / 2.0:
            halves.append((it, arc, end))
    door = None
    if singles:
        it, arc, end = min(singles, key=lambda x: abs(x[1]["radius"] - width))
        door = [(it, arc, end)]
    elif len({h[2] for h in halves}) == 2:
        door = [min((h for h in halves if h[2] == e), key=lambda x: abs(x[1]["radius"] - width / 2.0))
                for e in (g.a, g.b)]
    if door:
        used: set = set()
        leaves, parts = [], []
        for it, arc, end in door:
            used.add(id(it))
            leaf = _leaf(arc, zone, used)
            if leaf:
                used.update(id(x) for x in leaf)
                leaves.append(leaf)
            parts.append((it, arc, end, leaf))
        mid = parts[0][1]
        swing_across = statistics.mean(g.across(_arc_mid(p[1])) for p in parts)
        g.cls = "door"
        g.found = {"arcs": [p[0] for p in parts], "arc": [p[1] for p in parts],
                   "hinges": [p[1]["center"] for p in parts], "leaves": [x for lf in leaves for x in lf],
                   "leaf": len(leaves) == len(parts), "swing": 1.0 if swing_across >= 0 else -1.0,
                   "radius": mid["radius"], "double": len(parts) == 2}
        return
    # Window: >= 2 strokes parallel to the wall in the band, each spanning >= 80 % of the gap.
    band = g.rect(grow_face=BAND_SLACK_M)
    band_items = [it for it in zone if _inside_rect_part(it, band)]
    parallel = []
    for it in band_items:
        for p, q in zip(it.pts, it.pts[1:] + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])):
            if not _parallel(p, q, g.axis):
                continue
            off = g.across(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
            if abs(off) > g.t / 2.0 + BAND_SLACK_M:
                continue
            lo, hi = sorted((g.along(p), g.along(q)))
            cover = min(hi, g.b) - max(lo, g.a)
            if cover >= WINDOW_COVER * width:
                parallel.append((it, round(off, 3)))
    if len({off for _, off in parallel}) >= 2:
        g.cls = "window"
        g.found = {"lines": list({id(it): it for it, _ in parallel}.values())}
        return
    # Doorless: nothing in the band (the jamb faces at the gap ends do not count) and no door-like arc. Strokes
    # that are only in the classification zone (a chair or a round table beside an open plan) do not count; an
    # arc there counts when it could be a mis-sized door swing: hinged within the zone of a gap end, radius
    # 0.4-1.5 g, not a full circle.
    inner = g.rect(grow_face=BAND_SLACK_M)
    shrink = 0.01
    inner = (inner[0] + shrink, inner[1], inner[2] - shrink, inner[3]) if g.axis == "h" else \
        (inner[0], inner[1] + shrink, inner[2], inner[3] - shrink)
    content = [it for it in index.query(inner) if it.st.id not in owned_global and it.geom.length > 0.005]
    swings = [it for it, arc in arcs if _door_like(g, arc)]
    if not content and not swings:
        g.cls = "empty"
        return
    g.cls = "unclassified"
    g.found = {"content": content + [it for it in swings if it not in content]}


def _door_like(g: Gap, arc: dict) -> bool:
    """An arc that may be a door swing of this gap, drawn off the door rule's tolerances."""
    width = g.width
    if not DOOR_LIKE_RADIUS[0] * width <= arc["radius"] <= DOOR_LIKE_RADIUS[1] * width or arc["sweep"] >= 300.0:
        return False
    return min(_jamb_distance(g, arc["center"], end) for end in (g.a, g.b)) <= ZONE_M


def _arc_mid(arc: dict) -> tuple[float, float]:
    cx, cy = arc["center"]
    a0 = math.atan2(arc["start"][1] - cy, arc["start"][0] - cx)
    a1 = math.atan2(arc["end"][1] - cy, arc["end"][0] - cx)
    d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    am = a0 + d / 2.0
    return (cx + arc["radius"] * math.cos(am), cy + arc["radius"] * math.sin(am))


def _parallel(p, q, axis: str) -> bool:
    if math.dist(p, q) <= 1e-9:
        return False
    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0
    target = 0.0 if axis == "h" else 90.0
    d = abs(ang - target) % 180.0
    return min(d, 180.0 - d) <= WINDOW_ANGLE_DEG


def _inside_rect_part(it: _S, rect) -> bool:
    return it.geom.intersects(sbox(*rect))


# --------------------------------------------------------------------------
# Main entry
# --------------------------------------------------------------------------

def gaps_and_openings(walls: list[WallItem], strokes_m: list[Stroke], file_rel: str, page_no: int,
                      units_to_m: Optional[float] = None
                      ) -> tuple[list[WallItem], list[OpeningItem], list[dict], set[str]]:
    """Merge wall runs, find and classify gaps, extend free-end walls that host a drawn door or window.

    ``strokes_m`` are the page's strokes in page metres **without** the wall primitives (hatch lines, fills).
    Returns ``(walls, openings, gap_log, owned)``: the merged/extended walls (page metres), the openings on them
    (page metres; ``box`` in page units when ``units_to_m`` is given), one log dict per gap and free end, and the
    ids of the strokes the openings own.
    """
    theta = dominant_angle(walls)
    pieces, others = pieces_of(walls, theta)
    index = StrokeIndex(strokes_m, theta)
    raster = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)
    edge_m = RASTER_EDGE_PX * units_to_m if raster and units_to_m else 0.0
    runs = group_runs(pieces)
    order = {id(q): q.run for q in pieces}
    caps, cap_log = end_caps(runs, edge_m)
    ends = [p for p in pieces if id(p) not in caps]    # the pieces that end walls (frames and nubs do not)
    runs = [r for r in ([q for q in run if id(q) not in caps] for run in runs) if r]
    runs, piece_log = join_fused_strips(runs, index, edge_m)
    piece_log += cap_log
    join_notes = {e["piece"]: e["note"] for e in piece_log}
    # An end cap stays a wall of its own, in its place among the runs (the output walls keep their order).
    runs = sorted(runs + [[p] for p in pieces if id(p) in caps],
                  key=lambda r: (min(order[id(q)] for q in r), r[0].a))
    for i, run in enumerate(runs):
        for q in run:
            q.run = i
    ctx = _Ctx(file_rel, page_no, units_to_m, theta, raster)
    owned: set[str] = set()
    gaps: list[Gap] = []
    merge_after: dict[int, set[int]] = {}        # run -> positions i where pieces i and i+1 join

    # (a) + (c): run gaps, split at perpendicular walls inside the band.
    for ri, run in enumerate(runs):
        merge_after[ri] = set()
        for i in range(len(run) - 1):
            p, q = run[i], run[i + 1]
            if q.a <= p.b + GAP_IGNORE_M:
                merge_after[ri].add(i)
                continue
            subs = _split(p, q, ends)
            if any(b - a > GAP_MAX_M for a, b in subs):
                for a, b in subs:
                    gaps.append(Gap("run" if len(subs) == 1 else "split", p.axis, p.c, _run_t(run), a, b, [p, q],
                                    cls="open"))
                continue
            trial = set(owned)
            found = []
            for a, b in subs:
                g = Gap("run" if len(subs) == 1 else "split", p.axis, _run_c(run), _run_t(run), a, b, [p, q])
                if g.width < GAP_MIN_M:
                    g.cls = "closed"
                else:
                    classify_gap(g, index, trial)
                    _own(g, index, trial)
                found.append(g)
            if len(subs) > 1 and any(g.cls in ("empty", "unclassified") for g in found):
                # Perpendicular walls cross the gap and one part holds no door or window symbol: the pieces are two
                # walls on one line (real02: the bedroom walls of both dwellings, the corridor and a bathroom
                # between them), never one wall across; free ends cast their own end gaps (b).
                for g in found:
                    g.found = {"split_reason": "a split part holds no door or window: the pieces are not one wall"}
                    g.cls = "open"
                gaps.extend(found)
                continue
            merge_after[ri].add(i)
            owned.update(trial)
            gaps.extend(found)

    # (b): end gaps from free ends.
    end_log: list[dict] = []
    for p in ends:
        for which in ("start", "end"):
            if not _is_free(p, which, ends):
                continue
            hit = _cast(p, which, ends)
            if hit is None:
                end_log.append({"piece": p, "which": which, "gap": None})
                continue
            q, a, b = hit
            # The same gap as a classified run gap: the run gap holds it (an open run gap does not).
            dup = next((g for g in gaps if g.cls != "open" and g.axis == p.axis
                        and abs(g.c - p.c) <= RUN_OFFSET_M + 0.01
                        and min(g.b, b) - max(g.a, a) >= 0.5 * min(g.width, b - a)), None)
            if dup is not None:
                end_log.append({"piece": p, "which": which, "gap": dup, "same_as_run_gap": True})
                continue
            g = Gap("end", p.axis, p.c, p.t, a, b, [p, q], free=(p, which), hit=q)
            if g.width < GAP_MIN_M:
                g.cls = "closed"
            else:
                classify_gap(g, index, owned)
                if g.cls in ("door", "window"):
                    _own(g, index, owned)
            gaps.append(g)
            end_log.append({"piece": p, "which": which, "gap": g})

    # Extend free-end walls that host a door or window (or close a gap < 0.25 m).
    extended: dict[int, tuple[list[str], str]] = {}
    for g in gaps:
        if g.kind != "end" or g.cls not in ("door", "window", "closed"):
            continue
        p, which = g.free
        if which == "start":
            p.a = g.a
        else:
            p.b = g.b
        ids = [it.st.id for it in g.found.get("arcs", []) + g.found.get("leaves", []) + g.found.get("lines", [])]
        reason = {"door": "extended to host the drawn door", "window": "extended to host the drawn window",
                  "closed": f"extended over a {g.width:.3f} m gap (< {GAP_MIN_M} m, closed)"}[g.cls]
        old_ids, old_reason = extended.get(p.k, ([], ""))
        extended[p.k] = (old_ids + ids, (old_reason + "; " if old_reason else "") + reason)

    # Build the output walls: one WallItem per merged run segment, other walls unchanged.
    out_walls: list[WallItem] = []
    piece_out: dict[int, int] = {}
    for ri, run in enumerate(runs):
        seg = [run[0]]
        for i in range(1, len(run) + 1):
            if i < len(run) and (i - 1) in merge_after[ri]:
                seg.append(run[i])
                continue
            out_walls.append(_merged_wall(seg, ctx, extended, join_notes))
            for q in seg:
                piece_out[q.k] = len(out_walls) - 1
            if i < len(run):
                seg = [run[i]]
    for k in others:
        out_walls.append(walls[k])
    _trim_into_bands(out_walls, theta)

    exterior = _exterior_test(out_walls)
    openings: list[OpeningItem] = []
    log: list[dict] = []
    gap_pos: dict[int, int] = {}
    for g in gaps:
        entry = _log_entry(g, theta, piece_out)
        if g.cls in ("door", "window") or (g.kind != "end" and g.cls in ("empty", "unclassified")):
            openings.append(_opening(g, ctx, exterior))
            entry["opening"] = len(openings) - 1
        if g.cls == "closed":
            entry["warning"] = f"gap of {g.width:.3f} m < {GAP_MIN_M} m closed"
        gap_pos[id(g)] = len(log)
        log.append(entry)
    for e in end_log:
        p, which = e["piece"], e["which"]
        face = p.end_face(which)
        mid = ((face[0][0] + face[1][0]) / 2, (face[0][1] + face[1][1]) / 2)
        d = -1.0 if which == "start" else 1.0
        direction = (d, 0.0) if p.axis == "h" else (0.0, d)
        g = e["gap"]
        log.append({"kind": "free_end", "wall": piece_out.get(p.k), "end": which,
                    "point": _out(mid, theta), "face": [_out(face[0], theta), _out(face[1], theta)],
                    "direction": [round(v, 6) for v in _rot(direction, theta)], "thickness": round(p.t, 4),
                    "gap_class": (g.cls if g is not None else "none"),
                    "gap": (None if g is None else gap_pos.get(id(g))),
                    "same_as_run_gap": bool(e.get("same_as_run_gap"))})
    for e in piece_log:
        entry = dict(e, wall=piece_out.get(e["piece"]))
        entry["input_wall"] = entry.pop("piece")
        if "of" in entry:
            entry["of"] = piece_out.get(entry["of"])
        log.append(entry)

    # Continuous-wall symbols (synthetic convention, raster double-line walls).
    cont_doors, cont_windows = _continuous_symbols(out_walls, index, owned, theta, ctx, openings)
    openings.extend(cont_doors)
    openings.extend(cont_windows)
    for o in cont_doors + cont_windows:
        log.append({"kind": "continuous", "class": o.kind, "center": list(o.center), "width": o.width,
                    "entity": o.entity})
    return out_walls, openings, log, owned


@dataclass
class _Ctx:
    file_rel: str
    page_no: int
    units_to_m: Optional[float]
    theta: float
    raster: bool

    def evidence(self, method: str, confidence: float, entity: str, note: Optional[str] = None,
                 box_units: Optional[list] = None) -> dict:
        if self.raster and method == "vector":
            method, confidence = "raster", min(confidence, CONF_RASTER)
        ev = B.evidence(self.file_rel, method, round(confidence, 3), page=self.page_no, entity=entity,
                        pixel_box=box_units if (method == "raster" and box_units) else None)
        if note:
            ev["note"] = note
        return ev

    def box(self, pts_m) -> list[float]:
        xs = [p[0] for p in pts_m]
        ys = [p[1] for p in pts_m]
        bx = [min(xs), min(ys), max(xs), max(ys)]
        if self.units_to_m:
            bx = [v / self.units_to_m for v in bx]
        return [round(v, 3) for v in bx]


def _out(p, theta: float) -> list[float]:
    q = _rot(p, theta)
    return [round(q[0], 4), round(q[1], 4)]


def _run_c(run: list[Piece]) -> float:
    total = sum(q.b - q.a for q in run)
    return sum(q.c * (q.b - q.a) for q in run) / total if total > 0 else run[0].c


def _run_t(run: list[Piece]) -> float:
    return _weighted_median([(q.t, q.b - q.a) for q in run])


def _weighted_median(values: list[tuple[float, float]]) -> float:
    vals = sorted(values)
    total = sum(w for _, w in vals)
    acc = 0.0
    for v, w in vals:
        acc += w
        if acc >= total / 2.0:
            return v
    return vals[-1][0]


def _split(p: Piece, q: Piece, pieces: list[Piece]) -> list[tuple[float, float]]:
    """The run gap between p and q minus the perpendicular walls reaching into the run band (gap kind c)."""
    a, b = p.b, q.a
    lo, hi = p.c - p.t / 2.0, p.c + p.t / 2.0
    cuts = []
    for w in pieces:
        if w.axis == p.axis:
            continue
        w0, w1 = w.c - w.t / 2.0, w.c + w.t / 2.0          # its extent along our axis
        if w1 <= a + GAP_IGNORE_M or w0 >= b - GAP_IGNORE_M:
            continue
        reach = min(w.b, hi) - max(w.a, lo)                 # how far it reaches into the band
        if reach >= 0.5 * p.t:
            cuts.append((max(w0, a), min(w1, b)))
    subs = [(a, b)]
    for c0, c1 in sorted(cuts):
        nxt = []
        for s0, s1 in subs:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 - s0 > GAP_IGNORE_M:
                nxt.append((s0, c0))
            if s1 - c1 > GAP_IGNORE_M:
                nxt.append((c1, s1))
        subs = nxt
    return subs


def _is_free(p: Piece, which: str, pieces: list[Piece]) -> bool:
    face = LineString(p.end_face(which))
    for q in pieces:
        if q is p:
            continue
        if sbox(*q.rect()).distance(face) <= FREE_END_M:
            return False
    return True


def _cast(p: Piece, which: str, pieces: list[Piece]) -> Optional[tuple[Piece, float, float]]:
    """First wall face hit from a free end along the axis within GAP_MAX_M: (wall, gap a, gap b)."""
    lo, hi = p.c - p.t / 2.0, p.c + p.t / 2.0
    best = None
    for q in pieces:
        if q is p:
            continue
        r = q.rect()
        if p.axis == "h":
            c0, c1, s0, s1 = r[1], r[3], r[0], r[2]
        else:
            c0, c1, s0, s1 = r[0], r[2], r[1], r[3]
        if min(c1, hi) - max(c0, lo) < 0.5 * p.t:
            continue
        if which == "end":
            d = s0 - p.b
            if -GAP_IGNORE_M <= d <= GAP_MAX_M and (best is None or d < best[0]):
                best = (d, q, p.b, s0)
        else:
            d = p.a - s1
            if -GAP_IGNORE_M <= d <= GAP_MAX_M and (best is None or d < best[0]):
                best = (d, q, s1, p.a)
    if best is None or best[0] <= GAP_IGNORE_M:
        return None
    return best[1], best[2], best[3]


def _own(g: Gap, index: StrokeIndex, owned: set) -> None:
    """Arc, leaf, hinge pin and the strokes entirely within the gap +- 0.10 m (which include the window's own band
    lines). Band lines running past the gap (a wall face line, a bed edge 9 mm off the face) count for the
    classification but are not owned: §2.8 decides about them."""
    if g.cls not in ("door", "window", "empty"):
        return
    ids = set()
    for key in ("arcs", "leaves"):
        ids.update(it.st.id for it in g.found.get(key, []))
    # +-0.10 m along the wall, the wall band (faces +-20 mm) across it: jamb frames and window lines sit there,
    # a bed or counter standing in front of a window does not.
    zone = g.rect(grow_face=BAND_SLACK_M, grow_along=OWN_MARGIN_M)
    for it in index.query(zone, predicate="contains"):
        ids.add(it.st.id)
    g.found["owned"] = sorted(ids)
    owned.update(ids)


def _merged_wall(seg: list[Piece], ctx: _Ctx, extended: dict, joined: Optional[dict] = None) -> WallItem:
    """One WallItem for consecutive run pieces (thickness = length-weighted median); an unchanged single piece is
    returned as it was (with the note of ``joined``, if any). ``joined``: input wall index -> the note of a piece
    ``join_fused_strips`` gave the run's centre line and thickness, or of an end cap (``end_caps``)."""
    theta = ctx.theta
    joined = joined or {}
    if len(seg) == 1 and seg[0].k not in extended:
        w = seg[0].wall
        if seg[0].k not in joined:
            return w
        old = w.evidence.get("note")
        return dataclasses.replace(w, evidence=dict(w.evidence, note=(old + "; " if old else "") + joined[seg[0].k]))
    axis = seg[0].axis
    a = min(q.a for q in seg)
    b = max(q.b for q in seg)
    c = sum(q.c * (q.b - q.a) for q in seg) / max(sum(q.b - q.a for q in seg), 1e-12)
    t = _weighted_median([(q.t, q.b - q.a) for q in seg])
    if axis == "h":
        s, e = (a, c), (b, c)
        corners = [(a, c - t / 2), (b, c - t / 2), (b, c + t / 2), (a, c + t / 2)]
    else:
        s, e = (c, a), (c, b)
        corners = [(c - t / 2, a), (c + t / 2, a), (c + t / 2, b), (c - t / 2, b)]
    s, e = _rot(s, theta), _rot(e, theta)
    corners = [_rot(p, theta) for p in corners]
    entities: list[str] = []
    for q in seg:
        for part in q.wall.entity.split(","):
            if part and part not in entities:
                entities.append(part)
    entity = ",".join(entities)
    base = seg[0].wall.evidence
    methods = {q.wall.evidence.get("method") for q in seg}
    method = "raster" if methods == {"raster"} else "vector"
    confidence = min(q.wall.evidence.get("confidence", 1.0) for q in seg)
    # Walls drawn as face lines carry their layer and the layer choice: kept when every piece has the same.
    layers = {q.wall.evidence.get("layer") for q in seg}
    first_notes = {q.wall.evidence.get("note") for q in seg}
    notes = [first_notes.pop()] if len(first_notes) == 1 and None not in first_notes else []
    notes += [joined[q.k] for q in seg if q.k in joined]
    for q in seg:
        if q.k in extended:
            ids, reason = extended[q.k]
            method = "derived"
            entity = entity + ("," + ",".join(ids) if ids else "")
            notes.append(reason)
    if len(seg) > 1:
        notes.append(f"run of {len(seg)} pieces")
    ev = B.evidence(base.get("file", ctx.file_rel), method, round(confidence, 3), page=base.get("page", ctx.page_no),
                    entity=entity, layer=layers.pop() if len(layers) == 1 else None)
    if notes:
        ev["note"] = "; ".join(notes)
    return WallItem(start=(round(s[0], 4), round(s[1], 4)), end=(round(e[0], 4), round(e[1], 4)),
                    thickness=round(t, 4), box=ctx.box(corners), entity=entity, evidence=ev,
                    status=seg[0].wall.status)


def _trim_into_bands(walls: list[WallItem], theta: float) -> None:
    """A wall end that pokes into a perpendicular wall's band (the run-length decomposition gave it the junction
    square) is moved back to the face it crosses first: the through-wall keeps the junction (§2.4.3)."""
    pieces, _ = pieces_of(walls, theta)
    for p in pieces:
        changed = False
        for which in ("start", "end"):
            pos = p.a if which == "start" else p.b
            for q in pieces:
                if q is p or q.axis == p.axis:
                    continue
                f0, f1 = q.c - q.t / 2.0, q.c + q.t / 2.0
                if not (f0 + 1e-6 < pos < f1 + 1e-6 or f0 - 1e-6 < pos < f1 - 1e-6):
                    continue
                # q must cover p's whole band and continue past it on both sides (a through-wall).
                if not (q.a < p.c - p.t / 2.0 - 1e-6 and q.b > p.c + p.t / 2.0 + 1e-6):
                    continue
                new = f0 if which == "end" else f1
                if which == "end" and new > p.a + 0.05:
                    p.b, changed = new, True
                elif which == "start" and new < p.b - 0.05:
                    p.a, changed = new, True
        if changed:
            w = p.wall
            if p.axis == "h":
                s, e = (p.a, p.c), (p.b, p.c)
            else:
                s, e = (p.c, p.a), (p.c, p.b)
            s, e = _rot(s, theta), _rot(e, theta)
            if math.dist(s, w.end) + math.dist(e, w.start) < math.dist(s, w.start) + math.dist(e, w.end):
                s, e = e, s
            walls[p.k] = dataclasses.replace(w, start=(round(s[0], 4), round(s[1], 4)),
                                             end=(round(e[0], 4), round(e[1], 4)))


def _exterior_test(walls: list[WallItem]):
    """A function telling whether a page-metre rectangle touches the outside of its wall component."""
    polys = []
    for w in walls:
        polys.append(LineString([w.start, w.end]).buffer(w.thickness / 2.0, cap_style=2, join_style=2))
    if not polys:
        return lambda rect: False
    union = unary_union(polys).buffer(0.002, join_style=2).buffer(-0.002, join_style=2)
    rings = []
    for part in getattr(union, "geoms", [union]):
        rings.append(part.exterior)
    outer = unary_union(rings)

    def touches(corners) -> bool:
        return Polygon(corners).buffer(0.003).intersects(outer)
    return touches


def _opening(g: Gap, ctx: _Ctx, exterior) -> OpeningItem:
    theta = ctx.theta
    mid = (g.a + g.b) / 2.0
    center = _rot(g.point(mid), theta)
    axis_deg = (0.0 if g.axis == "h" else 90.0) + theta
    corners = [_rot(p, theta) for p in (g.point(g.a, -g.t / 2), g.point(g.b, -g.t / 2), g.point(g.b, g.t / 2),
                                         g.point(g.a, g.t / 2))]
    box = ctx.box(corners)
    width = round(g.width, 4)
    names = ",".join(dict.fromkeys(e for p in g.pieces for e in p.wall.entity.split(",") if e))
    if g.cls == "door":
        side = _rot(_swing_side(g), theta)
        probe = (center[0] + side[0] * DOOR_SWING_PROBE, center[1] + side[1] * DOOR_SWING_PROBE)
        rotation = _door_rotation(axis_deg, side)
        ids = [it.st.id for it in g.found["arcs"] + g.found["leaves"]]
        conf = CONF_DOOR_LEAF if g.found["leaf"] else CONF_DOOR
        ev = ctx.evidence("vector", conf, ",".join(ids), box_units=box)
        if not g.found["leaf"]:
            ev["note"] = "swing arc without a drawn leaf"
        return OpeningItem(kind="door", width=width, center=_r(center), rotation_deg=round(rotation % 360.0, 3),
                           box=box, entity=ids[0], evidence=ev, swing_point=_r(probe), height=DOOR_HEIGHT_M,
                           assumed=["height"])
    if g.cls == "window":
        ids = [it.st.id for it in g.found["lines"]]
        ev = ctx.evidence("vector", CONF_WINDOW, ",".join(ids), box_units=box)
        return OpeningItem(kind="window", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                           box=box, entity=ids[0], evidence=ev, height=WINDOW_HEIGHT_M, sill=WINDOW_SILL_M,
                           assumed=["height", "sill_height"])
    if g.cls == "empty":
        ev = ctx.evidence("derived", CONF_DOORLESS, f"gap:{names}", box_units=box)
        item = OpeningItem(kind="opening", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                           box=box, entity=f"gap:{names}", evidence=ev, height=DOOR_HEIGHT_M, assumed=["height"])
        if exterior(corners):
            item.status = "unverified"
            item.evidence["note"] = "possible undrawn door or window (empty gap in an exterior wall)"
        return item
    ids = [it.st.id for it in g.found.get("content", [])]
    ev = ctx.evidence("derived", 0.5, f"gap:{names}", box_units=box)
    ev["note"] = "unclassified gap content: " + ",".join(ids[:20]) + (" ..." if len(ids) > 20 else "")
    return OpeningItem(kind="opening", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                       box=box, entity=f"gap:{names}", evidence=ev, status="unverified", height=DOOR_HEIGHT_M,
                       assumed=["height"], type_raw="unclassified gap content")


def _r(p) -> tuple[float, float]:
    return (round(p[0], 4), round(p[1], 4))


def _swing_side(g: Gap) -> tuple[float, float]:
    """Unit vector (aligned frame) from the wall towards the side the door opens into."""
    sgn = g.found["swing"]
    return (0.0, sgn) if g.axis == "h" else (sgn, 0.0)


def _door_rotation(axis_deg: float, side) -> float:
    """Wall direction whose left normal points to the swing side ``side`` (page frame): the synthetic door
    convention, where a door block opens towards its local +Y with rotation = wall angle."""
    t = math.radians(axis_deg)
    left = (-math.sin(t), math.cos(t))
    return axis_deg if left[0] * side[0] + left[1] * side[1] > 0 else axis_deg + 180.0


def _log_entry(g: Gap, theta: float, piece_out: dict) -> dict:
    entry = {"kind": g.kind, "class": g.cls, "width": round(g.width, 4),
             "p0": _out(g.point(g.a), theta), "p1": _out(g.point(g.b), theta), "thickness": round(g.t, 4),
             "walls": sorted({piece_out.get(p.k) for p in g.pieces if piece_out.get(p.k) is not None})}
    if g.found.get("owned"):
        entry["owned"] = g.found["owned"]
    if g.cls == "door":
        entry["hinges"] = [_out(h, theta) for h in g.found["hinges"]]
        entry["radius"] = round(g.found["radius"], 4)
        entry["leaf"] = g.found["leaf"]
    if g.cls == "unclassified":
        entry["strokes"] = [it.st.id for it in g.found.get("content", [])]
    if g.found.get("split_reason"):
        entry["note"] = g.found["split_reason"]
    if g.kind == "end":
        p, which = g.free
        entry["free_wall"] = piece_out.get(p.k)
        entry["free_end"] = which
        entry["hit_wall"] = piece_out.get(g.hit.k) if g.hit else None
        entry["line"] = [_out(g.point(g.a), theta), _out(g.point(g.b), theta)]
    return entry


# --------------------------------------------------------------------------
# Continuous-wall symbols
# --------------------------------------------------------------------------

def _continuous_symbols(walls: list[WallItem], index: StrokeIndex, owned: set, theta: float, ctx: _Ctx,
                        existing: list[OpeningItem]) -> tuple[list[OpeningItem], list[OpeningItem]]:
    pieces, _ = pieces_of(walls, theta)
    doors: list[OpeningItem] = []
    # Doors: arc + leaf with the end-point rule, hinged in a wall band.
    arcs = [(it, arc) for it, arc in _arcs_in(index.items) if it.st.id not in owned
            and CONTINUOUS_RADIUS_M[0] <= arc["radius"] <= CONTINUOUS_RADIUS_M[1]
            and SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]]
    for it, arc in arcs:
        hinge = arc["center"]
        host = None
        for p in pieces:
            x0, y0, x1, y1 = p.rect()
            if x0 - HINGE_M <= hinge[0] <= x1 + HINGE_M and y0 - HINGE_M <= hinge[1] <= y1 + HINGE_M:
                host = p
                break
        if host is None:
            continue
        found = None
        for tip, other in ((arc["end"], arc["start"]), (arc["start"], arc["end"])):
            near = index.query((tip[0] - END_POINT_TOL_M, tip[1] - END_POINT_TOL_M, tip[0] + END_POINT_TOL_M,
                                tip[1] + END_POINT_TOL_M))
            for leaf in near:
                if leaf is it or leaf.st.id in owned or len(leaf.pts) < 2:
                    continue
                for a, b in ((leaf.pts[0], leaf.pts[-1]), (leaf.pts[-1], leaf.pts[0])):
                    if math.dist(a, tip) > END_POINT_TOL_M:
                        continue
                    w = math.dist(b, a)
                    if w <= 0 or abs(math.dist(b, other) - w) > 2 * END_POINT_TOL_M:
                        continue
                    found = (leaf, b, a, other)
                    break
                if found:
                    break
            if found:
                break
        leaf_ids = None
        if not found:
            found, leaf_ids = _shape_leaf(it, arc, index, owned)
        if not found:
            continue
        leaf, hinge_pt, tip, closed_end = found
        w = math.dist(hinge_pt, closed_end)
        mid = ((hinge_pt[0] + closed_end[0]) / 2.0, (hinge_pt[1] + closed_end[1]) / 2.0)
        # Onto the host's centre line.
        mid = (mid[0], host.c) if host.axis == "h" else (host.c, mid[1])
        side = (tip[0] - hinge_pt[0], tip[1] - hinge_pt[1])
        n = math.hypot(*side) or 1.0
        side = (side[0] / n, side[1] / n)
        axis_deg = (0.0 if host.axis == "h" else 90.0) + theta
        center = _rot(mid, theta)
        side_page = _rot(side, theta)
        probe = (center[0] + side_page[0] * DOOR_SWING_PROBE, center[1] + side_page[1] * DOOR_SWING_PROBE)
        rotation = _door_rotation(axis_deg, side_page)
        corners = [_rot(p, theta) for p in (hinge_pt, closed_end,
                                            (closed_end[0] + side[0] * w, closed_end[1] + side[1] * w), tip)]
        bx = ctx.box(corners)
        ids = [it.st.id] + (leaf_ids or [leaf.st.id])
        owned.update(ids)
        ev = ctx.evidence("vector", CONF_DOOR_LEAF, ",".join(ids), box_units=bx)
        doors.append(OpeningItem(kind="door", width=round(w, 4), center=_r(center),
                                 rotation_deg=round(rotation % 360, 3), box=bx, entity=ids[0], evidence=ev,
                                 swing_point=_r(probe), height=DOOR_HEIGHT_M, assumed=["height"]))
    windows = _continuous_windows(pieces, index, owned, theta, ctx, existing + doors)
    return doors, windows


def _shape_leaf(it: _S, arc: dict, index: StrokeIndex, owned: set):
    """A door leaf drawn as a thin shape (a closed rectangle, as CAD door blocks draw it) for a continuous-wall arc:
    the gap classifier's leaf rule (<= 60 mm wide, 0.85-1.05 r long, from the hinge along the arc's start or end
    radius). Returns ((leaf, hinge, tip, closed end), leaf ids) or (None, None)."""
    hinge, r = arc["center"], arc["radius"]
    reach = LEAF_LENGTH[1] * r + LEAF_START_M + LEAF_CORRIDOR_M
    near = [x for x in index.query((hinge[0] - reach, hinge[1] - reach, hinge[0] + reach, hinge[1] + reach))
            if x is not it and x.st.id not in owned]
    for tip, other in ((arc["end"], arc["start"]), (arc["start"], arc["end"])):
        leaf = _leaf({**arc, "start": tip, "end": tip}, near, {id(it)})
        if leaf:
            return (leaf[0], hinge, tip, other), [x.st.id for x in leaf]
    return None, None


def _continuous_windows(pieces: list[Piece], index: StrokeIndex, owned: set, theta: float, ctx: _Ctx,
                        existing: list[OpeningItem]) -> list[OpeningItem]:
    """>= 3 distinct parallel stroke offsets inside a wall band, one strictly inside it, or >= 2 strictly inside it,
    over >= 0.4 m."""
    out = []
    taken = [(_rot(o.center, -theta), o.width) for o in existing]
    for p in pieces:
        x0, y0, x1, y1 = p.rect()
        band = (x0 - BAND_SLACK_M, y0 - BAND_SLACK_M, x1 + BAND_SLACK_M, y1 + BAND_SLACK_M)
        segs = []
        for it in index.query(band, predicate="intersects"):
            if it.st.id in owned:
                continue
            pts = it.pts + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])
            for a, b in zip(pts, pts[1:]):
                if not _parallel(a, b, p.axis):
                    continue
                off = (a[1] + b[1]) / 2 - p.c if p.axis == "h" else (a[0] + b[0]) / 2 - p.c
                if abs(off) > p.t / 2 + BAND_SLACK_M:
                    continue
                lo, hi = sorted((a[0], b[0])) if p.axis == "h" else sorted((a[1], b[1]))
                lo, hi = max(lo, p.a), min(hi, p.b)
                if hi - lo > 0.01:
                    segs.append((lo, hi, round(off, 3), it))
        if len(segs) < 3:
            continue
        cuts = sorted({s[0] for s in segs} | {s[1] for s in segs})
        intervals = []
        for u, v in zip(cuts, cuts[1:]):
            m = (u + v) / 2
            offs = {s[2] for s in segs if s[0] <= m <= s[1]}
            inner = {o for o in offs if abs(o) < p.t / 2 - BAND_SLACK_M}
            # Three offsets with one inside the band; or two inside it where the wall's faces are no strokes here
            # (walls drawn as face lines: the faces are the wall primitive, real02's glass lines lie between them).
            if (len(offs) >= 3 and inner) or len(inner) >= 2:
                if intervals and abs(intervals[-1][1] - u) < 1e-6:
                    intervals[-1][1] = v
                else:
                    intervals.append([u, v])
        for u, v in intervals:
            if v - u < CONTINUOUS_WINDOW_M:
                continue
            mid = (u + v) / 2
            centre_f = (mid, p.c) if p.axis == "h" else (p.c, mid)
            if any(math.dist(centre_f, c) < max(w / 2, 0.2) for c, w in taken):
                continue
            used = [s[3] for s in segs if s[0] < v and s[1] > u and abs(s[2]) < p.t / 2 - BAND_SLACK_M]
            ids = sorted({it.st.id for it in used})
            owned.update(ids)
            corners_f = [(u, p.c - p.t / 2), (v, p.c + p.t / 2)] if p.axis == "h" else \
                [(p.c - p.t / 2, u), (p.c + p.t / 2, v)]
            bx = ctx.box([_rot(q, theta) for q in corners_f])
            axis_deg = ((0.0 if p.axis == "h" else 90.0) + theta) % 180.0
            out.append(OpeningItem(kind="window", width=round(v - u, 4), center=_r(_rot(centre_f, theta)),
                                   rotation_deg=round(axis_deg, 3), box=bx, entity=ids[0] if ids else "band",
                                   evidence=ctx.evidence("vector", CONF_WINDOW, ",".join(ids), box_units=bx),
                                   height=WINDOW_HEIGHT_M, sill=WINDOW_SILL_M, assumed=["height", "sill_height"]))
            taken.append((centre_f, v - u))
    return out
