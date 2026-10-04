"""Window glass (docs/milestone5.md §2.1): Blender renders of small probe scenes.

The pane is a closed box as shell.py builds it (``DEFAULTS["glass_thickness"]``
= 6 mm) with ``materials.window_glass_material``. One Blender process renders:

- shift: an emissive stripe 3 m behind a pane, seen obliquely, with the pane
  and with the pane hidden (open hole). Real glass refracts at both faces, so
  the stripe only moves by a fraction of the 6 mm thickness; a pane that
  refracts at its first face only bends the whole outside view (23 px here).
  The object index and the depth still stop at the pane.
- ghost: a small lamp inside the room seen reflected in the pane (black
  world, no clamping). The two faces reflect it on top of each other; a ray
  that leaves the pane unrefracted after the inner reflection puts a second,
  misplaced copy next to it.
- light: a closed white room lit by a sun and a blue sky through one window,
  half of it behind a frosted (rough Glass BSDF) panel inside the room: the
  light on the diffuse surfaces with the pane equals the open hole (BSDF
  rays and shadow rays agree), also for rough transmission rays.
Skipped without a Blender binary.
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
    import numpy as np
    from mathutils import Vector
    from wenart.blender import common, geom2d, materials as M, render as R
    from wenart.blender.shell import DEFAULTS

    out_dir = sys.argv[sys.argv.index("--") + 1]
    scene = bpy.context.scene
    col = scene.collection
    PANE_INDEX = 7
    T = DEFAULTS["glass_thickness"]


    def reset():
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        world = bpy.data.worlds.new("w")
        scene.world = world
        return world.node_tree.nodes["Background"]


    def plain(name, colour=None, strength=None, glass_roughness=None):
        mat = bpy.data.materials.new(name)
        nt = mat.node_tree
        for n in list(nt.nodes):
            if n.bl_idname != "ShaderNodeOutputMaterial":
                nt.nodes.remove(n)
        if strength is not None:
            node = nt.nodes.new("ShaderNodeEmission")
            node.inputs["Strength"].default_value = strength
        elif glass_roughness is not None:
            node = nt.nodes.new("ShaderNodeBsdfGlass")
            node.inputs["Roughness"].default_value = glass_roughness
        else:
            node = nt.nodes.new("ShaderNodeBsdfDiffuse")
            node.inputs["Color"].default_value = (*colour, 1.0)
        nt.links.new(node.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
        return mat


    def box(name, centre, size, mat, index=0):
        v, f = geom2d.box(centre, size)
        ob = common.new_mesh_object(name, v, f, collection=col, wenart_id=name, kind="wall", status="assumed",
                                    materials=[mat])
        ob.pass_index = index
        return ob


    def camera(loc, target, lens):
        data = bpy.data.cameras.new("cam")
        cam = bpy.data.objects.new("cam", data)
        col.objects.link(cam)
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        data.lens = lens
        scene.camera = cam


    def render(name, res, samples, light_passes=False, clamp=True):
        R.configure_device(scene, "cpu")
        R.configure_render(scene, samples, res, "CPU", False)
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.seed = 1
        if not clamp:
            scene.cycles.sample_clamp_direct = scene.cycles.sample_clamp_indirect = 0.0
        vl = scene.view_layers[0]
        vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = light_passes
        R.set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = os.path.join(out_dir, name + ".exr")
        bpy.ops.render.render(write_still=True)
        return R.read_exr(scene.render.filepath)


    def runs(row, level):
        on = np.flatnonzero(row > level)
        spans = []
        for c in on.tolist():
            if spans and c == spans[-1][1] + 1:
                spans[-1][1] = c
            else:
                spans.append([c, c])
        return spans


    result = {"thickness": T}
    # shift: stripe x 0..0.2 m at y = 3, pane in the plane y = 0, camera 1.2 m inside, looking across
    for hole in (True, False):
        bg = reset()
        bg.inputs["Strength"].default_value = 0.0
        pane = box("pane", (0.0, 0.0, 1.0), (2.0, T, 2.0), M.window_glass_material("glass"), PANE_INDEX)
        pane.hide_render = hole
        box("stripe", (0.1, 3.0, 1.0), (0.2, 0.01, 4.0), plain("stripe", strength=5.0))
        camera((-1.2, -1.2, 1.0), (0.1, 3.0, 1.0), 50)
        ch = render("shift_hole" if hole else "shift_glass", (200, 100), 16)
        lum = R.find_rgb(ch, "Combined").mean(axis=2)
        index = np.rint(R.find_channel(ch, "Object Index.X"))
        depth = R.find_channel(ch, "Depth.Z")
        result["shift_hole" if hole else "shift_glass"] = {
            "stripe": runs(lum[50], 0.5), "index": float(index[50, 100]), "depth": float(depth[50, 100])}

    # ghost: lamp (8 cm cube) inside at x = +0.9, camera at x = -0.9, both 1 m in front of the pane
    bg = reset()
    bg.inputs["Strength"].default_value = 0.0
    box("pane", (0.0, 0.0, 1.0), (3.0, T, 2.0), M.window_glass_material("glass"), PANE_INDEX)
    box("lamp", (0.9, -1.0, 1.0), (0.08, 0.08, 0.08), plain("lamp", strength=20.0))
    camera((-0.9, -1.0, 1.0), (0.0, 0.0, 1.0), 50)
    lum = R.find_rgb(render("ghost", (200, 100), 64, clamp=False), "Combined").mean(axis=2)
    result["ghost"] = {"reflections": runs(lum[50], 0.01 * float(lum[50].max())), "max": float(lum.max())}

    # light: white room x -2..2, y 0..4, z 0..3; window x -0.75..0.75, z 0.8..2.3 in the wall y -0.2..0
    for hole in (True, False):
        bg = reset()
        bg.inputs["Color"].default_value = (0.4, 0.6, 1.0, 1.0)
        bg.inputs["Strength"].default_value = 1.0
        white = plain("white", colour=(0.7, 0.7, 0.7))
        for i, (c, s) in enumerate([((0, 2, -0.05), (4.4, 4.4, 0.1)), ((0, 2, 3.05), (4.4, 4.4, 0.1)),
                                    ((-2.1, 2, 1.5), (0.2, 4.4, 3)), ((2.1, 2, 1.5), (0.2, 4.4, 3)),
                                    ((0, 4.1, 1.5), (4.4, 0.2, 3)), ((-1.375, -0.1, 1.5), (1.25, 0.2, 3)),
                                    ((1.375, -0.1, 1.5), (1.25, 0.2, 3)), ((0, -0.1, 0.4), (1.5, 0.2, 0.8)),
                                    ((0, -0.1, 2.65), (1.5, 0.2, 0.7))]):
            box(f"w{i}", c, s, white)
        pane = box("pane", (0, -0.1, 1.55), (1.5, T, 1.5), M.window_glass_material("glass"), PANE_INDEX)
        pane.hide_render = hole
        box("frosted", (-0.375, 0.25, 1.55), (0.75, 0.01, 1.5), plain("frosted", glass_roughness=0.3))
        sun = bpy.data.lights.new("sun", "SUN")
        sun.energy, sun.angle = 3.0, math.radians(1.0)
        so = bpy.data.objects.new("sun", sun)
        col.objects.link(so)
        so.rotation_euler = Vector((0.3, 1.0, -0.6)).normalized().to_track_quat("-Z", "Y").to_euler()
        camera((0, 0.3, 1.6), (0, 4.0, 0.8), 18)       # looks away from the window
        ch = render("light_hole" if hole else "light_glass", (80, 60), 64, light_passes=True)
        light = R.find_rgb(ch, "Diffuse Direct") + R.find_rgb(ch, "Diffuse Indirect")
        result["light_hole" if hole else "light_glass"] = {"mean": float(light.mean())}
    json.dump(result, open(os.path.join(out_dir, "glass.json"), "w"))
""")


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("glass")
    script = tmp / "glass_probe.py"
    script.write_text(PROBE, encoding="utf-8")
    cli.run_blender(script, [str(tmp)], timeout=900)
    return json.loads((tmp / "glass.json").read_text(encoding="utf-8"))


def test_the_view_through_the_pane_stays_in_place(probe):
    """Both faces refract: the stripe through the pane is where the open hole shows it (within 1 px)."""
    (hole,), (glass,) = probe["shift_hole"]["stripe"], probe["shift_glass"]["stripe"]
    assert hole[1] - hole[0] > 5, probe
    assert abs(glass[0] - hole[0]) <= 1 and abs(glass[1] - hole[1]) <= 1, probe


def test_index_and_depth_stop_at_the_pane(probe):
    """The camera ray stops at the pane for the data passes (gate, pane restore and vision check rely on it)."""
    g, h = probe["shift_glass"], probe["shift_hole"]
    assert g["index"] == 7 and h["index"] == 0
    # Centre ray from (-1.2, -1.2) towards (0.1, 3.0) meets the pane's room face (y = -T/2) after 1.253 m.
    d_y = 4.2 / (1.3 ** 2 + 4.2 ** 2) ** 0.5
    assert g["depth"] == pytest.approx((1.2 - probe["thickness"] / 2) / d_y, abs=0.01)
    assert g["depth"] < h["depth"]


def test_the_two_faces_reflect_a_lamp_in_one_place(probe):
    """No misplaced second reflection: the ray reflected at the outer face also refracts back out."""
    reflections = probe["ghost"]["reflections"]
    assert len(reflections) == 1, probe["ghost"]
    assert probe["ghost"]["max"] > 0.5


def test_the_room_is_lit_as_through_an_open_hole(probe):
    """Shadow rays and BSDF rays (also through a frosted panel) see the same pane: no over-counted sun."""
    hole, glass = probe["light_hole"]["mean"], probe["light_glass"]["mean"]
    assert hole > 0.01
    assert glass / hole == pytest.approx(1.0, abs=0.02), (glass, hole)
