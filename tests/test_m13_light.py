"""Milestone 13 track T5 (docs/milestone13.md §13.1, §13.2, K5 light / materials / render, K8 camera replay): the
pure parts, no Blender.

- the sun constant and the A/B variants (``lighting.SUN_STRENGTH_WM2``, ``WENART_LIGHT_VARIANT``), the mood factor;
- the EV cap ``render.EXPOSURE_LIMITS = (-2, 3)`` and the ``lighting_dark`` finding, the Milestone 11 limits for the
  A/B base; the project white balance helpers;
- the dim-room rule scaled by the sun;
- the room rig table (real lumens -> watts through the manual's table) and the pure fixture placement;
- the shell material table: every asset id exists in the vocabulary and in the asset checks file (never invented);
- the exterior world record with the sun disc and the hidden lamp;
- the camera replay parser on the committed real02 scene manifest, the camera file in the build fingerprint;
- ``ab.prepare_m13`` from a directory and for a project without camera records, the 8 + 8 fixed views;
- the lever A/B job script (``bash -n`` and its contract lines);
- the fabric colour path (bug B1) and the stage / plan pass-through.
Every test here fails on the Milestone 12 code (the constants, functions and flags did not exist).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from wenart.blender import build as B
from wenart.blender import cameras as C
from wenart.blender import lighting as L
from wenart.blender import looks as LK
from wenart.blender import materials as M
from wenart.blender import render as R
from wenart.run import ab as AB
from wenart.run import plan as PL
from wenart.run import stages as S
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
REAL02 = ROOT / "results" / "renders" / "real02" / "scene_manifest.json"
REAL03 = ROOT / "results" / "renders" / "real03" / "scene_manifest.json"


# --------------------------------------------------------------------------
# Sun constant, variants, mood factor
# --------------------------------------------------------------------------

def test_sun_constant_and_the_light_variants():
    assert isinstance(L.SUN_STRENGTH_WM2, float) and L.SUN_STRENGTH_WM2 > 0
    assert L.LIGHT_VARIANTS == ("base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
    assert L.SUN_VARIANT_WM2 == {"sun100": 100.0, "sun300": 300.0, "sun1000": 1000.0}
    # Production (no variant): the constant and the EV cap on; the rig and the shell table wait for the lead's
    # decision from P1 (LEVER_DEFAULTS: the Milestone 6-12 lights and materials until then).
    prod = L.light_levers(env={})
    assert prod["variant"] is None and prod["sun_wm2"] == L.SUN_STRENGTH_WM2 and prod["source"] == "default"
    assert prod["ev_cap"] and prod == {**prod, **{k: bool(v) for k, v in L.LEVER_DEFAULTS.items()}}
    assert set(L.LEVER_DEFAULTS) == {"ev_cap", "rig", "shell"} and L.LEVER_DEFAULTS["ev_cap"] is True
    # Every named variant starts from the Milestone 11 base (sun 3.0, no cap, no rig, no shell).
    base = L.light_levers("base")
    assert (base["sun_wm2"], base["ev_cap"], base["rig"], base["shell"]) == (3.0, False, False, False)
    for name, wm2 in L.SUN_VARIANT_WM2.items():
        lv = L.light_levers(env={L.LIGHT_VARIANT_ENV: name})
        assert lv["sun_wm2"] == wm2 and not lv["ev_cap"] and not lv["rig"] and not lv["shell"]
        assert lv["variant"] == name and lv["source"] == "env"
    assert L.light_levers("evcap")["ev_cap"] and L.light_levers("evcap")["sun_wm2"] == 3.0
    assert L.light_levers("rig")["rig"] and not L.light_levers("rig")["shell"]
    assert L.light_levers("shell")["shell"] and not L.light_levers("shell")["rig"]
    every = L.light_levers("all")
    assert (every["sun_wm2"], every["ev_cap"], every["rig"], every["shell"]) == (300.0, True, True, True)
    combo = L.light_levers("sun1000+rig")
    assert combo["sun_wm2"] == 1000.0 and combo["rig"] and not combo["ev_cap"] and combo["names"] == ["sun1000", "rig"]
    assert L.parse_light_variant("") == [] and L.parse_light_variant(None) == []
    with pytest.raises(ValueError, match="unknown variant"):
        L.parse_light_variant("sun200")
    with pytest.raises(ValueError, match="more than one sun"):
        L.parse_light_variant("sun100,sun300")
    # The style's sun_strength is a factor against warm daylight (3.0): overcast keeps a tenth, night none.
    assert L.sun_strength_wm2({"sun_strength": 3.0}, L.light_levers("sun300")) == (300.0, 1.0)
    assert L.sun_strength_wm2(V.LIGHTING["overcast"], L.light_levers("sun1000")) == (100.0, 0.1)
    assert L.sun_strength_wm2(V.LIGHTING["night"], L.light_levers("sun1000")) == (0.0, 0.0)
    assert L.sun_strength_wm2({}, L.light_levers(env={}))[0] == L.SUN_STRENGTH_WM2


def test_dim_room_rule_follows_the_sun():
    small = [{"type": "window", "width": 0.6, "height": 1.2, "sill_height": 0.9}]
    assert "0.060 < 0.08" in L.fill_light_reason(small, 0.06)                      # the Milestone 6 rule as it was
    assert "0.060 < 0.08" in L.fill_light_reason(small, 0.06, sun_wm2=3.0)
    assert L.fill_light_reason(small, 0.06, sun_wm2=300.0) is None                # 100x the daylight: no fill
    assert L.fill_light_reason(small, 0.0005, sun_wm2=300.0).endswith("< 0.08)")
    assert "x sun 300/3 W/m2" in L.fill_light_reason(small, 0.0005, sun_wm2=300.0)
    assert L.fill_light_reason([], None, sun_wm2=300.0) == "room has no window"


# --------------------------------------------------------------------------
# EV cap, lighting_dark, project white balance
# --------------------------------------------------------------------------

def test_ev_cap_and_the_lighting_dark_finding():
    assert R.EXPOSURE_LIMITS == (-2.0, 3.0) and R.EXPOSURE_LIMITS_M11 == (-2.0, 8.0)
    assert R.exposure_limits_for(L.light_levers("base")) == (-2.0, 8.0)
    assert R.exposure_limits_for(L.light_levers("sun300")) == (-2.0, 8.0)
    assert R.exposure_limits_for(L.light_levers("evcap")) == (-2.0, 3.0)
    assert R.exposure_limits_for(L.light_levers("all")) == (-2.0, 3.0)
    assert R.exposure_limits_for(L.light_levers(env={})) == (-2.0, 3.0)
    ev, raw, at_limit = R.exposure_from(0.9 / 2 ** 6.5)
    assert ev == 3.0 and raw == pytest.approx(6.5, abs=1e-3) and at_limit
    dark = R.lighting_dark_entry("cam_r_L0_yatak_odasi_1", "r_L0_yatak_odasi", raw, ev, R.EXPOSURE_LIMITS, 0.0099)
    assert dark["check"] == "lighting_dark" and dark["severity"] == "critical" and dark["target"] == "cam_r_L0_yatak_odasi_1"
    assert dark["room_id"] == "r_L0_yatak_odasi" and dark["metrics"]["ev_cap"] == 3.0
    assert dark["metrics"]["stops_over_cap"] == pytest.approx(3.5, abs=1e-3) and "+6.50 EV" in dark["message"]
    assert set(dark) == {"check", "severity", "target", "room_id", "message", "metrics"}      # the Violation shape
    major = R.lighting_dark_entry("c", "r", 4.0, 3.0, (-2.0, 3.0))
    assert major["severity"] == "major" and major["metrics"]["incident_p50"] is None
    assert R.lighting_dark_entry("c", "r", 2.9, 2.8333, (-2.0, 3.0), 0.1) is None
    assert R.lighting_dark_entry("c", "r", None, 0.0, (-2.0, 3.0)) is None
    assert R.lighting_dark_entry("c", "r", 5.0, 5.0, R.EXPOSURE_LIMITS_M11) is None        # the base variant


def test_project_white_balance_helpers(tmp_path):
    assert R.parse_white_balance("project") == ("project", None)
    assert R.parse_white_balance("kelvin:5300") == ("kelvin", [5300.0])
    with pytest.raises(R.UsageError):
        R.parse_white_balance("kelvin:100")
    with pytest.raises(R.UsageError):
        R.parse_white_balance("locked")
    assert R.project_wb_camera([("ext_1", "exterior"), ("cam_b", "interior"), ("cam_a", None)]) == "cam_a"
    assert R.project_wb_camera([("ext_2", "exterior"), ("ext_1", "exterior")]) == "ext_1"
    assert R.project_wb_camera([]) is None
    base = dict(samples=128, resolution=[1920, 1080], denoiser="OPENIMAGEDENOISE", exposure_mode="auto",
                exposure_value=None, target=0.9, wb_mode="project", wb_fixed=None, hidden=[], plugged=[])
    k_none = R.render_key(R.key_settings(**base))
    k_wp = R.render_key(R.key_settings(**base, project_whitepoint=[1.1, 1.0, 0.8]))
    k_wp2 = R.render_key(R.key_settings(**base, project_whitepoint=[1.2, 1.0, 0.8]))
    assert len({k_none, k_wp, k_wp2}) == 3
    manifest = tmp_path / "render_manifest.json"
    assert R.load_project_whitepoint(manifest) is None
    manifest.write_text(json.dumps({"white_balance_project": {"whitepoint": [1.1, 1.0, 0.8], "source": "metered on c"}}))
    assert R.load_project_whitepoint(manifest)["whitepoint"] == [1.1, 1.0, 0.8]
    manifest.write_text(json.dumps({"white_balance_project": {"whitepoint": None}}))
    assert R.load_project_whitepoint(manifest) is None
    assert R.RENDER_CODE_VERSION == "m13.1"
    # The sun lamp hides under the exterior world with a sun disc only.
    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_exterior_sun_disc": True}
    assert R.sun_hidden_for(props, "exterior") and not R.sun_hidden_for(props, "interior")
    assert not R.sun_hidden_for(dict(props, wenart_world_exterior_sun_disc=False), "exterior")
    assert not R.sun_hidden_for({}, "exterior")


# --------------------------------------------------------------------------
# The room rig
# --------------------------------------------------------------------------

def test_lumens_to_watts_follow_the_manual_table():
    # Blender 5.2 manual, "Power of Lights": 800 lm LED bulb 2.1 W, 1000 lm bulb 2.9 W, 1500 lm PAR38 4 W,
    # 2500 lm tube 4.5 W; linear between the rows.
    assert L.watts_for_lumens(800) == 2.1 and L.watts_for_lumens(1000) == 2.9
    assert L.watts_for_lumens(1500) == 4.0 and L.watts_for_lumens(2500) == 4.5
    assert L.watts_for_lumens(0) == 0.0 and L.watts_for_lumens(400) == pytest.approx(1.05)
    assert L.watts_for_lumens(1100) == pytest.approx(2.9 + 1.1 * 100 / 500, abs=1e-3)
    assert L.watts_for_lumens(5000) == pytest.approx(9.0)
    assert "light_object.html" in L.LUMEN_WATT_SOURCE


def test_room_rig_table():
    assert set(L.ROOM_RIGS) == {"dining", "living", "kitchen", "bedroom", "bathroom", "wc", "hall", "stair"}
    for room_type, fixtures in L.ROOM_RIGS.items():
        rig = L.room_rig(room_type)
        assert len(rig) == len(fixtures) >= 1
        for f in rig:
            assert f["kind"] in L.RIG_KINDS and f["source"] and len(f["size_m"]) == 3
            if "lumens" in f:
                assert f["lumens"] > 0 and f["watts_radiometric"] == L.watts_for_lumens(f["lumens"])
                assert f["watts_applied"] == pytest.approx(f["watts_radiometric"] * L.RIG_GAIN)
            else:
                assert f["kind"] == "strip" and f["lumens_per_m"] > 0
            assert f["gain"] == L.RIG_GAIN and f["lumen_watt_source"] == L.LUMEN_WATT_SOURCE
    for room_type in ("storage", "balcony", "shaft", "unknown", "other", None):
        assert L.room_rig(room_type) == []
    assert [f["kind"] for f in L.room_rig("kitchen")] == ["strip", "ceiling"]
    assert [f["kind"] for f in L.room_rig("bathroom")] == ["mirror", "ceiling"]
    assert [f["kind"] for f in L.room_rig("bedroom")] == ["bedside"] and L.room_rig("bedroom")[0]["count"] == 2
    assert L.room_rig("dining")[0]["lumens"] == 2400.0 and L.room_rig("dining")[0]["watts_radiometric"] == 4.45
    # Warm fixtures: 2700 K unless the style's sun is warmer still.
    assert L.rig_temperature_k({"colour_temperature_k": 5200}) == 2700.0
    assert L.rig_temperature_k({"colour_temperature_k": 2200}) == 2200.0
    assert L.rig_temperature_k({}) == 2700.0 and L.rig_temperature_k({"colour_temperature_k": "x"}) == 2700.0


def _piece(pid, ftype, center, size, front=270.0, rot=0.0):
    return {"id": pid, "type": ftype, "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
            "front_deg": front, "room_id": "r1"}


def test_rig_plan_places_the_fixtures_on_their_anchors():
    bedroom = {"id": "r1", "room_type": "bedroom", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    bed = _piece("bed", "bed_double", (2.0, 2.0), (1.8, 2.0), front=270.0)   # the head against the +y wall
    stands = [_piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4)), _piece("n2", "nightstand", (3.2, 2.75), (0.45, 0.4))]
    plan = L.rig_plan(bedroom, [bed] + stands, 0.0, 2.7, lighting={"colour_temperature_k": 5200})
    assert [f["kind"] for f in plan["fixtures"]] == ["bedside", "bedside"] and plan["dropped"] == []
    assert sorted(f["anchor_id"] for f in plan["fixtures"]) == ["n1", "n2"]
    assert all(f["temperature_k"] == 2700.0 and f["light"]["type"] == "POINT" for f in plan["fixtures"])
    assert all(f["light"]["energy_w"] == L.room_rig("bedroom")[0]["watts_applied"] for f in plan["fixtures"])
    assert all(0.5 < f["center"][2] < 1.2 for f in plan["fixtures"])              # on the nightstand top
    # Without nightstands the lamps stand beside the bed head; a bed-less bedroom drops them with the reason.
    plan = L.rig_plan(bedroom, [bed], 0.0, 2.7)
    assert [f["anchor_id"] for f in plan["fixtures"]] == ["bed", "bed"]
    assert all(f["center"][1] > 2.5 for f in plan["fixtures"])                     # at the head (+y) side
    plan = L.rig_plan(bedroom, [], 0.0, 2.7)
    assert plan["fixtures"] == [] and "no bed" in plan["dropped"][0]["reason"]
    # The agent's set_lighting factor scales the powers.
    plan = L.rig_plan(bedroom, [bed], 0.0, 2.7, agent_factor=2.0)
    assert plan["fixtures"][0]["light"]["energy_w"] == pytest.approx(2.0 * L.room_rig("bedroom")[0]["watts_applied"])
    # Dining: the pendant over the table, 0.75 m above its top; living: only with a dining table (optional).
    dining = {"id": "r1", "room_type": "dining", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    table = _piece("t", "table_dining", (2.5, 2.0), (1.8, 0.9))
    plan = L.rig_plan(dining, [table], 0.0, 2.7)
    (pendant,) = plan["fixtures"]
    assert pendant["kind"] == "pendant" and pendant["anchor_id"] == "t" and pendant["center"][:2] == [2.5, 2.0]
    assert pendant["center"][2] == pytest.approx(0.75 + 0.75 + 0.07)
    assert L.rig_plan(dict(dining, room_type="living"), [], 0.0, 2.7) == {"fixtures": [], "dropped": []}
    assert L.rig_plan(dining, [], 0.0, 2.7)["dropped"][0]["kind"] == "pendant"
    # Kitchen: the strip under the wall cabinets along the counter (in front of its back edge), a ceiling fixture.
    kitchen = {"id": "r1", "room_type": "kitchen", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    counter = _piece("k", "kitchen_counter", (2.0, 2.7), (3.0, 0.6), front=270.0)  # back against y = 3
    plan = L.rig_plan(kitchen, [counter], 0.0, 2.7)
    kinds = [f["kind"] for f in plan["fixtures"]]
    assert kinds == ["strip", "ceiling"]
    strip = plan["fixtures"][0]
    assert strip["light"]["type"] == "AREA" and strip["length_m"] == pytest.approx(2.9)
    assert strip["center"][1] == pytest.approx(3.0 - L.RIG_STRIP_SETBACK_M) and strip["center"][2] < L.RIG_WALL_CABINET_BOTTOM_M
    assert strip["lumens"] == pytest.approx(500.0 * 2.9) and strip["light"]["direction"] == [0.0, 0.0, -1.0]
    # Bathroom: the mirror light over the basin against its wall, a ceiling fixture at the pole.
    bath = {"id": "r1", "room_type": "bathroom", "polygon": [[0, 0], [2.5, 0], [2.5, 2], [0, 2]]}
    basin = _piece("b", "washbasin", (1.0, 1.75), (0.6, 0.5), front=270.0)
    plan = L.rig_plan(bath, [basin], 0.0, 2.5)
    mirror, ceiling = plan["fixtures"]
    assert mirror["kind"] == "mirror" and mirror["center"][2] == pytest.approx(L.RIG_MIRROR_LIGHT_Z_M)
    assert mirror["center"][1] == pytest.approx(2.0 - 0.04) and mirror["anchor_id"] == "b"
    assert ceiling["kind"] == "ceiling" and ceiling["center"][2] == pytest.approx(2.5 - 0.03 - 0.04)
    # A long hall gets one ceiling fixture per 3 m (area_light_plans), a short one a single fixture.
    hall = {"id": "r1", "room_type": "hall", "polygon": [[0, 0], [12, 0], [12, 1.5], [0, 1.5]]}
    assert len(L.rig_plan(hall, [], 0.0, 2.7)["fixtures"]) == len(L.area_light_plans(hall["polygon"])) >= 2
    short = {"id": "r1", "room_type": "hall", "polygon": [[0, 0], [3, 0], [3, 1.5], [0, 1.5]]}
    assert len(L.rig_plan(short, [], 0.0, 2.7)["fixtures"]) == 1
    # A fixture mesh is real geometry: a drum of 8 sides (10 faces) for a pendant, a bar for a strip.
    verts, faces = L._fixture_mesh(pendant)
    assert len(verts) == 16 and len(faces) == 10
    verts, faces = L._fixture_mesh(strip)
    assert len(verts) == 8 and len(faces) == 6


# --------------------------------------------------------------------------
# The shell material table and the exterior world
# --------------------------------------------------------------------------

def test_shell_slot_table_resolves_to_existing_cc0_assets():
    checks = json.loads((ROOT / "wenart" / "style" / "asset_checks_m10.json").read_text(encoding="utf-8"))
    checked = {entry["asset"]: entry for entry in checks["textures"].values()}
    known = {e.get("asset") for e in list(V.MATERIALS.values()) + list(V.FURNITURE_MATERIALS.values()) if e.get("asset")}
    assert tuple(M.SHELL_SLOTS) == M.SHELL_SLOT_NAMES == ("ceiling", "worktop", "front", "ceramic", "metal", "tile", "plaster")
    for slot, asset in M.shell_assets().items():
        if asset is None:
            assert slot in ("ceramic", "tile", "plaster")
            continue
        assert asset in known, (slot, asset)                       # an id of the style vocabulary, never invented
        assert checked[asset]["exists"] is True and checked[asset]["licence"] == "CC0", (slot, asset)
        assert checked[asset]["source"] in M.CC0_SOURCES
    assert M.shell_assets()["ceiling"] == "white_plaster_02" and M.shell_assets()["worktop"] == "marble_01"
    assert M.shell_assets()["front"] == "white_planks_clean" and M.shell_assets()["metal"] == "Metal032"
    # Slugs -> slots: the ceiling is plaster_white asked without an asset (the style profiles' ceiling slot).
    assert M.shell_slot_of("plaster_white", None) == "ceiling" and M.shell_slot_of("plaster_white", "white_plaster_02") == "plaster"
    assert M.shell_slot_of("paint", "plastered_wall") == "plaster" and M.shell_slot_of("lime_plaster") == "plaster"
    assert M.shell_slot_of("stone_worktop") == "worktop" and M.shell_slot_of("painted_wood_white") == "front"
    assert M.shell_slot_of("ceramic_white") == "ceramic" and M.shell_slot_of("steel_brushed") == "metal"
    assert M.shell_slot_of("metal_brass") == "metal" and M.shell_slot_of("tiles_light") == "tile"
    assert M.shell_slot_of("tiles_subway") == "tile" and M.shell_slot_of("wood_oak_light", "WoodFloor051") is None
    assert M.shell_slot_of("fabric_linen") is None and M.shell_slot_of("glass") is None
    # The layers per slot (the Blender 5.2 Principled inputs and nodes named in the module docstring).
    spec = M.shell_slot_spec("tile", {})
    assert set(spec["layers"]) == {"coat", "displacement", "ao", "imperfection"} and spec["layers"]["coat"]["ior"] == 1.5
    assert M.shell_slot_spec("ceiling", {})["layers"]["ao"]["distance_m"] == 0.3
    assert M.shell_slot_spec("ceiling", {"ceiling": {"material": "plaster_white", "asset": "beige_wall_001"}})["asset"] == \
        "beige_wall_001"                                           # the style's own ceiling set wins
    assert "bevel" in M.shell_slot_spec("plaster", {})["layers"] and "coat" in M.shell_slot_spec("ceramic", {})["layers"]
    assert M.shell_slot_spec("ceramic", {})["layers"]["coat"]["weight"] == 1.0
    for slot in M.SHELL_SLOT_NAMES:
        s = M.shell_slot_spec(slot, {})
        for name, layer in s["layers"].items():
            assert name in ("coat", "sheen", "bevel", "ao", "imperfection", "displacement"), (slot, name)
            if name == "coat":
                assert 0 < layer["weight"] <= 1.0 and 1.0 <= layer["ior"] <= 2.0 and 0 <= layer["roughness"] <= 1
            if name == "bevel":
                assert 0.0005 <= layer["radius_m"] <= 0.01
            if name == "ao":
                assert 0.1 <= layer["distance_m"] <= 0.5 and 0 < layer["mix"] <= 0.2
    with pytest.raises(KeyError):
        M.shell_slot_spec("floor", {})
    # Fabrics get the Principled sheen, woods a light coat; other kinds nothing.
    assert M.material_kind_layers("fabric_linen") == {"sheen": {"weight": 0.5, "roughness": 0.5}}
    assert "coat" in M.material_kind_layers("wood_veneer_oak") and M.material_kind_layers("ceramic_white") is None
    assert M.material_kind_layers("grass") is None
    # The library takes the levers: shell on under the shell / all variants, off under the base; production follows
    # LEVER_DEFAULTS (the lead's flag after P1).
    assert M.MaterialLibrary({}, None, levers=L.light_levers("base")).shell_on is False
    assert M.MaterialLibrary({}, None, levers=L.light_levers("shell")).shell_on is True
    assert M.MaterialLibrary({}, None, levers=L.light_levers("all")).shell_on is True
    assert M.MaterialLibrary({}, None, levers=L.light_levers(env={})).shell_on is bool(L.LEVER_DEFAULTS["shell"])
    assert M.MaterialLibrary({}, None, levers={"shell": True}).shell_on is True


def test_exterior_world_record_with_the_sun_disc():
    lighting = {"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 45.0}
    old = M.exterior_world(lighting)                                      # the Milestone 11 record, unchanged
    assert old["sun_disc"] is False and old["direct_sun"] == "lamp" and old["strength"] == 0.5
    rec = M.exterior_world(lighting, sun_disc=True, sun_elevation_deg=40.0, sun_azimuth_deg=100.0, sun_wm2=300.0)
    assert rec["sun_disc"] is True and rec["direct_sun"] == "sky disc"
    assert (rec["sun_elevation_deg"], rec["sun_azimuth_deg"]) == (40.0, 100.0)    # the arguments win
    # The world's Background Strength (0.5 x the mood's 1.0 for warm daylight) scales the disc too, so the
    # intensity is 300 / (1000 x 0.5) = 0.6 (T5 review, 15 Oct 2026).
    assert rec["strength"] == 0.5 and rec["sun_disc_world_strength"] == 0.5
    assert rec["sun_intensity"] == pytest.approx(0.6) and rec["sun_size_deg"] == 0.545
    assert rec["sun_disc_reference_wm2"] == 1000.0 and "does not double the sun" in rec["reason"]
    assert M.sky_sun_intensity(None) == 1.0 and M.sky_sun_intensity(1000.0) == 1.0 and M.sky_sun_intensity(3.0) == 0.003
    assert M.sky_sun_intensity(300.0, world_strength=0.5) == 0.6 and M.sky_sun_intensity(300.0, 1000.0, 1.0) == 0.3
    assert M.sky_sun_intensity(2e6) == 1000.0                                # the node's range


def test_fabric_colour_path_b1():
    style = {"furniture": {"fabric_colour": "grey", "by_type": {"sofa": {"fabric_colour": "light grey",
                                                                           "material_tags": ["fabric"]}}}}
    sofa = {"type": "sofa", "design": {"material_tags": ["fabric"]}}
    assert LK.fabric_colour_for(sofa, style) == ("light grey", "style.json furniture.by_type.sofa")
    assert LK.fabric_colour_for({"type": "armchair", "design": {}}, style) == ("grey", "style.json furniture.fabric_colour")
    assert LK.fabric_colour_for({"type": "armchair", "asset": {"fabric_colour": "sand"}}, style) == \
        ("sand", "asset.fabric_colour (fit stage)")
    assert LK.fabric_colour_for({"type": "sofa", "design": {"fabric_colour": "navy"}}, style)[0] == "navy"
    assert LK.fabric_colour_for({"type": "table_coffee", "design": {}}, style) == (None, None)
    design, notes = LK.design_for(sofa, style)
    assert design["fabric_colour"] == "light grey" and any("M13 B1" in n for n in notes)
    design, notes = LK.design_for({"type": "table_coffee", "design": {"material_tags": ["glass"]}}, style)
    assert "fabric_colour" not in design and notes == ["furniture.design (layout stage)"]


# --------------------------------------------------------------------------
# Camera replay (K8)
# --------------------------------------------------------------------------

def test_replay_parser_reads_the_committed_m11_cameras():
    manifest = json.loads(REAL02.read_text(encoding="utf-8"))
    out = C.replay_cameras(manifest)
    plans = out["plans"]
    assert len(plans) == len(manifest["cameras"]) == 41 and out["dropped"] == [] and out["policy"] == "search"
    assert all(p["source"] == "replayed" and p["replayed_from"]["camera_policy"] == "search" for p in plans)
    first = next(p for p in plans if p["name"] == "cam_r_L-1_salon_1")
    rec = next(c for c in manifest["cameras"] if c["name"] == "cam_r_L-1_salon_1")
    assert first["position"] == rec["position"] and first["target"] == rec["target"]
    assert (first["lens_mm"], first["sensor_mm"], first["shift_y"], first["room_id"], first["level_id"]) == \
        (18.0, 36.0, -0.1, "r_L-1_salon", "L-1")
    assert first["kind"] == "interior" and first["index"] == 1 and "search_seconds" not in first
    assert [p["name"] for p in plans if p["kind"] == "exterior"] == [f"ext_{i}" for i in range(1, 7)]
    assert next(p["view"] for p in plans if p["name"] == "ext_1") == "corner"
    assert len(C.replay_cameras(manifest, kinds=("interior",))["plans"]) == 35
    assert {p["level_id"] for p in C.replay_cameras(manifest, level_id="L0")["plans"] if p["kind"] == "interior"} == {"L0"}
    assert C.replayed_rooms(plans) == {c["room_id"] for c in manifest["cameras"] if c["room_id"]}
    # Records without a position, a lens or a target / rotation are dropped with the reason; a rotation-only
    # record is kept; defaults fill the sensor, resolution and shift.
    bad = {"cameras": [{"name": "a"}, {"name": "b", "position": [0, 0, 1.25], "lens_mm": 18},
                       {"name": "c", "position": [0, 0, 1.25], "lens_mm": 18, "rotation_euler_deg": [90, 0, 30],
                        "room_id": "r", "level_id": "L0", "kind": "interior"},
                       {"name": "ext_9", "position": [20, 20, 5], "target": [0, 0, 2], "lens_mm": 26}]}
    out = C.replay_cameras(bad)
    assert [d["name"] for d in out["dropped"]] == ["a", "b"] and [p["name"] for p in out["plans"]] == ["c", "ext_9"]
    c = out["plans"][0]
    assert "target" not in c and c["rotation_euler_deg"] == [90.0, 0.0, 30.0] and c["sensor_mm"] == 36.0
    assert c["resolution"] == [1920, 1080] and c["shift_x"] == 0.0 and c["index"] == 1
    assert out["plans"][1]["kind"] == "exterior" and out["plans"][1]["index"] == 9
    assert C.replay_cameras({})["plans"] == [] and C.replay_cameras({"cameras": "x"})["plans"] == []


def test_build_takes_the_camera_file_into_the_fingerprint(tmp_path, monkeypatch):
    monkeypatch.delenv(B.CAMERAS_FROM_ENV, raising=False)
    monkeypatch.delenv(B.CAMERAS_EXTRA_ENV, raising=False)
    monkeypatch.delenv(L.LIGHT_VARIANT_ENV, raising=False)
    ns = B.parse_args(["--building", "b", "--out", "o", "--cameras-from", "x.json", "--cameras-extra"])
    assert ns.cameras_from == "x.json" and ns.cameras_extra
    assert B.parse_args(["--building", "b", "--out", "o"]).cameras_from is None
    assert B.cameras_from_spec(None, "real02", env={B.CAMERAS_FROM_ENV: "results/renders/{name}/scene_manifest.json"}) == \
        "results/renders/real02/scene_manifest.json"
    assert B.cameras_from_spec("given.json", "real02", env={B.CAMERAS_FROM_ENV: "env.json"}) == "given.json"
    assert B.cameras_from_spec(None, "real02", env={}) is None and B.cameras_from_spec("", None, env={}) is None
    assert B.cameras_extra_flag(None, env={B.CAMERAS_EXTRA_ENV: "yes"}) and not B.cameras_extra_flag(None, env={})
    rec = B.camera_file_record(str(REAL02))
    assert rec["cameras"] == 41 and len(rec["sha256"]) == 64 and rec["camera_policy"] == "search"
    assert B.camera_file_record(str(tmp_path / "none.json")) == {"path": str(tmp_path / "none.json"), "missing": True}
    assert B.camera_file_record(None) is None
    building = ROOT / "results" / "furniture" / "real02" / "building_final.json"
    plain = B.fingerprint_args(str(building), brief={})
    assert plain["cameras_from"] is None and plain["cameras_extra"] is False and plain["light_variant"] is None
    with_file = B.fingerprint_args(str(building), brief={}, cameras_from=str(REAL02))
    assert with_file["cameras_from"]["sha256"] == rec["sha256"] and with_file["cameras_from"]["path"] == str(REAL02)
    # The environment stands in for the flag (the orchestrated run), {name} = the project id of the building.
    monkeypatch.setenv(B.CAMERAS_FROM_ENV, "results/renders/{name}/scene_manifest.json")
    monkeypatch.setenv(B.CAMERAS_EXTRA_ENV, "1")
    from_env = B.fingerprint_args(str(building), brief={})
    assert from_env["cameras_from"]["path"] == "results/renders/real02/scene_manifest.json" and from_env["cameras_extra"]
    assert from_env["cameras_from"]["sha256"] == rec["sha256"]
    # A changed camera file is another fingerprint; another light variant too.
    other = tmp_path / "cams.json"
    other.write_text(json.dumps({"cameras": [{"name": "cam_x_1", "position": [1, 1, 1.25], "target": [2, 1, 1.25],
                                              "lens_mm": 18, "room_id": "r", "level_id": "L0"}]}))
    assert B.fingerprint_args(str(building), brief={}, cameras_from=str(other))["cameras_from"]["sha256"] != rec["sha256"]
    monkeypatch.setenv(L.LIGHT_VARIANT_ENV, "sun300")
    assert B.fingerprint_args(str(building), brief={})["light_variant"] == "sun300"
    # The manifest's summary of the replay.
    replay = C.replay_cameras(json.loads(REAL02.read_text(encoding="utf-8")))
    plans = replay["plans"] + [{"name": "cam_r_L1_new_1", "source": "searched"}]
    summary = B.cameras_from_summary(rec, replay, plans, False)
    assert (summary["replayed"], summary["searched"], summary["extra"]) == (41, 1, False) and "reason" not in summary
    missing = B.cameras_from_summary({"path": "x", "missing": True}, {"plans": [], "dropped": []}, plans[-1:], False)
    assert "does not exist" in missing["reason"]
    empty = B.cameras_from_summary({"path": "x", "cameras": 0}, {"plans": [], "dropped": []}, plans[-1:], True)
    assert "no camera records" in empty["reason"] and empty["extra"] is True
    assert B.EXTRA_CAMERA_SUFFIX == "_s"


# --------------------------------------------------------------------------
# prepare_m13, the fixed views, the job script, the pass-through
# --------------------------------------------------------------------------

def test_the_fixed_views_exist_in_the_committed_baselines():
    for project, path in (("real02", REAL02), ("real03", REAL03)):
        names = {c["name"] for c in json.loads(path.read_text(encoding="utf-8"))["cameras"]}
        views = AB.m13_views(project)
        assert len(views) == 8 and len(set(views)) == 8 and set(views) <= names
        types = [v["room_type"] for v in AB.M13_AB_VIEWS[project]]
        assert {"living", "bedroom", "bathroom", "hall"} <= set(types)
        evs = [v["m11_ev"] for v in AB.M13_AB_VIEWS[project]]
        assert max(evs) >= 7.0 and min(evs) <= 0.0           # a dark daylight room and a lamp-lit room in every set
    assert "kitchen" in {v["room_type"] for v in AB.M13_AB_VIEWS["real02"]}
    assert AB.m13_views("real04") == [] and AB.M13_AB_VARIANTS == L.LIGHT_VARIANTS
    assert AB.M13_BASELINE_COMMITS["real02"] == AB.M13_BASELINE_COMMITS["real03"] == "93aff07ff7ac6c2bf9c1c5c1d33298398fce9bc5"
    assert AB.M13_BASELINE_COMMITS["real04"].startswith("eddde01")


def test_prepare_m13_from_a_directory(tmp_path):
    src = tmp_path / "baseline"
    src.mkdir()
    scene = {"cameras": [{"name": "cam_r_L0_a_1", "position": [1, 1, 1.25], "target": [2, 1, 1.25], "lens_mm": 18,
                          "room_id": "r_L0_a", "level_id": "L0", "kind": "interior"},
                         {"name": "cam_r_L0_a_2", "position": [1, 2, 1.25], "target": [2, 2, 1.25], "lens_mm": 16,
                          "room_id": "r_L0_a", "level_id": "L0", "kind": "interior"}],
             "style_profile": {"lighting": {"mood": "warm daylight"}, "walls": {"material": "paint"}},
             "build_fingerprint": "f" * 64}
    (src / "scene_manifest.json").write_text(json.dumps(scene))
    (src / "render_manifest.json").write_text(json.dumps({"renders": []}))
    (src / "building_final.json").write_text(json.dumps({"project": {"id": "p"}}))
    (src / "cam_r_L0_a_1_preview.jpg").write_bytes(b"jpg")
    info = AB.prepare_m13("p", tmp_path / "out", str(src))
    out = tmp_path / "out" / "ab" / "m13"
    assert info["cameras"] == 2 and info["camera_records"] and info["previews"] == 1 and info["missing"] == ["cam_r_L0_a_2"]
    assert info["reason"] is None and info["commit"] is None and info["source"] == str(src)
    assert sorted(info["files"]) == ["building_final.json", "render_manifest.json", "scene_manifest.json", "style.json"]
    assert json.loads((out / "style.json").read_text())["walls"] == {"material": "paint"}
    assert (out / "cam_r_L0_a_1_preview.jpg").read_bytes() == b"jpg" and (out / "building_final.json").is_file()
    assert info["views"] == [] and info["views_missing"] == []
    # A baseline without camera records (real04's case): an empty camera set with the reason, the building kept.
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "building_final.json").write_text("{}")
    info = AB.prepare_m13("real04", tmp_path / "out4", str(empty))
    assert info["cameras"] == 0 and info["camera_records"] is False and "real04" in info["reason"]
    assert info["files"] == ["building_final.json"] and info["views_missing"] == []
    # From git (a show callable): the baseline commit of the project, the previews per camera.
    files = {"results/renders/p/scene_manifest.json": json.dumps(scene).encode(),
             "results/renders/p/render_manifest.json": b"{}", "results/furniture/p/building_final.json": b"{}",
             "results/renders/p/cam_r_L0_a_1_preview.jpg": b"a", "results/renders/p/cam_r_L0_a_2_preview.jpg": b"b"}

    def show(commit, path):
        assert commit == "abc"
        if path not in files:
            raise FileNotFoundError(path)
        return files[path]

    info = AB.prepare_m13("p", tmp_path / "git", "abc", show=show)
    assert info["cameras"] == 2 and info["previews"] == 2 and info["commit"] == "abc" and info["source"] == "git abc"
    with pytest.raises(ValueError, match="no baseline commit"):
        AB.prepare_m13("nope", tmp_path / "x", show=show)
    # The real baseline from the working tree (equal to commit 93aff07): the 8 views are all there.
    info = AB.prepare_m13("real02", tmp_path / "real02", str(ROOT / "results" / "renders" / "real02"))
    assert info["cameras"] == 41 and info["previews"] == 41 and info["views_missing"] == []


def test_lever_sheets_and_summary(tmp_path):
    from PIL import Image

    res = tmp_path / "ab_m13"
    for v in ("base", "sun300"):
        d = res / v / "real02"
        d.mkdir(parents=True)
        renders = []
        for cam in AB.m13_views("real02"):
            renders.append({"camera": cam, "seconds": 4.5, "samples": 128, "preview": f"{cam}_preview.jpg", "vram_mib": 3000,
                            "exposure": {"ev": 3.0, "ev_raw": 6.1, "at_limit": True, "incident_p50": 0.013,
                                         "wb_temperature": 5300.0, "wb_mode": "project",
                                         "lighting_dark": R.lighting_dark_entry(cam, "r", 6.1, 3.0, (-2, 3), 0.013)}})
            Image.new("RGB", (64, 36), (100, 90, 80)).save(d / f"{cam}_preview.jpg")
        (d / "render_manifest.json").write_text(json.dumps({"renders": renders, "light_variant": {"build": v},
                                                            "exposure_limits": [-2, 3]}))
        (d / "vram.json").write_text(json.dumps({"peak_mib": 4100}))
    summary = AB.lever_summary(res, ("real02",), ("base", "sun300", "rig"))
    rows = summary["rows"]
    assert len(rows) == 17 and sum(1 for r in rows if r["status"] == "rendered") == 16
    assert all(r["lighting_dark"] == "critical" and r["vram_peak_mib"] == 4100 for r in rows if r["status"] == "rendered")
    assert (res / "summary.json").is_file() and "| real02 | base | cam_r_L-1_salon_1 | 4.5 | 3.0 | 6.1 | critical |" in \
        (res / "summary.md").read_text()
    sheets = AB.lever_sheets(res, "real02", ("base", "sun300", "rig"))
    assert len(sheets) == 8 and all(s.is_file() for s in sheets)
    with Image.open(sheets[0]) as im:
        assert im.width > 3 * 600 and im.height > 36           # three tiles side by side, labels under them


def test_levers_ab_job_script():
    script = ROOT / "scripts" / "jobs" / "levers_ab.sh"
    subprocess.run(["bash", "-n", str(script)], check=True)
    text = script.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text
    assert "/workspace/logs" in text.replace("$WS/logs", "/workspace/logs") and "LOGS=$WS/logs" in text
    for v in L.LIGHT_VARIANTS:
        assert v in text, v
    assert "WENART_LIGHT_VARIANT" in text and "WENART_CAMERAS_FROM" in text and "WENART_DEADLINE" in text
    assert "m13-prepare" in text and "m13-sheets" in text and "m13-summary" in text
    assert "--white-balance project" in text and 'AB_SAMPLES:-128' in text
    assert "nvidia-smi --query-gpu=memory.used" in text and "vram.json" in text
    assert "seconds_left" in text and "pod stop" not in text          # the job never stops the pod itself
    assert "trap 'on_exit' EXIT" in text and "copy_results" in text
    assert "tests/gpu/test_m13_light.py" in text


def test_stages_and_plan_pass_the_camera_file_through():
    assert S.CAMERAS_FROM_ENV == B.CAMERAS_FROM_ENV == "WENART_CAMERAS_FROM"
    assert S.cameras_from_env("real03", {"WENART_CAMERAS_FROM": "r/{name}/s.json"}) == "r/real03/s.json"
    rec = PL.camera_records_for("real02", ROOT)
    assert rec["cameras"] == 41 and rec["path"].endswith("results/renders/real02/scene_manifest.json")
    assert rec["source"] == "committed baseline run" and "reason" not in rec
    rec4 = PL.camera_records_for("real04", ROOT)
    assert rec4["cameras"] == 0 and "camera search runs" in rec4["reason"]
    env = PL.camera_records_for("real04", ROOT, env={"WENART_CAMERAS_FROM": str(REAL03)})
    assert env["cameras"] == 83 and env["source"] == "env WENART_CAMERAS_FROM"
    assert S.WHITE_BALANCE == "project" and "project" in R.WB_MODES


def test_the_cli_forwards_the_camera_flags_to_the_build_and_its_reuse_fingerprint(tmp_path, monkeypatch):
    """Round 2 (K8): ``wenart.blender.cli build --cameras-from F [--cameras-extra]`` passes the flags on to
    build.py (stages.build emits them) and takes them into the ``--reuse`` fingerprint exactly as build.py
    computes it; without the flags the environment path stays (both read WENART_CAMERAS_FROM)."""
    from wenart.blender import cli as CLI
    monkeypatch.delenv(B.CAMERAS_FROM_ENV, raising=False)
    monkeypatch.delenv(B.CAMERAS_EXTRA_ENV, raising=False)
    monkeypatch.delenv(L.LIGHT_VARIANT_ENV, raising=False)
    building = ROOT / "results" / "furniture" / "real02" / "building_final.json"
    seen = []
    monkeypatch.setattr(CLI, "run_blender", lambda script, args, **kw: seen.append(list(args)))
    out = tmp_path / "scene"
    CLI.build(str(building), str(out), cameras_from=str(REAL02), cameras_extra=True)
    assert seen[-1][seen[-1].index("--cameras-from") + 1] == str(REAL02) and "--cameras-extra" in seen[-1]
    CLI.build(str(building), str(out))
    assert "--cameras-from" not in seen[-1] and "--cameras-extra" not in seen[-1]
    # The reuse fingerprint with the flags = build.py's fingerprint_args with the same values.
    fp_flags = CLI.build_fingerprint(str(building), cameras_from=str(REAL02), cameras_extra=True)
    brief_args = B.brief_args(json.loads(building.read_text()), None)
    expect = B.build_fingerprint(B.fingerprint_args(str(building), None, None, None, False, None, False, False, False,
                                                    "m5", None, "base", brief_args, cameras_from=str(REAL02),
                                                    cameras_extra=True))
    assert fp_flags == expect and fp_flags != CLI.build_fingerprint(str(building))
    # The environment gives the same fingerprint as the flags (build.py resolves the file either way).
    monkeypatch.setenv(B.CAMERAS_FROM_ENV, str(REAL02))
    monkeypatch.setenv(B.CAMERAS_EXTRA_ENV, "1")
    assert CLI.build_fingerprint(str(building)) == fp_flags
    # The subcommand parses the flags.
    monkeypatch.setattr(CLI, "build", lambda *a, **kw: seen.append(kw) or tmp_path / "m.json")
    assert CLI.main(["build", "--building", "b", "--out", "o", "--cameras-from", "x.json", "--cameras-extra"]) == 0
    assert seen[-1]["cameras_from"] == "x.json" and seen[-1]["cameras_extra"] is True
    assert CLI.main(["build", "--building", "b", "--out", "o"]) == 0 and seen[-1]["cameras_from"] is None
