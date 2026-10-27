"""Exterior evidence (docs/milestone10.md §3.1 item 8): the roof type, facade materials, openings seen from outside,
the site and the north arrow.

What: ``exterior(top_plan, section, elevations, sites, reference_outline, heights, conflict, warnings) -> dict``,
the ``exterior`` block of ``sheets.json``.

Why: the builder (track E) needs the roof type, outline and break line, and the facade only where a drawing says
it; everything else is ``assumed`` later and listed.

How:
- roof from the top plan's roof lines: a closed outline around everything else of the plan (``register.roof_outlines``)
  and a closed outline inside it covering >= 30 % of it (the line where the slope changes) mean a **mansard**
  (``type_source: plan_roof_lines``); the break line is compared with the section's slope change (a difference is a
  warning). Without plan lines a roof plan whose slope texts all give one slope (real06, 24 Oct 2026: ``EĞİM%33``
  ten times, with hip lines) is a **hip** roof at that slope (``type_source: roof_plan``; the pitch goes first in
  ``pitches_deg``); else the section's profile decides: one slope per side ``gable`` (the hip/gable choice across
  the section is assumed), two slopes per side ``gambrel``, no slope and a slab on top ``flat``;
- 27 Oct 2026: the roofs a roof plan draws (``roof_plan_outline``, ``roof.plan_outline`` in the roof plan's own
  metres): the eaves loop the hip and valley lines end on, the drawn wall line inside it (the overhang), and every
  other roof drawn beside it (a lower roof over a veranda or a porch, a canopy); the building registers them on the
  top level's walls (``to_building.roof_outline_record``);
- facades: elevation regions (side from their title: GÜNEY / SOUTH / SÜD / SUD = south ...), materials from
  labels (``SIVA``, ``TAŞ KAPLAMA``, ``AHŞAP``, ``TUĞLA``, render, stone, timber, brick) and hatches; window- and
  door-sized rectangles counted per facade (positions along the facade);
- site plans: the plot (the largest closed outline), labelled areas (parking, garden, paving ...), trees (circles) and
  the north arrow (an ``N`` / ``K`` text: north points from the arrow's centre to it; ``north`` = the compass
  bearing of the drawing's +Y).
- Milestone 13 (docs/milestone13.md §13.2, track T6; CLAUDE.md vegetation rules): ``hedge_rows`` turns rows of tree
  symbols into hedges: >= ``HEDGE_MIN_COUNT`` circles of equal radius (within ``HEDGE_RADIUS_TOL_M``) at most
  ``HEDGE_MAX_RADIUS_M`` at a pitch <= ``HEDGE_PITCH_FACTOR`` x their diameter along a line or a gentle polyline
  (turns <= ``HEDGE_MAX_TURN_DEG`` between steps). ``site_of`` writes them as ``hedges`` (the building's
  ``site.hedges``: id, polyline, width, height by class, species null, inferred, the symbols as evidence); the
  symbols of a hedge are no longer single trees (real04: 101 symbols of r 0.359 m in four rows, 42 / 45 / 7 / 7,
  became 100 four-metre trees in Milestone 12).
"""
from __future__ import annotations

import math
import re
from typing import Callable, Optional

from shapely.geometry import Point, Polygon

from wenart.sheets import register as RG
from wenart.sheets import titles as T
from wenart.sheets import units_check as UC

BREAK_MIN_SHARE = 0.30
SIDE_WORDS = [
    ("south", r"\bGUNEY\b|\bSOUTH\b|\bSUD\b|\bSUED\b"), ("north", r"\bKUZEY\b|\bNORTH\b|\bNORD\b"),
    ("east", r"\bDOGU\b|\bEAST\b|\bOST\b|\bEST\b"), ("west", r"\bBATI\b|\bWEST\b|\bOUEST\b"),
    ("front", r"\bON\b|\bFRONT\b|\bVORDER"), ("back", r"\bARKA\b|\bBACK\b|\bREAR\b|\bRUECK|\bRUCK"),
    ("left", r"\bSOL\b|\bLEFT\b"), ("right", r"\bSAG\b|\bRIGHT\b"),
]
MATERIAL_WORDS = [
    ("stone_cladding", r"\bTAS KAPLAMA\b|\bTAS\b|\bSTONE\b|\bNATURSTEIN\b|\bPIERRE\b"),
    ("wood_cladding", r"\bAHSAP\b|\bTIMBER\b|\bWOOD\b|\bHOLZ\b|\bBOIS\b"),
    ("brick", r"\bTUGLA\b|\bBRICK\b|\bKLINKER\b|\bBRIQUE\b"),
    ("render", r"\bSIVA\b|\bRENDER\b|\bPUTZ\b|\bENDUIT\b|\bSTUCCO\b"),
    ("fibre_cement", r"\bKOMPOZIT\b|\bFIBRE CEMENT\b|\bFIBER CEMENT\b"),
]
# Roof coverings named on an elevation or roof plan (exterior vocabulary slugs, never a colour).
COVERING_WORDS = [
    ("concrete_tiles", r"\bBETON KIREMIT\b|\bCONCRETE TILES?\b|\bBETONDACHSTEIN\b|\bTUILES? BETON\b"),
    ("clay_tiles", r"\bKIREMIT\b|\bCLAY TILES?\b|\bROOF TILES?\b|\bDACHZIEGEL\b|\bZIEGEL\b|\bTUILES?\b"),
    ("slate", r"\bARDUAZ\b|\bSLATE\b|\bSCHIEFER\b|\bARDOISE\b"),
    ("standing_seam", r"\bTRAPEZ\b|\bSTANDING SEAM\b|\bSTEHFALZ\b|\bJOINT DEBOUT\b"),
    ("green_roof", r"\bYESIL CATI\b|\bGREEN ROOF\b|\bGRUNDACH\b|\bGRUENDACH\b|\bTOITURE VEGETALE\b"),
]
TREE_BLOCK_RE = re.compile(r"AGAC|TREE|BAUM|ARBRE|ARBOL")

# Milestone 13 (T6): the hedge-row detector lives in wenart.blender.vegetation (pure, no shapely: the Blender build
# runs it too); the sheets stage re-exports it so ``hedge_rows`` is the sheets API (docs/milestone13.md §13.2).
from wenart.blender.vegetation import (HEDGE_CLASS_RADIUS_M, HEDGE_HEIGHT_M, HEDGE_MAX_RADIUS_M,  # noqa: E402,F401
                                       HEDGE_MAX_TURN_DEG, HEDGE_MIN_COUNT, HEDGE_PITCH_FACTOR,
                                       HEDGE_RADIUS_TOL_M, HEDGE_SIMPLIFY_M, hedge_height_class, hedge_rows)


def hedge_records(trees: list, region_id: Optional[str] = None) -> tuple[list[dict], list]:
    """``(hedges, single_trees)`` of the sheets reader's tree list (pure): the hedges of ``hedge_rows`` as
    ``site.hedges`` records (``id``, ``polyline``, ``width_m``, ``height_m``, ``height_class``, ``species`` null,
    ``inferred`` true, ``evidence`` = the symbols' evidence with ``rule: site_hedge_symbol``, ``symbol_count``,
    ``pitch_m``) and the trees that are in no row."""
    rows = hedge_rows(trees)
    taken = set()
    hedges = []
    for k, row in enumerate(rows):
        ev = []
        for i in row["symbol_indices"]:
            taken.add(i)
            for e in (trees[i].get("evidence") or [])[:1]:
                ev.append(dict(e, rule="site_hedge_symbol"))
        hedges.append({"id": f"hedge_{k + 1:03d}", "polyline": row["polyline"], "width_m": row["width_m"],
                       "height_m": row["height_m"], "height_class": row["height_class"], "species": None,
                       "inferred": True, "symbol_count": row["count"], "pitch_m": row["pitch_m"],
                       "length_m": row["length_m"], "symbol_ids": row["symbol_ids"], "evidence": ev,
                       "reason": f"{row['count']} tree symbols of radius {row['radius_m']:.2f} m at a pitch of "
                                 f"{row['pitch_m']:.2f} m in one row: a {row['height_class']} hedge "
                                 f"{row['height_m']:.1f} m high (height assumed; species not drawn)"})
    singles = [t for i, t in enumerate(trees) if i not in taken]
    return hedges, singles
NORTH_BLOCK_RE = re.compile(r"KUZEY|NORTH|NORD")
PLOT_WALL_M = (0.05, 0.6)            # site plan: two closed rings this far apart inside the plot are a plot wall
WINDOW_M = ((0.4, 3.0), (0.4, 2.6))
DOOR_M = ((0.7, 3.0), (1.9, 2.8))


def area_kind(label: str) -> Optional[str]:
    """What a site label names (``wenart.ingest.generic.labels.area_kind``: parking, garden, paving, pool, terrace;
    None = not a site word)."""
    from wenart.ingest.generic.labels import area_kind as kind_of
    return kind_of(label)


def side_of(title: Optional[str]) -> Optional[str]:
    """The side an elevation's title names (``$defs/side``), or None."""
    folded = T.fold(title or "")
    for side, pattern in SIDE_WORDS:
        if re.search(pattern, folded):
            return side
    return None


COMPASS_DEG = {"north": 0.0, "east": 90.0, "south": 180.0, "west": 270.0}
LOCAL_NORMAL_DEG = {"right": 0.0, "back": 90.0, "left": 180.0, "front": 270.0}     # ccw from +X


def normal_deg(side: Optional[str], north_deg: Optional[float]) -> Optional[float]:
    """The outward normal of a side in the building frame, degrees counter-clockwise from +X (None for ``all`` or a
    compass side without a north). ``north_deg`` = compass bearing of the building's +Y."""
    if side in LOCAL_NORMAL_DEG:
        return LOCAL_NORMAL_DEG[side]
    if side in COMPASS_DEG and north_deg is not None:
        return round((90.0 - (COMPASS_DEG[side] - north_deg)) % 360.0, 3) + 0.0
    return None


def view_bearing_deg(side: Optional[str], north_deg: Optional[float]) -> Optional[float]:
    """The direction the viewer of an elevation looks (towards the building), degrees counter-clockwise from +X."""
    n = normal_deg(side, north_deg)
    return None if n is None else round((n + 180.0) % 360.0, 3) + 0.0


def compass_of(normal: float, north_deg: float) -> tuple[str, float]:
    """(nearest compass side, compass bearing) of an outward normal given ccw from +X."""
    bearing = (north_deg + 90.0 - normal) % 360.0
    side = min(COMPASS_DEG, key=lambda k: min(abs(COMPASS_DEG[k] - bearing), 360.0 - abs(COMPASS_DEG[k] - bearing)))
    return side, round(bearing, 3) + 0.0


def _apply(tf: list, p) -> tuple[float, float]:
    return (round(tf[0] * p[0] + tf[1] * p[1] + tf[2], 4) + 0.0, round(tf[3] * p[0] + tf[4] * p[1] + tf[5], 4) + 0.0)


def _closed_pts(e) -> Optional[list]:
    if len(e.strokes) != 1 or not e.strokes[0].closed or len(e.strokes[0].pts) < 3:
        return None
    pts = list(e.strokes[0].pts)
    # 11 Oct 2026 (real04): a closed polyline whose last vertex repeats the first a little off (0.45 units on the
    # pools) closes into a tiny bow-tie that shapely calls invalid; the near-duplicate is dropped
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    if len(pts) > 3 and math.dist(pts[0], pts[-1]) <= 1e-3 * diag:
        pts = pts[:-1]
    return pts


def _ev(region, entity: Optional[str], rule: str, text: Optional[str] = None, confidence: float = 1.0) -> dict:
    ev = {"file": region.file, "page": region.sheet.page, "layer": None, "entity": entity, "method": "vector",
          "confidence": confidence, "rule": rule, "region_id": region.id}
    if text is not None:
        ev["text"] = text
    return ev


def roof_from_plan(top, warnings: list, section=None) -> Optional[dict]:
    """Roof outline and break line drawn on the top plan (building metres), or None."""
    if top is None or top.transform_to_building is None or not top.metres_per_unit:
        return None
    mpu = top.metres_per_unit
    ids = RG.roof_outlines(top, mpu)
    if not ids:
        return None
    outline_ent = next(e for e in top.ents if e.id == ids[0])
    pts = _closed_pts(outline_ent)
    if pts is None:
        return None
    opoly = Polygon(pts)
    inner = []
    for e in top.ents:
        if e is outline_ent:
            continue
        ip = _closed_pts(e)
        if ip is None or len(ip) < 4:
            continue
        poly = Polygon(ip)
        if poly.is_valid and opoly.contains(poly) and poly.area >= BREAK_MIN_SHARE * opoly.area:
            inner.append((poly.area, e, ip))
    tf = top.transform_to_building
    out = {"outline": [list(_apply(tf, p)) for p in pts], "break_line": None, "type": None,
           "evidence": [_ev(top, outline_ent.id, "roof_outline")]}
    w = (opoly.bounds[2] - opoly.bounds[0]) * mpu
    h = (opoly.bounds[3] - opoly.bounds[1]) * mpu
    out["note"] = f"roof outline {w:.2f} x {h:.2f} m on {top.id}"
    if inner:
        _, e, ip = max(inner, key=lambda x: x[0])
        out["break_line"] = [list(_apply(tf, p)) for p in ip]
        out["type"] = "mansard"
        out["evidence"].append(_ev(top, e.id, "roof_break_line"))
        bb = Polygon(ip).bounds
        out["note"] += f"; closed line inside it {(bb[2] - bb[0]) * mpu:.2f} x {(bb[3] - bb[1]) * mpu:.2f} m " \
                       f"({e.id}): the slope changes there (mansard)"
        if section is not None and section.profile and len(section.profile) >= 4 and section.mpu:
            prof = section.profile
            change = (prof[-2][0] - prof[1][0]) * section.mpu
            widths = ((bb[2] - bb[0]) * mpu, (bb[3] - bb[1]) * mpu)
            nearest = min(widths, key=lambda v: abs(v - change))
            if abs(nearest - change) > 0.05:
                warnings.append(f"roof: the break line on {top.id} ({e.id}) is {nearest:.2f} m wide along the cut, the "
                                f"section's slope changes {change:.2f} m apart ({abs(nearest - change):.2f} m); both "
                                f"kept as drawn")
    return out


SLOPE_PCT_RE = re.compile(r"\b(?:EGIM|SLOPE|PENTE|NEIGUNG|GEFALLE)\b\s*:?\s*%\s*(\d+(?:[.,]\d+)?)"
                          r"|\b(?:EGIM|SLOPE|PENTE|NEIGUNG|GEFALLE)\b\s*:?\s*(\d+(?:[.,]\d+)?)\s*%")


def roof_from_roof_plan(roof_plans: list) -> Optional[dict]:
    """A hip roof from a roof plan whose slope texts (>= 2, ``EĞİM%33``) all give one slope and whose hip lines
    (>= 2) run from the corners: ``{"type": "hip", "pitch_deg", "slope_pct", "evidence", "note"}``, or None."""
    for r in roof_plans:
        slopes = []
        for t in r.texts:
            m = SLOPE_PCT_RE.search(T.fold(t.text))
            if m:
                slopes.append((float((m.group(1) or m.group(2)).replace(",", ".")), t))
        if len(slopes) < 2 or (r.features or {}).get("hip_lines", 0) < 2:
            continue
        values = sorted(v for v, _ in slopes)
        if values[-1] - values[0] > 1.0 or values[0] <= 0:
            continue
        pct = values[len(values) // 2]
        pitch = math.degrees(math.atan(pct / 100.0))
        return {"type": "hip", "pitch_deg": pitch, "slope_pct": pct,
                "evidence": [_ev(r, t.id, "roof_slope_text", text=t.text) for _, t in slopes[:3]],
                "note": f"{len(slopes)} slope texts on {r.id} all give {pct:g} % ({pitch:.1f} degrees), "
                        f"{r.features.get('hip_lines')} hip lines: a hip roof"}
    return None


# 27 Oct 2026 (real06; user: "In the plan roof is covering this balcony also and there is a small roof on top of the
# rest of the veranda", "The project needs to find these kind of things by itself"): a roof plan draws the roof's
# outline, not only its type. The hip roof was built over the outer walls + overhang (assumed) while the roof plan drew
# the eaves around the first-floor balcony too, and a lower roof beside it over the rest of the veranda. Every
# tolerance below has a physical reason; none is a value of one drawing.
ROOF_PLAN = {
    # a hip or valley runs from an eaves corner up to the ridge: at least a metre on any roof over a room (a 1.5 m
    # wing at 45 degrees has 1.06 m hips); slope arrows and tile hatching are shorter
    "hip_min_m": 1.0,
    # hips and valleys of equal pitches meet the eaves at 45 degrees (unequal pitches lean, rarely past 20-70)
    "hip_angle_deg": (20.0, 70.0),
    # a roof line drawn up to 2 cm short of the next one still closes the loop (a drafting gap, far under any edge)
    "join_m": 0.02,
    # a hip ends on the eaves loop when its end lies this close to it (under a gutter's width)
    "end_tol_m": 0.05,
    # a closed loop smaller than a small room is no roof over the building (a downpipe box, a chimney cap)
    "min_roof_m2": 4.0,
    # an exploded hatch pattern (tiles, gravel, colour fills) draws many strokes shorter than half a metre; a roof's
    # eaves, gutter and ridge lines run metres
    "hatch_min_lines": 50, "hatch_short_m": 0.5, "hatch_share": 0.9,
    # a layer whose texts are mostly bare numbers holds dimension chains (their lines are no roof edges)
    "dim_text_share": 0.5,
    # the eaves stand 0.1-1.5 m outside the walls under them: a closed line inside the eaves loop at a constant offset
    # in this range (within 5 cm all round) is the drawn wall line ("lower building line")
    "wall_offset_m": (0.1, 1.5), "offset_tol_m": 0.05,
    # a separate roof (a lower roof, a canopy over a door or a porch) is at least a canopy's size and wider than a
    # gutter band between two eaves lines
    "other_min_m2": 1.0, "other_min_width_m": 0.3,
    # it joins the main roof when it lies within a gutter and its fascia of the eaves loop; a roof drawn apart from
    # the main one is a roof when it has hips of its own (a box, a legend or a plot line drawn apart has none)
    "touch_m": 0.4, "apart_min_hips": 2,
}
_BARE_NUMBER_RE = re.compile(r"^[\s\d.,+\-/x×]+$")


def _hip_like(a, b, cfg: dict = ROOF_PLAN) -> bool:
    ang = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) % 90.0
    return cfg["hip_angle_deg"][0] <= ang <= cfg["hip_angle_deg"][1] and math.dist(a, b) >= cfg["hip_min_m"]


def _annotation_layers(region, mpu: float, cfg: dict = ROOF_PLAN) -> tuple[set, set]:
    """``(dimension layers, hatch layers)`` of a region (pure): layers whose texts are mostly bare numbers, and layers
    of many short strokes (an exploded hatch pattern)."""
    texts: dict = {}
    for t in region.texts:
        n = texts.setdefault(t.layer, [0, 0])
        n[0] += 1
        n[1] += bool(_BARE_NUMBER_RE.match(t.text or ""))
    dims = {k for k, (n, num) in texts.items() if n and num >= cfg["dim_text_share"] * n}
    strokes: dict = {}
    for e in region.ents:
        for a, b, _st in UC.segments(e.strokes):
            n = strokes.setdefault(e.layer, [0, 0])
            n[0] += 1
            n[1] += math.dist(a, b) * mpu < cfg["hatch_short_m"]
    hatch = {k for k, (n, short) in strokes.items() if n >= cfg["hatch_min_lines"] and short >= cfg["hatch_share"] * n}
    return dims, hatch


def _loops(segments: list, join: float) -> tuple[list, list]:
    """``(faces, rings)`` of straight segments ``(a, b, entity)`` (metres): the faces they close (each segment
    lengthened by ``join`` at both ends, so a corner drawn short still closes) and every distinct closed ring among
    the faces' outer and inner rings and the outer rings of their union (pure, shapely)."""
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union

    lines = []
    for a, b, _e in segments:
        d = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        lines.append(LineString([(a[0] - ux * join, a[1] - uy * join), (b[0] + ux * join, b[1] + uy * join)]))
    if not lines:
        return [], []
    faces = [f for f in polygonize(unary_union(lines)) if f.area > 0]
    rings = []
    union = unary_union(faces) if faces else None
    for g in getattr(union, "geoms", [union]) if union is not None else []:
        rings.append(Polygon(g.exterior))
    for f in faces:
        rings.append(Polygon(f.exterior))
        rings += [Polygon(h) for h in f.interiors]
    out = []
    for p in rings:
        if p.is_valid and not any(abs(p.area - q.area) < 1e-6 * max(1.0, p.area) and p.symmetric_difference(q).area
                                  < 1e-4 for q in out):
            out.append(p)
    return faces, out


def _ring_pts(poly) -> list:
    """The corners of a polygon's outer ring, counter-clockwise, collinear points dropped (1 cm), as lists."""
    from shapely.geometry.polygon import orient
    p = orient(poly.simplify(0.01, preserve_topology=True), 1.0)
    return [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(p.exterior.coords)[:-1]]


def roof_plan_outline(region, cfg: dict = ROOF_PLAN) -> tuple[Optional[dict], str]:
    """The roofs a roof plan draws, in the region's own metres (``(x - x0, y - y0) * metres_per_unit`` from the
    region's geometry box corner; ``to_building.roof_outline_record`` registers them on the walls). Returns ``(record,
    why)``; the record is None when nothing could be read (``why`` says why).

    How (any outline shape, any number of separate roofs):

    - the roof's lines: hip and valley lines (``_hip_like``) tell the layers the roof is drawn on (each with two or
      more of them; else every layer holding one); dimension layers, hatch patterns, the section cut line, texts and
      arcs never count (``_annotation_layers``);
    - the eaves loop of the main roof: among the closed loops of the roof's lines (``_loops``), the one most hip and
      valley lines end on (their other end inside it), at least two, at least ``min_roof_m2`` (ties: the larger);
    - the wall line: a closed loop of the roof's lines without its hips, inside the eaves loop at a constant offset of
      ``wall_offset_m`` (the drawn "lower building line"); its offset is the drawn overhang;
    - the other roofs (a lower roof over a veranda or a porch, a canopy, another hipped roof): the closed faces of the
      lines outside the main roof (on any layer but the annotation ones), joined where they touch, each at least
      ``other_min_m2`` and ``other_min_width_m`` wide (a gutter band between two eaves lines is no roof), smaller than
      the main roof and not around it, and either joining it (``touch_m``) or with hips of its own
      (``apart_min_hips``).

    Record: ``{"region_id", "frame": {"origin_units", "metres_per_unit"}, "points", "area_m2", "size_m", "hip_lines",
    "layers", "entities", "wall_line", "overhang_m", "others": [{"points", "area_m2", "size_m", "layers", "entities",
    "touches_main", "hip_lines"}], "evidence", "note"}``."""
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union

    mpu = region.metres_per_unit
    if not mpu:
        return None, f"roof plan {region.id}: no drawing unit"
    x0, y0 = region.geometry_box[0], region.geometry_box[1]
    dims, hatch = _annotation_layers(region, mpu, cfg)
    segs = []
    for e in region.ents:
        if e.dim is not None or e.kind in ("HATCH", "DIMENSION") or e.layer in dims or e.layer in hatch \
                or RG.CUT_LAYER_RE.search(T.fold(e.layer or "")):
            continue
        for a, b, _st in UC.segments(e.strokes):
            am = ((a[0] - x0) * mpu, (a[1] - y0) * mpu)
            bm = ((b[0] - x0) * mpu, (b[1] - y0) * mpu)
            if math.dist(am, bm) >= cfg["join_m"]:
                segs.append((am, bm, e))
    hips = [s for s in segs if _hip_like(s[0], s[1], cfg)]
    if len(hips) < 2:
        return None, f"roof plan {region.id}: fewer than two hip or valley lines (the eaves loop cannot be told)"
    per_layer: dict = {}
    for s in hips:
        per_layer[s[2].layer] = per_layer.get(s[2].layer, 0) + 1
    layers = {k for k, n in per_layer.items() if n >= 2} or set(per_layer)
    roof_segs = [s for s in segs if s[2].layer in layers]
    _faces, rings = _loops(roof_segs, cfg["join_m"])
    roof_hips = [s for s in hips if s[2].layer in layers]
    best = None
    for poly in rings:
        if poly.area < cfg["min_roof_m2"]:
            continue
        ring, grown = poly.exterior, poly.buffer(cfg["end_tol_m"])
        on = []
        for a, b, e in roof_hips:
            da, db = ring.distance(Point(a)), ring.distance(Point(b))
            if min(da, db) <= cfg["end_tol_m"] + cfg["join_m"] and grown.contains(Point(b if da <= db else a)) \
                    and max(da, db) > cfg["end_tol_m"] + cfg["join_m"]:
                on.append(e.id)
        key = (len(on), poly.area)
        if len(on) >= 2 and (best is None or key > best[0]):
            best = (key, poly, on)
    if best is None:
        return None, (f"roof plan {region.id}: no closed loop of its roof lines "
                      f"({', '.join(sorted(map(str, layers)))}) that two or more hip or valley lines end on")
    (_n, _a), main, on = best
    pts = _ring_pts(main)
    ring = main.exterior
    tol = cfg["end_tol_m"]
    ents = sorted({e.id for a, b, e in roof_segs if ring.distance(Point(a)) <= tol and ring.distance(Point(b)) <= tol
                   and LineString([a, b]).length > 0})
    # the wall line: the roof's lines without the hips and valleys, a loop inside at a constant offset
    _f2, rings2 = _loops([s for s in roof_segs if not _hip_like(s[0], s[1], cfg)], cfg["join_m"])
    wall, offset = None, None
    for poly in sorted(rings2, key=lambda p: -p.area):
        if poly.area >= main.area - 1e-6 or not main.buffer(1e-6).contains(poly):
            continue
        cs = list(poly.exterior.coords)
        mids = [((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0) for p, q in zip(cs, cs[1:])]
        ds = sorted(ring.distance(Point(m)) for m in mids)
        d = ds[len(ds) // 2]
        if not cfg["wall_offset_m"][0] <= d <= cfg["wall_offset_m"][1]:
            continue
        shrunk = main.buffer(-d, join_style=2)
        if shrunk.is_empty or shrunk.geom_type != "Polygon" \
                or shrunk.exterior.hausdorff_distance(poly.exterior) > cfg["offset_tol_m"]:
            continue
        wall, offset = poly, d
        break
    # the other roofs: the closed faces of the lines outside the main roof, joined where they touch
    inner = main.buffer(-cfg["join_m"])
    outside = [s for s in segs if not inner.contains(LineString([s[0], s[1]]))]
    faces3, _r3 = _loops(outside, cfg["join_m"])
    # a face around the main roof (a plot, a site or a frame line: the main roof is its hole) or larger than it is
    # no other roof and must not join the faces inside it
    keep = [f for f in faces3 if not main.contains(f.representative_point()) and f.area >= 0.25 * cfg["other_min_m2"]
            and not f.buffer(-cfg["other_min_width_m"] / 2.0).is_empty
            and not Polygon(f.exterior).contains(main.representative_point()) and f.area <= main.area]
    others = []
    joined = unary_union(keep) if keep else None
    for g in getattr(joined, "geoms", [joined]) if joined is not None else []:
        if g.geom_type != "Polygon" or g.area < cfg["other_min_m2"]:
            continue
        g = Polygon(g.exterior)
        # a loop around the main roof (a plot, a site or a frame line) or larger than it is no other roof
        if g.contains(main.representative_point()) or g.area > main.area:
            continue
        touches = g.distance(main) <= cfg["touch_m"]
        n_hips = sum(1 for a, b, _e in hips if g.buffer(tol).contains(LineString([a, b])))
        if not touches and n_hips < cfg["apart_min_hips"]:
            continue
        edge_ents = sorted({e.id for a, b, e in outside if g.exterior.distance(Point(a)) <= tol
                            and g.exterior.distance(Point(b)) <= tol})
        gb = g.bounds
        others.append({"points": _ring_pts(g), "area_m2": round(g.area, 3),
                       "size_m": [round(gb[2] - gb[0], 3), round(gb[3] - gb[1], 3)],
                       "layers": sorted({str(e.layer) for e in region.ents if e.id in set(edge_ents)}),
                       "entities": edge_ents, "touches_main": touches, "hip_lines": n_hips})
    mb = main.bounds
    ev = [_ev(region, eid, "roof_plan_outline") for eid in ents[:6]]
    note = (f"the eaves loop of the roof lines of {region.id} ({', '.join(sorted(map(str, layers)))}): {len(pts)} "
            f"corners, {mb[2] - mb[0]:.2f} x {mb[3] - mb[1]:.2f} m, {main.area:.2f} m2; {len(on)} hip or valley lines "
            f"end on it")
    if wall is not None:
        note += f"; the drawn wall line runs {offset:.2f} m inside it (the overhang)"
    if others:
        note += "; " + ", ".join(f"another roof of {o['area_m2']:.2f} m2" + (" beside it" if o["touches_main"] else "")
                                 for o in others)
    return {"region_id": region.id, "frame": {"origin_units": [x0, y0], "metres_per_unit": mpu},
            "points": pts, "area_m2": round(main.area, 3), "size_m": [round(mb[2] - mb[0], 3), round(mb[3] - mb[1], 3)],
            "hip_lines": len(on), "layers": sorted(map(str, layers)), "entities": ents,
            "wall_line": _ring_pts(wall) if wall is not None else None,
            "overhang_m": round(offset, 3) if offset is not None else None, "others": others,
            "evidence": ev, "note": note}, ""


def roof_from_section(section) -> Optional[tuple[str, list[str]]]:
    """(type, assumed) from the section profile alone."""
    if section is None or not section.profile:
        if section is not None and len(section.bands) >= 1 and not section.roof_lines:
            return "flat", []
        return None
    prof = section.profile
    ridge_k = max(range(len(prof)), key=lambda k: prof[k][1])
    left = [p for p in prof[: ridge_k + 1]]
    slopes_left = sum(1 for a, b in zip(left, left[1:]) if b[0] > a[0] and b[1] > a[1])
    if slopes_left <= 1:
        return "gable", ["hip/gable choice across the section (no roof plan or elevation)"]
    return "gambrel", ["mansard/gambrel choice across the section (no roof plan or elevation)"]


def gable_end(region) -> Optional[str]:
    """The entity id of a closed wall outline of an elevation that peaks in the middle (a gable end: two equal eaves
    corners and one higher point between them), else None."""
    for e in region.ents:
        for st in e.strokes:
            if not st.closed or len(st.pts) < 5:
                continue
            xs = [p[0] for p in st.pts]
            ys = [p[1] for p in st.pts]
            top = max(range(len(st.pts)), key=lambda k: ys[k])
            w = max(xs) - min(xs)
            if w <= 0 or abs(xs[top] - (min(xs) + max(xs)) / 2.0) > 0.05 * w:
                continue
            below = sorted(ys)[-3:-1]                         # the two eaves corners under the peak
            if abs(below[0] - below[1]) <= 0.01 * w and ys[top] - below[1] > 0.05 * w:
                return e.id
    return None


def elevation_z(region, datum: Optional[float], ground_z: Optional[float]) -> Optional[dict]:
    """How an elevation's y maps to building z: ``z = (y - y_ref) * metres_per_unit + z_ref``.

    A level mark wins (``43.00`` with the section's datum 43.00 is z 0; a mark more than 30 m from the datum, or a
    small mark without a datum, is read as relative to the ground floor: ``±0.00`` is z 0). An absolute mark (over
    30 m) without a datum is read against the elevation's own ground: the mark on the ground line (else the lowest
    mark) is taken as the ground's z (assumed, with a ``warning``). Else the lowest horizontal line spanning half the
    drawing is the ground (z of the section's ground line, else 0.0 assumed); else None."""
    mpu = region.metres_per_unit
    if not mpu:
        return None
    segs = UC.segments([st for e in region.ents for st in e.strokes])
    gb = region.geometry_box
    width = gb[2] - gb[0]
    flat = [(min(a[1], b[1]), st) for a, b, st in segs
            if abs(a[1] - b[1]) <= 1e-6 * max(1.0, abs(a[1])) + 1e-9 and abs(b[0] - a[0]) >= 0.5 * width]
    marks = [(t, value, mp) for t, value in UC.mark_texts(region.texts) for mp in [UC.mark_point(t, segs)]
             if mp is not None]
    if marks:
        t, value, mp = marks[0]
        if datum is not None and abs(value - datum) <= 30.0:
            return {"y_ref": mp[1], "z_ref": round(value - datum, 4), "method": "vector",
                    "evidence": [_ev(region, t.id, "level_mark", t.text)],
                    "note": f"level mark {t.text} - datum {datum:.2f}"}
        if abs(value) <= 30.0:
            return {"y_ref": mp[1], "z_ref": round(value, 4), "method": "vector",
                    "evidence": [_ev(region, t.id, "level_mark", t.text)],
                    "note": f"level mark {t.text} read relative to the ground floor"}
        # Absolute marks and no datum: the elevation's own ground mark is the ground (assumed).
        g_tol = 0.02 / mpu
        ground_y = min(f[0] for f in flat) if flat else None
        on_ground = [m for m in marks if ground_y is not None and abs(m[2][1] - ground_y) <= g_tol]
        gt, _, gmp = on_ground[0] if on_ground else min(marks, key=lambda m: m[2][1])
        gz = ground_z if ground_z is not None else 0.0
        where = "on its ground line" if on_ground else "the lowest"
        note = f"no section datum: the elevation's mark {gt.text} ({where}) taken as z {gz:.2f} (assumed)"
        return {"y_ref": gmp[1], "z_ref": round(gz, 4), "method": "derived",
                "evidence": [_ev(region, gt.id, "level_mark", gt.text, confidence=0.5)], "note": note,
                "warning": f"elevation {region.id}: {note}"}
    if flat:
        y, st = min(flat, key=lambda f: f[0])
        z_ref = ground_z if ground_z is not None else 0.0
        note = ("the lowest long horizontal line is the ground (the section's ground level)" if ground_z is not None
                else "the lowest long horizontal line is the ground, taken as z 0.00 (assumed)")
        return {"y_ref": y, "z_ref": z_ref, "method": "derived",
                "evidence": [_ev(region, getattr(st, "id", None), "ground_line", confidence=0.6)], "note": note}
    return None


def facade_of(region, zmap: Optional[dict] = None, north_deg: Optional[float] = None,
              warnings: Optional[list] = None) -> tuple[list[dict], dict]:
    """(facade entries, openings seen) of one elevation region. ``zmap``: ``elevation_z`` (z ranges in building z)."""
    titled = side_of(region.title["text"] if region.title else None)
    side = titled or "all"
    if titled is None and warnings is not None:
        warnings.append(f"elevation {region.id}: no side in its title: its facade entries are listed for side 'all' "
                        f"(not mapped onto a side)")
    mpu = region.metres_per_unit or 0.0

    def zr(y0: float, y1: float) -> Optional[list]:
        if zmap is None or not mpu:
            return None
        return [round((y - zmap["y_ref"]) * mpu + zmap["z_ref"], 3) + 0.0 for y in (y0, y1)]

    entries = []
    for t in region.texts:
        folded = T.fold(t.text)
        for slug, pattern in MATERIAL_WORDS:
            if re.search(pattern, folded):
                entries.append({"region": region.id, "side": side, "z_range": None, "colour": None, "material": slug,
                                "source": "label", "evidence": [_ev(region, t.id, "facade_label", t.text)]})
                break
    segs = UC.segments([st for e in region.ents for st in e.strokes])
    for e in region.ents:
        if e.kind == "HATCH" and mpu:
            b = e.box
            band = zr(b[1], b[3])
            if band is not None and band[1] <= 0.01:
                # Below the ground floor's level: terrain or a foundation, not a facade (listed).
                if warnings is not None:
                    warnings.append(f"elevation {region.id}: hatch {e.id} lies below the ground floor's level "
                                    f"(z {band[0]:.2f} to {band[1]:.2f} m): terrain or foundation, not a facade")
                continue
            label = _label_in(region, b) or _label_by_leader(region, b, segs)
            entry = {"region": region.id, "side": side, "z_range": zr(b[1], b[3]), "colour": None,
                     "material": label[0] if label else "hatched", "source": "hatch",
                     "evidence": [_ev(region, e.id, "facade_hatch", confidence=0.6)]}
            if label:
                entry["evidence"].append(_ev(region, label[1].id, "facade_label", label[1].text))
                entries = [x for x in entries if x["evidence"][0]["entity"] != label[1].id]
            if zmap is None:
                entry["note"] = "z range unknown (no level mark or ground line on the elevation): whole height"
            entries.append(entry)
    windows, doors, positions = 0, 0, []

    def zy(y: float) -> float:
        """Building z of a drawing y (metres above the drawing's ground without a level mark or ground line)."""
        if zmap is not None:
            return round((y - zmap["y_ref"]) * mpu + zmap["z_ref"], 3) + 0.0
        return round((y - region.geometry_box[1]) * mpu, 3) + 0.0

    if mpu:
        # The drawing y of the ground floor's level (building z 0) when the z mapping is known: a terrain hatch or a
        # foundation drawn below the ground line never moves it.
        ground = zmap["y_ref"] - zmap["z_ref"] / mpu if zmap is not None else region.geometry_box[1]
        # The facade's left end (seen from outside, as drawn): the widest closed outline standing on the ground (the
        # wall outline; the roof's eaves reach further out but start above the ground).
        g_tol = 0.05 / mpu
        outlines = [st.bbox() for e in region.ents for st in e.strokes if st.closed and len(st.pts) >= 4]
        standing = [b for b in outlines if abs(b[1] - ground) <= g_tol] or outlines
        widest = max(standing, key=lambda b: b[2] - b[0], default=None)
        x_left = widest[0] if widest is not None else region.geometry_box[0]
        for e in region.ents:
            for st in e.strokes:
                if not st.closed or len(st.pts) != 4:
                    continue
                b = st.bbox()
                w, h = (b[2] - b[0]) * mpu, (b[3] - b[1]) * mpu
                at_ground = (b[1] - ground) * mpu <= 0.3
                kind = None
                if at_ground and DOOR_M[0][0] <= w <= DOOR_M[0][1] and DOOR_M[1][0] <= h <= DOOR_M[1][1]:
                    doors += 1
                    kind = "door"
                elif not at_ground and WINDOW_M[0][0] <= w <= WINDOW_M[0][1] and WINDOW_M[1][0] <= h <= WINDOW_M[1][1]:
                    windows += 1
                    kind = "window"
                if kind:
                    # x: the centre from the facade's left end; sill and head in building z.
                    positions.append({"kind": kind, "x": round(((b[0] + b[2]) / 2.0 - x_left) * mpu, 3) + 0.0,
                                      "x_left": round((b[0] - x_left) * mpu, 3) + 0.0, "width": round(w, 3),
                                      "sill": zy(b[1]), "head": zy(b[3]), "entity": e.id})
    seen = {"region": region.id, "side": side, "view_bearing_deg": view_bearing_deg(side, north_deg),
            "windows": windows, "doors": doors, "positions_m": sorted(positions, key=lambda p: (p["x"], p["sill"])),
            "plan_check": None}
    if region.title:
        seen["title"] = region.title["text"]
    return entries, seen


def _label_by_leader(region, box, segs) -> Optional[tuple[str, object]]:
    """A material label whose leader (a straight line starting next to the label) ends inside ``box``."""
    for t in region.texts:
        folded = T.fold(t.text)
        slug = next((s for s, pattern in MATERIAL_WORDS if re.search(pattern, folded)), None)
        if slug is None:
            continue
        reach = 1.5 * max(t.height, 1e-9)
        for a, b, _ in segs:
            for near, far in ((a, b), (b, a)):
                if _point_box_gap(near, t.box) <= reach and box[0] <= far[0] <= box[2] and box[1] <= far[1] <= box[3]:
                    return slug, t
    return None


def _point_box_gap(p, box) -> float:
    dx = max(box[0] - p[0], 0.0, p[0] - box[2])
    dy = max(box[1] - p[1], 0.0, p[1] - box[3])
    return math.hypot(dx, dy)


def covering_of(regions: list) -> Optional[dict]:
    """The roof covering named by a label on an elevation or roof plan (``KİREMİT`` -> ``clay_tiles``), or None."""
    for r in regions:
        for t in r.texts:
            folded = T.fold(t.text)
            for slug, pattern in COVERING_WORDS:
                if re.search(pattern, folded):
                    return {"covering": slug, "source": "elevation" if r.cls == "elevation" else "roof_plan",
                            "evidence": [_ev(r, t.id, "roof_covering_label", t.text)]}
    return None


def _label_in(region, box) -> Optional[tuple[str, object]]:
    """A material label inside a hatch's box: (slug, text)."""
    for t in region.texts:
        if box[0] <= t.point[0] <= box[2] and box[1] <= t.point[1] <= box[3]:
            folded = T.fold(t.text)
            for slug, pattern in MATERIAL_WORDS:
                if re.search(pattern, folded):
                    return slug, t
    return None


SITE_TARGET = {"paving": "paving", "garden": "grass", "parking": "parking", "pool": "pools", "terrace": "paving"}


LABEL_REACH_M = 1.5                  # 11 Oct 2026 (real04): a label's estimated box may lie just outside its tilted area
LABEL_MIN_AREA_M2 = {"pool": 4.0, "parking": 10.0, "paving": 2.0, "terrace": 2.0, "garden": 4.0}
LABEL_MAX_AREA_M2 = {"pool": 150.0, "parking": 1500.0, "paving": 400.0, "terrace": 200.0, "garden": 3000.0}
LABEL_AREA_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*M2\b")


def label_holder(t, closed: list, kind: str, mpu: float):
    """``(entity, points)`` of the closed outline a site label names (source units), or ``(None, None)``: the outlines
    that hold the label's point or lie within ``LABEL_REACH_M`` of it (the label's box is estimated without its
    rotation), at least ``LABEL_MIN_AREA_M2`` of its kind; an area written in the label (``24M2 HAVUZ``) picks the
    outline whose area is nearest to it (within 25 %); else the smallest outline that holds the point and is no
    larger than ``LABEL_MAX_AREA_M2`` of its kind (the building setback line around several areas never takes a
    label from its own area); else the smallest near one."""
    pt = Point(t.point)
    reach = LABEL_REACH_M / mpu
    cands = [(a * mpu * mpu, e, p) for a, e, p in closed
             if a * mpu * mpu >= LABEL_MIN_AREA_M2.get(kind, 1.0) and Polygon(p).distance(pt) <= reach]
    if not cands:
        return None, None
    m = LABEL_AREA_RE.search(T.fold(t.text))
    if m:
        want = float(m.group(1).replace(",", "."))
        near = [c for c in cands if abs(c[0] - want) <= 0.25 * want]
        if near:
            _, e, p = min(near, key=lambda c: (abs(c[0] - want), Polygon(c[2]).distance(pt)))
            return e, p
    inside = [c for c in cands if c[0] <= LABEL_MAX_AREA_M2.get(kind, 2000.0) and Polygon(c[2]).contains(pt)]
    _, e, p = min(inside or cands, key=lambda c: (c[0], Polygon(c[2]).distance(pt)))
    return e, p


def site_of(region, warnings: list) -> Optional[dict]:
    """Site evidence in building metres (the region must be registered, ``register.register_site``): the plot (the
    largest closed outline), the closed outlines holding a parking / garden / paving label, the trees (circles) and
    every site label. Unregistered: the labels only, without positions (listed)."""
    mpu = region.metres_per_unit
    if not mpu:
        return None
    out = {"region": region.id, "registered": region.transform_to_building is not None, "plot": None,
           "plot_walls": [], "paving": [], "grass": [], "parking": [], "pools": [], "trees": [], "hedges": [],
           "labels": [], "evidence": []}
    tf = region.transform_to_building
    building = set((region.registration or {}).get("outline_entities") or [])
    closed = [(Polygon(p).area, e, p) for e in region.ents for p in [_closed_pts(e)] if p and len(p) >= 3
              and Polygon(p).is_valid and e.id not in building]
    labels = []
    for t in region.texts:
        kind = area_kind(t.text)
        if kind:
            labels.append((kind, t))
            out["labels"].append({"label": t.text, "kind": kind,
                                  "point": list(_apply(tf, t.point)) if tf else None,
                                  "evidence": [_ev(region, t.id, "site_label", t.text)]})
    if tf is None:
        warnings.append(f"site plan {region.id}: not registered onto the building (no outline of the building's size "
                        f"found): its plot, areas and trees are not used; labels listed")
        out["note"] = "not registered: no positions"
        return out
    # Milestone 12 (docs/milestone12.md §3.1, track L): the site plan's level marks (spot heights, KOT), placed in
    # building metres; the pipeline's level step reads them (wenart.ingest.generic.levels).
    from wenart.levels import marks as LM
    # 11 Oct 2026 (real04): a mark attribute's bare value (BDK 44.00) is a mark too; on a site plan it is a spot height
    # of the ground (``site_ground``), whatever its tag says.
    out["marks"] = [{"text": t.text, "point": list(_apply(tf, t.point)), "entity": t.id, "site_ground": True,
                     "attrib_tag": (t.evidence or {}).get("attrib_tag"),
                     "evidence": [_ev(region, t.id, "level_mark", t.text)]}
                    for t in region.texts
                    if LM.read_mark(t.text, bare=LM.is_mark_tag((t.evidence or {}).get("attrib_tag"))) is not None]
    if closed:
        area, e, pts = max(closed, key=lambda c: c[0])
        out["plot"] = [list(_apply(tf, p)) for p in pts]
        out["evidence"].append(_ev(region, e.id, "site_plot"))
        closed = [c for c in closed if c[1] is not e]
    for kind, t in labels:
        target = SITE_TARGET.get(kind)
        if target is None:
            continue
        e, pts = label_holder(t, closed, kind, mpu)
        if e is None:
            continue
        out[target].append({"polygon": [list(_apply(tf, p)) for p in pts], "label": t.text,
                            "evidence": [_ev(region, e.id, f"site_{target}"), _ev(region, t.id, "site_label", t.text)]})
    for e in region.ents:
        block = T.fold(e.block or "")
        if block and NORTH_BLOCK_RE.search(block):
            continue
        circles = [st for st in e.strokes if st.kind == "circle" and st.arc is not None]
        if not circles:
            continue
        # A tree: a block or a layer that names one (AĞAÇ, TREE, BAUM, ARBRE). Any other lone circle (a north arrow's
        # ring, a manhole, a round column) is listed, never built as a tree.
        if not (TREE_BLOCK_RE.search(block) or TREE_BLOCK_RE.search(T.fold(e.layer or ""))):
            if not e.block and len(e.strokes) == 1:
                warnings.append(f"site plan {region.id}: circle {e.id} on layer {e.layer!r} is not read as a tree "
                                f"(neither its layer nor a block names one)")
            continue
        crown = max(circles, key=lambda st: st.arc["radius"])            # the crown; a trunk circle inside is not
        (cx, cy), r = crown.arc["center"], crown.arc["radius"]
        ev = dict(_ev(region, e.id, "site_tree"), layer=e.layer)
        out["trees"].append({"points": [list(_apply(tf, (cx, cy)))], "radius_m": round(r * mpu, 3), "evidence": [ev]})
    # Milestone 13 (T6): rows of equal small symbols are hedges; their symbols are no longer single trees.
    out["hedges"], out["trees"] = hedge_records(out["trees"], region.id)
    for h in out["hedges"]:
        warnings.append(f"site plan {region.id}: {h['symbol_count']} tree symbols in a row ({h['length_m']:.1f} m): "
                        f"read as the hedge {h['id']} ({h['height_class']}, {h['height_m']:.1f} m assumed), not as trees")
    if out["plot"]:
        out["plot_walls"] = _plot_walls(region, closed, tf, mpu)
    return out


def _plot_walls(region, closed: list, tf: list, mpu: float) -> list:
    """Two closed rings inside the plot, one inside the other at a constant 0.05-0.6 m: a plot wall; its centre
    line's edges are the walls (building metres)."""
    rings = sorted(((a, e, p) for a, e, p in closed), key=lambda c: -c[0])
    out = []
    used = set()
    for i, (area_o, e_o, p_o) in enumerate(rings):
        if e_o.id in used:
            continue
        po = Polygon(p_o)
        for area_i, e_i, p_i in rings[i + 1:]:
            if e_i.id in used:
                continue
            pi = Polygon(p_i)
            if not po.contains(pi):
                continue
            bo, bi = po.bounds, pi.bounds
            gaps = [(bi[0] - bo[0]) * mpu, (bi[1] - bo[1]) * mpu, (bo[2] - bi[2]) * mpu, (bo[3] - bi[3]) * mpu]
            if max(gaps) - min(gaps) > 0.01 or not (PLOT_WALL_M[0] <= min(gaps) <= PLOT_WALL_M[1]):
                continue
            t = sum(gaps) / 4.0
            mid = po.buffer(-t / 2.0 / mpu, join_style="mitre")
            if mid.is_empty or mid.geom_type != "Polygon":
                continue
            pts = [_apply(tf, p) for p in list(mid.exterior.coords)[:-1]]
            ev = [_ev(region, e_o.id, "site_plot_wall"), _ev(region, e_i.id, "site_plot_wall")]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                out.append({"start": list(a), "end": list(b), "thickness": round(t, 3), "kind": "plot",
                            "evidence": ev})
            used |= {e_o.id, e_i.id}
            break
    return out


def north_of(region) -> Optional[dict]:
    """North from an ``N`` / ``K`` text next to an arrow: the bearing of the drawing's +Y axis. The arrow is the
    entity nearest to the letter; its tip is its farthest non-circle point from its centre on the letter's side (the
    way it points); without such a point the direction from the arrow's centre to the letter is used."""
    for t in region.texts:
        if T.fold(t.text) not in ("N", "K", "KUZEY", "NORTH", "NORD"):
            continue
        h = max(t.height, 1e-9)
        near = [e for e in region.ents if math.dist(e.centre, t.point) <= 8 * h and e.dim is None]
        if not near:
            continue
        arrow = min(near, key=lambda e: math.dist(e.centre, t.point))
        cx, cy = arrow.centre
        tx, ty = t.point[0] - cx, t.point[1] - cy
        if math.hypot(tx, ty) <= 0.5 * h:
            continue
        tips = [p for st in arrow.strokes if st.kind not in ("circle", "arc") for p in st.pts
                if (p[0] - cx) * tx + (p[1] - cy) * ty > 0]
        tip = max(tips, key=lambda p: math.dist(p, (cx, cy)), default=None)
        nx, ny = (tip[0] - cx, tip[1] - cy) if tip is not None and math.dist(tip, (cx, cy)) > 0 else (tx, ty)
        bearing = (math.degrees(math.atan2(ny, nx)) - 90.0) % 360.0
        if round(bearing, 1) >= 360.0:
            bearing = 0.0
        return {"value": round(bearing, 1) + 0.0, "method": "vector", "confidence": 0.8,
                "evidence": [_ev(region, arrow.id, "north_arrow", confidence=0.8),
                             _ev(region, t.id, "north_arrow", t.text, 0.8)],
                "note": "north points from the arrow's centre to its tip, next to the N; value = compass bearing of +Y"}
    return None


def ridge_lines(roof: dict, heights: dict, reference_outline) -> list:
    """A gable read from the section: the ridge runs across the cut, at the profile's top (s along the cut axis from
    the outline's min side, building metres), over the roof outline (else the reference outline)."""
    axis = heights.get("cut_axis")
    prof = (heights.get("roof") or {}).get("profile") or []
    if axis is None or len(prof) < 3:
        return []
    s_ridge = max(prof, key=lambda p: p[1])[0]
    if roof.get("outline"):
        xs = [p[0] for p in roof["outline"]]
        ys = [p[1] for p in roof["outline"]]
        b = (min(xs), min(ys), max(xs), max(ys))
    elif reference_outline is not None:
        b = reference_outline.bounds
    else:
        return []
    if axis == "x":
        return [[[s_ridge, round(b[1], 4) + 0.0], [s_ridge, round(b[3], 4) + 0.0]]]
    return [[[round(b[0], 4) + 0.0, s_ridge], [round(b[2], 4) + 0.0, s_ridge]]]


def exterior(top_plan, section, elevations: list, sites: list, reference_outline, conflict: Callable,
             warnings: list, reference=None, heights: Optional[dict] = None, plans: Optional[list] = None,
             outlines: Optional[dict] = None, roof_plans: Optional[list] = None) -> dict:
    """The ``exterior`` block. ``reference``: the reference plan region (site plans register onto it);
    ``heights``: the ``heights`` block (datum, ground, cut axis, roof profile); ``plans`` / ``outlines``: the read
    plans and their outlines in building metres (11 Oct 2026: every copy of the building on a site plan,
    ``buildings.site_buildings``)."""
    heights = heights or {}
    out = {"roof": None, "facade": [], "openings_seen": [], "site": None, "north": None, "balconies": [],
           "chimneys": []}
    plan_roof = roof_from_plan(top_plan, warnings, section)
    sec_type = roof_from_section(section)
    if plan_roof is not None and plan_roof["type"] == "mansard" and sec_type is not None and sec_type[0] == "gable":
        # The section shows one slope per side: the closed line inside the roof outline is no slope break (an outer
        # wall face, a room outline). The section wins; the line is listed.
        line = next((e["entity"] for e in plan_roof["evidence"] if e.get("rule") == "roof_break_line"), None)
        conflict("other", [top_plan.id, section.region.id],
                 f"roof type: the closed line {line} inside the roof outline on {top_plan.id} reads as a mansard "
                 f"break line, the section {section.region.id} shows one slope per side (gable)",
                 "the section wins: gable; the closed line is not used as a break line")
        plan_roof = dict(plan_roof, type=None, break_line=None,
                         evidence=[e for e in plan_roof["evidence"] if e.get("rule") != "roof_break_line"])
    roof = None
    hip = roof_from_roof_plan(roof_plans or []) if not (plan_roof is not None and plan_roof["type"]) else None
    if hip is not None:
        ev = hip["evidence"][0]
        roof = {"type": "hip", "type_source": "roof_plan", "outline": plan_roof["outline"] if plan_roof else None,
                "break_line": None, "ridge_lines": [], "covering": None,
                "evidence": hip["evidence"] + (plan_roof["evidence"] if plan_roof else []), "note": hip["note"],
                "pitches_deg": [{"value": round(hip["pitch_deg"], 1), "method": "derived", "confidence": 0.9,
                                 "evidence": [ev], "note": f"atan({hip['slope_pct']:g} %)"}]}
        if sec_type is not None and sec_type[0] != "gable":
            warnings.append(f"roof: the roof plan {ev['region_id']} gives a hip roof at {hip['slope_pct']:g} %; the "
                            f"section's profile reads as {sec_type[0]} (its outline also draws trusses and trims): "
                            f"the roof plan wins")
    elif plan_roof is not None and plan_roof["type"]:
        roof = {"type": plan_roof["type"], "type_source": "plan_roof_lines", "outline": plan_roof["outline"],
                "break_line": plan_roof["break_line"], "ridge_lines": [], "covering": None,
                "evidence": plan_roof["evidence"], "note": plan_roof["note"]}
        if section is not None and section.profile:
            roof["evidence"] += [_ev(section.region, i, "roof_line") for i in section.profile_ids]
    elif sec_type is not None:
        kind, assumed = sec_type
        roof = {"type": kind, "type_source": "section", "outline": plan_roof["outline"] if plan_roof else None,
                "break_line": None, "ridge_lines": [], "covering": None,
                "evidence": [_ev(section.region, i, "roof_line") for i in section.profile_ids]
                + (plan_roof["evidence"] if plan_roof else []), "assumed": assumed}
    if roof is not None and roof["type"] == "gable" and roof["type_source"] == "section":
        ends = [(r, e) for r in elevations for e in [gable_end(r)] if e is not None]
        if ends:
            # An elevation draws a gable end (a wall outline peaking in the middle): the choice is drawn.
            roof["assumed"] = [a for a in roof.get("assumed") or [] if not a.startswith("hip/gable")]
            roof["also_seen_in"] = ["elevation"]
            roof["evidence"] = roof["evidence"] + [_ev(r, e, "gable_end") for r, e in ends[:1]]
        roof["ridge_lines"] = ridge_lines(roof, heights, reference_outline)
        if not roof["ridge_lines"]:
            roof.setdefault("assumed", []).append("ridge direction (the section's cut direction is unknown)")
        if roof["ridge_lines"]:
            roof.setdefault("assumed", []).append("the ridge runs across the cut (a gable read from one section)")
    if roof is not None:
        cover = covering_of(elevations)                 # only a drawn covering (§1.6b rows 12, 13)
        if cover is not None:
            roof["covering"], roof["covering_source"] = cover["covering"], cover["source"]
            roof["evidence"] = roof["evidence"] + cover["evidence"]
    if roof is not None and roof_plans:
        # 27 Oct 2026: the roofs the roof plan draws (``roof_plan_outline``), in the roof plan's own metres; the
        # building registers them on the top level's walls (``to_building.roof_outline_record``)
        first = (hip or {}).get("evidence", [{}])[0].get("region_id") if hip else None
        ordered = sorted(roof_plans, key=lambda r: r.id != first)
        reasons = []
        for r in ordered:
            rec, why = roof_plan_outline(r)
            if rec is not None:
                roof["plan_outline"] = rec
                break
            reasons.append(why)
        if roof.get("plan_outline") is None:
            roof["plan_outline"] = None
            roof["plan_outline_note"] = "; ".join(reasons)
            warnings.append(f"roof: the outline of the roof plan is not read: {'; '.join(reasons)}")
    out["roof"] = roof

    # Site plans (registered onto the reference through the building's outline) and the north.
    # The site plan with the most evidence first (11 Oct 2026, real04: four drawings of the plot; one has the marks).
    sites = sorted(sites, key=lambda r: -(len(r.texts) + len(r.ents)))
    for r in sites:
        copies = None
        if reference is not None and reference_outline is not None and r.metres_per_unit:
            from wenart.sheets import buildings as BLD
            w_one, w_copies = [], []
            one = RG.register_site(r, reference, reference_outline, w_one)
            reg_one = (r.transform_to_building, r.registration)
            copies = BLD.site_buildings(r, plans or [reference], outlines or {reference.id: reference_outline},
                                        w_copies)
            if copies is None or (len(copies) < 2 and one):
                r.transform_to_building, r.registration = reg_one     # one building: the outline fit stays
                copies = None
                warnings.extend(w_one)
            else:
                warnings.extend(w_copies)
        site = site_of(r, warnings)
        if site is not None and copies:
            from wenart.sheets import buildings as BLD
            site["buildings"] = copies
            site["datum"] = BLD.site_datum(copies, heights)
            if len(copies) > 1:
                warnings.append(f"site plan {r.id}: {len(copies)} buildings on the plot ("
                                + ", ".join(f"{c['id']}: turned {c['rotation_deg']:.1f} deg, dz {c['dz']:+.2f} m"
                                            for c in copies) + ")")
        if site is not None and out["site"] is None:
            out["site"] = site
        north = north_of(r)
        if north is None or out["north"] is not None:
            continue
        reg = r.registration or {}
        if r.transform_to_building is None:
            warnings.append(f"site plan {r.id}: north arrow drawn but the site plan is not registered: north unknown")
            continue
        rot = float(reg.get("rotation_deg") or 0.0)
        north["value"] = round((north["value"] + rot) % 360.0, 1) + 0.0
        north["note"] = (f"north points from the arrow's centre to its N; value = compass bearing of the building's +Y "
                         f"(the site plan turned {rot:.0f} deg onto the building)")
        out["north"] = north

    # Elevations: z in building z (level mark or ground line), the viewer's direction from the side and the north.
    datum = (heights.get("datum") or {}).get("value")
    grounds = [g["z"]["value"] for g in heights.get("ground") or [] if g["z"].get("value") is not None]
    ground_z = sum(grounds) / len(grounds) if grounds else None
    north_deg = (out["north"] or {}).get("value")
    for r in elevations:
        zmap = elevation_z(r, datum, ground_z)
        if zmap is not None and zmap.get("warning"):
            warnings.append(zmap["warning"])
        entries, seen = facade_of(r, zmap, north_deg, warnings)
        out["facade"].extend(entries)
        out["openings_seen"].append(seen)
    return out
