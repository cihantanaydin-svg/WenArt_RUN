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

Milestone 6 (docs/milestone6.md §1.3, §5), all optional so older manifests
stay valid: camera ``shift_x`` / ``shift_y`` / ``policy`` / ``score``, the
scene manifest's ``camera_policy``, ``assumed`` entries with ``parent`` and
``kind`` (design details and lights: every entry that has one has both and a
reason), render entries' ``window_pull`` and ``alt_preview``, the exposure's
``ev_offset`` and the render manifest's ``incomplete`` / ``not_rendered`` /
``deadline`` and control flags.

Milestone 7 (docs/milestone7.md §6.4), optional as well: opening entries'
``virtual`` and ``line`` (a separator without geometry), furniture entries'
``stair`` record, the furniture summary's ``not_built`` (``build: false``
pieces) and ``stairs``, the manifest's ``site`` (what the scene leaves
out: plot walls, exterior areas, site decor, ``built: false``) and
``rooms_without_view`` (§6.2: rooms the camera search gives no view, with the
reason).

Milestone 8 (docs/milestone8.md §5), optional: camera ``lens_rule`` (why the
searched camera has its 18 / 16 mm or brief lens; ``lens_mm`` stays required),
the scene manifest's ``lens_mm`` (the brief's lens, null = automatic) and
render entries' ``lens_mm`` / ``sensor_mm`` (the lens as rendered).

Milestone 10 (docs/milestone10.md §1.6b row 11; track E owns this module), optional as well: object kinds of
the whole building (``WHOLE_BUILDING_KINDS``); camera ``kind`` (interior / exterior: an exterior camera has
``room_id`` and ``level_id`` null), ``index`` any integer >= 1, ``variant``, ``view`` (corner / aerial /
elevation / null), ``sides`` (``$defs/side`` names), ``region_id`` and ``dropped_reason`` (null for a built
camera; the dropped exterior views are listed in ``cameras_dropped``, never in ``cameras``); the manifest's
``variant``, ``variants``, ``whole_building``, ``exterior_looks`` (``exterior.resolve_looks``), ``brief`` (the
brief values used) and a built ``site`` (``built: true`` with the terrain, its changes and the light wells).
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
        "ev_offset": {"type": "number"},
    },
}
_SHARE = {"type": ["number", "null"], "minimum": 0, "maximum": 1}
WINDOW_PULL = {
    "oneOf": [
        {"type": "null"},
        {"type": "object", "required": ["ev", "clip_before", "clip_after", "pane_px"],
         "properties": {"ev": {"type": "number", "maximum": 0}, "k": {"enum": [0, 1, 2, 3, 4]},
                        "pane_ev": {"type": "number"}, "clip_before": _SHARE, "clip_after": _SHARE,
                        "pane_px": {"type": "integer", "minimum": 1}, "pane_median": {"type": "number"},
                        "wall_median": {"type": ["number", "null"]}, "rule": {"type": "string"}}},
    ],
}
# Milestone 10 (docs/milestone10.md §1.6b row 11): object kinds of the whole building; views.KIND_MAP never maps
# them to furniture.
WHOLE_BUILDING_KINDS = ("slab", "roof", "facade", "terrain", "site_wall", "site_area", "site_decor", "light_well",
                        "railing",
                        # Milestone 11 (docs/milestone11.md §1.1 E10, E11): the inferred site and the facade details
                        "site_steps", "site_boundary", "facade_detail", "splashback")
# wenart/schema/building.schema.json $defs/side.
SIDES = ("all", "north", "east", "south", "west", "front", "back", "left", "right")
CAMERA_VIEWS = ("corner", "aerial", "elevation",
                # Milestone 11 (docs/milestone11.md §1.1 E14, §17.3): the frontal view of the entrance facade and
                # the agent's fixed exterior cameras
                "frontal", "agent")
ASSUMED_ENTRY = {
    "type": "object",
    "required": ["object", "field", "value", "reason"],
    "properties": {"parent": {"type": "string"}, "kind": {"type": "string"}, "reason": {"type": "string"}},
    # A design detail or light (Milestone 6) names both its parent element / room and its kind.
    "dependentRequired": {"parent": ["kind"], "kind": ["parent"]},
}

SCENE_OBJECT = {
    "type": "object",
    "required": ["name", "wenart_id", "kind", "status", "evidence", "material", "textured", "pass_index", "assumed"],
    "properties": {
        "name": {"type": "string"},
        "wenart_id": {"type": "string"},
        "kind": {"enum": ["wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "furniture",
                          "decor", "camera", "light"] + list(WHOLE_BUILDING_KINDS)},
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
        # Milestone 7 (§6.4): a virtual separator (no geometry) and a built stair.
        "virtual": {"type": "boolean"},
        "line": {"type": ["array", "null"], "items": {"type": "array", "items": {"type": "number"}},
                 "minItems": 2, "maxItems": 2},
        # Milestone 10 (track F): an accent wall (its rooms in room_ids, read by the gate), a piece's design and
        # recolour records, a wall-hung piece's bottom, a lit lamp's light.
        "accent": {"type": "boolean"},
        "accent_material": {"type": ["string", "null"]},
        "design": {"type": "object"},
        "recolour": {"type": "object"},
        "mount_bottom_m": {"type": "number", "minimum": 0},
        "light": {"type": "object", "required": ["name", "energy_w"]},
        # Milestone 10 (track F): the door and window records of the M10 opening geometry (shell.build_door_m10 /
        # build_window_m10: parametric.door_parts / window_parts).
        "door": {"type": "object", "required": ["door_style", "surface_mounted", "handles", "operation"]},
        "window": {"type": "object", "required": ["material", "frame_width", "frame_depth", "mullions", "transoms",
                                                  "inside_sill", "inside_side"]},
        "stair": {"type": "object", "required": ["risers", "riser_m", "riser_source", "flights"],
                  "properties": {"risers": {"type": "integer", "minimum": 2},
                                 "riser_m": {"type": "number", "exclusiveMinimum": 0},
                                 "riser_source": {"type": "string"}, "flights": {"type": "array"}}},
    },
    "allOf": [
        {"if": {"properties": {"kind": {"enum": ["door", "window"]}}, "required": ["kind"]},
         "then": {"required": ["room_ids"]}},
        {"if": {"properties": {"accent": {"const": True}}, "required": ["accent"]},
         "then": {"required": ["room_ids"], "properties": {"kind": {"const": "wall"}}}},
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

_CAMERA_M10 = {
    # Milestone 10 (docs/milestone10.md §1.6b row 11); optional so M9 manifests stay valid.
    "kind": {"enum": ["interior", "exterior"]},
    "variant": {"type": ["string", "null"]},
    "view": {"enum": list(CAMERA_VIEWS) + [None]},
    "sides": {"type": "array", "items": {"enum": list(SIDES)}},
    "region_id": {"type": ["string", "null"]},
    "dropped_reason": {"type": ["string", "null"]},
}
# An exterior camera has no room and no level.
_EXTERIOR_NO_ROOM = {"if": {"properties": {"kind": {"const": "exterior"}}, "required": ["kind"]},
                     "then": {"properties": {"room_id": {"type": "null"}, "level_id": {"type": "null"}}}}

SCENE_CAMERA = {
    "type": "object",
    "required": ["name", "room_id", "level_id", "index", "position", "target", "lens_mm", "sensor_mm",
                 "resolution", "visible_openings", "visible_furniture", "warning"],
    "allOf": [_EXTERIOR_NO_ROOM,
              {"if": {"properties": {"kind": {"const": "interior"}}, "required": ["kind"]},
               "then": {"properties": {"room_id": {"type": "string"}, "dropped_reason": {"type": "null"}}}}],
    "properties": {
        "name": {"type": "string"},
        "room_id": {"type": ["string", "null"]},
        "level_id": {"type": ["string", "null"]},
        "index": {"type": "integer", "minimum": 1},
        **_CAMERA_M10,
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
        # Milestone 8 (docs/milestone8.md §5): why the camera has its lens (search policy; optional).
        "lens_rule": {"type": ["string", "null"]},
    },
}

# Milestone 10: an exterior view no place worked for (no camera object; the scene manifest's cameras_dropped).
DROPPED_CAMERA = {
    "type": "object",
    "required": ["name", "kind", "view", "room_id", "level_id", "sides", "region_id", "variant", "dropped_reason"],
    "properties": dict(_CAMERA_M10, name={"type": "string"}, room_id={"type": "null"}, level_id={"type": "null"},
                       index={"type": "integer", "minimum": 1}, dropped_reason={"type": "string"}),
}
# Milestone 10 (§1.6b row 12): an outside look of exterior.resolve_looks.
EXTERIOR_LOOK = {
    "type": "object",
    "required": ["material", "colour", "source", "assumed", "reason"],
    "properties": {"material": {"type": "string"}, "colour": {"type": ["string", "null"]},
                   "rgb": {"oneOf": [{"type": "null"}, _VEC3]}, "asset": {"type": ["string", "null"]},
                   "source": {"enum": ["documents", "brief", "style", "fallback", "build"]},
                   "assumed": {"type": "boolean"}, "reason": {"type": "string"},
                   "warnings": {"type": "array", "items": {"type": "string"}}},
}
# The manifest's site: what the M3-M9 scene leaves out (built false) or the M10 site build (built true).
SITE_LEFT_OUT = {"type": "object", "required": ["built", "reason"],
                 "properties": {"built": {"const": False}, "reason": {"type": "string"}},
                 "additionalProperties": {"type": "object", "required": ["count", "ids"]}}
SITE_BUILT = {"type": "object", "required": ["built", "mode", "reason", "objects", "terrain", "light_wells"],
              "properties": {"built": {"const": True}, "mode": {"enum": ["full", "ground"]},
                             "reason": {"type": "string"}, "objects": {"type": "array", "items": {"type": "string"}},
                             "terrain": {"type": "object", "required": ["kind", "z", "changes"]},
                             "light_wells": {"type": "array", "items": {
                                 "type": "object", "required": ["opening_id", "source", "reason"]}}}}

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
        # Milestone 7 (§6.2): rooms the camera search gives no view, with the reason.
        "rooms_without_view": {"type": "array", "items": {
            "type": "object", "required": ["room_id", "level_id", "reason"]}},
        "materials": {"type": "object", "additionalProperties": {
            "type": "object", "required": ["textured", "asset", "reason"],
        }},
        "pass_index": {"type": "object", "additionalProperties": {"type": "integer"}},
        "assumed": {"type": "array", "items": ASSUMED_ENTRY},
        "camera_policy": {"enum": ["search", "m5"]},
        "lens_mm": {"type": ["number", "null"]},
        "search_seconds": {"type": ["number", "null"]},
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
                          # Milestone 7: pieces not built (build: false) and the stairs built with the shell.
                          "not_built": {"type": "array", "items": {
                              "type": "object", "required": ["id", "type", "reason"]}},
                          "stairs": {"type": "array", "items": {"type": "string"}},
                      }},
        "site": {"oneOf": [{"type": "null"}, SITE_LEFT_OUT, SITE_BUILT]},
        # Milestone 10 (docs/milestone10.md §1.6, §1.6b rows 8-12), optional.
        "variant": {"type": "object", "required": ["id", "rooms_changed", "exterior_changed", "views"]},
        "variants": {"type": "array", "items": {"type": "object", "required": ["id", "rooms_changed",
                                                                                "exterior_changed"]}},
        "whole_building": {"type": ["object", "null"]},
        "cameras_dropped": {"type": "array", "items": DROPPED_CAMERA},
        "exterior_looks": {"oneOf": [{"type": "null"}, {"type": "object", "additionalProperties": EXTERIOR_LOOK}]},
        "brief": {"type": "object", "additionalProperties": {"type": "object", "required": ["value", "assumed"]}},
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
        # Milestone 6 (§5 rows 7 and 10).
        "window_pull": WINDOW_PULL,
        "alt_preview": {"type": ["string", "null"]},
        "alt_preview_bytes": {"type": ["integer", "null"]},
        # Milestone 8 (§5): the lens the camera was rendered with (optional: older manifests have none).
        "lens_mm": {"type": "number", "exclusiveMinimum": 0},
        "sensor_mm": {"type": "number", "exclusiveMinimum": 0},
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
        # Milestone 6 (§5 rows 10-12).
        "alt_look": {"type": ["string", "null"]},
        "max_bounces": {"type": ["integer", "null"], "minimum": 0},
        "ev_offset": {"type": "number"},
        "preview_quality": {"type": ["integer", "null"], "minimum": 1, "maximum": 100},
        "incomplete": {"type": "boolean"},
        "not_rendered": {"type": "array", "items": {"type": "string"}},
        "deadline": {"type": ["number", "null"]},
        # Review fixes L1 and L2: the applied bounce limits of --max-bounces, and the entries that left
        # `renders` (camera not in the scene, or cut by the deadline with an older build's entry).
        "bounces": {"type": ["object", "null"],
                    "required": ["max_bounces", "diffuse_bounces", "glossy_bounces", "volume_bounces",
                                 "transmission_bounces"],
                    "additionalProperties": {"type": "integer", "minimum": 0}},
        "dropped_stale": {"type": "array", "items": {
            "type": "object", "required": ["camera", "reason", "files"],
            "properties": {"camera": {"type": "string"}, "reason": {"type": "string"},
                           "scene_sha256": {"type": ["string", "null"]}, "render_key": {"type": ["string", "null"]},
                           "files": {"type": "array", "items": {"type": "string"}}}}},
    },
}


def validate_scene_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, SCENE_MANIFEST)


def validate_render_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, RENDER_MANIFEST)
