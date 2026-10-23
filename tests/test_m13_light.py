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

Fix round after P4a (17 Oct 2026, render code m13.3; the ``test_fixround_p4a_*`` tests, each failing on 03881bc):
every view keeps the project's daylight cast (``render.mixed_whitepoint``: P4a's rig-lit halls kept 2700 K ^ 0.35,
linear R/B 2.24 on white); the sky pull tries up to 6 stops and stops at a mid-tone median (P4a's terrace: a flat
dark slate sky at k 4), blends by the sky's coverage on the mask and a 2 px ring (``render.sky_pull_weights``: P4a's
white rims round the silhouettes) and records the views into the sun; the views under the interior world hide the
haze from their camera rays (P4a's grey-card windows); CPU replays of the GPU checks: the rig-lit walls against the
same project's daylight walls, the pulled sky's floor by its rule, the panes' saturation. The Blender-bound twin
(the kitchen window with and without the haze in view) is in tests/test_look_m6.py.

Fix round after P4b (17 Oct 2026, pod P4b, real03; the ``test_fixround_p4b_*`` tests, each failing on 11949a9 or on the
mutation its docstring names): ``RenderRun.sky_pull`` records whether the view looks into the sun (the review of the
P4a fix round; lead decision (4): such views are only listed); the GPU pane floor holds under the clear-sky moods
only; an unclipped pull near the walls comes before a clipped one (``render.choose_pull``); the interior glazing is
not pulled and is recorded against the room's walls; a view is balanced for its own room's rig lights
(``render.room_rig_kelvin``) with a block-median share for diagnosis; a ``lighting_dark`` view under one exposure step
over the cap is minor; the exterior exposure is capped by the sunlit ground (``render.exterior_exposure``) and the
lawn is recorded; CPU replays of the new and changed GPU checks (the orange check from a rig share of 0.4, the named
sky views, the pull, glazing, ground and lawn pins).

Pass before P5 (17 Oct 2026; the review of the fix round after P4b; the ``test_pass_p5_*`` tests, each failing on
adc3004): ``render.choose_pull``'s second rule applies only to panes that need a pull as rendered
(``render.pull_needed``; the pod records of P4a real02 cam_r_L1_teras_2_2 and P4b real03 yasama_3 / yasama_4_1 keep
k 0), and the interior glazing's clipped panes are pulled and their clip recorded (``render.choose_interior_pull``,
``RenderRun.interior_pull``, ``interior_glazing.clip`` / ``pull``; P4b real03 giris_holu_1 / 2 / 3_1), with CPU
replays of the two new GPU pins.

Fix round after P5 (22 Oct 2026, pod P5, real04, render code m13.4; the ``test_fixround_p5_*`` tests, each failing on
29e54d0 or on the mutation its docstring names): the GPU orange check sorts walls by the room type's finish and takes
its daylight references from unblocked views only; the sky pull gives a haze-shell hit at a roof's edge the roof's
reference (``render.shell_edge_pixels``; P5's dotted white edges) and records the dots left (``render.sky_edge_dots``);
an interior view's white point takes the tint of its own daylight (``render.view_tint_gain``; P5's olive L0
bedrooms); CPU replays of the new and changed GPU checks (dotted edges, olive walls, the white point with its tint).

Fix round after P6a (22 Oct 2026, render code m13.5): the new tests are in tests/test_m13_p6a_render.py. Pins changed
here on purpose: the code version and the sky pull's "no k" rule text (it names the median floor). The view tint's
pins below hold unchanged: m13.5 keeps the gain rule and meters its green on the walls.
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
    # fix round after P3 (16-17 Oct 2026): the view white point, the open-air world, the sky and window pulls -> m13.2;
    # fix round after P4a (17 Oct 2026): the daylight cast in every view, the sky pull's coverage weights, steps and
    # mid-tone target, the haze hidden from the interior views' camera rays -> m13.3 (P4a's views are not reused);
    # fix round after P5 (22 Oct 2026): the sky edge's shell hits and the view's daylight tint -> m13.4 (P5 rendered
    # m13.3); fix round after P6a (22 Oct 2026): the sky pull's median floor and the wall-metered tint -> m13.5 (P6a
    # rendered m13.4)
    assert R.RENDER_CODE_VERSION == "m13.5"
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
    white point is the project's daylight colour mixed with the rig's colour by the view's rig share; share 0 is the
    project point exactly. Fix round after P4a (17 Oct 2026): share 1 is no longer the rig's own white point (the
    residual applied to the rig's colour, 2700 K ^ 0.35 left on white: P4a's orange halls) but the rig's colour
    divided by the project's daylight cast (``test_fixround_p4a_every_view_keeps_the_project_daylight_cast``)."""
    lum = 0.2126 * P3_ANCHOR[0] + 0.7152 * P3_ANCHOR[1] + 0.0722 * P3_ANCHOR[2]
    assert lum == pytest.approx(1.0, abs=1e-4)
    assert R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 0.0, 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    # the project's daylight colour is recovered from its white point: the residual-corrected mix of share 0 is it
    day = R.normalise_whitepoint([v ** (1 / 0.65) for v in P3_ANCHOR])
    assert R.whitepoint_from(day, 0.35) == pytest.approx(P3_ANCHOR, abs=1e-5)
    full = R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, 1.0, 0.35)
    rig = R.normalise_whitepoint(RIG_2700K)
    assert full == pytest.approx(R.normalise_whitepoint([rig[i] / day[i] ** 0.35 for i in range(3)]), abs=1e-6)
    ratios = [_rb(R.mixed_whitepoint(P3_ANCHOR, RIG_2700K, s, 0.35)) for s in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert ratios == sorted(ratios) and ratios[0] < ratios[-1]                    # warmer with the rig's share
    # A white tile lit by the rig alone, scene-linear (pixel = light / white point): under the project point it is
    # 7.9 times redder than blue (P3's peach baths), under the view's own point the daylight rooms' cast is left.
    under_anchor = _rb([RIG_2700K[i] / P3_ANCHOR[i] for i in range(3)])
    under_view = _rb([RIG_2700K[i] / full[i] for i in range(3)])
    assert under_anchor > 7.0 and under_view == pytest.approx(_rb([d ** 0.35 for d in day]), abs=1e-3)
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
    # k 6 is a little darker than the walls (0.70 against 0.72) but unclipped with the pane target: fix round after P4b,
    # it comes before k 5 (the deepest k still brighter, without the target; render.choose_pull's second rule)
    assert R.choose_pull(cands, 0.72)[0] == 6
    # walls at 0.99: k 1 is unclipped at 98 % of the walls (fix round after P4b: the fourth rule; no pull before), and
    # nothing is pulled when every unclipped k is under 0.8 of the walls
    assert R.choose_pull(cands, 0.99)[0] == 1
    assert R.choose_pull(cands[4:], 0.99)[0] == 0
    # ... and only when the panes as rendered are clipped: unclipped panes are not darkened under the walls for nothing
    assert R.choose_pull(cands, 0.99, clip_before=0.0)[0] == 0 and R.choose_pull(cands, 0.99, clip_before=0.3)[0] == 1
    wide = [c(1, 0.0, 0.80, 0.99), c(2, 0.0, 0.64, 0.97)]   # a sun patch keeps p90 high: the median target stops it
    assert R.choose_pull(wide, 0.3)[0] == 2
    assert not R.pull_qualifies(c(3, 0.02, 0.6, 0.7), 0.3)  # the clip rule stays


def test_fixround_p3_the_sky_pull_keeps_the_facade_exposure():
    """P3: ext_1/2/4 metered on shaded facades (EV -4.0..-4.5) had a near-white sky (median 0.81-0.92, saturation
    0.03-0.13) while ext_3/7 (-7.67) were blue. The sky (no surface hit) is pulled by the smallest k that brings
    its median under 0.8 with saturation >= 0.12; a sky that already reads blue, or one that never does (beside the
    sun), stays as rendered."""
    import numpy as np

    # fix round after P4a (17 Oct 2026): up to 6 stops (test_fixround_p4a_the_sky_pull_tries_six_stops_...)
    assert R.SKY_PULL_STEPS == (1, 2, 3, 4, 5, 6) and R.SKY_PULL_MEDIAN_MAX == 0.8 and R.SKY_PULL_SAT_MIN == 0.12
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


def _wb_entry(camera, room_id, whitepoint, share=None, anchor=P3_ANCHOR, shift=0.0, world="World", day_green=None,
              gain=1.0):
    """Fix round after P5 (22 Oct 2026): the entry records the view's daylight tint (``wb_day_green``,
    ``wb_view_tint_gain``; none and 1.0 by default, as an m13.4 render of a view without a metered daylight)."""
    return {"camera": camera, "room_id": room_id, "world": world,
            "exposure": {"wb_project_whitepoint": list(anchor), "whitepoint": list(whitepoint), "wb_rig_share": share,
                         "wb_rig_whitepoint": RIG_2700K if share is not None else None, "wb_view_shift_mired": shift,
                         "wb_day_green": day_green, "wb_view_tint_gain": gain}}


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
    # a room whose rig built no fixture needs only its fill light (a synthetic case: real02's r_L0_yatak_odasi_4,
    # whose bedside lamps once stood outside the room, gets two wall sconces since the fix round after P4a)
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


# --------------------------------------------------------------------------
# Fix round after P4a (17 Oct 2026): the daylight cast in every view, the sky pull's weights, steps and mid-tone
# target, the views into the sun, the haze hidden from the interior views' camera rays
# --------------------------------------------------------------------------

# P4a (runs/20261017-072801-full, real02, not committed): the project white point (5,608.6 K, metered on the terrace
# with the rig hidden, residual 0.35) and the rig's white point at 2700 K (kelvin_whitepoint), as render_manifest.json
# recorded them.
P4A_ANCHOR = [1.114215, 0.979539, 0.866367]
P4A_RIG = [1.935351, 0.803501, 0.19225]


def test_fixround_p4a_every_view_keeps_the_project_daylight_cast():
    """P4a: all 12 rig-lit hall views of real02 were orange (wall R/B 1.64-1.81 against the 1.5 pin). The m13.2 white
    point applied the mood's residual to the rig's own colour, so a room lit by the rig alone kept 2700 K ^ 0.35: a
    white wall at linear R/B 2.244, against 1.145 in the daylight rooms under the same anchor. Every view now keeps the
    project's daylight cast: a white surface lit by the view's own mixed light reads 1.145 at every share (the
    verifier's pin at 0.25 / 0.5 / 0.9 and the kitchens' 0.70-0.79), the white point moves with the share with no
    step, and the rig's optional extra warmth (``WB_RIG_RESIDUAL``, 0) is capped at the mood's residual. Fails on
    03881bc (2.244 at share 1; no ``rig_residual``)."""
    day = R.normalise_whitepoint([v ** (1 / 0.65) for v in P4A_ANCHOR])
    rig = R.normalise_whitepoint(P4A_RIG)
    cast = _rb([d ** 0.35 for d in day])                       # a white wall in a daylight room: the mood's cast
    assert cast == pytest.approx(1.145, abs=1e-3)
    assert R.WB_RIG_RESIDUAL == 0.0 and "kept for every view" in R.WB_VIEW_RULE
    for s in (0.02, 0.25, 0.5, 0.70, 0.79, 0.9, 1.0):
        wp = R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, s, 0.35)
        light = [(1 - s) * d + s * q for d, q in zip(day, rig)]
        assert _rb([v / w for v, w in zip(light, wp)]) == pytest.approx(cast, abs=1e-3), s
        assert wp[2] < P4A_ANCHOR[2] and wp[0] > P4A_ANCHOR[0], s     # warmer than the anchor: a positive mired shift
    # P4a's hall white point (share 1, the residual on the rig's colour) left 2.244 on white
    m132 = R.whitepoint_from(rig, 0.35)
    assert _rb([rig[i] / m132[i] for i in range(3)]) == pytest.approx(2.244, abs=2e-3)
    full = R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.35)
    assert _rb([rig[i] / full[i] for i in range(3)]) == pytest.approx(cast, abs=1e-3)
    # continuous in the share: no step between the kitchens (0.70-0.79) and the halls (0.90-1.0)
    blue = [R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 0.70 + 0.01 * i, 0.35)[2] for i in range(31)]
    steps = [b1 - b2 for b1, b2 in zip(blue, blue[1:])]
    assert min(steps) > 0.0 and max(steps) < 0.01
    # the lever: the rig part's extra warmth, a share of the rig's colour over the daylight's, none at share 0,
    # never more than the mood's residual, nothing under a mood with residual 0 (cool daylight: full correction)
    warm = R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.35, 0.1)
    under = _rb([rig[i] / warm[i] for i in range(3)])
    assert under == pytest.approx(cast * (_rb(rig) / _rb(day)) ** 0.1, rel=1e-3) and cast < under < 1.5
    assert R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 0.0, 0.35, 0.1) == pytest.approx(
        R.normalise_whitepoint(P4A_ANCHOR), abs=1e-6)
    assert R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.35, 0.9) == pytest.approx(
        R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.35, 0.35), abs=1e-9)
    neutral = R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.0, 0.1)
    assert _rb([rig[i] / neutral[i] for i in range(3)]) == pytest.approx(1.0, abs=1e-4)
    assert R.mixed_whitepoint(P4A_ANCHOR, P4A_RIG, 1.0, 0.35, float("nan")) == pytest.approx(full, abs=1e-9)


# P4a's sky pull records (render_manifest.json, ``tried``: k, median, saturation of the EV - k saves)
P4A_SKY_TRIED = {
    "cam_r_L1_teras_1": ((0.8793, 0.0386), [(1, 0.8028, 0.0529), (2, 0.7026, 0.0785), (3, 0.576, 0.1176),
                                            (4, 0.4261, 0.1681)]),
    "cam_r_L1_teras_2_1": ((0.6606, 0.0694), [(1, 0.5247, 0.1056), (2, 0.3754, 0.1389)]),
    "cam_r_L1_teras_2_2": ((0.795, 0.067), [(1, 0.6931, 0.099), (2, 0.564, 0.1494)]),
    "ext_1": ((0.9395, 0.0249), [(1, 0.881, 0.0351), (2, 0.8085, 0.0516), (3, 0.7101, 0.0781), (4, 0.5841, 0.1154)]),
    "ext_2": ((0.8516, 0.0622), [(1, 0.7673, 0.0905), (2, 0.6567, 0.1325)]),
    "ext_5": ((0.9406, 0.0083), [(1, 0.8852, 0.0131), (2, 0.8109, 0.0146), (3, 0.7152, 0.0266), (4, 0.5905, 0.0382)]),
}


def test_fixround_p4a_the_sky_pull_tries_six_stops_and_stops_at_mid_tone():
    """P4a: the terrace's hazy sky reached the saturation floor only at k 4 (median 0.43, saturation 0.17: a flat dark
    slate sky against M11's bright clouds), ext_1 stayed white (k 4 gave 0.115, just under the floor; no k 5) and
    ext_5, 6 degrees off the sun, never turns blue. A k now also qualifies at a mid-tone median (<= 0.6) with a
    saturation of at least 0.10, and up to 6 stops are tried: the terrace stops at k 3 (median 0.58), ext_1 is pulled
    at k 4, teras_2_1 at k 1 (median 0.52 instead of 0.38), ext_2 and teras_2_2 keep k 2, ext_5 stays as rendered.
    Fails on 03881bc (k 4 / 0 / 2 and steps 1-4)."""
    from wenart.blender import schemas

    assert R.SKY_PULL_STEPS == (1, 2, 3, 4, 5, 6) and max(R.SKY_PULL_STEPS) == \
        schemas.SKY_PULL["oneOf"][1]["properties"]["k"]["maximum"]
    assert R.SKY_PULL_MEDIAN_TARGET == 0.6 and R.SKY_PULL_SAT_NEAR == 0.10 and R.SKY_PULL_SAT_MIN == 0.12
    chosen = {}
    for cam, (before, tried) in P4A_SKY_TRIED.items():
        cands = [{"k": k, "median": m, "saturation": s} for k, m, s in tried]
        chosen[cam] = R.choose_sky_pull({"median": before[0], "saturation": before[1]}, cands)
    assert {c: k for c, (k, _rule) in chosen.items()} == {"cam_r_L1_teras_1": 3, "cam_r_L1_teras_2_1": 1,
                                                          "cam_r_L1_teras_2_2": 2, "ext_1": 4, "ext_2": 2, "ext_5": 0}
    assert "mid-tone" in chosen["cam_r_L1_teras_1"][1] and "mid-tone" in chosen["ext_1"][1]
    assert "mid-tone" not in chosen["ext_2"][1] and chosen["ext_5"][1].startswith("no k")
    # the floor each pull was chosen against (the GPU check's blended-sky floor)
    assert R.sky_pull_floor({"median": 0.58, "saturation": 0.1176}) == R.SKY_PULL_SAT_NEAR
    assert R.sky_pull_floor({"median": 0.66, "saturation": 0.1325}) == R.SKY_PULL_SAT_MIN
    # the mid-tone rule needs both: a pale sky at mid-tone (ext_5 at k 4) or a saturated one over the shoulder fails
    assert not R.sky_pull_qualifies({"median": 0.59, "saturation": 0.038})
    assert not R.sky_pull_qualifies({"median": 0.65, "saturation": 0.11})
    assert not R.sky_pull_qualifies({"median": 0.85, "saturation": 0.3})
    # a sky already at mid-tone with the near floor is not pulled (P4a's teras_2_3 read 0.47 / 0.21)
    assert R.choose_sky_pull({"median": 0.55, "saturation": 0.105}, [])[0] == 0
    # k 5 and 6 are tried when nothing up to 4 qualifies
    deep = [{"k": k, "median": 0.95 - 0.1 * k, "saturation": 0.02 * k} for k in R.SKY_PULL_STEPS]
    assert R.choose_sky_pull({"median": 0.95, "saturation": 0.01}, deep)[0] == 5


def _edge_frame():
    """A pulled view at 12 x 10 as Cycles 5.2.2 writes it (the bpy shim, a plane's edge at 64 spp: Normal pass
    magnitudes 0.05 / 0.75 / 1 ... 1 / 0.95 / 0.30 across the edge, the depth hit where sample 0 hit): rows 0-4 sky
    with a chimney (rows 2-9, columns 4-7, 8 m) and its anti-aliased edges, rows 5-9 far ground behind the haze
    (300 m, |N| 0.4: the samples that scatter in the haze add no normal; at row 5, column 10 a hill-line pixel half
    sky, |N| 0.2), a haze-shell hit at 40 m in the sky."""
    import numpy as np

    h, w = 10, 12
    depth = np.full((h, w), 1e10)
    index = np.zeros((h, w))
    normal = np.zeros((h, w, 3))
    depth[5:] = 300.0
    normal[5:] = (0.0, 0.0, 0.4)
    normal[5, 10] = (0.0, 0.0, 0.2)                 # the hill line: half the samples reach the far ground
    depth[2:, 4:8], index[2:, 4:8], normal[2:, 4:8] = 8.0, 5.0, (0.0, -1.0, 0.0)
    normal[2:5, 3] = (0.0, -0.05, 0.0)              # sky, a sliver of the chimney in some samples (no hit at sample 0)
    normal[2:5, 4] = (0.0, -0.75, 0.0)              # the chimney's edge (hit), a quarter sky
    normal[2:5, 7] = (0.0, -0.95, 0.0)              # the other edge (hit), 5 % sky
    normal[2:5, 8] = (0.0, -0.30, 0.0)              # sky (no hit), 30 % chimney
    depth[0, 0], index[0, 0] = 40.0, HAZE_INDEX     # the shell, nothing behind it
    channels = {"ViewLayer.Depth.Z": depth, "ViewLayer.Object Index.X": index, "ViewLayer.Normal.X": normal[..., 0],
                "ViewLayer.Normal.Y": normal[..., 1], "ViewLayer.Normal.Z": normal[..., 2]}
    return channels


def test_fixround_p4a_sky_pull_weights_follow_the_sky_coverage():
    """P4a: 2-4 px white rims round the leaves, the roof ridge and the chimney of every pulled view (ext_2 ridge rims
    177-217 against a sky of 168; teras_1 159-223 against 125): the binary mask left the anti-aliased edge pixels at
    the unpulled sky and the inward feather gave the first two sky pixels 1/3 and 2/3 of the pull. The weights are now
    the sky coverage from the Normal pass on the mask and on a 2 px ring outside it: ``1 - |N|`` on the mask, ``1 -
    |N| / ref`` in the ring with ``ref`` the normal a fully covered pixel of that surface keeps nearby (the chimney 1,
    the far ground behind the haze 0.4), taken apart for the surfaces seen through the haze. A pure sky pixel next to
    the silhouette gets the full pull, an edge pixel its sky share, a covered pixel none (the far ground too, and its
    hill line half). Fails on 03881bc (no ``sky_pull_weights``)."""
    import numpy as np

    channels = _edge_frame()
    depth, index, normal = _passes(channels)
    mask = R.sky_mask(depth, index, normal, {HAZE_INDEX})
    assert mask[:5, :4].all() and mask[0:2, 4:8].all() and not mask[2:, 4:8].any() and not mask[5:].any()
    weights, ring = R.sky_pull_weights(mask, normal, depth=depth, index=index, haze_indices={HAZE_INDEX})
    assert R.SKY_RING_PX == 2 and R.SKY_REF_PX == 4 and R.SKY_FAR_MARGIN_M == 100.0
    assert weights[0, 0] == 1.0 and weights[1, 5] == 1.0                     # the shell's sky and the sky over it
    assert weights[3, 2] == 1.0                                              # one pixel from the edge: full pull
    assert weights[3, 3] == pytest.approx(0.95) and weights[3, 8] == pytest.approx(0.70)   # sky with a sliver
    assert ring[3, 4] and weights[3, 4] == pytest.approx(0.25)               # the edge, a quarter sky
    assert ring[3, 7] and weights[3, 7] == pytest.approx(0.05)
    assert ring[3, 5] and weights[3, 5] == 0.0                               # the chimney: no sky in it
    assert ring[6, 5] and not ring[7:, 4:8].any() and (weights[7:] == 0.0).all()   # 2 px from the sky, not 3
    far = np.zeros(ring.shape, dtype=bool)
    far[5:, :4] = far[5:, 8:] = True
    far[5, 10] = False
    assert ring[5, 0] and ring[6, 9] and (weights[far] == 0.0).all()         # the far ground behind the haze: covered
    assert weights[5, 10] == pytest.approx(0.5)                              # the hill line: half sky
    # 03881bc's feather: the first sky pixels got a third and two thirds of the pull, the edge pixels none
    feather = R.feather_weights(mask)
    assert feather[3, 3] == pytest.approx(1 / 3) and feather[3, 4] == 0.0
    # without the depth and the haze set the chimney (1) sets the far ground's reference: its haze would count as sky
    _w, ring_all = R.sky_pull_weights(mask, normal)
    assert np.array_equal(ring_all, ring) and _w[5, 0] == pytest.approx(0.6) and _w[3, 4] == pytest.approx(0.25)
    # foliage keeps less than 1 when fully covered (its leaf normals partly cancel): its own reference
    leaf = normal.copy()
    leaf[2:, 4:8] = (0.0, -0.7, 0.0)
    leaf[2:5, 4] = (0.0, -0.35, 0.0)                                         # half sky
    lw, _r = R.sky_pull_weights(mask, leaf, depth=depth, index=index, haze_indices={HAZE_INDEX})
    assert lw[3, 4] == pytest.approx(0.5) and lw[3, 5] == 0.0
    # without a Normal pass: the mask at full weight, no ring
    w0, r0 = R.sky_pull_weights(mask)
    assert np.array_equal(w0, mask.astype(float)) and not r0.any()


def test_fixround_p4a_the_sky_pull_blends_the_edges_by_their_sky_share(tmp_path, monkeypatch):
    """``RenderRun.sky_pull`` on the edge frame: the whole sky takes the k 2 save, the chimney's edge pixels are
    blended by their sky share, nothing outside the mask and the ring changes, and the record says the ring and the
    sun offset (none without a sun lamp in the stand-in scene). Fails on 03881bc (the sky next to the chimney at a
    third of the pull, the edge unchanged)."""
    import types

    import numpy as np

    channels = _edge_frame()
    depth, index, normal = _passes(channels)
    h, w = depth.shape
    main = np.zeros((h, w, 3), dtype=np.uint8)
    main[:5] = (224, 226, 228)                     # the near-white sky at the facade EV
    main[2:, 4:8] = (200, 200, 200)                # the white chimney
    main[5:] = (110, 120, 100)                     # far ground
    main[2:5, 4] = (218, 219, 220)                 # its edge pixels as rendered (mostly chimney)
    pulled = {1: (200, 212, 230), 2: (150, 172, 206), 3: (110, 128, 160)}

    def fake_save(scene, result, path, ev, look=R.LOOK):
        k = int(round(-4.0 - float(ev)))
        img = (main.astype(np.float64) * 0.5 ** k).astype(np.uint8)
        img[:2] = pulled[k]
        img[2:5, :4] = pulled[k]
        img[2:5, 8:] = pulled[k]
        return img

    run = types.SimpleNamespace(ctx=types.SimpleNamespace(scene=None, haze={HAZE_INDEX}), out=tmp_path, warnings=[])
    cam = types.SimpleNamespace(name="ext_2")
    monkeypatch.setattr(R, "save_display", fake_save)
    record, weights, final = R.RenderRun.sky_pull(run, cam, {"ev": -4.0}, None, main, channels)
    assert record["k"] == 2 and record["ring_px"] == 7                      # columns 4 and 7, rows 2-4; the hill line
    assert record["sun_offset_deg"] is None and record["into_sun"] is False
    assert record["targets"]["ring_px"] == R.SKY_RING_PX
    mask = R.sky_mask(depth, index, normal, {HAZE_INDEX})
    pure = mask & (np.abs(normal).sum(axis=-1) == 0)
    assert np.array_equal(final[pure], np.broadcast_to(np.array(pulled[2], np.uint8), final[pure].shape))
    k2 = (main.astype(np.float64) * 0.25).astype(np.uint8)                 # the k 2 save outside the sky
    assert np.array_equal(final[3, 4], np.rint(main[3, 4] * 0.75 + k2[3, 4] * 0.25).astype(np.uint8))
    assert np.array_equal(final[3, 3], np.rint(main[3, 3] * 0.05 + np.array(pulled[2]) * 0.95).astype(np.uint8))
    _w, ring = R.sky_pull_weights(mask, normal, depth=depth, index=index, haze_indices={HAZE_INDEX})
    assert np.array_equal(final[5, 10], np.rint(main[5, 10] * 0.5 + k2[5, 10] * 0.5).astype(np.uint8))
    still = ~mask & (weights == 0.0)
    assert np.array_equal(final[still], main[still])                         # the chimney's core and the far ground
    assert (still | mask | ring).all()                                       # only the mask and the ring can change


def test_fixround_p4a_the_record_names_the_views_into_the_sun():
    """P4a's ext_1 and ext_5 look 6 degrees off the sun (azimuth 45, elevation 35, north assumed): their skies stay
    white at any EV, and a locked exterior EV would not change that (the verifier's analysis). The sky pull records
    the angle between the view's and the sun's azimuth and ``into_sun`` within ``SKY_INTO_SUN_DEG``, for the report."""
    el, az = math.radians(35.0), math.radians(45.0)
    travel = (-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el))   # the light's direction

    def view(deg, down=-0.1):
        return (math.cos(math.radians(deg)), math.sin(math.radians(deg)), down)
    assert R.sun_offset_deg(view(39.0), travel) == pytest.approx(6.0, abs=0.01)           # ext_1
    assert R.sun_offset_deg(view(51.0, -0.27), travel) == pytest.approx(6.0, abs=0.01)    # ext_5, the aerial
    assert R.sun_offset_deg(view(225.0), travel) == pytest.approx(180.0, abs=0.01)        # the sun behind (ext_3)
    assert R.sun_offset_deg(view(135.0), travel) == pytest.approx(90.0, abs=0.01)         # ext_2 / ext_4 (84-96)
    assert R.sun_offset_deg(view(-170.0), travel) == pytest.approx(145.0, abs=0.01)       # across +-180
    assert R.sun_offset_deg((0.0, 0.0, -1.0), travel) is None and R.sun_offset_deg(view(10.0), None) is None
    assert R.sun_offset_deg(None, travel) is None and R.SKY_INTO_SUN_DEG == 30.0
    import types

    assert R.camera_forward(types.SimpleNamespace(name="cam")) is None       # a stand-in without a world matrix


def test_fixround_p4a_views_under_the_interior_world_hide_the_haze_from_their_camera_rays():
    """P4a's windows showed a flat grey card (pane saturation 0.00-0.07 against M11's clouds at 0.13-0.25): the camera's
    ray through the glass crossed up to 1200 m of haze before it reached the interior world. Every view that is not
    under the exterior sky renders with the haze hidden from its camera and transmission rays; the exterior views and
    the open-air rooms keep it (their sky is the haze and the sky world). The helpers hide and restore exactly those
    two ray types."""
    import types

    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_interior": "World"}
    assert R.haze_hidden_for(props, "interior", "bedroom") and R.haze_hidden_for(props, None, "hall")
    assert not R.haze_hidden_for(props, "exterior") and not R.haze_hidden_for(props, None, "balcony")
    assert not R.haze_hidden_for({}, "exterior")                               # no exterior world: no change outdoors
    assert R.haze_hidden_for({"wenart_world_interior": "World"}, None, "balcony")    # a terrace under the interior HDRI
    objs = [types.SimpleNamespace(name="haze", visible_camera=True, visible_transmission=True, visible_diffuse=True,
                                  visible_glossy=True),
            types.SimpleNamespace(name="haze.001", visible_camera=False, visible_transmission=True,
                                  visible_diffuse=True, visible_glossy=True)]
    saved = R.hide_haze_from_view(objs)
    assert [(o.visible_camera, o.visible_transmission, o.visible_diffuse, o.visible_glossy) for o in objs] == \
        [(False, False, True, True)] * 2
    R.restore_haze(saved)
    assert [(o.visible_camera, o.visible_transmission) for o in objs] == [(True, True), (False, True)]


def _wall_views(out: Path, views_rb: dict, wet_rooms=(), room_types: dict | None = None, blocked=(),
                entry_types: bool = False, rgb: dict | None = None, exposure: dict | None = None):
    """Hand-made renders of a project (32 x 18): every view all wall (index 0, a hit, a horizontal normal) of display
    R/B ``views_rb[cam][1]``; ``views_rb[cam]`` = (room_id, R/B, rig share). Returns ``(name, scene, render)``.
    Fix round after P5 (18 Oct 2026): the room floors carry a room type (``room_types``, else ``bathroom`` for the
    ``wet_rooms`` and ``bedroom`` for the others) as the scene manifest does, the entries carry it too with
    ``entry_types``, and the views of ``blocked`` record one element over 56 % of the frame (``index_stats``).
    Fix round after P5 (22 Oct 2026): ``rgb[cam]`` sets a view's wall colour instead (the olive check) and
    ``exposure[cam]`` adds fields to its exposure record."""
    import numpy as np

    from wenart import views

    w, h = 32, 18
    renders = out / "real02" / "renders"
    renders.mkdir(parents=True)
    entries = []
    types = dict(room_types or {})
    for room, _rb, _share in views_rb.values():
        types.setdefault(room, "bathroom" if room in wet_rooms else "bedroom")
    rgb_of = rgb
    for cam, (room, rb, share) in views_rb.items():
        rgb = np.zeros((h, w, 3), np.uint8)
        rgb[...] = (rgb_of or {}).get(cam) or (int(round(100 * rb)), 110, 100)
        normal = np.zeros((h, w, 3), np.uint8)
        normal[...] = (255, 128, 128)                                       # +X: a wall
        views.write_png_rgb(renders / f"{cam}.png", rgb)
        views.write_png_rgb(renders / f"{cam}_normal.png", normal)
        views.write_png16(renders / f"{cam}_depth_mm.png", np.full((h, w), 2000, np.uint16))
        views.write_png16(renders / f"{cam}_index.png", np.zeros((h, w), np.uint16))
        stats = {"251": {"pixels": int(0.56 * w * h), "box": [0, 0, w - 1, h - 1]}} if cam in blocked else {}
        entries.append({"camera": cam, "room_id": room, "level_id": "L0", "resolution": [w, h], "png": f"{cam}.png",
                        "render_key": "0" * 16, "index_stats": stats, "world": "World", "lens_mm": 18.0,
                        "files": {"index": f"{cam}_index.png", "depth_mm": f"{cam}_depth_mm.png",
                                  "normal": f"{cam}_normal.png"},
                        "exposure": {"wb_rig_share": share, "lighting_dark": None, **(exposure or {}).get(cam, {})},
                        **({"room_type": types[room]} if entry_types else {})})
    render = {"white_balance_mode": "project", "white_balance_project": {"whitepoint": P4A_ANCHOR, "residual": 0.35},
              "renders": entries}
    (renders / "render_manifest.json").write_text(json.dumps(render), encoding="utf-8")
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}},
             "objects": [{"kind": "floor", "wenart_id": r, "wet": r in wet_rooms or types[r] in ("kitchen", "bathroom"),
                          "room_type": types[r]} for r in sorted(types)]}
    return "real02", scene, render


def test_fixround_p4a_gpu_orange_check_compares_rig_lit_walls_with_the_daylight_walls(tmp_path, monkeypatch):
    """P4a: the fixed 1.5 pin ignored the paint (real02's warm greige walls, linear R/B 1.34). The GPU check now
    compares the walls of the rig-lit views with the walls of the same project's daylight views of the same kind
    (painted, or tiled in the rooms with a wet floor): at most ``RIG_ROOM_REL_MAX`` (1.1) times their median, set from
    the bpy shim re-render of P4a's scene at P4a's EV (painted daylight median 1.36; halls 1.64-1.78 with m13.2's white
    point, 1.26-1.36 with m13.3's). The fixed 1.5 stays only where no daylight view of that kind exists. Fix round after
    P4b: the bound is the median plus ``RIG_ROOM_ABOVE_DAY`` (0.15; the same verdicts here) and the views from a rig
    share of 0.4 are checked (``test_fixround_p4b_gpu_orange_check_covers_the_mixed_views``)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.RIG_ROOM_REL_MAX == 1.1 and gpu.RIG_ROOM_MAX_RB == 1.5
    day = {"cam_r_bed_1": ("r_bed", 1.40, 0.0), "cam_r_bed_2": ("r_bed", 1.36, 0.0),
           "cam_r_salon_1": ("r_salon", 1.38, 0.0)}                        # like real02's painted daylight walls

    def check(case, rig_views, wet=("r_bath",)):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / case, rig_views, wet))
    # real02 with m13.3: halls 1.26-1.36, baths 1.02-1.08 (no daylight bath: the fixed 1.5)
    check("m133", {**day, "cam_r_hall_1": ("r_hall", 1.36, 1.0), "cam_r_hall_2": ("r_hall", 1.305, 0.97),
                   "cam_r_bath_1": ("r_bath", 1.08, 1.0)})
    # real02 with m13.2: halls 1.64-1.78 over 1.1 x 1.38
    with pytest.raises(AssertionError, match="cam_r_hall_1.*painted"):
        check("m132", {**day, "cam_r_hall_1": ("r_hall", 1.654, 1.0), "cam_r_bath_1": ("r_bath", 1.25, 1.0)})
    # white walls (daylight 1.05): a hall at 1.3 is orange there, though under the fixed 1.5 ...
    white = {"cam_r_bed_1": ("r_bed", 1.05, 0.0), "cam_r_bed_2": ("r_bed", 1.06, 0.0)}
    with pytest.raises(AssertionError, match="cam_r_hall_1.*painted"):
        check("white", {**white, "cam_r_hall_1": ("r_hall", 1.30, 1.0)})
    # ... and a warmer paint (daylight 1.48) lets a hall at 1.55 pass, over the fixed 1.5
    warm = {"cam_r_bed_1": ("r_bed", 1.48, 0.0), "cam_r_bed_2": ("r_bed", 1.47, 0.0), "cam_r_bed_3": ("r_bed", 1.49, 0.0)}
    check("warm", {**warm, "cam_r_hall_1": ("r_hall", 1.55, 1.0)})
    # a tiled bath over the fixed 1.5 fails; a daylight bath sets the tiled walls' own bound
    with pytest.raises(AssertionError, match="cam_r_bath_1.*tiled"):
        check("bath", {**day, "cam_r_bath_1": ("r_bath", 1.55, 1.0)})
    with pytest.raises(AssertionError, match="cam_r_bath_1.*tiled"):
        check("bath_day", {**day, "cam_r_bath_2": ("r_bath_2", 1.05, 0.0), "cam_r_bath_1": ("r_bath", 1.25, 1.0)},
              wet=("r_bath", "r_bath_2"))
    # the views of a mixed room (share between WB_RIG_SHARE_MIN and RIG_CHECK_SHARE: 0.4 since the fix round after
    # P4b, 0.8 before) are neither reference nor checked
    check("mixed", {**day, "cam_r_kit_1": ("r_kit", 2.5, 0.3), "cam_r_hall_1": ("r_hall", 1.2, 1.0)})
    # no daylight painted view: the fixed 1.5
    check("fallback", {"cam_r_hall_1": ("r_hall", 1.45, 1.0)})
    with pytest.raises(AssertionError, match="cam_r_hall_1"):
        check("fallback_warm", {"cam_r_hall_1": ("r_hall", 1.55, 1.0)})


def test_fixround_p4a_gpu_sky_and_pane_checks(tmp_path, monkeypatch):
    """The GPU sky check holds a pulled sky to the floor of the rule its k was chosen by (a mid-tone pull: the near
    floor 0.10, else 0.12, each less the allowance), and lists the views into the sun; the pane check fails a project
    whose interior panes are grey cards (P4a: 0.00-0.07) and a window pull rendered before m13.3."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    # fix round after P4b: the pane floor holds under the clear-sky moods only (real02's warm daylight here)
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}}, "wenart_mood": "warm daylight"}
    tried = [{"k": 1, "median": 0.8028, "saturation": 0.0529}, {"k": 2, "median": 0.7026, "saturation": 0.0785},
             {"k": 3, "median": 0.576, "saturation": 0.1176}]                       # P4a's terrace up to k 3
    teras = _sky(3, before=(0.8793, 0.0386), after=(0.5762, 0.095), tried=tried, full=0.99)

    def project(sky=teras, panes=None, cam="cam_r_L1_teras_1"):
        renders = [{"camera": cam, "room_id": "r_L1_teras", "open_air": True, "sky_pull": sky}]
        for i, (sat, k) in enumerate(panes or []):
            wp = {"k": k, "pane_median_after": 0.7, "pane_saturation": sat}
            if k:
                wp["pane_saturation_after"] = sat
            renders.append({"camera": f"cam_r_bed_{i + 1}", "room_id": "r_bed", "open_air": False, "window_pull": wp})
        return "real02", scene, {"renders": renders}
    gpu.test_sky_and_window_pulls_reach_their_targets(project())                  # 0.095 >= 0.10 - 0.02
    with pytest.raises(AssertionError, match="under the floor 0.1 - 0.02"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(dict(teras, saturation_after=0.079)))
    # the same blend after a pull chosen by the 0.12 floor fails (03881bc held every pull to it)
    saturated = dict(teras, tried=tried[:2] + [dict(tried[2], saturation=0.13)])
    with pytest.raises(AssertionError, match="under the floor 0.12 - 0.02"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(saturated))
    # the panes: P4a's grey cards fail, the sky passes, a record without pane_saturation is an older render
    good = [(0.14, 1), (0.17, 1), (0.13, 2), (0.02, 1)]
    gpu.test_sky_and_window_pulls_reach_their_targets(project(panes=good))
    with pytest.raises(AssertionError, match="grey cards"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(panes=[(0.005, 1), (0.006, 2), (0.07, 0)]))
    old = project(panes=good)
    del old[2]["renders"][1]["window_pull"]["pane_saturation"]
    with pytest.raises(AssertionError, match="before m13.3"):
        gpu.test_sky_and_window_pulls_reach_their_targets(old)
    assert gpu.PANE_SAT_MIN <= 0.13                                                # M11's skies pass


# --------------------------------------------------------------------------
# Fix round after P4b (17 Oct 2026; pod P4b, real03): the ``test_fixround_p4b_*`` tests, each failing on 11949a9 or on
# the mutation its docstring names
# --------------------------------------------------------------------------

# Blender's white points at tint 0 (bpy 5.2.2, ``white_balance_temperature`` -> ``white_balance_whitepoint``,
# G-normalised; measured for this round): the rig colours of render.kelvin_whitepoint
WP_2700K = [2.4086, 1.0, 0.2393]
WP_4000K = [1.5303, 1.0, 0.5772]
P4B_ANCHOR = [1.115, 0.995, 0.714]          # real03's project white point (5,153 K, P4b render_manifest)


def _sun_view(deg, down=-0.1):
    return (math.cos(math.radians(deg)), math.sin(math.radians(deg)), down)


P4A_SUN_TRAVEL = (-math.cos(math.radians(35.0)) * math.cos(math.radians(45.0)),
                  -math.cos(math.radians(35.0)) * math.sin(math.radians(45.0)), -math.sin(math.radians(35.0)))


def test_fixround_p4b_the_sky_pull_records_whether_the_view_looks_into_the_sun(tmp_path, monkeypatch):
    """The review of the P4a fix round: no CPU test ran ``RenderRun.sky_pull`` with a scene, so ``sun_offset_deg`` was
    always None there and two mutations passed (``offset >= SKY_INTO_SUN_DEG``; the camera's direction passed for the
    sun's). On the edge frame with P4a's geometry (sun azimuth 45, elevation 35): a view 6 degrees off the sun whose
    sky never qualifies is recorded ``into_sun`` with the rule's note; a view with the sun behind (180 degrees) is not.
    Lead decision (4): the views into the sun are only listed."""
    import types

    import numpy as np

    channels = _edge_frame()
    h, w = channels["ViewLayer.Depth.Z"].shape
    main = np.full((h, w, 3), 236, dtype=np.uint8)

    def white_sky(scene, result, path, ev, look=R.LOOK):
        return np.full((h, w, 3), 230, dtype=np.uint8)           # a white sky beside the sun at every k
    monkeypatch.setattr(R, "save_display", white_sky)
    monkeypatch.setattr(R, "sun_travel", lambda scene: P4A_SUN_TRAVEL)
    run = types.SimpleNamespace(ctx=types.SimpleNamespace(scene=types.SimpleNamespace(name="scene"),
                                                          haze={HAZE_INDEX}), out=tmp_path, warnings=[])
    for deg, offset, into in ((39.0, 6.0, True), (225.0, 180.0, False), (75.0, 30.0, True), (76.0, 31.0, False)):
        monkeypatch.setattr(R, "camera_forward", lambda cam, d=deg: _sun_view(d))
        record, _w, final = R.RenderRun.sky_pull(run, types.SimpleNamespace(name="ext_1"), {"ev": -4.0}, None,
                                                 main, channels)
        assert record["k"] == 0 and final is None and record["tried"], deg
        assert record["sun_offset_deg"] == pytest.approx(offset, abs=0.01) and record["into_sun"] is into, deg
        note = f" (the view looks into the sun: {record['sun_offset_deg']:g} degrees off its azimuth)"
        assert record["rule"].endswith(note) is into, (deg, record["rule"])
    # fix round after P6a (22 Oct 2026; pin changed on purpose): the rule names the median floor of the pulled saves
    assert record["rule"] == "no k brings the sky under the shoulder with saturation above the median floor 0.4: no pull"


def test_fixround_p4b_gpu_pane_floor_holds_under_the_clear_sky_moods(tmp_path, monkeypatch):
    """The review of the P4a fix round: the pane-saturation floor (0.08, set under real02's warm daylight) failed a
    correct overcast, blue-hour or night window as a "grey card". It holds under the clear-sky moods only (warm
    daylight, cool daylight, bright noon, golden evening); for the others (and a project without a mood) the value is
    printed."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.PANE_SAT_MOODS == ("warm daylight", "cool daylight", "bright noon", "golden evening")
    assert set(gpu.PANE_SAT_MOODS) <= set(V.LIGHTING)

    def project(mood, sats, where="scene"):
        renders = [{"camera": f"cam_r_bed_{i}", "room_id": "r_bed", "open_air": False,
                    "exposure": {"mood": mood if where == "exposure" else None},
                    "window_pull": {"k": 1, "pane_median_after": 0.6, "pane_saturation": s, "pane_saturation_after": s}}
                   for i, s in enumerate(sats)]
        scene = {"lighting": {}} if where != "scene" else {"lighting": {}, "wenart_mood": mood}
        return "real05", scene, {"renders": renders}
    grey = [0.01, 0.02, 0.03]
    for mood in ("warm daylight", "Cool Daylight", "bright noon", "golden evening"):
        with pytest.raises(AssertionError, match="grey cards"):
            gpu.test_sky_and_window_pulls_reach_their_targets(project(mood, grey))
    with pytest.raises(AssertionError, match="grey cards"):                     # the mood on the exposure records
        gpu.test_sky_and_window_pulls_reach_their_targets(project("warm daylight", grey, "exposure"))
    for mood in ("overcast", "cloudy soft", "blue hour", "night", "interior evening", None):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(mood, grey))
    gpu.test_sky_and_window_pulls_reach_their_targets(project("warm daylight", [0.12, 0.14, 0.2]))


# P4b's window pull records (render_manifest.json): tried k (clip, median, p90) and the wall median
P4B_PULLS = {
    "cam_r_L0_yasama_8_3": (0.4855, [(1, 0.1377, 0.6088, 0.9818), (2, 0.0, 0.467, 0.9381)]),
    "cam_r_L0_ebeveyn_odasi_5_3": (0.4783, [(1, 0.0112, 0.5536, 0.9762), (2, 0.0, 0.4041, 0.9308)]),
    "cam_r_L0_ebeveyn_odasi_6_2": (0.5091, [(1, 0.011, 0.6315, 0.9619), (2, 0.0, 0.4895, 0.9109)]),
    "cam_r_L0_ruzgarlik_2": (0.4686, [(1, 0.0028, 0.3907, 0.9348)]),
    "cam_r_L0_giris_holu_3_1": (0.4582, [(1, 0.039, 0.4657, 0.9785), (2, 0.0, 0.3226, 0.9345)]),
    "cam_r_L0_yasama_4_2": (0.5836, [(1, 0.0, 0.3801, 0.9235)]),
    "cam_r_L0_yangin_merdiveni_1": (0.4531, [(1, 0.0, 0.535, 0.7248)]),
}


def test_fixround_p4b_an_unclipped_pull_near_the_walls_comes_before_a_clipped_one():
    """P4b: 10 real03 views kept clipped panes (P4a: 0) because a clip-free k made the panes a little darker than the
    bright greige walls: yasama_8_3 kept 13.9 % at k 1 although k 2 was clip-free at 0.467 against walls of 0.486. The
    smallest unclipped k with the pane target whose panes are at least 0.8 of the wall median now comes before a
    clipped k that stays brighter; panes under 0.8 of the walls still get no pull (yasama_4_2: 0.38 against 0.58).
    The search goes on past the walls and stops under 0.8 of them (``pull_search_done``). Fails on 11949a9 (k 1 / 1 /
    1 / 0)."""
    assert R.PULL_WALL_RATIO_MIN == 0.8

    def cands(rows):
        return [{"k": k, "clip": c, "median": m, "p90": p} for k, c, m, p in rows]
    chosen = {cam: R.choose_pull(cands(rows), wall) for cam, (wall, rows) in P4B_PULLS.items()}
    assert {cam: k for cam, (k, _r) in chosen.items()} == {
        "cam_r_L0_yasama_8_3": 2, "cam_r_L0_ebeveyn_odasi_5_3": 2, "cam_r_L0_ebeveyn_odasi_6_2": 2,
        "cam_r_L0_ruzgarlik_2": 1, "cam_r_L0_giris_holu_3_1": 1, "cam_r_L0_yasama_4_2": 0,
        "cam_r_L0_yangin_merdiveni_1": 1}
    assert "slightly darker than the walls" in chosen["cam_r_L0_yasama_8_3"][1]
    assert chosen["cam_r_L0_yangin_merdiveni_1"][1].startswith("smallest k with pane clip <= 1 %, the pane target and")
    assert chosen["cam_r_L0_giris_holu_3_1"][1].startswith("lowest pane clip")      # k 2 is under 0.8 of the walls
    # without the pane target: an unclipped k that keeps the panes brighter first, then one near the walls
    no_target = [{"k": 1, "clip": 0.02, "median": 0.8, "p90": 0.99}, {"k": 2, "clip": 0.0, "median": 0.75, "p90": 0.97}]
    assert R.choose_pull(no_target, 0.7) == (2, "unclipped panes brighter than the walls, the lowest highlights (no k "
                                                "reached the target)")
    assert R.choose_pull(no_target, 0.9)[0] == 2 and "no k reached the target" in R.choose_pull(no_target, 0.9)[1]
    assert R.choose_pull(no_target, 0.95)[0] == 0                                   # 0.75 < 0.8 x 0.95
    # the pane target near the walls comes before an unclipped k that stays brighter without it
    bright_pale = [{"k": 1, "clip": 0.0, "median": 0.8, "p90": 0.95}, {"k": 2, "clip": 0.0, "median": 0.55, "p90": 0.9}]
    assert R.choose_pull(bright_pale, 0.6)[0] == 2
    # the search: done at a qualifying k, at the smallest unclipped k near the walls, and under 0.8 of the walls
    y83 = cands(P4B_PULLS["cam_r_L0_yasama_8_3"][1])
    assert not R.pull_search_done(y83[0], 0.4855) and R.pull_search_done(y83[1], 0.4855)
    assert R.pull_search_done({"k": 3, "clip": 0.0, "median": 0.38, "p90": 0.9}, 0.4855)        # too dark: stop
    assert not R.pull_search_done({"k": 1, "clip": 0.0, "median": 0.70, "p90": 0.97}, 0.4855)   # no target yet: go on
    # under the walls, still clipped and over 0.8 of them: the next k may be clip-free
    assert not R.pull_search_done({"k": 2, "clip": 0.02, "median": 0.45, "p90": 0.95}, 0.4855)
    assert not R.pull_search_done({"k": 1, "clip": 0.03, "median": 0.9, "p90": 0.99}, None)
    assert R.pull_search_done({"k": 1, "clip": 0.0, "median": 0.6, "p90": 0.8}, None)
    from wenart.blender import schemas

    assert schemas.WINDOW_PULL["oneOf"][1]["properties"]["interior_pane_px"] == {"type": "integer", "minimum": 0}


def _glazing_frame():
    """A view of 20 x 30 px: an exterior window (index 5, columns 2-8) whose panes clip, an interior window between
    two rooms (index 6, columns 15-25) showing an amber hall, the room's walls (index 0) elsewhere; rows 2-10 glass
    (Diffuse Color 0.01), every other pixel albedo 0.5."""
    import numpy as np

    h, w = 20, 30
    index = np.zeros((h, w))
    index[2:11, 2:9] = 5
    index[2:11, 15:26] = 6
    albedo = np.full((h, w, 3), 0.5)
    albedo[index > 0] = 0.01
    main = np.zeros((h, w, 3), dtype=np.uint8)
    main[...] = (120, 110, 100)                       # greige walls
    main[index == 5] = (252, 252, 252)                # the sunlit outside, clipped
    main[index == 6] = (230, 180, 120)                # the 2700 K hall next door
    channels = {"ViewLayer.Diffuse Color.R": albedo[..., 0], "ViewLayer.Diffuse Color.G": albedo[..., 1],
                "ViewLayer.Diffuse Color.B": albedo[..., 2]}
    return index, channels, main


def test_fixround_p4b_interior_glazing_is_not_pulled_and_is_recorded(tmp_path, monkeypatch):
    """P4b: real03's 19 windows between halls, stairs, studios and bedrooms were pulled like outside windows
    (yasama_8_3, giris_holu_3_1 and yangin_merdiveni_1 at k 1: the neighbouring room a stop darker and more saturated,
    13.9 % clipped panes in yasama_8_3). A window whose ``room_ids`` name two indoor rooms is interior glazing
    (``interior_window_ids``; a window onto a roof terrace is not); the window pull leaves its panes out
    (``interior_pane_px``), and the view records them against its walls (``interior_glazing``: display R/B of each).
    Fails on 11949a9 (no ``interior_window_ids``; the interior panes in the pull's mask)."""
    import types

    import numpy as np

    real03 = json.loads(REAL03.read_text(encoding="utf-8"))
    ids = R.interior_window_ids(real03)
    assert len(ids) == 19 and {"win_L0_055", "win_L0_056", "win_L0_028"} <= ids and "win_L0_046" not in ids
    real02 = json.loads(REAL02.read_text(encoding="utf-8"))
    assert R.interior_window_ids(real02) == set()            # its two-room windows open onto the roof terraces
    assert R.interior_window_indices([("win_L0_055", 41), ("win_L0_046", 33), (None, 7)], real03) == {41}
    assert R.interior_window_indices([("win_L0_055", 41)], None) == set()
    index, channels, main = _glazing_frame()
    walls = index == 0

    def fake_save(scene, result, path, ev, look=R.LOOK):
        return (main.astype(np.float64) * 0.5 ** round(-float(ev))).astype(np.uint8)
    monkeypatch.setattr(R, "save_display", fake_save)
    ctx = types.SimpleNamespace(scene=None, windows={5, 6}, interior_windows={6}, haze=set(),
                                pass_index={"win_L0_046": 5, "win_L0_055": 6})
    run = types.SimpleNamespace(ctx=ctx, out=tmp_path, warnings=[])
    cam = types.SimpleNamespace(name="cam_r_L0_yasama_8_3")
    products = {"index": index.astype(np.uint16)}
    record, weights, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert record["pane_px"] == 63 and record["interior_pane_px"] == 99 and record["k"] >= 1
    assert record["targets"]["wall_ratio_min"] == R.PULL_WALL_RATIO_MIN
    assert np.array_equal(final[index == 6], main[index == 6])          # the hall next door as rendered
    assert (weights[index == 6] == 0).all() and (final[index == 5] < main[index == 5]).all()
    glazing = R.RenderRun.interior_glazing(run, final, channels, products, walls)
    assert glazing["windows"] == ["win_L0_055"] and glazing["pane_px"] == 99
    assert glazing["pane_rb"] == pytest.approx(230 / 120, abs=1e-3) and glazing["wall_rb"] == pytest.approx(1.2)
    assert glazing["delta_rb"] == pytest.approx(230 / 120 - 1.2, abs=2e-3)
    # without interior glazing in the scene: every window is pulled and nothing is recorded
    ctx.interior_windows = set()
    record, _w, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert record["pane_px"] == 162 and record["interior_pane_px"] == 0
    assert R.RenderRun.interior_glazing(run, final, channels, products, walls) is None
    from wenart.blender import schemas

    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(glazing, schemas.RENDER_ENTRY["properties"]["interior_glazing"])
    jsonschema.validate(None, schemas.RENDER_ENTRY["properties"]["interior_glazing"])


def test_fixround_p4b_the_white_point_follows_the_camera_rooms_rig(tmp_path, monkeypatch):
    """The P4b interior-glazing verifier: the build may light halls, stairs and baths at a neutral 4000 K, but the
    render balanced every view for the scene's first rig light (real03: a 2700 K bedside lamp), which would put a
    white wall of a 4000 K hall at linear R/B 0.33 (blue) instead of the daylight rooms' 1.27. A view is now balanced
    for its own room's rig lights (``room_rig_kelvin``; energy-weighted in mired when a room mixes temperatures), the
    scene's first light only when its room has none; the record says the source and a block-median share for
    diagnosis (``wb_rig_share_p50``; the white point still uses ``rig_share``, the verifier refuted a share change).
    Fails on 11949a9 (no ``room_rig_kelvin``; ``wb_rig_kelvin`` 2700 for the hall)."""
    import types

    lights = [("r_bed", 2700.0, 2.5), ("r_hall", 4000.0, 9.0), ("r_hall", 4000.0, 3.0), ("r_mix", 2700.0, 1.0),
              ("r_mix", 4000.0, 1.0)]
    assert R.room_rig_kelvin(lights, "r_hall") == (4000.0, "room")
    assert R.room_rig_kelvin(lights, "r_bed") == (2700.0, "room")
    assert R.room_rig_kelvin(lights, "r_living") == (2700.0, "scene")             # no rig light: the first one
    assert R.room_rig_kelvin(lights, "r_mix") == (round(1e6 / ((1e6 / 2700 + 1e6 / 4000) / 2), 1), "room")
    assert R.room_rig_kelvin([("r_mix", 2700.0, 3.0), ("r_mix", 4000.0, 1.0)], "r_mix")[0] == \
        round(1e6 / ((3 * 1e6 / 2700 + 1e6 / 4000) / 4), 1)
    assert R.room_rig_kelvin([], "r_hall") == (None, None)
    # the colour check: a white wall of a 4000 K hall at share 1, corrected for 4000 K, keeps the daylight cast; for
    # 2700 K it turns blue (the verifier's 0.33)
    day = R.normalise_whitepoint([v ** (1 / 0.65) for v in P4B_ANCHOR])
    cast = _rb([d ** 0.35 for d in day])
    hall = R.normalise_whitepoint(WP_4000K)
    right = R.mixed_whitepoint(P4B_ANCHOR, WP_4000K, 1.0, 0.35)
    wrong = R.mixed_whitepoint(P4B_ANCHOR, WP_2700K, 1.0, 0.35)
    assert cast == pytest.approx(1.271, abs=2e-3)
    assert _rb([a / b for a, b in zip(hall, right)]) == pytest.approx(cast, abs=1e-3)
    assert _rb([a / b for a, b in zip(hall, wrong)]) == pytest.approx(0.335, abs=2e-3)
    # Look._view_white with stand-ins: the hall view takes the hall's 4000 K
    look = object.__new__(R.Look)
    look.scene, look.windows, look.haze, look.room_types = {}, set(), set(), {}
    look.project = {"residual": 0.35}
    monkeypatch.setattr(R, "rig_objects", lambda scene: ["rig"])
    monkeypatch.setattr(R, "rig_lights", lambda scene: lights)
    monkeypatch.setattr(R, "hide_objects", lambda objs: [])
    monkeypatch.setattr(R, "unhide_objects", lambda saved: None)
    monkeypatch.setattr(R, "meter_camera", lambda *a, **k: {"illuminant": [0.01, 0.01, 0.01], "incident_p50": 0.002,
                                                            "seconds": 0.5})
    monkeypatch.setattr(R, "kelvin_whitepoint", lambda scene, k: R.normalise_whitepoint(
        {2700.0: WP_2700K, 4000.0: WP_4000K}[k]))
    for room, kelvin, source in (("r_hall", 4000.0, "room"), ("r_living", 2700.0, "scene")):
        cam = types.SimpleNamespace(name=f"cam_{room}_1", get={"wenart_room": room,
                                                                "wenart_camera_kind": "interior"}.get)
        rec = {"whitepoint": list(P4B_ANCHOR), "meter_seconds": 1.0}
        meter = {"illuminant": [0.1, 0.1, 0.1], "incident_p50": 0.02}
        look._view_white(cam, rec, meter, tmp_path, (64, 36))
        assert rec["wb_rig_kelvin"] == kelvin and rec["wb_rig_kelvin_source"] == source, room
        assert rec["wb_rig_share"] == pytest.approx(0.9) and rec["wb_rig_share_p50"] == pytest.approx(0.9)
        rig = R.normalise_whitepoint({2700.0: WP_2700K, 4000.0: WP_4000K}[kelvin])
        # fix round after P5 (22 Oct 2026; pin changed on purpose): the mix then takes the tint of the view's own
        # daylight (the stand-in's grey daylight against real03's green anchor, by the daylight share 0.1)
        gain = R.view_tint_gain(P4B_ANCHOR, 1.0, 0.35, 0.9)
        assert gain == pytest.approx((1.0 / R.green_ratio(P4B_ANCHOR)) ** 0.1, abs=1e-6) and gain < 1.0
        assert rec["wb_day_green"] == 1.0 and rec["wb_view_tint_gain"] == gain
        assert rec["whitepoint"] == pytest.approx(
            R.tinted_whitepoint(R.mixed_whitepoint(P4B_ANCHOR, rig, 0.9, 0.35, 0.0), gain), abs=1e-9)
    # the diagnostic share: the block medians, clamped; never None for a view with light
    assert R.rig_share_p50(0.18159, 0.089643) == pytest.approx(0.506, abs=1e-3)       # P4b banyo_6_1 (sums: 0.439)
    assert R.rig_share_p50(0.1, 0.2) == 0.0 and R.rig_share_p50(0.1, None) == 1.0
    assert R.rig_share_p50(None, 0.1) is None and R.rig_share_p50(0.0, 0.0) is None


def test_fixround_p4b_lighting_dark_under_one_exposure_step_is_minor():
    """P4b re-lit and re-rendered giris_holu_2_1 (0.01 stops over the cap) and giris_holu_4_2 / yasama_7_1 (0.04): the
    EV is rounded to 1/6 stop, so such a view renders at the cap anyway. Less than one exposure step over the cap is a
    minor, report-only finding with ``metrics.below_exposure_step``; the schema takes it; from one step it is major as
    before. Fails on 11949a9 (major)."""
    from wenart.blender import schemas

    assert R.LIGHTING_DARK_MINOR_STOPS == R.EXPOSURE_STEP == 1.0 / 6.0
    for over in (0.01, 0.04, 0.16):
        rec = R.lighting_dark_entry("cam_r_L0_giris_holu_2_1", "r_L0_giris_holu_2", 3.0 + over, 3.0, (-10.38, 3.0),
                                    0.0112)
        assert rec["severity"] == "minor" and rec["metrics"]["below_exposure_step"] is True, over
        assert "reported only" in rec["message"]
        pytest.importorskip("jsonschema").validate(rec, schemas.LIGHTING_DARK)
    step = R.lighting_dark_entry("c", "r", 3.0 + 1.0 / 6.0, 3.0, (-2.0, 3.0))
    assert step["severity"] == "major" and "below_exposure_step" not in step["metrics"]
    assert "reported only" not in step["message"]
    assert R.lighting_dark_entry("c", "r", 5.2, 3.0, (-2.0, 3.0))["severity"] == "critical"


def _meter_frame():
    """A metering frame of an exterior view, 24 x 48 px: rows 0-7 the shaded facade (normal z 0, incident 19), rows
    8-11 the far ground behind the haze shell (300 m, incident 50), rows 12-23 the sunlit near ground (8 m, incident
    265); the haze shell at 40 m takes the first column of rows 8-11 at sample 0."""
    import numpy as np

    h, w = 24, 48
    light = np.zeros((h, w, 3))
    nz = np.zeros((h, w))
    depth = np.full((h, w), 12.0)
    index = np.zeros((h, w))
    light[:8] = 19.0
    light[8:12], nz[8:12], depth[8:12] = 50.0, 1.0, 300.0
    light[12:], nz[12:], depth[12:] = 265.0, 1.0, 8.0
    depth[8:12, 0], index[8:12, 0] = 40.0, HAZE_INDEX
    albedo = np.full((h, w, 3), 0.4)
    return light, albedo, index, depth, nz


def test_fixround_p4b_the_exterior_exposure_caps_the_sunlit_ground(tmp_path, monkeypatch):
    """P4b: real03's ext_3 / ext_4 metered the shaded back facade (incident 19-22 against 79-123) at -4.33 / -4.67 EV
    and the sunlit lawn came out cream (saturation 0.11-0.19 against 0.35-0.42). The metering pass also gives the sunlit
    ground in front of the haze shell (``ground_p50``), and the facade exposure is capped at the ground's plus 1.5 stops
    (``exterior_exposure``, per view): a shaded facade (19) under a ground of 265 is capped, a sunlit one (110) is not,
    no ground means no cap. ``Look._decide`` records the cap. Fails on 11949a9 (no ``exterior_exposure``)."""
    import types

    assert R.EXTERIOR_GROUND_HEADROOM_STOPS == 1.5 and R.GROUND_NZ_MIN == 0.9
    light, albedo, index, depth, nz = _meter_frame()
    s = R.meter_stats(light, albedo, index, depth, set(), blocks_across=12, normal_z=nz, haze_indices={HAZE_INDEX})
    assert s["metered"] == "facade" and s["incident_p50"] == pytest.approx(19.0)       # the facade rule is unchanged
    assert s["ground_p50"] == pytest.approx(265.0) and s["ground_blocks_used"] == 36   # the far ground is left out
    no_haze = R.meter_stats(light, albedo, index, depth, set(), blocks_across=12, normal_z=nz)
    assert no_haze["ground_blocks_used"] == 48 and no_haze["incident_p50"] == pytest.approx(19.0)
    assert "ground_p50" not in R.meter_stats(light, albedo, index, depth, set(), blocks_across=12)
    limits = (-10.3808, 3.0)
    ev, raw, at_limit, rec = R.exterior_exposure(19.0, 265.0, 0.9, limits)
    assert rec["ground_cap"] is True and raw == pytest.approx(math.log2(0.9 / 265.0) + 1.5, abs=1e-3)
    assert ev == pytest.approx(-40 / 6) and not at_limit                               # -6.70 rounded to 1/6
    assert rec["ev_facade"] == pytest.approx(-4.333333) and rec["ev_ground"] == pytest.approx(-8.2019, abs=1e-3)
    assert ev <= rec["ev_ground"] + rec["ground_headroom_stops"] + R.EXPOSURE_STEP / 2
    sunlit = R.exterior_exposure(110.0, 265.0, 0.9, limits)
    assert sunlit[:3] == R.exposure_from(110.0, 0.9, limits) and sunlit[3]["ground_cap"] is False
    for ground in (None, 0.0, float("nan")):
        none = R.exterior_exposure(19.0, ground, 0.9, limits)
        assert none[:3] == R.exposure_from(19.0, 0.9, limits) and none[3]["ground_cap"] is False
    # real02 (P4a, the CPU shim re-meter): ext_1 14.1 / ground 176.5 is capped to -6.17; ext_3 169.4 / 210.7 is not
    assert R.exterior_exposure(14.145, 176.54, 0.9, limits)[0] == pytest.approx(-37 / 6)
    assert R.exterior_exposure(169.41, 210.71, 0.9, limits)[0] == R.exposure_from(169.41, 0.9, limits)[0] == -7.5
    # Look._decide records the cap for an exterior view and leaves an interior view as it was
    look = object.__new__(R.Look)
    look.scene, look.windows, look.haze, look.look_from = {}, set(), {HAZE_INDEX}, None
    look.exposure_mode, look.exposure_value, look.target, look.wb_mode = "auto", None, 0.9, "off"
    look.limits, look.floor_shift, look.mood, look.ev_offset = (-2.0, 3.0), 8.3808, "warm daylight", 0.0
    seen = []

    def meter(scene, cam, out, res, windows, haze=()):
        seen.append(haze)
        base = {"seconds": 0.2, "resolution": [8, 4], "samples": 16, "blocks": 32, "blocks_used": 8, "block_px": 1,
                "interior_frac": 0.3, "illuminant": [1.0, 1.0, 1.0], "incident_p50": 19.0}
        if cam.get("wenart_camera_kind") == "exterior":
            base.update(metered="facade", ground_p50=265.0, ground_blocks_used=12)
        return base
    monkeypatch.setattr(R, "meter_camera", meter)
    ext = types.SimpleNamespace(name="ext_3", get={"wenart_camera_kind": "exterior"}.get)
    rec = look.decide(ext, tmp_path, (64, 36))
    assert rec["ev"] == pytest.approx(-40 / 6) and rec["ground_cap"] is True
    assert rec["ev_facade"] == pytest.approx(-4.333333)
    assert rec["meter"]["ground_blocks_used"] == 12 and seen == [{HAZE_INDEX}] and rec["lighting_dark"] is None
    room = types.SimpleNamespace(name="cam_r_1", get={"wenart_camera_kind": "interior", "wenart_room": "r"}.get)
    rec = look.decide(room, tmp_path, (64, 36))
    assert "ground_cap" not in rec and rec["ev"] == R.exposure_from(19.0, 0.9, look.view_limits())[0]
    from wenart.blender import schemas

    props = schemas.EXPOSURE["properties"]
    assert {"ev_facade", "ev_ground", "ground_p50", "ground_headroom_stops", "ground_cap", "ground_rule",
            "wb_rig_kelvin_source", "wb_rig_share_p50"} <= set(props)


def test_fixround_p4b_the_lawn_is_the_green_ground_in_front_of_the_haze():
    """The lawn record of an exterior view (``lawn_mask`` / ``lawn_record``, the GPU pin of its saturation): surface
    hits facing up with a green albedo, nearer than the haze shell; not the facade, the grey paving, the far ground
    behind the shell or the sky."""
    import numpy as np

    h, w = 10, 10
    albedo = np.full((h, w, 3), 0.4)
    albedo[5:, :] = (0.12, 0.2, 0.06)                 # the grass (Grass004-like)
    albedo[5:, 8:] = (0.3, 0.3, 0.3)                  # grey paving
    normal = np.zeros((h, w, 3))
    normal[5:, :, 2] = 1.0
    depth = np.full((h, w), 10.0)
    depth[:2] = 1e10                                  # the sky
    depth[5:7, :] = 400.0                             # far grass behind the shell
    index = np.zeros((h, w))
    depth[2, 0], index[2, 0] = 60.0, HAZE_INDEX
    mask = R.lawn_mask(albedo, normal, depth, index, {HAZE_INDEX})
    want = np.zeros((h, w), dtype=bool)
    want[7:, :8] = True
    assert np.array_equal(mask, want)
    assert R.lawn_mask(albedo, normal, depth)[5:7, :8].all()             # no haze: the far grass counts
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[...] = (110, 140, 80)
    rec = R.lawn_record(img, mask)
    assert rec == {"px_share": 0.24, "saturation": pytest.approx((140 - 80) / 140, abs=1e-4),
                   "median": pytest.approx(R.masked_median(img, mask), abs=1e-4)}
    assert R.lawn_record(img, np.zeros((h, w), dtype=bool)) is None


def test_fixround_p4b_gpu_orange_check_covers_the_mixed_views(tmp_path, monkeypatch):
    """The verifier's better fix of the P4b orange finding: the GPU check covered only views with a rig share of 0.8 or
    more, and P4b's mixed halls and baths (0.44-0.65) read 1.40-1.69 unchecked. The views from 0.4 are checked against
    the daylight walls of their kind plus 0.15. Fails on 11949a9 (a share-0.5 view at 2.5 passed)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.RIG_CHECK_SHARE == 0.4 and gpu.RIG_ROOM_ABOVE_DAY == 0.15
    day = {"cam_r_bed_1": ("r_bed", 1.29, 0.0), "cam_r_bed_2": ("r_bed", 1.31, 0.0)}      # real03's lit greige

    def check(case, views):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / case, views, ("r_bath",)))
    with pytest.raises(AssertionError, match="cam_r_hall_1"):
        check("mixed", {**day, "cam_r_hall_1": ("r_hall", 1.69, 0.62)})                # giris_holu_3_1 in P4b
    check("mixed_fixed", {**day, "cam_r_hall_1": ("r_hall", 1.42, 0.49)})           # ruzgarlik_1 predicted
    with pytest.raises(AssertionError, match="cam_r_hall_1"):
        check("over", {**day, "cam_r_hall_1": ("r_hall", 1.46, 1.0)})               # 0.16 over 1.30
    check("under_04", {**day, "cam_r_hall_1": ("r_hall", 2.0, 0.35),                # under 0.4: not checked
                       "cam_r_hall_2": ("r_hall", 1.40, 1.0)})


def test_fixround_p4b_gpu_named_sky_views_pass_when_their_sky_already_qualifies(tmp_path, monkeypatch):
    """The exterior ground cap renders the shaded-facade views darker, so a named view of ``SKY_PULLED_VIEWS`` may need
    no sky pull: it passes when its rendered sky already qualifies (``render.sky_pull_qualifies``), and still fails
    when the sky is over the shoulder and not pulled. Fails on 11949a9 (k 0 failed whatever the sky)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}}}

    def project(ext_2):
        return "real02", scene, {"renders": [{"camera": "ext_2", "room_id": None, "sky_pull": ext_2}]}
    blue = _sky(0, before=(0.66, 0.14), tried=[])
    gpu.test_sky_and_window_pulls_reach_their_targets(project(blue))
    with pytest.raises(AssertionError, match="ext_2.*not pulled"):
        gpu.test_sky_and_window_pulls_reach_their_targets(project(_sky(0, before=(0.86, 0.06), tried=[])))


def test_fixround_p4b_gpu_pull_glazing_and_exterior_checks(tmp_path, monkeypatch):
    """CPU replays of the three new GPU checks: a window pull that kept clipped panes although a clip-free k near the
    walls was tried fails (P4b's yasama_8_3); the named real03 interior-glazing views fail over 0.3 of their walls and
    without a record; an exterior view over its ground EV plus the headroom, or with a bleached lawn, fails; a minor
    lighting_dark view is not dark for the hall check."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    # the window pull
    wall, rows = P4B_PULLS["cam_r_L0_yasama_8_3"]
    tried = [{"k": k, "clip": c, "median": m, "p90": p} for k, c, m, p in rows]

    def pulls(k, clip_after):
        return "real03", {}, {"renders": [{"camera": "cam_r_L0_yasama_8_3", "room_id": "r_L0_yasama_8",
                                           "window_pull": {"k": k, "tried": tried, "wall_median": wall,
                                                           "clip_after": clip_after, "rule": "r"}}]}
    gpu.test_window_pull_takes_an_unclipped_k_when_one_was_tried(pulls(2, 0.004))
    with pytest.raises(AssertionError, match="cam_r_L0_yasama_8_3"):
        gpu.test_window_pull_takes_an_unclipped_k_when_one_was_tried(pulls(1, 0.1386))     # P4b
    gpu.test_window_pull_takes_an_unclipped_k_when_one_was_tried(pulls(0, 0.004))           # unclipped as rendered
    with pytest.raises(AssertionError, match="cam_r_L0_yasama_8_3"):
        gpu.test_window_pull_takes_an_unclipped_k_when_one_was_tried(pulls(0, 0.307))       # clipped, not pulled
    # the interior glazing of the named views
    names = gpu.INTERIOR_GLAZING_VIEWS["real03"]
    assert gpu.INTERIOR_GLAZING_MAX_DELTA == 0.3 and "cam_r_L0_yasama_8_3" in names

    def glazing(delta, missing=()):
        renders = []
        for cam in names:
            e = {"camera": cam, "room_id": "r"}
            if cam not in missing:
                e["interior_glazing"] = {"pane_rb": 1.29 + delta, "wall_rb": 1.29, "delta_rb": delta,
                                         "windows": ["win_L0_055"], "pane_px": 900, "rule": "r"}
            renders.append(e)
        return "real03", {}, {"renders": renders}
    gpu.test_interior_glazing_keeps_one_white_point(glazing(0.2))
    with pytest.raises(AssertionError, match="two white points"):
        gpu.test_interior_glazing_keeps_one_white_point(glazing(0.53))                  # yasama_8_3 in P4b
    with pytest.raises(AssertionError, match="no interior_glazing record"):
        gpu.test_interior_glazing_keeps_one_white_point(glazing(0.1, missing=names[:1]))
    # the exterior views
    def ext(ev, lawn_sat, ground_ev=-8.2, share=0.4):
        x = {"mode": "auto", "ev": ev, "ev_offset": 0.0, "at_limit": False, "meter": {"metered": "facade"},
             "ev_facade": -4.33, "ev_ground": ground_ev, "ground_headroom_stops": 1.5, "ground_cap": True}
        return "real03", {}, {"renders": [{"camera": "ext_3", "room_id": None, "exposure": x,
                                           "lawn": {"px_share": share, "saturation": lawn_sat, "median": 0.5}}]}
    gpu.test_exterior_views_cap_the_ground_and_keep_the_lawn_green(ext(-6.667, 0.34))
    with pytest.raises(AssertionError, match="over the ground EV"):
        gpu.test_exterior_views_cap_the_ground_and_keep_the_lawn_green(ext(-4.333, 0.34))      # P4b's ext_3
    with pytest.raises(AssertionError, match="bleached lawn"):
        gpu.test_exterior_views_cap_the_ground_and_keep_the_lawn_green(ext(-6.667, 0.11))
    gpu.test_exterior_views_cap_the_ground_and_keep_the_lawn_green(ext(-6.667, 0.11, share=0.05))   # little lawn
    into_sun = ext(-6.167, 0.246, ground_ev=-7.619)                 # real02's ext_1 (shim), 6 degrees off the sun
    into_sun[2]["renders"][0]["sky_pull"] = {"into_sun": True, "sun_offset_deg": 6.01}
    gpu.test_exterior_views_cap_the_ground_and_keep_the_lawn_green(into_sun)
    assert gpu.LAWN_SAT_MIN == 0.25 and gpu.LAWN_MIN_SHARE == 0.10
    # a minor lighting_dark (under one exposure step) is not dark
    minor = R.lighting_dark_entry("cam_r_h_1", "r_h", 3.01, 3.0, (-2.0, 3.0))
    major = R.lighting_dark_entry("cam_r_h_1", "r_h", 3.5, 3.0, (-2.0, 3.0))
    assert not gpu._dark({"exposure": {"lighting_dark": minor}}) and gpu._dark({"exposure": {"lighting_dark": major}})
    assert not gpu._dark({"exposure": {"lighting_dark": None}})


# --------------------------------------------------------------------------
# Pass before P5 (17 Oct 2026): the review of the fix round after P4b
# --------------------------------------------------------------------------

# The pod records the review replayed (render_manifest.json window_pull): the walls, the panes as rendered (clip,
# median, p90) and the tried k (clip, median, p90). P4a real02 (runs/20261017-072801-full), P4b real03
# (runs/20261017-091212-full).
P5_PULLS = {
    "real02/cam_r_L1_teras_2_2": (0.37, (0.0, 0.4787, 0.6516), [(1, 0.0, 0.3348, 0.5129)]),
    "real03/cam_r_L0_yasama_3": (0.4906, (0.0, 0.5614, 0.6639), [(1, 0.0, 0.4129, 0.5281)]),
    "real03/cam_r_L0_yasama_4_1": (0.4668, (0.0, 0.537, 0.6702), [(1, 0.0, 0.3882, 0.5348)]),
    "real03/cam_r_L0_yasama_8_3": (0.4855, (0.307, 0.7288, 1.0),
                                   [(1, 0.1377, 0.6088, 0.9818), (2, 0.0, 0.467, 0.9381)]),
    "real03/cam_r_L0_ebeveyn_odasi_5_3": (0.4783, (0.367, 0.6849, 0.9994),
                                          [(1, 0.0112, 0.5536, 0.9762), (2, 0.0, 0.4041, 0.9308)]),
    "real03/cam_r_L0_ebeveyn_odasi_6_2": (0.5091, (0.3442, 0.7469, 0.9992),
                                          [(1, 0.011, 0.6315, 0.9619), (2, 0.0, 0.4895, 0.9109)]),
    "real03/cam_r_L0_ruzgarlik_2": (0.4686, (0.0431, 0.5382, 0.979), [(1, 0.0028, 0.3907, 0.9348)]),
    "real02/cam_r_L-1_mutfak_1": (0.5984, (0.3434, 0.8502, 0.9967),
                                  [(1, 0.0, 0.7679, 0.9583), (2, 0.0, 0.6567, 0.9062), (3, 0.0, 0.5201, 0.8416)]),
}


def _p5_cands(rows):
    return [{"k": k, "clip": c, "median": m, "p90": p} for k, c, m, p in rows]


def test_pass_p5_panes_fine_as_rendered_are_not_pulled_under_their_walls(tmp_path, monkeypatch):
    """The review of the fix round after P4b: ``choose_pull``'s second rule (an unclipped k slightly darker than the
    walls) had no check on the panes as rendered, so panes that were unclipped and on target went a stop under their
    walls (P4a real02 cam_r_L1_teras_2_2: 0.4787 against walls of 0.37 -> 0.3348 at k 1; P4b real03 yasama_3 and
    yasama_4_1 the same). It now applies only when the panes need a pull (``pull_needed``: clipped, or off the pane
    target); the clipped views keep the fix round's k. ``RenderRun.window_pull`` passes the as-rendered median and
    p90. Fails on adc3004 (k 1 for the three fine views and for the window_pull frame)."""
    import types

    import numpy as np

    chosen = {cam: R.choose_pull(_p5_cands(rows), wall, clip_before=before[0], pane_median=before[1],
                                 pane_p90=before[2])[0] for cam, (wall, before, rows) in P5_PULLS.items()}
    assert chosen == {"real02/cam_r_L1_teras_2_2": 0, "real03/cam_r_L0_yasama_3": 0, "real03/cam_r_L0_yasama_4_1": 0,
                      "real03/cam_r_L0_yasama_8_3": 2, "real03/cam_r_L0_ebeveyn_odasi_5_3": 2,
                      "real03/cam_r_L0_ebeveyn_odasi_6_2": 2, "real03/cam_r_L0_ruzgarlik_2": 1,
                      "real02/cam_r_L-1_mutfak_1": 3}
    wall, before, rows = P5_PULLS["real02/cam_r_L1_teras_2_2"]
    # the same record with clipped panes, or with panes off the target (p90 and median over it), takes k 1
    assert R.choose_pull(_p5_cands(rows), wall, clip_before=0.3, pane_median=before[1], pane_p90=before[2])[0] == 1
    assert R.choose_pull(_p5_cands(rows), wall, clip_before=0.0, pane_median=0.7, pane_p90=0.9)[0] == 1
    # pull_needed: not given -> True (the rules before this pass), clipped or off target -> True
    assert R.pull_needed(None) and R.pull_needed(0.02) and R.pull_needed(0.0, 0.7, 0.9)
    assert not R.pull_needed(0.0) and not R.pull_needed(0.01, 0.4787, 0.6516) and not R.pull_needed(0.0, 0.7, None)
    assert not R.pull_needed(0.0, 0.64, 0.95)                 # the median target alone is enough
    # the walls rule of the fix round after P4b without the as-rendered panes is unchanged
    assert R.choose_pull(_p5_cands(rows), wall)[0] == 1
    # window_pull end to end: walls (120, 110, 100) at 0.437, panes (200, 200, 200) at 0.784, unclipped, p90 under
    # the shoulder; k 1 (0.392) is unclipped at 0.90 of the walls but the panes need no pull
    index, channels, main = _glazing_frame()
    main[index == 5] = (200, 200, 200)
    walls = index == 0

    def fake_save(scene, result, path, ev, look=R.LOOK):
        return (main.astype(np.float64) * 0.5 ** round(-float(ev))).astype(np.uint8)
    monkeypatch.setattr(R, "save_display", fake_save)
    ctx = types.SimpleNamespace(scene=None, windows={5}, interior_windows=set(), haze=set(), pass_index={})
    run = types.SimpleNamespace(ctx=ctx, out=tmp_path, warnings=[])
    cam = types.SimpleNamespace(name="cam_r_L1_teras_2_2")
    products = {"index": index.astype(np.uint16)}
    record, weights, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert record["clip_before"] == 0.0 and record["pane_p90"] == pytest.approx(0.784, abs=2e-3)
    assert record["tried"][0]["median"] >= R.PULL_WALL_RATIO_MIN * record["wall_median"]
    assert record["k"] == 0 and weights is None and final is None
    # panes (220, 220, 220) at 0.863: unclipped but off the pane target (p90 over the shoulder, median over 0.65), so
    # they need a pull and k 1 (0.431, under the walls and over 0.8 of them) is taken by the second rule
    main[index == 5] = (220, 220, 220)
    record, _w, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert record["clip_before"] == 0.0 and record["pane_p90"] > R.PULL_P90_MAX
    assert R.PULL_WALL_RATIO_MIN * record["wall_median"] <= record["tried"][0]["median"] <= record["wall_median"]
    assert record["k"] == 1 and "slightly darker than the walls" in record["rule"]
    # ... and with clipped panes the same frame takes the unclipped k near the walls
    main[index == 5] = (252, 252, 252)
    record, _w, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert record["k"] >= 1 and record["clip_after"] <= R.PULL_MAX_CLIP


def test_pass_p5_gpu_pin_of_panes_pulled_without_need(tmp_path, monkeypatch):
    """CPU replay of ``test_window_pull_leaves_panes_that_need_no_pull`` (tests/gpu/test_render.py): the fix round's
    choice for P4a's cam_r_L1_teras_2_2 (k 1, panes under the walls although fine as rendered) fails; k 0, the
    clipped ruzgarlik_2 at k 1 and a pull that keeps the panes brighter pass. Fails on adc3004 (no such check)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)

    def manifest(cam, k, median_after):
        wall, before, rows = P5_PULLS[cam]
        wp = {"k": k, "ev": -float(k), "wall_median": wall, "clip_before": before[0], "pane_median": before[1],
              "pane_p90": before[2], "tried": _p5_cands(rows), "rule": "r"}
        if k:
            wp["pane_median_after"] = median_after
        return cam.split("/")[0], {}, {"renders": [{"camera": cam.split("/")[1], "window_pull": wp}]}
    with pytest.raises(AssertionError, match="cam_r_L1_teras_2_2"):
        gpu.test_window_pull_leaves_panes_that_need_no_pull(manifest("real02/cam_r_L1_teras_2_2", 1, 0.3348))
    gpu.test_window_pull_leaves_panes_that_need_no_pull(manifest("real02/cam_r_L1_teras_2_2", 0, None))
    gpu.test_window_pull_leaves_panes_that_need_no_pull(manifest("real03/cam_r_L0_ruzgarlik_2", 1, 0.3907))
    gpu.test_window_pull_leaves_panes_that_need_no_pull(manifest("real03/cam_r_L0_yasama_3", 1, 0.52))  # brighter


# P4b real03's interior-only views (their one window is interior glazing, so the P4b record's mask was the interior
# panes): the walls, the clip as rendered and the tried k (clip, median)
P5_INTERIOR = {
    "cam_r_L0_giris_holu_1": (0.4812, 0.127, [(1, 0.0342, 0.632), (2, 0.0, 0.4896)]),
    "cam_r_L0_giris_holu_2": (0.4553, 0.0842, [(1, 0.0435, 0.6748), (2, 0.0028, 0.5408)]),
    "cam_r_L0_giris_holu_3_1": (0.4582, 0.1316, [(1, 0.039, 0.4657), (2, 0.0, 0.3226)]),
    "cam_r_L0_kat_merdiveni_3": (0.4137, 0.2693, [(1, 0.0216, 0.7325), (2, 0.0, 0.6129)]),
    "cam_r_L0_yangin_merdiveni_2": (0.4817, 0.0144, [(1, 0.0, 0.0182)]),
    "cam_r_L0_giris_holu_2_1": (0.4642, 0.0011, [(1, 0.0, 0.29)]),
}


def test_pass_p5_clipped_interior_glazing_is_pulled_and_its_clip_recorded(tmp_path, monkeypatch):
    """The review of the fix round after P4b: the interior glazing was left out of the window pull and its clip was
    not recorded, so the halls that look through a daylit room to the sunlit outside went back to clipped panes
    (P4b real03 giris_holu_1 12.7 %, giris_holu_2 8.4 %, giris_holu_3_1 13.2 %) with no record of it. Clipped interior
    panes are now pulled by the smallest k that unclips them at 0.8 of the walls or more (``choose_interior_pull``;
    giris_holu_3_1 the lowest clip at that bound, as P4b; a lamp through the glass that only unclips far under the
    walls is not pulled), unclipped ones are not, and ``interior_glazing`` records ``clip`` as written and ``pull``.
    The window and interior pulls share their saves. Fails on adc3004 (no ``choose_interior_pull``, no
    ``interior_pull``, no ``clip``)."""
    import types

    import numpy as np

    chosen = {cam: R.choose_interior_pull([{"k": k, "clip": c, "median": m} for k, c, m in rows], wall, before)
              for cam, (wall, before, rows) in P5_INTERIOR.items()}
    assert {cam: k for cam, (k, _r) in chosen.items()} == {
        "cam_r_L0_giris_holu_1": 2, "cam_r_L0_giris_holu_2": 2, "cam_r_L0_giris_holu_3_1": 1,
        "cam_r_L0_kat_merdiveni_3": 2, "cam_r_L0_yangin_merdiveni_2": 0, "cam_r_L0_giris_holu_2_1": 0}
    assert chosen["cam_r_L0_giris_holu_3_1"][1].startswith("lowest interior pane clip")
    assert chosen["cam_r_L0_giris_holu_2_1"][1].startswith("interior panes unclipped as rendered")
    assert R.choose_interior_pull([{"k": 1, "clip": 0.0, "median": 0.05}], None, 0.2)[0] == 1     # no wall in view
    assert R.choose_interior_pull([{"k": 1, "clip": 0.3, "median": 0.05}], None, 0.4)[0] == 0     # ... never the lowest
    assert R.choose_interior_pull([], 0.5, None)[0] == 0
    # the lowest clip at the bound is taken only when it is under the clip as rendered (a lamp that k 1 does not help)
    assert R.choose_interior_pull([{"k": 1, "clip": 0.0144, "median": 0.45}], 0.4817, 0.0144)[0] == 0
    assert R.choose_interior_pull([{"k": 1, "clip": 0.0100001, "median": 0.45}], 0.4817, 0.0144)[0] == 1
    # the search stops at an unclipped k or under 0.8 of the walls
    assert R.interior_pull_search_done({"k": 2, "clip": 0.0, "median": 0.49}, 0.4812)
    assert R.interior_pull_search_done({"k": 2, "clip": 0.02, "median": 0.30}, 0.4582)
    assert not R.interior_pull_search_done({"k": 1, "clip": 0.0342, "median": 0.632}, 0.4812)
    assert not R.interior_pull_search_done({"k": 1, "clip": 0.0342, "median": 0.05}, None)
    # the frame: index 5 an exterior window (clipped), index 6 interior glazing whose panes clip (the sunlit outside
    # through the neighbouring room)
    index, channels, main = _glazing_frame()
    main[index == 6] = (252, 252, 252)
    walls = index == 0
    saved = []

    def fake_save(scene, result, path, ev, look=R.LOOK):
        saved.append(round(-float(ev)))
        return (main.astype(np.float64) * 0.5 ** round(-float(ev))).astype(np.uint8)
    monkeypatch.setattr(R, "save_display", fake_save)
    ctx = types.SimpleNamespace(scene=None, windows={5, 6}, interior_windows={6}, haze=set(),
                                pass_index={"win_L0_046": 5, "win_L0_008": 6})
    run = types.SimpleNamespace(ctx=ctx, out=tmp_path, warnings=[])
    cam = types.SimpleNamespace(name="cam_r_L0_giris_holu_1")
    products = {"index": index.astype(np.uint16)}
    saves = {}
    record, _w, final = R.RenderRun.window_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls, saves)
    assert record["k"] == 1 and np.array_equal(final[index == 6], main[index == 6]) and sorted(saves) == [1]
    ipull, iweights, ifinal = R.RenderRun.interior_pull(run, cam, {"ev": 0.0}, None, final, channels, products, walls,
                                                        saves)
    assert saved == [1]                                          # the interior pull reused the window pull's save
    assert ipull["k"] == 1 and ipull["clip_before"] == 1.0 and ipull["clip_after"] <= R.PULL_MAX_CLIP
    assert ipull["tried"] == [{"k": 1, "clip": 0.0, "median": pytest.approx(0.4941, abs=1e-3)}]
    assert (iweights[index != 6] == 0).all() and (ifinal[index == 6] < 252).all()
    assert np.array_equal(ifinal[index != 6], final[index != 6])      # the exterior pull and the walls as they were
    glazing = R.RenderRun.interior_glazing(run, ifinal, channels, products, walls, ipull)
    assert glazing["windows"] == ["win_L0_008"] and glazing["clip"] == 0.0 and glazing["pull"]["k"] == 1
    assert glazing["rule"].endswith("(pulled k 1)")
    # unpulled, the record says the panes are clipped as written
    assert R.RenderRun.interior_glazing(run, final, channels, products, walls)["clip"] == 1.0
    # the amber hall of the fix round after P4b (unclipped): not pulled, recorded with clip 0
    index, channels, main = _glazing_frame()
    saved.clear()
    ipull, iweights, ifinal = R.RenderRun.interior_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls)
    assert ipull["k"] == 0 and ipull["tried"] == [] and iweights is None and ifinal is None and saved == []
    glazing = R.RenderRun.interior_glazing(run, main, channels, products, walls, ipull)
    assert glazing["clip"] == 0.0 and glazing["pull"]["k"] == 0 and not glazing["rule"].endswith(")")
    # a lamp seen through the glass in a dark neighbouring room (P4b's yangin_merdiveni_2): 3 of 99 pane pixels clip
    # at any k up to 4 while the room is under 0.8 of the walls from k 1: one k is tried and nothing is pulled
    scene_lin = main.astype(np.float64)
    scene_lin[index == 6] = 40.0
    lamp = np.argwhere(index == 6)[:3]
    scene_lin[lamp[:, 0], lamp[:, 1]] = 4000.0
    lit = np.clip(scene_lin, 0, 255).astype(np.uint8)
    monkeypatch.setattr(R, "save_display", lambda scene, result, path, ev, look=R.LOOK: np.clip(
        scene_lin * 0.5 ** round(-float(ev)), 0, 255).astype(np.uint8))
    ipull, iweights, ifinal = R.RenderRun.interior_pull(run, cam, {"ev": 0.0}, None, lit, channels, products, walls)
    assert ipull["clip_before"] == pytest.approx(3 / 99, abs=1e-4) and len(ipull["tried"]) == 1
    assert ipull["k"] == 0 and ifinal is None and ipull["rule"].startswith("no k lowers the interior pane clip")
    # a view without interior glazing in the scene: no interior record
    ctx.interior_windows = set()
    assert R.RenderRun.interior_pull(run, cam, {"ev": 0.0}, None, main, channels, products, walls) == (None, None, None)
    from wenart.blender import schemas

    jsonschema = pytest.importorskip("jsonschema")
    prop = schemas.RENDER_ENTRY["properties"]["interior_glazing"]
    jsonschema.validate(glazing, prop)
    pulled = R.interior_glazing_record(ifinal if ifinal is not None else main, index == 6, walls, ["w"],
                                       {**ipull, "k": 1, "ev": -1.0, "clip_after": 0.0,
                                        "tried": [{"k": 1, "clip": 0.0, "median": 0.49}]})
    jsonschema.validate(pulled, prop)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({k: v for k, v in glazing.items() if k != "clip"}, prop)
    assert prop["oneOf"][1]["required"].count("clip") == 1


def test_pass_p5_gpu_pin_of_the_interior_glazing_clip(tmp_path, monkeypatch):
    """CPU replay of ``test_interior_glazing_pull_removes_clipping`` (tests/gpu/test_render.py): clipped interior
    panes written over ``PULL_MAX_CLIP`` plus the feather allowance although a tried k unclipped them near the walls
    fail (the fix round after P4b: giris_holu_1 not pulled, 12.7 %), as do an unclipped interior pane that was pulled
    and a record without ``clip``; a pull that unclipped them, and a lamp no k unclipped near the walls, pass. Fails
    on adc3004 (no such check)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)

    def manifest(cam, k, clip_written, drop=()):
        wall, before, rows = P5_INTERIOR[cam]
        pull = {"k": k, "ev": -float(k), "clip_before": before, "clip_after": clip_written, "wall_median": wall,
                "tried": [{"k": kk, "clip": c, "median": m} for kk, c, m in rows] if before > 0.01 else [],
                "rule": "r"}
        g = {"windows": ["win_L0_008"], "pane_px": 900, "pane_rb": 1.3, "wall_rb": 1.29, "delta_rb": 0.01,
             "clip": clip_written, "pull": pull, "rule": "r"}
        for key in drop:
            g.pop(key)
        return "real03", {}, {"renders": [{"camera": cam, "interior_glazing": g}]}
    gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_1", 2, 0.0))
    gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_2", 2, 0.0028 + 0.004))
    with pytest.raises(AssertionError, match="cam_r_L0_giris_holu_1.*clipped as written"):
        gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_1", 0, 0.127))
    gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_3_1", 1, 0.039))   # k 2 too dark
    gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_yangin_merdiveni_2", 0, 0.0144))   # a lamp
    with pytest.raises(AssertionError, match="unclipped interior panes"):
        gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_2_1", 1, 0.0))
    with pytest.raises(AssertionError, match="no clip or pull"):
        gpu.test_interior_glazing_pull_removes_clipping(manifest("cam_r_L0_giris_holu_1", 2, 0.0, drop=("clip",)))
    gpu.test_interior_glazing_pull_removes_clipping(("real03", {}, {"renders": [{"camera": "c", "interior_glazing":
                                                                                 None}]}))


def test_pass_p5_render_writes_the_interior_pull_and_records_it(tmp_path, monkeypatch):
    """``RenderRun.render`` wires the interior pull between the window pull and the sky pull: the written PNG has the
    clipped interior panes pulled, ``interior_glazing`` records their ``clip`` as written and the ``pull``, and the
    alt preview gets the interior pull's weights. Blender and the file helpers are stand-ins (the CPU tests have no
    Blender). Fails on adc3004 (the interior panes written clipped, no ``clip``) and on the mutations that drop
    ``final = ifinal``, the ``ipull`` argument of ``interior_glazing`` or ``(ipull, iweights)`` in the alt pulls."""
    import sys
    import types

    import numpy as np

    index, channels, main = _glazing_frame()
    main[index == 6] = (252, 252, 252)                    # the interior panes clip (the sunlit outside behind them)
    walls = index == 0

    def fake_save(scene, result, path, ev, look=R.LOOK):
        return (main.astype(np.float64) * 0.5 ** round(-float(ev))).astype(np.uint8)
    written, alt_pulls = {}, []
    monkeypatch.setattr(R, "save_display", fake_save)
    monkeypatch.setattr(R, "select_world", lambda scene, cam, room_type=None: "interior")
    monkeypatch.setattr(R, "set_view_clip", lambda cam, props, room_type=None: ({"end": 60.0}, 60.0))
    monkeypatch.setattr(R, "set_output", lambda scene, fmt, quality=90: None)
    monkeypatch.setattr(R, "read_exr", lambda path: channels)
    products = {"index": index.astype(np.uint16), "depth_mm": np.full(index.shape, 3000, dtype=np.uint16),
                "normal": np.zeros(index.shape + (3,), dtype=np.uint8), "index_values": [0, 5, 6],
                "depth": {"min": 1.0, "max": 5.0}, "index_stats": {}, "depth_legacy": None}
    monkeypatch.setattr(R, "pass_products", lambda ch, haze=(): products)
    monkeypatch.setattr(R, "read_display_png", lambda path: main.copy())
    monkeypatch.setattr(R, "view_walls", lambda prods: walls)
    monkeypatch.setattr(R, "write_png", lambda path, array, compression=None: written.__setitem__(Path(path).name,
                                                                                                   np.array(array)))
    monkeypatch.setattr(R, "encode_preview", lambda scene, png, path, quality=None: 100)
    monkeypatch.setattr(R, "save_preview", lambda scene, result, path, quality=None: 100)
    result = types.SimpleNamespace(save_render=lambda path, scene=None: None)
    monkeypatch.setitem(sys.modules, "bpy", types.SimpleNamespace(
        ops=types.SimpleNamespace(render=types.SimpleNamespace(render=lambda write_still=True: None)),
        data=types.SimpleNamespace(images=types.SimpleNamespace(get=lambda name: result))))

    class Cam(dict):
        name = "cam_r_L0_giris_holu_1"
        data = types.SimpleNamespace(clip_end=60.0, lens=18.0, sensor_width=36.0)

    class Scene(dict):
        camera = None
        render = types.SimpleNamespace(filepath="")
    look = {"ev": 0.0, "at_limit": False, "notes": [], "wb_temperature": 5600, "meter_seconds": 0.1}
    ctx = types.SimpleNamespace(
        scene=Scene(), res=(30, 20), haze_objects=[], haze=set(), windows={5, 6}, interior_windows={6},
        pass_index={"win_L0_046": 5, "win_L0_008": 6}, device="CPU", fingerprint="f",
        args=types.SimpleNamespace(preview_quality=None, alt_look="None", samples=16),
        look=types.SimpleNamespace(room_type=lambda cam: "hall", decide=lambda cam, out, res: dict(look),
                                   apply=lambda lk: None))
    run = object.__new__(R.RenderRun)
    run.ctx, run.out, run.entries, run.warnings, run.hidden, run.plugged, run.rendered = \
        ctx, tmp_path, {}, [], [], [], 0
    run.write_manifest = lambda: None
    run.alt_preview = lambda cam, lk, res, pulls, path: alt_pulls.extend(pulls) or 50
    R.RenderRun.render(run, Cam(), "k", "test")
    entry = run.entries["cam_r_L0_giris_holu_1"]
    png = written["cam_r_L0_giris_holu_1.png"]
    assert entry["window_pull"]["k"] == 1 and entry["window_pull"]["interior_pane_px"] == 99
    g = entry["interior_glazing"]
    assert g["pull"]["k"] == 1 and g["pull"]["clip_before"] == 1.0 and g["clip"] <= R.PULL_MAX_CLIP
    assert (png[index == 6] < 252).all() and (png[index == 5] < 252).all()
    assert np.array_equal(png[index == 0], main[index == 0])                 # the walls as rendered
    assert [k for k, _w in alt_pulls] == [1, 1] and (alt_pulls[1][1][index == 5] == 0).all()
    assert (alt_pulls[1][1][index == 6] > 0).all()
    from wenart.blender import schemas

    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(g, schemas.RENDER_ENTRY["properties"]["interior_glazing"])
    jsonschema.validate(entry["window_pull"], schemas.RENDER_ENTRY["properties"]["window_pull"])


# --------------------------------------------------------------------------
# Fix round after P5 (18 Oct 2026; pod P5, real04; the ``test_fixround_p5_*`` tests, each failing on 6e899cd or on the
# mutation its docstring names)
# --------------------------------------------------------------------------

def test_fixround_p5_gpu_orange_check_sorts_walls_by_room_type_and_skips_blocked_references(tmp_path, monkeypatch):
    """P5 real04 failed the orange check on cam_r_L-1_mutfak_3 at 1.223 against 1.208 with no cast in the image: the
    check called the kitchen ``tiled`` by its wet floor (its walls are the greige paint with a 0.6 m splashback) and
    took the tiled reference from one daylight view, the blocked cam_r_L1_banyo_1 (1.058). The kind is now the wall
    finish of the room type (bathroom / wc tiled) and the references come from unblocked views only. The values are
    P5's (painted daylight walls 1.38-1.70, median 1.515; kitchens 1.139-1.223 at rig share 0.60-0.68; baths
    1.068-1.103). Fails on 6e899cd (the kitchen, tiled by its wet floor, at 1.22 against 1.21) and with the mutation
    that keeps the blocked bath among the references (case 'bath_blocked_ref': a rig-lit bath at 1.45 against 1.21
    instead of the fixed 1.5). Fix round after P6b (23 Oct 2026), review: the views carry P5's rig temperatures
    (``wb_rig_kelvin``: the kitchens 2700 K, the baths 4000 K) and the really orange kitchen is back at its own share
    0.682: a mixed view under the 2700 K rig keeps the painted median + 0.15 (``warm rig``), so 1.70 fails at 1.67 (it
    passes against the warmest daylight view + 0.05 = 1.75 with the mutation that gives every mixed view the spread
    bound, the rule of 86cdeff)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    day = {"cam_r_L0_yatak_odasi_1": ("r_L0_yatak_odasi", 1.38, 0.0),
           "cam_r_L0_yatak_odasi_2": ("r_L0_yatak_odasi", 1.515, 0.0),
           "cam_r_L-1_salon_1": ("r_L-1_salon", 1.70, 0.0),
           "cam_r_L1_banyo_1": ("r_L1_banyo", 1.058, 0.0)}                      # the blocked view (P5)
    types = {"r_L0_yatak_odasi": "bedroom", "r_L-1_salon": "living", "r_L1_banyo": "bathroom",
             "r_L-1_mutfak": "kitchen", "r_L0_banyo": "bathroom", "r_L-1_banyo": "bathroom"}
    kitchens = {"cam_r_L-1_mutfak_1": ("r_L-1_mutfak", 1.139, 0.667), "cam_r_L-1_mutfak_2": ("r_L-1_mutfak", 1.158, 0.601),
                "cam_r_L-1_mutfak_3": ("r_L-1_mutfak", 1.223, 0.682)}
    baths = {"cam_r_L0_banyo_1": ("r_L0_banyo", 1.103, 1.0), "cam_r_L-1_banyo_1": ("r_L-1_banyo", 1.068, 1.0)}

    # fix round after P6b, review: P5's rig temperatures (render_manifest wb_rig_kelvin; source room)
    kelvin = {**{c: {"wb_rig_kelvin": 2700.0} for c in kitchens}, **{c: {"wb_rig_kelvin": 4000.0} for c in baths},
              "cam_r_L0_banyo_2": {"wb_rig_kelvin": 4000.0}}

    def check(case, views, entry_types=True, exposure=kelvin):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / case, views, room_types=types,
                                                               blocked={"cam_r_L1_banyo_1"}, entry_types=entry_types,
                                                               exposure=exposure))
    check("p5", {**day, **kitchens, **baths})
    # the scene manifest's room floors give the type when the entries carry none (a render before m13.2)
    check("p5_manifest_types", {**day, **kitchens, **baths}, entry_types=False)
    # a kitchen really orange still fails, against the painted bound (1.515 + 0.15; 1.52 + 0.15 in 8 bits). Fix round
    # after P6b (23 Oct 2026), review: at its own share 0.682, as a mixed view under the 2700 K rig (``warm rig``; the
    # spread bound, 1.70 + 0.05, is for a neutral rig only) ...
    with pytest.raises(AssertionError, match=r"cam_r_L-1_mutfak_3', 1.7, 'painted', 1.67, 0.682, 'warm rig'"):
        check("kitchen_orange", {**day, **kitchens, "cam_r_L-1_mutfak_3": ("r_L-1_mutfak", 1.70, 0.682)})
    # ... and with no rig temperature in its record
    with pytest.raises(AssertionError, match=r"cam_r_L-1_mutfak_3', 1.7, 'painted', 1.67, 0.682, 'warm rig'"):
        check("kitchen_orange_no_k", {**day, **kitchens, "cam_r_L-1_mutfak_3": ("r_L-1_mutfak", 1.70, 0.682)},
              exposure={})
    # the blocked bath is no reference: a rig-lit bath at 1.45 meets the fixed 1.5 (1.208 with the blocked reference)
    check("bath_blocked_ref", {**day, **baths, "cam_r_L0_banyo_2": ("r_L0_banyo", 1.45, 1.0)})
    # an unblocked daylight bath still sets the tiled reference
    with pytest.raises(AssertionError, match="cam_r_L0_banyo_2.*tiled"):
        check("bath_day_ref", {**day, **baths, "cam_r_L-1_banyo_2": ("r_L-1_banyo", 1.06, 0.0),
                               "cam_r_L0_banyo_2": ("r_L0_banyo", 1.45, 1.0)})
    assert gpu._wall_kind({"room_type": "wc"}, {}) == "tiled"
    assert gpu._wall_kind({"room_type": "kitchen"}, {}) == "painted"
    assert gpu._wall_kind({"room_id": "r_x"}, {"r_x": "bathroom"}) == "tiled"
    assert gpu._wall_kind({"room_type": "dining"}, {}) == "painted"


def _dotted_edge_frame():
    """A pulled view at 8 x 20 with the dotted edge of P5's roofs and pergola (bpy 5.2.2 shim of real04 at P5's k:
    every second edge pixel a haze-shell hit with a normal): rows 0-2 sky with a pure shell hit at (0, 0); a roof
    (rows 4-7, columns 0-7, 10 m, |N| 1) whose edge row 3 is half sky (|N| 0.5): sample 0 crossed the haze shell on
    the even columns (depth 40 m, the haze index) and reached the background on the odd ones; sky over columns 8-10
    and 12; a post (rows 4-7, column 11, 10 m); far ground behind the haze (rows 4-7, columns 13-19, 300 m, |N| 0.4)
    with a fully covered shell hit at (4, 16) and a hill line at row 3 (|N| 0.2, a shell hit at column 15); a shell
    hit at (3, 12) next to both the post and the far ground (|N| 0.3)."""
    import numpy as np

    h, w = 8, 20
    depth = np.full((h, w), 1e10)
    index = np.zeros((h, w))
    normal = np.zeros((h, w, 3))
    depth[0, 0], index[0, 0] = 40.0, HAZE_INDEX
    depth[4:, :8], index[4:, :8], normal[4:, :8] = 10.0, 7.0, (0.0, 0.0, 1.0)
    normal[3, :8] = (0.0, 0.0, 0.5)
    depth[3, 0:8:2], index[3, 0:8:2] = 40.0, HAZE_INDEX
    depth[4:, 11], index[4:, 11], normal[4:, 11] = 10.0, 8.0, (1.0, 0.0, 0.0)
    depth[4:, 13:], normal[4:, 13:] = 300.0, (0.0, 0.0, 0.4)
    depth[4, 16], index[4, 16] = 40.0, HAZE_INDEX
    normal[3, 13:] = (0.0, 0.0, 0.2)
    depth[3, 15], index[3, 15] = 40.0, HAZE_INDEX
    depth[3, 12], index[3, 12], normal[3, 12] = 40.0, HAZE_INDEX, (0.0, 0.0, 0.3)
    return {"ViewLayer.Depth.Z": depth, "ViewLayer.Object Index.X": index, "ViewLayer.Normal.X": normal[..., 0],
            "ViewLayer.Normal.Y": normal[..., 1], "ViewLayer.Normal.Z": normal[..., 2]}


def test_fixround_p5_a_shell_hit_at_a_roof_edge_takes_the_roofs_reference():
    """P5 real04's sky-pulled ext_1 (k 3) and teras_2_1 (k 4): a dotted white line along every roof, gutter and
    pergola edge. An edge pixel whose sample 0 crossed the haze shell while its other samples hit the roof is a shell
    hit with a normal: it took the reference of the other such edge pixels (|N| 0.5, its own), got weight 0 and kept
    its unpulled sky; every second edge pixel stayed white. It now takes the nearer surface group's reference (the
    roof, 1) and half the pull; a shell hit nearer the far ground, or as near to it as to a near surface, keeps the
    shell group (the far ground's own reference). Fails on 29e54d0 (weight 0) and with the mutation that never
    reassigns (``shell_edge_pixels`` returning nothing)."""
    import numpy as np

    channels = _dotted_edge_frame()
    depth, index, normal = _passes(channels)
    mask = R.sky_mask(depth, index, normal, {HAZE_INDEX})
    assert mask[0, 0] and mask[3, 1:8:2].all() and not mask[3, 0:8:2].any() and not mask[3, 12] and not mask[3, 15]
    weights, ring = R.sky_pull_weights(mask, normal, depth=depth, index=index, haze_indices={HAZE_INDEX})
    assert ring[3, 0:8:2].all() and ring[3, 12] and ring[3, 15] and ring[4, 16]
    assert weights[3, 0:8:2] == pytest.approx([0.5] * 4)                     # the roof's 1: half the pull
    assert weights[3, 1:8:2] == pytest.approx([0.5] * 4)                     # the background half: as before
    assert weights[3, 15] == pytest.approx(0.5) and weights[4, 16] == 0.0    # the far ground's 0.4 (shell group)
    assert weights[3, 12] == pytest.approx(0.25)                             # a tie: the shell group (0.4)
    assert (weights[4:, :8] == 0.0).all() and (weights[4:, 11] == 0.0).all() and (weights[4:, 13:] == 0.0).all()
    near = ~mask & np.isin(np.rint(index), [7.0, 8.0])
    far = ~mask & (depth > 140.0) & (depth < 1e9)
    shell = ~mask & (np.rint(index) == HAZE_INDEX)
    edge = R.shell_edge_pixels(shell & ring, near, far, R.SKY_REF_PX)
    assert sorted(zip(*np.nonzero(edge))) == [(3, 0), (3, 2), (3, 4), (3, 6)]
    assert not R.shell_edge_pixels(np.zeros_like(mask), near, far).any()
    # beyond max_px no surface decides: the candidate stays in the shell group
    lone = np.zeros_like(mask)
    lone[0, 19] = True
    assert not R.shell_edge_pixels(lone, near, far, 2).any()


def test_fixround_p5_the_sky_pull_blends_the_dotted_edge_and_records_no_dots(tmp_path, monkeypatch):
    """``RenderRun.sky_pull`` on the dotted-edge frame (``save_display`` stands in for Blender): the shell hits on the
    roof's edge take half the k 2 save like the background pixels between them, so no edge pixel stays brighter than
    the pulled sky, the roof and its neighbours; the record says ``edge_dot_px`` 0 of ``edge_px`` (``sky_edge_dots``,
    for the GPU check). With 29e54d0's weights (0 on those four pixels) the same blend has four dots. Fails on
    29e54d0 (no ``edge_dot_px``; the edge pixels unpulled)."""
    import types

    import numpy as np

    channels = _dotted_edge_frame()
    depth, index, normal = _passes(channels)
    mask = R.sky_mask(depth, index, normal, {HAZE_INDEX})
    h, w = depth.shape
    main = np.zeros((h, w, 3), dtype=np.uint8)
    main[...] = (224, 226, 228)                    # the near-white sky at the facade EV
    main[4:, :8] = (60, 62, 64)                    # the dark roof
    main[3, :8] = (190, 192, 194)                  # its edge as rendered: half sky, the bright part dominates (AgX)
    main[4:, 11] = (80, 80, 80)                    # the post
    main[3:, 13:] = (200, 205, 190)                # the far ground behind the haze, the hill line
    pure = mask & (np.abs(normal).sum(axis=-1) == 0)
    pulled = {1: (200, 212, 230), 2: (150, 172, 206), 3: (110, 128, 160)}

    def fake_save(scene, result, path, ev, look=R.LOOK):
        k = round(-4.0 - float(ev))
        img = (main.astype(np.float64) * 0.5 ** k).astype(np.uint8)
        img[pure] = pulled[k]
        return img

    run = types.SimpleNamespace(ctx=types.SimpleNamespace(scene=None, haze={HAZE_INDEX}), out=tmp_path, warnings=[])
    monkeypatch.setattr(R, "save_display", fake_save)
    record, weights, final = R.RenderRun.sky_pull(run, types.SimpleNamespace(name="cam_r_L1_teras_2_1"),
                                                  {"ev": -4.0}, None, main, channels)
    assert record["k"] == 2 and R.SKY_EDGE_NEAR_PX == R.SKY_RING_PX + 1 and R.SKY_EDGE_DOT_MARGIN == 0.05
    k2 = fake_save(None, None, None, -6.0)
    for col in range(8):                                                     # shell and background halves alike
        assert np.array_equal(final[3, col], np.rint(main[3, col] * 0.5 + k2[3, col] * 0.5).astype(np.uint8)), col
    assert record["edge_dot_px"] == 0 and record["edge_px"] > 0
    assert (record["edge_dot_px"], record["edge_px"]) == R.sky_edge_dots(final, mask, weights,
                                                                         R.sky_pull_weights(
                                                                             mask, normal, depth=depth, index=index,
                                                                             haze_indices={HAZE_INDEX})[1])
    # 29e54d0's weights: the four shell hits at the edge unpulled -> four dots
    old = weights.copy()
    old[3, 0:8:2] = 0.0
    _w, ring = R.sky_pull_weights(mask, normal, depth=depth, index=index, haze_indices={HAZE_INDEX})
    dots, edge = R.sky_edge_dots(R.blend_pull(main, k2, old), mask, old, ring)
    assert dots == 4 and edge == record["edge_px"]


def test_fixround_p5_sky_edge_dots_counts_dots_not_lines():
    """``sky_edge_dots`` counts an edge pixel brighter than the fully pulled sky, the surface the pull left alone and
    the edge pixels next to it; a connected light line (a sunlit coping, the soft line of an anti-aliased dark edge)
    is not a dot, nor is an edge pixel without both a sky and a surface within ``SKY_EDGE_NEAR_PX``."""
    import numpy as np

    h, w = 10, 12
    mask = np.zeros((h, w), dtype=bool)
    mask[:4] = True                                                          # sky rows 0-3
    ring = np.zeros((h, w), dtype=bool)
    ring[4:6] = True                                                         # the ring rows 4-5
    weights = np.where(mask, 1.0, 0.0)
    weights[4] = 0.5                                                         # the edge row, half pulled
    image = np.zeros((h, w, 3), dtype=np.uint8)
    image[:4] = (120, 130, 150)                                              # the pulled sky (0.5)
    image[4:] = (60, 60, 60)                                                 # the roof
    image[4, :] = (100, 100, 100)                                            # the edge row between them
    edge = 2 * w                                                             # both ring rows: sky and roof within 3 px
    assert R.sky_edge_dots(image, mask, weights, ring) == (0, edge)
    image[4, 3] = image[4, 7] = (230, 230, 230)                              # two dots
    assert R.sky_edge_dots(image, mask, weights, ring) == (2, edge)
    image[4, :] = (230, 230, 230)                                            # a connected light line: no dot
    assert R.sky_edge_dots(image, mask, weights, ring) == (0, edge)
    # a ring pixel with no surface within SKY_EDGE_NEAR_PX (a 6-row ring) is no edge pixel
    deep = np.zeros((h, w), dtype=bool)
    deep[4:] = True
    assert R.sky_edge_dots(image, mask, weights, deep)[1] == 0
    assert R.sky_edge_dots(image, np.zeros_like(mask), weights, ring) == (0, 0)


def test_fixround_p5_gpu_sky_edge_check_fails_on_dotted_edges(tmp_path, monkeypatch):
    """CPU replay of ``test_sky_pull_leaves_no_dotted_edges``: P5's pulls without the record fail (rendered before
    m13.4), the shim's m13.3 shares fail (a view over ``SKY_EDGE_DOT_VIEW_MAX``, the median over
    ``SKY_EDGE_DOT_MEDIAN_MAX``), the m13.4 shares pass, and a project without a pulled sky skips."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)

    def project(*pulls):
        renders = [{"camera": f"cam_{i}", "sky_pull": p} for i, p in enumerate(pulls)]
        return "real04", {}, {"renders": renders}
    m134 = [dict(_sky(3), edge_dot_px=4, edge_px=1924), dict(_sky(4), edge_dot_px=1, edge_px=1791)]
    gpu.test_sky_pull_leaves_no_dotted_edges(project(*m134))
    m133 = [dict(_sky(3), edge_dot_px=63, edge_px=1924), dict(_sky(4), edge_dot_px=26, edge_px=1791)]
    with pytest.raises(AssertionError, match="dotted sky edges"):
        gpu.test_sky_pull_leaves_no_dotted_edges(project(*m133))
    # one dotted view among clean ones: the view bound
    with pytest.raises(AssertionError, match="cam_2"):
        gpu.test_sky_pull_leaves_no_dotted_edges(project(*m134, dict(_sky(2), edge_dot_px=40, edge_px=1000)))
    with pytest.raises(AssertionError, match="before m13.4"):
        gpu.test_sky_pull_leaves_no_dotted_edges(project(_sky(3), *m134))
    with pytest.raises(pytest.skip.Exception):
        gpu.test_sky_pull_leaves_no_dotted_edges(project(_sky(0), None))
    assert gpu.SKY_EDGE_DOT_VIEW_MAX == 0.015 and gpu.SKY_EDGE_DOT_MEDIAN_MAX == 0.005


P5_ANCHOR = [1.106758, 0.981679, 0.867122]      # real04's project white point (P3's 5,635 K, P5 render_manifest)


def test_fixround_p5_the_view_takes_the_tint_of_its_own_daylight():
    """P5 real04's six sunlit L0 bedroom views read olive (wall display G/((R+B)/2) 1.048-1.066, M12 1.007-1.017):
    their daylight is mostly sunlight bounced off the green ground, while the project anchor was metered on the
    terrace. bpy 5.2.2 shim of real04 (the P3 pre-flight scene, P5's anchor): the daylight green ratio
    G/sqrt(RB) of yatak_odasi_1 1.402, yatak_odasi_3 1.348, e_yatak_odasi_1 1.321, salon_1 1.178, oyun_1 1.022;
    the anchor's 1.002. The view's white point takes ``(day ^ (1 - r) / anchor) ^ (1 - share)`` on its G (walls
    1.076 -> 1.021, 1.057 -> 1.019, 1.078 -> 1.040, 1.037 -> 1.019 on the shim) and keeps its R/B (the temperature).
    Fails on 29e54d0 (no ``view_tint_gain``)."""
    assert R.green_ratio([1.0, 1.0, 1.0]) == 1.0 and R.green_ratio([1.0, 0.0, 1.0]) is None
    assert R.green_ratio(None) is None and R.green_ratio([1.0, float("nan"), 1.0]) is None
    assert R.green_ratio(P5_ANCHOR) == pytest.approx(1.002086, abs=1e-5)
    for day, gain in ((1.402053, 1.243065), (1.347611, 1.211474), (1.321004, 1.195872), (1.177723, 1.109878),
                      (1.021969, 1.012119)):
        assert R.view_tint_gain(P5_ANCHOR, day, 0.35) == pytest.approx(gain, abs=1e-5), day
    # by the daylight share (the rig part keeps the rig's colour), clamped, and none without a daylight
    assert R.view_tint_gain(P5_ANCHOR, 1.402053, 0.35, 0.5) == pytest.approx(1.243065 ** 0.5, abs=1e-5)
    assert R.view_tint_gain(P5_ANCHOR, 1.402053, 0.35, 1.0) == 1.0
    assert R.view_tint_gain(P5_ANCHOR, 3.0, 0.35) == R.WB_TINT_GAIN_MAX == 1.3
    assert R.view_tint_gain(P5_ANCHOR, 0.3, 0.35) == pytest.approx(1 / 1.3, abs=1e-6)
    assert R.view_tint_gain(P5_ANCHOR, None, 0.35) == 1.0 and R.view_tint_gain(P5_ANCHOR, 1.4, 1.0) == 1.0
    assert R.view_tint_gain([1.0, 0.0, 1.0], 1.4, 0.35) == 1.0
    # the tinted white point keeps R/B (its temperature) and luminance 1; its own daylight then leaves the anchor's
    # tint: (day / wp) has the anchor's day^r green ratio
    wp = R.tinted_whitepoint(P5_ANCHOR, 1.243065)
    assert wp[0] / wp[2] == pytest.approx(P5_ANCHOR[0] / P5_ANCHOR[2], abs=1e-5)
    assert R.luminance(wp) == pytest.approx(1.0, abs=1e-5)
    assert R.green_ratio(wp) == pytest.approx(1.402053 ** 0.65, abs=1e-4)
    assert R.tinted_whitepoint(P5_ANCHOR, 1.0) == pytest.approx(P5_ANCHOR, abs=2e-6)
    assert R.WB_TINT_RULE.startswith("the view's own daylight tint")


def test_fixround_p5_view_white_tints_the_daylight_views_only(tmp_path, monkeypatch):
    """``Look._view_white`` with stand-ins: a daylight view (share 0) gets the anchor with its daylight's tint, a
    mixed view the rig mix with the tint by its daylight share, a view without daylight (the rig alone) and a view
    under the exterior sky keep their white points, and a scene without a rig tints by the metered light. Every
    interior view records ``wb_day_green`` and ``wb_view_tint_gain``. Fails on 29e54d0 (the anchor exactly)."""
    import types

    look = object.__new__(R.Look)
    look.scene, look.windows, look.haze, look.room_types = {}, set(), set(), {}
    look.project = {"residual": 0.35}
    green_day = [1.0, 1.402053, 1.0]                                        # green ratio 1.402053
    meters = []
    monkeypatch.setattr(R, "rig_objects", lambda scene: ["rig"])
    monkeypatch.setattr(R, "rig_lights", lambda scene: [("r_bed", 2700.0, 2.5)])
    monkeypatch.setattr(R, "hide_objects", lambda objs: [])
    monkeypatch.setattr(R, "unhide_objects", lambda saved: None)
    monkeypatch.setattr(R, "meter_camera", lambda *a, **k: dict(meters.pop(0), seconds=0.1))
    monkeypatch.setattr(R, "kelvin_whitepoint", lambda scene, k: R.normalise_whitepoint(WP_2700K))

    def view(day, all_light=None, kind="interior", room="r_bed"):
        cam = types.SimpleNamespace(name=f"cam_{room}_1", get={"wenart_room": room, "wenart_camera_kind": kind}.get)
        rec = {"whitepoint": list(P5_ANCHOR), "meter_seconds": 1.0}
        meters.append({"illuminant": day, "incident_p50": 0.02})
        look._view_white(cam, rec, {"illuminant": all_light or day, "incident_p50": 0.02}, tmp_path, (64, 36))
        meters.clear()
        return rec
    rec = view(green_day)                                                    # share 0: the daylight bedroom
    assert rec["wb_rig_share"] == 0.0 and rec["wb_day_green"] == pytest.approx(1.402053)
    assert rec["wb_view_tint_gain"] == pytest.approx(1.243065, abs=1e-5)
    assert rec["whitepoint"] == pytest.approx(R.tinted_whitepoint(P5_ANCHOR, rec["wb_view_tint_gain"]), abs=1e-9)
    assert "daylight tint" in rec["wb_view_rule"]
    rec = view(green_day, [4.0, 4.0 * 1.402053 / 2 + 1.0, 3.0])                # share 0.66 (luminance), mixed
    share = rec["wb_rig_share"]
    assert share == pytest.approx(0.66, abs=0.01) and rec["wb_view_tint_gain"] == R.view_tint_gain(P5_ANCHOR, rec["wb_day_green"], 0.35,
                                                                               share)
    rig = R.normalise_whitepoint(WP_2700K)
    assert rec["whitepoint"] == pytest.approx(R.tinted_whitepoint(R.mixed_whitepoint(P5_ANCHOR, rig, share, 0.35, 0.0),
                                                                  rec["wb_view_tint_gain"]), abs=1e-9)
    assert rec["wb_view_rule"].startswith(R.WB_VIEW_RULE)
    rec = view(None, [0.1, 0.1, 0.1])                                        # the rig alone: no daylight
    assert rec["wb_rig_share"] == 1.0 and rec["wb_day_green"] is None and rec["wb_view_tint_gain"] == 1.0
    assert rec["whitepoint"] == pytest.approx(R.mixed_whitepoint(P5_ANCHOR, rig, 1.0, 0.35, 0.0), abs=1e-9)
    rec = view(green_day, kind="exterior")                                   # under the exterior sky: the anchor
    assert rec["whitepoint"] == P5_ANCHOR and "wb_view_tint_gain" not in rec
    monkeypatch.setattr(R, "rig_objects", lambda scene: [])                  # no rig: the metered light is daylight
    rec = view(green_day)
    assert rec["wb_rig_share"] is None and rec["wb_view_tint_gain"] == pytest.approx(1.243065, abs=1e-5)
    assert rec["whitepoint"] == pytest.approx(R.tinted_whitepoint(P5_ANCHOR, rec["wb_view_tint_gain"]), abs=1e-9)
    # the project daylight's own tint (the anchor's green ratio to the power 1 / (1 - r)): the anchor
    rec = view([1.0, R.green_ratio(P5_ANCHOR) ** (1 / 0.65), 1.0])
    assert rec["wb_view_tint_gain"] == pytest.approx(1.0, abs=2e-6)
    assert rec["whitepoint"] == pytest.approx(P5_ANCHOR, abs=1e-5)


def test_fixround_p5_gpu_white_point_check_reads_the_recorded_tint(tmp_path, monkeypatch):
    """CPU replay of ``test_views_keep_the_project_white_point_or_mix_it_with_the_rig`` with m13.4 records: a daylight
    view with its tinted anchor passes; one whose white point is the plain anchor although its daylight is green, one
    whose recorded gain does not follow its recorded daylight green ratio, and an interior view without the record
    (an m13.3 render) fail."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    gain = R.view_tint_gain(P5_ANCHOR, 1.402053, 0.35)
    tinted = R.tinted_whitepoint(P5_ANCHOR, gain)
    mixed = R.mixed_whitepoint(P5_ANCHOR, RIG_2700K, 0.8, 0.35)
    mgain = R.view_tint_gain(P5_ANCHOR, 1.05, 0.35, 0.8)
    base = [_wb_entry("ext_2", None, P5_ANCHOR, anchor=P5_ANCHOR, world="wenart_world_exterior"),
            _wb_entry("cam_r_b_1", "r_b", R.tinted_whitepoint(mixed, mgain), share=0.8, anchor=P5_ANCHOR, shift=90.0,
                      day_green=1.05, gain=mgain)]
    good = base + [_wb_entry("cam_r_s_1", "r_s", tinted, share=0.0, anchor=P5_ANCHOR, day_green=1.402053, gain=gain)]
    gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P5_ANCHOR, good))
    plain = base + [_wb_entry("cam_r_s_1", "r_s", P5_ANCHOR, share=0.0, anchor=P5_ANCHOR, day_green=1.402053,
                              gain=gain)]
    with pytest.raises(AssertionError, match="cam_r_s_1"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P5_ANCHOR, plain))
    off = base + [_wb_entry("cam_r_s_1", "r_s", tinted, share=0.0, anchor=P5_ANCHOR, day_green=1.2, gain=gain)]
    with pytest.raises(AssertionError, match="tint gain off the recorded daylight green ratio"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P5_ANCHOR, off))
    old = _wb_entry("cam_r_s_1", "r_s", P5_ANCHOR, share=0.0, anchor=P5_ANCHOR)
    for key in ("wb_day_green", "wb_view_tint_gain"):
        old["exposure"].pop(key)
    with pytest.raises(AssertionError, match="before m13.4"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(_wb_project(P5_ANCHOR, base + [old]))


def test_fixround_p5_gpu_olive_check_reads_the_daylight_walls(tmp_path, monkeypatch):
    """CPU replay of ``test_daylight_walls_are_not_olive``: painted daylight walls at the shim's tinted values
    (G/((R+B)/2) 1.019-1.040) pass; an olive bedroom (1.078, the shim with the project white point) fails; a bath
    (tiled), a rig-lit hall and a blocked daylight view are not judged."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)

    def rgb(green):                                                           # R 120, B 100: G = 110 x green
        return (120, round(110 * green), 100)
    types_ = {"r_bed": "bedroom", "r_liv": "living", "r_bath": "bathroom", "r_hall": "hall"}
    views_ = {"cam_r_bed_1": ("r_bed", 1.2, 0.0), "cam_r_liv_1": ("r_liv", 1.2, 0.0),
              "cam_r_bath_1": ("r_bath", 1.2, 0.0), "cam_r_hall_1": ("r_hall", 1.2, 0.9),
              "cam_r_bed_2": ("r_bed", 1.2, 0.0)}
    colours = {"cam_r_bed_1": rgb(1.021), "cam_r_liv_1": rgb(1.019), "cam_r_bath_1": rgb(1.10),
               "cam_r_hall_1": rgb(1.10), "cam_r_bed_2": rgb(1.10)}

    def check(case, colours, blocked=("cam_r_bed_2",)):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_daylight_walls_are_not_olive(_wall_views(tmp_path / case, views_, room_types=types_, blocked=blocked,
                                                          entry_types=True, rgb=colours))
    check("tinted", colours)
    with pytest.raises(AssertionError, match=r"cam_r_bed_1', \(1\.08"):              # 119 / 110 in 8 bits
        check("olive", dict(colours, cam_r_bed_1=rgb(1.078)))
    with pytest.raises(AssertionError, match="cam_r_bed_2"):                   # the same view unblocked
        check("unblocked", colours, blocked=())
    assert gpu.DAYLIGHT_WALL_GREEN_MAX == 1.06
