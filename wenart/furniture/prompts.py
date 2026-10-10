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
room's ``schemas.layout_types``.

Milestone 12 (docs/milestone12.md §4.5; owner: track G): the layout and the
completion no longer ask for coordinates. ``choice_prompt`` (with
``CHOICE_SYSTEM_PROMPT`` and the strict ``choice_schema``) asks the vision
model to pick one of the group solver's candidates from their top-down images
(``layout.candidate_png``), their groups, options, scores and score terms; the
answer is a candidate number and a reason. The Milestone 10 completion
question is gone (``layout_prompt`` stays for ``LayoutClient.propose``).
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
    "stair": "stair room or stair core (Turkish: MERDİVEN, YANGIN MERDİVENİ = fire stair); never furnished",
    "shaft": "shaft or lift (Turkish: ŞAFT, HAVA BACASI, ASANSÖR); never furnished",
    "other": "room of unspecified use",
    "balcony": "balcony or terrace (Turkish: BALKON, TERAS)",
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
    "stair": "nothing: a stair room holds only its stair (this text is never sent).",
    "shaft": "nothing: a shaft is never furnished (this text is never sent).",
    "other": "a small table with chairs or a desk and a bookshelf; keep it sparse.",
    "balcony": "a small table with two chairs; the railing side stays free.",
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
# Milestone 12: choosing among the group solver's candidates (docs/milestone12.md §4.5)
# --------------------------------------------------------------------------

CHOICE_SYSTEM_PROMPT = (
    "You are an interior planner. You look at top-down plans of one room, each showing one candidate furniture "
    "layout that code has already checked (inside the room, no overlap, doors, windows and walkways free), and you "
    "pick the candidate a person would like best to live with. You never move pieces or give coordinates. Answer "
    "only with JSON that follows the given schema."
)

CHOICE_LEGEND = (
    "How to read the images (north up, metres): the black outline is the room; orange shapes are door strips and "
    "door swings, cyan strips are windows; grey boxes are pieces drawn in the documents (they stay); coloured boxes "
    "are the candidate's new pieces, one colour per functional group, each with its type; the red edge of a piece "
    "is its front."
)


def choice_schema(n: int) -> dict[str, Any]:
    """The answer of a candidate choice: one of ``1..n`` and a short reason (strict, xgrammar-safe keywords)."""
    return {"type": "object", "additionalProperties": False, "required": ["candidate", "reason"],
            "properties": {"candidate": {"enum": list(range(1, n + 1))},
                           "reason": {"type": "string", "maxLength": 300}}}


def choice_prompt(room: dict, candidates: list[dict], style_text: str, purpose: str = "furnish") -> str:
    """The question for one room: the room, the style, and per candidate its groups and options, its score and the
    terms that make it (``solver`` candidates, best first). ``purpose`` "complete": the room has drawn furniture."""
    room_type = room.get("room_type") or "other"
    if room_type not in ROOM_TYPE_TEXT:
        room_type = "other"
    task = ("Task: choose the best furniture layout for this " + ROOM_TYPE_TEXT[room_type]
            + f" labelled '{room.get('label', room['id'])}' ({float(room.get('area_computed') or 0.0):.1f} m²). "
            + ("The documents draw some furniture in it; the candidates only add what the room misses. "
               if purpose == "complete" else "")
            + f"Style brief: {style_text.strip() or 'none'}.")
    lines = []
    for c in candidates:
        groups = ", ".join(f"{g['group']} ({c.get('options', {}).get(g['group_id'], '-')})" for g in c["groups"])
        pieces = ", ".join(sorted(p["type"] for p in c["pieces"]))
        terms = ", ".join(f"{k} {v:.2f}" for k, v in sorted(c.get("terms", {}).items()))
        missing = "; ".join(f"{x['group']} not placed" for x in c.get("not_placed", []))
        lines.append(f"Candidate {c['rank']}: score {c['score']:.1f}; groups: {groups or '-'}; new pieces: "
                     f"{pieces or '-'}" + (f"; {missing}" if missing else "") + f"; terms (0-1, higher is better): "
                     f"{terms}")
    rules = ("Prefer the candidate where the main group works best (a sofa that faces its TV with the coffee table "
             "between, a bed with free sides and its headboard on a wall, chairs around the table, a kitchen run in "
             "the order fridge - sink - hob), the walkways from the doors stay short and the room looks balanced. "
             "The score is the code's own ranking; you may disagree when the image shows a better room.")
    fields = ("Fields of the answer: candidate (the number of the candidate you choose) and reason (one short "
              "sentence why).")
    return "\n\n".join([task, CHOICE_LEGEND, "Candidates:\n" + "\n".join(lines), rules, fields,
                        "Answer only with JSON."])
