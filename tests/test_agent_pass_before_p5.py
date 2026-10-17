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
def test_real04_the_agents_frontal_view_keeps_its_role(tmp_path):
    """Fails on adc3004: real04 has no planner frontal view (P3 dropped ext_6), so the agent's frontal view is
    ``agent``; a set to ext_3's corner pose and a remove were accepted."""
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
