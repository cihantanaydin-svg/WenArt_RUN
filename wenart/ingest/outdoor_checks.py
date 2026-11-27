"""Checks of an outdoor space before it is built (27 Nov 2026, audit fix round 5a, rule R16).

What: ``refuse(...)`` says why a labelled outdoor space (``wenart.levels.outdoor.outdoor_spaces``) is not built, or
None; ``clip_upper(...)`` keeps an inferred upper space near the storeys under it. The space is then kept as a finding
(its site area records ``space: {built: false, reason, finding: R16}`` and a warning says why), never dropped silently.

- The rectangle fallback (no drawn outline: a rectangle from the label to the facade, scaled to the stated area, the
  building cut out) is checked against the stated area: under ``RECT_AREA_SHARE[0]`` or over ``RECT_AREA_SHARE[1]`` of
  it, it is not the drawn space (real17's corner balcony: 2.09 m² against a stated 3.78).
- An upper-plan label is the space below seen from above when its own level mark is a lower storey's floor (real15's
  'TERAS +0.50' printed on the first-floor plan over the ground-floor terrace), or, with no door of its level onto it
  and no drawn outline, when a space of the same kind lies under it on a lower storey.
- An inferred (rectangle) upper space onto which no door or opening of its level opens is not built (nobody reaches
  it); one that is built reaches at most ``UPPER_REACH_M`` beyond the outline of the storeys under it.

Why: real15's first-floor 'TERAS' label got a 204 m² rectangle cantilevering 5.5 m past the west facade with no door
onto it; real17's corner balcony was built at half its size, leaving a hole in the floor.

How: pure shapely geometry on the building's levels, site areas, level marks and wall outlines.
"""
from __future__ import annotations

import math
from typing import Optional

RECT_AREA_SHARE = (0.8, 1.2)    # a rectangle fallback within this share of the stated area is the space
UPPER_REACH_M = 2.0             # an inferred upper space reaches at most this beyond the storeys under it
MARK_REACH_M = 1.2              # a level mark this close to the label is the label's own
MARK_TOL_M = 0.10               # ... and names a lower storey's floor when it is within this of it
SAME_REACH_M = 3.0              # a same-kind label of a lower storey this close lies under the label
UPPER_MIN_M = 0.5               # a storey this far over the ground storey is an upper storey


def _shp(poly):
    from shapely.geometry import Polygon
    return Polygon([tuple(map(float, p[:2])) for p in poly]).buffer(0)


def is_rectangle(method) -> bool:
    return str(method or "").startswith("rectangle")


def is_upper(level_id: str, levels: dict, ground_id: Optional[str]) -> bool:
    """A storey over the ground storey (by more than ``UPPER_MIN_M``); a basement never is."""
    lv, g = levels.get(level_id), levels.get(ground_id) if ground_id else None
    if lv is None or not isinstance(lv.get("elevation"), (int, float)):
        return False
    gz = float(g["elevation"]) if g is not None and isinstance(g.get("elevation"), (int, float)) else 0.0
    return float(lv["elevation"]) > gz + UPPER_MIN_M


def lower_levels(level_id: str, levels: dict) -> list[dict]:
    lv = levels.get(level_id)
    if lv is None or not isinstance(lv.get("elevation"), (int, float)):
        return []
    z = float(lv["elevation"])
    return [x for x in levels.values() if isinstance(x.get("elevation"), (int, float))
            and float(x["elevation"]) < z - UPPER_MIN_M and not x.get("base_level_id")]


DOOR_NEAR_M = 0.6               # a door or doorless opening this close to a space's outline opens onto it


def doors_near(building: dict, level_id: str, polygon) -> list[str]:
    """The doors and doorless openings of the level whose centre lies within ``DOOR_NEAR_M`` of the space's outline
    (pure): a door the levels model's landing probe missed (an inferred rectangle off its facade) still opens onto it."""
    from shapely.geometry import Point

    sp = _shp(polygon)
    return [o["id"] for o in building.get("openings") or [] if o.get("level_id") == level_id and o.get("center")
            and not o.get("virtual") and o.get("type") in ("door", "opening")
            and sp.distance(Point(float(o["center"][0]), float(o["center"][1]))) <= DOOR_NEAR_M]


def own_mark(anchor, level_id: str, marks) -> Optional[dict]:
    """The level mark printed with the label (within ``MARK_REACH_M`` of its anchor, on its level)."""
    best = None
    for m in marks or []:
        if m.get("level_id") not in (None, level_id) or not m.get("point") or m.get("z") is None:
            continue
        d = math.dist(tuple(map(float, m["point"][:2])), tuple(map(float, anchor[:2])))
        if d <= MARK_REACH_M and (best is None or d < best[0]):
            best = (d, m)
    return best[1] if best else None


def refuse(area: dict, kind: str, level_id: str, levels: dict, ground_id: Optional[str], method, polygon,
           stated_m2: Optional[float], doors_onto: Optional[list], site_areas: list, marks: list,
           space_kind=None) -> Optional[str]:
    """Why the space is not built (module docstring), or None (pure). ``polygon``: its outline after the building is
    cut out; ``doors_onto``: the doors of its level that open onto it, or None while the doors are not all read (the
    levels model runs before the size tags and the core rules make the last doors: then only the area and the mark
    decide, ``unreached`` judges the rest at the end of the reading); ``space_kind(label)``: the outdoor word of a
    label (``levels.outdoor.space_kind``)."""
    sp = _shp(polygon)
    if is_rectangle(method) and stated_m2:
        share = sp.area / float(stated_m2)
        if not RECT_AREA_SHARE[0] <= share <= RECT_AREA_SHARE[1]:
            return (f"its rectangle fallback is {sp.area:.2f} m² against the stated {float(stated_m2):.2f} m² "
                    f"({share:.0%}, outside {RECT_AREA_SHARE[0]:.0%}-{RECT_AREA_SHARE[1]:.0%}): not the drawn space")
    lower = lower_levels(level_id, levels)
    if not lower or level_id == ground_id or not is_upper(level_id, levels, ground_id):
        return None
    anchor = area.get("anchor")
    m = own_mark(anchor, level_id, marks) if anchor else None
    if m is not None:
        z = float(m["z"])
        own = levels.get(level_id) or {}
        if abs(z - float(own.get("elevation") or 0.0)) > UPPER_MIN_M:
            under = next((x for x in lower if abs(z - float(x["elevation"])) <= MARK_TOL_M), None)
            if under is not None:
                return (f"its own level mark {m.get('raw') or m.get('id')} is the floor of {under['id']}: the space of "
                        f"{under['id']} seen from above, not built again on {level_id}")
    if doors_onto is None or doors_onto:
        return None
    if anchor and space_kind is not None and is_rectangle(method):
        from shapely.geometry import Point
        p = Point(float(anchor[0]), float(anchor[1]))
        ids = {x["id"] for x in lower}
        for x in site_areas or []:
            if x is area or not isinstance(x, dict) or (x.get("level_id") or ground_id) not in ids:
                continue
            k = space_kind(x.get("label_raw") or x.get("label"))
            if k is None or k.get("kind") != kind:
                continue
            near = (len(x.get("polygon") or []) >= 3 and _shp(x["polygon"]).buffer(0.5).contains(p)) or (
                x.get("anchor") and math.dist(tuple(map(float, x["anchor"][:2])), (p.x, p.y)) <= SAME_REACH_M)
            if near:
                return (f"no door of {level_id} opens onto it and the {kind} '{x.get('label')}' of "
                        f"{x.get('level_id') or ground_id} lies under its label: that space seen from above")
    if is_rectangle(method):
        return f"no door or opening of {level_id} opens onto its inferred outline (nobody reaches it)"
    return None


def clip_upper(polygon, level_id: str, levels: dict, outlines: dict, ground_id: Optional[str] = None):
    """An inferred upper space cut to ``UPPER_REACH_M`` beyond the storeys under it: ``(polygon, reason or None)``."""
    from shapely.ops import unary_union

    if not is_upper(level_id, levels, ground_id):
        return polygon, None
    lower = lower_levels(level_id, levels)
    rings = [_shp(outlines[x["id"]]) for x in lower if len(outlines.get(x["id"]) or []) >= 3]
    if not rings:
        return polygon, None
    sp = _shp(polygon)
    reach = unary_union(rings).buffer(UPPER_REACH_M, join_style=2)
    if reach.contains(sp):
        return polygon, None
    cut = sp.intersection(reach)
    parts = [g for g in getattr(cut, "geoms", [cut]) if g.geom_type == "Polygon" and g.area > 0.05]
    if not parts:
        return polygon, None
    g = max(parts, key=lambda q: q.area)
    return ([[round(x, 4), round(y, 4)] for x, y in list(g.exterior.coords)[:-1]],
            f"cut to {UPPER_REACH_M:g} m beyond the storeys under it ({sp.area:.2f} -> {g.area:.2f} m²)")


def unreached(b: dict, warn=None) -> list[dict]:
    """The end of the reading (``completion``, after the size tags and the core rules made the last doors): an
    inferred (rectangle) outdoor space of an upper storey that no door or doorless opening of its storey reaches (its
    door list, else ``doors_near``), or that lies over a space of the same kind below with no door, is not built: it
    leaves ``site.outdoor_spaces`` for ``site.outdoor_spaces_refused`` and its site area records why (a finding, never
    a silent drop). Returns the records."""
    from wenart.levels import outdoor as OD

    site = b.get("site") if isinstance(b.get("site"), dict) else None
    if not site or not site.get("outdoor_spaces"):
        return []
    levels = {lv["id"]: lv for lv in b.get("levels") or [] if not lv.get("base_level_id")}
    ground_id = next((lv["id"] for lv in levels.values() if lv.get("order") == 0), None)
    areas = {a["space"].get("id"): a for a in site.get("areas") or [] if isinstance(a, dict)
             and isinstance(a.get("space"), dict) and a["space"].get("built")}
    out, keep = [], []
    for s in site["outdoor_spaces"]:
        why = None
        if is_rectangle(s.get("method")) and s.get("level_id") in levels and len(s.get("polygon") or []) >= 3:
            a = areas.get(s.get("id")) or {"anchor": None}
            doors = list(s.get("doors") or []) or doors_near(b, s["level_id"], s["polygon"])
            why = refuse(a, str(s.get("kind") or ""), s["level_id"], levels, ground_id, s.get("method"), s["polygon"],
                         None, doors, site.get("areas") or [], [], OD.space_kind)
        if why is None:
            keep.append(s)
            continue
        site.setdefault("outdoor_spaces_refused", []).append(dict(s, refused={"rule": "R16", "reason": why}))
        if s.get("id") in areas:
            areas[s["id"]]["space"] = {"built": False, "reason": why, "finding": "R16"}
        out.append({"space": s.get("id"), "level_id": s.get("level_id"), "reason": why})
        if warn:
            warn(f"outdoor space {s.get('id')} ({s.get('label')}) on {s.get('level_id')} not built: {why} (R16; a "
                 f"finding to review)")
    site["outdoor_spaces"] = keep
    return out
