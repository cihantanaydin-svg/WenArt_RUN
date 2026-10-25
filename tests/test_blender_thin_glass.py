"""Thin glass (``materials.thin_glass_material``: shower panels, stair and terrace balustrades) seen at a grazing angle.

The 25 Oct 2026 real04 run rendered every stair and roof-terrace glass balustrade black: the Fresnel node takes
1 / IOR on a back face, so past ~44 degrees the pane's back face reflected everything (total internal reflection)
and nothing came through. One Blender process renders a bright emissive wall behind a 12 mm pane (a
``details.balustrade`` glass part) head-on and at 75 degrees, with the pane and without it: the wall seen through
the pane keeps most of its light at both angles. Skipped without a Blender binary.
"""
import json
import textwrap

import pytest

from wenart.blender import cli

BLENDER = cli.find_blender()
pytestmark = pytest.mark.skipif(BLENDER is None, reason="no Blender binary")

PROBE = textwrap.dedent("""
    import bpy, json, math, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from wenart.blender import details as D, materials as M

    out_dir = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = 32
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    sc.world = world

    def mesh(name, parts, mat):
        verts, faces = [], []
        for v, f in parts:
            o = len(verts)
            verts += list(v)
            faces += [[i + o for i in ff] for ff in f]
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        me.materials.append(mat)
        return ob

    _, glass = D.balustrade((-3.0, 0.0), (3.0, 0.0), -1.0, 3.0, "glass_channel")
    pane = mesh("pane", glass, M.thin_glass_material("thin_glass"))
    lamp = bpy.data.materials.new("lamp")
    lamp.use_nodes = True
    nt = lamp.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != "ShaderNodeOutputMaterial":
            nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
    wall = ([(-50, 3, -50), (50, 3, -50), (50, 3, 50), (-50, 3, 50)], [[0, 1, 2, 3]])
    mesh("wall", [wall], lamp)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 200
    sc.collection.objects.link(cam)
    sc.camera = cam
    out = {}
    for angle in (0, 75):
        a = math.radians(angle)
        cam.location = (-2.0 * math.sin(a), -2.0 * math.cos(a), 0.5)
        cam.rotation_euler = (math.pi / 2, 0.0, -a)
        for with_pane in (True, False):
            pane.hide_render = not with_pane
            path = os.path.join(out_dir, f"p{angle}_{int(with_pane)}.png")
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
            img = bpy.data.images.load(path)
            px = list(img.pixels)
            out[f"{angle}_{int(with_pane)}"] = sum(px[i] for i in range(0, len(px), 4)) / (len(px) / 4)
    json.dump(out, open(os.path.join(out_dir, "thin_glass.json"), "w"))
""")


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("thin_glass")
    script = tmp / "thin_glass_probe.py"
    script.write_text(PROBE, encoding="utf-8")
    cli.run_blender(script, [str(tmp)], timeout=900)
    return json.loads((tmp / "thin_glass.json").read_text(encoding="utf-8"))


def test_a_thin_pane_is_see_through_head_on_and_at_a_grazing_angle(probe):
    for angle in (0, 75):
        bare = probe[f"{angle}_0"]
        assert bare > 0.5, probe
        assert probe[f"{angle}_1"] > 0.7 * bare, (angle, probe)   # was ~0 at 75 degrees (total internal reflection)
