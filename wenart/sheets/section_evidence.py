"""What a section draws at each storey, for the checks of the storeys the plans do not draw (27 Nov 2026, audit fix round
5b, rule R22).

What: ``read(section, heights, cut)`` records, in ``sheets.json`` (``heights.section_evidence``), for the section the
heights were read from: each slab band's floor height in the building frame (``z``: the section's relative level marks
minus the datum's relative value, else the heights' own band frame) and the stretches its slab lines cover between the
outer walls (``cover``: metres from the section's left outer wall face, both lines of the band), and for every storey
between two bands the short strokes drawn in it per ``BIN_M`` along the section (``strokes``: the treads and risers of a
stair cut or seen there). ``s_width`` is the section's width between its outer walls; ``cut`` the cut line in the sheets
frame (``axis``, ``at``, ``flipped``, the two marks of a jogged cut, ``ends``).

Why: real10 has no plan of its ground floor; the typical floor plan stands for it, so the ground floor got the escape
stair, a slab, a facade window and two kitchen windows where section A-A draws a double-height entrance hall (the
+2.50 slab stops at the core landing, the escape stair's first flight starts on the +5.50 slab). A copied storey must be
checked against what the section draws (``wenart.sheets.typical_check``).

How: pure geometry on the section's lines (no AI); nothing is decided here.
"""
from __future__ import annotations

import statistics
from typing import Optional

BIN_M = 0.25                 # the strokes of a storey are counted per this many metres along the section
STROKE_MAX_M = 0.45          # a stroke this short or shorter is a tread, a riser or a stair rail post (counted)
LINE_TOL = 1e-6              # a slab line lies on its band's y within this (source units)


def _frame_free_lines(section) -> list:
    from wenart.sheets import heights as HT
    lines = HT._lines(section.region)
    box = section.region.geometry_box
    framed = HT.frame_keys(lines, box)
    fbox = HT.drawn_frame_box(section.region)
    if not framed and fbox is not None:
        framed = HT.frame_keys(lines, fbox)
    return [ln for ln in lines if ln.key not in framed]


def _z_of(section, heights: dict):
    """y (source units) -> building z (m): through the relative level marks and the datum's relative value when there are
    two or more marks, else through the heights' own band frame (``_bands``), else None."""
    s = float(section.mpu)
    datum = heights.get("datum") if isinstance(heights.get("datum"), dict) else None
    rel0 = datum.get("relative") if datum else None
    pairs = []
    for m in section.marks or []:
        rec = m[4] if len(m) > 4 and isinstance(m[4], dict) else None
        if rec is not None and rec.get("relative") and rec.get("value") is not None:
            pairs.append(float(rec["value"]) - float(m[2][1]) * s)
    if rel0 is not None and len(pairs) >= 2:
        c = statistics.median(pairs)
        return lambda y: float(y) * s + c - float(rel0), "level_marks"
    bands = heights.get("_bands") or []
    if bands and section.bands:
        yb, yt = section.bands[0][0], section.bands[0][1]
        z_t = float(bands[0][1])
        return lambda y: (float(y) - yt) * s + z_t, "bands"
    return None, None


def _cover(lines: list, y: float, x0: float, x1: float, s: float) -> list:
    spans = sorted((max(min(ln.a[0], ln.b[0]), x0), min(max(ln.a[0], ln.b[0]), x1)) for ln in lines
                   if abs(ln.a[1] - y) <= LINE_TOL and abs(ln.b[1] - y) <= LINE_TOL)
    out: list = []
    for a, b in spans:
        if b <= a:
            continue
        if out and a <= out[-1][1] + 1e-9:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [[round((a - x0) * s, 3) + 0.0, round((b - x0) * s, 3) + 0.0] for a, b in out]


def read(section, heights: dict, cut: Optional[dict]) -> Optional[dict]:
    """The section evidence (module docstring), or None without a usable section."""
    if section is None or not section.mpu or section.walls is None or not section.bands:
        return None
    s = float(section.mpu)
    x0, x1 = section.walls
    z_of, how = _z_of(section, heights)
    if z_of is None:
        return None
    lines = _frame_free_lines(section)
    bands = []
    for yb, yt, _ib, _it in section.bands:
        top, bot = _cover(lines, yt, x0, x1, s), _cover(lines, yb, x0, x1, s)
        bands.append({"z": round(z_of(yt), 3) + 0.0, "thickness": round((yt - yb) * s, 3) + 0.0,
                      "cover_top": top, "cover_bottom": bot})
    storeys = []
    for (yb0, yt0, _a, _b), (yb1, _yt1, _c, _d) in zip(section.bands, section.bands[1:]):
        bins: dict = {}
        for ln in lines:
            lo, hi = sorted((ln.a[1], ln.b[1]))
            if lo < yt0 - LINE_TOL or hi > yb1 + LINE_TOL or ln.length * s > STROKE_MAX_M or ln.length <= 0:
                continue
            mx = (ln.a[0] + ln.b[0]) / 2.0
            if not x0 <= mx <= x1:
                continue
            k = int((mx - x0) * s / BIN_M)
            bins[k] = bins.get(k, 0) + 1
        storeys.append({"z_floor": round(z_of(yt0), 3) + 0.0, "z_ceiling": round(z_of(yb1), 3) + 0.0,
                        "strokes": {str(k): v for k, v in sorted(bins.items())}})
    rec = {"region_id": section.region.id, "z_frame": how, "s_width": round((x1 - x0) * s, 3) + 0.0,
           "bin_m": BIN_M, "bands": bands, "storeys": storeys, "cut": None}
    if cut is not None:
        rec["cut"] = {k: cut.get(k) for k in ("axis", "at", "flipped", "jogged", "ends", "region", "method")
                      if cut.get(k) is not None}
    return rec
