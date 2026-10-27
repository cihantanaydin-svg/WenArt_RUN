"""The way up: every stair leads into its floors (27 Oct 2026, user on real06's first floor: "Needs a pathway here, how
will the people go up to 2nd floor otherwise?" and "Make argus catch these kind of things before me").

What (pure; the building JSON's dicts, shapely):

- ``walk_graph(building, level)``: the floor a visitor walks on: the level's room outlines minus the openings of its
  floor (the slab under it), the walls, the fixed equipment (``schemas.FIXED_TYPES``) and the stairs that rise from
  the level (their flights and half landing), narrowed by half the clear width ``WALK_CLEAR_M`` (where a 0.80 m wide
  person fits): the parts left ("cores") are joined by the doors and doorless openings (a door joins the cores its two
  approaches touch). The main floor of the level is the group of cores that holds the most rooms' floors.
- ``stair_ends(plan)``: where a stair is entered and left: the start area (``ARRIVAL_DEPTH_M`` before its first
  riser, the first flight's width, on its own level) and the arrival area (as deep, past its last riser and its apron,
  on the level above).
- ``assess(building, piece, level)``: whether a visitor walks from the stair's arrival into the main floor of the
  level above, and from the main floor of its own level onto its first step.
- ``opening_polygon(plan, soffit)``: the floor opening a stair needs: over every step with less than ``HEADROOM_M``
  under the slab above (from ``HEADROOM_MARGIN_M`` before the first such step), the half landing, the well between
  two flights side by side and the last flight up to its last riser; never the arrival floor. ``derived_opening`` is
  the same from a piece (the reading's ``sheets.to_building`` cuts the slabs with it).
- ``upper_reading(building, piece)``: the same U stair drawn on the plan of the next level up (one of its flights
  within ``UPPER_MATCH_M`` of one of ours) names the end of the half landing (the landing that plan draws, at least
  ``HALF_LANDING_MIN_M`` deep) and, when that plan draws one of the two flights only, the flight that arrives there
  (``direction_assumed`` false: the upper plan says it). ``read_across_levels`` applies it to every stair of a
  building (the reading, ``ingest.pipeline``).
- ``fix_arrivals(building)``: the build-time check and fix (``build.prepare``, before the slabs are planned): a stair
  whose arrival or start is cut off from its floor takes the first reading that leads into both floors: the upper
  plan's, the same reading with its derived opening cut again, the assumed rise direction flipped, the assumed half
  landing at the other end (``HALF_LANDING_MIN_M`` or the flights' width deep, stopped at the first wall), both; the
  opening is derived again for it (a drawn opening is kept) and every change is logged ``by: architect`` with the
  before and after and the reason. When no reading connects, the drawing is kept and the record says so; the
  architect's K4 reports both.
- ``flip(building, piece)``: the architect action ``flip_stair`` (an answer or a decision of the AI architect or of
  Argus): the other reading of a stair whose rise direction is assumed (the direction turned round, the half landing
  at the other end, both), the first that leads into both floors, its opening derived again; refused when the
  direction is drawn or no other reading leads in.
- ``walk_review(building)``: the model review's M9 on the built floors: (a) every stair's arrival and start reach
  the main floor, (b) every door of a room is reached from the room's main floor, (c) no part of a floor is cut off
  by a floor opening with no stair or door joining it.
- ``stair_rooms(building, piece)``: the room a stair starts in and the room it arrives in (Argus's sense line and
  the architect's circulation join these, never the rooms at the stair's centre).

Why: on real06's first floor the stair (no UP arrow read; the half landing taken from a 0.35 m strip at the wrong
end) arrived on a 0.9 m strip by the outer wall that the stair opening cut off from the hall: nobody could walk from
the stair into the rooms, and every check passed, because they joined the floors at the stair's centre. A stair makes
sense only when a person walks off it into the rooms, and onto it from them; that is measured here, for every stair
of every project.
"""
from __future__ import annotations

import copy
import math
from typing import Optional

from wenart import geometry as G

WALK_CLEAR_M = 0.80             # a visitor walks where the floor is at least this wide
ARRIVAL_DEPTH_M = 0.90          # the floor beyond the last riser (and before the first) a visitor steps onto
HALF_LANDING_MIN_M = 0.90       # a U stair's half landing is at least this deep (and at least its flights' width)
LANDING_TOL_M = 0.05            # ... less this drawing tolerance
LANDING_MIN_M = 0.60            # a half landing a wall cuts shorter than this is no reading
UPPER_MATCH_M = 0.05            # the same flight on the plan of the next level up: its line and one end within 5 cm
PARALLEL_SIN = math.sin(math.radians(2.0))
HEADROOM_M = 2.00               # clear height over a step under the slab above; less needs the floor opening
HEADROOM_MARGIN_M = 0.30        # the opening starts this far (about one going) before the first step that needs it
OPENING_GAP_M = 0.002           # the opening stands this far outside the steps (parametric.STAIR_SHAFT_GAP)
WELL_MAX_M = 0.60               # two flights side by side this close share the well between them in the opening
DOOR_APPROACH_M = 0.60          # a door's approach: this deep in front of its wall face, its width less 5 cm a side
TOUCH_M2 = 0.02                 # an approach or an end area shares at least this much with a walkable part
STEP_OFF_M2 = 0.20              # the floor past the last riser (outside the opening) a visitor must step onto
ROOM_CORE_M2 = 0.25             # a room's main floor covers at least this much of it
# 27 Oct 2026 (real04, two twin houses: each house's floor is a group of its own; the smaller one's stairs were "not
# on the main floor"): a building may hold several dwellings, each with its own floor. Every group holding at least
# MAIN_MIN_ROOMS rooms and MAIN_SHARE of the largest group's rooms is a main floor; a pocket holds fewer.
MAIN_MIN_ROOMS = 2
MAIN_SHARE = 0.5
PART_MIN_M2 = 0.50              # a cut-off part of a floor smaller than this is no place (M9 c)
ROOM_JOIN_M = 0.02              # room outlines this close are one floor (no wall between them)
ERODE_EPS_M = 0.01              # cores narrowed by half the clear width less this: a way of exactly 0.80 m passes
WALK_TYPES = ("door", "opening")


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------

def _poly(points):
    """A valid shapely polygon of ``points`` (None when degenerate)."""
    from shapely.geometry import Polygon
    try:
        p = Polygon([(float(q[0]), float(q[1])) for q in points])
    except (TypeError, ValueError, IndexError):
        return None
    if not p.is_valid:
        p = p.buffer(0)
    return p if not p.is_empty and p.area > 1e-9 else None


def _union(geoms):
    from shapely.ops import unary_union
    geoms = [g for g in geoms if g is not None and not g.is_empty]
    return unary_union(geoms) if geoms else None


def _parts(geom) -> list:
    """The polygons of a geometry (a polygon, a multipolygon or a collection)."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon" and not g.is_empty]


def _rect_of(fp: dict):
    try:
        return _poly(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def _wall_poly(w: dict):
    try:
        if G.distance(w["start"][:2], w["end"][:2]) < 1e-9:
            return None
        return _poly(G.centerline_to_rectangle(w["start"][:2], w["end"][:2], float(w.get("thickness") or 0.1)))
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def _band(c, r, hw: float, d0: float, d1: float):
    """The rectangle from ``d0`` to ``d1`` along the unit ``r`` from the point ``c``, ``hw`` to each side."""
    p = (-r[1], r[0])
    return _poly([(c[0] + r[0] * d0 + p[0] * hw, c[1] + r[1] * d0 + p[1] * hw),
                  (c[0] + r[0] * d1 + p[0] * hw, c[1] + r[1] * d1 + p[1] * hw),
                  (c[0] + r[0] * d1 - p[0] * hw, c[1] + r[1] * d1 - p[1] * hw),
                  (c[0] + r[0] * d0 - p[0] * hw, c[1] + r[1] * d0 - p[1] * hw)])


def _unit(v) -> Optional[tuple[float, float]]:
    n = math.hypot(float(v[0]), float(v[1]))
    return None if n < 1e-9 else (float(v[0]) / n, float(v[1]) / n)


def _dot(a, b) -> float:
    return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1])


def compass(v) -> str:
    """``north`` / ``east`` / ``south`` / ``west`` for a direction in plan (+Y north), else its degrees."""
    u = _unit(v) or (0.0, 1.0)
    deg = math.degrees(math.atan2(u[1], u[0])) % 360.0
    for name, at in (("east", 0.0), ("north", 90.0), ("west", 180.0), ("south", 270.0), ("east", 360.0)):
        if abs(deg - at) <= 10.0:
            return name
    return f"{deg:.0f} deg"


def _bounds(geom) -> str:
    x0, y0, x1, y1 = geom.bounds
    return f"x {x0:.2f}-{x1:.2f}, y {y0:.2f}-{y1:.2f}"


def _ring(poly) -> list:
    """The outer ring of a polygon as a counter-clockwise list of rounded points."""
    pts = [(round(x, 4) + 0.0, round(y, 4) + 0.0) for x, y in list(poly.exterior.coords)[:-1]]
    if G.polygon_signed_area(pts) < 0:
        pts.reverse()
    return [list(p) for p in pts]


# --------------------------------------------------------------------------
# Levels, slabs and the stairs as planned
# --------------------------------------------------------------------------

def _elev(lv: dict) -> float:
    return float(lv.get("elevation") or 0.0)


def _next_level(building: dict, level: dict, up: bool) -> Optional[dict]:
    z = _elev(level)
    rows = [lv for lv in building.get("levels") or [] if (_elev(lv) > z + 1e-6 if up else _elev(lv) < z - 1e-6)]
    if not rows:
        return None
    zz = min(_elev(lv) for lv in rows) if up else max(_elev(lv) for lv in rows)
    same = [lv for lv in rows if abs(_elev(lv) - zz) <= 1e-6]
    base = [lv for lv in same if not lv.get("base_level_id")]
    return (base or same)[0]


def level_above(building: dict, level: dict) -> Optional[dict]:
    """The level directly above ``level`` (the lowest elevation over it; a base level before an alternative)."""
    return _next_level(building, level, True)


def level_below(building: dict, level: dict) -> Optional[dict]:
    return _next_level(building, level, False)


def _level(building: dict, level_id) -> Optional[dict]:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)


def slab_under(building: dict, level_id) -> Optional[dict]:
    """The building's slab under ``level_id`` (``above_level_id``; the base one before a variant's)."""
    rows = [s for s in building.get("slabs") or [] if isinstance(s, dict) and s.get("above_level_id") == level_id]
    base = [s for s in rows if not s.get("variants")]
    return (base or rows or [None])[0]


def floor_voids(building: dict, level_id) -> list[tuple]:
    """``[(opening id, polygon)]``: the openings of the floor of ``level_id`` (the slab under it)."""
    out = []
    for o in (slab_under(building, level_id) or {}).get("openings") or []:
        p = _poly(o.get("polygon") or []) if isinstance(o, dict) and len(o.get("polygon") or []) >= 3 else None
        if p is not None:
            out.append((o.get("id"), p))
    return out


def soffit_over(building: dict, level: dict) -> Optional[float]:
    """The underside of the slab over ``level``, above its floor (m); None without a level above."""
    up = level_above(building, level)
    if up is None:
        return None
    slab = slab_under(building, up["id"])
    try:
        thick = float((slab or {}).get("thickness") or 0.0)
    except (TypeError, ValueError):
        thick = 0.0
    if thick <= 0.0:
        from wenart.blender import parametric as P
        thick = P.STAIR_SLAB_M
    return _elev(up) - _elev(level) - thick


def planned(building: dict, level: dict) -> list[dict]:
    """The stairs of ``level`` as the shell builds them (``shell.plan_stairs``: the floor of the level above cut over
    them when there is one); [] when they cannot be planned (a level without its heights)."""
    from wenart.blender import shell
    try:
        return shell.plan_stairs(building, level, slab_void=level_above(building, level) is not None)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError):
        return []


def stair_area(plan: dict):
    """The floor a planned stair takes on its own level: its flights (first to last riser, across their width) and
    its half landing (or winders)."""
    parts = []
    for f in plan.get("flights") or []:
        r = f["rise_dir"]
        a, b = f["nosings"][0], f["nosings"][-1]
        d = max(G.distance(a, b), float(f.get("going") or 0.25))
        parts.append(_band(a, r, float(f["width"]) / 2.0, 0.0, d))
    land = plan.get("landing")
    if isinstance(land, dict) and land.get("role") in ("mid", "winders"):
        parts.append(_poly(land.get("polygon") or []))
    return _union(parts)


def stair_ends(plan: dict) -> Optional[dict]:
    """``{"arrival", "start", "arrival_at", "start_at"}`` of a planned stair (module docstring): polygons and the
    middle of the last riser (past the apron) and of the first riser."""
    flights = plan.get("flights") or []
    if not flights:
        return None
    first, last = flights[0], flights[-1]
    r = last["rise_dir"]
    apron = float(plan.get("top_apron") or 0.0)
    c = last["nosings"][-1]
    arrival = _band(c, r, float(last["width"]) / 2.0, apron, apron + ARRIVAL_DEPTH_M)
    land = plan.get("landing")
    if isinstance(land, dict) and land.get("role") == "top":
        arrival = _union([arrival, _poly(land.get("polygon") or [])])     # a top landing is the arrival floor
    r0 = first["rise_dir"]
    s = first["nosings"][0]
    start = _band(s, r0, float(first["width"]) / 2.0, -ARRIVAL_DEPTH_M, 0.0)
    return {"arrival": arrival, "start": start, "arrival_at": (c[0] + r[0] * apron, c[1] + r[1] * apron),
            "start_at": (float(s[0]), float(s[1])), "arrival_dir": tuple(r), "start_dir": tuple(r0)}


def _tops(items: list[dict]) -> list:
    """The top landings (at the floor of the level above) of planned stairs."""
    out = []
    for it in items or []:
        land = (it.get("plan") or {}).get("landing")
        if isinstance(land, dict) and land.get("role") == "top":
            p = _poly(land.get("polygon") or [])
            if p is not None:
                out.append(p)
    return out


# --------------------------------------------------------------------------
# The walk on one floor
# --------------------------------------------------------------------------

def _fixed_types() -> tuple:
    try:
        from wenart.furniture import schemas as SC
        return tuple(t for t in SC.FIXED_TYPES if t != "stair")
    except Exception:  # noqa: BLE001 - the table is optional for the walk
        return ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge", "washing_machine", "toilet",
                "washbasin", "shower", "bathtub")


def door_sides(plan, o: dict) -> list[tuple]:
    """``[(room or None, approach polygon)]`` on the two sides of a door's wall (``architect_actions.window_sides``
    order): the approach is ``DOOR_APPROACH_M`` deep in front of the wall face, the door's width less 5 cm a side."""
    from wenart.blender import architect_actions as AA
    w = plan.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return []
    a, u, _ = plan.axis(w)
    n = (-u[1], u[0])
    t = plan.t_of(w, o["center"])
    c = (a[0] + u[0] * t, a[1] + u[1] * t)
    face = float(w.get("thickness") or 0.2) / 2.0
    half = max(0.15, float(o.get("width") or 0.8) / 2.0 - 0.05)
    rooms = AA.window_sides(plan, o)
    out = []
    for k, sgn in enumerate((1.0, -1.0)):
        p0 = (c[0] + n[0] * sgn * face, c[1] + n[1] * sgn * face)
        p1 = (c[0] + n[0] * sgn * (face + DOOR_APPROACH_M), c[1] + n[1] * sgn * (face + DOOR_APPROACH_M))
        rect = _poly([(p0[0] - u[0] * half, p0[1] - u[1] * half), (p0[0] + u[0] * half, p0[1] + u[1] * half),
                      (p1[0] + u[0] * half, p1[1] + u[1] * half), (p1[0] - u[0] * half, p1[1] - u[1] * half)])
        out.append((rooms[k] if k < len(rooms) else None, rect))
    return out


def walk_graph(building: dict, level: dict, voids: Optional[list] = None, items: Optional[list] = None,
               tops: Optional[list] = None) -> dict:
    """The walk on one floor (module docstring). ``voids``: ``[(id, polygon)]`` instead of the floor's openings;
    ``items``: the level's planned stairs (``planned``); ``tops``: the top landings of the stairs of the level below
    (floor at this level). Returns ``{"level_id", "free", "cores", "opened", "group", "doors", "room_main", "main",
    "holes", "rooms", "obstacles"}``: ``opened[i]`` is the floor a visitor reaches from core ``i`` (its 0.80 m wide
    places), ``group[i]`` the cores joined to it by doors, ``doors`` ``[{"id", "type", "rooms", "approach",
    "touch"}]`` (per side the cores its approach touches), ``room_main`` the main core of each room, ``main`` the
    group of the main floor."""
    from wenart.blender import architect_actions as AA

    lid = level["id"]
    rooms = {}
    for r in building.get("rooms") or []:
        if r.get("level_id") == lid and len(r.get("polygon") or []) >= 3:
            p = _poly(r["polygon"])
            if p is not None:
                rooms[r["id"]] = p
    holes = list(floor_voids(building, lid)) if voids is None else [(i, p) for i, p in voids if p is not None]
    out = {"level_id": lid, "free": None, "cores": [], "opened": [], "group": [], "doors": [], "room_main": {},
           "main": None, "holes": holes, "rooms": rooms, "obstacles": []}
    if not rooms:
        return out
    floor = _union([p.buffer(ROOM_JOIN_M, join_style=2) for p in rooms.values()]).buffer(-ROOM_JOIN_M, join_style=2)
    walls = [_wall_poly(w) for w in building.get("walls") or [] if w.get("level_id") == lid]
    fixed = _fixed_types()
    obstacles = []
    for f in building.get("furniture") or []:
        if f.get("level_id") == lid and f.get("type") in fixed and f.get("build") is not False:
            p = _rect_of(f.get("footprint") or {})
            if p is not None:
                obstacles.append((f.get("id"), p))
    items = planned(building, level) if items is None else items
    for it in items:
        if it.get("plan"):
            p = stair_area(it["plan"])
            if p is not None:
                obstacles.append((it["piece"].get("id"), p))
    if tops is None:
        below = level_below(building, level)
        tops = _tops(planned(building, below)) if below is not None else []
    cut = _union([p for _, p in holes] + walls + [p for _, p in obstacles])
    free = floor.difference(cut) if cut is not None else floor
    if tops:
        free = free.union(_union(tops))
    r = WALK_CLEAR_M / 2.0 - ERODE_EPS_M
    cores = _parts(free.buffer(-r))
    opened = [c.buffer(r).intersection(free) for c in cores]
    plan = AA.Plan(building)
    doors = []
    for o in building.get("openings") or []:
        if o.get("level_id") != lid or o.get("type") not in WALK_TYPES or o.get("build") is False:
            continue
        sides = door_sides(plan, o)
        if not sides:
            continue
        touch = [[i for i, op in enumerate(opened) if app is not None and op.intersection(app).area >= TOUCH_M2]
                 for _, app in sides]
        doors.append({"id": o.get("id"), "type": o.get("type"),
                      "rooms": [rm["id"] if rm is not None and not AA.Plan.is_outside(rm) else None for rm, _ in sides],
                      "approach": [app for _, app in sides], "touch": touch})
    parent = list(range(len(cores)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for d in doors:
        ids = d["touch"][0] + d["touch"][1]
        for j in ids[1:]:
            a, b = find(ids[0]), find(j)
            if a != b:
                parent[b] = a
    group = [find(i) for i in range(len(cores))]
    room_main = {}
    for rid, p in rooms.items():
        best = max(((op.intersection(p).area, i) for i, op in enumerate(opened)), default=(0.0, None))
        if best[1] is not None and best[0] >= ROOM_CORE_M2:
            room_main[rid] = best[1]
    count: dict = {}
    area: dict = {}
    for rid, i in room_main.items():
        count[group[i]] = count.get(group[i], 0) + 1
    for i, op in enumerate(opened):
        area[group[i]] = area.get(group[i], 0.0) + op.area
    main = max(set(group), key=lambda g: (count.get(g, 0), area.get(g, 0.0))) if group else None
    top = count.get(main, 0) if main is not None else 0
    mains = {g for g in set(group) if count.get(g, 0) >= max(MAIN_MIN_ROOMS, MAIN_SHARE * top)}
    if main is not None:
        mains.add(main)
    out.update(free=free, cores=cores, opened=opened, group=group, doors=doors, room_main=room_main, main=main,
               mains=mains, obstacles=obstacles)
    return out


def reach(graph: dict, area) -> dict:
    """Where a visitor gets from ``area`` on the floor of ``graph`` (``walk_graph``): ``{"ok", "pocket", "floor_m2",
    "main", "rooms", "missed", "doors", "room"}``. ``ok``: at least ``STEP_OFF_M2`` of floor there and a part of the
    main floor touched (None when the floor cannot be measured: no rooms); ``pocket``: not ok and no room's main floor
    reached at all (a strip or a corner the openings and walls close off, or no floor); ``rooms``: the rooms whose main
    floor is reached, ``missed`` the others; ``room``: the room most of the area's floor lies in."""
    if graph.get("free") is None or area is None:
        return {"ok": None, "pocket": None, "floor_m2": 0.0, "main": None, "rooms": [], "missed": [], "doors": [],
                "room": None}
    floor = area.intersection(graph["free"])
    touch = [i for i, op in enumerate(graph["opened"]) if op.intersection(area).area >= TOUCH_M2]
    groups = {graph["group"][i] for i in touch}
    mains = graph.get("mains") or ({graph["main"]} if graph["main"] is not None else set())
    main = bool(groups & mains) if graph["main"] is not None else None
    rooms = sorted(rid for rid, i in graph["room_main"].items() if graph["group"][i] in groups)
    missed = sorted(rid for rid, i in graph["room_main"].items() if graph["group"][i] not in groups)
    doors = sorted(str(d["id"]) for d in graph["doors"] if any(graph["group"][i] in groups for s in d["touch"]
                                                                  for i in s))
    best = max(((floor.intersection(p).area, rid) for rid, p in graph["rooms"].items()), default=(0.0, None))
    ok = None if main is None else (floor.area >= STEP_OFF_M2 and bool(main))
    pocket = None if ok is None else (not ok and (floor.area < STEP_OFF_M2 or not rooms))
    return {"ok": ok, "pocket": pocket, "floor_m2": round(floor.area, 3), "main": main, "rooms": rooms,
            "missed": missed, "doors": doors, "room": best[1] if best[0] > 1e-6 else None}


def assess(building: dict, piece: dict, level: Optional[dict] = None, items: Optional[list] = None) -> dict:
    """The walk from a stair into its floors (module docstring): ``{"stair", "level_id", "up_level_id", "judged",
    "ok", "arrival", "start", "plan", "ends"}`` (``arrival`` / ``start``: ``reach`` on the level above and on its own
    level). ``judged`` false (with ``note``) when the stair has no plan or no level above."""
    pid = piece.get("id")
    level = level or _level(building, piece.get("level_id"))
    up = level_above(building, level) if level is not None else None
    rec = {"stair": pid, "level_id": (level or {}).get("id"), "up_level_id": (up or {}).get("id"), "judged": False,
           "ok": None}
    if level is None or up is None:
        return dict(rec, note="no level above")
    items = planned(building, level) if items is None else items
    it = next((x for x in items if x["piece"].get("id") == pid), None)
    if it is None or not it.get("plan") or not it["plan"].get("flights"):
        return dict(rec, note="not built" if it is not None else "not planned")
    ends = stair_ends(it["plan"])
    arr = reach(walk_graph(building, up, tops=_tops(items)), ends["arrival"])
    st = reach(walk_graph(building, level, items=items), ends["start"])
    ok = arr["ok"] is not False and st["ok"] is not False
    return dict(rec, judged=True, ok=ok, arrival=arr, start=st, plan=it["plan"], ends=ends)


# --------------------------------------------------------------------------
# The opening a stair needs
# --------------------------------------------------------------------------

def opening_polygon(plan: dict, soffit: float) -> Optional[list]:
    """The floor opening of a planned stair (module docstring), counter-clockwise, rounded to 0.1 mm; None without
    flights. ``soffit``: the underside of the slab above, over the stair's floor (m)."""
    from wenart.blender import geom2d

    flights = plan.get("flights") or []
    if not flights:
        return None
    riser = float(plan.get("riser_m") or 0.0)
    o = flights[0]["nosings"][0]
    u = flights[0]["rise_dir"]
    v = (u[1], -u[0])

    def to_f(p):
        q = (p[0] - o[0], p[1] - o[1])
        return (_dot(q, v), _dot(q, u))

    def from_f(q):
        return (o[0] + v[0] * q[0] + u[0] * q[1], o[1] + v[1] * q[0] + u[1] * q[1])

    def box(points):
        fs = [to_f(p) for p in points]
        return (min(p[0] for p in fs), min(p[1] for p in fs), max(p[0] for p in fs), max(p[1] for p in fs))

    boxes = []
    for k, f in enumerate(flights):
        r, g, n = f["rise_dir"], float(f["going"]), len(f["nosings"])
        need = [i for i in range(n) if soffit - (float(f["base_z"]) + (i + 1) * riser) < HEADROOM_M - 1e-9]
        if not need and k < len(flights) - 1:
            continue                                   # the whole flight has its headroom under the floor above
        i0 = need[0] if need else n - 1
        d0 = max(0.0, i0 * g - HEADROOM_MARGIN_M)
        d1 = max((n - 1) * g, d0 + 1e-3)
        s, hw = f["nosings"][0], float(f["width"]) / 2.0
        p = (-r[1], r[0])
        a, b = (s[0] + r[0] * d0, s[1] + r[1] * d0), (s[0] + r[0] * d1, s[1] + r[1] * d1)
        boxes.append(box([(a[0] + p[0] * hw, a[1] + p[1] * hw), (a[0] - p[0] * hw, a[1] - p[1] * hw),
                          (b[0] + p[0] * hw, b[1] + p[1] * hw), (b[0] - p[0] * hw, b[1] - p[1] * hw)]))
    flight_boxes = list(boxes)
    for i, a in enumerate(flight_boxes):                # the well between two flights side by side
        for b in flight_boxes[i + 1:]:
            lo, hi = max(a[1], b[1]), min(a[3], b[3])
            gap0, gap1 = (a[2], b[0]) if a[2] <= b[0] else (b[2], a[0])
            if hi - lo > 1e-3 and 0.0 < gap1 - gap0 <= WELL_MAX_M:
                boxes.append((gap0, lo, gap1, hi))
    land = plan.get("landing")
    if isinstance(land, dict) and land.get("role") in ("mid", "winders", "top") and len(land.get("polygon") or []) >= 3:
        boxes.append(box(land["polygon"]))
    if not boxes:
        return None
    gp = OPENING_GAP_M
    loops = geom2d.rect_union_outline([(b[0] - gp, b[1] - gp, b[2] + gp, b[3] + gp) for b in boxes])
    if not loops:
        return None
    best = max(loops, key=lambda lp: abs(G.polygon_signed_area(lp)))
    pts = [from_f(q) for q in best]
    poly = _poly(pts)
    return _ring(poly) if poly is not None else None


def derived_opening(piece: dict, rise: float, soffit: float) -> Optional[list]:
    """``opening_polygon`` of a stair piece with drawn flights (``parametric.stair_plan`` with ``rise`` floor to floor
    and the slab underside ``soffit``); None for a stair without drawn flights (its footprint stays the opening)."""
    from wenart.blender import parametric as P
    data = P.stair_data(piece)
    if not data or not data.get("flights"):
        return None
    try:
        plan = P.stair_plan(piece, float(rise), float(soffit), float(soffit) + P.STAIR_SHAFT_CAP_M, ())
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError):
        return None
    if plan.get("generic"):
        return None
    return opening_polygon(plan, float(soffit))


# --------------------------------------------------------------------------
# The readings of a stair
# --------------------------------------------------------------------------

def _flights(data: dict) -> list[dict]:
    out = []
    for f in (data or {}).get("flights") or []:
        try:
            s, e = (float(f["start"][0]), float(f["start"][1])), (float(f["end"][0]), float(f["end"][1]))
            w = float(f["width"])
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        a = _unit((e[0] - s[0], e[1] - s[1]))
        if a is not None and w > 0:
            out.append({"start": s, "end": e, "width": w, "axis": a})
    return out


def _frame(fl: list[dict]) -> dict:
    """The frame of a stair's drawn flights: origin and axis of flight 1, the span along it (``s_lo``, ``s_hi``) and
    across (``v_lo``, ``v_hi``)."""
    o, u = fl[0]["start"], fl[0]["axis"]
    v = (-u[1], u[0])
    ss, vs = [], []
    for f in fl:
        for p in (f["start"], f["end"]):
            q = (p[0] - o[0], p[1] - o[1])
            ss.append(_dot(q, u))
            c = _dot(q, v)
            vs += [c - f["width"] / 2.0, c + f["width"] / 2.0]
    return {"o": o, "u": u, "v": v, "s_lo": min(ss), "s_hi": max(ss), "v_lo": min(vs), "v_hi": max(vs)}


def _at(fr: dict, s: float, v: float) -> tuple[float, float]:
    o, u, w = fr["o"], fr["u"], fr["v"]
    return (o[0] + u[0] * s + w[0] * v, o[1] + u[1] * s + w[1] * v)


def _s_of(fr: dict, p) -> float:
    return _dot((p[0] - fr["o"][0], p[1] - fr["o"][1]), fr["u"])


def is_u(data: dict) -> bool:
    """Two drawn flights side by side, parallel (a U-turn stair)."""
    fl = _flights(data)
    if len(fl) != 2:
        return False
    a, b = fl
    cross = abs(a["axis"][0] * b["axis"][1] - a["axis"][1] * b["axis"][0])
    return cross <= PARALLEL_SIN


def half_landing_need(data: dict) -> float:
    """How deep a half landing of this stair must be: its widest flight, at least ``HALF_LANDING_MIN_M``."""
    return max([HALF_LANDING_MIN_M] + [f["width"] for f in _flights(data)])


def landing_end(data: dict) -> Optional[str]:
    """``"hi"`` / ``"lo"``: the end of the flights (along flight 1's drawn axis) the recorded landing lies at."""
    fl = _flights(data)
    land = (data or {}).get("landing")
    poly = land.get("polygon") if isinstance(land, dict) else None
    if not fl or not poly or len(poly) < 3:
        return None
    fr = _frame(fl)
    c = G.polygon_centroid([(float(p[0]), float(p[1])) for p in poly])
    return "hi" if _s_of(fr, c) > (fr["s_lo"] + fr["s_hi"]) / 2.0 else "lo"


def landing_movable(data: dict) -> bool:
    """The half landing's end is not drawn: the reading assumed it (``landing_assumed``), or an older reading kept a
    strip thinner than a half landing (``half_landing_need`` less ``LANDING_TOL_M``) at that end."""
    if not is_u(data) or not isinstance((data or {}).get("landing"), dict):
        return False
    if data.get("landing_assumed") is not None:
        return bool(data["landing_assumed"])
    try:
        depth = float(data["landing"].get("depth"))
    except (TypeError, ValueError):
        return data.get("turn_assumed", True) is not False
    return depth < half_landing_need(data) - LANDING_TOL_M


def _wall_stop(walls: list, fr: dict, s0: float, sgn: float, depth: float) -> float:
    """How far the floor beyond the flights' end ``s0`` reaches (along ``sgn`` x the axis, at most ``depth``) before
    the first wall that crosses the middle of the flights' span (three rays: the middle and 0.1 m in from each
    side)."""
    from shapely.geometry import LineString
    polys = [p for p in walls if p is not None]
    if not polys:
        return depth
    wall = _union(polys)
    best = depth
    for v in ((fr["v_lo"] + fr["v_hi"]) / 2.0, fr["v_lo"] + 0.1, fr["v_hi"] - 0.1):
        a = _at(fr, s0 + sgn * 0.01, v)
        b = _at(fr, s0 + sgn * depth, v)
        hit = LineString([a, b]).intersection(wall)
        if hit.is_empty:
            continue
        pts = [c for g in getattr(hit, "geoms", [hit]) for c in getattr(g, "coords", [])]
        if pts:
            best = min(best, min(G.distance(a, p) for p in pts) + 0.01)
    return max(0.0, best)


def _landing_at(data: dict, end: str, depth: float, walls: list) -> Optional[dict]:
    """A half landing across the flights' span at ``end``, ``depth`` deep, stopped at the first wall; None when the
    walls leave less than ``LANDING_MIN_M``."""
    fl = _flights(data)
    if not fl:
        return None
    fr = _frame(fl)
    sgn = 1.0 if end == "hi" else -1.0
    s0 = fr["s_hi"] if end == "hi" else fr["s_lo"]
    d = _wall_stop(walls, fr, s0, sgn, depth)
    if d < LANDING_MIN_M:
        return None
    s1 = s0 + sgn * d
    pts = [_at(fr, s0, fr["v_lo"]), _at(fr, s0, fr["v_hi"]), _at(fr, s1, fr["v_hi"]), _at(fr, s1, fr["v_lo"])]
    poly = _poly(pts)
    if poly is None:
        return None
    return {"polygon": _ring(poly), "depth": round(d, 4)}


def _level_walls(building: dict, level_id) -> list:
    return [_wall_poly(w) for w in building.get("walls") or [] if w.get("level_id") == level_id]


def flipped(data: dict) -> dict:
    """The reading with the rise direction turned round (still assumed: no drawing says it)."""
    out = copy.deepcopy(data)
    d = out.get("direction")
    fl = _flights(out)
    vec = _unit(d) if isinstance(d, (list, tuple)) and len(d) >= 2 else (fl[0]["axis"] if fl else None)
    if vec is not None:
        out["direction"] = [round(-vec[0], 4) + 0.0, round(-vec[1], 4) + 0.0]
    out["direction_assumed"] = True
    return out


def moved_landing(data: dict, walls: list) -> Optional[dict]:
    """The reading with the half landing at the other end of the flights (``half_landing_need`` deep, stopped at the
    first wall; ``landing_assumed`` stays true); None when it is no U stair or no half landing fits there."""
    if not is_u(data):
        return None
    end = landing_end(data)
    if end is None:
        return None
    land = _landing_at(data, "lo" if end == "hi" else "hi", half_landing_need(data), walls)
    if land is None:
        return None
    out = copy.deepcopy(data)
    out["landing"] = land
    out["landing_assumed"] = True
    return out


def _same_flight(a: dict, b: dict) -> bool:
    """Flight ``b`` (another plan) is flight ``a``: parallel, its line within ``UPPER_MATCH_M``, one of its ends
    within ``UPPER_MATCH_M`` of one of ``a``'s and the widths within twice that."""
    cross = abs(a["axis"][0] * b["axis"][1] - a["axis"][1] * b["axis"][0])
    if cross > PARALLEL_SIN or abs(a["width"] - b["width"]) > 2 * UPPER_MATCH_M:
        return False
    n = (-a["axis"][1], a["axis"][0])
    off = abs(_dot((b["start"][0] - a["start"][0], b["start"][1] - a["start"][1]), n))
    if off > UPPER_MATCH_M:
        return False
    return min(G.distance(p, q) for p in (a["start"], a["end"]) for q in (b["start"], b["end"])) <= UPPER_MATCH_M


def upper_match(building: dict, piece: dict) -> Optional[dict]:
    """The same U stair drawn on the plan of the next level up (module docstring): ``{"piece", "level_id", "end",
    "depth", "arrives"}`` (``arrives``: the index of our flight that plan draws alone, else None), or None when no
    stair there matches, or it draws no half landing beyond one end of our flights."""
    data = (piece or {}).get("stair")
    if not isinstance(data, dict) or not is_u(data):
        return None
    level = _level(building, piece.get("level_id"))
    up = level_above(building, level) if level is not None else None
    if up is None:
        return None
    ours = _flights(data)
    fr = _frame(ours)
    for t in building.get("furniture") or []:
        if t is piece or t.get("type") != "stair" or t.get("level_id") != up["id"]:
            continue
        td = t.get("stair") if isinstance(t.get("stair"), dict) else {}
        theirs = _flights(td)
        matched = sorted({i for i, a in enumerate(ours) for b in theirs if _same_flight(a, b)})
        if not matched:
            continue
        land = td.get("landing")
        poly = land.get("polygon") if isinstance(land, dict) else None
        if not poly or len(poly) < 3 or td.get("landing_assumed") is True:
            continue
        ss = [_s_of(fr, p) for p in poly]
        l0, l1 = min(ss), max(ss)
        if l1 - l0 < HALF_LANDING_MIN_M - LANDING_TOL_M:
            continue                                   # a strip, no half landing
        if l0 >= fr["s_hi"] - UPPER_MATCH_M:
            end, depth = "hi", l1 - fr["s_hi"]
        elif l1 <= fr["s_lo"] + UPPER_MATCH_M:
            end, depth = "lo", fr["s_lo"] - l0
        else:
            continue
        return {"piece": t, "level_id": up["id"], "end": end, "depth": round(depth, 4),
                "arrives": matched[0] if len(matched) == 1 and len(theirs) == 1 else None}
    return None


def upper_reading(building: dict, piece: dict) -> Optional[dict]:
    """The stair record as the plan of the next level up draws it (``upper_match``): the half landing at the end that
    plan draws its landing (as deep as drawn, stopped at the first wall of our level), and, when it draws only one of
    the two flights, the rise direction that makes that flight arrive (``direction_assumed`` false). None when no
    such plan exists or it says what the record already says."""
    m = upper_match(building, piece)
    if m is None:
        return None
    data = piece["stair"]
    land = _landing_at(data, m["end"], max(m["depth"], LANDING_MIN_M), _level_walls(building, piece.get("level_id")))
    if land is None:
        return None
    out = copy.deepcopy(data)
    out["landing"] = land
    out["landing_assumed"] = False
    out["landing_source"] = "upper plan"
    fl = _flights(out)
    fr = _frame(fl)
    towards = fr["u"] if m["end"] == "hi" else (-fr["u"][0], -fr["u"][1])
    say = f"the plan of {m['level_id']} draws the same stair ({m['piece'].get('id')}) with its landing at the " \
          f"{compass(towards)} end: the half landing is there, {land['depth']:.2f} m deep"
    if m["arrives"] is not None:
        first_up = m["arrives"] != 0            # flight 1 rises to the landing when the other flight arrives
        d = towards if first_up else (-towards[0], -towards[1])
        out["direction"] = [round(d[0], 4) + 0.0, round(d[1], 4) + 0.0]
        out["direction_assumed"] = False
        out["turn_assumed"] = False
        out["direction_source"] = "upper plan"
        a = fl[m["arrives"]]
        say += (f"; it draws only the flight at ({(a['start'][0] + a['end'][0]) / 2:.2f}, "
                f"{(a['start'][1] + a['end'][1]) / 2:.2f}): that flight arrives on {m['level_id']}")
    out["reason"] = say
    out["upper_plan"] = {"piece_id": m["piece"].get("id"), "level_id": m["level_id"], "landing_depth": m["depth"],
                         "arrives": m["arrives"]}
    same = (landing_end(out) == landing_end(data)
            and _unit(out.get("direction") or (0, 0)) == _unit(data.get("direction") or (0, 0))
            and abs(float((data.get("landing") or {}).get("depth") or 0.0) - land["depth"]) < 0.01)
    return None if same else out


def fit_footprint(piece: dict) -> None:
    """The piece's footprint around its drawn flights and its half landing (in its own rotation), the drawn one kept
    as ``drawn_footprint`` (in place)."""
    data = piece.get("stair") if isinstance(piece.get("stair"), dict) else {}
    fl = _flights(data)
    fp = piece.get("footprint") or {}
    if not fl or not fp:
        return
    rot = float(fp.get("rotation_deg") or 0.0)
    ex = G.rotate_point((1.0, 0.0), rot)
    ey = G.rotate_point((0.0, 1.0), rot)
    pts = []
    for f in fl:
        n = (-f["axis"][1], f["axis"][0])
        hw = f["width"] / 2.0
        pts += [(p[0] + n[0] * s * hw, p[1] + n[1] * s * hw) for p in (f["start"], f["end"]) for s in (-1, 1)]
    land = data.get("landing")
    if isinstance(land, dict):
        pts += [(float(p[0]), float(p[1])) for p in land.get("polygon") or []]
    xs = [_dot(p, ex) for p in pts]
    ys = [_dot(p, ey) for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    piece.setdefault("drawn_footprint", copy.deepcopy(fp))
    piece["footprint"] = {"center": [round(ex[0] * cx + ey[0] * cy, 4), round(ex[1] * cx + ey[1] * cy, 4)],
                          "size": [round(max(xs) - min(xs), 4), round(max(ys) - min(ys), 4)], "rotation_deg": rot}


def read_across_levels(building: dict) -> list[dict]:
    """The reading's step (``ingest.pipeline``, before the slabs are cut; pure, in place): every U stair the plan of
    the next level up draws again takes that plan's half landing and arriving flight (``upper_reading``); its
    footprint covers its flights and that landing (the drawn one kept), it is labelled ``adjusted_by_ai`` (by code)
    and the upper plan's stair joins its evidence. Returns ``[{"stair", "reason"}]``."""
    out = []
    for piece in building.get("furniture") or []:
        if piece.get("type") != "stair" or not isinstance(piece.get("stair"), dict):
            continue
        new = upper_reading(building, piece)
        if new is None:
            continue
        upper = next((t for t in building.get("furniture") or [] if t.get("id") == new["upper_plan"]["piece_id"]), {})
        piece["stair"] = new
        fit_footprint(piece)
        piece.setdefault("adjusted_by_ai", {"by": "code", "rule": "stair_upper_plan", "reason": new["reason"]})
        ev = next((e for e in upper.get("evidence") or [] if isinstance(e, dict)), None)
        if ev is not None:
            piece.setdefault("evidence", []).append(dict(ev, rule="stair_upper_plan",
                                                         note=f"the same stair on the plan of {upper.get('level_id')}"))
        out.append({"stair": piece.get("id"), "reason": new["reason"]})
    return out


# --------------------------------------------------------------------------
# The build-time check and fix
# --------------------------------------------------------------------------

def _opening_of(building: dict, up_id, piece: dict) -> tuple[Optional[dict], Optional[dict]]:
    """``(slab, opening)``: the opening of the floor of ``up_id`` cut for ``piece`` (its ``furniture_id``, else one
    over its footprint)."""
    slab = slab_under(building, up_id)
    if slab is None:
        return None, None
    ops = [o for o in slab.get("openings") or [] if isinstance(o, dict)]
    o = next((o for o in ops if o.get("furniture_id") == piece.get("id")), None)
    if o is None:
        fp = _rect_of(piece.get("footprint") or {})
        o = next((o for o in ops if fp is not None and (_poly(o.get("polygon") or []) or fp).intersection(fp).area
                  > 0.25 * fp.area), None)
    return slab, o


def _with(building: dict, piece: dict, data: dict, level: dict, recut: bool) -> tuple[dict, dict, Optional[list]]:
    """``(building copy, piece copy, new opening polygon)``: ``building`` with ``piece`` read as ``data`` and, when
    ``recut``, its floor opening derived again (the slabs copied)."""
    p2 = copy.deepcopy(piece)
    p2["stair"] = copy.deepcopy(data)
    fit_footprint(p2)
    b2 = dict(building, furniture=[p2 if f is piece else f for f in building.get("furniture") or []])
    if not recut:
        return b2, p2, None
    up = level_above(building, level)
    soffit = soffit_over(building, level)
    it = next((x for x in planned(b2, level) if x["piece"].get("id") == p2.get("id")), None)
    if up is None or soffit is None or it is None or not it.get("plan"):
        return b2, p2, None
    poly = opening_polygon(it["plan"], soffit)
    if poly is None:
        return b2, p2, None
    slabs = copy.deepcopy(building.get("slabs") or [])
    b2["slabs"] = slabs
    slab, o = _opening_of(b2, up["id"], piece)
    if slab is None:
        return b2, p2, None
    if o is None:
        n = len(slab.setdefault("openings", [])) + 1
        o = {"id": f"sv_{up['id']}_{n:03d}", "kind": "stair_void", "furniture_id": p2.get("id"), "source": "derived"}
        slab["openings"].append(o)
    o["polygon"] = poly
    return b2, p2, poly


def _summary(rec: dict) -> dict:
    out = {}
    for key in ("arrival", "start"):
        r = rec.get(key) or {}
        out[key] = {k: r.get(k) for k in ("ok", "floor_m2", "room", "rooms", "missed")}
    ends = rec.get("ends") or {}
    if ends:
        out["arrival"]["at"] = [round(c, 3) for c in ends["arrival_at"]]
        out["arrival"]["towards"] = compass(ends["arrival_dir"])
        out["start"]["at"] = [round(c, 3) for c in ends["start_at"]]
    return out


def candidates(building: dict, piece: dict, level: dict) -> list[tuple[str, dict, bool]]:
    """The readings to try for a stair cut off from its floor, in order: ``[(name, stair record, recut)]``
    (``recut``: the floor opening is derived again for it; a drawn opening is kept)."""
    data = piece.get("stair") if isinstance(piece.get("stair"), dict) else {}
    up = level_above(building, level)
    _slab, o = _opening_of(building, (up or {}).get("id"), piece)
    recut = o is None or str(o.get("source") or "derived") == "derived"
    walls = _level_walls(building, level["id"])
    out = []
    upper = upper_reading(building, piece)
    if upper is not None:
        out.append(("the upper plan's reading", upper, recut))
    if recut and data.get("flights"):
        out.append(("the same reading, its opening cut to its flights, half landing and headroom", data, True))
    can_flip = data.get("flights") and data.get("direction_assumed", True) is not False
    if can_flip:
        out.append(("the assumed rise direction flipped", flipped(data), recut))
    if landing_movable(data):
        moved = moved_landing(data, walls)
        if moved is not None:
            out.append(("the assumed half landing at the other end", moved, recut))
            if can_flip:
                out.append(("the rise direction flipped and the half landing at the other end", flipped(moved), recut))
    return out


def _describe(data: dict) -> dict:
    land = data.get("landing") if isinstance(data.get("landing"), dict) else {}
    return {"direction": data.get("direction"), "direction_assumed": data.get("direction_assumed"),
            "landing": land.get("polygon"), "landing_depth": land.get("depth"),
            "landing_assumed": data.get("landing_assumed")}


def _apply(building: dict, piece: dict, b2: dict, p2: dict, poly: Optional[list], up_id, name: str, reason: str,
           rule: str) -> tuple[dict, dict]:
    """Carry a reading out on ``building`` (in place): ``piece`` becomes ``p2`` (its drawn footprint kept), and a new
    opening ``poly`` replaces the slabs by ``b2``'s; both labelled ``adjusted_by_ai`` (by the architect, ``rule``).
    Returns ``(before, after)``."""
    before = dict(_describe(piece.get("stair") or {}), footprint=copy.deepcopy(piece.get("footprint")))
    _slab, o_before = _opening_of(building, up_id, piece)
    before["opening"] = copy.deepcopy((o_before or {}).get("polygon"))
    drawn = piece.get("drawn_footprint")
    piece.clear()
    piece.update(p2)
    if drawn is not None:
        piece["drawn_footprint"] = drawn
    piece["stair"]["access_fix"] = {"by": "architect", "rule": rule, "reading": name, "reason": reason}
    piece["adjusted_by_ai"] = {"by": "architect", "rule": rule, "reason": reason}
    if poly is not None:
        building["slabs"] = b2["slabs"]
        _s, o_after = _opening_of(building, up_id, piece)
        if o_after is not None:
            o_after["adjusted_by_ai"] = {"by": "architect", "rule": rule,
                                         "reason": f"the opening of {piece.get('id')} cut to its flights, half landing "
                                                   f"and headroom (never its arrival)"}
            if before["opening"] is not None:
                o_after.setdefault("derived_polygon_before", before["opening"])
    after = dict(_describe(piece["stair"]), footprint=copy.deepcopy(piece.get("footprint")),
                 opening=poly if poly is not None else before["opening"])
    return before, after


def flip(building: dict, piece: dict, why: str = "", rule: str = "architect flip_stair") -> tuple[bool, str]:
    """The other reading of a stair whose rise direction (and half landing's end) is assumed (pure, in place; the
    architect action ``flip_stair``): the rise direction turned round, the half landing at the other end (the flights
    climbed in the other order), both, the first that leads into both floors (``assess``); its floor opening derived
    again (flights + half landing + headroom, never the arrival; a drawn opening is kept). ``(ok, what)``; refused
    when the direction is drawn (an arrow, a break line, riser text or the plan of the level above) or no other
    reading leads into both floors."""
    pid = piece.get("id")
    data = piece.get("stair") if isinstance(piece.get("stair"), dict) else None
    if not data or not _flights(data):
        return False, f"{pid} has no drawn flights to read again"
    if data.get("direction_assumed", True) is False:
        source = data.get("direction_source") or "an arrow, a break line or riser text"
        return False, f"{pid}: its rise direction is drawn ({source}): not flipped"
    level = _level(building, piece.get("level_id"))
    up = level_above(building, level) if level is not None else None
    if up is None:
        return False, f"{pid}: no level above it, nothing to arrive on"
    _slab, o = _opening_of(building, up["id"], piece)
    recut = o is None or str(o.get("source") or "derived") == "derived"
    options = [("the rise direction flipped", flipped(data))]
    if landing_movable(data):
        moved = moved_landing(data, _level_walls(building, level["id"]))
        if moved is not None:
            options += [("the half landing at the other end", moved),
                        ("the rise direction flipped and the half landing at the other end", flipped(moved))]
    for name, cand in options:
        b2, p2, poly = _with(building, piece, cand, level, recut)
        rec2 = assess(b2, p2, level)
        if not rec2.get("ok"):
            continue
        reason = (f"{why + ': ' if why else ''}{name}: arrives on {up['id']} in {rec2['arrival']['room']}, starts on "
                  f"{level['id']} in {rec2['start']['room']}")
        _apply(building, piece, b2, p2, poly, up["id"], name, reason, rule)
        return True, f"{pid}: {reason}"
    return False, (f"{pid}: no other reading leads into both floors (tried: {'; '.join(n for n, _ in options)}): "
                   f"kept as it is")


def fix_arrivals(building: dict) -> dict:
    """The build-time check and fix of every stair (module docstring; pure, in place on ``building``: the stair
    pieces and, for a changed opening, ``building["slabs"]`` replaced by a copy). Returns ``{"stairs": [{"stair",
    "level_id", "up_level_id", "status": ok | fixed | open | not judged, "found", "change", "reason", "before",
    "after", "tried"}], "fixed", "open"}``."""
    out = {"stairs": [], "fixed": 0, "open": 0}
    levels = sorted(building.get("levels") or [], key=_elev)
    for level in levels:
        if level_above(building, level) is None:
            continue
        items = planned(building, level)
        for pid in [x["piece"].get("id") for x in items if x.get("plan")]:
            it = next((x for x in items if x["piece"].get("id") == pid), None)    # as planned after earlier fixes
            if it is None or not it.get("plan"):
                continue
            piece = it["piece"]
            rec = assess(building, piece, level, items)
            row = {"stair": piece.get("id"), "level_id": level["id"], "up_level_id": rec.get("up_level_id"),
                   "status": "ok", "change": None}
            if not rec["judged"] or rec["ok"] is None:
                row.update(status="not judged", found=rec.get("note") or "the floors cannot be measured")
                out["stairs"].append(row)
                continue
            row["walk"] = _summary(rec)
            if rec["ok"]:
                row["found"] = (f"arrives on {rec['up_level_id']} in {rec['arrival']['room']} and starts on "
                                f"{level['id']} in {rec['start']['room']}: both lead into the floor")
                out["stairs"].append(row)
                continue
            row["found"] = cut_off_text(rec)
            tried = []
            for name, data, recut in candidates(building, piece, level):
                b2, p2, poly = _with(building, piece, data, level, recut)
                rec2 = assess(b2, p2, level)
                tried.append({"reading": name, "ok": bool(rec2.get("ok")), "walk": _summary(rec2) if rec2["judged"]
                              else None})
                if not rec2.get("ok"):
                    continue
                reason = (f"{row['found']}; {name} leads into both floors (arrives on {rec2['up_level_id']} in "
                          f"{rec2['arrival']['room']}, starts on {level['id']} in {rec2['start']['room']})")
                if data.get("reason") and name.startswith("the upper plan"):
                    reason += f": {data['reason']}"
                before, after = _apply(building, piece, b2, p2, poly, rec["up_level_id"], name, reason,
                                       "architect K4")
                row.update(status="fixed", change=f"{name}: {reason}", reason=reason, before=before, after=after,
                           walk=_summary(rec2))
                out["fixed"] += 1
                break
            else:
                row.update(status="open", reason="no other reading of the stair leads into both floors: the drawing "
                                                 "is kept (needs review)")
                out["open"] += 1
            row["tried"] = tried
            out["stairs"].append(row)
            if row["status"] == "fixed":
                items = planned(building, level)      # the other stairs of the level see this one as it is now
    return out


def run_extension(building: dict, piece: dict, plan: dict, target_riser: float, max_riser: float) -> tuple[int, str]:
    """A straight stair whose risers are too high gets a longer run at its foot (27 Oct 2026, the architect's K1 for
    any stair shape): ``(treads, why)``: the most treads of its drawn going, up to those that bring its riser down to
    ``target_riser`` and at least those that bring it to ``max_riser``, whose run and the floor a visitor steps from
    (``ARRIVAL_DEPTH_M`` before it) lie on free floor of its level (``walk_graph``: no wall, opening, fixed piece or
    other stair there; and no piece of furniture standing on the floor); ``(0, why)`` when none fits or it is no
    straight stair."""
    flights = plan.get("flights") or []
    if len(flights) != 1 or plan.get("generic"):
        return 0, "not a straight stair with a drawn flight"
    f = flights[0]
    rise, total = float(plan.get("rise_m") or 0.0), int(plan.get("risers") or 0)
    n_hi = int(math.ceil(rise / target_riser - 1e-9)) - total
    n_lo = max(1, int(math.ceil(rise / max_riser - 1e-9)) - total)
    if n_hi <= 0:
        return 0, "its risers are comfortable already"
    level = _level(building, piece.get("level_id"))
    if level is None:
        return 0, "its level is unknown"
    free = walk_graph(building, level)["free"]
    if free is None:
        return 0, "its floor cannot be measured (no rooms)"
    # every piece standing on the floor counts here (the layout is done when the architect asks): a run never ends in
    # a sofa; a wall-hung piece (``mount_bottom_m``) leaves the floor free
    pieces = _union([_rect_of(p.get("footprint") or {}) for p in building.get("furniture") or []
                     if p.get("level_id") == level["id"] and p.get("type") != "stair" and p.get("build") is not False
                     and not p.get("mount_bottom_m")])
    if pieces is not None:
        free = free.difference(pieces)
    r, g, s = f["rise_dir"], float(f["going"]), f["nosings"][0]
    for n in range(n_hi, n_lo - 1, -1):
        need = _band(s, r, float(f["width"]) / 2.0, -(n * g + ARRIVAL_DEPTH_M), 0.0)
        if need is not None and need.difference(free).area <= TOUCH_M2:
            return n, (f"{n} tread(s) of {g:.2f} m added at its foot ({n * g:.2f} m longer run; the floor there and "
                       f"{ARRIVAL_DEPTH_M:.2f} m before it are free): riser {rise / (total + n):.3f} m")
    return 0, (f"the floor before its first riser is taken (a wall, a piece or an opening within "
               f"{n_lo * g + ARRIVAL_DEPTH_M:.2f} m): a run {n_lo * g:.2f} m longer does not fit")


# --------------------------------------------------------------------------
# Under the stair: closed where it is low, carried where it hangs (27 Oct 2026)
# --------------------------------------------------------------------------
# User on real06's ground floor: "This stairs not making any sense": seen from below, the flights were loose slabs
# hanging in the room, the half landing a block in the air. A stair reads as a real one when the space under it is
# closed where a visitor would hit his head (a spandrel panel under every open side of its low part, and across it
# where the clear height reaches ``HEADROOM_M``), and when every landing is carried (by those panels, by its walls, or
# by a post at each free corner when it is high enough to walk under).
SPANDREL_T_M = 0.05             # a spandrel panel: a board on studs, in the stair's structure finish
SPANDREL_MIN_M = 0.05           # an open stretch of edge shorter than this needs no panel
SPANDREL_TOP_GAP_M = 0.003      # the panel stops this far under the soffit (no coplanar faces)
WALL_TOUCH_M = 0.06             # an edge this close to a wall face is carried and closed by that wall
POST_M = 0.10                   # a landing's post, square


def _waist(plan: dict, f: dict) -> tuple[float, float]:
    """``(k, t_v)`` of a planned flight: the soffit's rise per metre of going and the waist measured vertically
    (``parametric.STAIR_WAIST_M`` square to the soffit), as ``parametric.stair_parts`` builds them."""
    from wenart.blender import parametric as P
    k = float(plan["riser_m"]) / max(float(f["going"]), 1e-6)
    return k, P.STAIR_WAIST_M * math.sqrt(1.0 + k * k)


def under_parts(plan: dict) -> list[dict]:
    """The parts of a planned stair with a space under them lower than ``HEADROOM_M`` (pure): ``[{"poly", "what",
    "under": point -> the underside's height over the floor}]``: of every flight the stretch from where its soffit
    leaves the floor (or from its foot, when it starts on a landing) to where it reaches ``HEADROOM_M``, and a half
    landing (or its winders) whose underside is under ``HEADROOM_M``."""
    out = []
    for f in plan.get("flights") or []:
        r, n = f["rise_dir"], len(f["nosings"])
        o, base, length = f["nosings"][0], float(f["base_z"]), (n - 1) * float(f["going"])
        k, tv = _waist(plan, f)
        if k <= 1e-6 or n < 2:
            continue
        s_a = max(0.0, (tv - base) / k)
        s_h = min(length, (HEADROOM_M + tv - base) / k)
        if s_h - s_a <= SPANDREL_MIN_M:
            continue
        poly = _band(o, r, float(f["width"]) / 2.0, s_a, s_h)

        def under(p, o=o, r=r, k=k, tv=tv, base=base):
            return base + _dot((p[0] - o[0], p[1] - o[1]), r) * k - tv
        out.append({"poly": poly, "what": f"flight {f['index'] + 1}", "under": under})
    land = plan.get("landing")
    if isinstance(land, dict) and land.get("role") in ("mid", "winders"):
        z_u = float(land["z"]) - float(land.get("thickness") or 0.0)
        poly = _poly(land.get("polygon") or [])
        if poly is not None and 0.0 < z_u < HEADROOM_M:
            out.append({"poly": poly, "what": "the landing", "under": lambda p, z_u=z_u: z_u})
    return out


def _lines(geom) -> list:
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "LineString" and not g.is_empty]


def under_stair(plan: dict, walls=()) -> dict:
    """How the space under a planned stair is closed and its landing carried (pure; module docstring of this
    section): ``{"panels": [{"p", "q", "zp", "zq", "inward", "of"}], "posts": [{"at", "z"}], "low_m2", "reason"}``.
    A panel stands on every stretch of the boundary of ``under_parts`` that no other part and no wall (within
    ``WALL_TOUCH_M``) closes, from the floor to the underside over it; a half landing high enough to walk under gets a
    post at every corner no wall and no flight carries."""
    from shapely.geometry import LineString, Point
    parts = under_parts(plan)
    wall_polys = [p for p in (_wall_poly(w) for w in walls or ()) if p is not None]
    wall_zone = _union([p.buffer(WALL_TOUCH_M) for p in wall_polys])
    panels = []
    for i, part in enumerate(parts):
        others = _union([q["poly"].buffer(0.002) for j, q in enumerate(parts) if j != i])
        ring = _ring(part["poly"])
        for j in range(len(ring)):
            a, b = tuple(ring[j]), tuple(ring[(j + 1) % len(ring)])
            if G.distance(a, b) < SPANDREL_MIN_M:
                continue
            rest = LineString([a, b])
            for cut in (others, wall_zone):
                if cut is not None:
                    rest = rest.difference(cut)
            u = _unit((b[0] - a[0], b[1] - a[1]))
            inward = (-u[1], u[0])                       # left of a counter-clockwise edge
            for seg in _lines(rest):
                c = list(seg.coords)
                p, q = (c[0], c[-1]) if _dot((c[-1][0] - c[0][0], c[-1][1] - c[0][1]), u) >= 0 else (c[-1], c[0])
                if G.distance(p, q) < SPANDREL_MIN_M:
                    continue
                zp, zq = part["under"](p), part["under"](q)
                if max(zp, zq) <= 0.02:
                    continue                             # the stair's body stands on the floor there
                panels.append({"p": [round(p[0], 4), round(p[1], 4)], "q": [round(q[0], 4), round(q[1], 4)],
                               "zp": round(max(0.0, zp), 4), "zq": round(max(0.0, zq), 4),
                               "inward": [round(inward[0], 6), round(inward[1], 6)], "of": part["what"]})
    posts = []
    land = plan.get("landing")
    if isinstance(land, dict) and land.get("role") in ("mid", "winders"):
        z_u = float(land["z"]) - float(land.get("thickness") or 0.0)
        flights = _union([_band(f["nosings"][0], f["rise_dir"], float(f["width"]) / 2.0, 0.0,
                                max(G.distance(f["nosings"][0], f["nosings"][-1]), 0.01)).buffer(0.01)
                          for f in plan.get("flights") or []])
        poly = _poly(land.get("polygon") or [])
        if z_u >= HEADROOM_M and poly is not None:
            cx, cy = poly.centroid.x, poly.centroid.y
            for c in _ring(poly):
                pt = Point(c)
                if (wall_zone is not None and wall_zone.contains(pt)) or (flights is not None and flights.contains(pt)):
                    continue
                d = _unit((cx - c[0], cy - c[1])) or (0.0, 0.0)
                at = (c[0] + d[0] * POST_M * 0.71, c[1] + d[1] * POST_M * 0.71)     # under the landing's corner
                posts.append({"at": [round(at[0], 4), round(at[1], 4)], "z": round(z_u, 4)})
    low = _union([p["poly"] for p in parts])
    reason = (f"the space under the stair lower than {HEADROOM_M:.2f} m is closed by {len(panels)} spandrel panel(s) "
              f"in its structure finish where no wall closes it"
              + (f"; its landing ({HEADROOM_M:.2f} m or more over the floor) stands on {len(posts)} post(s)"
                 if posts else "") + " (not drawn: assumed, so the stair reads as built from below and the side)")
    return {"panels": panels, "posts": posts, "low_m2": round(low.area, 3) if low is not None else 0.0,
            "reason": reason}


def cut_off_text(rec: dict) -> str:
    """What is wrong with a stair's walk (``assess``), in words."""
    pid = rec.get("stair")
    bits = []
    ends = rec.get("ends") or {}
    for key, lid, verb in (("arrival", rec.get("up_level_id"), "arrives on"), ("start", rec.get("level_id"),
                                                                                "starts on")):
        r = rec.get(key) or {}
        if r.get("ok") is not False:
            continue
        at = ends.get(f"{key}_at")
        where = f" at ({at[0]:.2f}, {at[1]:.2f})" if at else ""
        missed = ", ".join((r.get("missed") or [])[:8]) or "the main floor"
        if r.get("floor_m2", 0.0) < STEP_OFF_M2:
            bits.append(f"{verb} {lid}{where} with only {r.get('floor_m2', 0.0):.2f} m2 of floor "
                        f"{'past its last' if key == 'arrival' else 'before its first'} riser (a floor opening or a "
                        f"wall is there)")
        elif r.get("pocket"):
            bits.append(f"{verb} {lid}{where} on {r.get('floor_m2', 0.0):.2f} m2 of floor that no {WALK_CLEAR_M:.2f} m "
                        f"way joins to any room of {lid} (cut off from {missed})")
        else:
            bits.append(f"{verb} {lid}{where} into {', '.join(r.get('rooms') or [])} only, not the main floor of "
                        f"{lid} (no {WALK_CLEAR_M:.2f} m way to {missed})")
    return f"stair {pid} " + "; ".join(bits) if bits else f"stair {pid} leads into both floors"


# --------------------------------------------------------------------------
# The model review's M9 and the rooms a stair joins
# --------------------------------------------------------------------------

def _blockers(graph: dict, approach) -> tuple[str, list]:
    """What stands on a door's approach: ``("opening" | "pieces" | "narrow", ids)``."""
    holes = [str(i) for i, h in graph.get("holes") or [] if approach is not None and h.intersection(approach).area
             >= TOUCH_M2]
    if holes:
        return "opening", holes
    pieces = [str(i) for i, p in graph.get("obstacles") or [] if approach is not None
              and p.intersection(approach).area >= TOUCH_M2]
    if pieces:
        return "pieces", pieces
    return "narrow", []


def walk_review(building: dict) -> dict:
    """M9 on the built floors (module docstring): ``{"stairs": [assess records], "doors": [{"door", "room",
    "level_id", "kind", "blocked_by", "part"}], "parts": [{"level_id", "area_m2", "bounds", "openings", "rooms",
    "doors"}], "checked": n}``."""
    out = {"stairs": [], "doors": [], "parts": [], "checked": 0}
    levels = sorted(building.get("levels") or [], key=_elev)
    ends_on: dict = {}
    plans: dict = {}
    for level in levels:
        items = planned(building, level)
        plans[level["id"]] = items
        if level_above(building, level) is None:
            continue
        for it in items:
            if not it.get("plan"):
                continue
            rec = assess(building, it["piece"], level, items)
            if not rec["judged"]:
                continue
            out["stairs"].append(rec)
            out["checked"] += 1
            ends_on.setdefault(rec["up_level_id"], []).append(rec["ends"]["arrival"])
            ends_on.setdefault(level["id"], []).append(rec["ends"]["start"])
    for level in levels:
        below = level_below(building, level)
        g = walk_graph(building, level, items=plans.get(level["id"]),
                       tops=_tops(plans.get(below["id"]) or []) if below is not None else [])
        if g["free"] is None:
            continue
        for d in g["doors"]:
            for k, rid in enumerate(d["rooms"]):
                if rid is None or rid not in g["room_main"]:
                    continue
                out["checked"] += 1
                home = g["group"][g["room_main"][rid]]
                touch = d["touch"][k]
                if any(g["group"][i] == home for i in touch):
                    continue
                kind, ids = _blockers(g, d["approach"][k]) if not touch else ("part", [])
                out["doors"].append({"door": d["id"], "type": d["type"], "room": rid, "level_id": level["id"],
                                     "kind": kind, "blocked_by": ids})
        if not g["holes"] or g["main"] is None:
            continue
        for grp in sorted(set(g["group"]) - (g.get("mains") or {g["main"]})):
            idx = [i for i, x in enumerate(g["group"]) if x == grp]
            geom = _union([g["opened"][i] for i in idx])
            if geom is None or geom.area < PART_MIN_M2:
                continue
            out["checked"] += 1
            near = [str(i) for i, h in g["holes"] if geom.distance(h) <= WALK_CLEAR_M / 2.0 + 0.1]
            if not near:
                continue
            if any(e is not None and e.intersection(geom).area >= TOUCH_M2 for e in ends_on.get(level["id"]) or []):
                continue                               # a stair's own end: its check reports it
            rooms = sorted(rid for rid, p in g["rooms"].items() if p.intersection(geom).area >= TOUCH_M2)
            doors = sorted(str(d["id"]) for d in g["doors"] if any(g["group"][i] == grp for s in d["touch"]
                                                                       for i in s))
            out["parts"].append({"level_id": level["id"], "area_m2": round(geom.area, 2), "bounds": _bounds(geom),
                                 "openings": near, "rooms": rooms, "doors": doors})
    return out


def is_upper_end(building: dict, piece: dict) -> bool:
    """The piece is the drawn upper end of a stair of the level below (``shell.stair_arrival``)."""
    from wenart.blender import shell
    level = _level(building, piece.get("level_id"))
    if level is None:
        return False
    try:
        return shell.stair_arrival(building, level, piece) is not None
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def stair_rooms(building: dict, piece: dict) -> Optional[dict]:
    """``{"start": room id, "arrival": room id, "level_id", "up_level_id"}``: the room most of a stair's start area
    lies in on its level, and the room most of its arrival floor (outside the floor's openings) lies in on the level
    above; None when the stair cannot be planned or has no level above."""
    level = _level(building, piece.get("level_id"))
    up = level_above(building, level) if level is not None else None
    if up is None:
        return None
    items = planned(building, level)
    it = next((x for x in items if x["piece"].get("id") == piece.get("id")), None)
    if it is None or not it.get("plan") or not it["plan"].get("flights"):
        return None
    ends = stair_ends(it["plan"])
    holes = _union([p for _, p in floor_voids(building, up["id"])])
    arrival = ends["arrival"].difference(holes) if holes is not None and ends["arrival"] is not None \
        else ends["arrival"]

    def room_of(level_id, area):
        best = (0.0, None)
        for r in building.get("rooms") or []:
            if r.get("level_id") != level_id or len(r.get("polygon") or []) < 3 or area is None:
                continue
            p = _poly(r["polygon"])
            a = p.intersection(area).area if p is not None else 0.0
            if a > best[0] + 1e-9:
                best = (a, r["id"])
        return best[1]

    return {"start": room_of(level["id"], ends["start"]), "arrival": room_of(up["id"], arrival),
            "level_id": level["id"], "up_level_id": up["id"]}
