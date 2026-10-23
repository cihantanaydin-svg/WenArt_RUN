"""Pass before P5 (17 Oct 2026; the review of the fix round after P4b), track A_agent.

What these tests pin (CPU only: MockModel, the fakes of ``test_agent_helpers``, synthetic cameras shaped like the
review's cases, and real04's committed building ``results/furniture/real04/building_decor.json`` with the camera
poses and the terrain record of P3, ``runs/20261016-172855-full``):

- decision 2 covers the frontal view by X6's own rule: an ``agent`` view square to the main facade keeps a frontal
  pose, the only such view is not removed, a corner camera the agent turned to the main facade keeps that role; the
  critic is told it is the frontal view and its "flat frontal, not a 3/4 corner" claim is dropped;
- the eye height is measured on the building's site as X6 and the validator measure it (real04's ``tin`` terrain
  record in the scene manifest has no surface), the critic is told it, the low-angle claim is dropped and an
  eye-height refusal names the ground and the z range;
- a ``set_exterior`` refused for an untouched vision finding gives the reason, through the loop;
- the exterior critic gets the round's scene (the loop wiring), and the room brief moves a no-spot piece's S2 to
  "not yours" (the ``room_brief`` wiring).

Round 2 (the review of this pass, P3's real04 log; real04's committed building and P3's camera records):

- the frontal role follows the label the next build gives a pose (``tools.next_view``: the planner's view and sides,
  ``agent.view_was`` / ``sides_was`` of a relabelled scene camera): a corner turned frontal is not set to a pose the
  build keeps a corner, unless another camera stays X6's frontal view, and that corner pose does not count when the
  agent's other frontal view is removed (checked against ``build.merge_agent_cameras`` +
  ``finish_agent_exterior_plans``);
- a height claim on the allowed aerial and site views is dropped with the reason (P3's 9 claims on ext_5 / ext_7),
  logged by the loop, and a set that would bring such a view down to eye level is refused.

Round 2, review (real04's committed building and P3's camera records):

- an aerial pose stands on or above the high-view line of the validator and X6 (``critic_vision.high_view_line``:
  ``ridge_z`` + 1.0 m, 7.01 m on real04): P3's round-6 spot of ext_5 (1.60 m over the ground) aimed 6 degrees down,
  and ext_7 the same way, are refused with both rules, and the critic keeps a height claim on a flagged record below
  the line;
- an exterior camera added in this session keeps its frontal role like a scene camera (``tools.added_camera``): the
  4-step real04 sequence (ext_4 frontal, ext_8 added frontal, ext_4 back to a corner, ext_8 added again at a corner
  pose) refuses the last add.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from test_agent_brief import fakes, toy
from test_agent_helpers import FakeEdits, jpg, project, write_json
from test_agent_loop_p4a import make
from test_agent_loop_p4b import EXT, FRONTAL, LOW_ANGLE, camera_project, cam, critique, x6
from test_m13_agent import FINISH, log_of
from wenart.agent import brief as BR
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_decor.json"

MAIN_Y = {"whole_building": {"main_facade": {"axis": "+y", "direction": [0.0, 1.0], "source": "entrance doors"}}}
# the review's case: no frontal ext_6 (real04's planner drops it), the agent's ext_8 square to the +y facade
AGENT_FRONTAL = {"name": "ext_8", "kind": "exterior", "room_id": None, "view": "agent", "sides": ["back"],
                 "position": [4.0, 20.0, 1.6], "target": [4.0, 3.5, 1.6], "lens_mm": 26.0, "policy": "agent"}
NO_FRONTAL = [c for c in EXT if c["name"] != "ext_6"]


# --------------------------------------------------------------------------
# decision 2: the frontal view by X6's rule
# --------------------------------------------------------------------------

def test_an_agent_view_square_to_the_main_facade_keeps_the_frontal_role(tmp_path):
    """Fails on adc3004: role_problem protected only the ``frontal`` / ``elevation`` labels, so the agent's frontal
    ext_8 (view ``agent``, the one X6 counts) was set to a corner pose and removed; code X6 "no frontal view" came back
    and the agent added a frontal view again (the P4b ping-pong, real04's case)."""
    ctx = camera_project(tmp_path, cameras=NO_FRONTAL + [AGENT_FRONTAL], scene_extra=MAIN_Y)
    reg = TL.build_registry()
    corner = reg.call(ctx, "set_camera", cam("ext_8", [18.0, 16.0, 1.6], [4.0, 3.5, 1.6]))
    assert not corner["accepted"] and corner["failed_checks"][0].startswith(
        "role: ext_8 is the frontal view and keeps its role")
    assert "main (+y) entrance facade, the frontal view X6 asks for" in corner["failed_checks"][0]
    gone = reg.call(ctx, "remove_camera", {"view_id": "ext_8", "reason": "a corner is better"})
    assert not gone["accepted"] and gone["failed_checks"][0].startswith("role: ext_8 is the only frontal view")
    assert ctx.tries["ext_8"] == 2
    # a pose still square to the main facade is a frontal pose
    assert reg.call(ctx, "set_camera", cam("ext_8", [4.0, 17.0, 1.6], [4.0, 3.5, 1.6]))["accepted"]
    # an agent view that is not square to the main facade has no role
    side = copy.deepcopy(dict(AGENT_FRONTAL, name="ext_9", position=[20.0, 4.0, 1.6], target=[4.0, 4.0, 1.6]))
    ctx2 = camera_project(tmp_path / "b", cameras=NO_FRONTAL + [AGENT_FRONTAL, side], scene_extra=MAIN_Y)
    assert TL.role_problem(ctx2, "remove", "ext_9", {}) is None
    assert TL.role_problem(ctx2, "set", "ext_9", cam("ext_9", [20.0, -10.0, 1.6], [4.0, 4.0, 1.6])) is None
    # another frontal view by X6's rule, added in this session, lets ext_8 go
    reg2 = TL.build_registry()
    assert reg2.call(ctx2, "add_camera", cam("ext_10", [-6.0, 24.0, 1.6], [2.0, 3.5, 1.6]))["accepted"]
    assert reg2.call(ctx2, "remove_camera", {"view_id": "ext_8", "reason": "ext_10 is the frontal view"})["accepted"]


def test_the_frontal_view_goes_only_while_x6_still_finds_one(tmp_path):
    """Fails on adc3004: the remove guard counted any other ``frontal`` / ``elevation`` label, so the frontal ext_6
    went while only an elevation of the -x facade stayed, and code X6 "no frontal view" came back. An elevation of
    another facade may still go while a frontal view stays."""
    elevation = {"name": "ext_9", "kind": "exterior", "room_id": None, "view": "elevation", "sides": ["left"],
                 "position": [-12.0, 5.0, 1.6], "target": [0.0, 5.0, 1.6], "lens_mm": 26.0}
    ctx = camera_project(tmp_path, cameras=EXT + [elevation], scene_extra=MAIN_Y)
    reg = TL.build_registry()
    gone = reg.call(ctx, "remove_camera", {"view_id": "ext_6", "reason": "the elevation is enough"})
    assert not gone["accepted"] and gone["failed_checks"][0].startswith("role: ext_6 is the only frontal view")
    assert reg.call(ctx, "remove_camera", {"view_id": "ext_9", "reason": "the frontal view is enough"})["accepted"]
    # without a main facade (no scene record, no site) the labels decide as before
    ctx2 = camera_project(tmp_path / "b", cameras=EXT + [elevation])
    assert CV.main_facade_of(ctx2.scene, ctx2.building) is None
    assert TL.role_problem(ctx2, "remove", "ext_9", {}) is None


def test_a_corner_turned_to_the_main_facade_is_the_frontal_view_of_the_next_build(tmp_path):
    """Fails on adc3004: a corner camera the agent set square to the main facade is labelled ``agent`` by the next
    build (``build.agent_exterior_view``) and is then X6's frontal view, but role_problem kept no role for it, so the
    next set turned it back into a corner."""
    ctx = camera_project(tmp_path, cameras=NO_FRONTAL, scene_extra=MAIN_Y)
    reg = TL.build_registry()
    assert TL.built_view(ctx, "ext_2")[0] == "corner"
    assert reg.call(ctx, "set_camera", cam("ext_2", [10.0, 24.0, 1.6], [10.0, 3.5, 1.6]))["accepted"]
    view, pose = TL.built_view(ctx, "ext_2")
    assert view == "agent" and pose["position"] == [10.0, 24.0, 1.6]
    back = reg.call(ctx, "set_camera", cam("ext_2", [20.0, -10.0, 1.45], [6.0, 1.5, 1.45]))
    assert not back["accepted"] and back["failed_checks"][0].startswith("role: ext_2 is the frontal view")
    gone = reg.call(ctx, "remove_camera", {"view_id": "ext_2", "reason": "drop it"})
    assert not gone["accepted"] and "only frontal view" in gone["failed_checks"][0]


def test_the_critic_is_told_an_agent_frontal_view_is_the_frontal_view(tmp_path):
    """Fails on adc3004: the critic was told "a view the agent placed" for the agent's frontal view and its "flat
    frontal elevation rather than a 3/4 corner view" claim was kept (cause exterior_camera: set_camera to a corner)."""
    res, prompt = critique(tmp_path, "ext_8", AGENT_FRONTAL, [FRONTAL], scene=dict(MAIN_Y, site={"terrain": {
        "kind": "flat", "z": {"+x": 0.0, "-x": 0.0, "+y": 0.0, "-y": 0.0}}}))
    assert "the one frontal view of the back (entrance) facade that X6 asks for" in prompt
    assert "a view the agent placed" not in prompt
    assert res["kept"] == [] and "ext_8 is the frontal view the camera policy requires" in res["dropped"][0]["dropped"]
    # the same agent camera at a corner pose keeps the claim
    turned = dict(AGENT_FRONTAL, position=[18.0, 16.0, 1.6])
    res, prompt = critique(tmp_path, "ext_8", turned, [FRONTAL], scene=MAIN_Y)
    assert [f["message"] for f in res["kept"]] == [FRONTAL] and "a view the agent placed" in prompt
    main = CV.main_facade_of(MAIN_Y)
    assert CV.camera_role(AGENT_FRONTAL, main) == "frontal" and CV.camera_role(turned, main) == "agent"
    assert CV.x6_frontal(dict(EXT[1]), None) and not CV.x6_frontal(AGENT_FRONTAL, None)
    assert P.camera_note(AGENT_FRONTAL, role="frontal").startswith("The camera of this view is the one frontal view")


# --------------------------------------------------------------------------
# real04: the tin terrain, the eye height and the frontal role on the committed building
# --------------------------------------------------------------------------

# P3 (runs/20261016-172855-full/results/renders/real04/scene_manifest.json): the terrain record and two corners
P3_TERRAIN = {"kind": "tin", "z": {"+x": -1.5558, "-x": -2.7042, "+y": -0.6927, "-y": -3.0}, "sides": [],
              "north_deg": 0.0, "north_source": "assumed (+Y is north: no north arrow)", "changes": []}
P3_EXT3 = {"name": "ext_3", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["right", "back"],
           "position": [23.0225, 23.6914, 2.8688], "target": [14.5915, 13.1478, 2.8688], "lens_mm": 26.0}
P3_EXT4 = {"name": "ext_4", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["left", "back"],
           "position": [-5.8495, 23.6914, 0.0517], "target": [2.5815, 13.1478, 0.0517], "lens_mm": 26.0}
P3_LOW = ("The camera is positioned at a low angle, looking up at the building, rather than at a standard eye level "
          "(1.5-1.7 m).")
# an agent frontal view between the entrance (+y) facade at y 12 and the copy b2 (y 18.6-30.6)
R04_FRONTAL = {"name": "ext_8", "kind": "exterior", "room_id": None, "view": "agent", "sides": ["back"],
               "position": [8.6, 17.5, 1.6], "target": [8.6, 6.0, 1.6], "lens_mm": 26.0, "policy": "agent"}


def real04_scene(cameras) -> dict:
    return {"cameras": copy.deepcopy(cameras), "site": {"terrain": copy.deepcopy(P3_TERRAIN)},
            "whole_building": {"main_facade": {"axis": "+y", "direction": [0.0, 1.0], "source": "entrance doors"}}}


def real04_ctx(tmp_path, cameras):
    out = tmp_path / "real04"
    out.mkdir(parents=True)
    (out / "building_decor.json").write_bytes(REAL04.read_bytes())
    write_json(out / "scene" / "scene_manifest.json", real04_scene(cameras))
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=LG.AgentLog(out, "real04", "m", "r"),
                               overrides=OV.Overrides(out), apply_edit=FakeEdits())


@pytest.fixture
def pose_rule(monkeypatch):
    """Fix round after P6a (22-23 Oct 2026; changed on purpose, the exterior track's ask): X6 counts an eye-level
    ``agent`` view square to the main facade as the frontal view only when it frames the whole building with the sky
    (``exterior_checks.x6_frontal``, which the camera-role guards read through ``tools.x6_frontal_of``), and the camera
    validator refuses an eye-level pose without sky (``exterior_checks.eye_level_problems``); both are pinned in
    tests/test_m13_p6a_exterior.py and tests/test_m13_p6a_integration.py. real04's strip between the entrance (+y)
    facade (y 12) and the copy b2 (y 18.6) holds no such pose at 24-28 mm (POSE_A: 2.34 frame widths, 0 % sky; POSE_B
    2 %; R04_ADDED 0.4 %), and decision 16 (real04's frontal view) is open. These tests pin the camera-role guards on
    the labels the next build gives, so they switch the frame measure off: without an exterior model a pose keeps the
    pose rule and the validator refuses nothing for the sky (the rule for a plan whose frame cannot be measured)."""
    from wenart.blender import exterior_checks as X

    monkeypatch.setattr(X, "exterior_model", lambda prep: None)


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_eye_height_is_measured_on_the_building_site(tmp_path):
    """Fails on adc3004: camera_eye read the scene manifest's terrain, and real04's tin record has no surface, so no
    eye height was known for any of its exterior cameras (P3); the critic was not told 1.60 m, P3's "low angle,
    looking up" on ext_3 (z 2.87 over the ground at 1.27) was kept, and an eye-height refusal named no ground."""
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    scene = real04_scene([P3_EXT3, P3_EXT4])
    assert CV.scene_ground_z(scene, 23.0225, 23.6914) is None            # the manifest record cannot answer
    eye = CV.camera_eye(P3_EXT3, scene, b)
    assert eye["eye_m"] == pytest.approx(1.6, abs=0.005) and eye["ground_z"] == pytest.approx(1.269, abs=0.01)
    assert CV.camera_eye(P3_EXT4, scene, b)["eye_m"] == pytest.approx(1.6, abs=0.005)
    model = MM.MockModel(critic=[{"findings": [x6(P3_LOW, "ext_3")]}])
    res = CV.critique_exterior(model, b, "ext_3", preview=jpg(tmp_path / "ext_3_preview.jpg"), plan_crop=None,
                               code={"findings": [], "ran": []}, call_id="t", camera=P3_EXT3, scene=scene)
    assert "Measured by code: the eye is 1.60 m above the ground" in json.dumps(model.critic_requests()[0])
    assert res["kept"] == [] and res["dropped"][0]["dropped"].startswith("code contradicts: eye 1.60 m")
    # the real validator refuses 1.6 m absolute at the front (ground -2.77): the hint names the ground and the range
    ctx = real04_ctx(tmp_path, [P3_EXT3, P3_EXT4])
    refused = TL.build_registry().call(ctx, "add_camera", cam("ext_9", [8.5, -14.0, 1.6], [8.5, 6.0, 1.6]))
    assert not refused["accepted"] and refused["failed_checks"][0].startswith("eye height 4.37 m above the ground")
    assert refused["failed_checks"][-1] == ("the ground at (8.5, -14) is at z -2.77 m: use z -1.27 to -1.07 for an "
                                            "eye-level view")


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_the_agents_frontal_view_keeps_its_role(tmp_path, pose_rule):
    """Fails on adc3004: real04 has no planner frontal view (P3 dropped ext_6), so the agent's frontal view is
    ``agent``; a set to ext_3's corner pose and a remove were accepted."""
    # fix round after P6a (changed on purpose): the frame measure is off here (``pose_rule``: real04's strip has no
    # eye-level pose with sky); the role guards these lines pin are unchanged
    ctx = real04_ctx(tmp_path, [P3_EXT3, P3_EXT4, R04_FRONTAL])
    reg = TL.build_registry()
    corner = reg.call(ctx, "set_camera", cam("ext_8", P3_EXT3["position"], P3_EXT3["target"]))
    assert not corner["accepted"] and corner["failed_checks"][0].startswith("role: ext_8 is the frontal view")
    gone = reg.call(ctx, "remove_camera", {"view_id": "ext_8", "reason": "two facades are better"})
    assert not gone["accepted"] and gone["failed_checks"][0].startswith("role: ext_8 is the only frontal view")
    assert TL.role_problem(ctx, "set", "ext_3", cam("ext_3", [24.0, 24.0, 2.9], [14.6, 13.1, 2.9])) is None
    # a scene without the record: the main facade of the building's own plan (build.prepare: the entrance doors)
    main = CV.main_facade_of({}, ctx.building)
    assert main["axis"] == "+y" and main["source"] == "entrance doors"
    assert CV.x6_frontal(R04_FRONTAL, main) and not CV.x6_frontal(dict(P3_EXT3, view="agent"), main)


# --------------------------------------------------------------------------
# the loop: the reason of a set_exterior refusal, the exterior critic's scene
# --------------------------------------------------------------------------

NO_PATH = {"check": "X4", "severity": "major", "target": "ext_1",
           "message": "no visible path to the entrance, only grass", "evidence_image": 1}
SUN_40 = {"tool_calls": [{"name": "set_exterior", "arguments": {"sun": {"elevation_deg": 40.0},
                                                                 "reason": "a warmer light on the entrance"}}]}
FLAT_0 = {"kind": "flat", "z": {"+x": 0.0, "-x": 0.0, "+y": 0.0, "-y": 0.0}}


def test_the_loop_gives_the_reason_and_the_critic_the_scene(tmp_path):
    """Fails on adc3004 (the reason) and on the mutation ``scene=None`` in run_vision_critic (the scene): a sun edit
    for the vision X4 "no path" was refused "finding X4:ext_1 is still there" with no reason (changed_targets leaves
    ext_1 out of ``changed``, so after_findings kept it through the "target not changed" branch); the exterior
    critic's measured eye height comes from the round's scene (the toy building has no site)."""
    loop, out, model = make(tmp_path, [SUN_40, FINISH], [[]], vision=True, max_rounds=1,
                            critic=[{"findings": []}, {"findings": []},
                                    {"findings": [dict(NO_PATH), x6(LOW_ANGLE, "ext_1")]}])
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text())
    scene["site"] = {"terrain": dict(FLAT_0)}
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene))
    loop.run()
    prompt = json.dumps(model.critic_requests()[2])
    assert "Exterior view ext_1" in prompt and "Measured by code: the eye is 1.60 m above the ground" in prompt
    events = log_of(out)["events"]
    x6s = [e for e in events if e["kind"] == "finding" and e["checklist"] == "X6"]
    assert len(x6s) == 1 and x6s[0]["dropped"].startswith("code contradicts: eye 1.60 m above the ground")
    edits = [e for e in events if e["kind"] in ("edit", "rejected_edit") and e["tool"] == "set_exterior"]
    assert [e["kind"] for e in edits] == ["rejected_edit"], edits
    text = json.dumps(edits[0])
    assert "finding X4:ext_1 is still there after the edit (the edit does not change what the finding is about " \
           "(the override sets sun; the cause site needs site or ground)" in text


def test_after_findings_gives_the_reason_only_to_the_target(tmp_path):
    """Pass before P5: the reason goes to the edit's target (``targets``) whatever ``changed`` holds; another vision
    finding the override does not touch keeps its message (an accepted edit's list becomes the round's)."""
    from wenart.agent import causes as CS
    from wenart.agent import loop as LP
    x4 = dict(NO_PATH, id="v:1", source="vision", room_id=None, cause="site")
    other = dict(x4, id="v:2", target="ext_2", message="no hedge along the plot")
    sun = {"sun": {"elevation_deg": 40.0}}
    changed = TL.changed_targets("set_exterior", dict(sun, reason="x"), {}, [x4], findings=[x4, other])
    kept = {f["target"]: f for f in LP.after_findings([], [x4, other], changed, {}, override=sun, targets=[x4])}
    assert kept["ext_1"]["message"].startswith("the edit does not change what the finding is about")
    assert kept["ext_2"]["message"] == "no hedge along the plot"
    ok, why = LP.accept_edit([x4, other], list(kept.values()), {"target_finding": [x4]})
    assert not ok and "does not change what the finding is about" in why
    # without targets (an older caller) nothing changes: the finding stays, without the reason
    plain = LP.after_findings([], [x4], changed, {}, override=sun)
    assert [CS.finding_key(f) for f in plain] == [("X4", "ext_1")] and plain[0]["message"] == x4["message"]


# --------------------------------------------------------------------------
# room_brief: the no-spot routing
# --------------------------------------------------------------------------

NO_SPOT = "fixture_place: f2: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d1)"


def test_room_brief_moves_a_no_spot_pieces_wall_cut_to_not_yours(tmp_path):
    """Fails on the mutation that drops the ``no_spot_findings`` call in room_brief (the P4b test called it
    directly): after the code's fix_fixture search found no spot for f2, its S2 is "not yours" with the reason, not
    a fixable step that every later round refuses and counts as a try."""
    out = project(tmp_path)
    mem = MEM.Memory(out)
    mem.record("r1", 1, "fix_fixture", {"piece_id": "f2", "reason": "through the wall"},
               {"accepted": False, "failed_checks": [NO_SPOT]})
    s2 = {"id": "c:S2:f2", "check": "S2", "severity": "major", "target": "f2", "room_id": "r1",
          "message": "f2 cuts wall w4 by 0.06 m", "metrics": {"wall_id": "w4", "depth": 0.06}}
    without = BR.room_brief(toy(), "r1", findings=[dict(s2)], memory=MEM.Memory(project(tmp_path / "b")), **fakes())
    assert [f["id"] for f in without["findings"]["fixable"]] == ["c:S2:f2"]
    brief = BR.room_brief(toy(), "r1", findings=[dict(s2)], memory=mem, **fakes())
    assert "c:S2:f2" not in [f["id"] for f in brief["findings"]["fixable"]]
    moved = [f for f in brief["findings"]["not_yours"] if f["id"] == "c:S2:f2"]
    assert len(moved) == 1 and "no valid spot within 0.5 m for f2 (fix_fixture, round 1)" in moved[0]["why"]


# --------------------------------------------------------------------------
# pass before P5, round 2 (review of the pass): the frontal role by the next build's label, the allowed aerials
# --------------------------------------------------------------------------

P3_EXT1 = {"name": "ext_1", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["left", "front"],
           "position": [-5.8495, -11.6912, -2.5414], "target": [2.5802, -1.1466, -2.5414], "lens_mm": 26.0}
P3_EXT2 = {"name": "ext_2", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["right", "front"],
           "position": [23.0225, -11.6912, -0.7169], "target": [14.5926, -1.1468, -0.7169], "lens_mm": 26.0}
P3_EXT5 = {"name": "ext_5", "kind": "exterior", "room_id": None, "view": "aerial", "sides": ["right", "back"],
           "position": [29.273, 22.1488, 17.1562], "target": [9.0224, 5.4568, 2.0046], "lens_mm": 26.87,
           "aerial_allowed": True}
P3_EXT7 = {"name": "ext_7", "kind": "exterior", "room_id": None, "view": "aerial", "sides": [],
           "position": [44.0704, 14.0365, 11.8884], "target": [8.5825, 14.0292, 3.5046], "lens_mm": 24.0,
           "aerial_allowed": True, "site_view": True, "horizon_frac": 0.78}
P3_EXTERIOR = [P3_EXT1, P3_EXT2, P3_EXT3, P3_EXT4, P3_EXT5, P3_EXT7]
# the review's poses: A square to the entrance (+y) facade, B 25.8 degrees off its normal and within 80 degrees of the
# left (-x) facade's normal too, so the build keeps ext_4 the corner view of left, back
POSE_A = ([8.6, 17.5, 1.6], [8.6, 6.0, 1.6])
POSE_B = ([4.0, 17.5, 1.6], [8.6, 8.0, 1.6])
# an agent frontal view added in round 1 (between the entrance facade and the copy b2, 10 m from POSE_B)
R04_ADDED = dict(R04_FRONTAL, position=[14.0, 17.5, 1.6], target=[10.0, 6.0, 1.6])
R04_FRONTAL_POSE = (R04_FRONTAL["position"], R04_FRONTAL["target"])
# P3's 9 vision X6 claims on the allowed aerial views (log seq 291-2464): "high angle, not at eye level"
P3_AERIAL_CLAIMS = [
    (291, "ext_5", ("The camera is positioned at a high angle looking down at the building, not at eye level (1.5-1.7 "
                    "m). This makes the roof the dominant feature and distorts the perception of the facade and ground "
                    "level.")),
    (292, "ext_7", ("The camera is positioned at a high angle looking down at the building, not at eye level (1.5-1.7 "
                    "m). This makes the roof the dominant feature and distorts the perception of the facade and ground "
                    "plane.")),
    (741, "ext_7", ("The camera is positioned at a high angle looking down at the building, rather than at the "
                    "required eye level (1.5-1.7 m). This results in a distorted perspective where the roof is "
                    "disproportionately large and the vertical lines of the building are not straight.")),
    (1172, "ext_5", ("The camera is positioned at a high angle looking down at the building, not at the required eye "
                     "level of 1.5-1.7 m.")),
    (1173, "ext_7", ("The camera is positioned at a high angle looking down at the building, not at the required eye "
                     "level of 1.5-1.7 m.")),
    (1599, "ext_5", ("The camera is positioned at a high angle looking down at the building, not at the required eye "
                     "level of 1.5-1.7 m.")),
    (1600, "ext_7", ("The camera is positioned at a high angle looking down at the building, not at eye level (1.5-1.7 "
                     "m). This results in a distorted perspective where the vertical lines of the building are not "
                     "straight and the roof is disproportionately large.")),
    (2463, "ext_5", ("The camera is positioned at a high angle looking down at the building, not at the required eye "
                     "level of 1.5-1.7 m.")),
    (2464, "ext_7", ("The camera is positioned at a high angle looking down at the building, not at eye level (1.5-1.7 "
                     "m). This results in a distorted perspective where the vertical lines of the building are not "
                     "straight and the ground plane is overly prominent.")),
]


def build_label(planned: dict, entries: list) -> dict:
    """The plan the build makes of the planner's camera ``planned`` with the agent's camera ``entries``
    (``build.merge_agent_cameras`` + ``build.finish_agent_exterior_plans``, as real04's build does)."""
    from wenart.blender import build as B
    plans, _ = B.merge_agent_cameras([], [copy.deepcopy(planned)], copy.deepcopy(entries))
    B.finish_agent_exterior_plans(plans, "base", (0.0, 0.0), 0.0, False)
    return plans[0]


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_a_corner_turned_frontal_is_not_set_to_a_pose_the_build_keeps_a_corner(tmp_path, pose_rule):
    """Fails on ceb3804 (review of the pass before P5, major): the frontal-role guard checked only that the new pose
    faces the main facade (``exterior_checks._faces``). real04's corner ext_4 (left, back; back is the entrance +y
    facade) was set square to it (POSE_A, labelled ``agent``: X6's frontal view), then set to POSE_B, 25.8 degrees off
    the +y normal; the build re-applies both sets to the planner's corner and keeps it the corner of left, back, so
    code X6 "no frontal view of the entrance (+y) facade" came back. The second set is refused now, unless another
    camera stays X6's frontal view."""
    # fix round after P6a (changed on purpose): the frame measure is off here (``pose_rule``: real04's strip has no
    # eye-level pose with sky); the role guards these lines pin are unchanged
    ctx = real04_ctx(tmp_path, P3_EXTERIOR)
    reg = TL.build_registry()
    main = CV.main_facade_of(ctx.scene, ctx.building)
    assert reg.call(ctx, "set_camera", cam("ext_4", *POSE_A))["accepted"]
    assert TL.built_view(ctx, "ext_4")[0] == "agent" and TL.x6_frontal_now(ctx, "ext_4", main)
    turned = reg.call(ctx, "set_camera", cam("ext_4", *POSE_B))
    assert not turned["accepted"] and turned["failed_checks"][0].startswith(
        "role: ext_4 is the frontal view and keeps its role")
    assert "the next build keeps this pose the corner view of left, back" in turned["failed_checks"][0]
    assert "main (+y) entrance facade" in turned["failed_checks"][0]
    # the guard says what the build does: the planner's ext_4 with the two sets is the corner, not X6's frontal view
    entries = [dict(cam("ext_4", *pose), action="set") for pose in (POSE_A, POSE_B)]
    built = build_label(P3_EXT4, entries)
    assert built["view"] == "corner" and built["sides"] == ["left", "back"] and not CV.x6_frontal(built, main)
    assert TL.next_view(ctx, "ext_4", cam("ext_4", *POSE_B))[0] == "corner"
    assert build_label(P3_EXT4, entries[:1])["view"] == "agent"
    # a pose square to the +y facade and more than 80 degrees off the -x normal stays X6's frontal view
    assert reg.call(ctx, "set_camera", cam("ext_4", [7.0, 17.5, 1.6], [8.0, 6.0, 1.6]))["accepted"]
    # another camera that stays X6's frontal view lets ext_4 go back to a corner pose
    ctx2 = real04_ctx(tmp_path / "b", P3_EXTERIOR + [R04_ADDED])
    reg2 = TL.build_registry()
    assert reg2.call(ctx2, "set_camera", cam("ext_4", *POSE_A))["accepted"]
    assert reg2.call(ctx2, "set_camera", cam("ext_4", *POSE_B))["accepted"]


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_the_next_build_label_starts_from_the_planners_view(tmp_path, pose_rule):
    """Fails on ceb3804 (review of the pass before P5, round 2): after round 1 the scene's ext_4 is ``agent`` with
    ``agent.view_was`` corner and ``sides_was`` left, back; built_view took the scene's ``agent`` as the base while the
    build re-applies the overrides to the planner's corner, so POSE_B counted as frontal, the set was accepted and the
    remove guard let the agent's added frontal ext_8 go: no frontal view was left."""
    # fix round after P6a (changed on purpose): the frame measure is off here (``pose_rule``: real04's strip has no
    # eye-level pose with sky); the role guards these lines pin are unchanged
    relabelled = dict(P3_EXT4, view="agent", sides=["back"], position=POSE_A[0], target=POSE_A[1], policy="agent",
                      agent={"action": "set", "view_was": "corner", "sides_was": ["left", "back"]})
    cams = [c for c in P3_EXTERIOR if c["name"] != "ext_4"] + [relabelled, R04_ADDED]
    ctx = real04_ctx(tmp_path, cams)
    ctx.overrides.add(1, "set_camera", cam("ext_4", *POSE_A), {"accepted": True})
    ctx.overrides.add(1, "add_camera", cam("ext_8", R04_ADDED["position"], R04_ADDED["target"]), {"accepted": True})
    main = CV.main_facade_of(ctx.scene, ctx.building)
    assert TL.built_view(ctx, "ext_4")[0] == "agent" and TL.x6_frontal_now(ctx, "ext_8", main)
    reg = TL.build_registry()
    assert reg.call(ctx, "set_camera", cam("ext_4", *POSE_B))["accepted"]      # ext_8 stays X6's frontal view
    view, pose = TL.built_view(ctx, "ext_4")
    assert view == "corner" and pose["sides"] == ["left", "back"] and not TL.x6_frontal_now(ctx, "ext_4", main)
    entries = [e for e in ctx.overrides.agent_overrides()["cameras"] if e["view_id"] == "ext_4"]
    assert build_label(P3_EXT4, entries)["view"] == view                         # = the build
    gone = reg.call(ctx, "remove_camera", {"view_id": "ext_8", "reason": "ext_4 is the frontal view"})
    assert not gone["accepted"] and gone["failed_checks"][0].startswith("role: ext_8 is the only frontal view")


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_a_height_claim_on_the_allowed_aerial_views_is_dropped_and_never_lowers_them(tmp_path):
    """Fails on ceb3804 (P3's observation): 9 vision X6 claims "high angle, not at eye level" on real04's allowed
    aerial views (ext_5 aerial_allowed, ext_7 aerial_allowed + site_view; P3 rounds 1-6) were kept with the cause
    exterior_camera, and P3's round-6 set_camera brought ext_5 down to eye level (z 2.46, accepted). A code record
    outranks AI vision: the allowed aerial is a design choice (docs/milestone13.md D8, the site view rule), so the
    claim is dropped with the reason, and a set that would bring an allowed aerial to eye level is refused."""
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    scene = real04_scene(P3_EXTERIOR)
    cams = {c["name"]: c for c in P3_EXTERIOR}
    for seq, view, message in P3_AERIAL_CLAIMS:
        model = MM.MockModel(critic=[{"findings": [x6(message, view)]}])
        res = CV.critique_exterior(model, b, view, preview=jpg(tmp_path / f"{view}_{seq}.jpg"), plan_crop=None,
                                   code={"findings": [], "ran": []}, call_id=f"r{seq}", camera=cams[view], scene=scene)
        what = "site view" if view == "ext_7" else "aerial view"
        assert res["kept"] == [], (seq, res)
        assert res["dropped"][0]["dropped"].startswith(
            f"code contradicts: {view} is the {what} the camera policy allows"), (seq, res["dropped"])
        assert "docs/milestone13.md D8" in res["dropped"][0]["dropped"]
    # the claim stays on a camera without the flags, and with a kind the record does not answer
    eye = CV.camera_eye(P3_EXT5, scene, b)
    plain = dict(P3_EXT5, view="agent", aerial_allowed=None)
    kept, dropped = CV.drop_camera_claims([dict(x6(P3_AERIAL_CLAIMS[0][2], "ext_5"))], [], "ext_5", plain, eye,
                                          {"findings": []})
    assert len(kept) == 1 and dropped == []
    # a flagged record on a level pose is no aerial pose (the build's rule: 5 degrees down at least)
    flat = dict(P3_EXT5, position=[29.3739, 22.2276, 4.0], target=[8.9821, 5.5057, 4.0])
    assert CV.allowed_aerial(flat, building=b) is None and CV.allowed_aerial(P3_EXT5, building=b) == "aerial view"
    # round 2, review: without the building the measured eye height decides; without either the height is unknown
    assert CV.allowed_aerial(P3_EXT5, eye) == "aerial view" and CV.allowed_aerial(P3_EXT5) is None
    kept, _ = CV.drop_camera_claims([x6(P3_AERIAL_CLAIMS[0][2], "ext_5")], [], "ext_5", flat,
                                    CV.camera_eye(flat, scene, b), {"findings": []})
    assert len(kept) == 1
    cut = "A high angle looking down, and the building is cut off at the left edge."
    kept, _ = CV.drop_camera_claims([x6(cut, "ext_5")], [], "ext_5", P3_EXT5, eye, {"findings": []})
    assert len(kept) == 1
    # never lowered: P3's accepted round-6 pose of ext_5 (z 2.46, level) and ext_7 at eye level are refused (both
    # pass the validator)
    ctx = real04_ctx(tmp_path / "tools", P3_EXTERIOR)
    reg = TL.build_registry()
    low = reg.call(ctx, "set_camera", cam("ext_5", [29.3739, 22.2276, 2.46], [8.9821, 5.5057, 2.46], lens_mm=26.75))
    assert not low["accepted"] and low["failed_checks"][0].startswith(
        "role: ext_5 is the aerial view the camera policy allows and keeps its role")
    # P3's eye-level try of ext_7 at the z the eye-height hint names (ground -0.37 m: z 1.23), valid on ceb3804
    level = reg.call(ctx, "set_camera", cam("ext_7", [40.779, 14.0358, 1.23], [8.5825, 14.0292, 1.23], lens_mm=24))
    assert not level["accepted"] and level["failed_checks"][0].startswith(
        "role: ext_7 is the site view the camera policy allows and keeps its role")
    assert ctx.tries["ext_5"] == 1 and ctx.tries["ext_7"] == 1
    # an aerial pose stays allowed: the role is the height, not the place
    assert TL.role_problem(ctx, "set", "ext_5", cam("ext_5", [30.0, 23.0, 18.0], [9.0, 5.5, 2.0])) is None
    assert TL.role_problem(ctx, "remove", "ext_5", {}) is None
    # P3's round 6 as the build records it now: ext_5 at z 2.46 is "agent" and its flag was dropped (flags_was); the
    # agent may raise it again, and the raised pose is the planner's allowed aerial for the next build, kept so
    lowered = dict(P3_EXT5, view="agent", position=[29.3739, 22.2276, 2.46], target=[8.9821, 5.5057, 2.46],
                   policy="agent", agent={"action": "set", "view_was": "aerial", "sides_was": ["right", "back"],
                                          "flags_was": {"aerial_allowed": True}})
    lowered.pop("aerial_allowed")
    ctx2 = real04_ctx(tmp_path / "round7", [c for c in P3_EXTERIOR if c["name"] != "ext_5"] + [lowered])
    ctx2.overrides.add(6, "set_camera", cam("ext_5", lowered["position"], lowered["target"], lens_mm=26.75),
                       {"accepted": True})
    assert TL.role_problem(ctx2, "set", "ext_5", cam("ext_5", [29.0, 22.0, 2.46], [9.0, 5.5, 2.46])) is None
    reg2 = TL.build_registry()
    assert reg2.call(ctx2, "set_camera", cam("ext_5", P3_EXT5["position"], P3_EXT5["target"], lens_mm=26.87))[
        "accepted"]
    view, plan = TL.built_view(ctx2, "ext_5")
    assert view == "aerial" and plan["aerial_allowed"] is True
    again = reg2.call(ctx2, "set_camera", cam("ext_5", lowered["position"], lowered["target"], lens_mm=26.75))
    assert not again["accepted"] and again["failed_checks"][0].startswith("role: ext_5 is the aerial view")


def test_the_loop_logs_the_dropped_aerial_height_claim(tmp_path):
    """Fails on ceb3804: the loop kept the vision X6 "high angle, not at eye level" on an allowed aerial view (cause
    exterior_camera, set_camera offered); now it is logged as dropped with the code's reason and is no work."""
    loop, out, _model = make(tmp_path, [FINISH], [[]], vision=True, max_rounds=1,
                             critic=[{"findings": []}, {"findings": []},
                                     {"findings": [x6(P3_AERIAL_CLAIMS[3][2], "ext_1")]}])
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text())
    scene["cameras"][2] = dict(scene["cameras"][2], view="aerial", aerial_allowed=True, position=[-20.0, -20.0, 18.0],
                               target=[4.0, 2.0, 1.6])
    scene["site"] = {"terrain": dict(FLAT_0)}
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene))
    loop.run()
    events = log_of(out)["events"]
    x6s = [e for e in events if e["kind"] == "finding" and e["checklist"] == "X6" and e.get("source") == "vision"]
    assert len(x6s) == 1 and x6s[0]["dropped"].startswith(
        "code contradicts: ext_1 is the aerial view the camera policy allows"), x6s


# --------------------------------------------------------------------------
# pass before P5, round 2, review: the high-view line of the allowed aerials, the in-session added camera's role
# --------------------------------------------------------------------------

def eye_z(b: dict, x: float, y: float, eye: float = 1.6) -> float:
    """The z of a camera ``eye`` m over real04's ground at ``(x, y)`` (the validator's ground, ``CV.ground_z``)."""
    return round(CV.ground_z(b, None, x, y) + eye, 4)


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_an_eye_level_pose_looking_down_is_no_aerial_view(tmp_path):
    """Fails on the round-2 tree (review of round 2, major): the aerial guard checked only the 5-degree pitch, so
    real04's ext_5 set at P3's round-6 spot 1.60 m over the ground and aimed 6 degrees down was accepted (the
    validator passes an eye height of 1.60 m), the build kept it ``aerial`` with ``aerial_allowed`` and the critic
    dropped a vision claim "at eye level looking down" on it. The guard now uses the validator's and X6's own line
    too: a camera below ``ridge_z + 1.0`` (7.01 m on real04) is an eye-level view; the refusal states both rules, and
    the critic drops a height claim only for a pose above that line."""
    from wenart.blender import build as B
    from wenart.blender import exterior_checks as X

    b = json.loads(REAL04.read_text(encoding="utf-8"))
    ctx = real04_ctx(tmp_path, P3_EXTERIOR)
    reg = TL.build_registry()
    low5 = cam("ext_5", [29.3739, 22.2276, 2.458], [8.9821, 5.5057, -0.314], lens_mm=26.87)
    # the pose is valid on its own and the build's aerial rule (5 degrees down) still calls it aerial
    assert X.validate_camera_override(b, dict(low5, action="set"))["ok"]
    assert B._down_pitch_deg(low5["position"], low5["target"]) == pytest.approx(6.0, abs=0.01)
    assert TL.next_view(ctx, "ext_5", low5)[0] == "aerial"
    refused = reg.call(ctx, "set_camera", low5)
    assert not refused["accepted"], refused
    why = refused["failed_checks"][0]
    assert why.startswith("role: ext_5 is the aerial view the camera policy allows and keeps its role")
    assert "an aerial view stands at least 1 m above the ridge (z 7.01 m or more; the ridge is at 6.01 m) and " \
           "looks down at least 5 degrees" in why
    assert "this pose stands at z 2.46 m, below that line (the camera validator and code X6 judge it as an " \
           "eye-level view)" in why
    assert "degrees down, less than" not in why            # the pitch is not the problem here
    ridge, line = CV.high_view_line(b)                     # = exterior_checks: validate_camera_override and _x6
    assert ridge == pytest.approx(6.01, abs=0.005) and line == pytest.approx(ridge + 1.0)
    # ext_7 (the site view) the same way: 1.60 m over the ground, 6 degrees down
    z7 = eye_z(b, 40.779, 14.0358)
    low7 = cam("ext_7", [40.779, 14.0358, z7], [8.5825, 14.0292, -2.1505], lens_mm=24)
    assert X.validate_camera_override(b, dict(low7, action="set"))["ok"]
    assert TL.next_view(ctx, "ext_7", low7)[0] == "aerial"
    refused7 = reg.call(ctx, "set_camera", low7)
    assert not refused7["accepted"] and refused7["failed_checks"][0].startswith(
        "role: ext_7 is the site view the camera policy allows and keeps its role")
    # above the line but level: the pitch rule, stated with the height rule
    level = TL.role_problem(ctx, "set", "ext_5", cam("ext_5", [30.0, 23.0, 9.0], [9.0, 5.5, 9.0]))
    assert "this pose looks 0.0 degrees down, less than the 5 degrees" in level
    assert "an aerial view stands at least 1 m above the ridge" in level and "below that line" not in level
    # an aerial pose above the line stays allowed
    assert TL.role_problem(ctx, "set", "ext_5", cam("ext_5", [30.0, 23.0, 18.0], [9.0, 5.5, 2.0])) is None
    assert reg.call(ctx, "set_camera", cam("ext_5", [30.0, 23.0, 18.0], [9.0, 5.5, 2.0], lens_mm=26.87))["accepted"]
    # the critic: a height claim on the flagged record at the eye-level pose is no longer answered by the policy
    scene = real04_scene(P3_EXTERIOR)
    built_low = dict(P3_EXT5, position=low5["position"], target=low5["target"])      # what the build keeps
    assert CV.allowed_aerial(built_low, building=b) is None
    assert CV.allowed_aerial(P3_EXT5, building=b) == "aerial view"
    assert CV.allowed_aerial(P3_EXT7, building=b) == "site view"
    claim = "The camera is at eye level looking down at the building, not an aerial view."
    model = MM.MockModel(critic=[{"findings": [x6(claim, "ext_5")]}, {"findings": [x6(claim, "ext_5")]}])
    res = CV.critique_exterior(model, b, "ext_5", preview=jpg(tmp_path / "ext_5_low.jpg"), plan_crop=None,
                               code={"findings": [], "ran": []}, call_id="low", camera=built_low, scene=scene)
    assert [f["message"] for f in res["kept"]] == [claim] and res["dropped"] == []
    res = CV.critique_exterior(model, b, "ext_5", preview=jpg(tmp_path / "ext_5_high.jpg"), plan_crop=None,
                               code={"findings": [], "ran": []}, call_id="high", camera=P3_EXT5, scene=scene)
    assert res["kept"] == [] and res["dropped"][0]["dropped"].startswith(
        "code contradicts: ext_5 is the aerial view the camera policy allows")
    # the critic judges by the building's line, not by the eye height alone: a flagged record 4.1 m over the ground
    # and 10 degrees down (above the eye-level band, below the line 7.01 m) keeps the claim
    mid = dict(P3_EXT5, position=[29.3739, 22.2276, 5.0], target=[8.9821, 5.5057, 0.35])
    mid_eye = CV.camera_eye(mid, scene, b)
    assert mid_eye["eye_m"] == pytest.approx(4.14, abs=0.01) and mid_eye["pitch_deg"] == pytest.approx(-10.0, abs=0.05)
    assert CV.allowed_aerial(mid, mid_eye) == "aerial view" and CV.allowed_aerial(mid, mid_eye, building=b) is None
    model = MM.MockModel(critic=[{"findings": [x6(P3_AERIAL_CLAIMS[3][2], "ext_5")]}])
    res = CV.critique_exterior(model, b, "ext_5", preview=jpg(tmp_path / "ext_5_mid.jpg"), plan_crop=None,
                               code={"findings": [], "ran": []}, call_id="mid", camera=mid, scene=scene)
    assert [f["message"] for f in res["kept"]] == [P3_AERIAL_CLAIMS[3][2]] and res["dropped"] == []


@pytest.mark.skipif(not REAL04.is_file(), reason="results/furniture/real04 not committed")
def test_real04_a_camera_added_in_this_session_keeps_its_frontal_role(tmp_path, pose_rule):
    """Fails on the round-2 tree (review of round 2: a major and a minor finding): role_problem returned None for a
    camera that is not in the scene manifest, so a camera added in this session had no role guard. The frontal set
    exception ("another camera stays X6's frontal view") trusted such a camera: ext_4 set frontal, ext_8 added
    frontal, ext_4 set to a corner pose (allowed: ext_8 is frontal), then ext_8 added again at a corner pose; the
    last add was accepted and the build had no frontal view (code X6 "no frontal view of the entrance (+y)
    facade"). An in-session added exterior camera is now guarded like a scene camera."""
    # fix round after P6a (changed on purpose): the frame measure is off here (``pose_rule``: real04's strip has no
    # eye-level pose with sky); the role guards these lines pin are unchanged
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    ctx = real04_ctx(tmp_path, P3_EXTERIOR)
    reg = TL.build_registry()
    main = CV.main_facade_of(ctx.scene, ctx.building)
    z8, z8b = eye_z(b, 14.0, 17.5), eye_z(b, 20.0, 17.5)
    # 1. ext_4 turned square to the entrance facade
    assert reg.call(ctx, "set_camera", cam("ext_4", *POSE_A))["accepted"]
    # 2. a frontal ext_8 added (no earlier entry: no role yet)
    assert reg.call(ctx, "add_camera", cam("ext_8", [14.0, 17.5, z8], [10.0, 6.0, z8]))["accepted"]
    assert TL.x6_frontal_now(ctx, "ext_8", main)
    # 3. ext_4 back to the corner pose: allowed while ext_8 stays X6's frontal view
    assert reg.call(ctx, "set_camera", cam("ext_4", *POSE_B))["accepted"]
    assert not TL.x6_frontal_now(ctx, "ext_4", main)
    # 4. ext_8 added again at a corner pose: refused, ext_8 is the frontal view
    again = reg.call(ctx, "add_camera", cam("ext_8", [20.0, 17.5, z8b], [12.0, 9.0, z8b]))
    assert not again["accepted"], again
    assert again["failed_checks"][0].startswith("role: ext_8 is the frontal view and keeps its role")
    assert "main (+y) entrance facade, the frontal view X6 asks for" in again["failed_checks"][0]
    assert ctx.tries["ext_8"] == 2                         # the add of step 2 and this refusal
    assert [n for n in TL.exterior_poses(ctx) if TL.x6_frontal_now(ctx, n, main)] == ["ext_8"]
    # the guard is the same as for a scene camera: the only frontal view is not removed ...
    gone = TL.role_problem(ctx, "remove", "ext_8", {})
    assert gone is not None and gone.startswith("role: ext_8 is the only frontal view")
    # ... and another frontal pose of ext_8 is still a frontal pose
    z8c = eye_z(b, 13.0, 17.5)
    moved = reg.call(ctx, "add_camera", cam("ext_8", [13.0, 17.5, z8c], [10.0, 6.0, z8c]))
    assert moved["accepted"], moved
    # an added camera that is not X6's frontal view has no role
    z9 = eye_z(b, 30.0, 5.0)
    assert reg.call(ctx, "add_camera", cam("ext_9", [30.0, 5.0, z9], [10.0, 6.0, z9]))["accepted"]
    assert TL.role_problem(ctx, "add", "ext_9", cam("ext_9", [30.0, -2.0, z9], [10.0, 6.0, z9])) is None
    # review (a): the agent's own frontal view added and re-added at a corner pose, no other frontal view
    ctx2 = real04_ctx(tmp_path / "a", P3_EXTERIOR)
    reg2 = TL.build_registry()
    assert reg2.call(ctx2, "add_camera", cam("ext_8", *R04_FRONTAL_POSE))["accepted"]
    turned = reg2.call(ctx2, "add_camera", cam("ext_8", R04_FRONTAL_POSE[0], [20.0, 10.0, 1.6]))
    assert not turned["accepted"] and turned["failed_checks"][0].startswith("role: ext_8 is the frontal view")
