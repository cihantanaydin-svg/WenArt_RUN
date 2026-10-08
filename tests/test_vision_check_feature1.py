"""CPU tests of Feature 1 downstream in the vision check (docs/milestone10.md §2.6, §2.8).

The checks read ``building_final.json``: a drawn piece the AI changed (``modified_by_ai``: its new type and size
are the expected ones), a piece it added to a furnished room (``completes_room``) and a type proposal are
expected as they stand, never a mismatch or an insertion. The expected elements carry what the AI did, the
combine labels a mismatch of such a piece as a render issue, the plan crop draws three colours (drawn as drawn
green, changed blue with the drawn outline dashed under it and the anchor marked, added orange), the controls
choose among the pieces as they stand, and a region page clips the DXF raster to its box.
"""
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import vc_ext_toy as E
import vc_toy as T
from wenart import views as V
from wenart.ingest import debug_image as DI
from wenart.vision_check import combine as CB
from wenart.vision_check import controls as CT
from wenart.vision_check import expected as X
from wenart.vision_check import plan_crop as PC
from wenart.vision_check import prompts as P
from wenart.vision_check.cli import main
from wenart.vision_check.project import Project

CAM = T.CAMERA["name"]
CFG = X.load_cfg()


def toy_with_feature1(tmp_path) -> Path:
    """The toy project whose final building says: the sofa was an armchair (modified_by_ai, same place), the
    added armchair completes the room, the unknown proxy got a type proposal."""
    out = T.write_toy_project(tmp_path)
    path = out / "building_final.json"
    b = json.loads(path.read_text(encoding="utf-8"))
    for f in b["furniture"]:
        if f["id"] == "f_sofa":
            f.update(modified_by_ai=True, drawn_type="armchair",
                     drawn_footprint={"center": [3.0, 0.55], "size": [0.9, 0.9], "rotation_deg": 0.0},
                     anchor={"kind": "centre", "point": [3.0, 0.55], "wall_id": None})
        if f["id"] == "f_arm":
            f.update(completes_room=True)
        if f["id"] == "f_unk":
            f.update(type_proposal=True, drawn_type="unknown")
    path.write_text(json.dumps(b, indent=1), encoding="utf-8")
    return out


def by_id(exp: dict) -> dict:
    return {e["wenart_id"]: e for e in exp["elements"]}


def test_expected_elements_carry_what_the_ai_did_to_a_piece(tmp_path):
    out = toy_with_feature1(tmp_path)
    exp = Project(out).expected(CAM)
    els = by_id(exp)
    sofa, arm, unk, table = els["f_sofa"], els["f_arm"], els["f_unk"], els["f_table"]
    assert (sofa["modified_by_ai"], sofa["drawn_type"], sofa["type"], sofa["source"]) == (
        True, "armchair", "sofa", "from_documents")                       # expected as it stands: a sofa
    assert arm["completes_room"] is True and arm["source"] == "added_by_ai" and not arm["modified_by_ai"]
    assert unk["type_proposal"] is True and unk["type_unverified"] is True
    assert (table["modified_by_ai"], table["completes_room"], table["type_proposal"], table["drawn_type"]) == (
        False, False, False, None)
    assert els["d_1"]["modified_by_ai"] is False and els["dec_plant"]["completes_room"] is False
    # The role logic is unchanged: a changed piece is judged like any other piece of its size.
    assert sofa["role"] == "required"


def test_the_json_crosscheck_uses_the_final_footprint_of_a_changed_piece(tmp_path):
    out = T.write_toy_project(tmp_path)
    path = out / "building_final.json"
    b = json.loads(path.read_text(encoding="utf-8"))
    sofa = next(f for f in b["furniture"] if f["id"] == "f_sofa")
    sofa["modified_by_ai"], sofa["drawn_type"] = True, "armchair"
    sofa["drawn_footprint"] = {"center": [3.0, 0.55], "size": [0.9, 0.9], "rotation_deg": 0.0}
    path.write_text(json.dumps(b), encoding="utf-8")
    cc = Project(out).expected(CAM)["json_crosscheck"]
    # The render has the 2.0 x 0.9 sofa of the final building where it stands: nothing is misplaced or missing.
    assert cc["misplaced"] == [] and cc["in_json_not_rendered"] == [] and cc["rendered_not_in_json"] == []


def test_check_items_and_a_mismatch_of_a_changed_piece_are_labelled(tmp_path):
    out = toy_with_feature1(tmp_path)
    project = Project(out)
    items = P.check_items(project.expected(CAM), None)
    sofa = next(i for i in items if i["wenart_id"] == "f_sofa")
    assert sofa["type"] == "sofa" and sofa["modified_by_ai"] and sofa["drawn_type"] == "armchair"
    assert next(i for i in items if i["wenart_id"] == "f_arm")["completes_room"] is True
    # A model that sees no sofa: both passes absent -> a mismatch, labelled as a render issue of a changed piece.
    clients = {}

    def factory(key, url):
        clients.setdefault(key, T.FakeClient(model=f"fake/{key}", truth={f"renders/{CAM}.png": {"door", "window",
                                                                                              "armchair"}}))
        return clients[key]

    for key in ("qwen", "glm"):
        assert main(["run", "--project-out", str(out), "--model-key", key, "--kinds", "cycles"],
                    client_factory=factory) == 0
    assert main(["combine", "--project-out", str(out), "--models", "qwen,glm", "--no-debug"]) == 0
    manifest = json.loads((out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    el = manifest["views"][CAM]["cycles"]["elements"]["f_sofa"]
    assert el["result"] == "missing" and el["modified_by_ai"] is True and el["drawn_type"] == "armchair"
    assert el["notes"] == ["modified_by_ai (drawn armchair): render/polish issue, not a document conflict"]
    arm = manifest["views"][CAM]["cycles"]["elements"]["f_arm"]
    assert arm["completes_room"] is True and arm["result"] == "ok" and "notes" not in arm
    assert manifest["drawn_check"]["checked"] >= 1                         # the drawn pieces ride in the manifest


def test_a_drawn_piece_the_ai_changed_is_a_control_like_any_other(tmp_path):
    out = toy_with_feature1(tmp_path)
    exp = {CAM: Project(out).expected(CAM)}
    sel = CT.select_controls(exp, CFG)
    furn = [c for c in sel["controls"] if c["id"] == "f_sofa"]
    # f_sofa is the first from_documents control, with what the AI did to it.
    assert furn and furn[0]["modified_by_ai"] is True and furn[0]["drawn_type"] == "armchair"
    assert furn[0]["completes_room"] is False and furn[0]["source"] == "from_documents"
    swaps = {s["id"]: s for s in sel["swaps"]}
    assert "f_sofa" in swaps and swaps["f_sofa"]["swap_to"] == "bed_double"


def test_exterior_views_are_never_control_cameras(tmp_path):
    exp = {"ext_1": {"view_kind": "exterior", "room_id": None, "elements": [
        {"kind": "window", "role": "required", "own_room": True, "touches_border": False, "area_frac": 0.9,
         "wenart_id": "w", "index": 1, "type": "window", "source": "from_documents"}]}}
    assert CT.select_controls(exp, CFG)["controls"] == []


# --------------------------------------------------------------------------
# The plan crop: three colours
# --------------------------------------------------------------------------

def plan_fixture(tmp_path):
    out = toy_with_feature1(tmp_path)
    project = Project(out)
    doc = project.building["documents"][0]
    page = doc["pages"][0]
    img = Image.new("RGB", (900, 1000), "white")
    # building (X, Y) -> pixel ((X + 1) * 100, (6 - Y) * 100) by the page's transform_to_building
    raster = DI.PageRaster(image=img, to_pixels=lambda p: (p[0], p[1]))
    exp = project.expected(CAM)
    image, mapping = PC.render_plan_crop(raster, page, project.room("r_salon"), T.CAMERA, exp["elements"],
                                         project.building)
    assert image is not None, mapping
    return project, image, mapping


def near(image, points, colour, radius=2) -> bool:
    """Any pixel of ``colour`` within ``radius`` px of one of ``points`` (crop pixels)."""
    arr = np.asarray(image)
    for x, y in points:
        x, y = int(round(x)), int(round(y))
        patch = arr[max(0, y - radius):y + radius + 1, max(0, x - radius):x + radius + 1].reshape(-1, 3)
        if any(tuple(p) == tuple(colour) for p in patch):
            return True
    return False


def edge_points(poly, mapping, n=24):
    pts = [mapping.to_crop(p) for p in poly]
    out = []
    for a, b in zip(pts, pts[1:] + pts[:1]):
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out


def test_the_plan_crop_draws_drawn_changed_and_added_pieces_in_three_colours(tmp_path):
    project, image, mapping = plan_fixture(tmp_path)
    b = project.building
    poly = {pid: PC.element_outline(pid, b)[0] for pid in ("f_table", "f_sofa", "f_arm")}
    assert near(image, edge_points(poly["f_table"], mapping), PC.COLOURS["from_documents"])        # drawn: green
    assert near(image, edge_points(poly["f_sofa"], mapping), PC.CHANGED_COLOUR)                    # changed: blue
    assert near(image, edge_points(poly["f_arm"], mapping), PC.COLOURS["added_by_ai"])             # added: orange
    drawn = PC.drawn_outline(next(f for f in b["furniture"] if f["id"] == "f_sofa"))
    assert drawn is not None
    assert near(image, edge_points(drawn, mapping), PC.COLOURS["from_documents"])                  # drawn outline, dashed
    # The anchor of the changed piece is marked (a black cross at its centre).
    cx, cy = mapping.to_crop((3.0, 0.55))
    assert near(image, [(cx, cy)], (0, 0, 0), radius=3)
    # The camera is purple, not the changed-piece blue.
    assert PC.CAMERA_COLOUR != PC.CHANGED_COLOUR


def test_piece_class_follows_status_then_the_ai_label_then_the_source():
    assert PC.piece_class({"status": "unverified", "modified_by_ai": True}, {}) == "unverified"
    assert PC.piece_class({"modified_by_ai": True}, {}) == "changed"
    assert PC.piece_class({}, {"modified_by_ai": True}) == "changed"
    assert PC.piece_class({"source": "added_by_ai"}, {}) == "added"
    assert PC.piece_class({}, {"source": "added_by_ai"}) == "added"
    assert PC.piece_class({}, {"source": "from_documents"}) == "drawn"
    assert PC.drawn_outline({"drawn_footprint": None}) is None


# --------------------------------------------------------------------------
# Regions of a multi-drawing sheet and exterior crops
# --------------------------------------------------------------------------

def test_a_region_page_clips_the_dxf_raster_to_its_box(monkeypatch, tmp_path):
    seen = {}

    def fake(path, width_px=2400, clip_box=None):
        seen["clip_box"] = clip_box
        return DI.PageRaster(image=Image.new("RGB", (10, 10), "white"), to_pixels=lambda p: p)

    monkeypatch.setattr(DI, "raster_from_dxf", fake)
    PC.load_raster({"format": "dxf", "file": "a.dxf"}, {"region_box": [0, 10, 500, 600], "region_id": "r3"},
                   tmp_path / "a.dxf")
    assert seen["clip_box"] == (0.0, 10.0, 500.0, 600.0)
    PC.load_raster({"format": "dwg", "file": "a.dwg"}, {"page": 1}, tmp_path / "a.dxf")
    assert seen["clip_box"] is None


def test_an_exterior_crop_frames_the_building_and_the_camera(tmp_path):
    out = E.write_ext_project(tmp_path)
    project = Project(out)
    exp = project.expected("ext_1")
    room = PC.exterior_room(project.building, exp, E.CAMERA)
    xs = [p[0] for p in room["polygon"]]
    ys = [p[1] for p in room["polygon"]]
    assert min(xs) == 0.0 and max(xs) == 16.0 and min(ys) == -10.0 and max(ys) == 6.0        # walls + the camera
    assert PC.exterior_level(project.building, exp) == "L0"
    assert PC.EXTERIOR_MARGIN_M > PC.MARGIN_M


def test_plan_crops_of_a_project_with_regions_and_an_exterior_view_without_a_page(tmp_path):
    out = E.write_ext_project(tmp_path)
    assert main(["plan-crops", "--project-out", str(out)]) == 0
    info = json.loads((out / "check" / "plan_crops.json").read_text(encoding="utf-8"))["views"]["ext_1"]
    assert info["plan"] is None and "no page with a transform for level L0" in info["reason"]
