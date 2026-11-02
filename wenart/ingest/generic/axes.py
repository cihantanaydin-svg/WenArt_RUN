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


def axis_line_ids(strokes: list, texts: list) -> set:
    """The ids of the axis lines among ``strokes`` (the module docstring)."""
    out = set()
    bub = bubbles(strokes, texts)
    for st in strokes:
        if is_axis_style(getattr(st, "layer", None), getattr(st, "linetype", None)):
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
