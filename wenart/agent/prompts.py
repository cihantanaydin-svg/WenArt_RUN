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
"""
from __future__ import annotations

import json

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
    "X6": {"what": "exterior camera at eye level 1.5-1.7 m, outside the building, 3/4 corner view with two facades, "
                   "the whole building in frame, verticals straight; one frontal view of the entrance", "how": "CV",
           "scope": "view"},
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
}
ROOM_CHECKS = ("R1", "R2", "R3", "R4", "R5", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "V1", "V2", "V3")
EXTERIOR_CHECKS = ("X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "V2", "V3")
# Milestone 12 (§5.4 "vision only where it adds something"): the room critic is asked only what an image of the
# render shows (looks, wrong objects, the room type, finishes, the camera), never what code measures.
ROOM_LOOK_CHECKS = ("R1", "R4", "F1", "F9", "D1", "D2", "V1", "V2")
CODE_ONLY = tuple(k for k, v in CHECKLIST.items() if v["how"] == "C")

CRITIC_SYSTEM = (
    "You are a strict architectural reviewer. You look at images of a building that a program made from "
    "architectural drawings, and you list only problems that you can clearly see in the images. You answer only "
    "with JSON that follows the given schema. Every finding names one checklist id, one severity and one target id "
    "copied exactly from the list of ids you are given. Never invent an id. If nothing is wrong, answer "
    '{"findings": []}.')

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


def exterior_critic_prompt(view: str, building_note: str, ids: list[str], image_labels: list[str],
                           code_findings: list[dict]) -> str:
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code_findings]
    return "\n".join([
        f"Exterior view {view} of the whole building. {building_note}",
        "Images: " + "; ".join(f"image {i + 1} = {label}" for i, label in enumerate(image_labels)) + ".",
        "", "Ids you may use as target:", *(f"- {i}" for i in ids),
        "", "Checklist:", checklist_text(EXTERIOR_CHECKS),
        "", "Problems the code already measured (do not repeat them):", *(known or ["- none"]),
        "", SEVERITY_TEXT,
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


def room_look_prompt(room: dict, pieces: list[dict], views: list[str], image_labels: list[str],
                     code_findings: list[dict]) -> str:
    """Milestone 12: the room critic on the renders only (looks, wrong objects); built pieces only (B5); the code
    findings are given so they are not repeated."""
    piece_lines = [f"- {p['id']}: {p.get('type')}" for p in pieces]
    known = [f"- {f['check']} {f['severity']} {f['target']}: {f['message']}" for f in code_findings]
    return "\n".join([
        f"Room {room['id']} ({room.get('label')}, type {room.get('room_type')}, "
        f"{round(float(room.get('area_computed') or 0.0), 1)} m2).",
        "Images: " + "; ".join(f"image {i + 1} = {label}" for i, label in enumerate(image_labels)) + ".",
        "", "Ids you may use as target (only pieces that are built and rendered):", f"- {room['id']}: the room itself",
        *piece_lines, *(f"- {v}: camera view" for v in views),
        "", "Checklist (only what the images show; positions, distances and sizes are measured by code):",
        checklist_text(ROOM_LOOK_CHECKS),
        "", "Problems the code already measured (never repeat them, not even under another checklist id):",
        *(known or ["- none"]),
        "", SEVERITY_TEXT,
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
    "set_front for a front into a wall, fix_fixture for a misread size or a piece through a wall or in a door swing "
    "(at most 0.5 m), retype_piece or mark_not_furniture when it is clearly a reading error.\n"
    "3. Drawn furniture is kept; a symbol, mark or line read as furniture: mark_not_furniture with the evidence.\n"
    "4. front_deg is the direction the front faces, degrees counter-clockwise from +x; a piece with its back on a "
    "free wall span faces that span's into_room_deg.\n"
    "5. When you are not sure an edit passes, call dry_run first (it is free). One edit per piece at a time: look at "
    "its result before the next.\n"
    "6. Every edit needs a short reason. When your checklist is done or nothing more can be fixed, call finish with "
    "the findings that stay open.")

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


def plan_prompt(round_no: int, brief: dict, tools: list[str], critical_only: bool) -> str:
    """The first call of a room session: a JSON plan (``PLAN_SCHEMA``) checked against the brief (§5.4)."""
    what = "critical" if critical_only else "critical and major"
    return "\n".join([
        f"Round {round_no}. Make a plan for the {what} fixable findings of {brief['room']['id']}.",
        "Room brief (JSON):", _brief_text(brief), "",
        f"Tools you can use: {', '.join(tools)}.",
        "Answer with a JSON plan: keep the program or name the group options you choose (program.choices), then the "
        "steps in order: for each step the finding ids it fixes, one tool, its target (a piece id, a group id, a "
        "free wall span id or the room id) and why. Put the findings you cannot fix under skip with the reason. Use "
        "only fixable findings, only tools the target allows, and never an edit the memory lists as rejected."])


def session_task(round_no: int, brief: dict, checklist: list[dict], problems: list[str], budget: int,
                 critical_only: bool) -> str:
    """The tool session after the plan: the brief, the checked plan as a checklist, the plan problems."""
    lines = [f"Round {round_no}, room {brief['room']['id']}: carry out the checklist with the tools "
             f"({budget} tool calls at most; dry_run is free).", "Room brief (JSON):", _brief_text(brief), "",
             "Checklist (your checked plan):"]
    lines += [f"{i + 1}. {s['tool']} on {s['target']} for {', '.join(s.get('finding_ids') or []) or '-'}: "
              f"{s.get('why', '')}" for i, s in enumerate(checklist)] or ["- (empty)"]
    if problems:
        lines += ["", "Plan steps refused by the check (do not do them):", *[f"- {p}" for p in problems]]
    lines += ["", ("Only critical findings this time. " if critical_only else "")
              + "Call finish when the checklist is done."]
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
