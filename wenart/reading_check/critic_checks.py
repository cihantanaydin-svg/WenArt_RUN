"""RC15's checks 1, 2 and 4 (20 Nov 2026; the user chose options 1, 2 and 4 for the structure stage, option 5 later).

What: three more calls of the vision critic (``critic.py``: the same input set, the same pod job, the same answers file,
the same calibration and trust file), each of which only FINDS problems; none changes the building.

1. ``inventory``: the model sees the plan (image 1) only and lists, as strict JSON, what the drawing holds: the rooms
   with their written labels and a point each, the mirror axis when the plan has mirrored halves, the stairs, the lifts,
   the balconies and terraces, the entrance door and the street side, the walls drawn at an angle, the storey names and
   count written in titles and texts. Code compares that list with the reading (``inventory_findings``): room_missing,
   mirror_twin_missing, stair_missing, lift_missing, balcony_missing, entrance_missing, angled_wall_straight,
   storey_count_differs, each at its point in building metres (``critic.norm_to_metres``).
2. ``compare``: image 2 is drawn like an architect's plan (``draw_arch``: black wall bands, door leaves and swings,
   window symbols, the drawing's own label spelling, no colours, no legend). Code writes short questions from the
   reading (``compare_questions``), one per item, each with a numbered mark at its place on both images: is there a
   room here (in the drawing, in the model), is this wall drawn at an angle and straight in the model, does this exterior
   door above the ground have a balcony or terrace in front in the drawing, is this opening a door, a window or a plain
   opening in the drawing. At most ``COMPARE_MAX`` questions a level, ``COMPARE_CHUNK`` a call. A finding is written only
   where the drawing answer contradicts what the reading has there (code knows the model side); the model's own answer
   about image 2 says whether it read image 2 right (``model_read_right``), which sets the finding's confidence.
3. ``plausibility``: a short text of each floor from building.json (``floor_summary``: rooms with type and area, which
   rooms each door joins, the exterior windows of each room, the entrance, the stair and lift landings); the same model,
   text only, answers ``PLAUSIBILITY_QUESTIONS`` naming element ids. Code keeps an answer only when its ids exist and
   are of the asked class (``plausibility_findings``); ``code_agrees`` says whether the summary's own numbers agree.

Why: the 6 Nov run of the open differences call gave 570 findings, nearly all false (the coloured bars of the model
image were not read as openings; open questions invite guesses). Closed questions about marked places, a plain
architect's drawing and a typed list the code compares itself are measurable kind by kind.

How: ``critic prepare`` adds per level ``facts`` (what the reading has, for the comparison), the compare questions and
the architect image; per reading ``bfacts`` (storeys) and the floor texts (``index["texts"]``). ``critic ask --which
inventory,compare,plausibility`` asks them on the pod. ``critic calibrate`` judges each finding against the known
errors (``known_errors.json``), the synthetic projects' exact truth and the user's marks (``user_marks.json``), writes
precision, recall and false alarms per check and kind to the trust file (``checks``), and the review sheets
(``review_sheets``) on which the user marks findings right or wrong.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Optional

CHECKS = ("inventory", "compare", "plausibility")
CALL_MAX_TOKENS = {"inventory": 3072, "compare": 1536, "plausibility": 2048}   # the longest valid answer + margin
COMPARE_MAX = 48               # questions per level (pod 1: 40 left real10's L-1 windows read as doors unasked)
COMPARE_CHUNK = 16             # questions (numbered marks) per call (pod 1: 20; an entry keeps its own, compare_chunk)
COMPARE_CHUNK_POD1 = 20
COMPARE_CAPS = {"room": 16, "angled": 4, "balcony": 8, "window": 6, "opening": 14}
INVENTORY_MAX_ROOMS = 40
ROOM_REACH_M = 0.4             # a listed room point this near a reading room counts as that room
STAIR_REACH_M = 1.5
LIFT_REACH_M = 1.5
ENTRANCE_REACH_M = 2.5
ANGLE_OFF_DEG = 3.0            # a wall this far off the plan's axes is drawn at an angle
ANGLE_SAME_DEG = 4.0
ANGLED_MIN_M = 1.0
GROUND_UP_M = 0.5
PROBE_M = 0.3
MIRROR_TOL_M = 1.2             # a listed room's mirror place this near a listed room of the same label: a twin pair
OPEN_AIR_TYPES = ("balcony", "terrace", "loggia", "deck", "patio", "courtyard", "roof_terrace", "garden")
HABITABLE_TYPES = ("living", "bedroom", "kitchen", "dining", "study", "office", "kids", "guest", "living_kitchen")
WET_TYPES = ("bathroom", "wc", "shower", "toilet")
LIFT_WORDS = ("asans", "lift", "elevator", "elevat")

INVENTORY_KINDS = ("room_missing", "mirror_twin_missing", "stair_missing", "lift_missing", "balcony_missing",
                   "entrance_missing", "angled_wall_straight", "storey_count_differs", "plan_not_read")
COMPARE_KINDS = ("room_missing", "room_not_in_drawing", "angled_wall_straight", "door_into_air", "balcony_missing",
                 "opening_type_differs", "opening_not_in_drawing", "plan_not_read", "window_missing")
EXTENT_MARGIN_M = 1.0          # a labelled place this far outside the level's walls is another plan, not a room missing
SECOND_LOOK_BELOW = 0.75       # a finding under this confidence gets the short second question (``second_look``)
SECOND_LOOK_MAX = 160          # second questions per pod at most (pod 1 would have had 158)
# (id, kind, element class of the ids, question)
PLAUSIBILITY_QUESTIONS = (
    ("P1", "habitable_no_window", "room",
     "Which habitable rooms (living, bedroom, kitchen, dining, study) have no exterior window and no glazed door to "
     "the outside or to a balcony? Give their room ids."),
    ("P2", "bedroom_through_bathroom", "room",
     "Which bedrooms can be reached only through a bathroom or WC (every door of the bedroom leads into a bathroom or "
     "WC)? Give the bedroom ids."),
    ("P3", "flat_no_entrance", "room",
     "Which flats have no entrance door from the common hall or the stair hall? Give one room id of each such flat "
     "(its hall or living room)."),
    ("P4", "kitchen_no_window", "room",
     "Which kitchens have no exterior window, no door to a balcony and no vent? Give the kitchen ids."),
    ("P5", "lift_door_into_flat", "door",
     "Which lift doors open into a flat's room instead of the common hall or landing? Give the door ids."),
    ("P6", "stair_no_landing_door", "stair",
     "Which stairs have no door or opening from their stair room to a landing or hall? Give the stair ids."),
    ("P7", "storey_no_stair_access", "room",
     "Which rooms of this storey have no way to a stair through doors and openings? Give their room ids; give every "
     "room when the storey has no stair at all; give none when every room reaches a stair."),
    ("P8", "door_into_air", "door",
     "Which exterior doors of this storey, above the ground, have nothing to step onto (no balcony, terrace or roof "
     "in front)? Give the door ids."),
    ("P9", "balcony_no_door", "outdoor",
     "Which balconies or terraces have no door from a room? Give their ids."),
)
PLAUSIBILITY_KINDS = tuple(q[1] for q in PLAUSIBILITY_QUESTIONS)
KINDS_BY_CHECK = {"inventory": INVENTORY_KINDS, "compare": COMPARE_KINDS, "plausibility": PLAUSIBILITY_KINDS}
KIND_TEXT = {
    "room_missing": "a room the drawing has (a labelled place) and the reading lacks",
    "mirror_twin_missing": "one half of a mirrored pair of rooms the reading lacks",
    "stair_missing": "a drawn stair the reading lacks",
    "lift_missing": "a drawn lift the reading lacks",
    "balcony_missing": "a drawn balcony or terrace the reading lacks",
    "entrance_missing": "the drawn entrance door the reading lacks",
    "angled_wall_straight": "a wall drawn at an angle that the reading builds straight or leaves out",
    "storey_count_differs": "the storey count written in the drawing differs from the reading's",
    "room_not_in_drawing": "a room of the reading where the drawing has none",
    "door_into_air": "an exterior door above the ground with nothing to step onto",
    "opening_type_differs": "an opening read as another type (door, window, plain opening) than drawn",
    "opening_not_in_drawing": "an opening of the reading where the drawing has none",
    "habitable_no_window": "a habitable room with no window",
    "bedroom_through_bathroom": "a bedroom reachable only through a bathroom",
    "flat_no_entrance": "a flat with no entrance door from the common hall",
    "kitchen_no_window": "a kitchen with no window or vent",
    "lift_door_into_flat": "a lift door into a flat",
    "stair_no_landing_door": "a stair with no landing door",
    "storey_no_stair_access": "a storey with no way to the stair",
    "balcony_no_door": "a balcony with no door",
    "plan_not_read": "a labelled plan outside the level's walls: a plan (a level) the reading did not read",
    "window_missing": "a window or door the drawing has in an outer wall of a habitable room and the reading lacks",
}
# How a finding of a kind is judged against a synthetic project's exact truth (``critic.judge``'s classes and sides)
JUDGE_RULES = {
    "room_missing": (("rooms",), ("truth_only",)),
    "mirror_twin_missing": (("rooms",), ("truth_only",)),
    "stair_missing": (("stairs",), ("truth_only",)),
    "lift_missing": (("rooms",), ("truth_only",)),
    "balcony_missing": (("rooms",), ("truth_only",)),
    "entrance_missing": (("doors", "openings"), ("truth_only",)),
    "angled_wall_straight": (("walls",), ("truth_only",)),
    "room_not_in_drawing": (("rooms",), ("read_only",)),
    # 20 Nov 2026 (pod 1): a door the truth lacks, or the outdoor room in front of it the reading lacks (walls were too
    # broad: any wall disagreement near a door counted)
    "door_into_air": (("doors", "rooms"), ("read_only", "truth_only")),
    "opening_type_differs": (("doors", "windows", "openings"), ("truth_only", "read_only")),
    "opening_not_in_drawing": (("doors", "windows", "openings"), ("read_only",)),
    "window_missing": (("windows", "doors"), ("truth_only",)),
    "habitable_no_window": (("windows",), ("truth_only",)),
    "bedroom_through_bathroom": (("doors", "openings"), ("truth_only", "read_only")),
    "flat_no_entrance": (("doors", "openings"), ("truth_only",)),
    "kitchen_no_window": (("windows",), ("truth_only",)),
    "lift_door_into_flat": (("doors", "openings"), ("read_only",)),
    "stair_no_landing_door": (("doors", "openings", "stairs"), ("truth_only",)),
    "storey_no_stair_access": (("doors", "openings", "stairs"), ("truth_only",)),
    "balcony_no_door": (("doors", "rooms"), ("truth_only", "read_only")),
}
SYSTEM_TEXT = ("You are a senior architect checking a computer's reading of an architectural floor plan. You answer "
               "only with the JSON the schema asks for. You point only at what you can see.")


# ============================================================================================ 1. facts of a reading
def _poly(points):
    from shapely.geometry import Polygon

    p = Polygon([tuple(q[:2]) for q in points])
    return p if p.is_valid else p.buffer(0)


def _rep(points) -> list:
    p = _poly(points).representative_point()
    return [round(p.x, 3), round(p.y, 3)]


def _r(p) -> list:
    return [round(float(p[0]), 3), round(float(p[1]), 3)]


def _deg(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def axis_deg(walls: list) -> float:
    """The plan's main direction (degrees mod 90): the angle bin holding the most wall length."""
    bins: dict = {}
    for w in walls:
        if not (w.get("start") and w.get("end")):
            continue
        k = int(round(_deg(w["start"], w["end"]))) % 90
        bins[k] = bins.get(k, 0.0) + math.dist(w["start"], w["end"])
    return float(max(bins, key=bins.get)) if bins else 0.0


def off_axis(ang: float, axis: float) -> float:
    d = (ang - axis) % 90.0
    return min(d, 90.0 - d)


def is_lift(room: dict) -> bool:
    t = f"{room.get('room_type') or ''} {room.get('room_subtype') or ''}".lower()
    lab = str(room.get("label") or "").lower()
    return "lift" in t or "elevator" in t or any(w in lab for w in LIFT_WORDS)


def _ground(levels: list) -> float:
    zero = [lv for lv in levels if lv.get("order") == 0]
    up = [lv for lv in levels if float(lv.get("elevation") or 0.0) >= -0.5]
    pick = zero or up or levels
    return float(pick[0].get("elevation") or 0.0) if pick else 0.0


def building_facts(building: dict) -> dict:
    """The reading's storeys (base variant), their labels and the ground floor's elevation (pure)."""
    levels = sorted((lv for lv in building.get("levels") or [] if lv.get("id")
                     and lv.get("variant") in (None, "base")), key=lambda lv: float(lv.get("elevation") or 0.0))
    roofs = [lv for lv in levels if lv.get("kind") in ("roof", "roof_terrace") or lv.get("roof_terrace")]
    return {"storeys": len(levels), "storeys_without_roof": len(levels) - len(roofs), "ground": _ground(levels),
            "levels": [{"id": lv["id"], "label": lv.get("label"), "elevation": lv.get("elevation"),
                        "typical_of": lv.get("typical_of"), "kind": lv.get("kind")}
                       for lv in levels]}


def _spaces(building: dict, lid: str) -> tuple:
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid and len(r.get("polygon") or []) >= 3]
    outdoor = [s for s in (building.get("site") or {}).get("outdoor_spaces") or []
               if isinstance(s, dict) and s.get("level_id") == lid and len(s.get("polygon") or []) >= 3]
    return rooms, outdoor


def _side_points(o: dict, w: dict) -> Optional[tuple]:
    c = o.get("center")
    if not (w and isinstance(c, (list, tuple)) and len(c) >= 2):
        return None
    (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
    n = math.hypot(x1 - x0, y1 - y0)
    if n <= 1e-9:
        return None
    nx, ny = -(y1 - y0) / n, (x1 - x0) / n
    reach = float(w.get("thickness") or 0.2) / 2.0 + PROBE_M
    return (c[0] + nx * reach, c[1] + ny * reach), (c[0] - nx * reach, c[1] - ny * reach)


def _where(p, rooms_p: list, outdoor_p: list, outline) -> str:
    """The id of the room or outdoor space at ``p``, else ``outside`` (out of the level's outline) or ``unknown``."""
    from shapely.geometry import Point

    pt = Point(p)
    for rid, poly in rooms_p:
        if poly.contains(pt):
            return rid
    for sid, poly in outdoor_p:
        if poly.buffer(0.05).contains(pt):
            return sid
    if outline is not None and not outline.contains(pt):
        return "outside"
    return "unknown"


def level_facts(building: dict, lid: str, *, outline=None, below=None, page=None, tf=None) -> dict:
    """What the reading has on level ``lid`` (pure but for the page): rooms and outdoor spaces with their polygons and
    a point each, the stairs, the lifts, every opening with the two spaces it joins, the entrances, the walls at an
    angle; with ``page``/``tf`` also the drawing's room labels and the drawn wall strokes at an angle (metres)."""
    from shapely.geometry import Point

    levels = sorted((lv for lv in building.get("levels") or [] if lv.get("id")),
                    key=lambda lv: float(lv.get("elevation") or 0.0))
    lv = next((x for x in levels if x["id"] == lid), {})
    ground = _ground([x for x in levels if x.get("variant") in (None, "base")] or levels)
    rooms, outdoor = _spaces(building, lid)
    rooms_p = [(r["id"], _poly(r["polygon"])) for r in rooms]
    outdoor_p = [(s["id"], _poly(s["polygon"])) for s in outdoor]
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == lid and w.get("start")
             and w.get("end")}
    ax = axis_deg(list(walls.values()))
    out = {"level": lid, "label": lv.get("label"), "elevation": lv.get("elevation"),
           "above_ground": float(lv.get("elevation") or 0.0) > ground + GROUND_UP_M, "axis_deg": ax,
           "extent": wall_extent(list(walls.values())), "mirror": mirror_facts(list(walls.values()))}
    out["rooms"] = [{"id": r["id"], "label": r.get("label_raw") or r.get("label"), "type": r.get("room_type"),
                     "subtype": r.get("room_subtype"), "at": _rep(r["polygon"]),
                     "area": round(float(r.get("area_computed") or _poly(r["polygon"]).area), 1),
                     "poly": [_r(q) for q in r["polygon"]], "twin_of": r.get("twin_of"),
                     "open_air": str(r.get("room_type") or "") in OPEN_AIR_TYPES} for r in rooms]
    out["outdoor"] = [{"id": s["id"], "label": s.get("label"), "kind": s.get("kind"), "at": _rep(s["polygon"]),
                       "area": round(_poly(s["polygon"]).area, 1), "poly": [_r(q) for q in s["polygon"]]}
                      for s in outdoor]
    stairs = []
    for f in building.get("furniture") or []:
        if f.get("level_id") == lid and f.get("type") == "stair" and (f.get("footprint") or {}).get("center"):
            stairs.append({"id": f["id"], "at": _r(f["footprint"]["center"]), "room_id": f.get("room_id")})
    for r in rooms:
        if r.get("room_type") == "stair" and not any(s.get("room_id") == r["id"] for s in stairs):
            stairs.append({"id": r["id"], "at": _rep(r["polygon"]), "room_id": r["id"]})
    out["stairs"] = stairs
    out["lifts"] = [{"id": r["id"], "at": _rep(r["polygon"])} for r in rooms if is_lift(r)]
    ops = []
    for o in building.get("openings") or []:
        if o.get("level_id") != lid or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        sides = _side_points(o, w) if w else None
        if sides is None:
            # 20 Nov 2026 (pod 1: 'o_r_L4_oda_4_hall ... unknown <-> unknown', so the stair room had no listed link):
            # an opening with no wall of its own (a passage between two rooms) joins the two spaces nearest to it
            sides = _free_sides(o, rooms_p, outdoor_p)
        a = _where(sides[0], rooms_p, outdoor_p, outline) if sides else "unknown"
        b = _where(sides[1], rooms_p, outdoor_p, outline) if sides else "unknown"
        exterior = bool(w and w.get("exterior")) or "outside" in (a, b) or \
            any(x in {s["id"] for s in outdoor} for x in (a, b))
        front = None
        if sides and exterior and out["above_ground"]:
            p = sides[0] if a in ("outside", "unknown") or a.startswith("os_") or a in {s["id"] for s in outdoor} \
                else sides[1]
            air = [poly for _sid, poly in outdoor_p] + [poly for rid, poly in rooms_p
                                                        if any(r["id"] == rid and r.get("room_type") in OPEN_AIR_TYPES
                                                               for r in rooms)]
            front = "open_air" if any(g.buffer(0.05).contains(Point(p)) for g in air) else \
                ("roof_below" if below is not None and below.contains(Point(p)) else "nothing")
        ops.append({"id": o["id"], "type": o.get("type") or "opening", "at": _r(o["center"]),
                    "width": round(float(o.get("width") or 0.0), 2), "exterior": exterior, "sides": [a, b],
                    "front": front, "wall_deg": round(_deg(w["start"], w["end"]), 1) if w else None,
                    "inferred": bool(o.get("inferred")) or any(isinstance(e, dict) and e.get("method") == "inferred"
                                                               for e in o.get("evidence") or [])})
    out["openings"] = ops
    out["entrances"] = [{"door_id": e.get("door_id"), "at": _r(e.get("centre") or e.get("face") or [0, 0]),
                         "main": bool(e.get("main"))}
                        for e in (building.get("site") or {}).get("entrances") or []
                        if isinstance(e, dict) and e.get("level_id") == lid and not e.get("into_air")
                        and (e.get("main") or not e.get("upper_floor"))]
    out["angled_walls"] = [{"id": w["id"], "a": _r(w["start"]), "b": _r(w["end"]), "deg": round(_deg(w["start"], w["end"]), 1)}
                           for w in walls.values() if off_axis(_deg(w["start"], w["end"]), ax) > ANGLE_OFF_DEG
                           and math.dist(w["start"], w["end"]) >= ANGLED_MIN_M]
    out["drawn_labels"], out["drawn_angled"] = [], []
    if page is not None and tf is not None:
        out["drawn_labels"] = drawn_labels(page, tf)
        out["drawn_angled"] = drawn_angled(page, tf, list(walls.values()), ax)
    out["window_places"] = window_places(out, outline)
    return out


def _free_sides(o: dict, rooms_p: list, outdoor_p: list) -> Optional[tuple]:
    """Two probe points across an opening with no wall: along its ``line``'s normal, else the two directions that
    land in two different spaces (pure but for shapely)."""
    from shapely.geometry import Point

    c = o["center"][:2]
    line = o.get("line") if isinstance(o.get("line"), (list, tuple)) and len(o.get("line") or []) >= 2 else None
    dirs = []
    if line and math.dist(line[0][:2], line[1][:2]) > 1e-6:
        (x0, y0), (x1, y1) = line[0][:2], line[1][:2]
        n = math.dist((x0, y0), (x1, y1))
        dirs = [(-(y1 - y0) / n, (x1 - x0) / n)]
    dirs += [(1.0, 0.0), (0.0, 1.0)]
    spaces = rooms_p + outdoor_p
    for dx, dy in dirs:
        for reach in (0.4, 0.8):
            p, q = (c[0] + dx * reach, c[1] + dy * reach), (c[0] - dx * reach, c[1] - dy * reach)
            sp = next((i for i, g in spaces if g.contains(Point(p))), None)
            sq = next((i for i, g in spaces if g.contains(Point(q))), None)
            if sp and sq and sp != sq:
                return p, q
    return None


def window_places(facts: dict, outline=None) -> list:
    """Per habitable room the reading gives no exterior window or door: the middle of its longest edge on the level's
    outline (``[{room_id, at, length}]``, pure but for shapely): where the compare check asks whether the drawing has a
    window (real10's kitchens: the drawn window frames were not read)."""
    from shapely.geometry import Point

    lit = {}
    outdoor = {s["id"] for s in facts.get("outdoor") or []}
    for o in facts.get("openings") or []:
        a, b = o.get("sides") or ["unknown", "unknown"]
        for x, y in ((a, b), (b, a)):
            if o.get("exterior") and (y in ("outside", "unknown") or y in outdoor):
                lit[x] = lit.get(x, 0) + 1
    out = []
    for r in facts.get("rooms") or []:
        if r.get("type") not in HABITABLE_TYPES or lit.get(r["id"]):
            continue
        best = None
        pts = r["poly"]
        for p0, p1 in zip(pts, pts[1:] + pts[:1]):
            L = math.dist(p0, p1)
            if L < 1.0:
                continue
            mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
            nx, ny = -(p1[1] - p0[1]) / L, (p1[0] - p0[0]) / L
            for s in (1.0, -1.0):
                probe = (mx + nx * s * 0.6, my + ny * s * 0.6)
                inside_room = _contains(pts, (mx - nx * s * 0.3, my - ny * s * 0.3))
                if not inside_room:
                    continue
                out_of = outline is not None and not outline.contains(Point(probe))
                if (out_of or any(_contains(sp["poly"], probe) for sp in facts.get("outdoor") or [])) and \
                        (best is None or L > best[2]):
                    # the mark 0.25 m inside the room, so a frame drawn tight to the facade still shows it
                    best = ([round(mx - nx * s * 0.25, 3), round(my - ny * s * 0.25, 3)], r["id"], L)
        if best:
            out.append({"room_id": best[1], "at": best[0], "length": round(best[2], 2)})
    return out


MIRROR_MIN_SCORE = 0.7         # the reading's walls this symmetric about an axis before a mirror finding is written


def mirror_facts(walls: list) -> dict:
    """``{"x": {axis, score}, "y": {axis, score}}`` (pure): for a mirror line of constant x (and of constant y), the
    position near the middle of the walls where the most wall end points have a wall end point at their mirror place
    (within 0.3 m), and that share. 20 Nov 2026 (pod 1): the model answered 'vertical, 500' for nearly every plan;
    the mirror findings need the reading's own symmetry (real09: 0.89, real20: low)."""
    pts = [tuple(w[k][:2]) for w in walls for k in ("start", "end") if w.get(k)]
    out = {}
    if len(pts) < 8:
        return out
    cell = 0.3
    grid: dict = {}
    for p in pts:
        grid.setdefault((round(p[0] / cell), round(p[1] / cell)), []).append(p)

    def near(q):
        gx, gy = round(q[0] / cell), round(q[1] / cell)
        return any(math.dist(q, p) <= 0.3 for dx in (-1, 0, 1) for dy in (-1, 0, 1) for p in grid.get((gx + dx, gy + dy), ()))

    for ax_name, i in (("x", 0), ("y", 1)):
        lo, hi = min(p[i] for p in pts), max(p[i] for p in pts)
        mid = (lo + hi) / 2.0
        scores = []
        for k in range(-30, 31):
            a = mid + k * 0.05
            hit = sum(1 for p in pts if near((2 * a - p[0], p[1]) if i == 0 else (p[0], 2 * a - p[1])))
            scores.append((hit / len(pts), a))
        top = max(s for s, _a in scores)
        tied = [a for s, a in scores if s == top]
        out[ax_name] = {"axis": round(tied[len(tied) // 2], 3), "score": round(top, 3)}   # the middle of the tie
    return out


def wall_extent(walls: list) -> Optional[list]:
    """``[min x, min y, max x, max y]`` of a level's walls (metres), or None."""
    pts = [w[k][:2] for w in walls for k in ("start", "end") if w.get(k)]
    if not pts:
        return None
    return [round(min(p[0] for p in pts), 3), round(min(p[1] for p in pts), 3), round(max(p[0] for p in pts), 3),
            round(max(p[1] for p in pts), 3)]


def drawn_labels(page, tf) -> list:
    """The drawing's room labels (``labels.merge_label_blocks``), each with its point in building metres."""
    from wenart import reading_check as RC
    from wenart.ingest.generic import labels as LB

    try:
        blocks = LB.merge_label_blocks(RC._runs(page.texts))
    except Exception:  # noqa: BLE001 - texts the label reader cannot take: no labels
        return []
    out = []
    for b in blocks:
        name = str(getattr(b, "name", "") or "").strip()
        if not name or getattr(b, "anchor", None) is None:
            continue
        p = RC._apply(tf, b.anchor)
        try:
            rtype, ext = LB.room_type_for(name)
        except Exception:  # noqa: BLE001 - a name the vocabulary cannot type
            rtype, ext = None, False
        out.append({"text": name[:40], "at": _r(p), "type": rtype,
                    "exterior": bool(getattr(b, "exterior", False)) or ext or rtype in OPEN_AIR_TYPES})
    return out


def drawn_angled(page, tf, walls: list, ax: float) -> list:
    """The drawing's wall strokes at an angle off the plan's axes (metres), joined when collinear and touching."""
    from wenart import reading_check as RC

    segs = RC.drawn_wall_segments(page, tf, RC.model_wall_layers(walls))
    out = []
    for a, b in segs:
        if math.dist(a, b) < ANGLED_MIN_M:
            continue
        ang = _deg(a, b)
        if off_axis(ang, ax) <= ANGLE_OFF_DEG:
            continue
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        if any(abs((ang - s["deg"] + 90) % 180 - 90) < ANGLE_SAME_DEG and math.dist(mid, s["mid"]) < 1.0 for s in out):
            continue                                            # the other face of the same wall
        out.append({"a": _r(a), "b": _r(b), "mid": _r(mid), "deg": round(ang, 1), "length": round(math.dist(a, b), 2)})
    return out


def follows_angled(seg: dict, walls_or_facts: list) -> bool:
    """Whether a model wall at the stroke's angle lies along it (within 0.5 m of its middle)."""
    mid = seg.get("mid") or [(seg["a"][0] + seg["b"][0]) / 2.0, (seg["a"][1] + seg["b"][1]) / 2.0]
    for w in walls_or_facts:
        a, b = (w.get("a"), w.get("b")) if "a" in w else (w.get("start"), w.get("end"))
        if not (a and b):
            continue
        d = abs((_deg(a, b) - seg["deg"] + 90) % 180 - 90)
        if d <= ANGLE_SAME_DEG and _seg_dist(mid, a, b) <= 0.5:
            return True
    return False


def _seg_dist(p, a, b) -> float:
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    dx, dy = bx - ax, by - ay
    n = dx * dx + dy * dy
    t = 0.0 if n <= 1e-12 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / n))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _contains(poly_pts: list, p, reach: float = 0.0) -> bool:
    from shapely.geometry import Point

    g = _poly(poly_pts)
    return g.contains(Point(p)) or (reach > 0 and g.distance(Point(p)) <= reach)


def room_at(facts: dict, p, reach: float = ROOM_REACH_M, outdoor: bool = False) -> Optional[dict]:
    """The reading's room (or, with ``outdoor``, also outdoor space) at ``p`` (metres), within ``reach``."""
    items = list(facts.get("rooms") or []) + (list(facts.get("outdoor") or []) if outdoor else [])
    for r in items:
        if _contains(r["poly"], p):
            return r
    best = None
    for r in items:
        d = _poly(r["poly"]).distance(__import__("shapely.geometry", fromlist=["Point"]).Point(p))
        if d <= reach and (best is None or d < best[0]):
            best = (d, r)
    return best[1] if best else None


# ================================================================================================= 2. inventory
def inventory_prompt(entry: dict) -> str:
    # 20 Nov 2026 (pod 1): the drawing's own room labels as a list (the model listed 6 of real09's 8), the storey
    # texts of the whole drawing file (real03's '1BK+ZK+12K' is in a block, not in the plan image), and what an angled
    # wall looks like (real20's slanted street facade was not listed)
    labels = sorted({str(x.get("text") or "").strip() for x in (entry.get("facts") or {}).get("drawn_labels") or []
                     if str(x.get("text") or "").strip()})[:40]
    storeys = [str(t)[:50] for t in entry.get("storey_texts") or []][:25]
    extra = ""
    if labels:
        extra += f"The drawing's room labels, as written in it: {'; '.join(labels)}.\n"
    if storeys:
        extra += (f"Texts of the drawing file that name storeys (titles, notes, blocks): {'; '.join(storeys)}. In Turkish "
                  f"notation BK is a basement, ZK the ground floor, 'nK' n upper floors.\n")
    return (f"The image is an architect's floor plan ({entry.get('title') or 'a level of a building'}). {extra}"
            f"List what the drawing holds, as an architect reading it would:\n"
            f"- rooms: every labelled room or space with its written label exactly as written and a point inside it;\n"
            f"- mirror: whether the plan has two mirrored halves (two flats mirrored about a line); the axis (vertical "
            f"or horizontal line) and its position;\n"
            f"- stairs and lifts: a point on each;\n"
            f"- balconies and terraces: a point on each;\n"
            f"- entrance: the building's entrance door, if this plan shows it, and the side of the street;\n"
            f"- angled walls: each wall drawn at an angle to the image's edges (a slanted facade along a street, a "
            f"corner cut at 45 degrees), by its two end points;\n"
            f"- storeys: the storey names written in titles and texts, and the number of storeys of the building when "
            f"a text says it (0 when no text says it).\n"
            f"Points are x and y in 0-1000 (0,0 the top-left corner, 1000,1000 the bottom-right corner). List only "
            f"what is drawn; leave a list empty when the drawing has none.")


STOREY_WORDS = re.compile(r"(\bKAT\b|KATI\b|BODRUM|ZEMIN|NORMAL|CATI|ASMA|\bB\.?K\b|\bZ\.?K\b|\b\d+\s*N?\.?\s*K\b|"
                          r"STOREY|FLOOR)", re.I)
STOREY_NOT = re.compile(r"(HOL|MERDIVEN|PLAN[I]? OLCEK|ASANSOR|KOT)", re.I)


def storey_texts(doc) -> list:
    """The texts of a DXF document (model space, every block, attributes) that name storeys, folded and deduplicated
    (at most 25, pure but for ezdxf): what the inventory reads the storey count from."""
    from wenart.textfold import fold_ascii

    out: list = []
    seen: set = set()

    def take(s):
        s = re.sub(r"\\[A-Za-z][^;]*;|[{}]", "", str(s or "")).strip()
        f = fold_ascii(s).upper()
        if not s or len(s) > 60 or not STOREY_WORDS.search(f) or STOREY_NOT.search(f) or f in seen:
            return
        seen.add(f)
        out.append(s)

    layouts = [doc.modelspace()] + [b for b in doc.blocks if not b.name.startswith("*")]
    for lay in layouts:
        for e in lay:
            t = e.dxftype()
            if t in ("TEXT", "ATTRIB", "ATTDEF"):
                take(e.dxf.text)
            elif t == "MTEXT":
                take(e.text)
            elif t == "INSERT":
                for a in getattr(e, "attribs", []) or []:
                    take(a.dxf.text)
            if len(out) >= 25:
                return out
    return out


def _pt_schema() -> dict:
    return {"x": {"type": "integer", "minimum": 0, "maximum": 1000}, "y": {"type": "integer", "minimum": 0, "maximum": 1000}}


def _obj(props: dict, required: Optional[list] = None) -> dict:
    return {"type": "object", "properties": props, "required": list(required or props.keys()),
            "additionalProperties": False}


INVENTORY_SCHEMA = _obj({
    "rooms": {"type": "array", "maxItems": INVENTORY_MAX_ROOMS,
              "items": _obj(dict({"label": {"type": "string", "maxLength": 40}}, **_pt_schema()))},
    "mirror": _obj({"axis": {"type": "string", "enum": ["none", "vertical", "horizontal"]},
                    "position": {"type": "integer", "minimum": 0, "maximum": 1000}}),
    "stairs": {"type": "array", "maxItems": 6, "items": _obj(_pt_schema())},
    "lifts": {"type": "array", "maxItems": 6, "items": _obj(_pt_schema())},
    "balconies": {"type": "array", "maxItems": 16,
                  "items": _obj(dict({"kind": {"type": "string", "enum": ["balcony", "terrace"]}}, **_pt_schema()))},
    "entrance": _obj(dict({"shown": {"type": "boolean"},
                           "street_side": {"type": "string", "enum": ["top", "bottom", "left", "right", "unknown"]}},
                          **_pt_schema())),
    "angled_walls": {"type": "array", "maxItems": 8,
                     "items": _obj({"x0": {"type": "integer", "minimum": 0, "maximum": 1000},
                                    "y0": {"type": "integer", "minimum": 0, "maximum": 1000},
                                    "x1": {"type": "integer", "minimum": 0, "maximum": 1000},
                                    "y1": {"type": "integer", "minimum": 0, "maximum": 1000}})},
    "storeys": _obj({"names": {"type": "array", "maxItems": 20, "items": {"type": "string", "maxLength": 40}},
                     "count": {"type": "integer", "minimum": 0, "maximum": 80}}),
})


def _m(entry: dict, x, y) -> list:
    from wenart.reading_check.critic import norm_to_metres

    return _r(norm_to_metres(float(x) / 1000.0, float(y) / 1000.0, entry["box"], entry["tf"]))


def _norm_label(s) -> str:
    from wenart.textfold import fold_ascii as fold

    return re.sub(r"[^a-z0-9]+", " ", fold(str(s or "")).lower()).strip()


def inventory_findings(data: dict, entry: dict, facts: dict, bfacts: Optional[dict] = None) -> list:
    """The inventory against the reading (pure): ``[{key, kind, at, point, description, confidence, element_ids}]``.
    A listed room whose point lies in no reading room (``room_missing``); of a listed pair mirrored about the listed
    axis, a half the reading lacks (``mirror_twin_missing``, instead of room_missing); a listed stair, lift, balcony,
    entrance with no reading one near; a listed angled wall no model wall follows; a written storey count the
    reading's storeys do not match."""
    out: list = []
    rooms = [dict(r, at=_m(entry, r["x"], r["y"]), point=[r["x"] / 1000.0, r["y"] / 1000.0])
             for r in data.get("rooms") or [] if isinstance(r, dict)]
    mirror = data.get("mirror") or {}
    twin_keys: set = set()
    pos = _code_mirror(entry, facts, mirror.get("axis"))
    if pos is not None:
        for i, r in enumerate(rooms):
            mx, my = (2 * pos - r["x"], r["y"]) if mirror["axis"] == "vertical" else (r["x"], 2 * pos - r["y"])
            if not (0 <= mx <= 1000 and 0 <= my <= 1000):
                continue
            mat = _m(entry, mx, my)
            twin = next((j for j, s in enumerate(rooms) if j != i and _norm_label(s["label"]) == _norm_label(r["label"])
                         and math.dist(s["at"], mat) <= MIRROR_TOL_M), None)
            if twin is None:
                # a drawing that labels one half only (real09): the reading has this room and nothing at its mirror
                # place inside the reading's extent: the mirrored half's room is missing
                here = room_at(facts, r["at"])
                if here is not None and room_at(facts, mat, outdoor=True) is None and _inside_extent(facts, mat) \
                        and not any(f["kind"] == "mirror_twin_missing" and math.dist(f["at"], mat) < 1.0 for f in out):
                    out.append({"kind": "mirror_twin_missing", "at": mat, "point": [mx / 1000.0, my / 1000.0],
                                "description": f"the plan mirrors about the {mirror['axis']} axis; '{r['label']}' "
                                               f"({here['id']}) has no twin in the reading at its mirror place",
                                "element_ids": [here["id"]], "confidence": 0.6})
                continue
            twin_keys.add(i)
            if room_at(facts, r["at"]) is None and room_at(facts, rooms[twin]["at"]) is not None:
                out.append({"kind": "mirror_twin_missing", "at": r["at"], "point": r["point"],
                            "description": f"'{r['label']}' mirrors '{rooms[twin]['label']}' about the "
                                           f"{mirror['axis']} axis; the reading has the twin but not this one",
                            "element_ids": [room_at(facts, rooms[twin]["at"])["id"]], "confidence": 0.75})
    for i, r in enumerate(rooms):
        if i in twin_keys and any(f["kind"] == "mirror_twin_missing" and f["at"] == r["at"] for f in out):
            continue
        if room_at(facts, r["at"], outdoor=True) is None:
            d = _nearest(facts.get("rooms") or [], r["at"])
            out.append({"kind": "room_missing", "at": r["at"], "point": r["point"],
                        "description": f"the drawing labels '{r['label']}' here; the reading has no room there"
                                       + (f" (nearest room {d[0]:.1f} m away)" if d else ""),
                        "element_ids": [], "confidence": round(min(0.95, 0.5 + (d[0] if d else 3.0) / 6.0), 2)})
    for kind, listed, have, reach, word in (
            ("stair_missing", data.get("stairs"), facts.get("stairs"), STAIR_REACH_M, "stair"),
            ("lift_missing", data.get("lifts"), facts.get("lifts"), LIFT_REACH_M, "lift")):
        for s in listed or []:
            at = _m(entry, s["x"], s["y"])
            near = [h for h in have or [] if math.dist(h["at"], at) <= reach]
            if not near and not (kind == "lift_missing" and _room_type_at(facts, at, ("shaft",))):
                out.append({"kind": kind, "at": at, "point": [s["x"] / 1000.0, s["y"] / 1000.0],
                            "description": f"the drawing has a {word} here; the reading has none within {reach:g} m",
                            "element_ids": [], "confidence": 0.7})
    for s in data.get("balconies") or []:
        at = _m(entry, s["x"], s["y"])
        osp = room_at({"rooms": facts.get("outdoor") or []}, at, reach=0.6)
        open_room = next((r for r in facts.get("rooms") or [] if r.get("open_air") and _contains(r["poly"], at, 0.6)),
                         None)
        if osp is None and open_room is None:
            inside = room_at(facts, at, reach=0.0)
            out.append({"kind": "balcony_missing", "at": at, "point": [s["x"] / 1000.0, s["y"] / 1000.0],
                        "description": f"the drawing has a {s.get('kind') or 'balcony'} here; the reading has "
                                       + (f"room {inside['id']} ({inside.get('label')}) there" if inside else
                                          "no outdoor space there"),
                        "element_ids": [inside["id"]] if inside else [], "confidence": 0.7})
    ent = data.get("entrance") or {}
    if ent.get("shown"):
        at = _m(entry, ent.get("x", 0), ent.get("y", 0))
        doors = [e for e in facts.get("entrances") or []] + \
                [{"door_id": o["id"], "at": o["at"]} for o in facts.get("openings") or []
                 if o.get("exterior") and o.get("type") in ("door", "opening")]
        if not any(math.dist(d["at"], at) <= ENTRANCE_REACH_M for d in doors):
            out.append({"kind": "entrance_missing", "at": at, "point": [ent.get("x", 0) / 1000.0, ent.get("y", 0) / 1000.0],
                        "description": f"the drawing's entrance door (street side {ent.get('street_side')}); the "
                                       f"reading has no exterior door within {ENTRANCE_REACH_M:g} m",
                        "element_ids": [], "confidence": 0.7})
    walls_m = facts.get("angled_walls") or []
    for s in data.get("angled_walls") or []:
        a, b = _m(entry, s["x0"], s["y0"]), _m(entry, s["x1"], s["y1"])
        if math.dist(a, b) < ANGLED_MIN_M:
            continue
        seg = {"a": a, "b": b, "deg": _deg(a, b)}
        if off_axis(seg["deg"], float(facts.get("axis_deg") or 0.0)) <= ANGLE_OFF_DEG:
            continue                                            # not at an angle in the plan's frame
        if not follows_angled(seg, walls_m):
            mid = [round((a[0] + b[0]) / 2, 3), round((a[1] + b[1]) / 2, 3)]
            out.append({"kind": "angled_wall_straight", "at": mid,
                        "point": [(s["x0"] + s["x1"]) / 2000.0, (s["y0"] + s["y1"]) / 2000.0],
                        "description": f"a wall drawn at {seg['deg']:.0f} deg ({math.dist(a, b):.1f} m); no model "
                                       f"wall follows it at its angle", "element_ids": [], "confidence": 0.7})
    st = data.get("storeys") or {}
    n = int(st.get("count") or 0)
    if n > 0 and bfacts and n not in (bfacts.get("storeys"), bfacts.get("storeys_without_roof")):
        out.append({"kind": "storey_count_differs", "at": None, "point": None,
                    "description": f"the drawing's texts give {n} storeys ({', '.join(st.get('names') or [])[:80]}); "
                                   f"the reading has {bfacts.get('storeys')}", "element_ids": [],
                    "confidence": 0.8, "building": True})
    for k, f in enumerate(out):
        f["key"] = f"{f['kind']}:{k}"           # the pod-1 keys (the review sheets' ids): later rules keep them
    # 20 Nov 2026 (pod 1, synthetic-14: 7 false room_missing): a labelled place outside the level's walls is another
    # plan in the same image, not a room missing: plan_not_read
    for f in out:
        if f["kind"] == "room_missing" and not _in_walls_extent(facts, f["at"]):
            f["kind"] = "plan_not_read"
            f["description"] = f["description"].replace("the reading has no room there",
                                                        "it lies outside the level's walls: a plan the reading did not "
                                                        "read")
    # ... an entrance on a plan above the ground is no building entrance (synthetic-21's roof plan)
    if facts.get("above_ground"):
        out = [f for f in out if f["kind"] != "entrance_missing"]
    # ... the mirror axis also mirrors the balconies (real09 L2: one listed, its twin missing)
    if pos is not None:
        listed =[(s, _m(entry, s["x"], s["y"])) for s in data.get("balconies") or [] if isinstance(s, dict)]
        k = 0
        for s, at in listed:
            mx, my = (2 * pos - s["x"], s["y"]) if mirror["axis"] == "vertical" else (s["x"], 2 * pos - s["y"])
            if not (0 <= mx <= 1000 and 0 <= my <= 1000):
                continue
            mat = _m(entry, mx, my)
            if any(math.dist(a, mat) <= MIRROR_TOL_M for _s, a in listed) or math.dist(at, mat) <= MIRROR_TOL_M:
                continue                                        # listed itself, or on the axis
            has = lambda p: room_at({"rooms": facts.get("outdoor") or []}, p, reach=0.6) is not None or any(  # noqa: E731
                r.get("open_air") and _contains(r["poly"], p, 0.6) for r in facts.get("rooms") or [])
            if has(at) and not has(mat) and _in_walls_extent(facts, mat, margin=2.0) \
                    and not any(f["kind"] == "balcony_missing" and f.get("at") and math.dist(f["at"], mat) < 1.0
                                for f in out):
                out.append({"kind": "balcony_missing", "at": mat, "point": [mx / 1000.0, my / 1000.0],
                            "description": f"the plan mirrors about the {mirror['axis']} axis; the {s.get('kind')} "
                                           f"listed at its twin place has no twin in the reading", "element_ids": [],
                            "confidence": 0.6, "key": f"balcony_missing:m{k}"})
                k += 1
    return out


def _code_mirror(entry: dict, facts: dict, orient: Optional[str]) -> Optional[float]:
    """The mirror line the model named (``vertical`` / ``horizontal`` in the image) as a 0-1000 image position, taken
    from the reading's own wall symmetry (``facts["mirror"]``) when that is at least ``MIRROR_MIN_SCORE``, else None
    (the model's own position is too rough, and it names a mirror for nearly every plan)."""
    from wenart.reading_check.critic import metres_to_norm

    tf = entry.get("tf") or []
    if orient not in ("vertical", "horizontal") or len(tf) < 6 or abs(tf[1]) > 1e-9 or abs(tf[3]) > 1e-9:
        return None
    m = (facts.get("mirror") or {}).get("x" if orient == "vertical" else "y") or {}
    if float(m.get("score") or 0.0) < MIRROR_MIN_SCORE:
        return None
    ext = facts.get("extent") or [0.0, 0.0, 0.0, 0.0]
    if orient == "vertical":
        return metres_to_norm(m["axis"], (ext[1] + ext[3]) / 2.0, entry["box"], tf)[0] * 1000.0
    return metres_to_norm((ext[0] + ext[2]) / 2.0, m["axis"], entry["box"], tf)[1] * 1000.0


def _in_walls_extent(facts: dict, p, margin: float = EXTENT_MARGIN_M) -> bool:
    """Whether ``p`` lies within the level's wall extent (``facts["extent"]``, else its rooms') plus ``margin``."""
    ext = facts.get("extent")
    if not ext:
        pts = [q for r in list(facts.get("rooms") or []) + list(facts.get("outdoor") or []) for q in r.get("poly") or []]
        if not pts:
            return True                                         # nothing to tell: not another plan
        ext = [min(q[0] for q in pts), min(q[1] for q in pts), max(q[0] for q in pts), max(q[1] for q in pts)]
    return ext[0] - margin <= p[0] <= ext[2] + margin and ext[1] - margin <= p[1] <= ext[3] + margin


def _inside_extent(facts: dict, p, margin: float = 0.3) -> bool:
    """Whether ``p`` lies within the bounding box of the reading's rooms and outdoor spaces (less ``margin``)."""
    pts = [q for r in list(facts.get("rooms") or []) + list(facts.get("outdoor") or []) for q in r.get("poly") or []]
    if not pts:
        return False
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return min(xs) + margin <= p[0] <= max(xs) - margin and min(ys) + margin <= p[1] <= max(ys) - margin


def _nearest(items: list, p) -> Optional[tuple]:
    from shapely.geometry import Point

    best = None
    for r in items:
        d = _poly(r["poly"]).distance(Point(p))
        if best is None or d < best[0]:
            best = (d, r)
    return best


def _room_type_at(facts: dict, p, types: tuple) -> bool:
    return any(r.get("type") in types and _contains(r["poly"], p, 0.5) for r in facts.get("rooms") or [])


# =================================================================================================== 3. compare
def compare_questions(entry: dict, facts: dict, cap: int = COMPARE_MAX, copies_facts: tuple = ()) -> list:
    """The level's yes/no questions (pure): ``[{n, qid, kind, at, point, model_fact, element_ids, ask}]``, at most
    ``cap``, room questions first (the drawing's labelled places, then the reading's rooms no label stands in), then
    the angled walls, the exterior doors above the ground (also of a ground plan whose copies stand above it,
    ``copies_facts``), the outer walls of habitable rooms with no window, and the openings (exterior first), each kind
    capped."""
    from wenart.reading_check.critic import metres_to_norm

    def norm(at):
        nx, ny = metres_to_norm(at[0], at[1], entry["box"], entry["tf"])
        return [round(nx, 4), round(ny, 4)] if 0.01 <= nx <= 0.99 and 0.01 <= ny <= 0.99 else None

    qs: list = []
    taken: list = []

    def add(kind, at, model_fact, ids, ask, sep=0.8):
        p = norm(at)
        if p is None or any(math.dist(at, t) < sep for t in taken):
            return False
        taken.append(at)
        qs.append({"kind": kind, "at": _r(at), "point": p, "model_fact": model_fact, "element_ids": list(ids),
                   "ask": ask})
        return True

    n_room = 0
    room_q = "Is there a room here in the drawing? Is there a room here in the model?"
    for lab in facts.get("drawn_labels") or []:
        if n_room >= COMPARE_CAPS["room"] or lab.get("exterior"):
            continue
        r = room_at(facts, lab["at"], reach=0.0)
        if add("room", lab["at"], "yes" if r else "no", [r["id"]] if r else [], room_q):
            n_room += 1
    for r in sorted(facts.get("rooms") or [], key=lambda r: -float(r.get("area") or 0)):
        if n_room >= COMPARE_CAPS["room"] or r.get("open_air") or float(r.get("area") or 0) < 1.5:
            continue
        if add("room", r["at"], "yes", [r["id"]], room_q, sep=1.5):
            n_room += 1
    n = 0
    ang_q = "Is this wall drawn at an angle in the drawing? Is it straight (not at that angle) in the model?"
    for s in sorted(facts.get("drawn_angled") or [], key=lambda s: -s["length"]):
        if n >= COMPARE_CAPS["angled"]:
            break
        straight = not follows_angled(s, facts.get("angled_walls") or [])
        if add("angled", s["mid"], "yes" if straight else "no", [], ang_q):
            n += 1
    for w in facts.get("angled_walls") or []:
        if n >= COMPARE_CAPS["angled"]:
            break
        mid = [(w["a"][0] + w["b"][0]) / 2.0, (w["a"][1] + w["b"][1]) / 2.0]
        if add("angled", mid, "no", [w["id"]], ang_q):
            n += 1
    n = 0
    bal_q = ("Does this exterior door above the ground have a balcony or terrace in front of it in the drawing? "
             "In the model?")
    # 20 Nov 2026 (pod 1: real09's ground plan L0 stands for L1 too, whose doors open into the air): a plan at the
    # ground asks about its doors when a storey above the ground is its copy, with that copy's front
    uppers = [cf for cf in copies_facts or [] if cf.get("above_ground")]
    if facts.get("above_ground") or uppers:
        for o in facts.get("openings") or []:
            if n >= COMPARE_CAPS["balcony"] or o.get("type") != "door" or not o.get("exterior"):
                continue
            front = o.get("front")
            twins = [x for cf in uppers for x in cf.get("openings") or []
                     if x.get("type") == "door" and math.dist(x["at"], o["at"]) <= 0.3]
            if not facts.get("above_ground"):
                if not twins:
                    continue
                front = twins[0].get("front")
            # a door the page stands for that opens into the air on any copy (real20: L1 over the ground floor's
            # roof, L2-L4 over nothing) is asked as one with nothing in front
            if any(x.get("front") == "nothing" for x in twins):
                front = "nothing"
            if add("balcony", o["at"], "yes" if front in ("open_air", "roof_below") else "no", [o["id"]], bal_q,
                   sep=0.6):
                n += 1
    n = 0
    win_q = ("Does the drawing show a window or a door in the outer wall at this mark? Does the model?")
    for wp in facts.get("window_places") or []:
        if n >= COMPARE_CAPS["window"]:
            break
        if add("window", wp["at"], "no", [wp["room_id"]], win_q, sep=0.6):
            n += 1
    n = 0
    op_q = ("Is this opening a door, a window or a plain opening in the drawing (none when the drawing has no opening "
            "here)? And in the model?")
    # exterior first; of those the plain gaps (a window or door read as a hole), then the inferred ones
    ops = sorted(facts.get("openings") or [], key=lambda o: (not o.get("exterior"), o.get("type") != "opening",
                                                             not o.get("inferred"), o["id"]))
    for o in ops:
        if n >= COMPARE_CAPS["opening"]:
            break
        if add("opening", o["at"], o.get("type") or "opening", [o["id"]], op_q, sep=0.6):
            n += 1
    qs = qs[:cap]
    for k, q in enumerate(qs):
        q["n"] = k + 1
        q["qid"] = f"q{k + 1}"
    return qs


def compare_chunks(questions: list, size: int = COMPARE_CHUNK) -> list:
    return [questions[i:i + size] for i in range(0, len(questions), size)] or []


def chunks_of(item: dict) -> list:
    """An entry's question chunks with the chunk size it was asked with (pod 1's entries: 20)."""
    return compare_chunks(item.get("compare") or [], int(item.get("compare_chunk") or COMPARE_CHUNK_POD1))


ANSWER_ENUM = ["yes", "no", "door", "window", "opening", "none", "unclear"]


def compare_schema(chunk: list) -> dict:
    ids = [q["qid"] for q in chunk]
    return _obj({"answers": {"type": "array", "minItems": len(ids), "maxItems": len(ids),
                             "items": _obj({"id": {"type": "string", "enum": ids},
                                            "drawing": {"type": "string", "enum": ANSWER_ENUM},
                                            "model": {"type": "string", "enum": ANSWER_ENUM}})}})


def compare_prompt(entry: dict, chunk: list) -> str:
    qs = "\n".join(f"- {q['qid']} (mark {q['n']}): {q['ask']}" for q in chunk)
    return (f"Image 1 is the architect's source drawing of {entry.get('title') or 'a level'}. Image 2 is a computer's "
            f"model of the same level drawn the same way (black walls, door leaves and swings, window symbols, room "
            f"labels) in the same frame. Both images carry the same red numbered marks. Answer each question about "
            f"the place of its mark: 'drawing' for image 1, 'model' for image 2. Answer yes or no; for an opening "
            f"door, window, opening (a plain gap) or none; 'unclear' only when the image cannot show it. Look at "
            f"each mark itself, not at the rest of the plan.\n{qs}")


def mark_image(src: Path, chunk: list, dest: Path) -> Path:
    """``src`` with a red numbered circle at each question's point (normalised), saved as ``dest``."""
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for q in chunk:
        x, y = q["point"][0] * w, q["point"][1] * h
        r = 13
        d.ellipse([x - r, y - r, x + r, y + r], outline=(220, 0, 0), width=3)
        tx, ty = label_origin(x, y, len(str(q["n"])), w, h, r)
        d.rectangle([tx - 1, ty, tx + 12 * len(str(q["n"])) + 2, ty + 20], fill=(255, 255, 255))
        d.text((tx, ty), str(q["n"]), fill=(220, 0, 0), font=font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=85)
    return dest


def label_origin(x: float, y: float, digits: int, w: int, h: int, r: int = 13) -> tuple:
    """Where a mark's number goes (pure): right of the ring and above it, moved left or below when that would leave
    the image (20 Nov 2026, pod 1: the numbers of the marks on a frame's right edge were cut off, and the model
    answered 'none' for 14 of them)."""
    tw = 12 * digits + 4
    tx = x + r + 2 if x + r + 2 + tw <= w else x - r - 2 - tw
    ty = y - r - 4 if y - r - 4 >= 0 else y + r + 2
    return max(0.0, tx), min(max(0.0, ty), h - 21.0)


def label_cut_pod1(point: list, size: list, n: int) -> bool:
    """Whether the number of a mark drawn by the pod-1 layout (right of the ring, above it) was cut off by the image's
    edge (pure): such a question could not be read, its answer is not counted."""
    w, h = float(size[0]), float(size[1])
    x, y = point[0] * w, point[1] * h
    return x + 15 + 12 * len(str(n)) + 2 > w or y - 17 < 0


def _first_answers(data: dict, key: str = "id") -> list:
    """The answers with the first one of each question id only (a model may repeat an id; the schema cannot forbid
    it: ``uniqueItems`` is not in vLLM's grammar)."""
    seen, out = set(), []
    for a in data.get("answers") or []:
        if isinstance(a, dict) and a.get(key) not in seen:
            seen.add(a.get(key))
            out.append(a)
    return out


def compare_findings(data: dict, chunk: list, *, facts: Optional[dict] = None, size: Optional[list] = None,
                     layout: int = 2) -> list:
    """The answers of one compare call against what the reading has at each mark (pure). A finding where the drawing
    answer contradicts the reading's own fact (``model_fact``); its confidence is 0.8 when the model's answer about
    image 2 matches the reading (it read image 2 right), 0.4 when it does not. A room the drawing has outside the
    level's walls is ``plan_not_read`` (``facts``); with ``layout`` 1 (pod 1) a mark whose number the image's edge cut
    off is not counted (``size``)."""
    byq = {q["qid"]: q for q in chunk}
    out = []
    for a in _first_answers(data):
        q = byq.get(a.get("id"))
        if q is None:
            continue
        if layout == 1 and size and label_cut_pod1(q["point"], size, q["n"]):
            continue
        dr, mo, fact = a.get("drawing"), a.get("model"), q["model_fact"]
        kind, text = None, ""
        if q["kind"] == "room":
            read_right = mo == fact
            if dr == "yes" and fact == "no":
                kind, text = "room_missing", "the drawing has a room here; the reading has none"
            elif dr == "no" and fact == "yes":
                kind, text = "room_not_in_drawing", "the reading has a room here; the drawing has none"
        elif q["kind"] == "angled":
            read_right = mo == fact
            if dr == "yes" and fact == "yes":
                kind, text = "angled_wall_straight", "the drawing draws this wall at an angle; the model's is straight"
        elif q["kind"] == "balcony":
            read_right = mo == fact
            if dr == "no" and fact == "no":
                kind, text = "door_into_air", "an exterior door above the ground with nothing in front in the drawing"
            elif dr == "yes" and fact == "no":
                kind, text = "balcony_missing", "the drawing has a balcony or terrace in front of this door; the reading has none"
        elif q["kind"] == "window":
            read_right = mo == fact
            if dr == "yes" and fact == "no":
                kind, text = "window_missing", "the drawing has a window or door in this outer wall; the reading has none"
        else:
            read_right = mo == fact
            if dr == "none":
                kind, text = "opening_not_in_drawing", f"the reading has a {fact} here; the drawing has no opening"
            elif dr in ("door", "window", "opening") and dr != fact:
                kind, text = "opening_type_differs", f"the drawing has a {dr} here; the reading a {fact}"
        if kind is None:
            continue
        if kind == "room_missing" and facts is not None and not _in_walls_extent(facts, q["at"]):
            kind, text = "plan_not_read", "the drawing has a room here, outside the level's walls: a plan not read"
        out.append({"key": q["qid"], "kind": kind, "at": q["at"], "point": q["point"], "description": text,
                    "element_ids": q.get("element_ids") or [], "confidence": 0.8 if read_right else 0.4,
                    "model_read_right": read_right, "answer": {"drawing": dr, "model": mo, "fact": fact}})
    return out


# ======================================================================================== 3b. the second look
# 20 Nov 2026 (the user: "Lets improve the AI"): a finding of the image checks under ``SECOND_LOOK_BELOW`` gets one
# short question about a close-up of the drawing around its place, asked once on the pod after the first pass;
# ``presence``: the finding holds when the answer is yes, ``absence``: when it is no, ``type``: when the opening type
# named is the drawing's first answer.
SECOND_KINDS = {
    "room_missing": ("presence", "a room (a space closed by walls, with or without a label)"),
    "mirror_twin_missing": ("presence", "a room (a space closed by walls, with or without a label)"),
    "balcony_missing": ("presence", "a balcony or a terrace"),
    "stair_missing": ("presence", "a stair (a flight of treads)"),
    "lift_missing": ("presence", "a lift shaft"),
    "angled_wall_straight": ("presence", "a wall drawn at an angle to the image's edges"),
    "window_missing": ("presence", "a window or a door in the outer wall"),
    "entrance_missing": ("presence", "an entrance door in the outer wall"),
    "door_into_air": ("absence", "a balcony, a terrace or a roof in front of the door"),
    "room_not_in_drawing": ("absence", "a room (a space closed by walls)"),
    "opening_not_in_drawing": ("absence", "an opening (a door, a window or a plain gap) in the wall"),
    "opening_type_differs": ("type", "the opening in the wall"),
}
SECOND_CROP_PX = 400           # the close-up: this many pixels of the 1600 px drawing around the place ...
SECOND_OUT_PX = 800            # ... shown at this size


def second_look_items(index: dict, found: list, below: float = SECOND_LOOK_BELOW, cap: int = SECOND_LOOK_MAX) -> list:
    """The findings that get a second look (pure): image-check findings of a ``SECOND_KINDS`` kind under ``below``
    with a place in their plan image, the least confident first, at most ``cap``; each as the item its call needs."""
    entries = {e["id"]: e for e in index.get("entries") or []}
    out = []
    for f in sorted(found, key=lambda f: (float(f.get("confidence") or 0), f["id"])):
        if f.get("call") not in ("inventory", "compare") or f.get("kind") not in SECOND_KINDS or f.get("dropped"):
            continue
        if float(f.get("confidence") or 0) >= below:
            continue
        e, pt = finding_point(f, entries)
        if e is None or pt is None or not (0.0 <= pt[0] <= 1.0 and 0.0 <= pt[1] <= 1.0):
            continue
        mode, what = SECOND_KINDS[f["kind"]]
        out.append({"id": f["id"], "kind": f["kind"], "mode": mode, "what": what, "folder": e["folder"],
                    "drawing": e["drawing"], "point": [round(pt[0], 4), round(pt[1], 4)], "set": e.get("set"),
                    "first": (f.get("answer") or {}).get("drawing"), "fact": (f.get("answer") or {}).get("fact")})
        if len(out) >= cap:
            break
    return out


def second_prompt(item: dict) -> str:
    if item["mode"] == "type":
        return ("The image is a close-up of an architect's floor plan. Look only at the red ring. Is the opening in the "
                "wall at the ring a door (a leaf with a swing arc), a window (thin parallel lines across the wall), a "
                "plain opening (a gap with nothing drawn in it), or is there no opening (none)? Answer unclear only "
                "when the close-up cannot show it.")
    return (f"The image is a close-up of an architect's floor plan. Look only at the red ring. Is there {item['what']} "
            f"at the ring in this drawing? Answer yes or no; unclear only when the close-up cannot show it.")


def second_schema(item: dict) -> dict:
    enum = ["door", "window", "opening", "none", "unclear"] if item["mode"] == "type" else ["yes", "no", "unclear"]
    return _obj({"answer": {"type": "string", "enum": enum}})


def second_image(item: dict, images_root: Path, dest: Path) -> Path:
    """The close-up of the drawing around the item's place with a red ring, saved as ``dest``."""
    from PIL import Image, ImageDraw

    im = Image.open(Path(images_root) / item["folder"] / item["drawing"]).convert("RGB")
    w, h = im.size
    x, y = item["point"][0] * w, item["point"][1] * h
    half = SECOND_CROP_PX / 2.0
    box = (int(max(0, x - half)), int(max(0, y - half)), int(min(w, x + half)), int(min(h, y + half)))
    c = im.crop(box)
    s = SECOND_OUT_PX / float(max(c.size))
    c = c.resize((max(1, int(c.size[0] * s)), max(1, int(c.size[1] * s))), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    px, py = (x - box[0]) * s, (y - box[1]) * s
    d.ellipse([px - 26, py - 26, px + 26, py + 26], outline=(220, 0, 0), width=4)
    dest.parent.mkdir(parents=True, exist_ok=True)
    c.save(dest, quality=88)
    return dest


def second_verdict(item: dict, data: dict) -> Optional[bool]:
    """Whether the second look confirms its finding (True), rejects it (False), or cannot tell (None) (pure)."""
    a = (data or {}).get("answer")
    if a in (None, "unclear"):
        return None
    if item["mode"] == "presence":
        return a == "yes"
    if item["mode"] == "absence":
        return a == "no"
    if a == item.get("fact"):
        return False                                            # the drawing has what the reading has
    return True if a == item.get("first") else None


def apply_second_looks(found: list, answers: dict) -> list:
    """The findings with their second look applied (in place, pure): a rejected one gets ``dropped: True`` (kept for
    the calibration of the second look itself, left out of the trust tables, the sheets and the store), a confirmed
    one at least confidence 0.85."""
    looks = {a["id"]: a for a in answers.get("answers") or [] if a.get("which") == "second"
             and isinstance(a.get("data"), dict) and a.get("item")}
    for f in found:
        a = looks.get(f.get("id"))
        if a is None:
            continue
        v = second_verdict(a["item"], a["data"])
        f["second_look"] = {"answer": a["data"].get("answer"), "verdict": v}
        if v is False:
            f["dropped"] = True
        elif v is True:
            f["confidence"] = max(float(f.get("confidence") or 0), 0.85)
    return found


def compare_reliability(data: dict, chunk: list) -> dict:
    """How often the model's answer about image 2 matched the reading (pure): ``{asked, right, unclear}``."""
    byq = {q["qid"]: q for q in chunk}
    asked = right = unclear = 0
    for a in _first_answers(data):
        q = byq.get(a.get("id"))
        if q is None:
            continue
        asked += 1
        right += int(a.get("model") == q["model_fact"])
        unclear += int(a.get("model") == "unclear" or a.get("drawing") == "unclear")
    return {"asked": asked, "right": right, "unclear": unclear}


def draw_arch(ax, building: dict, level: str, tf: list) -> None:
    """The model of ``level`` drawn like an architect's plan in the drawing's frame (``ax`` in drawing units): black
    wall bands with the openings cut, door leaves and swing arcs, window symbols (three lines), plain gaps, the room
    labels in the drawing's own spelling, outdoor spaces dashed with their labels, stairs with treads and an arrow,
    lifts crossed; no colour, no legend."""
    from matplotlib.patches import Polygon as MPoly

    from wenart.reading_check.sheets import _inverse

    inv = _inverse(tf)
    k = "#000000"
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level and w.get("start")
             and w.get("end") and math.dist(w["start"], w["end"]) > 1e-6}

    def band(a, b, t):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        nx, ny = -dy / n * t / 2.0, dx / n * t / 2.0
        return [inv(a[0] + nx, a[1] + ny), inv(b[0] + nx, b[1] + ny), inv(b[0] - nx, b[1] - ny), inv(a[0] - nx, a[1] - ny)]

    for w in walls.values():
        ax.add_patch(MPoly(band(w["start"], w["end"], max(0.08, float(w.get("thickness") or 0.2))), closed=True,
                           facecolor=k, edgecolor=k, lw=0.2, zorder=3))
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != level or not w or not o.get("center"):
            continue
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        t = max(0.08, float(w.get("thickness") or 0.2))
        half = float(o.get("width") or 0.9) / 2.0
        cx, cy = o["center"][:2]
        a = (cx - ux * half, cy - uy * half)
        b = (cx + ux * half, cy + uy * half)
        ax.add_patch(MPoly(band(a, b, t * 1.15), closed=True, facecolor="white", edgecolor="white", lw=0, zorder=4))
        for p in (a, b):                                        # the jambs
            q0, q1 = inv(p[0] + nx * t / 2, p[1] + ny * t / 2), inv(p[0] - nx * t / 2, p[1] - ny * t / 2)
            ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=k, lw=0.6, zorder=5)
        typ = o.get("type")
        if typ == "window":
            for off in (-t / 4.0, 0.0, t / 4.0):
                q0, q1 = inv(a[0] + nx * off, a[1] + ny * off), inv(b[0] + nx * off, b[1] + ny * off)
                ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=k, lw=0.5, zorder=5)
        elif typ == "door":
            side = -1.0 if str(o.get("swing_side") or "").lower() in ("right", "out", "outward") else 1.0
            leaves = [(a, 1.0, 2 * half)] if o.get("operation") != "double" else [(a, 1.0, half), (b, -1.0, half)]
            for hinge, dirn, wl in leaves:
                tip = (hinge[0] + nx * side * wl, hinge[1] + ny * side * wl)
                q0, q1 = inv(*hinge), inv(*tip)
                ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=k, lw=0.7, zorder=5)
                pts = []
                for s in range(0, 19):
                    ang = math.radians(90.0 * s / 18.0)
                    vx = ux * dirn * math.sin(ang) + nx * side * math.cos(ang)
                    vy = uy * dirn * math.sin(ang) + ny * side * math.cos(ang)
                    pts.append(inv(hinge[0] + vx * wl, hinge[1] + vy * wl))
                xs, ys = zip(*pts)
                ax.plot(xs, ys, color=k, lw=0.4, zorder=5)
    for r in building.get("rooms") or []:
        if r.get("level_id") != level or len(r.get("polygon") or []) < 3:
            continue
        if is_lift(r):
            pts = [inv(*p[:2]) for p in r["polygon"]]
            xs, ys = zip(*(pts + pts[:1]))
            ax.plot(xs, ys, color=k, lw=0.5, zorder=2)
            bx = (min(xs), min(ys), max(xs), max(ys))
            ax.plot([bx[0], bx[2]], [bx[1], bx[3]], color=k, lw=0.4, zorder=2)
            ax.plot([bx[0], bx[2]], [bx[3], bx[1]], color=k, lw=0.4, zorder=2)
        lab = r.get("label_raw") or r.get("label")
        if lab:
            c = inv(*_rep(r["polygon"]))
            ax.text(c[0], c[1], str(lab)[:28], fontsize=5.5, ha="center", va="center", color=k, clip_on=True, zorder=6)
    for s in (building.get("site") or {}).get("outdoor_spaces") or []:
        if not isinstance(s, dict) or s.get("level_id") != level or len(s.get("polygon") or []) < 3:
            continue
        pts = [inv(*p[:2]) for p in s["polygon"]]
        xs, ys = zip(*(pts + pts[:1]))
        ax.plot(xs, ys, color=k, lw=0.5, ls=(0, (4, 2)), zorder=2)
        if s.get("label"):
            c = inv(*_rep(s["polygon"]))
            ax.text(c[0], c[1], str(s["label"])[:20], fontsize=5.5, ha="center", va="center", color=k, clip_on=True,
                    zorder=6)
    for f in building.get("furniture") or []:
        if f.get("level_id") != level or f.get("type") != "stair" or not (f.get("footprint") or {}).get("center"):
            continue
        fp = f["footprint"]
        cx, cy = fp["center"][:2]
        sx, sy = float(fp["size"][0]) / 2.0, float(fp["size"][1]) / 2.0
        a = math.radians(float(fp.get("rotation_deg") or 0.0))
        ca, sa = math.cos(a), math.sin(a)
        pts = [inv(cx + ca * u - sa * v, cy + sa * u + ca * v) for u, v in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy))]
        xs, ys = zip(*(pts + pts[:1]))
        ax.plot(xs, ys, color=k, lw=0.6, zorder=2)
        for fl in ((f.get("details") or {}).get("stair") or f.get("stair") or {}).get("flights") or []:
            if not (fl.get("start") and fl.get("end")):
                continue
            s0, s1 = fl["start"][:2], fl["end"][:2]
            L = math.dist(s0, s1)
            if L <= 1e-6:
                continue
            ux, uy = (s1[0] - s0[0]) / L, (s1[1] - s0[1]) / L
            hw = float(fl.get("width") or 1.0) / 2.0
            step = float(fl.get("spacing") or 0.28) or 0.28
            m = 0.0
            while m <= L + 1e-6:
                p = (s0[0] + ux * m, s0[1] + uy * m)
                q0, q1 = inv(p[0] - uy * hw, p[1] + ux * hw), inv(p[0] + uy * hw, p[1] - ux * hw)
                ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=k, lw=0.35, zorder=2)
                m += max(0.15, step)
            p0, p1 = inv(*s0), inv(*s1)
            ax.annotate("", xy=p1, xytext=p0, arrowprops={"arrowstyle": "->", "color": k, "lw": 0.6}, zorder=6)


# ============================================================================================== 4. plausibility
def floor_summary(building: dict, lid: str, bfacts: dict, facts: Optional[dict] = None) -> dict:
    """A short text of one floor from building.json (pure but for shapely) and its id tables:
    ``{text, ids: {room, door, stair, outdoor}, points: {id: [x, y]}, windows: {room id: n}, doors_air: [ids],
    balcony_doors: {outdoor id: n}, lift_doors_into_rooms: [ids]}``."""
    f = facts or level_facts(building, lid)
    lv = next((x for x in bfacts.get("levels") or [] if x["id"] == lid), {})
    names = {r["id"]: r for r in f["rooms"]}
    names.update({s["id"]: dict(s, type=s.get("kind") or "outdoor") for s in f["outdoor"]})

    def nm(x):
        if x in ("outside", "unknown"):
            return x
        r = names.get(x) or {}
        common = " common" if r.get("subtype") == "common" else ""
        return f"{x} {r.get('label') or ''} ({r.get('type') or '?'}{common})".replace("  ", " ")

    windows = {r["id"]: 0 for r in f["rooms"]}
    balcony_doors = {s["id"]: 0 for s in f["outdoor"]}
    door_lines, air, lift_into = [], [], []
    lifts = {x["id"] for x in f["lifts"]}
    outdoor_ids = set(balcony_doors)
    for o in f["openings"]:
        a, b = o["sides"]
        if o["type"] == "window":
            for x, y in ((a, b), (b, a)):
                if x in windows and (y in ("outside", "unknown") or y in outdoor_ids) and o.get("exterior"):
                    windows[x] += 1
            continue
        for x, y in ((a, b), (b, a)):
            if x in outdoor_ids and y in windows:
                balcony_doors[x] += 1
            if x in windows and y in outdoor_ids and o["type"] == "door":
                windows[x] += 0                                 # a balcony door: listed below with the door
        if o.get("front") == "nothing":
            air.append(o["id"])
        if (a in lifts and b in names and b not in lifts and names[b].get("subtype") != "common"
                and names[b].get("type") not in ("hall", "corridor", "stair", "landing")) or \
                (b in lifts and a in names and a not in lifts and names[a].get("subtype") != "common"
                 and names[a].get("type") not in ("hall", "corridor", "stair", "landing")):
            lift_into.append(o["id"])
        extra = ""
        above_m = float(lv.get("elevation") or f.get("elevation") or 0.0) - float(bfacts.get("ground") or 0.0)
        if o.get("exterior") and f.get("above_ground"):
            # 20 Nov 2026 (pod 1: real09's d_L1_006 'nothing in front' was taken for the entrance): the height says it
            extra = {"open_air": ", balcony or terrace in front",
                     "roof_below": ", the roof of the storey below in front",
                     "nothing": f", nothing in front, {above_m:.2f} m above the ground"}.get(o.get("front") or "", "")
        door_lines.append(f"- {o['id']} ({o['type']}, {o['width']:.2f} m): {nm(a)} <-> {nm(b)}{extra}")
    above = float(lv.get("elevation") or f.get("elevation") or 0.0) - float(bfacts.get("ground") or 0.0)
    head = (f"Storey {lid} '{lv.get('label') or f.get('label') or ''}', floor at {above:+.2f} m from the ground floor"
            + (f", a copy of {lv['typical_of']}" if lv.get("typical_of") else "") + ".")
    ents = [e for e in f["entrances"]]
    lines = [head, f"The building has {bfacts.get('storeys')} storeys: "
             + ", ".join(f"{x['id']} {x.get('label') or ''}".strip() for x in bfacts.get("levels") or []) + "."]
    lines.append("Rooms (id, label, type, area, exterior windows):")
    for r in f["rooms"]:
        common = ", common" if r.get("subtype") == "common" else ""
        lines.append(f"- {r['id']} {r.get('label') or ''} ({r.get('type') or '?'}{common}), {r['area']:.1f} m2, "
                     f"{windows.get(r['id'], 0)} window(s)")
    if f["outdoor"]:
        lines.append("Balconies and terraces (id, label, kind, area, doors from rooms):")
        for s in f["outdoor"]:
            lines.append(f"- {s['id']} {s.get('label') or ''} ({s.get('kind') or 'outdoor'}), {s['area']:.1f} m2, "
                         f"{balcony_doors[s['id']]} door(s)")
    lines.append("Doors and openings (id, type, width: the two spaces they join):")
    lines += door_lines or ["- none"]
    st = f["stairs"]
    lines.append("Stairs: " + ("; ".join(f"{s['id']} in {nm(s.get('room_id') or 'unknown')}" for s in st) if st else "none")
                 + ".")
    lines.append("Lifts: " + (", ".join(nm(x["id"]) for x in f["lifts"]) if f["lifts"] else "none") + ".")
    lines.append("Entrance of the building on this storey: "
                 + (", ".join(f"{e['door_id']}{' (main)' if e.get('main') else ''}" for e in ents) if ents else "none")
                 + ". Vents and shafts are not listed.")
    ids = {"room": [r["id"] for r in f["rooms"]], "door": [o["id"] for o in f["openings"] if o["type"] != "window"],
           "window": [o["id"] for o in f["openings"] if o["type"] == "window"],
           "stair": [s["id"] for s in st] + [s.get("room_id") for s in st if s.get("room_id")],
           "outdoor": [s["id"] for s in f["outdoor"]] + [r["id"] for r in f["rooms"] if r.get("open_air")]}
    points = {r["id"]: r["at"] for r in f["rooms"]}
    points.update({s["id"]: s["at"] for s in f["outdoor"]})
    points.update({o["id"]: o["at"] for o in f["openings"]})
    points.update({s["id"]: s["at"] for s in st})
    types = {r["id"]: r.get("type") for r in f["rooms"]}
    return {"text": "\n".join(lines), "ids": ids, "points": points, "windows": windows, "doors_air": air,
            "balcony_doors": balcony_doors, "lift_doors_into_rooms": lift_into, "types": types}


def plausibility_prompt(item: dict) -> str:
    qs = "\n".join(f"- {q[0]}: {q[3]}" for q in PLAUSIBILITY_QUESTIONS)
    return (f"Below is a computer's reading of one storey of a building, as a list. Check it as an architect checks a "
            f"plan for sense. Answer every question with the ids of the elements it asks for, exactly as written in "
            f"the list; give no ids when nothing in the list matches. Use only what the list says.\n\n{item['text']}\n\n"
            f"Questions:\n{qs}")


PLAUSIBILITY_SCHEMA = _obj({"answers": {
    "type": "array", "minItems": len(PLAUSIBILITY_QUESTIONS), "maxItems": len(PLAUSIBILITY_QUESTIONS),
    "items": _obj({"q": {"type": "string", "enum": [q[0] for q in PLAUSIBILITY_QUESTIONS]},
                   "ids": {"type": "array", "maxItems": 12, "items": {"type": "string", "maxLength": 40}},
                   "note": {"type": "string", "maxLength": 160}})}})


def _code_agrees(kind: str, eid: str, item: dict) -> Optional[bool]:
    t = (item.get("types") or {}).get(eid)
    if kind == "habitable_no_window":
        return (item.get("windows") or {}).get(eid, 0) == 0 and t in HABITABLE_TYPES
    if kind == "kitchen_no_window":
        return (item.get("windows") or {}).get(eid, 0) == 0 and t in ("kitchen", "living_kitchen")
    if kind == "door_into_air":
        return eid in (item.get("doors_air") or [])
    if kind == "balcony_no_door":
        return (item.get("balcony_doors") or {}).get(eid, 1) == 0 if eid in (item.get("balcony_doors") or {}) else None
    if kind == "lift_door_into_flat":
        return eid in (item.get("lift_doors_into_rooms") or [])
    return None


def plausibility_findings(data: dict, item: dict, bfacts: Optional[dict] = None) -> tuple:
    """The answers of one plausibility call (pure): ``(findings, invalid)``; a finding per answered id that exists on
    the storey and is of the asked class (a storey-wide question, P7, gives one finding naming all its rooms), each at
    the element's point; ``invalid`` lists the ids that do not exist or are of another class. 20 Nov 2026 (pod 1: 10
    of 10 false on the one-storey synthetic houses): P7 counts only in a building of more than one storey (``bfacts``),
    where a stair is needed."""
    qmap = {q[0]: q for q in PLAUSIBILITY_QUESTIONS}
    if bfacts is not None and int(bfacts.get("storeys") or 0) <= 1:
        qmap.pop("P7", None)
    ids = item.get("ids") or {}
    allowed = {"room": set(ids.get("room") or []), "door": set(ids.get("door") or []),
               "stair": set(ids.get("stair") or []), "outdoor": set(ids.get("outdoor") or [])}
    points = item.get("points") or {}
    out, invalid = [], []
    for a in _first_answers(data, "q"):
        q = qmap.get(a.get("q"))
        if q is None:
            continue
        qid, kind, cls, _text = q
        good = []
        for eid in a.get("ids") or []:
            eid = str(eid).strip()
            if eid in allowed[cls]:
                if eid not in good:
                    good.append(eid)
            else:
                invalid.append({"q": qid, "id": eid})
        if not good:
            continue
        if kind == "storey_no_stair_access":
            agrees = None
            out.append({"key": f"{qid}:{good[0]}", "kind": kind, "at": points.get(good[0]), "element_ids": good,
                        "description": f"{len(good)} room(s) with no way to a stair: {', '.join(good[:6])}"
                                       + (f" ({a.get('note')})" if a.get("note") else ""),
                        "confidence": 0.6, "code_agrees": agrees})
            continue
        for eid in good:
            agrees = _code_agrees(kind, eid, item)
            out.append({"key": f"{qid}:{eid}", "kind": kind, "at": points.get(eid), "element_ids": [eid],
                        "description": f"{eid}: {KIND_TEXT[kind]}" + (f" ({a.get('note')})" if a.get("note") else ""),
                        "confidence": 0.7 if agrees is not False else 0.4, "code_agrees": agrees})
    return out, invalid


# ================================================================================================ 5. prepare
ID_RE = re.compile(r"\b(?:r|d|o|os|win|f)_[^\s,()]+")


def summaries_for(building: dict, bfacts: dict, facts_by_level: dict) -> list:
    """The floor texts of a reading (pure). 20 Nov 2026 (pod 1: real20's L2-L4 were asked one by one and answered
    differently, their texts differed only in the outdoor spaces' id numbers): a storey whose text equals an earlier
    one's but for its ids, its height and its name is left out; the earlier text carries it in ``copies`` with the id
    map (position by position) and its points, so every answer holds for it too (``propagate_copies``)."""
    out, seen = [], {}
    for lv in bfacts.get("levels") or []:
        lid = lv["id"]
        s = floor_summary(building, lid, bfacts, facts_by_level.get(lid))
        body = s["text"].split("\n", 2)[-1]
        body = re.sub(r", \d+\.\d\d m above the ground", "", body)
        key = ID_RE.sub("#", body)
        if key in seen:
            src = seen[key]
            a, b = ID_RE.findall(src["_body"]), ID_RE.findall(body)
            if len(a) == len(b):
                src.setdefault("copies", []).append({"level": lid, "ids": dict(zip(a, b)), "points": s["points"]})
                continue
        s["level"] = lid
        s["_body"] = body
        seen[key] = s
        out.append(s)
    for s in out:
        s.pop("_body", None)
    return out


def page_levels(building: dict, levels: list, drawn: set) -> dict:
    """``{level id: the drawn page level that stands for it, or None}`` (pure but for the reading check's inferred
    ground): a drawn level itself, an inferred ground floor its drawn storey, a copy through its ``typical_of`` chain."""
    from wenart import reading_check as RC

    try:
        g = RC.drawn_for_inferred_ground(building)
    except Exception:  # noqa: BLE001 - no inferred ground
        g = {}
    g = g if isinstance(g, dict) else {}
    typ = {lv["id"]: lv.get("typical_of") for lv in levels}

    def page(lid, depth=0):
        if lid in drawn:
            return lid
        if g.get(lid) in drawn:
            return g[lid]
        nxt = typ.get(lid)
        return page(nxt, depth + 1) if nxt and depth < 8 else None

    return {lv["id"]: page(lv["id"]) for lv in levels}


def prepare_reading(out_dir: Path, building: dict, sheets: dict, rendered: list, *, set_name: str, name: str,
                    project: str, arch: bool = True, truth: Optional[dict] = None) -> dict:
    """The checks' inputs of one reading (the entries ``rendered`` by ``critic.render_level`` are completed in place):
    per entry ``facts`` and ``compare`` (the questions); the reading's ``bfacts`` and floor ``texts``; with ``truth``
    (a synthetic project's exact truth) each entry's ``disagreements``."""
    from wenart import reading_check as RC
    from wenart.reading_check import critic as CR
    from wenart.reading_check import structure as SR

    bfacts = building_facts(building)
    shapes = SR.outlines(building)
    levels = bfacts["levels"]
    below = {}
    for i, lv in enumerate(levels):
        lower = [x for x in levels[:i] if float(x.get("elevation") or 0) < float(lv.get("elevation") or 0) - GROUND_UP_M]
        below[lv["id"]] = shapes.get(lower[-1]["id"]) if lower else None
    pages = RC.level_pages(building)
    facts_by_level = {}
    by_level = {e["level"]: e for e in rendered}
    for lv in levels:
        lid = lv["id"]
        page, tf = None, None
        if lid in by_level:
            pg = pages.get(lid) or {}
            try:
                page = RC.read_level_page(Path(out_dir), sheets, pg)
            except Exception:  # noqa: BLE001 - no page: no drawn labels
                page = None
            tf = pg.get("tf")
        facts_by_level[lid] = level_facts(building, lid, outline=shapes.get(lid), below=below.get(lid), page=page, tf=tf)
    dis = None
    if truth is not None:
        from wenart.reading_check import truth as TR

        dis = CR.level_disagreements(truth, TR.extract(building, project=project,
                                                        leave_out=truth.get("levels_left_out") or []))
    page_lv = page_levels(building, levels, set(by_level))
    for e in rendered:
        f = facts_by_level.get(e["level"]) or {}
        e["facts"] = f
        copies_facts = [facts_by_level[x] for x, p in page_lv.items() if p == e["level"] and x != e["level"]
                        and x in facts_by_level]
        e["compare"] = compare_questions(e, f, copies_facts=copies_facts)
        e["compare_chunk"] = COMPARE_CHUNK
        e["mark_layout"] = 2
        e["stands_for"] = sorted(x for x, p in page_lv.items() if p == e["level"])
        if dis is not None:
            e["disagreements"] = [dict(d, seg=[list(x) if x else None for x in d["seg"]] if d.get("seg") else None)
                                  for d in dis.get(e["level"]) or []]
            for c in e.get("copies") or []:
                e["disagreements"] += [dict(d, level=c, seg=[list(x) if x else None for x in d["seg"]] if d.get("seg") else None)
                                       for d in dis.get(c) or []]
    texts = []
    page_of = {lid: (by_level[p]["id"] if p in by_level else None) for lid, p in page_lv.items()}
    for s in summaries_for(building, bfacts, facts_by_level):
        lid = s.pop("level")
        texts.append(dict(s, id=f"{set_name}/{name}/{lid}#text", set=set_name, project=project, folder=f"{set_name}/{name}",
                          level=lid, page_entry=page_of.get(lid),
                          disagreements=[dict(d, seg=[list(x) if x else None for x in d["seg"]] if d.get("seg") else None)
                                         for d in (dis or {}).get(lid) or []] if dis is not None else None))
    return {"bfacts": bfacts, "texts": texts}


# ============================================================================================ 6. answers, judging
def item_findings(which: str, item: dict, data: dict, part: int = 0, bfacts: Optional[dict] = None) -> tuple:
    """The findings of one answer of a check (pure): ``(findings, extra)`` with ``extra`` the call's own numbers
    (the compare call's reliability, the plausibility call's invalid ids)."""
    if which == "inventory":
        return inventory_findings(data, item, item.get("facts") or {}, bfacts), {}
    if which == "compare":
        chunks = chunks_of(item)
        chunk = chunks[part] if part < len(chunks) else []
        return (compare_findings(data, chunk, facts=item.get("facts"), size=item.get("size"),
                                 layout=int(item.get("mark_layout") or 1)),
                {"reliability": compare_reliability(data, chunk)})
    if which == "plausibility":
        found, invalid = plausibility_findings(data, item, bfacts)
        found = propagate_copies(found, item)
        return found, {"invalid_ids": invalid}
    return [], {}


def propagate_copies(found: list, item: dict) -> list:
    """A floor text that stands for its copies (``item["copies"]``: ``[{level, ids: {id: copy id}, points}]``, the
    storeys whose text was the same but for ids and heights) gives each finding again on every copy, with the copy's
    ids (pure)."""
    out = list(found)
    for c in item.get("copies") or []:
        idmap, pts = c.get("ids") or {}, c.get("points") or {}
        for f in found:
            ids = [idmap.get(e) for e in f.get("element_ids") or []]
            if not ids or any(e is None for e in ids):
                continue
            out.append(dict(f, key=f"{f['key']}@{c['level']}", element_ids=ids, level_id=c["level"],
                            at=pts.get(ids[0]), copy_of=item.get("level")))
    return out


def judge_exact(finding: dict, disagreements: list, match_m: float) -> dict:
    """A finding of a synthetic project against its exact truth (``critic.judge`` with this module's kind rules)."""
    from wenart.reading_check import critic as CR

    if finding["kind"] == "plan_not_read":
        missing = int(finding.get("truth_levels_missing") or 0)
        return {"right": missing > 0, "reason": f"exact truth: {missing} level(s) of the truth not read"}
    if finding.get("at") is None:
        return {"right": None, "reason": "no place: not judged by the exact truth"}
    classes, sides = JUDGE_RULES.get(finding["kind"], (("rooms", "doors", "windows", "openings", "walls", "stairs"),
                                                       ("truth_only", "read_only")))
    best = None
    for d in disagreements:
        if d.get("class") in classes and d.get("side") in sides and d.get("at"):
            dist = CR._dist_to(tuple(finding["at"]), dict(d, seg=tuple(d["seg"]) if d.get("seg") else None))
            if best is None or dist < best[0]:
                best = (dist, d)
    right = best is not None and best[0] <= match_m
    return {"right": right, "reason": (f"exact truth: {best[1]['class']} {best[1]['side']} {best[1].get('id')} at "
                                       f"{best[0]:.2f} m") if right else "exact truth: no disagreement of its kind near"}


def judge_known(finding: dict, known: list, match_m: float) -> dict:
    """A finding of a real reading against the known errors of its reading (pure): right when a known error of the
    reading whose kinds name the finding's kind lies within ``match_m`` (a building-wide error: anywhere); wrong when
    the place is a known error's that this reading has fixed (``fixed``: the error of the reading before, absent
    here); otherwise not judged."""
    lv = finding.get("level_id")
    levels_ok = {lv} | set(finding.get("copies") or [])         # a page level stands for its copies
    best = None
    for k in known:
        # ``kinds``: the kinds that name the error (its recall counts for a check with one of them); ``also``: kinds
        # whose finding at that place is right too (a door into the air found as the balcony missing in front of it)
        if finding["kind"] not in list(k.get("kinds") or []) + list(k.get("also") or []):
            continue
        if k.get("level") and lv and k["level"] not in levels_ok:
            continue
        if k.get("at") is None or finding.get("at") is None:
            d = 0.0 if (k.get("at") is None and finding.get("at") is None) or k.get("building") else None
        else:
            d = math.dist(finding["at"], k["at"])
        if d is None or d > match_m:
            continue
        if best is None or d < best[0]:
            best = (d, k)
    if best is None:
        return {"right": None, "reason": "no known error or fixed place of its kind near"}
    k = best[1]
    if k.get("fixed"):
        return {"right": False, "reason": f"false alarm: known error {k['id']} is fixed in this reading", "known": k["id"]}
    return {"right": True, "reason": f"known error {k['id']}: {k.get('desc', '')[:80]}", "known": k["id"]}


def table(judged: list, kinds_by_check: dict = KINDS_BY_CHECK) -> dict:
    """``{check: {kind: {findings, judged, right, wrong, precision, false_alarms_after, trusted, small_sample}}}``."""
    from wenart.reading_check.critic import SMALL_SAMPLE, TRUST_MIN

    out: dict = {}
    for check, kinds in kinds_by_check.items():
        ks: dict = {}
        for kind in kinds:
            js = [j for j in judged if j["check"] == check and j["kind"] == kind]
            right = sum(1 for j in js if j.get("right") is True)
            wrong = sum(1 for j in js if j.get("right") is False)
            n = right + wrong
            ks[kind] = {"findings": len(js), "judged": n, "right": right, "wrong": wrong,
                        "precision": round(right / n, 4) if n else None,
                        "false_alarms_after": sum(1 for j in js if j.get("right") is False and j.get("set") == "after"),
                        "false_alarms_clean_synthetic": sum(1 for j in js if j.get("clean_class")),
                        "trusted": bool(n) and right / n >= TRUST_MIN and n >= 3, "small_sample": n < SMALL_SAMPLE,
                        "folders": len({j.get("folder") for j in js if j.get("right") is not None})}
        out[check] = ks
    return out


def recall(found: list, known_all: dict, match_m: float) -> list:
    """Each known error of a before reading (not fixed) with the checks that found it (pure)."""
    rows = []
    for folder, ks in known_all.items():
        for k in ks:
            if k.get("fixed"):
                continue
            by = sorted({f["call"] for f in found if f.get("folder") == folder and judge_known(f, [k], match_m).get("right")})
            rows.append({"id": k["id"], "folder": folder, "level": k.get("level"), "kinds": k.get("kinds"),
                         "desc": k.get("desc"), "found_by": by, "targeted": bool(k.get("kinds"))})
    return rows


def call_stats(index: dict, answers: dict) -> dict:
    """Per check: calls answered, failed, skipped; the compare calls' reliability (the model's answers about image 2
    against the reading) and the plausibility calls' invalid ids (pure)."""
    items = {e["id"]: e for e in index.get("entries") or []}
    items.update({t["id"]: t for t in index.get("texts") or []})
    out = {c: {"answered": 0, "failed": 0, "skipped": 0, "seconds": 0.0, "asked_marks": 0, "model_read_right": 0,
               "unclear": 0, "invalid_ids": 0, "answered_ids": 0} for c in CHECKS}
    for a in answers.get("answers") or []:
        w = a.get("which")
        if w not in out:
            continue
        s = out[w]
        if a.get("skipped"):
            s["skipped"] += 1
            continue
        if not isinstance(a.get("data"), dict):
            s["failed"] += 1
            continue
        s["answered"] += 1
        s["seconds"] += float(a.get("seconds") or 0)
        it = items.get(a.get("id"))
        if it is None:
            continue
        _f, extra = item_findings(w, it, a["data"], int(a.get("part") or 0))
        rel = extra.get("reliability")
        if rel:
            s["asked_marks"] += rel["asked"]
            s["model_read_right"] += rel["right"]
            s["unclear"] += rel["unclear"]
        if w == "plausibility":
            s["invalid_ids"] += len(extra.get("invalid_ids") or [])
            s["answered_ids"] += sum(len(x.get("ids") or []) for x in a["data"].get("answers") or [])
    for s in out.values():
        s["seconds"] = round(s["seconds"], 1)
    return out


def truth_levels_missing(truth: dict, building: dict) -> int:
    """How many levels of a synthetic project's exact truth the reading lacks, or reads with no room (pure)."""
    have = {r.get("level_id") for r in building.get("rooms") or []}
    return sum(1 for lv in truth.get("levels") or []
               if lv.get("id") not in have and ((truth.get("per_level") or {}).get(lv.get("id")) or {}).get("rooms"))


def stands_for(index: dict) -> dict:
    """``{entry id: levels}``: the storeys each plan image stands for (pure): its own level, its copies, and every
    storey whose floor text names it as its page or whose ``typical_of`` chain leads to one (real20: L2-L4 copies of
    the inferred L0, whose page is the drawn L1)."""
    out: dict = {}
    by_folder: dict = {}
    for e in index.get("entries") or []:
        by_folder.setdefault(e["folder"], {})[e["level"]] = e["id"]
        out[e["id"]] = {e["level"]} | set(copy_levels(e.get("copies"))) | set(e.get("stands_for") or [])
    text_page = {(t["folder"], t["level"]): t.get("page_entry") for t in index.get("texts") or []}
    for folder, rd in (index.get("readings") or {}).items():
        levels = {lv["id"]: lv for lv in (rd.get("bfacts") or {}).get("levels") or []}
        pages = by_folder.get(folder) or {}

        def page(lid, depth=0):
            if lid in pages:
                return pages[lid]
            if text_page.get((folder, lid)):
                return text_page[(folder, lid)]
            nxt = (levels.get(lid) or {}).get("typical_of")
            return page(nxt, depth + 1) if nxt and depth < 8 else None

        for lid in levels:
            p = page(lid)
            if p in out:
                out[p].add(lid)
    return out


def calibrate_checks(index: dict, found: list, answers: dict, *, known: Optional[dict] = None,
                     marks: Optional[dict] = None, match_m: float = 1.5, dropped: Optional[list] = None) -> dict:
    """The trust of checks 1, 2, 4 (pure given its inputs). Each finding is judged, in this order, by the user's mark
    (``marks``: {finding id: {right}}), by its synthetic project's exact truth (``judge_exact``; a finding on a
    synthetic reading with no error at all is a false alarm on a clean class), by the known errors of its real
    reading (``judge_known``: right at a known error of its kind, wrong at a place the reading has fixed), else not
    judged (the review sheet asks the user). ``dropped``: the findings the second look rejected, judged the same way
    to measure the second look itself (``second_look``). Returns ``{checks: {check: {kind: ...}}, recall, synthetic,
    calls, judgements, second_look}``."""
    known = known or {}
    marks = marks or {}
    readings = index.get("readings") or {}
    items = {e["id"]: e for e in index.get("entries") or []}
    items.update({t["id"]: t for t in index.get("texts") or []})
    dis_by_folder: dict = {}
    for it in items.values():
        if it.get("disagreements") is not None:
            dis_by_folder.setdefault(it["folder"], []).extend(it["disagreements"])
    judged = []
    n_found = len(found)
    for idx_f, f in enumerate(list(found) + list(dropped or [])):
        if f.get("call") not in CHECKS:
            continue
        rd = readings.get(f.get("folder")) or {}
        it = items.get(f.get("entry")) or {}
        j: dict = {"right": None, "reason": "not judged", "by": None}
        clean = False
        if f["id"] in marks:
            j = {"right": bool(marks[f["id"]].get("right")), "reason": "the user's mark", "by": "user"}
        elif rd.get("exact_truth"):
            dis = it.get("disagreements") or []
            clean = not dis_by_folder.get(f.get("folder"))
            fx = it.get("facts") or {}
            if f.get("at") is None and f["kind"] == "storey_count_differs":
                j = {"right": False, "reason": "exact truth: the synthetic storey count is the reading's", "by": "truth"}
            elif f["kind"] in ("room_missing", "plan_not_read", "mirror_twin_missing") and f.get("at") \
                    and "rooms" in fx and not fx["rooms"] and int(rd.get("truth_levels_missing") or 0) > 0 \
                    and any(math.dist(lab["at"], f["at"]) <= 1.5 for lab in fx.get("drawn_labels") or []):
                # synthetic-14: the reading has no room on this level at all (a level misread), and a drawn label
                # stands at the finding: the room is missing whatever level the truth files it under
                j = {"right": True, "reason": "exact truth: a level not read; the reading has no room on it, a drawn "
                                              "label stands here", "by": "truth"}
            else:
                j = dict(judge_exact(dict(f, truth_levels_missing=rd.get("truth_levels_missing")), dis, match_m),
                         by="truth")
        elif f.get("folder") in known:
            j = judge_known(f, known[f["folder"]], match_m)
            j["by"] = "known" if j.get("right") is not None else None
        judged.append({"id": f["id"], "check": f["call"], "kind": f["kind"], "folder": f.get("folder"),
                       "set": f.get("set"), "level": f.get("level_id"), "at": f.get("at"),
                       "confidence": f.get("confidence"), "description": f.get("description"),
                       "clean_class": clean and j.get("right") is False, "dropped": idx_f >= n_found,
                       "second_look": (f.get("second_look") or {}).get("verdict"), **j})
    looked = [j for j in judged if j.get("second_look") is not None or j["dropped"]]
    second = {"asked": sum(1 for a in answers.get("answers") or [] if a.get("which") == "second"),
              "dropped": sum(1 for j in judged if j["dropped"]),
              "dropped_right": sum(1 for j in judged if j["dropped"] and j.get("right") is True),
              "dropped_wrong": sum(1 for j in judged if j["dropped"] and j.get("right") is False),
              "confirmed": sum(1 for j in looked if j.get("second_look") is True),
              "confirmed_right": sum(1 for j in looked if j.get("second_look") is True and j.get("right") is True),
              "confirmed_wrong": sum(1 for j in looked if j.get("second_look") is True and j.get("right") is False)}
    judged_all = judged
    judged = [j for j in judged if not j["dropped"]]
    rows = recall(found, {k: v for k, v in known.items() if any(not x.get("fixed") for x in v)}, match_m)
    # the image checks see a level only through its plan (the page level and its copies); the floor texts every level
    seen: dict = {}
    sf = stands_for(index)
    for e in index.get("entries") or []:
        seen.setdefault(e["folder"], set()).update(sf.get(e["id"]) or {e["level"]})
    per_check = {}
    for c in CHECKS:
        tgt = [r for r in rows if set(r.get("kinds") or []) & set(KINDS_BY_CHECK[c])
               and (c == "plausibility" or r.get("level") is None or r.get("level") in seen.get(r["folder"], set()))]
        per_check[c] = {"targeted": len(tgt), "found": sum(1 for r in tgt if c in r["found_by"])}
    synth = []
    for folder, rd in sorted(readings.items()):
        if not rd.get("exact_truth"):
            continue
        dis = dis_by_folder.get(folder) or []
        fs = [j for j in judged if j["folder"] == folder]
        for c in CHECKS:
            cf = [j for j in fs if j["check"] == c]
            right = sum(1 for j in cf if j.get("right"))
            # the errors one of the check's kinds can name (labels and extra walls: none of these checks)
            rules = [JUDGE_RULES[k] for k in KINDS_BY_CHECK[c] if k in JUDGE_RULES]
            tgt = [d for d in dis if any(d.get("class") in cl and d.get("side") in sd for cl, sd in rules)]
            if c != "plausibility" and int(rd.get("truth_levels_missing") or 0) > 0:
                tgt.append({"class": "levels", "side": "truth_only"})
            if dis and not tgt:
                verdict = "caught" if right else ("not_targeted" if not cf else "false_alarm")
            else:
                verdict = ("caught" if right else "missed") if tgt else ("false_alarm" if cf else "clean")
            synth.append({"folder": folder, "class": rd.get("failure_class"), "check": c, "errors": len(dis),
                          "targeted_errors": len(tgt), "findings": len(cf), "right": right, "verdict": verdict})
    return {"checks": table(judged), "recall": {"rows": rows, "per_check": per_check},
            "synthetic": synth, "calls": call_stats(index, answers), "judgements": judged_all,
            "judged_by": {b: sum(1 for j in judged if j.get("by") == b) for b in ("user", "truth", "known", None)},
            "second_look": second}


def checks_summary(res: dict) -> str:
    """The calibration of checks 1, 2, 4 as short tables (markdown)."""
    lines = ["| check | kind | findings | judged | right | wrong | precision | false alarms after | trusted |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c, ks in (res.get("checks") or {}).items():
        for k, v in ks.items():
            if not v["findings"]:
                continue
            p = "-" if v["precision"] is None else f"{v['precision']:.2f}"
            lines.append(f"| {c} | {k} | {v['findings']} | {v['judged']} | {v['right']} | {v['wrong']} | {p} | "
                         f"{v['false_alarms_after']} | {'yes' if v['trusted'] else 'no'} |")
    pc = (res.get("recall") or {}).get("per_check") or {}
    lines.append("")
    lines.append("recall of the known errors (before readings): " + ", ".join(
        f"{c} {v['found']} of {v['targeted']}" for c, v in pc.items()))
    rows = (res.get("recall") or {}).get("rows") or []
    missed = [r for r in rows if r.get("targeted") and not r["found_by"]]
    lines.append(f"known errors: {len(rows)}; found by some check: {sum(1 for r in rows if r['found_by'])}; "
                 f"missed: {len(missed)}; not targeted by these checks: {sum(1 for r in rows if not r.get('targeted'))}")
    syn = res.get("synthetic") or []
    for c in CHECKS:
        s = [x for x in syn if x["check"] == c]
        if s:
            lines.append(f"synthetic {c}: " + ", ".join(f"{v} {sum(1 for x in s if x['verdict'] == v)}"
                                                       for v in ("caught", "missed", "false_alarm", "clean", "not_targeted")))
    for c, s in (res.get("calls") or {}).items():
        lines.append(f"calls {c}: {s['answered']} answered, {s['failed']} failed, {s['skipped']} skipped"
                     + (f"; image 2 read right on {s['model_read_right']} of {s['asked_marks']} marks"
                        if s.get("asked_marks") else "")
                     + (f"; {s['invalid_ids']} invalid of {s['answered_ids']} ids" if c == "plausibility" else ""))
    sl = res.get("second_look") or {}
    if sl.get("asked"):
        lines.append(f"second look: {sl['asked']} asked; {sl['dropped']} dropped (judged right {sl['dropped_right']}, wrong "
                     f"{sl['dropped_wrong']}); {sl['confirmed']} confirmed (right {sl['confirmed_right']}, wrong "
                     f"{sl['confirmed_wrong']})")
    jb = res.get("judged_by") or {}
    lines.append(f"judged by the user {jb.get('user', 0)}, by exact truth {jb.get('truth', 0)}, by known errors "
                 f"{jb.get('known', 0)}; not judged {jb.get(None, 0)} (on the review sheets)")
    return "\n".join(lines)


# ============================================================================================ 7. known errors
def _rooms_points(b: dict, lid: str) -> list:
    rooms, outdoor = _spaces(b, lid)
    return [(r["id"], r, False) for r in rooms] + [(s["id"], s, True) for s in outdoor]


def known_missing_rooms(before: dict, after: dict, levels: list, labels: tuple = ()) -> list:
    """Rooms and outdoor spaces of ``after`` on ``levels`` whose point lies in no space of ``before`` (pure): the
    before reading's missing rooms (``labels``: only these, folded, when given)."""
    out = []
    for lid in levels:
        have = [_poly(x["polygon"]) for _i, x, _o in _rooms_points(before, lid)]
        for rid, r, outdoor in _rooms_points(after, lid):
            lab = _norm_label(r.get("label"))
            if labels and not any(w in lab for w in labels):
                continue
            from shapely.geometry import Point

            p = _rep(r["polygon"])
            if any(h.buffer(0.1).contains(Point(p)) for h in have):
                continue
            twin = bool(r.get("twin_of")) or any(isinstance(e, dict) and e.get("rule") == "mirror_twin"
                                                 for e in r.get("evidence") or [])
            kinds = ["balcony_missing"] if outdoor else ["room_missing", "mirror_twin_missing"]
            out.append({"level": lid, "at": p, "kinds": kinds, "also": ["room_missing"] if outdoor else [],
                        "desc": f"{r.get('label')} ({rid} in the after reading) not read", "element": rid,
                        "twin": twin})
    return out


def known_angled(before: dict, after: dict, levels: list) -> list:
    """Walls of ``after`` drawn at an angle that no ``before`` wall follows (pure)."""
    out = []
    for lid in levels:
        wa = [w for w in after.get("walls") or [] if w.get("level_id") == lid and w.get("start") and w.get("end")]
        wb = [w for w in before.get("walls") or [] if w.get("level_id") == lid and w.get("start") and w.get("end")]
        ax = axis_deg(wa)
        for w in wa:
            if math.dist(w["start"], w["end"]) < 2.0 or off_axis(_deg(w["start"], w["end"]), ax) <= ANGLE_OFF_DEG:
                continue
            seg = {"a": w["start"], "b": w["end"], "deg": _deg(w["start"], w["end"])}
            if follows_angled(seg, wb):
                continue
            mid = [round((w["start"][0] + w["end"][0]) / 2, 3), round((w["start"][1] + w["end"][1]) / 2, 3)]
            out.append({"level": lid, "at": mid, "kinds": ["angled_wall_straight"],
                        "desc": f"wall {w['id']} at {seg['deg']:.0f} deg built straight or left out"})
    return out


def known_doors_into_air(building: dict) -> list:
    from wenart.reading_check import structure as SR

    return [{"level": f["level_id"], "at": _r(f["place"]) if f.get("place") else None,
             "kinds": ["door_into_air"], "also": ["balcony_missing"],
             "desc": f"door {(f.get('element_ids') or ['?'])[0]} into the air",
             "element": (f.get("element_ids") or [None])[0]}
            for f in SR.doors_into_air(building)]


def known_kitchens_without_window(before: dict, after: dict) -> list:
    """Kitchens of ``before`` with no exterior window whose ``after`` kitchen at the same place has one (pure)."""
    out = []
    bf, af = building_facts(before), building_facts(after)
    for lv in bf["levels"]:
        lid = lv["id"]
        if lid not in {x["id"] for x in af["levels"]}:
            continue
        sb = floor_summary(before, lid, bf)
        sa = floor_summary(after, lid, af)
        for rid, t in sb["types"].items():
            if t not in ("kitchen", "living_kitchen") or sb["windows"].get(rid, 0) > 0:
                continue
            p = sb["points"][rid]
            ra = [x for x, ta in sa["types"].items() if ta in ("kitchen", "living_kitchen")
                  and math.dist(sa["points"][x], p) <= 1.5]
            if ra and sa["windows"].get(ra[0], 0) > 0:
                # window_missing only ``also``: real10's kitchens have a balcony door, so no window question is asked
                out.append({"level": lid, "at": p, "kinds": ["kitchen_no_window", "habitable_no_window"],
                            "also": ["window_missing"],
                            "desc": f"kitchen {rid} without its drawn window", "element": rid})
    return out


def known_opening_changes(before: dict, after: dict, levels: list) -> list:
    """Openings of ``before`` that ``after`` reads as another type at the same place (within 0.3 m), or not at all
    (no opening of ``after`` within 0.6 m) (pure): real10's windows read as garden doors or holes (R10-P1, R10-P3)."""
    out = []
    for lid in levels:
        ob = [o for o in before.get("openings") or [] if o.get("level_id") == lid and o.get("center")]
        oa = [o for o in after.get("openings") or [] if o.get("level_id") == lid and o.get("center")]
        for o in ob:
            near = sorted(((math.dist(o["center"][:2], x["center"][:2]), x) for x in oa), key=lambda t: t[0])
            if near and near[0][0] <= 0.3:
                x = near[0][1]
                if (x.get("type") or "opening") != (o.get("type") or "opening"):
                    out.append({"level": lid, "at": _r(o["center"]), "kinds": ["opening_type_differs"],
                                "desc": f"{o['id']} read as a {o.get('type')}; drawn as a {x.get('type')}"})
            elif not near or near[0][0] > 0.6:
                out.append({"level": lid, "at": _r(o["center"]), "kinds": ["opening_not_in_drawing"],
                            "desc": f"{o['id']} ({o.get('type')}) where the drawing has no opening"})
    return out


def known_errors_for(project: str, before: dict, after: dict) -> tuple:
    """The listed known errors of a pod project's before reading and their fixed places in the after reading (pure):
    ``(before errors, after errors)``. The classes the brief lists: real09's missing left salon, kitchen and balcony
    (and its roof, which no check targets), real20's straight angled wall and doors into the air, real10's missing
    kitchen windows, real03's storey count; RC17's doors into the air on every reading."""
    bf, af = building_facts(before), building_facts(after)
    common = [x["id"] for x in bf["levels"] if x["id"] in {y["id"] for y in af["levels"]}]
    errs: list = []
    if project == "real09":
        errs += known_missing_rooms(before, after, [x for x in common if x in ("L0", "L1", "L2")],
                                    labels=("salon", "mutfak", "balkon"))
        errs.append({"level": None, "at": None, "kinds": [], "building": True,
                     "desc": "the roof read from the section is wrong (no check of 1, 2, 4 targets roofs)"})
    if project == "real20":
        errs += known_angled(before, after, common)
    if project == "real10":
        errs += known_kitchens_without_window(before, after)
        errs += known_opening_changes(before, after, common)
    if bf["storeys"] != af["storeys"] and project == "real03":
        errs.append({"level": None, "at": None, "kinds": ["storey_count_differs"], "building": True,
                     "desc": f"{bf['storeys']} storeys read; the drawing's texts give {af['storeys']}"})
    air_b, air_a = known_doors_into_air(before), known_doors_into_air(after)
    b_out = [dict(e, reading="before") for e in errs + air_b]
    a_out = [dict(e, reading="after") for e in air_a]
    for e in air_b:                                             # a door into the air the after reading no longer has
        if e.get("at") and not any(x["level"] == e["level"] and x.get("at") and math.dist(x["at"], e["at"]) < 0.5
                                   for x in air_a):
            a_out.append(dict(e, fixed=True, reading="after"))
    for e in errs:
        if e.get("kinds") and e.get("at") is not None:
            a_out.append(dict(e, fixed=True, reading="after"))
        elif e.get("kinds") and e.get("building"):
            a_out.append(dict(e, fixed=True, reading="after"))
    for k, e in enumerate(b_out):
        e["id"] = f"{project}-B{k + 1:02d}"
    for k, e in enumerate(a_out):
        e["id"] = f"{project}-A{k + 1:02d}"
    return b_out, a_out


def sparse_known(project: str, building: dict) -> list:
    """The user's screenshot corrections (the project's sparse truth) not holding on a reading, as known errors, and
    those holding as fixed places (``score.match_sparse``)."""
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    truth = TR.load_truth(project)
    if truth is None or not TR.is_sparse(truth):
        return []
    try:
        res = SC.match_sparse(truth, TR.extract(building, project=project), building)
    except Exception:  # noqa: BLE001 - a truth this reading cannot be matched with: none
        return []
    kinds_of = {("rooms", False): ["room_missing", "mirror_twin_missing"], ("rooms", True): ["room_not_in_drawing"],
                ("outdoor", False): ["balcony_missing"],
                ("doors", False): ["opening_type_differs", "entrance_missing"],
                ("doors", True): ["opening_not_in_drawing", "door_into_air"],
                ("windows", False): ["opening_type_differs", "habitable_no_window", "kitchen_no_window"],
                ("windows", True): ["opening_not_in_drawing"], ("openings", False): ["opening_type_differs"],
                ("openings", True): ["opening_not_in_drawing"], ("walls", False): ["angled_wall_straight"],
                ("stairs", False): ["stair_missing"]}
    out = []
    for x in res.get("entries") or []:
        cls, absent = x.get("type"), bool(x.get("absent"))
        sig = x.get("at") if isinstance(x.get("at"), (list, tuple)) else None
        at = sig[2] if sig and len(sig) >= 3 and isinstance(sig[2], (list, tuple)) and len(sig[2]) >= 2 else None
        # a place in the drawing's frame (thousands of units) is no metre place: left out
        if at is None or (cls, absent) not in kinds_of or max(abs(float(at[0])), abs(float(at[1]))) > 500:
            continue
        out.append({"level": x.get("level"), "at": _r(at), "kinds": kinds_of[(cls, absent)],
                    "fixed": bool(x.get("satisfied")), "records": x.get("records") or [],
                    "desc": f"user correction {', '.join(x.get('records') or [])}: {cls} {'absent' if absent else 'present'}"
                            f" {'holds' if x.get('satisfied') else 'does not hold'}"})
    return out


# ============================================================================================ 8. review sheets
def _crop(im, point, side_px: int, out_px: int):
    from PIL import ImageDraw

    w, h = im.size
    if point is None:
        c = im.copy()
        c.thumbnail((out_px, out_px))
        return c
    x, y = point[0] * w, point[1] * h
    half = side_px / 2.0
    box = (int(max(0, x - half)), int(max(0, y - half)), int(min(w, x + half)), int(min(h, y + half)))
    c = im.crop(box)
    sx, sy = out_px / max(1, c.size[0]), out_px / max(1, c.size[1])
    s = min(sx, sy)
    c = c.resize((max(1, int(c.size[0] * s)), max(1, int(c.size[1] * s))))
    d = ImageDraw.Draw(c)
    px, py = (x - box[0]) * s, (y - box[1]) * s
    d.ellipse([px - 10, py - 10, px + 10, py + 10], outline=(220, 0, 0), width=3)
    return c


def finding_point(f: dict, entries: dict) -> tuple:
    """The image entry and the normalised point of a finding (a plausibility finding through its storey's page)."""
    from wenart.reading_check.critic import metres_to_norm

    e = entries.get(f.get("image_entry") or f.get("entry"))
    if e is None or "box" not in e:
        return None, None
    if f.get("point") is not None:
        return e, f["point"]
    if f.get("at") is None:
        return e, None
    nx, ny = metres_to_norm(f["at"][0], f["at"][1], e["box"], e["tf"])
    return e, ([nx, ny] if -0.05 <= nx <= 1.05 and -0.05 <= ny <= 1.05 else None)


def review_sheets(index: dict, found: list, images_root: Path, dest: Path, *, judged: Optional[dict] = None,
                  per_sheet: int = 30, max_bytes: int = 2_000_000) -> dict:
    """One or a few JPEGs per reading folder (``<dest>/<set>/<name>/sheet_<k>.jpg``): each finding a numbered pair of
    crops (the drawing left, the model right, its point marked) with its kind and one line, the table by number under
    them, at most ``per_sheet`` findings a sheet, the most confident first (ties by id: the numbering is stable for the
    same answers); ``findings_index.json`` maps each number to the finding id. Returns ``{folder: [sheet files]}``."""
    from PIL import Image, ImageDraw, ImageFont

    entries = {e["id"]: e for e in index.get("entries") or []}
    judged = judged or {}
    dest = Path(dest)
    by_folder: dict = {}
    for f in found:
        if f.get("call") in CHECKS:
            by_folder.setdefault(f.get("folder") or "unknown", []).append(f)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
        bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    except OSError:
        font = bold = ImageFont.load_default()
    try:
        mono = ImageFont.truetype("DejaVuSansMono.ttf", 12)
    except OSError:
        mono = font
    written: dict = {}
    cell, pad, cols = 210, 8, 3
    pair_w = cell * 2 + pad
    cache: dict = {}

    def img(path):
        if path not in cache:
            cache[path] = Image.open(path).convert("RGB") if Path(path).is_file() else None
        return cache[path]

    for folder, fs in sorted(by_folder.items()):
        fs = sorted(fs, key=lambda f: (-float(f.get("confidence") or 0), f["id"]))
        out_dir = dest / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        idx = {"folder": folder, "sheets": [], "findings": {}}
        files = []
        for s, start in enumerate(range(0, len(fs), per_sheet)):
            chunk = fs[start:start + per_sheet]
            rows = math.ceil(len(chunk) / cols)
            width = cols * pair_w + (cols + 1) * pad
            grid_h = rows * (cell + 34) + pad
            table_h = 24 + 18 * len(chunk) + pad
            sheet = Image.new("RGB", (width, 40 + grid_h + table_h), "white")
            d = ImageDraw.Draw(sheet)
            d.text((pad, 10), f"RC15 checks - {folder} - sheet {s + 1}: drawing left, model right (red ring: the place)",
                   fill=(0, 0, 0), font=bold)
            numbers = {}
            for k, f in enumerate(chunk):
                n = start + k + 1
                numbers[str(n)] = f["id"]
                idx["findings"][f["id"]] = {"sheet": s + 1, "n": n}
                r, c = divmod(k, cols)
                x0, y0 = pad + c * (pair_w + pad), 40 + pad + r * (cell + 34)
                e, pt = finding_point(f, entries)
                for j, key in enumerate(("drawing", "model")):
                    im = img(Path(images_root) / e["folder"] / e[key]) if e is not None else None
                    if im is None:
                        d.rectangle([x0 + j * (cell + pad), y0 + 18, x0 + j * (cell + pad) + cell, y0 + 18 + cell],
                                    outline=(180, 180, 180))
                        d.text((x0 + j * (cell + pad) + 8, y0 + 100), "no plan image", fill=(120, 120, 120), font=font)
                        continue
                    crop = _crop(im, pt, 380, cell)
                    sheet.paste(crop, (x0 + j * (cell + pad), y0 + 18))
                jd = judged.get(f["id"]) or {}
                mark = {True: " [right]", False: " [wrong]"}.get(jd.get("right"), "")
                d.text((x0, y0), f"#{n} {f['call'][:3]} {f['kind']}{mark}", fill=(200, 0, 0), font=bold)
                d.text((x0, y0 + 18 + cell + 2), (f.get("level_id") or "") + " " + str(f.get("description") or "")[:58],
                       fill=(0, 0, 0), font=font)
            ty = 40 + grid_h
            head = f"{'#':<4}{'check':<14}{'kind':<26}{'level':<7}{'conf':<6}{'auto':<7}text"
            d.text((pad, ty), head, fill=(0, 0, 0), font=mono)
            for k, f in enumerate(chunk):
                jd = judged.get(f["id"]) or {}
                auto = {True: "right", False: "wrong"}.get(jd.get("right"), "-")
                line = (f"{start + k + 1:<4}{f['call']:<14}{f['kind'][:25]:<26}{str(f.get('level_id') or '-'):<7}"
                        f"{float(f.get('confidence') or 0):<6.2f}{auto:<7}{str(f.get('description') or '')[:120]}")
                d.text((pad, ty + 22 + 18 * k), line, fill=(0, 0, 0), font=mono)
            path = out_dir / f"sheet_{s + 1}.jpg"
            q = 80
            while True:
                sheet.save(path, quality=q, optimize=True)
                if path.stat().st_size <= max_bytes or q <= 40:
                    break
                q -= 10
            idx["sheets"].append({"file": path.name, "numbers": numbers})
            files.append(str(path))
        (out_dir / "findings_index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8")
        written[folder] = files
    return written


def marks_from_numbers(findings_index: dict, sheet: int, right: list, wrong: list) -> dict:
    """``{finding id: {"right": bool, "sheet", "n"}}`` from the numbers the user marked on a sheet (pure)."""
    sh = next((s for s in findings_index.get("sheets") or [] if s["file"] == f"sheet_{sheet}.jpg"), None)
    if sh is None:
        raise ValueError(f"no sheet {sheet} in {findings_index.get('folder')}")
    out = {}
    for flag, nums in ((True, right), (False, wrong)):
        for n in nums:
            fid = sh["numbers"].get(str(n))
            if fid is None:
                raise ValueError(f"no finding #{n} on sheet {sheet}")
            out[fid] = {"right": flag, "sheet": sheet, "n": int(n), "folder": findings_index.get("folder")}
    return out


def copy_levels(copies) -> list:
    """The level ids of an entry's ``copies``: plain level ids (a page's typical copies) or, for a floor text folded
    over identical storeys, ``{level, ids, points}`` records (pod x4vgfcm85u18op crashed on ``set()`` of those)."""
    return [c.get("level") if isinstance(c, dict) else c for c in (copies or []) if c]
