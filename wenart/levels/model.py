"""Levels inferred where the documents are silent (docs/milestone12.md §3.3, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026); every function is pure (returns a new building) and marks what it infers with
``inferred: true`` and evidence method ``inferred``:

- ``infer_levels(building: dict, brief: dict | None = None) -> dict``: room ``floor_offset_m``, door ``threshold_z``,
  ``site.ground.points``, ``site.terrain``, ``site.entrances``, ``site.plinth`` from ``building["level_marks"]`` and
  the rules of §3.3 (D3a: 0.15 m rise when nothing about the ground is drawn).

What ``infer_levels`` does, in order (the marks' kinds, points and building z come from the reading step,
``wenart.levels.read`` via ``wenart.ingest.generic.levels.apply_levels``; an agent edit changes them and runs this
again):

1. **Single drawn ground floor** (user decision of 10 Oct 2026: real03 ground floor only): a building with one base
   level that is a ground floor (no upper-floor title, elevation about 0 or outside doors) and no slabs, roof or
   variants gets the slab under it, a ``flat_cut`` roof (a flat roof slab with a parapet, ``inferred``, note "upper
   floors not drawn") and its site, so ``build.is_whole_building`` is true (``whole_single_level``).
2. **Level floors from marks**: a level whose elevation is assumed takes the most common floor mark inside its rooms
   (``elevation_source: level_mark``).
3. **Room floors**: a room with floor marks inside gets ``floor_offset_m`` (their median minus the level floor) and
   ``floor_evidence``; a mark more than ``room_offset_max`` off (a stair landing) or in a stair or shaft is listed,
   not used; marks in one room that disagree are a conflict. Other rooms: 0 (``floor_source: level``; wet rooms keep
   the level floor, no assumed drop).
4. **Thresholds**: every door and doorless opening on a wall gets ``threshold_z`` (building z): the higher floor of the
   rooms on its two sides (an outside door: its room's floor); a step between two rooms is listed
   (``level_inference.inner_steps``).
5. **Ground** (whole buildings): spot ground marks within ``ground_reach`` of the outline (outliers beyond
   ``ground_outlier`` from the median listed): >= 3 give a ``planar`` or ``tin`` surface (``wenart.levels.terrain``),
   1-2 per-side levels; else a site note (``TESVİYE 0.00 KOTU``) gives one level; else the drawn section ground lines
   stay; else **D3a**: the ground ``ground_rise`` (0.15 m) under the ground floor (assumed, one inferred step).
   ``site.ground.points``, ``site.ground.surface``, ``site.ground.terrain``.
6. **Entrances**: every outside door of a level at the ground: the ground in front (the nearest ground point within
   ``door_ground_reach``, else the terrain, as the build makes it: ``wenart.blender.site.terrain_model`` with the
   basement doors' own terrain), the rise, and the solution: ``none`` (flush, or a basement door whose side the build
   lowers), ``steps`` (n = ceil(rise / riser_max), riser = rise / n, tread, a landing of door width + 0.6 x 1.2 m, an
   intermediate landing every 12 risers, handrails and cheek walls above 0.45 m), a ``ramp`` only when drawn or when
   the brief asks for an accessible entrance (slope table), or ``into_air`` (L2) above ``door_into_air``.
7. **Plinth**: the ``SB.`` mark, else the ground floor; per side its height above the ground (at least
   ``plinth_min``).
8. **Basements**: levels below the ground floor are recorded with their light wells and courts (the build's rule,
   ``wenart.blender.site.light_wells``), written into ``site.ground.light_wells`` (``source: assumed``,
   ``inferred``).

Everything inferred is listed in ``building["level_inference"]`` (``inferred``, ``conflicts``, ``warnings``,
``params``); the pipeline copies the conflicts into the building's conflicts.

Why: the documents rarely say everything about the ground (§1.5); CLAUDE.md asks the AI and the code to infer, mark
and list rather than leave doors flush on the grass or floating.
"""
from __future__ import annotations

import copy
import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.levels import terrain as T

# A copy of the ``levels:`` block of wenart/defaults.yaml and of the brief's ``levels:`` defaults (tests pin it): the
# code runs where PyYAML is missing.
BUILTIN_PARAMS = {
    "ground_rise": 0.15, "accessible_entrance": False,
    "flush_max": 0.05, "riser_max_outdoor": 0.15, "riser_min_outdoor": 0.10, "riser_max_indoor": 0.18, "tread": 0.30,
    "tread_min": 0.28, "step_rule": [0.58, 0.66], "landing_depth": 1.20, "landing_extra_width": 0.60,
    "landing_every_risers": 12, "handrail_from": 0.45, "cheek_wall_from": 0.45,
    "ramp_slopes": [[0.15, 0.0833], [0.50, 0.0714], [1.00, 0.0625], [99.0, 0.05]], "ramp_handrail_from": 0.15,
    "ramp_width": 1.20, "door_into_air": 1.50, "door_ground_reach": 5.0, "door_mark_reach": 1.5, "ground_reach": 25.0,
    "ground_outlier": 3.0, "room_offset_max": 1.0, "plane_residual": 0.10, "terrain_blend": 20.0, "plinth_min": 0.15,
    "mark_tol": 0.02, "parapet": 0.30,
}
GROUND_KINDS = ("ground_natural", "ground_finished", "slope_top")
FLOOR_KINDS = ("floor", "entrance")
NO_FLOOR_ROOMS = ("stair", "shaft")
FLAT_THICKNESS = 0.30                       # the flat_cut roof slab (roof.DEFAULTS["flat_thickness"])
UPPER_WORDS = ("1. KAT", "NORMAL KAT", "FIRST FLOOR", "SECOND FLOOR", "UPPER FLOOR", "TIP KAT", "CATI", "ATTIC",
               "ROOF", "ASMA KAT", "MEZZANINE")


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------

def _default_params() -> dict:
    out = copy.deepcopy(BUILTIN_PARAMS)
    try:
        import yaml
        from wenart.brief import DEFAULTS_PATH

        data = yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8")) or {}
        out.update(copy.deepcopy(data.get("levels") or {}))
        out.update(copy.deepcopy((data.get("brief") or {}).get("levels") or {}))
    except (ImportError, OSError):              # Blender's Python: the built-in copy
        pass
    return out


def _brief_values(brief: Optional[dict]) -> dict:
    from wenart.brief import levels_block

    return levels_block(brief)


def level_params(brief: Optional[dict] = None) -> dict:
    """The level rules (``wenart/defaults.yaml`` ``levels:`` and the brief's ``levels:`` defaults) with the brief's
    ``levels:`` block over them (a ``load_brief`` result or a raw brief). A brief value of the wrong type is not
    used (``_warnings``); ``_from_brief`` lists the keys the brief set."""
    params = _default_params()
    params["_from_brief"], params["_warnings"] = [], []
    for key, given in sorted(_brief_values(brief).items()):
        if key not in params or key.startswith("_"):
            params["_warnings"].append(f"brief levels.{key}: unknown key, not used")
            continue
        want = params[key]
        ok = (isinstance(want, bool) and isinstance(given, bool)) or \
            (isinstance(want, (int, float)) and not isinstance(want, bool) and isinstance(given, (int, float))
             and not isinstance(given, bool) and given >= 0) or \
            (isinstance(want, list) and isinstance(given, list) and len(given) == len(want) or
             (key == "ramp_slopes" and isinstance(given, list) and given))
        if not ok:
            params["_warnings"].append(f"brief levels.{key}: {given!r} is not a {type(want).__name__}; "
                                       f"{want!r} used")
            continue
        params[key] = copy.deepcopy(given)
        params["_from_brief"].append(key)
    return params


def _brief_of(building: dict, brief: Optional[dict]) -> Optional[dict]:
    if brief is not None:
        return brief
    stored = (building.get("project") or {}).get("brief")
    return stored if isinstance(stored, dict) else None


# --------------------------------------------------------------------------
# Small helpers (pure)
# --------------------------------------------------------------------------

def _r(v: float, nd: int = 3) -> float:
    return round(float(v), nd) + 0.0


def base_levels(building: dict) -> list[dict]:
    return sorted((lv for lv in building.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (float(lv.get("elevation") or 0.0), lv["id"]))


def ground_level(building: dict) -> Optional[dict]:
    """The ground floor: the base level of order 0, else the lowest base level at or above -0.5 m, else the lowest."""
    base = base_levels(building)
    if not base:
        return None
    zero = [lv for lv in base if lv.get("order") == 0]
    if zero:
        return zero[0]
    up = [lv for lv in base if float(lv.get("elevation") or 0.0) >= -0.5]
    return up[0] if up else base[0]


def is_whole(building: dict) -> bool:
    """``build.is_whole_building`` (slabs, a roof or variants), without importing the build."""
    return bool(building.get("slabs") or isinstance(building.get("roof"), dict) or building.get("variants"))


def level_outline(building: dict, level_id: str) -> list[tuple[float, float]]:
    from wenart.blender import geom2d

    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level_id]
    outline, _method = geom2d.wall_outline(walls)
    return outline


def outlines_of(building: dict) -> dict[str, list]:
    return {lv["id"]: level_outline(building, lv["id"]) for lv in building.get("levels") or []}


def room_floor_z(building: dict, room: dict) -> float:
    """A room's finished floor (building z): its level's elevation + ``floor_offset_m``."""
    lv = next((x for x in building.get("levels") or [] if x["id"] == room.get("level_id")), None)
    return float((lv or {}).get("elevation") or 0.0) + float(room.get("floor_offset_m") or 0.0)


def _room_at(rooms: Sequence[dict], p) -> Optional[dict]:
    for r in rooms:
        if len(r.get("polygon") or []) >= 3 and G.point_in_polygon(p, r["polygon"]):
            return r
    return None


def _dist_to_polygon(p, polygon) -> float:
    from wenart.blender import geom2d

    return geom2d.distance_to_polygon_edges(p, polygon)


def opening_sides(building: dict, opening: dict, rooms: Sequence[dict], outline) -> Optional[dict]:
    """The two sides of a wall opening: ``{"centre", "normal", "half_t", "rooms": [room | None, room | None],
    "outside": [bool, bool], "wall"}`` (probes half the wall thickness + 0.05 m off the centre line), None when the
    opening has no wall."""
    from wenart.blender.shell import opening_centre_on_wall

    wall = next((w for w in building.get("walls") or [] if w["id"] == opening.get("wall_id")), None)
    if wall is None or G.distance(wall["start"], wall["end"]) < 1e-9:
        return None
    cx, cy, _ = opening_centre_on_wall(opening, wall)
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + 0.05
    out = {"centre": (cx, cy), "normal": (nx, ny), "half_t": float(wall["thickness"]) / 2.0, "rooms": [], "outside": [],
           "wall": wall}
    for s in (1.0, -1.0):
        p = (cx + s * nx * reach, cy + s * ny * reach)
        room = _room_at(rooms, p)
        out["rooms"].append(room)
        out["outside"].append(room is None and len(outline) >= 3 and not G.point_in_polygon(p, outline))
    return out


def _evidence(file: str, rule: str, note: str, confidence: float = 0.5, **extra) -> dict:
    ev = {"file": file or "", "page": None, "layer": None, "entity": None, "method": "inferred",
          "confidence": confidence, "rule": rule, "text": note}
    ev.update(extra)
    return ev


def _file_of(building: dict) -> str:
    for d in building.get("documents") or []:
        if d.get("file"):
            return d["file"]
    for lv in building.get("levels") or []:
        for e in lv.get("evidence") or []:
            if e.get("file"):
                return e["file"]
    return ""


def _median(vals: Sequence[float]) -> float:
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _mark_ev(m: dict) -> list[dict]:
    return [dict(e) for e in m.get("evidence") or []][:2]


def _use(m: dict, what: str) -> None:
    used = m.setdefault("used_for", [])
    if what not in used:
        used.append(what)


# --------------------------------------------------------------------------
# Steps and ramps (pure)
# --------------------------------------------------------------------------

def steps_for(rise: float, width: float, params: dict, outdoor: bool = True) -> Optional[dict]:
    """The flight for ``rise`` (m): ``n = ceil(rise / riser_max)`` risers of ``rise / n``, ``tread`` deep, in flights
    of at most ``landing_every_risers`` (intermediate landings between them); handrails and cheek walls above their
    thresholds. None for a flush rise."""
    if rise <= float(params["flush_max"]):
        return None
    rmax = float(params["riser_max_outdoor" if outdoor else "riser_max_indoor"])
    n = max(1, int(math.ceil(rise / rmax - 1e-9)))
    riser = rise / n
    # tread: the rule's at least, deeper when low risers need it to keep 2 R + T within the step rule
    tread = max(float(params["tread"]), math.ceil((float(params["step_rule"][0]) - 2 * riser) * 100 - 1e-6) / 100.0)
    per = max(1, int(params["landing_every_risers"]))
    flights, left = [], n
    while left > 0:
        k = min(per, left)
        flights.append(k)
        left -= k
    return {"count": n, "riser": _r(riser, 4), "tread": _r(tread), "rule_2r_t": _r(2 * riser + tread, 4),
            "flights": flights, "intermediate_landings": len(flights) - 1,
            "width": _r(width), "handrails": rise > float(params["handrail_from"]),
            "cheek_walls": rise > float(params["cheek_wall_from"]),
            "run": _r((n - len(flights)) * tread + (len(flights) - 1) * float(params["landing_depth"]))}


def ramp_for(rise: float, params: dict) -> Optional[dict]:
    """The ramp for ``rise`` by the slope table (``ramp_slopes``: rise up to -> slope), None for a flush rise."""
    if rise <= float(params["flush_max"]):
        return None
    slope = None
    for limit, s in params["ramp_slopes"]:
        if rise <= float(limit) + 1e-9:
            slope = float(s)
            break
    slope = slope if slope is not None else float(params["ramp_slopes"][-1][1])
    return {"slope": _r(slope, 4), "ratio": f"1:{round(1.0 / slope):d}", "length": _r(rise / slope),
            "width": _r(params["ramp_width"]), "handrails": rise > float(params["ramp_handrail_from"]),
            "along": "facade"}


# --------------------------------------------------------------------------
# Single drawn ground floor (U2)
# --------------------------------------------------------------------------

def is_ground_floor(building: dict, level: dict, outline) -> bool:
    """A level is a ground floor unless its title marks an upper floor or a basement: order 0 or no order with an
    elevation within 0.5 m of 0, or a level with an outside door."""
    from wenart import building as B

    label = B.fold_ascii(str(level.get("label") or "")).upper()
    order = level.get("order")
    if order is not None and order != 0:
        return False
    if any(w in label for w in UPPER_WORDS) or "BODRUM" in label or "BASEMENT" in label:
        return False
    if abs(float(level.get("elevation") or 0.0)) <= 0.5:
        return True
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == level["id"]]
    for o in building.get("openings") or []:
        if o.get("level_id") == level["id"] and o.get("type") == "door":
            sides = opening_sides(building, o, rooms, outline)
            if sides and any(sides["outside"]):
                return True
    return False


def whole_single_level(building: dict, params: dict, brief: Optional[dict], inferred: list) -> bool:
    """Step 1 (mutates ``building``): slabs, a ``flat_cut`` roof and the site of a single drawn ground floor. True
    when it applied."""
    if is_whole(building):
        return False
    base = base_levels(building)
    if len(base) != 1:
        return False
    lv = base[0]
    outline = level_outline(building, lv["id"])
    if len(outline) < 3 or not is_ground_floor(building, lv, outline):
        return False
    file = _file_of(building)
    slab_t, slab_src = 0.20, "assumed_default"
    try:
        from wenart import brief as BR
        values = brief if isinstance(brief, dict) and "values" in brief else {"values": brief or {}}
        v = BR.value(values, "slab_thickness", None)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and 0.05 <= float(v) <= 0.6:
            slab_t = float(v)
    except ImportError:
        pass
    note = ("a single drawn ground floor (user decision of 10 Oct 2026): the building ends at that floor; upper "
            "floors not drawn")
    building["slabs"] = [{
        "id": f"sl_{lv['id']}", "below_level_id": None, "above_level_id": lv["id"], "z_top": float(lv["elevation"]),
        "thickness": _r(slab_t), "thickness_source": slab_src, "outline": [[_r(x, 4), _r(y, 4)] for x, y in outline],
        "openings": [], "variants": [], "status": "assumed", "inferred": True,
        "evidence": [_evidence(file, "outer_wall_outline", f"the slab under {lv['id']}: the outer face of its outer "
                                                           f"walls; thickness from the brief (assumed)")]}]
    building["roof"] = {
        "type": "flat", "kind": "flat_cut", "type_source": "assumed", "over_level_id": lv["id"],
        "eaves_height": None, "ridge_height": None, "pitches_deg": [],
        "overhang": {"value": 0.0, "method": "assumed", "confidence": 0.0, "evidence": [],
                     "note": "flat_cut: the roof ends at the outer wall face"},
        "thickness": {"value": FLAT_THICKNESS, "method": "assumed", "confidence": 0.0, "evidence": [],
                      "note": "flat_cut: a flat roof slab (assumed)"},
        "knee_wall": None, "profile": None, "outline": None, "break_line": None, "ridge_lines": [], "planes": [],
        "openings": [], "covering": None, "covering_colour": None, "covering_source": None,
        "parapet_height": {"value": float(params["parapet"]), "method": "assumed", "confidence": 0.0,
                           "evidence": [], "note": "flat_cut: a low parapet on the outer walls (assumed)"},
        "assumed": [f"upper floors not drawn: a flat roof slab with a {float(params['parapet']):.2f} m parapet over "
                    f"{lv['id']} (flat_cut, inferred)"],
        "status": "assumed", "inferred": True, "note": "upper floors not drawn",
        "evidence": [_evidence(file, "single_level", note)]}
    site = building.get("site") if isinstance(building.get("site"), dict) else \
        {"boundary_walls": [], "areas": [], "decor": [], "openings": []}
    from wenart.sheets import exterior as SE
    from wenart.sheets import to_building as TB
    building["site"] = TB.site_block(site, {}, SE.area_kind, lv["id"])
    inferred.append({"item": "slabs", "value": [s["id"] for s in building["slabs"]], "reason": note})
    inferred.append({"item": "roof", "value": "flat_cut", "reason": note})
    inferred.append({"item": "site", "value": "ground, entrances, plinth", "reason": note})
    return True


# --------------------------------------------------------------------------
# The steps of infer_levels
# --------------------------------------------------------------------------

def _level_elevations(b: dict, marks: list, params: dict, inferred: list, warnings: list) -> None:
    """Step 2: an assumed level elevation from the most common floor mark in its rooms."""
    tol = float(params["mark_tol"])
    for lv in base_levels(b):
        if lv.get("elevation_source") not in (None, "assumed_default"):
            continue
        rooms = {r["id"] for r in b.get("rooms") or [] if r.get("level_id") == lv["id"]
                 and r.get("room_type") not in NO_FLOOR_ROOMS}
        zs = [m["z"] for m in marks if m.get("kind") in FLOOR_KINDS and m.get("room_id") in rooms
              and m.get("z") is not None]
        if not zs:
            continue
        counts: dict[float, int] = {}
        for z in zs:
            counts[round(z, 2)] = counts.get(round(z, 2), 0) + 1
        best = max(counts, key=lambda z: (counts[z], -abs(z - float(lv.get("elevation") or 0.0))))
        old = float(lv.get("elevation") or 0.0)
        gl = ground_level(b)
        if gl is not None and lv["id"] == gl["id"] and abs(best - old) > tol and \
                (counts[best] < 2 or counts[best] * 2 < len(zs)):
            # the ground floor (building z 0 by convention) moves only when most of its floor marks agree
            listed = ", ".join(f"{z:+.2f}" for z in sorted(counts))
            warnings.append(f"level {lv['id']}: its floor marks disagree ({listed}); the elevation {old:+.2f} m is kept")
            continue
        old = float(lv.get("elevation") or 0.0)
        if abs(best - old) > tol:
            warnings.append(f"level {lv['id']}: elevation {old:+.2f} m (assumed) -> {best:+.2f} m from "
                            f"{counts[best]} floor mark(s)")
            inferred.append({"item": f"level {lv['id']} elevation", "value": best,
                             "reason": f"{counts[best]} of {len(zs)} floor marks in its rooms read {best:+.2f}"})
        lv["elevation"] = _r(best)
        lv["elevation_source"] = "level_mark"
        for m in marks:
            if m.get("kind") in FLOOR_KINDS and m.get("room_id") in rooms and m.get("z") is not None \
                    and abs(m["z"] - best) <= tol:
                _use(m, f"level_elevation:{lv['id']}")


def _room_floors(b: dict, marks: list, params: dict, conflicts: list, warnings: list) -> None:
    """Step 3: room floor offsets from the floor marks inside them."""
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    tol = float(params["mark_tol"])
    for room in b.get("rooms") or []:
        if room.get("floor_source") == "agent":
            continue
        lv = levels.get(room.get("level_id"))
        own = [m for m in marks if m.get("room_id") == room["id"] and m.get("kind") in FLOOR_KINDS
               and m.get("z") is not None]
        room["floor_offset_m"] = 0.0
        room["floor_source"] = "level"
        room["floor_evidence"] = []
        if not own or lv is None:
            continue
        if room.get("room_type") in NO_FLOOR_ROOMS:
            warnings.append(f"{room['id']} ({room.get('room_type')}): floor mark(s) "
                            f"{', '.join(m.get('raw') or str(m['value']) for m in own)} not used (stair landings)")
            continue
        zs = [m["z"] for m in own]
        z = _median(zs)
        offset = z - float(lv["elevation"])
        if abs(offset) > float(params["room_offset_max"]):
            warnings.append(f"{room['id']}: floor mark {z:+.2f} m is {offset:+.2f} m off its level floor (more than "
                            f"{float(params['room_offset_max']):.2f} m): not the room floor, listed")
            continue
        if max(zs) - min(zs) > tol:
            conflicts.append({"kind": "level_mark_mismatch", "element_ids": [room["id"]] + [m["id"] for m in own],
                              "description": f"{room['id']}: the floor marks inside it read "
                                             f"{', '.join(f'{v:+.2f}' for v in zs)} m",
                              "resolution": f"their median {z:+.2f} m used"})
        room["floor_offset_m"] = _r(offset)
        room["floor_source"] = "mark"
        room["floor_evidence"] = [e for m in own for e in _mark_ev(m)][:4]
        for m in own:
            _use(m, "room_floor")


def _thresholds(b: dict, params: dict, outlines: dict) -> list[dict]:
    """Step 4: ``threshold_z`` of every door and doorless opening on a wall; the inner steps."""
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    rooms_by = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    steps = []
    for o in b.get("openings") or []:
        if o.get("type") not in ("door", "opening") or o.get("virtual") or not o.get("wall_id"):
            continue
        lv = levels.get(o.get("level_id"))
        if lv is None:
            continue
        sides = opening_sides(b, o, rooms_by.get(lv["id"]) or [], outlines.get(lv["id"]) or [])
        floors = [room_floor_z(b, r) for r in (sides or {}).get("rooms") or [] if r is not None]
        o["threshold_z"] = _r(max(floors) if floors else float(lv["elevation"]))
        if len(floors) == 2 and abs(floors[0] - floors[1]) > float(params["flush_max"]):
            rise = abs(floors[0] - floors[1])
            low = sides["rooms"][0] if floors[0] < floors[1] else sides["rooms"][1]
            st = steps_for(rise, float(o.get("width") or 0.9), params, outdoor=False)
            steps.append({"opening_id": o["id"], "rise": _r(rise), "low_room": low["id"],
                          "risers": st["count"] if st else 0, "riser": st["riser"] if st else 0.0})
    return steps


def _ground(b: dict, marks: list, params: dict, gl: dict, outline, inferred: list, warnings: list) -> dict:
    """Step 5: the ground (points, surface, levels). Returns ``{"source", "points", "surface"}``."""
    from wenart.blender import site as S

    site = b["site"]
    ground = site.get("ground") if isinstance(site.get("ground"), dict) else {}
    site["ground"] = ground
    ground.setdefault("light_wells", [])
    # The drawn levels (sections); the ones an earlier run made from marks are made again (a mark's kind may have
    # changed since).
    drawn_levels = [g for g in ground.get("levels") or [] if isinstance(g, dict) and not g.get("from_mark")
                    and (g.get("z") or {}).get("method") not in (None, "assumed")]
    file = _file_of(b)
    cand, notes = [], []
    for m in marks:
        if m.get("kind") not in GROUND_KINDS or m.get("z") is None:
            continue
        if m.get("note") or m.get("point") is None:
            notes.append(m)
            continue
        p = tuple(m["point"])
        if len(outline) >= 3 and G.point_in_polygon(p, outline):
            warnings.append(f"{m['id']}: ground mark {m.get('raw')} inside the building outline: not used")
            continue
        if len(outline) >= 3 and _dist_to_polygon(p, outline) > float(params["ground_reach"]):
            continue                              # another drawing on the sheet (classified unknown by the reader)
        cand.append(m)
    force = (ground.get("terrain_override") or {}).get("kind")     # the agent's set_terrain (edits.py)
    points, rejected = [], []
    if cand:
        med = _median([m["z"] for m in cand])
        for m in cand:
            if abs(m["z"] - med) > float(params["ground_outlier"]):
                rejected.append(m)
                warnings.append(f"{m['id']}: ground mark {m.get('raw')} ({m['z']:+.2f} m) is more than "
                                f"{float(params['ground_outlier']):.1f} m from the median of the ground marks "
                                f"({med:+.2f} m): listed, not used")
            else:
                points.append(m)
    ground["points"] = [{"x": _r(m["point"][0], 4), "y": _r(m["point"][1], 4), "z": _r(m["z"]),
                         "kind": m["kind"], "mark_id": m["id"], "inferred": False, "used": m not in rejected,
                         "evidence": _mark_ev(m)} for m in points + rejected]
    for m in points:
        _use(m, "ground")
    surface = None
    source = None
    if force == "flat" and points and not drawn_levels:
        z = _median([m["z"] for m in points])
        drawn_levels = [{"side": "all", "azimuth_deg": None, "from_mark": points[0]["id"],
                         "z": {"value": _r(z), "method": "vector", "confidence": 1.0,
                               "evidence": [e for m in points for e in _mark_ev(m)][:2] or
                               [_evidence(file, "level_mark", "ground marks", 1.0)],
                               "note": f"set_terrain flat: the median of {len(points)} ground mark(s)"}}]
        source = "marks"
    if len(points) >= 3 and force not in ("flat", "sides"):
        residual = {"planar": float("inf"), "tin": -1.0}.get(force, float(params["plane_residual"]))
        surface = T.fit_surface([(m["point"][0], m["point"][1], m["z"]) for m in points],
                                plane_residual=residual, blend_m=float(params["terrain_blend"]))
        if surface["kind"] in ("planar", "tin"):
            source = "marks"
            surface.update(inferred=False, source="ground marks",
                           reason=f"{len(points)} ground marks: {surface['kind']} (largest residual "
                                  f"{surface['residual']:.2f} m)")
        else:
            surface = None
    if source is None and points and force != "flat":
        # 1-2 points (or points on one line): one level per side, unless a drawn level holds that side.
        from wenart.blender.site import side_of
        north, north_src = S.north_deg(b)
        known = not north_src.startswith("assumed")
        cx = sum(p[0] for p in outline) / max(len(outline), 1)
        cy = sum(p[1] for p in outline) / max(len(outline), 1)
        have = {g.get("side") for g in drawn_levels}
        added = []
        for m in points:
            d = (m["point"][0] - cx, m["point"][1] - cy)
            n = math.hypot(*d) or 1.0
            side = side_of((d[0] / n, d[1] / n), north, known)
            if side in have or side in added:
                continue
            added.append(side)
            drawn_levels.append({"side": side, "azimuth_deg": None, "from_mark": m["id"],
                                 "z": {"value": _r(m["z"]), "method": "vector", "confidence": 1.0,
                                       "evidence": _mark_ev(m) or [_evidence(file, "level_mark", m.get("raw") or "",
                                                                             1.0)],
                                       "note": f"ground mark {m.get('raw')} ({m['id']})"}})
        source = "marks"
    if source is None and notes and not drawn_levels:
        m = notes[0]
        drawn_levels = [{"side": "all", "azimuth_deg": None, "from_mark": m["id"],
                         "z": {"value": _r(m["z"]), "method": "vector", "confidence": 1.0,
                               "evidence": _mark_ev(m) or [_evidence(file, "level_mark", m.get("raw") or "", 1.0)],
                               "note": f"site note {m.get('raw')} ({m['id']})"}}]
        _use(m, "ground")
        source = "site_note"
    elif notes:
        for m in notes:
            _use(m, "ground_check")
    if source is None and drawn_levels:
        source = "section"
    if source is None:
        z = float(gl["elevation"]) - float(params["ground_rise"])
        drawn_levels = [{"side": "all", "azimuth_deg": None,
                         "z": {"value": _r(z), "method": "assumed", "confidence": 0.0, "evidence": [],
                               "note": f"D3a: nothing about the ground is drawn: the ground floor stands "
                                       f"{float(params['ground_rise']):.2f} m above it (one inferred step)"}}]
        source = "D3a"
        inferred.append({"item": "site.ground", "value": _r(z),
                         "reason": f"D3a: no ground drawn: {float(params['ground_rise']):.2f} m under {gl['id']}"})
    ground["levels"] = drawn_levels
    zs = {round(float(g["z"]["value"]), 3) for g in drawn_levels}
    if surface is None:
        flat_z = next(iter(zs)) if len(zs) == 1 else (sum(zs) / len(zs) if zs else 0.0)
        surface = T.fit_surface([], flat_z=flat_z, blend_m=float(params["terrain_blend"]))
        surface["kind"] = "flat" if len(zs) <= 1 else "sides"
        surface.update(inferred=source == "D3a", source=source,
                       reason={"D3a": "nothing about the ground drawn (D3a)", "site_note": "the site note's level",
                               "section": "the drawn ground lines per side", "marks": "ground marks per side"}[source])
    if force:
        surface["agent"] = dict(ground["terrain_override"])
    ground["surface"] = surface
    ground["terrain"] = surface["kind"]
    ground["source"] = source
    return {"source": source, "points": points, "surface": surface}


def terrain_for(b: dict, levels: list, outline, outlines: dict) -> dict:
    """The terrain model as the build makes it (``wenart.blender.site``: the surface or the per-side levels, and
    the basement doors' own terrain)."""
    from wenart.blender import site as S

    lowest = min(levels, key=lambda lv: float(lv["elevation"])) if levels else None
    default_z = 0.0 if lowest is None or float(lowest["elevation"]) < 0 else float(lowest["elevation"])
    tm = S.terrain_model(b, outline, default_z)
    doors = S.door_terrain(b, levels, tm, outline, outlines)
    if doors:
        tm = S.terrain_model(b, outline, default_z, overrides=doors)
    return tm


def _entrances(b: dict, marks: list, params: dict, levels: list, outline, outlines: dict, tm: dict,
               ground_points: list, conflicts: list, warnings: list) -> list[dict]:
    """Step 6: ``site.entrances``."""
    from wenart.blender import site as S

    file = _file_of(b)
    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    ids = {lv["id"] for lv in levels}
    lowered = {i for ch in tm.get("changes") or [] for i in ch.get("opening_ids") or []}
    ramp_doors = {r.get("door_id") for r in (b.get("site") or {}).get("drawn_ramps") or [] if isinstance(r, dict)}
    overrides = (b.get("site") or {}).get("entrance_overrides") or {}       # the agent's set_entrance (edits.py)
    brief_ramp = bool(params.get("accessible_entrance"))
    out = []
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("level_id") not in ids:
            continue
        lv = next(x for x in levels if x["id"] == o["level_id"])
        sides = opening_sides(b, o, rooms_by.get(lv["id"]) or [], outlines.get(lv["id"]) or outline)
        if sides is None or sum(sides["outside"]) != 1:
            continue
        k = 0 if sides["outside"][0] else 1
        room = sides["rooms"][1 - k]
        n = sides["normal"]
        outward = (n[0], n[1]) if k == 0 else (-n[0], -n[1])
        cx, cy = sides["centre"]
        ht = sides["half_t"]
        face = (cx + outward[0] * ht, cy + outward[1] * ht)
        probe = (cx + outward[0] * (ht + 0.3), cy + outward[1] * (ht + 0.3))
        threshold = float(o.get("threshold_z") if o.get("threshold_z") is not None else
                          (room_floor_z(b, room) if room else lv["elevation"]))
        near = [m for m in ground_points if G.distance(probe, m["point"]) <= float(params["door_ground_reach"])]
        if near and o["id"] not in lowered:
            m = min(near, key=lambda m: G.distance(probe, m["point"]))
            gz, gsrc = float(m["z"]), f"ground mark {m['id']}"
            _use(m, f"entrance:{o['id']}")
        else:
            gz, gsrc = S.ground_z(tm, *probe), ("terrain lowered to the door (basement door)" if o["id"] in lowered
                                               else f"terrain ({tm['kind']})")
        landing_mark = None
        for m in marks:
            if m.get("kind") in ("threshold", "entrance") and m.get("point") is not None and m.get("z") is not None \
                    and G.distance(face, m["point"]) <= float(params["door_mark_reach"]) + float(o.get("width") or 0):
                if landing_mark is None or G.distance(face, m["point"]) < G.distance(face, landing_mark["point"]):
                    landing_mark = m
        top = threshold
        if landing_mark is not None:
            top = float(landing_mark["z"])
            _use(landing_mark, f"entrance:{o['id']}")
            if abs(top - threshold) > float(params["mark_tol"]):
                conflicts.append({"kind": "level_mark_mismatch", "element_ids": [o["id"], landing_mark["id"]],
                                  "description": f"{o['id']}: the landing mark {landing_mark.get('raw')} "
                                                 f"({top:+.2f} m) and the door's floor ({threshold:+.2f} m) differ",
                                  "resolution": "the landing at the mark, a step at the door"})
        rise = top - gz
        width = float(o.get("width") or 0.9)
        rec = {"door_id": o["id"], "level_id": lv["id"], "room_id": room["id"] if room else None,
               "threshold_z": _r(threshold), "ground_z": _r(gz), "rise": _r(max(rise, 0.0)),
               "ground_source": gsrc, "centre": [_r(cx, 4), _r(cy, 4)], "outward": [_r(outward[0], 6),
                                                                                    _r(outward[1], 6)],
               "face": [_r(face[0], 4), _r(face[1], 4)], "width": _r(width), "half_t": _r(ht, 4),
               "side": S.side_of(outward, *_north(b)), "solution": "none", "steps": None, "ramp": None,
               "landing": None, "main": False, "drawn": landing_mark is not None, "inferred": True,
               "into_air": False, "upper_floor": False, "below_ground": False,
               "terrain_lowered": o["id"] in lowered, "reason": "",
               "evidence": [dict(e) for e in (o.get("evidence") or [])[:1]] +
               (_mark_ev(landing_mark) if landing_mark else [])}
        if rise < -float(params["flush_max"]):
            rec["below_ground"] = True
            rec["reason"] = (f"the door is {-rise:.2f} m below the ground in front: the ground there must be lowered "
                             f"(a sunken court) or the door is no entrance (L3)")
        elif rise <= float(params["flush_max"]):
            rec["reason"] = ("flush threshold: the terrain on its side is lowered to its floor (basement door)"
                             if o["id"] in lowered else f"flush threshold (rise {max(rise, 0):.2f} m)")
        elif rise > float(params["door_into_air"]):
            rec["into_air"] = True
            gl = ground_level(b)
            rec["upper_floor"] = gl is not None and float(lv["elevation"]) > float(gl["elevation"]) + 0.5
            rec["reason"] = (f"{rise:.2f} m above the ground with nothing drawn: a door into the air (L2): an outside "
                             f"stair or no entrance, to decide" +
                             ("; on an upper floor: a French balcony or a balcony not drawn" if rec["upper_floor"]
                              else ""))
        else:
            st = steps_for(rise, width + float(params["landing_extra_width"]), params)
            rec["steps"] = st
            rec["landing"] = {"width": _r(width + float(params["landing_extra_width"])),
                              "depth": _r(params["landing_depth"]), "z": _r(top)}
            rec["solution"] = "steps"
            rec["reason"] = (f"{rise:.2f} m above the ground ({gsrc}): a landing and {st['count']} riser(s) of "
                             f"{st['riser']:.3f} m, tread {st['tread']:.2f} m (inferred)")
            if o["id"] in ramp_doors:
                rec["ramp"] = ramp_for(rise, params)
                rec["solution"] = "steps_and_ramp"
                rec["drawn"] = True
                rec["reason"] += f"; a drawn ramp {rec['ramp']['ratio']}"
        agent = overrides.get(o["id"])
        if isinstance(agent, dict) and not rec["into_air"] and not rec["below_ground"]:
            _apply_entrance_override(rec, agent, max(rise, 0.0), top, width, params)
        rec["evidence"].append(_evidence(file, "entrance", rec["reason"]))
        out.append(rec)
    # The main entrance: the widest door of the main facade (the side with the most entrances at the ground).
    usable = [e for e in out if not e["into_air"] and not e["below_ground"]]
    if usable:
        counts: dict = {}
        for e in usable:
            counts[S.nearest_axis(e["outward"])] = counts.get(S.nearest_axis(e["outward"]), 0) + 1
        order = ("-y", "+y", "-x", "+x")
        axis = max(counts, key=lambda a: (counts[a], -order.index(a)))
        marked = [e for e in usable if any(m.get("kind") == "entrance" and e["door_id"] in
                                           " ".join(m.get("used_for") or []) for m in marks)]
        main = (marked or sorted((e for e in usable if S.nearest_axis(e["outward"]) == axis),
                                 key=lambda e: (-e["width"], e["door_id"])))[0]
        main["main"] = True
        if brief_ramp and main["solution"] == "steps":
            rise = main["rise"]
            main["ramp"] = ramp_for(rise, params)
            main["solution"] = "steps_and_ramp"
            main["reason"] += f"; brief levels.accessible_entrance: a ramp {main['ramp']['ratio']} (inferred)"
    return out


def _apply_entrance_override(rec: dict, agent: dict, rise: float, top: float, width: float, params: dict) -> None:
    """The agent's ``set_entrance`` solution on an entrance record (mutated): steps and / or a ramp sized by the
    rules for the same rise, or none; ``adjusted_by_ai`` keeps the reason and the solution before."""
    sol = agent.get("solution")
    before = rec["solution"]
    landing = {"width": _r(width + float(params["landing_extra_width"])), "depth": _r(params["landing_depth"]),
               "z": _r(top)}
    steps = steps_for(rise, width + float(params["landing_extra_width"]), params)
    ramp = ramp_for(rise, params)
    if sol == "none" or (steps is None and ramp is None):
        rec.update(solution="none", steps=None, ramp=None, landing=None)
    elif sol == "steps":
        rec.update(solution="steps", steps=steps, ramp=None, landing=landing)
    elif sol == "ramp":
        rec.update(solution="ramp", steps=None, ramp=ramp, landing=landing)
    elif sol == "steps_and_ramp":
        rec.update(solution="steps_and_ramp", steps=steps, ramp=ramp, landing=landing)
    rec["adjusted_by_ai"] = {"reason": agent.get("reason") or "", "before": before}
    rec["reason"] += f"; set_entrance {sol} (agent: {agent.get('reason') or 'no reason'})"


def _north(b: dict) -> tuple[float, bool]:
    from wenart.blender import site as S

    north, src = S.north_deg(b)
    return north, not src.startswith("assumed")


def _plinth(b: dict, marks: list, params: dict, gl: dict, outline, tm: dict) -> dict:
    """Step 7: ``site.plinth``."""
    from wenart.blender import geom2d
    from wenart.blender import site as S

    own = [m for m in marks if m.get("kind") == "plinth" and m.get("z") is not None]
    top = _median([m["z"] for m in own]) if own else float(gl["elevation"])
    for m in own:
        _use(m, "plinth")
    pts = geom2d.ccw(outline)
    by_axis: dict[str, float] = {}
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        length = G.distance(p, q)
        if length < 0.3:
            continue
        nx, ny = (q[1] - p[1]) / length, -(q[0] - p[0]) / length       # counter-clockwise: right is out
        axis = S.nearest_axis((nx, ny))
        z = min(S.ground_z(tm, p[0] + nx * 0.3, p[1] + ny * 0.3), S.ground_z(tm, q[0] + nx * 0.3, q[1] + ny * 0.3))
        by_axis[axis] = min(by_axis.get(axis, z), z)
    north, known = _north(b)
    # A side where a lower level meets the ground (a basement opened by a sloped site) takes that level's floor.
    floors = sorted({_r(top)} | {_r(lv["elevation"]) for lv in base_levels(b)
                                 if float(lv["elevation"]) < float(gl["elevation"]) - 1e-6})
    flush = float(params["flush_max"])

    def top_at(z: float) -> float:
        return min([f for f in floors if f >= z - flush] or [top])

    sides = [{"axis": a, "side": S.side_of(S.AXES[a], north, known), "ground_z": _r(z), "top_z": _r(top_at(z)),
              "height": _r(max(top_at(z) - z, float(params["plinth_min"])))} for a, z in sorted(by_axis.items())]
    return {"top_z": _r(top), "floors": floors, "min_height": _r(params["plinth_min"]), "sides": sides,
            "height": max((s["height"] for s in sides), default=_r(params["plinth_min"])),
            "source": "mark" if own else "inferred", "inferred": not own,
            "evidence": [e for m in own for e in _mark_ev(m)][:2] or
            [_evidence(_file_of(b), "plinth", f"the plinth up to the floor of {gl['id']} (no SB. mark), at least "
                                              f"{float(params['plinth_min']):.2f} m")],
            "note": "the facade plinth is a raised base from the ground to this top (at least min_height)"}


def _basements(b: dict, params: dict, gl: dict, levels: list, outline, outlines: dict, tm: dict,
               brief: Optional[dict]) -> list[dict]:
    """Step 8: the levels below the ground floor and their light wells / courts, written into
    ``site.ground.light_wells`` (assumed, inferred)."""
    from wenart.blender import site as S
    from wenart import building as B

    out = []
    below = [lv for lv in levels if float(lv["elevation"]) < float(gl["elevation"]) - 0.5
             or lv.get("kind") == "basement" or "BODRUM" in B.fold_ascii(str(lv.get("label") or "")).upper()]
    if not below:
        return out
    court = "auto"
    try:
        from wenart import brief as BR
        court = BR.front_court(brief if isinstance(brief, dict) and "values" in brief else {"values": brief or {}})
    except ImportError:
        pass
    wells, _warn = S.light_wells(b, levels, tm, outline, outlines, front_court=court)
    ground = b["site"]["ground"]
    drawn = {w.get("opening_id") for w in ground.get("light_wells") or [] if w.get("source", "drawn") == "drawn"}
    keep = [w for w in ground.get("light_wells") or [] if w.get("source", "drawn") == "drawn"]
    for w in wells:
        if w["opening_id"] in drawn or w["source"] == "drawn":
            continue
        keep.append({"opening_id": w["opening_id"], "opening_ids": list(w.get("opening_ids") or [w["opening_id"]]),
                     "level_id": w["level_id"], "polygon": [[_r(x, 4), _r(y, 4)] for x, y in w["polygon"]],
                     "depth": _r(w["top_z"] - w["floor_z"]), "floor_z": _r(w["floor_z"]), "top_z": _r(w["top_z"]),
                     "kind": w.get("kind") or "light_well", "source": "assumed", "inferred": True,
                     "reason": w["reason"]})
    ground["light_wells"] = keep
    for lv in below:
        gz = min((S.ground_z(tm, *p) for p in outline), default=0.0)
        out.append({"level_id": lv["id"], "floor_z": _r(lv["elevation"]),
                    "below_ground_m": _r(gz - float(lv["elevation"])),
                    "light_wells": sum(1 for w in keep if w.get("level_id") == lv["id"])})
    return out


# --------------------------------------------------------------------------
# infer_levels
# --------------------------------------------------------------------------

def infer_levels(building: dict, brief: Optional[dict] = None) -> dict:
    """The level fields of §3.2 (module docstring); pure."""
    b = copy.deepcopy(building)
    brief = _brief_of(b, brief)
    params = level_params(brief)
    marks = [m for m in b.get("level_marks") or [] if isinstance(m, dict)]
    inferred: list[dict] = []
    conflicts: list[dict] = []
    warnings: list[str] = list(params["_warnings"])
    record = {"version": "m12", "ground_floor": None, "ground_source": None, "inferred": inferred,
              "conflicts": conflicts, "warnings": warnings, "inner_steps": [], "basements": [],
              "params": {k: v for k, v in params.items() if not k.startswith("_")},
              "params_from_brief": list(params["_from_brief"]),
              "flagged": "step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7)",
              "edits": list((building.get("level_inference") or {}).get("edits") or [])}
    b["level_inference"] = record
    gl = ground_level(b)
    if gl is None:
        return b
    record["ground_floor"] = gl["id"]
    _level_elevations(b, marks, params, inferred, warnings)
    record["single_level_whole"] = whole_single_level(b, params, brief, inferred)
    _room_floors(b, marks, params, conflicts, warnings)
    outlines = outlines_of(b)
    record["inner_steps"] = _thresholds(b, params, outlines)
    if not is_whole(b):
        return b
    if not isinstance(b.get("site"), dict):                 # a whole building always stands on a site
        from wenart.sheets import exterior as SE
        from wenart.sheets import to_building as TB
        b["site"] = TB.site_block({"boundary_walls": [], "areas": [], "decor": [], "openings": []}, {}, SE.area_kind,
                                  gl["id"])
    from wenart.blender import build as BB

    levels = base_levels(b)
    outline = BB.ground_outline(b, outlines)
    if len(outline) < 3:
        warnings.append("no closed outline at the ground: no ground, entrances or plinth inferred")
        return b
    g = _ground(b, marks, params, gl, outline, inferred, warnings)
    record["ground_source"] = g["source"]
    tm = terrain_for(b, levels, BB.ground_outline(b, outlines), outlines)
    site = b["site"]
    site["entrances"] = _entrances(b, marks, params, levels, outline, outlines, tm, g["points"], conflicts, warnings)
    for e in site["entrances"]:
        if e["solution"] != "none":
            inferred.append({"item": f"entrance {e['door_id']}", "value": e["solution"], "reason": e["reason"]})
    site["plinth"] = _plinth(b, marks, params, gl, outline, tm)
    if site["plinth"]["inferred"]:
        inferred.append({"item": "site.plinth", "value": site["plinth"]["top_z"],
                         "reason": "no SB. mark: the plinth up to the ground floor"})
    record["basements"] = _basements(b, params, gl, levels, outline, outlines, tm, brief)
    for w in site["ground"].get("light_wells") or []:
        if w.get("inferred"):
            inferred.append({"item": f"{w.get('kind')} {w['opening_id']}", "value": w["depth"], "reason": w["reason"]})
    return b
