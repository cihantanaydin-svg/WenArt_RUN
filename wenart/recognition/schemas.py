"""JSON schemas for the answers of the vision-language models.

Why schemas: every AI call in this project is temperature 0 with strict
JSON-schema validation (CLAUDE.md, no-hallucination rules). The same schema
is sent to vLLM as the structured-output grammar and used here to validate the
answer that comes back, so a malformed answer can never reach the building JSON.

Shape of the answers:

- ``page_class``: one object ``{class, level_label_raw, scale_text, confidence}``.
- ``text_items``, ``symbols``, ``room_labels``: one object ``{"items": [...]}``.
  The list sits under ``items`` instead of being the root value so that the
  root is an object with ``additionalProperties: false`` (strict, as the spec
  asks) and grammar backends see a single fixed root key.

Boxes are ``[x0, y0, x1, y1]`` in the image the model saw, normalised to
0..1000 of the image width and height (the native grounding convention of both
Qwen3-VL and GLM-4.xV; ``vlm_client.norm1000_to_pixels`` converts back).

Enum values come from the building schema (page classes, furniture types) so
the two can never drift apart.

Milestone 7 (docs/milestone7.md §3.3, §3.4) adds two per-item tasks in
``M7_SCHEMAS`` (kept out of ``SCHEMAS``/``TASKS``, which are the four whole-page
tasks of the Milestone 2 bake-off):

- ``symbol_type``: ``{type, front, confidence, reason}`` for one drawn object
  shown in two crops; ``type`` is every furniture type of the building schema
  plus ``not_furniture``; ``front`` is a side of the second crop or ``none``.
- ``room_label``: ``{label, size_text, area_text, box}`` for one room face of a
  raster page; every field may be null; ``box`` is 0..1000 of the crop.
"""
from __future__ import annotations

from typing import Any

import jsonschema

from wenart.building import load_schema

_BUILDING = load_schema()
PAGE_CLASSES: tuple[str, ...] = tuple(
    _BUILDING["$defs"]["document"]["properties"]["pages"]["items"]["properties"]["class"]["enum"]
)
FURNITURE_TYPES: tuple[str, ...] = tuple(_BUILDING["$defs"]["furniture"]["properties"]["type"]["enum"])
OPENING_SYMBOL_TYPES: tuple[str, ...] = ("door", "window")
SYMBOL_TYPES: tuple[str, ...] = FURNITURE_TYPES + OPENING_SYMBOL_TYPES

BOX_MAX = 1000  # boxes are normalised to 0..1000 (see module docstring)

BOX: dict[str, Any] = {
    "type": "array",
    "description": "[x0, y0, x1, y1], normalised to 0..1000 of the image width/height, origin top-left",
    "items": {"type": "number", "minimum": 0, "maximum": BOX_MAX},
    "minItems": 4,
    "maxItems": 4,
}

CONFIDENCE: dict[str, Any] = {"type": "number", "minimum": 0, "maximum": 1}

PAGE_CLASS: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "PageClass",
    "type": "object",
    "additionalProperties": False,
    "required": ["class", "level_label_raw", "scale_text", "confidence"],
    "properties": {
        "class": {"enum": list(PAGE_CLASSES)},
        "level_label_raw": {
            "type": ["string", "null"],
            "description": "The level title exactly as printed, e.g. 'ZEMİN KAT PLANI', or null",
        },
        "scale_text": {
            "type": ["string", "null"],
            "description": "The scale text exactly as printed, e.g. 'ÖLÇEK 1/100', or null",
        },
        "confidence": CONFIDENCE,
    },
}

TEXT_ITEMS: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TextItems",
    "type": "object",
    "additionalProperties": False,
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "box"],
                "properties": {
                    "text": {"type": "string", "description": "The text exactly as printed"},
                    "box": BOX,
                },
            },
        }
    },
}

SYMBOLS: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Symbols",
    "type": "object",
    "additionalProperties": False,
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "box", "rotation_deg", "confidence"],
                "properties": {
                    "type": {"enum": list(SYMBOL_TYPES)},
                    "box": BOX,
                    "rotation_deg": {
                        "type": ["number", "null"],
                        "minimum": 0,
                        "maximum": 360,
                        "description": "Rotation of the symbol in degrees counter-clockwise, or null",
                    },
                    "confidence": CONFIDENCE,
                },
            },
        }
    },
}

ROOM_LABELS: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "RoomLabels",
    "type": "object",
    "additionalProperties": False,
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["label_raw", "box"],
                "properties": {
                    "label_raw": {"type": "string", "description": "Room label exactly as printed, e.g. 'YATAK ODASI'"},
                    "box": BOX,
                },
            },
        }
    },
}

# Task name -> schema. The task names are also the prompt names in prompts.py.
SCHEMAS: dict[str, dict[str, Any]] = {
    "page_class": PAGE_CLASS,
    "text_items": TEXT_ITEMS,
    "symbols": SYMBOLS,
    "room_labels": ROOM_LABELS,
}
TASKS: tuple[str, ...] = tuple(SCHEMAS)

# --------------------------------------------------------------------------
# Milestone 7: one drawn object, one room face (docs/milestone7.md §3)
# --------------------------------------------------------------------------

NOT_FURNITURE = "not_furniture"
# The full list is offered to both passes (no room hint, §3.3): every furniture type of the building schema
# (``unknown`` included: "furniture, type unclear" is an honest answer) plus "this is not a piece".
SYMBOL_TYPE_CHOICES: tuple[str, ...] = FURNITURE_TYPES + (NOT_FURNITURE,)
FRONT_CHOICES: tuple[str, ...] = ("top", "right", "bottom", "left", "none")
REASON_MAX_CHARS = 160

SYMBOL_TYPE: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SymbolType",
    "type": "object",
    "additionalProperties": False,
    "required": ["type", "front", "confidence", "reason"],
    "properties": {
        "type": {"enum": list(SYMBOL_TYPE_CHOICES)},
        "front": {
            "enum": list(FRONT_CHOICES),
            "description": "Side of the second image the object faces, or none",
        },
        "confidence": CONFIDENCE,
        "reason": {"type": "string", "maxLength": REASON_MAX_CHARS},
    },
}

NULLABLE_TEXT: dict[str, Any] = {"type": ["string", "null"]}

ROOM_LABEL: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "RoomLabel",
    "type": "object",
    "additionalProperties": False,
    "required": ["label", "size_text", "area_text", "box"],
    "properties": {
        "label": dict(NULLABLE_TEXT, description="Room name exactly as printed, or null"),
        "size_text": dict(NULLABLE_TEXT, description="Room size exactly as printed, e.g. 11' x 10', or null"),
        "area_text": dict(NULLABLE_TEXT, description="Area exactly as printed, e.g. 24,50 m², or null"),
        # A nullable type list with constraints, the form the M2 bake-off ran on vLLM (``rotation_deg``).
        "box": dict(BOX, type=["array", "null"], description=BOX["description"] + "; null when there is no name"),
    },
}

# Per-item tasks of the recognition requests (wenart.recognition.answers): task -> schema.
M7_SCHEMAS: dict[str, dict[str, Any]] = {
    "symbol_type": SYMBOL_TYPE,
    "room_label": ROOM_LABEL,
}
M7_TASKS: tuple[str, ...] = tuple(M7_SCHEMAS)


def schema_of(task: str) -> dict[str, Any]:
    """The schema of a Milestone 2 task (``SCHEMAS``) or a Milestone 7 task (``M7_SCHEMAS``)."""
    if task in SCHEMAS:
        return SCHEMAS[task]
    return M7_SCHEMAS[task]


def validation_errors(task: str, data: Any) -> list[str]:
    """All schema violations of ``data`` for ``task`` as readable strings (empty = valid)."""
    validator = jsonschema.Draft202012Validator(schema_of(task))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    out = []
    for err in errors:
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{path}: {err.message}")
    return out


def is_valid(task: str, data: Any) -> bool:
    """True when ``data`` satisfies the schema of ``task``."""
    return not validation_errors(task, data)


def grammar_schema(task: str) -> dict[str, Any]:
    """The schema as sent to vLLM: without ``$schema`` (not needed by the grammar backend)."""
    schema = dict(schema_of(task))
    schema.pop("$schema", None)
    return schema
