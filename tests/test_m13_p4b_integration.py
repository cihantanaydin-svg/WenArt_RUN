"""Integration of the fix round after P4b (17 Oct 2026): the cross-track asks the lead applied.

What: CPU tests of the asks applied at integration: the schema value of a nightstand symbol, the entrance view's own
X6 rule (one function for X6, the build's view check and the agent's camera tool), the X7 sun rule in the exterior
validator, the main-facade sun under an elevation-only override, the entrance door kept through an agent ``set``, the
policy's frontal view kept at its best share, the neutral rig of the halls, stairs and baths, the G14 of a drawn hall
washer, the L front of a corner-sofa candidate, the headboard searched in the bed's head half and the duplicate
exterior view refused by the agent's camera tool.
Why: every behaviour change of the integration step gets a test that fails on the tree before it (11949a9 plus the
tracks' changes) or on the mutation named in its docstring.
How: small hand-made inputs, the committed real02 fixture and, where present, P4b's real03 building
(runs/20261017-091212-full, not committed: those tests skip without it); no Blender, no model server.
"""
from __future__ import annotations

import copy
import gzip
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import _m11_room as M
from wenart import building as B
from wenart.blender import build as BD
from wenart.blender import cameras as C
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X
from wenart.blender import lighting as L
from wenart.blender import overrides as O
from wenart.blender import rest as R
from wenart.blender import textiles as T
from wenart.furniture import group_checks as GC
from wenart.furniture import infer as INF

ROOT = Path(__file__).resolve().parents[1]
REAL02 = ROOT / "tests" / "fixtures" / "m11_f1b" / "real02_building_final.json.gz"
P4B_REAL03 = ROOT / "runs" / "20261017-091212-full" / "results" / "furniture" / "real03" / "building_decor.json"
ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    rot = (float(front) - 270.0) % 360.0 if front is not None else 0.0
    return M.fp(pid, ftype, center, size, rotation=rot, front=front, **kw)


# --------------------------------------------------------------------------
# I_ingest: the schema takes the nightstand symbol's type method
# --------------------------------------------------------------------------

def test_a_nightstand_symbol_keeps_the_building_schema_valid():
    """Fails on the tree before the integration: infer.NIGHTSTAND_METHOD 'nightstand_symbol' was no value of the
    schema's type_method enum, so run_project would mark the building needs_review after the answers (P3 real04: 6
    proposals, 6 schema errors)."""
    bed = fp("b1", "bed_double", (2.5, 2.97), (1.6, 2.0), 270.0, type_method="block_name")
    lamp = fp("l1", "floor_lamp", (1.43, 3.745), (0.5, 0.45), 270.0, type_method="ai_two_pass")
    lamp["evidence"] = [{"file": "one_building.dwg", "method": "vector", "confidence": 0.9}]
    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed, lamp])
    props = [p for p in INF.infer_types(b) if p.get("type_method") == INF.NIGHTSTAND_METHOD]
    assert [p["piece_id"] for p in props] == ["l1"]
    out = INF.apply_inferences(b, props)
    assert next(f for f in out["furniture"] if f["id"] == "l1")["type_method"] == INF.NIGHTSTAND_METHOD
    assert not [e for e in B.validation_errors(out) if "type_method" in e]


# --------------------------------------------------------------------------
# A_agent / S_site: the entrance view's rule, the X7 sun rule, the facade sun, the entrance door kept
# --------------------------------------------------------------------------

ENTRANCE = {"door_id": "d_ent", "main": True, "centre": [15.603, 0.2253], "face": [15.603, 0.0003],
            "outward": [0.0, -1.0], "threshold_z": 0.0}
PLANNED_EXT7 = {"name": "ext_7", "kind": "exterior", "view": "entrance", "entrance": "d_ent", "sides": ["front"],
                "position": [18.34, -7.52, 1.6], "target": [10.5, 0.0, 1.6], "lens_mm": 26.0, "source": "searched",
                "fill": 34.15, "warning": "the building does not fit the frame",
                "visible_openings": ["win_1", "d_ent"]}


def _x6(cams, building=None):
    prep = {"outlines": {}, "roof": {"ridge_z": 3.5}, "main_facade": {"axis": "-y", "direction": [0.0, -1.0]}}
    out: list = []
    X._x6(building or {"site": {"entrances": [dict(ENTRANCE)]}}, prep, {"cameras": cams}, None, out)
    return out


def test_an_entrance_view_is_judged_by_its_door_not_by_the_whole_building():
    """Fails on the tree before the integration: _x6 applied FILL_RANGE and 'does not fit' to the planner's
    entrance view (real03's ext_7 at 8 m: fill 3415 %, a minor and a major X6 every round), and nothing stopped the
    agent's far pose (40, -45). The planner's pose turns 42 degrees off the door's axis (frame_fixed aims at the
    building's middle) and still passes: the bearing is taken from the door."""
    frontal = {"name": "ext_6", "kind": "exterior", "view": "frontal", "sides": ["front"], "position": [16.6, -32.0, 1.6],
               "target": [16.6, 0.0, 1.6], "lens_mm": 26.0}
    assert _x6([PLANNED_EXT7, frontal]) == []
    far = dict(PLANNED_EXT7, position=[40.0, -45.0, 1.6], target=[16.6, 0.0, 1.6], fill=None, warning=None)
    got = _x6([far, frontal])
    assert [(v["severity"], v["target"]) for v in got] == [("major", "ext_7")]
    assert "not an entrance view any more" in got[0]["message"] and "from the door d_ent" in got[0]["message"]
    hidden = dict(PLANNED_EXT7, visible_openings=["win_1"])
    assert "does not show its door d_ent" in _x6([hidden, frontal])[0]["message"]
    side = dict(PLANNED_EXT7, position=[27.0, -3.0, 1.6], target=[15.6, 0.0, 1.6])      # 75 degrees off the axis
    assert "off the door d_ent's axis" in _x6([side, frontal])[0]["message"]
    away = dict(PLANNED_EXT7, target=[30.0, -2.0, 1.6])                                   # the door out of the frame
    assert "off the view direction" in _x6([away, frontal])[0]["message"]


def test_one_entrance_rule_for_x6_the_build_and_the_agent():
    """The build's view check keeps 'entrance' while the pose frames the door and relabels it 'agent' otherwise
    (fails before: agent_exterior_view kept any entrance pose); the agent's tool uses the same function and numbers."""
    from wenart.agent import tools as TL

    assert (TL.ENTRANCE_VIEW_MAX_M, TL.ENTRANCE_VIEW_MAX_DEG) == (X.ENTRANCE_VIEW_MAX_M, X.ENTRANCE_VIEW_MAX_DEG)
    assert TL.entrance_problem({"site": {"entrances": [ENTRANCE]}}, PLANNED_EXT7, PLANNED_EXT7["position"],
                               PLANNED_EXT7["target"]) is None             # the planner's own pose (42 degrees off)
    keep = copy.deepcopy(dict(PLANNED_EXT7, policy="agent"))
    assert BD.agent_exterior_view(keep, (16.6, 7.0), 0.0, False, [ENTRANCE]) is None and keep["view"] == "entrance"
    moved = copy.deepcopy(dict(PLANNED_EXT7, policy="agent", position=[40.0, -45.0, 1.45], target=[16.6, 0.0, 1.45]))
    change = BD.agent_exterior_view(moved, (16.6, 7.0), 0.0, False, [ENTRANCE])
    assert change["view_was"] == "entrance" and moved["view"] == "agent" and moved["agent"]["view_was"] == "entrance"
    unknown = copy.deepcopy(moved)
    unknown["view"] = "entrance"
    assert BD.agent_exterior_view(unknown, (16.6, 7.0), 0.0, False, None) is None     # no records: nothing to judge


def test_an_agent_set_on_an_entrance_view_keeps_its_door():
    """Fails before: overrides.CAMERA_KEEP_KEYS had no 'entrance', so P4b's agent-moved ext_7 had entrance None; a
    replayed entrance view keeps its door too (cameras.REPLAY_OPTIONAL)."""
    plans = [dict(PLANNED_EXT7, index=7)]
    entry = {"action": "set", "view_id": "ext_7", "kind": "exterior", "position": [17.0, -8.0, 1.45],
             "target": [15.6, 0.0, 1.45], "reason": "closer to the door"}
    out, applied = O.apply_cameras(plans, [entry])
    assert applied[0]["result"] == "replaced" and out[0]["entrance"] == "d_ent" and out[0]["view"] == "entrance"
    assert "entrance" in C.REPLAY_OPTIONAL


@pytest.fixture(scope="module")
def real02():
    with gzip.open(REAL02, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def test_the_exterior_validator_keeps_the_sun_inside_the_x7_rule(real02):
    """Fails before: validate_exterior_override took 5-89 degrees and any azimuth, so a replay or another caller could
    set P4b's 55 degrees, or real02's style azimuth 210 that lights the back (main facade +y, north assumed 0; lead
    decision 4: that north stays)."""
    ok = X.validate_exterior_override
    assert not ok(real02, {"sun": {"elevation_deg": 55.0}})["ok"]
    assert not ok(real02, {"sun": {"elevation_deg": 2.0}})["ok"]
    assert ok(real02, {"sun": {"elevation_deg": 45.0}})["ok"]
    back = ok(real02, {"sun": {"elevation_deg": 40.0, "azimuth_deg": 210.0}})
    assert not back["ok"] and "lights the back" in back["failed"][0]
    assert ok(real02, {"sun": {"elevation_deg": 40.0, "azimuth_deg": 45.0}})["ok"]
    turned = dict(real02, site=dict(real02.get("site") or {}, north_deg=180.0))
    assert ok(turned, {"sun": {"elevation_deg": 40.0, "azimuth_deg": 225.0}})["ok"]       # 45 in the building frame


def test_an_elevation_only_sun_override_keeps_the_main_facade_sun():
    """Fails before: any sun override skipped sun_from_main_facade, so the style's 210 degrees lit real02's back."""
    assert BD.facade_sun_applies(None)
    assert BD.facade_sun_applies({"elevation_deg": {"value": 40.0, "was": 45.0}})
    assert not BD.facade_sun_applies({"azimuth_deg": {"value": 45.0, "was": 210.0}})


def test_the_policy_frontal_view_is_kept_at_its_best_share(monkeypatch):
    """Fails before: a frontal or elevation view whose every free candidate filled under MIN_BUILDING_SHARE was
    dropped (real03 with the agent's roof overhang 0.5 m: no frontal view, X6 'no frontal view'). The candidate with
    the best share among those that failed on the share alone is kept, with the warning; a blocked candidate never."""
    checks = {(1.0, 0.0, 1.6): dict(ok=False, why="share", building_share=0.075, blocked=0.0, aim_visible=True),
              (2.0, 0.0, 1.6): dict(ok=False, why="share", building_share=0.078, blocked=0.0, aim_visible=True),
              (3.0, 0.0, 1.6): dict(ok=False, why="blocked", building_share=0.2, blocked=0.44, aim_visible=True)}
    monkeypatch.setattr(E, "building_points", lambda model: np.zeros((1, 3)))
    monkeypatch.setattr(E, "frame_fixed", lambda pos, aim, pts, lens: {
        "lens_mm": lens, "shift_y": 0.0, "target": [aim[0], aim[1], pos[2]], "warning": None, "fill": 0.7,
        "fits": True})
    monkeypatch.setattr(E, "view_check", lambda model, pos, *a: dict(checks[tuple(pos)]))
    monkeypatch.setattr(E, "visible_openings", lambda *a: ["d1"])
    model = SimpleNamespace(inside=lambda pos: None)
    cands = [(p, f"{p[0]:g} m") for p in checks]
    dropped = E._try(model, {}, [], "ext_6", "frontal", cands, (0.0, 10.0, 1.6), lens_mm=26.0)
    assert dropped.get("dropped")
    kept = E._try(model, {}, [], "ext_6", "frontal", cands, (0.0, 10.0, 1.6), lens_mm=26.0, keep_best_share=True)
    assert not kept.get("dropped") and kept["position"] == [2.0, 0.0, 1.6] and kept["share_kept"] is True
    assert "kept: no candidate passed" in kept["warning"] and "7.8%" in kept["warning"]
    checks[(2.0, 0.0, 1.6)]["aim_visible"] = False
    checks[(1.0, 0.0, 1.6)]["blocked"] = 0.5
    assert E._try(model, {}, [], "ext_6", "frontal", cands, (0.0, 10.0, 1.6), lens_mm=26.0,
                  keep_best_share=True).get("dropped")


@pytest.mark.skipif(not P4B_REAL03.is_file(), reason="P4b's real03 building is not on this disk")
def test_real03_keeps_its_frontal_view_under_the_agents_roof_overhang_and_its_entrance_view_has_no_x6():
    """The P4b verifier's steps 1 and 5 on real03's building_decor.json: the planner's ext_7 gives no X6; with the
    agent's overhang 0.5 m the frontal ext_6 is still planned (share 0.076) and X6 has no 'no frontal view'."""
    b = json.loads(P4B_REAL03.read_text(encoding="utf-8"))
    b["agent_overrides"] = {"exterior": {"roof": {"overhang_m": 0.5}, "site": {"path": True, "fence": "fence",
                                                                                 "front_court": "yes"}}}
    prep = BD.prepare(b, "base", None)
    levels = X._base_levels(prep["building"])
    model = E.build_model(prep["building"], levels, prep["roof"], prep["site"])
    plans, _dropped = E.plan_exterior(model, prep["building"], levels, (prep["site"] or {}).get("plot") or [],
                                      variant=prep["variant"])
    by = {p["name"]: p for p in plans}
    # pin changed on purpose in the fix round after P5: the long, low framing (exterior.long_low, user decision of
    # 22 Oct 2026) lifts the frontal view from 0.076 to about 0.146, so it passes MIN_BUILDING_SHARE without the keep;
    # the keep_best_share path stays pinned by the synthetic test above
    assert by["ext_6"]["view"] == "frontal" and not by["ext_6"].get("share_kept")
    assert by["ext_6"]["score"]["building_share"] >= E.MIN_BUILDING_SHARE
    assert by["ext_6"]["long_low"]["ratio"] > E.LONG_LOW_RATIO
    assert by["ext_7"]["view"] == "entrance" and by["ext_7"]["entrance"] == "d_L0_019"
    out: list = []
    X._x6(b, prep, {"cameras": plans}, None, out)
    assert [v["message"] for v in out if v["check"] == "X6"] == []


# --------------------------------------------------------------------------
# L_render: the neutral rig of the circulation and wet rooms
# --------------------------------------------------------------------------

def test_halls_stairs_and_baths_get_a_neutral_rig_and_the_evening_rule_stays():
    """Fails before: every rig was 2700 K, so a hall seen through interior glazing from a daylight room read amber
    (real03 R/B 1.8-2.15). The kitchen stays warm (a look decision)."""
    day = {"colour_temperature_k": 5200}
    assert {t: L.rig_temperature_for(t, day) for t in ("hall", "stair", "bathroom", "wc", "bedroom", "living",
                                                         "dining", "kitchen")} == {
        "hall": 4000.0, "stair": 4000.0, "bathroom": 4000.0, "wc": 4000.0, "bedroom": 2700.0, "living": 2700.0,
        "dining": 2700.0, "kitchen": 2700.0}
    assert L.rig_temperature_for("hall", {"colour_temperature_k": 2200}) == 2200.0      # the evening rule
    hall = {"id": "r_hall", "room_type": "hall", "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]}
    plan = L.rig_plan(hall, [], 0.0, 2.7, lighting=day)
    assert plan["fixtures"] and all(f["temperature_k"] == 4000.0 for f in plan["fixtures"])


# --------------------------------------------------------------------------
# F_furniture: G14 of a drawn hall washer
# --------------------------------------------------------------------------

def test_g14_lets_a_drawn_washing_machine_stand_in_a_hall():
    """Fails before: F1 let real03's drawn hall washers stand (F's change) but G14 still flagged them as the wrong
    type in every round; a drawn toilet in a bedroom keeps its major G14."""
    washer = fp("wm", "washing_machine", (2.0, 0.4), (0.6, 0.6), 270.0, type_method="block_name")
    hall = M.building(w=4.0, h=2.0, room_type="hall", window=None, furniture=[washer])
    assert [v for v in GC.check_room(hall, ROOM) if v["check"] == "G14"] == []
    toilet = fp("to", "toilet", (3.8, 3.6), (0.4, 0.7), 270.0)
    bedroom = M.building(furniture=[toilet])
    assert [(v["severity"], v["target"]) for v in GC.check_room(bedroom, ROOM) if v["check"] == "G14"] == \
        [("major", "to")]
    added = dict(washer, source="added_by_ai")
    assert [v["target"] for v in GC.check_room(M.building(w=4.0, h=2.0, room_type="hall", window=None,
                                                          furniture=[added]), ROOM) if v["check"] == "G14"] == ["wm"]


# --------------------------------------------------------------------------
# F_furniture -> I_ingest: the L front of a corner-sofa candidate
# --------------------------------------------------------------------------

def test_a_corner_sofa_candidate_carries_its_l_front_and_the_context_rule_turns_it():
    """Fails before: the candidate path wrote l_outline without l_front (only the re-read path had it), so the
    reading's corner-sofa rule typed real03's f_L0_138 / f_L0_139 with no front and f_L0_139 kept the wrong turn."""
    from test_generic_symbols import _furn, _l_sofa
    from wenart.ingest.generic import reading as RD
    from wenart.ingest.pipeline import ProjectBuild

    _pieces, cands, _ = _furn(_l_sofa())
    det = cands[0]["item"].details
    assert det["l_front"] == cands[0]["front_candidates"][0]["front_deg"] == 270.0
    sofa = M.fp("s1", "unknown", (2.3, 3.2), (2.6, 1.6), front=None)
    build = ProjectBuild(M.building(room_type="living", window=None, furniture=[sofa]))
    RD.context_types(build, {"s1": SimpleNamespace(details=dict(det))})
    got = next(f for f in build.building["furniture"] if f["id"] == "s1")
    assert got["type"] == "sofa_corner" and got["shape"] == "L" and got["front_deg"] == 270.0


# --------------------------------------------------------------------------
# F_furniture -> blender rest / textiles: the headboard in the bed's head half
# --------------------------------------------------------------------------

def _bed(extra):
    from test_decor_rest import BED_FP, boxes_mesh

    v, f = boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 0.94, 0.30), (-0.78, -0.98, 0.30, 0.78, 0.92, 0.58),
                       (-0.8, 0.94, 0.0, 0.8, 1.0, 1.10)] + extra, BED_FP["center"], BED_FP["rotation_deg"])
    return R.MeshCaster(v, f)


@pytest.mark.parametrize("extra", [[(-0.8, -1.0, 0.0, 0.8, -0.95, 0.70)],                 # a footboard over the top
                                   [(-0.78, -0.98, 0.58, 0.78, -0.70, 0.64)],             # a duvet roll at the foot
                                   [(-0.70, -0.60, 0.58, 0.70, 0.60, 0.59)]],             # a 1 cm crowned mattress
                         ids=["footboard", "duvet-roll", "crown"])
def test_bed_cushions_and_pillows_rest_against_the_headboard_in_the_head_half(extra):
    """Fails before (footboard, duvet roll): the back rays started 0.2 m in front of the foot and took the footboard
    or the roll for the headboard; the cushion was 'not rested' and the bed got no bedding (P4b real03 f_L0_070,
    f_L0_141)."""
    from test_decor_rest import BED_FP, piece

    caster = _bed(extra)
    cushion = T.cushion_mesh(0.5, 0.15, 0.5)
    item = {"id": "p", "type": "cushion", "rotation_deg": 90.0,
            "center": list(R.to_world(BED_FP["center"], 90.0, -0.4, 1.0 - 0.175))}
    plan = R.plan_decor(item, piece("bed_double", BED_FP), caster, cushion["verts"], cushion["faces"], "headboard",
                        lean_deg=12.0)
    assert "not_rested" not in plan, plan.get("not_rested")
    y = R.to_local(BED_FP["center"], 90.0, *plan["pose"]["center"])[1]
    assert 0.94 - 0.30 < y < 0.94                                     # against the headboard face at local y 0.94
    got = T.duvet_and_pillows(caster, BED_FP, 0.0)
    assert got is not None and all(v > 0.3 for v in got["record"]["pillow_local_y"])
    assert got["record"]["duvet_rect_local"][3] > 0.0 and got["record"]["head_problems"] == []


def test_a_headboard_hit_that_leaves_the_item_in_the_foot_half_gives_way_to_the_back_edge():
    """A bolster lying across the middle of the bed (local y 0.03-0.10) stops the mid-bed back rays at once: the
    cushion would sit with its centre in the foot half, so the footprint's back edge is the back (a mutation that
    keeps such a hit puts the centre at local y < 0)."""
    from test_decor_rest import BED_FP

    caster = _bed([(-0.7, 0.03, 0.58, 0.7, 0.10, 0.75)])
    planned = R.to_world(BED_FP["center"], 90.0, -0.4, 0.8)
    pose = R.place_leaning(caster, BED_FP, planned, (0.5, 0.15, 0.5), lean_deg=12.0, bed=True)
    assert pose is not None and pose["how"].startswith("no backrest hit")
    assert R.to_local(BED_FP["center"], 90.0, *pose["center"])[1] > 0.5


def test_bedding_in_the_foot_half_is_named():
    rec = {"pillow_local_y": [0.49, -0.6], "duvet_rect_local": [-1.0, -1.2, 1.0, -0.1]}
    assert T.bedding_head_problems(rec) == ["pillow 2 lies in the foot half (local y -0.60 m)",
                                            "the duvet's head edge is in the foot half (local y -0.10 m)"]
    assert T.bedding_head_problems({"pillow_local_y": [0.5], "duvet_rect_local": [-1, -1, 1, 0.4]}) == []


# --------------------------------------------------------------------------
# S_site -> agent: a near copy of another exterior view
# --------------------------------------------------------------------------

def test_the_agent_may_not_add_a_near_copy_of_an_exterior_view(tmp_path):
    """Fails before: nothing compared an exterior set/add with the other views (P4b showed ext_6 and ext_7 with the
    same frontal view). Within 6 m and 15 degrees of another view it is refused and counted as a try; the camera of
    the same name is left out, and a pose 8 m away or turned 40 degrees passes this rule."""
    from test_agent_loop_p4b import cam, camera_project
    from wenart.agent import tools as TL

    ctx = camera_project(tmp_path)
    reg = TL.build_registry()
    copy_of_2 = reg.call(ctx, "add_camera", cam("ext_9", [22.0, -12.0, 1.45], [6.5, 1.0, 1.45]))
    assert not copy_of_2["accepted"] and copy_of_2["failed_checks"][0].startswith("duplicate: ext_9")
    assert "from ext_2" in copy_of_2["failed_checks"][0] and ctx.tries["ext_9"] == 1
    assert TL.duplicate_view_problem(ctx, "ext_2", dict(cam("ext_2", [22.0, -12.0, 1.45], [6.5, 1.0, 1.45]),
                                                        action="set")) is None
    far = TL.duplicate_view_problem(ctx, "ext_9", dict(cam("ext_9", [28.0, -15.0, 1.45], [6.0, 1.5, 1.45]),
                                                       action="add"))
    turned = TL.duplicate_view_problem(ctx, "ext_9", dict(cam("ext_9", [21.0, -11.0, 1.45], [21.0, 10.0, 1.45]),
                                                          action="add"))
    assert far is None and turned is None
    assert math.isclose(TL.DUPLICATE_VIEW_M, 6.0) and math.isclose(TL.DUPLICATE_VIEW_DEG, 15.0)
