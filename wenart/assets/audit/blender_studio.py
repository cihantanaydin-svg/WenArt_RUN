"""Blender side of the ranking studio (31 Oct 2026, lesson UL217; jobs from ``studio.plan``). Runs only inside Blender:

    blender -b --factory-startup --python-exit-code 1 --python wenart/assets/audit/blender_studio.py -- <jobs.json>

What: one studio for every model: a seamless light floor and backdrop (a cyclorama), a soft key, fill and top light,
a dim neutral world. Per job: the model built by the scene builder itself (``furniture.create_furniture`` on a one-piece
building: the fit's asset record, the file's own shading, a bed frame's bedding, a soft seat's fabric dressing), the
front 3/4 camera of ``studio.camera`` on the built box, one PNG. One record per job (``measure`` path, ``render.
run_render``'s resume): ok, the build method (``library``; a fallback to the parametric family is recorded and the
image is not written: the user ranks the model, never our fallback), warnings, the box, seconds.

Why thin: the camera and the plan are pure (``studio.py``, CPU tests); this file talks to bpy and the scene builder.
Exit 3 when the deadline left jobs undone, else 0 (a failed model is recorded, never fatal).
"""
import json
import math
import os
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("WENART_REPO_ROOT") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(REPO))

import bpy  # noqa: E402,F401  (Blender only)
from mathutils import Vector  # noqa: E402

from wenart.assets.audit import studio as S  # noqa: E402


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
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


def matte(name, rgb, roughness=0.85):
    mat = bpy.data.materials.new(name)
    try:
        mat.use_nodes = True
    except (AttributeError, TypeError):
        pass
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def cyclorama(rgb):
    """Floor y in [-30, 6], a quarter-circle cove of radius 3 m up to a back wall at y = 9 m, 60 m wide."""
    verts, faces = [], []
    xs = (-30.0, 30.0)
    profile = [(-30.0, 0.0), (6.0, 0.0)]
    for k in range(1, 13):
        a = math.radians(90.0 * k / 12.0)
        profile.append((6.0 + 3.0 * math.sin(a), 3.0 - 3.0 * math.cos(a)))
    profile.append((9.0, 25.0))
    for y, z in profile:
        verts += [(xs[0], y, z), (xs[1], y, z)]
    for i in range(len(profile) - 1):
        a, b = 2 * i, 2 * i + 2
        faces.append((a, a + 1, b + 1, b))
    me = bpy.data.meshes.new("studio_cyc")
    me.from_pydata(verts, [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("studio_cyc", me)
    ob.data.materials.append(matte("studio_floor", rgb))
    bpy.context.scene.collection.objects.link(ob)
    return ob


def area_light(name, location, target, energy, size):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.size = size
    light.color = (1.0, 0.98, 0.95)
    ob = bpy.data.objects.new(name, light)
    ob.location = location
    ob.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(ob)
    return ob


def studio(scene, s):
    world = bpy.data.worlds.new("studio_world")
    scene.world = world
    try:
        world.use_nodes = True
    except (AttributeError, TypeError):
        pass
    g = float(s.get("world", 0.42))
    tree = getattr(world, "node_tree", None)
    bg = next((n for n in tree.nodes if n.type == "BACKGROUND"), None) if tree is not None else None
    if bg is not None:
        bg.inputs["Color"].default_value = (g, g, g, 1.0)
    cyclorama(tuple(s.get("floor_rgb", (0.72, 0.70, 0.67))))
    cam = bpy.data.objects.new("studio_cam", bpy.data.cameras.new("studio_cam"))
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = float(s.get("sensor_mm", 36.0))
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def place_lights(box_min, box_max):
    """Key (front left, high), fill (front right, low), top and rim: sized and placed on the model's box."""
    c = [(a + b) / 2.0 for a, b in zip(box_min, box_max)]
    r = max(0.6, 0.5 * math.dist(box_min, box_max))
    made = [area_light("studio_key", (c[0] - 2.6 * r, c[1] - 3.2 * r, c[2] + 3.0 * r), c, 330.0 * r * r, 2.4 * r),
            area_light("studio_fill", (c[0] + 3.2 * r, c[1] - 2.4 * r, c[2] + 1.2 * r), c, 110.0 * r * r, 3.0 * r),
            area_light("studio_top", (c[0], c[1], c[2] + 4.0 * r), c, 120.0 * r * r, 3.0 * r),
            area_light("studio_rim", (c[0] + 1.5 * r, c[1] + 3.5 * r, c[2] + 2.5 * r), c, 90.0 * r * r, 1.6 * r)]
    return made


def look(cam, spec):
    cam.location = spec["location"]
    cam.rotation_euler = (Vector(spec["target"]) - Vector(spec["location"])).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "PERSP"
    cam.data.lens = float(spec["lens_mm"])
    cam.data.clip_start = 0.01
    cam.data.clip_end = 500.0


def world_box(objects):
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objects:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        for corner in ev.bound_box:
            w = ob.matrix_world @ Vector(corner)
            for i in range(3):
                lo[i], hi[i] = min(lo[i], w[i]), max(hi[i], w[i])
    if lo[0] == math.inf:
        raise RuntimeError("nothing built")
    return lo, hi


def prop_box(spec, name):
    """A studio prop of ``studio.decor_stage`` (a plinth, a backdrop wall, a ceiling panel): a plain matte box, never
    part of the framed model; a prop with ``shadow`` false casts none (a ceiling panel over a light)."""
    (x0, y0, z0), (x1, y1, z1) = spec["min"], spec["max"]
    verts = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(matte(f"{name}_mat", tuple(spec.get("rgb") or (0.8, 0.8, 0.8))))
    if not spec.get("shadow", True):
        try:
            ob.visible_shadow = False
        except AttributeError:
            pass
    bpy.context.scene.collection.objects.link(ob)
    return ob


def one_decor(job, doc, scene, cam, library):
    """A decor or extras model on its stage (``job["stage"]``, ``studio.decor_stage``): the props, then the item built
    by the scene builder itself (``furniture.create_furniture`` on a building with that one decor item and no piece:
    ``_create_decor`` / ``_create_wall_art``, the fit's asset at the model's own size, the file's own materials; a
    pendant's cord and canopy up to the stage's ceiling), the stage's camera on the built box (model and cord)."""
    from wenart.blender import furniture as F

    stage = job["stage"]
    col = bpy.data.collections.new("studio_piece")
    scene.collection.children.link(col)
    props = [prop_box(p, f"studio_{p['kind']}_{i}") for i, p in enumerate(stage.get("props") or [])]
    level = {"id": "L0", "elevation": 0.0, "elevation_m": 0.0, "height": 6.0, "height_m": 6.0, "name": "studio",
             "ceiling_height": float(stage["ceiling_m"])}
    item = stage["item"]
    building = {"project": {"id": "studio"}, "levels": [level], "rooms": [], "walls": [], "openings": [],
                "furniture": [], "decor": [item]}
    assumed, warnings, manifest = [], [], []
    style = job.get("style") or doc.get("style") or {}
    summary = F.create_furniture(building, level, col, library, style, doc.get("assets"), {},
                                 manifest, assumed, warnings)
    entry = next((m for m in manifest if m.get("decor_id") == item["id"] or m.get("wenart_id") == item["id"]), {})
    method = entry.get("method") or "?"
    rec = {"method": method, "fallback_reason": entry.get("fallback_reason"), "warnings": warnings[:20],
           "stage": stage["kind"], "skipped": summary.get("decor_skipped") or [],
           "hang": entry.get("hang"), "mount": entry.get("mount")}
    if method != "library":                     # the user ranks the model, never our fallback
        rec["error"] = f"not built as asked: {method}" + (
            f" ({rec['skipped'][0].get('reason')})" if rec["skipped"] else "")
        return rec, col, props
    lo, hi = world_box(list(col.all_objects))
    rec["box_min"], rec["box_max"] = [round(v, 4) for v in lo], [round(v, 4) for v in hi]
    lights = place_lights(lo, hi)
    spec = S.camera(lo, hi, dict(doc["settings"], **(stage.get("camera") or {})))
    look(cam, spec)
    rec["camera"] = spec
    scene.render.filepath = job["image"]
    Path(job["image"]).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    rec["ok"] = Path(job["image"]).is_file()
    return rec, col, props + lights


def one(job, doc, scene, cam, library, keep):
    from wenart.blender import furniture as F

    if job.get("stage"):                        # 31 Oct 2026: the remaining batch's decor and extras models
        return one_decor(job, doc, scene, cam, library)
    col = bpy.data.collections.new("studio_piece")
    scene.collection.children.link(col)
    level = {"id": "L0", "elevation": 0.0, "elevation_m": 0.0, "height": 6.0, "height_m": 6.0, "name": "studio"}
    piece = job["piece"]
    building = {"project": {"id": "studio"}, "levels": [level], "rooms": [], "walls": [], "openings": [],
                "furniture": [piece], "decor": []}
    assumed, warnings, manifest = [], [], []
    style = job.get("style") or doc.get("style") or {}
    summary = F.create_furniture(building, level, col, library, style, doc.get("assets"), {},
                                 manifest, assumed, warnings)
    entry = next((m for m in manifest if m.get("wenart_id") == piece["id"] or m.get("id") == piece["id"]), {})
    method = entry.get("method") or "?"
    rec = {"method": method, "fallback_reason": entry.get("fallback_reason"), "warnings": warnings[:20],
           "dressing": {k: bool(entry.get(k)) for k in ("bedding", "fabric_dressing", "recolour") if k in entry},
           "not_built": summary.get("not_built") or []}
    objects = list(col.all_objects)
    ours = bool(job.get("procedural"))          # our build: parametric or module is the point
    if (method != "library" and not ours) or (ours and not str(method).startswith(("parametric", "module"))):
        rec["error"] = f"not built as asked: {method}"
        return rec, col, []
    lo, hi = world_box(objects)
    rec["box_min"], rec["box_max"] = [round(v, 4) for v in lo], [round(v, 4) for v in hi]
    lights = place_lights(lo, hi)
    spec = S.camera(lo, hi, doc["settings"])
    look(cam, spec)
    rec["camera"] = spec
    scene.render.filepath = job["image"]
    Path(job["image"]).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    rec["ok"] = Path(job["image"]).is_file()
    return rec, col, lights


def clear(col, extra):
    for ob in list(col.all_objects) + list(extra):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(col)
    try:
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except (AttributeError, TypeError):
        pass


def main(jobs_path):
    doc = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    s = doc["settings"]
    deadline = doc.get("deadline")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    dev = device(scene, s.get("device", "auto"))
    scene.cycles.samples = int(s.get("samples", 96))
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = int(s.get("resolution", 640))
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except (TypeError, AttributeError):
        pass
    cam = studio(scene, s)
    from wenart.blender.build import load_assets
    from wenart.blender.materials import MaterialLibrary
    warnings = []
    textures, _hdris, refused = load_assets(doc.get("assets"), False, warnings)

    def new_library(style=None):
        """A fresh material library per model: the purge after each model removes the materials the last one made
        (pod run 20261031-070545: 48 beds failed on a removed bedding material of a reused library)."""
        return MaterialLibrary(textures, doc.get("assets"), use_textures=True, refused=refused,
                               style=style or doc.get("style") or {})
    keep = {o.name for o in bpy.data.objects}
    left = []
    for job in doc.get("jobs") or []:
        if deadline and time.time() >= float(deadline):
            left.append(job["id"])
            continue
        t0 = time.time()
        rec = {"id": job["id"], "job_sha": job["job_sha"], "ok": False, "device": dev,
               "attempts": int(job.get("attempt", 1))}
        col, extra = None, []
        try:
            out, col, extra = one(job, doc, scene, cam, new_library(job.get("style")), keep)
            rec.update(out)
        except Exception as exc:  # noqa: BLE001 - one broken model must not stop the others
            rec["ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"
            col = bpy.data.collections.get("studio_piece")
        finally:
            if col is not None:
                clear(col, extra)
            for ob in [o for o in bpy.data.objects if o.name not in keep]:
                bpy.data.objects.remove(ob, do_unlink=True)
        rec["seconds"] = round(time.time() - t0, 2)
        write_json(job["measure"], rec)
        print(f"STUDIO {job['id']} {'ok' if rec.get('ok') else rec.get('error')} {rec['seconds']} s", flush=True)
    write_json(Path(doc["work"]) / "jobs" / f"status_{doc.get('worker', 0)}.json",
               {"device": dev, "blender": bpy.app.version_string, "left": left})
    return 3 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1]))
