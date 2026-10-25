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


def _q(qid: str) -> dict:
    return dict(next(q for q in QUESTIONS if q["id"] == qid), answers=[], status="ok")


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
        if pf.get("outside_access") in ("path", "on_path"):
            q["answers"].append({"element": pf["id"], "found": found, "change": "reached from outside: its steps and "
                                 "a path to the site's paths (A2); the windows stay as drawn"})
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
    for n in notes:
        q["answers"].append({"element": "downpipe", "found": n["reason"], "change": "no pipe at this station",
                             "open": n.get("station_m") is None})
        if n.get("station_m") is None:
            q["status"] = "open"
    return q


# --------------------------------------------------------------------------
# The review
# --------------------------------------------------------------------------

def review(building: dict, prep: dict) -> dict:
    """The architect's review of a whole-building build plan (pure; changes the plan in place): A3 (outside doors),
    A2 (access), A4 (light wells); A1 follows with the facade kit (``drainage_answer``)."""
    from wenart.blender import site as S

    a3, _recs = review_outside_doors(building)
    questions = [a3]
    if prep.get("site") is not None:
        levels = building.get("levels") or []
        outer = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"),
                                 kinds=("door",))
        windows = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"),
                                   kinds=("window",))
        questions.append(review_access(prep, outer))
        questions.append(review_light_wells(prep))
        questions.append(review_deck_doors(building, prep, outer, windows))
    return summary(questions)


def summary(questions: list[dict]) -> dict:
    order = {q["id"]: k for k, q in enumerate(QUESTIONS)}
    questions = sorted(questions, key=lambda q: order.get(q["id"], 99))
    return {"questions": questions, "changes": sum(1 for q in questions for a in q["answers"] if a.get("change")),
            "open": sum(1 for q in questions for a in q["answers"] if a.get("open"))}


def report_md(review_rec: dict, project: str = "") -> str:
    """The review as markdown: per question the architect's question, then each element, what was found and what
    was changed."""
    lines = [f"# Architect's review{': ' + project if project else ''}", "",
             f"{review_rec.get('changes', 0)} change(s), {review_rec.get('open', 0)} open point(s).", ""]
    for q in review_rec.get("questions") or []:
        lines += [f"## {q['id']} {q['topic']} ({q['status']})", "", f"*{q['question']}*", ""]
        if not q["answers"]:
            lines.append("- nothing to look at in this building")
        for a in q["answers"]:
            lines.append(f"- **{a['element']}**: {a['found']}" + (f" -> {a['change']}" if a.get("change") else "")
                         + (f" **Question for you: {a['ask']}**" if a.get("ask") else "")
                         + (" (open)" if a.get("open") and not a.get("ask") else ""))
        lines.append("")
    return "\n".join(lines)
