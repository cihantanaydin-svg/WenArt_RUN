"""The 3D files of a finished project (Milestone 9, user request of 4 Oct 2026: "final results to give 3d files that
can be opened in blender").

Run inside Blender on the built scene (``python -m wenart.blender.cli export`` starts it)::

    blender -b <out>/scene/scene.blend --python wenart/blender/export.py -- --renders <out>/renders/render_manifest.json
        --out <out>/export --name <project> [--max-texture 1024] [--no-glb]

Steps:

1. The render settings of the final images: Cycles, the view transform and look of ``render.py`` (AgX, AgX - Punchy),
   1920 x 1080; every camera of the render manifest gets its metered exposure (``wenart_exposure_ev``) and white
   point (``wenart_whitepoint``) as custom properties, and the scene takes the first camera's exposure, so a render
   of that camera in Blender looks like the delivered image (the others: set ``Render > Color Management >
   Exposure`` to the camera's ``wenart_exposure_ev``).
2. Textures: every image whose longest side is above ``--max-texture`` pixels is scaled down in memory (the delivered
   files stay small enough to download); every image is packed into the .blend, so no path on the pod remains.
3. ``<out>/<name>.blend`` (compressed, packed) with a text block ``WENART_README`` (what is in the file, the cameras
   and their exposure, the evidence labels of the objects: custom properties ``wenart_*``).
4. ``<out>/<name>.glb`` (glTF binary: meshes with their modifiers applied, materials, JPEG textures, cameras and
   lights): opens in Blender (File > Import > glTF 2.0) and other 3D tools; procedural materials (wet-wall tiles)
   export as their base colour.
5. ``<out>/export_manifest.json``: the files with bytes and sha256, the images (scaled, packed), the cameras, the
   Blender version.

Pure helpers (``scaled_size``, ``readme_text``, ``manifest_doc``) run without Blender (tests).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

VIEW_TRANSFORM = "AgX"                   # = render.py VIEW_TRANSFORM / LOOK
LOOK = "AgX - Punchy"
RESOLUTION = (1920, 1080)
DEFAULT_MAX_TEXTURE = 1024
MANIFEST = "export_manifest.json"
README_NAME = "WENART_README"


def scaled_size(width: int, height: int, max_side: int) -> tuple[int, int] | None:
    """The size an image is scaled down to (longest side ``max_side``, aspect kept), or None when it is small
    enough (or ``max_side`` is 0: no scaling)."""
    if max_side <= 0 or max(width, height) <= max_side:
        return None
    s = max_side / float(max(width, height))
    return max(1, int(round(width * s))), max(1, int(round(height * s)))


def camera_looks(render_manifest: dict) -> dict:
    """``{camera name: {"ev", "whitepoint"}}`` of a render manifest's views (missing values left out)."""
    out = {}
    doc = render_manifest or {}
    for view in doc.get("renders") or doc.get("views") or doc.get("cameras") or []:
        if not isinstance(view, dict):
            continue
        name = view.get("camera") or view.get("name")
        exposure = view.get("exposure") or {}
        if not name:
            continue
        entry = {}
        if isinstance(exposure.get("ev"), (int, float)):
            entry["ev"] = float(exposure["ev"])
        wp = exposure.get("whitepoint")
        if isinstance(wp, (list, tuple)) and len(wp) >= 3:
            entry["whitepoint"] = [float(v) for v in wp[:3]]
        out[str(name)] = entry
    return out


def readme_text(name: str, cameras: dict, max_texture: int, files: list[str]) -> str:
    lines = [f"WenArt_RUN scene of project {name} (docs/milestone9.md).", "",
             "Built from the building JSON of the project: walls, doors, windows, floors and ceilings from the "
             "documents; furniture from the documents (or added by the AI layout in empty rooms); decor added by AI "
             "or by rule. Every object carries custom properties wenart_* (its element id, room, type, source and, "
             "for library models, the asset id); ATTRIBUTION.md of the results lists the credits of every model.",
             "",
             f"Render settings as the delivered images: Cycles, view transform {VIEW_TRANSFORM}, look '{LOOK}', "
             f"{RESOLUTION[0]} x {RESOLUTION[1]}. Each camera has its metered exposure in the custom property "
             "wenart_exposure_ev (set Render Properties > Color Management > Exposure to it before rendering that "
             "camera) and its white point in wenart_whitepoint.", "",
             f"Textures larger than {max_texture} px were scaled down for the download (0 = none); the renders of "
             "the results used the full textures.", "", "Cameras:"]
    for cam, look in sorted(cameras.items()):
        ev = look.get("ev")
        lines.append(f"- {cam}: exposure {ev:+.2f} EV" if isinstance(ev, float) else f"- {cam}: exposure not metered")
    lines += ["", "Files: " + ", ".join(files)]
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_doc(name: str, out: Path, files: dict, images: list[dict], cameras: dict, max_texture: int,
                 blender_version: str, warnings: list[str], seconds: float) -> dict:
    """``export_manifest.json``: per file its bytes and sha256 (missing files are listed as such)."""
    entries = {}
    for kind, fname in files.items():
        path = Path(out) / fname
        entries[kind] = ({"file": fname, "bytes": path.stat().st_size, "sha256": sha256_file(path)} if path.is_file()
                         else {"file": fname, "missing": True})
    return {"schema_version": "0.1", "kind": "wenart_export", "project": name, "files": entries,
            "max_texture": max_texture, "images": images, "images_scaled": sum(1 for i in images if i.get("scaled")),
            "images_packed": sum(1 for i in images if i.get("packed")), "cameras": cameras,
            "view_transform": VIEW_TRANSFORM, "look": LOOK, "resolution": list(RESOLUTION),
            "blender_version": blender_version, "warnings": warnings, "seconds": round(seconds, 2),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def parse_args(argv):
    p = argparse.ArgumentParser(prog="export.py")
    p.add_argument("--renders", default=None, help="render_manifest.json (per-camera exposure)")
    p.add_argument("--out", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--max-texture", type=int, default=DEFAULT_MAX_TEXTURE)
    p.add_argument("--no-glb", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:      # inside Blender
    import bpy

    t0 = time.time()
    args = parse_args(argv if argv is not None else (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    manifest = {}
    if args.renders and Path(args.renders).is_file():
        manifest = json.loads(Path(args.renders).read_text(encoding="utf-8"))
    elif args.renders:
        warnings.append(f"{args.renders} not found: cameras without their metered exposure")
    looks = camera_looks(manifest)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    try:
        scene.view_settings.view_transform = VIEW_TRANSFORM
        scene.view_settings.look = LOOK
    except TypeError as exc:                   # an older Blender without the look: keep its default
        warnings.append(f"view transform / look not set: {exc}")
    cameras = {}
    for ob in bpy.data.objects:
        if ob.type != "CAMERA":
            continue
        look = looks.get(ob.name, {})
        if "ev" in look:
            ob["wenart_exposure_ev"] = look["ev"]
        if "whitepoint" in look:
            ob["wenart_whitepoint"] = look["whitepoint"]
        cameras[ob.name] = look
    first_name = next(iter(looks), None)
    if first_name and first_name in bpy.data.objects:
        scene.camera = bpy.data.objects[first_name]
        look = looks.get(first_name, {})
        if "ev" in look:
            scene.view_settings.exposure = look["ev"]
        if "whitepoint" in look:                      # as render.py sets it
            try:
                scene.view_settings.use_white_balance = True
                scene.view_settings.white_balance_whitepoint = tuple(look["whitepoint"])
            except (AttributeError, TypeError) as exc:
                warnings.append(f"white balance not set: {exc}")

    images = []
    for img in bpy.data.images:
        if img.type not in ("IMAGE",) or img.source not in ("FILE", "GENERATED"):
            continue
        rec = {"name": img.name, "size": list(img.size), "scaled": False, "packed": False}
        try:
            target = scaled_size(int(img.size[0]), int(img.size[1]), args.max_texture)
            if target is not None and not img.is_float:
                img.scale(target[0], target[1])
                rec.update(scaled=True, scaled_to=list(target))
            # pack() of a changed (scaled) image packs its pixels again, in the image's own file format, in place of
            # an earlier packed copy (the GLB textures of the library models are packed on import); an image from a
            # file is packed from it.
            if rec["scaled"] or img.packed_file is None:
                img.pack()
            rec["packed"] = img.packed_file is not None
        except (RuntimeError, ReferenceError) as exc:
            warnings.append(f"image {img.name}: {exc}")
        images.append(rec)

    files = {"blend": f"{args.name}.blend"}
    readme = bpy.data.texts.get(README_NAME) or bpy.data.texts.new(README_NAME)
    readme.clear()
    names = [files["blend"]] + ([] if args.no_glb else [f"{args.name}.glb"])
    readme.write(readme_text(args.name, cameras, args.max_texture, names))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / files["blend"]), compress=True, relative_remap=True, copy=True)
    if not args.no_glb:
        files["glb"] = f"{args.name}.glb"
        try:
            bpy.ops.export_scene.gltf(filepath=str(out / files["glb"]), export_format="GLB", export_apply=True,
                                      export_extras=True, export_cameras=True, export_lights=True,
                                      export_image_format="JPEG", export_yup=True)
        except Exception as exc:  # noqa: BLE001 - the .blend is the main file; the glb failure is recorded
            warnings.append(f"glTF export failed: {type(exc).__name__}: {exc}")
    doc = manifest_doc(args.name, out, files, images, cameras, args.max_texture, bpy.app.version_string, warnings,
                       time.time() - t0)
    (out / MANIFEST).write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"EXPORT_OK {out / files['blend']} " + " ".join(f"{k}={v.get('bytes')}" for k, v in doc["files"].items()))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # noqa: BLE001 - Blender keeps running after an exception in --python
        import traceback
        traceback.print_exc()
        print(f"EXPORT_FAILED {type(exc).__name__}: {exc}")
        code = 1
    sys.exit(code)
