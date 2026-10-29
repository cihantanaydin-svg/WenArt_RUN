"""Top-down views of every level with the ceilings off (user request of 25 Oct 2026: "I want a top down view of all
the floor with the ceiling off that I can take a look and tell what is wrong").

What: ``blender -b <scene.blend> -P wenart/blender/topdown.py -- --out <dir> [--levels L-1,L0] [--res 1600]
[--samples 24] [--device CPU|GPU] [--tilt 35] [--azimuth 225]`` renders ``top_<level>.png`` per level and
``top_<level>.png.frame.json`` (the view's frame); ``python -m wenart.report.topdown_labels`` writes the room names
on them (``top_<level>_plan.jpg``, the name the pod job's results copy takes). ``scripts/jobs/full.sh`` makes them
after every run (``RUN_TOPDOWN=0`` skips it).

How: the views are angled (25 Oct 2026, user: "make the top down view a bit angled"): an orthographic camera
``TILT_DEG`` from straight down; since the user's note of 25 Oct 2026 ("a better angle from right up to left down and
halved the walls preventing the views") it stands at the plan's upper right (north-east) and looks to the lower left
(``AZIMUTH_DEG`` 225: south-west). The walls, doors, windows and railings (``CUT_KINDS``) crossing ``WALL_CUT_M``
over the floor are cut there by a Boolean difference (``section_cut``: an architect's cutaway at half the earlier
1.2 m) and the ones above it are hidden; the furniture stays whole (only what lies above ``CUT_M``: ceilings, slabs,
upper floors, the roof, ceiling lights, is hidden), and so are the building copies, trees, hedges and grass (they
cover the plan); the camera frames the level's walls with ``PAD_M`` around them up to ``CUT_M``; a sun from nearly
overhead lights it. ``topdown_labels`` draws the windows (blue, with their ids) where the cut walls hide them.
"""
import argparse
import json
import sys

CUT_M = 2.2
PAD_M = 1.0
TILT_DEG = 35.0                 # 25 Oct 2026: the views are a bit angled (the walls and furniture show their height)
AZIMUTH_DEG = 225.0             # 25 Oct 2026 (user): from the upper right (north-east) to the lower left (south-west)
WALL_CUT_M = 0.6                # 25 Oct 2026 (user: "halved the walls"): an angled view cuts the walls here (was 1.2)
CUT_KINDS = {"wall", "door", "window", "railing", "facade_detail", "splashback", "light_well",
             "wall_plate"}         # 29 Oct 2026 (UL112): the switches and sockets are cut with their walls
HIDE_KINDS = {"ceiling", "roof", "site_decor", "site_decor_part", "vegetation_card", "atmosphere", "building_copy",
              "site_hedge", "site_grass", "light"}


def bbox(o):
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def section_cut(z: float) -> int:
    """Cut every rendered wall, door, window and railing (``CUT_KINDS``) that crosses height ``z`` with a Boolean
    difference of a box over ``z`` (the angled views: an architect's cutaway; full-height walls hid the rooms behind
    them); the furniture is never cut. The fast solver gives up on some meshes (real04's L1 outer wall stayed whole):
    those get the exact solver, and a mesh still standing above ``z`` is cut by a plane (``bisect_top``)."""
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
    cut = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or o is cutter or o.name.startswith("topdown_") \
                or str(o.get("wenart_kind")) not in CUT_KINDS:
            continue
        lo, hi = bbox(o)
        if lo[2] < z < hi[2]:
            m = o.modifiers.new("topdown_section", "BOOLEAN")
            m.operation = "DIFFERENCE"
            m.solver = "FLOAT" if "FLOAT" in {i.identifier for i in m.bl_rna.properties["solver"].enum_items} \
                else "FAST"
            m.object = cutter
            cut.append(o)
    for solver in ("EXACT", None):
        dg = bpy.context.evaluated_depsgraph_get()
        left = [o for o in cut if (evaluated_top(o, dg) or 0.0) > z + 0.02]
        for o in left:
            m = o.modifiers.get("topdown_section")
            if solver and m is not None:
                m.solver = solver
                if hasattr(m, "use_hole_tolerant"):
                    m.use_hole_tolerant = True
            elif not solver:
                if m is not None:
                    o.modifiers.remove(m)
                bisect_top(o, z)
        if not left:
            break
    return len(cut)


def evaluated_top(o, dg):
    ev = o.evaluated_get(dg)
    zs = [(ev.matrix_world @ v.co).z for v in ev.data.vertices]
    return max(zs) if zs else None


def bisect_top(o, z: float) -> None:
    """Cut ``o`` at world height ``z`` with a plane: the part above goes, the cut is closed (a copy of the mesh: the
    original data comes back for the next level, ``restore_meshes``)."""
    import bmesh
    from mathutils import Vector

    if "topdown_orig_mesh" not in o:
        o["topdown_orig_mesh"] = o.data.name
    me = o.data.copy()
    me.name = f"topdown_cut_{o.name}"
    bm = bmesh.new()
    bm.from_mesh(me)
    mw = o.matrix_world
    co = mw.inverted() @ Vector((0.0, 0.0, z))
    no = (mw.to_3x3().transposed() @ Vector((0.0, 0.0, 1.0))).normalized()
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                 plane_no=no, clear_outer=True)
    edges = [e for e in res.get("geom_cut", []) if isinstance(e, bmesh.types.BMEdge)]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(me)
    bm.free()
    o.data = me


def restore_meshes() -> None:
    """The meshes ``bisect_top`` replaced get their own data back."""
    import bpy

    for o in bpy.data.objects:
        name = o.get("topdown_orig_mesh") if o.type == "MESH" else None
        if name and bpy.data.meshes.get(name) is not None:
            o.data = bpy.data.meshes[name]
            del o["topdown_orig_mesh"]


def render_level(level_id: str, elevation: float, out: str, res: int, samples: int, device: str,
                 tilt: float = 0.0, azimuth: float = 0.0) -> dict:
    import bpy
    from mathutils import Vector  # noqa: F401  (bbox)

    sc = bpy.context.scene
    cut = elevation + CUT_M
    wall_cut = elevation + (WALL_CUT_M if tilt > 0 else CUT_M)
    restore_meshes()
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
        kind = str(o.get("wenart_kind"))
        hide = kind in HIDE_KINDS
        if not hide and o.type == "MESH":
            hide = bbox(o)[0][2] >= (wall_cut if kind in CUT_KINDS else cut) - 0.01
        o.hide_render = hide
        for m in [m for m in o.modifiers if m.name == "topdown_section"] if o.type == "MESH" else []:
            o.modifiers.remove(m)
    if tilt > 0:
        section_cut(wall_cut)
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
             "wall_cut_m": round(wall_cut - elevation, 3),
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
    ap.add_argument("--azimuth", type=float, default=AZIMUTH_DEG,
                    help="the view's direction, degrees from north (225: from the north-east to the south-west)")
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
