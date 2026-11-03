"""Axis (grid) lines of a drawing: never walls, never an outline (2 Nov 2026).

What: ``axis_line_ids(strokes, texts)``: the ids of the strokes that are axis lines of the structural grid:
- the stroke's layer names a grid (``AXIS_LAYER_RE``: AKS, AXIS, GRID, ACHSE, AXE, EKSEN, RASTER, ASSE, EJE ...),
- or its linetype is a centre / dash-dot line (``AXIS_LINETYPE_RE``: CENTER, DASHDOT, PHANTOM, ACAD_ISO04-06,
  ISO08-15 ...), the way a grid is drawn,
- or it is a long straight line that ends in an axis bubble (a circle around a grid label: a number or one or two
  letters, ``GRID_LABEL_RE``), whatever its layer and linetype: the label at its end says what it is.

Why: real10 (user: "the red lines should have been dotted lines, those are for coordinates, you can understand this
from the numbers at the end"): the grid of the plans, layer ``aks`` with the dash-dot linetype ACAD_ISO04W100, was
read as solid strokes: 24 lines across the whole plan took part in the walls, the rooms and the plan's outline (the
outline fit of the levels then turned two floors by 90 and 180 degrees). The reader did not keep linetypes at all.

How: pure; ``strokes`` are generic ``Stroke``s (``layer``, ``linetype``, ``kind``, ``pts``, ``arc``), ``texts``
objects with ``text`` and ``box`` (``TextRun``, the sheets' ``Txt``).
"""
from __future__ import annotations

import math
import re
from typing import Iterable

from wenart import building as B

AXIS_LAYER_RE = re.compile(r"\b(AKS|AKSLAR|AXIS|AXES|AXE|GRID|GRIDS|GRIDLINE|GRIDLINES|ACHSE|ACHSEN|ACHSRASTER|"
                           r"RASTER|EKSEN|ASSE|ASSI|EJE|EJES|S-GRID|A-GRID)\b")
AXIS_LINETYPE_RE = re.compile(r"CENT(?:ER|RE)|DASH-?DOT|PHANTOM|ISO0?[4568]W|ISO0?9W|ISO1[0-5]W|AXIS|ACHS")
GRID_LABEL_RE = re.compile(r"^(?:[A-Z]{1,2}|\d{1,3})['′]?$")
BUBBLE_TEXT_RATIO = (0.6, 4.0)        # a bubble's radius: this many times its label's height
BUBBLE_REACH = 2.5                     # a line ending within this many radii of a bubble's centre ...
BUBBLE_AIM = 0.5                       # ... and aiming at it (the centre within this many radii of the line)
AXIS_MIN_RADII = 15.0                  # an axis line is at least this many bubble radii long


def _fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).upper().split())


def is_axis_style(layer, linetype) -> bool:
    """True for a grid layer or a centre / dash-dot linetype (the module docstring)."""
    return bool((layer and AXIS_LAYER_RE.search(_fold(layer).replace("_", " ")))
                or (linetype and AXIS_LINETYPE_RE.search(_fold(linetype))))


def bubbles(strokes: Iterable, texts: Iterable) -> list[tuple[float, float, float]]:
    """``[(cx, cy, r)]``: the circles that hold a grid label at their centre, sized for it (``BUBBLE_TEXT_RATIO``)."""
    labels = []
    for t in texts:
        s = _fold(t.text)
        if GRID_LABEL_RE.match(s):
            b = t.box
            labels.append(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0, max(1e-9, b[3] - b[1])))
    if not labels:
        return []
    out = []
    for st in strokes:
        arc = getattr(st, "arc", None)
        if not arc or not getattr(st, "closed", False):
            continue
        cx, cy = arc["center"]
        r = float(arc["radius"])
        for lx, ly, h in labels:
            if math.dist((lx, ly), (cx, cy)) <= 0.6 * r and BUBBLE_TEXT_RATIO[0] * h <= r <= BUBBLE_TEXT_RATIO[1] * h:
                out.append((float(cx), float(cy), r))
                break
    return out


def _long(st, span: float) -> bool:
    pts = list(getattr(st, "pts", []) or [])
    return len(pts) >= 2 and span > 0 and math.dist(pts[0], pts[-1]) >= LINETYPE_SPAN_SHARE * span


def _straight(st):
    pts = list(getattr(st, "pts", []) or [])
    if getattr(st, "arc", None) or len(pts) < 2:
        return None
    a, b = pts[0], pts[-1]
    if len(pts) > 2:
        L = math.dist(a, b)
        if L <= 0:
            return None
        for p in pts[1:-1]:                       # every vertex on the chord
            if abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / L > 1e-6 * max(1.0, L):
                return None
    return a, b


LINETYPE_SPAN_SHARE = 0.3             # a line marked by its linetype alone spans this share of the plan (a grid line)


def axis_line_ids(strokes: list, texts: list) -> set:
    """The ids of the axis lines among ``strokes`` (the module docstring). 2 Nov 2026: a line whose linetype alone
    says centre / dash-dot is an axis line only when it spans ``LINETYPE_SPAN_SHARE`` of the plan (the overhead kitchen
    cabinets and the centre lines of a furniture symbol are drawn dash-dot too, short); a grid layer or a bubble at its
    end marks it at any length."""
    out = set()
    bub = bubbles(strokes, texts)
    xs = [p[0] for st in strokes for p in (getattr(st, "pts", None) or [])]
    ys = [p[1] for st in strokes for p in (getattr(st, "pts", None) or [])]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) if xs else 0.0
    for st in strokes:
        layer, lt = getattr(st, "layer", None), getattr(st, "linetype", None)
        if is_axis_style(layer, None) or (lt and is_axis_style(None, lt) and _long(st, span)):
            if getattr(st, "kind", "line") in ("line", "polyline") and not getattr(st, "closed", False):
                out.add(st.id)
            continue
        if not bub:
            continue
        seg = _straight(st)
        if seg is None:
            continue
        a, b = seg
        L = math.dist(a, b)
        for cx, cy, r in bub:
            if L < AXIS_MIN_RADII * r:
                continue
            near = min(math.dist(a, (cx, cy)), math.dist(b, (cx, cy)))
            if near > BUBBLE_REACH * r:
                continue
            aim = abs((b[0] - a[0]) * (cy - a[1]) - (b[1] - a[1]) * (cx - a[0])) / L
            if aim <= BUBBLE_AIM * r:
                out.add(st.id)
                break
    return out


TICK_MAX_M = 0.10                     # 3 Nov 2026: a tick circle or slash this small (page metres) ...
TICK_ON_M = 0.02                      # ... touching a dimension or axis line (this close) is part of the notation
BUILDING_ROLES = ("window", "door", "glass", "wall", "plaster", "structure", "stair", "furniture", "sanitary",
                  "finish", "site")


def notation_ids(strokes: list, dimension_ids=frozenset()) -> set:
    """3 Nov 2026 (real10, user: "I am talking about the lesson learned related to mixing the lines like the grid
    lines"; UL261 kept the axis lines out of the walls, rooms and outline, but a dimension chain crossing a facade
    recess's mouth and ending in its window to the salon, its DH lines and 7 cm tick circles and slashes on layer 0,
    made both gaps "unclassified content", so the recess (UL277) became a room): the strokes of the drawing's notation,
    never part of the building: the dimensions found (``dimension_ids``), every stroke on a grid layer
    (``is_axis_style``), a dimension layer (``layer_names``: DH, DV, OLCU, DIM ...) or a text layer (a tag's leader
    line: real10's '70/150' leader crossed the recess's window), and the tick marks (a circle or a short stroke at most
    ``TICK_MAX_M`` across, page metres) that touch one of those lines, on a layer that draws no building element
    (``BUILDING_ROLES``). The dimensions stay on the page for the scale; the readers that build
    the walls' gaps leave these out. Pure."""
    from shapely.geometry import LineString, Point
    from shapely.strtree import STRtree

    from wenart.ingest.generic import layer_names as LN

    out = set(dimension_ids)
    lines = []
    for st in strokes:
        layer = getattr(st, "layer", None)
        # (a centre / dash-dot linetype alone marks only the long grid lines, which the page already left out:
        # ``axis_line_ids``; short dash-dot strokes are glass, overhead cabinets, furniture centre lines)
        if st.id in out or is_axis_style(layer, None) or LN.layer_role(layer) in ("dimension", "text"):
            out.add(st.id)
            if len(st.pts) >= 2:
                lines.append(LineString(st.pts))
    if not lines:
        return out
    tree = STRtree(lines)
    for st in strokes:
        # (a short piece of a window, door, glass or wall layer touching a dimension line along the facade is the
        # building's: real10's right salon lost the frame nubs its glazed facade is closed by)
        if st.id in out or not st.pts or LN.layer_role(getattr(st, "layer", None)) in BUILDING_ROLES:
            continue
        xs, ys = [p[0] for p in st.pts], [p[1] for p in st.pts]
        if max(max(xs) - min(xs), max(ys) - min(ys)) > TICK_MAX_M:
            continue
        g = LineString(st.pts) if len(st.pts) >= 2 else Point(st.pts[0])
        if any(lines[i].distance(g) <= TICK_ON_M for i in tree.query(g.buffer(TICK_ON_M))):
            out.add(st.id)
    return out
