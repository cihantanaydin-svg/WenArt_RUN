"""27 Nov 2026 (check pod 2smyy0ktv63y40, a structure run): a stage's building counts for Argus only when the run
manifest says its stage ran in this run. The agent stage's building of a full run of 2 Nov stayed on the volume and
C1 called 799 rooms, walls and openings of the run lost between "layout" and "agent"."""
from __future__ import annotations

from wenart.audit import inputs as IN


def _manifest(statuses: dict) -> dict:
    return {"started_utc": "2026-11-27T06:14:11Z",
            "projects": [{"name": "p", "stages": [{"stage": s, "status": v} for s, v in statuses.items()]}]}


def test_a_stage_that_did_not_run_is_not_compared():
    stages = [("reading", {}), ("fit", {}), ("layout", {}), ("agent", {"rooms": []}), ("build", {})]
    m = _manifest({"pipeline_final": "ok", "fit": "ok", "layout": "ok", "decor": "ok", "refit": "ok",
                   "build": "ok", "polish": "skipped"})
    kept, stale = IN.stages_of_run(stages, m, "p")
    assert [n for n, _ in kept] == ["reading", "fit", "layout", "build"]
    assert stale == [{"record": "stage agent", "why": "stale: its stage did not run in this run (not run); the file "
                                                      "an earlier run left is not compared"}]


def test_a_skipped_or_failed_stage_is_stale_and_a_reused_one_counts():
    stages = [("reading", {}), ("decor", {}), ("final", {})]
    kept, stale = IN.stages_of_run(stages, _manifest({"pipeline": "reused", "decor": "skipped", "refit": "failed"}),
                                   "p")
    assert [n for n, _ in kept] == ["reading"]
    assert [s["record"] for s in stale] == ["stage decor", "stage final"]
    assert "decor skipped" in stale[0]["why"] and "refit failed" in stale[1]["why"]


def test_without_a_run_manifest_every_stage_is_kept():
    stages = [("reading", {}), ("agent", {})]
    assert IN.stages_of_run(stages, None, "p") == (stages, [])
    assert IN.stages_of_run(stages, {"projects": [{"name": "other", "stages": []}]}, "p") == (stages, [])


def test_a_structure_run_drops_the_agent_records_and_the_bare_build_explains_movable_pieces():
    from wenart.audit import conservation as CV
    m = dict(_manifest({"pipeline_final": "ok", "layout": "ok", "build": "ok"}), profile="structure")
    assert IN.bare_run(m) and IN.agent_ran(m, "p") is False and IN.agent_ran(None, "p") is None
    layout = {"furniture": [{"id": "f1", "type": "sofa", "source": "from_documents"},
                            {"id": "f2", "type": "toilet", "source": "from_documents"},
                            {"id": "f3", "type": "stair", "source": "inferred"}]}
    stages = [("layout", layout), ("build", {"furniture": []})]
    found = {f["target"]: f["severity"] for f in CV.audit(stages, None, bare=True)["findings"] if f["check"] == "C1"}
    assert found == {"f1": "info", "f2": "major", "f3": "major"}    # the sofa is left out by design; the toilet and
    full = {f["target"]: f["severity"] for f in CV.audit(stages, None)["findings"] if f["check"] == "C1"}
    assert full == {"f1": "major", "f2": "major", "f3": "major"}    # the stair are fixed: still lost if not built


def test_a_shower_room_reads_as_a_bathroom_by_its_shower():
    from wenart.blender import model_review as M
    assert M.shower_room({"label": "Duş"}) and M.shower_room({"label": "DUŞ/WC"}) and M.shower_room({"label": "Shower"})
    assert not M.shower_room({"label": "Banyo"}) and not M.shower_room({"label": "Duşakabin"})
    built = {"rooms": [{"id": "r1", "room_type": "bathroom", "label": "Duş"},
                       {"id": "r2", "room_type": "bathroom", "label": "Banyo"}],
             "furniture": [{"id": "f1", "type": "shower", "room_id": "r1"}, {"id": "f2", "type": "shower", "room_id": "r2"}]}
    found, _n = M.rooms_make_sense(built, None)
    assert {(v["target"], v["severity"]) for v in found if v["check"] == "M7"} == {("r2", "critical"), ("r2", "major")}
