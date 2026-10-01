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


def validation_errors(task: str, data: Any) -> list[str]:
    """All schema violations of ``data`` for ``task`` as readable strings (empty = valid)."""
    validator = jsonschema.Draft202012Validator(SCHEMAS[task])
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
    schema = dict(SCHEMAS[task])
    schema.pop("$schema", None)
    return schema
