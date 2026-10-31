"""A fridge never stands on or inside a kitchen counter run (pure; no geometry library: the model review runs it in
Blender).

31 Oct 2026 (user on real04 run 20261030-181158-full, the basement kitchen views cam_r_L-1_mutfak_1/2/3: "There can
not be a fridge inside the kitchen counter! make this a rule. The kitchen can be built around the fridge, (kitchen
counter ends and continues, if there is a place on top of the fire some sections can be included) but not over the
kitchen counter"; the open kitchen of the variant l-1b-acik-mutfak: "Again fridge inside the kitchen counter"; the
French-door fridge in the tall-unit column beside the oven tower: "Fridge here was making sense").

How the fridges got onto the counters (the general cause): the completion built an under-counter fridge into a drawn
counter (``solver.built_in_kitchen``: f_L-1_090 into f_L-1_004, f_L-1b_076 into f_L-1b_010 and their mirror twins).
The fit's kitchen details (UL187, ``fit.kitchen_details_hints``) then gave the kitchen its full-size fridge in the
tall-unit column of another run and cleared the old run's fridge hints, so the old run built a cupboard there. Nothing
held the moved piece: the fit fitted it on its own as a freestanding library fridge (a 1.64 m HSSD model on a 0.82 m
piece: the type's height range allows it) and the scene built that model at the piece's old place, inside the run's
base units, its top 0.74 m over the worktop: a second fridge on the counter beside the column's French-door fridge.

The rule (every project; real04 is only the test case):

1. A fridge (``proxies.FLOOR_APPLIANCE_TYPES``) stands on the floor: never hung (the build ignores a
   ``mount_bottom_m`` on it: ``proxies.mount_bottom``), never on a worktop.
2. A fridge or a tall piece (``RUN_SPLIT_TYPES``) in a counter run is either held by the run (the tall-unit column,
   the fridge column at a run end, the integrated under-counter unit: the run's own fronts, no model of its own,
   ``plan["built_ins"]``) or stands on the floor in a gap of the run (``gap_entry``: no base unit, plinth or worktop
   over its span; the run ends at the fridge and continues past it, ``plan["gaps"]``). A wall run over it stops at
   it (``fit.wall_run_hints``); sections over a fridge are allowed (the column's cupboard over its doors).
3. One fridge per kitchen unless the documents draw more: an added fridge the tall-unit column replaces is held by
   that column (``built_ins`` record ``column: True``, ``moved_from``) and never built again as a model of its own.
4. The check (``findings``) flags any fridge or tall piece (drawn, added, library, module or parametric) built with
   a model of its own whose footprint overlaps a run's built part (the plan's worktop, units and plinth; the whole
   footprint of a run without a module plan) by ``OVERLAP_MIN_M`` along and across (``in_run``), and any fridge
   whose base is over its floor (``off_floor``: a ``mount_bottom_m``, or the built box over the room's floor). The
   fit applies the planner's fix before the build (``fit.fit_building``: the column holds the moved fridge, else
   the old run takes it back, else the run leaves a gap at it) and logs every finding and fix in
   ``project["fridge_rule"]``; the model review reads the built model (M13 ``fridge_in_run``).
"""
from __future__ import annotations

from typing import Optional, Sequence

from wenart.blender.proxies import FLOOR_APPLIANCE_TYPES

RULE = ("a fridge never stands on or inside a kitchen counter run: it stands on the floor, in the tall-unit column "
        "or at a run end; where it meets a run the run ends at it and continues past it (no worktop under or over "
        "it); one fridge per kitchen unless the documents draw more (user, 31 Oct 2026)")
# The pieces a run is split around (a fridge-freezer is a ``fridge``: the schema has no freezer type; a tall housing
# standing in a run is a ``tall_cabinet``).
RUN_SPLIT_TYPES: tuple[str, ...] = FLOOR_APPLIANCE_TYPES + ("tall_cabinet",)
RUN_HOST_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
OVERLAP_MIN_M = 0.03      # S2's fixture tolerance: a piece reaching this far into a run along and across overlaps it
FLOOR_TOL_M = 0.01        # S1's floor gap tolerance: a base this far over the floor is off the floor
BUILT_RUN_KINDS: tuple[str, ...] = ("worktop", "base_unit", "filler", "plinth", "tall_unit", "waterfall")
GUARD_ROUNDS = 3          # the fit's guard re-checks after each fix (a column refused, a run refitted)


def _run_size(run: dict) -> Optional[tuple[float, float]]:
    fp = run.get("footprint") or {}
    try:
        w, d = float(fp["size"][0]), float(fp["size"][1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    return (w, d) if w > 0 and d > 0 else None


def run_overlap(run: dict, piece: dict) -> Optional[dict]:
    """The part of ``piece``'s footprint inside ``run``'s footprint, in the run's frame: ``{"x0_m", "x1_m"}`` (its
    extent along the run, inside the run), ``depth_m`` (across) and ``share`` (of the piece's footprint); None when
    it reaches less than ``OVERLAP_MIN_M`` into the run along or across (a piece that only meets the run)."""
    from wenart.blender import modules as MOD

    size = _run_size(run)
    corners = MOD._local_corners(run, piece)
    if size is None or corners is None:
        return None
    full = MOD._area(corners)
    inside = MOD._clip_to_box(corners, size[0] / 2.0, size[1] / 2.0)
    if full <= 1e-12 or len(inside) < 3:
        return None
    xs, ys = [p[0] for p in inside], [p[1] for p in inside]
    x0, x1, depth = min(xs), max(xs), max(ys) - min(ys)
    if x1 - x0 < OVERLAP_MIN_M - 1e-9 or depth < OVERLAP_MIN_M - 1e-9:
        return None
    return {"x0_m": round(x0, 4), "x1_m": round(x1, 4), "depth_m": round(depth, 4),
            "share": round(MOD._area(inside) / full, 4)}


def gap_entry(run: dict, piece: dict, overlap: dict, reason: str) -> dict:
    """The ``module_hints["ranges"]`` entry of the gap a run leaves for ``piece`` (``modules._range_gaps``): its
    span along the run (``overlap``), reaching the run's end when the stretch left beyond it is narrower than a
    filler panel (``modules.KITCHEN_FILLER_MAX_M``: the run ends at the fridge, no sliver of worktop beside it); a
    gap at a run end may be narrow (``min_m``: the run stops short of a fridge that reaches into its end)."""
    from wenart.blender import modules as MOD

    w = _run_size(run)[0]
    x0, x1 = float(overlap["x0_m"]), float(overlap["x1_m"])
    if x0 + w / 2.0 < MOD.KITCHEN_FILLER_MAX_M - 1e-9:
        x0 = -w / 2.0
    if w / 2.0 - x1 < MOD.KITCHEN_FILLER_MAX_M - 1e-9:
        x1 = w / 2.0
    at_end = abs(x0 + w / 2.0) < 1e-6 or abs(x1 - w / 2.0) < 1e-6
    return {"id": str(piece.get("id")), "type": str(piece.get("type")), "x0_m": round(x0, 4), "x1_m": round(x1, 4),
            "reason": reason, "fridge_rule": True, **({"min_m": OVERLAP_MIN_M} if at_end else {})}


def gap_reason(piece: dict, run: dict) -> str:
    """The words of a gap the rule makes (the plan's gap record and the fit report carry them)."""
    return (f"{piece.get('type')} {piece.get('id')} stands on the floor: the run {run.get('id')} ends at it and "
            "continues past it, no worktop under or over it (adjusted_by_ai; the run's drawn footprint is kept; "
            "fridge rule of 31 Oct 2026)")


def built_spans(run: dict) -> list[tuple[float, float, str]]:
    """``(x0, x1, kind)`` along ``run`` (its frame) where it is built: the worktop, units, plinth, tall units and
    waterfall ends of its module plan; the whole footprint for a run without one (a library or parametric counter,
    or before the fit)."""
    size = _run_size(run)
    if size is None:
        return []
    plan = ((run.get("asset") or {}).get("module_plan") or {}) if isinstance(run.get("asset"), dict) else {}
    if plan.get("builder") != "kitchen_run" or not plan.get("modules"):
        return [(-size[0] / 2.0, size[0] / 2.0, "footprint")]
    out = []
    for m in plan["modules"]:
        if m.get("kind") not in BUILT_RUN_KINDS:
            continue
        try:
            x, mw = float(m["pos_m"][0]), float(m["size_m"][0])
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        out.append((x - mw / 2.0, x + mw / 2.0, str(m["kind"])))
    return out


def held_by(pieces: Sequence[dict]) -> dict[str, str]:
    """``{piece id: run id}`` of the pieces a kitchen run holds (no model of their own): the piece's
    ``asset.built_in`` names the run and the run's module plan lists it under ``built_ins`` (as
    ``furniture.built_in_ids``)."""
    by_id = {p.get("id"): p for p in pieces if isinstance(p, dict)}
    out: dict[str, str] = {}
    for p in by_id.values():
        host_id = (p.get("asset") or {}).get("built_in") if isinstance(p.get("asset"), dict) else None
        host = by_id.get(host_id) if host_id else None
        if host is None or host is p or host.get("build") is False:
            continue
        plan = (host.get("asset") or {}).get("module_plan") or {}
        if any(isinstance(b, dict) and b.get("id") == p.get("id") for b in plan.get("built_ins") or []):
            out[str(p["id"])] = str(host_id)
    return out


def _not_built(piece: dict) -> bool:
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    return piece.get("build") is False or asset.get("method") == "none"


def findings(building: dict, boxes: Optional[dict] = None, floors: Optional[dict] = None) -> list[dict]:
    """The check (module docstring, rule 4): ``[{rule, piece, type, room_id, run?, x0_m?, x1_m?, depth_m?, share?,
    severity, message}]``.

    ``in_run``: a fridge or tall piece (``RUN_SPLIT_TYPES``) built with a model of its own (not held by a run,
    ``held_by``) whose footprint reaches ``OVERLAP_MIN_M`` into a counter run of its level and room (``run_overlap``)
    where the run is built (``built_spans``: the overlap along the run meets them by ``OVERLAP_MIN_M``); a piece the
    completion built into the run (``built_into``) is none before the fit has planned that run (no asset yet).
    ``off_floor``: a fridge with ``mount_bottom_m`` over 0, or, with ``boxes`` (``{piece id: (bottom z, top z)}``:
    the built model's box) and ``floors`` (``{room id: floor z}``), whose built bottom is more than ``FLOOR_TOL_M``
    over its room's floor."""
    pieces = [p for p in building.get("furniture") or [] if isinstance(p, dict)]
    held = held_by(pieces)
    runs = [p for p in pieces if p.get("type") in RUN_HOST_TYPES and not _not_built(p) and _run_size(p)]
    out: list[dict] = []
    for p in pieces:
        if p.get("type") not in RUN_SPLIT_TYPES or _not_built(p) or str(p.get("id")) in held \
                or not isinstance(p.get("footprint"), dict):
            continue
        for run in runs:
            if run.get("level_id") != p.get("level_id") or run.get("room_id") != p.get("room_id"):
                continue
            ov = run_overlap(run, p)
            if ov is None:
                continue
            spans = built_spans(run)
            if p.get("built_into") == run.get("id") and not run.get("asset"):
                continue                                   # before the fit: the completion built it into this run
            hit = max((min(ov["x1_m"], s1) - max(ov["x0_m"], s0) for s0, s1, _k in spans), default=0.0)
            if hit < OVERLAP_MIN_M - 1e-9:
                continue                                   # it stands in a gap of the run (or past its built end)
            out.append({"rule": "in_run", "piece": str(p["id"]), "type": p.get("type"), "room_id": p.get("room_id"),
                        "run": str(run["id"]), **ov, "severity": "critical",
                        "message": f"{p.get('type')} {p['id']} stands inside the counter run {run['id']} ("
                                   f"{ov['x1_m'] - ov['x0_m']:.2f} m along it, {ov['depth_m']:.2f} m deep, "
                                   f"{hit:.2f} m of it where the run is built): {RULE}"})
        if p.get("type") not in FLOOR_APPLIANCE_TYPES:
            continue
        try:
            mount = float(p.get("mount_bottom_m") or 0.0)
        except (TypeError, ValueError):
            mount = 0.0
        lift = mount if mount > FLOOR_TOL_M else None
        box = (boxes or {}).get(p.get("id"))
        if lift is None and box is not None and p.get("room_id") in (floors or {}):
            gap = float(box[0]) - float(floors[p["room_id"]])
            lift = gap if gap > FLOOR_TOL_M + 1e-9 else None
        if lift is not None:
            out.append({"rule": "off_floor", "piece": str(p["id"]), "type": p.get("type"),
                        "room_id": p.get("room_id"), "lift_m": round(lift, 3), "severity": "critical",
                        "message": f"{p.get('type')} {p['id']} stands {lift:.2f} m over its floor: {RULE}"})
    return out


def column_fridge_records(column_spans: Sequence[tuple[float, float, str]], fridges: Sequence[str],
                          moved_from: Optional[dict] = None) -> list[dict]:
    """The ``plan["built_ins"]`` records of the added fridges a run's tall-unit column holds (rule 3): one per piece
    id of ``fridges``, all at the column's fridge unit (its first ``fridge*`` span); none when the column has no
    fridge unit (then nothing holds them and the fit's guard gives them back to their run, or a gap)."""
    unit = next(((c0, c1) for c0, c1, k in column_spans if str(k).startswith("fridge")), None)
    if unit is None:
        return []
    return [{"id": str(pid), "kind": "fridge", "x_m": round((unit[0] + unit[1]) / 2.0, 4),
             "w_m": round(unit[1] - unit[0], 4), "shift_m": 0.0, "column": True, "moved": True,
             **({"moved_from": str((moved_from or {})[pid])} if (moved_from or {}).get(pid) else {})}
            for pid in fridges]
