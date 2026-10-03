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
ROOM_GUIDE: dict[str, str] = {
    "living": "one sofa with its back to a wall facing a tv_unit on the opposite wall, a coffee table in "
              "front of the sofa, optionally one armchair and a bookshelf; a dining table only when the "
              "room is larger than 18 m².",
    "bedroom": "one bed (bed_double for a master bedroom, bed_single for a children's room) with the "
               "headboard against a wall and not under the door, a nightstand on each free side of a "
               "double bed, one wardrobe against a wall, optionally a desk with a chair.",
    "kitchen": "a kitchen_counter along the longest free wall, sink_kitchen and stove inside the counter "
               "line (place them as separate pieces that touch the counter ends), a fridge at one end, "
               "a small dining table with chairs only when there is room.",
    "bathroom": "washbasin, toilet and a shower or bathtub, each against a wall, the toilet not directly "
                "opposite the door.",
    "wc": "one toilet against the wall opposite the door and one small washbasin.",
    "hall": "at most one slim dresser (console) or bookshelf against a wall and one chair; keep the "
            "corridor between the doors free.",
    "dining": "one dining table in the middle of the room with chairs on its long sides (each chair's "
              "front towards the table), optionally a dresser (sideboard) or a bookshelf against a wall; "
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
    types = schemas.ALLOWED_TYPES[room_type]
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
