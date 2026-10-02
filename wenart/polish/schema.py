"""JSON schema of ``polish_manifest.json`` and ``determinism.json`` (docs/milestone5.md §3.6).

What: the shape every reader relies on (the final report, the GPU test
``tests/gpu/test_polish.py``, the gate calibration's presumed-bad list).
``validate_manifest(m)`` returns the list of schema errors (empty = valid);
the runner checks its own output with it before writing the report.
Extra keys are allowed (the runner records a few more, such as ``wall_lab``
and ``gate_seconds``); the keys of the spec are required.
"""
from __future__ import annotations

NUM = {"type": ["number", "null"]}
STR = {"type": ["string", "null"]}

GATE_RESULT = {
    "type": "object",
    "required": ["decision", "reasons", "notes", "metrics", "gate_key"],
    "properties": {
        "decision": {"enum": ["accept", "reject"]},
        "reasons": {"type": "array"},
        "notes": {"type": "array"},
        "metrics": {"type": "object"},
        "gate_key": {"type": "string"},
    },
}

ATTEMPT = {
    "type": "object",
    "required": ["k", "role", "strength", "control", "scale", "size", "mode", "seed", "steps", "sigmas",
                 "seconds", "png", "sha256", "attempt_key", "panes_restored", "gate", "debug_jpg"],
    "properties": {
        "k": {"type": "integer", "minimum": 1},
        "role": {"enum": ["ladder", "grid", "presumed_bad"]},
        "strength": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
        "control": {"enum": ["depth", "canny", "geometry", None]},
        "scale": NUM,
        "size": {"type": "string"},
        "mode": {"enum": ["plain", "anchor"]},
        "seed": {"type": "integer"},
        "steps": {"type": "integer", "minimum": 1},
        "sigmas": {"type": "array", "items": {"type": "number"}},
        "seconds": NUM,
        "png": STR,
        "sha256": STR,
        "attempt_key": {"type": "string", "minLength": 64, "maxLength": 64},
        "panes_restored": {"type": ["integer", "null"], "minimum": 0},
        "gate": {"oneOf": [GATE_RESULT, {"type": "null"}]},
        "debug_jpg": STR,
        "error": STR,
    },
}

VIEW = {
    "type": "object",
    "required": ["camera", "room_id", "source_png", "source_sha256", "prompt", "controls", "attempts", "final",
                 "final_attempt", "reason"],
    "properties": {
        "camera": {"type": "string"},
        "room_id": STR,
        "source_png": {"type": "string"},
        "source_sha256": {"type": "string"},
        "prompt": STR,
        "controls": {"type": "object", "additionalProperties": {"type": "string"}},
        "attempts": {"type": "array", "items": ATTEMPT},
        "final": {"enum": ["polished", "cycles", None]},
        "final_attempt": {"type": ["integer", "null"]},
        "reason": {"enum": [None, "gate", "brief", "room", "error", "deadline"]},
    },
}

MODEL = {"type": "object", "required": ["repo", "revision", "licence"],
         "properties": {"repo": {"type": "string"}, "revision": {"type": "string"}, "licence": {"type": "string"},
                        "files": {"type": "array"}}}

MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema_version", "kind", "project", "incomplete", "models", "config", "thresholds", "device",
                 "torch", "diffusers", "memory_mode", "peak_vram_gib", "load_seconds", "seconds_per_forward",
                 "views", "rooms", "warnings"],
    "properties": {
        "schema_version": {"const": "0.1"},
        "kind": {"enum": ["run", "sweep", "smoke"]},
        "project": {"type": "string"},
        "incomplete": {"type": "boolean"},
        "models": {"type": "object", "required": ["base", "controlnet", "gate"],
                   "properties": {"base": MODEL, "controlnet": MODEL,
                                  "gate": {"type": "object", "additionalProperties": MODEL}}},
        "config": {"type": "object"},
        "thresholds": {"type": ["object", "null"]},
        "device": STR,
        "torch": STR,
        "diffusers": STR,
        "memory_mode": {"enum": ["resident", "offload", None]},
        "peak_vram_gib": NUM,
        "load_seconds": NUM,
        "seconds_per_forward": NUM,
        "views": {"type": "array", "items": VIEW},
        "rooms": {"type": "object", "additionalProperties": {
            "type": "object", "required": ["rule", "rung"],
            "properties": {"rule": {"enum": ["ok", "downgraded"]}, "rung": {"type": ["integer", "null"]}}}},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
}

DETERMINISM = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["camera", "max_abs_diff", "seconds"],
    "properties": {"camera": STR, "max_abs_diff": {"type": ["integer", "null"], "minimum": 0}, "seconds": NUM},
}


def _errors(schema: dict, data) -> list[str]:
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]


def validate_manifest(manifest: dict) -> list[str]:
    """Schema errors of a ``polish_manifest.json`` dict (empty list = valid)."""
    return _errors(MANIFEST, manifest)


def validate_determinism(data: dict) -> list[str]:
    """Schema errors of a ``determinism.json`` dict (empty list = valid)."""
    return _errors(DETERMINISM, data)
