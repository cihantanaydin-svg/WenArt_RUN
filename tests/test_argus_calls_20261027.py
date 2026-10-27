"""Argus's own tool calls made valid before they run (27 Oct 2026, user: "make Argus fix everything itself, give it
more power"; pod run 20261026-224516-full: 0 of 94 Argus edits accepted, most for arguments no tool takes): the tool
help with every argument's shape, the valid values, the code's repairs, the id checks, the model's one repair call,
and the camera tools' ``show`` (the AI names what a view must show, the code gives the pose)."""
from __future__ import annotations

import json

from test_agent_helpers import FakeEdits, fake_validators, project
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.agent import tools as TL
from wenart.agent.model import MockModel
from wenart.audit import calls as CL


def _ctx(tmp_path, **kw):
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    kw.setdefault("apply_edit", FakeEdits())
    kw.setdefault("validators", fake_validators())
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out), **kw)


def _valid(ctx) -> CL.Valid:
    return CL.Valid(ctx.building, ctx.scene, catalog=None)


def test_shape_names_types_values_and_ranges():
    assert CL.shape({"enum": ["a", "b"]}) == "one of a|b"
    assert CL.shape({"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}) == \
        "[number, number, number]"
    assert CL.shape({"type": "number", "minimum": 14, "maximum": 50}) == "number 14..50"
    assert CL.shape({"type": "object", "additionalProperties": {"type": "string"}}) == "{name: string}"
    site = CL.shape({"type": "object", "minProperties": 1, "properties": {"trees": {"type": "integer"}}})
    assert site == "{trees: integer} (at least one key)"
    help_lines = CL.tool_help(TL.build_registry(), ["set_camera", "place_group", "relayout_room"])
    cam = next(h for h in help_lines if h.startswith("- set_camera("))
    assert "kind: one of interior|exterior" in cam and "position: [number, number, number]" in cam
    assert "show: list of string" in cam and "view_id*: string" in cam and "reason" not in cam.split("):")[0]
    assert "group*: one of balcony|bathroom_set" in next(h for h in help_lines if h.startswith("- place_group("))
    assert "choices: {name: string}" in next(h for h in help_lines if h.startswith("- relayout_room("))


def test_the_camera_tools_take_show_and_the_code_picks_the_pose(tmp_path):
    ctx = _ctx(tmp_path)
    reg = TL.build_registry()
    before = ctx.camera("cam_r1_1")["position"]
    res = reg.call(ctx, "set_camera", {"view_id": "cam_r1_1", "show": ["f1"], "reason": "show the bed"})
    assert res["accepted"], res
    cam = OV.Overrides(ctx.project_out).agent_overrides()["cameras"][0]
    assert cam["kind"] == "interior" and cam["room_id"] == "r1" and "show" not in cam
    assert cam["position"] != before and len(cam["target"]) == 3
    bad = reg.call(ctx, "set_camera", {"view_id": "cam_r2_1", "show": ["f1"], "reason": "a piece of another room"})
    assert not bad["accepted"] and "f1 not in r2" in bad["failed_checks"][0]
    ext = reg.call(ctx, "set_camera", {"view_id": "ext_1", "show": ["f1"], "reason": "an exterior view"})
    assert not ext["accepted"] and "interior poses only" in ext["failed_checks"][0]


def test_poses_showing_returns_the_poses_that_show_the_pieces(tmp_path):
    from wenart.blender import camsearch as CSR

    ctx = _ctx(tmp_path)
    room = next(r for r in ctx.building["rooms"] if r["id"] == "r1")
    poses, not_here = CSR.poses_showing(room, ctx.building, ["f1", "f2", "f3"])
    assert not_here == ["f3"] and poses and set(poses[0]["shows"]) <= {"f1", "f2"} and poses[0]["shows"]
    assert len(poses[0]["shows"]) >= len(poses[-1]["shows"]) and poses[0]["lens_mm"] in (16.0, 18.0)


def test_the_code_repairs_the_calls_of_pod_run_224516(tmp_path):
    ctx = _ctx(tmp_path)
    reg = TL.build_registry()
    valid = _valid(ctx)
    # camera kind 'room', a pose at the origin, a 24 mm lens: the view's kind, the code picks the pose, the lens rule
    a, errs, notes = CL.vet({"tool": "set_camera", "args": {"view_id": "cam_r1_1", "kind": "room", "position": [0, 0, 1.6],
                                                              "target": [0, 0, 1.0], "lens_mm": 24}},
                            valid, reg, {"target": "r1", "message": "the bed is missing from the frame"})
    assert not errs, errs
    assert a["args"]["kind"] == "interior" and a["args"]["show"] == ["f1"] and "position" not in a["args"]
    assert "lens_mm" not in a["args"] and any("kind 'room'" in n for n in notes)
    # a piece id as the view id: the piece's room's view shows it
    a, errs, _n = CL.vet({"tool": "set_camera", "args": {"view_id": "f2"}}, valid, reg, None)
    assert not errs and a["args"]["view_id"] == "cam_r1_1" and a["args"]["show"] == ["f2"]
    # an optional argument that does not match its schema is left out; a group word the program knows otherwise
    a, errs, _n = CL.vet({"tool": "relayout_room", "args": {"room_id": "r1", "candidate": 1, "choices": 2}},
                         valid, reg, None)
    assert not errs and a["args"] == {"room_id": "r1", "candidate": 1}
    a, errs, _n = CL.vet({"tool": "place_group", "args": {"room_id": "r2", "group": "living"}}, valid, reg, None)
    assert not errs and a["args"]["group"] == "seating"
    # nothing left after the repairs, a ground look that is none, a wrong look for a slot, unknown ids
    _a, errs, _n = CL.vet({"tool": "set_exterior", "args": {"site": "high_poly_trees"}}, valid, reg, None)
    assert any("no argument of set_exterior is left" in e for e in errs)
    _a, errs, _n = CL.vet({"tool": "set_exterior", "args": {"ground": "textured_terrain"}}, valid, reg, None)
    assert any("no ground look" in e and "grass" in e for e in errs)
    _a, errs, _n = CL.vet({"tool": "set_material", "args": {"slot": "frames", "look_id": "dark_wood"}}, valid, reg,
                          None)
    assert any("no look of the slot frames" in e and "steel_black" in e for e in errs)
    _a, errs, _n = CL.vet({"tool": "retype_piece", "args": {"piece_id": "f_nope", "type": "sofa"}}, valid, reg, None)
    assert any("no piece 'f_nope'" in e for e in errs)


class _Catalog:
    def __init__(self, entries):
        self.entries = {e["id"]: e for e in entries}

    def entry(self, i):
        return self.entries.get(i)

    def candidates(self, t):
        return [e for e in self.entries.values() if e["type"] == t]


def test_swap_model_names_real_models_only(tmp_path):
    ctx = _ctx(tmp_path)
    cat = _Catalog([{"id": "bed_a", "type": "bed_double", "bbox_m": [1.6, 2.0, 1.0], "styles": ["modern"]},
                    {"id": "bed_b", "type": "bed_double", "bbox_m": [1.8, 2.1, 1.0]},
                    {"id": "sofa_a", "type": "sofa", "bbox_m": [2.0, 0.9, 0.8]}])
    valid = CL.Valid(ctx.building, ctx.scene, catalog=cat)
    piece = valid.pieces["f1"]
    opts = valid.model_options(piece)
    assert [o.split(" ")[0] for o in opts][:2] in (["bed_a", "bed_b"], ["bed_b", "bed_a"]) and "sofa_a" not in str(opts)
    reg = TL.build_registry()
    _a, errs, _n = CL.vet({"tool": "swap_model", "args": {"piece_id": "f1", "asset_id": "bed_double_002"}}, valid, reg)
    assert any("no catalogue model 'bed_double_002'" in e and "bed_a" in e for e in errs)
    _a, errs, _n = CL.vet({"tool": "swap_model", "args": {"piece_id": "f1", "asset_id": "sofa_a"}}, valid, reg)
    assert any("is a sofa model, not a bed_double" in e for e in errs)
    _a, errs, _n = CL.vet({"tool": "swap_model", "args": {"piece_id": "f1", "asset_id": "bed_b"}}, valid, reg)
    assert errs == []


def test_vet_all_drops_duplicates_repairs_with_the_model_and_drops_the_rest(tmp_path):
    ctx = _ctx(tmp_path)
    reg = TL.build_registry()
    valid = _valid(ctx)
    acts = [{"id": "x1", "tool": "set_camera", "args": {"view_id": "cam_r1_1", "show": ["f1"]}, "finding_id": "a:F1"},
            {"id": "x2", "tool": "set_camera", "args": {"view_id": "cam_r1_1", "show": ["f2"]}, "finding_id": "a:F2"},
            {"id": "x3", "tool": "set_material", "args": {"slot": "floor", "look_id": "oak_floor"},
             "finding_id": "a:F3"},
            {"id": "x4", "tool": "set_exterior", "args": {"site": "trees"}, "finding_id": "a:F4"}]

    def reply(body):
        text = body["messages"][-1]["content"]
        assert "refused_because" in text and "wood_oak_light" in text and "- set_material(" in text
        rows = json.loads(text.split("The refused calls:\n", 1)[1])
        out = []
        for r in rows:
            if r["tool"] == "set_material":
                out.append({"id": r["id"], "args": json.dumps({"slot": "floor", "look_id": "wood_oak_light"}),
                            "drop": False})
            else:
                out.append({"id": r["id"], "args": "{}", "drop": True})
        return {"items": out}

    model = MockModel(critic=[reply])
    errors: list = []
    good, counts = CL.vet_all(model, acts, valid, reg, {}, help_lines=CL.tool_help(reg, ["set_material"]),
                              errors=errors)
    assert [g["id"] for g in good] == ["x1", "x3"] and good[1]["args"]["look_id"] == "wood_oak_light"
    assert "the model repaired its call" in good[1]["repaired"]
    assert good[0]["args"]["kind"] == "interior" and good[0]["repaired"]          # the view's kind, by code
    assert counts == {"calls": 4, "valid": 2, "code_repaired": 1, "model_repaired": 1, "dropped": 1, "duplicates": 1}
    assert len(errors) == 1 and "a:F4 set_exterior dropped" in errors[0]


def test_a_swap_keeps_the_project_style_chain():
    """Pod run 224516 (GPU test test_refit_library_models_fit_the_style): the agent's swaps pinned models of other
    styles; a swap to a model of no family of the project's chain is refused, one of a fallback family is taken."""
    from wenart.furniture import edit_ops as EO

    b = {"furniture": [{"id": f"f{i}", "type": "sofa", "asset": {"style_family": "scandinavian"}} for i in range(3)]}
    assert EO.off_style_refusal(b, {"id": "m", "styles": ["minimal"]}) is None          # scandinavian -> minimal
    assert EO.off_style_refusal(b, {"id": "n", "styles": ["neutral"]}) is None
    why = EO.off_style_refusal(b, {"id": "g", "styles": ["classic"]})
    assert "none of the project's chain scandinavian -> minimal -> modern" in why
    assert EO.off_style_refusal({"furniture": []}, {"id": "g", "styles": ["classic"]}) is None    # no family known


def test_the_working_building_knows_the_project_style_family(tmp_path):
    """Pod run 091638 (GPU test test_refit_library_models_fit_the_style again): the agent's working building was fitted
    before style.json existed (no asset names a family), so no swap was checked; the project's style.json family is
    stamped on it (``project.style_family``) when the tools load it, and the swap of a classic sofa is refused."""
    from wenart.furniture import edit_ops as EO

    b = {"project": {"id": "p"}, "furniture": [{"id": "f1", "type": "sofa", "asset": {"asset_id": "x"}}]}
    assert EO.off_style_refusal(b, {"id": "g", "styles": ["classic"]}) is None           # no family known
    assert EO.stamp_style_family(b, {"family": "scandinavian"}) == "scandinavian"
    assert b["project"]["style_family"] == "scandinavian" and "style.json" in b["project"]["style_family_source"]
    assert "scandinavian -> minimal" in EO.off_style_refusal(b, {"id": "g", "styles": ["classic"]})
    assert EO.stamp_style_family(b, {"family": "classic"}) == "scandinavian"              # never overwritten
    assert EO.stamp_style_family({"project": {}}, {"palette": {}}) is None
    out = project(tmp_path)
    style = json.loads((out / "style.json").read_text(encoding="utf-8"))
    (out / "style.json").write_text(json.dumps(dict(style, family="scandinavian")), encoding="utf-8")
    ctx = TL.ToolContext.load(out, round=1, model_id="mock/agent", log=LG.AgentLog(out, "toy", "mock/agent", "rev"),
                              overrides=OV.Overrides(out))
    assert EO._style_family_of(ctx.building) == "scandinavian"


def test_argus_learns_how_its_own_edits_fared(tmp_path):
    """27 Oct 2026: the problem log keeps per run how many of Argus's own edits code accepted per tool and why it
    refused the others (numbers generalised); the next run's prompt names them (``history_lines``)."""
    from wenart.audit import argus_ai as AX
    from wenart.audit import report as R

    log_path = tmp_path / "problem_log.json"
    for run_id, accepted in (("r1", 0), ("r2", 2)):
        rep = {"run_id": run_id, "project": "p", "score": 5.0, "severity": {}, "findings": [],
               "own_edits": {"tried": 3, "accepted": accepted, "tools": {"set_camera": [3, accepted]},
                             "refusals": {"set_camera": {"kind: 'room' is not one of [...]": 3 - accepted}}}}
        R.update_log(rep, log_path)
    log = json.loads(log_path.read_text(encoding="utf-8"))
    rec = R.own_record(log, "p")
    assert rec["set_camera"]["tried"] == 6 and rec["set_camera"]["accepted"] == 2
    assert rec["set_camera"]["refusals"]["kind: 'room' is not one of [...]"] == 4
    lines = AX.history_lines("p", path=log_path)
    assert any("your own set_camera edits: 2 of 6 accepted; refused for: kind: 'room'" in x for x in lines)
    assert R.own_record(log, "other") == {}


def test_c7_a_piece_left_out_while_an_ai_pass_named_a_fitting_type():
    """27 Oct 2026: a drawn piece left out as a rug outline while an AI pass named it a sofa that fits its size is a
    lost piece (C7, major, kind lost) with the typed fix Argus carries out through retype_piece; a rug no pass named
    otherwise, a named type that does not fit, and a detail (minor) are told apart."""
    from wenart.audit import argus_ai as AX
    from wenart.audit import conservation as CV

    def piece(pid, size, how, named, **kw):
        return dict({"id": pid, "type": "unknown", "room_id": "r1", "build": False, "inferred_as": how,
                     "inferred_reason": f"a {how}", "footprint": {"center": [1, 1], "size": list(size)},
                     "evidence": [{"method": "vector"}],
                     "type_candidates": [{"type": t, "pass": n} for n, t in enumerate(named, 1)]}, **kw)

    b = {"furniture": [piece("f1", (2.12, 0.78), "rug", ["unknown", "sofa"]),
                       piece("f2", (3.9, 1.65), "rug", []),
                       piece("f3", (2.12, 0.78), "rug", ["nightstand"]),
                       piece("f4", (0.4, 0.4), "detail", ["nightstand"])]}
    found = {f["target"]: f for f in CV.named_left_out(b)}
    assert set(found) == {"f1", "f4"}
    assert (found["f1"]["check"], found["f1"]["severity"], found["f1"]["kind"]) == ("C7", "major", "lost")
    assert found["f1"]["fix"] == {"action": "type_piece", "element_id": "f1", "type": "sofa"}
    assert found["f4"]["severity"] == "minor"
    actions, work, _revoke = AX.code_actions({"findings": [found["f1"]]}, b)
    assert [(a["tool"], a["args"]["piece_id"], a["args"]["type"]) for a in actions] == [("retype_piece", "f1", "sofa")]


def test_argus_cycle_look_only_when_the_round_still_fits():
    """27 Oct 2026 (pod run 091638: the cycle look used its 420 s, then the big loop's round stopped at the
    deadline): the look runs only when the final round fits after its budget."""
    import types

    from wenart.agent.loop import FINAL_ROUND_SHARE
    from wenart.run import scheduler as SCH

    def loop(now, deadline):
        return types.SimpleNamespace(deadline=deadline, margin_s=60.0, clock=lambda: now, estimate=lambda: 1000.0)
    need = 420.0 + FINAL_ROUND_SHARE * 1000.0 + 60.0
    assert SCH.argus_cycle_fits(loop(0.0, need + 1.0), 420.0)
    assert not SCH.argus_cycle_fits(loop(0.0, need - 1.0), 420.0)
    assert SCH.argus_cycle_fits(None, 420.0) and SCH.argus_cycle_fits(loop(0.0, None), 420.0)
