"""Milestone 12 track A: what the agent reads from track S (docs/milestone12.md §13.3; lead notes of 10 Oct 2026).

- a piece is built only when ``topdown.is_built`` says so (track S's ``decor.piece_is_built``: ``build`` not false,
  not ``unknown``, not a library gap the fit left unbuilt), and the brief, the top-down and the vision critic's id
  list all use it;
- the scene checks are read from the folder the build writes (``outputs/<p>/scene/checks``) or the contract's
  ``build/checks``;
- the build manifest's furniture summary gives findings: a decor item that did not rest (minor S5 on its host),
  and a failed build whose S5 file is missing (critical); ``scene_summary`` reports the counts.
"""
from __future__ import annotations

import json

from wenart.agent import brief as BR
from wenart.agent import critic_code as CC
from wenart.agent import topdown as TD


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
