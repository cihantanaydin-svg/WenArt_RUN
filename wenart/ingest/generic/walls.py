"""Walls of the generic plan core (docs/milestone7.md §2.4): primitives -> wall mask -> rectangles -> snapped faces.

Real plans draw walls as hatch patterns, dark fills, closed outlines or wall-layer hatches, not as the 0.5 pt
rectangles of the synthetic PDFs. This module turns any of these into ``WallItem`` rectangles in three steps:

1. ``wall_primitives``: the drawn things that are wall material, each with its evidence:
   - *hatch groups*: >= ``HATCH_MIN_LINES`` straight strokes of one colour and direction (+- 1 deg), each <= 0.8 m,
     spatially connected, whose perpendicular offsets form a regular comb (median step <= 25 mm) -> vector 0.95,
     entity ``hatch:<n>``;
   - *dark fills*: filled closed strokes with luminance <= 0.35 **and** chroma (max - min RGB) <= 0.10 -> 0.9 (so
     real01's dark-green plants and red arrowheads are not walls);
   - *outline walls*: closed stroked polygons of 4-12 vertices, minimum width 0.05-0.60 m, length >= 0.4 m, with no
     other stroke inside -> 0.8;
   - *DXF hatches/solids* on wall-hint layers -> 0.95 (the paths of one entity are filled even-odd);
   - a raster page's own mask -> ``raster`` 0.85.
2. ``wall_mask``: everything rasterised at 10 mm/px in page metres (polygons even-odd per primitive; hatch lines 1 px
   wide, then a 3 x 3 closing and a 1 px erosion); components < 0.02 m² are dropped. The result is a ``WallMask``
   (a ``MaskLayer`` that also remembers which primitive drew each pixel, for the evidence).
3. ``walls_from_mask``: the mask is decomposed into axis rectangles in the dominant orientation pair (from the outline
   strokes, else from the mask's own edges): the mask's edge positions become grid lines (non-maximum suppression
   within 2 px, so the 1-2 px jaggedness of a rasterised hatch does not matter), every grid cell that is at least half
   wall goes to the direction of its longer run of wall cells (the longer wall keeps an L or T junction square;
   ``openings`` merges the pieces of a through-wall and trims the other wall back to its face), and cells of one
   direction merge into maximal strips of constant cross-section; each face then moves to the mask edge (<= 3 px).
   Components with no elongated rectangle (length >= 3 x thickness) drawn by a main-style primitive are dropped
   unless they touch a kept wall; rectangles thinner than ``MIN_WALL_M`` are not walls. Each rectangle face then snaps
   to a parallel outline stroke within 20 mm along >= 50 % of the face; the thickness is the distance between the
   snapped faces rounded to 5 mm. Without outline strokes the eroded mask decides.

Everything here is in page metres (page units x ``units_to_m``, y up, no offset). ``WallItem.box`` is in page units
when ``units_to_m`` is given (the debug image draws page units), else in page metres.

Notes from real01 (docs/milestone7.md research notes): the wall hatch is 21,308 black lines at 135 deg with a 3 mm
comb; lines clipped at a wall corner are short and, on the PDF's 0.12 pt grid, up to 18 deg off, so short lines join
a group within max(1 deg, atan(2 step / L)). The coffee table's thick frame, the round piece's annulus and the two
telephone keypads are also "solid" combs, of 0/90 deg lines: they pass the hatch rule, but that style holds < 25 % of
the main direction's lines, so it only counts where it touches a main-style wall; they are dropped and their strokes
go back to the furniture strokes (``info["dropped_strokes"]``).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

from wenart import building as B
from wenart.ingest.generic.model import GenericPage, MaskLayer, Stroke
from wenart.ingest.model import WallItem

# Primitives (§2.4.1)
HATCH_MIN_LINES = 20
HATCH_ANGLE_TOL_DEG = 1.0
HATCH_MAX_LINE_M = 0.8
HATCH_MAX_STEP_M = 0.025
HATCH_CONFIDENCE = 0.95
FILL_MAX_LUMINANCE = 0.35
FILL_MAX_CHROMA = 0.10
FILL_CONFIDENCE = 0.9
OUTLINE_MIN_VERTICES, OUTLINE_MAX_VERTICES = 4, 12
OUTLINE_WIDTH_M = (0.05, 0.60)
OUTLINE_MIN_LENGTH_M = 0.4
OUTLINE_CONFIDENCE = 0.8
DXF_HATCH_CONFIDENCE = 0.95
RASTER_CONFIDENCE = 0.85

# Mask (§2.4.2)
MASK_PX_M = 0.01
MIN_COMPONENT_M2 = 0.02
MIN_ELONGATION = 3.0
TOUCH_M = 0.02                 # a dropped-looking component this close to a kept wall is kept

# Decomposition and faces (§2.4.3-5)
MIN_WALL_M = 0.05              # thinner "walls" are drawn details (outline walls use the same lower bound)
MIN_IOU = 0.97
SNAP_M = 0.02                  # a face snaps to an outline stroke this close ...
SNAP_COVER = 0.5               # ... running along this share of the face
THICKNESS_ROUND_M = 0.005
THICKNESS_CLASS_M = 0.015
ANGLED_DEG = 3.0
SEGMENT_ANGLE_TOL_DEG = 1.0


@dataclass
class WallPrim:
    """One drawn thing that is wall material, in page metres."""
    kind: str                                   # hatch | fill | outline | dxf_hatch | raster
    entity: str                                 # "hatch:3", the stroke id, or "raster:mask"
    stroke_ids: list[str]
    method: str                                 # vector | raster
    confidence: float
    polygons: list[list[tuple[float, float]]] = field(default_factory=list)   # filled even-odd (one primitive)
    lines: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)  # hatch lines
    mask: Optional[MaskLayer] = None            # raster: the page's own mask, page metres
    direction_deg: Optional[float] = None       # hatch direction
    step_m: Optional[float] = None              # hatch comb step

    def describe(self) -> dict:
        out = {"entity": self.entity, "kind": self.kind, "method": self.method, "confidence": self.confidence,
               "strokes": len(self.stroke_ids)}
        if self.direction_deg is not None:
            out["direction_deg"] = round(self.direction_deg, 1)
            out["step_mm"] = round(self.step_m * 1000.0, 1)
        return out


@dataclass
class WallMask(MaskLayer):
    """The wall mask plus where its pixels came from (``prim_index`` = 1 + index into ``prims``, 0 = none)."""
    prim_index: object = None
    prims: list = field(default_factory=list)
    dropped_strokes: set = field(default_factory=set)   # primitive strokes whose component was dropped
    notes: list = field(default_factory=list)


# --------------------------------------------------------------------------
# Small geometry helpers
# --------------------------------------------------------------------------

def _scale_pts(pts, s: float) -> list[tuple[float, float]]:
    return [(float(x) * s, float(y) * s) for x, y in pts]


def _luminance(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _chroma(rgb) -> float:
    return max(rgb) - min(rgb)


def _angle_mod180(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def _angle_diff180(a: float, b: float) -> float:
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _is_straight(st: Stroke) -> bool:
    if st.kind == "line":
        return True
    if st.closed or len(st.pts) != 2:
        return False
    return st.kind in ("polyline", "curve") and st.arc is None


def segments_of(st: Stroke) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Straight pieces of a stroke (closing edge included for closed strokes); flattened arcs give their chords."""
    pts = list(st.pts)
    if st.closed and len(pts) > 2:
        pts = pts + [pts[0]]
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1) if pts[i] != pts[i + 1]]


def fill_polygons(st: Stroke, s: float = 1.0) -> list[list[tuple[float, float]]]:
    """Polygons a filled stroke covers (page units x s)."""
    pts = _scale_pts(st.pts, s)
    if len(pts) >= 3:
        return [pts]
    return []


# --------------------------------------------------------------------------
# 1. Primitives
# --------------------------------------------------------------------------

def wall_primitives(page: GenericPage, units_to_m: float) -> list[WallPrim]:
    """All wall primitives of a page, in page metres (see the module docstring for the rules)."""
    s = float(units_to_m)
    prims: list[WallPrim] = []
    if page.wall_mask is not None:
        m = page.wall_mask
        mask_m = MaskLayer(mask=m.mask, origin=(m.origin[0] * s, m.origin[1] * s), px=m.px * s)
        prims.append(WallPrim(kind="raster", entity="raster:mask", stroke_ids=[], method="raster",
                              confidence=RASTER_CONFIDENCE, mask=mask_m))
    used: set[str] = set()
    prims.extend(_dxf_hatches(page, s, used))
    prims.extend(_hatch_groups(page, s, used))
    prims.extend(_dark_fills(page, s, used))
    prims.extend(_outline_walls(page, s, used))
    return prims


def _entity_base(stroke_id: str) -> str:
    """Paths of one DXF HATCH share the id before '#' (``ent:1A2B#0``, ``ent:1A2B#1``)."""
    return stroke_id.split("#", 1)[0]


def _dxf_hatches(page: GenericPage, s: float, used: set) -> list[WallPrim]:
    if not page.wall_hint_layers:
        return []
    hint = {name.upper() for name in page.wall_hint_layers}
    groups: dict[str, list[Stroke]] = {}
    for st in page.strokes:
        if st.layer and st.layer.upper() in hint and st.fill is not None and len(st.pts) >= 3:
            groups.setdefault(_entity_base(st.id), []).append(st)
    out = []
    for base, strokes in groups.items():
        polys = [p for st in strokes for p in fill_polygons(st, s)]
        if not polys:
            continue
        used.update(st.id for st in strokes)
        out.append(WallPrim(kind="dxf_hatch", entity=base, stroke_ids=[st.id for st in strokes], method="vector",
                            confidence=DXF_HATCH_CONFIDENCE, polygons=polys))
    return out


def _hatch_groups(page: GenericPage, s: float, used: set) -> list[WallPrim]:
    """Regular combs of short parallel strokes of one colour (§2.4.1)."""
    cands: dict[tuple, list[tuple[Stroke, float, tuple, tuple]]] = {}
    for st in page.strokes:
        if st.id in used or st.fill is not None or not _is_straight(st):
            continue
        a, b = _scale_pts([st.pts[0], st.pts[-1]], s)
        length = math.dist(a, b)
        if length <= 1e-9 or length > HATCH_MAX_LINE_M:
            continue
        colour = tuple(round(c, 2) for c in st.colour) if st.colour is not None else None
        cands.setdefault(colour, []).append((st, _angle_mod180(a, b), a, b))
    prims: list[WallPrim] = []
    for colour, items in cands.items():
        first = len(prims)
        remaining = items
        while len(remaining) >= HATCH_MIN_LINES:
            peak = _angle_peak([it[1] for it in remaining])
            if peak is None:
                break
            near = [it for it in remaining if _angle_diff180(it[1], peak) <= 1.5]
            centre = _circular_median180([it[1] for it in near])
            group = [it for it in remaining if _angle_diff180(it[1], centre) <= HATCH_ANGLE_TOL_DEG]
            if len(group) < HATCH_MIN_LINES:
                break
            ids = {id(it[0]) for it in group}
            remaining = [it for it in remaining if id(it[0]) not in ids]
            for comp in _spatial_groups(group):
                if len(comp) < HATCH_MIN_LINES:
                    continue
                step = _comb_step(comp, centre)
                if step is None or step > HATCH_MAX_STEP_M:
                    continue
                n = len(prims)
                prims.append(WallPrim(kind="hatch", entity=f"hatch:{n}", stroke_ids=[it[0].id for it in comp],
                                      method="vector", confidence=HATCH_CONFIDENCE,
                                      lines=[(it[2], it[3]) for it in comp], direction_deg=centre, step_m=step))
                used.update(it[0].id for it in comp)
        _attach_short_lines(prims[first:], items, used)            # same colour only
    return prims


def _attach_short_lines(prims: list[WallPrim], items, used: set, px: float = 0.01) -> None:
    """Hatch lines clipped at a wall corner are short, and on a quantised page their direction is noisy (real01:
    0.12 pt grid). With both ends off by up to about one comb step, a line of length L cannot show its direction
    better than atan(2 step / L), so a leftover line of the group's colour joins a group when its angle is within
    max(1 deg, atan(2 step / L)) of the group's and its midpoint touches the group's lines (2 px at 10 mm/px)."""
    if not prims:
        return
    xs = [p[0] for pr in prims for ln in pr.lines for p in ln]
    ys = [p[1] for pr in prims for ln in pr.lines for p in ln]
    x0, y0 = min(xs) - 3 * px, min(ys) - 3 * px
    px = _fit_px(px, max(xs) - x0, max(ys) - y0)
    w = int((max(xs) - x0) / px) + 4
    h = int((max(ys) - y0) / px) + 4
    labels = np.zeros((h, w), np.uint16)
    for k, pr in enumerate(prims):
        lines = [np.array([[int((a[0] - x0) / px), int((a[1] - y0) / px)],
                           [int((b[0] - x0) / px), int((b[1] - y0) / px)]], np.int32) for a, b in pr.lines]
        cv2.polylines(labels, lines, False, k + 1, 1, cv2.LINE_8)
    labels = cv2.dilate(labels, np.ones((5, 5), np.uint8))
    for st, ang, a, b in items:
        if st.id in used:
            continue
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        c, r = int((mid[0] - x0) / px), int((mid[1] - y0) / px)
        if not (0 <= r < h and 0 <= c < w) or labels[r, c] == 0:
            continue
        pr = prims[int(labels[r, c]) - 1]
        length = math.dist(a, b)
        tol = max(HATCH_ANGLE_TOL_DEG, math.degrees(math.atan2(2.0 * pr.step_m, length)))
        if _angle_diff180(ang, pr.direction_deg) <= tol:
            pr.lines.append((a, b))
            pr.stroke_ids.append(st.id)
            used.add(st.id)


def _angle_peak(angles: list[float]) -> Optional[float]:
    """Centre of the fullest 0.5 deg bin (mod 180), or None when no bin holds HATCH_MIN_LINES."""
    hist = np.zeros(360, dtype=np.int64)
    for a in angles:
        hist[int(a * 2.0) % 360] += 1
    # A peak may straddle two bins: use the sum over 3 neighbouring bins.
    wide = hist + np.roll(hist, 1) + np.roll(hist, -1)
    k = int(np.argmax(wide))
    if wide[k] < HATCH_MIN_LINES:
        return None
    return (k + 0.5) / 2.0


def _circular_median180(angles: list[float]) -> float:
    ref = angles[0]
    unwrapped = [ref + ((a - ref + 90.0) % 180.0 - 90.0) for a in angles]
    return statistics.median(unwrapped) % 180.0


def _spatial_groups(items, px: float = 0.01) -> list[list]:
    """Connected groups of lines (drawn 1 px wide at ``px``, 8-connected); hatch lines of one wall system touch."""
    xs = [p[0] for it in items for p in (it[2], it[3])]
    ys = [p[1] for it in items for p in (it[2], it[3])]
    x0, y0 = min(xs) - 2 * px, min(ys) - 2 * px
    px = _fit_px(px, max(xs) - x0, max(ys) - y0)
    w = int((max(xs) - x0) / px) + 3
    h = int((max(ys) - y0) / px) + 3
    img = np.zeros((h, w), np.uint8)
    lines = [np.array([[int((it[2][0] - x0) / px), int((it[2][1] - y0) / px)],
                       [int((it[3][0] - x0) / px), int((it[3][1] - y0) / px)]], np.int32) for it in items]
    cv2.polylines(img, lines, False, 255, 1, cv2.LINE_8)
    n, lab = cv2.connectedComponents(img, connectivity=8)
    groups: dict[int, list] = {}
    for it, ln in zip(items, lines):
        c, r = ln[0]
        groups.setdefault(int(lab[r, c]), []).append(it)
    return list(groups.values())


def _fit_px(px: float, width: float, height: float, max_pixels: float = 6e7) -> float:
    """Coarsen ``px`` so a canvas of width x height stays below ``max_pixels`` (huge DXF model spaces)."""
    while (width / px) * (height / px) > max_pixels:
        px *= 2.0
    return px


def _comb_step(items, direction_deg: float) -> Optional[float]:
    """Median distance between neighbouring distinct offsets perpendicular to the lines."""
    th = math.radians(direction_deg)
    nx, ny = -math.sin(th), math.cos(th)
    offs = sorted(nx * (it[2][0] + it[3][0]) / 2 + ny * (it[2][1] + it[3][1]) / 2 for it in items)
    uniq = [offs[0]]
    for o in offs[1:]:
        if o - uniq[-1] > 0.0005:
            uniq.append(o)
    if len(uniq) < 3:
        return None
    return float(statistics.median(np.diff(uniq)))


def _dark_fills(page: GenericPage, s: float, used: set) -> list[WallPrim]:
    out = []
    for st in page.strokes:
        if st.id in used or st.fill is None or len(st.pts) < 3:
            continue
        if _luminance(st.fill) > FILL_MAX_LUMINANCE or _chroma(st.fill) > FILL_MAX_CHROMA:
            continue
        used.add(st.id)
        out.append(WallPrim(kind="fill", entity=st.id, stroke_ids=[st.id], method="vector",
                            confidence=FILL_CONFIDENCE, polygons=fill_polygons(st, s)))
    return out


def _outline_walls(page: GenericPage, s: float, used: set) -> list[WallPrim]:
    """Closed stroked thin polygons with nothing drawn inside them."""
    cands = []
    for st in page.strokes:
        if st.id in used or not st.closed or st.fill is not None or st.arc is not None:
            continue
        if not OUTLINE_MIN_VERTICES <= len(st.pts) <= OUTLINE_MAX_VERTICES:
            continue
        poly = Polygon(_scale_pts(st.pts, s))
        if not poly.is_valid or poly.area <= 0:
            continue
        rect = poly.minimum_rotated_rectangle
        sides = _rect_sides(rect)
        if not (OUTLINE_WIDTH_M[0] <= min(sides) <= OUTLINE_WIDTH_M[1] and max(sides) >= OUTLINE_MIN_LENGTH_M):
            continue
        cands.append((st, poly))
    if not cands:
        return []
    others = [st for st in page.strokes if st.pts]
    probes = []
    for st in others:                                   # one probe per stroke: the centre of its box
        x0, y0, x1, y1 = st.bbox()
        probes.append(Point((x0 + x1) / 2.0 * s, (y0 + y1) / 2.0 * s))
    tree = STRtree(probes)
    out = []
    for st, poly in cands:
        inner = poly.buffer(-0.002)
        if inner.is_empty:
            continue
        hit = any(others[int(j)] is not st for j in tree.query(inner, predicate="contains"))
        if hit:
            continue
        used.add(st.id)
        out.append(WallPrim(kind="outline", entity=st.id, stroke_ids=[st.id], method="vector",
                            confidence=OUTLINE_CONFIDENCE, polygons=[list(poly.exterior.coords)[:-1]]))
    return out


def _rect_sides(rect) -> tuple[float, float]:
    if rect.geom_type != "Polygon":
        return (0.0, 0.0)
    c = list(rect.exterior.coords)
    return (math.dist(c[0], c[1]), math.dist(c[1], c[2]))


# --------------------------------------------------------------------------
# 2. Mask
# --------------------------------------------------------------------------

class _Grid:
    """Page metres <-> pixel indices of a mask (row 0 at the top, y up in metres)."""

    def __init__(self, x0: float, y1: float, px: float, rows: int, cols: int):
        self.x0, self.y1, self.px, self.rows, self.cols = x0, y1, px, rows, cols

    def to_px(self, p) -> tuple[int, int]:
        return (int(math.floor((p[0] - self.x0) / self.px)), int(math.floor((self.y1 - p[1]) / self.px)))

    def to_px_f(self, p) -> tuple[float, float]:
        return ((p[0] - self.x0) / self.px, (self.y1 - p[1]) / self.px)

    def col_x(self, c: float) -> float:
        return self.x0 + c * self.px

    def row_y(self, r: float) -> float:
        return self.y1 - r * self.px


def _prim_bounds(prims: list[WallPrim]) -> Optional[tuple[float, float, float, float]]:
    xs, ys = [], []
    for p in prims:
        for poly in p.polygons:
            xs.extend(q[0] for q in poly)
            ys.extend(q[1] for q in poly)
        for a, b in p.lines:
            xs.extend((a[0], b[0]))
            ys.extend((a[1], b[1]))
        if p.mask is not None:
            rows, cols = np.asarray(p.mask.mask).shape
            xs.extend((p.mask.origin[0], p.mask.origin[0] + cols * p.mask.px))
            ys.extend((p.mask.origin[1], p.mask.origin[1] - rows * p.mask.px))
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def wall_mask(page: GenericPage, prims: list[WallPrim], units_to_m: float, px_m: float = MASK_PX_M) -> WallMask:
    """Rasterise the primitives into one wall mask in page metres (``px_m`` per pixel)."""
    bounds = _prim_bounds(prims)
    if bounds is None:
        return WallMask(mask=np.zeros((1, 1), bool), origin=(0.0, 0.0), px=px_m, prim_index=np.zeros((1, 1), np.int32),
                        prims=list(prims))
    margin = 5 * px_m
    x0, y0, x1, y1 = bounds[0] - margin, bounds[1] - margin, bounds[2] + margin, bounds[3] + margin
    px = _fit_px(px_m, x1 - x0, y1 - y0)
    cols = int(math.ceil((x1 - x0) / px)) + 1
    rows = int(math.ceil((y1 - y0) / px)) + 1
    grid = _Grid(x0, y1, px, rows, cols)
    mask = np.zeros((rows, cols), np.uint8)
    index = np.zeros((rows, cols), np.int32)
    for k, prim in enumerate(prims):
        layer = _draw_prim(prim, grid)
        mask |= layer
        index[(layer > 0) & (index == 0)] = k + 1
    out = WallMask(mask=mask > 0, origin=(x0, y1), px=px, prim_index=index, prims=list(prims))
    _drop_small_components(out)
    return out


def _draw_prim(prim: WallPrim, grid: _Grid) -> np.ndarray:
    layer = np.zeros((grid.rows, grid.cols), np.uint8)
    if prim.lines:
        pts = [np.array([grid.to_px(a), grid.to_px(b)], np.int32) for a, b in prim.lines]
        cv2.polylines(layer, pts, False, 1, 1, cv2.LINE_8)
        kernel = np.ones((3, 3), np.uint8)
        layer = cv2.morphologyEx(layer, cv2.MORPH_CLOSE, kernel)
        layer = cv2.erode(layer, kernel, iterations=1)
    for poly in prim.polygons:
        one = np.zeros_like(layer)
        cv2.fillPoly(one, [np.array([grid.to_px_f(p) for p in poly], np.float64).round().astype(np.int32)], 1)
        layer ^= one                                   # even-odd within one primitive
    if prim.mask is not None:
        src = np.asarray(prim.mask.mask).astype(np.uint8)
        # Destination pixel (c, r) -> source pixel: x = x0 + (c + 0.5) px -> c_src = (x - ox) / spx - 0.5.
        m = prim.mask
        sx = grid.px / m.px
        a = np.array([[sx, 0.0, (grid.x0 - m.origin[0]) / m.px + 0.5 * sx - 0.5],
                      [0.0, sx, (m.origin[1] - grid.y1) / m.px + 0.5 * sx - 0.5]], np.float64)
        warped = cv2.warpAffine(src, a, (grid.cols, grid.rows), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        layer |= (warped > 0).astype(np.uint8)
    return layer


def _drop_small_components(wm: WallMask) -> None:
    mask = np.asarray(wm.mask).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    min_px = MIN_COMPONENT_M2 / (wm.px * wm.px)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < min_px:
            _release(wm, lab == i, f"component of {stats[i, cv2.CC_STAT_AREA] * wm.px * wm.px:.3f} m² "
                                   f"< {MIN_COMPONENT_M2} m² dropped")


def _release(wm: WallMask, region: np.ndarray, note: str) -> None:
    """Clear a mask region; primitives drawn only there give their strokes back (they are not walls)."""
    index = np.asarray(wm.prim_index)
    inside = set(np.unique(index[region]).tolist()) - {0}
    wm.mask[region] = False
    remaining = set(np.unique(index[np.asarray(wm.mask)]).tolist())
    for k in inside:
        if k not in remaining:
            wm.dropped_strokes.update(wm.prims[k - 1].stroke_ids)
    index[region] = 0
    wm.notes.append(note)


# --------------------------------------------------------------------------
# 3. Rectangles, faces, WallItems
# --------------------------------------------------------------------------

@dataclass
class _Rect:
    axis: str                  # "h" (long side along x) | "v"
    x0: float
    y0: float
    x1: float
    y1: float
    prims: set = field(default_factory=set)
    snapped: int = 0

    @property
    def length(self) -> float:
        return (self.x1 - self.x0) if self.axis == "h" else (self.y1 - self.y0)

    @property
    def thickness(self) -> float:
        return (self.y1 - self.y0) if self.axis == "h" else (self.x1 - self.x0)


def walls_from_mask(mask: MaskLayer, outline_strokes_m: list[Stroke], file_rel: str, page_no: int,
                    units_to_m: Optional[float] = None) -> tuple[list[WallItem], dict]:
    """Wall rectangles from a wall mask (page metres) with faces snapped to the outline strokes.

    Returns ``(walls, info)``; ``info`` holds ``thickness_classes``, ``iou``, ``missed_m2``, ``dominant_deg``,
    ``faces_snapped``/``faces_unsnapped``, ``primitives``, ``dropped_strokes`` (primitive strokes that turned out
    not to be walls; §2.8 treats them as ordinary strokes), ``notes`` and ``warnings``.
    """
    info: dict = {"warnings": [], "notes": list(getattr(mask, "notes", []))}
    prims = list(getattr(mask, "prims", []) or [])
    index = getattr(mask, "prim_index", None)
    dropped = set(getattr(mask, "dropped_strokes", set()) or set())
    m = np.asarray(mask.mask).astype(bool).copy()
    if index is None:
        index = np.zeros(m.shape, np.int32)
    index = np.asarray(index)
    grid = _Grid(mask.origin[0], mask.origin[1], mask.px, m.shape[0], m.shape[1])
    segments = _outline_segments(outline_strokes_m)
    theta = _dominant_angle(segments, m, grid)
    info["dominant_deg"] = round(theta, 2)
    rot_m, rot_index, rot_grid, to_page = (m, index, grid, None)
    if abs(theta) > 0.5:
        rot_m, rot_index, rot_grid, to_page = _rotate_frame(m, index, grid, -theta)
        segments = [(_rot(a, -theta), _rot(b, -theta)) for a, b in segments]

    rects = _decompose(rot_m, rot_index, rot_grid)
    claimed = np.zeros(rot_m.shape, bool)
    for r in rects:
        claimed |= _rect_region(r, rot_grid)
    for r in rects:
        _refine_faces(r, rot_m, claimed, rot_grid)
    rects, dropped_regions = _filter_components(rects, rot_m, rot_index, rot_grid, _primary_prims(prims))
    for note, region in dropped_regions:
        info["notes"].append(note)
        inside = set(np.unique(rot_index[region]).tolist()) - {0}
        rot_m[region] = False
        remaining = set(np.unique(rot_index[rot_m]).tolist())
        for k in inside:
            if k not in remaining and k - 1 < len(prims):
                dropped.update(prims[k - 1].stroke_ids)
    iou, missed = _union_iou(rects, rot_m, rot_grid)
    info["iou"] = round(iou, 4)
    info["missed_m2"] = round(missed, 4)
    if rects and iou < MIN_IOU:
        info["warnings"].append(f"wall rectangles reproduce the wall mask with IoU {iou:.3f} < {MIN_IOU} "
                                f"({missed:.2f} m² of wall material not modelled; angled or curved walls?)")
    _angled_warning(rects, rot_m, rot_grid, info)

    snapped = unsnapped = 0
    for r in rects:
        n = _snap(r, segments)
        snapped += n
        unsnapped += 4 - n
        _round_thickness(r)
    info["faces_snapped"] = snapped
    info["faces_unsnapped"] = unsnapped
    if not segments and rects:
        info["notes"].append("no outline strokes: wall faces from the eroded mask")

    walls = []
    for r in sorted(rects, key=lambda r: (r.axis, round(r.y0, 3), round(r.x0, 3))):
        walls.append(_wall_item(r, prims, theta, file_rel, page_no, units_to_m))
    info["thickness_classes"] = thickness_classes(walls)
    info["primitives"] = [p.describe() for p in prims]
    info["dropped_strokes"] = sorted(dropped)
    return walls, info


def _outline_segments(strokes: list[Stroke]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    segs = []
    for st in strokes or []:
        if st.arc is not None or (st.fill is not None and st.colour is None):
            continue
        for a, b in segments_of(st):
            if math.dist(a, b) >= 0.02:
                segs.append((a, b))
    return segs


def _dominant_angle(segments, m: np.ndarray, grid: _Grid) -> float:
    """Dominant orientation (deg, in (-45, 45]) of the plan: length-weighted outline strokes, else the mask."""
    if not segments:
        segments = _mask_edges(m, grid)               # no outline strokes: the mask's own straight edges
    hist = np.zeros(180, np.float64)              # 0.5 deg bins over 0..90
    angles = [(_angle_mod180(a, b) % 90.0, math.dist(a, b)) for a, b in segments]
    for ang, w in angles:
        hist[int(ang * 2.0) % 180] += w
    if hist.sum() <= 0:
        return 0.0
    else:
        wide = hist + np.roll(hist, 1) + np.roll(hist, -1)
        peak = (int(np.argmax(wide)) + 0.5) / 2.0
        # Weighted mean of the segments within 1 deg of the peak (differences taken mod 90).
        near = [((ang - peak + 45.0) % 90.0 - 45.0, w) for ang, w in angles]
        near = [(d, w) for d, w in near if abs(d) <= 1.0]
        ang = peak + (sum(d * w for d, w in near) / sum(w for _, w in near) if near else 0.0)
    ang %= 90.0
    if ang > 45.0:
        ang -= 90.0
    return float(ang)


def _mask_edges(m: np.ndarray, grid: _Grid) -> list:
    """Straight edges (>= 5 px) of the mask's contours, polygon-approximated within 1.5 px, in page metres."""
    contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    segs = []
    for c in contours:
        approx = cv2.approxPolyDP(c, 1.5, True).reshape(-1, 2)
        for k in range(len(approx)):
            a, b = approx[k], approx[(k + 1) % len(approx)]
            if math.dist(a, b) >= 5:
                segs.append(((grid.col_x(a[0]), grid.row_y(a[1])), (grid.col_x(b[0]), grid.row_y(b[1]))))
    return segs


def _rot(p, deg: float) -> tuple[float, float]:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def _rotate_frame(m: np.ndarray, index: np.ndarray, grid: _Grid, deg: float):
    """Mask and primitive index rotated by ``deg`` about the page origin into a new grid (nearest neighbour)."""
    corners = [(grid.col_x(c), grid.row_y(r)) for c in (0, grid.cols) for r in (0, grid.rows)]
    rc = [_rot(p, deg) for p in corners]
    x0, x1 = min(p[0] for p in rc), max(p[0] for p in rc)
    y0, y1 = min(p[1] for p in rc), max(p[1] for p in rc)
    px = grid.px
    cols = int(math.ceil((x1 - x0) / px)) + 1
    rows = int(math.ceil((y1 - y0) / px)) + 1
    new = _Grid(x0, y1, px, rows, cols)
    # Destination pixel centre (cd, rd) -> rotated-frame point -> page point (rotate by -deg) -> source pixel:
    # cs = c*cd + s*rd + k1, rs = -s*cd + c*rd + k2 with c, s = cos, sin(-deg).
    t = math.radians(-deg)
    c, s = math.cos(t), math.sin(t)
    k1 = 0.5 * c + 0.5 * s + (c * new.x0 - s * new.y1 - grid.x0) / px - 0.5
    k2 = (grid.y1 - s * new.x0 - c * new.y1) / px - 0.5 * s + 0.5 * c - 0.5
    aff = np.array([[c, s, k1], [-s, c, k2]], np.float64)
    flags = cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP
    rm = cv2.warpAffine(m.astype(np.uint8), aff, (cols, rows), flags=flags) > 0
    ri = cv2.warpAffine(index.astype(np.float32), aff, (cols, rows), flags=flags).astype(np.int32)
    return rm, ri, new, deg


def _decompose(m: np.ndarray, index: np.ndarray, grid: _Grid) -> list[_Rect]:
    """Axis rectangles covering the mask.

    The mask's edge positions are clustered into grid lines (within EDGE_CLUSTER_PX, so the 1-2 px jaggedness of a
    rasterised hatch does not matter) and every grid cell is wall when at least half of its pixels are. A wall cell
    goes to the direction of its longer run of wall cells (so the longer wall keeps an L or T junction square;
    ``openings`` later merges the pieces of a through-wall into one run). Cells of one direction then merge into
    maximal strips of constant cross-section.
    """
    if not m.any():
        return []
    xb = _grid_lines(m, axis=1)
    yb = _grid_lines(m, axis=0)
    ii = cv2.integral(m.astype(np.uint8))                       # (rows+1, cols+1)
    nx, ny = len(xb) - 1, len(yb) - 1
    occ = np.zeros((ny, nx), bool)
    for j in range(ny):
        r0, r1 = yb[j], yb[j + 1]
        for i in range(nx):
            c0, c1 = xb[i], xb[i + 1]
            area = (r1 - r0) * (c1 - c0)
            if area <= 0:
                continue
            filled = ii[r1, c1] - ii[r0, c1] - ii[r1, c0] + ii[r0, c0]
            occ[j, i] = filled * 2 >= area
    widths = np.diff(xb)
    heights = np.diff(yb)
    hrun = np.zeros((ny, nx), np.int64)
    vrun = np.zeros((ny, nx), np.int64)
    for j in range(ny):
        for i0, i1 in _true_runs(occ[j]):
            hrun[j, i0:i1] = widths[i0:i1].sum()
    for i in range(nx):
        for j0, j1 in _true_runs(occ[:, i]):
            vrun[j0:j1, i] = heights[j0:j1].sum()
    is_h = occ & (hrun >= vrun)
    is_v = occ & ~is_h
    rects: list[_Rect] = []
    # Horizontal strips: per cell column the vertical runs of H cells, then equal runs of neighbouring columns merge.
    open_h: dict[tuple[int, int], int] = {}
    spans: list[tuple[int, int, int, int]] = []              # (i0, i1 excl, j0, j1 excl)
    for i in range(nx + 1):
        runs = set(_true_runs(is_h[:, i])) if i < nx else set()
        for key in list(open_h):
            if key not in runs:
                spans.append((open_h.pop(key), i, key[0], key[1]))
        for key in runs:
            open_h.setdefault(key, i)
    for i0, i1, j0, j1 in spans:
        rects.append(_cell_rect("h", xb[i0], xb[i1], yb[j0], yb[j1], index, grid))
    open_v: dict[tuple[int, int], int] = {}
    spans = []
    for j in range(ny + 1):
        runs = set(_true_runs(is_v[j])) if j < ny else set()
        for key in list(open_v):
            if key not in runs:
                spans.append((key[0], key[1], open_v.pop(key), j))
        for key in runs:
            open_v.setdefault(key, j)
    for i0, i1, j0, j1 in spans:
        rects.append(_cell_rect("v", xb[i0], xb[i1], yb[j0], yb[j1], index, grid))
    return rects


EDGE_CLUSTER_PX = 2
EDGE_MIN_PX = 4


def _grid_lines(m: np.ndarray, axis: int) -> list[int]:
    """Pixel boundaries where the mask has edges (axis=1: vertical edges -> column boundaries).

    Non-maximum suppression: the boundary with the most edge pixels wins and suppresses its neighbours within
    EDGE_CLUSTER_PX (a chained clustering would merge unrelated walls' faces a few pixels apart across the page).
    """
    mm = m.astype(np.int8)
    if axis == 1:
        hist = np.abs(np.diff(mm, axis=1, prepend=0, append=0)).sum(axis=0)
        size = m.shape[1]
    else:
        hist = np.abs(np.diff(mm, axis=0, prepend=0, append=0)).sum(axis=1)
        size = m.shape[0]
    order = np.argsort(-hist, kind="stable")
    taken = np.zeros(len(hist), bool)
    lines = []
    for k in order:
        if hist[k] < EDGE_MIN_PX:
            break
        if taken[max(0, k - EDGE_CLUSTER_PX):k + EDGE_CLUSTER_PX + 1].any():
            continue
        taken[k] = True
        lines.append(int(k))
    return sorted(set([0, size] + lines))


def _true_runs(row) -> list[tuple[int, int]]:
    """(start, end exclusive) of the runs of True in a 1-D bool array."""
    out = []
    start = None
    for k, v in enumerate(row):
        if v and start is None:
            start = k
        elif not v and start is not None:
            out.append((start, k))
            start = None
    if start is not None:
        out.append((start, len(row)))
    return out


def _cell_rect(axis: str, c0: int, c1: int, r0: int, r1: int, index: np.ndarray, grid: _Grid) -> _Rect:
    prim_ids = set(np.unique(index[r0:r1, c0:c1]).tolist())
    prim_ids.discard(0)
    return _Rect(axis, grid.col_x(c0), grid.row_y(r1), grid.col_x(c1), grid.row_y(r0), prims=prim_ids)


REFINE_PX = 3


def _refine_faces(r: _Rect, m: np.ndarray, claimed: np.ndarray, grid: _Grid) -> None:
    """Move each face to the mask edge (at most REFINE_PX): out while the pixel line beyond it is mostly wall that
    no other rectangle holds, in while its own boundary line is mostly empty. Grid lines are shared by the whole
    page, so a cell boundary can sit a few pixels off a face when a longer edge nearby suppressed it."""
    c0, r0 = grid.to_px((r.x0 + 1e-9, r.y1 - 1e-9))
    c1, r1 = grid.to_px((r.x1 - 1e-9, r.y0 + 1e-9))       # inclusive pixel box
    rows, cols = m.shape
    free = m & ~claimed

    def frac(img, row0, row1, col0, col1):
        if row0 < 0 or col0 < 0 or row1 >= rows or col1 >= cols or row1 < row0 or col1 < col0:
            return 0.0
        return float(img[row0:row1 + 1, col0:col1 + 1].mean())

    for _ in range(REFINE_PX):                      # top face (y1)
        if frac(free, r0 - 1, r0 - 1, c0, c1) >= 0.5:
            r0 -= 1
            claimed[r0, c0:c1 + 1] = True
        elif r1 - r0 > 1 and frac(m, r0, r0, c0, c1) < 0.5:
            r0 += 1
        else:
            break
    for _ in range(REFINE_PX):                      # bottom face (y0)
        if frac(free, r1 + 1, r1 + 1, c0, c1) >= 0.5:
            r1 += 1
            claimed[r1, c0:c1 + 1] = True
        elif r1 - r0 > 1 and frac(m, r1, r1, c0, c1) < 0.5:
            r1 -= 1
        else:
            break
    for _ in range(REFINE_PX):                      # left face (x0)
        if frac(free, r0, r1, c0 - 1, c0 - 1) >= 0.5:
            c0 -= 1
            claimed[r0:r1 + 1, c0] = True
        elif c1 - c0 > 1 and frac(m, r0, r1, c0, c0) < 0.5:
            c0 += 1
        else:
            break
    for _ in range(REFINE_PX):                      # right face (x1)
        if frac(free, r0, r1, c1 + 1, c1 + 1) >= 0.5:
            c1 += 1
            claimed[r0:r1 + 1, c1] = True
        elif c1 - c0 > 1 and frac(m, r0, r1, c1, c1) < 0.5:
            c1 -= 1
        else:
            break
    r.x0, r.x1 = grid.col_x(c0), grid.col_x(c1 + 1)
    r.y0, r.y1 = grid.row_y(r1 + 1), grid.row_y(r0)


def _primary_prims(prims: list[WallPrim]) -> set[int]:
    """1-based indices of the primitives that can carry a wall on their own: every non-hatch primitive, and the
    hatch groups of the page's main hatch directions (>= PRIMARY_SHARE of the lines of the most used direction).
    real01 hatches its walls at 135 deg; the coffee table frame, the round piece and the telephone keypads are solid
    combs of 0/90 deg lines, a secondary style that only counts where it touches a wall of the main style."""
    counts: dict[int, int] = {}
    for p in prims:
        if p.kind == "hatch" and p.direction_deg is not None:
            key = int(round(p.direction_deg / 5.0)) % 36
            counts[key] = counts.get(key, 0) + len(p.lines)
    top = max(counts.values()) if counts else 0
    main = {k for k, n in counts.items() if n >= PRIMARY_SHARE * top}
    out = set()
    for k, p in enumerate(prims, start=1):
        if p.kind != "hatch" or p.direction_deg is None or int(round(p.direction_deg / 5.0)) % 36 in main:
            out.add(k)
    return out


PRIMARY_SHARE = 0.25


def _filter_components(rects: list[_Rect], m: np.ndarray, index: np.ndarray, grid: _Grid, primary: set):
    """Keep a mask component when it has an elongated rectangle (length >= 3 x thickness, thickness >= MIN_WALL_M)
    drawn by a primary primitive, or when it touches a kept component (§2.4.2); thinner rectangles of kept
    components are dropped too. Returns (kept rects, [(note, region mask)])."""
    dropped_regions = []
    n, lab = cv2.connectedComponents(m.astype(np.uint8), connectivity=8)
    by_comp: dict[int, list[_Rect]] = {}
    for r in rects:
        c0, r0 = grid.to_px(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
        comp = int(lab[min(max(r0, 0), grid.rows - 1), min(max(c0, 0), grid.cols - 1)])
        by_comp.setdefault(comp, []).append(r)
    kept_comps = set()
    weak = []
    for comp, rs in by_comp.items():
        strong = [r for r in rs if r.thickness >= MIN_WALL_M - 1e-9 and r.length >= MIN_ELONGATION * r.thickness
                  and (not r.prims or r.prims & primary)]
        if strong:
            kept_comps.add(comp)
        else:
            weak.append(comp)
    # A weak component touching a kept one (within TOUCH_M) stays.
    if weak and kept_comps:
        kept_mask = np.isin(lab, list(kept_comps)).astype(np.uint8)
        k = max(1, int(math.ceil(TOUCH_M / grid.px)))
        grown = cv2.dilate(kept_mask, np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
        for comp in list(weak):
            if (grown & (lab == comp)).any():
                kept_comps.add(comp)
                weak.remove(comp)
    out = []
    for comp, rs in by_comp.items():
        if comp in kept_comps:
            for r in rs:
                if r.thickness >= MIN_WALL_M - 1e-9:
                    out.append(r)
                else:
                    region = _rect_region(r, grid) & (lab == comp)
                    dropped_regions.append((f"wall-like strip {r.length:.2f} x {r.thickness:.3f} m thinner than "
                                            f"{MIN_WALL_M} m: not a wall", region))
        else:
            ext = _comp_extent(rs)
            dropped_regions.append((f"wall-like component {ext[0]:.2f} x {ext[1]:.2f} m without an elongated "
                                    f"main-style part dropped", lab == comp))
    return out, dropped_regions


def _comp_extent(rs: list[_Rect]) -> tuple[float, float]:
    return (max(r.x1 for r in rs) - min(r.x0 for r in rs), max(r.y1 for r in rs) - min(r.y0 for r in rs))


def _rect_region(r: _Rect, grid: _Grid) -> np.ndarray:
    region = np.zeros((grid.rows, grid.cols), bool)
    c0, r0 = grid.to_px((r.x0 + 1e-9, r.y1 - 1e-9))
    c1, r1 = grid.to_px((r.x1 - 1e-9, r.y0 + 1e-9))
    region[max(r0, 0):r1 + 1, max(c0, 0):c1 + 1] = True
    return region


def _union_iou(rects: list[_Rect], m: np.ndarray, grid: _Grid) -> tuple[float, float]:
    if not m.any():
        return 1.0, 0.0
    u = np.zeros(m.shape, bool)
    for r in rects:
        u |= _rect_region(r, grid)
    inter = (u & m).sum()
    union = (u | m).sum()
    missed = (m & ~u).sum() * grid.px * grid.px
    return (inter / union if union else 1.0), float(missed)


def _angled_warning(rects: list[_Rect], m: np.ndarray, grid: _Grid, info: dict) -> None:
    """Large leftovers of the mask not covered by axis rectangles: walls at another angle."""
    u = np.zeros(m.shape, bool)
    for r in rects:
        u |= _rect_region(r, grid)
    rest = (m & ~u).astype(np.uint8)
    rest = cv2.morphologyEx(rest, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(rest, connectivity=8)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA] * grid.px * grid.px
        if area < 0.05:
            continue
        ys, xs = np.nonzero(lab == i)
        (_, _), (w, h), ang = cv2.minAreaRect(np.column_stack([xs, ys]).astype(np.float32))
        ang = ang % 90.0
        off = min(ang, 90.0 - ang)
        cx, cy = grid.col_x(xs.mean()), grid.row_y(ys.mean())
        if off > ANGLED_DEG:
            info["warnings"].append(f"angled wall not modelled ({area:.2f} m² at {off:.0f} deg near "
                                    f"({cx:.2f}, {cy:.2f}) m)")


def _snap(r: _Rect, segments) -> int:
    """Move each face of ``r`` to a parallel outline segment within SNAP_M along >= SNAP_COVER of it."""
    n = 0
    faces = (("y0", "h"), ("y1", "h"), ("x0", "v"), ("x1", "v"))
    new = {}
    for attr, fdir in faces:
        if fdir == "h":
            pos, lo, hi = getattr(r, attr), r.x0, r.x1
        else:
            pos, lo, hi = getattr(r, attr), r.y0, r.y1
        best = _snap_face(pos, lo, hi, fdir, segments)
        if best is not None:
            new[attr] = best
            n += 1
    old = (r.x0, r.y0, r.x1, r.y1)
    for attr, value in new.items():
        setattr(r, attr, value)
    if r.x1 - r.x0 < 0.01 or r.y1 - r.y0 < 0.01:     # never collapse or invert a rectangle
        r.x0, r.y0, r.x1, r.y1 = old
        n = 0
    r.snapped = n
    return n


def _snap_face(pos: float, lo: float, hi: float, fdir: str, segments) -> Optional[float]:
    length = hi - lo
    if length <= 1e-9:
        return None
    by_offset: dict[float, list[tuple[float, float]]] = {}
    for a, b in segments:
        if fdir == "h":
            if _angle_diff180(_angle_mod180(a, b), 0.0) > SEGMENT_ANGLE_TOL_DEG:
                continue
            off = (a[1] + b[1]) / 2.0
            s0, s1 = sorted((a[0], b[0]))
        else:
            if _angle_diff180(_angle_mod180(a, b), 90.0) > SEGMENT_ANGLE_TOL_DEG:
                continue
            off = (a[0] + b[0]) / 2.0
            s0, s1 = sorted((a[1], b[1]))
        if abs(off - pos) > SNAP_M or s1 < lo or s0 > hi:
            continue
        key = round(off / 0.002) * 0.002
        by_offset.setdefault(key, []).append((max(s0, lo), min(s1, hi)))
    best = None
    for key, spans in by_offset.items():
        cover = _covered(spans)
        if cover >= SNAP_COVER * length:
            if best is None or abs(key - pos) < abs(best[0] - pos) - 1e-9 or \
                    (abs(abs(key - pos) - abs(best[0] - pos)) <= 1e-9 and cover > best[1]):
                best = (key, cover)
    if best is None:
        return None
    return best[0]


def _covered(spans: list[tuple[float, float]]) -> float:
    total, end = 0.0, -math.inf
    for s0, s1 in sorted(spans):
        if s1 <= end:
            continue
        total += s1 - max(s0, end)
        end = s1
    return total


def _round_thickness(r: _Rect) -> None:
    """Thickness to the nearest 5 mm about the centre line."""
    t = r.thickness
    tr = max(THICKNESS_ROUND_M, round(t / THICKNESS_ROUND_M) * THICKNESS_ROUND_M)
    if r.axis == "h":
        c = (r.y0 + r.y1) / 2.0
        r.y0, r.y1 = c - tr / 2.0, c + tr / 2.0
    else:
        c = (r.x0 + r.x1) / 2.0
        r.x0, r.x1 = c - tr / 2.0, c + tr / 2.0


def _wall_item(r: _Rect, prims: list[WallPrim], theta: float, file_rel: str, page_no: int,
               units_to_m: Optional[float]) -> WallItem:
    if r.axis == "h":
        cy = (r.y0 + r.y1) / 2.0
        start, end = (r.x0, cy), (r.x1, cy)
    else:
        cx = (r.x0 + r.x1) / 2.0
        start, end = (cx, r.y0), (cx, r.y1)
    corners = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
    if abs(theta) > 0.5:
        start, end = _rot(start, theta), _rot(end, theta)
        corners = [_rot(p, theta) for p in corners]
    used = [prims[k - 1] for k in sorted(r.prims) if 0 < k <= len(prims)]
    if used:
        method = "raster" if all(p.method == "raster" for p in used) else "vector"
        confidence = min(p.confidence for p in used)
        entity = ",".join(p.entity for p in used)
    else:
        method, confidence, entity = "vector", 0.5, "mask"
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    box = [min(xs), min(ys), max(xs), max(ys)]
    if units_to_m:
        box = [v / units_to_m for v in box]
    box = [round(v, 3) for v in box]
    pixel_box = box if (method == "raster" and units_to_m) else None
    ev = B.evidence(file_rel, method, round(confidence, 3), page=page_no, entity=entity, pixel_box=pixel_box)
    start = (round(start[0], 4), round(start[1], 4))
    end = (round(end[0], 4), round(end[1], 4))
    return WallItem(start=start, end=end, thickness=round(r.thickness, 4), box=box, entity=entity, evidence=ev)


def thickness_classes(walls: list[WallItem]) -> list[dict]:
    """Wall thicknesses clustered within 15 mm: ``[{"thickness", "count", "length_m"}]`` by length."""
    items = sorted((w.thickness, math.dist(w.start, w.end)) for w in walls)
    classes: list[list[tuple[float, float]]] = []
    for t, length in items:
        if classes and t - classes[-1][0][0] <= THICKNESS_CLASS_M:
            classes[-1].append((t, length))
        else:
            classes.append([(t, length)])
    out = []
    for cls in classes:
        total = sum(length for _, length in cls)
        mean = sum(t * length for t, length in cls) / total if total > 0 else cls[0][0]
        out.append({"thickness": round(mean, 3), "count": len(cls), "length_m": round(total, 2)})
    out.sort(key=lambda c: -c["length_m"])
    return out
