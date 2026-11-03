"""Blender side of ``wenart.assets.zip_inspect`` (the user's request of 3 Nov 2026: "take a look inside beds.zip and
tell me if we can use the models"). Runs only inside Blender; imports nothing from ``wenart``:

    blender -b --factory-startup --python-exit-code 1 --python wenart/assets/zip_blender.py -- <jobs.json>

``jobs.json``: ``{"mode": "convert" | "render", "jobs": [...], "result": path}``.

- ``convert``: per job ``{"id", "src", "dst"}``: the source file (.fbx, .obj, .dae, .blend, .stl, .ply, .3ds, .usd*,
  .gltf) opened or imported with Blender's own importer, then exported as GLB (``export_scene.gltf``, Y up as glTF
  wants). Record per job: ok, the importer, the objects, meshes, images, the error.
- ``render``: per job ``{"id", "src" (a fixed GLB: metres, Z up, origin at the floor centre), "out_front",
  "out_back"}``: the model on a grey floor with a 0.5 m checker, a sun and a sky, two 3/4 views (from -Y, the assumed
  front, and from +Y), Cycles on the GPU, 640 x 480. Record per job: ok, the box, seconds, the error.

A failed job is recorded, never fatal.
"""
import json
import math
import sys
import time
import traceback
from pathlib import Path

import bpy  # noqa: F401  (Blender only)
from mathutils import Vector


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    tmp.replace(path)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def meshes():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def box(objs):
    lo, hi = [1e30] * 3, [-1e30] * 3
    for ob in objs:
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    return lo, hi


def load(src: Path) -> str:
    ext = src.suffix.lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=str(src))
        return "open_mainfile"
    reset()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(src))
        return "import_scene.gltf"
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(src))
        return "import_scene.fbx"
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(src))
        return "wm.obj_import"
    if ext == ".stl":
        bpy.ops.wm.stl_import(filepath=str(src))
        return "wm.stl_import"
    if ext == ".ply":
        bpy.ops.wm.ply_import(filepath=str(src))
        return "wm.ply_import"
    if ext in (".usd", ".usda", ".usdc", ".usdz"):
        bpy.ops.wm.usd_import(filepath=str(src))
        return "wm.usd_import"
    if ext == ".dae":
        if hasattr(bpy.ops.wm, "collada_import"):
            bpy.ops.wm.collada_import(filepath=str(src))
            return "wm.collada_import"
        raise RuntimeError("this Blender has no COLLADA importer")
    if ext == ".3ds":
        if hasattr(bpy.ops.import_scene, "max3ds"):
            bpy.ops.import_scene.max3ds(filepath=str(src))
            return "import_scene.max3ds"
        raise RuntimeError("this Blender has no 3DS importer (an extension)")
    raise RuntimeError(f"no importer for {ext}")


def convert(job):
    src, dst = Path(job["src"]), Path(job["dst"])
    rec = {"id": job["id"], "src": job["src"], "ok": False}
    t0 = time.time()
    try:
        rec["importer"] = load(src)
        rec["objects"] = len(bpy.data.objects)
        rec["meshes"] = len(meshes())
        rec["images"] = len(bpy.data.images)
        if not meshes():
            raise RuntimeError("no mesh after import")
        dst.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(dst), export_format="GLB", use_visible=False,
                                  export_cameras=False, export_lights=False, export_yup=True)
        rec["ok"] = dst.is_file()
        rec["bytes"] = dst.stat().st_size if dst.is_file() else 0
    except Exception as exc:  # noqa: BLE001 - recorded, never fatal
        rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["trace"] = traceback.format_exc()[-800:]
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def gpu(scene):
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if [d for d in prefs.devices if d.type == dev_type]:
                for d in prefs.devices:
                    d.use = d.type == dev_type
                scene.cycles.device = "GPU"
                return dev_type
        except Exception:  # noqa: BLE001 - no such backend here
            pass
    scene.cycles.device = "CPU"
    return "CPU"


def floor_material():
    mat = bpy.data.materials.new("floor_checker")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    chk = nt.nodes.new("ShaderNodeTexChecker")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    chk.inputs["Scale"].default_value = 1.0        # object coords in metres: one square = 0.5 m
    chk.inputs["Color1"].default_value = (0.55, 0.55, 0.55, 1.0)
    chk.inputs["Color2"].default_value = (0.42, 0.42, 0.42, 1.0)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], chk.inputs["Vector"])
    nt.links.new(chk.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    return mat


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def render(job, device_note):
    rec = {"id": job["id"], "ok": False}
    t0 = time.time()
    try:
        reset()
        scene = bpy.context.scene
        bpy.ops.import_scene.gltf(filepath=str(job["src"]))
        objs = meshes()
        if not objs:
            raise RuntimeError("no mesh")
        lo, hi = box(objs)
        rec["box_m"] = [round(hi[i] - lo[i], 4) for i in range(3)]
        cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        size = max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], 0.3)
        bpy.ops.mesh.primitive_plane_add(size=max(8.0, size * 4), location=(cx, cy, min(lo[2], 0.0) - 0.001))
        bpy.context.active_object.data.materials.append(floor_material())
        world = bpy.data.worlds.new("w")
        scene.world = world
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.85, 0.88, 0.92, 1.0)
        world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
        sun.data.energy = 3.0
        sun.rotation_euler = (math.radians(50), 0.0, math.radians(35))
        scene.collection.objects.link(sun)
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
        cam.data.lens = 35
        scene.collection.objects.link(cam)
        scene.camera = cam
        scene.render.engine = "CYCLES"
        rec["device"] = device_note or gpu(scene)
        scene.cycles.samples = 48
        scene.cycles.use_denoising = True
        scene.render.resolution_x, scene.render.resolution_y = 640, 480
        scene.render.image_settings.file_format = "PNG"
        target = (cx, cy, (lo[2] + hi[2]) * 0.4)
        dist = size * 1.9
        for key, sign in (("out_front", -1.0), ("out_back", 1.0)):
            cam.location = (cx + sign * -0.55 * dist, cy + sign * 0.85 * dist, hi[2] + size * 0.55)
            look_at(cam, target)
            scene.render.filepath = str(job[key])
            bpy.ops.render.render(write_still=True)
        rec["ok"] = all(Path(job[k]).is_file() for k in ("out_front", "out_back"))
    except Exception as exc:  # noqa: BLE001 - recorded, never fatal
        rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["trace"] = traceback.format_exc()[-800:]
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def main(jobs_path):
    doc = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    out = []
    for job in doc["jobs"]:
        rec = convert(job) if doc["mode"] == "convert" else render(job, None)
        print(f"[zip_blender] {doc['mode']} {job['id']}: {'ok' if rec.get('ok') else rec.get('error')}", flush=True)
        out.append(rec)
        write_json(doc["result"], {"mode": doc["mode"], "records": out})
    write_json(doc["result"], {"mode": doc["mode"], "records": out, "done": True})


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv[0])
