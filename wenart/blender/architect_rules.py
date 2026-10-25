"""The architect's questions about every element (user note of 25 Oct 2026: "don't restrict this to only 16
questions: depending on the job there might be 1000s of questions").

What: each rule of ``RULES`` is a question an architect asks of every element of one kind (every room, window, door,
wall, stair, level, furniture piece, tree); ``review(building, prep, plan, sides, graph)`` asks them all and returns
one question record per rule (``wenart/blender/architect.py`` shape) with one answer per element: ``ok`` (the
check passed, it is counted and not listed), a ``change`` (code fixed it), or ``open`` with the ``ask`` for the user
and the ``options`` an answer may pick (``architect_actions.ACTIONS``). A big building gets thousands of questions;
the report counts them by rule and lists only what changed or stays open.

How: every check is code on the building JSON and the build plan (never a guess); thresholds are the usual design
rules (a door at least 0.70 m, 0.80 m to the outside; a habitable ceiling at least 2.40 m; a sill at least 0.85 m
over a drop; 0.5 m free in front of a bed, a sofa or a wardrobe), named in ``LIMITS``. A rule whose fix code can
make safely makes it (none here: these are drawing questions); the others ask, with options.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G
from wenart.blender import architect_actions as AA

LIMITS = {
    "ceiling_habitable_m": 2.40, "ceiling_other_m": 2.10,
    "door_min_m": 0.70, "door_wet_min_m": 0.60, "door_outside_min_m": 0.80,
    "sill_safe_m": 0.85, "sill_drop_m": 1.0,
    "outer_wall_min_m": 0.15, "outer_wall_len_m": 1.0,
    "fit_tol_m": 0.03, "overlap_tol_m": 0.05,
    "piece_inside": 0.80,
    "front_clear_m": 0.50, "front_free": 0.60,
    "swing_depth_m": 0.80, "swing_cover": 0.25,
    "window_reach_m": 0.50, "window_cover": 0.50,
}
ROOM_MIN_M2 = {"bedroom": 6.5, "living": 10.0, "dining": 6.0, "kitchen": 4.0, "bathroom": 2.0, "wc": 1.0,
               "office": 5.0, "study": 5.0}
HABITABLE = ("bedroom", "living", "kitchen", "dining", "office", "study", "other")
WET = ("bathroom", "wc", "toilet", "shower")
UNKNOWN_TYPES = ("", "other", "unknown", "none")
ACCESS_TYPES = ("bed", "bed_double", "bed_single", "bed_bunk", "sofa", "sofa_corner", "wardrobe", "toilet", "sink",
                "washbasin", "kitchen_counter", "desk", "dresser", "bathtub", "shower", "fridge", "oven", "dishwasher",
                "washing_machine", "bookcase", "tv_unit", "sideboard")
COMPANIONS = ("chair", "dining_chair", "office_chair", "stool", "bar_stool", "coffee_table", "side_table",
              "nightstand", "rug", "ottoman", "bench", "plant", "floor_lamp", "lamp", "pouf", "armchair", "cushion",
              "towel", "bath_mat", "laundry_basket", "dining_table", "table")
FLOOR_ONLY = ("rug", "bath_mat", "carpet", "mat")

RULES = (
    {"id": "R3", "topic": "ceiling height", "scope": "room", "severity": "minor",
     "question": "Is every room high enough: 2.40 m for a habitable room, 2.10 m for the others?",
     "why": "a low ceiling feels oppressive and breaks most building codes"},
    {"id": "R4", "topic": "room area", "scope": "room", "severity": "minor",
     "question": "Is every room big enough for what it is (a bedroom 6.5 m2, a living room 10 m2, a kitchen 4 m2, a "
                 "bathroom 2 m2)?",
     "why": "a room smaller than any room of its type is usually a misread type or size"},
    {"id": "R5", "topic": "room type", "scope": "room", "severity": "minor",
     "question": "Do I know what every room is for?",
     "why": "an untyped room cannot be furnished or lit for its use"},
    {"id": "W2", "topic": "windows to the outside", "scope": "window", "severity": "major",
     "question": "Does every window look outside (or onto a terrace)?",
     "why": "a window between two rooms is usually a reading error: the dark room needs it on its outer wall"},
    {"id": "W3", "topic": "low sills", "scope": "window", "severity": "major",
     "question": "Where a window lies more than a metre over the ground, is its sill at least 0.85 m high?",
     "why": "a low sill over a drop is a fall risk (or the window needs a guard)"},
    {"id": "O1", "topic": "openings in their walls", "scope": "opening", "severity": "major",
     "question": "Does every door and window fit in its wall: within its length, clear of the other openings, under "
                 "the ceiling?",
     "why": "an opening past the wall's end or over another one is a drawing or reading error"},
    {"id": "D1", "topic": "door widths", "scope": "door", "severity": "minor",
     "question": "Is every door wide enough: 0.70 m inside (0.60 m to a WC), 0.80 m to the outside?",
     "why": "a narrow door cannot take furniture or a wheelchair; often a misread width"},
    {"id": "D2", "topic": "doors lead somewhere", "scope": "door", "severity": "major",
     "question": "Does every door join two rooms, or a room and the outside?",
     "why": "a door with the same room or nothing on both sides is on the wrong wall"},
    {"id": "X1", "topic": "outer walls", "scope": "wall", "severity": "minor",
     "question": "Is every outer wall thick enough for a facade (0.15 m or more)?",
     "why": "a thin outer wall is usually a partition read as the facade, or a glass wall"},
    {"id": "T1", "topic": "stairs", "scope": "stair", "severity": "major",
     "question": "Does every stair lead to another floor?",
     "why": "a stair that ends nowhere is a reading error of the level or the stair room"},
    {"id": "T2", "topic": "every floor reached", "scope": "level", "severity": "major",
     "question": "Can I reach every floor from the entrance?",
     "why": "a floor without a stair or a door from outside cannot be used"},
    {"id": "F1", "topic": "pieces in their rooms", "scope": "furniture", "severity": "minor",
     "question": "Does every piece of furniture stand inside its room?",
     "why": "a piece through a wall is a placement error"},
    {"id": "F2", "topic": "free doorways", "scope": "door", "severity": "minor",
     "question": "Can every door open and be walked through without furniture in the way?",
     "why": "a wardrobe in front of a door is the first thing a visitor bumps into"},
    {"id": "F3", "topic": "free windows", "scope": "window", "severity": "minor",
     "question": "Is every window free of tall furniture standing in front of it?",
     "why": "a wardrobe against a window blocks the light and looks wrong from outside"},
    {"id": "F4", "topic": "room to use", "scope": "furniture", "severity": "minor",
     "question": "Is there room in front of every bed, sofa, wardrobe, WC and counter to use it (0.5 m)?",
     "why": "a piece you cannot reach or open is not usable"},
    {"id": "G1", "topic": "trees", "scope": "tree", "severity": "minor",
     "question": "Does every tree and shrub stand on open ground, clear of the house, the pools, the paths and the "
                 "terraces?",
     "why": "a tree through a terrace or in front of a door is a reading or placement error"},
)


def _q(rule: dict) -> dict:
    return dict(rule, answers=[], status="ok")


def _open(q: dict, element: str, found: str, ask: str, options: list, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": None, "open": True, "ask": ask,
                              "options": options}, **extra))
    q["status"] = "open"


def _ok(q: dict, element: str, found: str, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": None}, **extra))


def _rtype(room: Optional[dict]) -> str:
    return str((room or {}).get("room_type") or "").lower()


def _where(kind: str, level_id, centre) -> dict:
    return {"kind": kind, "level_id": level_id, "centre": [round(float(centre[0]), 3), round(float(centre[1]), 3)]}


def _centroid(poly) -> tuple[float, float]:
    return sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)


# --------------------------------------------------------------------------
# Rooms
# --------------------------------------------------------------------------

def rooms_rules(plan: AA.Plan) -> list[dict]:
    r3, r4, r5 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("R3", "R4", "R5"))
    for r in plan.rooms:
        t = _rtype(r)
        if t in AA.OPEN_AIR:
            continue
        where = _where("room", r.get("level_id"), _centroid(r["polygon"]))
        ceiling = plan.ceiling(r.get("level_id"))
        need = LIMITS["ceiling_habitable_m"] if t in HABITABLE else LIMITS["ceiling_other_m"]
        if ceiling + 1e-6 < need:
            _open(r3, r["id"], f"{r['id']} ({t}) has a {ceiling:.2f} m ceiling (level {r.get('level_id')})",
                  f"Is the ceiling of level {r.get('level_id')} really {ceiling:.2f} m?", [AA.option("keep")],
                  where=where)
        else:
            _ok(r3, r["id"], f"{ceiling:.2f} m ceiling")
        area = AA.room_area(r)
        low = ROOM_MIN_M2.get(t)
        if low is not None and area + 1e-6 < low:
            smaller = [k for k, v in sorted(ROOM_MIN_M2.items(), key=lambda kv: -kv[1]) if v <= area and k != t]
            opts = [AA.option("retype_room", f"it is a {k}", room_type=k) for k in smaller[:2]]
            opts += [AA.option("retype_room", "it is a storage room", room_type="storage"), AA.option("keep")]
            _open(r4, r["id"], f"{r['id']} is a {t} of {area:.1f} m2 (a {t} has at least {low:g} m2)",
                  f"Is {r['id']} really a {t}?", opts, where=where)
        elif low is not None:
            _ok(r4, r["id"], f"{t} of {area:.1f} m2")
        if t in UNKNOWN_TYPES and not (r.get("label") or r.get("name")):
            opts = [AA.option("retype_room", f"it is a {k}", room_type=k)
                    for k in ("bedroom", "living", "office", "storage")] + [AA.option("keep")]
            _open(r5, r["id"], f"{r['id']} ({area:.1f} m2) has no type and no name in the drawing",
                  f"What is {r['id']} used for?", opts, where=where)
        else:
            _ok(r5, r["id"], f"{t}" + (f" ({r.get('label') or r.get('name')})" if t in UNKNOWN_TYPES else ""))
    return [r3, r4, r5]


# --------------------------------------------------------------------------
# Openings
# --------------------------------------------------------------------------

def _ground_z(building: dict) -> float:
    """The ground's height next to the house (the entrance level's floor; else the lowest level)."""
    levels = building.get("levels") or []
    ents = [e for e in (building.get("site") or {}).get("entrances") or [] if isinstance(e, dict)]
    lid = next((e.get("level_id") for e in ents if e.get("main")), ents[0].get("level_id") if ents else None)
    lv = next((x for x in levels if x["id"] == lid), None)
    if lv is not None:
        return float(lv["elevation"])
    return min((float(x["elevation"]) for x in levels), default=0.0)


def openings_rules(plan: AA.Plan, sides: list[dict]) -> list[dict]:
    w2, w3, o1, d1, d2 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("W2", "W3", "O1", "D1", "D2"))
    side_of = {s["opening"]["id"]: s for s in sides}
    ground = _ground_z(plan.b)
    glass = {}
    for o in plan.openings.values():
        w = plan.walls.get(o.get("wall_id"))
        if w is None or o.get("level_id") not in plan.levels:
            continue
        s = side_of.get(o["id"])
        a = plan.room.get((s or {}).get("a"))
        b = plan.room.get((s or {}).get("b"))
        out_a, out_b = AA.Plan.is_outside(a), AA.Plan.is_outside(b)
        where = _where(o.get("type"), o.get("level_id"), o["center"])
        # O1: the opening in its wall
        t = plan.t_of(w, o["center"])
        _a0, _u, length = plan.axis(w)
        half = float(o.get("width") or 0.0) / 2.0
        problems = []
        if t - half < -LIMITS["fit_tol_m"] or t + half > length + LIMITS["fit_tol_m"]:
            problems.append(f"runs past the end of {w['id']} ({length:.2f} m long)")
        for p in plan.openings.values():
            if p["id"] == o["id"] or p.get("wall_id") != o.get("wall_id"):
                continue
            tp, hp = plan.t_of(w, p["center"]), float(p.get("width") or 0.0) / 2.0
            if min(t + half, tp + hp) - max(t - half, tp - hp) > LIMITS["overlap_tol_m"]:
                problems.append(f"overlaps {p['id']}")
        ceiling = plan.ceiling(o.get("level_id"))
        sill = float(o.get("sill_height") if o.get("sill_height") is not None else (0.0 if o.get("type") == "door"
                                                                                    else 0.9))
        head = sill + float(o.get("height") if o.get("height") is not None else (2.1 if o.get("type") == "door"
                                                                                 else 1.2))
        if head > ceiling + 0.02 and not plan.b.get("roof"):
            problems.append(f"its head ({head:.2f} m) is over the {ceiling:.2f} m ceiling")
        if problems:
            _open(o1, o["id"], f"{o['id']} " + "; ".join(problems), f"Is {o['id']} drawn on the right wall and "
                  f"at the right size?", [AA.option("keep")], where=where)
        else:
            _ok(o1, o["id"], f"fits {w['id']}")
        if o.get("type") == "window":
            # W2: to the outside
            if out_a or out_b:
                _ok(w2, o["id"], "to the outside" if a is None or b is None else "onto an open-air room")
            elif a is not None and b is not None:
                dark = [x for x in (a, b) if _rtype(x) in HABITABLE]
                room = min(dark or [a, b], key=lambda x: glass.setdefault(
                    x["id"], AA.outside_glass(plan, x["id"])[0]))
                other = b if room is a else a
                _open(w2, o["id"], f"{o['id']} sits in the wall between {room['id']} ({_rtype(room)}) and "
                      f"{other['id']} ({_rtype(other)})",
                      f"Is {o['id']} on the outer wall of {room['id']} in the drawing (a reading error), or a "
                      f"borrowed-light window on purpose?",
                      [AA.option("move_window_to_outer_wall", f"a reading error: move it to the outer wall of "
                                 f"{room['id']}", room_id=room["id"]),
                       AA.option("keep", "a borrowed-light window on purpose")], where=where, room=room["id"])
            # W3: low sills over a drop
            lv = plan.levels[o["level_id"]]
            drop = float(lv["elevation"]) - ground
            if (a is None or b is None) and not (out_a and out_b) and drop >= LIMITS["sill_drop_m"]:
                if sill + 1e-6 < LIMITS["sill_safe_m"]:
                    _open(w3, o["id"], f"{o['id']} on level {o['level_id']} ({drop:.1f} m over the ground) has its "
                          f"sill at {sill:.2f} m", f"Does {o['id']} need a higher sill (or is it a French window "
                          f"with a guard)?", [AA.option("raise_sill"), AA.option("keep", "keep: a guard is fitted")],
                          where=where)
                else:
                    _ok(w3, o["id"], f"sill {sill:.2f} m")
        elif o.get("type") == "door":
            width = float(o.get("width") or 0.0)
            to_out = (a is None) != (b is None) or (out_a != out_b)
            wet = _rtype(a) in WET or _rtype(b) in WET
            need = LIMITS["door_outside_min_m"] if to_out else (LIMITS["door_wet_min_m"] if wet else
                                                                LIMITS["door_min_m"])
            if width + 1e-6 < need:
                room = (a if a is not None and not out_a else b) or {}
                _open(d1, o["id"], f"{o['id']} ({'to the outside' if to_out else 'inside'}) is {width:.2f} m wide",
                      f"Is {o['id']} really {width:.2f} m wide?",
                      [AA.option("widen_door", room_id=room.get("id")), AA.option("keep")], where=where)
            else:
                _ok(d1, o["id"], f"{width:.2f} m")
            if (a is None and b is None) or (a is not None and b is not None and a["id"] == b["id"]):
                what = "the same room" if a is not None else "no room"
                _open(d2, o["id"], f"{o['id']} has {what} on both sides", f"Is {o['id']} on the right wall?",
                      [AA.option("keep")], where=where)
            else:
                _ok(d2, o["id"], f"{(a or {}).get('id') or 'outside'} - {(b or {}).get('id') or 'outside'}")
    return [w2, w3, o1, d1, d2]


# --------------------------------------------------------------------------
# Walls, stairs, levels
# --------------------------------------------------------------------------

def outer_length(plan: AA.Plan, wall: dict) -> float:
    """How much of ``wall`` has a room on one side and the outside on the other (sampled)."""
    a, u, length = plan.axis(wall)
    n = (-u[1], u[0])
    reach = float(wall.get("thickness") or 0.2) / 2.0 + AA.PROBE_M
    lid = wall.get("level_id")
    step = max(0.25, length / 40.0)
    k, hits = 0, 0
    t = step / 2.0
    while t < length:
        p = (a[0] + u[0] * t, a[1] + u[1] * t)
        left = plan.room_at((p[0] + n[0] * reach, p[1] + n[1] * reach), lid)
        right = plan.room_at((p[0] - n[0] * reach, p[1] - n[1] * reach), lid)
        inside = [x for x in (left, right) if x is not None and not AA.Plan.is_outside(x)]
        if len(inside) == 1:
            hits += 1
        k += 1
        t += step
    return length * hits / k if k else 0.0


def walls_rules(plan: AA.Plan) -> list[dict]:
    x1 = _q(next(r for r in RULES if r["id"] == "X1"))
    for w in plan.walls.values():
        if w.get("level_id") not in plan.levels:
            continue
        outer = outer_length(plan, w)
        if outer < LIMITS["outer_wall_len_m"]:
            continue
        t = float(w.get("thickness") or 0.0)
        if t + 1e-6 < LIMITS["outer_wall_min_m"]:
            mid = plan.at_t(w, plan.axis(w)[2] / 2.0)
            _open(x1, w["id"], f"{w['id']} is an outer wall ({outer:.1f} m along the outside) only {t:.2f} m thick",
                  f"Is {w['id']} a glass wall or a partition read as the facade, or really {t:.2f} m thick?",
                  [AA.option("keep")], where=_where("wall", w.get("level_id"), mid))
        else:
            _ok(x1, w["id"], f"{t:.2f} m outer wall")
    return [x1]


def stairs_rules(plan: AA.Plan, graph: dict, starts: list, is_stair, reach) -> list[dict]:
    t1, t2 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("T1", "T2"))
    for r in plan.rooms:
        if not is_stair(r):
            continue
        if "stairs" in {x for ops in graph.get(r["id"], {}).values() for x in ops}:
            _ok(t1, r["id"], "joins " + ", ".join(sorted(nb for nb, ops in graph[r["id"]].items() if "stairs" in ops)))
        else:
            _open(t1, r["id"], f"the stair {r['id']} overlaps no room of the level above or below",
                  f"Where does the stair {r['id']} lead?", [AA.option("keep")],
                  where=_where("room", r.get("level_id"), _centroid(r["polygon"])))
    seen = reach(graph, starts) if starts else set()
    for lid in plan.levels:
        rooms = [r for r in plan.rooms if r.get("level_id") == lid and not AA.Plan.is_outside(r)]
        if not rooms:
            continue
        if any(r["id"] in seen for r in rooms):
            _ok(t2, lid, f"{sum(1 for r in rooms if r['id'] in seen)} of {len(rooms)} rooms reached")
        elif starts:
            _open(t2, lid, f"no room of level {lid} can be reached from the entrance",
                  f"How do people get to level {lid} (a stair or a door missing in the drawing)?", [AA.option("keep")])
    return [t1, t2]


# --------------------------------------------------------------------------
# Furniture
# --------------------------------------------------------------------------

def piece_rect(f: dict) -> Optional[list[tuple[float, float]]]:
    fp = f.get("footprint") or {}
    c, size = fp.get("center"), fp.get("size")
    if not c or not size:
        return None
    a = math.radians(float(fp.get("rotation_deg") or 0.0))
    ca, sa = math.cos(a), math.sin(a)
    hw, hd = float(size[0]) / 2.0, float(size[1]) / 2.0
    return [(c[0] + ca * x - sa * y, c[1] + sa * x + ca * y) for x, y in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]


def _grid(poly, n: int = 5):
    """``n`` x ``n`` points spread over a convex quadrilateral (bilinear)."""
    p0, p1, p2, p3 = poly
    out = []
    for i in range(n):
        s = (i + 0.5) / n
        for j in range(n):
            t = (j + 0.5) / n
            out.append(((1 - s) * (1 - t) * p0[0] + s * (1 - t) * p1[0] + s * t * p2[0] + (1 - s) * t * p3[0],
                        (1 - s) * (1 - t) * p0[1] + s * (1 - t) * p1[1] + s * t * p2[1] + (1 - s) * t * p3[1]))
    return out


def _height(f: dict) -> float:
    h = f.get("height")
    if h is None:
        h = ((f.get("asset") or {}).get("bbox_m") or [0, 0, 0.8])[2]
    return float(h or 0.8)


def _box(origin, u, n, along: float, depth: float):
    """A rectangle ``along`` wide (centred on ``origin`` along ``u``) and ``depth`` deep along ``n``."""
    ox, oy = origin
    h = along / 2.0
    return [(ox - u[0] * h, oy - u[1] * h), (ox + u[0] * h, oy + u[1] * h),
            (ox + u[0] * h + n[0] * depth, oy + u[1] * h + n[1] * depth),
            (ox - u[0] * h + n[0] * depth, oy - u[1] * h + n[1] * depth)]


def _covered(points, rects) -> float:
    if not points:
        return 0.0
    return sum(1 for p in points if any(G.point_in_polygon(p, r) for r in rects)) / len(points)


def furniture_rules(plan: AA.Plan, sides: list[dict]) -> list[dict]:
    f1, f2, f3, f4 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("F1", "F2", "F3", "F4"))
    pieces = []
    for f in plan.b.get("furniture") or []:
        if f.get("build") is False:
            continue
        rect = piece_rect(f)
        if rect is not None:
            pieces.append((f, rect, str(f.get("type") or "").lower()))
    by_room: dict = {}
    for f, rect, t in pieces:
        by_room.setdefault(f.get("room_id"), []).append((f, rect, t))
    for f, rect, t in pieces:
        room = plan.room.get(f.get("room_id"))
        where = _where("furniture", f.get("level_id"), (f.get("footprint") or {}).get("center") or (0, 0))
        if room is None:
            continue
        pts = _grid(rect)
        inside = sum(1 for p in pts if G.point_in_polygon(p, room["polygon"])) / len(pts)
        if inside + 1e-6 < LIMITS["piece_inside"]:
            _open(f1, f["id"], f"{f['id']} ({t}) stands {100 * (1 - inside):.0f}% outside {room['id']}",
                  f"Is {f['id']} in the right place?", [AA.option("keep")], where=where)
        else:
            _ok(f1, f["id"], f"{t} in {room['id']}")
        if t in ACCESS_TYPES and f.get("front_deg") is not None:
            a = math.radians(float(f["front_deg"]))
            n = (math.cos(a), math.sin(a))
            u = (-n[1], n[0])
            fp = f["footprint"]
            rot = math.radians(float(fp.get("rotation_deg") or 0.0))
            ext_u = abs(math.cos(rot) * u[0] + math.sin(rot) * u[1]) * float(fp["size"][0]) + \
                abs(-math.sin(rot) * u[0] + math.cos(rot) * u[1]) * float(fp["size"][1])
            ext_n = abs(math.cos(rot) * n[0] + math.sin(rot) * n[1]) * float(fp["size"][0]) + \
                abs(-math.sin(rot) * n[0] + math.cos(rot) * n[1]) * float(fp["size"][1])
            c = fp["center"]
            front = (c[0] + n[0] * ext_n / 2.0, c[1] + n[1] * ext_n / 2.0)
            strip = _box(front, u, n, ext_u * 0.8, LIMITS["front_clear_m"])
            spts = _grid(strip)
            others = [r for g, r, gt in by_room.get(f.get("room_id"), []) if g is not f and gt not in COMPANIONS
                      and gt not in FLOOR_ONLY and not str(g.get("id")).startswith(str(f["id"]) + "_")]
            free = sum(1 for p in spts if G.point_in_polygon(p, room["polygon"])
                       and not any(G.point_in_polygon(p, r) for r in others)) / len(spts)
            if free + 1e-6 < LIMITS["front_free"]:
                block = [g["id"] for g, r, gt in by_room.get(f.get("room_id"), []) if g is not f and gt not in
                         COMPANIONS and gt not in FLOOR_ONLY and any(G.point_in_polygon(p, r) for p in spts)]
                _open(f4, f["id"], f"only {100 * free:.0f}% of the 0.5 m in front of {f['id']} ({t}) is free"
                      + (f" ({', '.join(block[:3])} in the way)" if block else " (the wall is close)"),
                      f"Can {f['id']} be used where it stands?", [AA.option("keep")], where=where)
            else:
                _ok(f4, f["id"], f"{100 * free:.0f}% free in front")
    for s in sides:
        o = s["opening"]
        w = plan.walls.get(o.get("wall_id"))
        if w is None or s["type"] not in ("door", "window"):
            continue
        _a, u, _l = plan.axis(w)
        n = (-u[1], u[0])
        c = (plan.at_t(w, plan.t_of(w, o["center"])))
        half_t = float(w.get("thickness") or 0.2) / 2.0
        width = float(o.get("width") or 0.0)
        where = _where(s["type"], o.get("level_id"), o["center"])
        if s["type"] == "door":
            worst = (0.0, None, [])
            for sign, rid in ((1.0, s["a"]), (-1.0, s["b"])):
                if not rid or rid not in by_room:
                    continue
                nn = (n[0] * sign, n[1] * sign)
                box = _box((c[0] + nn[0] * half_t, c[1] + nn[1] * half_t), u, nn, width, LIMITS["swing_depth_m"])
                rects = [(g, r) for g, r, gt in by_room[rid] if gt not in FLOOR_ONLY]
                pts = _grid(box)
                cov = _covered(pts, [r for _g, r in rects])
                if cov > worst[0]:
                    worst = (cov, rid, [g["id"] for g, r in rects if any(G.point_in_polygon(p, r) for p in pts)])
            if worst[0] > LIMITS["swing_cover"]:
                _open(f2, o["id"], f"{100 * worst[0]:.0f}% of the doorway of {o['id']} in {worst[1]} is taken by "
                      f"{', '.join(worst[2][:3])}", f"Should {', '.join(worst[2][:2])} move away from {o['id']}?",
                      [AA.option("keep")], where=where)
            else:
                _ok(f2, o["id"], "doorway free")
        else:
            sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
            worst = (0.0, [])
            for sign, rid in ((1.0, s["a"]), (-1.0, s["b"])):
                if not rid or rid not in by_room:
                    continue
                nn = (n[0] * sign, n[1] * sign)
                box = _box((c[0] + nn[0] * half_t, c[1] + nn[1] * half_t), u, nn, width, LIMITS["window_reach_m"])
                tall = [(g, r) for g, r, gt in by_room[rid] if _height(g) > sill + 0.1 and gt not in FLOOR_ONLY
                        and gt not in ("curtain", "plant", "floor_lamp")]
                # along the window: the share of its width a tall piece covers
                line = [(box[0][0] + (box[1][0] - box[0][0]) * (k + 0.5) / 10 + nn[0] * 0.25,
                         box[0][1] + (box[1][1] - box[0][1]) * (k + 0.5) / 10 + nn[1] * 0.25) for k in range(10)]
                cov = _covered(line, [r for _g, r in tall])
                if cov > worst[0]:
                    worst = (cov, [g["id"] for g, r in tall if any(G.point_in_polygon(p, r) for p in line)])
            if worst[0] > LIMITS["window_cover"]:
                _open(f3, o["id"], f"{', '.join(worst[1][:2])} stand(s) in front of {100 * worst[0]:.0f}% of "
                      f"{o['id']}", f"Should {', '.join(worst[1][:2])} move away from window {o['id']}?",
                      [AA.option("keep")], where=where)
            else:
                _ok(f3, o["id"], "window free")
    return [f1, f2, f3, f4]


# --------------------------------------------------------------------------
# Site
# --------------------------------------------------------------------------

def site_rules(prep: dict) -> list[dict]:
    g1 = _q(next(r for r in RULES if r["id"] == "G1"))
    site = prep.get("site") or {}
    keep = []
    if len(site.get("outline") or []) >= 3:
        keep.append(("the house", site["outline"]))
    keep += [(f"pool {p.get('id')}", p["polygon"]) for p in site.get("pools") or [] if len(p.get("polygon") or []) >= 3]
    keep += [(f"path {a.get('id')}", a["polygon"]) for a in site.get("areas") or []
             if a.get("kind") == "path" and len(a.get("polygon") or []) >= 3]
    keep += [(f"{pf.get('kind')} {pf.get('id')}", pf["polygon"]) for pf in site.get("platforms") or []
             if pf.get("kind") in ("terrace", "pool", "parking") and not pf.get("sloped") and not pf.get("parent")
             and len(pf.get("polygon") or []) >= 3]          # a stepped band (``parent``) is a garden terrace
    for t in site.get("trees") or []:
        if t.get("build") is False or not t.get("center"):
            continue
        hit = next((name for name, poly in keep if G.point_in_polygon(t["center"][:2], poly)), None)
        if hit:
            _open(g1, t["id"], f"{t.get('kind', 'tree')} {t['id']} stands in {hit}",
                  f"Is {t['id']} drawn in the right place (a planter on purpose)?", [AA.option("keep")],
                  where=_where("tree", t.get("level_id"), t["center"]))
        else:
            _ok(g1, t["id"], "open ground")
    return [g1]


def review(building: dict, prep: dict, sides: list[dict], graph: dict, starts: list, is_stair, reach) -> list[dict]:
    """Every rule of ``RULES`` on every element it applies to (pure)."""
    plan = AA.Plan(building)
    out = rooms_rules(plan) + openings_rules(plan, sides) + walls_rules(plan) + \
        stairs_rules(plan, graph, starts, is_stair, reach) + furniture_rules(plan, sides)
    if prep.get("site") is not None:
        out += site_rules(prep)
    return out
