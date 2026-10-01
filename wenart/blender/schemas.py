"""JSON schemas for ``scene_manifest.json`` and ``render_manifest.json``.

Kept small on purpose: they pin the fields other stages rely on (object ids
and kinds, pass indices, camera positions, assumed defaults, render timings)
and allow extra keys so the manifests can grow. ``jsonschema`` is imported
lazily: Blender's Python does not have it, the CPU tests do.
"""
from __future__ import annotations

_EVIDENCE = {"type": "object", "required": ["file", "method", "confidence"]}

SCENE_OBJECT = {
    "type": "object",
    "required": ["name", "wenart_id", "kind", "status", "evidence", "material", "textured", "pass_index", "assumed"],
    "properties": {
        "name": {"type": "string"},
        "wenart_id": {"type": "string"},
        "kind": {"enum": ["wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "camera", "light"]},
        "status": {"enum": ["verified", "unverified", "assumed"]},
        "level_id": {"type": ["string", "null"]},
        "element_id": {"type": ["string", "null"]},
        "evidence": {"type": "array", "items": _EVIDENCE},
        "material": {"type": ["string", "null"]},
        "textured": {"type": "boolean"},
        "pass_index": {"type": ["integer", "null"]},
        "assumed": {"type": "object"},
    },
}

SCENE_CAMERA = {
    "type": "object",
    "required": ["name", "room_id", "level_id", "index", "position", "target", "lens_mm", "sensor_mm",
                 "resolution", "visible_openings", "visible_furniture", "warning"],
    "properties": {
        "name": {"type": "string"},
        "room_id": {"type": "string"},
        "level_id": {"type": "string"},
        "index": {"enum": [1, 2, 3]},
        "position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "target": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "lens_mm": {"type": "number"},
        "sensor_mm": {"type": "number"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "visible_openings": {"type": "array", "items": {"type": "string"}},
        "visible_furniture": {"type": "array", "items": {"type": "string"}},
        "warning": {"type": ["string", "null"]},
    },
}

SCENE_MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "WenArt scene manifest",
    "type": "object",
    "required": ["schema_version", "project", "building", "style", "blender_version", "levels", "objects",
                 "cameras", "materials", "pass_index", "assumed", "warnings", "checks", "previews"],
    "properties": {
        "schema_version": {"const": "0.1"},
        "project": {"type": "string"},
        "building": {"type": "string"},
        "style": {"type": ["string", "null"]},
        "blender_version": {"type": "string"},
        "textures_enabled": {"type": "boolean"},
        "levels": {"type": "array", "items": {"type": "object", "required": ["id", "elevation", "ceiling_height"]}},
        "objects": {"type": "array", "items": SCENE_OBJECT},
        "cameras": {"type": "array", "items": SCENE_CAMERA},
        "materials": {"type": "object", "additionalProperties": {
            "type": "object", "required": ["textured", "asset", "reason"],
        }},
        "pass_index": {"type": "object", "additionalProperties": {"type": "integer"}},
        "assumed": {"type": "array", "items": {"type": "object", "required": ["object", "field", "value", "reason"]}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "checks": {"type": "object", "properties": {
            "door_rays": {"type": "array", "items": {"type": "object", "required": ["opening_id", "hit", "hit_kind"]}},
        }},
        "previews": {"type": "object", "additionalProperties": {"type": "string"}},
        "files": {"type": "object"},
    },
}

RENDER_ENTRY = {
    "type": "object",
    "required": ["camera", "png", "exr", "preview", "seconds", "samples", "resolution", "depth", "index_values"],
    "properties": {
        "camera": {"type": "string"},
        "png": {"type": "string"},
        "exr": {"type": "string"},
        "preview": {"type": "string"},
        "depth_png": {"type": ["string", "null"]},
        "index_png": {"type": ["string", "null"]},
        "seconds": {"type": "number"},
        "samples": {"type": "integer"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "depth": {"type": ["object", "null"], "required": ["min", "max", "mean"]},
        "index_values": {"type": "array", "items": {"type": "integer"}},
        "skipped": {"type": "boolean"},
    },
}

RENDER_MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "WenArt render manifest",
    "type": "object",
    "required": ["schema_version", "scene", "device", "device_requested", "blender_version", "samples",
                 "resolution", "denoiser", "pass_index", "renders"],
    "properties": {
        "schema_version": {"const": "0.1"},
        "scene": {"type": "string"},
        "device": {"enum": ["OPTIX", "CUDA", "CPU"]},
        "device_requested": {"type": "string"},
        "blender_version": {"type": "string"},
        "samples": {"type": "integer"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "denoiser": {"type": ["string", "null"]},
        "pass_index": {"type": "object", "additionalProperties": {"type": "integer"}},
        "renders": {"type": "array", "items": RENDER_ENTRY},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
}


def validate_scene_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, SCENE_MANIFEST)


def validate_render_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, RENDER_MANIFEST)
