"""Answer schema of the layout model plus the furniture tables it is prompted with.

One source for three consumers: the prompt (``prompts.py``) lists exactly the
types and sizes below, the placer (``placer.py``) uses the same heights and
size options for its window rule and its shrink repair, and the tests check
that prompt, schema and tables agree.

Answer shape (strict, ``additionalProperties: false``, at most 12 pieces):

    {"pieces": [{"type": "bed_double", "center": [x, y], "rotation_deg": 0,
                 "size": [w, d], "against_wall": true, "reason": "..."}]}

Coordinates are building metres (the room polygon is given in the prompt in
the same frame). ``size = [width (X), depth (Y)]`` in the piece's own frame,
front = -Y at rotation 0 (the block frame of docs/milestone2.md), so a piece
with ``rotation_deg = 0`` faces down (-Y) and its back edge is on +Y.

Size options: three per type, the middle one is the drawing block size of
``wenart/synthetic/blocks.py`` (checked by ``tests/test_layout.py``). The
placer's shrink repair steps down this list.

Milestone 7 (docs/milestone7.md §6.5): ``stair``, ``side_table``,
``floor_lamp`` and ``potted_plant`` are documented-only types
(``DOCUMENTED_ONLY_TYPES``): they have size options and heights for the fit
and the placer (a drawn stair is an obstacle like any drawn piece) but are
not in ``LAYOUT_TYPES``, so the layout model can never add one. ``dining``
rooms get their own allowed types (anchor: the dining table); ``prayer``
rooms are never furnished by AI (``NOT_FURNISHED_ROOM_TYPES``).

Milestone 10 (docs/milestone10.md §2, §4.5): 14 new types with size options
and heights (typical catalogue sizes, assumed); ``FIXED_TYPES`` (stairs,
kitchen runs and appliances, sanitary ware: user decision 6 of 8 Oct 2026)
never change in a completed room; the per-room-type completion tables
(``EXPECTED_TYPES``, ``EXTRA_TYPES``, nightstands per bed, chairs per table
length, bar stools per island length) and ``completion_plan``. The new types
are added at the end of the ``ALLOWED_TYPES`` rows, so the first type of each
row (the vision check's decoy) stays the same.

What the empty-room model (Milestone 4) may propose (``LAYOUT_TYPES``, per
room ``layout_types``): every new type except ``sofa_corner`` (the M4 answer
has no chaise side: a corner sofa is only reached by changing a drawn sofa),
``bar_stool`` (only at a drawn kitchen island) and ``wall_cabinet`` (placed
by the §4.4 rule only); ``bunk_bed`` and ``crib`` only in a child's room
(``rooms[].room_subtype: child``), where ``bed_double`` is not proposed.

The corner sofa (``sofa_corner``, ``shape: L``, docs/milestone10.md §1.6b):
the footprint is the bounding box ``[width, depth]`` (front = -Y at rotation
0) and ``chaise_depth`` the depth of the long seat (= the footprint depth);
the main seat runs along the back over the whole width, ``seat_depth`` deep;
the long seat (chaise) is ``chaise_width`` wide on ``chaise_side`` seen from
the front (a viewer facing the sofa: ``right`` = local +X); both default to
0.9 m (``L_SEAT_DEPTH_M``, ``L_CHAISE_WIDTH_M``). ``l_parts`` gives the two
rectangles; the placer uses them in every check.

Milestone 11 (docs/milestone11.md §4.3, §6): ``ORIENTATION_RULES`` per type (back to a wall / free in a group, what
the front faces, the group partners; used by ``plausibility``, ``infer`` and ``groups``), ``GROUP_TYPES`` (the
functional groups), the armchair's front clearance (``CLEARANCE_DEPTH_M``, U13) and ``completion_plan`` taking an
``unverified`` flag per piece (an unverified table asks for no chairs, U10).
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable, Optional

import jsonschema

from wenart.synthetic.blocks import BLOCKS

MAX_PIECES = 12

# type -> [small, default, large] as (width, depth) in metres.
SIZE_OPTIONS: dict[str, list[tuple[float, float]]] = {
    "bed_single": [(0.9, 1.9), (0.9, 2.0), (1.2, 2.0)],
    "bed_double": [(1.4, 2.0), (1.6, 2.0), (1.8, 2.0)],
    "sofa": [(1.6, 0.9), (2.2, 0.9), (2.6, 0.95)],
    "armchair": [(0.8, 0.8), (0.9, 0.9), (1.0, 1.0)],
    "table_dining": [(1.2, 0.8), (1.6, 0.9), (2.0, 1.0)],
    "table_coffee": [(0.8, 0.5), (1.0, 0.6), (1.2, 0.7)],
    "desk": [(1.2, 0.6), (1.4, 0.7), (1.6, 0.8)],
    "chair": [(0.4, 0.4), (0.45, 0.45), (0.5, 0.5)],
    "wardrobe": [(1.2, 0.6), (1.8, 0.6), (2.4, 0.6)],
    "kitchen_counter": [(1.8, 0.6), (2.4, 0.6), (3.0, 0.6)],
    "kitchen_island": [(1.2, 0.8), (1.6, 0.9), (2.0, 1.0)],
    "fridge": [(0.6, 0.65), (0.7, 0.7), (0.9, 0.75)],
    "stove": [(0.5, 0.6), (0.6, 0.6), (0.9, 0.6)],
    "sink_kitchen": [(0.6, 0.5), (0.8, 0.5), (1.0, 0.6)],
    "washbasin": [(0.5, 0.4), (0.6, 0.45), (0.8, 0.5)],
    "toilet": [(0.36, 0.65), (0.4, 0.7), (0.45, 0.75)],
    "shower": [(0.8, 0.8), (0.9, 0.9), (1.2, 0.9)],
    "bathtub": [(1.5, 0.7), (1.7, 0.75), (1.8, 0.8)],
    "tv_unit": [(1.2, 0.4), (1.6, 0.45), (2.0, 0.45)],
    "bookshelf": [(0.8, 0.3), (1.0, 0.35), (1.2, 0.4)],
    "nightstand": [(0.4, 0.4), (0.5, 0.4), (0.6, 0.45)],
    "dresser": [(1.0, 0.45), (1.2, 0.5), (1.4, 0.5)],
    "washing_machine": [(0.55, 0.55), (0.6, 0.6), (0.7, 0.7)],
    # Documented-only types (Milestone 7): never proposed by the layout model; the sizes are typical
    # pieces within the recognition size table (wenart/recognition/size_table.yaml), for the placer only.
    "stair": [(0.9, 2.7), (1.0, 3.0), (2.0, 3.0)],              # one flight; a dog-leg pair of flights
    "side_table": [(0.4, 0.4), (0.45, 0.45), (0.6, 0.6)],
    "floor_lamp": [(0.3, 0.3), (0.4, 0.4), (0.5, 0.5)],
    "potted_plant": [(0.3, 0.3), (0.4, 0.4), (0.6, 0.6)],
    # Milestone 10 (docs/milestone10.md §1.1, §4.5): typical catalogue sizes (assumed; no drawing block yet).
    "sofa_corner": [(2.2, 1.5), (2.6, 1.6), (3.0, 1.7)],        # the L's bounding box; depth = chaise_depth
    "chaise": [(0.65, 1.6), (0.75, 1.7), (0.85, 1.8)],          # the long side runs along the depth
    "ottoman": [(0.5, 0.5), (0.6, 0.6), (0.8, 0.8)],
    "bench": [(1.0, 0.4), (1.2, 0.4), (1.4, 0.45)],
    "bar_stool": [(0.38, 0.38), (0.42, 0.42), (0.45, 0.45)],
    "office_chair": [(0.55, 0.55), (0.6, 0.6), (0.65, 0.65)],
    "console_table": [(0.9, 0.3), (1.2, 0.35), (1.4, 0.4)],
    "crib": [(1.26, 0.66), (1.36, 0.7), (1.46, 0.76)],          # 60x120 .. 70x140 mattresses, a long side as front
    "bunk_bed": [(0.95, 1.95), (1.0, 2.05), (1.1, 2.1)],
    "sideboard": [(1.4, 0.42), (1.6, 0.45), (1.8, 0.48)],
    "shoe_cabinet": [(0.6, 0.3), (0.8, 0.32), (1.0, 0.35)],
    "display_cabinet": [(0.8, 0.38), (1.0, 0.4), (1.2, 0.42)],
    "tall_cabinet": [(0.4, 0.58), (0.6, 0.6), (0.8, 0.6)],      # pantry / tall kitchen unit
    "wall_cabinet": [(0.6, 0.35), (0.9, 0.35), (1.2, 0.35)],    # the §4.4 rule takes the width from the counter run
}
DEFAULT_SIZE_INDEX = 1

# Typical height of each type in metres (window rule: nothing taller than the
# sill within 0.3 m of a window; also the ``height`` of added pieces).
HEIGHTS: dict[str, float] = {
    "bed_single": 0.5, "bed_double": 0.5, "sofa": 0.85, "armchair": 0.85,
    "table_dining": 0.75, "table_coffee": 0.45, "desk": 0.75, "chair": 0.9,
    "wardrobe": 2.1, "kitchen_counter": 0.9, "kitchen_island": 0.9, "fridge": 1.8,
    "stove": 0.9, "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.8,
    "shower": 2.0, "bathtub": 0.6, "tv_unit": 0.5, "bookshelf": 1.8,
    "nightstand": 0.5, "dresser": 0.8, "washing_machine": 0.85,
    # Milestone 7 documented-only types: a stair rises to the floor above (the default ceiling
    # height of wenart/defaults.yaml); the potted plant is the decor plant's height (decor.PLANT_HEIGHT_M).
    "stair": 2.7, "side_table": 0.55, "floor_lamp": 1.6, "potted_plant": 1.0,
    # Milestone 10 (assumed typical heights; the wall cabinet's own height, hung at WALL_CABINET_Z).
    "sofa_corner": 0.85, "chaise": 0.8, "ottoman": 0.45, "bench": 0.45, "bar_stool": 0.75, "office_chair": 1.0,
    "console_table": 0.8, "crib": 0.9, "bunk_bed": 1.65, "sideboard": 0.8, "shoe_cabinet": 1.0,
    "display_cabinet": 1.9, "tall_cabinet": 2.1, "wall_cabinet": 0.7,
}

# Types only the documents give (docs/milestone7.md §6.5): never proposed by the layout model.
DOCUMENTED_ONLY_TYPES: tuple[str, ...] = ("stair", "side_table", "floor_lamp", "potted_plant")
# Milestone 10: types no model ever proposes as a new piece.
RULE_ONLY_TYPES: tuple[str, ...] = ("wall_cabinet",)        # the §4.4 rule along a drawn counter run
CHANGE_ONLY_TYPES: tuple[str, ...] = ("sofa_corner",)       # a drawn sofa changed by AI (the placer picks the side)
ISLAND_ONLY_TYPES: tuple[str, ...] = ("bar_stool",)         # added only at a drawn kitchen island
CHILD_ONLY_TYPES: tuple[str, ...] = ("bunk_bed", "crib")    # only in a child's room (rooms[].room_subtype: child)
# The empty-room model's answer enum (the Milestone 4 schema below).
LAYOUT_TYPES: tuple[str, ...] = tuple(t for t in SIZE_OPTIONS if t not in DOCUMENTED_ONLY_TYPES + RULE_ONLY_TYPES
                                      + CHANGE_ONLY_TYPES + ISLAND_ONLY_TYPES)

# Room type -> types a room of that type may hold. Milestone 10 (§2.3): the new types at the end of each row, the
# ones least like a type before them first (the vision check's decoy is the first type of the row absent from a
# view: a corner sofa next to a sofa would be a poor decoy); ``layout_types`` (empty rooms) and
# ``completion_plan`` (rooms with drawn furniture) narrow a row per use; the recognition veto reads the whole row.
ALLOWED_TYPES: dict[str, tuple[str, ...]] = {
    "living": ("sofa", "armchair", "table_coffee", "tv_unit", "bookshelf", "table_dining", "chair",
               "console_table", "sideboard", "display_cabinet", "ottoman", "chaise", "sofa_corner"),
    "bedroom": ("bed_double", "bed_single", "nightstand", "wardrobe", "dresser", "desk", "chair", "bookshelf",
                "armchair", "bench", "ottoman", "office_chair", "bunk_bed", "crib"),
    "kitchen": ("kitchen_counter", "kitchen_island", "fridge", "stove", "sink_kitchen", "table_dining", "chair",
                "washing_machine", "bar_stool", "tall_cabinet", "wall_cabinet"),
    "bathroom": ("washbasin", "toilet", "shower", "bathtub", "washing_machine"),
    "wc": ("toilet", "washbasin"),
    "hall": ("dresser", "chair", "bookshelf", "console_table", "shoe_cabinet", "bench"),
    "dining": ("table_dining", "chair", "dresser", "bookshelf",      # Milestone 7 (§6.5)
               "display_cabinet", "sideboard", "bench"),
    "other": ("armchair", "chair", "table_dining", "bookshelf", "desk"),
}
FURNISHABLE_ROOM_TYPES: tuple[str, ...] = tuple(ALLOWED_TYPES)
# Room types the AI never furnishes even when the documents leave them empty (docs/milestone7.md §0:
# a pooja / prayer room is never furnished by AI and gets no decor).
NOT_FURNISHED_ROOM_TYPES: tuple[str, ...] = ("prayer",)

# Room type -> the piece its type calls for (GPU test: a bedroom gets a bed, a living room a sofa).
ANCHOR_TYPES: dict[str, tuple[str, ...]] = {
    "bedroom": ("bed_double", "bed_single", "bunk_bed", "crib"),
    "living": ("sofa", "sofa_corner"),
    "kitchen": ("kitchen_counter",),
    "bathroom": ("washbasin", "toilet"),
    "wc": ("toilet",),
    "dining": ("table_dining",),
}
CHILD_ANCHOR_TYPES: tuple[str, ...] = ("bed_single", "bunk_bed", "crib")   # §2.3: a child's room

# Types whose back normally touches a wall (prompt hint; the check applies to
# whatever the model marks ``against_wall``).
WALL_TYPES: tuple[str, ...] = (
    "bed_single", "bed_double", "sofa", "wardrobe", "kitchen_counter", "tv_unit", "bookshelf", "dresser",
    "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "washing_machine", "desk",
    # Milestone 10
    "sofa_corner", "bunk_bed", "console_table", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet",
    "wall_cabinet",
)
# 0.6 m free in front of these (docs/milestone4.md section 3; Milestone 10: the corner sofa (in front of its
# main seat), bunk beds, cribs and tall cabinets; Milestone 11 (docs/milestone11.md §1.2 U13): armchairs, with a
# shorter zone, ``CLEARANCE_DEPTH_M``).
CLEARANCE_TYPES: tuple[str, ...] = ("bed_single", "bed_double", "sofa", "desk", "wardrobe",
                                    "sofa_corner", "bunk_bed", "crib", "tall_cabinet", "armchair")
# Milestone 11 (U13: an added armchair stood 1 cm behind a sofa back, facing it): the depth of the free zone in
# front of a seat that is not the 0.6 m default (a knee zone; assumed typical value).
CLEARANCE_DEPTH_M: dict[str, float] = {"armchair": 0.45}
# Milestone 10: pieces of these types may stand in the front clearance of the key type (the desk's own chair; a
# bench or ottoman at the foot of a bed, §2.3 "bench (bed foot)", code review #21); Milestone 11: a coffee table,
# pouf or side table in front of an armchair.
CLEARANCE_EXEMPT: dict[str, tuple[str, ...]] = {"desk": ("office_chair",),
                                                "bed_double": ("bench", "ottoman"),
                                                "bed_single": ("bench", "ottoman"),
                                                "armchair": ("table_coffee", "ottoman", "side_table")}
# Allowed within 0.3 m of a window even when taller than the sill.
UNDER_WINDOW_TYPES: tuple[str, ...] = ("bed_single", "bed_double", "sofa", "table_dining", "table_coffee",
                                       "sofa_corner", "chaise", "bench")

# --------------------------------------------------------------------------
# Milestone 10: completion of rooms with drawn furniture (docs/milestone10.md §2)
# --------------------------------------------------------------------------

# Fixed equipment (user, 8 Oct 2026): only the look may change; a locked obstacle for the placer.
FIXED_TYPES: tuple[str, ...] = ("stair", "kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge",
                                "washing_machine", "toilet", "washbasin", "shower", "bathtub")
# Drawn pieces of these types keep their type and size (no room type lists a type to change them into).
UNCHANGEABLE_TYPES: tuple[str, ...] = FIXED_TYPES + DOCUMENTED_ONLY_TYPES + RULE_ONLY_TYPES
# Hung on the wall above the floor (``furniture.mount_bottom_m``): not a floor obstacle for the placer.
MOUNTED_TYPES: tuple[str, ...] = ("wall_cabinet",)
WALL_CABINET_Z: tuple[float, float] = (1.45, 2.15)          # §4.4: bottom and top above the floor, metres
# Corner sofa geometry (see the module docstring): the defaults of ``seat_depth`` and ``chaise_width`` (assumed).
L_SEAT_DEPTH_M = 0.9
L_CHAISE_WIDTH_M = 0.9
# The looks the completion writes into ``furniture.design`` (docs/milestone10.md §1.6b row 15, §4.4).
CABINET_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island", "wall_cabinet", "tall_cabinet")
WORKTOP_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
FRONT_STYLES: tuple[str, ...] = ("flat", "shaker", "slatted", "glass")
HANDLES: tuple[str, ...] = ("brushed_steel", "black", "brass")
WORKTOPS: tuple[str, ...] = ("stone", "wood", "terrazzo", "steel")
MATERIAL_TAGS: tuple[str, ...] = ("glass", "wood", "metal", "fabric", "rattan", "marble")
VANITY_MIN_DEPTH_M = 0.45                                   # a washbasin this deep gets the vanity look (§4.4)
# Bathrooms and WCs: sanitary ware hangs on the plumbing, nothing is added (§2.3).
NOTHING_ADDED_ROOM_TYPES: tuple[str, ...] = ("bathroom", "wc")
# Room type -> expected type -> count (missing ones are asked for, §2.3).
EXPECTED_TYPES: dict[str, dict[str, int]] = {
    "bedroom": {"nightstand": 2, "wardrobe": 1},
    "living": {"table_coffee": 1, "tv_unit": 1},
    "dining": {"chair": 4},
}
# Room type -> type -> the most the AI may add up to ("may also add", §2.3; "other": the M4 types, counts assumed).
EXTRA_TYPES: dict[str, dict[str, int]] = {
    "bedroom": {"dresser": 1, "desk": 1, "office_chair": 1, "bench": 1, "armchair": 1, "bookshelf": 1, "ottoman": 1},
    "living": {"armchair": 2, "chaise": 1, "ottoman": 1, "console_table": 1, "sideboard": 1, "bookshelf": 1,
               "display_cabinet": 1},
    "dining": {"sideboard": 1, "display_cabinet": 1, "bench": 1},
    "kitchen": {"bar_stool": 4, "table_dining": 1, "chair": 4, "tall_cabinet": 1},
    "hall": {"console_table": 1, "shoe_cabinet": 1, "bench": 1},
    "other": {"armchair": 2, "chair": 4, "table_dining": 1, "bookshelf": 1, "desk": 1},
    "bathroom": {},
    "wc": {},
}
# Nightstands by the bed (§2.3: 2 with a double bed, 1 with a single bed; bunk bed and crib assumed).
NIGHTSTANDS_PER_BED: dict[str, int] = {"bed_double": 2, "bed_single": 1, "bunk_bed": 1, "crib": 0}
# (length below, count): chairs at a dining table (§2.3: 4 at 1.2 m, 6 at 1.6 m, 8 at 2.0 m) and bar stools at a
# kitchen island (§2.3: 2-4; about one per 0.5 m, assumed).
CHAIRS_BY_TABLE_LENGTH: tuple[tuple[float, int], ...] = ((1.4, 4), (1.8, 6), (math.inf, 8))
BAR_STOOLS_BY_ISLAND_LENGTH: tuple[tuple[float, int], ...] = ((1.4, 2), (1.8, 3), (math.inf, 4))
# A new piece of the key type needs one of these in the room (and stands within COMPANION_REACH_M of it).
COMPANIONS: dict[str, tuple[str, ...]] = {"office_chair": ("desk",), "bar_stool": ("kitchen_island",),
                                          "chair": ("table_dining",)}
COMPANION_REACH_M = 0.6
# Upholstered types: the AI's colour is the fabric colour (``design.fabric_colour``), else ``design.colour``.
FABRIC_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "bed_single",
                                 "bed_double")

# --------------------------------------------------------------------------
# Milestone 11: orientation rules per type (docs/milestone11.md §4.3 F3, F4, F8, §6)
# --------------------------------------------------------------------------

# type -> {"back": "wall" | "wall_or_group" | "free" | "skip", "back_severity", "front_to": [types], "reach_m",
# "partners": [types], "partner_m"}:
# - back "wall": the back edge stands on a wall (F3: within BACK_WALL_M, parallel within BACK_PARALLEL_DEG);
#   "wall_or_group": on a wall, or free when its front faces one of ``front_to`` (a sofa facing the TV unit or the
#   coffee table in an open room); "free": a piece of a group (F8: one of ``partners`` within ``partner_m``, or a side
#   on a wall); "skip": no orientation checks (stairs, wall-hung cabinets);
# - front_to: what the front should face (F4) when one of these stands in the room within ``reach_m`` (edge to edge);
#   empty = only "the front does not face a wall closer than FRONT_WALL_MIN_M";
# - frontless types (FRONTLESS_TYPES) have no front: F4 is skipped.
# Sizes and distances are assumed typical values (planning handbooks), not from a standard.
BACK_WALL_M = 0.05
BACK_PARALLEL_DEG = 5.0
FRONT_WALL_MIN_M = 0.3
FACING_DEG = 45.0                  # the front faces a target when the target lies within 45 degrees of it
FRONTLESS_TYPES: tuple[str, ...] = ("table_dining", "table_coffee", "side_table", "floor_lamp", "potted_plant",
                                    "ottoman", "kitchen_island", "stair", "unknown")
_SEATS = ("sofa", "sofa_corner", "armchair", "chaise")
_BEDS = ("bed_double", "bed_single", "bunk_bed", "crib")


def _rule(back: str, front_to=(), reach_m: float = 0.0, partners=(), partner_m: float = 0.0,
          back_severity: str = "major") -> dict[str, Any]:
    return {"back": back, "back_severity": back_severity, "front_to": list(front_to), "reach_m": reach_m,
            "partners": list(partners), "partner_m": partner_m}


ORIENTATION_RULES: dict[str, dict[str, Any]] = {
    "bed_double": _rule("wall", back_severity="critical"),
    "bed_single": _rule("wall", back_severity="critical"),
    "bunk_bed": _rule("wall", back_severity="critical"),
    "crib": _rule("wall"),
    "sofa": _rule("wall_or_group", ("tv_unit", "table_coffee"), 4.5),
    "sofa_corner": _rule("wall_or_group", ("tv_unit", "table_coffee"), 4.5),
    "armchair": _rule("free", ("table_coffee", "sofa", "sofa_corner", "tv_unit"), 3.5,
                      _SEATS + ("table_coffee", "tv_unit", "ottoman", "side_table", "floor_lamp"), 2.0),
    "chaise": _rule("free", ("table_coffee", "tv_unit"), 3.5, _SEATS + ("table_coffee", "tv_unit"), 2.0),
    "chair": _rule("free", ("table_dining", "desk", "kitchen_island", "table_coffee"), 1.0,
                   ("table_dining", "desk", "kitchen_island", "table_coffee", "dresser"), 0.8),
    "office_chair": _rule("free", ("desk",), 1.0, ("desk",), 1.0),
    "bar_stool": _rule("free", ("kitchen_island", "kitchen_counter"), 0.8, ("kitchen_island", "kitchen_counter"),
                       0.8),
    "table_dining": _rule("free", partners=("chair", "bench", "bar_stool"), partner_m=1.0),
    "table_coffee": _rule("free", partners=_SEATS, partner_m=1.5),
    "kitchen_island": _rule("free", partners=("kitchen_counter", "sink_kitchen", "stove", "fridge", "bar_stool",
                                              "tall_cabinet"), partner_m=3.0),
    "ottoman": _rule("free", partners=_SEATS + _BEDS + ("table_coffee", "dresser"), partner_m=1.5),
    "side_table": _rule("free", partners=_SEATS + _BEDS + ("desk",), partner_m=0.8),
    "floor_lamp": _rule("free", partners=_SEATS + _BEDS + ("desk", "table_coffee"), partner_m=1.2),
    "potted_plant": _rule("free", partners=_SEATS + _BEDS + ("tv_unit", "sideboard", "console_table"),
                          partner_m=1.5),
    "bench": _rule("free", partners=_BEDS + ("table_dining", "shoe_cabinet"), partner_m=0.8),
    "desk": _rule("wall"),
    "wardrobe": _rule("wall"),
    "tv_unit": _rule("wall", ("sofa", "sofa_corner", "armchair"), 6.0),
    "bookshelf": _rule("wall"),
    "dresser": _rule("wall"),
    "sideboard": _rule("wall"),
    "console_table": _rule("wall"),
    "shoe_cabinet": _rule("wall"),
    "display_cabinet": _rule("wall"),
    "nightstand": _rule("wall", partners=_BEDS, partner_m=0.3, back_severity="minor"),
    "kitchen_counter": _rule("wall"),
    "sink_kitchen": _rule("wall"),
    "stove": _rule("wall"),
    "fridge": _rule("wall"),
    "tall_cabinet": _rule("wall"),
    "washing_machine": _rule("wall"),
    "washbasin": _rule("wall"),
    "toilet": _rule("wall"),
    "bathtub": _rule("wall"),
    "shower": _rule("wall", back_severity="minor"),
    "wall_cabinet": _rule("skip"),
    "stair": _rule("skip"),
}

# Functional groups (docs/milestone11.md §6, wenart/furniture/groups.py): the anchor types of a group and its members.
GROUP_TYPES: dict[str, dict[str, Any]] = {
    "dining_set": {"anchor": ("table_dining",), "members": ("chair",)},
    "bed_set": {"anchor": ("bed_double", "bed_single"), "members": ("nightstand",)},
    "living_set": {"anchor": ("sofa",), "members": ("table_coffee", "tv_unit")},
    "desk_set": {"anchor": ("desk",), "members": ("office_chair",)},
    "kitchen_run": {"anchor": ("kitchen_counter",), "members": ("sink_kitchen", "stove", "fridge")},
}


def orientation_rule(ftype: str) -> dict[str, Any]:
    """The ``ORIENTATION_RULES`` row of a type (``skip`` for a type without one)."""
    return ORIENTATION_RULES.get(ftype, _rule("skip"))

LAYOUT: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Layout",
    "type": "object",
    "additionalProperties": False,
    "required": ["pieces"],
    "properties": {
        "pieces": {
            "type": "array",
            "maxItems": MAX_PIECES,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "center", "rotation_deg", "size", "against_wall", "reason"],
                "properties": {
                    "type": {"enum": list(LAYOUT_TYPES)},
                    "center": {
                        "type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2,
                        "description": "[x, y] of the footprint centre in metres (building frame)",
                    },
                    "rotation_deg": {
                        "type": "number", "minimum": 0, "maximum": 360,
                        "description": "counter-clockwise; 0 = width along X, front towards -Y",
                    },
                    "size": {
                        "type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                        "minItems": 2, "maxItems": 2,
                        "description": "[width, depth] in metres, one of the size options of the type",
                    },
                    "against_wall": {"type": "boolean", "description": "the back edge touches a wall"},
                    "reason": {"type": "string", "maxLength": 200},
                },
            },
        }
    },
}


def validation_errors(data: Any) -> list[str]:
    """All violations of the layout schema as readable strings (empty = valid)."""
    validator = jsonschema.Draft202012Validator(LAYOUT)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    out = []
    for err in errors:
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{path}: {err.message}")
    return out


def is_valid(data: Any) -> bool:
    return not validation_errors(data)


def grammar_schema() -> dict[str, Any]:
    """The schema as sent to vLLM (without ``$schema``)."""
    schema = dict(LAYOUT)
    schema.pop("$schema", None)
    return schema


def default_size(ftype: str) -> tuple[float, float]:
    return SIZE_OPTIONS[ftype][DEFAULT_SIZE_INDEX]


def size_index(ftype: str, size, tol: float = 0.011) -> Optional[int]:
    """Index of ``size`` in the type's options (within ``tol`` per side), or None."""
    for i, (w, d) in enumerate(SIZE_OPTIONS.get(ftype, [])):
        if abs(float(size[0]) - w) <= tol and abs(float(size[1]) - d) <= tol:
            return i
    return None


def smaller_size(ftype: str, size) -> Optional[tuple[float, float]]:
    """The next smaller option below ``size`` (None when ``size`` is the smallest)."""
    options = SIZE_OPTIONS.get(ftype, [])
    if not options:
        return None
    idx = size_index(ftype, size)
    if idx is None:
        # Not an option: the largest option that is smaller than the given size.
        area = float(size[0]) * float(size[1])
        smaller = [opt for opt in options if opt[0] * opt[1] < area - 1e-6]
        return smaller[-1] if smaller else None
    return options[idx - 1] if idx > 0 else None


def nearest_size(ftype: str, size) -> tuple[float, float]:
    """The size option of ``ftype`` nearest to ``size`` (sum of the side differences; the first on ties)."""
    options = SIZE_OPTIONS[ftype]
    return min(options, key=lambda o: abs(o[0] - float(size[0])) + abs(o[1] - float(size[1])))


def block_sizes() -> dict[str, set[tuple[float, float]]]:
    """type -> drawing block sizes (for the prompt/table consistency test)."""
    out: dict[str, set[tuple[float, float]]] = {}
    for _name, (ftype, w, d) in BLOCKS.items():
        out.setdefault(ftype, set()).add((w, d))
    return out


# --------------------------------------------------------------------------
# Milestone 10: per-room tables
# --------------------------------------------------------------------------

def allowed_types(room_type: Optional[str], subtype: Optional[str] = None) -> tuple[str, ...]:
    """The ``ALLOWED_TYPES`` row of a room narrowed by its subtype: cribs and bunk beds only in a child's room,
    no double bed there."""
    row = ALLOWED_TYPES.get(room_type or "", ())
    if room_type != "bedroom":
        return row
    if subtype == "child":
        return tuple(t for t in row if t != "bed_double")
    return tuple(t for t in row if t not in CHILD_ONLY_TYPES)


def layout_types(room_type: Optional[str], subtype: Optional[str] = None) -> tuple[str, ...]:
    """What the empty-room model may propose in a room of this type (see the module docstring)."""
    return tuple(t for t in allowed_types(room_type, subtype) if t in LAYOUT_TYPES)


def anchor_types(room_type: Optional[str], subtype: Optional[str] = None) -> tuple[str, ...]:
    """The room's anchor types (one piece only, §2.3): a child's room takes a single bed, a bunk bed or a crib."""
    if room_type == "bedroom":
        return CHILD_ANCHOR_TYPES if subtype == "child" else ("bed_double", "bed_single")
    return ANCHOR_TYPES.get(room_type or "", ())


def change_types(room_type: Optional[str], subtype: Optional[str] = None) -> tuple[str, ...]:
    """The types a changeable drawn piece may become (§2.2: within the room type's types; never fixed equipment,
    a documented-only or a rule-only type)."""
    return tuple(t for t in allowed_types(room_type, subtype) if t not in UNCHANGEABLE_TYPES)


def count_by_length(length: float, table: tuple[tuple[float, int], ...]) -> int:
    """The count of ``table`` for a piece ``length`` metres long (the first row whose limit is above it)."""
    for limit, count in table:
        if length < limit - 1e-9:
            return count
    return table[-1][1]


def completion_plan(room_type: Optional[str], subtype: Optional[str],
                    present: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    """What a room with drawn furniture holds, misses and may get (§2.3), from its pieces ``(type, size)`` (or
    ``(type, size, unverified)``, Milestone 11: an unverified dining table asks for no chairs)
    after the agreed changes.

    Returns ``anchors`` (the anchor types the room may get), ``anchor_roles`` (every type that is the room's main
    piece when drawn: all bed types of a bedroom), ``has_anchor``, ``maxima`` (type -> the most the room may
    hold; an anchor type 1 while no anchor is present, the group counting as one), ``expected`` (type -> count),
    ``missing`` (expected type -> how many are missing), ``anchor_missing``, ``addable`` (type -> how many the
    AI may add: ``maxima`` minus what is present; never a fixed, rule-only, change-only or documented-only
    type; nothing in bathrooms and WCs) and ``counts`` (type -> present).
    """
    rtype = room_type or "other"
    present = list(present)
    items = [(p[0], tuple(float(v) for v in p[1])) for p in present]
    # Milestone 11 (U10: one block "masa" = table + 10 chairs read as one table, then 7 more chairs were asked for):
    # an unverified table (a third value True: its footprint may hold its drawn chairs) asks for no chairs.
    sure_tables = [max(float(v) for v in p[1]) for p in present
                   if p[0] == "table_dining" and not (len(p) > 2 and p[2])]
    unsure_table = any(p[0] == "table_dining" for p in present) and not sure_tables
    counts = Counter(t for t, _ in items)
    anchors = anchor_types(rtype, subtype)
    # Any bed type counts as the room's bed (code review #18: a double bed drawn in a child's room, a bunk bed in
    # another bedroom); the subtype only narrows what may be added.
    roles = tuple(dict.fromkeys(ANCHOR_TYPES.get(rtype, ()) + anchors))
    has_anchor = any(counts[a] for a in roles)
    expected = dict(EXPECTED_TYPES.get(rtype, {}))
    extra = dict(EXTRA_TYPES.get(rtype, {}))
    beds = [t for t, _ in items if t in NIGHTSTANDS_PER_BED]
    if "nightstand" in expected and beds:
        expected["nightstand"] = max(NIGHTSTANDS_PER_BED[b] for b in beds)
    tables = sure_tables
    if tables and rtype != "other":
        # Chairs follow a drawn dining table wherever it stands (a dining corner of a living room or kitchen).
        expected["chair"] = count_by_length(max(tables), CHAIRS_BY_TABLE_LENGTH)
        extra.pop("chair", None)
    elif unsure_table:
        expected.pop("chair", None)
        extra.pop("chair", None)
    if rtype == "kitchen":
        islands = [max(size) for t, size in items if t == "kitchen_island"]
        if islands:
            extra["bar_stool"] = count_by_length(max(islands), BAR_STOOLS_BY_ISLAND_LENGTH)
        else:
            extra.pop("bar_stool", None)
    blocked = set(FIXED_TYPES) | set(RULE_ONLY_TYPES) | set(CHANGE_ONLY_TYPES) | set(DOCUMENTED_ONLY_TYPES)
    maxima: dict[str, int] = {}
    for a in anchors:
        maxima[a] = 0 if has_anchor else 1
    for t, n in list(expected.items()) + list(extra.items()):
        maxima[t] = max(maxima.get(t, 0), n)
    missing = {t: n - counts[t] for t, n in expected.items() if n > counts[t]}
    addable_anchors = [a for a in anchors if a not in blocked]
    anchor_missing = not has_anchor and bool(addable_anchors)
    addable = {t: n - counts[t] for t, n in maxima.items() if n > counts[t] and t not in blocked}
    if rtype in NOTHING_ADDED_ROOM_TYPES or rtype not in ALLOWED_TYPES:
        missing, addable, anchor_missing = {}, {}, False
    return {"anchors": anchors, "anchor_roles": roles, "has_anchor": has_anchor, "maxima": maxima,
            "expected": expected,
            "missing": missing, "anchor_missing": anchor_missing, "addable": addable, "counts": dict(counts)}


def l_parts(size, chaise_side: Optional[str], chaise_depth: Optional[float], seat_depth: Optional[float] = None,
            chaise_width: Optional[float] = None) -> list[tuple[float, float, float, float]]:
    """The corner sofa's two rectangles in its local frame as ``(x0, x1, y0, y1)``: the main seat along the back
    (+Y) over the whole width, ``seat_depth`` deep, then the long seat (chaise) ``chaise_width`` wide on
    ``chaise_side`` (``right`` = +X) over ``chaise_depth`` from the back (defaults: ``L_SEAT_DEPTH_M``,
    ``L_CHAISE_WIDTH_M``, the footprint depth)."""
    w, d = float(size[0]), float(size[1])
    depth = min(float(chaise_depth), d) if chaise_depth else d
    seat = min(float(seat_depth) if seat_depth else L_SEAT_DEPTH_M, depth)
    cw = min(float(chaise_width) if chaise_width else L_CHAISE_WIDTH_M, w / 2.0)
    main = (-w / 2.0, w / 2.0, d / 2.0 - seat, d / 2.0)
    if chaise_side == "left":
        chaise = (-w / 2.0, -w / 2.0 + cw, d / 2.0 - depth, d / 2.0)
    else:
        chaise = (w / 2.0 - cw, w / 2.0, d / 2.0 - depth, d / 2.0)
    return [main, chaise]


def l_seat_front(size, chaise_side: Optional[str], chaise_depth: Optional[float], seat_depth: Optional[float] = None,
                 chaise_width: Optional[float] = None) -> tuple[float, float, float]:
    """``(x0, x1, y_front)`` of the corner sofa's main seat in front of which the clearance zone lies (the part
    of the seat not covered by the chaise)."""
    main, chaise = l_parts(size, chaise_side, chaise_depth, seat_depth, chaise_width)
    if chaise_side == "left":
        return chaise[1], main[1], main[2]
    return main[0], chaise[0], main[2]
