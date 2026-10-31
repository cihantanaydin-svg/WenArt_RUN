"""31 Oct 2026: the three GPU test failures of real06 run 20261030-224530-full (CPU; the run's view of the child's room
is cut into tests/fixtures/real06_224530_cocuk_odasi_2.json).

1. Index pass (``test_index_pass_contains_every_visible_proxy``, cam_r_L1_cocuk_odasi_2 without the library bed
   f_L1_004): the camera search's height profile of a bed found no ``back`` part in the UL163 slat and channel
   headboards and modelled the bed as one 0.92 m box over its whole footprint (``camsearch.PROFILE_BACK_ROLES``); and
   the GPU test's box3d guard read the bed's back alignment (its mesh 9.8 cm deeper than its footprint, head on the
   wall) as a misplaced mesh (``_built_centre``).
2. Olive walls (``test_daylight_walls_are_not_olive``, cam_r_L1_cocuk_odasi_1/2/3 at 1.42-1.50): the room's scheme
   deep:dark sage paints every wall dark sage, 1.502 by itself; the white balance is the other views' (their warm
   greige walls read 1.00). Such a room is left out like a room with an accent wall (``_scheme_green_views``).
3. Feature walls (``test_assumed_entries_of_the_design_details``, r_L1_ebeveyn_y_odasi and r_L1_oda_2): the AI's
   answers to C1 retyped the two bedrooms (each with its drawn bed) to storage rooms, so ``looks.accent_walls`` gave
   them no wall and ``feature_walls.plan_feature_walls``, which only visited the accent walls, recorded neither a
   panel nor a reason. Every room whose scheme names a panel now ends with a plan or a reason
   (``no_accent_wall_reason``), and an answer that is not the user's never retypes a room away from its drawn anchor
   piece (``architect_actions.drawn_anchor_against``).
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from test_blender_render import _gpu_test_module
from test_room_details_20261029 import SCANDI, _room, bedroom
from wenart.blender import architect_actions as AA
from wenart.blender import camsearch as C
from wenart.blender import feature_walls as FW
from wenart.blender import parametric as P

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "real06_224530_cocuk_odasi_2.json"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------ 1. the index pass

@pytest.mark.parametrize("form", P.HEADBOARD_FORMS)
def test_every_headboard_form_gives_the_bed_its_back_slab_in_the_model(form):
    """Every UL163 headboard form: the low part (frame and mattress) at the type height, the headboard a slab on the
    rear edge up to the full height, never one box of the full height over the whole bed."""
    for asset in (None, {"method": "library", "bbox_m": [1.6, 2.05, 1.1], "scaling": "uniform"}):
        piece = {"id": "b", "type": "bed_double", "height": 0.55, "asset": asset, "design": {"headboard": form},
                 "footprint": {"center": [0.0, 0.0], "size": [1.6, 2.0], "rotation_deg": 0.0}}
        w, d, top, _src = P.piece_bbox(piece)
        boxes = C.piece_profile(piece)
        assert len(boxes) >= 2, (form, asset, boxes)
        back = boxes[-1]
        # the frame and the mattress (a parametric bed: the frame's ledge and the mattress box; a library bed: one box)
        assert max(b[4] for b in boxes[:-1]) == pytest.approx(0.55)
        assert back[4] == pytest.approx(top) and top > 0.55 + 0.3
        assert back[3] == pytest.approx(d / 2.0) and back[3] - back[1] <= 0.15            # a slab, not the footprint
        assert back[2] - back[0] >= 0.9 * w                                                # as wide as the bed


def test_the_real06_bed_beside_the_lens_is_no_longer_a_full_height_box():
    fx = _fixture()
    bed = next(f for f in fx["building"]["furniture"] if f["id"] == "f_L1_004")
    assert bed["design"]["headboard"] == "slat" and bed["asset"]["method"] == "library"
    boxes = C.piece_profile(bed)
    assert len(boxes) == 2 and boxes[0][4] == pytest.approx(0.55) and boxes[-1][4] == pytest.approx(0.9205)
    shares = C.model_shares(fx["building"], fx["camera"])
    # the run's model saw 0.0897 of the frame (the 0.92 m box); the mattress at the frame's bottom edge is left
    assert shares["f_L1_004"] == pytest.approx(0.0174, abs=2e-3)


def _index_project(outputs: Path, fx: dict) -> tuple:
    path = outputs / "real06" / "building_final.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fx["building"]), encoding="utf-8")
    scene = {"building": str(path), "pass_index": fx["pass_index"], "cameras": [fx["camera"]],
             "objects": fx["objects"]}
    render = {"renders": [{"camera": fx["camera"]["name"], "index_values": fx["index_values"]}]}
    return "real06", scene, render


def test_the_real06_index_pass_case_is_library_box_edge_only(tmp_path, monkeypatch, capsys):
    fx = _fixture()
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / "outputs", fx))
    assert "('cam_r_L1_cocuk_odasi_2', 'f_L1_004', 0.0174)" in capsys.readouterr().out
    # the mesh's box3d stands 4.9 cm from the footprint centre by the fit's back alignment, as the build put it
    obj = next(o for o in fx["objects"] if o["wenart_id"] == "f_L1_004")
    bed = next(f for f in fx["building"]["furniture"] if f["id"] == "f_L1_004")
    assert gpu._built_centre(bed, obj["fit"]) == pytest.approx(obj["box3d"]["center"][:2], abs=1e-3)
    assert gpu._built_centre(bed, None) == pytest.approx(bed["footprint"]["center"])


def test_a_mesh_off_its_fit_still_fails_the_index_pass(tmp_path, monkeypatch):
    """Without the fit's depth record (or 5 cm off it), the mesh is not where the model puts it: still a failure."""
    for change in ("no_fit", "moved"):
        fx = _fixture()
        obj = next(o for o in fx["objects"] if o["wenart_id"] == "f_L1_004")
        if change == "no_fit":
            obj["fit"] = None
        else:
            obj["box3d"]["center"][1] += 0.05
        gpu = _gpu_test_module(monkeypatch, tmp_path / change)
        with pytest.raises(AssertionError, match=r"cam_r_L1_cocuk_odasi_2', \['f_L1_004'\]"):
            gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / change, fx))


# ------------------------------------------------------------------------------------------ 2. olive walls

def _gpu_render():
    spec = importlib.util.spec_from_file_location("gpu_render_31", ROOT / "tests" / "gpu" / "test_render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_room_painted_green_by_its_scheme_is_not_held_to_the_olive_bound():
    gpu = _gpu_render()
    rooms = {
        "r_L1_cocuk_odasi": {"id": "r_L1_cocuk_odasi", "room_type": "bedroom",
                             "scheme": {"walls": "deep_colour", "wall_colour": "dark sage", "key": "deep:dark sage"}},
        "r_L1_oda_2": {"id": "r_L1_oda_2", "room_type": "bedroom",
                       "scheme": {"walls": "limewash", "wall_colour": "warm greige", "key": "limewash:warm greige"}},
        "r_L1_blue": {"id": "r_L1_blue", "room_type": "bedroom",
                      "scheme": {"walls": "deep_colour", "wall_colour": "muted dusty blue", "key": "deep:blue"}},
        "r_L0_mutfak": {"id": "r_L0_mutfak", "room_type": "kitchen",
                        "scheme": {"walls": "plain", "wall_colour": None, "key": "art:warm greige"}},
    }
    # the run's measured walls: 1.42-1.50 for the child's room, its paint by itself 1.502
    assert gpu._paint_green(rooms["r_L1_cocuk_odasi"], SCANDI) == pytest.approx(1.502, abs=0.005)
    assert gpu._paint_green(rooms["r_L1_oda_2"], SCANDI) < gpu.DAYLIGHT_WALL_GREEN_MAX
    assert gpu._paint_green(rooms["r_L0_mutfak"], SCANDI) is None                 # the house's paint
    assert gpu._paint_green(rooms["r_L1_cocuk_odasi"], dict(SCANDI, room_schemes=False)) is None
    entries = {f"cam_{rid}_{k}": {"room_id": rid} for rid in rooms for k in (1, 2)}
    got = gpu._scheme_green_views(sorted(entries), entries, rooms, SCANDI)
    assert sorted(got) == ["cam_r_L1_cocuk_odasi_1", "cam_r_L1_cocuk_odasi_2"]       # the others stay pinned
    assert gpu._scheme_green_views(sorted(entries), entries, {}, SCANDI) == {}        # no building: every view pinned


# ------------------------------------------------------------------------------------------ 3. feature walls

def test_a_room_whose_scheme_names_a_panel_ends_with_a_plan_or_a_reason():
    b = bedroom()
    room = _room(b)
    room["scheme"] = {"feature": "fluted", "feature_kind": "fluted", "key": "panel:pale muted sage"}
    (plan,), skipped = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    assert plan["kind"] == "fluted" and skipped == []
    # the real06 case: the bedroom retyped to a storage room by an architect answer
    room.update(room_type="storage", drawn_type="bedroom",
                adjusted_by_ai={"by": "architect", "reason": "the answer to C1:r_L0_room: a storage"})
    plans, skipped = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    assert plans == [] and [s["room_id"] for s in skipped] == [room["id"]]
    why = skipped[0]["reason"]
    assert "a storage room gets no accent wall" in why and "drawn as a bedroom" in why and "C1:r_L0_room" in why
    # the brief turns accent walls off: the style's reason
    room.update(room_type="bedroom")
    plans, skipped = FW.plan_feature_walls(b, b["levels"][0], dict(SCANDI, wall_accent=False))
    assert plans == [] and "the style has no accent wall" in skipped[0]["reason"]
    # a scheme without a panel asks for no reason; a room without a scheme neither
    room["scheme"] = {"feature": "art_pair", "feature_kind": None, "key": "deep:x"}
    assert FW.plan_feature_walls(b, b["levels"][0], dict(SCANDI, wall_accent=False)) == ([], [])
    assert FW.scheme_names_panel({"scheme": {"feature": "headboard_panel"}}) and not FW.scheme_names_panel({})


def test_the_design_details_test_finds_the_reason_on_the_room():
    """The GPU test's ``_feature_walls`` reads ``feature_wall_skipped`` from the building as built: the build writes
    the planner's reasons there (``build_feature_walls``), so the two real06 bedrooms are no longer unrecorded."""
    import os

    os.environ.setdefault("RENDER_TEST_PROJECTS", "real06")
    spec = importlib.util.spec_from_file_location("gpu_look_31", ROOT / "tests" / "gpu" / "test_look_m6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    b = bedroom()
    room = _room(b)
    room.update(room_type="storage", drawn_type="bedroom",
                scheme={"feature": "fluted", "feature_kind": "fluted", "key": "panel:x"})
    rooms = {r["id"]: r for r in b["rooms"]}
    assert mod._feature_walls({"objects": []}, [], rooms)[2] == [room["id"]]           # the run's failure
    _plans, skipped = FW.plan_feature_walls(b, b["levels"][0], SCANDI)
    for s in skipped:                                                                 # as build_feature_walls does
        rooms[s["room_id"]]["feature_wall_skipped"] = s["reason"]
    assert mod._feature_walls({"objects": []}, [], rooms) == ([], [], [])


def _bedroom_plan(by: str):
    b = bedroom()
    answers = {"C1:r_L0_room": {"option": "retype_room", "params": {"room_type": "storage"}, "by": by,
                                "answer": "The room has the 0.85 m door to the hall, so it is reachable and not a "
                                          "shaft."}}
    return b, AA.apply_answers(b, answers)


def test_an_ai_answer_never_retypes_a_room_away_from_its_drawn_bed():
    b, applied = _bedroom_plan("ai")
    (rec,) = applied
    assert rec["ok"] is False and "holds the drawn bed_double" in rec["change"]
    assert _room(b)["room_type"] == "bedroom" and "adjusted_by_ai" not in _room(b)
    # the user's answer always wins
    b, applied = _bedroom_plan("user")
    assert applied[0]["ok"] is True and _room(b)["room_type"] == "storage"
    # a room without a drawn anchor of its type (an added bed, or none) can still be retyped by the AI
    b = bedroom()
    for f in b["furniture"]:
        f["source"] = "added_by_ai"
    plan = AA.Plan(b)
    assert AA.act_retype(plan, "C1:r_L0_room", {"by": "ai"}, "r_L0_room", "storage")[0] is True
    # a retype to a type that keeps the anchor (a bedroom read as a dressing room keeps no bed: refused; a bed in a
    # bedroom typed bedroom again changes nothing)
    b = bedroom()
    plan = AA.Plan(copy.deepcopy(b))
    assert AA.drawn_anchor_against(plan, _room(plan.b), "dressing")["type"] == "bed_double"
    assert AA.drawn_anchor_against(plan, _room(plan.b), "bedroom") is None
