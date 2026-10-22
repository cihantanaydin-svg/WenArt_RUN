"""CPU tests of the fix round after P6a (22 Oct 2026), track X_ext: the agent's exterior camera and X6's frontal view
(pod P6a, real04, runs/20261022-135644-m13_p6; docs/milestone13.md §14.13 decision 16).

What happened: the agent added ext_front_entrance at (8.5, 17.5, 1.6) -> (8.5, 12.5, 2.0), 26 mm, in the 5.7 m free
strip between real04's entrance (+y) facade and the copy b2 (log seq 6668). The validator passed it (inside nothing, eye
height 1.6 m), and X6 counted any ``agent`` view square to the main facade as "the frontal view", so "no frontal view
of the entrance (+y) facade" was gone and metrics 12 / 13 counted the view. The render is a blank wall: 0 of 576 rays
reach the sky, the facade spans 2.34 frame widths (both doors cut), 37 % of the pixels near black.

What is pinned (wenart/blender/exterior.py ``sky_share`` / ``frame_check`` / ``EYE_LENS_RANGE_MM`` /
``SKY_MIN_SHARE``; wenart/blender/exterior_checks.py ``x6_frontal`` / ``frame_problem`` / ``camera_frame`` /
``eye_level_problems`` / ``validate_camera_override`` / ``_x6``; wenart/agent/critic_vision.py ``x6_frontal`` /
``camera_role``; wenart/blender/build.py ``finish_agent_exterior_plans``):

- only rays above the horizon count as sky (the coarse ground ends: an aerial's misses below it are no sky);
- an ``elevation`` / ``agent`` view square to the main facade is X6's frontal view only when it frames the building
  (``frame_fixed`` fits, the re-centred frame still square) and shows the sky; otherwise "no frontal view" stays and the
  camera gets its own major X6; an eye-level agent view without sky gets one too; an agent view's fill gets no
  fill-range minor (real03's frontal ext_6 fills 0.94);
- the vision critic's camera role uses the same rule (the frame recorded on the camera, else measured on the building);
- the build records ``fill`` / ``fits`` / ``frame_target`` / ``sky_share`` on its agent exterior plans;
- the agent's eye-level exterior pose is refused without sky, and with a lens outside 24-28 mm (Milestone 11 E14)
  unless the building is long and low (CLAUDE.md, user OK of 22 Oct 2026);
- on the real runs: P6a's pose is refused and X6 keeps "no frontal view" with a major on the camera; every other
  accepted agent pose of P4a real02, P4b real03 and P6a real04 stays accepted, real02's and real03's frontal views stay
  frontal. The tests on runs/ skip without them (not committed). Pure Python, no Blender."""
import copy
import inspect
import json
import math
from pathlib import Path

import pytest

from wenart.agent import critic_vision as CV
from wenart.blender import build as B
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"
RUNS = ROOT / "runs"
P6A = RUNS / "20261022-135644-m13_p6" / "results"
P5 = RUNS / "20261017-224848-full" / "results"
P4A = RUNS / "20261017-072801-full" / "results"
P4B = RUNS / "20261017-091212-full" / "results"
# P6a's add_camera (log seq 6668)
P6A_POSE = ([8.5, 17.5, 1.6], [8.5, 12.5, 2.0])
MAIN_Y = {"axis": "+y", "direction": [0.0, 1.0], "source": "entrance doors"}


def _box(length=10.0, depth=8.0, ceiling=2.8, levels=1, roof="flat"):
    """A ``length`` x ``depth`` m box of ``levels`` storeys on flat ground with a ``roof`` (as
    tests/test_m13_exterior_framing.py ``_box``; with a roof the validator has a high-view line)."""
    pts = [(0, 0), (length, 0), (length, depth), (0, depth)]
    lvs = [{"id": f"L{k}", "elevation": round(k * (ceiling + 0.3), 3), "ceiling_height": ceiling}
           for k in range(levels)]
    walls = [{"id": f"w{k}_{i}", "level_id": lv["id"], "start": list(pts[i]), "end": list(pts[(i + 1) % 4]),
              "thickness": 0.25, "exterior": True} for k, lv in enumerate(lvs) for i in range(4)]
    site = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0, "method": "vector"}}]}, "decor": [],
            "boundary_walls": []}
    b = {"levels": lvs, "walls": walls, "openings": [], "rooms": [], "slabs": [], "site": site, "facade": {}}
    if roof:
        b["roof"] = {"type": roof}
    return b


def _ext(view_id, position, target, lens=26.0, action="add"):
    cam = {"action": action, "view_id": view_id, "kind": "exterior", "position": list(position),
           "target": list(target), "reason": "test"}
    if lens is not None:
        cam["lens_mm"] = lens
    return cam


def _model(building):
    return X.exterior_model(X._prep(building))


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# exterior.sky_share / frame_check
# --------------------------------------------------------------------------

def test_sky_share_counts_only_rays_above_the_horizon():
    """Fails on BASE (no ``exterior.sky_share``) and on a mutation that counts every ray that hits nothing: a box
    without a site has no ground, so half of a level camera's rays miss below the horizon."""
    b = _box(10.0, 8.0, levels=2, roof=None)
    m = E.build_model(b, b["levels"], None, None)                      # no site plan: no ground under the camera
    far = E.sky_share(m, [5.0, -30.0, 1.6], [5.0, 4.0, 1.6], 26.0)
    assert 0.3 < far < 0.5                                             # the upper half less the building
    import numpy as np
    from wenart.blender import camsearch
    a, bb = camsearch.ray_grid(E.RAY_GRID, lens_mm=26.0, sensor_mm=E.SENSOR_MM, resolution=E.RESOLUTION)
    dirs = camsearch.camera_directions([5.0, -30.0, 1.6], [5.0, 4.0, 1.6], a, bb)
    labels, _t = m.cast([5.0, -30.0, 1.6], dirs)
    assert float(np.mean(labels == E.LABELS["nothing"])) > far + 0.4  # the misses below the horizon are no sky
    # a camera 0.6 m from the wall sees the wall only
    assert E.sky_share(m, [5.0, -0.6, 1.6], [5.0, 4.0, 1.6], 26.0) == 0.0
    # looking 40 degrees down from 20 m up: the frame's top lies below the horizon, every miss is under it
    assert E.sky_share(m, [5.0, -20.0, 20.0], [5.0, 4.0, 20.0 - 24.0 * math.tan(math.radians(40.0))], 26.0) == 0.0


def test_frame_check_records_the_fill_the_fit_the_recentred_target_and_the_sky():
    """Fails on BASE (no ``exterior.frame_check``)."""
    b = _box(10.0, 8.0, levels=2, roof=None)
    m = E.build_model(b, b["levels"], None, None)
    pts = E.building_points(m)
    far = E.frame_check(m, [5.0, -30.0, 1.6], [7.0, 4.0, 1.6], 26.0)
    ff = E.frame_fixed([5.0, -30.0, 1.6], [7.0, 4.0, 1.6], pts, 26.0)
    assert far["fill"] == ff["fill"] and far["fits"] is True and far["frame_target"] == pytest.approx(ff["target"])
    assert far["sky_share"] == E.sky_share(m, [5.0, -30.0, 1.6], [7.0, 4.0, 1.6], 26.0) > E.SKY_MIN_SHARE
    near = E.frame_check(m, [5.0, -2.0, 1.6], [5.0, 4.0, 1.6], 26.0, pts)
    assert near["fits"] is False and near["fill"] > 1.0
    assert E.EYE_LENS_MM == 26.0 and E.EYE_LENS_RANGE_MM == (24.0, 28.0)      # Milestone 11 E14: 24-28 mm
    assert E.EYE_LENS_RANGE_MM[0] <= E.EYE_LENS_MM <= E.EYE_LENS_RANGE_MM[1] and E.SKY_MIN_SHARE == 0.03


# --------------------------------------------------------------------------
# X6: the frontal view frames the building with the sky
# --------------------------------------------------------------------------

AGENT_FRONT = {"name": "ext_front", "kind": "exterior", "view": "agent", "policy": "agent", "sides": ["back"],
               "position": [8.5, 30.0, 1.6], "target": [8.5, 6.0, 1.6], "lens_mm": 26.0}
TOY_PREP = {"outlines": {}, "roof": {"ridge_z": 6.0}, "main_facade": MAIN_Y}


def _x6(cams, prep=TOY_PREP):
    out = []
    X._x6({}, prep, {"cameras": copy.deepcopy(cams)}, None, out)
    return out


def test_x6_counts_an_agent_view_as_frontal_only_when_it_frames_the_building_with_sky():
    """Fails on BASE: ``_x6`` counted every agent view square to the main facade as the frontal view (P6a's
    ext_front_entrance: fill 2.34, no sky) and gave the camera no finding."""
    good = dict(AGENT_FRONT, fill=0.72, fits=True, sky_share=0.35, frame_target=[8.5, 6.0, 1.6])
    assert [v["message"] for v in _x6([good]) if v["check"] == "X6" and v["severity"] != "minor"] == []
    blank = dict(AGENT_FRONT, position=[8.5, 17.5, 1.6], target=[8.5, 12.5, 1.6], fill=2.3449, fits=False,
                 sky_share=0.0, frame_target=[8.36, 12.5, 1.6])
    out = _x6([blank])
    assert any(v["target"] == "exterior" and v["severity"] == "major" and "no frontal view" in v["message"]
               for v in out)
    own = [v for v in out if v["target"] == "ext_front"]
    assert len(own) == 1 and own[0]["severity"] == "major"
    assert "frames only part of the building" in own[0]["message"] and "2.34" in own[0]["message"]
    assert "no sky in the frame" in own[0]["message"]
    assert own[0]["metrics"] == {"fill": 2.3449, "fits": False, "sky_share": 0.0}
    # the bypasses of the verifier: a pitched-up pose (sky, the building does not fit), a pose that fits only turned
    # to a corner (real04's (22, 18.2): 29.8 degrees off square, framed 43.8 degrees off)
    up = dict(blank, sky_share=0.111)
    assert any("no frontal view" in v["message"] for v in _x6([up]))
    corner = dict(AGENT_FRONT, position=[22.0, 18.2, 1.6], target=[15.0, 6.0, 1.6], fill=0.82, fits=True,
                  sky_share=0.28, frame_target=[12.26, 8.06, 1.6])
    assert X._faces(corner, MAIN_Y["direction"])                        # the pose is square enough ...
    hits = _x6([corner])
    assert any("no frontal view" in v["message"] for v in hits)         # ... its framed view is a corner view
    assert not [v for v in hits if v["target"] == "ext_front"]          # a good view: no finding on the camera
    # the frontal view of the planner, and a pose whose frame cannot be measured (no record, no model): as before
    assert not any("no frontal view" in v["message"] for v in _x6([dict(AGENT_FRONT, view="frontal")]))
    assert not any("no frontal view" in v["message"] for v in _x6([AGENT_FRONT]))


def test_x6_eye_level_agent_view_without_sky_gets_a_major_and_its_fill_no_minor():
    """Fails on BASE: an agent view without sky had no finding; its recorded fill got the fill-range minor (P4b's
    real03 frontal ext_6 fills 0.94 of the frame: the minor would only move a view that frames the building)."""
    side = dict(AGENT_FRONT, name="ext_side", position=[30.0, 4.0, 1.6], target=[8.0, 4.0, 1.6], fill=0.5,
                fits=True, sky_share=0.0)                               # looks at the +x side, not the main facade
    out = _x6([dict(AGENT_FRONT, view="frontal"), side])
    own = [v for v in out if v["target"] == "ext_side" and v["severity"] == "major"]
    assert len(own) == 1 and "no sky in the frame" in own[0]["message"]
    assert "frames only part" not in own[0]["message"]                  # not a frontal pose: its fit is not judged
    wide = dict(AGENT_FRONT, fill=0.94, fits=True, sky_share=0.41, frame_target=[8.5, 6.0, 1.6])
    assert not [v for v in _x6([wide]) if "frame width" in v["message"]]
    planner = {"name": "ext_1", "kind": "exterior", "view": "corner", "sides": ["front", "left"],
               "position": [-5.0, -9.0, 1.6], "target": [5.0, 0.0, 1.6], "fill": 0.94}
    assert [v for v in _x6([planner]) if "frame width" in v["message"]]  # the planner's views keep the rule
    # a high agent view keeps the pose rule (its level frame says nothing about an aerial)
    high = dict(AGENT_FRONT, position=[8.5, 40.0, 12.0], fill=3.0, fits=False, sky_share=0.0)
    assert not [v for v in _x6([high]) if v["target"] == "ext_front" and v["severity"] == "major"]


def test_x6_measures_a_camera_without_a_recorded_frame_on_the_building():
    """A camera record without the frame (a manifest of P6a or before) is measured on the build's exterior model of
    the building (``camera_frame``, ``exterior_model``); fails on BASE (no ``exterior_checks.camera_frame``)."""
    b = _box(10.0, 8.0, levels=2)
    prep = X._prep(b)
    model = X.exterior_model(prep)
    near = {"name": "ext_9", "kind": "exterior", "view": "agent", "position": [5.0, -1.0, 1.6],
            "target": [5.0, 4.0, 1.6], "lens_mm": 26.0}
    rec = X.camera_frame(near, model)
    assert rec["fits"] is False and rec["sky_share"] == 0.0 and rec["fill"] > 1.0
    assert X.camera_frame(near, lambda: None) is None and X.camera_frame(near) is None
    recorded = dict(near, fill=0.7, fits=True, sky_share=0.3)
    assert X.camera_frame(recorded, model) == {"fill": 0.7, "fits": True, "sky_share": 0.3}
    out = []
    X._x6(b, dict(prep, main_facade={"axis": "-y", "direction": [0.0, -1.0]}), {"cameras": [near]}, None, out)
    assert any(v["target"] == "ext_9" and v["severity"] == "major" and "no sky" in v["message"] for v in out)
    assert any("no frontal view" in v["message"] for v in out)


def test_critic_vision_x6_frontal_is_x6s_rule():
    """The critic's camera role follows X6's rule: P6a's ext_front_entrance was told as "the frontal view". Fails on
    BASE (``critic_vision.x6_frontal`` judged the pose only)."""
    assert CV.X6_FRONTAL_POSE_VIEWS == X.FRONTAL_POSE_VIEWS
    blank = dict(AGENT_FRONT, fill=2.3449, fits=False, sky_share=0.0)
    assert not CV.x6_frontal(blank, MAIN_Y) and CV.camera_role(blank, MAIN_Y) == "agent"
    good = dict(AGENT_FRONT, fill=0.7, fits=True, sky_share=0.3)
    assert CV.x6_frontal(good, MAIN_Y) and CV.camera_role(good, MAIN_Y) == "frontal"
    assert CV.x6_frontal(AGENT_FRONT, MAIN_Y)                            # no frame known: the pose rule
    # with the building, a record without its frame is measured: 1 m from a box's -y wall is no frontal view
    b = _box(10.0, 8.0, levels=2)
    near = dict(AGENT_FRONT, position=[5.0, -1.0, 1.6], target=[5.0, 4.0, 1.6])
    main = {"axis": "-y", "direction": [0.0, -1.0]}
    assert CV.x6_frontal(near, main) and not CV.x6_frontal(near, main, building=b)
    assert CV.camera_role(near, main, prep=X._prep(b)) == "agent"


def test_critique_exterior_passes_its_building_to_the_camera_role():
    """Source wiring (fails on BASE): ``critique_exterior`` measures the role's frame on its building and plan."""
    src = inspect.getsource(CV.critique_exterior)
    assert "camera_role(camera, main_facade_of(scene, building, prep), building=building, prep=prep)" in src


# --------------------------------------------------------------------------
# build.finish_agent_exterior_plans records the frame
# --------------------------------------------------------------------------

def test_finish_agent_exterior_plans_records_the_frame_of_the_agents_plans():
    """Fails on BASE (no ``frame`` argument)."""
    agent = {"name": "ext_front_entrance", "kind": "exterior", "policy": "agent", "view": "agent", "sides": ["back"],
             "position": list(P6A_POSE[0]), "target": list(P6A_POSE[1]), "lens_mm": 26.0, "index": 1}
    replayed = dict(agent, name="ext_6", source="replayed")
    planner = {"name": "ext_1", "kind": "exterior", "view": "corner", "sides": ["front", "left"],
               "position": [-5.0, -9.0, 1.6], "target": [5.0, 0.0, 1.6], "lens_mm": 26.0, "fill": 0.69}
    plans = [copy.deepcopy(agent), copy.deepcopy(replayed), copy.deepcopy(planner)]
    seen = []

    def frame(p):
        seen.append(p["name"])
        return {"fill": 2.34489, "fits": False, "frame_target": [8.36051, 12.50189, 1.6], "sky_share": 0.0}

    B.finish_agent_exterior_plans(plans, "base", (8.5, 6.0), 0.0, False, frame=frame)
    assert seen == ["ext_front_entrance"]
    assert plans[0]["fill"] == 2.3449 and plans[0]["fits"] is False and plans[0]["sky_share"] == 0.0
    assert plans[0]["frame_target"] == [8.3605, 12.5019, 1.6]
    assert "fits" not in plans[1] and "fits" not in plans[2] and plans[2]["fill"] == 0.69
    again = [copy.deepcopy(agent)]
    B.finish_agent_exterior_plans(again, "base", (8.5, 6.0), 0.0, False, frame=lambda p: None)
    assert not any(k in again[0] for k in ("fill", "fits", "sky_share"))
    B.finish_agent_exterior_plans(again, "base", (8.5, 6.0), 0.0, False)        # without frame: as before
    assert not any(k in again[0] for k in ("fill", "fits", "sky_share"))

    def broken(p):
        raise ValueError("zero-size array to reduction operation minimum which has no identity")

    B.finish_agent_exterior_plans(again, "base", (8.5, 6.0), 0.0, False, frame=broken)   # a measure only
    assert not any(k in again[0] for k in ("fill", "fits", "sky_share")) and again[0]["variant"] == "base"


def test_the_build_passes_the_frame_check_on_its_exterior_model():
    """Source wiring (fails on BASE): build.main hands ``exterior.frame_check`` on its model to
    ``finish_agent_exterior_plans``."""
    src = inspect.getsource(B.main)
    assert "ext_points = E.building_points(model)" in src
    assert "frame=lambda p: E.frame_check(model, p[\"position\"], p[\"target\"], float(p[\"lens_mm\"]), ext_points," \
           in src


# --------------------------------------------------------------------------
# validate_camera_override: the eye-level lens and the sky
# --------------------------------------------------------------------------

def test_an_eye_level_exterior_lens_outside_24_28_mm_is_refused_unless_long_and_low():
    """The earlier review's open ask (docs/milestone13.md §14.13 "Not changed"); CLAUDE.md, user OK of 22 Oct 2026:
    a wider framing for long, low buildings only. Fails on BASE (no lens rule)."""
    box = _box(10.0, 8.0, levels=2)
    assert E.long_low(_model(box)) is None
    for lens in (18.0, 14.0, 35.0):
        got = X.validate_camera_override(box, _ext("ext_9", [5.0, -20.0, 1.6], [5.0, 4.0, 1.6], lens))
        assert not got["ok"] and any("outside the eye-level range 24-28 mm" in f for f in got["failed"]), lens
    for lens in (24.0, 26.0, 28.0, None):
        assert X.validate_camera_override(box, _ext("ext_9", [5.0, -20.0, 1.6], [5.0, 4.0, 1.6], lens))["ok"], lens
    low = _box(33.0, 15.0)
    assert E.long_low(_model(low)) is not None
    assert X.validate_camera_override(low, _ext("ext_9", [16.0, -25.0, 1.6], [16.0, 7.0, 1.6], 18.0))["ok"]
    # a high view is no eye-level view: its lens is not judged here
    assert X.validate_camera_override(box, _ext("ext_9", [5.0, -20.0, 12.0], [5.0, 4.0, 2.0], 18.0))["ok"]


def test_an_eye_level_exterior_pose_without_sky_is_refused():
    """CLAUDE.md: the sky, the sun and the horizon are always in the image. Fails on BASE (no sky rule)."""
    box = _box(10.0, 8.0, levels=2)
    near = X.validate_camera_override(box, _ext("ext_9", [5.0, -0.6, 1.6], [5.0, 4.0, 1.6]))
    assert not near["ok"] and len(near["failed"]) == 1 and near["failed"][0].startswith("no sky in the frame: 0%")
    assert X.validate_camera_override(box, _ext("ext_9", [5.0, -20.0, 1.6], [5.0, 4.0, 1.6]))["ok"]
    # a pose refused for a cheap reason gets no ray cast and no sky message (a camera in a wall sees no sky either)
    inside = X.validate_camera_override(box, _ext("ext_9", [5.0, 4.0, 1.6], [5.0, -4.0, 1.6]))
    assert not inside["ok"] and not any("no sky" in f for f in inside["failed"])
    assert X.eye_level_problems({}, [5.0, -0.6, 1.6], [5.0, 4.0, 1.6], 26.0) == []    # no model: nothing refused


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_the_strip_in_front_of_the_entrance_facade():
    """The committed real04 building: P6a's pose in the 5.7 m strip is refused (no sky); a 14 mm lens there is
    refused (real04 is not long and low); a 26 mm pose pitched 20 degrees up shows sky and passes (on P6a's building
    10 degrees up gave 11 %; the committed building's roof is higher), but X6 does not count it as frontal and gives
    the camera a major."""
    b = _read(REAL04)
    got = X.validate_camera_override(b, _ext("ext_front_entrance", *P6A_POSE))
    assert not got["ok"] and any(f.startswith("no sky in the frame: 0%") for f in got["failed"])
    wide = X.validate_camera_override(b, _ext("ext_9", P6A_POSE[0], [8.5, 12.5, 1.6], 14.0))
    assert not wide["ok"] and any("outside the eye-level range" in f for f in wide["failed"])
    up = [8.5, 12.5, 1.6 + 5.0 * math.tan(math.radians(20.0))]
    assert X.validate_camera_override(b, _ext("ext_9", P6A_POSE[0], up))["ok"]
    prep = X._prep(b)
    rec = X.camera_frame({"position": P6A_POSE[0], "target": up, "lens_mm": 26.0}, X.exterior_model(prep))
    assert rec["fits"] is False and rec["sky_share"] > E.SKY_MIN_SHARE
    cam = {"name": "ext_9", "kind": "exterior", "view": "agent", "policy": "agent", "position": P6A_POSE[0],
           "target": up, "lens_mm": 26.0}
    out = []
    X._x6(b, prep, {"cameras": [cam]}, None, out)
    assert any("no frontal view" in v["message"] for v in out)
    assert any(v["target"] == "ext_9" and v["severity"] == "major" and "frames only part" in v["message"]
               for v in out)


# --------------------------------------------------------------------------
# The real runs (not committed: skip without them)
# --------------------------------------------------------------------------

def _run(results: Path, project: str):
    return (_read(results / "furniture" / project / "building_final.json"),
            _read(results / "renders" / project / "scene_manifest.json"),
            _read(results / "agent" / project / "overrides.json"))


def _exterior_edits(overrides):
    for e in overrides.get("edits") or []:
        if e.get("tool") in ("set_camera", "add_camera") and (e.get("args") or {}).get("kind") == "exterior":
            yield dict(e["args"], action="set" if e["tool"] == "set_camera" else "add")


@pytest.mark.skipif(not (P6A / "agent" / "real04" / "overrides.json").is_file(), reason="P6a's run is not committed")
def test_p6a_ext_front_entrance_is_refused_and_x6_keeps_no_frontal_view():
    building, scene, overrides = _run(P6A, "real04")
    edits = list(_exterior_edits(overrides))
    front = [e for e in edits if e["view_id"] == "ext_front_entrance"]
    assert len(front) == 1 and front[0]["position"] == P6A_POSE[0] and front[0]["target"] == P6A_POSE[1]
    got = X.validate_camera_override(building, front[0])
    assert not got["ok"] and any(f.startswith("no sky in the frame: 0%") for f in got["failed"])
    for e in edits:                                                      # the agent's other pose (ext_5) stays
        if e["view_id"] != "ext_front_entrance":
            assert X.validate_camera_override(building, e)["ok"], e["view_id"]
    x6 = [v for v in X.check_exterior(building, scene, None)["violations"] if v["check"] == "X6"]
    assert any(v["target"] == "exterior" and "no frontal view of the entrance (+y) facade" in v["message"]
               for v in x6)
    own = [v for v in x6 if v["target"] == "ext_front_entrance" and v["severity"] == "major"]
    assert len(own) == 1 and "frames only part of the building" in own[0]["message"]
    assert "no sky in the frame" in own[0]["message"]
    assert own[0]["metrics"]["fill"] == pytest.approx(2.34, abs=0.01) and own[0]["metrics"]["sky_share"] == 0.0
    cam = next(c for c in scene["cameras"] if c["name"] == "ext_front_entrance")
    main = CV.main_facade_of(scene, building)
    assert CV.camera_role(cam, main) == "frontal"                        # the pose rule (BASE) ...
    assert CV.camera_role(cam, main, building=building) == "agent"       # ... and the frame it really has


@pytest.mark.skipif(not all((r / "agent").is_dir() for r in (P4A, P4B, P5)), reason="P4a/P4b/P5 runs not committed")
@pytest.mark.parametrize("results,project,frontal", [(P4A, "real02", "ext_6"), (P4B, "real03", "ext_6"),
                                                     (P5, "real04", None)])
def test_the_accepted_agent_poses_of_p4a_p4b_p5_stay_accepted(results, project, frontal):
    """Every exterior set / add the agent made on P4a's real02, P4b's real03 and P5's real04 passes the validator as
    before (17-47 % sky, 26 mm), and X6 adds no finding: real02's frontal ext_6 (the planner's) and real03's agent
    frontal ext_6 (fill 0.94, 41 % sky) stay the frontal view; P5's real04 had none (its X6 stays)."""
    building, scene, overrides = _run(results, project)
    edits = list(_exterior_edits(overrides))
    assert edits
    for e in edits:
        assert X.validate_camera_override(building, e) == {"ok": True, "failed": []}, (e["view_id"], e["position"])
    x6 = [v for v in X.check_exterior(building, scene, None)["violations"] if v["check"] == "X6"]
    assert not [v for v in x6 if "frames only part" in v["message"] or "no sky" in v["message"]]
    missing = [v for v in x6 if "no frontal view" in v["message"]]
    assert bool(missing) == (frontal is None)
    if frontal is not None:
        main = CV.main_facade_of(scene, building)
        cams = [c for c in scene["cameras"] if c["name"] == frontal and c.get("kind") == "exterior"]
        assert any(X.x6_frontal(c, main, model=X.exterior_model(X._prep(building))) for c in cams)
