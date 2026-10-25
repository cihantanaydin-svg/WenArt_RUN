"""Top-down views of every level with the ceilings off (user request of 25 Oct 2026: "I want a top down view of all
the floor with the ceiling off that I can take a look and tell what is wrong").

What: ``blender -b <scene.blend> -P wenart/blender/topdown.py -- --out <dir> [--levels L-1,L0] [--res 1600]
[--samples 24] [--device CPU|GPU] [--tilt 35] [--azimuth 0]`` renders ``top_<level>.png`` per level and
``top_<level>.png.frame.json`` (the view's frame); ``python -m wenart.report.topdown_labels`` writes the room names
on them (``top_<level>_plan.jpg``, the name the pod job's results copy takes). ``scripts/jobs/full.sh`` makes them
after every run (``RUN_TOPDOWN=0`` skips it).

How: the views are angled (25 Oct 2026, user: "make the top down view a bit angled"): an orthographic camera
``TILT_DEG`` from straight down, looking north (``--tilt 0``: the plan). Every mesh crossing ``SECTION_M`` over the
floor is cut there by a Boolean difference (``section_cut``: an architect's cutaway; full-height walls hid the rooms
behind them) and every mesh whose lowest point lies above it is hidden (ceilings, slabs, upper floors, the roof,
ceiling lights), and so are the building copies, trees, hedges and grass (they cover the plan); the camera frames
the level's walls with ``PAD_M`` around them up to the cut; a sun from nearly overhead lights it.
"""
import argparse
import json
import sys

CUT_M = 2.2
PAD_M = 1.0
TILT_DEG = 35.0                 # 25 Oct 2026: the views are a bit angled (the walls and furniture show their height)
SECTION_M = 1.2                 # an angled view cuts the walls at this height over the floor (a cutaway)
HIDE_KINDS = {"ceiling", "roof", "site_decor", "site_decor_part", "vegetation_card", "atmosphere", "building_copy",
              "site_hedge", "site_grass", "light"}


def bbox(o):
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def section_cut(z: float) -> int:
    """Cut every rendered mesh that crosses height ``z`` (walls, doors, tall furniture) with a Boolean difference of a
    box over ``z`` (the angled views: an architect's cutaway; full-height walls hid the rooms behind them)."""
    import bpy

    cutter = bpy.data.objects.get("topdown_cutter")
    if cutter is None:
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cutter = bpy.context.active_object
        cutter.name = "topdown_cutter"
    cutter.scale = (2000.0, 2000.0, 1000.0)
    cutter.location = (0.0, 0.0, z + 500.0)
    cutter.hide_render = True
    cutter.display_type = "WIRE"
    n = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or o is cutter or o.name.startswith("topdown_"):
            continue
        lo, hi = bbox(o)
        if lo[2] < z < hi[2]:
            m = o.modifiers.new("topdown_section", "BOOLEAN")
            m.operation = "DIFFERENCE"
            m.solver = "FLOAT" if "FLOAT" in {i.identifier for i in m.bl_rna.properties["solver"].enum_items} \
                else "FAST"
            m.object = cutter
            n += 1
    return n


def render_level(level_id: str, elevation: float, out: str, res: int, samples: int, device: str,
                 tilt: float = 0.0, azimuth: float = 0.0) -> dict:
    import bpy
    from mathutils import Vector  # noqa: F401  (bbox)

    sc = bpy.context.scene
    cut = elevation + (SECTION_M if tilt > 0 else CUT_M)
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
        for m in [m for m in o.modifiers if m.name == "topdown_section"] if o.type == "MESH" else []:
            o.modifiers.remove(m)
    if tilt > 0:
        section_cut(elevation + SECTION_M)
    col = bpy.data.collections.get(f"level_{level_id}")
    walls = [o for o in (col.all_objects if col else []) if o.type == "MESH" and str(o.get("wenart_kind")) == "wall"]
    if not walls:
        return {}
    los, his = zip(*[bbox(o) for o in walls])
    x0, y0 = min(v[0] for v in los) - PAD_M, min(v[1] for v in los) - PAD_M
    x1, y1 = max(v[0] for v in his) + PAD_M, max(v[1] for v in his) + PAD_M
    import math
    from mathutils import Vector

    # 25 Oct 2026 (user: "make the top down view a bit angled"): an axonometric view, tilted ``tilt`` degrees from
    # straight down, looking toward ``azimuth`` (0 = north); the frame covers the level's box up to the cut height
    t, az = math.radians(tilt), math.radians(azimuth)
    view = Vector((math.sin(az) * math.sin(t), math.cos(az) * math.sin(t), -math.cos(t))).normalized()
    target = Vector(((x0 + x1) / 2.0, (y0 + y1) / 2.0, elevation))
    rot = view.to_track_quat("-Z", "Y")
    right, up = rot @ Vector((1.0, 0.0, 0.0)), rot @ Vector((0.0, 1.0, 0.0))
    corners = [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (elevation, cut)]
    us = [(c - target).dot(right) for c in corners]
    vs = [(c - target).dot(up) for c in corners]
    umin, umax, vmin, vmax = min(us), max(us), min(vs), max(vs)
    w, h = umax - umin, vmax - vmin
    cam = bpy.data.objects.get("topdown_camera")
    if cam is None:
        cam = bpy.data.objects.new("topdown_camera", bpy.data.cameras.new("topdown_camera"))
        sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(w, h)
    cam.data.clip_end = 500.0
    centre = target + right * ((umin + umax) / 2.0) + up * ((vmin + vmax) / 2.0)
    cam.location = centre - view * 60.0
    cam.rotation_euler = rot.to_euler()
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
             "w": sc.render.resolution_x, "h": sc.render.resolution_y, "tilt_deg": tilt, "azimuth_deg": azimuth,
             "target": list(target), "right": list(right), "up": list(up),
             "umin": umin, "umax": umax, "vmin": vmin, "vmax": vmax}
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
    ap.add_argument("--tilt", type=float, default=TILT_DEG, help="degrees from straight down (0 = a plan)")
    ap.add_argument("--azimuth", type=float, default=0.0, help="the view's direction, degrees from north")
    a = ap.parse_args(argv)
    from pathlib import Path
    Path(a.out).mkdir(parents=True, exist_ok=True)
    if a.device.upper() != "CPU":                  # the pod: OPTIX, then CUDA (render.configure_device)
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from wenart.blender.render import configure_device
        a.device = "GPU" if configure_device(bpy.context.scene, "auto") != "CPU" else "CPU"
    wanted = [x for x in a.levels.split(",") if x]
    levels = []
    for col in bpy.data.collections:
        if col.name.startswith("level_"):
            lid = col.name[len("level_"):]
            floors = [o for o in col.all_objects if o.type == "MESH" and str(o.get("wenart_kind")) == "floor"]
            if floors and (not wanted or lid in wanted):
                levels.append((lid, min(bbox(o)[0][2] for o in floors)))
    for lid, elev in sorted(levels, key=lambda x: x[1]):
        frame = render_level(lid, round(elev, 3), str(Path(a.out) / f"top_{lid}.png"), a.res, a.samples, a.device,
                             a.tilt, a.azimuth)
        print(f"TOPDOWN {lid} {frame.get('w')}x{frame.get('h')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []))
