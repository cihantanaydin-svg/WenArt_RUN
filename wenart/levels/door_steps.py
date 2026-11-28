"""Steps at a door between two floors of different height (27 Nov 2026, audit fix round 5b; 28 Nov 2026 fix-up).

What: ``place(b, inner_steps, params)`` runs after the level model's thresholds (``levels.model._thresholds``: every door
or doorless opening between two rooms whose floors differ by more than ``flush_max`` gives an inner step record). It first
clears the step plans of every opening (a re-inference that made the floors flush leaves none behind), then for each
record:

- a drawn stair or short run of steps in front of the door (a stair piece of either room within ``DRAWN_REACH_M`` of the
  door) is the steps: recorded as drawn, no inferred blocks;
- else it plans, relative to the door (``opening["steps"]``: the lower side, the risers, riser, tread, run, kind and the
  door it was planned for), steps in the lower room (``risers`` of at most ``riser_max_indoor``, ``riser_max_outdoor``
  when the lower room is an outdoor one; the last riser is the threshold in the wall), or a ramp in front of a garage's
  vehicle door (``levels.model.is_garage_door``, the one predicate). The flight must stand inside the lower room and be
  no obstacle: off the approach of the room's other doors and openings, off every stair, and the room's floor beside it
  still one walkway at least ``WALK_CLEAR_M`` wide. Otherwise nothing is built: a finding (``unbuilt``, the reason).

The build rebuilds the blocks from the opening as it is then (``plan_blocks``; ``shell.door_step_blocks``), so a door the
later stages move or resize carries its steps; a door moved to another wall loses them (listed by the build).

Why: real15's garage door d_L0_006 joined floors 0.25 m apart and real10's shelter doors d_L-2_001 / d_L-2_004 0.35 m
apart, with no step: the model review found a wall under the door seen from the lower room (M1). The review of the round
(STEPS-1 to -6, GENERAL-4) found the first plan absolute, never cleared, blind to walkways and drawn steps, its ramp
inside out and its garage rule a second one.

How: pure geometry (shapely in ``place``; ``plan_blocks`` is plain Python for Blender).
"""
from __future__ import annotations

import math
from typing import Optional

FIT_TOL_M = 0.02             # a flight's plan may stand this far over its room's outline (a plaster layer)
DRAWN_REACH_M = 0.5          # a drawn short run of steps this close to the door is its steps
SHORT_RUN_MAX = 4            # ... a drawn stair of at most this many steps (a storey's stair is no door step)
APPROACH_DEPTH_M = 0.9       # another door's approach: its width this deep in front of it
WALK_CLEAR_M = 0.8           # the lower room's floor beside the flight stays one walkway this wide
OUTDOOR_TYPES = ("balcony",)


def _r(v: float, nd: int = 4) -> float:
    return round(float(v), nd) + 0.0


def _frame(o: dict, wall: dict) -> tuple:
    """``(c, u, n_left, t)``: the opening's centre on the wall's centre line, the wall's unit direction, its left normal and
    its thickness (pure)."""
    a, b = wall["start"][:2], wall["end"][:2]
    L = math.dist(a, b) or 1.0
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    c0 = o.get("center") or [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]
    k = (c0[0] - a[0]) * u[0] + (c0[1] - a[1]) * u[1]
    return (a[0] + u[0] * k, a[1] + u[1] * k), u, (-u[1], u[0]), float(wall.get("thickness") or 0.2)


def _box(c, u, n, w: float, d0: float, d1: float) -> list:
    """The rectangle ``w`` wide along ``u`` centred on ``c``, from ``d0`` to ``d1`` along ``n`` (counter-clockwise when
    ``n`` is ``u``'s left normal)."""
    hw = w / 2.0
    pts = []
    for s_, d in ((-hw, d0), (hw, d0), (hw, d1), (-hw, d1)):
        pts.append([_r(c[0] + u[0] * s_ + n[0] * d), _r(c[1] + u[1] * s_ + n[1] * d)])
    return pts


def plan_blocks(o: dict, wall: Optional[dict] = None, steps: Optional[dict] = None) -> list:
    """The blocks of a door's step plan rebuilt from the opening and wall as they are now (pure, plain Python; the plan's
    own wall when none is given): ``[{"polygon", "z0", "z1", "slope_to"?}]``; [] when the plan is drawn, missing or made
    for another wall."""
    st = steps if steps is not None else o.get("steps")
    if not isinstance(st, dict) or st.get("source") == "drawn" or st.get("kind") not in ("steps", "ramp"):
        return []
    if wall is None:
        wall = st.get("wall") if isinstance(st.get("wall"), dict) else None
        if wall is None or (o.get("wall_id") and wall.get("id") and o["wall_id"] != wall["id"]):
            return []
    if st.get("wall_id") and wall.get("id") and st["wall_id"] != wall["id"]:
        return []
    c, u, nl, t = _frame(o, wall)
    side = float(st.get("side") or 1.0)
    n = (nl[0] * side, nl[1] * side)
    w = float(o.get("width") or st.get("width") or 0.9)
    face = t / 2.0
    z_low, z_high = float(st["z_low"]), float(st["z_high"])
    if st["kind"] == "ramp":
        run = float(st.get("run") or 0.0)
        return [{"polygon": _box(c, u, n, w, face, face + run), "z0": _r(z_low), "z1": _r(z_high), "slope_to": "door"}]
    out = []
    risers, riser, tread = int(st.get("risers") or 0), float(st.get("riser") or 0.0), float(st.get("tread") or 0.3)
    for j in range(1, risers):                  # the last riser is the threshold in the wall
        out.append({"polygon": _box(c, u, n, w, face, face + (risers - j) * tread), "z0": _r(z_low),
                    "z1": _r(z_low + j * riser)})
    return out


def _poly(points):
    from shapely.geometry import Polygon
    if not points or len(points) < 3:
        return None
    p = Polygon(points)
    p = p if p.is_valid else p.buffer(0)
    return p if not p.is_empty and p.area > 0 else None


def _obstacles(b: dict, o: dict, low: dict, foot, walls: dict) -> list:
    """What the flight ``foot`` would stand on in the lower room: other doors' approaches, stairs, a walkway it cuts."""
    from shapely.geometry import Point
    why = []
    lp = _poly(low.get("polygon"))
    for x in b.get("openings") or []:
        if x is o or x.get("level_id") != low.get("level_id") or x.get("type") not in ("door", "opening") or \
                x.get("virtual") or not x.get("center"):
            continue
        wx = walls.get(x.get("wall_id"))
        if wx is None or lp is None or lp.distance(Point(x["center"][:2])) > float(wx.get("thickness") or 0.2) + 0.15:
            continue
        c, u, nl, t = _frame(x, wx)
        for sgn in (1.0, -1.0):
            n = (nl[0] * sgn, nl[1] * sgn)
            probe = (c[0] + n[0] * (t / 2.0 + 0.05), c[1] + n[1] * (t / 2.0 + 0.05))
            if lp.contains(Point(probe)):
                zone = _poly(_box(c, u, n, float(x.get("width") or 0.9), t / 2.0, t / 2.0 + APPROACH_DEPTH_M))
                if zone is not None and zone.intersection(foot).area > 0.02:
                    why.append(f"the approach of {x['id']}")
    for f in b.get("furniture") or []:
        if f.get("level_id") != low.get("level_id") or f.get("type") != "stair":
            continue
        fp = f.get("footprint") or {}
        try:
            from wenart import geometry as G
            q = _poly(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))
        except (KeyError, TypeError, ValueError):
            q = None
        if q is not None and q.intersection(foot).area > 0.02:
            why.append(f"the stair {f['id']}")
    if lp is not None:
        before = lp.buffer(-WALK_CLEAR_M / 2.0, join_style=2)
        after = lp.difference(foot).buffer(-WALK_CLEAR_M / 2.0, join_style=2)
        n_before = len(getattr(before, "geoms", [before])) if not before.is_empty else 0
        n_after = len(getattr(after, "geoms", [after])) if not after.is_empty else 0
        if n_after > max(n_before, 1):
            why.append(f"the walkway of {low['id']} (less than {WALK_CLEAR_M:.2f} m left beside the flight)")
    return why


def _drawn_steps(b: dict, o: dict, rooms: tuple, wall: dict) -> Optional[dict]:
    """A drawn stair or short run of either room within ``DRAWN_REACH_M`` of the door, or None."""
    from shapely.geometry import Point
    c, _u, _n, _t = _frame(o, wall)
    door = Point(c).buffer(float(o.get("width") or 0.9) / 2.0 + DRAWN_REACH_M)
    ids = {r["id"] for r in rooms if r}
    lids = {r.get("level_id") for r in rooms if r}
    for f in b.get("furniture") or []:
        if f.get("type") != "stair" or f.get("level_id") not in lids or f.get("build") is False:
            continue
        if f.get("room_id") and f.get("room_id") not in ids:
            continue
        stair = f.get("stair") or {}
        steps = int(stair.get("steps_drawn") or 0) or int(sum(int(fl.get("lines") or 0)
                                                             for fl in stair.get("flights") or []))
        if not (int(stair.get("short_steps") or 0) > 0 or 0 < steps <= SHORT_RUN_MAX):
            continue                                   # a storey's stair beside the door is no door step
        fp = f.get("footprint") or {}
        try:
            from wenart import geometry as G
            q = _poly(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))
        except (KeyError, TypeError, ValueError):
            q = None
        if q is not None and q.intersects(door):
            return f
    return None


def plan(o: dict, wall: dict, low: dict, high: dict, z_low: float, z_high: float, params: dict,
         b: Optional[dict] = None, walls: Optional[dict] = None) -> dict:
    """The steps or ramp of opening ``o`` in ``wall`` from room ``low`` (floor ``z_low``) up to ``high`` (``z_high``),
    relative to the door (module docstring): ``{"kind": steps | ramp, "source", "side", "room_id", "risers", "riser",
    "tread", "run", "rise", "z_low", "z_high", "wall_id", "width", "center", "blocks", "fits", "reason"}`` (pure)."""
    from shapely.geometry import Point
    from wenart.levels import model as M
    rise = z_high - z_low
    w = float(o.get("width") or 0.9)
    c, u, nl, t = _frame(o, wall)
    lp = _poly(low.get("polygon"))
    side = 1.0
    probe = (c[0] + nl[0] * (t / 2.0 + 0.05), c[1] + nl[1] * (t / 2.0 + 0.05))
    if lp is not None and not lp.contains(Point(probe)):
        side = -1.0
    base = {"room_id": low["id"], "high_room_id": high["id"], "z_low": _r(z_low), "z_high": _r(z_high),
            "rise": _r(rise), "wall_id": wall.get("id"), "width": _r(w), "center": [_r(c[0]), _r(c[1])],
            "side": side, "inferred": True,
            "wall": {"id": wall.get("id"), "start": list(wall["start"][:2]), "end": list(wall["end"][:2]),
                     "thickness": float(wall.get("thickness") or 0.2)}}
    drawn = _drawn_steps(b, o, (low, high), wall) if b is not None else None
    if drawn is not None:
        return dict(base, kind="steps", source="drawn", piece=drawn["id"], risers=0, riser=0.0, tread=0.0, run=0.0,
                    blocks=[], fits=True, inferred=False,
                    reason=f"{o['id']} joins {low['id']} ({z_low:+.2f}) and {high['id']} ({z_high:+.2f}), "
                           f"{rise:.2f} m apart: the drawn stair {drawn['id']} at the door is its steps (no inferred "
                           f"blocks)")
    vehicle = M.is_garage_door(o, low)
    outdoor = low.get("room_type") in OUTDOOR_TYPES
    if vehicle:
        slope = float(params.get("drive_slope") or 0.12)
        run = rise / slope
        rec = dict(base, kind="ramp", source="inferred", slope=_r(slope), run=_r(run), risers=0, riser=0.0, tread=0.0)
        what = f"a ramp at 1:{round(1.0 / slope):d}, {run:.2f} m long, in front of the vehicle door"
    else:
        st = M.steps_for(rise, w, params, outdoor=outdoor) or {"count": 1, "riser": rise, "tread": 0.30}
        n, riser, tread = int(st["count"]), float(st["riser"]), float(st["tread"])
        run = (n - 1) * tread
        rec = dict(base, kind="steps", source="inferred", risers=n, riser=_r(riser), tread=_r(tread), run=_r(run))
        what = f"{n} risers of {riser:.3f} m ({n - 1} tread block(s) of {tread:.2f} m and the threshold)"
    n_vec = (nl[0] * side, nl[1] * side)
    foot = _poly(_box(c, u, n_vec, w, t / 2.0, t / 2.0 + max(run, 0.01)))
    inside = bool(lp is not None and foot is not None and lp.buffer(FIT_TOL_M).contains(foot))
    blocked = _obstacles(b, o, low, foot, walls or {}) if (inside and b is not None and foot is not None) else []
    fits = inside and not blocked
    rec["blocks"] = plan_blocks(o, wall, rec) if fits else []
    rec["fits"] = fits
    head = (f"{o['id']} joins {low['id']} ({z_low:+.2f}) and {high['id']} ({z_high:+.2f}), {rise:.2f} m apart, no step "
            f"drawn: {what}")
    if fits:
        rec["reason"] = f"{head} inside {low['id']} (the lower room; inferred)"
    elif not inside:
        rec["reason"] = (f"{head} does not fit inside {low['id']}, the lower room ({run:.2f} m in front of the door): not "
                         f"built, listed (a finding)")
    else:
        rec["reason"] = f"{head} would block {', '.join(blocked)}: not built, listed (a finding)"
    return rec


def place(b: dict, inner_steps: list, params: dict) -> dict:
    """Plans the steps of every inner step record (module docstring) on its opening (``opening["steps"]``, in place)
    and on the record (``placed``, ``kind``, ``reason``). Returns ``{"built": [...], "unbuilt": [...]}``."""
    from shapely.geometry import Point
    from wenart.levels import model as M
    for o in b.get("openings") or []:
        o.pop("steps", None)                       # STEPS-2 / GENERAL-4: no stale plan survives a re-inference
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
        z_low = float(M.room_floor_z(b, low))
        z_high = z_low + float(s.get("rise") or 0.0)
        cx, cy = (o.get("center") or [0.0, 0.0])[:2]
        high, best = None, 1e9
        for r in others:
            p = _poly(r.get("polygon"))
            if p is None:
                continue
            d = p.distance(Point(cx, cy))
            if d < best and d <= float(wall.get("thickness") or 0.2) + 0.15:
                high, best = r, d
        if high is None:
            continue
        rec = plan(o, wall, low, high, z_low, z_high, params, b, walls)
        if rec["fits"]:
            o["steps"] = {k: v for k, v in rec.items() if k != "blocks"}    # relative: the build rebuilds the blocks
        s["placed"] = rec["room_id"] if rec["fits"] else None
        s["kind"] = rec["kind"] if rec.get("source") != "drawn" else "drawn"
        s["reason"] = rec["reason"]
        (out["built"] if rec["fits"] else out["unbuilt"]).append({"opening_id": o["id"], "reason": rec["reason"]})
    return out
