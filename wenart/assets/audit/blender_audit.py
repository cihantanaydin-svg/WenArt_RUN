"""Blender side of the audit render (docs/milestone12.md §6.1; jobs from ``render.py``). Runs only inside Blender:

    blender -b --factory-startup --python-exit-code 1 --python wenart/assets/audit/blender_audit.py -- <jobs.json>

What: per job: the floor, the grid, the person and the seat bar as boxes (``render.reference_layout``), the model
imported with ``unit_scale``, ``-origin_offset`` and the catalogue turn applied (the piece frame of the scene builder),
its mesh measured with ``meshstats.analyse`` (loaded by path: this file imports no ``wenart`` package) plus its
model-frame box, its texture images (count, largest size, missing files, a hash of the image data), then the four
views of ``render.camera_specs``. One ``measure/<id>.json`` per job (written also when the job fails); texture jobs
render a 1 m plane with the set's maps from above.

Why thin: everything that can be tested on the CPU lives in ``render.py`` and ``meshstats.py``; this file only talks
to bpy. Exit 3 when the deadline left jobs undone, else 0 (a failed model is recorded, never fatal).
"""
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import bpy  # noqa: F401  (Blender only)
import numpy as np
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("audit_meshstats", HERE / "meshstats.py")
meshstats = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(meshstats)

COLOURS = {"floor": (0.55, 0.55, 0.55), "grid": (0.12, 0.12, 0.12), "person": (0.25, 0.35, 0.55),
           "bar": (0.85, 0.45, 0.10)}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    tmp.replace(path)


def device(scene, requested="auto"):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    found = "CPU"
    if requested != "cpu":
        for dev_type in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                if [d for d in prefs.devices if d.type == dev_type]:
                    for d in prefs.devices:
                        d.use = d.type == dev_type
                    scene.cycles.device = "GPU"
                    found = dev_type
                    break
            except Exception as exc:  # noqa: BLE001 - no such backend here
                print(f"{dev_type} not usable: {exc}")
    if found == "CPU":
        scene.cycles.device = "CPU"
    return found


def material(name, rgb):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    try:
        mat.use_nodes = True
    except (AttributeError, TypeError):
        pass
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    mat.diffuse_color = (*rgb, 1.0)
    return mat


def cuboid(name, box, mat):
    (x0, y0, z0), (x1, y1, z1) = box["min"], box["max"]
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
             (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build_reference(layout):
    made = [cuboid("ref_floor", layout["floor"], material("ref_floor", COLOURS["floor"]))]
    for i, b in enumerate(layout["grid"]):
        made.append(cuboid(f"ref_grid_{i}", b, material("ref_grid", COLOURS["grid"])))
    for i, b in enumerate(layout["person"]):
        made.append(cuboid(f"ref_person_{i}", b, material("ref_person", COLOURS["person"])))
    for i, b in enumerate(layout["bar"]):
        made.append(cuboid(f"ref_bar_{i}", b, material("ref_bar", COLOURS["bar"])))
    return made


def image_info(meshes):
    images, missing, hashes, max_px = set(), [], [], 0
    for ob in meshes:
        for slot in ob.material_slots:
            mat = slot.material
            tree = getattr(mat, "node_tree", None) if mat is not None else None
            for node in (tree.nodes if tree is not None else []):
                if node.type != "TEX_IMAGE" or node.image is None or node.image.name in images:
                    continue
                img = node.image
                images.add(img.name)
                w, h = (int(v) for v in img.size)
                data = None
                if img.packed_file is not None:
                    data = bytes(img.packed_file.data)
                else:
                    path = Path(bpy.path.abspath(img.filepath)) if img.filepath else None
                    if path is not None and path.is_file():
                        data = path.read_bytes()
                if data is None or (w == 0 and h == 0):
                    missing.append(img.name)
                    continue
                max_px = max(max_px, w, h)
                hashes.append(hashlib.sha256(data).hexdigest())
    tex_hash = hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest() if hashes else None
    return {"images": len(images), "max_px": max_px, "missing": sorted(missing), "hash": tex_hash}


def mesh_arrays(meshes):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, tris, offset, colour_attrs = [], [], 0, 0
    for ob in meshes:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        try:
            me.calc_loop_triangles()
            n_v, n_t = len(me.vertices), len(me.loop_triangles)
            co = np.empty(n_v * 3, dtype=np.float32)          # the property's own type: the fast path
            me.vertices.foreach_get("co", co)
            co = co.reshape(-1, 3).astype(np.float64)
            mw = np.array(ob.matrix_world, dtype=np.float64)
            co = co @ mw[:3, :3].T + mw[:3, 3]
            tri = np.empty(n_t * 3, dtype=np.int32)
            me.loop_triangles.foreach_get("vertices", tri)
            verts.append(co)
            tris.append(tri.reshape(-1, 3).astype(np.int64) + offset)
            offset += n_v
            colour_attrs += len(getattr(me, "color_attributes", None) or [])
        finally:
            ev.to_mesh_clear()
    if not verts:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), 0
    return np.concatenate(verts), np.concatenate(tris), colour_attrs


def look(cam, spec):
    cam.location = spec["location"]
    direction = Vector(spec["target"]) - Vector(spec["location"])
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if spec["type"] == "ortho":
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = float(spec["ortho_scale"])
    else:
        cam.data.type = "PERSP"
        cam.data.lens = float(spec.get("lens_mm", 50))
    cam.data.clip_start = 0.01
    cam.data.clip_end = 1000.0


def clear(keep):
    for ob in [o for o in bpy.data.objects if o.name not in keep]:
        bpy.data.objects.remove(ob, do_unlink=True)
    try:
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except (AttributeError, TypeError):
        pass


def one(job, scene, cam, keep):
    before = {o.name for o in bpy.data.objects}
    if job["file"].lower().endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=job["file"], import_shading="NORMALS")
    new = [o for o in bpy.data.objects if o.name not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("no mesh objects in the file")
    for ob in new:
        if ob.type == "LIGHT":
            ob.hide_render = True
    root = bpy.data.objects.new("audit_root", None)
    scene.collection.objects.link(root)
    for ob in new:
        if ob.parent is None:
            ob.parent = root
    u = float(job["unit_scale"])
    off = Vector(job["origin_offset"])
    t = Matrix.Rotation(math.radians(job["rot_deg"]), 4, "Z") @ Matrix.Translation(-off) @ Matrix.Scale(u, 4)
    root.matrix_world = t
    bpy.context.view_layer.update()
    verts, tris, colour_attrs = mesh_arrays(meshes)
    stats = meshstats.analyse(verts, tris)
    if len(verts):
        inv = np.array(t.inverted(), dtype=np.float64)
        model = verts @ inv[:3, :3].T + inv[:3, 3]
        model = model * u                                   # metres in the model frame (raw x unit_scale)
        stats["model_box_min"] = [round(float(v), 4) for v in model.min(axis=0)]
        stats["model_box_max"] = [round(float(v), 4) for v in model.max(axis=0)]
    stats["textures"] = image_info(meshes)
    stats["colour_attributes"] = colour_attrs
    stats["mesh_objects"] = len(meshes)
    build_reference(job["layout"])
    for spec, path in zip(job["cameras"], job["views"]):
        look(cam, spec)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
    return stats


def texture_one(job, scene, cam):
    me = bpy.data.meshes.new("tex_plane")
    me.from_pydata([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [], [(0, 1, 2, 3)])
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    sw, sh = (float(v) or 1.0 for v in job["size_m"])
    for loop in me.loops:
        x, y, _ = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((x + 0.5) / sw, (y + 0.5) / sh)
    ob = bpy.data.objects.new("tex_plane", me)
    scene.collection.objects.link(ob)
    mat = bpy.data.materials.new("tex_mat")
    try:
        mat.use_nodes = True
    except (AttributeError, TypeError):
        pass
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    files = job["files"]
    alb = nt.nodes.new("ShaderNodeTexImage")
    alb.image = bpy.data.images.load(files["albedo"])
    nt.links.new(alb.outputs["Color"], bsdf.inputs["Base Color"])
    if files.get("roughness"):
        r = nt.nodes.new("ShaderNodeTexImage")
        r.image = bpy.data.images.load(files["roughness"])
        r.image.colorspace_settings.name = "Non-Color"
        nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
    if files.get("normal"):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(files["normal"])
        n.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    ob.data.materials.append(mat)
    look(cam, {"type": "ortho", "location": [0, 0, 5], "target": [0, 0, 0], "ortho_scale": 1.0})
    scene.render.filepath = job["out"]
    bpy.ops.render.render(write_still=True)


def main(jobs_path):
    doc = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    s = doc["settings"]
    deadline = doc.get("deadline")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    dev = device(scene, s.get("device", "auto"))
    scene.cycles.samples = int(s.get("samples", 24))
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = int(s.get("resolution", 512))
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    world = bpy.data.worlds.new("audit_world")
    scene.world = world
    try:
        world.use_nodes = True
    except (AttributeError, TypeError):      # always node-based in newer Blender versions
        pass
    grey = float(s.get("background", 0.75))
    tree = getattr(world, "node_tree", None)
    bg = next((n for n in tree.nodes if n.type == "BACKGROUND"), None) if tree is not None else None
    if bg is not None:
        bg.inputs["Color"].default_value = (grey, grey, grey, 1.0)
    else:
        world.color = (grey, grey, grey)
    cam = bpy.data.objects.new("audit_cam", bpy.data.cameras.new("audit_cam"))
    cam.data.sensor_width = float(s.get("sensor_mm", 36))
    scene.collection.objects.link(cam)
    scene.camera = cam
    sun = bpy.data.objects.new("audit_sun", bpy.data.lights.new("audit_sun", "SUN"))
    sun.data.energy = float(s.get("sun_energy", 3.0))
    sun.data.angle = math.radians(5.0)
    sun.rotation_euler = (math.radians(40), 0.0, math.radians(-30))
    scene.collection.objects.link(sun)
    keep = {o.name for o in bpy.data.objects}
    left = []
    for job in doc.get("jobs") or []:
        if deadline and time.time() >= float(deadline):
            left.append(job["id"])
            continue
        t0 = time.time()
        rec = {"id": job["id"], "job_sha": job["job_sha"], "ok": False, "device": dev,
               "attempts": int(job.get("attempt", 1))}
        try:
            rec.update(one(job, scene, cam, keep))
        except Exception as exc:  # noqa: BLE001 - one broken model must not stop the others
            rec["ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            clear(keep)
        rec["seconds"] = round(time.time() - t0, 2)
        write_json(job["measure"], rec)
        print(f"AUDIT {job['id']} {'ok' if rec.get('ok') else rec.get('error')} {rec['seconds']} s", flush=True)
    for job in doc.get("textures") or []:
        if deadline and time.time() >= float(deadline):
            left.append(job["id"])
            continue
        try:
            texture_one(job, scene, cam)
        except Exception as exc:  # noqa: BLE001
            print(f"TEXTURE {job['id']} failed: {exc}", flush=True)
        finally:
            clear(keep)
    write_json(Path(doc["work"]) / "jobs" / f"status_{doc.get('worker', 0)}.json",
               {"device": dev, "blender": bpy.app.version_string, "left": left})
    return 3 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1]))
