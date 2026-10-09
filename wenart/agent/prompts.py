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
}
ROOM_CHECKS = ("R1", "R2", "R3", "R4", "R5", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "V1", "V2", "V3")
EXTERIOR_CHECKS = ("X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "V2", "V3")
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
    "orientation and footprint; only a clear drawing error may be fixed.\n"
    "3. Drawn furniture is kept. You may turn it (front), snap it to the nearest wall, resize it to a real product "
    "size, change its type within the room type, or fix a clear drawing error. Remove a drawn piece only when it is "
    "clearly not furniture, with the plan crop as evidence.\n"
    "4. Pieces added by AI may be moved, swapped or removed freely.\n"
    "5. Every edit needs a short reason. One change per call. Look before you change: use room, room_topdown, "
    "plan_crop or view first when you are not sure.\n"
    "6. At most 3 tries per finding. When a finding cannot be fixed, leave it open.\n"
    "7. When you are done, call finish with the findings that are still open.")


def planner_task(round_no: int, findings: list[dict], minor: list[dict], budget: int, critical_only: bool) -> str:
    def line(f):
        return json.dumps({"id": f["id"], "check": f["check"], "severity": f["severity"], "target": f["target"],
                           "room_id": f.get("room_id"), "message": f["message"], "source": f["source"]},
                          ensure_ascii=False)
    head = (f"Round {round_no}. Fix these {'critical' if critical_only else 'critical and major'} findings "
            f"({len(findings)}); you have {budget} tool calls in this round.")
    lines = [head, "", *[line(f) for f in findings]]
    if minor and not critical_only:
        lines += ["", f"Minor findings (fix only when it is cheap and safe; {len(minor)}):",
                  *[line(f) for f in minor[:20]]]
    lines += ["", "Start with the most severe finding. Call finish when done."]
    return "\n".join(lines)
