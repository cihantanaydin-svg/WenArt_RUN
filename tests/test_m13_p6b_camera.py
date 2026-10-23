"""Fix round after P6b (23 Oct 2026; pod P6b, real03 with the Milestone 11 cameras replayed), track C_cam: a replayed
camera that a newly built piece blocks or contains is moved by the build (docs/milestone13.md §7: "A frozen camera that
ends up inside a newly built piece is moved by the free-floor rule and marked").

What: CPU tests of ``camsearch.move_blocked_replayed`` / ``lens_inside_pieces`` (the trigger: the model's one-element
share over ``SCORE["blocked_single"]`` or the lens inside a built piece at eye height, never the near share or the
nearest-depth rule, and a piece the lens looks out of left out first; the move: the nearest free point of the room
within ``REPLAY_MOVE_MAX_M`` whose view through the same frame is not blocked, distinct from the room's other views
first; the pose kept with ``BLOCKED_WARNING`` without one), of the build's wiring (``build.replayed_moves`` before the
search and ``merge_agent_cameras``, ``cameras_from.moved``), the schemas (``replay`` status ``moved``,
``cameras_from.moved``), the before | after note (``sheets13.camera_note``) and the GPU test's rule for a moved camera
(``tests/gpu/test_camera_replay.py::moved_problem``). On the runs' data (``runs/``, not committed; skipped without
them): P6b's building moves exactly yasama_2_2, 3_2, 5_2 and 6_1 (0.66-0.88 m) and keeps 4_3 (it looks out of the
fridge it stands in), 4_2 and 6_2 (near and depth rules over the counter); P4b real03, P4a real02 and P4a with this
round's coat closets read as wardrobes (P6c's risk) move nothing. The last test builds the example building in Blender
twice (WENART_BLENDER): the second build has a fridge on a replayed camera's spot.
Why: P6b's reading typed the boxes at the end of real03's kitchen runs as 2.02 m fridges (P4b had 0.9 m chairs);
four frozen Milestone 11 views stood inside or against them: three black final images, test_no_blocked_searched_view
and test_exposure_recorded_and_within_the_clamp failed. Every test fails on BASE (commit 620997b: no
``move_blocked_replayed``, no ``moved`` status) or names the mutation it guards.
"""
from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import math
from pathlib import Path

import jsonschema
import pytest

from wenart.blender import build as B
from wenart.blender import cameras as CA
from wenart.blender import camsearch as CS
from wenart.blender import cli
from wenart.blender import schemas
from wenart.report import sheets13 as SH

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
P6B = RUNS / "20261022-235127-fetch_results" / "results"
P4B = RUNS / "20261017-091212-full" / "results"
P4A = RUNS / "20261017-072801-full" / "results"
P6A = RUNS / "20261022-135644-m13_p6" / "results"
CAMERA_FILE = {"real02": ROOT / "results" / "renders" / "real02" / "scene_manifest.json",
               "real03": ROOT / "results" / "renders" / "real03" / "scene_manifest.json"}
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")


# --------------------------------------------------------------------------
# A hand-made kitchen: 5 x 4 m, a 2.02 m fridge against the west wall, a 0.9 m counter run on the south wall
# --------------------------------------------------------------------------

FRIDGE = ("fr", "fridge", (0.345, 2.0), (0.74, 0.69), 90.0, (0.74, 0.69, 2.02))    # x 0..0.69, y 1.63..2.37
COUNTER = ("ct", "kitchen_counter", (2.5, 0.3), (2.4, 0.6), 0.0, (2.4, 0.6, 0.9))


def _building(furniture=(FRIDGE, COUNTER), width: float = 5.0, depth: float = 4.0) -> dict:
    t, h = 0.2, 0.1
    walls = [{"id": "w_s", "level_id": "L0", "start": [-t, -h], "end": [width + t, -h], "thickness": t},
             {"id": "w_e", "level_id": "L0", "start": [width + h, -t], "end": [width + h, depth + t], "thickness": t},
             {"id": "w_n", "level_id": "L0", "start": [width + t, depth + h], "end": [-t, depth + h], "thickness": t},
             {"id": "w_w", "level_id": "L0", "start": [-h, depth + t], "end": [-h, -t], "thickness": t}]
    pieces = [{"id": fid, "type": ftype, "room_id": "r", "level_id": "L0", "front_deg": 0.0,
               "footprint": {"center": list(c), "size": list(s), "rotation_deg": rot},
               "asset": {"method": "library", "bbox_m": list(bbox)}} for fid, ftype, c, s, rot, bbox in furniture]
    return {"project": {"id": "hand"}, "status": "ok",
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.6}], "walls": walls, "openings": [],
            "rooms": [{"id": "r", "level_id": "L0", "label": "Mutfak", "room_type": "kitchen",
                       "polygon": [[0, 0], [width, 0], [width, depth], [0, depth]]}],
            "furniture": pieces}


def _cam(name: str, xy, yaw_deg: float, source: str = "replayed") -> dict:
    """A replayed Milestone 11 interior record as ``cameras.replay_cameras`` makes it (1.25 m, pitch 0, 18 mm)."""
    y = math.radians(yaw_deg)
    return {"name": name, "room_id": "r", "level_id": "L0", "kind": "interior", "source": source, "index": 1,
            "position": [xy[0], xy[1], 1.25], "target": [xy[0] + math.cos(y), xy[1] + math.sin(y), 1.25],
            "lens_mm": 18.0, "sensor_mm": 36.0, "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": -0.1,
            "visible_openings": [], "visible_furniture": [], "warning": None, "policy": "search",
            "replayed_from": {"build_fingerprint": "f" * 64, "camera_policy": "search", "policy": "search"}}


def _view(plan: dict) -> list[float]:
    return [float(t) - float(p) for t, p in zip(plan["target"], plan["position"])]


def _same_frame(before: dict, after: dict) -> None:
    """Yaw, pitch, height, lens, shift, sensor, name and source are the record's."""
    assert _view(after) == pytest.approx(_view(before), abs=1e-6)
    assert after["position"][2] == pytest.approx(before["position"][2], abs=1e-9)
    for key in ("name", "lens_mm", "shift_x", "shift_y", "sensor_mm", "resolution", "source", "room_id"):
        assert after[key] == before[key], key


def test_a_replayed_camera_inside_a_tall_piece_moves_with_its_frame():
    """The lens 0.3 m deep inside the fridge, looking out of it into the room (the box centre is behind the lens,
    but the box side it leaves through is 0.29 m ahead, more than ``REPLAY_LOOKS_OUT_M``): trigger ``inside``, the
    camera moves 0.6 m to the nearest free point with an unblocked view, its frame unchanged, the record and the warning
    name the fridge and §7, the plan validates as a scene camera. Fails on BASE (no move) and on the mutation
    "the looks-out exclusion without the distance ahead" (the camera would stay inside the fridge)."""
    building = _building()
    before = _cam("cam_r_1", (0.4, 2.0), 0.0)
    plan = copy.deepcopy(before)
    hits = CS.move_blocked_replayed([plan], building)
    assert [(h["name"], h["status"], h["trigger"], h["blocked_by"], h["blocked_by_type"]) for h in hits] == \
        [("cam_r_1", "moved", "inside", "fr", "fridge")]
    assert hits[0]["share_old"] == 1.0 and hits[0]["share"] <= CS.SCORE["blocked_single"]
    assert plan["position"] == pytest.approx([1.0, 2.0, 1.25])
    _same_frame(before, plan)
    rp = plan["replay"]
    assert rp["status"] == "moved" and rp["position_old"] == before["position"] and rp["target_old"] == before["target"]
    assert rp["moved_m"] == pytest.approx(0.6) and rp["trigger"] == "inside" and rp["blocked_by"] == "fr"
    assert "docs/milestone13.md §7" in rp["reason"] and "fridge fr" in rp["reason"]
    assert plan["warning"].startswith("replayed camera moved 0.60 m from (0.40, 2.00) to (1.00, 2.00)")
    assert CS.BLOCKED_WARNING not in plan["warning"]
    jsonschema.validate(plan, schemas.SCENE_CAMERA)
    view = CS.score_camera(building, plan)
    assert not CS.is_blocked(view["shares"])


def test_a_replayed_camera_in_front_of_a_tall_piece_moves_on_the_share_rule():
    """0.26 m in front of the fridge, looking at it: the one-element share is 1.0 (> 0.5) with the lens outside the
    box; trigger ``single_share``, the camera steps back 0.55 m along its own view line (the nearest free point)."""
    building = _building()
    before = _cam("cam_r_1", (0.95, 2.0), 180.0)
    plan = copy.deepcopy(before)
    assert CS.lens_inside_pieces(building["rooms"][0], building, plan["position"], 0.0) == []
    hits = CS.move_blocked_replayed([plan], building)
    assert [(h["status"], h["trigger"], h["blocked_by"]) for h in hits] == [("moved", "single_share", "fr")]
    assert plan["position"] == pytest.approx([1.5, 2.0, 1.25]) and plan["replay"]["moved_m"] == pytest.approx(0.55)
    _same_frame(before, plan)


def test_a_lens_that_looks_out_of_a_piece_stays_and_one_along_its_side_moves():
    """P6b's yasama_4_3 case: the lens inside the fridge's box, 0.07 m behind the side its view leaves through, the
    box centre behind it: the fridge is left out of the frame (its face is under the near clip) and the view is good,
    so the camera stays. A lens beside the box's side, looking along it (the front face 0.345 m ahead), moves: the
    mutation "nearest side instead of the side ahead" keeps it inside the fridge."""
    building = _building()
    out = _cam("cam_r_1", (0.62, 2.0), 0.0)
    room = building["rooms"][0]
    (piece, ahead), = CS.lens_inside_pieces(room, building, out["position"], 0.0, (1.0, 0.0))
    assert piece["id"] == "fr" and ahead == pytest.approx(0.07)
    assert CS.score_camera(building, out)["shares"]["max_single"] == 1.0           # the model with the fridge
    plan = copy.deepcopy(out)
    assert CS.move_blocked_replayed([plan], building) == [] and plan == out
    along = _cam("cam_r_2", (0.345, 2.3), 0.0)
    (_piece, ahead), = CS.lens_inside_pieces(room, building, along["position"], 0.0, (1.0, 0.0))
    assert ahead == pytest.approx(0.345)
    hits = CS.move_blocked_replayed([along], building)
    assert [(h["status"], h["trigger"]) for h in hits] == [("moved", "inside")]


def test_low_pieces_clear_views_and_other_cameras_never_move():
    """A lens over the 0.9 m counter (inside its footprint, above its top), a clear view, a searched camera inside the
    fridge, an exterior record and a record without a target are left as they are."""
    building = _building()
    plans = [_cam("cam_r_1", (2.5, 0.3), 90.0), _cam("cam_r_2", (3.5, 2.5), 200.0),
             _cam("cam_r_3", (0.4, 2.0), 0.0, source="searched"),
             dict(_cam("ext_1", (0.4, 2.0), 0.0), kind="exterior", room_id=None, level_id=None),
             {k: v for k, v in _cam("cam_r_4", (0.4, 2.0), 0.0).items() if k != "target"}]
    before = copy.deepcopy(plans)
    assert CS.move_blocked_replayed(plans, building) == [] and plans == before


def test_without_an_unblocked_point_in_reach_the_pose_stays_with_the_blocked_warning(monkeypatch):
    """No free point within ``REPLAY_MOVE_MAX_M`` gives an unblocked view (the reach cut to 0.3 m here): the camera
    keeps its pose, gets no ``replay`` record and its warning carries ``BLOCKED_WARNING`` (the GPU blocked-view test
    allows such a view); a room without a free point (the fallback point) is the same."""
    building = _building()
    monkeypatch.setattr(CS, "REPLAY_MOVE_MAX_M", 0.3)
    plan = _cam("cam_r_1", (0.4, 2.0), 0.0)
    hits = CS.move_blocked_replayed([plan], building)
    assert [(h["status"], h["moved_m"]) for h in hits] == [("kept", 0.0)]
    assert plan["position"] == [0.4, 2.0, 1.25] and "replay" not in plan
    assert plan["warning"].startswith(CS.BLOCKED_WARNING) and "within 0.3 m" in plan["warning"]
    monkeypatch.undo()
    tiny = _building(furniture=[("fr", "fridge", (0.4, 0.4), (0.74, 0.69), 0.0, (0.74, 0.69, 2.02))],
                     width=0.9, depth=0.9)
    plan = _cam("cam_r_1", (0.4, 0.4), 90.0)
    hits = CS.move_blocked_replayed([plan], tiny)
    assert [h["status"] for h in hits] == ["kept"] and CS.BLOCKED_WARNING in plan["warning"]


def test_a_moved_camera_keeps_distinct_from_the_room_s_other_views():
    """Another view of the room at the nearest free point with the same yaw: the moved camera goes to the nearest
    point 1 m or 50 degrees away from it (``select_views``' rule); a view turned 60 degrees does not stop the nearest
    point."""
    building = _building()
    plan, other = _cam("cam_r_1", (0.4, 2.0), 0.0), _cam("cam_r_2", (1.0, 2.0), 0.0)
    CS.move_blocked_replayed([plan, other], building)
    assert math.hypot(plan["position"][0] - 1.0, plan["position"][1] - 2.0) >= CS.MIN_DISTANCE_M
    assert plan["replay"]["moved_m"] <= CS.REPLAY_MOVE_MAX_M and other["position"] == [1.0, 2.0, 1.25]
    plan, other = _cam("cam_r_1", (0.4, 2.0), 0.0), _cam("cam_r_2", (1.0, 2.0), 60.0)
    CS.move_blocked_replayed([plan, other], building)
    assert plan["position"] == pytest.approx([1.0, 2.0, 1.25])


def test_the_build_moves_replayed_cameras_before_the_search_and_records_them():
    """``build.replayed_moves`` runs the move on the level's replayed plans against ``camera_building`` before the
    search and ``merge_agent_cameras`` (so every build, the agent's previews too, re-checks the frozen cameras), its
    lines name the camera; ``cameras_from.moved`` lists the moved replayed cameras and validates."""
    building = _building()
    plans = [_cam("cam_r_1", (0.4, 2.0), 0.0), _cam("cam_r_2", (3.5, 2.5), 200.0)]
    lines = B.replayed_moves(plans, building)
    assert len(lines) == 1 and lines[0].startswith("cam_r_1: replayed camera moved 0.60 m")
    record = {"path": "results/renders/real03/scene_manifest.json", "sha256": "0" * 64, "cameras": 2}
    summary = B.cameras_from_summary(record, {"plans": plans, "dropped": []}, plans, False)
    assert summary["moved"] == ["cam_r_1"] and summary["replayed"] == 2 and summary["repitched"] == []
    jsonschema.validate(summary, schemas.CAMERAS_FROM)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(summary, moved=[1]), schemas.CAMERAS_FROM)
    src = inspect.getsource(B.main)
    at = src.index("replayed_moves(replayed, camera_building(building, fit_not_built))")
    assert src.index("replayed = [p for p in replay[\"plans\"]") < at < src.index("cams.plan_cameras(") \
        < src.index("merge_agent_cameras(replayed, plans")


def test_the_schema_types_the_moved_record():
    """A moved record validates; one without its old pose, distance, trigger or reason does not; the re-pitch record
    still validates and a re-pitch record relabelled ``moved`` does not."""
    plan = _cam("cam_r_1", (0.4, 2.0), 0.0)
    CS.move_blocked_replayed([plan], _building())
    jsonschema.validate(plan, schemas.SCENE_CAMERA)
    for key in ("position_old", "target_old", "moved_m", "trigger", "blocked_by", "reason"):
        bad = dict(plan, replay={k: v for k, v in plan["replay"].items() if k != key})
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schemas.SCENE_CAMERA)
    for bad_rp in (dict(plan["replay"], status="shifted"), dict(plan["replay"], moved_m=0.0),
                   dict(plan["replay"], trigger="near"), dict(plan["replay"], share=1.5)):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(dict(plan, replay=bad_rp), schemas.SCENE_CAMERA)
    aerial = CA.replay_cameras({"cameras": [{"name": "ext_5", "kind": "exterior", "view": "aerial", "lens_mm": 28.54,
                                             "position": [-12.1724, -9.4236, 16.2917],
                                             "target": [7.1726, 6.517, 1.8195]}]})["plans"]
    assert B.repitch_replayed_aerials(aerial) == ["ext_5"]
    cam = dict(aerial[0], index=1, room_id=None, level_id=None, visible_openings=[], visible_furniture=[], warning=None)
    jsonschema.validate(cam, schemas.SCENE_CAMERA)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(cam, replay=dict(cam["replay"], status="moved")), schemas.SCENE_CAMERA)


def test_the_before_after_sheet_notes_a_moved_camera():
    """``sheets13.camera_note`` of a moved replayed camera says how far, from where to where, same yaw and lens, the
    piece and §7 (on BASE a moved camera had no note: shown as the baseline's own frame)."""
    plan = _cam("cam_r_L0_yasama_3_2", (0.4, 2.0), 0.0)
    CS.move_blocked_replayed([plan], _building())
    note = SH.camera_note(plan)
    assert note == ("replayed camera moved by the build 0.60 m from (0.40, 2.00) to (1.00, 2.00), same yaw and lens: "
                    "the fridge fr of this build contains the baseline pose (docs/milestone13.md §7)")
    assert SH.camera_note({"replay": {"status": "moved"}}) == SH.MOVED_NOTE_FALLBACK
    assert "blocks the baseline pose" in SH.camera_note(
        {"position": [1, 2, 1.25], "replay": dict(plan["replay"], trigger="single_share")})


def _gpu_replay_module():
    spec = importlib.util.spec_from_file_location("gpu_camera_replay_p6b",
                                                  ROOT / "tests" / "gpu" / "test_camera_replay.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_gpu_replay_test_accepts_a_moved_camera_and_only_a_faithful_one():
    """tests/gpu/test_camera_replay.py (``moved_problem``): a moved camera follows its record when its old pose is the
    record's, it moved in plan only and at most ``REPLAY_MOVE_MAX_M``, its view vector and lens are the record's, it
    has a reason and is in ``cameras_from.moved``; on BASE a moved camera failed with "pose or lens changed"."""
    gpu = _gpu_replay_module()
    rec = _cam("cam_r_1", (0.4, 2.0), 0.0)
    cam = copy.deepcopy(rec)
    CS.move_blocked_replayed([cam], _building())
    assert gpu.moved_problem(cam, rec, ["cam_r_1"]) is None
    turned = dict(cam, target=[cam["target"][0], cam["target"][1] + 0.5, cam["target"][2]])
    raised = dict(cam, position=[cam["position"][0], cam["position"][1], 1.4])
    far = dict(cam, position=[2.5, 2.0, 1.25], target=[3.5, 2.0, 1.25], replay=dict(cam["replay"], moved_m=2.1))
    problems = {"yaw": gpu.moved_problem(turned, rec, ["cam_r_1"]),
                "height": gpu.moved_problem(raised, rec, ["cam_r_1"]),
                "far": gpu.moved_problem(far, rec, ["cam_r_1"]),
                "lens": gpu.moved_problem(dict(cam, lens_mm=24.0), rec, ["cam_r_1"]),
                "old": gpu.moved_problem(dict(cam, replay=dict(cam["replay"], position_old=[9, 9, 1.25])), rec,
                                         ["cam_r_1"]),
                "reason": gpu.moved_problem(dict(cam, replay=dict(cam["replay"], reason="")), rec, ["cam_r_1"]),
                "listed": gpu.moved_problem(cam, rec, [])}
    assert all(problems.values()), problems
    assert "yaw or pitch" in problems["yaw"] and "height" in problems["height"] and "at most" in problems["far"]


# --------------------------------------------------------------------------
# The runs' data (runs/, not committed): P6b real03, P4b real03, P4a real02, P6a real04
# --------------------------------------------------------------------------

def _replayed(project: str, building: dict) -> list[dict]:
    """The camera file's interior plans of the building's rooms, as the build replays them."""
    rooms = {r["id"] for r in building["rooms"]}
    plans = CA.replay_cameras(json.loads(CAMERA_FILE[project].read_text(encoding="utf-8")))["plans"]
    return [p for p in plans if p["kind"] == "interior" and p.get("room_id") in rooms]


def _move_all(plans: list[dict], building: dict) -> list[dict]:
    hits = []
    for level in building["levels"]:
        hits += CS.move_blocked_replayed([p for p in plans if p.get("level_id") == level["id"]], building)
    return hits


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


P6B_MOVES = {   # P6b's building_final: the verifiers' points (verify:gpu_tests:0, verify:look:0)
    "cam_r_L0_yasama_2_2": ((31.0672, 5.15), 0.8817, "single_share", "f_L0_206"),
    "cam_r_L0_yasama_3_2": ((2.1539, 5.15), 0.7202, "inside", "f_L0_202"),
    "cam_r_L0_yasama_5_2": ((2.1539, 7.9773), 0.6831, "inside", "f_L0_200"),
    "cam_r_L0_yasama_6_1": ((31.0672, 7.9728), 0.6598, "inside", "f_L0_204"),
}


@pytest.mark.skipif(not (P6B / "furniture" / "real03" / "building_final.json").is_file(),
                    reason="needs runs/20261022-235127-fetch_results (pod P6b)")
def test_p6b_moves_the_four_views_at_the_fridges_and_keeps_the_others():
    """P6b's building (the agent's final, f_L0_204 moved 0.15 m onto yasama_6_1) and the committed camera file: exactly
    yasama_2_2, 3_2, 5_2 and 6_1 move, 0.66-0.88 m, each off its fridge, to an unblocked view (single share 0.11-0.15);
    yasama_4_3 stays (its lens is inside fridge f_L0_194's box but leaves it 0.057 m ahead, looking away), 4_2 and 6_2
    stay although ``is_blocked`` flags them (near share 0.39 / 0.47 and depth 0.094 m over the 1.18 m counter run:
    the mutation "trigger on is_blocked" moves them); every moved record validates."""
    building = _load(P6B / "furniture" / "real03" / "building_final.json")
    plans = _replayed("real03", building)
    before = {p["name"]: copy.deepcopy(p) for p in plans}
    assert len(plans) == 83
    hits = _move_all(plans, building)
    assert sorted(h["name"] for h in hits) == sorted(P6B_MOVES) and all(h["status"] == "moved" for h in hits)
    by = {p["name"]: p for p in plans}
    for name, (xy, dist, trigger, piece) in P6B_MOVES.items():
        p = by[name]
        assert p["position"][:2] == pytest.approx(list(xy), abs=1e-4), name
        assert p["replay"]["moved_m"] == pytest.approx(dist, abs=1e-3)
        assert (p["replay"]["trigger"], p["replay"]["blocked_by"], p["replay"]["blocked_by_type"]) == \
            (trigger, piece, "fridge")
        assert p["replay"]["share"] <= 0.15 and not CS.is_blocked(CS.score_camera(building, p)["shares"])
        _same_frame(before[name], p)
        jsonschema.validate(p, schemas.SCENE_CAMERA)
    for name, p in by.items():
        if name not in P6B_MOVES:
            assert p == before[name], name
    room4 = next(r for r in building["rooms"] if r["id"] == "r_L0_yasama_4")
    cam43 = by["cam_r_L0_yasama_4_3"]
    (piece, ahead), = CS.lens_inside_pieces(room4, building, cam43["position"], 0.0,
                                           CS._forward_xy(cam43["position"], cam43["target"]))
    assert piece["id"] == "f_L0_194" and ahead <= CS.REPLAY_LOOKS_OUT_M
    for name in ("cam_r_L0_yasama_4_2", "cam_r_L0_yasama_6_2"):
        shares = CS.score_camera(building, by[name])["shares"]
        assert CS.is_blocked(shares) and shares["max_single"] <= CS.SCORE["blocked_single"], name
    summary = B.cameras_from_summary({"path": str(CAMERA_FILE["real03"]), "cameras": 83},
                                     {"plans": plans, "dropped": []}, plans, False)
    assert sorted(summary["moved"]) == sorted(P6B_MOVES)
    jsonschema.validate(summary, schemas.CAMERAS_FROM)


@pytest.mark.skipif(not (P6B / "furniture" / "real03" / "building_decor.json").is_file(),
                    reason="needs runs/20261022-235127-fetch_results (pod P6b)")
def test_p6b_before_the_agent_moves_the_same_four_views():
    """The building before the agent's rounds (building_decor.json: f_L0_204 at its drawn place, 0.13 m from
    yasama_6_1's lens): the same four cameras move to the same points; 6_1 on the share rule (0.81), so the agent's
    preview builds would have moved it too."""
    building = _load(P6B / "furniture" / "real03" / "building_decor.json")
    plans = _replayed("real03", building)
    hits = {h["name"]: h for h in _move_all(plans, building)}
    assert sorted(hits) == sorted(P6B_MOVES)
    assert hits["cam_r_L0_yasama_6_1"]["trigger"] == "single_share" and hits["cam_r_L0_yasama_6_1"]["share_old"] > 0.8
    by = {p["name"]: p for p in plans}
    for name, (xy, _dist, _trigger, _piece) in P6B_MOVES.items():
        assert by[name]["position"][:2] == pytest.approx(list(xy), abs=1e-4), name


@pytest.mark.parametrize("project, run", [("real03", P4B), ("real02", P4A)])
def test_p4_buildings_move_no_replayed_camera(project, run):
    """P4b real03 (the boxes at the kitchen runs were 0.9 m chairs; the GPU blocked-view test passed) and P4a real02
    (35 replayed interior cameras): nothing moves."""
    path = run / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip(f"needs {run.parent.name}")
    building = _load(path)
    plans = _replayed(project, building)
    before = copy.deepcopy(plans)
    assert len(plans) == {"real03": 83, "real02": 35}[project]
    assert _move_all(plans, building) == [] and plans == before


@pytest.mark.skipif(not (P4A / "furniture" / "real02" / "building_final.json").is_file(),
                    reason="needs runs/20261017-072801-full (pod P4a)")
def test_p6c_risk_real02_corridor_closets_read_as_wardrobes_move_no_camera():
    """P6c's risk (gpu_tests lens, minor): this round's reading turns real02's corridor coat closets (f_L1_021 /
    f_L1_024, P4a's coffee tables with chairs) into 1.52 x 0.60 m wardrobes and drops their chairs. On P4a's building
    with that reading (the drawn footprints, the wardrobe's 2.1 m) no replayed camera is blocked or inside: the L1
    corridor views see the wardrobe at a third of the frame (koridor_1 / koridor_2: single share 0.32-0.33)."""
    building = _load(P4A / "furniture" / "real02" / "building_final.json")
    for f in building["furniture"]:
        if f["id"] in ("f_L1_021", "f_L1_024"):
            f.update(type="wardrobe", footprint=copy.deepcopy(f["drawn_footprint"]), build=True)
            f.pop("asset", None)
        elif f["id"] in ("f_L1_022", "f_L1_023", "f_L1_025", "f_L1_026"):
            f["build"] = False
    plans = _replayed("real02", building)
    assert _move_all(plans, building) == []
    by = {p["name"]: p for p in plans}
    for name in ("cam_r_L1_koridor_1", "cam_r_L1_koridor_2"):
        elements = CS.score_camera(building, by[name])["shares"]["elements"]
        assert 0.25 < elements["f_L1_021"] <= CS.SCORE["blocked_single"], name


@pytest.mark.skipif(not (P6A / "renders" / "real04" / "scene_manifest.json").is_file(),
                    reason="needs runs/20261022-135644-m13_p6 (pod P6a)")
def test_p6a_real04_has_no_replayed_camera():
    """real04 has no camera file records (P6a: 49 searched cameras): the move has nothing to do."""
    scene = _load(P6A / "renders" / "real04" / "scene_manifest.json")
    building = _load(P6A / "furniture" / "real04" / "building_final.json")
    replayed = [c for c in scene["cameras"] if c.get("source") == "replayed"]
    assert replayed == [] and _move_all(copy.deepcopy(scene["cameras"]), building) == []


# --------------------------------------------------------------------------
# The real build (Blender)
# --------------------------------------------------------------------------

def _build(building: dict, out: Path, extra: list[str]) -> dict:
    path = out.parent / f"{out.name}_building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--out", str(out), "--no-textures",
                                             "--no-preview", "--no-glb", "--camera-policy", "search"] + extra,
                    log_path=out / "build.log")
    return json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))


@needs_blender
def test_example_build_moves_a_replayed_camera_off_a_new_fridge(tmp_path):
    """The example building built once (its searched cameras), then with ``--cameras-from`` that manifest and a 2.02 m
    fridge standing on the first interior camera's spot: that camera is moved (``replay.status: moved``, its frame
    kept, ``cameras_from.moved``, a build warning, its Blender camera object still a replayed one), every other camera
    is the replayed record, and the scene manifest validates."""
    building = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    first = _build(copy.deepcopy(building), tmp_path / "first", [])
    inside = [c for c in first["cameras"] if c.get("kind") != "exterior"]
    assert inside
    cam = inside[0]
    x, y = cam["position"][:2]
    building["furniture"] = list(building.get("furniture") or []) + [
        {"id": "f_new_fridge", "type": "fridge", "room_id": cam["room_id"], "level_id": cam["level_id"],
         "footprint": {"center": [x, y], "size": [0.74, 0.69], "rotation_deg": 0.0}, "height": 2.02,
         "front_deg": 0.0, "label": "added_by_ai"}]
    second = _build(building, tmp_path / "second", ["--cameras-from", str(tmp_path / "first" / "scene_manifest.json")])
    schemas.validate_scene_manifest(second)
    by = {c["name"]: c for c in second["cameras"]}
    moved = by[cam["name"]]
    assert moved["source"] == "replayed" and moved["replay"]["status"] == "moved"
    assert moved["replay"]["blocked_by"] == "f_new_fridge" and moved["replay"]["position_old"] == cam["position"]
    assert 0.0 < moved["replay"]["moved_m"] <= CS.REPLAY_MOVE_MAX_M
    _same_frame(dict(cam, source="replayed"), moved)
    assert second["cameras_from"]["moved"] == [cam["name"]]
    assert any(w.startswith(f"{cam['name']}: replayed camera moved") for w in second["warnings"])
    for c in inside[1:]:
        assert by[c["name"]]["position"] == pytest.approx(c["position"], abs=1e-6), c["name"]
        assert "replay" not in by[c["name"]], c["name"]
    obj = next(o for o in second["objects"] if o["kind"] == "camera" and o["name"] == cam["name"])
    assert obj["assumed"]["source"] == "replayed"
