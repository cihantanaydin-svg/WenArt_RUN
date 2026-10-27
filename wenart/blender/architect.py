"""The architect: an architect's review questions put to every building before it is built (user request of 25 Oct
2026: "design a module called architect that can ask these kind of questions and make necessary changes ... ask
questions like an architect").

What: ``review(building, prep)`` asks the questions of ``QUESTIONS`` about the building JSON and the build plan
(``build.prepare``: the site plan, the roof, the outlines), fixes what a code rule can fix in the plan (pure; the
build then makes what the plan says) and returns ``{"questions": [...], "changes": n, "open": n}``;
``drainage_answer(kit)`` adds the answer about the rain water once the facade kit is planned. ``report_md`` writes
the review as the architect would hand it over (``architect.md`` next to the scene).

Why: the renders showed what an architect would have asked at the first look: downpipes hanging in the air in
front of loggias, a pool deck whose only steps were closed by a glass railing, a door to a roof terrace built like a
bedroom door, a light well standing over a lower terrace. Each was a general rule missing in the build, not a
real04 accident.

How: each question has an id, the topic, the question in an architect's words, a check (code: the plan's geometry,
never a guess) and, where one exists, a fix that changes the plan; a fix is kept only when the same check passes
afterwards (CLAUDE.md: "findings removed" is the measure). Every answer names the element, what was found, what was
changed and why, and the change is marked ``inferred`` / ``adjusted_by_ai`` (by code) in the plan. A question that
code cannot settle stays open in the report with the reason.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RULES

OPEN_AIR_TYPES = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")
DOOR_LEVEL_TOL_M = 0.30         # a door opens onto a platform when its sill is this close to the platform's level
DOOR_PROBE_M = 0.40             # how far in front of the wall face the door's landing is probed
ACCESS_MAX_DROP_M = 3.0         # the tallest flight the architect adds to reach an otherwise closed terrace
STEP_GAP_M = 0.10               # the railing stops this much wider than the flight on each side

QUESTIONS = (
    {"id": "A1", "topic": "rain water",
     "question": "Where does the rain go? Every gutter must drain into a downpipe fixed to a wall all the way down to "
                 "the ground: no pipe in front of a loggia, across a window or in the air."},
    {"id": "A2", "topic": "access",
     "question": "How do people get to each terrace and pool deck? From the house through a door at its level, or "
                 "from the garden by steps that no railing closes."},
    {"id": "A3", "topic": "outside doors",
     "question": "Which doors open to the open air? A door to a terrace or balcony is an outside door: glazed, "
                 "weather-tight, never the bedroom door of the inside."},
    {"id": "A4", "topic": "light wells",
     "question": "Why does this basement window have a light well? Only where the ground outside stands above its "
                 "sill; a terrace below the sill lights it on its own."},
    {"id": "A5", "topic": "decks without a door",
     "question": "This terrace lies at the floor level of the rooms beside it, right outside their windows, and no "
                 "door opens onto it: can people still reach it from outside? (The drawn windows stay windows; only "
                 "when no outside way exists does the architect ask you about a door.)"},
)


# 25 Oct 2026 (user: "make the architect more clever, asking better and better questions"): the design review an
# architect walks through a plan: arriving, moving through the house, light, air, privacy, use, safety. Each has the
# reason it matters (``why``); open findings carry a follow-up question for the user (``ask``).
QUESTIONS += (
    {"id": "B1", "topic": "arrival", "severity": "major",
     "question": "Where do I come in? Is there a path from the street to the main entrance door?",
     "why": "a front door nobody can find or reach on foot is the first thing a visitor notices"},
    {"id": "B2", "topic": "parking", "severity": "minor",
     "question": "Where do I leave the car, and how do I walk from it to the front door?",
     "why": "a parking with no path to the entrance makes people cross the lawn or the driveway's kerb"},
    {"id": "C1", "topic": "circulation", "severity": "major",
     "question": "Can I reach every room from the entrance, and without walking through somebody's bedroom?",
     "why": "a room you can only reach through a bedroom is a planning fault (an en-suite bathroom or dressing "
            "room is the exception)"},
    {"id": "C2", "topic": "kitchen", "severity": "minor",
     "question": "Is the kitchen next to where people eat and sit (a door or an opening to the living or dining "
                 "space)?",
     "why": "carrying plates through a hall or another room every day is a sign the plan is not working"},
    {"id": "L1", "topic": "daylight", "severity": "major",
     "question": "Does every bedroom, living room and kitchen get daylight: a window with glass of at least a tenth "
                 "of its floor?",
     "why": "a habitable room without enough daylight feels like a cellar; building codes ask for about 1/10"},
    {"id": "L2", "topic": "fresh air", "severity": "minor",
     "question": "Can every bathroom and kitchen be aired: a window, else a mechanical extract?",
     "why": "steam and cooking smells need a way out"},
    {"id": "P1", "topic": "privacy", "severity": "minor",
     "question": "Does a bathroom door open straight into the living room, the dining space or the kitchen?",
     "why": "a toilet door in the room where people eat or receive guests is uncomfortable for everybody"},
    {"id": "R1", "topic": "room size", "severity": "minor",
     "question": "Is every bedroom wide enough for its bed with room to walk around it?",
     "why": "a bedroom narrower than about 2.4 m leaves no passage beside a bed"},
    {"id": "R2", "topic": "use", "severity": "minor",
     "question": "Is every room furnished for what it is (a bed in each bedroom, a sofa in the living room, a "
                 "table where people eat, a WC and a basin in each bathroom)?",
     "why": "a room without its main piece reads as unfinished in the renders"},
    {"id": "S1", "topic": "falls", "severity": "major",
     "question": "Where could somebody fall more than half a metre: is every such terrace, pool deck and roof "
                 "terrace edge guarded?",
     "why": "an unguarded drop is the first safety question of every design review"},
    {"id": "E1", "topic": "outside doors", "severity": "major",
     "question": "Does every outside door open onto something: the ground, a terrace, a balcony or steps?",
     "why": "a door into the air or below the ground is a drawing or level error"},
    # 26 Oct 2026 (user on real06: "windows second floor what is that? are the people going to jump off from it?")
    {"id": "O2", "topic": "gaps in the facade", "severity": "major",
     "question": "Is every gap in an outer wall a door or a window (never a bare hole in the facade)?",
     "why": "a gap with no door and no glass reads as a hole; on an upper floor nothing stops a fall"},
)
HABITABLE = ("bedroom", "living", "kitchen", "dining", "office", "study", "other")
WET = ("bathroom", "wc", "toilet", "shower", "kitchen", "laundry")
DAYLIGHT_RATIO = 0.10
BED_ROOM_MIN_M = 2.4
STAIR_WORDS = ("merdiven", "stair", "treppe", "escalier", "escalera", "escada", "scala")
ANCHORS = {"bedroom": ("bed_double", "bed_single", "bed", "bed_bunk"), "living": ("sofa", "sofa_corner"),
           "bathroom": ("toilet",), "kitchen": ("kitchen_counter", "sink_kitchen", "cooktop", "stove")}


FIRST_FIVE = {"A1": ("minor", "rain running down a facade stains it and a pipe in the air looks like a mistake"),
              "A2": ("major", "a terrace or pool nobody can walk to is useless and unsafe"),
              "A3": ("minor", "an inside door on the open air leaks and looks wrong from outside"),
              "A4": ("minor", "a light well where none is needed is a concrete box in the garden"),
              "A5": ("minor", "a deck at the floor's level begs for a door; the drawings decide it")}


def _q(qid: str) -> dict:
    q = dict(next(q for q in QUESTIONS if q["id"] == qid), answers=[], status="ok")
    sev, why = FIRST_FIVE.get(qid, (q.get("severity") or "minor", q.get("why") or ""))
    q.setdefault("severity", sev)
    q.setdefault("why", why)
    return q


# --------------------------------------------------------------------------
# A2: access to the terraces and pool decks
# --------------------------------------------------------------------------

def doors_onto(platform: dict, outer_doors: Sequence[dict]) -> list[str]:
    """The outside doors (``site.outer_openings`` records) that open onto a platform: the landing in front of the
    door lies on it and the sill is within ``DOOR_LEVEL_TOL_M`` of its level."""
    z = platform.get("z")
    if not isinstance(z, (int, float)):
        return []
    out = []
    for r in outer_doors:
        cx, cy = r["centre"]
        ox, oy = r["outward"]
        reach = float(r.get("half_t") or 0.1) + DOOR_PROBE_M
        landing = (cx + ox * reach, cy + oy * reach)
        if G.point_in_polygon(landing, platform["polygon"]) and abs(float(r["bottom"]) - float(z)) <= DOOR_LEVEL_TOL_M:
            out.append(r["opening"]["id"])
    return out


def steps_open(platform: dict) -> bool:
    """Whether a platform's flight of steps is there and no railing closes it."""
    i = platform.get("steps_edge")
    if i is None or platform.get("sloped"):
        return False
    return i not in (platform.get("railing_edges") or []) or i in (platform.get("railing_gaps") or [])


def access_edge(platform: dict) -> Optional[int]:
    """The edge for a new flight down to the garden (pure): not against the building, not shared with a band, the
    ground under it lower by ``level_tol`` .. ``ACCESS_MAX_DROP_M``, long enough for a flight; the smallest drop
    first, then the longest edge."""
    from wenart.blender.site import PLATFORM

    poly = platform.get("polygon") or []
    n = len(poly)
    drops = platform.get("edge_drops") or {}
    blocked = set(platform.get("against_edges") or []) | {int(k) for k in (platform.get("edge_floor") or {})}
    cands = []
    for i in range(n):
        if i in blocked:
            continue
        length = G.distance(poly[i], poly[(i + 1) % n])
        drop = drops.get(i, drops.get(str(i)))
        if drop is None or length < PLATFORM["step_width"] + 2 * STEP_GAP_M:
            continue
        if PLATFORM["level_tol"] < float(drop) <= ACCESS_MAX_DROP_M:
            cands.append((float(drop), -length, i))
    return min(cands)[2] if cands else None


PATH_SAMPLE_M = 0.25            # a route is checked every this many metres
PATH_TARGET_STEP_M = 0.5        # the points of an existing path a new path may join
LANDING_M = 0.6                 # the new path starts this far past the last step


def steps_landing(pf: dict) -> Optional[tuple[float, float]]:
    """Where a platform's flight of steps lands on the ground (pure): past the last tread, out from the middle of the
    steps edge."""
    from wenart.blender.site import PLATFORM

    i = pf.get("steps_edge")
    poly = pf.get("polygon") or []
    if i is None or len(poly) < 3:
        return None
    if pf.get("steps_dir") == "up":                      # a flight up out of a sunken deck lands on the slope above
        land = (pf.get("flight") or {}).get("landing")
        return (float(land[0]), float(land[1])) if land else None
    a, b = poly[i], poly[(i + 1) % len(poly)]
    length = G.distance(a, b)
    if length <= 1e-6:
        return None
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = uy, -ux                                     # counter-clockwise polygon: the right normal points out
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    drop = float((pf.get("edge_drops") or {}).get(i, (pf.get("edge_drops") or {}).get(str(i), 0.3)) or 0.3)
    count = max(1, int(math.ceil(drop / PLATFORM["step_rise"] - 1e-9)))
    d = count * PLATFORM["step_tread"] + LANDING_M
    return mid[0] + nx * d, mid[1] + ny * d


def _free(pt, keep_out, half: float) -> bool:
    """Whether a path point and its sides (``half`` either way, both axes) stay out of every keep-out polygon."""
    for dx, dy in ((0.0, 0.0), (half, 0.0), (-half, 0.0), (0.0, half), (0.0, -half)):
        q = (pt[0] + dx, pt[1] + dy)
        if any(G.point_in_polygon(q, poly) for poly in keep_out):
            return False
    return True


def _route_ok(points, keep_out, half: float) -> bool:
    for a, b in zip(points, points[1:]):
        length = G.distance(a, b)
        n = max(1, int(length / PATH_SAMPLE_M))
        for k in range(n + 1):
            t = k / n
            if not _free((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), keep_out, half):
                return False
    return True


def path_targets(paths: Sequence[dict], half: float) -> list[tuple[float, float]]:
    """Points along the existing paths a new path may join (pure): a grid of ``PATH_TARGET_STEP_M`` inside each path
    polygon, at least ``half`` - 0.2 m from its edge (its middle)."""
    from wenart.blender import geom2d

    out = []
    for p in paths:
        poly = p.get("polygon") or []
        if len(poly) < 3:
            continue
        xs, ys = [q[0] for q in poly], [q[1] for q in poly]
        x = min(xs)
        while x <= max(xs):
            y = min(ys)
            while y <= max(ys):
                if G.point_in_polygon((x, y), poly) and geom2d.distance_to_polygon_edges((x, y), poly) >= half - 0.2:
                    out.append((x, y))
                y += PATH_TARGET_STEP_M
            x += PATH_TARGET_STEP_M
    return out


def access_path(start, targets, keep_out, half: float) -> Optional[list[tuple[float, float]]]:
    """The shortest L-shaped route (two straight legs along the plan axes) from ``start`` to one of ``targets`` that
    keeps out of ``keep_out`` (pure), or None."""
    if not _free(start, keep_out, half):
        return None
    best = None
    for t in targets:
        for corner in ((start[0], t[1]), (t[0], start[1])):
            pts = [start, corner, t]
            length = G.distance(start, corner) + G.distance(corner, t)
            if best is not None and length >= best[0]:
                continue
            if _route_ok(pts, keep_out, half):
                best = (length, pts)
    return best[1] if best else None


def path_areas(pf_id: str, points, half: float, reason: str) -> list[dict]:
    """The route as path areas of the site plan (one rectangle per leg, ``inferred``)."""
    from wenart.blender.site import PAVING_LIFT

    out = []
    for k, (a, b) in enumerate(zip(points, points[1:])):
        length = G.distance(a, b)
        if length < 0.05:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy, ux
        a0 = (a[0] - ux * half, a[1] - uy * half)        # the legs overlap at the corner
        b0 = (b[0] + ux * half, b[1] + uy * half)
        poly = [(a0[0] + nx * half, a0[1] + ny * half), (a0[0] - nx * half, a0[1] - ny * half),
                (b0[0] - nx * half, b0[1] - ny * half), (b0[0] + nx * half, b0[1] + ny * half)]
        out.append({"id": f"path_access_{pf_id}_{k}", "kind": "path", "polygon": [list(p) for p in poly], "z": None,
                    "material": None, "colour": None, "source": "assumed", "area_id": None, "lift": PAVING_LIFT,
                    "inferred": True, "reason": reason})
    return out


def site_keep_out(site: dict, skip_id: str) -> list:
    """What a new path keeps out of (pure): the building's ground outline, the other buildings, the pools, the light
    wells and every flat platform but ``skip_id`` itself, its stepped bands included (a path on the ground never cuts
    a band's retaining wall; a driveway's draped parking may be crossed)."""
    keep = []
    if len(site.get("outline") or []) >= 3:
        keep.append(site["outline"])
    keep += [h for h in site.get("copy_holes") or [] if len(h) >= 3]
    keep += [p["polygon"] for p in site.get("pools") or [] if len(p.get("polygon") or []) >= 3]
    keep += [w["polygon"] for w in site.get("wells") or [] if len(w.get("polygon") or []) >= 3]
    for pf in site.get("platforms") or []:
        if pf["id"] == skip_id or pf.get("kind") == "parking" or pf.get("sloped"):
            continue
        keep.append(pf["polygon"])
    return keep


def outside_access(pf: dict, site: dict) -> Optional[list[dict]]:
    """A path from the foot of a deck's steps to the nearest path of the site (25 Oct 2026, user: "try to have an
    access from the outside instead of including the door"), or None when the steps already land on a path or no
    route keeps out of the house, the pools and the other terraces."""
    from wenart.blender.site import INFERRED

    half = INFERRED["path_width"] / 2.0
    start = steps_landing(pf)
    paths = [a for a in site.get("areas") or [] if a.get("kind") == "path"]
    if start is None:
        return None
    if not paths or any(G.point_in_polygon(start, p["polygon"]) for p in paths):
        return []                                        # no paths to join (the garden is the way in), or on one
    paved = [a for a in site.get("areas") or [] if a.get("kind") in ("parking", "paving") and a.get("id") != pf["id"]
             and len(a.get("polygon") or []) >= 3]
    if any(G.point_in_polygon(start, a["polygon"]) for a in paved):
        return []                                        # the steps land on a driveway or another terrace
    route = access_path(start, path_targets(paths, half), site_keep_out(site, pf["id"]), half)
    if route is None:
        return None
    reason = (f"architect A2: a path from the steps of {pf['id']} to the site's path "
              f"({sum(G.distance(a, b) for a, b in zip(route, route[1:])):.1f} m; inferred)")
    return path_areas(pf["id"], route, half, reason)


def review_access(prep: dict, outer_doors: Sequence[dict]) -> dict:
    q = _q("A2")
    site = prep.get("site") or {}
    for pf in site.get("platforms") or []:
        if pf.get("parent") or pf.get("kind") not in ("terrace", "pool"):
            continue
        name = f"{'pool deck' if pf.get('pools') else 'terrace'} {pf['id']} at {float(pf['z']):+.2f} m"
        doors = doors_onto(pf, outer_doors)
        before = steps_open(pf)
        # 26 Oct 2026 (labelled outdoor spaces, wenart/levels/outdoor.py): a platform at most a kerb's height over the
        # garden on an open edge is reached from the garden itself
        from wenart.blender.site import PLATFORM
        flush = not pf.get("elevated") and pf.get("edge") in ("none", "kerb") and \
            float(pf.get("drop_m") or 0.0) <= PLATFORM["level_tol"] + 1e-9 and \
            len(pf.get("against_edges") or []) < len(pf.get("polygon") or [])
        if flush and not doors and not before:
            pf["outside_access"] = "garden"
            q["answers"].append({"element": pf["id"], "found": f"{name}: reached from the garden (at most "
                                 f"{PLATFORM['level_tol']:.2f} m over it on an open edge)", "change": None})
            continue
        if doors or before:
            how = (f"door {', '.join(doors)} from the house" if doors else "") + \
                  (" and " if doors and before else "") + ("steps to the garden" if before else "")
            q["answers"].append({"element": pf["id"], "found": f"{name}: reached by {how}", "change": None})
            if not doors:
                _path_from_outside(pf, site, name, q)
            continue
        i = pf.get("steps_edge")
        if i is not None and not pf.get("sloped"):
            pf.setdefault("railing_gaps", []).append(i)
            change = (f"the glass railing on edge {i} closed its steps: the railing now stops "
                      f"{STEP_GAP_M:.2f} m beside the flight")
        else:
            i = access_edge(pf)
            if i is None:
                q["answers"].append({"element": pf["id"], "found": f"{name}: no door from the house at its level and "
                                     f"no edge where steps of up to {ACCESS_MAX_DROP_M:g} m can reach the garden",
                                     "change": None, "open": True})
                q["status"] = "open"
                continue
            pf["steps_edge"] = i
            pf["edge"] = "steps" if pf.get("edge") in (None, "none", "kerb", "retaining") else pf.get("edge")
            if i in (pf.get("railing_edges") or []):
                pf.setdefault("railing_gaps", []).append(i)
            change = f"no way in: a flight of steps down to the garden on edge {i} (inferred)"
        pf.setdefault("architect", []).append({"question": "A2", "change": change})
        ok = steps_open(pf)
        q["answers"].append({"element": pf["id"], "found": f"{name}: no door from the house at its level, no open "
                             f"steps", "change": change, "fixed": ok})
        if not ok:
            q["status"] = "open"
        else:
            _path_from_outside(pf, site, name, q)
    if any(a.get("change") for a in q["answers"]) and q["status"] == "ok":
        q["status"] = "fixed"
    return q


def _path_from_outside(pf: dict, site: dict, name: str, q: dict) -> None:
    """The deck's way in from outside (no door from the house): a path from its steps to the site's paths."""
    areas = outside_access(pf, site)
    if areas is None:
        pf["outside_access"] = "steps"
        q["answers"].append({"element": pf["id"], "found": f"{name}: its steps land on the garden, no path of the site "
                             f"can be reached around the house, the pools and the terraces", "change": None,
                             "open": True})
        q["status"] = "open"
        return
    if not areas:
        pf["outside_access"] = "on_path"
        return
    site.setdefault("areas", []).extend(areas)
    pf["outside_access"] = "path"
    pf.setdefault("architect", []).append({"question": "A2", "change": areas[0]["reason"]})
    q["answers"].append({"element": pf["id"], "found": f"{name}: its steps led onto the lawn and nowhere else",
                         "change": areas[0]["reason"].replace("architect A2: ", ""), "fixed": True})


def review_deck_doors(building: dict, prep: dict, outer_doors: Sequence[dict], outer_windows: Sequence[dict]) -> dict:
    """A5 (an open question for the user, never a change: drawn openings are the anchor): a terrace or pool deck at a
    level's floor (``DOOR_LEVEL_TOL_M``) with that level's windows opening onto it and no door to it."""
    q = _q("A5")
    levels = building.get("levels") or []
    for pf in (prep.get("site") or {}).get("platforms") or []:
        if pf.get("parent") or pf.get("kind") not in ("terrace", "pool") or not isinstance(pf.get("z"), (int, float)):
            continue
        lv = next((x for x in levels if abs(float(x["elevation"]) - float(pf["z"])) <= DOOR_LEVEL_TOL_M), None)
        if lv is None or doors_onto(pf, outer_doors):
            continue
        facing = []
        for r in outer_windows:
            if r["level"]["id"] != lv["id"]:
                continue
            cx, cy = r["centre"]
            ox, oy = r["outward"]
            reach = float(r.get("half_t") or 0.1) + DOOR_PROBE_M
            if G.point_in_polygon((cx + ox * reach, cy + oy * reach), pf["polygon"]):
                facing.append(r["opening"]["id"])
        if not facing:
            continue
        name = f"{'pool deck' if pf.get('pools') else 'terrace'} {pf['id']}"
        found = (f"{name} lies at the {lv['id']} floor ({float(pf['z']):+.2f} m) outside window(s) "
                 f"{', '.join(sorted(facing))}; no door opens onto it")
        # 25 Oct 2026 (user: "try to have an access from the outside instead of including the door"): the deck is
        # reached from outside (A2: its steps and a path); the drawn windows stay windows
        if pf.get("outside_access") in ("path", "on_path", "garden"):
            how = ("from the garden at its own level" if pf.get("outside_access") == "garden" else
                   "its steps and a path to the site's paths")
            q["answers"].append({"element": pf["id"], "found": found, "change": f"reached from outside: {how} (A2); "
                                 f"the windows stay as drawn"})
            continue
        q["answers"].append({"element": pf["id"], "found": found, "change": None, "open": True,
                             "ask": f"no path from outside reaches the {name}: should the architect find another "
                                    f"way, or should " + (f"window {facing[0]}" if len(facing) == 1 else
                                                          f"one of the windows {', '.join(sorted(facing))}")
                                    + " be a door?"})
        q["status"] = "open"
    return q


# --------------------------------------------------------------------------
# A3: doors to the open air
# --------------------------------------------------------------------------

def open_air_doors(building: dict) -> list[dict]:
    """The doors between an inside room and an open-air room (``OPEN_AIR_TYPES``) of the same level (pure):
    ``[{"opening", "room", "outside_room", "outward", "centre", "bottom", "top", "half_t"}]``; ``outward`` points
    into the open-air room."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    walls = {w["id"]: w for w in building.get("walls") or []}
    rooms = building.get("rooms") or []

    def room_at(pt, level_id):
        return next((r for r in rooms if r.get("level_id") == level_id and len(r.get("polygon") or []) >= 3
                     and G.point_in_polygon(pt, r["polygon"])), None)

    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        lv = levels.get(o.get("level_id"))
        if o.get("type") != "door" or w is None or lv is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, w)
        nx, ny = G.unit_normal_left(w["start"], w["end"])
        half_t = float(w.get("thickness") or 0.2) / 2.0
        reach = half_t + 0.25
        a = room_at((cx + nx * reach, cy + ny * reach), lv["id"])
        b = room_at((cx - nx * reach, cy - ny * reach), lv["id"])
        types = [str((r or {}).get("room_type") or "").lower() for r in (a, b)]
        outside = [t in OPEN_AIR_TYPES for t in types]
        if a is None or b is None or outside[0] == outside[1]:
            continue
        inside_room, open_room, sign = (b, a, 1.0) if outside[0] else (a, b, -1.0)
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in building.get("levels") or [])
        bottom, top, _ = opening_vertical(o, lv, above)
        out.append({"opening": o, "level": lv, "room": inside_room["id"], "outside_room": open_room["id"],
                    "outward": (nx * sign, ny * sign), "centre": (cx, cy), "bottom": bottom, "top": top,
                    "half_t": half_t})
    return out


def review_outside_doors(building: dict) -> tuple[dict, list[dict]]:
    """A3: every door to an open-air room becomes an outside door (``outside_door`` on the opening: the library plan
    takes it as a ``terrace_door``, the parametric fallback builds a glazed leaf)."""
    q = _q("A3")
    recs = open_air_doors(building)
    for r in recs:
        o = r["opening"]
        if o.get("outside_door"):
            q["answers"].append({"element": o["id"], "found": f"door {o['id']} to {r['outside_room']}: an outside "
                                 f"door", "change": None})
            continue
        o["outside_door"] = {"outside_room": r["outside_room"], "outward": [round(v, 6) for v in r["outward"]],
                             "reason": f"door {o['id']} opens from {r['room']} to the open-air {r['outside_room']}: "
                                       f"an outside door (glazed, weather-tight; adjusted_by_ai by code)"}
        q["answers"].append({"element": o["id"], "found": f"door {o['id']} from {r['room']} to the open-air "
                             f"{r['outside_room']} was an inside door", "change": "built as a glazed outside door",
                             "fixed": True})
        q["status"] = "fixed"
    return q, recs


# --------------------------------------------------------------------------
# A4: light wells
# --------------------------------------------------------------------------

def review_light_wells(prep: dict) -> dict:
    """A4: the plan's light wells and front courts against the platforms (``site.wells_on_platforms`` already ran
    in ``site_plan``): each well's reason, and the ones the platforms took away."""
    q = _q("A4")
    site = prep.get("site") or {}
    for w in site.get("wells") or []:
        q["answers"].append({"element": w["opening_id"], "found": w.get("reason"), "change": None})
    for a in site.get("assumed") or []:
        if str(a.get("field", "")).startswith("light_well:") and a.get("value") is None:
            q["answers"].append({"element": a["field"].split(":", 1)[1], "found": a.get("reason"),
                                 "change": "light well left out", "fixed": True})
            q["status"] = "fixed"
    return q


# --------------------------------------------------------------------------
# A1: rain water (after the facade kit)
# --------------------------------------------------------------------------

def drainage_answer(kit: Optional[dict], boxes: Sequence[dict]) -> dict:
    """A1 from the planned facade kit: the gutters, the downpipes placed on walls (``facade.pipe_spot``) and the
    stations where no wall reached the ground."""
    q = _q("A1")
    gutters = [b for b in boxes if b.get("kind") == "gutter"]
    pipes = [b for b in boxes if b.get("kind") == "downpipe" and b["size"][0] == b["size"][1]]
    notes = list((kit or {}).get("downpipes_not_placed") or [])
    if not gutters:
        q["answers"].append({"element": "roof", "found": "no gutter: no pitched eaves to drain", "change": None})
        return q
    q["answers"].append({"element": "gutters", "found": f"{len(gutters)} gutter run(s), {len(pipes)} downpipe(s), each "
                         f"on a wall face down to the ground", "change": None})
    # 26 Oct 2026 (user: "why there is that many rain gutters"): the count and the spacing an architect expects
    from wenart.blender import facade as FA
    xy = [(float(b["center"][0]), float(b["center"][1])) for b in pipes if b.get("center")]
    close = [(i, j) for i in range(len(xy)) for j in range(i + 1, len(xy))
             if math.hypot(xy[i][0] - xy[j][0], xy[i][1] - xy[j][1]) < FA.KIT["pipe_gap_m"] - 0.05]
    short = [b for b in gutters if float(b["size"][0]) < 1.5]
    if close or short:
        q["answers"].append({"element": "downpipes", "found": (f"{len(close)} pair(s) of downpipes closer than "
                                                               f"{FA.KIT['pipe_gap_m']:.1f} m" if close else "")
                             + ("; " if close and short else "")
                             + (f"{len(short)} gutter run(s) shorter than 1.5 m (broken-up eaves)" if short else ""),
                             "change": None, "open": True, "ask": "Should the eaves run straight and the pipes stand "
                                                                  "only at the corners?",
                             "options": [AA.option("keep")]})
        q["status"] = "open"
    else:
        q["answers"].append({"element": "downpipes", "found": f"{len(pipes)} downpipe(s), at least "
                             f"{FA.KIT['pipe_gap_m']:.1f} m apart; no broken-up eaves", "change": None})
    for n in notes:
        q["answers"].append({"element": "downpipe", "found": n["reason"], "change": "no pipe at this station",
                             "open": n.get("station_m") is None})
        if n.get("station_m") is None:
            q["status"] = "open"
    return q


# --------------------------------------------------------------------------
# The plan: rooms, their doors and windows
# --------------------------------------------------------------------------

def _rooms_at(building: dict):
    rooms = [r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3]

    def room_at(pt, level_id):
        return next((r for r in rooms if r.get("level_id") == level_id and G.point_in_polygon(pt, r["polygon"])), None)
    return rooms, room_at


def opening_sides(building: dict) -> list[dict]:
    """Every door, window and opening with the rooms on its two sides (pure): ``[{"opening", "type", "a", "b",
    "area_m2"}]``, ``a`` / ``b`` a room id or None (outside); virtual separators link the rooms across their line."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    walls = {w["id"]: w for w in building.get("walls") or []}
    _rooms, room_at = _rooms_at(building)
    out = []
    for o in building.get("openings") or []:
        lv = levels.get(o.get("level_id"))
        if lv is None or o.get("type") not in ("door", "window", "opening"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is not None:
            cx, cy, _ = opening_centre_on_wall(o, w)
            nx, ny = G.unit_normal_left(w["start"], w["end"])
            reach = float(w.get("thickness") or 0.2) / 2.0 + 0.25
        elif o.get("virtual") and len(o.get("line") or []) >= 2:
            (x0, y0), (x1, y1) = o["line"][0][:2], o["line"][-1][:2]
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            nx, ny = G.unit_normal_left((x0, y0), (x1, y1))
            reach = 0.25
        else:
            continue
        a = room_at((cx + nx * reach, cy + ny * reach), lv["id"])
        b = room_at((cx - nx * reach, cy - ny * reach), lv["id"])
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels.values())
        try:
            bottom, top, _ = opening_vertical(o, lv, above)
        except (KeyError, TypeError, ValueError):
            bottom, top = 0.0, 1.2
        out.append({"opening": o, "type": "opening" if o.get("virtual") else o["type"],
                    "a": (a or {}).get("id"), "b": (b or {}).get("id"),
                    "area_m2": max(0.0, float(o.get("width") or 0.0) * (float(top) - float(bottom)))})
    return out


def _rtype(room: Optional[dict]) -> str:
    return str((room or {}).get("room_type") or "").lower()


def _is_stair(room: dict) -> bool:
    text = f"{room.get('id')} {room.get('label') or ''} {room.get('room_subtype') or ''}".lower()
    return any(w in text for w in STAIR_WORDS)


def room_graph(building: dict, sides: Sequence[dict]) -> dict:
    """``{room id: {neighbour id: [opening ids]}}`` through doors, openings and separators, and through the stairs:
    a stair room links to the rooms of the levels above and below that it overlaps (pure)."""
    rooms, _ = _rooms_at(building)
    graph: dict = {r["id"]: {} for r in rooms}
    for s in sides:
        if s["type"] == "window" or not s["a"] or not s["b"] or s["a"] == s["b"]:
            continue
        graph[s["a"]].setdefault(s["b"], []).append(s["opening"]["id"])
        graph[s["b"]].setdefault(s["a"], []).append(s["opening"]["id"])
    order = sorted(building.get("levels") or [], key=lambda lv: float(lv["elevation"]))
    nxt = {a["id"]: b["id"] for a, b in zip(order, order[1:])}
    for st in (r for r in rooms if _is_stair(r)):
        poly = st["polygon"]
        c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
        for lid in (nxt.get(st["level_id"]), next((k for k, v in nxt.items() if v == st["level_id"]), None)):
            for r in rooms:
                if r.get("level_id") == lid and (G.point_in_polygon(c, r["polygon"])
                                                 or any(G.point_in_polygon(p, poly) for p in r["polygon"])):
                    graph[st["id"]].setdefault(r["id"], []).append("stairs")
                    graph[r["id"]].setdefault(st["id"], []).append("stairs")
    # 26 Oct 2026 (real06: "no room of L1 can be reached"): a stair drawn as a piece in a room (not a stair room)
    # links that room with the room of the next level over its footprint
    by_id = {r["id"]: r for r in rooms}
    for f in building.get("furniture") or []:
        if str(f.get("type") or "").lower() not in ("stair", "stairs", "staircase") or f.get("room_id") not in by_id:
            continue
        fp = f.get("footprint") or {}
        c = fp.get("center")
        if not c:
            continue
        here = by_id[f["room_id"]]
        up = nxt.get(here.get("level_id"))
        for r in rooms:
            if r.get("level_id") == up and G.point_in_polygon((float(c[0]), float(c[1])), r["polygon"]):
                graph[here["id"]].setdefault(r["id"], []).append("stairs")
                graph[r["id"]].setdefault(here["id"], []).append("stairs")
    return graph


def entrance_rooms(building: dict, sides: Sequence[dict]) -> list[str]:
    """The rooms just inside the entrance doors (``site.entrances``), else inside any outside door."""
    by_id = {s["opening"]["id"]: s for s in sides}
    ids = [e.get("door_id") for e in (building.get("site") or {}).get("entrances") or []
           if isinstance(e, dict) and not e.get("into_air") and not e.get("below_ground")
           and not (e.get("upper_floor") and e.get("onto"))]           # 26 Oct 2026: a door onto an upper balcony
    out = [r for i in ids if i in by_id for r in (by_id[i]["a"], by_id[i]["b"]) if r]
    if not out:
        out = [r for s in sides if s["type"] == "door" and (s["a"] is None) != (s["b"] is None)
               for r in (s["a"], s["b"]) if r]
    return sorted(set(out))


def _reach(graph: dict, starts: Sequence[str], blocked=lambda rid: False) -> set:
    seen = set(starts)
    todo = list(starts)
    while todo:
        rid = todo.pop()
        for nb in graph.get(rid, {}):
            if nb not in seen:
                seen.add(nb)
                if not blocked(nb):
                    todo.append(nb)
    return seen


def review_circulation(building: dict, sides: Sequence[dict]) -> dict:
    """C1: every room reachable from the entrance; none only through a bedroom (an en-suite bathroom, dressing room
    or balcony of that bedroom excepted)."""
    q = _q("C1")
    rooms, _ = _rooms_at(building)
    by_id = {r["id"]: r for r in rooms}
    graph = room_graph(building, sides)
    starts = entrance_rooms(building, sides)
    if not starts:
        q["answers"].append({"element": "entrance", "found": "no room lies inside an entrance or outside door",
                             "change": None, "open": True, "ask": "Which door is the way into the house?",
                             "options": [AA.option("keep")]})
        q["status"] = "open"
        return q
    everywhere = _reach(graph, starts)
    for rid in sorted(set(by_id) - everywhere):
        q["answers"].append({"element": rid, "found": f"{rid} ({_rtype(by_id[rid])}, {by_id[rid]['level_id']}) cannot "
                             f"be reached from the entrance through any door, opening or stair", "change": None,
                             "open": True, "ask": f"Is a door to {rid} missing in the drawing, or is it a shaft?",
                             "options": [AA.option("retype_room", "it is a shaft or store room", room_type="storage"),
                                         AA.option("keep")]})
        q["status"] = "open"
    free = _reach(graph, starts, blocked=lambda rid: _rtype(by_id.get(rid)) == "bedroom")
    for rid in sorted(everywhere - free):
        if _rtype(by_id[rid]) in ("bathroom", "wc", "balcony", "terrace", "dressing", "closet", "storage"):
            continue                                     # en-suite: reached through its own bedroom
        via = sorted(nb for nb in graph.get(rid, {}) if _rtype(by_id.get(nb)) == "bedroom")
        q["answers"].append({"element": rid, "found": f"{rid} ({_rtype(by_id[rid])}) is reached only through the "
                             f"bedroom {', '.join(via) or 'next to it'}", "change": None, "open": True,
                             "ask": f"Should {rid} have its own door from a hall?",
                             "options": [AA.option("retype_room", "it belongs to the bedroom: a dressing room",
                                                   room_type="dressing"), AA.option("keep")],
                             # 26 Oct 2026: a small untyped room behind a bedroom is its dressing room by default
                             **({"default": "retype_room:dressing"} if _rtype(by_id[rid]) in ("", "other", "unknown")
                                and AA.room_area(by_id[rid]) <= 8.0 else {})})
        q["status"] = "open"
    for rid in sorted(free & set(by_id)):
        q["answers"].append({"element": rid, "found": f"reached from {', '.join(starts)}", "change": None})
    return q


def review_kitchen(building: dict, sides: Sequence[dict]) -> dict:
    q = _q("C2")
    rooms, _ = _rooms_at(building)
    by_id = {r["id"]: r for r in rooms}
    graph = room_graph(building, sides)
    for r in rooms:
        if _rtype(r) != "kitchen":
            continue
        near = [nb for nb in graph.get(r["id"], {}) if _rtype(by_id.get(nb)) in ("living", "dining")]
        two = [nb2 for nb in graph.get(r["id"], {}) for nb2 in graph.get(nb, {})
               if _rtype(by_id.get(nb2)) in ("living", "dining") and _rtype(by_id.get(nb)) == "hall"]
        if near:
            q["answers"].append({"element": r["id"], "found": f"{r['id']} opens onto {', '.join(sorted(near))}",
                                 "change": None})
        else:
            q["answers"].append({"element": r["id"], "found": f"{r['id']} has no door or opening to a living or dining "
                                 f"space" + (f" (through the hall to {', '.join(sorted(set(two)))})" if two else ""),
                                 "change": None, "open": True,
                                 "ask": f"Is {r['id']} open to the living space (the drawing shows a wall), or is "
                                        f"it a separate kitchen on purpose?",
                                 "options": [AA.option("keep", "a separate kitchen on purpose")]})
            q["status"] = "open"
    return q


def review_daylight_air(building: dict, sides: Sequence[dict], answers: Optional[dict] = None) -> tuple[dict, dict]:
    """L1 (habitable rooms: glass >= ``DAYLIGHT_RATIO`` of the floor; a glazed outside door counts half) and L2 (wet
    rooms: a window, else a mechanical extract is assumed). A room whose only window looks into another room is
    W2's question (the window: a reading error?); L1 asks about it again once the window is kept."""
    l1, l2 = _q("L1"), _q("L2")
    answers = answers or {}
    rooms, _ = _rooms_at(building)
    by_id = {r["id"]: r for r in rooms}
    glass: dict = {}
    borrowed: dict = {}
    for s in sides:
        sa, sb = s["a"], s["b"]
        # a window or door onto an open-air room (a terrace, a balcony) lights the room as one onto the outside
        if sa and _rtype(by_id.get(sa)) in OPEN_AIR_TYPES:
            sa = None
        if sb and _rtype(by_id.get(sb)) in OPEN_AIR_TYPES:
            sb = None
        outside = sa is None or sb is None
        room = sa or sb
        if s["type"] == "window" and sa and sb:
            for here, there in ((sa, sb), (sb, sa)):
                borrowed.setdefault(here, []).append((s["opening"]["id"], there))
        if not room or not outside:
            continue
        if s["type"] == "window":
            glass[room] = glass.get(room, 0.0) + s["area_m2"]
        elif s["type"] == "door":
            glass[room] = glass.get(room, 0.0) + 0.5 * s["area_m2"]
    for r in rooms:
        t = _rtype(r)
        area = abs(_area(r["polygon"]))
        g = glass.get(r["id"], 0.0)
        where = RULES._where("room", r.get("level_id"), RULES._centroid(r["polygon"]))
        opts = [AA.option("enlarge_windows", room_id=r["id"]),
                AA.option("retype_room", "a store or service room (no daylight needed)", room_type="storage"),
                AA.option("keep", "keep it as drawn (a dark room on purpose)")]
        if t in HABITABLE and area > 4.0:
            ratio = g / area if area else 0.0
            if ratio + 1e-9 < DAYLIGHT_RATIO:
                inner = borrowed.get(r["id"]) or []
                pending = [wid for wid, _there in inner if (answers.get(f"W2:{wid}") or {}).get("option") != "keep"]
                if not g and inner and pending:
                    # its only window looks into another room: W2 asks whether it is a reading error
                    wid, there = inner[0]
                    l1["answers"].append({"element": r["id"], "found": f"{r['id']} ({t}, {area:.1f} m2) has no window "
                                          f"to the outside; its only window {wid} looks into {there} (W2 asks about "
                                          f"{wid})", "change": None})
                else:
                    l1["answers"].append({"element": r["id"], "found": f"{r['id']} ({t}, {area:.1f} m2) has "
                                          f"{g:.2f} m2 of glass: 1/{(area / g):.0f} of its floor" if g else
                                          f"{r['id']} ({t}, {area:.1f} m2) has no window to the outside",
                                          "change": None, "open": True, "where": where, "options": opts,
                                          "ask": (f"Is {r['id']} a store or service room (then no daylight is "
                                                  f"needed), or should it get a window?" if not g else
                                                  f"Should the windows of {r['id']} be larger?")})
                    l1["status"] = "open"
            else:
                l1["answers"].append({"element": r["id"], "found": f"glass 1/{(area / g):.0f} of the floor",
                                      "change": None})
        if t in WET and g <= 0.0:
            l2["answers"].append({"element": r["id"], "found": f"{r['id']} ({t}) has no window",
                                  "change": "a mechanical extract is assumed (inferred; listed in the report)"})
            l2["status"] = "fixed"
        elif t in WET:
            l2["answers"].append({"element": r["id"], "found": f"a window ({g:.2f} m2)", "change": None})
    return l1, l2


def _area(poly) -> float:
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def review_privacy(building: dict, sides: Sequence[dict]) -> dict:
    q = _q("P1")
    rooms, _ = _rooms_at(building)
    by_id = {r["id"]: r for r in rooms}
    for s in sides:
        if s["type"] != "door" or not s["a"] or not s["b"]:
            continue
        ta, tb = _rtype(by_id.get(s["a"])), _rtype(by_id.get(s["b"]))
        pair = {ta, tb}
        if pair & {"bathroom", "wc", "toilet"} and pair & {"living", "dining", "kitchen"}:
            q["answers"].append({"element": s["opening"]["id"], "found": f"the bathroom door {s['opening']['id']} "
                                 f"opens into {s['a'] if ta in ('living', 'dining', 'kitchen') else s['b']}",
                                 "change": None, "open": True,
                                 "ask": "Keep it (a guest WC by the living room), or should a small lobby screen it?",
                                 "options": [AA.option("keep", "keep: a guest WC by the living room")]})
            q["status"] = "open"
        elif pair & {"bathroom", "wc", "toilet"}:
            q["answers"].append({"element": s["opening"]["id"], "found": f"opens into {s['a'] if ta not in WET else s['b']}",
                                 "change": None})
    return q


def review_room_use(building: dict) -> tuple[dict, dict]:
    """R1 (a bedroom's narrower side at least ``BED_ROOM_MIN_M``) and R2 (each room has its anchor piece:
    ``ANCHORS``)."""
    r1, r2 = _q("R1"), _q("R2")
    rooms, _ = _rooms_at(building)
    pieces: dict = {}
    for f in building.get("furniture") or []:
        if f.get("build") is False:
            continue
        pieces.setdefault(f.get("room_id"), set()).add(str(f.get("type") or ""))
    for r in rooms:
        t = _rtype(r)
        xs, ys = [p[0] for p in r["polygon"]], [p[1] for p in r["polygon"]]
        narrow = min(max(xs) - min(xs), max(ys) - min(ys))
        if t == "bedroom" and narrow < BED_ROOM_MIN_M:
            r1["answers"].append({"element": r["id"], "found": f"{r['id']} is {narrow:.2f} m wide", "change": None,
                                  "open": True, "ask": f"Is {r['id']} a study or a dressing room rather than a "
                                                       f"bedroom?",
                                  "options": [AA.option("retype_room", "a study", room_type="study"),
                                              AA.option("retype_room", "a dressing room", room_type="dressing"),
                                              AA.option("keep")]})
            r1["status"] = "open"
        elif t == "bedroom":
            r1["answers"].append({"element": r["id"], "found": f"{narrow:.2f} m wide", "change": None})
        want = ANCHORS.get(t)
        if want and not (pieces.get(r["id"], set()) & set(want)):
            # 26 Oct 2026: the room's drawn pieces name what it is (a fridge and a counter and no bed: a kitchen)
            have = pieces.get(r["id"], set())
            named = [k for k, anchors in ANCHORS.items() if k != t and have & set(anchors)]
            opts = [AA.option("retype_room", f"it is a {k} (its pieces say so)", room_type=k) for k in named[:2]]
            r2["answers"].append({"element": r["id"], "found": f"{r['id']} ({t}) has no {' / '.join(want)}"
                                  + (f"; its pieces are those of a {' / '.join(named)}" if named else ""),
                                  "change": None, "open": True,
                                  "ask": f"Is {r['id']} really a {t}? (The furnishing adds the missing piece when "
                                         f"the room type is right.)", "options": opts + [AA.option("keep")]})
            r2["status"] = "open"
        elif want:
            r2["answers"].append({"element": r["id"], "found": "has its " + " / ".join(
                sorted(pieces.get(r["id"], set()) & set(want))), "change": None})
    return r1, r2


def review_falls(prep: dict) -> dict:
    """S1: the drops over ``railing_drop`` on the platforms (railings), the roof terraces (parapets and railings)."""
    q = _q("S1")
    site = prep.get("site") or {}
    for pf in site.get("platforms") or []:
        if pf.get("parent") or pf.get("kind") not in ("terrace", "pool"):
            continue
        edges = pf.get("railing_edges") or []
        if edges:
            q["answers"].append({"element": pf["id"], "found": f"{pf['id']}: {len(edges)} edge(s) over a drop of more "
                                 f"than 0.5 m carry a glass railing (max drop {float(pf.get('drop_m') or 0):.2f} m)"
                                 + (f"; the steps leave a gap in it" if pf.get("railing_gaps") else ""),
                                 "change": None})
    for o in (prep.get("roof") or {}).get("openings") or []:
        guard = o.get("guard_height") or o.get("parapet_height")
        q["answers"].append({"element": o["id"], "found": f"roof terrace {o['id']}: guarded to {float(guard):.2f} m "
                             f"(parapet {float(o['parapet_height']):.2f} m" + (" + glass railing)" if o.get("guard_height")
                                                                                 else ")"), "change": None})
    return q


INTO_AIR_DROP_M = 1.0           # an outside door or gap this far over the ground outside, with nothing to step on
LANDING_TOL_M = 0.30            # a platform within this of the door's bottom is its landing
LANDING_PROBE_M = 0.50          # the landing is looked for this far out of the wall face


def outer_gaps(building: dict, prep: dict) -> list[dict]:
    """Every door and bare gap (``opening``) in an outer wall with where it lands (pure; 26 Oct 2026):
    ``[{"rec" (site.outer_openings), "drop", "lands", "upper"}]``: ``lands`` names what is outside at its bottom
    (an open-air room, a site platform, a lower roof, the ground within 0.2 m) or is None; ``drop`` is its bottom
    over the ground outside; ``upper``: its level stands over the ground floor."""
    from wenart.blender import site as S
    from wenart.blender.architect_actions import OPEN_AIR

    levels = building.get("levels") or []
    if not levels or len(prep.get("ground_outline") or []) < 3:
        return []
    site = prep.get("site") or {}
    terrain = site.get("terrain")
    # the ground floor (levels.model.ground_level's rule, not imported: the build's import closure stays small):
    # the level of order 0, else the lowest at or above -0.5 m, else the lowest
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    zero = [lv for lv in order if lv.get("order") == 0]
    up = [lv for lv in order if float(lv["elevation"]) >= -0.5]
    gl = float((zero or up or order)[0]["elevation"])
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: gl)
    rooms = [r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3]
    outlines = prep.get("outlines") or {}
    out = []
    for r in S.outer_openings(building, levels, prep.get("ground_outline") or [], outlines, kinds=("door", "opening")):
        o, lv = r["opening"], r["level"]
        (cx, cy), (ox, oy) = r["centre"], r["outward"]
        probe = (cx + ox * (r["half_t"] + LANDING_PROBE_M), cy + oy * (r["half_t"] + LANDING_PROBE_M))
        bottom = float(r["bottom"])
        lands = None
        room = next((x for x in rooms if x.get("level_id") == lv["id"] and G.point_in_polygon(probe, x["polygon"])),
                    None)
        if room is not None and str(room.get("room_type") or "").lower() in OPEN_AIR:
            lands = f"the {room.get('room_type')} {room['id']}"
        if lands is None:
            pf = next((p for p in site.get("platforms") or [] if len(p.get("polygon") or []) >= 3
                       and isinstance(p.get("z"), (int, float)) and abs(float(p["z"]) - bottom) <= LANDING_TOL_M
                       and G.point_in_polygon(probe, p["polygon"])), None)
            if pf is not None:
                lands = f"the {pf.get('kind', 'platform')} {pf.get('id')}"
        if lands is None:
            low = next((x for x in levels if float(x["elevation"]) < float(lv["elevation"]) - 0.5
                        and len(outlines.get(x["id"]) or []) >= 3 and G.point_in_polygon(probe, outlines[x["id"]])),
                       None)
            if low is not None:
                lands = f"the roof of level {low['id']}"
        drop = bottom - gz(*probe)
        if lands is None and drop <= 0.2:
            lands = "the ground"
        out.append({"rec": r, "drop": drop, "lands": lands,
                    "upper": float(lv["elevation"]) > gl + 0.5, "where": {"kind": o.get("type"),
                                                                          "level_id": lv["id"],
                                                                          "centre": [round(cx, 3), round(cy, 3)]}})
    return out


def review_outside_door_landings(building: dict, prep: Optional[dict] = None) -> tuple[dict, dict]:
    """E1 (every outside door lands on something) and O2 (every gap in an outer wall is a door or a window), on the
    openings as they stand after the answers (26 Oct 2026; the site's entrance records were read before: a door the
    answers turned into a window still asked). A door into the air (over ``INTO_AIR_DROP_M``, nothing outside) on
    an upper floor, and a bare gap in the facade with nothing to land on, are read as windows by default
    (``door_to_window``); the French window with a guard is the other choice."""
    e1, o2 = _q("E1"), _q("O2")
    if prep is None or prep.get("site") is None:
        for e in (building.get("site") or {}).get("entrances") or []:
            if isinstance(e, dict) and (e.get("into_air") or e.get("below_ground")):
                e1["answers"].append({"element": e.get("door_id"), "found": f"door {e.get('door_id')} opens into "
                                      f"the air", "change": None, "open": True,
                                      "ask": f"Is the level of {e.get('door_id')} or of the ground outside it wrong?",
                                      "options": [AA.option("door_to_window"), AA.option("french_window"),
                                                  AA.option("keep")]})
                e1["status"] = "open"
        return e1, o2
    for g in outer_gaps(building, prep):
        o = g["rec"]["opening"]
        oid = o["id"]
        gap = o.get("type") == "opening"
        if g["lands"] is not None and not gap:
            e1["answers"].append({"element": oid, "found": f"lands on {g['lands']}", "change": None})
            continue
        if gap and g["lands"] is not None:
            # a bare gap at the floor onto the ground or a terrace: a passage, or a door the drawing did not show
            o2["answers"].append({"element": oid, "found": f"{oid} is a bare gap onto {g['lands']}", "change": None,
                                  "open": True, "ask": f"Is {oid} a door to {g['lands']} or a window?",
                                  "options": [AA.option("gap_to_door"), AA.option("door_to_window"),
                                              AA.option("keep", "keep: an open passage")], "where": g["where"],
                                  "default": "gap_to_door"})
            o2["status"] = "open"
            continue
        q = o2 if gap else e1
        if g["drop"] < INTO_AIR_DROP_M and not gap:
            q["answers"].append({"element": oid, "found": f"{g['drop']:.2f} m over the ground: steps outside",
                                 "change": None})
            continue
        what = "a bare gap with no door or glass" if gap else "a door"
        over = f"{g['drop']:.2f} m over the ground outside" + (" on an upper floor" if g["upper"] else "")
        default = gap or g["upper"]
        q["answers"].append({"element": oid, "found": f"{oid} is {what} {over}, with nothing outside to step on",
                             "change": None, "open": True,
                             "ask": f"Is {oid} a window (a drawing or reading error), or a French window with a "
                                    f"guard?",
                             "options": [AA.option("door_to_window"), AA.option("french_window"), AA.option("keep")],
                             "where": g["where"], **({"default": "door_to_window"} if default else {})})
        q["status"] = "open"
    return e1, o2


def review_arrival(building: dict, prep: dict) -> tuple[dict, dict]:
    """B1 (a path reaches the main entrance) and B2 (the parking is joined to the paths: else a path is added, as
    A2 does for the decks)."""
    from wenart.blender.site import INFERRED

    b1, b2 = _q("B1"), _q("B2")
    site = prep.get("site") or {}
    paths = [a for a in site.get("areas") or [] if a.get("kind") == "path"]
    ents = [e for e in (building.get("site") or {}).get("entrances") or [] if isinstance(e, dict)]
    main = next((e for e in ents if e.get("main")), ents[0] if ents else None)
    if main is None:
        b1["answers"].append({"element": "entrance", "found": "no entrance door is known", "change": None,
                              "open": True, "ask": "Which door is the main entrance?"})
        b1["status"] = "open"
    else:
        did = main.get("door_id")
        hit = [p["id"] for p in paths if any(did in str(x) for x in [p.get("id")])]
        b1["answers"].append({"element": did, "found": f"main entrance {did}: " + (
            f"reached by {', '.join(hit)}" if hit else ("a path of the site leads to the house" if paths else
                                                         "no path of the site leads to it")), "change": None,
            **({} if hit or paths else {"open": True, "ask": "Where does the street or the gate meet the plot?"})})
        if not hit and not paths:
            b1["status"] = "open"
    half = INFERRED["path_width"] / 2.0
    for pf in site.get("platforms") or []:
        if pf.get("kind") != "parking" or len(pf.get("polygon") or []) < 3 or not paths:
            continue
        if any(_touches(pf["polygon"], p["polygon"]) for p in paths):
            b2["answers"].append({"element": pf["id"], "found": f"parking {pf['id']} meets a path", "change": None})
            continue
        targets = path_targets(paths, half)
        keep = site_keep_out(site, pf["id"])
        best = None
        for s in _edge_points(pf["polygon"], 1.0):
            route = access_path(s, targets, keep, half)
            if route and (best is None or _length(route) < _length(best)):
                best = route
        if best is None:
            b2["answers"].append({"element": pf["id"], "found": f"parking {pf['id']} is not joined to any path",
                                  "change": None, "open": True,
                                  "ask": "Where should people walk from the car to the door?"})
            b2["status"] = "open"
            continue
        reason = f"architect B2: a path from the parking {pf['id']} to the site's path ({_length(best):.1f} m; inferred)"
        site.setdefault("areas", []).extend(path_areas(pf["id"], best, half, reason))
        b2["answers"].append({"element": pf["id"], "found": f"parking {pf['id']} was not joined to the paths",
                              "change": reason.replace("architect B2: ", ""), "fixed": True})
        b2["status"] = "fixed"
    return b1, b2


def _touches(a, b, tol: float = 0.3) -> bool:
    from wenart.blender import geom2d
    return any(G.point_in_polygon(p, b) or geom2d.distance_to_polygon_edges(p, b) <= tol for p in a) or \
        any(G.point_in_polygon(p, a) for p in b)


def _edge_points(poly, step: float):
    """Points just outside a polygon's edges, every ``step`` metres."""
    from wenart.blender import geom2d
    pts = []
    ccw = geom2d.ccw(poly)
    for i in range(len(ccw)):
        a, b = ccw[i], ccw[(i + 1) % len(ccw)]
        length = G.distance(a, b)
        if length < 1e-6:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = uy, -ux
        k = 0.5
        while k < length:
            pts.append((a[0] + ux * k + nx * 0.8, a[1] + uy * k + ny * 0.8))
            k += step
    return pts


def _length(route) -> float:
    return sum(G.distance(a, b) for a, b in zip(route, route[1:]))


# --------------------------------------------------------------------------
# The review
# --------------------------------------------------------------------------

def review(building: dict, prep: dict) -> dict:
    """The architect's review of a whole-building build plan (pure; changes the plan in place): the answers first
    (``prep["architect_applied"]``: ``build.prepare`` carried them out before planning; else here), then A3 (outside
    doors), the plan questions, every rule of ``architect_rules.RULES`` on every element, and the site questions
    (A2 access, A4 light wells, A5, B1-B2); A1 follows with the facade kit (``drainage_answer``)."""
    from wenart.blender import site as S

    if "architect_applied" in prep:
        answers, applied = prep.get("architect_answers") or {}, prep.get("architect_applied") or []
    else:
        answers = AA.answers_of(building)
        applied = AA.apply_answers(building, answers)
    a3, _recs = review_outside_doors(building)
    questions = [a3]
    sides = opening_sides(building)
    questions.append(review_circulation(building, sides))
    questions.append(review_kitchen(building, sides))
    questions += list(review_daylight_air(building, sides, answers))
    questions.append(review_privacy(building, sides))
    questions += list(review_room_use(building))
    questions += list(review_outside_door_landings(building, prep))
    questions.append(review_falls(prep))
    graph = room_graph(building, sides)
    questions += RULES.review(building, prep, sides, graph, entrance_rooms(building, sides), _is_stair, _reach)
    # 25 Oct 2026: the open-air rooms (terrace furniture, terrace doors) and the details (stairs, guards, balustrades)
    from wenart.blender import architect_details as AD
    questions += AD.review(building, prep, sides)
    if prep.get("site") is not None:
        questions += list(review_arrival(building, prep))
        levels = building.get("levels") or []
        outer = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"),
                                 kinds=("door",))
        windows = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"),
                                   kinds=("window",))
        questions.append(review_access(prep, outer))
        questions.append(review_light_wells(prep))
        questions.append(review_deck_doors(building, prep, outer, windows))
    return summary(close_answered(questions, answers, applied), applied)


# --------------------------------------------------------------------------
# The answers: asked once, remembered, acted on (wenart/blender/architect_actions.py)
# --------------------------------------------------------------------------

STORE_WORDS = AA.STORE_WORDS


def apply_answers(building: dict, brief_answers: Optional[dict] = None) -> dict:
    """The answers for ``building`` (``architect_actions.answers_of``) carried out on it (in place); returns them
    (normalised) and keeps what was done in ``building["_architect_applied"]``."""
    answers = AA.answers_of(building, brief_answers)
    building["_architect_applied"] = AA.apply_answers(building, answers)
    return answers


def _who(rec: dict) -> str:
    by = rec.get("by", "user")
    return "you" if by == "user" else ("the architect's default" if by == "architect" else
                                        "Argus, the auditor" if by == "argus" else "the AI architect")


DEFAULT_ROUNDS = 6              # a default may open a question that has a default of its own; a chain moves on


def chain_of(answer: dict) -> list[str]:
    """26 Oct 2026 (user: "make the AI architect a lot more smart and let it take decisions more"): the choices the
    architect tries in turn on an open point: its ``default``, then its ``fallback`` choices (a window that cannot move
    to an outer wall is kept as a borrowed-light window; a doorway a drawn counter fills becomes a serving window)."""
    out = []
    for c in ([answer.get("default")] if answer.get("default") else []) + list(answer.get("fallback") or []):
        if c and c not in out:
            out.append(c)
    return out


def defaults_of(review_rec: dict, answers: dict, tried: Optional[dict] = None) -> dict:
    """The safe default answer of every open point that has one (``chain_of``: its default, then its fallbacks) and
    no answer of the AI or the user (26 Oct 2026, user: "I need ai models to see understand and fix everything before
    even I look at it"): a door into the air on an upper floor and a bare gap in the facade become windows, a low sill
    gets a guard, a door gets its floor's threshold, a wall-hung basin hangs at its working height, a piece
    leaves a doorway or a window. A point still open under the architect's own answer (it could not be carried out)
    gets the next choice of its chain that ``tried`` (``{key: [choices]}``) does not hold. ``build.prepare`` carries
    them out (``by: architect``, the lowest source: the AI's and the user's answers win); the points without a safe
    default stay for the AI architect and the user."""
    tried = tried or {}
    out = {}
    for q in review_rec.get("questions") or []:
        for a in q.get("answers") or []:
            key = f"{q['id']}:{a['element']}"
            if not a.get("open"):
                continue
            prev = answers.get(key)
            if prev is not None and prev.get("by") != "architect":
                continue                                  # the AI's or the user's answer stands
            done = set(tried.get(key) or []) | ({prev.get("choice")} if prev and prev.get("choice") else set())
            nxt = next((c for c in chain_of(a) if c not in done), None)
            opt = next((o for o in a.get("options") or [] if o.get("choice") == nxt), None) if nxt else None
            if opt is None:
                continue
            out[key] = {"option": opt["id"], "params": dict(opt.get("params") or {}), "by": "architect",
                        "choice": opt["choice"], "answer": "the safe default" if not done else
                        f"the next safe fix ({', '.join(sorted(done))} could not be done)",
                        "reason": a.get("found"), "where": a.get("where")}
    return out


def open_keys(review_rec: dict, severity: Optional[str] = None, undecided: bool = False) -> set:
    """The keys (``rule:element``) of the open points of a review record (of one severity); ``undecided``: only those
    with no safe fix of their own (``chain_of`` empty: they stay for the AI and the user)."""
    return {f"{q['id']}:{a['element']}" for q in review_rec.get("questions") or [] for a in q.get("answers") or []
            if a.get("open") and (severity is None or q.get("severity", "minor") == severity)
            and not (undecided and chain_of(a))}


def close_answered(questions: list[dict], answers: dict, applied: Sequence[dict] = ()) -> list[dict]:
    """An open point that has an answer is not asked again: it shows the answer and what it changed. An answer that
    could not be carried out leaves the point open with the reason; an answer whose change settled the check shows
    on the (now passing) element."""
    done = {r["key"]: r for r in applied}
    by_el = {(r["rule"], r["element"]): r for r in applied}
    for q in questions:
        for a in q["answers"]:
            key = f"{q['id']}:{a['element']}"
            rec = done.get(key) or by_el.get((q["id"], a["element"]))
            if rec is None and key in answers:
                rec = {"key": key, "option": answers[key].get("option", "keep"), "ok": True, "change": None,
                       "by": answers[key].get("by", "user"), "answer": answers[key].get("answer")}
            if rec is None:
                continue
            label = AA.ACTIONS.get(rec["option"], rec["option"])
            words = f" (\"{rec['answer']}\")" if rec.get("answer") else ""
            if a.get("open") and rec.get("ok"):
                a["open"] = False
                a.pop("ask", None)
                a["answered"] = True
                a["change"] = f"answered by {_who(rec)}{words}: {label}" + (f" -> {rec['change']}"
                                                                            if rec.get("change") else "")
            elif a.get("open"):
                a["note"] = f"{_who(rec)} answered {rec['option']}{words}, but it could not be done: {rec['change']}"
            elif rec.get("ok") and rec.get("change") and not a.get("change"):
                a["answered"] = True
                a["change"] = f"answered by {_who(rec)}{words}: {rec['change']}"
        if q["status"] == "open" and not any(a.get("open") for a in q["answers"]):
            q["status"] = "answered"
    # 26 Oct 2026: an answer whose change removed its element from the question (a door that became a window is no
    # longer asked E1) is still listed under its rule, so every change shows in the report
    seen = {f"{q['id']}:{a['element']}" for q in questions for a in q["answers"]}
    by_id = {q["id"]: q for q in questions}
    for rec in applied:
        if str(rec.get("rule") or "").startswith("AI.") and "A0" not in by_id:
            # 26 Oct 2026 (user: "let it take decisions more"): the AI architect's own decisions (``AI.<action>:<el>``)
            by_id["A0"] = {"id": "A0", "topic": "the AI architect's own decisions", "scope": "building",
                           "severity": "minor", "question": "What did the AI architect decide on its own?",
                           "why": "it looked at each floor of the model and changed what it judged wrong; code checked "
                                  "every change", "answers": [], "status": "answered"}
            questions.append(by_id["A0"])
        rule = "A0" if str(rec.get("rule") or "").startswith("AI.") else rec.get("rule")
        if not rec.get("ok") or not rec.get("change") or rec["key"] in seen or rule not in by_id:
            continue
        q = by_id[rule]
        label = AA.ACTIONS.get(rec["option"], rec["option"])
        words = f" (\"{rec['answer']}\")" if rec.get("answer") else ""
        q["answers"].append({"element": rec["element"], "found": "settled by its answer", "answered": True,
                             "change": f"answered by {_who(rec)}{words}: {label} -> {rec['change']}"})
        seen.add(rec["key"])
    return questions


def status_of(a: dict) -> str:
    if a.get("open"):
        return "open"
    if a.get("answered"):
        return "answered"
    if a.get("change"):
        return "changed"
    return "ok"


ORDER = ("B1", "B2", "A2", "A5", "E1", "O2", "C1", "C2", "T1", "T2", "L1", "W2", "L2", "W3", "P1", "R1", "R2", "R3",
         "R4", "R5", "O1", "D1", "D2", "D4", "D5", "D6", "D3", "X1", "F5", "F1", "F2", "F3", "F4", "H1", "U1", "S4",
         "S2", "S3", "K1", "K2", "K3", "S1", "A3", "A4", "A1", "G1")


def summary(questions: list[dict], applied: Optional[Sequence[dict]] = None) -> dict:
    """The review record: the questions in the architect's order (``ORDER``), each with its counts, and the totals:
    ``asked`` (every element checked by every rule), ``changes``, ``open``, ``answered``."""
    order = {qid: k for k, qid in enumerate(ORDER)}
    questions = sorted(questions, key=lambda q: order.get(q["id"], 99))
    total = {"ok": 0, "changed": 0, "open": 0, "answered": 0}
    for q in questions:
        c = {"ok": 0, "changed": 0, "open": 0, "answered": 0}
        for a in q["answers"]:
            if a.get("open") and not a.get("options"):
                a["options"] = [AA.option("keep")]
            st = status_of(a)
            a["status"] = st
            c[st] += 1
        q["counts"] = dict(c, asked=len(q["answers"]))
        for k in total:
            total[k] += c[k]
    out = {"questions": questions, "asked": sum(len(q["answers"]) for q in questions),
           "changes": sum(1 for q in questions for a in q["answers"] if a.get("change")),
           "open": total["open"], "answered": total["answered"], "rules": len(questions)}
    if applied is not None:
        out["applied"] = list(applied)
    return out


def compact(review_rec: dict) -> dict:
    """The record without the passing answers (the scene manifest's copy; ``architect.json`` keeps them all)."""
    out = {k: v for k, v in review_rec.items() if k != "questions"}
    out["questions"] = [dict({k: v for k, v in q.items() if k != "answers"},
                             answers=[a for a in q["answers"] if a.get("status", status_of(a)) != "ok"])
                        for q in review_rec.get("questions") or []]
    return out


def open_points(review_rec: dict) -> list[tuple[dict, dict]]:
    """``[(question, answer)]`` still open, the major ones first."""
    out = [(q, a) for q in review_rec.get("questions") or [] for a in q["answers"] if a.get("open")]
    out.sort(key=lambda qa: (qa[0].get("severity") != "major", order_of(qa[0]["id"]), str(qa[1]["element"])))
    return out


def order_of(qid: str) -> int:
    return ORDER.index(qid) if qid in ORDER else 99


MD_OPEN_MAX = 150               # the report lists this many open points (all of them are in architect.json)
MD_CHANGES_MAX = 200


def report_md(review_rec: dict, project: str = "") -> str:
    """The review as markdown, for any size of building: the totals, a table of every rule (elements asked, fine,
    changed, answered, open), the open questions for you (the first ``MD_OPEN_MAX``, major first, with their answer
    keys and options) and what was changed (the first ``MD_CHANGES_MAX``); every answer is in ``architect.json``."""
    qs = review_rec.get("questions") or []
    lines = [f"# Architect's review{': ' + project if project else ''}", "",
             f"{review_rec.get('asked', sum(len(q['answers']) for q in qs))} questions asked ({len(qs)} rules x the "
             f"elements they apply to), {review_rec.get('changes', 0)} change(s), {review_rec.get('answered', 0)} "
             f"answered, {review_rec.get('open', 0)} open point(s).", "",
             "| rule | topic | asked | fine | changed | answered | open |", "|---|---|---|---|---|---|---|"]
    for q in qs:
        c = q.get("counts") or {}
        lines.append(f"| {q['id']} | {q['topic']} | {c.get('asked', len(q['answers']))} | {c.get('ok', 0)} | "
                     f"{c.get('changed', 0)} | {c.get('answered', 0)} | {c.get('open', 0)} |")
    lines.append("")
    concerns = open_points(review_rec)
    if concerns:
        lines += ["## The architect's questions for you", ""]
        for k, (q, a) in enumerate(concerns[:MD_OPEN_MAX], 1):
            opts = ", ".join(f"`{o['id']}`" + (f" ({o['label']})" if o.get("label") and o["id"] == "keep" else "")
                             for o in a.get("options") or [])
            lines.append(f"{k}. **{q['id']} {q['topic']}** ({q.get('severity', 'minor')}): {a['found']}."
                         + (f" *{a['ask']}*" if a.get("ask") else "") + f" Answer key `{q['id']}:{a['element']}`"
                         + (f"; options {opts}" if opts else "") + (f". Note: {a['note']}" if a.get("note") else ""))
        if len(concerns) > MD_OPEN_MAX:
            lines.append(f"... and {len(concerns) - MD_OPEN_MAX} more open point(s) in architect.json.")
        lines += ["", "Answers go into `projects/<project>/architect_answers.json` as `{\"answers\": {\"<key>\": "
                  "{\"option\": \"<option>\", \"answer\": \"<your words>\"}}}`; the next run carries them out and "
                  "does not ask again. The AI architect on the pod answers the rest it can settle (checked by code).",
                  ""]
    changed = [(q, a) for q in qs for a in q["answers"] if a.get("change")]
    if changed:
        lines += ["## What the architect changed or settled", ""]
        for q, a in changed[:MD_CHANGES_MAX]:
            lines.append(f"- **{q['id']} {a['element']}**: {a['found']} -> {a['change']}")
        if len(changed) > MD_CHANGES_MAX:
            lines.append(f"- ... and {len(changed) - MD_CHANGES_MAX} more in architect.json")
        lines.append("")
    failed = [r for r in review_rec.get("applied") or [] if not r.get("ok") and not r.get("skipped")]
    if failed:
        lines += ["## Answers that could not be carried out", ""]
        lines += [f"- `{r['key']}` ({r['option']}, by {_who(r)}): {r.get('change')}" for r in failed]
        lines.append("")
    skipped = [r for r in review_rec.get("applied") or [] if r.get("skipped")]
    if skipped:
        lines += ["## Answers about elements not in this reading of the plan", ""]
        lines += [f"- `{r['key']}` ({r['option']}, by {_who(r)}): {r.get('change')}" for r in skipped]
        lines.append("")
    lines += ["## The questions", ""]
    for q in qs:
        c = q.get("counts") or {}
        lines.append(f"- **{q['id']} {q['topic']}** ({q.get('severity', 'minor')}, {q['status']}): *{q['question']}*"
                     + (f" Why: {q['why']}." if q.get("why") else "")
                     + f" Asked of {c.get('asked', len(q['answers']))} element(s).")
    # 25 Oct 2026: the user's requests and corrections as lessons, and how their rules came out here
    from wenart.blender import architect_lessons as LS
    lines += LS.report_md(review_rec)
    lines.append("")
    return "\n".join(lines)
