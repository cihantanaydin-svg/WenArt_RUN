"""Argus, the sense line: the house can be walked through (26 Oct 2026, user: "everything needs to be judged ... think
outside the box").

What (code, on the building as built, every room and every level):

- N1 a room that cannot be reached from outside through doors, doorless openings, open-plan joins and stairs
  (critical: a room nobody can enter makes no sense; a reading error: a door not read, a wall read twice);
- N2 a room reached only through a wet room (a bathroom or a shower room as the way into a bedroom or a kitchen);
- N3 a level above the lowest one that no stair (or other way) reaches;
- N4 the house has no entrance at all (no passable opening to the outside on any level);
- N5 a room misses a piece of its set (a bathroom's shower or bath, a kitchen's hob or fridge: the group checks'
  completeness, G9 / G10) while it holds a drawn piece nothing typed or a piece a decision took out: most likely that
  piece is the missing one (real06: the L1 bathroom's 2.42 x 0.98 m curved outline the AI left "unknown", "likely a
  bathtub or shower", and its added shower an AI decision removed).

How: a graph of the rooms and ``outside``: an opening that is not a window joins the rooms on its two sides
(``architect_actions.window_sides``; no room = outside, an open-air room counts as outside); two rooms of a level whose
outlines touch (closer than ``OPEN_GAP_M``, no wall between them) over ``OPEN_JOIN_M`` or more are one open plan; a
stair joins the room it starts in with the room its arrival floor lies in on the level above
(``stair_access.stair_rooms``, 27 Oct 2026: never the rooms at its centre, which passed real06's stair that arrived on
a strip cut off from the hall; the walk itself is the model review's M9); only a stair that cannot be planned joins the
rooms at its centre on its level and the levels next to it. Rooms smaller than ``MIN_ROOM_M2`` (shafts, voids) are not
checked.
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from wenart.audit import kinds as K

OPEN_GAP_M = 0.04          # outlines this close have no wall between them
OPEN_JOIN_M = 0.60         # ... over this length they are one open plan
MIN_ROOM_M2 = 1.5
WET = ("bathroom", "wc", "toilet", "shower", "shower_room", "laundry")
STAIR_TYPES = ("stair", "stairs", "staircase", "stair_spiral", "ladder")


def _poly(r: dict):
    from shapely.geometry import Polygon
    try:
        p = Polygon([tuple(pt[:2]) for pt in r.get("polygon") or []])
        return p if p.is_valid and p.area > 0 else p.buffer(0)
    except Exception:  # noqa: BLE001
        return None


def graph(building: dict) -> tuple[dict, dict]:
    """``(edges, via)``: ``edges[node] = set of nodes`` over the room ids and ``"outside"``; ``via[(a, b)]`` the
    opening, ``open plan`` or stair id that joins them (pure)."""
    from wenart.blender import architect_actions as AA

    plan = AA.Plan(building)
    edges: dict = {r["id"]: set() for r in plan.rooms}
    edges["outside"] = set()
    via: dict = {}

    def join(a, b, how):
        if a == b:
            return
        edges.setdefault(a, set()).add(b)
        edges.setdefault(b, set()).add(a)
        via.setdefault((a, b), how)
        via.setdefault((b, a), how)

    def node(room: Optional[dict]) -> str:
        return "outside" if AA.Plan.is_outside(room) else room["id"]

    for o in building.get("openings") or []:
        if o.get("type") == "window" or o.get("build") is False:
            continue
        sides = AA.window_sides(plan, o)
        if len(sides) == 2:
            join(node(sides[0]), node(sides[1]), o["id"])
    by_level: dict = {}
    for r in plan.rooms:
        by_level.setdefault(r.get("level_id"), []).append(r)
    for rooms in by_level.values():
        polys = [(r, _poly(r)) for r in rooms]
        for i, (ra, pa) in enumerate(polys):
            for rb, pb in polys[i + 1:]:
                if pa is None or pb is None or pa.distance(pb) > OPEN_GAP_M:
                    continue
                shared = pa.buffer(OPEN_GAP_M).intersection(pb.buffer(OPEN_GAP_M))
                if shared.area / (2 * OPEN_GAP_M) >= OPEN_JOIN_M:
                    join(node(ra), node(rb), "open plan")
    order = sorted(plan.levels.values(), key=lambda lv: float(lv.get("elevation") or 0.0))
    index = {lv["id"]: i for i, lv in enumerate(order)}
    from wenart.blender import stair_access as SA
    for f in building.get("furniture") or []:
        if str(f.get("type")) not in STAIR_TYPES:
            continue
        # 27 Oct 2026 (real06's first floor: the stair's centre lay in the hall of both floors while it arrived on a
        # strip its opening cut off from the hall): a stair joins the room it starts in with the room its arrival floor
        # lies in on the level above; the drawn upper end of the stair below joins nothing (that stair does). Whether a
        # visitor walks from the arrival into the floor is the model review's M9. Only a stair that cannot be planned
        # (no heights, no flights) falls back to its centre.
        try:
            ends = SA.stair_rooms(building, f)
            upper_end = ends is None and SA.is_upper_end(building, f)
        except Exception:  # noqa: BLE001 - shapely's errors too: the centre stands in
            ends, upper_end = None, False
        if ends is not None:
            a, b = plan.room.get(ends["start"]), plan.room.get(ends["arrival"])
            if a is not None and b is not None:
                join(node(a), node(b), f["id"])
            continue
        if upper_end:
            continue
        c = (f.get("footprint") or {}).get("center")
        room = plan.room.get(f.get("room_id"))
        lid = f.get("level_id") or (room or {}).get("level_id")
        if c is None or lid not in index:
            continue
        here = plan.room_at(c, lid) or room
        for k in (index[lid] - 1, index[lid] + 1):
            if 0 <= k < len(order):
                other = plan.room_at(c, order[k]["id"])
                if here is not None and other is not None:
                    join(node(here), node(other), f["id"])
    return edges, via


def _reach(edges: dict, start: str = "outside", avoid: tuple = ()) -> set:
    seen, todo = {start}, deque([start])
    while todo:
        n = todo.popleft()
        for m in edges.get(n, ()):
            if m in seen:
                continue
            seen.add(m)
            if m not in avoid:
                todo.append(m)
    return seen


def audit(building: Optional[dict]) -> dict:
    """``{"findings", "checked"}`` of the sense line (module docstring)."""
    from wenart.blender import architect_actions as AA

    b = building or {}
    if not b.get("rooms"):
        return {"findings": [], "checked": {}, "note": "no rooms"}
    edges, via = graph(b)
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    checked = [rid for rid, r in rooms.items() if AA.room_area(r) >= MIN_ROOM_M2 and not AA.Plan.is_outside(r)]
    out = []
    if not edges.get("outside"):
        out.append(K.finding("sense", "N4", "critical", "building", "the house has no entrance: no door or opening "
                             "joins a room to the outside", owner="reading", kind="no_sense", fix="gap_to_door"))
    reached = _reach(edges)
    wet = tuple(rid for rid, r in rooms.items() if str(r.get("room_type") or "").lower() in WET)
    dry_reached = _reach(edges, avoid=wet)
    for rid in checked:
        r = rooms[rid]
        name = f"{rid} ({r.get('label') or r.get('room_type')})"
        if rid not in reached:
            out.append(K.finding("sense", "N1", "critical", rid, f"room {name} on {r.get('level_id')} cannot be "
                                 f"reached from outside: no door, opening, open-plan join or stair leads to it",
                                 owner="reading", kind="no_sense", fix="gap_to_door",
                                 evidence={"neighbours": sorted(edges.get(rid, ()))}))
        elif rid not in dry_reached and rid not in wet:
            out.append(K.finding("sense", "N2", "major", rid, f"room {name} is reached only through a wet room "
                                 f"({', '.join(sorted(n for n in edges.get(rid, ()) if n in wet))})", owner="reading",
                                 kind="no_sense", fix="window_to_door"))
    levels = sorted(b.get("levels") or [], key=lambda lv: float(lv.get("elevation") or 0.0))
    for lv in levels[1:]:
        ids = [rid for rid in checked if rooms[rid].get("level_id") == lv["id"]]
        if ids and not any(rid in reached for rid in ids):
            out.append(K.finding("sense", "N3", "critical", lv["id"], f"level {lv['id']} cannot be reached: no stair "
                                 f"or door leads up to it", owner="reading", kind="no_sense"))
    return {"findings": out, "checked": {"rooms": len(checked), "joins": sum(len(v) for v in edges.values()) // 2,
                                         "reached": len([r for r in checked if r in reached])}}


VISION_METHODS = ("ai_two_pass", "ai_one_pass", "ai", "inferred", "rule", "none", None)


def misfits(building: dict, room_id: str, here: list[dict]) -> list[dict]:
    """27 Oct 2026 (real06's r_L1_oda_2: a drawn single bed typed "sofa" by two AI passes in a bedroom with no bed): the
    drawn pieces of the room the vision passes or a size rule typed (no block name, no name text, no code rule) as a
    type the room's type may not hold; most likely the piece its set misses."""
    try:
        from wenart.furniture import schemas as SC
        room = next(r for r in building.get("rooms") or [] if r.get("id") == room_id)
        allowed = set(SC.allowed_types(room.get("room_type"), room.get("room_subtype")))
    except Exception:  # noqa: BLE001 - no room or no type table: no suspects
        return []
    if not allowed:
        return []
    return [f for f in here if f.get("source") == "from_documents" and f.get("type") not in ("unknown", "other", "")
            and f.get("type") not in allowed and f.get("type_method") in VISION_METHODS
            and any(isinstance(e, dict) and e.get("method") in ("vector", "raster") for e in f.get("evidence") or [])]


def anchor_gap(building: dict, room_id: str, here: list[dict]) -> Optional[dict]:
    """27 Oct 2026 (pod run 091638, real06's r_L1_oda_2: a bedroom without a bed; no group check names a bedroom's
    missing bed, so N5 never looked): the room's missing anchor (``schemas.anchor_types``: a bedroom's beds) as a gap
    ``{"message", "metrics": {"missing": "a|b"}, "anchor": True}`` when no built piece of the room is one, else None."""
    try:
        from wenart.furniture import schemas as SC
        room = next(r for r in building.get("rooms") or [] if r.get("id") == room_id)
        anchors = SC.anchor_types(room.get("room_type"), room.get("room_subtype"))
    except Exception:  # noqa: BLE001 - no room or no table: no gap
        return None
    if not anchors or any(f.get("type") in anchors and f.get("build") is not False for f in here):
        return None
    return {"message": f"{room.get('room_type')} {room_id} has no {' / '.join(anchors)}",
            "metrics": {"missing": "|".join(anchors)}, "anchor": True}


def _fits_any(piece: dict, types: list[str]) -> bool:
    size = ((piece.get("footprint") or {}).get("size") or [])[:2]
    if len(size) < 2:
        return False
    try:
        from wenart.furniture import sizes as SZ
        return any(SZ.fits(t, [float(v) for v in size], 0.15) for t in types if t)
    except Exception:  # noqa: BLE001
        return False


def set_links(building: dict) -> list[dict]:
    """N5 (module docstring)."""
    try:
        from wenart.furniture import group_checks as GC

        res = GC.check_building(building)
    except Exception:  # noqa: BLE001 - no measure
        return []
    out = []
    rooms = list(dict.fromkeys(list(res["rooms"]) + [str(r.get("id")) for r in building.get("rooms") or []]))
    for room_id in rooms:
        vs = res["rooms"].get(room_id) or []
        gaps = [v for v in vs if v.get("check") in ("G9", "G10") and v.get("target") == room_id
                and (v.get("metrics") or {}).get("missing")]
        here = [f for f in building.get("furniture") or [] if f.get("room_id") == room_id]
        anchor = anchor_gap(building, room_id, here)
        if anchor is not None:
            gaps.append(anchor)
        if not gaps:
            continue
        suspects = [f for f in here if str(f.get("type")) in ("unknown", "other", "")
                    and (f.get("build") is not False or str(f.get("not_built_reason") or "").startswith("untyped"))
                    and any(isinstance(e, dict) and e.get("method") in ("vector", "raster")
                            for e in f.get("evidence") or [])]     # left out only for being untyped
        suspects += [f for f in here if f.get("build") is False and "answer to" in str(f.get("not_built_reason") or "")]
        suspects += misfits(building, room_id, here)
        for g in gaps:
            for f in suspects:
                if g.get("anchor") and not _fits_any(f, str(g["metrics"]["missing"]).split("|")):
                    continue                      # a room's missing anchor: only a piece of its size
                size = (f.get("footprint") or {}).get("size") or []
                hints = " / ".join(str(c.get("reason") or c.get("type"))[:90] for c in f.get("type_candidates") or [])
                out.append(K.finding("sense", "N5", "major", f["id"],
                                     f"{room_id}: {g['message']}, while {f['id']} "
                                     f"({f.get('type')}{', not built: ' + str(f.get('not_built_reason'))[:80] if f.get('build') is False else ''}"
                                     f"{', %.2f x %.2f m' % tuple(size[:2]) if len(size) >= 2 else ''}) stands in it"
                                     + (f"; the AI passes said: {hints}" if hints else "")
                                     + f": most likely the missing {g['metrics']['missing']}",
                                     owner="reading" if f.get("build") is not False or "untyped" in
                                     str(f.get("not_built_reason") or "") else "architect", kind="misread",
                                     fix="retype_piece", evidence={"room": room_id, "missing": g["metrics"]["missing"]}))
    return out


def run(inp) -> dict:
    """The line for ``report.LINE_MODULES``: the building as built (the scene's), else the final one."""
    building = inp.stage("build") or inp.final
    res = audit(building)
    res["findings"] = list(res.get("findings") or []) + (set_links(building) if building else [])
    return res
