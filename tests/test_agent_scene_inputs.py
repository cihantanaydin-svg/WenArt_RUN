"""Milestone 12 track A: what the agent reads from tracks S and L (docs/milestone12.md §13.3; lead notes of 10 Oct
2026).

- a piece is built only when ``topdown.is_built`` says so (track S's ``decor.piece_is_built``: ``build`` not false,
  not ``unknown``, not a library gap the fit left unbuilt), and the brief, the top-down and the vision critic's id
  list all use it;
- the scene checks are read from the folder the build writes (``outputs/<p>/scene/checks``) or the contract's
  ``build/checks``;
- the build manifest's furniture summary gives findings: a decor item that did not rest (minor S5 on its host),
  and a failed build whose S5 file is missing (critical); ``scene_summary`` reports the counts;
- the ``levels`` tool shows track L's data (marks with kind and use, room floors, thresholds, ground, entrances,
  ``level_inference``, L-findings) and the level tools take track L's schemas (``LEVEL_EDIT_SCHEMAS``);
- track G's group findings are reported once (plausibility runs G1-G13, the group family adds the rest).
"""
from __future__ import annotations

import json

from wenart.agent import brief as BR
from wenart.agent import critic_code as CC
from wenart.agent import tools as TL
from wenart.agent import topdown as TD
from tests import _levels_fixture as LF


def piece(pid, ptype="sofa", **kw):
    return dict({"id": pid, "type": ptype, "room_id": "r1", "source": "from_documents",
                 "footprint": {"center": [1.0, 1.0], "size": [1.0, 0.8], "rotation_deg": 0.0}}, **kw)


def test_unknown_and_library_gaps_are_not_built():
    assert TD.is_built(piece("a"))
    assert not TD.is_built(piece("b", build=False))
    assert not TD.is_built(piece("c", "unknown"))
    assert not TD.is_built(piece("d", asset={"method": "none"}))
    assert TD.is_built(piece("e", asset={"method": "library"}))
    building = {"rooms": [{"id": "r1", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}],
                "furniture": [piece("a"), piece("c", "unknown"), piece("d", asset={"method": "none"})]}
    assert [p["id"] for p in TD.built_pieces(building, "r1")] == ["a"]
    assert BR.built(piece("a")) and not BR.built(piece("c", "unknown"))


def test_the_scene_checks_folder_is_where_the_build_writes(tmp_path):
    assert CC.scene_checks_dir(tmp_path) == tmp_path / "scene" / "checks"        # nothing yet: the build's folder
    (tmp_path / "build" / "checks").mkdir(parents=True)
    (tmp_path / "build" / "checks" / "scene_L0.json").write_text(json.dumps({"violations": []}))
    assert CC.scene_checks_dir(tmp_path) == tmp_path / "build" / "checks"
    (tmp_path / "scene" / "checks").mkdir(parents=True)
    (tmp_path / "scene" / "checks" / "scene_L0.json").write_text(json.dumps({"violations": [
        {"check": "S5", "severity": "critical", "target": "dec_1", "room_id": "r1", "message": "floats",
         "metrics": {"gap_m": 0.2}}]}))
    assert CC.scene_checks_dir(tmp_path) == tmp_path / "scene" / "checks"
    found = CC.scene_violations(CC.scene_checks_dir(tmp_path))
    assert found[0]["severity"] == "critical"


def _quiet():
    return {"plausibility_fn": lambda b: {"rooms": {}}, "exterior_fn": lambda b, s, r: {"violations": []},
            "views_fn": lambda b, r: {"views": {}}, "groups_fn": lambda b: {"rooms": {}},
            "levels_fn": lambda b, s, r: []}


def test_the_manifest_summary_gives_findings(tmp_path):
    building = {"rooms": [{"id": "r1"}], "furniture": [piece("f1", "bed_double")]}
    manifest = {"furniture": {"scene_checks": {"L0": {"S5": {"checked": 4, "failed": 1}}},
                              "decor_not_rested": [{"id": "dec_7", "type": "cushion", "host_id": "f1",
                                                    "support": "mattress", "reason": "gap 0.12 m", "attempts": 2,
                                                    "room_id": "r1"}],
                              "dressed_beds": ["f1"], "scene_checks_failed": True}}
    out = CC.run(building, manifest, None, scene_dir=tmp_path / "none", **_quiet())
    s5 = [f for f in out["findings"] if f["check"] == "S5"]
    assert {(f["severity"], f["target"]) for f in s5} == {("minor", "f1"), ("critical", None)}
    assert out["scene_summary"] == {"scene_checks": {"L0": {"S5": {"checked": 4, "failed": 1}}},
                                    "scene_checks_failed": True, "dressed_beds": 1, "decor_not_rested": 1}
    # The S5 violations of the scene file are there: no extra critical finding from the manifest flag.
    (tmp_path / "scene_L0.json").write_text(json.dumps({"violations": [
        {"check": "S5", "severity": "critical", "target": "dec_9", "room_id": "r1", "message": "sunk",
         "metrics": {}}]}))
    out = CC.run(building, manifest, None, scene_dir=tmp_path, **_quiet())
    crit = [f for f in out["findings"] if f["check"] == "S5" and f["severity"] == "critical"]
    assert [f["target"] for f in crit] == ["dec_9"]
    assert CC.run(building, None, None, **_quiet())["scene_summary"] == {}


def test_the_levels_tool_shows_track_l_data(tmp_path):
    from wenart.levels import checks, edits, model
    b = LF.building()
    b["level_marks"] = [LF.mark("lm_001", -0.30, kind="unknown", point=(3.0, 4.0)),
                        LF.mark("lm_002", -0.45, kind="ground_finished", point=(8.0, -3.0))]
    b = model.infer_levels(b)
    ctx = TL.ToolContext(project_out=tmp_path, building=b, level_checks=checks.check_levels)
    out = TL.t_levels(ctx, {})
    assert {m["id"] for m in out["marks"]} == {"lm_001", "lm_002"}
    assert all("kind" in m and "used_for" in m for m in out["marks"])
    assert out["level_inference"] == {k: (v[:20] if isinstance(v, list) else v)
                                      for k, v in b["level_inference"].items()}
    assert out["ground"]["points"] or out["ground"]["surface"] is not None or out["terrain"] is not None
    assert isinstance(out["findings"], list) and all("error" not in f for f in out["findings"])
    json.dumps(out)
    reg = TL.build_registry()
    for op in edits.LEVEL_EDIT_OPS:
        params = reg.tools[op].parameters
        assert params["required"] == edits.LEVEL_EDIT_SCHEMAS[op]["required"]
        assert set(params["properties"]) == set(edits.LEVEL_EDIT_SCHEMAS[op]["properties"])


def test_group_findings_are_reported_once():
    """Track G: plausibility runs G1-G13 (F5's place) and leaves G5's headboard part to F3; the group family adds
    only the rest (G14 here), so the critic reports one finding per fault."""
    def v(check, target, part=None):
        return {"check": check, "severity": "major", "target": target, "room_id": "r1", "message": check,
                "metrics": {"part": part} if part else {}}

    plaus = {"rooms": {"r1": {"score": 50, "violations": [v("G4", "f2"), v("F3", "f1")]}}, "mean": 50}
    groups = {"rooms": {"r1": [v("G4", "f2"), v("G5", "f1", "headboard"), v("G14", "f9")]}}
    q = dict(_quiet(), plausibility_fn=lambda b: plaus, groups_fn=lambda b: groups)
    out = CC.run({"rooms": [{"id": "r1"}], "furniture": []}, None, None, **q)
    assert sorted(f["id"] for f in out["findings"]) == ["c:F3:f1", "c:G14:f9", "c:G4:f2"]
    assert CC.FAMILY_OF["G14"] == "groups"


def test_needs_review_and_type_disagreements_reach_the_planner():
    """Milestone 12 (§4.1, track R): an untyped drawn piece left for review is a fixable NR finding (typing it or
    recording it as not furniture is the fix, although it is not built); a type disagreement is a minor RC finding."""
    from wenart.agent import brief as BR, critic_code as CC
    building = {"furniture": [{"id": "f_L0_090", "room_id": "r1", "type": "unknown", "build": False,
                               "source": "from_documents"}],
                "needs_review": [{"id": "f_L0_090", "kind": "untyped", "reason": "no size or context fits",
                                  "crop": "crops/f_L0_090.png", "room_id": "r1", "level_id": "L0"}],
                "conflicts": [{"id": "c1", "kind": "type_disagreement", "element_ids": ["f_L0_091"],
                               "description": "the drawing says sink, both passes said fridge",
                               "resolution": "drawn block name kept"}]}
    got = CC.reading_items(building)
    assert [(v["check"], v["severity"], v["target"]) for v in got] == [("NR", "major", "f_L0_090"),
                                                                      ("RC", "minor", "f_L0_091")]
    assert "crops/f_L0_090.png" in got[0]["message"]
    assert CC.FAMILY_OF["NR"] == CC.FAMILY_OF["RC"] == "reading"
    allowed = {"f_L0_090": {"retype_piece": {"allowed": True}, "mark_not_furniture": {"allowed": True}}}
    fixable, not_yours = BR.classify([CC.finding(v) for v in got[:1]], building, "r1", allowed, {}, {})
    assert [f["check"] for f in fixable] == ["NR"] and set(fixable[0]["tools"]) == {"retype_piece", "mark_not_furniture"}
    assert not not_yours
