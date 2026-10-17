"""Render the cameras of a built scene with Cycles (run inside Blender).

    blender -b outputs/<p>/scene/scene.blend --python wenart/blender/render.py -- \
        --cameras all|cam_a,cam_b --samples 256 --res 1920x1080 --out outputs/<p>/renders [--force] \
        [--exposure auto|off|<EV>] [--exposure-target 0.9] [--white-balance auto|off|fixed:r,g,b] \
        [--look-from <render_manifest.json>] [--hide ID[,ID] [--plug]] [--hide-sets 'cam:id;cam:id+plug'] \
        [--alt-look None] [--max-bounces N] [--no-denoise] [--ev-offset X] [--preview-quality Q]

Device: OPTIX, then CUDA, then CPU (printed as ``DEVICE=...``). Passes:
Combined, Depth (Z), Normal, Object Index (every proxy and opening has a
unique ``pass_index`` from the scene manifest) and Diffuse Color (Milestone
6, the pane mask of the window pull). Files per camera:
``<cam>.png`` (display-referred RGB8: AgX, look ``LOOK``, the camera's exposure
and white balance), ``<cam>_passes.exr`` (multilayer, half float, ZIP,
scene-linear: exposure and white balance never reach it),
``<cam>_preview.jpg`` (<= 300 KB), and the helper maps written with the
``wenart.views`` encoders (docs/milestone5.md §2.5): ``<cam>_index.png``
(uint16, pixel = pass index), ``<cam>_depth_mm.png`` (uint16 planar depth in
mm, 0 = no surface), ``<cam>_normal.png`` (RGB8 world normal, (0, 0, 0) =
no surface) and the legacy ``<cam>_depth.png`` (16-bit, per-view min..max,
near = dark). ``render_manifest.json`` lists per camera the samples, device
time, depth range, index values, ``index_stats`` (pixels and box per index),
the exposure record, the ``render_key`` and the camera's ``lens_mm`` /
``sensor_mm`` as rendered (Milestone 8: 18 or 16 mm for searched cameras;
a lens change is a scene change, so ``scene_sha256`` re-renders it); the pass index table keyed by
wenart id (identical to the scene manifest's) and the scene fingerprint
(``scene_sha256`` of ``scene.blend``).

Per-camera exposure and white balance (§2.4): before the final render a
metering pre-render at 1/8 resolution, 16 samples, no denoiser, no adaptive
sampling, with the Diffuse Direct / Indirect / Color passes on (off again
afterwards), written to a temporary EXR and read with Blender's
OpenImageIO. Interior pixels (not a window index, a surface hit, diffuse
albedo luminance >= 0.02) give the incident light Y = luminance(direct +
indirect), the colour-free light a grey card would meter; block means over
``width // 40`` px blocks, Y50 = median of the blocks that are >= 75 %
interior. ``view_settings.exposure = clamp(log2(target / Y50), -2, +8)``
rounded to 1/6 stop. White balance: the illuminant (sum of direct + indirect
over the interior, G = 1) raised to ``1 - residual`` (the residual keeps
part of the mood's colour: warm daylight 0.35, golden evening 0.5, cool
daylight 0, overcast 0, night 0.5) and normalised to luminance 1 becomes
``white_balance_whitepoint``. The mood is the scene property
``wenart_mood`` written by build.py. ``--look-from`` copies the EV and
whitepoint of another render manifest's entry instead (controls use it so a
hidden-object render has the look of the normal one).

Hidden-object controls (§2.6): ``--hide`` hides the objects with a pass
index whose wenart id (``proxy:`` dropped) is listed (a door's frame and
leaf, a window's frame and glass, a piece with its decor); ``--plug`` closes
the wall hole of a hidden door or window with a box (pass index 0) that
carries the wall's material slots, each face with the slot of the wall face
around the hole on its side (wet-room tiles, exterior plaster;
``plug_face_slots``), and switches its portal off. ``--hide-sets`` renders
several controls in one Blender process, each set into ``<out>/hide_<id>/``.
An unknown id, an unknown camera or a ``--look-from`` manifest without the
camera exits with 2 before anything is rendered.

Idempotent and resumable: the manifest is rewritten after every camera, so a
killed run keeps what it rendered. A camera is reused ("skipped") only when
its PNG, EXR, preview and helper maps exist, and its manifest entry carries
the fingerprint of the current scene.blend and the same ``render_key``
(first 16 hex of sha256 over samples, resolution, denoiser, exposure mode,
target, limits or look-from values, white-balance mode, passes, hidden and
plugged ids and ``RENDER_CODE_VERSION``); an entry without a render key
(Milestone 4) is stale. A reused camera's statistics are read again from
the EXR and its measured seconds and exposure are kept. Anything else is
rendered again and the reason is printed. A ``--cameras`` subset merges into
the previous manifest; entries of cameras that no longer exist in the scene
are dropped with a warning and listed under ``dropped_stale`` (camera,
reason, the entry's ``scene_sha256`` and ``render_key``, the names of its
files still on disk). The files are never deleted; ``dropped_stale`` is
carried over by later runs while files of the camera remain and it has no
entry again; readers take views from ``renders`` only. ``--force``
re-renders everything asked.

Why no compositor: Blender 5.x replaced ``scene.node_tree`` by
``compositing_node_group`` and reworked the File Output node; the multilayer
EXR output needs none of that, and the passes are read back with the OpenImageIO
module bundled with Blender (3.1 in 5.2.2). Render Result pixels cannot be
read in background mode (5.2.2), so metering also goes through an EXR.

Milestone 6 (docs/milestone6.md §5 rows 7, 10-12; ``RENDER_CODE_VERSION``
``m6.1``):

- Window pull: the final render also writes the Diffuse Color pass (the EXR
  gains the layer Blender 5.2.2 names ``Diffuse Color``, older builds
  ``DiffCol``; the other passes are unchanged). After the render the Render
  Result is saved again at EV - k (Blender applies the view transform at
  save time: no second render) to a temporary PNG and read back with OIIO.
  Pane mask = window index and Diffuse Color luminance < 0.05 (the glass, not
  the frame), feathered over 3 px inwards (numpy, ``views.erode``). k = the
  smallest of 1..4 with pane clip <= 1 % and pane median > wall median (walls
  = ``views.regions`` ``struct:walls`` of the view); if none qualifies, the k
  with the lowest clip that keeps the panes brighter than the walls; with no
  wall pixels the clip rule alone; when no k keeps the panes brighter, no
  pull. The pulled panes are blended into ``<cam>.png`` and the preview
  (pixels outside the mask stay exactly as saved) and recorded as
  ``window_pull: {ev (-k), k, pane_ev, clip_before, clip_after, pane_px,
  pane_median, wall_median, rule}``, ``null`` when no pane is in view.
- ``--alt-look <look>`` (Milestone 6: ``"AgX - Punchy"``; Milestone 7: ``None``):
  also ``<cam>_alt_preview.jpg``, the Render
  Result saved with that look at the EV and, when the panes were pulled, at
  EV - k with the main image's k, blended with the same mask.
- Control and A/B flags (§6): ``--max-bounces N``, ``--no-denoise``,
  ``--ev-offset X`` (added to the auto, fixed or ``--look-from`` EV) and
  ``--preview-quality Q`` (one fixed JPEG quality, no size step-down); every
  one is part of the render key. ``--max-bounces N`` (the ``ctl_direct``
  control) sets N diffuse, glossy and volume bounces (``bounce_settings``);
  transmission and the total stay at >= 2 so a camera ray still passes both
  faces of the window glass (a Glass BSDF for camera rays: with
  ``max_bounces = 0`` every pane rendered black, review L1). The applied
  values are in the render key and the manifest (``bounces``).
- Deadline: once ``WENART_DEADLINE`` (epoch seconds, environment) is past,
  no new camera is rendered (cameras whose files can be reused still are);
  the manifest says ``incomplete: true`` and lists ``not_rendered``; exit 3.
  A not-rendered camera whose carried-over entry was rendered from another
  scene build loses that entry (listed under ``dropped_stale``, files kept),
  so no reader takes an older build's image for a view of this scene
  (review L2).
  Previews with a pull are written by Blender's JPEG writer from the
  blended PNG (``encode_preview``), the same encoder and quality as a direct
  save (decoded pixels equal).

Milestone 7 (docs/milestone7.md §6.1, user decision 6; ``RENDER_CODE_VERSION``
``m7.1``): the default look is ``AgX - Punchy`` (``LOOK``; Milestones 5-6 used
``None``). The view transform and the look are part of the render key, so a
render of another look is never reused. The window pull saves its EV - k
images with the same look (``save_display(..., look=LOOK)``), so the pulled
panes blend into a picture of one look. The A/B alternative is now the old
look: ``--alt-look None`` (``stages.ALT_LOOK``). EV and white balance are
metered scene-linear (before the view transform) and do not change.

Milestone 10 (docs/milestone10.md §3.3): an exterior camera (custom property
``wenart_camera_kind = exterior``, ``exterior.create_cameras``) meters its
facades: the meter mask keeps the surfaces whose world normal is nearly
horizontal (walls, not the ground, the roof or the sky; ``meter_stats``
``normal_z``) when they fill at least 2 % of the frame; the record says
``meter.metered``. Interior cameras are metered as before; render entries
carry ``room_id`` / ``level_id`` None for exterior views.

Milestone 13 (docs/milestone13.md §13.2 render.py, K5; ``RENDER_CODE_VERSION`` ``m13.1``):

- ``EXPOSURE_LIMITS = (-2.0, 3.0)``: the auto exposure never pushes a view more than +3 EV (the +6..+8 pushes of
  Milestone 11 smeared the denoiser and hid dark rooms). When the metered EV would pass the cap the render keeps
  +3 and writes a ``lighting_dark`` entry (the ``Violation`` shape: check ``lighting_dark``, severity major, or
  critical 2 stops over the cap, target the camera, ``room_id``, ``metrics`` ev_wanted / ev_used / ev_cap /
  incident_p50) on the camera's manifest entry and in the manifest's ``lighting_dark`` list, for the report (T8)
  and the agent. The A/B variants without the cap lever (``WENART_LIGHT_VARIANT`` ``m11`` and the single ``sun*`` /
  ``rig`` / ``shell`` levers, ``lighting.light_levers``; ``base`` before round 3) keep the Milestone 11 limits
  ``EXPOSURE_LIMITS_M11`` (-2..+8); production, ``base`` (round 3) and every run with ``evcap`` use the cap
  (``exposure_limits_for``). Pre-flight of pod P3: the floor (-2) was set under the M11 sun of 3 W/m²; it moves down
  by ``sun_floor_shift`` (log2 of the scene's sun lamp over 3 W/m², 8.4 stops at 1000 W/m²) so a sunlit facade or
  room is not held stops too bright; each entry's ``exposure.limits`` are the limits it was metered against and
  the manifest's ``exposure_floor`` records the sun and the shift (``exposure_limits`` stays the run's cap).
- ``--white-balance project``: one whitepoint for every view of a project. It comes from the previous render
  manifest of the folder (``white_balance_project``, so a re-render keeps it), else it is metered once before the
  loop; ``kelvin:<K>`` sets it from a colour temperature (the brief's ``render.white_balance_k``, wired through
  stages.render) through Blender's own conversion. The record says ``wb_mode: project`` and ``wb_source``; the
  render key carries the whitepoint, so a changed one re-renders. ``auto`` (per view) and ``off`` stay for the
  controls and the previews.
  Round 3 (docs/milestone13.md §14.3; P1 metered the rig-lit real02 bathroom at 3,422 K and turned every daylight
  view blue-grey, the Milestone 11 daylight white point was 5,408 K): the project white point is metered on
  daylight only. The metering pass hides every rig object (the lights and the emissive shades, ``wenart_rig``), so
  the illuminant is the sun, the sky and the HDRI. The candidates are the interior cameras of rooms whose window
  faces the sun (``sunlit_rooms``), then of the other rooms with a window portal (``daylight_rooms``), name order
  (``wb_camera_order``); up to ``WB_METER_MAX_CAMERAS`` are metered and the one with the most incident light sets
  the white point (``pick_wb_candidate``: the sun, not a sky-lit window; round-3 review, synthetic-01's sky-lit
  bath read 9,068 K and cast the sunlit living room orange). The record ``white_balance_project`` carries
  ``kelvin`` (Blender's temperature of the whitepoint), ``metered_on``, ``daylight_only: true``, ``tried``,
  ``candidates`` and the hidden rig count; a previous record is reused only when it was metered that way (or came
  from ``kelvin:``).
- ``select_world``: under the exterior world with a sun disc for every ray (``wenart_world_exterior_sun_disc``
  without ``wenart_world_exterior_disc_camera_only``, the P1 world) the sun lamp is hidden, so the sky's disc is
  the one direct sun. Round 3: the exterior world shows the disc to camera rays only (``materials.
  exterior_world_nodes``), so the lamp stays shown under it (``sun_hidden_for``) and is the one direct sun.

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8; ``RENDER_CODE_VERSION`` ``m13.2``). What: four
changes to the light and colour of the views. Why: pod P3 (real04) rendered 24 of 48 views with an orange cast, the
roof terraces under the interior HDRI (a black or dusk sky), the exteriors 3.7 stops apart and every window as a
blank pale plane. How:

- White balance per view (``mixed_whitepoint``): the project white point stays the anchor (metered on daylight, the
  rig hidden, as round 3). For every interior view a second metering pass with the rig hidden gives the view's
  daylight; ``rig_share`` = 1 - daylight / all light (luminance of the metered illuminants). The view's white point
  is the project's daylight colour mixed with the rig's light colour by that share (light adds linearly) and
  corrected with the mood's residual, as the project white point is: a daylight view (share < ``WB_RIG_SHARE_MIN``)
  keeps the project white point exactly, a room lit only by the rig gets the rig's own white point (the 2700 K rig
  under the 5,635 K daylight point turned P3's windowless baths and halls orange), a mixed room (P3's basement
  kitchen: daylight + strips + a ceiling fixture) moves part of the way. The rig's light colour is Blender's white
  point at the rig's temperature and tint 0 (``kelvin_whitepoint``; measured on bpy 5.2.2: a white plane under a
  2700 K point light gave G-normalised (2.4082, 1, 0.2386), the white point at 2700 K (2.4086, 1, 0.2393)). Wall
  bounce colours do not move the white point (only the luminance share and the two light colours do). The record
  keeps ``wb_mode: project`` and adds ``wb_project_whitepoint``, ``wb_rig_share``, ``wb_rig_kelvin``,
  ``wb_rig_whitepoint``, ``wb_view_rule`` and ``wb_view_shift_mired``; exterior and open-air views keep the
  project white point.
- Open-air rooms (``open_air``: ``shell.OUTDOOR_ROOM_TYPES``, the roof terraces and balconies of real02 / real04)
  render under the exterior world and follow its sun-lamp rule (``world_for`` / ``sun_hidden_for`` take the room
  type). The type comes from the camera's ``wenart_room_type`` (``cameras.create_cameras``), else from the scene
  manifest's room floors (``room_types_from_manifest``). The project white point is still metered under the interior
  world (``lock_project_whitepoint`` passes no room type), so P3's 5,635 K does not move.
- Sky pull (``choose_sky_pull``): a view under the exterior sky meters its facades (Milestone 10) and keeps that
  exposure; the sky (no surface hit in the depth pass) is saved again at EV - k like the window panes, k the smallest
  of ``SKY_PULL_STEPS`` whose sky median is at most ``SKY_PULL_MEDIAN_MAX`` (under the AgX shoulder) and whose median
  saturation is at least ``SKY_PULL_SAT_MIN``; none qualifies or the sky already does: no pull. Recorded as
  ``sky_pull``. No state is shared between cameras, so subset renders, agent previews and variants agree.
- Window pull down to 10 stops (``PULL_STEPS``) with a pane target: a k qualifies when the pane clip is at most 1 %
  and the pane highlights are under the shoulder (pane p90 <= ``PULL_P90_MAX``) or the pane median has reached
  ``PULL_MEDIAN_TARGET``, and the panes stay brighter than the walls. P3 stopped at k 1-2 with pane medians of
  0.86-0.97 (the sunlit outside 5-8 stops over), the blank pale windows. The pairing of the interior HDRI with the
  sun stays an A/B lever (off).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path


def _repo_root() -> Path:
    env = os.environ.get("WENART_REPO_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


sys.path.insert(0, str(_repo_root()))

DEFAULT_SAMPLES = 256
DEFAULT_RES = (1920, 1080)
PREVIEW_MAX_BYTES = 300_000
DEPTH_BACKGROUND = 1e9  # Blender writes a huge value where no surface was hit
# Part of every render_key: bump when the pixels a camera gets change for the same settings.
# m5.2: plugs take the wall faces' materials (wet-room tiles). The window glass of the same
# day (both faces refract) is a build change: the build fingerprint and scene_sha256 cover it.
# m6.1: the Diffuse Color pass in the final render and the window pull (docs/milestone6.md §5).
# m7.1: the look AgX - Punchy (docs/milestone7.md §6.1); view transform and look also enter the key.
# m13.1: the EV cap +3 with the lighting_dark record, the project white balance, the sun lamp hidden under the
# exterior sky with a sun disc (docs/milestone13.md §13.2).
# m13.2 (fix round after P3, 16-17 Oct 2026): the view's white point mixed from the project's daylight and the rig by
# the view's rig share, open-air rooms under the exterior world, the sky pull, the window pull to 10 stops.
RENDER_CODE_VERSION = "m13.2"
PASSES = ("combined", "z", "normal", "object_index", "diffuse_color")
VIEW_TRANSFORM = "AgX"
LOOK = "AgX - Punchy"
PREVIEW_QUALITIES = (85, 70, 55, 40, 30, 20)

# Window pull (docs/milestone6.md §5 row 7). Fix round after P3 (16-17 Oct 2026): up to 10 stops (P3's interiors
# metered +0.3..+2.5 EV, the sunlit outside -4..-7.7: k 1-2 left the panes at medians 0.86-0.97, a blank pale plane);
# a k qualifies when the pane highlights are under the AgX shoulder (p90 <= PULL_P90_MAX) or the pane median has
# reached PULL_MEDIAN_TARGET (a deeper pull would only darken the outside), with the clip and wall rules as before.
PULL_STEPS = tuple(range(1, 11))   # stops tried, smallest first
PULL_MAX_CLIP = 0.01               # pane clip share a pull should reach
PULL_P90_MAX = 0.85                # pane display luminance p90 a pull should reach (the AgX shoulder)
PULL_MEDIAN_TARGET = 0.65          # ... or the pane median at mid-tone: stop pulling there
# Sky pull (fix round after P3): a view under the exterior sky keeps its facade exposure; its sky is pulled by the
# smallest k whose median is under the shoulder and whose median saturation reaches the floor (P3: ext_1/2/4 skies
# 0.92 / 0.84 / 0.81 at saturation 0.03-0.13, ext_3 0.27 and ext_7 0.20 read blue).
SKY_PULL_STEPS = (1, 2, 3, 4)
SKY_PULL_MEDIAN_MAX = 0.8
SKY_PULL_SAT_MIN = 0.12
SKY_PULL_MIN_SHARE = 0.005         # a sky smaller than this share of the frame is not pulled
PANE_ALBEDO_MAX = 0.05             # pane = window index and Diffuse Color luminance below this (glass, not frame)
PULL_FEATHER_PX = 3                # the mask edge blends over this many pixels, inside the mask
DISPLAY_PNG_LEVEL = 1              # zlib level of the pulled display PNGs (OIIO)
DEADLINE_ENV = "WENART_DEADLINE"
EXIT_INCOMPLETE = 3
# --max-bounces N (docs/milestone6.md §6.2 ctl_direct): transmission and the total never go below this, so
# a camera ray passes both faces of the window glass (review L1).
MIN_GLASS_BOUNCES = 2

# Metering and exposure (docs/milestone5.md §2.4; calibrated in pod runs 0/1).
METER_RES_DIV = 8
METER_MIN_RES = (16, 9)
METER_SAMPLES = 16
METER_BLOCKS_ACROSS = 40          # block size = width // 40 px
METER_BLOCK_COVERAGE = 0.75       # a block counts when this share of it is interior
METER_MIN_ALBEDO = 0.02           # diffuse albedo luminance below this is not metered
EXPOSURE_TARGET = 0.9
# Milestone 13: the cap (docs/milestone13.md §13.2); the Milestone 11 limits stay for the A/B's m11 variant (round 3).
EXPOSURE_LIMITS = (-2.0, 3.0)
EXPOSURE_LIMITS_M11 = (-2.0, 8.0)
# Pre-flight of pod P3 (16 Oct 2026): the floor EXPOSURE_LIMITS[0] was set under the Milestone 5-11 sun of 3 W/m²
# (lighting.SUN_STRENGTH_M11_WM2). Round 3 made the sun 1000 W/m², so a sunlit facade wants about -7.6 EV (real04
# ext_7 on the CPU: incident p50 180, wanted -7.64) and a sunlit room about -4.5 (real04 terrace); the -2 floor kept
# them 2.5-5.6 stops too bright (a washed-out, near white exterior). The floor moves down by the stops the scene's
# sun lamp adds over that reference (``sun_floor_shift``); the +3 cap and the lighting_dark finding stay as they are.
SUN_FLOOR_REFERENCE_WM2 = 3.0
EXPOSURE_STEP = 1.0 / 6.0
LIGHTING_DARK_CHECK = "lighting_dark"
LIGHTING_DARK_CRITICAL_STOPS = 2.0     # this many stops over the cap: critical, else major
WB_MODES = ("auto", "off", "fixed", "project", "kelvin")
WB_RESIDUAL = {"warm daylight": 0.35, "golden evening": 0.5, "cool daylight": 0.0, "overcast": 0.0, "night": 0.5}
# Round 3: the project white point is metered on daylight (rig hidden). Up to this many candidate cameras are
# metered (rooms whose window faces the sun first, then the other rooms with a window, name order) and the daylight
# candidate with the most incident light gives the white point: the sun, not a sky-lit window, sets the project's
# white (round-3 review, 16 Oct 2026: synthetic-01's bath, the first windowed room in name order, gets skylight only
# and metered 9,068 K under the 1000 W/m2 sun, which cast its sunlit living room orange; P1's real02 kitchen was
# sky-lit at 3 W/m2 too, M11 auto WB 7,672 K). A windowless candidate is metered only when no daylight one gave light.
WB_METER_MAX_CAMERAS = 3
# A window faces the sun when the sun's travel direction and the portal's inward axis (unit vectors) have at least
# this dot product: about 87 degrees between them, grazing sun excluded.
SUNLIT_DOT_MIN = 0.05
# Fix round after P3 (16-17 Oct 2026): the white point of a view moves from the project's daylight white toward the
# rig's white by the view's rig share (``mixed_whitepoint``); below this share (metering noise, a pendant in a sunlit
# living room) the view keeps the project white point exactly.
WB_RIG_SHARE_MIN = 0.02
WB_VIEW_RULE = ("the project's daylight colour and the rig's light colour mixed by the view's rig share (1 - "
                "daylight / all metered light), corrected with the mood's residual")
# The scene properties of the worlds (build.py / materials.exterior_world_nodes) that select_world reads.
WORLD_PROPS = ("wenart_world_exterior", "wenart_world_interior", "wenart_world_exterior_sun_disc",
               "wenart_world_exterior_disc_camera_only")
WINDOW_CLIP_LEVEL = 0.98          # a window pixel is clipped when every display channel reaches this
LUMA = (0.2126, 0.7152, 0.0722)
PLUG_EXTRA_M = 0.002              # a plug is the wall thickness + 2 x 2 mm (no coplanar faces)


# --------------------------------------------------------------------------
# Arguments (pure)
# --------------------------------------------------------------------------

class UsageError(ValueError):
    """A bad flag value: render.py prints it and exits with 2."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="render.py")
    parser.add_argument("--out", required=True)
    parser.add_argument("--cameras", default="all")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--res", default=f"{DEFAULT_RES[0]}x{DEFAULT_RES[1]}")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu"])
    parser.add_argument("--no-denoise", action="store_true")
    parser.add_argument("--exposure", default="auto", help="auto | off | <EV> (fixed stops)")
    parser.add_argument("--exposure-target", type=float, default=EXPOSURE_TARGET,
                        help="scene-linear incident light the metered median is mapped to")
    parser.add_argument("--white-balance", default="auto", help="auto | off | fixed:r,g,b (whitepoint)")
    parser.add_argument("--look-from", help="render_manifest.json whose per-camera EV and whitepoint are used")
    parser.add_argument("--hide", help="wenart ids to hide (comma separated)")
    parser.add_argument("--plug", action="store_true", help="close the wall holes of hidden doors/windows")
    parser.add_argument("--hide-sets", help="'cam:id[,id][+plug];...': one control render per set")
    parser.add_argument("--alt-look", help="also save <cam>_alt_preview.jpg with this AgX look (e.g. 'None')")
    parser.add_argument("--max-bounces", type=int,
                        help="N indirect diffuse/glossy/volume bounces (0 = direct light only); window glass "
                             "still transmits (transmission and total bounces >= 2)")
    parser.add_argument("--ev-offset", type=float, default=0.0, help="stops added to the auto/fixed/look-from EV")
    parser.add_argument("--preview-quality", type=int, help="fixed JPEG quality of the previews (no step-down)")
    return parser.parse_args(argv)


def check_control_flags(args: argparse.Namespace) -> None:
    """Range checks of the Milestone 6 control flags (``UsageError``)."""
    if args.max_bounces is not None and args.max_bounces < 0:
        raise UsageError(f"--max-bounces must be 0 or more, not {args.max_bounces}")
    if not math.isfinite(float(args.ev_offset)):
        raise UsageError(f"--ev-offset {args.ev_offset!r} is not finite")
    if args.preview_quality is not None and not 1 <= args.preview_quality <= 100:
        raise UsageError(f"--preview-quality must be 1..100, not {args.preview_quality}")
    if args.alt_look is not None and not str(args.alt_look).strip():
        raise UsageError("--alt-look needs a look name such as 'None' or 'AgX - Punchy'")


def deadline_from_env(env=None) -> tuple[float | None, str | None]:
    """``(deadline, note)``: ``WENART_DEADLINE`` as epoch seconds, or None
    (unset, or not a finite number: then ``note`` says it was ignored)."""
    text = (os.environ if env is None else env).get(DEADLINE_ENV)
    if text is None or not str(text).strip():
        return None, None
    try:
        value = float(text)
    except ValueError:
        value = float("nan")
    if not math.isfinite(value):
        return None, f"{DEADLINE_ENV}={text!r} is not a number of epoch seconds: ignored"
    return value, None


def deadline_passed(deadline: float | None, now: float | None = None) -> bool:
    """True once ``deadline`` (epoch seconds) is reached; never without a deadline."""
    return deadline is not None and (time.time() if now is None else float(now)) >= deadline


def parse_exposure(text: str) -> tuple[str, float | None]:
    """``auto`` -> ("auto", None), ``off`` -> ("off", None), a number -> ("fixed", ev)."""
    t = str(text).strip().lower()
    if t in ("auto", "off"):
        return t, None
    try:
        ev = float(t)
    except ValueError:
        raise UsageError(f"--exposure must be auto, off or a number of stops, not {text!r}") from None
    if not math.isfinite(ev):
        raise UsageError(f"--exposure {text!r} is not finite")
    return "fixed", ev


def parse_white_balance(text: str) -> tuple[str, list[float] | None]:
    """``auto`` | ``off`` | ``project`` | ``fixed:r,g,b`` | ``kelvin:K`` -> (mode, value): the whitepoint
    normalised to luminance 1 for ``fixed``, the temperature (1800-100000 K, Blender's range) as ``[K]`` for
    ``kelvin``, None otherwise. ``project`` (Milestone 13): one whitepoint for every view, see the module."""
    t = str(text).strip().lower()
    if t in ("auto", "off", "project"):
        return t, None
    if t.startswith("fixed:"):
        try:
            rgb = [float(v) for v in t[len("fixed:"):].split(",")]
        except ValueError:
            rgb = []
        if len(rgb) == 3 and all(math.isfinite(v) and v > 0 for v in rgb):
            return "fixed", normalise_whitepoint(rgb)
    if t.startswith("kelvin:"):
        try:
            kelvin = float(t[len("kelvin:"):])
        except ValueError:
            kelvin = float("nan")
        if math.isfinite(kelvin) and 1800.0 <= kelvin <= 100000.0:
            return "kelvin", [kelvin]
    raise UsageError(f"--white-balance must be auto, off, project, fixed:r,g,b with three positive numbers or "
                     f"kelvin:K (1800-100000), not {text!r}")


def exposure_limits_for(levers: dict | None = None) -> tuple[float, float]:
    """The EV limits of a run (pure; Milestone 13): ``EXPOSURE_LIMITS`` (the cap) unless the levers say the cap is
    off (``lighting.light_levers``: the ``m11``, ``sun*``, ``rig`` and ``shell`` variants of the A/B keep the
    Milestone 11 limits ``EXPOSURE_LIMITS_M11``; production and ``base`` use the cap, round 3)."""
    if levers is None:
        try:
            from wenart.blender.lighting import light_levers
            levers = light_levers()
        except Exception:  # noqa: BLE001 - the cap is the default
            levers = {"ev_cap": True}
    return tuple(EXPOSURE_LIMITS) if levers.get("ev_cap", True) else tuple(EXPOSURE_LIMITS_M11)


def sun_floor_shift(sun_wm2, reference_wm2: float = SUN_FLOOR_REFERENCE_WM2) -> float:
    """Stops the EV floor moves down for the scene's sun (pure; pre-flight of pod P3): ``log2(sun / reference)``
    for a sun lamp stronger than the 3 W/m² the floor was set under, else 0 (no sun, the M11 sun, a bad value)."""
    try:
        sun = float(sun_wm2)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(sun) or sun <= float(reference_wm2):
        return 0.0
    return round(math.log2(sun / float(reference_wm2)), 4)


def view_limits(limits, floor_shift: float = 0.0) -> tuple[float, float]:
    """The EV limits a view is metered against (pure): the run's ``limits`` with the floor moved down by
    ``floor_shift`` stops (``sun_floor_shift``); the cap (the upper limit) never moves."""
    lo, hi = limits
    return (round(float(lo) - float(floor_shift or 0.0), 4), float(hi))


def scene_sun_wm2(scene) -> float | None:
    """The W/m² of the built scene's sun lamp (bpy objects; ``lighting.build_lighting`` names it ``sun``), None when
    the scene has none."""
    ob = scene.objects.get("sun")
    if ob is None or ob.type != "LIGHT" or getattr(ob.data, "type", None) != "SUN":
        return None
    return float(ob.data.energy)


def lighting_dark_entry(camera: str, room_id, ev_raw: float | None, ev: float, limits, incident_p50=None,
                        target: float = EXPOSURE_TARGET) -> dict | None:
    """The ``lighting_dark`` finding of a view whose metered EV would pass the cap (pure; the ``Violation`` shape
    of docs/milestone13.md §13.2): None when the wanted EV is within ``limits``. Severity ``major``, or
    ``critical`` from ``LIGHTING_DARK_CRITICAL_STOPS`` over the cap."""
    if ev_raw is None or not math.isfinite(float(ev_raw)):
        return None
    hi = float(limits[1])
    over = float(ev_raw) - hi
    if over <= 1e-9:
        return None
    return {"check": LIGHTING_DARK_CHECK, "severity": "critical" if over >= LIGHTING_DARK_CRITICAL_STOPS else "major",
            "target": camera, "room_id": room_id,
            "message": (f"{camera}: the metered exposure wanted {float(ev_raw):+.2f} EV, the cap is {hi:+.2f} EV "
                        f"({over:.2f} stops over); the room is too dark for the camera (incident p50 "
                        f"{float(incident_p50):.5f} at target {target:g})" if incident_p50 is not None else
                        f"{camera}: the metered exposure wanted {float(ev_raw):+.2f} EV, the cap is {hi:+.2f} EV "
                        f"({over:.2f} stops over); the room is too dark for the camera"),
            "metrics": {"ev_wanted": round(float(ev_raw), 4), "ev_used": round(float(ev), 6), "ev_cap": hi,
                        "stops_over_cap": round(over, 4),
                        "incident_p50": None if incident_p50 is None else round(float(incident_p50), 6)}}


def wb_camera_order(cameras: list, daylight_rooms=None, sunlit_rooms=None) -> list[str]:
    """The cameras to meter the project whitepoint on, in order (pure; round 3): entries ``(name, kind)`` or
    ``(name, kind, room_id)``. Interior cameras whose room has a window facing the sun (``sunlit_rooms``) first,
    then those of the other rooms with a window (``daylight_rooms``), name order within each (the white point is
    metered on daylight, the sun first), then the other interior cameras, then the exterior ones."""
    rows = sorted(((str(r[0]), r[1], r[2] if len(r) > 2 else None) for r in cameras), key=lambda r: r[0])
    daylight = {str(r) for r in (daylight_rooms or ())}
    sunlit = {str(r) for r in (sunlit_rooms or ())} & daylight if daylight_rooms is not None else \
        {str(r) for r in (sunlit_rooms or ())}

    def rank(kind, room) -> int:
        if kind == "exterior":
            return 3
        room = None if room is None else str(room)
        return 0 if room in sunlit else 1 if room in daylight else 2

    return [n for _, n in sorted(((rank(k, room), n) for n, k, room in rows), key=lambda r: r[0])]


def project_wb_camera(cameras: list, daylight_rooms=None, sunlit_rooms=None) -> str | None:
    """The first camera to meter the project whitepoint on (pure; Milestone 13): the first of ``wb_camera_order``
    (a camera of a sunlit room, else of a room with a window, else the first interior camera, else the first
    camera), None for none."""
    order = wb_camera_order(cameras, daylight_rooms, sunlit_rooms)
    return order[0] if order else None


def sunlit_rooms_from(portals: list, sun_travel, min_dot: float = SUNLIT_DOT_MIN) -> set[str]:
    """The rooms whose window lets the sun in (pure; round-3 review): ``portals`` = ``[(room_id, inward xyz)]`` (the
    portal light's emission axis points into the room), ``sun_travel`` = the sun's light direction (xyz, from the
    sun into the scene) or None (no sun: no room). A room is sunlit when one of its portals has
    ``inward . travel >= min_dot`` (unit vectors); obstruction is not checked here, the metering is."""
    if sun_travel is None:
        return set()

    def unit(v):
        n = math.sqrt(sum(float(c) * float(c) for c in v))
        return [float(c) / n for c in v] if n > 0 else None

    travel = unit(sun_travel)
    if travel is None:
        return set()
    out = set()
    for room, inward in portals:
        u = unit(inward)
        if room and u is not None and sum(a * b for a, b in zip(u, travel)) >= float(min_dot):
            out.add(str(room))
    return out


def pick_wb_candidate(rows: list) -> dict | None:
    """The metered candidate that sets the project white point (pure; round-3 review): ``rows`` = ``[{"camera",
    "daylight", "incident_p50", "whitepoint", ...}]``. Among the rows with a whitepoint, a daylight row wins over any
    other; among those the most incident light (a sunlit room over a sky-lit one: the sun sets the white), name
    order on a tie. None when no row has a whitepoint."""
    usable = [r for r in rows if r.get("whitepoint")]
    if not usable:
        return None
    return sorted(usable, key=lambda r: (not r.get("daylight"), -float(r.get("incident_p50") or 0.0),
                                         str(r.get("camera"))))[0]


def parse_ids(text: str | None) -> list[str]:
    """``"a, b,proxy:c"`` -> ``["a", "b", "c"]`` (order kept, duplicates and ``proxy:`` dropped)."""
    out: list[str] = []
    for part in str(text or "").split(","):
        part = part.strip()
        if part.startswith("proxy:"):
            part = part[len("proxy:"):]
        if part and part not in out:
            out.append(part)
    return out


def parse_hide_sets(text: str) -> list[dict]:
    """``'cam:idA;cam:idB+plug'`` -> ``[{"camera", "ids", "plug", "dir"}]``.

    A set is ``<camera>:<id>[,<id>...][+plug]``; its renders go to
    ``hide_<ids joined by _>`` (``hide_<id>`` for the usual single id)."""
    sets = []
    for raw in str(text or "").split(";"):
        raw = raw.strip()
        if not raw:
            continue
        plug = False
        if raw.endswith("+plug"):
            plug, raw = True, raw[: -len("+plug")]
        camera, sep, ids_text = raw.partition(":")
        ids = parse_ids(ids_text)
        if not sep or not camera.strip() or not ids:
            raise UsageError(f"--hide-sets entry {raw!r} is not 'camera:id[,id][+plug]'")
        sets.append({"camera": camera.strip(), "ids": ids, "plug": plug, "dir": "hide_" + "_".join(ids)})
    if not sets:
        raise UsageError("--hide-sets lists no set")
    return sets


def group_hide_sets(sets: list[dict]) -> list[dict]:
    """Sets grouped by output folder: ``[{"dir", "ids", "plug", "cameras": [...]}]`` in first-seen order.

    One folder holds one control (the same ids, plugged or not) for any
    number of cameras; the same ids asked once with and once without
    ``+plug`` would write two different renders into one folder, so that is
    a usage error. A repeated set is listed once."""
    groups: dict[str, dict] = {}
    for s in sets:
        g = groups.setdefault(s["dir"], {"dir": s["dir"], "ids": s["ids"], "plug": s["plug"], "cameras": []})
        if g["plug"] != s["plug"]:
            raise UsageError(f"--hide-sets asks for {s['dir']} both with and without +plug")
        if s["camera"] not in g["cameras"]:
            g["cameras"].append(s["camera"])
    return list(groups.values())


# --------------------------------------------------------------------------
# Metering, exposure and white balance (pure numpy)
# --------------------------------------------------------------------------

def luminance(rgb):
    """Rec.709 luminance of an ... x 3 array (or a 3-sequence)."""
    import numpy as np

    a = np.asarray(rgb, dtype=np.float64)
    return a[..., 0] * LUMA[0] + a[..., 1] * LUMA[1] + a[..., 2] * LUMA[2]


FACADE_NZ_MAX = 0.3               # Milestone 10: an exterior view meters the facade (|normal z| below this)
FACADE_MIN_SHARE = 0.02           # ... when that leaves at least this share of the frame, else every surface


def meter_stats(light, albedo, index, depth, window_indices, blocks_across: int = METER_BLOCKS_ACROSS,
                min_coverage: float = METER_BLOCK_COVERAGE, min_albedo: float = METER_MIN_ALBEDO,
                normal_z=None) -> dict:
    """Incident-light statistics of a metering render.

    ``light`` = Diffuse Direct + Indirect (H x W x 3, colour-free), ``albedo``
    = Diffuse Color, ``index`` = object index, ``depth`` = Cycles Z. Interior
    mask: not a window index, a surface hit (depth < 1e9) and albedo
    luminance >= ``min_albedo``. Returns ``{"incident_p50": Y50 or None,
    "illuminant": [r, g, b] (sum over the mask) or None, "interior_frac",
    "blocks", "blocks_used", "block_px"}``; Y50 is the median of the block
    means of blocks that are at least ``min_coverage`` interior (block side
    ``width // blocks_across`` px). A per-pixel median at a few samples is 0
    (most paths find no light), block means are not.

    Milestone 10: ``normal_z`` (the world normal's Z, given for an exterior
    view) narrows the mask to the facades (``|z| < FACADE_NZ_MAX``: walls, not
    the ground, the roof or the sky) when they cover at least
    ``FACADE_MIN_SHARE`` of the frame; ``metered`` says ``facade`` or
    ``surfaces``."""
    import numpy as np

    light = np.nan_to_num(np.asarray(light, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    albedo = np.nan_to_num(np.asarray(albedo, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    idx = np.rint(np.nan_to_num(np.asarray(index, dtype=np.float64))).astype(np.int64)
    d = np.nan_to_num(np.asarray(depth, dtype=np.float64), nan=DEPTH_BACKGROUND, posinf=DEPTH_BACKGROUND)
    mask = (~np.isin(idx, sorted(int(v) for v in window_indices))) & (d < DEPTH_BACKGROUND) & \
           (luminance(albedo) >= min_albedo)
    metered = "surfaces"
    if normal_z is not None:
        nz = np.nan_to_num(np.asarray(normal_z, dtype=np.float64), nan=1.0)
        facade = mask & (np.abs(nz) < FACADE_NZ_MAX)
        if facade.size and float(facade.mean()) >= FACADE_MIN_SHARE:
            mask, metered = facade, "facade"
    y = luminance(light)
    h, w = mask.shape
    b = max(1, w // max(1, blocks_across))
    hh, ww = (h // b) * b, (w // b) * b
    stats = {"incident_p50": None, "illuminant": None, "interior_frac": round(float(mask.mean()), 4) if mask.size else 0.0,
             "blocks": 0, "blocks_used": 0, "block_px": b}
    if normal_z is not None:
        stats["metered"] = metered
    if hh and ww:
        shape = (hh // b, b, ww // b, b)
        m = mask[:hh, :ww]
        count = m.reshape(shape).sum(axis=(1, 3))
        ysum = np.where(m, y[:hh, :ww], 0.0).reshape(shape).sum(axis=(1, 3))
        good = count >= min_coverage * b * b
        stats["blocks"] = int(count.size)
        stats["blocks_used"] = int(good.sum())
        if good.any():
            stats["incident_p50"] = float(np.median(ysum[good] / count[good]))
    if mask.any():
        total = light[mask].sum(axis=0)
        if float(total.sum()) > 0:
            stats["illuminant"] = [float(v) for v in total]
    return stats


def exposure_from(y50: float, target: float = EXPOSURE_TARGET, limits: tuple[float, float] = EXPOSURE_LIMITS,
                  step: float = EXPOSURE_STEP) -> tuple[float, float, bool]:
    """``(ev, ev_raw, at_limit)``: ``ev_raw = log2(target / y50)``, clamped to
    ``limits`` and rounded to ``step`` stops (1/6: reruns land on the same value)."""
    lo, hi = limits
    raw = math.log2(float(target) / max(float(y50), 1e-9))
    clamped = min(hi, max(lo, raw))
    ev = round(round(clamped / step) * step, 6)
    return ev, round(raw, 4), bool(raw < lo or raw > hi)


def normalise_whitepoint(rgb) -> list[float]:
    """Scale an RGB whitepoint to luminance 1 (Blender reads it back unchanged then)."""
    lum = float(luminance(rgb))
    return [round(float(v) / lum, 6) for v in rgb]


def whitepoint_from(illuminant, residual: float) -> list[float] | None:
    """Whitepoint of the grey-card white balance: the illuminant normalised to
    G = 1, raised to ``1 - residual`` (0 = full correction, 1 = none) and
    normalised to luminance 1. None when a channel has no light."""
    ill = [float(v) for v in illuminant]
    if len(ill) != 3 or min(ill) <= 0 or not all(math.isfinite(v) for v in ill):
        return None
    g = ill[1]
    k = 1.0 - float(residual)
    return normalise_whitepoint([(v / g) ** k for v in ill])


def rig_share(all_illuminant, day_illuminant) -> float | None:
    """The share of a view's metered light that comes from the room-light rig (pure; fix round after P3, 16-17 Oct
    2026): ``1 - luminance(day) / luminance(all)``, clamped to 0..1, where ``all_illuminant`` is the metering pass's
    illuminant (``meter_stats``) with everything lit and ``day_illuminant`` the same view metered with every rig
    object hidden. None when the view has no light to meter; 1 when nothing is left without the rig."""
    if all_illuminant is None or len(all_illuminant) != 3:
        return None
    total = float(luminance([float(v) for v in all_illuminant]))
    if not math.isfinite(total) or total <= 0.0:
        return None
    day = 0.0 if day_illuminant is None or len(day_illuminant) != 3 else \
        float(luminance([float(v) for v in day_illuminant]))
    if not math.isfinite(day):
        return None
    return round(min(1.0, max(0.0, 1.0 - day / total)), 6)


def mixed_whitepoint(project_wp, rig_rgb, share, residual) -> list[float]:
    """The white point of one view (pure; fix round after P3, 16-17 Oct 2026). What: the project white point
    ``project_wp`` (metered on daylight, the anchor) moved toward the rig by the view's ``share`` of rig light. Why:
    P3 applied the 5,635 K daylight point to rooms lit only by the 2700 K rig (24 of 48 views orange). How: the
    project's daylight colour is recovered from its white point (``whitepoint_from`` is ``normalise((ill / G) ^ (1 -
    residual))``, so the illuminant is the white point to the power ``1 / (1 - residual)``), both light colours are
    scaled to luminance 1, mixed linearly by ``share`` (light adds; the share is a luminance share) and turned into a
    white point with the same residual. ``share`` 0 (or a residual of 1: no correction at all) gives the project
    white point, ``share`` 1 the rig's own white point (``whitepoint_from(rig_rgb, residual)``). ``rig_rgb`` is the
    rig's light colour (``kelvin_whitepoint`` at the rig temperature)."""
    wp = normalise_whitepoint([float(v) for v in project_wp])
    try:
        s = min(1.0, max(0.0, float(share)))
    except (TypeError, ValueError):
        return wp
    k = 1.0 - float(residual or 0.0)
    if s <= 0.0 or k <= 1e-6 or not math.isfinite(s):
        return wp
    day = normalise_whitepoint([max(v, 1e-9) ** (1.0 / k) for v in wp])
    rig = normalise_whitepoint([max(float(v), 1e-9) for v in rig_rgb])
    mixed = whitepoint_from([(1.0 - s) * d + s * r for d, r in zip(day, rig)], residual)
    return wp if mixed is None else mixed


def wb_residual(mood: str | None) -> tuple[float, str | None]:
    """``(residual, note)`` for a light mood: ``WB_RESIDUAL`` (the Milestone 5 moods), else the mood's
    ``wb_residual`` in the vocabulary's ``LIGHTING`` table (Milestone 10's moods of ``wenart/style/finishes.py``:
    blue hour, interior evening, ...; review #37); unknown moods get 0 and a note."""
    key = str(mood or "").strip().lower()
    if key in WB_RESIDUAL:
        return WB_RESIDUAL[key], None
    try:
        from wenart.style.vocabulary import LIGHTING
        value = (LIGHTING.get(key) or {}).get("wb_residual")
    except ImportError:
        value = None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value), None
    return 0.0, f"mood {mood!r} has no white-balance residual (scene built before Milestone 5?): full correction"


def window_clip_frac(display_rgb, index, window_indices, level: float = WINDOW_CLIP_LEVEL) -> float | None:
    """Share of window pixels whose display channels are all >= ``level``
    (0..1 floats, or uint8 scaled by 255); None when no window is in view."""
    import numpy as np

    rgb = np.asarray(display_rgb)
    rgb = rgb.astype(np.float64) / 255.0 if rgb.dtype == np.uint8 else rgb.astype(np.float64)
    idx = np.asarray(index)
    win = np.isin(idx, sorted(int(v) for v in window_indices))
    if not win.any():
        return None
    clipped = (rgb[..., :3] >= level).all(axis=-1) & win
    return round(float(clipped.sum()) / float(win.sum()), 4)


def bounce_settings(max_bounces: int) -> dict:
    """The Cycles bounce limits of ``--max-bounces N`` (the ``ctl_direct`` control, docs/milestone6.md
    §6.2): N diffuse, glossy and volume bounces, so the room gets no more than N bounces of indirect
    light (0 = direct light only); transmission and the total stay at ``MIN_GLASS_BOUNCES`` or more so
    a camera ray still passes both faces of the window glass and the panes show the sky. A plain
    ``max_bounces = N`` turned every pane black with N = 0 (review L1)."""
    n = int(max_bounces)
    keep = max(n, MIN_GLASS_BOUNCES)
    return {"max_bounces": keep, "diffuse_bounces": n, "glossy_bounces": n, "volume_bounces": n,
            "transmission_bounces": keep}


def camera_lens(cam) -> dict:
    """``{"lens_mm", "sensor_mm"}`` of a Blender camera object as rendered (Milestone 8: every entry of the
    render manifest records the lens its pixels were taken with; the scene manifest's plan has the same)."""
    return {"lens_mm": round(float(cam.data.lens), 4), "sensor_mm": round(float(cam.data.sensor_width), 4)}


def render_key(settings: dict) -> str:
    """First 16 hex of sha256 over the canonical JSON of the render settings."""
    blob = json.dumps(settings, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def key_settings(samples: int, resolution, denoiser, exposure_mode: str, exposure_value, target: float,
                 wb_mode: str, wb_fixed, hidden, plugged, look_from_values: dict | None = None,
                 alt_look: str | None = None, max_bounces: int | None = None, ev_offset: float = 0.0,
                 preview_quality: int | None = None, limits=None, project_whitepoint=None) -> dict:
    """What the render key covers (docs/milestone5.md §2.5, docs/milestone6.md
    §5 rows 10-11, docs/milestone7.md §6.1). With ``look_from_values``
    (``{"ev", "whitepoint"}`` of the source entry) the exposure and white
    balance are mode ``from`` with those values; ``alt_look``, ``max_bounces``,
    ``ev_offset`` and ``preview_quality`` are the Milestone 6 control flags;
    ``view_transform`` and ``look`` are the display transform of the PNG and
    the preview (Milestone 7: a change of the default look re-renders).
    Milestone 13: ``limits`` (the EV limits of the run, ``EXPOSURE_LIMITS`` when None) and the project whitepoint
    (``project_whitepoint`` for mode ``project``; the kelvin value for mode ``kelvin``) are part of the key."""
    if look_from_values is not None:
        exposure = {"mode": "from", "ev": look_from_values.get("ev"), "whitepoint": look_from_values.get("whitepoint")}
        wb = "from"
    else:
        if exposure_mode == "auto":
            exposure = {"mode": "auto", "target": float(target),
                        "limits": list(EXPOSURE_LIMITS if limits is None else limits)}
        elif exposure_mode == "fixed":
            exposure = {"mode": "fixed", "ev": float(exposure_value)}
        else:
            exposure = {"mode": "off"}
        if wb_mode == "fixed":
            wb = "fixed:" + ",".join(f"{v:.6f}" for v in wb_fixed)
        elif wb_mode == "kelvin":
            wb = f"kelvin:{float(wb_fixed[0]):g}"
        elif wb_mode == "project":
            wb = "project:" + (",".join(f"{float(v):.6f}" for v in project_whitepoint) if project_whitepoint else "none")
        else:
            wb = wb_mode
    settings = {"samples": int(samples), "resolution": [int(v) for v in resolution], "denoiser": denoiser,
                "exposure": exposure, "white_balance": wb, "passes": list(PASSES),
                "hidden": sorted(hidden), "plugged": sorted(plugged), "code": RENDER_CODE_VERSION,
                "view_transform": VIEW_TRANSFORM, "look": LOOK, "alt_look": alt_look or None, "max_bounces": None if max_bounces is None else int(max_bounces),
                "ev_offset": round(float(ev_offset or 0.0), 6),
                "preview_quality": None if preview_quality is None else int(preview_quality)}
    if max_bounces is not None:
        # The applied limits (review L1): a --max-bounces render of the old rule (max_bounces only, black
        # panes) gets another key. Absent for a normal render, so its key is unchanged.
        settings["bounces"] = bounce_settings(max_bounces)
    return settings


# --------------------------------------------------------------------------
# Window pull (numpy; docs/milestone6.md §5 row 7)
# --------------------------------------------------------------------------

def pane_mask(index, albedo, window_indices, albedo_max: float = PANE_ALBEDO_MAX):
    """bool H x W: window pixels (pass index of a window) whose Diffuse Color
    luminance is below ``albedo_max``: the glass, not the painted frame."""
    import numpy as np

    idx = np.rint(np.nan_to_num(np.asarray(index, dtype=np.float64))).astype(np.int64)
    win = np.isin(idx, sorted(int(v) for v in window_indices))
    alb = luminance(np.nan_to_num(np.asarray(albedo, dtype=np.float64)))
    return win & (alb < albedo_max)


def feather_weights(mask, px: int = PULL_FEATHER_PX):
    """float H x W in 0..1: 0 outside ``mask``; inside, k / px for a pixel at
    chessboard distance k (< px) from the nearest pixel outside it, else 1
    (``views.erode``; the image border does not count as outside). The pull
    is blended with these weights, so nothing outside the mask changes."""
    import numpy as np

    from wenart import views

    m = np.asarray(mask, dtype=bool)
    weights = np.zeros(m.shape, dtype=np.float64)
    level = m.copy()
    for _ in range(max(1, int(px))):
        weights += level
        level = views.erode(level, 1)
    return weights / float(max(1, int(px)))


def display_luminance(rgb):
    """Rec.709 luminance of display RGB (uint8 scaled by 255, or 0..1 floats)."""
    import numpy as np

    a = np.asarray(rgb)
    a = a.astype(np.float64) / 255.0 if a.dtype == np.uint8 else a.astype(np.float64)
    return luminance(a[..., :3])


def clip_share(rgb, mask, level: float = WINDOW_CLIP_LEVEL) -> float | None:
    """Share of ``mask`` pixels whose display channels are all >= ``level``; None for an empty mask."""
    import numpy as np

    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return None
    a = np.asarray(rgb)[m][:, :3]                       # the masked pixels only (fast on a 1080p view)
    a = a.astype(np.float64) / 255.0 if a.dtype == np.uint8 else a.astype(np.float64)
    clipped = (a >= level).all(axis=-1)
    return round(float(clipped.sum()) / float(m.sum()), 4)


def masked_median(rgb, mask) -> float:
    """Median display luminance of the ``mask`` pixels of ``rgb``."""
    import numpy as np

    return float(np.median(display_luminance(np.asarray(rgb)[np.asarray(mask, dtype=bool)])))


def masked_percentile(rgb, mask, q: float) -> float:
    """The ``q``-th percentile (0-100) of the display luminance of the ``mask`` pixels of ``rgb``."""
    import numpy as np

    return float(np.percentile(display_luminance(np.asarray(rgb)[np.asarray(mask, dtype=bool)]), float(q)))


def masked_saturation(rgb, mask) -> float:
    """Median HSV saturation ``(max - min) / max`` of the ``mask`` pixels of display ``rgb`` (0 for black pixels);
    the sky check of the sky pull (fix round after P3)."""
    import numpy as np

    a = np.asarray(rgb)[np.asarray(mask, dtype=bool)][:, :3]
    a = a.astype(np.float64) / 255.0 if a.dtype == np.uint8 else a.astype(np.float64)
    hi, lo = a.max(axis=-1), a.min(axis=-1)
    sat = np.where(hi > 0, (hi - lo) / np.where(hi > 0, hi, 1.0), 0.0)
    return float(np.median(sat))


def pull_reaches_target(candidate: dict, p90_max: float = PULL_P90_MAX,
                        median_target: float = PULL_MEDIAN_TARGET) -> bool:
    """The pane target of a pull (pure; fix round after P3): the pane highlights under the AgX shoulder
    (``p90 <= p90_max``) or the pane median down to ``median_target``. A candidate without ``p90`` (a record of the
    Milestone 6-13.1 rule) meets the target by its clip alone."""
    if candidate.get("p90") is None:
        return True
    return candidate["p90"] <= p90_max or candidate["median"] <= median_target


def pull_qualifies(candidate: dict, wall_median: float | None, max_clip: float = PULL_MAX_CLIP) -> bool:
    """A pull of ``candidate["k"]`` stops is enough: pane clip <= ``max_clip``, the pane target reached
    (``pull_reaches_target``; fix round after P3: the clip rule alone stopped P3's pulls at pane medians of
    0.86-0.97) and the pane median above the wall median (no wall: the clip and target rules alone)."""
    return candidate["clip"] <= max_clip and pull_reaches_target(candidate) and \
        (wall_median is None or candidate["median"] > wall_median)


def choose_pull(candidates: list[dict], wall_median: float | None,
                max_clip: float = PULL_MAX_CLIP) -> tuple[int, str]:
    """``(k, rule)`` from ``[{"k", "clip", "median", "p90"}]`` (the EV - k saves,
    ``clip``, ``median`` and ``p90`` over the pane mask): the smallest k that
    ``pull_qualifies``; else the k with the lowest clip, then the lowest p90 (the deepest pull), that keeps the pane
    median above the wall median; with no wall (``wall_median`` None) the lowest clip and p90; ``(0, ...)`` = no
    pull when no k keeps the panes brighter than the walls (or nothing was tried)."""
    cands = sorted(candidates, key=lambda c: c["k"])
    for c in cands:
        if pull_qualifies(c, wall_median, max_clip):
            return int(c["k"]), ("smallest k with pane clip <= 1 %, the pane target and panes brighter than the walls"
                                 if wall_median is not None else
                                 "smallest k with pane clip <= 1 % and the pane target (no wall in view)")
    bright = [c for c in cands if wall_median is None or c["median"] > wall_median]
    if bright:
        best = min(bright, key=lambda c: (c["clip"], c["p90"] if c.get("p90") is not None else 0.0, c["k"]))
        return int(best["k"]), ("lowest pane clip and highlights that keep the panes brighter than the walls"
                                if wall_median is not None else "lowest pane clip and highlights (no wall in view)")
    return 0, "no k keeps the panes brighter than the walls: no pull"


def sky_mask(depth):
    """bool H x W: the world-background pixels (no surface hit in the Cycles depth pass: not finite or at
    ``DEPTH_BACKGROUND``), the sky of a view under the exterior world (fix round after P3)."""
    import numpy as np

    d = np.asarray(depth, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        return ~(np.isfinite(d) & (d < DEPTH_BACKGROUND))


def sky_pull_qualifies(candidate: dict, median_max: float = SKY_PULL_MEDIAN_MAX,
                       sat_min: float = SKY_PULL_SAT_MIN) -> bool:
    """A sky reads as sky (pure): median display luminance at most ``median_max`` (under the AgX shoulder) and median
    saturation at least ``sat_min``."""
    return candidate["median"] <= median_max and candidate["saturation"] >= sat_min


def choose_sky_pull(before: dict, candidates: list[dict]) -> tuple[int, str]:
    """``(k, rule)`` of the sky pull (pure; fix round after P3): ``before`` = ``{"median", "saturation"}`` of the
    sky as rendered, ``candidates`` = ``[{"k", "median", "saturation"}]`` of the EV - k saves. 0 when the sky already
    qualifies (``sky_pull_qualifies``); else the smallest qualifying k; else 0 (no k gives a blue sky under the
    shoulder: a near-white sky beside the sun stays as rendered rather than turning grey)."""
    if sky_pull_qualifies(before):
        return 0, "the sky is under the shoulder and saturated as rendered: no pull"
    for c in sorted(candidates, key=lambda c: c["k"]):
        if sky_pull_qualifies(c):
            return int(c["k"]), (f"smallest k with the sky median <= {SKY_PULL_MEDIAN_MAX:g} and saturation >= "
                                 f"{SKY_PULL_SAT_MIN:g}")
    return 0, "no k brings the sky under the shoulder with saturation: no pull"


def blend_pull(main, pulled, weights):
    """uint8 H x W x 3: ``main * (1 - w) + pulled * w`` rounded; exactly ``main`` where w = 0."""
    import numpy as np

    w = np.asarray(weights, dtype=np.float64)
    out = np.array(np.asarray(main)[..., :3], dtype=np.uint8, copy=True)
    sel = w > 0                                          # only the masked pixels are computed
    if sel.any():
        ws = w[sel][:, None]
        a = out[sel].astype(np.float64)
        b = np.asarray(pulled)[..., :3][sel].astype(np.float64)
        out[sel] = np.clip(np.rint(a * (1.0 - ws) + b * ws), 0, 255).astype(np.uint8)
    return out


# --------------------------------------------------------------------------
# Pass products (numpy; the encoders of wenart.views)
# --------------------------------------------------------------------------

def find_channel(channels: dict, *suffixes: str):
    for n, values in channels.items():
        if n.endswith(suffixes):
            return values
    return None


def find_rgb(channels: dict, *names: str):
    """H x W x 3 of the first pass in ``names`` that has R, G, B (or X, Y, Z) channels."""
    import numpy as np

    for name in names:
        for comps in (("R", "G", "B"), ("X", "Y", "Z")):
            parts = [find_channel(channels, f"{name}.{c}") for c in comps]
            if all(p is not None for p in parts):
                return np.stack(parts, axis=-1)
    return None


def pass_products(channels: dict) -> dict:
    """Statistics and helper maps from the EXR channels of one camera:
    ``depth`` stats ``{min, max, mean, coverage}`` (None without a depth
    pass), ``index_values``, ``index_stats`` (``{str(index): {pixels, box}}``)
    and the arrays ``index`` (uint16), ``depth_mm`` (uint16), ``normal``
    (uint8 RGB) and ``depth_legacy`` (uint16, per-view min..max, near = dark)."""
    import numpy as np

    from wenart import views

    out: dict = {"depth": None, "index_values": [], "index_stats": {}, "index": None, "depth_mm": None,
                 "normal": None, "depth_legacy": None}
    depth = find_channel(channels, "Depth.Z")
    # Blender 5.2 names the pass "Object Index.X"; older builds wrote "IndexOB.X".
    index = find_channel(channels, "Object Index.X", "IndexOB.X")
    normal = find_rgb(channels, "Normal")
    valid = None
    if depth is not None:
        valid = np.isfinite(depth) & (depth < DEPTH_BACKGROUND)
        if valid.any():
            d = depth[valid]
            out["depth"] = {"min": float(d.min()), "max": float(d.max()), "mean": float(d.mean()),
                            "coverage": float(valid.mean())}
            lo, hi = out["depth"]["min"], max(out["depth"]["max"], out["depth"]["min"] + 1e-6)
            legacy = np.full(depth.shape, 65535, dtype=np.uint16)
            legacy[valid] = np.clip((d - lo) / (hi - lo) * 65535.0, 0, 65535).astype(np.uint16)
            out["depth_legacy"] = legacy
        else:
            out["depth"] = {"min": 0.0, "max": 0.0, "mean": 0.0, "coverage": 0.0}
        out["depth_mm"] = views.encode_depth_mm(depth)
    if index is not None:
        idx16 = views.encode_index(index)
        out["index"] = idx16
        stats = views.compute_index_stats(idx16)
        out["index_values"] = sorted(stats)
        out["index_stats"] = {str(k): v for k, v in sorted(stats.items())}
    if normal is not None:
        out["normal"] = views.encode_normal(normal, valid)
    return out


# --------------------------------------------------------------------------
# Plug geometry (pure)
# --------------------------------------------------------------------------

def plug_box(wall: dict, points, extra: float = PLUG_EXTRA_M) -> tuple[list, list, dict]:
    """Box that closes the hole of a hidden door/window in ``wall``.

    ``wall`` is the scene-manifest wall entry (``start``, ``end``,
    ``thickness``); ``points`` are the world vertices of the hidden opening
    objects (frame, leaf, glass). The box spans the points along the wall
    axis and in height, and the wall thickness + 2 x ``extra`` across,
    centred on the wall centre line (the hole was cut there). Returns
    ``(verts, faces, info)`` with outward normals (``geom2d.box``)."""
    from wenart.blender import geom2d

    (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 1e-9:
        raise ValueError(f"wall {wall.get('wenart_id')} has no length")
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    pts = [(float(p[0]), float(p[1]), float(p[2])) for p in points]
    if not pts:
        raise ValueError("no vertices to plug")
    along = [(x - x0) * ux + (y - y0) * uy for x, y, _ in pts]
    zs = [z for _, _, z in pts]
    a0, a1, z0, z1 = min(along), max(along), min(zs), max(zs)
    am = (a0 + a1) / 2.0
    cx, cy = x0 + ux * am, y0 + uy * am
    thickness = float(wall["thickness"]) + 2.0 * extra
    angle = math.degrees(math.atan2(uy, ux))
    verts, faces = geom2d.box((cx, cy, (z0 + z1) / 2.0), (a1 - a0, thickness, z1 - z0), angle)
    info = {"along_m": [round(a0, 4), round(a1, 4)], "z_m": [round(z0, 4), round(z1, 4)],
            "thickness_m": round(thickness, 4), "center": [round(cx, 4), round(cy, 4), round((z0 + z1) / 2.0, 4)]}
    return verts, faces, info


PLUG_PROBE_M = 0.05               # probe points this far beyond the plug's edges, on the wall face


def _face_side(normal, left) -> str:
    """``left`` / ``right`` of the wall axis for a face across the wall, else ``ends`` (top,
    bottom, jamb and end faces; the limits of shell._assign_wall_face_materials)."""
    n = [float(c) for c in normal]
    size = math.sqrt(sum(c * c for c in n)) or 1.0
    across = (n[0] * left[0] + n[1] * left[1]) / size
    if abs(n[2] / size) > 0.5 or abs(across) < 0.5:
        return "ends"
    return "left" if across > 0 else "right"


def plug_face_sides(wall: dict, verts, faces) -> list[str]:
    """``left`` / ``right`` / ``ends`` per plug face (left of the wall's start -> end axis)."""
    from wenart import geometry as G
    from wenart.blender import geom2d

    left = G.unit_normal_left(wall["start"][:2], wall["end"][:2])
    return [_face_side(geom2d.face_normal(verts, f), left) for f in faces]


def plug_face_slots(wall: dict, verts, faces, wall_faces) -> list[int]:
    """Material slot per plug face, copied from the wall faces around the hole.

    The plug carries the wall's slot list (``[wall, exterior, wet]``,
    shell.py); it must read as the wall around it. ``wall_faces`` are the
    wall mesh's faces in world space as ``(normal, vertices, material_index)``:
    their slots are the build's classification (``shell._assign_wall_face_materials``:
    room-side faces of a bathroom / wc / kitchen use the wet slot, outer faces of
    an exterior wall the exterior slot). Top, bottom and end faces of the plug
    take slot 0, as the wall's top, bottom and jamb faces do. A face across the
    wall takes the slot of the wall face on the same side that holds a point
    ``PLUG_PROBE_M`` beyond the plug's edge (above, below, before, after along
    the wall; the most frequent slot, ties to the first); without such a face
    the slot of the nearest face of that side, else 0."""
    from collections import Counter

    from wenart import geometry as G

    (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 1e-9:
        raise ValueError(f"wall {wall.get('wenart_id')} has no length")
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    left = G.unit_normal_left((x0, y0), (x1, y1))

    def plane(p):                                      # (along the wall, height)
        return ((p[0] - x0) * ux + (p[1] - y0) * uy, p[2])

    def centre(poly):
        return (sum(a for a, _ in poly) / len(poly), sum(z for _, z in poly) / len(poly))

    by_side: dict[str, list] = {"left": [], "right": [], "ends": []}
    for normal, face_verts, slot in wall_faces:
        by_side[_face_side(normal, left)].append(([plane(v) for v in face_verts], int(slot)))

    slots = []
    for face, side in zip(faces, plug_face_sides(wall, verts, faces)):
        if side == "ends":
            slots.append(0)
            continue
        polys = by_side[side]
        pts = [plane(verts[i]) for i in face]
        a0, a1 = min(a for a, _ in pts), max(a for a, _ in pts)
        z0, z1 = min(z for _, z in pts), max(z for _, z in pts)
        am, zm, d = (a0 + a1) / 2.0, (z0 + z1) / 2.0, PLUG_PROBE_M
        probes = [(am, z1 + d), (am, z0 - d), (a0 - d, zm), (a1 + d, zm)]
        hits = [next((slot for poly, slot in polys if G.point_in_polygon(p, poly)), None) for p in probes]
        hits = [h for h in hits if h is not None]
        if hits:
            slots.append(Counter(hits).most_common(1)[0][0])
        elif polys:
            slots.append(min(polys, key=lambda ps: math.dist(centre(ps[0]), (am, zm)))[1])
        else:
            slots.append(0)
    return slots


# --------------------------------------------------------------------------
# Manifest bookkeeping (pure)
# --------------------------------------------------------------------------

def scene_fingerprint(blend_path: str) -> str | None:
    """sha256 of the scene file; None when the scene is unsaved (no file to fingerprint)."""
    if not blend_path or not Path(blend_path).is_file():
        return None
    digest = hashlib.sha256()
    with open(blend_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_previous(manifest_path: Path) -> dict[str, dict]:
    """Entries of the last render manifest keyed by camera; empty when absent or unreadable."""
    if not manifest_path.exists():
        return {}
    try:
        return {r["camera"]: r for r in json.loads(manifest_path.read_text(encoding="utf-8")).get("renders", [])}
    except (ValueError, KeyError, TypeError):
        return {}


def load_project_whitepoint(manifest_path: Path) -> dict | None:
    """The ``white_balance_project`` record of the last render manifest (Milestone 13: the locked whitepoint of a
    re-render), None when absent or unusable."""
    if not manifest_path.exists():
        return None
    try:
        rec = json.loads(manifest_path.read_text(encoding="utf-8")).get("white_balance_project")
    except (ValueError, AttributeError):
        return None
    wp = (rec or {}).get("whitepoint") if isinstance(rec, dict) else None
    if not isinstance(wp, list) or len(wp) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in wp):
        return None
    return dict(rec)


def load_dropped(manifest_path: Path) -> dict[str, dict]:
    """``dropped_stale`` items of the last render manifest keyed by camera; empty when absent or unreadable."""
    if not manifest_path.exists():
        return {}
    try:
        items = json.loads(manifest_path.read_text(encoding="utf-8")).get("dropped_stale") or []
        return {d["camera"]: d for d in items if isinstance(d, dict) and d.get("camera")}
    except (ValueError, KeyError, TypeError, AttributeError):
        return {}


def stale_item(camera: str, entry: dict, reason: str) -> dict:
    """A ``dropped_stale`` item (``files`` is filled in when the manifest is written)."""
    return {"camera": camera, "reason": reason, "scene_sha256": entry.get("scene_sha256"),
            "render_key": entry.get("render_key"), "files": []}


def reuse_reason(cam_name: str, previous: dict | None, fingerprint: str | None, files: list[Path],
                 key: str | None = None) -> str | None:
    """Why a camera must be rendered again, or None when its files can be reused."""
    missing = [p.name for p in files if not p.exists()]
    if missing:
        return f"missing {', '.join(missing)}"
    if previous is None:
        return "no manifest entry for its files (run cut before the manifest was written?)"
    if fingerprint is None:
        return "scene file not fingerprinted"
    if previous.get("scene_sha256") != fingerprint:
        return "scene.blend changed since the render (stale files)"
    if key is not None:
        if not previous.get("render_key"):
            return "no render_key (rendered before Milestone 5: stale)"
        if previous["render_key"] != key:
            return f"render settings changed (render_key {previous['render_key']} -> {key})"
    return None


def relative_posix(path: Path | str, base: Path | str) -> str:
    """``path`` relative to the folder ``base`` in POSIX form (M5 JSON paths, §1.1)."""
    return Path(os.path.relpath(os.path.abspath(path), os.path.abspath(base))).as_posix()


def look_from_values(entry: dict | None) -> dict | None:
    """``{"ev", "whitepoint"}`` of a source manifest entry, or None when it has no usable exposure record."""
    exposure = (entry or {}).get("exposure") or {}
    ev = exposure.get("ev")
    if not isinstance(ev, (int, float)) or not math.isfinite(float(ev)):
        return None
    wp = exposure.get("whitepoint")
    if wp is not None and (len(wp) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in wp)):
        return None
    return {"ev": float(ev), "whitepoint": [float(v) for v in wp] if wp is not None else None}


# --------------------------------------------------------------------------
# Blender side
# --------------------------------------------------------------------------

def open_air(room_type) -> bool:
    """Whether a room type is open to the sky (pure; fix round after P3, 16-17 Oct 2026): the types of
    ``shell.OUTDOOR_ROOM_TYPES`` (``balcony``: the TERAS / BALKON rooms of real02, real04 and the synthetic
    projects). A camera of such a room renders under the exterior world (``world_for``)."""
    from wenart.blender.shell import OUTDOOR_ROOM_TYPES

    return bool(room_type) and str(room_type) in OUTDOOR_ROOM_TYPES


def world_for(scene_props: dict, camera_kind: str | None, room_type: str | None = None) -> str | None:
    """The world name a camera renders under (pure; Milestone 11, docs/milestone11.md §1.1 E13): an exterior camera
    the build's exterior world (``wenart_world_exterior``: a physical sky matched to the sun lamp), any other the
    interior one (``wenart_world_interior``: the style's HDRI); None when the scene has no such property (a scene
    built before Milestone 11 keeps its one world). Fix round after P3 (16-17 Oct 2026): a camera of an open-air room
    (``open_air(room_type)``: a roof terrace) is outdoors too and gets the exterior world (P3: real04's terrace views
    under the interior HDRI, 5.2 stops under the sun, had a black sky at the sunlit EV -7.5); without an exterior
    world in the scene it keeps the interior one."""
    outdoors = camera_kind == "exterior" or open_air(room_type)
    name = scene_props.get("wenart_world_exterior") if outdoors else None
    if not name:
        name = None if camera_kind == "exterior" else scene_props.get("wenart_world_interior")
    return str(name) if name else None


def under_exterior_sky(scene_props: dict, camera_kind: str | None, room_type: str | None = None) -> bool:
    """Whether a camera renders under the exterior world (pure; fix round after P3): its sky gets the sky pull and
    its white point stays the project's."""
    name = scene_props.get("wenart_world_exterior")
    return bool(name) and world_for(scene_props, camera_kind, room_type) == str(name)


def sun_hidden_for(scene_props: dict, camera_kind: str | None, room_type: str | None = None) -> bool:
    """Whether the sun lamp is hidden for a camera (pure; Milestone 13): under the exterior world whose sky carries
    the sun disc for every ray (``wenart_world_exterior_sun_disc``, the P1 world) the disc is the one direct sun.
    Round 3: with ``wenart_world_exterior_disc_camera_only`` the disc is in the image only and the lamp stays (it
    is the one direct sun outdoors). Fix round after P3: a camera of an open-air room follows the exterior rule."""
    return under_exterior_sky(scene_props, camera_kind, room_type) \
        and bool(scene_props.get("wenart_world_exterior_sun_disc")) \
        and not bool(scene_props.get("wenart_world_exterior_disc_camera_only"))


def room_types_from_manifest(manifest: dict | None) -> dict[str, str]:
    """``{room id: room type}`` from a scene manifest (pure; fix round after P3): the room floors (kind ``floor``,
    ``wenart_id`` = the room id, no ``room_id`` of their own; door thresholds carry the room they open into and are
    left out) record the room's ``room_type``. The fallback of ``camera_room_type`` for scenes whose cameras carry no
    ``wenart_room_type``."""
    out: dict[str, str] = {}
    for o in (manifest or {}).get("objects") or []:
        if isinstance(o, dict) and o.get("kind") == "floor" and o.get("room_type") and o.get("wenart_id") \
                and not o.get("room_id"):
            out.setdefault(str(o["wenart_id"]), str(o["room_type"]))
    return out


def camera_room_type(prop_room_type, room_id, manifest_types: dict | None = None) -> str | None:
    """The room type of a camera (pure; fix round after P3): its ``wenart_room_type`` property (set by
    ``cameras.create_cameras``), else the scene manifest's type of its room (``room_types_from_manifest``), else
    None (an exterior camera, or a scene built before the property and without room floors)."""
    if prop_room_type:
        return str(prop_room_type)
    if room_id and manifest_types:
        return manifest_types.get(str(room_id))
    return None


def select_world(scene, cam, room_type: str | None = None) -> str | None:
    """Switch ``scene.world`` to the world of ``cam`` (``world_for``); returns the world's name. Milestone 13: the
    sun lamp (``wenart_id`` ``sun``) is hidden under the exterior world with a sun disc for every ray
    (``sun_hidden_for``) and shown again for every other camera (round 3: always shown under the camera-only disc).
    Fix round after P3: ``room_type`` (``camera_room_type``) puts the camera of an open-air room under the exterior
    world; the project white-point metering passes none, so those candidates are metered under the interior world as
    on P3 (5,635 K on real04: under the 5.2 stops brighter sky the half-shaded terrace would read blue and warm
    every room view)."""
    import bpy

    props = {k: scene.get(k) for k in WORLD_PROPS}
    want = world_for(props, cam.get("wenart_camera_kind"), room_type)
    world = bpy.data.worlds.get(want) if want else None
    if world is not None:
        scene.world = world
    hide = sun_hidden_for(props, cam.get("wenart_camera_kind"), room_type)
    for ob in scene.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN" and ob.get("wenart_id") == "sun":
            ob.hide_render = hide
    return scene.world.name if scene.world is not None else None


def rig_objects(scene) -> list:
    """The light-rig objects of the scene (round 3): the emissive shades and their lights, tagged ``wenart_rig`` by
    ``lighting.build_room_rig``; hidden while the project white point is metered on daylight."""
    return [ob for ob in scene.objects if ob.get("wenart_rig")]


def window_portals(scene) -> list:
    """``[(room_id, inward xyz)]`` of the window portals (round 3): ``lighting.build_portals`` tags every portal
    light with the room it faces (``wenart_room``) and points its emission axis (local -Z) into that room."""
    from mathutils import Vector

    out = []
    for ob in scene.objects:
        if ob.type == "LIGHT" and ob.data.type == "AREA" and ob.get("wenart_room") and ob.data.cycles.is_portal:
            inward = ob.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))
            out.append((str(ob["wenart_room"]), tuple(float(c) for c in inward)))
    return out


def daylight_rooms(scene) -> set[str]:
    """The rooms with a window portal (round 3): these rooms get daylight; the project white point is metered in
    one of them."""
    return {room for room, _ in window_portals(scene)}


def sun_travel(scene) -> tuple | None:
    """The sun lamp's light direction (its local -Z in the world, xyz), None without a shown sun lamp of strength
    > 0 (``wenart_id`` ``sun``, ``lighting.build_lighting``)."""
    from mathutils import Vector

    for ob in scene.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN" and ob.get("wenart_id") == "sun" \
                and float(ob.data.energy) > 0.0:
            return tuple(float(c) for c in ob.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0)))
    return None


def sunlit_rooms(scene) -> set[str]:
    """The rooms with a window facing the sun (round-3 review, ``sunlit_rooms_from``): metered first for the
    project white point."""
    return sunlit_rooms_from(window_portals(scene), sun_travel(scene))


def hide_objects(objects) -> list:
    """Hide ``objects`` from rendering; returns ``[(object, previous hide_render)]`` for ``unhide_objects``."""
    saved = []
    for ob in objects:
        saved.append((ob, bool(ob.hide_render)))
        ob.hide_render = True
    return saved


def unhide_objects(saved) -> None:
    """Undo ``hide_objects``."""
    for ob, previous in saved:
        ob.hide_render = previous


def whitepoint_kelvin(scene, whitepoint) -> tuple[float, float]:
    """``(kelvin, tint)`` of a whitepoint through Blender's own white balance (``ColorManagedViewSettings
    .white_balance_whitepoint`` -> ``white_balance_temperature`` / ``white_balance_tint``); the view settings are
    restored."""
    vs = scene.view_settings
    saved = (vs.use_white_balance, tuple(vs.white_balance_whitepoint))
    try:
        vs.use_white_balance = True
        vs.white_balance_whitepoint = tuple(float(v) for v in whitepoint)
        return round(float(vs.white_balance_temperature), 1), round(float(vs.white_balance_tint), 2)
    finally:
        vs.use_white_balance, vs.white_balance_whitepoint = saved


def kelvin_whitepoint(scene, kelvin: float, tint: float = 0.0) -> list[float]:
    """The white point (luminance 1) Blender's white balance uses for ``kelvin`` / ``tint``
    (``white_balance_temperature`` / ``white_balance_tint`` -> ``white_balance_whitepoint``); the view settings are
    restored. Fix round after P3: at tint 0 it is the colour of a lamp at that temperature (bpy 5.2.2, 16 Oct 2026: a
    white plane under a 2700 K point light, Diffuse Direct G-normalised (2.4082, 1, 0.2386); the white point at
    2700 K, tint 0: (2.4086, 1, 0.2393)), so ``mixed_whitepoint`` takes it as the rig's light colour."""
    vs = scene.view_settings
    saved = (vs.use_white_balance, tuple(vs.white_balance_whitepoint))
    try:
        vs.use_white_balance = True
        vs.white_balance_temperature = float(kelvin)
        vs.white_balance_tint = float(tint)
        return normalise_whitepoint([float(v) for v in vs.white_balance_whitepoint])
    finally:
        vs.use_white_balance, vs.white_balance_whitepoint = saved


def rig_temperature(scene) -> float | None:
    """The colour temperature of the scene's room-light rig (the rig lights carry ``use_temperature``,
    ``lighting.build_room_rig``; ``lighting.rig_temperature_k`` gives every fixture of a build the same one), None
    without a shown rig light with a temperature."""
    for ob in rig_objects(scene):
        if ob.type == "LIGHT" and not ob.hide_render and getattr(ob.data, "use_temperature", False):
            return round(float(ob.data.temperature), 1)
    return None


def previous_whitepoint_usable(previous: dict | None) -> bool:
    """Whether a previous manifest's ``white_balance_project`` record is kept for this render (pure; round 3): it
    needs a whitepoint and must have been metered on daylight (``daylight_only``) or set from ``kelvin:<K>``; a
    record metered with the rig lit (the P1 runs) is metered again."""
    if not previous or not isinstance(previous.get("whitepoint"), list) or len(previous["whitepoint"]) != 3:
        return False
    return bool(previous.get("daylight_only")) or str(previous.get("source") or "").startswith("kelvin:")


def configure_device(scene, requested: str = "auto") -> str:
    """Cycles device: OPTIX, then CUDA, then CPU. Returns the one in use."""
    import bpy

    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    device = "CPU"
    if requested != "cpu":
        for dev_type in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == dev_type]
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == dev_type
                    scene.cycles.device = "GPU"
                    device = dev_type
                    break
            except Exception as exc:  # noqa: BLE001 - no such backend on this machine
                print(f"{dev_type} not usable: {exc}")
    if device == "CPU":
        scene.cycles.device = "CPU"
    print(f"DEVICE={device}")
    return device


def configure_render(scene, samples: int, res: tuple[int, int], device: str, denoise: bool,
                     max_bounces: int | None = None) -> str | None:
    """Samples, resolution, denoiser, the pass toggles (``PASSES``: combined,
    depth, normal, object index and, since Milestone 6, Diffuse Color for the
    window pull) and, for a control render, the bounce limits of
    ``max_bounces`` (``bounce_settings``). Returns the denoiser name."""
    scene.cycles.samples = samples
    if max_bounces is not None:
        for name, value in bounce_settings(max_bounces).items():
            setattr(scene.cycles, name, value)
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = denoise
    denoiser = None
    if denoise:
        try:
            scene.cycles.denoiser = "OPENIMAGEDENOISE"
            scene.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
            scene.cycles.denoising_use_gpu = device != "CPU"
            denoiser = "OPENIMAGEDENOISE"
        except TypeError:
            denoiser = scene.cycles.denoiser
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    scene.render.film_transparent = False
    vl = bpy_view_layer(scene)
    vl.use_pass_combined = True
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_object_index = True
    vl.use_pass_diffuse_color = True          # the pane mask of the window pull (Milestone 6)
    _light_passes(scene, False)
    # Data passes (depth, normal, index) are written at the first surface whose
    # alpha reaches this threshold: thin glass (alpha = Fresnel) is seen through.
    vl.pass_alpha_threshold = 0.5
    return denoiser


def bpy_view_layer(scene):
    return scene.view_layers[0]


def _light_passes(scene, on: bool) -> None:
    """Diffuse Direct / Indirect: on only for the metering pre-render (Diffuse Color stays on)."""
    vl = bpy_view_layer(scene)
    vl.use_pass_diffuse_direct = on
    vl.use_pass_diffuse_indirect = on
    vl.use_pass_diffuse_color = True


def set_output(scene, fmt: str, quality: int = 90) -> None:
    """Output format. Blender 5.x selects multilayer EXR through
    ``media_type = 'MULTI_LAYER_IMAGE'`` (``file_format`` then only offers
    OPEN_EXR_MULTILAYER); plain images need ``media_type = 'IMAGE'``."""
    s = scene.render.image_settings
    if fmt == "OPEN_EXR_MULTILAYER":
        s.media_type = "MULTI_LAYER_IMAGE"
        s.file_format = fmt
        s.color_mode = "RGBA"
        s.color_depth = "16"
        s.exr_codec = "ZIP"
        # Single-part file: every reader (and OIIO's subimage 0) sees all channels.
        s.use_exr_interleave = True
        return
    s.media_type = "IMAGE"
    s.file_format = fmt
    if fmt == "PNG":
        s.color_mode = "RGB"
        s.color_depth = "8"
        s.compression = 15
    elif fmt == "JPEG":
        s.color_mode = "RGB"
        s.quality = quality


def save_preview(scene, result, path: Path, quality: int | None = None) -> int:
    """JPEG preview of the Render Result: under PREVIEW_MAX_BYTES (quality
    steps down until it fits), or at the one fixed ``quality``
    (``--preview-quality``, no step-down). Returns the file size."""
    size = 0
    for q in ([int(quality)] if quality else PREVIEW_QUALITIES):
        set_output(scene, "JPEG", q)
        result.save_render(str(path), scene=scene)
        size = path.stat().st_size
        if quality or size <= PREVIEW_MAX_BYTES:
            break
    return size


def encode_preview(scene, png: Path, path: Path, quality: int | None = None) -> int:
    """JPEG preview of a display PNG (a pulled image) with Blender's own JPEG
    writer and the qualities of ``save_preview``: the PNG is loaded as an
    image and saved with ``Image.save_render`` under the Standard view
    transform (no look, exposure 0, gamma 1, no white balance, no dither),
    which leaves its sRGB bytes as they are. Checked on Blender 5.2.2: the
    decoded JPEG equals a direct ``save_render`` of the same pixels at the
    same quality (max difference 0); ``Image.save`` ignores ``quality``.
    The scene's settings are restored. Returns the file size."""
    import bpy

    vs, r = scene.view_settings, scene.render
    saved = (vs.view_transform, vs.look, vs.exposure, vs.gamma, vs.use_white_balance, r.dither_intensity)
    image = bpy.data.images.load(str(png), check_existing=False)
    size = 0
    try:
        vs.view_transform = "Standard"
        vs.look, vs.exposure, vs.gamma, vs.use_white_balance = "None", 0.0, 1.0, False
        r.dither_intensity = 0.0
        for q in ([int(quality)] if quality else PREVIEW_QUALITIES):
            set_output(scene, "JPEG", q)
            image.save_render(str(path), scene=scene, quality=q)
            size = path.stat().st_size
            if quality or size <= PREVIEW_MAX_BYTES:
                break
    finally:
        bpy.data.images.remove(image)
        (vs.view_transform, vs.look, vs.exposure, vs.gamma, vs.use_white_balance, r.dither_intensity) = saved
    return size


def save_display(scene, result, path: Path, ev: float, look: str = LOOK):
    """The Render Result saved as a display PNG at ``ev`` with ``look`` (the
    view transform is applied at save time) and read back (uint8 H x W x 3);
    the file is removed again. The scene's exposure and look are restored."""
    vs = scene.view_settings
    saved = (vs.exposure, vs.look)
    try:
        vs.exposure = float(ev)
        vs.look = look
        set_output(scene, "PNG")
        scene.render.image_settings.compression = 0          # a temporary file: no zlib (same pixels, faster)
        result.save_render(str(path), scene=scene)
        return read_display_png(path)
    finally:
        vs.exposure, vs.look = saved
        Path(path).unlink(missing_ok=True)


def read_exr(exr_path: Path) -> dict:
    """``{channel name: H x W float array}`` of every subimage of an EXR (Blender's OpenImageIO)."""
    import numpy as np
    import OpenImageIO as oiio

    inp = oiio.ImageInput.open(str(exr_path))
    if inp is None:
        raise RuntimeError(f"cannot read {exr_path}: {oiio.geterror()}")
    channels: dict = {}
    part = 0
    # A multi-part EXR keeps each layer in its own part; a single-part file has them all in part 0.
    while inp.seek_subimage(part, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        data = inp.read_image("float")
        if data is not None:
            data = np.asarray(data).reshape(spec.height, spec.width, len(names))
            for i, n in enumerate(names):
                channels[n] = data[:, :, i]
        part += 1
    inp.close()
    return channels


def read_display_png(path: Path):
    """uint8 H x W x 3 of a PNG (Blender's OpenImageIO; Pillow is not in Blender's Python)."""
    import numpy as np
    import OpenImageIO as oiio

    buf = oiio.ImageBuf(str(path))
    px = buf.get_pixels(oiio.UINT8)
    if px is None:
        raise RuntimeError(f"cannot read {path}: {buf.geterror()}")
    return np.asarray(px)[:, :, :3]


def write_png(path: Path, array, compression: int | None = None) -> None:
    """Write a uint16 H x W (grey) or uint8 H x W x 3 (RGB) array as PNG with OpenImageIO.

    ``compression`` = zlib level 0-9 (``png:compressionLevel``; OIIO's
    default otherwise): the pulled display images use 1 (3x faster at 1080p,
    the same pixels). Raises RuntimeError when the file cannot be written:
    these maps are part of a finished render, a missing one must not pass
    unnoticed."""
    import numpy as np
    import OpenImageIO as oiio

    a = np.ascontiguousarray(array)
    if a.ndim == 2:
        a = a.reshape(a.shape[0], a.shape[1], 1)
    h, w, c = a.shape
    fmt = {np.dtype(np.uint16): "uint16", np.dtype(np.uint8): "uint8"}.get(a.dtype)
    if fmt is None:
        raise ValueError(f"write_png: uint8 or uint16 expected, got {a.dtype}")
    out = oiio.ImageOutput.create(str(path))
    if out is None:
        raise RuntimeError(f"cannot create {path}: {oiio.geterror()}")
    spec = oiio.ImageSpec(w, h, c, fmt)
    if compression is not None:
        spec.attribute("png:compressionLevel", int(compression))
    # OIIO wants (height, width, channels); a 2-D array is read with the wrong stride.
    if not out.open(str(path), spec) or not out.write_image(a):
        err = out.geterror()
        out.close()
        raise RuntimeError(f"cannot write {path}: {err}")
    out.close()


def vram_used_mib() -> int | None:
    """The GPU memory in use (MiB, ``nvidia-smi --query-gpu=memory.used``), None without nvidia-smi or on the CPU.
    Milestone 13: read after every view's render (Cycles keeps the scene resident with persistent data, so the
    value after a view is close to its peak); the lever A/B job samples nvidia-smi for the peak as well."""
    import subprocess

    try:
        proc = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    values = [int(float(line.strip())) for line in proc.stdout.splitlines() if line.strip().replace(".", "").isdigit()]
    return max(values) if values else None


def pass_index_table(scene) -> dict[str, int]:
    """``{wenart_id: pass_index}`` of every object with an index, the table of the scene
    manifest (a door's frame and leaf share the id and the index, so one key each)."""
    table: dict[str, int] = {}
    for o in scene.objects:
        if o.pass_index > 0:
            key = o.get("wenart_id") or o.name
            table[key] = int(o.pass_index)
    return table


def window_indices(scene) -> set[int]:
    """Pass indices of the window objects (frame and glass), left out of the metering."""
    return {int(o.pass_index) for o in scene.objects if o.pass_index > 0 and o.get("wenart_kind") == "window"}


def indexed_objects(scene) -> dict[str, list]:
    """``{wenart id without proxy:: [objects with a pass index]}`` (what --hide can hide)."""
    out: dict[str, list] = {}
    for o in scene.objects:
        if o.pass_index > 0 and o.get("wenart_id"):
            key = str(o["wenart_id"])
            if key.startswith("proxy:"):
                key = key[len("proxy:"):]
            out.setdefault(key, []).append(o)
    return out


class Look:
    """Decides and applies the exposure and white balance of one camera."""

    def __init__(self, scene, args, mood: str | None, windows: set[int], look_from: dict | None,
                 look_from_path: Path | None, limits=None, project: dict | None = None):
        self.scene = scene
        self.exposure_mode, self.exposure_value = parse_exposure(args.exposure)
        self.target = float(args.exposure_target)
        self.wb_mode, self.wb_fixed = parse_white_balance(args.white_balance)
        self.mood = mood
        self.windows = windows
        self.look_from = look_from            # {camera: {"ev", "whitepoint"}} or None
        self.look_from_path = look_from_path
        self.ev_offset = float(getattr(args, "ev_offset", 0.0) or 0.0)
        # Milestone 13: the EV limits of this run (the cap, or the Milestone 11 limits for the A/B's m11) and the
        # project whitepoint ({"whitepoint", "from_camera", "source", ...}; set by lock_project_whitepoint).
        self.limits = tuple(EXPOSURE_LIMITS if limits is None else limits)
        self.project = project
        self.variant = None                   # the light variant of this render (main sets it)
        # pre-flight of P3: the stops the floor moves down for the scene's sun (main sets it, sun_floor_shift)
        self.floor_shift = 0.0
        self.sun_wm2 = None
        # fix round after P3: the scene manifest's room types (main sets them, room_types_from_manifest), the
        # fallback of a camera without ``wenart_room_type``
        self.room_types: dict[str, str] = {}

    def room_type(self, cam) -> str | None:
        """The room type of ``cam`` (``camera_room_type``: its property, else the scene manifest's)."""
        return camera_room_type(cam.get("wenart_room_type"), cam.get("wenart_room"), self.room_types)

    def view_limits(self) -> tuple[float, float]:
        """The limits a view is metered against: the run's limits, the floor moved for the sun (``view_limits``)."""
        return view_limits(self.limits, self.floor_shift)

    def key_settings(self, cam_name: str, samples: int, res, denoiser, hidden, plugged, alt_look=None,
                     max_bounces=None, preview_quality=None) -> dict:
        values = self.look_from[cam_name] if self.look_from is not None else None
        return key_settings(samples, res, denoiser, self.exposure_mode, self.exposure_value, self.target,
                            self.wb_mode, self.wb_fixed, hidden, plugged, values, alt_look=alt_look,
                            max_bounces=max_bounces, ev_offset=self.ev_offset, preview_quality=preview_quality,
                            limits=self.view_limits(),
                            project_whitepoint=(self.project or {}).get("whitepoint") if self.wb_mode == "project" else None)

    def decide(self, cam, out_dir: Path, res: tuple[int, int]) -> dict:
        """The exposure record of a camera before its final render
        (``window_clip_frac`` comes later); ``--ev-offset`` is added to the EV
        of every mode and recorded as ``ev_offset``."""
        rec = self._decide(cam, out_dir, res)
        rec["ev_offset"] = self.ev_offset
        if self.ev_offset:
            rec["ev"] = round(float(rec["ev"]) + self.ev_offset, 6)
        return rec

    def _decide(self, cam, out_dir: Path, res: tuple[int, int]) -> dict:
        rec = {"mode": self.exposure_mode, "ev": 0.0, "ev_raw": None, "at_limit": False, "target": None,
               "limits": None, "incident_p50": None, "whitepoint": None, "wb_mode": self.wb_mode,
               "wb_temperature": None, "wb_tint": None, "residual": None, "window_clip_frac": None,
               "meter_seconds": 0.0, "meter": None, "mood": self.mood, "source": None, "notes": [],
               "lighting_dark": None}
        if self.look_from is not None:
            values = self.look_from[cam.name]
            rec.update(mode="from", wb_mode="from", ev=values["ev"], whitepoint=values["whitepoint"],
                       source=relative_posix(self.look_from_path, out_dir))
            return rec
        meter = None
        if self.exposure_mode == "auto" or self.wb_mode == "auto":
            meter = meter_camera(self.scene, cam, out_dir, res, self.windows)
            rec["meter_seconds"] = meter.pop("seconds")
            rec["meter"] = {k: meter[k] for k in ("resolution", "samples", "blocks", "blocks_used", "block_px",
                                                   "interior_frac")}
            if "metered" in meter:               # Milestone 10: an exterior view meters its facades
                rec["meter"]["metered"] = meter["metered"]
            rec["incident_p50"] = None if meter["incident_p50"] is None else round(meter["incident_p50"], 6)
        if self.exposure_mode == "auto":
            limits = self.view_limits()
            rec.update(target=self.target, limits=list(limits))
            if self.floor_shift:
                rec["floor_shift_stops"] = self.floor_shift
            if meter["incident_p50"] is None or meter["incident_p50"] <= 0:
                rec["notes"].append("no interior block to meter: EV 0 used")
            else:
                ev, raw, at_limit = exposure_from(meter["incident_p50"], self.target, limits)
                rec.update(ev=ev, ev_raw=raw, at_limit=at_limit)
                rec["lighting_dark"] = lighting_dark_entry(cam.name, cam.get("wenart_room"), raw, ev, limits,
                                                           meter["incident_p50"], self.target)
        elif self.exposure_mode == "fixed":
            rec["ev"] = float(self.exposure_value)
        if self.wb_mode == "auto":
            residual, note = wb_residual(self.mood)
            rec["residual"] = residual
            if note:
                rec["notes"].append(note)
            wp = whitepoint_from(meter["illuminant"], residual) if meter["illuminant"] else None
            if wp is None:
                rec["notes"].append("no light on interior surfaces to balance: white balance off")
            rec["whitepoint"] = wp
        elif self.wb_mode == "fixed":
            rec["whitepoint"] = list(self.wb_fixed)
        elif self.wb_mode in ("project", "kelvin"):
            project = self.project or {}
            rec["whitepoint"] = list(project["whitepoint"]) if project.get("whitepoint") else None
            rec["residual"] = project.get("residual")
            rec["wb_source"] = project.get("source")
            if project.get("from_camera"):
                rec["wb_from_camera"] = project["from_camera"]
            if rec["whitepoint"] is None:
                rec["notes"].append("no project whitepoint (nothing to meter): white balance off")
            elif self.wb_mode == "project":
                self._view_white(cam, rec, meter, out_dir, res)
        return rec

    def _view_white(self, cam, rec: dict, meter: dict | None, out_dir: Path, res: tuple[int, int]) -> None:
        """Fix round after P3 (16-17 Oct 2026): the view's own white point from the project anchor and the view's rig
        share (``mixed_whitepoint``, module docstring). A second metering pass with every rig object hidden gives the
        view's daylight; exterior and open-air views, views without a metering pass and scenes without a rig keep
        the project white point. Every case records ``wb_project_whitepoint`` and ``wb_view_rule``."""
        anchor = [float(v) for v in rec["whitepoint"]]
        rec.update(wb_project_whitepoint=anchor, wb_rig_share=None, wb_rig_kelvin=None, wb_rig_whitepoint=None)
        if under_exterior_sky({k: self.scene.get(k) for k in WORLD_PROPS}, cam.get("wenart_camera_kind"),
                              self.room_type(cam)) or cam.get("wenart_camera_kind") == "exterior":
            rec["wb_view_rule"] = "under the exterior sky (daylight): the project white point"
            return
        if meter is None or not meter.get("illuminant"):
            rec["wb_view_rule"] = "no metering pass with light: the project white point"
            return
        rigs = rig_objects(self.scene)
        kelvin = rig_temperature(self.scene)
        if not rigs or kelvin is None:
            rec["wb_view_rule"] = "no rig light in the scene: the project white point"
            return
        hidden = hide_objects(rigs)
        try:
            day = meter_camera(self.scene, cam, out_dir, res, self.windows)
        finally:
            unhide_objects(hidden)
        rec["meter_seconds"] = round(float(rec["meter_seconds"] or 0.0) + float(day.pop("seconds", 0.0)), 3)
        share = rig_share(meter["illuminant"], day.get("illuminant"))
        rig_rgb = kelvin_whitepoint(self.scene, kelvin)
        rec.update(wb_rig_share=share, wb_rig_kelvin=kelvin, wb_rig_whitepoint=rig_rgb,
                   wb_day_incident_p50=None if day.get("incident_p50") is None else round(day["incident_p50"], 6))
        if share is None or share < WB_RIG_SHARE_MIN:
            rec["wb_view_rule"] = f"rig share below {WB_RIG_SHARE_MIN:g}: the project white point"
            return
        rec["whitepoint"] = mixed_whitepoint(anchor, rig_rgb, share, (self.project or {}).get("residual") or 0.0)
        rec["wb_view_rule"] = WB_VIEW_RULE

    def apply(self, rec: dict) -> None:
        """Set view transform, look, exposure and white balance; read back temperature and tint. Fix round after P3:
        a view with a ``wb_project_whitepoint`` records ``wb_view_shift_mired``, its white point's mired minus the
        project's (0 for a view that kept the project white point, > 0 toward the warm rig)."""
        vs = self.scene.view_settings
        vs.view_transform = VIEW_TRANSFORM
        vs.look = LOOK
        vs.exposure = float(rec["ev"])
        if rec.get("whitepoint"):
            vs.use_white_balance = True
            vs.white_balance_whitepoint = tuple(float(v) for v in rec["whitepoint"])
            rec["wb_temperature"] = round(float(vs.white_balance_temperature), 1)
            rec["wb_tint"] = round(float(vs.white_balance_tint), 2)
            project_k = (self.project or {}).get("kelvin")
            if rec.get("wb_project_whitepoint") and project_k and rec["wb_temperature"]:
                rec["wb_view_shift_mired"] = round(1e6 / float(rec["wb_temperature"]) - 1e6 / float(project_k), 2)
        else:
            vs.use_white_balance = False
            rec["wb_temperature"] = rec["wb_tint"] = None

    def lock_project_whitepoint(self, cameras: list, out_dir: Path, res: tuple[int, int], previous: dict | None) -> dict:
        """Milestone 13: the one whitepoint of the project for mode ``project`` or ``kelvin``: the previous
        manifest's ``white_balance_project`` (locked across re-renders, ``previous_whitepoint_usable``), else
        ``kelvin:K`` through Blender's conversion (``white_balance_temperature`` -> ``white_balance_whitepoint``),
        else the metered illuminant with the mood's residual. Round 3 (docs/milestone13.md §14.3): the metering is
        daylight only: every rig object is hidden (``rig_objects``), the cameras are taken in ``wb_camera_order``
        (rooms whose window faces the sun first, ``sunlit_rooms``, then the other rooms with a window,
        ``daylight_rooms``), up to ``WB_METER_MAX_CAMERAS`` daylight candidates are metered (a windowless one only
        when no daylight candidate gave light) and ``pick_wb_candidate`` keeps the daylight candidate with the most
        incident light, so the sun and not a sky-lit window sets the white. The record carries ``kelvin`` /
        ``tint`` (Blender's reading of the whitepoint), ``metered_on``, ``daylight_only``, ``tried``,
        ``candidates`` (camera, room, daylight, sunlit, incident, kelvin) and ``rig_objects_hidden``. Returns the
        record (also kept in ``self.project``)."""
        record: dict
        if self.wb_mode == "kelvin":
            vs = self.scene.view_settings
            saved = (vs.use_white_balance, tuple(vs.white_balance_whitepoint))
            vs.use_white_balance = True
            vs.white_balance_temperature = float(self.wb_fixed[0])
            wp = normalise_whitepoint([float(v) for v in vs.white_balance_whitepoint])
            vs.use_white_balance, vs.white_balance_whitepoint = saved
            record = {"whitepoint": wp, "from_camera": None, "source": f"kelvin:{float(self.wb_fixed[0]):g}",
                      "residual": None, "kelvin": float(self.wb_fixed[0]), "metered_on": None, "daylight_only": False}
        elif previous_whitepoint_usable(previous):
            record = dict(previous, source=f"previous manifest ({previous.get('source')})")
        else:
            daylight = daylight_rooms(self.scene)
            sunlit = sunlit_rooms(self.scene)
            order = wb_camera_order([(o.name, o.get("wenart_camera_kind"), o.get("wenart_room")) for o in cameras],
                                    daylight, sunlit)
            by_name = {o.name: o for o in cameras}
            residual, _note = wb_residual(self.mood)
            rows: list[dict] = []
            hidden = hide_objects(rig_objects(self.scene))
            try:
                for cam_name in order:
                    cam = by_name[cam_name]
                    room = cam.get("wenart_room")
                    is_day = cam.get("wenart_camera_kind") != "exterior" and room is not None and str(room) in daylight
                    if len(rows) >= WB_METER_MAX_CAMERAS or (
                            not is_day and any(r["daylight"] and r["whitepoint"] for r in rows)):
                        break
                    # the camera's own world (an exterior candidate meters under the exterior sky, as it renders;
                    # every render selects its world again, so nothing needs restoring). Fix round after P3: no room
                    # type here, so an open-air room's candidate is metered under the interior world as on P3 (its
                    # render takes the exterior world): the project white point does not move.
                    select_world(self.scene, cam)
                    meter = meter_camera(self.scene, cam, out_dir, res, self.windows)
                    rows.append({"camera": cam_name, "room_id": None if room is None else str(room), "daylight": is_day,
                                 "sunlit": is_day and str(room) in sunlit, "incident_p50": meter.get("incident_p50"),
                                 "whitepoint": whitepoint_from(meter["illuminant"], residual) if meter["illuminant"]
                                 else None})
            finally:
                unhide_objects(hidden)
            best = pick_wb_candidate(rows)
            wp = best["whitepoint"] if best else None
            name = best["camera"] if best else (rows[-1]["camera"] if rows else None)
            candidates = []
            for r in rows:
                c = {k: r[k] for k in ("camera", "room_id", "daylight", "sunlit")}
                c["incident_p50"] = None if r["incident_p50"] is None else round(float(r["incident_p50"]), 6)
                c["kelvin"] = whitepoint_kelvin(self.scene, r["whitepoint"])[0] if r["whitepoint"] else None
                candidates.append(c)
            record = {"whitepoint": wp, "from_camera": name,
                      "source": (f"metered on {name} (daylight only: {len(hidden)} rig objects hidden; the most "
                                 f"incident light of {len(rows)} candidates)" if wp else "no light to meter"),
                      "residual": residual, "metered_on": name if wp else None, "daylight_only": True,
                      "tried": [r["camera"] for r in rows], "candidates": candidates,
                      "rig_objects_hidden": len(hidden), "daylight_rooms": sorted(daylight),
                      "sunlit_rooms": sorted(sunlit), "daylight_camera": bool(best and best["daylight"]),
                      "sunlit_camera": bool(best and best["sunlit"])}
            if wp is not None:
                record["kelvin"], record["tint"] = whitepoint_kelvin(self.scene, wp)
        self.project = record
        return record


def meter_camera(scene, cam, out_dir: Path, res: tuple[int, int], windows: set[int]) -> dict:
    """Metering pre-render of ``cam`` (1/8 resolution, 16 samples, no denoiser,
    no adaptive sampling, diffuse light passes on), read back and measured
    with ``meter_stats``. Every changed setting is restored."""
    import bpy

    r, c = scene.render, scene.cycles
    saved = (r.resolution_x, r.resolution_y, c.samples, c.use_denoising, c.use_adaptive_sampling, r.filepath)
    w = max(METER_MIN_RES[0], res[0] // METER_RES_DIV)
    h = max(METER_MIN_RES[1], res[1] // METER_RES_DIV)
    tmp = out_dir / f".meter_{cam.name}.exr"
    t0 = time.time()
    try:
        scene.camera = cam
        r.resolution_x, r.resolution_y = w, h
        c.samples, c.use_denoising, c.use_adaptive_sampling = METER_SAMPLES, False, False
        r.use_persistent_data = True
        _light_passes(scene, True)
        set_output(scene, "OPEN_EXR_MULTILAYER")
        r.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        channels = read_exr(tmp)
    finally:
        _light_passes(scene, False)
        r.resolution_x, r.resolution_y, c.samples, c.use_denoising, c.use_adaptive_sampling, r.filepath = saved
        if tmp.exists():
            tmp.unlink()
    direct = find_rgb(channels, "Diffuse Direct", "DiffDir")
    indirect = find_rgb(channels, "Diffuse Indirect", "DiffInd")
    albedo = find_rgb(channels, "Diffuse Color", "DiffCol")
    index = find_channel(channels, "Object Index.X", "IndexOB.X")
    depth = find_channel(channels, "Depth.Z")
    if any(a is None for a in (direct, indirect, albedo, index, depth)):
        raise RuntimeError(f"metering EXR of {cam.name} lacks a pass: {sorted(channels)}")
    normal_z = None
    if cam.get("wenart_camera_kind") == "exterior":        # Milestone 10: meter the facades
        normal = find_rgb(channels, "Normal")
        normal_z = None if normal is None else normal[..., 2]
    stats = meter_stats(direct + indirect, albedo, index, depth, windows, normal_z=normal_z)
    stats.update(resolution=[w, h], samples=METER_SAMPLES, seconds=round(time.time() - t0, 3))
    return stats


# --------------------------------------------------------------------------
# Hide and plug
# --------------------------------------------------------------------------

class Hider:
    """Hides objects by wenart id, plugs the holes of hidden openings and undoes both."""

    def __init__(self, scene, scene_manifest: dict | None):
        self.scene = scene
        self.manifest = scene_manifest
        self.by_id = indexed_objects(scene)
        self.hidden_objects: list = []
        self.plugs: list = []
        self.info: dict = {}

    def unknown(self, ids) -> list[str]:
        return [i for i in ids if i not in self.by_id]

    def kind_of(self, wenart_id: str) -> str | None:
        objs = self.by_id.get(wenart_id) or []
        return objs[0].get("wenart_kind") if objs else None

    def apply(self, ids: list[str], plug: bool) -> list[str]:
        """Hide ``ids``; with ``plug`` close the holes of hidden doors/windows. Returns the plugged ids."""
        plugged = []
        for wenart_id in ids:
            objs = self.by_id[wenart_id]
            for o in objs:
                if not o.hide_render:
                    o.hide_render = True
                    self.hidden_objects.append(o)
            if plug and self.kind_of(wenart_id) in ("door", "window"):
                self.info[wenart_id] = self._plug(wenart_id, objs)
                plugged.append(wenart_id)
        return plugged

    def _plug(self, wenart_id: str, objs: list) -> dict:
        from wenart.blender import common

        if self.manifest is None:
            raise RuntimeError("--plug needs scene_manifest.json next to the scene")
        objects = self.manifest.get("objects") or []
        entry = next((o for o in objects if o.get("wenart_id") == wenart_id and o.get("kind") in ("door", "window")),
                     None)
        if entry is None or not entry.get("wall_id"):
            raise RuntimeError(f"{wenart_id}: no door/window entry with a wall_id in the scene manifest")
        wall = next((o for o in objects if o.get("kind") == "wall" and o.get("wenart_id") == entry["wall_id"]), None)
        if wall is None or "start" not in wall or "thickness" not in wall:
            raise RuntimeError(f"{wenart_id}: wall {entry['wall_id']} not in the scene manifest")
        points = [tuple(o.matrix_world @ v.co) for o in objs if o.type == "MESH" for v in o.data.vertices]
        verts, faces, info = plug_box(wall, points)
        wall_ob = next((o for o in self.scene.objects if o.get("wenart_id") == wall["wenart_id"]
                        and o.get("wenart_kind") == "wall"), None)
        if wall_ob is None or not wall_ob.data.materials:
            raise RuntimeError(f"{wenart_id}: wall object {wall['wenart_id']} has no material")
        # The wall's slots, each face as the wall around the hole (wet-room tiles, exterior plaster).
        mw = wall_ob.matrix_world
        m3 = mw.to_3x3()
        wall_faces = [(tuple(m3 @ p.normal), [tuple(mw @ wall_ob.data.vertices[i].co) for i in p.vertices],
                       p.material_index) for p in wall_ob.data.polygons]
        slots = plug_face_slots(wall, verts, faces, wall_faces)
        materials = list(wall_ob.data.materials)
        slots = [s if s < len(materials) else 0 for s in slots]
        ob = common.new_mesh_object(f"plug_{wenart_id}", verts, faces, collection=self.scene.collection,
                                    wenart_id=f"plug:{wenart_id}", kind="wall", status="assumed",
                                    materials=materials, face_material_indices=slots)
        ob.pass_index = 0
        self.plugs.append(ob)
        # A plugged window lets no sky in: its portal would only waste samples.
        for o in self.scene.objects:
            if o.type == "LIGHT" and o.get("wenart_opening") == wenart_id and not o.hide_render:
                o.hide_render = True
                self.hidden_objects.append(o)
        names: dict[str, str] = {}
        for side, slot in zip(plug_face_sides(wall, verts, faces), slots):
            names.setdefault(side, materials[slot].name)
        info.update(wall_id=wall["wenart_id"], materials=names)
        return info

    def undo(self) -> None:
        from wenart.blender import common

        for ob in self.plugs:
            common.delete_object(ob)
        for o in self.hidden_objects:
            o.hide_render = False
        self.plugs, self.hidden_objects, self.info = [], [], {}


# --------------------------------------------------------------------------
# One output folder
# --------------------------------------------------------------------------

class RenderRun:
    """Renders cameras into one folder and keeps its ``render_manifest.json``."""

    def __init__(self, ctx: "Context", out_dir: Path, cameras: list, hidden: list[str], plugged: list[str]):
        self.ctx = ctx
        self.out = out_dir
        self.out.mkdir(parents=True, exist_ok=True)
        self.cameras = cameras
        self.hidden = list(hidden)
        self.plugged = list(plugged)
        self.manifest_path = self.out / "render_manifest.json"
        self.previous = load_previous(self.manifest_path)
        self.warnings: list[str] = []
        if ctx.fingerprint is None:
            self.warnings.append("scene has no file on disk: no fingerprint, every camera is rendered")
        # The manifest is cumulative: entries of cameras not asked for in this run are
        # carried over (a --cameras subset must not forget the others), entries of cameras
        # that no longer exist in the scene are dropped, and each one says what it is.
        # Dropped entries are listed under dropped_stale (their files stay on disk, review L2);
        # earlier items are carried over while the camera has no entry and files of it remain.
        run_names = {o.name for o in cameras}
        self.entries: dict[str, dict] = {}
        self.dropped: dict[str, dict] = dict(load_dropped(self.manifest_path))
        self.carried = set(self.dropped)     # items of earlier runs (kept only while files remain)
        for name, entry in self.previous.items():
            if name not in ctx.camera_names:
                self.warnings.append(f"{name}: no such camera in the scene, manifest entry dropped "
                                     f"(listed under dropped_stale, files kept)")
                self.dropped[name] = stale_item(name, entry, "no such camera in the scene (a camera of an "
                                                             "earlier build or camera policy)")
                self.carried.discard(name)
                continue
            if name not in run_names and entry.get("scene_sha256") != ctx.fingerprint:
                self.warnings.append(f"{name}: rendered from another scene build and not asked for in this run")
            if name not in run_names and not entry.get("render_key"):
                self.warnings.append(f"{name}: stale entry (no render_key, rendered before Milestone 5) kept; "
                                     f"re-render it")
            self.entries[name] = entry
        self.rendered = self.skipped = 0
        self.not_rendered: list[str] = []      # cameras the deadline stopped (docs/milestone6.md §5 row 12)

    @property
    def incomplete(self) -> bool:
        return bool(self.not_rendered)

    def cut(self, cam) -> None:
        """Past the deadline: ``cam`` goes on ``not_rendered``. A carried-over entry of it that was
        rendered from another scene build is dropped (``dropped_stale``, files kept): it is not a view
        of this scene, and readers would take it for one (review L2)."""
        self.not_rendered.append(cam.name)
        entry = self.entries.get(cam.name)
        fingerprint = self.ctx.fingerprint
        if entry is None or fingerprint is None or entry.get("scene_sha256") == fingerprint:
            return
        del self.entries[cam.name]
        old = str(entry.get("scene_sha256") or "none")[:12]
        self.dropped[cam.name] = stale_item(cam.name, entry, f"not re-rendered before {DEADLINE_ENV}; the entry "
                                                             f"was rendered from another scene build ({old})")
        self.carried.discard(cam.name)
        self.warnings.append(f"{cam.name}: not re-rendered before {DEADLINE_ENV}; its entry from another scene "
                             f"build was dropped (listed under dropped_stale, files kept)")

    def dropped_stale(self) -> list[dict]:
        """The ``dropped_stale`` list: cameras without an entry, with the files of them still on disk."""
        out = []
        for name in sorted(self.dropped):
            if name in self.entries:
                continue                     # rendered (or reused) again in this run
            item = dict(self.dropped[name])
            item["files"] = sorted(p.name for p in self.files(name).values() if p.exists())
            if item["files"] or name not in self.carried:
                out.append(item)             # a carried item without files left is not stale any more
        return out

    def write_manifest(self) -> None:
        ctx = self.ctx
        args = ctx.args
        manifest = {
            "schema_version": "0.1",
            "scene": relative_posix(ctx.blend_path, self.out) if ctx.blend_path else None,
            "scene_sha256": ctx.fingerprint,
            "device": ctx.device,
            "device_requested": ctx.args.device,
            "blender_version": ctx.blender_version,
            "samples": ctx.args.samples,
            "resolution": list(ctx.res),
            "denoiser": ctx.denoiser,
            "render_code_version": RENDER_CODE_VERSION,
            "view_transform": VIEW_TRANSFORM,
            "look": LOOK,
            "exposure_mode": "from" if ctx.look.look_from is not None else ctx.look.exposure_mode,
            "exposure_target": ctx.look.target,
            "exposure_limits": list(ctx.look.limits),
            # pre-flight of P3: the floor the views were metered against (the cap stays exposure_limits[1])
            "exposure_floor": {"sun_wm2": getattr(ctx.look, "sun_wm2", None), "reference_wm2": SUN_FLOOR_REFERENCE_WM2,
                               "shift_stops": ctx.look.floor_shift, "view_limits": list(ctx.look.view_limits())},
            "white_balance_mode": "from" if ctx.look.look_from is not None else ctx.look.wb_mode,
            # Milestone 13 (docs/milestone13.md §13.2): the project whitepoint, the light variant of the build and
            # the render, the views whose metered EV passed the cap
            "white_balance_project": ctx.look.project,
            "light_variant": ctx.light_variant,
            "lighting_dark": [self.entries[name]["exposure"]["lighting_dark"] for name in sorted(self.entries)
                              if (self.entries[name].get("exposure") or {}).get("lighting_dark")],
            "look_from": relative_posix(ctx.look.look_from_path, self.out) if ctx.look.look_from_path else None,
            "hidden": self.hidden,
            "plugged": self.plugged,
            "alt_look": args.alt_look or None,
            "max_bounces": args.max_bounces,
            "bounces": None if args.max_bounces is None else bounce_settings(args.max_bounces),
            "ev_offset": float(args.ev_offset or 0.0),
            "preview_quality": args.preview_quality,
            "pass_index": ctx.pass_index,
            "renders": [self.entries[name] for name in sorted(self.entries)],
            # Milestone 12 (pod P7): a --cameras re-render after an edit renders the changed rooms' views only;
            # the other views keep their files from the earlier build (not asked for in this run), listed here
            "carried_from_earlier_build": sorted(
                name for name, e in self.entries.items()
                if name not in {o.name for o in self.cameras} and e.get("scene_sha256") != ctx.fingerprint),
            "dropped_stale": self.dropped_stale(),
            "incomplete": self.incomplete,
            "not_rendered": list(self.not_rendered),
            "deadline": ctx.deadline,
            "warnings": self.warnings,
        }
        self.manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    def files(self, cam_name: str) -> dict[str, Path]:
        o = self.out
        return {"png": o / f"{cam_name}.png", "exr": o / f"{cam_name}_passes.exr",
                "preview": o / f"{cam_name}_preview.jpg", "depth": o / f"{cam_name}_depth.png",
                "index": o / f"{cam_name}_index.png", "depth_mm": o / f"{cam_name}_depth_mm.png",
                "normal": o / f"{cam_name}_normal.png", "alt_preview": o / f"{cam_name}_alt_preview.jpg"}

    def key(self, cam) -> str:
        ctx = self.ctx
        return render_key(ctx.look.key_settings(cam.name, ctx.args.samples, ctx.res, ctx.denoiser,
                                                self.hidden, self.plugged, alt_look=ctx.args.alt_look,
                                                max_bounces=ctx.args.max_bounces,
                                                preview_quality=ctx.args.preview_quality))

    def check(self, cam) -> tuple[str | None, str]:
        """``(reason to render or None, render_key)``."""
        key = self.key(cam)
        f = self.files(cam.name)
        if self.ctx.args.force:
            return "--force", key
        needed = [f["png"], f["exr"], f["preview"], f["index"], f["depth_mm"], f["normal"]]
        if self.ctx.args.alt_look:
            needed.append(f["alt_preview"])
        return reuse_reason(cam.name, self.previous.get(cam.name), self.ctx.fingerprint, needed, key), key

    def reuse(self, cam, key: str) -> None:
        """Keep the files; statistics come from the EXR on disk (cheap), time and exposure from the run that made it."""
        prev = self.previous[cam.name]
        f = self.files(cam.name)
        try:
            products = pass_products(read_exr(f["exr"]))
        except Exception as exc:  # noqa: BLE001 - fall back to the stored statistics, loudly
            products = None
            self.warnings.append(f"{cam.name}: pass readback failed ({exc}); statistics copied from the previous "
                                 f"manifest")
        entry = dict(prev)
        entry.update(skipped=True, scene_sha256=self.ctx.fingerprint, render_key=key,
                     preview_bytes=f["preview"].stat().st_size, hidden=self.hidden, plugged=self.plugged,
                     **camera_lens(cam))
        if self.ctx.args.alt_look:
            entry["alt_preview_bytes"] = f["alt_preview"].stat().st_size
        if products is not None and products["depth"] is not None:
            entry.update(depth=products["depth"], index_values=products["index_values"],
                         index_stats=products["index_stats"])
        self.entries[cam.name] = entry
        self.skipped += 1
        self.write_manifest()
        print(f"SKIP {cam.name} (rendered from this scene with these settings, {prev['seconds']}s) "
              f"depth={entry.get('depth')} indices={entry.get('index_values')}")

    def render(self, cam, key: str, reason: str) -> None:
        import bpy

        ctx = self.ctx
        f = self.files(cam.name)
        if f["png"].exists():
            print(f"RERENDER {cam.name}: {reason}")
        scene = ctx.scene
        scene.camera = cam
        # Milestone 11 E13: the exterior views under the physical sky; fix round after P3: the open-air rooms too
        room_type = ctx.look.room_type(cam)
        world = select_world(scene, cam, room_type)
        props = {k: scene.get(k) for k in WORLD_PROPS}
        under_sky = under_exterior_sky(props, cam.get("wenart_camera_kind"), room_type)
        look = ctx.look.decide(cam, self.out, ctx.res)
        ctx.look.apply(look)
        set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = str(f["exr"])
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        seconds = time.time() - t0
        result = bpy.data.images.get("Render Result")
        set_output(scene, "PNG")
        result.save_render(str(f["png"]), scene=scene)
        channels = read_exr(f["exr"])
        products = pass_products(channels)
        if products["index"] is None or products["depth_mm"] is None or products["normal"] is None:
            raise RuntimeError(f"{cam.name}: the EXR lacks the index, depth or normal pass")
        quality = ctx.args.preview_quality
        main_img = read_display_png(f["png"])
        pull, weights, final = self.window_pull(cam, look, result, main_img, channels, products)
        sky = sky_weights = None
        if under_sky:
            # fix round after P3: the sky of a view under the exterior world (the panes and the sky never overlap:
            # a pane is a surface hit, the sky none)
            sky, sky_weights, sky_img = self.sky_pull(cam, look, result, final if final is not None else main_img,
                                                      channels)
            if sky_img is not None:
                final = sky_img
        if final is not None:
            write_png(f["png"], final, DISPLAY_PNG_LEVEL)    # the pulled panes and sky, everything else as saved
            preview_bytes = encode_preview(scene, f["png"], f["preview"], quality)
        else:
            preview_bytes = save_preview(scene, result, f["preview"], quality)
        pulls = [(int(p["k"]), w) for p, w in ((pull, weights), (sky, sky_weights)) if p and w is not None]
        alt_bytes = self.alt_preview(cam, look, result, pulls, f["alt_preview"]) if ctx.args.alt_look else None
        write_png(f["index"], products["index"])
        write_png(f["depth_mm"], products["depth_mm"])
        write_png(f["normal"], products["normal"])
        if products["depth_legacy"] is not None:
            write_png(f["depth"], products["depth_legacy"])
        look["window_clip_frac"] = window_clip_frac(final if final is not None else read_display_png(f["png"]),
                                                    products["index"], ctx.windows)
        if look["at_limit"]:
            self.warnings.append(f"{cam.name}: exposure at the limit ({look['ev_raw']:+.2f} EV wanted, "
                                 f"{look['ev']:+.2f} used)")
        if look.get("lighting_dark"):
            self.warnings.append(f"{cam.name}: {LIGHTING_DARK_CHECK} ({look['lighting_dark']['severity']}): "
                                 f"{look['lighting_dark']['message']}")
        for note in look["notes"]:
            self.warnings.append(f"{cam.name}: {note}")
        self.entries[cam.name] = {
            "camera": cam.name, "room_id": cam.get("wenart_room"), "level_id": cam.get("wenart_level"),
            **camera_lens(cam),
            "lighting_dark": look.get("lighting_dark"),
            "sun_hidden": sun_hidden_for(props, cam.get("wenart_camera_kind"), room_type),
            # fix round after P3: the room type the world was chosen by, and the sky pull of a view under the sky
            "room_type": room_type, "open_air": open_air(room_type), "sky_pull": sky,
            "vram_mib": vram_used_mib() if ctx.device != "CPU" else None,
            "png": f["png"].name, "exr": f["exr"].name, "preview": f["preview"].name,
            "depth_png": f["depth"].name if f["depth"].exists() else None, "index_png": f["index"].name,
            "files": {"index": f["index"].name, "depth_mm": f["depth_mm"].name, "normal": f["normal"].name,
                      "depth": f["depth"].name if f["depth"].exists() else None},
            "preview_bytes": preview_bytes, "seconds": round(seconds, 2), "samples": ctx.args.samples,
            "resolution": list(ctx.res), "depth": products["depth"], "index_values": products["index_values"],
            "index_stats": products["index_stats"], "skipped": False, "scene_sha256": ctx.fingerprint,
            "render_key": key, "exposure": look, "hidden": self.hidden, "plugged": self.plugged,
            "window_pull": pull,
            "alt_preview": f["alt_preview"].name if alt_bytes is not None else None,
            "alt_preview_bytes": alt_bytes,
            "world": world,
        }
        self.rendered += 1
        self.write_manifest()   # after every camera: a killed run keeps what it rendered
        pull_text = "none" if pull is None else f"{pull['ev']:+g}EV clip {pull['clip_before']}->{pull['clip_after']}"
        sky_text = "none" if sky is None else f"k={sky['k']} sat {sky['saturation_before']}->{sky['saturation_after']}"
        print(f"RENDERED {cam.name} in {seconds:.1f}s ev={look['ev']:+.3f} wb={look['wb_temperature']} "
              f"rig_share={look.get('wb_rig_share')} meter={look['meter_seconds']}s pull={pull_text} sky={sky_text} "
              f"world={world} depth={products['depth']} indices={products['index_values']}")

    def window_pull(self, cam, look: dict, result, main, channels: dict, products: dict):
        """``(record, weights, final)`` of the window pull of one camera
        (module docstring): ``record`` None when no pane is in view (or the EXR
        has no Diffuse Color pass), ``final`` None when no k was chosen (the
        PNG stays as saved)."""
        import numpy as np

        from wenart import views

        albedo = find_rgb(channels, "Diffuse Color", "DiffCol")
        if albedo is None:
            self.warnings.append(f"{cam.name}: the EXR has no Diffuse Color pass: no window pull")
            return None, None, None
        mask = pane_mask(products["index"], albedo, self.ctx.windows)
        if not mask.any():
            return None, None, None
        t0 = time.time()
        walls = views.regions(products["index"], products["depth_mm"], products["normal"], {}).masks.get(
            views.STRUCT_WALLS)
        wall_median = masked_median(main, walls) if walls is not None else None
        tmp = self.out / f".pull_{cam.name}.png"
        candidates, images = [], {}
        for k in PULL_STEPS:
            img = save_display(self.ctx.scene, result, tmp, float(look["ev"]) - k, look=LOOK)
            cand = {"k": k, "clip": clip_share(img, mask), "median": masked_median(img, mask),
                    "p90": masked_percentile(img, mask, 90.0)}
            candidates.append(cand)
            images[k] = img
            if pull_qualifies(cand, wall_median):
                break                    # the smallest qualifying k: later ones are not needed
            if wall_median is not None and cand["median"] <= wall_median:
                break                    # darker than the walls: a deeper k is darker still and never chosen
        k, rule = choose_pull(candidates, wall_median)
        clip_before = clip_share(main, mask)
        record = {"ev": -float(k) if k else 0.0, "k": k, "pane_ev": round(float(look["ev"]) - k, 6),
                  "clip_before": clip_before, "clip_after": clip_before, "pane_px": int(np.count_nonzero(mask)),
                  "pane_median": round(masked_median(main, mask), 4),
                  "pane_p90": round(masked_percentile(main, mask, 90.0), 4),
                  "wall_median": None if wall_median is None else round(wall_median, 4), "rule": rule,
                  "targets": {"p90_max": PULL_P90_MAX, "median_target": PULL_MEDIAN_TARGET, "max_clip": PULL_MAX_CLIP},
                  "tried": [{"k": c["k"], "clip": c["clip"], "median": round(c["median"], 4),
                             "p90": round(c["p90"], 4)} for c in candidates]}
        if k == 0:
            record["seconds"] = round(time.time() - t0, 3)
            return record, None, None
        weights = feather_weights(mask)
        final = blend_pull(main, images[k], weights)
        record["clip_after"] = clip_share(final, mask)
        record["pane_median_after"] = round(masked_median(final, mask), 4)
        record["pane_p90_after"] = round(masked_percentile(final, mask, 90.0), 4)
        record["seconds"] = round(time.time() - t0, 3)
        return record, weights, final

    def sky_pull(self, cam, look: dict, result, main, channels: dict):
        """``(record, weights, final)`` of the sky pull of a view under the exterior sky (fix round after P3, module
        docstring; ``choose_sky_pull``): ``record`` None when the depth pass is missing or the sky covers less than
        ``SKY_PULL_MIN_SHARE`` of the frame, ``final`` None when no k is chosen. ``main`` is the display image after
        the window pull; only sky pixels change (feathered inwards like the panes)."""
        import numpy as np

        depth = find_channel(channels, "Depth.Z")
        if depth is None:
            self.warnings.append(f"{cam.name}: the EXR has no depth pass: no sky pull")
            return None, None, None
        mask = sky_mask(depth)
        share = float(mask.mean()) if mask.size else 0.0
        if share < SKY_PULL_MIN_SHARE:
            return None, None, None
        t0 = time.time()
        before = {"median": masked_median(main, mask), "saturation": masked_saturation(main, mask)}
        tmp = self.out / f".sky_{cam.name}.png"
        candidates, images = [], {}
        if not sky_pull_qualifies(before):
            for k in SKY_PULL_STEPS:
                img = save_display(self.ctx.scene, result, tmp, float(look["ev"]) - k, look=LOOK)
                cand = {"k": k, "median": masked_median(img, mask), "saturation": masked_saturation(img, mask)}
                candidates.append(cand)
                images[k] = img
                if sky_pull_qualifies(cand):
                    break                # the smallest qualifying k
        k, rule = choose_sky_pull(before, candidates)
        record = {"ev": -float(k) if k else 0.0, "k": k, "sky_ev": round(float(look["ev"]) - k, 6),
                  "sky_px": int(np.count_nonzero(mask)), "sky_share": round(share, 4),
                  "median_before": round(before["median"], 4), "saturation_before": round(before["saturation"], 4),
                  "median_after": round(before["median"], 4), "saturation_after": round(before["saturation"], 4),
                  "rule": rule, "targets": {"median_max": SKY_PULL_MEDIAN_MAX, "saturation_min": SKY_PULL_SAT_MIN},
                  "tried": [{"k": c["k"], "median": round(c["median"], 4), "saturation": round(c["saturation"], 4)}
                            for c in candidates]}
        if k == 0:
            record["seconds"] = round(time.time() - t0, 3)
            return record, None, None
        weights = feather_weights(mask)
        final = blend_pull(main, images[k], weights)
        record["median_after"] = round(masked_median(final, mask), 4)
        record["saturation_after"] = round(masked_saturation(final, mask), 4)
        record["seconds"] = round(time.time() - t0, 3)
        return record, weights, final

    def alt_preview(self, cam, look: dict, result, pulls: list, path: Path) -> int:
        """``<cam>_alt_preview.jpg``: the Render Result with ``--alt-look`` at the
        camera's EV; with a window pull the alt look is also saved at EV - k
        (the main image's k) and blended with the main image's weights. Fix round after P3: ``pulls`` =
        ``[(k, weights)]`` of every pull the main image got (the panes, the sky), blended in that order."""
        scene, quality = self.ctx.scene, self.ctx.args.preview_quality
        alt = self.ctx.args.alt_look
        if not pulls:
            vs = scene.view_settings
            saved = (vs.look, vs.exposure)
            try:
                vs.look, vs.exposure = alt, float(look["ev"])
                return save_preview(scene, result, path, quality)
            finally:
                vs.look, vs.exposure = saved
        tmp = self.out / f".alt_{cam.name}.png"
        image = save_display(scene, result, tmp, float(look["ev"]), look=alt)
        for k, weights in pulls:
            pulled = save_display(scene, result, tmp, float(look["ev"]) - int(k), look=alt)
            image = blend_pull(image, pulled, weights)
        try:
            write_png(tmp, image, DISPLAY_PNG_LEVEL)
            return encode_preview(scene, tmp, path, quality)
        finally:
            tmp.unlink(missing_ok=True)


class Context:
    """What every output folder of one Blender process shares."""

    def __init__(self, scene, args, device, denoiser, res, look: Look, camera_names: set[str],
                 deadline: float | None = None):
        import bpy

        self.scene = scene
        self.args = args
        self.device = device
        self.denoiser = denoiser
        self.res = res
        self.look = look
        self.camera_names = camera_names
        self.deadline = deadline
        self.blend_path = bpy.data.filepath or None
        self.fingerprint = scene_fingerprint(bpy.data.filepath)
        self.blender_version = bpy.app.version_string
        self.pass_index = pass_index_table(scene)
        self.windows = window_indices(scene)
        # Milestone 13: the variant the render runs under (the build's is in the scene, wenart_light_variant)
        self.light_variant = {"render": look.variant, "build": scene.get("wenart_light_variant") or None}


def _load_scene_manifest() -> dict | None:
    import bpy

    if not bpy.data.filepath:
        return None
    path = Path(bpy.data.filepath).parent / "scene_manifest.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    import bpy

    args = parse_args(argv)
    out = Path(args.out)
    try:
        width, height = (int(v) for v in args.res.lower().split("x"))
        parse_exposure(args.exposure)      # bad look flags fail before any work
        if not (math.isfinite(args.exposure_target) and args.exposure_target > 0):
            raise UsageError(f"--exposure-target must be a positive number, not {args.exposure_target}")
        parse_white_balance(args.white_balance)
        sets = group_hide_sets(parse_hide_sets(args.hide_sets)) if args.hide_sets else None
        hide_ids = parse_ids(args.hide)
        if sets is not None and (hide_ids or args.plug):
            raise UsageError("--hide-sets cannot be combined with --hide / --plug")
        if args.plug and not hide_ids and sets is None:
            raise UsageError("--plug needs --hide")
        check_control_flags(args)
    except (UsageError, ValueError) as exc:
        print(f"usage error: {exc}")
        return 2
    scene = bpy.context.scene
    if args.alt_look:
        # The look list depends on the view transform (AgX here); an unknown name raises TypeError.
        scene.view_settings.view_transform = VIEW_TRANSFORM
        try:
            scene.view_settings.look = args.alt_look
        except TypeError:
            print(f"usage error: --alt-look {args.alt_look!r} is not a look of {VIEW_TRANSFORM}")
            return 2
        finally:
            scene.view_settings.look = LOOK
    deadline, deadline_note = deadline_from_env()
    if deadline_note:
        print(f"WARNING: {deadline_note}")

    all_cameras = sorted((o for o in scene.objects if o.type == "CAMERA" and o.get("wenart_kind") == "camera"),
                         key=lambda o: o.name)
    by_name = {o.name: o for o in all_cameras}
    if sets is not None:
        missing = sorted({c for s in sets for c in s["cameras"]} - set(by_name))
        cameras = [by_name[c] for c in dict.fromkeys(c for s in sets for c in s["cameras"]) if c in by_name]
    elif args.cameras != "all":
        wanted = [c for c in args.cameras.split(",") if c]
        missing = sorted(set(wanted) - set(by_name))
        cameras = [o for o in all_cameras if o.name in set(wanted)]
    else:
        missing, cameras = [], all_cameras
    if missing:
        print(f"unknown cameras: {missing}")
        return 2
    if not cameras:
        print("no cameras to render")
        return 2

    hider = Hider(scene, _load_scene_manifest())
    asked = hide_ids + [i for s in (sets or []) for i in s["ids"]]
    unknown = hider.unknown(asked)
    if unknown:
        print(f"unknown id: {sorted(set(unknown))} (no object with a pass index carries it)")
        return 2
    if (args.plug or any(s["plug"] for s in sets or [])) and hider.manifest is None:
        print("--plug needs scene_manifest.json next to the scene file")
        return 2

    look_from = None
    look_from_path = None
    if args.look_from:
        look_from_path = Path(args.look_from)
        if not look_from_path.is_file():
            print(f"--look-from {look_from_path} does not exist")
            return 2
        source = load_previous(look_from_path)
        look_from, bad = {}, []
        for cam in cameras:
            values = look_from_values(source.get(cam.name))
            if values is None:
                bad.append(cam.name)
            else:
                look_from[cam.name] = values
        if bad:
            print(f"--look-from {look_from_path}: no exposure record for camera(s) {sorted(set(bad))}")
            return 2

    device = configure_device(scene, args.device)
    denoiser = configure_render(scene, args.samples, (width, height), device, not args.no_denoise, args.max_bounces)
    scene.view_settings.view_transform = VIEW_TRANSFORM
    scene.view_settings.look = LOOK
    mood = scene.get("wenart_mood") or None
    windows = window_indices(scene)
    # Milestone 13: the EV limits of this run from the light variant (the A/B's m11 keeps the Milestone 11 limits).
    try:
        from wenart.blender.lighting import light_levers
        levers = light_levers()
    except ValueError as exc:
        print(f"usage error: {exc}")
        return 2
    look = Look(scene, args, mood, windows, look_from, look_from_path, limits=exposure_limits_for(levers))
    look.variant = levers["variant"]
    # fix round after P3: the room types of the scene manifest, for cameras built without wenart_room_type
    look.room_types = room_types_from_manifest(hider.manifest)
    # pre-flight of P3: the EV floor follows the built scene's sun lamp (sun_floor_shift; 0 under the M11 sun)
    look.sun_wm2 = scene_sun_wm2(scene)
    look.floor_shift = sun_floor_shift(look.sun_wm2)
    if look.wb_mode in ("project", "kelvin") and look_from is None:
        # One whitepoint for the project: the previous manifest's (if metered on daylight), else metered once on
        # daylight (round 3: rig hidden, a camera of a room with a window first).
        previous = load_project_whitepoint(out / "render_manifest.json") if sets is None else None
        record = look.lock_project_whitepoint(all_cameras, out, (width, height), previous)
        print(f"WHITE_BALANCE project: {record['source']} whitepoint={record['whitepoint']}")
    ctx = Context(scene, args, device, denoiser, (width, height), look, set(by_name), deadline)
    print(f"LIGHT_VARIANT render={levers['variant'] or 'none'} build={scene.get('wenart_light_variant') or 'none'} "
          f"ev_limits={list(look.limits)} view_limits={list(look.view_limits())} sun_wm2={look.sun_wm2}")
    if mood is None:
        print("WARNING: scene has no wenart_mood (built before Milestone 5): white-balance residual 0")

    if sets is None:
        # One hide for the whole run (the scene file is never saved, nothing to undo).
        plugged = hider.apply(hide_ids, args.plug) if hide_ids else []
        runs = [(RenderRun(ctx, out, cameras, hide_ids, plugged), None)]
    else:
        # Per set: reuse check, then hide -> plug -> render -> undo (only when it renders).
        runs = []
        for s in sets:
            plugged = [i for i in s["ids"] if s["plug"] and hider.kind_of(i) in ("door", "window")]
            runs.append((RenderRun(ctx, out / s["dir"], [by_name[c] for c in s["cameras"]], s["ids"], plugged), s))

    total = {"rendered": 0, "skipped": 0, "not_rendered": 0}
    for run, hide_set in runs:
        run.write_manifest()
        for cam in run.cameras:
            reason, key = run.check(cam)
            if reason is None:
                run.reuse(cam, key)
                continue
            if deadline_passed(deadline):
                # Past the deadline: no new camera (docs/milestone6.md §5 row 12); reusable ones still count.
                run.cut(cam)
                continue
            if hide_set is not None:
                hider.apply(hide_set["ids"], hide_set["plug"])
            try:
                run.render(cam, key, reason)
            finally:
                if hide_set is not None:
                    hider.undo()
        if run.incomplete:
            run.warnings.append(f"{DEADLINE_ENV} passed: {len(run.not_rendered)} camera(s) not rendered")
            run.write_manifest()
        total["rendered"] += run.rendered
        total["skipped"] += run.skipped
        total["not_rendered"] += len(run.not_rendered)
        print(f"RENDER_DONE {run.out} cameras={len(run.cameras)} rendered={run.rendered} skipped={run.skipped} "
              f"not_rendered={len(run.not_rendered)} listed={len(run.entries)} device={device} hidden={run.hidden} "
              f"plugged={run.plugged}")
    if sets is not None:
        print(f"HIDE_SETS_DONE sets={len(sets)} rendered={total['rendered']} skipped={total['skipped']} "
              f"not_rendered={total['not_rendered']}")
    if total["not_rendered"]:
        print(f"RENDER_INCOMPLETE {total['not_rendered']} camera(s) not rendered: {DEADLINE_ENV} passed")
        return EXIT_INCOMPLETE
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if code:
        sys.exit(code)
