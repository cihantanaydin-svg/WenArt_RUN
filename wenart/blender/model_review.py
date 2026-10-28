"""The review of the 3D model itself (26 Oct 2026, user: "reviewing the 3d model itself could be better solution rather
than individual renders investigate decide apply").

What: ``review(built, scene_manifest, prep=None)`` measures the model as it was built (the building as built,
``scene/building_built.json``; the scene manifest's world boxes of every piece; the build plan of ``build.prepare``
and the facade kit of ``facade.articulation_plan``: gutters, downpipes, guards) and returns
``{"findings": [...], "checks": {id: {"checked", "failed"}}}``; each finding is a code-critic violation
``{check, severity, target, room_id, message, metrics}``:

- M1 every door and doorless opening stands on the floor of the rooms it joins (its built bottom vs their floors), and
  the floors a door joins differ by at most one step;
- M2 every fixture and table works at its height (the built top of a washbasin, a kitchen worktop, a dining table, a
  desk over its room's floor); 27 Oct 2026: no piece whose back stands on a window's wall rises over that window's
  sill (``fit.window_cap``: a tall chest covered a child's room window);
- M3 every outside opening whose bottom is less than ``GUARD_SILL_M`` over its floor and more than ``DROP_M`` over
  the ground outside has a guard (the facade kit's guard) or lands on a balcony, terrace or platform;
- M4 no door or bare gap of an upper floor opens onto nothing (``architect.outer_gaps`` on the built openings);
- M5 the rain water: downpipes at least ``facade.KIT["pipe_gap_m"]`` apart, at most one per
  ``area_per_pipe_m2`` of roof (at least 2), no gutter run shorter than ``GUTTER_MIN_M``;
- M6 one door and window language: one library model family per opening category of the building;
- M7 the rooms make sense: a kitchen has its run, a bedroom its bed, a bathroom its WC and basin, a living room its
  seating; one dining table per room;
- M8 the entrances make sense (26 Oct 2026, real06: two flights ran into each other in the inner corner of an L and
  their handrails crossed in front of the small door; user: "these sections not making sense, the AI inspector needs
  to make sense of this"): the steps and landings of two doors never overlap (critical), no handrail crosses another
  door's approach zone (``site.door_approach``: the door's width + 0.1 m on each side, 1.0 m out; critical), no ramp
  passes in front of another door (major), no steps or landing in front of a door into a garage or carport (major).
  Measured on the steps as built (``prep["site"]["inferred"]``: ``site.entrance_layout``);
- M9 the visitor's walk on the built floors (27 Oct 2026, real06's first floor: the stair arrived on a strip by the
  outer wall that its opening cut off from the hall; user: "Needs a pathway here, how will the people go up to 2nd
  floor otherwise?" and "Make argus catch these kind of things before me"; ``stair_access.walk_review``): (a) every
  stair's arrival (on the level above) and start (on its own level) reach the level's main floor through a 0.80 m way
  (critical when they lead into a pocket no way joins to any room, major when only to rooms off the main floor);
  (b) every door of a room is reached on foot from the room's main floor (major; names what stands in front of it:
  a floor opening, a fixed piece, a narrow floor); (c) no part of a floor is cut off by a floor opening with no stair
  or door joining it to the rest (critical); (d) (with the scene manifest; user on real06's ground floor: "This stairs
  not making any sense") the space under every stair lower than 2.0 m is closed and every landing high enough to walk
  under is carried, as built (``stair_undersides``: major). Each finding names the element, the areas and the rooms
  measured and the fix (the assumed stair flipped by the architect's K4, the opening cut to the flights, half landing
  and headroom, the underside closed);
- M10 the outdoor spaces as a visitor uses them (27 Oct 2026, ``outdoor_review``): a door onto every balcony and
  veranda, a guard on every open edge over a drop, an outdoor floor of its kind (never the garden paving), a covered
  kind covered, no roof at a balcony's floor level to step onto, one post language.
- M11 the roof as the roof plan draws it (27 Oct 2026, real06: the roof plan drew the hip roof over the first-floor
  balcony, the model left the balcony open to the sky; user: "Make argus catch these kind of things before me"): the
  built roof's footprint (``prep["roof"]``: its outline without its terrace openings) against the eaves loop the roof
  plan draws (``roof.roof_plan_outline``, put on the walls by ``wenart.sheets.to_building``): an outline assumed (the
  walls + overhang) while a roof plan draws it is ``major`` (kind ``misread``); a drawn outdoor space the drawn roof
  covers and the built roof leaves open (``M11_OPEN_M2`` / ``M11_OPEN_SHARE``) is ``major`` (kind ``lost``); a built
  footprint whose overlap with the drawn one (IoU) is under ``M11_IOU_MIN`` is ``major``; a lower roof the roof plan
  draws (a porch or veranda roof) with no built roof over most of it is ``major`` (kind ``lost``). Polygon areas
  are exact (convex pieces clipped against each other, ``overlap_area``): no shapely inside Blender;
- M12 doors side by side (27 Oct 2026, user on real06's dressing room: "doors next to each other not making sense";
  ``door_spacing``): no two doors of a floor whose openings overlap or whose frames touch (less than two frames of wall
  between them on one wall line, or frames meeting at a corner), no two doors between the same two rooms closer than a
  door's width, no two swing leaves into one room that sweep over each other; and (user: "Not every opening inside the
  house requires a door or a window") no passage drawn open between two rooms with a leaf (unless a room needs
  privacy), glass or a guard (with no drop) a decision gave it.
- M15 outdoor rooms dressed for outside (28 Oct 2026, user on real04 run 20261028-005318-full, its roof terrace:
  "makes no sense to have that table with the carpet outside, that's outside area"; ``outdoor.review``): no rug,
  runner or carpet on the floor of an open-air room or an outdoor space, and no library model of an outdoor type
  (table, chair, sofa ...) there that is not made for outside (``outdoor.outdoor_ready``). Major; kind ``no_sense``.
- M16 enough ceiling light (28 Oct 2026, same run, user: "More lights from the ceiling needed"; its 50.9 m² living and
  dining room had one pendant; ``ceiling_lights.review``): every lit room holds the ceiling lights the lighting rule
  hangs there (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run,
  and the lumen method's count for its floor); major with no light, under half of them or an unlit table or bed,
  else minor; kind ``taste``.

Why: the renders show what their cameras frame (real06: 34 views; many walls, rooms' far sides and facades never in a
frame), and a vision model judging a height or a gap from a perspective image is a guess. The model holds every
element with its exact place: measured here, every element is checked, on every floor, before any render time is
spent, and every finding names its element and the number that fails. The vision models keep what only an image
shows (the look, the style, odd shapes). The findings go to the agent loop as code findings (``critic_code``, family
``model``: each has a cause and its tools, or the stage that owns it) and to the inspector's report.

How: pure Python on dicts (the build's own functions: ``shell.opening_vertical``, ``shell.room_floor_z``,
``site.outer_openings``, ``facade.articulation_plan``); a part that cannot be measured (no manifest, no plan) is
recorded as ``unavailable`` in ``checks``, never guessed.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

DOOR_TOL_M = 0.03               # a door's bottom within this of its floor stands on it
STEP_MAX_M = 0.20               # two floors joined by a door differ by at most one step (more needs a drawn stair)
GUARD_SILL_M = 0.85             # an opening whose bottom is lower over its floor needs a guard over a drop ...
DROP_M = 1.0                    # ... of this much to the ground outside
GUTTER_MIN_M = 1.5              # a gutter run shorter than this is broken-up eaves ...
GUTTER_DRAWN_TOL_M = 0.15       # ... unless it runs along a drawn eaves edge of its length (within a gutter's width)
# type -> (lowest top, highest top) over the room's floor, the working height a visitor sees at once
WORKING_TOPS = {"washbasin": (0.78, None), "kitchen_counter": (0.84, 0.97), "sink_kitchen": (0.80, 1.30),
                "table_dining": (0.68, 0.82), "desk": (0.68, 0.82)}
ANCHORS = {"kitchen": ("kitchen_counter", "sink_kitchen", "stove", "cooktop"),
           "bedroom": ("bed_double", "bed_single", "bed", "bed_bunk"),
           "living": ("sofa", "sofa_corner", "armchair"),
           "bathroom": ("toilet",)}
BATH_BASIN = ("washbasin", "vanity", "bathroom_vanity")
CHECKS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12", "M15", "M16")
# M11 (27 Oct 2026): the roof as the roof plan draws it. Physical reasons:
M11_IOU_MIN = 0.90              # the built roof's footprint matches the drawn eaves loop within a gutter's width all
                                # round (a 0.15 m band around a 10 x 15 m roof is about 5 % of it)
M11_OPEN_M2 = 1.0               # a drawn-covered outdoor space left open over more than a chair's room ...
M11_OPEN_SHARE = 0.25           # ... or a quarter of it is a roof the model lost
M11_DRAWN_SHARE = 0.5           # a space is drawn covered when the drawn roof lies over at least half of it
M11_CLEAR_M = 2.1               # a roof is over a space when its eaves stand a door's clear height over its floor
M11_OTHER_SHARE = 0.5           # a drawn lower roof is built when built roofs lie over at least half of it
# M9: the fixes the findings name (the architect's K4 carries out the first at build time when the stair is assumed)
FIX_STAIR = ("flip the assumed stair (its rise direction or the end of its half landing: architect K4 at build) or cut "
             "its floor opening to the flights, the half landing and the headroom, never over the arrival floor")
FIX_DOOR = {"opening": "cut the floor opening back to the stair's flights, half landing and headroom (architect K4), "
                       "so a 0.80 m way passes in front of the door",
            "pieces": "move the piece off the door's approach, or the door off the piece",
            "narrow": "widen the floor in front of the door to a 0.80 m way",
            "part": "join the part of the room the door opens onto to the room's main floor by a 0.80 m way"}
FIX_PART = ("cut the floor opening back to the stair's flights, half landing and headroom (never the arrival floor), "
            "or join the part by a door")
REVIEW_JSON = "model_review.json"          # beside the scene (outputs/<p>/scene/)
REVIEW_MD = "model_review.md"


def _v(check: str, severity: str, target, message: str, room_id=None, kind: Optional[str] = None, **metrics) -> dict:
    out = {"check": check, "severity": severity, "target": target, "room_id": room_id, "message": message,
           "metrics": dict(metrics, model_review=True)}
    if kind:
        out["kind"] = kind               # the problem kind (wenart.audit.kinds) when the check's default is not it
    return out


def _levels(built: dict) -> dict:
    return {lv["id"]: lv for lv in built.get("levels") or [] if lv.get("id")}


def _room_floors(built: dict) -> dict:
    from wenart.blender.shell import room_floor_z
    levels = _levels(built)
    out = {}
    for r in built.get("rooms") or []:
        lv = levels.get(r.get("level_id"))
        if lv is not None:
            try:
                out[r["id"]] = float(room_floor_z(r, lv))
            except (KeyError, TypeError, ValueError):
                out[r["id"]] = float(lv.get("elevation") or 0.0)
    return out


def doors_on_floors(built: dict, floors: dict) -> tuple[list[dict], int]:
    """M1: the built bottom of every door and doorless opening vs the floors of the rooms on its two sides."""
    from wenart.blender import architect_actions as AA
    from wenart.blender.shell import opening_vertical
    levels = _levels(built)
    plan = AA.Plan(built)
    out, n = [], 0
    for o in built.get("openings") or []:
        if o.get("type") not in ("door", "opening") or o.get("level_id") not in levels or not o.get("wall_id"):
            continue
        lv = levels[o["level_id"]]
        above = any(float(x.get("elevation") or 0.0) > float(lv.get("elevation") or 0.0) for x in levels.values())
        try:
            bottom = float(opening_vertical(o, lv, above)[0])
        except (KeyError, TypeError, ValueError):
            continue
        sides = [r for r in AA.window_sides(plan, o) if r is not None and not AA.Plan.is_outside(r)]
        zs = [floors[r["id"]] for r in sides if r["id"] in floors]
        if not zs:
            continue
        n += 1
        if bottom - max(zs) > DOOR_TOL_M:
            out.append(_v("M1", "critical", o["id"], f"{o['id']} ({o.get('type')}) starts {bottom - max(zs):.2f} m over "
                          f"the floor of {', '.join(r['id'] for r in sides)}: the door is raised off its floor",
                          sides[0]["id"], bottom_z=round(bottom, 3), floors=[round(z, 3) for z in zs]))
        elif len(zs) == 2 and abs(zs[0] - zs[1]) > STEP_MAX_M and not o.get("steps"):
            # a door between two rooms whose floors differ by more than one step: half a metre of wall under the door
            # seen from the lower room (real06: the kitchen floor read 0.5 m up from a misread mark)
            low = sides[0] if zs[0] < zs[1] else sides[1]
            out.append(_v("M1", "critical", o["id"], f"{o['id']} ({o.get('type')}) joins floors {abs(zs[0] - zs[1]):.2f} m "
                          f"apart: from {low['id']} the door starts {abs(zs[0] - zs[1]):.2f} m up, with no stair",
                          low["id"], bottom_z=round(bottom, 3), floors=[round(z, 3) for z in zs]))
        elif min(zs) - bottom > DOOR_TOL_M:
            out.append(_v("M1", "major", o["id"], f"{o['id']} ({o.get('type')}) starts {min(zs) - bottom:.2f} m under "
                          f"the floor of its rooms: it is sunk into the floor", sides[0]["id"],
                          bottom_z=round(bottom, 3), floors=[round(z, 3) for z in zs]))
    return out, n


SILL_COVER_M = 0.03              # a top this far over a window's sill covers the window's glass


def over_sills(manifest: Optional[dict], built: dict, floors: dict) -> tuple[list[dict], int]:
    """M2 (27 Oct 2026, user on real06: "this in front of a window not making sense"): a built piece in front of a
    window (the fit's record ``window_cap``: ``fit.window_front``) whose top rises ``SILL_COVER_M`` over the window's
    sill covers it (major; the next fit takes a lower model). Pure (no geometry library: it runs inside Blender)."""
    pieces = {f.get("id"): f for f in built.get("furniture") or []}
    out, n = [], 0
    for ob in (manifest or {}).get("objects") or []:
        pid = ob.get("element_id") or ob.get("wenart_id")
        if ob.get("kind") != "furniture" or pid not in pieces or not isinstance(ob.get("box3d"), dict):
            continue
        front = pieces[pid].get("window_cap") if isinstance(pieces[pid].get("window_cap"), dict) else None
        rid = ob.get("room_id")
        box = ob["box3d"]
        if front is None or rid not in floors or not box.get("center") or not box.get("size"):
            continue
        n += 1
        sill = float(front["sill_m"])
        top = float(box["center"][2]) + float(box["size"][2]) / 2.0 - floors[rid]
        if top > sill + SILL_COVER_M:
            out.append(_v("M2", "major", pid, f"{pid} ({ob['type']}) stands in front of "
                          f"{', '.join(front.get('windows') or ['a window'])} with its top at {top:.2f} m over the "
                          f"floor: it covers the window (sill {sill:.2f} m); a lower model of its type", rid,
                          rule="window", top_m=round(top, 3), sill_m=round(sill, 3),
                          windows=list(front.get("windows") or [])))
    return out, n


def working_heights(manifest: Optional[dict], floors: dict) -> tuple[list[dict], int]:
    """M2: the built top of every fixture and table of ``WORKING_TOPS`` over its room's floor."""
    out, n = [], 0
    for ob in (manifest or {}).get("objects") or []:
        if ob.get("kind") != "furniture" or ob.get("type") not in WORKING_TOPS or not isinstance(ob.get("box3d"), dict):
            continue
        box = ob["box3d"]
        rid = ob.get("room_id")
        if rid not in floors or not box.get("center") or not box.get("size"):
            continue
        top = float(box["center"][2]) + float(box["size"][2]) / 2.0 - floors[rid]
        low, high = WORKING_TOPS[ob["type"]]
        pid = ob.get("element_id") or ob.get("wenart_id")
        n += 1
        if top < low - 1e-6:
            sev = "critical" if ob["type"] in ("washbasin", "kitchen_counter") else "major"
            out.append(_v("M2", sev, pid, f"{pid} ({ob['type']}) has its top at {top:.2f} m over the floor: a "
                          f"{ob['type']} works at {low:.2f} m or more (a basin at knee height)", rid, top_m=round(top, 3),
                          low_m=low))
        elif high is not None and top > high + 1e-6:
            out.append(_v("M2", "major", pid, f"{pid} ({ob['type']}) has its top at {top:.2f} m over the floor, over "
                          f"its working height ({high:.2f} m)", rid, top_m=round(top, 3), high_m=high))
    return out, n


def guards_and_air(built: dict, prep: dict, plan_boxes: list) -> tuple[list[dict], list[dict], int, int]:
    """M3 (a guard before every low opening over a drop) and M4 (no upper-floor door or gap onto nothing)."""
    from wenart.blender import architect as AR
    from wenart.blender import site as S
    guarded = {str(b.get("parent")) for b in plan_boxes if b.get("kind") in ("guard_glass", "railing")}
    m3, m4, n3, n4 = [], [], 0, 0
    gaps = {g["rec"]["opening"]["id"]: g for g in AR.outer_gaps(built, prep)}
    for g in gaps.values():
        o = g["rec"]["opening"]
        n4 += 1
        if g["lands"] is None and g["upper"] and g["drop"] >= DROP_M and not isinstance(o.get("guard"), dict):
            m4.append(_v("M4", "critical", o["id"], f"{o['id']} ({o.get('type')}) on an upper floor opens onto nothing "
                         f"{g['drop']:.2f} m over the ground (no balcony, terrace or steps)", None,
                         drop_m=round(g["drop"], 3)))
    levels = _levels(built)
    site = prep.get("site") or {}
    terrain = site.get("terrain")
    if len(prep.get("ground_outline") or []) < 3:
        return m3, m4, n3, n4
    for rec in S.outer_openings(built, list(levels.values()), prep.get("ground_outline") or [], prep.get("outlines"),
                                kinds=("door", "window", "opening")):
        o, lv = rec["opening"], rec["level"]
        floor = float(lv.get("elevation") or 0.0)
        if rec["bottom"] - floor >= GUARD_SILL_M:
            continue
        (cx, cy), (ox, oy) = rec["centre"], rec["outward"]
        gz = S.ground_z(terrain, cx + ox * 1.0, cy + oy * 1.0) if terrain else floor
        drop = rec["bottom"] - gz
        if drop < DROP_M:
            continue
        gap = gaps.get(o["id"])
        if gap is not None and gap["lands"] is not None:
            continue
        n3 += 1
        if o["id"] not in guarded:
            m3.append(_v("M3", "critical", o["id"], f"{o['id']} ({o.get('type')}) has its bottom "
                         f"{rec['bottom'] - floor:.2f} m over its floor and {drop:.2f} m over the ground outside, with "
                         f"no guard: somebody could fall out", None, drop_m=round(drop, 3)))
    return m3, m4, n3, n4


def rain_water(plan_boxes: list, roof: Optional[dict]) -> tuple[list[dict], int]:
    """M5: the downpipes (vertical pipe boxes of the facade kit) and the gutter runs."""
    from wenart.blender import facade as FA
    pipes = [b for b in plan_boxes if b.get("kind") == "downpipe" and float(b["size"][2]) > 0.5]
    gutters = [b for b in plan_boxes if b.get("kind") == "gutter"]
    if not gutters:
        return [], 0
    out = []
    xy = [(float(b["center"][0]), float(b["center"][1])) for b in pipes]
    close = sorted({(i, j) for i in range(len(xy)) for j in range(i + 1, len(xy))
                    if math.hypot(xy[i][0] - xy[j][0], xy[i][1] - xy[j][1]) < FA.KIT["pipe_gap_m"] - 0.05})
    area = G.polygon_area((roof or {}).get("outline") or []) if len((roof or {}).get("outline") or []) >= 3 else 0.0
    cap = max(2, int(math.ceil(area / FA.KIT["area_per_pipe_m2"]))) if area > 0 else None
    short = [b for b in gutters if float(b["size"][0]) < GUTTER_MIN_M]
    # 27 Oct 2026: a drawn roof outline (a roof plan's eaves loop) that steps in and out has its short eaves edges as
    # drawn; the gutter along such an edge (its length within a gutter's width of the edge's) is no broken-up eaves
    outline = (roof or {}).get("outline") or []
    if short and len(outline) >= 3 and not any(a.get("field") == "outline" for a in (roof or {}).get("assumed") or []):
        edges = [G.distance(outline[i], outline[(i + 1) % len(outline)]) for i in range(len(outline))]
        short = [b for b in short if not any(abs(float(b["size"][0]) - e) <= GUTTER_DRAWN_TOL_M for e in edges)]
    if close:
        out.append(_v("M5", "major", "building", f"{len(close)} pair(s) of downpipes stand closer than "
                      f"{FA.KIT['pipe_gap_m']:.1f} m", None, pipes=len(pipes)))
    if cap is not None and len(pipes) > cap + 1:
        out.append(_v("M5", "major", "building", f"{len(pipes)} downpipes for {area:.0f} m2 of roof (about one per "
                      f"{FA.KIT['area_per_pipe_m2']:.0f} m2: {cap})", None, pipes=len(pipes), cap=cap))
    if short:
        out.append(_v("M5", "major", "building", f"{len(short)} gutter run(s) shorter than {GUTTER_MIN_M:.1f} m: the "
                      f"eaves step in and out along the facade", None, short=len(short)))
    return out, len(pipes) + len(gutters)


def opening_language(manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M6: the library models of the outside doors and windows, one family per category."""
    cats: dict = {}
    n = 0
    for ob in (manifest or {}).get("objects") or []:
        lm = ob.get("library_model") if ob.get("kind") in ("door", "window") else None
        if not isinstance(lm, dict) or not lm.get("asset_id"):
            continue
        n += 1
        fam = str(lm.get("family") or lm.get("asset_id"))
        cats.setdefault(str(lm.get("category") or ob["kind"]), {}).setdefault(fam, []).append(
            ob.get("element_id") or ob.get("wenart_id"))
    out = []
    for cat, fams in sorted(cats.items()):
        if len(fams) > 1:
            names = "; ".join(f"{k}: {len(v)}" for k, v in sorted(fams.items(), key=lambda kv: -len(kv[1])))
            out.append(_v("M6", "major", "building", f"the {cat} openings use {len(fams)} different models ({names}): "
                          f"one door and window language per house", None, category=cat, families=len(fams)))
    return out, n


def rooms_make_sense(built: dict, manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M7: each room's anchors as built (the manifest's pieces, else the building's built pieces); one dining table."""
    built_types: dict = {}
    objs = [ob for ob in (manifest or {}).get("objects") or [] if ob.get("kind") == "furniture"]
    if objs:
        for ob in objs:
            built_types.setdefault(ob.get("room_id"), []).append((ob.get("element_id"), str(ob.get("type") or "")))
    else:
        for f in built.get("furniture") or []:
            if f.get("build") is not False:
                built_types.setdefault(f.get("room_id"), []).append((f.get("id"), str(f.get("type") or "")))
    out, n = [], 0
    for r in built.get("rooms") or []:
        t = str(r.get("room_type") or "").lower()
        have = built_types.get(r["id"]) or []
        types = {x[1] for x in have}
        want = ANCHORS.get(t)
        if want is None:
            continue
        n += 1
        if not types & set(want):
            out.append(_v("M7", "critical" if t in ("kitchen", "bathroom") else "major", r["id"],
                          f"{r['id']} ({t}) has no {' / '.join(want)} in the model: the room does not read as a {t}",
                          r["id"], missing=list(want)))
        if t == "bathroom" and not types & set(BATH_BASIN):
            out.append(_v("M7", "major", r["id"], f"{r['id']} (bathroom) has no washbasin in the model", r["id"],
                          missing=list(BATH_BASIN)))
        tables = [pid for pid, ft in have if ft == "table_dining"]
        if len(tables) > 1:
            out.append(_v("M7", "major", tables[1], f"{r['id']} holds {len(tables)} dining tables ({', '.join(tables)}): "
                          f"one dining set per room", r["id"], tables=tables))
    return out, n


def entrances_make_sense(built: dict, inferred: Optional[dict]) -> tuple[list[dict], int]:
    """M8: the entrance steps as built (``inferred``: the site plan's ``inferred`` with ``entrances`` and ``steps``,
    ``site.inferred_site``) against each other, the other doors' approach zones and the garage doors."""
    from wenart.blender import site as S
    ents = [e for e in (inferred or {}).get("entrances") or [] if isinstance(e, dict) and e.get("centre")]
    steps = [st for st in (inferred or {}).get("steps") or [] if isinstance(st, dict)]
    rooms = {r.get("id"): r for r in built.get("rooms") or [] if isinstance(r, dict)}
    room_of = {e["opening_id"]: (e.get("record") or {}).get("room_id") for e in ents}
    zones = {e["opening_id"]: S.door_approach(e) for e in ents}
    rail_zones = {e["opening_id"]: S.door_approach(e, shrink=0.01) for e in ents}
    tol = S.ENTRANCE_GROUP["overlap_tol_m"]
    garages = {i for i, rid in room_of.items() if S.room_role(rooms.get(rid)) == "garage"}

    def doors(st):
        return [st["opening_id"]] + [m for m in st.get("members") or [] if m != st["opening_id"]]

    out = []
    feet = [S.steps_footprint(st) for st in steps]
    for i, a in enumerate(steps):
        for j in range(i + 1, len(steps)):
            b = steps[j]
            if any(S.convex_overlap(p, q, tol) for p in feet[i] for q in feet[j]):
                da, db = doors(a), doors(b)
                out.append(_v("M8", "critical", da[0], f"the steps and landing of {', '.join(da)} and those of "
                              f"{', '.join(db)} overlap: two flights run into each other (one platform with one "
                              f"flight belongs there)", room_of.get(da[0]), doors=da + db))
    for st in steps:
        own = set(doors(st))
        for door, zone in rail_zones.items():
            if door in own:
                continue
            inside = sum(S.segment_in_convex(p0, p1, zone) for p0, p1 in st.get("rails") or [])
            if inside > S.ENTRANCE_GROUP["rail_min_m"]:
                out.append(_v("M8", "critical", door, f"a handrail of the steps of {', '.join(doors(st))} crosses "
                              f"the way out of {door} ({inside:.2f} m of rail in front of the door): nobody gets "
                              f"through", room_of.get(door), steps_of=doors(st), rail_m=round(inside, 3)))
        ramp = st.get("ramp") or {}
        if len(ramp.get("polygon") or []) >= 3:
            for door, zone in zones.items():
                if door not in own and S.convex_overlap(ramp["polygon"], zone, tol):
                    out.append(_v("M8", "major", door, f"the ramp of {', '.join(doors(st))} passes in front of "
                                  f"{door}", room_of.get(door), ramp_of=doors(st)))
        for door in sorted(garages):
            if door in own:
                out.append(_v("M8", "major", door, f"{door} leads into a garage or carport, and steps and a landing "
                              f"stand in front of it: a car cannot drive in", room_of.get(door), steps_of=doors(st)))
            elif any(S.convex_overlap(p, zones[door], tol) for p in S.steps_footprint(st)):
                out.append(_v("M8", "major", door, f"the steps of {', '.join(doors(st))} stand in front of the garage "
                              f"door {door}", room_of.get(door), steps_of=doors(st)))
    return out, len(ents)


def _clip_convex(subject: list, clip: list) -> list:
    """The part of the convex polygon ``subject`` inside the convex counter-clockwise polygon ``clip`` (pure)."""
    from wenart.blender import geom2d
    poly = list(subject)
    n = len(clip)
    for i in range(n):
        p, q = clip[i], clip[(i + 1) % n]
        a, b = q[1] - p[1], -(q[0] - p[0])                 # a x + b y + c <= 0: left of p -> q (inside)
        poly = geom2d.clip_half_plane(poly, a, b, -(a * p[0] + b * p[1]))
        if not poly:
            return []
    return poly


def overlap_area(a, b) -> float:
    """The area two simple polygons share (pure, exact: their convex pieces clipped against each other)."""
    from wenart.blender import geom2d
    if len(a or []) < 3 or len(b or []) < 3:
        return 0.0
    pa = geom2d.convex_pieces(geom2d.ccw(a))
    pb = [geom2d.ccw(q) for q in geom2d.convex_pieces(geom2d.ccw(b))]
    return sum(G.polygon_area(c) for x in pa for y in pb for c in [_clip_convex(x, y)] if len(c) >= 3)


def _built_cover(space_poly, outline, holes) -> float:
    """The area of ``space_poly`` under the built roof (its outline less its terrace openings)."""
    return max(0.0, overlap_area(space_poly, outline) - sum(overlap_area(space_poly, h) for h in holes))


OPEN_STEP_M = 0.10              # the sky over a space is sampled this fine (a 10 cm grid: a few hundredths of a m2)


def open_area(poly, outline, holes: list, others: list, step: float = OPEN_STEP_M, within=None) -> float:
    """The area of ``poly`` open to the sky (pure, sampled on a ``step`` grid): neither under the roof's ``outline``
    (its terrace openings ``holes`` left open) nor under any of ``others`` (light roofs, floors and slabs above);
    ``within``: only the part of ``poly`` inside this polygon counts (where a drawing puts a roof over it)."""
    xs, ys = [float(p[0]) for p in poly], [float(p[1]) for p in poly]
    n_open = 0
    y = min(ys) + step / 2.0
    while y < max(ys):
        x = min(xs) + step / 2.0
        while x < max(xs):
            p = (x, y)
            if G.point_in_polygon(p, poly) and (within is None or G.point_in_polygon(p, within)) and not (
                    (len(outline) >= 3 and G.point_in_polygon(p, outline)
                     and not any(G.point_in_polygon(p, h) for h in holes))
                    or any(G.point_in_polygon(p, q) for q in others)):
                n_open += 1
            x += step
        y += step
    return n_open * step * step


def _covers_over(built: dict, z: float, clear: float = 1.0) -> list:
    """The polygons over a floor at ``z`` besides the roof (pure): the slabs of the floors above, the outdoor spaces
    above (a balcony's slab over a veranda) and the light roofs of the outdoor spaces, all ``clear`` or more higher."""
    out = [s["outline"] for s in built.get("slabs") or [] if len(s.get("outline") or []) >= 3
           and float(s.get("z_top") or 0.0) > z + clear]
    site = built.get("site") if isinstance(built.get("site"), dict) else {}
    for s in site.get("outdoor_spaces") or []:
        if len(s.get("polygon") or []) >= 3 and float(s.get("z") or 0.0) > z + clear:
            out.append(s["polygon"])
        lr = s.get("roof") if isinstance(s.get("roof"), dict) else None
        if lr and len(lr.get("polygon") or []) >= 3 and float(lr.get("top_z") or 0.0) > z + clear:
            out.append(lr["polygon"])
    return out


def roof_vs_plan(built: dict, roof_model: Optional[dict]) -> tuple[list[dict], int]:
    """M11: the roof as built against the roofs the roof plan draws (module docstring). ``roof_model``: the roof the
    build makes (``roof.roof_model`` through ``build.prepare``). ``(findings, checked)``; 0 checked when no roof plan
    outline was read (nothing to compare)."""
    roof = built.get("roof") if isinstance(built.get("roof"), dict) else None
    rec = (roof or {}).get("roof_plan_outline")
    if not isinstance(rec, dict):
        return [], 0
    rid = rec.get("region_id") or "the roof plan"
    out = []
    used = (roof or {}).get("outline_source") == "roof_plan"
    top_plan = any(isinstance(e, dict) and e.get("rule") == "roof_outline" for e in roof.get("evidence") or [])
    if not used and not top_plan:
        out.append(_v("M11", "major", "roof", f"the roof is built over the outer walls + overhang (assumed) while "
                      f"{rid if rec.get('region_id') else 'a roof plan'} draws its outline: "
                      f"{rec.get('reason') or 'its outline was not used'}", kind="misread",
                      roof_plan=rec.get("region_id"), reason=rec.get("reason")))
    drawn = rec.get("points") or []
    outline = (roof_model or {}).get("outline") or []
    if len(drawn) < 3 or len(outline) < 3:
        return out, 1
    holes = [o["polygon"] for o in (roof_model or {}).get("openings") or [] if len(o.get("polygon") or []) >= 3]
    a_d, a_b = G.polygon_area(drawn), G.polygon_area(outline) - sum(G.polygon_area(h) for h in holes)
    inter = _built_cover(drawn, outline, holes)
    iou = inter / max(1e-9, a_d + a_b - inter)
    eaves = roof_model.get("eaves_z")
    site = built.get("site") if isinstance(built.get("site"), dict) else {}
    opened = []
    for s in site.get("outdoor_spaces") or []:
        poly = s.get("polygon") or []
        if len(poly) < 3 or (eaves is not None and float(eaves) - float(s.get("z") or 0.0) < M11_CLEAR_M):
            continue
        area = G.polygon_area(poly)
        under = overlap_area(poly, drawn)
        if area <= 0 or under < M11_DRAWN_SHARE * area:
            continue
        # open to the sky as built: under no roof, light roof, floor or slab above (the sampled area), counted where
        # the drawn roof is over it
        gap = open_area(poly, outline, holes, _covers_over(built, float(s.get("z") or 0.0)), within=drawn)
        if gap >= max(M11_OPEN_M2, M11_OPEN_SHARE * area):
            opened.append(s.get("id"))
            out.append(_v("M11", "major", s.get("id"), f"{rid} draws the roof over {s.get('id')} "
                          f"({s.get('label') or s.get('kind')}): the built roof leaves {gap:.1f} m2 of it open to the "
                          f"sky", s.get("id"), kind="lost", roof_plan=rid, open_m2=round(gap, 3),
                          area_m2=round(area, 3)))
    if iou < M11_IOU_MIN:
        out.append(_v("M11", "major", "roof", f"the built roof matches {rid}'s outline by {iou:.0%} (IoU): "
                      f"{a_d - inter:.1f} m2 drawn left open, {max(0.0, a_b - inter):.1f} m2 built where none is drawn"
                      + (f" (over {', '.join(map(str, opened))})" if opened else ""), kind="misread",
                      roof_plan=rid, iou=round(iou, 4), drawn_m2=round(a_d, 3), built_m2=round(a_b, 3)))
    light = [s["roof"]["polygon"] for s in site.get("outdoor_spaces") or []
             if isinstance(s.get("roof"), dict) and len(s["roof"].get("polygon") or []) >= 3]
    for k, other in enumerate(rec.get("others") or []):
        pts = other.get("points") or []
        if len(pts) < 3:
            continue
        area = G.polygon_area(pts)
        got = min(area, _built_cover(pts, outline, holes) + sum(overlap_area(pts, q) for q in light))
        if area > 0 and got < M11_OTHER_SHARE * area:
            out.append(_v("M11", "major", "roof", f"{rid} draws another roof of {area:.1f} m2 (a lower roof, a porch "
                          f"or veranda roof) beside the main one; the model builds a roof over {got:.1f} m2 of it",
                          kind="lost", roof_plan=rid, other=k, area_m2=round(area, 3), built_m2=round(got, 3)))
    return out, 1 + len(rec.get("others") or [])


def stair_walks(built: dict) -> tuple[list[dict], int]:
    """M9: the visitor's walk on the built floors (module docstring; ``stair_access.walk_review``). Every finding
    carries ``owner`` and ``fix`` (Argus's model line shows them)."""
    from wenart.blender import stair_access as SA
    rec = SA.walk_review(built)
    out = []
    for s in rec["stairs"]:
        if s.get("ok") is not False:
            continue
        ends = {k: s.get(k) or {} for k in ("arrival", "start")}
        bad = [k for k, r in ends.items() if r.get("ok") is False]
        sev = "critical" if any(ends[k].get("pocket") for k in bad) else "major"
        room = (ends["arrival"] if "arrival" in bad else ends["start"]).get("room")
        f = _v("M9", sev, s["stair"], f"{SA.cut_off_text(s)}: nobody gets from the stair into the rooms"
               if "arrival" in bad else f"{SA.cut_off_text(s)}: nobody gets from the rooms onto the stair", room,
               part="stair", level_id=s.get("level_id"), up_level_id=s.get("up_level_id"),
               **{f"{k}_{m}": ends[k].get(m) for k in ("arrival", "start") for m in ("ok", "floor_m2", "rooms", "missed")})
        out.append(dict(f, owner="architect", fix=FIX_STAIR))
    types = {f.get("id"): f.get("type") for f in built.get("furniture") or []}
    for d in rec["doors"]:
        what = {"opening": f"the floor opening {', '.join(d['blocked_by'])} lies in front of it",
                "pieces": f"{', '.join(d['blocked_by'])} stand(s) in front of it",
                "narrow": f"the floor in front of it is narrower than a {SA.WALK_CLEAR_M:.2f} m way",
                "part": "it opens onto a part of the room no way joins to the room's main floor"}[d["kind"]]
        f = _v("M9", "major", d["door"], f"{d['door']} ({d.get('type')}) of {d['room']} on {d['level_id']} cannot be "
               f"reached on foot from the room's main floor: {what}", d["room"], part="door", kind=d["kind"],
               blocked_by=list(d["blocked_by"]), blocked_types=[types.get(i) for i in d["blocked_by"]],
               level_id=d["level_id"])
        out.append(dict(f, owner="furniture" if d["kind"] == "pieces" else "architect", fix=FIX_DOOR[d["kind"]]))
    for p in rec["parts"]:
        rooms = f", rooms {', '.join(p['rooms'])}" if p["rooms"] else ""
        doors = f", doors {', '.join(p['doors'])}" if p["doors"] else ""
        f = _v("M9", "critical", p["openings"][0], f"{p['area_m2']:.2f} m2 of the floor of {p['level_id']} "
               f"({p['bounds']}{rooms}{doors}) is cut off by the floor opening {', '.join(p['openings'])}: no stair or "
               f"door joins it to the rest of the floor", p["rooms"][0] if p["rooms"] else None, part="floor",
               level_id=p["level_id"], area_m2=p["area_m2"], rooms=list(p["rooms"]), openings=list(p["openings"]))
        out.append(dict(f, owner="architect", fix=FIX_PART))
    return out, rec["checked"]


def stair_undersides(built: dict, manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M9 (d) (27 Oct 2026, user on real06's ground floor: "This stairs not making any sense": loose slabs seen from
    below): every built stair whose space under it is lower than ``stair_access.HEADROOM_M`` somewhere, or whose
    landing hangs high enough to walk under, has that space closed and that landing carried in the scene (its manifest
    record ``stair.under``: the spandrel panels and posts ``shell.stair_under_plan`` builds); a stair built without
    them is a major finding (its flights read as loose slabs hanging in the room)."""
    from wenart.blender import stair_access as SA
    entries = {ob.get("element_id"): ob for ob in (manifest or {}).get("objects") or []
               if isinstance(ob.get("stair"), dict)}
    out, n = [], 0
    for level in built.get("levels") or []:
        walls = [w for w in built.get("walls") or [] if w.get("level_id") == level.get("id")]
        for it in SA.planned(built, level):
            plan, pid = it.get("plan"), it["piece"].get("id")
            if not plan or pid not in entries:
                continue
            need = SA.under_stair(plan, walls)
            n += 1
            if not need["panels"] and not need["posts"]:
                continue
            got = entries[pid]["stair"].get("under") or {}
            short = []
            if int(got.get("panels") or 0) < len(need["panels"]):
                short.append(f"{need['low_m2']:.2f} m2 under its flights and landing is lower than "
                             f"{SA.HEADROOM_M:.2f} m and open on {len(need['panels'])} side(s) "
                             f"({int(got.get('panels') or 0)} panel(s) built)")
            if int(got.get("posts") or 0) < len(need["posts"]):
                short.append(f"its landing hangs over the floor with no support at {len(need['posts'])} corner(s)")
            if short:
                f = _v("M9", "major", pid, f"stair {pid}: " + "; ".join(short) + ": seen from below and from the side "
                       "its flights read as loose slabs hanging in the room", it["piece"].get("room_id"),
                       part="underside", level_id=level.get("id"), low_m2=need["low_m2"],
                       panels_needed=len(need["panels"]), posts_needed=len(need["posts"]))
                out.append(dict(f, owner="build", fix="build the stair with its underside closed where it is low "
                                                     "(spandrel panels) and its landing carried (posts): "
                                                     "shell.stair_under_plan"))
    return out, n


def doors_side_by_side(built: dict) -> tuple[list[dict], int]:
    """M12: the doors of every floor against each other (``door_spacing.conflicts``): overlapping openings, touching
    frames, two doors of one passage, leaves that sweep over each other. The finding's target is the door a decision
    made from another drawn type when there is one (its ``made_by`` key names the decision to undo), else the later
    id; ``other`` names the second door. Also the passages between two rooms that got a leaf, glass or a guard they do
    not need (``door_spacing.needless``)."""
    from wenart.blender import door_spacing as DS
    recs, n = DS.conflicts(built)
    # 27 Oct 2026 (user: "Not every opening inside the house requires a door or a window"): the openings between two
    # rooms that got a leaf, glass or a guard they do not need
    extra, m = DS.needless(built)
    recs, n = recs + extra, n + m
    out = [_v("M12", r["severity"], r["target"], r["message"], r.get("room_id"), rule=r["kind"], other=r["other"],
              doors=r["doors"], gap_m=r["gap_m"], share=r["share"], same_rooms=r["same_rooms"],
              made_by={k: v.get("key") for k, v in (r.get("made_by") or {}).items()}) for r in recs]
    return out, n


def review(built: dict, scene_manifest: Optional[dict] = None, prep: Optional[dict] = None) -> dict:
    """The review of the built model (module docstring). ``prep``: ``build.prepare`` of ``built`` (made here when not
    given; the plan of a whole building has the site, the outlines and the roof the facade kit needs)."""
    checks: dict = {}
    findings: list[dict] = []
    floors = _room_floors(built)

    def note(cid, got, n):
        checks[cid] = {"checked": n, "failed": len(got), "status": "ok"}
        findings.extend(got)

    got, n = doors_on_floors(built, floors)
    note("M1", got, n)
    if scene_manifest:
        got, n = working_heights(scene_manifest, floors)
        got2, n2 = over_sills(scene_manifest, built, floors)
        note("M2", got + got2, n + n2)
        got, n = opening_language(scene_manifest)
        note("M6", got, n)
    else:
        checks["M2"] = checks["M6"] = {"status": "unavailable", "note": "no scene manifest"}
    got, n = rooms_make_sense(built, scene_manifest)
    note("M7", got, n)
    try:
        if prep is None:
            from wenart.blender import build as B
            prep = B.prepare(built, "base", None)
        boxes: list = []
        if prep.get("whole") and prep.get("outlines"):
            from wenart.blender import facade as FA
            levels = [lv for lv in built.get("levels") or []]
            plan = FA.articulation_plan(built, levels, prep["outlines"], prep.get("ground_outline") or [],
                                        (prep.get("site") or {}).get("terrain"), prep.get("roof"), None, None,
                                        (prep.get("site") or {}).get("wells") or [])
            boxes = list(plan.get("boxes") or [])
        m3, m4, n3, n4 = guards_and_air(built, prep, boxes)
        note("M3", m3, n3)
        note("M4", m4, n4)
        got, n = rain_water(boxes, prep.get("roof"))
        note("M5", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        for cid in ("M3", "M4", "M5"):
            checks.setdefault(cid, {"status": "error", "note": f"{type(exc).__name__}: {exc}"})
    # M8 (26 Oct 2026): the entrance steps as the build made them (the site plan's inferred site)
    inferred = ((prep or {}).get("site") or {}).get("inferred")
    if inferred is None:
        checks["M8"] = {"status": "unavailable", "note": "no inferred site (site: ground, or no plan): no entrance "
                                                         "steps built"}
    else:
        try:
            got, n = entrances_make_sense(built, inferred)
            note("M8", got, n)
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            checks["M8"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M9 (27 Oct 2026): the visitor's walk from every stair into its floors, to every door, on every floor
    try:
        got, n = stair_walks(built)
        if scene_manifest:                                   # the stairs' undersides as built (the scene's records)
            more, m = stair_undersides(built, scene_manifest)
            got, n = got + more, n + m
        note("M9", got, n)
    except Exception as exc:  # noqa: BLE001 - shapely's errors too: a check that cannot run is recorded, never a stop
        checks["M9"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M10 (27 Oct 2026, user: "make argus catch these kind of things before me"): the outdoor spaces as a visitor uses
    # them: a way out onto them, guards, an outdoor floor, the cover of a covered kind, no roof to step onto from a
    # balcony, one post language (``outdoor_review``)
    try:
        from wenart.blender import outdoor_review as OR

        got, n = OR.review(built, prep)
        note("M10", got, n)
    except ImportError as exc:                     # inside Blender (no shapely): the review after the build has it
        checks["M10"] = {"status": "unavailable", "note": f"{type(exc).__name__}: {exc}"}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError) as exc:
        checks["M10"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M11 (27 Oct 2026): the roof as the roof plan draws it (the roof the build makes: the plan's, else the model's)
    try:
        roof_model = (prep or {}).get("roof")
        if roof_model is None and isinstance(built.get("roof"), dict):
            from wenart.blender import roof as R
            roof_model = R.roof_model(built["roof"], built)
        got, n = roof_vs_plan(built, roof_model)
        if n:
            note("M11", got, n)
        else:
            checks["M11"] = {"status": "unavailable", "note": "no roof plan outline read (roof.roof_plan_outline)"}
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        checks["M11"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M12 (27 Oct 2026, user on real06: "doors next to each other not making sense"): doors side by side
    try:
        got, n = doors_side_by_side(built)
        note("M12", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError,
            ImportError) as exc:
        checks["M12"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M15 (28 Oct 2026, user on real04's roof terrace: "makes no sense to have that table with the carpet outside"):
    # outdoor rooms dressed for outside (pure)
    try:
        from wenart.blender import outdoor as OD

        got, n = OD.review(built)
        note("M15", got, n)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        checks["M15"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M16 (28 Oct 2026, user: "More lights from the ceiling needed"): enough ceiling light for each room's zones and
    # floor. The lighting rule lives with the decor (wenart.furniture, shapely and numpy): Blender's Python has no
    # shapely, so inside the build it is "unavailable" and the pipeline's refresh after the build
    # (cli.refresh_model_review), the code critic and Argus run it. It is imported by name, out of the build
    # script's import closure (build.FINGERPRINT_CODE): the scene never depends on it.
    try:
        import importlib

        CL = importlib.import_module("wenart.furniture.ceiling_lights")
        got, n = CL.review(built, density_of(built))
        note("M16", got, n)
    except ImportError as exc:
        checks["M16"] = {"status": "unavailable", "note": f"{type(exc).__name__}: {exc}"}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        checks["M16"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    return {"findings": findings, "checks": checks}


def density_of(built: dict):
    """M16: each room's decor density as the decor stage filled it (the building's ``decor_minimum``), else
    balanced."""
    minimum = built.get("decor_minimum") if isinstance(built.get("decor_minimum"), dict) else {}

    def of(room: dict) -> str:
        rec = minimum.get(room.get("id")) if isinstance(minimum.get(room.get("id")), dict) else {}
        return str(rec.get("density") or "balanced")
    return of


def report_md(rec: dict, project: str = "") -> str:
    """The review as a short report (``scene/model_review.md``)."""
    lines = [f"# Review of the 3D model{': ' + project if project else ''}", "",
             "Every element of the model as built, measured (not seen through a camera): "
             + "; ".join(f"{k} {v.get('checked', '-')} checked, {v.get('failed', '-')} failed" if v.get("status") == "ok"
                         else f"{k} {v.get('status')}" for k, v in sorted(rec["checks"].items())) + ".", ""]
    order = {"critical": 0, "major": 1, "minor": 2}
    rows = sorted(rec["findings"], key=lambda f: (order.get(f["severity"], 3), f["check"], str(f["target"])))
    if not rows:
        lines.append("Nothing to fix in the model.")
    else:
        lines += ["| severity | check | element | what |", "|---|---|---|---|"]
        lines += [f"| {f['severity']} | {f['check']} | {f['target']} | {f['message']} |" for f in rows]
    return "\n".join(lines) + "\n"
