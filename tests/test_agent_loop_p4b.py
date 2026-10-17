"""Fix round after pod P4b (17 Oct 2026; real03, the review of the P4a fix round and the lead's decisions), track
A_agent.

What these tests pin (CPU only: MockModel, the fakes of ``test_agent_helpers``, small synthetic buildings shaped like
the P4a / P4b cases):

- decision 1: a camera replayed from the baseline (set 1) is frozen: set / remove / add of its name are refused, a
  new camera is accepted; X6 and V1 on it are report-only (cause ``replayed_camera``);
- decision 2: a frontal view stays square to its facade, an entrance view stays close in front of its door, the only
  view of either role is not removed; an eye-height refusal names the ground and the z to use;
- one X6 rubric: the critic is told each camera's role and measured eye height; contradicted X6 claims are dropped;
- S2 wall cuts: exact depth (a move INTO the wall stays a cut), chained edits, cuts under 0.03 m gone, a swap that
  keeps the footprint keeps the cut;
- light-fixture findings go to the decor lamp or the floor lamp they are about before the rig;
- set_exterior: the sun within the code's X7 rule, the built site and garden as the no-op state, vision findings the
  override does not touch stay, the dry re-check reads the new sun;
- a lighting_dark view under one exposure step is minor and report-only; FINAL_ROUND_LIGHTING is off (decision 6);
- fix_fixture after "no valid spot", repeated dry runs, the swap_model footprint note.
"""
from __future__ import annotations

import copy
import json
import random

import pytest

from test_agent_helpers import (CAMERAS, FakeEdits, building, fake_validators, project, violation, write_json)
from test_agent_loop_p4a import CHAIR_CUT, DARK, LIGHT, WALL_CUT, corridor_with_table, make
from test_m13_agent import FINISH, ctx_for, finding, log_of
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.blender import exterior_checks as X
from wenart.blender import scene_checks as SC

FLAT = {"kind": "flat", "z": {"+x": -0.15, "-x": -0.15, "+y": -0.15, "-y": -0.15}}
ENTRANCE = {"door_id": "d_ent", "level_id": "L0", "main": True, "centre": [4.0, 3.5], "face": [4.0, 3.6],
            "outward": [0.0, 1.0], "threshold_z": 0.0}
EXT = [
    # the replayed set 1 (decision 1): ext_1 and the interior view cam_r1_1
    {"name": "ext_1", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["left", "front"],
     "position": [-8.0, -8.0, 1.6], "target": [4.0, 2.0, 1.6], "lens_mm": 26.0, "source": "replayed"},
    # the searched frontal and entrance views (real03's ext_6 / ext_7 shapes)
    {"name": "ext_6", "kind": "exterior", "room_id": None, "view": "frontal", "sides": ["back"],
     "position": [4.0, 20.0, 1.6], "target": [4.0, 3.5, 1.6], "lens_mm": 26.0, "source": "searched"},
    {"name": "ext_7", "kind": "exterior", "room_id": None, "view": "entrance", "sides": ["back"], "entrance": "d_ent",
     "position": [6.7, 11.0, 1.6], "target": [4.0, 3.6, 1.6], "lens_mm": 26.0, "source": "searched"},
    {"name": "ext_2", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["right", "front"],
     "position": [20.0, -10.0, 1.45], "target": [6.0, 1.5, 1.45], "lens_mm": 26.0, "source": "searched"},
]


def camera_project(tmp_path, cameras=None, scene_extra=None, **kw):
    """``ctx_for`` with the exterior cameras above (cam_r1_1 replayed), the entrance d_ent and a flat terrain."""
    out = project(tmp_path)
    b = building()
    b["site"] = {"entrances": [dict(ENTRANCE)]}
    for name in ("building_decor.json", "building_final.json", "building.json"):
        write_json(out / name, b)
    cams = [dict(CAMERAS[0], source="replayed"), dict(CAMERAS[1])] + copy.deepcopy(cameras or EXT)
    scene = {"cameras": cams, "site": {"terrain": dict(FLAT)}}
    scene.update(scene_extra or {})
    write_json(out / "scene" / "scene_manifest.json", scene)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    kw.setdefault("apply_edit", FakeEdits())
    kw.setdefault("validators", fake_validators())
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out), **kw)


def cam(view_id, position, target, kind="exterior", **extra):
    return dict({"view_id": view_id, "kind": kind, "position": list(position), "target": list(target),
                 "lens_mm": 26, "reason": "a better view"}, **extra)


# --------------------------------------------------------------------------
# decision 1: the replayed set 1 is frozen
# --------------------------------------------------------------------------

def test_a_replayed_camera_is_frozen_but_a_new_camera_may_be_added(tmp_path):
    """Fails on 11949a9: the P4a fix round's build merge makes an agent set really replace a replayed record, and
    tools.camera_handler had no replayed check: real02's frozen frontal ext_6 [7.59, 29.50] would have become a
    near-duplicate of ext_3 (docs/milestone13.md §7). Set, remove and an add of its name are refused (a try each);
    a new camera under a new name is accepted."""
    ctx = camera_project(tmp_path)
    reg = TL.build_registry()
    corner = cam("ext_1", [24.0, 22.0, 1.6], [7.59, 6.0, 1.6])
    for tool, args in (("set_camera", corner), ("add_camera", corner),
                       ("remove_camera", {"view_id": "ext_1", "reason": "drop it"}),
                       ("set_camera", cam("cam_r1_1", [3.0, 0.6, 1.3], [1.0, 3.0, 1.2], kind="interior",
                                          room_id="r1"))):
        res = reg.call(ctx, tool, args)
        assert not res["accepted"] and res.get("frozen"), (tool, res)
        assert res["failed_checks"][0].startswith("frozen: ") and "set 1" in res["failed_checks"][0]
        assert "add_camera with a new view id" in res["failed_checks"][0]
    assert ctx.tries["ext_1"] == 3 and ctx.tries["cam_r1_1"] == 1 and ctx.accepted == []
    assert not OV.overrides_path(ctx.project_out).exists()
    new = reg.call(ctx, "add_camera", cam("ext_9", [-9.0, 6.0, 1.6], [4.0, 2.0, 1.6]))
    assert new["accepted"], new
    # a record that already replaced a replayed one (an older run) is still set 1's
    assert CS.frozen_camera({"name": "ext_6", "source": "searched", "replaced_replayed": {"position": [0, 0, 0]}})
    assert not CS.frozen_camera({"name": "ext_6", "source": "searched"}) and not CS.frozen_camera(None)


def test_placement_findings_on_a_replayed_view_are_report_only(tmp_path):
    """Fails on 11949a9: X6 on a replayed view had the cause exterior_camera (set_camera offered), so the vision
    critic's "frontal, not a 3/4 view" on real02's replayed ext_6 sent the agent to move it every round. Now X6 and V1
    on a set-1 camera are ``replayed_camera`` (no tool, reported to the cameras); a building-level X6 ("no frontal
    view") keeps add_camera."""
    x6 = finding("X6", "major", "ext_1", None, "ext_1: eye height 1.90 m above the ground (wanted 1.5-1.7 m)")
    v1 = finding("V1", "major", "cam_r1_1", "r1", "the camera stands 0.2 m from a door leaf")
    other = finding("X6", "major", "ext_6", None, "ext_6: pitched 3 degrees")
    whole = finding("X6", "major", "exterior", None, "no frontal view of the entrance (+y) facade")
    cams = [dict(CAMERAS[0], source="replayed")] + EXT
    marked = CS.mark_replayed([x6, v1, other, whole], cams)
    assert [CS.cause_of(f) for f in marked] == ["replayed_camera", "replayed_camera", "exterior_camera",
                                                "exterior_camera"]
    assert CS.tools_for_finding(x6) == [] and CS.REPORT_TO["replayed_camera"] == "cameras"
    assert "set 1" in CS.no_tool_reason(x6) and "add_camera" in CS.no_tool_reason(x6)
    assert "add_camera" in CS.tools_for_finding(whole)
    # through the loop: the vision X6 on the replayed ext_1 is reported (not dropped, not work), the code V1 on the
    # replayed cam_r1_1 too
    loop, out, model = make(tmp_path, [{"content": "nothing"}], [[violation("V1", "major", "cam_r1_1", "r1",
                                                                             "the camera stands in the door swing")]],
                            critic=[{"findings": []}, {"findings": []},
                                    {"findings": [{"check": "X6", "severity": "major", "target": "ext_1",
                                                   "message": "a flat frontal elevation rather than a 3/4 corner "
                                                              "view", "evidence_image": 1}]}],
                            vision=True, max_rounds=1)
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text())
    scene["cameras"][2] = dict(scene["cameras"][2], source="replayed", view="corner", sides=["left", "front"])
    scene["cameras"][0] = dict(scene["cameras"][0], source="replayed")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene))
    res = loop.run()
    events = [e for e in log_of(out)["events"] if e["kind"] == "finding" and e["checklist"] in ("X6", "V1")]
    assert sorted((e["source"], e["checklist"]) for e in events) == [("code", "V1"), ("vision", "X6")]
    for e in events:
        assert e["cause"] == "replayed_camera" and not e.get("dropped") and e["report_to"] == "cameras"
        assert "set 1" in e["not_yours"]
    assert res["stop"]["reason"] == "no_fixable"


# --------------------------------------------------------------------------
# decision 2: a frontal or entrance view keeps its role; the eye-height hint
# --------------------------------------------------------------------------

def test_a_frontal_view_stays_square_and_an_entrance_view_stays_at_its_door(tmp_path):
    """Fails on 11949a9: P4b turned the frontal ext_6 and the entrance ext_7 into corner views (8 accepted
    set_camera edits flipped them back and forth) and pulled ext_7 to (40, -45), a blown-out far view; the final set
    had no entrance view. Now the frontal view must stay square (within 30 degrees, the build's own rule) to its
    facade, the entrance view within 14 m of the door and 30 degrees of its axis, and the only view of a role is not
    removed."""
    ctx = camera_project(tmp_path)
    reg = TL.build_registry()
    corner = reg.call(ctx, "set_camera", cam("ext_6", [14.0, 12.0, 1.6], [4.0, 3.5, 1.6]))
    assert not corner["accepted"] and corner["failed_checks"][0].startswith("role: ext_6 is the frontal view")
    assert "back facade" in corner["failed_checks"][0] and not corner.get("frozen")
    closer = reg.call(ctx, "set_camera", cam("ext_6", [4.0, 15.0, 1.6], [4.0, 3.5, 1.6]))
    assert closer["accepted"], closer
    far = reg.call(ctx, "set_camera", cam("ext_7", [4.0, 30.0, 1.6], [4.0, 3.6, 1.6]))
    assert not far["accepted"] and "from the door d_ent" in far["failed_checks"][0]
    side = reg.call(ctx, "set_camera", cam("ext_7", [14.0, 4.0, 1.6], [4.0, 3.6, 1.6]))
    assert not side["accepted"] and "off the door d_ent's axis" in side["failed_checks"][0]
    near = reg.call(ctx, "set_camera", cam("ext_7", [2.0, 9.0, 1.6], [4.0, 3.6, 1.6]))
    assert near["accepted"], near
    for view in ("ext_6", "ext_7"):
        res = reg.call(ctx, "remove_camera", {"view_id": view, "reason": "a duplicate"})
        assert not res["accepted"] and res["failed_checks"][0].startswith(f"role: {view} is the only")
    # a corner view may move freely (no role to keep); another frontal view lets the first one go
    assert reg.call(ctx, "set_camera", cam("ext_2", [22.0, -12.0, 1.45], [6.0, 1.5, 1.45]))["accepted"]
    ctx2 = camera_project(tmp_path / "b", cameras=EXT + [dict(EXT[1], name="ext_8", position=[4.0, 18.0, 1.6])])
    assert TL.build_registry().call(ctx2, "remove_camera", {"view_id": "ext_6", "reason": "two frontal views"})[
        "accepted"]


def test_an_eye_height_refusal_names_the_ground_and_the_z_to_use(tmp_path):
    """Fails on 11949a9: P4b's 1.6 m tries were refused "eye height 1.75 m above the ground" with no word of the
    ground at -0.15 m."""
    validators = fake_validators()
    validators.validate_camera_override = lambda b, c: {
        "ok": False, "failed": ["eye height 1.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above "
                                "the ridge 3.00 m)"]}
    ctx = camera_project(tmp_path, validators=validators)
    res = TL.build_registry().call(ctx, "add_camera", cam("ext_9", [-9.0, 6.0, 1.6], [4.0, 2.0, 1.6]))
    assert not res["accepted"]
    # pass before P5 (pin changed on purpose): "z 1.35 to 1.55", readable below zero too ("z -2.54 to -2.44")
    assert res["failed_checks"][-1] == "the ground at (-9, 6) is at z -0.15 m: use z 1.35 to 1.55 for an eye-level view"
    assert CV.scene_ground_z({"site": {"terrain": FLAT}}, 3, 4) == -0.15
    assert CV.scene_ground_z({}, 3, 4) is None
    assert CV.scene_ground_z({"site": {"terrain": {"kind": "tin"}}}, 1, 1) is None


# --------------------------------------------------------------------------
# one X6 rubric: roles and measured eye height for the critic, contradicted claims dropped
# --------------------------------------------------------------------------

LOW_ANGLE = "Low camera angle looking up at the building rather than eye level 1.5-1.7 m."
FRONTAL = "A flat frontal elevation of one facade rather than a 3/4 corner view with two facades."
WHOLE = "The whole building is not in the frame; only the door and part of the facade are visible."


def x6(message, target):
    return {"check": "X6", "severity": "major", "target": target, "message": message, "evidence_image": 1}


def critique(tmp_path, view, camera, messages, code=None, scene=None):
    from test_agent_helpers import jpg
    preview = jpg(tmp_path / f"{view}_preview.jpg")
    model = MM.MockModel(critic=[{"findings": [x6(m, view) for m in messages]}])
    res = CV.critique_exterior(model, building(), view, preview=preview, plan_crop=None,
                               code=code or {"findings": [], "ran": []}, call_id="t", camera=camera,
                               scene={"site": {"terrain": FLAT}} if scene is None else scene)
    return res, json.dumps(model.critic_requests()[0])


def test_the_critic_is_told_the_role_and_the_measured_eye_height_and_contradicted_x6_claims_are_dropped(tmp_path):
    """Fails on 11949a9: the X6 rubric asked every view for a 3/4 corner at 1.5-1.7 m and camera_note spoke only of
    aerial views, so P4b's critic called the frontal and the entrance views wrong and 5 cameras 1.60 m above the
    ground "low angle"; no X6 claim was ever dropped. A corner view keeps its "frontal" claim (P4b's round-3 ext_2:
    the agent had made the corner frontal, and the claim was right)."""
    corner, frontal, entrance = EXT[3], dict(EXT[1], position=[4.0, 20.0, 1.45], target=[4.0, 3.5, 1.45]), \
        dict(EXT[2], position=[6.7, 11.0, 1.45], target=[4.0, 3.6, 1.45])
    assert "3/4 corner" not in P.CHECKLIST["X6"]["what"].split(";")[0]
    assert "frontal view looks square" in P.CHECKLIST["X6"]["what"] and "entrance door up close" in \
        P.CHECKLIST["X6"]["what"]
    eye = CV.camera_eye(corner, {"site": {"terrain": FLAT}})
    assert eye == {"eye_m": 1.6, "pitch_deg": 0.0, "ground_z": -0.15}
    note = P.camera_note(frontal, eye)
    assert "the one frontal view of the back (entrance) facade" in note and "NOT a finding" in note
    assert "1.60 m above the ground" in note and "do not report its height or angle" in note
    assert "door up close" in P.camera_note(entrance) and "replayed from the baseline" in P.camera_note(EXT[0])
    # the height claim on a camera at 1.60 m above the ground: dropped with the code's numbers
    res, prompt = critique(tmp_path, "ext_2", corner, [LOW_ANGLE, FRONTAL])
    assert "1.60 m above the ground" in prompt and "3/4 corner view that shows two facades" in prompt
    assert [f["message"] for f in res["kept"]] == [FRONTAL]                      # the corner keeps "frontal"
    assert res["dropped"][0]["dropped"].startswith("code contradicts: eye 1.60 m above the ground, pitch 0.0 deg")
    # the frontal and the entrance view: "frontal" is by design; the entrance view is not the whole building
    res, _ = critique(tmp_path, "ext_6", frontal, [FRONTAL, LOW_ANGLE])
    assert res["kept"] == [] and "ext_6 is the frontal view the camera policy requires" in res["dropped"][0]["dropped"]
    res, _ = critique(tmp_path, "ext_7", entrance, [WHOLE])
    assert res["kept"] == [] and "not the whole building" in res["dropped"][0]["dropped"]
    res, _ = critique(tmp_path, "ext_2", corner, [WHOLE])
    assert [f["message"] for f in res["kept"]] == [WHOLE]
    # a camera really too high, or a ground the scene does not give: the height claim stays
    res, _ = critique(tmp_path, "ext_2", dict(corner, position=[20.0, -10.0, 1.85], target=[6.0, 1.5, 1.85]),
                      [LOW_ANGLE])
    assert len(res["kept"]) == 1
    res, _ = critique(tmp_path, "ext_2", corner, [LOW_ANGLE], scene={})
    assert len(res["kept"]) == 1
    assert CV.camera_claims("A plain sky.") == set()


# --------------------------------------------------------------------------
# S2 wall cuts: exact depth, chained edits, cuts under 0.03 m, swaps
# --------------------------------------------------------------------------

def wall_of(b):
    return next(w for w in SC.wall_boxes(b, "L1") if w["id"] == "w_L1_006")


def test_a_move_into_the_wall_keeps_the_cut_and_the_depth_is_exact():
    """Fails on 11949a9: the 7 x 7 grid missed the wall's axis, so real02's f_L1_024 moved 0.05 m INTO w_L1_006 was
    predicted 0.0016 m deep and accepted (review of the P4a fix round). The depth is now exact: a footprint across the
    axis is half the wall thick."""
    before_b = corridor_with_table()
    into = corridor_with_table((12.39, 9.95))
    kept = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, into, building_before=before_b)
    assert [CS.finding_key(f) for f in kept] == [("S2", "f_L1_024/w_L1_006")]
    assert kept[0]["evidence"]["metrics"]["predicted_depth_after"] == pytest.approx(0.0516, abs=1e-4)
    ok, why = LP.accept_edit([WALL_CUT], kept, {"target_finding": [dict(WALL_CUT, metrics=kept[0]["metrics"])]})
    assert not ok and why.startswith("finding S2:f_L1_024/w_L1_006 is still there")
    w = wall_of(before_b)
    assert LP.footprint_wall_depth(before_b["furniture"][0], w) == pytest.approx(0.055)       # across the axis
    assert LP.footprint_wall_depth(corridor_with_table((12.39, 9.83))["furniture"][0], w) == pytest.approx(-0.011)
    # against dense sampling, any footprint and rotation, near the wall's ends too
    rnd = random.Random(7)
    wall = {"id": "w", "a": (0.0, 0.0), "b": (3.0, 0.0), "thickness": 0.2}
    from wenart import geometry as G
    for _ in range(60):
        fp = {"center": [rnd.uniform(-0.6, 3.6), rnd.uniform(-0.7, 0.7)], "size": [rnd.uniform(0.2, 1.4),
                                                                                   rnd.uniform(0.2, 0.9)],
              "rotation_deg": rnd.uniform(0, 360)}
        best = None
        for i in range(81):
            for j in range(81):
                x, y = G.rotate_point((fp["center"][0] + (i / 80 - 0.5) * fp["size"][0],
                                       fp["center"][1] + (j / 80 - 0.5) * fp["size"][1]), fp["rotation_deg"],
                                      tuple(fp["center"]))
                if 0.0 <= x <= 3.0:
                    d = min(0.1 - abs(y), x, 3.0 - x)
                    best = d if best is None else max(best, d)
        exact = LP.footprint_wall_depth({"footprint": fp}, wall)
        assert (exact is None) == (best is None)
        if exact is not None:
            assert best <= exact + 1e-9 and exact - best < 0.02


def test_chained_moves_start_from_the_predicted_cut_and_cuts_under_3_cm_are_gone():
    """Fails on 11949a9: (1) a second move of the round started from the measured depth, so 0.04 m toward the wall
    then 0.06 m away was GONE while the same end state from the round start keeps 0.0316 m; each kept copy stacked
    another prefix on the message. (2) A move that leaves 0.02 m was kept as a major finding and rejected, while the
    same cut is a minor within-tolerance finding no tool is asked to fix."""
    start, step1, step2 = (corridor_with_table((12.39, y)) for y in (9.83, 9.87, 9.81))
    k1 = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, step1, building_before=start)
    assert k1[0]["evidence"]["metrics"]["predicted_depth_after"] == pytest.approx(0.0916, abs=1e-4)
    k2 = LP.after_findings([], k1, {"f_L1_024"}, step2, building_before=step1)
    direct = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, step2, building_before=start)
    assert k2 and direct
    assert k2[0]["evidence"]["metrics"]["predicted_depth_after"] == pytest.approx(0.0316, abs=1e-4) \
        == direct[0]["evidence"]["metrics"]["predicted_depth_after"]
    assert k2[0]["message"].count("predicted from the footprint") == 1
    assert k2[0]["message"].endswith(WALL_CUT["message"])
    # 0.04 m away from the axis-crossing start: 0.0156 m left, under 0.03 m: gone (and the same rule as the critic)
    left = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, corridor_with_table((12.39, 9.86)),
                             building_before=corridor_with_table())
    assert left == []
    assert LP.accept_edit([WALL_CUT], left, {"target_finding": [WALL_CUT]})[0]


def test_an_edit_that_keeps_the_footprint_keeps_the_wall_cut(tmp_path):
    """Fails on 11949a9: a swap_model keeps the drawn footprint (the model is fitted to it), yet its S2 wall cut
    counted as gone: P4b accepted 5 swaps for S2 and 4 cuts were still there. The fit scales a model to the
    footprint's width (K2), so a cut across the width stays exactly (the bathtub f_L0_184, 0.049 m twice); a cut
    across the depth can shrink only by what another model's depth may differ (x1.10, ``fit.NON_UNIFORM_CAP``): the
    washers' 0.14-0.16 m stayed, the shower f_L0_180's 0.041 m (0.97 m deep) cleared and is left to the next round.
    A retype (another model and class) and a pair cut are still left to the next round."""
    b = corridor_with_table()

    def swap(bb):
        out = copy.deepcopy(bb)
        out["furniture"][0]["asset_pin"] = "abo_other"
        return out

    # the table turned 90 degrees: its width (1.2 m) runs across the wall: the cut stays exactly
    across = copy.deepcopy(b)
    across["furniture"][0]["footprint"].update(size=[1.2, 0.7], rotation_deg=90.0, center=[12.39, 9.65])
    kept = LP.after_findings([], [WALL_CUT], {"f_L1_024"}, swap(across), building_before=across)
    assert [CS.finding_key(f) for f in kept] == [("S2", "f_L1_024/w_L1_006")]
    assert kept[0]["message"].startswith("the edit keeps the footprint 1.20 x 0.70 m (the model is fitted to its "
                                         "width), so the cut into w_L1_006 stays at least 0.052 m")
    assert not LP.accept_edit([WALL_CUT], kept, {"target_finding": [WALL_CUT]})[0]
    # a cut across the depth: a deep one stays (0.15 - 0.7 x (1 - 1/1.1) = 0.086 m), a shallow one may clear
    deep = finding("S2", "major", "f_L1_024", "r_L1_koridor_2", "washing machine cuts the wall by 0.150 m",
                   depth_m=0.15, tolerance_m=0.03, wall_id="w_L1_006")
    kept = LP.after_findings([], [deep], {"f_L1_024"}, swap(b), building_before=b)
    assert kept and kept[0]["evidence"]["metrics"]["predicted_depth_after"] == pytest.approx(0.0864, abs=1e-3)
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, swap(b), building_before=b) == []
    assert LP.swap_depth_slack(b["furniture"][0], wall_of(b)) == pytest.approx(0.7 * (1 - 1 / 1.1))
    assert LP.swap_depth_slack(across["furniture"][0], wall_of(across)) == 0.0
    retyped = copy.deepcopy(across)
    retyped["furniture"][0]["type"] = "table_side"
    assert LP.after_findings([], [WALL_CUT], {"f_L1_024"}, retyped, building_before=across) == []
    assert LP.after_findings([], [CHAIR_CUT], {"f_L1_024"}, swap(across), building_before=across) == []
    # the tool result says so
    ctx = ctx_for(tmp_path)
    res = TL.build_registry().call(ctx, "swap_model", {"piece_id": "f1", "asset_id": "abo_x", "reason": "nicer"})
    assert res["accepted"] and res["footprint_kept"].startswith("the footprint 1.60 x 2.00 m is kept")


# --------------------------------------------------------------------------
# light fixtures: the decor lamp or the floor lamp first, the rig last
# --------------------------------------------------------------------------

def lamp_building():
    b = building()
    b["furniture"].append({"id": "f_lamp", "level_id": "L0", "room_id": "r2", "type": "floor_lamp",
                           "source": "added_by_ai", "status": "verified",
                           "footprint": {"center": [7.5, 3.1], "size": [0.4, 0.4], "rotation_deg": 0.0},
                           "asset": {"method": "library", "asset_id": "abo_lamp"}})
    b["furniture"].append({"id": "f_tbl", "level_id": "L0", "room_id": "r2", "type": "table_dining",
                           "source": "added_by_ai", "status": "verified",
                           "footprint": {"center": [6.0, 1.5], "size": [1.6, 0.9], "rotation_deg": 0.0}})
    b["decor"] = [{"id": "dec_1", "kind": "decor", "type": "table_lamp", "room_id": "r1", "host_id": "f2"},
                  {"id": "dec_2", "kind": "decor", "type": "pendant_light", "room_id": "r2", "host_id": None,
                   "slot": "ceiling:over_f_tbl"}]
    return b


def test_a_light_finding_goes_to_the_lamp_it_is_about_before_the_rig():
    """Fails on 11949a9: light_subject sent every 'lamp' to the lighting stage: real02's hosted table lamps
    (decor) and floor lamps (furniture, swap_model can fix them) lost their path. The P4a wall-mounted lamp stays the
    rig's even with a table lamp on the nightstand."""
    b = lamp_building()

    def routed(message, target, room):
        f = {"id": "v:t:1", "source": "vision", "check": "D2", "severity": "major", "target": target,
             "room_id": room, "message": message, "evidence": {"image": 1}}
        return CV.reroute_light_findings([f], b, room)[0]

    table = routed("The table lamp on the nightstand is a crude grey box.", "f2", "r1")
    assert table["target"] == "dec_1" and table["cause"] == "decor_model"
    assert table["evidence"]["metrics"]["target_was"] == "f2" and table["evidence"]["metrics"]["retarget"] == "decor"
    assert CS.tools_for_finding(table) == [] and CS.REPORT_TO["decor_model"] == "decor"
    floor = routed("The floor lamp beside the sofa is rendered as a plain cylinder.", "f3", "r2")
    assert floor["target"] == "f_lamp" and "cause" not in floor
    assert CS.cause_of(floor) == "wrong_model" and "swap_model" in CS.tools_for_finding(floor)
    pendant = routed("The pendant light over the dining table floats with no cord.", "f_tbl", "r2")
    assert pendant["target"] == "dec_2" and pendant["cause"] == "decor_model"
    wall = routed("The wall-mounted lamp next to the nightstand is rendered as a crude, flat rectangular box.", "f2",
                  "r1")
    assert wall["target"] == "r1" and wall["cause"] == "light_fixture"
    assert wall["evidence"]["metrics"]["retarget"] == "rig" and wall["evidence"]["metrics"]["light_kind"] == "wall"
    bedside = routed("The bedside lamp is a crude box.", "f1", "r1")      # no lamp on the bed: the rig's lamp
    assert bedside["target"] == "r1" and bedside["cause"] == "light_fixture"
    assert [CV.light_kind(m) for m in ("a sconce above the bed", "the lamp on the wall", "a reading lamp",
                                       "a lamp")] == ["wall", "wall", "table", "generic"]


# --------------------------------------------------------------------------
# set_exterior: the X7 sun rule, the built state, untouched vision findings, the new sun in the dry re-check
# --------------------------------------------------------------------------

SUN_225 = {"sun": {"elevation_deg": 40.0, "azimuth_deg": 225.0}, "reason": "the sun on the entrance"}
SCENE_EXT = {"lighting": {"sun": {"elevation_deg": 40.0, "azimuth_deg": 210.0}},
             "whole_building": {"main_facade": {"axis": "+y", "direction": [0.0, 1.0]}},
             "exterior_looks": {"garden": {"material": "grass"}, "ground": {"material": "soil"}},
             "brief": {"site_options.front_court": {"value": "auto"}}}


def test_a_sun_override_must_keep_the_code_x7_rule(tmp_path):
    """Fails on 11949a9: validate_exterior_override took 5-89 degrees, so P4b's sun at 55 degrees (azimuth 225) was
    accepted and the next round raised X7 "sun 55 degrees above the horizon (wanted 25-50)". The azimuth is turned to
    the building frame with the site's north (decision 4: real02's assumed north stays)."""
    ctx = camera_project(tmp_path, scene_extra=SCENE_EXT)
    reg = TL.build_registry()
    high = reg.call(ctx, "set_exterior", {"sun": {"elevation_deg": 55.0}, "reason": "not washed out"})
    assert not high["accepted"] and high["failed_checks"][0].startswith("sun: 55 degrees above the horizon")
    back = reg.call(ctx, "set_exterior", SUN_225)
    assert not back["accepted"] and "lights the back" in back["failed_checks"][0] and "north 0" in \
        back["failed_checks"][0]
    ctx.building["site"]["north_deg"] = 180.0
    turned = reg.call(ctx, "set_exterior", SUN_225)
    assert turned["accepted"], turned
    assert TL.sun_problems(ctx, {"elevation_deg": 45.0}) == []


def test_the_built_site_and_garden_are_the_no_op_state(tmp_path):
    """Fails on 11949a9: exterior_state read site.ground.look (not set), so P4b's ground 'grass' on the 'grass'
    garden was accepted as a change, and the site's defaults (a path, a hedge, 3 trees) were unknown to it."""
    ctx = camera_project(tmp_path, scene_extra=SCENE_EXT)
    reg = TL.build_registry()
    for args in ({"ground": "grass"}, {"site": {"fence": "hedge"}}, {"site": {"path": True, "trees": 3}},
                 {"site": {"front_court": "auto"}}):
        res = reg.call(ctx, "set_exterior", dict(args, reason="the same"))
        assert not res["accepted"] and res["failed_checks"][0].startswith("no_change:"), args
    assert reg.call(ctx, "set_exterior", {"site": {"fence": "fence"}, "reason": "a fence"})["accepted"]
    state = TL.exterior_state(ctx)
    assert state["ground"] == "grass" and state["site"]["fence"] == "fence" and state["site"]["trees"] == 3


X4 = {"id": "v:r1-v3:1", "source": "vision", "check": "X4", "severity": "major", "target": "ext_1", "room_id": None,
      "message": "no visible path to the entrance, only grass", "evidence": {"image": 1}}


def test_a_set_exterior_keeps_the_vision_findings_it_does_not_touch():
    """Fails on 11949a9: changed_targets added the step's finding target and after_findings dropped every vision
    finding on a changed target, so P4b's ground (seq 951) and sun (seq 1357) edits each counted the vision X4 "no
    path" as removed; it came back. Now only an override of a slot of the cause (X4/site: site or ground; X2: roof;
    X7: sun) touches it. Pass before P5 (changed on purpose): ``changed`` is changed_targets' own output (the
    hand-made ``changed | {"ext_1"}`` pinned a path the pipeline never takes) and the edit's target goes in as
    ``targets``; the reason is checked in accept_edit's text (tests/test_agent_pass_before_p5.py runs it through the
    loop)."""
    x4 = dict(X4, cause=CS.cause_of(X4))
    assert x4["cause"] == "site"
    sun = {"sun": {"elevation_deg": 40.0}}
    changed = TL.changed_targets("set_exterior", dict(sun, reason="x"), {}, [x4], findings=[x4])
    assert "ext_1" not in changed and LP.BUILDING in changed
    assert "ext_1" in TL.changed_targets("set_exterior", {"site": {"path": True}}, {}, [x4], findings=[x4])
    kept = LP.after_findings([], [x4], changed, {}, override=sun, targets=[x4])
    assert [CS.finding_key(f) for f in kept] == [("X4", "ext_1")]
    assert kept[0]["message"].startswith("the edit does not change what the finding is about (the override sets sun")
    ok, why = LP.accept_edit([x4], kept, {"target_finding": [x4]})
    assert not ok and "does not change what the finding is about" in why
    assert LP.after_findings([], [x4], {"ext_1", LP.BUILDING}, {}, override={"site": {"path": True}}) == []
    assert LP.after_findings([], [x4], {"ext_1", LP.BUILDING}, {}, override={"ground": "grass"}) == []
    assert CS.override_touches("roof", {"roof": {"overhang_m": 0.5}}) and not CS.override_touches("facade", sun)
    # a vision X7 about one view's exposure is that view's exposure, not the sun
    blown = finding("X7", "major", "ext_7", None, "The view is overexposed and washed out")
    assert CS.cause_of(blown) == "lighting_exterior" and CS.tools_for_finding(blown) == []
    assert CS.cause_of(finding("X7", "major", "sun", None, "sun 55 degrees above the horizon")) == "sun"


def test_the_dry_recheck_reads_the_sun_the_override_sets(tmp_path):
    """Fails on 11949a9: the dry re-check's critic read the round's scene manifest, so a sun edit could never remove
    the code's X7 (and a bad one never showed it)."""
    def x7(building, scene, manifest):
        out = []
        X._x7({"main_facade": {"axis": "+y", "direction": [0.0, 1.0]}}, scene, out)
        return [CC.finding(v) for v in out]

    loop, out, model = make(tmp_path, [{"tool_calls": [{"name": "set_exterior", "arguments": {
        "sun": {"elevation_deg": 40.0}, "reason": "the sun within 25-50 degrees"}}]}, FINISH],
        [[violation("X7", "major", "sun", None, "sun 55 degrees above the horizon (wanted 25-50)")], []],
        recheck=x7, max_rounds=1)
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text())
    scene.update(copy.deepcopy(SCENE_EXT))
    scene["lighting"]["sun"] = {"elevation_deg": 55.0, "azimuth_deg": 0.0, "azimuth_building_deg": 0.0}
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene))
    loop.run()
    edits = [e for e in log_of(out)["events"] if e["kind"] in ("edit", "rejected_edit") and e["tool"] == "set_exterior"]
    assert [e["kind"] for e in edits] == ["edit"], edits
    after = LP.scene_after(scene, "set_exterior", {"sun": {"azimuth_deg": 225.0}}, {"site": {"north_deg": 180.0}})
    assert after["lighting"]["sun"]["azimuth_building_deg"] == 45.0 and scene["lighting"]["sun"]["azimuth_deg"] == 0.0
    assert LP.scene_after(scene, "move_piece", {}, {}) is scene


# --------------------------------------------------------------------------
# lighting: under one exposure step; the final round stays critical-only (decision 6)
# --------------------------------------------------------------------------

def test_a_view_under_one_exposure_step_over_the_cap_is_minor_and_report_only():
    """Fails on 11949a9: P4b re-lit and re-rendered three rooms for 0.01-0.04 stops over the cap; the render rounds
    the EV to 1/6 stop."""
    from wenart.blender import render as R
    assert CC.LIGHTING_STEP_STOPS == R.EXPOSURE_STEP

    def entry(cam, over):
        return {"check": "lighting_dark", "severity": "major", "target": cam, "room_id": "r1",
                "message": f"{cam}: {over} stops over", "metrics": {"stops_over_cap": over}}

    items = {v["target"]: v for v in CC.lighting_items({"lighting_dark": [entry("cam_a", 0.04),
                                                                          entry("cam_b", 0.42)]}, building())}
    small, big = items["cam_a"], items["cam_b"]
    assert small["severity"] == "minor" and small["metrics"]["below_exposure_step"] is True
    assert small["metrics"]["severity_was"] == "major" and "set_lighting_factor" not in small["metrics"]
    assert "less than one exposure step" in small["message"]
    f = CC.finding(small)
    assert CS.cause_of(f) == "lighting_within_step" and CS.tools_for_finding(f) == []
    assert big["severity"] == "major" and CS.cause_of(CC.finding(big)) == "lighting"


def test_the_final_round_lighting_is_off_by_default(tmp_path):
    """Fails on 11949a9 (FINAL_ROUND_LIGHTING was True): decision 6 of 17 Oct 2026, the switch stays off."""
    assert LP.FINAL_ROUND_LIGHTING is False
    loop, out, model = make(tmp_path, [LIGHT, FINISH], [[DARK], []], recheck=lambda b, s, m: [])
    res = loop.final_round(4)
    assert res["stop"] == "no_finding" and res["accepted"] == 0 and model.chat_requests() == []


# --------------------------------------------------------------------------
# fix_fixture after "no valid spot"; repeated dry runs
# --------------------------------------------------------------------------

NO_SPOT = "fixture_place: f2: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d1)"


class NoSpotEdits(FakeEdits):
    """``FakeEdits`` whose fix_fixture search finds no spot (edit_ops._fix_fixture's refusal)."""

    def __call__(self, building, edit, *, catalog=None):
        if edit["op"] == "fix_fixture":
            self.calls.append(copy.deepcopy(edit))
            return {"accepted": False, "failed_checks": [NO_SPOT if edit.get("center") is None else
                                                         "fixture_place: still through a wall"],
                    "score_before": 50.0, "score_after": 50.0, "building": None, "changed_ids": [], "message": ""}
        return super().__call__(building, edit, catalog=catalog)


def test_fix_fixture_is_not_tried_again_after_the_code_found_no_spot(tmp_path):
    """Fails on 11949a9: after "no valid spot within 0.50 m" P4b sent 21 guessed centres in 5 cm steps (and 13
    max_tries); now the step closes, a later call without a new size is refused (a try), in this session and in the
    next round (memory), and the room brief lists the piece's wall and outline cuts as not yours."""
    out = project(tmp_path)
    edits = NoSpotEdits()
    reg = TL.build_registry()
    ctx = TL.ToolContext.load(out, round=1, model_id="m", log=LG.AgentLog(out, "toy", "m", "r"),
                              overrides=OV.Overrides(out), apply_edit=edits, validators=fake_validators(),
                              memory=MEM.Memory(out))
    ctx.begin_session("r1")
    first = reg.call(ctx, "fix_fixture", {"piece_id": "f2", "reason": "through the wall"})
    assert not first["accepted"] and first["step_closed"] and "do not try centres" in first["message"]
    centre = reg.call(ctx, "fix_fixture", {"piece_id": "f2", "center": [0.9, 3.2], "reason": "a guess"})
    assert not centre["accepted"] and centre["failed_checks"][0].startswith("no_spot: f2") and centre["no_spot"]
    assert len(edits.calls) == 1 and ctx.tries["f2"] == 2
    assert MEM.Memory(out).no_spot("r1") == {"f2": {"round": 1, "reason": NO_SPOT}}
    # the next round: refused from the memory; a real product size is another search
    ctx2 = TL.ToolContext.load(out, round=2, model_id="m", log=LG.AgentLog(out, "toy", "m", "r"),
                               overrides=OV.Overrides(out), apply_edit=edits, validators=fake_validators(),
                               memory=MEM.Memory(out))
    again = reg.call(ctx2, "fix_fixture", {"piece_id": "f2", "center": [0.95, 3.2], "reason": "another guess"})
    assert again["failed_checks"][0].startswith("no_spot: f2") and "(round 1)" in again["failed_checks"][0]
    sized = reg.call(ctx2, "fix_fixture", {"piece_id": "f2", "size": [0.45, 0.4], "reason": "a real size"})
    assert not sized.get("no_spot") and len(edits.calls) == 2
    s2 = {"id": "c:S2:f2", "check": "S2", "severity": "major", "target": "f2", "message": "cuts wall w4",
          "cause": "collision", "tools": ["fix_fixture"]}
    f6 = {"id": "c:F6:f2", "check": "F6", "severity": "major", "target": "f2", "message": "no room", "cause":
          "clearance", "tools": ["move_piece"]}
    fixable, not_yours = BR.no_spot_findings([s2, f6], [], MEM.Memory(out), "r1")
    assert [f["id"] for f in fixable] == ["c:F6:f2"] and not_yours[0]["id"] == "c:S2:f2"
    assert "no valid spot within 0.5 m for f2 (fix_fixture, round 1)" in not_yours[0]["why"]
    assert "tools" not in not_yours[0]


def test_a_repeated_dry_run_is_answered_from_the_first_and_counts_a_try(tmp_path):
    """Fails on 11949a9: P4b sent the move of f_L0_141 to [17.88, 4.85] nine times as a dry run, each validated
    again with the same answer. A repeat in the session is answered from the first one and counts as a try; after an
    accepted edit the building changed and the dry run is validated again."""
    edits = FakeEdits()
    ctx = ctx_for(tmp_path, apply_edit=edits)
    ctx.begin_session("r1")
    reg = TL.build_registry()
    ask = {"tool": "rotate_piece", "args": {"piece_id": "f2", "front_deg": 90}}
    first = reg.call(ctx, "dry_run", copy.deepcopy(ask))
    again = reg.call(ctx, "dry_run", copy.deepcopy(ask))
    assert first["would_accept"] and "repeat_of" not in first and len(edits.calls) == 1
    assert again["repeat_of"] == 1 and again["would_accept"] and again["message"].startswith("same as dry run #1")
    assert ctx.tries == {"f2": 1} and "counted as a try" in again["note"]
    assert [e["status"] for e in ctx.log.events if e["kind"] == "dry_run"] == ["would_accept", "repeat"]
    assert reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90, "reason": "turn"})["accepted"]
    third = reg.call(ctx, "dry_run", copy.deepcopy(ask))
    assert "repeat_of" not in third and len(edits.calls) == 3
    # another session starts with no dry runs
    ctx.begin_session("r2")
    assert "repeat_of" not in reg.call(ctx, "dry_run", copy.deepcopy(ask))
