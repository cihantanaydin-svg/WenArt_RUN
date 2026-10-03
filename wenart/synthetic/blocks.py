"""The one place where drawing block names, layer names and sizes are defined.

``wenart.ingest`` imports this table: a block name -> furniture type is a
lookup, never a guess. Unknown block names map to ``unknown`` and the piece
is marked ``unverified`` (see docs/milestone2.md, conventions).

Block local frame (furniture): footprint rectangle centred at the origin,
``size = [width (X), depth (Y)]`` in metres, front side = -Y, so a piece
inserted with ``rotation`` faces ``front_deg = (270 + rotation) mod 360``.
Each block draws its rectangle plus a short line on the front edge.

Opening blocks: the insert point is the opening centre on the wall centre
line, the insert rotation follows the wall direction. The block name carries
the clear width in centimetres (``KAPI_90`` = 0.90 m door).
"""
from __future__ import annotations

import re
from typing import Optional

# name -> (furniture type, width (X), depth (Y)) in metres.
BLOCKS: dict[str, tuple[str, float, float]] = {
    "KANEPE_3LU": ("sofa", 2.2, 0.9),
    "KANEPE_2LI": ("sofa", 1.6, 0.9),
    "KOLTUK": ("armchair", 0.9, 0.9),
    "SEHPA": ("table_coffee", 1.0, 0.6),
    "YEMEK_MASASI": ("table_dining", 1.6, 0.9),
    "SANDALYE": ("chair", 0.45, 0.45),
    "TV_UNITESI": ("tv_unit", 1.6, 0.45),
    "KITAPLIK": ("bookshelf", 1.0, 0.35),
    "YATAK_CIFT": ("bed_double", 1.6, 2.0),
    "YATAK_TEK": ("bed_single", 0.9, 2.0),
    "KOMIDIN": ("nightstand", 0.5, 0.4),
    "DOLAP": ("wardrobe", 1.8, 0.6),
    "SIFONYER": ("dresser", 1.2, 0.5),
    "CALISMA_MASASI": ("desk", 1.4, 0.7),
    "TEZGAH": ("kitchen_counter", 2.4, 0.6),
    "BUZDOLABI": ("fridge", 0.7, 0.7),
    "OCAK": ("stove", 0.6, 0.6),
    "EVIYE": ("sink_kitchen", 0.8, 0.5),
    "LAVABO": ("washbasin", 0.6, 0.45),
    "KLOZET": ("toilet", 0.4, 0.7),
    "DUS": ("shower", 0.9, 0.9),
    "KUVET": ("bathtub", 1.7, 0.75),
    "CAMASIR_MAK": ("washing_machine", 0.6, 0.6),
}

# Blocks with a clear footprint but no known type. Their size is "as drawn":
# the generator picks a size per project and the extractor must read the
# rectangle inside the block definition. The type is always ``unknown``.
UNKNOWN_BLOCKS: tuple[str, ...] = ("BLOK_A", "BLOK_B")

# Opening blocks by clear width in centimetres.
DOOR_WIDTHS_CM: tuple[int, ...] = (80, 90)
WINDOW_WIDTHS_CM: tuple[int, ...] = (60, 120, 180)
DOOR_BLOCKS: tuple[str, ...] = tuple(f"KAPI_{w}" for w in DOOR_WIDTHS_CM)
WINDOW_BLOCKS: tuple[str, ...] = tuple(f"PENCERE_{w}" for w in WINDOW_WIDTHS_CM)

# Window symbol: two parallel lines this far apart (metres) plus end lines.
WINDOW_SYMBOL_DEPTH = 0.10

# DXF layers.
LAYER_WALLS = "DUVAR"
LAYER_DOORS = "KAPI"
LAYER_WINDOWS = "PENCERE"
LAYER_TEXT = "YAZI"
LAYER_DIMENSIONS = "OLCU"
LAYER_FURNITURE = "MOBILYA"
LAYERS: tuple[str, ...] = (LAYER_WALLS, LAYER_DOORS, LAYER_WINDOWS, LAYER_TEXT, LAYER_DIMENSIONS, LAYER_FURNITURE)

_OPENING_RE = re.compile(r"^(KAPI|PENCERE)_(\d+)$")


def furniture_type(block_name: str) -> str:
    """Block name -> furniture type; anything not in BLOCKS is ``unknown``."""
    entry = BLOCKS.get(block_name)
    return entry[0] if entry else "unknown"


def furniture_size(block_name: str) -> Optional[tuple[float, float]]:
    """(width, depth) in metres for known blocks, None for unknown ones."""
    entry = BLOCKS.get(block_name)
    return (entry[1], entry[2]) if entry else None


def opening_from_block(block_name: str) -> Optional[tuple[str, float]]:
    """``KAPI_90`` -> ("door", 0.9); ``PENCERE_120`` -> ("window", 1.2); other names -> None."""
    match = _OPENING_RE.match(block_name)
    if not match:
        return None
    kind = "door" if match.group(1) == "KAPI" else "window"
    return kind, int(match.group(2)) / 100.0


# --------------------------------------------------------------------------
# synthetic-06 (docs/milestone7.md §5.2): a plan drawn "the real way" in
# inches with English layer and block names. The generic DXF adapter reads
# it; nothing in wenart.ingest looks these names up (the generic core types
# blocks by its own keyword table), they are listed here so the generator and
# the truth use one table.
# --------------------------------------------------------------------------

# AIA-style layers and their ACI colours (7 = black on the sheet).
CAD_LAYER_WALLS = "A-WALL"
CAD_LAYER_DOORS = "A-DOOR"
CAD_LAYER_GLAZING = "A-GLAZ"
CAD_LAYER_FURNITURE = "A-FURN"
CAD_LAYER_ANNOTATION = "A-ANNO"
CAD_LAYER_DIMENSIONS = "A-DIMS"
CAD_LAYERS: tuple[tuple[str, int], ...] = (
    (CAD_LAYER_WALLS, 7), (CAD_LAYER_DOORS, 2), (CAD_LAYER_GLAZING, 4), (CAD_LAYER_FURNITURE, 8),
    (CAD_LAYER_ANNOTATION, 7), (CAD_LAYER_DIMENSIONS, 1),
)

# Block name -> (furniture type, width (X), depth (Y)) in INCHES; same local frame as BLOCKS (footprint centred
# at the origin, front = -Y). DINING-6 is the table; its six chairs are nested CHAIR inserts.
CAD_BLOCKS: dict[str, tuple[str, float, float]] = {
    "BED-DOUBLE": ("bed_double", 60.0, 80.0),
    "SOFA-3": ("sofa", 84.0, 36.0),
    "DINING-6": ("table_dining", 72.0, 36.0),
    "CHAIR": ("chair", 18.0, 18.0),
    "WC": ("toilet", 20.0, 28.0),
    "BASIN": ("washbasin", 20.0, 16.0),
}
# The room tag: one attribute definition, no frame (a frame would be a drawn shape the core has to explain).
CAD_ROOMTAG = "ROOMTAG"
CAD_ROOMTAG_ATTRIBUTE = "NAME"
# DINING-6: chair centres and rotations in the table's frame (2 per long side, 1 per end; 2 in clear of the table).
CAD_DINING_CHAIRS: tuple[tuple[float, float, float], ...] = (
    (-18.0, 29.0, 0.0), (18.0, 29.0, 0.0), (-18.0, -29.0, 180.0), (18.0, -29.0, 180.0),
    (47.0, 0.0, 270.0), (-47.0, 0.0, 90.0),
)
