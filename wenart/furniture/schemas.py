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
"""
from __future__ import annotations

from typing import Any, Optional

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
}

# Types only the documents give (docs/milestone7.md §6.5): never proposed by the layout model.
DOCUMENTED_ONLY_TYPES: tuple[str, ...] = ("stair", "side_table", "floor_lamp", "potted_plant")
LAYOUT_TYPES: tuple[str, ...] = tuple(t for t in SIZE_OPTIONS if t not in DOCUMENTED_ONLY_TYPES)

# Room type -> types the model may place there.
ALLOWED_TYPES: dict[str, tuple[str, ...]] = {
    "living": ("sofa", "armchair", "table_coffee", "tv_unit", "bookshelf", "table_dining", "chair"),
    "bedroom": ("bed_double", "bed_single", "nightstand", "wardrobe", "dresser", "desk", "chair", "bookshelf"),
    "kitchen": ("kitchen_counter", "kitchen_island", "fridge", "stove", "sink_kitchen", "table_dining", "chair",
                "washing_machine"),
    "bathroom": ("washbasin", "toilet", "shower", "bathtub", "washing_machine"),
    "wc": ("toilet", "washbasin"),
    "hall": ("dresser", "chair", "bookshelf"),
    "dining": ("table_dining", "chair", "dresser", "bookshelf"),      # Milestone 7 (§6.5)
    "other": ("armchair", "chair", "table_dining", "bookshelf", "desk"),
}
FURNISHABLE_ROOM_TYPES: tuple[str, ...] = tuple(ALLOWED_TYPES)
# Room types the AI never furnishes even when the documents leave them empty (docs/milestone7.md §0:
# a pooja / prayer room is never furnished by AI and gets no decor).
NOT_FURNISHED_ROOM_TYPES: tuple[str, ...] = ("prayer",)

# Room type -> the piece its type calls for (GPU test: a bedroom gets a bed, a living room a sofa).
ANCHOR_TYPES: dict[str, tuple[str, ...]] = {
    "bedroom": ("bed_double", "bed_single"),
    "living": ("sofa",),
    "kitchen": ("kitchen_counter",),
    "bathroom": ("washbasin", "toilet"),
    "wc": ("toilet",),
    "dining": ("table_dining",),
}

# Types whose back normally touches a wall (prompt hint; the check applies to
# whatever the model marks ``against_wall``).
WALL_TYPES: tuple[str, ...] = (
    "bed_single", "bed_double", "sofa", "wardrobe", "kitchen_counter", "tv_unit", "bookshelf", "dresser",
    "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "washing_machine", "desk",
)
# 0.6 m free in front of these (docs/milestone4.md section 3).
CLEARANCE_TYPES: tuple[str, ...] = ("bed_single", "bed_double", "sofa", "desk", "wardrobe")
# Allowed within 0.3 m of a window even when taller than the sill.
UNDER_WINDOW_TYPES: tuple[str, ...] = ("bed_single", "bed_double", "sofa", "table_dining", "table_coffee")

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


def block_sizes() -> dict[str, set[tuple[float, float]]]:
    """type -> drawing block sizes (for the prompt/table consistency test)."""
    out: dict[str, set[tuple[float, float]]] = {}
    for _name, (ftype, w, d) in BLOCKS.items():
        out.setdefault(ftype, set()).add((w, d))
    return out
