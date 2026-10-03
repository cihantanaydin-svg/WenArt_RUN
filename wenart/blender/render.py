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
the exposure record and the ``render_key``; the pass index table keyed by
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
RENDER_CODE_VERSION = "m7.1"
PASSES = ("combined", "z", "normal", "object_index", "diffuse_color")
VIEW_TRANSFORM = "AgX"
LOOK = "AgX - Punchy"
PREVIEW_QUALITIES = (85, 70, 55, 40, 30, 20)

# Window pull (docs/milestone6.md §5 row 7).
PULL_STEPS = (1, 2, 3, 4)          # stops tried, smallest first
PULL_MAX_CLIP = 0.01               # pane clip share a pull should reach
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
EXPOSURE_LIMITS = (-2.0, 8.0)
EXPOSURE_STEP = 1.0 / 6.0
WB_RESIDUAL = {"warm daylight": 0.35, "golden evening": 0.5, "cool daylight": 0.0, "overcast": 0.0, "night": 0.5}
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
    """``auto`` | ``off`` | ``fixed:r,g,b`` -> (mode, whitepoint normalised to luminance 1 or None)."""
    t = str(text).strip().lower()
    if t in ("auto", "off"):
        return t, None
    if t.startswith("fixed:"):
        try:
            rgb = [float(v) for v in t[len("fixed:"):].split(",")]
        except ValueError:
            rgb = []
        if len(rgb) == 3 and all(math.isfinite(v) and v > 0 for v in rgb):
            return "fixed", normalise_whitepoint(rgb)
    raise UsageError(f"--white-balance must be auto, off or fixed:r,g,b with three positive numbers, not {text!r}")


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


def meter_stats(light, albedo, index, depth, window_indices, blocks_across: int = METER_BLOCKS_ACROSS,
                min_coverage: float = METER_BLOCK_COVERAGE, min_albedo: float = METER_MIN_ALBEDO) -> dict:
    """Incident-light statistics of a metering render.

    ``light`` = Diffuse Direct + Indirect (H x W x 3, colour-free), ``albedo``
    = Diffuse Color, ``index`` = object index, ``depth`` = Cycles Z. Interior
    mask: not a window index, a surface hit (depth < 1e9) and albedo
    luminance >= ``min_albedo``. Returns ``{"incident_p50": Y50 or None,
    "illuminant": [r, g, b] (sum over the mask) or None, "interior_frac",
    "blocks", "blocks_used", "block_px"}``; Y50 is the median of the block
    means of blocks that are at least ``min_coverage`` interior (block side
    ``width // blocks_across`` px). A per-pixel median at a few samples is 0
    (most paths find no light), block means are not."""
    import numpy as np

    light = np.nan_to_num(np.asarray(light, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    albedo = np.nan_to_num(np.asarray(albedo, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    idx = np.rint(np.nan_to_num(np.asarray(index, dtype=np.float64))).astype(np.int64)
    d = np.nan_to_num(np.asarray(depth, dtype=np.float64), nan=DEPTH_BACKGROUND, posinf=DEPTH_BACKGROUND)
    mask = (~np.isin(idx, sorted(int(v) for v in window_indices))) & (d < DEPTH_BACKGROUND) & \
           (luminance(albedo) >= min_albedo)
    y = luminance(light)
    h, w = mask.shape
    b = max(1, w // max(1, blocks_across))
    hh, ww = (h // b) * b, (w // b) * b
    stats = {"incident_p50": None, "illuminant": None, "interior_frac": round(float(mask.mean()), 4) if mask.size else 0.0,
             "blocks": 0, "blocks_used": 0, "block_px": b}
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


def wb_residual(mood: str | None) -> tuple[float, str | None]:
    """``(residual, note)`` for a light mood; unknown moods get 0 and a note."""
    key = str(mood or "").strip().lower()
    if key in WB_RESIDUAL:
        return WB_RESIDUAL[key], None
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


def render_key(settings: dict) -> str:
    """First 16 hex of sha256 over the canonical JSON of the render settings."""
    blob = json.dumps(settings, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def key_settings(samples: int, resolution, denoiser, exposure_mode: str, exposure_value, target: float,
                 wb_mode: str, wb_fixed, hidden, plugged, look_from_values: dict | None = None,
                 alt_look: str | None = None, max_bounces: int | None = None, ev_offset: float = 0.0,
                 preview_quality: int | None = None) -> dict:
    """What the render key covers (docs/milestone5.md §2.5, docs/milestone6.md
    §5 rows 10-11, docs/milestone7.md §6.1). With ``look_from_values``
    (``{"ev", "whitepoint"}`` of the source entry) the exposure and white
    balance are mode ``from`` with those values; ``alt_look``, ``max_bounces``,
    ``ev_offset`` and ``preview_quality`` are the Milestone 6 control flags;
    ``view_transform`` and ``look`` are the display transform of the PNG and
    the preview (Milestone 7: a change of the default look re-renders)."""
    if look_from_values is not None:
        exposure = {"mode": "from", "ev": look_from_values.get("ev"), "whitepoint": look_from_values.get("whitepoint")}
        wb = "from"
    else:
        if exposure_mode == "auto":
            exposure = {"mode": "auto", "target": float(target), "limits": list(EXPOSURE_LIMITS)}
        elif exposure_mode == "fixed":
            exposure = {"mode": "fixed", "ev": float(exposure_value)}
        else:
            exposure = {"mode": "off"}
        wb = "fixed:" + ",".join(f"{v:.6f}" for v in wb_fixed) if wb_mode == "fixed" else wb_mode
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


def pull_qualifies(candidate: dict, wall_median: float | None, max_clip: float = PULL_MAX_CLIP) -> bool:
    """A pull of ``candidate["k"]`` stops is enough: pane clip <= ``max_clip`` and
    the pane median above the wall median (no wall: the clip rule alone)."""
    return candidate["clip"] <= max_clip and (wall_median is None or candidate["median"] > wall_median)


def choose_pull(candidates: list[dict], wall_median: float | None,
                max_clip: float = PULL_MAX_CLIP) -> tuple[int, str]:
    """``(k, rule)`` from ``[{"k", "clip", "median"}]`` (the EV - k saves,
    ``clip`` and ``median`` over the pane mask): the smallest k that
    ``pull_qualifies``; else the k with the lowest clip that keeps the pane
    median above the wall median (ties: the smaller k); with no wall
    (``wall_median`` None) the lowest clip; ``(0, ...)`` = no pull when no k
    keeps the panes brighter than the walls (or nothing was tried)."""
    cands = sorted(candidates, key=lambda c: c["k"])
    for c in cands:
        if pull_qualifies(c, wall_median, max_clip):
            return int(c["k"]), ("smallest k with pane clip <= 1 % and panes brighter than the walls"
                                 if wall_median is not None else "smallest k with pane clip <= 1 % (no wall in view)")
    bright = [c for c in cands if wall_median is None or c["median"] > wall_median]
    if bright:
        best = min(bright, key=lambda c: (c["clip"], c["k"]))
        return int(best["k"]), ("lowest pane clip that keeps the panes brighter than the walls"
                                if wall_median is not None else "lowest pane clip (no wall in view)")
    return 0, "no k keeps the panes brighter than the walls: no pull"


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
                 look_from_path: Path | None):
        self.scene = scene
        self.exposure_mode, self.exposure_value = parse_exposure(args.exposure)
        self.target = float(args.exposure_target)
        self.wb_mode, self.wb_fixed = parse_white_balance(args.white_balance)
        self.mood = mood
        self.windows = windows
        self.look_from = look_from            # {camera: {"ev", "whitepoint"}} or None
        self.look_from_path = look_from_path
        self.ev_offset = float(getattr(args, "ev_offset", 0.0) or 0.0)

    def key_settings(self, cam_name: str, samples: int, res, denoiser, hidden, plugged, alt_look=None,
                     max_bounces=None, preview_quality=None) -> dict:
        values = self.look_from[cam_name] if self.look_from is not None else None
        return key_settings(samples, res, denoiser, self.exposure_mode, self.exposure_value, self.target,
                            self.wb_mode, self.wb_fixed, hidden, plugged, values, alt_look=alt_look,
                            max_bounces=max_bounces, ev_offset=self.ev_offset, preview_quality=preview_quality)

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
               "meter_seconds": 0.0, "meter": None, "mood": self.mood, "source": None, "notes": []}
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
            rec["incident_p50"] = None if meter["incident_p50"] is None else round(meter["incident_p50"], 6)
        if self.exposure_mode == "auto":
            rec.update(target=self.target, limits=list(EXPOSURE_LIMITS))
            if meter["incident_p50"] is None or meter["incident_p50"] <= 0:
                rec["notes"].append("no interior block to meter: EV 0 used")
            else:
                ev, raw, at_limit = exposure_from(meter["incident_p50"], self.target, EXPOSURE_LIMITS)
                rec.update(ev=ev, ev_raw=raw, at_limit=at_limit)
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
        return rec

    def apply(self, rec: dict) -> None:
        """Set view transform, look, exposure and white balance; read back temperature and tint."""
        vs = self.scene.view_settings
        vs.view_transform = VIEW_TRANSFORM
        vs.look = LOOK
        vs.exposure = float(rec["ev"])
        if rec.get("whitepoint"):
            vs.use_white_balance = True
            vs.white_balance_whitepoint = tuple(float(v) for v in rec["whitepoint"])
            rec["wb_temperature"] = round(float(vs.white_balance_temperature), 1)
            rec["wb_tint"] = round(float(vs.white_balance_tint), 2)
        else:
            vs.use_white_balance = False
            rec["wb_temperature"] = rec["wb_tint"] = None


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
    stats = meter_stats(direct + indirect, albedo, index, depth, windows)
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
            "exposure_limits": list(EXPOSURE_LIMITS),
            "white_balance_mode": "from" if ctx.look.look_from is not None else ctx.look.wb_mode,
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
                     preview_bytes=f["preview"].stat().st_size, hidden=self.hidden, plugged=self.plugged)
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
        pull, weights, final = self.window_pull(cam, look, result, read_display_png(f["png"]), channels, products)
        if final is not None:
            write_png(f["png"], final, DISPLAY_PNG_LEVEL)    # the pulled panes, everything else as saved
            preview_bytes = encode_preview(scene, f["png"], f["preview"], quality)
        else:
            preview_bytes = save_preview(scene, result, f["preview"], quality)
        alt_bytes = self.alt_preview(cam, look, result, pull, weights, f["alt_preview"]) if ctx.args.alt_look else None
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
        for note in look["notes"]:
            self.warnings.append(f"{cam.name}: {note}")
        self.entries[cam.name] = {
            "camera": cam.name, "room_id": cam.get("wenart_room"), "level_id": cam.get("wenart_level"),
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
        }
        self.rendered += 1
        self.write_manifest()   # after every camera: a killed run keeps what it rendered
        pull_text = "none" if pull is None else f"{pull['ev']:+g}EV clip {pull['clip_before']}->{pull['clip_after']}"
        print(f"RENDERED {cam.name} in {seconds:.1f}s ev={look['ev']:+.3f} wb={look['wb_temperature']} "
              f"meter={look['meter_seconds']}s pull={pull_text} depth={products['depth']} "
              f"indices={products['index_values']}")

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
            cand = {"k": k, "clip": clip_share(img, mask), "median": masked_median(img, mask)}
            candidates.append(cand)
            images[k] = img
            if pull_qualifies(cand, wall_median):
                break                    # the smallest qualifying k: later ones are not needed
        k, rule = choose_pull(candidates, wall_median)
        clip_before = clip_share(main, mask)
        record = {"ev": -float(k) if k else 0.0, "k": k, "pane_ev": round(float(look["ev"]) - k, 6),
                  "clip_before": clip_before, "clip_after": clip_before, "pane_px": int(np.count_nonzero(mask)),
                  "pane_median": round(masked_median(main, mask), 4),
                  "wall_median": None if wall_median is None else round(wall_median, 4), "rule": rule,
                  "tried": [{"k": c["k"], "clip": c["clip"], "median": round(c["median"], 4)} for c in candidates]}
        if k == 0:
            record["seconds"] = round(time.time() - t0, 3)
            return record, None, None
        weights = feather_weights(mask)
        final = blend_pull(main, images[k], weights)
        record["clip_after"] = clip_share(final, mask)
        record["pane_median_after"] = round(masked_median(final, mask), 4)
        record["seconds"] = round(time.time() - t0, 3)
        return record, weights, final

    def alt_preview(self, cam, look: dict, result, pull: dict | None, weights, path: Path) -> int:
        """``<cam>_alt_preview.jpg``: the Render Result with ``--alt-look`` at the
        camera's EV; with a window pull the alt look is also saved at EV - k
        (the main image's k) and blended with the main image's weights."""
        scene, quality = self.ctx.scene, self.ctx.args.preview_quality
        alt = self.ctx.args.alt_look
        if weights is None:
            vs = scene.view_settings
            saved = (vs.look, vs.exposure)
            try:
                vs.look, vs.exposure = alt, float(look["ev"])
                return save_preview(scene, result, path, quality)
            finally:
                vs.look, vs.exposure = saved
        tmp = self.out / f".alt_{cam.name}.png"
        plain = save_display(scene, result, tmp, float(look["ev"]), look=alt)
        pulled = save_display(scene, result, tmp, float(look["ev"]) - int(pull["k"]), look=alt)
        try:
            write_png(tmp, blend_pull(plain, pulled, weights), DISPLAY_PNG_LEVEL)
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
    look = Look(scene, args, mood, windows, look_from, look_from_path)
    ctx = Context(scene, args, device, denoiser, (width, height), look, set(by_name), deadline)
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
