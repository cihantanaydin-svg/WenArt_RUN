"""Fix round after P6a (22 Oct 2026; pod P6a, real04, runs/20261022-135644-m13_p6; render code m13.5; track R_render):
CPU tests of the render changes and of the GPU checks that come with them. Each test fails on BASE 52d4bb8 (P6a's
code 8e8cc97 with its results) or on the mutation its docstring names. No Blender needed.

- The sky pull never takes a crushed sky (``render.SKY_PULL_MEDIAN_MIN``, ``render.sky_pull_candidate_ok``): P6a's
  ext_5, 5.4 degrees off the sun, went to k 6 with the sky median at 0.109 (a near-black band over the aerial view);
  every other pull of P4a real02, P4b real03, P5 and P6a real04 keeps its k, and the search stops at the first save
  under the floor. The GPU sky check holds a pulled sky to the floor.
- Cycles' per-sample clamps are set and recorded (``render.CLAMP_DIRECT`` 0, ``render.CLAMP_INDIRECT`` 10: Cycles'
  own defaults, read back from P6a's real04.blend), and enter the render key only when not the default.
- The daylight-only metering pass measures the light on the walls (``render.meter_stats`` ``wall_illuminant``) and
  the view's tint follows the walls' green (``render.daylight_green``, ``WB_TINT_METER``); the gain rule is a recorded
  choice (``WB_TINT_KEEP_GREEN_RESIDUAL``: m13.4's, or the P6a verifier's with no green left on white), read back by
  the GPU white-point check; the olive check also holds the lower walls (no pink).
- The GPU index check's ray model: a library piece seen only as a sliver of its fitted box (P6a's office chair
  f_L0_041 and oval coffee table f_L1_024) gets a slack of ``LIBRARY_BOX_SLACK_SHARE`` per side; fixed equipment, a
  box seen on more of the frame and a moved mesh keep the strict rule.
- The GPU colour checks keep their per-view values (``gpu_check_values.json``): P6a's orange check passed and its
  values were lost.
"""
from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from test_m13_light import (HAZE_INDEX, P4A_SKY_TRIED, P5_ANCHOR, _gpu_render_module, _haze_frame, _wall_views,
                            _wb_entry, _wb_project)
from wenart.blender import render as R
from wenart.blender import schemas

# --------------------------------------------------------------------------
# The sky pull's median floor
# --------------------------------------------------------------------------

# P6a's ext_5 (runs/20261022-135644-m13_p6, real04, render_manifest.json sky_pull): before, and k 1-6 tried
P6A_EXT5_BEFORE = (0.8255, 0.0141)
P6A_EXT5_TRIED = [(1, 0.7325, 0.0209), (2, 0.6132, 0.0314), (3, 0.4678, 0.048), (4, 0.3249, 0.0588),
                  (5, 0.2048, 0.0741), (6, 0.109, 0.1034)]
# P6a's other pulls (real04 and its variant l-1b-acik-mutfak): (before, tried, chosen k)
P6A_SKY = {
    "cam_r_L1_teras_1": ((0.888, 0.0348), [(1, 0.8135, 0.0509), (2, 0.718, 0.0741), (3, 0.5953, 0.1111)], 3),
    "cam_r_L1_teras_2_1": ((0.6278, 0.0898), [(1, 0.4852, 0.1377)], 1),
    "cam_r_L1_teras_3": ((0.8969, 0.0342), [(1, 0.8284, 0.0465), (2, 0.7373, 0.0677), (3, 0.6186, 0.103),
                                           (4, 0.4729, 0.1538)], 4),
    "ext_1": ((0.8684, 0.0439), [(1, 0.7894, 0.0619), (2, 0.6869, 0.0909), (3, 0.5564, 0.1384)], 3),
    "variant ext_1": ((0.8692, 0.0603), [(1, 0.7905, 0.0837), (2, 0.6897, 0.1204)], 2),
    "variant ext_5": ((0.8855, 0.026), [(1, 0.8135, 0.0374), (2, 0.7157, 0.0532), (3, 0.5928, 0.0807),
                                        (4, 0.4441, 0.1186)], 4),
}


def _cands(rows):
    return [{"k": k, "median": m, "saturation": s} for k, m, s in rows]


def _choose(before, rows):
    return R.choose_sky_pull({"median": before[0], "saturation": before[1]}, _cands(rows))


def test_p6a_the_sky_pull_never_takes_a_crushed_sky():
    """P6a's ext_5 looked 5.4 degrees off the sun: its hazy white sky reached saturation 0.1034 only at k 6, with the
    median at 0.109, and the mid-tone rule took it (a near-black band over the top 13 % of the aerial view; P5's k 6
    stopped at 0.0968 because its EV rounded 1/6 stop brighter). A pulled save now needs a median of at least
    ``SKY_PULL_MEDIAN_MIN`` under both rules: ext_5 stays as rendered, a crushed save that reaches the main rule's
    saturation is refused too, and every pull of P6a (and its variant), P4a's replay and the deep case keeps its k. A
    dark but blue sky as rendered still needs no pull (the floor holds only for the pulled saves). Fails on 52d4bb8
    (ext_5 gets k 6; no ``sky_pull_candidate_ok``)."""
    assert R.SKY_PULL_MEDIAN_MIN == 0.4 and R.SKY_PULL_MEDIAN_MIN < 0.4261      # P4a's accepted terrace record
    k, rule = _choose(P6A_EXT5_BEFORE, P6A_EXT5_TRIED)
    assert k == 0 and rule.startswith("no k") and "median floor 0.4" in rule
    assert not R.sky_pull_candidate_ok({"median": 0.109, "saturation": 0.1034})
    assert R.sky_pull_qualifies({"median": 0.109, "saturation": 0.1034})          # the old rule took it
    # the main rule's crushed save (saturation over 0.12) is refused as well
    crushed = P6A_EXT5_TRIED[:5] + [(6, 0.11, 0.13)]
    assert _choose(P6A_EXT5_BEFORE, crushed)[0] == 0
    # every other pull keeps its k
    for cam, (before, tried, want) in P6A_SKY.items():
        assert _choose(before, tried)[0] == want, cam
    p4a = {cam: _choose(before, tried)[0] for cam, (before, tried) in P4A_SKY_TRIED.items()}
    assert p4a == {"cam_r_L1_teras_1": 3, "cam_r_L1_teras_2_1": 1, "cam_r_L1_teras_2_2": 2, "ext_1": 4, "ext_2": 2,
                   "ext_5": 0}
    deep = [{"k": k, "median": 0.95 - 0.1 * k, "saturation": 0.02 * k} for k in R.SKY_PULL_STEPS]
    assert R.choose_sky_pull({"median": 0.95, "saturation": 0.01}, deep)[0] == 5      # median 0.45 >= 0.4
    # a dark blue sky as rendered (blue hour) is under the shoulder and saturated: no pull, no floor
    assert R.choose_sky_pull({"median": 0.2, "saturation": 0.3}, [])[0] == 0
    assert R.sky_pull_candidate_ok({"median": 0.4, "saturation": 0.10})
    assert not R.sky_pull_candidate_ok({"median": 0.399, "saturation": 0.2})


def test_p6a_the_sky_pull_search_stops_under_the_median_floor(tmp_path, monkeypatch):
    """``RenderRun.sky_pull`` (``save_display`` stands in for Blender) on a hazy sky whose saves stay pale until they
    are dark: k 1-3 are pale (saturation 0.06-0.08), k 4 is at median 0.38, under the floor, and k 5 would reach the
    mid-tone rule at median 0.25. The search stops at k 4 (a deeper k is only darker), no k is taken, the sky stays as
    rendered and the record carries the floor in its targets. Fails on 52d4bb8 (k 5 at median 0.25, five saves)."""
    import numpy as np

    channels, reg = _haze_frame()
    h, w = reg["sky"].shape
    main = np.zeros((h, w, 3), dtype=np.uint8)
    main[reg["sky"]] = (223, 225, 228)
    main[reg["building"]] = (150, 140, 130)
    main[reg["far"]] = (120, 130, 110)
    main[reg["near"]] = (100, 100, 100)
    skies = {1: (200, 205, 212), 2: (170, 176, 184), 3: (133, 136, 145), 4: (95, 97, 101), 5: (60, 63, 68),
             6: (40, 42, 47)}
    saves = []

    def fake_save(scene, result, path, ev, look=R.LOOK):
        k = int(round(-4.0 - float(ev)))
        saves.append(k)
        img = (main.astype(np.float64) * 0.5 ** k).astype(np.uint8)
        img[reg["sky"]] = skies[k]
        return img

    run = types.SimpleNamespace(ctx=types.SimpleNamespace(scene=None, haze={HAZE_INDEX}), out=tmp_path, warnings=[])
    monkeypatch.setattr(R, "save_display", fake_save)
    record, weights, final = R.RenderRun.sky_pull(run, types.SimpleNamespace(name="ext_5"), {"ev": -4.0}, None, main,
                                                  channels)
    assert saves == [1, 2, 3, 4]
    assert [c["k"] for c in record["tried"]] == [1, 2, 3, 4] and record["tried"][-1]["median"] < 0.4
    assert record["k"] == 0 and weights is None and final is None and record["rule"].startswith("no k")
    assert record["targets"]["median_min"] == R.SKY_PULL_MEDIAN_MIN
    schemas.validate_render_manifest(_manifest({"camera": "ext_5", "sky_pull": record}))


def _manifest(entry_fields: dict, **top) -> dict:
    """A minimal valid render manifest with one entry carrying ``entry_fields``."""
    entry = {"camera": "cam", "png": "cam.png", "exr": "cam_passes.exr", "preview": "cam_preview.jpg", "seconds": 1.0,
             "samples": 16, "resolution": [64, 36], "depth": {"min": 1.0, "max": 2.0, "mean": 1.5},
             "index_values": [], "index_stats": {}, "files": {"index": "i.png", "depth_mm": "d.png", "normal": "n.png"},
             "render_key": "0" * 16, "hidden": [], "plugged": [],
             "exposure": {"mode": "auto", "ev": 0.0, "ev_raw": 0.0, "at_limit": False, "target": 0.9,
                          "incident_p50": 0.5, "whitepoint": None, "wb_temperature": None, "wb_tint": None,
                          "residual": None, "window_clip_frac": None, "meter_seconds": 0.1, "source": None}}
    entry.update(entry_fields)
    return {"schema_version": "0.1", "scene": None, "device": "CPU", "device_requested": "cpu",
            "blender_version": "5.2.2", "samples": 16, "resolution": [64, 36], "denoiser": None, "pass_index": {},
            "renders": [entry], **top}


# P6a's ext_5 record as written (k 6, the crushed sky)
P6A_EXT5_RECORD = {
    "ev": -6.0, "k": 6, "sky_ev": -12.0, "sky_px": 276700, "sky_share": 0.1334, "haze_px": 148678,
    "full_weight_share": 0.9812, "ring_px": 5418, "sun_offset_deg": 5.4, "into_sun": True, "median_before": 0.8255,
    "saturation_before": 0.0141, "median_after": 0.109, "saturation_after": 0.1034,
    "rule": "smallest k with the sky median <= 0.6 (mid-tone) and saturation >= 0.1",
    "tried": [{"k": k, "median": m, "saturation": s} for k, m, s in P6A_EXT5_TRIED], "edge_dot_px": 0, "edge_px": 5696}


def test_p6a_gpu_sky_check_fails_a_crushed_sky(tmp_path, monkeypatch):
    """CPU replay of ``test_sky_and_window_pulls_reach_their_targets``: P6a's ext_5 record (k 6, chosen save and blended
    sky at median 0.109) passed every check; it now fails twice (the chosen save under the floor, the blended sky under
    ``SKY_PULL_MEDIAN_MIN - SKY_PULL_MEDIAN_ALLOWANCE``). The variant's ext_5 (k 4 at 0.4441) and P6a's teras_3 pass,
    and a project whose only sky over the shoulder has nothing but a crushed qualifying k needs no pull (its "no view
    pulled" rule counts only the k the pull may take). Fails on 52d4bb8 (ext_5 passes; the last case fails)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    scene = {"lighting": {"world_exterior": {"name": "wenart_world_exterior"}}}
    assert gpu.SKY_PULL_MEDIAN_ALLOWANCE == 0.05

    def project(**skies):
        return "real04", scene, {"renders": [{"camera": c, "room_id": None, "sky_pull": s} for c, s in skies.items()]}
    variant = dict(P6A_EXT5_RECORD, k=4, ev=-4.0, median_before=0.8855, saturation_before=0.026, median_after=0.4441,
                   saturation_after=0.1186, tried=_cands(P6A_SKY["variant ext_5"][1]))
    teras_3 = dict(P6A_EXT5_RECORD, k=4, ev=-4.0, median_before=0.8969, saturation_before=0.0342, median_after=0.4732,
                   saturation_after=0.1538, tried=_cands(P6A_SKY["cam_r_L1_teras_3"][1]), into_sun=True)
    gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_5=variant, ext_3=teras_3))
    with pytest.raises(AssertionError, match=r"ext_5', 'sky pull off its targets'") as err:
        gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_5=P6A_EXT5_RECORD, ext_3=teras_3))
    assert "crushed sky: blended median 0.109" in str(err.value)
    # ext_5 as m13.5 renders it: k 0, its tried saves end under the floor; no other sky over the shoulder
    stays = dict(P6A_EXT5_RECORD, k=0, ev=0.0, median_after=0.8255, saturation_after=0.0141,
                 tried=_cands(P6A_EXT5_TRIED[:4]), rule="no k")
    gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_5=stays))
    gpu.test_sky_and_window_pulls_reach_their_targets(project(ext_5=dict(stays, tried=_cands(P6A_EXT5_TRIED))))


# --------------------------------------------------------------------------
# Cycles' per-sample clamps
# --------------------------------------------------------------------------

def test_p6a_the_clamps_are_set_recorded_and_keyed_only_off_the_default(tmp_path):
    """The interior-sky A/B found Cycles' indirect clamp never set: the outside seen through the two-face pane is
    reached at bounce 2 and clamped with it. ``configure_render`` now sets ``sample_clamp_direct`` 0 and
    ``sample_clamp_indirect`` 10, Cycles' own defaults (P6a's real04.blend reads 0.0 / 10.0), so no render changes;
    ``--clamp-indirect`` takes another value for a clamp A/B (0 = off, never negative), which enters the render key;
    the default does not, so no key moves; the manifest records ``clamp``. Fails on 52d4bb8 (nothing set or
    recorded, no flag)."""
    assert (R.CLAMP_DIRECT, R.CLAMP_INDIRECT) == (0.0, 10.0)
    assert R.clamp_record() == {"direct": 0.0, "indirect": 10.0} and R.clamp_record(100) == {"direct": 0.0,
                                                                                               "indirect": 100.0}

    def scene():
        return types.SimpleNamespace(cycles=types.SimpleNamespace(), render=types.SimpleNamespace(),
                                     view_layers=[types.SimpleNamespace()])
    s = scene()
    assert R.configure_render(s, 16, (64, 36), "CPU", False) is None
    assert (s.cycles.sample_clamp_direct, s.cycles.sample_clamp_indirect) == (0.0, 10.0)
    s = scene()
    R.configure_render(s, 16, (64, 36), "CPU", False, clamp_indirect=0.0)
    assert (s.cycles.sample_clamp_direct, s.cycles.sample_clamp_indirect) == (0.0, 0.0)
    # the key: unchanged at the default, another key for another clamp
    base = dict(samples=256, resolution=(1920, 1080), denoiser="OPENIMAGEDENOISE", exposure_mode="auto",
                exposure_value=None, target=0.9, wb_mode="project", wb_fixed=None, hidden=[], plugged=[],
                project_whitepoint=P5_ANCHOR)
    plain = R.key_settings(**base)
    assert "clamp_indirect" not in plain
    assert R.render_key(R.key_settings(**base, clamp_indirect=10.0)) == R.render_key(plain)
    other = R.key_settings(**base, clamp_indirect=100.0)
    assert other["clamp_indirect"] == 100.0 and R.render_key(other) != R.render_key(plain)
    # the flag and its range
    args = R.parse_args(["--out", "x", "--clamp-indirect", "0"])
    assert args.clamp_indirect == 0.0 and R.parse_args(["--out", "x"]).clamp_indirect is None
    R.check_control_flags(args)
    for bad in ("-1", "nan"):
        with pytest.raises(R.UsageError, match="clamp-indirect"):
            R.check_control_flags(R.parse_args(["--out", "x", "--clamp-indirect", bad]))
    # the manifest records the clamps (and validates), RenderRun.write_manifest with stand-ins
    for flag, want in ((None, 10.0), (0.0, 0.0)):
        manifest = _write_manifest(tmp_path / str(flag), flag)
        assert manifest["clamp"] == {"direct": 0.0, "indirect": want}
        schemas.validate_render_manifest(manifest)
    with pytest.raises(Exception):
        schemas.validate_render_manifest(_manifest({}, clamp={"direct": 0.0, "indirect": -1.0}))


def _write_manifest(out: Path, clamp_indirect) -> dict:
    look = object.__new__(R.Look)
    look.look_from, look.look_from_path, look.exposure_mode, look.target = None, None, "auto", 0.9
    look.limits, look.floor_shift, look.sun_wm2, look.wb_mode, look.project = (-2.0, 3.0), 0.0, None, "project", None
    args = types.SimpleNamespace(samples=16, device="cpu", alt_look=None, max_bounces=None, ev_offset=0.0,
                                 preview_quality=None, clamp_indirect=clamp_indirect)
    run = object.__new__(R.RenderRun)
    run.ctx = types.SimpleNamespace(args=args, blend_path=None, fingerprint=None, device="CPU",
                                    blender_version="5.2.2", res=(64, 36), denoiser=None, look=look,
                                    light_variant={"render": None, "build": None}, pass_index={}, deadline=None)
    out.mkdir(parents=True)
    run.out, run.manifest_path = out, out / "render_manifest.json"
    run.entries, run.cameras, run.hidden, run.plugged = {}, [], [], []
    run.dropped, run.carried, run.not_rendered, run.warnings = {}, set(), [], []
    run.write_manifest()
    return json.loads(run.manifest_path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The GPU index check: a sliver of a library piece's box
# --------------------------------------------------------------------------

# P6a (runs/20261022-135644-m13_p6, real04): building_final.json cut to the camera's room (its level and a level
# above, the walls of its openings, the planned pieces with asset method and fitted box), the camera plan, the built
# mesh's box3d, the view's index values and the planned pieces' pass indices. camsearch.model_shares of the cut equals
# the whole building's for every planned piece, with the box as fitted, 2 cm and 15 % smaller per side.
P6A_INDEX = {
    "cam_r_L0_yatak_odasi_4_3": {
        "piece": "f_L0_041",
        "cut": {"project": {"id": "real04"}, "status": "ok",
                "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 3.0},
                           {"id": "L9", "elevation": 99.0, "ceiling_height": 3.0}],
                "walls": [{"id": "w_L0_003", "level_id": "L0", "start": [1.2, 7.082], "end": [4.218, 7.082],
                           "thickness": 0.12},
                          {"id": "w_L0_013", "level_id": "L0", "start": [4.268, 0.0], "end": [4.268, 11.8],
                           "thickness": 0.1}],
                "openings": [{"id": "d_L0_008", "type": "door", "level_id": "L0", "wall_id": "w_L0_013",
                              "center": [4.268, 7.687], "width": 0.778, "height": 2.1, "sill_height": None},
                             {"id": "win_L0_005", "type": "window", "level_id": "L0", "wall_id": "w_L0_003",
                              "center": [2.3354, 7.082], "width": 1.8696, "height": 1.2, "sill_height": 0.9}],
                "rooms": [{"id": "r_L0_yatak_odasi_4", "level_id": "L0", "label": "Yatak Odası",
                           "polygon": [[0.2, 9.2], [1.2, 9.2], [1.2, 7.142], [4.218, 7.142], [4.218, 11.8],
                                       [0.2, 11.8]]}],
                "furniture": [
                    {"id": "f_L0_009", "level_id": "L0", "room_id": "r_L0_yatak_odasi_4", "type": "bed_double",
                     "source": "from_documents", "footprint": {"center": [3.218, 10.2943], "size": [1.8, 2.0],
                                                                "rotation_deg": 270.0},
                     "front_deg": 180.0, "height": None,
                     "asset": {"method": "library", "bbox_m": [1.8, 2.1798, 1.1644]}},
                    {"id": "f_L0_025", "level_id": "L0", "room_id": "r_L0_yatak_odasi_4", "type": "desk",
                     "source": "from_documents", "footprint": {"center": [0.5006, 10.6351], "size": [1.4471, 0.6],
                                                                "rotation_deg": 90.0},
                     "front_deg": 0.0, "height": None,
                     "asset": {"method": "library", "bbox_m": [1.4471, 0.5803, 0.7084]}},
                    {"id": "f_L0_030", "level_id": "L0", "room_id": "r_L0_yatak_odasi_4", "type": "wardrobe",
                     "source": "from_documents", "footprint": {"center": [2.25, 7.73], "size": [2.0896, 0.5852],
                                                                "rotation_deg": 180.0},
                     "front_deg": 90.0, "height": 2.1,
                     "asset": {"method": "library", "bbox_m": [2.0896, 0.5706, 2.1864]}},
                    {"id": "f_L0_036", "level_id": "L0", "room_id": "r_L0_yatak_odasi_4", "type": "nightstand",
                     "source": "from_documents", "footprint": {"center": [3.99, 9.05], "size": [0.5, 0.45],
                                                                "rotation_deg": 270.0},
                     "front_deg": 180.0, "height": None, "asset": {"method": "library", "bbox_m": [0.5, 0.42, 0.5995]}},
                    {"id": "f_L0_041", "level_id": "L0", "room_id": "r_L0_yatak_odasi_4", "type": "office_chair",
                     "source": "from_documents", "footprint": {"center": [0.8574, 10.6351], "size": [0.5, 0.5],
                                                                "rotation_deg": 270.0},
                     "front_deg": 180.0, "height": None,
                     "asset": {"method": "library", "bbox_m": [0.5, 0.4972, 0.8196]}}]},
        "plan": {"name": "cam_r_L0_yatak_odasi_4_3", "room_id": "r_L0_yatak_odasi_4", "level_id": "L0", "index": 3,
                 "position": [1.7, 11.142, 1.25], "target": [1.7, 10.142, 1.25], "lens_mm": 18.0, "sensor_mm": 36.0,
                 "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": -0.1, "policy": "search", "warning": None,
                 "visible_openings": ["d_L0_008", "win_L0_005"],
                 "visible_furniture": ["f_L0_009", "f_L0_025", "f_L0_030", "f_L0_036", "f_L0_041"],
                 "kind": "interior", "variant": "base"},
        "box3d": {"center": [0.8574, 10.6351, 0.4098], "size": [0.5001, 0.4972, 0.8195], "rotation_deg": 270.0},
        "index_values": [104, 121, 137, 142, 148, 173, 176],
        "pass_index": {"f_L0_009": 121, "f_L0_025": 137, "f_L0_030": 142, "f_L0_036": 148, "f_L0_041": 153},
        "shares": (0.0192, 0.0131, 0.0013)},
    "cam_r_L1_koridor_2_1": {
        "piece": "f_L1_024",
        "cut": {"project": {"id": "real04"}, "status": "ok",
                "levels": [{"id": "L1", "elevation": 3.15, "ceiling_height": 2.451},
                           {"id": "L9", "elevation": 99.0, "ceiling_height": 3.0}],
                "walls": [{"id": "w_L1_002", "level_id": "L1", "start": [2.8005, 7.5171], "end": [14.3725, 7.5171],
                           "thickness": 0.15},
                          {"id": "w_L1_013", "level_id": "L1", "start": [11.5045, 9.9341], "end": [11.5045, 11.8001],
                           "thickness": 0.1},
                          {"id": "w_L1_015", "level_id": "L1", "start": [14.4225, 0.2001], "end": [14.4225, 10.2001],
                           "thickness": 0.1}],
                "openings": [{"id": "d_L1_002", "type": "door", "level_id": "L1", "wall_id": "w_L1_002",
                              "center": [13.7895, 7.5171], "width": 0.822, "height": 2.1, "sill_height": None},
                             {"id": "d_L1_005", "type": "door", "level_id": "L1", "wall_id": "w_L1_013",
                              "center": [11.5045, 10.9901], "width": 0.824, "height": 2.1, "sill_height": None},
                             {"id": "d_L1_006", "type": "door", "level_id": "L1", "wall_id": "w_L1_015",
                              "center": [14.4225, 8.4381], "width": 0.824, "height": 2.1, "sill_height": None}],
                "rooms": [{"id": "r_L1_koridor_2", "level_id": "L1", "label": "Koridor",
                           "polygon": [[8.7865, 7.5921], [14.3725, 7.5921], [14.3725, 10.1901], [12.8545, 10.1901],
                                       [12.8545, 11.8001], [11.5545, 11.8001], [11.5545, 9.7341], [8.7865, 9.7341]]}],
                "furniture": [
                    {"id": "f_L1_024", "level_id": "L1", "room_id": "r_L1_koridor_2", "type": "table_coffee",
                     "source": "from_documents", "footprint": {"center": [13.61, 9.8], "size": [1.2, 0.7],
                                                                "rotation_deg": 0.0},
                     "front_deg": None, "height": None,
                     "asset": {"method": "library", "bbox_m": [1.2, 0.7122, 0.4443]}},
                    {"id": "f_L1_025", "level_id": "L1", "room_id": "r_L1_koridor_2", "type": "chair",
                     "source": "from_documents", "footprint": {"center": [12.65, 9.9001], "size": [0.6, 0.45],
                                                                "rotation_deg": 90.0},
                     "front_deg": 0.0, "height": None, "asset": {"method": "parametric", "bbox_m": [0.6, 0.45, 0.9]}}]},
        "plan": {"name": "cam_r_L1_koridor_2_1", "room_id": "r_L1_koridor_2", "level_id": "L1", "index": 1,
                 "position": [12.2865, 10.5921, 4.4], "target": [12.2865, 9.5921, 4.4], "lens_mm": 18.0,
                 "sensor_mm": 36.0, "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": -0.1, "policy": "search",
                 "warning": None, "visible_openings": ["d_L1_002", "d_L1_006"],
                 "visible_furniture": ["f_L1_024", "f_L1_025"], "kind": "interior", "variant": "base"},
        "box3d": {"center": [13.61, 9.8, 3.3722], "size": [1.2, 0.7122, 0.4443], "rotation_deg": 0.0},
        "index_values": [198, 200, 204, 223],
        "pass_index": {"f_L1_024": 222, "f_L1_025": 223},
        "shares": (0.0104, 0.0080, 0.0)},
}


def _index_project(outputs: Path, cam: str, piece_change=None, box_change=None) -> tuple:
    import copy

    case = copy.deepcopy(P6A_INDEX[cam])
    piece = next(f for f in case["cut"]["furniture"] if f["id"] == case["piece"])
    if piece_change:
        piece_change(piece, case["box3d"])
    if box_change:
        box_change(piece, case["box3d"])
    path = outputs / "real04" / "building_final.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(case["cut"]), encoding="utf-8")
    scene = {"building": str(path), "pass_index": case["pass_index"], "cameras": [case["plan"]],
             "objects": [{"wenart_id": case["piece"], "kind": "furniture", "box3d": case["box3d"]}]}
    render = {"renders": [{"camera": cam, "index_values": case["index_values"]}]}
    return "real04", scene, render


def test_p6a_the_cuts_reproduce_the_pod_model_shares():
    """The fixtures are P6a's two failing views: the model sees 0.0192 of the office chair's fitted box and 0.0104 of
    the oval table's, 0.0131 / 0.0080 with the 2 cm slack (over ``MODEL_HIDDEN_SHARE`` 0.005: the failures) and
    0.0013 / 0.0 with 15 % per side. Every other planned piece keeps its share."""
    import copy

    from wenart.blender import camsearch

    for cam, case in P6A_INDEX.items():
        pid = case["piece"]
        got = []
        for frac in (None, 0.0, 0.15):
            b = copy.deepcopy(case["cut"])
            piece = next(f for f in b["furniture"] if f["id"] == pid)
            if frac is not None:
                w, d = piece["asset"]["bbox_m"][:2]
                piece["asset"]["bbox_m"][:2] = [w - 2 * max(0.02, frac * w), d - 2 * max(0.02, frac * d)]
            got.append(round(camsearch.model_shares(b, case["plan"]).get(pid, 0.0), 4))
        assert tuple(got) == case["shares"], cam


@pytest.mark.parametrize("cam", sorted(P6A_INDEX))
def test_p6a_gpu_index_check_allows_a_sliver_of_a_library_box(cam, tmp_path, monkeypatch, capsys):
    """P6a's GPU index check failed on the office chair f_L0_041 (yatak_odasi_4_3) and the oval glass-top coffee table
    f_L1_024 (koridor_2_1): both built where the model puts them (box3d within 3 mm), seen by the model only as a
    sliver of their fitted boxes in a corner of the frame where the renders show the desk, the wall and the floor (a
    chair back narrower than its star base, the oval's tips). A library piece whose whole box the model sees on at
    most ``LIBRARY_SLIVER_MAX`` of the frame gets ``LIBRARY_BOX_SLACK_SHARE`` of each side as slack: both pass as
    "library box edge only". Fails on 52d4bb8 (the 2 cm slack leaves 0.0131 / 0.0080)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.LIBRARY_SLIVER_MAX == 0.03 and gpu.LIBRARY_BOX_SLACK_SHARE == 0.15 and gpu.LIBRARY_BOX_SLACK_M == 0.02
    gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path, cam))
    out = capsys.readouterr().out
    pid, share = P6A_INDEX[cam]["piece"], P6A_INDEX[cam]["shares"][0]
    assert "library box edge only" in out and f"('{cam}', '{pid}', {share})" in out


def _fixed(piece, box):                 # fixed equipment keeps the 2 cm (drawn like walls; its mesh fills its box)
    piece["type"] = "washing_machine"


def _moved(piece, box):                 # the mesh built 5 cm off its footprint
    box["center"][0] += 0.05


def _parametric(piece, box):            # a parametric piece fills its box
    piece["asset"]["method"] = "parametric"


def _bigger(piece, box):                # a box seen on more than LIBRARY_SLIVER_MAX of the frame
    piece["footprint"]["center"][1] -= 0.6
    box["center"][1] -= 0.6


@pytest.mark.parametrize("change", [_fixed, _moved, _parametric, _bigger],
                         ids=["fixed_equipment", "moved_5cm", "parametric", "more_than_a_sliver"])
def test_p6a_gpu_index_check_keeps_the_strict_rule_otherwise(change, tmp_path, monkeypatch):
    """The sliver slack does not hide a missing piece: fixed equipment (P5's toilet f_L1_013 behind a ceiling light over
    55.7 % of its bath view: share 0.0178, 0.0029 at 15 %, stays a failure), a moved mesh, a parametric piece and a
    piece moved 0.6 m into the frame (its box seen on more than ``LIBRARY_SLIVER_MAX``) still fail as on 52d4bb8.
    Mutations: dropping the fixed-type condition makes the first case pass; dropping the sliver-share condition makes
    the earlier round's pin of the 5 cm wider wardrobe (tests/test_render_gpu_logic_m10.py, share 0.068) pass."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    cam = "cam_r_L0_yatak_odasi_4_3"
    if change is _bigger:
        from wenart.blender import camsearch

        b = json.loads(json.dumps(P6A_INDEX[cam]["cut"]))
        _bigger(next(f for f in b["furniture"] if f["id"] == "f_L0_041"), {"center": [0.0, 0.0, 0.0]})
        assert camsearch.model_shares(b, P6A_INDEX[cam]["plan"])["f_L0_041"] > gpu.LIBRARY_SLIVER_MAX
    with pytest.raises(AssertionError, match=rf"{cam}', \['f_L0_041'\]"):
        gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path, cam, piece_change=change))


# --------------------------------------------------------------------------
# The GPU colour checks keep their values
# --------------------------------------------------------------------------

def test_p6a_gpu_colour_checks_keep_their_values(tmp_path, monkeypatch):
    """P6a's orange check passed on 18 views and its per-view values were lost: pytest keeps no output of a passing
    test and junit-full.xml has no system-out. The orange and olive checks now write their values to
    ``gpu_check_values.json`` in ``$WENART_RESULTS`` (next to the job's junit XML), else in the project's renders
    folder, merged per check and project, also when the check passes. Fails on 52d4bb8 (no file)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.CHECK_VALUES_FILE == "gpu_check_values.json"
    views = {"cam_r_bed_1": ("r_bed", 1.40, 0.0), "cam_r_bed_2": ("r_bed", 1.36, 0.0),
             "cam_r_hall_1": ("r_hall", 1.36, 1.0)}
    results = tmp_path / "results"
    monkeypatch.setenv("WENART_RESULTS", str(results))
    monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / "a")
    project = _wall_views(tmp_path / "a", views)
    gpu.test_rig_lit_rooms_have_no_orange_cast(project)                       # passes ...
    data = json.loads((results / "gpu_check_values.json").read_text(encoding="utf-8"))
    orange = data["rig_lit_rooms_have_no_orange_cast"]["real02"]               # ... and keeps its values
    assert orange["rig_lit"]["cam_r_hall_1"]["wall_rb"] == pytest.approx(1.36, abs=0.01)
    assert orange["rig_lit"]["cam_r_hall_1"]["bound"] == pytest.approx(orange["references"]["painted"] + 0.15)
    assert set(orange["daylight"]) == {"cam_r_bed_1", "cam_r_bed_2"} and orange["warm"] == []
    monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / "a2")                    # the olive check on neutral walls
    gpu.test_daylight_walls_are_not_olive(_wall_views(tmp_path / "a2", views, rgb={
        "cam_r_bed_1": (120, 113, 100), "cam_r_bed_2": (118, 112, 100), "cam_r_hall_1": (130, 110, 100)}))
    data = json.loads((results / "gpu_check_values.json").read_text(encoding="utf-8"))
    assert set(data) == {"rig_lit_rooms_have_no_orange_cast", "daylight_walls_are_not_olive"}
    assert set(data["daylight_walls_are_not_olive"]["real02"]["views"]) == {"cam_r_bed_1", "cam_r_bed_2"}
    # without $WENART_RESULTS: the project's renders folder; a failing check keeps its values too
    monkeypatch.delenv("WENART_RESULTS")
    monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / "b")
    with pytest.raises(AssertionError, match="cam_r_hall_1"):
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / "b", dict(views, cam_r_hall_1=("r_hall", 1.8,
                                                                                                           1.0))))
    kept = json.loads((tmp_path / "b" / "real02" / "renders" / "gpu_check_values.json").read_text(encoding="utf-8"))
    assert kept["rig_lit_rooms_have_no_orange_cast"]["real02"]["warm"] == ["cam_r_hall_1"]


# --------------------------------------------------------------------------
# The daylight tint: metered on the walls; the gain rule a recorded choice
# --------------------------------------------------------------------------

# P6a real04 (render_manifest.json): the recorded daylight green ratio and m13.4's tint gain of the 18 painted
# daylight views and the rig shares the gain was taken by (under WB_RIG_SHARE_MIN: 0)
P6A_TINT = {
    "cam_r_L-1_salon_1": (1.056202, 1.034028, 0.0), "cam_r_L-1_salon_2": (1.071576, 1.043787, 0.0),
    "cam_r_L-1_salon_3": (1.104327, 1.064414, 0.0), "cam_r_L0_e_yatak_odasi_1": (1.207234, 1.127876, 0.0),
    "cam_r_L0_e_yatak_odasi_2": (1.215422, 1.132843, 0.0), "cam_r_L0_e_yatak_odasi_3": (1.218028, 1.134421, 0.0),
    "cam_r_L0_koridor_1": (0.971349, 0.985363, 0.297014), "cam_r_L0_koridor_2": (0.976593, 0.98677, 0.237834),
    "cam_r_L0_koridor_3": (0.970544, 0.983503, 0.226804), "cam_r_L0_yatak_odasi_1": (1.235891, 1.137055, 0.052692),
    "cam_r_L0_yatak_odasi_2": (1.228221, 1.132877, 0.05153), "cam_r_L0_yatak_odasi_3": (1.209933, 1.129514, 0.0),
    "cam_r_L0_yatak_odasi_4_1": (0.994256, 0.994376, 0.0316), "cam_r_L0_yatak_odasi_4_2": (0.9949, 0.994723, 0.020726),
    "cam_r_L0_yatak_odasi_4_3": (0.99346, 0.993676, 0.0), "cam_r_L1_oyun_1": (0.979637, 0.984667, 0.0),
    "cam_r_L1_oyun_2": (0.983685, 0.98731, 0.0), "cam_r_L1_oyun_3": (0.98179, 0.986073, 0.0),
}
# bpy 5.2.2 shim of P6a's real04.blend (480 x 270, the daylight-only meter at 240 x 135 as on the pod): the green ratio
# of the daylight over every interior surface and on the walls, and the gain each rule gives (render.view_tint_gain)
P6A_SHIM_GREEN = {"cam_r_L-1_salon_2": (1.078392, 1.224139), "cam_r_L0_e_yatak_odasi_2": (1.242216, 1.439585)}
P4B_ANCHOR = [1.115155, 0.994669, 0.713725]      # real03's project white point (P4b, green ratio 1.115)


def _green_on_white(anchor, day, gain):
    """The green ratio a white surface under daylight of green ratio ``day`` keeps through the tinted white point."""
    return day / R.green_ratio(R.tinted_whitepoint(anchor, gain))


def test_p6a_the_view_tint_rules():
    """The gain keeps m13.4's rule by default (``WB_TINT_KEEP_GREEN_RESIDUAL``: the mood's residual of the view's green;
    all 18 of P6a's recorded gains reproduce) and takes the P6a verifier's rule with ``keep_green_residual=False``: no
    green on white in any view and no anchor green on another view (real03's green anchor, P4b, green ratio 1.115).
    What changes the olive views is the green the gain is given: on the shim the walls' green gives e_yatak_odasi_2
    1.265 where the room's gave 1.149. A residual of 1 is no correction under both rules. Fails on 52d4bb8 (no
    ``keep_green_residual``)."""
    assert R.WB_TINT_KEEP_GREEN_RESIDUAL is True and R.RENDER_CODE_VERSION == "m13.6"
    for cam, (day, gain_m134, share) in P6A_TINT.items():
        s = share if share >= R.WB_RIG_SHARE_MIN else 0.0
        assert R.view_tint_gain(P5_ANCHOR, day, 0.35, s) == pytest.approx(gain_m134, abs=1e-6), cam
        assert R.view_tint_gain(P5_ANCHOR, day, 0.35, s, keep_green_residual=True) == pytest.approx(gain_m134,
                                                                                                    abs=1e-6), cam
        gain = R.view_tint_gain(P5_ANCHOR, day, 0.35, s, keep_green_residual=False)
        assert gain == pytest.approx(min(1.3, (day / R.green_ratio(P5_ANCHOR)) ** (1.0 - s)), abs=1e-6), cam
        if s == 0.0:
            assert _green_on_white(P5_ANCHOR, day, gain) == pytest.approx(1.0, abs=2e-5), cam
            assert _green_on_white(P5_ANCHOR, day, gain_m134) == pytest.approx(day ** 0.35, abs=2e-5), cam
    gains = {cam: (R.view_tint_gain(P5_ANCHOR, every, 0.35), R.view_tint_gain(P5_ANCHOR, walls, 0.35),
                   R.view_tint_gain(P5_ANCHOR, walls, 0.35, keep_green_residual=False))
             for cam, (every, walls) in P6A_SHIM_GREEN.items()}
    assert gains["cam_r_L0_e_yatak_odasi_2"] == pytest.approx((1.149013, 1.264594, 1.3), abs=1e-6)
    assert gains["cam_r_L-1_salon_2"] == pytest.approx((1.048098, 1.138117, 1.221596), abs=1e-6)
    # the temperature (R/B of the white point) is the anchor's under both rules
    for gain in gains["cam_r_L0_e_yatak_odasi_2"]:
        wp = R.tinted_whitepoint(P5_ANCHOR, gain)
        assert wp[0] / wp[2] == pytest.approx(P5_ANCHOR[0] / P5_ANCHOR[2], abs=1e-5)
    # real03: without the residual, neutral and green daylight both end at no green on white
    for day in (0.95, 1.0, 1.05, 1.1826, 1.25):
        gain = R.view_tint_gain(P4B_ANCHOR, day, 0.35, keep_green_residual=False)
        assert _green_on_white(P4B_ANCHOR, day, gain) == pytest.approx(1.0, abs=2e-5), day
        assert _green_on_white(P4B_ANCHOR, day, R.view_tint_gain(P4B_ANCHOR, day, 0.35)) == \
            pytest.approx(day ** 0.35, abs=2e-5), day
    assert R.view_tint_gain(P5_ANCHOR, 1.215422, 1.0) == R.view_tint_gain(P5_ANCHOR, 1.215422, 1.0, 0.0, 1.3,
                                                                           False) == 1.0


def _wall_frame():
    """A 10 x 20 metering frame: rows 0-4 a wall (index 0, normal z 0) lit green (1, 1.4, 1), rows 5-9 the floor
    (normal z 1) lit neutral (2, 2, 2); columns 15-19 of the wall rows a piece of furniture (index 5) and columns 0-2
    of them a window (index 7), neither of them wall."""
    import numpy as np

    h, w = 10, 20
    light = np.zeros((h, w, 3))
    light[:5] = (1.0, 1.4, 1.0)
    light[5:] = (2.0, 2.0, 2.0)
    albedo = np.full((h, w, 3), 0.6)
    index = np.zeros((h, w))
    index[:5, 15:] = 5
    index[:5, :3] = 7
    depth = np.full((h, w), 3.0)
    nz = np.zeros((h, w))
    nz[5:] = 1.0
    return light, albedo, index, depth, nz


def test_p6a_the_daylight_pass_meters_the_walls():
    """``meter_stats`` with the metering pass's normal Z also sums the light on the wall pixels (``views.regions``'
    walls: an interior surface with pass index 0 and |normal z| < 0.3, not a window, not a piece) and their share of
    the frame; nothing it reported before changes. ``daylight_green`` takes the walls' green (``WB_TINT_METER``
    ``walls``) when they cover ``WB_TINT_WALL_MIN_SHARE`` of the frame, else the green of every interior surface (as
    m13.4), and that with ``surfaces``. Fails on 52d4bb8 (no ``wall_normal_z``, no ``daylight_green``)."""
    light, albedo, index, depth, nz = _wall_frame()
    plain = R.meter_stats(light, albedo, index, depth, {7}, blocks_across=4)
    walls = R.meter_stats(light, albedo, index, depth, {7}, blocks_across=4, wall_normal_z=nz)
    assert {k: v for k, v in walls.items() if k not in ("wall_illuminant", "wall_frac")} == plain
    assert walls["wall_frac"] == pytest.approx(5 * 12 / 200) and walls["wall_illuminant"] == pytest.approx(
        [60.0, 84.0, 60.0])
    assert R.green_ratio(walls["wall_illuminant"]) == pytest.approx(1.4)
    assert R.WB_TINT_METER == "walls" and R.WB_TINT_METERS == ("surfaces", "walls")
    every = R.green_ratio(plain["illuminant"])
    assert every < 1.4
    assert R.daylight_green(walls) == (pytest.approx(1.4), "walls")
    assert R.daylight_green(walls, "surfaces") == (pytest.approx(every), "surfaces")
    assert R.daylight_green(dict(walls, wall_frac=0.04)) == (pytest.approx(every), "surfaces")
    assert R.daylight_green(plain) == (pytest.approx(every), "surfaces")              # no wall keys
    assert R.daylight_green(None) == (None, None) and R.daylight_green({"illuminant": None}) == (None, None)
    with pytest.raises(ValueError, match="meter"):
        R.daylight_green(walls, "floor")


def test_p6a_view_white_meters_the_tint_on_the_walls(tmp_path, monkeypatch):
    """``Look._view_white``: the daylight-only pass (rig hidden) is metered with ``walls``, the white point takes the
    gain of the walls' green and the record says ``wb_day_green_source``, ``wb_day_green_all`` (the room's green, m13.4's
    meter), ``wb_day_wall_share`` and ``wb_tint_green_residual`` (all valid in the schema). ``WB_TINT_METER``
    ``surfaces`` gives m13.4's green, ``WB_TINT_KEEP_GREEN_RESIDUAL`` False the verifier's rule, each recorded. A
    project-balanced interior view's first metering pass asks for the walls too (the tint of a scene without a rig), an
    exterior view's does not. Fails on 52d4bb8 (no ``walls`` asked, the room's green, no record)."""
    look = object.__new__(R.Look)
    look.scene, look.windows, look.haze, look.room_types = {}, set(), set(), {}
    look.project = {"residual": 0.35, "whitepoint": list(P5_ANCHOR), "source": "s"}
    calls = []

    def meter(scene, cam, out, res, windows, haze=(), **kw):
        calls.append(kw)
        return {"illuminant": [1.0, 1.2, 1.0], "incident_p50": 0.02, "seconds": 0.1,
                "wall_illuminant": [1.0, 1.4, 1.0], "wall_frac": 0.3}
    monkeypatch.setattr(R, "rig_objects", lambda scene: ["rig"])
    monkeypatch.setattr(R, "rig_lights", lambda scene: [("r_bed", 2700.0, 2.5)])
    monkeypatch.setattr(R, "hide_objects", lambda objs: [])
    monkeypatch.setattr(R, "unhide_objects", lambda saved: None)
    monkeypatch.setattr(R, "meter_camera", meter)
    monkeypatch.setattr(R, "kelvin_whitepoint", lambda scene, k: R.normalise_whitepoint([1.9353, 0.8035, 0.1922]))
    cam = types.SimpleNamespace(name="cam_r_bed_1", get={"wenart_room": "r_bed", "wenart_camera_kind": "interior"}.get)

    def view():
        rec = {"whitepoint": list(P5_ANCHOR), "meter_seconds": 1.0}
        look._view_white(cam, rec, {"illuminant": [1.0, 1.2, 1.0], "incident_p50": 0.02}, tmp_path, (64, 36))
        return rec
    rec = view()
    assert calls == [{"walls": True}]
    assert rec["wb_day_green_source"] == "walls" and rec["wb_day_green"] == pytest.approx(1.4)
    assert rec["wb_day_green_all"] == pytest.approx(1.2) and rec["wb_day_wall_share"] == 0.3
    assert rec["wb_tint_green_residual"] is True
    assert rec["wb_view_tint_gain"] == R.view_tint_gain(P5_ANCHOR, 1.4, 0.35) > R.view_tint_gain(P5_ANCHOR, 1.2, 0.35)
    assert rec["whitepoint"] == pytest.approx(R.tinted_whitepoint(P5_ANCHOR, rec["wb_view_tint_gain"]), abs=1e-9)
    entry = _manifest({"exposure": dict(_manifest({})["renders"][0]["exposure"], **{
        k: rec[k] for k in ("wb_day_green", "wb_day_green_source", "wb_day_green_all", "wb_day_wall_share",
                            "wb_tint_green_residual", "wb_view_tint_gain")})})
    schemas.validate_render_manifest(entry)
    monkeypatch.setattr(R, "WB_TINT_METER", "surfaces")
    rec = view()
    assert rec["wb_day_green_source"] == "surfaces" and rec["wb_day_green"] == pytest.approx(1.2)
    assert rec["wb_view_tint_gain"] == R.view_tint_gain(P5_ANCHOR, 1.2, 0.35)
    monkeypatch.setattr(R, "WB_TINT_KEEP_GREEN_RESIDUAL", False)
    rec = view()
    assert rec["wb_tint_green_residual"] is False
    assert rec["wb_view_tint_gain"] == R.view_tint_gain(P5_ANCHOR, 1.2, 0.35, keep_green_residual=False)
    # Look._decide: the first metering pass of a project-balanced interior view asks for the walls, an exterior's not
    look.look_from, look.exposure_mode, look.exposure_value, look.target = None, "auto", None, 0.9
    look.wb_mode, look.limits, look.floor_shift, look.mood, look.ev_offset = "project", (-2.0, 3.0), 0.0, None, 0.0
    monkeypatch.setattr(R, "meter_camera", lambda *a, **kw: calls.append(kw) or dict(
        {"illuminant": [1.0, 1.2, 1.0], "incident_p50": 0.5, "seconds": 0.1, "resolution": [8, 4], "samples": 16,
         "blocks": 1, "blocks_used": 1, "block_px": 1, "interior_frac": 1.0}))
    monkeypatch.setattr(R, "rig_objects", lambda scene: [])
    calls.clear()
    look.decide(cam, tmp_path, (64, 36))
    assert calls == [{"walls": True}]
    calls.clear()
    look.decide(types.SimpleNamespace(name="ext_1", get={"wenart_camera_kind": "exterior"}.get), tmp_path, (64, 36))
    assert calls == [{}]


def test_p6a_gpu_white_point_check_reads_the_rule_each_record_took(tmp_path, monkeypatch):
    """CPU replay of ``test_views_keep_the_project_white_point_or_mix_it_with_the_rig``: P6a's e_yatak_odasi_2 record
    (m13.4: daylight green 1.215422, gain 1.132843, its white point as written) passes in its m13.4 manifest (P6b's
    real03 records are re-checked the same way) and fails in an m13.5 manifest (no source, no rule); an m13.5 record
    metered on the walls passes with either rule when it says which it took, and fails when its gain belongs to the
    other rule. Fails on 52d4bb8 (the m13.5 manifest passes the m13.4 record; no rule read)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    wp = [1.012339, 1.017214, 0.793146]                                       # as P6a wrote it
    assert R.tinted_whitepoint(P5_ANCHOR, 1.132843) == pytest.approx(wp, abs=1e-5)

    def project(code, entry):
        name, scene, render = _wb_project(P5_ANCHOR, [entry], rig_rooms=())
        return name, scene, dict(render, render_code_version=code)

    def record(day, keep, **extra):
        gain = R.view_tint_gain(P5_ANCHOR, day, 0.35, keep_green_residual=keep)
        e = _wb_entry("cam_r_L0_e_yatak_odasi_2", "r_L0_e_yatak_odasi", R.tinted_whitepoint(P5_ANCHOR, gain),
                      share=0.009468, anchor=P5_ANCHOR, day_green=day, gain=gain)
        e["exposure"].update(extra)
        return e
    old = _wb_entry("cam_r_L0_e_yatak_odasi_2", "r_L0_e_yatak_odasi", wp, share=0.009468, anchor=P5_ANCHOR,
                    day_green=1.215422, gain=1.132843)
    gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(project("m13.4", old))
    with pytest.raises(AssertionError, match="no wb_day_green_source / wb_tint_green_residual"):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(project("m13.5", old))
    meta = dict(wb_day_green_source="walls", wb_day_green_all=1.242216, wb_day_wall_share=0.2947)
    for keep in (True, False):
        gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(
            project("m13.5", record(1.439585, keep, wb_tint_green_residual=keep, **meta)))
        with pytest.raises(AssertionError, match="tint gain off the recorded daylight green ratio"):
            gpu.test_views_keep_the_project_white_point_or_mix_it_with_the_rig(
                project("m13.5", record(1.439585, keep, wb_tint_green_residual=not keep, **meta)))


def test_p6a_gpu_olive_check_fails_pink_lower_walls(tmp_path, monkeypatch):
    """CPU replay of ``test_daylight_walls_are_not_olive``: a bedroom whose upper walls read green (1.10) and whose lower
    walls read pink (0.93) passes the olive pin on its mean (about 1.015) and now fails on the lower half
    (``DAYLIGHT_LOWER_WALL_GREEN_MIN``); the shim's m13.5 extreme (lower walls 0.965) passes, and the values (with the
    lower walls) are kept. Fails on 52d4bb8 (the pink view passes)."""
    import numpy as np

    from wenart import views

    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.DAYLIGHT_LOWER_WALL_GREEN_MIN == 0.95

    def two_tone(up, low):                                                    # R 120, B 100: G = 110 x green
        img = np.zeros((18, 32, 3), np.uint8)
        img[:9] = (120, round(110 * up), 100)
        img[9:] = (120, round(110 * low), 100)
        return img

    def check(case, up, low):
        out = tmp_path / case
        monkeypatch.setattr(gpu, "OUTPUTS", out)
        project = _wall_views(out, {"cam_r_bed_1": ("r_bed", 1.2, 0.0)}, room_types={"r_bed": "bedroom"},
                              entry_types=True)
        views.write_png_rgb(out / "real02" / "renders" / "cam_r_bed_1.png", two_tone(up, low))
        gpu.test_daylight_walls_are_not_olive(project)
        return json.loads((out / "real02" / "renders" / "gpu_check_values.json").read_text(encoding="utf-8"))
    kept = check("ok", 1.03, 0.965)
    view = kept["daylight_walls_are_not_olive"]["real02"]["views"]["cam_r_bed_1"]
    assert view["lower_wall_green"] == pytest.approx(0.964, abs=0.005) and view["wall_green"] < 1.06
    with pytest.raises(AssertionError, match=r"pink lower daylight walls .*cam_r_bed_1"):
        check("pink", 1.10, 0.93)
