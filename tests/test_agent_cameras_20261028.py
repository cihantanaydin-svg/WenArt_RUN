"""28 Oct 2026 (real06 run 222248, GPU tests): the agent's interior views record what they frame
(``camsearch.frame_lists`` through ``build.finish_agent_interior_plans``: an override's lists were empty, so the depth
check held a view through a window to the 60 m indoor bound), an interior pose that copies another view of its room is
refused and ``show`` takes the next best pose (``tools.duplicate_interior_problem``: cam_r_L1_cocuk_odasi_1 and _2 got
one pose in two rounds), and the GPU colour checks read a room's wall finish (``_wall_kind``: oak panelling is no
paint)."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

from test_agent_helpers import CAMERAS, building
from test_argus_calls_20261027 import _ctx
from wenart.agent import overrides as OV
from wenart.agent import tools as TL
from wenart.blender import build as BD
from wenart.blender import camsearch as CSR
from wenart.blender import overrides as O

ROOT = Path(__file__).resolve().parents[1]


def _gpu():
    spec = importlib.util.spec_from_file_location("gpu_render_28", ROOT / "tests" / "gpu" / "test_render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _agent_plan(position, target, view_id="cam_r1_1"):
    entry = {"view_id": view_id, "kind": "interior", "room_id": "r1", "action": "set", "position": position,
             "target": target, "reason": "test"}
    return O.fixed_plan(entry, "L0")


def test_an_agent_view_records_the_openings_and_pieces_it_frames():
    b = building()
    plan = _agent_plan([2.0, 0.6, 1.25], [2.0, 1.6, 1.25])           # looks north at the bed and win1
    assert plan["visible_openings"] == [] and plan["visible_furniture"] == []
    searched = dict(copy.deepcopy(CAMERAS[0]), policy="search", source="searched", visible_openings=["x"])
    replayed = dict(_agent_plan([2.0, 0.6, 1.25], [2.0, 1.6, 1.25], "cam_r1_9"), source="replayed")
    lines = BD.finish_agent_interior_plans([plan, searched, replayed], b)
    assert "win1" in plan["visible_openings"] and "f1" in plan["visible_furniture"], plan
    assert {"anchors_in_frame", "set_in_frame"} <= set(plan) and len(lines) == 1 and "frames" in lines[0]
    assert searched["visible_openings"] == ["x"] and replayed["visible_openings"] == []      # only the agent's own
    away = _agent_plan([2.0, 3.0, 1.25], [2.0, 2.0, 1.25])           # looks south: the door, not the window
    BD.finish_agent_interior_plans([away], b)
    assert "win1" not in away["visible_openings"]
    assert CSR.frame_lists(b, dict(plan, room_id="r_none")) is None


def test_two_views_of_a_room_are_distinct_by_the_search_rule():
    a = {"position": [1.0, 1.0, 1.25], "target": [1.0, 2.0, 1.25]}
    assert not CSR.distinct_views(a, copy.deepcopy(a))
    assert not CSR.distinct_views(a, {"position": [1.4, 1.0, 1.25], "target": [1.6, 2.0, 1.25]})   # 0.4 m, 11 deg
    assert CSR.distinct_views(a, {"position": [1.0, 1.0, 1.25], "target": [2.0, 1.0, 1.25]})       # 90 deg
    assert CSR.distinct_views(a, {"position": [2.2, 1.0, 1.25], "target": [2.2, 2.0, 1.25]})       # 1.2 m apart
    assert CSR.distinct_views(a, {"position": [1.0, 1.0, 1.25], "target": [1.0, 1.0, 0.0]})        # no look


def _two_views(tmp_path):
    ctx = _ctx(tmp_path)
    second = dict(copy.deepcopy(CAMERAS[0]), name="cam_r1_2", position=[0.6, 0.6, 1.3], target=[3.0, 3.0, 1.2])
    ctx.scene["cameras"].append(second)
    return ctx


def test_a_pose_that_copies_another_view_of_the_room_is_refused(tmp_path):
    ctx = _two_views(tmp_path)
    reg = TL.build_registry()
    other = ctx.camera("cam_r1_2")
    res = reg.call(ctx, "set_camera", {"view_id": "cam_r1_1", "kind": "interior", "room_id": "r1",
                                       "position": list(other["position"]), "target": list(other["target"]),
                                       "reason": "copy the other view"})
    assert not res["accepted"] and "duplicate: cam_r1_1 would show the view cam_r1_2" in res["failed_checks"][0], res
    # an accepted override counts as the view's pose now: a later set of the other view may not copy it
    assert TL.duplicate_interior_problem(ctx, "cam_r1_2", {"room_id": "r1", **{k: ctx.camera("cam_r1_1")[k]
                                                                             for k in ("position", "target")}})
    assert TL.duplicate_interior_problem(ctx, "cam_r1_1", {"room_id": "r1", "position": [3.5, 3.0, 1.3],
                                                           "target": [3.5, 2.0, 1.3]}) is None
    assert TL.duplicate_view_problem(ctx, "ext_1", {"kind": "exterior", "position": [40, 40, 1.6],
                                                    "target": [41, 41, 1.6]}) is None


def test_show_takes_the_next_pose_when_the_best_copies_another_view(tmp_path, monkeypatch):
    ctx = _two_views(tmp_path)
    other = ctx.camera("cam_r1_2")
    best = {"position": list(other["position"]), "target": list(other["target"]), "lens_mm": 18.0}
    nxt = {"position": [3.4, 3.0, 1.25], "target": [3.0, 2.1, 1.25], "lens_mm": 18.0}
    monkeypatch.setattr(CSR, "poses_showing", lambda room, b, show, lens_mm=None: ([best, nxt], []))
    monkeypatch.setattr(ctx, "checks", lambda: type("C", (), {"validate_camera_override":
                                                              staticmethod(lambda b, e: {"ok": True})})())
    entry, failed = TL.show_pose(ctx, {"view_id": "cam_r1_1", "show": ["f1"]}, {"action": "set"})
    assert entry is not None and entry["position"] == nxt["position"] and not failed
    monkeypatch.setattr(CSR, "poses_showing", lambda room, b, show, lens_mm=None: ([best], []))
    entry, failed = TL.show_pose(ctx, {"view_id": "cam_r1_1", "show": ["f1"]}, {"action": "set"})
    assert entry is None and "duplicate" in failed[0]


def test_the_colour_checks_read_the_wall_finish_of_the_room():
    gpu = _gpu()
    style = {"walls": {"material": "plaster_white"}, "kitchen_walls": {"material": "wood_oak_light"}}
    assert gpu._wall_kind({"room_type": "kitchen"}, {}, style) == "wood"
    assert gpu._wall_kind({"room_type": "living_room"}, {}, style) == "painted"
    assert gpu._wall_kind({"room_type": "bathroom"}, {}, style) == "tiled"
    assert gpu._wall_kind({"room_type": "kitchen"}, {}) == "painted"                 # no style: as before
    assert gpu._wall_kind({"room_type": "bedroom"}, {}, {"walls": {"material": "brick_red"}}) == "brick"
    assert gpu._wall_kind({"room_type": "bedroom"}, {}, {"walls": {"material": "painted_wood_white"}}) == "painted"


def test_the_views_of_a_room_are_its_scene_cameras_at_their_pose_now(tmp_path):
    ctx = _two_views(tmp_path)
    poses = TL.interior_poses(ctx, "r1")
    assert set(poses) == {"cam_r1_1", "cam_r1_2"} and all(p["position"] for p in poses.values())
    assert set(TL.interior_poses(ctx, "r2")) == {"cam_r2_1"} and json.dumps(poses)


def test_argus_k5_finds_two_views_of_one_room_with_one_pose():
    from types import SimpleNamespace

    from wenart.audit import render_check as RC

    cams = [{"name": "cam_a_1", "room_id": "a", "position": [1, 1, 1.25], "target": [1, 2, 1.25]},
            {"name": "cam_a_2", "room_id": "a", "position": [1.3, 1, 1.25], "target": [1.4, 2, 1.25],
             "policy": "agent"},
            {"name": "cam_a_3", "room_id": "a", "position": [1, 1, 1.25], "target": [2, 1, 1.25]},
            {"name": "cam_b_1", "room_id": "b", "position": [1, 1, 1.25], "target": [1, 2, 1.25]},
            {"name": "ext_1", "room_id": None, "kind": "exterior", "position": [1, 1, 1.6], "target": [1, 2, 1.6]}]
    got = RC.duplicate_views({"cameras": cams})
    assert [f["target"] for f in got] == ["cam_a_2"] and got[0]["check"] == "K5"
    assert got[0]["evidence"]["same_as"] == "cam_a_1" and "remove_camera cam_a_2" in got[0]["fix"]
    res = RC.run(SimpleNamespace(check=None, manifest={"cameras": cams}))
    assert [f["check"] for f in res["findings"]] == ["K5"] and res["checked"]["interior_views"] == 4
