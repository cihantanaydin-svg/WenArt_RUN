"""Build the Blender scene from a building JSON (run inside Blender).

    blender -b --python wenart/blender/build.py -- --building outputs/<p>/building.json \
        --style outputs/<p>/style.json --assets assets --out outputs/<p>/scene \
        [--level L0] [--no-textures] [--preview-samples 16]

Writes into ``--out``: ``scene.blend``, ``scene.glb``, ``scene_manifest.json``
(every object with its wenart id, kind, status, the element evidence copied
from the JSON, material, textured/flat, assumed defaults; cameras with the
ids in their frustum; the pass-index table; door ray checks) and one
top-down orthographic PNG per level at 100 px/m (``level_<id>_top.png``).

Nothing is added, moved or removed relative to the JSON: walls, openings,
rooms and furniture come from the building file one to one; cameras and
lights are the only objects that are not elements and they carry
``wenart_status = assumed``.
"""
from __future__ import annotations

import argparse
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

# Style used when no --style is given or the file is missing (docs/milestone3.md §1).
DEFAULT_STYLE = {
    "source_text": "(default) Scandinavian, light oak floor, white walls, warm daylight",
    "floor": {"material": "wood_oak_light", "asset": "WoodFloor051"},
    "walls": {"material": "plaster_white", "asset": "Plaster001", "tint": [0.95, 0.94, 0.90]},
    "ceiling": {"material": "plaster_white"},
    "wet_floor": {"material": "tiles_light", "asset": "Tiles074"},
    "wet_walls": {"material": "tiles_light"},
    "trim": {"material": "painted_wood_white"},
    "door": {"material": "wood_oak_light"},
    "window_frame": {"material": "painted_metal_white"},
    "lighting": {"hdri": "kloppenheim_06", "sun_elevation_deg": 35, "sun_azimuth_deg": 210,
                 "sun_strength": 3.0, "colour_temperature_k": 5200, "mood": "warm daylight"},
    "matched_terms": [], "unmatched_terms": [], "warnings": [],
}
PREVIEW_PX_PER_M = 100
PREVIEW_MARGIN_M = 0.5


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="build.py")
    parser.add_argument("--building", required=True)
    parser.add_argument("--style")
    parser.add_argument("--assets")
    parser.add_argument("--out", required=True)
    parser.add_argument("--level", help="build only this level id")
    parser.add_argument("--no-textures", action="store_true", help="flat colours only")
    parser.add_argument("--preview-samples", type=int, default=16)
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--no-glb", action="store_true")
    return parser.parse_args(argv)


def load_style(path: str | None, warnings: list[str]) -> tuple[dict, str | None]:
    if not path:
        warnings.append("no --style given: default style profile assumed")
        return json.loads(json.dumps(DEFAULT_STYLE)), None
    p = Path(path)
    if not p.exists():
        warnings.append(f"style file {p} missing: default style profile assumed")
        return json.loads(json.dumps(DEFAULT_STYLE)), None
    style = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(style, list):  # profiles_from_brief output: render the first, note the others
        if len(style) > 1:
            warnings.append(f"style file lists {len(style)} profiles; the first is used")
        style = style[0]
    for key, value in DEFAULT_STYLE.items():
        style.setdefault(key, json.loads(json.dumps(value)))
    return style, str(p)


def load_assets(assets_dir: str | None, no_textures: bool, warnings: list[str]) -> tuple[dict, dict]:
    """``(textures, hdris)`` from ``<assets>/manifest.json`` (empty when absent)."""
    if no_textures or not assets_dir:
        if not no_textures:
            warnings.append("no --assets given: flat colours and sky lighting")
        return {}, {}
    manifest = Path(assets_dir) / "manifest.json"
    if not manifest.exists():
        warnings.append(f"assets manifest {manifest} missing: flat colours and sky lighting")
        return {}, {}
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return data.get("textures", {}) or {}, data.get("hdris", {}) or {}


def hdri_file(hdris: dict, assets_dir: str | None, style: dict) -> str | None:
    wanted = (style.get("lighting") or {}).get("hdri")
    entry = hdris.get(wanted) if wanted else None
    if not entry:
        return None
    path = Path(entry.get("file", ""))
    if not path.is_absolute() and assets_dir:
        path = Path(assets_dir) / path
    return str(path) if path.exists() else None


def main(argv: list[str]) -> int:
    import bpy

    from wenart.blender import cameras as cams
    from wenart.blender import common, lighting, proxies, shell
    from wenart.blender.materials import MaterialLibrary
    from wenart.blender.render import configure_device

    args = parse_args(argv)
    t0 = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    building = json.loads(Path(args.building).read_text(encoding="utf-8"))
    if building.get("status") != "ok":
        print(f"building status is {building.get('status')!r}: nothing to build (needs review first)")
        return 2
    warnings: list[str] = list(building.get("warnings", []))
    style, style_path = load_style(args.style, warnings)
    textures, hdris = load_assets(args.assets, args.no_textures, warnings)
    hdri = hdri_file(hdris, args.assets, style)
    if (style.get("lighting") or {}).get("hdri") and hdri is None and not args.no_textures:
        warnings.append(f"HDRI {style['lighting'].get('hdri')} not available: physical sky used")

    levels = [lv for lv in building["levels"] if args.level is None or lv["id"] == args.level]
    if not levels:
        print(f"no level {args.level!r} in {args.building}")
        return 2

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = building["project"]["id"]
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    library = MaterialLibrary(textures, args.assets, use_textures=not args.no_textures)

    manifest_objects: list[dict] = []
    assumed: list[dict] = []
    pass_indices: dict[str, int] = {}
    camera_plans: list[dict] = []
    checks: dict = {"door_rays": []}
    level_collections = {}

    for level in levels:
        col = common.get_or_make_collection(f"level_{level['id']}")
        level_collections[level["id"]] = col
        shell.build_walls(building, level, col, library, style, manifest_objects, assumed, warnings)
        shell.build_openings(building, level, col, library, style, pass_indices, manifest_objects, assumed, warnings)
        shell.build_floors_ceilings(building, level, col, library, style, manifest_objects, warnings)
        proxies.create_proxies(building, level, col, {
            "proxy": library.proxy("proxy"), "proxy_glass": library.proxy("proxy_glass"),
            "proxy_unverified": library.proxy("proxy_unverified")}, pass_indices, manifest_objects, assumed)
        plans = cams.plan_cameras(building, level["id"])
        cams.create_cameras(plans, col, manifest_objects)
        camera_plans.extend(plans)
        for plan in plans:
            if plan.get("warning"):
                warnings.append(f"{plan['name']}: {plan['warning']}")
        bpy.context.view_layer.update()
        checks["door_rays"].extend(shell.door_ray_checks(building, level, scene))
        if level.get("ceiling_height_source") == "assumed_default":
            assumed.append({"object": f"level_{level['id']}", "field": "ceiling_height",
                            "value": level["ceiling_height"], "reason": "building JSON: assumed_default"})

    light_col = common.get_or_make_collection("lighting")
    light_info = lighting.build_lighting(building, levels, style, hdri, light_col, manifest_objects, assumed)

    previews = {}
    if not args.no_preview:
        configure_device(scene, "cpu" if os.environ.get("WENART_PREVIEW_CPU") else "auto")
        for level in levels:
            png = out / f"level_{level['id']}_top.png"
            render_top_down(scene, building, level, level_collections, png, args.preview_samples)
            previews[level["id"]] = png.name

    if camera_plans:
        scene.camera = bpy.data.objects.get(camera_plans[0]["name"])
    scene.render.resolution_x, scene.render.resolution_y = cams.RESOLUTION
    scene.render.resolution_percentage = 100

    blend = out / "scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    files = {"blend": blend.name}
    if not args.no_glb:
        glb = out / "scene.glb"
        try:
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True,
                                      export_extras=True, export_cameras=True, export_lights=True,
                                      export_image_format="JPEG", export_yup=True)
            files["glb"] = glb.name
        except Exception as exc:  # noqa: BLE001 - the export must not break the build
            warnings.append(f"glTF export failed: {exc}")

    manifest = {
        "schema_version": "0.1",
        "project": building["project"]["id"],
        "building": str(Path(args.building)),
        "style": style_path,
        "style_profile": style,
        "blender_version": bpy.app.version_string,
        "textures_enabled": not args.no_textures,
        "assets_dir": args.assets,
        "levels": [{"id": lv["id"], "label": lv.get("label"), "elevation": lv["elevation"],
                    "ceiling_height": lv["ceiling_height"], "ceiling_height_source": lv.get("ceiling_height_source")}
                   for lv in levels],
        "objects": manifest_objects,
        "cameras": camera_plans,
        "materials": library.records,
        "lighting": light_info,
        "pass_index": pass_indices,
        "assumed": assumed,
        "warnings": warnings,
        "checks": checks,
        "previews": previews,
        "files": files,
        "seconds": round(time.time() - t0, 1),
    }
    (out / "scene_manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    kinds = {}
    for o in manifest_objects:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print(f"BUILD_DONE {out} objects={kinds} cameras={len(camera_plans)} warnings={len(warnings)} "
          f"seconds={manifest['seconds']}")
    return 0


def render_top_down(scene, building: dict, level: dict, level_collections: dict, png: Path, samples: int) -> None:
    """Orthographic top view of one level at 100 px/m: ceilings and other
    levels hidden for the shot, then restored."""
    import bpy

    from wenart import geometry as G
    from wenart.blender import common

    walls = [w for w in building["walls"] if w["level_id"] == level["id"]]
    pts = [w["start"] for w in walls] + [w["end"] for w in walls]
    for r in building["rooms"]:
        if r["level_id"] == level["id"]:
            pts.extend(r["polygon"])
    if not pts:
        return
    x0, y0, x1, y1 = G.bbox(pts)
    x0 -= PREVIEW_MARGIN_M
    y0 -= PREVIEW_MARGIN_M
    x1 += PREVIEW_MARGIN_M
    y1 += PREVIEW_MARGIN_M
    w_m, h_m = x1 - x0, y1 - y0
    cam = bpy.data.cameras.new("top_preview")
    cam.type = "ORTHO"
    cam.ortho_scale = max(w_m, h_m)
    cam.clip_start = 0.1
    cam.clip_end = 100.0
    ob = bpy.data.objects.new("top_preview", cam)
    top_z = float(level["elevation"]) + float(level["ceiling_height"])
    ob.location = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top_z + 10.0)
    ob.rotation_euler = (0.0, 0.0, 0.0)  # looking down -Z, image up = +Y (north)
    scene.collection.objects.link(ob)

    hidden = []
    for lid, col in level_collections.items():
        for o in col.objects:
            if lid != level["id"] or o.get("wenart_kind") == "ceiling":
                if not o.hide_render:
                    o.hide_render = True
                    hidden.append(o)
    old = (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath,
           scene.cycles.samples, scene.render.image_settings.file_format, scene.render.image_settings.color_mode)
    scene.camera = ob
    scene.render.resolution_x = max(16, int(math.ceil(w_m * PREVIEW_PX_PER_M)))
    scene.render.resolution_y = max(16, int(math.ceil(h_m * PREVIEW_PX_PER_M)))
    scene.render.resolution_percentage = 100
    scene.render.engine = "CYCLES"
    scene.cycles.samples = max(1, samples)
    scene.cycles.use_denoising = samples >= 8
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath,
     scene.cycles.samples, scene.render.image_settings.file_format, scene.render.image_settings.color_mode) = old
    for o in hidden:
        o.hide_render = False
    common.delete_object(ob)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if code:
        sys.exit(code)
