"""Prompts, element labels and the sentinel decoy of the vision check (docs/milestone5.md §5.3, §5.6).

What:

- ``check_items``: the labelled list one call asks about. The view's
  required and optional elements by descending area get ``E1..En``; one
  sentinel decoy is shuffled in at a position fixed by the sha1 of the
  camera name (the same list on every image of that camera, so Cycles and
  polished answers line up). Type-unverified pieces are asked as
  "furniture piece (type unverified)".
- ``place_decoy``: a 0.18 W x 0.25 H window over bare structure (index 0,
  not background, >= 98 % of the window) on a 5 % grid; among the windows
  that qualify the lowest one wins (nearest the floor, where furniture
  stands), then the one nearest the image centre, then the leftmost.
- ``decoy_type``: the first type allowed in the room type
  (``wenart.furniture.schemas.ALLOWED_TYPES``) that is absent from the room
  and from the view, else the first absent fallback type of ``check.yaml``.
- ``check_prompt``: the per-view prompt (statuses, "an empty doorway is NOT
  a door", extras exclude only walls, floor, ceiling and the outside view);
  ``plan_ab=True`` adds the note about Image 2 (the source-plan crop).
- Milestone 10: ``HINTS`` has a sentence for the 14 new furniture types and the 12 new decor types (the test
  ``tests/test_vision_check_prompts.py`` keeps ``HINTS`` equal to the categories). ``exterior_prompt`` is the
  prompt of an exterior view (the building seen from outside; the expected elements are the windows and doors of
  the facades in view) and ``facade_prompt`` the advisory count of one facade crop.
"""
from __future__ import annotations

import hashlib
from typing import Optional

import numpy as np

from wenart.vision_check import schemas as S
from wenart.vision_check.expected import TYPE_UNVERIFIED_TEXT

# What each category looks like in a photo of a furnished room (not on a plan).
HINTS: dict[str, str] = {
    "door": "door leaf in its frame in a wall opening",
    "window": "glazed window with frame and glass",
    "bed_single": "narrow single bed",
    "bed_double": "wide double bed with headboard",
    "sofa": "sofa / couch for two or more people",
    "armchair": "upholstered chair for one person",
    "table_dining": "dining table",
    "table_coffee": "low coffee table",
    "desk": "work desk",
    "chair": "single chair",
    "wardrobe": "tall closed cupboard for clothes",
    "kitchen_counter": "run of kitchen base cabinets with a worktop",
    "kitchen_island": "free-standing kitchen counter",
    "fridge": "refrigerator",
    "stove": "cooker / hob, often built into the counter",
    "sink_kitchen": "kitchen sink, often built into the counter",
    "washbasin": "bathroom washbasin",
    "toilet": "toilet",
    "shower": "shower tray or glass shower enclosure",
    "bathtub": "bathtub",
    "tv_unit": "low long cabinet / sideboard",
    "bookshelf": "open shelf unit",
    "nightstand": "small bedside table",
    "dresser": "chest of drawers",
    "washing_machine": "front-loading washing machine",
    "stair": "staircase with steps",
    "side_table": "small side table",
    "floor_lamp": "standing floor lamp",
    "potted_plant": "large potted plant standing on the floor",
    "cushion": "cushion or pillow",
    "book_set": "row of books",
    "plant": "potted plant",
    "rug": "rug or carpet lying on the floor",
    "wall_art": "framed picture, print or painting hanging on a wall",
    # Milestone 9 decor (docs/milestone9.md §3)
    "vase": "vase standing on a table, a sideboard or a shelf",
    "bowl": "decorative bowl or tray on a table",
    "plant_small": "small potted plant on a table or a shelf",
    "table_lamp": "lamp standing on a table, a desk or a nightstand",
    "mirror": "mirror hanging on a wall",
    "lamp": "floor, table, wall or ceiling lamp",
    "textile": "curtain or rug",
    "other_furniture": "any other piece of furniture",
    "other_object": "any other object",
    # Milestone 10 furniture (docs/milestone10.md §1.1)
    "sofa_corner": "L-shaped corner sofa with a chaise end",
    "chaise": "chaise longue: a long seat with a raised back end",
    "ottoman": "low upholstered footstool or pouf",
    "bench": "long seat without a back, at a bed foot, a table or an entrance",
    "bar_stool": "tall stool at a counter or an island",
    "office_chair": "swivel chair on a stand or wheels at a desk",
    "console_table": "narrow table standing against a wall",
    "crib": "baby cot with bars",
    "bunk_bed": "two beds stacked on top of each other",
    "sideboard": "low long cabinet with doors or drawers for dishes and linen",
    "shoe_cabinet": "narrow cabinet for shoes at an entrance",
    "display_cabinet": "cabinet with glass doors that shows its content",
    "tall_cabinet": "tall narrow cupboard or pantry unit",
    "wall_cabinet": "kitchen cabinet fixed to the wall above the counter",
}
# Milestone 10 decor (docs/milestone10.md §1.1). Only the types the categories hold are added: the categories come
# from the building schema's decor enum (``schemas.DECOR_CATEGORIES``), so a type without a hint cannot reach a prompt.
_DECOR_HINTS_M10: dict[str, str] = {
    "curtain": "curtain hanging beside or in front of a window",
    "blind": "roller or slat blind covering a window",
    "throw": "blanket or throw lying on a sofa, a chair or a bed",
    "books": "stack of books lying on a table, a shelf or the floor",
    "candle": "candle or candle holder on a table or a shelf",
    "basket": "woven basket on the floor or on a shelf",
    "tray": "serving tray on a table, an ottoman or a bed",
    "clock": "clock hanging on a wall or standing on a shelf",
    "sculpture": "decorative sculpture or figure on a table, a shelf or the floor",
    "plant_large": "large potted plant standing on the floor",
    "pendant_light": "lamp hanging from the ceiling on a cord or a chain",
    "ceiling_light": "lamp fixed flat to the ceiling",
}
HINTS.update({k: v for k, v in _DECOR_HINTS_M10.items() if k in S.CATEGORIES})
UNVERIFIED_HINT = "any piece of furniture at that place"

IMAGE_LABEL = "Image 1 (the render to check):"
PLAN_LABEL = "Image 2 (source floor plan of this room, for orientation):"


def camera_hash(camera: str) -> int:
    return int(hashlib.sha1(camera.encode("utf-8")).hexdigest(), 16)


# --------------------------------------------------------------------------
# Decoy
# --------------------------------------------------------------------------

def place_decoy(index, depth_mm, box_frac=(0.18, 0.25), min_bare_frac: float = 0.98,
                step_frac: float = 0.05) -> Optional[list[int]]:
    """Pixel box ``[x0, y0, x1, y1]`` of the decoy window over bare structure, or None.

    Bare = index 0 and a rendered surface (depth > 0). Windows of
    ``box_frac`` of the image on a ``step_frac`` grid; a window qualifies
    when >= ``min_bare_frac`` of its pixels are bare. The lowest qualifying
    window wins, then the one nearest the horizontal centre, then the leftmost.
    """
    idx = np.asarray(index)
    depth = np.asarray(depth_mm)
    H, W = idx.shape
    bw, bh = max(1, int(round(box_frac[0] * W))), max(1, int(round(box_frac[1] * H)))
    sx, sy = max(1, int(round(step_frac * W))), max(1, int(round(step_frac * H)))
    if bw > W or bh > H:
        return None
    bare = ((idx == 0) & (depth > 0)).astype(np.int64)
    integral = np.zeros((H + 1, W + 1), dtype=np.int64)
    integral[1:, 1:] = bare.cumsum(axis=0).cumsum(axis=1)
    xs = np.arange(0, W - bw + 1, sx)
    ys = np.arange(0, H - bh + 1, sy)
    X, Y = np.meshgrid(xs, ys)
    sums = integral[Y + bh, X + bw] - integral[Y, X + bw] - integral[Y + bh, X] + integral[Y, X]
    ok = sums >= min_bare_frac * bw * bh
    if not ok.any():
        return None
    cands = [(int(y), int(x)) for y, x in zip(Y[ok].tolist(), X[ok].tolist())]
    y0, x0 = min(cands, key=lambda c: (-c[0], abs(c[1] + bw / 2.0 - W / 2.0), c[1]))
    return [x0, y0, x0 + bw, y0 + bh]


def decoy_type(room_type: Optional[str], absent_from: set, fallback_types) -> Optional[str]:
    """First allowed type of the room type not in ``absent_from``, else the first absent fallback type."""
    from wenart.furniture.schemas import ALLOWED_TYPES

    for t in list(ALLOWED_TYPES.get(room_type or "", ())) + list(fallback_types):
        if t not in absent_from:
            return t
    return None


# --------------------------------------------------------------------------
# Items (labels)
# --------------------------------------------------------------------------

def check_items(expected: dict, decoy: Optional[dict] = None, swap: Optional[dict] = None) -> list[dict]:
    """The labelled items of one check call.

    ``expected``: an ``expected_view`` result; ``decoy``: ``{"type",
    "box_px", "box_1000"}`` or None; ``swap``: ``{"id", "type"}`` replaces
    the type asked for that element (type-swap control). Each item:
    ``{"label", "wenart_id" (None for the decoy), "decoy", "kind", "type",
    "category", "type_unverified", "role", "source", "box_1000",
    "touches_border", "swapped_from"}``.
    """
    elements = [e for e in expected.get("elements") or [] if e.get("role") in ("required", "optional")]
    elements.sort(key=lambda e: (-int(e["pixels"]), int(e["index"])))
    items = []
    for e in elements:
        etype = e["type"]
        unverified = bool(e.get("type_unverified"))
        swapped_from = None
        if swap and swap.get("id") == e["wenart_id"]:
            swapped_from, etype, unverified = etype, swap["type"], False
        items.append({"wenart_id": e["wenart_id"], "decoy": False, "kind": e["kind"], "type": etype,
                      "category": S.element_category(e["kind"], etype, unverified),
                      "type_unverified": unverified, "role": e["role"], "source": e.get("source"),
                      "box_1000": list(e["box_1000"]), "touches_border": bool(e.get("touches_border")),
                      "swapped_from": swapped_from})
    if decoy is not None:
        pos = camera_hash(expected.get("camera") or "") % (len(items) + 1)
        items.insert(pos, {"wenart_id": None, "decoy": True, "kind": "furniture", "type": decoy["type"],
                           "category": decoy["type"], "type_unverified": False, "role": "decoy", "source": None,
                           "box_1000": list(decoy["box_1000"]), "touches_border": False, "swapped_from": None})
    for i, item in enumerate(items, 1):
        item["label"] = f"E{i}"
    return items


def element_line(item: dict) -> str:
    """One prompt line (§5.3).

    ``- E3: tv_unit (low long cabinet / sideboard); expected inside box [83, 674, 362, 933]``, plus
    ``, cut by the image edge`` when the element touches the border.
    """
    b = item["box_1000"]
    if item.get("type_unverified"):
        what = f"{TYPE_UNVERIFIED_TEXT} ({UNVERIFIED_HINT})"
    else:
        what = f"{item['type']} ({HINTS.get(item['type'], item['type'])})"
    edge = ", cut by the image edge" if item.get("touches_border") else ""
    return f"- {item['label']}: {what}; expected inside box [{b[0]}, {b[1]}, {b[2]}, {b[3]}]{edge}"


def check_prompt(items: list[dict], room_label: Optional[str], room_type: Optional[str], size=None,
                 plan_ab: bool = False, view_kind: str = "interior") -> str:
    """The per-view element-check prompt (§5.3). Boxes are on the 0..1000 grid, so the pixel ``size``
    (kept for callers) is not stated: the client may send a downscaled image.

    ``view_kind`` ``exterior`` (Milestone 10): the view is the building seen from outside; the expected
    elements are the windows and doors of the facades in view (``exterior_prompt``)."""
    if view_kind == "exterior":
        return exterior_prompt(items, plan_ab)
    room = room_label or "?"
    if room_type:
        room += f" ({room_type})"
    lines = [element_line(it) for it in items] or ["- (none)"]
    parts = [
        f"Task: image 1 is one view of the room '{room}'. Check every expected element listed below.",
        "Expected elements (boxes are [x0, y0, x1, y1] on a 0..1000 grid of the image width and height, origin "
        "top-left):\n" + "\n".join(lines),
        "For each label answer:\n"
        "- status: present = an element of that type is clearly visible at about that place (seen_as = the listed "
        "type); different = another kind of object is there instead (seen_as = what you see there); absent = "
        "nothing of that kind is there (seen_as = nothing); unsure = you cannot tell (too dark, too small, hidden).\n"
        "- seen_as: one of the categories below, or nothing.\n"
        "- confidence: 0..1.\n"
        "A door is a door leaf in its frame: an empty doorway without a door leaf is NOT a door (answer absent). "
        "A 'furniture piece (type unverified)' is present when any piece of furniture stands there.",
        "extras: every door, window, piece of furniture, lamp, curtain, rug or other object you see that is NOT in "
        "the list above, with its category and box (0..1000). Do not list walls, floor, ceiling or the view outside "
        f"a window. Empty list when there is none. At most {S.MAX_EXTRAS}.",
        "door_count, window_count: how many doors and how many windows are visible in image 1, fully or partly.",
        "Categories: " + ", ".join(S.CATEGORIES) + ".",
    ]
    if plan_ab:
        parts.insert(1, "Image 2 is the source floor plan of this room (north up) with the camera and its view "
                        "cone drawn, for orientation only. Judge every element from image 1 only.")
    parts.append("Answer only with JSON that follows the schema.")
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# Exterior views (Milestone 10, docs/milestone10.md §3.3 item 4)
# --------------------------------------------------------------------------

FACADE_IMAGE_LABEL = "Image 1 (a crop of one facade of the building, seen from outside):"


def exterior_prompt(items: list[dict], plan_ab: bool = False) -> str:
    """The element-check prompt of an exterior view: the building seen from outside, the expected elements are
    its windows and doors in view. Same answer shape as ``check_prompt``; extras exclude the parts of the
    building and the site (walls, roof, ground, trees, plot wall, sky) and anything seen through a window."""
    lines = [element_line(it) for it in items] or ["- (none)"]
    parts = [
        "Task: image 1 is one view of a building seen from outside. Check every expected element listed below "
        "(windows and doors in the facades).",
        "Expected elements (boxes are [x0, y0, x1, y1] on a 0..1000 grid of the image width and height, origin "
        "top-left):\n" + "\n".join(lines),
        "For each label answer:\n"
        "- status: present = an element of that type is clearly visible at about that place (seen_as = the listed "
        "type); different = another kind of object is there instead (seen_as = what you see there); absent = "
        "nothing of that kind is there (seen_as = nothing); unsure = you cannot tell (too small, hidden, in shadow).\n"
        "- seen_as: one of the categories below, or nothing.\n"
        "- confidence: 0..1.\n"
        "A window is glass in a frame in a wall; a door is a door leaf in a wall opening. A plain wall without glass "
        "or a leaf is NOT a window or a door (answer absent).",
        "extras: every door, window, balcony railing, lamp or other object you see that is NOT in the list above, "
        "with its category and box (0..1000). Do not list walls, roof, chimney, ground, paving, grass, trees, the "
        "plot wall, the sky or anything you see through a window. Empty list when there is none. "
        f"At most {S.MAX_EXTRAS}.",
        "door_count, window_count: how many doors and how many windows are visible in image 1, fully or partly.",
        "Categories: " + ", ".join(S.CATEGORIES) + ".",
    ]
    if plan_ab:
        parts.insert(1, "Image 2 is the source floor plan with the camera and its view cone drawn, for orientation "
                        "only. Judge every element from image 1 only.")
    parts.append("Answer only with JSON that follows the schema.")
    return "\n\n".join(parts)


def facade_prompt(side: Optional[str]) -> str:
    """The advisory count of one facade crop: windows and doors seen, no expected number named (a number in the
    question would bias the answer)."""
    what = f"the {side} facade" if side and side not in ("all", "front", "back", "left", "right") \
        else f"the {side} side" if side else "one facade"
    return "\n\n".join([
        f"Task: image 1 is a crop of {what} of a building, seen from outside. Count the windows and the doors "
        "you can see in this crop, fully or partly.",
        "A window is glass in a frame in the wall; a door is a door leaf in a wall opening. A plain wall without "
        "glass or a leaf is not a window or a door. Do not count roof windows, garage doors of other buildings, "
        "or anything you see through a window.",
        "Answer window_count, door_count and confidence (0..1). Answer only with JSON that follows the schema."])
