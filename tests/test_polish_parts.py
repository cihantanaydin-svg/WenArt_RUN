"""CPU tests of the pure polish parts (docs/milestone5.md §3.2-§3.6, §9 "polish").

Sigma tails and sigma0 (numpy replication of the diffusers 0.40.0 scheduler
maths, shift 3), size plans (pad/crop and resize round trips), control
images, the prompt and its word tables, pane restore, the room-rule helpers,
the ladder outcome, the attempt lists of polish.yaml and the manifest schema.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from wenart import views as V
from wenart.polish import config as PC
from wenart.polish import controls as CT
from wenart.polish import panes as PN
from wenart.polish import prompt as PR
from wenart.polish import rooms as RM
from wenart.polish import schedule as S
from wenart.polish import sizing as SZ
from wenart.polish import zimage as ZI
from wenart.polish.runner import accepted, attempt_key, ladder_outcome, write_preview
from wenart.polish.schema import validate_determinism, validate_manifest
from wenart.style import vocabulary as VOC

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# Sigma schedule (§3.2)
# --------------------------------------------------------------------------

def test_default_sigmas_match_torch_linspace_for_8_steps():
    assert S.default_sigmas(8) == [1.0, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]
    assert S.default_sigmas(1) == [1.0]
    nine = S.default_sigmas(9)
    assert len(nine) == 9 and nine[0] == 1.0 and abs(nine[-1] - 1 / 9) < 1e-7
    assert all(a > b for a, b in zip(nine, nine[1:]))
    with pytest.raises(ValueError):
        S.default_sigmas(0)


def test_shifted_schedule_of_8_steps_with_shift_3():
    shifted = S.shift_sigmas(S.default_sigmas(8), 3.0)
    expected = [1.0, 0.9545, 0.9, 0.8333, 0.75, 0.6429, 0.5, 0.3]
    assert np.allclose(shifted, expected, atol=5e-5)
    # The scheduler appends the terminal sigma 0 (a target, not a forward).
    assert S.scheduler_sigmas([0.25, 0.125]) == pytest.approx([0.5, 0.3, 0.0], abs=1e-6)
    # N = 9 (research table) for comparison.
    nine = S.shift_sigmas(S.default_sigmas(9))
    assert np.allclose(nine, [1.0, 0.96, 0.913, 0.8571, 0.7895, 0.7059, 0.6, 0.4615, 0.2727], atol=5e-4)


@pytest.mark.parametrize("strength, steps_run, sigma_start", [
    (0.125, 1, 0.30), (0.25, 2, 0.50), (0.375, 3, 0.643), (0.5, 4, 0.75),   # §3.2 table (shift 3)
    (0.75, 6, 0.90),                                                         # presumed_bad
    (0.3, 3, 0.643), (0.15, 2, 0.50), (1.0, 8, 1.0),
])
def test_sigma_tail_and_sigma0(strength, steps_run, sigma_start):
    tail = S.sigma_tail(8, strength)
    assert len(tail) == steps_run
    assert tail == S.default_sigmas(8)[8 - steps_run:]          # the tail of the default sigmas
    assert S.sigma0(tail) == pytest.approx(sigma_start, abs=5e-4)
    sch = S.schedule(8, strength)
    assert sch["forwards"] == steps_run and sch["t_start"] == 8 - steps_run
    assert sch["sigma0"] == pytest.approx(sigma_start, abs=5e-4) and sch["shift"] == 3.0
    assert sch["shifted"][0] == sch["sigma0"]


def test_sigma_tail_errors():
    with pytest.raises(ValueError):
        S.sigma_tail(8, 0.0)          # no step left
    with pytest.raises(ValueError):
        S.t_start(8, 1.5)
    with pytest.raises(ValueError):
        S.sigma0([])


def test_t_start_equals_diffusers_get_timesteps_formula():
    for n in (4, 8, 12, 16):
        for strength in np.linspace(0.05, 1.0, 20):
            init = min(n * strength, n)
            assert S.t_start(n, strength) == int(max(n - init, 0))


# --------------------------------------------------------------------------
# Sizes (§3.3)
# --------------------------------------------------------------------------

def test_native_plan_pads_1080_to_1088_four_pixels_each_side():
    plan = SZ.plan_size("native", (1920, 1080))
    assert plan.mode == "native" and plan.model == (1920, 1088) and plan.pad == (0, 4, 0, 4)
    odd = SZ.plan_size("native", (70, 45))
    assert odd.model == (80, 48) and odd.pad == (5, 1, 5, 2)
    assert SZ.plan_size(None, (64, 48)).pad == (0, 0, 0, 0)


def test_native_pad_and_crop_round_trip_is_exact():
    rng = np.random.default_rng(1)
    img = rng.integers(0, 256, size=(45, 70, 3), dtype=np.uint8)
    plan = SZ.plan_size("native", (70, 45))
    padded = SZ.to_model(img, plan)
    assert padded.shape == (48, 80, 3)
    # Reflect padding: the first padded row mirrors row 1 (the edge row is not repeated).
    assert np.array_equal(padded[0, 5:75], img[1])
    assert np.array_equal(SZ.from_model(padded, plan), img)
    grey = rng.integers(0, 256, size=(45, 70), dtype=np.uint8)
    assert np.array_equal(SZ.from_model(SZ.to_model(grey, plan), plan), grey)


def test_resize_plan_round_trip_is_close():
    y, x = np.mgrid[0:90, 0:160]
    img = np.stack([x * 1.5, y * 2.5, (x + y)], axis=2).clip(0, 255).astype(np.uint8)
    plan = SZ.plan_size("128x64", (160, 90))
    assert plan.mode == "resize" and plan.model == (128, 64)
    small = SZ.to_model(img, plan)
    assert small.shape == (64, 128, 3)
    back = SZ.from_model(small, plan)
    assert back.shape == img.shape
    assert np.abs(back.astype(int) - img.astype(int))[4:-4, 4:-4].mean() < 2.0


@pytest.mark.parametrize("bad", ["1536x860", "abc", "16x", "0x16", "1536X864X2"])
def test_bad_sizes_are_rejected(bad):
    with pytest.raises(ValueError):
        SZ.parse_size(bad)


def test_size_plan_shape_checks():
    plan = SZ.plan_size("native", (64, 40))
    with pytest.raises(ValueError):
        SZ.to_model(np.zeros((41, 64, 3), np.uint8), plan)
    with pytest.raises(ValueError):
        SZ.from_model(np.zeros((40, 64, 3), np.uint8), plan)


# --------------------------------------------------------------------------
# Control images (§3.4)
# --------------------------------------------------------------------------

def toy_passes(h=40, w=64):
    index = np.zeros((h, w), dtype=np.uint16)
    depth = np.full((h, w), 4000, dtype=np.uint16)
    normal = np.zeros((h, w, 3), dtype=np.float32)
    normal[:10] = [0, 0, -1]
    normal[10:28] = [0, 1, 0]
    normal[28:] = [0, 0, 1]
    depth[28:] = np.linspace(3000, 1000, h - 28).astype(np.uint16)[:, None]
    index[24:34, 8:24] = 3
    depth[24:34, 8:24] = 1500
    normal[24:34, 8:24] = [1, 0, 0]
    index[6:26, 36:60] = 2
    depth[0:2, 0:6] = 0
    normal[0:2, 0:6] = 0
    return index, depth, normal


def test_depth_control_near_is_bright_and_background_black():
    _, depth, _ = toy_passes()
    ctrl = CT.depth_control(depth)
    assert ctrl.shape == depth.shape + (3,) and ctrl.dtype == np.uint8
    assert np.array_equal(ctrl[..., 0], ctrl[..., 1]) and np.array_equal(ctrl[..., 0], ctrl[..., 2])
    assert (ctrl[0:2, 0:6] == 0).all()                       # no surface
    valid = depth > 0
    vals = depth[valid].astype(float)
    vmin, vmax = np.percentile(vals, 2), np.percentile(vals, 85)
    x = 1 - np.clip((depth.astype(float) - vmin) / (vmax - vmin), 0, 1)
    assert np.abs(ctrl[..., 0][valid].astype(int) - np.rint(x[valid] * 255)).max() <= 1
    assert ctrl[39, 30, 0] > ctrl[30, 30, 0]                  # nearer floor row is brighter
    assert ctrl[5, 5, 0] == 0 or ctrl[5, 5, 0] < ctrl[39, 30, 0]
    assert (CT.depth_control(np.zeros((4, 4), np.uint16)) == 0).all()
    flat = CT.depth_control(np.full((4, 4), 2000, np.uint16))
    assert (flat == 255).all()                                # one depth: everything "near"


def test_canny_control_is_white_on_black():
    img = np.zeros((40, 64, 3), np.uint8)
    img[10:30, 20:44] = 220
    ctrl = CT.canny_control(img)
    assert set(np.unique(ctrl).tolist()) <= {0, 255} and ctrl.max() == 255
    assert ctrl[20, 32].sum() == 0 and ctrl[0, 0].sum() == 0


def test_geometry_control_is_the_view_edges_dilated_to_2_px():
    index, depth, normal = toy_passes()
    edges = V.geometry_edges(index, depth, normal)
    ctrl = CT.geometry_control(index, depth, normal)
    on = ctrl[..., 0] == 255
    assert set(np.unique(ctrl).tolist()) == {0, 255}
    assert on[edges].all()                                    # every geometry edge is in the control
    assert on.sum() > edges.sum() and on.sum() <= 4 * edges.sum()
    # A horizontal 1 px edge becomes 2 px thick.
    col = 50
    rows = np.flatnonzero(edges[:, col])
    r = rows[0]
    assert on[r, col] and (on[r - 1, col] or on[r + 1, col])
    with pytest.raises(ValueError):
        CT.make_control("hed", None)


def test_write_control_keeps_an_identical_file(tmp_path):
    arr = CT.depth_control(toy_passes()[1])
    path, sha = CT.write_control(arr, tmp_path / CT.control_filename("cam_a", "depth"))
    assert path.name == "cam_a_control_depth.png" and np.array_equal(V.read_rgb(path), arr)
    mtime = path.stat().st_mtime_ns
    path2, sha2 = CT.write_control(arr.copy(), path)
    assert sha2 == sha and path.stat().st_mtime_ns == mtime
    _, sha3 = CT.write_control(255 - arr, path)
    assert sha3 != sha
    assert CT.CONTROL_TYPES == PC.CONTROL_TYPES


# --------------------------------------------------------------------------
# Prompt (§3.5)
# --------------------------------------------------------------------------

def test_word_tables_cover_every_vocabulary_slug_room_and_furniture_type():
    for slug in list(VOC.MATERIALS) + list(VOC.FURNITURE_MATERIALS):
        assert slug in PR.MATERIAL_WORDS, slug
    for mood in VOC.LIGHTING:
        assert mood in PR.MOOD_WORDS, mood
    for family, _ in VOC.STYLE_FAMILIES:
        assert family in PR.FAMILY_WORDS, family
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    rooms = schema["$defs"]["room"]["properties"]["room_type"]["enum"]
    furniture = schema["$defs"]["furniture"]["properties"]["type"]["enum"]
    assert set(rooms) <= set(PR.ROOM_WORDS)
    assert set(furniture) - {"unknown"} <= set(PR.FURNITURE_WORDS)
    assert "unknown" not in PR.FURNITURE_WORDS


def committed_profile(project="synthetic-01") -> dict:
    scene = json.loads((ROOT / "results" / "renders" / project / "scene_manifest.json").read_text(encoding="utf-8"))
    return scene["style_profile"]


def test_prompt_of_the_synthetic_01_living_room():
    out = PR.build_prompt(committed_profile(), "living", ["sofa", "armchair", "table_coffee"])
    assert out["prompt"] == (
        "Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak "
        "wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, "
        "realistic materials and textures, sharp focus, 24 mm lens.")
    assert out["family"] == "scandinavian" and out["walls"] == "plaster_white" and out["floor"] == "wood_oak_light"
    assert out["mood"] == "warm daylight" and out["warnings"] == []


def test_prompt_uses_the_wet_room_slots_and_the_rendered_profile():
    out = PR.build_prompt(committed_profile(), "bathroom", ["washbasin", "toilet"])
    assert "Light ceramic tile walls, light ceramic tile floor, washbasin, toilet." in out["prompt"]
    assert out["prompt"].startswith("Photorealistic interior photograph of a bathroom in Scandinavian style.")
    hall = PR.build_prompt(committed_profile("synthetic-03"), "hall", [])
    assert "hallway" in hall["prompt"] and "Charcoal grey plaster walls, polished concrete floor." in hall["prompt"]


def test_prompt_fallbacks_are_listed_in_warnings():
    profile = {"source_text": "something plain", "walls": {"material": "plaster_new"}, "floor": {"material": "carpet"}}
    out = PR.build_prompt(profile, "attic", ["unknown", "sofa", "robot"])
    p = out["prompt"]
    assert p.startswith("Photorealistic interior photograph of a room. ")    # no family, unknown room type
    assert "Plaster new walls, carpet floor, sofa, robot." in p
    assert p.endswith("Natural light through the windows, soft natural shadows, realistic materials and textures, "
                      "sharp focus, 24 mm lens.")
    assert out["furniture"] == ["sofa", "robot"]
    text = " ".join(out["warnings"])
    for word in ("attic", "plaster_new", "robot", "style family", "light mood"):
        assert word in text, word
    empty = PR.build_prompt({}, None, [])
    assert empty["prompt"].startswith("Photorealistic interior photograph of a room. Natural light")


def test_prompt_takes_the_profile_family_and_the_milestone_7_words():
    # docs/milestone7.md §6.3/§6.5: the profile's family field wins; dining/prayer rooms and the new types have words.
    profile = dict(committed_profile(), family="japandi")
    out = PR.build_prompt(profile, "dining", ["table_dining", "chair", "side_table", "floor_lamp"])
    assert out["prompt"].startswith("Photorealistic interior photograph of a dining room in Japandi style.")
    assert "dining table, chair, side table, floor lamp." in out["prompt"] and out["family"] == "japandi"
    assert PR.build_prompt(dict(profile, family=None), "prayer", [])["family"] == "scandinavian"   # old derivation
    assert PR.build_prompt(profile, "prayer", [])["prompt"].startswith(
        "Photorealistic interior photograph of a prayer room in Japandi style.")
    hall = PR.build_prompt(profile, "hall", ["stair", "potted_plant"])
    assert "staircase, potted plant." in hall["prompt"] and hall["warnings"] == []


def test_furniture_types_from_expected_elements():
    def el(t, pixels, kind="furniture", own=True, role="required", status="verified"):
        return {"type": t, "pixels": pixels, "kind": kind, "own_room": own, "role": role, "status": status}
    expected = {"elements": [
        el("chair", 50), el("sofa", 900), el("chair", 300), el("plant", 800, kind="decor"),
        el("bed_double", 700, own=False), el("tv_unit", 100, role="optional"), el("desk", 90, role="ignore"),
        el("unknown", 600), el("wardrobe", 500, status="unverified"), el("door", 1000, kind="door"),
    ] + [el(f"t{i}", 10 - i, role="optional") for i in range(10)]}
    types = PR.furniture_types(expected)
    assert types[:3] == ["sofa", "chair", "tv_unit"] and len(types) == 8
    assert PR.furniture_types(None) == [] and PR.furniture_types({"elements": []}) == []


# --------------------------------------------------------------------------
# Window panes (§3.2 last bullet)
# --------------------------------------------------------------------------

TABLE = {2: {"wenart_id": "win_1", "kind": "window"}, 3: {"wenart_id": "f_1", "kind": "furniture"},
         4: {"wenart_id": "win_2", "kind": "window"}}


def test_restore_panes_pastes_the_eroded_window_with_a_feather():
    index = np.zeros((40, 64), np.uint16)
    index[4:30, 30:60] = 2           # 26 x 30 window
    index[30:36, 2:8] = 4            # too small: nothing left after a 6 px erosion
    index[10:20, 5:20] = 3
    cycles = np.full((40, 64, 3), 100, np.uint8)
    polished = np.full((40, 64, 3), 180, np.uint8)
    out, n = PN.restore_panes(polished, cycles, index, TABLE)
    assert n == 1
    core = V.erode(index == 2, 6)
    assert (out[core] == 100).all()                               # the pane is the Cycles pixels
    assert (out[index != 2] == 180).all()                         # nothing outside the window changes
    band = (index == 2) & ~core & ~V.erode(index == 2, 3)         # the outer 3 px of the frame
    assert (out[band] == 180).all()
    feather = (index == 2) & ~core & V.erode(index == 2, 3)
    vals = out[feather][:, 0]
    assert ((vals >= 100) & (vals <= 180)).all()                  # 3 px feather inside the frame
    # Along a straight side the ramp is 1 - d / 4 for d = 1, 2, 3 px from the pane (rows 9, 8, 7).
    assert out[7:10, 45, 0].tolist() == [160, 140, 120] and out[10, 45, 0] == 100
    alpha, n2 = PN.pane_alpha(index, TABLE)
    assert n2 == 1 and alpha.max() == 1.0 and alpha[index != 2].max() == 0.0
    same, n0 = PN.restore_panes(polished, cycles, np.zeros((40, 64), np.uint16), TABLE)
    assert n0 == 0 and np.array_equal(same, polished)
    with pytest.raises(ValueError):
        PN.restore_panes(polished[:-1], cycles, index, TABLE)
    assert PN.window_indices(TABLE) == [2, 4]


# --------------------------------------------------------------------------
# Room rule helpers (§3.6)
# --------------------------------------------------------------------------

def test_srgb_to_lab_reference_values():
    lab = RM.srgb_to_lab(np.array([[255, 255, 255], [0, 0, 0], [255, 0, 0], [128, 128, 128]], np.uint8))
    assert lab[0] == pytest.approx([100.0, 0.0, 0.0], abs=0.02)
    assert lab[1] == pytest.approx([0.0, 0.0, 0.0], abs=1e-6)
    assert lab[2] == pytest.approx([53.24, 80.09, 67.20], abs=0.05)
    assert lab[3] == pytest.approx([53.59, 0.0, 0.0], abs=0.02)


def test_wall_lab_delta_e_and_common_rungs():
    index, depth, normal = toy_passes()
    table = {2: {"wenart_id": "win_1", "kind": "window"}, 3: {"wenart_id": "f_1", "kind": "furniture"}}
    mask = RM.wall_mask(index, depth, normal, table)
    assert mask[15, 5] and not mask[15, 45] and not mask[5, 5] and not mask[35, 30]   # wall, not pane/ceiling/floor
    rgb = np.full((40, 64, 3), 200, np.uint8)
    lab = RM.wall_lab(rgb, mask)
    assert lab == pytest.approx(RM.srgb_to_lab(np.array([200, 200, 200], np.uint8)).round(2).tolist(), abs=0.01)
    assert RM.wall_lab(rgb, np.zeros((40, 64), bool)) is None
    assert RM.max_delta_e({"a": [50, 0, 0], "b": [53, 4, 0], "c": None}) == pytest.approx(5.0)
    assert RM.max_delta_e([[50, 0, 0]]) is None
    assert RM.labs_agree({"a": [50, 0, 0], "b": [54, 0, 0]}) and not RM.labs_agree({"a": [50, 0, 0], "b": [56, 0, 0]})
    assert RM.labs_agree({"a": [50, 0, 0], "b": None})
    assert RM.common_rungs({"a": {1, 2, 3}, "b": {2, 3}}, 3) == [2, 3]
    assert RM.common_rungs({"a": {1}, "b": {2}}, 3) == [] and RM.common_rungs({}, 3) == []


# --------------------------------------------------------------------------
# Ladder outcome and attempt keys (§3.6)
# --------------------------------------------------------------------------

def rec(k, decision=None, error=None):
    return {"k": k, "gate": {"decision": decision} if decision else None, "error": error}


def test_ladder_outcome():
    assert ladder_outcome([rec(1, "reject"), rec(2, "accept"), rec(3, "accept")], True) == ("polished", 2, None)
    assert ladder_outcome([rec(1, "reject"), rec(2, "reject")], True) == ("cycles", None, "gate")
    assert ladder_outcome([rec(1, "reject"), rec(2, error="boom")], True) == ("cycles", None, "error")
    assert ladder_outcome([rec(1, "reject")], False) == ("cycles", None, "deadline")
    assert ladder_outcome([], False) == ("cycles", None, "deadline")
    assert not accepted(rec(1, "accept", error="gate: x")) and not accepted(None) and accepted(rec(1, "accept"))


def test_attempt_key_changes_with_every_input():
    cfg = PC.load_config()
    models = PC.models_record(cfg, {"models": {}})
    attempt = PC.ladder(cfg)[0]
    base = dict(seed=1, steps=8, sigmas=[0.375, 0.25, 0.125], prompt="p", control_sha256="c" * 64,
                source_sha256="s" * 64, models=models, versions={"torch": "2.9.1", "diffusers": "0.40.0"})
    key = attempt_key(attempt, **base)
    assert len(key) == 64 and key == attempt_key(dict(attempt), **base)
    for change in ({"seed": 2}, {"prompt": "q"}, {"control_sha256": "d" * 64}, {"source_sha256": "t" * 64},
                   {"sigmas": [0.25, 0.125]}, {"versions": {"torch": "2.9.2", "diffusers": "0.40.0"}}):
        assert attempt_key(attempt, **{**base, **change}) != key, change
    for field, value in (("strength", 0.25), ("control", "canny"), ("scale", 0.7), ("size", "1536x864"),
                         ("mode", "anchor")):
        assert attempt_key({**attempt, field: value}, **base) != key, field
    other = json.loads(json.dumps(models))
    other["controlnet"]["revision"] = "x" * 40
    assert attempt_key(attempt, **{**base, "models": other}) != key


# --------------------------------------------------------------------------
# polish.yaml attempt lists
# --------------------------------------------------------------------------

def test_ladder_and_grids_parse_into_checked_attempts(tmp_path):
    cfg = PC.load_config()
    ladder = PC.ladder(cfg)
    assert [(a["role"], a["strength"], a["control"]) for a in ladder] == [
        ("ladder", 0.375, "geometry"), ("ladder", 0.25, "canny"), ("ladder", 0.125, "depth")]
    sweep = PC.grid(cfg, "sweep")
    assert len(sweep) == 11 and sweep[-1]["role"] == "presumed_bad" and sweep[-1]["control"] is None
    assert sweep[-1]["scale"] is None and {a["mode"] for a in sweep} == {"plain", "anchor"}
    assert len(PC.grid(cfg, "smoke")) == 4
    f = tmp_path / "g.yaml"
    f.write_text("attempts:\n  - {strength: 0.25, control: canny, scale: 0.9}\n", encoding="utf-8")
    g = PC.grid(cfg, str(f))
    assert g == [{"role": "grid", "strength": 0.25, "control": "canny", "scale": 0.9, "size": "native",
                  "mode": "plain"}]
    j = tmp_path / "g.json"
    j.write_text(json.dumps([{"strength": 0.5, "control": "depth", "scale": 0.8, "size": "1536x864"}]),
                 encoding="utf-8")
    assert PC.grid(cfg, str(j))[0]["size"] == "1536x864"
    with pytest.raises(ValueError):
        PC.grid(cfg, "nope")


@pytest.mark.parametrize("bad", [
    {"strength": 0.0, "control": "depth", "scale": 0.8},
    {"strength": 1.2, "control": "depth", "scale": 0.8},
    {"strength": 0.3, "control": "hed", "scale": 0.8},
    {"strength": 0.3, "control": "depth", "scale": None},
    {"strength": 0.3, "control": None, "scale": None},                     # only presumed_bad may skip control
    {"strength": 0.3, "control": "depth", "scale": 0.8, "mode": "tile"},
    {"strength": 0.3, "control": "depth", "scale": 0.8, "size": "100x100"},
    {"role": "presumed_bad", "strength": 0.75, "control": None, "mode": "anchor"},
    {"role": "best", "strength": 0.3, "control": "depth", "scale": 0.8},
])
def test_bad_attempts_are_rejected(bad):
    with pytest.raises(ValueError):
        PC.check_attempt(bad, "grid")


def test_models_record_lists_repos_revisions_licences_files():
    cfg = PC.load_config()
    from wenart.gate.api import load_models_config
    rec = PC.models_record(cfg, load_models_config())
    assert rec["base"]["repo"] == "Tongyi-MAI/Z-Image-Turbo" and rec["base"]["licence"] == "Apache-2.0"
    assert rec["controlnet"]["files"] == ["Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors"]
    assert rec["controlnet"]["config_sha256"] == "f7225591bd7534c4ef9b9844c93a4d843813d55cd1f542b571af835cc70acba9"
    assert set(rec["gate"]) == {"depth", "sam", "dino"} and all(m["revision"] for m in rec["gate"].values())


# --------------------------------------------------------------------------
# Backend helpers without torch
# --------------------------------------------------------------------------

def test_zimage_module_imports_without_torch_and_sets_the_alloc_conf(monkeypatch):
    code = ("import sys, wenart.polish.zimage, wenart.polish.runner, wenart.polish.__main__; "
            "print(','.join(m for m in ('torch', 'diffusers', 'transformers') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""
    monkeypatch.delenv("PYTORCH_CUDA_ALLOC_CONF", raising=False)
    ZI.ZImageBackend(PC.load_config(), device="cuda")
    import os
    assert os.environ["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
    monkeypatch.setenv("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:64")
    ZI.ZImageBackend(PC.load_config())
    assert os.environ["PYTORCH_CUDA_ALLOC_CONF"] == "max_split_size_mb:64"   # the job's setting wins
    out = ZI.to_uint8(np.array([[[0.0, 0.5, 1.0]], [[0.0019, 0.998, 1.2]]]))
    assert out.tolist() == [[[0, 128, 255]], [[0, 254, 255]]]


# --------------------------------------------------------------------------
# Schema and previews
# --------------------------------------------------------------------------

def test_schema_rejects_bad_manifests():
    errors = validate_manifest({"schema_version": "0.1", "kind": "final"})
    assert any("kind" in e for e in errors) and any("views" in e for e in errors)
    assert validate_determinism({"camera": "c", "max_abs_diff": 0, "seconds": 1.0}) == []
    assert validate_determinism({"camera": "c", "max_abs_diff": -1, "seconds": 1.0})
    # Review G1: the CPU-offload fallback is gone, so a manifest never records memory_mode "offload".
    base = {"schema_version": "0.1", "kind": "run"}
    assert any(e.startswith("memory_mode:") for e in validate_manifest(dict(base, memory_mode="offload")))
    for mode in ("resident", None):
        assert not [e for e in validate_manifest(dict(base, memory_mode=mode)) if e.startswith("memory_mode:")]


def test_write_preview_stays_under_the_byte_limit(tmp_path):
    rng = np.random.default_rng(3)
    noise = rng.integers(0, 256, size=(600, 900, 3), dtype=np.uint8)
    path = write_preview(noise, tmp_path / "p.jpg", max_bytes=60_000)
    assert path.stat().st_size <= 60_000
    small = write_preview(noise, tmp_path / "s.jpg", width=300)
    from PIL import Image
    with Image.open(small) as img:
        assert img.size == (300, 200)
