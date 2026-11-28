"""Checks of an outdoor space before it is built (27 Nov 2026, audit fix round 5a, rule R16; 28 Nov 2026, the fix-up's
decision).

What: ``verdict(...)`` says why a labelled outdoor space (``wenart.levels.outdoor.outdoor_spaces``) is not built, or
None, and what about it is a finding; ``clip_upper(...)`` keeps an inferred upper space near the storeys under it;
``unreached(b)`` writes the findings of the spaces no door reaches once every door is read. A space a drawn door lands
on, with a drawn outline or with a label of its own storey is never dropped (ENTRANCES-5, GENERAL-4: real17's
kitchen doors never open into the air); what is wrong with it is a finding on the space (``finding``), logged.

- The rectangle fallback (no drawn outline: a rectangle from the label to the facade, scaled to the stated area, the
  building cut out) off the stated area (under ``RECT_AREA_SHARE[0]`` or over ``RECT_AREA_SHARE[1]`` of it) is built
  as read, with a finding (real17's corner balcony: 2.09 m² against a stated 3.78).
- An upper-plan label is the space below seen from above, not built again, only when it is no drawn outline, no door
  of its storey lands on it and its own level mark (printed with the label, outside the storey's outline) is a lower
  storey's floor (real15's 'TERAS +0.50' printed on the first-floor plan over the ground-floor terrace): then the label
  is the lower storey's, and the refusal is written to ``site.outdoor_spaces_refused`` (by its area id: a re-run of the
  levels model, the agent's level edits, gives the same verdict: ENTRANCES-6, GENERAL-5).
- No door reaches a space (``unreached``, at the end of the reading): a finding, never a drop; a window of an adjoining
  room facing the space with its sill near the floor (``LOW_SILL_M``) is named as its probable door (for the architect's
  typed action; nothing is converted); a stacked space of the same kind on another storey at the same place that a
  door reaches gives it its status (a typical floor's balcony). Only a purely inferred space (no drawn outline, no
  label, no door, no facing window) is not built, as a finding.
- An inferred upper space reaches at most ``UPPER_REACH_M`` beyond the outline of the storeys under it (never a
  basement's: GENERAL-13).

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
TWIN_REACH_M = 0.6              # a space of another storey this close (centres) of the same kind is its stacked twin
UPPER_MIN_M = 0.5               # a storey this far over the ground storey is an upper storey
LOW_SILL_M = 0.60               # a window this near the floor facing a doorless space is its probable door
RULE = "A-R16"


def _shp(poly):
    from shapely.geometry import Polygon
    return Polygon([tuple(map(float, p[:2])) for p in poly]).buffer(0)


def is_rectangle(method) -> bool:
    return str(method or "").startswith("rectangle")


def is_upper(level_id: str, levels: dict, ground_id: Optional[str]) -> bool:
    """A storey over the ground storey (by more than ``UPPER_MIN_M``); a basement never is."""
    lv = levels.get(level_id)
    if lv is None or not isinstance(lv.get("elevation"), (int, float)):
        return False
    return float(lv["elevation"]) > _ground_z(levels, ground_id) + UPPER_MIN_M


def _ground_z(levels: dict, ground_id: Optional[str]) -> float:
    g = levels.get(ground_id) if ground_id else None
    return float(g["elevation"]) if g is not None and isinstance(g.get("elevation"), (int, float)) else 0.0


def lower_levels(level_id: str, levels: dict, ground_id: Optional[str] = None) -> list[dict]:
    """The base storeys under ``level_id``, from the ground storey up (never a basement: GENERAL-13)."""
    lv = levels.get(level_id)
    if lv is None or not isinstance(lv.get("elevation"), (int, float)):
        return []
    z, gz = float(lv["elevation"]), _ground_z(levels, ground_id)
    return [x for x in levels.values() if isinstance(x.get("elevation"), (int, float))
            and gz - UPPER_MIN_M <= float(x["elevation"]) < z - UPPER_MIN_M and not x.get("base_level_id")]


DOOR_NEAR_M = 0.6               # a door or doorless opening this close to a space's outline opens onto it


def doors_near(building: dict, level_id: str, polygon) -> list[str]:
    """The doors and doorless openings of the level whose centre lies within ``DOOR_NEAR_M`` of the space's outline
    (pure): a door the levels model's landing probe missed (an inferred rectangle off its facade) still opens onto it."""
    from shapely.geometry import Point

    sp = _shp(polygon)
    return [o["id"] for o in building.get("openings") or [] if o.get("level_id") == level_id and o.get("center")
            and not o.get("virtual") and o.get("type") in ("door", "opening")
            and sp.distance(Point(float(o["center"][0]), float(o["center"][1]))) <= DOOR_NEAR_M]


def landing_doors(building: dict, area: dict, level_id: str, polygon, on_ids, site_areas) -> list[str]:
    """The drawn doors (``type`` door) of the level that land on a space while the levels model builds it: the doors
    its landing probe found (``on_ids``) and those within ``DOOR_NEAR_M`` of its outline (``doors_near``), less the
    doors that land on another space's drawn outline (a balcony's door beside a large inferred rectangle; pure)."""
    from shapely.geometry import Point

    ops = {o.get("id"): o for o in building.get("openings") or []}
    ids = [i for i in dict.fromkeys(list(on_ids or []) + doors_near(building, level_id, polygon))
           if (ops.get(i) or {}).get("type") == "door" and (ops.get(i) or {}).get("center")]
    others = []
    for x in site_areas or []:
        if x is area or not isinstance(x, dict) or x.get("level_id") not in (None, level_id):
            continue
        poly = x.get("polygon") if len(x.get("polygon") or []) >= 3 else (x.get("outline_inferred") or {}).get("polygon")
        if poly and len(poly) >= 3:
            others.append(_shp(poly))
    return [i for i in ids if not any(q.distance(Point(float(ops[i]["center"][0]), float(ops[i]["center"][1])))
                                      <= DOOR_NEAR_M for q in others)]


def facing_window(building: dict, level_id: str, polygon) -> Optional[dict]:
    """A window of the level within ``DOOR_NEAR_M`` of the space's outline whose sill is near the floor
    (``LOW_SILL_M``, a French window included): the space's probable door (pure)."""
    from shapely.geometry import Point

    sp = _shp(polygon)
    best = None
    for o in building.get("openings") or []:
        if o.get("level_id") != level_id or o.get("type") != "window" or not o.get("center") or o.get("virtual"):
            continue
        sill = o.get("sill_height")
        if sill is not None and float(sill) > LOW_SILL_M:
            continue
        d = sp.distance(Point(float(o["center"][0]), float(o["center"][1])))
        if d <= DOOR_NEAR_M and (best is None or d < best[0]):
            best = (d, o)
    return best[1] if best else None


def own_mark(anchor, level_id: str, marks, outline=None) -> Optional[dict]:
    """The level mark printed with the label (within ``MARK_REACH_M`` of its anchor, on its level, outside the storey's
    ``outline`` when one is given: ENTRANCES-5)."""
    from shapely.geometry import Point

    inner = _shp(outline).buffer(-0.05) if outline is not None and len(outline) >= 3 else None
    best = None
    for m in marks or []:
        if m.get("level_id") not in (None, level_id) or not m.get("point") or m.get("z") is None:
            continue
        if inner is not None and inner.contains(Point(float(m["point"][0]), float(m["point"][1]))):
            continue
        d = math.dist(tuple(map(float, m["point"][:2])), tuple(map(float, anchor[:2])))
        if d <= MARK_REACH_M and (best is None or d < best[0]):
            best = (d, m)
    return best[1] if best else None


def verdict(area: dict, kind: str, level_id: str, levels: dict, ground_id: Optional[str], method, polygon,
            stated_m2: Optional[float], doors_onto: Optional[list], site_areas: list, marks: list,
            space_kind=None, outline=None) -> tuple[Optional[str], Optional[str]]:
    """``(refusal, finding)`` of a space (module docstring; pure). ``polygon``: its outline after the building is cut
    out; ``doors_onto``: the doors of its level that land on it (None: not known yet, as none); ``outline``: its
    storey's wall outline."""
    sp = _shp(polygon)
    finding = None
    if is_rectangle(method) and stated_m2:
        share = sp.area / float(stated_m2)
        if not RECT_AREA_SHARE[0] <= share <= RECT_AREA_SHARE[1]:
            finding = (f"its rectangle fallback is {sp.area:.2f} m² against the stated {float(stated_m2):.2f} m² "
                       f"({share:.0%}, outside {RECT_AREA_SHARE[0]:.0%}-{RECT_AREA_SHARE[1]:.0%}): built as read, the "
                       f"drawn outline to review")
    if doors_onto or not is_rectangle(method) or level_id == ground_id or not is_upper(level_id, levels, ground_id):
        return None, finding            # a door lands on it, or a drawn outline: never dropped
    lower = lower_levels(level_id, levels, ground_id)
    anchor = area.get("anchor")
    m = own_mark(anchor, level_id, marks, outline) if anchor and lower else None
    if m is not None:
        z = float(m["z"])
        own = levels.get(level_id) or {}
        if abs(z - float(own.get("elevation") or 0.0)) > UPPER_MIN_M:
            under = next((x for x in lower if abs(z - float(x["elevation"])) <= MARK_TOL_M), None)
            if under is not None:
                return (f"its own level mark {m.get('raw') or m.get('id')} (outside the storey) is the floor of "
                        f"{under['id']} and no door of {level_id} lands on it: the space of {under['id']} seen from "
                        f"above, not built again on {level_id}"), finding
    return None, finding


def refuse(area: dict, kind: str, level_id: str, levels: dict, ground_id: Optional[str], method, polygon,
           stated_m2: Optional[float], doors_onto: Optional[list], site_areas: list, marks: list,
           space_kind=None, outline=None) -> Optional[str]:
    """The refusal of ``verdict`` (the space is not built), or None (pure)."""
    return verdict(area, kind, level_id, levels, ground_id, method, polygon, stated_m2, doors_onto, site_areas, marks,
                   space_kind, outline)[0]


def record_refusal(building: dict, area: dict, level_id: str, polygon, method, reason: str) -> None:
    """A refusal of the levels model's hook on ``site.outdoor_spaces_refused``, once per area (a re-run replaces it)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else None
    if site is None:
        return
    rec = {"area_id": area.get("id"), "label": area.get("label"), "level_id": level_id, "polygon": polygon,
           "method": method, "refused": {"rule": RULE, "reason": reason}}
    site["outdoor_spaces_refused"] = [x for x in site.get("outdoor_spaces_refused") or []
                                      if not (isinstance(x, dict) and x.get("area_id") == area.get("id")
                                              and x.get("area_id") is not None)] + [rec]


def clip_upper(polygon, level_id: str, levels: dict, outlines: dict, ground_id: Optional[str] = None):
    """An inferred upper space cut to ``UPPER_REACH_M`` beyond the storeys under it (the ground storey up, never a
    basement's outline): ``(polygon, reason or None)``."""
    from shapely.ops import unary_union

    if not is_upper(level_id, levels, ground_id):
        return polygon, None
    lower = lower_levels(level_id, levels, ground_id)
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
    """The end of the reading (``completion``, after the size tags and the core rules made the last doors): every
    outdoor space no door or doorless opening of its storey reaches (its door list, else ``doors_near``) gets a finding
    (``finding`` on the space, a record, a warning): its stacked twin's status when a same-kind space of another storey
    at the same place is reached, else 'no door reaches it' with the facing low-sill window named as its probable door.
    Only a purely inferred space (no drawn outline, no label, no door, no facing window) leaves
    ``site.outdoor_spaces`` for ``site.outdoor_spaces_refused``. Returns the records."""
    site = b.get("site") if isinstance(b.get("site"), dict) else None
    if not site or not site.get("outdoor_spaces"):
        return []
    levels = {lv["id"]: lv for lv in b.get("levels") or [] if not lv.get("base_level_id")}
    reached = {}
    for s in site["outdoor_spaces"]:
        if len(s.get("polygon") or []) >= 3 and s.get("level_id") in levels:
            reached[s.get("id")] = list(s.get("doors") or []) or doors_near(b, s["level_id"], s["polygon"])
    out, keep = [], []
    for s in site["outdoor_spaces"]:
        if s.get("id") not in reached or reached[s["id"]]:
            keep.append(s)
            continue
        c = _shp(s["polygon"]).centroid
        twin = next((x for x in site["outdoor_spaces"] if x is not s and x.get("id") in reached
                     and reached[x["id"]] and x.get("kind") == s.get("kind") and x.get("level_id") != s.get("level_id")
                     and _shp(x["polygon"]).centroid.distance(c) <= TWIN_REACH_M), None)
        win = facing_window(b, s["level_id"], s["polygon"])
        if twin is not None:
            why = (f"no door of {s['level_id']} is read onto it; its stacked twin {twin['id']} on {twin['level_id']} is "
                   f"reached by {', '.join(reached[twin['id']][:2])}: the same space of a typical floor, kept"
                   + (f"; the window {win['id']} (sill {float(win.get('sill_height') or 0):.2f} m) faces it: its "
                      f"probable door" if win else ""))
        else:
            why = (f"no door or opening of {s['level_id']} reaches it"
                   + (f"; the window {win['id']} of the adjoining room (sill {float(win.get('sill_height') or 0):.2f} "
                      f"m) faces it: its probable balcony door (for the architect's typed action)" if win else ""))
        purely = is_rectangle(s.get("method")) and not str(s.get("label") or "").strip() and win is None \
            and twin is None
        rec = {"space": s.get("id"), "level_id": s.get("level_id"), "reason": why, "rule": RULE}
        if win is not None:
            rec["probable_door"] = win["id"]
        if twin is not None:
            rec["twin"] = twin["id"]
        if purely:
            from wenart.ingest import rule_guards as RG
            purely = not RG.blocked("outdoor_unreached", b, {"level_id": s.get("level_id"), "space": s.get("id"),
                                                             "why": why})
        if purely:
            rec["refused"] = True
            site.setdefault("outdoor_spaces_refused", []).append(dict(s, refused={"rule": RULE, "reason": why}))
        else:
            s["finding"] = {"rule": RULE, "reason": why, **({"probable_door": win["id"]} if win else {})}
            keep.append(s)
        out.append(rec)
        if warn:
            warn(f"outdoor space {s.get('id')} ({s.get('label')}) on {s.get('level_id')}: {why} "
                 f"({'not built' if purely else 'a finding to review'}, {RULE})")
    site["outdoor_spaces"] = keep
    return out
