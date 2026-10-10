"""The generic DXF adapter: any DXF (or a DWG converted by ``wenart.ingest.dwg``) -> ``GenericPage``
(docs/milestone7.md §5.2).

What: ``read_page(path, file_rel)`` reads the model space of a DXF that does not follow the synthetic layer
convention (``dxf_extract.has_synthetic_layers`` is False) into the adapter-neutral page model of the generic core
(``wenart.ingest.generic.model``); ``collect_texts(doc)`` gives its texts alone for the page classification (§2.1).

Why: real DWG/DXF files use any layer names, draw walls as hatches and lines, furniture as nested blocks, room names
as MTEXT or block attributes, and dimensions in feet and inches. The core decides what the geometry means; this
module only turns entities into strokes, texts and dimensions without losing what they are (layer, block chain,
handle) and without guessing.

How, per model-space entity (paper space and layouts are out of scope):
- Entities on layers that are off or frozen, and invisible entities, are not drawn and not read (counted in a
  warning). Unsupported types (LEADER, IMAGE, 3DSOLID, ...) are counted in a warning.
- INSERT: exploded recursively with ``virtual_entities`` (transforms applied, MINSERT arrays resolved); every
  stroke keeps the block-name chain, outermost first (``DINING-6/CHAIR``). Entities on layer ``0`` inside a block
  take the layer of the INSERT; BYBLOCK colours take its colour. ATTRIBs of every INSERT, nested ones included, are
  read as texts (``virtual_entities`` does not yield them; ATTDEFs are templates and are skipped).
- LINE, LWPOLYLINE/POLYLINE, ARC, CIRCLE, ELLIPSE, SPLINE -> ``Stroke`` with the points flattened to <= 5 mm
  (in drawing units; with unknown units 0.25 % of the entity's size). An open polyline with bulges is split into
  its straight runs (``<id>:<k>``) and one arc stroke per bulge; a closed one stays one shape. ARC/CIRCLE strokes
  carry ``arc``; an ellipse, spline or closed bulge polyline gets ``arc`` when a circle fits all its points within
  1 % of the radius.
- HATCH -> one closed stroke per boundary path, ids ``HATCH:<handle>#<k>`` (``generic.walls`` fills all paths of
  one id even-odd: one shape with its islands, the outer loop and the room islands of a wall hatch). The
  ``hatch_style`` is honoured (normal: every path; outer: external and outermost paths; ignore: external only).
  Solid hatches are filled with their colour; pattern hatches are filled only on wall-hint layers (their pattern
  lines are not reproduced; elsewhere the boundary is an outline, so a black tile pattern is never a "dark fill").
- SOLID/TRACE/3DFACE -> a filled closed stroke. POINT -> a dot (not on ``DEFPOINTS``, which never plots).
- TEXT/ATTRIB -> one ``TextRun``; MTEXT -> one run per paragraph (``\\P``), with the inline height codes honoured
  (``\\H9;``, ``\\H0.7x;``). Text boxes are estimates: 0.8 x cap height per character, 0.25 x cap height below the
  baseline (no font files are read, so the boxes are the same on every machine and in the DWG and DXF runs).
- DIMENSION (linear: rotated and aligned) -> ``DimensionPrim`` **measured from geometry**, never from code 42:
  aligned = distance of the definition points; rotated = their projection on ``dxf.angle``, or, when the file has
  no angle (LibreDWG's ``dxf2dwg`` drops it), on the dimension line drawn in the dimension's ``*D`` block
  (``dimension_angle_from_block``). The measurement itself is
  ``dxf_extract._linear_dimension_span`` (shared with the synthetic path). ``text`` = the text override as drawn
  (``None`` = the measurement is printed). A measurement <= 1e-6 units is dropped with a warning. The dimension
  block's lines, arrows and text are not returned as strokes or texts: the dimension *is* the primitive.
- Colours: ACI resolved (BYLAYER, BYBLOCK), true colour honoured; **ACI 7 and white -> black** (ezdxf reports ACI 7
  as white: the paper colour of a model-space background, black on a plotted sheet).
- Units: ``$INSUNITS`` 1 in, 2 ft, 4 mm, 5 cm, 6 m -> ``units_to_m``; 0 (unitless) or any other code -> None and a
  warning: the core then needs the dimension texts for a scale (§2.3), else the project ends ``needs_review``.

Stroke ids are DXF evidence entities: ``LINE:2F``; exploded block content ``INSERT:4B/3`` (the 4th entity of the
block of INSERT 4B; nested ``INSERT:4B/3/0``); MINSERT copies ``INSERT:4B[2]/3``; polyline pieces ``LWPOLYLINE:2F:1``;
hatch paths ``HATCH:5C#0``. Text ids: ``TEXT:2A``, ``MTEXT:2B`` (``MTEXT:2B:1`` for its second paragraph),
``ATTRIB:3C``. Page coordinates are drawing units, y up, not shifted; ``size`` is the extent of what was read.
"""
from __future__ import annotations

import dataclasses
import math
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import ezdxf
from ezdxf import colors as dxf_colors
from ezdxf import path as dxf_path
from ezdxf import recover
from ezdxf import xclip as dxf_xclip
from ezdxf.math import Vec3, bulge_to_arc
from ezdxf.tools.text import MTextContext, MTextParser, TokenType
from shapely.geometry import LineString, Point, Polygon

from wenart import building as B
from wenart.ingest.dxf_extract import _linear_dimension_span
from wenart.ingest.generic.model import DimensionPrim, GenericPage, Stroke, TextRun

# $INSUNITS codes the adapter accepts (metres per drawing unit); every other code is treated as unitless.
INSUNITS_M = {1: 0.0254, 2: 0.3048, 4: 0.001, 5: 0.01, 6: 1.0}
WALL_HINT_RE = re.compile(r"WALL|DUVAR|A-WALL|MUR|PARED", re.IGNORECASE)
# Reinforced-concrete walls of Turkish drawings (real03, 10 Oct 2026): layer "... - BA" (betonarme) with its hatch
# "... - B-H", or "PERDE" (shear wall); only as the last word of the layer name, since "BA" is short.
CONCRETE_HINT_RE = re.compile(r"(?:^|[\s_\-|$])(?:BA|B-H|BETONARME|PERDE)$", re.IGNORECASE)
FLATTEN_M = 0.005                  # chord error of flattened curves (metres)
FLATTEN_REL = 0.0025               # ... relative to the entity size when the units are unknown
CIRCLE_FIT_TOL = 0.01              # a curve is an arc when a circle fits within 1 % of its radius
MIN_DIMENSION_UNITS = 1e-6
DIM_LINE_TOL = 0.02                # |cos| between a block line and the extension direction (about 1.1 deg)
CHAR_WIDTH = 0.8                   # text box estimate: width per character, x cap height x width factor
DESCENT = 0.25                     # text box estimate: depth below the baseline, x cap height
MTEXT_LINE_SPACING = 5.0 / 3.0     # AutoCAD's MTEXT baseline distance at line spacing factor 1.0
MAX_BLOCK_DEPTH = 16
CLIP_KEEP_SHARE = 0.2               # a closed outline crossing an XCLIP boundary is kept (cut) with >= 20 % inside
ROUND = 6                          # decimals of page coordinates (DWG and DXF runs give the same numbers)
BOX_TOL = 1e-3                     # sheets.json region boxes are rounded to 3 decimals (sheets.model.round_box)
BLACK = (0.0, 0.0, 0.0)
CURVE_TYPES = ("LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE")
FILLED_TYPES = ("SOLID", "TRACE", "3DFACE")
# Hatch boundary path flags (DXF group code 92) and hatch styles (code 75).
PATH_EXTERNAL, PATH_OUTERMOST = 1, 16
HATCH_STYLE_OUTER, HATCH_STYLE_IGNORE = 1, 2


def units_to_m(insunits) -> Optional[float]:
    """``$INSUNITS`` code -> metres per drawing unit for inches, feet, mm, cm and m; None otherwise."""
    try:
        return INSUNITS_M.get(int(insunits))
    except (TypeError, ValueError):
        return None


def is_wall_hint_layer(name: Optional[str]) -> bool:
    """Layer names that say "wall" (``WALL``, ``A-WALL``, ``DUVAR``, ``MUR``, ``PARED``, any case, anywhere), or
    concrete wall (``... - BA``, ``... - B-H``, ``BETONARME``, ``PERDE`` as the last word)."""
    return bool(name) and (WALL_HINT_RE.search(name) is not None or CONCRETE_HINT_RE.search(name) is not None)


def read_page(path: str | Path, file_rel: str, region_box=None, units_to_m_override: Optional[float] = None
              ) -> GenericPage:
    """Read the model space of a DXF into a ``GenericPage`` (one page per file).

    Milestone 10 (docs/milestone10.md §1.6a): ``region_box`` (``[x0, y0, x1, y1]`` in drawing units, a
    ``sheets.json`` region) keeps only what belongs to that region (``clip_page``); ``units_to_m_override`` replaces
    the ``$INSUNITS`` metres per unit (the unit check of the sheets stage, ``unit_mismatch``)."""
    page, _info = read_page_info(path, file_rel)
    if region_box is not None:
        page = clip_page(page, region_box)
    if units_to_m_override is not None:
        page = dataclasses.replace(page, units_to_m=float(units_to_m_override),
                                   warnings=[w for w in page.warnings if "names no drawing unit" not in w])
    return page


# Milestone 10: the sheets stage and the pipeline read a large DXF once (real02: 25 s); the last two pages read are
# kept, keyed by the path, its size and its modification time.
_CACHE: "OrderedDict[tuple, tuple]" = OrderedDict()
CACHE_SIZE = 2


def read_page_info(path: str | Path, file_rel: str) -> tuple[GenericPage, dict]:
    """The whole model space as a ``GenericPage`` and the header facts the sheets stage needs: ``insunits`` (the
    ``$INSUNITS`` code as stored), ``layouts`` (``[{name, entities}]`` of the paper-space layouts with entities)."""
    p = Path(path)
    stat = p.stat()
    key = (str(p.resolve()), stat.st_size, stat.st_mtime_ns, file_rel)
    if key in _CACHE:
        _CACHE.move_to_end(key)
        page, info = _CACHE[key]
        return _copy_page(page), dict(info)
    doc, auditor = recover.readfile(str(path))
    insunits = doc.header.get("$INSUNITS", 0)
    u2m = units_to_m(insunits)
    reader = _Reader(doc, file_rel, u2m)
    reader.run()
    warnings = []
    if auditor.has_errors:
        messages = "; ".join(str(e.message) for e in auditor.errors[:5])
        warnings.append(f"{file_rel}: ezdxf audit reported {len(auditor.errors)} errors ({messages})")
    if u2m is None:
        warnings.append(f"{file_rel}: $INSUNITS={insunits} names no drawing unit (in, ft, mm, cm, m); the scale must "
                        "come from the dimension texts")
    warnings.extend(reader.warnings)
    layers = sorted({st.layer for st in reader.strokes if st.layer and is_wall_hint_layer(st.layer)})
    page = GenericPage(file=file_rel, page=1, source_kind="dxf", units="dxf", units_to_m=u2m,
                       size=reader.extent_size(), strokes=reader.strokes, texts=reader.texts,
                       dimensions=reader.dims, wall_hint_layers=tuple(layers), warnings=warnings)
    layouts = []
    for layout in doc.layouts:
        if layout.name.lower() == "model":
            continue
        count = sum(1 for e in layout if e.dxftype() != "VIEWPORT")
        if count:
            layouts.append({"name": layout.name, "entities": count})
    info = {"insunits": int(insunits) if insunits is not None else None, "layouts": layouts,
            "hidden": _hidden_boxes(reader.hidden_top)}
    _CACHE[key] = (page, info)
    while len(_CACHE) > CACHE_SIZE:
        _CACHE.popitem(last=False)
    return _copy_page(page), dict(info)


def _hidden_boxes(hidden: list) -> list[dict]:
    """``{id, type, layer, box}`` of the model-space entities that were not read (layer off or frozen, invisible):
    the sheets stage lists those far from every drawing as strays."""
    from ezdxf import bbox as dxf_bbox

    out = []
    for eid, entity in hidden:
        try:
            ext = dxf_bbox.extents([entity], fast=True)
        except Exception:  # noqa: BLE001 - an entity without a box is not listed
            continue
        if not ext.has_data:
            continue
        out.append({"id": eid, "type": entity.dxftype(), "layer": entity.dxf.get("layer"),
                    "box": [_r(ext.extmin.x), _r(ext.extmin.y), _r(ext.extmax.x), _r(ext.extmax.y)]})
    return out


def _copy_page(page: GenericPage) -> GenericPage:
    """A shallow copy with its own lists (strokes and texts are shared and never changed by the readers)."""
    return dataclasses.replace(page, strokes=list(page.strokes), texts=list(page.texts),
                               dimensions=list(page.dimensions), warnings=list(page.warnings))


def stroke_entity(stroke_id: str) -> str:
    """The model-space entity a stroke or text id comes from: ``INSERT:4B[2]/3`` -> ``INSERT:4B``,
    ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``, ``MTEXT:2B:1`` -> ``MTEXT:2B``."""
    head = stroke_id.split("/")[0].split("#")[0]
    head = re.sub(r"\[\d+\]$", "", head)
    return ":".join(head.split(":")[:2])


def clip_page(page: GenericPage, box) -> GenericPage:
    """The part of a page that belongs to one drawing region (docs/milestone10.md §1.6a): an entity belongs to the
    region whose box holds the centre of its bounding box (all strokes of an INSERT or a polyline go together), a
    text by the centre of its box (the adapters' text boxes are estimated from the character count, so this is the
    text's own place, never an MTEXT column width), a dimension by the centre of its measured span."""
    x0, y0, x1, y1 = (float(v) for v in box)

    def inside(p) -> bool:
        # A plan's outer face lines lie on its region box: the 3-decimal rounding of the box must not cut them off.
        return x0 - BOX_TOL <= p[0] <= x1 + BOX_TOL and y0 - BOX_TOL <= p[1] <= y1 + BOX_TOL

    boxes: dict[str, list[float]] = {}
    for st in page.strokes:
        key = stroke_entity(st.id)
        b = st.bbox()
        cur = boxes.get(key)
        boxes[key] = list(b) if cur is None else [min(cur[0], b[0]), min(cur[1], b[1]), max(cur[2], b[2]),
                                                   max(cur[3], b[3])]
    keep = {k for k, b in boxes.items() if inside(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0))}
    strokes = [st for st in page.strokes if stroke_entity(st.id) in keep]
    tboxes: dict[str, list[float]] = {}
    for t in page.texts:
        key = stroke_entity(t.id) if t.id.startswith("MTEXT:") else t.id
        cur = tboxes.get(key)
        b = t.box
        tboxes[key] = list(b) if cur is None else [min(cur[0], b[0]), min(cur[1], b[1]), max(cur[2], b[2]),
                                                    max(cur[3], b[3])]
    tkeep = {k for k, b in tboxes.items() if inside(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0))}
    texts = [t for t in page.texts if (stroke_entity(t.id) if t.id.startswith("MTEXT:") else t.id) in tkeep]
    dims = [d for d in page.dimensions if inside(((d.p1[0] + d.p2[0]) / 2.0, (d.p1[1] + d.p2[1]) / 2.0))]
    pts = [p for st in strokes for p in st.pts] + [(t.box[0], t.box[1]) for t in texts] + \
        [(t.box[2], t.box[3]) for t in texts] + [p for d in dims for p in (d.p1, d.p2)]
    size = (0.0, 0.0)
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        size = (_r(max(xs) - min(xs)), _r(max(ys) - min(ys)))
    layers = sorted({st.layer for st in strokes if st.layer and is_wall_hint_layer(st.layer)})
    return dataclasses.replace(page, size=size, strokes=strokes, texts=texts, dimensions=dims,
                               wall_hint_layers=tuple(layers), warnings=list(page.warnings))


def collect_texts(doc, file_rel: Optional[str] = None) -> list[TextRun]:
    """Every text of the model space: TEXT, MTEXT paragraphs, texts inside inserted blocks and the ATTRIBs of
    every INSERT (nested included), in page units. Evidence is filled when ``file_rel`` is given."""
    reader = _Reader(doc, file_rel, units_to_m(doc.header.get("$INSUNITS", 0)), texts_only=True)
    reader.run()
    return reader.texts


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _r(v: float) -> float:
    return round(float(v), ROUND) + 0.0


def _xy(p) -> tuple[float, float]:
    return (_r(p[0]), _r(p[1]))


def _rgb01(rgb) -> tuple[float, float, float]:
    r, g, b = (int(c) for c in rgb)
    if (r, g, b) == (255, 255, 255):
        return BLACK                       # white draws black on the sheet (ACI 7 and true-colour white)
    return (round(r / 255.0, 6), round(g / 255.0, 6), round(b / 255.0, 6))


def _aci_rgb(aci: int) -> tuple[float, float, float]:
    if aci == 7:
        return BLACK
    return _rgb01(dxf_colors.aci2rgb(aci))


def _fit_circle(pts) -> Optional[tuple[tuple[float, float], float]]:
    """Least-squares circle (Kasa) through >= 3 points, None when degenerate."""
    if len(pts) < 3:
        return None
    n = float(len(pts))
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    suu = suv = svv = suuu = svvv = suvv = svuu = 0.0
    for x, y in pts:
        u, v = x - mx, y - my
        suu += u * u
        suv += u * v
        svv += v * v
        suuu += u * u * u
        svvv += v * v * v
        suvv += u * v * v
        svuu += v * u * u
    det = suu * svv - suv * suv
    if abs(det) <= 1e-12 * max(suu * svv, 1e-300):    # (nearly) collinear points: no circle
        return None
    a = 0.5 * (suuu + suvv)
    b = 0.5 * (svvv + svuu)
    uc = (a * svv - b * suv) / det
    vc = (b * suu - a * suv) / det
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    return (mx + uc, my + vc), r


def _arc_dict(center, radius: float, pts, full: bool = False) -> dict:
    """``Stroke.arc`` of an arc through ``pts`` (in drawing order): start and end angles counter-clockwise."""
    cx, cy = center
    if full:
        start, end = 0.0, 360.0
    else:
        a0 = math.degrees(math.atan2(pts[0][1] - cy, pts[0][0] - cx)) % 360.0
        a1 = math.degrees(math.atan2(pts[-1][1] - cy, pts[-1][0] - cx)) % 360.0
        # Drawing direction from the signed area of the points with the centre.
        area = 0.0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            area += (x0 - cx) * (y1 - cy) - (x1 - cx) * (y0 - cy)
        start, end = (a0, a1) if area >= 0 else (a1, a0)
    return {"center": _xy(center), "radius": _r(radius), "start_deg": _r(start), "end_deg": _r(end)}


def _fitted_arc(pts, closed: bool) -> Optional[dict]:
    fit = _fit_circle(pts)
    if fit is None:
        return None
    (cx, cy), r = fit
    if r <= 0 or max(abs(math.hypot(x - cx, y - cy) - r) for x, y in pts) > CIRCLE_FIT_TOL * r:
        return None
    return _arc_dict((cx, cy), r, pts, full=closed)


def _closed_pts(pts, closed: bool) -> tuple[list, bool]:
    """Drop the repeated closing point of a closed outline (``Stroke.closed`` says it)."""
    if len(pts) > 2 and pts[0] == pts[-1]:
        return pts[:-1], True
    return pts, closed


# --------------------------------------------------------------------------
# The model-space walker
# --------------------------------------------------------------------------

def _xclip_polygon(insert) -> Optional[Polygon]:
    """The enabled XCLIP boundary of an INSERT in page units (AutoCAD shows only what lies inside it), or None.
    Found on real03 (10 Oct 2026): a block of three flats is clipped to the one flat that stands there; without the
    boundary the hidden flats overlapped the neighbouring flat. Inverted clips are not supported (warning-free None:
    everything is read, as before)."""
    try:
        xc = dxf_xclip.XClip(insert)
        if not (xc.has_clipping_path and xc.is_clipping_enabled) or getattr(xc, "is_inverted_clip", False):
            return None
        pts = [(float(v.x), float(v.y)) for v in xc.get_wcs_clipping_path().vertices]
    except Exception:                                   # a damaged filter dictionary: read the block unclipped
        return None
    if len(pts) == 2:
        (x0, y0), (x1, y1) = pts
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly if poly.geom_type == "Polygon" and poly.area > 0 else None


def _clip_stroke(st: Stroke, clip: Polygon) -> list[Stroke]:
    """``st`` cut to an XCLIP boundary: unchanged inside, dropped outside; a crossing open stroke keeps its pieces
    inside (``<id>:c<k>`` from the second piece on), a crossing closed one the part of its area inside when that is
    at least ``CLIP_KEEP_SHARE`` of it (else it is dropped)."""
    geom = Point(st.pts[0]) if len(st.pts) == 1 or len(set(st.pts)) == 1 else \
        (Polygon(st.pts) if st.closed and len(st.pts) >= 3 else LineString(st.pts))
    if geom.geom_type == "Polygon" and not geom.is_valid:
        geom = LineString(list(st.pts) + [st.pts[0]])
    if clip.covers(geom):
        return [st]
    if not clip.intersects(geom):
        return []
    cut = geom.intersection(clip)
    if geom.geom_type == "Polygon" and cut.area < CLIP_KEEP_SHARE * geom.area:
        # A closed outline mostly outside belongs to the hidden part (real03: a room of the clipped-away flat next
        # door reached 0.24 m into the window; its sliver, filled even-odd, cut a hole in the shared wall).
        return []
    parts = list(getattr(cut, "geoms", [cut]))
    out = []
    for part in parts:
        if part.is_empty:
            continue
        if part.geom_type == "Polygon":
            pts, closed = [(float(x), float(y)) for x, y in part.exterior.coords[:-1]], True
        elif part.geom_type == "LineString":
            pts, closed = [(float(x), float(y)) for x, y in part.coords], False
        else:
            continue
        if len(pts) < 2:
            continue
        sid = st.id if not out else f"{st.id}:c{len(out)}"
        out.append(dataclasses.replace(st, id=sid, pts=pts, closed=closed, arc=None))
    return out


@dataclass
class _Ref:
    """The block reference an entity was exploded from."""
    chain: str                             # block names, outermost first
    layer: str                             # effective layer of the INSERT
    rgb: tuple                             # resolved colour of the INSERT (for BYBLOCK)
    depth: int
    clip: Optional[Polygon] = None         # XCLIP boundary of this INSERT and its parents, page units (None = none)


class _Reader:
    def __init__(self, doc, file_rel: Optional[str], u2m: Optional[float], texts_only: bool = False) -> None:
        self.doc = doc
        self.file_rel = file_rel
        self.u2m = u2m
        self.texts_only = texts_only
        self.flat_tol = FLATTEN_M / u2m if u2m else None
        self.strokes: list[Stroke] = []
        self.texts: list[TextRun] = []
        self.dims: list[DimensionPrim] = []
        self.warnings: list[str] = []
        self.skipped: Counter = Counter()
        self.hidden = 0
        self.hidden_top: list = []         # top-level entities not read (layer off or frozen, invisible): sheets strays
        self.textsize = float(doc.header.get("$TEXTSIZE", 0.0) or 0.0)
        self._layer_cache: dict[str, tuple] = {}
        self._clip: Optional[Polygon] = None   # the XCLIP boundary of the block being exploded
        self.clipped = 0                       # strokes and texts outside an XCLIP boundary (dropped or cut)

    # ---- driver ----------------------------------------------------------

    def run(self) -> None:
        for n, entity in enumerate(self.doc.modelspace()):
            handle = entity.dxf.get("handle") or f"n{n}"
            self._entity(entity, f"{entity.dxftype()}:{handle}", None)
        where = self.file_rel or "DXF"
        if self.hidden:
            self.warnings.append(f"{where}: {self.hidden} entities on layers that are off or frozen (or invisible) "
                                 "were not read")
        if self.skipped:
            listed = ", ".join(f"{k} x{v}" for k, v in sorted(self.skipped.items()))
            self.warnings.append(f"{where}: entity types not read: {listed}")
        if self.clipped:
            self.warnings.append(f"{where}: {self.clipped} strokes and texts outside the XCLIP boundaries of their "
                                 "blocks were left out or cut (as AutoCAD shows them)")

    def extent_size(self) -> tuple[float, float]:
        pts = [p for st in self.strokes for p in st.pts]
        pts += [(t.box[0], t.box[1]) for t in self.texts] + [(t.box[2], t.box[3]) for t in self.texts]
        pts += [p for d in self.dims for p in (d.p1, d.p2)]
        if not pts:
            return (0.0, 0.0)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (_r(max(xs) - min(xs)), _r(max(ys) - min(ys)))

    # ---- layers and colours ----------------------------------------------

    def _layer_info(self, name: str) -> tuple:
        """(visible, rgb) of a layer; unknown layers are visible and black."""
        key = name.upper()
        if key not in self._layer_cache:
            try:
                layer = self.doc.layers.get(name)
            except ezdxf.DXFTableEntryError:
                layer = None
            if layer is None:
                self._layer_cache[key] = (True, BLACK)
            else:
                visible = not (layer.is_off() or layer.is_frozen())
                rgb = layer.rgb if layer.dxf.hasattr("true_color") else None
                colour = _rgb01(rgb) if rgb is not None else _aci_rgb(abs(int(layer.dxf.get("color", 7))) or 7)
                self._layer_cache[key] = (visible, colour)
        return self._layer_cache[key]

    def _effective_layer(self, entity, ref: Optional[_Ref]) -> str:
        layer = entity.dxf.get("layer") or "0"
        if ref is not None and layer == "0":
            return ref.layer
        return layer

    def _colour(self, entity, layer: str, ref: Optional[_Ref]) -> tuple:
        if entity.dxf.hasattr("true_color"):
            return _rgb01(entity.rgb)
        aci = int(entity.dxf.get("color", 256))
        if aci == 0:                                   # BYBLOCK: the INSERT's colour (black at the top level)
            return ref.rgb if ref is not None else BLACK
        if aci == 256:                                 # BYLAYER
            return self._layer_info(layer)[1]
        return _aci_rgb(abs(aci))

    # ---- dispatch ----------------------------------------------------------

    def _entity(self, entity, eid: str, ref: Optional[_Ref]) -> None:
        kind = entity.dxftype()
        layer = self._effective_layer(entity, ref)
        if entity.dxf.get("invisible", 0) or not self._layer_info(layer)[0]:
            self.hidden += 1
            if ref is None:
                self.hidden_top.append((eid, entity))
            return
        chain = ref.chain if ref else None
        if kind == "INSERT":
            self._insert(entity, eid, ref, layer)
        elif kind in ("TEXT", "ATTRIB"):
            self._text(entity, eid, layer, chain)
        elif kind == "MTEXT":
            self._mtext(entity, eid, layer, chain)
        elif self.texts_only:
            return
        elif kind in CURVE_TYPES:
            self._curve(entity, eid, layer, ref)
        elif kind == "HATCH":
            self._hatch(entity, eid, layer, ref)
        elif kind in FILLED_TYPES:
            self._filled(entity, eid, layer, ref)
        elif kind == "POINT":
            if layer.upper() != "DEFPOINTS":
                p = _xy(entity.dxf.location)
                self._add(Stroke(id=eid, kind="line", pts=[p, p], colour=self._colour(entity, layer, ref),
                                 layer=layer, block=chain))
        elif kind == "DIMENSION":
            if ref is None:
                self._dimension(entity, eid)
            else:
                self.skipped["DIMENSION in a block"] += 1
        else:
            self.skipped[kind] += 1

    def _add(self, stroke: Stroke) -> None:
        if not stroke.pts:
            return
        if self._clip is None:
            self.strokes.append(stroke)
            return
        pieces = _clip_stroke(stroke, self._clip)
        if pieces != [stroke]:
            self.clipped += 1
        self.strokes.extend(pieces)

    # ---- blocks ------------------------------------------------------------

    def _insert(self, insert, eid: str, ref: Optional[_Ref], layer: str) -> None:
        depth = (ref.depth + 1) if ref else 1
        if depth > MAX_BLOCK_DEPTH:
            self.warnings.append(f"{self.file_rel or 'DXF'}: {eid} is nested deeper than {MAX_BLOCK_DEPTH} blocks; "
                                 "not read")
            return
        name = insert.dxf.name
        clip = _xclip_polygon(insert)
        parent = ref.clip if ref else None
        if clip is not None and parent is not None:
            clip = clip.intersection(parent)
            if clip.geom_type != "Polygon":
                clip = max(getattr(clip, "geoms", []), key=lambda g: g.area, default=Polygon())
        elif clip is None:
            clip = parent
        sub = _Ref(chain=name if ref is None else f"{ref.chain}/{name}", layer=layer,
                   rgb=self._colour(insert, layer, ref), depth=depth, clip=clip)
        copies = [insert] if insert.mcount <= 1 else list(insert.multi_insert())
        outer = self._clip
        self._clip = clip
        try:
            for m, one in enumerate(copies):
                base = eid if len(copies) == 1 else f"{eid}[{m}]"
                for k, child in enumerate(one.virtual_entities(skipped_entity_callback=self._skipped_child)):
                    self._entity(child, f"{base}/{k}", sub)
                for j, attrib in enumerate(one.attribs):
                    handle = attrib.dxf.get("handle")
                    aid = f"ATTRIB:{handle}" if handle and len(copies) == 1 else f"{base}/attrib{j}"
                    self._entity(attrib, aid, sub)
        finally:
            self._clip = outer

    def _skipped_child(self, entity, reason: str) -> None:
        self.skipped[f"{entity.dxftype()} in a block ({reason})"] += 1

    # ---- strokes -----------------------------------------------------------

    def _tol(self, size: float) -> float:
        if self.flat_tol:
            return self.flat_tol
        return max(abs(size) * FLATTEN_REL, 1e-9)

    def _flatten(self, path, size: float) -> list[tuple[float, float]]:
        pts = [_xy(v) for v in path.flattening(self._tol(size))]
        out = []
        for p in pts:
            if not out or p != out[-1]:
                out.append(p)
        return out

    def _curve(self, entity, eid: str, layer: str, ref: Optional[_Ref]) -> None:
        kind = entity.dxftype()
        colour = self._colour(entity, layer, ref)
        chain = ref.chain if ref else None
        width = 0.0
        if kind == "LINE":
            p0, p1 = _xy(entity.dxf.start), _xy(entity.dxf.end)
            self._add(Stroke(id=eid, kind="line", pts=[p0, p1], colour=colour, layer=layer, block=chain))
            return
        if kind == "LWPOLYLINE":
            width = float(entity.dxf.get("const_width", 0.0) or 0.0)
            verts = [(float(x), float(y), float(b)) for x, y, b in entity.get_points("xyb")]
            self._polyline(entity, eid, verts, bool(entity.closed), entity.ocs(),
                           float(entity.dxf.get("elevation", 0.0)), colour, layer, chain, width)
            return
        if kind == "POLYLINE":
            if entity.is_2d_polyline:
                verts = [(float(v.dxf.location.x), float(v.dxf.location.y), float(v.dxf.get("bulge", 0.0)))
                         for v in entity.vertices]
                elevation = float(entity.dxf.get("elevation", Vec3()).z)
                self._polyline(entity, eid, verts, bool(entity.is_closed), entity.ocs(), elevation, colour, layer,
                               chain, float(entity.dxf.get("default_start_width", 0.0) or 0.0))
            elif entity.is_3d_polyline:
                pts = [_xy(v.dxf.location) for v in entity.vertices]
                pts, closed = _closed_pts(pts, bool(entity.is_closed))
                self._add(Stroke(id=eid, kind="polyline", pts=pts, closed=closed, colour=colour, layer=layer,
                                 block=chain))
            else:
                self.skipped["POLYLINE (mesh/polyface)"] += 1
            return
        if kind in ("ARC", "CIRCLE"):
            radius = float(entity.dxf.radius)
            pts = self._flatten(dxf_path.make_path(entity), radius)
            center = entity.ocs().to_wcs(entity.dxf.center)
            full = kind == "CIRCLE"
            if full:
                pts, _ = _closed_pts(pts, True)
            self._add(Stroke(id=eid, kind="circle" if full else "arc", pts=pts, closed=full, colour=colour,
                             layer=layer, block=chain, arc=_arc_dict((center.x, center.y), radius, pts, full=full)))
            return
        # ELLIPSE, SPLINE: flattened curves; an arc when a circle fits.
        path = dxf_path.make_path(entity)
        box = path.bbox() if hasattr(path, "bbox") else None
        size = max(box.size.x, box.size.y) if box is not None and box.has_data else 1.0
        pts = self._flatten(path, size)
        closed = bool(getattr(entity, "closed", False)) or (len(pts) > 2 and pts[0] == pts[-1])
        if kind == "ELLIPSE":
            span = (float(entity.dxf.end_param) - float(entity.dxf.start_param)) % (2 * math.pi)
            closed = closed or span < 1e-9
        pts, closed = _closed_pts(pts, closed)
        self._add(Stroke(id=eid, kind="curve", pts=pts, closed=closed, colour=colour, layer=layer, block=chain,
                         arc=_fitted_arc(pts, closed)))

    def _polyline(self, entity, eid: str, verts: list, closed: bool, ocs, elevation: float, colour, layer: str,
                  chain: Optional[str], width: float) -> None:
        """A polyline from OCS vertices ``(x, y, bulge)``: one stroke, or straight runs + one arc per bulge."""
        def wcs(x, y):
            return _xy(ocs.to_wcs(Vec3(x, y, elevation)))

        if not verts:
            return
        has_bulge = any(abs(b) > 1e-12 for _, _, b in (verts if closed else verts[:-1]))
        if not has_bulge:
            pts, closed = _closed_pts([wcs(x, y) for x, y, _ in verts], closed)
            self._add(Stroke(id=eid, kind="polyline", pts=pts, closed=closed, colour=colour, width=width,
                             layer=layer, block=chain))
            return
        if closed:
            path = dxf_path.make_path(entity)
            box = path.bbox()
            pts, _ = _closed_pts(self._flatten(path, max(box.size.x, box.size.y)), True)
            self._add(Stroke(id=eid, kind="polyline", pts=pts, closed=True, colour=colour, width=width, layer=layer,
                             block=chain, arc=_fitted_arc(pts, True)))
            return
        pieces: list[Stroke] = []
        run: list[tuple[float, float]] = []

        def flush_run():
            if len(run) >= 2:
                pieces.append(Stroke(id="", kind="polyline" if len(run) > 2 else "line", pts=list(run),
                                     colour=colour, width=width, layer=layer, block=chain))

        for i in range(len(verts) - 1):
            x0, y0, b = verts[i]
            x1, y1, _ = verts[i + 1]
            if abs(b) <= 1e-12:
                if not run:
                    run.append(wcs(x0, y0))
                run.append(wcs(x1, y1))
                continue
            flush_run()
            run = []
            center, a0, a1, radius = bulge_to_arc((x0, y0), (x1, y1), b)
            steps = max(2, int(math.ceil(abs(4.0 * math.atan(b)) /
                                         (2.0 * math.acos(max(-1.0, 1.0 - self._tol(radius) / radius))))))
            # bulge_to_arc returns the counter-clockwise arc (a0 -> a1); a negative bulge runs it backwards.
            span = (a1 - a0) % (2.0 * math.pi)
            ang = [a0 + span * k / steps for k in range(steps + 1)]
            if b < 0:
                ang.reverse()
            pts = [wcs(center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)) for a in ang]
            pts[0], pts[-1] = wcs(x0, y0), wcs(x1, y1)
            c = ocs.to_wcs(Vec3(center[0], center[1], elevation))
            pieces.append(Stroke(id="", kind="arc", pts=pts, colour=colour, width=width, layer=layer, block=chain,
                                 arc=_arc_dict((c.x, c.y), radius, pts)))
        flush_run()
        for k, piece in enumerate(pieces):
            piece.id = f"{eid}:{k}"
            self._add(piece)

    def _hatch(self, hatch, eid: str, layer: str, ref: Optional[_Ref]) -> None:
        colour = self._colour(hatch, layer, ref)
        solid = bool(hatch.dxf.get("solid_fill", 0))
        fill = colour if (solid or is_wall_hint_layer(layer)) else None
        style = int(hatch.dxf.get("hatch_style", 0))
        paths = list(hatch.paths)
        flags = [int(getattr(bp, "path_type_flags", 0)) for bp in paths]
        has_external = any(f & PATH_EXTERNAL for f in flags)
        ocs = hatch.ocs()
        elevation = float(hatch.dxf.get("elevation", Vec3()).z)
        for k, (bp, f) in enumerate(zip(paths, flags)):
            if has_external and style == HATCH_STYLE_IGNORE and not f & PATH_EXTERNAL:
                continue
            if has_external and style == HATCH_STYLE_OUTER and not f & (PATH_EXTERNAL | PATH_OUTERMOST):
                continue
            path = dxf_path.from_hatch_boundary_path(bp, ocs, elevation)
            box = path.bbox()
            if not box.has_data:
                continue
            pts, _ = _closed_pts(self._flatten(path, max(box.size.x, box.size.y)), True)
            if len(pts) < 3:
                continue
            self._add(Stroke(id=f"{eid}#{k}", kind="polyline", pts=pts, closed=True, colour=colour, fill=fill,
                             layer=layer, block=ref.chain if ref else None))

    def _filled(self, entity, eid: str, layer: str, ref: Optional[_Ref]) -> None:
        verts = entity.wcs_vertices()
        pts = []
        for v in verts:
            p = _xy(v)
            if not pts or p != pts[-1]:
                pts.append(p)
        pts, _ = _closed_pts(pts, True)
        colour = self._colour(entity, layer, ref)
        self._add(Stroke(id=eid, kind="polyline", pts=pts, closed=True, colour=colour,
                         fill=colour if entity.dxftype() != "3DFACE" else None, layer=layer,
                         block=ref.chain if ref else None))

    # ---- texts -------------------------------------------------------------

    def _run(self, eid: str, text: str, corners, height: float, rotation: float, layer: str,
             chain: Optional[str], tag: Optional[str] = None) -> None:
        xs = [c[0] for c in corners]
        ys = [c[1] for c in corners]
        box = (_r(min(xs)), _r(min(ys)), _r(max(xs)), _r(max(ys)))
        if self._clip is not None and not self._clip.contains(Point((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)):
            self.clipped += 1                    # a text whose centre lies outside the XCLIP boundary is not shown
            return
        evidence = []
        if self.file_rel is not None:
            evidence.append(B.evidence(self.file_rel, "vector", 1.0, layer=layer, entity=eid, block=chain, text=text))
            if tag:
                # Milestone 12 (docs/milestone12.md §3.1, contract §13.3): the attribute tag (KOT, BDK, TZK ...) for
                # the level-mark reader.
                evidence[-1]["attrib_tag"] = tag
        self.texts.append(TextRun(id=eid, text=text, box=box, height=_r(height), rotation_deg=_r(rotation % 360.0),
                                  source="vector", evidence=evidence))

    def _height(self, height: float, eid: str) -> float:
        if height > 0:
            return height
        if self.textsize > 0:
            self.warnings.append(f"{self.file_rel or 'DXF'}: {eid} has no text height; $TEXTSIZE "
                                 f"{self.textsize:g} used for its box")
            return self.textsize
        self.warnings.append(f"{self.file_rel or 'DXF'}: {eid} has no text height; its box is a point")
        return 0.0

    def _text(self, entity, eid: str, layer: str, chain: Optional[str]) -> None:
        text = entity.plain_text().strip()
        if not text:
            return
        if entity.dxftype() == "ATTRIB" and entity.is_invisible:
            return
        h = self._height(float(entity.dxf.get("height", 0.0) or 0.0), eid)
        wf = float(entity.dxf.get("width", 1.0) or 1.0)
        rotation = float(entity.dxf.get("rotation", 0.0))
        width = len(text) * CHAR_WIDTH * h * wf
        ocs = entity.ocs()
        halign = int(entity.dxf.get("halign", 0))
        valign = int(entity.dxf.get("valign", 0))
        insert = Vec3(entity.dxf.insert)
        align = Vec3(entity.dxf.get("align_point", insert))
        # Baseline relative to the anchor: valign baseline / bottom (descender) / middle / top; halign MIDDLE
        # centres both ways. ALIGNED and FIT run from the insert point to the align point.
        if halign in (3, 5):
            anchor, dx, baseline = insert, 0.0, 0.0
            if (align - insert).magnitude > 1e-12:
                width = (align - insert).magnitude
                rotation = math.degrees(math.atan2(align.y - insert.y, align.x - insert.x))
        elif halign == 0 and valign == 0:
            anchor, dx, baseline = insert, 0.0, 0.0
        else:
            anchor = align
            dx = {1: -width / 2.0, 2: -width, 4: -width / 2.0}.get(halign, 0.0)
            baseline = -h / 2.0 if halign == 4 else {1: DESCENT * h, 2: -h / 2.0, 3: -h}.get(valign, 0.0)
        y0, y1 = baseline - DESCENT * h, baseline + h
        local = [(dx, y0), (dx + width, y0), (dx + width, y1), (dx, y1)]
        corners = self._place(local, anchor, rotation, ocs)
        self._run(eid, text, corners, h, rotation, layer, chain,
                  tag=str(entity.dxf.tag) if entity.dxftype() == "ATTRIB" and entity.dxf.get("tag") else None)

    @staticmethod
    def _place(local, anchor: Vec3, rotation_deg: float, ocs=None) -> list[tuple[float, float]]:
        a = math.radians(rotation_deg)
        ca, sa = math.cos(a), math.sin(a)
        out = []
        for x, y in local:
            p = Vec3(anchor.x + x * ca - y * sa, anchor.y + x * sa + y * ca, anchor.z)
            if ocs is not None:
                p = ocs.to_wcs(p)
            out.append((p.x, p.y))
        return out

    def _mtext_lines(self, mtext, base_h: float) -> list[tuple[str, float]]:
        """Paragraphs of an MTEXT as ``(text, cap height)``; inline ``\\H`` codes honoured."""
        ctx = MTextContext()
        ctx.cap_height = base_h
        lines: list[list] = [["", 0.0]]
        for token in MTextParser(mtext.text, ctx):
            t = token.type
            if t in (TokenType.NEW_PARAGRAPH, TokenType.NEW_COLUMN, TokenType.WRAP_AT_DIMLINE):
                lines.append(["", 0.0])
            elif t == TokenType.WORD:
                lines[-1][0] += token.data
                lines[-1][1] = max(lines[-1][1], float(token.ctx.cap_height))
            elif t == TokenType.STACK:
                upr, lwr, _ = token.data
                lines[-1][0] += f"{upr}/{lwr}"
                lines[-1][1] = max(lines[-1][1], float(token.ctx.cap_height))
            elif t in (TokenType.SPACE, TokenType.NBSP, TokenType.TABULATOR):
                lines[-1][0] += " "
        return [(" ".join(text.split()), h) for text, h in lines]

    def _mtext(self, mtext, eid: str, layer: str, chain: Optional[str]) -> None:
        base_h = float(mtext.dxf.get("char_height", 0.0) or 0.0)
        lines = self._mtext_lines(mtext, base_h)
        if not any(text for text, _ in lines):
            return
        fallback = None
        heights = []
        for text, h in lines:
            if h <= 0:
                if fallback is None:
                    fallback = self._height(0.0, eid)
                h = fallback
            heights.append(h)
        factor = float(mtext.dxf.get("line_spacing_factor", 1.0) or 1.0)
        advances = [MTEXT_LINE_SPACING * h * factor for h in heights]
        total = sum(advances[:-1]) + heights[-1]
        attach = int(mtext.dxf.get("attachment_point", 1))
        row, col = (attach - 1) // 3, (attach - 1) % 3
        top = {0: 0.0, 1: total / 2.0, 2: total}[row]
        rotation = float(mtext.get_rotation())
        anchor = Vec3(mtext.dxf.insert)
        texts = [(k, text, h) for k, (text, _), h in zip(range(len(lines)), lines, heights)]
        several = sum(1 for _, text, _ in texts if text) > 1
        offset = 0.0
        for k, text, h in texts:
            baseline = top - offset - h
            offset += advances[k]
            if not text:
                continue
            width = len(text) * CHAR_WIDTH * h
            x0 = {0: 0.0, 1: -width / 2.0, 2: -width}[col]
            local = [(x0, baseline - DESCENT * h), (x0 + width, baseline - DESCENT * h), (x0 + width, baseline + h),
                     (x0, baseline + h)]
            corners = self._place(local, anchor, rotation)
            self._run(f"{eid}:{k}" if several else eid, text, corners, h, rotation, layer, chain)

    # ---- dimensions --------------------------------------------------------

    def _dimension(self, dim, eid: str) -> None:
        where = self.file_rel or "DXF"
        dimtype = dim.dimtype
        if dimtype not in (0, 1):
            self.warnings.append(f"{where}: {eid} is not a linear dimension (type {dimtype}); not read")
            return
        if dimtype == 0 and not dim.dxf.hasattr("angle"):
            angle = dimension_angle_from_block(dim)
            if angle is None:
                # AutoCAD omits group code 50 when the angle is the DXF default 0: measure along x, as the
                # synthetic reader (dxf_extract) does, and say so.
                angle = 0.0
                self.warnings.append(f"{where}: {eid} states no angle and its block draws no dimension line; "
                                     "measured at the DXF default angle 0 (assumed)")
            # On the in-memory entity only (the file is never saved), so the shared measurement reads it.
            dim.dxf.angle = angle
        span, measured = _linear_dimension_span(dim)
        if not measured or measured <= MIN_DIMENSION_UNITS:
            self.warnings.append(f"{where}: {eid} measures {measured or 0:.3g} units; dropped")
            return
        text = dim.dxf.get("text") or None
        if text is not None and text.strip() in ("", "<>"):
            text = None
        self.dims.append(DimensionPrim(id=eid, p1=_xy(span[0]), p2=_xy(span[1]), measured_units=_r(measured),
                                       text=text))


def dimension_angle_from_block(dim) -> Optional[float]:
    """Direction (degrees, 0 <= a < 180) of the dimension line drawn in a linear dimension's ``*D`` block.

    ``defpoint`` lies on the dimension line, at the foot of one extension line (which one depends on the writer:
    ezdxf puts it at the first, AutoCAD at the second). The extension lines are perpendicular to the dimension line,
    so the dimension line is the block LINE collinear with ``defpoint`` (``defpoint`` on the line or on its
    extension: AutoCAD draws the dimension line from arrow base to arrow base, one arrow length short of
    ``defpoint``) that is perpendicular to ``defpoint - defpoint2`` or to ``defpoint - defpoint3``; an extension
    line through ``defpoint`` is parallel to one of them. With both offsets zero the longest such line is taken.
    None when the block draws no such line."""
    try:
        parts = [e for e in dim.virtual_entities() if e.dxftype() == "LINE"]
    except Exception:  # noqa: BLE001 - a broken or missing block: no recovery
        return None
    d = Vec3(dim.dxf.defpoint)
    feet = [Vec3(dim.dxf.get(key, d)) for key in ("defpoint2", "defpoint3")]
    scale = max([(f - d).magnitude for f in feet] + [(feet[1] - feet[0]).magnitude, 1e-9])
    tol = max(1e-6, 1e-5 * scale)
    offsets = [(d - f).normalize() for f in feet if (d - f).magnitude > tol]
    best = None
    for line in parts:
        a, b = Vec3(line.dxf.start), Vec3(line.dxf.end)
        seg = b - a
        length = seg.magnitude
        if length <= tol:
            continue
        u = seg / length
        t = (d - a).dot(u)
        if ((a + u * t) - d).magnitude > tol:
            continue                                       # defpoint is not on the line or its extension
        score = min((abs(o.dot(u)) for o in offsets), default=0.0)
        if score > DIM_LINE_TOL:
            continue                                       # an extension line, not the dimension line
        key = (score, -length)
        if best is None or key < best[0]:
            best = (key, u)
    if best is None:
        return None
    u = best[1]
    angle = math.degrees(math.atan2(u.y, u.x)) % 180.0
    snapped = round(angle / 90.0) * 90.0
    if abs(angle - snapped) < 1e-7:
        angle = snapped % 180.0
    return round(angle, 9)
