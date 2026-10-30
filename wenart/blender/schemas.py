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

Milestone 13 (docs/milestone13.md §13.2 T5, §13.3; the lead owns this module), optional so the M11 manifests stay
valid: scene cameras carry ``source`` (``searched`` | ``replayed``: a camera recreated from a scene manifest's record
by ``build.py --cameras-from``, with ``replayed_from``) and a replayed record's ``rotation_euler_deg`` / ``clip_start``
/ ``clip_end``; the scene manifest's ``cameras_from`` (the camera file and what came of it, ``CAMERAS_FROM``) and
``light_variant`` (the ``WENART_LIGHT_VARIANT`` of the build, null in production); render entries' ``lighting_dark``
(the ``Violation`` of a view whose metered EV would pass the +3 cap, ``LIGHTING_DARK``, also under ``exposure``),
``sun_hidden`` and ``vram_mib``; the render manifest's ``lighting_dark`` list, ``white_balance_project`` (the one
whitepoint of the project, ``WHITE_BALANCE_PROJECT``) and ``light_variant`` (``{render, build}``). The per-view
``exposure.wb_mode`` takes the Milestone 13 modes ``project`` | ``kelvin`` (``render.WB_MODES``; every pod job renders
``--white-balance project``), its ``limits`` is null outside mode ``auto`` (``--look-from``, ``--exposure fixed``), and
a replayed camera record may carry ``rotation_euler_deg`` instead of a ``target`` (``_TARGET_OR_ROTATION``: one of
the two is required).

Fix round after P4a (17 Oct 2026; render code m13.3), all optional so the m13.2 manifests stay valid: the exposure's
``wb_rig_residual`` (the rig part's extra warmth of the view's white point, ``render.WB_RIG_RESIDUAL``), the window
pull's ``pane_saturation`` / ``pane_saturation_after``, the sky pull's ``k`` up to 6 (``render.SKY_PULL_STEPS``) with
``ring_px``, ``sun_offset_deg`` and ``into_sun``, and the render entry's ``haze_hidden`` (the haze hidden from the
camera's rays of a view under the interior world; null without haze). The camera replay of the same round: a scene
camera's ``replaced_replayed`` (the replayed record an agent camera replaced) and ``renamed_from`` (a name clash the
build renamed), ``cameras_from.agent`` and ``cameras_from.agent_replaced``.

Fix round after P4b (17 Oct 2026; pod P4b, real03; render code still m13.3), all optional so the P4a / P4b manifests
stay valid: a ``lighting_dark`` finding may be ``minor`` (less than one exposure step over the cap, with
``metrics.below_exposure_step``: reported only); the exposure's ground cap of an exterior view (``ev_facade``,
``ev_ground``, ``ground_p50``, ``ground_headroom_stops``, ``ground_cap``, ``ground_rule``; ``render.exterior_exposure``)
and the white point's ``wb_rig_kelvin_source`` (``room`` | ``scene``, ``render.room_rig_kelvin``) and
``wb_rig_share_p50`` (a block-median share for diagnosis, ``render.rig_share_p50``); the window pull's
``interior_pane_px`` (the panes of the interior glazing it left out) and the render entry's ``interior_glazing``
(``INTERIOR_GLAZING``: the panes of the windows between two indoor rooms against the room's walls,
``render.interior_glazing_record``) and ``lawn`` (an exterior view's lawn as written, ``render.lawn_record``).

Pass before P5 (17 Oct 2026): ``interior_glazing`` requires the panes' ``clip`` as written and may carry ``pull``
(``INTERIOR_PULL``: the pull of clipped interior panes, ``render.RenderRun.interior_pull``); no pod has written an
``interior_glazing`` record yet, so no manifest loses its validity.

Fix round after P6a (22 Oct 2026; render code m13.5), all optional so the m13.4 manifests (P6a real04, P6b real03)
stay valid: the render manifest's ``clamp`` (Cycles' per-sample clamps the render set, ``render.clamp_record``), the
exposure's ``wb_day_green_source``, ``wb_day_green_all``, ``wb_day_wall_share`` and ``wb_tint_green_residual`` (where the
view's daylight green was metered, the all-surface green and the tint rule, ``render.daylight_green``), and the sky pull's ``targets.median_min`` (a free
object already: ``render.SKY_PULL_MEDIAN_MIN``).

Fix round after P6a, part I2 (22-23 Oct 2026; X_ext's ask): the scene camera's frame keys are typed (``SCENE_CAMERA``):
``fill`` (a number >= 0: the share of the frame width the building spans, recorded by the exterior planner and, for
an agent plan, by ``build.finish_agent_exterior_plans``), ``fits`` (boolean), ``sky_share`` (0..1: the share of the
frame's rays that look up into the sky, ``exterior.sky_share``) and ``frame_target`` (the re-centred target, a point).
All optional; every recorded manifest of P4a, P4b, P5 and P6a has only ``fill`` as a number on its cameras.

Fix round after P6b (23 Oct 2026; docs/milestone13.md §7): a scene camera's ``replay`` is the re-pitch record or the
record of a replayed interior camera the build moved off a piece of this build (``status: moved``, with
``position_old``, ``target_old``, ``moved_m``, ``trigger``, ``blocked_by`` and the reason; ``camsearch.
move_blocked_replayed``), and ``cameras_from.moved`` names those cameras. Optional: the recorded manifests stay valid.
The same round's render record (G_render's ask): the exposure's ``wb_walls`` is typed (``WB_WALLS``): null, or the
light on the view's walls in its two metering passes as ``render.wall_rig_record`` writes it (``share``,
``rig_share``, ``light_rgb``, ``day_rgb``, ``rig_rgb``, ``rig_rb``, ``lamp_rb``, ``rig_kelvin``: each a number, an RGB
triple or null; ``rule``: a string). Optional: no pod has written it yet (render code m13.5 is unrendered).
"""
from __future__ import annotations

_EVIDENCE = {"type": "object", "required": ["file", "method", "confidence"]}
_VEC3 = {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
BOX3D = {
    "type": "object",
    "required": ["center", "size", "rotation_deg"],
    "properties": {"center": _VEC3, "size": _VEC3, "rotation_deg": {"type": "number"},
                   # 30 Oct 2026 (optional): a furniture mesh's convex plan outline in the box frame about its centre
                   # (geom2d.plan_outline), read by the GPU index-pass test
                   "outline": {"type": "array", "minItems": 3,
                               "items": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}}},
}
PIXEL_BOX = {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4}
INDEX_STATS = {
    "type": "object",
    "propertyNames": {"pattern": "^[1-9][0-9]*$"},
    "additionalProperties": {"type": "object", "required": ["pixels", "box"],
                             "properties": {"pixels": {"type": "integer", "minimum": 1}, "box": PIXEL_BOX}},
}
# Milestone 13 (docs/milestone13.md §13.2): where a scene camera comes from (``wenart.blender.cameras.replay_cameras``
# gives ``replayed``; the search and the m5 policy ``searched``).
CAMERA_SOURCES = ("searched", "replayed")
# The ``Violation`` shape of ``render.lighting_dark_entry``: a view whose metered EV would pass the cap.
LIGHTING_DARK = {
    "type": "object",
    "required": ["check", "severity", "target", "room_id", "message", "metrics"],
    # fix round after P4b (17 Oct 2026): ``minor`` = less than one exposure step over the cap (reported only)
    "properties": {"check": {"const": "lighting_dark"}, "severity": {"enum": ["minor", "major", "critical"]},
                   "target": {"type": "string"}, "room_id": {"type": ["string", "null"]},
                   "message": {"type": "string"},
                   "metrics": {"type": "object", "required": ["ev_wanted", "ev_used", "ev_cap", "stops_over_cap"],
                               "properties": {"ev_wanted": {"type": "number"}, "ev_used": {"type": "number"},
                                              "ev_cap": {"type": "number"}, "stops_over_cap": {"type": "number"},
                                              "incident_p50": {"type": ["number", "null"]},
                                              "below_exposure_step": {"type": "boolean"}}}},
}
# The one whitepoint of a project (``render.py --white-balance project | kelvin:K``, ``lock_project_whitepoint``):
# ``whitepoint`` null when no interior camera gave light to meter (every view then renders without a white
# balance, noted on its exposure).
WHITE_BALANCE_PROJECT = {
    "type": "object",
    "required": ["whitepoint", "from_camera", "source"],
    "properties": {"whitepoint": {"oneOf": [{"type": "null"}, {"type": "array", "items": {"type": "number",
                                                                                       "exclusiveMinimum": 0},
                                                              "minItems": 3, "maxItems": 3}]},
                   "from_camera": {"type": ["string", "null"]}, "source": {"type": "string"},
                   "residual": {"type": ["number", "null"]}, "kelvin": {"type": "number", "exclusiveMinimum": 0}},
}
# The scene manifest's ``cameras_from`` (``build.cameras_from_summary``): the camera file of ``--cameras-from``
# (``path`` with its ``sha256`` and record count, or ``missing``), the counts of replayed and searched cameras, the
# records dropped with their reason and a ``reason`` when the search ran for everything.
CAMERAS_FROM = {
    "type": "object",
    "required": ["path", "replayed", "searched", "extra", "dropped"],
    "properties": {"path": {"type": "string"}, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                   "missing": {"type": "boolean"}, "cameras": {"type": "integer", "minimum": 0},
                   "build_fingerprint": {"type": ["string", "null"]}, "camera_policy": {"type": ["string", "null"]},
                   "replayed": {"type": "integer", "minimum": 0}, "searched": {"type": "integer", "minimum": 0},
                   "extra": {"type": "boolean"},
                   "dropped": {"type": "array", "items": {"type": "object", "required": ["name", "reason"]}},
                   "reason": {"type": "string"},
                   # fix round part 2 (17 Oct 2026): the replayed aerials the build re-pitched for the horizon
                   "repitched": {"type": "array", "items": {"type": "string"}},
                   # fix round after P6b (23 Oct 2026): the replayed interior cameras the build moved off a piece (§7)
                   "moved": {"type": "array", "items": {"type": "string"}},
                   # fix round after P4a (17 Oct 2026, build.cameras_from_summary): this build's agent cameras (also
                   # counted in ``searched``) and those of them that replace a replayed record
                   "agent": {"type": "array", "items": {"type": "string"}},
                   "agent_replaced": {"type": "array", "items": {"type": "string"}}},
}

_RGB = {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 3, "maxItems": 3}
# Fix round after P6b (23 Oct 2026): the light on a view's walls (``render.wall_rig_record``, written by
# ``Look._view_white`` for every interior view metered with the rig hidden; no white point reads it). Every key is
# always written; a colour is luminance 1 (``render.normalise_whitepoint``, 6 places: a channel may round to 0) or
# null (no light, metering noise, a rig share under ``render.WB_RIG_SHARE_MIN``).
_WALL_RGB = {"oneOf": [{"type": "null"}, {"type": "array", "items": {"type": "number", "minimum": 0},
                                          "minItems": 3, "maxItems": 3}]}
_RATIO = {"type": ["number", "null"], "minimum": 0}
WB_WALLS = {
    "oneOf": [
        {"type": "null"},
        {"type": "object",
         "required": ["share", "rig_share", "light_rgb", "day_rgb", "rig_rgb", "rig_rb", "lamp_rb", "rig_kelvin",
                      "rule"],
         "properties": {"share": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                        "rig_share": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                        "light_rgb": _WALL_RGB, "day_rgb": _WALL_RGB, "rig_rgb": _WALL_RGB,
                        "rig_rb": _RATIO, "lamp_rb": _RATIO,
                        "rig_kelvin": {"type": ["number", "null"]},
                        "rule": {"type": "string"}}},
    ],
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
        # Milestone 13 (K5): project (one metered whitepoint per project) and kelvin (``--white-balance kelvin:K``),
        # ``render.WB_MODES`` plus ``from`` (a --look-from render).
        "wb_mode": {"enum": ["auto", "off", "fixed", "from", "project", "kelvin"]},
        "wb_temperature": {"type": ["number", "null"]},
        "wb_tint": {"type": ["number", "null"]},
        "residual": {"type": ["number", "null"]},
        "window_clip_frac": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "meter_seconds": {"type": "number", "minimum": 0},
        "source": {"type": ["string", "null"]},
        "ev_offset": {"type": "number"},
        # Milestone 13 (K5): the EV limits of the run, the lighting_dark finding of the view, the project whitepoint's
        # source and camera (modes project / kelvin).
        "limits": {"oneOf": [{"type": "null"},                 # null outside mode auto (from, fixed, off)
                             {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}]},
        "lighting_dark": {"oneOf": [{"type": "null"}, LIGHTING_DARK]},
        # pre-flight of pod P3: the stops the floor of ``limits`` moved down for the scene's sun (render.py)
        "floor_shift_stops": {"type": "number", "minimum": 0},
        "wb_source": {"type": ["string", "null"]},
        "wb_from_camera": {"type": "string"},
        # Fix round after P3 (16-17 Oct 2026, render.Look._view_white): the project anchor, the view's rig share and
        # the rig's white point; ``whitepoint`` is then mixed_whitepoint(anchor, rig, share). Optional (older
        # manifests have none).
        "wb_project_whitepoint": {"oneOf": [{"type": "null"}, _RGB]},
        "wb_rig_share": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "wb_rig_kelvin": {"type": ["number", "null"]},
        "wb_rig_whitepoint": {"oneOf": [{"type": "null"}, _RGB]},
        "wb_view_rule": {"type": "string"},
        "wb_view_shift_mired": {"type": "number"},
        "wb_day_incident_p50": {"type": ["number", "null"]},
        # Fix round after P4a (17 Oct 2026): the rig part's extra warmth the view's white point was mixed with
        # (render.WB_RIG_RESIDUAL; 0 = every view keeps the project's daylight cast). Optional.
        "wb_rig_residual": {"type": "number", "minimum": 0, "maximum": 1},
        # Fix round after P4b (17 Oct 2026), optional: whose rig light the view was balanced for
        # (render.room_rig_kelvin: its own room's, or the scene's first), the block-median rig share (diagnosis only,
        # render.rig_share_p50) and the ground cap of an exterior view's exposure (render.exterior_exposure).
        "wb_rig_kelvin_source": {"enum": ["room", "scene"]},
        "wb_rig_share_p50": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "ev_facade": {"type": "number"},
        "ev_ground": {"type": ["number", "null"]},
        "ground_p50": {"type": ["number", "null"]},
        "ground_headroom_stops": {"type": "number", "minimum": 0},
        "ground_cap": {"type": "boolean"},
        # Fix round after P5 (22 Oct 2026, optional): the green ratio of the view's own daylight (render.green_ratio,
        # null without a metered daylight) and the G gain of its white point (render.view_tint_gain, clamped to
        # 1 / WB_TINT_GAIN_MAX .. WB_TINT_GAIN_MAX = 1.3 and rounded to 6 places).
        "wb_day_green": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "wb_view_tint_gain": {"type": "number", "minimum": 0.769231, "maximum": 1.3},
        # Fix round after P6a (22 Oct 2026, optional): the light wb_day_green was metered on (render.WB_TINT_METER: the
        # walls, or every interior surface), the green ratio of every interior surface (m13.4's meter; null without
        # light), the walls' share of the metering frame (render.meter_stats wall_frac; null without a wall metering)
        # and whether the gain kept the mood's residual of the view's green (render.WB_TINT_KEEP_GREEN_RESIDUAL).
        "wb_day_green_source": {"enum": ["surfaces", "walls", None]},
        "wb_day_green_all": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "wb_day_wall_share": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "wb_tint_green_residual": {"type": "boolean"},
        "ground_rule": {"type": "string"},
        # Fix round after P6b (23 Oct 2026, optional): the light on the view's walls (WB_WALLS, recorded only).
        "wb_walls": WB_WALLS,
        # 30 Oct 2026 (m13.6, optional): which rig colour the white point mixed (render.wall_rig_mix: the rig light on
        # the walls, else the lamp's) and by which share (the walls' rig share, else the frame's)
        "wb_rig_source": {"enum": ["walls", "lamp"]},
        "wb_rig_mix_share": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        # 28 Oct 2026 (optional): an exterior view with no facade to meter took the EV of the exterior views metered
        # before it (render.exterior_fallback_ev; how in ``source``)
        "fallback": {"enum": ["exterior"]},
    },
}
_SHARE = {"type": ["number", "null"], "minimum": 0, "maximum": 1}
WINDOW_PULL = {
    "oneOf": [
        {"type": "null"},
        {"type": "object", "required": ["ev", "clip_before", "clip_after", "pane_px"],
         # fix round after P3 (16-17 Oct 2026): render.PULL_STEPS is 1..10 (was 1..4); pane_p90 and the targets
         "properties": {"ev": {"type": "number", "maximum": 0}, "k": {"type": "integer", "minimum": 0, "maximum": 10},
                        "pane_ev": {"type": "number"}, "clip_before": _SHARE, "clip_after": _SHARE,
                        "pane_px": {"type": "integer", "minimum": 1}, "pane_median": {"type": "number"},
                        "pane_p90": {"type": "number"}, "pane_p90_after": {"type": "number"},
                        # fix round after P4a (17 Oct 2026): the panes' median saturation before and after the pull
                        # (optional; P4a's grey cards had 0.00-0.07)
                        "pane_saturation": {"type": "number", "minimum": 0, "maximum": 1},
                        "pane_saturation_after": {"type": "number", "minimum": 0, "maximum": 1},
                        "targets": {"type": "object"},
                        "wall_median": {"type": ["number", "null"]}, "rule": {"type": "string"},
                        # fix round after P4b (17 Oct 2026; optional): the pixels of the interior glazing's panes the
                        # pull left out (render.interior_window_ids)
                        "interior_pane_px": {"type": "integer", "minimum": 0}}},
    ],
}
# Fix round after P4b (17 Oct 2026): the panes of the interior glazing in a view (windows between two indoor rooms,
# left out of the window pull) against the camera room's walls, display R/B of each (render.interior_glazing_record);
# null when none is in view. Pass before P5 (17 Oct 2026; no pod has written the record yet, so ``clip`` is required):
# ``clip`` = the panes' clip share as written, ``pull`` = the interior pull (render.RenderRun.interior_pull: only
# clipped interior panes, by render.choose_interior_pull; k 0 = no pull).
INTERIOR_PULL = {
    "oneOf": [
        {"type": "null"},
        {"type": "object", "required": ["ev", "k", "clip_before", "clip_after", "pane_px", "rule", "tried"],
         "properties": {"ev": {"type": "number", "maximum": 0}, "k": {"type": "integer", "minimum": 0, "maximum": 10},
                        "pane_ev": {"type": "number"}, "clip_before": _SHARE, "clip_after": _SHARE,
                        "pane_px": {"type": "integer", "minimum": 1}, "pane_median": {"type": "number"},
                        "pane_median_after": {"type": "number"}, "wall_median": {"type": ["number", "null"]},
                        "rule": {"type": "string"}, "targets": {"type": "object"},
                        "tried": {"type": "array", "items": {
                            "type": "object", "required": ["k", "clip", "median"],
                            "properties": {"k": {"type": "integer", "minimum": 1, "maximum": 10}, "clip": _SHARE,
                                           "median": {"type": "number"}}}},
                        "seconds": {"type": "number", "minimum": 0}}},
    ],
}
INTERIOR_GLAZING = {
    "oneOf": [
        {"type": "null"},
        {"type": "object", "required": ["windows", "pane_px", "pane_rb", "wall_rb", "delta_rb", "clip", "rule"],
         "properties": {"windows": {"type": "array", "items": {"type": "string"}},
                        "pane_px": {"type": "integer", "minimum": 1}, "pane_rb": {"type": ["number", "null"]},
                        "wall_rb": {"type": ["number", "null"]}, "delta_rb": {"type": ["number", "null"]},
                        "clip": _SHARE, "pull": INTERIOR_PULL, "rule": {"type": "string"}}},
    ],
}
# Fix round after P3 (16-17 Oct 2026): the sky pull of a view under the exterior sky (render.Renderer.sky_pull);
# k 0 = no pull (render.SKY_PULL_STEPS is 1..4; 1..6 since the fix round after P4a, 17 Oct 2026).
SKY_PULL = {
    "oneOf": [
        {"type": "null"},
        {"type": "object", "required": ["ev", "k", "sky_px", "sky_share", "median_before", "median_after", "rule"],
         "properties": {"ev": {"type": "number", "maximum": 0}, "k": {"type": "integer", "minimum": 0, "maximum": 6},
                        "sky_ev": {"type": "number"}, "sky_px": {"type": "integer", "minimum": 1},
                        "sky_share": _SHARE, "median_before": {"type": "number"}, "median_after": {"type": "number"},
                        "saturation_before": {"type": "number"}, "saturation_after": {"type": "number"},
                        "rule": {"type": "string"}, "targets": {"type": "object"}, "tried": {"type": "array"},
                        # fix round part 3 (17 Oct 2026): the haze-shell pixels counted as sky (render.haze_sky) and
                        # the share of the sky at full feather weight (render.full_weight_share; optional, older
                        # records have neither)
                        "haze_px": {"type": "integer", "minimum": 0}, "full_weight_share": _SHARE,
                        # fix round after P4a (17 Oct 2026; optional): the ring pixels outside the mask that got part
                        # of the pull (render.sky_pull_weights), the degrees between the view's and the sun's azimuth
                        # (render.sun_offset_deg, null without a sun lamp) and whether the view looks into the sun
                        "ring_px": {"type": "integer", "minimum": 0},
                        "sun_offset_deg": {"type": ["number", "null"], "minimum": 0, "maximum": 180},
                        "into_sun": {"type": "boolean"},
                        # fix round after P5 (22 Oct 2026; optional): the edge pixels left brighter than the pulled
                        # sky and the surface beside them, and the edge pixels looked at (render.sky_edge_dots)
                        "edge_dot_px": {"type": "integer", "minimum": 0},
                        "edge_px": {"type": "integer", "minimum": 0}}},
    ],
}
# Milestone 10 (docs/milestone10.md §1.6b row 11): object kinds of the whole building; views.KIND_MAP never maps
# them to furniture.
WHOLE_BUILDING_KINDS = ("slab", "roof", "facade", "terrain", "site_wall", "site_area", "site_decor", "light_well",
                        "railing",
                        # Milestone 11 (docs/milestone11.md §1.1 E10, E11): the inferred site and the facade details
                        "site_steps", "site_boundary", "facade_detail", "splashback",
                        # 11 Oct 2026 (real04): the other buildings on the plot (instances) and the pools
                        "building_copy", "site_pool",
                        # Milestone 13 (T6, round 2): the site parts of their own (platforms, hedges, grass, the haze
                        # volume); common.KINDS and views.SITE_PART_KINDS list the same names, site.site_kind
                        # writes them only once this tuple knows them
                        "site_platform", "site_hedge", "site_grass", "atmosphere",
                        # site.entrance_meshes: an entrance's ramp and handrails (common.KINDS, 24 Oct 2026)
                        "site_ramp", "site_handrail",
                        # 29 Oct 2026 (UL112): the light switches and sockets of a level (wall_plates, common.KINDS)
                        "wall_plate")
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

# Milestone 13 (K8): a searched camera aims at its ``target``; a camera replayed from a record that carries a rotation
# only (``cameras.replay_cameras``, ``create_cameras``) has ``rotation_euler_deg`` and a null or absent ``target``.
_TARGET_OR_ROTATION = {"anyOf": [{"required": ["target"], "properties": {"target": {"type": "array"}}},
                                 {"required": ["rotation_euler_deg"]}]}
_CAMERA_REPLAY_REPITCHED = {
    "type": "object",
    "required": ["status", "pitch_deg_old", "pitch_deg", "lens_mm_old", "lens_mm", "horizon_frac_old", "horizon_frac"],
    "properties": {"status": {"enum": ["repitched"]}, "pitch_deg_old": {"type": "number"},
                   "pitch_deg": {"type": "number"}, "lens_mm_old": {"type": "number", "exclusiveMinimum": 0},
                   "lens_mm": {"type": "number", "exclusiveMinimum": 0}, "horizon_frac_old": {"type": "number"},
                   "horizon_frac": {"type": "number"}, "shift_y_old": {"type": "number"},
                   "position_old": _VEC3, "distance_m": {"type": "number", "exclusiveMinimum": 0},
                   "reason": {"type": "string"}},
}
# Fix round after P6b (23 Oct 2026; docs/milestone13.md §7): a replayed interior camera the build moved off a piece of
# this build that blocks or contains it (``camsearch.move_blocked_replayed``): the old pose, how far, why and by what,
# the model's one-element share at the old and the new pose. Yaw, pitch, height and lens are the record's.
_CAMERA_REPLAY_MOVED = {
    "type": "object",
    "required": ["status", "position_old", "target_old", "moved_m", "trigger", "blocked_by", "reason"],
    "properties": {"status": {"enum": ["moved"]}, "position_old": _VEC3, "target_old": _VEC3,
                   "moved_m": {"type": "number", "exclusiveMinimum": 0},
                   "trigger": {"enum": ["single_share", "inside"]}, "blocked_by": {"type": ["string", "null"]},
                   "blocked_by_type": {"type": ["string", "null"]},
                   "share_old": {"type": "number", "minimum": 0, "maximum": 1},
                   "share": {"type": "number", "minimum": 0, "maximum": 1}, "reason": {"type": "string"}},
}
_CAMERA_REPLAY = {"oneOf": [_CAMERA_REPLAY_REPITCHED, _CAMERA_REPLAY_MOVED]}
SCENE_CAMERA = {
    "type": "object",
    "required": ["name", "room_id", "level_id", "index", "position", "lens_mm", "sensor_mm",
                 "resolution", "visible_openings", "visible_furniture", "warning"],
    "allOf": [_EXTERIOR_NO_ROOM, _TARGET_OR_ROTATION,
              {"if": {"properties": {"kind": {"const": "interior"}}, "required": ["kind"]},
               "then": {"properties": {"room_id": {"type": "string"}, "dropped_reason": {"type": "null"}}}}],
    "properties": {
        "name": {"type": "string"},
        "room_id": {"type": ["string", "null"]},
        "level_id": {"type": ["string", "null"]},
        "index": {"type": "integer", "minimum": 1},
        **_CAMERA_M10,
        "position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "target": {"oneOf": [{"type": "null"}, {"type": "array", "items": {"type": "number"}, "minItems": 3,
                                                "maxItems": 3}]},
        "lens_mm": {"type": "number"},
        "sensor_mm": {"type": "number"},
        "resolution": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "visible_openings": {"type": "array", "items": {"type": "string"}},
        "visible_furniture": {"type": "array", "items": {"type": "string"}},
        "warning": {"type": ["string", "null"]},
        # Milestone 6 (docs/milestone6.md §1.3); optional so M5 manifests stay valid.
        "shift_x": {"type": "number"},
        "shift_y": {"type": "number"},
        "policy": {"enum": ["search", "m5", "agent"]},      # agent: a fixed camera of the agent (M11 §17.3)
        "score": {"type": ["object", "null"]},
        # Milestone 8 (docs/milestone8.md §5): why the camera has its lens (search policy; optional).
        "lens_rule": {"type": ["string", "null"]},
        # Milestone 13 (docs/milestone13.md §13.2, K8): a searched camera or one replayed from a scene manifest's
        # record (``cameras.replay_cameras``: the record's rotation and clip when it carries them; ``extra`` marks the
        # searched camera of a room that also has a replayed one, --cameras-extra).
        "source": {"enum": list(CAMERA_SOURCES)},
        "replayed_from": {"type": "object", "properties": {"build_fingerprint": {"type": ["string", "null"]},
                                                           "camera_policy": {"type": ["string", "null"]},
                                                           "policy": {"type": ["string", "null"]}}},
        "rotation_euler_deg": _VEC3,
        "clip_start": {"type": "number", "exclusiveMinimum": 0},
        "clip_end": {"type": "number", "exclusiveMinimum": 0},
        "extra": {"type": "boolean"},
        # Exterior plans (``exterior.plan_exterior``): the pitch (negative = down) and where the horizon lies in the
        # frame (0 bottom, 1 top). Fix round part 2 (17 Oct 2026): ``replay`` of a replayed aerial the build re-pitched
        # so the horizon is in its frame (``build.repitch_replayed_aerials``, CLAUDE.md horizon rule); optional. Fix
        # round after P6b (23 Oct 2026): or of a replayed interior camera the build moved off a piece (status moved).
        "pitch_deg": {"type": "number"},
        "horizon_frac": {"type": "number"},
        "replay": _CAMERA_REPLAY,
        # fix round after P4a (17 Oct 2026, build.merge_agent_cameras, overrides.replaced_replayed_of): the replayed
        # record an agent camera replaced (its pose, lens, shift, view, sides and replay trail), and the name a camera
        # had before build.dedupe_camera_names renamed a clash to <name>_dup<k>; both optional
        "replaced_replayed": {"type": "object",
                              "properties": {"position": _VEC3,
                                             "target": {"oneOf": [{"type": "null"}, _VEC3]},
                                             "rotation_euler_deg": _VEC3, "lens_mm": {"type": "number"},
                                             "shift_x": {"type": "number"}, "shift_y": {"type": "number"},
                                             "view": {"type": ["string", "null"]},
                                             "sides": {"type": "array", "items": {"type": "string"}},
                                             "replayed_from": {"type": "object"}, "replay": {"type": "object"}}},
        "renamed_from": {"type": "string"},
        # fix round after P6a (part I2, X_ext's ask): the frame of an exterior camera (``exterior.frame_check``; the
        # planner records ``fill``, build.finish_agent_exterior_plans all four on an agent plan); optional
        "fill": {"type": "number", "minimum": 0},
        "fits": {"type": "boolean"},
        "sky_share": {"type": "number", "minimum": 0, "maximum": 1},
        "frame_target": _VEC3,
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
                   "source": {"enum": ["documents", "brief", "style", "fallback", "build", "agent"]},   # agent: M11
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
        # pod P8: the build's time per phase (walls, furniture, cameras, previews, save, glb ...), summed over levels
        "phase_seconds": {"type": "object", "additionalProperties": {"type": "number"}},
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
        # Milestone 13 (docs/milestone13.md §13.2 T5): the camera replay and the light variant of the build
        # (``WENART_LIGHT_VARIANT``; null = production), optional so the M11 manifests stay valid.
        "cameras_from": {"oneOf": [{"type": "null"}, CAMERAS_FROM]},
        "light_variant": {"type": ["string", "null"]},
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
        # Milestone 13 (docs/milestone13.md §13.2 T5): the view's lighting_dark finding (null within the cap), whether
        # the sun lamp was hidden under the sun-disc sky (exterior cameras) and the GPU memory after the view.
        "lighting_dark": {"oneOf": [{"type": "null"}, LIGHTING_DARK]},
        "sun_hidden": {"type": "boolean"},
        "vram_mib": {"type": ["integer", "null"], "minimum": 0},
        # Fix round after P3 (16-17 Oct 2026): the camera's room type, whether it is an open-air room (rendered under
        # the exterior world) and the sky pull of a view under the exterior sky.
        "room_type": {"type": ["string", "null"]},
        "open_air": {"type": "boolean"},
        "sky_pull": SKY_PULL,
        # Fix round part 2 (17 Oct 2026): the clip range the view was rendered with (render.set_view_clip): an
        # open-air view under the exterior world takes the exterior clip end (rule set), every other view its own
        # (rule null); optional, older manifests have none.
        "clip": {"type": "object", "required": ["start_m", "end_m", "built_end_m", "rule"],
                 "properties": {"start_m": {"type": "number", "exclusiveMinimum": 0},
                                "end_m": {"type": "number", "exclusiveMinimum": 0},
                                "built_end_m": {"type": "number", "exclusiveMinimum": 0},
                                "rule": {"type": ["string", "null"]}}},
        # Fix round after P4a (17 Oct 2026): whether the haze volume was hidden from the camera's rays (a view under the
        # interior world, render.haze_hidden_for); null in a scene without haze. Optional.
        "haze_hidden": {"type": ["boolean", "null"]},
        # Fix round after P4b (17 Oct 2026; optional): the interior glazing in view (INTERIOR_GLAZING) and an exterior
        # view's lawn as written (render.lawn_mask / lawn_record: share of the frame, display saturation and median).
        "interior_glazing": INTERIOR_GLAZING,
        "lawn": {"oneOf": [{"type": "null"},
                           {"type": "object", "required": ["px_share", "saturation", "median"],
                            "properties": {"px_share": _SHARE, "saturation": _SHARE, "median": {"type": "number"}}}]},
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
        # Milestone 13 (docs/milestone13.md §13.2 T5, K5): the EV limits of the run, the views whose metered EV
        # passed the cap (a Violation each, for the report), the project whitepoint and the light variant of the
        # render and of the build (``WENART_LIGHT_VARIANT``; null = production). Optional: M11 manifests have none.
        "exposure_limits": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
        # pre-flight of pod P3: the EV floor moved down for the scene's sun (render.sun_floor_shift), optional
        "exposure_floor": {"type": ["object", "null"], "required": ["shift_stops", "view_limits"],
                           "properties": {"sun_wm2": {"type": ["number", "null"]},
                                          "reference_wm2": {"type": "number"},
                                          "shift_stops": {"type": "number", "minimum": 0},
                                          "view_limits": {"type": "array", "items": {"type": "number"},
                                                          "minItems": 2, "maxItems": 2}}},
        "lighting_dark": {"type": "array", "items": LIGHTING_DARK},
        "white_balance_project": {"oneOf": [{"type": "null"}, WHITE_BALANCE_PROJECT]},
        "light_variant": {"type": ["object", "null"], "properties": {"render": {"type": ["string", "null"]},
                                                                     "build": {"type": ["string", "null"]}}},
        # Fix round after P6a (22 Oct 2026; optional, older manifests have none): Cycles' per-sample clamps the render
        # set (render.clamp_record: direct 0 = off, indirect render.CLAMP_INDIRECT = 10 unless --clamp-indirect).
        "clamp": {"type": ["object", "null"], "required": ["direct", "indirect"],
                  "properties": {"direct": {"type": "number", "minimum": 0},
                                 "indirect": {"type": "number", "minimum": 0}}},
    },
}


def validate_scene_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, SCENE_MANIFEST)


def validate_render_manifest(manifest: dict) -> None:
    import jsonschema

    jsonschema.validate(manifest, RENDER_MANIFEST)
