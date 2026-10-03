"""What an extractor reads from one drawn page, before rooms are derived.

Both extractors (``dxf_extract``, ``pdf_extract``) return a ``LevelExtraction``.
Geometry is already in the building frame (metres, X right, Y up, origin at
the outer corner of the outer walls of that page); every item keeps its page
box (DXF millimetres or PDF points, origin bottom-left) for the debug image
and one evidence dict that points at the source entity.

The small text helpers at the end (``text_role``, ``parse_scale_text``,
``parse_number``, ``normalise_level``) are shared by the extractors and the
classifier so the plan vocabulary (Turkish, and since Milestone 7 English
titles and imperial lengths) is interpreted in one place. Numbers go through
``wenart.units`` (one parser for metric and imperial text).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B
from wenart import units as U

# Metres per PDF point at scale 1:1 (1 pt = 1/72 inch).
METRES_PER_POINT = 0.0254 / 72.0

# How far from the door centre the swing probe point lies (metres). The room
# that contains the probe is the swing side.
DOOR_SWING_PROBE = 0.3

# A metric scale note; an imperial note (``SCALE 1/4" = 1'-0"``) is not 1:4 (generic.scale.note_ratio reads it).
_SCALE_RE = re.compile(r"(?:OLCEK|ÖLÇEK|OLÇEK|SCALE)\s*:?\s*1\s*[/:]\s*(\d+)(?!\d|\.\d|\s*(?:\"|”|″|''|IN\b|INCH))",
                       re.IGNORECASE)

# Page class keywords (ASCII-folded, upper case), first match wins: Turkish titles, then the English class words
# of docs/milestone7.md §2.1 (``FURNITURE (LAYOUT) PLAN`` before ``FLOOR PLAN``: "FIRST FLOOR FURNITURE PLAN").
CLASS_KEYWORDS = [
    ("MOBILYA", "furniture_plan"),
    (re.compile(r"\bFURNITURE\s+(?:LAYOUT\s+)?PLAN"), "furniture_plan"),
    ("KAT PLANI", "floor_plan"),
    (re.compile(r"\bFLOOR\s+PLAN"), "floor_plan"),
    ("KESIT", "section"),
    ("GORUNUS", "elevation"),
    ("VAZIYET", "site_plan"),
]


@dataclass
class TextItem:
    """One text run as drawn (DXF TEXT or merged PDF chars)."""
    text: str
    start: tuple[float, float]       # baseline start / insert point, page units
    box: list[float]                 # [x0, y0, x1, y1], page units
    rotation_deg: float
    entity: str                      # "TEXT:<handle>" or "char:<n>"
    height: float                    # text height (DXF) or font size (PDF), page units
    role: str = "other"              # title | scale | dimension | room_label | other
    evidence: Optional[dict] = None
    element_id: Optional[str] = None  # room id once a label is placed (pipeline)
    # Milestone 7 (generic core): the label block this text stands for (``generic.labels.LabelBlock``: name lines,
    # printed size and area, exterior flag) and whether the page is labelled in Turkish (casing, placeholder).
    block: Optional[object] = None
    turkish: Optional[bool] = None


@dataclass
class WallItem:
    start: tuple[float, float]       # building metres
    end: tuple[float, float]
    thickness: float
    box: list[float]                 # page units
    entity: str
    evidence: dict
    exterior: bool = False           # set by rooms.derive_rooms
    status: str = "verified"
    element_id: Optional[str] = None # building id once assigned (pipeline)


@dataclass
class OpeningItem:
    kind: str                        # door | window | opening
    width: float                     # metres
    center: tuple[float, float]      # building metres, on the wall centre line
    rotation_deg: float              # wall direction (+180 for doors swinging the other way)
    box: list[float]
    entity: str
    evidence: dict
    swing_point: Optional[tuple[float, float]] = None  # doors: a point in the room it opens into
    block: Optional[str] = None
    status: str = "verified"
    element_id: Optional[str] = None
    # Milestone 7 (docs/milestone7.md §1.3, §2.6, §2.7.1); defaults keep the old extractors unchanged.
    virtual: bool = False                               # a separator line with no wall (kind "opening")
    line: Optional[tuple[tuple[float, float], tuple[float, float]]] = None  # virtual separator, building metres
    height: Optional[float] = None                      # metres; None = the build's default
    sill: Optional[float] = None                        # windows: sill height, metres
    assumed: list[str] = field(default_factory=list)    # names of values that are assumed ("height", "sill")
    type_raw: Optional[str] = None                      # e.g. "unclassified gap content"


@dataclass
class FurnitureItem:
    type: str                        # schema furniture type or "unknown"
    type_raw: Optional[str]          # block name, None for PDF footprints
    center: tuple[float, float]
    size: tuple[float, float]        # [width (X), depth (Y)] in the piece's frame
    rotation_deg: float
    front_deg: Optional[float]
    box: list[float]
    entity: str
    evidence: dict
    status: str = "verified"
    element_id: Optional[str] = None
    # Milestone 7 (docs/milestone7.md §1.3, §2.8, §3.3).
    type_method: Optional[str] = None                   # block_name | rule | ai_two_pass | none
    type_candidates: list[dict] = field(default_factory=list)  # [{type, model, pass, confidence}]
    extra_evidence: list[dict] = field(default_factory=list)   # further evidence (e.g. the two AI passes)
    details: dict = field(default_factory=dict)         # "stair": {...}, "counter_run": {...}, "candidate_key": ...


@dataclass
class DimensionItem:
    p1: tuple[float, float]          # measured span, building metres (dimension-line end points)
    p2: tuple[float, float]
    measured: float                  # metres, from the geometry
    printed: str                     # text as drawn, e.g. "3,99"
    printed_value: Optional[float]   # metres, parsed from the text (None if not a number)
    box: list[float]                 # text box, page units
    entity: str
    evidence: dict
    tick_count: int = 0              # PDF: 45-degree ticks found at the ends (0..2)
    wall_ids: list[str] = field(default_factory=list)  # walls the dimension runs along (pipeline)
    conflict_id: Optional[str] = None                   # set when text and geometry disagree


@dataclass
class LevelExtraction:
    """Everything one page says about one level, in the building frame."""
    file: str                        # project-relative path
    page: int                        # 1-based (1 for DXF)
    level_id: str
    units: str                       # "mm" (DXF) or "pt" (PDF)
    page_size: Optional[list[float]] = None     # PDF: [width, height] in points
    scale: Optional[dict] = None                # schema page.scale block or None
    transform_to_building: Optional[list[float]] = None  # affine page units -> metres
    title: Optional[TextItem] = None
    scale_text: Optional[TextItem] = None
    texts: list[TextItem] = field(default_factory=list)
    labels: list[TextItem] = field(default_factory=list)   # room label candidates
    walls: list[WallItem] = field(default_factory=list)
    openings: list[OpeningItem] = field(default_factory=list)
    furniture: list[FurnitureItem] = field(default_factory=list)
    dimensions: list[DimensionItem] = field(default_factory=list)
    # Conflicts found while reading the page, as schema conflict dicts without an id
    # (kind, element_ids, description, resolution): scale disagreements, blocks drawn at
    # another size than their name says, etc. Items have no element id yet, so the
    # description names the source entity; the pipeline copies them into the building.
    conflicts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Milestone 7 (docs/milestone7.md §1.2); defaults keep the old extractors unchanged.
    source_kind: Optional[str] = None               # cad_pdf | dxf | raster_scan | raster_photo (generic core only)
    units_system: Optional[str] = None              # imperial | metric (None = metric, old extractors)
    level_assumed: bool = False                     # level id/label assumed (no level title on the page)
    site: Optional[dict] = None                     # schema "site" block (plot walls, areas, decor)
    separators: list[OpeningItem] = field(default_factory=list)  # virtual separators (kind opening, virtual)
    candidates: list[dict] = field(default_factory=list)         # furniture candidates waiting for AI typing
    wall_mask_png: Optional[str] = None             # debug PNG of the wall mask
    notes: list[str] = field(default_factory=list)  # report lines (rules that fired, dropped separators, ...)
    review: list[str] = field(default_factory=list) # needs_review reasons found while reading the page (generic core)
    report: dict = field(default_factory=dict)      # generic core: data for the report and debug image (not saved)

    @property
    def metres_per_unit(self) -> Optional[float]:
        return self.scale["metres_per_unit"] if self.scale else None

    def doors(self) -> list[OpeningItem]:
        return [o for o in self.openings if o.kind == "door"]

    def windows(self) -> list[OpeningItem]:
        return [o for o in self.openings if o.kind == "window"]


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def parse_scale_text(text: str) -> Optional[int]:
    """``ÖLÇEK 1/100`` -> 100; None when the text is not a (metric) scale note."""
    match = _SCALE_RE.search(B.fold_ascii(text).upper())
    return int(match.group(1)) if match else None


def parse_number(text: str) -> Optional[float]:
    """``3,45`` / ``3.45`` / ``345 cm`` -> metres as float; None if not a plain metric number.

    Units: a bare number or ``m`` means metres; ``cm`` and ``mm`` are converted (``wenart.units``; feet and
    inches are lengths too, but not a plain number here: ``text_role`` calls them dimensions separately).
    """
    length = U.parse_length(text)
    return length.metres if length is not None and length.system == "metric" else None


def page_class_for(text: str) -> Optional[str]:
    """Page class from the keywords in a title text, or None."""
    folded = B.fold_ascii(text).upper()
    for keyword, page_class in CLASS_KEYWORDS:
        if (keyword.search(folded) if isinstance(keyword, re.Pattern) else keyword in folded):
            return page_class
    return None


# English level titles (§2.1) live in ``building.normalise_level_label`` (title case, like the Turkish ones).
english_level_label = B.english_level_label


def normalise_level(title_raw: str) -> Optional[tuple[str, int]]:
    """Level title (Turkish or English, ``building.normalise_level_label``) -> (label, order), or None:
    ``GROUND FLOOR PLAN`` -> (``Ground Floor``, 0), ``ZEMİN KAT PLANI`` -> (``Zemin Kat``, 0)."""
    return B.normalise_level_label(title_raw)


def text_role(text: str) -> str:
    """Rough role of a text on a plan: title, scale, dimension or room label candidate."""
    stripped = text.strip()
    if not stripped:
        return "other"
    if parse_scale_text(stripped) is not None:
        return "scale"
    if parse_number(stripped) is not None or U.parse_length(stripped) is not None:
        return "dimension"
    if page_class_for(stripped) is not None or normalise_level(stripped) is not None:
        return "title"
    return "room_label"
