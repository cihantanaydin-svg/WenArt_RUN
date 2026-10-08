"""A small multi-drawing CAD sheet for the sheets-stage tests (docs/milestone10.md §3.1), written with ezdxf.

What: ``write_sheet(path, ...)`` draws, in centimetres, one frame with a title box (``PLANLAR``, 16 fields), four
plans (ground floor, basement, the basement's alternative ``( Açık mutfak)``, an attic with its roof outline and break
line), a section (three slab bands, level marks 43.00 / 40.00, a roof of two slopes, ground lines) and one stray
line far away. Every plan is a 10 x 8 m dwelling with 20 cm outer walls and a 10 cm inner wall (closed solid-hatched
rectangles on layer ``DUVAR``), two labelled rooms, a door block (quarter arc + leaf) and a stair block.

Why: real02 needs LibreDWG; this sheet tests the same rules in a second, with known answers (``EXPECTED``).
Options vary one thing at a time: the header unit, where the 40.00 mark points, the alternative's title, a plan
without walls, the plans' positions; ``exterior=True`` widens the frame and adds a site plan and a south elevation.
"""
from __future__ import annotations

from pathlib import Path

import ezdxf

# Plan origins (lower-left outer corner of the dwelling, cm) and titles, in reading order after the title box.
PLANS = {
    "ground": ((500.0, 2500.0), "ZEMİN KAT PLANI"),
    "basement": ((2500.0, 2500.0), "BODRUM KAT PLANI"),
    "alternative": ((4300.0, 2500.0), "BODRUM KAT PLANI ( Açık mutfak)"),
    "attic": ((500.0, 800.0), "ÇATI KAT PLANI"),
}
SECTION = (2700.0, 300.0)
SITE = (6200.0, 2300.0)              # exterior=True: a site plan and a south elevation right of the plans
ELEVATION = (6500.0, 300.0)
NORTH_DEG = 330.0                    # the site plan's north arrow points 30 deg clockwise from +Y
TITLE_FIELDS = ("PROJE: KONUT", "MİMARİ PROJE", "İŞVEREN: D. ŞAHİN", "ADRES: İSTANBUL", "MİMAR: A. YILMAZ",
                "ÇİZEN: B. KAYA", "KONTROL: C. DEMİR", "PAFTA NO: A-01", "REVİZYON: 0", "TARİH: EKİM 2026",
                "ONAY: BELEDİYE", "STATİK: E. ÇELİK", "ELEKTRİK: F. AK", "MEKANİK: G. SU", "SAYFA: BİR", "NOT: TASLAK")
W, D = 1000.0, 800.0                 # dwelling outer size (cm)
OUTER, INNER = 20.0, 10.0
EXPECTED = {
    "regions": 6,
    "plans": 4,
    "levels": {"L-1": "basement", "L0": "floor", "L1": "attic"},
    "alternative": {"level_id": "L-1b", "slug": "acik-mutfak", "gloss": "open kitchen", "variant": "Açık mutfak"},
    "floor_z": {"L-1": -3.0, "L0": 0.0, "L1": 3.15},
    "slab": 0.15,
    "ceiling": {"L-1": 2.85, "L0": 3.0},
    "pitch_deg": 28.61,
    "eaves_above_attic": 0.5,
    "ridge_above_attic": 3.5,
    "overhang": 0.5,
    "roof_thickness": 0.2,
}


def _rect(msp, x0, y0, x1, y1, layer, hatch=False):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    if hatch:
        h = msp.add_hatch(color=7, dxfattribs={"layer": layer})
        h.paths.add_polyline_path(pts, is_closed=True)


def _blocks(doc) -> None:
    door = doc.blocks.new("KAPI")
    door.add_arc((0, 0), 90, 0, 90, dxfattribs={"layer": "0"})
    door.add_line((0, 0), (0, 90), dxfattribs={"layer": "0"})
    stair = doc.blocks.new("MERDIVEN")
    stair.add_lwpolyline([(0, 0), (100, 0), (100, 250), (0, 250)], close=True)
    for k in range(1, 9):
        stair.add_line((0, k * 28), (100, k * 28))


def _plan(msp, origin, title, labels, walls=True, area_text=True):
    ox, oy = origin
    if not walls:
        # The outline as four single lines on layer 0: one drawing, but nothing the wall rules read as a wall.
        for a, b in (((0, 0), (W, 0)), ((W, 0), (W, D)), ((W, D), (0, D)), ((0, D), (0, 0)), ((500, 0), (500, D))):
            msp.add_line((ox + a[0], oy + a[1]), (ox + b[0], oy + b[1]), dxfattribs={"layer": "0"})
    if walls:
        _rect(msp, ox, oy, ox + W, oy + OUTER, "DUVAR", hatch=True)
        _rect(msp, ox, oy + D - OUTER, ox + W, oy + D, "DUVAR", hatch=True)
        _rect(msp, ox, oy + OUTER, ox + OUTER, oy + D - OUTER, "DUVAR", hatch=True)
        _rect(msp, ox + W - OUTER, oy + OUTER, ox + W, oy + D - OUTER, "DUVAR", hatch=True)
        _rect(msp, ox + 495, oy + OUTER, ox + 505, oy + D - OUTER, "DUVAR", hatch=True)
    left, right = labels
    # Clear room areas: (495 - 20) x 760 = 36.10 m², (980 - 505) x 760 = 36.10 m².
    msp.add_mtext(f"{left}\\P36.1M2" if area_text else left,
                  dxfattribs={"insert": (ox + 200, oy + 420), "char_height": 15, "layer": "0"})
    msp.add_mtext(f"{right}\\P36.1M2" if area_text else right,
                  dxfattribs={"insert": (ox + 700, oy + 420), "char_height": 15, "layer": "0"})
    msp.add_blockref("KAPI", (ox + 200, oy + D - OUTER - 100), dxfattribs={"layer": "KAPI"})
    msp.add_blockref("MERDIVEN", (ox + 820, oy + 100), dxfattribs={"layer": "MERDIVEN"})
    msp.add_text(title, height=50, dxfattribs={"insert": (ox, oy - 150), "layer": "0"})


def _mark(line, msp, ox, oy, x, y, value) -> None:
    """A level mark: a V with its apex on the level, a bar, the value above."""
    line((x, y), (x - 15.0, y + 15.0))
    line((x, y), (x + 15.0, y + 15.0))
    line((x - 15.0, y + 15.0), (x + 80.0, y + 15.0))
    msp.add_mtext(value, dxfattribs={"insert": (ox + x - 10.0, oy + y + 45.0), "char_height": 20, "layer": "0"})


def _site(msp, origin) -> None:
    """Site plan (1/100, cm): plot 24 x 20 m, the building's outline 10 x 8 m at (7, 6), a parking bay with its label,
    a garden label, a tree and a north arrow; drawn unrotated (the reference's frame)."""
    ox, oy = origin
    _rect(msp, ox, oy, ox + 2400.0, oy + 2000.0, "VAZIYET")
    _rect(msp, ox + 700.0, oy + 600.0, ox + 700.0 + W, oy + 600.0 + D, "VAZIYET")
    _rect(msp, ox + 1900.0, oy + 1400.0, ox + 2300.0, oy + 1900.0, "VAZIYET")
    msp.add_text("OTOPARK", height=40, dxfattribs={"insert": (ox + 1950.0, oy + 1640.0), "layer": "VAZIYET"})
    msp.add_text("BAHÇE", height=40, dxfattribs={"insert": (ox + 250.0, oy + 250.0), "layer": "VAZIYET"})
    msp.add_circle((ox + 300.0, oy + 1700.0), 100.0, dxfattribs={"layer": "AGAC"})
    import math
    cx, cy = ox + 2100.0, oy + 500.0
    ux, uy = math.sin(math.radians(30.0)), math.cos(math.radians(30.0))
    msp.add_line((cx - ux * 75.0, cy - uy * 75.0), (cx + ux * 75.0, cy + uy * 75.0), dxfattribs={"layer": "VAZIYET"})
    msp.add_text("N", height=40, dxfattribs={"insert": (cx + ux * 160.0 - 12.0, cy + uy * 160.0 - 20.0),
                                             "layer": "VAZIYET"})
    msp.add_text("VAZİYET PLANI", height=50, dxfattribs={"insert": (ox, oy - 150.0), "layer": "0"})


def _elevation(msp, origin) -> None:
    """South elevation (cm): ground line at y 315 with a ±0.00 mark, the facade 10 x 6.30 m, a stone plinth (solid
    hatch, 1 m, labelled), a render label, three 1.20 x 1.50 m windows (sill 1.00 m) and a 0.90 x 2.10 m door."""
    ox, oy = origin
    line = lambda a, b: msp.add_line((ox + a[0], oy + a[1]), (ox + b[0], oy + b[1]), dxfattribs={"layer": "0"})  # noqa: E731
    line((-100.0, 315.0), (1100.0, 315.0))
    _rect(msp, ox, oy + 315.0, ox + W, oy + 945.0, "CEPHE")
    _rect(msp, ox, oy + 315.0, ox + W, oy + 415.0, "TARAMA", hatch=True)
    msp.add_text("TAŞ KAPLAMA", height=20, dxfattribs={"insert": (ox + 600.0, oy + 355.0), "layer": "TARAMA"})
    msp.add_text("SIVA", height=20, dxfattribs={"insert": (ox + 450.0, oy + 650.0), "layer": "CEPHE"})
    for x, y in ((150.0, 415.0), (700.0, 415.0), (150.0, 730.0)):
        _rect(msp, ox + x, oy + y, ox + x + 120.0, oy + y + 150.0, "CEPHE")
    _rect(msp, ox + 450.0, oy + 315.0, ox + 540.0, oy + 525.0, "CEPHE")
    _mark(line, msp, ox, oy, 1150.0, 315.0, "±0.00")
    msp.add_text("GÜNEY GÖRÜNÜŞÜ", height=50, dxfattribs={"insert": (ox, oy + 165.0), "layer": "0"})


def _section(msp, origin, mark40_at_bottom: bool) -> None:
    ox, oy = origin
    line = lambda a, b: msp.add_line((ox + a[0], oy + a[1]), (ox + b[0], oy + b[1]), dxfattribs={"layer": "0"})  # noqa: E731
    for x in (0.0, OUTER, W - OUTER, W):
        line((x, 0.0), (x, 615.0))
    for y in (0.0, 15.0, 300.0, 315.0, 615.0, 630.0):
        line((0.0, y), (W, y))
    # Roof: eaves 50 cm outside the walls and 50 cm above the attic floor (630), ridge 350 cm above it.
    line((-50.0, 630.0), (-50.0, 680.0))
    line((W + 50.0, 630.0), (W + 50.0, 680.0))
    line((-50.0, 680.0), (W / 2, 980.0))
    line((W / 2, 980.0), (W + 50.0, 680.0))
    # The underside 20 cm below the outer line (perpendicular), parallel to it.
    import math
    ang = math.atan2(300.0, W / 2 + 50.0)
    dx, dy = 20.0 * math.sin(ang), -20.0 * math.cos(ang)
    line((-50.0 + dx, 680.0 + dy), (W / 2, 980.0 - 20.0 / math.cos(ang)))
    line((W / 2, 980.0 - 20.0 / math.cos(ang)), (W + 50.0 - dx, 680.0 + dy))
    # Ground lines at the ground floor's level on both sides.
    line((-600.0, 315.0), (-10.0, 315.0))
    line((W + 10.0, 315.0), (W + 600.0, 315.0))
    # Level marks: a V under the text, apex on the level.
    for value, y in (("43.00", 315.0), ("40.00", 0.0 if mark40_at_bottom else 15.0)):
        ax = W + 150.0
        line((ax, y), (ax - 15.0, y + 15.0))
        line((ax, y), (ax + 15.0, y + 15.0))
        line((ax - 15.0, y + 15.0), (ax + 80.0, y + 15.0))
        msp.add_mtext(value, dxfattribs={"insert": (ox + ax - 10.0, oy + y + 45.0), "char_height": 20,
                                          "layer": "0"})


def write_sheet(path: Path, insunits: int = 4, mark40_at_bottom: bool = True,
                alternative_title: str = PLANS["alternative"][1], walls: dict | None = None, titles: dict | None = None,
                stray: bool = True, section: bool = True, frame: bool = True, exterior: bool = False) -> Path:
    """Write the sheet (DXF R2013) and return its path."""
    doc = ezdxf.new("R2013")
    doc.header["$INSUNITS"] = insunits
    for name in ("DUVAR", "KAPI", "MERDIVEN", "VAZIYET", "AGAC", "CEPHE", "TARAMA"):
        doc.layers.add(name)
    _blocks(doc)
    msp = doc.modelspace()
    if frame:
        _rect(msp, 0.0, 0.0, 9000.0 if exterior else 6000.0, 5000.0, "PAFTA")
        _rect(msp, 200.0, 4500.0, 5800.0, 4900.0, "PAFTA")
        msp.add_mtext("PLANLAR", dxfattribs={"insert": (300.0, 4800.0), "char_height": 150, "layer": "PAFTA"})
        # Title-block fields (small texts): with them the stray line holds < 1 % of the sheet's entities.
        for k, field in enumerate(TITLE_FIELDS):
            msp.add_text(field, height=30, dxfattribs={"insert": (1500.0 + 1000.0 * (k // 4), 4800.0 - 80.0 * (k % 4)),
                                                         "layer": "PAFTA"})
    walls = walls or {}
    labels = {"ground": ("SALON", "YATAK ODASI"), "basement": ("SALON", "MUTFAK"),
              "alternative": ("SALON", "AÇIK MUTFAK"), "attic": ("ÇOCUK ODASI", "BANYO")}
    for key, (origin, title) in PLANS.items():
        t = alternative_title if key == "alternative" else (titles or {}).get(key, title)
        _plan(msp, origin, t, labels[key], walls=walls.get(key, True))
    ax, ay = PLANS["attic"][0]
    _rect(msp, ax - 50.0, ay - 50.0, ax + W + 50.0, ay + D + 50.0, "CATI")          # roof outline
    _rect(msp, ax + 150.0, ay + 120.0, ax + W - 150.0, ay + D - 120.0, "CATI")       # break line
    if section:
        _section(msp, SECTION, mark40_at_bottom)
    if exterior:
        _site(msp, SITE)
        _elevation(msp, ELEVATION)
    if stray:
        msp.add_line((100000.0, 100000.0), (100050.0, 100000.0), dxfattribs={"layer": "0"})
    doc.saveas(path)
    return Path(path)
