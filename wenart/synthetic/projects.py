"""The five synthetic projects (docs/milestone2.md §1, docs/milestone6.md §3, docs/synthetic.md).

Everything is written out by hand so the ground truth is readable: room
rectangles, doors with the room they open into, windows, furniture with the
block name, position and rotation, and the dimension chains. ``finalise``
(via ``LevelBuilder.build``) derives rooms, IDs and links and refuses layouts
that are inconsistent.

- synthetic-01..03 (Milestone 2): DXF, vector PDF, scan and photo; deliberate conflicts.
- synthetic-04 (Milestone 6): one level on the 3rd floor drawn twice (DXF and
  vector PDF, both with furniture), two L-shaped rooms, an armchair at 45°.
- synthetic-05 (Milestone 6): notched outline, a floor-plan DXF without
  furniture plus a furniture-plan DXF, an en-suite, a study (room type
  ``other``), a style photo and ``polish: false``.

Coordinates: metres in the building frame (origin = outer corner of the
outer wall, X right, Y up). Rotations: degrees counter-clockwise.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.synthetic.model import Level, LevelBuilder, Opening, format_metres

REPO_ROOT = Path(__file__).resolve().parents[2]

BRIEF_01 = {"style": "Scandinavian, light oak floor, white walls, linen textiles, warm daylight"}
BRIEF_03 = {"styles": [
    "Modern minimal, polished concrete floor, charcoal and white, brass details, cool daylight",
    "Warm Mediterranean, terracotta floor, cream plaster walls, rattan and linen, golden evening light",
]}
BRIEF_04 = {"style": "Japandi, walnut floor, cream walls, warm daylight, linen and paper lamps"}
BRIEF_05 = {"style": "Modern, white walls, warm daylight, linen textiles, brass details",
            "style_photos": ["salon_referans.jpg"], "polish": False}
# synthetic-05's style photo: our own Milestone 4 render of the synthetic-03 Salon (no third-party image).
STYLE_PHOTO_05 = "tests/fixtures/style_photo_synthetic-03_salon.jpg"


@dataclass
class PageSpec:
    """One drawn page of a level. ``omit_openings`` holds indices into
    ``level.openings`` that this page leaves out (deliberate conflicts)."""
    level: Level
    page_class: str = "floor_plan"
    title_raw: Optional[str] = None
    omit_openings: tuple[int, ...] = ()
    with_furniture: bool = True
    with_dimensions: bool = True

    @property
    def title(self) -> str:
        return self.title_raw or self.level.title_raw

    def openings(self) -> list[Opening]:
        return [o for i, o in enumerate(self.level.openings) if i not in self.omit_openings]

    def furniture(self):
        return self.level.furniture if self.with_furniture else []

    def dimensions(self):
        return self.level.dimensions if self.with_dimensions else []


@dataclass
class DxfDoc:
    file: str
    page: PageSpec


@dataclass
class PdfDoc:
    file: str
    pages: list[PageSpec]
    hidden: bool = False  # written under truth/, not a project document


@dataclass
class RasterDoc:
    file: str
    source_pdf: str        # project-relative path of the PDF it is made from
    source_page: int       # 1-based
    kind: str              # scan | photo
    page: PageSpec
    seed: int


@dataclass
class Project:
    """One synthetic project. ``warnings`` are the extra warnings the pipeline
    must report (besides the per-level ceiling-height warning).
    ``style_photos`` maps a file name in ``<project>/style_photos/`` to its
    source file (relative to the repo root, or absolute); ``generate_project``
    copies it byte for byte. The brief names the same files (``style_photos:``)."""
    name: str
    brief: Optional[dict]
    levels: list[Level]
    documents: list
    conflicts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    style_photos: dict[str, str] = field(default_factory=dict)

    def style_photo_sources(self) -> dict[str, Path]:
        """``style_photos`` with every source resolved (relative paths join the repo root)."""
        out = {}
        for name, src in self.style_photos.items():
            path = Path(src)
            out[name] = path if path.is_absolute() else REPO_ROOT / path
        return out


# --------------------------------------------------------------------------
# synthetic-01: L0 DXF (furniture in 3 of 5 rooms), L1 vector PDF + scan
# --------------------------------------------------------------------------

def level_01_zemin() -> Level:
    b = LevelBuilder("ZEMİN KAT PLANI", 9.6, 7.2)
    # Inner walls (face to face). Outer walls are 0..3: bottom, right, top, left.
    a = b.wall((5.30, 0.25), (5.30, 6.95))   # 4: left column | right column
    b2 = b.wall((0.25, 5.20), (5.25, 5.20))  # 5: Salon | Mutfak
    c = b.wall((5.35, 3.80), (9.35, 3.80))   # 6: Yatak Odası | Hol + Banyo
    d = b.wall((7.00, 3.85), (7.00, 6.95))   # 7: Hol | Banyo
    del b2
    # Rooms: Salon 5.0 x 4.9 = 24.50 (label matches), Mutfak 8.50, Yatak 14.00, Hol 4.96, Banyo 7.13
    b.label("SALON 24,50 m²", (1.0, 2.5))
    b.label("MUTFAK", (1.0, 6.0))
    b.label("YATAK ODASI", (6.0, 1.3))
    b.label("HOL", (5.6, 5.0))
    b.label("BANYO", (7.4, 5.1))
    # Doors
    b.door(2, (6.15, 7.075), 90, "HOL")             # entrance, top wall
    b.door(a, (5.30, 4.50), 90, "SALON 24,50 m²")
    b.door(a, (5.30, 6.10), 80, "MUTFAK")
    b.door(c, (5.95, 3.80), 80, "YATAK ODASI")
    b.door(d, (7.00, 5.40), 80, "BANYO")
    # Windows
    b.window(0, (1.50, 0.125), 180)
    b.window(0, (3.80, 0.125), 120)
    b.window(0, (7.35, 0.125), 180)
    b.window(3, (0.125, 2.70), 120)
    b.window(2, (2.75, 7.075), 120)
    b.window(2, (8.20, 7.075), 60)
    # Furniture: Salon, Yatak Odası, Banyo only
    b.furniture("KANEPE_3LU", (2.75, 4.65), 0)
    b.furniture("SEHPA", (2.75, 3.50), 0)
    b.furniture("TV_UNITESI", (2.75, 0.525), 180)
    b.furniture("KOLTUK", (4.50, 3.40), 270)
    b.furniture("KITAPLIK", (0.475, 4.30), 90)
    b.furniture("YATAK_CIFT", (7.80, 2.70), 0)
    b.furniture("KOMIDIN", (6.65, 3.50), 0)
    b.furniture("KOMIDIN", (8.95, 3.50), 0)
    b.furniture("DOLAP", (9.00, 1.50), 270)
    b.furniture("KLOZET", (8.95, 4.40), 270)
    b.furniture("LAVABO", (9.075, 5.40), 270)
    b.furniture("DUS", (7.55, 6.45), 0)
    b.furniture("CAMASIR_MAK", (8.95, 6.55), 0)
    b.dimension_chain("bottom", [0.0, 5.30, 9.60])
    b.dimension_chain("left", [0.0, 5.20, 7.20])
    return b.build()


def level_01_birinci() -> Level:
    b = LevelBuilder("1. KAT PLANI", 9.6, 7.2)
    a = b.wall((4.30, 0.25), (4.30, 6.95))   # 4
    c = b.wall((6.00, 0.25), (6.00, 6.95))   # 5
    b.wall((0.25, 4.20), (4.25, 4.20))       # 6: Ebeveyn | Çocuk
    b.wall((6.05, 4.00), (9.35, 4.00))       # 7: Yatak | Banyo
    # Rooms: Ebeveyn 15.60, Çocuk 10.80, Hol 10.72, Yatak 12.21, Banyo 9.57
    b.label("EBEVEYN YATAK ODASI", (0.5, 2.0))
    b.label("ÇOCUK ODASI", (0.6, 5.5))
    b.label("HOL", (4.6, 3.5))
    b.label("YATAK ODASI", (6.4, 1.8))
    b.label("BANYO", (6.4, 5.4))
    b.door(a, (4.30, 2.00), 90, "EBEVEYN YATAK ODASI")
    b.door(a, (4.30, 5.50), 80, "ÇOCUK ODASI")
    b.door(c, (6.00, 2.00), 90, "YATAK ODASI")
    b.door(c, (6.00, 5.50), 80, "BANYO")
    b.window(0, (2.25, 0.125), 180)
    b.window(0, (7.70, 0.125), 180)
    b.window(3, (0.125, 2.20), 120)
    b.window(2, (2.25, 7.075), 120)
    b.window(2, (5.15, 7.075), 60)
    b.window(2, (7.70, 7.075), 60)
    b.dimension_chain("bottom", [0.0, 4.30, 6.00, 9.60])
    b.dimension_chain("left", [0.0, 4.20, 7.20])
    return b.build()


def project_01() -> Project:
    l0 = level_01_zemin()
    l1 = level_01_birinci()
    pdf = PdfDoc("1_kat.pdf", [PageSpec(l1)])
    return Project(
        name="synthetic-01",
        brief=BRIEF_01,
        levels=[l0, l1],
        documents=[
            DxfDoc("zemin_kat.dxf", PageSpec(l0)),
            pdf,
            RasterDoc("1_kat_scan.png", "1_kat.pdf", 1, "scan", pdf.pages[0], seed=101),
        ],
    )


# --------------------------------------------------------------------------
# synthetic-02: one level, scan + phone photo only, furniture in every room
# --------------------------------------------------------------------------

def level_02_zemin() -> Level:
    b = LevelBuilder("ZEMİN KAT PLANI", 8.4, 6.6)
    a = b.wall((4.50, 0.25), (4.50, 6.35))   # 4: Salon/Mutfak | Yatak/Antre/Banyo
    c = b.wall((0.25, 4.20), (8.15, 4.20))   # 5: lower rooms | upper rooms
    d = b.wall((6.20, 4.25), (6.20, 6.35))   # 6: Antre | Banyo
    # Rooms: Salon 16.38, Mutfak 8.82, Antre 3.36, Banyo 3.99, Yatak 14.04
    b.label("SALON", (1.0, 2.0))
    b.label("MUTFAK", (0.5, 4.45))
    b.label("ANTRE", (4.7, 5.0))
    b.label("BANYO", (6.4, 4.95))
    b.label("YATAK ODASI", (5.4, 0.5))
    b.door(2, (5.20, 6.475), 90, "ANTRE")           # entrance
    b.door(a, (4.50, 4.75), 80, "MUTFAK")
    b.door(d, (6.20, 4.75), 80, "BANYO")
    b.door(c, (5.25, 4.20), 80, "YATAK ODASI")
    b.door(c, (3.90, 4.20), 90, "SALON")
    b.window(0, (2.35, 0.125), 180)
    b.window(0, (6.35, 0.125), 180)
    b.window(3, (0.125, 2.20), 120)
    b.window(2, (2.35, 6.475), 120)
    b.window(2, (7.70, 6.475), 60)
    # Salon
    b.furniture("KANEPE_2LI", (2.35, 3.65), 0)
    b.furniture("SEHPA", (2.35, 2.50), 0)
    b.furniture("TV_UNITESI", (2.35, 0.525), 180)
    b.furniture("KOLTUK", (3.90, 2.50), 270)
    # Mutfak
    b.furniture("TEZGAH", (1.50, 6.00), 0)
    b.furniture("EVIYE", (0.75, 6.00), 0)
    b.furniture("OCAK", (2.25, 6.00), 0)
    b.furniture("BUZDOLABI", (3.15, 6.00), 0)
    b.furniture("YEMEK_MASASI", (2.40, 4.95), 0)
    # Antre
    b.furniture("KITAPLIK", (5.925, 5.80), 270)
    # Banyo
    b.furniture("KLOZET", (7.75, 4.60), 270)
    b.furniture("LAVABO", (7.875, 5.35), 270)
    b.furniture("DUS", (6.75, 5.85), 0)
    b.furniture("CAMASIR_MAK", (7.75, 6.00), 0)
    # Yatak Odası
    b.furniture("YATAK_CIFT", (6.90, 3.10), 0)
    b.furniture("KOMIDIN", (7.875, 3.90), 0)
    b.furniture("DOLAP", (4.90, 1.60), 90)
    b.furniture("CALISMA_MASASI", (7.75, 1.20), 270)
    b.furniture("SANDALYE", (7.00, 1.20), 90)
    b.dimension_chain("bottom", [0.0, 4.50, 8.40])
    b.dimension_chain("left", [0.0, 4.20, 6.60])
    return b.build()


def project_02() -> Project:
    l0 = level_02_zemin()
    pdf = PdfDoc("truth/plan.pdf", [PageSpec(l0)], hidden=True)
    return Project(
        name="synthetic-02",
        brief=None,
        levels=[l0],
        documents=[
            pdf,
            RasterDoc("plan_scan.png", "truth/plan.pdf", 1, "scan", pdf.pages[0], seed=201),
            RasterDoc("plan_photo.jpg", "truth/plan.pdf", 1, "photo", pdf.pages[0], seed=202),
        ],
    )


# --------------------------------------------------------------------------
# synthetic-03: 3-page PDF (Bodrum, Zemin, 1. Kat) + furniture-plan DXF of Zemin
# --------------------------------------------------------------------------

W3, H3 = 10.2, 7.8


def level_03_bodrum() -> Level:
    b = LevelBuilder("BODRUM KAT PLANI", W3, H3)
    a = b.wall((4.30, 0.25), (4.30, 7.55))   # 4
    c = b.wall((6.00, 0.25), (6.00, 7.55))   # 5
    b.wall((0.25, 3.80), (4.25, 3.80))       # 6: Kiler | Kiler
    d = b.wall((6.05, 5.50), (9.95, 5.50))   # 7: Yatak | WC + Banyo
    b.wall((8.00, 5.55), (8.00, 7.55))       # 8: WC | Banyo
    # Rooms: Kiler 14.00, Kiler 14.80, Hol 11.68, Yatak 20.28, WC 3.80, Banyo 3.80
    b.label("KİLER", (1.0, 2.0))
    b.label("KİLER", (1.0, 5.7))
    b.label("HOL", (4.6, 3.9))
    b.label("YATAK ODASI", (6.5, 2.9))
    b.label("WC", (6.5, 6.5))
    b.label("BANYO", (8.4, 6.5))
    b.door(a, (4.30, 2.00), 80, (2.0, 2.0))        # into the lower Kiler
    b.door(a, (4.30, 5.70), 80, (2.0, 5.7))        # into the upper Kiler
    b.door(c, (6.00, 2.85), 90, "YATAK ODASI")
    b.door(c, (6.00, 6.55), 80, "WC")
    b.door(d, (9.00, 5.50), 80, "BANYO")
    b.window(0, (8.00, 0.125), 60)
    b.window(3, (0.125, 2.00), 60)
    b.window(3, (0.125, 5.70), 60)
    b.dimension_chain("bottom", [0.0, 4.30, 6.00, W3])
    # Deliberate conflict: the first left segment measures 3,80 but prints 3,99 (5 %).
    b.dimension_chain("left", [0.0, 3.80, H3], text_overrides={0: "3,99"})
    return b.build()


def level_03_zemin() -> Level:
    b = LevelBuilder("ZEMİN KAT PLANI", W3, H3)
    a = b.wall((5.30, 0.25), (5.30, 7.55))   # 4: Salon/Mutfak/Antre | Hol
    c = b.wall((7.00, 0.25), (7.00, 7.55))   # 5: Hol | Yatak/WC/Kiler
    b.wall((0.25, 5.00), (5.25, 5.00))       # 6: Salon | Mutfak + Antre
    d = b.wall((3.60, 5.05), (3.60, 7.55))   # 7: Mutfak | Antre
    b.wall((7.05, 5.50), (9.95, 5.50))       # 8: Yatak | WC + Kiler
    e = b.wall((8.50, 5.55), (8.50, 7.55))   # 9: WC | Kiler
    # Rooms: Salon 23.50 (label says 24,00 -> 2 % off, within tolerance), Mutfak 8.25,
    # Antre 4.00, Hol 11.68, Yatak 15.08, WC 2.80, Kiler 2.80
    b.label("SALON 24,00 m²", (1.0, 2.5))
    b.label("MUTFAK", (0.6, 6.3))
    b.label("ANTRE", (3.8, 5.3))
    b.label("HOL", (5.6, 4.0))
    b.label("YATAK ODASI", (7.3, 2.6))
    b.label("WC", (7.3, 6.5))
    b.label("KİLER", (8.7, 7.2))
    b.door(2, (4.45, 7.675), 90, "ANTRE")           # entrance
    b.door(a, (5.30, 6.30), 80, "HOL")
    b.door(d, (3.60, 6.30), 80, "MUTFAK")
    b.door(a, (5.30, 2.60), 90, "SALON 24,00 m²")
    b.door(c, (7.00, 2.85), 90, "YATAK ODASI")
    b.door(c, (7.00, 6.55), 80, "WC")
    b.door(e, (8.50, 6.55), 80, "KİLER")
    b.window(0, (2.75, 0.125), 180)
    b.window(0, (9.30, 0.125), 120)
    b.window(3, (0.125, 2.60), 120)
    b.window(2, (1.90, 7.675), 120)   # Mutfak window: index 10, missing on the PDF page
    b.window(2, (9.25, 7.675), 60)
    b.window(1, (10.075, 2.85), 120)
    # Furniture (only on the furniture-plan DXF)
    b.furniture("KANEPE_3LU", (2.50, 4.45), 0)
    b.furniture("KOLTUK", (4.50, 4.40), 270)
    b.furniture("KOLTUK", (0.75, 3.90), 90)
    b.furniture("SEHPA", (2.50, 3.30), 0)
    b.furniture("TV_UNITESI", (2.50, 0.525), 180)
    b.furniture("KITAPLIK", (4.70, 1.00), 270)
    b.furniture("TEZGAH", (1.50, 7.20), 0)
    b.furniture("EVIYE", (0.75, 7.20), 0)
    b.furniture("OCAK", (2.25, 7.20), 0)
    b.furniture("BUZDOLABI", (3.15, 7.15), 0)
    b.furniture("YEMEK_MASASI", (1.60, 6.00), 0)
    b.furniture("SANDALYE", (1.20, 5.30), 180)
    b.furniture("SANDALYE", (2.00, 5.30), 180)
    b.furniture("YATAK_CIFT", (8.50, 4.40), 0)
    b.furniture("KOMIDIN", (7.35, 5.20), 0)
    b.furniture("KOMIDIN", (9.65, 5.20), 0)
    b.furniture("DOLAP", (8.00, 0.60), 180)
    b.furniture("SIFONYER", (9.65, 1.50), 270)
    b.furniture("KLOZET", (8.05, 5.95), 270)
    b.furniture("LAVABO", (8.175, 7.10), 270)
    b.furniture("BLOK_A", (9.65, 6.50), 90, size=(1.2, 0.5))   # unknown type, footprint only
    b.dimension_chain("bottom", [0.0, 5.30, 7.00, W3])
    b.dimension_chain("left", [0.0, 5.00, H3])
    return b.build()


def level_03_birinci() -> Level:
    b = LevelBuilder("1. KAT PLANI", W3, H3)
    a = b.wall((4.30, 0.25), (4.30, 7.55))   # 4
    c = b.wall((6.00, 0.25), (6.00, 7.55))   # 5
    b.wall((0.25, 4.20), (4.25, 4.20))       # 6: Ebeveyn | Çocuk
    d = b.wall((6.05, 4.20), (9.95, 4.20))   # 7: Yatak | Banyo + Balkon
    b.wall((8.00, 4.25), (8.00, 7.55))       # 8: Banyo | Balkon
    # Rooms: Ebeveyn 15.60, Çocuk 13.20, Hol 11.68, Yatak 15.21, Banyo 6.27, Balkon 6.27
    b.label("EBEVEYN YATAK ODASI", (0.5, 2.0))
    b.label("ÇOCUK ODASI", (0.6, 5.9))
    b.label("HOL", (4.6, 3.9))
    b.label("YATAK ODASI", (6.4, 2.0))
    b.label("BANYO", (6.3, 5.9))
    b.label("BALKON", (8.3, 5.9))
    b.door(a, (4.30, 2.00), 90, "EBEVEYN YATAK ODASI")
    b.door(a, (4.30, 5.90), 80, "ÇOCUK ODASI")
    b.door(c, (6.00, 2.00), 90, "YATAK ODASI")
    b.door(c, (6.00, 5.90), 80, "BANYO")
    b.door(d, (9.00, 4.20), 80, "BALKON")
    b.window(0, (2.25, 0.125), 180)
    b.window(0, (8.00, 0.125), 180)
    b.window(3, (0.125, 2.20), 120)
    b.window(3, (0.125, 5.90), 120)
    b.window(2, (2.25, 7.675), 120)
    b.window(2, (7.00, 7.675), 60)
    b.window(2, (9.00, 7.675), 180)
    b.dimension_chain("bottom", [0.0, 4.30, 6.00, W3])
    b.dimension_chain("left", [0.0, 4.20, H3])
    return b.build()


def project_03() -> Project:
    lb = level_03_bodrum()
    l0 = level_03_zemin()
    l1 = level_03_birinci()
    missing_window = 10  # index into l0.openings: the Mutfak window the PDF page forgot
    assert l0.openings[missing_window].block == "PENCERE_120" and l0.openings[missing_window].center[1] == 7.675
    pdf = PdfDoc("kat_planlari.pdf", [
        PageSpec(lb),
        PageSpec(l0, omit_openings=(missing_window,), with_furniture=False),
        PageSpec(l1),
    ])
    dxf = DxfDoc("mobilya_plani.dxf", PageSpec(l0, page_class="furniture_plan",
                                                title_raw="ZEMİN KAT MOBİLYA PLANI",
                                                with_dimensions=False))
    salon = l0.room_by_label("SALON 24,00 m²")
    bad_dim = lb.dimensions[[i for i, d in enumerate(lb.dimensions) if d.text_override][0]]
    win = l0.openings[missing_window]
    pct_area = abs(salon.area_label - salon.area_computed) / salon.area_label * 100
    pct_dim = abs(bad_dim.printed_value - bad_dim.measured) / bad_dim.measured * 100
    conflicts = [
        {"id": "c_001", "kind": "area_label_vs_computed", "element_ids": [salon.id],
         "description": f"Label says {format_metres(salon.area_label)} m², polygon gives "
                        f"{format_metres(salon.area_computed)} m² ({pct_area:.1f}%)",
         "resolution": "within tolerance (3%), kept polygon from mobilya_plani.dxf"},
        {"id": "c_002", "kind": "dimension_vs_measured", "element_ids": list(bad_dim.wall_ids),
         "description": f"kat_planlari.pdf p1: dimension text {bad_dim.printed} vs measured "
                        f"{bad_dim.measured:.2f} m ({pct_dim:.1f}%)",
         "resolution": "kept measured geometry (vector PDF)"},
        {"id": "c_003", "kind": "count_mismatch", "element_ids": [win.id],
         "description": f"Zemin Kat: mobilya_plani.dxf has {len(l0.windows())} windows, "
                        f"kat_planlari.pdf p2 has {len(l0.windows()) - 1}",
         "resolution": "DXF wins over vector PDF, window kept"},
    ]
    return Project(
        name="synthetic-03",
        brief=BRIEF_03,
        levels=[lb, l0, l1],
        documents=[pdf, dxf],
        conflicts=conflicts,
    )


# --------------------------------------------------------------------------
# synthetic-04: 2+1 flat on the 3rd floor, DXF + vector PDF of the same level
# (both with furniture), L-shaped living room and hall, armchair at 45°
# --------------------------------------------------------------------------

W4, H4 = 12.0, 8.0


def level_04() -> Level:
    b = LevelBuilder("3. KAT PLANI", W4, H4)
    b.wall((3.50, 4.65), (3.50, 7.75))       # 4: kitchen leg | hall (vertical leg)
    a = b.wall((3.45, 4.60), (11.75, 4.60))  # 5: living + bedroom | hall, bath, child room
    b.wall((7.00, 0.25), (7.00, 4.55))       # 6: living | bedroom
    b.wall((5.15, 5.90), (7.95, 5.90))       # 7: corridor leg | bath
    vh = b.wall((5.20, 5.95), (5.20, 7.75))  # 8: hall | bath
    vc = b.wall((8.00, 4.65), (8.00, 7.75))  # 9: corridor + bath | child room
    # Rooms: Salon + Mutfak L = 6.7 x 4.3 + 3.2 x 3.2 = 39.05 (label matches); Hol L = 4.4 x 1.2 + 1.6 x 1.9
    # = 8.32; Yatak 4.7 x 4.3 = 20.21; Banyo 2.7 x 1.8 = 4.86; Çocuk 3.7 x 3.1 = 11.47
    b.label("SALON + MUTFAK 39,05 m²", (0.6, 3.9))
    b.label("HOL", (3.8, 7.2))
    b.label("YATAK ODASI", (7.4, 0.6))
    b.label("BANYO", (5.5, 7.4))
    b.label("ÇOCUK ODASI", (8.4, 7.2))
    # Doors
    b.door(2, (4.35, 7.875), 90, "HOL")                       # entrance, top wall
    b.door(a, (4.40, 4.60), 90, "SALON + MUTFAK 39,05 m²")
    b.door(vh, (5.20, 6.85), 80, "BANYO")
    b.door(vc, (8.00, 5.25), 80, "ÇOCUK ODASI")
    b.door(a, (7.50, 4.60), 80, "YATAK ODASI")
    # Windows: living 5 on three walls, bedroom and child room 2 each, bath 1
    b.window(0, (2.00, 0.125), 180)
    b.window(0, (5.00, 0.125), 180)
    b.window(3, (0.125, 2.30), 120)
    b.window(3, (0.125, 6.20), 120)
    b.window(2, (1.85, 7.875), 120)
    b.window(2, (6.60, 7.875), 60)
    b.window(2, (9.90, 7.875), 120)
    b.window(1, (11.875, 6.20), 120)
    b.window(0, (9.40, 0.125), 180)
    b.window(1, (11.875, 2.40), 120)
    # Salon + Mutfak: kitchen leg
    b.furniture("TEZGAH", (1.45, 7.45), 0)
    b.furniture("EVIYE", (0.85, 7.50), 0)
    b.furniture("OCAK", (2.05, 7.45), 0)
    b.furniture("BUZDOLABI", (3.05, 7.40), 0)
    b.furniture("YEMEK_MASASI", (1.85, 5.60), 0)
    b.furniture("SANDALYE", (1.45, 4.80), 180)
    b.furniture("SANDALYE", (2.25, 4.80), 180)
    b.furniture("SANDALYE", (1.45, 6.40), 0)
    b.furniture("SANDALYE", (2.25, 6.40), 0)
    # Salon + Mutfak: living bar
    b.furniture("KANEPE_3LU", (3.40, 2.40), 90)
    b.furniture("SEHPA", (4.60, 2.40), 90)
    b.furniture("TV_UNITESI", (6.725, 2.40), 270)
    b.furniture("KOLTUK", (6.25, 3.85), 315)       # 45 degrees: faces the room centre
    b.furniture("KITAPLIK", (0.425, 3.60), 90)
    # Yatak Odası
    b.furniture("YATAK_CIFT", (9.60, 3.55), 0)
    b.furniture("KOMIDIN", (8.50, 4.35), 0)
    b.furniture("KOMIDIN", (10.70, 4.35), 0)
    b.furniture("DOLAP", (7.35, 1.50), 90)
    # Banyo (bathtub block KUVET)
    b.furniture("KUVET", (7.10, 7.375), 0)
    b.furniture("KLOZET", (7.60, 6.35), 270)
    b.furniture("LAVABO", (6.00, 6.175), 180)
    b.dimension_chain("bottom", [0.0, 7.00, W4])
    b.dimension_chain("left", [0.0, 4.60, H4])
    return b.build()


def project_04() -> Project:
    lv = level_04()
    # Different file stems: the preview names derive from the stem (generate.write_previews).
    return Project(name="synthetic-04", brief=BRIEF_04, levels=[lv], documents=[
        DxfDoc("3_kat_plani.dxf", PageSpec(lv)),
        PdfDoc("3_kat_plani_pdf.pdf", [PageSpec(lv)]),
    ])


# --------------------------------------------------------------------------
# synthetic-05: 3+1 flat, notched outline, floor-plan DXF without furniture +
# furniture-plan DXF, en-suite, study, twin beds, style photo, polish off
# --------------------------------------------------------------------------

W5, H5 = 13.5, 9.0
# Outer face: 13.5 x 9.0 m with a 3.0 x 1.75 m recess at the bottom right.
OUTLINE_05 = [(0.0, 0.0), (10.5, 0.0), (10.5, 1.75), (W5, 1.75), (W5, H5), (0.0, H5)]


def level_05() -> Level:
    b = LevelBuilder("ZEMİN KAT PLANI", outline=OUTLINE_05)
    # Outer walls 0..5 follow the outline edges: bottom, recess vertical (inner face x = 10.25),
    # recess horizontal (inner face y = 2.00), right, top, left.
    h = b.t_out / 2.0
    o_bottom, o_notch_h, o_right, o_top, o_left = 0, 2, 3, 4, 5
    h1 = b.wall((0.25, 4.10), (13.25, 4.10))   # 6: bottom band | kitchen, hall, study
    h2 = b.wall((3.55, 5.40), (10.15, 5.40))   # 7: hall | antre, bath, bedroom
    vk = b.wall((3.50, 4.15), (3.50, 8.75))    # 8: kitchen | hall + antre
    vc = b.wall((10.20, 4.15), (10.20, 8.75))  # 9: hall + bedroom | study
    b.wall((5.10, 5.45), (5.10, 8.75))         # 10: antre | bath
    b.wall((7.20, 5.45), (7.20, 8.75))         # 11: bath | bedroom
    b.wall((5.50, 0.25), (5.50, 4.05))         # 12: salon | master bedroom
    ve = b.wall((10.30, 2.00), (10.30, 4.05))  # 13: master bedroom | en-suite
    # Rooms: Salon 5.2 x 3.8 = 19.76 (label matches), Ebeveyn 4.7 x 3.8 = 17.86, en-suite 2.9 x 2.05 = 5.945,
    # Mutfak 3.2 x 4.6 = 14.72, Hol 6.6 x 1.2 = 7.92, Antre 1.5 x 3.3 = 4.95, Banyo 2.0 x 3.3 = 6.6,
    # Yatak 2.9 x 3.3 = 9.57, Çalışma 3.0 x 4.6 = 13.8
    b.label("SALON 19,76 m²", (0.6, 3.6))
    b.label("EBEVEYN YATAK ODASI", (5.8, 0.5))
    b.label("EBEVEYN BANYO", (10.5, 2.6))
    b.label("MUTFAK", (1.2, 6.0))
    b.label("HOL", (8.6, 4.6))
    b.label("ANTRE", (3.7, 6.3))
    b.label("BANYO", (5.4, 6.4))
    b.label("YATAK ODASI", (7.5, 6.5))
    b.label("ÇALIŞMA ODASI", (10.5, 7.0))
    # Doors
    b.door(o_top, (4.30, H5 - h), 90, "ANTRE")           # entrance
    b.door(h2, (4.30, 5.40), 80, "HOL")
    b.door(h1, (4.50, 4.10), 90, "SALON 19,76 m²")
    b.door(vk, (3.50, 4.75), 80, "MUTFAK")
    b.door(h1, (6.20, 4.10), 90, "EBEVEYN YATAK ODASI")
    b.door(ve, (10.30, 3.30), 80, "EBEVEYN BANYO")      # en-suite: reached through the master bedroom only
    b.door(h2, (6.15, 5.40), 80, "BANYO")
    b.door(h2, (8.00, 5.40), 80, "YATAK ODASI")
    b.door(vc, (10.20, 4.75), 80, "ÇALIŞMA ODASI")
    # Windows
    b.window(o_bottom, (1.80, h), 180)
    b.window(o_bottom, (4.20, h), 120)
    b.window(o_bottom, (7.90, h), 180)
    b.window(o_notch_h, (11.80, 1.75 + h), 60)           # en-suite window onto the recess
    b.window(o_left, (h, 6.50), 120)
    b.window(o_top, (1.85, H5 - h), 120)
    b.window(o_top, (6.15, H5 - h), 60)
    b.window(o_top, (8.70, H5 - h), 120)
    b.window(o_right, (W5 - h, 6.50), 120)
    b.window(o_top, (11.75, H5 - h), 120)
    # Furniture: only on the furniture plan (the floor-plan DXF draws none)
    b.furniture("KANEPE_3LU", (0.70, 2.15), 90)
    b.furniture("SEHPA", (1.95, 2.15), 90)
    b.furniture("TV_UNITESI", (5.225, 2.15), 270)
    b.furniture("YEMEK_MASASI", (3.20, 3.35), 0)
    b.furniture("SANDALYE", (2.80, 2.45), 180)
    b.furniture("SANDALYE", (3.60, 2.45), 180)
    b.furniture("YATAK_CIFT", (8.40, 3.05), 0)
    b.furniture("KOMIDIN", (7.10, 3.85), 0)
    b.furniture("KOMIDIN", (9.70, 3.85), 0)
    b.furniture("DOLAP", (5.85, 1.60), 90)
    b.furniture("SIFONYER", (9.50, 0.50), 180)
    b.furniture("DUS", (12.80, 3.60), 0)
    b.furniture("KLOZET", (11.60, 2.35), 180)
    b.furniture("LAVABO", (11.70, 3.825), 0)
    b.furniture("TEZGAH", (1.45, 8.45), 0)
    b.furniture("TEZGAH", (0.55, 6.50), 90)
    b.furniture("EVIYE", (0.85, 8.50), 0)
    b.furniture("OCAK", (2.05, 8.45), 0)
    b.furniture("BUZDOLABI", (3.05, 8.40), 0)
    b.furniture("CAMASIR_MAK", (0.55, 4.90), 90)
    b.furniture("KUVET", (6.00, 8.375), 0)
    b.furniture("KLOZET", (5.50, 7.20), 90)
    b.furniture("LAVABO", (6.925, 7.00), 270)
    b.furniture("YATAK_TEK", (8.00, 7.75), 0)
    b.furniture("YATAK_TEK", (9.60, 7.75), 0)
    b.furniture("KOMIDIN", (8.80, 8.55), 0)
    b.dimension_chain("bottom", [0.0, 5.50, 10.50])
    b.dimension_chain("left", [0.0, 4.10, H5])
    return b.build()


def project_05() -> Project:
    lv = level_05()
    floor_plan, furniture_plan = "zemin_kat.dxf", "zemin_kat_mobilya.dxf"
    return Project(
        name="synthetic-05",
        brief=BRIEF_05,
        levels=[lv],
        documents=[
            DxfDoc(floor_plan, PageSpec(lv, with_furniture=False)),
            DxfDoc(furniture_plan, PageSpec(lv, page_class="furniture_plan", title_raw="ZEMİN KAT MOBİLYA PLANI",
                                            with_dimensions=False)),
        ],
        # The pipeline's warning for a floor plan without furniture plus a furniture plan (ingest/pipeline.py).
        warnings=[f"{lv.label}: furniture taken from {furniture_plan} ({len(lv.furniture)} pieces); "
                  f"{floor_plan} draws none"],
        style_photos={"salon_referans.jpg": STYLE_PHOTO_05},
    )


def all_projects() -> list[Project]:
    return [project_01(), project_02(), project_03(), project_04(), project_05()]
