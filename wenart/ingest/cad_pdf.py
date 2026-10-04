"""CAD PDF page -> ``GenericPage`` for the generic plan core (docs/milestone7.md §2.2).

What: ``read_page(path, page, file_rel)`` reads one vector PDF page with pdfplumber (pdfminer underneath) into the
adapter-neutral page model (``wenart.ingest.generic.model``):

- every painted path (pdfminer's ``LTLine``, ``LTRect`` and ``LTCurve``) becomes one ``Stroke`` with ``colour`` =
  the stroking colour when the path is stroked, ``fill`` = the non-stroking colour when it is filled and has an
  area, ``width`` = the line width; gray, RGB and CMYK colours are normalised to RGB 0..1 (pattern colours, which
  have no RGB value, become None);
- the geometry comes from the path itself (``original_path``: the operators ``m``, ``l``, ``c`` (also its short
  forms ``v``, ``y``) and ``h`` with the current transformation applied), **never** from pdfminer's ``pts``, which
  hold only the path vertices: a door swing drawn as one cubic Bézier has two vertices and no shape. Béziers are
  flattened until the chord error is at most ``CHORD_PT`` (0.25 pt); ``h`` or a repeated first point closes a path;
- a flattened Bézier curve that fits a circle within ``CIRCLE_FIT_TOL`` (1 %) of its radius gets ``arc`` (the
  centre, radius and the start/end angles of its first and last point);
- zero-length paths (dots, e.g. the seat dots of a chair) are kept as two equal points;
- texts are ``pdf_extract.merge_chars`` runs (consecutive characters on one baseline), with their box, height and
  rotation (real01's upright ``30'`` has rotation 90).

Coordinates are PDF points with **y up** and the origin at the page's lower-left corner: pdfminer's user space,
which is pdfplumber's ``top`` space (y down) flipped once (``y = height - top``), the space ``pdf_extract`` and
``truth/pages.json`` use as well. Stroke ids are ``path:<n>`` with ``n`` counting the painted paths in
content-stream order, the same numbering as ``pdf_extract`` (so the evidence of both extractors names a path the
same way); text ids are the ``char:<n>`` of the run's first character.

Why a separate adapter: real CAD exports (AutoCAD via Ghostscript for real01) draw walls as 45° hatch combs, doors as
Bézier arcs and furniture as loose lines; the synthetic PDF reader (``pdf_extract``) only knows the 0.5 pt wall
rectangles of the synthetic generator. ``pipeline`` sends pages classified ``generic_labels`` and titled pages without
0.5 pt wall rectangles here and then to ``generic.core.extract``.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import pdfplumber
from pdfminer.layout import LTCurve, LTFigure, LTLine, LTRect

from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.ingest.pdf_extract import merge_chars

CHORD_PT = 0.25              # max chord error of a flattened Bézier (points)
CIRCLE_FIT_TOL = 0.01        # a curve is an arc when a circle fits within 1 % of its radius
CIRCLE_FIT_SAMPLES = 16      # points per Bézier for the circle fit
MAX_BEZIER_STEPS = 64


# --------------------------------------------------------------------------
# Colours and paths
# --------------------------------------------------------------------------

def colour_rgb(value) -> Optional[tuple[float, float, float]]:
    """A pdfminer colour (gray number or 1-tuple, RGB 3-tuple, CMYK 4-tuple) -> RGB 0..1; None for none or a
    pattern name (no RGB value)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        g = float(value)
        return (g, g, g)
    try:
        vals = tuple(float(v) for v in value)
    except (TypeError, ValueError):
        return None
    if len(vals) == 1:
        return vals * 3
    if len(vals) == 3:
        return vals
    if len(vals) == 4:
        c, m, y, k = vals
        return ((1.0 - c) * (1.0 - k), (1.0 - m) * (1.0 - k), (1.0 - y) * (1.0 - k))
    return None


def _bezier(p0, p1, p2, p3, n: int = 0) -> list[tuple[float, float]]:
    """Points of one cubic Bézier after ``p0``: ``n`` of them, or enough that the chord error stays below
    ``CHORD_PT``. For ``n`` equal parameter steps the chord error is at most |B''| / (8 n²) and |B''| <= 6 d, where
    d is the larger second difference of the control points, so n = sqrt(0.75 d / CHORD_PT) suffices."""
    if n <= 0:
        d = max(math.hypot(p0[0] - 2 * p1[0] + p2[0], p0[1] - 2 * p1[1] + p2[1]),
                math.hypot(p1[0] - 2 * p2[0] + p3[0], p1[1] - 2 * p2[1] + p3[1]))
        n = max(2, min(MAX_BEZIER_STEPS, int(math.ceil(math.sqrt(0.75 * d / CHORD_PT)))))
    out = []
    for k in range(1, n + 1):
        t = k / n
        a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def fit_circle(pts) -> Optional[tuple[float, float, float, float]]:
    """``(cx, cy, r, max residual)`` of a least-squares (Kåsa) circle through ``pts``, or None."""
    n = len(pts)
    if n < 3:
        return None
    sx = sum(p[0] for p in pts) / n
    sy = sum(p[1] for p in pts) / n
    u = [p[0] - sx for p in pts]
    v = [p[1] - sy for p in pts]
    suu = sum(a * a for a in u)
    svv = sum(b * b for b in v)
    suv = sum(a * b for a, b in zip(u, v))
    det = suu * svv - suv * suv
    if abs(det) < 1e-12:
        return None
    r1 = 0.5 * (sum(a ** 3 for a in u) + sum(a * b * b for a, b in zip(u, v)))
    r2 = 0.5 * (sum(b ** 3 for b in v) + sum(b * a * a for a, b in zip(u, v)))
    uc = (r1 * svv - r2 * suv) / det
    vc = (r2 * suu - r1 * suv) / det
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    cx, cy = uc + sx, vc + sy
    resid = max(abs(math.dist(p, (cx, cy)) - r) for p in pts)
    return cx, cy, r, resid


def arc_of(pts: list[tuple[float, float]], dense: list[tuple[float, float]]) -> Optional[dict]:
    """The ``Stroke.arc`` of a flattened curve that fits a circle within 1 % of its radius, else None."""
    if len(dense) < 5:
        return None
    fit = fit_circle(dense)
    if fit is None:
        return None
    cx, cy, r, resid = fit
    if r <= 0 or resid > CIRCLE_FIT_TOL * r:
        return None
    return {"center": (cx, cy), "radius": r,
            "start_deg": math.degrees(math.atan2(pts[0][1] - cy, pts[0][0] - cx)),
            "end_deg": math.degrees(math.atan2(pts[-1][1] - cy, pts[-1][0] - cx))}


def _path_ops(obj) -> list:
    """The object's path operators in user space (y up); a path without ``original_path`` (old pdfminer) is
    rebuilt from its vertices as straight pieces."""
    path = getattr(obj, "original_path", None)
    if path:
        return [tuple(op) for op in path]
    pts = [(float(x), float(y)) for x, y in obj.pts]
    if not pts:
        return []
    ops = [("m", pts[0])] + [("l", p) for p in pts[1:]]
    if isinstance(obj, LTRect):
        ops.append(("h",))
    return ops


def _normalise_ops(ops) -> list[tuple]:
    """pdfminer writes path operators as ``(op, (x, y), (x, y), ...)``; older versions as ``(op, x, y, ...)``.
    Both -> ``(op, x, y, x, y, ...)`` with floats."""
    out = []
    for op in ops:
        name, rest = op[0], op[1:]
        flat: list[float] = []
        for item in rest:
            if isinstance(item, (tuple, list)):
                flat.extend(float(v) for v in item)
            else:
                flat.append(float(item))
        out.append((name, *flat))
    return out


def _iter_paths(objs):
    """Painted paths in content-stream order, descending into form XObjects (``LTFigure``)."""
    for obj in objs:
        if isinstance(obj, (LTRect, LTLine, LTCurve)):
            yield obj
        elif isinstance(obj, LTFigure):
            yield from _iter_paths(obj)


def _flatten_ops(ops: list[tuple]) -> tuple[list[tuple[float, float]], bool, bool, list[tuple[float, float]]]:
    """``flatten_path`` for operators in the flat ``(op, x, y, ...)`` form."""
    pts: list[tuple[float, float]] = []
    dense: list[tuple[float, float]] = []
    closed = False
    bezier = False
    cur: Optional[tuple[float, float]] = None
    start: Optional[tuple[float, float]] = None
    for op in ops:
        name = op[0]
        xy = [(op[i], op[i + 1]) for i in range(1, len(op) - 1, 2)]
        if name in ("m", "l") and xy:
            cur = xy[-1]
            if name == "m":
                start = cur
            pts.append(cur)
            dense.append(cur)
        elif name in ("c", "v", "y") and xy and cur is not None:
            if name == "c" and len(xy) >= 3:
                c1, c2, end = xy[0], xy[1], xy[2]
            elif name == "v" and len(xy) >= 2:
                c1, c2, end = cur, xy[0], xy[1]
            elif name == "y" and len(xy) >= 2:
                c1, c2, end = xy[0], xy[1], xy[1]
            else:
                continue
            bezier = True
            pts.extend(_bezier(cur, c1, c2, end))
            dense.extend(_bezier(cur, c1, c2, end, CIRCLE_FIT_SAMPLES))
            cur = end
        elif name == "h":
            closed = True
            if start is not None:
                cur = start
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        closed = True
        pts = pts[:-1]
    return pts, closed, bezier, dense


def flatten_path(path) -> tuple[list[tuple[float, float]], bool, bool, list[tuple[float, float]]]:
    """``(points, closed, has Bézier, dense points)`` of one path given as operators: ``(op, (x, y), ...)`` as
    pdfminer's ``original_path`` and pdfplumber's ``curve["path"]`` write them, or ``(op, x, y, ...)``.

    ``dense`` samples every Bézier with ``CIRCLE_FIT_SAMPLES`` points (for the circle fit); straight pieces add
    their end points only. A closed path does not repeat its first point."""
    return _flatten_ops(_normalise_ops(path))


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

def stroke_of(obj, index: int) -> Optional[Stroke]:
    """One painted pdfminer path object -> ``Stroke`` (``path:<index>``); None for an empty path."""
    pts, closed, bezier, dense = flatten_path(_path_ops(obj))
    if not pts:
        return None
    if len(pts) == 1:
        pts = [pts[0], pts[0]]                                  # a dot
    if isinstance(obj, LTLine):
        kind = "line"
    elif bezier:
        kind = "curve"
    else:
        kind = "polyline"
    colour = colour_rgb(obj.stroking_color) if getattr(obj, "stroke", True) else None
    distinct = {(round(x, 6), round(y, 6)) for x, y in pts}
    # A fill paints an area: a two-point path has none, so its fill is not recorded.
    fill = colour_rgb(obj.non_stroking_color) if getattr(obj, "fill", False) and len(distinct) >= 3 else None
    arc = arc_of(pts, dense) if bezier else None
    return Stroke(id=f"path:{index}", kind=kind, pts=pts, closed=closed and len(distinct) >= 3, colour=colour,
                  fill=fill, width=float(getattr(obj, "linewidth", 0.0) or 0.0), arc=arc)


def text_runs(chars: list[dict]) -> list[TextRun]:
    """``merge_chars`` runs as ``TextRun``s (box y up, rotation from the character matrix)."""
    runs = []
    for item in merge_chars(chars):
        runs.append(TextRun(id=item.entity, text=item.text, box=tuple(float(v) for v in item.box),
                            height=float(item.height), rotation_deg=float(item.rotation_deg)))
    return runs


def page_from_pdfplumber(pdf_page, page_no: int, file_rel: str) -> GenericPage:
    """A ``GenericPage`` from an open pdfplumber page (``classify`` reuses the open document)."""
    strokes: list[Stroke] = []
    for index, obj in enumerate(_iter_paths(pdf_page.layout)):
        stroke = stroke_of(obj, index)
        if stroke is not None:
            strokes.append(stroke)
    warnings = []
    if pdf_page.images:
        warnings.append(f"{file_rel} p{page_no}: {len(pdf_page.images)} embedded image(s) not read by the vector "
                        f"adapter")
    return GenericPage(file=file_rel, page=page_no, source_kind="cad_pdf", units="pt", units_to_m=None,
                       size=(float(pdf_page.width), float(pdf_page.height)), strokes=strokes,
                       texts=text_runs(pdf_page.chars), warnings=warnings)


def read_page(path: str | Path, page: int, file_rel: str) -> GenericPage:
    """Page ``page`` (1-based) of the vector PDF at ``path`` as a ``GenericPage`` in points, y up."""
    with pdfplumber.open(str(path)) as pdf:
        return page_from_pdfplumber(pdf.pages[page - 1], page, file_rel)
