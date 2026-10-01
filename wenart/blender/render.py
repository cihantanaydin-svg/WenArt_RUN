"""Render the cameras of a built scene with Cycles (run inside Blender).

    blender -b outputs/<p>/scene/scene.blend --python wenart/blender/render.py -- \
        --cameras all|cam_a,cam_b --samples 256 --res 1920x1080 --out outputs/<p>/renders [--force]

Device: OPTIX, then CUDA, then CPU (printed as ``DEVICE=...``). Passes:
Combined, Depth (Z), Normal and Object Index (every proxy and opening has a
unique ``pass_index`` from the scene manifest). Files per camera:
``<cam>.png`` (RGB), ``<cam>_passes.exr`` (multilayer, half float, ZIP),
``<cam>_preview.jpg`` (<= 300 KB), plus ``<cam>_depth.png`` (16-bit, near
= dark) and ``<cam>_index.png`` (8-bit, pixel value = pass index) so tools
without an EXR reader can check the passes. ``render_manifest.json`` lists
camera, samples, device, seconds, the depth range and the index values seen,
the pass index table keyed by wenart id (identical to the scene manifest's)
and the scene fingerprint (``scene_sha256`` of ``scene.blend``).

Idempotent and resumable: the manifest is rewritten after every camera, so a
killed run keeps what it rendered. A camera is reused ("skipped") only when
its PNG, EXR and preview exist and its manifest entry carries the fingerprint
of the current scene.blend; its statistics are read again from the EXR and its
measured seconds are kept. Anything else (no entry, rebuilt scene, missing
file) is rendered again and the reason is printed. A ``--cameras`` subset
merges into the previous manifest; entries of cameras that no longer exist in
the scene are dropped with a warning. ``--force`` re-renders everything asked.

Why no compositor: Blender 5.x replaced ``scene.node_tree`` by
``compositing_node_group`` and reworked the File Output node; the multilayer
EXR output needs none of that, and the passes are read back with the OpenImageIO
module bundled with Blender (3.1 in 5.2.2).
"""
from __future__ import annotations

import argparse
import hashlib
import json
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="render.py")
    parser.add_argument("--out", required=True)
    parser.add_argument("--cameras", default="all")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--res", default=f"{DEFAULT_RES[0]}x{DEFAULT_RES[1]}")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu"])
    parser.add_argument("--no-denoise", action="store_true")
    return parser.parse_args(argv)


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
    return denoiser


def bpy_view_layer(scene):
    return scene.view_layers[0]


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


def read_passes(exr_path: Path, depth_png: Path, index_png: Path) -> tuple[dict | None, list[int]]:
    """Depth statistics and the set of object-index values of a multilayer EXR,
    plus the two helper PNGs. Uses Blender's bundled OpenImageIO."""
    try:
        import OpenImageIO as oiio
        import numpy as np
    except ImportError as exc:
        print(f"pass readback skipped: {exc}")
        return None, []
    inp = oiio.ImageInput.open(str(exr_path))
    if inp is None:
        print(f"pass readback failed: {oiio.geterror()}")
        return None, []
    # Collect every channel of every subimage (a multi-part EXR keeps each
    # layer in its own part; a single-part file has them all in part 0).
    channels: dict[str, object] = {}
    part = 0
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
    if not channels:
        return None, []

    def channel(*suffixes: str):
        for n, values in channels.items():
            if n.endswith(suffixes):
                return values
        return None

    depth = channel("Depth.Z")
    # Blender 5.2 names the pass "Object Index.X"; older builds wrote "IndexOB.X".
    index = channel("Object Index.X", "IndexOB.X")
    stats = None
    if depth is not None:
        valid = np.isfinite(depth) & (depth < DEPTH_BACKGROUND)
        if valid.any():
            d = depth[valid]
            stats = {"min": float(d.min()), "max": float(d.max()), "mean": float(d.mean()),
                     "coverage": float(valid.mean())}
            lo, hi = stats["min"], max(stats["max"], stats["min"] + 1e-6)
            norm = np.full(depth.shape, 65535, dtype=np.uint16)
            norm[valid] = np.clip((d - lo) / (hi - lo) * 65535.0, 0, 65535).astype(np.uint16)
            _write_png(oiio, depth_png, norm, "uint16")
        else:
            stats = {"min": 0.0, "max": 0.0, "mean": 0.0, "coverage": 0.0}
    values: list[int] = []
    if index is not None:
        rounded = np.rint(np.nan_to_num(index)).astype(np.int64)
        values = sorted(int(v) for v in np.unique(rounded) if v > 0)
        _write_png(oiio, index_png, np.clip(rounded, 0, 255).astype(np.uint8), "uint8")
    return stats, values


def _write_png(oiio, path: Path, array, dtype: str) -> None:
    import numpy as np

    h, w = array.shape
    spec = oiio.ImageSpec(w, h, 1, dtype)
    out = oiio.ImageOutput.create(str(path))
    if out is None:
        print(f"cannot create {path}: {oiio.geterror()}")
        return
    out.open(str(path), spec)
    # OIIO wants (height, width, channels); a 2-D array is read with the wrong stride.
    out.write_image(np.ascontiguousarray(array.reshape(h, w, 1)))
    out.close()


def scene_fingerprint(blend_path: str) -> str | None:
    """sha256 of the scene file; None when the scene is unsaved (no file to fingerprint)."""
    if not blend_path or not Path(blend_path).is_file():
        return None
    digest = hashlib.sha256()
    with open(blend_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pass_index_table(scene) -> dict[str, int]:
    """``{wenart_id: pass_index}`` of every object with an index, the table of the scene
    manifest (a door's frame and leaf share the id and the index, so one key each)."""
    table: dict[str, int] = {}
    for o in scene.objects:
        if o.pass_index > 0:
            key = o.get("wenart_id") or o.name
            table[key] = int(o.pass_index)
    return table


def load_previous(manifest_path: Path) -> dict[str, dict]:
    """Entries of the last render manifest keyed by camera; empty when absent or unreadable."""
    if not manifest_path.exists():
        return {}
    try:
        return {r["camera"]: r for r in json.loads(manifest_path.read_text(encoding="utf-8")).get("renders", [])}
    except (ValueError, KeyError, TypeError):
        return {}


def reuse_reason(cam_name: str, previous: dict | None, fingerprint: str | None, files: list[Path]) -> str | None:
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
    return None


def main(argv: list[str]) -> int:
    import bpy

    args = parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    width, height = (int(v) for v in args.res.lower().split("x"))
    scene = bpy.context.scene
    device = configure_device(scene, args.device)
    denoiser = configure_render(scene, args.samples, (width, height), device, not args.no_denoise)
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        pass

    all_cameras = [o for o in scene.objects if o.type == "CAMERA" and o.get("wenart_kind") == "camera"]
    all_cameras.sort(key=lambda o: o.name)
    cameras = all_cameras
    if args.cameras != "all":
        wanted = set(args.cameras.split(","))
        cameras = [o for o in all_cameras if o.name in wanted]
        missing = wanted - {o.name for o in cameras}
        if missing:
            print(f"unknown cameras: {sorted(missing)}")
            return 2
    if not cameras:
        print("no cameras to render")
        return 2

    fingerprint = scene_fingerprint(bpy.data.filepath)
    pass_index = pass_index_table(scene)
    manifest_path = out / "render_manifest.json"
    previous = load_previous(manifest_path)
    warnings: list[str] = []
    if fingerprint is None:
        warnings.append("scene has no file on disk: no fingerprint, every camera is rendered")

    # The manifest is cumulative: entries of cameras not asked for in this run are
    # carried over (a --cameras subset must not forget the others), entries of cameras
    # that no longer exist in the scene are dropped, and each one says what it is.
    scene_names = {o.name for o in all_cameras}
    run_names = {o.name for o in cameras}
    entries: dict[str, dict] = {}
    for name, entry in previous.items():
        if name not in scene_names:
            warnings.append(f"{name}: no such camera in the scene, manifest entry dropped")
            continue
        if name not in run_names and entry.get("scene_sha256") != fingerprint:
            warnings.append(f"{name}: rendered from another scene build and not asked for in this run")
        entries[name] = entry

    def write_manifest() -> None:
        manifest = {
            "schema_version": "0.1",
            "scene": bpy.data.filepath,
            "scene_sha256": fingerprint,
            "device": device,
            "device_requested": args.device,
            "blender_version": bpy.app.version_string,
            "samples": args.samples,
            "resolution": [width, height],
            "denoiser": denoiser,
            "pass_index": pass_index,
            "renders": [entries[name] for name in sorted(entries)],
            "warnings": warnings,
        }
        manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    write_manifest()
    n_rendered = n_skipped = 0
    for cam in cameras:
        png = out / f"{cam.name}.png"
        exr = out / f"{cam.name}_passes.exr"
        preview = out / f"{cam.name}_preview.jpg"
        depth_png = out / f"{cam.name}_depth.png"
        index_png = out / f"{cam.name}_index.png"
        prev = previous.get(cam.name)
        reason = "--force" if args.force else reuse_reason(cam.name, prev, fingerprint, [png, exr, preview])
        if reason is None:
            # Reuse: the statistics come from the EXR on disk (cheap), the time from the run that made it.
            stats, values = read_passes(exr, depth_png, index_png)
            if stats is None and prev.get("depth") is not None:
                stats, values = prev["depth"], list(prev.get("index_values", []))
                warnings.append(f"{cam.name}: pass readback failed, statistics copied from the previous manifest")
            entries[cam.name] = {
                "camera": cam.name, "png": png.name, "exr": exr.name, "preview": preview.name,
                "depth_png": depth_png.name if depth_png.exists() else None,
                "index_png": index_png.name if index_png.exists() else None,
                "preview_bytes": preview.stat().st_size, "seconds": prev["seconds"],
                "samples": prev.get("samples", args.samples), "resolution": prev.get("resolution", [width, height]),
                "depth": stats, "index_values": values, "skipped": True, "room_id": cam.get("wenart_room"),
                "scene_sha256": fingerprint,
            }
            n_skipped += 1
            write_manifest()
            print(f"SKIP {cam.name} (rendered from this scene, {prev['seconds']}s) depth={stats} indices={values}")
            continue
        if png.exists():
            print(f"RERENDER {cam.name}: {reason}")
        scene.camera = cam
        set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = str(exr)
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        seconds = time.time() - t0
        result = bpy.data.images.get("Render Result")
        set_output(scene, "PNG")
        result.save_render(str(png), scene=scene)
        preview_bytes = save_preview(scene, result, preview)
        stats, values = read_passes(exr, depth_png, index_png)
        entries[cam.name] = {
            "camera": cam.name, "png": png.name, "exr": exr.name, "preview": preview.name,
            "depth_png": depth_png.name if depth_png.exists() else None,
            "index_png": index_png.name if index_png.exists() else None,
            "preview_bytes": preview_bytes, "seconds": round(seconds, 2), "samples": args.samples,
            "resolution": [width, height], "depth": stats, "index_values": values, "skipped": False,
            "room_id": cam.get("wenart_room"), "scene_sha256": fingerprint,
        }
        n_rendered += 1
        write_manifest()   # after every camera: a killed run keeps what it rendered
        print(f"RENDERED {cam.name} in {seconds:.1f}s depth={stats} indices={values}")

    print(f"RENDER_DONE {out} cameras={len(cameras)} rendered={n_rendered} skipped={n_skipped} "
          f"listed={len(entries)} device={device}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if code:
        sys.exit(code)
