"""Milestone 5 Cycles look fixes (docs/milestone5.md §2, §9): CPU tests.

Pure parts (no Blender): flag parsing, metering statistics, exposure and
white-balance maths, the render key and the reuse rule, pass products with
the ``wenart.views`` encoders, plug and oriented boxes, portal placement,
opening rooms, the preview mapping and the build fingerprint.

Blender parts (skipped without a Blender binary): a one-room building
(4 x 3 m, one window in the south wall, one door in the north wall, a sofa
with a cushion and a rotated armchair) built with a tan, noisy fake
``white_plaster_02`` texture and rendered at 64x36 with 8 samples:
camera-only glass (index and depth stop at the pane), flat albedo (the
plaster renders white, not tan), portals, metering, ``--look-from``, render
key reuse, uint16 index maps, depth_mm / normal against the EXR,
``--hide`` / ``--plug`` / ``--hide-sets``, build fingerprint reuse,
``room_ids``, ``box3d`` and the ``preview_maps`` mapping.
"""
import json
import math
import shutil
import textwrap
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import views
from wenart.blender import build as B
from wenart.blender import cameras as C
from wenart.blender import cli, geom2d, lighting, schemas
from wenart.blender import render as R

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                   "/workspace/tools/blender, /opt/wenart/blender, PATH)")
EV = [{"file": "room.dxf", "method": "vector", "confidence": 1.0}]
CAM_FREE, CAM_DOOR, CAM_WINDOW = "cam_r_1_1", "cam_r_1_2", "cam_r_1_3"
WINDOW, DOOR, SOFA, CHAIR = "win_1", "door_1", "f_sofa", "f_chair"
RES, SAMPLES = "64x36", 8


def _wall(wid, start, end):
    return {"id": wid, "level_id": "L0", "start": start, "end": end, "thickness": 0.2, "height": 2.7,
            "exterior": True, "status": "verified", "evidence": EV}


def room_building() -> dict:
    """One 4 x 3 m room: window win_1 (1.2 x 1.2 m, sill 0.9) in the south
    wall, door door_1 in the north wall, a sofa with a cushion, an armchair
    turned by 30 degrees."""
    return {
        "schema_version": "0.1", "status": "ok",
        "project": {"id": "room", "source_folder": "projects/room", "brief": {}},
        "documents": [],
        "levels": [{"id": "L0", "label": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                    "ceiling_height_source": "dimension", "evidence": EV}],
        "walls": [_wall("w_s", [-0.2, -0.1], [4.2, -0.1]), _wall("w_n", [-0.2, 3.1], [4.2, 3.1]),
                  _wall("w_w", [-0.1, -0.2], [-0.1, 3.2]), _wall("w_e", [4.1, -0.2], [4.1, 3.2])],
        "openings": [
            {"id": WINDOW, "type": "window", "level_id": "L0", "wall_id": "w_s", "center": [2.0, -0.1],
             "width": 1.2, "height": 1.2, "sill_height": 0.9, "swing_side": None, "status": "verified",
             "evidence": EV},
            {"id": DOOR, "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [3.0, 3.1],
             "width": 0.8, "height": None, "sill_height": None, "swing_side": None, "status": "verified",
             "evidence": EV},
        ],
        "rooms": [{"id": "r_1", "level_id": "L0", "label": "Room", "room_type": "living",
                   "polygon": [[0.0, 0.0], [4.0, 0.0], [4.0, 3.0], [0.0, 3.0]], "area_computed": 12.0,
                   "area_label": None, "has_documented_furniture": True, "status": "verified", "evidence": EV}],
        "furniture": [
            {"id": SOFA, "level_id": "L0", "room_id": "r_1", "type": "sofa", "source": "from_documents",
             "footprint": {"center": [1.4, 2.5], "size": [1.8, 0.8], "rotation_deg": 0.0}, "front_deg": 270.0,
             "height": None, "asset": None, "status": "verified", "evidence": EV},
            {"id": CHAIR, "level_id": "L0", "room_id": "r_1", "type": "armchair", "source": "added_by_ai",
             "footprint": {"center": [3.1, 1.0], "size": [0.8, 0.8], "rotation_deg": 30.0}, "front_deg": 120.0,
             "height": None, "asset": None, "status": "verified", "evidence": EV},
        ],
        "decor": [{"host_id": SOFA, "type": "cushion", "size": [0.4, 0.4]}],
        "conflicts": [], "unverified": [], "warnings": [],
    }


def _tan_texture_set(root: Path) -> dict:
    """A tan, noisy photo of a white wall (mean linear ~(0.27, 0.25, 0.20), like
    Poly Haven's white_plaster_02) and a grey wood map, CC0 entries."""
    rng = np.random.default_rng(7)
    entries = {}
    for asset_id, mean_lin, size_m in (("white_plaster_02", (0.27, 0.25, 0.20), 1.0),
                                       ("WoodFloor051", (0.20, 0.13, 0.07), 1.0)):
        tex = root / "textures" / asset_id
        tex.mkdir(parents=True, exist_ok=True)
        lin = np.asarray(mean_lin) * (1.0 + 0.2 * rng.standard_normal((64, 64, 1)))
        lin = np.clip(lin, 0.0, 1.0)
        srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
        Image.fromarray((srgb * 255 + 0.5).astype(np.uint8), "RGB").save(tex / "albedo.png")
        Image.new("RGB", (16, 16), (128, 128, 255)).save(tex / "normal.png")
        Image.new("L", (16, 16), 200).save(tex / "roughness.png")
        entries[asset_id] = {"id": asset_id, "source": "polyhaven" if "plaster" in asset_id else "ambientcg",
                             "licence": "CC0", "size_m": [size_m, size_m], "fetched_utc": "2026-10-02T00:00:00Z",
                             "files": {"albedo": f"textures/{asset_id}/albedo.png",
                                       "normal": f"textures/{asset_id}/normal.png",
                                       "roughness": f"textures/{asset_id}/roughness.png"}}
    manifest = {"schema_version": "0.1", "textures": entries, "hdris": {}, "models": {}}
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def _rgb_png(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


# ==========================================================================
# Pure parts
# ==========================================================================

def test_flags_parse_and_refuse_bad_values():
    assert R.parse_exposure("auto") == ("auto", None) and R.parse_exposure("OFF") == ("off", None)
    assert R.parse_exposure("1.5") == ("fixed", 1.5) and R.parse_exposure("-2") == ("fixed", -2.0)
    for bad in ("bright", "nan", "inf"):
        with pytest.raises(R.UsageError):
            R.parse_exposure(bad)
    assert R.parse_white_balance("auto") == ("auto", None) and R.parse_white_balance("off") == ("off", None)
    mode, wp = R.parse_white_balance("fixed:1.1,1,0.8")
    assert mode == "fixed" and float(R.luminance(wp)) == pytest.approx(1.0, abs=1e-5)
    assert wp[0] / wp[2] == pytest.approx(1.1 / 0.8, rel=1e-5)
    for bad in ("fixed:1,1", "fixed:1,0,1", "fixed:a,b,c", "warm"):
        with pytest.raises(R.UsageError):
            R.parse_white_balance(bad)
    assert R.parse_ids(" a, proxy:b ,a,,c") == ["a", "b", "c"]


def test_hide_sets_parse_and_group_by_folder():
    sets = R.parse_hide_sets("cam_a:win_1+plug; cam_b:win_1+plug;cam_a:f_1;cam_a:f_1;cam_c:d_1,d_2")
    assert [s["dir"] for s in sets] == ["hide_win_1", "hide_win_1", "hide_f_1", "hide_f_1", "hide_d_1_d_2"]
    assert sets[0]["plug"] and not sets[2]["plug"] and sets[4]["ids"] == ["d_1", "d_2"]
    groups = R.group_hide_sets(sets)
    assert [(g["dir"], g["cameras"], g["plug"]) for g in groups] == [
        ("hide_win_1", ["cam_a", "cam_b"], True), ("hide_f_1", ["cam_a"], False),
        ("hide_d_1_d_2", ["cam_c"], False)]
    with pytest.raises(R.UsageError, match="with and without"):
        R.group_hide_sets(R.parse_hide_sets("cam_a:win_1+plug;cam_b:win_1"))
    for bad in ("", ";", "cam_a", "cam_a:", ":win_1"):
        with pytest.raises(R.UsageError):
            R.parse_hide_sets(bad)


def _meter_scene(h=36, w=80):
    """Light 0.1 on the left half, 0.4 on the right half; a window block, a
    background strip and a dark (albedo 0.01) strip that must not be metered."""
    light = np.zeros((h, w, 3))
    light[:, : w // 2] = 0.1
    light[:, w // 2:] = 0.4
    albedo = np.full((h, w, 3), 0.8)
    index = np.zeros((h, w))
    depth = np.full((h, w), 3.0)
    index[:10, :20] = 7                   # window glass: very bright, not metered
    light[:10, :20] = 50.0
    depth[:, -4:] = 1e10                  # background
    light[:, -4:] = 99.0
    albedo[-6:, :] = 0.01                 # black floor strip: light is unreliable there
    light[-6:, :] = 0.0
    return light, albedo, index, depth


def test_meter_stats_uses_interior_blocks_only():
    light, albedo, index, depth = _meter_scene()
    s = R.meter_stats(light, albedo, index, depth, {7})
    assert s["block_px"] == 2 and s["blocks"] == 18 * 40
    # Interior: everything but the window, the background and the dark strip.
    interior = 36 * 80 - 10 * 20 - 36 * 4 - 6 * 76 + 0
    assert s["interior_frac"] == pytest.approx(interior / (36 * 80), abs=1e-3)
    # More interior blocks are at 0.4 (right) than at 0.1 (left, minus the window): median 0.4.
    assert s["incident_p50"] == pytest.approx(0.4)
    ill = np.asarray(s["illuminant"])
    assert ill[0] == ill[1] == ill[2] > 0          # grey light, window and background excluded
    # Blocks that are mostly window or background do not count; a nearly empty view has no Y50.
    empty = R.meter_stats(light, albedo, np.full_like(index, 7), depth, {7})
    assert empty["incident_p50"] is None and empty["illuminant"] is None and empty["blocks_used"] == 0
    # A block counts only when >= 75 % of it is interior.
    tiny_light = np.full((4, 4, 3), 1.0)
    tiny_index = np.zeros((4, 4))
    tiny_index[0, :] = 7                                  # 1 row of 4 -> 75 % interior: counts
    s = R.meter_stats(tiny_light, np.full((4, 4, 3), 0.5), tiny_index, np.ones((4, 4)), {7}, blocks_across=1)
    assert s["blocks_used"] == 1 and s["incident_p50"] == pytest.approx(1.0)
    tiny_index[1, :2] = 7                                 # 62.5 % interior: does not count
    s = R.meter_stats(tiny_light, np.full((4, 4, 3), 0.5), tiny_index, np.ones((4, 4)), {7}, blocks_across=1)
    assert s["blocks_used"] == 0 and s["incident_p50"] is None


def test_exposure_is_clamped_and_rounded_to_a_sixth_of_a_stop():
    ev, raw, at_limit = R.exposure_from(0.9 / 2 ** 3.27)
    assert raw == pytest.approx(3.27, abs=1e-3) and ev == pytest.approx(20 / 6) and not at_limit
    assert (ev * 6) == pytest.approx(round(ev * 6))
    ev, raw, at_limit = R.exposure_from(1e-6)
    assert ev == 8.0 and raw > 8 and at_limit
    ev, raw, at_limit = R.exposure_from(100.0)
    assert ev == -2.0 and raw < -2 and at_limit
    ev, _, _ = R.exposure_from(0.45, target=0.9)
    assert ev == pytest.approx(1.0)
    assert R.EXPOSURE_LIMITS == (-2.0, 8.0) and R.EXPOSURE_TARGET == 0.9


def test_whitepoint_keeps_the_mood_residual():
    ill = [1.225 * 3, 1.0 * 3, 0.809 * 3]                # warm light (sum over the mask)
    full = R.whitepoint_from(ill, 0.0)
    assert float(R.luminance(full)) == pytest.approx(1.0, abs=1e-5)
    assert full[0] / full[1] == pytest.approx(1.225, rel=1e-4) and full[2] / full[1] == pytest.approx(0.809, rel=1e-4)
    part = R.whitepoint_from(ill, 0.35)
    assert part[0] / part[1] == pytest.approx(1.225 ** 0.65, rel=1e-4)
    assert R.whitepoint_from(ill, 1.0) == pytest.approx([1.0, 1.0, 1.0], abs=1e-5)
    assert R.whitepoint_from([1.0, 0.0, 1.0], 0.0) is None and R.whitepoint_from([1, 1], 0) is None
    assert R.wb_residual("warm daylight") == (0.35, None) and R.wb_residual("Golden Evening")[0] == 0.5
    assert R.wb_residual("cool daylight")[0] == R.wb_residual("overcast")[0] == 0.0
    assert R.wb_residual("night")[0] == 0.5
    residual, note = R.wb_residual(None)
    assert residual == 0.0 and "residual" in note


def test_window_clip_fraction():
    rgb = np.zeros((4, 4, 3), dtype=np.uint8)
    rgb[0, :] = 255                        # clipped
    rgb[1, :] = (255, 255, 240)            # one channel below 0.98
    index = np.zeros((4, 4), dtype=np.uint16)
    index[:2, :] = 5
    assert R.window_clip_frac(rgb, index, {5}) == 0.5
    assert R.window_clip_frac(rgb, index, {6}) is None
    assert R.window_clip_frac(rgb.astype(float) / 255.0, index, {5}) == 0.5


def test_render_key_covers_every_setting():
    base = dict(samples=128, resolution=[1920, 1080], denoiser="OPENIMAGEDENOISE", exposure_mode="auto",
                exposure_value=None, target=0.9, wb_mode="auto", wb_fixed=None, hidden=[], plugged=[])
    k0 = R.render_key(R.key_settings(**base))
    assert len(k0) == 16 and int(k0, 16) >= 0
    assert R.render_key(R.key_settings(**base)) == k0
    assert R.render_key(R.key_settings(**dict(base, hidden=["b", "a"]))) == \
        R.render_key(R.key_settings(**dict(base, hidden=["a", "b"])))
    changed = [dict(base, samples=64), dict(base, resolution=[960, 540]), dict(base, denoiser=None),
               dict(base, target=0.8), dict(base, exposure_mode="off"),
               dict(base, exposure_mode="fixed", exposure_value=1.0), dict(base, wb_mode="off"),
               dict(base, wb_mode="fixed", wb_fixed=[1.1, 1.0, 0.8]), dict(base, hidden=["win_1"]),
               dict(base, hidden=["win_1"], plugged=["win_1"])]
    keys = {R.render_key(R.key_settings(**c)) for c in changed}
    assert len(keys) == len(changed) and k0 not in keys
    a = R.render_key(R.key_settings(**base, look_from_values={"ev": 3.5, "whitepoint": [1.0, 1.0, 1.0]}))
    b = R.render_key(R.key_settings(**base, look_from_values={"ev": 3.0, "whitepoint": [1.0, 1.0, 1.0]}))
    assert a != b and a != k0
    # The target only matters when exposure is metered.
    assert R.render_key(R.key_settings(**dict(base, exposure_mode="off"))) == \
        R.render_key(R.key_settings(**dict(base, exposure_mode="off", target=0.5)))
    settings = R.key_settings(**base)
    assert settings["code"] == R.RENDER_CODE_VERSION == "m5.2" and settings["passes"] == list(R.PASSES)


def test_reuse_needs_files_fingerprint_and_render_key(tmp_path):
    files = [tmp_path / "a.png", tmp_path / "a_index.png"]
    assert "missing a.png, a_index.png" in R.reuse_reason("a", {}, "fp", files, "k")
    for f in files:
        f.write_bytes(b"x")
    assert "no manifest entry" in R.reuse_reason("a", None, "fp", files, "k")
    assert "not fingerprinted" in R.reuse_reason("a", {"scene_sha256": "fp"}, None, files, "k")
    assert "scene.blend changed" in R.reuse_reason("a", {"scene_sha256": "old"}, "fp", files, "k")
    assert "before Milestone 5" in R.reuse_reason("a", {"scene_sha256": "fp"}, "fp", files, "k")
    assert "k0 -> k" in R.reuse_reason("a", {"scene_sha256": "fp", "render_key": "k0"}, "fp", files, "k")
    assert R.reuse_reason("a", {"scene_sha256": "fp", "render_key": "k"}, "fp", files, "k") is None


def test_look_from_values_need_a_usable_exposure_record():
    assert R.look_from_values({"exposure": {"ev": 3.5, "whitepoint": [1, 1, 1]}}) == \
        {"ev": 3.5, "whitepoint": [1.0, 1.0, 1.0]}
    assert R.look_from_values({"exposure": {"ev": 0.0, "whitepoint": None}}) == {"ev": 0.0, "whitepoint": None}
    for bad in (None, {}, {"exposure": {}}, {"exposure": {"ev": float("nan")}},
                {"exposure": {"ev": 1.0, "whitepoint": [1, 0, 1]}}, {"exposure": {"ev": "3"}}):
        assert R.look_from_values(bad) is None, bad


def test_pass_products_use_the_views_encoders():
    h, w = 6, 8
    depth = np.full((h, w), 2.5, dtype=np.float32)
    depth[0, 0] = 1e10                                   # background
    index = np.zeros((h, w), dtype=np.float32)
    index[2:4, 1:5] = 300.0                              # > 255 must survive
    index[5, 7] = 7.0
    normal = np.zeros((h, w, 3), dtype=np.float32)
    normal[..., 2] = 1.0
    normal[0, 0] = 0.0
    channels = {"ViewLayer.Depth.Z": depth, "ViewLayer.Object Index.X": index,
                **{f"ViewLayer.Normal.{c}": normal[..., i] for i, c in enumerate("XYZ")}}
    p = R.pass_products(channels)
    assert p["index"].dtype == np.uint16 and p["index"].max() == 300
    assert p["index_values"] == [7, 300]
    assert p["index_stats"] == {"7": {"pixels": 1, "box": [7, 5, 8, 6]}, "300": {"pixels": 8, "box": [1, 2, 5, 4]}}
    assert p["depth_mm"][1, 1] == 2500 and p["depth_mm"][0, 0] == 0
    assert np.array_equal(p["depth_mm"], views.encode_depth_mm(depth))
    assert tuple(p["normal"][1, 1]) == (128, 128, 255) and tuple(p["normal"][0, 0]) == (0, 0, 0)
    assert p["depth"]["coverage"] == pytest.approx((h * w - 1) / (h * w)) and p["depth"]["min"] == 2.5
    assert p["depth_legacy"].dtype == np.uint16 and p["depth_legacy"][0, 0] == 65535


def test_plug_box_closes_the_hole_along_the_wall():
    wall = {"wenart_id": "w", "start": [0.0, 0.0], "end": [4.0, 0.0], "thickness": 0.2}
    points = [(1.4, -0.04, 0.9), (2.6, 0.04, 2.1), (2.0, 0.0, 1.5)]
    verts, faces, info = R.plug_box(wall, points)
    xs, ys, zs = zip(*verts)
    assert (min(xs), max(xs)) == pytest.approx((1.4, 2.6)) and (min(zs), max(zs)) == pytest.approx((0.9, 2.1))
    assert (min(ys), max(ys)) == pytest.approx((-0.102, 0.102))          # thickness + 2 x 2 mm, on the centre line
    assert info["thickness_m"] == pytest.approx(0.204)
    for f in faces:                                                       # outward normals
        n = geom2d.face_normal(verts, f)
        c = geom2d.face_center(verts, f)
        assert (c[0] - 2.0) * n[0] + c[1] * n[1] + (c[2] - 1.5) * n[2] > 0
    # A wall along Y (rotated 90 degrees): the box turns with it.
    wall_y = {"wenart_id": "w", "start": [5.0, 0.0], "end": [5.0, 3.0], "thickness": 0.1}
    verts, _, _ = R.plug_box(wall_y, [(5.0, 1.0, 0.0), (5.0, 1.8, 2.1)])
    xs, ys, _ = zip(*verts)
    assert (min(xs), max(xs)) == pytest.approx((4.948, 5.052)) and (min(ys), max(ys)) == pytest.approx((1.0, 1.8))
    with pytest.raises(ValueError):
        R.plug_box(wall, [])


def _wall_side(y, normal_y, slot, pieces):
    """Faces of one side of a wall along X at ``y``: rectangles (x0, x1, z0, z1) in the plane."""
    return [((0.0, normal_y, 0.0), [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], s)
            for (x0, x1, z0, z1), s in zip(pieces, slot if isinstance(slot, list) else [slot] * len(pieces))]


def _slots_by_normal(verts, faces, slots):
    return {tuple(round(c) for c in geom2d.face_normal(verts, f)): s for f, s in zip(faces, slots)}


def test_plug_faces_take_the_material_of_the_wall_face_next_to_the_hole():
    """A plug reads as the wall around it: room side tiles in a bathroom (slot 2), outside the exterior
    plaster (slot 1), top, bottom and ends slot 0, as shell._assign_wall_face_materials sets the wall."""
    wall = {"wenart_id": "w", "start": [0.0, 0.0], "end": [4.0, 0.0], "thickness": 0.2}
    verts, faces, _ = R.plug_box(wall, [(1.4, -0.04, 0.9), (2.6, 0.04, 2.1)])
    around = [(0.0, 1.4, 0.0, 2.7), (2.6, 4.0, 0.0, 2.7), (1.4, 2.6, 0.0, 0.9), (1.4, 2.6, 2.1, 2.7)]
    jambs = [((1.0, 0.0, 0.0), [(1.4, -0.1, 0.9), (1.4, 0.1, 0.9), (1.4, 0.1, 2.1), (1.4, -0.1, 2.1)], 0),
             ((0.0, 0.0, 1.0), [(0.0, -0.1, 2.7), (4.0, -0.1, 2.7), (4.0, 0.1, 2.7), (0.0, 0.1, 2.7)], 0)]
    wet = _wall_side(0.1, 1.0, 2, around) + _wall_side(-0.1, -1.0, 1, around) + jambs
    by_normal = _slots_by_normal(verts, faces, R.plug_face_slots(wall, verts, faces, wet))
    assert by_normal == {(0, 1, 0): 2, (0, -1, 0): 1, (1, 0, 0): 0, (-1, 0, 0): 0, (0, 0, 1): 0, (0, 0, -1): 0}
    # A dry room: slot 0 on the room side.
    dry = _wall_side(0.1, 1.0, 0, around) + _wall_side(-0.1, -1.0, 1, around)
    assert _slots_by_normal(verts, faces, R.plug_face_slots(wall, verts, faces, dry))[(0, 1, 0)] == 0
    # The room side runs on into a dry room (left piece): the faces above and below the hole decide.
    mixed = _wall_side(0.1, 1.0, [0, 2, 2, 2], around) + _wall_side(-0.1, -1.0, 1, around)
    assert _slots_by_normal(verts, faces, R.plug_face_slots(wall, verts, faces, mixed))[(0, 1, 0)] == 2
    # No face next to the hole on that side: the nearest face of that side; none at all: slot 0.
    far = _wall_side(0.1, 1.0, 2, [(3.5, 4.0, 0.0, 2.7)])
    got = _slots_by_normal(verts, faces, R.plug_face_slots(wall, verts, faces, far))
    assert got[(0, 1, 0)] == 2 and got[(0, -1, 0)] == 0
    # A wall along Y: the frame turns with it.
    wall_y = {"wenart_id": "w", "start": [5.0, 0.0], "end": [5.0, 3.0], "thickness": 0.2}
    verts_y, faces_y, _ = R.plug_box(wall_y, [(5.0, 1.0, 0.9), (5.0, 1.8, 2.1)])
    side = [(0.0, 1.0, 0.0, 2.7), (1.8, 3.0, 0.0, 2.7), (1.0, 1.8, 0.0, 0.9), (1.0, 1.8, 2.1, 2.7)]
    turned = [((nx, 0.0, 0.0), [(x, a, z0), (x, b, z0), (x, b, z1), (x, a, z1)], s)
              for nx, x, s in ((1.0, 5.1, 2), (-1.0, 4.9, 1)) for a, b, z0, z1 in side]
    got = _slots_by_normal(verts_y, faces_y, R.plug_face_slots(wall_y, verts_y, faces_y, turned))
    assert got[(1, 0, 0)] == 2 and got[(-1, 0, 0)] == 1 and got[(0, 1, 0)] == 0


def test_oriented_box_measures_in_the_piece_frame():
    verts, _ = geom2d.box((3.1, 1.0, 0.425), (0.8, 0.6, 0.85), 30.0)
    box = geom2d.oriented_box(verts, 30.0)
    assert box["center"] == pytest.approx([3.1, 1.0, 0.425], abs=1e-4)
    assert box["size"] == pytest.approx([0.8, 0.6, 0.85], abs=1e-4) and box["rotation_deg"] == 30.0
    # The same points measured unrotated give the larger axis-aligned box.
    aabb = geom2d.oriented_box(verts, 0.0)
    assert aabb["size"][0] > 0.8 and aabb["size"][1] > 0.6
    with pytest.raises(ValueError):
        geom2d.oriented_box([], 0.0)


def test_opening_rooms_lists_the_rooms_on_either_side():
    building = json.loads((ROOT / "projects" / "synthetic-01" / "truth" / "building.json").read_text("utf-8"))
    rooms = C.opening_rooms(building, "L0")
    openings = {o["id"]: o for o in building["openings"] if o["level_id"] == "L0"}
    assert set(rooms) == set(openings)
    for oid, ids in rooms.items():
        o = openings[oid]
        if o["type"] == "window":
            assert len(ids) == 1, (oid, ids)           # exterior windows: the one room inside
        if o.get("swing_side"):
            assert o["swing_side"] in ids, (oid, ids)  # a door lists the room it opens into
    assert any(len(ids) == 2 for ids in rooms.values())  # an interior door between two rooms
    assert C.opening_rooms(room_building()) == {WINDOW: ["r_1"], DOOR: ["r_1"]}


def test_portal_plan_sits_in_the_window_facing_the_room():
    b = room_building()
    walls = {w["id"]: w for w in b["walls"]}
    plan = lighting.portal_plan(b["openings"][0], walls["w_s"], b["levels"][0], False, b["rooms"])
    assert plan["size"] == pytest.approx([1.1, 1.1])               # 1.2 minus a 5 cm frame each side
    assert plan["inward"] == pytest.approx([0.0, 1.0]) and plan["room_id"] == "r_1" and plan["note"] is None
    assert plan["center"] == pytest.approx([2.0, -0.1 + 0.09, 1.5])  # inner wall face minus 1 cm, sill + 0.6
    # Drawn the other way round, the wall's left side is outside: the portal still faces the room.
    flipped = dict(walls["w_s"], start=[4.2, -0.1], end=[-0.2, -0.1])
    assert lighting.portal_plan(b["openings"][0], flipped, b["levels"][0], False, b["rooms"])["inward"] == \
        pytest.approx([0.0, 1.0])
    lonely = lighting.portal_plan(b["openings"][0], walls["w_s"], b["levels"][0], False, [])
    assert lonely["room_id"] is None and "no room" in lonely["note"]


def test_preview_mapping_is_exactly_100_px_per_metre():
    m = B.preview_mapping(-0.7, -0.7, 4.7, 3.7)
    assert m["resolution"] == [540, 440] and m["m_per_px"] == 0.01 and m["ortho_scale"] == pytest.approx(5.4)
    assert m["bbox_m"] == pytest.approx([-0.7, -0.7, 4.7, 3.7])
    odd = B.preview_mapping(0.0, 0.0, 10.605, 7.2)            # rounds up to whole pixels, centred
    assert odd["resolution"] == [1061, 720]
    assert odd["bbox_m"][2] - odd["bbox_m"][0] == pytest.approx(10.61)
    assert (odd["bbox_m"][0] + odd["bbox_m"][2]) / 2 == pytest.approx(10.605 / 2)
    assert B.preview_mapping(0, 0, 9.6 + 1.0, 7.2 + 1.0)["resolution"] == [1060, 820]   # synthetic-01


def _fp_inputs(tmp_path: Path) -> dict:
    (tmp_path / "building.json").write_text(json.dumps(room_building()), encoding="utf-8")
    shutil.copy(STYLE, tmp_path / "style.json")
    _tan_texture_set(tmp_path / "assets")
    return B.fingerprint_args(str(tmp_path / "building.json"), str(tmp_path / "style.json"),
                              str(tmp_path / "assets"), "L0", False, 4)


def test_build_fingerprint_follows_inputs_code_and_arguments(tmp_path):
    args = _fp_inputs(tmp_path)
    fp = B.build_fingerprint(args)
    assert len(fp) == 64 and B.build_fingerprint(dict(args)) == fp
    assert cli.build_fingerprint(args["building"], args["style"], args["assets"], "L0", False, 4) == fp
    # Arguments.
    assert B.build_fingerprint(dict(args, preview_samples=8)) != fp
    assert B.build_fingerprint(dict(args, proxies=True)) != fp
    # The style file.
    style = json.loads((tmp_path / "style.json").read_text(encoding="utf-8"))
    style["lighting"]["mood"] = "overcast"
    (tmp_path / "style.json").write_text(json.dumps(style), encoding="utf-8")
    fp_style = B.build_fingerprint(args)
    assert fp_style != fp
    # An asset entry the style uses; its fetch time does not count.
    manifest_path = tmp_path / "assets" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["textures"]["white_plaster_02"]["fetched_utc"] = "2030-01-01T00:00:00Z"
    manifest["textures"]["unused_asset"] = {"id": "unused_asset", "licence": "CC0"}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert B.build_fingerprint(args) == fp_style
    manifest["textures"]["white_plaster_02"]["size_m"] = [2.0, 2.0]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert B.build_fingerprint(args) != fp_style
    # The building file.
    b = room_building()
    b["furniture"][0]["footprint"]["center"] = [1.5, 2.5]
    (tmp_path / "building.json").write_text(json.dumps(b), encoding="utf-8")
    assert B.build_fingerprint(args) not in (fp, fp_style)
    # The code: every wenart/blender/*.py file and the vocabulary are hashed.
    code = B.code_hashes()
    assert {"wenart/blender/build.py", "wenart/blender/render.py", "wenart/blender/materials.py",
            "wenart/style/vocabulary.py", "wenart/furniture/catalog.json", "wenart/geometry.py"} <= set(code)
    assert all(v and len(v) == 64 for v in code.values())
    fake = tmp_path / "repo"
    for rel in code:
        (fake / rel).parent.mkdir(parents=True, exist_ok=True)
        (fake / rel).write_text("x", encoding="utf-8")
    before = B.build_fingerprint(args, repo_root=fake)
    (fake / "wenart" / "blender" / "lighting.py").write_text("y", encoding="utf-8")
    assert B.build_fingerprint(args, repo_root=fake) != before


def test_referenced_assets_come_from_the_style_and_the_building():
    style = json.loads(STYLE.read_text(encoding="utf-8"))
    b = room_building()
    b["furniture"][0]["asset"] = {"method": "library", "asset_id": "sofa_02"}
    b["decor"][0]["asset"] = {"asset_id": "cushion_01"}
    ids = B.referenced_asset_ids(b, style)
    assert {"WoodFloor051", "white_plaster_02", "Tiles074", "kloppenheim_06", "sofa_02", "cushion_01"} <= set(ids)
    assert ids == sorted(ids)


def test_reusable_build_needs_every_listed_file(tmp_path):
    ok, why = B.reusable_build(tmp_path, "f" * 64)
    assert not ok and "scene.blend" in why
    (tmp_path / "scene.blend").write_bytes(b"blend")
    assert "scene_manifest" in B.reusable_build(tmp_path, "f" * 64)[1]
    manifest = {"build_fingerprint": "f" * 64, "files": {"blend": "scene.blend", "glb": "scene.glb"},
                "previews": {"L0": "level_L0_top.png"}}
    (tmp_path / "scene_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    ok, why = B.reusable_build(tmp_path, "f" * 64)
    assert not ok and "level_L0_top.png" in why and "scene.glb" in why
    (tmp_path / "scene.glb").write_bytes(b"g")
    (tmp_path / "level_L0_top.png").write_bytes(b"p")
    assert B.reusable_build(tmp_path, "f" * 64) == (True, "")
    ok, why = B.reusable_build(tmp_path, "e" * 64)
    assert not ok and "fingerprint changed" in why


# ==========================================================================
# Blender parts
# ==========================================================================

PROBE_SCRIPT = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    import numpy as np
    from mathutils import Vector
    from wenart.blender import render as R
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
    scene = bpy.context.scene
    out = {}
    if spec.get("portals"):
        rows = []
        for o in scene.objects:
            if o.type == "LIGHT" and o.data.type == "AREA" and o.data.cycles.is_portal:
                mw = o.matrix_world
                rows.append({"name": o.name, "opening": o.get("wenart_opening"), "shape": o.data.shape,
                             "size": [o.data.size, o.data.size_y], "location": list(mw.translation),
                             "minus_z": list((mw.to_3x3() @ Vector((0, 0, -1))).normalized()),
                             "x_axis": list((mw.to_3x3() @ Vector((1, 0, 0))).normalized()),
                             "kind": o.get("wenart_kind"), "status": o.get("wenart_status")})
        out["portals"] = rows
        out["fill_lights"] = [o.name for o in scene.objects if o.type == "LIGHT" and o.data.type == "AREA"
                              and not o.data.cycles.is_portal]
        glass = bpy.data.materials["glass"]
        mix = next(n for n in glass.node_tree.nodes if n.bl_idname == "ShaderNodeMixShader")
        fac = mix.inputs["Fac"].links[0].from_node
        out["glass"] = {"fac_from": [fac.bl_idname, fac.operation,
                                     sorted(link.from_socket.name for i in fac.inputs for link in i.links)],
                        "camera_shader": mix.inputs[2].links[0].from_node.bl_idname,
                        "other_shader": mix.inputs[1].links[0].from_node.bl_idname,
                        "ior": next(n for n in glass.node_tree.nodes
                                    if n.bl_idname == "ShaderNodeBsdfGlass").inputs["IOR"].default_value}
    if spec.get("albedo"):
        cam = bpy.data.objects[spec["albedo"]["camera"]]
        scene.camera = cam
        R.configure_device(scene, "cpu")
        R.configure_render(scene, 16, tuple(spec["albedo"]["res"]), "CPU", False)
        vl = scene.view_layers[0]
        vl.use_pass_diffuse_color = True
        R.set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = spec["albedo"]["exr"]
        bpy.ops.render.render(write_still=True)
        ch = R.read_exr(spec["albedo"]["exr"])
        alb = R.find_rgb(ch, "Diffuse Color")
        nz = R.find_channel(ch, "Normal.Z")
        idx = np.rint(R.find_channel(ch, "Object Index.X"))
        dep = R.find_channel(ch, "Depth.Z")
        wall = (idx == 0) & (np.abs(nz) < 0.3) & (dep < 1e9)
        px = alb[wall]
        lum = px @ np.array(R.LUMA)
        out["albedo"] = {"pixels": int(wall.sum()), "mean": px.mean(axis=0).tolist(),
                         "cv": float(lum.std() / lum.mean())}
    if spec.get("exr"):
        ch = R.read_exr(spec["exr"]["path"])
        np.save(spec["exr"]["out"] + "_z.npy", R.find_channel(ch, "Depth.Z"))
        np.save(spec["exr"]["out"] + "_index.npy", R.find_channel(ch, "Object Index.X"))
        np.save(spec["exr"]["out"] + "_normal.npy", R.find_rgb(ch, "Normal"))
    if spec.get("png16"):
        a = np.array([[0, 255, 256, 300], [1000, 4096, 65534, 65535]], dtype=np.uint16)
        R.write_png(spec["png16"] + "_grey.png", a)
        rgb = np.arange(2 * 3 * 3, dtype=np.uint8).reshape(2, 3, 3) * 10
        R.write_png(spec["png16"] + "_rgb.png", rgb)
    json.dump(out, open(spec["out"], "w"))
""")


def _probe(room, **spec) -> dict:
    tmp = room["tmp"]
    n = len(list(tmp.glob("probe_*.json")))
    spec_path = tmp / f"probe_{n}.json"
    result = tmp / f"probe_{n}.out.json"
    spec["out"] = str(result)
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    (tmp / "probe.py").write_text(PROBE_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "probe.py", [str(spec_path)], blend=str(room["scene"] / "scene.blend"), timeout=600)
    return json.loads(result.read_text(encoding="utf-8"))


def _render(room, out: Path, **kw) -> dict:
    kw.setdefault("samples", SAMPLES)
    kw.setdefault("res", RES)
    path = cli.render(room["scene"] / "scene.blend", out, device="cpu", **kw)
    if kw.get("hide_sets"):
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _entries(manifest: dict) -> dict:
    return {r["camera"]: r for r in manifest["renders"]}


@pytest.fixture(scope="module")
def room(tmp_path_factory):
    """The one-room building built with the tan fake plaster and rendered (3 cameras, auto look)."""
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("look_room")
    (tmp / "building.json").write_text(json.dumps(room_building()), encoding="utf-8")
    _tan_texture_set(tmp / "assets")
    scene = tmp / "scene"
    build_kw = dict(style=STYLE, assets=tmp / "assets", level="L0", preview_samples=4)
    cli.build(tmp / "building.json", scene, **build_kw)
    manifest = json.loads((scene / "scene_manifest.json").read_text(encoding="utf-8"))
    room = {"tmp": tmp, "scene": scene, "manifest": manifest, "build_kw": build_kw, "renders": tmp / "renders"}
    room["render"] = _render(room, room["renders"])
    return room


@needs_blender
def test_build_manifest_has_the_m5_fields(room):
    m = room["manifest"]
    schemas.validate_scene_manifest(m)
    assert m["wenart_mood"] == "warm daylight"
    kw = room["build_kw"]
    assert m["build_fingerprint"] == cli.build_fingerprint(str(room["tmp"] / "building.json"), str(kw["style"]),
                                                           str(kw["assets"]), "L0", False, 4)
    by_name = {o["name"]: o for o in m["objects"]}
    for name in ("win_1_frame", "win_1_glass", "door_1_frame", "door_1_leaf"):
        assert by_name[name]["room_ids"] == ["r_1"], name
    sofa, chair, cushion = by_name["furn_f_sofa"], by_name["furn_f_chair"], by_name["decor_f_sofa_1"]
    # box3d is the mesh as built: on the footprint, turned with the piece.
    assert chair["box3d"]["rotation_deg"] == 30.0 and chair["box3d"]["center"][:2] == pytest.approx([3.1, 1.0], abs=0.02)
    assert chair["box3d"]["size"][:2] == pytest.approx([0.8, 0.8], abs=0.02) and chair["box3d"]["size"][2] > 0.5
    assert sofa["box3d"]["center"][:2] == pytest.approx([1.4, 2.5], abs=0.02)
    assert sofa["box3d"]["size"][:2] == pytest.approx([1.8, 0.8], abs=0.02)
    assert sofa["box3d"]["center"][2] - sofa["box3d"]["size"][2] / 2 == pytest.approx(0.0, abs=0.01)  # on the floor
    assert cushion["box3d"]["center"][2] - cushion["box3d"]["size"][2] / 2 > 0.2                      # on the seat
    table = views.index_table(m)
    assert table[by_name["furn_f_chair"]["pass_index"]]["box3d"] == chair["box3d"]
    assert table[by_name["win_1_glass"]["pass_index"]]["room_ids"] == ["r_1"]


@needs_blender
def test_materials_record_albedo_modes(room):
    mats = room["manifest"]["materials"]
    walls = mats["plaster_white__white_plaster_02"]
    assert walls["textured"] and walls["albedo_mode"] == "flat" and walls["detail"] == 0.35
    assert walls["albedo_gain"] is None and walls["gain_clamped"] is None and walls["tint"] is None
    assert 0.2 < walls["albedo_mean_luminance"] < 0.3                 # the tan photo, measured
    floor = mats["wood_oak_light__WoodFloor051"]
    assert floor["albedo_mode"] == "texture" and floor["detail"] is None
    # (0.20, 0.13, 0.07) -> lum ~0.14; light oak wants ~0.49: gain 3.5 clamped to 2.5.
    assert floor["albedo_gain"] == 2.5 and floor["gain_clamped"] is True
    assert mats["glass"]["reason"].startswith("camera-only glass")
    assert mats["painted_metal_white"]["albedo_mode"] == "flat" and mats["painted_metal_white"]["detail"] == 0.15


@needs_blender
def test_portals_glass_and_no_fill_light(room):
    p = _probe(room, portals=True)
    # Glass for camera rays and singular rays (tests/test_blender_glass.py renders why).
    assert p["glass"] == {"fac_from": ["ShaderNodeMath", "MAXIMUM", ["Is Camera Ray", "Is Singular Ray"]],
                          "camera_shader": "ShaderNodeBsdfGlass",
                          "other_shader": "ShaderNodeBsdfTransparent", "ior": pytest.approx(1.45)}
    assert len(p["portals"]) == 1 and p["fill_lights"] == []          # the room has a window: no fill light
    portal = p["portals"][0]
    assert portal["opening"] == WINDOW and portal["shape"] == "RECTANGLE" and portal["kind"] == "light"
    assert portal["size"] == pytest.approx([1.1, 1.1]) and portal["status"] == "assumed"
    assert portal["minus_z"] == pytest.approx([0.0, 1.0, 0.0], abs=1e-5)       # into the room (+Y)
    assert abs(portal["x_axis"][0]) == pytest.approx(1.0, abs=1e-5)            # size along the wall
    assert portal["location"] == pytest.approx([2.0, -0.01, 1.5], abs=1e-4)
    entry = next(o for o in room["manifest"]["objects"] if o["name"] == portal["name"])
    assert entry["kind"] == "light" and entry["status"] == "assumed" and entry["reason"] == "portal"
    assert room["manifest"]["lighting"]["portals"] == [portal["name"]]


@needs_blender
def test_camera_only_glass_stops_index_and_depth_at_the_pane(room):
    v = views.load_views(room["renders"], [CAM_DOOR])[CAM_DOOR]
    win_index = room["manifest"]["pass_index"][WINDOW]
    idx, depth, normal = v.read_index(), v.read_depth_mm(), v.read_normal()
    pane = idx == win_index
    assert pane.sum() > 20, "the door camera looks at the window"
    # Camera at the door (y ~2.6), pane on the south wall centre line (y = -0.1): 2.7 .. 4.5 m away.
    assert (depth[pane] > 2000).all() and (depth[pane] < 4600).all()
    # Mostly the pane itself (facing +-Y); the frame's sill and head add a few horizontal faces.
    assert (np.abs(normal[pane][:, 1]) > 0.9).mean() > 0.8
    assert v.exposure["window_clip_frac"] is not None


@needs_blender
def test_flat_albedo_renders_the_tan_photo_white(room):
    res = _probe(room, albedo={"camera": CAM_FREE, "res": [64, 36], "exr": str(room["tmp"] / "albedo.exr")})
    a = res["albedo"]
    assert a["pixels"] > 300
    flat = (0.85, 0.84, 0.80)
    assert a["mean"] == pytest.approx(flat, abs=0.03), a      # the vocabulary colour, not the tan photo
    assert a["cv"] < 0.06, a


@needs_blender
def test_metering_records_a_clamped_exposure_and_a_whitepoint(room):
    manifest = room["render"]
    schemas.validate_render_manifest(manifest)
    assert manifest["exposure_mode"] == "auto" and manifest["white_balance_mode"] == "auto"
    assert manifest["scene"] == "../scene/scene.blend" and manifest["view_transform"] == "AgX"
    for e in manifest["renders"]:
        x = e["exposure"]
        assert x["mode"] == "auto" and x["wb_mode"] == "auto" and x["source"] is None
        assert math.isfinite(x["ev"]) and -2.0 <= x["ev"] <= 8.0 and x["ev"] * 6 == pytest.approx(round(x["ev"] * 6))
        assert x["at_limit"] == (x["ev_raw"] < -2.0 or x["ev_raw"] > 8.0)
        assert x["incident_p50"] > 0 and x["target"] == 0.9 and x["limits"] == [-2.0, 8.0]
        assert len(x["whitepoint"]) == 3 and min(x["whitepoint"]) > 0
        assert float(R.luminance(x["whitepoint"])) == pytest.approx(1.0, abs=1e-4)
        assert x["residual"] == 0.35 and x["mood"] == "warm daylight"
        assert 1800 < x["wb_temperature"] < 20000 and x["meter_seconds"] > 0
        assert x["meter"]["resolution"] == [16, 9] and x["meter"]["samples"] == 16
        assert not list(room["renders"].glob(".meter_*")), "the metering EXR is temporary"


@needs_blender
def test_helper_maps_are_uint16_and_agree_with_the_exr(room):
    entry = _entries(room["render"])[CAM_DOOR]
    out = room["renders"]
    for key in ("index", "depth_mm"):
        img = Image.open(out / entry["files"][key])
        assert img.mode.startswith("I;16"), (key, img.mode)
    assert Image.open(out / entry["files"]["normal"]).mode == "RGB"
    stem = str(room["tmp"] / "exr_dump")
    _probe(room, exr={"path": str(out / entry["exr"]), "out": stem})
    z, index, normal = (np.load(f"{stem}_{n}.npy") for n in ("z", "index", "normal"))
    idx = views.read_index(out / entry["files"]["index"])
    depth_mm = views.read_depth_mm(out / entry["files"]["depth_mm"])
    assert np.array_equal(idx, views.encode_index(index))
    assert np.array_equal(depth_mm, views.encode_depth_mm(z))
    valid = z < 1e9
    assert np.abs(depth_mm[valid].astype(float) - z[valid] * 1000.0).max() <= 0.5 + 1e-3
    raw_normal = np.asarray(Image.open(out / entry["files"]["normal"]).convert("RGB"))
    assert np.array_equal(raw_normal, views.encode_normal(normal, valid))
    assert {int(k): v for k, v in entry["index_stats"].items()} == views.compute_index_stats(idx)
    assert sorted(int(k) for k in entry["index_stats"]) == entry["index_values"]


@needs_blender
def test_blender_png_writer_keeps_values_above_255(room):
    stem = str(room["tmp"] / "writer")
    _probe(room, png16=stem)
    grey = views.read_index(stem + "_grey.png")
    assert grey.dtype == np.uint16 and grey.tolist() == [[0, 255, 256, 300], [1000, 4096, 65534, 65535]]
    rgb = views.read_rgb(stem + "_rgb.png")
    assert rgb.tolist() == (np.arange(18, dtype=np.uint8).reshape(2, 3, 3) * 10).tolist()


@needs_blender
def test_render_key_decides_reuse(room, tmp_path):
    out = tmp_path / "renders"
    first = _entries(_render(room, out, cameras=CAM_FREE))[CAM_FREE]
    again = _entries(_render(room, out, cameras=CAM_FREE))[CAM_FREE]
    assert not first["skipped"] and again["skipped"] and again["render_key"] == first["render_key"]
    assert again["exposure"] == first["exposure"] and again["seconds"] == first["seconds"]
    changed = _entries(_render(room, out, cameras=CAM_FREE, exposure_target=0.5))[CAM_FREE]
    assert not changed["skipped"] and changed["render_key"] != first["render_key"]
    # Same metering, another target: log2(0.5 / 0.9) = -0.85 stops (each EV rounded to 1/6).
    assert changed["exposure"]["ev"] - first["exposure"]["ev"] == pytest.approx(math.log2(0.5 / 0.9), abs=0.17)
    log = (out / "render.log").read_text(encoding="utf-8")
    assert "render settings changed" in log
    # An entry without a render key (Milestone 4) is stale.
    path = out / "render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for e in manifest["renders"]:
        e.pop("render_key")
    path.write_text(json.dumps(manifest), encoding="utf-8")
    redone = _entries(_render(room, out, cameras=CAM_FREE, exposure_target=0.5))[CAM_FREE]
    assert not redone["skipped"] and "before Milestone 5" in (out / "render.log").read_text(encoding="utf-8")
    # Fixed and off exposure: no metering for the exposure, the key changes again.
    fixed = _entries(_render(room, out, cameras=CAM_FREE, exposure="1.5", white_balance="off"))[CAM_FREE]
    x = fixed["exposure"]
    assert x["mode"] == "fixed" and x["ev"] == 1.5 and x["whitepoint"] is None and x["meter_seconds"] == 0
    assert x["wb_temperature"] is None and not fixed["skipped"]


@needs_blender
def test_look_from_copies_the_look_and_refuses_missing_cameras(room, tmp_path):
    source = room["renders"] / "render_manifest.json"
    out = tmp_path / "copy"
    entry = _entries(_render(room, out, cameras=CAM_DOOR, look_from=source))[CAM_DOOR]
    src = _entries(room["render"])[CAM_DOOR]
    x = entry["exposure"]
    assert x["mode"] == "from" and x["wb_mode"] == "from" and x["meter_seconds"] == 0
    assert x["ev"] == src["exposure"]["ev"] and x["whitepoint"] == src["exposure"]["whitepoint"]
    assert x["source"] == R.relative_posix(source, out)
    assert x["wb_temperature"] == pytest.approx(src["exposure"]["wb_temperature"], abs=0.2)
    # Same scene, settings and look: the same picture up to sampling noise (8 samples here).
    a, b = _rgb_png(out / entry["png"]), _rgb_png(room["renders"] / src["png"])
    assert a.reshape(-1, 3).mean(axis=0) == pytest.approx(b.reshape(-1, 3).mean(axis=0), abs=3.0)
    assert np.abs(a - b).mean() < 6.0
    # A camera the source manifest does not have: exit 2, nothing rendered.
    partial = tmp_path / "partial.json"
    manifest = json.loads(source.read_text(encoding="utf-8"))
    manifest["renders"] = [r for r in manifest["renders"] if r["camera"] != CAM_WINDOW]
    partial.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(cli.BlenderFailed) as err:
        _render(room, tmp_path / "missing", cameras=CAM_WINDOW, look_from=partial)
    assert err.value.returncode == 2 and "no exposure record" in str(err.value)
    assert not (tmp_path / "missing" / f"{CAM_WINDOW}.png").exists()


@needs_blender
def test_hide_plug_and_hide_sets(room, tmp_path):
    table = room["manifest"]["pass_index"]
    base = views.load_views(room["renders"], [CAM_DOOR, CAM_WINDOW])
    v0 = base[CAM_DOOR]
    pane = v0.read_index() == table[WINDOW]
    pane_depth = v0.read_depth_mm()[pane].astype(float)
    assert pane.sum() > 20 and table[SOFA] in base[CAM_DOOR].index_stats

    # Controls in one Blender process, with the look of the normal renders.
    out = tmp_path / "controls"
    sets = f"{CAM_DOOR}:{WINDOW}+plug;{CAM_DOOR}:{SOFA};{CAM_WINDOW}:{DOOR}"
    _render(room, out, hide_sets=sets, look_from=room["renders"] / "render_manifest.json")
    plugged_m = json.loads((out / f"hide_{WINDOW}" / "render_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_render_manifest(plugged_m)
    assert plugged_m["hidden"] == [WINDOW] and plugged_m["plugged"] == [WINDOW]
    e = _entries(plugged_m)[CAM_DOOR]
    assert e["hidden"] == [WINDOW] and e["plugged"] == [WINDOW] and e["exposure"]["mode"] == "from"
    v = views.load_views(out / f"hide_{WINDOW}")[CAM_DOOR]
    assert v.level_id == "L0" and table[WINDOW] not in v.index_stats
    idx, depth, normal = v.read_index(), v.read_depth_mm(), v.read_normal()
    # Where the pane was: plain wall (index 0, vertical, at the pane's distance minus the half wall).
    assert (idx[pane] == 0).all() and (depth[pane] > 0).all()
    assert (np.abs(normal[pane][:, 2]) < 0.3).mean() > 0.95
    assert np.abs(depth[pane].astype(float) - pane_depth).mean() < 250
    sofa_m = json.loads((out / f"hide_{SOFA}" / "render_manifest.json").read_text(encoding="utf-8"))
    sofa_e = _entries(sofa_m)[CAM_DOOR]
    assert sofa_m["plugged"] == [] and table[SOFA] not in sofa_e["index_values"]   # piece and cushion hidden
    assert table[WINDOW] in sofa_e["index_values"]
    door_e = _entries(json.loads((out / f"hide_{DOOR}" / "render_manifest.json").read_text("utf-8")))[CAM_WINDOW]
    assert table[DOOR] in base[CAM_WINDOW].index_stats and table[DOOR] not in door_e["index_values"]
    # Run again: the reuse check comes first, nothing is rendered or hidden.
    _render(room, out, hide_sets=sets, look_from=room["renders"] / "render_manifest.json")
    log = (out / "render.log").read_text(encoding="utf-8")
    assert log.count("SKIP ") == 3 and "RENDERED" not in log

    # --hide without --plug: the window hole shows the outside (no surface: depth 0).
    hole = _entries(_render(room, tmp_path / "hole", cameras=CAM_DOOR, hide=[WINDOW]))[CAM_DOOR]
    assert hole["hidden"] == [WINDOW] and hole["plugged"] == []
    hv = views.load_views(tmp_path / "hole")[CAM_DOOR]
    assert (hv.read_depth_mm()[pane] == 0).mean() > 0.5

    # An id no indexed object carries: exit 2 before rendering; the CLI passes the 2 on.
    with pytest.raises(cli.BlenderFailed) as err:
        _render(room, tmp_path / "bad", cameras=CAM_DOOR, hide="nope_1")
    assert err.value.returncode == 2 and "unknown id" in str(err.value)
    assert cli.main(["render", "--scene", str(room["scene"] / "scene.blend"), "--out", str(tmp_path / "bad2"),
                     "--cameras", CAM_DOOR, "--res", RES, "--samples", "1", "--device", "cpu",
                     "--hide-sets", f"{CAM_DOOR}:nope_1"]) == 2


PLUG_SCRIPT = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from pathlib import Path
    from wenart.blender import render as R
    out = sys.argv[sys.argv.index("--") + 1]
    manifest = json.loads((Path(bpy.data.filepath).parent / "scene_manifest.json").read_text(encoding="utf-8"))
    hider = R.Hider(bpy.context.scene, manifest)
    hider.apply(["win_1"], plug=True)

    def faces(ob):
        m3 = ob.matrix_world.to_3x3()
        return [[[round(c) for c in (m3 @ p.normal)], ob.data.materials[p.material_index].name]
                for p in ob.data.polygons]

    json.dump({"plug": faces(hider.plugs[0]), "wall": faces(bpy.data.objects["w_s"]),
               "info": hider.info["win_1"]}, open(out, "w"))
""")


@needs_blender
def test_a_plugged_window_in_a_bathroom_shows_the_wall_tiles(room, tmp_path):
    """The plug takes the faces' materials of the wall around the hole: the bathroom tiles on the room
    side, the exterior plaster outside, not the dry wall plaster everywhere."""
    building = room_building()
    building["rooms"][0]["room_type"] = "bathroom"
    (tmp_path / "building.json").write_text(json.dumps(building), encoding="utf-8")
    scene = tmp_path / "scene"
    cli.build(tmp_path / "building.json", scene, **room["build_kw"])
    (tmp_path / "plug.py").write_text(PLUG_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp_path / "plug.py", [str(tmp_path / "plug.json")], blend=str(scene / "scene.blend"),
                    timeout=600)
    got = json.loads((tmp_path / "plug.json").read_text(encoding="utf-8"))

    def side(rows, normal):
        return {m for n, m in rows if n == normal}

    room_side, outside = side(got["wall"], [0, 1, 0]), side(got["wall"], [0, -1, 0])   # room at +Y of w_s
    assert len(room_side) == 1 and next(iter(room_side)).startswith("tiles_light"), got["wall"]
    assert len(outside) == 1 and next(iter(outside)).startswith("plaster_exterior"), got["wall"]
    assert side(got["plug"], [0, 1, 0]) == room_side and side(got["plug"], [0, -1, 0]) == outside
    ends = {m for n, m in got["plug"] if n[1] == 0}
    assert len(ends) == 1 and next(iter(ends)).startswith("plaster_white"), got["plug"]
    # Recorded per side of the wall axis (w_s runs towards +X: its left side is +Y, the room).
    assert got["info"]["materials"] == {"left": next(iter(room_side)), "right": next(iter(outside)),
                                        "ends": next(iter(ends))}


@needs_blender
def test_build_reuse_skips_blender_when_nothing_changed(room, tmp_path, capsys):
    kw = room["build_kw"]
    blend = room["scene"] / "scene.blend"
    mtime = blend.stat().st_mtime_ns
    path = cli.build(room["tmp"] / "building.json", room["scene"], reuse=True, **kw)
    assert path == room["scene"] / "scene_manifest.json"
    assert f"BUILD_REUSED {room['manifest']['build_fingerprint']}" in capsys.readouterr().out
    assert blend.stat().st_mtime_ns == mtime
    # Another style: the fingerprint differs and Blender builds again.
    style = json.loads(STYLE.read_text(encoding="utf-8"))
    style["lighting"]["mood"] = "overcast"
    (tmp_path / "style.json").write_text(json.dumps(style), encoding="utf-8")
    copy = tmp_path / "scene"
    shutil.copytree(room["scene"], copy)
    cli.build(room["tmp"] / "building.json", copy, reuse=True, **dict(kw, style=tmp_path / "style.json"))
    assert "BUILD_NEEDED: fingerprint changed" in capsys.readouterr().out
    rebuilt = json.loads((copy / "scene_manifest.json").read_text(encoding="utf-8"))
    assert rebuilt["build_fingerprint"] != room["manifest"]["build_fingerprint"]
    assert rebuilt["wenart_mood"] == "overcast"


@needs_blender
def test_preview_map_maps_the_walls_to_their_pixels(room):
    m = room["manifest"]
    pm = m["preview_maps"]["L0"]
    assert pm["png"] == m["previews"]["L0"] == "level_L0_top.png" and pm["m_per_px"] == 0.01
    img = np.asarray(Image.open(room["scene"] / pm["png"]).convert("RGB"), dtype=float)
    assert [img.shape[1], img.shape[0]] == pm["resolution"]
    x0, y0, x1, y1 = pm["bbox_m"]
    mpp = pm["m_per_px"]
    # Outer wall faces: x -0.2 .. 4.2, y -0.2 .. 3.2. Outside them the camera sees the dark world.
    bg = img[2, 2]
    fg = np.abs(img - bg).sum(axis=2) > 60
    rows, cols = np.flatnonzero(fg.any(axis=1)), np.flatnonzero(fg.any(axis=0))
    u = lambda x: (x - x0) / mpp      # noqa: E731
    v = lambda y: (y1 - y) / mpp      # noqa: E731
    assert cols[0] == pytest.approx(u(-0.2), abs=1.5) and cols[-1] + 1 == pytest.approx(u(4.2), abs=1.5)
    assert rows[0] == pytest.approx(v(3.2), abs=1.5) and rows[-1] + 1 == pytest.approx(v(-0.2), abs=1.5)
