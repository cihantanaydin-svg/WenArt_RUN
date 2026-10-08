"""The layout prompt: one per room type, English with the Turkish room label.

What the model gets (docs/milestone4.md section 3): the style text, the room
polygon in metres, the doors (with the swing side) and windows (with the sill
height) as compact JSON, the allowed types for the room type, the size options
per type and the rules the placer will check. Pass 1 and pass 2 differ in the
order of the instruction blocks (and in the seed, set by the client), so the
two answers are independent enough for the agreement confidence.

Everything the model may answer is rendered from ``schemas.py`` so prompt and
schema cannot drift apart (``tests/test_layout.py`` checks this).

Milestone 7 (docs/milestone7.md §6.5): texts for ``dining`` rooms; the
``prayer`` entry exists for completeness only (a prayer room is never
furnished by AI, ``schemas.NOT_FURNISHED_ROOM_TYPES``, so no prompt is sent).

Milestone 10 (docs/milestone10.md §2.3): the empty-room prompt lists the
room's ``schemas.layout_types``; ``completion_prompt`` is the question for a
room with drawn furniture: the room (label, type, subtype, polygon, area),
the doors (approach point, swing) and windows (sill), the drawn pieces (id,
type, box, front, anchor, the wall an against-wall piece stands on, fixed or
changeable), the types a drawn piece may become and the types the AI may add
(with their size options and counts), the missing types and the style text.
The per-room answer schema (``wenart.furniture.complete.answer_schema``) is
built from the same lists.
"""
from __future__ import annotations

import json
from typing import Any

from wenart.furniture import schemas

# Milestone 7: "of a home" (was "of a Turkish apartment"): real01 is an Indian house with English labels.
SYSTEM_PROMPT = (
    "You are an interior planner. You place furniture in one empty room of a home (an "
    "apartment or a house) and answer only with JSON that follows the given schema. Use the room "
    "polygon, doors and windows exactly as given. Never place furniture outside the room, "
    "on a door, in a door swing or overlapping another piece."
)

ROOM_TYPE_TEXT: dict[str, str] = {
    "living": "living room (Turkish: SALON)",
    "bedroom": "bedroom (Turkish: YATAK ODASI, ÇOCUK ODASI = children's room, EBEVEYN YATAK ODASI = master bedroom)",
    "kitchen": "kitchen (Turkish: MUTFAK)",
    "bathroom": "bathroom (Turkish: BANYO)",
    "wc": "toilet room (Turkish: WC)",
    "hall": "hall or corridor (Turkish: HOL, ANTRE, KORİDOR)",
    "dining": "dining room (Turkish: YEMEK ODASI)",
    "prayer": "prayer room (Indian plans: POOJA, PUJA, MANDIR)",
    "other": "room of unspecified use",
}

# What a good layout of each room type contains (short, so the model does not over-furnish).
# Milestone 10: the new types where they fit (sideboard, console_table, shoe_cabinet, bench, tall_cabinet, a child's
# bunk bed or crib, the desk's office_chair).
ROOM_GUIDE: dict[str, str] = {
    "living": "one sofa with its back to a wall facing a tv_unit on the opposite wall, a coffee table in "
              "front of the sofa, optionally one armchair and a bookshelf or a sideboard; a dining table only "
              "when the room is larger than 18 m².",
    "bedroom": "one bed (bed_double for a master bedroom, bed_single, bunk_bed or crib for a children's room) "
               "with the headboard against a wall and not under the door, a nightstand on each free side of a "
               "double bed, one wardrobe against a wall, optionally a desk with an office_chair.",
    "kitchen": "a kitchen_counter along the longest free wall, sink_kitchen and stove inside the counter "
               "line (place them as separate pieces that touch the counter ends), a fridge at one end, "
               "optionally a tall_cabinet next to the fridge, a small dining table with chairs only when "
               "there is room.",
    "bathroom": "washbasin, toilet and a shower or bathtub, each against a wall, the toilet not directly "
                "opposite the door.",
    "wc": "one toilet against the wall opposite the door and one small washbasin.",
    "hall": "at most one slim console_table, shoe_cabinet, bench or bookshelf against a wall; keep the "
            "corridor between the doors free.",
    "dining": "one dining table in the middle of the room with chairs on its long sides (each chair's "
              "front towards the table), optionally a sideboard or a bookshelf against a wall; "
              "keep the walkway around the table free.",
    "prayer": "nothing: a prayer room is never furnished by AI (this text is never sent).",
    "other": "a small table with chairs or a desk and a bookshelf; keep it sparse.",
}


def _round(value: float) -> float:
    return round(float(value), 2)


def room_block(room: dict, doors: list[dict], windows: list[dict]) -> dict[str, Any]:
    """The compact JSON of the room as given to the model (also written to the debug log)."""
    return {
        "room_id": room["id"],
        "label": room["label"],
        "room_type": room.get("room_type", "other"),
        "area_m2": _round(room["area_computed"]),
        "polygon_m": [[_round(x), _round(y)] for x, y in room["polygon"]],
        "doors": [{
            "id": d["id"], "center": [_round(d["center"][0]), _round(d["center"][1])],
            "width": _round(d["width"]),
            "opens_into_this_room": d.get("swing_side") == room["id"],
        } for d in doors],
        "windows": [{
            "id": w["id"], "center": [_round(w["center"][0]), _round(w["center"][1])],
            "width": _round(w["width"]),
            "sill_height": _round(w["sill_height"]) if w.get("sill_height") is not None else None,
        } for w in windows],
    }


def _size_table(types: tuple[str, ...]) -> str:
    lines = []
    for ftype in types:
        options = ", ".join(f"[{w}, {d}]" for w, d in schemas.SIZE_OPTIONS[ftype])
        wall = " (usually against a wall)" if ftype in schemas.WALL_TYPES else ""
        lines.append(f"- {ftype}: height {schemas.HEIGHTS[ftype]} m, size options {options}{wall}")
    return "\n".join(lines)


def _rules_block(sill_note: str) -> str:
    return (
        "Rules that are checked afterwards (pieces that fail are moved or removed):\n"
        "- every footprint lies fully inside the room polygon; pieces do not overlap;\n"
        "- keep 0.6 m free in front of beds, sofas, desks and wardrobes (front = the -Y side at "
        "rotation 0, rotated with the piece);\n"
        "- keep a 0.9 m wide walkway from every door to every other door and window;\n"
        "- keep the door swing free: a half circle with the door width as radius inside the room "
        "the door opens into, and 0.6 m in front of every door;\n"
        f"- within 0.3 m of a window nothing may be taller than the sill{sill_note}; beds, sofas and "
        "tables may stand under a window;\n"
        "- a piece with against_wall true must touch a wall with its back edge (its +Y side at "
        "rotation 0): choose rotation_deg so the back faces the wall (0 = back to a wall on the +Y "
        "side, 90 = back to a wall on the -X side, 180 = back to a wall on the -Y side, "
        "270 = back to a wall on the +X side) and set the centre half the depth away from the wall."
    )


def _fields_block(types: tuple[str, ...]) -> str:
    return (
        "Fields of the answer: pieces, a list (at most "
        f"{schemas.MAX_PIECES}, the most important piece first) of objects with\n"
        f"- type: one of {', '.join(types)}\n"
        "- center: [x, y] of the footprint centre in metres, in the same frame as the room polygon\n"
        "- rotation_deg: 0..360 counter-clockwise; at 0 the width runs along X and the front faces -Y\n"
        "- size: [width, depth] in metres, exactly one of the size options of the type\n"
        "- against_wall: true when the back edge touches a wall\n"
        "- reason: one short sentence why the piece is there"
    )


def layout_prompt(room: dict, doors: list[dict], windows: list[dict], style_text: str, pass_no: int = 1) -> str:
    """The user prompt for one room. ``pass_no`` 2 reorders the instruction blocks."""
    room_type = room.get("room_type", "other")
    if room_type not in schemas.ALLOWED_TYPES:
        room_type = "other"
    types = schemas.layout_types(room_type, room.get("room_subtype"))
    sill_note = ""
    if any(w.get("sill_height") is None for w in windows):
        sill_note = " (sill_height null = 0.9 m assumed)"
    task = (f"Task: furnish this empty {ROOM_TYPE_TEXT[room_type]} labelled '{room['label']}' on the plan. "
            f"Style brief: {style_text.strip() or 'none'}.")
    guide = f"A good layout for this room type: {ROOM_GUIDE[room_type]}"
    room_json = "Room (metres, X right, Y up):\n" + json.dumps(room_block(room, doors, windows), ensure_ascii=False)
    sizes = "Allowed types with their size options [width, depth]:\n" + _size_table(types)
    rules = _rules_block(sill_note)
    fields = _fields_block(types)
    end = "Answer only with JSON."
    if pass_no == 1:
        blocks = [task, room_json, sizes, rules, guide, fields, end]
    else:
        blocks = [task, guide, rules, sizes, room_json, fields, end]
    return "\n\n".join(blocks)


# --------------------------------------------------------------------------
# Milestone 10: completing a room with drawn furniture (docs/milestone10.md §2.3)
# --------------------------------------------------------------------------

COMPLETION_SYSTEM_PROMPT = (
    "You are an interior planner. You complete one room of a home whose plan already draws some furniture, and "
    "answer only with JSON that follows the given schema. Drawn pieces stay where they are: you may change the type, "
    "size and look of a piece marked changeable, never its place or the direction it faces, and never a fixed "
    "piece. New pieces go only on free floor: never outside the room, on a door, in a door swing, on a walkway or "
    "overlapping another piece."
)

# What the completed room should get (short, so the model does not over-furnish).
COMPLETION_GUIDE: dict[str, str] = {
    "living": "a coffee table in front of the sofa (beyond the sofa's 0.6 m clearance) and a tv_unit against the "
              "wall the sofa faces; an armchair, a sideboard or a bookshelf only where the room stays open.",
    "bedroom": "a nightstand on each free side of a double bed (one beside a single bed), touching the headboard "
               "wall; a wardrobe against a free wall, not in front of a window; a bench at the foot of the bed or "
               "a desk with an office_chair only when the room stays open.",
    "dining": "chairs on the long sides of the table, each chair's front towards the table and close to its edge; "
              "a sideboard against a free wall.",
    "kitchen": "bar stools at the free long side of the island; a small dining table with chairs only where 1.2 m "
               "stays free; a tall_cabinet at the end of the counter run.",
    "hall": "one slim piece (console_table, shoe_cabinet or bench) against a wall; keep the corridor between the "
            "doors free.",
    "other": "a few pieces that suit the room; keep it sparse.",
    "bathroom": "nothing is added: sanitary ware hangs on the plumbing.",
    "wc": "nothing is added: sanitary ware hangs on the plumbing.",
}


def _counts(table: dict) -> str:
    return ", ".join(f"{t} ({n})" for t, n in table.items())


def _completion_fields(change_types: list[str], add_types: list[str], keep_size: bool) -> str:
    if keep_size or not change_types:
        changes = "- changes: always an empty list [] (no drawn piece may change its type or size here)"
    else:
        changes = ("- changes: a list (only the drawn pieces you change) of objects with id (a changeable drawn "
                   f"piece), type (one of {', '.join(change_types)}), size ([width, depth], one of the size options "
                   "of the new type), style (a style family), colour (one of the colours) and reason (one short "
                   "sentence)")
    if add_types:
        added = ("- added: a list (the most important piece first) of objects with type (one of "
                 f"{', '.join(add_types)}), center ([x, y] of the footprint centre in metres, in the same frame as "
                 "the room polygon), rotation_deg (0..360 counter-clockwise; at 0 the width runs along X and the "
                 "front faces -Y), size ([width, depth], exactly one of the size options of the type), against_wall "
                 "(true when the back edge touches a wall) and reason (one short sentence)")
    else:
        added = "- added: always an empty list [] (nothing may be added here)"
    return "Fields of the answer:\n" + changes + "\n" + added


def completion_prompt(question: dict, style_text: str, pass_no: int = 1) -> str:
    """The user prompt for one room with drawn furniture; ``pass_no`` 2 reorders the blocks.

    ``question`` (built by ``wenart.furniture.complete``): ``room`` (the room block with doors and windows),
    ``drawn`` (the drawn pieces), ``change_types``, ``add`` (type -> how many may be added), ``missing`` (type ->
    count), ``anchor_missing``, ``anchors``, ``styles``, ``colours``, ``keep_size``.
    """
    room = question["room"]
    room_type = room.get("room_type") or "other"
    if room_type not in ROOM_TYPE_TEXT:
        room_type = "other"
    child = " (a child's room)" if room.get("room_subtype") == "child" else ""
    change_types = list(question["change_types"])
    add = dict(question["add"])
    sill_note = ""
    if any(w.get("sill_height") is None for w in room["windows"]):
        sill_note = " (sill_height null = 0.9 m assumed)"
    task = (f"Task: complete this {ROOM_TYPE_TEXT[room_type]}{child} labelled '{room['label']}' on the plan. The "
            "documents draw some furniture in it (listed below). Add the pieces the room misses where they fit"
            + ("." if question["keep_size"] or not change_types else
               ", and change a drawn piece marked changeable only where a better type, size or look suits the "
               "room and the style.")
            + f" Style brief: {style_text.strip() or 'none'}.")
    room_json = "Room (metres, X right, Y up):\n" + json.dumps(room, ensure_ascii=False)
    drawn = ("Drawn pieces (from the documents; front_deg = the direction the piece faces, 0 = +X, 90 = +Y; anchor = "
             "the point that stays: the centre of a free piece, the middle of the back edge of a piece against a "
             "wall):\n" + json.dumps(question["drawn"], ensure_ascii=False))
    missing_items = dict(question["missing"])
    lines = []
    if question.get("anchor_missing"):
        lines.append(f"- the room has no {' or '.join(question['anchors'])}: add one")
    if missing_items:
        lines.append(f"- expected for this room type and missing: {_counts(missing_items)}")
    if not lines:
        lines.append("- nothing expected is missing")
    lines.append(f"- you may add at most: {_counts(add)}" if add else "- nothing may be added")
    guide = COMPLETION_GUIDE.get(room_type, COMPLETION_GUIDE["other"])
    missing = "What the room misses:\n" + "\n".join(lines) + f"\nA good completion: {guide}"
    size_types = list(dict.fromkeys(change_types + list(add)))
    sizes = ("Types with their size options [width, depth]:\n" + _size_table(tuple(size_types))) if size_types else \
        "Types with their size options: none (nothing may change or be added)."
    if question["keep_size"] or not change_types:
        change_rules = "Rules for changes: no drawn piece may change its type or size in this room (changes: [])."
    else:
        change_rules = (
            "Rules for changes (list a drawn piece only when you change it):\n"
            "- only pieces with kind changeable; fixed pieces (stairs, kitchen runs and appliances, sanitary ware) "
            "never change;\n"
            "- a changed piece keeps its anchor and the direction it faces: against a wall its back edge stays on "
            "the same wall at the same point and the new size grows into the room; a free piece keeps its centre;\n"
            f"- the room's main piece ({', '.join(question['anchors']) or 'none'}) may only become another main "
            "piece type, and no other piece may become one (never a second main piece);\n"
            "- the size is one of the size options of the new type; a size that does not fit is reduced or the "
            "change is undone;\n"
            f"- style: one of {', '.join(question['styles'])}; colour: one of {', '.join(question['colours'])}.")
    rules = ("Rules for added pieces: the drawn pieces (after your changes) are obstacles; keep 0.6 m free in front "
             "of drawn beds, sofas, desks and wardrobes too.\n" + _rules_block(sill_note))
    fields = _completion_fields(change_types, list(add), question["keep_size"])
    end = "Answer only with JSON."
    if pass_no == 1:
        blocks = [task, room_json, drawn, missing, sizes, change_rules, rules, fields, end]
    else:
        blocks = [task, missing, change_rules, rules, sizes, drawn, room_json, fields, end]
    return "\n\n".join(blocks)
