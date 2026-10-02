"""JSON schemas for ``scene_manifest.json`` and ``render_manifest.json``.

Kept small on purpose: they pin the fields other stages rely on (object ids
and kinds, pass indices, camera positions, assumed defaults, render timings)
and allow extra keys so the manifests can grow. ``jsonschema`` is imported
lazily: Blender's Python does not have it, the CPU tests do.

Milestone 5 (docs/milestone5.md §2.5, §2.7) makes these fields required:
render entries carry ``index_stats``, ``files.depth_mm`` / ``files.normal``,
``render_key``, ``exposure``, ``hidden`` and ``plugged`` (an entry without
them is a Milestone 4 render, stale for ``wenart.views``); scene manifests
carry ``preview_maps`` and ``build_fingerprint``, door and window entries
``room_ids`` and furniture, proxy and decor entries ``box3d``.
"""
from __future__ import annotations

_EVIDENCE = {"type": "object", "required": ["file", "method", "confidence"]}
_VEC3 = {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
BOX3D = {
    "type": "object",
    "required": ["center", "size", "rotation_deg"],
    "properties": {"center": _VEC3, "size": _VEC3, "rotation_deg": {"type": "number"}},
}
PIXEL_BOX = {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4}
INDEX_STATS = {
    "type": "object",
    "propertyNames": {"pattern": "^[1-9][0-9]*$"},
    "additionalProperties": {"type": "object", "required": ["pixels", "box"],
                             "properties": {"pixels": {"type": "integer", "minimum": 1}, "box": PIXEL_BOX}},
}
EXPOSURE = {
    "type": "object",
    "required": ["mode", "ev", "ev_raw", "at_limit", "target", "incident_p50", "whitepoint", "wb_temperature",
                 "wb_tint", "residual", "window_clip_frac", "meter_seconds", "source"],
    "properties": {
        "mode": {"enum": ["auto", "off", "fixed", "from"]},
        "ev": {"type": "number"},
        "ev_raw": {"type": ["number", "null"]},
        "at_limit": {"type": "boolean"},
        "target": {"type": ["number", "null"]},
        "incident_p50": {"type": ["number", "null"]},
        "whitepoint": {"oneOf": [{"type": "null"}, {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                    "minItems": 3, "maxItems": 3}]},
        "wb_mode": {"enum": ["auto", "off", "fixed", "from"]},
        "wb_temperature": {"type": ["number", "null"]},
        "wb_tint": {"type": ["number", "null"]},
        "residual": {"type": ["number", "null"]},
        "window_clip_frac": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "meter_seconds": {"type": "number", "minimum": 0},
        "source": {"type": ["string", "null"]},
    },
}

SCENE_OBJECT = {
    "type": "object",
    "required": ["name", "wenart_id", "kind", "status", "evidence", "material", "textured", "pass_index", "assumed"],
    "properties": {
        "name": {"type": "string"},
        "wenart_id": {"type": "string"},
        "kind": {"enum": ["wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "furniture",
                          "decor", "camera", "light"]},
        # Milestone 4 per-piece fields (furniture and decor entries only).
        "method": {"type": ["string", "null"]},
        "fit_scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "bbox_m": {"type": ["array", "null"], "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "asset": {"type": ["object", "null"]},
        "decor": {"type": "array", "items": {"type": "object", "required": ["name", "type", "method"]}},
        "status": {"enum": ["verified", "unverified", "assumed"]},
        "level_id": {"type": ["string", "null"]},
        "element_id": {"type": ["string", "null"]},
        "evidence": {"type": "array", "items": _EVIDENCE},
        "material": {"type": ["string", "null"]},
        "textured": {"type": "boolean"},
        "pass_index": {"type": ["integer", "null"]},
        "assumed": {"type": "object"},
        # Milestone 5 (§2.7): rooms carrying an opening, world box of a piece as built.
        "room_ids": {"type": "array", "items": {"type": "string"}},
        "box3d": BOX3D,
    },
    "allOf": [
        {"if": {"properties": {"kind": {"enum": ["door", "window"]}}, "required": ["kind"]},
         "then": {"required": ["room_ids"]}},
        {"if": {"properties": {"kind": {"enum": ["furniture", "furniture_proxy", "decor"]}}, "required": ["kind"]},
         "then": {"required": ["box3d"]}},
    ],
}

PREVIEW_MAP = {
    "type": "object",
    "required": ["png", "bbox_m", "m_per_px", "resolution"],
    "properties": {
        "png": {"type": "string"},
        "bbox_m": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
        "m_per_px": {"type": "number", "exclusiveMinimum": 0},
        "resolution": {"type": "array", "items": {"type": "integer", "minimum": 1}, "minItems": 2, "maxItems": 2},
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
        # Milestone 6 (docs/milestone6.md §1.3); optional so M5 manifests stay valid.
        "shift_x": {"type": "number"},
        "shift_y": {"type": "number"},
        "policy": {"enum": ["search", "m5"]},
        "score": {"type": ["object", "null"]},
    },
}

SCENE_MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "WenArt scene manifest",
    "type": "object",
    "required": ["schema_version", "project", "building", "style", "blender_version", "levels", "objects",
                 "cameras", "materials", "pass_index", "assumed", "warnings", "checks", "previews", "preview_maps",
                 "build_fingerprint"],
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
        "preview_maps": {"type": "object", "additionalProperties": PREVIEW_MAP},
        "build_fingerprint": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "wenart_mood": {"type": "string"},
        "files": {"type": "object"},
        "furniture": {"type": "object", "required": ["pieces", "by_method", "fallbacks", "proxies", "decor"],
                      "properties": {
                          "pieces": {"type": "integer"},
                          "by_method": {"type": "object", "additionalProperties": {"type": "integer"}},
                          "fallbacks": {"type": "array", "items": {
                              "type": "object", "required": ["id", "type", "reason"]}},
                          "proxies": {"type": "integer"},
                          "decor": {"type": "integer"},
                      }},
    },
}

RENDER_ENTRY = {
    "type": "object",
    "required": ["camera", "png", "exr", "preview", "seconds", "samples", "resolution", "depth", "index_values",
                 "index_stats", "files", "render_key", "exposure", "hidden", "plugged"],
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
        # Milestone 5 (§2.4-2.6).
        "index_stats": INDEX_STATS,
        "files": {"type": "object", "required": ["index", "depth_mm", "normal"],
                  "properties": {"index": {"type": "string"}, "depth_mm": {"type": "string"},
                                 "normal": {"type": "string"}, "depth": {"type": ["string", "null"]}}},
        "render_key": {"type": "string", "pattern": "^[0-9a-f]{16}$"},
        "exposure": EXPOSURE,
        "hidden": {"type": "array", "items": {"type": "string"}},
        "plugged": {"type": "array", "items": {"type": "string"}},
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
        "scene": {"type": ["string", "null"]},  # relative to the manifest folder since M5
        "device": {"enum": ["OPTIX", "CUDA", "CPU"]},
        "device_requested": {"type": "string"},
        "blender_version": {"type": "string"},
        "samples": {"type": "integer"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "denoiser": {"type": ["string", "null"]},
        "pass_index": {"type": "object", "additionalProperties": {"type": "integer"}},
        "renders": {"type": "array", "items": RENDER_ENTRY},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "hidden": {"type": "array", "items": {"type": "string"}},
        "plugged": {"type": "array", "items": {"type": "string"}},
        "look_from": {"type": ["string", "null"]},
        "render_code_version": {"type": "string"},
    },
}


def validate_scene_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, SCENE_MANIFEST)


def validate_render_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, RENDER_MANIFEST)
