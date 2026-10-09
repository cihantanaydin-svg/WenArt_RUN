"""CPU tests of wenart.vision_check.expected (docs/milestone5.md §1.4, §5.1).

A toy room rendered by a numpy ray caster (tests/vc_toy.py) with the pinhole
of wenart/blender/cameras.py gives index, depth and normal maps whose
geometry is known: the projection is checked against a known camera, the
roles and visibility against hand-computed values, and the JSON cross-check
with a dropped, a moved and an unknown element.

Milestone 6 (docs/milestone6.md §1.3, §4.2): the projection and its inverse
with lens shift (round trip, principal point), the cross-check of a view
rendered with ``shift_y = -0.10`` (no misplaced element; the same render read
without the shift misplaces its openings) and the projection against
Blender's ``world_to_camera_view`` on cameras made by ``create_cameras``
(skipped without Blender).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import vc_toy as T
from wenart import views as V
from wenart.blender.cli import find_blender as cli_find_blender
from wenart.vision_check import expected as X

ROOT = Path(__file__).resolve().parents[1]
CFG = X.load_cfg()
CAM = T.CAMERA["name"]


def toy_expected(tmp_path, **kw) -> dict:
    out = T.write_toy_project(tmp_path, **kw)
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    return X.expected_view(view, scene, building)


def by_id(exp: dict) -> dict:
    return {e["wenart_id"]: e for e in exp["elements"]}


# --------------------------------------------------------------------------
# Import rule and camera maths
# --------------------------------------------------------------------------

def test_expected_imports_no_pil_cv2_torch_or_blender():
    code = ("import sys, wenart.vision_check.expected; "
            "print(','.join(m for m in ('PIL', 'cv2', 'torch', 'bpy', 'wenart.blender.shell') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


def test_camera_basis_is_a_look_at_with_world_up():
    f, r, u = X.camera_basis([0, 0, 1.4], [0, 5, 1.4])
    assert np.allclose(f, [0, 1, 0]) and np.allclose(r, [1, 0, 0]) and np.allclose(u, [0, 0, 1])
    f, r, u = X.camera_basis(T.CAMERA["position"], T.CAMERA["target"])
    assert abs(np.dot(f, r)) < 1e-12 and abs(np.dot(f, u)) < 1e-12 and u[2] > 0


@pytest.mark.parametrize("lens", [24.0, 18.0, 16.0])
def test_projection_against_a_known_camera(lens):
    # Milestone 8: the camera's own lens_mm (18 mm: f = 960 px, 16 mm: 853.3 px; m5 cameras 24 mm: 1280 px).
    cam = {"position": [0.0, 0.0, 1.4], "target": [0.0, 5.0, 1.4], "lens_mm": lens, "sensor_mm": 36.0}
    W, H = 1920, 1080
    fpx = lens / 36.0 * W
    assert X.focal_px(cam, W) == pytest.approx(fpx)
    pts = [(0.0, 4.0, 1.4), (1.0, 2.0, 1.4), (0.0, 2.0, 2.4), (-0.5, 1.0, 0.9)]
    uv, z = X.project_points(pts, cam, (W, H))
    assert np.allclose(z, [4.0, 2.0, 2.0, 1.0])
    assert np.allclose(uv[0], [960, 540])                           # straight ahead: the image centre
    assert np.allclose(uv[1], [960 + fpx * 0.5, 540])               # 1 m right at 2 m
    assert np.allclose(uv[2], [960, 540 - fpx * 0.5])               # 1 m up at 2 m (v grows downwards)
    assert np.allclose(uv[3], [960 - fpx * 0.5, 540 + fpx * 0.5])
    # The toy camera (tilted down) agrees with the test's own projection.
    p = (4.5, -0.1, 1.5)
    uv, _ = X.project_points([p], T.CAMERA, T.SIZE)
    assert np.allclose(uv[0], T.project_point(p))


def test_projection_with_lens_shift_moves_the_principal_point():
    """docs/milestone6.md §1.3: u = W/2 - shift_x W + f (d.r)/(d.f), v = H/2 + shift_y W - f (d.u)/(d.f)."""
    W, H = 1920, 1080
    fpx = 24.0 / 36.0 * W
    cam = {"position": [0.0, 0.0, 1.25], "target": [0.0, 5.0, 1.25], "lens_mm": 24.0, "sensor_mm": 36.0,
           "shift_x": 0.05, "shift_y": -0.10}
    pts = [(0.0, 4.0, 1.25), (1.0, 2.0, 1.25), (0.0, 2.0, 0.25)]
    uv, z = X.project_points(pts, cam, (W, H))
    assert np.allclose(z, [4.0, 2.0, 2.0])
    assert np.allclose(uv[0], [960 - 96, 540 - 192])                 # straight ahead: the shifted principal point
    assert np.allclose(uv[1], [960 - 96 + fpx * 0.5, 540 - 192])
    assert np.allclose(uv[2], [960 - 96, 540 - 192 + fpx * 0.5])
    # No shift keys (an M5 camera) and shift 0 give the same pixels.
    plain = {k: v for k, v in cam.items() if not k.startswith("shift")}
    assert np.array_equal(X.project_points(pts, plain, (W, H))[0],
                          X.project_points(pts, dict(plain, shift_x=0.0, shift_y=0.0), (W, H))[0])
    assert X.focal_px(cam, W) == X.focal_px(plain, W) == pytest.approx(fpx)


@pytest.mark.parametrize("shift", [(0.0, -0.10), (0.07, -0.10), (0.0, 0.0)])
def test_unproject_inverts_project_with_shift(shift):
    W, H = 320, 180
    cam = {"position": [1.0, 2.0, 1.25], "target": [4.0, 3.0, 0.9], "lens_mm": 24.0, "sensor_mm": 36.0,
           "shift_x": shift[0], "shift_y": shift[1]}
    rng = np.random.default_rng(5)
    rows, cols = rng.integers(0, H, 200), rng.integers(0, W, 200)
    depth = np.zeros((H, W))
    depth[rows, cols] = rng.uniform(0.5, 9.0, 200)
    world = X.unproject_pixels(rows, cols, depth, cam, (W, H))
    uv, z = X.project_points(world, cam, (W, H))
    assert np.allclose(uv[:, 0], cols + 0.5, atol=1e-6) and np.allclose(uv[:, 1], rows + 0.5, atol=1e-6)
    assert np.allclose(z, depth[rows, cols], atol=1e-9)
    # unproject(project(p)) = p for points that project onto pixel centres.
    again = X.unproject_pixels(np.floor(uv[:, 1]).astype(int), np.floor(uv[:, 0]).astype(int), depth, cam, (W, H))
    assert np.allclose(again, world, atol=1e-9)


def shifted_toy(tmp_path, shift_y: float = -0.10, record_shift: bool = True):
    """The toy project rendered by a camera with ``shift_y``: an unshifted render 2k rows taller
    (k = -shift_y W; the focal length depends on W only) cropped to rows 2k .. 2k + H, whose principal
    point then sits at H/2 + shift_y W. ``record_shift``: write the shift into the scene manifest camera."""
    out = T.write_toy_project(tmp_path)
    W, H = T.SIZE
    k = int(round(-shift_y * W))
    index, depth, normal = T.raycast(T.default_boxes(), T.default_openings(), (W, H + 2 * k))
    rows = slice(2 * k, 2 * k + H)
    entry = T.write_render(out / "renders", CAM, index[rows], depth[rows], normal[rows])
    T.write_manifest(out / "renders", [entry])
    scene_path = out / "scene" / "scene_manifest.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    if record_shift:
        scene["cameras"][0]["shift_y"] = shift_y
        scene_path.write_text(json.dumps(scene, indent=1), encoding="utf-8")
    view = V.load_views(out / "renders")[CAM]
    return X.expected_view(view, scene, T.toy_building())


def lens_toy(tmp_path, lens: float, record_lens: bool = True):
    """The toy project rendered through a ``lens`` mm camera (Milestone 8); ``record_lens``: write the lens into
    the scene manifest camera (else the manifest keeps the toy's 24 mm while the pixels are ``lens``)."""
    out = T.write_toy_project(tmp_path)
    camera = dict(T.CAMERA, lens_mm=lens)
    index, depth, normal = T.raycast(T.default_boxes(), T.default_openings(), T.SIZE, camera=camera)
    entry = T.write_render(out / "renders", CAM, index, depth, normal)
    T.write_manifest(out / "renders", [entry])
    scene_path = out / "scene" / "scene_manifest.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    if record_lens:
        scene["cameras"][0]["lens_mm"] = lens
        scene_path.write_text(json.dumps(scene, indent=1), encoding="utf-8")
    view = V.load_views(out / "renders")[CAM]
    return X.expected_view(view, scene, T.toy_building()), scene["cameras"][0]


@pytest.mark.parametrize("lens", [18.0, 16.0])
def test_expected_elements_of_a_wide_lens_view(tmp_path, lens):
    """Milestone 8: a view rendered through the 18 / 16 mm lens its scene camera records projects every
    element where the render has it (no misplaced, no missing element), and each piece's pixel box lies in its
    box projected through that lens; read with the old 24 mm the same render is misplaced."""
    exp, camera = lens_toy(tmp_path / "wide", lens)
    cc = exp["json_crosscheck"]
    assert cc["error"] is None and cc["misplaced"] == [] and cc["in_json_not_rendered"] == []
    in_view = {eid for eid, p in cc["projected"].items() if p["in_view"]}
    assert {"win_1", "d_1", "f_sofa", "f_table", "f_arm"} <= in_view
    by_id = {e["wenart_id"]: e for e in exp["elements"]}
    for fid in ("f_sofa", "f_table"):
        piece = next(f for f in T.toy_building()["furniture"] if f["id"] == fid)
        box3d = X.furniture_box3d(piece, {"elevation": 0.0}, T.PIECES[fid][5])
        hull = X.projected_hull(X.box_corners(box3d), camera, T.SIZE)
        x0, y0 = hull.min(axis=0)
        x1, y1 = hull.max(axis=0)
        bx0, by0, bx1, by1 = by_id[fid]["box_px"]
        assert bx0 >= x0 - 1.5 and by0 >= y0 - 1.5 and bx1 <= x1 + 1.5 and by1 <= y1 + 1.5, (fid, hull, by_id[fid])
        assert by_id[fid]["visibility"] is not None and by_id[fid]["visibility"] > 0.5, by_id[fid]
    wrong = lens_toy(tmp_path / "unrecorded", lens, record_lens=False)[0]["json_crosscheck"]
    assert wrong["misplaced"] or wrong["in_json_not_rendered"]


def test_crosscheck_of_a_shifted_view_reports_no_misplaced_element(tmp_path):
    exp = shifted_toy(tmp_path / "shifted")
    cc = exp["json_crosscheck"]
    assert cc["error"] is None and cc["misplaced"] == [] and cc["in_json_not_rendered"] == []
    in_view = {eid: p for eid, p in cc["projected"].items() if p["in_view"]}
    assert {"win_1", "d_1", "f_sofa"} <= set(in_view)
    assert all(p["outside_share"] == 0.0 for p in in_view.values()), in_view
    # The same render read as an unshifted view puts every pixel 0.10 W too high: the openings are misplaced.
    wrong = shifted_toy(tmp_path / "unrecorded", record_shift=False)["json_crosscheck"]
    assert {"win_1", "d_1"} <= {x["id"] for x in wrong["misplaced"]}


@pytest.mark.skipif(cli_find_blender() is None, reason="no Blender binary")
def test_projection_matches_blender_world_to_camera_view(tmp_path):
    """Cameras made by ``cameras.create_cameras`` (one with shift (0.07, -0.10), one M5 camera without
    shift) and Blender's ``world_to_camera_view``: within 0.01 px of ``project_points``."""
    W, H = 1920, 1080
    plans = [{"name": "cam_s_1", "room_id": "s", "level_id": "L0", "index": 1, "position": [1.0, 2.0, 1.25],
              "target": [2.0, 2.5, 1.25], "lens_mm": 24.0, "sensor_mm": 36.0, "resolution": [W, H],
              "shift_x": 0.07, "shift_y": -0.10},
             {"name": "cam_s_2", "room_id": "s", "level_id": "L0", "index": 2, "position": [1.0, 2.0, 1.25],
              "target": [2.0, 3.0, 1.25], "lens_mm": 24.0, "sensor_mm": 36.0, "resolution": [W, H],
              "shift_x": 0.0, "shift_y": -0.10},
             {"name": "cam_m_1", "room_id": "s", "level_id": "L0", "index": 1, "position": [0.0, 0.0, 1.4],
              "target": [3.0, 1.0, 1.3], "lens_mm": 24.0, "sensor_mm": 36.0, "resolution": [W, H]},
             # Milestone 8: the 18 mm and the 16 mm lens of searched cameras.
             {"name": "cam_s_3", "room_id": "s", "level_id": "L0", "index": 3, "position": [1.0, 2.0, 1.25],
              "target": [2.0, 3.0, 1.25], "lens_mm": 18.0, "sensor_mm": 36.0, "resolution": [W, H],
              "shift_x": 0.0, "shift_y": -0.10},
             {"name": "cam_n_1", "room_id": "n", "level_id": "L0", "index": 1, "position": [1.0, 2.0, 1.25],
              "target": [2.0, 2.5, 1.25], "lens_mm": 16.0, "sensor_mm": 36.0, "resolution": [W, H],
              "shift_x": 0.0, "shift_y": -0.10}]
    pts = [(3.0, 3.0, 0.2), (2.5, 1.0, 2.0), (4.0, 2.0, 1.25), (2.0, 4.0, 0.0), (0.2, 5.0, 2.4), (3.0, 0.5, 0.9)]
    src, out = tmp_path / "plans.json", tmp_path / "uv.json"
    src.write_text(json.dumps({"plans": plans, "points": pts}), encoding="utf-8")
    expr = (f"import sys, json; sys.path.insert(0, {str(ROOT)!r})\n"
            "import bpy\n"
            "from bpy_extras.object_utils import world_to_camera_view\n"
            "from mathutils import Vector\n"
            "from wenart.blender import cameras\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            "scene = bpy.context.scene\n"
            f"scene.render.resolution_x, scene.render.resolution_y = {W}, {H}\n"
            "scene.render.resolution_percentage = 100\n"
            "col = bpy.data.collections.new('c'); scene.collection.children.link(col)\n"
            f"data = json.load(open({str(src)!r}))\n"
            "objs = cameras.create_cameras(data['plans'], col, [])\n"
            "bpy.context.view_layer.update()\n"
            "res = {}\n"
            "for ob in objs:\n"
            "    res[ob.name] = []\n"
            "    for p in data['points']:\n"
            "        v = world_to_camera_view(scene, ob, Vector(p))\n"
            f"        res[ob.name].append([v.x * {W}, (1.0 - v.y) * {H}, v.z])\n"
            f"json.dump(res, open({str(out)!r}, 'w'))\n")
    proc = subprocess.run([cli_find_blender(), "-b", "--factory-startup", "--python-exit-code", "1",
                           "--python-expr", expr], capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    res = json.loads(out.read_text(encoding="utf-8"))
    for plan in plans:
        uv, z = X.project_points(pts, plan, (W, H))
        ref = np.array(res[plan["name"]])
        front = z > 0.1                                  # points on or behind the camera plane have no pixel
        assert front.sum() >= 4, plan["name"]
        assert np.abs(uv[front] - ref[front, :2]).max() < 0.01, plan["name"]
        assert np.allclose(z, ref[:, 2], atol=1e-5), plan["name"]


def test_box_corners_rotation_and_near_plane_clipping():
    c = X.box_corners({"center": [1, 2, 0.5], "size": [2, 1, 1], "rotation_deg": 90})
    assert np.allclose(sorted(set(np.round(c[:, 0], 6))), [0.5, 1.5])
    assert np.allclose(sorted(set(np.round(c[:, 1], 6))), [1, 3])
    cam = {"position": [0.0, 0.0, 1.0], "target": [0.0, 5.0, 1.0], "lens_mm": 24.0, "sensor_mm": 36.0}
    straddling = X.box_corners({"center": [0, 0, 1], "size": [1, 2, 1], "rotation_deg": 0})   # the camera is inside it
    hull = X.projected_hull(straddling, cam, (160, 90))
    assert hull is not None and np.isfinite(hull).all() and X.polygon_area(hull) > 160 * 90
    behind = X.box_corners({"center": [0, -3, 1], "size": [1, 1, 1], "rotation_deg": 0})
    assert X.projected_hull(behind, cam, (160, 90)) is None


def test_hull_clip_and_area_helpers():
    square = X.convex_hull([(0, 0), (10, 0), (10, 10), (0, 10), (5, 5)])
    assert len(square) == 4 and X.polygon_area(square) == pytest.approx(100.0)
    assert X.polygon_area(X.clip_to_rect(square, 5, 20)) == pytest.approx(50.0)
    assert X.polygon_area(X.clip_to_rect(square + 100, 5, 5)) == 0.0


# --------------------------------------------------------------------------
# Elements, roles, visibility
# --------------------------------------------------------------------------

def test_expected_view_lists_every_index_with_boxes_and_evidence(tmp_path):
    exp = toy_expected(tmp_path)
    assert exp["camera"] == CAM and exp["room_id"] == "r_salon" and exp["room_type"] == "living"
    assert exp["size"] == list(T.SIZE) and exp["level_id"] == "L0"
    els = exp["elements"]
    assert [e["pixels"] for e in els] == sorted((e["pixels"] for e in els), reverse=True)
    ids = by_id(exp)
    assert set(ids) == {"win_1", "d_1", "f_sofa", "f_table", "f_arm", "f_unk", "dec_plant"}
    sofa = ids["f_sofa"]
    assert sofa["kind"] == "furniture" and sofa["type"] == "sofa" and sofa["host_decor"] == ["cushion"]
    assert sofa["source"] == "from_documents" and sofa["evidence"][0]["layer"] == "MOBILYA"
    W, H = T.SIZE
    for e in els:
        assert e["area_frac"] == pytest.approx(e["pixels"] / (W * H), abs=1e-6)
        assert e["box_1000"] == V.box_to_1000(e["box_px"], W, H)
        x0, y0, x1, y1 = e["box_px"]
        assert e["touches_border"] == (x0 == 0 or y0 == 0 or x1 == W or y1 == H)
    # Proxies lose their prefix, are furniture and their type is not trusted.
    assert ids["f_unk"]["kind"] == "furniture" and ids["f_unk"]["type_unverified"]
    assert not sofa["type_unverified"]
    assert ids["dec_plant"]["kind"] == "decor"


def test_roles_follow_the_spec_rule(tmp_path):
    ids = by_id(toy_expected(tmp_path))
    assert ids["f_sofa"]["role"] == "required" and ids["win_1"]["role"] == "required"
    assert ids["d_1"]["role"] == "required" and ids["f_arm"]["role"] == "required"
    assert ids["dec_plant"]["area_frac"] < 0.002 and ids["dec_plant"]["role"] == "ignore"
    roles = CFG["roles"]
    assert X.role_of("furniture", True, 0.0019, None, roles) == "ignore"
    assert X.role_of("furniture", True, 0.03, 0.5, roles) == "required"          # big enough on its own
    # Run 1b calibration: furniture mostly out of the frame (visibility < 0.35) is optional however large
    # its pixel area, and so are doors and windows that touch the image border.
    assert X.role_of("furniture", True, 0.30, 0.01, roles) == "optional"
    assert X.role_of("furniture", True, 0.30, None, roles) == "required"         # visibility unknown
    assert X.role_of("door", True, 0.25, None, roles, touches_border=True) == "optional"
    assert X.role_of("window", True, 0.05, None, roles, touches_border=False) == "required"
    assert X.role_of("door", True, 0.25, None, {**roles, "border_openings_required": True},
                     touches_border=True) == "required"
    assert X.role_of("furniture", True, 0.02, 0.5, roles) == "required"          # 1 % + visible
    assert X.role_of("furniture", True, 0.02, None, roles) == "required"         # visibility unknown
    assert X.role_of("furniture", True, 0.02, 0.2, roles) == "optional"          # a sliver of a big piece
    assert X.role_of("window", True, 0.009, None, roles) == "optional"
    assert X.role_of("door", False, 0.2, 1.0, roles) == "optional"               # another room: never required
    assert X.role_of("decor", True, 0.2, 1.0, roles) == "optional"               # decor: never required


def test_visibility_in_frame_share_and_occlusion(tmp_path):
    ids = by_id(toy_expected(tmp_path))
    arm = ids["f_arm"]                             # cut by the left image edge
    assert arm["touches_border"] and arm["in_frame"] < 0.8 and arm["unoccluded"] == pytest.approx(1.0, abs=0.02)
    sofa = ids["f_sofa"]                           # fully in frame, the table hides part of it
    assert sofa["in_frame"] == pytest.approx(1.0) and 0.6 < sofa["unoccluded"] < 0.95
    assert sofa["visibility"] == pytest.approx(sofa["in_frame"] * sofa["unoccluded"], abs=1e-3)
    plant = ids["dec_plant"]                        # behind the armchair
    assert plant["in_frame"] == pytest.approx(1.0) and plant["unoccluded"] < 0.2
    assert ids["win_1"]["visibility"] is None and ids["d_1"]["visibility"] is None   # openings: None
    # The table is mostly below the frame: a big piece seen as a sliver.
    assert ids["f_table"]["in_frame"] < 0.35


def test_box_visibility_unit_cases():
    cam = {"position": [0.0, 0.0, 1.0], "target": [0.0, 5.0, 1.0], "lens_mm": 24.0, "sensor_mm": 36.0}
    box = {"center": [0.0, 3.0, 1.0], "size": [0.6, 0.6, 0.6], "rotation_deg": 0.0}
    full = X.box_visibility(box, cam, (160, 90), pixels=10**6)
    assert full["in_frame"] == pytest.approx(1.0) and full["unoccluded"] == 1.0
    half = X.box_visibility(box, cam, (160, 90), pixels=int(full["hull_px"] / 2))
    assert half["visibility"] == pytest.approx(0.5, abs=0.01)
    assert X.box_visibility(None, cam, (160, 90), 10) is None
    assert X.box_visibility(box, None, (160, 90), 10) is None


def test_own_room_of_openings_with_and_without_room_ids(tmp_path):
    m5 = by_id(toy_expected(tmp_path / "m5"))
    pre = by_id(toy_expected(tmp_path / "pre", m5=False))
    for ids in (m5, pre):
        assert ids["d_1"]["own_room"] and ids["win_1"]["own_room"] and ids["f_sofa"]["own_room"]
    assert m5["d_1"]["room_ids"] == ["r_salon", "r_hol"]
    # Pre-M5 manifests have no room_ids on openings: the rooms come from the building JSON.
    assert pre["d_1"]["room_ids"] == ["r_salon", "r_hol"] and pre["win_1"]["room_ids"] == ["r_salon"]
    # From the hall's side the window is not its own; the door is.
    rooms = X.opening_rooms(T.toy_building())
    assert rooms == {"d_1": ["r_salon", "r_hol"], "win_1": ["r_salon"]}


def test_other_room_elements_are_never_required(tmp_path):
    out = T.write_toy_project(tmp_path)
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    for obj in scene["objects"]:
        if obj.get("wenart_id") == "f_sofa" and obj["kind"] == "furniture":
            obj["room_id"] = "r_hol"
    scene["cameras"][0]["room_id"] = "r_salon"
    ids = by_id(X.expected_view(view, scene, building))
    assert not ids["f_sofa"]["own_room"] and ids["f_sofa"]["role"] == "optional"


# --------------------------------------------------------------------------
# JSON cross-check
# --------------------------------------------------------------------------

def test_crosscheck_is_clean_when_the_render_matches_the_json(tmp_path):
    cc = toy_expected(tmp_path)["json_crosscheck"]
    assert cc["error"] is None and cc["tested"] == 6           # 2 openings + 4 pieces (decor is not tested)
    assert cc["in_json_not_rendered"] == [] and cc["misplaced"] == [] and cc["rendered_not_in_json"] == []
    proj = cc["projected"]
    assert proj["win_1"]["visible_share"] > 0.9 and proj["f_sofa"]["in_view"]
    # The projected centre of the window lands on its rendered index box centre.
    ids = by_id(toy_expected(tmp_path / "again"))
    b = ids["win_1"]["box_px"]
    assert math.dist(proj["win_1"]["centre_px"], ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)) < 2.0


def test_crosscheck_finds_a_dropped_piece_and_a_dropped_door(tmp_path):
    cc = toy_expected(tmp_path / "a", drop=("f_arm",))["json_crosscheck"]
    assert [x["id"] for x in cc["in_json_not_rendered"]] == ["f_arm"]
    item = cc["in_json_not_rendered"][0]
    assert item["visible_share"] >= 0.35 and item["area_frac"] >= 0.01 and item["source"] == "added_by_ai"
    cc = toy_expected(tmp_path / "b", drop=("d_1",))["json_crosscheck"]
    assert [x["id"] for x in cc["in_json_not_rendered"]] == ["d_1"]          # an empty doorway is not a door


def test_crosscheck_skips_pieces_that_are_not_built(tmp_path):
    """Milestone 7 §3.3: a drawn symbol both AI passes call not furniture stays in the building with
    ``build: false`` and is not in the scene, so its absence from the render is not a mismatch."""
    out = T.write_toy_project(tmp_path, drop=("f_arm",))
    path = out / "building_final.json"
    building = json.loads(path.read_text(encoding="utf-8"))
    for piece in building["furniture"]:
        if piece["id"] == "f_arm":
            piece["build"] = False
    path.write_text(json.dumps(building), encoding="utf-8")
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    cc = X.expected_view(view, scene, building)["json_crosscheck"]
    assert cc["in_json_not_rendered"] == []


def test_crosscheck_skips_the_upper_end_of_a_stair_built_below(tmp_path):
    """Milestone 10: a top-level stair that is the drawn upper end of the stair below is listed in the scene
    manifest's ``furniture.not_built`` with ``arrives_from`` and not built; its absence is no mismatch. Any
    other piece missing from the render still is."""
    out = T.write_toy_project(tmp_path, drop=("f_arm",))
    path = out / "scene" / "scene_manifest.json"
    scene = json.loads(path.read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    view = V.load_views(out / "renders")[CAM]
    assert [x["id"] for x in X.expected_view(view, scene, building)["json_crosscheck"]["in_json_not_rendered"]] \
        == ["f_arm"]
    scene.setdefault("furniture", {}).setdefault("not_built", []).append(
        {"id": "f_arm", "type": "armchair", "reason": "arrives from f_x (L-1 -> L0)", "arrives_from": "f_x"})
    assert X.expected_view(view, scene, building)["json_crosscheck"]["in_json_not_rendered"] == []
    scene["furniture"]["not_built"][-1].pop("arrives_from")             # not built for another reason: still tested
    assert [x["id"] for x in X.expected_view(view, scene, building)["json_crosscheck"]["in_json_not_rendered"]] \
        == ["f_arm"]


def test_crosscheck_skips_what_a_control_render_hides_on_purpose(tmp_path):
    out = T.write_toy_project(tmp_path, controls=("f_arm",))
    hidden = V.load_views(out / "controls" / "hide_f_arm")[CAM]
    assert hidden.hidden == ("f_arm",) and hidden.level_id == "L0"
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    exp = X.expected_view(hidden, scene, T.toy_building())
    assert "f_arm" not in by_id(exp) and exp["json_crosscheck"]["in_json_not_rendered"] == []
    assert exp["hidden"] == ["f_arm"]


def test_crosscheck_finds_a_moved_piece(tmp_path):
    cc = toy_expected(tmp_path, shift={"f_sofa": (-0.9, 0.0)})["json_crosscheck"]
    assert [x["id"] for x in cc["misplaced"]] == ["f_sofa"] and cc["in_json_not_rendered"] == []
    item = cc["misplaced"][0]
    assert item["outside_share"] > CFG["crosscheck"]["misplaced_max_outside"] and item["outside_p90_m"] > 0.3


def bed_expected(tmp_path, *, head="near", shift=(0.0, 0.0), json_height=1.0, size=T.SIZE) -> dict:
    """The toy room plus a bed drawn at (1.6, 2.6), 1.6 x 2.0 m: a 0.5 m mattress and a 1.0 m headboard.

    The scene builds it 1.0 m high (manifest ``box3d``) and the render shows the mattress and the headboard
    (``head`` = the side towards the camera or away from it), moved by ``shift`` against the drawing;
    ``json_height`` is the library height the building JSON records (``asset.bbox_m``).
    """
    centre = (1.6, 2.6)
    box3d = {"center": [centre[0], centre[1], 0.5], "size": [1.6, 2.0, 1.0], "rotation_deg": 0.0}
    bed = {"name": "furn_f_bed", "wenart_id": "f_bed", "kind": "furniture", "type": "bed_double",
           "room_id": "r_salon", "level_id": "L0", "pass_index": 9, "source": "from_documents", "status": "verified",
           "evidence": T.EV, "center": box3d["center"], "size": box3d["size"], "rotation_deg": 0.0, "box3d": box3d}
    out = T.write_toy_project(tmp_path, size=size, extra_objects=[bed])
    boxes = T.default_boxes()
    cx, cy = centre[0] + shift[0], centre[1] + shift[1]
    boxes[9] = ((cx, cy), (1.6, 2.0), 0.5)                                      # mattress
    boxes[19] = ((cx, cy + (0.95 if head == "near" else -0.95)), (1.6, 0.1), 1.0)   # headboard (same index)
    index, depth, normal = T.raycast(boxes, T.default_openings(), size)
    index[index == 19] = 9
    T.write_manifest(out / "renders", [T.write_render(out / "renders", CAM, index, depth, normal)])
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    building["furniture"].append({
        "id": "f_bed", "level_id": "L0", "room_id": "r_salon", "type": "bed_double", "source": "from_documents",
        "footprint": {"center": list(centre), "size": [1.6, 2.0], "rotation_deg": 0.0}, "front_deg": 90.0,
        "height": json_height, "asset": {"method": "library", "bbox_m": [1.6, 2.0, json_height]},
        "status": "verified", "evidence": T.EV})
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    return X.expected_view(view, scene, building)["json_crosscheck"]


def test_crosscheck_misplaced_ignores_the_shape_and_height_of_a_piece_where_it_is_drawn(tmp_path):
    # A bed rendered exactly on its drawn footprint, headboard towards the camera: its bounding box has
    # air above the mattress, so the box centre and the index-box centre differ (0.066 W before the fix).
    for head in ("near", "far"):
        cc = bed_expected(tmp_path / head, head=head)
        assert cc["misplaced"] == [] and cc["in_json_not_rendered"] == [], head
        assert cc["projected"]["f_bed"]["outside_share"] == 0.0
    # The building JSON records a 1.5 m library asset but the scene built a 1.0 m piece (asset file
    # missing: parametric fallback). The cross-check uses the height the scene built, so the projected
    # shape is the same as with a matching JSON height and nothing is misplaced (0.14 W before the fix).
    tall = bed_expected(tmp_path / "tall", json_height=1.5)
    assert tall["misplaced"] == []
    assert tall["projected"]["f_bed"]["area_frac"] == bed_expected(tmp_path / "same")["projected"]["f_bed"]["area_frac"]


def test_crosscheck_misplaced_finds_a_piece_or_an_opening_off_its_drawing(tmp_path):
    for shift in ((0.4, 0.0), (0.0, -0.4)):           # sideways in the frame, away from the camera
        cc = bed_expected(tmp_path / f"bed{shift}", shift=shift)
        assert [x["id"] for x in cc["misplaced"]] == ["f_bed"], shift
        item = cc["misplaced"][0]
        assert item["kind"] == "furniture" and item["type"] == "bed_double" and item["source"] == "from_documents"
        assert item["outside_share"] > CFG["crosscheck"]["misplaced_max_outside"] and item["pixels"] > 100
    # The window is rendered where the toy builds it; the building JSON draws it 0.6 m further east.
    out = T.write_toy_project(tmp_path / "win")
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = T.toy_building()
    win = next(o for o in building["openings"] if o["id"] == "win_1")
    win["center"] = [win["center"][0] + 0.6, win["center"][1]]
    cc = X.expected_view(view, scene, building)["json_crosscheck"]
    assert [x["id"] for x in cc["misplaced"]] == ["win_1"] and cc["misplaced"][0]["kind"] == "window"
    # Unmoved, every rendered element lies inside its drawn shape.
    clean = X.expected_view(view, scene, T.toy_building())["json_crosscheck"]
    assert clean["misplaced"] == []
    assert all(p["outside_share"] == 0.0 for p in clean["projected"].values() if p["in_view"])


def test_crosscheck_finds_an_index_without_a_building_element(tmp_path):
    ghost = {"name": "furn_ghost", "wenart_id": "f_ghost", "kind": "furniture", "type": "desk", "room_id": "r_salon",
             "level_id": "L0", "pass_index": 9, "center": [2.0, 2.5, 0.375], "size": [0.6, 0.4, 0.75],
             "rotation_deg": 0.0, "source": "from_documents", "status": "verified", "evidence": []}
    exp = toy_expected(tmp_path, extra_objects=[ghost])
    cc = exp["json_crosscheck"]
    assert [(x["id"], x["index"]) for x in cc["rendered_not_in_json"]] == [("f_ghost", 9)]


def test_crosscheck_uses_the_build_defaults_for_openings():
    building = T.toy_building()
    level = building["levels"][0]
    win = next(o for o in building["openings"] if o["id"] == "win_1")
    shape = X.opening_shape(win, building, level)
    zs = shape["corners"][:, 2]
    assert zs.min() == pytest.approx(0.9) and zs.max() == pytest.approx(2.1)     # sill 0.90 + height 1.20
    assert np.allclose(shape["corners"][:, 1], -0.1)                              # on the wall centre line
    wide = dict(win, width=1.6)
    assert X.opening_shape(wide, building, level)["corners"][:, 2].max() == pytest.approx(2.3)   # 1.40 above 1.5 m
    door = next(o for o in building["openings"] if o["id"] == "d_1")
    dz = X.opening_shape(door, building, level)["corners"][:, 2]
    assert dz.min() == pytest.approx(0.0) and dz.max() == pytest.approx(2.1)
    piece = building["furniture"][0]
    box = X.furniture_box3d(piece, level)
    assert box["size"] == [2.0, 0.9, 0.85] and box["center"][2] == pytest.approx(0.425)


def test_crosscheck_reports_a_missing_depth_map_without_raising(tmp_path):
    out = T.write_toy_project(tmp_path)
    (out / "renders" / f"{CAM}_depth_mm.png").unlink()
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    exp = X.expected_view(view, scene, T.toy_building())
    assert "depth_mm unreadable" in exp["json_crosscheck"]["error"] and exp["elements"]


# --------------------------------------------------------------------------
# Project level
# --------------------------------------------------------------------------

def test_expected_views_is_pure_and_skips_stale_views(tmp_path):
    out = T.write_toy_project(tmp_path)
    manifest = json.loads((out / "renders" / "render_manifest.json").read_text(encoding="utf-8"))
    stale = dict(manifest["renders"][0], camera="cam_old")
    del stale["render_key"]
    manifest["renders"].append(stale)
    (out / "renders" / "render_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    before = sorted(p.relative_to(out) for p in out.rglob("*"))
    exp = X.expected_views(out)
    assert list(exp) == [CAM]
    assert sorted(p.relative_to(out) for p in out.rglob("*")) == before        # writes nothing
    exp2, warnings = X.collect_expected(out)
    assert list(exp2) == [CAM] and any("cam_old" in w for w in warnings)


def _fake_expected(room, n_required, n_optional=0):
    els = [{"role": "required", "pixels": 100 + i} for i in range(n_required)]
    els += [{"role": "optional", "pixels": 10} for _ in range(n_optional)]
    return {"room_id": room, "elements": els}


def test_sweep_views_most_required_one_per_room_ties_by_name():
    exp = {"cam_a_1": _fake_expected("a", 3), "cam_a_2": _fake_expected("a", 5), "cam_b_1": _fake_expected("b", 4),
           "cam_c_2": _fake_expected("c", 4), "cam_c_1": _fake_expected("c", 4, 9), "cam_d_1": _fake_expected("d", 1)}
    assert X.sweep_views(exp, 3) == ["cam_a_2", "cam_b_1", "cam_c_1"]
    assert X.sweep_views(exp, 10) == ["cam_a_2", "cam_b_1", "cam_c_1", "cam_d_1"]
    assert X.sweep_views({}, 4) == []


def test_largest_required():
    exp = {"elements": [{"wenart_id": "a", "role": "optional", "pixels": 900},
                        {"wenart_id": "b", "role": "required", "pixels": 300},
                        {"wenart_id": "c", "role": "required", "pixels": 500}]}
    assert X.largest_required(exp)["wenart_id"] == "c"
    assert X.largest_required({"elements": [{"role": "optional", "pixels": 1}]}) is None
    assert X.largest_required({}) is None
