"""Milestone 13 track T5 GPU tests (docs/milestone13.md §13.1, pod P1; ``pytest -m gpu tests/gpu/test_m13_light.py``;
skipped without a Blender binary): one small scene built and rendered per light variant, the EV within the run's
limits, the sun disc visible in the exterior world and its irradiance measured against the sun lamp.

- ``test_every_variant_builds_and_renders_within_its_limits``: synthetic-01 level L0 (the ingest pipeline's
  building, flat colours) built with ``WENART_LIGHT_VARIANT`` = base, sun300, evcap, rig, shell, all through the real
  build script and two interior views rendered at 320 x 180, 16 samples, ``--white-balance project``. Checks: the
  scene manifest's ``lighting`` block records the variant, the levers and the sun (constant x mood factor); the rig
  fixtures and the shell records appear only under their levers; every render entry's EV lies within the manifest's
  ``exposure_limits`` (-2..+8 for base and the single sun / rig / shell variants, -2..+3 under the cap), a
  ``lighting_dark`` entry exists exactly when the metered EV passed the cap; one project whitepoint for every view;
  ``vram_mib`` recorded on the GPU.
- ``test_exterior_sky_carries_a_visible_sun_disc``: the exterior world of ``materials.exterior_world_nodes``
  (sun disc on) rendered from a camera looking at the sun: the disc's pixels are far brighter than the sky beside
  them; a white plane facing the sun lit by the sky alone (lamp hidden, as render.py does under that world) and by
  the lamp alone gives the disc / lamp irradiance ratio, printed as ``SUN_DISC_RATIO`` (the calibration number of
  ``materials.EXTERIOR_SUN_DISC_REFERENCE_WM2`` for the lead) and required within a factor of 20 of 1.
"""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cli
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import render as R
from wenart.ingest.pipeline import build_project

pytestmark = pytest.mark.gpu
if cli.find_blender() is None:
    # Skipped at import on a CPU machine (as tests/gpu/test_m13_modules.py and test_m13_site.py do): pytest keys test
    # modules by basename here (no test packages), so the CPU twin tests/test_m13_light.py of docs/milestone13.md
    # §13.1 can only be collected when this module is not; the pods run `pytest -m gpu tests/gpu/<file>` explicitly.
    pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender, PATH)",
                allow_module_level=True)

ROOT = Path(__file__).resolve().parents[2]
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                   "/workspace/tools/blender, /opt/wenart/blender, PATH)")
VARIANTS = ("base", "sun300", "evcap", "rig", "shell", "all")
CAMERAS = "cam_r_L0_salon_1,cam_r_L0_banyo_1"          # a daylight living room and a windowless bath of synthetic-01


@pytest.fixture(scope="module")
def building(tmp_path_factory):
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("m13light")
    build_project(ROOT / "projects" / "synthetic-01", tmp / "pipeline")
    return tmp / "pipeline" / "building.json", tmp


@needs_blender
@pytest.mark.parametrize("variant", VARIANTS)
def test_every_variant_builds_and_renders_within_its_limits(building, variant, monkeypatch):
    path, tmp = building
    monkeypatch.setenv(L.LIGHT_VARIANT_ENV, variant)
    levers = L.light_levers(variant)
    out = tmp / variant / "scene"
    cli.build(path, out, level="L0", no_textures=True, preview_samples=4)
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    light = manifest["lighting"]
    assert light["variant"] == variant and manifest["light_variant"] == variant
    assert light["levers"]["sun_wm2"] == levers["sun_wm2"] and light["levers"]["ev_cap"] == levers["ev_cap"]
    assert light["sun"]["strength"] == pytest.approx(levers["sun_wm2"] * light["sun"]["mood_factor"])
    assert light["sun"]["strength_wm2_constant"] == L.SUN_STRENGTH_WM2
    rig_objects = [o for o in manifest["objects"] if o.get("method") == "rig"]
    if levers["rig"]:
        assert light["rig"]["on"] and rig_objects and light["rig"]["lights"], "the rig fixtures are built"
        assert all(o["status"] == "assumed" and o["assumed"]["lumens"] for o in rig_objects)
    else:
        assert not light["rig"]["on"] and not rig_objects and not light["rig"]["lights"]
    shell_records = [m for m in manifest["materials"].values() if m.get("shell_slot")]
    if levers["shell"]:
        assert shell_records, "the shell slots (ceiling, worktop, fronts, ceramic, tiles) carry the layers"
        assert all(m["shell_layers"]["applied"] for m in shell_records)
    else:
        assert not shell_records
    renders = tmp / variant / "renders"
    cli.render(out / "scene.blend", renders, cameras=CAMERAS, samples=16, res="320x180", white_balance="project")
    rm = json.loads((renders / "render_manifest.json").read_text(encoding="utf-8"))
    assert rm["light_variant"] == {"render": variant, "build": variant}
    limits = rm["exposure_limits"]
    assert limits == list(R.exposure_limits_for(levers))
    assert rm["white_balance_project"] and rm["white_balance_project"]["whitepoint"]
    wps = {tuple(r["exposure"]["whitepoint"]) for r in rm["renders"]}
    assert len(wps) == 1, "one whitepoint for every view of the project"
    for r in rm["renders"]:
        ex = r["exposure"]
        assert limits[0] <= ex["ev"] <= limits[1] + 1e-9, (r["camera"], ex["ev"], limits)
        assert ex["wb_mode"] == "project" and ex.get("wb_source")
        wanted_dark = ex["ev_raw"] is not None and ex["ev_raw"] > limits[1]
        assert bool(ex.get("lighting_dark")) == wanted_dark, (r["camera"], ex["ev_raw"], limits)
        if wanted_dark:
            assert ex["lighting_dark"]["check"] == "lighting_dark" and ex["lighting_dark"]["target"] == r["camera"]
            assert r["camera"] in [d["target"] for d in rm["lighting_dark"]]
        if rm["device"] != "CPU":
            assert isinstance(r.get("vram_mib"), int) and r["vram_mib"] > 0
        assert r["seconds"] > 0
    print(f"M13_VARIANT {variant}: " + "; ".join(f"{r['camera']} ev={r['exposure']['ev']:+.2f} "
                                                    f"raw={r['exposure']['ev_raw']} p50={r['exposure']['incident_p50']} "
                                                    f"dark={bool(r['exposure'].get('lighting_dark'))} "
                                                    f"vram={r.get('vram_mib')}" for r in rm["renders"]))


SUN_DISC_SCRIPT = textwrap.dedent("""
    import json, math, sys
    sys.path.insert(0, {root!r})
    import bpy
    from mathutils import Vector
    from wenart.blender import lighting as L
    from wenart.blender import materials as M
    from wenart.blender import render as R
    out = {out!r}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = 96, 54
    scene.render.resolution_percentage = 100
    lighting = {{"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 210.0}}
    rec = M.exterior_world_nodes(scene, lighting, sun_disc=True, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                                 sun_wm2=300.0)
    scene.world = bpy.data.worlds[M.EXTERIOR_WORLD]
    d = Vector(L.sun_direction(35.0, 210.0))
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 300.0; sun.angle = math.radians(0.53)
    sob = bpy.data.objects.new("sun", sun); sob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sob); sob["wenart_id"] = "sun"
    # 1. a camera looking at the sun: the disc against the sky
    cam = bpy.data.cameras.new("c"); cam.lens = 50.0
    cob = bpy.data.objects.new("c", cam); cob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cob); scene.camera = cob
    sob.hide_render = True
    scene.render.image_settings.file_format = "OPEN_EXR"; scene.render.image_settings.color_depth = "32"
    scene.view_settings.view_transform = "Standard"
    scene.render.filepath = out + "/sky.exr"
    bpy.ops.render.render(write_still=True)
    ch = R.read_exr(out + "/sky.exr")
    import numpy as np
    rgb = R.find_rgb(ch, "Combined", "ViewLayer.Combined")
    if rgb is None:
        rgb = np.stack([v for k, v in ch.items() if k.endswith((".R", ".G", ".B"))][:3], axis=-1)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    h, w = lum.shape
    centre = float(lum[h // 2 - 2: h // 2 + 3, w // 2 - 2: w // 2 + 3].max())
    edge = float(np.median(lum[:, : w // 4]))
    # 2. a white plane facing the sun: the sky's disc alone vs the lamp alone (diffuse direct at the centre)
    bpy.data.objects.remove(cob)
    mesh = bpy.data.meshes.new("p"); mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [[0, 1, 2, 3]])
    mesh.update(); pob = bpy.data.objects.new("p", mesh); scene.collection.objects.link(pob)
    pob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    mat = bpy.data.materials.new("white"); mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    cam2 = bpy.data.cameras.new("c2"); cam2.type = "ORTHO"; cam2.ortho_scale = 0.5
    cob2 = bpy.data.objects.new("c2", cam2); cob2.location = d * 2.0
    cob2.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cob2); scene.camera = cob2
    vl = scene.view_layers[0]; vl.use_pass_diffuse_direct = True
    scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    def direct(path):
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        c = R.read_exr(path)
        arr = R.find_rgb(c, "Diffuse Direct", "DiffDir")
        return float(np.median(0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]))
    sob.hide_render = True
    sky_only = direct(out + "/disc.exr")
    black = bpy.data.worlds.new("black"); black.use_nodes = True
    black.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    scene.world = black; sob.hide_render = False
    lamp_only = direct(out + "/lamp.exr")
    json.dump({{"record": rec, "disc_centre": centre, "sky_edge": edge, "sky_only_direct": sky_only,
               "lamp_only_direct": lamp_only}}, open(out + "/sun_disc.json", "w"))
    print("SUN_DISC_DONE")
""")


@needs_blender
def test_exterior_sky_carries_a_visible_sun_disc(tmp_path):
    script = SUN_DISC_SCRIPT.format(root=str(ROOT), out=str(tmp_path))
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", script],
                          capture_output=True, text=True, timeout=900, cwd=str(ROOT),
                          env=dict(os.environ, WENART_LIGHT_VARIANT=""))
    assert proc.returncode == 0 and "SUN_DISC_DONE" in proc.stdout, proc.stdout[-3000:] + proc.stderr[-3000:]
    data = json.loads((tmp_path / "sun_disc.json").read_text(encoding="utf-8"))
    rec = data["record"]
    # the disc's intensity is 300 W/m2 over the reference x the world's strength (0.5 for warm daylight) = 0.6
    assert rec["sun_disc"] is True and rec["direct_sun"] == "sky disc"
    assert rec["sun_intensity"] == pytest.approx(M.sky_sun_intensity(300.0, world_strength=rec["strength"])) == pytest.approx(0.6)
    assert data["disc_centre"] > 20.0 * max(data["sky_edge"], 1e-6), "the sun disc is far brighter than the sky"
    assert data["sky_only_direct"] > 0 and data["lamp_only_direct"] > 0
    ratio = data["sky_only_direct"] / data["lamp_only_direct"]
    print(f"SUN_DISC_RATIO disc/lamp = {ratio:.3f} (sky-only direct {data['sky_only_direct']:.4f}, lamp-only "
          f"{data['lamp_only_direct']:.4f}; reference {rec['sun_disc_reference_wm2']} W/m2, sun 300 W/m2)")
    assert 1.0 / 20.0 <= ratio <= 20.0, f"the disc's irradiance is off the lamp's by more than 20x: {ratio}"
