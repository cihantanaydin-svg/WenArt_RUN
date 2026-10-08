"""A small multi-drawing CAD sheet for the sheets-stage tests (docs/milestone10.md §3.1), written with ezdxf.

What: ``write_sheet(path, ...)`` draws, in centimetres, one frame with a title box (``PLANLAR``), four plans (ground
floor, basement, the basement's alternative ``( Açık mutfak)``, an attic with its roof outline and break line), a
section (three slab bands, level marks 43.00 / 40.00, a roof of two slopes, ground lines) and one stray line far
away. Every plan is a 10 x 8 m dwelling with 20 cm outer walls and a 10 cm inner wall (closed solid-hatched
rectangles on layer ``DUVAR``), two labelled rooms, a door block (quarter arc + leaf) and a stair block.

Why: real02 needs LibreDWG; this sheet tests the same rules in a second, with known answers (``EXPECTED``).
Options vary one thing at a time: the header unit, where the 40.00 mark points, the alternative's title, a plan
without walls, the plans' positions.
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
                alternative_title: str = PLANS["alternative"][1], walls: dict | None = None,
                stray: bool = True, section: bool = True, frame: bool = True) -> Path:
    """Write the sheet (DXF R2013) and return its path."""
    doc = ezdxf.new("R2013")
    doc.header["$INSUNITS"] = insunits
    for name in ("DUVAR", "KAPI", "MERDIVEN"):
        doc.layers.add(name)
    _blocks(doc)
    msp = doc.modelspace()
    if frame:
        _rect(msp, 0.0, 0.0, 6000.0, 5000.0, "PAFTA")
        _rect(msp, 200.0, 4500.0, 5800.0, 4900.0, "PAFTA")
        msp.add_mtext("PLANLAR", dxfattribs={"insert": (300.0, 4800.0), "char_height": 150, "layer": "PAFTA"})
    walls = walls or {}
    labels = {"ground": ("SALON", "YATAK ODASI"), "basement": ("SALON", "MUTFAK"),
              "alternative": ("SALON", "AÇIK MUTFAK"), "attic": ("ÇOCUK ODASI", "BANYO")}
    for key, (origin, title) in PLANS.items():
        t = alternative_title if key == "alternative" else title
        _plan(msp, origin, t, labels[key], walls=walls.get(key, True))
    ax, ay = PLANS["attic"][0]
    _rect(msp, ax - 50.0, ay - 50.0, ax + W + 50.0, ay + D + 50.0, "CATI")          # roof outline
    _rect(msp, ax + 150.0, ay + 120.0, ax + W - 150.0, ay + D - 120.0, "CATI")       # break line
    if section:
        _section(msp, SECTION, mark40_at_bottom)
    if stray:
        msp.add_line((100000.0, 100000.0), (100050.0, 100000.0), dxfattribs={"layer": "0"})
    doc.saveas(path)
    return Path(path)
