"""Fix round after P6b (23 Oct 2026; pod P6b, real03 on 8e8cc97, runs/20261022-235127-fetch_results; render code
m13.5 kept; track G_render): CPU tests of the render record and of the GPU checks that come with it. Each test fails on
BASE 620997b or on the mutation its docstring names. No Blender needed.

- ``test_every_room_has_three_views`` keeps a room the area rule leaves without a view when its views are all replayed
  from the camera file (P4b and P6b real03 failed on the empty halls r_L0_oda_7 / r_L0_oda_10, one M11 view each).
- The orange check holds a view lit by the rig alone to the daylight median + 0.15 and a mixed view to the warmest
  daylight view of its kind + 0.05 (at most 0.35 over the median): P6b's mixed halls pass, P4b's 2700 K views, P4a's
  m13.2 halls and a hall over the cap still fail, P5 real04 passes as before.
- ``render.wall_rig_record`` / ``Look._view_white`` record the walls' own rig share and the rig light measured on the
  walls (``wb_walls``, the P6b verifier's step 1: measure first); no white point changes.
- The interior-glazing check keeps its values; its bound is unchanged.
"""
from __future__ import annotations

import copy
import hashlib
import json
import types
from pathlib import Path

import pytest

from test_blender_render import _gpu_test_module
from test_m13_light import P5_ANCHOR, _gpu_render_module, _wall_views
from test_m13_p6a_render import _manifest
from test_render_gpu_logic_m10 import EXAMPLE, _searched_scene, _write_building
from wenart.blender import render as R
from wenart.blender import schemas

ROOT = Path(__file__).resolve().parents[1]
P6B = ROOT / "runs" / "20261022-235127-fetch_results" / "results"
P4B = ROOT / "runs" / "20261017-091212-full" / "results"
CAMERA_FILE = ROOT / "results" / "renders" / "real03" / "scene_manifest.json"     # the M11 camera file both replayed
CAMERA_FILE_SHA = "ec9374cf04f626aeccd5d1cf3183bbb2b54f1245d4b43aa821f4b066a1d3f6b0"


# --------------------------------------------------------------------------
# Three views: rooms kept by their replayed views
# --------------------------------------------------------------------------

def _with_small_hall(building: dict) -> dict:
    """The example building with an empty 1.2 x 1.5 m hall on L0 (under camsearch's 2.5 m2: no view by the rule)."""
    b = copy.deepcopy(building)
    b["rooms"].append({"id": "r_L0_oda_7", "level_id": "L0", "label": "Oda", "room_type": "hall",
                       "polygon": [[6.3, 4.3], [7.5, 4.3], [7.5, 5.8], [6.3, 5.8]], "area_computed": 1.8,
                       "has_documented_furniture": False, "status": "verified", "evidence": []})
    return b


def _replay_project(tmp_path: Path, building: dict, path: Path, source="replayed", in_file=True, sha_ok=True,
                    searched_too=False):
    """``(name, scene, render)`` of a searched build of the example whose small hall has one view replayed from a
    camera file (the build leaves the hall out of ``rooms_without_view``, as real03's did)."""
    scene, render = _searched_scene(building, "base", path)
    assert "r_L0_oda_7" in {r["room_id"] for r in scene["rooms_without_view"]}          # the rule gives it no view
    cam = {"name": "cam_r_L0_oda_7_1", "room_id": "r_L0_oda_7", "level_id": "L0", "policy": "search",
           "kind": "interior", "source": source}
    cams = [cam] + ([dict(cam, name="cam_r_L0_oda_7_2", source=None)] if searched_too else [])
    record = {"name": "cam_r_L0_oda_7_1" if in_file else "cam_r_L0_oda_9_1", "room_id": "r_L0_oda_7",
              "level_id": "L0", "kind": "interior", "position": [6.5, 4.5, 1.25], "target": [7.4, 5.7, 1.25],
              "lens_mm": 16.0}
    data = json.dumps({"cameras": [record]}).encode("utf-8")
    camera_file = tmp_path / "cameras_m11.json"
    camera_file.write_bytes(data)
    scene = dict(scene, cameras=scene["cameras"] + cams,
                 rooms_without_view=[r for r in scene["rooms_without_view"] if r["room_id"] != "r_L0_oda_7"],
                 cameras_from={"path": str(camera_file), "replayed": 1, "extra": False,
                               "sha256": hashlib.sha256(data).hexdigest() if sha_ok else "0" * 64})
    render = {"renders": render["renders"] + [{"camera": c["name"]} for c in cams]}
    return "example", scene, render


def test_p6b_three_views_keep_a_room_whose_views_are_all_replayed(tmp_path, monkeypatch, capsys):
    """P4b and P6b real03 failed ``test_every_room_has_three_views`` the same way: the empty 1.86 / 1.89 m2 halls
    r_L0_oda_7 and r_L0_oda_10 get no view by the area rule, the camera file replays one M11 view of each, the build
    leaves them out of ``rooms_without_view``, and the set equalities used the rule alone. A room whose views are all
    replayed and named for it in the camera file is now kept. Still failing: the same view searched (not replayed),
    a replayed view the camera file does not name, a camera file whose sha256 is not the build's, and a searched view
    next to the replayed one, each at the "rooms_without_view" assertion. Fails on 620997b (the replayed hall fails
    "rooms_without_view") and with the camera file's names left out of ``_kept_by_replay``."""
    building = _with_small_hall(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    outputs = tmp_path / "outputs"
    path = _write_building(outputs, "example", building)
    gpu = _gpu_test_module(monkeypatch, outputs)
    gpu.test_every_room_has_three_views(_replay_project(tmp_path, building, path))
    assert "kept for their replayed views: ['r_L0_oda_7']" in capsys.readouterr().out
    for case in ({"source": "search"}, {"in_file": False}, {"sha_ok": False}, {"searched_too": True}):
        with pytest.raises(AssertionError, match=r"rooms_without_view \[\], the rule gives \['r_L0_oda_7'\]"):
            gpu.test_every_room_has_three_views(_replay_project(tmp_path, building, path, **case))
    # the helper on its own: no camera file read (None) keeps nothing; an agent's replacement of a replayed view counts
    by_room = {"r_a": [{"name": "cam_r_a_1", "source": "replayed"}],
               "r_b": [{"name": "cam_r_b_1", "policy": "agent", "replaced_replayed": True}],
               "r_c": [{"name": "cam_r_c_1", "source": "replayed"}, {"name": "cam_r_c_2", "policy": "agent"}]}
    files = {"r_a": {"cam_r_a_1"}, "r_b": {"cam_r_b_1"}, "r_c": {"cam_r_c_1"}}
    assert gpu._kept_by_replay({"r_a", "r_b", "r_c", "r_d"}, by_room, files) == {"r_a", "r_b"}
    assert gpu._kept_by_replay({"r_a"}, by_room, None) == set()
    assert gpu._kept_by_replay({"r_a"}, by_room, {"r_a": {"cam_r_a_2"}}) == set()       # the file names another view


@pytest.mark.skipif(not all((run / "renders" / "real03" / "scene_manifest.json").is_file() for run in (P6B, P4B))
                    or not CAMERA_FILE.is_file()
                    or hashlib.sha256(CAMERA_FILE.read_bytes()).hexdigest() != CAMERA_FILE_SHA,
                    reason="P6b / P4b runs or the committed real03 camera file not here")
@pytest.mark.parametrize("run", [P6B, P4B], ids=["P6b", "P4b"])
def test_p6b_three_views_pass_on_the_real03_runs(run, tmp_path, monkeypatch, capsys):
    """CPU replay of ``test_every_room_has_three_views`` on the P6b and P4b real03 manifests and final buildings (the
    camera file is the committed results/renders/real03/scene_manifest.json, sha256 ec9374cf both builds read): both
    pass and keep exactly r_L0_oda_7 and r_L0_oda_10. Fails on 620997b on both."""
    outputs = tmp_path / "outputs"
    (outputs / "real03").mkdir(parents=True)
    gpu = _gpu_test_module(monkeypatch, outputs)
    scene = json.loads((run / "renders" / "real03" / "scene_manifest.json").read_text(encoding="utf-8"))
    render = json.loads((run / "renders" / "real03" / "render_manifest.json").read_text(encoding="utf-8"))
    scene["building"] = str(run / "furniture" / "real03" / "building_final.json")
    assert scene["cameras_from"]["sha256"] == CAMERA_FILE_SHA
    gpu.test_every_room_has_three_views(("real03", scene, render))
    assert "kept for their replayed views: ['r_L0_oda_10', 'r_L0_oda_7']" in capsys.readouterr().out


# --------------------------------------------------------------------------
# The orange check: rig alone against the median, mixed views against the daylight spread
# --------------------------------------------------------------------------

# P6b real03 (logs/pytest-full.log): the painted daylight views' wall display R/B (rig share < 0.02, unblocked) ...
P6B_DAY = {"ebeveyn_odasi_1": 1.256, "ebeveyn_odasi_2": 1.3, "ebeveyn_odasi_2_1": 1.295, "ebeveyn_odasi_2_2": 1.288,
           "ebeveyn_odasi_2_3": 1.236, "ebeveyn_odasi_3_1": 1.485, "ebeveyn_odasi_3_2": 1.446,
           "ebeveyn_odasi_4_1": 1.289, "ebeveyn_odasi_4_2": 1.311, "ebeveyn_odasi_4_3": 1.303,
           "ebeveyn_odasi_5_3": 1.406, "ebeveyn_odasi_6_1": 1.54, "ebeveyn_odasi_6_2": 1.506,
           "ebeveyn_odasi_m_k_a_2_1": 1.425, "ebeveyn_odasi_m_k_a_2_3": 1.356, "oda_01_1": 1.54, "oda_01_2": 1.582,
           "oda_01_3": 1.533, "yasama_3_1": 1.43, "yasama_3_3": 1.307, "yasama_4_2": 1.241, "yasama_4_3": 1.211,
           "yasama_5_1": 1.388, "yasama_5_3": 1.294, "yasama_7_1": 1.188, "yasama_7_2": 1.361, "yasama_7_3": 1.238,
           "yasama_8_1": 1.183, "yasama_8_2": 1.21, "yasama_8_3": 1.209}
# ... and the painted rig-lit views (wall R/B, rig share; the render manifest) and three of the tiled baths
P6B_RIG = {"giris_holu_1": (1.492, 0.569178), "giris_holu_2": (1.599, 0.622621), "giris_holu_2_1": (1.52, 0.683587),
           "giris_holu_2_2": (1.515, 0.652607), "giris_holu_3_1": (1.535, 0.75514), "giris_holu_4_1": (1.486, 0.626547),
           "giris_holu_4_2": (1.583, 0.705595), "kat_holu_1": (1.436, 0.717718), "kat_holu_2": (1.423, 0.669383),
           "kat_holu_3": (1.451, 0.723666), "kat_merdiveni_1": (1.492, 0.723808), "kat_merdiveni_2": (1.446, 0.79578),
           "kat_merdiveni_3": (1.49, 0.761103), "oda_10_1": (1.425, 0.931057), "oda_7_1": (1.423, 0.985383),
           "ruzgarlik_1": (1.409, 0.437265), "yangin_merdiveni_1": (1.595, 0.889906),
           "yangin_merdiveni_2": (1.442, 0.955833), "yangin_merdiveni_3": (1.363, 0.979928)}
P6B_BATHS = {"banyo_2_1": (1.174, 0.776088), "banyo_5_1": (1.123, 1.0), "banyo_6_1": (1.138, 0.528767)}
# P4b real03 (2700 K rig, m13.2, the same project anchor): the views the old rule checked (share >= 0.8)
P4B_RIG = {"kat_merdiveni_2": (1.693, 0.856457), "kat_merdiveni_3": (1.734, 0.832486), "oda_10_1": (1.648, 0.895986),
           "oda_7_1": (1.665, 0.986547), "yangin_merdiveni_1": (1.864, 0.974565),
           "yangin_merdiveni_2": (1.756, 0.990217), "yangin_merdiveni_3": (1.562, 0.995399)}


def _views(day: dict, rig: dict, baths: dict | None = None) -> dict:
    out = {f"cam_r_L0_{c}": (f"r_{c}", rb, 0.0) for c, rb in day.items()}
    out.update({f"cam_r_L0_{c}": (f"r_{c}", rb, share) for c, (rb, share) in rig.items()})
    out.update({f"cam_r_L0_{c}": (f"r_{c}", rb, share) for c, (rb, share) in (baths or {}).items()})
    return out


def test_p6b_gpu_orange_check_judges_mixed_views_against_the_daylight_spread(tmp_path, monkeypatch):
    """P6b failed the orange check on 10 mixed views (rig share 0.57-0.89) at 1.486-1.599 against 1.455 (the painted
    daylight median 1.305 + 0.15), while the daylight-only oda_01 views of the same paint read 1.53-1.58 and the views
    lit by the rig alone 1.363-1.442: the P6b verifier refuted the white-point change (wall R/B does not rise with the
    frame's share). A view lit by the rig alone keeps the median + 0.15; a mixed view may reach the warmest daylight
    view + 0.05 (1.63 here, in 8 bits). P6b passes (in 8-bit images: the values to 0.01), P4b's seven 2700 K views each
    fail against P6b's own daylight walls (4 rig alone over 1.455, 3 mixed over 1.63), and the values file keeps each
    bound's regime and the warmest daylight view. Fails on 620997b (P6b's 10 mixed views over 1.455)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    wet = tuple(f"r_{c}" for c in P6B_BATHS)

    def check(case, views):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / case, views, wet))
        return json.loads((tmp_path / case / "real02" / "renders" / "gpu_check_values.json").read_text(
            encoding="utf-8"))["rig_lit_rooms_have_no_orange_cast"]["real02"]
    kept = check("p6b", _views(P6B_DAY, P6B_RIG, P6B_BATHS))
    assert (gpu.RIG_ALONE_SHARE, gpu.RIG_ROOM_ABOVE_WARMEST_DAY, gpu.RIG_ROOM_ABOVE_DAY_MAX) == (0.95, 0.05, 0.35)
    assert kept["references"]["painted"] == pytest.approx(1.305) and kept["warmest"]["painted"] == pytest.approx(1.58)
    rig = kept["rig_lit"]
    assert rig["cam_r_L0_giris_holu_2"]["regime"] == "mixed" and rig["cam_r_L0_giris_holu_2"]["bound"] == 1.63
    assert rig["cam_r_L0_yangin_merdiveni_2"]["regime"] == "rig alone"
    assert rig["cam_r_L0_yangin_merdiveni_2"]["bound"] == pytest.approx(1.455)
    assert rig["cam_r_L0_banyo_5_1"]["regime"] == "fixed" and rig["cam_r_L0_banyo_5_1"]["bound"] == 1.5
    assert kept["warm"] == [] and kept["rig_alone_share"] == 0.95
    for cam, (rb, share) in P4B_RIG.items():
        regime, bound = ("rig alone", 1.455) if share >= 0.95 else ("mixed", 1.63)
        written = int(round(100 * rb)) / 100                                  # the 8-bit value _wall_views writes
        with pytest.raises(AssertionError, match=rf"cam_r_L0_{cam}', {written}, 'painted', {bound}, "
                                                 rf"{share}, '{regime}'"):
            check(f"p4b_{cam}", _views(P6B_DAY, {cam: (rb, share)}))


def test_p6b_gpu_orange_bound_rules(tmp_path, monkeypatch):
    """``_orange_bound``: no daylight view of the kind gives the fixed 1.5; a share of 0.95 or more the median + 0.15;
    a mixed view the larger of that and the warmest daylight view + 0.05, the latter at most the median + 0.35. One odd
    daylight view (2.20 among 1.30 / 1.31) lets a mixed hall reach 1.66, not 2.25: a hall at 1.70 fails (it passes
    with the mutation RIG_ROOM_ABOVE_DAY_MAX = 10). P5 real04's values (its 11 painted daylight views and 15 rig-lit
    views) and P4a real02's m13.2 halls against the shim's daylight walls keep their verdicts: all pass, all fail. No
    bound is lower than the rule before (the median + 0.15, the fixed 1.5 without a daylight view), so no view that
    passed before (P6a real04) fails now; a share at 0.95 or over keeps it exactly."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    for share in (None, 0.0, 0.4, 0.62, 0.89, 0.949, 0.95, 0.99, 1.0):
        for median, warmest in ((1.305, 1.582), (1.515, 1.695), (1.36, 1.55), (1.30, 1.31), (1.31, 2.2)):
            bound, regime = gpu._orange_bound(share, median, warmest)
            assert bound >= round(median + gpu.RIG_ROOM_ABOVE_DAY, 3)
            assert (bound == round(median + 0.15, 3)) if regime == "rig alone" else regime == "mixed"
            assert regime == ("rig alone" if (share or 0.0) >= 0.95 else "mixed")
        assert gpu._orange_bound(share, None, None) == (gpu.RIG_ROOM_MAX_RB, "fixed")
    assert gpu._orange_bound(0.95, 1.305, 1.582) == (1.455, "rig alone")
    assert gpu._orange_bound(0.949, 1.305, 1.582) == (1.632, "mixed")
    assert gpu._orange_bound(0.6, 1.305, 1.33) == (1.455, "mixed")                 # a narrow spread: the median rule
    assert gpu._orange_bound(None, 1.305, 1.582) == (1.632, "mixed")
    assert gpu._orange_bound(0.7, None, None) == (1.5, "fixed")
    assert gpu._orange_bound(0.7, 1.31, 2.2) == (1.66, "mixed")
    monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / "odd")
    with pytest.raises(AssertionError, match=r"cam_r_hall_1', 1.7, 'painted', 1.66"):
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / "odd", {
            "cam_r_bed_1": ("r_bed", 1.30, 0.0), "cam_r_bed_2": ("r_bed", 1.31, 0.0),
            "cam_r_bed_3": ("r_bed", 2.20, 0.0), "cam_r_hall_1": ("r_hall", 1.70, 0.6)}))
    # P5 real04 (runs/20261017-224848-full): painted daylight 1.382-1.695 (median 1.515), the halls and kitchens
    p5_day = [1.44, 1.695, 1.423, 1.507, 1.613, 1.567, 1.539, 1.382, 1.533, 1.498, 1.515]
    p5_rig = [(1.634, 0.711), (1.534, 0.844), (1.61, 0.795), (1.415, 0.999), (1.406, 0.996), (1.421, 1.0),
              (1.306, 1.0), (1.323, 1.0), (1.307, 1.0), (1.37, 1.0), (1.314, 1.0), (1.39, 1.0), (1.139, 0.667),
              (1.158, 0.601), (1.223, 0.682)]
    median = sorted(p5_day)[len(p5_day) // 2]
    assert all(rb <= gpu._orange_bound(s, median, max(p5_day))[0] for rb, s in p5_rig)
    # P4a real02 (m13.2, runs/20261017-072801-full): halls 1.639-1.808 at 0.90-1.0; the shim's daylight walls
    # (the fix round after P4a) median 1.36, warmest 1.55
    p4a = [(1.77, 0.9), (1.769, 0.974), (1.654, 0.943), (1.808, 1.0), (1.765, 1.0), (1.755, 1.0), (1.73, 1.0),
           (1.706, 1.0), (1.639, 0.999), (1.657, 0.999), (1.643, 1.0), (1.709, 1.0)]
    assert all(rb > gpu._orange_bound(s, 1.36, 1.55)[0] for rb, s in p4a)


def test_p6b_gpu_orange_check_keeps_the_light_on_the_walls(tmp_path, monkeypatch, capsys):
    """The orange check prints and keeps the light on the walls of every view it reads, rig-lit and daylight
    (``_walls_record`` of ``wb_walls``: the linear R/B of the walls' light with everything lit and with the rig hidden,
    the walls' rig share, the rig light's R/B and Kelvin measured on the walls, the lamp's R/B), None for a record
    without it (a render before this round); the verdict does not read it (the same views without the records give
    the same bounds). The values are P6b shim records: giris_holu_2 (light R/B 3.68, daylight 3.07, rig 4.17 against
    the lamp's 2.65) and the daylight-only oda_01_2 (3.35). Fails on 620997b (no wall_light_rb in the values)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    oda_01_2 = {"share": 0.6367, "rig_share": 0.0, "light_rgb": [1.526784, 0.898405, 0.455212],
                "day_rgb": [1.522816, 0.899191, 0.459111], "rig_rgb": None, "rig_rb": None, "lamp_rb": 10.0668,
                "rig_kelvin": None}
    views = {"cam_r_bed_1": ("r_bed", 1.30, 0.0), "cam_r_bed_2": ("r_bed", 1.58, 0.0),
             "cam_r_hall_1": ("r_hall", 1.60, 0.62), "cam_r_hall_2": ("r_hall", 1.41, 0.7)}

    def check(case, exposure):
        monkeypatch.setattr(gpu, "OUTPUTS", tmp_path / case)
        gpu.test_rig_lit_rooms_have_no_orange_cast(_wall_views(tmp_path / case, views, exposure=exposure))
        return json.loads((tmp_path / case / "real02" / "renders" / "gpu_check_values.json").read_text(
            encoding="utf-8"))["rig_lit_rooms_have_no_orange_cast"]["real02"]
    kept = check("w", {"cam_r_hall_1": {"wb_walls": dict(GIRIS_HOLU_2, rig_kelvin=3284.1)},
                       "cam_r_bed_2": {"wb_walls": oda_01_2}})
    hall, hall_2 = kept["rig_lit"]["cam_r_hall_1"], kept["rig_lit"]["cam_r_hall_2"]
    bed = kept["daylight"]["cam_r_bed_2"]
    assert hall["wall_light_rb"] == pytest.approx(3.6805, abs=1e-4) and hall["wall_day_rb"] == pytest.approx(3.0699,
                                                                                                         abs=1e-4)
    assert hall["wall_rig_share"] == 0.593776 and hall["wall_rig_kelvin"] == 3284.1
    assert hall["wall_rig_rb"] == 4.1708 and hall["lamp_rb"] == 2.6511
    assert bed["wall_light_rb"] == pytest.approx(3.354, abs=1e-3) and bed["wall_rig_rb"] is None
    assert bed["wall_rb"] == 1.58 and kept["daylight"]["cam_r_bed_1"]["wall_light_rb"] is None
    assert all(hall_2[k] is None for k in ("wall_light_rb", "wall_day_rb", "wall_rig_share", "wall_rig_rb",
                                           "wall_rig_kelvin", "lamp_rb"))
    assert "the light on the walls (render wb_walls" in capsys.readouterr().out
    # the verdict does not read the record: the same views without it give the same bounds
    plain = check("plain", {})
    assert {c: (v["bound"], v["regime"]) for c, v in plain["rig_lit"].items()} == \
        {c: (v["bound"], v["regime"]) for c, v in kept["rig_lit"].items()}
    assert hall["bound"] == 1.63 and hall["regime"] == "mixed"


# --------------------------------------------------------------------------
# The walls' own rig record (render.wall_rig_record, Look._view_white)
# --------------------------------------------------------------------------

# bpy 5.2.2 shim of P6b's real03.blend (final/real03/3d, 240 x 135, 16 spp, the two metering passes of render.py with
# the walls metered): cam_r_L0_giris_holu_2's record (frame share 0.594 on the shim, 0.623 on the pod)
GIRIS_HOLU_2 = {"share": 0.5789, "rig_share": 0.593776, "light_rgb": [1.581745, 0.884637, 0.429763],
                "day_rgb": [1.446513, 0.920654, 0.471191], "rig_rb": 4.1708, "lamp_rb": 2.6511}


def test_p6b_wall_rig_record_measures_the_rig_light_on_the_walls():
    """``wall_rig_record``: the walls' rig share from the two passes' wall light and the colour of the rig light on
    the walls (all-light minus daylight, luminance 1), next to the lamp's R/B. The shim record of P6b's giris_holu_2
    is reproduced from its two wall colours and share: the walls' rig share 0.594 (the frame's on the same shim:
    0.594) and the rig light on the walls R/B 4.17 (about 3,280 K) against the 4000 K lamp's 2.65. Edge cases: no wall
    metering (None), no wall light (no share), a daylight pass without walls (no share), a walls' share under
    ``WB_RIG_SHARE_MIN`` or a negative channel (no rig colour), walls without daylight (share 1, the rig colour is the
    walls' light). Fails on 620997b (no ``wall_rig_record``)."""
    lum = R.luminance
    total = 1000.0
    all_wall = [v * total for v in GIRIS_HOLU_2["light_rgb"]]
    day_lum = (1.0 - GIRIS_HOLU_2["rig_share"]) * total
    day_wall = [v * day_lum for v in GIRIS_HOLU_2["day_rgb"]]
    lamp = R.normalise_whitepoint([2.6511, 1.0, 1.0])
    rec = R.wall_rig_record({"wall_illuminant": all_wall, "wall_frac": 0.5789},
                            {"wall_illuminant": day_wall, "wall_frac": 0.5789}, lamp)
    assert rec["share"] == 0.5789 and rec["rig_share"] == pytest.approx(0.593776, abs=2e-6)
    assert rec["rig_rb"] == pytest.approx(4.1708, abs=2e-3) and rec["lamp_rb"] == pytest.approx(2.6511, abs=1e-4)
    assert rec["light_rgb"] == pytest.approx(GIRIS_HOLU_2["light_rgb"], abs=1e-5)
    assert rec["day_rgb"] == pytest.approx(GIRIS_HOLU_2["day_rgb"], abs=1e-5)
    assert float(lum(rec["rig_rgb"])) == pytest.approx(1.0, abs=1e-5) and rec["rig_kelvin"] is None
    assert rec["rule"] == R.WALL_RIG_RULE and "measured only" in rec["rule"]
    # hand-made light
    rec = R.wall_rig_record({"wall_illuminant": [3.0, 2.0, 1.2], "wall_frac": 0.4},
                            {"wall_illuminant": [1.0, 1.0, 1.0]})
    assert rec["rig_share"] == pytest.approx(1.0 - 1.0 / float(lum([3.0, 2.0, 1.2])), abs=1e-6)
    assert rec["rig_rgb"] == pytest.approx(R.normalise_whitepoint([2.0, 1.0, 0.2]), abs=1e-6) and rec["rig_rb"] == 10.0
    assert rec["lamp_rb"] is None
    assert R.wall_rig_record(None, {}) is None
    assert R.wall_rig_record({"illuminant": [1.0, 1.0, 1.0]}, {}) is None              # a meter without walls
    none = R.wall_rig_record({"wall_illuminant": None, "wall_frac": 0.0}, {"wall_illuminant": None})
    assert none["rig_share"] is None and none["rig_rgb"] is None and none["light_rgb"] is None
    nowalls = R.wall_rig_record({"wall_illuminant": [1.0, 1.0, 1.0], "wall_frac": 0.3}, {"illuminant": [1, 1, 1]})
    assert nowalls["rig_share"] is None and nowalls["light_rgb"] == pytest.approx([1.0, 1.0, 1.0])
    low = R.wall_rig_record({"wall_illuminant": [1.0, 1.0, 1.0]}, {"wall_illuminant": [0.99, 0.99, 0.99]})
    assert low["rig_share"] == pytest.approx(0.01) and low["rig_rgb"] is None
    neg = R.wall_rig_record({"wall_illuminant": [1.0, 1.0, 1.0]}, {"wall_illuminant": [0.5, 0.5, 1.1]})
    assert neg["rig_share"] > R.WB_RIG_SHARE_MIN and neg["rig_rgb"] is None and neg["rig_rb"] is None
    dark = R.wall_rig_record({"wall_illuminant": [2.0, 1.0, 0.5]}, {"wall_illuminant": None})
    assert dark["rig_share"] == 1.0 and dark["rig_rgb"] == pytest.approx(R.normalise_whitepoint([2.0, 1.0, 0.5]))


def test_p6b_view_white_records_the_walls_and_keeps_the_white_point(tmp_path, monkeypatch):
    """``Look._view_white`` records ``wb_walls`` from the all-light pass (``_decide`` meters the walls of a
    project-balanced interior view since the fix round after P6a) and the daylight pass, with ``rig_kelvin`` Blender's
    reading of the rig light on the walls (``whitepoint_kelvin``) and ``lamp_rb`` the rig lamp's colour the white point
    mixes; the white point and every other field are those of the same view metered without the walls. The record is
    valid in the render manifest schema. A view under the rig-share floor records it too; without a wall metering it is
    None. Fails on 620997b (no ``wb_walls``)."""
    look = object.__new__(R.Look)
    look.scene, look.windows, look.haze, look.room_types = {}, set(), set(), {}
    look.project = {"residual": 0.35, "whitepoint": list(P5_ANCHOR), "source": "s"}
    lamp = R.normalise_whitepoint([1.5, 1.0, 0.566])
    kelvin_calls = []
    day = {"illuminant": [1.0, 1.0, 0.9], "incident_p50": 0.01, "seconds": 0.1,
           "wall_illuminant": [0.5, 0.5, 0.45], "wall_frac": 0.3}
    monkeypatch.setattr(R, "rig_objects", lambda scene: ["rig"])
    monkeypatch.setattr(R, "rig_lights", lambda scene: [("r_hall", 4000.0, 10.0)])
    monkeypatch.setattr(R, "hide_objects", lambda objs: [])
    monkeypatch.setattr(R, "unhide_objects", lambda saved: None)
    monkeypatch.setattr(R, "meter_camera", lambda *a, **kw: dict(day))
    monkeypatch.setattr(R, "kelvin_whitepoint", lambda scene, k: lamp)
    monkeypatch.setattr(R, "whitepoint_kelvin", lambda scene, wp: kelvin_calls.append(list(wp)) or (3284.1, 3.2))
    cam = types.SimpleNamespace(name="cam_r_hall_1",
                                get={"wenart_room": "r_hall", "wenart_camera_kind": "interior"}.get)

    def view(all_stats):
        rec = {"whitepoint": list(P5_ANCHOR), "meter_seconds": 1.0}
        look._view_white(cam, rec, all_stats, tmp_path, (64, 36))
        return rec
    lit = {"illuminant": [3.0, 2.4, 1.5], "incident_p50": 0.03, "wall_illuminant": [1.6, 1.1, 0.6], "wall_frac": 0.3}
    rec = view(lit)
    plain = view({k: v for k, v in lit.items() if not k.startswith("wall")})
    walls = rec["wb_walls"]
    assert walls == R.wall_rig_record(lit, day, lamp) | {"rig_kelvin": 3284.1}
    assert walls["rig_share"] == pytest.approx(R.rig_share([1.6, 1.1, 0.6], [0.5, 0.5, 0.45]))
    assert walls["lamp_rb"] == pytest.approx(1.5 / 0.566, abs=1e-4) and kelvin_calls == [walls["rig_rgb"]]
    assert plain["wb_walls"] is None
    assert {k: v for k, v in rec.items() if k != "wb_walls"} == {k: v for k, v in plain.items() if k != "wb_walls"}
    assert rec["whitepoint"] == plain["whitepoint"] != list(P5_ANCHOR)          # mixed with the rig, as before
    schemas.validate_render_manifest(_manifest({"exposure": dict(_manifest({})["renders"][0]["exposure"],
                                                                 wb_walls=walls)}))
    # under the rig-share floor: the record is still written, the white point is the anchor's (with its tint)
    monkeypatch.setattr(R, "meter_camera", lambda *a, **kw: dict(day, illuminant=[2.99, 2.39, 1.49]))
    low = view(dict(lit, illuminant=[3.0, 2.4, 1.5]))
    assert low["wb_rig_share"] < R.WB_RIG_SHARE_MIN and low["wb_walls"]["rig_share"] is not None


# --------------------------------------------------------------------------
# The interior-glazing check keeps its values
# --------------------------------------------------------------------------

def test_p6b_gpu_glazing_check_keeps_its_values(tmp_path, monkeypatch):
    """``test_interior_glazing_keeps_one_white_point`` keeps every view's pane and wall R/B (with the view's rig share
    and the light on its own walls, ``_walls_record``) in ``gpu_check_values.json`` whatever the verdict: P6b's three
    named real03 views still fail at the unchanged 0.3 (0.692 / 0.321 / -0.398) with their values kept, and a project
    without named views (real02) is skipped with its values kept. Fails on 620997b (no values file)."""
    gpu = _gpu_render_module(monkeypatch, tmp_path)
    assert gpu.INTERIOR_GLAZING_MAX_DELTA == 0.3
    results = tmp_path / "results"
    monkeypatch.setenv("WENART_RESULTS", str(results))
    p6b = {"cam_r_L0_yasama_8_3": (1.901, 1.209, 0.0), "cam_r_L0_ebeveyn_odasi_2_1": (1.616, 1.295, 0.015617),
           "cam_r_L0_yangin_merdiveni_1": (1.197, 1.595, 0.889906), "cam_r_L0_kat_holu_1": (2.164, 1.436, 0.717718)}

    stair = {"light_rgb": [1.649542, 0.867126, 0.403591], "day_rgb": [1.481038, 0.904521, 0.529336],
             "rig_share": 0.902754, "rig_rb": 4.2756, "rig_kelvin": 3284.7, "lamp_rb": 2.6511}   # the P6b shim's

    def project(name, views):
        renders = [{"camera": c, "room_id": "r", "exposure": {"wb_rig_share": s} | (
                        {"wb_walls": stair} if c == "cam_r_L0_yangin_merdiveni_1" else {}),
                    "interior_glazing": {"pane_rb": p, "wall_rb": w, "delta_rb": round(p - w, 3),
                                         "windows": ["win_L0_055"], "pane_px": 900, "rule": "r"}}
                   for c, (p, w, s) in views.items()]
        return name, {}, {"renders": renders}
    with pytest.raises(AssertionError, match="two white points"):
        gpu.test_interior_glazing_keeps_one_white_point(project("real03", p6b))
    with pytest.raises(pytest.skip.Exception):
        gpu.test_interior_glazing_keeps_one_white_point(project("real02", {"cam_r_L1_koridor_1": (1.3, 1.31, 1.0)}))
    data = json.loads((results / "gpu_check_values.json").read_text(encoding="utf-8"))
    data = data["interior_glazing_keeps_one_white_point"]
    real03 = data["real03"]
    assert real03["named"] == list(gpu.INTERIOR_GLAZING_VIEWS["real03"]) and real03["max_delta"] == 0.3
    assert real03["views"]["cam_r_L0_yasama_8_3"]["delta_rb"] == 0.692
    assert real03["views"]["cam_r_L0_kat_holu_1"]["rig_share"] == 0.717718
    assert real03["views"]["cam_r_L0_yangin_merdiveni_1"]["wall_light_rb"] == pytest.approx(4.0871, abs=1e-4)
    assert real03["views"]["cam_r_L0_yangin_merdiveni_1"]["wall_rig_kelvin"] == 3284.7
    assert real03["views"]["cam_r_L0_kat_holu_1"]["wall_light_rb"] is None                 # no record: None
    assert data["real02"]["named"] == [] and set(data["real02"]["views"]) == {"cam_r_L1_koridor_1"}
