"""The working model of the sheets stage (docs/milestone10.md §1.2, §3.1).

What: ``Sheet`` (one drawing surface: a DXF model space or layout, a PDF page, an image) with its entities and
texts, ``Ent`` (one source entity: all strokes of a DXF entity or INSERT, one PDF path, one DIMENSION) and ``Txt``
(one text: a TEXT, an MTEXT with its paragraphs joined, an ATTRIB, a PDF text run), and ``Region`` (one drawing
region of a sheet, written to ``sheets.json``).

Why: the sheets stage works on every format the same way. The adapters of the generic core already read DXF/DWG
(``wenart.ingest.dxf_generic``) and vector PDF pages (``wenart.ingest.cad_pdf``) into strokes and texts in source
units; this module groups them back into the entities the split clusters (an INSERT is one entity, its box is the
box of its block geometry) without reading the files again.

How: ``entities_from_page`` groups the strokes of a ``GenericPage`` by their top-level entity id (``INSERT:4B/3`` ->
``INSERT:4B``, ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``), the texts by their entity
(an MTEXT's paragraphs are one text), and adds one entity per DIMENSION (the box of its measured span). A text's
point is the centre of its estimated box (the adapters estimate boxes from the character count, so an MTEXT column
width never makes a text wide). Boxes are ``(x0, y0, x1, y1)`` in source units, y up.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

Box = tuple[float, float, float, float]

_INDEX_RE = re.compile(r"\[\d+\]$")


@dataclass
class Ent:
    """One source entity (all its strokes) in source units."""
    id: str                                   # evidence entity: LINE:2F, INSERT:4B, HATCH:5C, path:12, DIMENSION:7A
    kind: str                                 # LINE, INSERT, HATCH, ..., path, DIMENSION
    layer: Optional[str]
    box: Box
    strokes: list = field(default_factory=list)   # the generic-model Strokes of the entity
    block: Optional[str] = None               # INSERT name (outermost)
    rect: Optional[Box] = None                # the entity is one closed axis-aligned rectangle with this box
    dim: Optional[object] = None              # DIMENSION: the DimensionPrim

    @property
    def centre(self) -> tuple[float, float]:
        return ((self.box[0] + self.box[2]) / 2.0, (self.box[1] + self.box[3]) / 2.0)


@dataclass
class Txt:
    """One text (paragraphs of an MTEXT joined with a space)."""
    id: str                                   # TEXT:2A, MTEXT:2B, ATTRIB:3C, INSERT:4B/2, char:12
    text: str
    box: Box
    height: float                             # cap height in source units (the tallest paragraph)
    rotation_deg: float = 0.0
    layer: Optional[str] = None
    evidence: dict = field(default_factory=dict)

    @property
    def point(self) -> tuple[float, float]:
        return ((self.box[0] + self.box[2]) / 2.0, (self.box[1] + self.box[3]) / 2.0)


@dataclass
class Sheet:
    """One drawing surface of a document."""
    id: str                                   # s1, s2 ...
    space: str                                # model | layout:<name> | page:<n>
    file: str                                 # project-relative path
    page: int                                 # 1-based PDF page; 1 for DXF model space
    ents: list[Ent] = field(default_factory=list)
    texts: list[Txt] = field(default_factory=list)
    generic_page: Optional[object] = None     # the GenericPage the entities come from (None for raster pages)
    raster: bool = False                      # an image page: one region, classified by the pipeline's OCR
    size: Optional[tuple[float, float]] = None   # raster pages: width, height in pixels
    box: Optional[Box] = None                 # set by the split
    frames: list = field(default_factory=list)
    gap: Optional[float] = None


@dataclass
class Region:
    """One drawing region (``sheets.json`` ``regions[]``)."""
    id: str
    file: str
    sheet: Sheet
    box: Box                                  # geometry box with the points of its texts
    geometry_box: Box                         # the entities only
    ents: list[Ent] = field(default_factory=list)
    texts: list[Txt] = field(default_factory=list)
    frame: Optional[str] = None
    kind: str = "drawing"                     # drawing | box (a lone rectangle: title box) | text (texts only)
    cls: str = "other"
    class_method: str = "none"
    class_confidence: float = 0.0
    status: str = "unverified"
    title: Optional[dict] = None
    title_txt: Optional[Txt] = None
    features: dict = field(default_factory=dict)
    level: Optional[dict] = None
    variant_group: Optional[str] = None
    variant: Optional[str] = None
    variant_slug: Optional[str] = None
    variant_gloss: Optional[str] = None
    ai: list = field(default_factory=list)
    metres_per_unit: Optional[float] = None
    transform_to_building: Optional[list] = None
    registration: Optional[dict] = None
    use: str = "ignored"
    ignored_reason: Optional[str] = None
    conflicts: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    notes: list = field(default_factory=list)  # report lines (not in sheets.json)

    @property
    def n_entities(self) -> int:
        return len(self.ents) + len(self.texts)

    def strokes(self) -> list:
        return [st for e in self.ents for st in e.strokes]


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def box_union(boxes) -> Optional[Box]:
    boxes = list(boxes)
    if not boxes:
        return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def box_of_points(pts) -> Box:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def box_size(box: Box) -> tuple[float, float]:
    return (box[2] - box[0], box[3] - box[1])


def box_inside(inner: Box, outer: Box, tol: float = 0.0) -> bool:
    return (inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol and inner[2] <= outer[2] + tol
            and inner[3] <= outer[3] + tol)


def box_distance(a: Box, b: Box) -> float:
    """Distance between two boxes (0 when they touch or overlap)."""
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def point_box_distance(p, b: Box) -> float:
    dx = max(b[0] - p[0], 0.0, p[0] - b[2])
    dy = max(b[1] - p[1], 0.0, p[1] - b[3])
    return math.hypot(dx, dy)


def in_box(p, b: Box, tol: float = 0.0) -> bool:
    return b[0] - tol <= p[0] <= b[2] + tol and b[1] - tol <= p[1] <= b[3] + tol


def round_box(box, nd: int = 3) -> list[float]:
    return [round(float(v), nd) + 0.0 for v in box]


def top_entity(stroke_id: str) -> str:
    """The top-level entity of a stroke or text id: ``INSERT:4B[2]/3`` -> ``INSERT:4B``, ``LWPOLYLINE:2F:1`` ->
    ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``, ``MTEXT:2B:1`` -> ``MTEXT:2B``, ``path:12`` -> ``path:12``."""
    head = stroke_id.split("/")[0].split("#")[0]
    head = _INDEX_RE.sub("", head)
    parts = head.split(":")
    return ":".join(parts[:2])


def _axis_rectangle(st) -> Optional[Box]:
    """Box of a closed stroke whose 4 corners form an axis-aligned rectangle (a frame or title box candidate)."""
    if not st.closed or st.fill is not None or len(st.pts) != 4:
        return None
    xs = sorted({round(p[0], 6) for p in st.pts})
    ys = sorted({round(p[1], 6) for p in st.pts})
    if len(xs) != 2 or len(ys) != 2:
        return None
    return (xs[0], ys[0], xs[1], ys[1])


def entities_from_page(page, file_rel: str) -> tuple[list[Ent], list[Txt]]:
    """Entities and texts of a ``GenericPage`` (DXF or vector PDF), in drawing order of their first stroke."""
    groups: dict[str, list] = {}
    order: list[str] = []
    for st in page.strokes:
        key = top_entity(st.id)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(st)
    ents: list[Ent] = []
    for key in order:
        strokes = groups[key]
        box = box_union(st.bbox() for st in strokes)
        kind = key.split(":")[0]
        block = strokes[0].block.split("/")[0] if strokes[0].block else None
        rect = _axis_rectangle(strokes[0]) if len(strokes) == 1 else None
        layer = strokes[0].layer
        ents.append(Ent(id=key, kind=kind, layer=layer, box=box, strokes=strokes, block=block, rect=rect))
    for dim in page.dimensions:
        ents.append(Ent(id=dim.id, kind="DIMENSION", layer=None, box=box_of_points([dim.p1, dim.p2]), dim=dim))
    texts: list[Txt] = []
    by_id: dict[str, Txt] = {}
    for run in page.texts:
        key = top_entity(run.id) if run.id.startswith("MTEXT:") else run.id
        layer = (run.evidence[0].get("layer") if run.evidence else None)
        if key in by_id:
            t = by_id[key]
            t.text = f"{t.text} {run.text}".strip()
            t.box = box_union([t.box, run.box])
            t.height = max(t.height, float(run.height))
            continue
        ev = dict(run.evidence[0]) if run.evidence else {"file": file_rel, "method": "vector", "confidence": 1.0,
                                                          "entity": key, "text": run.text}
        ev["entity"] = key
        t = Txt(id=key, text=run.text, box=tuple(run.box), height=float(run.height),
                rotation_deg=float(run.rotation_deg), layer=layer, evidence=ev)
        by_id[key] = t
        texts.append(t)
    for t in texts:
        t.evidence["text"] = t.text
    return ents, texts
