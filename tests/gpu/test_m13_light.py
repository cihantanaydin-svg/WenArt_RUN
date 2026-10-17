"""Milestone 13 track T5 GPU tests (docs/milestone13.md §13.1, pod P1; round 3 §14.3, pod P3; ``pytest -m gpu
tests/gpu/test_m13_light.py``; skipped without a Blender binary): one small scene built and rendered per light
variant, the EV within the run's limits, the project white point metered on daylight, the sun disc visible in the
exterior world while the lamp stays the one direct sun.

- ``test_every_variant_builds_and_renders_within_its_limits``: synthetic-01 level L0 (the ingest pipeline's
  building, flat colours) built with ``WENART_LIGHT_VARIANT`` = m11, base, sun300, evcap, rig, shell, all through
  the real build script and two interior views rendered at 320 x 180, 16 samples, ``--white-balance project``.
  Checks: the scene manifest's ``lighting`` block records the variant, the levers and the sun (constant x mood
  factor); the rig fixtures and the shell records appear exactly under their levers (round 3: ``base`` = production
  has both, ``m11`` neither); every render entry's EV lies within its own ``limits`` (the manifest's ``exposure_limits`` with the floor
  moved down for the scene's sun, ``render.sun_floor_shift``, pre-flight of P3; the cap -2..+8 for
  m11 and the single sun / rig / shell variants, -2..+3 under the cap), a ``lighting_dark`` entry exists exactly
  when the metered EV passed the cap; one project whitepoint for every view, metered on daylight (every rig object
  hidden; the daylight candidate with the most incident light, a sunlit room under a sun of 300 W/m² or more, its
  white point within ``SUNLIT_WB_K``; ``kelvin`` and the candidates recorded); ``vram_mib`` recorded on the GPU.
  Fix round after P3 (16-17 Oct 2026): the project white point is the anchor of every view
  (``wb_project_whitepoint``); a view's own white point is the anchor mixed with the rig's colour by its rig share
  (``render.mixed_whitepoint``), the anchor itself without the rig or below ``render.WB_RIG_SHARE_MIN``.
  Fix round part 2 (17 Oct 2026): that rule reads each view's own share, so two pins that do not: with the rig on,
  the sunlit living room keeps the project white point (share under ``render.WB_RIG_SHARE_MIN``, no mired shift)
  and the bath lit mostly by its rig has a share of at least ``RIG_ONLY_MIN_SHARE`` and a warmer white point.
  Fix round after P4a (17 Oct 2026): every view keeps the project's daylight cast (``render.mixed_whitepoint`` with
  the rig part's extra warmth ``render.WB_RIG_RESIDUAL``, recorded as ``wb_rig_residual``); the rule above recomputes
  each view's white point with it, so a manifest rendered with m13.2 no longer passes (re-run on m13.3 renders).
  Fix round after P4b (17 Oct 2026): ``wb_rig_kelvin`` is no longer ``lighting.RIG_WARM_K`` for every view: a view is
  balanced for its own room's rig lights (``render.room_rig_kelvin``, ``wb_rig_kelvin_source`` ``room``), the scene's
  first rig light when its room has none (``scene``); the expected value comes from the scene manifest's rig lights
  (``rig_kelvin_from_manifest``), so the build may give halls, stairs and baths a neutral temperature.
- ``test_exterior_sky_carries_a_visible_sun_disc``: the exterior world of ``materials.exterior_world_nodes`` (the
  round-3 world: the disc for camera rays only) rendered from a camera looking at the sun: the disc's pixels are far
  brighter than the sky beside them. Then a white plane facing the sun measures the Diffuse Direct light of (a) the
  production world with the lamp hidden, (b) the P1 world (the disc for every ray) with the lamp hidden, (c) the sky
  without a disc, (d) the lamp alone under a black world. ``SUN_DISC_RATIO`` = (b - c) / d is the disc's own direct
  light against the lamp's (the calibration number of ``materials.EXTERIOR_SUN_DISC_REFERENCE_WM2`` for the lead;
  required within a factor of 20 of 1), and (a - c) / d must be near zero: under the camera-ray mix the sky lights
  the scene like the disc-less sky, so the lamp is the only sun light. Round 4 (§14.8): the sky world is the lamp's
  pair (``materials.exterior_sky_strength``), so (b - c) / d over the record's ``sun_intensity`` (the sky's own sun
  at sun_intensity 1) is 1 within 5 %, and the disc-less sky over the lamp on a horizontal plane (e, f) is the
  record's clear-sky ratio within 10 % and inside ``materials.CLEAR_SKY_DIFFUSE_RANGE``. The Blender script prints its own traceback
  and exits non-zero per part (P1: the failure after ``Saved: sky.exr`` was invisible in the captured tail; its
  causes were a plain-EXR read through the multilayer pass names and ``file_format = "OPEN_EXR_MULTILAYER"`` set
  without ``media_type``, both fixed by ``render.set_output``).
- ``test_sky_sun_table_rows_reproduce`` (round-4 review): rows of ``materials.SKY_SUN_TABLE`` away from 35 degrees
  (12, 45, 65: the golden-evening, overcast and bright-noon suns) re-measured with the table's own method.
"""
from __future__ import annotations

import json
import os
import subprocess
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
VARIANTS = ("m11", "base", "sun300", "evcap", "rig", "shell", "all")
CAMERAS = "cam_r_L0_salon_1,cam_r_L0_banyo_1"          # a sunlit living room and a sky-lit bath of synthetic-01
# Fix round part 2 (17 Oct 2026): the white-balance pins of the two views (rig on): the living room (three windows)
# keeps the project white point; the bath (one small sky-lit window, win_L0_006; its rig: a mirror light and a
# ceiling fixture) is lit mostly by the rig.
DAYLIGHT_CAMERA, RIG_ONLY_CAMERA = CAMERAS.split(",")
RIG_ONLY_MIN_SHARE = 0.5                # the bath's rig share (bpy 5.2.2 shim run of part 1: 0.819-0.824)
# The white point is metered on daylight (rig hidden): up to render.WB_METER_MAX_CAMERAS cameras of rooms with a
# window portal (rooms whose window faces the sun first) and the one with the most incident light wins. Round-3
# review (16 Oct 2026, a local bpy 5.2.2 run of this test): the first windowed room in name order,
# cam_r_L0_banyo_1, gets skylight only and metered 9,068 K under the 1000 W/m2 sun (the sunlit living room then
# rendered orange); under a real sun the white point must sit near daylight. The ordering and the choice are
# pinned pure in tests/test_m13_light.py.
SUNLIT_WB_K = (4000.0, 7000.0)          # the white point when the sun (>= 300 W/m2) lights the metered room


def rig_lights_from_manifest(manifest: dict) -> list[tuple]:
    """``[(room_id, kelvin, watts)]`` of the scene manifest's rig lights (kind ``light`` with ``assumed.rig``; their
    ``parent`` is the room, ``assumed.temperature_k`` / ``power_w`` the fixture's), in manifest order (fix round
    after P4b, 17 Oct 2026)."""
    out = []
    for o in manifest.get("objects") or []:
        a = o.get("assumed") or {}
        if o.get("kind") == "light" and a.get("rig") and a.get("temperature_k"):
            out.append((o.get("parent"), float(a["temperature_k"]), float(a.get("power_w") or 0.0)))
    return out


def rig_kelvin_from_manifest(manifest: dict, room_id) -> tuple:
    """The temperature a view of ``room_id`` must be balanced for (``render.room_rig_kelvin`` on the manifest's rig
    lights) and its source (``room`` | ``scene``)."""
    return R.room_rig_kelvin(rig_lights_from_manifest(manifest), room_id)


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
    assert light["sun"]["strength_wm2_constant"] == L.SUN_STRENGTH_WM2 == 1000.0
    rig_objects = [o for o in manifest["objects"] if o.get("method") == "rig"]
    if levers["rig"]:
        assert light["rig"]["on"] and rig_objects and light["rig"]["lights"], "the rig fixtures are built"
        assert all(o["status"] == "assumed" and o["assumed"]["lumens"] for o in rig_objects)
        # round 3: gain 2.0 and the shade's fixed radiance under the clip bound
        assert light["rig"]["gain"] == L.RIG_GAIN == 2.0
        assert light["rig"]["shade_emission_wm2sr"] == L.SHADE_EMISSION_WM2SR < light["rig"]["shade_emission_bound"]
        assert all(o["assumed"]["gain"] == 2.0 and o["assumed"]["shade_emission_wm2sr"] == L.SHADE_EMISSION_WM2SR
                   for o in rig_objects)
    else:
        assert not light["rig"]["on"] and not rig_objects and not light["rig"]["lights"]
    shell_records = [m for m in manifest["materials"].values() if m.get("shell_slot")]
    if levers["shell"]:
        assert shell_records, "the shell slots (ceiling, worktop, fronts, ceramic, tiles) carry the layers"
        assert all(m["shell_layers"]["applied"] for m in shell_records)
        # the ceiling slot's material carries the slot in its name (never a .001 twin of the walls' plaster)
        assert all(name.endswith("__ceiling") or "__ceiling__" in name for name, m in manifest["materials"].items()
                   if m.get("shell_slot") == "ceiling")
        assert not any(name.startswith("plaster_white") and name.endswith(".001") for name in manifest["materials"])
    else:
        assert not shell_records
    renders = tmp / variant / "renders"
    cli.render(out / "scene.blend", renders, cameras=CAMERAS, samples=16, res="320x180", white_balance="project")
    rm = json.loads((renders / "render_manifest.json").read_text(encoding="utf-8"))
    assert rm["light_variant"] == {"render": variant, "build": variant}
    limits = rm["exposure_limits"]
    assert limits == list(R.exposure_limits_for(levers))
    wbp = rm["white_balance_project"]
    print(f"M13_WB {variant}: " + json.dumps({k: wbp.get(k) for k in ("kelvin", "tint", "metered_on", "candidates",
                                                                      "sunlit_rooms", "daylight_rooms")}))
    assert wbp and wbp["whitepoint"]
    # round 3: the project white point comes from daylight: cameras of rooms with a window (sunlit ones first),
    # every rig object hidden while metering, the candidate with the most incident light, Blender's kelvin recorded
    assert wbp["daylight_only"] is True and wbp["metered_on"] == wbp["from_camera"] and wbp["daylight_camera"] is True
    assert wbp["kelvin"] > 1800 and wbp["source"].startswith(f"metered on {wbp['metered_on']}")
    assert (wbp["rig_objects_hidden"] > 0) == bool(levers["rig"])
    cands = wbp["candidates"]
    assert 1 <= len(cands) <= R.WB_METER_MAX_CAMERAS and [c["camera"] for c in cands] == wbp["tried"]
    chosen = next(c for c in cands if c["camera"] == wbp["metered_on"])
    assert chosen["daylight"] and chosen["incident_p50"] == max(c["incident_p50"] or 0.0 for c in cands
                                                                if c["daylight"] and c["kelvin"])
    if levers["sun_wm2"] >= 300.0:
        # a real sun: a sunlit room is metered and the white point is daylight, not the blue of a sky-lit window
        assert wbp["sunlit_rooms"] and wbp["sunlit_camera"] is True, wbp
        assert SUNLIT_WB_K[0] <= wbp["kelvin"] <= SUNLIT_WB_K[1], wbp
    # Fix round after P3 (16-17 Oct 2026): one project white point (the anchor, metered on daylight) for every view;
    # each view's own white point is the anchor mixed with the rig's light colour by the view's rig share
    # (render.mixed_whitepoint; P3 put the 2700 K rig under the 5,635 K daylight point and 24 of 48 views turned
    # orange). Without the rig, or below WB_RIG_SHARE_MIN, a view keeps the anchor exactly.
    anchor = [float(v) for v in wbp["whitepoint"]]
    for r in rm["renders"]:
        ex = r["exposure"]
        assert ex["wb_project_whitepoint"] == pytest.approx(anchor, abs=1e-6), r["camera"]
        share = ex.get("wb_rig_share")
        if not levers["rig"]:
            assert share is None and ex["whitepoint"] == pytest.approx(anchor, abs=1e-6), (r["camera"], ex)
            continue
        assert share is not None and 0.0 <= share <= 1.0, (r["camera"], ex)
        # fix round after P4b (17 Oct 2026): the view is balanced for its own room's rig lights (render.room_rig_kelvin;
        # the build may light halls, stairs and baths at a neutral temperature), the scene's first rig light only when
        # its room has none (scene order: any of the scene's rig temperatures)
        kelvin, source = rig_kelvin_from_manifest(manifest, r.get("room_id"))
        temps = {k for _r, k, _e in rig_lights_from_manifest(manifest)}
        assert ex["wb_rig_kelvin_source"] == source, (r["camera"], ex, source)
        assert (ex["wb_rig_kelvin"] == kelvin) if source == "room" else (ex["wb_rig_kelvin"] in temps), \
            (r["camera"], ex["wb_rig_kelvin"], kelvin, temps)
        # fix round part 2 (17 Oct 2026): the mixing rule below reads the view's own share, so it cannot see a share
        # that is wrong; two pins that do not: the daylight living room keeps the project white point (bpy 5.2.2
        # shim run of part 1: share 0.0 in base, rig and all), the bath lit mostly by its rig is corrected toward
        # the rig (0.82 there; a share stuck at 0 would leave it orange, as P3's baths)
        if r["camera"] == DAYLIGHT_CAMERA:
            assert share < R.WB_RIG_SHARE_MIN and ex["whitepoint"] == pytest.approx(anchor, abs=1e-6), (r["camera"], ex)
            assert abs(ex["wb_view_shift_mired"]) <= 0.5, (r["camera"], ex)
        elif r["camera"] == RIG_ONLY_CAMERA:
            assert share >= RIG_ONLY_MIN_SHARE and ex["wb_view_shift_mired"] > 0.0, (r["camera"], ex)
        if share < R.WB_RIG_SHARE_MIN:
            assert ex["whitepoint"] == pytest.approx(anchor, abs=1e-6), (r["camera"], ex)
        else:
            # fix round after P4a (17 Oct 2026): with the rig part's extra warmth the view was mixed with
            want = R.mixed_whitepoint(anchor, ex["wb_rig_whitepoint"], share, wbp["residual"], ex.get("wb_rig_residual"))
            assert ex["whitepoint"] == pytest.approx(want, abs=1e-5) and ex["wb_view_rule"] == R.WB_VIEW_RULE
            assert ex.get("wb_rig_residual") == R.WB_RIG_RESIDUAL, (r["camera"], ex)       # fix round after P4a
            assert ex["wb_view_shift_mired"] >= -0.5, (r["camera"], ex)     # toward the warm rig, never cooler
        print(f"M13_WB_VIEW {variant} {r['camera']}: rig share {share} -> {ex['wb_temperature']} K "
              f"(shift {ex.get('wb_view_shift_mired')} mired; {ex['wb_view_rule']})")
    # pre-flight of P3 (16 Oct 2026): the floor moves down with the scene's sun (render.sun_floor_shift); the cap of
    # exposure_limits stays, and each view is metered against its own ``limits``
    floor = rm["exposure_floor"]
    assert floor["shift_stops"] == pytest.approx(R.sun_floor_shift(light["sun"]["strength"]), abs=1e-4)
    assert floor["view_limits"] == list(R.view_limits(limits, floor["shift_stops"]))
    for r in rm["renders"]:
        ex = r["exposure"]
        assert ex["limits"] == floor["view_limits"] and ex["limits"][1] == limits[1]
        assert ex["limits"][0] <= ex["ev"] <= limits[1] + 1e-9, (r["camera"], ex["ev"], ex["limits"])
        assert ex["wb_mode"] == "project" and ex.get("wb_source")
        wanted_dark = ex["ev_raw"] is not None and ex["ev_raw"] > limits[1]
        assert bool(ex.get("lighting_dark")) == wanted_dark, (r["camera"], ex["ev_raw"], limits)
        if wanted_dark:
            assert ex["lighting_dark"]["check"] == "lighting_dark" and ex["lighting_dark"]["target"] == r["camera"]
            assert r["camera"] in [d["target"] for d in rm["lighting_dark"]]
        if rm["device"] != "CPU":
            assert isinstance(r.get("vram_mib"), int) and r["vram_mib"] > 0
        assert r["seconds"] > 0
    print(f"M13_VARIANT {variant}: wb={wbp['kelvin']}K on {wbp['metered_on']} (rig hidden {wbp['rig_objects_hidden']}); "
          + "; ".join(f"{r['camera']} ev={r['exposure']['ev']:+.2f} raw={r['exposure']['ev_raw']} "
                      f"p50={r['exposure']['incident_p50']} dark={bool(r['exposure'].get('lighting_dark'))} "
                      f"vram={r.get('vram_mib')}" for r in rm["renders"]))


# The measurement script (run inside Blender). Placeholders: __ROOT__ (the repo), __OUT__ (a folder), __SUN__
# (the lamp's W/m²). Every part runs under ``part()``: a failure prints the part's name and its traceback to stdout
# and exits with 1, so the pytest assertion's tail shows the cause.
SUN_DISC_SCRIPT = r'''
import json, math, sys, traceback
sys.path.insert(0, "__ROOT__")
OUT = "__OUT__"
SUN_WM2 = float("__SUN__")


def part(name, fn):
    """Run one part; on an error print the name and the traceback and exit non-zero (the P1 failure after
    'Saved: sky.exr' left no traceback in the captured tail)."""
    try:
        return fn()
    except Exception:
        print("SUN_DISC_PART_FAILED " + name)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)


import bpy
import numpy as np
from mathutils import Vector
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import render as R

data = {"sun_wm2": SUN_WM2}
LIGHTING = {"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 210.0}
d = Vector(L.sun_direction(35.0, 210.0))
state = {}


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_x, scene.render.resolution_y = 96, 54
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = SUN_WM2
    sun.angle = math.radians(0.53)
    sob = bpy.data.objects.new("sun", sun)
    sob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sob)
    sob["wenart_id"] = "sun"
    state["scene"], state["sun"] = scene, sob


def world_production():
    """The round-3 exterior world: the disc for camera rays only (materials.exterior_world_nodes defaults)."""
    scene = state["scene"]
    rec = M.exterior_world_nodes(scene, LIGHTING, sun_disc=True, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                                 sun_wm2=SUN_WM2)
    scene.world = bpy.data.worlds[M.EXTERIOR_WORLD]
    data["record"] = rec
    data["scene_props"] = {k: scene.get(k) for k in R.WORLD_PROPS}
    data["world_nodes"] = sorted(n.bl_idname for n in scene.world.node_tree.nodes)
    data["sun_hidden_by_render"] = R.sun_hidden_for(data["scene_props"], "exterior")


def luminance(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def render_pass(path, names):
    """Render to a multilayer EXR (render.set_output: media_type MULTI_LAYER_IMAGE, the 5.2 way) and read one
    pass back through render.read_exr / find_rgb (the pass names of Blender 5.2.2: 'ViewLayer.Combined.R',
    'ViewLayer.Diffuse Direct.R'; older builds 'DiffDir')."""
    scene = state["scene"]
    R.set_output(scene, "OPEN_EXR_MULTILAYER")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    channels = R.read_exr(path)
    rgb = R.find_rgb(channels, *names)
    if rgb is None:
        raise RuntimeError("no pass %r in %s; channels: %s" % (names, path, sorted(channels)))
    return rgb


def disc_image():
    """1. a camera looking at the sun: the disc against the sky (a SUN lamp is no object the camera sees)."""
    scene = state["scene"]
    cam = bpy.data.cameras.new("c")
    cam.lens = 50.0
    cob = bpy.data.objects.new("c", cam)
    cob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cob)
    scene.camera = cob
    lum = luminance(render_pass(OUT + "/sky.exr", ("Combined",)))
    h, w = lum.shape
    data["disc_centre"] = float(lum[h // 2 - 2: h // 2 + 3, w // 2 - 2: w // 2 + 3].max())
    data["sky_edge"] = float(np.median(lum[:, : w // 4]))
    bpy.data.objects.remove(cob)


def plane():
    """2. a white diffuse plane facing the sun, an orthographic camera on the sun's side, Diffuse Direct on."""
    scene = state["scene"]
    mesh = bpy.data.meshes.new("p")
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [[0, 1, 2, 3]])
    mesh.update()
    pob = bpy.data.objects.new("p", mesh)
    scene.collection.objects.link(pob)
    pob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    mat = bpy.data.materials.new("white")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    cam2 = bpy.data.cameras.new("c2")
    cam2.type = "ORTHO"
    cam2.ortho_scale = 0.5
    cob2 = bpy.data.objects.new("c2", cam2)
    cob2.location = d * 2.0
    cob2.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cob2)
    scene.camera = cob2
    scene.view_layers[0].use_pass_diffuse_direct = True
    state["plane"], state["cam2"] = pob, cob2


def horizontal(on):
    """Round 4: the white plane flat on the ground (normal +Z) with the camera above it, or back facing the sun."""
    pob, cob2 = state["plane"], state["cam2"]
    n = Vector((0.0, 0.0, 1.0)) if on else d
    pob.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    cob2.location = n * 2.0
    cob2.rotation_euler = (-n).to_track_quat("-Z", "Y").to_euler()


def direct(path):
    return float(np.median(luminance(render_pass(path, ("Diffuse Direct", "DiffDir")))))


def measure():
    """3. the direct light on the plane: (a) the production world, lamp hidden (what the shading rays see under the
    camera-ray mix); (b) the P1 world, the disc for every ray, lamp hidden; (c) the sky without a disc; (d) the lamp
    alone under a black world."""
    scene, sob = state["scene"], state["sun"]
    sob.hide_render = True
    data["mix_sky_direct"] = direct(OUT + "/mix.exr")
    M.exterior_world_nodes(scene, LIGHTING, sun_disc=True, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                           sun_wm2=SUN_WM2, disc_camera_only=False)
    scene.world = bpy.data.worlds[M.EXTERIOR_WORLD]
    data["disc_all_direct"] = direct(OUT + "/disc_all.exr")
    M.exterior_world_nodes(scene, LIGHTING, sun_disc=False, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                           sun_wm2=SUN_WM2)
    scene.world = bpy.data.worlds[M.EXTERIOR_WORLD]
    data["dome_direct"] = direct(OUT + "/dome.exr")
    data["dome_record"] = M.exterior_world(LIGHTING, sun_disc=False, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                                           sun_wm2=SUN_WM2)
    horizontal(True)                          # round 4: the sky's diffuse light on the ground
    data["dome_h_direct"] = direct(OUT + "/dome_h.exr")
    horizontal(False)
    black = bpy.data.worlds.new("black")
    black.use_nodes = True
    nodes, links = black.node_tree.nodes, black.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.0
    links.new(bg.outputs["Background"], out.inputs["Surface"])
    scene.world = black
    sob.hide_render = False
    data["lamp_only_direct"] = direct(OUT + "/lamp.exr")
    horizontal(True)                          # round 4: the lamp's direct light on the ground
    data["lamp_h_direct"] = direct(OUT + "/lamp_h.exr")


def save():
    with open(OUT + "/sun_disc.json", "w") as fh:
        json.dump(data, fh, indent=1)
    print("SUN_DISC_DONE")


part("setup", setup)
part("world", world_production)
part("disc image", disc_image)
part("plane", plane)
part("measure", measure)
part("save", save)
'''


def sun_disc_script(root: Path, out: Path, sun_wm2: float = L.SUN_STRENGTH_WM2) -> str:
    """The measurement script with its placeholders filled (pure)."""
    return (SUN_DISC_SCRIPT.replace("__ROOT__", str(root)).replace("__OUT__", str(out))
            .replace("__SUN__", f"{float(sun_wm2):g}"))


def sun_disc_numbers(data: dict) -> dict:
    """The ratios of the measurement (pure): ``disc_ratio`` = the disc's own direct light (the P1 world minus the
    dome) over the lamp's, ``mix_residual`` = what the camera-ray mix still adds over the dome, over the lamp's.
    Round 4: ``world_sun_ratio`` = the sky's own sun at the record's strength and sun_intensity 1 over the lamp
    (``disc_ratio`` / the record's ``sun_intensity``; 1 when the sky is the lamp's pair) and
    ``diffuse_to_direct_h`` = the disc-less sky over the lamp on a horizontal plane (the clear-sky ratio)."""
    lamp = float(data["lamp_only_direct"])
    dome = float(data["dome_direct"])
    out = {"disc_ratio": (float(data["disc_all_direct"]) - dome) / lamp,
           "mix_residual": (float(data["mix_sky_direct"]) - dome) / lamp,
           "dome_ratio": dome / lamp}
    intensity = float((data.get("record") or {}).get("sun_intensity") or 0.0)
    if intensity > 0:
        out["world_sun_ratio"] = out["disc_ratio"] / intensity
    if data.get("lamp_h_direct"):
        out["diffuse_to_direct_h"] = float(data["dome_h_direct"]) / float(data["lamp_h_direct"])
    return out


@needs_blender
def test_exterior_sky_carries_a_visible_sun_disc(tmp_path):
    script = sun_disc_script(ROOT, tmp_path)
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", script],
                          capture_output=True, text=True, timeout=900, cwd=str(ROOT),
                          env=dict(os.environ, WENART_LIGHT_VARIANT=""))
    tail = proc.stdout[-4000:] + proc.stderr[-2000:]
    assert "SUN_DISC_PART_FAILED" not in proc.stdout, tail
    assert proc.returncode == 0 and "SUN_DISC_DONE" in proc.stdout, tail
    data = json.loads((tmp_path / "sun_disc.json").read_text(encoding="utf-8"))
    rec = data["record"]
    # The production world: the disc for camera rays only, the lamp the one direct sun (render.py keeps it shown).
    assert rec["sun_disc"] is True and rec["sun_disc_camera_only"] is True and rec["direct_sun"] == "lamp"
    assert rec["sun_intensity"] == pytest.approx(M.sky_sun_intensity(L.SUN_STRENGTH_WM2, world_strength=rec["strength"]))
    # round 4: the sky is the lamp's pair (strength 1000 / (1000 x 0.1297)), the disc keeps its image brightness
    assert rec["sun_intensity"] == pytest.approx(M.sky_pair_ratios(35.0)[0], abs=1e-4)
    assert rec["strength"] * rec["sun_intensity"] == pytest.approx(L.SUN_STRENGTH_WM2 / 1000.0, abs=1e-5)
    assert data["scene_props"]["wenart_world_exterior_disc_camera_only"] is True
    assert data["sun_hidden_by_render"] is False and not R.sun_hidden_for(data["scene_props"], "exterior")
    assert {"ShaderNodeLightPath", "ShaderNodeMixShader"} <= set(data["world_nodes"])
    assert data["world_nodes"].count("ShaderNodeTexSky") == 2 and data["world_nodes"].count("ShaderNodeBackground") == 2
    # The disc is in the image, far brighter than the sky beside it.
    assert data["disc_centre"] > 20.0 * max(data["sky_edge"], 1e-6), "the sun disc is far brighter than the sky"
    assert data["lamp_only_direct"] > 0 and data["dome_direct"] > 0
    n = sun_disc_numbers(data)
    print(f"SUN_DISC_RATIO disc/lamp = {n['disc_ratio']:.3f} (P1 world disc-all direct {data['disc_all_direct']:.4f}, "
          f"dome {data['dome_direct']:.4f}, lamp-only {data['lamp_only_direct']:.4f}; dome/lamp {n['dome_ratio']:.4f}; "
          f"reference {rec['sun_disc_reference_wm2']} W/m2, sun {data['sun_wm2']} W/m2); camera-ray mix residual "
          f"{n['mix_residual']:.4f} of the lamp")
    # With the camera-ray mix the sky-only direct light is the dome's: the disc adds nothing (noise allowed).
    assert abs(n["mix_residual"]) <= 0.02, f"the camera-ray mix still lets the disc light the scene: {n}"
    # The calibration number: the disc-for-every-ray sky's own direct light against the lamp's.
    assert n["disc_ratio"] > 0, f"the P1 world's disc adds no light over the dome: {n}"
    assert 1.0 / 20.0 <= n["disc_ratio"] <= 20.0, f"the disc's irradiance is off the lamp's by more than 20x: {n}"
    # Round 4 (docs/milestone13.md §14.8): the sky world is the lamp's pair, so its own sun at sun_intensity 1 gives
    # the lamp's irradiance (bpy 5.2.2 CPU: 1.00), and the sky's diffuse light on the ground over the lamp's direct
    # light is the pair's clear-sky ratio (0.166 at 35 degrees; pvlib's Bird / Ineichen-Perez 0.149-0.212).
    print(f"SKY_PAIR world sun / lamp = {n['world_sun_ratio']:.3f}; horizontal diffuse / direct = "
          f"{n['diffuse_to_direct_h']:.4f} (record {data['dome_record']['sky_calibration']['diffuse_to_direct']})")
    assert n["world_sun_ratio"] == pytest.approx(1.0, abs=0.05), n
    want = data["dome_record"]["sky_calibration"]["diffuse_to_direct"]
    assert n["diffuse_to_direct_h"] == pytest.approx(want, rel=0.10), (n, want)
    assert M.CLEAR_SKY_DIFFUSE_RANGE[0] <= n["diffuse_to_direct_h"] <= M.CLEAR_SKY_DIFFUSE_RANGE[1], n


# Round-4 review (16 Oct 2026): SKY_SUN_TABLE was measured with a scratch script at 14 elevations; this script is the
# same method in the repo, so the rows away from the 35-degree pair of the sun-disc test are re-measured on the pod.
# Placeholders: __ROOT__, __OUT__, __ELEVATIONS__ (comma separated degrees). Per elevation, a white Lambert plane and
# its Diffuse Direct pass (the median pixel): (a) the SKY_PAIR_REFERENCE_WM2 lamp alone under a black world on the
# plane facing the sun; (b) the production sky (exterior_world_nodes, one sky for every ray) at Background Strength 1
# and sun_intensity 1 with and without the disc on the same plane; (c) the sky without the disc on a horizontal
# plane. sun_ratio = (disc - dome) / lamp, dome_ratio = horizontal dome / lamp (the table's definitions).
SKY_TABLE_SCRIPT = r'''
import json, math, sys, traceback
sys.path.insert(0, "__ROOT__")
OUT = "__OUT__"
ELEVATIONS = [float(e) for e in "__ELEVATIONS__".split(",")]


def part(name, fn):
    try:
        return fn()
    except Exception:
        print("SKY_TABLE_PART_FAILED " + name)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)


import bpy
import numpy as np
from mathutils import Vector
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import render as R

AZ = 210.0
state, rows = {}, []


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_x, scene.render.resolution_y = 12, 12
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.view_layers[0].use_pass_diffuse_direct = True
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = M.SKY_PAIR_REFERENCE_WM2
    sun.angle = math.radians(0.53)
    sob = bpy.data.objects.new("sun", sun)
    scene.collection.objects.link(sob)
    mesh = bpy.data.meshes.new("p")
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [[0, 1, 2, 3]])
    mesh.update()
    pob = bpy.data.objects.new("p", mesh)
    scene.collection.objects.link(pob)
    mat = bpy.data.materials.new("white")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    cam = bpy.data.cameras.new("c")
    cam.type = "ORTHO"
    cam.ortho_scale = 0.5
    cob = bpy.data.objects.new("c", cam)
    scene.collection.objects.link(cob)
    scene.camera = cob
    black = bpy.data.worlds.new("black")
    black.use_nodes = True
    nodes = black.node_tree.nodes
    for n in list(nodes):
        nodes.remove(n)
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.0
    black.node_tree.links.new(bg.outputs["Background"], nodes.new("ShaderNodeOutputWorld").inputs["Surface"])
    state.update(scene=scene, sun=sob, plane=pob, cam=cob, black=black)


def face(normal):
    n = Vector(normal).normalized()
    state["plane"].rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    state["cam"].location = n * 2.0
    state["cam"].rotation_euler = (-n).to_track_quat("-Z", "Y").to_euler()


def direct(tag):
    scene = state["scene"]
    path = OUT + "/" + tag + ".exr"
    R.set_output(scene, "OPEN_EXR_MULTILAYER")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    rgb = R.find_rgb(R.read_exr(path), "Diffuse Direct", "DiffDir")
    if rgb is None:
        raise RuntimeError("no Diffuse Direct pass in " + path)
    return float(np.median(0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]))


def sky(el, disc):
    """The production sky at the table's unit: Background Strength 1, sun_intensity 1, one sky for every ray."""
    scene = state["scene"]
    M.exterior_world_nodes(scene, {"mood": "warm daylight"}, sun_disc=disc, sun_elevation_deg=el,
                           sun_azimuth_deg=AZ, sun_wm2=M.SKY_PAIR_REFERENCE_WM2, disc_camera_only=False)
    world = bpy.data.worlds[M.EXTERIOR_WORLD]
    for n in world.node_tree.nodes:
        if n.bl_idname == "ShaderNodeBackground":
            n.inputs["Strength"].default_value = 1.0
        if n.bl_idname == "ShaderNodeTexSky" and n.sun_disc:
            n.sun_intensity = 1.0
    scene.world = world


def measure():
    scene, sob = state["scene"], state["sun"]
    for el in ELEVATIONS:
        d = Vector(L.sun_direction(el, AZ))
        sob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        scene.world = state["black"]
        sob.hide_render = False
        face(d)
        lamp = direct("lamp_%g" % el)
        sob.hide_render = True
        sky(el, False)
        dome_n = direct("dome_n_%g" % el)
        face((0.0, 0.0, 1.0))
        dome_h = direct("dome_h_%g" % el)
        sky(el, True)
        face(d)
        disc_n = direct("disc_n_%g" % el)
        rows.append({"elevation_deg": el, "lamp_n": lamp, "dome_n": dome_n, "dome_h": dome_h, "disc_n": disc_n,
                     "sun_ratio": (disc_n - dome_n) / lamp, "dome_ratio": dome_h / lamp})


def save():
    with open(OUT + "/sky_table.json", "w") as fh:
        json.dump({"blender": bpy.app.version_string, "rows": rows}, fh, indent=1)
    print("SKY_TABLE_DONE")


part("setup", setup)
part("measure", measure)
part("save", save)
'''
SKY_TABLE_CHECK_ELEVATIONS = (12.0, 45.0, 65.0)       # golden evening, overcast, bright noon (wenart/style/finishes.py)


@needs_blender
def test_sky_sun_table_rows_reproduce(tmp_path):
    """Round-4 review: ``materials.SKY_SUN_TABLE`` rows away from 35 degrees, re-measured with the table's method:
    the sky's own sun within 3 % and its horizontal dome within 5 % of the table (128 samples here; the table: 256)."""
    els = ",".join(f"{e:g}" for e in SKY_TABLE_CHECK_ELEVATIONS)
    script = (SKY_TABLE_SCRIPT.replace("__ROOT__", str(ROOT)).replace("__OUT__", str(tmp_path))
              .replace("__ELEVATIONS__", els))
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", script],
                          capture_output=True, text=True, timeout=900, cwd=str(ROOT),
                          env=dict(os.environ, WENART_LIGHT_VARIANT=""))
    tail = proc.stdout[-4000:] + proc.stderr[-2000:]
    assert "SKY_TABLE_PART_FAILED" not in proc.stdout, tail
    assert proc.returncode == 0 and "SKY_TABLE_DONE" in proc.stdout, tail
    rows = json.loads((tmp_path / "sky_table.json").read_text(encoding="utf-8"))["rows"]
    assert [r["elevation_deg"] for r in rows] == list(SKY_TABLE_CHECK_ELEVATIONS)
    for r in rows:
        sun_ratio, dome_ratio = M.sky_pair_ratios(r["elevation_deg"])
        print(f"SKY_TABLE {r['elevation_deg']:g} deg: sun_ratio {r['sun_ratio']:.4f} (table {sun_ratio:.4f}), "
              f"dome_ratio {r['dome_ratio']:.5f} (table {dome_ratio:.5f})")
        assert r["sun_ratio"] == pytest.approx(sun_ratio, rel=0.03), r
        assert r["dome_ratio"] == pytest.approx(dome_ratio, rel=0.05), r
