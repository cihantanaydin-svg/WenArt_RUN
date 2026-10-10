"""Level checks L1–L7 (docs/milestone12.md §3.5, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``CHECKS``: ``("L1", ..., "L7")``.
- ``check_levels(building: dict, scene_manifest: dict | None = None, render_manifest: dict | None = None)
  -> list[Violation]`` with ``Violation = {"check", "severity", "target", "room_id", "message", "metrics"}``
  (the M11 format); pure, no I/O; L7 needs the manifests and is skipped without them.

What each check measures (on the building JSON as ``wenart.levels.model.infer_levels`` leaves it; the terrain is the
build's own, ``wenart.blender.site.terrain_model`` with the basement doors' side changes):

| Check | Rule | Severity |
|---|---|---|
| L1 | an outside door: the landing top = its threshold, the steps reach the ground, a flush door's ground = its threshold, each within ``mark_tol`` (a flush door within ``flush_max``); a door below the ground outside (not lowered by the build) | critical |
| L2 | a door more than ``flush_max`` above the ground in front with no steps or ramp (every rise; above ``door_into_air`` a door into the air) | critical |
| L3 | a level floor more than 0.05 m below the terrain at its outline that is not a basement; a basement window below the ground without a light well or court | critical |
| L4 | the built floors (room floors, level floors), the ground, the plinth and the landings vs every vector level mark, within ``mark_tol`` | major |
| L5 | entrance steps: riser ``riser_min_outdoor``-``riser_max_outdoor``, tread >= ``tread_min``, ``step_rule`` on 2R + T; ramps within the slope table; inner steps riser <= ``riser_max_indoor`` | major |
| L6 | a terrain surface steeper than 1:3 (no retaining edge is built); a window of a level that is not a basement with its sill under the ground outside and no light well | major |
| L7 | every entrance is seen by >= 1 exterior view (``visible_openings``); when the view lists its objects (``visible_objects``), its steps or ramp are among them | minor |

Why: the agent's critic and edit validator (track A) and the tests measure the levels the same way the build makes
them; a check never guesses (an item the inputs cannot measure is not reported).
"""
from __future__ import annotations

import math
from typing import Optional

CHECKS: tuple[str, ...] = ("L1", "L2", "L3", "L4", "L5", "L6", "L7")
SEVERITY = {"L1": "critical", "L2": "critical", "L3": "critical", "L4": "major", "L5": "major", "L6": "major",
            "L7": "minor"}
MAX_TERRAIN_SLOPE = 1.0 / 3.0
BELOW_TOL_M = 0.05


def _v(check: str, target, message: str, room_id=None, severity: Optional[str] = None, **metrics) -> dict:
    return {"check": check, "severity": severity or SEVERITY[check], "target": target, "room_id": room_id,
            "message": message, "metrics": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in metrics.items()}}


def _ctx(building: dict) -> Optional[dict]:
    """The terrain, outlines and levels the checks measure on (None for a building without a closed outline)."""
    from wenart.blender import build as BB
    from wenart.levels import model as M

    levels = M.base_levels(building)
    if not levels:
        return None
    outlines = M.outlines_of(building)
    outline = BB.ground_outline(building, outlines)
    if len(outline) < 3 or not isinstance(building.get("site"), dict):
        return {"levels": levels, "outlines": outlines, "outline": outline, "tm": None}
    tm = M.terrain_for(building, levels, outline, outlines)
    return {"levels": levels, "outlines": outlines, "outline": outline, "tm": tm}


def _gz(ctx: dict, x: float, y: float) -> Optional[float]:
    from wenart.blender import site as S

    return None if ctx.get("tm") is None else S.ground_z(ctx["tm"], x, y)


def _l1_l2_l5(building: dict, params: dict, out: list) -> None:
    from wenart.levels import model as M

    tol = float(params["mark_tol"])
    flush = float(params["flush_max"])
    for e in (building.get("site") or {}).get("entrances") or []:
        if not isinstance(e, dict):
            continue
        did = e.get("door_id")
        thr, gz = float(e.get("threshold_z") or 0.0), float(e.get("ground_z") or 0.0)
        rise = thr - gz
        sol = e.get("solution") or "none"
        if e.get("below_ground") or (rise < -flush and not e.get("terrain_lowered")):
            out.append(_v("L1", did, f"door {did}: its threshold {thr:+.2f} m is {-rise:.2f} m below the ground in "
                                     f"front ({gz:+.2f} m): a door into the ground", threshold_z=thr, ground_z=gz))
            continue
        if sol == "none":
            if rise > float(params["door_into_air"]) or e.get("into_air"):
                # an upper floor's door to the outside may be a French balcony or a balcony not drawn: major
                out.append(_v("L2", did, f"door {did} is {rise:.2f} m above the ground with no steps or ramp: a door "
                                         f"into the air (an outside stair, or no entrance)"
                              + ("; on an upper floor (a French balcony?)" if e.get("upper_floor") else ""),
                              severity="major" if e.get("upper_floor") else None, rise=rise))
            elif rise > flush:
                out.append(_v("L2", did, f"door {did} is {rise:.2f} m above the ground in front with no steps or ramp",
                              rise=rise))
            continue
        landing = e.get("landing") or {}
        if landing.get("z") is not None and abs(float(landing["z"]) - thr) > tol:
            out.append(_v("L1", did, f"door {did}: the landing top {float(landing['z']):+.2f} m is "
                                     f"{abs(float(landing['z']) - thr):.2f} m off its threshold {thr:+.2f} m",
                          landing_z=float(landing["z"]), threshold_z=thr))
        top = float(landing.get("z", thr))
        st = e.get("steps")
        if st:
            bottom = top - int(st["count"]) * float(st["riser"])
            if abs(bottom - gz) > tol:
                out.append(_v("L1", did, f"door {did}: the steps end {bottom:+.2f} m, the ground is {gz:+.2f} m",
                              steps_bottom=bottom, ground_z=gz))
            r, t = float(st["riser"]), float(st["tread"])
            lo, hi = float(params["riser_min_outdoor"]), float(params["riser_max_outdoor"])
            rule = params["step_rule"]
            problems = []
            low_single = int(st["count"]) == 1 and r < lo - 1e-6     # one low step: the whole rise is under a riser
            if not lo - 1e-6 <= r <= hi + 1e-6 and not low_single:
                problems.append(f"riser {r:.3f} m outside {lo:.2f}-{hi:.2f} m")
            if t < float(params["tread_min"]) - 1e-6:
                problems.append(f"tread {t:.2f} m under {float(params['tread_min']):.2f} m")
            if int(st["count"]) > 1 and not float(rule[0]) - 1e-6 <= 2 * r + t <= float(rule[1]) + 1e-6:
                problems.append(f"2R + T = {2 * r + t:.3f} m outside {float(rule[0]):.2f}-{float(rule[1]):.2f} m")
            if problems:
                out.append(_v("L5", did, f"entrance steps of {did}: " + "; ".join(problems), riser=r, tread=t,
                              rule_2r_t=2 * r + t))
            elif low_single:
                out.append(_v("L5", did, f"entrance of {did}: one {r:.2f} m step (lower than {lo:.2f} m: a trip risk; "
                                         f"a ramp would do)", severity="minor", riser=r))
        ramp = e.get("ramp")
        if ramp:
            want = M.ramp_for(max(rise, 0.0), params)
            if want and float(ramp.get("slope") or 1.0) > float(want["slope"]) + 1e-4:
                out.append(_v("L5", did, f"ramp of {did}: slope {float(ramp['slope']):.3f} steeper than "
                                         f"{want['ratio']} for a {rise:.2f} m rise", slope=float(ramp["slope"]),
                              max_slope=float(want["slope"])))
    for s in (building.get("level_inference") or {}).get("inner_steps") or []:
        if float(s.get("riser") or 0.0) > float(params["riser_max_indoor"]) + 1e-6:
            limit = float(params["riser_max_indoor"])
            out.append(_v("L5", s.get("opening_id"), f"inner step at {s.get('opening_id')}: riser "
                                                     f"{float(s['riser']):.3f} m over {limit:.2f} m",
                          riser=float(s["riser"])))


def _is_basement(level: dict, ground_floor: Optional[dict]) -> bool:
    from wenart import building as B

    return level.get("kind") == "basement" or "BODRUM" in B.fold_ascii(str(level.get("label") or "")).upper() or \
        (ground_floor is not None and float(level["elevation"]) < float(ground_floor["elevation"]) - 0.5)


def _windows_below(building: dict, ctx: dict, levels: list) -> list[tuple[dict, dict, float, float]]:
    """Outside windows of ``levels`` whose sill is more than 5 cm under the ground outside:
    ``[(opening, level, bottom, ground)]``."""
    from wenart.blender import site as S

    out = []
    for rec in S.outer_openings(building, levels, ctx["outline"], ctx["outlines"], kinds=("window",)):
        cx, cy = rec["centre"]
        ox, oy = rec["outward"]
        gz = _gz(ctx, cx + ox * (rec["half_t"] + 0.3), cy + oy * (rec["half_t"] + 0.3))
        if gz is not None and rec["bottom"] < gz - BELOW_TOL_M:
            out.append((rec["opening"], rec["level"], rec["bottom"], gz))
    return out


def _wells(building: dict) -> set:
    ids = set()
    for w in ((building.get("site") or {}).get("ground") or {}).get("light_wells") or []:
        if isinstance(w, dict):
            ids.add(w.get("opening_id"))
            ids.update(w.get("opening_ids") or [])
    return ids


def _l3_l6(building: dict, ctx: dict, params: dict, out: list) -> None:
    from wenart.levels import model as M

    if ctx.get("tm") is None:
        return
    gl = M.ground_level(building)
    for lv in ctx["levels"]:
        outline = ctx["outlines"].get(lv["id"]) or []
        if len(outline) < 3 or _is_basement(lv, gl):
            continue
        cx = sum(p[0] for p in outline) / len(outline)
        cy = sum(p[1] for p in outline) / len(outline)
        top = None
        for p in outline:
            d = math.hypot(p[0] - cx, p[1] - cy) or 1.0
            z = _gz(ctx, p[0] + (p[0] - cx) / d * 0.3, p[1] + (p[1] - cy) / d * 0.3)
            top = z if top is None else max(top, z)
        if top is not None and float(lv["elevation"]) < top - BELOW_TOL_M:
            out.append(_v("L3", lv["id"], f"level {lv['id']} (floor {float(lv['elevation']):+.2f} m) lies "
                                          f"{top - float(lv['elevation']):.2f} m below the terrain at its outline and is "
                                          f"not a basement", floor_z=float(lv["elevation"]), terrain_z=top))
    wells = _wells(building)
    below = _windows_below(building, ctx, ctx["levels"])
    for o, lv, bottom, gz in below:
        if o["id"] in wells:
            continue
        if _is_basement(lv, gl):
            out.append(_v("L3", o["id"], f"basement window {o['id']} ({lv['id']}): sill {bottom:+.2f} m under the "
                                         f"ground {gz:+.2f} m and no light well or court", sill_z=bottom, ground_z=gz))
        else:
            out.append(_v("L6", o["id"], f"window {o['id']} ({lv['id']}): sill {bottom:+.2f} m under the terrain "
                                         f"{gz:+.2f} m outside and no light well", sill_z=bottom, ground_z=gz))
    surface = ((building.get("site") or {}).get("ground") or {}).get("surface") or {}
    if surface.get("kind") in ("planar", "tin") and float(surface.get("slope") or 0.0) > MAX_TERRAIN_SLOPE + 1e-6:
        out.append(_v("L6", "terrain", f"the terrain slopes up to 1:{1.0 / float(surface['slope']):.1f} (steeper than "
                                       f"1:3) and no retaining edge is built", slope=float(surface["slope"])))


def _l4(building: dict, ctx: dict, params: dict, out: list) -> None:
    from wenart.levels import model as M

    tol = float(params["mark_tol"])
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    ents = {e.get("door_id"): e for e in site.get("entrances") or [] if isinstance(e, dict)}
    for m in building.get("level_marks") or []:
        if not isinstance(m, dict) or m.get("z") is None:
            continue
        if not any(e.get("method") == "vector" for e in m.get("evidence") or []):
            continue
        z = float(m["z"])
        kind = m.get("kind")
        built, what = None, None
        if kind in ("floor", "entrance") and m.get("room_id") in rooms:
            room = rooms[m["room_id"]]
            level_z = float((levels.get(room["level_id"]) or {}).get("elevation") or 0.0)
            if room.get("room_type") in M.NO_FLOOR_ROOMS or abs(z - level_z) > float(params["room_offset_max"]):
                continue                              # a stair landing or another floor's mark (listed by the reader)
            built, what = M.room_floor_z(building, room), f"the floor of {room['id']}"
        elif kind == "slab_top" and m.get("level_id") in levels and m.get("placement") == "section":
            built, what = float(levels[m["level_id"]]["elevation"]), f"the floor of {m['level_id']}"
        elif kind in ("ground_natural", "ground_finished", "slope_top") and ctx.get("tm") is not None:
            if m.get("point") is not None and not m.get("note"):
                if len(ctx["outline"]) >= 3 and M._dist_to_polygon(tuple(m["point"]), ctx["outline"]) > \
                        float(params["ground_reach"]):
                    continue
                built, what = _gz(ctx, *m["point"]), "the ground there"
            else:
                zs = [float(g["z"]["value"]) for g in (site.get("ground") or {}).get("levels") or []
                      if (g.get("z") or {}).get("value") is not None]
                if zs:
                    built = min(zs, key=lambda v: abs(v - z))
                    what = "the drawn ground level"
        elif kind == "plinth" and isinstance(site.get("plinth"), dict):
            built, what = float(site["plinth"]["top_z"]), "the plinth top"
        elif kind in ("threshold", "entrance") and m.get("door_id") in ents:
            e = ents[m["door_id"]]
            built = float((e.get("landing") or {}).get("z", e.get("threshold_z")))
            what = f"the landing of {m['door_id']}"
        if built is None:
            continue
        if abs(built - z) > tol:
            out.append(_v("L4", m["id"], f"level mark {m.get('raw')!r} ({m['id']}, {kind}) reads {z:+.2f} m; "
                                         f"{what} is built at {built:+.2f} m ({abs(built - z):.2f} m apart)",
                          room_id=m.get("room_id"), mark_z=z, built_z=built))


def _l7(building: dict, scene_manifest: Optional[dict], render_manifest: Optional[dict], out: list) -> None:
    cams = []
    for man in (scene_manifest, render_manifest):
        for c in (man or {}).get("cameras") or []:
            if isinstance(c, dict) and c.get("kind") == "exterior" and not c.get("dropped") \
                    and all(c.get("name") != x.get("name") for x in cams):
                cams.append(c)
        for r in (man or {}).get("renders") or []:
            if isinstance(r, dict) and r.get("kind") == "exterior" and all(r.get("name") != x.get("name")
                                                                           for x in cams):
                cams.append(r)
    for e in (building.get("site") or {}).get("entrances") or []:
        if not isinstance(e, dict) or e.get("into_air") or e.get("below_ground"):
            continue
        did = e.get("door_id")
        seen = [c for c in cams if did in (c.get("visible_openings") or [])]
        if not seen:
            out.append(_v("L7", did, f"entrance {did} is seen by no exterior view", views=len(cams)))
            continue
        if e.get("solution") in ("steps", "ramp", "steps_and_ramp"):
            listed = [c for c in seen if isinstance(c.get("visible_objects"), list)]
            names = {f"steps_{did}", f"ramp_{did}"}
            if listed and not any(names & set(c["visible_objects"]) for c in listed):
                out.append(_v("L7", did, f"the steps / ramp of entrance {did} are in none of the views that see it "
                                         f"({', '.join(c.get('name') or '?' for c in listed)})"))


def check_levels(building: dict, scene_manifest: Optional[dict] = None,
                 render_manifest: Optional[dict] = None) -> list[dict]:
    """L1–L7 (module docstring); pure."""
    from wenart.levels import model as M

    params = M.level_params(M._brief_of(building, None))
    out: list[dict] = []
    if not isinstance(building, dict) or not building.get("levels"):
        return out
    ctx = _ctx(building)
    if ctx is None:
        return out
    _l1_l2_l5(building, params, out)
    _l3_l6(building, ctx, params, out)
    _l4(building, ctx, params, out)
    if scene_manifest is not None or render_manifest is not None:
        _l7(building, scene_manifest, render_manifest, out)
    return out
