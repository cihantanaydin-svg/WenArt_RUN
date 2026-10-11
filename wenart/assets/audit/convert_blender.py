"""OBJ -> GLB conversion of pod P4's new models in our Blender (docs/milestone12.md §6.4; Google Scanned Objects and
the Infinigen exports). Runs only inside Blender; imports nothing from ``wenart``:

    blender -b --factory-startup --python-exit-code 1 --python wenart/assets/audit/convert_blender.py -- <jobs.json>

``jobs.json``: ``{"jobs": [{"id", "src" (.obj), "dst" (.glb), "axes": [[up, forward], ...], "expect_dims": [x, y, z]
| null, "texture": png | null}], "result": path}``. Per job: the OBJ imported with the first axes (``wm.obj_import``
``up_axis`` / ``forward_axis``); when ``expect_dims`` is given (the size Infinigen measured in its own Z-up scene) and
the imported box differs by more than 2 % on an axis, the next axes are tried and the best match is kept; a
material without an image gets the job's ``texture`` as its base colour (a GSO .mtl whose map path does not
resolve); then ``export_scene.gltf`` (GLB, Y up as glTF wants: our importer turns it back to Z up). The record of
every job (ok, the axes used, the box, vertices, faces, images, seconds, error) goes to ``result``. A failed job is
recorded, never fatal.
"""
import json
import sys
import time
from pathlib import Path

import bpy  # noqa: F401  (Blender only)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    tmp.replace(path)


def meshes():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def box(objs):
    lo, hi = [1e30] * 3, [-1e30] * 3
    verts = faces = 0
    for ob in objs:
        mw = ob.matrix_world
        for v in ob.data.vertices:
            w = mw @ v.co
            for i in range(3):
                lo[i], hi[i] = min(lo[i], w[i]), max(hi[i], w[i])
        verts += len(ob.data.vertices)
        faces += len(ob.data.polygons)
    if not verts:
        return None, 0, 0
    return [round(hi[i] - lo[i], 4) for i in range(3)], verts, faces


def off_by(dims, expect):
    return max(abs(a - b) / max(b, 1e-3) for a, b in zip(dims, expect))


def load(src, up, forward):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=src, up_axis=up, forward_axis=forward)
    objs = meshes()
    if not objs:
        raise RuntimeError("no mesh in the OBJ")
    return objs


def image_ok(img):
    """An image with pixels: packed, loaded, or a file that exists (the OBJ importer makes a node for a missing
    map too)."""
    if img is None:
        return False
    if img.packed_file is not None or img.has_data:
        return True
    return bool(img.filepath) and Path(bpy.path.abspath(img.filepath)).is_file()


def fallback_texture(objs, texture):
    """The archive's texture as base colour of every material without a usable image (an image node whose file is
    missing gets it; else a new node on Base Color). Returns how many materials got it."""
    if not texture or not Path(texture).is_file():
        return 0
    img = bpy.data.images.load(texture, check_existing=True)
    n = 0
    for ob in objs:
        for slot in ob.material_slots:
            mat = slot.material
            if mat is None:
                continue
            try:
                mat.use_nodes = True
            except (AttributeError, TypeError):
                pass
            nt = mat.node_tree
            nodes = [nd for nd in nt.nodes if nd.type == "TEX_IMAGE"]
            if any(image_ok(nd.image) for nd in nodes):
                continue
            bsdf = next((nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED"), None)
            base = next((nd for nd in nodes
                         if any(lk.to_socket.name == "Base Color" for lk in nd.outputs["Color"].links)), None)
            if base is not None:
                base.image = img
            elif bsdf is not None:
                tex = nt.nodes.new("ShaderNodeTexImage")
                tex.image = img
                nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            else:
                continue
            n += 1
        if not ob.material_slots:
            mat = bpy.data.materials.new(f"{ob.name}_texture")
            ob.data.materials.append(mat)
            n += fallback_texture([ob], texture)
    return n


def images_of(objs):
    names = set()
    for ob in objs:
        for slot in ob.material_slots:
            nt = getattr(slot.material, "node_tree", None) if slot.material else None
            for nd in (nt.nodes if nt is not None else []):
                if nd.type == "TEX_IMAGE" and image_ok(nd.image):
                    names.add(nd.image.name)
    return len(names)


def one(job):
    tried = []
    best = None
    for up, forward in job.get("axes") or [["Y", "NEGATIVE_Z"]]:
        objs = load(job["src"], up, forward)
        dims, verts, faces = box(objs)
        err = off_by(dims, job["expect_dims"]) if dims and job.get("expect_dims") else 0.0
        tried.append({"up": up, "forward": forward, "dims": dims, "off": round(err, 4)})
        if best is None or err < best[0]:
            best = (err, up, forward)
        if err <= 0.02:
            break
    if (tried[-1]["up"], tried[-1]["forward"]) != (best[1], best[2]):
        objs = load(job["src"], best[1], best[2])
    objs = meshes()
    dims, verts, faces = box(objs)
    textured = fallback_texture(objs, job.get("texture"))
    dst = Path(job["dst"])
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.stem + ".part.glb")
    bpy.ops.export_scene.gltf(filepath=str(tmp), export_format="GLB", export_yup=True, use_selection=False,
                              export_apply=True)
    tmp.replace(dst)
    return {"ok": True, "up": best[1], "forward": best[2], "axes_off": round(best[0], 4), "tried": tried,
            "dims": dims, "vertices": verts, "faces": faces, "images": images_of(objs),
            "fallback_textures": textured, "bytes": dst.stat().st_size}


def main(jobs_path):
    doc = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    out = {"blender": bpy.app.version_string, "results": {}}
    failed = 0
    for job in doc.get("jobs") or []:
        t0 = time.time()
        try:
            rec = one(job)
        except Exception as exc:  # noqa: BLE001 - one broken model must not stop the others
            rec = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            failed += 1
        rec["seconds"] = round(time.time() - t0, 2)
        out["results"][job["id"]] = rec
        print(f"CONVERT {job['id']} {'ok' if rec.get('ok') else rec.get('error')} {rec['seconds']} s", flush=True)
        write_json(doc["result"], out)
    write_json(doc["result"], out)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1]))
