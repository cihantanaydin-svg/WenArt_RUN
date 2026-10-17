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

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8; the ``test_fixround_p3_*`` tests, each failing on the
P3 code 3724033 / 5bd7bab): the view white point mixed from the project's daylight and the rig by the view's rig
share; the roof terraces (``balcony``) under the exterior world and the cameras marked with their room type; the
window pull to 10 stops with the pane target; the sky pull of the views under the exterior sky; a rig replaces the
fill light only with a ceiling fixture; the hall and stair fixtures carry bulbs for 450 lm per m².

Fix round part 2 (17 Oct 2026, the review of part 1; the ``test_fixround_part2_*`` tests, each failing on 62b2b3c):
the open-air views take the exterior clip end (``render.view_clip_end`` / ``set_view_clip``), and CPU replays of the
GPU checks of tests/gpu/test_render.py on hand-made manifests: the white-point pins that do not read the view's own
share, the sky pull that must fire, the named windowless bedrooms that keep their fill light, the clip and the dark
band under the horizon of the open-air views. The Blender-bound twins (a windowless bedroom's build, an open-air view
rendered with the exterior clip) are in tests/test_look_m6.py.

Fix round part 3 (17 Oct 2026, the review of part 2; the ``test_fixround_part3_*`` tests, each failing on eb80db2):
the sky pull's mask counts the haze shell as sky (``render.haze_sky``: the haze's reserved pass index
``site.HAZE_PASS_INDEX`` and no normal behind it), so the pull is blended on the whole sky at full weight and never on
the far ground behind the shell; the reserved index stays out of the index map and the pass index tables; the GPU sky
check holds the blended sky to the saturation floor (with a feather allowance) and pins the mask's coherence
(``full_weight_share``).
"""
from __future__ import annotations

import json
import math
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
    # Round 3 (docs/milestone13.md §14.3, pod P1 of 15 Oct 2026): the manual's clear-sky sun; the per-mood ratio
    # stays against the warm-daylight 3.0, so a style's sun_strength scales the same way.
    assert isinstance(L.SUN_STRENGTH_WM2, float) and L.SUN_STRENGTH_WM2 == 1000.0
    assert L.SUN_REFERENCE_MOOD_WM2 == 3.0 and L.SUN_STRENGTH_M11_WM2 == 3.0
    assert L.LIGHT_VARIANTS == ("m11", "base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
    assert L.SUN_VARIANT_WM2 == {"sun100": 100.0, "sun300": 300.0, "sun1000": 1000.0}
    # Production (no variant): the constant and every lever on (the lead's P1 decisions: EV cap, rig, shell).
    prod = L.light_levers(env={})
    assert prod["variant"] is None and prod["sun_wm2"] == 1000.0 and prod["source"] == "default"
    assert prod["ev_cap"] and prod["rig"] and prod["shell"]
    assert L.LEVER_DEFAULTS == {"ev_cap": True, "rig": True, "shell": True}
    assert L.M11_LEVERS == {"ev_cap": False, "rig": False, "shell": False}
    # ``base`` = production under its name; ``m11`` = the Milestone 11 look (sun 3.0, no cap, no rig, no shell).
    base = L.light_levers("base")
    assert (base["sun_wm2"], base["ev_cap"], base["rig"], base["shell"]) == (1000.0, True, True, True)
    assert base["variant"] == "base" and base["source"] == "arg"
    m11 = L.light_levers("m11")
    assert (m11["sun_wm2"], m11["ev_cap"], m11["rig"], m11["shell"]) == (3.0, False, False, False)
    # Every single lever starts from the Milestone 11 look (its P1 meaning, so the P1 sheets still compare).
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
    assert L.light_levers("m11,rig")["rig"] and not L.light_levers("m11,rig")["shell"]
    # Names combined with ``base`` start from production and only turn levers on (never off).
    with_sun = L.light_levers("base,sun300")
    assert (with_sun["sun_wm2"], with_sun["ev_cap"], with_sun["rig"], with_sun["shell"]) == (300.0, True, True, True)
    assert L.parse_light_variant("") == [] and L.parse_light_variant(None) == []
    with pytest.raises(ValueError, match="unknown variant"):
        L.parse_light_variant("sun200")
    with pytest.raises(ValueError, match="more than one sun"):
        L.parse_light_variant("sun100,sun300")
    with pytest.raises(ValueError, match="exclude each other"):
        L.parse_light_variant("m11,base")
    # The style's sun_strength is a factor against warm daylight (3.0): overcast keeps a tenth, night none.
    assert L.sun_strength_wm2({"sun_strength": 3.0}, L.light_levers("sun300")) == (300.0, 1.0)
    assert L.sun_strength_wm2(V.LIGHTING["overcast"], L.light_levers("sun1000")) == (100.0, 0.1)
    assert L.sun_strength_wm2(V.LIGHTING["night"], L.light_levers("sun1000")) == (0.0, 0.0)
    assert L.sun_strength_wm2({}, L.light_levers(env={})) == (1000.0, 1.0)
    assert L.sun_strength_wm2(V.LIGHTING["overcast"], L.light_levers(env={})) == (100.0, 0.1)


def test_fill_light_rule_at_1000_wm2():
    """Round 3 check of the dim-room rule at the production sun (docs/milestone13.md §14.3 item 1): the fill light
    never dominates a sunlit room (any window counts as daylight at scale 333) and still helps a sunless one."""
    small = [{"type": "window", "width": 0.6, "height": 1.2, "sill_height": 0.9}]
    prod = L.light_levers(env={})
    assert L.sun_strength_wm2({}, prod)[0] / L.SUN_REFERENCE_MOOD_WM2 == pytest.approx(1000.0 / 3.0)
    assert L.fill_light_reason(small, 0.06, sun_wm2=1000.0) is None                 # the P1 dim bedroom: sunlit now
    assert L.fill_light_reason(small, 0.0003, sun_wm2=1000.0) is None                # even a slit: 0.1 >= 0.08
    reason = L.fill_light_reason(small, 0.0002, sun_wm2=1000.0)
    assert reason is not None and "x sun 1000/3 W/m2" in reason                     # 0.067 < 0.08: fill
    assert L.fill_light_reason([], None, sun_wm2=1000.0) == "room has no window"      # sunless: the fill or the rig
    assert L.fill_light_reason(small, 0.06, sun_wm2=3.0) is not None                 # the m11 look keeps the M6 rule


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
    assert R.exposure_limits_for(L.light_levers("m11")) == (-2.0, 8.0)          # the Milestone 11 look
    assert R.exposure_limits_for(L.light_levers("base")) == (-2.0, 3.0)         # round 3: base = production
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
    # Round 3 (§14.3): the white point is metered on daylight: a camera in a room with a window portal first (P1
    # metered real02 on the windowless, rig-lit cam_r_L-1_banyo_1: 3,422 K), then the other interior cameras,
    # then the exterior ones; up to WB_METER_MAX_CAMERAS are tried.
    cams = [("ext_1", "exterior", None), ("cam_r_L-1_banyo_1", "interior", "r_L-1_banyo"),
            ("cam_r_L-1_salon_1", "interior", "r_L-1_salon"), ("cam_r_L-1_mutfak_1", "interior", "r_L-1_mutfak")]
    daylight = {"r_L-1_salon", "r_L-1_mutfak"}
    assert R.wb_camera_order(cams, daylight) == ["cam_r_L-1_mutfak_1", "cam_r_L-1_salon_1", "cam_r_L-1_banyo_1", "ext_1"]
    assert R.project_wb_camera(cams, daylight) == "cam_r_L-1_mutfak_1"
    assert R.project_wb_camera(cams) == "cam_r_L-1_banyo_1"                   # no daylight table: name order
    assert R.wb_camera_order([("ext_1", "exterior", None)], daylight) == ["ext_1"]
    assert R.WB_METER_MAX_CAMERAS == 3
    # Round-3 review (16 Oct 2026): the first windowed room in name order may get skylight only (synthetic-01's
    # bath metered 9,068 K under the 1000 W/m2 sun and cast the sunlit living room orange), so a room whose window
    # faces the sun comes first and the metered daylight candidate with the most incident light wins.
    assert R.wb_camera_order(cams, daylight, {"r_L-1_salon"}) == \
        ["cam_r_L-1_salon_1", "cam_r_L-1_mutfak_1", "cam_r_L-1_banyo_1", "ext_1"]
    assert R.project_wb_camera(cams, daylight, {"r_L-1_salon", "r_L-1_banyo"}) == "cam_r_L-1_salon_1"  # a sunlit
    # room without a window portal is no daylight room (the portal table is the evidence of the window)
    travel = L.sun_direction(35.0, 210.0)
    travel = tuple(-c for c in travel)                       # from the sun into the scene (a lamp's -Z axis)
    portals = [("r_s", (0.5, 0.866, 0.0)), ("r_n", (-0.5, -0.866, 0.0)), ("r_e", (-1.0, 0.0, 0.0)),
               ("r_w", (0.866, -0.5, 0.0)), (None, (0.5, 0.866, 0.0))]
    # the sun at azimuth 210 (south-south-west) shines towards +Y / +X: the south window's inward axis (+Y, +X)
    # faces it, the north one (-Y) does not, the east one (-X) is in shadow, the west one at 90 degrees is grazing
    assert R.sunlit_rooms_from(portals, travel) == {"r_s"}
    assert R.sunlit_rooms_from(portals, None) == set() and R.sunlit_rooms_from(portals, (0.0, 0.0, 0.0)) == set()
    assert R.sunlit_rooms_from([("r_w", (0.866, -0.5, 0.0))], travel, min_dot=-0.1) == {"r_w"}
    assert 0.0 < R.SUNLIT_DOT_MIN < 0.2
    rows = [{"camera": "cam_b", "daylight": True, "incident_p50": 0.02, "whitepoint": [1.2, 1.0, 0.8]},
            {"camera": "cam_s", "daylight": True, "incident_p50": 1.6, "whitepoint": [1.1, 1.0, 0.9]},
            {"camera": "cam_w", "daylight": False, "incident_p50": 3.0, "whitepoint": [1.0, 1.0, 1.0]},
            {"camera": "cam_x", "daylight": True, "incident_p50": 9.0, "whitepoint": None}]
    assert R.pick_wb_candidate(rows)["camera"] == "cam_s"                   # the sun, not the sky-lit window
    assert R.pick_wb_candidate(rows[2:])["camera"] == "cam_w"               # no daylight light: the windowless one
    assert R.pick_wb_candidate([rows[3]]) is None and R.pick_wb_candidate([]) is None
    tie = [dict(rows[1], camera="cam_t"), rows[1]]
    assert R.pick_wb_candidate(tie)["camera"] == "cam_s"                    # name order on a tie
    # A previous manifest's record is kept only when it was metered on daylight or set from kelvin.
    assert not R.previous_whitepoint_usable({"whitepoint": [1.1, 1.0, 0.8], "source": "metered on cam_r_L-1_banyo_1"})
    assert R.previous_whitepoint_usable({"whitepoint": [1.1, 1.0, 0.8], "source": "metered on c", "daylight_only": True})
    assert R.previous_whitepoint_usable({"whitepoint": [1.1, 1.0, 0.8], "source": "kelvin:5300", "kelvin": 5300.0})
    assert not R.previous_whitepoint_usable({"whitepoint": None, "daylight_only": True}) and not R.previous_whitepoint_usable(None)
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
    # fix round after P3 (16-17 Oct 2026): the view white point, the open-air world, the sky and window pulls -> m13.2
    assert R.RENDER_CODE_VERSION == "m13.2"
    # The sun lamp hides under the exterior world with a sun disc for every ray only (the P1 world); round 3:
    # with the disc for camera rays only the lamp stays, it is the one direct sun outdoors.
    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_exterior_sun_disc": True}
    assert R.sun_hidden_for(props, "exterior") and not R.sun_hidden_for(props, "interior")
    assert not R.sun_hidden_for(dict(props, wenart_world_exterior_sun_disc=False), "exterior")
    assert not R.sun_hidden_for(dict(props, wenart_world_exterior_disc_camera_only=True), "exterior")
    assert not R.sun_hidden_for({}, "exterior")
    assert set(R.WORLD_PROPS) == {"wenart_world_exterior", "wenart_world_interior", "wenart_world_exterior_sun_disc",
                                  "wenart_world_exterior_disc_camera_only"}


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
            assert slot in ("front", "ceramic", "tile", "plaster")     # fix round after P3: the front is a paint
            continue
        assert asset in known, (slot, asset)                       # an id of the style vocabulary, never invented
        assert checked[asset]["exists"] is True and checked[asset]["licence"] == "CC0", (slot, asset)
        assert checked[asset]["source"] in M.CC0_SOURCES
    # fix round after P3 (16-17 Oct 2026): the worktop is ambientCG Marble012 (marble_01 reads as tiles) and the
    # painted front has no photo set (white_planks_clean showed plank joints every 10 cm); it is a paint finish
    assert M.shell_assets()["ceiling"] == "white_plaster_02" and M.shell_assets()["worktop"] == "Marble012"
    assert M.shell_assets()["front"] is None and M.shell_slot_spec("front", {})["paint"]
    assert M.shell_assets()["metal"] == "Metal032"
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
    # The library takes the levers: shell on under the shell / all variants and in production (round 3: base =
    # production, LEVER_DEFAULTS shell on), off under the Milestone 11 look.
    assert M.MaterialLibrary({}, None, levers=L.light_levers("m11")).shell_on is False
    assert M.MaterialLibrary({}, None, levers=L.light_levers("base")).shell_on is True
    assert M.MaterialLibrary({}, None, levers=L.light_levers("shell")).shell_on is True
    assert M.MaterialLibrary({}, None, levers=L.light_levers("all")).shell_on is True
    assert M.MaterialLibrary({}, None, levers=L.light_levers(env={})).shell_on is True is L.LEVER_DEFAULTS["shell"]
    assert M.MaterialLibrary({}, None, levers={"shell": True}).shell_on is True
    # The ceiling slot is the one slot a slug reaches without an asset, so its name carries the slot (no .001 twin
    # of the walls' plaster_white__white_plaster_02 under the shell lever).
    assert M.material_name("plaster_white", "white_plaster_02", slot="plaster") == "plaster_white__white_plaster_02"
    assert M.material_name("plaster_white", "white_plaster_02", slot="ceiling") == "plaster_white__white_plaster_02__ceiling"
    assert M.material_name("plaster_white", None, slot="ceiling") == "plaster_white__ceiling"
    assert M.material_name("plaster_white", None, "sage", slot="ceiling") == "plaster_white__ceiling__sage"
    assert M.material_name("tiles_light", None, None, "ab12", unverified=True, slot="tile") == "tiles_light__pab12__unverified"
    assert M.material_name("wood_oak_light", "WoodFloor051") == "wood_oak_light__WoodFloor051"


def test_exterior_world_record_with_the_sun_disc():
    lighting = {"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 45.0}
    old = M.exterior_world(lighting)                                      # the Milestone 11 record, unchanged
    assert old["sun_disc"] is False and old["direct_sun"] == "lamp" and old["strength"] == 0.5
    # Round 3 (§14.3): the disc is for camera rays only (a Light Path 'Is Camera Ray' mix of the sky with and
    # without the disc), so the lamp at SUN_STRENGTH_WM2 is the one direct sun outdoors and the facades get shadows.
    rec = M.exterior_world(lighting, sun_disc=True, sun_elevation_deg=40.0, sun_azimuth_deg=100.0, sun_wm2=300.0)
    assert rec["sun_disc"] is True and rec["direct_sun"] == "lamp" and rec["sun_disc_camera_only"] is True
    assert rec["world_mix"]["node"] == "ShaderNodeMixShader" and "Is Camera Ray" in rec["world_mix"]["factor"]
    assert "only the camera sees" in rec["reason"]
    assert (rec["sun_elevation_deg"], rec["sun_azimuth_deg"]) == (40.0, 100.0)    # the arguments win
    # The world's Background Strength scales the disc too (T5 review, 15 Oct 2026). Round 4: the strength is the one
    # whose own sun equals the 300 W/m² lamp at 40 degrees (300 / (1000 x 0.1331) = 2.254), and the intensity is
    # divided by it, so the disc's image brightness stays strength x intensity = 300 / 1000 (the P1 disc).
    assert rec["strength"] == pytest.approx(300.0 / (1000.0 * 0.1331), abs=1e-4)
    assert rec["sun_disc_world_strength"] == rec["strength"]
    assert rec["sun_intensity"] == pytest.approx(0.1331, abs=1e-4) and rec["sun_size_deg"] == 0.545
    assert rec["strength"] * rec["sun_intensity"] == pytest.approx(0.3, abs=1e-5)
    assert rec["sun_disc_reference_wm2"] == 1000.0
    prod = M.exterior_world(lighting, sun_disc=True, sun_wm2=L.SUN_STRENGTH_WM2)
    assert prod["sun_intensity"] == pytest.approx(0.1297) and prod["direct_sun"] == "lamp"
    assert prod["strength"] * prod["sun_intensity"] == pytest.approx(1.0, abs=1e-5)  # the P1 disc's 0.5 x 2.0
    # The P1 world (the disc for every ray, the lamp hidden under it) stays selectable for the measurement.
    p1 = M.exterior_world(lighting, sun_disc=True, sun_wm2=300.0, disc_camera_only=False)
    assert p1["direct_sun"] == "sky disc" and p1["sun_disc_camera_only"] is False and "world_mix" not in p1
    assert "does not double the sun" in p1["reason"]
    assert M.sky_sun_intensity(None) == 1.0 and M.sky_sun_intensity(1000.0) == 1.0 and M.sky_sun_intensity(3.0) == 0.003
    assert M.sky_sun_intensity(300.0, world_strength=0.5) == 0.6 and M.sky_sun_intensity(300.0, 1000.0, 1.0) == 0.3
    assert M.sky_sun_intensity(2e6) == 1000.0                                # the node's range
    # The sky's sun where the lamp is: ShaderNodeTexSky.sun_rotation is the compass azimuth itself (measured on
    # bpy 5.2.2, round 3: rotation 90 degrees puts the sun at +X / east, 180 at -Y, 270 at -X). The Milestone
    # 3-11 formula 90 - azimuth matched the lamp only at 45 degrees (real02) and put real03's sun (210) at 240.
    assert M.sky_sun_rotation_rad(210.0) == pytest.approx(math.radians(210.0))
    assert M.sky_sun_rotation_rad(45.0) == pytest.approx(math.radians(45.0))
    assert M.sky_sun_rotation_rad(0.0) == 0.0 and M.sky_sun_rotation_rad(90.0) == pytest.approx(math.pi / 2)


def test_round4_the_exterior_sky_is_the_pair_of_the_sun_lamp():
    """Round 4 (docs/milestone13.md §14.8, the P3 pre-flight: the exterior sky world at 0.5 was about 4 stops too dark
    against the 1000 W/m² lamp, ext_7's sky band 14/255 at the metered EV -7.67): the sky's Background Strength is
    the one whose own sun equals the lamp (the measured pair ``SKY_SUN_TABLE``, bpy 5.2.2), the disc keeps its
    image brightness, and the pair's horizontal diffuse-to-direct ratio lies in the clear-sky range (pvlib 0.13.1
    Bird / Ineichen-Perez: 0.149-0.212 at 35 degrees). Fails on the round-3 code (strength 0.5, no calibration)."""
    lighting = {"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 45.0, "sun_strength": 3.0}
    rec = M.exterior_world(lighting, sun_disc=True, sun_wm2=L.SUN_STRENGTH_WM2)
    # 1000 / (1000 x 0.1297): x15.4 the Milestone 11 0.5 (the pre-flight's x15.5 gave a blue sky band)
    assert rec["strength"] == pytest.approx(1000.0 / 129.7, abs=1e-4) and 15.0 < rec["strength"] / 0.5 < 16.0
    cal = rec["sky_calibration"]
    assert cal["rule"] == "sun pair" and cal["sky_sun_wm2"] == pytest.approx(129.7) and cal["mood_balance"] == 1.0
    assert cal["strength"] * cal["sky_sun_wm2"] == pytest.approx(L.SUN_STRENGTH_WM2, rel=1e-5)   # its sun = the lamp
    # the P1 measurement SUN_DISC_RATIO 0.129 (tests/gpu/test_m13_light.py) is the table's 35-degree row
    assert M.sky_pair_ratios(35.0)[0] == pytest.approx(0.129, abs=0.001)
    # the visible disc keeps its round-3 image brightness: strength x intensity = lamp / 1000 = 0.5 x 2.0
    assert rec["strength"] * rec["sun_intensity"] == pytest.approx(1.0, abs=1e-5)
    # the pair's own clear-sky ratio on a horizontal plane: 0.0124 / (0.1297 x sin 35) = 0.166
    assert cal["pair_diffuse_to_direct"] == pytest.approx(0.01238 / (0.1297 * math.sin(math.radians(35.0))), abs=1e-4)
    assert 0.149 <= cal["pair_diffuse_to_direct"] <= 0.212 and cal["pair_in_clear_sky_range"] is True
    assert M.CLEAR_SKY_DIFFUSE_RANGE == (0.10, 0.25) and cal["diffuse_to_direct"] == cal["pair_diffuse_to_direct"]
    # every elevation from 25 degrees up is a clear sky; a low sun has more diffuse light (as the clear-sky models)
    for e in (25.0, 30.0, 35.0, 45.0, 55.0, 65.0, 75.0, 85.0):
        c = M.exterior_sky_strength(1000.0, e)
        assert c["pair_in_clear_sky_range"] is True, (e, c["pair_diffuse_to_direct"])
    assert M.exterior_sky_strength(1000.0, 12.0)["pair_diffuse_to_direct"] > 0.25
    # pvlib 0.13.1 ``clearsky.bird`` at sea level (precipitable water 1.42 cm, ozone 0.3 cm, AOD380 = AOD500 x
    # (380 / 500) ** -1.3, Kasten-Young relative air mass; computed on CPU, 16 Oct 2026): DHI / (DNI x sin e) at
    # AOD500 0.05 and 0.1. The measured pair lies between them at every elevation from 10 to 85 degrees.
    bird = {10: (0.403, 0.644), 12: (0.351, 0.549), 15: (0.294, 0.448), 20: (0.233, 0.344), 25: (0.194, 0.282),
            30: (0.168, 0.240), 35: (0.149, 0.212), 40: (0.136, 0.190), 45: (0.125, 0.175), 55: (0.111, 0.153),
            65: (0.102, 0.140), 75: (0.097, 0.132), 85: (0.095, 0.129)}
    for e, (clean, typical) in bird.items():
        assert clean <= M.exterior_sky_strength(1000.0, float(e))["pair_diffuse_to_direct"] <= typical, e
    assert M.exterior_sky_strength(1000.0, 12.0)["pair_in_clear_sky_range"] is None
    # the table: elevations rise, the sun brightens with the elevation (less air), read linearly and held at its ends
    els = [r[0] for r in M.SKY_SUN_TABLE]
    assert els == sorted(els) and [r[1] for r in M.SKY_SUN_TABLE] == sorted(r[1] for r in M.SKY_SUN_TABLE)
    assert M.sky_pair_ratios(37.5)[0] == pytest.approx((0.1297 + 0.1331) / 2.0)
    assert M.sky_pair_ratios(0.0) == M.sky_pair_ratios(5.0) and M.sky_pair_ratios(90.0) == M.sky_pair_ratios(85.0)
    # the table was measured with this air: a change of EXTERIOR_SKY needs a new measurement
    assert {k: M.EXTERIOR_SKY[k] for k in M.SKY_TABLE_AIR} == M.SKY_TABLE_AIR
    # the sky follows the lamp (the A/B suns) and the elevation (a lower sun is dimmer through more air)
    assert M.exterior_world(lighting, sun_disc=True, sun_wm2=300.0)["strength"] == pytest.approx(0.3 * rec["strength"],
                                                                                                abs=1e-4)
    low = M.exterior_world(lighting, sun_disc=True, sun_elevation_deg=12.0, sun_wm2=1000.0)
    assert low["strength"] == pytest.approx(1000.0 / (1000.0 * 0.0853), abs=1e-3) and low["strength"] > rec["strength"]
    # moods keep the Milestone 11 balance of sky to sun (MOOD_STRENGTH over the lamp's mood factor): overcast is
    # a sky-dominated light, 14 x its clear pair; without a lamp (a sunless mood, or no lamp given) the M11 0.5
    overcast = {"mood": "overcast", "sun_elevation_deg": 45.0, "sun_strength": 0.3}
    sun, factor = L.sun_strength_wm2(overcast)
    oc = M.exterior_world(overcast, sun_disc=True, sun_wm2=sun)["sky_calibration"]
    assert factor == pytest.approx(0.1) and oc["mood_balance"] == pytest.approx(14.0)
    assert oc["diffuse_to_direct"] == pytest.approx(14.0 * oc["pair_diffuse_to_direct"], abs=1e-3)
    night = M.exterior_world({"mood": "night", "sun_elevation_deg": -10.0, "sun_strength": 0.0}, sun_disc=True,
                             sun_wm2=0.0)
    assert night["sky_calibration"]["rule"] == "m11" and night["strength"] == pytest.approx(0.05 * 0.5)
    assert M.exterior_world(lighting)["sky_calibration"]["rule"] == "m11"


def test_rig_gain_and_the_shade_emission_bound():
    """Round 3 (§14.3 item 3): gain 2.0 (P1: gain 4 lit the real02 kitchen but blew the shades white) and the
    shade's fixed radiance under the AgX Punchy clip at the project EV range -2..+3."""
    assert L.RIG_GAIN == 2.0
    assert L.room_rig("bedroom")[0]["watts_applied"] == pytest.approx(L.watts_for_lumens(470.0) * 2.0)
    assert L.room_rig("kitchen")[1]["watts_applied"] == pytest.approx(L.watts_for_lumens(1600.0) * 2.0)
    # The bound: a scene-linear 32 shows as display 255 (bpy 5.2.2, measured); at the cap +3 (x 8) the shade's
    # brightest channel (the red of 2700 K = 1.0) must stay under it: 32 / 8 = 4.0 W/(m2 sr).
    assert L.SHADE_EV_MAX == R.EXPOSURE_LIMITS[1] == 3.0 and L.SHADE_EMISSION_CLIP == 32.0
    assert L.shade_emission_bound() == pytest.approx(4.0)
    assert L.shade_emission_bound(ev_max=-2.0) == pytest.approx(128.0)
    assert L.shade_emission_bound(ev_max=3.0, channel_max=max(L._blackbody_rgb(2700.0))) == pytest.approx(4.0)
    assert 0.0 < L.SHADE_EMISSION_WM2SR == 2.0 < L.shade_emission_bound()        # one stop of margin at the cap
    assert L.SHADE_EMISSION_WM2SR * 2.0 ** L.SHADE_EV_MAX == pytest.approx(16.0)  # 16 < 32: never pure white
    assert L.SHADE_EMISSION_WM2SR * 2.0 ** -2.0 == pytest.approx(0.5)             # a soft glow at EV -2
    assert L._blackbody_rgb(2700.0)[0] == 1.0 and L._blackbody_rgb(2700.0)[2] < 0.4


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
    # Round 3: the variant names are m11 (the Milestone 11 look) and base (production); a folder that is missing
    # (m11 in a P1 results folder, rig here) is a "not rendered" row and a grey tile, nothing breaks.
    summary = AB.lever_summary(res, ("real02",), ("m11", "base", "sun300", "rig"))
    rows = summary["rows"]
    assert len(rows) == 18 and sum(1 for r in rows if r["status"] == "rendered") == 16
    assert [r["variant"] for r in rows if r["status"] != "rendered"] == ["m11", "rig"]
    assert all(r["lighting_dark"] == "critical" and r["vram_peak_mib"] == 4100 for r in rows if r["status"] == "rendered")
    assert (res / "summary.json").is_file() and "| real02 | base | cam_r_L-1_salon_1 | 4.5 | 3.0 | 6.1 | critical |" in \
        (res / "summary.md").read_text()
    assert "| real02 | m11 | - | not rendered |" in (res / "summary.md").read_text()
    sheets = AB.lever_sheets(res, "real02", ("m11", "base", "sun300", "rig"))
    assert len(sheets) == 8 and all(s.is_file() for s in sheets)
    with Image.open(sheets[0]) as im:
        assert im.width > 4 * 600 and im.height > 36           # four tiles side by side, labels under them
    assert AB.M13_AB_VARIANTS[:2] == ("m11", "base") and AB.M13_AB_VARIANTS == L.LIGHT_VARIANTS


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


# --------------------------------------------------------------------------
# Pre-flight of pod P3 (16 Oct 2026, CPU build and render of P3's real04 inputs with the bpy module)
# --------------------------------------------------------------------------

def test_preflight_p3_the_ev_floor_follows_the_scene_sun():
    """real04 ext_7 under the 1000 W/m² sun: the facades' incident p50 179.63 wants -7.64 EV, the -2 floor (set under
    the 3 W/m² sun of Milestone 11) held the view 5.6 stops too bright (a near white exterior); the sunlit terrace
    (p50 20.87) wanted -4.56. The floor moves down log2(sun / 3) stops; the +3 cap and lighting_dark do not move."""
    assert R.SUN_FLOOR_REFERENCE_WM2 == L.SUN_STRENGTH_M11_WM2 == 3.0
    shift = R.sun_floor_shift(L.SUN_STRENGTH_WM2)
    assert shift == pytest.approx(math.log2(1000.0 / 3.0), abs=1e-4)
    for no_shift in (None, 0.0, 2.0, 3.0, float("nan"), "x"):
        assert R.sun_floor_shift(no_shift) == 0.0
    limits = R.view_limits(R.EXPOSURE_LIMITS, shift)
    assert limits[1] == R.EXPOSURE_LIMITS[1] == 3.0 and limits[0] == pytest.approx(-2.0 - shift, abs=1e-4)
    assert R.view_limits(R.EXPOSURE_LIMITS, 0.0) == R.EXPOSURE_LIMITS
    ev_old, raw_old, at_old = R.exposure_from(179.634978, R.EXPOSURE_TARGET, R.EXPOSURE_LIMITS)
    ev, raw, at_limit = R.exposure_from(179.634978, R.EXPOSURE_TARGET, limits)
    assert raw == raw_old == pytest.approx(-7.6409, abs=1e-3)
    assert (ev_old, at_old) == (-2.0, True)                     # the old floor: 5.6 stops too bright
    assert ev == pytest.approx(-7.6667, abs=1e-3) and not at_limit
    assert R.exposure_from(20.870293, R.EXPOSURE_TARGET, limits)[0] == pytest.approx(-4.5, abs=1e-6)
    dark_view = R.lighting_dark_entry("c", "r", 6.3718, 3.0, limits, 0.0109)
    assert dark_view is not None and dark_view == R.lighting_dark_entry("c", "r", 6.3718, 3.0, R.EXPOSURE_LIMITS, 0.0109)
    # the render key carries the floor, so a scene with another sun is never reused
    base = dict(samples=8, resolution=(160, 90), denoiser="OPENIMAGEDENOISE", exposure_mode="auto",
                exposure_value=None, target=0.9, wb_mode="auto", wb_fixed=None, hidden=[], plugged=[])
    assert R.render_key(R.key_settings(**base, limits=limits)) != R.render_key(R.key_settings(**base,
                                                                                         limits=R.EXPOSURE_LIMITS))
    # the records validate: the manifest's exposure_floor and the entry's floor_shift_stops
    from wenart.blender import schemas
    rm = json.loads((ROOT / "results" / "renders" / "real02" / "render_manifest.json").read_text(encoding="utf-8"))
    rm["exposure_limits"] = list(R.EXPOSURE_LIMITS)
    rm["exposure_floor"] = {"sun_wm2": 1000.0, "reference_wm2": 3.0, "shift_stops": shift, "view_limits": list(limits)}
    rm["renders"][0]["exposure"].update(limits=list(limits), floor_shift_stops=shift)
    schemas.validate_render_manifest(rm)
    rm["exposure_floor"]["shift_stops"] = -1.0
    with pytest.raises(Exception):
        schemas.validate_render_manifest(rm)


def test_preflight_p3_replayed_cameras_the_build_did_not_use_are_listed_with_the_reason():
    """A camera record whose room is not a rendered room of the build (P4 re-ingests real02 and real03: a renamed
    room) or an exterior record in a build without exterior views was left out without a word (only the counts of
    ``cameras_from`` differed). ``build.unused_replayed`` names each one with the reason; the build adds them to
    ``cameras_from.dropped`` and the warnings."""
    from wenart.blender import schemas
    replay = C.replay_cameras(json.loads(REAL02.read_text(encoding="utf-8")))
    plans = replay["plans"]
    assert len(plans) == 41 and replay["dropped"] == []
    made = [p for p in plans if p["kind"] == "interior" and p["room_id"] != "r_L0_banyo"]
    unused = B.unused_replayed(plans, made, replay["dropped"])
    assert {u["name"] for u in unused} == {p["name"] for p in plans if p not in made}
    assert {u["name"] for u in unused} == {"cam_r_L0_banyo_1", "cam_r_L0_banyo_2"} | {f"ext_{k}" for k in range(1, 7)}
    assert all("room r_L0_banyo on level L0" in u["reason"] for u in unused if u["name"].startswith("cam_"))
    assert all("no exterior views" in u["reason"] for u in unused if u["name"].startswith("ext_"))
    assert B.unused_replayed(plans, plans, []) == []
    assert B.unused_replayed(plans, made, unused) == []                      # never listed twice
    record = B.cameras_from_summary({"path": str(REAL02), "cameras": 41}, dict(replay, dropped=unused), made, False)
    assert record["replayed"] == len(made) and len(record["dropped"]) == 8
    jsonschema_validate = __import__("jsonschema").validate
    jsonschema_validate(record, schemas.CAMERAS_FROM)


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8): the light and colour of P3's real04 views
# --------------------------------------------------------------------------

# P3's project white point (cam_r_L1_teras_1, daylight only, 5,635 K, tint 5.26, residual 0.35) and Blender's white
# point at 2700 K, tint 0 (bpy 5.2.2: the colour of a 2700 K lamp; render.kelvin_whitepoint), both luminance 1.
P3_ANCHOR = [1.106758, 0.981679, 0.867122]
RIG_2700K = [1.9353, 0.8035, 0.1922]


def _rb(rgb) -> float:
    return float(rgb[0]) / float(rgb[2])


def test_fixround_p3_the_view_white_point_mixes_daylight_and_the_rig_by_its_share():
    """P3 applied the daylight point to rooms lit only by the 2700 K rig: 24 of 48 views over R/B 1.6. The view's
    white point is the project's daylight colour mixed with the rig's colour by the view's rig share, corrected with
    the same residual; share 0 is the project point exactly, share 1 the rig's own white point."""
    lum = 0.2126 * P3_ANCHOR[0] + 0.7152 * P3_ANCHOR[1] + 0.0722 * P3_ANCHOR[2]
    assert lum == pytest.approx(1.0, abs=1e-4)
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 0.0, 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    # the project's daylight colour is recovered from its white point: the residual-corrected mix of share 0 is it
    day = R.normalise_whitepoint([v ** (1 / 0.65) for v in P3_ANCHOR])
    assert R.whitepoint_from(day, 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    full = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 1.0, 0.35)
    assert full == pytest.approx(R.whitepoint_from(RIG_2700K, 0.35), abs=1e-6)
    ratios = [_rb(R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, s, 0.35)) for s in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert ratios == sorted(ratios) and ratios[0] < ratios[-1]                    # warmer with the rig's share
    # A white tile lit by the rig alone, scene-linear (pixel = light / white point): under the project point it is
    # 7.9 times redder than blue (P3's peach baths), under the view's own point the residual's cast is left.
    under_anchor = _rb([RIG_2700K[i] / P3_ANCHOR[i] for i in range(3)])
    under_view = _rb([RIG_2700K[i] / full[i] for i in range(3)])
    assert under_anchor > 7.0 and under_view == pytest.approx(_rb(RIG_2700K) ** 0.35, rel=1e-3)
    assert under_view < 2.3
    # no correction at all (a residual of 1) and bad shares keep the anchor; residual 0 neutralises the rig fully
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 1.0, 1.0) == pytest.approx(P3_ANCHOR, abs=1e-5)
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, None, 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, float("nan"), 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 2.0, 0.35) == pytest.approx(full, abs=1e-6)
    neutral = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 1.0, 0.0)
    assert _rb([RIG_2700K[i] / neutral[i] for i in range(3)]) == pytest.approx(1.0, abs=1e-4)
    # the rig share: 1 - daylight / all light (luminance of the two metered illuminants)
    assert R.rig_share([1.0, 1.0, 1.0], [0.25, 0.25, 0.25]) == pytest.approx(0.75)
    assert R.rig_share([1.0, 1.0, 1.0], None) == 1.0 and R.rig_share([1.0, 1.0, 1.0], [2.0, 2.0, 2.0]) == 0.0
    assert R.rig_share(None, [1.0, 1.0, 1.0]) is None and R.rig_share([0.0, 0.0, 0.0], None) is None
    assert 0.0 < R.WB_RIG_SHARE_MIN <= 0.05 and "rig share" in R.WB_VIEW_RULE


def test_fixround_p3_roof_terraces_render_under_the_exterior_world():
    """P3: real04's six terrace views rendered under the interior HDRI (5.2 stops under the sun pair): a black sky
    at the sunlit EV -7.5, a dusk sky beside hard sun shadows. A camera of an open-air room (shell.OUTDOOR_ROOM_TYPES,
    'balcony': the TERAS rooms of real02 and real04) renders under the exterior world and follows its lamp rule."""
    from wenart.blender.shell import OUTDOOR_ROOM_TYPES

    real04 = json.loads((ROOT / "results" / "furniture" / "real04" / "building_final.json").read_text(encoding="utf-8"))
    terraces = {r["id"]: r.get("room_type") for r in real04["rooms"] if r["id"] in ("r_L1_teras", "r_L1_teras_2")}
    assert terraces == {"r_L1_teras": "balcony", "r_L1_teras_2": "balcony"} and "balcony" in OUTDOOR_ROOM_TYPES
    assert R.open_air("balcony") and not R.open_air("living") and not R.open_air(None) and not R.open_air("")
    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_interior": "World",
             "wenart_world_exterior_sun_disc": True, "wenart_world_exterior_disc_camera_only": True}
    assert R.world_for(props, None, "balcony") == R.world_for(props, "interior", "balcony") == "wenart_world_exterior"
    assert R.world_for(props, "interior", "living") == R.world_for(props, "interior") == "World"
    assert R.world_for(props, "exterior") == "wenart_world_exterior"
    assert R.world_for({"wenart_world_interior": "World"}, None, "balcony") == "World"     # no exterior build
    assert R.world_for({}, None, "balcony") is None and R.world_for({}, "exterior") is None
    assert R.under_exterior_sky(props, None, "balcony") and not R.under_exterior_sky(props, None, "bedroom")
    assert not R.under_exterior_sky({"wenart_world_interior": "World"}, None, "balcony")
    p1 = dict(props, wenart_world_exterior_disc_camera_only=False)                       # the P1 world
    assert R.sun_hidden_for(p1, None, "balcony") == R.sun_hidden_for(p1, "exterior") is True
    assert R.sun_hidden_for(props, None, "balcony") == R.sun_hidden_for(props, "exterior") is False
    assert not R.sun_hidden_for(p1, None, "living")
    # the room type: the camera's property first, else the scene manifest's room floors (real02's committed
    # manifest: its terrace camera cam_r_L1_teras_1; door thresholds carry the room they open into and are left out)
    manifest = json.loads(REAL02.read_text(encoding="utf-8"))
    types = R.room_types_from_manifest(manifest)
    assert types["r_L1_teras"] == types["r_L1_teras_2"] == "balcony" and all(k.startswith("r_") for k in types)
    assert "cam_r_L1_teras_1" in {c["name"] for c in manifest["cameras"]}
    assert R.camera_room_type("", "r_L1_teras", types) == "balcony"
    assert R.camera_room_type("bedroom", "r_L1_teras", types) == "bedroom"
    assert R.camera_room_type(None, None, types) is None and R.room_types_from_manifest(None) == {}


def _fake_blender(monkeypatch):
    """A stand-in for bpy and mathutils, enough for cameras.create_cameras (the CPU tests have no Blender)."""
    import sys
    import types

    class Obj(dict):
        def __init__(self, name, data=None):
            super().__init__()
            self.name, self.data, self.location, self.rotation_euler = name, data, None, None

    class Vec(list):
        def __sub__(self, other):
            return Vec(a - b for a, b in zip(self, other))

        def to_track_quat(self, *_):
            return types.SimpleNamespace(to_euler=lambda: (0.0, 0.0, 0.0))

    data = types.SimpleNamespace(cameras=types.SimpleNamespace(new=lambda name: types.SimpleNamespace(name=name)),
                                 objects=types.SimpleNamespace(new=lambda name, cam: Obj(name, cam)))
    monkeypatch.setitem(sys.modules, "bpy", types.SimpleNamespace(data=data))
    monkeypatch.setitem(sys.modules, "mathutils", types.SimpleNamespace(Vector=Vec))
    linked = []
    return types.SimpleNamespace(objects=types.SimpleNamespace(link=linked.append)), linked


def test_fixround_p3_cameras_carry_their_room_type(monkeypatch):
    """The build marks every room camera with its room's type (replayed cameras included), so render.py finds the
    terrace cameras without the scene manifest."""
    building = json.loads((ROOT / "results" / "furniture" / "real02" / "building_final.json").read_text(encoding="utf-8"))
    room_types = {r["id"]: r.get("room_type") for r in building["rooms"]}
    plans = [p for p in C.replay_cameras(json.loads(REAL02.read_text(encoding="utf-8")))["plans"]
             if p["kind"] == "interior"]
    assert C.camera_room_type({"room_id": "r_L1_teras"}, room_types) == "balcony"
    assert C.camera_room_type({"room_id": "r_L1_teras", "room_type": "living"}, room_types) == "living"
    assert C.camera_room_type({"room_id": None}, room_types) == "" and C.camera_room_type({"room_id": "r_x"}) == ""
    collection, linked = _fake_blender(monkeypatch)
    manifest_objects: list = []
    made = C.create_cameras(plans, collection, manifest_objects, room_types=room_types)
    assert len(made) == len(plans) == len(linked) == len(manifest_objects)
    by_name = {ob.name: ob for ob in made}
    assert by_name["cam_r_L1_teras_1"]["wenart_room_type"] == "balcony"
    assert all(ob["wenart_room_type"] == room_types[ob["wenart_room"]] for ob in made)
    assert R.world_for({"wenart_world_exterior": "sky", "wenart_world_interior": "World"},
                       by_name["cam_r_L1_teras_1"].get("wenart_camera_kind"),
                       by_name["cam_r_L1_teras_1"]["wenart_room_type"]) == "sky"
    assert next(o for o in manifest_objects if o["name"] == "cam_r_L1_teras_1")["assumed"]["room_type"] == "balcony"
    # without the building's map the property is empty and render.py types the camera from the scene manifest
    collection, _ = _fake_blender(monkeypatch)
    made = C.create_cameras(plans[:1], collection, [])
    assert made[0]["wenart_room_type"] == ""


def test_fixround_p3_the_window_pull_reaches_the_pane_target():
    """P3: the pull stopped at the first k with pane clip <= 1 % (k 1-2), leaving pane medians of 0.86-0.97 (the
    sunlit outside 5-8 stops over): a blank pale window. A k now also needs the pane highlights under the AgX
    shoulder (p90 <= 0.85) or the pane median at mid-tone (0.65), up to 10 stops, panes still brighter than the
    walls."""
    assert R.PULL_STEPS == tuple(range(1, 11)) and R.PULL_P90_MAX == 0.85 and R.PULL_MEDIAN_TARGET == 0.65

    def c(k, clip, median, p90):
        return {"k": k, "clip": clip, "median": median, "p90": p90}
    salon_1 = c(1, 0.0, 0.9672, 0.985)                       # P3 cam_r_L-1_salon_1 at k 1: clip 0, median 0.967
    assert not R.pull_qualifies(salon_1, 0.5)                # the Milestone 6 rule took it
    assert R.pull_qualifies({k: v for k, v in salon_1.items() if k != "p90"}, 0.5)   # a record of the old rule
    cands = [salon_1, c(2, 0.0, 0.93, 0.97), c(3, 0.0, 0.88, 0.95), c(4, 0.0, 0.82, 0.92), c(5, 0.0, 0.74, 0.86),
             c(6, 0.0, 0.70, 0.80), c(7, 0.0, 0.60, 0.70)]
    assert R.choose_pull(cands, 0.5) == (6, "smallest k with pane clip <= 1 %, the pane target and panes brighter "
                                            "than the walls")
    assert R.choose_pull(cands, None)[0] == 6
    assert R.choose_pull(cands, 0.72)[0] == 5                # k 6 darker than the walls: the deepest k still brighter
    assert R.choose_pull(cands, 0.99)[0] == 0
    wide = [c(1, 0.0, 0.80, 0.99), c(2, 0.0, 0.64, 0.97)]   # a sun patch keeps p90 high: the median target stops it
    assert R.choose_pull(wide, 0.3)[0] == 2
    assert not R.pull_qualifies(c(3, 0.02, 0.6, 0.7), 0.3)  # the clip rule stays


def test_fixround_p3_the_sky_pull_keeps_the_facade_exposure():
    """P3: ext_1/2/4 metered on shaded facades (EV -4.0..-4.5) had a near-white sky (median 0.81-0.92, saturation
    0.03-0.13) while ext_3/7 (-7.67) were blue. The sky (no surface hit) is pulled by the smallest k that brings
    its median under 0.8 with saturation >= 0.12; a sky that already reads blue, or one that never does (beside the
    sun), stays as rendered."""
    import numpy as np

    assert R.SKY_PULL_STEPS == (1, 2, 3, 4) and R.SKY_PULL_MEDIAN_MAX == 0.8 and R.SKY_PULL_SAT_MIN == 0.12
    ext_2 = {"median": 0.84, "saturation": 0.08}
    cands = [{"k": 1, "median": 0.78, "saturation": 0.10}, {"k": 2, "median": 0.70, "saturation": 0.14},
             {"k": 3, "median": 0.60, "saturation": 0.17}]
    assert R.choose_sky_pull(ext_2, cands)[0] == 2
    assert R.choose_sky_pull({"median": 0.5, "saturation": 0.3}, cands) == \
        (0, "the sky is under the shoulder and saturated as rendered: no pull")
    assert R.choose_sky_pull({"median": 0.92, "saturation": 0.03},
                             [{"k": k, "median": 0.9 - 0.1 * k, "saturation": 0.05} for k in (1, 2, 3, 4)])[0] == 0
    depth = np.array([[1e10, 5.0], [np.inf, np.nan]])
    assert R.sky_mask(depth).tolist() == [[True, False], [True, True]]
    img = np.array([[[100, 116, 127], [200, 200, 200]], [[0, 0, 0], [100, 116, 127]]], dtype=np.uint8)
    mask = np.array([[True, True], [False, True]])
    assert R.masked_saturation(img, mask) == pytest.approx((127 - 100) / 127, abs=1e-6)     # P3 ext_7's blue sky
    assert R.masked_saturation(img, np.array([[False, True], [True, False]])) == 0.0
    assert R.masked_percentile(np.full((2, 2, 3), 255, np.uint8), np.ones((2, 2), bool), 90) == pytest.approx(1.0)


def test_fixround_p3_a_rig_replaces_the_fill_light_only_with_a_ceiling_fixture():
    """P3: r_L0_yatak_odasi_4 has no daylight window; its bedroom rig (two 470 lm bedside lamps) replaced the 150 W
    fill light and the room rendered night-dark (+6.1..+6.5 EV wanted, beyond set_lighting's x3). Bedside lamps or a
    pendant add to the fill light; halls, kitchens and baths (a ceiling fixture) keep the round-3 rule."""
    why = "room has no window"
    bedroom = {"id": "r_L0_yatak_odasi_4", "room_type": "bedroom", "polygon": [[0, 0], [4.2, 0], [4.2, 4], [0, 4]]}
    bed = _piece("bed", "bed_double", (2.1, 3.0), (1.8, 2.0), front=270.0)
    plan = L.rig_plan(bedroom, [bed], 0.0, 2.7)
    assert [f["kind"] for f in plan["fixtures"]] == ["bedside", "bedside"]
    assert L.rig_replaces_fill(plan, why) is False
    hall = {"id": "r_h", "room_type": "hall", "polygon": [[0, 0], [6, 0], [6, 2], [0, 2]]}
    assert L.rig_replaces_fill(L.rig_plan(hall, [], 0.0, 2.7), why) is True
    assert L.rig_replaces_fill(L.rig_plan(hall, [], 0.0, 2.7), None) is False          # a daylit room: no fill light
    kitchen = {"id": "r_k", "room_type": "kitchen", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    assert L.rig_replaces_fill(L.rig_plan(kitchen, [], 0.0, 2.7), why) is True
    dining = {"id": "r_d", "room_type": "dining", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    assert L.rig_replaces_fill(L.rig_plan(dining, [_piece("t", "table_dining", (2.5, 2), (1.8, 0.9))], 0.0, 2.7),
                               why) is False
    assert L.rig_replaces_fill({"fixtures": []}, why) is False


def test_fixround_p3_hall_and_stair_fixtures_carry_bulbs_for_the_floor_area():
    """P3: the halls had one 1100 lm fixture for 11.9-15.3 m² and metered +3.0..+3.6 EV even after the agent's
    x2.8-x3.0 (10 lighting_dark views); the baths, two fixtures in 5 m², metered +1.5..+2.0. Hall and stair fixtures
    now carry 1100 lm bulbs for 450 lm per m²; the other rigs are unchanged."""
    hall_spec = L.room_rig("hall")[0]
    assert hall_spec["lumens_per_m2"] == L.RIG_CIRCULATION_LUMENS_PER_M2 == 450.0
    assert L.room_rig("stair")[0]["lumens_per_m2"] == 450.0
    assert L.rig_bulbs(hall_spec, 11.9, 1) == 5 and L.rig_bulbs(hall_spec, 15.3, 1) == 7
    assert L.rig_bulbs(hall_spec, 7.6, 2) == 2 and L.rig_bulbs(hall_spec, 1.0, 1) == 1
    for room_type in ("bathroom", "wc", "kitchen", "bedroom", "dining", "living"):
        assert all(L.rig_bulbs(f, 50.0, 1) == 1 and "lumens_per_m2" not in f for f in L.room_rig(room_type))
    hall = {"id": "r_L-1_koridor_2", "room_type": "hall", "polygon": [[0, 0], [3.5, 0], [3.5, 3.4], [0, 3.4]]}
    (fixture,) = L.rig_plan(hall, [], 0.0, 2.7)["fixtures"]
    assert fixture["bulbs"] == 5 and fixture["lumens_per_bulb"] == 1100.0 and fixture["lumens"] == 5500.0
    assert fixture["light"]["energy_w"] == pytest.approx(5 * hall_spec["watts_applied"])
    assert fixture["watts_applied"] == pytest.approx(5 * L.watts_for_lumens(1100.0) * L.RIG_GAIN)
    assert "5 x 1100 lm bulbs" in fixture["reason"]
    long_hall = {"id": "r1", "room_type": "hall", "polygon": [[0, 0], [12, 0], [12, 1.5], [0, 1.5]]}
    fixtures = L.rig_plan(long_hall, [], 0.0, 2.7, agent_factor=2.0)["fixtures"]
    assert len(fixtures) == 4 and all(f["bulbs"] == 2 for f in fixtures)          # 18 m² x 450 / (4 x 1100)
    assert fixtures[0]["light"]["energy_w"] == pytest.approx(2.0 * 2 * hall_spec["watts_applied"])
    bath = {"id": "r_b", "room_type": "bathroom", "polygon": [[0, 0], [2.5, 0], [2.5, 2], [0, 2]]}
    ceiling = L.rig_plan(bath, [], 0.0, 2.5)["fixtures"][0]
    assert "bulbs" not in ceiling and ceiling["light"]["energy_w"] == L.room_rig("bathroom")[1]["watts_applied"]
    # P3's evidence: incident light per applied W/m² of the halls' views (L-1 koridor_2 0.0498-0.0682, L1 koridor
    # 0.0678-0.0918) at the old and the new density; the metered EV is log2(0.9 / incident)
    for area, per_wm2 in ((11.9, (0.0498, 0.0682)), (15.3, (0.0678, 0.0918))):
        old = 1 * hall_spec["watts_applied"] / area
        new = L.rig_bulbs(hall_spec, area, 1) * hall_spec["watts_applied"] / area
        assert all(math.log2(0.9 / (k * old)) > 4.5 for k in per_wm2)              # over the +3 cap without the agent
        assert all(math.log2(0.9 / (k * new)) < 2.85 for k in per_wm2)             # within it before any agent edit


# --------------------------------------------------------------------------
# Fix round part 2 (17 Oct 2026, the review of part 1): the open-air clip, and CPU replays of the GPU checks of
# tests/gpu/test_render.py on hand-made manifests (each replay fails on the part-1 GPU checks, which passed them)
# --------------------------------------------------------------------------

EXT_PROPS = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_interior": "World",
             "wenart_world_exterior_sun_disc": True, "wenart_world_exterior_disc_camera_only": True}


class _Cam(dict):
    """A stand-in for a Blender camera object: custom properties and ``data.clip_start`` / ``data.clip_end``."""

    def __init__(self, kind=None, clip_end=200.0):
        super().__init__(wenart_camera_kind=kind)
        import types
        self.data = types.SimpleNamespace(clip_start=0.05, clip_end=clip_end)


def test_fixround_part2_open_air_views_take_the_exterior_clip_end():
    """Part 1 put the terrace views under the exterior world but kept the room cameras' 200 m clip: the ground ended
    1.3 degrees under the horizon and the rays above it showed the sky's below-horizon colour, a dark band along the
    horizon of every terrace view. An open-air view under the exterior world now takes the exterior views' clip end
    (``exterior.CLIP_END``) for metering and render, records it and gets the built clip back afterwards."""
    from wenart.blender import exterior as E

    rule = R.OPEN_AIR_CLIP_RULE
    assert C.CLIP_END_M == 200.0 and E.CLIP_END == 3000.0 and "exterior.CLIP_END" in rule
    assert R.view_clip_end(200.0, EXT_PROPS, "interior", "balcony") == (3000.0, rule)
    assert R.view_clip_end(200, EXT_PROPS, None, "balcony") == (3000.0, rule)
    assert R.view_clip_end(5000.0, EXT_PROPS, None, "balcony") == (5000.0, rule)          # never shortened
    assert R.view_clip_end(200.0, EXT_PROPS, "interior", "living") == (200.0, None)
    assert R.view_clip_end(200.0, EXT_PROPS, None, None) == (200.0, None)
    assert R.view_clip_end(200.0, {"wenart_world_interior": "World"}, None, "balcony") == (200.0, None)  # no exterior
    assert R.view_clip_end(150.0, EXT_PROPS, "exterior") == (150.0, None)        # an exterior view keeps its own clip
    # The band's geometry on real02's committed terrace camera (4.4 m up, level, 16 mm on 36 mm, 1920 px): the ground
    # at the clip end lies h / d under the horizon; 200 m: about 19 rows (the review: ~19 px), the exterior clip end:
    # under the GPU check's HORIZON_MARGIN_PX (and the skirt and the backdrop ring catch those rays before it).
    manifest = json.loads(REAL02.read_text(encoding="utf-8"))
    cam = next(c for c in manifest["cameras"] if c["name"] == "cam_r_L1_teras_1")
    fpx = cam["lens_mm"] / cam["sensor_mm"] * cam["resolution"][0]
    rows = {d: fpx * cam["position"][2] / d for d in (C.CLIP_END_M, E.CLIP_END)}
    assert 17.0 < rows[200.0] < 21.0 and rows[3000.0] < 2.0
    # the Blender side on a stand-in camera: set, read back, the built clip end returned for the restore
    terrace = _Cam("interior")
    record, built = R.set_view_clip(terrace, EXT_PROPS, "balcony")
    assert terrace.data.clip_end == 3000.0 and built == 200.0
    assert record == {"start_m": 0.05, "end_m": 3000.0, "built_end_m": 200.0, "rule": rule}
    living = _Cam("interior")
    record, built = R.set_view_clip(living, EXT_PROPS, "living")
    assert living.data.clip_end == built == 200.0 and record["rule"] is None and record["end_m"] == 200.0
    from wenart.blender import schemas

    __import__("jsonschema").validate(record, schemas.RENDER_ENTRY["properties"]["clip"])


def _gpu_render_module(monkeypatch, outputs: Path):
    """tests/gpu/test_render.py imported against ``outputs`` (its env is read at import), as
    tests/test_blender_render.py does."""
    import importlib.util

    monkeypatch.setenv("WENART_OUTPUTS", str(outputs))
    monkeypatch.setenv("RENDER_TEST_PROJECTS", "real04")
    spec = importlib.util.spec_from_file_location("gpu_test_render_m13_light",
                                                  ROOT / "tests" / "gpu" / "test_render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _wb_project(anchor, entries, rig_rooms=("r_b",)):
    rooms = {r: {"replaces_fill_light": True, "fixtures": [f"rig_{r}_ceiling_1"]} for r in rig_rooms}
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}, "rig": {"on": True, "rooms": rooms}}}
    render = {"white_balance_mode": "project", "renders": entries,
              "white_balance_project": {"whitepoint": anchor, "residual": 0.35, "kelvin": 5635.0}}
    return "real04", scene, render


def _wb_entry(camera, room_id, whitepoint, share=None, anchor=P3_ANCHOR, shift=0.0, world="World"):
    return {"camera": camera, "room_id": room_id, "world": world,
            "exposure": {"wb_project_whitepoint": list(anchor), "whitepoint": list(whitepoint), "wb_rig_share": share,
                         "wb_rig_whitepoint": RIG_2700K if share is not None else None, "wb_view_shift_mired": shift}}


def test_fixround_part2_gpu_white_point_pins_do_not_read_the_views_own_share(tmp_path, monkeypatch):
    """The part-1 GPU check computed each view's expected white point from the view's own recorded share, so a share
    that is wrong passed: a daylight view with an inflated share, or a rig-lit room whose share stuck at 0. The views
    under the exterior sky must keep the anchor with no share; the rooms whose rig replaces the fill light must be
    corrected toward the rig."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    mixed = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 0.8, 0.35)
    good = [_wb_entry("ext_2", None, P3_ANCHOR, world="wenart_world_exterior"),
            _wb_entry("cam_r_L1_teras_1", "r_L1_teras", P3_ANCHOR, world="wenart_world_exterior"),
            _wb_entry("cam_r_s_1", "r_s", P3_ANCHOR, share=0.0),
            _wb_entry("cam_r_b_1", "r_b", mixed, share=0.8, shift=90.0)]
    gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P3_ANCHOR, good))
    # a terrace view metered with an inflated share (self-consistent: the mix of that share)
    inflated = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 0.4, 0.35)
    bad = good[:1] + [_wb_entry("cam_r_L1_teras_1", "r_L1_teras", inflated, share=0.4, shift=40.0,
                                world="wenart_world_exterior")] + good[2:]
    with pytest.raises(AssertionError, match="cam_r_L1_teras_1.*under the exterior sky"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P3_ANCHOR, bad))
    # the rig-lit bath with its share stuck at 0 (the anchor itself: self-consistent, P3's orange bath)
    bad = good[:3] + [_wb_entry("cam_r_b_1", "r_b", P3_ANCHOR, share=0.0)]
    with pytest.raises(AssertionError, match="cam_r_b_1.*lit by its rig alone"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P3_ANCHOR, bad))
    # a rig-lit room barely corrected: each share over the floor, the median under RIG_ONLY_MEDIAN_SHARE
    weak = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 0.1, 0.35)
    bad = good[:3] + [_wb_entry("cam_r_b_1", "r_b", weak, share=0.1, shift=10.0)]
    with pytest.raises(AssertionError, match="median rig share"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P3_ANCHOR, bad))
    assert gpu.RIG_ONLY_MEDIAN_SHARE == 0.5


def _sky(k, before=(0.84, 0.06), after=(0.70, 0.14), tried=None, full=0.93):
    tried = tried if tried is not None else [{"k": 1, "median": 0.78, "saturation": 0.10},
                                             {"k": 2, "median": 0.70, "saturation": 0.14}][:max(k, 2)]
    return {"ev": -float(k), "k": k, "sky_px": 5000, "sky_share": 0.2, "median_before": before[0],
            "saturation_before": before[1], "median_after": after[0] if k else before[0],
            "saturation_after": after[1] if k else before[1], "rule": "r", "tried": tried,
            "haze_px": 2400, "full_weight_share": full}


def test_fixround_part2_gpu_sky_pull_check_fails_when_no_sky_is_pulled(tmp_path, monkeypatch):
    """The part-1 GPU check judged only the pulls that happened: with the sky pull never firing (sky_pull None, or
    k 0 although a tried k qualifies) real04's ext_2 / ext_4 kept P3's near-white skies and the check passed."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}}}

    def project(*skies):
        return "real04", scene, {"renders": [{"camera": c, "room_id": None, "sky_pull": s}
                                             for c, s in zip(("ext_1", "ext_2", "ext_4"), skies)]}
    unpullable = _sky(0, before=(0.92, 0.03), tried=[{"k": k, "median": 0.9 - 0.08 * k, "saturation": 0.05}
                                                     for k in (1, 2, 3, 4)])
    k1 = _sky(1, before=(0.81, 0.10), after=(0.72, 0.13), tried=[{"k": 1, "median": 0.72, "saturation": 0.13}])
    gpu.test_sky_and_window_pulls_reach_their_targets(project(unpullable, _sky(2), k1))
    assert gpu.SKY_PULLED_VIEWS["real04"] == ("ext_2", "ext_4")
    with pytest.raises(AssertionError, match="ext_2.*not pulled"):              # no sky record at all
        gpu.test_sky_and_window_pulls_reach_their_targets(project(unpullable, None, k1))
    with pytest.raises(AssertionError, match="ext_4.*not pulled"):              # k 0 with a qualifying k tried
        gpu.test_sky_and_window_pulls_reach_their_targets(project(unpullable, _sky(2), _sky(0)))
    with pytest.raises(AssertionError, match="no view pulled"):                 # none pulled anywhere
        gpu.test_sky_and_window_pulls_reach_their_targets(
            ("real03", scene, {"renders": [{"camera": "ext_9", "room_id": None, "sky_pull": _sky(0)}]}))


def _fill_scene(rooms: dict, objects=(), assumed=(), lights=()):
    floors = [{"kind": "floor", "wenart_id": r, "room_type": "bedroom"} for r in rooms]
    return {"lighting": {"rig": {"on": True, "rooms": rooms, "lights": list(lights)}},
            "objects": floors + [{"name": n} for n in objects], "assumed": list(assumed)}


def test_fixround_part2_gpu_fill_light_check_names_its_rooms(tmp_path, monkeypatch):
    """The part-1 GPU check took its rooms from the manifest's own ``adds_to_fill_light`` flags: with the old wiring
    (the bedside rig replaced the fill light) no room had the flag, nothing was checked and it passed, while
    r_L0_yatak_odasi_4 rendered night-dark. The windowless bedrooms are named now."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    names = ("r_L0_yatak_odasi_3", "r_L0_yatak_odasi_4")
    fixtures = {r: [f"rig_{r}_bedside_1", f"rig_{r}_bedside_2"] for r in names}
    good = {r: {"fixtures": fixtures[r], "dropped": [], "replaces_fill_light": False, "adds_to_fill_light": True,
                "fill_light_reason": "room has no window"} for r in names}
    lights = [f"{f}_light" for r in names for f in fixtures[r]]
    assumed = [{"kind": "rig_adds_to_fill_light", "parent": r} for r in names]
    render = {"renders": []}
    gpu.test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(
        ("real04", _fill_scene(good, [f"light_{r}" for r in names], assumed, lights), render))
    # the part-1 wiring undone: the bedside rig replaces the fill light, no flag, no light_<room>
    old = {r: dict(good[r], replaces_fill_light=True, adds_to_fill_light=False) for r in names}
    replaced = [{"kind": "rig_replaces_fill_light", "parent": r} for r in names]
    with pytest.raises(AssertionError, match="r_L0_yatak_odasi_3.*no fill light"):
        gpu.test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(
            ("real04", _fill_scene(old, (), replaced, lights), render))
    # the fill light built but the room not flagged and its bedside lights lost
    lost = {r: dict(good[r], adds_to_fill_light=False) for r in names}
    with pytest.raises(AssertionError, match="without adds_to_fill_light.*without their lights"):
        gpu.test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(
            ("real04", _fill_scene(lost, [f"light_{r}" for r in names], assumed, ()), render))
    # a required room missing from the scene; the L-1b rooms are checked only where L-1b is built
    with pytest.raises(AssertionError, match="r_L0_yatak_odasi_4.*not in the scene"):
        gpu.test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(
            ("real04", _fill_scene({names[0]: good[names[0]]}, [f"light_{names[0]}"], assumed[:1],
                                   lights[:2]), render))
    assert gpu.FILL_LIGHT_ROOMS["real04"] == {"r_L0_yatak_odasi_3": True, "r_L0_yatak_odasi_4": True,
                                              "r_L-1b_oda": False, "r_L-1b_oda_2": False}
    # a room whose rig built no fixture (real02's r_L0_yatak_odasi_4: the bedside lamps would stand outside the
    # room) needs only its fill light
    bare = dict(good, r_L0_yatak_odasi_4={"fixtures": [], "dropped": [{"kind": "bedside"}],
                                          "replaces_fill_light": False, "adds_to_fill_light": False})
    gpu.test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(
        ("real04", _fill_scene(bare, [f"light_{r}" for r in names], assumed[:1], lights[:2]), render))


def _open_air_project(out: Path, band_rows: int = 0, clip: bool = True, black_band: bool = False):
    """A real04-like open-air view at 192 x 108 (real02's terrace camera: 4.4 m up, level, 16 mm, shift_y -0.1:
    the horizon at row 54 - 0.1 x 192 = 34.8): sky above the horizon (no hit), far ground under it (hit, beyond
    the 65 m of depth_mm), and ``band_rows`` rows of no-hit dark sky under the horizon (the 200 m clip's band)."""
    import numpy as np

    from wenart import views

    w, h = 192, 108
    renders = out / "real04" / "renders"
    renders.mkdir(parents=True)
    rgb = np.zeros((h, w, 3), np.uint8)
    normal = np.zeros((h, w, 3), np.uint8)
    rgb[:35] = (150, 175, 215)                              # sky (rows 0..34; the horizon at 34.8)
    rgb[35:] = (95, 105, 85)                                # far ground and terrace
    normal[35:] = (128, 128, 255)                           # hit, normal up
    if band_rows:
        rgb[35:35 + band_rows] = (6, 6, 7) if black_band else (34, 36, 40)    # haze-lifted dark grey
        normal[35:35 + band_rows] = 0
    views.write_png_rgb(renders / "cam_r_L1_teras_1.png", rgb)
    views.write_png_rgb(renders / "cam_r_L1_teras_1_normal.png", normal)
    views.write_png16(renders / "cam_r_L1_teras_1_depth_mm.png", np.zeros((h, w), np.uint16))
    views.write_png16(renders / "cam_r_L1_teras_1_index.png", np.zeros((h, w), np.uint16))
    entry = {"camera": "cam_r_L1_teras_1", "room_id": "r_L1_teras", "level_id": "L1", "resolution": [w, h],
             "png": "cam_r_L1_teras_1.png", "render_key": "0" * 16, "index_stats": {},
             "files": {"index": "cam_r_L1_teras_1_index.png", "depth_mm": "cam_r_L1_teras_1_depth_mm.png",
                       "normal": "cam_r_L1_teras_1_normal.png"},
             "open_air": True, "world": "wenart_world_exterior"}
    if clip:
        entry["clip"] = {"start_m": 0.05, "end_m": 3000.0, "built_end_m": 200.0, "rule": R.OPEN_AIR_CLIP_RULE}
    render = {"renders": [entry]}
    (renders / "render_manifest.json").write_text(json.dumps(render), encoding="utf-8")
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}},
             "objects": [{"kind": "floor", "wenart_id": "r_L1_teras", "room_type": "balcony"}],
             "cameras": [{"name": "cam_r_L1_teras_1", "position": [1.2005, 4.701, 4.4], "target": [1.2005, 5.701, 4.4],
                          "lens_mm": 16.0, "sensor_mm": 36.0, "shift_x": 0.0, "shift_y": -0.1,
                          "resolution": [1920, 1080]}]}
    return "real04", scene, render


def test_fixround_part2_gpu_open_air_check_sees_the_clip_and_the_horizon_band(tmp_path, monkeypatch):
    """The part-1 GPU check counted only near-black pixels among the no-hit pixels of the upper half: a haze-lifted
    dark-grey band of below-horizon sky under the horizon passed it. The check now needs the exterior clip end on
    the entry and no dark no-hit pixels under the horizon (the rays from the scene manifest's camera plan)."""
    import numpy as np

    gpu = _gpu_render_module(monkeypatch, tmp_path)
    # the horizon from the plan: real02's terrace camera at 192 x 108 has it at row 34.8
    below = gpu._below_horizon({"position": [0, 0, 4.4], "target": [0, 1, 4.4], "lens_mm": 16.0, "sensor_mm": 36.0,
                                "shift_y": -0.1}, (108, 192))
    # rows 35 and 36 (0.7 and 1.7 px under it at the centre) are within HORIZON_MARGIN_PX; from row 38 every pixel
    # is under the horizon by more than the margin (the corners' rays are longer, so row 37 only near the centre)
    assert not below[:37].any() and below[37].any() and below[38:].all()
    # a replayed record with a rotation only: the same camera (looking along +Y: X 90 degrees)
    replayed = gpu._below_horizon({"position": [0, 0, 4.4], "rotation_euler_deg": [90.0, 0.0, 0.0], "lens_mm": 16.0,
                                   "sensor_mm": 36.0, "shift_y": -0.1}, (108, 192))
    assert np.array_equal(replayed, below) and gpu._below_horizon({"lens_mm": 16.0}, (108, 192)) is None
    def check(case: str, **kw):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)       # the module reads its outputs folder at call time
        gpu.test_open_air_views_render_under_the_exterior_sky(_open_air_project(tmp_path / case, **kw))
    check("good")
    with pytest.raises(AssertionError, match="dark"):                           # a dark-grey band of 6 rows
        check("band", band_rows=6)
    with pytest.raises(AssertionError, match="exterior clip end"):              # rendered with the room camera's clip
        check("clip", clip=False)
    # the part-1 black-pixel check still catches a black band
    with pytest.raises(AssertionError, match="black sky pixels"):
        check("black", band_rows=3, black_band=True)


# --------------------------------------------------------------------------
# Fix round part 3 (17 Oct 2026, the review of part 2): the haze shell is sky
# --------------------------------------------------------------------------

HAZE_INDEX = 32767


def _haze_frame(seed: int = 0, h: int = 60, w: int = 80):
    """The passes of a view under the exterior sky as Cycles 5.2.2 writes them (real02's terrace and ext_2 in the
    shim): rows 0-29 sky with a building block (rows 12-29, columns 30-49, 10 m), rows 30-37 far ground behind the haze
    (300 m), rows 38-59 near ground (5 m). The haze shell (30 m, the reserved index) takes a random half of the sky's
    and the far ground's pixels at sample 0 (depth and index); the Normal pass is zero on the sky's shell hits and
    carries the far ground's normal (from the samples that passed the shell) on the far ground's.
    ``(channels, regions)``."""
    import numpy as np

    rng = np.random.default_rng(seed)
    depth = np.full((h, w), 1e10, dtype=np.float32)
    index = np.zeros((h, w), dtype=np.float32)
    normal = np.zeros((h, w, 3), dtype=np.float32)
    rows = np.arange(h)[:, None] * np.ones((1, w), dtype=int)
    building = np.zeros((h, w), dtype=bool)
    building[12:30, 30:50] = True
    sky = (rows < 30) & ~building
    far = (rows >= 30) & (rows < 38)
    near = rows >= 38
    depth[building], index[building], normal[building] = 10.0, 5.0, (0.0, -1.0, 0.0)
    depth[far], normal[far] = 300.0, (0.0, 0.0, 1.0)
    depth[near], normal[near] = 5.0, (0.0, 0.0, 1.0)
    shell = rng.random((h, w)) < 0.5
    sky_shell, far_shell = sky & shell, far & shell
    depth[sky_shell | far_shell], index[sky_shell | far_shell] = 30.0, HAZE_INDEX
    normal[far_shell] = (0.0, 0.0, 0.5)              # the far ground's normal from the samples past the shell
    channels = {"ViewLayer.Depth.Z": depth, "ViewLayer.Object Index.X": index, "ViewLayer.Normal.X": normal[..., 0],
                "ViewLayer.Normal.Y": normal[..., 1], "ViewLayer.Normal.Z": normal[..., 2]}
    return channels, {"sky": sky, "building": building, "far": far, "near": near, "sky_shell": sky_shell,
                      "far_shell": far_shell}


def _passes(channels):
    return (channels["ViewLayer.Depth.Z"], channels["ViewLayer.Object Index.X"],
            R.find_rgb(channels, "Normal"))


def test_fixround_part3_the_sky_mask_counts_the_haze_shell_as_sky():
    """Review of part 2: with the exterior clip end the camera rays cross the haze shell (``site.haze_box``), and
    Cycles writes the shell into the depth and index passes on a random half of them (real02's terrace at 16 and
    128 spp: 0.48 / 0.47 of the open sky left as no-hit). The depth-only mask (eb80db2) marked that random half, so
    no sky pixel reached full feather weight. The mask now adds the hits with the haze's reserved index and a zero
    normal (``haze_sky``), and never the haze hits in front of the far ground (they carry its normal)."""
    import numpy as np

    channels, reg = _haze_frame()
    depth, index, normal = _passes(channels)
    old = R.sky_mask(depth)                                                  # the depth alone: eb80db2's mask
    assert np.array_equal(old, reg["sky"] & ~reg["sky_shell"])
    assert 0.4 < old.sum() / reg["sky"].sum() < 0.6
    assert R.full_weight_share(old, R.feather_weights(old)) < 0.02          # speckled: no pixel at full weight
    mask = R.sky_mask(depth, index, normal, {HAZE_INDEX})
    assert np.array_equal(mask, reg["sky"])                                  # the whole sky and nothing else
    assert not (mask & reg["far_shell"]).any()                               # the far ground behind the shell stays
    assert np.array_equal(R.haze_sky(depth, index, normal, {HAZE_INDEX}), reg["sky_shell"])
    assert R.full_weight_share(mask, R.feather_weights(mask)) >= 0.8
    # a zero-normal hit of another object is no sky; without the haze set or a pass: the depth alone
    other = index.copy()
    other[reg["sky_shell"]] = 7.0
    assert np.array_equal(R.sky_mask(depth, other, normal, {HAZE_INDEX}), old)
    assert np.array_equal(R.sky_mask(depth, index, normal, ()), old)
    assert np.array_equal(R.sky_mask(depth, index, None, {HAZE_INDEX}), old)
    assert np.array_equal(R.sky_mask(depth, None, normal, {HAZE_INDEX}), old)
    assert R.full_weight_share(np.zeros((2, 2), dtype=bool), np.zeros((2, 2))) is None


def test_fixround_part3_the_sky_pull_blends_the_whole_sky_and_not_the_far_ground(tmp_path, monkeypatch):
    """Review of part 2: on the speckled mask every pulled sky pixel got a third of the pull, the PNG sky alternated
    between luminance 184 and 223 (19.6 levels between neighbours against 0.4) and the blended saturation stayed at
    0.057 against the 0.12 floor. ``RenderRun.sky_pull`` on the haze frame (``save_display`` stands in for Blender):
    the k 2 save reaches the whole sky, the full-weight sky has no neighbour step, the blended saturation reaches the
    floor, the record says ``haze_px`` and ``full_weight_share``, and nothing outside the sky changes (the haze hits in
    front of the far ground included)."""
    import types

    import numpy as np

    from wenart import views

    channels, reg = _haze_frame()
    h, w = reg["sky"].shape
    main = np.zeros((h, w, 3), dtype=np.uint8)
    main[reg["sky"]] = (223, 225, 228)          # the near-white sky at the facade EV (the denoised sky is smooth)
    main[reg["building"]] = (150, 140, 130)
    main[reg["far"]] = (120, 130, 110)
    main[reg["near"]] = (100, 100, 100)
    skies = {1: (205, 215, 232), 2: (150, 172, 206), 3: (110, 128, 160), 4: (80, 94, 120)}

    def fake_save(scene, result, path, ev, look=R.LOOK):
        k = int(round(-4.0 - float(ev)))
        img = (main.astype(np.float64) * 0.5 ** k).astype(np.uint8)      # everything darker at EV - k
        img[reg["sky"]] = skies[k]
        return img

    run = types.SimpleNamespace(ctx=types.SimpleNamespace(scene=None, haze={HAZE_INDEX}), out=tmp_path, warnings=[])
    cam = types.SimpleNamespace(name="cam_r_L1_teras_1")
    monkeypatch.setattr(R, "save_display", fake_save)
    record, weights, final = R.RenderRun.sky_pull(run, cam, {"ev": -4.0}, None, main, channels)
    assert record["k"] == 2 and record["sky_px"] == int(reg["sky"].sum())
    assert record["haze_px"] == int(reg["sky_shell"].sum()) > 0
    assert record["full_weight_share"] >= 0.8
    assert record["saturation_after"] >= R.SKY_PULL_SAT_MIN and record["median_after"] <= R.SKY_PULL_MEDIAN_MAX
    assert np.array_equal(final[~reg["sky"]], main[~reg["sky"]])            # the far ground behind the haze too
    lum = final[..., :3].astype(np.float64) @ np.array([0.2126, 0.7152, 0.0722])
    core = views.erode(reg["sky"], 2)                                        # the sky at full feather weight
    pairs = core[:, :-1] & core[:, 1:]
    assert pairs.sum() > 1000 and float(np.abs(np.diff(lum, axis=1))[pairs].max()) < 1.0
    assert np.array_equal(final[core], np.broadcast_to(np.array(skies[2], dtype=np.uint8), final[core].shape))


def test_fixround_part3_the_haze_index_is_reserved_and_kept_out_of_the_tables():
    """The haze objects get ``site.HAZE_PASS_INDEX`` (Blender's ``Object.pass_index`` maximum; a scene built before
    part 3 has them at 0, and ``reserve_haze_index`` gives it at render time), found by ``wenart_id`` or the
    ``wenart_haze`` material. The index stays out of the pass index table (it equals the scene manifest's), of what
    ``--hide`` can hide, and of the index map and its statistics (the haze is no object in view)."""
    import types

    from wenart.blender import site as SITE

    class Ob(dict):
        def __init__(self, name, pass_index=0, slots=(), **props):
            super().__init__(props)
            self.name, self.pass_index, self.material_slots = name, pass_index, list(slots)

    assert SITE.HAZE_PASS_INDEX == R._haze_index() == HAZE_INDEX
    objs = [Ob("haze", wenart_id="haze", wenart_kind="atmosphere"),
            Ob("haze.001", slots=[types.SimpleNamespace(material={"wenart_haze": True})]),
            Ob("win_1_glass", 3, wenart_id="win_1", wenart_kind="window"),
            Ob("furn_f_1", 4, wenart_id="f_1", wenart_kind="furniture"),
            Ob("ground", 0, slots=[types.SimpleNamespace(material=None)], wenart_id="ground", wenart_kind="terrain")]
    scene = types.SimpleNamespace(objects=objs)
    assert R.reserve_haze_index(scene) == {HAZE_INDEX}
    assert [o.pass_index for o in objs] == [HAZE_INDEX, HAZE_INDEX, 3, 4, 0]
    assert R.reserve_haze_index(scene) == {HAZE_INDEX}                       # idempotent
    assert R.pass_index_table(scene) == {"win_1": 3, "f_1": 4}
    assert sorted(R.indexed_objects(scene)) == ["f_1", "win_1"]              # --hide haze stays an unknown id
    assert R.window_indices(scene) == {3}
    assert R.reserve_haze_index(types.SimpleNamespace(objects=objs[2:])) == set()
    channels, _ = _haze_frame()
    products = R.pass_products(channels, {HAZE_INDEX})
    assert not (products["index"] == HAZE_INDEX).any() and products["index_values"] == [5]
    assert list(products["index_stats"]) == ["5"]
    assert HAZE_INDEX in R.pass_products(channels)["index_values"]          # without the set it would be an object


def test_fixround_part3_gpu_sky_pull_check_holds_the_floor_and_the_mask(tmp_path, monkeypatch):
    """The part-2 GPU check let the blended sky off the saturation floor (it blamed the feather at the silhouettes), so
    the reviewer's 128 spp shim re-render of real02 on eb80db2 passed it: terrace k 4 with saturation 0.034 -> 0.057,
    ext_2 k 2 with 0.059 -> 0.079, every sky pixel at a third of the pull. The blended sky now keeps the floor within
    ``SKY_PULL_SAT_ALLOWANCE`` and a pulled sky's mask is coherent (``full_weight_share`` at least
    ``SKY_MASK_FULL_WEIGHT_MIN``); the fixed shim render (0.146 / 0.128, full weight 0.961 / 0.957) passes."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}}}
    assert gpu.SKY_PULL_SAT_ALLOWANCE == 0.02 and gpu.SKY_MASK_FULL_WEIGHT_MIN == 0.8

    def project(**skies):
        return "real02", scene, {"renders": [
            {"camera": c, "room_id": "r_L1_teras" if c.startswith("cam_") else None,
             "open_air": c.startswith("cam_"), "sky_pull": s} for c, s in skies.items()]}
    tried_t = [{"k": 1, "median": 0.8017, "saturation": 0.0476}, {"k": 2, "median": 0.702, "saturation": 0.0688},
               {"k": 3, "median": 0.5755, "saturation": 0.1037}, {"k": 4, "median": 0.4258, "saturation": 0.1481}]
    tried_e = [{"k": 1, "median": 0.7511, "saturation": 0.0882}, {"k": 2, "median": 0.6365, "saturation": 0.1285}]
    # the fixed shim render (480 x 270, 128 spp)
    teras = _sky(4, before=(0.879, 0.0311), after=(0.4261, 0.1463), tried=tried_t, full=0.9614)
    ext_2 = _sky(2, before=(0.839, 0.0591), after=(0.6365, 0.1279), tried=tried_e, full=0.9565)
    gpu.test_sky_and_window_pulls_reach_their_targets(project(cam_r_L1_teras_1=teras, ext_2=ext_2))
    # eb80db2's records on the same scene: the speckled blend under the floor, no mask record
    head_t = {k: v for k, v in _sky(4, before=(0.8793, 0.0342), after=(0.7284, 0.0573), tried=tried_t).items()
              if k not in ("haze_px", "full_weight_share")}
    head_e = {k: v for k, v in _sky(2, before=(0.839, 0.0594), after=(0.7715, 0.0788), tried=tried_e).items()
              if k not in ("haze_px", "full_weight_share")}
    with pytest.raises(AssertionError, match="cam_r_L1_teras_1.*under the floor"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(cam_r_L1_teras_1=head_t, ext_2=ext_2))
    with pytest.raises(AssertionError, match="ext_2.*not pulled to its target"):         # a named view, too
        gpu.test_sky_and_window_pulls_reach_their_targets(project(cam_r_L1_teras_1=teras, ext_2=head_e))
    with pytest.raises(AssertionError, match="without full_weight_share"):
        gpu.test_sky_and_window_pulls_reach_their_targets(
            project(cam_r_L1_teras_1={k: v for k, v in teras.items() if k != "full_weight_share"}, ext_2=ext_2))
    # a speckled mask fails on its own, even with the blend at the floor
    with pytest.raises(AssertionError, match="speckled sky mask"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(cam_r_L1_teras_1=dict(teras, full_weight_share=0.0),
                                                                  ext_2=ext_2))
    # the allowance: 0.10 passes, 0.099 fails
    gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_2=dict(ext_2, saturation_after=0.10)))
    with pytest.raises(AssertionError, match="under the floor"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_2=dict(ext_2, saturation_after=0.099)))
