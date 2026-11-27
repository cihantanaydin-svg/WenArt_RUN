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
6b. **Outdoor spaces and site symbols** (26 Oct 2026, ``wenart.levels.outdoor``): the drawn site symbols are typed
   (``type_site_decor``); every labelled outdoor space of any level gets ``site.outdoor_spaces`` (its outline, floor,
   doors, drawn steps, columns, roof and posts); a door onto one has ``solution`` none and ``onto`` (the space is its
   landing; an upper floor's door onto a balcony is no door into the air).
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
import re
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.levels import terrain as T

# 28 Oct 2026: the pure rules live in wenart.levels.rules (the build reads them without the sheet pipeline)
from wenart.levels.rules import (BUILTIN_PARAMS, _brief_values, _default_params,  # noqa: F401
                                 drive_for, level_params, ramp_for, steps_for)

GROUND_KINDS = ("ground_natural", "ground_finished", "slope_top")
# the keys of ``level_inference`` the levels model writes (13 Nov 2026): every other key is kept on a run again
MODEL_KEYS = ("version", "ground_floor", "ground_source", "inferred", "conflicts", "warnings", "inner_steps", "basements",
              "params", "params_from_brief", "flagged", "single_level_whole", "edits", "conflicts_copied", "frame",
              "level_frames", "ground_gate")
FLOOR_KINDS = ("floor", "entrance")
NO_FLOOR_ROOMS = ("stair", "shaft")
FLAT_THICKNESS = 0.30                       # the flat_cut roof slab (roof.DEFAULTS["flat_thickness"])
UPPER_WORDS = ("1. KAT", "NORMAL KAT", "FIRST FLOOR", "SECOND FLOOR", "UPPER FLOOR", "TIP KAT", "CATI", "ATTIC",
               "ROOF", "ASMA KAT", "MEZZANINE")


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------

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

STOREY_MIN_M = 2.0             # 12 Nov 2026: two whole storeys stand at least this far apart (a floor of rooms and its slab)
STOREY_MAX_M = 6.0             # ... and at most this far (a taller storey is a double-height space a section must give)
# 23 Nov 2026 (stairs round, lesson UL376; real15: L1 at +7.82 m from a section whose 9 slab bands were mapped onto two
# plans, its 17-tread stair and its floor marks +0.50 / +3.50 saying a 3.00 m storey): a stair's risers check the storey
STAIR_RISER_M = (0.15, 0.19)   # a plausible riser
STAIR_RISERS_EXTRA = (-1, 2)   # a flight drawn with L lines has L-1 to L+2 risers (its end lines drawn or not, a landing)
STAIR_STOREY_MIN_LINES = 5     # a stair with fewer lines drawn says nothing about the storey
STAIR_STOREY_TOL_M = 0.05


def stair_lines(f: dict) -> int:
    """The lines a stair piece draws: its flights' tread lines summed, or the steps its numbers count (pure)."""
    recs = [r for r in ((f.get("details") or {}).get("stair"), f.get("stair")) if isinstance(r, dict)]
    lines = max((sum(int(fl.get("lines") or 0) for fl in r.get("flights") or [] if isinstance(fl, dict))
                 for r in recs), default=0)
    steps = max((int(r.get("steps_drawn") or 0) for r in recs if isinstance(r.get("steps_drawn"), (int, float))),
                default=0)
    return max(lines, steps)


def stair_rise_range(lines: int) -> Optional[tuple[float, float]]:
    """The storey heights (m) a stair of ``lines`` drawn lines can climb: ``STAIR_RISERS_EXTRA`` around its lines,
    each riser ``STAIR_RISER_M``; None for a stair of fewer than ``STAIR_STOREY_MIN_LINES`` lines (pure)."""
    if lines < STAIR_STOREY_MIN_LINES:
        return None
    return (round((lines + STAIR_RISERS_EXTRA[0]) * STAIR_RISER_M[0], 3),
            round((lines + STAIR_RISERS_EXTRA[1]) * STAIR_RISER_M[1], 3))


def storey_stairs(b: dict, level_id: str) -> list[tuple[dict, tuple[float, float]]]:
    """The stair pieces of a level with the storey heights each can climb (``stair_rise_range``) (pure)."""
    out = []
    for f in b.get("furniture") or []:
        if f.get("type") == "stair" and f.get("level_id") == level_id:
            rng = stair_rise_range(stair_lines(f))
            if rng is not None:
                out.append((f, rng))
    return out


def _floor_mark(b: dict, marks: list, level_id: str) -> Optional[tuple[float, int, int]]:
    """The most common floor mark in a level's rooms: (z, its count, all floor marks) or None."""
    rooms = {r["id"] for r in b.get("rooms") or [] if r.get("level_id") == level_id
             and r.get("room_type") not in NO_FLOOR_ROOMS}
    zs = [round(float(m["z"]), 2) for m in marks if m.get("kind") in FLOOR_KINDS and m.get("room_id") in rooms
          and m.get("z") is not None]
    if not zs:
        return None
    counts: dict = {}
    for z in zs:
        counts[z] = counts.get(z, 0) + 1
    best = max(counts, key=lambda z: (counts[z], -abs(z)))
    return best, counts[best], len(zs)


def _storey_vs_stairs(b: dict, marks: list, params: dict, conflicts: list, inferred: list, warnings: list) -> None:
    """Step 1b (23 Nov 2026, stairs round, UL376): a storey a section gives is checked against the stairs that climb
    it. Two storeys next to each other (orders n and n + 1), the upper one's elevation from a section: when no stair of
    the lower one (``storey_stairs``) can climb the step, it is a conflict (``storey_height_mismatch``). The step is
    corrected only when the plans' own floor marks say otherwise: the most common floor mark of each storey's rooms
    (two marks or more on the upper one), their difference a storey (``STOREY_MIN_M``-``STOREY_MAX_M``) that a stair
    climbs; the storey further from the ground floor (which stays at building z 0: above it the upper storey, below it
    the lower one) and the storeys beyond it then move by the difference, the lower storey's ceiling, walls and
    openings of the old ceiling height and the moved slabs with them, the moved level's source a level mark (the
    marks are source data; the section's bands stay as drawn, listed). Nothing changes silently: every check that
    fails is a conflict and a warning, every move is inferred."""
    tol = float(params["mark_tol"])
    ordered = sorted((lv for lv in base_levels(b) if lv.get("order") is not None and lv.get("elevation") is not None),
                     key=lambda x: int(x["order"]))
    for a, c in zip(ordered, ordered[1:]):
        if int(c["order"]) != int(a["order"]) + 1 or c.get("elevation_source") != "section":
            continue
        step = float(c["elevation"]) - float(a["elevation"])
        stairs = storey_stairs(b, a["id"])
        if not stairs or any(lo - STAIR_STOREY_TOL_M <= step <= hi + STAIR_STOREY_TOL_M for _f, (lo, hi) in stairs):
            continue
        said = "; ".join(f"{f['id']} ({stair_lines(f)} lines: {lo:.2f}-{hi:.2f} m)" for f, (lo, hi) in stairs)
        ids = [a["id"], c["id"]] + [f["id"] for f, _r_ in stairs]
        ma, mc = _floor_mark(b, marks, a["id"]), _floor_mark(b, marks, c["id"])
        mstep = round(mc[0] - ma[0], 3) if ma and mc else None
        fits = mstep is not None and mc[1] >= 2 and STOREY_MIN_M - tol <= mstep <= STOREY_MAX_M + tol and any(
            lo - STAIR_STOREY_TOL_M <= mstep <= hi + STAIR_STOREY_TOL_M for _f, (lo, hi) in stairs)
        what = (f"{c['id']} stands {step:.2f} m above {a['id']} (the section), but no stair of {a['id']} climbs that "
                f"at {STAIR_RISER_M[0]:.2f}-{STAIR_RISER_M[1]:.2f} m a riser: {said}")
        if not fits:
            why = ("its floor marks say nothing" if mstep is None else
                   f"the floor marks ({ma[0]:+.2f} / {mc[0]:+.2f}: {mstep:.2f} m) do not settle it")
            conflicts.append({"kind": "storey_height_mismatch", "element_ids": ids, "description": what,
                              "resolution": f"unresolved: the section's storey kept ({why})"})
            warnings.append(f"levels: {what}; the section's storey kept ({why})")
            continue
        # the storey further from the ground floor moves (the ground floor stays at building z 0): above it the upper
        # storey and those over it, below it the lower storey and those under it
        gl = ground_level(b)
        g_order = int(gl["order"]) if gl is not None and gl.get("order") is not None else int(a["order"])
        change = round(mstep - step, 3)                    # the new storey less the section's
        up = int(c["order"]) > g_order
        mover = c if up else a
        delta = change if up else -change
        moved = {lv["id"] for lv in ordered if (int(lv["order"]) >= int(c["order"]) if up
                                                else int(lv["order"]) <= int(a["order"]))}
        old_m = float(mover["elevation"])
        for lv in ordered:
            if lv["id"] in moved:
                lv["elevation"] = _r(float(lv["elevation"]) + delta)
        mover["elevation_before"] = _r(old_m)
        mover["elevation_source"] = "level_mark"
        file = _file_of(b)
        note = (f"{what}; the floor marks of {a['id']} ({ma[0]:+.2f}, {ma[1]} of {ma[2]}) and {c['id']} "
                f"({mc[0]:+.2f}, {mc[1]} of {mc[2]}) give {mstep:.2f} m, which the stair climbs: {mover['id']} "
                f"{old_m:+.2f} -> {float(mover['elevation']):+.2f} m and the storeys {'over' if up else 'under'} it by "
                f"{delta:+.2f} m (the ground floor stays; the marks are source data; the section's slab bands stay as "
                f"drawn)")
        mover.setdefault("evidence", []).append(_evidence(file, "storey_vs_stairs", note, confidence=0.8))
        conflicts.append({"kind": "storey_height_mismatch", "element_ids": ids, "description": what,
                          "resolution": f"the floor marks and the stair: {mover['id']} at "
                                        f"{float(mover['elevation']):+.2f} m (was {old_m:+.2f} m from the section)"})
        warnings.append(f"level {mover['id']}: elevation {old_m:+.2f} m (section) -> "
                        f"{float(mover['elevation']):+.2f} m ({note})")
        inferred.append({"item": f"level {mover['id']} elevation", "value": _r(float(mover["elevation"])),
                         "reason": note})
        # the lower storey's ceiling, walls and openings of that ceiling height, its floor to floor; the moved slabs
        old_ceiling = a.get("ceiling_height")
        if isinstance(old_ceiling, (int, float)) and a.get("ceiling_height_source") == "section" \
                and float(old_ceiling) + change >= STOREY_MIN_M:
            new_ceiling = _r(float(old_ceiling) + change)
            a["ceiling_height"] = new_ceiling
            n_w = n_o = 0
            for key in ("walls", "walls_merged", "openings"):
                for e in b.get(key) or []:
                    if isinstance(e, dict) and e.get("level_id") == a["id"] and isinstance(e.get("height"), (int, float)) \
                            and abs(float(e["height"]) - float(old_ceiling)) <= 0.01:
                        e["height"] = new_ceiling
                        n_o += key == "openings"
                        n_w += key != "openings"
            inferred.append({"item": f"level {a['id']} ceiling height", "value": new_ceiling,
                             "reason": f"its storey changed by {change:+.2f} m: {n_w} walls and {n_o} openings of the "
                                       f"ceiling height {float(old_ceiling):.2f} m follow"})
        if isinstance(a.get("floor_to_floor"), dict):
            a["floor_to_floor"] = {"value": mstep, "method": "derived", "confidence": 0.8,
                                   "evidence": [_evidence(file, "storey_vs_stairs", note, confidence=0.8)],
                                   "note": f"was {a['floor_to_floor'].get('value')} m from the section: {note}"}
        for sl in b.get("slabs") or []:
            if isinstance(sl, dict) and sl.get("above_level_id") in moved and isinstance(sl.get("z_top"), (int, float)):
                sl["z_top_before"] = _r(float(sl["z_top"]))
                sl["z_top"] = _r(float(sl["z_top"]) + delta)
                sl["z_top_source"] = "level_mark"


def _plan_frame(b: dict, marks: list, gl: Optional[dict], tol: float, inferred: list, warnings: list,
                conflicts: Optional[list] = None, prev_frame: Optional[dict] = None) -> float:
    """12 Nov 2026 (review of the reader targets, real11: no section gives the height frame, the ground floor's plan
    prints its floor '+2.50' in the stair and at its threshold, the basement '-0.50' and its ground '-0.50 / ±0.00'): the
    plans' own height frame when no section datum gives one. When the ground floor's marks (floor marks in its rooms,
    stairs included, and its threshold and entrance marks) agree on a value v other than 0 (two or more), and its room
    floor marks alone do not already move it there, every relative plan mark is read as mark - v (the one-frame rule of
    the user's C0061); 0.0 otherwise. The marks are changed in place (``frame_shift``).

    19 Nov 2026 (review A3, A3C-3: two outside threshold marks '-0.15' outvoted the one room mark '±0.00', a stair
    landing's '+1.50' shifted the whole building): the frame's value is one at least one floor mark of a room that is
    no stair reads; the stair, threshold and entrance marks only confirm it (two or more marks in all); a room floor
    mark of the ground floor reading 0 keeps the marks as printed.

    27 Nov 2026 (audit H4: an agent's level edit ran the model again and that run took this frame for R01 a's and moved
    the ground): the frame is recorded (``level_inference.frame``, rule ``plan_frame``); a run again finds the marks
    shifted and keeps that record (``_set_frame_once``)."""
    if gl is None or isinstance((b.get("project") or {}).get("datum"), dict):
        return 0.0
    if gl.get("elevation_source") not in (None, "assumed_default"):
        return _set_frame_once(b, marks, gl, tol, inferred, warnings, conflicts, prev_frame)
    rooms = {r["id"]: r for r in b.get("rooms") or [] if r.get("level_id") == gl["id"]}
    own = [m for m in marks if m.get("z") is not None and not m.get("frame_shift") and (
        (m.get("kind") in FLOOR_KINDS and m.get("room_id") in rooms) or
        (m.get("kind") in ("threshold", "entrance") and m.get("level_id") == gl["id"]))]
    # 19 Nov 2026 (review A4, A4C-02: a ground-floor terrace room marked ±0.00, the garden's level, refused the frame and
    # every storey shifted): an open-air room's mark is no room floor of the storey either
    room_only = [m for m in own if m.get("kind") in FLOOR_KINDS
                 and (rooms.get(m.get("room_id")) or {}).get("room_type") not in NO_FLOOR_ROOMS
                 and not _open_air(rooms.get(m.get("room_id")))]
    if not room_only or any(abs(float(m["z"])) <= tol for m in room_only):
        return 0.0
    counts: dict = {}
    for m in own:
        counts[round(float(m["z"]), 2)] = counts.get(round(float(m["z"]), 2), 0) + 1
    cands = {z: n for z, n in counts.items() if any(abs(float(m["z"]) - z) <= tol for m in room_only)}
    if not cands:
        return 0.0
    v = max(cands, key=lambda z: (cands[z], -abs(z)))
    if abs(v) <= tol or counts[v] < 2 or sum(1 for m in room_only if abs(float(m["z"]) - v) <= tol) >= 2:
        return 0.0
    n = 0
    for m in marks:
        if m.get("z") is not None and m.get("relative", True) is not False and not m.get("frame_shift"):
            m["z"] = _r(float(m["z"]) - v)
            m["frame_shift"] = v
            n += 1
    warnings.append(f"levels: the ground floor's plan marks read {v:+.2f} m ({counts[v]} marks: its floor, stair and "
                    f"threshold): every plan mark ({n}) is read in that frame (mark - {v:.2f}; no section datum)")
    inferred.append({"item": "plan height frame", "value": v,
                     "reason": f"{counts[v]} of the ground floor's marks read {v:+.2f} (one height frame, C0061)"})
    b.setdefault("level_inference", {})["frame"] = {"value": v, "rule": "plan_frame", "marks": counts[v],
                                                    "ground_floor": gl["id"], "source": gl.get("elevation_source")}
    return v


PRINTED_STOREY_RULES = ("plan_title_marks", "section_storey_marks")   # a storey's own printed floor mark gives it
MAIN_ROOM_TYPES = ("living", "dining", "bedroom", "kitchen", "hall")   # a frame needs one of these (never a garage ...)
FRAME_AREA_SHARE = 0.5          # ... and rooms of this share of the storey's floor area (all its rooms, audit H1/H2)


def printed_storey(lv: dict) -> bool:
    """27 Nov 2026 (audit H1/H2/G4): whether a level's elevation is its own printed storey mark in the plans' common
    frame: a level mark (its plan title's, or its rooms' marks moved it) or a section's storey marks
    (``elevation_rule``, written by ``sheets.to_building``); such a storey's marks need no frame (pure)."""
    return lv.get("elevation_source") == "level_mark" or lv.get("elevation_rule") in PRINTED_STOREY_RULES


def _title_of(lv: dict) -> str:
    """A level's title text (its evidence), else its label (pure)."""
    for e in lv.get("evidence") or []:
        if isinstance(e, dict) and e.get("text") and e.get("rule") in ("title_keyword", "plan_title_marks",
                                                                         "title_level"):
            return str(e["text"])
    return str(lv.get("label") or lv.get("id"))


def _floor_rooms(b: dict, level_id: str) -> list:
    """The rooms of a storey that are its floor (no stair, no shaft, no open-air room; pure)."""
    return [r for r in b.get("rooms") or [] if r.get("level_id") == level_id
            and r.get("room_type") not in NO_FLOOR_ROOMS and not _open_air(r)]


def _room_area(r: dict) -> float:
    try:
        return abs(float(r.get("area_computed"))) if r.get("area_computed") is not None else \
            abs(G.polygon_area([tuple(q[:2]) for q in r.get("polygon") or []]))
    except (TypeError, ValueError):
        return 0.0


def frame_basis(b: dict, level_id: str, rooms_at: Sequence[dict]) -> tuple[bool, str]:
    """27 Nov 2026 (audit H1/H2/G4): whether the rooms ``rooms_at`` that share one floor mark may give a storey's height
    frame (pure): they hold a main room (``MAIN_ROOM_TYPES``; never from a garage, a store, a wet or a technical room
    alone) and ``FRAME_AREA_SHARE`` of the area of all the storey's floor rooms (a storey that marks only the rooms
    that differ, a sunken garage or a split level, keeps its steps). ``(ok, why)``."""
    total = sum(_room_area(r) for r in _floor_rooms(b, level_id))
    share = sum(_room_area(r) for r in rooms_at) / total if total > 0 else 0.0
    main = [r["id"] for r in rooms_at if r.get("room_type") in MAIN_ROOM_TYPES]
    if not main:
        return False, (f"the rooms that read it ({', '.join(r['id'] for r in rooms_at)}) hold no main room (living, "
                       f"dining, bedroom, kitchen, hall)")
    if share < FRAME_AREA_SHARE:
        return False, f"the rooms that read it are {share:.0%} of the storey's floor area (under {FRAME_AREA_SHARE:.0%})"
    return True, f"{share:.0%} of the storey's floor area, main rooms {', '.join(main[:4])}"


def frame_counts(rec: Optional[dict]) -> bool:
    """Whether a recorded height frame is R01 a's (``_set_frame_once``), the one whose ±0.00 may be the ground
    (``frame_zero``): rule ``set_frame_once``, or a record of 26 Nov that names its rooms (pure)."""
    if not isinstance(rec, dict) or not rec.get("value"):
        return False
    return rec.get("rule") == "set_frame_once" or (rec.get("rule") is None and "rooms" in rec)


def _set_frame_once(b: dict, marks: list, gl: dict, tol: float, inferred: list, warnings: list,
                    conflicts: Optional[list] = None, prev_frame: Optional[dict] = None) -> float:
    """26 Nov 2026 (R01 a; real15: the section set the ground floor at building z 0, every room mark of it read
    '+0.50' and of L1 '+3.50'; the frame was never applied, so the marked rooms stood 0.5 m above the unmarked ones and
    the stairs arrived 0.5 m under the halls): one height frame per building, read once before any mark is used, when
    the ground floor's elevation is not assumed (a section, a level mark, the stair check set it; an assumed one moves
    to its marks instead, ``_level_elevations``) and no section datum gives the frame. Each marked room of the ground
    floor (no stair, no open-air room) reads its most common floor mark; the value most of those rooms share (two rooms
    or more, at least half of them; one room only with a threshold or entrance mark of the storey reading it too) less
    the ground floor's model elevation is the frame: every relative plan mark is read as mark - frame
    (``frame_shift``), so the ground floor's main floor mark reads its elevation. Returns the frame (0.0: none).

    27 Nov 2026 (audit H1: a storey that marks only its sunken garage and store, a split level or 3 cm wet-room drops
    shifted every mark of the building): never when the ground floor's elevation is its own printed storey mark
    (``printed_storey``: a title's or a section's storey mark is already the plans' frame); never when a marked room
    reads the storey's elevation (it confirms the frame); and only from rooms that hold a main room and most of the
    storey's floor area (``frame_basis``). Every frame is a ``level_mark_mismatch`` conflict naming the storey's title
    and the marks. A run again (the marks carry the frame) keeps the first run's record (``prev_frame``; audit H4)."""
    shifts = {round(float(m["frame_shift"]), 3) for m in marks if m.get("frame_shift")}
    if len(shifts) == 1:
        # a run again (an agent edit): the marks carry the frame already; it is recorded again, never applied twice
        v = shifts.pop()
        if isinstance(prev_frame, dict) and abs(float(prev_frame.get("value") or 0.0) - v) <= 1e-3:
            rec = dict(prev_frame)
        else:
            # no record of the first run: R01 a always writes one, so the marks were shifted by the plans' frame of an
            # assumed ground floor (``_plan_frame``) or the levels below
            rec = {"value": v, "rule": "plan_frame", "ground_floor": gl["id"], "source": gl.get("elevation_source")}
        rec["again"] = True
        b.setdefault("level_inference", {})["frame"] = rec
        return v
    rooms = {r["id"]: r for r in b.get("rooms") or [] if r.get("level_id") == gl["id"]}
    per_room: dict = {}
    for m in marks:
        if m.get("z") is None or m.get("frame_shift") or m.get("kind") not in FLOOR_KINDS:
            continue
        r = rooms.get(m.get("room_id"))
        if r is None or r.get("room_type") in NO_FLOOR_ROOMS or _open_air(r):
            continue
        per_room.setdefault(r["id"], []).append(round(float(m["z"]), 2))
    if not per_room:
        return 0.0
    elev = float(gl.get("elevation") or 0.0)
    vals = {}
    for rid, zs in per_room.items():
        vals[rid] = max(set(zs), key=lambda z: (zs.count(z), -abs(z - elev)))

    def rooms_at(v: float) -> int:
        return sum(1 for x in vals.values() if abs(x - v) <= tol)
    v = max(sorted(set(vals.values())), key=lambda z: (rooms_at(z), -abs(z - elev)))
    n = rooms_at(v)
    frame = round(v - elev, 3)
    if abs(frame) <= tol or n * 2 < len(vals):
        return 0.0
    confirm = [m for m in marks if m.get("z") is not None and not m.get("frame_shift") and m.get("level_id") == gl["id"]
               and m.get("kind") in ("threshold", "entrance") and abs(float(m["z"]) - v) <= tol]
    if n < 2 and not confirm:
        return 0.0
    at = [rooms[rid] for rid, x in vals.items() if abs(x - v) <= tol]
    refuse = None
    if printed_storey(gl):
        refuse = (f"its elevation is its own printed storey mark ({gl.get('elevation_source')}"
                  + (f", {gl['elevation_rule']}" if gl.get("elevation_rule") else "") +
                  "), already the plans' height frame")
    elif rooms_at(elev) > 0:
        refuse = f"{rooms_at(elev)} marked room(s) read the storey's elevation {elev:+.2f} m (they confirm it)"
    else:
        ok, basis = frame_basis(b, gl["id"], at)
        if not ok:
            refuse = basis
    if refuse is not None:
        warnings.append(f"levels: {n} of the {len(vals)} marked rooms of the ground floor {gl['id']} read {v:+.2f} m "
                        f"while it stands at {elev:+.2f} m: no height frame ({refuse}); the rooms keep their own steps")
        return 0.0
    _ok, basis = frame_basis(b, gl["id"], at)
    k = 0
    used = []
    for m in marks:
        if m.get("z") is not None and m.get("relative", True) is not False and not m.get("frame_shift"):
            m["z"] = _r(float(m["z"]) - frame)
            m["frame_shift"] = frame
            k += 1
            if m.get("room_id") in vals and abs(float(m["z"]) - elev) <= tol:
                used.append(m)
    why = (f"{n} of the {len(vals)} marked rooms of the ground floor {gl['id']} read {v:+.2f} m ({basis}) while its "
           f"elevation ({gl.get('elevation_source')}) is {elev:+.2f} m: the plans' marks stand in a frame {frame:+.2f} m "
           f"off; every plan mark ({k}) is read as mark - {frame:.2f} (one height frame, read once; no section datum)")
    warnings.append(f"levels: {why}")
    inferred.append({"item": "plan height frame", "value": frame, "reason": why})
    if conflicts is not None:
        conflicts.append({"kind": "level_mark_mismatch", "element_ids": [gl["id"]] + [m["id"] for m in used][:12],
                          "description": f"the ground floor {gl['id']} ('{_title_of(gl)}') stands at {elev:+.2f} m "
                                         f"({gl.get('elevation_source')}), its rooms' marks read {v:+.2f} m "
                                         f"({', '.join(str(m.get('raw') or m['id']) for m in used[:6])})",
                          "resolution": f"one height frame of {frame:+.2f} m: every plan mark is read as mark - "
                                        f"{frame:.2f} ({basis})"})
    b.setdefault("level_inference", {})["frame"] = {"value": frame, "rule": "set_frame_once", "rooms": n,
                                                    "of": len(vals), "mark": v, "ground_floor": gl["id"],
                                                    "source": gl.get("elevation_source")}
    return frame


def _level_elevations(b: dict, marks: list, params: dict, inferred: list, warnings: list,
                      conflicts: Optional[list] = None, prev_frame: Optional[dict] = None) -> None:
    """Step 2: an assumed level elevation from the most common floor mark in its rooms.

    12 Nov 2026 (reviews of the reader targets; real07: a stair-landing datum moved both floors while their slabs stayed;
    real11: '+0.00' on the 7th storey's plan, the plans in a '+2.50' frame; real13: a roof mark '+16.00' would have made a
    7 m storey): the plans' marks are first read in their own height frame (``_plan_frame``); the moves are proposed,
    an assumed level above a moved one moves by the same amount, and the set is kept only while every storey stays
    ``STOREY_MIN_M`` to ``STOREY_MAX_M`` above the one below. A conflict refuses the proposal it blames (the one against a
    level that does not move, else the one with fewer marks, else the larger move), never simply the lower one, and the
    others are checked again; a refused move is a warning. A level that moves takes the slab under it along, unless the
    slab is a variant's (an alternative level stands there), with the move as its evidence."""
    tol = float(params["mark_tol"])
    gl = ground_level(b)
    _plan_frame(b, marks, gl, tol, inferred, warnings, conflicts, prev_frame)
    proposed: dict = {}
    for lv in base_levels(b):
        if lv.get("elevation_source") not in (None, "assumed_default") or lv.get("typical_of"):
            continue        # 13 Nov 2026: a typical floor's copy re-reads that floor's marks: they are its floor's
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
        if gl is not None and lv["id"] == gl["id"] and abs(best - old) > tol and \
                (counts[best] < 2 or counts[best] * 2 < len(zs)):
            # the ground floor (building z 0 by convention) moves only when most of its floor marks agree
            listed = ", ".join(f"{z:+.2f}" for z in sorted(counts))
            warnings.append(f"level {lv['id']}: its floor marks disagree ({listed}); the elevation {old:+.2f} m is kept")
            continue
        proposed[lv["id"]] = (lv, best, counts, zs, rooms)
    ordered = sorted((lv for lv in base_levels(b) if lv.get("order") is not None), key=lambda x: int(x["order"]))
    refused: dict = {}
    gi = next((i for i, lv in enumerate(ordered) if gl is not None and lv["id"] == gl["id"]), None)

    def follow(levels: list, out: dict) -> None:
        shift = 0.0
        for lv in levels:
            old = float(lv.get("elevation") or 0.0)
            if lv["id"] in proposed and lv["id"] not in refused:
                shift = proposed[lv["id"]][1] - old
                out[lv["id"]] = proposed[lv["id"]][1]
            elif lv.get("elevation_source") in (None, "assumed_default"):
                out[lv["id"]] = old + shift            # an assumed level follows the moved level next to it
            else:
                shift = 0.0
                out[lv["id"]] = old

    def final_z(across: bool = False) -> dict:
        """19 Nov 2026 (review A3, A3C-2: a basement mark '-2.80' moved every plan mark by -0.20 because the ground
        floor would follow it): an assumed level follows the moved level next to it towards the ground floor: above it
        the one below, below it the one above; never across the ground floor (``across`` gives the old bottom-up
        reading, the probe of the plans' height frame)."""
        out: dict = {}
        if across or gi is None:
            follow(ordered, out)
        else:
            follow(ordered[gi:], out)
            follow(list(reversed(ordered[:gi])), out)
        return out

    def settle(across: bool) -> dict:
        refused.clear()
        while True:
            z = final_z(across)
            blame: dict = {}
            for a, c in zip(ordered, ordered[1:]):
                step = (z[c["id"]] - z[a["id"]]) / max(1, int(c["order"]) - int(a["order"]))
                if STOREY_MIN_M - tol <= step <= STOREY_MAX_M + tol:
                    continue
                live = [x for x in (a, c) if x["id"] in proposed and x["id"] not in refused]
                if not live:
                    continue
                if len(live) == 1:
                    pick = live[0]
                else:
                    pick = min(live, key=lambda x: (proposed[x["id"]][2][proposed[x["id"]][1]],
                                                    -abs(proposed[x["id"]][1] - float(x.get("elevation") or 0.0))))
                blame.setdefault(pick["id"], []).append((a["id"], c["id"], round(step, 2)))
            if not blame:
                return final_z(across)
            worst = max(blame, key=lambda k: (len(blame[k]), abs(proposed[k][1] - float(proposed[k][0].get("elevation")
                                                                                        or 0.0))))
            refused[worst] = blame[worst]

    z = settle(True)
    s = 0.0
    if gl is not None and gl["id"] in z and (gl["id"] not in proposed or gl["id"] in refused) \
            and not isinstance((b.get("project") or {}).get("datum"), dict):
        s = z[gl["id"]] - float(gl.get("elevation") or 0.0)
    if abs(s) > tol:
        # 19 Nov 2026 (review A3, A3C-2): only when the ground floor's own floor or threshold marks read s
        g_rooms = {r["id"] for r in b.get("rooms") or [] if r.get("level_id") == gl["id"]}
        confirm = [m for m in marks if m.get("z") is not None and abs(float(m["z"]) - s) <= tol and (
            (m.get("kind") in FLOOR_KINDS and m.get("room_id") in g_rooms)
            or (m.get("kind") in ("threshold", "entrance") and m.get("level_id") == gl["id"]))]
        if not confirm:
            warnings.append(f"levels: the levels below the ground floor {gl['id']} moved by their floor marks would carry "
                            f"it {s:+.2f} m, but none of its own floor or threshold marks reads that: it stays, the "
                            f"marks as printed; an assumed level below it follows the moved level above it")
            s = 0.0
    if abs(s) <= tol:
        z = settle(False)
    else:
        # 13 Nov 2026 (round-2 review, A2-FC4 / F3: real11's basements moved by their marks carried the assumed
        # ground floor 2.50 m up): the ground floor stays at its height (building z 0 by convention); a ground floor
        # that would only follow the levels below by s shows the plans' marks in a frame where it stands at s: every
        # relative mark is read as mark - s (the one-frame rule of C0061), the levels with it
        z = {k: _r(v - s) for k, v in z.items()}
        for k in list(proposed):
            lvp, best, counts, zs, rooms = proposed[k]
            proposed[k] = (lvp, round(best - s, 2), {round(c - s, 2): n for c, n in counts.items()},
                           [_r(x - s) for x in zs], rooms)
        n = 0
        for m in marks:
            if m.get("z") is not None and m.get("relative", True) is not False:
                m["z"] = _r(float(m["z"]) - s)
                m["frame_shift"] = _r(float(m.get("frame_shift") or 0.0) + s)
                n += 1
        warnings.append(f"levels: the levels below the ground floor {gl['id']} moved by their floor marks would carry "
                        f"it {s:+.2f} m: the plans' marks stand in a frame with the ground floor at {s:+.2f} m; every "
                        f"plan mark ({n}) is read as mark - {s:.2f} (no section datum)")
        inferred.append({"item": "plan height frame", "value": _r(s),
                         "reason": f"the ground floor would follow the levels below by {s:+.2f} m (one height frame, "
                                   f"C0061)"})
    file = _file_of(b)
    for lv in ordered:
        lid = lv["id"]
        old = float(lv.get("elevation") or 0.0)
        if lid in refused:
            best = proposed[lid][1]
            pairs = "; ".join(f"{x} to {y} {st:+.2f} m a storey" for x, y, st in refused[lid])
            warnings.append(f"level {lid}: its floor marks read {best:+.2f} m, out of the storeys' order (every storey "
                            f"{STOREY_MIN_M:.1f}-{STOREY_MAX_M:.1f} m above the one below; {pairs}): the elevation "
                            f"{old:+.2f} m is kept" + ("" if abs(z[lid] - old) <= tol else
                                                       f" (it follows the level below to {z[lid]:+.2f} m)"))
        new = z[lid]
        if lid in proposed and lid not in refused:
            _lv, best, counts, zs, rooms = proposed[lid]
            why = f"{counts[best]} of {len(zs)} floor marks in its rooms read {best:+.2f}"
            for m in marks:
                if m.get("kind") in FLOOR_KINDS and m.get("room_id") in rooms and m.get("z") is not None \
                        and abs(m["z"] - best) <= tol:
                    _use(m, f"level_elevation:{lid}")
        elif abs(new - old) > tol:
            why = "an assumed level above a level moved by its floor marks, moved by the same amount"
        else:
            continue
        if abs(new - old) > tol:
            warnings.append(f"level {lid}: elevation {old:+.2f} m (assumed) -> {new:+.2f} m ({why})")
            inferred.append({"item": f"level {lid} elevation", "value": _r(new), "reason": why})
            for sl in b.get("slabs") or []:
                if not isinstance(sl, dict) or sl.get("above_level_id") != lid or sl.get("z_top") is None \
                        or abs(float(sl["z_top"]) - new) <= tol:
                    continue
                if sl.get("variants"):
                    # a variant's slab carries that variant's alternative level, which did not move
                    continue
                note = (f"the slab under level {lid} follows it: z_top {float(sl['z_top']):+.2f} -> {new:+.2f} m "
                        f"({why})")
                warnings.append(f"slab {sl.get('id')}: z_top {float(sl['z_top']):+.2f} m -> {new:+.2f} m with level {lid}")
                sl["z_top_before"] = _r(float(sl["z_top"]))
                sl["z_top_source"] = "level_mark"
                sl["z_top"] = _r(new)
                sl.setdefault("evidence", []).append(_evidence(file, "level_elevation", note))
                inferred.append({"item": f"slab {sl.get('id')} z_top", "value": _r(new), "reason": note})
        elif lid in proposed and lid not in refused and lv.get("elevation_source") != "level_mark":
            # 19 Nov 2026 (review A4, SW-A4-05: real07's levels said level_mark while the warnings still said the
            # elevations were assumed): the marks confirm the elevation: said so, the assumption no longer holds
            line = f"level {lid}: elevation {new:+.2f} m confirmed by its floor marks ({why}): no longer assumed"
            warnings.append(line)
            inferred.append({"item": f"level {lid} elevation", "value": _r(new), "reason": line})
        lv["elevation"] = _r(new)
        if lid in proposed and lid not in refused:
            lv["elevation_source"] = "level_mark"     # (a level that only followed stays assumed, listed as inferred)


SHAFT_HEAD_TYPES = ("shaft", "lift", "elevator")    # R01 c: a mark over such a footprint is the shaft head's


def _shaft_heads(b: dict, level: dict, levels: dict) -> list:
    """The footprints (polygons) of the shafts of ``level`` and of the storey under it, air shafts left out (pure;
    R01 c)."""
    below = None
    if level.get("order") is not None:
        below = next((lv["id"] for lv in levels.values() if lv.get("order") is not None
                      and int(lv["order"]) == int(level["order"]) - 1), None)
    return [r["polygon"] for r in b.get("rooms") or [] if r.get("level_id") in (level["id"], below)
            and len(r.get("polygon") or []) >= 3 and (r.get("room_type") in SHAFT_HEAD_TYPES
                                                       or r.get("room_subtype") in SHAFT_HEAD_TYPES)
            and r.get("room_subtype") != "air_shaft"]


def _door_neighbours(b: dict, room: dict) -> list[dict]:
    """The rooms a door or doorless opening joins ``room`` to (pure; R01 c)."""
    rooms = [r for r in b.get("rooms") or [] if r.get("level_id") == room.get("level_id")]
    outline = level_outline(b, room.get("level_id"))
    out = []
    for o in b.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or o.get("type") not in ("door", "opening") or o.get("virtual"):
            continue
        sides = opening_sides(b, o, rooms, outline)
        ids = [r["id"] if r is not None else None for r in (sides or {}).get("rooms") or []]
        if room["id"] in ids:
            out += [r for r in sides["rooms"] if r is not None and r["id"] != room["id"]]
    return out


def _room_floors(b: dict, marks: list, params: dict, conflicts: list, warnings: list) -> None:
    """Step 3: room floor offsets from the floor marks inside them.

    26 Nov 2026 (R01 b, c; real10 L7: the lift machine room took the median of '+23.50' by its door and '+24.70' over
    the lift shaft, a 0.60 m step at its door; real15: every marked room of both storeys stood 0.5 m over the unmarked
    ones): marks that disagree are never averaged. A mark over a shaft's footprint (this storey's or the one under it)
    is the shaft head's, listed, not the room's; of the rest the room floor is the value that equals the level floor,
    else the one value at the floor of a room a door joins it to; when none does, the level floor stays (a
    ``level_mark_mismatch`` either way, never silent). When half or more of a level's marked rooms (two or more, more
    than those at the level floor) share one offset that is not 0, that offset is the level's frame, not a step in each
    room: it is taken off every room of the level, listed (``level_inference.level_frames``).

    27 Nov 2026 (audit H8): a value two or more of a room's marks read, more than any other value, is its floor before
    the mark at the level floor (a sunken living room with a ±0.00 mark at its entry); the level floor decides a tie.
    (audit H2/G4/H7; real13 L-2: its title '2.BODRUM (-3.00 KOTU)' against two '-3.50' room marks): no level frame for a
    storey whose elevation is its own printed storey mark (``printed_storey``) or with a marked room at its floor, and
    only from rooms that hold a main room and most of the storey's floor area (``frame_basis``); a frame taken is a
    ``level_mark_mismatch`` conflict naming the storey's title and the marks, and its rooms say ``floor_source:
    level_frame`` with the marks it overruled (``floor_overruled``)."""
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    tol = float(params["mark_tol"])
    chosen: dict = {}                              # room id -> (z, the marks used, reference elevation)
    agreed: dict = {}                              # room id -> the floor its marks agree on (the neighbours' check)
    for m in marks:
        if m.get("kind") in FLOOR_KINDS and m.get("z") is not None and m.get("room_id"):
            agreed.setdefault(m["room_id"], []).append(float(m["z"]))
    agreed = {k: sum(v) / len(v) for k, v in agreed.items() if max(v) - min(v) <= tol}
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
        # 13 Nov 2026: a typical floor's copy re-reads that floor's marks: the offset is against that floor
        ref = levels.get(lv.get("typical_of")) if lv.get("typical_of") else None
        elev = float((ref or lv)["elevation"])
        zs = [float(m["z"]) for m in own]
        used = list(own)
        z = sum(zs) / len(zs)
        if max(zs) - min(zs) > tol:
            heads = _shaft_heads(b, lv, levels)
            over = [m for m in own if m.get("point") is not None
                    and any(G.point_in_polygon(tuple(m["point"][:2]), poly) for poly in heads)]
            rest = [m for m in own if m not in over] or own
            listed = [f"{m.get('raw') or m['id']} over a shaft's footprint (its head, not the room floor)"
                      for m in over if m not in rest]
            rz = [float(m["z"]) for m in rest]
            if max(rz) - min(rz) <= tol:
                z, used, how = sum(rz) / len(rz), rest, "the marks that agree"
            else:
                values = sorted({round(v, 2) for v in rz})
                # 27 Nov 2026 (audit H8: a sunken living room marked -0.30 twice and ±0.00 at its entry was built flat):
                # a value most of the room's marks read (two or more, more than any other value) is its floor; the mark
                # at the level floor decides a tie
                tally = sorted(((sum(1 for x in rz if abs(x - v) <= tol), v) for v in values), reverse=True)
                pick, how = (None, "")
                if tally[0][0] >= 2 and (len(tally) < 2 or tally[0][0] > tally[1][0]):
                    pick, how = tally[0][1], f"the value most of its marks read ({tally[0][0]} of {len(rz)})"
                at_floor = [v for v in values if abs(v - elev) <= tol]
                if pick is None and at_floor:
                    pick, how = at_floor[0], "the mark at the level floor"
                if pick is None:
                    near = {round(agreed.get(r["id"], float(levels.get(r.get("level_id"), lv)["elevation"])), 2)
                            for r in _door_neighbours(b, room)}
                    fit = [v for v in values if any(abs(v - n) <= tol for n in near)]
                    pick, how = (fit[0], "the mark at the floor of a room a door joins it to") if len(fit) == 1 \
                        else (None, "")
                if pick is None:
                    z, used, how = elev, [], "none of them is the level floor or a neighbour's: the level floor kept"
                else:
                    used = [m for m in rest if abs(float(m["z"]) - pick) <= tol]
                    z = sum(float(m["z"]) for m in used) / len(used)
                listed += [f"{m.get('raw') or m['id']} ({float(m['z']):+.2f} m)" for m in rest if m not in used]
            conflicts.append({"kind": "level_mark_mismatch", "element_ids": [room["id"]] + [m["id"] for m in own],
                              "description": f"{room['id']}: the floor marks inside it read "
                                             f"{', '.join(f'{v:+.2f}' for v in zs)} m",
                              "resolution": f"never averaged: {how} ({z:+.2f} m) used"
                                            + (f"; listed: {'; '.join(listed)}" if listed else "")})
            if not used:
                warnings.append(f"{room['id']}: its floor marks disagree ({', '.join(f'{v:+.2f}' for v in zs)} m): "
                                f"the level floor is kept, listed")
                continue
        chosen[room["id"]] = (z, used, elev)
    # R01 b: a shared offset of most marked rooms of a level is its frame (27 Nov 2026, audit H2/G4: never for a storey
    # whose elevation is its own printed storey mark, never when a marked room reads the level floor, and only from
    # rooms that hold a main room and most of the storey's floor area)
    per_level: dict = {}
    for room in b.get("rooms") or []:
        if room["id"] in chosen:
            per_level.setdefault(room["level_id"], []).append(room)
    frames = {}
    for lid, rooms in per_level.items():
        offs = [round(chosen[r["id"]][0] - chosen[r["id"]][2], 2) for r in rooms]
        # a mark further off the floor than ``room_offset_max`` is no room floor (a roof's, a landing's): no frame
        cands = sorted({o for o in offs if tol < abs(o) <= float(params["room_offset_max"])})
        if not cands:
            continue
        top = max(cands, key=lambda o: (sum(1 for x in offs if abs(x - o) <= tol), -abs(o)))
        n = sum(1 for x in offs if abs(x - top) <= tol)
        zero = sum(1 for x in offs if abs(x) <= tol)
        if not (n >= 2 and n * 2 >= len(offs) and n > zero):
            continue
        lv = levels.get(lid) or {}
        at = [r for r, x in zip(rooms, offs) if abs(x - top) <= tol]
        if printed_storey(lv):
            refuse = (f"its elevation is its own printed storey mark ({lv.get('elevation_source')}"
                      + (f", {lv['elevation_rule']}" if lv.get("elevation_rule") else "") + ")")
        elif zero:
            refuse = f"{zero} marked room(s) read its floor"
        else:
            ok, refuse = frame_basis(b, lid, at)
            refuse = None if ok else refuse
        if refuse is not None:
            warnings.append(f"level {lid}: {n} of its {len(offs)} marked rooms stand {top:+.2f} m off its floor: no "
                            f"frame ({refuse}); each keeps its own step")
            continue
        _ok, basis = frame_basis(b, lid, at)
        frames[lid] = top
        marks_at = [m for r in at for m in chosen[r["id"]][1]]
        warnings.append(f"level {lid}: {n} of its {len(offs)} marked rooms stand {top:+.2f} m off its floor ({basis}): "
                        f"the level's frame, not a step in each room; taken off every room of {lid}")
        b.setdefault("level_inference", {}).setdefault("level_frames", {})[lid] = {"value": top, "rooms": n,
                                                                                     "of": len(offs)}
        conflicts.append({"kind": "level_mark_mismatch", "element_ids": [lid] + [m["id"] for m in marks_at][:12],
                          "description": f"level {lid} ('{_title_of(lv)}') stands at {float(lv.get('elevation') or 0):+.2f} m "
                                         f"({lv.get('elevation_source')}), {n} of its {len(offs)} marked rooms read "
                                         f"{top:+.2f} m off it ({', '.join(str(m.get('raw') or m['id']) for m in marks_at[:6])})",
                          "resolution": f"the level's frame: {top:+.2f} m taken off every marked room of {lid} ({basis}); "
                                        f"those rooms at the level floor (floor_source level_frame, the marks overruled)"})
    for room in b.get("rooms") or []:
        if room["id"] not in chosen:
            continue
        z, used, elev = chosen[room["id"]]
        frame = frames.get(room["level_id"], 0.0)
        offset = z - elev - frame
        if abs(offset) > float(params["room_offset_max"]):
            warnings.append(f"{room['id']}: floor mark {z:+.2f} m is {offset:+.2f} m off its level floor (more than "
                            f"{float(params['room_offset_max']):.2f} m): not the room floor, listed")
            continue
        room["floor_offset_m"] = _r(offset)
        room["floor_source"] = "mark"
        room["floor_evidence"] = [e for m in used for e in _mark_ev(m)][:4]
        if frame and abs(offset) <= tol:
            # 27 Nov 2026 (audit H7): the level's frame overruled its marks: said so on the room
            room["floor_source"] = "level_frame"
            room["floor_overruled"] = [{"mark_id": m["id"], "raw": m.get("raw"), "z": _r(float(m["z"]))} for m in used]
            room["floor_frame"] = _r(frame)
            for m in used:
                _use(m, "level_frame")
            continue
        if frame:
            room["floor_frame"] = _r(frame)
        for m in used:
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


GROUND_GATE_M = 0.05      # R01 e: the ground never stands more than this over the plinth top, a threshold, a garage
FRAME_PLINTH_MAX_M = 1.5  # R01: the plans' ±0.00 is the ground only this far under the ground floor at most


def frame_zero(b: dict, gl: dict) -> Optional[float]:
    """The plans' ±0.00 in the model's frame when the one height frame (``_set_frame_once``) moved the marks and it lies
    under the ground floor by at most ``FRAME_PLINTH_MAX_M``; else None (pure)."""
    rec = (b.get("level_inference") or {}).get("frame")
    if not frame_counts(rec):           # 27 Nov 2026 (audit H4): R01 a's frame only, never the assumed floor's
        return None
    fz = -float(rec["value"])
    drop = float(gl.get("elevation") or 0.0) - fz
    return _r(fz) if 0.0 < drop <= FRAME_PLINTH_MAX_M else None


def _ground_gate(b: dict, marks: list, gl: dict, outline, points: list, params: Optional[dict] = None) -> Optional[dict]:
    """26 Nov 2026 (R01 e; real15: the ground read from three terrace marks stood 0.5 m over the ground floor, its
    entrance 0.15 m under the ground): ``{"why", "limit", "limit_from", "frame_zero", "refused", "kept"}`` when every
    usable ground mark (``points``) stands more than ``GROUND_GATE_M`` over the lowest of the plinth top (its SB. mark,
    else the ground floor's floor) and the ground floor's outside door thresholds: a building is never sunk into its
    ground (a sloping site keeps marks under the floor on its low side and passes); ``frame_zero``: the plans' ±0.00 in
    the model's frame when a height frame was applied and it lies under that limit, else None. None when the marks pass
    (pure).

    27 Nov 2026 (audit H3: a garage sunk under the garden, reached by its own drive, refused the whole drawn sloping
    ground): a garage's floor and doors (``is_garage_door``, a garage room) and a door with a drawn ramp are no limit:
    they have their own drive or ramp down. The marks are refused only when they would bury a door: the terrain they
    make (``terrain.fit_surface`` as ``_ground`` fits it, else the nearest mark) stands over a limiting door's
    threshold in front of it (a site sloping down to its door keeps its marks); with no such door, when they all stand
    over the plinth top. The default ground the gate leaves is held to the same limit (``_ground``)."""
    elev = float(gl.get("elevation") or 0.0)
    sb = [float(m["z"]) for m in marks if m.get("kind") == "plinth" and m.get("z") is not None]
    lim = [(min(sb), "the plinth top (its SB. mark)") if sb else (elev, f"the floor of {gl['id']} (the plinth top)")]
    rooms = {r["id"]: r for r in b.get("rooms") or [] if r.get("level_id") == gl["id"]}
    ramps = {r.get("door_id") for r in (b.get("site") or {}).get("drawn_ramps") or [] if isinstance(r, dict)}
    rooms_l = list(rooms.values())
    doors = []
    for d in outside_doors(b, [gl], outline, outlines_of(b)):
        o = next((x for x in b.get("openings") or [] if x.get("id") == d["id"]), {})
        sides = opening_sides(b, o, rooms_l, outlines_of(b).get(gl["id"]) or outline) if o else None
        room = next((r for r in (sides or {}).get("rooms") or [] if r is not None), None)
        if d["level_id"] != gl["id"] or d["id"] in ramps or is_garage_door(o, room) or \
                (room is not None and room.get("room_type") == "garage"):
            continue                                       # its own drive or ramp down (audit H3)
        doors.append(d)
    if doors:
        d = min(doors, key=lambda x: (x["threshold"], x["id"]))
        lim.append((float(d["threshold"]), f"the threshold of the outside door {d['id']}"))
    top, what = min(lim, key=lambda x: (x[0], x[1]))
    low = min(float(m["z"]) for m in points)
    if low <= top + GROUND_GATE_M:
        return None
    buried = _buried_doors(points, doors, params) if doors else []
    if doors and not buried:
        return None                                        # the marks' terrain falls to every door: they stay
    bury = ""
    if buried:
        d, z = buried[0]
        bury = f"; their terrain stands at {z:+.2f} m in front of the door {d['id']} (threshold {float(d['threshold']):+.2f} m)"
    fz = frame_zero(b, gl)
    if fz is not None and fz > top + GROUND_GATE_M:
        fz = None
    why = (f"every ground mark ({len(points)}, the lowest {low:+.2f} m) stands more than {GROUND_GATE_M:.2f} m over "
           f"{what} ({top:+.2f} m){bury}: a building is never sunk into its ground; those marks are refused (listed), "
           f"the ground comes from the section's ground line, else the plans' ±0.00"
           + (f" ({fz:+.2f} m)" if fz is not None else "") + ", else the default, never over that limit")
    return {"why": why, "limit": _r(top), "limit_from": what, "frame_zero": None if fz is None else _r(fz),
            "refused": [m["id"] for m in points], "buried": [d["id"] for d, _z in buried]}


def _buried_doors(points: list, doors: list, params: Optional[dict]) -> list:
    """The doors (with the ground there) the terrain of the ground marks ``points`` buries: over the door's threshold
    by more than ``GROUND_GATE_M`` 0.3 m in front of its face (pure; audit H3). The terrain: the plane or the TIN of
    three or more marks (``terrain.fit_surface``, the residual and blend of ``params``), else the nearest mark."""
    pts = [(float(m["point"][0]), float(m["point"][1]), float(m["z"])) for m in points]
    surf = None
    if len(pts) >= 3:
        surf = T.fit_surface(pts, plane_residual=float((params or {}).get("plane_residual") or 0.10),
                             blend_m=float((params or {}).get("terrain_blend") or 20.0))
        if surf.get("kind") not in ("planar", "tin"):
            surf = None
    out = []
    for d in doors:
        x = float(d["face"][0]) + float(d["outward"][0]) * 0.3
        y = float(d["face"][1]) + float(d["outward"][1]) * 0.3
        z = T.surface_z(surf, x, y) if surf is not None else min(pts, key=lambda q: math.hypot(q[0] - x, q[1] - y))[2]
        if z > float(d["threshold"]) + GROUND_GATE_M:
            out.append((d, _r(z)))
    return out


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
                    and not g.get("from_frame") and (g.get("z") or {}).get("method") not in (None, "assumed")]
    file = _file_of(b)
    cand, notes = [], []
    for m in marks:
        if m.get("kind") not in GROUND_KINDS or m.get("z") is None or m.get("copy_of"):
            continue                              # (R03-05) a storey copy's re-read marks are never the ground's
        if m.get("note") or m.get("point") is None:
            notes.append(m)
            continue
        p = tuple(m["point"])
        if len(outline) >= 3 and G.point_in_polygon(p, outline):
            warnings.append(f"{m['id']}: ground mark {m.get('raw')} inside the building outline: not used")
            continue
        if len(outline) >= 3 and _dist_to_polygon(p, outline) > float(params["ground_reach"]) \
                and not m.get("site_plan"):
            continue                              # another drawing on the sheet (classified unknown by the reader)
        cand.append(m)
    force = (ground.get("terrain_override") or {}).get("kind")     # the agent's set_terrain (edits.py)
    points, rejected = [], []
    if cand:
        # 19 Nov 2026 (review A3, OA3-08: once the upper storeys' copies of the street's '+2.50' were no ground, real13's
        # street marks on its ground floor's plan fell 4 m off the median its basements' garden marks set, on a steep
        # site): a mark is an outlier against the median of its own plan's ground marks (the plans of a sloping site
        # print the ground of their own side)
        by_plan: dict = {}
        for m in cand:
            by_plan.setdefault(m.get("level_id"), []).append(m["z"])
        for m in cand:
            med = _median(by_plan[m.get("level_id")])
            if abs(m["z"] - med) > float(params["ground_outlier"]) and not m.get("site_plan"):
                rejected.append(m)
                warnings.append(f"{m['id']}: ground mark {m.get('raw')} ({m['z']:+.2f} m) is more than "
                                f"{float(params['ground_outlier']):.1f} m from the median of its plan's ground marks "
                                f"({med:+.2f} m): listed, not used")
            else:
                points.append(m)
    gate = _ground_gate(b, marks, gl, outline, points, params) if points and force is None else None
    if gate is not None:
        rejected += [m for m in points if m["id"] in gate["refused"]]
        points = [m for m in points if m["id"] not in gate["refused"]]
        warnings.append(f"levels: {gate['why']}")
        b.setdefault("level_inference", {})["ground_gate"] = gate
    ground["points"] = [{"x": _r(m["point"][0], 4), "y": _r(m["point"][1], 4), "z": _r(m["z"]),
                         "kind": m["kind"], "mark_id": m["id"], "inferred": False, "used": m not in rejected,
                         "evidence": _mark_ev(m)} for m in points + rejected]
    if gate is not None and not points and not drawn_levels and gate.get("frame_zero") is not None:
        # R01 e: no section ground line: the ground at the printed ±0.00 of the plans' frame
        drawn_levels = [{"side": "all", "azimuth_deg": None, "from_frame": True, "frame_why": "ground_gate",
                         "z": {"value": _r(gate["frame_zero"]), "method": "derived", "confidence": 0.5,
                               "evidence": [_evidence(file, "ground_gate", gate["why"])],
                               "note": f"the plans' ±0.00 in the model's frame ({gate['frame_zero']:+.2f} m): {gate['why']}"}}]
        inferred.append({"item": "site.ground", "value": _r(gate["frame_zero"]), "reason": gate["why"]})
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
        source = "frame" if drawn_levels[0].get("from_frame") else "section"
    fz = frame_zero(b, gl) if source is None else None
    if fz is not None:
        # R01 a/e: nothing about the ground drawn, but the plans' height frame (``_set_frame_once``) puts their ±0.00
        # under the ground floor: the ground stands there (real15: the section's ±0.00 ground, the floor at '+0.50')
        why = (f"no ground drawn; the plans' marks stand in a frame where the ground floor {gl['id']} reads "
               f"{float(gl['elevation']) - fz:+.2f} m: the ground at their ±0.00 ({fz:+.2f} m)")
        # 27 Nov 2026 (audit H9): its own rule and reason (no ground mark was refused on this path)
        drawn_levels = [{"side": "all", "azimuth_deg": None, "from_frame": True, "frame_why": "plan_frame_zero",
                         "z": {"value": _r(fz), "method": "derived", "confidence": 0.5,
                               "evidence": [_evidence(file, "plan_frame_zero", why)], "note": why}}]
        source = "frame"
        inferred.append({"item": "site.ground", "value": _r(fz), "reason": why})
    if source is None:
        z = float(gl["elevation"]) - float(params["ground_rise"])
        note = (f"D3a: nothing about the ground is drawn: the ground floor stands {float(params['ground_rise']):.2f} m "
                f"above it (one inferred step)")
        if gate is not None and z > float(gate["limit"]) + GROUND_GATE_M:
            # 27 Nov 2026 (audit H3): the default is held to the gate's own limit (never over the lowest door)
            z = float(gate["limit"])
            note = (f"D3a held to the ground gate's limit: the ground at {gate['limit_from']} ({z:+.2f} m), never over "
                    f"it (the refused marks stood over it)")
        drawn_levels = [{"side": "all", "azimuth_deg": None,
                         "z": {"value": _r(z), "method": "assumed", "confidence": 0.0, "evidence": [], "note": note}}]
        source = "D3a"
        inferred.append({"item": "site.ground", "value": _r(z),
                         "reason": note if gate is not None else
                         f"D3a: no ground drawn: {float(params['ground_rise']):.2f} m under {gl['id']}"})
    ground["levels"] = drawn_levels
    zs = {round(float(g["z"]["value"]), 3) for g in drawn_levels}
    if surface is None:
        flat_z = next(iter(zs)) if len(zs) == 1 else (sum(zs) / len(zs) if zs else 0.0)
        surface = T.fit_surface([], flat_z=flat_z, blend_m=float(params["terrain_blend"]))
        surface["kind"] = "flat" if len(zs) <= 1 else "sides"
        frame_why = drawn_levels[0].get("frame_why") if drawn_levels else None
        surface.update(inferred=source in ("D3a", "frame"), source=source,
                       reason={"D3a": "nothing about the ground drawn (D3a)", "site_note": "the site note's level",
                               "section": "the drawn ground lines per side", "marks": "ground marks per side",
                               "frame": ("the plans' ±0.00 (no ground drawn: the plans' height frame)"
                                         if frame_why == "plan_frame_zero" else
                                         "the plans' ±0.00 (the ground marks stood over the floor: refused)")}[source])
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


def outside_doors(b: dict, levels: list, outline, outlines: dict) -> list[dict]:
    """The outside doors of the base levels (pure; 26 Oct 2026, for ``wenart.levels.outdoor``): ``[{"id",
    "level_id", "face", "outward", "threshold", "width"}]`` (the face of the wall on the outside, the threshold as
    ``_entrances`` reads it)."""
    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    by_id = {lv["id"]: lv for lv in levels}
    out = []
    for o in b.get("openings") or []:
        lv = by_id.get(o.get("level_id"))
        if o.get("type") != "door" or lv is None:
            continue
        sides = opening_sides(b, o, rooms_by.get(lv["id"]) or [], outlines.get(lv["id"]) or outline)
        if sides is None or sum(sides["outside"]) != 1:
            continue
        k = 0 if sides["outside"][0] else 1
        room = sides["rooms"][1 - k]
        n = sides["normal"]
        ow = (n[0], n[1]) if k == 0 else (-n[0], -n[1])
        cx, cy = sides["centre"]
        ht = sides["half_t"]
        threshold = float(o.get("threshold_z") if o.get("threshold_z") is not None else
                          (room_floor_z(b, room) if room else lv["elevation"]))
        out.append({"id": o["id"], "level_id": lv["id"], "face": (cx + ow[0] * ht, cy + ow[1] * ht), "outward": ow,
                    "threshold": threshold, "width": float(o.get("width") or 0.9)})
    return out


FACADE_GAP_WIDTH_M = (0.4, 4.0)     # 3 Nov 2026: the unreadable gaps of an outside wall the facade rule types
FACADE_WINDOW = (0.9, 1.4)          # ... a window's sill and height when the level has no outside window to copy
UNCLEAR_GAP = "unclassified gap content"


OPEN_AIR_ROOMS_RE = re.compile(r"(?<![a-z])(?:balcony|balkon|teras|terrace|loggia|lodjia|veranda|porch|deck|patio)")


def _open_air(room: Optional[dict]) -> bool:
    """19 Nov 2026 (review A4, A4FC-4 / A4C-02): a room open to the air by its type or label (a balcony, a terrace).
    26 Nov 2026 (audit rule R19): or by the build's one shared check (``outdoor.is_open_air``: a light well, an air
    shaft, an open-air flag): its mark is no floor of the storey, its outer gap no facade window."""
    from wenart import building as B
    from wenart.blender import outdoor as OD

    r = room or {}
    return bool(OPEN_AIR_ROOMS_RE.search(B.fold_ascii(f"{r.get('room_type') or ''} {r.get('label') or ''}").lower())) \
        or (bool(r) and OD.is_open_air(r))


ENTRANCE_DROP_MAX_M = 1.2          # 24 Nov 2026: an entrance a few steps over the ground (marks decide the steps)
ENTRANCE_MARK_REACH_M = 1.0        # ... marked by a ground or threshold mark this close outside the gap's face


def entrance_mark(b: dict, level_id: str, face, ow) -> Optional[dict]:
    """A ground or threshold level mark of ``level_id`` within ``ENTRANCE_MARK_REACH_M`` outside the gap face ``face``
    (outward ``ow``) that marks no other door (pure), or None."""
    for m in b.get("level_marks") or []:
        if m.get("level_id") != level_id or not m.get("point") or m.get("door_id") \
                or m.get("kind") not in ("ground_finished", "ground", "threshold"):
            continue
        dx, dy = float(m["point"][0]) - face[0], float(m["point"][1]) - face[1]
        if (dx * dx + dy * dy) ** 0.5 <= ENTRANCE_MARK_REACH_M and dx * ow[0] + dy * ow[1] > -0.05:
            return m
    return None


def facade_gaps(b: dict, levels: list, outline, outlines: dict, spaces: Sequence[dict], tm: dict,
                params: dict) -> list[dict]:
    """3 Nov 2026 (real10, user: "tell me what purple means", then "go ahead"): a gap in an outside wall whose lines no
    rule could read (``UNCLEAR_GAP``), or with nothing drawn in it (purple in the reading's sheets), is typed by what
    lies outside it: onto a drawn
    outdoor space at its floor (a balcony, terrace; ``outdoor.space_doors``' probe) it is a door (the space's door,
    added to its ``doors``); with a drop outside (the ground more than ``flush_max`` under its floor, no space) it is a
    window at the sill and height of the level's outside windows (their median; else ``FACADE_WINDOW``). A gap at
    the ground with nothing drawn outside stays open (the architect's question). The drawn type stays
    (``drawn_type``), ``type_inferred`` keeps the reason; pure apart from ``b`` and ``spaces``. Returns the
    ``inferred`` records."""
    from shapely.geometry import Point

    from wenart.blender import site as S
    from wenart.levels import outdoor as OD

    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    by_id = {lv["id"]: lv for lv in levels}

    def outside(o):
        lv = by_id.get(o.get("level_id"))
        if lv is None:
            return None
        sides = opening_sides(b, o, rooms_by.get(lv["id"]) or [], outlines.get(lv["id"]) or outline)
        if sides is None or sum(sides["outside"]) != 1:
            return None
        k = 0 if sides["outside"][0] else 1
        n = sides["normal"]
        ow = (n[0], n[1]) if k == 0 else (-n[0], -n[1])
        cx, cy = sides["centre"]
        face = (cx + ow[0] * sides["half_t"], cy + ow[1] * sides["half_t"])
        return lv, sides["rooms"][1 - k], face, ow

    typical: dict = {}
    for o in b.get("openings") or []:
        if o.get("type") == "window" and o.get("sill_height") is not None and o.get("height") and outside(o):
            typical.setdefault(o["level_id"], []).append((float(o["sill_height"]), float(o["height"])))
    every = [x for v in typical.values() for x in v]
    out = []
    for o in b.get("openings") or []:
        # an unclear gap, or an empty one (nothing drawn in it: "possible undrawn door or window"; real10's facade gaps
        # once the dimension marks crossing them were left out, UL296)
        if o.get("type") != "opening" or o.get("virtual") or o.get("drawn_type") \
                or not FACADE_GAP_WIDTH_M[0] <= float(o.get("width") or 0.0) <= FACADE_GAP_WIDTH_M[1]:
            continue
        # a gap that holds another opening of its wall (real06: a 1.95 m gap around the drawn 0.70 m balcony door)
        # is that opening's leftover, never a second door or window
        held = [x for x in b.get("openings") or [] if x is not o and x.get("wall_id") == o.get("wall_id")
                and x.get("type") in ("door", "window") and not x.get("virtual") and x.get("center") and o.get("center")
                and G.distance(x["center"], o["center"]) < (float(x.get("width") or 0.0)
                                                           + float(o.get("width") or 0.0)) / 2.0 - 0.05]
        if held:
            continue
        # 12 Nov 2026 (review B2 FC-01, real06 L1: the rest of the 1.95 m balcony gap beside its drawn door was typed a
        # second door): the part of a gap a drawn door left (evidence ``rest_of``) is that door's leftover too
        if any(isinstance(e, dict) and e.get("rest_of") for e in o.get("evidence") or []):
            continue
        side = outside(o)
        if side is None:
            continue
        lv, room, face, ow = side
        if room is None:
            continue                     # no room of the house behind it: not a facade opening of a room
        if _open_air(room):
            continue                     # 19 Nov 2026 (review A4, A4FC-4): a balcony's open edge, never a window
        probe = (face[0] + ow[0] * OD.SPACE["door_probe"], face[1] + ow[1] * OD.SPACE["door_probe"])
        floor = room_floor_z(b, room)
        onto = None
        for sp in spaces:
            if sp.get("level_id") == lv["id"] and len(sp.get("polygon") or []) >= 3 \
                    and OD._shp(sp["polygon"]).distance(Point(probe)) <= OD.SPACE["door_reach"]:
                onto = sp
                break
        drop = floor - float(S.ground_z(tm, *probe))
        if onto is not None:
            o["drawn_type"], o["type"] = "opening", "door"
            if o.get("height") is None:
                o["height"] = 2.1
            why = (f"a gap with unreadable lines in the outside wall onto the {onto.get('kind')} {onto['id']} "
                   f"('{onto.get('label')}') at its floor: its door")
            if o["id"] not in (onto.get("doors") or []):
                onto.setdefault("doors", []).append(o["id"])
        elif drop <= ENTRANCE_DROP_MAX_M and entrance_mark(b, lv["id"], face, ow) is not None:
            # 24 Nov 2026 (review of f706c8a1: real17's shop 7 entrance 'DÜKKAN GİRİŞİ' became a window once the ground
            # stood in the drawing's frame): a gap at the floor a few steps over the ground with a level mark of the
            # ground or a threshold right outside it (no building corner: the drawing marks the entrance's level) is
            # an entrance door; its steps follow from the marks
            mk = entrance_mark(b, lv["id"], face, ow)
            o["drawn_type"], o["type"] = "opening", "door"
            if o.get("height") is None:
                o["height"] = 2.1
            why = (f"a gap with unreadable lines in the outside wall {drop:.2f} m over the ground, the level mark "
                   f"{mk.get('raw')} ({mk['id']}) right outside it: an entrance door")
        elif drop > float(params["flush_max"]):
            rows = sorted(typical.get(lv["id"]) or every)
            sill, height = rows[len(rows) // 2] if rows else FACADE_WINDOW
            o["drawn_type"], o["type"] = "opening", "window"
            o["drawn_sill_height"], o["drawn_height"] = o.get("sill_height"), o.get("height")
            o["sill_height"], o["height"] = round(sill, 3), round(height, 3)
            for k in ("swing_side", "operation", "operation_source", "threshold_z"):
                o.pop(k, None)
            why = (f"a gap with unreadable lines in the outside wall, {drop:.2f} m over the ground outside and no "
                   f"balcony or terrace drawn there: a window (sill {sill:.2f} m, height {height:.2f} m, "
                   + ("the level's windows)" if typical.get(lv["id"]) else
                      "the building's windows)" if rows else "the default)"))
        else:
            continue
        o["type_inferred"] = {"method": "facade_gap", "reason": why}
        out.append({"item": f"opening {o['id']}", "value": o["type"], "reason": why})
    return out


def keep_completion_entrances(b: dict, old: list) -> None:
    """The completion's entrance decisions after the levels model rebuilt ``site.entrances`` (13 Nov 2026, review
    CODE-01: an accepted agent level edit re-runs ``wenart.levels.model.infer_levels``, which brought back refused
    doors with steps and picked a new main entrance; the same merge as the levels model's records, CS1-04). Once the
    completion has run (``level_inference.core_rules.entrances``): a door it refused (``entrance_refused``) has no
    record, the records it inferred (rule ``inferred_entrance``) stay as written, and the main entrance is the one it
    left in ``old`` (the records before the rebuild), or none when it left none. Mutates ``b``."""
    if not isinstance(((b.get("level_inference") or {}).get("core_rules") or {}).get("entrances"), dict):
        return                                    # the reading's own first run: the completion has not decided yet
    site = b.get("site")
    if not isinstance(site, dict):
        return
    doors = {o["id"]: o for o in b.get("openings") or [] if o.get("type") == "door"}
    ents = [e for e in site.get("entrances") or [] if e.get("door_id") in doors
            and not doors[e["door_id"]].get("entrance_refused")]
    have = {e.get("door_id") for e in ents}
    for e in old or []:
        if any((ev or {}).get("rule") == "inferred_entrance" for ev in e.get("evidence") or []) and \
                e.get("door_id") in doors and e.get("door_id") not in have:
            ents.append(copy.deepcopy(e))
            have.add(e.get("door_id"))
    main = next((e for e in old or [] if e.get("main") and e.get("door_id") in have), None)
    for e in ents:
        if main is not None and e.get("door_id") == main.get("door_id"):
            e["main"], e["main_reason"] = True, main.get("main_reason") or e.get("main_reason")
        elif e.get("main"):
            e["main"] = False
            e.pop("main_reason", None)
    site["entrances"] = ents


def _entrances(b: dict, marks: list, params: dict, levels: list, outline, outlines: dict, tm: dict,
               ground_points: list, conflicts: list, warnings: list, spaces: Sequence[dict] = ()) -> list[dict]:
    """Step 6: ``site.entrances``. 26 Oct 2026: a door that opens onto a labelled outdoor space (``spaces``,
    ``wenart.levels.outdoor``: its ``doors``) lands on it: no steps or landing of its own (``solution`` none,
    ``onto`` the space; the space's own edge and steps lead down); an upper floor's door onto a balcony is no door
    into the air."""
    from wenart.blender import site as S

    file = _file_of(b)
    onto = {d: s for s in spaces for d in s.get("doors") or []}
    gl0 = ground_level(b)
    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    ids = {lv["id"] for lv in levels}
    lowered = {i for ch in tm.get("changes") or [] for i in ch.get("opening_ids") or []}
    ramp_doors = {r.get("door_id") for r in (b.get("site") or {}).get("drawn_ramps") or [] if isinstance(r, dict)}
    ramp_shapes = {r.get("door_id"): r for r in (b.get("site") or {}).get("drawn_ramps") or []
                   if isinstance(r, dict) and r.get("length") and r.get("width")}
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
        landing_mark = None
        for m in marks:
            # 26 Oct 2026: a landing mark of another level's plan is not this door's (real06: the upper floor's
            # "+3,50" made two ground-floor doors "doors into the air")
            if m.get("level_id") not in (None, lv["id"]):
                continue
            if m.get("kind") in ("threshold", "entrance") and m.get("point") is not None and m.get("z") is not None \
                    and G.distance(face, m["point"]) <= float(params["door_mark_reach"]) + float(o.get("width") or 0):
                if landing_mark is None or G.distance(face, m["point"]) < G.distance(face, landing_mark["point"]):
                    landing_mark = m
        near = [m for m in ground_points if G.distance(probe, m["point"]) <= float(params["door_ground_reach"])]
        # 13 Nov 2026 (coordinator, real13: "a building's entrance never disappears"; the 1st basement's entrance door,
        # its plan printing '-0.50' at its threshold, read 3.00 m below a '+2.50' ground mark of an upper floor's plan):
        # the door's own plan speaks first: its ground marks, else the threshold mark it prints at the door (the
        # outside landing there), and only then the marks of the other plans
        own = [m for m in near if m.get("level_id") in (None, lv["id"])]
        if near and o["id"] not in lowered and not own and landing_mark is not None and landing_mark.get("kind") == "threshold":
            gz, gsrc = float(landing_mark["z"]), (f"the threshold mark {landing_mark['id']} its own plan prints at the "
                                                 f"door (no ground mark of that plan within reach)")
        elif own and o["id"] not in lowered:
            # 19 Nov 2026 (review A3, OA3-08: real14's ground-floor door took the ground of a roof-terrace mark): never
            # another plan's ground mark; without one of its own plan the door stands on the terrain
            m = min(own, key=lambda m: G.distance(probe, m["point"]))
            gz, gsrc = float(m["z"]), f"ground mark {m['id']}"
            _use(m, f"entrance:{o['id']}")
        else:
            gz, gsrc = S.ground_z(tm, *probe), ("terrain lowered to the door (basement door)" if o["id"] in lowered
                                               else f"terrain ({tm['kind']})")
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
        elif is_garage_door(o, room):
            # 12 Nov 2026 (real07, user correction C0045 "a car should be able to enter and exit"; the levels gave its
            # sectional door steps 0.50 m high): a garage door's entrance is a drive down to the ground, never steps
            rec["ramp"] = drive_for(rise, width, params)
            rec["solution"] = "drive"
            rec["reason"] = (f"{rise:.2f} m above the ground ({gsrc}): a garage door: a drive {rec['ramp']['ratio']} "
                             f"{rec['ramp']['length']:.2f} m straight out, {rec['ramp']['width']:.2f} m wide (inferred)")
            shape = ramp_shapes.get(o["id"])
            if shape is not None and rec["ramp"] is not None:
                # 12 Nov 2026 (round-2 review, A2-FC9; CLAUDE.md: ramps are inferred only where not drawn): a drawn
                # ramp outline in front of the door gives the drive its length, width and place (its own slope)
                ln, wd = float(shape["length"]), float(shape["width"])
                ax, ay = shape["apex"]
                shift = (ax - face[0]) * -outward[1] + (ay - face[1]) * outward[0]
                slope = max(rise, 0.0) / ln
                rec["ramp"].update(slope=_r(slope, 4), ratio=f"1:{max(1, round(1.0 / slope)):d}" if slope > 0 else "flat",
                                   length=_r(ln), width=_r(wd), shift=_r(shift, 4), drawn=True,
                                   outline=[list(p) for p in shape["polygon"]])
                rec["drawn"] = True
                rec["inferred"] = False
                rec["evidence"] += [dict(e) for e in shape.get("outline_evidence") or shape.get("evidence") or []][:1]
                rec["reason"] = (f"{rise:.2f} m above the ground ({gsrc}): a garage door: the drawn ramp in front of it, "
                                 f"{ln:.2f} m long and {wd:.2f} m wide (slope {slope:.2f})")
            elif o["id"] in ramp_doors:
                rec["drawn"] = True
                rec["reason"] += "; a drawn ramp in front of the door"
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
        space = onto.get(o["id"])
        if space is not None:
            upper = gl0 is not None and float(lv["elevation"]) > float(gl0["elevation"]) + 0.5
            how = ("a slab with a guard on its open edges" if space.get("elevated") else
                   "its own edge and steps lead down to the ground" if float(space["z"]) - gz > float(params["flush_max"])
                   else "at the ground")
            rec.update(solution="none", steps=None, ramp=None, landing=None, into_air=False, below_ground=False,
                       upper_floor=upper, onto=space["id"],
                       reason=f"opens onto the {space['kind']} {space['id']} ('{space.get('label')}') at "
                              f"{float(space['z']):+.2f} m: the {space['kind']} is its landing ({how}); no steps of "
                              f"its own (inferred)")
        agent = overrides.get(o["id"])
        if isinstance(agent, dict) and not rec["into_air"] and not rec["below_ground"] and space is None \
                and rec["solution"] != "drive":
            _apply_entrance_override(rec, agent, max(rise, 0.0), top, width, params)
        elif isinstance(agent, dict):
            # 12 Nov 2026 (round-2 review, BP7: a stored override met a door that cannot take one, e.g. a door that
            # became a garage door's drive after a later edit; nothing changes silently)
            why = ("a garage door's drive" if rec["solution"] == "drive" else "a door into the air" if rec["into_air"]
                   else "below the ground" if rec["below_ground"] else f"opens onto {space['id']}")
            warnings.append(f"entrance override of {o['id']} ({agent.get('solution')}) not applied: the door is {why}")
        rec["evidence"].append(_evidence(file, "entrance", rec["reason"]))
        out.append(rec)
    # The main entrance (26 Oct 2026, main_entrance): the door a visitor uses, not the widest garden door.
    usable = [e for e in out if not e["into_air"] and not e["below_ground"] and not e.get("upper_floor")]
    if usable:
        main, why = main_entrance(b, usable, marks)
        main["main"] = True
        main["main_reason"] = why
        if brief_ramp and main["solution"] == "steps":   # (a drive is no steps)
            rise = main["rise"]
            main["ramp"] = ramp_for(rise, params)
            main["solution"] = "steps_and_ramp"
            main["reason"] += f"; brief levels.accessible_entrance: a ramp {main['ramp']['ratio']} (inferred)"
    return out


# 26 Oct 2026 (real06: the 2.95 m sliding garden door was the main entrance, as the widest door of the main facade;
# the small swing door beside it in the same corner is the house's door): the main entrance is chosen by what the
# door is. A hinged door 0.80-1.30 m wide (0.75 m counts: the architect's D1 widens an outside door to 0.80 m; a
# double leaf up to 1.60 m) is an entrance door; a door wider than 1.60 m is a garden or terrace door.
MAIN_DOOR_WIDTH = (0.75, 1.30)
MAIN_DOUBLE_MAX = 1.60
GARDEN_DOOR_MIN = 1.60
HINGED = (None, "swing", "double", "unknown")          # building.schema: operation null = swing (assumed)


# 3 Nov 2026 (real10, user: "this should be the main entrance to the building, find a way to figure out the main
# enterences"; "Understanding the building starts with the stairs in the shaft"): in a building with a stair core the
# main entrance is the outside door reached from the core: the stair core, the shared hall it opens into and the halls
# joined to them through openings (at most CORE_PATH_HOPS rooms from the core); a door into one of those rooms ranks
# right after a door the documents mark, whatever its width up to CORE_DOOR_MAX (a double entrance door)
CORE_PATH_HOPS = 3
CORE_DOOR_MAX = 3.2
JOIN_REACH_M = 0.55              # = twins.SHARED_HALL_REACH_M (core walls run 0.4-0.8 m thick)


def core_path(b: dict, level_id: Optional[str]) -> dict:
    """``{room id: hops}``: the rooms of ``level_id`` reached from its stair core (rooms whose ``label_inferred``
    method is ``stair_core`` or ``shared_hall``) through openings joining hall rooms, at most ``CORE_PATH_HOPS`` (pure)."""
    from shapely.geometry import Point, Polygon

    rooms = [r for r in b.get("rooms") or [] if isinstance(r, dict) and r.get("level_id") == level_id
             and len(r.get("polygon") or []) >= 3]
    start = [r for r in rooms if (r.get("label_inferred") or {}).get("method") in ("stair_core", "shared_hall")]
    if not start:
        return {}
    polys = {r["id"]: Polygon(r["polygon"]) for r in rooms}
    pts = [Point(o["center"][:2]) for o in b.get("openings") or [] if isinstance(o, dict)
           and o.get("level_id") == level_id and o.get("center")]
    hops = {r["id"]: 0 for r in start}
    frontier = list(hops)
    while frontier:
        nxt = []
        for rid in frontier:
            if hops[rid] >= CORE_PATH_HOPS:
                continue
            here = polys[rid]
            near = [q for q in pts if here.distance(q) <= JOIN_REACH_M]
            for r in rooms:
                if r["id"] in hops or r.get("room_type") not in ("hall", "stair", "unknown"):
                    continue
                if any(polys[r["id"]].distance(q) <= JOIN_REACH_M for q in near):
                    hops[r["id"]] = hops[rid] + 1
                    nxt.append(r["id"])
        frontier = nxt
    return hops


def main_tier(e: dict, opening: Optional[dict], room: Optional[dict], marked: bool,
              core_hops: Optional[int] = None) -> tuple[int, str]:
    """``(tier, reason)`` of an entrance for the main entrance (pure; lower is better): 0 a door marked as the
    entrance in the documents (a GIRIS / entrance mark); 1 a door into a room reached from the stair core
    (``core_path``, ``core_hops``); 2 a hinged entrance-size door into a hall, entry, corridor or stair room; 3 such a
    door into another room (not a garage or a service room); 4 any other door up to ``GARDEN_DOOR_MIN``; 5 a wider
    (garden or terrace) door."""
    from wenart.blender import site as S

    w = float(e.get("width") or 0.0)
    op = (opening or {}).get("operation")
    role = S.room_role(room)
    into = (f"the {room.get('room_type') or 'room'} {room['id']}" if isinstance(room, dict) and room.get("id")
            else "the building")
    what = f"{e['door_id']}, a {w:.2f} m {op or 'swing'} door into {into}"
    if marked:
        return 0, f"{what}: marked as the entrance in the documents"
    if core_hops is not None and op in HINGED + ("sliding", "folding") and MAIN_DOOR_WIDTH[0] - 1e-6 <= w <= \
            CORE_DOOR_MAX + 1e-6:
        return 1, (f"{what}: the outside door reached from the stair core ({core_hops} room(s) from it through the "
                   f"shared halls): the building's main entrance (inferred)")
    size = op in HINGED and (MAIN_DOOR_WIDTH[0] - 1e-6 <= w <= MAIN_DOOR_WIDTH[1] + 1e-6
                             or (op == "double" and MAIN_DOOR_WIDTH[0] - 1e-6 <= w <= MAIN_DOUBLE_MAX + 1e-6))
    if size and role == "hall":
        return 2, f"{what}: a hinged entrance door into a hall (inferred)"
    if size and role in (None, "room"):
        return 3, f"{what}: no entrance door into a hall; a hinged entrance-size door into a room (inferred)"
    if w <= GARDEN_DOOR_MIN + 1e-6:
        return 4, f"{what}: no hinged entrance door into a hall or a room; the next door up to " \
                  f"{GARDEN_DOOR_MIN:.2f} m (inferred)"
    return 5, f"{what}: only garden or terrace doors (over {GARDEN_DOOR_MIN:.2f} m) lead outside (inferred)"


def main_entrance(b: dict, usable: Sequence[dict], marks: Sequence[dict]) -> tuple[dict, str]:
    """The main entrance among the usable ``site.entrances`` records (pure; 26 Oct 2026): the best ``main_tier``,
    then a door of the main facade (the side with the most entrances), then the widest, then by id. Returns the
    record and the reason (kept on the record as ``main_reason``)."""
    from wenart.blender import site as S

    counts: dict = {}
    for e in usable:
        counts[S.nearest_axis(e["outward"])] = counts.get(S.nearest_axis(e["outward"]), 0) + 1
    order = ("-y", "+y", "-x", "+x")
    axis = max(counts, key=lambda a: (counts[a], -order.index(a)))
    ops = {o.get("id"): o for o in b.get("openings") or [] if isinstance(o, dict)}
    rooms = {r.get("id"): r for r in b.get("rooms") or [] if isinstance(r, dict)}
    paths = {lid: core_path(b, lid) for lid in {e.get("level_id") for e in usable}}
    ranked = []
    for e in usable:
        marked = any(m.get("kind") == "entrance" and e["door_id"] in " ".join(m.get("used_for") or []) for m in marks)
        hops = (paths.get(e.get("level_id")) or {}).get(e.get("room_id"))
        tier, why = main_tier(e, ops.get(e["door_id"]), rooms.get(e.get("room_id")), marked, hops)
        # among the doors reached from the core, the one nearest the ground (the entrance storey; real10: the 1st
        # basement's front door, not a door of the shared hall a storey up)
        near_ground = float(e.get("rise") or 0.0) if tier == 1 else 0.0
        # 3 Nov 2026 (real10): a door the plan draws beats a gap whose type was inferred (``facade_gaps``: a 2.86 m
        # terrace gap of a hall the walls left open won on its width over the drawn 2.40 m double front door)
        o = ops.get(e["door_id"]) or {}
        guessed = bool(o.get("type_inferred")) or (o.get("drawn_type") not in (None, o.get("type")))
        ranked.append(((tier, round(near_ground, 2), guessed, S.nearest_axis(e["outward"]) != axis,
                        -float(e["width"]), str(e["door_id"])), e, why))
    ranked.sort(key=lambda x: x[0])
    _key, main, why = ranked[0]
    if len(ranked) > 1:
        why += f"; {len(ranked) - 1} other outside door(s): " + ", ".join(
            f"{e['door_id']} (tier {k[0]})" for k, e, _w in ranked[1:])
    return main, why


GARAGE_DOOR_TYPES = ("garage_sectional", "garage", "garage_door", "sectional", "roller", "up_and_over")


def is_garage_door(o: dict, room: Optional[dict]) -> bool:
    """Whether an outside door is a garage door (pure; 12 Nov 2026): its ``door_type`` is a garage door's, or it leads
    into a garage room (``blender.site.room_role``) and a car passes it (``twins.GARAGE_DOOR_MIN_M``, the reader's and the
    architect's one width; round-2 review BP5). The one predicate of the levels, the site and the model review."""
    from wenart.blender import site as S
    from wenart.ingest.twins import GARAGE_DOOR_MIN_M

    if str(o.get("door_type") or "").lower() in GARAGE_DOOR_TYPES:
        return True
    return S.room_role(room) == "garage" and float(o.get("width") or 0.0) >= GARAGE_DOOR_MIN_M - 1e-6


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
    # 13 Nov 2026 (review CS1-04): the model owns only its own keys; the records the completion rules wrote
    # (storeys, core_rules, sense_rules, the party walls, rules_off ...) stay; the conflicts are copied again
    old = building.get("level_inference")
    kept = {k: copy.deepcopy(v) for k, v in old.items() if k not in MODEL_KEYS} if isinstance(old, dict) else {}
    b["level_inference"] = record = dict(kept, **record)
    gl = ground_level(b)
    if gl is None:
        return b
    record["ground_floor"] = gl["id"]
    _storey_vs_stairs(b, marks, params, conflicts, inferred, warnings)       # 23 Nov 2026 (stairs round, UL376)
    _level_elevations(b, marks, params, inferred, warnings, conflicts,
                      (old or {}).get("frame") if isinstance(old, dict) else None)
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
    from wenart.blender import site as S

    levels = base_levels(b)
    outline = BB.ground_outline(b, outlines)
    if len(outline) < 3:
        warnings.append("no closed outline at the ground: no ground, entrances or plinth inferred")
        return b
    g = _ground(b, marks, params, gl, outline, inferred, warnings)
    record["ground_source"] = g["source"]
    tm = terrain_for(b, levels, BB.ground_outline(b, outlines), outlines)
    site = b["site"]
    # 26 Oct 2026 (real06): the drawn site symbols are typed, the labelled outdoor spaces of every level get their
    # outline, floor, doors, steps and cover (wenart.levels.outdoor); a door onto a space lands on it
    from wenart.levels import outdoor as OD
    OD.type_site_decor(b, outline)
    doors = outside_doors(b, levels, outline, outlines)
    site["outdoor_spaces"] = OD.outdoor_spaces(b, levels, outlines, marks, doors,
                                               lambda x, y: S.ground_z(tm, x, y), inferred, warnings)
    OD.mark_decor_used(b, site["outdoor_spaces"])
    inferred += OD.decor_summary(b)
    # 3 Nov 2026 (real10): the outside walls' unreadable gaps: a door onto a drawn balcony or terrace, a window over a
    # drop (before the entrances, so a balcony door lands on its balcony)
    inferred += facade_gaps(b, levels, outline, outlines, site["outdoor_spaces"], tm, params)
    site["entrances"] = _entrances(b, marks, params, levels, outline, outlines, tm, g["points"], conflicts, warnings,
                                   spaces=site["outdoor_spaces"])
    # 13 Nov 2026 (review CODE-01): the completion's entrance decisions stay
    keep_completion_entrances(b, copy.deepcopy((building.get("site") or {}).get("entrances") or []))
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
