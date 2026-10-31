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

GAP_SILL_MAX_M = 0.20          # a plain opening with its bottom this low is a doorless doorway (F2)
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
    "threshold_tol_m": 0.03,
}
ROOM_MIN_M2 = {"bedroom": 6.5, "living": 10.0, "dining": 6.0, "kitchen": 4.0, "bathroom": 2.0, "wc": 1.0,
               "office": 5.0, "study": 5.0}
HABITABLE = ("bedroom", "living", "kitchen", "dining", "office", "study", "other")
WET = ("bathroom", "wc", "toilet", "shower")
WET_SET = set(WET)
UNKNOWN_TYPES = ("", "other", "unknown", "none")
ACCESS_TYPES = ("bed", "bed_double", "bed_single", "bed_bunk", "sofa", "sofa_corner", "wardrobe", "toilet", "sink",
                "washbasin", "kitchen_counter", "desk", "dresser", "bathtub", "shower", "fridge", "oven", "dishwasher",
                "washing_machine", "bookcase", "tv_unit", "sideboard")
COMPANIONS = ("chair", "dining_chair", "office_chair", "stool", "bar_stool", "coffee_table", "side_table",
              "nightstand", "rug", "ottoman", "bench", "plant", "floor_lamp", "lamp", "pouf", "armchair", "cushion",
              "towel", "bath_mat", "laundry_basket", "dining_table", "table")
FLOOR_ONLY = ("rug", "bath_mat", "carpet", "mat")
FAR_BASIN_MOVE_M = 1.5          # H2 (29 Oct 2026): a farther basin move to a solid wall is offered for the user's OK
FIXED_STAIRS = ("stair", "stairs", "staircase")
# 26 Oct 2026: a kitchen run's drawn pieces (a doorway they fill is a serving window over the counter)
KITCHEN_RUN = ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "hob", "oven", "fridge", "dishwasher")

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
    # 27 Oct 2026 (user on real06: "In some of the rooms the full windows from top to bottom (with a bit of remaining
    # wall of course) could look better")
    {"id": "W5", "topic": "tall windows", "scope": "room", "severity": "minor",
     "question": "In a style that favours large glazing, do the living, dining and bed rooms (and the rooms onto the "
                 "garden) get tall windows: from a low upstand to under the lintel, the same on every facade of the "
                 "room, where the documents fix no sill or head and no piece stands in front?",
     "why": "a Scandinavian or modern living room with 0.90 m sills and 1.20 m windows looks like an office; tall "
            "glass brings the garden in, and the documents' sills, a dresser's or a counter's sill stay"},
    # 29 Oct 2026 (user on real06: "If there is a window here it needs to alight with the stairs")
    {"id": "W6", "topic": "windows at stairs", "scope": "window", "severity": "major",
     "question": "Does every window behind a stair landing sit over it (its sill a guard height over the landing), and "
                 "does the window of the floor above light the stair from just over the landing?",
     "why": "a landing that cuts across a window's glass is a drawing or reading error a visitor sees at once"},
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
    {"id": "F5", "topic": "clashing furniture", "scope": "furniture", "severity": "major",
     "question": "Does any piece cut another (a side table in a sofa, a lamp in a bed, a chair through its table)?",
     "why": "two pieces through each other are the first thing a client sees in a render"},
    {"id": "F4", "topic": "room to use", "scope": "furniture", "severity": "minor",
     "question": "Is there room in front of every bed, sofa, wardrobe, WC and counter to use it (0.5 m)?",
     "why": "a piece you cannot reach or open is not usable"},
    # 26 Oct 2026 (user: "why the sink is so low, why doors are up ... I need ai models to see understand and fix
    # everything before even I look at it"): what a visitor sees at once
    {"id": "D4", "topic": "doors on their floor", "scope": "door", "severity": "major",
     "question": "Does every door stand on the floor of the rooms it joins (no door raised over both floors)?",
     "why": "a door that starts half a metre over the floor is the first thing a visitor sees; it is a level error"},
    # 26 Oct 2026 (user on real06's facade: "these sections not making sense": a 2.95 m flat oak leaf in the facade)
    {"id": "D5", "topic": "door types", "scope": "door", "severity": "major",
     "question": "What kind of door is every outside door and every wide door: French doors or a glazed sliding door "
                 "into a room, the entrance door at the front, a sectional door to the garage, and never one leaf "
                 "much wider than 1.2 m?",
     "why": "a 3 m flat wooden leaf in a facade reads as a garage door on a house that has none; a living room opens "
            "to the garden through glass"},
    # 27 Oct 2026 (user: "Not every opening inside the house requires a door or a window")
    {"id": "D6", "topic": "inside passages", "scope": "opening", "severity": "minor",
     "question": "Does every opening inside the house get only what the drawing and its rooms need: an open passage "
                 "where no leaf or swing arc is drawn, a door only where a room needs privacy (a bathroom, a WC, a "
                 "bedroom)?",
     "why": "a hall, a kitchen and a living room open into each other; a leaf or glass in a passage drawn open is a "
            "reading or decision error, a bathroom or bedroom behind an unclear gap needs its door"},
    # 29 Oct 2026 (user: "Doors looks without frames they need frames", "Sometimes maybe not needed frames but mostly
    # yes it does"; lesson UL122): framed by default, a concealed frameless door a choice of the minimal styles
    {"id": "D7", "topic": "door frames", "scope": "door", "severity": "minor",
     "question": "Is every door framed (a jamb lining, a head and an architrave on its indoor faces), unless it is a "
                 "concealed flush door of a minimal or modern style?",
     "why": "a door standing in a raw hole in the wall looks unfinished; a concealed frameless door is a choice, never "
            "an omission"},
    # 29 Oct 2026 (user on real06's dressing room: "this dressing could be a see through dressing room in the both
    # sides argus should have think of this"; lessons UL120, UL125)
    {"id": "D8", "topic": "walk-in dressing rooms", "scope": "room", "severity": "minor",
     "question": "Is every walk-in dressing room (a dressing room, or wardrobe runs facing each other across an aisle) "
                 "see-through on every side: slatted or glazed sliding fronts, or open runs, with real contents and a "
                 "light inside?",
     "why": "closed white panels on both sides of a narrow aisle read as a corridor of cupboards; a walk-in shows its "
            "clothes"},
    # 29 Oct 2026 (user: "Leaving all the doors open in default could be a good approach"; lessons UL116, UL126, UL127)
    {"id": "D9", "topic": "doors open", "scope": "door", "severity": "minor",
     "question": "Does every interior door stand open (its leaf turned open on its swing side, ajar where a piece or a "
                 "wall stops it), unless there is a reason to close it?",
     "why": "a house of closed doors reads as a corridor of panels; an open door shows the room beyond, an open front "
            "door reads as a mistake"},
    {"id": "H1", "topic": "working heights", "scope": "furniture", "severity": "major",
     "question": "Is every fixture at its working height (a washbasin's rim at 0.80-0.90 m)?",
     "why": "a basin at knee height looks like a toy and cannot be used"},
    # 29 Oct 2026 (user on real06 run 20261028-154514-full: "this sink not making sense there"; fixture_use rule 4)
    {"id": "H2", "topic": "a wall over every basin", "scope": "furniture", "severity": "major",
     "question": "Does every basin stand under a solid wall for its mirror and its tap, or under a high window (its "
                 "sill 1.25 m or more over the floor)?",
     "why": "a basin right under a window has no mirror over it and its tap meets the sill"},
    {"id": "G1", "topic": "trees", "scope": "tree", "severity": "minor",
     "question": "Does every tree and shrub stand on open ground, clear of the house, the pools, the paths and the "
                 "terraces?",
     "why": "a tree through a terrace or in front of a door is a reading or placement error"},
    # 28 Oct 2026 (user on real04: "There could be better outside solutions to the grade slope", "Better solutions
    # needed for the elevation difference outside"; wenart/blender/grading.py, the model review's M15)
    {"id": "G2", "topic": "grading", "scope": "site", "severity": "minor",
     "question": "Does the garden meet every level difference as a landscape architect would build it: a planted "
                 "slope of at most 1:3 (lawn) or 1:2 (ground cover), terraced planters at one level per side with a "
                 "coping and planting, garden steps of solid blocks (each tread on its riser, cheek walls, a landing at "
                 "the foot), retaining walls in the house's base stone with a coping (never bare concrete), paths level "
                 "across and stepped where steeper than 1:12, a ramp only on an accessible route?",
     "why": "bare concrete boxes stacked like stairs, loose treads in the grass and a paved strip tilted across the "
            "slope read as raw blocks, not as a designed garden"},
    # 28 Oct 2026 (user: "I am not liking this is the only outside flooring")
    {"id": "G3", "topic": "outdoor floors", "scope": "site", "severity": "minor",
     "question": "Does each outdoor floor have the material of its use (the terrace and pool deck, the steps, the "
                 "garden path, the drive), in one language with the house's base, never one slab everywhere?",
     "why": "one paving on the terraces, the steps, the paths and the drive reads as a car park, not a garden"},
)


def _q(rule: dict) -> dict:
    return dict(rule, answers=[], status="ok")


def _open(q: dict, element: str, found: str, ask: str, options: list, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": None, "open": True, "ask": ask,
                              "options": options}, **extra))
    q["status"] = "open"


def _ok(q: dict, element: str, found: str, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": None}, **extra))


INNER_WINDOW = {"door_gap_m": 0.3, "tall_m": 1.0, "against_m": 0.45, "cover_share": 0.3}
PRIVATE_TYPES = ("bedroom",)
TALL_TYPES = ("wardrobe", "tall_cabinet", "bookshelf", "display_cabinet", "fridge", "kitchen_counter", "dresser",
              "shoe_cabinet", "sideboard", "bed_double", "bed_single", "bunk_bed")


def inner_window_problems(plan, o: dict, a: dict, b: dict, glass: dict) -> list[str]:
    """Why an inner window between rooms ``a`` and ``b`` makes no sense (pure; ``inner_window_reasons``)."""
    return [text for _kind, text in inner_window_reasons(plan, o, a, b, glass)]


def inner_window_soft(plan, reasons: list, a: dict, b: dict, glass: dict) -> bool:
    """Whether the only reason against an inner window is a door beside it while it is the only daylight of a
    habitable room (pure; 29 Oct 2026): then closing it is offered, never chosen by default."""
    return bool(reasons) and all(k == "door_side" for k, _t in reasons) and any(
        _rtype(x) in HABITABLE and glass.setdefault(x["id"], AA.outside_glass(plan, x["id"])[0]) <= 1e-6
        for x in (a, b))


def inner_window_reasons(plan, o: dict, a: dict, b: dict, glass: dict) -> list[tuple[str, str]]:
    """Why an inner window between rooms ``a`` and ``b`` makes no sense, as (kind, text) (pure; 29 Oct 2026,
    ``INNER_WINDOW``): ``wet``: a wet room on a side; ``door_side``: a door or opening on its wall within
    ``door_gap_m`` of it (side lights read as windows); ``against``: a piece over its sill or a tall one
    (``TALL_TYPES``) against it, within ``against_m`` of the wall over ``cover_share`` of its width; ``both_lit``:
    both rooms lit by their own outside glass and a bedroom on a side (no room needs its light)."""
    from shapely.geometry import LineString, Polygon

    out = []
    wet = sorted({x["id"] for x in (a, b) if _rtype(x) in WET_SET})
    if wet:
        out.append(("wet", f"{', '.join(wet)} is a wet room (no window into it from another room)"))
    w = plan.walls.get(o.get("wall_id"))
    if w is not None:
        t, half = plan.t_of(w, o["center"]), float(o.get("width") or 0.0) / 2.0
        for p in plan.openings.values():
            if p["id"] == o["id"] or p.get("wall_id") != o.get("wall_id") or p.get("type") not in ("door", "opening"):
                continue
            tp, hp = plan.t_of(w, p["center"]), float(p.get("width") or 0.0) / 2.0
            gap = max(tp - hp - (t + half), t - half - (tp + hp))
            if gap <= INNER_WINDOW["door_gap_m"]:
                out.append(("door_side", f"it stands {max(gap, 0.0):.2f} m beside {p['id']} (a door's side read as a "
                                          f"window)"))
                break
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        span = LineString([(float(o["center"][0]) - ux * half, float(o["center"][1]) - uy * half),
                           (float(o["center"][0]) + ux * half, float(o["center"][1]) + uy * half)])
        band = span.buffer(INNER_WINDOW["against_m"], cap_style=2)
        sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
        for f in plan.b.get("furniture") or []:
            fp = f.get("footprint") or {}
            if f.get("build") is False or not fp.get("center") or f.get("room_id") not in (a["id"], b["id"]):
                continue
            h = f.get("height") or ((f.get("asset") or {}).get("bbox_m") or [None, None, None])[2]
            if not ((h is not None and float(h) > sill + 0.05) or (h is None and f.get("type") in TALL_TYPES)):
                continue
            cx, cy = (float(v) for v in fp["center"][:2])
            sw, sd = (float(v) for v in fp["size"][:2])
            r = math.radians(float(fp.get("rotation_deg") or 0.0))
            pts = [(cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r))
                   for dx, dy in ((-sw / 2, -sd / 2), (sw / 2, -sd / 2), (sw / 2, sd / 2), (-sw / 2, sd / 2))]
            piece = Polygon(pts)
            if not piece.is_valid or not piece.intersects(band):
                continue
            proj = [((px - x0) * ux + (py - y0) * uy) for px, py in pts]
            cover = min(max(proj), t + half) - max(min(proj), t - half)
            if cover >= INNER_WINDOW["cover_share"] * 2 * half:
                out.append(("against", f"{f['id']} ({f.get('type')}) stands against it"))
                break
    lit = [x["id"] for x in (a, b) if glass.setdefault(x["id"], AA.outside_glass(plan, x["id"])[0]) > 1e-6]
    private = [x["id"] for x in (a, b) if _rtype(x) in PRIVATE_TYPES]
    if len(lit) == 2 and private:
        # a window between two lit day rooms (a kitchen and a living room) may be a view on purpose; into a bedroom
        # it only costs privacy
        out.append(("both_lit", f"{a['id']} and {b['id']} both have outside windows (no room needs its light) and "
                                f"{', '.join(private)} needs privacy"))
    return out


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


def openings_rules(plan: AA.Plan, sides: list[dict], unreached: Optional[set] = None) -> list[dict]:
    w2, w3, o1, d1, d2, d4 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("W2", "W3", "O1", "D1", "D2", "D4"))
    side_of = {s["opening"]["id"]: s for s in sides}
    ground = _ground_z(plan.b)
    glass = {}
    # 27 Oct 2026 (user on real06: "doors next to each other not making sense"): two drawn doors on one wall between
    # the same two rooms whose frames touch or overlap are one passage drawn or read twice (``door_spacing``): merged
    # by default like two openings over each other; a door a decision made beside a door is undone where it was made
    from wenart.blender import door_spacing as DS
    twins: dict = {}
    for r in DS.conflicts(plan.b)[0]:
        x, y = (plan.openings.get(i) for i in r["doors"])
        if r["kind"] in ("overlap", "frames") and r["same_rooms"] and not r["made_by"] and x is not None \
                and y is not None and x.get("wall_id") == y.get("wall_id"):
            twins.setdefault(x["id"], (y["id"], r))
            twins.setdefault(y["id"], (x["id"], r))
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
        pair = twins.get(o["id"])
        if pair is not None and not any(pair[0] in x for x in problems):
            gap = pair[1]["gap_m"]
            problems.append(f"its frame touches {pair[0]}" + (f" ({max(gap, 0.0):.2f} m apart)" if gap is not None
                                                              else "") + f", both doors between "
                            f"{' and '.join(pair[1]['rooms'][o['id']])}: one passage drawn or read twice")
        if problems:
            # 26 Oct 2026: two openings over each other on one wall are one opening read twice: merged by default
            twin = next((p for p in plan.openings.values() if p["id"] != o["id"] and p.get("wall_id") == o.get("wall_id")
                         and min(t + half, plan.t_of(w, p["center"]) + float(p.get("width") or 0.0) / 2.0)
                         - max(t - half, plan.t_of(w, p["center"]) - float(p.get("width") or 0.0) / 2.0)
                         > LIMITS["overlap_tol_m"]), None)
            if twin is None and pair is not None:
                twin = plan.openings.get(pair[0])
            opts = ([AA.option("merge_openings", f"one opening read twice: merge it with {twin['id']}",
                               other_id=twin["id"])] if twin is not None else []) + [AA.option("keep")]
            _open(o1, o["id"], f"{o['id']} " + "; ".join(problems), f"Is {o['id']} drawn on the right wall and "
                  f"at the right size?", opts, where=where,
                  **({"default": opts[0]["choice"]} if twin is not None and o["id"] < twin["id"] else {}))
        else:
            _ok(o1, o["id"], f"fits {w['id']}")
        if o.get("type") == "window":
            # W2: to the outside
            if out_a or out_b:
                _ok(w2, o["id"], "to the outside" if a is None or b is None else "onto an open-air room")
            elif o.get("interior_glazing") and a is not None and b is not None:
                # 26 Oct 2026: decided as a borrowed-light, high or serving window; 29 Oct 2026: a decision kept
                # against a reason the window makes no sense is asked again, closing it by default (a serving hatch
                # over a drawn counter is no window to close)
                kind = o["interior_glazing"].get("kind", "clear")
                reasons = [] if kind == "pass_through" else inner_window_reasons(plan, o, a, b, glass)
                against = [] if inner_window_soft(plan, reasons, a, b, glass) else [t for _k, t in reasons]
                if against:
                    _open(w2, o["id"], f"{o['id']} was kept as a {kind} borrowed-light window between {a['id']} and "
                          f"{b['id']}; against it: {'; '.join(against)}",
                          f"Should {o['id']} stay a window between {a['id']} and {b['id']}?",
                          [AA.option("close_window", "close it: " + "; ".join(against)),
                           AA.option("keep", f"keep the {kind} borrowed-light window")],
                          where=where, room=a["id"], default="close_window", fallback=["keep"])
                else:
                    _ok(w2, o["id"], f"a {kind} borrowed-light window between {a['id']} and {b['id']} (decided)")
            elif a is not None and b is not None:
                dark = [x for x in (a, b) if _rtype(x) in HABITABLE]
                room = min(dark or [a, b], key=lambda x: glass.setdefault(
                    x["id"], AA.outside_glass(plan, x["id"])[0]))
                other = b if room is a else a
                # 26 Oct 2026: moved by default when the darker room has no glass to the outside at all (or the
                # window stands inside one room): a borrowed light then is a reading error, never a design
                dark_glass = glass.setdefault(room["id"], AA.outside_glass(plan, room["id"])[0])
                default = "move_window_to_outer_wall" if (dark_glass <= 1e-6 or room["id"] == other["id"]) else None
                opts = [AA.option("move_window_to_outer_wall", f"a reading error: move it to the outer wall of "
                                  f"{room['id']}", room_id=room["id"]),
                        AA.option("keep", "a borrowed-light window on purpose")]
                # 26 Oct 2026 (user: "let it take decisions more"): when it cannot move (no free outer wall) or the
                # dark room has glass of its own, the architect keeps it as a borrowed-light window: clear glass
                # between dry rooms, a high window (sill 1.80 m) where one side is a bathroom
                wet_side = WET_SET & {_rtype(a), _rtype(b)}
                keep_as = AA.option("high_window", "a high borrowed-light window (sill 1.80 m) for the bathroom's "
                                    "privacy") if wet_side else \
                    AA.option("interior_glazing", "a borrowed-light window on purpose (clear glass)")
                opts.insert(1, keep_as)
                # 29 Oct 2026 (user on real06: "these windows are not making sense" (two windows beside the door
                # between a shower room and a dressing room), "This window and dolap is not making sense" (a hall
                # window onto a wardrobe)): an inner window with a reason against it is closed by default
                # (only a door beside it while it is a dark room's only daylight: closing it is offered, the
                # borrowed light stays the fallback)
                reasons = inner_window_reasons(plan, o, a, b, glass)
                soft = inner_window_soft(plan, reasons, a, b, glass)
                against = [t for _k, t in reasons]
                if against:
                    opts.insert(2 if soft else 1, AA.option("close_window", "close it: " + "; ".join(against)))
                    if default is None and not soft:
                        default = "close_window"
                # a room no door reaches: the widest window from a reached room is its door (a misread door)
                lost = [x for x in (a, b) if x["id"] in (unreached or set())]
                if len(lost) == 1 and a["id"] != b["id"]:
                    rival = [p for p in plan.openings.values() if p.get("type") == "window" and p["id"] != o["id"]
                             and lost[0]["id"] in [(r or {}).get("id") for r in AA.window_sides(plan, p)]
                             and not any((r or {}).get("id") in (unreached or set()) - {lost[0]["id"]}
                                         or AA.Plan.is_outside(r) for r in AA.window_sides(plan, p))]
                    opts.insert(0, AA.option("window_to_door", f"{lost[0]['id']} has no door: this is its door"))
                    if all(float(p.get("width") or 0.0) < float(o.get("width") or 0.0) or
                           (float(p.get("width") or 0.0) == float(o.get("width") or 0.0) and p["id"] > o["id"])
                           for p in rival):
                        default = "window_to_door"
                _open(w2, o["id"], f"{o['id']} sits in the wall between {room['id']} ({_rtype(room)}) and "
                      f"{other['id']} ({_rtype(other)})" + (f"; against it: {'; '.join(against)}" if against else ""),
                      f"Is {o['id']} on the outer wall of {room['id']} in the drawing (a reading error), or a "
                      f"borrowed-light window on purpose?", opts, where=where, room=room["id"],
                      **({"default": default} if default else {}),
                      fallback=["close_window"] if against and not soft else [keep_as["choice"]])
            # W3: low sills over a drop
            lv = plan.levels[o["level_id"]]
            drop = float(lv["elevation"]) - ground
            if (a is None or b is None) and not (out_a and out_b) and drop >= LIMITS["sill_drop_m"]:
                if sill + 1e-6 < LIMITS["sill_safe_m"]:
                    # 26 Oct 2026: the low sill gets a real guard by default (a guard across the window,
                    # 1.10 m over the floor); "keep: a guard is fitted" had fitted none
                    if o.get("guard"):
                        _ok(w3, o["id"], f"sill {sill:.2f} m with a guard to {float(o['guard'].get('top_m') or 1.1):.2f} m")
                    else:
                        _open(w3, o["id"], f"{o['id']} on level {o['level_id']} ({drop:.1f} m over the ground) has "
                              f"its sill at {sill:.2f} m", f"Does {o['id']} need a higher sill, or is it a French "
                              f"window with a guard?",
                              [AA.option("french_window", "keep the low sill: a guard across the window",
                                         door_id=o["id"]), AA.option("raise_sill"), AA.option("keep")],
                              where=where, default=f"french_window")
                else:
                    _ok(w3, o["id"], f"sill {sill:.2f} m")
        elif o.get("type") == "door":
            width = float(o.get("width") or 0.0)
            to_out = (a is None) != (b is None) or (out_a != out_b)
            wet = _rtype(a) in WET or _rtype(b) in WET
            need = LIMITS["door_outside_min_m"] if to_out else (LIMITS["door_wet_min_m"] if wet else
                                                                LIMITS["door_min_m"])
            # 26 Oct 2026: an upper-floor door to no open-air room is E1's (a door into the air), never widened
            upper_air = to_out and (a is None or b is None) and \
                float(plan.levels[o["level_id"]]["elevation"]) - ground >= LIMITS["sill_drop_m"]
            # D4: the door on the floor of its rooms (a threshold over both floors is a level reading error)
            floors = [z for z in (AA.room_floor(plan, x) for x in (a, b) if x is not None and not AA.Plan.is_outside(x))
                      if z is not None]
            thr = o.get("threshold_z")
            if floors and thr is not None and float(thr) - max(floors) > LIMITS["threshold_tol_m"]:
                _open(d4, o["id"], f"{o['id']}'s threshold {float(thr):+.2f} m is {float(thr) - max(floors):.2f} m "
                      f"over the floor of its room(s) ({', '.join(f'{z:+.2f}' for z in floors)} m)",
                      f"Should {o['id']} stand on its floor?", [AA.option("snap_threshold"), AA.option("keep")],
                      where=where, default="snap_threshold")
            elif floors:
                _ok(d4, o["id"], "on its floor")
            if upper_air:
                pass
            elif width + 1e-6 < need:
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
    return [w2, w3, o1, d1, d2, d4]


def door_types(plan: AA.Plan, sides: list[dict]) -> list[dict]:
    """D5 (pure): the kind of every outside door and every door of ``architect_actions.WIDE_DOOR_M`` or more
    (``architect_actions.door_kind``: the room behind it, the main entrance, the drawn operation). A door that needs
    a kind is open with the safe default the build carries out (``architect.defaults_of``: French doors or a glazed
    sliding door into a room, the entrance door, a sectional garage door, two leaves inside) and the other kinds as
    options; a door already decided (``door_decision``) or right as one leaf is fine. A door of an upper floor with
    nothing outside is E1's question (a door into the air), not a door type."""
    d5 = _q(next(r for r in RULES if r["id"] == "D5"))
    side_of = {s["opening"]["id"]: s for s in sides}
    ground = _ground_z(plan.b)
    main = AA.main_entrance_id(plan.b)
    for o in plan.openings.values():
        if o.get("type") != "door" or plan.walls.get(o.get("wall_id")) is None or o.get("level_id") not in plan.levels:
            continue
        s = side_of.get(o["id"]) or {}
        a, b = plan.room.get(s.get("a")), plan.room.get(s.get("b"))
        out_a, out_b = AA.Plan.is_outside(a), AA.Plan.is_outside(b)
        if out_a and out_b:
            continue                                     # no room on either side: D2's question
        outer = out_a != out_b
        if outer and (a is None or b is None) and \
                float(plan.levels[o["level_id"]]["elevation"]) - ground >= LIMITS["sill_drop_m"]:
            continue                                     # an upper-floor door onto nothing: E1's
        width = float(o.get("width") or 0.0)
        dec = o.get("door_decision")
        if isinstance(dec, dict) and dec.get("kind") in AA.DOOR_KINDS:
            _ok(d5, o["id"], f"{width:.2f} m: {AA.DOOR_KINDS[dec['kind']]['label']}")
            continue
        rooms = [_rtype(x) for x in (a, b) if x is not None and not AA.Plan.is_outside(x)]
        kind, why, others = AA.door_kind(width, rooms, outer, o["id"] == main, AA.drawn_operation(o))
        if kind is None:
            _ok(d5, o["id"], why)
            continue
        opts = [AA.option("door_type", AA.DOOR_KINDS[k]["label"], door_id=o["id"], kind=k) for k in [kind] + others]
        opts.append(AA.option("keep", f"keep one {width:.2f} m leaf as drawn"))
        _open(d5, o["id"], f"{o['id']} is {why}", f"What kind of door is {o['id']} ({width:.2f} m)?", opts,
              where=_where("door", o.get("level_id"), o["center"]), default=opts[0]["choice"])
    return [d5]


def tall_windows_rule(plan: AA.Plan, family: Optional[str]) -> list[dict]:
    """W5 (pure; 27 Oct 2026): in a style family that favours tall glazing (``architect_actions.tall_glazing``), every
    room that may get tall windows (``architect_actions.tall_room``) with a facade whose windows may grow
    (``tall_window_groups``) is open with the safe default ``tall_window`` (the architect carries it out; the AI
    architect or the user may keep the sills); a room whose windows are tall, or kept (the documents, a piece in front,
    no garden), is fine with the reason. Another family keeps its sills (not asked)."""
    w5 = _q(next(r for r in RULES if r["id"] == "W5"))
    if not AA.tall_glazing(family):
        return [w5]
    for r in plan.rooms:
        if r.get("level_id") not in plan.levels or not AA.tall_room(plan, r["id"]):
            continue
        groups = AA.tall_window_groups(plan, r["id"])
        if not groups:
            continue
        found = "; ".join(f"facing {g['facing_deg']:.0f} deg: {g['state']} ({g['why']})" for g in groups)
        if any(g["state"] == "grow" for g in groups):
            opts = [AA.option("tall_window", f"tall windows ({family} style): from a {AA.TALL_SILL_M:.2f} m upstand "
                              f"to {AA.LINTEL_M:.2f} m under the ceiling", room_id=r["id"]),
                    AA.option("keep", "keep the sills as they are")]
            _open(w5, r["id"], f"{r['id']} ({_rtype(r)}, {family} style): {found}",
                  f"Should the windows of {r['id']} be tall windows?", opts,
                  where=_where("room", r.get("level_id"), _centroid(r["polygon"])), default="tall_window")
        else:
            _ok(w5, r["id"], found)
    return [w5]


STAIR_WINDOW = {"reach_m": 0.35, "over_m": 0.9, "low_sill_m": 0.3, "cut_m": 0.05, "cover_share": 0.3,
                "raise_gap_m": 0.4}


def stair_parts(building: dict, level: dict) -> list[tuple]:
    """``(polygon, top, stair id, void)`` of every half landing and winder of the stairs that start on ``level``
    (``stair_access.planned``: tops over the level's floor; ``void``: the stair's opening in the floor above)."""
    from shapely.geometry import Polygon

    from wenart.blender import stair_access as SA

    out = []
    for it in SA.planned(building, level):
        p = it.get("plan") or {}
        land = p.get("landing") if isinstance(p.get("landing"), dict) else {}
        sid = (it.get("piece") or {}).get("id")
        rings = p.get("void") if isinstance(p.get("void"), list) else []
        if rings and not isinstance(rings[0][0], (list, tuple)):
            rings = [rings]                                  # one ring or a list of rings
        from shapely.ops import unary_union
        polys = [Polygon(r).buffer(0) for r in rings if isinstance(r, (list, tuple)) and len(r) >= 3]
        void = unary_union(polys) if polys else None
        if land.get("role") == "winders":
            parts = [(w.get("polygon"), w.get("top")) for w in land.get("winders") or []]
        elif land.get("role") == "mid":
            parts = [(land.get("polygon"), land.get("z"))]
        else:
            continue
        for poly, top in parts:
            if isinstance(poly, list) and len(poly) >= 3 and top is not None:
                out.append((Polygon(poly).buffer(0), float(top), sid, void))
    return out


def _span_parts(plan: AA.Plan, o: dict, parts: list[tuple]) -> list[tuple]:
    """The stair parts that stand against window ``o``'s span: within ``reach_m`` of its wall's face and over
    ``cover_share`` of its width along the wall (pure)."""
    from shapely.geometry import LineString

    w = plan.walls.get(o.get("wall_id"))
    if w is None:
        return []
    (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    half = float(o.get("width") or 0.0) / 2.0
    cx, cy = (float(v) for v in o["center"][:2])
    span = LineString([(cx - ux * half, cy - uy * half), (cx + ux * half, cy + uy * half)])
    band = span.buffer(float(w.get("thickness") or 0.2) / 2.0 + STAIR_WINDOW["reach_m"], cap_style=2)
    t = plan.t_of(w, o["center"])
    out = []
    for poly, top, sid, void in parts:
        inter = poly.intersection(band)
        if inter.is_empty:
            continue
        proj = [((px - x0) * ux + (py - y0) * uy) for px, py in inter.exterior.coords] if inter.geom_type == "Polygon" \
            else [((px - x0) * ux + (py - y0) * uy) for g in getattr(inter, "geoms", []) if g.geom_type == "Polygon"
                  for px, py in g.exterior.coords]
        if proj and min(max(proj), t + half) - max(min(proj), t - half) >= STAIR_WINDOW["cover_share"] * 2 * half:
            out.append((poly, top, sid, void))
    return out


def stair_window_findings(plan: AA.Plan) -> list[dict]:
    """The windows a stair's half landing or winders stand against (pure; 29 Oct 2026, ``STAIR_WINDOW``): ``cut``
    (the stair surface over the window's sill: the landing cuts across its glass; to raise it a guard height over the
    landing, or to close when it cannot rise and a window of the level above lights the stair) and ``high`` (a window
    of the level above over the stair's opening, more than ``raise_gap_m`` over a guard height above the landing: to
    lower it so it starts over the landing). Each: ``window``, ``kind``, ``level_id``, ``top`` (the landing over its
    level's floor), ``stair``, ``sill``, ``height`` (the new ones, None when it cannot change), ``upper`` (the window
    of the level above that lights the stair), ``why``."""
    b = plan.b
    order = sorted(plan.levels.values(), key=lambda lv: float(lv["elevation"]))
    out = []
    for i, lv in enumerate(order):
        parts = stair_parts(b, lv)
        if not parts:
            continue
        above = order[i + 1] if i + 1 < len(order) else None
        here = [o for o in plan.openings.values() if o.get("type") == "window" and o.get("level_id") == lv["id"]]
        up = [o for o in plan.openings.values() if above is not None and o.get("type") == "window"
              and o.get("level_id") == above["id"]]
        e0, e1 = float(lv["elevation"]), float(above["elevation"]) if above is not None else None
        uppers = {}
        for o in up:
            hit = _span_parts(plan, o, parts)
            if hit:
                uppers[o["id"]] = (o, max(h[1] for h in hit), hit[0][2], hit)
        for o in here:
            hit = _span_parts(plan, o, parts)
            if not hit:
                continue
            top = max(h[1] for h in hit)
            sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
            height = float(o.get("height") if o.get("height") is not None else 1.2)
            if top <= sill - STAIR_WINDOW["cut_m"]:
                continue
            new_sill = top + STAIR_WINDOW["over_m"]
            limit = plan.top(o)
            new_h = min(height, limit - new_sill)
            stacked = [u for u, *_r in uppers.values()]
            rec = {"window": o["id"], "kind": "cut", "level_id": lv["id"], "top": round(top, 3), "stair": hit[0][2],
                   "upper": stacked[0]["id"] if stacked else None, "sill": None, "height": None}
            if new_h >= AA.MIN_WINDOW_H - 1e-6:
                rec.update(sill=round(new_sill, 3), height=round(new_h, 3),
                           why=f"the stair's landing at {top:.2f} m stands across its sill at {sill:.2f} m: the sill "
                               f"rises a guard height over the landing")
            else:
                rec["why"] = (f"the stair's landing at {top:.2f} m stands across its sill at {sill:.2f} m and a sill "
                              f"{STAIR_WINDOW['over_m']:.2f} m over it leaves {max(new_h, 0.0):.2f} m of glass under "
                              f"{limit:.2f} m")
            out.append(rec)
        for o, top, sid, hit in uppers.values():
            void = next((h[3] for h in hit if h[3] is not None), None)
            if void is None or e1 is None:
                continue
            from shapely.geometry import Point
            w = plan.walls.get(o.get("wall_id"))
            inner = [r for r in AA.window_sides(plan, o) if r is not None and not AA.Plan.is_outside(r)]
            if w is None or not inner:
                continue
            if void.distance(Point(*[float(v) for v in o["center"][:2]])) > \
                    float(w.get("thickness") or 0.2) / 2.0 + STAIR_WINDOW["reach_m"]:
                continue                               # a floor stands in front of it on its level
            sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
            height = float(o.get("height") if o.get("height") is not None else 1.2)
            want = max(STAIR_WINDOW["low_sill_m"], e0 + top + STAIR_WINDOW["over_m"] - e1)
            if sill - want <= STAIR_WINDOW["raise_gap_m"]:
                continue
            head = sill + height
            out.append({"window": o["id"], "kind": "high", "level_id": o["level_id"], "top": round(top, 3),
                        "stair": sid, "upper": None, "sill": round(want, 3), "height": round(head - want, 3),
                        "why": f"it lights the stair over its opening: its sill {sill:.2f} m starts "
                               f"{e1 + sill - e0 - top:.2f} m over the landing ({top:.2f} m over {lv['id']}); it "
                               f"starts {STAIR_WINDOW['over_m']:.2f} m over the landing (at least "
                               f"{STAIR_WINDOW['low_sill_m']:.2f} m over its floor), its head kept"})
    return out


def stair_windows_rule(plan: AA.Plan) -> list[dict]:
    """W6 (29 Oct 2026, user on real06: "If there is a window here it needs to alight with the stairs"): every
    finding of ``stair_window_findings`` is open with its safe default (the architect carries it out); a ``cut``
    window that cannot rise is closed when a window of the level above lights the stair, else kept (asked)."""
    w6 = _q(next(r for r in RULES if r["id"] == "W6"))
    for f in stair_window_findings(plan):
        o = plan.openings.get(f["window"])
        if o is None:
            continue
        where = _where("window", o.get("level_id"), o["center"])
        opts, default = [], None
        if f["sill"] is not None:
            opts.append(AA.option("stair_window", f"set it to the stair: sill {f['sill']:.2f} m, {f['height']:.2f} m "
                                  f"of glass", window_id=o["id"], sill=f["sill"], height=f["height"], why=f["why"]))
            default = opts[-1]["choice"]
        elif f["upper"]:
            opts.append(AA.option("close_stair_window", f"close it: {f['upper']} of the level above lights the stair",
                                  window_id=o["id"], why=f"{f['why']}; {f['upper']} of the level above lights the "
                                                         f"stair"))
            default = opts[-1]["choice"]
        opts.append(AA.option("keep", "keep it as drawn"))
        _open(w6, o["id"], f"{o['id']} ({f['kind']}): {f['why']}" + (f" (stair {f['stair']})" if f['stair'] else ""),
              f"Should {o['id']} be set to the stair {f['stair'] or ''} in front of it?", opts, where=where,
              **({"default": default} if default else {}))
    return [w6]


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
    from wenart.furniture import fixture_use as FU

    f1, f2, f3, f4, h1, h2 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("F1", "F2", "F3", "F4", "H1", "H2"))
    openings = [o for o in plan.b.get("openings") or [] if o.get("id")]
    pieces = []
    for f in plan.b.get("furniture") or []:
        if f.get("build") is False or str(f.get("type") or "").lower() in FIXED_STAIRS:
            continue                       # 26 Oct 2026: a stair is built like a wall, never moved for a doorway
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
        # H1 (26 Oct 2026): a fixture's working top, measured on the model the fit chose (a wall-hung basin model
        # stood on the floor with its rim at 0.54 m; a 0.10 m bowl lay on the floor)
        rule = AA.FIXTURE_TOPS.get(t)
        fh = AA.fitted_height(f) if rule else None
        if rule and fh is not None:
            low, high, target = rule
            top = fh + float(f.get("mount_bottom_m") or 0.0)
            # a model taller than the working top may carry its mirror or tap: its rim is not its top, it passes
            if top >= low - 1e-6:
                _ok(h1, f["id"], f"{t} top at {top:.2f} m")
            else:
                hang = 0.30 <= fh < low
                opts = ([AA.option("mount_fixture", f"hang it with its top at {target:.2f} m")] if hang else []) + \
                    [AA.option("remove_piece", "another model is needed: not built as it is"), AA.option("keep")]
                _open(h1, f["id"], f"{f['id']} ({t}) has its top at {top:.2f} m (a {t} works at {low:.2f}-"
                      f"{high:.2f} m; the model is {fh:.2f} m tall)", f"Should {f['id']} be at its working height?",
                      opts, where=where, **({"default": "mount_fixture"} if hang else {}))
        pts = _grid(rect)
        inside = sum(1 for p in pts if G.point_in_polygon(p, room["polygon"])) / len(pts)
        if inside + 1e-6 < LIMITS["piece_inside"]:
            _open(f1, f["id"], f"{f['id']} ({t}) stands {100 * (1 - inside):.0f}% outside {room['id']}",
                  f"Is {f['id']} in the right place?", [AA.option("keep")], where=where)
        else:
            _ok(f1, f["id"], f"{t} in {room['id']}")
        here = [g for g, _r, _t in by_room.get(f.get("room_id"), [])]
        if t in FU.BASINS:
            _basin_wall(plan, h2, f, room, here, openings, where)
        if t in FU.DOOR_FRONTED and not FU.in_run(f, here) and not (t in FU.STORAGE_OPEN_M
                                                                     and f.get("mount_bottom_m")):
            # 29 Oct 2026 (user on real06: "This washing machine would not open"; fixture_use rule 1): a door-fronted
            # piece keeps its width x its access depth free; the safe default turns a blocked front to its free side
            # (rule 2: a front read the wrong way round), else the point stays for the AI architect and the user.
            # 30 Oct 2026 (real04 run 20261029-201533-full: the drawn wardrobes f_L0_009 / f_L0_011 had 0.17 m free,
            # the drawn desks before their doors; the model review's M19 found it critical while this rule measured
            # the wardrobes with its old 80 % strip, 88 % free): door-fronted storage is measured like M19 and U16
            # (``piece_access`` with storage, one measure for one fault), and a front that cannot open gets
            # ``clear_front`` (rule 5: the safest move of the piece or of what stands in front of it that passes
            # every code check) as its default, or after ``free_front`` as the next safe fix
            prob = FU.piece_access(f, room["polygon"], here, storage=True)
            if prob is None:
                _ok(f4, f["id"], "its door or drawers open: free in front")
            else:
                blocked = AA._door_blocked(plan, f.get("level_id"))
                fix = FU.free_front(f, room["polygon"], here, blocked=blocked) if t in FU.ACCESS_M else None
                clear = (FU.clear_front(f, room["polygon"], here, blocked=blocked, openings=openings,
                                        walls=plan.walls) if prob["severity"] == "critical" else None)
                opts = ([AA.option("free_front", f"turn or move {f['id']} so its door opens: {fix['reason']}",
                                   piece_id=f["id"])] if fix else [])
                if clear:
                    opts.append(AA.option("clear_front", f"clear the front of {f['id']}: {clear['reason']}",
                                          piece_id=f["id"]))
                opts.append(AA.option("keep"))
                chain = [o["choice"] for o in opts if o["id"] != "keep"]
                _open(f4, f["id"], FU.describe(f, prob), f"Can {f['id']} be opened and used where it stands?", opts,
                      where=where, **({"default": chain[0], "fallback": chain[1:]} if chain else {}))
        elif t in ACCESS_TYPES and f.get("front_deg") is not None:
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
        # 26 Oct 2026 (Argus, real06): a doorless gap is a doorway too (the code critic's F7 calls it a door: a drawn
        # counter across real06's 2.9 m kitchen gap was a critical every run while this rule never looked at it)
        gap = s["type"] == "opening" and float(o.get("sill_height") or 0.0) <= GAP_SILL_MAX_M
        if w is None or (s["type"] not in ("door", "window") and not gap):
            continue
        _a, u, _l = plan.axis(w)
        n = (-u[1], u[0])
        c = (plan.at_t(w, plan.t_of(w, o["center"])))
        half_t = float(w.get("thickness") or 0.2) / 2.0
        width = float(o.get("width") or 0.0)
        where = _where(s["type"], o.get("level_id"), o["center"])
        if s["type"] == "door" or gap:
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
                first = worst[2][0] if worst[2] else None
                opts = ([AA.option("move_piece", f"move {first} clear of the doorway", piece_id=first,
                                   away_from=o["id"])] if first else [])
                # 26 Oct 2026 (user: "let it take decisions more"): when the piece cannot move, a doorway a drawn
                # kitchen run fills is a serving window over the counter, and a piece the AI added gives way
                chain = _blocked_chain(plan, first, o, s, door=True)
                opts += chain + [AA.option("keep")]
                _open(f2, o["id"], f"{100 * worst[0]:.0f}% of the doorway of {o['id']} in {worst[1]} is taken by "
                      f"{', '.join(worst[2][:3])}", f"Should {', '.join(worst[2][:2])} move away from {o['id']}?",
                      opts, where=where, **({"default": opts[0]["choice"]} if first else {}),
                      fallback=[c["choice"] for c in chain])
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
                first = worst[1][0] if worst[1] else None
                opts = ([AA.option("move_piece", f"move {first} away from the window", piece_id=first,
                                   away_from=o["id"])] if first else [])
                chain = _blocked_chain(plan, first, o, s, door=False)
                opts += chain + [AA.option("keep")]
                _open(f3, o["id"], f"{', '.join(worst[1][:2])} stand(s) in front of {100 * worst[0]:.0f}% of "
                      f"{o['id']}", f"Should {', '.join(worst[1][:2])} move away from window {o['id']}?",
                      opts, where=where, **({"default": opts[0]["choice"]} if first else {}),
                      fallback=[c["choice"] for c in chain])
            else:
                _ok(f3, o["id"], "window free")
    return [f1, f2, f3, f4, h1, h2]


def _basin_wall(plan: AA.Plan, h2: dict, f: dict, room: dict, here: list, openings: list, where: dict) -> None:
    """H2 (29 Oct 2026; ``fixture_use`` rule 4): a basin under a window whose sill is under ``BASIN_SILL_M``: the safe
    default moves it at most 0.5 m to a solid stretch of wall (``clear_basin``), else the window over it becomes a
    bathroom window (``basin_sill``: only where the documents do not give its heights); a farther move is offered for
    the user's OK; ``keep`` leaves it with its mirror beside it (``decor_ai.basin_mirror``)."""
    from wenart.furniture import fixture_use as FU

    got = FU.basin_window(f, openings, plan.walls)
    if got is None:
        _ok(h2, f["id"], "a solid wall over it")
        return
    blocked = AA._door_blocked(plan, f.get("level_id"))
    near = FU.clear_basin(f, room["polygon"], here, openings, plan.walls, blocked=blocked)
    far = None if near else FU.clear_basin(f, room["polygon"], here, openings, plan.walls, blocked=blocked,
                                           max_move=FAR_BASIN_MOVE_M)
    o = plan.openings.get(got["window"]) or {}
    head = min(FU.sill_of(o) + float(o.get("height") if o.get("height") is not None else 1.2), plan.top(o)) if o else 0.0
    raise_ok = bool(o) and AA.heights_given(plan.b, o) is None and head - FU.BASIN_SILL_M >= AA.MIN_WINDOW_H - 1e-9
    opts = []
    if near:
        opts.append(AA.option("clear_basin", f"move {f['id']} {near['moved_m']:.2f} m to a solid stretch of wall",
                              piece_id=f["id"]))
    if raise_ok:
        opts.append(AA.option("basin_sill", f"{got['window']}: a bathroom window over the basin, its sill at "
                                            f"{FU.BASIN_SILL_M:.2f} m", window_id=got["window"]))
    if far:
        opts.append(AA.option("clear_basin", f"move {f['id']} {far['moved_m']:.2f} m to a solid stretch of wall (more "
                                             f"than the {FU.MOVE_MAX_M:.2f} m a drawn fixture may move: your OK)",
                              piece_id=f["id"], max_move_m=round(far["moved_m"] + 0.01, 2)))
    opts.append(AA.option("keep", "keep it under the window; its mirror hangs beside it"))
    chain = [x["choice"] for x in opts if x["id"] in ("clear_basin", "basin_sill") and not x["params"].get("max_move_m")]
    _open(h2, f["id"], f"{f['id']} ({f.get('type')}) stands under window {got['window']} (sill {got['sill_m']:.2f} m "
          f"over {got['share']:.0%} of its width): no mirror over it, its tap against the sill",
          f"Should {f['id']} move to a solid wall, or {got['window']} become a high bathroom window?", opts,
          where=where, **({"default": chain[0], "fallback": chain[1:]} if chain else {}))


def _blocked_chain(plan, piece_id: Optional[str], o: dict, side: dict, door: bool) -> list[dict]:
    """26 Oct 2026 (user: "make the AI architect a lot more smart and let it take decisions more"): the fixes tried
    in turn when the piece in a doorway (``door``) or before a window cannot move: a doorway between two rooms that
    a drawn kitchen run fills becomes a serving window over the counter (``pass_through``); a piece the AI added (not
    from the documents) is left out (``remove_piece``). Drawn pieces are never removed (CLAUDE.md)."""
    piece = next((f for f in plan.b.get("furniture") or [] if f.get("id") == piece_id), None) if piece_id else None
    if piece is None:
        return []
    out = []
    t = str(piece.get("type") or "").lower()
    if door and t in KITCHEN_RUN and side.get("a") and side.get("b") and piece.get("source") == "from_documents":
        out.append(AA.option("pass_through", f"a serving window over {piece_id}: the doorway at counter height",
                             door_id=o["id"]))
    if piece.get("source") not in (None, "from_documents"):
        out.append(AA.option("remove_piece", f"{piece_id} (added by the AI) gives way", piece_id=piece_id))
    return out


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


def grading_rules(prep: dict) -> list[dict]:
    """G2 / G3 (28 Oct 2026; wenart/blender/grading.py): the site's grading and its outdoor floors as the model
    review's M15 measures them on the plan (``grading.review``: G1-G6 for G2, G7 for G3), asked after the access and
    arrival questions have added their steps and paths (``architect.review``). Every finding is an open point with its
    element (the build carries the rules out; an open point says what is still crude); a site measured clean is ok."""
    from wenart.blender import grading as GR

    g2, g3 = (_q(next(r for r in RULES if r["id"] == i)) for i in ("G2", "G3"))
    site = prep.get("site") or {}
    try:
        found, checked = GR.review(site)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        _ok(g2, "site", f"not measured ({type(exc).__name__}: {exc})")
        return [g2, g3]
    for f in found:
        rule = (f.get("metrics") or {}).get("rule")
        if rule == "G13" and f.get("severity") == "minor":
            continue            # 30 Oct 2026 (UL198): a way into a parking that cars do not use, another one works
        if rule == "G15":
            continue            # 31 Oct 2026: the outdoor walk is A6's own question (architect_walk: fixed or open there)
        q = g3 if rule == "G7" else g2
        _open(q, str(f.get("target")), f"{rule}: {f['message']}",
              "Should the site keep this, or should it be graded as the rule asks?", [AA.option("keep")])
    if checked and not any(a.get("open") for a in g2["answers"]):
        _ok(g2, "site", f"{checked} terraces, flights, paths, banks and walls measured: none crude")
    if not any(a.get("open") for a in g3["answers"]):
        _ok(g3, "site", "each outdoor floor has the material of its use")
    return [g2, g3]


def passages_rule(plan: AA.Plan, sides: list[dict]) -> list[dict]:
    """D6 (27 Oct 2026, user: "Not every opening inside the house requires a door or a window"): every doorless gap at
    the floor between two rooms of the house (``GAP_SILL_MAX_M``; the reading found no swing arc and no leaf in it):
    an open passage (ok, logged with its evidence), except an unclear gap (lines in it no rule could read,
    ``door_spacing.unclear_gap``) into a room that needs privacy (``door_spacing.PRIVACY_ROOMS``): a door there by
    default (``gap_to_door``: one solid leaf), or kept open. A clear empty gap stays open whatever the rooms are."""
    from wenart.blender import door_spacing as DS

    d6 = _q(next(r for r in RULES if r["id"] == "D6"))
    for s in sides:
        o = s["opening"]
        if s.get("type") != "opening" or o.get("virtual") or o.get("wall_id") not in plan.walls \
                or float(o.get("sill_height") or 0.0) > GAP_SILL_MAX_M:
            continue                                   # a separator line between two rooms has no wall: no gap
        a, b = plan.room.get(s.get("a")), plan.room.get(s.get("b"))
        if a is None or b is None or AA.Plan.is_outside(a) or AA.Plan.is_outside(b) or a["id"] == b["id"]:
            continue
        private = [r["id"] for r in (a, b) if DS.needs_privacy(r)]
        unclear = DS.unclear_gap(o)
        between = f"between {a['id']} ({_rtype(a) or '?'}) and {b['id']} ({_rtype(b) or '?'})"
        if private and unclear:
            where = _where("opening", o.get("level_id"), o["center"])
            opts = [AA.option("gap_to_door", f"a door for the privacy of {', '.join(private)} (one solid leaf)",
                              door_id=o["id"]), AA.option("keep", "an open passage as drawn")]
            _open(d6, o["id"], f"{o['id']} is a gap {between} with lines no rule could read and no swing arc; "
                  f"{', '.join(private)} needs privacy", f"Does {o['id']} need a door for the privacy of "
                  f"{', '.join(private)}, or is it an open passage?", opts, where=where, default=opts[0]["choice"])
        else:
            why = "an empty gap: no leaf, no swing arc" if not unclear else "no leaf or swing arc read"
            _ok(d6, o["id"], f"an open passage {between} ({why}" + (f"; drawn open into {', '.join(private)}"
                                                                    if private else "; no room needs privacy") + ")")
    return [d6]


def clash_rule(building: dict, clashes: Optional[dict]) -> list[dict]:
    """F5 from ``clashes.resolve`` (``build.prepare`` ran it): every piece checked, the ones moved or not built,
    the clashes left."""
    from wenart.blender import clashes as CL

    f5 = _q(next(r for r in RULES if r["id"] == "F5"))
    if clashes is None:
        clashes = CL.resolve(building)
    done = {}
    for x in clashes.get("fixed") or []:
        for m in x.get("members") or [x["id"]]:
            done.setdefault(m, x)
    left = {}
    for x in clashes.get("left") or []:
        left.setdefault(x["id"], x)
        left.setdefault(x["other"], x)
    legs = {x["id"]: x for x in clashes.get("legs") or []}          # UL178: seats left in a table's corner legs
    for f in building.get("furniture") or []:
        if str(f.get("type") or "") in CL.SKIP_TYPES + CL.FLOOR_ONLY or not f.get("footprint"):
            continue
        x = done.get(f["id"])
        if f["id"] in legs and f["id"] not in left:
            c = legs[f["id"]]
            _open(f5, f["id"], f"{f['id']} ({f.get('type')}) stands {c['depth_m']:.2f} m into a corner leg of "
                  f"{c['other']}: no leg-free place within the move limits (UL178)",
                  f"Should {f['id']} stand pulled out from {c['other']}, or another place?",
                  [AA.option("keep")], where=_where("furniture", f.get("level_id"), f["footprint"]["center"]))
        elif f["id"] in left:
            c = left[f["id"]]
            other = c["other"] if c["id"] == f["id"] else c["id"]
            _open(f5, f["id"], f"{f['id']} ({f.get('type')}) and {other} still overlap {c['depth_m']:.2f} m: no "
                  f"free place within the move limits", f"Which of {f['id']} and {other} should go?",
                  [AA.option("keep")], where=_where("furniture", f.get("level_id"), f["footprint"]["center"]))
        elif x is not None:
            f5["answers"].append({"element": f["id"], "found": f"{f.get('type')} clashed with {x['other']}",
                                  "change": x["reason"].replace("architect F5: ", ""), "fixed": True})
            f5["status"] = "fixed" if f5["status"] == "ok" else f5["status"]
        elif f.get("build") is not False:
            _ok(f5, f["id"], "clear of the other pieces")
    return [f5]


def review(building: dict, prep: dict, sides: list[dict], graph: dict, starts: list, is_stair, reach) -> list[dict]:
    """Every rule of ``RULES`` on every element it applies to (pure)."""
    plan = AA.Plan(building)
    seen = reach(graph, starts) if starts else set()
    unreached = {r["id"] for r in plan.rooms if r["id"] not in seen and not AA.Plan.is_outside(r)} if starts else set()
    out = rooms_rules(plan) + openings_rules(plan, sides, unreached) + door_types(plan, sides) + \
        tall_windows_rule(plan, prep.get("style_family")) + stair_windows_rule(plan) + walls_rules(plan) + \
        passages_rule(plan, sides) + \
        stairs_rules(plan, graph, starts, is_stair, reach) + furniture_rules(plan, sides) + \
        clash_rule(building, prep.get("clashes"))
    if prep.get("site") is not None:
        out += site_rules(prep)
    out += door_frames_rule(plan, prep.get("style_family")) + walk_in_rule(plan, prep.get("style_family")) + \
        door_states_rule(plan, prep.get("style_family"))
    return out


def door_states_rule(plan: AA.Plan, family: Optional[str]) -> list[dict]:
    """D9 (pure; 29 Oct 2026, UL127): every interior door of a style with a family is open with the safe default
    ``door_state:open`` (the build opens it, ajar where a piece or a wall stops its leaf: ``door_states``); the AI
    architect or the user may set it ajar or close it (``door_state:ajar`` / ``door_state:closed``: its
    ``open_state``); a door already answered is fine with its answer. The entrance and the outside doors stay closed
    by the build's rule (not asked)."""
    d9 = _q(next(r for r in RULES if r["id"] == "D9"))
    if not str(family or "").strip():
        return [d9]
    for o in plan.openings.values():
        if o.get("type") != "door" or plan.walls.get(o.get("wall_id")) is None or o.get("level_id") not in plan.levels:
            continue
        sides = AA.window_sides(plan, o) or [None, None]
        if len(sides) != 2 or any(AA.Plan.is_outside(r) for r in sides):
            continue
        dec = o.get("state_decision") if isinstance(o.get("state_decision"), dict) else None
        if dec is not None and dec.get("by") not in (None, "architect"):
            _ok(d9, o["id"], f"{dec.get('state')} ({dec.get('by')}'s answer)")
            continue
        opts = [AA.option("door_state", "open: the leaf turned open on its swing side (ajar where a piece or a wall "
                                        "stops it)", door_id=o["id"], state="open"),
                AA.option("door_state", "ajar: the leaf a little open", door_id=o["id"], state="ajar"),
                AA.option("door_state", "closed", door_id=o["id"], state="closed")]
        _open(d9, o["id"], f"{o['id']}: an interior door, open by default (UL127)", f"Should {o['id']} stand open?",
              opts, where=_where("door", o.get("level_id"), o.get("center")), default="door_state:open")
    return [d9]


def door_frames_rule(plan: AA.Plan, family: Optional[str]) -> list[dict]:
    """D7 (pure; 29 Oct 2026, UL122): in a style family that may hide its doors' frames (``looks.FRAMELESS_FAMILIES``)
    every inside door is open with the safe default ``door_frames:framed`` (the architect carries it out; the AI
    architect or the user may choose a concealed frameless door, ``door_frames:frameless``); a door already decided is
    fine with its answer. Another family frames every door (not asked)."""
    from wenart.blender import looks as LK

    d7 = _q(next(r for r in RULES if r["id"] == "D7"))
    fam = str(family or "").strip().lower()
    if fam not in LK.FRAMELESS_FAMILIES:
        return [d7]
    for o in plan.openings.values():
        if o.get("type") != "door" or plan.walls.get(o.get("wall_id")) is None or o.get("level_id") not in plan.levels:
            continue
        sides = AA.window_sides(plan, o) or [None, None]
        if any(AA.Plan.is_outside(r) for r in sides):
            continue                                     # the facade face of an outside door has no architrave
        dec = o.get("frame_decision") if isinstance(o.get("frame_decision"), dict) else None
        if dec is not None and dec.get("by") not in (None, "architect"):
            _ok(d7, o["id"], f"{'frameless' if dec.get('frameless') else 'framed'} ({dec.get('by')}'s answer)")
            continue
        opts = [AA.option("door_frames", "framed: a jamb lining, a head and an architrave on its indoor faces",
                          door_id=o["id"], frame="framed"),
                AA.option("door_frames", f"a concealed frameless flush door ({fam} style): no architrave, the frame "
                                         "flush with the wall", door_id=o["id"], frame="frameless")]
        _open(d7, o["id"], f"{o['id']}: an inside door of a {fam} house, framed by default",
              f"Should {o['id']} be framed, or a concealed frameless flush door?", opts,
              where=_where("door", o.get("level_id"), o.get("center")), default="door_frames:framed")
    return [d7]


def walk_in_rule(plan: AA.Plan, family: Optional[str]) -> list[dict]:
    """D8 (pure; 29 Oct 2026, UL120, UL125): every walk-in dressing room (``wardrobe_fronts.walk_in``) is open with
    its family's see-through front as the safe default (``wardrobe_fronts.WALK_IN_FRONTS``: slatted or smoked-glass
    sliding fronts, or open runs; the architect carries it out) and the other fronts, closed ones too, as options; a
    walk-in already answered is fine with its answer."""
    from wenart.blender import wardrobe_fronts as WF

    d8 = _q(next(r for r in RULES if r["id"] == "D8"))
    fam = str(family or "").strip().lower()
    if not fam:
        return [d8]
    for r in plan.rooms:
        if r.get("level_id") not in plan.levels:
            continue
        why = WF.walk_in(plan.b, r)
        if why is None:
            continue
        robes = [f for f in plan.b.get("furniture") or [] if f.get("room_id") == r["id"]
                 and str(f.get("type")) in WF.WARDROBE_TYPES and f.get("build", True) is not False]
        if not robes:
            continue
        ans = r.get("wardrobe_fronts") if isinstance(r.get("wardrobe_fronts"), dict) else None
        if ans is not None and ans.get("by") not in (None, "architect"):
            _ok(d8, r["id"], f"{r['id']}: {WF.FRONT_WHAT.get(ans.get('kind'), ans.get('kind'))} ({ans.get('by')})")
            continue
        default = WF.WALK_IN_FRONTS.get(fam, WF.WALK_IN_DEFAULT)
        opts = [AA.option("wardrobe_fronts", WF.FRONT_WHAT[k] + (" (the family's)" if k == default else ""),
                          room_id=r["id"], kind=k) for k in WF.CHOICES]
        _open(d8, r["id"], f"{r['id']}: a walk-in ({why}), {len(robes)} wardrobe run(s)",
              f"Which fronts should the walk-in {r['id']} have?", opts,
              where=_where("room", r.get("level_id"), _centroid(r["polygon"])), default=f"wardrobe_fronts:{default}")
    return [d8]
