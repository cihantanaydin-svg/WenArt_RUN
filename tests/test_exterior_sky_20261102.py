"""2 Nov 2026 (user requests): two general site rules for every project's exterior views.

Rule 1, clouds in the exterior sky: the camera sees a Poly Haven pure-sky HDRI (sky only, no ground) over the physical
sky, on camera rays only (the Light Path 'Is Camera Ray' branch of the exterior world); every other ray keeps the
physical sky, so the lighting, the facade exposure and the white point stay as they were. The pure sky follows the
mood, the pod fetches it with the style's assets, a missing file keeps the cloudless sky with a warning, and the scene
and render manifests say which sky was used.

Rule 2, neighbouring houses: a simple inferred house massing on each fenced neighbour plot, set back from its front,
never on our plot or a tree, hidden from shadow and diffuse rays like the horizon context, and an obstacle of the
exterior cameras.

CPU only. The bpy node check runs the pip ``bpy`` module in a subprocess and is skipped where it is not installed."""
import importlib.util
import inspect
import json
import math
import os
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Point, Polygon

from wenart import geometry as G
from wenart.assets import fetch
from wenart.blender import build as B
from wenart.blender import exterior as E
from wenart.blender import materials as M
from wenart.blender import render as R
from wenart.blender import site as S
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
FLAT = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
OURS = [(0, 0), (15, 0), (15, 12), (0, 12)]


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


PLOT = _rect(-6, -4, 25, 36)


def _neighbours():
    drive = {"id": "drive", "kind": "parking", "polygon": [(19, -4), (24, -4), (24, 35), (-1, 35), (-1, 30), (19, 30)]}
    return S.outside_roads([drive], PLOT, _rect(-60, -60, 90, 100), OURS)


# --------------------------------------------------------------------------
# Rule 1: the pure sky per mood, its fetch, the fallback and the records
# --------------------------------------------------------------------------

def test_each_mood_gets_a_pure_sky_and_a_sunless_mood_keeps_the_physical_sky():
    pick = {mood: M.exterior_cloud_sky(dict(entry, mood=mood))["hdri"] for mood, entry in V.LIGHTING.items()}
    assert pick["warm daylight"] == "kloofendal_38d_partly_cloudy_puresky"
    assert pick["cool daylight"] == pick["bright noon"] == "kloofendal_48d_partly_cloudy_puresky"
    assert pick["golden evening"] == "qwantani_sunset_puresky"
    assert pick["overcast"] == "overcast_soil_puresky" and pick["cloudy soft"] == "kloofendal_overcast_puresky"
    for mood, entry in V.LIGHTING.items():                   # every vocabulary mood: a sun above the horizon or none
        assert (pick[mood] is None) == (float(entry["sun_elevation_deg"]) <= 0.0), mood
    assert pick["night"] is None and pick["blue hour"] is None and pick["interior evening"] is None
    # only pure skies (no ground: the reason HDRIs were kept out of the exterior views), each one verified
    for hdri in set(M.EXTERIOR_CLOUD_SKIES.values()) | {M.EXTERIOR_CLOUD_DEFAULT}:
        assert hdri.endswith("_puresky") and hdri in M.PURESKY_HDRIS
    assert {M.PURESKY_HDRIS[M.EXTERIOR_CLOUD_SKIES[m]]["sky"] for m in ("overcast", "cloudy soft")} == {"overcast"}
    assert M.PURESKY_HDRIS[pick["warm daylight"]]["sky"] == "partly cloudy"
    # the overcast moods reuse their own interior HDRI (already a pure sky)
    assert pick["overcast"] == V.LIGHTING["overcast"]["hdri"] and pick["cloudy soft"] == V.LIGHTING["cloudy soft"]["hdri"]
    # an unknown daytime mood takes the default, a lighting without mood or with the sun down none
    assert M.exterior_cloud_sky({"mood": "studio sun", "sun_elevation_deg": 40})["hdri"] == M.EXTERIOR_CLOUD_DEFAULT
    assert M.exterior_cloud_sky({})["hdri"] is None
    assert M.exterior_cloud_sky({"mood": "warm daylight", "sun_elevation_deg": -2})["hdri"] is None
    assert "Poly Haven" in M.exterior_cloud_sky({"mood": "warm daylight"})["reason"]


def test_the_pod_fetches_the_pure_sky_with_the_style(tmp_path, monkeypatch):
    profile = {"lighting": {"hdri": "kloppenheim_06", "mood": "warm daylight", "sun_elevation_deg": 35}}
    assert fetch.hdri_plan(profile) == [("polyhaven", "kloppenheim_06", "style"),
                                        ("polyhaven", "kloofendal_38d_partly_cloudy_puresky", fetch.SKY_LABEL)]
    # an overcast style's own HDRI is its pure sky: fetched once
    over = {"lighting": {"hdri": "overcast_soil_puresky", "mood": "overcast", "sun_elevation_deg": 45}}
    assert fetch.hdri_plan(over) == [("polyhaven", "overcast_soil_puresky", "style")]
    assert fetch.hdri_plan({"lighting": {"hdri": "dikhololo_night", "mood": "night", "sun_elevation_deg": -10}}) == \
        [("polyhaven", "dikhololo_night", "style")]
    calls = []
    monkeypatch.setattr(fetch, "texture_plan", lambda *a, **k: [])
    monkeypatch.setattr(fetch, "shell_texture_rows", lambda style=None: [])
    monkeypatch.setattr(fetch, "site_texture_rows", lambda style=None: [])
    monkeypatch.setattr(fetch, "fetch_hdri", lambda aid, out, size="2k", source="polyhaven", licence=None:
                        calls.append((aid, size)) or {"file": f"hdris/{aid}_{size}.hdr"})
    result = fetch.fetch_for_style(profile, tmp_path, size="2k", log=lambda *_: None)
    assert calls == [("kloppenheim_06", "2k"), ("kloofendal_38d_partly_cloudy_puresky", "2k")]
    assert set(result["hdris"]) == {"kloppenheim_06", "kloofendal_38d_partly_cloudy_puresky"} and not result["failed"]
    # the build fingerprint follows it: a build cached before the file reached the volume is redone
    assert "kloofendal_38d_partly_cloudy_puresky" in B.referenced_asset_ids({}, profile)


def test_a_missing_pure_sky_keeps_the_physical_sky_and_the_build_warns(monkeypatch):
    style = {"lighting": {"mood": "warm daylight", "sun_elevation_deg": 35}}
    choice, path = B.exterior_sky_file({}, "/nowhere", style)
    assert choice["hdri"] == "kloofendal_38d_partly_cloudy_puresky" and path is None
    scene = {}
    rec = {"name": M.EXTERIOR_WORLD, "sun_elevation_deg": 35.0, "sun_azimuth_deg": 210.0, "sun_disc": True}
    out = M.exterior_sky_clouds(scene, rec, None, choice)
    assert out["exterior_sky"] == M.EXTERIOR_SKY_PHYSICAL and out["clouds"]["used"] is False
    assert "not available" in out["clouds"]["reason"] and "physical sky" in out["clouds"]["reason"]
    assert out["clouds"]["hdri"] == choice["hdri"] and "clouds" not in rec           # the input record is untouched
    assert M.exterior_sky_clouds(scene, rec, "/nowhere/x.hdr", choice)["clouds"]["used"] is False
    # a sunless mood: no choice, no warning reason beyond the choice's own
    night = M.exterior_cloud_sky({"mood": "night", "sun_elevation_deg": -10})
    assert M.exterior_sky_clouds(scene, rec, None, night)["clouds"]["reason"] == night["reason"]
    # a failure inside Blender is caught and recorded (never a crash): a bpy without the world
    fake = types.SimpleNamespace(data=types.SimpleNamespace(worlds=types.SimpleNamespace(get=lambda name: None)))
    monkeypatch.setitem(sys.modules, "bpy", fake)
    broken = M.exterior_sky_clouds(scene, rec, __file__, choice)
    assert broken["clouds"]["used"] is False and "cloud layer not built" in broken["clouds"]["reason"]
    assert scene == {}                                                  # the scene keeps the physical sky
    # the build turns a chosen but unused pure sky into a warning (not with --no-textures)
    src = inspect.getsource(B.main)
    assert "M.exterior_sky_clouds(scene, light_info[\"world_exterior\"], sky_file, sky_choice)" in src
    assert "warnings.append(f\"exterior sky: {clouds['reason']}\")" in src


def _sky_image(w=256, h=128, sun_u=0.6, sun_elev=38.0):
    """A synthetic equirectangular sky in bpy pixel order (row 0 straight down): a blue gradient, a cloud band and a
    one-pixel sun of 20000."""
    elev = ((np.arange(h) + 0.5) / h - 0.5) * 180.0
    img = np.zeros((h, w, 4), dtype=np.float32)
    img[..., 0], img[..., 1], img[..., 2], img[..., 3] = 0.3, 0.45, 0.8, 1.0
    img[(elev > 10) & (elev < 20)] = (1.2, 1.2, 1.2, 1.0)                    # clouds
    j = int(round((sun_elev / 180.0 + 0.5) * h - 0.5))
    i = int(round(sun_u * w - 0.5))
    img[j, i, :3] = 20000.0
    return img, i, j


def test_puresky_stats_find_the_sun_clip_it_and_measure_the_band():
    img, i, j = _sky_image()
    st = M.puresky_stats(img, band_deg=(2.0, 30.0), clip_x_median=16.0)
    assert st["sun_px"] == [i, j] and abs(st["sun_elevation_deg"] - 38.0) < 1.0
    assert st["sun_phi_deg"] == pytest.approx((0.5 - st["sun_u"]) * 360.0, abs=1e-3)
    lum_blue = 0.2126 * 0.3 + 0.7152 * 0.45 + 0.0722 * 0.8
    assert st["median"] == pytest.approx(lum_blue, rel=1e-5) and st["clip"] == pytest.approx(16.0 * lum_blue, rel=1e-5)
    assert lum_blue < st["band_mean"] < 1.2                                    # blue sky and the cloud band, no sun
    assert st["sun_share"] > 0.5                                               # the one-pixel sun carries the light
    # the plan: turned so the image's sun stands at the lamp's azimuth, scaled to the physical sky's band brightness
    rec = {"sun_elevation_deg": 35.0, "sun_azimuth_deg": 210.0}
    plan = M.exterior_cloud_plan(rec, st)
    assert plan["rotation_deg"] == M.puresky_rotation_deg(st["sun_phi_deg"], 210.0)
    assert plan["gain"] == pytest.approx(M.sky_band_luminance(35.0) / st["band_mean"], rel=1e-5)
    assert plan["band_physical"] == pytest.approx(7.7527) and plan["mix"] == M.EXTERIOR_CLOUDS["mix"]
    assert plan["sun_elevation_offset_deg"] == pytest.approx(st["sun_elevation_deg"] - 35.0, abs=1e-3)
    with pytest.raises(ValueError):
        M.exterior_cloud_plan(rec, dict(st, band_mean=0.0))


def test_the_rotation_puts_the_image_sun_at_the_lamp_azimuth():
    """``puresky_rotation_deg``: the world direction of the image's sun is phi - rotation (Mapping type POINT) and the
    compass azimuth A is the direction 90 - A. Checked on bpy 5.2.2 (2 Nov 2026): kloofendal_38d (sun at u 0.600)
    turned 83.97 degrees lands on the sky disc's pixel column at azimuth 210, -81.04 at azimuth 45."""
    for phi in (-36.035, 0.0, 120.0):
        for az in (0.0, 45.0, 210.0, 300.0):
            rot = M.puresky_rotation_deg(phi, az)
            assert -180.0 < rot <= 180.0
            world = math.radians(phi - rot)
            assert math.cos(world) == pytest.approx(math.cos(math.radians(90.0 - az)), abs=1e-9)
            assert math.sin(world) == pytest.approx(math.sin(math.radians(90.0 - az)), abs=1e-9)
    assert M.puresky_rotation_deg(-36.035, 210.0) == pytest.approx(83.965)
    assert M.puresky_rotation_deg(-36.035, 45.0) == pytest.approx(-81.035)


def test_the_band_table_follows_the_dome_measure():
    rows = M.SKY_BAND_TABLE
    assert [e for e, _ in rows] == [e for e, _s, _d in M.SKY_SUN_TABLE]       # the same elevations as the sun pair
    assert M.sky_band_luminance(0.0) == rows[0][1] and M.sky_band_luminance(90.0) == rows[-1][1]
    assert M.sky_band_luminance(37.5) == pytest.approx((7.7527 + 7.7256) / 2.0)
    assert all(b > 0 for _e, b in rows) and "bpy 5.2.2" in M.SKY_BAND_SOURCE


def test_the_render_manifest_names_the_sky_each_view_saw():
    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_interior": "World",
             "wenart_world_exterior_sky": "kloofendal_38d_partly_cloudy_puresky"}
    assert "wenart_world_exterior_sky" in R.WORLD_PROPS and M.EXTERIOR_SKY_PROP == "wenart_world_exterior_sky"
    assert R.exterior_sky_for(props, "exterior") == "kloofendal_38d_partly_cloudy_puresky"
    assert R.exterior_sky_for(props, "interior", "balcony") == "kloofendal_38d_partly_cloudy_puresky"   # open air
    assert R.exterior_sky_for(props, "interior", "living") is None
    assert R.exterior_sky_for(dict(props, wenart_world_exterior_sky=None), "exterior") == "physical"  # an older scene
    assert R.exterior_sky_for({"wenart_world_interior": "World"}, "exterior") is None
    assert '"exterior_sky": exterior_sky_for(props, cam.get("wenart_camera_kind"), room_type)' in inspect.getsource(R)


def test_attribution_credits_the_exterior_pure_sky(tmp_path):
    from wenart.run import copy as CO

    scene = {"lighting": {"world": {"kind": "hdri", "file": "/a/hdris/kloppenheim_06_2k.hdr"},
                          "world_exterior": {"clouds": {"used": True,
                                                        "file": "/a/hdris/kloofendal_38d_partly_cloudy_puresky_2k.hdr"}}}}
    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    credits = {c["asset_id"]: c for c in CO.texture_credits(tmp_path)}
    sky = credits["hdri:kloofendal_38d_partly_cloudy_puresky_2k"]
    assert sky["licence"] == "CC0" and sky["kind"] == "hdri" and "exterior" in sky["changes"]
    scene["lighting"]["world_exterior"]["clouds"]["used"] = False
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    assert len(CO.texture_credits(tmp_path)) == 1


BPY_NODES = textwrap.dedent(r"""
    import json, sys
    sys.path.insert(0, sys.argv[1])
    import numpy as np
    import bpy
    from wenart.blender import materials as M
    out = {}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w, h = 64, 32
    img = bpy.data.images.new("sky", w, h, float_buffer=True)
    px = np.zeros((h, w, 4), np.float32); px[...] = (0.3, 0.45, 0.8, 1.0); px[22, 38, :3] = 20000.0
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = sys.argv[2]; img.file_format = "HDR"; img.save()
    lighting = {"mood": "warm daylight", "sun_azimuth_deg": 210.0, "sun_elevation_deg": 35.0}
    for name, disc, cam_only in (("production", True, True), ("no_disc", False, True)):
        scene = bpy.context.scene
        scene.world = bpy.data.worlds.new("interior_" + name)
        rec = M.exterior_world_nodes(scene, lighting, sun_disc=disc, sun_elevation_deg=35.0, sun_azimuth_deg=210.0,
                                     sun_wm2=1000.0, disc_camera_only=cam_only)
        before = scene.get(M.EXTERIOR_SKY_PROP)
        rec = M.exterior_sky_clouds(scene, rec, sys.argv[2], M.exterior_cloud_sky(lighting))
        tree = bpy.data.worlds[M.EXTERIOR_WORLD].node_tree
        cam = tree.nodes["wenart_sky_camera"]
        src = cam.inputs["Color"].links[0].from_node
        outn = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputWorld")
        mix = outn.inputs["Surface"].links[0].from_node
        fac = mix.inputs[0].links[0].from_socket
        lit = mix.inputs[1].links[0].from_node
        lit_src = lit.inputs["Color"].links[0].from_node
        out[name] = {"used": rec["clouds"]["used"], "reason": rec["clouds"]["reason"], "sky": rec["exterior_sky"],
                     "prop_before": before, "prop": scene.get(M.EXTERIOR_SKY_PROP),
                     "camera_colour": [src.bl_idname, getattr(src, "operation", None), src.name],
                     "mix": mix.bl_idname, "factor": [fac.node.bl_idname, fac.name],
                     "camera_on_1": mix.inputs[2].links[0].from_node.name,
                     "lighting_sky": [lit_src.bl_idname, bool(getattr(lit_src, "sun_disc", True))],
                     "env": sum(1 for n in tree.nodes if n.bl_idname == "ShaderNodeTexEnvironment"),
                     "rotation": rec["clouds"]["plan"]["rotation_deg"] if rec["clouds"]["used"] else None}
    json.dump(out, open(sys.argv[3], "w"))
""")


@pytest.mark.skipif(importlib.util.find_spec("bpy") is None, reason="no bpy module (pip bpy 5.2.2)")
def test_the_cloud_layer_is_wired_on_camera_rays_only_in_bpy(tmp_path):
    """The real node graph (pip bpy, a subprocess): the camera Background's colour comes from the cloud chain, the
    Mix Shader's factor is Light Path 'Is Camera Ray', the lighting Background keeps the physical sky without the disc;
    a world with one sky for every ray is split the same way. The scene property names the pure sky."""
    script = tmp_path / "nodes.py"
    script.write_text(BPY_NODES, encoding="utf-8")
    result = tmp_path / "nodes.json"
    proc = subprocess.run([sys.executable, str(script), str(ROOT), str(tmp_path / "sky.hdr"), str(result)],
                          capture_output=True, text=True, timeout=300, env=dict(os.environ, PYTHONPATH=str(ROOT)))
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    data = json.loads(result.read_text(encoding="utf-8"))
    for name, d in data.items():
        assert d["used"] is True, (name, d["reason"])
        assert d["prop_before"] == M.EXTERIOR_SKY_PHYSICAL and d["prop"] == d["sky"] == M.EXTERIOR_CLOUD_DEFAULT
        assert d["camera_colour"] == ["ShaderNodeVectorMath", "MULTIPLY_ADD", M.CLOUD_NODE_PREFIX + "colour"]
        assert d["mix"] == "ShaderNodeMixShader" and d["factor"] == ["ShaderNodeLightPath", "Is Camera Ray"]
        assert d["camera_on_1"] == "wenart_sky_camera" and d["env"] == 1
        assert d["lighting_sky"] == ["ShaderNodeTexSky", False]          # every other ray: the sky, no disc
        assert -180.0 < d["rotation"] <= 180.0


# --------------------------------------------------------------------------
# Rule 2: the neighbouring houses
# --------------------------------------------------------------------------

def test_a_house_stands_on_each_neighbour_plot_set_back_and_never_on_ours():
    nbs = _neighbours()["neighbours"]
    res = S.neighbour_houses(nbs, FLAT, keep_out=[PLOT, OURS])
    assert len(res["houses"]) == len(nbs) >= 4 and not res["skipped"]
    ours = Polygon(PLOT).buffer(S.NEIGHBOUR_HOUSES["clear_m"])
    by_plot = {nb["id"]: nb for nb in nbs}
    c = S.NEIGHBOUR_HOUSES
    for h in res["houses"]:
        foot = Polygon(h["footprint"])
        plot = Polygon(by_plot[h["plot"]]["polygon"])
        assert plot.contains(foot) and not foot.intersects(ours)
        assert plot.exterior.distance(foot) >= min(c["side_m"], c["front_m"]) - 1e-6
        a, b = h["front"]
        assert min(G.point_segment_distance(p, a, b) for p in h["footprint"]) == pytest.approx(c["front_m"], abs=1e-3)
        assert c["width_m"][0] - 1e-6 <= h["width_m"] <= c["width_m"][1] + 1e-6
        assert c["depth_m"][0] - 1e-6 <= h["depth_m"] <= c["depth_m"][1] + 1e-6
        assert h["storeys"] in (1, 2) and h["roof"] in ("gable", "flat")
        assert h["inferred"] is True and h["source"] == "inferred" and h["context"] is True and "inferred" in h["reason"]
        assert h["hidden_rays"] == list(S.CONTEXT_HIDDEN_RAYS) and "visible_shadow" in h["hidden_rays"]
        assert h["base_z"] < 0.0 < h["eave_z"] < h["top_z"] < 12.0
        gate = next(s for s in by_plot[h["plot"]]["fence"] if s["kind"] == "gate")      # the front holds the gate
        assert G.point_segment_distance(G.segment_midpoint(gate["start"], gate["end"]), a, b) < 1e-6
        mid = G.segment_midpoint(a, b)
        o = h["axes"]["origin"]
        assert (mid[0] - o[0]) * h["facing"][0] + (mid[1] - o[1]) * h["facing"][1] > 0       # it faces its front
    assert {h["roof"] for h in res["houses"]} == {"gable", "flat"}
    assert S.neighbour_houses(nbs, FLAT, keep_out=[PLOT, OURS]) == res                      # deterministic


def test_trees_and_our_plot_keep_houses_away_and_the_switch_turns_them_off(monkeypatch):
    nbs = _neighbours()["neighbours"]
    first = S.neighbour_houses(nbs, FLAT, keep_out=[PLOT])["houses"][0]
    centre = Polygon(first["footprint"]).centroid
    crown = list(Point(centre.x, centre.y).buffer(3.0).exterior.coords)
    res = S.neighbour_houses(nbs, FLAT, keep_out=[PLOT], avoid=[crown])
    assert first["plot"] in {s["plot"] for s in res["skipped"]}
    assert "tree" in next(s for s in res["skipped"] if s["plot"] == first["plot"])["reason"]
    assert all(not Polygon(h["footprint"]).intersects(Polygon(crown)) for h in res["houses"])
    # a plot that is our own (or touches it) gets no house
    whole = S.neighbour_houses(nbs, FLAT, keep_out=[_rect(-100, -100, 200, 200)])
    assert not whole["houses"] and len(whole["skipped"]) == len(nbs)
    # the switch (constant and environment)
    monkeypatch.delenv(S.NEIGHBOUR_HOUSES_ENV, raising=False)
    assert S.neighbour_houses_on() is True and S.neighbour_houses_on(False) is False
    monkeypatch.setenv(S.NEIGHBOUR_HOUSES_ENV, "off")
    assert S.neighbour_houses_on() is False


def test_house_parts_are_closed_solids_with_roof_and_panes():
    houses = S.neighbour_houses(_neighbours()["neighbours"], FLAT, keep_out=[PLOT])["houses"]
    for h in houses[:3]:
        v, f, slots = S.neighbour_house_parts(h)
        assert len(f) == len(slots) and set(slots) <= {"facade", "roof", "flat_roof", "window"}
        assert "window" in slots and ("roof" in slots if h["roof"] == "gable" else "flat_roof" in slots)
        vol = 0.0
        for face in f:
            p0 = np.asarray(v[face[0]])
            for k in range(1, len(face) - 1):
                vol += float(np.dot(p0, np.cross(np.asarray(v[face[k]]), np.asarray(v[face[k + 1]])))) / 6.0
        body = h["width_m"] * h["depth_m"] * (h["eave_z"] - h["base_z"])
        assert vol > body * 0.98                         # wound outwards; the roof adds to the body
        zs = [p[2] for p in v]
        assert min(zs) == pytest.approx(h["base_z"], abs=1e-4) and max(zs) == pytest.approx(h["top_z"], abs=1e-4)
    looks = S.neighbour_house_looks(houses)
    assert [k for k, _ in looks][:3] == ["render|off white", "clay_tiles|", "aluminium_anthracite|"]
    slugs = dict(E.build_finish_slugs({}))                # the assets stage fetches their sets
    for slug in {S.NEIGHBOUR_HOUSES["facade"], S.NEIGHBOUR_HOUSES["flat_roof"], S.NEIGHBOUR_HOUSES["window"],
                 *S.NEIGHBOUR_HOUSES["roofs"]}:
        assert slug in slugs and (slug in V.MATERIALS or slug in V.FURNITURE_MATERIALS)


def test_houses_are_exterior_camera_obstacles():
    roads = _neighbours()
    houses = S.neighbour_houses(roads["neighbours"], FLAT, keep_out=[PLOT, OURS])
    plan = {"terrain": FLAT, "extent": _rect(-60, -60, 90, 100), "outline": OURS, "copy_holes": [], "plot_walls": [],
            "inferred": {}, "platforms": [], "hedges": [], "trees": [], "neighbour_houses": houses}
    m = E.build_model({"walls": []}, [], None, plan)
    assert E.LABELS["neighbour"] in m.labels and len(m.neighbour_prisms) == len(houses["houses"])
    h = houses["houses"][0]
    c = Polygon(h["footprint"]).centroid
    assert m.inside((c.x, c.y, 1.6)) == "neighbour"                       # no camera inside a house
    assert m.inside((c.x, c.y, h["top_z"] + 5.0)) is None
    # a ray through the house hits it: a camera behind it sees the house, not our building
    o = h["axes"]["origin"]
    behind = (o[0] - 30.0 * h["facing"][0], o[1] - 30.0 * h["facing"][1], 1.6)
    d = np.array([[h["facing"][0], h["facing"][1], 0.0]])
    labels, _t = m.cast(behind, d)
    assert int(labels[0]) == E.LABELS["neighbour"]
    assert "\"neighbour\"))" in inspect.getsource(E.view_check)         # a ray ending on a house counts as blocked


def test_the_horizon_context_leaves_room_for_the_houses():
    houses = S.neighbour_houses(_neighbours()["neighbours"], FLAT, keep_out=[PLOT])["houses"]
    h = houses[0]
    c = Polygon(h["footprint"]).centroid
    ctx = {"trees": [{"center": [c.x, c.y], "width": 6.0, "species": "oak"},
                     {"center": [500.0, 500.0], "width": 6.0, "species": "birch"}],
           "count": 2, "species": {"oak": 1, "birch": 1}, "reason": "context"}
    out = S.clear_context_for_houses(ctx, houses)
    assert out["count"] == 1 and out["species"] == {"birch": 1} and out["cleared_for_houses"] == 1
    assert "neighbouring houses" in out["reason"] and ctx["count"] == 2
    assert S.clear_context_for_houses(dict(ctx, trees=ctx["trees"][1:]), houses)["count"] == 2
    assert S.clear_context_for_houses(None, houses) is None
