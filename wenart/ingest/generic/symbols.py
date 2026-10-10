"""Furniture and site decor of the generic plan core (docs/milestone7.md §2.8, §2.5): clusters, composites, rules.

A real plan draws furniture as loose strokes with no block names (real01) or as DXF INSERTs; either way the
footprint must come from the geometry and the type from a rule, a block name or two agreeing AI passes:

1. **Strokes considered**: every stroke except the wall primitives, the strokes the openings own, the dimension
   strokes and glyph strokes inside text boxes (grown 10 %; a vector stroke only when all of it lies in one, a raster
   segment by itself). Polylines and closed paths are split into segments, and a
   segment is wall outline (dropped) when >= 90 % of its length lies within 20 mm of the bridged wall geometry (wall
   rectangles plus every opening rectangle) - real01's 94.7 m outline polyline runs across every window and door gap,
   so the whole stroke would never pass a 90 % test against the walls alone - or when >= 50 % of it lies inside the
   wall material (jamb lines crossing a wall). Dropped segments that close a piece's contour (a headboard 9 mm off the
   wall face) are given back to that piece. Segments inside the building outline are furniture strokes; the others
   are site strokes. A furniture segment that is straight, longer than 4.5 m and runs out of the building outline (the
   roof ridge on synthetic-07's attic plan, a grid axis) is dropped: it would chain every piece and door leaf it
   touches.
2. **Clusters**: union-find over segments closer than 20 mm (dots included); a cluster whose bbox lies >= 80 % inside
   another merges into it unless it is a closed polygon with both sides >= 0.3 m that fits a size-table type (a sink or
   hob in a counter stays its own piece) - but not when a closed contour of the container encloses it and it is the
   container's inner outline (>= 40 % of that contour's area: a bed's double outline, a table's inlay) or a detail
   on it (spanning < 60 % of the contour's short side: pillows on a bed). Clusters with both sides < 0.20 m are
   details (counted, dropped).
3. **Deterministic types**: *stair* (merged collinear tread strokes, split at a perpendicular divider crossing >= 80 %
   of them; each side with >= 5 equal, evenly spaced segments 0.20-0.35 m apart is a flight); *kitchen counter* (a
   chained polyline of >= 2 straight legs whose ends lie within 50 mm of a wall face, parallel to walls at 0.45-0.75 m:
   one piece per leg, the corner square to the longer leg; segments with an end on a wall face and perpendicular to
   it are the run's end caps); *block name* (DXF INSERT keywords, checked against the size table).
4. **Composite split**: a cluster that fits no size-table type, or that holds >= 2 top-level closed contours >= 0.20 m
   on both sides, is split. Closed contours are chains of strokes joined end to end (within 5 mm), polygonised and
   filled: a nightstand whose edge merely lies along the bed's edge keeps its own contour; contours overlapping < 15 %
   of the smaller are separate; equal-sized contours that touch each other (sofa cushions, wardrobe doors) are parts of
   one piece. Each top-level contour plus the strokes inside it seeds a piece; the remaining strokes are re-clustered
   at 2 mm (strokes joined end to end stay together) after the seed rings are removed and join the seed whose polygon
   contains them or the piece within 20 mm; edge contact never merges two pieces. Parts that fit no type and cannot
   be split stay **one composite** (``unknown``, ``unverified``, "possible group of N pieces"), never typed as one
   table or bed. A cluster drawn only by DXF block content splits by INSERT instance first (one piece per instance
   of a furniture-named block: a WC's tank and bowl stay one piece, DINING-6 gives its table and each CHAIR).
   Pieces whose outline a circle fits for >= 90 % get ``details`` ``shape "round"`` and ``circle_fit`` (§6.4).
5. Everything else is an **AI candidate** (§3): ``unknown``, ``unverified``, ``type_method "none"`` until two passes
   agree. Clusters > 4.5 m on a side are ``unknown``/``unverified`` and never asked.
6. **Site decor**: clusters outside the building outline: green fills or radial clusters -> ``plant``; edge and
   boundary lines (< 50 mm wide or > 4.5 m long) are not decor; else ``other``.

All coordinates are page metres (y up); ``box`` is in page units when ``units_to_m`` is given.

Milestone 11 (docs/milestone11.md §1.2 U8, U10, U12): the counter rule never reads a block's own strokes; a table
drawn with its chairs (a named table block, or an unknown composite) is split into the table and one chair per
chair part facing it (``split_table_chairs``); a kitchen cluster whose counter run is a closed outline along the
walls is split into counter legs, a peninsula (``kitchen_island``), the named hob and sink blocks and the rest
(``kitchen_split``). Only pieces that were never asked are split, so the AI candidates stay as they were.

Milestone 12 (docs/milestone12.md §4.1 D7, track R; section "Milestone 12" at the end of this file): layer words
and symbol shapes (room-number circle, door swing, north arrow) mark pieces that are not furniture
(``whole_symbol``; ``reading.read_furniture`` moves them to ``building["symbols"]``); the Turkish/English block
words of M12 (``BLOCK_KEYWORDS_M12``) type pieces after the answers only, so earlier questions keep their keys and
hashes; an untyped cluster is re-read (``reread``: symbol strokes out, counter runs, one part per block instance and
stroke group, each typed on its own); its unknown parts that fit a type are asked under content keys
(``extra_candidate``, ``extra_key``); a named block with a stray axis line keeps the named footprint
(``trim_stray_lines``).
"""
from __future__ import annotations

import hashlib
import math
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import polygonize, unary_union
from shapely.strtree import STRtree

from wenart import building as B
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import FurnitureItem, OpeningItem, WallItem

OUTLINE_NEAR_M = 0.02
OUTLINE_SHARE = 0.9
WALL_MATERIAL_SHARE = 0.5
TEXT_GROW = 0.10
CHAIN_M = 0.005
CLUSTER_M = 0.02
RECLUSTER_M = 0.002
CONTAIN_SHARE = 0.8
CONTAIN_KEEP_SIDE_M = 0.3
DETAIL_M = 0.20
LINE_DETAIL_M = 0.05           # a cluster whose minimum rectangle is thinner than this is a drawn line, not furniture
MAX_SIDE_M = 4.5
OVERSIZE_SPLIT_MAX_SEGS = 4000     # an oversized cluster with more segments is not split (time bound)
CONTOUR_MIN_M = 0.20
CONTOUR_OVERLAP = 0.15
ATTACH_M = 0.02
SNAP_DEG = 3.0
FOOTPRINT_CONFIDENCE = 0.9
SIZE_TOLERANCE = 0.15

STAIR_MERGE_M = 0.005
STAIR_DIVIDER_SHARE = 0.8
STAIR_MIN_TREADS = 5
STAIR_STEP_M = (0.20, 0.35)
STAIR_STEP_TOL = 0.10
TREAD_LENGTH_M = (0.5, 3.0)    # an isolated tread line spans a flight 0.5-3.0 m wide (size table: stair 0.7-3.0 m)
TREAD_ALIGN_M = 0.01           # equal tread lines: both ends within 10 mm (the stair rule's flight sides)
TREAD_WALL_M = 0.03            # the tread area, shrunk by 30 mm, must hold no wall
NOSING_M = 0.06                # Milestone 10 (real02): a tread drawn as a nosing strip, two lines <= 60 mm apart
LOOSE_TREAD_M = 0.4            # ... and treads cut by the stair's break line: the loose rule takes lines >= 0.4 m
LOOSE_OVERLAP = 0.8            # ... whose extent overlaps the flight's by >= 80 % of the shorter
COUNTER_END_M = 0.05
COUNTER_DEPTH_M = (0.45, 0.75)
FRONT_WALL_M = 0.25
# Block-named pieces (``_block_item``): types without a front (recognition.symbols.FRONTLESS_TYPES) and types whose
# back is their long side, which may take the corner rule (``corner_back_front``; not beds, toilets, baths: their
# back is a short side or they have none).
FRONTLESS_BLOCK_TYPES: tuple[str, ...] = ("table_dining", "table_coffee", "side_table", "floor_lamp", "potted_plant")
LONG_BACK_TYPES: tuple[str, ...] = ("washbasin", "wardrobe", "kitchen_counter", "sink_kitchen", "sofa", "tv_unit",
                                    "bookshelf", "dresser", "sideboard", "console_table", "shoe_cabinet",
                                    "display_cabinet", "tall_cabinet", "wall_cabinet", "desk")
CORNER_LONG_RATIO = 1.25
ROUND_SHARE = 0.9              # §6.4: round when a circle fits >= 90 % of the outline
L_ARM_M = (0.5, 1.3)           # Milestone 10: an L outline (the corner sofa) with both arms 0.5-1.3 m deep ...
L_NOTCH_SHARE = 0.15           # ... the open corner >= 15 % of its box ...
L_REST_SHARE = 0.08            # ... and <= 8 % of the box left open elsewhere (rounded or stepped corners)
L_BOX_M = 0.05
ROUND_TOL_M = 0.01
ROUND_TOL_REL = 0.03

# Built-in size table, used when wenart/recognition/size_table.yaml is missing or unreadable: plausible footprint
# (width range, depth range) in metres, either orientation, +15 % tolerance applied by ``fits``. Sources: standard
# furniture sizes (Neufert, manufacturer ranges), the synthetic block table (wenart/synthetic/blocks.py) and the
# real01 reference (tests/fixtures/real01_reference.yaml).
FALLBACK_SIZE_TABLE: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {
    "bed_single": ((0.8, 1.2), (1.8, 2.2)),
    "bed_double": ((1.35, 2.0), (1.85, 2.25)),
    "sofa": ((1.2, 3.0), (0.7, 1.1)),
    "armchair": ((0.6, 1.1), (0.6, 1.1)),
    "table_dining": ((0.7, 1.2), (0.8, 2.6)),
    "table_coffee": ((0.4, 1.2), (0.6, 1.4)),
    "desk": ((0.9, 2.0), (0.5, 0.9)),
    "chair": ((0.35, 0.65), (0.35, 0.65)),
    "wardrobe": ((0.8, 3.0), (0.5, 0.7)),
    "kitchen_counter": ((0.6, 5.0), (0.5, 0.75)),
    "kitchen_island": ((1.0, 2.5), (0.6, 1.2)),
    "fridge": ((0.55, 0.95), (0.55, 0.8)),
    "stove": ((0.45, 0.95), (0.5, 0.7)),
    "sink_kitchen": ((0.45, 1.2), (0.4, 0.6)),
    "washbasin": ((0.4, 0.9), (0.35, 0.6)),
    "toilet": ((0.35, 0.5), (0.55, 0.8)),
    "shower": ((0.7, 1.6), (0.7, 1.2)),
    "bathtub": ((1.4, 1.9), (0.65, 0.9)),
    "tv_unit": ((1.0, 2.4), (0.3, 0.6)),
    "bookshelf": ((0.6, 2.0), (0.25, 0.45)),
    "nightstand": ((0.35, 0.65), (0.3, 0.55)),
    "dresser": ((0.8, 1.6), (0.4, 0.6)),
    "washing_machine": ((0.55, 0.7), (0.55, 0.7)),
    "stair": ((0.7, 3.0), (1.5, 6.0)),
    "side_table": ((0.3, 0.7), (0.3, 0.7)),
    "floor_lamp": ((0.25, 0.6), (0.25, 0.6)),
    "potted_plant": ((0.2, 1.0), (0.2, 1.0)),
    # Milestone 10 (docs/milestone10.md §1.1; size_table.yaml has the sources).
    "sofa_corner": ((1.8, 4.0), (1.4, 3.0)),
    "chaise": ((0.55, 0.95), (1.3, 2.0)),
    "ottoman": ((0.35, 1.0), (0.35, 1.0)),
    "bench": ((0.8, 2.0), (0.3, 0.55)),
    "bar_stool": ((0.3, 0.5), (0.3, 0.5)),
    "office_chair": ((0.5, 0.75), (0.5, 0.75)),
    "console_table": ((0.7, 1.6), (0.25, 0.45)),
    "crib": ((0.6, 0.85), (1.15, 1.5)),
    "bunk_bed": ((0.85, 1.2), (1.9, 2.2)),
    "sideboard": ((1.0, 2.4), (0.35, 0.55)),
    "shoe_cabinet": ((0.5, 1.4), (0.2, 0.4)),
    "display_cabinet": ((0.5, 1.6), (0.3, 0.55)),
    "tall_cabinet": ((0.3, 1.2), (0.3, 0.7)),
    "wall_cabinet": ((0.3, 1.2), (0.25, 0.4)),
}

# Milestone 10 block-name words (docs/milestone10.md §1.1), tried before BLOCK_KEYWORDS: only words that name the
# type in English or Turkish (Turkish letters folded to ASCII, spaces and hyphens read as "_"); words of up to four
# letters must be a whole word of the name (BANK is a bench, BANKO a counter). The generic words YATAK (bed) and
# MASA (table) are tried after BLOCK_KEYWORDS (YATAK_TEK, YEMEK_MASASI say more), and BLOCK_KEYWORDS' KOLTUK
# (armchair in M7) is read as a seat: armchair or sofa by the size table, the corner sofa for an L outline.
BLOCK_KEYWORDS_M10: tuple[tuple[str, str], ...] = (
    # A TV console is the M7 TV unit, not a console table (review #15: "TV konsolu" is the Turkish name of a TV unit).
    ("TV_KONSOL", "tv_unit"), ("TVKONSOL", "tv_unit"), ("TV_CONSOLE", "tv_unit"), ("TVCONSOLE", "tv_unit"),
    ("KOSE_KOLTUK", "sofa_corner"), ("KOSEKOLTUK", "sofa_corner"), ("CORNER_SOFA", "sofa_corner"),
    ("SECTIONAL", "sofa_corner"), ("CHAISE", "chaise"), ("SEZLONG", "chaise"), ("OTTOMAN", "ottoman"),
    ("PUF", "ottoman"), ("POUF", "ottoman"), ("BENCH", "bench"), ("BANK", "bench"), ("BAR_STOOL", "bar_stool"),
    ("BARSTOOL", "bar_stool"), ("BAR_TABURE", "bar_stool"), ("OFFICE_CHAIR", "office_chair"),
    ("CALISMA_SANDALYE", "office_chair"), ("OFIS_KOLTU", "office_chair"), ("OFIS_SANDALYE", "office_chair"),
    ("CONSOLE", "console_table"), ("KONSOL", "console_table"), ("CRIB", "crib"), ("BESIK", "crib"),
    ("BUNK", "bunk_bed"), ("RANZA", "bunk_bed"), ("SIDEBOARD", "sideboard"), ("BUFE", "sideboard"),
    ("SHOE", "shoe_cabinet"), ("AYAKKABI", "shoe_cabinet"), ("VITRIN", "display_cabinet"),
    ("DISPLAY_CABINET", "display_cabinet"), ("TALL_CABINET", "tall_cabinet"), ("BOY_DOLAB", "tall_cabinet"),
    ("WALL_CABINET", "wall_cabinet"), ("UST_DOLAP", "wall_cabinet"), ("USTDOLAP", "wall_cabinet"),
)
BLOCK_GENERIC_M10: tuple[tuple[str, str], ...] = (("YATAK", "bed"), ("MASA", "table"))
# Milestone 12 (docs/milestone12.md §4.1 D7): more Turkish and English words, tried first, matched like the M10 words
# (folded: İ/ı -> I, Ş -> S, Ç -> C, ...; words of up to four letters only as a whole word of the name). The more
# specific word comes first (DISHWASHER before WASHER, ALT_DOLAP before the M7 DOLAP). A dishwasher (BULAŞIK
# makinesi) is a base unit of the counter run: a kitchen counter piece.
BLOCK_KEYWORDS_M12: tuple[tuple[str, str], ...] = (
    ("DISHWASHER", "kitchen_counter"), ("BULASIK", "kitchen_counter"), ("ALT_DOLAP", "kitchen_counter"),
    ("ALTDOLAP", "kitchen_counter"), ("WASHING_MACHINE", "washing_machine"), ("WASHER", "washing_machine"),
    ("DRYER", "washing_machine"), ("KURUTMA", "washing_machine"), ("CAMASIR", "washing_machine"),
    ("REFRIGERATOR", "fridge"), ("BUZDOLAB", "fridge"), ("FIRIN", "stove"), ("OVEN", "stove"), ("COOKER", "stove"),
    ("EVYE", "sink_kitchen"), ("VANITY", "washbasin"), ("LAVATORY", "washbasin"), ("JAKUZI", "bathtub"),
    ("BERJER", "armchair"), ("CEKYAT", "sofa"), ("GARDIROP", "wardrobe"), ("GARDROP", "wardrobe"),
    ("CLOSET", "wardrobe"), ("KOMODIN", "nightstand"), ("BOOKCASE", "bookshelf"), ("SHELF", "bookshelf"),
    ("DRESSER", "dresser"), ("ORTA_SEHPA", "table_coffee"), ("YAN_SEHPA", "side_table"), ("TELEVIZYON", "tv_unit"),
    ("TV_UNITE", "tv_unit"), ("TABURE", "bar_stool"), ("SAKSI", "potted_plant"), ("BITKI", "potted_plant"),
    ("ABAJUR", "floor_lamp"), ("LAMBADER", "floor_lamp"),
)
SEAT_KEYWORDS = ("KOLTUK",)
WHOLE_WORD_MAX = 4
_FOLD = str.maketrans({"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O",
                       "ö": "o", "Ç": "C", "ç": "c", " ": "_", "-": "_"})

# DXF block-name keywords (§2.8), English then Turkish (wenart/synthetic/blocks.py); first match wins, so the more
# specific words come first (ARMCHAIR before CHAIR, CHAIR before DINING, BEDSIDE before BED).
BLOCK_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("ARMCHAIR", "armchair"), ("CHAIR", "chair"), ("NIGHTSTAND", "nightstand"), ("BEDSIDE", "nightstand"),
    ("SOFA", "sofa"), ("DINING", "table_dining"), ("COFFEE", "table_coffee"), ("BED-DOUBLE", "bed_double"),
    ("BED_DOUBLE", "bed_double"), ("BED-SINGLE", "bed_single"), ("BED_SINGLE", "bed_single"), ("BED", "bed"),
    ("TABLE", "table"), ("WC", "toilet"), ("TOILET", "toilet"), ("BASIN", "washbasin"), ("SINK", "sink_kitchen"),
    ("WARDROBE", "wardrobe"), ("FRIDGE", "fridge"), ("STOVE", "stove"), ("HOB", "stove"), ("BATH", "bathtub"),
    ("SHOWER", "shower"), ("DESK", "desk"), ("TV", "tv_unit"), ("PLANT", "potted_plant"), ("LAMP", "floor_lamp"),
    ("KANEPE", "sofa"), ("KOLTUK", "armchair"), ("SEHPA", "table_coffee"), ("YEMEK_MASASI", "table_dining"),
    ("SANDALYE", "chair"), ("TV_UNITESI", "tv_unit"), ("KITAPLIK", "bookshelf"), ("YATAK_CIFT", "bed_double"),
    ("YATAK_TEK", "bed_single"), ("KOMIDIN", "nightstand"), ("DOLAP", "wardrobe"), ("SIFONYER", "dresser"),
    ("CALISMA_MASASI", "desk"), ("TEZGAH", "kitchen_counter"), ("BUZDOLABI", "fridge"), ("OCAK", "stove"),
    ("EVIYE", "sink_kitchen"), ("LAVABO", "washbasin"), ("KLOZET", "toilet"), ("DUS", "shower"), ("KUVET", "bathtub"),
    ("CAMASIR_MAK", "washing_machine"),
)


# --------------------------------------------------------------------------
# Size table
# --------------------------------------------------------------------------

def load_size_table() -> tuple[dict, str]:
    """(table, source): ``wenart/recognition/size_table.yaml`` (area Y) when present and readable, else the
    built-in FALLBACK_SIZE_TABLE. Accepted YAML shapes: ``{types: {t: {width: [lo, hi], depth: [lo, hi]}}}`` or the
    same without ``types``; ``width_m``/``depth_m`` keys are accepted too."""
    path = Path(__file__).resolve().parents[2] / "recognition" / "size_table.yaml"
    if path.exists():
        try:
            import yaml

            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            types = data.get("types", data) if isinstance(data, dict) else {}
            table = {}
            for name, spec in types.items():
                if not isinstance(spec, dict):
                    continue
                w = spec.get("width", spec.get("width_m"))
                d = spec.get("depth", spec.get("depth_m"))
                if isinstance(w, (list, tuple)) and isinstance(d, (list, tuple)) and len(w) == 2 and len(d) == 2:
                    table[name] = ((float(w[0]), float(w[1])), (float(d[0]), float(d[1])))
            if table:
                return table, "wenart/recognition/size_table.yaml"
        except Exception:                                  # unreadable: the built-in table, said so in the notes
            pass
    return dict(FALLBACK_SIZE_TABLE), "built-in size table (symbols.FALLBACK_SIZE_TABLE)"


def fits(table: dict, ftype: str, size) -> bool:
    """Whether a footprint (a, b) fits ``ftype``'s range in either orientation (+15 %)."""
    if ftype not in table:
        return False
    (w0, w1), (d0, d1) = table[ftype]
    a, b = size

    def inside(v, lo, hi):
        return lo / (1 + SIZE_TOLERANCE) <= v <= hi * (1 + SIZE_TOLERANCE)
    return (inside(a, w0, w1) and inside(b, d0, d1)) or (inside(a, d0, d1) and inside(b, w0, w1))


def fitting_types(table: dict, size, shape: Optional[str] = None) -> list[str]:
    """Types whose size range fits (``stair`` never: the stair rule decides); a shaped type (the corner sofa) only
    for its drawn shape (``recognition.symbols.SHAPED_TYPES``)."""
    from wenart.recognition.symbols import shape_allows
    return [t for t in table if t != "stair" and fits(table, t, size) and shape_allows(t, shape)]


# --------------------------------------------------------------------------
# Segments
# --------------------------------------------------------------------------

@dataclass
class Seg:
    id: str                    # stroke id, "#k" appended for a polyline piece
    stroke: Stroke
    pts: list[tuple[float, float]]
    geom: object
    curve: bool                # an arc / curve kept whole
    dot: bool = False

    @property
    def length(self) -> float:
        return self.geom.length


def _segments(strokes: list[Stroke], drop: set) -> list[Seg]:
    out = []
    for st in strokes:
        if st.id in drop or not st.pts:
            continue
        pts = list(st.pts)
        if len(set(pts)) == 1:
            out.append(Seg(st.id, st, [pts[0]], Point(pts[0]), False, dot=True))
            continue
        curved = st.kind in ("arc", "circle", "curve") or st.arc is not None
        if curved:
            ring = pts + [pts[0]] if st.closed and len(pts) > 2 else pts
            out.append(Seg(st.id, st, ring, LineString(ring), True))
            continue
        if st.closed and len(pts) > 2:
            pts = pts + [pts[0]]
        if len(pts) == 2:
            out.append(Seg(st.id, st, pts, LineString(pts), False))
            continue
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            if a == b:
                continue
            out.append(Seg(f"{st.id}#{k}", st, [a, b], LineString([a, b]), False))
    return out


def _dimension_ids(dims) -> set[str]:
    """Stroke ids of the dimension candidates: G1's ``DimCandidate.stroke_ids`` (line pieces and end marks) and
    ``extension_ids`` (attributes or dict keys; strokes or ids)."""
    out: set[str] = set()
    for d in dims or []:
        for key in ("stroke_ids", "extension_ids"):
            ids = d.get(key) if isinstance(d, dict) else getattr(d, key, None)
            for x in ids or []:
                out.add(x.id if isinstance(x, Stroke) else str(x))
    return out


def _stroke_geom(st: Stroke):
    """The whole stroke as one geometry (closed paths closed)."""
    pts = list(st.pts)
    if len(set(pts)) == 1:
        return Point(pts[0])
    if st.closed and len(pts) > 2:
        pts.append(pts[0])
    return LineString(pts)


def _text_boxes(texts) -> list:
    boxes = []
    for t in texts or []:
        x0, y0, x1, y1 = t.box
        gx, gy = (x1 - x0) * TEXT_GROW / 2.0, (y1 - y0) * TEXT_GROW / 2.0
        boxes.append(sbox(x0 - gx, y0 - gy, x1 + gx, y1 + gy))
    return boxes


def _as_polygon(outline):
    if outline is None:
        return None
    if isinstance(outline, (Polygon,)) or hasattr(outline, "geom_type"):
        return outline
    return Polygon(outline)


def _wall_geometry(walls: list, openings: list, site_walls: list):
    polys = [TP.wall_polygon(w) for w in list(walls) + list(site_walls)]
    all_walls = list(walls) + list(site_walls)
    for o in openings or []:
        if getattr(o, "virtual", False):
            continue
        p = TP.opening_polygon(o, all_walls)
        if p is not None:
            polys.append(p)
    return unary_union(polys) if polys else Polygon()


def _drop_outline(segs: list[Seg], wall_geom) -> tuple[list[Seg], int]:
    """Segments with >= 90 % of their length within 20 mm of the bridged wall geometry are wall outline (§2.8).
    Segments with >= 50 % of their length inside the wall or opening material itself are wall drawing too (real01's
    window jamb line runs from the outer wall face to the bed's head edge: 89 % near the wall, 82 % inside it)."""
    if wall_geom.is_empty or not segs:
        return segs, 0
    near = wall_geom.buffer(OUTLINE_NEAR_M, join_style=2)
    shapely.prepare(near)
    shapely.prepare(wall_geom)
    geoms = np.array([s.geom for s in segs], dtype=object)
    inside = shapely.within(geoms, near)
    disjoint = shapely.disjoint(geoms, near)
    keep = []
    dropped = 0
    for i, s in enumerate(segs):
        if inside[i]:
            dropped += 1
            continue
        if disjoint[i] or s.dot or s.length <= 0:
            keep.append(s)
            continue
        share = s.geom.intersection(near).length / s.length
        in_wall = s.geom.intersection(wall_geom).length / s.length
        if share >= OUTLINE_SHARE or in_wall >= WALL_MATERIAL_SHARE:
            dropped += 1
        else:
            keep.append(s)
    return keep, dropped


# --------------------------------------------------------------------------
# Clusters
# --------------------------------------------------------------------------

def _union_find(geoms: list, dist: float) -> list[list[int]]:
    if not geoms:
        return []
    tree = STRtree(geoms)
    left, right = tree.query(np.array(geoms, dtype=object), predicate="dwithin", distance=dist)
    parent = list(range(len(geoms)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in zip(left.tolist(), right.tolist()):
        if i != j:
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
    groups: dict[int, list[int]] = {}
    for i in range(len(geoms)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


@dataclass
class Cluster:
    segs: list[Seg]
    note: list = field(default_factory=list)

    @property
    def geom(self):
        return unary_union([s.geom for s in self.segs])

    def bounds(self, theta: float = 0.0) -> tuple[float, float, float, float]:
        """Bounding box on the page axes, or in the plan's aligned frame (rotated by -``theta``) when ``theta`` is
        not 0: on a plan drawn at an angle the page-axis box of a rotated piece covers its neighbours (§2.8)."""
        pts = [p for s in self.segs for p in s.pts]
        if theta % 360.0:
            to_f, _ = _frame(theta)
            pts = [to_f(p) for p in pts]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def size(self, theta: float = 0.0) -> tuple[float, float]:
        b = self.bounds(theta)
        return (b[2] - b[0], b[3] - b[1])

    def stroke_ids(self) -> list[str]:
        return sorted({s.stroke.id for s in self.segs}, key=_id_key)


def _id_key(sid: str):
    """Numeric ids in numeric order; the id itself breaks ties (DXF ids such as ``INSERT:2DE26/3`` all had key
    ``(head, 0)``, so their order followed Python's per-process string hashing and varied from run to run)."""
    head, _, tail = sid.partition(":")
    try:
        return (head, int(tail.split("#")[0]), sid)
    except ValueError:
        return (head, 0, sid)


def clusters_of(segs: list[Seg], dist: float = CLUSTER_M) -> list[Cluster]:
    return [Cluster([segs[i] for i in idx]) for idx in _union_find([s.geom for s in segs], dist)]


def chain_clusters(segs: list[Seg], dist: float = RECLUSTER_M) -> list[Cluster]:
    """Clusters at ``dist`` that also keep strokes joined end to end (within 5 mm) together: the 2 mm re-cluster of
    the composite split must separate touching pieces without breaking a shape whose joints carry the 1-3 mm gaps
    of a 0.12 pt coordinate grid."""
    if not segs:
        return []
    groups = _union_find([s.geom for s in segs], dist)
    parent = list(range(len(segs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for idx in groups:
        for k in idx[1:]:
            union(idx[0], k)
    ends, _ = _end_nodes(segs)
    first: dict = {}
    for i, e in enumerate(ends):
        if e is None:
            continue
        for n in e:
            if n in first:
                union(i, first[n])
            else:
                first[n] = i
    out: dict = {}
    for i in range(len(segs)):
        out.setdefault(find(i), []).append(segs[i])
    return [Cluster(v) for v in out.values()]


# --------------------------------------------------------------------------
# Closed contours (endpoint chains) and the containment merge
# --------------------------------------------------------------------------

def _end_nodes(segs: list[Seg], tol: float = CHAIN_M) -> tuple[list, dict]:
    """Stroke ends merged within ``tol`` (5 mm: a CAD PDF on a 0.12 pt grid leaves 1-3 mm between joined ends).
    Returns ``(ends, coords)``: per segment ``(node a, node b)`` or None, and node -> mean coordinate."""
    pts, owner = [], []
    for i, s in enumerate(segs):
        if s.dot or len(s.pts) < 2:
            continue
        pts.extend([s.pts[0], s.pts[-1]])
        owner.extend([i, i])
    parent = list(range(len(pts)))

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    grid: dict = {}
    for k, p in enumerate(pts):
        cx, cy = int(math.floor(p[0] / tol)), int(math.floor(p[1] / tol))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((cx + dx, cy + dy), ()):
                    if math.dist(p, pts[j]) <= tol:
                        ra, rb = find(k), find(j)
                        if ra != rb:
                            parent[ra] = rb
        grid.setdefault((cx, cy), []).append(k)
    members: dict = {}
    for k in range(len(pts)):
        members.setdefault(find(k), []).append(k)
    coords = {r: (sum(pts[k][0] for k in ks) / len(ks), sum(pts[k][1] for k in ks) / len(ks))
              for r, ks in members.items()}
    ends: list = [None] * len(segs)
    for k in range(0, len(pts), 2):
        ends[owner[k]] = (find(k), find(k + 1))
    return ends, coords


def contours(segs: list[Seg]) -> list[tuple[Polygon, list[int]]]:
    """Closed contours of a stroke set: strokes joined end to end (within 5 mm) form chains; the faces of each
    chain component, polygonised and filled, are its contours. Strokes that only touch another stroke's middle (a
    blanket line ending on a bed outline, a nightstand edge lying along the bed's edge) are not joined, so touching
    pieces keep separate contours. Returns ``[(polygon, indices of the ring strokes)]``."""
    ends, coords = _end_nodes(segs)
    parent: dict = {}

    def find(k):
        while parent.setdefault(k, k) != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for e in ends:
        if e is not None:
            ra, rb = find(e[0]), find(e[1])
            if ra != rb:
                parent[ra] = rb
    comps: dict = {}
    for i, e in enumerate(ends):
        if e is not None:
            comps.setdefault(find(e[0]), []).append(i)
    out = []
    for idx in comps.values():
        if len(idx) == 1 and not segs[idx[0]].stroke.closed:
            continue
        lines = []
        for i in idx:
            pts = list(segs[i].pts)
            pts[0], pts[-1] = coords[ends[i][0]], coords[ends[i][1]]
            if len(set(pts)) >= 2:
                lines.append(LineString(pts))
        if not lines:
            continue
        faces = [p for p in polygonize(unary_union(lines)) if p.area > 1e-6]
        if not faces:
            continue
        filled = unary_union([Polygon(f.exterior) for f in faces])
        for poly in getattr(filled, "geoms", [filled]):
            ring = poly.exterior.buffer(CHAIN_M)
            members = [i for i in idx if ring.contains(segs[i].geom)]
            out.append((Polygon(poly.exterior), members or idx))
    return out


def _rect_sides(geom) -> tuple[float, float]:
    rect = geom.minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        b = geom.bounds
        return (b[2] - b[0], b[3] - b[1])
    c = list(rect.exterior.coords)
    return (math.dist(c[0], c[1]), math.dist(c[1], c[2]))


def _closed_outline(cl: Cluster, theta: float = 0.0) -> Optional[Polygon]:
    """The cluster's own closed outline: a contour covering >= 80 % of the cluster's bbox area (aligned frame of
    ``theta``), else the filled faces of all its strokes noded together when they do (Milestone 10, real02: an
    armchair whose arms are drawn as open lines ending on the body's sides closes only at those T-junctions; its body
    alone covers 79.9-80.0 % of the box, so mirrored copies fell either side of the share), else None."""
    b = cl.bounds(theta)
    area = max((b[2] - b[0]) * (b[3] - b[1]), 1e-12)
    best = None
    for poly, _ in contours(cl.segs):
        if poly.area >= 0.8 * area and (best is None or poly.area > best.area):
            best = poly
    if best is None:
        lines = [s.geom for s in cl.segs if not s.dot]
        faces = [p for p in polygonize(unary_union(lines)) if p.area > 1e-6] if lines else []
        if faces:
            filled = unary_union([Polygon(f.exterior) for f in faces])
            top = max(getattr(filled, "geoms", [filled]), key=lambda g: g.area)
            if top.area >= 0.8 * area:
                best = Polygon(top.exterior)
    return best


def _merge_contained(clusters: list[Cluster], table: dict, theta: float = 0.0) -> list[Cluster]:
    """A cluster whose bbox lies >= 80 % inside another merges into it, unless it is a closed polygon with both sides
    >= 0.3 m that fits a size-table type and is not an inner outline of the container (a closed contour of the
    container encloses it and it covers >= 40 % of that contour: a bed's double outline, a table's inlay).

    The boxes are taken in the plan's aligned frame (``theta``, the dominant wall angle), like the walls and the
    footprints: on a plan drawn at an angle a page-axis box of a rotated stair covers the chairs next door."""
    boxes = {i: clusters[i].bounds(theta) for i in range(len(clusters))}
    order = sorted(range(len(clusters)), key=lambda i: -_bbox_area(boxes[i]))
    alive = {i: clusters[i] for i in order}
    container_contours: dict[int, list] = {}
    for pos, i in enumerate(order):
        if i not in alive:
            continue
        bi = boxes[i]
        for j in order[pos + 1:]:
            if j not in alive:
                continue
            if _inside_share(boxes[j], bi) < CONTAIN_SHARE:
                continue
            if _keeps_own_piece(alive[j], alive[i], table, container_contours, i, theta):
                continue
            alive[i].segs.extend(alive[j].segs)
            del alive[j]
            container_contours.pop(i, None)
            bi = boxes[i] = alive[i].bounds(theta)
    return list(alive.values())


def _keeps_own_piece(inner: Cluster, outer: Cluster, table: dict, cache: dict, key, theta: float = 0.0) -> bool:
    """The containment exception of §2.8 (a sink or hob in a counter stays its own piece), limited to shapes that
    are not drawn details of the container: when a closed contour of the container encloses the shape, the shape is
    the container's inner outline (>= 40 % of its area: a bed's double outline, a table's inlay) or a detail on it
    (spanning < 60 % of its short side: pillows on a bed); a sink spans most of a counter's depth."""
    w, h = inner.size(theta)
    if min(w, h) < CONTAIN_KEEP_SIDE_M:
        return False
    poly = _closed_outline(inner, theta)
    if poly is None or not fitting_types(table, _rect_sides(poly)):
        return False
    if key not in cache:
        cache[key] = [p for p, _ in contours(outer.segs)]
    for c in cache[key]:
        if not c.buffer(0.005).contains(poly):
            continue
        if poly.area >= 0.4 * c.area:
            return False
        rect = c.minimum_rotated_rectangle
        if rect.geom_type != "Polygon":
            return False
        q = list(rect.exterior.coords)
        e1 = (q[1][0] - q[0][0], q[1][1] - q[0][1])
        e2 = (q[2][0] - q[1][0], q[2][1] - q[1][1])
        short = e1 if math.hypot(*e1) <= math.hypot(*e2) else e2
        n = math.hypot(*short) or 1.0
        u = (short[0] / n, short[1] / n)
        proj = [p[0] * u[0] + p[1] * u[1] for p in poly.exterior.coords]
        if max(proj) - min(proj) < 0.6 * n:
            return False
    return True


def _bbox_area(b) -> float:
    return max(b[2] - b[0], 0.0) * max(b[3] - b[1], 0.0)


def _inside_share(inner, outer) -> float:
    """Share of bbox ``inner`` lying inside bbox ``outer`` (a degenerate box counts by its extent)."""
    ix0, iy0 = max(inner[0], outer[0]), max(inner[1], outer[1])
    ix1, iy1 = min(inner[2], outer[2]), min(inner[3], outer[3])
    if ix1 < ix0 or iy1 < iy0:
        return 0.0
    area = _bbox_area(inner)
    if area <= 1e-12:
        span = max(inner[2] - inner[0], inner[3] - inner[1])
        inside = max(ix1 - ix0, iy1 - iy0)
        return 1.0 if span <= 1e-12 else inside / span
    return _bbox_area((ix0, iy0, ix1, iy1)) / area


# --------------------------------------------------------------------------
# Composite split
# --------------------------------------------------------------------------

def top_contours(cl: Cluster) -> list[tuple[Polygon, list[int]]]:
    """Top-level closed contours >= 0.20 m on both sides: nested ones dropped, ones overlapping >= 15 % of the
    smaller merged, and equal-sized contours that touch each other (sofa cushions, wardrobe doors, cabinet fronts)
    merged into one object."""
    cands = [(p, m) for p, m in contours(cl.segs) if min(_rect_sides(p)) >= CONTOUR_MIN_M]
    cands.sort(key=lambda pm: -pm[0].area)
    tops: list[list] = []
    for poly, members in cands:
        placed = False
        for t in tops:
            inter = t[0].intersection(poly).area
            if inter >= 0.85 * poly.area:
                placed = True                       # nested: part of the bigger one
                break
            if inter >= CONTOUR_OVERLAP * min(poly.area, t[0].area):
                t[0] = t[0].union(poly)
                t[1] = t[1] + members
                placed = True
                break
        if not placed:
            tops.append([poly, list(members), [poly]])
    # Equal neighbours are parts of one piece.
    merged = True
    while merged:
        merged = False
        for a in range(len(tops)):
            for b in range(a + 1, len(tops)):
                pa, pb = tops[a][2][0], tops[b][2][0]
                if tops[a][0].distance(tops[b][0]) > 0.005:
                    continue
                sa, sb = sorted(_rect_sides(pa)), sorted(_rect_sides(pb))
                if all(abs(x - y) <= 0.15 * max(x, y) for x, y in zip(sa, sb)):
                    tops[a][0] = tops[a][0].union(tops[b][0])
                    tops[a][1] += tops[b][1]
                    tops[a][2] += tops[b][2]
                    del tops[b]
                    merged = True
                    break
            if merged:
                break
    return [(t[0], t[1]) for t in tops]


def _block_keyword(name: str) -> Optional[str]:
    # Milestone 12: the composite split groups strokes by the instances the M7-M11 words name, so the parts (and the
    # questions and answers) of earlier rounds stay as they were; the M12 words type the parts.
    return keyword_type(name, extended=False)


def keyword_type(name: str, extended: bool = True) -> Optional[str]:
    """The type word of a block name: the Milestone 12 words (``extended``) and the Milestone 10 words first (folded
    name, whole words for short ones), then the M7 keywords (substring of the upper-case or the folded name: DUŞ is
    DUS), then the generic M10 words; None when no word matches. Generic words (``bed``, ``table``, ``seat``) are
    resolved by ``block_type``."""
    folded = (name or "").translate(_FOLD).upper()
    words = set(folded.replace(".", "_").split("_"))

    def match(table):
        for key, ftype in table:
            if (key in words) if len(key) <= WHOLE_WORD_MAX else (key in folded):
                return key, ftype
        return None, None

    key, ftype = match(BLOCK_KEYWORDS_M12) if extended else (None, None)
    if ftype is not None:
        return ftype
    key, ftype = match(BLOCK_KEYWORDS_M10)
    if ftype is not None:
        return ftype
    upper = (name or "").upper()
    hit = next(((key, ftype) for key, ftype in BLOCK_KEYWORDS if key in upper or key in folded), None)
    if hit is not None:
        return "seat" if hit[0] in SEAT_KEYWORDS else hit[1]
    return match(BLOCK_GENERIC_M10)[1]


def block_instance(st: Stroke) -> tuple[str, bool]:
    """(instance key, named) of a DXF block stroke: the INSERT instance of the innermost block in its chain whose
    name holds a furniture keyword (``INSERT:FF/3`` for a CHAIR nested in DINING-6, ``INSERT:FF`` for the table
    lines of DINING-6 or for a pillow block inside a BED block), else the outermost instance; ``named`` tells
    whether a keyword was found. Ids that do not follow ``dxf_generic``'s ``INSERT:<h>/<k>/...`` form group by the
    block chain."""
    names = (st.block or "").split("/")
    parts = st.id.split("/")
    keyed = [i for i, name in enumerate(names) if _block_keyword(name) is not None]
    if len(parts) < len(names) + 1:
        return f"{st.block}|", bool(keyed)
    i = keyed[-1] if keyed else 0
    return f"{'/'.join(names[:i + 1])}|{'/'.join(parts[:i + 1])}", bool(keyed)


def split_composite(cl: Cluster, table: dict) -> list[tuple[Cluster, int]]:
    """Pieces of a cluster: ``[(cluster, n)]`` where ``n`` > 1 marks an unsplittable composite of n parts.

    A cluster drawn entirely by DXF block content splits by block instance first (one piece per INSERT of a
    furniture-named block: a WC's tank and bowl stay one piece, DINING-6 gives its table and each CHAIR); instances
    whose chain names no furniture go through the geometric split."""
    if cl.segs and all(s.stroke.block for s in cl.segs):
        groups: dict[str, list[Seg]] = {}
        named: dict[str, bool] = {}
        for s in cl.segs:
            key, has_name = block_instance(s.stroke)
            groups.setdefault(key, []).append(s)
            named[key] = has_name
        out: list[tuple[Cluster, int]] = []
        for key in sorted(groups):
            sub = Cluster(groups[key])
            out.extend([(sub, 1)] if named[key] else _split_geometric(sub, table))
        return out
    return _split_geometric(cl, table)


def _split_geometric(cl: Cluster, table: dict) -> list[tuple[Cluster, int]]:
    tops = top_contours(cl)
    corners, _ = min_rect([p for s in cl.segs for p in s.pts])
    size = (math.dist(corners[0], corners[1]), math.dist(corners[1], corners[2]))
    fits_any = bool(fitting_types(table, size))
    if len(tops) < 2 and fits_any:
        return [(cl, 1)]
    if not tops:
        return [(cl, _parts_count(cl))]
    ring_ids = {i for _, members in tops for i in members}
    pieces = [Cluster([cl.segs[i] for i in members]) for _, members in tops]
    polys = [p for p, _ in tops]
    rest = [s for i, s in enumerate(cl.segs) if i not in ring_ids]
    loose: list[Cluster] = []
    for sub in chain_clusters(rest, RECLUSTER_M):
        g = sub.geom
        home = None
        for k, p in enumerate(polys):
            if g.length > 0 and g.intersection(p.buffer(0.003)).length >= 0.9 * g.length:
                home = k
                break
            if g.length == 0 and p.buffer(0.003).contains(g):
                home = k
                break
        if home is None:
            dists = [p.exterior.distance(g) for p in polys]
            k = int(np.argmin(dists))
            if dists[k] <= ATTACH_M:
                home = k
        if home is None:
            loose.append(sub)
        else:
            pieces[home].segs.extend(sub.segs)
    # Loose parts next to a grown piece (a chair back beyond its connector) join that piece.
    changed = True
    while loose and changed:
        changed = False
        geoms = [p.geom for p in pieces]
        for sub in list(loose):
            dists = [g.distance(sub.geom) for g in geoms]
            k = int(np.argmin(dists))
            if dists[k] <= ATTACH_M:
                pieces[k].segs.extend(sub.segs)
                loose.remove(sub)
                changed = True
    out = [(p, 1) for p in pieces]
    if loose:
        for sub in clusters_of([s for c in loose for s in c.segs], CLUSTER_M):
            out.append((sub, 1))
    if len(out) == 1 and not fits_any:
        return [(cl, _parts_count(cl))]
    return out


def _parts_count(cl: Cluster) -> int:
    return max(1, len(top_contours(cl)), len(clusters_of(cl.segs, RECLUSTER_M)) if len(cl.segs) < 50 else 1)


def reclose(cl: Cluster, pool: list[Seg], taken: set, theta: float = 0.0) -> int:
    """Give a cluster back the near-wall segments that close its contours.

    The outline rule drops every segment within 20 mm of a wall face, which also removes the back edge of a bed or a
    nightstand standing against the wall (real01: 6-9 mm off the face). A chain of dropped segments that lies inside
    the cluster's bbox (grown 20 mm) and joins two ends of the cluster's strokes is part of the piece, not wall
    outline. Returns the number of segments added. The bbox is taken in the aligned frame of ``theta``."""
    b = cl.bounds(theta)
    grow = OUTLINE_NEAR_M
    box_ = (b[0] - grow, b[1] - grow, b[2] + grow, b[3] + grow)
    to_f = _frame(theta)[0] if theta % 360.0 else (lambda p: p)
    near = [s for s in pool if id(s) not in taken and all(box_[0] <= q[0] <= box_[2] and box_[1] <= q[1] <= box_[3]
                                                          for q in map(to_f, s.pts))]
    if not near:
        return 0
    allsegs = cl.segs + near
    ends, _ = _end_nodes(allsegs)
    n0 = len(cl.segs)
    anchored = {n for e in ends[:n0] if e is not None for n in e}
    parent: dict = {}

    def find(k):
        while parent.setdefault(k, k) != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for e in ends[n0:]:
        if e is not None:
            ra, rb = find(e[0]), find(e[1])
            if ra != rb:
                parent[ra] = rb
    comp_segs: dict = {}
    comp_nodes: dict = {}
    for k, e in enumerate(ends[n0:]):
        if e is None:
            continue
        r = find(e[0])
        comp_segs.setdefault(r, []).append(near[k])
        comp_nodes.setdefault(r, set()).update(e)
    added = 0
    for r, members in comp_segs.items():
        if len(comp_nodes[r] & anchored) >= 2:
            for s in members:
                cl.segs.append(s)
                taken.add(id(s))
                added += 1
    return added


# --------------------------------------------------------------------------
# Deterministic types: stair and kitchen counter
# --------------------------------------------------------------------------

def _frame(theta: float):
    """(page -> aligned frame, aligned frame -> page) point maps for the plan's dominant angle ``theta``."""
    t = math.radians(theta)
    c, s = math.cos(t), math.sin(t)

    def to_f(p):
        return (p[0] * c + p[1] * s, -p[0] * s + p[1] * c)

    def from_f(p):
        return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
    return to_f, from_f


def _straight(segs: list[Seg], to_f) -> list[tuple[str, float, float, float, Seg]]:
    """Axis segments in the aligned frame: (axis, offset, lo, hi, seg); axis "h" lies along x."""
    out = []
    for s in segs:
        if s.curve or s.dot:
            continue
        a, b = to_f(s.pts[0]), to_f(s.pts[-1])
        if abs(a[1] - b[1]) <= 0.003 and abs(a[0] - b[0]) > 0.003:
            out.append(("h", (a[1] + b[1]) / 2, min(a[0], b[0]), max(a[0], b[0]), s))
        elif abs(a[0] - b[0]) <= 0.003 and abs(a[1] - b[1]) > 0.003:
            out.append(("v", (a[0] + b[0]) / 2, min(a[1], b[1]), max(a[1], b[1]), s))
    return out


def stair_rule(cl: Cluster, theta: float) -> Optional[dict]:
    """Flights of evenly spaced tread lines (§2.8): ``{"flights", "landing", "bbox_f", "segs"}`` in the aligned
    frame, or None."""
    to_f, from_f = _frame(theta)
    axis_segs = _straight(cl.segs, to_f)
    best = None
    for axis in ("h", "v"):
        treads = _merge_collinear([x for x in axis_segs if x[0] == axis])
        if len(treads) < STAIR_MIN_TREADS:
            continue
        others = [x for x in axis_segs if x[0] != axis]
        # A perpendicular divider crossing >= 80 % of the treads splits them.
        cuts = []
        for o in others:
            # treads: (offset, lo, hi, members); o: (axis, offset, lo, hi, seg)
            crossing = [t for t in treads if t[1] + 0.01 < o[1] < t[2] - 0.01 and o[2] - 0.005 <= t[0] <= o[3] + 0.005]
            if len(crossing) >= STAIR_DIVIDER_SHARE * len(treads):
                cuts.append(o[1])
        cuts = sorted(set(round(c, 3) for c in cuts))
        pieces = []
        for off, lo, hi, members in treads:
            bounds = [lo] + [c for c in cuts if lo + 0.01 < c < hi - 0.01] + [hi]
            for u, v in zip(bounds, bounds[1:]):
                pieces.append((off, u, v, members))
        flights = []
        sides: dict = {}
        for off, u, v, members in pieces:
            key = (round(u / 0.01), round(v / 0.01))
            sides.setdefault(key, []).append((off, u, v, members))
        for key, group in sides.items():
            flight = _flight(sorted(group, key=lambda g: g[0]))
            if flight:
                flights.append(flight)
        if flights and (best is None or sum(f["lines"] for f in flights) > sum(f["lines"] for f in best[1])):
            best = (axis, flights, cuts)
    if best is None:
        best = _loose_flights(axis_segs)
    if best is None:
        return None
    axis, flights, cuts = best
    xs = [p[0] for s in cl.segs for p in map(to_f, s.pts)]
    ys = [p[1] for s in cl.segs for p in map(to_f, s.pts)]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    lo_off = min(f["offsets"][0] for f in flights)
    hi_off = max(f["offsets"][-1] for f in flights)
    lo_end, hi_end = (bbox[1], bbox[3]) if axis == "h" else (bbox[0], bbox[2])
    landing = None
    if hi_end - hi_off >= 0.3 and hi_end - hi_off >= lo_off - lo_end:
        landing = (hi_off, hi_end)
    elif lo_off - lo_end >= 0.3:
        landing = (lo_end, lo_off)

    def pt(along_axis_pos, off):
        return from_f((along_axis_pos, off)) if axis == "h" else from_f((off, along_axis_pos))

    out_flights = []
    for f in sorted(flights, key=lambda f: f["u"]):
        mid = (f["u"] + f["v"]) / 2.0
        out_flights.append({"start": _r(pt(mid, f["offsets"][0])), "end": _r(pt(mid, f["offsets"][-1])),
                            "width": round(f["v"] - f["u"], 4), "lines": f["lines"],
                            "spacing": round(f["spacing"], 4)})
    land = None
    if landing:
        u = min(f["u"] for f in flights)
        v = max(f["v"] for f in flights)
        corners = [pt(u, landing[0]), pt(v, landing[0]), pt(v, landing[1]), pt(u, landing[1])]
        land = {"polygon": [list(_r(c)) for c in corners], "depth": round(landing[1] - landing[0], 4)}
    used = {id(s) for f in flights for s in f["segs"]}
    return {"flights": out_flights, "landing": land, "axis": axis, "bbox_f": bbox, "theta": theta,
            "tread_segs": used, "dividers": cuts}


def _loose_flights(axis_segs) -> Optional[tuple[str, list, list]]:
    """The stair rule's fallback for treads drawn as nosing strips and flights cut by a break line (real02's U stairs
    with winders: every tread is two lines 50 mm apart, the treads beside the break line are shorter, the two flights
    are not crossed by one divider line). Per axis: tread lines >= 0.4 m, nosing pairs (<= 60 mm apart, overlapping)
    as one tread, the treads grouped by overlapping extents (>= 80 % of the shorter) into flight sides, and in each
    side the longest run of >= 5 evenly spaced treads (0.20-0.35 m +- 10 %) is a flight. A grid (the same on the
    other axis: floor tiles) is no stair. Returns ``(axis, flights, [])`` like the strict rule, or None."""
    found: dict = {}
    for axis in ("h", "v"):
        lines = [m for m in _merge_collinear([x for x in axis_segs if x[0] == axis])
                 if m[2] - m[1] >= LOOSE_TREAD_M]
        treads: list[list] = []
        for off, lo, hi, members in sorted(lines, key=lambda m: m[0]):
            last = treads[-1] if treads else None
            if last is not None and off - last[4] <= NOSING_M and _overlap(last[1], last[2], lo, hi) >= \
                    LOOSE_OVERLAP * min(last[2] - last[1], hi - lo):
                last[0] = (last[0] + off) / 2.0
                last[1], last[2], last[4] = min(last[1], lo), max(last[2], hi), off
                last[3] = last[3] + list(members)
                continue
            treads.append([off, lo, hi, list(members), off])
        sides: list[list] = []
        for tr in treads:
            for side in sides:
                ref = side[0]
                if _overlap(ref[1], ref[2], tr[1], tr[2]) >= LOOSE_OVERLAP * min(ref[2] - ref[1], tr[2] - tr[1]):
                    side.append(tr)
                    break
            else:
                sides.append([tr])
        flights = []
        for side in sides:
            run = _even_run(sorted(side, key=lambda tr: tr[0]))
            if run:
                los, his = sorted(tr[1] for tr in run), sorted(tr[2] for tr in run)
                flights.append({"offsets": [tr[0] for tr in run], "u": los[len(los) // 2], "v": his[len(his) // 2],
                                "lines": len(run), "spacing": statistics.median(
                                    [b[0] - a[0] for a, b in zip(run, run[1:])]),
                                "segs": [s for tr in run for s in tr[3]]})
        found[axis] = flights
    for axis, other in (("h", "v"), ("v", "h")):
        if found[axis] and not found[other]:
            return axis, found[axis], []
    return None


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return min(a1, b1) - max(a0, b0)


def _even_run(treads: list) -> Optional[list]:
    """The longest run of >= STAIR_MIN_TREADS treads with steps 0.20-0.35 m (+- 10 %) equal within 10 %."""
    lo_step, hi_step = STAIR_STEP_M[0] * (1 - STAIR_STEP_TOL), STAIR_STEP_M[1] * (1 + STAIR_STEP_TOL)
    best: list = []
    for i in range(len(treads)):
        run = [treads[i]]
        for tr in treads[i + 1:]:
            step = tr[0] - run[-1][0]
            if step < lo_step:
                continue
            first = run[1][0] - run[0][0] if len(run) > 1 else step
            if step > hi_step or abs(step - first) > STAIR_STEP_TOL * first:
                break
            run.append(tr)
        if len(run) > len(best):
            best = run
    return best if len(best) >= STAIR_MIN_TREADS else None


def _r(p) -> tuple[float, float]:
    return (round(p[0], 4), round(p[1], 4))


def _merge_collinear(items) -> list[tuple[float, float, float, list]]:
    """Strokes on one line (within 5 mm) with overlapping or touching extents become one (union extent)."""
    out: list[list] = []
    for axis, off, lo, hi, s in sorted(items, key=lambda x: (x[1], x[2])):
        for m in out:
            if abs(m[0] - off) <= STAIR_MERGE_M and lo <= m[2] + STAIR_MERGE_M and hi >= m[1] - STAIR_MERGE_M:
                m[1], m[2] = min(m[1], lo), max(m[2], hi)
                m[3].append(s)
                break
        else:
            out.append([off, lo, hi, [s]])
    return [tuple(m) for m in out]


def _flight(group) -> Optional[dict]:
    """>= 5 equal, evenly spaced (0.20-0.35 m +- 10 %) tread segments."""
    if len(group) < STAIR_MIN_TREADS:
        return None
    offs = [g[0] for g in group]
    steps = [b - a for a, b in zip(offs, offs[1:])]
    if not steps:
        return None
    med = statistics.median(steps)
    if not STAIR_STEP_M[0] * (1 - STAIR_STEP_TOL) <= med <= STAIR_STEP_M[1] * (1 + STAIR_STEP_TOL):
        return None
    if any(abs(st - med) > STAIR_STEP_TOL * med for st in steps):
        return None
    return {"offsets": offs, "u": group[0][1], "v": group[0][2], "lines": len(group), "spacing": med,
            "segs": [s for g in group for s in g[3]]}


def group_treads(clusters: list[Cluster], theta: float, wall_geom=None, notes: Optional[list] = None
                 ) -> list[Cluster]:
    """Isolated tread lines become one stair cluster (§2.8).

    Treads drawn from wall face to wall face lose their side strokes with the wall outline, so every tread is a
    cluster of its own and the stair rule never sees >= 5 of them together. Clusters that are one straight line
    along a frame axis (``theta``), 0.5-3.0 m long, with both ends within 10 mm of each other's, evenly spaced
    0.20-0.35 m apart (+-10 %, >= 5 lines: the flight test of the stair rule) and with no wall in the area between the
    first and the last line, are merged into one cluster - kept only when the stair rule then finds its flight.
    Returns the new cluster list; ``notes`` receives a line per stair candidate."""
    to_f, from_f = _frame(theta)
    lines: dict[str, list] = {"h": [], "v": []}
    for i, cl in enumerate(clusters):
        if not cl.segs or any(s.curve or s.dot for s in cl.segs):
            continue
        st = _straight(cl.segs, to_f)
        if len(st) != len(cl.segs) or len({x[0] for x in st}) != 1:
            continue
        merged = _merge_collinear(st)
        if len(merged) != 1:
            continue
        off, lo, hi, _ = merged[0]
        if TREAD_LENGTH_M[0] <= hi - lo <= TREAD_LENGTH_M[1]:
            lines[st[0][0]].append((off, lo, hi, [i]))
    step_lo = STAIR_STEP_M[0] * (1 - STAIR_STEP_TOL)
    step_hi = STAIR_STEP_M[1] * (1 + STAIR_STEP_TOL)
    groups: list[list[int]] = []
    for axis, items in lines.items():
        bins: list[list] = []
        for it in sorted(items, key=lambda x: (x[1], x[2], x[0])):
            for b in bins:
                if abs(b[0][1] - it[1]) <= TREAD_ALIGN_M and abs(b[0][2] - it[2]) <= TREAD_ALIGN_M:
                    b.append(it)
                    break
            else:
                bins.append([it])
        for b in bins:
            b.sort(key=lambda x: x[0])
            rows: list = []                                  # a line drawn twice is one tread
            for it in b:
                if rows and it[0] - rows[-1][0] <= STAIR_MERGE_M:
                    rows[-1] = (rows[-1][0], rows[-1][1], rows[-1][2], rows[-1][3] + it[3])
                else:
                    rows.append(it)
            run: list = []
            for it in rows + [None]:
                if it is not None and run and step_lo <= it[0] - run[-1][0] <= step_hi:
                    run.append(it)
                    continue
                if len(run) >= STAIR_MIN_TREADS and _flight(run) is not None \
                        and not _wall_between(run, axis, from_f, wall_geom):
                    groups.append([k for r in run for k in r[3]])
                run = [it] if it is not None else []
    if not groups:
        return clusters
    out = list(clusters)
    gone: set = set()
    for idx in groups:
        merged = Cluster([s for k in idx for s in clusters[k].segs])
        if stair_rule(merged, theta) is None:
            continue
        merged.note.append(f"{len(idx)} isolated tread lines grouped")
        out.append(merged)
        gone.update(idx)
        if notes is not None:
            b = merged.bounds()
            notes.append(f"{len(idx)} isolated, evenly spaced tread lines at ({(b[0] + b[2]) / 2:.2f}, "
                         f"{(b[1] + b[3]) / 2:.2f}) grouped as a stair candidate")
    return [cl for k, cl in enumerate(out) if k not in gone]


def _wall_between(run, axis: str, from_f, wall_geom) -> bool:
    """True when a wall (or an opening rectangle) lies in the area spanned by the tread lines ``run``, shrunk by 30
    mm: lines on both sides of a wall are no flight."""
    if wall_geom is None or wall_geom.is_empty:
        return False
    lo = max(r[1] for r in run) + TREAD_WALL_M
    hi = min(r[2] for r in run) - TREAD_WALL_M
    a, b = run[0][0] + TREAD_WALL_M, run[-1][0] - TREAD_WALL_M
    if hi <= lo or b <= a:
        return False
    corners = [(lo, a), (hi, a), (hi, b), (lo, b)] if axis == "h" else [(a, lo), (b, lo), (b, hi), (a, hi)]
    return Polygon([from_f(p) for p in corners]).intersects(wall_geom)


def _chains(segs: list[Seg], to_f) -> list[list[Seg]]:
    """Straight axis segments joined end to end (within 5 mm) into simple chains, in order."""
    straight = [s for s in segs if not s.curve and not s.dot]
    ends, coords = _end_nodes(straight)
    adj: dict = {}
    for i, e in enumerate(ends):
        if e is None:
            continue
        adj.setdefault(e[0], []).append(i)
        adj.setdefault(e[1], []).append(i)
    seen = set()
    chains = []
    for i in range(len(straight)):
        if i in seen or ends[i] is None:
            continue
        # Walk to one end of the chain, then collect forward.
        comp = []
        stack = [i]
        while stack:
            k = stack.pop()
            if k in seen:
                continue
            seen.add(k)
            comp.append(k)
            for n in ends[k]:
                stack.extend(j for j in adj[n] if j not in seen)
        degrees = {}
        for k in comp:
            for n in ends[k]:
                degrees[n] = degrees.get(n, 0) + 1
        if any(d > 2 for d in degrees.values()):
            continue
        start_nodes = [n for n, d in degrees.items() if d == 1]
        if len(start_nodes) != 2:
            continue
        order, node, used = [], start_nodes[0], set()
        while True:
            nxt = [k for k in adj[node] if k in comp and k not in used]
            if not nxt:
                break
            k = nxt[0]
            used.add(k)
            order.append(straight[k])
            a, b = ends[k]
            node = b if a == node else a
        chains.append((order, coords[start_nodes[0]], coords[node]))
    return chains


def counter_rule(cl: Cluster, walls: list, openings: list, theta: float, loose_in_blocks: bool = False) -> list[dict]:
    """Kitchen counter legs (§2.8): a chain of >= 2 straight segments whose two ends lie within 50 mm of a wall
    face (openings included) with segments parallel to a wall face at 0.45-0.75 m. Returns one dict per leg
    ``{"rect_f", "front_f", "wall", "segs", "length", "depth"}`` (aligned frame). ``loose_in_blocks`` (Milestone 12
    re-read): the cluster's strokes are the loose drawing of a block holding blocks (a flat inserted as a block,
    real03), so they count as loose strokes."""
    to_f, from_f = _frame(theta)
    faces = _wall_faces(walls, openings, to_f)
    out = []
    # Milestone 11 (docs/milestone11.md §1.2 U12): a block's own strokes are never a counter run (real02: five strokes
    # of a bedroom wardrobe block were read as counter legs); a counter drawn as a block is typed by its name.
    loose = list(cl.segs) if loose_in_blocks else [s for s in cl.segs if not s.stroke.block]
    for chain, a_end, b_end in _chains(loose, to_f):
        if len(chain) < 2:
            continue
        if not (_near_face(to_f(a_end), faces) and _near_face(to_f(b_end), faces)):
            continue
        legs = []
        for s in chain:
            p, q = to_f(s.pts[0]), to_f(s.pts[-1])
            if _is_cap(p, q, faces):
                continue
            for f in faces:
                if f["axis"] == "h" and abs(p[1] - q[1]) <= 0.003:
                    d = (p[1] + q[1]) / 2 - f["pos"]
                    lo, hi = sorted((p[0], q[0]))
                    if COUNTER_DEPTH_M[0] <= abs(d) <= COUNTER_DEPTH_M[1] and math.copysign(1, d) == f["normal"] \
                            and min(hi, f["hi"]) - max(lo, f["lo"]) >= 0.8 * (hi - lo):
                        legs.append({"seg": s, "axis": "h", "lo": lo, "hi": hi, "front": (p[1] + q[1]) / 2,
                                     "back": f["pos"], "face": f})
                        break
                if f["axis"] == "v" and abs(p[0] - q[0]) <= 0.003:
                    d = (p[0] + q[0]) / 2 - f["pos"]
                    lo, hi = sorted((p[1], q[1]))
                    if COUNTER_DEPTH_M[0] <= abs(d) <= COUNTER_DEPTH_M[1] and math.copysign(1, d) == f["normal"] \
                            and min(hi, f["hi"]) - max(lo, f["lo"]) >= 0.8 * (hi - lo):
                        legs.append({"seg": s, "axis": "v", "lo": lo, "hi": hi, "front": (p[0] + q[0]) / 2,
                                     "back": f["pos"], "face": f})
                        break
        if not legs:
            continue
        # The corner square goes to the longer leg: extend it to the other leg's wall face.
        for i in range(len(legs)):
            for j in range(len(legs)):
                if i == j or legs[i]["axis"] == legs[j]["axis"]:
                    continue
                li, lj = legs[i], legs[j]
                if (li["hi"] - li["lo"]) < (lj["hi"] - lj["lo"]):
                    continue
                # Does lj's front line meet li's extent end? Extend li to lj's back face.
                if abs(lj["front"] - li["hi"]) <= COUNTER_END_M and abs(lj["back"] - li["hi"]) <= COUNTER_DEPTH_M[1]:
                    li["hi"] = max(li["hi"], lj["back"])
                elif abs(lj["front"] - li["lo"]) <= COUNTER_END_M:
                    li["lo"] = min(li["lo"], lj["back"])
        for leg in legs:
            f0, f1 = sorted((leg["front"], leg["back"]))
            rect = (leg["lo"], f0, leg["hi"], f1) if leg["axis"] == "h" else (f0, leg["lo"], f1, leg["hi"])
            front_dir = (0.0, math.copysign(1.0, leg["front"] - leg["back"])) if leg["axis"] == "h" else \
                (math.copysign(1.0, leg["front"] - leg["back"]), 0.0)
            out.append({"rect_f": rect, "front_f": front_dir, "segs": chain, "leg": leg["seg"],
                        "length": leg["hi"] - leg["lo"], "depth": abs(leg["front"] - leg["back"]),
                        "wall_face": leg["face"]})
    return out


def _wall_faces(walls: list, openings: list, to_f) -> list[dict]:
    """Both long faces of every axis wall in the aligned frame: {"axis", "pos", "lo", "hi", "normal"} where
    ``normal`` is the side of the face away from the wall (+1 / -1)."""
    faces = []
    for w in walls:
        start, end, t = (w["start"], w["end"], w["thickness"]) if isinstance(w, dict) else (w.start, w.end, w.thickness)
        a, b = to_f(start), to_f(end)
        if abs(a[1] - b[1]) <= 0.01:
            c, lo, hi = (a[1] + b[1]) / 2, min(a[0], b[0]), max(a[0], b[0])
            faces.append({"axis": "h", "pos": c + t / 2, "lo": lo, "hi": hi, "normal": 1.0})
            faces.append({"axis": "h", "pos": c - t / 2, "lo": lo, "hi": hi, "normal": -1.0})
        elif abs(a[0] - b[0]) <= 0.01:
            c, lo, hi = (a[0] + b[0]) / 2, min(a[1], b[1]), max(a[1], b[1])
            faces.append({"axis": "v", "pos": c + t / 2, "lo": lo, "hi": hi, "normal": 1.0})
            faces.append({"axis": "v", "pos": c - t / 2, "lo": lo, "hi": hi, "normal": -1.0})
    return faces


def _is_cap(p, q, faces: list[dict]) -> bool:
    """A segment with one end on a wall face, perpendicular to that face: the end of a counter run, not a leg."""
    horizontal = abs(p[1] - q[1]) <= 0.003
    for end in (p, q):
        for f in faces:
            if f["axis"] == "h" and not horizontal and abs(end[1] - f["pos"]) <= COUNTER_END_M \
                    and f["lo"] - COUNTER_END_M <= end[0] <= f["hi"] + COUNTER_END_M:
                return True
            if f["axis"] == "v" and horizontal and abs(end[0] - f["pos"]) <= COUNTER_END_M \
                    and f["lo"] - COUNTER_END_M <= end[1] <= f["hi"] + COUNTER_END_M:
                return True
    return False


def _near_face(p, faces: list[dict]) -> bool:
    """Whether point ``p`` (aligned frame) lies within 50 mm of a wall face."""
    for f in faces:
        across, along = (p[1], p[0]) if f["axis"] == "h" else (p[0], p[1])
        if abs(across - f["pos"]) <= COUNTER_END_M and f["lo"] - COUNTER_END_M <= along <= f["hi"] + COUNTER_END_M:
            return True
    return False


# --------------------------------------------------------------------------
# Footprints, fronts, evidence
# --------------------------------------------------------------------------

def min_rect(pts) -> tuple[list[tuple[float, float]], float]:
    """Corners and area of the minimum-area rectangle of a point set (cv2.minAreaRect, fast on thousands of
    points; coordinates are shifted to the first point to keep float32 precision)."""
    import cv2

    arr = np.asarray(pts, dtype=np.float64)
    o = arr[0]
    box = cv2.boxPoints(cv2.minAreaRect((arr - o).astype(np.float32)))
    corners = [(float(x) + o[0], float(y) + o[1]) for x, y in box]
    return corners, math.dist(corners[0], corners[1]) * math.dist(corners[1], corners[2])


def short_side(segs: list[Seg]) -> float:
    """Short side of the minimum-area rectangle of a stroke set (0 for one straight line, whatever its angle)."""
    pts = list({p for s in segs for p in s.pts})
    if len(pts) < 3:
        return 0.0
    c, _ = min_rect(pts)
    return min(math.dist(c[0], c[1]), math.dist(c[1], c[2]))


def _short_ids(ids, limit: int = 12) -> str:
    """``id_ranges`` of ``ids``, at most ``limit`` entries (then ``... (+n)``)."""
    parts = id_ranges(ids).split(",") if ids else []
    if len(parts) <= limit:
        return ",".join(parts)
    return ",".join(parts[:limit]) + f",... (+{len(parts) - limit})"


def circle_fit(segs: list[Seg]) -> Optional[dict]:
    """``{"share", "radius"}`` of a least-squares circle through the piece's outline: the convex hull of its stroke
    points, sampled every ~1 cm (sampling the outline, not the vertices: a rectangle's 4 corners lie on a circle
    too). ``share`` = the fraction of the outline within max(10 mm, 3 % r) of the circle."""
    from shapely.geometry import MultiPoint

    pts = [p for s in segs for p in s.pts]
    if len(set(pts)) < 3:
        return None
    hull = MultiPoint(pts).convex_hull
    if hull.geom_type != "Polygon" or hull.area <= 0:
        return None
    ring = hull.exterior
    n = max(64, min(2000, int(ring.length / 0.01)))
    samples = np.array([ring.interpolate(k * ring.length / n).coords[0] for k in range(n)])
    o = samples.mean(axis=0)
    xs, ys = samples[:, 0] - o[0], samples[:, 1] - o[1]
    a = np.c_[2.0 * xs, 2.0 * ys, np.ones(n)]
    sol, *_ = np.linalg.lstsq(a, xs * xs + ys * ys, rcond=None)
    cx, cy, c = sol
    r2 = c + cx * cx + cy * cy
    if r2 <= 0:
        return None
    r = math.sqrt(r2)
    d = np.hypot(xs - cx, ys - cy)
    share = float(np.mean(np.abs(d - r) <= max(ROUND_TOL_M, ROUND_TOL_REL * r)))
    return {"share": round(share, 3), "radius": round(r, 4)}


def round_shape(segs: list[Seg]) -> dict:
    """``{"shape": "round", "circle_fit": {...}}`` when a circle fits >= 90 % of the piece's outline
    (docs/milestone7.md §6.4: a round side table), else ``{}``."""
    fit = circle_fit(segs)
    if fit is None or fit["share"] < ROUND_SHARE:
        return {}
    return {"shape": "round", "circle_fit": fit}


def footprint(pts, theta: float) -> tuple[tuple[float, float], float, float, float, list]:
    """(centre, extent along u, extent along v, angle of u in deg, corners): the minimum-area rectangle, snapped to
    the plan's dominant orientation when within 3 deg of it."""
    to_f, from_f = _frame(theta)
    fp = [to_f(p) for p in pts]
    xs = [p[0] for p in fp]
    ys = [p[1] for p in fp]
    frame_area = (max(xs) - min(xs)) * (max(ys) - min(ys))
    c, area = min_rect(pts)
    if len(pts) >= 3 and area > 1e-12 and frame_area > 1.02 * area:     # round pieces stay in the frame
        c = c + [c[0]]
        ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0]))
        off = (ang - theta) % 90.0
        off = min(off, 90.0 - off)
        if off > SNAP_DEG:
            angle_u = ang % 180.0
            ext_u, ext_v = math.dist(c[0], c[1]), math.dist(c[1], c[2])
            centre = ((c[0][0] + c[2][0]) / 2.0, (c[0][1] + c[2][1]) / 2.0)
            return centre, ext_u, ext_v, angle_u, [tuple(p) for p in c[:4]]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    centre = from_f(((x0 + x1) / 2.0, (y0 + y1) / 2.0))
    return centre, x1 - x0, y1 - y0, theta % 180.0, corners


def size_rotation(ext_u: float, ext_v: float, angle_u: float, front_deg: Optional[float]):
    """(size [width, depth], rotation_deg) in the codebase convention: an unrotated piece faces -Y, width across
    the front; without a front the width is the longer side."""
    if front_deg is None:
        if ext_u >= ext_v:
            return (round(ext_u, 4), round(ext_v, 4)), round(angle_u % 180.0, 3)
        return (round(ext_v, 4), round(ext_u, 4)), round((angle_u + 90.0) % 180.0, 3)
    rotation = (front_deg + 90.0) % 360.0
    d = abs((front_deg - angle_u + 90.0) % 180.0 - 90.0)      # 0 when the front is along u
    if d < 45.0:
        return (round(ext_v, 4), round(ext_u, 4)), round(rotation, 3)
    return (round(ext_u, 4), round(ext_v, 4)), round(rotation, 3)


def id_ranges(ids) -> str:
    """``line:3,line:4,line:5,curve:9`` -> ``curve:9,line:3-5`` (segment suffixes dropped). Numeric ids are
    grouped into ranges per prefix; other ids (``INSERT:4B/3``) follow sorted, so the text does not depend on the
    cluster order (a DWG and its DXF give the same evidence)."""
    groups: dict[str, list[int]] = {}
    other: list[str] = []
    for sid in ids:
        base = sid.split("#", 1)[0]
        head, _, tail = base.partition(":")
        if tail.isdigit():
            groups.setdefault(head, []).append(int(tail))
        elif base not in other:
            other.append(base)
    parts = []
    for head in sorted(groups):
        nums = sorted(set(groups[head]))
        start = prev = nums[0]
        for n in nums[1:] + [None]:
            if n is not None and n == prev + 1:
                prev = n
                continue
            parts.append(f"{head}:{start}" if start == prev else f"{head}:{start}-{prev}")
            if n is not None:
                start = prev = n
    return ",".join(parts + sorted(other))


def _sides(corners) -> list[tuple[tuple, tuple]]:
    return [(corners[i], corners[(i + 1) % 4]) for i in range(4)]


def _outward_deg(side, centre) -> float:
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    return math.degrees(math.atan2(my - centre[1], mx - centre[0])) % 360.0


def _snap_deg(deg: float, theta: float) -> float:
    k = round((deg - theta) / 90.0)
    return round((theta + 90.0 * k) % 360.0, 3)


def near_wall_sides(sides, centre, wall_polys: list) -> list[int]:
    """Indices of the sides that have a wall within ``FRONT_WALL_M`` in front of them: the probe runs from the
    side's midpoint outwards, perpendicular to the side. (Measuring the midpoint's distance to any wall counted the
    short sides of a piece <= 0.5 m deep as near the wall its back touches, so a shallow piece against one wall got
    no front; M11 diagnosis, real02.)"""
    out = []
    for k, side in enumerate(sides):
        (ax, ay), (bx, by) = side
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            continue
        nx, ny = (by - ay) / length, -(bx - ax) / length
        if nx * (mx - centre[0]) + ny * (my - centre[1]) < 0:
            nx, ny = -nx, -ny
        probe = LineString([(mx, my), (mx + nx * FRONT_WALL_M, my + ny * FRONT_WALL_M)])
        if any(w.distance(probe) <= 1e-9 for w in wall_polys):
            out.append(k)
    return out


def front_candidates(piece_segs: list[Seg], centre, corners, wall_polys: list, others: list, theta: float,
                     table: dict) -> list[dict]:
    """Deterministic front candidates (§2.8): the only side within 0.25 m of a wall is the back; the side holding
    >= 2 small closed shapes is a bed's head (pillows); a chair-sized piece faces the nearest table-sized piece."""
    out = []
    sides = _sides(corners)
    near = [sides[k] for k in near_wall_sides(sides, centre, wall_polys)]
    if len(near) == 1:
        back = _outward_deg(near[0], centre)
        out.append({"front_deg": _snap_deg(back + 180.0, theta),
                    "rule": "only side within 0.25 m of a wall is the back"})
    # Pillows: >= 2 small closed contours next to one side.
    small = [p for p, _ in contours(piece_segs) if 0.15 <= max(_rect_sides(p)) <= 0.8 and min(_rect_sides(p)) >= 0.08]
    if len(small) >= 2:
        best = None
        tied = False
        for k, side in enumerate(sides):
            line = LineString(side)
            reach = 0.3 * math.dist(*sides[(k + 1) % 4])          # 30 % of the piece's extent away from the side
            n = sum(1 for p in small if line.distance(p.centroid) <= reach)
            if n >= 2 and best is not None and n == best[0]:
                tied = True
            elif n >= 2 and (best is None or n > best[0]):
                best, tied = (n, side), False
        # Two sides with the same count: the rule cannot tell the head (picking the first side made mirrored twins
        # disagree: real02's r_L0_yatak_odasi_3 bed lost its front, its twin kept one; M11 diagnosis).
        if best is not None and not tied:
            head = _outward_deg(best[1], centre)
            out.append({"front_deg": _snap_deg(head + 180.0, theta),
                        "rule": "head = side with >= 2 small closed shapes"})
    # A chair faces the nearest table.
    u = math.dist(*sides[0])
    v = math.dist(*sides[1])
    if max(u, v) <= 0.7:
        best = None
        for o in others:
            if o["poly"] is None:
                continue
            if not (fits(table, "table_dining", o["size"]) or fits(table, "table_coffee", o["size"])):
                continue
            seats = [x for x in others
                     if x is not o and max(x["size"]) <= 0.7 and x["poly"].distance(o["poly"]) <= 0.5]
            if len(seats) + 1 < 2:                    # a table has at least two seats around it
                continue
            d = o["poly"].distance(Point(centre))
            if d <= 0.5 + max(u, v) / 2 and (best is None or d < best[0]):
                best = (d, o)
        if best is not None:
            tc = best[1]["poly"].centroid
            deg = math.degrees(math.atan2(tc.y - centre[1], tc.x - centre[0]))
            out.append({"front_deg": _snap_deg(deg, theta), "rule": "chair faces the nearest table"})
    uniq: list[dict] = []
    for c in out:
        same = [u for u in uniq if abs(c["front_deg"] - u["front_deg"]) < 1e-6]
        if same:
            same[0]["rule"] += "; " + c["rule"]          # rules that agree are kept together
        else:
            uniq.append(dict(c))
    return uniq


# --------------------------------------------------------------------------
# Main entry
# --------------------------------------------------------------------------

@dataclass
class _Ctx:
    file_rel: str
    page_no: Optional[int]
    units_to_m: Optional[float]
    theta: float
    level_id: Optional[str]

    def evidence(self, ids, confidence: float = FOOTPRINT_CONFIDENCE, raster: bool = False, box=None,
                 method: Optional[str] = None, note: Optional[str] = None) -> dict:
        m = method or ("raster" if raster else "vector")
        if m == "raster":
            confidence = min(confidence, 0.7)
        ev = B.evidence(self.file_rel, m, round(confidence, 3), page=self.page_no, entity=id_ranges(ids) or None,
                        pixel_box=box if (m == "raster" and box) else None)
        if note:
            ev["note"] = note
        return ev

    def box(self, corners) -> list[float]:
        xs = [p[0] for p in corners]
        ys = [p[1] for p in corners]
        bx = [min(xs), min(ys), max(xs), max(ys)]
        if self.units_to_m:
            bx = [v / self.units_to_m for v in bx]
        return [round(v, 3) for v in bx]


def _face_info(faces, point) -> tuple[Optional[str], Optional[str]]:
    """(room_type, label) of the face containing ``point``; faces are polygons, point lists or dicts with
    ``polygon`` and optional ``room_type``/``label``."""
    for f in faces or []:
        if isinstance(f, dict):
            poly = f.get("polygon")
            poly = poly if hasattr(poly, "contains") else Polygon(poly)
            if poly.contains(Point(point)):
                return f.get("room_type"), f.get("label")
        else:
            poly = f if hasattr(f, "contains") else Polygon(f)
            if poly.contains(Point(point)):
                return None, None
    return None, None


def furniture(strokes_m: list[Stroke], owned: set, walls: list[WallItem], openings: list[OpeningItem], texts_m: list,
              dims: list, outline, faces: list, *, wall_strokes=(), site_walls=(), level_id: Optional[str] = None,
              file_rel: Optional[str] = None, page_no: Optional[int] = None, units_to_m: Optional[float] = None,
              size_table: Optional[dict] = None, notes: Optional[list] = None, extra_out: Optional[list] = None,
              symbols_out: Optional[list] = None
              ) -> tuple[list[FurnitureItem], list[dict], list[dict]]:
    """Furniture pieces typed by rules or block names, AI candidates and site decor (all page metres).

    ``owned``: stroke ids the openings own; ``wall_strokes``: ids of the wall primitives (hatch lines, fills) that are
    walls; ``site_walls``: the plot/other walls (WallItems or ``site.boundary_walls`` dicts) so their outline strokes
    are not decor; ``outline``: the building outline (shapely polygon or point list; None -> from ``walls``);
    ``faces``: room faces (polygons, or dicts with ``polygon``, ``room_type``, ``label``) for room checks and hints;
    ``dims``: dimension candidates exposing ``stroke_ids``. ``notes`` (a list) receives report lines.
    Returns ``(pieces, candidates, decor)``: rule/block-name typed pieces plus the unknown composites and oversize
    clusters (never asked); AI candidate dicts ``{key, footprint, strokes, bbox, room_hint, front_candidates, fits,
    item}`` whose ``item`` is the FurnitureItem (``unknown``, ``unverified``, ``type_method "none"``) to keep until
    answers exist; site decor dicts ``{kind, center, size, evidence[, id]}``.

    Milestone 12 (track R): clusters nobody types (larger than 4.5 m, composites, parts fitting no type) are re-read
    (``reread``). Every piece and candidate whose strokes are a symbol gets ``details["symbol"]`` (``whole_symbol``;
    or ``details["not_furniture"]`` for a column or decor) for ``reading.read_furniture``. With ``extra_out`` (a list)
    the never-asked unknown pieces that fit a type become extra candidates there (``extra_key``; the core asks them
    after its own); with ``symbols_out`` the symbols found inside re-read clusters are appended there.
    """
    notes = notes if notes is not None else []
    if size_table is None:
        table, source = load_size_table()
    else:
        table, source = size_table, "given size table"
    notes.append(f"furniture size checks use the {source}")
    ref = walls[0].evidence if walls else {}
    ctx = _Ctx(file_rel or ref.get("file", ""), page_no if page_no is not None else ref.get("page"), units_to_m,
               _dominant(walls), level_id)
    raster_page = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)

    drop = set(owned or ()) | set(wall_strokes or ()) | _dimension_ids(dims)
    segs = _segments(strokes_m, drop)
    boxes = _text_boxes(texts_m)
    if boxes:
        tree = STRtree(boxes)
        kept = []
        glyphs = 0
        whole_in: dict[str, bool] = {}
        for s in segs:
            if s.stroke.source == "vector":
                # Milestone 10 (real02): a vector stroke is a glyph only when all of it lies in a text box; a room
                # label written over a fixture (BANYO over the WC bowl) must not cut the fixture's outline.
                inside = whole_in.get(s.stroke.id)
                if inside is None:
                    inside = whole_in[s.stroke.id] = bool(len(tree.query(_stroke_geom(s.stroke), predicate="within")))
            else:
                inside = bool(len(tree.query(s.geom, predicate="within")))
            if inside:
                glyphs += 1
            else:
                kept.append(s)
        segs = kept
        if glyphs:
            notes.append(f"{glyphs} glyph strokes inside text boxes ignored")
    wall_geom = _wall_geometry(walls, openings, list(site_walls or ()))
    kept, n_outline = _drop_outline(segs, wall_geom)
    kept_ids = {id(s) for s in kept}
    near_wall = [s for s in segs if id(s) not in kept_ids]
    notes.append(f"{n_outline} stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)")
    # Milestone 10 (real02's attic): the long sides of an outline larger than any piece in both directions (the
    # mansard's break line runs through the bathrooms) are no furniture strokes: they would chain every fixture they
    # touch into one cluster. A long piece drawn by separate lines (one 5 m stroke per side) stays.
    def _area_outline(s: Seg) -> bool:
        b = s.stroke.bbox()
        return min(b[2] - b[0], b[3] - b[1]) > MAX_SIDE_M
    long_lines = [s for s in kept if not s.curve and not s.dot and s.length > MAX_SIDE_M and _area_outline(s)]
    if long_lines:
        kept = [s for s in kept if s not in long_lines]
        notes.append(f"{len(long_lines)} sides of outlines larger than {MAX_SIDE_M} m both ways are no furniture: "
                     f"{_short_ids([s.id for s in long_lines])}")

    poly = _as_polygon(outline)
    if poly is None or poly.is_empty:
        poly = TP.building_outline(walls, openings)
    inside_poly = poly.buffer(0.001)
    shapely.prepare(inside_poly)
    mids = np.array([s.geom.centroid if not s.dot else s.geom for s in kept], dtype=object)
    inside_mask = shapely.contains(inside_poly, mids) if len(mids) else np.zeros(0, bool)
    inside = [s for s, m in zip(kept, inside_mask) if m]
    outside = [s for s, m in zip(kept, inside_mask) if not m]
    # Pod F2 (synthetic-07's attic): a long straight stroke that crosses the building outline (a roof ridge or eaves
    # line drawn on the top plan, a grid axis, a section line) is no furniture stroke: it would chain every piece and
    # door leaf it touches into one cluster. Strokes outside the outline (site decor) are not touched.
    crossing = [s for s in inside if not s.curve and not s.dot and s.length > MAX_SIDE_M
                and s.geom.difference(inside_poly).length > OUTLINE_NEAR_M]
    if crossing:
        drop_ids = {id(s) for s in crossing}
        inside = [s for s in inside if id(s) not in drop_ids]
        notes.append(f"{len(crossing)} straight strokes longer than {MAX_SIDE_M} m that cross the building outline "
                     f"are no furniture: {_short_ids([s.id for s in crossing])}")
    pool = [s for s in near_wall if inside_poly.contains(s.geom.centroid if not s.dot else s.geom)]

    clusters = clusters_of(inside)
    taken: set = set()
    for cl in sorted(clusters, key=lambda c: -_bbox_area(c.bounds(ctx.theta))):
        reclose(cl, pool, taken, ctx.theta)
    clusters = group_treads(clusters, ctx.theta, wall_geom, notes)
    clusters = _merge_contained(clusters, table, ctx.theta)

    wall_polys = [TP.wall_polygon(w) for w in walls]
    pieces: list[FurnitureItem] = []
    cands: list[dict] = []
    reread_symbols: list[dict] = []
    page_containers = containers_of(s.stroke for s in segs)
    details = 0
    line_ids: list[str] = []
    parts_all: list[tuple[Cluster, int]] = []
    l_parts: dict[int, dict] = {}
    for cl in clusters:
        w, h = cl.size(ctx.theta)
        if max(w, h) < DETAIL_M:
            details += 1
            continue
        if short_side(cl.segs) < LINE_DETAIL_M:
            line_ids.extend(cl.stroke_ids())
            continue
        # A stair is read before the L outline: a quarter-turn stair drawn as a closed L with its treads inside is
        # a stair, not a corner sofa (review #11).
        small = max(w, h) <= MAX_SIDE_M
        stair = stair_rule(cl, ctx.theta) if small else None
        lsh = l_shape(cl, ctx.theta) if small and stair is None else None
        if lsh is not None:
            # An L outline is one piece (its rotated minimum rectangle is no footprint): the corner sofa (§1.1).
            l_parts[id(cl)] = lsh
            parts_all.append((cl, 1))
            continue
        fp = footprint([p for s in cl.segs for p in s.pts], ctx.theta)
        oversize = max(fp[1], fp[2]) > MAX_SIDE_M
        # Milestone 10 (real02): a kitchen whose counter run, appliances and bar stools touch is one cluster larger
        # than 4.5 m; its counter legs are still read, and the rest is split as usual.
        legs = counter_rule(cl, walls, openings, ctx.theta) if oversize else None
        if oversize and not legs:
            # Milestone 11 (U8): a kitchen whose counter run is drawn as closed outlines along the walls is split into
            # the counter legs, the hob and sink blocks and the rest (never asked).
            ks = kitchen_split(cl, walls, openings, ctx.theta)
            if ks is not None:
                pieces.extend(kitchen_items(ks, walls, ctx, raster_page, table, wall_polys, notes))
                continue
            # real03 (10 Oct 2026): a living room whose sofa, table, chairs and kitchen blocks touch is one cluster
            # larger than 4.5 m. It is split like a composite (named blocks by instance, the rest by contours); the
            # parts that fit within 4.5 m go on as pieces, and what is still larger is recorded but not built.
            subs = split_composite(cl, table) if len(cl.segs) <= OVERSIZE_SPLIT_MAX_SEGS else []
            small_subs = [(sub, n) for sub, n in subs if max(sub.size(ctx.theta)) <= MAX_SIDE_M]
            if len(subs) > 1 and small_subs:
                parts_all.extend(small_subs)
                rest = [sub for sub, _ in subs if max(sub.size(ctx.theta)) > MAX_SIDE_M]
                notes.append(f"cluster {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}) larger than "
                             f"{MAX_SIDE_M} m split into {len(small_subs)} parts"
                             + (f" ({len(rest)} still larger: not built)" if rest else ""))
            else:
                rest = [cl]
                notes.append(f"cluster {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}) larger than "
                             f"{MAX_SIDE_M} m: unknown, unverified, not asked, not built")
            for big in rest:
                # Milestone 12 (track R): what stays larger than 4.5 m is re-read (symbol strokes out, one part per
                # block instance and stroke group); only when that gives nothing is it recorded as before.
                got = reread(big, ctx, table, walls, openings, wall_polys, texts_m, notes, raster_page,
                             containers=page_containers,
                             why=f"cluster larger than {MAX_SIDE_M} m") if len(big.segs) <= OVERSIZE_SPLIT_MAX_SEGS \
                    else {"items": [], "symbols": []}
                for it in got["items"]:
                    if it.type == "unknown" and max(it.size) > MAX_SIDE_M:
                        it.details.update(oversize=True, build=False)
                if got["symbols"] or [it for it in got["items"] if not it.details.get("oversize")]:
                    pieces.extend(got["items"])
                    reread_symbols.extend(got["symbols"])
                    notes.append(f"cluster larger than {MAX_SIDE_M} m re-read (M12): {len(got['items'])} pieces, "
                                 f"{len(got['symbols'])} symbols")
                    continue
                bfp = footprint([p for s in big.segs for p in s.pts], ctx.theta)
                pieces.append(_unknown(big, bfp, ctx, raster_page, f"cluster larger than {MAX_SIDE_M} m on a side: "
                                       "a group of drawn pieces, not built", {"oversize": True, "build": False}))
            continue
        if oversize:
            stair = None
        elif not small:
            stair = stair_rule(cl, ctx.theta)
        if stair is not None:
            pieces.append(_stair_item(cl, stair, fp, ctx, raster_page, notes))
            continue
        if not oversize:
            legs = counter_rule(cl, walls, openings, ctx.theta)
            if legs or not fitting_types(table, (fp[1], fp[2])):
                # Milestone 11 (U8): a kitchen cluster (a counter run, or one that fits no type): its closed counter
                # outlines become the legs and the free blocks (a peninsula), its hob and sink blocks are named, the
                # rest is never asked. Mirrored twins take the same path whichever strokes their clusters hold.
                ks = kitchen_split(cl, walls, openings, ctx.theta)
                if ks is not None:
                    pieces.extend(kitchen_items(ks, walls, ctx, raster_page, table, wall_polys, notes))
                    continue
        if legs:
            used = set()
            for leg in legs:
                pieces.append(_counter_item(leg, walls, ctx, raster_page))
                used.update(id(s) for s in leg["segs"])
            rest = [s for s in cl.segs if id(s) not in used]
            for sub in clusters_of(rest, CLUSTER_M):
                if max(sub.size(ctx.theta)) >= DETAIL_M:
                    parts_all.extend(split_composite(sub, table))
                else:
                    details += 1
            continue
        parts_all.extend(split_composite(cl, table))

    # Footprints of all parts first (the chair rule looks at the tables).
    infos = []
    for part, n in parts_all:
        if max(part.size(ctx.theta)) < DETAIL_M:
            details += 1
            continue
        if short_side(part.segs) < LINE_DETAIL_M:
            line_ids.extend(part.stroke_ids())
            continue
        pts = [p for s in part.segs for p in s.pts]
        lsh = l_parts.get(id(part))
        fp = lsh["fp"] if lsh else footprint(pts, ctx.theta)
        infos.append({"part": part, "n": n, "fp": fp, "size": (fp[1], fp[2]), "poly": Polygon(fp[4]), "l": lsh,
                      "note": lsh["note"] if lsh else None})
    infos = named_instances(infos, table, ctx.theta, notes)
    for info in infos:
        part, n, fp, lsh = info["part"], info["n"], info["fp"], info.get("l")
        if info.get("rule_type"):
            # Milestone 11: a chair split off a named table block (``_split_named``).
            pieces.append(_rule_item(part.segs, fp, info["rule_type"], info.get("front"), ctx, raster_page, table,
                                     info.get("note") or "split (M11)"))
            continue
        shape = l_details(lsh) if lsh else (round_shape(part.segs) if n == 1 else {})
        block_item = None if info.get("no_name") else _block_item(part, fp, ctx, raster_page, table, lsh,
                                                                   wall_polys, [o for o in infos if o is not info],
                                                                   extended=False)
        if block_item is not None:
            block_item.details.update(shape)
            if info.get("note"):
                block_item.evidence["note"] = "; ".join(x for x in (block_item.evidence.get("note"), info["note"]) if x)
            pieces.append(block_item)
            continue
        types = fitting_types(table, (fp[1], fp[2]), "L" if lsh else None)
        if (n > 1 or not types) and not lsh:
            # Milestone 11 (U10, U8): a composite that is a table with its chairs, or a kitchen counter run with its
            # appliances, is split into its pieces (never asked: the candidates and their keys do not change).
            split = split_table_chairs(part, table, ctx.theta)
            if split is not None:
                made = table_chair_items(split, ctx, raster_page, table)
                pieces.extend(made)
                notes.append(f"table + {len(made) - 1} chairs at ({fp[0][0]:.2f}, {fp[0][1]:.2f}) split (M11)")
                continue
            ks = kitchen_split(part, walls, openings, ctx.theta)
            if ks is not None:
                pieces.extend(kitchen_items(ks, walls, ctx, raster_page, table, wall_polys, notes))
                continue
        if n > 1 or not types:
            reason = (f"possible group of {n} pieces" if n > 1 else "fits no size-table type")
            # Milestone 12 (track R): never asked, so it may be re-read; the re-read is kept when it found more than
            # the one unknown piece it started from.
            got = reread(part, ctx, table, walls, openings, wall_polys, texts_m, notes, raster_page, why=reason,
                         containers=page_containers)
            typed = [it for it in got["items"] if it.type != "unknown"]
            if typed or got["symbols"] or len(got["items"]) > 1:
                pieces.extend(got["items"])
                reread_symbols.extend(got["symbols"])
                notes.append(f"unknown piece {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}) "
                             f"({reason}) re-read (M12): {len(got['items'])} pieces, {len(got['symbols'])} symbols")
                continue
            pieces.append(_unknown(part, fp, ctx, raster_page, reason,
                                   dict({"composite": n} if n > 1 else {}, **shape)))
            notes.append(f"unknown piece {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}): {reason}")
            continue
        others = [o for o in infos if o is not info]
        if lsh:
            # The open inner corner of an L is its front (the drawn outline decides, before walls or pillows).
            fronts = [{"front_deg": lsh["front_deg"], "rule": "L outline: the open inner corner is the front"}]
        else:
            fronts = front_candidates(part.segs, fp[0], fp[4], wall_polys, others, ctx.theta, table)
        cand = _candidate(part, fp, ctx, raster_page, faces, fronts, types, len(cands) + 1)
        cand["item"].details.update(shape)
        if not lsh:
            # M11: the fronts that would face a wall (an AI front there is vetoed, recognition.symbols._front) and
            # the corner rule's front (used once the type is known to have its back on the long side, core).
            sides = _sides(fp[4])
            cand["wall_fronts"] = [_snap_deg(_outward_deg(sides[k], fp[0]), ctx.theta)
                                   for k in near_wall_sides(sides, fp[0], wall_polys)]
            corner = corner_back_front(fp[0], fp[4], wall_polys, ctx.theta)
            if corner is not None:
                cand["item"].details["corner_front"] = corner
        if lsh:
            cand["footprint"]["shape"] = "L"            # travels with the footprint into the question and decide
        if info.get("note"):
            cand["item"].evidence["note"] = "; ".join(x for x in (cand["item"].evidence.get("note"), info["note"]) if x)
        cands.append(cand)
    if details:
        notes.append(f"{details} drawn details smaller than {DETAIL_M} m ignored")
    if line_ids:
        notes.append(f"{len(line_ids)} line details (minimum rectangle thinner than {LINE_DETAIL_M} m: single lines, "
                     f"not furniture) ignored: {_short_ids(line_ids)}")
    decor = _site_decor(outside, ctx, raster_page, notes, wall_geom)
    pieces = _m12_pass(pieces, cands, segs, texts_m, openings, ctx, raster_page, table, faces, wall_polys,
                       reread_symbols, notes, extra_out, symbols_out)
    apply_room_checks(pieces, cands, faces, notes)
    return pieces, cands, decor


def _m12_pass(pieces: list[FurnitureItem], cands: list[dict], segs: list[Seg], texts, openings: list, ctx: _Ctx,
              raster: bool, table: dict, faces, wall_polys: list, reread_symbols: list, notes: list,
              extra_out: Optional[list], symbols_out: Optional[list]) -> list[FurnitureItem]:
    """Milestone 12 (track R), the end of ``furniture``: every piece and candidate whose strokes are a symbol (or a
    column, or decor) is marked (``whole_symbol``; the drawing outranks the AI passes, CLAUDE.md trust order); the
    candidates keep their re-read part (``cand["_part"]``) for the core's re-read after the answers; with
    ``extra_out`` the never-asked unknown pieces that fit a type become extra candidates (``extra_candidate``)."""
    index: dict[str, list[Seg]] = {}
    for s in segs:
        index.setdefault(s.stroke.id, []).append(s)
    jambs = opening_jambs(openings)

    def strokes_of(item: FurnitureItem) -> list[Seg]:
        return [s for sid in expand_ids(item.evidence.get("entity")) for s in index.get(sid, [])]

    marked = 0
    for item in pieces + [c["item"] for c in cands]:
        keys = copy_keys(strokes_of(item))
        if keys:
            item.details["copy_keys"] = keys
        if item.type == "stair" or item.details.get("build") is False:
            continue
        found = whole_symbol(strokes_of(item), texts, jambs)
        if found is None or (found["by"] == "layer" and item.type_method in ("rule", "block_name")):
            continue           # a rule or a block name typed it: its layer name says less (real02: "DEKOAKRILIK01")
        item.details["not_furniture" if "as" in found else "symbol"] = dict(found)
        marked += 1
    if marked:
        notes.append(f"{marked} drawn pieces are symbols, columns or decor, not furniture (M12; moved by the reading "
                     f"step)")
    for cand in cands:
        part = strokes_of(cand["item"])
        if part:
            cand["_part"] = Cluster(part)
    if symbols_out is not None:
        symbols_out.extend(reread_symbols)
    if extra_out is None:
        return pieces
    kept = []
    for item in pieces:
        part = strokes_of(item)
        if (item.type != "unknown" or item.details.get("build") is False or item.details.get("symbol")
                or item.details.get("not_furniture") or not part or item.details.get("oversize")):
            kept.append(item)
            continue
        fp = footprint([p for s in part for p in s.pts], ctx.theta)
        if not fitting_types(table, (fp[1], fp[2]), "L" if item.details.get("l_outline") else None):
            kept.append(item)                     # nothing to offer: the reading step lists it (needs review)
            continue
        extra_out.append(extra_candidate(Cluster(part), fp, item, ctx, raster, faces, wall_polys, table))
    if len(kept) < len(pieces):
        notes.append(f"{len(pieces) - len(kept)} never-asked unknown pieces that fit a type are asked as extra "
                     f"questions (M12)")
    return kept


def extra_candidate(part: Cluster, fp, item: FurnitureItem, ctx: _Ctx, raster: bool, faces, wall_polys: list,
                    table: dict) -> dict:
    """An AI candidate for a never-asked unknown piece (Milestone 12): as ``_candidate`` but keyed by its strokes
    (``extra_key``) and keeping the piece's own evidence and details (the re-read reason, a door swing)."""
    shape = "L" if item.details.get("l_outline") else None
    types = fitting_types(table, (fp[1], fp[2]), shape)
    cand = _candidate(part, fp, ctx, raster, faces, front_candidates(part.segs, fp[0], fp[4], wall_polys, [],
                                                                     ctx.theta, table), types, 0)
    key = extra_key(ctx.level_id, part.stroke_ids())
    cand["key"] = key
    cand["extra"] = True
    if shape:
        cand["footprint"]["shape"] = shape
    cand["item"].details.update({k: v for k, v in item.details.items() if k not in ("candidate_key",)},
                                candidate_key=key)
    cand["item"].evidence = item.evidence
    sides = _sides(fp[4])
    cand["wall_fronts"] = [_snap_deg(_outward_deg(sides[k], fp[0]), ctx.theta)
                           for k in near_wall_sides(sides, fp[0], wall_polys)]
    cand["_part"] = part
    return cand


def apply_room_checks(pieces: list[FurnitureItem], candidates: list[dict], faces: list, notes: list) -> None:
    """Room-dependent parts of §2.8, also callable again once the separators are known: a kitchen counter is
    ``verified`` only in a kitchen; a rule stair in a face that is neither hall nor unlabelled is ``unverified``;
    candidates get their ``room_hint``. ``faces``: dicts with ``polygon``, ``room_type``, ``label`` (or bare
    polygons, which carry no room type)."""
    for p in pieces:
        room_type, label = _face_info(faces, p.center)
        if p.type == "kitchen_counter" and p.type_method == "rule":
            p.status = "verified" if room_type == "kitchen" else "unverified"
            if p.status == "unverified" and faces:
                notes.append(f"kitchen counter at ({p.center[0]:.2f}, {p.center[1]:.2f}) not in a kitchen "
                             f"({label or 'unlabelled'}): unverified")
        elif p.type == "stair" and p.type_method == "rule":
            if label is not None and room_type not in (None, "hall", "unknown"):
                if p.status != "unverified":
                    notes.append(f"stair drawn in the labelled room '{label}' ({room_type}): unverified")
                p.status = "unverified"
    for c in candidates:
        room_type, label = _face_info(faces, c["footprint"]["center"])
        c["room_hint"] = label or room_type


def _dominant(walls) -> float:
    from wenart.ingest.generic.openings import dominant_angle
    return dominant_angle(walls) if walls else 0.0


def _unknown(cl: Cluster, fp, ctx: _Ctx, raster: bool, reason: str, details: dict) -> FurnitureItem:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    ev = ctx.evidence(cl.stroke_ids(), raster=raster, box=box, note=reason)
    return FurnitureItem(type="unknown", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=cl.stroke_ids()[0], evidence=ev, status="unverified",
                         type_method="none", details=dict(details, reason=reason))


def _stair_item(cl: Cluster, stair: dict, fp, ctx: _Ctx, raster: bool, notes: list) -> FurnitureItem:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    status = "verified"
    flights = stair["flights"]
    turn = "U" if len(flights) == 2 else ("straight" if len(flights) == 1 else "other")
    a = flights[0]
    d = (a["end"][0] - a["start"][0], a["end"][1] - a["start"][1])
    n = math.hypot(*d) or 1.0
    reason = ("no UP arrow, break line or riser text drawn: rise direction and flight order are assumed"
              + ("; two side-by-side flights read as a U-turn (dog-leg) stair" if len(flights) == 2 else ""))
    details = {"stair": {"flights": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in f.items()}
                                     for f in flights],
                         "landing": stair["landing"], "direction": [round(d[0] / n, 4), round(d[1] / n, 4)],
                         "direction_assumed": True, "turn": turn, "turn_assumed": True, "void_assumed": True,
                         "riser_m": None, "riser_source": None, "reason": reason}}
    ev = ctx.evidence(cl.stroke_ids(), raster=raster, box=box,
                      note=f"stair rule: {len(flights)} flight(s), {', '.join(str(f['lines']) for f in flights)} "
                           f"tread lines")
    widths = ", ".join(f"{f['width']:.3f}" for f in flights)
    notes.append(f"stair at ({fp[0][0]:.2f}, {fp[0][1]:.2f}): {len(flights)} flight(s) of {widths} m")
    return FurnitureItem(type="stair", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=cl.stroke_ids()[0], evidence=ev, status=status,
                         type_method="rule", details=details)


def _counter_item(leg: dict, walls: list, ctx: _Ctx, raster: bool) -> FurnitureItem:
    to_f, from_f = _frame(ctx.theta)
    x0, y0, x1, y1 = leg["rect_f"]
    corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    centre = from_f(((x0 + x1) / 2, (y0 + y1) / 2))
    fdir = from_f(leg["front_f"])
    front_deg = round(math.degrees(math.atan2(fdir[1], fdir[0])) % 360.0, 3)
    size, rotation = size_rotation(x1 - x0, y1 - y0, ctx.theta % 180.0, front_deg)
    box = ctx.box(corners)
    status = "unverified"                      # verified by apply_room_checks when it stands in a kitchen
    ids = sorted({s.stroke.id for s in leg["segs"]}, key=_id_key)
    wall_index = None
    best = math.inf
    for k, w in enumerate(walls):
        d = TP.wall_polygon(w).distance(Polygon(corners))
        if d < best:
            best, wall_index = d, k
    ev = ctx.evidence(ids, raster=raster, box=box, note="kitchen counter rule: chained legs between wall faces")
    return FurnitureItem(type="kitchen_counter", type_raw=None, center=_r(centre), size=size, rotation_deg=rotation,
                         front_deg=front_deg, box=box, entity=ids[0], evidence=ev, status=status, type_method="rule",
                         details={"counter_run": {"wall_id": None, "wall_index": wall_index, "strokes": ids,
                                                  "depth": round(leg["depth"], 4), "length": round(x1 - x0 if
                                                  abs(leg["front_f"][1]) > 0 else y1 - y0, 4)}})


def block_type(names: list[str], size, table: dict, shape: Optional[str] = None, extended: bool = True
               ) -> Optional[str]:
    """Furniture type from DXF block names (innermost first) by the keyword tables (``keyword_type``), resolved by
    the size table for the generic words BED / YATAK, TABLE / MASA and KOLTUK (armchair, sofa; an L-shaped outline:
    the corner sofa); None when no keyword matches."""
    for name in names:
        ftype = keyword_type(name, extended)
        if ftype is None:
            continue
        if ftype == "bed":
            return "bed_double" if fits(table, "bed_double", size) else "bed_single"
        if ftype == "table":
            for t in ("table_dining", "table_coffee", "desk"):
                if fits(table, t, size):
                    return t
            return "table_dining"
        if ftype == "seat":
            # KOLTUK: an armchair (M7) or, when the drawn piece is longer, a sofa; an L outline is a corner sofa.
            if shape == "L":
                return "sofa_corner"
            for t in ("armchair", "sofa"):
                if fits(table, t, size):
                    return t
            return "armchair"
        return ftype
    return None


def _block_chain(part: Cluster) -> Optional[str]:
    """The block chain that draws >= 60 % of a part's segments, or None."""
    chains = [s.stroke.block for s in part.segs if s.stroke.block]
    if not chains or len(chains) < 0.6 * len(part.segs):
        return None
    chain = max(set(chains), key=chains.count)
    return chain if chains.count(chain) >= 0.6 * len(part.segs) else None


def corner_back_front(centre, corners, wall_polys: list, theta: float) -> Optional[float]:
    """The front of an elongated piece standing in a corner: exactly two adjacent sides within ``FRONT_WALL_M`` of a
    wall, one of them the long side (>= ``CORNER_LONG_RATIO`` x the short side) -> the long side is the back. None
    otherwise. Only used for types whose back is their long side (``LONG_BACK_TYPES``: block-named pieces here, AI-typed
    pieces in ``core._apply_decision``), where the general rule (only one side near a wall) gives nothing (real02:
    washbasins and wardrobes drawn in a corner)."""
    sides = _sides(corners)
    near = near_wall_sides(sides, centre, wall_polys)
    if len(near) != 2 or (near[1] - near[0]) % 2 == 0:            # two adjacent sides, not two opposite ones
        return None
    lengths = {k: math.dist(*sides[k]) for k in near}
    long_k, short_k = sorted(near, key=lambda k: -lengths[k])
    if lengths[long_k] < CORNER_LONG_RATIO * lengths[short_k]:
        return None
    return _snap_deg(_outward_deg(sides[long_k], centre) + 180.0, theta)


STRAY_MAX = 2                      # at most this many straight lines are left out of a named block's footprint
CHAIR_RULE_TYPES: tuple[str, ...] = ("chair", "office_chair", "bar_stool", "armchair", "ottoman")


def trim_stray_lines(part: Cluster, ftype: str, table: dict, theta: float) -> Optional[tuple[tuple, str]]:
    """Milestone 12 (real03's ``klozet1``: a 1.15 m axis line through a 0.36 x 0.85 m toilet made it 1.145 x 0.356 m):
    the footprint of a named block without the straight lines that stick out of it (longest first, at most
    ``STRAY_MAX``), when that footprint fits the named type; ``(footprint, note)`` or None."""
    by_stroke: dict[str, list[Seg]] = {}
    for s in part.segs:
        by_stroke.setdefault(s.stroke.id, []).append(s)
    lines = sorted((sid for sid, ss in by_stroke.items() if len(ss) == 1 and not ss[0].curve and not ss[0].dot
                    and len(set(ss[0].pts)) == 2), key=lambda sid: (-by_stroke[sid][0].length, sid))
    left_out: list[str] = []
    for sid in lines[:STRAY_MAX]:
        left_out.append(sid)
        rest = [p for k, ss in by_stroke.items() if k not in left_out for s in ss for p in s.pts]
        if len(rest) < 3:
            return None
        fp = footprint(rest, theta)
        if fits(table, ftype, (fp[1], fp[2])):
            return fp, (f"{len(left_out)} straight line(s) drawn past the {ftype} ({', '.join(left_out)}: an axis or "
                        f"reference line) left out of its footprint")
    return None


def _unique_front(fronts: list[dict]) -> Optional[dict]:
    """The one deterministic front of ``front_candidates`` (rules that agree are merged there), else None."""
    return fronts[0] if len(fronts) == 1 else None


def _block_item(part: Cluster, fp, ctx: _Ctx, raster: bool, table: dict,
                lsh: Optional[dict] = None, wall_polys: Optional[list] = None,
                others: Optional[list] = None, extended: bool = True) -> Optional[FurnitureItem]:
    """A piece typed by its block name. Its front: the L outline's open corner for a corner sofa; else the unique
    deterministic front of ``front_candidates`` (§2.8: the only side near a wall is the back, a bed's pillows, a
    chair facing a table), else, for a type whose back is its long side, the corner rule (``corner_back_front``);
    else none (frontless types never get one). Block-named pieces are never asked (§3.3), so without this the drawn
    front was lost and the builder faced the piece by its footprint rotation alone (real02: every washbasin and two
    wardrobes faced the wall, a bed stood with its head in the room, toilets turned 90 deg)."""
    chain = _block_chain(part)
    if chain is None:
        return None
    names = list(reversed(chain.split("/")))
    ftype = block_type(names, (fp[1], fp[2]), table, "L" if lsh else None, extended)
    if ftype is None:
        return None
    trim_note = None
    if not lsh and not fits(table, ftype, (fp[1], fp[2])):
        trimmed = trim_stray_lines(part, ftype, table, ctx.theta)
        if trimmed is not None:
            fp, trim_note = trimmed
    front, rule = (lsh["front_deg"], None) if lsh and ftype == "sofa_corner" else (None, None)
    if front is None and ftype not in FRONTLESS_BLOCK_TYPES and wall_polys is not None:
        fronts = front_candidates(part.segs, fp[0], fp[4], wall_polys, list(others or []), ctx.theta, table)
        if ftype not in CHAIR_RULE_TYPES:
            # Milestone 12: "a chair faces the nearest table" is for seats; a toilet or washing machine named by its
            # block next to a table-sized piece is no chair (real03: toilets and washing machines faced sideways).
            fronts = [dict(c, rule="; ".join(r for r in c["rule"].split("; ") if not r.startswith("chair faces")))
                      for c in fronts if any(not r.startswith("chair faces") for r in c["rule"].split("; "))]
        found = _unique_front(fronts)
        if found is not None:
            front, rule = found["front_deg"], found["rule"]
            width, depth = size_rotation(fp[1], fp[2], fp[3], front)[0]
            if ftype in LONG_BACK_TYPES and width * CORNER_LONG_RATIO <= depth:
                front, rule = None, None          # its short end on the wall: the front is one of the long sides
        elif ftype in LONG_BACK_TYPES:
            front = corner_back_front(fp[0], fp[4], wall_polys, ctx.theta)
            rule = "corner: the long side against a wall is the back" if front is not None else None
    size, rotation = size_rotation(fp[1], fp[2], fp[3], front)
    box = ctx.box(fp[4])
    ok = fits(table, ftype, (fp[1], fp[2]))
    note = None if ok else f"block name says {ftype} but {fp[1]:.2f} x {fp[2]:.2f} m does not fit its size range"
    note = "; ".join(x for x in (trim_note, note) if x) or None
    if rule:
        note = "; ".join(x for x in (note, f"front {front:g} deg: {rule}") if x)
    ev = ctx.evidence(part.stroke_ids(), confidence=0.9, raster=raster, box=box, note=note)
    ev["block"] = chain
    item = FurnitureItem(type=ftype, type_raw=chain, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=round(front, 3) if front is not None else None, box=box,
                         entity=part.stroke_ids()[0], evidence=ev, status="verified" if ok else "unverified",
                         type_method="block_name")
    if rule:
        item.details["front_rule"] = rule
    return item


# --------------------------------------------------------------------------
# Milestone 10: L outlines and named block instances
# --------------------------------------------------------------------------

def l_shape(cl: Cluster, theta: float) -> Optional[dict]:
    """An L-shaped outline in the plan's aligned frame (docs/milestone10.md §1.1: the drawn corner sofas of real02's
    basement): the largest top contour fills its box but for one open corner (>= 15 % of the box, the rest open
    <= 8 %: rounded or stepped corners), both arms 0.5-1.3 m deep. The arm along the longer side is the main seat,
    the other arm the chaise (it runs the full depth of the box); the open corner is the front. ``chaise_side`` is
    seen from the front, i.e. by someone standing there and facing the piece. Returns ``{"fp", "front_deg",
    "chaise_side", "chaise_depth", "seat_depth", "chaise_width", "note"}`` (``fp`` as ``footprint``: the box) or
    None."""
    tops = top_contours(cl)
    if not tops:
        return None
    to_f, from_f = _frame(theta)
    pts = [to_f(p) for s in cl.segs for p in s.pts]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    w, h = x1 - x0, y1 - y0
    if min(w, h) < 2 * L_ARM_M[0]:
        return None
    outline = max(tops, key=lambda tm: tm[0].area)[0]
    poly = Polygon([to_f(q) for q in outline.exterior.coords])
    if not poly.is_valid:
        poly = poly.buffer(0)
    b = poly.bounds
    if max(abs(b[0] - x0), abs(b[1] - y0), abs(b[2] - x1), abs(b[3] - y1)) > L_BOX_M:
        return None
    box = sbox(x0, y0, x1, y1)
    rest = sorted(getattr(box.difference(poly), "geoms", [box.difference(poly)]), key=lambda g: -g.area)
    if not rest or rest[0].is_empty or rest[0].area < L_NOTCH_SHARE * box.area:
        return None
    if sum(g.area for g in rest[1:]) > L_REST_SHARE * box.area:
        return None
    nx0, ny0, nx1, ny1 = rest[0].bounds
    left, right = nx0 - x0 <= L_BOX_M, x1 - nx1 <= L_BOX_M
    bottom, top = ny0 - y0 <= L_BOX_M, y1 - ny1 <= L_BOX_M
    if left == right or bottom == top:
        return None                                   # the open part is not one corner
    arm_x, arm_y = h - (ny1 - ny0), w - (nx1 - nx0)  # depth of the arm along x (full width), along y (full height)
    if not (L_ARM_M[0] <= arm_x <= L_ARM_M[1] and L_ARM_M[0] <= arm_y <= L_ARM_M[1]):
        return None
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    if w >= h:                                        # main seat along x, the chaise is the arm along y
        front = (0.0, -1.0) if bottom else (0.0, 1.0)
        seat, chaise_w, chaise_d = arm_x, arm_y, h
        chaise_c = ((x1 - arm_y / 2.0) if left else (x0 + arm_y / 2.0), cy)
    else:
        front = (-1.0, 0.0) if left else (1.0, 0.0)
        seat, chaise_w, chaise_d = arm_y, arm_x, w
        chaise_c = (cx, (y0 + arm_x / 2.0) if top else (y1 - arm_x / 2.0))
    look = (-front[0], -front[1])                     # the viewer in front faces the piece
    right_hand = (look[1], -look[0])
    side = "right" if (chaise_c[0] - cx) * right_hand[0] + (chaise_c[1] - cy) * right_hand[1] > 0 else "left"
    fx, fy = from_f(front)
    front_deg = round(math.degrees(math.atan2(fy, fx)) % 360.0, 3)
    corners = [from_f(q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    fp = (from_f((cx, cy)), w, h, theta % 180.0, corners)
    note = (f"L outline {max(w, h):.2f} x {min(w, h):.2f} m: main seat {seat:.2f} m deep, chaise {chaise_w:.2f} x "
            f"{chaise_d:.2f} m on the {side} (seen from the front), open corner {nx1 - nx0:.2f} x {ny1 - ny0:.2f} m")
    return {"fp": fp, "front_deg": front_deg, "chaise_side": side, "chaise_depth": round(chaise_d, 4),
            "seat_depth": round(seat, 4), "chaise_width": round(chaise_w, 4), "note": note}


def l_details(lsh: dict) -> dict:
    """``FurnitureItem.details`` of an L-shaped piece: ``l_outline`` = the building fields of a corner sofa
    (``chaise_side``, ``chaise_depth``, ``seat_depth``, ``chaise_width``; docs/milestone10.md §1.6b row 15). Not
    ``shape`` itself: the schema allows ``shape: L`` only on a ``sofa_corner``, and a candidate's type is decided
    later (the pipeline writes ``shape: L`` and these fields when the piece is a ``sofa_corner``)."""
    return {"l_outline": {"chaise_side": lsh["chaise_side"], "chaise_depth": lsh["chaise_depth"],
                          "seat_depth": lsh["seat_depth"], "chaise_width": lsh["chaise_width"]}}


def _instance_key(part: Cluster) -> Optional[str]:
    """The named block instance (``block_instance``) that draws every segment of a part, or None."""
    keys = set()
    for s in part.segs:
        if not s.stroke.block:
            return None
        key, named = block_instance(s.stroke)
        if not named:
            return None
        keys.add(key)
    return keys.pop() if len(keys) == 1 else None


def named_instances(infos: list[dict], table: dict, theta: float, notes: list) -> list[dict]:
    """One named piece per named block instance (Milestone 10, real02): a detail part (< 0.20 m across) that the
    20 mm clustering split off (a WC's flush plate) joins the instance's largest part; of several furniture-sized
    parts (an armchair block with its footstool) and of an instance whose whole footprint does not fit its named type
    (a bed block drawn with its two nightstands, split geometrically) the largest part that fits takes the name and
    the others are asked like unnamed strokes (``no_name``). Notes for each."""
    groups: dict[str, list[dict]] = {}
    out: list[dict] = []
    for info in infos:
        key = _instance_key(info["part"]) if not info.get("l") else None
        if key is None:
            out.append(info)
        else:
            groups.setdefault(key, []).append(info)
    for key, items in groups.items():
        small = [it for it in items if min(it["size"]) < DETAIL_M]
        big = [it for it in items if it not in small]
        if small and big:
            # A detail of the instance (a WC's flush plate) joins its largest piece.
            host = max(big, key=lambda it: it["size"][0] * it["size"][1])
            part = Cluster(host["part"].segs + [s for it in small for s in it["part"].segs])
            fp = footprint([q for s in part.segs for q in s.pts], theta)
            note = f"{len(small) + 1} drawn parts of one block instance are one piece"
            notes.append(f"{key.split('|')[0]} at ({fp[0][0]:.2f}, {fp[0][1]:.2f}): {note}")
            items = [it for it in big if it is not host] + [
                {"part": part, "n": 1, "fp": fp, "size": (fp[1], fp[2]), "poly": Polygon(fp[4]), "note": note}]
        if len(items) > 1:
            out.extend(_pick_named(items, table, notes))
            continue
        for info in items:
            out.extend(_split_named(info, table, theta, notes))
    return out


def _pick_named(items: list[dict], table: dict, notes: list) -> list[dict]:
    """Several furniture-sized parts of one named instance (an armchair block with its footstool): the largest part
    that fits the named type takes the name, the others are asked; none fits -> each keeps the name (unverified)."""
    chain = _block_chain(items[0]["part"])
    names = list(reversed(chain.split("/"))) if chain else []
    named = [it for it in items if names and block_type(names, it["size"], table, extended=False) is not None and
             fits(table, block_type(names, it["size"], table, extended=False), it["size"])]
    if not named:
        return items
    keep = max(named, key=lambda it: it["size"][0] * it["size"][1])
    note = f"block {chain} holds {len(items)} drawn pieces: the {keep['size'][0]:.2f} x {keep['size'][1]:.2f} m " \
           f"piece takes the name, the others are asked"
    notes.append(note)
    keep["note"] = "; ".join(x for x in (keep.get("note"), note) if x)
    for it in items:
        if it is not keep:
            it["no_name"] = True
            it["note"] = f"drawn inside block {chain} next to its named piece; type asked"
    return items


def _split_named(info: dict, table: dict, theta: float, notes: list) -> list[dict]:
    chain = _block_chain(info["part"])
    if chain is None:
        return [info]
    names = list(reversed(chain.split("/")))
    ftype = block_type(names, info["size"], table, extended=False)
    if ftype is None or ftype in ("stair",) or fits(table, ftype, info["size"]):
        return [info]
    if ftype in TABLE_TYPES:
        # Milestone 11 (U10): a table block drawn with its chairs (real02's "masa": a 3.35 m table and 10 chairs read
        # as one 3.35 x 1.57 m table) -> the named table and one chair per chair part, each facing the table.
        split = split_table_chairs(info["part"], table, theta)
        if split is not None:
            tfp = footprint(list(split["table_poly"].exterior.coords)[:-1], theta)
            note = (f"block {chain} ({info['size'][0]:.2f} x {info['size'][1]:.2f} m) holds a table and "
                    f"{len(split['chairs'])} chairs: split (M11)")
            notes.append(note)
            out = [{"part": split["table"], "n": 1, "fp": tfp, "size": (tfp[1], tfp[2]), "poly": Polygon(tfp[4]),
                    "note": note}]
            for chair in split["chairs"]:
                cfp, front = chair_footprint(chair, split["table_poly"], theta)
                out.append({"part": chair, "n": 1, "fp": cfp, "size": (cfp[1], cfp[2]), "poly": Polygon(cfp[4]),
                            "rule_type": "chair", "front": front,
                            "note": f"chair of block {chain}, facing the table (M11 split)"})
            return out
    subs = [sub for sub, n in _split_geometric(info["part"], table) if n == 1]
    if len(subs) < 2:
        return [info]
    parts = []
    for sub in subs:
        fp = footprint([q for s in sub.segs for q in s.pts], theta)
        parts.append({"part": sub, "n": 1, "fp": fp, "size": (fp[1], fp[2]), "poly": Polygon(fp[4])})
    named = [pt for pt in parts if block_type(names, pt["size"], table, extended=False) is not None and
             fits(table, block_type(names, pt["size"], table, extended=False), pt["size"])]
    if not named:
        return [info]
    keep = max(named, key=lambda pt: pt["fp"][1] * pt["fp"][2])
    note = (f"block {chain} ({info['size'][0]:.2f} x {info['size'][1]:.2f} m) holds {len(parts)} drawn pieces: the "
            f"{keep['size'][0]:.2f} x {keep['size'][1]:.2f} m piece takes the name, the others are asked")
    notes.append(note)
    keep["note"] = note
    for pt in parts:
        if pt is not keep:
            pt["no_name"] = True
            pt["note"] = f"drawn inside block {chain} next to its named piece; type asked"
    return parts


# --------------------------------------------------------------------------
# Milestone 11: group splitting (docs/milestone11.md §1.2 U8, U10, step 4)
# --------------------------------------------------------------------------
#
# A drawn group read as one piece is split into its pieces when the drawing shows them: a dining table with the
# chairs around it (real02's 10-seat "masa" block and the open kitchen's MASA111), and a kitchen counter run drawn
# as closed outlines along the walls with the hob and sink blocks on it (real02's kitchens, one 4.6 x 2.9 m cluster).
# Only pieces that were never asked are split (named blocks, composites, oversize clusters): the AI candidates and
# their keys stay as they were, so the answers of earlier runs still apply. Parts of a split that no rule or block
# name types stay unknown and are not asked (the agent types them, docs/milestone11.md §5).

TABLE_TYPES = ("table_dining", "table_coffee")
CHAIR_MAX_M = 0.8              # a chair part is at most this large across ...
CHAIR_REACH_M = 0.4            # ... and stands within this of the table outline
CHAIR_DEPTH_M = 0.45           # a chair whose visible part is shallower is tucked under the table to this depth
KITCHEN_APPLIANCES = ("stove", "sink_kitchen", "fridge")
OUTLINE_CLOSE_M = 0.3          # an open counter outline whose ends are this close is closed
COUNTER_LEG_FILL = 0.85        # a leg fills >= 85 % of its box
COUNTER_COVER = 0.9            # the legs and islands cover >= 90 % of the outline
ISLAND_MIN_M2 = 0.25


def split_table_chairs(part: Cluster, table: dict, theta: float) -> Optional[dict]:
    """``{"table": Cluster, "table_poly", "chairs": [Cluster]}`` when ``part`` is a table outline (its largest
    top-level closed contour fits a table type) with at least two chair-sized parts within ``CHAIR_REACH_M`` around
    it and nothing else; else None."""
    tops = top_contours(part)
    if not tops:
        return None
    tpoly, tidx = max(tops, key=lambda tm: tm[0].area)
    sides = _rect_sides(tpoly)
    if not any(fits(table, t, sides) for t in TABLE_TYPES):
        return None
    own = set(tidx)
    inner = tpoly.buffer(-0.02)
    inside, rest = [], []
    for k, s in enumerate(part.segs):
        mid = s.geom if s.dot else s.geom.centroid
        (inside if k in own or inner.contains(mid) else rest).append(s)
    subs = [sub for sub in clusters_of(rest, CLUSTER_M) if max(sub.size(theta)) >= DETAIL_M]
    if len(subs) < 2:
        return None
    for sub in subs:
        w, h = sub.size(theta)
        if max(w, h) > CHAIR_MAX_M or sub.geom.distance(tpoly) > CHAIR_REACH_M:
            return None
    small = [s for s in rest if not any(s in sub.segs for sub in subs)]
    return {"table": Cluster(inside + small), "table_poly": tpoly, "chairs": subs}


def chair_footprint(chair: Cluster, tpoly, theta: float) -> tuple[tuple, float]:
    """(footprint as ``footprint`` returns it, front_deg) of a chair beside a table: its visible box in the plan's
    aligned frame, grown towards the table to ``CHAIR_DEPTH_M`` when shallower (the seat under the table edge),
    facing the table."""
    to_f, from_f = _frame(theta)
    x0, y0, x1, y1 = chair.bounds(theta)
    tb = [to_f(p) for p in tpoly.exterior.coords]
    tx0, ty0 = min(p[0] for p in tb), min(p[1] for p in tb)
    tx1, ty1 = max(p[0] for p in tb), max(p[1] for p in tb)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # The side of the table the chair stands on: the axis on which it lies outside the table's extent.
    out_x = max(tx0 - cx, cx - tx1, 0.0)
    out_y = max(ty0 - cy, cy - ty1, 0.0)
    if out_x >= out_y:
        d = (1.0, 0.0) if cx < tx0 else (-1.0, 0.0)
        depth = x1 - x0
        if depth < CHAIR_DEPTH_M:
            if d[0] > 0:
                x1 = x0 + CHAIR_DEPTH_M
            else:
                x0 = x1 - CHAIR_DEPTH_M
    else:
        d = (0.0, 1.0) if cy < ty0 else (0.0, -1.0)
        depth = y1 - y0
        if depth < CHAIR_DEPTH_M:
            if d[1] > 0:
                y1 = y0 + CHAIR_DEPTH_M
            else:
                y0 = y1 - CHAIR_DEPTH_M
    corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    fd = from_f(d)
    front = _snap_deg(math.degrees(math.atan2(fd[1], fd[0])), theta)
    return footprint(corners, theta), front


def _rule_item(segs: list, fp, ftype: str, front: Optional[float], ctx: _Ctx, raster: bool, table: dict,
               note: str, details: Optional[dict] = None) -> FurnitureItem:
    """A piece typed by a Milestone 11 split rule (``type_method: rule``); ``verified`` when its footprint fits the
    type's size range."""
    size, rotation = size_rotation(fp[1], fp[2], fp[3], front)
    box = ctx.box(fp[4])
    ids = sorted({s.stroke.id for s in segs}, key=_id_key)
    ok = fits(table, ftype, (fp[1], fp[2]))
    full = note if ok else f"{note}; {fp[1]:.2f} x {fp[2]:.2f} m does not fit the {ftype} size range"
    ev = ctx.evidence(ids, confidence=0.85, raster=raster, box=box, note=full)
    return FurnitureItem(type=ftype, type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=round(front, 3) if front is not None else None, box=box, entity=ids[0], evidence=ev,
                         status="verified" if ok else "unverified", type_method="rule",
                         details=dict(details or {}, split_rule=note))


def table_chair_items(split: dict, ctx: _Ctx, raster: bool, table: dict, named: Optional[FurnitureItem] = None
                      ) -> list[FurnitureItem]:
    """The table (``named``: the block-named table, else a rule table) and one chair per part, facing the table."""
    tpoly = split["table_poly"]
    out = []
    note = f"table + {len(split['chairs'])} chairs drawn as one group: split (M11)"
    if named is None:
        fp = footprint(list(tpoly.exterior.coords)[:-1], ctx.theta)
        ttype = next((t for t in TABLE_TYPES if fits(table, t, (fp[1], fp[2]))), "table_dining")
        out.append(_rule_item(split["table"].segs, fp, ttype, None, ctx, raster, table, note))
    else:
        out.append(named)
    for chair in split["chairs"]:
        fp, front = chair_footprint(chair, tpoly, ctx.theta)
        out.append(_rule_item(chair.segs, fp, "chair", front, ctx, raster, table,
                              "chair of the drawn table + chairs group, facing the table (M11 split)"))
    return out


def _appliance_type(s: Seg, extended: bool = False) -> Optional[str]:
    # The M11 kitchen split keeps its M7-M11 words (Milestone 12: the parts of earlier rounds stay as they were).
    for name in reversed((s.stroke.block or "").split("/")):
        t = keyword_type(name, extended) if name else None
        if t in KITCHEN_APPLIANCES:
            return t
    return None


def _outline_polygons(segs: list[Seg], to_f) -> list[tuple[Polygon, list[Seg]]]:
    """Closed (or nearly closed) loose polylines of a cluster as polygons in the aligned frame, with their segments."""
    by_stroke: dict[str, list[Seg]] = {}
    for s in segs:
        if s.stroke.block or s.curve or s.dot or s.stroke.kind != "polyline":
            continue
        by_stroke.setdefault(s.stroke.id, []).append(s)
    out = []
    for sid, ss in sorted(by_stroke.items()):
        pts = [to_f(p) for p in ss[0].stroke.pts]
        if len(pts) < 4:
            continue
        if not ss[0].stroke.closed and math.dist(pts[0], pts[-1]) > OUTLINE_CLOSE_M:
            continue
        poly = Polygon(pts).buffer(0)
        if poly.is_empty or poly.geom_type != "Polygon" or poly.area < 0.3:
            continue
        out.append((poly, ss))
    return out


def counter_legs(poly: Polygon, faces: list[dict], cover: float = COUNTER_COVER, short_corner: bool = False
                 ) -> Optional[tuple[list[dict], list[tuple]]]:
    """A counter outline (aligned frame) as legs along wall faces and free blocks (a peninsula or island):
    ``([{"rect": (x0, y0, x1, y1), "front_f", "depth", "length"}], [(x0, y0, x1, y1)])``, or None when it is no
    counter run (no leg, or the legs and blocks cover < ``cover`` of it). A leg is the outline within 0.75 m of a wall
    face it lies on, 0.45-0.75 m deep and filling its box; a corner goes to the longer leg. Milestone 12 re-read
    (``short_corner``): where the longer leg stops short of the corner, the other leg keeps its full-depth part."""
    from shapely.geometry import box as sbox

    legs = []
    coords = list(poly.exterior.coords)
    for f in faces:
        lo, hi = f["lo"], f["hi"]
        k = 0 if f["axis"] == "v" else 1
        # The leg's depth is the distance from the face to an outline corner (0.45-0.75 m): the strip stops at the
        # leg's front edge, so a perpendicular leg running away from the wall is not taken in.
        depths = sorted({round((p[k] - f["pos"]) * f["normal"], 4) for p in coords
                         if COUNTER_DEPTH_M[0] <= (p[k] - f["pos"]) * f["normal"] <= COUNTER_DEPTH_M[1] + 0.02})
        for reach in depths:
            a, b = sorted((f["pos"], f["pos"] + f["normal"] * reach))
            strip = sbox(a, lo, b, hi) if f["axis"] == "v" else sbox(lo, a, hi, b)
            part = poly.intersection(strip)
            if part.is_empty or part.area < 0.1:
                continue
            x0, y0, x1, y1 = part.bounds
            on_face = (abs((x0 if f["normal"] > 0 else x1) - f["pos"]) if f["axis"] == "v"
                       else abs((y0 if f["normal"] > 0 else y1) - f["pos"]))
            depth = (x1 - x0) if f["axis"] == "v" else (y1 - y0)
            length = (y1 - y0) if f["axis"] == "v" else (x1 - x0)
            if on_face > COUNTER_END_M or depth < COUNTER_DEPTH_M[0] or length < 0.3:
                continue
            if part.area < COUNTER_LEG_FILL * (x1 - x0) * (y1 - y0):
                continue
            front = (f["normal"], 0.0) if f["axis"] == "v" else (0.0, f["normal"])
            legs.append({"rect": (x0, y0, x1, y1), "front_f": front, "depth": depth, "length": length})
            break
    if not legs:
        return None
    legs.sort(key=lambda lg: (-lg["length"], lg["rect"]))
    kept: list[dict] = []
    for lg in legs:
        r = sbox(*lg["rect"])
        for k in kept:
            r = r.difference(sbox(*k["rect"]))
        r = r.buffer(-0.005, join_style="mitre").buffer(0.005, join_style="mitre")  # no slivers (mm offsets)
        if r.is_empty:
            continue
        r = max(getattr(r, "geoms", [r]), key=lambda g: g.area)
        x0, y0, x1, y1 = r.bounds
        if r.area < 0.9 * (x1 - x0) * (y1 - y0):
            # Milestone 12 (real03): a longer leg that stops short of the corner leaves an L; the leg is its part of
            # full depth (``_full_depth``), the corner piece goes with it only where the leg reaches.
            full = _full_depth(r, bool(lg["front_f"][0])) if short_corner else None
            if full is None:
                continue
            x0, y0, x1, y1 = full
        length = (y1 - y0) if lg["front_f"][0] else (x1 - x0)
        if length < 0.3:
            continue
        kept.append(dict(lg, rect=(x0, y0, x1, y1), length=length))
    if not kept:
        return None
    rest = poly.difference(unary_union([sbox(*k["rect"]) for k in kept]))
    rest = rest.buffer(-0.005, join_style="mitre").buffer(0.005, join_style="mitre")   # no slivers along the legs
    blocks = []
    for g in getattr(rest, "geoms", [rest]):
        if g.is_empty or g.area < ISLAND_MIN_M2:
            continue
        x0, y0, x1, y1 = g.bounds
        if g.area >= 0.85 * (x1 - x0) * (y1 - y0) and min(x1 - x0, y1 - y0) >= COUNTER_DEPTH_M[0]:
            blocks.append((x0, y0, x1, y1))
    covered = sum(sbox(*k["rect"]).intersection(poly).area for k in kept) + sum(
        sbox(*b).intersection(poly).area for b in blocks)
    if covered < cover * poly.area:
        return None
    return kept, blocks


def _full_depth(r, along_y: bool) -> Optional[tuple[float, float, float, float]]:
    """The longest box of ``r``'s full depth (across the leg) along the leg's axis (y for a leg on a vertical wall
    face), between two of ``r``'s vertex coordinates; None when there is none."""
    x0, y0, x1, y1 = r.bounds
    cuts = sorted({round(p[1] if along_y else p[0], 6) for p in r.exterior.coords})
    inside = r.buffer(0.002, join_style="mitre")
    best = None
    for i, a in enumerate(cuts):
        for b in cuts[i + 1:]:
            box = (x0, a, x1, b) if along_y else (a, y0, b, y1)
            if (best is None or b - a > best[0]) and inside.contains(sbox(*box)):
                best = (b - a, box)
    return best[1] if best else None


def kitchen_split(cl: Cluster, walls: list, openings: list, theta: float) -> Optional[dict]:
    """``{"legs": [counter_rule-shaped leg dicts], "blocks": [(rect_f, segs)], "rest": [Seg]}``: a cluster whose loose
    closed outlines are counter runs along the walls (``counter_legs``; one leg is enough when the cluster holds a
    stove, sink or fridge block, else an L or U along two walls); ``rest`` = every other segment (the appliance
    blocks, stools, chairs). None otherwise."""
    appliance = any(_appliance_type(s) for s in cl.segs)
    to_f, _from_f = _frame(theta)
    faces = _wall_faces(walls, openings, to_f)
    legs, blocks, used = [], [], set()
    for poly, ss in _outline_polygons(cl.segs, to_f):
        found = counter_legs(poly, faces)
        if found is None or (not appliance and len(found[0]) < 2):
            # Without a hob, sink or fridge block only an L or U run along two walls is a counter (one 0.6 m deep
            # rectangle along one wall may be a wardrobe or a shelf).
            continue
        for lg in found[0]:
            legs.append({"rect_f": lg["rect"], "front_f": lg["front_f"], "segs": ss, "leg": ss[0],
                         "length": lg["length"], "depth": lg["depth"]})
        blocks += [(b, ss) for b in found[1]]
        used.update(id(s) for s in ss)
    if not legs:
        return None
    return {"legs": legs, "blocks": blocks, "rest": [s for s in cl.segs if id(s) not in used]}


def split_by_instance(segs: list[Seg]) -> list[Cluster]:
    """One part per DXF block instance (``block_instance``) and the loose strokes clustered at 20 mm."""
    groups: dict[str, list[Seg]] = {}
    loose = []
    for s in segs:
        if s.stroke.block:
            groups.setdefault(block_instance(s.stroke)[0], []).append(s)
        else:
            loose.append(s)
    parts = [Cluster(v) for _k, v in sorted(groups.items())]
    return parts + clusters_of(loose, CLUSTER_M)


def kitchen_items(split: dict, walls: list, ctx: _Ctx, raster: bool, table: dict, wall_polys: list,
                  notes: list) -> list[FurnitureItem]:
    """The counter legs (``_counter_item``), the free blocks (a peninsula or island: ``kitchen_island``) and the rest
    by block instance: a named block (hob, sink) by its name, every other part unknown and not asked."""
    out = [_counter_item(leg, walls, ctx, raster) for leg in split["legs"]]
    for item in out:
        item.evidence["note"] = "kitchen counter run drawn as a closed outline along the walls (M11 split)"
    _to_f, from_f = _frame(ctx.theta)
    for (x0, y0, x1, y1), ss in split["blocks"]:
        corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        fp = footprint(corners, ctx.theta)
        ftype = "kitchen_island" if fits(table, "kitchen_island", (fp[1], fp[2])) else "kitchen_counter"
        out.append(_rule_item(ss, fp, ftype, None, ctx, raster, table,
                              "free block of a kitchen counter outline (peninsula or island, M11 split)"))
    runs = []
    for leg in split["legs"]:
        x0, y0, x1, y1 = leg["rect_f"]
        fdir = from_f(leg["front_f"])
        runs.append((Polygon([from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]),
                     round(math.degrees(math.atan2(fdir[1], fdir[0])) % 360.0, 3)))
    for sub in split_by_instance(split["rest"]):
        w, h = sub.size(ctx.theta)
        if max(w, h) < DETAIL_M or short_side(sub.segs) < LINE_DETAIL_M:
            continue
        fp = footprint([p for s in sub.segs for p in s.pts], ctx.theta)
        poly = Polygon(fp[4])
        run = next(((rp, fr) for rp, fr in runs if rp.contains(Point(fp[0]))), None)
        item = _block_item(sub, fp, ctx, raster, table, None, wall_polys, [])
        if item is not None and item.front_deg is None and run is not None and item.type in KITCHEN_APPLIANCES:
            # A hob or sink set into a counter leg faces the way the leg faces.
            item = _rule_item(sub.segs, fp, item.type, run[1], ctx, raster, table,
                              f"{item.type} block {item.type_raw} on a counter leg: the leg's front (M11 split)")
            item.type_method, item.type_raw = "block_name", _block_chain(sub)
        if item is None:
            inside = run is not None and poly.area > 0 and poly.intersection(run[0]).area >= 0.8 * poly.area
            if inside:
                item = _unknown(sub, fp, ctx, raster, "detail inside a kitchen counter leg (an appliance front or "
                                "drawers, M11 split): not built", {"split": "kitchen", "build": False})
            else:
                item = _unknown(sub, fp, ctx, raster, "part of a kitchen counter cluster (M11 split): not asked, the "
                                "agent types it", {"split": "kitchen"})
        out.append(item)
    notes.append(f"kitchen counter cluster split (M11): {len(split['legs'])} counter legs, "
                 f"{len(split['blocks'])} free blocks, {len(out) - len(split['legs']) - len(split['blocks'])} other "
                 f"parts")
    return out


def _candidate(part: Cluster, fp, ctx: _Ctx, raster: bool, faces, fronts: list, types: list, n: int) -> dict:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    key = f"sym_{ctx.level_id}_{n:03d}" if ctx.level_id else f"sym_{n:03d}"
    room_type, label = _face_info(faces, fp[0])        # apply_room_checks refreshes it
    ev = ctx.evidence(part.stroke_ids(), raster=raster, box=box)
    item = FurnitureItem(type="unknown", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=part.stroke_ids()[0], evidence=ev, status="unverified",
                         type_method="none", details={"candidate_key": key, "front_candidates": fronts})
    xs = [p[0] for s in part.segs for p in s.pts]
    ys = [p[1] for s in part.segs for p in s.pts]
    return {"key": key, "footprint": {"center": list(_r(fp[0])), "size": list(size), "rotation_deg": rotation},
            "strokes": [[list(_r(p)) for p in s.pts] for s in part.segs],
            "bbox": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
            "room_hint": label or room_type, "front_candidates": fronts, "fits": types, "item": item}


def raster_clusters(segs: list[Seg], dist: float = CLUSTER_M, px: float = 0.01) -> list[Cluster]:
    """Clusters of strokes closer than about ``dist``, from connected components of the strokes drawn on a ``px``
    raster with a line width reaching ``dist``. Used for site decor, where dense plant fills (real01: 9 x ~2,500
    segments) make the exact pairwise clustering slow and stroke-exact grouping is not needed."""
    import cv2

    if not segs:
        return []
    xs = [p[0] for s in segs for p in s.pts]
    ys = [p[1] for s in segs for p in s.pts]
    x0, y0 = min(xs) - 3 * px, min(ys) - 3 * px
    w = int((max(xs) - x0) / px) + 4
    h = int((max(ys) - y0) / px) + 4
    while w * h > 6e7:
        px *= 2.0
        w = int((max(xs) - x0) / px) + 4
        h = int((max(ys) - y0) / px) + 4
    img = np.zeros((h, w), np.uint8)
    thick = max(1, int(math.ceil(dist / px)))
    polys = []
    for s in segs:
        arr = np.array([[int((p[0] - x0) / px), int((p[1] - y0) / px)] for p in s.pts], np.int32)
        polys.append(arr)
    cv2.polylines(img, polys, False, 255, thick, cv2.LINE_8)
    n, lab = cv2.connectedComponents(img, connectivity=8)
    groups: dict = {}
    for s, arr in zip(segs, polys):
        c, r = arr[0]
        groups.setdefault(int(lab[r, c]), []).append(s)
    return [Cluster(v) for v in groups.values()]


def _site_decor(segs: list[Seg], ctx: _Ctx, raster: bool, notes: list, wall_geom=None) -> list[dict]:
    """Clusters outside the building: green fills or radial clusters -> plant; edge lines -> not decor; else other.
    Footprints leave out the parts of strokes lying on a wall face (an edge line continuing a house face)."""
    clusters = raster_clusters(segs)
    near = wall_geom.buffer(OUTLINE_NEAR_M, join_style=2) if wall_geom is not None and not wall_geom.is_empty else None
    out = []
    lines = 0
    for cl in clusters:
        w, h = cl.size()
        if max(w, h) < DETAIL_M:
            continue
        pts = [p for s in cl.segs for p in s.pts]
        if near is not None:
            clipped = []
            for s in cl.segs:
                g = s.geom.difference(near) if s.geom.intersects(near) else s.geom
                for part in getattr(g, "geoms", [g]):
                    if not part.is_empty:
                        clipped.extend(part.coords)
            pts = clipped or pts
        fp = footprint(pts, ctx.theta)
        if min(fp[1], fp[2]) < 0.05 or max(fp[1], fp[2]) > MAX_SIDE_M:
            lines += 1                                   # a boundary, edge or extension line, not an object
            continue
        fills = [s.stroke.fill for s in cl.segs if s.stroke.fill is not None]
        green = [f for f in fills if f[1] >= f[0] + 0.05 and f[1] >= f[2] + 0.05]
        kind = "plant" if fills and len(green) >= 0.3 * len(fills) else ("plant" if _radial(cl) else "other")
        box = ctx.box(fp[4])
        item = {"kind": kind, "center": list(_r(fp[0])), "size": [round(fp[1], 4), round(fp[2], 4)],
                "evidence": [ctx.evidence(cl.stroke_ids(), raster=raster, box=box)], "box": box}
        out.append(item)
    out.sort(key=lambda d: (d["center"][1], d["center"][0]))
    for n, item in enumerate(out, start=1):
        if ctx.level_id:
            item["id"] = f"sd_{ctx.level_id}_{n:03d}"
    if lines:
        notes.append(f"{lines} site edge or boundary line groups outside the building (not decor)")
    return out


def _radial(cl: Cluster) -> bool:
    """>= 8 straight strokes whose lines pass within 5 % of the cluster size of its centre (a drawn tree/plant)."""
    b = cl.bounds()
    c = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    tol = 0.05 * max(b[2] - b[0], b[3] - b[1])
    n = 0
    for s in cl.segs:
        if s.curve or s.dot:
            continue
        a, q = s.pts[0], s.pts[-1]
        length = math.dist(a, q)
        if length < 0.2 * max(b[2] - b[0], b[3] - b[1]):
            continue
        d = abs((q[0] - a[0]) * (a[1] - c[1]) - (a[0] - c[0]) * (q[1] - a[1])) / length
        if d <= tol:
            n += 1
    return n >= 8


# --------------------------------------------------------------------------
# Milestone 12 (docs/milestone12.md §4.1 D7, track R): non-furniture symbols and the deeper re-read
# --------------------------------------------------------------------------
#
# What the drawing says about a stroke before its shape: a layer whose name says door, text, area outline, axis,
# section, level mark, wall, structure, view line or services holds no furniture (real03: the "MYD - IZ-1" trace
# lines along the facades and the "MYD - ALAN-NET" area outlines chained whole living rooms into 5-13 m clusters;
# door details on "MYD - KAPI" and "Pkapı" were typed console tables and shoe cabinets by both AI passes). Strong
# shapes say what a drawn symbol is: a small circle with a short number inside is a room-number tag, a quarter arc
# with its leaf is a door swing. Symbols are recorded (``building["symbols"]`` by ``reading.read_furniture``) and
# never built (CLAUDE.md: "removed only when clearly not furniture, logged with the plan crop as evidence").
#
# The re-read (``reread``) takes a cluster nobody typed (an oversized cluster, a composite that fits no type, an AI
# candidate still unknown after its answers) apart: symbol strokes out, then one part per block instance and per
# connected stroke group, each typed on its own (block name, stair, counter run, table + chairs). Parts that no rule
# types are asked as extra questions with content keys (``extra_key``): the keys and input hashes of the questions of
# earlier rounds stay as they were, so their answers still apply.

SYMBOL_KINDS: tuple[str, ...] = ("level_mark", "room_number", "north_arrow", "axis_bubble", "section_mark",
                                 "door_arc", "dimension_outline", "text_frame", "other")
# Words of a layer name (folded, upper case; keys of up to three letters only as a whole word, longer ones anywhere
# in a word: "Pkapı" is a door layer) -> what its strokes are. Furniture words win (a sanitary layer "Pvitrifiye").
FURNITURE_LAYER_WORDS: tuple[str, ...] = ("TEFRIS", "MOBILYA", "FURN", "VITRIFIYE", "SIHHI", "SANITARY", "FIXTURE",
                                          "PLUMB", "APPLIANCE", "EQUIP", "MUTFAK", "KITCHEN")
LAYER_WORDS: tuple[tuple[str, str], ...] = (
    ("KOTA", "dimension_outline"), ("KOT", "level_mark"), ("LEVEL", "level_mark"),
    ("ALAN", "dimension_outline"), ("AREA", "dimension_outline"), ("OLCU", "dimension_outline"),
    ("DIM", "dimension_outline"),
    ("TEXT", "text_frame"), ("YAZI", "text_frame"), ("ETIKET", "text_frame"), ("TAG", "text_frame"),
    ("ANNO", "text_frame"), ("NOTE", "text_frame"),
    ("AKS", "axis_bubble"), ("AXIS", "axis_bubble"), ("GRID", "axis_bubble"),
    ("KESIT", "section_mark"), ("SECTION", "section_mark"), ("NORTH", "north_arrow"), ("KUZEY", "north_arrow"),
    ("KAPI", "door"), ("DOOR", "door"), ("PENCERE", "door"), ("WINDOW", "door"), ("CAM", "door"), ("GLASS", "door"),
    ("GLAZ", "door"), ("DOGRAMA", "door"),
    ("KOLON", "structure"), ("COLUMN", "structure"), ("BETON", "structure"), ("PERDE", "structure"),
    ("KIRIS", "structure"), ("BEAM", "structure"), ("BA", "structure"),
    ("DEKO", "decor"), ("DECOR", "decor"), ("AKSESUAR", "decor"), ("ACCESSOR", "decor"),
    ("DUVAR", "other"), ("WALL", "other"), ("DOSEME", "other"), ("SLAB", "other"), ("IZ", "other"), ("GOR", "other"),
    ("GORUNUS", "other"), ("HIDDEN", "other"), ("OVERHEAD", "other"), ("TARAMA", "other"), ("HATCH", "other"),
    ("MEKANIK", "other"), ("ELEKTRIK", "other"), ("TESISAT", "other"), ("HVAC", "other"), ("ASANSOR", "other"),
    ("LIFT", "other"), ("ELEVATOR", "other"), ("CATI", "other"), ("ROOF", "other"), ("BAGIMSIZ", "other"),
)
# Pseudo kinds of a whole piece that is not furniture but stays in the building: a column stands in the room (kept as
# a not-built obstacle), decor is left to the decor stage.
NOT_FURNITURE_AS: dict[str, str] = {"structure": "column", "decor": "decor"}
LAYER_SHARE = 0.9                   # a piece is a symbol by its layers when >= 90 % of its strokes say so
ROOM_NUMBER_RADIUS_M = (0.10, 0.35)  # a room-number tag: a circle 0.20-0.70 m across ...
ROOM_NUMBER_RE = re.compile(r"^[A-Z]{0,2}-?\d{1,3}[A-Z]?$")       # ... with one short number inside
DOOR_RADIUS_M = (0.40, 1.40)        # a door swing: a 45-135 deg arc of 0.40-1.40 m ...
DOOR_SWEEP_DEG = (45.0, 135.0)
LEAF_THIN_M = 0.08                  # ... with its leaf (a line or a strip <= 8 cm) from the hinge
HINGE_M = 0.05
HINGE_WALL_M = 0.15                 # a lone arc (its leaf owned by the opening) hinged within 15 cm of a wall
NORTH_TEXTS = ("N", "K", "KUZEY", "NORTH")
EXTRA_KEY_HEX = 8
DETAIL_INSIDE_LEG = 0.6             # a part >= 60 % inside a counter leg is a detail of it (a dishwasher front)


def _fold_words(name: Optional[str]) -> list[str]:
    folded = (name or "").translate(_FOLD).upper()
    return [w for w in re.split(r"[^A-Z0-9]+", folded) if w]


def _word_hit(key: str, words: list[str]) -> bool:
    return key in words if len(key) <= 3 else any(key in w for w in words)


def layer_kind(layer: Optional[str]) -> Optional[str]:
    """What a layer name says about its strokes: ``"furniture"``, a symbol kind of ``SYMBOL_KINDS``, the pseudo kinds
    ``"door"`` (a door or window layer: ``door_arc`` or ``other`` by shape), ``"structure"``, ``"decor"``, or None
    (nothing). Only the layer's own name counts (``xref$0$LAYER`` -> ``LAYER``; ``xref|LAYER`` -> ``LAYER``)."""
    if not layer:
        return None
    words = _fold_words(re.split(r"[$|]", layer)[-1])
    if any(_word_hit(k, words) for k in FURNITURE_LAYER_WORDS):
        return "furniture"
    for key, kind in LAYER_WORDS:
        if _word_hit(key, words):
            return kind
    return None


def stroke_kind(st: Stroke) -> Optional[str]:
    """``layer_kind`` of a stroke, unless a block of its chain names a furniture type (a WC block on a services layer
    is furniture)."""
    for name in reversed((st.block or "").split("/")):
        if name and keyword_type(name) is not None:
            return "furniture"
    return layer_kind(st.layer)


def split_symbol_strokes(segs: list[Seg]) -> tuple[list[Seg], dict[str, list[Seg]]]:
    """(furniture segments, {kind: segments}) by ``stroke_kind``; segments of no kind stay furniture."""
    keep: list[Seg] = []
    out: dict[str, list[Seg]] = {}
    for s in segs:
        kind = stroke_kind(s.stroke)
        if kind in (None, "furniture"):
            keep.append(s)
        else:
            out.setdefault(kind, []).append(s)
    return keep, out


def _full_circle(s: Seg) -> Optional[tuple[tuple[float, float], float]]:
    arc = s.stroke.arc
    if not s.curve or not arc:
        return None
    if abs(float(arc["end_deg"]) - float(arc["start_deg"])) < 359.0:
        return None
    return (float(arc["center"][0]), float(arc["center"][1])), float(arc["radius"])


def _sweep(arc: dict) -> float:
    return (float(arc["end_deg"]) - float(arc["start_deg"])) % 360.0


def _text_centres(texts) -> list[tuple[float, float, str]]:
    out = []
    for t in texts or []:
        box = t.box if hasattr(t, "box") else t["box"]
        text = t.text if hasattr(t, "text") else t["text"]
        out.append(((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0, str(text)))
    return out


def room_number_sign(segs: list[Seg], texts) -> Optional[str]:
    """Why ``segs`` are a room-number tag (one circle 0.20-0.70 m across, every other stroke inside it, a short
    number such as ``5``, ``12``, ``A3`` written inside), else None (real03: the TAG_BBOLUM circles 1-8, read as
    floor lamps by both AI passes)."""
    circles = [(s, c) for s in segs for c in [_full_circle(s)] if c and ROOM_NUMBER_RADIUS_M[0] <= c[1] <=
               ROOM_NUMBER_RADIUS_M[1]]
    if len(circles) != 1:
        return None
    circle, ((cx, cy), r) = circles[0]
    for s in segs:
        if s is not circle and any(math.dist(p, (cx, cy)) > 1.05 * r for p in s.pts):
            return None
    for tx, ty, text in _text_centres(texts):
        word = re.sub(r"\s+", "", text.translate(_FOLD).upper())
        if math.dist((tx, ty), (cx, cy)) <= r and ROOM_NUMBER_RE.match(word):
            return f"circle {2 * r:.2f} m across with the number {text.strip()!r} inside: a room-number tag"
    return None


def north_arrow_sign(segs: list[Seg], texts) -> Optional[str]:
    """A circle with an arrow and the letter N (K for Kuzey) inside or next to it: a north arrow."""
    circles = [c for c in (_full_circle(s) for s in segs) if c and 0.15 <= c[1] <= 1.5]
    if not circles or len(segs) < 2:
        return None
    (cx, cy), r = max(circles, key=lambda c: c[1])
    for tx, ty, text in _text_centres(texts):
        if text.translate(_FOLD).upper().strip() in NORTH_TEXTS and math.dist((tx, ty), (cx, cy)) <= 1.6 * r:
            return f"circle {2 * r:.2f} m across with an arrow and {text.strip()!r}: a north arrow"
    return None


def _sector(s: Seg) -> Optional[Polygon]:
    poly = Polygon([tuple(s.stroke.arc["center"])] + list(s.pts))
    poly = poly if poly.is_valid else poly.buffer(0)
    return None if poly.is_empty else poly


def opening_jambs(openings: list) -> list[tuple[float, float]]:
    """Both ends of every opening (OpeningItems or building dicts with ``center``, ``width``, ``rotation_deg``): the
    jambs a door leaf is hinged at."""
    out = []
    for o in openings or []:
        centre = o.center if hasattr(o, "center") else o.get("center")
        width = o.width if hasattr(o, "width") else o.get("width")
        rot = o.rotation_deg if hasattr(o, "rotation_deg") else o.get("rotation_deg", 0.0)
        if centre is None or not width:
            continue
        ux, uy = math.cos(math.radians(rot or 0.0)), math.sin(math.radians(rot or 0.0))
        h = float(width) / 2.0
        out += [(centre[0] - ux * h, centre[1] - uy * h), (centre[0] + ux * h, centre[1] + uy * h)]
    return out


def door_swing(segs: list[Seg], jambs: Optional[list] = None) -> Optional[tuple[list[Seg], list[Seg], str]]:
    """``(swing segments, other segments, reason)`` when ``segs`` hold a door swing: one or two arcs of 45-135 deg
    and 0.40-1.40 m radius with the thin strokes inside their sectors (the leaf open or closed: lines or strips
    <= 8 cm). The door is told by its leaf, a strip <= 8 cm wide and >= 70 % of the radius long with an end at the
    hinge (the arc centre, 5 cm), or by a hinge within 15 cm of an opening's jamb (``jambs``: the leaf belongs to the
    opening). None otherwise: a chair's half-round back is too small, a quadrant shower's sides are plain lines and
    its corner is no jamb."""
    if any(keyword_type(n) for s in segs for n in (s.stroke.block or "").split("/") if n):
        return None                         # a furniture-named block (a quadrant shower, a corner sofa)
    arcs = [s for s in segs if s.curve and s.stroke.arc and DOOR_RADIUS_M[0] <= float(s.stroke.arc["radius"]) <=
            DOOR_RADIUS_M[1] and DOOR_SWEEP_DEG[0] <= _sweep(s.stroke.arc) <= DOOR_SWEEP_DEG[1]]
    if not arcs or len(arcs) > 2:
        return None
    sectors = [p for p in (_sector(a) for a in arcs) if p is not None]
    if not sectors:
        return None
    zone = unary_union(sectors).buffer(0.03)
    hinges = [tuple(a.stroke.arc["center"]) for a in arcs]
    r = max(float(a.stroke.arc["radius"]) for a in arcs)
    swing = list(arcs)
    leaf = False
    by_stroke: dict[str, list[Seg]] = {}
    for s in segs:
        if s not in arcs and not s.dot and not s.curve and s.geom.length > 0:
            by_stroke.setdefault(s.stroke.id, []).append(s)
    for sid in sorted(by_stroke):
        ss = by_stroke[sid]
        geom = unary_union([s.geom for s in ss])
        line = len(ss) == 1 and len(set(ss[0].pts)) <= 2
        if not (line or short_side(ss) <= LEAF_THIN_M):
            continue
        if geom.intersection(zone).length < 0.9 * geom.length:
            continue
        swing.extend(ss)
        pts = [p for s in ss for p in s.pts]
        if not line and any(min(math.dist(p, h) for p in pts) <= HINGE_M for h in hinges) and \
                max(_rect_sides(geom)) >= 0.7 * r:
            leaf = True
    at_jamb = any(math.dist(j, h) <= HINGE_WALL_M for j in (jambs or []) for h in hinges)
    if not leaf and not at_jamb:
        return None
    rest = [s for s in segs if s not in swing]
    why = (f"{len(arcs)} quarter arc(s) of {r:.2f} m " + ("with its leaf from the hinge" if leaf else
                                                         "hinged at an opening's jamb") + ": a door swing")
    return swing, rest, why


def whole_symbol(segs: list[Seg], texts=None, jambs: Optional[list] = None) -> Optional[dict]:
    """``{"kind", "reason"}`` (or ``{"as": "column" | "decor", "reason"}``) when the strokes of one piece are a
    symbol, not furniture: a room-number tag, a north arrow, a door swing and nothing else, or >= 90 % of its strokes on
    non-furniture layers (none on a furniture layer or in a furniture-named block). None otherwise."""
    if not segs:
        return None
    why = room_number_sign(segs, texts)
    if why:
        return {"kind": "room_number", "reason": why, "by": "shape"}
    why = north_arrow_sign(segs, texts)
    if why:
        return {"kind": "north_arrow", "reason": why, "by": "shape"}
    swing = door_swing(segs, jambs)
    if swing is not None and not swing[1]:
        return {"kind": "door_arc", "reason": swing[2], "by": "shape"}
    kinds = [stroke_kind(s.stroke) for s in segs]
    if "furniture" in kinds:
        return None
    named = [k for k in kinds if k is not None]
    if not named or len(named) < LAYER_SHARE * len(kinds):
        return None
    kind = max(sorted(set(named)), key=named.count)
    layers = sorted({re.split(r"[$|]", s.stroke.layer or "")[-1] for s, k in zip(segs, kinds) if k == kind})
    reason = f"drawn on the {', '.join(repr(x) for x in layers[:3])} layer(s): {kind}, not furniture"
    if kind in NOT_FURNITURE_AS:
        return {"as": NOT_FURNITURE_AS[kind], "reason": reason, "by": "layer"}
    if kind == "door":
        kind = "door_arc" if any(s.curve and s.stroke.arc for s in segs) else "other"
    return {"kind": kind, "reason": reason, "by": "layer"}


def expand_ids(entity: Optional[str]) -> list[str]:
    """``id_ranges`` back to ids (``path:3-5,curve:9`` -> path:3, path:4, path:5, curve:9), in order."""
    out: list[str] = []
    for part in (entity or "").split(","):
        head, _, tail = part.partition(":")
        match = re.fullmatch(r"(\d+)-(\d+)", tail)
        if match:
            out.extend(f"{head}:{n}" for n in range(int(match.group(1)), int(match.group(2)) + 1))
        elif part:
            out.append(part)
    return out


def copy_keys(segs: list[Seg]) -> list[str]:
    """Keys that are equal for two pieces drawn by the same entities of the same block definition in two inserts of
    that block (real03: the four 1+1 B flats are one block inserted four times; entity 36 of each is the same bathtub).
    One key per level ``j`` >= 1 of the block chain: the hash of the strokes' (block names from ``j`` on, entity
    indices below ``j``). Empty for strokes outside blocks."""
    rows: dict[int, set] = {}
    depth = None
    for s in segs:
        if not s.stroke.block:
            return []
        names = s.stroke.block.split("/")
        parts = s.stroke.id.split("#", 1)[0].split("/")
        if len(parts) < len(names) + 1:
            return []
        depth = len(names) if depth is None else min(depth, len(names))
        for j in range(1, len(names)):
            rows.setdefault(j, set()).add(("/".join(names[j:]), "/".join(parts[j + 1:])))
    out = []
    for j in range(1, depth or 0):
        digest = hashlib.sha1(repr(sorted(rows[j])).encode("utf-8")).hexdigest()[:12]
        out.append(f"{j}:{digest}")
    return out


def extra_key(level_id: Optional[str], stroke_ids) -> str:
    """The question key of a re-read part: ``sym_<level>_x<hash of its stroke ids>``. A content key, so it is the same
    in every round whatever else the round asks (the sequential keys of the core's candidates must not move)."""
    digest = hashlib.sha1("\n".join(sorted(set(stroke_ids))).encode("utf-8")).hexdigest()[:EXTRA_KEY_HEX]
    return f"sym_{level_id}_x{digest}" if level_id else f"sym_x{digest}"


def symbol_record(segs: list[Seg], kind: str, reason: str, ctx: "_Ctx", raster: bool) -> dict:
    """A symbol found in the strokes (page metres; the core moves ``center`` to the building frame)."""
    fp = footprint([p for s in segs for p in s.pts], ctx.theta)
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    ids = sorted({s.stroke.id for s in segs}, key=_id_key)
    ev = ctx.evidence(ids, raster=raster, box=box, note=reason)
    return {"kind": kind, "reason": reason, "center": list(_r(fp[0])), "size": list(size), "rotation_deg": rotation,
            "box": box, "evidence": [ev], "stroke_ids": ids}


def _object_key(st: Stroke) -> str:
    """The block instance a stroke belongs to as an object: the innermost instance whose block name names a furniture
    type (a tap block inside a shower block belongs to the shower; a chair block inside a dining block is a chair),
    else the innermost instance (``INSERT:7C/5/20`` for a sink block nested in a flat block); the chain for ids of
    another form; "" for a stroke outside any block."""
    if not st.block:
        return ""
    names = st.block.split("/")
    parts = st.id.split("#", 1)[0].split("/")
    if len(parts) < len(names) + 1:
        return f"{st.block}|"
    named = [i for i, n in enumerate(names) if n and keyword_type(n) is not None]
    depth = named[-1] + 1 if named else len(names)
    return "/".join(parts[:depth])


def containers_of(strokes) -> set[str]:
    """Block instances that hold other block instances among ``strokes`` (a flat block holding sink and fridge
    blocks): their own strokes are loose drawing, not one object. Taken over the whole page (``furniture``, the core)
    so that a re-read of a few strokes of a flat still knows the flat is a container."""
    out: set[str] = set()
    for st in strokes:
        parts = _object_key(st).split("/")
        for i in range(1, len(parts)):
            out.add("/".join(parts[:i]))
    return out


def _containers(segs: list[Seg], given: Optional[set] = None) -> set[str]:
    return containers_of(s.stroke for s in segs) | set(given or ())


def _is_loose(st: Stroke, containers: set[str]) -> bool:
    key = _object_key(st)
    return key == "" or key in containers or key.endswith("|")


def object_groups(segs: list[Seg], table: dict, theta: float, containers: Optional[set] = None) -> list[Cluster]:
    """One part per block instance and connected stroke group (``_object_key``): a block that holds no other block (a
    sink, a fridge, a shower with its tap) is one object, ``part.note`` ``["block"]``, never merged into another part
    (unless it draws several things that together fit no type: then it is split like loose strokes); the loose strokes
    of a block holding blocks (a flat) are clustered at 20 mm and a part lying >= 80 % inside another is merged into
    it (``_merge_contained``: a bed's pillows; a sink in a counter stays its own)."""
    by_inst: dict[str, list[Seg]] = {}
    for s in segs:
        by_inst.setdefault(_object_key(s.stroke), []).append(s)
    containers = _containers(segs, containers)
    blocks: list[Cluster] = []
    loose: list[Cluster] = []
    for key in sorted(by_inst):
        groups = sorted(clusters_of(by_inst[key], CLUSTER_M), key=lambda c: c.stroke_ids()[0])
        whole = Cluster(by_inst[key], note=["block"])
        if key and key not in containers and not key.endswith("|") and (
                len(groups) == 1 or fitting_types(table, whole.size(theta))):
            blocks.append(whole)
        else:
            loose.extend(groups)                  # a flat's own strokes, or a block drawing several things
    return blocks + _merge_contained(loose, table, theta)


DRAIN_RADIUS_M = (0.015, 0.06)      # a sink's or basin's drain: a small full circle
KITCHEN_NEAR_M = 1.0                # a kitchen appliance block this close makes an outline along the walls a counter
# The re-read takes a counter outline whose legs cover >= 80 % of it (real03's 1+1 B counter ends in a 0.2 m^2 step
# round a column: 86 %); the uncovered rest is left out.
REREAD_COUNTER_COVER = 0.8


def _drain(segs: list[Seg]) -> bool:
    """A drain among the strokes: a full circle 3-12 cm across."""
    return any(c is not None and DRAIN_RADIUS_M[0] <= c[1] <= DRAIN_RADIUS_M[1] for c in map(_full_circle, segs))


def _leg_front(poly: Polygon, leg_polys: list, leg_fronts: list) -> Optional[float]:
    """The front of the counter leg that holds most of ``poly`` (None without one)."""
    best = None
    for lp, front in zip(leg_polys, leg_fronts):
        share = poly.intersection(lp).area
        if share > 0 and (best is None or share > best[0]):
            best = (share, front)
    return best[1] if best else None


def _kitchen_block(s: Seg) -> bool:
    """A stroke of a kitchen appliance block (hob, sink, fridge, dishwasher, base cabinet) by its name."""
    return bool(_appliance_type(s, True)) or any(keyword_type(n) == "kitchen_counter"
                                                for n in (s.stroke.block or "").split("/") if n)


def _kitchen_near(geom, segs: list[Seg]) -> bool:
    """A kitchen appliance block within ``KITCHEN_NEAR_M`` of ``geom`` (page metres). Local on purpose: a whole flat
    re-read at once holds the kitchen blocks, but the vanity in its bathroom is no counter."""
    near = geom.buffer(KITCHEN_NEAR_M)
    return any(_kitchen_block(s) and near.intersects(s.geom) for s in segs)


def _counter_runs(keep: list[Seg], ctx: "_Ctx", walls: list, openings: list, raster: bool, notes: list,
                  containers: Optional[set] = None
                  ) -> tuple[list[FurnitureItem], list[Polygon], list[Optional[float]], set]:
    """Counter runs among the loose strokes of a re-read cluster (Milestone 12, real03: every counter is drawn in the
    flat block itself): a closed outline of loose strokes joined end to end (``contours``) along wall faces
    (``counter_legs``), or an open front line running between wall faces (``counter_rule``), with two legs or a
    kitchen appliance block near it. Returns (counter items, leg polygons, leg fronts, ids of the used segments)."""
    containers = _containers(keep, containers)
    loose = [s for s in keep if _is_loose(s.stroke, containers)]
    to_f, from_f = _frame(ctx.theta)
    faces = _wall_faces(walls, openings, to_f)
    items: list[FurnitureItem] = []
    polys: list[Polygon] = []
    fronts: list[Optional[float]] = []
    used: set = set()

    def add_leg(leg: dict, note: str) -> None:
        item = _counter_item(leg, walls, ctx, raster)
        item.evidence["note"] = note
        items.append(item)
        x0, y0, x1, y1 = leg["rect_f"]
        polys.append(Polygon([from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]))
        fronts.append(item.front_deg)

    for poly, members in sorted(contours(loose), key=lambda pm: (-pm[0].area, sorted(pm[1]))):
        segs = [loose[i] for i in members]
        if poly.area < 0.3 or any(id(s) in used for s in segs) or len({s.stroke.id for s in segs}) > 4:
            continue
        found = counter_legs(Polygon([to_f(p) for p in poly.exterior.coords]).buffer(0), faces, REREAD_COUNTER_COVER,
                             short_corner=True)
        if found is None or not (len(found[0]) >= 2 or _kitchen_near(poly, keep)):
            continue
        for lg in found[0]:
            add_leg({"rect_f": lg["rect"], "front_f": lg["front_f"], "segs": segs, "length": lg["length"],
                     "depth": lg["depth"]}, "kitchen counter run drawn as one outline along the walls (M12 re-read)")
        for (x0, y0, x1, y1) in found[1]:
            notes.append(f"counter outline {segs[0].stroke.id}: a free block {x1 - x0:.2f} x {y1 - y0:.2f} m left "
                         f"to the re-read")
        used.update(id(s) for s in segs)
        notes.append(f"counter outline {segs[0].stroke.id}: {len(found[0])} legs (M12 re-read)")
    by_stroke: dict[str, list[Seg]] = {}
    for s in loose:
        if id(s) not in used and s.stroke.kind == "polyline" and not s.curve:
            by_stroke.setdefault(s.stroke.id, []).append(s)
    for sid in sorted(by_stroke):
        segs = by_stroke[sid]
        if len(segs) < 2:
            continue
        legs = counter_rule(Cluster(segs), walls, openings, ctx.theta, loose_in_blocks=True)
        if not legs or not (len(legs) >= 2 or _kitchen_near(unary_union([s.geom for s in segs]), keep)):
            continue
        for leg in legs:
            add_leg(leg, "kitchen counter: its front line runs between wall faces (M12 re-read)")
        used.update(id(s) for s in segs)
        notes.append(f"counter front line {sid}: {len(legs)} legs (M12 re-read)")
    return items, polys, fronts, used


def reread(cl: Cluster, ctx: "_Ctx", table: dict, walls: list, openings: list, wall_polys: list, texts,
           notes: list, raster: bool = False, why: str = "", containers: Optional[set] = None) -> dict:
    """The deeper re-read of an untyped cluster: ``{"items": [FurnitureItem], "symbols": [symbol records]}``.

    1. Strokes on non-furniture layers leave the cluster (``split_symbol_strokes``); their groups >= 0.20 m are
       symbols (a room-number tag by its shape, a door layer group with an arc a ``door_arc``).
    2. Counter runs drawn as loose outlines or front lines along the walls (``_counter_runs``).
    3. The rest is split by block instance and connected stroke group (``object_groups``). Each part: details
       (< 0.20 m) and lines are dropped; a room-number tag, a north arrow or a lone door swing is a symbol; a door
       swing on a part (a fridge drawn with its door) is a symbol and the part goes on without it (``details["door"]``);
       the stair rule; a bowl with a drain in a counter leg or beside a kitchen block is the kitchen sink; another part
       >= 60 % inside a counter leg is a detail of it (a dishwasher front); a block name (``_block_item``, its L
       outline kept); loose strokes drawn as a table with chairs around it (``split_table_chairs``); what is left is an
       ``unknown`` piece (``details["reread"]``, ``l_outline``/``l_front``, ``drain``, ``door``: the reading step's
       context rules and the core's extra question use them).
    """
    keep, removed = split_symbol_strokes(cl.segs)
    jambs = opening_jambs(openings)
    symbols: list[dict] = []
    dropped = 0
    for kind in sorted(removed):
        for g in sorted(clusters_of(removed[kind], CLUSTER_M), key=lambda c: c.stroke_ids()[0]):
            if max(g.size(ctx.theta)) < DETAIL_M:
                dropped += 1
                continue
            k = kind
            if kind == "door":
                k = "door_arc" if any(s.curve and s.stroke.arc for s in g.segs) else "other"
            elif kind in NOT_FURNITURE_AS:
                k = "other"
            layers = sorted({re.split(r"[$|]", s.stroke.layer or "")[-1] for s in g.segs})
            why_k = (f"drawn on the {', '.join(repr(x) for x in layers[:3])} layer(s) inside a furniture cluster: "
                     f"{kind}, not furniture")
            sign = room_number_sign(g.segs, texts)
            if sign:
                k, why_k = "room_number", sign
            symbols.append(symbol_record(g.segs, k, why_k, ctx, raster))
    items, leg_polys, leg_fronts, used = _counter_runs(keep, ctx, walls, openings, raster, notes, containers)
    rest = [s for s in keep if id(s) not in used]
    later: list[tuple[Cluster, Optional[str]]] = []
    for part in object_groups(rest, table, ctx.theta, containers):
        if max(part.size(ctx.theta)) < DETAIL_M or short_side(part.segs) < LINE_DETAIL_M:
            dropped += 1
            continue
        sign = room_number_sign(part.segs, texts)
        if sign:
            symbols.append(symbol_record(part.segs, "room_number", sign, ctx, raster))
            continue
        sign = north_arrow_sign(part.segs, texts)
        if sign:
            symbols.append(symbol_record(part.segs, "north_arrow", sign, ctx, raster))
            continue
        door_note = None
        swing = door_swing(part.segs, jambs)
        if swing is not None:
            symbols.append(symbol_record(swing[0], "door_arc", swing[2], ctx, raster))
            if not swing[1]:
                continue
            part = Cluster(swing[1], note=list(part.note))
            door_note = "drawn with a door swing (a cabinet or appliance door)"
            if max(part.size(ctx.theta)) < DETAIL_M:
                continue
        fp = footprint([p for s in part.segs for p in s.pts], ctx.theta)
        stair = stair_rule(part, ctx.theta) if max(fp[1], fp[2]) <= MAX_SIDE_M else None
        if stair is not None:
            items.append(_stair_item(part, stair, fp, ctx, raster, notes))
            continue
        later.append((part, door_note))
    for part, door_note in later:
        lsh = l_shape(part, ctx.theta)
        fp = lsh["fp"] if lsh else footprint([p for s in part.segs for p in s.pts], ctx.theta)
        poly = Polygon(fp[4])
        in_leg = bool(leg_polys) and poly.area > 0 and max(poly.intersection(lp).area for lp in leg_polys) >= \
            DETAIL_INSIDE_LEG * poly.area
        named = keyword_type((_block_chain(part) or "").split("/")[-1])
        drain = _drain(part.segs)
        own = {id(s) for s in part.segs}
        if drain and named in (None, "sink_kitchen") and fits(table, "sink_kitchen", (fp[1], fp[2])) and (
                in_leg or _kitchen_near(poly, [s for s in keep if id(s) not in own])):
            front = _leg_front(poly, leg_polys, leg_fronts)
            items.append(_rule_item(part.segs, fp, "sink_kitchen", front, ctx, raster, table,
                                    "a bowl with its drain " + ("in a counter leg" if in_leg else "beside the "
                                                                "kitchen appliances") + " (M12 re-read)"))
            continue
        if in_leg and named not in KITCHEN_APPLIANCES:
            dropped += 1                    # a dishwasher, drawers or a door front drawn in a counter leg
            continue
        item = _block_item(part, fp, ctx, raster, table, lsh, wall_polys, [])
        if item is not None and not fits(table, item.type, tuple(item.size)):
            item = None                     # a piece of a named block (a bed's pillow) is not the named piece
        if item is not None:
            if lsh:
                item.details.update(l_details(lsh))
            if door_note:
                item.evidence["note"] = "; ".join(x for x in (item.evidence.get("note"), door_note) if x)
            items.append(item)
            continue
        split = split_table_chairs(part, table, ctx.theta) if "block" not in part.note and not lsh else None
        if split is not None:
            items.extend(table_chair_items(split, ctx, raster, table))
            continue
        reason = "re-read part of an untyped cluster" + (f" ({why})" if why else "")
        details = dict({"reread": why or "cluster"}, **(l_details(lsh) if lsh else round_shape(part.segs)))
        if lsh:
            details["l_front"] = lsh["front_deg"]
        if drain:
            details["drain"] = True
        if door_note:
            details["door"] = True
            reason += f"; {door_note}"
        items.append(_unknown(part, fp, ctx, raster, reason, details))
    if dropped:
        notes.append(f"re-read of {cl.stroke_ids()[0]}: {dropped} details, lines or symbol strokes dropped")
    index: dict[str, list[Seg]] = {}
    for s in cl.segs:
        index.setdefault(s.stroke.id, []).append(s)
    for item in items:
        keys = copy_keys([s for sid in expand_ids(item.evidence.get("entity")) for s in index.get(sid, [])])
        if keys:
            item.details["copy_keys"] = keys
    return {"items": items, "symbols": symbols}
