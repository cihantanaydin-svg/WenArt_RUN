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

from shapely.geometry import Polygon

from wenart.sheets import register as RG
from wenart.sheets import titles as T

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
AREA_WORDS = [
    ("parking", r"\bOTOPARK\b|\bPARK\b|\bPARKING\b|\bGARAGE\b|\bCARPORT\b|\bSTELLPLATZ\b"),
    ("garden", r"\bBAHCE\b|\bGARDEN\b|\bGARTEN\b|\bJARDIN\b|\bCIM\b|\bLAWN\b|\bYESIL\b"),
    ("paving", r"\bKALDIRIM\b|\bPAVING\b|\bPFLASTER\b|\bTERAS\b|\bTERRACE\b|\bAVLU\b|\bPATIO\b"),
    ("pool", r"\bHAVUZ\b|\bPOOL\b|\bPISCINE\b"),
]
WINDOW_M = ((0.4, 3.0), (0.4, 2.6))
DOOR_M = ((0.7, 3.0), (1.9, 2.8))


def area_kind(label: str) -> Optional[str]:
    """What a site label names: parking, garden, paving, pool (None = not a site word)."""
    folded = T.fold(label)
    for kind, pattern in AREA_WORDS:
        if re.search(pattern, folded):
            return kind
    return None


def side_of(title: Optional[str]) -> str:
    folded = T.fold(title or "")
    for side, pattern in SIDE_WORDS:
        if re.search(pattern, folded):
            return side
    return "unknown"


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


def facade_of(region) -> tuple[list[dict], dict]:
    """(facade entries, openings seen) of one elevation region."""
    side = side_of(region.title["text"] if region.title else None)
    mpu = region.metres_per_unit or 0.0
    entries = []
    for t in region.texts:
        folded = T.fold(t.text)
        for slug, pattern in MATERIAL_WORDS:
            if re.search(pattern, folded):
                entries.append({"region": region.id, "side": side, "z_range": None, "material": slug,
                                "source": "label", "evidence": [_ev(region, t.id, "facade_label", t.text)]})
                break
    for e in region.ents:
        if e.kind == "HATCH" and mpu:
            b = e.box
            entries.append({"region": region.id, "side": side, "z_range": [round(b[1] * mpu, 3), round(b[3] * mpu, 3)],
                            "material": "hatched", "source": "hatch",
                            "evidence": [_ev(region, e.id, "facade_hatch", confidence=0.6)]})
    windows, doors, positions = 0, 0, []
    if mpu:
        ground = region.geometry_box[1]
        x_left = region.geometry_box[0]
        for e in region.ents:
            for st in e.strokes:
                if not st.closed or len(st.pts) != 4:
                    continue
                b = st.bbox()
                w, h = (b[2] - b[0]) * mpu, (b[3] - b[1]) * mpu
                at_ground = (b[1] - ground) * mpu <= 0.3
                if at_ground and DOOR_M[0][0] <= w <= DOOR_M[0][1] and DOOR_M[1][0] <= h <= DOOR_M[1][1]:
                    doors += 1
                    positions.append({"kind": "door", "x": round((b[0] - x_left) * mpu, 3), "sill": 0.0,
                                      "head": round((b[3] - ground) * mpu, 3)})
                elif not at_ground and WINDOW_M[0][0] <= w <= WINDOW_M[0][1] and WINDOW_M[1][0] <= h <= WINDOW_M[1][1]:
                    windows += 1
                    positions.append({"kind": "window", "x": round((b[0] - x_left) * mpu, 3),
                                      "sill": round((b[1] - ground) * mpu, 3), "head": round((b[3] - ground) * mpu, 3)})
    seen = {"region": region.id, "side": side, "windows": windows, "doors": doors,
            "positions_m": sorted(positions, key=lambda p: (p["x"], p["sill"])), "plan_check": None}
    return entries, seen


def site_of(region, warnings: list) -> Optional[dict]:
    mpu = region.metres_per_unit
    if not mpu:
        return None
    closed = [(Polygon(p).area, e, p) for e in region.ents for p in [_closed_pts(e)] if p and len(p) >= 3
              and Polygon(p).is_valid]
    plot = max(closed, key=lambda c: c[0]) if closed else None
    areas = []
    for t in region.texts:
        kind = area_kind(t.text)
        if kind:
            areas.append({"label": t.text, "kind": kind, "point": [round(t.point[0] * mpu, 3),
                                                                   round(t.point[1] * mpu, 3)],
                          "evidence": [_ev(region, t.id, "site_label", t.text)]})
    trees = sum(1 for e in region.ents for st in e.strokes if st.kind == "circle")
    site = {"region": region.id, "registered": False,
            "note": "site-plan metres (origin of the drawing); not registered onto the building frame",
            "plot": [[round(x * mpu, 3), round(y * mpu, 3)] for x, y in plot[2]] if plot else None,
            "plot_entity": plot[1].id if plot else None, "areas": areas, "trees": trees}
    return site


def north_of(region) -> Optional[dict]:
    """North from an ``N`` / ``K`` text next to an arrow: the bearing of the drawing's +Y axis."""
    for t in region.texts:
        if T.fold(t.text) not in ("N", "K", "KUZEY", "NORTH", "NORD"):
            continue
        h = max(t.height, 1e-9)
        near = [e for e in region.ents if math.dist(e.centre, t.point) <= 8 * h and e.dim is None]
        if not near:
            continue
        cx = sum(e.centre[0] for e in near) / len(near)
        cy = sum(e.centre[1] for e in near) / len(near)
        nx, ny = t.point[0] - cx, t.point[1] - cy
        if math.hypot(nx, ny) <= 0.5 * h:
            continue
        bearing = (math.degrees(math.atan2(ny, nx)) - 90.0) % 360.0
        return {"value": round(bearing, 1), "method": "vector", "confidence": 0.8,
                "evidence": [_ev(region, t.id, "north_arrow", t.text, 0.8)],
                "note": "north points from the arrow's centre to its N; value = compass bearing of +Y"}
    return None


def exterior(top_plan, section, elevations: list, sites: list, reference_outline, conflict: Callable,
             warnings: list) -> dict:
    out = {"roof": None, "facade": [], "openings_seen": [], "site": None, "north": None, "balconies": [],
           "chimneys": []}
    plan_roof = roof_from_plan(top_plan, warnings, section)
    sec_type = roof_from_section(section)
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
    if roof is not None and section is not None and section.mpu and section.profile and reference_outline is not None \
            and roof["type"] == "gable":
        roof["ridge_lines"] = []                    # the ridge's plan position needs the cut axis (track E)
    out["roof"] = roof
    for r in elevations:
        entries, seen = facade_of(r)
        out["facade"].extend(entries)
        out["openings_seen"].append(seen)
    for r in sites:
        site = site_of(r, warnings)
        if site is not None and out["site"] is None:
            out["site"] = site
        north = north_of(r)
        if north is not None and out["north"] is None:
            out["north"] = north
    return out
