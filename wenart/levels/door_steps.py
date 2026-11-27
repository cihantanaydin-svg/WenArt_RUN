"""Steps at a door between two floors of different height (27 Nov 2026, audit fix round 5b).

What: ``place(b, inner_steps, params)`` runs after the level model's thresholds (``levels.model._thresholds``: every door
or doorless opening between two rooms whose floors differ by more than ``flush_max`` gives an inner step record). For
each it plans what the build makes (``opening["steps"]``, inferred, listed):

- steps: ``risers`` of ``rise / risers`` (at most ``riser_max_indoor``) and treads of ``tread``; the last riser is the
  threshold in the wall, the others stand as blocks in front of the door on the lower side, inside the lower room (the
  flight's plan inside its outline); the higher room never takes steps (its floor is the door's threshold), so a flight
  that does not fit in the lower room is not built: a difference that cannot be built is a finding;
- a ramp (``drive_slope``) in front of a vehicle door of a garage (``levels.model.is_garage_door``, the lower room a
  garage): cars need a slope, not steps; it must fit inside the garage too.

Every record says where it went and why; the ones that cannot be built are listed (``unbuilt``) with the reason, and
the build keeps its single threshold block for them (``shell.inner_step``).

Why: real15's garage door d_L0_006 joined floors 0.25 m apart and real10's shelter doors d_L-2_001 / d_L-2_004 0.35 m
apart, with no step: the model review found a 0.25-0.35 m wall under the door seen from the lower room (M1).

How: pure geometry (shapely) on the building JSON; the build reads the blocks (``shell.door_step_blocks``).
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import Point, Polygon

from wenart import geometry as G

FIT_TOL_M = 0.02             # a flight's plan may stand this far over its room's outline (a plaster layer)
VEHICLE_DOOR_M = 2.0         # a garage door this wide or wider is a vehicle door (a ramp, never steps)


def _r(v: float, nd: int = 4) -> float:
    return round(float(v), nd) + 0.0


def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    p = Polygon(points)
    p = p if p.is_valid else p.buffer(0)
    return p if not p.is_empty and p.area > 0 else None


def _box(c, u, n, w: float, d0: float, d1: float) -> list:
    """The rectangle ``w`` wide along ``u`` centred on ``c``, from ``d0`` to ``d1`` along ``n``."""
    hw = w / 2.0
    pts = []
    for s, d in ((-hw, d0), (hw, d0), (hw, d1), (-hw, d1)):
        pts.append([_r(c[0] + u[0] * s + n[0] * d), _r(c[1] + u[1] * s + n[1] * d)])
    return pts


def plan(o: dict, wall: dict, low: dict, high: dict, z_low: float, z_high: float, params: dict) -> dict:
    """The steps or ramp of opening ``o`` in ``wall`` from room ``low`` (floor ``z_low``) up to ``high`` (``z_high``):
    ``{"kind": steps | ramp, "room_id", "blocks": [{"polygon", "z0", "z1"}], "risers", "riser", "tread", "run",
    "fits", "reason"}`` (pure). ``fits`` False: the flight does not stand inside the lower room (not built)."""
    from wenart.levels import model as M
    rise = z_high - z_low
    w = float(o.get("width") or 0.9)
    t = float(wall.get("thickness") or 0.2)
    a, b = wall["start"][:2], wall["end"][:2]
    L = math.dist(a, b) or 1.0
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    nrm = (-u[1], u[0])
    c0 = o.get("center") or [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]
    # the opening's centre on the wall's centre line
    k = (c0[0] - a[0]) * u[0] + (c0[1] - a[1]) * u[1]
    c = (a[0] + u[0] * k, a[1] + u[1] * k)
    lp = _poly(low.get("polygon"))
    probe = (c[0] + nrm[0] * (t / 2.0 + 0.05), c[1] + nrm[1] * (t / 2.0 + 0.05))
    if lp is not None and not lp.contains(Point(probe)):
        nrm = (-nrm[0], -nrm[1])
    vehicle = w >= VEHICLE_DOOR_M and (low.get("room_type") == "garage" or M.is_garage_door(o, low))
    face = t / 2.0
    if vehicle:
        slope = float(params.get("drive_slope") or 0.12)
        run = rise / slope
        blocks = [{"polygon": _box(c, u, nrm, w, face, face + run), "z0": _r(z_low), "z1": _r(z_high),
                   "slope_to": "door"}]
        rec = {"kind": "ramp", "slope": _r(slope), "run": _r(run), "risers": 0, "riser": 0.0, "tread": 0.0}
        what = f"a ramp at 1:{round(1.0 / slope):d}, {run:.2f} m long, in front of the vehicle door"
    else:
        st = M.steps_for(rise, w, params, outdoor=False) or {"count": 1, "riser": rise, "tread": 0.30}
        n, riser, tread = int(st["count"]), float(st["riser"]), float(st["tread"])
        blocks = []
        for j in range(1, n):                       # the last riser is the threshold in the wall
            blocks.append({"polygon": _box(c, u, nrm, w, face, face + (n - j) * tread), "z0": _r(z_low),
                           "z1": _r(z_low + j * riser)})
        run = (n - 1) * tread
        rec = {"kind": "steps", "risers": n, "riser": _r(riser), "tread": _r(tread), "run": _r(run)}
        what = (f"{n} risers of {riser:.3f} m ({n - 1} tread block(s) of {tread:.2f} m and the threshold)")
    foot = _poly(_box(c, u, nrm, w, face, face + max(run, 0.01)))
    fits = bool(lp is not None and foot is not None and lp.buffer(FIT_TOL_M).contains(foot))
    rec.update(room_id=low["id"], high_room_id=high["id"], z_low=_r(z_low), z_high=_r(z_high), rise=_r(rise),
               blocks=blocks if fits else [], fits=fits, inferred=True, source="inferred")
    rec["reason"] = (f"{o['id']} joins {low['id']} ({z_low:+.2f}) and {high['id']} ({z_high:+.2f}), {rise:.2f} m apart, "
                     f"no step drawn: {what} inside {low['id']} (the lower room; inferred)" if fits else
                     f"{o['id']} joins {low['id']} ({z_low:+.2f}) and {high['id']} ({z_high:+.2f}), {rise:.2f} m apart, "
                     f"no step drawn: {what} does not fit inside {low['id']}, the lower room ({run:.2f} m in front "
                     f"of the door): not built, listed (a finding)")
    return rec


def place(b: dict, inner_steps: list, params: dict) -> dict:
    """Plans the steps of every inner step record (module docstring) on its opening (``opening["steps"]``, in place)
    and on the record (``placed``, ``reason``). Returns ``{"built": [...], "unbuilt": [...]}``."""
    from wenart.levels import model as M
    ops = {o["id"]: o for o in b.get("openings") or []}
    walls = {w["id"]: w for w in b.get("walls") or []}
    rooms = {r["id"]: r for r in b.get("rooms") or []}
    out = {"built": [], "unbuilt": []}
    for s in inner_steps or []:
        o = ops.get(s.get("opening_id"))
        low = rooms.get(s.get("low_room"))
        if o is None or low is None or walls.get(o.get("wall_id")) is None:
            continue
        wall = walls[o["wall_id"]]
        others = [r for r in rooms.values() if r["id"] != low["id"] and r.get("level_id") == low.get("level_id")]
        lv = next((x for x in b.get("levels") or [] if x["id"] == low.get("level_id")), None)
        if lv is None:
            continue
        z_low = float(M.room_floor_z(b, low))
        z_high = z_low + float(s.get("rise") or 0.0)
        # the higher room: the room across the wall from the lower one at the opening
        cx, cy = (o.get("center") or [0.0, 0.0])[:2]
        high = None
        best = 1e9
        for r in others:
            p = _poly(r.get("polygon"))
            if p is None:
                continue
            d = p.distance(Point(cx, cy))
            if d < best and d <= float(wall.get("thickness") or 0.2) + 0.15:
                high, best = r, d
        if high is None:
            continue
        rec = plan(o, wall, low, high, z_low, z_high, params)
        o["steps"] = rec if rec["fits"] else None
        s["placed"] = rec["room_id"] if rec["fits"] else None
        s["kind"] = rec["kind"]
        s["reason"] = rec["reason"]
        (out["built"] if rec["fits"] else out["unbuilt"]).append({"opening_id": o["id"], "reason": rec["reason"]})
    return out
