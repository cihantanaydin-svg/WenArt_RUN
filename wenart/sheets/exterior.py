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
  warning). Without plan lines the section's profile decides: one slope per side ``gable`` (the hip/gable choice
  across the section is assumed), two slopes per side ``gambrel``, no slope and a slab on top ``flat``;
- facades: elevation regions (side from their title: GÜNEY / SOUTH / SÜD / SUD = south ...), materials from
  labels (``SIVA``, ``TAŞ KAPLAMA``, ``AHŞAP``, ``TUĞLA``, render, stone, timber, brick) and hatches; window- and
  door-sized rectangles counted per facade (positions along the facade);
- site plans: the plot (the largest closed outline), labelled areas (parking, garden, paving ...), trees (circles) and
  the north arrow (an ``N`` / ``K`` text: north points from the arrow's centre to it; ``north`` = the compass
  bearing of the drawing's +Y).
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
    return list(e.strokes[0].pts)


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

    A level mark wins (``43.00`` with the section's datum 43.00 is z 0; a mark more than 30 m from the datum, or any
    mark without a datum, is read as relative to the ground floor: ``±0.00`` is z 0); else the lowest horizontal
    line spanning half the drawing is the ground (z of the section's ground line, else 0.0 assumed); else None."""
    mpu = region.metres_per_unit
    if not mpu:
        return None
    segs = UC.segments([st for e in region.ents for st in e.strokes])
    for t, value in UC.mark_texts(region.texts):
        mp = UC.mark_point(t, segs)
        if mp is None:
            continue
        absolute = datum is not None and abs(value - datum) <= 30.0
        z_ref = value - datum if absolute else value
        note = (f"level mark {t.text} - datum {datum:.2f}" if absolute else
                f"level mark {t.text} read relative to the ground floor")
        return {"y_ref": mp[1], "z_ref": round(z_ref, 4), "method": "vector",
                "evidence": [_ev(region, t.id, "level_mark", t.text)], "note": note}
    gb = region.geometry_box
    width = gb[2] - gb[0]
    flat = [(min(a[1], b[1]), st) for a, b, st in segs
            if abs(a[1] - b[1]) <= 1e-6 * max(1.0, abs(a[1])) + 1e-9 and abs(b[0] - a[0]) >= 0.5 * width]
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
        ground = zmap["y_ref"] if zmap is not None and zmap["method"] == "derived" else region.geometry_box[1]
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


SITE_TARGET = {"paving": "paving", "garden": "grass", "parking": "parking"}


def site_of(region, warnings: list) -> Optional[dict]:
    """Site evidence in building metres (the region must be registered, ``register.register_site``): the plot (the
    largest closed outline), the closed outlines holding a parking / garden / paving label, the trees (circles) and
    every site label. Unregistered: the labels only, without positions (listed)."""
    mpu = region.metres_per_unit
    if not mpu:
        return None
    out = {"region": region.id, "registered": region.transform_to_building is not None, "plot": None,
           "plot_walls": [], "paving": [], "grass": [], "parking": [], "trees": [], "labels": [], "evidence": []}
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
    if closed:
        area, e, pts = max(closed, key=lambda c: c[0])
        out["plot"] = [list(_apply(tf, p)) for p in pts]
        out["evidence"].append(_ev(region, e.id, "site_plot"))
        closed = [c for c in closed if c[1] is not e]
    for kind, t in labels:
        target = SITE_TARGET.get(kind)
        if target is None:
            continue
        holders = [c for c in closed if Polygon(c[2]).contains(Point(t.point))]
        if not holders:
            continue
        _, e, pts = min(holders, key=lambda c: c[0])
        out[target].append({"polygon": [list(_apply(tf, p)) for p in pts], "label": t.text,
                            "evidence": [_ev(region, e.id, f"site_{target}"), _ev(region, t.id, "site_label", t.text)]})
    for e in region.ents:
        block = T.fold(e.block or "")
        if block and NORTH_BLOCK_RE.search(block):
            continue
        circles = [st for st in e.strokes if st.kind == "circle" and st.arc is not None]
        is_tree = bool(block and TREE_BLOCK_RE.search(block)) or (not e.block and len(e.strokes) == 1 and circles)
        if not is_tree or not circles:
            continue
        crown = max(circles, key=lambda st: st.arc["radius"])            # the crown; a trunk circle inside is not
        (cx, cy), r = crown.arc["center"], crown.arc["radius"]
        out["trees"].append({"points": [list(_apply(tf, (cx, cy)))], "radius_m": round(r * mpu, 3),
                             "evidence": [_ev(region, e.id, "site_tree")]})
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
             warnings: list, reference=None, heights: Optional[dict] = None) -> dict:
    """The ``exterior`` block. ``reference``: the reference plan region (site plans register onto it);
    ``heights``: the ``heights`` block (datum, ground, cut axis, roof profile)."""
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
    if plan_roof is not None and plan_roof["type"]:
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
    out["roof"] = roof

    # Site plans (registered onto the reference through the building's outline) and the north.
    for r in sites:
        if reference is not None and reference_outline is not None and r.metres_per_unit:
            RG.register_site(r, reference, reference_outline, warnings)
        site = site_of(r, warnings)
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
        entries, seen = facade_of(r, zmap, north_deg, warnings)
        out["facade"].extend(entries)
        out["openings_seen"].append(seen)
    return out
