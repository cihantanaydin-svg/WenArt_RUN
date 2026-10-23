"""Fix round after P6a, part I2 (22-23 Oct 2026): the windows-only interior sky, its A/B on pod P6c and the asks of the
P6a fix reports addressed to the render, sky and build side.

- The user's decision of 22 Oct 2026 on the interior-sky A/B, "Windows only +3.5": the light variant ``skywin35``
  (``lighting.SKY_WINDOW_VARIANTS``) raises the interior world by 2^3.5 only on the camera's paths
  (``materials.world_nodes(..., gain_rays="camera_paths")``: Light Path max(Is Camera Ray, Is Singular Ray), the factor
  ``window_glass_material`` uses). Pure tests of the levers, the record and the node graph (a fake bpy); the default
  and every other variant build the world byte for byte as before. With ``WENART_BLENDER`` (the bpy 5.2.2 shim or the
  pod's Blender) a small lit room with a window renders base / skywin35 / sky35: the room light stays, the sky through
  the pane is sky35's, a library mirror (Roughness 0.03, glossy) keeps the old sky, a sharp mirror sees the new one,
  and a pane seen from outside reflects the sky by Fresnel (R_render's terrace ask is skipped on that measurement).
- The A/B of pod P6c: ``wenart.run.ab.M13_SKYWIN_AB_VIEWS`` (real02: five window views of P4a's run and one rig-lit
  hall), the summary's windows-only columns, ``scripts/jobs/m13_p6.sh`` taking the project, the view set and the
  folder from the environment with P6a's defaults.
- The asks: ``cli render --clamp-indirect`` (R_render), the scene camera's frame keys typed in ``schemas.SCENE_CAMERA``
  (X_ext), curtains and blinds kept under the slope by ``build.decor_under_roof`` (D_decor) and the floor-lamp shades
  in S2 (``scene_checks``, D_decor).
Each test fails on 52d4bb8 (or on a mutation where it guards the default), except the guards that say so.
"""
from __future__ import annotations

import copy
import inspect
import json
import math
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import jsonschema
import pytest

from test_m13_sky_ab import _ab_env, _cam, _p6_env, _run_p6     # the fakes of the P6a job tests

from wenart.blender import build as B
from wenart.blender import cli
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import scene_checks as SC
from wenart.blender import schemas as S
from wenart.run import ab as AB

ROOT = Path(__file__).resolve().parents[1]
P6_JOB = ROOT / "scripts" / "jobs" / "m13_p6.sh"
P4A = ROOT / "runs" / "20261017-072801-full" / "results" / "renders" / "real02"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                                           "/workspace/tools/blender, /opt/wenart/blender or PATH)")
GAIN = 2.0 ** 3.5


# --------------------------------------------------------------------------
# The windows-only level: levers, record, node graph
# --------------------------------------------------------------------------

def test_skywin35_is_a_windows_only_sky_level_from_production():
    assert L.SKY_WINDOW_VARIANT_STOPS == {"skywin35": 3.5} and L.SKY_WINDOW_VARIANTS == ("skywin35",)
    assert (L.SKY_RAYS_ALL, L.SKY_RAYS_CAMERA) == ("all", "camera_paths")
    assert "skywin35" in L.KNOWN_LIGHT_VARIANTS and L.SKY_VARIANTS == ("sky2", "sky35", "sky52")
    prod = L.light_levers(env={})
    win = L.light_levers(env={L.LIGHT_VARIANT_ENV: "skywin35"})
    # production's sun, EV cap, rig and shell; the gain of sky35, but on the camera's paths only
    assert {k: win[k] for k in ("sun_wm2", "ev_cap", "rig", "shell")} == \
        {k: prod[k] for k in ("sun_wm2", "ev_cap", "rig", "shell")}
    assert win["sky_stops"] == 3.5 and win["sky_rays"] == "camera_paths" and win["variant"] == "skywin35"
    assert L.interior_sky_gain(win) == pytest.approx(GAIN, rel=1e-12) and L.interior_sky_rays(win) == "camera_paths"
    assert L.lever_record(win) == {"sun_wm2": 1000.0, "ev_cap": True, "rig": True, "shell": True, "source": "env",
                                   "sky_stops": 3.5, "sky_rays": "camera_paths"}
    assert L.light_levers("base,skywin35")["sky_rays"] == "camera_paths"
    old = L.light_levers("m11+skywin35")            # with the Milestone 11 look it starts from that look
    assert (old["sun_wm2"], old["rig"], old["sky_stops"], old["sky_rays"]) == (3.0, False, 3.5, "camera_paths")
    for both in ("sky35,skywin35", "skywin35+sky2"):
        with pytest.raises(ValueError, match="more than one interior sky level"):
            L.parse_light_variant(both)
    # every other levers dict: all rays (production, the lever variants, the sky levels, a dict from before)
    assert prod["sky_rays"] == "all" and L.interior_sky_rays(prod) == "all" and L.interior_sky_rays(None) == "all"
    for name in L.LIGHT_VARIANTS + L.SKY_VARIANTS:
        assert L.interior_sky_rays(L.light_levers(name)) == "all", name
        assert "sky_rays" not in L.lever_record(L.light_levers(name)), name
    assert L.interior_sky_rays({"sky_stops": 3.5}) == "all"
    assert L.interior_sky_rays({"sky_stops": 0.0, "sky_rays": "camera_paths"}) == "all"     # no gain: nothing to aim
    with pytest.raises(ValueError, match="unknown sky_rays"):
        L.interior_sky_rays({"sky_stops": 2.0, "sky_rays": "glossy"})


def test_the_world_record_of_a_windows_only_sky_keeps_the_rooms_strength():
    strength, extra = M.world_strength_record(1.0, GAIN, "camera_paths")
    assert strength == 1.0                       # what lights the room
    assert extra == {"strength_base": 1.0, "strength_gain": 11.313708, "sky_stops": 3.5, "sky_rays": "camera_paths",
                     "strength_camera": 11.313708, "gain_factor": "Light Path max(Is Camera Ray, Is Singular Ray)"}
    # guards (hold on 52d4bb8 too): production and the sky levels as they were
    assert M.world_strength_record(1.0) == (1.0, {}) and M.world_strength_record(1.0, 1.0, "camera_paths") == (1.0, {})
    assert M.world_strength_record(1.0, GAIN)[0] == pytest.approx(GAIN)
    assert "sky_rays" not in M.world_strength_record(1.0, GAIN, "all")[1]
    with pytest.raises(ValueError, match="gain_rays"):
        M.world_strength_record(1.0, GAIN, "glossy")


class _Socket:
    def __init__(self, node, key):
        self.node, self.key, self.default_value = node, key, None


class _Sockets(dict):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def __missing__(self, key):
        self[key] = _Socket(self.node, key)
        return self[key]


class _Node:
    def __init__(self, kind):
        self.bl_idname, self.operation = kind, None
        self.inputs, self.outputs = _Sockets(self), _Sockets(self)


class _Nodes(list):
    def new(self, kind):
        self.append(_Node(kind))
        return self[-1]


class _Links(list):
    def new(self, a, b):
        self.append((a, b))


class _World:
    def __init__(self, name):
        self.name, self.use_nodes = name, False
        self.node_tree = types.SimpleNamespace(nodes=_Nodes(), links=_Links())


@pytest.fixture()
def fake_bpy(monkeypatch):
    bpy = types.SimpleNamespace(data=types.SimpleNamespace(
        worlds=types.SimpleNamespace(new=_World),
        images=types.SimpleNamespace(load=lambda path, check_existing=True: types.SimpleNamespace(filepath=path))))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    return bpy


def _graph(scene):
    nodes = scene.world.node_tree.nodes
    links = [(a.node.bl_idname, a.node.operation, a.key, b.node.bl_idname, b.node.operation, b.key)
             for a, b in scene.world.node_tree.links]
    bg = next(n for n in nodes if n.bl_idname == "ShaderNodeBackground")
    return nodes, links, bg


def test_world_nodes_raises_the_sky_on_the_camera_paths_only(fake_bpy, tmp_path):
    hdri = tmp_path / "kloppenheim_06_2k.hdr"
    hdri.write_bytes(b"hdr")
    lighting = {"mood": "warm daylight", "sun_azimuth_deg": 210.0, "sun_elevation_deg": 35.0}
    for path, base in ((str(hdri), 1.0), (None, 0.5)):                 # the HDRI and the physical-sky fallback
        scene = types.SimpleNamespace(world=None)
        rec = M.world_nodes(scene, lighting, path, strength_gain=GAIN, gain_rays="camera_paths")
        nodes, links, bg = _graph(scene)
        assert bg.inputs["Strength"].default_value == base           # every other ray: the room's strength
        kinds = [n.bl_idname for n in nodes]
        assert kinds.count("ShaderNodeLightPath") == 1
        assert sorted(n.operation for n in nodes if n.bl_idname == "ShaderNodeMath") == ["MAXIMUM", "MULTIPLY_ADD"]
        assert ("ShaderNodeLightPath", None, "Is Camera Ray", "ShaderNodeMath", "MAXIMUM", 0) in links
        assert ("ShaderNodeLightPath", None, "Is Singular Ray", "ShaderNodeMath", "MAXIMUM", 1) in links
        assert ("ShaderNodeMath", "MAXIMUM", "Value", "ShaderNodeMath", "MULTIPLY_ADD", 0) in links
        assert ("ShaderNodeMath", "MULTIPLY_ADD", "Value", "ShaderNodeBackground", None, "Strength") in links
        mad = next(n for n in nodes if n.operation == "MULTIPLY_ADD")
        assert mad.inputs[1].default_value == pytest.approx(base * (GAIN - 1.0))   # f = 1: base x gain
        assert mad.inputs[2].default_value == pytest.approx(base)                  # f = 0: base
        assert rec["kind"] == ("hdri" if path else "sky") and rec["strength"] == base
        assert rec["strength_base"] == base and rec["strength_camera"] == pytest.approx(base * GAIN, abs=1e-6)
        assert rec["sky_rays"] == "camera_paths" and rec["sky_stops"] == 3.5
    # guards (hold on 52d4bb8 too): the default and sky35 build the graph and the record as before
    scene = types.SimpleNamespace(world=None)
    rec = M.world_nodes(scene, lighting, str(hdri))
    assert json.dumps(rec) == json.dumps({"kind": "hdri", "file": str(hdri), "strength": 1.0})
    nodes, links, bg = _graph(scene)
    assert [n.bl_idname for n in nodes] == ["ShaderNodeOutputWorld", "ShaderNodeBackground", "ShaderNodeTexEnvironment",
                                            "ShaderNodeTexCoord", "ShaderNodeMapping"]
    assert bg.inputs["Strength"].default_value == 1.0
    for rays in ("all", "camera_paths"):
        scene = types.SimpleNamespace(world=None)
        assert M.world_nodes(scene, lighting, str(hdri), strength_gain=1.0, gain_rays=rays) == rec
        assert "ShaderNodeLightPath" not in [n.bl_idname for n in _graph(scene)[0]]
    scene = types.SimpleNamespace(world=None)
    rec = M.world_nodes(scene, lighting, str(hdri), strength_gain=GAIN)
    assert "ShaderNodeLightPath" not in [n.bl_idname for n in _graph(scene)[0]]
    assert _graph(scene)[2].inputs["Strength"].default_value == pytest.approx(GAIN) and "sky_rays" not in rec


def test_build_lighting_and_the_fingerprint_carry_the_windows_only_level(tmp_path, monkeypatch):
    src = inspect.getsource(L.build_lighting)
    assert "gain_rays=interior_sky_rays(levers))" in src and src.count("gain_rays") == 1
    building = tmp_path / "building_final.json"
    building.write_text(json.dumps({"project": {"id": "real02"}}), encoding="utf-8")
    for var in ("WENART_CAMERAS_FROM", "WENART_CAMERAS_EXTRA", L.LIGHT_VARIANT_ENV):
        monkeypatch.delenv(var, raising=False)
    prints = set()
    for v in (None, "base", "sky35", "skywin35"):
        if v:
            monkeypatch.setenv(L.LIGHT_VARIANT_ENV, v)
        args = B.fingerprint_args(str(building))
        assert args["light_variant"] == v
        prints.add(B.build_fingerprint(args))
    assert len(prints) == 4


# --------------------------------------------------------------------------
# The bpy shim / the pod's Blender: a lit room with a window, base / skywin35 / sky35
# --------------------------------------------------------------------------

PROBE = textwrap.dedent('''
    import bpy, json, math, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    import numpy as np
    from mathutils import Vector
    from wenart.blender import common, geom2d, lighting as L, materials as M, render as R
    from wenart.blender.shell import DEFAULTS

    out_dir = sys.argv[sys.argv.index("--") + 1]
    scene = bpy.context.scene
    col = scene.collection
    T = DEFAULTS["glass_thickness"]
    PANE, GROUND, MIRROR_GLOSSY, MIRROR_SHARP = 7, 3, 5, 6
    LIGHTING = {"mood": "warm daylight", "sun_azimuth_deg": 180.0, "sun_elevation_deg": 35.0}

    # a small equirectangular HDRI (the production branch of world_nodes): a bright sky over a darker ground
    hdri = os.path.join(out_dir, "probe_sky.hdr")
    img = bpy.data.images.new("probe_sky", 64, 32, float_buffer=True)
    px = []
    for y in range(32):
        rgb = (2.0, 2.8, 4.0) if y >= 16 else (0.3, 0.32, 0.24)
        for _x in range(64):
            px.extend((*rgb, 1.0))
    img.pixels = px
    img.filepath_raw = hdri
    img.file_format = "HDR"
    img.save()


    def plain(name, colour, roughness=0.9, metallic=0.0):
        mat = bpy.data.materials.new(name)
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        return mat


    def box(name, centre, size, mat, index=0):
        v, f = geom2d.box(centre, size)
        ob = common.new_mesh_object(name, v, f, collection=col, wenart_id=name, kind="wall", status="assumed",
                                    materials=[mat])
        ob.pass_index = index
        return ob


    def camera(name, loc, target, lens):
        data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, data)
        col.objects.link(cam)
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        data.lens = lens
        return cam


    def clear():
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)


    def room():
        clear()
        white = plain("white", (0.7, 0.7, 0.7))
        # room x -2..2, y 0..4, z 0..3; window x -0.75..0.75, z 0.8..2.3 in the wall y -0.2..0 (outside: y < -0.2)
        for i, (c, s) in enumerate([((0, 2, -0.05), (4.4, 4.4, 0.1)), ((0, 2, 3.05), (4.4, 4.4, 0.1)),
                                    ((-2.1, 2, 1.5), (0.2, 4.4, 3)), ((2.1, 2, 1.5), (0.2, 4.4, 3)),
                                    ((0, 4.1, 1.5), (4.4, 0.2, 3)), ((-1.375, -0.1, 1.5), (1.25, 0.2, 3)),
                                    ((1.375, -0.1, 1.5), (1.25, 0.2, 3)), ((0, -0.1, 0.4), (1.5, 0.2, 0.8)),
                                    ((0, -0.1, 2.65), (1.5, 0.2, 0.7))]):
            box(f"w{i}", c, s, white)
        box("pane", (0, -0.1, 1.55), (1.5, T, 1.5), M.window_glass_material("glass"), PANE)
        box("lawn", (0, -30.2, -0.05), (60.0, 60.0, 0.1), plain("lawn", (0.12, 0.2, 0.06)), GROUND)
        # two mirrors on the back wall: the library mirror's glass (mirror_glass_spec: Roughness 0.03) and a sharp one
        spec = M.mirror_glass_spec()
        box("mirror_glossy", (-0.6, 3.98, 1.6), (1.0, 0.02, 1.4),
            plain("mirror_glossy", spec["base"], spec["roughness"], spec["metallic"]), MIRROR_GLOSSY)
        box("mirror_sharp", (0.6, 3.98, 1.6), (1.0, 0.02, 1.4),
            plain("mirror_sharp", spec["base"], 0.0, spec["metallic"]), MIRROR_SHARP)
        sun = bpy.data.lights.new("sun", "SUN")
        sun.energy, sun.angle = 300.0, math.radians(0.53)
        so = bpy.data.objects.new("sun", sun)
        col.objects.link(so)
        so.rotation_euler = Vector((0.25, 0.8, -0.57)).normalized().to_track_quat("-Z", "Y").to_euler()
        return {"window": camera("cam_window", (0.3, 3.6, 1.4), (0.0, -1.0, 1.45), 28),
                "room": camera("cam_room", (0, 0.4, 1.6), (0, 4.0, 0.6), 18),
                "mirror": camera("cam_mirror", (0.0, 1.6, 1.55), (0.0, 3.9, 1.55), 24)}


    def render(cam, name, res=(160, 90), samples=32, clamp=None):
        scene.camera = cam
        R.configure_device(scene, "cpu")
        R.configure_render(scene, samples, res, "CPU", False, clamp_indirect=clamp)   # production clamps
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.seed = 1
        vl = scene.view_layers[0]
        vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = True
        R.set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = os.path.join(out_dir, name + ".exr")
        bpy.ops.render.render(write_still=True)
        ch = R.read_exr(scene.render.filepath)
        return {"combined": R.find_rgb(ch, "Combined"), "index": np.rint(R.find_channel(ch, "Object Index.X")),
                "light": R.find_rgb(ch, "Diffuse Direct") + R.find_rgb(ch, "Diffuse Indirect")}


    def mean(rgb, mask):
        return float(rgb[mask].mean()) if mask.any() else None


    result = {}
    for variant in ("base", "skywin35", "sky35"):
        cams = room()
        levers = L.light_levers(variant)
        rec = M.world_nodes(scene, LIGHTING, hdri, strength_gain=L.interior_sky_gain(levers),
                            gain_rays=L.interior_sky_rays(levers))
        w = render(cams["window"], variant + "_window")
        pane = w["index"] == PANE
        upper = pane.copy()
        upper[pane.shape[0] // 2:, :] = False             # the upper half of the frame: the sky through the pane
        r = render(cams["room"], variant + "_room")        # looks away from the window
        m = render(cams["mirror"], variant + "_mirror")    # the mirrors reflect the window behind the camera
        result[variant] = {"record": rec, "pane_sky": mean(w["combined"], upper),
                           "walls_light": mean(w["light"], w["index"] == 0), "room_light": float(r["light"].mean()),
                           "mirror_glossy": mean(m["combined"], m["index"] == MIRROR_GLOSSY),
                           "mirror_sharp": mean(m["combined"], m["index"] == MIRROR_SHARP)}

    # R_render's terrace ask: a pane seen from outside, a white sky of radiance 1 over it and a black room behind
    reflect = {}
    for angle in (0, 60):
        clear()
        world = bpy.data.worlds.new("white")
        scene.world = world
        bg = world.node_tree.nodes["Background"]
        bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs["Strength"].default_value = 1.0
        box("pane", (0, 0, 1.5), (2.0, T, 2.0), M.window_glass_material("glass"), PANE)
        black = plain("black", (0.0, 0.0, 0.0), 1.0)
        black.node_tree.nodes.get("Principled BSDF").inputs["Specular IOR Level"].default_value = 0.0
        box("room", (0, 1.6, 1.5), (6.0, 3.0, 6.0), black)
        a = math.radians(angle)
        cam = camera("cam_out", (2.0 * math.sin(a), -2.0 * math.cos(a), 1.5), (0.0, 0.0, 1.5), 50)
        o = render(cam, f"outside_{angle}", res=(64, 36), samples=64)
        reflect[str(angle)] = mean(o["combined"], o["index"] == PANE)
    result["outside_pane"] = reflect
    json.dump(result, open(os.path.join(out_dir, "sky_probe.json"), "w"), indent=1)
''')


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("skywin")
    script = tmp / "sky_probe.py"
    script.write_text(PROBE, encoding="utf-8")
    cli.run_blender(script, [str(tmp)], timeout=1800)
    return json.loads((tmp / "sky_probe.json").read_text(encoding="utf-8"))


@needs_blender
def test_the_windows_only_sky_keeps_the_room_light_and_brightens_the_panes(probe):
    base, win, whole = probe["base"], probe["skywin35"], probe["sky35"]
    assert win["record"]["sky_rays"] == "camera_paths" and win["record"]["strength"] == base["record"]["strength"]
    # the room light (the diffuse passes: what the metering, the white point and the tint read) stays ...
    for key in ("room_light", "walls_light"):
        assert win[key] == pytest.approx(base[key], rel=0.01), (key, base[key], win[key])
    assert whole["room_light"] > 1.03 * base["room_light"]          # ... where the whole-world sky35 lights it
    # the sky through the pane: sky35's (both under Cycles' indirect clamp at bounce 2)
    assert win["pane_sky"] > 2.5 * base["pane_sky"]
    assert win["pane_sky"] == pytest.approx(whole["pane_sky"], rel=0.1)
    # a sharp mirror sees the brighter sky; the library mirror's Roughness 0.03 is glossy in Cycles: the old sky
    assert win["mirror_sharp"] > 1.1 * base["mirror_sharp"]
    assert win["mirror_glossy"] == pytest.approx(base["mirror_glossy"], rel=0.02)
    assert whole["mirror_glossy"] > 1.3 * base["mirror_glossy"]


@needs_blender
def test_a_pane_seen_from_outside_already_reflects_the_sky(probe):
    """R_render's ask ("the camera-ray path is pure Glass refraction both ways") does not hold: the Glass BSDF of
    ``window_glass_material`` reflects by Fresnel on both faces, about 6.5 % of a white sky head-on (two faces of IOR
    1.45 glass: 2 x 3.4 %) and more at a grazing angle. The dark panes of teras_2_x are the dark room behind them at the
    facade's exposure; a stronger reflection is a glazing change, not a fix."""
    head_on, grazing = probe["outside_pane"]["0"], probe["outside_pane"]["60"]
    assert 0.05 < head_on < 0.085 and grazing > 1.5 * head_on


# --------------------------------------------------------------------------
# The A/B of pod P6c: views, summary, m13_p6.sh
# --------------------------------------------------------------------------

SKYWIN_REAL02 = ["cam_r_L-1_salon_1", "cam_r_L-1_mutfak_1", "cam_r_L0_yatak_odasi_1", "cam_r_L0_e_yatak_odasi_3",
                 "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1", "cam_r_L-1_koridor_2_1"]


def test_the_windows_only_ab_views_and_levels():
    assert AB.M13_SKYWIN_AB_VARIANTS == ("base", "skywin35", "sky35")
    assert all(v in L.KNOWN_LIGHT_VARIANTS for v in AB.M13_SKYWIN_AB_VARIANTS)
    assert AB.AB_VIEW_SETS["skywin"] is AB.M13_SKYWIN_AB_VIEWS and AB.view_set_of("skywin") is AB.M13_SKYWIN_AB_VIEWS
    real02 = AB.M13_SKYWIN_AB_VIEWS["real02"]
    assert [v["camera"] for v in real02] == SKYWIN_REAL02 and AB.ab_views("real02", "skywin") == SKYWIN_REAL02
    assert [v["room_type"] for v in real02].count("hall") == 1 and real02[-1]["room_type"] == "hall"
    for v in real02:
        assert v["camera"].startswith(f"cam_{v['room_id']}_") and v["camera"][len(v["room_id"]) + 5:].isdigit(), v
    # real04: P6a's six sky views and its rig-lit hall; the earlier sets keep their views
    assert [v["camera"] for v in AB.M13_SKYWIN_AB_VIEWS["real04"]] == \
        [v["camera"] for v in AB.M13_SKY_AB_VIEWS["real04"]] + ["cam_r_L-1_koridor_2_1"]
    assert AB.ab_views("real02", "sky") == [] and AB.ab_views("real03", "skywin") == []


@pytest.mark.skipif(not (P4A / "scene_manifest.json").is_file(), reason="needs runs/20261017-072801-full (pod P4a)")
def test_the_real02_views_see_windows_in_p4a_and_the_hall_is_rig_lit():
    """real02 replays its Milestone 11 cameras: every view is a P4a camera of its room that saw a window or a glazed
    door (pane pixels in its window pull); the hall is lit by the rig."""
    scene = json.loads((P4A / "scene_manifest.json").read_text(encoding="utf-8"))
    manifest = json.loads((P4A / "render_manifest.json").read_text(encoding="utf-8"))
    renders = {r["camera"]: r for r in manifest["renders"]}
    res = AB.resolve_views("real02", "skywin", scene)
    assert res["views"] == SKYWIN_REAL02 and not res["replaced"] and not res["dropped"]
    by_name = {c["name"]: c for c in scene["cameras"]}
    for v in AB.M13_SKYWIN_AB_VIEWS["real02"]:
        cam, entry = by_name[v["camera"]], renders[v["camera"]]
        assert cam["room_id"] == v["room_id"] and cam["kind"] == "interior" and entry["room_type"] == v["room_type"]
        assert cam.get("source") == "replayed", v["camera"]
        assert any(o.startswith(("win_", "d_")) for o in cam.get("visible_openings") or []), v["camera"]
        assert (entry.get("window_pull") or {}).get("pane_px", 0) > 30000, v["camera"]
    hall = renders["cam_r_L-1_koridor_2_1"]["exposure"]
    assert hall["wb_rig_share"] > 0.85
    assert all(renders[c]["exposure"]["wb_rig_share"] < 0.85 for c in SKYWIN_REAL02[:-1])


def _skywin_results(res: Path, views: list) -> None:
    for v in AB.M13_SKYWIN_AB_VARIANTS:
        d = res / v / "real02"
        d.mkdir(parents=True)
        lv = L.light_levers(v)
        strength, extra = M.world_strength_record(1.0, L.interior_sky_gain(lv), L.interior_sky_rays(lv))
        (d / "lighting.json").write_text(json.dumps({"lighting": {"world": {"kind": "hdri", "strength": strength,
                                                                              **extra}}}))
        renders = [{"camera": cam, "seconds": 6.0, "samples": 128, "window_pull": {"k": 2},
                    "exposure": {"ev": 1.0, "ev_raw": 1.0, "wb_temperature": 5600.0}} for cam in views]
        (d / "render_manifest.json").write_text(json.dumps({"renders": renders, "light_variant": {"build": v}}))


def test_the_summary_shows_what_the_camera_sees_at_a_windows_only_level(tmp_path):
    res = tmp_path / "ab_m13" / "skywin"
    views = SKYWIN_REAL02[:2]
    _skywin_results(res, views)
    summary = AB.lever_summary(res, ("real02",), AB.M13_SKYWIN_AB_VARIANTS, views={"real02": views},
                               view_set="skywin")
    rows = {(r["variant"], r["camera"]): r for r in summary["rows"]}
    win, whole, base = (rows[(v, views[0])] for v in ("skywin35", "sky35", "base"))
    assert (win["world_strength"], win["sky_stops"], win["sky_rays"]) == (1.0, 3.5, "camera_paths")
    assert win["world_strength_camera"] == pytest.approx(GAIN, abs=1e-6)
    assert whole["sky_rays"] == "all" and whole["world_strength_camera"] is None
    assert base["sky_rays"] == "all" and base["world_strength"] == 1.0
    md = (res / "summary.md").read_text()
    assert md.startswith("# Milestone 13 interior sky A/B, view set 'skywin'") and "windows-only level" in md
    assert "| real02 | skywin35 | cam_r_L-1_salon_1 | 1.0 (camera paths 11.313708) | 3.5 |" in md
    assert "| real02 | sky35 | cam_r_L-1_salon_1 | 11.313708" in md


def test_the_views_cli_resolves_the_windows_only_set(tmp_path, capsys):
    rooms = {v["camera"]: v["room_id"] for v in AB.M13_SKYWIN_AB_VIEWS["real02"]}
    cams = [_cam(n, rooms[n]) for n in SKYWIN_REAL02 if n != "cam_r_L0_yatak_odasi_1"]
    cams.append(_cam("cam_r_L0_yatak_odasi_2", "r_L0_yatak_odasi"))
    scene = tmp_path / "scene_manifest.json"
    scene.write_text(json.dumps({"cameras": cams}), encoding="utf-8")
    assert AB.main(["m13-views", "--project", "real02", "--view-set", "skywin", "--scene", str(scene)]) == 0
    out = capsys.readouterr()
    assert out.out.strip().split(",") == [n if n != "cam_r_L0_yatak_odasi_1" else "cam_r_L0_yatak_odasi_2"
                                          for n in SKYWIN_REAL02]
    assert "cam_r_L0_yatak_odasi_1 -> cam_r_L0_yatak_odasi_2" in out.err


def test_m13_p6_takes_the_view_set_and_the_folder_from_the_environment():
    text = P6_JOB.read_text(encoding="utf-8")
    subprocess.run(["bash", "-n", str(P6_JOB)], check=True)
    assert 'SKY_VIEW_SET="${P6_SKY_VIEW_SET:-sky}"' in text and 'SKY_NAME="${P6_SKY_NAME:-ab_m13/sky}"' in text
    # the P6c command in the header: real02 with its M11 cameras, the approved settings and the windows-only A/B
    for part in ("--env RUN_PROJECTS=real02", "'CAMERAS_FROM=results/renders/{name}/scene_manifest.json'",
                 "--env RUN_POLISH=off", "--env RENDER_SAMPLES=256", "--max-minutes 240", "--over-5-ok",
                 "--env P6_SKY_PROJECT=real02", "--env P6_SKY_VIEW_SET=skywin",
                 "'P6_SKY_VARIANTS=base skywin35 sky35'", "--env P6_SKY_NAME=ab_m13/skywin"):
        assert part in text, part


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_m13_p6_runs_the_windows_only_ab_on_real02(tmp_path):
    env = _p6_env(tmp_path, 3 * 3600, RUN_PROJECTS="real02", P6_SKY_PROJECT="real02", P6_SKY_VIEW_SET="skywin",
                  P6_SKY_VARIANTS=" ".join(AB.M13_SKYWIN_AB_VARIANTS), P6_SKY_NAME="ab_m13/skywin",
                  RENDER_SAMPLES="256", RUN_POLISH="off")
    proc = _run_p6(env, tmp_path / "repo")
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-2000:]
    ab = _ab_env(tmp_path)
    assert ab["AB_PROJECTS"] == "real02" and ab["AB_VARIANTS"] == "base skywin35 sky35"
    assert (ab["AB_VIEW_SET"], ab["AB_NAME"], ab["AB_SOURCE"], ab["AB_GPU_TESTS"]) == \
        ("skywin", "ab_m13/skywin", "run", "0")
    assert "views skywin into ab_m13/skywin" in proc.stdout
    # the defaults stay P6a's (guard; holds on 52d4bb8 too)
    env = _p6_env(tmp_path / "d", 3 * 3600)
    proc = _run_p6(env, tmp_path / "d" / "repo")
    assert proc.returncode == 0 and (_ab_env(tmp_path / "d")["AB_VIEW_SET"], _ab_env(tmp_path / "d")["AB_NAME"]) == \
        ("sky", "ab_m13/sky")
    # a folder outside the results or a bad set name fails fast, before the full run
    for i, bad in enumerate(({"P6_SKY_NAME": "../x"}, {"P6_SKY_NAME": "/abs"}, {"P6_SKY_VIEW_SET": "sky win"})):
        env = _p6_env(tmp_path / f"bad{i}", 3 * 3600, **bad)
        proc = _run_p6(env, tmp_path / f"bad{i}" / "repo")
        assert proc.returncode == 2, (bad, proc.stdout[-2000:])
        assert not (tmp_path / f"bad{i}" / "fakes" / "full.env").exists()


# --------------------------------------------------------------------------
# Asks: cli --clamp-indirect, the scene camera's frame keys, curtains under the slope, lamp shades in S2
# --------------------------------------------------------------------------

def test_cli_render_passes_the_indirect_clamp(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli, "run_blender", lambda script, args, **kw: calls.append(list(args)))
    base = ["render", "--scene", str(tmp_path / "s.blend"), "--out", str(tmp_path / "r")]
    assert cli.main(base + ["--clamp-indirect", "100"]) == 0
    assert calls[-1][calls[-1].index("--clamp-indirect") + 1] == "100"
    assert cli.main(base + ["--clamp-indirect", "0"]) == 0 and calls[-1][-2:] == ["--clamp-indirect", "0"]
    cli.render(str(tmp_path / "s.blend"), str(tmp_path / "r"), clamp_indirect=12.5)
    assert calls[-1][-2:] == ["--clamp-indirect", "12.5"]
    assert cli.main(base) == 0 and "--clamp-indirect" not in calls[-1]       # no flag: the command line as before
    # the flag render.py reads (R_render's, pinned there): the same name and the value as a number
    from wenart.blender import render as R
    assert R.parse_args(["--out", "x", "--clamp-indirect", "100"]).clamp_indirect == 100.0


def _camera(**extra) -> dict:
    cam = {"name": "ext_front_entrance", "room_id": None, "level_id": None, "index": 1, "position": [8.6, 17.5, 1.6],
           "target": [8.6, 6.0, 1.6], "lens_mm": 26.0, "sensor_mm": 36.0, "resolution": [1920, 1080],
           "visible_openings": [], "visible_furniture": [], "warning": None, "kind": "exterior", "policy": "agent"}
    cam.update(extra)
    return cam


def test_the_scene_camera_frame_keys_are_typed():
    ok = _camera(fill=2.3449, fits=False, sky_share=0.0, frame_target=[8.3605, 12.5019, 1.6])
    jsonschema.validate(ok, S.SCENE_CAMERA)
    jsonschema.validate(_camera(), S.SCENE_CAMERA)                        # all optional
    for bad in ({"fits": "no"}, {"sky_share": 1.5}, {"sky_share": -0.1}, {"fill": -1.0}, {"fill": "2.3"},
                {"frame_target": [1.0, 2.0]}):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(_camera(**bad), S.SCENE_CAMERA)


EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def _attic():
    prep = B.prepare(EXAMPLE, "base")       # the example's attic: knee wall 0.87 m at y 0.6, slope to 2.23 m at y 2.4
    return prep, prep["building"]["levels"][-1]


def test_curtains_and_blinds_stay_under_the_slope():
    """The builder's bound (D_decor's ask, verify:look:1 step 5): a hostless curtain or blind keeps its top 2 cm under
    the slope over it, its bottom kept; too little left (<= 0.3 m) is not built; a flat ceiling or a hosted item is
    left alone."""
    from wenart.blender import furniture as F
    from wenart.furniture import decor as D

    assert (B.WINDOW_DECOR_TYPES, B.WINDOW_DECOR_CEILING_CLEAR_M) == (D.WINDOW_DECOR_TYPES,
                                                                      D.WINDOW_DECOR_CEILING_CLEAR_M)
    prep, attic = _attic()
    b = copy.deepcopy(prep["building"])
    room = "r_L1_oyun_odasi"
    ceiling = {y: F.ceiling_above(attic, (3.0, y), (1.6, depth), 0.0)[0] for y, depth in ((1.2, 0.08), (0.3, 0.06),
                                                                                          (4.0, 0.08))}
    # the blind by the knee wall: 0.3 m or less left under the slope; the curtain on the slope: shorter; the flat part
    assert ceiling[0.3] - 0.02 - 0.6 <= 0.3 < ceiling[1.2] - 0.02 - 0.8 < 1.45 and 0.8 + 1.45 + 0.02 <= ceiling[4.0]
    b["decor"] = [
        {"id": "dec_curtain_slope", "type": "curtain", "level_id": "L1", "room_id": room, "host_id": None,
         "center": [3.0, 1.2, 0.8], "size": [1.6, 0.08, 1.45], "rotation_deg": 0.0},
        {"id": "dec_blind_knee", "type": "blind", "level_id": "L1", "room_id": room, "host_id": None,
         "center": [3.0, 0.3, 0.6], "size": [1.6, 0.06, 0.48], "rotation_deg": 0.0},
        {"id": "dec_curtain_flat", "type": "curtain", "level_id": "L1", "room_id": room, "host_id": None,
         "center": [3.0, 4.0, 0.8], "size": [1.6, 0.08, 1.45], "rotation_deg": 0.0},
        {"id": "dec_curtain_nobottom", "type": "curtain", "level_id": "L1", "room_id": room, "host_id": None,
         "center": [3.0, 1.2], "size": [1.6, 0.08, 1.45], "rotation_deg": 0.0},
    ]
    before = copy.deepcopy(b["decor"])
    decor, warnings, not_built = B.decor_under_roof(b, attic)
    assert b["decor"] == before                                                   # the building is not changed
    by_id = {d["id"]: d for d in decor}
    assert sorted(by_id) == ["dec_curtain_flat", "dec_curtain_nobottom", "dec_curtain_slope"]
    slope = by_id["dec_curtain_slope"]
    assert slope["center"] == [3.0, 1.2, 0.8] and slope["size"][:2] == [1.6, 0.08]
    assert slope["size"][2] == pytest.approx(ceiling[1.2] - 0.02 - 0.8, abs=1e-4)
    assert by_id["dec_curtain_flat"] == before[2] and by_id["dec_curtain_nobottom"] == before[3]
    assert [n["id"] for n in not_built] == ["dec_blind_knee"] and "<= 0.3 m" in not_built[0]["reason"]
    assert sorted(w.split(":")[0] for w in warnings) == ["dec_blind_knee", "dec_curtain_slope"]
    assert "shorter from the top" in next(w for w in warnings if w.startswith("dec_curtain_slope"))
    # a level without a roof keeps its window decor as it is (guard; holds on 52d4bb8 too)
    ground = next(lv for lv in prep["building"]["levels"] if lv["id"] == "L0")
    assert B.decor_under_roof(b, ground) == (b["decor"], [], [])


def _cylinder(cx, cy, r, z0, z1, n=16, closed=True):
    verts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for z in (z0, z1)
             for i in range(n)]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    if closed:
        faces += [list(range(n))[::-1], list(range(n, 2 * n))]
    return verts, faces


def _lamp(cx, cy, shade_r, z0=1.2, z1=1.6):
    """A floor lamp as most are built: a closed pole and an open fabric drum (no top, no bottom) at z0-z1."""
    pv, pf = _cylinder(cx, cy, 0.015, 0.0, z0 + 0.05, 8)
    sv, sf = _cylinder(cx, cy, shade_r, z0, z1, 24, closed=False)
    return {"verts": pv + sv, "faces": pf + [[i + len(pv) for i in f] for f in sf], "method": "library"}


def _lamp_piece(pid, cx, cy, size, ftype="floor_lamp"):
    return {"id": pid, "type": ftype, "level_id": "L0", "room_id": "r", "status": "verified",
            "footprint": {"center": [cx, cy], "size": [size, size], "rotation_deg": 0.0},
            "asset": {"method": "library"}}


def test_two_floor_lamp_shades_through_each_other_are_an_s2_violation():
    building = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [], "walls": [],
                "furniture": [_lamp_piece("f_a", 5.30, 0.74, 0.59), _lamp_piece("f_b", 5.68, 1.02, 0.44),
                              _lamp_piece("f_c", 8.0, 0.74, 0.59), _lamp_piece("f_d", 8.55, 0.74, 0.44)]}
    # P6a's real04 pair f_L-1_063 / f_L-1_064: shades of 0.59 m and 0.44 m, 0.47 m apart (4 cm through each other);
    # f_c / f_d stand 0.55 m apart, their shades 3.5 cm clear of each other
    meshes = {"f_a": _lamp(5.30, 0.74, 0.295), "f_b": _lamp(5.68, 1.02, 0.22), "f_c": _lamp(8.0, 0.74, 0.295),
              "f_d": _lamp(8.55, 0.74, 0.22)}
    report = SC.measure_pure(meshes, building)
    s2 = [v for v in report["violations"] if v["check"] == "S2"]
    assert [(v["target"], v["metrics"]["other"]) for v in s2] == [("f_a", "f_b")]
    assert s2[0]["metrics"]["shade"] is True and "shades overlap" in s2[0]["message"]
    assert s2[0]["metrics"]["depth_m"] == pytest.approx(0.295 + 0.22 - math.hypot(0.38, 0.28), abs=0.01)
    assert SC.shade_overlap(meshes["f_c"]["verts"], meshes["f_d"]["verts"]) == 0.0
    # the shade: the circle inside the box of the vertices in the top 35 % (a round shade keeps its radius)
    cx, cy, r, z0, z1 = SC.shade_disc(meshes["f_a"]["verts"])
    assert (cx, cy, r, z1) == (pytest.approx(5.3), pytest.approx(0.74), pytest.approx(0.295), 1.6)
    assert z0 == pytest.approx(1.6 - SC.LAMP_SHADE_SHARE * 1.6)
    # shades at heights that do not meet are apart
    assert SC.shade_overlap(_lamp(5.30, 0.74, 0.295, 0.3, 0.7)["verts"], meshes["f_b"]["verts"]) == 0.0
    # guard (holds on 52d4bb8 too): a lamp beside an armchair keeps the mesh test, which finds the open drum's
    # vertices inside the closed chair
    building["furniture"].append(_lamp_piece("f_e", 8.0, 2.0, 0.6, "armchair"))
    chair_verts, chair_faces = _cylinder(8.0, 2.0, 0.3, 0.0, 1.0, 16)
    meshes["f_e"] = {"verts": chair_verts, "faces": chair_faces}
    meshes["f_g"] = _lamp(8.0, 2.0, 0.2, 0.5, 0.9)
    building["furniture"].append(_lamp_piece("f_g", 8.0, 2.0, 0.4))
    s2 = [v for v in SC.measure_pure(meshes, building)["violations"] if v["check"] == "S2"]
    assert {(v["target"], v["metrics"]["other"]) for v in s2} == {("f_a", "f_b"), ("f_e", "f_g")}
    assert "shade" not in next(v for v in s2 if v["target"] == "f_e")["metrics"]
