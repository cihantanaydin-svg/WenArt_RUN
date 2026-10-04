"""CPU tests for wenart.views, the shared view loader of Milestone 5 (docs/milestone5.md §1.2).

Synthetic arrays and a hand-made manifest cover the encoders, the 16-bit PNG
round trip (values above 255 with Pillow 12.x), normals, index statistics,
the pass-index table, regions, geometry edges, the box convention,
``load_views`` with stale entries and ``project_paths``. The pass-index
table is also checked against the committed scene manifests.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import views as V
from wenart.recognition import vlm_client

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "renders"


# --------------------------------------------------------------------------
# Import rule
# --------------------------------------------------------------------------

def test_views_imports_only_stdlib_and_numpy():
    """render.py imports the encoders inside Blender: no Pillow/OpenCV/yaml at import time."""
    code = ("import sys, wenart.views; bad = [m for m in ('PIL', 'cv2', 'yaml', 'torch', 'shapely') "
            "if m in sys.modules]; print(','.join(bad))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


# --------------------------------------------------------------------------
# Encoders
# --------------------------------------------------------------------------

def test_encode_depth_mm_rounds_and_blanks_invalid_values():
    z = np.array([[1.2344, 0.0, -1.0, np.nan],
                  [np.inf, 1e10, 65.535, 65.6],
                  [0.0004, 0.0006, 3.0, 2e9]], dtype=np.float64)
    out = V.encode_depth_mm(z)
    assert out.dtype == np.uint16 and out.shape == z.shape
    assert out.tolist() == [[1234, 0, 0, 0],
                            [0, 0, 65535, 0],
                            [0, 1, 3000, 0]]
    assert V.encode_depth_mm(z.astype(np.float32))[2, 2] == 3000          # float32 EXR channels work too
    assert V.encode_depth_mm(np.array([[2.5004]]))[0, 0] == 2500


def test_encode_index_rint_and_clip():
    x = np.array([[0.0, 12.0000001, 300.4, 300.6], [70000.0, -3.0, np.nan, 65535.2]])
    out = V.encode_index(x)
    assert out.dtype == np.uint16
    assert out.tolist() == [[0, 12, 300, 301], [65535, 0, 0, 65535]]


def _unit_normals(h, w, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.normal(size=(h, w, 3))
    return n / np.linalg.norm(n, axis=2, keepdims=True)


def test_normal_encode_write_read_round_trip(tmp_path):
    n = _unit_normals(6, 7)
    n[0, 0] = [0.0, 0.0, -1.0]            # a channel at -1 still has the others > 0
    hit = np.ones((6, 7), dtype=bool)
    hit[5, 6] = hit[2, 3] = False
    enc = V.encode_normal(n, hit)
    assert enc.dtype == np.uint8 and enc.shape == (6, 7, 3)
    assert enc[5, 6].tolist() == [0, 0, 0] and enc[0, 0].tolist() == [128, 128, 0]
    path = V.write_png_rgb(tmp_path / "n.png", enc)
    back = V.read_normal(path)
    assert back.dtype == np.float32 and back.shape == (6, 7, 3)
    hit_back = V.normal_hit(back)
    assert (hit_back == hit).all()
    assert np.abs(back[hit] - n[hit]).max() <= 0.5 / 127.5 + 1e-6
    assert (back[~hit] == 0).all()
    assert (back[hit] != 0).all()        # 127.5 is not an integer: no exact zero component
    # hit=None: every finite non-zero normal is hit.
    n2 = n.copy()
    n2[1, 1] = 0.0
    n2[1, 2] = np.nan
    enc2 = V.encode_normal(n2)
    assert enc2[1, 1].tolist() == [0, 0, 0] and enc2[1, 2].tolist() == [0, 0, 0] and enc2[0, 1].any()
    with pytest.raises(ValueError):
        V.encode_normal(np.zeros((4, 4)), None)


# --------------------------------------------------------------------------
# 16-bit PNG and RGB readers
# --------------------------------------------------------------------------

def test_png16_round_trip_keeps_values_above_255(tmp_path):
    a = np.array([[0, 1, 255, 256], [1000, 30000, 65534, 65535]], dtype=np.uint16)
    path = V.write_png16(tmp_path / "sub" / "idx.png", a)
    with Image.open(path) as img:
        assert img.mode.startswith("I;16") and img.size == (4, 2)
    for reader in (V.read_index, V.read_depth_mm):
        back = reader(path)
        assert back.dtype == np.uint16 and back.tolist() == a.tolist()
    # Integer arrays of another dtype are accepted when they fit, never wrapped.
    V.write_png16(tmp_path / "i32.png", a.astype(np.int32))
    assert V.read_index(tmp_path / "i32.png").tolist() == a.tolist()
    with pytest.raises(ValueError):
        V.write_png16(tmp_path / "bad.png", np.array([[70000]], dtype=np.int32))
    with pytest.raises(ValueError):
        V.write_png16(tmp_path / "bad.png", np.array([[-1]], dtype=np.int32))
    with pytest.raises(ValueError):
        V.write_png16(tmp_path / "bad.png", np.zeros((2, 2), dtype=np.float32))
    with pytest.raises(ValueError):
        V.write_png16(tmp_path / "bad.png", np.zeros((2, 2, 3), dtype=np.uint16))


def test_grey_readers_accept_mode_i_and_8_bit_and_reject_rgb(tmp_path):
    # Older Pillow versions open a 16-bit PNG as mode I (int32); a TIFF gives that mode here
    # (saving mode I as PNG is deprecated in Pillow 12).
    Image.fromarray(np.array([[3, 300]], dtype=np.int32)).save(tmp_path / "mode_i.tif")
    with Image.open(tmp_path / "mode_i.tif") as img:
        assert img.mode == "I"
    assert V.read_index(tmp_path / "mode_i.tif").tolist() == [[3, 300]]
    Image.fromarray(np.array([[-3, 70000]], dtype=np.int32)).save(tmp_path / "bad_i.tif")
    with pytest.raises(ValueError):
        V.read_index(tmp_path / "bad_i.tif")
    Image.fromarray(np.array([[7, 200]], dtype=np.uint8)).save(tmp_path / "l.png")
    legacy = V.read_index(tmp_path / "l.png")
    assert legacy.dtype == np.uint16 and legacy.tolist() == [[7, 200]]
    Image.fromarray(np.zeros((2, 2, 3), dtype=np.uint8)).save(tmp_path / "rgb.png")
    with pytest.raises(ValueError):
        V.read_depth_mm(tmp_path / "rgb.png")


def test_read_rgb_converts_any_mode(tmp_path):
    rgba = np.zeros((3, 4, 4), dtype=np.uint8)
    rgba[..., 0] = 200
    rgba[..., 3] = 255
    Image.fromarray(rgba).save(tmp_path / "a.png")
    out = V.read_rgb(tmp_path / "a.png")
    assert out.dtype == np.uint8 and out.shape == (3, 4, 3) and out[0, 0].tolist() == [200, 0, 0]
    out[0, 0] = 1                                    # writable copy
    V.write_png_rgb(tmp_path / "b.png", out)
    assert V.read_rgb(tmp_path / "b.png")[0, 0].tolist() == [1, 1, 1]
    with pytest.raises(ValueError):
        V.write_png_rgb(tmp_path / "c.png", np.zeros((3, 4), dtype=np.uint8))


def test_compute_index_stats_boxes_are_exclusive():
    idx = np.zeros((10, 20), dtype=np.uint16)
    idx[2:5, 3:9] = 12
    idx[9, 19] = 300
    stats = V.compute_index_stats(idx)
    assert stats == {12: {"pixels": 18, "box": [3, 2, 9, 5]}, 300: {"pixels": 1, "box": [19, 9, 20, 10]}}
    assert V.compute_index_stats(np.zeros((3, 3), dtype=np.uint16)) == {}


# --------------------------------------------------------------------------
# Pass-index table
# --------------------------------------------------------------------------

def _obj(name, wenart_id, kind, pass_index, **extra):
    base = {"name": name, "wenart_id": wenart_id, "kind": kind, "status": "verified", "level_id": "L0",
            "evidence": [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}], "material": None,
            "textured": False, "pass_index": pass_index, "assumed": {}}
    base.update(extra)
    return base


def hand_made_manifest() -> dict:
    """A small scene manifest with every kind of object render.py and build.py write."""
    return {
        "schema_version": "0.1", "project": "toy", "building": "outputs/toy/building_final.json",
        "style_profile": {"walls": {"material": "plaster_white"}},
        "cameras": [{"name": "cam_a", "room_id": "r_L0_salon", "level_id": "L0"},
                    {"name": "cam_b", "room_id": "r_L0_hol", "level_id": "L0"}],
        "pass_index": {"d_1": 1, "win_1": 2, "f_1": 3, "proxy:f_9": 4, "dec_1": 5, "f_2": 6},
        "objects": [
            _obj("w_1", "w_1", "wall", None),
            _obj("r_L0_salon_floor", "r_L0_salon", "floor", None),
            _obj("d_1_threshold", "d_1", "floor", None, room_id="r_L0_salon"),
            _obj("op_1", "op_1", "opening", None),
            _obj("d_1_frame", "d_1", "door", 1, wall_id="w_1", room_ids=["r_L0_salon", "r_L0_hol"]),
            _obj("d_1_leaf", "d_1", "door", 1, wall_id="w_1"),
            _obj("win_1_frame", "win_1", "window", 2, wall_id="w_1"),
            _obj("win_1_glass", "win_1", "window", 2, wall_id="w_1", room_ids=["r_L0_salon"]),
            # Hosted decor listed before its host: the host still wins.
            _obj("decor_f_1_1", "f_1", "decor", 3, host_id="f_1", room_id="r_L0_salon", type="cushion",
                 source="added_by_ai", status="assumed"),
            _obj("furn_f_1", "f_1", "furniture", 3, room_id="r_L0_salon", type="sofa", source="from_documents",
                 center=[1.0, 2.0, 0.4], size=[2.0, 0.9, 0.8], rotation_deg=90.0),
            _obj("decor_f_1_2", "f_1", "decor", 3, host_id="f_1", room_id="r_L0_salon", type="cushion",
                 source="added_by_ai", status="assumed"),
            _obj("decor_f_1_3", "f_1", "decor", 3, host_id="f_1", room_id="r_L0_salon", type="textile",
                 source="added_by_ai", status="assumed"),
            _obj("proxy_f_9", "proxy:f_9", "furniture_proxy", 4, room_id="r_L0_hol", type="unknown",
                 source="from_documents", status="unverified", center=[3, 3, 0.4], size=[1, 1, 0.8], rotation_deg=0),
            _obj("decor_dec_1", "dec_1", "decor", 5, room_id="r_L0_salon", type="plant", source="added_by_ai",
                 status="assumed", center=[0.5, 0.5, 0.3], size=[0.4, 0.4, 0.6], rotation_deg=0.0),
            _obj("furn_f_2", "f_2", "furniture", 6, room_id="r_L0_hol", type="tv_unit", source="added_by_ai",
                 box3d={"center": [5, 5, 0.25], "size": [1.6, 0.4, 0.5], "rotation_deg": 180.0},
                 center=[0, 0, 0], size=[1, 1, 1], rotation_deg=0.0),
            _obj("cam_a", "cam_a", "camera", None),
            _obj("sun", "sun", "light", None),
        ],
    }


def test_index_table_on_a_hand_made_manifest():
    table = V.index_table(hand_made_manifest())
    assert list(table) == [1, 2, 3, 4, 5, 6]
    door, window, sofa, proxy, plant, tv = (table[i] for i in range(1, 7))
    assert door["wenart_id"] == "d_1" and door["kind"] == "door" and door["type"] == "door"
    assert door["room_ids"] == ["r_L0_salon", "r_L0_hol"] and door["room_id"] is None
    assert door["source"] == "from_documents" and door["box3d"] is None and door["host_decor"] == []
    assert window["kind"] == "window" and window["room_ids"] == ["r_L0_salon"]   # merged over the parts
    assert sofa["wenart_id"] == "f_1" and sofa["kind"] == "furniture" and sofa["type"] == "sofa"
    assert sofa["host_decor"] == ["cushion", "textile"] and sofa["status"] == "verified"
    assert sofa["source"] == "from_documents" and sofa["room_ids"] == ["r_L0_salon"]
    assert sofa["box3d"] == {"center": [1.0, 2.0, 0.4], "size": [2.0, 0.9, 0.8], "rotation_deg": 90.0}
    assert sofa["evidence"][0]["method"] == "vector" and sofa["manifest_kind"] == "furniture"
    assert proxy["wenart_id"] == "f_9" and proxy["kind"] == "furniture" and proxy["type"] == "unknown"
    assert proxy["status"] == "unverified" and proxy["manifest_kind"] == "furniture_proxy"
    assert plant["kind"] == "decor" and plant["type"] == "plant" and plant["source"] == "added_by_ai"
    assert tv["box3d"] == {"center": [5, 5, 0.25], "size": [1.6, 0.4, 0.5], "rotation_deg": 180.0}
    # The table keys match the manifest's own pass-index table.
    m = hand_made_manifest()
    assert {v: k.replace("proxy:", "") for k, v in m["pass_index"].items()} == {
        i: e["wenart_id"] for i, e in table.items()}


def test_index_table_hosted_decor_without_host_falls_back_to_decor():
    m = {"objects": [_obj("decor_x", "f_7", "decor", 9, host_id="f_7", type="book_set", room_id="r")]}
    entry = V.index_table(m)[9]
    assert entry["kind"] == "decor" and entry["wenart_id"] == "f_7" and entry["host_decor"] == ["book_set"]


@pytest.mark.parametrize("project, n, counts", [
    ("synthetic-01", 64, {"door": 9, "window": 12, "furniture": 39, "decor": 4}),
    ("synthetic-03", 91, {"door": 17, "window": 16, "furniture": 53, "decor": 5}),
])
def test_index_table_matches_the_m5_scene_manifests(project, n, counts):
    """The M5 scene manifests (commit a2adcef; results/ now holds the M6 runs)."""
    try:
        raw = subprocess.run(["git", "-C", str(RESULTS.parents[1]), "show",
                              f"a2adcef:results/renders/{project}/scene_manifest.json"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git history with the M5 scene manifests not available")
    scene = json.loads(raw.decode("utf-8"))
    table = V.index_table(scene)
    assert len(table) == n == len(scene["pass_index"])
    assert {v: k.replace("proxy:", "") for k, v in scene["pass_index"].items()} == {
        i: e["wenart_id"] for i, e in table.items()}
    got = {}
    for e in table.values():
        got[e["kind"]] = got.get(e["kind"], 0) + 1
        assert e["kind"] in V.OBJECT_KINDS and e["evidence"] and e["status"]
        assert e["source"] in ("from_documents", "added_by_ai")
        if e["kind"] in ("furniture", "decor"):
            assert e["room_id"] and e["room_ids"] == [e["room_id"]] and e["box3d"]["size"]
        else:
            # Openings (M5 manifests): the rooms whose edge carries them, one (outer wall) or two (inner wall).
            assert e["type"] == e["kind"] and e["box3d"] is None and 1 <= len(e["room_ids"]) <= 2
    assert got == counts
    hosted = {o["pass_index"] for o in scene["objects"] if o["kind"] == "decor" and o.get("host_id")}
    for pi in hosted:
        assert table[pi]["kind"] == "furniture" and table[pi]["host_decor"]
    plants = [e for e in table.values() if e["kind"] == "decor"]
    assert plants and all(e["type"] == "plant" and not e["host_decor"] for e in plants)
    if project == "synthetic-01":
        assert table[12]["wenart_id"] == "f_L0_001" and table[12]["host_decor"] == ["cushion"]
        assert table[1]["wenart_id"] == "d_L0_001" and table[6]["wenart_id"] == "win_L0_001"
    else:
        proxy = table[scene["pass_index"]["proxy:f_L0_021"]]
        assert proxy["wenart_id"] == "f_L0_021" and proxy["type"] == "unknown" and proxy["status"] == "unverified"


# --------------------------------------------------------------------------
# Regions and geometry edges
# --------------------------------------------------------------------------

def toy_view(h=60, w=80):
    """index/depth_mm/normal of a tiny room: ceiling top, wall middle, floor bottom, a sofa and a window."""
    index = np.zeros((h, w), dtype=np.uint16)
    depth = np.full((h, w), 3000, dtype=np.uint16)
    normal = np.zeros((h, w, 3), dtype=np.float32)
    normal[:15] = [0, 0, -1]          # ceiling
    normal[15:40] = [1, 0, 0]         # wall
    normal[40:] = [0, 0, 1]           # floor
    index[40:50, 10:30] = 3           # sofa (pass index 3 = f_1)
    depth[40:50, 10:30] = 2000
    normal[40:50, 10:30] = [0, -1, 0]
    index[18:38, 50:70] = 2           # window (pass index 2 = win_1), 20 x 20
    index[20:24, 2:6] = 99            # an index missing from the table
    depth[0:3, 70:80] = 0             # background (no surface)
    normal[0:3, 70:80] = 0
    return index, depth, normal


def test_regions_objects_structure_background_and_panes():
    index, depth, normal = toy_view()
    table = V.index_table(hand_made_manifest())
    reg = V.regions(index, depth, normal, table)
    assert set(reg.object_ids()) == {"f_1", "win_1", "index:99"}
    assert set(reg.structure_ids()) == {V.STRUCT_FLOOR, V.STRUCT_CEILING, V.STRUCT_WALLS}
    assert reg.kinds["f_1"] == "furniture" and reg.kinds["win_1"] == "window" and reg.kinds["index:99"] == "unknown"
    assert reg.kinds[V.STRUCT_FLOOR] == "floor" and reg.kinds[V.STRUCT_WALLS] == "wall"
    assert reg.pixels["f_1"] == 200 and reg.pixels["win_1"] == 400 and reg.indices["f_1"] == 3
    assert reg.background.sum() == 30
    assert reg.pixels[V.STRUCT_CEILING] == 15 * 80 - 30                       # background is no structure
    assert reg.pixels[V.STRUCT_WALLS] == 25 * 80 - 400 - 16
    assert reg.pixels[V.STRUCT_FLOOR] == 20 * 80 - 200
    total = sum(reg.pixels.values()) + int(reg.background.sum())
    assert total == index.size                                                 # every pixel in one region
    assert reg.panes.sum() == 8 * 8 and reg.panes[24:32, 56:64].all()           # 20 x 20 eroded by 6 px
    assert not (reg.panes & ~reg.masks["win_1"]).any()
    # Encoded uint8 normals give the same regions.
    enc = V.encode_normal(normal, V.normal_hit(normal))
    reg8 = V.regions(index, depth, enc, table, pane_erode_px=2)
    assert reg8.pixels == reg.pixels and reg8.panes.sum() == 16 * 16
    with pytest.raises(ValueError):
        V.regions(index[:10], depth, normal, table)


def test_erode_keeps_the_image_border_like_cv2():
    m = np.zeros((10, 10), dtype=bool)
    m[0:5, 0:5] = True                         # touches the top-left image corner
    out = V.erode(m, 2)
    assert out[0:3, 0:3].all() and out.sum() == 9
    assert (V.erode(m, 0) == m).all() and not V.erode(np.zeros((4, 4), bool), 3).any()


def test_geometry_edges_index_depth_and_normal_changes():
    h, w = 20, 30
    index = np.zeros((h, w), dtype=np.uint16)
    depth = np.full((h, w), 3000, dtype=np.uint16)
    normal = np.zeros((h, w, 3), dtype=np.float32)
    normal[:] = [1, 0, 0]
    assert not V.geometry_edges(index, depth, normal).any()        # one flat surface: no edge
    # An object nearer than the wall: its outline is marked on the object's side, 1 px wide.
    index[5:10, 5:10] = 7
    depth[5:10, 5:10] = 2000
    e = V.geometry_edges(index, depth, normal)
    assert e.dtype == bool
    ring = np.zeros_like(e)
    ring[5:10, 5:10] = True
    ring[6:9, 6:9] = False
    assert (e == ring).all()
    # Depth steps: 2 % is no edge, 5 % is (marked on the nearer side).
    d2 = np.full((h, w), 3000, dtype=np.uint16)
    d2[:, 15:] = 3060
    assert not V.geometry_edges(np.zeros((h, w), np.uint16), d2, normal).any()
    d2[:, 15:] = 3150
    e2 = V.geometry_edges(np.zeros((h, w), np.uint16), d2, normal)
    assert e2[:, 14].all() and e2.sum() == h
    d2[:, 15:] = 2850                                               # now the right side is nearer
    assert V.geometry_edges(np.zeros((h, w), np.uint16), d2, normal)[:, 15].all()
    # Normal turns: 20 degrees is no edge, 90 degrees (wall to floor) is.
    n2 = np.zeros((h, w, 3), dtype=np.float32)
    n2[:] = [1, 0, 0]
    a = math.radians(20)
    n2[10:] = [math.cos(a), math.sin(a), 0]
    flat = np.full((h, w), 3000, dtype=np.uint16)
    assert not V.geometry_edges(np.zeros((h, w), np.uint16), flat, n2).any()
    n2[10:] = [0, 0, 1]
    e3 = V.geometry_edges(np.zeros((h, w), np.uint16), flat, n2)
    assert e3[9].all() and e3.sum() == w
    # Background next to a surface is an edge on the surface side; uint8 normals work too.
    d3 = flat.copy()
    d3[:, :3] = 0
    e4 = V.geometry_edges(np.zeros((h, w), np.uint16), d3, V.encode_normal(normal, d3 > 0))
    assert e4[:, 3].all() and e4.sum() == h


# --------------------------------------------------------------------------
# Boxes
# --------------------------------------------------------------------------

def test_box_to_1000_rounds_outwards_and_round_trips():
    assert V.box_to_1000([0, 0, 1920, 1080], 1920, 1080) == [0, 0, 1000, 1000]
    assert V.box_to_1000([1, 1, 2, 2], 1920, 1080) == [0, 0, 2, 2]
    assert V.box_to_1000([960, 540, 961, 541], 1920, 1080) == [500, 500, 501, 501]
    assert V.box_to_1000([10.5, 20.2, 30.7, 40.1], 1920, 1080) == [5, 18, 16, 38]
    assert V.box_to_1000([np.int64(3), 3, 1921, 1100], 1920, 1080)[2:] == [1000, 1000]
    box = [123, 456, 789, 1011]
    back = vlm_client.norm1000_to_pixels(V.box_to_1000(box, 1920, 1080), 1920, 1080)
    assert back[0] <= box[0] and back[1] <= box[1] and back[2] >= box[2] and back[3] >= box[3]
    assert back[2] - box[2] < 1920 / 1000 + 1e-9 and back[3] - box[3] < 1080 / 1000 + 1e-9


# --------------------------------------------------------------------------
# load_views
# --------------------------------------------------------------------------

def m5_entry(camera, room_id, **extra):
    entry = {
        "camera": camera, "png": f"{camera}.png", "exr": f"{camera}_passes.exr", "preview": f"{camera}_preview.jpg",
        "depth_png": f"{camera}_depth.png", "index_png": f"{camera}_index.png", "seconds": 1.0, "samples": 16,
        "resolution": [80, 60], "index_values": [2, 3], "room_id": room_id, "scene_sha256": "x",
        "index_stats": {"3": {"pixels": 200, "box": [10, 40, 30, 50]}, "2": {"pixels": 400, "box": [50, 18, 70, 38]}},
        "files": {"depth_mm": f"{camera}_depth_mm.png", "normal": f"{camera}_normal.png"},
        "render_key": "0123456789abcdef", "exposure": {"mode": "auto", "ev": 1.5},
        "hidden": [], "plugged": [],
    }
    entry.update(extra)
    return entry


def write_render_dir(project_out: Path, entries: list[dict]) -> Path:
    """renders/ with a manifest and the PNGs of every entry; scene/ with the hand-made scene manifest."""
    renders = project_out / "renders"
    renders.mkdir(parents=True)
    index, depth, normal = toy_view()
    for e in entries:
        V.write_png_rgb(renders / e["png"], np.full((60, 80, 3), 128, dtype=np.uint8))
        V.write_png16(renders / e["index_png"], index)
        files = e.get("files") or {}
        if files.get("depth_mm"):
            V.write_png16(renders / files["depth_mm"], depth)
        if files.get("normal"):
            V.write_png_rgb(renders / files["normal"], V.encode_normal(normal, V.normal_hit(normal)))
    manifest = {"schema_version": "0.1", "scene": "/nowhere/scene/scene.blend", "renders": entries}
    (renders / "render_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (project_out / "scene").mkdir()
    (project_out / "scene" / "scene_manifest.json").write_text(json.dumps(hand_made_manifest()), encoding="utf-8")
    return renders


def test_load_views_reads_m5_entries_and_flags_stale_ones(tmp_path):
    stale = m5_entry("cam_old", "r_L0_hol")
    del stale["render_key"]
    no_normal = m5_entry("cam_c", "r_L0_hol", files={"depth_mm": "cam_c_depth_mm.png"})
    renders = write_render_dir(tmp_path / "toy", [m5_entry("cam_a", "r_L0_salon"), stale, no_normal,
                                                  m5_entry("cam_b", "r_L0_hol", level_id="L9", hidden=["f_1"],
                                                           plugged=["win_1"])])
    views = V.load_views(renders, ["cam_a", "cam_b"])
    assert list(views) == ["cam_a", "cam_b"]
    a = views["cam_a"]
    assert a.camera == "cam_a" and a.room_id == "r_L0_salon" and a.level_id == "L0"   # from the scene manifest
    assert a.size == (80, 60) and a.width == 80 and a.height == 60
    assert a.png == (renders / "cam_a.png").resolve() and a.png.is_absolute()
    assert a.index.name == "cam_a_index.png" and a.depth_mm.name == "cam_a_depth_mm.png"
    assert a.normal.name == "cam_a_normal.png"
    assert a.index_stats == {3: {"pixels": 200, "box": [10, 40, 30, 50]}, 2: {"pixels": 400, "box": [50, 18, 70, 38]}}
    assert a.exposure == {"mode": "auto", "ev": 1.5} and a.hidden == () and a.render_key == "0123456789abcdef"
    assert a.entry["camera"] == "cam_a"
    b = views["cam_b"]
    assert b.level_id == "L9" and b.hidden == ("f_1",) and b.plugged == ("win_1",)
    assert hash(a) != hash(b) and {a, b}                        # usable in sets
    with pytest.raises(AttributeError):
        a.camera = "x"                                            # frozen
    # The readers through the view.
    assert a.read_rgb().shape == (60, 80, 3) and a.read_index().max() == 99
    assert a.read_depth_mm()[0, 0] == 3000 and V.normal_hit(a.read_normal()).sum() == 60 * 80 - 30
    stats = V.compute_index_stats(a.read_index())
    assert stats[3] == a.index_stats[3] and stats[2] == a.index_stats[2]
    # Stale entries raise (all cameras) or are skipped with a warning.
    with pytest.raises(V.StaleRender) as err:
        V.load_views(renders)
    assert err.value.camera == "cam_old" and err.value.missing == ["render_key"]
    with pytest.raises(V.StaleRender) as err:
        V.load_views(renders, "cam_c")
    assert err.value.missing == ["files.normal"]
    warnings = []
    views = V.load_views(renders, skip_stale=True, warnings=warnings)
    assert list(views) == ["cam_a", "cam_b"] and len(warnings) == 2 and "cam_old" in warnings[0]
    with pytest.raises(KeyError):
        V.load_views(renders, ["cam_zz"])


def test_load_views_controls_layout_finds_the_scene_manifest(tmp_path):
    out = tmp_path / "toy"
    write_render_dir(out, [m5_entry("cam_a", "r_L0_salon")])
    hide = out / "controls" / "hide_f_1"
    hide.mkdir(parents=True)
    entry = m5_entry("cam_a", "r_L0_salon", hidden=["f_1"])
    (hide / "render_manifest.json").write_text(json.dumps({"renders": [entry]}), encoding="utf-8")
    view = V.load_views(hide)["cam_a"]
    assert view.level_id == "L0" and view.hidden == ("f_1",) and view.png.parent == hide.resolve()


def _rewrite_manifest(render_dir: Path, **fields) -> dict:
    path = render_dir / "render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update(fields)
    path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def test_load_views_skips_older_build_entries_of_a_deadline_cut_render(tmp_path):
    # Review L2 (b): a render cut by WENART_DEADLINE kept the entries of the cameras it did not render, also
    # when they were rendered from another scene build (M5, or a camera since moved), and load_views returned
    # them as views of the current scene. A manifest written before the render.py fix still holds them.
    old = m5_entry("cam_old", "r_L0_salon", scene_sha256="m5" * 32)
    same = m5_entry("cam_same", "r_L0_hol", scene_sha256="now" * 16)
    kept = m5_entry("cam_kept", "r_L0_hol", scene_sha256="m5" * 32)          # not cut: a --cameras subset run
    renders = write_render_dir(tmp_path / "toy", [old, same, kept])
    manifest = _rewrite_manifest(renders, scene_sha256="now" * 16, incomplete=True,
                                 not_rendered=["cam_old", "cam_same"])
    warnings = []
    views = V.load_views(renders, skip_stale=True, warnings=warnings)
    assert list(views) == ["cam_same", "cam_kept"]
    assert len(warnings) == 1 and "cam_old" in warnings[0] and "deadline" in warnings[0]
    with pytest.raises(V.StaleRender) as err:
        V.load_views(renders, "cam_old")
    assert err.value.missing == ["scene_sha256"] and "another scene build" in str(err.value)
    assert V.deadline_stale(old, manifest) and V.deadline_stale(same, manifest) is None
    assert V.deadline_stale(kept, manifest) is None and V.deadline_stale(old, None) is None
    assert V.view_from_entry(old, renders).camera == "cam_old"               # without the manifest: no check


def test_dropped_stale_items_are_never_views(tmp_path):
    # Cameras that left the scene (the M6 camera search dropped some M5 cameras): render.py moves their
    # entries to dropped_stale and keeps their files. Every reader takes views from `renders` only.
    renders = write_render_dir(tmp_path / "toy", [m5_entry("cam_a", "r_L0_salon"), m5_entry("cam_gone", "r_L0_hol")])
    manifest = json.loads((renders / "render_manifest.json").read_text(encoding="utf-8"))
    gone = manifest["renders"].pop()
    _rewrite_manifest(renders, renders=manifest["renders"], dropped_stale=[
        {"camera": "cam_gone", "reason": "no such camera in the scene", "scene_sha256": "x",
         "render_key": gone["render_key"], "files": sorted(p.name for p in renders.glob("cam_gone*"))}])
    assert (renders / "cam_gone.png").is_file()                              # its files stay
    assert list(V.load_views(renders)) == ["cam_a"]
    with pytest.raises(KeyError):
        V.load_views(renders, ["cam_gone"])
    # The other readers of render_manifest.json: the realism control views and the final report's inputs.
    from wenart.vision_check import realism
    rm = json.loads((renders / "render_manifest.json").read_text(encoding="utf-8"))
    assert realism.control_views(rm, hand_made_manifest()) == ["cam_a"]
    from test_report import make_project
    from wenart.report import final
    out = make_project(tmp_path / "report")
    path = out / "renders" / "render_manifest.json"
    rm = json.loads(path.read_text(encoding="utf-8"))
    rm["dropped_stale"] = [{"camera": "cam_gone_1", "reason": "no such camera in the scene", "files": []}]
    path.write_text(json.dumps(rm), encoding="utf-8")
    inp = final.load_inputs(out)
    assert inp.entries and "cam_gone_1" not in inp.entries


def test_view_from_entry_rejects_pre_m5_entries():
    # An M4 render entry: an M5 entry without the fields Milestone 5 added (the committed results now hold
    # M5 manifests, so the pre-M5 shape is built here).
    pre_m5 = {k: v for k, v in m5_entry("cam_a", "r_L0_salon").items()
              if k not in ("render_key", "index_stats", "files")}
    with pytest.raises(V.StaleRender) as err:
        V.view_from_entry(pre_m5, RESULTS / "synthetic-01")
    assert set(err.value.missing) == {"render_key", "index_stats", "files.depth_mm", "files.normal"}
    empty_view = m5_entry("cam_e", "r", index_stats={})       # a view with no indexed object is not stale
    assert V.view_from_entry(empty_view, "/tmp").index_stats == {}


# --------------------------------------------------------------------------
# project_paths
# --------------------------------------------------------------------------

def test_project_paths_follow_the_scene_manifest(tmp_path):
    out = tmp_path / "outputs" / "toy"
    (out / "scene").mkdir(parents=True)
    building = {"project": {"id": "toy", "source_folder": "projects/synthetic-01"}}
    (out / "building_final.json").write_text(json.dumps(building), encoding="utf-8")
    scene = hand_made_manifest()
    scene["building"] = str(out / "building_final.json")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    paths = V.project_paths(out)
    assert paths["project"] == "toy" and paths["project_out"] == out.resolve()
    assert paths["scene_manifest"]["project"] == "toy"
    assert paths["scene_manifest_path"] == out.resolve() / "scene" / "scene_manifest.json"
    assert paths["building_path"] == (out / "building_final.json").resolve()
    assert paths["style_profile"] == {"walls": {"material": "plaster_white"}}
    assert paths["project_dir"] == ROOT / "projects" / "synthetic-01"
    assert paths["brief_path"] == ROOT / "projects" / "synthetic-01" / "brief.yaml"
    assert paths["render_dir"] == out.resolve() / "renders"
    assert paths["brief"] is None or "values" in paths["brief"]
    # Repo-relative building path that does not exist here: the project output's copy is used;
    # no source_folder: projects/<p>.
    scene["building"] = "outputs/toy/building_final.json"
    (out / "building_final.json").write_text(json.dumps({"project": {"id": "toy"}}), encoding="utf-8")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    paths = V.project_paths(out)
    assert paths["building_path"] == (out / "building_final.json").resolve()
    assert paths["project_dir"] == ROOT / "projects" / "toy"
