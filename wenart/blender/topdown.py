"""Top-down views of every level with the ceilings off (user request of 25 Oct 2026: "I want a top down view of all
the floor with the ceiling off that I can take a look and tell what is wrong").

What: ``blender -b <scene.blend> -P wenart/blender/topdown.py -- --out <dir> [--levels L-1,L0] [--res 1600]
[--samples 24] [--device CPU|GPU]`` renders ``top_<level>.png`` per level from straight above (orthographic, north
up) and ``top_<level>.png.frame.json`` (the plan box the image covers); ``python -m wenart.report.topdown_labels``
writes the room names on them.

How: for each level everything whose lowest point lies over the level's floor + ``CUT_M`` is hidden (ceilings,
slabs, upper floors, the roof, ceiling lights), and so are the building copies, trees, hedges and grass (they cover
the plan); the camera frames the level's walls with ``PAD_M`` around them; a sun from nearly overhead lights it.
"""
import argparse
import json
import sys

CUT_M = 2.2
PAD_M = 1.0
HIDE_KINDS = {"ceiling", "roof", "site_decor", "site_decor_part", "vegetation_card", "atmosphere", "building_copy",
              "site_hedge", "site_grass", "light"}


def bbox(o):
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def render_level(level_id: str, elevation: float, out: str, res: int, samples: int, device: str) -> dict:
    import bpy
    from mathutils import Vector  # noqa: F401  (bbox)

    sc = bpy.context.scene
    cut = elevation + CUT_M
    for col in bpy.data.collections:
        col.hide_render = col.name in ("building_copies", "building_instance") or col.name.startswith("veg_")
    for o in bpy.data.objects:
        if o.name.startswith("topdown_"):
            continue
        if o.type == "LIGHT":
            o.hide_render = True
            continue
        if o.type not in ("MESH", "EMPTY", "CURVE"):
            continue
        hide = str(o.get("wenart_kind")) in HIDE_KINDS
        if not hide and o.type == "MESH":
            hide = bbox(o)[0][2] > cut
        o.hide_render = hide
    col = bpy.data.collections.get(f"level_{level_id}")
    walls = [o for o in (col.all_objects if col else []) if o.type == "MESH" and str(o.get("wenart_kind")) == "wall"]
    if not walls:
        return {}
    los, his = zip(*[bbox(o) for o in walls])
    x0, y0 = min(v[0] for v in los) - PAD_M, min(v[1] for v in los) - PAD_M
    x1, y1 = max(v[0] for v in his) + PAD_M, max(v[1] for v in his) + PAD_M
    w, h = x1 - x0, y1 - y0
    cam = bpy.data.objects.get("topdown_camera")
    if cam is None:
        cam = bpy.data.objects.new("topdown_camera", bpy.data.cameras.new("topdown_camera"))
        sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(w, h)
    cam.data.clip_end = 500.0
    cam.location = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, elevation + 40.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    sc.camera = cam
    sc.render.resolution_x = res if w >= h else int(res * w / h)
    sc.render.resolution_y = int(res * h / w) if w >= h else res
    sun = bpy.data.objects.get("topdown_sun")
    if sun is None:
        sun = bpy.data.objects.new("topdown_sun", bpy.data.lights.new("topdown_sun", "SUN"))
        sc.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.rotation_euler = (0.35, 0.25, 0.0)
    sun.hide_render = False
    sc.render.engine = "CYCLES"
    sc.cycles.device = device
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.use_border = False
    sc.view_settings.exposure = 0.0
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    frame = {"level_id": level_id, "elevation": elevation, "x0": x0, "y0": y0, "x1": x1, "y1": y1,
             "w": sc.render.resolution_x, "h": sc.render.resolution_y}
    with open(out + ".frame.json", "w", encoding="utf-8") as f:
        json.dump(frame, f)
    return frame


def main(argv) -> int:
    import bpy

    ap = argparse.ArgumentParser(description="top-down views of every level, ceilings off")
    ap.add_argument("--out", required=True)
    ap.add_argument("--levels", default="")
    ap.add_argument("--res", type=int, default=1600)
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--device", default="CPU")
    a = ap.parse_args(argv)
    from pathlib import Path
    Path(a.out).mkdir(parents=True, exist_ok=True)
    wanted = [x for x in a.levels.split(",") if x]
    levels = []
    for col in bpy.data.collections:
        if col.name.startswith("level_"):
            lid = col.name[len("level_"):]
            floors = [o for o in col.all_objects if o.type == "MESH" and str(o.get("wenart_kind")) == "floor"]
            if floors and (not wanted or lid in wanted):
                levels.append((lid, min(bbox(o)[0][2] for o in floors)))
    for lid, elev in sorted(levels, key=lambda x: x[1]):
        frame = render_level(lid, round(elev, 3), str(Path(a.out) / f"top_{lid}.png"), a.res, a.samples, a.device)
        print(f"TOPDOWN {lid} {frame.get('w')}x{frame.get('h')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
