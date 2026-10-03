"""Dimension texts, their dimension lines and the scale of a generic page (docs/milestone7.md §2.3).

**Dimensions.** A text run that parses as one length (``wenart.units``: ``50'``, ``14'-0"``, ``4,30``) is a
dimension text when a dimension line goes with it:

- (a) *gap*: two collinear straight strokes whose gap midpoint lies inside the text box, with the text
  centre within ``GAP_AXIS_TOL`` × text height of their axis. The text belongs to that line whatever its
  rotation (real01's upright ``30'`` sits in the gap of a vertical line);
- (b) *parallel*: a straight stroke parallel to the text baseline within ``PARALLEL_DIST`` × text height,
  the nearest one whose marks bracket the text.

The measured span runs between two **end marks** on the line's axis that bracket the text: filled
triangles (arrowheads, the tip is the end), short 30–60° strokes (ticks, their centre is the end), dots
(their centre), or, only at the line's own ends, perpendicular extension lines (where they cross the
axis). Arrowheads, ticks and dots between the ends split a chain into its dimensions; a cluster of
tick-like strokes (a hatch) is no tick. Measured = distance between the two ends, in page units.
DXF ``DimensionPrim``s with a text override come measured from geometry (§5.2); without an override their
text is their own measurement and says nothing about the scale.

**Scale** (``provisional_scale``): first rule that holds wins.

1. DXF with known drawing units (``units_to_m``) -> ``dxf_insunits``.
2. A scale note (``ÖLÇEK 1/100``, ``SCALE 1:50``, ``1/4" = 1'-0"``) -> ``pdf_scale_text``. As in
   ``pdf_extract._resolve_scale``: confidence 1.0 when the dimension median agrees within 1 %, 0.9 without
   dimensions, 0.5 when they disagree (the note is kept). On raster pages a note counts only with a
   verified pixel size (``page.dpi``) and never against the dimensions.
3. ≥ ``MIN_AGREEING_DIMENSIONS`` ratios within 1 % of the median and the majority -> ``dimension_text``
   (0.9, or 0.7 with disagreeing texts), the rule of ``pdf_extract`` reproduced exactly.
4. Two dimensions within 0.5 % (the majority) -> **provisional** ``dimension_text``, their mean.
5. One dimension -> **provisional** ``dimension_text``.

``confirm_scale`` runs after the faces exist: a provisional scale from two dimensions needs ≥ 2 room-size
labels within 5 % of their faces (confidence 0.85), from one dimension ≥ 3 (0.7, warning); otherwise the
scale is None ("scale not corroborated: ...", the pipeline stops with ``needs_review``). Size labels alone
never give a scale. Every dimension off the chosen ratio by more than 1 % is a ``scale_disagreement``
conflict.
"""
from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from wenart import building as B
from wenart import units
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.ingest.model import METRES_PER_POINT, parse_scale_text

# Dimension finder (multiples of the text height h unless noted)
ANGLE_TOL_DEG = 1.0           # parallel / collinear strokes
GAP_AXIS_TOL = 0.5            # (a) text centre to the axis of the two pieces
GAP_BOX_GROW = 0.1            # (a) the gap midpoint may lie this far outside the text box
PARALLEL_DIST = 2.5           # (b) text centre to a parallel dimension line
AXIS_TOL = 0.15               # a mark (tip, tick centre, dot, crossing) lies this close to the axis
MARK_REACH = 1.5              # a mark may lie this far beyond a line end (arrowheads drawn outside)
TICK_LEN = (0.1, 2.0)         # tick length range
TICK_ANGLE = (30.0, 60.0)     # degrees between tick and line
HATCH_SPACING = 0.5           # >= 3 tick-like strokes this close along the line are a hatch, not ticks
DOT_MAX = 0.5                 # dot size
ARROW_MAX = 2.0               # arrowhead longest side
EXT_ANGLE_TOL_DEG = 2.0       # extension lines: 90 +- this to the line
EXT_MIN_LEN = 0.3             # extension line length
MIN_SPAN = 0.2                # shortest measured span
STRAIGHT_TOL = 1e-3           # relative: a polyline whose points lie this close to its chord is straight
STRONG_MARKS = ("arrow", "tick", "dot")
MARK_RANK = {"arrow": 0, "tick": 1, "dot": 2, "extension": 3}

# Scale rules
SCALE_AGREEMENT = 0.01        # ratios agree within 1 % (pdf_extract.SCALE_AGREEMENT)
PAIR_AGREEMENT = 0.005        # two dimensions agree within 0.5 %
MIN_AGREEING_DIMENSIONS = 3   # pdf_extract.MIN_AGREEING_DIMENSIONS
SCALE_NOTE_DISPUTED_CONFIDENCE = 0.5
LABEL_AGREEMENT = 0.05        # a room-size label corroborates within 5 % per side
TWO_DIM_LABELS, TWO_DIM_CONFIDENCE = 2, 0.85
ONE_DIM_LABELS, ONE_DIM_CONFIDENCE = 3, 0.7
INCH_M = 0.0254

# Bare integer dimension texts on metric pages (``15240``, ``345``): the metre reading must make a plausible page,
# else the millimetre or centimetre reading that alone does is taken (assumed). Printed text is 2-5 mm tall at
# 1:20-1:200, i.e. 0.04-1.0 m in the building; a plan shows 2 m to 2 km.
UNIT_READINGS = (("cm", 0.01), ("mm", 0.001))
TEXT_HEIGHT_M = (0.04, 1.0)
DRAWING_EXTENT_M = (2.0, 2000.0)

# Imperial scale notes: <paper inches> = <real feet-inches> ("1/4\" = 1'-0\"", "1\" = 10'").
_INCH_MARK = r"(?:\"|”|″|''|in\.?|inch(?:es)?)"
_IMPERIAL_NOTE_HINT_RE = re.compile(rf"\d\s*{_INCH_MARK}\s*=", re.IGNORECASE)
_IMPERIAL_NOTE_RE = re.compile(
    rf"(?P<paper>\d+\s*/\s*\d+|\d*\.\d+|\d+)\s*{_INCH_MARK}\s*=\s*"
    rf"(?P<real>\d+(?:\.\d+)?\s*(?:'|’|′|ft\.?|feet|foot)(?:\s*-?\s*\d+(?:\s+\d+/\d+)?\s*{_INCH_MARK}?)?)",
    re.IGNORECASE)


@dataclass
class DimCandidate:
    """One dimension: its text, the measured span (page units) and the strokes that draw it."""
    text: str
    length: units.Length
    p1: tuple[float, float]                   # page units, the two measured ends
    p2: tuple[float, float]
    measured_units: float                     # |p2 - p1|
    end_marks: tuple[str, str]                # per end: arrow | tick | dot | extension | dimension
    stroke_ids: list[str]                     # dimension line piece(s) and the arrowheads / ticks / dots used
    text_id: str
    source: str = "vector"                    # text source (vector | ocr); DXF dimension entities: vector
    how: str = "gap"                          # gap | parallel | dimension_entity
    extension_ids: list[str] = field(default_factory=list)   # extension lines at the ends (may be wall faces)
    text_evidence: list[dict] = field(default_factory=list)  # the text run's own evidence (OCR model, box, dpi)
    unit_assumed: Optional[str] = None        # "mm" / "cm": a bare integer re-read (``unit_reading``)
    unit_note: Optional[str] = None           # why (or why the unit of the bare integers stays unclear)

    @property
    def ratio(self) -> float:
        """Metres per page unit this dimension implies (printed / measured)."""
        return self.length.metres / self.measured_units


# --------------------------------------------------------------------------
# Stroke geometry
# --------------------------------------------------------------------------

@dataclass
class _Seg:
    stroke: Stroke
    a: tuple[float, float]
    b: tuple[float, float]


def _straight(stroke: Stroke) -> Optional[_Seg]:
    """A straight open stroke as one segment (lines, and polylines/curves whose points lie on their chord)."""
    if stroke.closed or stroke.fill is not None or len(stroke.pts) < 2 or stroke.kind in ("arc", "circle"):
        return None
    a, b = stroke.pts[0], stroke.pts[-1]
    length = math.dist(a, b)
    if length <= 0:
        return None
    if len(stroke.pts) > 2:
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        for p in stroke.pts[1:-1]:
            if abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) > STRAIGHT_TOL * length:
                return None
    return _Seg(stroke, (float(a[0]), float(a[1])), (float(b[0]), float(b[1])))


def _distinct_vertices(stroke: Stroke) -> list[tuple[float, float]]:
    pts = [(float(x), float(y)) for x, y in stroke.pts]
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-9:
        pts = pts[:-1]
    out: list[tuple[float, float]] = []
    for p in pts:
        if not out or math.dist(p, out[-1]) > 1e-9:
            out.append(p)
    return out


def _angle_mod180(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def _angle_diff180(x: float, y: float) -> float:
    d = abs(x - y) % 180.0
    return min(d, 180.0 - d)


class _Index:
    """The page's strokes, split by what they can be in a dimension, with numpy boxes for fast lookups."""

    def __init__(self, page: GenericPage):
        self.segs: list[_Seg] = []
        self.blobs: list[Stroke] = []          # closed / filled / tiny strokes: arrowheads and dots
        for s in page.strokes:
            seg = _straight(s)
            if seg is not None:
                self.segs.append(seg)
            elif s.pts:
                self.blobs.append(s)
        if self.segs:
            arr = np.array([[g.a[0], g.a[1], g.b[0], g.b[1]] for g in self.segs], dtype=float)
        else:
            arr = np.zeros((0, 4))
        self.seg_xy = arr
        self.seg_box = np.column_stack([np.minimum(arr[:, 0], arr[:, 2]), np.minimum(arr[:, 1], arr[:, 3]),
                                        np.maximum(arr[:, 0], arr[:, 2]), np.maximum(arr[:, 1], arr[:, 3])])
        self.blob_box = (np.array([s.bbox() for s in self.blobs], dtype=float) if self.blobs
                         else np.zeros((0, 4)))

    def segs_near(self, box, grow: float) -> list[int]:
        x0, y0, x1, y1 = box
        b = self.seg_box
        hit = (b[:, 2] >= x0 - grow) & (b[:, 0] <= x1 + grow) & (b[:, 3] >= y0 - grow) & (b[:, 1] <= y1 + grow)
        return [int(i) for i in np.nonzero(hit)[0]]

    def blobs_near(self, box, grow: float) -> list[int]:
        x0, y0, x1, y1 = box
        b = self.blob_box
        if not len(b):
            return []
        hit = (b[:, 2] >= x0 - grow) & (b[:, 0] <= x1 + grow) & (b[:, 3] >= y0 - grow) & (b[:, 1] <= y1 + grow)
        return [int(i) for i in np.nonzero(hit)[0]]


# --------------------------------------------------------------------------
# End marks along a line
# --------------------------------------------------------------------------

@dataclass
class _Mark:
    kind: str
    t: float                                   # position along the axis (page units from the line start)
    stroke_id: str


class _Axis:
    def __init__(self, a, b):
        self.a = a
        self.length = math.dist(a, b)
        self.u = ((b[0] - a[0]) / self.length, (b[1] - a[1]) / self.length)
        self.n = (-self.u[1], self.u[0])
        self.angle = _angle_mod180(a, b)

    def t(self, p) -> float:
        return (p[0] - self.a[0]) * self.u[0] + (p[1] - self.a[1]) * self.u[1]

    def off(self, p) -> float:
        return (p[0] - self.a[0]) * self.n[0] + (p[1] - self.a[1]) * self.n[1]

    def point(self, t: float) -> tuple[float, float]:
        return (self.a[0] + self.u[0] * t, self.a[1] + self.u[1] * t)


def _arrow_mark(stroke: Stroke, axis: _Axis, h: float, line_ids: set[str]) -> Optional[_Mark]:
    if stroke.id in line_ids or not (stroke.closed or stroke.fill is not None):
        return None
    verts = _distinct_vertices(stroke)
    if len(verts) != 3:
        return None
    if max(math.dist(verts[i], verts[(i + 1) % 3]) for i in range(3)) > ARROW_MAX * h:
        return None
    tol = AXIS_TOL * h
    for i, tip in enumerate(verts):
        if abs(axis.off(tip)) > tol:
            continue
        b1, b2 = verts[(i + 1) % 3], verts[(i + 2) % 3]
        o1, o2 = axis.off(b1), axis.off(b2)
        if o1 * o2 >= 0 or min(abs(o1), abs(o2)) < 0.3 * max(abs(o1), abs(o2)):
            continue                            # the base must straddle the axis, roughly symmetric
        t_tip, t1, t2 = axis.t(tip), axis.t(b1), axis.t(b2)
        if abs(t1 - t2) > 0.5 * abs(o1 - o2) + tol:
            continue                            # base roughly perpendicular to the axis
        t_base = (t1 + t2) / 2.0
        lo, hi = min(t_tip, t_base), max(t_tip, t_base)
        if hi < -tol or lo > axis.length + tol:
            continue                            # must touch the line
        return _Mark("arrow", t_tip, stroke.id)
    return None


def _dot_mark(stroke: Stroke, axis: _Axis, h: float) -> Optional[_Mark]:
    x0, y0, x1, y1 = stroke.bbox()
    size = max(x1 - x0, y1 - y0)
    if size > DOT_MAX * h:
        return None
    zero_length = size <= 1e-9
    round_shape = stroke.kind in ("circle",) or (stroke.arc is not None and stroke.closed) or \
        (stroke.closed and len(_distinct_vertices(stroke)) >= 5)
    if not (zero_length or round_shape):
        return None
    centre = tuple(stroke.arc["center"]) if stroke.arc else ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
    if abs(axis.off(centre)) > AXIS_TOL * h:
        return None
    return _Mark("dot", axis.t(centre), stroke.id)


def _seg_marks(seg: _Seg, axis: _Axis, h: float) -> list[_Mark]:
    out = []
    length = math.dist(seg.a, seg.b)
    diff = _angle_diff180(_angle_mod180(seg.a, seg.b), axis.angle)
    tol = AXIS_TOL * h
    if TICK_LEN[0] * h <= length <= TICK_LEN[1] * h and TICK_ANGLE[0] <= diff <= TICK_ANGLE[1]:
        mid = ((seg.a[0] + seg.b[0]) / 2.0, (seg.a[1] + seg.b[1]) / 2.0)
        if abs(axis.off(mid)) <= tol:
            out.append(_Mark("tick", axis.t(mid), seg.stroke.id))
    if abs(diff - 90.0) <= EXT_ANGLE_TOL_DEG and length >= EXT_MIN_LEN * h:
        oa, ob = axis.off(seg.a), axis.off(seg.b)
        if min(oa, ob) <= tol and max(oa, ob) >= -tol:
            # crossing point of the extension line with the axis
            if abs(ob - oa) > 1e-12:
                k = -oa / (ob - oa)
                k = min(max(k, 0.0), 1.0)
            else:
                k = 0.5
            cross = (seg.a[0] + (seg.b[0] - seg.a[0]) * k, seg.a[1] + (seg.b[1] - seg.a[1]) * k)
            out.append(_Mark("extension", axis.t(cross), seg.stroke.id))
    return out


def _marks_on(axis: _Axis, index: _Index, h: float, line_ids: set[str]) -> list[_Mark]:
    reach = MARK_REACH * h
    p0, p1 = axis.point(-reach), axis.point(axis.length + reach)
    box = (min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]))
    marks: list[_Mark] = []
    for i in index.segs_near(box, ARROW_MAX * h):
        seg = index.segs[i]
        if seg.stroke.id in line_ids:
            continue
        marks.extend(_seg_marks(seg, axis, h))
    for i in index.blobs_near(box, ARROW_MAX * h):
        stroke = index.blobs[i]
        mark = _arrow_mark(stroke, axis, h, line_ids) or _dot_mark(stroke, axis, h)
        if mark is not None:
            marks.append(mark)
    marks = [m for m in marks if -reach <= m.t <= axis.length + reach]
    # A comb of tick-like strokes is a hatch (a wall crossing the line), not ticks.
    ticks = sorted((m for m in marks if m.kind == "tick"), key=lambda m: m.t)
    hatch = set()
    for i, m in enumerate(ticks):
        close = [o for o in ticks if abs(o.t - m.t) <= HATCH_SPACING * h]
        if len(close) >= 3:
            hatch.update(id(o) for o in close)
    return [m for m in marks if id(m) not in hatch]


def _bracket(axis: _Axis, marks: list[_Mark], t_text: float, h: float):
    """The two end marks around ``t_text``: the nearest strong mark on each side; an extension line only
    at the line's own end. Returns ((t, kind, ids, ext_ids), (t, kind, ids, ext_ids)) or None."""
    tol = AXIS_TOL * h
    strong = [m for m in marks if m.kind in STRONG_MARKS]
    ext = [m for m in marks if m.kind == "extension"]

    def side(lower: bool):
        if lower:
            cands = [m for m in strong if m.t < t_text]
            best_t = max((m.t for m in cands), default=None)
            if best_t is None:
                at_end = [m for m in ext if abs(m.t) <= tol and m.t < t_text]
                best_t = max((m.t for m in at_end), default=None)
        else:
            cands = [m for m in strong if m.t > t_text]
            best_t = min((m.t for m in cands), default=None)
            if best_t is None:
                at_end = [m for m in ext if abs(m.t - axis.length) <= tol and m.t > t_text]
                best_t = min((m.t for m in at_end), default=None)
        if best_t is None:
            return None
        here = [m for m in marks if abs(m.t - best_t) <= tol]
        kind = min((m.kind for m in here), key=lambda k: MARK_RANK[k])
        ids = sorted({m.stroke_id for m in here if m.kind != "extension"})
        ext_ids = sorted({m.stroke_id for m in here if m.kind == "extension"})
        return best_t, kind, ids, ext_ids

    lo, hi = side(True), side(False)
    if lo is None or hi is None or hi[0] - lo[0] < MIN_SPAN * h:
        return None
    return lo, hi


# --------------------------------------------------------------------------
# Finding dimensions
# --------------------------------------------------------------------------

def _text_height(run: TextRun) -> float:
    if run.height and run.height > 0:
        return float(run.height)
    x0, y0, x1, y1 = run.box
    return max(min(x1 - x0, y1 - y0), 1e-9)


def _inside(p, box, grow: float) -> bool:
    return box[0] - grow <= p[0] <= box[2] + grow and box[1] - grow <= p[1] <= box[3] + grow


def _gap_candidates(run: TextRun, h: float, index: _Index) -> list[tuple[float, _Axis, list[str]]]:
    """(a): pairs of collinear strokes whose gap midpoint lies in the text box -> (rank, axis, line ids)."""
    box = run.box
    c = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
    diag = math.dist(box[:2], box[2:])
    near = []
    for i in index.segs_near(box, diag + h):
        seg = index.segs[i]
        axis = _Axis(seg.a, seg.b)
        if abs(axis.off(c)) > GAP_AXIS_TOL * h:
            continue
        near.append((seg, axis))
    out = []
    for i, (s1, ax1) in enumerate(near):
        for s2, _ in near[i + 1:]:
            if _angle_diff180(ax1.angle, _angle_mod180(s2.a, s2.b)) > ANGLE_TOL_DEG:
                continue
            if max(abs(ax1.off(s2.a)), abs(ax1.off(s2.b))) > AXIS_TOL * h:
                continue
            t1 = sorted((ax1.t(s1.a), ax1.t(s1.b)))
            t2 = sorted((ax1.t(s2.a), ax1.t(s2.b)))
            if t1[1] <= t2[0]:
                inner, outer = (t1[1], t2[0]), (t1[0], t2[1])
            elif t2[1] <= t1[0]:
                inner, outer = (t2[1], t1[0]), (t2[0], t1[1])
            else:
                continue                        # overlapping pieces are no gap
            mid = ax1.point((inner[0] + inner[1]) / 2.0)
            if not _inside(mid, box, GAP_BOX_GROW * h):
                continue
            axis = _Axis(ax1.point(outer[0]), ax1.point(outer[1]))
            out.append((abs(axis.off(c)), axis, [s1.stroke.id, s2.stroke.id]))
    out.sort(key=lambda x: x[0])
    return out


def _parallel_candidates(run: TextRun, h: float, index: _Index) -> list[tuple[float, _Axis, list[str]]]:
    """(b): straight strokes parallel to the baseline within ``PARALLEL_DIST`` x h -> (distance, axis, ids)."""
    box = run.box
    c = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
    rot = run.rotation_deg % 180.0
    out = []
    for i in index.segs_near(box, PARALLEL_DIST * h):
        seg = index.segs[i]
        if _angle_diff180(_angle_mod180(seg.a, seg.b), rot) > ANGLE_TOL_DEG:
            continue
        axis = _Axis(seg.a, seg.b)
        dist = abs(axis.off(c))
        if dist > PARALLEL_DIST * h:
            continue
        t = axis.t(c)
        if t < 0.0 or t > axis.length:
            continue
        out.append((dist, axis, [seg.stroke.id]))
    out.sort(key=lambda x: x[0])
    return out


def _evidence_method(source: str) -> str:
    return "ocr" if source == "ocr" else "vector"


def find_dimensions(page: GenericPage) -> list[DimCandidate]:
    """Every dimension of the page (§2.3): text runs that parse as one length with a marked dimension line,
    and DXF dimension entities with a text override. Page units; in text order."""
    system = LB.page_unit_system(page.texts)
    index = _Index(page)
    options = []           # (rank, text order, DimCandidate, span key)
    for order, run in enumerate(page.texts):
        if run.source == "ai" or not run.text:
            continue                            # VLM texts never make a scale (§4.3)
        length = units.parse_length(run.text, system)
        if length is None or length.metres <= 0:
            continue
        h = _text_height(run)
        c = ((run.box[0] + run.box[2]) / 2.0, (run.box[1] + run.box[3]) / 2.0)
        for case, cands in (("gap", _gap_candidates(run, h, index)),
                            ("parallel", _parallel_candidates(run, h, index))):
            for dist, axis, line_ids in cands:
                marks = _marks_on(axis, index, h, set(line_ids))
                bracket = _bracket(axis, marks, axis.t(c), h)
                if bracket is None:
                    continue
                (t0, k0, ids0, ext0), (t1, k1, ids1, ext1) = bracket
                p1, p2 = axis.point(t0), axis.point(t1)
                dim = DimCandidate(text=run.text.strip(), length=length, p1=p1, p2=p2,
                                   measured_units=t1 - t0, end_marks=(k0, k1),
                                   stroke_ids=list(dict.fromkeys(line_ids + ids0 + ids1)), text_id=run.id,
                                   source=run.source, how=case, extension_ids=sorted(set(ext0 + ext1)),
                                   text_evidence=[dict(e) for e in run.evidence])
                rank = (0 if case == "gap" else 1, dist / h)
                options.append((rank, order, dim, _span_key(line_ids, t0, t1)))
    # Greedy: the best (text, line) pairs first; a text and a measured span are used once.
    options.sort(key=lambda o: (o[0], o[1]))
    used_texts: set[int] = set()
    used_spans: set = set()
    chosen: list[tuple[int, DimCandidate]] = []
    for rank, order, dim, span in options:
        if order in used_texts or span in used_spans:
            continue
        used_texts.add(order)
        used_spans.add(span)
        chosen.append((order, dim))
    chosen.sort(key=lambda x: x[0])
    found = [dim for _, dim in chosen]
    for prim in page.dimensions:
        if not prim.text or "<>" in prim.text or prim.measured_units <= 0:
            continue                            # the measurement itself: no information about the scale
        length = units.parse_length(prim.text, system)
        if length is None or length.metres <= 0:
            continue
        found.append(DimCandidate(text=prim.text.strip(), length=length, p1=tuple(prim.p1), p2=tuple(prim.p2),
                                  measured_units=prim.measured_units, end_marks=("dimension", "dimension"),
                                  stroke_ids=[prim.id], text_id=prim.id, how="dimension_entity"))
    unit_reading(page, found, system)
    return found


def _median_text_height(page: GenericPage) -> Optional[float]:
    heights = [_text_height(run) for run in page.texts if run.source != "ai" and run.text and run.text.strip()]
    return statistics.median(heights) if heights else None


def _drawing_extent(page: GenericPage) -> Optional[float]:
    xs = [p[0] for st in page.strokes for p in st.pts]
    ys = [p[1] for st in page.strokes for p in st.pts]
    if not xs:
        return max(page.size) if page.size else None
    return max(max(xs) - min(xs), max(ys) - min(ys))


def unit_reading(page: GenericPage, dims: list[DimCandidate], system: str) -> Optional[str]:
    """Bare integer dimension texts on a metric page (review2 ingest-7): ``15240`` is metres to the parser, but
    metric CAD prints millimetres (or centimetres) that way. When every dimension text is a bare integer and the
    metre reading gives an implausible page (text taller than 1 m or the drawing wider than 2 km in the building),
    the one reading of cm and mm that gives plausible text heights (0.04-1.0 m) and drawing size (2-2000 m) is
    taken: the dimensions' lengths are re-read in place, ``unit_assumed`` and ``unit_note`` record it. With no or
    two such readings nothing changes and ``unit_note`` names the unit problem (the review reasons repeat it).
    Returns the note (None when the metre reading stands)."""
    if system != "metric" or not dims:
        return None
    if not all(d.length.system == "metric" and units.is_bare_integer(d.text) for d in dims):
        return None
    ratios = [d.length.metres / d.measured_units for d in dims if d.measured_units > 0 and d.length.metres > 0]
    height, extent = _median_text_height(page), _drawing_extent(page)
    if not ratios or not height or not extent:
        return None
    mpu = statistics.median(ratios)

    def plausible(factor: float) -> bool:
        return (TEXT_HEIGHT_M[0] <= height * mpu * factor <= TEXT_HEIGHT_M[1]
                and DRAWING_EXTENT_M[0] <= extent * mpu * factor <= DRAWING_EXTENT_M[1])

    if plausible(1.0):
        return None
    fits = [(name, factor) for name, factor in UNIT_READINGS if plausible(factor)]
    shown = ", ".join(repr(d.text) for d in dims[:4]) + (", ..." if len(dims) > 4 else "")
    as_metres = (f"read as metres they make the drawing {extent * mpu:,.0f} m wide with {height * mpu:,.1f} m tall "
                 f"text")
    if len(fits) == 1:
        name, factor = fits[0]
        note = (f"dimension texts are bare integers on a metric page ({shown}); {as_metres}: read as {name} "
                f"(assumed: only that unit gives {height * mpu * factor:.2f} m text and a "
                f"{extent * mpu * factor:.1f} m drawing)")
        for d in dims:
            d.length = units.read_as(d.length, name)
            d.unit_assumed = name
            d.unit_note = note
        return note
    which = " or ".join(name for name, _ in fits) if fits else "no metric unit"
    note = (f"likely a unit problem: the dimension texts are bare integers ({shown}) and {as_metres}; "
            f"{which} would fit, so the unit cannot be told (metres kept)")
    for d in dims:
        d.unit_note = note
    return note


def _unit_note(dims: list[DimCandidate]) -> Optional[str]:
    return next((d.unit_note for d in dims if d.unit_note), None)


def _span_key(line_ids: list[str], t0: float, t1: float):
    return (tuple(sorted(line_ids)), round(t0, 3), round(t1, 3))


# --------------------------------------------------------------------------
# Scale notes
# --------------------------------------------------------------------------

def note_ratio(text: str) -> Optional[float]:
    """Drawing scale of a note as real length / paper length: ``ÖLÇEK 1/100`` -> 100, ``SCALE 1:50`` -> 50,
    ``1/4" = 1'-0"`` -> 48, ``1" = 10'`` -> 120; None when the text is no scale note."""
    # Imperial first: "SCALE 1/4\" = 1'-0\"" would read as 1:4 by the metric rule.
    if not _IMPERIAL_NOTE_HINT_RE.search(text):
        denominator = parse_scale_text(text)
        return float(denominator) if denominator else None
    match = _IMPERIAL_NOTE_RE.search(text)
    if not match:
        return None
    paper = match.group("paper").replace(" ", "")
    if "/" in paper:
        num, den = paper.split("/")
        if int(den) == 0:
            return None
        paper_in = int(num) / int(den)
    else:
        paper_in = float(paper)
    real = units.parse_length(match.group("real").strip())
    if paper_in <= 0 or real is None or real.system != "imperial" or real.metres <= 0:
        return None
    return round((real.metres / INCH_M) / paper_in, 9)


def _page_unit_m(page: GenericPage) -> Optional[float]:
    """Metres of paper per page unit: PDF points, or raster pixels with a verified pixel size."""
    if page.units == "pt":
        return METRES_PER_POINT
    if page.units == "px" and page.dpi:
        return INCH_M / float(page.dpi)
    return None


def _is_raster(page: GenericPage) -> bool:
    return page.source_kind.startswith("raster") or page.units == "px"


# --------------------------------------------------------------------------
# Scale
# --------------------------------------------------------------------------

def _off_pct(ratio: float, reference: float) -> float:
    return (ratio - reference) / reference * 100.0


def _describe(items, reference: float) -> str:
    return ", ".join(f"'{d.text}' ({_off_pct(r, reference):+.1f}%)" for d, r in items)


def _dim_evidence(page: GenericPage, dim: DimCandidate, confidence: float) -> dict:
    page_no = None if page.source_kind == "dxf" else page.page
    ev = B.evidence(page.file, _evidence_method(dim.source), confidence, page=page_no, entity=dim.text_id,
                    text=dim.text)
    for key in ("model", "pixel_box", "dpi"):        # what the OCR run says about itself
        for own in dim.text_evidence:
            if own.get(key) is not None:
                ev[key] = own[key]
                break
    return ev


def _scale(page, mpu: float, method: str, confidence: float, evidence: dict, provisional: Optional[str] = None):
    out = {"metres_per_unit": mpu, "method": method, "confidence": confidence, "evidence": evidence}
    if provisional:
        out["provisional"] = provisional
    return out


def provisional_scale(page: GenericPage, dims: list[DimCandidate]) -> tuple[Optional[dict], list[str]]:
    """The page scale before the faces exist: (scale dict as ``documents[].pages[].scale``, reasons).

    A provisional scale (from one or two dimensions) carries ``"provisional": "one_dimension" |
    "two_dimensions"`` until ``confirm_scale`` checks it against the room-size labels; every other scale
    is final. None = no scale source (the reasons say why)."""
    sc, reasons = _provisional_scale(page, dims)
    note = _unit_note(dims)
    if note is None or (page.source_kind == "dxf" and page.units_to_m):
        return sc, reasons
    where = f"{page.file} p{page.page}"
    assumed = next((d.unit_assumed for d in dims if d.unit_assumed), None)
    if sc is not None and assumed and sc["method"] == "dimension_text":
        sc = dict(sc, unit_assumed=assumed)
        sc["evidence"] = dict(sc["evidence"], note=f"dimension unit {assumed} assumed")
        return sc, [f"{where}: {note}"] + reasons
    if sc is None and reasons:
        reasons = reasons[:-1] + [f"{reasons[-1]}; {note}"]
    else:
        reasons = [f"{where}: {note}"] + reasons
    return sc, reasons


def _provisional_scale(page: GenericPage, dims: list[DimCandidate]) -> tuple[Optional[dict], list[str]]:
    where = f"{page.file} p{page.page}"
    reasons: list[str] = []
    if page.source_kind == "dxf" and page.units_to_m:
        return (_scale(page, float(page.units_to_m), "dxf_insunits", 1.0,
                       B.evidence(page.file, "vector", 1.0, entity="$INSUNITS")),
                [f"{where}: drawing units known ({page.units_to_m:g} m per unit)"])
    ratios = [(d, d.ratio) for d in dims if d.measured_units > 0 and d.length.metres > 0]
    median = statistics.median(r for _, r in ratios) if ratios else None

    # Scale notes (not on DXF pages: model space is drawn 1:1).
    notes = []
    if page.source_kind != "dxf":
        for run in page.texts:
            if run.source == "ai" or not run.text:
                continue
            ratio = note_ratio(run.text)
            if ratio:
                notes.append((run, ratio))
    if len({round(r, 6) for _, r in notes}) > 1:
        reasons.append(f"{where}: several different scale notes ({', '.join(repr(r.text) for r, _ in notes)}); "
                       f"none used")
        notes = []
    if notes:
        run, ratio = notes[0]
        unit_m = _page_unit_m(page)
        if unit_m is None:
            reasons.append(f"{where}: scale note '{run.text}' ignored: "
                           + ("raster page without a verified pixel size" if _is_raster(page)
                              else f"page units '{page.units}' have no paper size"))
        else:
            from_note = ratio * unit_m
            raster = _is_raster(page)
            ev_method = "ocr" if run.source == "ocr" else "vector"

            def note_scale(confidence: float) -> dict:
                ev = B.evidence(page.file, ev_method, confidence, page=page.page, entity=run.id, text=run.text)
                return _scale(page, from_note, "pdf_scale_text", confidence, ev)

            if median is None:
                return note_scale(0.9), reasons + [f"{where}: scale from the note '{run.text}' (no dimension text)"]
            if abs(_off_pct(median, from_note)) <= SCALE_AGREEMENT * 100.0:
                return note_scale(1.0), reasons + [
                    f"{where}: scale note '{run.text}' confirmed by {len(ratios)} dimension text(s)"]
            if not raster:
                disagreeing = [(d, r) for d, r in ratios if abs(_off_pct(r, from_note)) > SCALE_AGREEMENT * 100.0]
                return note_scale(SCALE_NOTE_DISPUTED_CONFIDENCE), reasons + [
                    f"{where}: '{run.text}' gives {from_note:.6f} m/unit but the median of {len(ratios)} dimension "
                    f"texts gives {median:.6f} m/unit ({_off_pct(median, from_note):+.1f}%); scale note kept; "
                    f"disagreeing texts: {_describe(disagreeing, from_note)}"]
            reasons.append(f"{where}: scale note '{run.text}' ({from_note:.6f} m/px at {page.dpi:g} dpi) disagrees "
                           f"with the dimension texts ({median:.6f} m/px, {_off_pct(median, from_note):+.1f}%); "
                           f"a raster note never counts against the dimensions")

    if not ratios:
        return None, reasons + [f"{where}: no scale note and no dimension text with a dimension line"]
    n = len(ratios)
    agreeing = [(d, r) for d, r in ratios if abs(_off_pct(r, median)) <= SCALE_AGREEMENT * 100.0]
    odd = [(d, r) for d, r in ratios if abs(_off_pct(r, median)) > SCALE_AGREEMENT * 100.0]
    if len(agreeing) >= MIN_AGREEING_DIMENSIONS and len(agreeing) * 2 > n:
        confidence = 0.9 if not odd else 0.7
        reason = f"{where}: scale from {len(agreeing)} of {n} agreeing dimension texts"
        if odd:
            reason += f"; disagreeing: {_describe(odd, median)}"
        return (_scale(page, median, "dimension_text", confidence, _dim_evidence(page, agreeing[0][0], confidence)),
                reasons + [reason])
    if len(agreeing) >= MIN_AGREEING_DIMENSIONS:
        return None, reasons + [f"{where}: no scale note and only {len(agreeing)} of {n} dimension texts agree "
                                f"on a scale (not the majority); disagreeing: {_describe(odd, median)}"]
    # Two dimensions within 0.5 % that are the majority -> provisional.
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            ri, rj = ratios[i][1], ratios[j][1]
            spread = abs(ri - rj) / ((ri + rj) / 2.0)
            if spread <= PAIR_AGREEMENT:
                pairs.append((spread, i, j))
    if pairs and 2 * 2 > n:
        spread, i, j = min(pairs)
        mean = (ratios[i][1] + ratios[j][1]) / 2.0
        first = ratios[i][0]
        reason = (f"{where}: provisional scale from 2 dimension texts ('{ratios[i][0].text}', '{ratios[j][0].text}', "
                  f"{100.0 * spread:.3f}% apart): {mean:.6f} m/unit; needs >= {TWO_DIM_LABELS} room-size labels "
                  f"within {100 * LABEL_AGREEMENT:.0f}%")
        return (_scale(page, mean, "dimension_text", TWO_DIM_CONFIDENCE,
                       _dim_evidence(page, first, TWO_DIM_CONFIDENCE), "two_dimensions"), reasons + [reason])
    if n == 1:
        dim, ratio = ratios[0]
        reason = (f"{where}: provisional scale from 1 dimension text ('{dim.text}'): {ratio:.6f} m/unit; needs >= "
                  f"{ONE_DIM_LABELS} room-size labels within {100 * LABEL_AGREEMENT:.0f}%")
        return (_scale(page, ratio, "dimension_text", ONE_DIM_CONFIDENCE, _dim_evidence(page, dim, ONE_DIM_CONFIDENCE),
                       "one_dimension"), reasons + [reason])
    return None, reasons + [f"{where}: no scale note and the {n} dimension texts do not agree on a scale: "
                            f"{_describe(ratios, median)} against their median {median:.6f} m/unit"]


def _label_checks(label_blocks, faces_m) -> list[tuple[LB.LabelBlock, list[float], list[float]]]:
    """Room-size labels on rectangular faces: (block, measured sides in label order, relative errors)."""
    checks = []
    seen: set[int] = set()
    for face, block in faces_m:
        if block is None or block.size is None or face is None or face.is_empty or id(block) in seen:
            continue                                # a label corroborates once
        seen.add(id(block))
        a, b, rectangularity = LB.clear_size(face)
        if rectangularity < LB.RECTANGULAR_MIN:
            continue
        measured, errs = LB.match_sides((block.size[0].metres, block.size[1].metres), (a, b))
        checks.append((block, measured, errs))
    return checks


def _reread_size_labels(blocks, unit: Optional[str]) -> int:
    """With the dimension unit assumed (``unit_reading``), a size label of two bare integers on the page (``3350 x
    3050``) is written in that unit too: its ``size`` is re-read in place (the room checks use the same blocks).
    Returns how many blocks changed."""
    if not unit:
        return 0
    seen: set[int] = set()
    changed = 0
    for block in blocks:
        if id(block) in seen or block.size is None:
            continue
        seen.add(id(block))
        a, b = block.size
        if all(x.system == "metric" and units.is_bare_integer(x.text) for x in (a, b)):
            block.size = (units.read_as(a, unit), units.read_as(b, unit))      # from the text: idempotent
            changed += 1
    return changed


def confirm_scale(scale: Optional[dict], dims: list[DimCandidate], label_blocks,
                  faces_m) -> tuple[Optional[dict], list[dict], list[str]]:
    """Check the scale against the room-size labels and the dimensions: (scale, conflicts, warnings).

    ``faces_m``: (shapely Polygon in page metres at this scale, LabelBlock or None) per face.
    ``label_blocks`` is the page's full list (used for the report line on labels without a face).
    A provisional scale is confirmed (the ``provisional`` key removed) or rejected: then the result is
    None and the last warning starts with "scale not corroborated:" (the ``needs_review`` reason).
    Conflicts: one ``scale_disagreement`` per dimension off the chosen ratio by more than 1 %."""
    if scale is None:
        return None, [], []
    scale = dict(scale)
    kind = scale.pop("provisional", None)
    mpu = scale["metres_per_unit"]
    warnings: list[str] = []
    unit = next((d.unit_assumed for d in dims if d.unit_assumed), None)
    reread = _reread_size_labels(list(label_blocks or []) + [b for _, b in faces_m if b is not None], unit)
    if unit:
        warnings.append(f"dimension texts written as bare integers read in {unit} (assumed unit: "
                        f"{_unit_note(dims)})")
    if reread:
        warnings.append(f"{reread} room-size labels written as bare integers read in {unit} like the dimension "
                        f"texts (assumed)")
    checks = _label_checks(label_blocks, faces_m)
    agree = [c for c in checks if max(abs(e) for e in c[2]) <= LABEL_AGREEMENT]
    disagree = [c for c in checks if max(abs(e) for e in c[2]) > LABEL_AGREEMENT]

    def describe_labels(items) -> str:
        return "; ".join(f"{b.name} {b.size_text} vs {m[0]:.2f} x {m[1]:.2f} m "
                         f"({100 * e[0]:+.1f}%, {100 * e[1]:+.1f}%)" for b, m, e in items)

    if kind is not None:
        need = TWO_DIM_LABELS if kind == "two_dimensions" else ONE_DIM_LABELS
        used = [d for d in dims if d.measured_units > 0 and abs(_off_pct(d.ratio, mpu)) <= SCALE_AGREEMENT * 100.0]
        if len(agree) < need:
            dims_text = ", ".join(f"'{d.text}' {d.measured_units:.2f} units -> {d.ratio:.6f} m/unit" for d in dims)
            note = _unit_note(dims)
            warnings.append(f"scale not corroborated: {len(agree)} of {len(checks)} room-size labels agree within "
                            f"{100 * LABEL_AGREEMENT:.0f}% (need {need}); candidates: {dims_text or 'none'}"
                            + (f"; labels: {describe_labels(checks)}" if checks else "")
                            + (f"; {note}" if note else ""))
            return None, [], warnings
        scale["confidence"] = TWO_DIM_CONFIDENCE if kind == "two_dimensions" else ONE_DIM_CONFIDENCE
        scale["evidence"] = dict(scale["evidence"], confidence=scale["confidence"])
        if kind == "one_dimension":
            warnings.append(f"scale from one dimension, corroborated by {len(agree)} room sizes")
        else:
            warnings.append(f"scale from {len(used)} dimensions, corroborated by {len(agree)} room sizes")
    if disagree:
        warnings.append(f"{len(disagree)} of {len(checks)} room-size labels differ from the scale by more than "
                        f"{100 * LABEL_AGREEMENT:.0f}%: {describe_labels(disagree)}")
    conflicts = []
    for d in dims:
        if d.measured_units <= 0:
            continue
        off = _off_pct(d.ratio, mpu)
        if abs(off) > SCALE_AGREEMENT * 100.0:
            measured_m = d.measured_units * mpu
            conflicts.append({
                "kind": "scale_disagreement", "element_ids": [],
                "description": f"dimension text '{d.text}' ({d.text_id}) reads {d.length.metres:.3f} m but its line "
                               f"measures {measured_m:.3f} m at the page scale ({off:+.1f}%)",
                "resolution": f"page scale kept ({scale['method']}, {mpu:.6f} m/unit); the dimension text is "
                              f"listed, not used"})
    return scale, conflicts, warnings
