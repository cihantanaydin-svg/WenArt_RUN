"""Prompts and checklists of the agent (docs/milestone11.md §4, §5, §8; CLAUDE.md furniture and evidence rules).

What: the checklist of §4 as data (``CHECKLIST``: id -> what, how, scope), the critic questions per room and per
exterior view, and the planner's system prompt and task text. Simple, explicit English: the model gets the rules
it must follow, the ids it may name and the exact answer format.

Why one place: the vision critic's JSON schema (``critic_vision``), the code critic and the report use the same
ids and words.

How: ``how`` is ``C`` (code measures it), ``V`` (only an image shows it) or ``CV`` (both); ``scope`` says what a
finding of the check targets (``building``, ``room``, ``piece``, ``opening``, ``view``). The vision critic is asked
only the checks it can see (``V`` and ``CV``) plus the ``C`` ones as context; a ``C``-only finding of the vision
critic that the code measured without a violation is dropped (``critic_vision``).

Fix round after P4b (17 Oct 2026): the X6 rubric is the code's (one rubric: each exterior view keeps its role, a
frontal view is square to the entrance facade by design, an entrance view shows the door up close), and
``camera_note`` tells the exterior critic every camera's role, its measured eye height and pitch, and that a
replayed (set 1) camera is fixed. Why: P4b's cameras flipped between frontal and corner each round.

Fix round after P4a (17 Oct 2026): ``plan_prompt`` and ``session_task`` take ``lighting`` (the final round: critical
findings and the views too dark for the EV cap that one ``set_lighting`` clears, ``loop.FINAL_ROUND_LIGHTING``), and
the session task says that the ``set_lighting`` steps come first (``loop.lighting_first``). Why: P4a's salon
set_lighting was the last of 14 steps and the session's calls ran out before it.

Pass before P5, integration (17 Oct 2026; track F's ask). What: rule 3 of ``PLANNER_SYSTEM_M12`` (the planner the
loop uses) says that a room's plan crop or a view is no evidence that a drawn piece typed from the drawing is not
furniture (only the piece's own recognition crop, which ``plan_crop`` with its piece_id shows), and that a placement
finding (F9, S2, G*) on such a piece is fixed by moving, snapping or turning it. Why: the code refuses that removal
since the pass before P5 (``edit_ops.own_crop_named``), but the agent cited the room's camera crop for it (P3 real04
seq 3282 / 3689 / 3692: ``check/cam_r_L1_koridor_2_1_plan.jpg`` for an F9 / S2 finding on a coffee table), each a
refused try. The Milestone 11 ``PLANNER_SYSTEM`` (the model check of pod G1 only) is unchanged.

Fix round after P5 (22 Oct 2026; the user's decisions of the same day, CLAUDE.md): ``PLANNER_SYSTEM_M12`` names what
the decisions change for the tools. Rule 2: a drawn bathtub or shower up to 5 cm longer than its bay is a misread
size that ``fix_fixture`` shrinks to the nearest real product size that fits (drawn footprint kept). Rule 3: a
placement finding that a drawn piece typed from the drawing does not fit its room (F1, G14) is answered with
``retype_piece``, never a removal (P5 marked the code-typed coffee table f_L1_021 "a stair" with a camera crop), and
the code's own retype of a vision-typed piece (``adjusted_by_ai`` by code, ``drawn_type`` kept) is the reading's,
not the agent's to undo. Rule 7: a long, low building's exterior view may be framed wider or tilted, a
refused exterior camera names the free stretch of its view line, and a ``camera_blocked`` view (the lens touches a
surface, one element fills the frame) is moved to a free point with headroom.

Fix round after P6b (23 Oct 2026), review (the integration's ask): rule 3 of ``PLANNER_SYSTEM_M12`` says that
complete_group needs a verified anchor or a drawn one typed by code from the drawing, as the retype_piece tool
description says (``tools.py``) and ``edit_ops.unsure_group_anchor`` decides since the fix round after P6b. Why: the
planner was told to confirm every unverified anchor first, which costs a try per code-typed anchor (real02's sofas
f_L-1b_041 / 042, the code-typed beds f_L0_019-022).
"""
from __future__ import annotations

import json
from typing import Optional

SEVERITIES = ("critical", "major", "minor")

# §4.1–§4.4.
CHECKLIST: dict[str, dict] = {
    # building and exterior
    "X1": {"what": "outer walls closed on every level; levels stacked on slabs; no floating parts", "how": "C",
           "scope": "building"},
    "X2": {"what": "the roof covers the whole outline (overhang 0.3-0.8 m) and matches the section; no wall rises "
                   "above the roof except gables and parapets; nothing pokes through the roof", "how": "CV",
           "scope": "building"},
    "X3": {"what": "windows and doors on the facades in plausible places; no long blank facade on a habitable room; "
                   "an entrance door at grade, with steps or a ramp when the floor is above grade", "how": "CV",
           "scope": "building"},
    "X4": {"what": "textured ground (grass, paving), a path to the entrance, the plot boundary; the basement below "
                   "grade when the section says so", "how": "CV", "scope": "building"},
    "X5": {"what": "believable scale: storey 2.6-3.3 m, door 2.0-2.2 m, window sill 0.8-1.1 m", "how": "C",
           "scope": "building"},
    # fix round after P4b: one rubric with the code's X6 (exterior_checks._x6): each view keeps its role
    "X6": {"what": "exterior camera outside the building at eye level 1.5-1.7 m above the ground, level (verticals "
                   "straight); each view keeps its role: a corner view shows two facades and the whole building, the "
                   "one frontal view looks square at the entrance facade (one facade, by design), an entrance view "
                   "shows the entrance door up close (not the whole building)", "how": "CV", "scope": "view"},
    "X7": {"what": "sun 25-50 deg above the horizon from the side of the main facade, shadows visible; the sky "
                   "matches the lighting", "how": "CV", "scope": "building"},
    "X8": {"what": "facade, roof and frame materials follow the brief", "how": "C", "scope": "building"},
    # rooms
    "R1": {"what": "the room type fits the area, fixtures and doors (a room with a bathtub is a bathroom; a 3 m2 "
                   "room is not a bedroom)", "how": "CV", "scope": "room"},
    "R2": {"what": "ceiling height plausible; attic slopes follow the roof", "how": "C", "scope": "room"},
    "R3": {"what": "every door opens into free space; the door swing is clear", "how": "C", "scope": "opening"},
    "R4": {"what": "finishes fit the room: tiles in wet rooms, a backsplash (not full-height tiles) in kitchens, the "
                   "brief's colours elsewhere", "how": "CV", "scope": "room"},
    "R5": {"what": "lighting: no black room, no blown-out window", "how": "C", "scope": "view"},
    # furniture
    "F1": {"what": "the right furniture type for the room (no kitchen counter in a bedroom, no dining table in a "
                   "bathroom)", "how": "CV", "scope": "piece"},
    "F2": {"what": "real size: within the type's product sizes, plausible height", "how": "C", "scope": "piece"},
    "F3": {"what": "back to the wall where it belongs: bed headboard, sofa (unless it faces a group in an open "
                   "room), wardrobe, kitchen run, TV unit, bookshelf, dresser, desk", "how": "C", "scope": "piece"},
    "F4": {"what": "fronts face the right way: sofa to the TV unit or coffee table, armchairs to the coffee table, "
                   "dining chairs to the table, desk to a window or wall, bed foot to free space", "how": "CV",
           "scope": "piece"},
    "F5": {"what": "groups belong together: dining table + chairs, bed + nightstands, sofa + coffee table (+ TV "
                   "unit), desk + chair", "how": "C", "scope": "piece"},
    "F6": {"what": "clearances: 0.6 m in front of wardrobes, 0.9 m walkway, 0.7 m beside a bed, 0.75 m behind "
                   "dining chairs", "how": "C", "scope": "piece"},
    "F7": {"what": "no blocked door or window (a piece taller than the sill)", "how": "C", "scope": "piece"},
    "F8": {"what": "no floating piece: a piece away from the walls is part of a group", "how": "C", "scope": "piece"},
    "F9": {"what": "nothing odd in the image: a piece through a wall, a giant box, a piece on the roof, duplicated "
                   "pieces", "how": "V", "scope": "piece"},
    # views
    "V1": {"what": "camera inside the room, not inside a piece, not pressed against a door leaf; eye height "
                   "1.2-1.6 m; the room's main group in frame", "how": "CV", "scope": "view"},
    "V2": {"what": "the render matches the building JSON", "how": "CV", "scope": "view"},
    "V3": {"what": "no debug markers (stripes) in final images", "how": "C", "scope": "view"},
    "V4": {"what": "the polish changed no geometry", "how": "C", "scope": "view"},
    # Milestone 12 (docs/milestone12.md §4.6, §3.5, §5.4): group checks G1-G14 and level checks L1-L7 (code, track G
    # and L), scene checks S1-S6 (Blender, track S), library gaps (track S), and the two looks only an image shows.
    "G1": {"what": "TV unit opposite the sofa: on its axis, facing it, >= 1.5 m away", "how": "C", "scope": "piece"},
    "G2": {"what": "coffee table between sofa and TV, >= 0.30 m from the sofa front", "how": "C", "scope": "piece"},
    "G3": {"what": "armchairs face the coffee table or the sofa, <= 2.5 m from it", "how": "C", "scope": "piece"},
    "G4": {"what": "one nightstand per free side of the bed head, touching the bed side", "how": "C",
           "scope": "piece"},
    "G5": {"what": "bed headboard on a wall; >= 0.60 m free along each free long side and at the foot", "how": "C",
           "scope": "piece"},
    "G6": {"what": "dining chairs = seats of the table, evenly spread, facing it, >= 0.81 m pull-out", "how": "C",
           "scope": "piece"},
    "G7": {"what": "desk with a chair in front, >= 0.80 m behind the desk front", "how": "C", "scope": "piece"},
    "G8": {"what": "kitchen order fridge - sink - hob, landings, triangle, aisle >= 0.90 m", "how": "C",
           "scope": "room"},
    "G9": {"what": "a sink, a hob and a fridge in every kitchen (zone)", "how": "C", "scope": "room"},
    "G10": {"what": "bathroom: toilet + washbasin (+ shower or bath), clear zones in front", "how": "C",
            "scope": "room"},
    "G11": {"what": "walkways: every door reaches every door and use zone (>= 0.60 m, main path >= 0.80 m)",
            "how": "C", "scope": "room"},
    "G12": {"what": "no piece taller than the sill within 0.30 m in front of a window", "how": "C", "scope": "piece"},
    "G13": {"what": ">= 0.80 m free in front of wardrobes and door-fronted storage", "how": "C", "scope": "piece"},
    "G14": {"what": "no piece of a type its room (zone) never holds", "how": "C", "scope": "piece"},
    "L1": {"what": "outside doors: steps, landing or ground in front at the threshold", "how": "C",
           "scope": "opening"},
    "L2": {"what": "a door above the ground has steps or a ramp", "how": "C", "scope": "opening"},
    "L3": {"what": "no floor below the terrain unless it is a basement with light wells", "how": "C",
           "scope": "building"},
    "L4": {"what": "built floors and ground match every level mark within 0.02 m", "how": "C", "scope": "building"},
    "L5": {"what": "steps and ramps within the riser, tread and slope limits", "how": "C", "scope": "building"},
    "L6": {"what": "terrain slope with a retaining edge; no terrain above a sill without a light well", "how": "C",
           "scope": "building"},
    "L7": {"what": "every entrance is seen in an exterior view", "how": "C", "scope": "view"},
    "S1": {"what": "every floor piece stands on its floor", "how": "C", "scope": "piece"},
    "S2": {"what": "no piece cuts a wall or another piece", "how": "C", "scope": "piece"},
    "S3": {"what": "the built front equals the planned front", "how": "C", "scope": "piece"},
    "S4": {"what": "the built size is a real size of its type", "how": "C", "scope": "piece"},
    "S5": {"what": "decor rests on its host (no gap, no cut-through)", "how": "C", "scope": "piece"},
    "S6": {"what": "every built piece is a typed, audited model or a by-design parametric piece", "how": "C",
           "scope": "piece"},
    "LG": {"what": "library gap: no audited model of this type and style fitted", "how": "C", "scope": "piece"},
    "D1": {"what": "decor that looks wrong in the render: a cushion or throw floating, sunk into a back or "
                   "hanging in the air, pillows on pillows", "how": "V", "scope": "piece"},
    "D2": {"what": "a wrong object: a model that is not what its type says (a blob as a throw, a street lamp, a "
                   "table lamp stretched into a floor lamp, a bench as a throw), or a crude low-poly model",
           "how": "V", "scope": "piece"},
    # 25 Oct 2026 (user: "there is no taste in the furniture selection"): the piece that breaks the room's set
    "D3": {"what": "a piece that does not go with the rest of the room: a third wood tone, a second metal finish, "
                   "another design style (an ornate classic piece in a modern room) or a loud colour outside the "
                   "brief's palette; name the one piece that clashes",
           "how": "V", "scope": "piece"},
    # 26 Oct 2026 (user: "problems that somebody looking at it understands: why there is that many rain gutters, why
    # the sink is so low, why doors are up ... the house needs to make sense and needs to look very stylish ... I need
    # ai models to see understand and fix everything before even I look at it"): what a client sees at the first look
    "Q1": {"what": "a door that makes no sense: its leaf or frame does not reach the floor (a gap under it, raised "
                   "over the floor), it floats, or it opens onto nothing (a door high in a facade with no balcony)",
           "how": "V", "scope": "opening"},
    "Q2": {"what": "a fixture at the wrong working height: a washbasin, sink or worktop far below hip height (a rim "
                   "near the knee instead of about 0.85 m), a basin bowl lying on the floor, a toilet in the air",
           "how": "V", "scope": "piece"},
    "Q3": {"what": "a fall risk: an opening on an upper floor that reaches down to the floor with no real guard (a "
                   "full glass pane or a railing with gaps under 11 cm), a stair, landing or floor edge with no railing",
           "how": "V", "scope": "opening"},
    "Q4": {"what": "a room that makes no sense: a kitchen with no counters, sink or hob; a bedroom with no bed; a "
                   "bathroom with no basin; or the furniture of another room (a dining set in a bedroom, a kitchen "
                   "counter in a bedroom)",
           "how": "V", "scope": "room"},
    "Q5": {"what": "pieces that repeat or do not belong together: several tables where one belongs, chairs of "
                   "different models at one table, a folding or garden chair indoors, two sofas of other styles",
           "how": "V", "scope": "piece"},
    "Q6": {"what": "a piece placed the wrong way: a cabinet, wardrobe or bookcase with its back or side to the room, "
                   "standing free in the room, or in front of a window or a door",
           "how": "V", "scope": "piece"},
    "Q7": {"what": "doors and windows that do not fit the house or each other: a dark traditional panelled door in a "
                   "modern or Scandinavian house, busy patterned or opaque glass, different window types side by side, "
                   "a wide door built as one flat slab that reads as a garage door on a house with no garage",
           "how": "V", "scope": "opening"},
    "Q8": {"what": "rain water that makes no sense: more downpipes than the building's corners need, pipes across "
                   "windows or in the air, gutters stepping in and out along the facade",
           "how": "V", "scope": "building"},
    # 26 Oct 2026 (user, circling real06's entrance: "these sections not making sense, AI inspector needs to make
    # sense of this")
    "Q9": {"what": "an entrance that makes no sense: a handrail or railing that crosses in front of a door or another "
                   "stair, two flights of steps that run into each other, a ramp passing in front of a door, steps up "
                   "to a garage door, a door with no way to reach it",
           "how": "V", "scope": "opening"},
}
VISITOR_CHECKS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9")
ROOM_CHECKS = ("R1", "R2", "R3", "R4", "R5", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "V1", "V2", "V3")
EXTERIOR_CHECKS = ("X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "V2", "V3", "Q1", "Q3", "Q7", "Q8", "Q9")
# Milestone 12 (§5.4 "vision only where it adds something"): the room critic is asked only what an image of the
# render shows (looks, wrong objects, the room type, finishes, the camera), never what code measures.
ROOM_LOOK_CHECKS = ("R1", "R4", "F1", "F9", "D1", "D2", "D3", "V1", "V2", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
CODE_ONLY = tuple(k for k, v in CHECKLIST.items() if v["how"] == "C")

CRITIC_SYSTEM = (
    "You are a strict architectural reviewer. You look at images of a building that a program made from "
    "architectural drawings, and you list only problems that you can clearly see in the images. You answer only "
    "with JSON that follows the given schema. Every finding names one checklist id, one severity and one target id "
    "copied exactly from the list of ids you are given. Never invent an id. If nothing is wrong, answer "
    '{"findings": []}.')

VISITOR_TEXT = ("Look at each image the way the client will when they first see it: anything a visitor would point at "
                "(a door off the floor, a basin at knee height, a window you could fall out of, a room that is not "
                "what it is called, pieces that do not go together, too many pipes, railings across a door) is a "
                "finding, even when the "
                "code measured something nearby. The Q checks are such first-look problems: report every one you see.")
SEVERITY_TEXT = ("Severity: critical = the image is clearly wrong (a missing roof, a bed in the middle of the room, a "
                 "blocked door, a piece through a wall); major = clearly odd (a sofa facing a wall, chairs not at the "
                 "table); minor = a matter of taste.")


def checklist_text(ids) -> str:
    return "\n".join(f"- {i}: {CHECKLIST[i]['what']}" for i in ids)


def room_critic_prompt(room: dict, pieces: list[dict], openings: list[dict], views: list[str],
                       image_labels: list[str], code_findings: list[dict]) -> str:
    """The question for one room: its ids, what each image is, the checklist and what the code already found."""
    piece_lines = [f"- {p['id']}: {p.get('type')} ({p.get('source')}), size "
                   f"{'x'.join(str(round(float(s), 2)) for s in (p.get('footprint') or {}).get('size') or [])} m, "
                   f"front {p.get('front_deg')} deg" for p in pieces]
    opening_lines = [f"- {o['id']}: {o.get('type')} width {o.get('width')} m" for o in openings]
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code_findings]
    return "\n".join([
        f"Room {room['id']} ({room.get('label')}, type {room.get('room_type')}, "
        f"{round(float(room.get('area_computed') or 0.0), 1)} m2).",
        "Images: " + "; ".join(f"image {i + 1} = {label}" for i, label in enumerate(image_labels)) + ".",
        "In the top-down image each piece is a box with its id; the arrow shows its front; orange = door and its "
        "swing; blue = window band; red = a check the code failed.",
        "", "Ids you may use as target:", f"- {room['id']}: the room itself", *piece_lines, *opening_lines,
        *(f"- {v}: camera view" for v in views),
        "", "Checklist:", checklist_text(ROOM_CHECKS),
        "", "Problems the code already measured (do not repeat them):", *(known or ["- none"]),
        "", SEVERITY_TEXT,
        "List what is wrong with this room in the images. For each finding give evidence_image = the number of the "
        "image that shows it."])


# Fix round after P4b (camera_note): what each exterior camera role is, for the critic.
CAMERA_ROLES = {
    "corner": "a 3/4 corner view that shows two facades ({sides}) and the whole building",
    "frontal": "the one frontal view of the {sides} (entrance) facade that X6 asks for: a view square to that facade, "
               "showing one facade, is by design and NOT a finding (do not report that it is not a corner view)",
    "elevation": "a frontal elevation view of the {sides} facade: a view square to that facade is by design and NOT a "
                 "finding (do not report that it is not a corner view)",
    "entrance": "the eye-level view of the entrance door ({sides} facade): the door up close with its path and steps "
                "is by design and NOT a finding (do not report that it is not a corner view or that the whole "
                "building is not in the frame)",
    "agent": "a view the agent placed",
}


def camera_note(camera: Optional[dict], eye: Optional[dict] = None, role: Optional[str] = None) -> str:
    """Round 2 (Milestone 13 D8, track T6): what the exterior critic is told about a camera the policy allows above
    eye level: a record with ``aerial_allowed`` (the one true aerial view ``ext_5``, the site view) or ``view``
    aerial. A true aerial is not a finding: its height, pitch and the missing eye level are by design; the critic
    judges the building and the site in it. '' without a record.

    Fix round after P4b (17 Oct 2026; pod P4b, real03): every other exterior camera is told its role
    (``CAMERA_ROLES``: corner, frontal, elevation, entrance, agent) and, with ``eye``
    (``critic_vision.camera_eye``), its eye height above the ground and its pitch measured by code; a camera replayed
    from the baseline (set 1) is told that its pose is fixed (decision 1 of 17 Oct 2026). Why: the X6 rubric asked
    every view for a 3/4 corner at 1.5-1.7 m, so the critic called the frontal and the entrance view wrong and 5 views
    "low angle" at 1.60 m above the ground; the cameras flipped between frontal and corner each round.

    Pass before P5 (17 Oct 2026): ``role`` (``critic_vision.camera_role``) replaces the camera's ``view``: an agent
    view that is X6's frontal view (square to the main facade) is told as ``CAMERA_ROLES["frontal"]``, not "a view
    the agent placed" (real04's frontal view is one the agent adds: the planner drops ext_6)."""
    if not isinstance(camera, dict):
        return ""
    if camera.get("aerial_allowed") or camera.get("site_view") or camera.get("view") == "aerial":
        what = "site view (the building in its plot, with the horizon)" if camera.get("site_view") else "aerial view"
        return (f"This view is the {what} the camera policy allows (one true aerial view beside the eye-level corner "
                f"and frontal views): its height above eye level, its downward pitch and the whole-building framing "
                f"are by design and are NOT a finding (do not report X6 or V1 for the camera of this view); judge the "
                f"roof, the facades, the site and the lighting it shows.")
    role = role or camera.get("view")
    parts = []
    if role in CAMERA_ROLES:
        sides = ", ".join(str(x) for x in camera.get("sides") or []) or "its"
        parts.append(f"The camera of this view is {CAMERA_ROLES[role].format(sides=sides)}.")
    if role in ("corner", "frontal") and isinstance(camera.get("long_low"), dict):
        # integration of the fix round after P5 (E_exterior's ask; user decision (2) of 22 Oct 2026): the closer
        # framing of a long, low building (exterior.long_low) is by design, so the critic does not push it back out
        fill = float(camera["long_low"].get("fill_target") or 0.9)
        parts.append(f"It is framed close by design: a long, low building fills up to {fill * 100:.0f}% of the frame "
                     f"width (user decision of 22 Oct 2026); do not report that the camera is too close or the "
                     f"building too large.")
    if isinstance(eye, dict) and eye.get("eye_m") is not None:
        parts.append(f"Measured by code: the eye is {float(eye['eye_m']):.2f} m above the ground, pitch "
                     f"{float(eye.get('pitch_deg') or 0.0):.1f} deg; do not report its height or angle from the image.")
    if camera.get("source") == "replayed" or isinstance(camera.get("replaced_replayed"), dict):
        parts.append("The camera is replayed from the baseline run (set 1): its pose is fixed for the before/after "
                     "comparison; judge the building and the site, not the camera placement.")
    return " ".join(parts)


def exterior_critic_prompt(view: str, building_note: str, ids: list[str], image_labels: list[str],
                           code_findings: list[dict]) -> str:
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code_findings]
    return "\n".join([
        f"Exterior view {view} of the whole building. {building_note}",
        "Images: " + "; ".join(f"image {i + 1} = {label}" for i, label in enumerate(image_labels)) + ".",
        "", "Ids you may use as target:", *(f"- {i}" for i in ids),
        "", "Checklist:", checklist_text(EXTERIOR_CHECKS),
        "", "Problems the code already measured (do not repeat them):", *(known or ["- none"]),
        "", VISITOR_TEXT, SEVERITY_TEXT,
        "List what is wrong with the building or its site in the image. Use the view id as target for camera "
        "problems and 'building' for the building as a whole."])


PLANNER_SYSTEM = (
    "You are the planner of an architectural visualisation pipeline. You fix the problems in the findings list by "
    "calling the tools. You never write code and never answer with prose only while problems are open.\n"
    "Rules you must follow (they are also checked by code; a rejected edit tells you why):\n"
    "1. Walls, openings and room outlines from the drawings are locked. Use correct_geometry only for a clear "
    "drawing error (a gap up to 0.15 m, a duplicate wall within 0.02 m, an opening up to 0.10 m off its wall).\n"
    "2. Drawn fixed equipment (stairs, kitchen runs, island, appliances, sanitary ware) keeps its type, place, "
    "orientation and footprint; only a clear drawing error may be fixed. Fixed equipment in a room that never holds "
    "it (a kitchen counter or a toilet in a stair room, a shaft or on a balcony, a stove in a bedroom) is such an "
    "error: change_type it to what the plan crop shows (a stair) or remove it, with the reason.\n"
    "3. Drawn furniture is kept. You may turn it (front), snap it to the nearest wall, resize it to a real product "
    "size, change its type within the room type, or fix a clear drawing error. Remove a drawn piece only when it is "
    "clearly not furniture, with the plan crop as evidence.\n"
    "4. Pieces added by AI may be moved, swapped or removed freely.\n"
    "5. Every edit needs a short reason. One change per call. Look before you change: use room, room_topdown, "
    "plan_crop or view first when you are not sure.\n"
    "6. At most 3 tries per finding. When a finding cannot be fixed, leave it open.\n"
    "7. An unexplained drawn box (F9, type unknown) must not stay a box: look at its plan crop and change_type it to "
    "the type its footprint, room and neighbours show, or remove it when it is clearly not furniture (a rug outline, "
    "a label, a detail drawn inside another piece).\n"
    "8. When you are done, call finish with the findings that are still open.")


def doubt_note(piece: dict) -> str:
    """`` (look closely, D2: ...)`` for a piece whose model, or a decor model on it (``piece["decor_doubt"]``, set by
    the caller), the library audit kept with a vision doubt; '' otherwise."""
    from wenart.furniture import catalog as C
    parts = []
    own = C.vision_doubt(piece.get("asset") if isinstance(piece.get("asset"), dict) else None)
    if own:
        parts.append(f"its 3D model is in doubt ({own[0]})")
    for d in piece.get("decor_doubt") or []:
        parts.append(f"the {d['type']} on it is in doubt ({d['doubt'][0]})")
    if not parts:
        return ""
    return " (look closely, D2: " + "; ".join(parts) + "; is it a real, single, well-made object of its type?)"


def built_as_note(p: dict) -> str:
    """`` (built by our module builder / parametric family, not a library model: ...)`` for a piece whose asset is a
    module builder or a parametric family (Milestone 13: the critic must not call it a crude or wrong model; the
    library gap is reported by code); '' for a library model."""
    asset = p.get("asset") if isinstance(p.get("asset"), dict) else {}
    method = asset.get("method")
    if method == "module":
        return " (built by our module builder with real module sizes, not a library model: judge only a clearly " \
               "broken shape)"
    if method == "parametric":
        return " (built by our parametric family, not a library model: judge only a clearly broken shape)"
    return ""


def context_lines(context: Optional[dict]) -> list[str]:
    """Milestone 13: what the critic and the planner must know about the room: the licence mode, the pieces built
    below the library level and the drawn groups (``brief.room_brief`` keys ``licence_mode``, ``below_library``,
    ``drawn_groups``); [] without a context."""
    if not context:
        return []
    lines = []
    mode = context.get("licence_mode")
    if mode:
        lines.append(f"Library licence mode: {mode} (commercial = commercial-safe models only; relaxed = non-"
                     f"commercial, share-alike and tool-flagged models allowed for this proof of concept).")
    below = context.get("below_library") or []
    if below:
        lines.append("Pieces built below the library level (no audited model fitted; ours, with real proportions): "
                     + "; ".join(f"{b.get('id')} {b.get('type')} ({b.get('method')}: {b.get('builder')})"
                                 for b in below) + ".")
    groups = context.get("drawn_groups") or []
    if groups:
        parts = []
        for g in groups:
            members = ", ".join(g.get("members") or []) or "no drawn partner"
            built = "" if g.get("anchor_built", True) else " (anchor not built)"
            parts.append(f"{g.get('anchor_type')} {g.get('anchor_id')} with {members}{built}")
        lines.append("Drawn groups (the architect drew the anchor with its partners; they move as one unit, every "
                     "member within 0.5 m of its drawn centre): " + "; ".join(parts) + ".")
    return lines


def room_look_prompt(room: dict, pieces: list[dict], views: list[str], image_labels: list[str],
                     code_findings: list[dict], context: Optional[dict] = None,
                     openings: Optional[list[dict]] = None) -> str:
    """Milestone 12: the room critic on the renders only (looks, wrong objects); built pieces only (B5); the code
    findings are given so they are not repeated. A piece whose library model (or a decor model on it) the audit kept
    with a vision doubt (decision 1a) is marked so the critic looks at it (D2). Milestone 13: ``context`` (the
    licence mode, the pieces built below the library level, the drawn groups; ``context_lines``) tells the critic
    what it sees."""
    piece_lines = [f"- {p['id']}: {p.get('type')}{doubt_note(p)}{built_as_note(p)}" for p in pieces]
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code_findings]
    return "\n".join([
        f"Room {room['id']} ({room.get('label')}, type {room.get('room_type')}, "
        f"{round(float(room.get('area_computed') or 0.0), 1)} m2).",
        "Images: " + "; ".join(f"image {i + 1} = {label}" for i, label in enumerate(image_labels)) + ".",
        *context_lines(context),
        "", "Ids you may use as target (only pieces that are built and rendered):", f"- {room['id']}: the room itself",
        *piece_lines, *(f"- {o['id']}: {o.get('type')} {float(o.get('width') or 0):.2f} m wide" for o in openings or []
                        if o.get("id")),
        *(f"- {v}: camera view" for v in views),
        "", "Checklist (only what the images show; positions, distances and sizes are measured by code):",
        checklist_text(ROOM_LOOK_CHECKS),
        "", "Problems the code already measured (never repeat them, not even under another checklist id):",
        *(known or ["- none"]),
        "", VISITOR_TEXT, SEVERITY_TEXT,
        "List what is wrong in the renders. For each finding give evidence_image = the number of the image that shows "
        "it."])


# --------------------------------------------------------------------------
# Milestone 12: the planner of one room session (docs/milestone12.md §5.2-§5.4)
# --------------------------------------------------------------------------

PLANNER_SYSTEM_M12 = (
    "You are the planner of an architectural visualisation pipeline. You fix the problems of ONE room (or of the "
    "building) by calling tools. You never write code.\n"
    "You get a room brief: the built pieces with their lock state and the tools each piece allows (with the move "
    "allowance left), the groups, the free wall spans, the solver's candidate layouts and the findings. Only the "
    "findings under 'fixable' are your work; each lists the tools that can fix it. Never edit a piece or a finding "
    "under 'not yours' or 'not_built'. The memory lists edits that were already rejected: never send them again.\n"
    "Rules (checked by code; a rejected edit tells you which check failed and by how much):\n"
    "1. Work on groups, not single pieces: relayout_room with a solver candidate, place_group, complete_group, "
    "move_group (to a free wall span). Use move_piece only for a small fix of one piece.\n"
    "2. Drawn fixed equipment (stairs, kitchen runs, appliances, sanitary ware) keeps type, place and footprint; only "
    "rotate_piece for a front into a wall, fix_fixture for a misread size or a piece through a wall or in a door swing "
    "(at most 0.5 m), retype_piece or mark_not_furniture only for a fixture read in a room that never holds it "
    "(a clear reading error; the piece's allowed tools say so). It is never marked as not furniture otherwise. Call "
    "fix_fixture without center first; when it answers 'no valid spot', no centre will do: the finding stays for "
    "review. A drawn bathtub or shower up to 5 cm longer than its bay is a misread size: fix_fixture without center "
    "and size shrinks it to the nearest real product size that fits (its drawn footprint is kept).\n"
    "3. Drawn furniture is kept; a symbol, mark or line read as furniture: mark_not_furniture with the evidence. "
    "The room's plan crop or a view is no evidence that a drawn piece typed from the drawing is not furniture (only "
    "its own recognition crop is: plan_crop with its piece_id shows it); for a placement finding (F9, S2, G*) on such "
    "a piece, move, snap or turn it. When such a piece's type does not fit its room (F1, G14), retype_piece gives it "
    "a type that fits its footprint and the room; never mark it or remove it for that. A piece the code already "
    "retyped from its size, room and neighbours (adjusted_by_ai by code, drawn_type kept) keeps that type. "
    "retype_piece with the piece's own type confirms an unverified piece (complete_group needs a verified anchor or "
    "a drawn one typed by code from the drawing); "
    "a confirm changes nothing in the render, so it never clears a finding about how a piece looks. "
    "mark_not_furniture on an untyped piece needs the image path of the plan crop you read in its evidence "
    "(check/<view>_plan.jpg, from plan_crop or view); without it the mark is refused (no_crop).\n"
    "4. rotate_piece turns a piece; set_front only gives a front to a piece that has none (front_inferred). front_deg "
    "is the direction the front faces, degrees counter-clockwise from +x; a piece with its back on a "
    "free wall span faces that span's into_room_deg.\n"
    "5. When you are not sure an edit passes, call dry_run first (it is free; the same dry run again is answered "
    "from the first one and counts as a try). One edit per piece at a time: look at its result before the next.\n"
    "6. Every edit needs a short reason. When your checklist is done or nothing more can be fixed, call finish with "
    "the findings that stay open.\n"
    "7. An edit is accepted only when the finding it targets is gone in the code re-check and no new critical "
    "finding appears (nor a G9 / G10 for a fixture the edit removed); an edit that changes nothing measurable is "
    "rejected. A step's critical findings must all be gone; its major ones may stay when none gets worse. "
    "set_room_type furnishes nothing: an empty room needs place_group or relayout_room. The brief's drawn_groups "
    "move as one "
    "unit (place_group re-solves them around the drawn anchor); below_library pieces are our module or parametric "
    "builds, not wrong models (the library gap is already recorded); the licence_mode says which library models "
    "may be used. The roof, site, sun, materials, levels and exterior cameras belong to the building session only. "
    "Cameras replayed from the baseline run (set 1) are fixed: never set or remove them (add_camera with a new view "
    "id adds a view); a frontal view stays square to its facade, an entrance view stays close in front of its door. "
    "An exterior view of a long, low building may be framed wider or tilted; a refused exterior camera names the "
    "free stretch of its view line. A camera_blocked view (the lens touches a surface or "
    "one element fills the frame) is moved to a free point of its room with headroom (set_camera).\n"
    "8. A fixable finding may name an edit_target: the piece the tool must act on instead of the finding's target "
    "(a chair or nightstand stands around an anchor the fit left unbuilt: retype_piece types and builds an unknown "
    "anchor, place_group re-solves the drawn group so the refit builds a typed one), or the room set_lighting acts "
    "on for a view too dark for the EV cap (lighting_dark). Use the edit_target as the step's target; never move "
    "the piece that stands around it.")

PLAN_SCHEMA: dict = {
    "type": "object", "additionalProperties": False, "required": ["room_id", "program", "steps"],
    "properties": {
        "room_id": {"type": "string", "minLength": 1, "maxLength": 80},
        "program": {"type": "object", "additionalProperties": False, "required": ["keep"],
                    "properties": {"keep": {"type": "boolean"},
                                   "choices": {"type": "array", "maxItems": 8, "items": {
                                       "type": "object", "additionalProperties": False,
                                       "required": ["group_id", "option"],
                                       "properties": {"group_id": {"type": "string"},
                                                      "option": {"type": "string"}}}}}},
        "steps": {"type": "array", "maxItems": 12, "items": {
            "type": "object", "additionalProperties": False, "required": ["finding_ids", "tool", "target", "why"],
            "properties": {"finding_ids": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                           "tool": {"type": "string", "minLength": 1, "maxLength": 40},
                           "target": {"type": "string", "minLength": 1, "maxLength": 80},
                           "why": {"type": "string", "minLength": 3, "maxLength": 300}}}},
        "skip": {"type": "array", "maxItems": 20, "items": {
            "type": "object", "additionalProperties": False, "required": ["finding_id", "why"],
            "properties": {"finding_id": {"type": "string"}, "why": {"type": "string", "maxLength": 300}}}},
    }}


def _brief_text(brief: dict) -> str:
    return json.dumps(brief, ensure_ascii=False, separators=(",", ":"), default=str)


FINAL_LIGHTING_WORDS = "the views too dark for the EV cap that one set_lighting clears"


def plan_prompt(round_no: int, brief: dict, tools: list[str], critical_only: bool, lighting: bool = False) -> str:
    """The first call of a room session: a JSON plan (``PLAN_SCHEMA``) checked against the brief (§5.4).
    ``lighting`` (fix round after P4a): the final round also takes ``FINAL_LIGHTING_WORDS``."""
    what = "critical" if critical_only else "critical and major"
    if critical_only and lighting:
        what += f" (and {FINAL_LIGHTING_WORDS})"
    return "\n".join([
        f"Round {round_no}. Make a plan for the {what} fixable findings of {brief['room']['id']}.",
        "Room brief (JSON):", _brief_text(brief), "",
        f"Tools you can use: {', '.join(tools)}.",
        "Answer with a JSON plan: keep the program or name the group options you choose (program.choices), then the "
        "steps in order: for each step the finding ids it fixes, one tool, its target (a piece id, a group id, a "
        "free wall span id or the room id) and why. Put the findings you cannot fix under skip with the reason. Use "
        "only fixable findings, only tools the target allows, and never an edit the memory lists as rejected."])


def session_task(round_no: int, brief: dict, checklist: list[dict], problems: list[str], budget: int,
                 critical_only: bool, lighting: bool = False) -> str:
    """The tool session after the plan: the brief, the checked plan as a checklist, the plan problems. Fix round
    after P4a: the ``set_lighting`` steps first; ``lighting``: the final round also lights the too-dark views."""
    lines = [f"Round {round_no}, room {brief['room']['id']}: carry out the checklist with the tools "
             f"({budget} tool calls at most; dry_run is free).", "Room brief (JSON):", _brief_text(brief), "",
             "Checklist (your checked plan):"]
    lines += [f"{i + 1}. {s['tool']} on {s['target']} for {', '.join(s.get('finding_ids') or []) or '-'}: "
              f"{s.get('why', '')}" for i, s in enumerate(checklist)] or ["- (empty)"]
    if problems:
        lines += ["", "Plan steps refused by the check (do not do them):", *[f"- {p}" for p in problems]]
    if any(s.get("tool") == "set_lighting" for s in checklist):
        lines += ["", "Do the set_lighting steps first: they do not depend on the furniture, and the factor the "
                      "finding names is what the view needs."]
    only = ""
    if critical_only:
        only = (f"Only critical findings and {FINAL_LIGHTING_WORDS} this time. " if lighting
                else "Only critical findings this time. ")
    lines += ["", only + "Call finish when the checklist is done."]
    return "\n".join(lines)


def planner_task(round_no: int, findings: list[dict], minor: list[dict], budget: int, critical_only: bool) -> str:
    def line(f):
        return json.dumps({"id": f["id"], "check": f["check"], "severity": f["severity"], "target": f["target"],
                           "room_id": f.get("room_id"), "message": f["message"], "source": f["source"]},
                          ensure_ascii=False)
    rooms = sorted({str(f.get("room_id")) for f in findings if f.get("room_id")})
    where = f" in {rooms[0]}" if len(rooms) == 1 else ""
    head = (f"Round {round_no}. Fix these {'critical' if critical_only else 'critical and major'} findings{where} "
            f"({len(findings)}); you have {budget} tool calls for them.")
    lines = [head, "", *[line(f) for f in findings]]
    if minor and not critical_only:
        lines += ["", f"Minor findings (fix only when it is cheap and safe; {len(minor)}):",
                  *[line(f) for f in minor[:20]]]
    lines += ["", "Start with the most severe finding. Call finish when done."]
    return "\n".join(lines)
