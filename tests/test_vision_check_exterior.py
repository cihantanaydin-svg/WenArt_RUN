"""CPU tests of the exterior views of the vision check (docs/milestone10.md §3.3 item 4).

A toy house (tests/vc_ext_toy.py: 8 x 6 m, a gable roof, two windows and a door in the south wall, one window in
the east wall) rendered by a numpy ray caster gives index, depth and normal maps whose geometry is known. The
expected elements, their roles (thresholds of ``check.yaml: roles_exterior``), the cross-check of the outer
openings and of the roof, the facades in view, the prompts and the advisory facade count are tested on it; the
scope of a variant on the Milestone 10 example building.
"""
import json
from pathlib import Path

import numpy as np
import pytest

import vc_ext_toy as E
import vc_toy as T
from wenart import views as V
from wenart.recognition.vlm_client import schema_errors
from wenart.vision_check import calls as C
from wenart.vision_check import combine as CB
from wenart.vision_check import exterior as EXT
from wenart.vision_check import expected as X
from wenart.vision_check import prompts as P
from wenart.vision_check import schemas as S
from wenart.vision_check.project import Project

ROOT = Path(__file__).resolve().parents[1]
CAM = E.CAMERA["name"]
CFG = X.load_cfg()


def ext_expected(tmp_path, **kw) -> dict:
    out = E.write_ext_project(tmp_path, **kw)
    view = V.load_views(out / "renders")[CAM]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    return X.expected_view(view, scene, building)


def by_id(exp: dict) -> dict:
    return {e["wenart_id"]: e for e in exp["elements"]}


# --------------------------------------------------------------------------
# Expected elements
# --------------------------------------------------------------------------

def test_an_exterior_camera_is_recognised_by_its_kind_or_its_name():
    assert EXT.is_exterior({"kind": "exterior", "name": "ext_1"})
    assert not EXT.is_exterior({"kind": "interior", "name": "ext_9", "room_id": "r"})
    assert EXT.is_exterior({"name": "ext_2", "room_id": None})
    assert not EXT.is_exterior({"name": "cam_r_salon_1", "room_id": "r_salon"})
    assert not EXT.is_exterior(None, type("V", (), {"camera": "cam_r_1", "room_id": "r"})())


def test_the_expected_elements_of_an_exterior_view_are_the_outer_openings(tmp_path):
    exp = ext_expected(tmp_path)
    assert exp["view_kind"] == "exterior" and exp["room_id"] is None and exp["level_id"] is None
    els = by_id(exp)
    assert set(els) == {"win_s1", "d_s1", "win_s2", "win_e1"}
    assert all(e["own_room"] for e in els.values())                       # an outer opening of the variant
    assert {k: e["side"] for k, e in els.items()} == {"win_s1": "south", "d_s1": "south", "win_s2": "south",
                                                       "win_e1": "east"}
    roles = {k: e["role"] for k, e in els.items()}
    assert roles["d_s1"] == "required" and roles["win_s2"] == "required"   # thresholds of roles_exterior
    assert all(r in ("required", "optional") for r in roles.values())
    assert all(not e["modified_by_ai"] and not e["completes_room"] for e in els.values())
    assert exp["warnings"] == []


def test_the_interior_thresholds_would_have_ignored_every_window_of_the_house(tmp_path):
    exp = ext_expected(tmp_path)
    interior = CFG["roles"]
    for e in exp["elements"]:
        assert e["area_frac"] < float(interior["required_area_frac"])
        assert X.role_of(e["kind"], True, e["area_frac"], None, interior) != "required"


def test_furniture_seen_through_a_window_is_ignored_in_an_exterior_view(tmp_path):
    out = E.write_ext_project(tmp_path)
    index = V.read_index(out / "renders" / f"{CAM}_index.png").copy()
    index[60:100, 120:160] = 9
    depth = V.read_depth_mm(out / "renders" / f"{CAM}_depth_mm.png")
    normal = V.read_normal(out / "renders" / f"{CAM}_normal.png")
    entry = T.write_render(out / "renders", CAM, index, depth, normal)
    entry.update(room_id=None, level_id=None)
    T.write_manifest(out / "renders", [entry])
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    scene["objects"].append({"name": "furn_f_1", "wenart_id": "f_1", "kind": "furniture", "status": "verified",
                             "level_id": "L0", "element_id": "f_1", "room_id": "r_salon", "type": "sofa",
                             "source": "from_documents", "evidence": E.EV, "pass_index": 9,
                             "box3d": {"center": [4, 3, 0.4], "size": [2, 1, 0.8], "rotation_deg": 0}})
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    view = V.load_views(out / "renders")[CAM]
    exp = X.expected_view(view, scene, building)
    assert by_id(exp)["f_1"]["role"] == "ignore"
    # ... and it is a known id: not "rendered, not in the JSON" (the building has no f_1: it is listed, as in a room).
    assert [i["id"] for i in exp["json_crosscheck"]["rendered_not_in_json"]] == ["f_1"]


def test_whole_building_objects_are_never_rendered_not_in_json(tmp_path):
    out = E.write_ext_project(tmp_path)
    index = V.read_index(out / "renders" / f"{CAM}_index.png").copy()
    index[10:20, 10:20] = 20
    entry = T.write_render(out / "renders", CAM, index, V.read_depth_mm(out / "renders" / f"{CAM}_depth_mm.png"),
                           V.read_normal(out / "renders" / f"{CAM}_normal.png"))
    entry.update(room_id=None, level_id=None)
    T.write_manifest(out / "renders", [entry])
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    scene["objects"].append({"name": "sl", "wenart_id": "sl_L0", "kind": "slab", "status": "verified",
                             "level_id": "L0", "evidence": E.EV, "pass_index": 20})
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    exp = X.expected_view(V.load_views(out / "renders")[CAM], scene, building)
    assert exp["json_crosscheck"]["rendered_not_in_json"] == []
    assert by_id(exp)["sl_L0"]["kind"] == "slab" and by_id(exp)["sl_L0"]["role"] == "optional"


# --------------------------------------------------------------------------
# Cross-check, roof, facades
# --------------------------------------------------------------------------

def test_the_crosscheck_of_a_clean_exterior_render_finds_nothing(tmp_path):
    exp = ext_expected(tmp_path)
    cc = exp["json_crosscheck"]
    assert cc["error"] is None and cc["tested"] == 4
    assert cc["in_json_not_rendered"] == [] and cc["misplaced"] == [] and cc["rendered_not_in_json"] == []
    assert cc["roof_not_rendered"] == []
    assert set(cc["projected"]) == {"win_s1", "d_s1", "win_s2", "win_e1"}
    roof = exp["exterior"]["roof"]
    assert roof["result"] == "ok" and roof["present_share"] > 0.9 and roof["planes"] == 2


def test_a_window_the_render_left_out_is_in_json_not_rendered(tmp_path):
    exp = ext_expected(tmp_path, drop=("win_s2",))
    assert [i["id"] for i in exp["json_crosscheck"]["in_json_not_rendered"]] == ["win_s2"]
    assert "win_s2" not in by_id(exp)


def test_a_roof_the_render_left_out_is_found_missing(tmp_path):
    exp = ext_expected(tmp_path, roof=False)
    roof = exp["exterior"]["roof"]
    assert roof["result"] == "missing" and roof["present_share"] < 0.2 and roof["expected"] is True
    assert [i["id"] for i in exp["json_crosscheck"]["roof_not_rendered"]] == ["roof"]
    assert CB.review_reasons(None, exp["json_crosscheck"]) == ["json cross-check roof_not_rendered: roof"]


def test_a_building_without_a_roof_has_no_roof_check(tmp_path):
    out = E.write_ext_project(tmp_path)
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    building["roof"] = None
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    exp = X.expected_view(V.load_views(out / "renders")[CAM], scene, building)
    assert exp["exterior"]["roof"]["result"] == "not_checked"
    assert "flat roof" in exp["exterior"]["roof"]["note"]


def test_the_roof_planes_are_derived_when_the_building_has_none(tmp_path):
    out = E.write_ext_project(tmp_path)
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    building["roof"]["planes"] = []
    building["roof"]["outline"] = [[-0.5, -0.5], [8.5, -0.5], [8.5, 6.5], [-0.5, 6.5]]
    building["roof"]["ridge_lines"] = [[[-0.5, 3.0], [8.5, 3.0]]]
    building["roof"]["pitches_deg"] = [{"value": 26.565, "method": "vector", "confidence": 1.0, "evidence": E.EV}]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    exp = X.expected_view(V.load_views(out / "renders")[CAM], scene, building)
    assert exp["exterior"]["roof"]["planes_source"] == "derived" and exp["exterior"]["roof"]["planes"] >= 2


def test_the_facades_in_view_with_their_openings(tmp_path):
    exp = ext_expected(tmp_path)
    facades = {f["side"]: f for f in exp["exterior"]["facades"]}
    assert set(facades) == {"south", "east"}
    south = facades["south"]
    assert south["windows"] + south["partial_windows"] == 2 and south["doors"] + south["partial_doors"] == 1
    assert sorted(south["ids"]) == ["d_s1", "win_s1", "win_s2"]
    x0, y0, x1, y1 = south["box_px"]
    assert 0 <= x0 < x1 <= 320 and 0 <= y0 < y1 <= 180 and south["area_frac"] > 0.05
    assert exp["exterior"]["planned_not_seen"] == [] or set(exp["exterior"]["planned_not_seen"]) <= {"win_e1"}
    assert exp["exterior"]["variant"] == "base" and exp["exterior"]["view"] == "corner"


def test_the_facade_box_of_a_back_face_is_not_listed(tmp_path):
    out = E.write_ext_project(tmp_path)
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    sc = EXT.scope(E.CAMERA, {}, building)
    boxes = EXT.facade_boxes(E.CAMERA, E.SIZE, sc)
    assert set(boxes) == {"south", "east"}                              # the north and west faces turn away


# --------------------------------------------------------------------------
# Scope of a variant (the Milestone 10 example building)
# --------------------------------------------------------------------------

def example() -> dict:
    return json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def test_the_scope_of_a_variant_holds_only_its_levels():
    b = example()
    base = EXT.scope({"variant": "base"}, {}, b)
    alt = EXT.scope({"variant": "l-1b-acik-mutfak"}, {}, b)
    assert base["level_ids"] == ["L-1", "L0", "L1"] and alt["level_ids"] == ["L-1b", "L0", "L1"]
    assert base["variant"] == "base" and alt["variant"] == "l-1b-acik-mutfak"
    levels = {o["level_id"] for o in alt["openings"].values()}
    assert levels and levels <= set(alt["level_ids"])
    assert all(o["side"] in ("north", "east", "south", "west") for o in alt["openings"].values())
    # The scene manifest names the variant when the camera does not.
    again = EXT.scope({}, {"variant": {"id": "l-1b-acik-mutfak"}}, b)
    assert again["level_ids"] == alt["level_ids"]


def test_an_unknown_variant_falls_back_to_the_whole_building_with_a_warning():
    sc = EXT.scope({"variant": "nope"}, {}, example())
    assert sc["warnings"] and "nope" in sc["warnings"][0]


# --------------------------------------------------------------------------
# Sweep views
# --------------------------------------------------------------------------

def test_sweep_views_leave_out_exterior_views_and_sweep_exterior_picks_each_kind():
    def el(n):
        return {"elements": [{"role": "required"}] * n}
    ev = {"cam_a_1": dict(el(3), room_id="a"), "cam_b_1": dict(el(2), room_id="b"),
          "ext_1": dict(el(5), view_kind="exterior", exterior={"view": "corner"}),
          "ext_2": dict(el(4), view_kind="exterior", exterior={"view": "corner"}),
          "ext_5": dict(el(1), view_kind="exterior", exterior={"view": "aerial"})}
    assert X.sweep_views(ev, 8) == ["cam_a_1", "cam_b_1"]
    assert X.sweep_exterior_views(ev, 2) == ["ext_1", "ext_5"]            # a new view kind first
    assert X.sweep_exterior_views(ev, 3) == ["ext_1", "ext_5", "ext_2"]


# --------------------------------------------------------------------------
# Prompts, schema and the advisory facade count
# --------------------------------------------------------------------------

def test_the_exterior_prompt_asks_about_windows_and_doors_of_a_building_seen_from_outside(tmp_path):
    exp = ext_expected(tmp_path)
    items = P.check_items(exp, None)
    text = P.check_prompt(items, None, None, view_kind="exterior")
    assert "a building seen from outside" in text and "Do not list walls, roof" in text
    assert "an empty doorway" not in text and "room" not in text.split("Categories:")[0].lower().replace("broom", "")
    assert "- E1:" in text and "window (glazed window with frame and glass)" in text or "door (door leaf" in text
    assert P.check_prompt(items, "Salon", "living") != text


def test_the_facade_prompt_names_no_expected_number():
    text = P.facade_prompt("south")
    bare = text.replace("image 1", "").replace("(0..1)", "")
    assert "south facade" in text and not any(ch.isdigit() for ch in bare) and "expected" not in text.lower()
    schema = S.facade_schema()
    assert schema_errors(schema, {"window_count": 3, "door_count": 1, "confidence": 0.9}) == []
    assert schema_errors(schema, {"window_count": 41, "door_count": 1, "confidence": 0.9})
    assert schema_errors(schema, {"window_count": 3, "door_count": 1})


def ext_project(tmp_path, **kw) -> Project:
    out = E.write_ext_project(tmp_path, **kw)
    return Project(out)


def test_the_facade_calls_ride_with_the_cycles_kind(tmp_path):
    project = ext_project(tmp_path)
    kinds = C.check_kinds(project, ["cycles"])
    assert (CAM, "cycles") in kinds and (CAM, "facade:south") in kinds and (CAM, "facade:east") in kinds
    spec = C.check_spec(project, CAM, "facade:south", "fake/model")
    assert spec.prompt_kind == "facade" and spec.key == f"facade|{CAM}|facade:south"
    assert spec.images == [project.check_dir / f"{CAM}_facade_south.png"] and spec.images[0].is_file()
    assert spec.expected["facade"]["side"] == "south" and "south facade" in spec.prompt
    assert spec.input_sha256 and spec.items == []
    plain = C.check_spec(project, CAM, "cycles", "fake/model")
    assert "a building seen from outside" in plain.prompt and plain.prompt_kind == "check"


def test_combine_facade_judges_a_count_against_the_range_of_the_openings_seen():
    spec = type("S", (), {"expected": {"facade": {"side": "south", "windows": 2, "partial_windows": 1, "doors": 1,
                                                  "partial_doors": 0, "ids": ["a"], "box_px": [0, 0, 1, 1]}}})()

    def rec(w, d):
        return {"data": {"window_count": w, "door_count": d, "confidence": 0.9}}

    ok = CB.combine_facade(spec, {"qwen": rec(3, 1), "glm": rec(2, 1)}, ["qwen", "glm"])
    assert (ok["windows"], ok["doors"], ok["result"]) == ("ok", "ok", "ok") and ok["advisory"] is True
    assert ok["expected"] == {"windows": [2, 3], "doors": [1, 1], "ids": ["a"]}
    few = CB.combine_facade(spec, {"qwen": rec(1, 1), "glm": rec(0, 1)}, ["qwen", "glm"])
    assert (few["windows"], few["result"]) == ("fewer", "mismatch")
    more = CB.combine_facade(spec, {"qwen": rec(2, 3), "glm": rec(2, 2)}, ["qwen", "glm"])
    assert (more["doors"], more["result"]) == ("more", "mismatch")
    split = CB.combine_facade(spec, {"qwen": rec(1, 1), "glm": rec(3, 1)}, ["qwen", "glm"])
    assert (split["windows"], split["result"]) == ("unverified", "unverified")
    gone = CB.combine_facade(spec, {"qwen": rec(2, 1), "glm": None}, ["qwen", "glm"])
    assert gone["result"] == "not_computed"
    one = CB.combine_facade(spec, {"qwen": rec(1, 1)}, ["qwen"])
    assert one["windows"] == "unverified" and one["result"] == "unverified"


def test_run_and_combine_an_exterior_project_with_a_fake_model(tmp_path):
    project = ext_project(tmp_path)
    truth = {f"renders/{CAM}.png": {"window", "door"}}
    client = T.FakeClient(truth=truth, counts={f"renders/{CAM}.png": (3, 1)},
                          facade_counts={f"check/{CAM}_facade_south.png": (2, 1), f"check/{CAM}_facade_east.png": (0, 0)})
    from wenart.vision_check.cli import main as vc_main
    for key in ("qwen", "glm"):
        assert vc_main(["run", "--project-out", str(project.out), "--model-key", key, "--kinds", "cycles"],
                       client_factory=lambda k, url: client) == 0
    assert vc_main(["combine", "--project-out", str(project.out), "--models", "qwen,glm", "--no-debug"]) == 0
    manifest = json.loads((project.out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    cam = manifest["views"][CAM]
    assert cam["view_kind"] == "exterior" and cam["room_id"] is None
    assert cam["exterior"]["roof"]["result"] == "ok"
    south = cam["facades"]["south"]
    assert south["result"] == "ok" and south["passes"]["qwen"] == {"window_count": 2, "door_count": 1,
                                                                   "confidence": 0.9}
    assert cam["facades"]["east"]["expected"]["windows"][0] + cam["facades"]["east"]["expected"]["windows"][1] >= 0
    assert "facade:south" not in cam                                      # not an image kind of the view
    report = (project.out / "check" / "check_report.md").read_text(encoding="utf-8")
    assert "## Exterior views" in report and "| ext_1 | south |" in report
    assert "## Elevation check" in report and "## Drawn pieces against the source plan" in report
