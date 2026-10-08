"""Heights from a vector section (docs/milestone10.md §3.1 item 7).

What: ``read_section(region, mpu) -> SectionGeometry`` finds what a section draws (slab bands, outer wall faces,
roof lines, ground lines, level marks); ``heights(sections, levels, reference_extent, brief, file_of) -> (dict,
conflicts, warnings)`` turns it into the ``heights`` block of ``sheets.json``: floor levels, ceiling heights, floor
to floor, slabs, the ground per side and the roof (eaves, ridge, pitches, overhang, thickness, knee wall, profile).

Why: plans give no heights. real02's only height source is one section; every value it gives carries the slab line
or mark it was measured from; values no drawing gives are ``assumed`` (the brief's ``ceiling_height`` and
``slab_thickness``) and listed.

How (source units, y up; metres = units x metres per unit):
- straight pieces of the region's strokes are horizontal (within 0.5 deg), vertical or sloped (5-85 deg);
- outer wall faces: the outermost vertical lines at least 2 m long; the building width is their distance;
- slab bands: horizontal lines that cover >= 50 % of the building width, taken bottom-up in pairs 0.05-0.6 m apart
  (one band = one slab: its top is the floor above, its bottom the ceiling below);
- roof: the upper envelope of the sloped lines (>= 0.5 m long) above the top band, simplified to its corners (the
  profile); pitches = the slopes of its sides from the eaves up; eaves = its lowest end, ridge = its highest point,
  overhang = from the outer wall face to the eaves end; roof thickness = the distance to the parallel line under the
  first slope; the knee wall = the roof underside above the top floor at the inner face of the outer wall;
- ground lines: horizontal lines outside the wall faces that reach within 1 m of them (the upper one per side is
  the terrain, others are listed);
- level marks: ``units_check.mark_texts`` / ``mark_point`` (the triangle apex under ``43.00``). The mark at the
  ground floor's slab top is the datum (building z = 0); a mark whose value and the height of the point it marks
  differ by more than 5 cm is a ``level_mark_mismatch`` (geometry wins).
- Bands map to the plan levels bottom-up (n bands = n levels; n + 1 = a flat roof slab on top). The section width
  must match the reference plan's extent along one axis within 1 % or 5 cm: that axis is the cut direction.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from wenart.sheets import units_check as UC

H_TOL_DEG = 0.5
SLOPE_DEG = (5.0, 85.0)
WALL_MIN_M = 2.0
BAND_COVER = 0.5
BAND_M = (0.05, 0.6)
ROOF_MIN_M = 0.5
GROUND_REACH_M = 1.0
GROUND_MIN_M = 1.0                     # a ground line is at least 1 m long (not a slab or eaves end)
MARK_TOL_M = 0.05
SECTION_WIDTH_TOL = (0.01, 0.05)       # 1 % or 5 cm
PROFILE_TOL_M = 0.01
ROOF_THICKNESS_M = (0.05, 0.6)
FLOOR_TO_FLOOR_M = 3.00                # no section: floor to floor (assumed, docs/milestone10.md §1.6b row 6)


@dataclass
class Line:
    a: tuple[float, float]
    b: tuple[float, float]
    id: str
    key: str = ""             # unique per straight piece: the edges of one closed polyline share the entity id

    @property
    def length(self) -> float:
        return math.dist(self.a, self.b)

    @property
    def angle(self) -> float:
        return math.degrees(math.atan2(self.b[1] - self.a[1], self.b[0] - self.a[0])) % 180.0


@dataclass
class SectionGeometry:
    region: object
    mpu: Optional[float]
    walls: Optional[tuple[float, float]] = None          # x of the outer wall faces (left, right)
    wall_ids: tuple = (None, None)
    wall_inner: Optional[tuple[float, float]] = None     # x of the inner faces of the outer walls
    bands: list = field(default_factory=list)            # [(y_bottom, y_top, id_bottom, id_top)]
    profile: list = field(default_factory=list)          # [(x, y)] outer roof line, left to right
    profile_ids: list = field(default_factory=list)
    underside: list = field(default_factory=list)        # [Line] sloped lines under the outer roof line
    roof_lines: int = 0
    ground: list = field(default_factory=list)           # [(side, y, id)]
    marks: list = field(default_factory=list)            # [(Txt, value, (x, y), how)]

    @property
    def width(self) -> Optional[float]:
        return None if self.walls is None else self.walls[1] - self.walls[0]

    def features(self) -> dict:
        return {"slab_bands": len(self.bands), "roof_lines": self.roof_lines, "level_marks": len(self.marks),
                "ground_lines": len(self.ground), "outer_walls": self.walls is not None}


def _lines(region) -> list[Line]:
    out = []
    for k, (a, b, st) in enumerate(UC.segments(region.strokes())):
        out.append(Line(tuple(a), tuple(b), st.id, f"{st.id}#{k}"))
    return out


def _metres(units: float, mpu: Optional[float], fallback_rel: float, ref: float) -> float:
    """``units`` of a length given in metres, or a share of ``ref`` when the unit is unknown."""
    return units / mpu if mpu else fallback_rel * ref


def read_section(region, mpu: Optional[float]) -> SectionGeometry:
    g = SectionGeometry(region=region, mpu=mpu)
    lines = _lines(region)
    if not lines:
        return g
    box = region.geometry_box
    height = max(box[3] - box[1], 1e-9)
    horiz, vert, slope = [], [], []
    for ln in lines:
        a = ln.angle
        if min(a, 180.0 - a) <= H_TOL_DEG:
            horiz.append(ln)
        elif abs(a - 90.0) <= H_TOL_DEG:
            vert.append(ln)
        elif SLOPE_DEG[0] <= min(a, 180.0 - a) <= SLOPE_DEG[1]:
            slope.append(ln)
    wall_min = _metres(WALL_MIN_M, mpu, 0.25, height)
    walls = [ln for ln in vert if ln.length >= wall_min]
    if len(walls) < 2:
        return g
    left = min(walls, key=lambda ln: ln.a[0])
    right = max(walls, key=lambda ln: ln.a[0])
    x0, x1 = left.a[0], right.a[0]
    if x1 - x0 <= 0:
        return g
    g.walls = (x0, x1)
    g.wall_ids = (left.id, right.id)
    inner_l = [ln.a[0] for ln in walls if x0 < ln.a[0] <= x0 + _metres(0.6, mpu, 0.05, x1 - x0)]
    inner_r = [ln.a[0] for ln in walls if x1 - _metres(0.6, mpu, 0.05, x1 - x0) <= ln.a[0] < x1]
    g.wall_inner = (min(inner_l) if inner_l else x0, max(inner_r) if inner_r else x1)
    width = x1 - x0

    # Slab bands.
    rows: dict[float, list[Line]] = {}
    for ln in horiz:
        rows.setdefault(round((ln.a[1] + ln.b[1]) / 2.0, 6), []).append(ln)
    covering = []
    for y, lns in rows.items():
        spans = sorted((max(min(ln.a[0], ln.b[0]), x0), min(max(ln.a[0], ln.b[0]), x1)) for ln in lns)
        covered, cur = 0.0, None
        for s0, s1 in spans:
            if s1 <= s0:
                continue
            if cur is None or s0 > cur[1]:
                if cur is not None:
                    covered += cur[1] - cur[0]
                cur = [s0, s1]
            else:
                cur[1] = max(cur[1], s1)
        if cur is not None:
            covered += cur[1] - cur[0]
        if covered >= BAND_COVER * width:
            covering.append((y, max(lns, key=lambda ln: ln.length).id))
    covering.sort()
    lo, hi = (_metres(BAND_M[0], mpu, 0.0, height), _metres(BAND_M[1], mpu, 0.05, height))
    i = 0
    while i < len(covering) - 1:
        (ya, ida), (yb, idb) = covering[i], covering[i + 1]
        if lo <= yb - ya <= hi:
            g.bands.append((ya, yb, ida, idb))
            i += 2
        else:
            i += 1

    # Roof: the upper envelope of the long sloped lines above the top band.
    top = g.bands[-1][1] if g.bands else box[1]
    roof_min = _metres(ROOF_MIN_M, mpu, 0.05, width)
    roof = [ln for ln in slope if ln.length >= roof_min and min(ln.a[1], ln.b[1]) >= top - 1e-6]
    g.roof_lines = len(roof)
    if roof:
        g.profile, g.profile_ids, outer = _envelope(roof, _metres(PROFILE_TOL_M, mpu, 0.001, width))
        g.underside = [ln for ln in roof if ln.key not in outer]

    # Level marks.
    segs = UC.segments(region.strokes())
    for t, value in UC.mark_texts(region.texts):
        mp = UC.mark_point(t, segs)
        if mp is not None:
            g.marks.append((t, value, (mp[0], mp[1]), mp[2]))

    # Ground lines: horizontal lines outside the walls that reach within 1 m of them; a level mark's own line (a line
    # that starts at the mark's apex and runs to the wall) is no ground line; a mark standing on a ground line is.
    reach = _metres(GROUND_REACH_M, mpu, 0.1, width)
    min_ground = _metres(GROUND_MIN_M, mpu, 0.1, width)
    on_tol = _metres(0.01, mpu, 0.001, width)
    apexes = [m[2] for m in g.marks]
    for ln in horiz:
        lx0, lx1 = sorted((ln.a[0], ln.b[0]))
        if lx1 - lx0 < min_ground:
            continue
        if any(min(abs(px - lx0), abs(px - lx1)) <= on_tol and abs(py - ln.a[1]) <= on_tol for px, py in apexes):
            continue
        if lx1 <= x0 + 1e-6 and x0 - lx1 <= reach:
            g.ground.append(("left", ln.a[1], ln.id))
        elif lx0 >= x1 - 1e-6 and lx0 - x1 <= reach:
            g.ground.append(("right", ln.a[1], ln.id))
    return g


def _envelope(lines: list[Line], tol: float) -> tuple[list[tuple[float, float]], list[str], set]:
    """Upper envelope of sloped lines, as corner points left to right, the entity ids of the lines it runs on and
    their keys (the edges of one closed roof polyline are told apart by their keys)."""
    xs = sorted({ln.a[0] for ln in lines} | {ln.b[0] for ln in lines})
    x_min, x_max = xs[0], xs[-1]
    n = 2000
    samples = []
    for k in range(n + 1):
        x = x_min + (x_max - x_min) * k / n
        best = None
        for ln in lines:
            (ax, ay), (bx, by) = sorted((ln.a, ln.b))
            if ax - 1e-9 <= x <= bx + 1e-9 and bx > ax:
                y = ay + (by - ay) * (x - ax) / (bx - ax)
                if best is None or y > best[0]:
                    best = (y, ln.key or ln.id)
        if best is not None:
            samples.append((x, best[0], best[1]))
    if not samples:
        return [], [], set()
    # Corners: where the supporting line changes; the corner is the intersection of the two lines.
    by_id = {(ln.key or ln.id): ln for ln in lines}
    pts = [(samples[0][0], samples[0][1])]
    ids = [samples[0][2]]
    for (xa, ya, ia), (xb, yb, ib) in zip(samples, samples[1:]):
        if ib != ia:
            p = _intersect(by_id[ia], by_id[ib]) or (xb, yb)
            if math.dist(p, pts[-1]) > tol:
                pts.append(p)
            ids.append(ib)
    pts.append((samples[-1][0], samples[-1][1]))
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > tol:
            out.append(p)
    keys = list(dict.fromkeys(ids))
    return out, list(dict.fromkeys(by_id[k].id for k in keys)), set(keys)


def _intersect(l1: Line, l2: Line) -> Optional[tuple[float, float]]:
    (x1, y1), (x2, y2) = l1.a, l1.b
    (x3, y3), (x4, y4) = l2.a, l2.b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _y_on(ln: Line, x: float) -> Optional[float]:
    (ax, ay), (bx, by) = sorted((ln.a, ln.b))
    if bx - ax <= 0 or not (ax - 1e-9 <= x <= bx + 1e-9):
        return None
    return ay + (by - ay) * (x - ax) / (bx - ax)


# --------------------------------------------------------------------------
# Heights
# --------------------------------------------------------------------------

def _ev(file_rel: str, entity: Optional[str], rule: str, region_id: str, text: Optional[str] = None,
        confidence: float = 1.0, method: str = "vector") -> dict:
    ev = {"file": file_rel, "page": 1, "layer": None, "entity": entity, "method": method, "confidence": confidence,
          "rule": rule, "region_id": region_id}
    if text is not None:
        ev["text"] = text
    return ev


def _value(v: Optional[float], method: str, evidence: list, confidence: float = 1.0, note: Optional[str] = None,
           nd: int = 3) -> dict:
    out = {"value": None if v is None else round(float(v), nd) + 0.0, "method": method,
           "confidence": confidence if method != "assumed" else 0.0, "evidence": evidence}
    if note is not None:
        out["note"] = note
    return out


def assumed(v: Optional[float], note: str) -> dict:
    return _value(v, "assumed", [], 0.0, note)


def heights(section: Optional[SectionGeometry], levels: list[dict], reference_extent: Optional[tuple[float, float]],
            brief_values: dict, file_rel: Optional[str], conflict,
            cut: Optional[dict] = None) -> tuple[dict, list[str]]:
    """The ``heights`` block. ``levels``: the base plan levels bottom-up ``[{id, order, kind}]``;
    ``reference_extent``: (width, height) in metres of the reference plan's outline (cut-axis check); ``conflict``:
    a callable ``(kind, regions, description, resolution) -> id`` that lists a conflict."""
    warnings: list[str] = []
    ceiling_default = float(brief_values.get("ceiling_height", 2.70))
    slab_default = float(brief_values.get("slab_thickness", 0.20))
    out = {"section_regions": [], "cut_axis": None, "cut_at": None, "flipped": None, "datum": None, "levels": [],
           "slabs": [], "ground": [],
           "roof": {"eaves_z": None, "ridge_z": None, "pitches_deg": [], "knee_wall": None, "overhang": None,
                    "thickness": None, "profile": []}}
    usable = section is not None and section.mpu and section.bands and section.walls is not None
    if not usable:
        why = ("no section drawing" if section is None else
               "the section has no unit" if not section.mpu else
               "no slab bands found in the section" if not section.bands else "no outer walls found in the section")
        _assumed_levels(out, levels, ceiling_default, slab_default, why)
        warnings.append(f"heights assumed ({why}): ceiling {ceiling_default:.2f} m, slab {slab_default:.2f} m, "
                        f"floor to floor {FLOOR_TO_FLOOR_M:.2f} m")
        return out, warnings
    s = float(section.mpu)
    r = section.region
    rid = r.id
    out["section_regions"] = [rid]
    bands = section.bands
    n = len(levels)
    if len(bands) == n or len(bands) == n + 1:
        mapped = list(zip(levels, bands[:n]))
        roof_band = bands[n] if len(bands) == n + 1 else None
    else:
        k = min(len(bands), n)
        mapped = list(zip(levels[:k], bands[:k]))
        roof_band = None
        warnings.append(f"section {rid}: {len(bands)} slab bands for {n} plan levels: the lowest {k} levels "
                        f"mapped bottom-up, the rest assumed")
        conflict("other", [rid], f"section {rid} draws {len(bands)} slab bands, the plans {n} levels",
                 "bands mapped bottom-up; unmatched levels assumed")
    by_level = {lv["id"]: band for lv, band in mapped}
    ground_level = next((lv for lv, _ in mapped if lv.get("order") == 0), None)
    zero_y = by_level[ground_level["id"]][1] if ground_level else mapped[0][1][1]
    if ground_level is None:
        warnings.append(f"section {rid}: no ground-floor plan; building z = 0 at the floor of the lowest level")

    def z(y: float) -> float:
        return (y - zero_y) * s

    # Datum and marks.
    marks = []
    for t, value, (mx, my), how in section.marks:
        marks.append({"t": t, "value": value, "y": my, "how": how})
    datum = None
    if marks:
        near = min(marks, key=lambda m: abs(m["y"] - zero_y))
        if abs(near["y"] - zero_y) * s <= MARK_TOL_M:
            datum = near
            out["datum"] = _value(near["value"], "vector",
                                  [_ev(file_rel, near["t"].id, "level_mark", rid, near["t"].text)],
                                  note="absolute level of the ground floor (building z = 0) from the level mark")
    if datum is not None:
        for m in marks:
            if m is datum:
                continue
            value_z = m["value"] - datum["value"]
            drawn_z = z(m["y"])
            if abs(value_z - drawn_z) > MARK_TOL_M:
                what = _what_at(section, m["y"])
                cid = conflict("level_mark_mismatch", [rid],
                               f"section {rid}: the level mark {m['t'].text} ({m['t'].id}) gives {value_z:+.2f} m but "
                               f"points at {drawn_z:+.2f} m{what} ({abs(value_z - drawn_z):.2f} m apart)",
                               "geometry wins: slab tops from the slab lines")
                m["conflict"] = cid
    elif marks:
        warnings.append(f"section {rid}: no level mark at the ground floor's slab top: marks used as cross-checks of "
                        f"differences only")

    # Levels and slabs.
    for idx, (lv, (yb, yt, idb, idt)) in enumerate(mapped):
        entry = {"level_id": lv["id"]}
        entry["floor_z"] = _value(z(yt), "vector", [_ev(file_rel, idt, "slab_bands", rid)])
        above = mapped[idx + 1][1] if idx + 1 < len(mapped) else roof_band
        if above is not None:
            entry["ceiling_height"] = _value((above[0] - yt) * s, "vector",
                                             [_ev(file_rel, above[2], "slab_bands", rid)])
            entry["floor_to_floor"] = _value((above[1] - yt) * s, "vector",
                                             [_ev(file_rel, above[3], "slab_bands", rid)])
        elif lv.get("kind") == "attic" and section.profile:
            top = _underside_max(section)
            if top is not None:
                entry["ceiling_height"] = _value((top[0] - yt) * s, "vector",
                                                 [_ev(file_rel, top[1], "roof_underside", rid)],
                                                 note="sloped: the roof underside, highest under the ridge")
            else:
                entry["ceiling_height"] = assumed(ceiling_default, "no roof underside found (brief ceiling_height)")
            entry["floor_to_floor"] = None
        else:
            entry["ceiling_height"] = assumed(ceiling_default, "nothing drawn above the top level (brief "
                                                               "ceiling_height)")
            entry["floor_to_floor"] = None
        mark = None
        if datum is not None:
            mark = next((m for m in marks if abs(m["value"] - datum["value"] - z(yt)) <= MARK_TOL_M), None) or \
                next((m for m in marks if abs(m["y"] - yt) * s <= MARK_TOL_M), None)
        if mark is not None:
            ev = [_ev(file_rel, mark["t"].id, "level_mark", rid, mark["t"].text)]
            entry["level_mark"] = _value(mark["value"] - datum["value"], "vector", ev,
                                         note=f"printed {mark['t'].text} - datum {datum['value']:.2f}")
            entry["level_mark_target_z"] = _value(z(mark["y"]), "vector", ev,
                                                  note=f"the line the mark points at{_what_at(section, mark['y'])}")
        else:
            entry["level_mark"] = None
            entry["level_mark_target_z"] = None
        out["levels"].append(entry)
        below = mapped[idx - 1][0]["id"] if idx > 0 else None
        out["slabs"].append({"between": [below, lv["id"]],
                             "thickness": _value((yt - yb) * s, "vector", [_ev(file_rel, idb, "slab_bands", rid)]),
                             "z_top": _value(z(yt), "vector", [_ev(file_rel, idt, "slab_bands", rid)])})
    for lv in levels[len(mapped):]:
        _assumed_level(out, lv, ceiling_default, slab_default, "not in the section")
    if roof_band is not None:
        top_id = mapped[-1][0]["id"]
        out["slabs"].append({"between": [top_id, None],
                             "thickness": _value((roof_band[1] - roof_band[0]) * s, "vector",
                                                 [_ev(file_rel, roof_band[2], "slab_bands", rid)]),
                             "z_top": _value(z(roof_band[1]), "vector", [_ev(file_rel, roof_band[3], "slab_bands",
                                                                                rid)])})

    # Ground per side: the upper line is the terrain; others are listed.
    for side in ("left", "right"):
        lines = sorted((g for g in section.ground if g[0] == side), key=lambda g: -g[1])
        if not lines:
            continue
        top_line = lines[0]
        note = None
        if len(lines) > 1:
            others = ", ".join(f"{z(g[1]):+.2f} m ({g[2]})" for g in lines[1:])
            note = f"upper of {len(lines)} ground lines; also drawn: {others}"
            warnings.append(f"section {rid}: {len(lines)} horizontal lines outside the {side} wall; the upper one "
                            f"({z(top_line[1]):+.2f} m) is read as the terrain, the others ({others}) are not")
        out["ground"].append({"side": side, "z": _value(z(top_line[1]), "vector",
                                                         [_ev(file_rel, top_line[2], "ground_line", rid)],
                                                         note=note)})

    # Cut axis.
    width_m = section.width * s
    if reference_extent is not None:
        fits = []
        for axis, ext in zip(("x", "y"), reference_extent):
            tol = max(SECTION_WIDTH_TOL[0] * ext, SECTION_WIDTH_TOL[1])
            if abs(width_m - ext) <= tol:
                fits.append((abs(width_m - ext), axis))
        if fits:
            out["cut_axis"] = min(fits)[1]
            if cut is not None and cut["axis"] != out["cut_axis"]:
                warnings.append(f"section {rid}: its width fits the {out['cut_axis']} extent but the cut line on "
                                f"{cut['region']} runs along {cut['axis']}: the cut line wins")
                out["cut_axis"] = cut["axis"]
        elif cut is not None:
            out["cut_axis"] = cut["axis"]
            warnings.append(f"section {rid}: {width_m:.2f} m wide, no outline extent fits; the cut line on "
                            f"{cut['region']} gives the axis {cut['axis']}")
        else:
            conflict("section_width_mismatch", [rid],
                     f"section {rid} is {width_m:.2f} m wide between its outer walls; the reference plan's outline is "
                     f"{reference_extent[0]:.2f} x {reference_extent[1]:.2f} m",
                     "unresolved: heights kept, cut direction unknown")

    # Roof.
    roof = out["roof"]
    prof = section.profile
    top_floor_y = mapped[-1][1][1] if mapped else None
    if prof and len(prof) >= 2:
        ids = section.profile_ids
        ev = [_ev(file_rel, i, "roof_line", rid) for i in ids]
        ends = [prof[0], prof[-1]]
        eave = min(ends, key=lambda p: p[1])
        ridge = max(prof, key=lambda p: p[1])
        roof["eaves_z"] = _value(z(eave[1]), "vector", ev[:1],
                                 note=None if top_floor_y is None else
                                 f"{(eave[1] - top_floor_y) * s:.2f} m above the top floor")
        roof["ridge_z"] = _value(z(ridge[1]), "vector", ev,
                                 note=None if top_floor_y is None else
                                 f"{(ridge[1] - top_floor_y) * s:.2f} m above the top floor")
        pitches = []
        for (ax, ay), (bx, by) in zip(prof, prof[1:]):
            if bx - ax <= 0:
                continue
            ang = math.degrees(math.atan2(abs(by - ay), bx - ax))
            if SLOPE_DEG[0] <= ang <= SLOPE_DEG[1] and not any(abs(ang - p) <= 0.5 for p in pitches):
                pitches.append(ang)
        left_side = [p for p in prof if p[0] <= ridge[0]]
        order = []
        for (ax, ay), (bx, by) in zip(left_side, left_side[1:]):
            if bx - ax > 0:
                order.append(math.degrees(math.atan2(abs(by - ay), bx - ax)))
        pitches.sort(key=lambda a: min((k for k, o in enumerate(order) if abs(o - a) <= 0.5), default=99))
        roof["pitches_deg"] = [_value(p, "vector", ev, nd=1) for p in pitches]
        x0, x1 = section.walls
        over = [x0 - prof[0][0], prof[-1][0] - x1]
        if all(o > 0 for o in over):
            roof["overhang"] = _value(min(over) * s, "vector", [_ev(file_rel, section.wall_ids[0], "roof_line", rid)],
                                      note=f"left {over[0] * s:.2f} m, right {over[1] * s:.2f} m")
        thick = _roof_thickness(section)
        if thick is not None:
            roof["thickness"] = _value(thick[0] * s, "vector", [_ev(file_rel, thick[1], "roof_line", rid)],
                                       note="perpendicular to the first slope")
        else:
            roof["thickness"] = assumed(None, "not drawn: the roof is one line in the section")
        knee = _knee(section, top_floor_y)
        if knee is not None:
            under = _underside_at(section, section.walls[0])
            under_note = "" if under is None or top_floor_y is None else \
                f"; the underside meets the outer face {(under - top_floor_y) * s:.2f} m above the floor"
            roof["knee_wall"] = _value(knee[0] * s, "vector", [_ev(file_rel, knee[1], "roof_line", rid)],
                                       note="the roof's top surface at the outer face of the outer wall above the top "
                                            f"floor (a cross-check){under_note}")
        # s along cut_axis, 0 at the building's min outer face along the axis: the section's left outer wall face,
        # or its right one when the cut line says the section is seen flipped.
        if cut is not None and cut["flipped"]:
            roof["profile"] = [[round((x1 - x) * s, 3) + 0.0, round(z(y), 3) + 0.0] for x, y in reversed(prof)]
        else:
            roof["profile"] = [[round((x - x0) * s, 3) + 0.0, round(z(y), 3) + 0.0] for x, y in prof]
    if cut is not None:
        out["cut_at"], out["flipped"] = cut["at"], cut["flipped"]
        if cut["flipped"]:
            for g in out["ground"]:
                g["side"] = {"left": "right", "right": "left"}[g["side"]]
    elif section.profile or out["ground"]:
        warnings.append(f"section {rid}: no cut line on the plans: the section's left end is taken as the building's "
                        f"min side along the cut axis (flipped unknown)")
    _name_ground_sides(out, rid, warnings)
    return out, warnings


def _name_ground_sides(out: dict, rid: str, warnings: list) -> None:
    """Section sides -> ``$defs/side``: along x the left end is ``left`` (-X), along y ``front`` (-Y) (not flipped).
    With the cut axis unknown, one level for both sides is ``all``; two different ones keep left/right (listed)."""
    names = {"x": {"left": "left", "right": "right"}, "y": {"left": "front", "right": "back"}}.get(out["cut_axis"])
    if names is not None:
        for g in out["ground"]:
            g["side"] = names[g["side"]]
        return
    zs = {round(float(g["z"]["value"]), 2) for g in out["ground"]}
    if len(out["ground"]) == 2 and len(zs) == 1:
        first = out["ground"][0]
        first["side"] = "all"
        first["z"]["evidence"] = first["z"]["evidence"] + out["ground"][1]["z"]["evidence"]
        out["ground"] = [first]
    elif out["ground"]:
        warnings.append(f"section {rid}: the cut direction is unknown: the ground levels keep the section's left/right")


def _what_at(section: SectionGeometry, y: float) -> str:
    for yb, yt, _, _ in section.bands:
        if abs(y - yb) <= 1e-6 * max(1.0, abs(y)) + 1e-6:
            return " (the bottom of a slab)"
        if abs(y - yt) <= 1e-6 * max(1.0, abs(y)) + 1e-6:
            return " (the top of a slab)"
    return ""


def _underside_max(section: SectionGeometry) -> Optional[tuple[float, str]]:
    """Highest point of the roof underside: the highest end of the sloped lines under the outer roof line."""
    if not section.underside:
        return None
    best = None
    for ln in section.underside:
        for p in (ln.a, ln.b):
            if best is None or p[1] > best[0]:
                best = (p[1], ln.id)
    return best


def _roof_thickness(section: SectionGeometry) -> Optional[tuple[float, str]]:
    prof = section.profile
    if len(prof) < 2 or not section.underside:
        return None
    (ax, ay), (bx, by) = prof[0], prof[1]
    length = math.hypot(bx - ax, by - ay)
    if length <= 0:
        return None
    ang = math.degrees(math.atan2(by - ay, bx - ax)) % 180.0
    nx, ny = -(by - ay) / length, (bx - ax) / length
    best = None
    lo, hi = (ROOF_THICKNESS_M[0] / section.mpu, ROOF_THICKNESS_M[1] / section.mpu)
    for ln in section.underside:
        if abs((ln.angle - ang + 90.0) % 180.0 - 90.0) > 1.0:
            continue
        d = abs((ln.a[0] - ax) * nx + (ln.a[1] - ay) * ny)
        if lo <= d <= hi and (best is None or d < best[0]):
            best = (d, ln.id)
    return best


def _knee(section: SectionGeometry, top_floor_y: Optional[float]) -> Optional[tuple[float, str]]:
    """The roof's top surface (the profile) at the left outer wall face, above the top floor (units, line id)."""
    if top_floor_y is None or section.walls is None or len(section.profile) < 2:
        return None
    x = section.walls[0]
    for (ax, ay), (bx, by), lid in zip(section.profile, section.profile[1:], section.profile_ids or [None] * 99):
        if ax <= x <= bx and bx > ax:
            return ay + (by - ay) * (x - ax) / (bx - ax) - top_floor_y, lid
    return None


def _underside_at(section: SectionGeometry, x: float) -> Optional[float]:
    """The highest roof underside line's y at ``x`` (None when no underside line passes over ``x``)."""
    ys = [y for ln in section.underside for y in [_y_on(ln, x)] if y is not None]
    return max(ys) if ys else None


def _assumed_level(out: dict, lv: dict, ceiling: float, slab: float, why: str) -> None:
    order = lv.get("order") or 0
    out["levels"].append({"level_id": lv["id"],
                          "floor_z": assumed(round(order * FLOOR_TO_FLOOR_M, 3), f"{why}: order x "
                                                                                 f"{FLOOR_TO_FLOOR_M:.2f} m"),
                          "ceiling_height": assumed(ceiling, f"{why}: brief ceiling_height"),
                          "floor_to_floor": assumed(FLOOR_TO_FLOOR_M, f"{why}: {FLOOR_TO_FLOOR_M:.2f} m (above the "
                                                                      f"ceiling and slab: an assumed plenum)"),
                          "level_mark": None, "level_mark_target_z": None})


def _assumed_levels(out: dict, levels: list[dict], ceiling: float, slab: float, why: str) -> None:
    prev = None
    for lv in levels:
        _assumed_level(out, lv, ceiling, slab, why)
        order = lv.get("order") or 0
        out["slabs"].append({"between": [prev, lv["id"]], "thickness": assumed(slab, f"{why}: brief slab_thickness"),
                             "z_top": assumed(round(order * FLOOR_TO_FLOOR_M, 3), f"{why}: the level's floor")})
        prev = lv["id"]
