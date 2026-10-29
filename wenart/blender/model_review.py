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
- M13 the kitchen as one designed kitchen (28 Oct 2026, user on real04: "Kitchen design could have been a lot better
  this is terrible", on real06: "Why is this closing the window"; ``kitchen_design``): a hood over every hob, no
  cooker in a gap of a run and no under-counter appliance off its run's worktop line, no wall cabinet over a window
  or glazed door of the building as built (critical), one bottom and top line, no unexplained gap between the
  cabinets of a wall, no box of a width no real wall unit has, wall units on the base joints (minor). M2 reads a
  module run at its worktop line (``module.worktop_m``), not at its tap, hood or column.
- M14 decor attached to what holds it (28 Oct 2026, user on real04 run 20261028-005318-full: "still flying pillows all
  around", "More flying pillows", "I did not like this bed", "Light is flying in the air needs to be connected to
  ceiling"; ``decor_attached``): every hosted decor item's rest record (the scene manifest's ``rest``) within the S5
  tolerances (``rest.rest_ok``: the gap under it, behind a leaning cushion, a cloth the host pokes through or a torn
  drape), and every pendant or ceiling light up to the ceiling over it (its ``hang`` record's ``gap_left_m``; without
  one, its box against the level's ceiling there: an older build left a library pendant 0.99 m under it, dec_L-1_008).
- M15 the grading of the site and its outdoor floors (28 Oct 2026, users on real04: "There could be better outside
  solutions to the grade slope", "Better solutions needed for the elevation difference outside", "I am not liking this
  is the only outside flooring"; ``grading.review``): G1 every terrace tier planted, the tiers of one side at one level;
  G2 every tread on its riser and the ground, never buried by the ground beside it without a hole and cheek walls,
  never through a planter, wall, hedge or pool; G3 paths level across, stepped with landings where steeper than 1:12;
  G4 a ramp only on an accessible route, at most the ramp slope of its rise; G5 banks at most 1:3 (lawn) or 1:2
  (planted); G6 retaining walls in the house's base stone (never bare concrete) with a coping; G7 never one floor look
  for every outdoor use. Each finding carries its rule (``metrics.rule``) and element.
- M16 outdoor rooms dressed for outside (28 Oct 2026, user on real04 run 20261028-005318-full, its roof terrace:
  "makes no sense to have that table with the carpet outside, that's outside area"; ``outdoor.review``): no rug,
  runner or carpet on the floor of an open-air room or an outdoor space, and no library model of an outdoor type
  (table, chair, sofa ...) there that is not made for outside (``outdoor.outdoor_ready``). Major; kind ``no_sense``.
- M17 enough ceiling light (28 Oct 2026, same run, user: "More lights from the ceiling needed"; its 50.9 m² living and
  dining room had one pendant; ``ceiling_lights.review``): every lit room holds the ceiling lights the lighting rule
  hangs there (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run,
  and the lumen method's count for its floor); major with no light, under half of them or an unlit table or bed,
  else minor; kind ``taste``.
- M18 the stair's handrails as one designed balustrade (28 Oct 2026, user on real04's stairs: "There should have been
  better indoor stair solutions should be there I did not like this one"; the corridor view: steel rails at different
  angles crossing each other near the well; ``stair_rails_review``): no rail crosses another or the floor guard of the
  level above, none runs beside that floor guard over its floor, no handrail stops short (a rail end no newel takes, an
  open turn, landing or apron edge without a rail and without a reason), every flight holds a handrail over most of its
  run, the handrail 0.85-1.10 m over the nosing line (1.0 m on a level edge), nothing through a tread, a wall or the
  floor above, no infill gap of 0.11 m, no rail out over the room (minor). Measured on the scene's guard records
  (``stair.guards``), or on the straight per-flight rails of an older scene.
- M20 every door a real product (29 Oct 2026, user: "Better door models needed"; real06 run 20261028-154514-full:
  the build refused the HSSD doors the plan chose, and the parametric doors were slabs in flat frames;
  ``opening_models.door_product_problems``): a door the plan gave a library model built parametric (major, with the
  build's reason: the scene's ``library_planned`` record or its warnings), a parametric door without its architrave
  and (a flush leaf) its face detail (major). Kind ``taste``; the build owns it.
- M21 the rooms furnished for their use (29 Oct 2026, the user's review of real06 run 20261028-154514-full: "There is
  no TV in the house", "a bit more furniture would be nice", "There are no library and books in the house", "bath is
  too empty there should be some dolaps", "I did not like this light"; ``wenart.furniture.room_use.review``): a TV in
  every living room (major) and the master bedroom (minor), living and dining rooms furnished to their density, a
  bookshelf with books, storage in every bathroom (minor), no library model the user rejected (major), no floor lamp
  built at its oversized plan symbol (minor); kind ``taste``.
- M23 the professional bar (29 Oct 2026, lesson UL106; user, showing a professional bedroom render: "I want my renders
  to be as professional as these ones"; ``wenart.furniture.dressing.review``): every living room and bedroom of a
  style family that builds them has its feature panel on the accent wall (``feature_walls``) and its wood floor laid
  in the family's pattern (``parquet``) unless the decor stage's recipe turned them off, layered curtains (a sheer) and
  a bed's throw in two layers. Minor; kind ``taste``.
- M19 fixtures you can use (29 Oct 2026, the user on real06 run 20261028-154514-full: "This washing machine would not
  open": its door faced the toilet 0.11 m away; "this sink not making sense there": a basin right under a window;
  ``fixture_use``): every door-fronted piece as built keeps its width x its access depth free in front of it (a washer,
  a dishwasher, a cooker, a fridge, a nightstand: critical when its door or drawers cannot open, major when it cannot
  be used; door-fronted storage: critical when its doors cannot open, its walking room is G13's), and no basin stands
  under a window with its sill under 1.25 m (major: no mirror over it, its tap against the sill). Pure (runs inside
  Blender); kind ``no_sense``.
- M22 backs on their walls (29 Oct 2026, user: "There is a gap between wall and water faucet not looking good"; real06's
  sink unit f_L0_020 stood 0.08 m off the wall under the window; ``fixture_use.back_gaps``): no piece whose back belongs
  on a wall stands parallel to it 0.055-0.15 m off it (major; a drawing gap the reading snaps,
  ``reading.fixture_use_fixes``).
- M24 every chimney as a builder makes it (29 Oct 2026, lesson UL109, user on real06 run 20261028-154514-full: "There
  are no chimneys there could be some chimney in the projects"; ``chimney.measure``), on the scene's chimney records
  (their bottom as built), else the plan's: a chimney off the roof (it does not reach the roof) or floating over its
  covering (a gap under it) is critical; one reaching under the roof's underside into the rooms (no drawn fireplace
  under it), lower than the 3-2-10 rule of thumb (0.6 m over the roof within 3 m, 0.9 m over its exit) or standing in
  front of an outside window is major. Kind ``no_sense``; the build owns it.
- M29 the doors and the walk-ins as a designer shows them (29 Oct 2026, lessons UL116 "not all the doors needs to be
  closed in default", UL117 "Not every single one of them with the same dimension", UL120 / UL125 the see-through
  walk-in "argus should have think of this", UL122 "Doors looks without frames they need frames";
  ``door_states.state_problems`` and ``frame_problems``): every inside door closed in a house whose doors could open,
  all doors one size (major) or the entrance no bigger than the inside doors (minor), an open leaf standing in a piece
  (major, kind ``geometry``), a walk-in dressing room with closed fronts only (major, the architect's D8 answer that
  fixes it in ``fix_choice``), a door without a frame and no recorded frameless reason (major) or an indoor face
  without its architrave (minor). The build owns them; a walk-in's fronts the architect.

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
CHECKS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18",
          "M19", "M20", "M21", "M22", "M23", "M24")   # 29 Oct 2026: M19 fixtures in use, M20 doors as products, M21 rooms for their use, M22 backs on walls, M23 the professional bar, M24 chimneys
CHECKS += ("M29",)          # 29 Oct 2026 (UL116, UL117, UL120, UL122, UL125): the doors and walk-ins as designed
HUNG_DECOR = ("pendant_light", "ceiling_light")     # M14: decor hung from the ceiling
FIX_HANG = ("connect it to the ceiling over it: a cord or rod and a canopy from its top (furniture.hang_plan), or lift "
            "it until its own top meets the ceiling")
FIX_REST = "place it again on the built host (rest.plan_decor / plan_throw), or leave it out"
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
        # 28 Oct 2026: a kitchen run built of modules works at its worktop line, not at its tallest part (the tap, the
        # cooker hood, a fridge column: real04's f_L-1_003 read 1.18 m from its tap)
        worktop = (ob.get("module") or {}).get("worktop_m") if isinstance(ob.get("module"), dict) else None
        if isinstance(worktop, (int, float)):
            top = float(worktop) + float(ob.get("mount_bottom_m") or 0.0)
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


def chimneys_review(built: dict, prep: Optional[dict], manifest: Optional[dict]) -> tuple[list[dict], Optional[int]]:
    """M24 (29 Oct 2026, lesson UL109): every chimney measured against the roof (``chimney.measure``): the scene's
    chimney records (their bottom as built) when there is a scene, else the plan's (``prep["chimneys"]``). ``None``
    checked when no roof is built."""
    from wenart.blender import chimney as CH
    from wenart.blender import roof as R

    model = (prep or {}).get("roof")
    if model is None and isinstance(built.get("roof"), dict):
        model = R.roof_model(built["roof"], built)
    if not model or not model.get("equations"):
        return [], None
    if manifest and manifest.get("objects"):
        recs = [(o["chimney"], o["chimney"].get("bottom")) for o in manifest["objects"]
                if o.get("detail") == "chimney" and isinstance(o.get("chimney"), dict)]
    else:
        recs = [(c, None) for c in ((prep or {}).get("chimneys") or {}).get("chimneys") or []]
    out = []
    for ch, bottom in recs:
        for p in CH.measure(ch, model, built, bottom):
            nums = {k: v for k, v in p.items() if k not in ("problem", "severity", "message")}
            out.append(_v("M24", p["severity"], ch.get("id"), p["message"], ch.get("room_id"), problem=p["problem"],
                          source=ch.get("source"), **nums))
    return out, len(recs)


def opening_language(manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M6: the library models of the outside doors and windows, one family per category; 28 Oct 2026: the inside
    doors one family per role (``opening_models.plan_inside``: ``inside_door:solid``, ``inside_door:glazed``)."""
    cats: dict = {}
    n = 0
    for ob in (manifest or {}).get("objects") or []:
        lm = ob.get("library_model") if ob.get("kind") in ("door", "window") else None
        if not isinstance(lm, dict) or not lm.get("asset_id"):
            continue
        n += 1
        fam = str(lm.get("family") or lm.get("asset_id"))
        cat = str(lm.get("category") or ob["kind"]) + (f":{lm['role']}" if lm.get("role") else "")
        # 29 Oct 2026 (UL89): a door category takes a family per way its doors open (a sliding and a French door)
        way = (lm.get("opening") or {}).get("operation") if ob.get("kind") == "door" else None
        cat += f":{way}" if way else ""
        cats.setdefault(cat, {}).setdefault(fam, []).append(ob.get("element_id") or ob.get("wenart_id"))
    out = []
    for cat, fams in sorted(cats.items()):
        if len(fams) > 1:
            names = "; ".join(f"{k}: {len(v)}" for k, v in sorted(fams.items(), key=lambda kv: -len(kv[1])))
            out.append(_v("M6", "major", "building", f"the {cat} openings use {len(fams)} different models ({names}): "
                          f"one door and window language per house", None, category=cat, families=len(fams)))
    return out, n


def door_products(manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M20 (module docstring): every door of the scene a library model or a parametric door built as a product."""
    from wenart.blender import opening_models as OM

    rows = OM.built_doors(manifest)
    out = []
    for p in OM.door_product_problems(manifest):
        out.append(_v("M20", p["severity"], p["target"], p["message"], None,
                      kind="lost" if p["kind"] == "library_door_not_built" else None, problem=p["kind"]))
    return out, len(rows)


M29_KINDS = {"leaf_in_piece": "geometry", "no_frame": "taste", "no_architrave": "taste"}   # else reference_missed
M29_FIX = {"all_closed": "the build's door_states (an inside door stands open by default)",
           "one_size": "the build's door_states.apply_sizes (sizes by role and family)",
           "leaf_in_piece": "move the piece out of the open leaf, or the build closes the door (door_states)",
           "view_closed_doors": "the build opens a door a view sees into a room worth showing (door_states.revise_for_cameras)",
           "dressing_closed_fronts": "the architect's D8 answer (wardrobe_fronts) and the build's see-through fronts",
           "no_frame": "the build frames every door (opening_build._door_frame, parametric.door_frame_parts)",
           "no_architrave": "the build's architrave on the door's indoor faces (parametric.architrave_boxes)"}


def doors_as_designed(built: dict, manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M29 (29 Oct 2026; lessons UL116 "not all the doors needs to be closed in default", UL117 "Not every single one
    of them with the same dimension", UL120 / UL125 the see-through walk-in, UL122 "Doors looks without frames they
    need frames"; ``door_states.state_problems`` and ``frame_problems``): every inside door closed in a house whose
    doors could open, all doors one size, an open leaf in a piece, a walk-in with closed fronts only, a door with no
    frame and no recorded reason (the frames when there is a scene manifest)."""
    from wenart.blender import door_states as DS

    probs = DS.state_problems(built, manifest)
    if manifest and manifest.get("objects"):
        probs += DS.frame_problems(manifest)
    out = []
    for p in probs:
        v = _v("M29", p["severity"], p["target"], p["message"], None, kind=M29_KINDS.get(p["kind"]), problem=p["kind"])
        v["owner"] = "architect" if p["kind"] == "dressing_closed_fronts" else "build"
        v["fix"] = M29_FIX.get(p["kind"], "the build's doors")
        if p.get("fix_choice"):
            v["metrics"]["fix_choice"] = p["fix_choice"]
        out.append(v)
    n = sum(1 for o in built.get("openings") or [] if o.get("type") == "door")
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


# M13 (28 Oct 2026, user on real04's kitchen: "Kitchen design could have been a lot better this is terrible"; on
# real06's: "What kind of a kitchen is this", "Why is this closing the window"): the kitchen as one designed kitchen.
M13_TOP_TOL_M = 0.03            # an under-counter appliance's top this far off its run's worktop line is off the line
M13_UNDER_COUNTER_M = 1.30      # an appliance lower than this beside a run is an under-counter one (a tall fridge is not)
M13_IN_LINE_M = 0.05            # an appliance whose front is this close to a run's front line stands in the run
M13_GAP_MIN_M = 0.02            # two wall cabinets of one wall line this far apart leave a gap ...
M13_LINE_TOL_M = 0.01           # ... and their bottom and top lines agree within this
M13_EXPLAIN_M = 0.35            # a gap is explained by a hood, a window or a door within this of it
APPLIANCE_TYPES = ("stove", "fridge", "dishwasher", "washing_machine")


def _frame_of(fp: dict) -> tuple[tuple[float, float], float, float, float]:
    c = (float(fp["center"][0]), float(fp["center"][1]))
    return c, math.radians(float(fp.get("rotation_deg") or 0.0)), float(fp["size"][0]), float(fp["size"][1])


def _local(c, rot: float, p) -> tuple[float, float]:
    dx, dy = float(p[0]) - c[0], float(p[1]) - c[1]
    return math.cos(rot) * dx + math.sin(rot) * dy, -math.sin(rot) * dx + math.cos(rot) * dy


def _world(c, rot: float, x: float, y: float = 0.0) -> tuple[float, float]:
    return c[0] + math.cos(rot) * x - math.sin(rot) * y, c[1] + math.sin(rot) * x + math.cos(rot) * y


def _plan(piece: dict) -> dict:
    plan = ((piece.get("asset") or {}).get("module_plan") or {}) if isinstance(piece.get("asset"), dict) else {}
    return plan if isinstance(plan, dict) else {}


def kitchen_design(built: dict, manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """M13 (module note above): every kitchen run as one designed kitchen, measured on the model as built (pure, no
    geometry library: it runs inside Blender):

    (a) every hob has a cooker hood above it (its run's plan holds the hood: ``modules.plan_kitchen_run``; a
        freestanding cooker has none) - major;
    (b) no appliance of a run stands off its worktop line: a cooker in a gap of the run (``plan.gaps``: a freestanding
        model where the hob belongs), an under-counter appliance with its own model in line with a run whose top
        (the manifest's box, else its fitted height) is more than ``M13_TOP_TOL_M`` off the run's worktop - major;
    (c) the wall cabinets read as one run: never over a window or glazed door of the building as built
        (``modules.wall_unit_blocks``, unless the build left it free: the manifest's ``module.blocked_m``) - critical;
        one bottom and top line in a room - major; no gap between two cabinets of one wall line that no hood, window
        or door explains - major; a cabinet built as a box of a width no real wall unit has (not a wall run of real
        units) - major; wall units whose joints miss the base units' joints - minor."""
    from wenart.blender import modules as MOD
    pieces = [f for f in built.get("furniture") or [] if isinstance(f, dict) and f.get("build") is not False
              and isinstance(f.get("footprint"), dict) and f["footprint"].get("size")]
    by_id = {f.get("id"): f for f in pieces}
    entries = {ob.get("element_id"): ob for ob in (manifest or {}).get("objects") or []
               if ob.get("kind") == "furniture" and ob.get("element_id")}
    floors = _room_floors(built)
    runs = [f for f in pieces if f.get("type") in ("kitchen_counter", "kitchen_island")
            and _plan(f).get("builder") == "kitchen_run" and _plan(f).get("modules")]
    out: list[dict] = []
    n = 0
    # (a) hobs and hoods
    for f in pieces:
        if f.get("type") != "stove":
            continue
        n += 1
        host = by_id.get((f.get("asset") or {}).get("built_in")) if isinstance(f.get("asset"), dict) else None
        plan = _plan(host) if host is not None else {}
        rec = next((b for b in plan.get("built_ins") or [] if isinstance(b, dict) and b.get("id") == f["id"]), None)
        if rec is not None and (rec.get("hood") or plan.get("hood")):
            continue
        where = f"built into {host['id']}" if rec is not None else "a freestanding cooker"
        out.append(_v("M13", "major", f["id"], f"{f['id']} (stove, {where}) has no cooker hood above it: every hob "
                      "gets a hood sized to it (a chimney hood on the wall, an under-cabinet hood under a wall "
                      "cabinet, an island hood over an island)", f.get("room_id"), rule="hood"))
    # (b) appliances on the worktop line
    for run in runs:
        plan = _plan(run)
        worktop = float(plan.get("worktop_m") or MOD.KITCHEN_WORKTOP_HEIGHT_M)
        c, rot, w, d = _frame_of(run["footprint"])
        for g in plan.get("gaps") or []:
            if g.get("type") == "stove":
                n += 1
                out.append(_v("M13", "major", g.get("id"), f"{g.get('id')} (stove) stands in a gap of the counter run "
                              f"{run['id']} with its own freestanding model: a hob in a run is set into the "
                              f"worktop with an oven under it, on the run's worktop line ({worktop:.2f} m)",
                              run.get("room_id"), rule="worktop_line", run=run["id"]))
        for f in pieces:
            if f.get("type") not in APPLIANCE_TYPES or f.get("room_id") != run.get("room_id") \
                    or (f.get("asset") or {}).get("built_in") or any(g.get("id") == f.get("id")
                                                                     for g in plan.get("gaps") or []):
                continue
            fc, frot, fw, fd = _frame_of(f["footprint"])
            if math.cos(frot - rot) < 0.99:
                continue                                  # not facing the way this run faces
            lx, ly = _local(c, rot, fc)
            front_gap = abs((ly - fd / 2.0) + d / 2.0)    # its front edge against the run's front line (-Y)
            if front_gap > M13_IN_LINE_M + abs(fd - d) or abs(lx) > w / 2.0 + fw / 2.0 + M13_IN_LINE_M:
                continue                                  # not in line with the run, or not beside it
            ob = entries.get(f["id"])
            box = (ob or {}).get("box3d") if isinstance((ob or {}).get("box3d"), dict) else None
            if box and box.get("center") and box.get("size") and f.get("room_id") in floors:
                top = float(box["center"][2]) + float(box["size"][2]) / 2.0 - floors[f["room_id"]]
            else:
                bb = (f.get("asset") or {}).get("bbox_m") if isinstance(f.get("asset"), dict) else None
                if not bb or len(bb) < 3:
                    continue
                top = float(bb[2])
            if top >= M13_UNDER_COUNTER_M:
                continue                                  # a tall appliance beside the run
            n += 1
            if abs(top - worktop) > M13_TOP_TOL_M:
                out.append(_v("M13", "major", f["id"], f"{f['id']} ({f['type']}) stands in line with the counter run "
                              f"{run['id']} with its top at {top:.2f} m, {abs(top - worktop):.2f} m "
                              f"{'under' if top < worktop else 'over'} the worktop line ({worktop:.2f} m): an "
                              "appliance in a run is built into it, its top on the worktop line", f.get("room_id"),
                              rule="worktop_line", run=run["id"], top_m=round(top, 3), worktop_m=round(worktop, 3)))
    # (c) the wall cabinets
    cabinets = [f for f in pieces if f.get("type") == "wall_cabinet"]
    by_room: dict = {}
    for cab in cabinets:
        n += 1
        ob = entries.get(cab["id"])
        record = (ob or {}).get("module") if isinstance((ob or {}).get("module"), dict) else None
        plan = record if record is not None else _plan(cab)
        free = [tuple(s) for s in (plan.get("blocked_m") or [])]
        blocks = [b for b in MOD.wall_unit_blocks(cab, built)
                  if not any(s[0] <= b["x0_m"] + 1e-3 and s[1] >= b["x1_m"] - 1e-3 for s in free)]
        if blocks and (ob is not None or manifest is None):
            out.append(_v("M13", "critical", cab["id"], f"{cab['id']} (wall cabinet) hangs over "
                          f"{', '.join(str(b['id']) for b in blocks)}: a wall cabinet never covers any part of a "
                          "window or glazed door (its full width and a margin)", cab.get("room_id"),
                          rule="covers_window", windows=[b["id"] for b in blocks]))
        units = plan.get("units_m") if plan.get("builder", "wall_run") == "wall_run" else None
        width = float(cab["footprint"]["size"][0])
        if not units and not any(abs(width - s) <= MOD.WALL_RUN_TOL_M for s in MOD.WALL_RUN_WIDTHS_M):
            out.append(_v("M13", "major", cab["id"], f"{cab['id']} (wall cabinet) is one box {width:.2f} m wide, a width "
                          "no real wall unit has: a wall run of real units (300-900 mm) in line with the base units",
                          cab.get("room_id"), rule="odd_width", width_m=round(width, 3), kind="taste"))
        if plan.get("misaligned"):
            out.append(_v("M13", "minor", cab["id"], f"{cab['id']} (wall cabinet): {plan['misaligned']} joint(s) of its "
                          "wall units miss the base units' joints under them", cab.get("room_id"), rule="joints",
                          kind="taste"))
        by_room.setdefault(cab.get("room_id"), []).append(cab)
    hoods = []                                           # (room, centre, rotation, half width) of every built hood
    for run in runs:
        h = _plan(run).get("hood")
        if isinstance(h, dict):
            c, rot, _w, _d = _frame_of(run["footprint"])
            hoods.append((run.get("room_id"), _world(c, rot, float(h.get("x_m") or 0.0)), rot,
                          float(h.get("w_m") or 0.6) / 2.0))
    for rid, cabs in by_room.items():
        lines = {}
        for cab in cabs:
            try:
                bottom = float(cab.get("mount_bottom_m") if cab.get("mount_bottom_m") is not None else 1.45)
            except (TypeError, ValueError):
                bottom = 1.45
            top = bottom + float(cab.get("height") or 0.7)
            lines[cab["id"]] = (round(bottom, 3), round(top, 3))
        if len({b for b, _t in lines.values()}) > 1 or len({t for _b, t in lines.values()}) > 1:
            spread = sorted(set(lines.values()))
            if spread[-1][0] - spread[0][0] > M13_LINE_TOL_M or spread[-1][1] - spread[0][1] > M13_LINE_TOL_M:
                out.append(_v("M13", "major", cabs[0]["id"], f"the wall cabinets of {rid} do not share one bottom and top "
                              f"line ({', '.join(f'{k}: {b:.2f}-{t:.2f} m' for k, (b, t) in sorted(lines.items()))})",
                              rid, rule="one_line", kind="taste"))
        for i, a in enumerate(cabs):
            ca, ra, wa, _da = _frame_of(a["footprint"])
            for b in cabs[i + 1:]:
                cb, rb, wb, _db = _frame_of(b["footprint"])
                if abs(math.sin(ra - rb)) > 0.02:
                    continue
                bx, by = _local(ca, ra, cb)
                if abs(by) > 0.03:
                    continue                             # not on one wall line
                gap = abs(bx) - wa / 2.0 - wb / 2.0
                if gap <= M13_GAP_MIN_M:
                    continue
                mid_x = (bx / abs(bx)) * (wa / 2.0 + gap / 2.0) if abs(bx) > 1e-9 else 0.0
                mid = _world(ca, ra, mid_x)
                explained = any(hr == rid and math.hypot(hc[0] - mid[0], hc[1] - mid[1]) <= hw + gap / 2.0 + 0.02
                                for hr, hc, _hrot, hw in hoods)
                probe = dict(a, footprint={"center": list(mid), "size": [gap + 2 * M13_EXPLAIN_M, 0.35],
                                           "rotation_deg": math.degrees(ra)})
                explained = explained or bool(MOD.wall_unit_blocks(probe, built, 0.0)) or _door_near(built, probe)
                if not explained:
                    out.append(_v("M13", "major", b["id"], f"{a['id']} and {b['id']} (wall cabinets of one wall) leave a "
                                  f"{gap:.2f} m gap that no hood, window or door explains: one continuous run",
                                  rid, rule="gap", gap_m=round(gap, 3), kind="taste"))
    return out, n


def _door_near(built: dict, probe: dict) -> bool:
    """Whether a door of the probe's level stands in the wall behind the probe's span (as ``wall_unit_blocks`` reads
    a glazed door; any door here: a wall cabinet stops at a door)."""
    from wenart.blender import modules as MOD
    doors = [dict(o, type="door", glazed=True) for o in built.get("openings") or [] if o.get("type") in ("door",
                                                                                                        "opening")]
    return bool(MOD.wall_unit_blocks(dict(probe, mount_bottom_m=0.5, height=1.5), dict(built, openings=doors), 0.0))


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
        # 28 Oct 2026: as the build closes it: with the stair's structure (its soffit) and no panel over a floor opening
        voids = [p for _i, p in SA.floor_voids(built, level.get("id"))]
        for it in SA.planned(built, level):
            plan, pid = it.get("plan"), it["piece"].get("id")
            if not plan or pid not in entries:
                continue
            plan = dict(plan, structure=entries[pid]["stair"].get("structure"))
            need = SA.under_stair(plan, walls, voids)
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


def decor_attached(manifest: Optional[dict], built: dict) -> tuple[list[dict], int]:
    """M14 (module docstring): decor that is not attached to what holds it, from the scene manifest's decor records."""
    from wenart.blender import rest as R
    from wenart.blender.furniture import ceiling_above

    tol = R.REST_TOLERANCES
    levels = {lv.get("id"): lv for lv in built.get("levels") or []}
    out: list[dict] = []
    n = 0
    for ob in (manifest or {}).get("objects") or []:
        if ob.get("kind") != "decor":
            continue
        did = ob.get("decor_id") or ob.get("wenart_id") or ob.get("name")
        dtype = ob.get("type")
        if dtype in HUNG_DECOR:
            hang = ob.get("hang") if isinstance(ob.get("hang"), dict) else None
            if hang is not None and hang.get("gap_left_m") is not None:
                gap, how = float(hang["gap_left_m"]), "its hang record"
            else:
                level, c, s = levels.get(ob.get("level_id")), ob.get("center"), ob.get("size")
                if level is None or not isinstance(c, (list, tuple)) or not isinstance(s, (list, tuple)) \
                        or len(c) < 3 or len(s) < 3:
                    continue
                top = float(c[2]) + float(s[2]) / 2.0 - float(level.get("elevation") or 0.0)
                gap = float(ceiling_above(level, c[:2], (0.0, 0.0))[0]) - top
                how = "its box (no hang record: nothing was built up to the ceiling)"
            n += 1
            if gap > tol["decor_hang_gap_m"] + 1e-9:
                out.append(_v("M14", "major", did, f"{dtype} {did} hangs in the air: its top {gap:.2f} m under the "
                                                   f"ceiling over it with nothing (cord, rod, canopy) up to it ({how})",
                              room_id=ob.get("room_id"), kind="detached", rule="hang", gap_m=round(gap, 4),
                              tolerance_m=tol["decor_hang_gap_m"], fix=FIX_HANG))
            continue
        rest = ob.get("rest")
        if not isinstance(rest, dict) or not rest:
            continue
        n += 1
        ok, why = R.rest_ok(rest)
        if not ok:
            out.append(_v("M14", "major", did, f"{dtype} {did} on {ob.get('host_id')} is not attached to its support "
                                               f"({ob.get('support') or 'its host'}): {'; '.join(why)}",
                          room_id=ob.get("room_id"), kind="detached", rule="rest", host_id=ob.get("host_id"),
                          measured={k: rest.get(k) for k in ("gap_m", "penetration_m", "support_share", "back_gap_m",
                                                             "poke_m", "cloth_edge_m") if k in rest},
                          fix=FIX_REST))
    return out, n


FIX_RAILS = ("build the stair's guards as one continuous balustrade per open side with newels at its turns and ends, "
             "its handrail over the nosing line, stopped under the slab and beside the floor guard of the level above, "
             "a wall handrail where a flight has none (stair_rails.plan_guards, shell.stair_guard_plan)")


def stair_rails_review(built: dict, manifest: Optional[dict]) -> tuple[list[dict], int]:
    """M18 (module docstring): the handrails and balustrades of every built stair as built: the scene manifest's
    ``stair.guards`` record (``stair_rails.summary``), or for a scene built before 28 Oct 2026 its ``stair.rails``
    (``stair_rails.legacy_guards``), on the stair's plan of the building as built (``stair_access.planned``), the
    level's walls, the openings of the slab above and that floor's guards (the scene's ``void_guard`` runs);
    ``stair_rails.review`` measures them. One finding per stair and rule."""
    from wenart.blender import shell as SH
    from wenart.blender import stair_access as SA
    from wenart.blender import stair_rails as SR

    entries = {ob.get("element_id"): ob for ob in (manifest or {}).get("objects") or []
               if isinstance(ob.get("stair"), dict)}
    guards_by_level: dict = {}
    house_kind = None                                  # the house's balustrade language (a scene before 28 Oct 2026)
    for ob in (manifest or {}).get("objects") or []:
        a = ob.get("assumed") if isinstance(ob.get("assumed"), dict) else {}
        if a.get("detail") == "void_guard":
            guards_by_level.setdefault(ob.get("level_id"), []).extend(
                [(tuple(p), tuple(q)) for p, q in a.get("runs") or []])
            house_kind = house_kind or a.get("balustrade")
    out, n = [], 0
    for level in built.get("levels") or []:
        walls = [w for w in built.get("walls") or [] if w.get("level_id") == level.get("id")]
        up = SH.level_above(built, level)
        openings = SH.slab_openings_above(built, level) or None
        upper = guards_by_level.get(up["id"], []) if up is not None else []
        for it in SA.planned(built, level):
            plan, pid = it.get("plan"), it["piece"].get("id")
            if not plan or pid not in entries:
                continue
            rec = entries[pid]["stair"]
            n += 1
            plan = dict(plan, structure=rec.get("structure"), upper_wall_rects=SH.upper_wall_rects(built, up, plan))
            rects = SR.wall_rects_near([p for f in plan["flights"] for p in f["nosings"]]
                                       + list((plan.get("landing") or {}).get("polygon") or []), walls)
            guards = rec.get("guards") if isinstance(rec.get("guards"), dict) else None
            if guards is None:
                guards = SR.legacy_guards(plan, rec.get("rails") or [], house_kind)
            seen = set()
            for f in SR.review(guards, plan, rects, openings, upper):
                if f["rule"] in seen:
                    continue
                seen.add(f["rule"])
                kind_of = "taste" if f["rule"] == "outside" else None
                out.append(dict(_v("M18", f["severity"], pid, f"stair {pid}: {f['message']}",
                                   it["piece"].get("room_id"), kind=kind_of, rule=f["rule"],
                                   level_id=level.get("id"), legacy=bool(guards.get("legacy")), **f["metrics"]),
                                owner="build", fix=FIX_RAILS))
    return out, n


FIX_FRONT = ("turn it on its wall to its free side, or move it at most 0.5 m (architect F4 free_front; rotate_piece), "
             "or move what stands in front of its door")
FIX_BASIN = ("move the basin at most 0.5 m to a solid stretch of wall (architect H2 clear_basin), else raise the window's "
             "sill to 1.25 m where the documents do not give it (basin_sill)")


def fixtures_in_use(built: dict) -> tuple[list[dict], int]:
    """M19 (module docstring): blocked door and drawer fronts and basins under low windows, on the building as built
    (``fixture_use``: pure)."""
    from wenart.furniture import fixture_use as FU

    out = []
    for r in FU.blocked_fronts(built):
        p = r["problem"]
        out.append(dict(_v("M19", p["severity"], r["piece"], r["message"], r["room_id"], rule="access",
                           free_m=p["free_m"], open_m=p["open_m"], use_m=p["use_m"], blockers=p["blockers"],
                           wall=p["wall"]), owner="furniture", fix=FIX_FRONT))
    for r in FU.basins_under_windows(built):
        out.append(dict(_v("M19", "major", r["piece"], r["message"], r["room_id"], rule="basin_window",
                           window=r["window"], sill_m=r["sill_m"], share=r["share"]), owner="architect", fix=FIX_BASIN))
    n = sum(1 for f in FU._built(built) if str(f.get("type")) in FU.DOOR_FRONTED + FU.BASINS)
    return out, n


def backs_on_walls(built: dict) -> tuple[list[dict], int]:
    """M22 (module docstring): pieces whose back belongs on a wall standing a drawing gap off it, as built."""
    from wenart.furniture import fixture_use as FU

    out = [dict(_v("M22", "major", r["piece"], r["message"], r["room_id"], gap_m=r["gap_m"]), owner="reading",
                fix="snap its back onto the wall (reading fixture_use_fixes; move_piece with snap_wall_id)")
           for r in FU.back_gaps(built)]
    n = sum(1 for f in FU._built(built) if str(f.get("type")) in FU.BACK_TYPES and f.get("front_deg") is not None)
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
        got, n = decor_attached(scene_manifest, built)      # 28 Oct 2026
        note("M14", got, n)
        got, n = door_products(scene_manifest)              # 29 Oct 2026 (UL89)
        note("M20", got, n)
    else:
        checks["M2"] = checks["M6"] = checks["M14"] = checks["M20"] = {"status": "unavailable",
                                                                       "note": "no scene manifest"}
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
    # M24 (29 Oct 2026, lesson UL109): every chimney on the roof, as built (the scene's records) or planned
    try:
        got, n = chimneys_review(built, prep, scene_manifest)
        if n is None:
            checks["M24"] = {"status": "unavailable", "note": "no roof is built"}
        else:
            note("M24", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        checks["M24"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M29 (29 Oct 2026, lessons UL116, UL117, UL120, UL122, UL125): the doors and the walk-ins as a designer shows them
    try:
        got, n = doors_as_designed(built, scene_manifest)
        note("M29", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        checks["M29"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M12 (27 Oct 2026, user on real06: "doors next to each other not making sense"): doors side by side
    try:
        got, n = doors_side_by_side(built)
        note("M12", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError,
            ImportError) as exc:
        checks["M12"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M13 (28 Oct 2026, user on real04's and real06's kitchens): the kitchen as one designed kitchen (hood over every
    # hob, appliances on the worktop line, one wall run that never covers a window)
    try:
        got, n = kitchen_design(built, scene_manifest)
        note("M13", got, n)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError, ImportError) as exc:
        checks["M13"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M15 (28 Oct 2026, users on real04's slope and outdoor floors): the grading of the site as a landscape architect
    # checks it, on the site plan (the architect's paths and steps in) and the scene manifest's floors and walls
    site = (prep or {}).get("site")
    if not site:
        checks["M15"] = {"status": "unavailable", "note": "no site plan (not a whole building, or site: none)"}
    else:
        try:
            from wenart.blender import grading as GR

            got, n = GR.review(site, scene_manifest)
            note("M15", got, n)
        except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
            checks["M15"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M16 (28 Oct 2026, user on real04's roof terrace: "makes no sense to have that table with the carpet outside"):
    # outdoor rooms dressed for outside (pure)
    try:
        from wenart.blender import outdoor as OD

        got, n = OD.review(built)
        note("M16", got, n)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        checks["M16"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M17 (28 Oct 2026, user: "More lights from the ceiling needed"): enough ceiling light for each room's zones and
    # floor. The lighting rule lives with the decor (wenart.furniture, shapely and numpy): Blender's Python has no
    # shapely, so inside the build it is "unavailable" and the pipeline's refresh after the build
    # (cli.refresh_model_review), the code critic and Argus run it. It is imported by name, out of the build
    # script's import closure (build.FINGERPRINT_CODE): the scene never depends on it.
    try:
        import importlib

        CL = importlib.import_module("wenart.furniture.ceiling_lights")
        got, n = CL.review(built, density_of(built))
        note("M17", got, n)
    except ImportError as exc:
        checks["M17"] = {"status": "unavailable", "note": f"{type(exc).__name__}: {exc}"}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        checks["M17"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M18 (28 Oct 2026, user on real04's stairs: "There should have been better indoor stair solutions"): the stairs'
    # handrails as one designed balustrade, on the scene's records of every built stair
    if scene_manifest:
        try:
            got, n = stair_rails_review(built, scene_manifest)
            note("M18", got, n)
        except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError, ImportError,
                StopIteration) as exc:
            checks["M18"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    else:
        checks["M18"] = {"status": "unavailable", "note": "no scene manifest"}
    # M21 (29 Oct 2026, the user's review of real06 run 154514: "There is no TV in the house", "a bit more furniture
    # would be nice", "no library and books", "bath is too empty", "I did not like this light"): the rooms furnished
    # for their use (wenart.furniture.room_use, shapely: imported by name as M17, out of the build's closure)
    try:
        import importlib

        RU = importlib.import_module("wenart.furniture.room_use")
        got, n = RU.review(built)
        note("M21", got, n)
    except ImportError as exc:
        checks["M21"] = {"status": "unavailable", "note": f"{type(exc).__name__}: {exc}"}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        checks["M21"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    # M23 (29 Oct 2026, lesson UL106; user: "I want my renders to be as professional as these ones"): each living room
    # and bedroom against the professional bar as built (a feature panel on the accent wall, the floor's pattern,
    # layered curtains and bedding: wenart.furniture.dressing.review, the rule Argus' U23 reads too). Imported by name,
    # out of the build script's import closure, as M17.
    if scene_manifest:
        try:
            import importlib

            DR = importlib.import_module("wenart.furniture.dressing")
            got, n = DR.review(built, scene_manifest, check="M23")
            note("M23", [dict(_v("M23", g["severity"], g["target"], g["message"], room_id=g["room_id"],
                                 kind="taste", missing=g["missing"]), fix=FIX_PRO_BAR) for g in got], n)
        except ImportError as exc:
            checks["M23"] = {"status": "unavailable", "note": f"{type(exc).__name__}: {exc}"}
        except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
            checks["M23"] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    else:
        checks["M23"] = {"status": "unavailable", "note": "no scene manifest"}
    # M19 / M22 (29 Oct 2026, the user on real06: "This washing machine would not open", "this sink not making sense
    # there", "There is a gap between wall and water faucet not looking good"): fronts that open, basins under a solid
    # wall, backs on their walls, on the building as built (pure)
    for cid, fn in (("M19", fixtures_in_use), ("M22", backs_on_walls)):
        try:
            got, n = fn(built)
            note(cid, got, n)
        except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError, IndexError, ImportError) as exc:
            checks[cid] = {"status": "error", "note": f"{type(exc).__name__}: {exc}"}
    return {"findings": findings, "checks": checks}


FIX_PRO_BAR = ("the decor stage's professional dressing (wenart.furniture.dressing: layered curtains and bedding, the "
               "lights' roles) and the build's finishes (feature_walls on the accent wall, parquet on the wood floor)")


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
