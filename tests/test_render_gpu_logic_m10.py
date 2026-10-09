"""CPU tests of the Milestone 10 parts of the GPU render tests (tests/gpu/test_render.py), fixed after the
full run of pod F1 (real02, 9 Oct 2026, runs/20261009-062657-full).

The GPU test module is imported against hand-made outputs in tmp_path (``_gpu_test_module`` of
tests/test_blender_render.py) and its test functions are called directly. No Blender needed.

- Three views: the scene manifest's ``variant`` is the build's variant record (an object, schemas.py); the
  test takes its ``id`` (it passed the whole record to ``views.views_for``: KeyError on the pod) and checks
  that the record's stored ``views`` name the rooms ``views_for`` gives. Built on
  docs/examples/building_m10.example.json for the base and the alternative ``l-1b-acik-mutfak``.
- Depth: exterior views (sky by design) and an interior view of a room open to the sky (real02's roof
  terrace) pass with the depth values of the pod; an interior view nearer than 0.1 m, a closed room with
  sky-like coverage and an exterior view beyond the clip end still fail, and every bad view is listed.
- Index pass: the pod's one failing view, ``cam_r_L0_yatak_odasi_3`` without the library wardrobe
  ``f_L0_012`` in its index pass, replayed from the run's building_final.json (cut to that room), scene and
  render manifests: the model sees the wardrobe's fitted box only at the frame edge (1.2 cm inside the
  frustum), so it is allowed as "library box edge only"; it still fails when the wardrobe is parametric,
  built 5 cm off its footprint, or 5 cm larger per side.
"""
import copy
import json
from pathlib import Path

import pytest

from test_blender_render import _gpu_test_module
from wenart import views as V
from wenart.blender import camsearch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"


def _write_building(outputs: Path, name: str, building: dict) -> Path:
    path = outputs / name / "building_final.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(building), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Three views: the variant record of the scene manifest
# --------------------------------------------------------------------------

def _searched_scene(building: dict, variant: str, building_path: Path) -> tuple[dict, dict]:
    """``(scene, render)`` manifests of a search-policy build of ``variant``, as the M10 build writes them: one
    camera per view of every room ``views_for`` renders (``room_view_count``), the rooms without a view and the
    skipped ones (twins) in ``rooms_without_view``, one exterior view, and ``variant`` in the shape of
    ``build.variant_summary``."""
    record = V.variant_record(building, variant)
    plan = V.views_for(building, variant)
    rooms = {r["id"]: r for r in building["rooms"]}
    without = [w for lv in record["levels"] for w in camsearch.rooms_without_view(building, lv)]
    no_view = {w["room_id"] for w in without}
    cams = [{"name": f"cam_{rid}_{i}", "room_id": rid, "level_id": rooms[rid]["level_id"], "policy": "search",
             "kind": "interior"}
            for rid in plan["rooms"] if rid not in no_view
            for i in range(1, camsearch.room_view_count(rooms[rid], building) + 1)]
    cams.append({"name": "ext_1", "room_id": None, "level_id": None, "policy": "search", "kind": "exterior"})
    skipped = [dict(s, level_id=rooms[s["room_id"]]["level_id"]) for s in plan["skipped"]]
    scene = {"building": str(building_path), "levels": [{"id": lv} for lv in record["levels"]], "cameras": cams,
             "rooms_without_view": without + skipped,
             "variant": {"id": record["id"], "label": record.get("label"), "base": V.is_base_variant(record),
                         "levels": list(record["levels"]), "changes": record.get("changes") or [],
                         "rooms_changed": plan["rooms_changed"], "exterior_changed": plan["exterior_changed"],
                         "views": plan}}
    return scene, {"renders": [{"camera": c["name"]} for c in cams]}


@pytest.mark.parametrize("variant", ["base", "l-1b-acik-mutfak"])
def test_three_views_take_the_variant_id_of_the_scene_manifest(variant, tmp_path, monkeypatch, capsys):
    building = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    path = _write_building(tmp_path / "outputs", "example", building)
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    scene, render = _searched_scene(building, variant, path)
    assert isinstance(scene["variant"], dict) and len(scene["cameras"]) > 1
    gpu.test_every_room_has_three_views(("example", scene, render))
    assert "rooms with nothing to show" in capsys.readouterr().out
    # A manifest from before Milestone 10 has no variant record: the base.
    if variant == "base":
        gpu.test_every_room_has_three_views(("example", dict(scene, variant=None), render))


def test_three_views_still_fail_on_a_missing_room_or_a_wrong_variant_record(tmp_path, monkeypatch):
    building = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    path = _write_building(tmp_path / "outputs", "example", building)
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    # The cameras of a room the base renders are missing.
    scene, render = _searched_scene(building, "base", path)
    room = scene["cameras"][0]["room_id"]
    short = dict(scene, cameras=[c for c in scene["cameras"] if c["room_id"] != room])
    with pytest.raises(AssertionError, match=rf"rooms without a view \['{room}'\]"):
        gpu.test_every_room_has_three_views(("example", short, render))
    # The record's stored views name other rooms than views_for.
    scene, render = _searched_scene(building, "l-1b-acik-mutfak", path)
    wrong = copy.deepcopy(scene)
    wrong["variant"]["views"]["rooms"] = wrong["variant"]["views"]["rooms"][1:]
    with pytest.raises(AssertionError, match="views_for gives"):
        gpu.test_every_room_has_three_views(("example", wrong, render))
    # The scene of the alternative read as the base renders the wrong rooms.
    with pytest.raises(AssertionError):
        gpu.test_every_room_has_three_views(("example", dict(scene, variant=dict(scene["variant"], id="base")),
                                             render))


# --------------------------------------------------------------------------
# Depth: exterior views and rooms open to the sky
# --------------------------------------------------------------------------

# Depth statistics of the pod F1 renders (render_manifest.json of real02).
POD_DEPTH = {
    "cam_r_L0_banyo_1": ("r_L0_banyo", "interior", {"min": 0.4714, "max": 1.5, "mean": 1.119, "coverage": 1.0}),
    "cam_r_L1_teras_1": ("r_L1_teras", "interior",
                         {"min": 0.4642, "max": 38.9087, "mean": 1.9588, "coverage": 0.7854}),
    "ext_1": (None, "exterior", {"min": 6.5017, "max": 52.2357, "mean": 14.2855, "coverage": 0.6463}),
    "ext_5": (None, "exterior", {"min": 19.4006, "max": 74.704, "mean": 30.7639, "coverage": 0.8638}),
}
# real02's roof: the two terraces are its openings (building_final.json roof.openings, cut to the ids).
ROOF = {"type": "mansard", "openings": [{"id": "ro_001", "kind": "terrace", "room_id": "r_L1_teras"},
                                         {"id": "ro_002", "kind": "terrace", "room_id": "r_L1_teras_2"}]}


def _depth_project(outputs: Path, depths: dict, roof=ROOF) -> tuple:
    """``(name, scene, render)`` of views with the given ``{camera: (room_id, kind, depth)}`` and their files."""
    name = "real02"
    out = outputs / name / "renders"
    out.mkdir(parents=True)
    path = _write_building(outputs, name, {"rooms": [], "roof": roof})
    cams, renders = [], []
    for cam, (room_id, kind, depth) in depths.items():
        cams.append({"name": cam, "room_id": room_id, "kind": kind, "policy": "search"})
        entry = {"camera": cam, "room_id": room_id, "png": f"{cam}.png", "exr": f"{cam}_passes.exr",
                 "preview": f"{cam}_preview.jpg", "depth": dict(depth)}
        for key in ("png", "exr", "preview"):
            (out / entry[key]).write_bytes(b"x" * 64)
        renders.append(entry)
    return name, {"building": str(path), "cameras": cams}, {"renders": renders}


def test_exterior_and_open_sky_views_pass_with_the_pod_depths(tmp_path, monkeypatch, capsys):
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    gpu.test_passes_exist_and_depth_is_plausible(_depth_project(tmp_path / "outputs", POD_DEPTH))
    assert "('cam_r_L1_teras_1', 0.785)" in capsys.readouterr().out


@pytest.mark.parametrize("camera, depth, why", [
    # The stair-core view of pod F1: an interior view nearer than 0.1 m.
    ("cam_r_L0_banyo_1", {"min": 0.08, "max": 1.69, "coverage": 1.0}, "0.1 < min < max < 60"),
    # A closed room (no roof opening) keeps the coverage bound.
    ("cam_r_L0_banyo_1", {"min": 0.47, "max": 38.9, "coverage": 0.785}, "coverage not over 0.9"),
    # The open-sky room keeps the interior depth range.
    ("cam_r_L1_teras_1", {"min": 0.08, "max": 38.9, "coverage": 0.785}, "0.1 < min < max < 60"),
    ("cam_r_L1_teras_1", {"min": 0.46, "max": 74.7, "coverage": 0.785}, "0.1 < min < max < 60"),
    # Exterior views: within the clip end, not mostly sky.
    ("ext_5", {"min": 19.4, "max": 600.0, "coverage": 0.864}, "0.1 < min < max < 500"),
    ("ext_1", {"min": 0.08, "max": 52.2, "coverage": 0.646}, "0.1 < min < max < 500"),
    ("ext_1", {"min": 6.5, "max": 52.2, "coverage": 0.2}, "coverage not over 0.25"),
])
def test_implausible_depths_still_fail(camera, depth, why, tmp_path, monkeypatch):
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    depths = dict(POD_DEPTH)
    depths[camera] = depths[camera][:2] + (depth,)
    with pytest.raises(AssertionError, match=why) as err:
        gpu.test_passes_exist_and_depth_is_plausible(_depth_project(tmp_path / "outputs", depths))
    assert camera in str(err.value)


def test_every_bad_view_is_listed(tmp_path, monkeypatch):
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    depths = dict(POD_DEPTH)
    depths["cam_r_L0_oda_2"] = ("r_L0_oda", "interior", {"min": 0.0824, "max": 1.6909, "coverage": 1.0})
    depths["cam_r_L0_oda_2_1"] = ("r_L0_oda", "interior", {"min": 0.0699, "max": 1.335, "coverage": 1.0})
    project = _depth_project(tmp_path / "outputs", depths)
    (tmp_path / "outputs" / "real02" / "renders" / "ext_1_passes.exr").unlink()
    with pytest.raises(AssertionError) as err:
        gpu.test_passes_exist_and_depth_is_plausible(project)
    text = str(err.value)
    assert all(cam in text for cam in ("cam_r_L0_oda_2'", "cam_r_L0_oda_2_1", "ext_1_passes.exr")), text
    assert "cam_r_L1_teras_1" not in text and "ext_5" not in text


def test_without_a_roof_opening_the_terrace_is_a_closed_room(tmp_path, monkeypatch):
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    with pytest.raises(AssertionError, match="cam_r_L1_teras_1"):
        gpu.test_passes_exist_and_depth_is_plausible(_depth_project(tmp_path / "outputs", POD_DEPTH, roof=None))


# --------------------------------------------------------------------------
# Index pass: the real02 wardrobe seen only at the edge of its fitted box
# --------------------------------------------------------------------------

# runs/20261009-062657-full/results/furniture/real02/building_final.json cut to r_L0_yatak_odasi: level L0, the
# room, its two openings and their walls, its six pieces (shown_pieces; asset reduced to method and bbox_m).
# camsearch.model_shares of this cut equals that of the whole building for the camera below.
REAL02_BEDROOM = {
    "project": {"id": "real02"}, "status": "ok",
    "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 3.0}],
    "walls": [{"id": "w_L0_001", "level_id": "L0", "start": [0.0, 1.6], "end": [15.172, 1.6], "thickness": 0.2},
              {"id": "w_L0_010", "level_id": "L0", "start": [3.268, 0.0], "end": [3.268, 11.8], "thickness": 0.1}],
    "openings": [{"id": "d_L0_005", "type": "door", "level_id": "L0", "wall_id": "w_L0_010", "center": [3.268, 6.51],
                  "width": 0.824, "height": 2.1, "sill_height": None},
                 {"id": "win_L0_001", "type": "window", "level_id": "L0", "wall_id": "w_L0_001",
                  "center": [1.7419, 1.6], "width": 2.6831, "height": 1.2, "sill_height": 0.9}],
    "rooms": [{"id": "r_L0_yatak_odasi", "level_id": "L0", "label": "Yatak Odası",
               "polygon": [[0.2, 1.7], [3.218, 1.7], [3.218, 7.044], [0.2, 7.044]]}],
    "furniture": [
        {"id": "f_L0_012", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "wardrobe",
         "source": "from_documents", "footprint": {"center": [0.9273, 6.7436], "size": [1.4533, 0.6],
                                                    "rotation_deg": 0.0},
         "front_deg": None, "height": None, "asset": {"method": "library", "bbox_m": [1.4533, 0.6, 1.89]}},
        {"id": "f_L0_021", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "bed_double",
         "source": "from_documents", "footprint": {"center": [1.1506, 3.0087], "size": [1.55, 1.9],
                                                    "rotation_deg": 90.0},
         "front_deg": None, "height": None, "asset": {"method": "library", "bbox_m": [1.55, 1.9, 0.77]}},
        {"id": "f_L0_032", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "unknown",
         "source": "from_documents", "footprint": {"center": [0.654, 5.0636], "size": [1.4471, 0.9068],
                                                    "rotation_deg": 90.0},
         "front_deg": 0.0, "height": None, "asset": {"method": "parametric", "bbox_m": [1.4471, 0.9068, 0.8]}},
        {"id": "f_L0_041", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "nightstand",
         "source": "added_by_ai", "footprint": {"center": [0.421, 4.08], "size": [0.5, 0.4], "rotation_deg": 90.0},
         "front_deg": 0.0, "height": 0.5, "asset": {"method": "library", "bbox_m": [0.5, 0.4, 0.4235]}},
        {"id": "f_L0_042", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "nightstand",
         "source": "added_by_ai", "footprint": {"center": [0.421, 1.98], "size": [0.5, 0.4], "rotation_deg": 90.0},
         "front_deg": 0.0, "height": 0.5, "asset": {"method": "library", "bbox_m": [0.5, 0.4, 0.4235]}},
        {"id": "f_L0_043", "level_id": "L0", "room_id": "r_L0_yatak_odasi", "type": "bench",
         "source": "added_by_ai", "footprint": {"center": [2.35, 2.333], "size": [1.2, 0.4], "rotation_deg": 90.0},
         "front_deg": 0.0, "height": 0.45, "asset": {"method": "library", "bbox_m": [1.2, 0.4, 0.4769]}},
    ],
}
# scene_manifest.json: the camera plan (score and placement text left out), the room's furniture objects (box3d of
# the built meshes) and the pass indices of the room and of the view's index pass.
REAL02_CAMERA = {
    "name": "cam_r_L0_yatak_odasi_3", "room_id": "r_L0_yatak_odasi", "level_id": "L0", "index": 3,
    "position": [0.7, 6.2, 1.25], "target": [1.566025, 5.7, 1.25], "lens_mm": 18.0, "sensor_mm": 36.0,
    "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": -0.1, "policy": "search", "warning": None,
    "visible_openings": ["d_L0_005"], "visible_furniture": ["f_L0_012", "f_L0_021", "f_L0_032", "f_L0_043"],
    "kind": "interior", "variant": "base",
}
REAL02_OBJECTS = [
    {"name": "proxy_f_L0_032", "wenart_id": "proxy:f_L0_032", "kind": "furniture_proxy", "pass_index": 107,
     "box3d": {"center": [0.704, 5.0636, 0.4], "size": [1.4471, 1.0068, 0.8], "rotation_deg": 90.0}},
    {"name": "furn_f_L0_012", "wenart_id": "f_L0_012", "kind": "furniture", "pass_index": 117, "method": "library",
     "box3d": {"center": [0.9273, 6.7436, 0.945], "size": [1.4533, 0.6, 1.89], "rotation_deg": 0.0}},
    {"name": "furn_f_L0_021", "wenart_id": "f_L0_021", "kind": "furniture", "pass_index": 126, "method": "library",
     "box3d": {"center": [1.1506, 3.0087, 0.385], "size": [1.55, 1.9, 0.77], "rotation_deg": 90.0}},
    {"name": "furn_f_L0_041", "wenart_id": "f_L0_041", "kind": "furniture", "pass_index": 142, "method": "library",
     "box3d": {"center": [0.421, 4.08, 0.2117], "size": [0.5, 0.4, 0.4235], "rotation_deg": 90.0}},
    {"name": "furn_f_L0_042", "wenart_id": "f_L0_042", "kind": "furniture", "pass_index": 143, "method": "library",
     "box3d": {"center": [0.421, 1.98, 0.2117], "size": [0.5, 0.4, 0.4235], "rotation_deg": 90.0}},
    {"name": "furn_f_L0_043", "wenart_id": "f_L0_043", "kind": "furniture", "pass_index": 144, "method": "library",
     "box3d": {"center": [2.35, 2.333, 0.2385], "size": [1.2, 0.4, 0.4769], "rotation_deg": 90.0}},
]
REAL02_PASS_INDEX = {"d_L0_005": 92, "win_L0_001": 100, "proxy:f_L0_032": 107, "f_L0_012": 117, "f_L0_021": 126,
                     "f_L0_037": 138, "f_L0_041": 142, "f_L0_042": 143, "f_L0_043": 144, "dec_L0_005": 161,
                     "dec_L0_006": 162}
REAL02_INDEX_VALUES = [92, 100, 107, 126, 138, 144, 161, 162]        # render_manifest.json: no 117 (the wardrobe)


def _wardrobe(building: dict) -> dict:
    return next(f for f in building["furniture"] if f["id"] == "f_L0_012")


def _index_project(outputs: Path, building: dict, objects: list) -> tuple:
    path = _write_building(outputs, "real02", building)
    scene = {"building": str(path), "pass_index": REAL02_PASS_INDEX, "cameras": [REAL02_CAMERA], "objects": objects}
    render = {"renders": [{"camera": REAL02_CAMERA["name"], "index_values": REAL02_INDEX_VALUES}]}
    return "real02", scene, render


def test_the_real02_cut_reproduces_the_pod_model_shares():
    """The fixture is the pod's case: the model sees 0.0104 of the wardrobe's fitted box (two grid columns at the
    left border of 192 x 108 rays), none of it with the box 1 or 2 cm smaller per side."""
    shares = camsearch.model_shares(REAL02_BEDROOM, REAL02_CAMERA)
    assert shares["f_L0_012"] == pytest.approx(0.0104, abs=1e-4)
    assert shares["f_L0_021"] == pytest.approx(0.0491, abs=1e-4) and shares["f_L0_043"] < 0.005
    for slack in (0.01, 0.02):
        smaller = copy.deepcopy(REAL02_BEDROOM)
        box = _wardrobe(smaller)["asset"]["bbox_m"]
        box[0], box[1] = box[0] - 2 * slack, box[1] - 2 * slack
        got = camsearch.model_shares(smaller, REAL02_CAMERA)
        assert got.get("f_L0_012", 0.0) == 0.0 and got["d_L0_005"] > shares["d_L0_005"]   # the door behind it
        assert all(got[f] == shares[f] for f in ("f_L0_021", "f_L0_032", "f_L0_043"))


def test_the_real02_wardrobe_is_allowed_as_library_box_edge_only(tmp_path, monkeypatch, capsys):
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / "outputs", REAL02_BEDROOM,
                                                                    REAL02_OBJECTS))
    out = capsys.readouterr().out
    assert "library box edge only" in out and "('cam_r_L0_yatak_odasi_3', 'f_L0_012', 0.0104)" in out


def _parametric(building: dict, objects: list) -> None:
    _wardrobe(building)["asset"] = None


def _moved(building: dict, objects: list) -> None:
    box = next(o for o in objects if o["wenart_id"] == "f_L0_012")["box3d"]
    box["center"][0] += 0.05                                     # the mesh was built 5 cm off its footprint


def _wider(building: dict, objects: list) -> None:
    box = next(o for o in objects if o["wenart_id"] == "f_L0_012")["box3d"]
    for size in (_wardrobe(building)["asset"]["bbox_m"], box["size"]):   # 5 cm larger per side, built as fitted
        size[0] += 0.1
        size[1] += 0.1


@pytest.mark.parametrize("change", [_parametric, _moved, _wider], ids=["parametric", "moved_5cm", "wider"])
def test_the_strict_rule_still_holds_for_a_box_the_mesh_fills_or_a_misplaced_mesh(change, tmp_path, monkeypatch):
    building, objects = copy.deepcopy(REAL02_BEDROOM), copy.deepcopy(REAL02_OBJECTS)
    change(building, objects)
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    with pytest.raises(AssertionError, match=r"cam_r_L0_yatak_odasi_3', \['f_L0_012'\]"):
        gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / "outputs", building, objects))
