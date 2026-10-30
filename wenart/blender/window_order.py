"""One facade, one window language (30 Oct 2026, lessons UL210 and UL211; pure, no bpy, no shapely).

The user on real06 run 20261029-100801-full:
- UL210, "Big windows next to small windows not making any sense needs better solution". On both floors of a side
  facade, a bathroom's window stood 2-3 cm from a room's window: 0.85 m of glass on a 1.25 m sill (architect H2: a
  bathroom window over the basin rises clear of the tap) beside 1.20 m on a 0.90 m sill. The two looked like a big
  and a small window glued together.
- UL211, "This window all the way to the edge of a wall not making any sense needs better solution". A window's frame
  ran into the facade's corner with no solid wall between them.

What (``build.prepare`` runs ``piers`` and then ``compose`` after the architect's answers and the roof clips, before
the curtains follow their windows, ``window_decor.refit``; the model review's M36 and ``review`` read the result):

1. **Facade lines** (``facade_lines``): every window on an outer wall lies on an edge of its level's outline (the
   outer wall faces, ``geom2d.wall_outline``). Windows of one edge, in order along it, whose frames stand less than
   ``GROUP_GAP_M`` apart (narrower than a real pier) form one group: one composition.
2. **The group's lines** (``compose``): every window of a group takes the group's sill and head, the lowest sill and
   the highest head of its windows (the head under the roof for each of them, ``head_limit``). No window loses
   glass. A window that needs a higher sill gets a transom at that height and a fixed lower light below it
   (``lower_light``; ``parametric.window_product_parts`` builds the transom, the bead and the glass):
   - its own sill was set higher (an answer such as H2 over a basin, or a counter);
   - a wall-backed piece stands in front of it, taller than the group's sill;
   - it is an upper storey's window without a guard, and the group's sill is under ``GUARD_SILL_M``: the fixed
     lower light guards it.
   A wet room's window (a bathroom, a WC, a shower) takes satin glass (``glass: satin``, its lower light too): privacy
   comes from the glass, never from a higher sill. A window whose sill or head the documents fix keeps them, and so
   does its group (``review`` reports it). The drawn values stay (``drawn_sill_height``, ``drawn_height``) and every
   change is recorded on the window (``window_group``) and in its evidence.
3. **The corner pier** (``piers``): every window keeps ``PIER_MIN_M`` of solid wall between its frame (its surround
   in the families with surrounds, else its reveal) and either end of its outline edge, i.e. the facade's corner.
   - A window closer than that is moved along its wall, away from the corner, by the shortfall and at most
     ``MOVE_MAX_M``. This is a clear drawing fix (``window_pier``, ``corrected_by_ai`` when the window has no other
     record, ``drawn_center`` kept). The move keeps the same room behind the whole window and the outside in front
     of it, keeps ``OPENING_GAP_M`` from every other opening on its line, and puts no new wall-backed piece in front
     of it.
   - Where the move cannot pass, the window narrows from the corner side by the shortfall, down to ``MIN_WIDTH_M``
     (the far jamb stays, so a drawn pair's mullion gap stays as drawn); a part move with a part narrowing is tried
     first.
   - Otherwise it stays, and ``review`` reports it.
   - A window the architect's answers move, widen or add (W2's move to the outer wall, L1's daylight) keeps the same
     pier: ``architect_actions.apply_answers`` runs ``piers`` on it right after the answer.

Why: a facade is read as rows of openings. Two windows side by side are one element, with one head line and one sill
line; a pier at a corner holds the corner. UK Approved Document A asks for a 665 mm pier at a masonry return, a
structural minimum for load-bearing masonry. We take 0.40 m of solid wall on the outer face as the visual minimum below
which a window is clearly misplaced, and correct only those, since the documents stay the anchor.
"""
from __future__ import annotations

import copy
import math
from typing import Callable, Optional

from wenart import geometry as G

RULE_GROUP = "window_group"
RULE_PIER = "window_pier"
LESSON_GROUP = "UL210"
LESSON_PIER = "UL211"
REVIEW_CHECK = "M36"
GROUP_GAP_M = 0.60                # frames closer than this on one facade line: one composition
LINE_TOL_M = 0.03                 # sills or heads within this are one line
GUARD_SILL_M = 0.90               # an upper storey's glass under this needs a guard (a fixed lower light is one)
LOWER_LIGHT_MIN_M = 0.15          # = parametric.TRANSOM_LIGHT_MIN_M: a fixed lower light at least this tall
UPPER_LIGHT_MIN_M = 0.45          # the light above a transom at least this tall (else the window keeps its lines)
PIECE_CLEAR_M = 0.05              # a lower light reaches this far over the top of a piece standing in front
UPPER_STOREY_M = 1.0              # a level whose floor stands this far over the ground level's is an upper storey
PIER_MIN_M = 0.40                 # solid wall between a window's frame and its facade's corner (module docstring)
MOVE_MAX_M = 0.60                 # a window moves at most this far along its wall to keep its pier
MIN_WIDTH_M = 0.45                # a window narrowed for its pier keeps at least this width
PIER_TOL_M = 0.001                # a pier this close to PIER_MIN_M is kept (the centres are rounded to 0.1 mm)
OPENING_GAP_M = 0.10              # a moved window keeps this from every other opening on its line
EDGE_TOL_M = 0.08                 # a window's wall face lies this close to its outline edge
JOG_MAX_M = 0.12                  # outline steps shallower than this are no corner (walls of different thickness)
CORNER_PROBE_M = 0.30             # past an edge's end, where the house is looked for (an inner or an outer corner)
SEE_THROUGH_TYPES: tuple[str, ...] = ("shower",)   # a glass enclosure in front of a window needs no lower light
PROBE_M = 0.15                    # past the wall face, where the room and the outside are probed
STEP_M = 0.05


def _sill(o: dict) -> float:
    return float(o["sill_height"]) if o.get("sill_height") is not None else 0.9


def _head(o: dict) -> float:
    return _sill(o) + (float(o["height"]) if o.get("height") is not None else 1.2)


def _windows(building: dict) -> list[dict]:
    return [o for o in building.get("openings") or [] if o.get("type") == "window" and o.get("build") is not False
            and not o.get("interior_glazing") and o.get("center") and o.get("width")]


def frame_extra(style_family: Optional[str]) -> float:
    """What a window's frame shows past its opening on the facade: the family's surround (classic, Mediterranean,
    rustic), else the reveal of the modern families (``facade.DIMENSIONS``, ``facade.KIT``)."""
    from wenart.blender import facade as F

    rules = F.ARTICULATION.get(str(style_family or "").lower(), F.ARTICULATION["default"])
    return float(F.DIMENSIONS["surround_width"] if rules.get("surround") else F.KIT["reveal_width"])


def _upper_levels(building: dict) -> set:
    levels = [lv for lv in building.get("levels") or [] if lv.get("id")]
    if not levels:
        return set()
    zs = [float(lv.get("elevation") or 0.0) for lv in levels]
    ground = min((z for z in zs if z >= -0.01), default=min(zs))
    return {lv["id"] for lv in levels if float(lv.get("elevation") or 0.0) > ground + UPPER_STOREY_M}


def facade_lines(building: dict) -> list[dict]:
    """``[{"level_id", "origin", "dir", "length", "windows": [{"id", "t", "half"}]}]``: the outline edges of every level
    with the windows on them (pure; module docstring, step 1), the windows in order along their edge."""
    from wenart.blender import architect_actions as AA
    from wenart.blender import geom2d

    plan = AA.Plan(building)
    out = []
    by_level: dict = {}
    for o in _windows(building):
        by_level.setdefault(o.get("level_id"), []).append(o)
    for lid, wins in by_level.items():
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
        outline, _method = geom2d.wall_outline(walls)
        if len(outline) < 3:
            continue
        # a wall a few cm thicker than its neighbours (a window's own wall segment) steps the outline at the jambs:
        # no corner (real06: 0.30 m window walls in 0.25 m facades); a real pier or pilaster stays one
        outline, _closed = geom2d.close_jogs(outline, JOG_MAX_M)
        edges = []
        m = len(outline)
        for k in range(m):
            p, q = outline[k], outline[(k + 1) % m]
            length = G.distance(p, q)
            if length < 1e-6:
                continue
            d = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
            inward = (-d[1], d[0])                    # the outline runs counter-clockwise: the house on the left
            # an outer (convex) corner at an end: just behind the face, past the end along the facade, lies outside
            # the house; in a recess or at an inner corner it lies in the house (a window there keeps no pier). Probed
            # past the outline's small steps (a thicker wall's few cm at a corner)
            ends = []
            for pt, sgn in ((p, -1.0), (q, 1.0)):
                probe = (pt[0] + sgn * d[0] * CORNER_PROBE_M + inward[0] * 0.05,
                         pt[1] + sgn * d[1] * CORNER_PROBE_M + inward[1] * 0.05)
                ends.append(not G.point_in_polygon(probe, outline))
            edges.append({"level_id": lid, "origin": (float(p[0]), float(p[1])), "dir": d, "length": length,
                          "convex": tuple(ends), "windows": []})
        for o in wins:
            w = plan.walls.get(o.get("wall_id"))
            if w is None:
                continue
            _a, u, _l = plan.axis(w)
            half_t = float(w.get("thickness") or 0.2) / 2.0
            c = (float(o["center"][0]), float(o["center"][1]))
            best = None
            for e in edges:
                d = e["dir"]
                if abs(u[0] * d[1] - u[1] * d[0]) > 0.02:
                    continue
                rel = (c[0] - e["origin"][0], c[1] - e["origin"][1])
                t = rel[0] * d[0] + rel[1] * d[1]
                off = abs(rel[0] * -d[1] + rel[1] * d[0])
                if not (-0.05 <= t <= e["length"] + 0.05) or off > half_t + EDGE_TOL_M:
                    continue
                if best is None or off < best[0]:
                    best = (off, e, t)
            if best is not None:
                best[1]["windows"].append({"id": o["id"], "t": best[2], "half": float(o["width"]) / 2.0})
        for e in edges:
            if e["windows"]:
                e["windows"].sort(key=lambda r: (r["t"], r["id"]))
                out.append(e)
    return out


def groups(building: dict, lines: Optional[list[dict]] = None) -> list[dict]:
    """``[{"level_id", "ids", "line"}]``: the windows of one facade line standing less than ``GROUP_GAP_M`` apart, two
    or more (module docstring, step 1)."""
    out = []
    for line in lines if lines is not None else facade_lines(building):
        cur = [line["windows"][0]]
        for prev, nxt in zip(line["windows"], line["windows"][1:]):
            gap = (nxt["t"] - nxt["half"]) - (prev["t"] + prev["half"])
            if gap < GROUP_GAP_M:
                cur.append(nxt)
                continue
            if len(cur) > 1:
                out.append({"level_id": line["level_id"], "ids": [r["id"] for r in cur], "line": line})
            cur = [nxt]
        if len(cur) > 1:
            out.append({"level_id": line["level_id"], "ids": [r["id"] for r in cur], "line": line})
    return out


def _inside_room(plan, o: dict) -> Optional[dict]:
    from wenart.blender import architect_actions as AA

    sides = AA.window_sides(plan, o)
    rooms = [r for r in sides if r is not None and not plan.is_outside(r)]
    return rooms[0] if len(rooms) == 1 else None


def _front_tops(plan, o: dict, room: Optional[dict]) -> list[tuple[str, float]]:
    """``[(id, top)]`` of the wall-backed pieces of the window's ``room`` standing in front of window ``o``
    (``architect_actions.front_pieces``) with their built heights; a glass shower enclosure is no blocker."""
    from wenart.blender import architect_actions as AA
    from wenart.blender import wall_plates as WP

    by = {f.get("id"): f for f in plan.b.get("furniture") or []}
    out = []
    for label in AA.front_pieces(plan, o):
        pid = label.split(" ", 1)[0]
        f = by.get(pid)
        if f is None or str(f.get("type")) in SEE_THROUGH_TYPES:
            continue
        if room is not None and f.get("room_id") not in (None, room["id"]):
            continue                                      # behind a partition: another room's piece
        out.append((pid, float(WP.piece_height(f))))
    return out


def _why_own(o: dict) -> str:
    for key in ("adjusted_by_ai", "corrected_by_ai", "tall_window"):
        rec = o.get(key)
        if isinstance(rec, dict) and rec.get("reason"):
            return str(rec["reason"])[:120]
    return "its sill as planned"


def _keep_drawn(o: dict, *fields) -> None:
    for f in fields:
        o.setdefault(f"drawn_{f}", copy.deepcopy(o.get(f)))


def _evidence(o: dict, rule: str, text: str) -> None:
    ev = o.setdefault("evidence", [])
    if isinstance(ev, list):
        ev.append({"file": "building.json", "method": "inferred", "confidence": 0.7, "rule": rule, "text": text})


def compose(building: dict, head_limit: Optional[Callable] = None) -> list[dict]:
    """In place (module docstring, step 2): every group's windows on the group's lines; returns one record per window
    changed or kept (``{"id", "group", "action", "why", ...}``)."""
    from wenart.blender import architect_actions as AA

    plan = AA.Plan(building)
    upper = _upper_levels(building)
    out = []
    for grp in groups(building):
        ws = [plan.openings[i] for i in grp["ids"] if i in plan.openings]
        sills = [_sill(o) for o in ws]
        heads = [_head(o) for o in ws]
        if max(sills) - min(sills) <= LINE_TOL_M and max(heads) - min(heads) <= LINE_TOL_M:
            continue
        fixed = [(o["id"], AA.heights_given(building, o)) for o in ws]
        fixed = [(i, why) for i, why in fixed if why]
        if fixed:
            for o in ws:
                out.append({"id": o["id"], "group": grp["ids"], "action": "kept",
                            "why": f"the documents fix {fixed[0][0]}'s lines ({fixed[0][1]}): the group keeps its "
                                   f"own lines ({LESSON_GROUP})"})
            continue
        g_sill = min(sills)
        g_head = max(heads)
        for o in ws:
            lim = head_limit(o) if head_limit is not None else None
            if lim is not None:
                g_head = min(g_head, float(lim))
        if g_head - g_sill < UPPER_LIGHT_MIN_M:
            continue
        for o in ws:
            o["composition"] = list(grp["ids"])          # one product for every window of it (looks, opening_build)
        for o in ws:
            old_s, old_h = _sill(o), _head(o)
            room = _inside_room(plan, o)
            wet = room is not None and str(room.get("room_type") or "").lower() in AA.WET_ROOMS
            need, whys = None, []
            if old_s > g_sill + LINE_TOL_M:
                need = old_s
                whys.append(f"its own sill {old_s:.2f} m ({_why_own(o)})")
            tops = [(pid, top) for pid, top in _front_tops(plan, o, room) if top > g_sill]
            if tops:
                top = max(t for _p, t in tops) + PIECE_CLEAR_M
                need = top if need is None else max(need, top)
                whys.append("in front of " + ", ".join(f"{p} ({t:.2f} m)" for p, t in tops))
            if o.get("level_id") in upper and g_sill < GUARD_SILL_M - 1e-6 and not o.get("guard"):
                need = GUARD_SILL_M if need is None else max(need, GUARD_SILL_M)
                whys.append(f"an upper storey's window: the fixed lower light guards it up to {GUARD_SILL_M:.2f} m")
            if need is not None:
                need = max(need, g_sill + LOWER_LIGHT_MIN_M)
                if g_head - need < UPPER_LIGHT_MIN_M:
                    out.append({"id": o["id"], "group": grp["ids"], "action": "kept",
                                "why": f"{o['id']} keeps its lines: above a lower light to {need:.2f} m too little "
                                       f"glass would be left ({'; '.join(whys)})"})
                    continue
            if abs(old_s - g_sill) <= LINE_TOL_M and abs(old_h - g_head) <= LINE_TOL_M and need is None and \
                    not (wet and o.get("glass") != "satin"):
                continue
            _keep_drawn(o, "sill_height", "height")
            o["sill_height"], o["height"] = round(g_sill, 3), round(g_head - g_sill, 3)
            if need is not None:
                o["lower_light"] = {"at_m": round(need, 3), "glass": "satin" if (wet or tops) else "glass",
                                    "why": "; ".join(whys)}
            else:
                o.pop("lower_light", None)
            if wet:
                o["glass"] = "satin"
            others = [i for i in grp["ids"] if i != o["id"]]
            reason = (f"{o['id']} on the facade line of {', '.join(others)}: one composition, sill {g_sill:.2f} m and "
                      f"head {g_head:.2f} m (was {old_s:.2f}-{old_h:.2f} m)"
                      + (f"; a fixed lower light to {need:.2f} m under a transom ({'; '.join(whys)})" if need else "")
                      + ("; satin glass in a wet room (privacy from the glass, not a higher sill)" if wet else "")
                      + f" ({LESSON_GROUP}, user: \"Big windows next to small windows not making any sense\")")
            o["window_group"] = {"rule": RULE_GROUP, "group": list(grp["ids"]), "sill_m": round(g_sill, 3),
                                 "head_m": round(g_head, 3), "was": [round(old_s, 3), round(old_h, 3)],
                                 "lower_light": o.get("lower_light"), "glass": o.get("glass"), "reason": reason}
            _evidence(o, RULE_GROUP, reason)
            out.append({"id": o["id"], "group": grp["ids"], "action": "lines", "why": reason,
                        "sill_m": round(g_sill, 3), "head_m": round(g_head, 3), "was": [old_s, old_h]})
    return out


def _span_rooms(plan, o: dict, wall: dict, t0: float, t1: float) -> tuple[set, set]:
    """The room ids behind and in front of ``wall`` along ``t0..t1`` (metres along the wall from its start),
    ``None`` for no room; probed every ``STEP_M``."""
    a, u, _l = plan.axis(wall)
    n = (-u[1], u[0])
    reach = float(wall.get("thickness") or 0.2) / 2.0 + PROBE_M
    left, right = set(), set()
    steps = max(1, int(math.ceil((t1 - t0) / STEP_M)))
    for k in range(steps + 1):
        t = t0 + (t1 - t0) * k / steps
        p = (a[0] + u[0] * t, a[1] + u[1] * t)
        lr = plan.room_at((p[0] + n[0] * reach, p[1] + n[1] * reach), wall.get("level_id"))
        rr = plan.room_at((p[0] - n[0] * reach, p[1] - n[1] * reach), wall.get("level_id"))
        left.add(None if plan.is_outside(lr) else lr["id"])
        right.add(None if plan.is_outside(rr) else rr["id"])
    return left, right


def _line_wall(plan, wall: dict, point) -> Optional[dict]:
    """The wall of ``wall``'s line (parallel, its axis within 1 cm) whose length holds ``point``: the wall a moved
    window stands in."""
    a, u, length = plan.axis(wall)
    t = (point[0] - a[0]) * u[0] + (point[1] - a[1]) * u[1]
    if -1e-6 <= t <= length + 1e-6:
        return wall
    for w in plan.walls.values():
        if w.get("level_id") != wall.get("level_id") or w["id"] == wall["id"]:
            continue
        a2, u2, l2 = plan.axis(w)
        if abs(u[0] * u2[1] - u[1] * u2[0]) > 0.02:
            continue
        if abs((a2[0] - a[0]) * -u[1] + (a2[1] - a[1]) * u[0]) > 0.01:
            continue
        t2 = (point[0] - a2[0]) * u2[0] + (point[1] - a2[1]) * u2[1]
        if -1e-6 <= t2 <= l2 + 1e-6:
            return w
    return None


def _place_problems(plan, o: dict, wall: dict, room: Optional[dict], t_new: float, width: float) -> list[str]:
    """Why window ``o`` cannot stand at ``t_new`` (metres along ``wall``) with ``width`` (pure; [] when it can): its
    room behind it and the outside in front of it, nothing on either side that is not along it now (another room, a
    partition, the outside behind it), ``OPENING_GAP_M`` from every other opening of its line, no piece newly in
    front that hides more glass than what stands there now, a wall of its line."""
    half = width / 2.0
    why = []
    t_was, half_was = plan.t_of(wall, o["center"]), float(o.get("width") or 0.0) / 2.0
    left, right = _span_rooms(plan, o, wall, t_new - half, t_new + half)
    was_l, was_r = _span_rooms(plan, o, wall, t_was - half_was, t_was + half_was)
    # the drawn place may already touch a corner's or a partition's thickness (no room there): only what is new counts
    inside = room["id"] if room else None
    if room is None or not ({inside, None} >= (left | right)) or (left - was_l) or (right - was_r):
        why.append("another room or no outside along the new place")
    # ``OPENING_GAP_M`` from every other opening, or no closer than it stands now (a narrowing that keeps its far
    # jamb leaves a drawn pair's mullion gap as drawn)
    taken = plan.spans_on(wall, skip=(o["id"],))
    for s0, s1 in taken:
        gap = max(s0 - (t_new + half), (t_new - half) - s1)
        if gap < OPENING_GAP_M - 1e-9 and gap < max(s0 - (t_was + half_was), (t_was - half_was) - s1) - 1e-6:
            why.append(f"another opening within {OPENING_GAP_M:.2f} m")
            break
    c_new = plan.at_t(wall, t_new)
    trial = dict(o, center=[round(c_new[0], 4), round(c_new[1], 4)], width=width)
    was = max([_sill(o)] + [t for _p, t in _front_tops(plan, o, room)])
    now = [(p, t) for p, t in _front_tops(plan, trial, room) if t > was + LINE_TOL_M]
    if now:
        why.append("it would stand behind " + ", ".join(f"{p} ({t:.2f} m)" for p, t in now))
    if _line_wall(plan, wall, c_new) is None:
        why.append("no wall of its line holds the new place")
    return why


def _piers(line: dict, rec: dict, extra: float) -> tuple[float, float]:
    """The solid wall between a window's frame (``extra`` past its opening) and the two ends of its facade line;
    an end that is no outer corner (a recess, an inner corner) counts as far away."""
    lo = rec["t"] - rec["half"] - extra
    hi = line["length"] - (rec["t"] + rec["half"] + extra)
    convex = line.get("convex") or (True, True)
    return (lo if convex[0] else math.inf), (hi if convex[1] else math.inf)


def piers(building: dict, style_family: Optional[str] = None, only: Optional[tuple] = None) -> list[dict]:
    """In place (module docstring, step 3): every window (of ``only`` when given: the architect's moved, widened and
    new windows keep the same pier) ``PIER_MIN_M`` from its facade's corners; returns one record per window moved,
    narrowed or kept (``{"id", "action", "pier_m", "why", ...}``)."""
    from wenart.blender import architect_actions as AA

    plan = AA.Plan(building)
    extra = frame_extra(style_family)
    out = []
    for line in facade_lines(building):
        d = line["dir"]
        for rec in line["windows"]:
            if only is not None and rec["id"] not in only:
                continue
            o = plan.openings.get(rec["id"])
            wall = plan.walls.get(o.get("wall_id")) if o else None
            if o is None or wall is None:
                continue
            p_lo, p_hi = _piers(line, rec, extra)
            bad_lo, bad_hi = p_lo < PIER_MIN_M - PIER_TOL_M, p_hi < PIER_MIN_M - PIER_TOL_M
            if not bad_lo and not bad_hi:
                continue
            if bad_lo and bad_hi:
                out.append({"id": o["id"], "action": "kept", "pier_m": round(min(p_lo, p_hi), 3),
                            "why": f"{o['id']}: under {PIER_MIN_M:.2f} m of wall to both corners of its facade "
                                   f"({p_lo:.2f} and {p_hi:.2f} m): the facade is too short to move it ({LESSON_PIER})"})
                continue
            short, sign = (p_lo, 1.0) if bad_lo else (p_hi, -1.0)
            deficit = PIER_MIN_M - short
            room = _inside_room(plan, o)
            a, u, _l = plan.axis(wall)
            along = sign * (d[0] * u[0] + d[1] * u[1])        # the move's sign along the wall's own axis
            t_wall = plan.t_of(wall, o["center"])
            width = float(o["width"])
            far = p_lo if sign < 0 else p_hi
            # the near jamb leaves the corner by the shortfall; the far jamb follows by ``shift`` (the whole window
            # moves), the rest narrows it from the corner side: the largest move that passes the checks first
            placed, first_no = None, None
            k = int(math.floor(min(deficit, MOVE_MAX_M) / STEP_M + 1e-9))
            shifts = ([deficit] if deficit <= MOVE_MAX_M + 1e-9 else []) + [STEP_M * i for i in range(k, -1, -1)]
            for shift in shifts:
                new_w = width - (deficit - shift)
                if new_w < MIN_WIDTH_M - 1e-9:
                    first_no = first_no or [f"narrower than {MIN_WIDTH_M:.2f} m"]
                    break
                if far - shift < PIER_MIN_M - 1e-6:
                    continue
                t_new = t_wall + along * (shift + (deficit - shift) / 2.0)
                why = _place_problems(plan, o, wall, room, t_new, new_w)
                if why:
                    first_no = first_no or why
                    continue
                placed = (shift, new_w, plan.at_t(wall, t_new))
                break
            if placed is None:
                out.append({"id": o["id"], "action": "kept", "pier_m": round(short, 3),
                            "why": f"{o['id']}: {short:.2f} m of wall to its facade corner, under {PIER_MIN_M:.2f} m; no "
                                   f"move or narrowing passes ({'; '.join(first_no or ['too far'])}) ({LESSON_PIER})"})
                continue
            shift, new_w, c_new = placed
            _keep_drawn(o, "center", "width")
            host = _line_wall(plan, wall, c_new) or wall
            o["center"] = [round(c_new[0], 4), round(c_new[1], 4)] + list(o["center"][2:])
            o["wall_id"] = host["id"]
            o["width"] = round(new_w, 4)
            if shift >= deficit - 1e-9:
                action, what = "moved", f"moved {deficit:.2f} m along its wall away from the corner"
            elif shift <= 1e-9:
                action, what = "narrowed", f"narrowed from the corner side to {new_w:.2f} m (the far jamb kept: " \
                                           f"{'; '.join(first_no or ['the move could not pass'])})"
            else:
                action, what = "moved", (f"moved {shift:.2f} m away from the corner and narrowed from its side to "
                                         f"{new_w:.2f} m (a longer move: {'; '.join(first_no or ['no'])})")
            reason = (f"{o['id']}: its frame stood {max(short, 0.0):.2f} m from its facade's corner (under the "
                      f"{PIER_MIN_M:.2f} m of solid wall a corner keeps): {what} ({LESSON_PIER}, user: \"This window all "
                      f"the way to the edge of a wall not making any sense\")")
            o["window_pier"] = {"rule": RULE_PIER, "action": action, "pier_was_m": round(short, 3),
                                "shift_m": round(shift + (deficit - shift) / 2.0, 3), "reason": reason}
            if not isinstance(o.get("corrected_by_ai"), dict):
                o["corrected_by_ai"] = {"by": "code", "rule": RULE_PIER, "reason": reason}
            _evidence(o, RULE_PIER, reason)
            out.append({"id": o["id"], "action": action, "pier_m": round(short, 3), "why": reason})
    return out


def review(building: dict, style_family: Optional[str] = None, check: str = REVIEW_CHECK) -> tuple[list[dict], int]:
    """``(findings, checked)`` (pure): a facade group whose windows stand on different sill or head lines, and a
    window with less than ``PIER_MIN_M`` of wall to its facade's corner, each with the reason it stayed (``compose`` and
    ``piers`` record why they kept a window)."""
    out, n = [], 0
    lines = facade_lines(building)
    by = {o["id"]: o for o in _windows(building)}
    for grp in groups(building, lines):
        n += 1
        ws = [by[i] for i in grp["ids"] if i in by]
        sills, heads = [_sill(o) for o in ws], [_head(o) for o in ws]
        if max(sills) - min(sills) > LINE_TOL_M or max(heads) - min(heads) > LINE_TOL_M:
            out.append({"check": check, "severity": "major", "target": ws[0]["id"], "room_id": None,
                        "kind": "staggered_windows", "lesson": LESSON_GROUP,
                        "message": (f"{', '.join(grp['ids'])} stand side by side on one facade line with sills "
                                    f"{'/'.join(f'{s:.2f}' for s in sills)} m and heads "
                                    f"{'/'.join(f'{h:.2f}' for h in heads)} m: a big window beside a small one")})
    extra = frame_extra(style_family)
    for line in lines:
        for rec in line["windows"]:
            n += 1
            short = min(_piers(line, rec, extra))
            if short < PIER_MIN_M - 0.02:
                out.append({"check": check, "severity": "major", "target": rec["id"], "room_id": None,
                            "kind": "window_at_corner", "lesson": LESSON_PIER,
                            "message": (f"{rec['id']}: {max(short, 0.0):.2f} m of wall between its frame and its "
                                        f"facade's corner (at least {PIER_MIN_M:.2f} m)")})
    return out, n
