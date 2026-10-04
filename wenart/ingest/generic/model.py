"""The adapter-neutral page model of the generic plan core (docs/milestone7.md §1.2).

Every adapter (``wenart.ingest.cad_pdf``, ``wenart.ingest.dxf_generic``, ``wenart.ingest.raster``) reads one drawn
page into a ``GenericPage``: strokes (lines, polylines, arcs, circles, flattened curves) with colour, fill, width
and, for DXF, layer and block names; text runs; dimension entities when the format has them; and for raster pages
the wall mask computed from the pixels. Coordinates are page units with **y up** (PDF points, DXF drawing units or
pixels), so one transform maps them to the building frame. ``core.extract`` does everything else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

STROKE_KINDS = ("line", "polyline", "arc", "circle", "curve")
SOURCE_KINDS = ("cad_pdf", "dxf", "raster_scan", "raster_photo")
TEXT_SOURCES = ("vector", "ocr", "ai")


@dataclass
class Stroke:
    """One drawn line, polyline, arc, circle or flattened curve, in page units (y up)."""
    id: str                                   # "path:123", "ent:1A2B", "seg:45" (raster)
    kind: str                                 # one of STROKE_KINDS
    pts: list[tuple[float, float]]            # flattened, >= 1 point (a dot has two equal points)
    closed: bool = False
    colour: Optional[tuple[float, float, float]] = None   # stroke RGB 0..1; None = unknown (raster: dark)
    fill: Optional[tuple[float, float, float]] = None     # fill RGB 0..1 when the path is filled
    width: float = 0.0                                    # line width in page units (0 = hairline)
    layer: Optional[str] = None                           # DXF layer
    block: Optional[str] = None                           # DXF INSERT name chain, outermost first: "A/B"
    arc: Optional[dict] = None                            # {"center": (x, y), "radius", "start_deg", "end_deg"}
    source: str = "vector"                                # "vector" | "raster"

    def bbox(self) -> tuple[float, float, float, float]:
        xs = [p[0] for p in self.pts]
        ys = [p[1] for p in self.pts]
        return (min(xs), min(ys), max(xs), max(ys))


@dataclass
class TextRun:
    """One line of text with its box (page units, y up)."""
    id: str
    text: str
    box: tuple[float, float, float, float]
    height: float
    rotation_deg: float = 0.0
    source: str = "vector"                    # one of TEXT_SOURCES
    evidence: list[dict] = field(default_factory=list)   # building.evidence dicts (ocr/ai: model, pass, confidence)


@dataclass
class DimensionPrim:
    """A dimension the format states as such (DXF DIMENSION); PDF and raster dimensions are found by the core."""
    id: str
    p1: tuple[float, float]
    p2: tuple[float, float]
    measured_units: float                     # in page units
    text: Optional[str] = None                # text override as drawn, None = the measurement


@dataclass
class MaskLayer:
    """A boolean wall mask; pixel (row r, col c) covers page x in [x0 + c*px, x0 + (c+1)*px] and page y in
    [y1 - (r+1)*px, y1 - r*px] where ``origin`` = (x0, y1) is the page point of the top-left pixel corner."""
    mask: "object"                            # numpy bool array [rows, cols]
    origin: tuple[float, float]
    px: float                                 # page units per pixel


@dataclass
class GenericPage:
    file: str                                 # project-relative path
    page: int                                 # 1-based
    source_kind: str                          # one of SOURCE_KINDS
    units: str                                # "pt" | "dxf" | "px"
    units_to_m: Optional[float]               # known a priori (DXF $INSUNITS); None = resolved by the core
    size: tuple[float, float]                 # page width, height in page units
    strokes: list[Stroke] = field(default_factory=list)
    texts: list[TextRun] = field(default_factory=list)
    dimensions: list[DimensionPrim] = field(default_factory=list)
    wall_mask: Optional[MaskLayer] = None     # raster pages give the mask directly
    wall_hint_layers: tuple[str, ...] = ()    # DXF layers that look like walls (WALL, A-WALL, DUVAR, ...)
    to_original: Optional[list[list[float]]] = None   # 3x3 page units -> original image pixels (photos)
    dpi: Optional[float] = None               # raster pages: pixels per inch of the (rectified) image, if known
    warnings: list[str] = field(default_factory=list)
