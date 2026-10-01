"""What an extractor reads from one drawn page, before rooms are derived.

Both extractors (``dxf_extract``, ``pdf_extract``) return a ``LevelExtraction``.
Geometry is already in the building frame (metres, X right, Y up, origin at
the outer corner of the outer walls of that page); every item keeps its page
box (DXF millimetres or PDF points, origin bottom-left) for the debug image
and one evidence dict that points at the source entity.

The small text helpers at the end (``text_role``, ``parse_scale_text``,
``parse_number``) are shared by the extractors and the classifier so the
Turkish plan vocabulary is interpreted in one place.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B

# Metres per PDF point at scale 1:1 (1 pt = 1/72 inch).
METRES_PER_POINT = 0.0254 / 72.0

# How far from the door centre the swing probe point lies (metres). The room
# that contains the probe is the swing side.
DOOR_SWING_PROBE = 0.3

_SCALE_RE = re.compile(r"(?:OLCEK|ÖLÇEK|OLÇEK|SCALE)\s*:?\s*1\s*[/:]\s*(\d+)", re.IGNORECASE)
_NUMBER_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*(?:m|cm|mm)?\s*$", re.IGNORECASE)

# Page class keywords (ASCII-folded, upper case), first match wins.
CLASS_KEYWORDS = [
    ("MOBILYA", "furniture_plan"),
    ("KAT PLANI", "floor_plan"),
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
    """``ÖLÇEK 1/100`` -> 100; None when the text is not a scale note."""
    match = _SCALE_RE.search(B.fold_ascii(text).upper())
    return int(match.group(1)) if match else None


def parse_number(text: str) -> Optional[float]:
    """``3,45`` / ``3.45`` / ``345 cm`` -> metres as float; None if not a plain number.

    Units: a bare number or ``m`` means metres; ``cm`` and ``mm`` are converted.
    """
    match = _NUMBER_RE.match(text)
    if not match:
        return None
    value = float(match.group(1).replace(",", "."))
    lowered = text.lower()
    if lowered.rstrip().endswith("mm"):
        return value / 1000.0
    if lowered.rstrip().endswith("cm"):
        return value / 100.0
    return value


def page_class_for(text: str) -> Optional[str]:
    """Page class from the keywords in a title text, or None."""
    folded = B.fold_ascii(text).upper()
    for keyword, page_class in CLASS_KEYWORDS:
        if keyword in folded:
            return page_class
    return None


def text_role(text: str) -> str:
    """Rough role of a text on a plan: title, scale, dimension or room label candidate."""
    stripped = text.strip()
    if not stripped:
        return "other"
    if parse_scale_text(stripped) is not None:
        return "scale"
    if parse_number(stripped) is not None:
        return "dimension"
    if page_class_for(stripped) is not None or B.normalise_level_label(stripped) is not None:
        return "title"
    return "room_label"
