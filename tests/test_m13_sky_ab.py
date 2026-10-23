"""Pod P6a (22 Oct 2026, the user's OK; docs/milestone13.md §14.13 decision 4): the interior sky A/B, CPU only.

- the sky light variants (``lighting.SKY_VARIANTS``: ``sky2``, ``sky35``, ``sky52``) raise the interior world's
  Background Strength by 2^stops (``interior_sky_gain`` -> ``materials.world_nodes(..., strength_gain=)``, checked on a
  fake bpy), start from production, keep every other lever, enter the build fingerprint and the manifest's lighting
  block; the default (no variant) and every lever variant build the world exactly as before (Milestone 13 final pass,
  23 Oct 2026: the default is the windows-only sky, ``sky0`` the old world; the lever variants keep it);
- the fixed real04 views (``ab.M13_SKY_AB_VIEWS``), their resolution against the scene manifest the A/B replays
  (``resolve_views``) and ``prepare_m13(..., run_dir=)`` from a pod's own run output;
- the summary and sheets of the sky set; ``levers_ab.sh`` run end to end with fake Blender and assets in its new
  run mode (AB_SOURCE=run, AB_VIEW_SET=sky, AB_NAME), its P1 defaults unchanged;
- ``scripts/jobs/m13_p6.sh``: ``bash -n``, its defaults, and runs with a fake full.sh / levers_ab.sh (the A/B only for
  real04, only with time left before the deadline minus the reserve, one GPU test run).
Each test fails on 0f40067 (no sky variants, no sky views, no run mode, no m13_p6.sh).
"""
from __future__ import annotations

import inspect
import json
import math
import os
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

from wenart.blender import build as B
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import render as R
from wenart.run import ab as AB

ROOT = Path(__file__).resolve().parents[1]
LEVERS_AB = ROOT / "scripts" / "jobs" / "levers_ab.sh"
P6_JOB = ROOT / "scripts" / "jobs" / "m13_p6.sh"
P5_SCENE = ROOT / "runs" / "20261017-224848-full" / "results" / "renders" / "real04" / "scene_manifest.json"
SKY_VIEWS = [v["camera"] for v in AB.M13_SKY_AB_VIEWS["real04"]]


# --------------------------------------------------------------------------
# The variants and the gain
# --------------------------------------------------------------------------

def test_sky_variants_raise_only_the_interior_world_from_production():
    assert L.SKY_VARIANT_STOPS == {"sky2": 2.0, "sky35": 3.5, "sky52": 5.2}
    assert L.SKY_VARIANTS == ("sky2", "sky35", "sky52")
    # the lever A/B's names stay P1's (its sheets and defaults pin them); the sky names come on top
    assert L.LIGHT_VARIANTS == ("m11", "base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
    # fix round after P6a (pin changed on purpose): the windows-only level skywin35 comes after the sky levels;
    # Milestone 13 final pass (23 Oct 2026; pin changed on purpose): the old world sky0 comes last
    assert L.KNOWN_LIGHT_VARIANTS == L.LIGHT_VARIANTS + L.SKY_VARIANTS + L.SKY_WINDOW_VARIANTS + ("sky0",)
    prod = L.light_levers(env={})
    for name, stops in L.SKY_VARIANT_STOPS.items():
        lv = L.light_levers(env={L.LIGHT_VARIANT_ENV: name})
        # production: the 1000 W/m² sun, the EV cap, the rig and the shell, only the interior sky raised
        assert {k: lv[k] for k in ("sun_wm2", "ev_cap", "rig", "shell")} == \
            {k: prod[k] for k in ("sun_wm2", "ev_cap", "rig", "shell")}, name
        assert lv["sky_stops"] == stops and lv["variant"] == name and lv["source"] == "env"
        assert L.interior_sky_gain(lv) == pytest.approx(2.0 ** stops, rel=1e-12)
        assert R.exposure_limits_for(lv) == tuple(R.EXPOSURE_LIMITS)            # the production EV cap
    assert L.interior_sky_gain(L.light_levers("sky2")) == 4.0
    assert L.interior_sky_gain(L.light_levers("sky35")) == pytest.approx(11.3137085, abs=1e-6)
    assert L.interior_sky_gain(L.light_levers("sky52")) == pytest.approx(36.7583, abs=1e-3)   # the 38x of the docstring
    both = L.light_levers("base,sky35")
    assert both["sky_stops"] == 3.5 and both["rig"] and both["shell"] and both["sun_wm2"] == 1000.0
    # with the Milestone 11 look or a single lever the sky level starts from that look, as the other levers do
    old = L.light_levers("m11+sky52")
    assert (old["sun_wm2"], old["ev_cap"], old["rig"], old["shell"], old["sky_stops"]) == (3.0, False, False, False, 5.2)
    sun = L.light_levers("sun300,sky2")
    assert (sun["sun_wm2"], sun["rig"], sun["sky_stops"]) == (300.0, False, 2.0)
    with pytest.raises(ValueError, match="more than one interior sky level"):
        L.parse_light_variant("sky2,sky35")
    with pytest.raises(ValueError, match="unknown variant"):
        L.parse_light_variant("sky4")


def test_the_default_is_the_windows_only_sky_and_every_lever_variant_keeps_the_world_as_built():
    """Milestone 13 final pass (23 Oct 2026; pin changed on purpose: the user's decision after pod P6c; this was
    ``test_the_default_and_every_lever_variant_keep_the_world_as_built``): production (no variant, ``base`` and a list
    that starts from production) builds the windows-only sky, 3.5 stops on the camera's paths (``skywin35``'s level,
    an alias); the Milestone 11 look and every single P1 lever keep the old world, and ``sky0`` names the old world
    under production's levers. Fails on 81d5cad (production at 0 stops on all rays, no ``sky0``)."""
    prod = L.light_levers(env={})
    assert (L.PRODUCTION_SKY_STOPS, L.PRODUCTION_SKY_RAYS) == (3.5, "camera_paths")
    assert prod["variant"] is None and (prod["sky_stops"], prod["sky_rays"]) == (3.5, "camera_paths")
    assert L.interior_sky_gain(prod) == pytest.approx(2.0 ** 3.5, rel=1e-12)
    assert L.interior_sky_rays(prod) == "camera_paths"
    keys = ("sun_wm2", "ev_cap", "rig", "shell", "sky_stops", "sky_rays")
    for name in ("base", "skywin35", "base,skywin35", "base+sun300", "base,rig"):
        lv = L.light_levers(name)
        assert (lv["sky_stops"], lv["sky_rays"]) == (3.5, "camera_paths"), name
    # skywin35 is an alias of production: the same levers, only the variant's name differs
    assert {k: L.light_levers("skywin35")[k] for k in keys} == {k: prod[k] for k in keys} == \
        {k: L.light_levers("base")[k] for k in keys}
    # the old world: the Milestone 11 look and every single lever (their P1 meaning), and sky0
    for name in [n for n in L.LIGHT_VARIANTS if n != "base"] + ["sky0", "base,sky0", "m11,sky0", "sun1000+rig"]:
        lv = L.light_levers(name)
        assert (lv["sky_stops"], lv["sky_rays"]) == (0.0, "all") and L.interior_sky_gain(lv) == 1.0, name
    old = L.light_levers("sky0")
    assert L.SKY_OLD_WORLD_VARIANT == "sky0" and old["variant"] == "sky0"
    assert {k: old[k] for k in keys[:4]} == {k: prod[k] for k in keys[:4]}      # production's sun, cap, rig, shell
    for both in ("sky0,skywin35", "sky0+sky35"):
        with pytest.raises(ValueError, match="more than one interior sky level"):
            L.parse_light_variant(both)
    assert L.interior_sky_gain(None) == 1.0 and L.interior_sky_gain({"sun_wm2": 1000.0}) == 1.0  # an older levers dict
    # the manifest's levers block records the sky always (a block without it was built before the final pass)
    assert L.lever_record(prod) == {"sun_wm2": 1000.0, "ev_cap": True, "rig": True, "shell": True, "source": "default",
                                    "sky_stops": 3.5, "sky_rays": "camera_paths"}
    assert L.lever_record(old) == {"sun_wm2": 1000.0, "ev_cap": True, "rig": True, "shell": True, "source": "arg",
                                   "sky_stops": 0.0, "sky_rays": "all"}
    assert L.lever_record(L.light_levers("sky35")) == {"sun_wm2": 1000.0, "ev_cap": True, "rig": True, "shell": True,
                                                       "source": "arg", "sky_stops": 3.5, "sky_rays": "all"}
    assert L.lever_record(L.light_levers("m11")) == {"sun_wm2": 3.0, "ev_cap": False, "rig": False, "shell": False,
                                                     "source": "arg", "sky_stops": 0.0, "sky_rays": "all"}
    before = {"sun_wm2": 1000.0, "ev_cap": True, "rig": True, "shell": True, "source": "default"}  # P5's levers dict
    assert L.lever_record(before) == dict(before, sky_stops=0.0, sky_rays="all")
    # the world record of production: the room's strength, the camera's at 2^3.5
    strength, extra = M.world_strength_record(1.0, L.interior_sky_gain(prod), L.interior_sky_rays(prod))
    assert strength == 1.0 and (extra["sky_stops"], extra["sky_rays"]) == (3.5, "camera_paths")
    assert extra["strength_camera"] == pytest.approx(11.313708, abs=1e-6)
    # the world record: gain 1.0 (sky0) returns the strength untouched and no extra key
    assert M.world_strength_record(1.0, L.interior_sky_gain(old), L.interior_sky_rays(old)) == (1.0, {})
    assert M.world_strength_record(1.0) == (1.0, {}) and M.world_strength_record(0.8, 1.0) == (0.8, {})
    strength, extra = M.world_strength_record(1.0, 2.0 ** 3.5)
    assert strength == pytest.approx(11.313708, abs=1e-6)
    assert extra == {"strength_base": 1.0, "strength_gain": 11.313708, "sky_stops": 3.5}
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="positive number"):
            M.world_strength_record(1.0, bad)


def test_build_lighting_passes_the_gain_to_the_interior_world_only():
    """The wiring: the interior world gets the gain, the exterior world and the sun lamp do not (the sun's strength
    and the exterior sky come from ``sun_strength_wm2``, which never reads ``sky_stops``)."""
    src = inspect.getsource(L.build_lighting)
    assert "world_nodes(scene, world_lighting(lighting, in_building), hdri_path,\n" in src
    # fix round after P6a (pin changed on purpose): the rays that see the gain go along (all for a sky level)
    assert "strength_gain=interior_sky_gain(levers), gain_rays=interior_sky_rays(levers))" in src
    assert src.count("strength_gain") == 1 and "exterior_world_nodes(scene, world_lighting(lighting, in_building), " \
        "sun_disc=True,\n" in src and '"levers": lever_record(levers)' in src
    for name in L.SKY_VARIANTS:
        assert L.sun_strength_wm2({}, L.light_levers(name)) == L.sun_strength_wm2({}, L.light_levers(env={}))
    assert "strength_gain" not in inspect.signature(M.exterior_world_nodes).parameters


class _Socket:
    def __init__(self):
        self.default_value = None


class _Sockets(dict):
    def __missing__(self, key):
        self[key] = _Socket()
        return self[key]


class _Node:
    def __init__(self, kind):
        self.bl_idname = kind
        self.inputs, self.outputs = _Sockets(), _Sockets()


class _Nodes(list):
    def new(self, kind):
        self.append(_Node(kind))
        return self[-1]

    def remove(self, node):
        list.remove(self, node)


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


def _background_strength(scene) -> float:
    return next(n for n in scene.world.node_tree.nodes if n.bl_idname == "ShaderNodeBackground") \
        .inputs["Strength"].default_value


def test_world_nodes_raises_the_background_by_the_gain(fake_bpy, tmp_path):
    hdri = tmp_path / "kloppenheim_06_2k.hdr"
    hdri.write_bytes(b"hdr")
    lighting = {"mood": "warm daylight", "sun_azimuth_deg": 210.0, "sun_elevation_deg": 35.0}
    # production (and the default argument): the record P5's manifest holds, byte for byte
    scene = types.SimpleNamespace(world=None)
    rec = M.world_nodes(scene, lighting, str(hdri))
    assert json.dumps(rec) == json.dumps({"kind": "hdri", "file": str(hdri), "strength": 1.0})
    assert _background_strength(scene) == 1.0
    scene = types.SimpleNamespace(world=None)
    assert M.world_nodes(scene, lighting, str(hdri), strength_gain=1.0) == rec and _background_strength(scene) == 1.0
    # sky35: the HDRI's Background at 2^3.5, recorded with the base strength, the gain and the stops
    scene = types.SimpleNamespace(world=None)
    gain = L.interior_sky_gain(L.light_levers("sky35"))
    rec = M.world_nodes(scene, lighting, str(hdri), strength_gain=gain)
    assert _background_strength(scene) == pytest.approx(11.313708, abs=1e-6)
    assert rec["strength"] == pytest.approx(11.313708, abs=1e-6) and rec["strength_base"] == 1.0
    assert rec["sky_stops"] == 3.5 and rec["kind"] == "hdri"
    # the physical sky fallback (no HDRI file): half the mood strength, times the gain
    scene = types.SimpleNamespace(world=None)
    assert M.world_nodes(scene, lighting, None) == {"kind": "sky", "file": None, "strength": 0.5}
    scene = types.SimpleNamespace(world=None)
    rec = M.world_nodes(scene, lighting, None, strength_gain=4.0)
    assert _background_strength(scene) == 2.0 and rec["strength"] == 2.0 and rec["strength_base"] == 0.5
    assert rec["sky_stops"] == 2.0


def test_the_sky_variant_enters_the_build_fingerprint(tmp_path, monkeypatch):
    building = tmp_path / "building_final.json"
    building.write_text(json.dumps({"project": {"id": "real04"}}), encoding="utf-8")
    for var in ("WENART_CAMERAS_FROM", "WENART_CAMERAS_EXTRA", L.LIGHT_VARIANT_ENV):
        monkeypatch.delenv(var, raising=False)
    base = B.fingerprint_args(str(building))
    monkeypatch.setenv(L.LIGHT_VARIANT_ENV, "base")
    named_base = B.fingerprint_args(str(building))
    monkeypatch.setenv(L.LIGHT_VARIANT_ENV, "sky35")
    sky = B.fingerprint_args(str(building))
    # Milestone 13 final pass (23 Oct 2026): the old world is a named variant, so a sky0 build never reuses a
    # production build (the windows-only sky) and the reverse
    monkeypatch.setenv(L.LIGHT_VARIANT_ENV, "sky0")
    old = B.fingerprint_args(str(building))
    assert base["light_variant"] is None and named_base["light_variant"] == "base" and sky["light_variant"] == "sky35"
    assert old["light_variant"] == "sky0"
    assert {k: v for k, v in sky.items() if k != "light_variant"} == {k: v for k, v in base.items()
                                                                     if k != "light_variant"}
    assert len({B.build_fingerprint(base), B.build_fingerprint(named_base), B.build_fingerprint(sky),
                B.build_fingerprint(old)}) == 4


# --------------------------------------------------------------------------
# The views, their resolution and the prepare from a run
# --------------------------------------------------------------------------

def _cam(name, room, kind="interior"):
    return {"name": name, "position": [1.0, 1.0, 1.25], "target": [2.0, 1.0, 1.25], "lens_mm": 18.0,
            "room_id": room, "level_id": "L0", "kind": kind}


def test_the_sky_views_and_their_resolution():
    views = AB.M13_SKY_AB_VIEWS["real04"]
    assert 4 <= len(views) <= 6 and len(set(SKY_VIEWS)) == len(SKY_VIEWS)
    for v in views:
        assert v["camera"].startswith(f"cam_{v['room_id']}_") and v["camera"][len(v["room_id"]) + 5:].isdigit(), v
    assert {"bedroom", "living"} <= {v["room_type"] for v in views}
    assert {"cam_r_L0_yatak_odasi_1", "cam_r_L-1_salon_1", "cam_r_L0_e_yatak_odasi_1",
            "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1"} <= set(SKY_VIEWS)
    # Milestone 13 final pass (23 Oct 2026; pin changed on purpose): the old world is sky0, base is production now
    assert AB.M13_SKY_AB_VARIANTS == (L.SKY_OLD_WORLD_VARIANT,) + L.SKY_VARIANTS == ("sky0", "sky2", "sky35", "sky52")
    # fix round after P6a (pin changed on purpose): the windows-only A/B's set
    assert AB.AB_VIEW_SETS == {"levers": AB.M13_AB_VIEWS, "sky": AB.M13_SKY_AB_VIEWS,
                               "skywin": AB.M13_SKYWIN_AB_VIEWS}
    # the lever A/B is unchanged: no scene, the configured names
    assert AB.ab_views("real02") == AB.m13_views("real02") and AB.ab_views("real04") == []
    assert AB.ab_views("real04", "sky") == SKY_VIEWS and AB.ab_views("real02", "sky") == []
    with pytest.raises(ValueError, match="unknown view set"):
        AB.view_set_of("skies")
    # a scene without cam_r_L0_yatak_odasi_3 but with _2 (same room): replaced; without the play room: dropped
    cams = [_cam(n, v["room_id"]) for n, v in zip(SKY_VIEWS, views)
            if n not in ("cam_r_L0_yatak_odasi_3", "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1")]
    cams.append(_cam("cam_r_L0_yatak_odasi_2", "r_L0_yatak_odasi"))
    cams.append(_cam("ext_1", None, "exterior"))
    res = AB.resolve_views("real04", "sky", {"cameras": cams})
    assert res["views"] == ["cam_r_L0_yatak_odasi_1", "cam_r_L0_yatak_odasi_2", "cam_r_L0_e_yatak_odasi_1",
                            "cam_r_L-1_salon_1", "cam_r_L-1_salon_2"]
    assert res["replaced"] == [{"wanted": "cam_r_L0_yatak_odasi_3", "used": "cam_r_L0_yatak_odasi_2",
                                "reason": "no camera cam_r_L0_yatak_odasi_3 in the scene manifest: the first other "
                                          "camera of r_L0_yatak_odasi"}]
    assert [d["wanted"] for d in res["dropped"]] == ["cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1"]
    # a replacement never takes a camera that is itself one of the wanted views
    only = AB.resolve_views("real04", "sky", {"cameras": [_cam("cam_r_L0_yatak_odasi_3", "r_L0_yatak_odasi")]})
    assert only["views"] == ["cam_r_L0_yatak_odasi_3"] and len(only["dropped"]) == 5


@pytest.mark.skipif(not P5_SCENE.is_file(), reason="needs runs/20261017-224848-full (pod P5's results)")
def test_the_sky_views_are_p5_cameras_that_see_a_window_or_a_glazed_door():
    scene = json.loads(P5_SCENE.read_text(encoding="utf-8"))
    by_name = {c["name"]: c for c in scene["cameras"]}
    res = AB.resolve_views("real04", "sky", scene)
    assert res["views"] == SKY_VIEWS and not res["replaced"] and not res["dropped"]
    for v in AB.M13_SKY_AB_VIEWS["real04"]:
        rec = by_name[v["camera"]]
        assert rec["room_id"] == v["room_id"] and rec["kind"] == "interior"
        assert any(o.startswith(("win_", "d_")) for o in rec.get("visible_openings") or []), v["camera"]


def _run_output(root: Path, cameras: list) -> Path:
    from PIL import Image

    run = root / "outputs" / "real04"
    (run / "scene").mkdir(parents=True)
    (run / "renders").mkdir()
    (run / "building_final.json").write_text(json.dumps({"project": {"id": "real04"}, "run": "p6"}), encoding="utf-8")
    (run / "style.json").write_text(json.dumps({"name": "p6 style", "lighting": {"mood": "warm daylight"}}),
                                    encoding="utf-8")
    (run / "scene" / "scene_manifest.json").write_text(json.dumps(
        {"cameras": cameras, "style_profile": {"name": "profile"}, "build_fingerprint": "f" * 64,
         "camera_policy": "search"}), encoding="utf-8")
    (run / "renders" / "render_manifest.json").write_text(json.dumps({"renders": []}), encoding="utf-8")
    for c in cameras:
        Image.new("RGB", (64, 36), (120, 110, 100)).save(run / "renders" / f"{c['name']}_preview.jpg")
    return run


def _p6_cameras() -> list:
    rooms = {v["camera"]: v["room_id"] for v in AB.M13_SKY_AB_VIEWS["real04"]}
    cams = [_cam(n, rooms[n]) for n in SKY_VIEWS if n != "cam_r_L0_yatak_odasi_3"]
    return cams + [_cam("cam_r_L0_yatak_odasi_2", "r_L0_yatak_odasi"), _cam("ext_1", None, "exterior")]


def test_prepare_m13_from_a_run_output(tmp_path):
    run = _run_output(tmp_path / "pod", _p6_cameras())
    decoy = tmp_path / "repo"           # a committed building must never stand in for the run's
    (decoy / "results" / "furniture" / "real04").mkdir(parents=True)
    (decoy / "results" / "furniture" / "real04" / "building_final.json").write_text('{"run": "committed"}')
    out = tmp_path / "pod" / "outputs" / "real04"
    info = AB.prepare_m13("real04", out, repo_root=decoy, run_dir=run, view_set="sky")
    m13 = out / "ab" / "m13"
    assert info["source"] == f"run {run}" and info["commit"] is None and info["view_set"] == "sky"
    assert json.loads((m13 / "building_final.json").read_text())["run"] == "p6"
    assert (m13 / "style.json").read_bytes() == (run / "style.json").read_bytes()    # the run's file, not the profile
    assert json.loads((m13 / "scene_manifest.json").read_text())["camera_policy"] == "search"
    assert info["cameras"] == 7 and info["previews"] == 7 and info["missing"] == []
    assert info["views"][1] == "cam_r_L0_yatak_odasi_2" and len(info["views"]) == 6
    assert info["views_replaced"][0]["wanted"] == "cam_r_L0_yatak_odasi_3" and info["views_missing"] == []
    assert sorted(info["files"]) == ["building_final.json", "render_manifest.json", "scene_manifest.json",
                                     "style.json"]
    # without its own building the run gives none (the committed one is never taken)
    (run / "building_final.json").unlink()
    info = AB.prepare_m13("real04", tmp_path / "other", repo_root=decoy, run_dir=run, view_set="sky")
    assert "building_final.json" not in info["files"]
    with pytest.raises(ValueError, match="no directory"):
        AB.prepare_m13("real04", tmp_path / "x", run_dir=tmp_path / "missing")
    assert not (tmp_path / "x").exists()                         # nothing written for a bad run output
    with pytest.raises(ValueError, match="unknown view set"):
        AB.prepare_m13("real04", tmp_path / "y", run_dir=run, view_set="nope")
    # the lever A/B's directory prepare keeps its keys (no view_set, no views_replaced)
    info = AB.prepare_m13("real02", tmp_path / "real02", str(ROOT / "results" / "renders" / "real02"))
    assert "view_set" not in info and "views_replaced" not in info and info["views"] == AB.m13_views("real02")


def test_the_cli_resolves_and_rejects_view_sets(tmp_path, capsys):
    scene = tmp_path / "scene_manifest.json"
    scene.write_text(json.dumps({"cameras": _p6_cameras()}), encoding="utf-8")
    assert AB.main(["m13-views", "--project", "real04", "--view-set", "sky", "--scene", str(scene)]) == 0
    out = capsys.readouterr()
    assert out.out.strip().split(",")[:2] == ["cam_r_L0_yatak_odasi_1", "cam_r_L0_yatak_odasi_2"]
    assert "cam_r_L0_yatak_odasi_3 -> cam_r_L0_yatak_odasi_2" in out.err
    assert AB.main(["m13-views", "--project", "real02"]) == 0
    assert capsys.readouterr().out.strip() == ",".join(AB.m13_views("real02"))
    assert AB.main(["m13-views", "--project", "real04", "--view-set", "nope"]) == 2
    run = _run_output(tmp_path / "pod", _p6_cameras())
    assert AB.main(["m13-prepare", "--project", "real04", "--project-out", str(tmp_path / "o"), "--from-run", str(run),
                    "--commit", "abc"]) == 1


# --------------------------------------------------------------------------
# Summary and sheets of the sky set
# --------------------------------------------------------------------------

def _variant_results(res: Path, views: list, variants=AB.M13_SKY_AB_VARIANTS) -> None:
    from PIL import Image

    for v in variants:
        d = res / v / "real04"
        d.mkdir(parents=True)
        stops = L.light_levers(v)["sky_stops"]
        strength, extra = M.world_strength_record(1.0, L.interior_sky_gain(L.light_levers(v)))
        (d / "lighting.json").write_text(json.dumps({"lighting": {"world": {"kind": "hdri", "strength": strength,
                                                                              **extra}}}))
        renders = []
        for cam in views:
            renders.append({"camera": cam, "seconds": 6.1, "samples": 128, "preview": f"{cam}_preview.jpg",
                            "window_pull": {"k": max(0, 3 - int(stops)), "pane_median_after": 0.6,
                                            "pane_p90_after": 0.82},
                            "exposure": {"ev": 1.5 - stops, "ev_raw": 1.5 - stops, "wb_temperature": 5600.0,
                                         "wb_day_green": 1.4 - 0.05 * stops, "wb_view_tint_gain": 1.2}})
            Image.new("RGB", (64, 36), (90, 100, 110)).save(d / f"{cam}_preview.jpg")
        (d / "render_manifest.json").write_text(json.dumps({"renders": renders, "light_variant": {"build": v},
                                                            "white_balance_project": {"kelvin": 5635.0}}))


def test_sky_summary_and_sheets(tmp_path):
    from PIL import Image

    res = tmp_path / "ab_m13" / "sky"
    views = ["cam_r_L0_yatak_odasi_1", "cam_r_L0_yatak_odasi_2"]
    _variant_results(res, views, AB.M13_SKY_AB_VARIANTS[:3])          # sky52 not rendered (cut by the deadline)
    summary = AB.lever_summary(res, ("real04",), AB.M13_SKY_AB_VARIANTS, views={"real04": views}, view_set="sky")
    assert summary["view_set"] == "sky" and summary["views"] == {"real04": views}
    rows = {(r["variant"], r["camera"]): r for r in summary["rows"]}
    assert rows[("sky35", "cam_r_L0_yatak_odasi_1")]["world_strength"] == pytest.approx(11.313708, abs=1e-6)
    assert rows[("sky35", "cam_r_L0_yatak_odasi_1")]["sky_stops"] == 3.5
    # Milestone 13 final pass (23 Oct 2026; pin changed on purpose): the old world's row is sky0
    assert rows[("sky0", "cam_r_L0_yatak_odasi_1")]["sky_stops"] == 0.0
    assert rows[("sky0", "cam_r_L0_yatak_odasi_1")]["pull_k"] == 3 and rows[("sky2", views[1])]["pull_k"] == 1
    assert rows[("sky0", views[0])]["wb_project_k"] == 5635.0 and rows[("sky0", views[0])]["wb_day_green"] == 1.4
    assert rows[("sky52", None)]["status"] == "not rendered"
    md = (res / "summary.md").read_text()
    assert md.startswith("# Milestone 13 interior sky A/B, view set 'sky'")
    assert "| real04 | sky35 | cam_r_L0_yatak_odasi_1 | 11.313708" in md and "| real04 | sky52 | - | not rendered |" in md
    base = tmp_path / "run_final" / "real04"
    base.mkdir(parents=True)
    Image.new("RGB", (64, 36), (10, 10, 10)).save(base / f"{views[0]}_preview.jpg")
    sheets = AB.lever_sheets(res, "real04", AB.M13_SKY_AB_VARIANTS, views=views, baseline_dir=base,
                             baseline_label="run final")
    assert [s.name for s in sheets] == [f"real04_{v}.jpg" for v in views] and all(s.is_file() for s in sheets)
    # the lever A/B's summary keeps its title and table (the P1 / round-3 sheets compare)
    lev = AB.lever_summary(tmp_path / "lev", ("real02",), ("base",))
    assert "view_set" not in lev and (tmp_path / "lev" / "summary.md").read_text().startswith(
        "# Milestone 13 lever A/B (scripts/jobs/levers_ab.sh)\n\n| Project | Variant | View | Seconds | EV used |")


# --------------------------------------------------------------------------
# levers_ab.sh: the P1 defaults and the run mode end to end with fakes
# --------------------------------------------------------------------------

def test_levers_ab_keeps_its_p1_defaults_and_takes_the_sky_options():
    subprocess.run(["bash", "-n", str(LEVERS_AB)], check=True)
    text = LEVERS_AB.read_text(encoding="utf-8")
    for default in ('AB_PROJECTS:-real02 real03', 'AB_VARIANTS:-m11 base sun100 sun300 sun1000 evcap rig shell all',
                    'AB_SAMPLES:-128', 'AB_VIEW_SET:-levers', 'AB_SOURCE:-baseline', 'AB_NAME:-ab_m13',
                    'AB_BASELINE_LABEL:-M11 baseline', 'AB_BASELINE_DIR:-$REPO/results/renders/{name}',
                    'AB_RUN_DIR:-$REPO/outputs/{name}', 'BASE_COL=baseline_m11', 'AB_GPU_TESTS:-1'):
        assert default in text, default
    assert "m13-views" in text and "--from-run" in text and "--baseline-label" in text
    assert 'out=outputs/$p/$NAME/$v' in text and 'AB_OUT=$RESULTS/$NAME' in text


FAKE_BLENDER = r'''
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
cmd = args[0]
def opt(name):
    return args[args.index(name) + 1] if name in args else None
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"cmd": cmd, "args": args, "variant": os.environ.get("WENART_LIGHT_VARIANT"),
                        "cameras_from": os.environ.get("WENART_CAMERAS_FROM")}) + "\n")
out = Path(opt("--out"))
out.mkdir(parents=True, exist_ok=True)
if cmd == "build":
    from wenart.blender import lighting as L
    from wenart.blender import materials as M
    levers = L.light_levers()
    strength, extra = M.world_strength_record(1.0, L.interior_sky_gain(levers))
    (out / "scene.blend").write_bytes(b"blend")
    (out / "build.log").write_text("build\n")
    (out / "scene_manifest.json").write_text(json.dumps({"light_variant": levers["variant"], "lighting": {
        "world": {"kind": "hdri", "strength": strength, **extra}, "levers": L.lever_record(levers)}}))
elif cmd == "render":
    from PIL import Image
    v = os.environ.get("WENART_LIGHT_VARIANT")
    renders = []
    for cam in [c for c in opt("--cameras").split(",") if c]:
        Image.new("RGB", (64, 36), (100, 90, 80)).save(out / f"{cam}_preview.jpg")
        renders.append({"camera": cam, "seconds": 5.0, "samples": int(opt("--samples")), "preview": f"{cam}_preview.jpg",
                        "window_pull": {"k": 1}, "exposure": {"ev": 1.0, "ev_raw": 1.0, "wb_temperature": 5600.0}})
    (out / "render_manifest.json").write_text(json.dumps({"renders": renders, "light_variant": {"render": v, "build": v},
                                                          "white_balance_project": {"kelvin": 5635.0}}))
    (out / "render.log").write_text("RENDERED\n")
'''

FAKE_PY = r'''#!/usr/bin/env bash
if [ "${1:-}" = "-m" ]; then
  case "${2:-}" in
    wenart.assets) echo "assets ${*:3}" >> "$FAKE_LOG.assets"; exit 0 ;;
    wenart.blender.cli) shift 2; exec "$REAL_PY" "$FAKE_BLENDER" "$@" ;;
    pytest) { echo "pytest ${*:3}"; env | grep -E '^(RUN_TEST_PROJECTS|RENDER_TEST_PROJECTS|CHECK_TEST_PROJECTS|CHECK_MODELS|WENART_RESULTS)=' | sort; } >> "$FAKE_LOG.pytest"; exit "${FAKE_PYTEST_RC:-0}" ;;
  esac
fi
exec "$REAL_PY" "$@"
'''


def _fakes(tmp_path: Path) -> dict:
    fake_dir = tmp_path / "fakes"
    fake_dir.mkdir(parents=True)
    (fake_dir / "blender.py").write_text(FAKE_BLENDER, encoding="utf-8")
    py = fake_dir / "python"
    py.write_text(FAKE_PY, encoding="utf-8")
    py.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("WENART_", "AB_", "P6_", "RUN_", "JOB_"))}
    env.update(WENART_WS=str(tmp_path / "ws"), WENART_REPO=str(tmp_path / "repo"),
               WENART_RESULTS=str(tmp_path / "results"), WENART_ASSETS=str(tmp_path / "assets"), WENART_PY=str(py),
               WENART_BLENDER="/bin/echo", PYTHONPATH=str(ROOT), REAL_PY=sys.executable,
               FAKE_BLENDER=str(fake_dir / "blender.py"), FAKE_LOG=str(fake_dir / "log"), FAKE_DIR=str(fake_dir))
    return env


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_levers_ab_runs_the_sky_ab_on_a_run_output_with_fakes(tmp_path):
    env = _fakes(tmp_path)
    repo = tmp_path / "repo"
    run = _run_output(repo, _p6_cameras())
    env.update(AB_PROJECTS="real04", AB_VARIANTS=" ".join(AB.M13_SKY_AB_VARIANTS), AB_VIEW_SET="sky", AB_SOURCE="run",
               AB_NAME="ab_m13/sky", AB_GPU_TESTS="0", JOB_ID="t")
    proc = subprocess.run(["bash", str(LEVERS_AB)], env=env, cwd=str(repo), capture_output=True, text=True,
                          timeout=600)
    assert proc.returncode == 0, proc.stdout[-4000:] + proc.stderr[-2000:]
    res = tmp_path / "results" / "ab_m13" / "sky"
    want = ["cam_r_L0_yatak_odasi_1", "cam_r_L0_yatak_odasi_2", "cam_r_L0_e_yatak_odasi_1", "cam_r_L-1_salon_1",
            "cam_r_L-1_salon_2", "cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1"]
    for v in AB.M13_SKY_AB_VARIANTS:
        rm = json.loads((res / v / "real04" / "render_manifest.json").read_text())
        assert [r["camera"] for r in rm["renders"]] == want and rm["light_variant"]["build"] == v
        world = json.loads((res / v / "real04" / "lighting.json").read_text())["lighting"]["world"]
        assert world["strength"] == pytest.approx(2.0 ** L.light_levers(v)["sky_stops"], rel=1e-9), v
        assert (repo / "outputs" / "real04" / "ab_m13" / "sky" / v / "scene" / "scene.blend").is_file()
    assert sorted(p.name for p in (res / "sheets").iterdir()) == sorted(f"real04_{c}.jpg" for c in want)
    assert sorted(p.name for p in (res / "run_final" / "real04").iterdir()) == sorted(f"{c}_preview.jpg" for c in want)
    md = (res / "summary.md").read_text()
    assert "interior sky A/B" in md and "| real04 | sky52 | cam_r_L-1_salon_1 | 36.758" in md
    prep = json.loads((res / "prepare_real04.json").read_text())
    assert prep["source"].startswith("run ") and prep["views_replaced"][0]["used"] == "cam_r_L0_yatak_odasi_2"
    m13 = repo / "outputs" / "real04" / "ab" / "m13"
    assert (m13 / "building_final.json").read_bytes() == (run / "building_final.json").read_bytes()
    calls = [json.loads(line) for line in (tmp_path / "fakes" / "log").read_text().splitlines()]
    builds = [c for c in calls if c["cmd"] == "build"]
    renders = [c for c in calls if c["cmd"] == "render"]
    assert [c["variant"] for c in builds] == list(AB.M13_SKY_AB_VARIANTS) == [c["variant"] for c in renders]
    for c in builds:
        a = c["args"]
        assert a[a.index("--building") + 1] == "outputs/real04/ab/m13/building_final.json" and "--reuse" in a
        assert a[a.index("--style") + 1] == "outputs/real04/ab/m13/style.json"
        assert a[a.index("--brief") + 1] == "projects/real04"
        assert c["cameras_from"] == "outputs/real04/ab/m13/scene_manifest.json"
    for c in renders:
        a = c["args"]
        assert a[a.index("--cameras") + 1] == ",".join(want) and a[a.index("--samples") + 1] == "128"
        assert a[a.index("--white-balance") + 1] == "project"
    # no committed baseline was read and nothing went to the lever A/B's folders
    assert not (tmp_path / "results" / "ab_m13" / "baseline_m11").exists()
    assert not (repo / "outputs" / "real04" / "ab_m13" / "base").exists()


# --------------------------------------------------------------------------
# scripts/jobs/m13_p6.sh
# --------------------------------------------------------------------------

FAKE_FULL = r'''#!/usr/bin/env bash
set -euo pipefail
echo "RUN_PROJECTS=$RUN_PROJECTS RENDER_SAMPLES=${RENDER_SAMPLES:-} RUN_POLISH=${RUN_POLISH:-}" > "$FAKE_DIR/full.env"
p=${RUN_PROJECTS%% *}
mkdir -p "$WENART_RESULTS" "$WENART_REPO/outputs/$p/scene"
echo '{}' > "$WENART_REPO/outputs/$p/building_final.json"
echo '{"cameras": []}' > "$WENART_REPO/outputs/$p/scene/scene_manifest.json"
cat > "$WENART_RESULTS/run_manifest.json" <<EOF
{"projects": [{"name": "$p", "state": "ok", "stages": [{"stage": "build", "status": "${FAKE_BUILD_STATUS:-ok}"}]}],
 "test_lists": {"RUN_TEST_PROJECTS": "$p", "RENDER_TEST_PROJECTS": "$p", "FURNISH_TEST_PROJECTS": "",
                "CHECK_TEST_PROJECTS": "$p", "POLISH_TEST_PROJECTS": ""}}
EOF
if [ "${FAKE_JUNIT:-1}" = "1" ]; then echo '<testsuite/>' > "$WENART_RESULTS/junit-full.xml"; fi
exit "${FAKE_FULL_RC:-0}"
'''

FAKE_AB = r'''#!/usr/bin/env bash
env | grep -E '^(AB_|WENART_DEADLINE=|JOB_ID=)' | sort > "$FAKE_DIR/ab.env"
exit 0
'''


def _p6_env(tmp_path: Path, deadline_s: int | None, **extra) -> dict:
    env = _fakes(tmp_path)
    (tmp_path / "repo").mkdir(exist_ok=True)
    for name, text in (("full.sh", FAKE_FULL), ("ab.sh", FAKE_AB)):
        path = tmp_path / "fakes" / name
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)
    env.update(P6_FULL_JOB=str(tmp_path / "fakes" / "full.sh"), P6_AB_JOB=str(tmp_path / "fakes" / "ab.sh"),
               JOB_ID="p6t")
    if deadline_s is not None:
        env["WENART_DEADLINE"] = str(int(time.time()) + deadline_s)
    env.update(extra)
    return env


def _run_p6(env: dict, cwd: Path):
    return subprocess.run(["bash", str(P6_JOB)], env=env, cwd=str(cwd), capture_output=True, text=True, timeout=300)


def _ab_env(tmp_path: Path) -> dict:
    path = tmp_path / "fakes" / "ab.env"
    if not path.is_file():
        return {}
    return dict(line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)


def test_m13_p6_job_script_contract():
    subprocess.run(["bash", "-n", str(P6_JOB)], check=True)
    text = P6_JOB.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text and os.access(P6_JOB, os.X_OK)
    assert "LOGS=$WS/logs" in text and 'WS="${WENART_WS:-/workspace}"' in text and "exec > >(tee -a \"$LOG\")" in text
    assert "trap 'on_exit' EXIT" in text and "trap 'exit 143' TERM" in text and "ERR" in text
    assert "pod stop" not in text and "runpodctl" not in text          # the watchdog stops the pod, never the job
    for default in ('RUN_PROJECTS:-real04', f'P6_SKY_VARIANTS:-{" ".join(AB.M13_SKY_AB_VARIANTS)}',
                    'P6_SKY_SAMPLES:-128', 'P6_SKY_PROJECT:-real04', 'P6_SKY_AB:-1', 'P6_RESERVE_S:-600',
                    'P6_TESTS_RESERVE_S:-900', 'P6_SKY_VARIANT_EST_S:-660', 'P6_SKY_MIN_VARIANTS:-2',
                    'P6_FULL_JOB:-scripts/jobs/full.sh', 'P6_AB_JOB:-scripts/jobs/levers_ab.sh'):
        assert default in text, default
    # fix round after P6a (pin changed on purpose): the view set and the folder come from P6_SKY_VIEW_SET /
    # P6_SKY_NAME, whose defaults are P6a's (tests/test_m13_p6a_sky.py runs both)
    for setting in ('AB_VIEW_SET="$SKY_VIEW_SET"', "AB_SOURCE=run", 'AB_NAME="$SKY_NAME"', "AB_GPU_TESTS=0",
                    'P6_SKY_VIEW_SET:-sky}', 'P6_SKY_NAME:-ab_m13/sky}'):
        assert setting in text, setting
    # review: the A/B has a hard bound at its deadline (a hung Blender never runs into the watchdog)
    assert 'cap=(timeout -k 60 "$(( d - $(now_s) ))")' in text and 'run_step sky-ab "${cap[@]}" env' in text
    # the command in the header: the approved P6 settings (polish off, 256 spp, 4 h, over $5 OK)
    assert "scripts/gpu_run.py run --job scripts/jobs/m13_p6.sh" in text
    for flag in ("--max-minutes 240", "--over-5-ok", "--env RUN_POLISH=off", "--env RENDER_SAMPLES=256"):
        assert flag in text, flag


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_m13_p6_runs_the_sky_ab_after_the_full_run_with_the_reserve(tmp_path):
    env = _p6_env(tmp_path, 3 * 3600, RENDER_SAMPLES="256", RUN_POLISH="off")
    deadline = int(env["WENART_DEADLINE"])
    proc = _run_p6(env, tmp_path / "repo")
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-2000:]
    assert (tmp_path / "fakes" / "full.env").read_text().strip() == "RUN_PROJECTS=real04 RENDER_SAMPLES=256 RUN_POLISH=off"
    ab = _ab_env(tmp_path)
    # Milestone 13 final pass (23 Oct 2026; pin changed on purpose): the old world is sky0 (P6a ran it as base)
    assert ab["AB_PROJECTS"] == "real04" and ab["AB_VARIANTS"] == "sky0 sky2 sky35 sky52" and ab["AB_SAMPLES"] == "128"
    assert (ab["AB_VIEW_SET"], ab["AB_SOURCE"], ab["AB_NAME"], ab["AB_GPU_TESTS"]) == ("sky", "run", "ab_m13/sky", "0")
    assert ab["AB_VARIANT_EST_S"] == "660" and ab["JOB_ID"] == "p6t"
    assert int(ab["WENART_DEADLINE"]) == deadline - 600            # the copy reserve; full.sh's tests ran
    assert "GPU tests: full.sh ran them" in proc.stdout and not (tmp_path / "fakes" / "log.pytest").exists()
    assert (tmp_path / "results" / "m13_p6-p6t.log").is_file()


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_m13_p6_skips_the_ab_without_time_or_for_another_project(tmp_path):
    # 1000 s left: 400 after the reserve, 1320 needed for two variants -> no A/B, no failure
    env = _p6_env(tmp_path / "a", 1000)
    proc = _run_p6(env, tmp_path / "a" / "repo")
    assert proc.returncode == 0, proc.stdout[-3000:]
    assert "sky A/B skipped" in proc.stdout and _ab_env(tmp_path / "a") == {}
    # real03 (pod P6b with this job): the A/B is off
    env = _p6_env(tmp_path / "b", 3 * 3600, RUN_PROJECTS="real03")
    proc = _run_p6(env, tmp_path / "b" / "repo")
    assert proc.returncode == 0 and "sky A/B off" in proc.stdout and _ab_env(tmp_path / "b") == {}
    # P6_SKY_AB=0
    env = _p6_env(tmp_path / "c", 3 * 3600, P6_SKY_AB="0")
    proc = _run_p6(env, tmp_path / "c" / "repo")
    assert proc.returncode == 0 and "sky A/B off" in proc.stdout and _ab_env(tmp_path / "c") == {}
    # this job's run built no real04 scene: the outputs are an earlier pod's, the A/B would build them -> failure
    env = _p6_env(tmp_path / "d", 3 * 3600, FAKE_BUILD_STATUS="failed")
    proc = _run_p6(env, tmp_path / "d" / "repo")
    assert proc.returncode == 1 and "sky-ab-not-built" in proc.stdout and _ab_env(tmp_path / "d") == {}
    # a bad number fails fast
    env = _p6_env(tmp_path / "e", 3 * 3600, P6_RESERVE_S="ten")
    assert _run_p6(env, tmp_path / "e" / "repo").returncode == 2


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_m13_p6_runs_the_gpu_tests_once_when_full_sh_did_not(tmp_path):
    env = _p6_env(tmp_path, 3 * 3600, FAKE_JUNIT="0", FAKE_FULL_RC="1")
    deadline = int(env["WENART_DEADLINE"])
    proc = _run_p6(env, tmp_path / "repo")
    assert proc.returncode == 1 and "FAILED steps: full" in proc.stdout     # full.sh's exit 1 is reported
    # the A/B kept the time of the tests back
    assert int(_ab_env(tmp_path)["WENART_DEADLINE"]) == deadline - 600 - 900
    log = (tmp_path / "fakes" / "log.pytest").read_text().splitlines()
    assert len([line for line in log if line.startswith("pytest ")]) == 1
    args = log[0].split()
    assert args[:3] == ["pytest", "-m", "gpu"] and f"--junitxml={tmp_path / 'results'}/junit-full.xml" in args
    assert "tests/gpu/test_full_run.py" in args and "tests/gpu/test_render.py" in args
    assert "tests/gpu/test_furnish.py" not in args and "tests/gpu/test_polish.py" not in args   # empty lists
    assert "RUN_TEST_PROJECTS=real04" in log and "CHECK_MODELS=agent" in log
    assert "CHECK_TEST_PROJECTS=real04" in log
    # without a run manifest (the full run stopped early) nothing runs here: the same command resumes
    # review (22 Oct 2026): a rerun with P6_SKIP_FULL=1 (to finish a cut A/B) never asks for the GPU tests the
    # full-run pod ran, and keeps no test reserve
    env = _p6_env(tmp_path / "x", 3 * 3600, P6_SKIP_FULL="1")
    proc = _run_p6(env, tmp_path / "x" / "repo")
    assert proc.returncode == 1 and "sky-ab-no-run-output" in proc.stdout
    assert "gpu-tests-missing" not in proc.stdout and "run by the full-run pod" in proc.stdout
    env = _p6_env(tmp_path / "y", 3 * 3600, P6_SKIP_FULL="1")
    out = tmp_path / "y" / "repo" / "outputs" / "real04"
    (out / "scene").mkdir(parents=True)
    (out / "building_final.json").write_text("{}")
    (out / "scene" / "scene_manifest.json").write_text('{"cameras": []}')
    deadline = int(env["WENART_DEADLINE"])
    proc = _run_p6(env, tmp_path / "y" / "repo")
    assert proc.returncode == 0, proc.stdout[-3000:]
    assert int(_ab_env(tmp_path / "y")["WENART_DEADLINE"]) == deadline - 600
