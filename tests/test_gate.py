"""CPU tests for the change gate (docs/milestone5.md §4, §9 "gate").

A synthetic room (back wall, side wall, floor, ceiling, a window, a door, a
sofa and a chair in front of it) is written as a render folder with the M5
helper passes; fake models with the documented interface (``depth``,
``sam_masks``, ``dino_tokens``) stand in for DAv2 / SAM 2.1 / DINOv2. The
tests cover: regions and validity masks, edge recall (a 25 px shift fails,
texture noise passes), added lines (a painted frame fails), the depth fit
and error, Lab / ΔE76 / chroma on known colours, IoU and SAM reliability,
patch features, ``decide`` op semantics, the gate key and caching, failing
closed when a model fails, every benign and negative control generator
(deterministic, changes only what it should), the calibration proposal
rule, the model wrapper against fake torch/transformers modules, the debug
image size, and the calibration end to end on a tiny project.
"""
import contextlib
import json
import math
import subprocess
import sys
import time
import types
from pathlib import Path

import cv2
import numpy as np
import pytest

from wenart import views as V
from wenart.gate import api, calibrate, colour, controls as K, depth, edges, features, lines, masks
from wenart.gate import models as gate_models
from wenart.gate.__main__ import main as gate_main

ROOT = Path(__file__).resolve().parents[1]
SOFA, CHAIR, WINDOW, DOOR = 12, 14, 6, 1


# --------------------------------------------------------------------------
# Synthetic room
# --------------------------------------------------------------------------

def build_room(W=640, H=360, sofa=True, chair=True, seed=0):
    """RGB + uint16 index + uint16 depth_mm + uint8 normal of a small furnished room."""
    rng = np.random.default_rng(seed)
    index = np.zeros((H, W), np.uint16)
    depth_m = np.zeros((H, W), np.float64)
    normal = np.zeros((H, W, 3), np.float64)
    rgb = np.zeros((H, W, 3), np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    ceil_y, floor_y, side_x = int(0.18 * H), int(0.62 * H), int(0.12 * W)
    back = (yy >= ceil_y) & (yy < floor_y) & (xx >= side_x)
    depth_m[back], normal[back], rgb[back] = 5.0, [0, -1, 0], [200, 198, 190]
    ceil = yy < ceil_y
    depth_m[ceil], normal[ceil], rgb[ceil] = 4.0 + yy[ceil] / ceil_y, [0, 0, -1], [228, 228, 224]
    flo = yy >= floor_y
    depth_m[flo] = 5.0 - 3.5 * (yy[flo] - floor_y) / (H - floor_y)
    normal[flo], rgb[flo] = [0, 0, 1], [150, 112, 74]
    side = (xx < side_x) & ~flo & ~ceil
    depth_m[side], normal[side], rgb[side] = 2.0 + 3.0 * xx[side] / side_x, [1, 0, 0], [185, 183, 176]
    # Window: frame + pane share one index.
    wx0, wx1, wy0, wy1 = int(0.62 * W), int(0.84 * W), int(0.24 * H), int(0.52 * H)
    win = (xx >= wx0) & (xx < wx1) & (yy >= wy0) & (yy < wy1)
    index[win], depth_m[win], normal[win], rgb[win] = WINDOW, 5.05, [0, -1, 0], [250, 250, 250]
    f = max(4, W // 120)
    pane = (xx >= wx0 + f) & (xx < wx1 - f) & (yy >= wy0 + f) & (yy < wy1 - f)
    rgb[pane] = [140, 178, 226]
    dx0, dx1, dy0 = int(0.18 * W), int(0.28 * W), int(0.26 * H)
    door = (xx >= dx0) & (xx < dx1) & (yy >= dy0) & (yy < floor_y)
    index[door], depth_m[door], normal[door], rgb[door] = DOOR, 4.98, [0, -1, 0], [158, 120, 82]
    sx0, sx1, sy0, sy1 = int(0.34 * W), int(0.58 * W), int(0.50 * H), int(0.80 * H)
    if sofa:
        s = (xx >= sx0) & (xx < sx1) & (yy >= sy0) & (yy < sy1)
        top = s & (yy < sy0 + (sy1 - sy0) // 4)
        index[s], depth_m[s], normal[s], rgb[s] = SOFA, 3.2, [0, -1, 0], [72, 82, 112]
        normal[top], rgb[top] = [0, 0, 1], [92, 102, 132]
    if chair:
        cx0, cx1, cy0, cy1 = sx1 - int(0.06 * W), sx1 + int(0.05 * W), int(0.66 * H), int(0.90 * H)
        c = (xx >= cx0) & (xx < cx1) & (yy >= cy0) & (yy < cy1)
        index[c], depth_m[c], normal[c], rgb[c] = CHAIR, 2.4, [0, -1, 0], [128, 60, 48]
    rgb *= (0.92 + 0.08 * (1 - yy / H))[:, :, None]
    rgb += cv2.GaussianBlur(rng.normal(0, 1.5, (H, W)).astype(np.float32), (0, 0), 1.0)[:, :, None]
    return {"rgb": np.clip(np.rint(rgb), 0, 255).astype(np.uint8), "index": index,
            "depth_mm": V.encode_depth_mm(depth_m), "normal": V.encode_normal(normal, np.abs(normal).sum(axis=2) > 0),
            "boxes": {"wall": [side_x, ceil_y, W, floor_y], "window": [wx0, wy0, wx1, wy1]}}


def scene_manifest(wall_mode="flat"):
    def furn(wid, idx, ftype, room="r_1"):
        return {"name": f"furn_{wid}", "wenart_id": wid, "kind": "furniture", "type": ftype, "room_id": room,
                "source": "from_documents", "status": "verified", "pass_index": idx, "level_id": "L0",
                "center": [0, 0, 0.4], "size": [1, 1, 0.8], "rotation_deg": 0}
    return {
        "schema_version": "0.1", "project": "toy", "building": "/nowhere/building_final.json",
        "style_profile": {"walls": {"material": "plaster_white"}, "wet_walls": {"material": "tiles_light"},
                          "ceiling": {"material": "plaster_white"}, "floor": {"material": "wood_oak_light"}},
        "materials": {"plaster_white__x": {"slug": "plaster_white", "albedo_mode": wall_mode},
                      "plaster_white": {"slug": "plaster_white", "albedo_mode": wall_mode},
                      "tiles_light": {"slug": "tiles_light", "albedo_mode": "texture"}},
        "objects": [
            {"name": "d_1_frame", "wenart_id": "d_1", "kind": "door", "pass_index": DOOR, "level_id": "L0",
             "room_ids": ["r_1"]},
            {"name": "win_1_frame", "wenart_id": "win_1", "kind": "window", "pass_index": WINDOW, "level_id": "L0",
             "room_ids": ["r_1"]},
            {"name": "win_1_glass", "wenart_id": "win_1", "kind": "window", "pass_index": WINDOW, "level_id": "L0"},
            furn("f_1", SOFA, "sofa"), furn("f_2", CHAIR, "armchair"),
            {"name": "r_1_floor", "wenart_id": "r_1", "element_id": "r_1", "kind": "floor", "wet": False,
             "material": "wood_oak_light"},
            {"name": "r_1_ceiling", "wenart_id": "r_1", "element_id": "r_1", "kind": "ceiling", "wet": False,
             "material": "plaster_white"},
            {"name": "r_2_ceiling", "wenart_id": "r_2", "element_id": "r_2", "kind": "ceiling", "wet": True,
             "material": "plaster_white"},
        ],
        "cameras": [{"name": "cam_a", "room_id": "r_1", "level_id": "L0"},
                    {"name": "cam_b", "room_id": "r_2", "level_id": "L0"}],
    }


def write_view(folder: Path, camera: str, data: dict, room_id="r_1", **extra) -> dict:
    """Write one camera's PNGs into ``folder`` and return its render-manifest entry."""
    H, W = data["index"].shape
    V.write_png_rgb(folder / f"{camera}.png", data["rgb"])
    V.write_png16(folder / f"{camera}_index.png", data["index"])
    V.write_png16(folder / f"{camera}_depth_mm.png", data["depth_mm"])
    V.write_png_rgb(folder / f"{camera}_normal.png", data["normal"])
    entry = {"camera": camera, "png": f"{camera}.png", "index_png": f"{camera}_index.png", "room_id": room_id,
             "level_id": "L0", "resolution": [W, H], "render_key": "0123456789abcdef",
             "index_stats": {str(k): v for k, v in V.compute_index_stats(data["index"]).items()},
             "files": {"depth_mm": f"{camera}_depth_mm.png", "normal": f"{camera}_normal.png"}}
    entry.update(extra)
    return entry


def write_project(out: Path, cams=(("cam_a", "r_1"),), W=640, H=360, wall_mode="flat") -> dict:
    renders = out / "renders"
    renders.mkdir(parents=True)
    data = build_room(W, H)
    entries = [write_view(renders, cam, data, room) for cam, room in cams]
    (renders / "render_manifest.json").write_text(json.dumps({"schema_version": "0.1", "renders": entries}),
                                                  encoding="utf-8")
    (out / "scene").mkdir()
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene_manifest(wall_mode)), encoding="utf-8")
    return data


class FakeModels:
    """Image-driven stand-ins for DAv2 / SAM 2.1 / DINOv2 with the ``models.Models`` interface."""

    def __init__(self, fail=None):
        self.calls = {"depth": 0, "sam": 0, "dino": 0, "settle": 0}
        self.fail = fail or set()

    def info(self):
        return {k: {"repo": f"fake/{k}", "revision": "0", "licence": "test"} for k in ("depth", "sam", "dino")}

    def settle(self):
        self.calls["settle"] += 1
        return True

    def depth(self, rgb):
        self.calls["depth"] += 1
        if "depth" in self.fail:
            raise RuntimeError("depth model failed")
        g = cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2GRAY).astype(np.float32)
        return cv2.GaussianBlur(g, (0, 0), 3.0) / 255.0

    def sam_masks(self, rgb, boxes):
        self.calls["sam"] += 1
        if "sam" in self.fail:
            raise RuntimeError("sam model failed")
        a = np.asarray(rgb, np.float32)
        out = np.zeros((len(boxes), a.shape[0], a.shape[1]), bool)
        for k, (x0, y0, x1, y1) in enumerate(boxes):
            x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
            cx0, cx1, cy0, cy1 = x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4, y0 + (y1 - y0) // 4, y1 - (y1 - y0) // 4
            med = np.median(a[cy0:cy1, cx0:cx1].reshape(-1, 3), axis=0)
            out[k, y0:y1, x0:x1] = np.linalg.norm(a[y0:y1, x0:x1] - med, axis=2) < 40
        return out

    def dino_tokens(self, rgb):
        self.calls["dino"] += 1
        a = np.asarray(rgb, np.float32)
        gh, gw = a.shape[0] // 14, a.shape[1] // 14
        a = a[:gh * 14, :gw * 14].reshape(gh, 14, gw, 14, 3)
        return np.concatenate([a.mean(axis=(1, 3)) - 128.0, a.std(axis=(1, 3))], axis=-1)


def texture(img, sigma, seed=1):
    n = cv2.GaussianBlur(np.random.default_rng(seed).normal(0, sigma, img.shape[:2]).astype(np.float32), (0, 0), 1.2)
    return np.clip(img + n[:, :, None], 0, 255).astype(np.uint8)


@pytest.fixture(scope="module")
def room(tmp_path_factory):
    """A written one-camera project, its view, a gate with fake models and the prepared reference."""
    out = tmp_path_factory.mktemp("gate") / "toy"
    data = write_project(out, W=960, H=540)
    view = V.load_views(out / "renders")["cam_a"]
    gate = api.Gate(models=FakeModels(), device="cpu")
    ref = gate.prepare(view, data["rgb"])
    return {"out": out, "data": data, "view": view, "gate": gate, "ref": ref}


# --------------------------------------------------------------------------
# Imports, regions, reference
# --------------------------------------------------------------------------

def test_gate_package_imports_without_torch_opencv_or_pillow():
    code = ("import sys, wenart.gate, wenart.gate.api; "
            "print(','.join(m for m in ('torch', 'transformers', 'cv2', 'PIL') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""
    code = "import sys, wenart.gate.models; print('torch' in sys.modules, 'transformers' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False False"


def test_prepare_builds_regions_valid_mask_and_reference_edges(room):
    ref, data = room["ref"], room["data"]
    regs = ref.regions
    assert set(regs.object_ids()) == {"d_1", "win_1", "f_1", "f_2"}
    assert {"struct:floor", "struct:walls", "struct:ceiling"} <= set(regs.structure_ids())
    assert regs.kinds["win_1"] == "window" and regs.kinds["f_1"] == "furniture"
    # Panes (window mask eroded 6 px) and background are not valid; reference edges never lie there.
    assert not (ref.valid & regs.panes).any() and regs.panes.sum() > 0
    assert not (ref.edges & ~ref.valid).any()
    assert ref.edges.sum() > 500 and (ref.edges <= ref.geometry).all()
    # Lab means and valid pixel counts per region; the walls of the toy room are plaster, flat.
    assert set(ref.lab_means) == set(regs.masks)
    assert ref.valid_pixels["win_1"] < regs.pixels["win_1"]            # pane pixels removed
    assert ref.albedo["struct:walls"]["albedo_mode"] == "flat"
    assert ref.albedo["struct:walls"]["slot"] == "style_profile.walls"
    assert ref.sha256 == api.image_sha256(data["rgb"]) and len(ref.gate_key) == 16
    assert ref.size == (960, 540) and ref.model_outputs == {}            # model outputs come on first use


def test_prepare_caches_and_compare_checks_the_size(room):
    gate, view, data, ref = room["gate"], room["view"], room["data"], room["ref"]
    assert gate.prepare(view, data["rgb"]) is ref
    with pytest.raises(ValueError):
        gate.prepare(view, data["rgb"][:-2])
    with pytest.raises(ValueError):
        gate.compare(ref, data["rgb"][:, :-4])
    with pytest.raises(ValueError):
        gate.compare(ref, data["rgb"].astype(np.float32))


# --------------------------------------------------------------------------
# Edges, lines
# --------------------------------------------------------------------------

def test_canny_and_distance_to():
    img = np.zeros((40, 60, 3), np.uint8)
    img[:, 30:] = 200
    e = edges.canny(img)
    assert e.any() and np.abs(np.nonzero(e)[1] - 29.5).max() <= 2
    d = edges.distance_to(e)
    assert d[20, 29:31].min() == 0 and d[20, 0] >= 25
    assert np.isinf(edges.distance_to(np.zeros((5, 5), bool))).all()
    m = np.zeros((7, 7), bool)
    m[3, 3] = True
    assert edges.distance_to(m)[3, 6] == pytest.approx(3.0) and edges.distance_to(m)[0, 0] == pytest.approx(math.sqrt(18))
    val, n = edges.recall(m, edges.distance_to(m), 0.5)
    assert (val, n) == (1.0, 1)
    assert edges.recall(np.zeros((7, 7), bool), edges.distance_to(m), 3) == (None, 0)


def test_texture_noise_passes_and_a_25px_shift_fails_the_edges(room):
    gate, ref, data = room["gate"], room["ref"], room["data"]
    noisy = gate.compare(ref, texture(data["rgb"], 12))
    assert noisy["decision"] == "accept", noisy["reasons"]
    assert noisy["metrics"]["edges"]["global"] >= 0.99
    assert all(v >= 0.99 for v in noisy["metrics"]["edges"]["regions"].values())
    assert noisy["metrics"]["added_lines"]["global"] == 0.0
    shifted = texture(K.shift_object(data["rgb"], data["index"], data["depth_mm"], SOFA, 25), 12)
    res = gate.compare(ref, shifted)
    assert res["decision"] == "reject"
    em = res["metrics"]["edges"]
    assert em["regions"]["f_1"] < 0.85 and em["global"] < 0.95
    assert em["regions"]["d_1"] >= 0.99 and em["regions"]["win_1"] >= 0.99      # the other objects stay
    failed = {(r["check"], r["region"]) for r in res["reasons"]}
    assert ("edges", "f_1") in failed and ("edges", "global") in failed
    reason = next(r for r in res["reasons"] if r["check"] == "edges" and r["region"] == "f_1")
    assert reason["op"] == ">=" and reason["threshold"] == 0.85


def test_edge_metrics_skip_objects_without_reference_pixels():
    regs = types.SimpleNamespace(masks={"a": np.zeros((20, 20), bool), "b": np.zeros((20, 20), bool)})
    regs.masks["a"][2:10, 2:10] = True
    regs.masks["b"][15:17, 15:17] = True
    ref = np.zeros((20, 20), bool)
    ref[2, 2:10] = True
    out, missed = edges.edge_metrics(ref, edges.distance_to(ref), regs, ["a", "b"], 3, min_ref_px=5)
    assert out["regions"] == {"a": 1.0} and out["skipped"] == {"b": "no_reference_px"}
    assert out["global"] == 1.0 and not missed.any() and out["ref_px"]["a"] == 8


def test_added_lines_find_a_painted_frame_on_a_bare_wall(room):
    gate, ref, data = room["gate"], room["ref"], room["data"]
    framed = data["rgb"].copy()
    x0, y0, x1, y1 = data["boxes"]["wall"]
    cv2.rectangle(framed, (x0 + 200, y0 + 30), (x0 + 360, y0 + 130), (120, 100, 80), 3)
    res = gate.compare(ref, framed)
    value = res["metrics"]["added_lines"]["regions"]["struct:walls"]
    assert value > 0.04 * 4                                   # four sides, both Canny sides of each stroke
    assert res["decision"] == "reject"
    assert [r for r in res["reasons"] if r["check"] != "added_lines"] == []
    reason = res["reasons"][0]
    assert (reason["region"], reason["op"], reason["threshold"]) == ("struct:walls", "<=", 0.04)
    assert res["metrics"]["edges"]["global"] == 1.0            # recall alone would not see it
    assert len(gate.last_artifacts["lines"]) >= 4


def test_added_lines_ignore_lines_along_real_geometry():
    """A seam the Cycles image hides (same colour both sides) is still a geometry edge, not an addition."""
    H, W = 120, 200
    test = np.full((H, W, 3), 180, np.uint8)
    cv2.line(test, (10, 60), (190, 60), (60, 60, 60), 2)
    test_edges = edges.canny(test)
    geometry = np.zeros((H, W), bool)
    geometry[60, :] = True
    masks_ = {"struct:walls": np.ones((H, W), bool)}
    no_geo, found = lines.added_lines(test_edges, edges.distance_to(np.zeros((H, W), bool)), masks_,
                                      ["struct:walls"], W, 0.04, 0.7)
    assert no_geo["regions"]["struct:walls"] > 0.5 and found
    with_geo, found = lines.added_lines(test_edges, edges.distance_to(geometry), masks_, ["struct:walls"], W, 0.04, 0.7)
    assert with_geo["regions"]["struct:walls"] == 0.0 and found == []
    # A region fully excluded (window panes) is skipped.
    out, _ = lines.added_lines(test_edges, edges.distance_to(geometry), masks_, ["struct:walls"], W, 0.04, 0.7,
                               exclude=np.ones((H, W), bool))
    assert out["skipped"] == {"struct:walls": "too_small"}


def test_segment_helpers():
    xs, ys = lines.segment_pixels([0, 0, 10, 5])
    assert len(xs) == 11 and (xs[0], ys[0], xs[-1], ys[-1]) == (0, 0, 10, 5)
    dist = np.zeros((10, 20), np.float32)
    dist[:, 10:] = 9.0
    assert lines.unmatched_share([0, 5, 19, 5], dist) == pytest.approx(0.5)
    e = np.zeros((50, 100), bool)
    e[20, 5:95] = True
    e[30, 5:20] = True                                       # too short
    segs = lines.segments(e, 40)
    assert segs.shape == (1, 4) and abs(segs[0, 2] - segs[0, 0]) >= 80
    assert lines.segments(np.zeros((10, 10), bool), 4).shape == (0, 4)


# --------------------------------------------------------------------------
# Depth
# --------------------------------------------------------------------------

def test_depth_fit_recovers_scale_and_shift_despite_outliers():
    rng = np.random.default_rng(0)
    ref = rng.uniform(0.1, 1.0, (60, 80))
    pred = (ref - 0.2) / 3.0
    s, t = depth.fit_scale_shift(pred, ref)
    assert s == pytest.approx(3.0, abs=1e-9) and t == pytest.approx(0.2, abs=1e-9)
    bad = pred.copy()
    bad[:, :4] += 0.15                                       # 5 % of the pixels changed (values stay in range)
    s, t = depth.fit_scale_shift(bad, ref)
    assert s == pytest.approx(3.0, abs=1e-6) and t == pytest.approx(0.2, abs=1e-6)
    mask = np.ones(ref.shape, bool)
    mask[:30] = False
    assert depth.fit_scale_shift(bad, ref, mask)[0] == pytest.approx(3.0, abs=1e-6)
    with pytest.raises(ValueError):
        depth.fit_scale_shift(pred, ref, np.zeros(ref.shape, bool))
    assert depth.fit_scale_shift(np.ones((4, 4)), np.full((4, 4), 2.0)) == (0.0, 2.0)


def test_depth_error_is_zero_after_the_fit_and_flags_a_changed_region():
    H, W = 60, 80
    ref = np.tile(np.linspace(0.2, 1.0, W), (H, 1))
    obj = np.zeros((H, W), bool)
    obj[20:40, 30:50] = True
    valid = np.ones((H, W), bool)
    valid[:, :2] = False
    test = 2.0 * ref + 0.5
    err, info = depth.error_map(ref, test, valid)
    assert np.isnan(err[:, :2]).all() and np.nanmax(err) < 1e-6
    assert info["scale"] == pytest.approx(0.5) and info["shift"] == pytest.approx(-0.25)
    test2 = test.copy()
    test2[obj] += 0.8
    m, err = depth.depth_metrics(ref, test2, valid, {"obj": obj, "rest": ~obj, "tiny": np.eye(H, W, dtype=bool)},
                                 ["obj", "rest", "tiny"], 0.02)       # tiny: 58 valid px = 1.2 % < 2 %
    rng_ = np.percentile(ref[valid], 98) - np.percentile(ref[valid], 2)
    assert m["regions"]["obj"] == pytest.approx(0.4 / rng_, rel=1e-3)
    assert m["regions"]["rest"] < 1e-6 and m["skipped"] == {"tiny": "too_small"}
    assert m["global"] == pytest.approx(m["regions"]["obj"] * obj[valid].mean(), rel=1e-3)


# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------

def test_lab_of_known_colours_delta_e_and_chroma():
    lab = colour.srgb_to_lab(np.array([[255, 255, 255], [0, 0, 0], [255, 0, 0], [128, 128, 128]], np.uint8))
    assert lab[0] == pytest.approx([100.0, 0.0, 0.0], abs=0.02)
    assert lab[1] == pytest.approx([0.0, 0.0, 0.0], abs=1e-4)
    assert lab[2] == pytest.approx([53.24, 80.09, 67.20], abs=0.05)
    assert lab[3] == pytest.approx([53.59, 0.0, 0.0], abs=0.02)
    assert colour.delta_e76(lab[0], lab[2]) == pytest.approx(math.sqrt(46.76 ** 2 + 80.09 ** 2 + 67.20 ** 2), abs=0.1)
    assert colour.chroma(lab[2]) == pytest.approx(104.55, abs=0.05)
    assert colour.chroma(lab[3]) == pytest.approx(0.0, abs=0.01)
    # Lab -> sRGB inverts the forward conversion on a grid of colours.
    levels = np.arange(0, 256, 17, dtype=np.uint8)
    grid = np.stack(np.meshgrid(levels, levels, levels, indexing="ij"), axis=-1).reshape(-1, 3)
    back = colour.lab_to_srgb(colour.srgb_to_lab(grid))
    assert np.abs(back.astype(int) - grid.astype(int)).max() <= 1
    # Linear-light helpers.
    assert colour.to_uint8(colour.to_linear(grid)).tolist() == grid.tolist()


def test_colour_and_neutral_metrics_on_a_tinted_wall():
    H, W = 40, 60
    rgb = np.full((H, W, 3), 128, np.uint8)
    wall = np.zeros((H, W), bool)
    wall[:20] = True
    floor_ = ~wall
    rgb[floor_] = [150, 110, 70]
    valid = np.ones((H, W), bool)
    masks_ = {"struct:walls": wall, "struct:floor": floor_}
    ref_lab = colour.srgb_to_lab(rgb)
    ref_means = colour.region_means(ref_lab, masks_, list(masks_), valid)
    tinted = K.lab_edit(rgb, wall, d_b=10.0)
    test_lab = colour.srgb_to_lab(tinted)
    m, test_means = colour.colour_metrics(ref_lab, test_lab, ref_means, masks_, list(masks_), valid, 0.01)
    assert m["regions"]["struct:walls"] == pytest.approx(10.0, abs=0.6)
    assert m["regions"]["struct:floor"] == 0.0
    assert m["global"] == pytest.approx(m["regions"]["struct:walls"] / 2, abs=0.4)
    albedo = {"struct:walls": {"albedo_mode": "flat"}, "struct:ceiling": {"albedo_mode": "texture"}}
    pixels = {"struct:walls": int(wall.sum()), "struct:floor": int(floor_.sum()), "struct:ceiling": 5}
    n = colour.neutral_metrics(ref_means, test_means, pixels, H * W, albedo, 0.01)
    assert n["regions"]["struct:walls"] == pytest.approx(10.0, abs=0.6)
    assert n["skipped"] == {"struct:ceiling": "albedo_texture"} and "struct:floor" not in n["regions"]
    n2 = colour.neutral_metrics(ref_means, test_means, pixels, H * W, {}, 0.01)
    assert n2["regions"] == {} and n2["skipped"]["struct:walls"] == "albedo_unknown"
    # Labels give the same means as a mask-by-mask mean.
    assert ref_means["struct:floor"] == pytest.approx(ref_lab[floor_].mean(axis=0).tolist(), abs=1e-3)


def test_structure_albedo_follows_the_room_and_the_records():
    scene = scene_manifest("flat")
    dry = colour.structure_albedo(scene, "r_1")
    assert dry["struct:walls"] == {"material": "plaster_white", "albedo_mode": "flat",
                                   "source": "scene manifest materials.plaster_white__x", "slot": "style_profile.walls",
                                   "wet": False}
    assert dry["struct:ceiling"]["material"] == "plaster_white" and dry["struct:ceiling"]["slot"] == "ceiling object"
    wet = colour.structure_albedo(scene, "r_2")                 # wet room: tiles on the walls
    assert wet["struct:walls"]["material"] == "tiles_light" and wet["struct:walls"]["albedo_mode"] == "texture"
    assert wet["struct:walls"]["slot"] == "style_profile.wet_walls"
    scene["style_profile"]["walls"]["material"] = "mystery_paint"   # not in the records or the vocabulary
    assert colour.structure_albedo(scene, "r_1")["struct:walls"]["albedo_mode"] is None
    assert colour.structure_albedo({}, None)["struct:walls"]["albedo_mode"] is None


def test_neutral_check_rejects_a_tinted_flat_wall_and_skips_textured_walls(tmp_path):
    for mode, expect in (("flat", "reject"), ("texture", "accept")):
        out = tmp_path / mode
        data = write_project(out, wall_mode=mode)
        gate = api.Gate(models=FakeModels(), device="cpu")
        ref = gate.prepare(V.load_views(out / "renders")["cam_a"], data["rgb"])
        x0, y0, x1, y1 = data["boxes"]["wall"]
        test = data["rgb"].copy()
        test[ref.regions.masks["struct:walls"]] = K.lab_edit(data["rgb"], ref.regions.masks["struct:walls"],
                                                             d_a=4.0, d_b=7.0)[ref.regions.masks["struct:walls"]]
        res = gate.compare(ref, test)
        assert res["decision"] == expect, (mode, res["reasons"])
        neutral = res["metrics"]["neutral"]
        if mode == "flat":
            assert neutral["regions"]["struct:walls"] > 5.0
            assert {r["check"] for r in res["reasons"]} == {"neutral"}
        else:
            assert neutral["skipped"]["struct:walls"] == "albedo_texture"


# --------------------------------------------------------------------------
# Masks, features
# --------------------------------------------------------------------------

def test_iou_boxes_and_mask_metrics():
    a = np.zeros((10, 10), bool)
    a[2:6, 2:6] = True
    b = np.zeros((10, 10), bool)
    b[4:8, 2:6] = True
    assert masks.iou(a, b) == pytest.approx(8 / 24)
    assert masks.iou(a, a) == 1.0 and masks.iou(np.zeros((3, 3)), np.zeros((3, 3))) is None
    assert masks.mask_box(a) == [2, 2, 6, 6] and masks.mask_box(np.zeros((3, 3))) is None
    boxes, skipped = masks.sam_objects({"a": a, "tiny": np.eye(10, dtype=bool) & False}, ["a", "tiny"], 100, 0.05)
    assert boxes == {"a": [2, 2, 6, 6]} and skipped == {"tiny": "too_small"}
    index_masks = {"a": a, "thin": b}
    ref_sam = {"a": a, "thin": np.zeros((10, 10), bool)}       # SAM misses the thin object on the reference
    rel = masks.reliability(ref_sam, index_masks)
    assert rel == {"a": 1.0, "thin": 0.0}
    m = masks.mask_metrics(ref_sam, {"a": b, "thin": b}, rel, {"tiny": "too_small"}, 0.7)
    assert m["regions"] == {"a": pytest.approx(0.3333, abs=1e-4)}
    assert m["skipped"] == {"tiny": "too_small", "thin": "sam_unreliable"} and m["global"] is None


def test_feature_cosine_and_patch_shares():
    rng = np.random.default_rng(0)
    tok = rng.normal(size=(4, 6, 8))
    assert np.allclose(features.cosine_map(tok, tok), 1.0, atol=1e-6)
    assert np.allclose(features.cosine_map(tok, -tok), -1.0, atol=1e-6)
    with pytest.raises(ValueError):
        features.cosine_map(tok, tok[:, :5])
    mask = np.zeros((56, 84), bool)
    mask[:28, :42] = True                                      # the top-left 2 x 3 patches of a 4 x 6 grid
    shares = features.patch_shares(mask, (4, 6))
    assert shares[:2, :3].min() == 1.0 and shares[2:, :].max() == 0.0
    test = tok.copy()
    test[:2, :3] = rng.normal(size=(2, 3, 8))
    m, cos = features.feature_metrics(tok, test, {"obj": mask, "other": ~mask}, ["obj", "other"], mask.size, 0.01)
    assert m["regions"]["other"] == pytest.approx(1.0, abs=1e-4) and m["regions"]["obj"] < 0.8
    assert cos.shape == (4, 6)


# --------------------------------------------------------------------------
# decide, gate key, model failures
# --------------------------------------------------------------------------

THRESHOLDS = {
    "edges": {"hard": True, "global_min": 0.95, "region_min": 0.85, "region_min_ref_px": 200, "radius_px": 3},
    "added_lines": {"hard": True, "region_max_len_frac": 0.04, "min_len_frac": 0.04},
    "masks": {"hard": True, "region_min": 0.9},
    "features": {"hard": False, "region_min": 0.8},
    "calibration": {"source": None},
}


def test_decide_follows_the_op_semantics():
    metrics = {
        "edges": {"global": 0.95, "regions": {"a": 0.85, "b": 0.8499}, "skipped": {}},
        "added_lines": {"global": 0.1, "regions": {"struct:walls": 0.04, "struct:floor": 0.0401}, "skipped": {}},
        "masks": {"global": None, "regions": {"a": None, "b": 0.95}, "skipped": {}},
        "features": {"global": 0.5, "regions": {"a": 0.79}, "skipped": {}},
    }
    decision, reasons, notes = api.decide(metrics, THRESHOLDS)
    assert decision == "reject"
    assert reasons == [
        {"check": "edges", "region": "b", "value": 0.8499, "threshold": 0.85, "op": ">="},
        {"check": "added_lines", "region": "struct:floor", "value": 0.0401, "threshold": 0.04, "op": "<="},
    ]
    assert notes == [{"check": "features", "region": "a", "value": 0.79, "threshold": 0.8, "op": ">="}]
    # Equal values pass, a soft failure alone accepts, None values pass, unknown metrics are ignored.
    metrics["edges"]["regions"]["b"] = 0.85
    metrics["added_lines"]["regions"]["struct:floor"] = 0.04
    metrics["colour"] = {"global": 99.0, "regions": {}}
    assert api.decide(metrics, THRESHOLDS)[:2] == ("accept", [])
    # A hard check with limits but no metrics (or an error) fails closed.
    del metrics["masks"]
    decision, reasons, _ = api.decide(metrics, THRESHOLDS)
    assert decision == "reject" and reasons == [{"check": "masks", "region": "global", "value": None,
                                                 "threshold": 0.9, "op": ">=", "error": "not computed"}]
    metrics["masks"] = {"global": None, "regions": {}, "skipped": {}, "error": "RuntimeError: boom"}
    assert api.decide(metrics, THRESHOLDS)[1][0]["error"] == "RuntimeError: boom"
    # hard: false turns the same failure into a note; a check without limits is not checked.
    soft = json.loads(json.dumps(THRESHOLDS))
    soft["masks"]["hard"] = False
    soft["neutral"] = {"hard": True}
    decision, reasons, notes = api.decide(metrics, soft)
    assert decision == "accept" and reasons == [] and [n["check"] for n in notes] == ["masks", "features"]
    # The package thresholds give every §4.2 check its limits.
    package = api.load_thresholds()
    assert {c for c in package if api.limits_of(c, package.get(c) or {})} == set(api.CHECKS)


def test_gate_key_depends_on_models_reference_and_metric_parameters_not_limits():
    th = api.load_thresholds()
    info = {"depth": {"repo": "r", "revision": "1"}}
    key = api.make_gate_key("abc", info, th)
    assert key == api.make_gate_key("abc", info, json.loads(json.dumps(th)))
    looser = json.loads(json.dumps(th))
    looser["edges"]["global_min"] = 0.5
    looser["depth"]["region_max"] = 0.5
    looser["features"]["hard"] = True
    assert api.make_gate_key("abc", info, looser) == key          # decide re-applies limits
    wider = json.loads(json.dumps(th))
    wider["edges"]["radius_px"] = 5
    assert api.make_gate_key("abc", info, wider) != key
    assert api.make_gate_key("abd", info, th) != key
    assert api.make_gate_key("abc", {"depth": {"repo": "r", "revision": "2"}}, th) != key
    assert "radius_px" in api.compute_params(th)["edges"] and "global_min" not in api.compute_params(th)["edges"]
    assert "calibration" not in api.compute_params(th)


def test_model_outputs_on_the_reference_are_computed_once(tmp_path):
    data = write_project(tmp_path / "p")
    fake = FakeModels()
    gate = api.Gate(models=fake, device="cpu")
    ref = gate.prepare(V.load_views(tmp_path / "p" / "renders")["cam_a"], data["rgb"])
    r1 = gate.compare(ref, data["rgb"])
    r2 = gate.compare(ref, texture(data["rgb"], 6))
    assert fake.calls == {"depth": 3, "sam": 3, "dino": 3, "settle": 1}   # 1 reference + 2 tests each
    assert r1["decision"] == "accept" and r1["gate_key"] == ref.gate_key == r2["gate_key"]
    assert set(ref.model_outputs) == {"depth", "sam", "dino"}
    assert set(ref.model_outputs["sam"]["boxes"]) == {"d_1", "win_1", "f_1", "f_2"}
    m = r1["metrics"]
    assert set(m) == set(api.CHECKS) | {"regions", "seconds", "size"}
    assert m["size"] == [640, 360] and m["regions"]["f_1"]["kind"] == "furniture"
    assert all(m[c]["global"] is None or isinstance(m[c]["global"], float) for c in api.CHECKS)
    json.dumps(r1)                                              # JSON-ready for the manifests
    assert gate.model_info()["sam"]["repo"] == "fake/sam"


def test_a_failing_model_fails_the_check_closed(tmp_path):
    data = write_project(tmp_path / "p")
    gate = api.Gate(models=FakeModels(fail={"sam"}), device="cpu")
    ref = gate.prepare(V.load_views(tmp_path / "p" / "renders")["cam_a"], data["rgb"])
    res = gate.compare(ref, data["rgb"])
    assert res["metrics"]["masks"]["error"] == "RuntimeError: sam model failed"
    assert res["decision"] == "reject"
    assert res["reasons"] == [{"check": "masks", "region": "global", "value": None, "threshold": 0.9, "op": ">=",
                               "error": "RuntimeError: sam model failed"}]
    assert "sam" not in ref.model_outputs                       # retried on the next comparison
    assert gate.models.calls["settle"] == 0                     # memory policy waits for a full comparison


def test_without_torch_the_default_models_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "torch", None)             # import torch -> ImportError
    data = write_project(tmp_path / "p")
    gate = api.Gate(device="cuda")
    ref = gate.prepare(V.load_views(tmp_path / "p" / "renders")["cam_a"], data["rgb"])
    res = gate.compare(ref, data["rgb"])
    assert isinstance(gate.models, gate_models.Models) and gate.models.resident is None
    assert res["decision"] == "reject"
    assert {r["check"] for r in res["reasons"]} == {"depth", "masks"}      # features is soft: a note
    assert all("ImportError" in r["error"] or "ModuleNotFoundError" in r["error"] for r in res["reasons"])
    assert [n["check"] for n in res["notes"]] == ["features"]
    assert res["metrics"]["edges"]["global"] == 1.0                         # the CPU checks still ran


def test_gate_without_a_scene_manifest_uses_index_regions(tmp_path):
    data = write_project(tmp_path / "p")
    (tmp_path / "p" / "scene" / "scene_manifest.json").unlink()
    gate = api.Gate(models=FakeModels(), device="cpu")
    ref = gate.prepare(V.load_views(tmp_path / "p" / "renders")["cam_a"], data["rgb"])
    assert "index:12" in ref.regions.masks and ref.albedo == {} and ref.warnings
    assert gate.compare(ref, data["rgb"])["metrics"]["neutral"]["regions"] == {}


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------

def test_benign_generators_are_deterministic_and_small(room):
    rgb = room["data"]["rgb"]
    first = K.benign_controls(rgb, seed=7)
    again = K.benign_controls(rgb, seed=7)
    assert [c["control"] for c in first] == ["exposure", "exposure", "white_balance", "blur", "jpeg", "unsharp",
                                             "noise"]
    for a, b in zip(first, again):
        assert np.array_equal(a["image"], b["image"]), a["control"]
        assert a["image"].shape == rgb.shape and a["image"].dtype == np.uint8
        diff = np.abs(a["image"].astype(int) - rgb.astype(int))
        assert 0 < diff.mean() < 25, (a["control"], diff.mean())          # +0.3 EV moves 200 -> ~222
    assert not np.array_equal(K.noise(rgb, seed=1), K.noise(rgb, seed=2))
    up = K.exposure(rgb, 0.3).astype(int)
    assert (up >= rgb.astype(int)).all() and (K.exposure(rgb, -0.3).astype(int) <= rgb.astype(int)).all()
    wb = K.white_balance(rgb, (1.03, 1.0, 0.97)).astype(int)
    assert (wb[..., 1] == rgb[..., 1]).all() and (wb[..., 0] >= rgb[..., 0]).all() and (wb[..., 2] <= rgb[..., 2]).all()
    assert K.seed_for("toy", "cam_a") == K.seed_for("toy", "cam_a") != K.seed_for("toy", "cam_b")


def test_every_benign_control_is_accepted_by_the_gate(room):
    gate, ref = room["gate"], room["ref"]
    for ctl in K.benign_controls(room["data"]["rgb"], seed=3):
        res = gate.compare(ref, ctl["image"])
        assert res["decision"] == "accept", (ctl["control"], ctl["magnitude"], res["reasons"])


def _changed(a, b):
    return (np.asarray(a) != np.asarray(b)).any(axis=2)


def test_object_negatives_change_only_the_object_and_respect_nearer_objects(room):
    d = room["data"]
    rgb, index, depth_mm = d["rgb"], d["index"], d["depth_mm"]
    sofa = index == SOFA
    chair = index == CHAIR
    grown = K._grow(sofa, 1)
    x0, y0, x1, y1 = K.object_box(sofa)
    negs = K.object_negatives(rgb, index, depth_mm, SOFA, "f_1")
    again = K.object_negatives(rgb, index, depth_mm, SOFA, "f_1")
    assert [(c["control"], c["magnitude"]) for c in negs] == [
        ("shift", 6), ("shift", 12), ("shift", 25), ("scale", 1.04), ("scale", 1.08), ("scale", 1.15),
        ("rotate", 2.0), ("erase", None)]
    for c, c2 in zip(negs, again):
        assert np.array_equal(c["image"], c2["image"]), c["control"]
        changed = _changed(c["image"], rgb)
        assert changed.any(), c["control"]
        # Nearer objects keep their pixels (only the 1 px rim next to the sofa may be inpainted).
        assert not (changed & chair & ~grown).any(), c["control"]
        if c["control"] == "shift":
            assert K.shift_direction(sofa, rgb.shape[1]) == 1           # sofa left of centre: moves right
            moved = np.zeros_like(sofa)
            moved[:, c["magnitude"]:] = sofa[:, :-c["magnitude"]]
            assert not (changed & ~(grown | moved)).any()
            assert c["image"][(y0 + y1) // 2, x0 + c["magnitude"] + 2].tolist() == rgb[(y0 + y1) // 2, x0 + 2].tolist()
        elif c["control"] == "erase":
            assert not (changed & ~grown).any()
        else:
            s = c["magnitude"] if c["control"] == "scale" else 1.0
            pad = 2 + (int(math.ceil(math.hypot(x1 - x0, y1 - y0) * math.sin(math.radians(2.0)))) if
                       c["control"] == "rotate" else 0)
            cx = (x0 + x1 - 1) / 2.0
            bx0, bx1 = cx - (cx - x0) * s - pad, cx + (x1 - cx) * s + pad
            by0 = (y1 - 1) - (y1 - 1 - y0) * s - pad
            ys, xs = np.nonzero(changed & ~grown)
            assert xs.min() >= bx0 - 1 and xs.max() <= bx1 + 1 and ys.min() >= by0 - 1 and ys.max() <= y1 + pad
    with pytest.raises(ValueError):
        K.object_box(np.zeros((4, 4), bool))


def test_view_negatives_paste_on_the_wall_and_edit_only_their_region(room):
    d, ref = room["data"], room["ref"]
    rgb = d["rgb"]
    walls, floor_ = ref.regions.masks["struct:walls"], ref.regions.masks["struct:floor"]
    crop, cmask = K.crop_of(rgb, d["index"], WINDOW)
    donor = {"rgb": crop, "mask": cmask, "camera": "cam_x", "object": "win_9"}
    negs = K.view_negatives(rgb, ref.regions.masks, donor)
    again = K.view_negatives(rgb, ref.regions.masks, donor)
    assert [c["control"] for c in negs] == ["paste", "white_balance_strong", "wall_b", "floor_L"]
    for c, c2 in zip(negs, again):
        assert np.array_equal(c["image"], c2["image"]), c["control"]
    paste = negs[0]
    changed = _changed(paste["image"], rgb)
    assert changed.any() and (changed & ~walls).sum() <= 0.05 * changed.sum()
    assert paste["info"]["cover"] >= 0.95 and paste["info"]["donor_camera"] == "cam_x" and paste["object"] == "win_9"
    wall_b, floor_l = negs[2], negs[3]
    assert not (_changed(wall_b["image"], rgb) & ~walls).any()
    assert not (_changed(floor_l["image"], rgb) & ~floor_).any()
    lab0, lab1 = colour.srgb_to_lab(rgb), colour.srgb_to_lab(wall_b["image"])
    assert (lab1[walls][:, 2] - lab0[walls][:, 2]).mean() == pytest.approx(10.0, abs=0.5)
    lab2 = colour.srgb_to_lab(floor_l["image"])
    assert (lab2[floor_][:, 0] - lab0[floor_][:, 0]).mean() == pytest.approx(-15.0, abs=0.5)
    wb = negs[1]["image"].astype(int)
    assert (wb[..., 0] >= rgb[..., 0]).all() and (wb[..., 2] <= rgb[..., 2]).all()
    # Every negative is rejected by the gate.
    gate = room["gate"]
    for c in negs:
        assert gate.compare(ref, c["image"])["decision"] == "reject", c["control"]
    # Without a donor or a wall region the control is reported as skipped, never invented.
    no_donor = K.view_negatives(rgb, ref.regions.masks, None)
    assert no_donor[0]["image"] is None and no_donor[0]["skipped"] == "no donor crop"
    bare = K.view_negatives(rgb, {}, donor)
    assert [c["image"] is None for c in bare] == [True, False, True, True]


def test_paste_position_prefers_the_wall_centre_and_can_fail():
    wall = np.zeros((100, 200), bool)
    wall[20:80, 40:180] = True
    crop = np.ones((20, 30), bool)
    x, y, cover = K.paste_position(wall, crop, (10, 10))
    assert cover == 1.0 and abs(x + 15 - 109.5) <= 10 and abs(y + 10 - 49.5) <= 10
    assert K.paste_position(wall, np.ones((70, 30), bool), (10, 10)) is None
    assert K.paste_position(np.zeros((10, 10), bool), crop, (5, 5)) is None
    big = np.ones((90, 300, 3), np.uint8)
    out = K.paste_crop(np.zeros((100, 200, 3), np.uint8), wall, big, np.ones((90, 300), bool))
    assert out is not None and out[1]["scale"] < 0.35                    # shrunk to fit, never enlarged


def test_every_object_negative_is_rejected_except_maybe_the_smallest(room):
    gate, ref, d = room["gate"], room["ref"], room["data"]
    decisions = {}
    for c in K.object_negatives(d["rgb"], d["index"], d["depth_mm"], SOFA, "f_1"):
        decisions[(c["control"], c["magnitude"])] = gate.compare(ref, c["image"])["decision"]
    gross = [k for k in decisions if not K.is_small(*k)]
    assert gross and all(decisions[k] == "reject" for k in gross), decisions
    assert decisions[("shift", 6)] == "reject" and decisions[("scale", 1.04)] == "reject"


# --------------------------------------------------------------------------
# Calibration summary and proposal rule
# --------------------------------------------------------------------------

def _rec(control, magnitude, small, decision, edges_region, depth_global, colour_global=1.0, camera="cam_a"):
    return {"camera": camera, "control": control, "magnitude": magnitude, "object": "f_1", "small": small,
            "decision": decision, "reasons": [], "notes": [],
            "metrics": {"edges": {"global": 1.0, "regions": {"f_1": edges_region, "d_1": 1.0}},
                        "depth": {"global": depth_global, "regions": {}},
                        "colour": {"global": colour_global, "regions": {}}}}


def test_proposal_rule_is_25_percent_of_the_gap_to_the_small_negatives():
    th = {"edges": {"hard": True, "global_min": 0.95, "region_min": 0.85},
          "depth": {"hard": True, "global_max": 0.02},
          "colour": {"hard": True, "global_max": 10.0}}
    cal = {
        "benign": [_rec("blur", 1.0, False, "accept", 0.97, 0.004), _rec("jpeg", 75, False, "accept", 0.95, 0.010)],
        "negative": [_rec("shift", 6, True, "reject", 0.75, 0.03), _rec("shift", 12, True, "reject", 0.70, 0.05),
                     _rec("shift", 25, False, "reject", 0.40, 0.20), _rec("erase", None, False, "reject", 0.1, 0.4),
                     _rec("scale", 1.04, True, "accept", 0.90, 0.009), _rec("scale", 1.15, False, "reject", 0.5, 0.1),
                     _rec("wall_b", 10.0, True, "reject", 1.0, 0.0, colour_global=12.0)],
    }
    s = calibrate.summarise(cal, th)
    region = s["per_metric"]["edges"]["region_min"]
    # Small negatives: best (closest to passing) of 0.75, 0.70 and 0.90 -> 0.90 > worst benign 0.95? no: 0.90 < 0.95.
    assert region["worst_benign"] == 0.95 and region["best_small_negative"] == 0.90 and region["best_negative"] == 0.90
    assert region["separates"] and region["proposed"] == pytest.approx(0.95 - 0.25 * 0.05)
    assert region["basis"] == "small" and region["looser_than_current"] is False
    assert region["per_control"] == {"erase": 0.1, "scale:1.04": 0.9, "scale:1.15": 0.5, "shift:12": 0.7,
                                     "shift:25": 0.4, "shift:6": 0.75}
    assert region["caught"] == ["erase", "scale:1.04", "scale:1.15", "shift:12", "shift:25", "shift:6"]
    assert region["missed"] == [] and region["proposed_partial"] is None
    dep = s["per_metric"]["depth"]["global_max"]
    assert dep["worst_benign"] == 0.010 and dep["best_small_negative"] == 0.009 and not dep["separates"]
    assert dep["proposed"] is None
    # depth misses scale x1.04 (0.009 <= worst benign 0.010) but catches the shifts: a partial proposal.
    assert dep["missed"] == ["scale:1.04"] and "shift:6" in dep["caught"]
    assert dep["proposed_partial"] == pytest.approx(0.010 + 0.25 * (0.03 - 0.010))
    assert any(x.startswith("depth.global_max does not separate") and "misses scale:1.04" in x
               for x in s["explanations"])
    col = s["per_metric"]["colour"]["global_max"]                 # only colour negatives count for colour
    assert col["best_negative"] == 12.0 and col["worst_benign"] == 1.0
    assert col["proposed"] == pytest.approx(1.0 + 0.25 * 11.0) and col["looser_than_current"] is False
    # Gross negatives only: the proposal says so.
    cal2 = {"benign": cal["benign"], "negative": [_rec("erase", None, False, "reject", 0.1, 0.4)]}
    e = calibrate.summarise(cal2, th)["per_metric"]["edges"]["region_min"]
    assert e["basis"] == "gross" and e["proposed"] == pytest.approx(0.95 - 0.25 * 0.85)
    assert e["looser_than_current"] is True                       # 0.7375 < 0.85 needs the user's OK
    assert calibrate.proposal(0.95, 0.75) == pytest.approx(0.90)          # *_min limit
    assert calibrate.proposal(0.01, 0.05) == pytest.approx(0.02)          # *_max limit
    # Rates and the smallest detected change.
    assert s["rates"]["benign_accept"] == 1.0 and s["rates"]["negative_reject"] == pytest.approx(6 / 7, abs=1e-4)
    assert s["rates"]["small_negative_reject"] == pytest.approx(3 / 4)
    assert s["rates"]["by_control"]["negative:scale:1.04"] == {"kind": "negative", "control": "scale",
                                                               "magnitude": 1.04, "n": 1, "accepted": 1,
                                                               "rejected": 0, "rate": 0.0}
    assert s["smallest_detected"]["shift_px"] == 6 and s["smallest_detected"]["scale"] == 1.15
    assert s["smallest_detected"]["by_magnitude"]["scale"] == {"1.04": 0.0, "1.15": 1.0}
    assert any("scale:1.04" in x and "accepted" in x for x in s["explanations"])
    assert calibrate.worst_value({"metrics": {"edges": {"error": "x"}}}, "edges", "global", ">=") is None


# --------------------------------------------------------------------------
# Debug image
# --------------------------------------------------------------------------

def test_debug_image_is_a_small_jpeg_with_four_tiles(room, tmp_path):
    gate, ref, d = room["gate"], room["ref"], room["data"]
    test = K.shift_object(d["rgb"], d["index"], d["depth_mm"], SOFA, 25)
    res = gate.compare(ref, test)
    path = gate.write_debug(ref, test, res, tmp_path / "dbg" / "cam_a_a1_gate.jpg")
    assert path.is_file() and path.stat().st_size <= 300_000
    from PIL import Image
    with Image.open(path) as img:
        assert img.format == "JPEG" and img.size == (2 * (960 // 3), 2 * 180 + 28)
    # Without matching artefacts (another image) the CPU maps are recomputed.
    gate.compare(ref, d["rgb"])
    path2 = gate.write_debug(ref, test, res, tmp_path / "dbg" / "again.jpg")
    assert path2.stat().st_size <= 300_000
    from wenart.gate import debug
    assert debug.failing_regions(res)["f_1"].startswith("edges")
    big = np.random.default_rng(0).integers(0, 255, (1080, 1920, 3), dtype=np.uint8)
    p3 = debug.write_debug_image(tmp_path / "noise.jpg", big, big, None, [], None, None, {"decision": "accept"})
    assert p3.stat().st_size <= 300_000


# --------------------------------------------------------------------------
# Model wrapper (fake torch / transformers modules)
# --------------------------------------------------------------------------

class FT:
    """A tiny numpy-backed stand-in for a torch tensor."""

    def __init__(self, a):
        self.a = np.asarray(a)

    @property
    def shape(self):
        return self.a.shape

    def to(self, *args, **kwargs):
        return self

    def cpu(self):
        return self

    def float(self):
        return FT(self.a.astype(np.float32))

    def numpy(self):
        return self.a

    def __getitem__(self, key):
        return FT(self.a[key])

    def __len__(self):
        return len(self.a)


def fake_hf(log):
    """Fake ``torch`` and ``transformers`` modules that record how the wrapper calls them."""
    torch = types.ModuleType("torch")
    torch.float32 = "float32"
    torch.inference_mode = contextlib.nullcontext
    torch.cuda = types.SimpleNamespace(mem_get_info=lambda: (2 * 1024 ** 3, 24 * 1024 ** 3),
                                       empty_cache=lambda: log.append(("empty_cache",)))

    class Model:
        def __init__(self, kind, repo, kwargs):
            self.kind, self.devices = kind, []
            self.config = types.SimpleNamespace(patch_size=14, num_register_tokens=0)
            log.append(("load", kind, repo, kwargs.get("revision"), kwargs.get("dtype")))

        def eval(self):
            return self

        def to(self, device):
            self.devices.append(device)
            return self

        def get_image_embeddings(self, pixel_values):
            log.append(("embed", pixel_values.shape))
            return ["embedding"]

        def __call__(self, **kw):
            if self.kind == "depth":
                return types.SimpleNamespace(predicted_depth=FT(np.ones((1, 37, 66))))
            if self.kind == "sam":
                assert kw["multimask_output"] is False and kw["image_embeddings"] == ["embedding"]
                boxes = kw["input_boxes"].a[0]
                log.append(("decode", len(boxes)))
                H, W = 90, 160
                out = np.zeros((1, len(boxes), 1, H, W), np.float32)
                for k, (x0, y0, x1, y1) in enumerate(boxes):
                    out[0, k, 0, int(y0):int(y1), int(x0):int(x1)] = 1.0
                return types.SimpleNamespace(pred_masks=FT(out))
            pv = kw["pixel_values"].a
            gh, gw = pv.shape[2] // 14, pv.shape[3] // 14
            return types.SimpleNamespace(last_hidden_state=FT(np.arange((1 + gh * gw) * 4, dtype=np.float32)
                                                              .reshape(1, 1 + gh * gw, 4)))

    class Processor:
        def __init__(self, kind):
            self.kind = kind

        def __call__(self, images=None, return_tensors=None, **kw):
            w, h = images.size
            if self.kind == "sam":
                return {"pixel_values": FT(np.zeros((1, 3, 1024, 1024))), "original_sizes": FT([[h, w]]),
                        "input_boxes": FT(np.asarray(kw["input_boxes"], np.float32))}
            if self.kind == "dino":
                log.append(("dino_proc", kw["size"], kw["do_center_crop"]))
                return {"pixel_values": FT(np.zeros((1, 3, kw["size"]["height"], kw["size"]["width"])))}
            return {"pixel_values": FT(np.zeros((1, 3, 518, 924)))}

        def post_process_depth_estimation(self, outputs, target_sizes=None):
            log.append(("depth_post", target_sizes))
            return [{"predicted_depth": FT(np.full(target_sizes[0], 0.5))}]

        def post_process_masks(self, masks, original_sizes):
            return [FT(masks.a[0] > 0)]

    def loader(kind):
        def from_pretrained(repo, **kwargs):
            if kwargs.get("dtype"):
                return Model(kind, repo, kwargs)
            log.append(("proc", kind, repo, kwargs.get("revision")))
            return Processor(kind)
        return types.SimpleNamespace(from_pretrained=from_pretrained)

    tf = types.ModuleType("transformers")
    tf.AutoModelForDepthEstimation = loader("depth")
    tf.Sam2Model = loader("sam")
    tf.Sam2Processor = loader("sam")
    tf.AutoModel = loader("dino")

    def auto_proc(repo, **kwargs):
        return loader("depth" if "Depth" in repo else "dino").from_pretrained(repo, **kwargs)
    tf.AutoImageProcessor = types.SimpleNamespace(from_pretrained=auto_proc)
    return torch, tf


def test_models_wrapper_calls_the_transformers_apis_as_documented(monkeypatch):
    log = []
    torch, tf = fake_hf(log)
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "transformers", tf)
    cfg = api.load_models_config()
    m = gate_models.Models(device="cuda")
    assert m.info() == {k: {"repo": cfg["models"][k]["repo"], "revision": cfg["models"][k]["revision"],
                            "licence": cfg["models"][k]["licence"]} for k in ("depth", "sam", "dino")}
    rgb = np.zeros((90, 160, 3), np.uint8)
    disp = m.depth(rgb)
    assert disp.shape == (90, 160) and disp.dtype == np.float32 and ("depth_post", [(90, 160)]) in log
    boxes = [[10 + k, 5, 40 + k, 50] for k in range(70)]           # more than one decoder chunk
    sam = m.sam_masks(rgb, boxes)
    assert sam.shape == (70, 90, 160) and sam.dtype == bool
    assert sam[3, 5:50, 13:43].all() and not sam[3, :, :13].any()  # order of the boxes kept
    assert [e[1] for e in log if e[0] == "decode"] == [64, 6] and sum(e[0] == "embed" for e in log) == 1
    assert m.sam_masks(rgb, []).shape == (0, 90, 160)
    tok = m.dino_tokens(np.zeros((1080, 1920, 3), np.uint8))
    assert tok.shape == (37, 66, 4) and tok[0, 0, 0] == 4.0          # CLS token dropped
    assert ("dino_proc", {"height": 518, "width": 924}, False) in log
    loads = [e for e in log if e[0] == "load"]
    assert [(e[1], e[2], e[3], e[4]) for e in loads] == [
        ("depth", cfg["models"]["depth"]["repo"], cfg["models"]["depth"]["revision"], "float32"),
        ("sam", cfg["models"]["sam"]["repo"], cfg["models"]["sam"]["revision"], "float32"),
        ("dino", cfg["models"]["dino"]["repo"], cfg["models"]["dino"]["revision"], "float32")]
    assert all(e[3] == cfg["models"][e[1]]["revision"] for e in log if e[0] == "proc")
    # 2 GiB free < 4 GiB: not resident; every model goes back to the CPU after its call.
    assert m.settle() is False and m.memory()["resident"] is False
    sam_model = m._loaded["sam"][1]
    assert sam_model.devices[-1] == "cpu"
    m.sam_masks(rgb, boxes[:2])
    assert sam_model.devices[-2:] == ["cuda", "cpu"] and ("empty_cache",) in log
    assert gate_models.dino_size(1920, 1080) == (518, 924) and gate_models.dino_size(1080, 1080) == (518, 518)


def test_models_wrapper_needs_every_model_key():
    with pytest.raises(KeyError):
        gate_models.Models(config={"models": {"depth": {}}})


# --------------------------------------------------------------------------
# Calibration end to end (fake models, fake expected elements)
# --------------------------------------------------------------------------

class FakeExpected:
    """The §1.4 expected-elements API over the index stats (or NotImplementedError like the F0 stub)."""

    def __init__(self, broken=False):
        self.broken = broken

    def expected_views(self, project_out, render_dir=None):
        if self.broken:
            raise NotImplementedError("area D")
        views = V.load_views(Path(project_out) / "renders")
        table = V.index_table(json.loads((Path(project_out) / "scene" / "scene_manifest.json").read_text()))
        return {cam: {"camera": cam, "room_id": v.room_id, "elements": calibrate.index_elements(v, table)}
                for cam, v in views.items()}

    def sweep_views(self, expected_views, n):
        return sorted(expected_views)[:n]

    def largest_required(self, expected):
        return next((e for e in expected["elements"] if e["role"] == "required"), None)


@pytest.fixture()
def project(tmp_path):
    out = tmp_path / "outputs" / "toy"
    data = write_project(out, cams=(("cam_a", "r_1"), ("cam_b", "r_2")))
    hidden = build_room(640, 360, sofa=False)
    hide = out / "controls" / "hide_f_1"
    hide.mkdir(parents=True)
    entry = write_view(hide, "cam_a", hidden, hidden=["f_1"])
    (hide / "render_manifest.json").write_text(json.dumps({"renders": [entry]}), encoding="utf-8")
    (out / "check").mkdir()
    controls = [{"id": "f_1", "index": SOFA, "kind": "furniture", "camera": "cam_a", "room_id": "r_1", "plug": False,
                 "area_frac": 0.07, "source": "from_documents", "dir": "controls/hide_f_1"},
                {"id": "win_1", "index": WINDOW, "kind": "window", "camera": "cam_a", "room_id": "r_1", "plug": True,
                 "area_frac": 0.06, "source": "from_documents", "dir": "controls/hide_win_1"}]
    (out / "check" / "controls.json").write_text(json.dumps({"schema_version": "0.1", "controls": controls}),
                                                  encoding="utf-8")
    sweep = out / "polish" / "sweep"
    sweep.mkdir(parents=True)
    bad = texture(K.shift_object(data["rgb"], data["index"], data["depth_mm"], SOFA, 40), 20)
    V.write_png_rgb(sweep / "cam_a_a11.png", bad)
    (sweep / "polish_manifest.json").write_text(json.dumps({"views": [
        {"camera": "cam_a", "attempts": [{"k": 1, "role": "grid", "strength": 0.25, "png": "cam_a_a1.png"},
                                         {"k": 11, "role": "presumed_bad", "strength": 0.75, "png": "cam_a_a11.png"}]},
        {"camera": "cam_b", "attempts": [{"k": 11, "role": "presumed_bad", "strength": 0.75, "png": "missing.png"}]},
    ]}), encoding="utf-8")
    return out


def test_calibration_end_to_end(project):
    gate = api.Gate(models=FakeModels(), device="cpu")
    logs = []
    cal = calibrate.run_calibration(project, gate=gate, expected_api=FakeExpected(), log=logs.append)
    js = json.loads((project / "gate" / "gate_calibration.json").read_text(encoding="utf-8"))
    md = (project / "gate" / "gate_calibration.md").read_text(encoding="utf-8")
    assert js["schema_version"] == "0.1" and js["project"] == "toy" and js["incomplete"] is False
    assert js["views"] == ["cam_a", "cam_b"] and [o["wenart_id"] for o in js["objects"]["cam_a"]] == ["f_1", "win_1"]
    assert len(js["benign"]) == 14 and all(r["decision"] == "accept" for r in js["benign"])
    assert js["rates"]["benign_accept"] == 1.0
    controls = {(r["control"], r["camera"]) for r in js["negative"]}
    assert {("removal", "cam_a"), ("insertion", "cam_a"), ("paste", "cam_a"), ("paste", "cam_b")} <= controls
    removal = [r for r in js["negative"] if r["control"] in ("removal", "insertion")]
    assert len(removal) == 2 and all(r["decision"] == "reject" for r in removal)
    assert all(r["object"] == "f_1" for r in removal)
    # Accepted negatives at 640 px: the 2 degree rotations (corners move ~2 px, inside the 3 px radius) and
    # the b* +10 on cam_b's walls (a wet room: tiles, albedo_mode texture, so no neutral check; ΔE < 15).
    accepted = {(r["camera"], r["control"]) for r in js["negative"] if r["decision"] == "accept"}
    assert accepted == {("cam_a", "rotate"), ("cam_b", "rotate"), ("cam_b", "wall_b")}
    wet = next(r for r in js["negative"] if r["camera"] == "cam_b" and r["control"] == "wall_b")
    assert wet["metrics"]["neutral"]["skipped"]["struct:walls"] == "albedo_texture"
    assert js["rates"]["negative_reject"] == pytest.approx(1 - 5 / len(js["negative"]), abs=1e-4)
    assert js["rates"]["by_control"]["negative:rotate:2.0"]["rate"] == 0.0
    assert {s["control"]: s["reason"] for s in js["skipped"]} == {
        "hide:win_1": "control render missing (hide_win_1)", "presumed_bad": "attempt PNG or view missing"}
    assert len(js["presumed_bad"]) == 1 and js["presumed_bad"][0]["decision"] == "reject"
    assert js["presumed_bad"][0]["attempt"] == 11 and js["presumed_bad"][0]["magnitude"] == 0.75
    assert js["presumed_bad"][0]["png"] == "../polish/sweep/cam_a_a11.png"      # relative to gate/ (§1.1)
    assert set(js["per_metric"]) == set(api.CHECKS)
    assert js["per_metric"]["edges"]["region_min"]["basis"] == "small"
    assert js["smallest_detected"]["shift_px"] is not None
    assert js["models"]["sam"]["repo"] == "fake/sam" and js["thresholds"]["edges"]["radius_px"] == 3
    assert md.startswith("# Change-gate calibration: toy\n") and "## Per metric" in md and "| edges | region_min |" in md
    assert "hide:win_1" in md and cal["rates"] == js["rates"] and logs
    # Area D's API missing -> the index-pass fallback, said in the warnings.
    cal2 = calibrate.run_calibration(project, gate=api.Gate(models=FakeModels(), device="cpu"),
                                     expected_api=FakeExpected(broken=True), out_dir=project / "gate2",
                                     cameras=["cam_b"], log=lambda *_: None)
    assert cal2["views"] == ["cam_b"] and any("not implemented" in w for w in cal2["warnings"])
    assert [o["wenart_id"] for o in cal2["objects"]["cam_b"]] == ["f_1", "win_1"]


def test_calibration_stops_at_the_deadline_and_the_cli_runs(project, monkeypatch):
    cal = calibrate.run_calibration(project, gate=api.Gate(models=FakeModels(), device="cpu"),
                                    expected_api=FakeExpected(), deadline=time.time() - 1, log=lambda *_: None)
    assert cal["incomplete"] is True and cal["benign"] == [] and cal["negative"] == []
    js = json.loads((project / "gate" / "gate_calibration.json").read_text(encoding="utf-8"))
    assert js["incomplete"] is True and any("deadline" in w for w in js["warnings"])
    assert "INCOMPLETE" in (project / "gate" / "gate_calibration.md").read_text(encoding="utf-8")
    # CLI: calibrate with the env deadline in the past, then compare one image.
    monkeypatch.setenv("WENART_DEADLINE", str(time.time() - 1))
    rc = gate_main(["calibrate", "--project-out", str(project), "--out", str(project / "gate_cli"), "--views", "1"],
                   gate=api.Gate(models=FakeModels(), device="cpu"), expected_api=FakeExpected())
    assert rc == 0 and json.loads((project / "gate_cli" / "gate_calibration.json").read_text())["incomplete"]
    with pytest.raises(KeyError):
        gate_main(["calibrate", "--project-out", str(project), "--views", "cam_zz"],
                  gate=api.Gate(models=FakeModels(), device="cpu"), expected_api=FakeExpected())
    renders = project / "renders"
    rc = gate_main(["compare", "--render-dir", str(renders), "--camera", "cam_a", "--test", str(renders / "cam_a.png"),
                    "--debug", str(project / "cmp" / "dbg.jpg"), "--json", str(project / "cmp" / "res.json")],
                   gate=api.Gate(models=FakeModels(), device="cpu"))
    assert rc == 0 and (project / "cmp" / "dbg.jpg").is_file()
    assert json.loads((project / "cmp" / "res.json").read_text())["decision"] == "accept"
    rc = gate_main(["compare", "--render-dir", str(renders), "--camera", "cam_a",
                    "--test", str(project / "polish" / "sweep" / "cam_a_a11.png")],
                   gate=api.Gate(models=FakeModels(), device="cpu"))
    assert rc == 1
