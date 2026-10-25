"""Double-sided exports (25 Oct 2026: real04's corner sofa "Sofa en L", a SketchUp export, rendered with dark
bands): every face of such a model has a copy on the same vertices turned the other way, in another colour, and
the two fight in the render. ``furniture.backface_twins`` finds those faces and ``furniture.separate_twins`` moves
each 0.2 mm along its own normal, so the copy that faces the camera is the nearer one and shows its own colour from
either side. The geometry is pure; the render probe needs a Blender binary."""
import json
import textwrap

import pytest

from wenart.blender import cli
from wenart.blender import furniture as F

BLENDER = cli.find_blender()


def test_the_turned_copies_are_found_and_moved_apart():
    q = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1)]
    assert F.backface_twins(q, [[0, 1, 2, 3], [3, 2, 1, 0]]) == {0, 1}          # a face and its back copy
    assert F.backface_twins(q, [[0, 1, 2, 3], [0, 1, 4]]) == set()              # a plain model
    assert F.backface_twins(q, [[0, 1, 2, 3], [0, 1, 2, 3]]) == set()           # a copy turned the same way
    assert F.backface_twins(q, [[0, 1, 2, 3], [3, 2, 1, 0], [0, 1, 4]]) == {0, 1}
    verts, faces, n = F.separate_twins(q, [[0, 1, 2, 3], [3, 2, 1, 0], [0, 1, 4]])
    assert n == 2 and faces[2] == [0, 1, 4] and verts[:5] == [tuple(map(float, v)) for v in q]
    up = {round(verts[k][2], 6) for k in faces[0]}
    down = {round(verts[k][2], 6) for k in faces[1]}
    assert up == {F.TWIN_OFFSET_M} and down == {-F.TWIN_OFFSET_M}                # each along its own normal
    assert F.separate_twins(q, [[0, 1, 4]])[2] == 0


PROBE = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from wenart.blender import furniture as F

    out_dir = sys.argv[sys.argv.index("--") + 1]
    separate = "--separate" in sys.argv
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 8
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = 24
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    sc.world = world

    def emit(name, value):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            if n.bl_idname != "ShaderNodeOutputMaterial":
                nt.nodes.remove(n)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = value
        nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
        return mat

    verts = [(-5, 0, -5), (5, 0, -5), (5, 0, 5), (-5, 0, 5)]
    faces = [[0, 1, 2, 3], [3, 2, 1, 0]]                          # the white front faces -Y, its dark copy +Y
    if separate:
        verts, faces, _ = F.separate_twins(verts, faces)
    me = bpy.data.meshes.new("sheet")
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(emit("front_white", 1.0))
    me.materials.append(emit("back_dark", 0.05))
    me.polygons[0].material_index = 0
    me.polygons[1].material_index = 1
    ob = bpy.data.objects.new("sheet", me)
    sc.collection.objects.link(ob)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    out = {}

    def shot(tag):
        path = os.path.join(out_dir, tag + ".png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        px = list(bpy.data.images.load(path).pixels)
        return sum(px[i] for i in range(0, len(px), 4)) / (len(px) / 4)

    cam.location, cam.rotation_euler = (0, -3, 0), (1.5708, 0, 0)          # looking at the -Y side
    out["front"] = shot("front")
    cam.location, cam.rotation_euler = (0, 3, 0), (1.5708, 0, 3.14159)     # looking at the +Y side
    out["back"] = shot("back")
    json.dump(out, open(os.path.join(out_dir, ("separate" if separate else "as_exported") + ".json"), "w"))
""")


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_each_side_shows_its_own_colour_once_the_copies_are_apart(tmp_path):
    script = tmp_path / "backfaces_probe.py"
    script.write_text(PROBE, encoding="utf-8")
    cli.run_blender(script, [str(tmp_path), "--separate"], timeout=900)
    cli.run_blender(script, [str(tmp_path)], timeout=900)
    sep = json.loads((tmp_path / "separate.json").read_text(encoding="utf-8"))
    raw = json.loads((tmp_path / "as_exported.json").read_text(encoding="utf-8"))
    assert sep["front"] > 0.95 and sep["back"] < 0.3, sep          # white from -Y, the dark copy (0.05) from +Y
    assert raw["front"] < 0.95 or raw["back"] > 0.3, raw           # as exported, one side shows the wrong copy
