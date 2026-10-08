"""synthetic-07 layout: ONE CAD sheet with every drawing kind (docs/milestone10.md §3.4, docs/synthetic.md).

What: the whole sheet as data. Four plan levels (basement, its open-kitchen alternative, ground floor, attic under a
gable roof with a roof terrace), the section ``A-A KESİTİ``, the elevations ``GÜNEY GÖRÜNÜŞÜ`` and ``DOĞU GÖRÜNÜŞÜ``, the
site plan ``VAZİYET PLANI``, a ``LEJANT``, the title block, the frame and one stray LINE. Every drawing is a list of
``Prim`` (line, polyline, circle, arc, hatch, text, mtext, insert) in its own metric frame plus the position of that
frame on the sheet (centimetres, ``$INSUNITS`` = 5).

Why: the ground truth must be exact, so the drawing and the truth come from the same numbers. ``sheet_writer`` turns the
prims into DXF entities, ``sheet_truth`` reads boxes, ids, heights and openings from the same objects. The plans reuse
the Level model of ``model.py`` (rooms from the wall union, door rotations, furniture checks), so the rooms, ids and
footprints are derived exactly as in synthetic-01 .. -05; only the drawing differs: walls are open face lines on a layer
without a wall word (like real02's ``DBM_w_sld``), columns are closed rectangles on a structural layer, doors and
windows are blocks (a door with arcs; a sliding leaf; a double door), room labels are MTEXT ``SALON\\P43.5M2``.

How: the building is 10.0 x 8.0 m (outer faces; building XY frame = ground-floor frame, origin at the min corner,
docs/milestone10.md §1.6b row 1). z = 0 at the finished ground floor. Basement -3.00, ground 0.00, attic +3.00, slabs
0.20 m, ceilings 2.80 m. The roof is a 35 degree gable (ridge along X at y = 4.0) whose UNDERSIDE meets the outer wall face
1.00 m above the attic floor (the knee wall), 0.50 m overhang, 0.25 m thick (perpendicular to the slope); the SE quadrant
of the attic is a roof terrace (shown on the attic plan; the elevations draw the roof envelope). Each plan sits at its own
offset on the sheet (pure shifts); the offsets make the box tops all different, so the reading order of the regions
(top to bottom by box top, then left to right) never depends on a tie.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, fields
from typing import Optional

from wenart import geometry as G
from wenart.synthetic import blocks
from wenart.synthetic.dxf_writer import canonical_ring
from wenart.synthetic.model import Furniture, Level, LevelBuilder, Opening, wall_union

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

PROJECT = "synthetic-07"
FILE_DXF = "sheet.dxf"
FILE_DWG = "source/sheet.dwg"                       # the DWG copy (dxf2dwg); not a project document
CM = 100.0                                          # drawing units (cm) per metre
INSUNITS = 5                                        # centimetres
METRES_PER_UNIT = 0.01
FRAME = (0.0, 0.0, 11000.0, 5600.0)                 # cm
STRAY = ((-90000.0, 80000.0), (-89900.0, 80400.0))  # cm, one LINE far outside the frame

WIDTH, DEPTH = 10.0, 8.0                            # outer faces, metres (X, Y)
T_OUT, T_IN = 0.25, 0.10
SLAB = 0.20
FLOOR_TO_FLOOR = 3.0
CEILING = FLOOR_TO_FLOOR - SLAB                     # 2.80
PITCH_DEG, KNEE, OVERHANG, ROOF_T = 35.0, 1.0, 0.5, 0.25
CUT_AT = 3.0                                        # the cut line A-A runs along Y at x = 3.0, looking towards -X
PLINTH = 0.6                                        # stone plinth on the south facade, metres
TERRACE = ((6.10, -OVERHANG), (WIDTH + OVERHANG, -OVERHANG), (WIDTH + OVERHANG, 4.0), (6.10, 4.0))

# Layers (no wall word in the plan wall layer: WALL | DUVAR | MUR | PARED).
LAYERS: tuple[tuple[str, int], ...] = (
    ("AR_w_sld", 7), ("S-BETON", 5), ("A_Kapi", 2), ("A_Pencere", 4), ("A_Mobilya", 8), ("A_Yazi", 7),
    ("A_Cati", 3), ("A_Kesit_Cizgisi", 1), ("K_Kesit", 7), ("K_Kot", 1), ("K_Zemin", 7), ("K_Cati", 6),
    ("G_Cephe", 7), ("G_Pencere", 4), ("G_Kapi", 2), ("G_Tarama", 8), ("V_Parsel", 1), ("V_Sinir_Duv", 7),
    ("V_Bina", 7), ("V_Agac", 3), ("V_Yol", 8), ("V_Kuzey", 7), ("A_Cerceve", 7), ("A_Antet", 7), ("A_Lejant", 7),
)
L_WALL, L_COLUMN, L_DOOR, L_WINDOW, L_FURN, L_TEXT = "AR_w_sld", "S-BETON", "A_Kapi", "A_Pencere", "A_Mobilya", "A_Yazi"
L_ROOF_PLAN, L_CUT = "A_Cati", "A_Kesit_Cizgisi"
L_SEC, L_LEVEL, L_GROUND, L_SEC_ROOF = "K_Kesit", "K_Kot", "K_Zemin", "K_Cati"
L_ELEV, L_ELEV_WIN, L_ELEV_DOOR, L_HATCH = "G_Cephe", "G_Pencere", "G_Kapi", "G_Tarama"
L_PLOT, L_PLOT_WALL, L_BUILDING, L_TREE, L_ROAD, L_NORTH = "V_Parsel", "V_Sinir_Duv", "V_Bina", "V_Agac", "V_Yol", "V_Kuzey"
L_FRAME, L_TITLEBLOCK, L_LEGEND = "A_Cerceve", "A_Antet", "A_Lejant"

TEXT_LABEL, TEXT_TITLE, TEXT_NOTE, TEXT_MARK = 20.0, 30.0, 20.0, 25.0     # cm
CHAR_WIDTH, DESCENT, LINE_SPACING = 0.8, 0.25, 5.0 / 3.0                  # text box estimate (as synthetic-06)

# Door and window blocks of this sheet: name -> (kind, clear width m, operation).
OPENING_BLOCKS: dict[str, tuple[str, float, Optional[str]]] = {
    "KAPI_80": ("door", 0.8, "swing"), "KAPI_90": ("door", 0.9, "swing"),
    "KAPI_SURME_90": ("door", 0.9, "sliding"), "KAPI_CIFT_140": ("door", 1.4, "double"),
    "PENCERE_60": ("window", 0.6, None), "PENCERE_120": ("window", 1.2, None), "PENCERE_180": ("window", 1.8, None),
}
STAIR_BLOCK, STAIR_SIZE = "MERDIVEN", (1.0, 3.0)
DOOR_HEIGHT, WINDOW_HEIGHT, WINDOW_SILL = 2.10, 1.20, 0.90


def rnd(v: float, n: int = 6) -> float:
    return G.snap(float(v), n)


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------

@dataclass
class Prim:
    """One drawing primitive in a drawing's metric frame (metres; text height in cm). ``role`` is the key the truth
    uses to find the entity again (empty = plain geometry)."""
    kind: str                       # line | poly | circle | arc | hatch | text | mtext | insert
    layer: str
    pts: list = field(default_factory=list)
    closed: bool = False
    role: str = ""
    text: str = ""
    height: float = 0.0
    radius: float = 0.0
    angles: tuple = ()
    block: str = ""
    rotation: float = 0.0
    linetype: str = ""
    pattern: str = ""
    scale: float = 1.0


def line(layer, a, b, role="", linetype="") -> Prim:
    return Prim("line", layer, [G.snap_point(a), G.snap_point(b)], role=role, linetype=linetype)


def poly(layer, pts, closed=False, role="", linetype="") -> Prim:
    return Prim("poly", layer, [G.snap_point(p) for p in pts], closed=closed, role=role, linetype=linetype)


def rect(layer, x0, y0, x1, y1, role="", linetype="") -> Prim:
    return poly(layer, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True, role, linetype)


def circle(layer, c, r, role="") -> Prim:
    return Prim("circle", layer, [G.snap_point(c)], radius=r, role=role)


def arc(layer, c, r, a0, a1, role="") -> Prim:
    return Prim("arc", layer, [G.snap_point(c)], radius=r, angles=(a0, a1), role=role)


def hatch(layer, pts, pattern, scale, role="") -> Prim:
    return Prim("hatch", layer, [G.snap_point(p) for p in pts], closed=True, pattern=pattern, scale=scale, role=role)


def text(layer, at, s, height, role="") -> Prim:
    return Prim("text", layer, [G.snap_point(at)], text=s, height=height, role=role)


def mtext(layer, at, lines, height, role="") -> Prim:
    """MTEXT with its top left corner at ``at``; ``lines`` joined by \\P."""
    return Prim("mtext", layer, [G.snap_point(at)], text="\\P".join(lines), height=height, role=role)


def insert(layer, block, at, rotation=0.0, role="") -> Prim:
    return Prim("insert", layer, [G.snap_point(at)], block=block, rotation=rotation, role=role)


def text_box_m(p: Prim) -> list[float]:
    """Estimated box (metres) of a text prim (the rule of synthetic-06: 0.8 x height per character, 0.25 x height below
    the baseline, MTEXT lines 5/3 x height apart)."""
    h = p.height / CM
    x, y = p.pts[0]
    lines = p.text.split("\\P") if p.kind == "mtext" else [p.text]
    width = max(len(s) for s in lines) * CHAR_WIDTH * h
    if p.kind == "mtext":
        last = y - h - (len(lines) - 1) * LINE_SPACING * h
        return [rnd(x), rnd(last - DESCENT * h), rnd(x + width), rnd(y)]
    return [rnd(x), rnd(y - DESCENT * h), rnd(x + width), rnd(y + h)]


# --------------------------------------------------------------------------
# Blocks (metres, local frame; layer 0 so they take the layer of the INSERT)
# --------------------------------------------------------------------------

def _door_block(name: str) -> list[Prim]:
    """Hinge at (-w/2, 0), the door opens towards +Y (the side of the room it opens into)."""
    _, w, operation = OPENING_BLOCKS[name]
    if operation == "swing":
        return [line("0", (-w / 2, 0), (-w / 2, w)), arc("0", (-w / 2, 0), w, 0.0, 90.0)]
    if operation == "double":
        h = w / 2
        return [line("0", (-w / 2, 0), (-w / 2, h)), arc("0", (-w / 2, 0), h, 0.0, 90.0),
                line("0", (w / 2, 0), (w / 2, h)), arc("0", (w / 2, 0), h, 90.0, 180.0)]
    # sliding: the leaf (a thin rectangle) stands half open beside the wall plane, an arrow shows the travel
    return [rect("0", 0.0, 0.05, w, 0.09), line("0", (-w / 2 + 0.1, 0.14), (w / 2 - 0.1, 0.14)),
            line("0", (w / 2 - 0.1, 0.14), (w / 2 - 0.2, 0.19)), line("0", (w / 2 - 0.1, 0.14), (w / 2 - 0.2, 0.09))]


def _window_block(name: str) -> list[Prim]:
    """Three lines along the 0.25 m outer wall band (both faces and the glass) and two jambs across it."""
    _, w, _ = OPENING_BLOCKS[name]
    h = T_OUT / 2
    return [line("0", (-w / 2, h), (w / 2, h)), line("0", (-w / 2, 0), (w / 2, 0)), line("0", (-w / 2, -h), (w / 2, -h)),
            line("0", (-w / 2, -h), (-w / 2, h)), line("0", (w / 2, -h), (w / 2, h))]


def _furniture_block(size) -> list[Prim]:
    w, d = size
    inset = min(0.05, d * 0.15)
    return [rect("0", -w / 2, -d / 2, w / 2, d / 2), line("0", (-w / 4, -d / 2 + inset), (w / 4, -d / 2 + inset))]


def _stair_block() -> list[Prim]:
    """1.0 x 3.0 m flight, 12 risers of 0.25 m, walking line with an arrow towards +Y (up)."""
    w, d = STAIR_SIZE
    out = [rect("0", -w / 2, -d / 2, w / 2, d / 2)]
    out += [line("0", (-w / 2, -d / 2 + 0.25 * k), (w / 2, -d / 2 + 0.25 * k)) for k in range(1, 12)]
    out += [line("0", (0, -d / 2 + 0.3), (0, d / 2 - 0.3)), line("0", (0, d / 2 - 0.3), (-0.12, d / 2 - 0.6)),
            line("0", (0, d / 2 - 0.3), (0.12, d / 2 - 0.6))]
    return out


def _tree_block() -> list[Prim]:
    return [circle("0", (0, 0), 1.2), circle("0", (0, 0), 0.15), line("0", (-0.5, 0), (0.5, 0)), line("0", (0, -0.5), (0, 0.5))]


def _north_block() -> list[Prim]:
    """Circle of r 0.7 with an arrow from the centre to the north (+Y)."""
    return [circle("0", (0, 0), 0.7), poly("0", [(0, 0.7), (-0.25, -0.35), (0, -0.15), (0.25, -0.35)], True)]


def block_table() -> dict[str, list[Prim]]:
    table: dict[str, list[Prim]] = {}
    for name in sorted(OPENING_BLOCKS):
        table[name] = _door_block(name) if OPENING_BLOCKS[name][0] == "door" else _window_block(name)
    for name in sorted(blocks.BLOCKS):
        table[name] = _furniture_block(blocks.furniture_size(name))
    table[STAIR_BLOCK] = _stair_block()
    table["AGAC"] = _tree_block()
    table["KUZEY"] = _north_block()
    return table


BLOCK_TABLE = block_table()


# --------------------------------------------------------------------------
# Boxes (analytic, from the prims themselves)
# --------------------------------------------------------------------------

def _arc_points(c, r, a0, a1) -> list[tuple[float, float]]:
    a0 %= 360.0
    a1 %= 360.0
    if a1 <= a0:
        a1 += 360.0
    angles = [a0, a1] + [k for k in (0.0, 90.0, 180.0, 270.0, 360.0, 450.0) if a0 < k < a1]
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in angles]


def _points(p: Prim, rot: float = 0.0, off=(0.0, 0.0)) -> list[tuple[float, float]]:
    """Points bounding a non-text prim, rotated by ``rot`` about the origin and moved by ``off``."""
    def place(q):
        r = G.rotate_point(q, rot)
        return (r[0] + off[0], r[1] + off[1])

    if p.kind in ("line", "poly", "hatch"):
        return [place(q) for q in p.pts]
    if p.kind == "circle":
        c = place(p.pts[0])
        return [(c[0] + dx * p.radius, c[1] + dy * p.radius) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    if p.kind == "arc":
        c = place(p.pts[0])
        return _arc_points(c, p.radius, p.angles[0] + rot, p.angles[1] + rot)
    if p.kind == "insert":
        at = place(p.pts[0])
        pts = []
        for q in BLOCK_TABLE[p.block]:
            pts += _points(q, rot + p.rotation, at)
        return pts
    return []


def prim_box(p: Prim) -> Optional[list[float]]:
    """Box (metres) of a geometry prim; None for texts (they never bridge or extend a drawing)."""
    if p.kind in ("text", "mtext"):
        return None
    pts = _points(p)
    return [rnd(v) for v in G.bbox(pts)] if pts else None


def union_box(boxes) -> list[float]:
    boxes = [b for b in boxes if b is not None]
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


# --------------------------------------------------------------------------
# Levels (model.Level + the facts only this sheet has)
# --------------------------------------------------------------------------

@dataclass
class SheetOpening(Opening):
    """An opening whose block is one of OPENING_BLOCKS; ``sill`` / ``clear_height`` are the true vertical values
    (above the level floor) that an elevation shows."""
    operation: Optional[str] = None
    sill: float = 0.0
    clear_height: float = 0.0

    @property
    def width(self) -> float:
        return OPENING_BLOCKS[self.block][1]


@dataclass
class SheetFurniture(Furniture):
    @property
    def type(self) -> str:
        return "stair" if self.block == STAIR_BLOCK else super().type

    @property
    def status(self) -> str:
        return "verified" if self.block == STAIR_BLOCK else super().status

    def front_deg(self) -> Optional[float]:
        return None if self.block == STAIR_BLOCK else super().front_deg()


@dataclass
class SheetLevel(Level):
    level_id: str = ""
    level_label: str = ""
    level_order: int = 0
    kind: str = "floor"
    variant: str = "base"
    variant_group: Optional[str] = None
    base_level_id: Optional[str] = None
    region_class: str = "floor_plan"
    floor_z: float = 0.0

    @property
    def id(self) -> str:
        return self.level_id

    @property
    def label(self) -> str:
        return self.level_label

    @property
    def order(self) -> int:
        return self.level_order

    @property
    def elevation(self) -> float:
        return self.floor_z


def _builder(title: str, **kw) -> LevelBuilder:
    b = LevelBuilder(title, WIDTH, DEPTH)
    base = {f.name: getattr(b.level, f.name) for f in fields(Level)}
    b.level = SheetLevel(**base, **kw)
    b.level.ceiling_height = CEILING
    return b


def _door(b: LevelBuilder, block: str, wall: int, at, into: str) -> None:
    _, _, operation = OPENING_BLOCKS[block]
    b.level.openings.append(SheetOpening("door", block, wall, G.snap_point(at), swing_into=into, operation=operation,
                                         sill=0.0, clear_height=DOOR_HEIGHT))


def _window(b: LevelBuilder, block: str, wall: int, at, sill: float = WINDOW_SILL, height: float = WINDOW_HEIGHT) -> None:
    b.level.openings.append(SheetOpening("window", block, wall, G.snap_point(at), sill=sill, clear_height=height))


def _piece(b: LevelBuilder, block: str, at, rotation: float = 0.0) -> None:
    size = STAIR_SIZE if block == STAIR_BLOCK else None
    b.level.furniture.append(SheetFurniture(block, G.snap_point(at), float(rotation), size))


S, E, N, W = 0, 1, 2, 3                       # outer wall indices: bottom, right, top, left
LABEL_SALON, LABEL_MUTFAK, LABEL_HOL = "SALON\n43.5M2", "MUTFAK\n13.3M2", "HOL\n13.3M2"
LABEL_OPEN = "SALON + AÇIK MUTFAK\n57.2M2"


def level_bodrum(alt: bool = False) -> SheetLevel:
    """BODRUM KAT PLANI (-3.00). ``alt``: the open-kitchen alternative (the partition between Salon and Mutfak is
    gone, level id L-1b). Windows sit high (sill 2.00 m, below the ground line of the elevations); the north door is the
    basement's outside door."""
    title = "BODRUM KAT PLANI" + (" (AÇIK MUTFAK)" if alt else "")
    b = _builder(title, level_id="L-1b" if alt else "L-1", level_label="Bodrum Kat", level_order=-1, kind="basement",
                 variant="Açık mutfak" if alt else "base", variant_group="vg_L-1", base_level_id="L-1" if alt else None,
                 region_class="alternative_floor_plan" if alt else "floor_plan", floor_z=-FLOOR_TO_FLOOR)
    v = b.wall((6.10, 3.95 if alt else 0.25), (6.10, 7.75))
    h = b.wall((6.10, 4.00), (9.75, 4.00))
    salon = LABEL_OPEN if alt else LABEL_SALON
    kitchen = LABEL_OPEN if alt else LABEL_MUTFAK
    _door(b, "KAPI_SURME_90", v, (6.10, 6.00), salon)           # Hol -> Salon, sliding leaf
    _door(b, "KAPI_80", h, (7.60, 4.00), kitchen)
    _door(b, "KAPI_90", N, (8.0, 7.875), LABEL_HOL)             # outside door of the basement (below the ground line)
    for x in (1.5, 4.5, 8.0):
        _window(b, "PENCERE_120", S, (x, 0.125), 2.0, 0.6)
    _window(b, "PENCERE_120", W, (0.125, 4.0), 2.0, 0.6)
    for x in (1.5, 4.5):
        _window(b, "PENCERE_120", N, (x, 7.875), 2.0, 0.6)
    _window(b, "PENCERE_60", E, (9.875, 6.0), 2.0, 0.6)
    b.label(salon, (1.0, 4.6))
    if not alt:
        b.label(LABEL_MUTFAK, (6.35, 2.8))
    b.label(LABEL_HOL, (6.35, 6.6))
    _piece(b, "KANEPE_3LU", (3.2, 7.2), 0)                      # 3-seat sofa against the north wall
    _piece(b, "BUZDOLABI", (9.40, 0.65), 270)                   # the counter run along the east wall
    _piece(b, "TEZGAH", (9.45, 2.20), 270)
    _piece(b, "EVIYE", (9.50, 1.70), 270)
    _piece(b, "OCAK", (9.45, 2.85), 270)
    _piece(b, STAIR_BLOCK, (9.25, 6.0), 0)
    return b.build()


def level_zemin() -> SheetLevel:
    """ZEMİN KAT PLANI (0.00): reference plan of the registration."""
    b = _builder("ZEMİN KAT PLANI", level_id="L0", level_label="Zemin Kat", level_order=0, kind="floor", floor_z=0.0)
    v = b.wall((6.10, 0.25), (6.10, 7.75))
    h = b.wall((6.10, 4.00), (9.75, 4.00))
    yatak = "YATAK ODASI\n43.5M2"
    _door(b, "KAPI_CIFT_140", N, (8.0, 7.875), LABEL_HOL)       # entrance, double door
    _door(b, "KAPI_90", v, (6.10, 6.00), yatak)
    _door(b, "KAPI_80", h, (7.60, 4.00), "BANYO\n13.3M2")
    _door(b, "KAPI_90", S, (4.5, 0.125), yatak)                 # garden door
    _window(b, "PENCERE_120", S, (1.5, 0.125))
    _window(b, "PENCERE_60", S, (8.0, 0.125), 1.5, 0.6)
    _window(b, "PENCERE_120", W, (0.125, 4.0))
    for x in (1.5, 4.5):
        _window(b, "PENCERE_120", N, (x, 7.875))
    _window(b, "PENCERE_60", E, (9.875, 3.0), 1.5, 0.6)
    b.label(yatak, (1.0, 4.6))
    b.label("BANYO\n13.3M2", (7.0, 3.0))
    b.label(LABEL_HOL, (6.35, 6.6))
    _piece(b, "YATAK_CIFT", (3.0, 6.70), 0)                     # the only drawn bed, in the bedroom
    _piece(b, "KLOZET", (9.40, 2.40), 270)
    _piece(b, "LAVABO", (9.525, 1.40), 270)
    _piece(b, "DUS", (6.70, 0.80), 0)
    _piece(b, STAIR_BLOCK, (9.25, 6.0), 0)
    return b.build()


def level_cati() -> SheetLevel:
    """ÇATI KAT PLANI (+3.00): attic under the gable roof; the south-east room is the roof terrace."""
    b = _builder("ÇATI KAT PLANI", level_id="L1", level_label="Çatı Katı", level_order=1, kind="attic", floor_z=FLOOR_TO_FLOOR)
    v = b.wall((6.10, 0.25), (6.10, 7.75))
    h = b.wall((6.10, 4.00), (9.75, 4.00))
    oyun, teras = "OYUN ODASI\n43.5M2", "TERAS\n13.3M2"
    _door(b, "KAPI_90", v, (6.10, 6.00), oyun)
    _door(b, "KAPI_80", h, (7.60, 4.00), teras)
    _window(b, "PENCERE_120", W, (0.125, 4.0), 0.6, 1.2)        # gable-end windows
    _window(b, "PENCERE_60", E, (9.875, 6.0), 0.6, 1.0)
    b.label(oyun, (1.0, 4.6))
    b.label(teras, (7.0, 3.0))
    b.label(LABEL_HOL, (6.35, 6.6))
    _piece(b, STAIR_BLOCK, (9.25, 6.0), 0)
    return b.build()


# --------------------------------------------------------------------------
# Roof model (section and elevations are drawn from it)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Roof:
    pitch_deg: float = PITCH_DEG
    knee: float = KNEE
    overhang: float = OVERHANG
    thickness: float = ROOF_T                  # perpendicular to the slope
    floor_z: float = FLOOR_TO_FLOOR            # attic floor
    half: float = DEPTH / 2                    # ridge distance from the outer face

    @property
    def tan(self) -> float:
        return math.tan(math.radians(self.pitch_deg))

    @property
    def vertical_thickness(self) -> float:
        return self.thickness / math.cos(math.radians(self.pitch_deg))

    def under(self, d: float) -> float:
        """z of the underside at distance ``d`` from the nearest outer face (negative outside the wall)."""
        return self.floor_z + self.knee + d * self.tan

    def top(self, d: float) -> float:
        return self.under(d) + self.vertical_thickness

    @property
    def eaves_under(self) -> float:
        return self.under(-self.overhang)

    @property
    def eaves_top(self) -> float:
        return self.top(-self.overhang)

    @property
    def ridge_under(self) -> float:
        return self.under(self.half)

    @property
    def ridge_top(self) -> float:
        return self.top(self.half)

    def outline(self, length: float) -> list[tuple[float, float]]:
        """The 6 points of the roof band across a section of ``length`` (top line, tip drops, underside back)."""
        return [(-self.overhang, self.eaves_top), (self.half, self.ridge_top), (length + self.overhang, self.eaves_top),
                (length + self.overhang, self.eaves_under), (self.half, self.ridge_under), (-self.overhang, self.eaves_under)]


ROOF = Roof()
GROUND_Z = 0.0
SLAB_TOPS = (-FLOOR_TO_FLOOR, 0.0, FLOOR_TO_FLOOR)       # under the basement, between basement / ground, ground / attic
MARKS = ((-FLOOR_TO_FLOOR, "-3.00"), (0.0, "±0.00"), (FLOOR_TO_FLOOR, "+3.00"))
MARK_S = -3.4                                            # section s of the level-mark triangles


# --------------------------------------------------------------------------
# Drawings
# --------------------------------------------------------------------------

@dataclass
class Drawing:
    """One region of the sheet: prims in a local metric frame, the position of that frame's origin on the sheet (cm),
    the class and the title (a prim below the drawing)."""
    key: str
    cls: str
    origin: tuple[float, float]
    prims: list
    title: Optional[Prim] = None
    level: Optional[SheetLevel] = None
    use: str = "ignored"
    extra: dict = field(default_factory=dict)

    @property
    def geometry(self) -> list[Prim]:
        return [p for p in self.prims if p.kind not in ("text", "mtext")]

    @property
    def texts(self) -> list[Prim]:
        return [p for p in self.prims if p.kind in ("text", "mtext")] + ([self.title] if self.title else [])

    def box_m(self) -> list[float]:
        return union_box(prim_box(p) for p in self.geometry)

    def box_cm(self) -> list[float]:
        b = self.box_m()
        ox, oy = self.origin
        return [rnd(ox + CM * b[0], 3), rnd(oy + CM * b[1], 3), rnd(ox + CM * b[2], 3), rnd(oy + CM * b[3], 3)]

    def to_sheet(self, point) -> tuple[float, float]:
        return (rnd(self.origin[0] + CM * point[0], 3), rnd(self.origin[1] + CM * point[1], 3))


def _faces(level: SheetLevel) -> list[Prim]:
    """Wall faces as open two-point polylines: the rings of the wall union cut at every opening (the gap is the
    opening's clear width), each tagged with the wall it lies on (``face:<wall index>``)."""
    union = wall_union(level)
    rings = [canonical_ring(union.exterior.coords)]
    rings += sorted((canonical_ring(r.coords) for r in union.interiors), key=lambda r: (r[0][1], r[0][0]))
    out: list[Prim] = []
    for ring in rings:
        for i, a in enumerate(ring):
            b = ring[(i + 1) % len(ring)]
            length = G.distance(a, b)
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            cuts = []
            for op in level.openings:
                wall = level.walls[op.wall_index]
                wl = G.distance(wall.start, wall.end)
                wx, wy = (wall.end[0] - wall.start[0]) / wl, (wall.end[1] - wall.start[1]) / wl
                if abs(ux * wy - uy * wx) > 1e-9:
                    continue
                dx, dy = op.center[0] - a[0], op.center[1] - a[1]
                if abs(dx * -uy + dy * ux) > wall.thickness / 2 + 1e-6:
                    continue
                t = dx * ux + dy * uy
                c0, c1 = max(0.0, t - op.width / 2), min(length, t + op.width / 2)
                if c1 - c0 > 1e-9:                            # the opening lies on this stretch of the face
                    cuts.append((c0, c1))
            pos = 0.0
            for c0, c1 in sorted(cuts) + [(length, length)]:
                if c0 - pos > 1e-6:
                    p0 = G.snap_point((a[0] + ux * pos, a[1] + uy * pos))
                    p1 = G.snap_point((a[0] + ux * c0, a[1] + uy * c0))
                    out.append(poly(L_WALL, [p0, p1], False, role=f"face:{_owner(level, p0, p1)}"))
                pos = max(pos, c1)
    return out


def _owner(level: SheetLevel, p0, p1) -> int:
    """Index of the wall whose face line contains the segment p0-p1."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    length = G.distance(p0, p1)
    ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
    for i, wall in enumerate(level.walls):
        wl = G.distance(wall.start, wall.end)
        wx, wy = (wall.end[0] - wall.start[0]) / wl, (wall.end[1] - wall.start[1]) / wl
        if abs(ux * wy - uy * wx) > 1e-9:
            continue
        dx, dy = mx - wall.start[0], my - wall.start[1]
        if abs(abs(dx * -wy + dy * wx) - wall.thickness / 2) > 1e-6:
            continue
        if -1e-6 <= dx * wx + dy * wy <= wl + 1e-6:
            return i
    raise ValueError(f"{level.id}: no wall carries the face {p0} -> {p1}")


COLUMN_SIZE = 0.25
COLUMNS = ((0.125, 0.125), (WIDTH - 0.125, 0.125), (WIDTH - 0.125, DEPTH - 0.125), (0.125, DEPTH - 0.125),
           (6.10, 0.125), (6.10, DEPTH - 0.125))                 # four corners and the partition's two feet, inside the bands


def plan_prims(level: SheetLevel) -> list[Prim]:
    prims = _faces(level)
    for k, (cx, cy) in enumerate(COLUMNS):
        h = COLUMN_SIZE / 2
        prims.append(rect(L_COLUMN, cx - h, cy - h, cx + h, cy + h, role=f"column:{k}"))
    for op in level.openings:
        prims.append(insert(L_DOOR if op.kind == "door" else L_WINDOW, op.block, op.center, op.rotation_deg, role=f"open:{op.id}"))
    for piece in level.furniture:
        prims.append(insert(L_FURN, piece.block, piece.center, piece.rotation_deg, role=f"furn:{piece.id}"))
    for room in level.rooms:
        label = level.labels[room.label_index]
        prims.append(mtext(L_TEXT, label.at, label.label_raw.split("\n"), TEXT_LABEL, role=f"label:{room.id}"))
    return prims


def cut_line_prims() -> list[Prim]:
    """The section cut A-A on the ground plan: a dash-dot line along Y at x = CUT_AT, an arm and an arrowhead at each
    end pointing towards -X (the viewing direction), and the letter A."""
    y0, y1 = -1.2, DEPTH + 1.0
    out = [line(L_CUT, (CUT_AT, y0), (CUT_AT, y1), "cut:line", "DASHDOT")]
    for tag, y in (("s", y0), ("n", y1)):
        out.append(line(L_CUT, (CUT_AT, y), (CUT_AT - 0.6, y), f"cut:arm_{tag}"))
        out.append(poly(L_CUT, [(CUT_AT - 0.6, y), (CUT_AT - 0.35, y + 0.1), (CUT_AT - 0.35, y - 0.1)], True, f"cut:head_{tag}"))
        out.append(text(L_TEXT, (CUT_AT + 0.15, y - 0.15), "A", TEXT_TITLE, f"cut:letter_{tag}"))
    return out


def roof_plan_prims() -> list[Prim]:
    o = OVERHANG
    return [rect(L_ROOF_PLAN, -o, -o, WIDTH + o, DEPTH + o, role="roof:outline", linetype="DASHED"),
            line(L_ROOF_PLAN, (-o, DEPTH / 2), (WIDTH + o, DEPTH / 2), "roof:ridge", "DASHED")]


def section_prims() -> list[Prim]:
    """A-A KESİTİ in the frame (s = building y, z = building z), looking towards -X."""
    r = ROOF
    prims: list[Prim] = []
    for k, zt in enumerate(SLAB_TOPS):
        prims.append(rect(L_SEC, 0.0, zt - SLAB, DEPTH, zt, role=f"slab:{k}"))
    bands = ((-FLOOR_TO_FLOOR, -SLAB), (0.0, CEILING), (FLOOR_TO_FLOOR, None))      # wall pieces between the slab bands
    for side, (outer, inner) in (("S", (0.0, T_OUT)), ("N", (DEPTH, DEPTH - T_OUT))):
        for k, (z0, z1) in enumerate(bands):
            top_out = z1 if z1 is not None else r.under(0.0)
            top_in = z1 if z1 is not None else r.under(T_OUT)
            role_out = f"knee:{side}" if z1 is None else f"wall_out:{side}:{k}"
            prims.append(line(L_SEC, (outer, z0), (outer, top_out), role_out))
            prims.append(line(L_SEC, (inner, z0), (inner, top_in), f"wall_in:{side}:{k}"))
    prims.append(line(L_GROUND, (-3.0, GROUND_Z), (0.0, GROUND_Z), "ground:S"))
    prims.append(line(L_GROUND, (DEPTH, GROUND_Z), (DEPTH + 3.0, GROUND_Z), "ground:N"))
    prims.append(poly(L_SEC_ROOF, r.outline(DEPTH), True, "roof"))
    for k, (z, label) in enumerate(MARKS):
        prims.append(poly(L_LEVEL, [(MARK_S - 0.15, z + 0.25), (MARK_S + 0.15, z + 0.25), (MARK_S, z)], True, f"mark_tri:{k}"))
        x1 = -3.0 if z == GROUND_Z else 0.0
        prims.append(line(L_LEVEL, (MARK_S, z), (x1, z), f"mark_line:{k}"))
        prims.append(text(L_TEXT, (MARK_S - 1.3, z + 0.05), label, TEXT_MARK, f"mark_text:{k}"))
    return prims


def south_prims(openings: list) -> list[Prim]:
    """GÜNEY GÖRÜNÜŞÜ: x = metres from the facade's west end, z = building z. ``openings`` = [(opening, x_left)]."""
    r = ROOF
    prims = [line(L_GROUND, (-3.0, GROUND_Z), (WIDTH + 3.0, GROUND_Z), "ground"),
             poly(L_ELEV, [(0, 0), (WIDTH, 0), (WIDTH, r.eaves_under), (0, r.eaves_under)], True, "wall"),
             poly(L_ELEV, [(-OVERHANG, r.eaves_under), (WIDTH + OVERHANG, r.eaves_under), (WIDTH + OVERHANG, r.ridge_top),
                           (-OVERHANG, r.ridge_top)], True, "roof"),
             line(L_ELEV, (-OVERHANG, r.eaves_top), (WIDTH + OVERHANG, r.eaves_top), "fascia"),
             rect(L_HATCH, 0.0, 0.0, WIDTH, PLINTH, role="plinth"),
             hatch(L_HATCH, [(0, 0), (WIDTH, 0), (WIDTH, PLINTH), (0, PLINTH)], "ANSI31", 3.0, "plinth_hatch")]
    prims += _opening_rects(openings)
    prims += [text(L_TEXT, (WIDTH + 1.2, 2.5), "SIVA", TEXT_NOTE, "note:render"), line(L_ELEV, (WIDTH + 1.1, 2.6), (WIDTH - 0.4, 2.6), "leader:render"),
              text(L_TEXT, (WIDTH + 1.2, 0.25), "TAŞ KAPLAMA", TEXT_NOTE, "note:stone"),
              line(L_ELEV, (WIDTH + 1.1, 0.3), (WIDTH - 0.4, 0.3), "leader:stone"),
              text(L_TEXT, (WIDTH + 1.2, 5.4), "KİREMİT", TEXT_NOTE, "note:roof"), line(L_ELEV, (WIDTH + 1.1, 5.5), (WIDTH - 0.4, 5.5), "leader:roof")]
    return prims


def east_prims(openings: list) -> list[Prim]:
    """DOĞU GÖRÜNÜŞÜ: the gable end seen from the east, x = metres from the facade's south end (the left end)."""
    r = ROOF
    prims = [line(L_GROUND, (-3.0, GROUND_Z), (DEPTH + 3.0, GROUND_Z), "ground"),
             poly(L_ELEV, [(0, 0), (DEPTH, 0), (DEPTH, r.under(0.0)), (r.half, r.ridge_under), (0, r.under(0.0))], True, "wall"),
             poly(L_SEC_ROOF, r.outline(DEPTH), True, "roof")]
    prims += _opening_rects(openings)
    prims += [text(L_TEXT, (DEPTH + 1.2, 2.5), "SIVA", TEXT_NOTE, "note:render"), line(L_ELEV, (DEPTH + 1.1, 2.6), (DEPTH - 0.4, 2.6), "leader:render")]
    return prims


def _opening_rects(openings) -> list[Prim]:
    out = []
    for op, x_left, z0, z1 in openings:
        layer = L_ELEV_DOOR if op.kind == "door" else L_ELEV_WIN
        out.append(rect(layer, x_left, z0, x_left + op.width, z1, role=f"open:{op.id}"))
        if op.kind == "door":
            out.append(line(layer, (x_left + op.width - 0.15, z0 + 1.0), (x_left + op.width - 0.15, z0 + 1.15), role=f"handle:{op.id}"))
    return out


# Site plan (building frame, metres)
PLOT = ((-6.0, -7.0), (18.0, -7.0), (18.0, 13.0), (-6.0, 13.0))
PLOT_WALL_T = 0.20
PLOT_WALL_INSET = 0.05                                 # outer face of the plot wall, inside the boundary line
PARKING = ((11.0, 8.5), (16.0, 8.5), (16.0, 12.5), (11.0, 12.5))
ROAD = ((-8.0, 14.5), (20.0, 14.5), (20.0, 18.5), (-8.0, 18.5))
TREES = ((-3.5, -3.5), (13.5, -4.5), (-3.0, 10.0))
NORTH_AT = (15.0, 2.0)
SITE_LABELS = (("OTOPARK", (12.3, 10.2)), ("BAHÇE", (1.5, -4.0)), ("YOL", (6.5, 16.2)))


def plot_wall_centre() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Centre lines (corner to corner) of the four plot walls, 0.20 m thick, outer face PLOT_WALL_INSET inside the line."""
    d = PLOT_WALL_INSET + PLOT_WALL_T / 2
    (x0, y0), (x1, y1) = PLOT[0], PLOT[2]
    c = [(x0 + d, y0 + d), (x1 - d, y0 + d), (x1 - d, y1 - d), (x0 + d, y1 - d)]
    return [(c[i], c[(i + 1) % 4]) for i in range(4)]


def site_prims() -> list[Prim]:
    (x0, y0), (x1, y1) = PLOT[0], PLOT[2]
    prims = [poly(L_PLOT, PLOT, True, "plot", "DASHDOT")]
    o, i = PLOT_WALL_INSET, PLOT_WALL_INSET + PLOT_WALL_T
    prims.append(rect(L_PLOT_WALL, x0 + o, y0 + o, x1 - o, y1 - o, role="plot_wall_outer"))
    prims.append(rect(L_PLOT_WALL, x0 + i, y0 + i, x1 - i, y1 - i, role="plot_wall_inner"))
    prims.append(rect(L_BUILDING, 0.0, 0.0, WIDTH, DEPTH, role="building"))
    prims.append(poly(L_ROAD, PARKING, True, "parking"))
    prims.append(poly(L_ROAD, ROAD, True, "road"))
    prims += [insert(L_TREE, "AGAC", t, 0.0, f"tree:{k}") for k, t in enumerate(TREES)]
    prims.append(insert(L_NORTH, "KUZEY", NORTH_AT, 0.0, "north"))
    prims.append(text(L_TEXT, (NORTH_AT[0] - 0.2, NORTH_AT[1] + 0.95), "N", TEXT_TITLE, "north_n"))
    for name, at in SITE_LABELS:
        prims.append(text(L_TEXT, at, name, TEXT_MARK, f"label:{name}"))
    return prims


def legend_prims() -> list[Prim]:
    """LEJANT: a box with five samples (local frame = the box's lower left corner, 18.0 x 7.5 m)."""
    prims = [rect(L_LEGEND, 0.0, 0.0, 18.0, 7.5, role="box")]
    rows = (6.5, 5.3, 4.1, 2.9, 1.5)
    prims += [line(L_LEGEND, (0.5, rows[0]), (2.5, rows[0]), "wall_a"), line(L_LEGEND, (0.5, rows[0] + 0.25), (2.5, rows[0] + 0.25), "wall_b"),
              text(L_TEXT, (3.2, rows[0] - 0.05), "DUVAR", TEXT_NOTE)]
    prims += [rect(L_LEGEND, 1.1, rows[1] - 0.1, 1.4, rows[1] + 0.2, role="column"), text(L_TEXT, (3.2, rows[1] - 0.05), "KOLON", TEXT_NOTE)]
    prims += [line(L_LEGEND, (0.6, rows[2]), (0.6, rows[2] + 0.9)), arc(L_LEGEND, (0.6, rows[2]), 0.9, 0.0, 90.0), text(L_TEXT, (3.2, rows[2] - 0.05), "KAPI", TEXT_NOTE)]
    prims += [line(L_LEGEND, (0.5, rows[3]), (2.5, rows[3]), "dashed", "DASHED"), text(L_TEXT, (3.2, rows[3] - 0.05), "ÇATI ÇIKIŞI", TEXT_NOTE)]
    prims += [rect(L_LEGEND, 0.5, rows[4] - 0.1, 2.5, rows[4] + 0.3, role="hatch_box"),
              hatch(L_LEGEND, [(0.5, rows[4] - 0.1), (2.5, rows[4] - 0.1), (2.5, rows[4] + 0.3), (0.5, rows[4] + 0.3)], "ANSI31", 3.0, "hatch"),
              text(L_TEXT, (3.2, rows[4] - 0.05), "TAŞ KAPLAMA", TEXT_NOTE)]
    return prims


TITLE_BLOCK = (50.0, 0.0, 110.0, 3.6)                    # metres on the sheet (frame edge to frame edge)
TITLE_CELLS = (("PROJE", "ÖRNEK KONUT"), ("ÇİZEN", "WENART"), ("ÖLÇEK 1/100", ""), ("TARİH", "08.10.2026"), ("PAFTA", "A-01"))


def title_block_prims() -> list[Prim]:
    x0, y0, x1, y1 = TITLE_BLOCK
    prims = [rect(L_TITLEBLOCK, x0, y0, x1, y1, role="box"), line(L_TITLEBLOCK, (x0, 1.8), (x1, 1.8), "divider_h")]
    step = (x1 - x0) / len(TITLE_CELLS)
    for k, (label, value) in enumerate(TITLE_CELLS):
        if k:
            prims.append(line(L_TITLEBLOCK, (x0 + k * step, y0), (x0 + k * step, y1), f"divider:{k}"))
        prims.append(text(L_TEXT, (x0 + k * step + 0.2, 2.35), label, TEXT_NOTE, f"cell_label:{k}"))
        if value:
            prims.append(text(L_TEXT, (x0 + k * step + 0.2, 0.7), value, 40.0, f"cell_value:{k}"))
    return prims


# --------------------------------------------------------------------------
# The sheet
# --------------------------------------------------------------------------

# Position (cm) of each local origin: plans at their own offsets (row 1), section / elevations (row 2), site plan right.
ORIGINS = {"basement": (600.0, 4200.0), "basement_alt": (2300.0, 4175.0), "ground": (4000.0, 4040.0), "attic": (5750.0, 4075.0),
           "section": (1200.0, 2000.0), "south": (4000.0, 1990.0), "east": (6200.0, 1980.0), "site": (8500.0, 2700.0),
           "legend": (8600.0, 700.0), "titleblock": (0.0, 0.0)}
TITLE_DROP = 0.7                                          # metres between a drawing's box and its title's top
BRIEF_07 = {"style": "Modern minimal, light oak floor, white walls, warm daylight",
            "exterior": {"facade": "white render", "roof": "clay tiles", "window_frame": "anthracite aluminium"}}


@dataclass
class SheetProject:
    name: str
    brief: dict
    levels: list                       # SheetLevel: L-1, L-1b, L0, L1
    drawings: list                     # Drawing in construction order
    roof: Roof = ROOF

    def drawing(self, key: str) -> Drawing:
        return next(d for d in self.drawings if d.key == key)

    def reading_order(self) -> list[Drawing]:
        """Top to bottom by box top (y up), then left to right. Equal tops (within 1 mm) are refused: a tie would make
        the region ids depend on the reader's tolerance."""
        ordered = sorted(self.drawings, key=lambda d: (-d.box_cm()[3], d.box_cm()[0]))
        tops = [d.box_cm()[3] for d in ordered]
        if any(abs(a - b) < 0.1 for a, b in zip(tops, tops[1:])):
            raise ValueError(f"{self.name}: two regions have the same box top: {tops}")
        return ordered

    def region_ids(self) -> dict[str, str]:
        return {d.key: f"r{i}" for i, d in enumerate(self.reading_order(), start=1)}


def _below(prims: list, title: str, kind: str) -> Prim:
    """Title prim below the drawing: top left at the box's left edge, ``TITLE_DROP`` m under the box bottom."""
    box = union_box(prim_box(p) for p in prims if p.kind not in ("text", "mtext"))
    at = (box[0], box[1] - TITLE_DROP)
    return mtext(L_TEXT, at, [title], TEXT_TITLE, "title") if kind == "mtext" else text(L_TEXT, (at[0], at[1] - TEXT_TITLE / CM), title, TEXT_TITLE, "title")


# The elevations: the facade's wall index and the direction the viewer standing outside looks (building XY).
VIEWS = {"south": {"wall": S, "look": (0.0, 1.0)}, "east": {"wall": E, "look": (-1.0, 0.0)}}


def view_bearing_deg(side: str) -> float:
    """Direction the viewer looks, degrees counter-clockwise from +X (south elevation 90, east elevation 180)."""
    look = VIEWS[side]["look"]
    return rnd(math.degrees(math.atan2(look[1], look[0])) % 360.0)


def along_facade(side: str, point) -> float:
    """Metres from the facade's left end seen from outside to ``point``: a viewer looking along (dx, dy) with up = +Z
    has the right-hand direction (dy, -dx), so the south facade (looking north) runs west to east (x) and the east
    facade (looking west) from its south end to its north end (y). The facades start at 0."""
    dx, dy = VIEWS[side]["look"]
    return rnd(point[0] * dy - point[1] * dx)


def _elevation_openings(levels, side: str) -> list:
    """The openings of ``levels`` on the facade ``side`` ('south' or 'east') that stand above the ground line, as
    (opening, x from the facade's left end seen from outside (its left edge), z0, z1)."""
    out = []
    for level in levels:
        for op in level.openings:
            if op.wall_index != VIEWS[side]["wall"]:
                continue
            z0 = level.floor_z + op.sill
            z1 = z0 + op.clear_height
            if z1 <= GROUND_Z + 1e-9:
                continue                                      # below the ground line: not visible
            out.append((op, rnd(along_facade(side, op.center) - op.width / 2), rnd(z0), rnd(z1)))
    return out


def project_07() -> SheetProject:
    lv_b, lv_a, lv_0, lv_1 = level_bodrum(), level_bodrum(alt=True), level_zemin(), level_cati()
    drawings = []

    def plan(key, level, title, extra=None, extras=()):
        prims = plan_prims(level) + list(extras)
        d = Drawing(key, level.region_class, ORIGINS[key], prims, level=level, use="read", extra=extra or {})
        d.title = _below(prims, title, "mtext")
        drawings.append(d)

    plan("basement", lv_b, lv_b.title_raw)
    plan("basement_alt", lv_a, lv_a.title_raw)
    plan("ground", lv_0, lv_0.title_raw, extras=cut_line_prims())
    plan("attic", lv_1, lv_1.title_raw, extras=roof_plan_prims())

    def sketch(key, cls, prims, title, use, kind="text", extra=None):
        d = Drawing(key, cls, ORIGINS[key], prims, use=use, extra=extra or {})
        if title:
            d.title = _below(prims, title, kind)
        drawings.append(d)
        return d

    sketch("section", "section", section_prims(), "A-A KESİTİ", "heights")
    levels_up = [lv_0, lv_1]                       # openings above the ground line; the basement is below it
    sketch("south", "elevation", south_prims(_elevation_openings(levels_up, "south")), "GÜNEY GÖRÜNÜŞÜ", "exterior",
           extra={"side": "south", "openings": _elevation_openings(levels_up, "south")})
    sketch("east", "elevation", east_prims(_elevation_openings(levels_up, "east")), "DOĞU GÖRÜNÜŞÜ", "exterior",
           extra={"side": "east", "openings": _elevation_openings(levels_up, "east")})
    sketch("site", "site_plan", site_prims(), "VAZİYET PLANI", "exterior")
    sketch("legend", "legend", legend_prims(), "LEJANT", "ignored")
    sketch("titleblock", "title_block", title_block_prims(), None, "ignored")
    return SheetProject(PROJECT, BRIEF_07, [lv_b, lv_a, lv_0, lv_1], drawings)
