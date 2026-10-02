"""Render the cameras of a built scene with Cycles (run inside Blender).

    blender -b outputs/<p>/scene/scene.blend --python wenart/blender/render.py -- \
        --cameras all|cam_a,cam_b --samples 256 --res 1920x1080 --out outputs/<p>/renders [--force] \
        [--exposure auto|off|<EV>] [--exposure-target 0.9] [--white-balance auto|off|fixed:r,g,b] \
        [--look-from <render_manifest.json>] [--hide ID[,ID] [--plug]] [--hide-sets 'cam:id;cam:id+plug']

Device: OPTIX, then CUDA, then CPU (printed as ``DEVICE=...``). Passes:
Combined, Depth (Z), Normal and Object Index (every proxy and opening has a
unique ``pass_index`` from the scene manifest). Files per camera:
``<cam>.png`` (display-referred RGB8: AgX, look None, the camera's exposure
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
the wall hole of a hidden door or window with a box of the wall's first
material (pass index 0) and switches its portal off. ``--hide-sets`` renders
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
are dropped with a warning. ``--force`` re-renders everything asked.

Why no compositor: Blender 5.x replaced ``scene.node_tree`` by
``compositing_node_group`` and reworked the File Output node; the multilayer
EXR output needs none of that, and the passes are read back with the OpenImageIO
module bundled with Blender (3.1 in 5.2.2). Render Result pixels cannot be
read in background mode (5.2.2), so metering also goes through an EXR.
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
RENDER_CODE_VERSION = "m5.1"
PASSES = ("combined", "z", "normal", "object_index")
VIEW_TRANSFORM = "AgX"
LOOK = "None"

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
    return parser.parse_args(argv)


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


def render_key(settings: dict) -> str:
    """First 16 hex of sha256 over the canonical JSON of the render settings."""
    blob = json.dumps(settings, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def key_settings(samples: int, resolution, denoiser, exposure_mode: str, exposure_value, target: float,
                 wb_mode: str, wb_fixed, hidden, plugged, look_from_values: dict | None = None) -> dict:
    """What the render key covers (docs/milestone5.md §2.5). With
    ``look_from_values`` (``{"ev", "whitepoint"}`` of the source entry) the
    exposure and white balance are mode ``from`` with those values."""
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
    return {"samples": int(samples), "resolution": [int(v) for v in resolution], "denoiser": denoiser,
            "exposure": exposure, "white_balance": wb, "passes": list(PASSES),
            "hidden": sorted(hidden), "plugged": sorted(plugged), "code": RENDER_CODE_VERSION}


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


def configure_render(scene, samples: int, res: tuple[int, int], device: str, denoise: bool) -> str | None:
    """Samples, resolution, denoiser and the pass toggles. Returns the denoiser name."""
    scene.cycles.samples = samples
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
    _diffuse_passes(scene, False)
    # Data passes (depth, normal, index) are written at the first surface whose
    # alpha reaches this threshold: thin glass (alpha = Fresnel) is seen through.
    vl.pass_alpha_threshold = 0.5
    return denoiser


def bpy_view_layer(scene):
    return scene.view_layers[0]


def _diffuse_passes(scene, on: bool) -> None:
    vl = bpy_view_layer(scene)
    vl.use_pass_diffuse_direct = on
    vl.use_pass_diffuse_indirect = on
    vl.use_pass_diffuse_color = on


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


def save_preview(scene, result, path: Path) -> int:
    """JPEG preview under PREVIEW_MAX_BYTES (quality steps down until it fits)."""
    size = 0
    for quality in (85, 70, 55, 40, 30, 20):
        set_output(scene, "JPEG", quality)
        result.save_render(str(path), scene=scene)
        size = path.stat().st_size
        if size <= PREVIEW_MAX_BYTES:
            break
    return size


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


def write_png(path: Path, array) -> None:
    """Write a uint16 H x W (grey) or uint8 H x W x 3 (RGB) array as PNG with OpenImageIO.

    Raises RuntimeError when the file cannot be written: these maps are part
    of a finished render, a missing one must not pass unnoticed."""
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
    # OIIO wants (height, width, channels); a 2-D array is read with the wrong stride.
    if not out.open(str(path), oiio.ImageSpec(w, h, c, fmt)) or not out.write_image(a):
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

    def key_settings(self, cam_name: str, samples: int, res, denoiser, hidden, plugged) -> dict:
        values = self.look_from[cam_name] if self.look_from is not None else None
        return key_settings(samples, res, denoiser, self.exposure_mode, self.exposure_value, self.target,
                            self.wb_mode, self.wb_fixed, hidden, plugged, values)

    def decide(self, cam, out_dir: Path, res: tuple[int, int]) -> dict:
        """The exposure record of a camera before its final render (``window_clip_frac`` comes later)."""
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
        _diffuse_passes(scene, True)
        set_output(scene, "OPEN_EXR_MULTILAYER")
        r.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        channels = read_exr(tmp)
    finally:
        _diffuse_passes(scene, False)
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
        ob = common.new_mesh_object(f"plug_{wenart_id}", verts, faces, collection=self.scene.collection,
                                    wenart_id=f"plug:{wenart_id}", kind="wall", status="assumed",
                                    materials=[wall_ob.data.materials[0]])
        ob.pass_index = 0
        self.plugs.append(ob)
        # A plugged window lets no sky in: its portal would only waste samples.
        for o in self.scene.objects:
            if o.type == "LIGHT" and o.get("wenart_opening") == wenart_id and not o.hide_render:
                o.hide_render = True
                self.hidden_objects.append(o)
        info.update(wall_id=wall["wenart_id"], material=wall_ob.data.materials[0].name)
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
        run_names = {o.name for o in cameras}
        self.entries: dict[str, dict] = {}
        for name, entry in self.previous.items():
            if name not in ctx.camera_names:
                self.warnings.append(f"{name}: no such camera in the scene, manifest entry dropped")
                continue
            if name not in run_names and entry.get("scene_sha256") != ctx.fingerprint:
                self.warnings.append(f"{name}: rendered from another scene build and not asked for in this run")
            if name not in run_names and not entry.get("render_key"):
                self.warnings.append(f"{name}: stale entry (no render_key, rendered before Milestone 5) kept; "
                                     f"re-render it")
            self.entries[name] = entry
        self.rendered = self.skipped = 0

    def write_manifest(self) -> None:
        ctx = self.ctx
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
            "pass_index": ctx.pass_index,
            "renders": [self.entries[name] for name in sorted(self.entries)],
            "warnings": self.warnings,
        }
        self.manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    def files(self, cam_name: str) -> dict[str, Path]:
        o = self.out
        return {"png": o / f"{cam_name}.png", "exr": o / f"{cam_name}_passes.exr",
                "preview": o / f"{cam_name}_preview.jpg", "depth": o / f"{cam_name}_depth.png",
                "index": o / f"{cam_name}_index.png", "depth_mm": o / f"{cam_name}_depth_mm.png",
                "normal": o / f"{cam_name}_normal.png"}

    def key(self, cam) -> str:
        ctx = self.ctx
        return render_key(ctx.look.key_settings(cam.name, ctx.args.samples, ctx.res, ctx.denoiser,
                                                self.hidden, self.plugged))

    def check(self, cam) -> tuple[str | None, str]:
        """``(reason to render or None, render_key)``."""
        key = self.key(cam)
        f = self.files(cam.name)
        if self.ctx.args.force:
            return "--force", key
        needed = [f["png"], f["exr"], f["preview"], f["index"], f["depth_mm"], f["normal"]]
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
        preview_bytes = save_preview(scene, result, f["preview"])
        products = pass_products(read_exr(f["exr"]))
        if products["index"] is None or products["depth_mm"] is None or products["normal"] is None:
            raise RuntimeError(f"{cam.name}: the EXR lacks the index, depth or normal pass")
        write_png(f["index"], products["index"])
        write_png(f["depth_mm"], products["depth_mm"])
        write_png(f["normal"], products["normal"])
        if products["depth_legacy"] is not None:
            write_png(f["depth"], products["depth_legacy"])
        look["window_clip_frac"] = window_clip_frac(read_display_png(f["png"]), products["index"], ctx.windows)
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
        }
        self.rendered += 1
        self.write_manifest()   # after every camera: a killed run keeps what it rendered
        print(f"RENDERED {cam.name} in {seconds:.1f}s ev={look['ev']:+.3f} wb={look['wb_temperature']} "
              f"meter={look['meter_seconds']}s depth={products['depth']} indices={products['index_values']}")


class Context:
    """What every output folder of one Blender process shares."""

    def __init__(self, scene, args, device, denoiser, res, look: Look, camera_names: set[str]):
        import bpy

        self.scene = scene
        self.args = args
        self.device = device
        self.denoiser = denoiser
        self.res = res
        self.look = look
        self.camera_names = camera_names
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
    except (UsageError, ValueError) as exc:
        print(f"usage error: {exc}")
        return 2
    scene = bpy.context.scene

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
    denoiser = configure_render(scene, args.samples, (width, height), device, not args.no_denoise)
    scene.view_settings.view_transform = VIEW_TRANSFORM
    scene.view_settings.look = LOOK
    mood = scene.get("wenart_mood") or None
    windows = window_indices(scene)
    look = Look(scene, args, mood, windows, look_from, look_from_path)
    ctx = Context(scene, args, device, denoiser, (width, height), look, set(by_name))
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

    total = {"rendered": 0, "skipped": 0}
    for run, hide_set in runs:
        run.write_manifest()
        for cam in run.cameras:
            reason, key = run.check(cam)
            if reason is None:
                run.reuse(cam, key)
                continue
            if hide_set is not None:
                hider.apply(hide_set["ids"], hide_set["plug"])
            try:
                run.render(cam, key, reason)
            finally:
                if hide_set is not None:
                    hider.undo()
        total["rendered"] += run.rendered
        total["skipped"] += run.skipped
        print(f"RENDER_DONE {run.out} cameras={len(run.cameras)} rendered={run.rendered} skipped={run.skipped} "
              f"listed={len(run.entries)} device={device} hidden={run.hidden} plugged={run.plugged}")
    if sets is not None:
        print(f"HIDE_SETS_DONE sets={len(sets)} rendered={total['rendered']} skipped={total['skipped']}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if code:
        sys.exit(code)
