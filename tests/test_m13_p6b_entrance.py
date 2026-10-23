"""CPU tests of the fix round after P6b (23 Oct 2026), track E_entrance: the entrance view framed on its door
(wenart/blender/exterior.py ``entrance_frame``, ``facade_points``, ``entrance_shot_problem``, ``_try_entrance``).

What is pinned: an entrance view (a ``flat_cut`` building's ``entrance_views``) stays level and aims at its door (the
target is the door's aim point at the camera's height, no yaw re-centring on the whole building); its lens shift comes
only from the building points inside the horizontal field of view and the door's aim point, so a corner beside the
camera, just in front of its plane, cannot drive it; a place is accepted only with its door in ``visible_openings``
and ``SKY_MIN_SHARE`` of sky, else the same place level with no lens shift, then the next distance; with no such
place the first free one is kept with ``ENTRANCE_KEPT_WARNING``, with no free place the view is dropped.
Why: P6b's ext_7 (real03, 8 m from the door of a 33 m facade) was framed by ``frame_fixed`` on all building points;
after the agent's roof overhang of 0.6 m a wall corner 0.17 m in front of the camera plane set the shift to -0.72
(clamped to -0.35): no sky, the door out of the frame, the boundary hedge on 46 % of the image. On a plain 33 m box
the old frame never showed the door at all.
How: hand-made point sets and stubbed ray checks, a synthetic 33.3 x 15 m single-floor building (tests/_levels_fixture
stretched; ``levels.model.infer_levels`` gives it the ``flat_cut`` roof and the entrance record), and, where present,
P6b's and P4b's real03 buildings (runs/, git-ignored: those tests skip without them). Pure Python, no Blender.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from wenart.blender import build as B
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X
from wenart.levels import model as LM
from tests import _levels_fixture as F

ROOT = Path(__file__).resolve().parents[1]
P6B_RUN = ROOT / "runs" / "20261022-235127-fetch_results" / "results"
P6B_REAL03 = P6B_RUN / "furniture" / "real03" / "building_final.json"
P4B_REAL03 = ROOT / "runs" / "20261017-091212-full" / "results" / "furniture" / "real03" / "building_final.json"
P6B_TARGET = (15.603, 0.0003, 1.45)          # d_L0_019's face at the eye height (ground -0.15 + 1.6)


# --------------------------------------------------------------------------
# entrance_frame: level, aimed at the door, shift from the points in the frame
# --------------------------------------------------------------------------

def _facade(x0=0.0, x1=33.0, y=0.0, z0=-0.15, z1=3.2, step=1.0):
    """The bottom and top points of a straight facade along x at ``y``."""
    xs = np.arange(x0, x1 + 1e-9, step)
    return np.array([(x, y, z) for x in xs for z in (z0, z1)], dtype=np.float64)


def test_entrance_frame_is_level_aimed_at_the_door_and_ignores_a_corner_beside_the_camera():
    """Fails on 620997b (no ``entrance_frame``) and on the mutation that drops the field-of-view filter: a corner
    0.17 m in front of the camera plane, beside the camera (P6b's (30.13, 0.15) after the re-centred yaw), has
    tangents of about +-10 and would set the shift to the clamp."""
    pos = (18.3392, -7.5172, 1.45)
    aim = (15.603, 0.0003, 1.2)
    pts = _facade()
    rec = E.entrance_frame(pos, aim, pts, E.EYE_LENS_MM)
    assert rec["target"] == [pytest.approx(15.603), pytest.approx(0.0003), pytest.approx(1.45)]
    assert abs(rec["shift_y"]) < 0.05 and rec["warning"] is None
    assert rec["fill"] is None and rec["fits"] is None and rec["lens_mm"] == E.EYE_LENS_MM
    f, r, u = E._basis(np.array(pos), np.array(rec["target"]))
    side = np.array(pos) + 0.17 * f + 6.0 * r                  # beside the camera, outside the 34.7 degree half width
    near = np.vstack([pts, side + np.array([0.0, 0.0, -1.6]), side + np.array([0.0, 0.0, 1.75])])
    assert E.entrance_frame(pos, aim, near, E.EYE_LENS_MM) == rec
    # a tall part of the building inside the frame does count: the frame moves up to it
    tall = np.vstack([pts, np.array(pos) + 6.0 * f + np.array([0.0, 0.0, 6.0])])
    assert E.entrance_frame(pos, aim, tall, E.EYE_LENS_MM)["shift_y"] > 0.1


def test_entrance_shot_problem_names_the_hidden_door_and_the_missing_sky():
    assert E.entrance_shot_problem("d1", ["d1", "w1"], 0.18) is None
    assert E.entrance_shot_problem("d1", ["w1"], 0.18) == "the door d1 is not in the frame"
    assert E.entrance_shot_problem("d1", ["d1"], 0.0) == "0% sky (< 3%)"
    assert E.entrance_shot_problem(None, [], E.SKY_MIN_SHARE) is None


def test_facade_points_sample_the_edges_between_the_corners():
    """A facade that crosses the frame between two corners outside it must still be seen (the corners alone give
    nothing in the frame)."""
    b = _long_building(None)
    prep = B.prepare(b, "base", None)
    vb = prep["building"]
    levels = X._base_levels(vb)
    model = E.build_model(vb, levels, prep["roof"], prep["site"])
    corners = E.building_points(model)
    dense = E.facade_points(model)
    assert len(dense) > len(corners) and np.allclose(dense[:len(corners)], corners)
    front = dense[np.abs(dense[:, 1] - dense[:, 1].min()) < 1e-6]          # the outer face of the front wall
    xs = np.unique(np.round(front[:, 0], 6))
    assert np.max(np.diff(xs)) <= E.ENTRANCE_POINT_STEP_M + 1e-6


# --------------------------------------------------------------------------
# _try_entrance: the door and the sky, else the level pose, else the next place
# --------------------------------------------------------------------------

def _stubbed(monkeypatch, shift, door_seen, sky):
    """Every place is free; ``entrance_frame`` gives ``shift``; ``door_seen(pos, shift_y)`` and ``sky(pos, shift_y)``
    decide the gate."""
    monkeypatch.setattr(E, "facade_points", lambda model: np.zeros((1, 3)))
    monkeypatch.setattr(E, "entrance_frame", lambda pos, aim, pts, lens: {
        "lens_mm": lens, "shift_y": shift, "target": [aim[0], aim[1], pos[2]], "warning": None, "fill": None,
        "fits": None})
    monkeypatch.setattr(E, "view_check", lambda model, pos, *a: dict(ok=True, why=None, building_share=0.5,
                                                                       blocked=0.0, aim_visible=True))
    monkeypatch.setattr(E, "visible_openings", lambda model, b, lv, pos, tgt, lens, s: ["d1"] if door_seen(pos, s)
                        else ["w1"])
    monkeypatch.setattr(E, "sky_share", lambda model, pos, tgt, lens, s=0.0: sky(pos, s))
    return SimpleNamespace(inside=lambda pos: None)


CANDS = [((8.0, -8.0, 1.6), "8.0 m"), ((10.0, -10.0, 1.6), "10.0 m"), ((12.0, -12.0, 1.6), "12.0 m")]
AIM = (0.0, 0.0, 1.2)


def test_an_entrance_place_without_its_door_or_sky_is_refused_for_the_level_pose_or_the_next_place(monkeypatch):
    """Fails on 620997b (``_try`` accepted the first free place: P6b's ext_7 with the door out of the frame and 0 %
    sky) and on the mutation that drops the gate (the plan would stand at 8 m)."""
    model = _stubbed(monkeypatch, 0.2, door_seen=lambda pos, s: pos[0] != 8.0,
                     sky=lambda pos, s: 0.0 if s else 0.15)
    plan = E._try_entrance(model, {}, [], "ext_7", CANDS, AIM, "d1", extra={"entrance": "d1"})
    assert plan["position"] == [10.0, -10.0, 1.6] and plan["shift_y"] == 0.0 and plan["sky_share"] == 0.15
    assert plan["view"] == "entrance" and plan["entrance"] == "d1" and plan["pitch_deg"] == 0.0
    assert plan["target"] == [0.0, 0.0, 1.6] and "fill" not in plan
    assert plan["warning"].startswith("level with no lens shift; refused before: 10.0 m: 0% sky")
    # the framed pose itself passes when it shows both
    model = _stubbed(monkeypatch, 0.2, door_seen=lambda pos, s: True, sky=lambda pos, s: 0.18)
    plan = E._try_entrance(model, {}, [], "ext_7", CANDS, AIM, "d1")
    assert plan["position"] == [8.0, -8.0, 1.6] and plan["shift_y"] == 0.2 and plan["warning"] is None


def test_with_no_place_showing_the_door_the_first_free_one_is_kept_and_with_none_free_the_view_is_dropped(
        monkeypatch):
    model = _stubbed(monkeypatch, 0.0, door_seen=lambda pos, s: False, sky=lambda pos, s: 0.2)
    plan = E._try_entrance(model, {}, [], "ext_7", CANDS, AIM, "d1")
    assert not plan.get("dropped") and plan["position"] == [8.0, -8.0, 1.6]
    assert plan["warning"] == E.ENTRANCE_KEPT_WARNING.format(door="d1", why="the door d1 is not in the frame")
    inside = SimpleNamespace(inside=lambda pos: "building")
    dropped = E._try_entrance(inside, {}, [], "ext_7", CANDS, AIM, "d1", extra={"entrance": "d1"})
    assert dropped["dropped"] and dropped["view"] == "entrance" and dropped["entrance"] == "d1"
    assert dropped["dropped_reason"].startswith("8.0 m: inside the building")


# --------------------------------------------------------------------------
# A synthetic long, low, single-floor building (runs everywhere)
# --------------------------------------------------------------------------

def _long_building(overhang, fence="hedge", length=33.3, depth=15.0, door_x=15.6):
    """tests/_levels_fixture's building stretched to ``length`` x ``depth`` m, the front door at ``door_x`` on the
    south wall, read by ``levels.model.infer_levels`` (a ``flat_cut`` roof, the entrance record); ``overhang``: the
    agent's flat roof override with the round-3 site edit of P6b (path, ``fence``, front court)."""
    b = F.building()
    b["walls"] = [F._wall("w_1", (0, 0), (length, 0)), F._wall("w_2", (length, 0), (length, depth)),
                  F._wall("w_3", (length, depth), (0, depth)), F._wall("w_4", (0, depth), (0, 0)),
                  F._wall("w_5", (door_x - 2, 0), (door_x - 2, depth), exterior=False)]
    b["openings"] = [F._opening("d_front", "door", "w_1", (door_x, 0.0), 1.0),
                     F._opening("d_inner", "door", "w_5", (door_x - 2, depth / 2), 0.9),
                     F._opening("win_1", "window", "w_1", (door_x - 6, 0.0), 1.5)]
    b["rooms"] = [F._room("r_living", [(0.1, 0.1), (door_x - 2.1, 0.1), (door_x - 2.1, depth - 0.1),
                                       (0.1, depth - 0.1)], "living"),
                  F._room("r_hall", [(door_x - 1.9, 0.1), (length - 0.1, 0.1), (length - 0.1, depth - 0.1),
                                     (door_x - 1.9, depth - 0.1)], "hall")]
    b = LM.infer_levels(b)
    if overhang is not None:
        b["agent_overrides"] = {"exterior": {"roof": {"type": "flat", "overhang_m": overhang},
                                             "site": {"path": True, "fence": fence, "front_court": "yes"}}}
    return b


def _entrance_plan(b, brief=None):
    prep = B.prepare(b, "base", brief)
    vb = prep["building"]
    levels = X._base_levels(vb)
    model = E.build_model(vb, levels, prep["roof"], prep["site"])
    plans, dropped = E.plan_exterior(model, vb, levels, (prep["site"] or {}).get("plot") or [], variant="base")
    ent = [p for p in plans + dropped if p.get("view") == "entrance"]
    assert len(ent) == 1 and not ent[0].get("dropped")
    out: list = []
    X._x6(b, prep, {"cameras": [dict(p, source="searched") for p in plans]}, None, out)
    return ent[0], model, [v["message"] for v in out if v["check"] == "X6" and v.get("target") == ent[0]["name"]]


@pytest.mark.parametrize("overhang, fence", [(None, "hedge"), (0.6, "none"), (0.8, "hedge")])
def test_a_33_m_single_floor_building_frames_its_entrance_door_with_the_sky(overhang, fence):
    """Fails on 620997b: the yaw re-centred on the whole 33 m building turned the 8 m view to x = 24.3, and the door
    (x = 15.6) was out of the frame at every overhang (X6 'does not show its door'). Now: level, aimed at the door's
    face at the eye height, shift about 0, the door in the frame, sky well over SKY_MIN_SHARE, no X6."""
    b = _long_building(overhang, fence)
    plan, model, x6 = _entrance_plan(b)
    assert plan["placement"] == "8.0 m in front of the entrance d_front" and plan["entrance"] == "d_front"
    assert plan["target"] == [pytest.approx(15.6), pytest.approx(-0.1), pytest.approx(plan["position"][2])]
    assert plan["pitch_deg"] == 0.0 and abs(plan["shift_y"]) < 0.02 and plan["warning"] is None
    assert "d_front" in plan["visible_openings"] and "fill" not in plan
    assert plan["sky_share"] >= 0.15 and plan["sky_share"] == E.sky_share(model, plan["position"], plan["target"],
                                                                          plan["lens_mm"], plan["shift_y"])
    assert plan["score"]["building_share"] >= 0.4 and x6 == []
    assert X.entrance_view_problem(X.entrance_record(b, plan), plan["position"], plan["target"],
                                   plan["lens_mm"]) is None


# --------------------------------------------------------------------------
# P6b's and P4b's real03 (runs/, not committed)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not P6B_REAL03.is_file(), reason="P6b's real03 run (runs/20261022-235127-fetch_results) is absent")
@pytest.mark.parametrize("overhang, fence", [(0.5, "hedge"), (0.6, "none"), (0.6, "hedge"), (0.8, "hedge")])
def test_p6b_real03_entrance_view_keeps_its_door_and_sky_under_the_agents_roof_and_site_edits(overhang, fence):
    """The P6b replay: on 620997b overhangs 0.6-0.8 gave target (14.06, -0.76), shift -0.72 clamped to -0.35, 0 % sky
    and no door (the pod's ext_7); 0.5 gave a frame turned to the building's middle. Now every case aims at the door
    d_L0_019 at the eye height with 17-20 % sky, no hedge ray and no X6."""
    b = json.loads(P6B_REAL03.read_text(encoding="utf-8"))
    b["agent_overrides"]["exterior"]["roof"]["overhang_m"] = overhang
    b["agent_overrides"]["exterior"]["site"]["fence"] = fence
    plan, _model, x6 = _entrance_plan(b)
    assert plan["name"] == "ext_7" and plan["entrance"] == "d_L0_019"
    assert plan["placement"] == "8.0 m in front of the entrance d_L0_019"
    assert plan["target"] == [pytest.approx(c, abs=1e-3) for c in P6B_TARGET]
    assert abs(plan["shift_y"]) < 0.02 and plan["warning"] is None and plan["pitch_deg"] == 0.0
    assert "d_L0_019" in plan["visible_openings"] and 0.17 <= plan["sky_share"] <= 0.20
    assert plan["score"]["hedge_blocked"] == 0.0 and plan["score"]["blocked"] == 0.0
    assert x6 == []


@pytest.mark.skipif(not P4B_REAL03.is_file(), reason="P4b's real03 run (runs/20261017-091212-full) is absent")
def test_p4b_real03_entrance_view_now_aims_at_its_door():
    """P4b's ext_7 (overhang 0.5, fence) showed its door only by chance (turned 42 degrees off the door's axis to the
    building's middle, 'does not fit'); now it looks straight at the door with the sky and no warning."""
    b = json.loads(P4B_REAL03.read_text(encoding="utf-8"))
    plan, _model, x6 = _entrance_plan(b)
    assert plan["target"] == [pytest.approx(c, abs=1e-3) for c in P6B_TARGET]
    look = math.degrees(math.atan2(plan["target"][1] - plan["position"][1], plan["target"][0] - plan["position"][0]))
    assert look == pytest.approx(110.0, abs=0.5)              # 20 degrees off the door's axis (outward -y), at the door
    assert "d_L0_019" in plan["visible_openings"] and plan["sky_share"] >= 0.17 and plan["warning"] is None
    assert x6 == []
