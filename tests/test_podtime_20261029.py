"""29 Oct 2026 (user: "Give me the breakdown of the pod time for each pod how much time each thing is taking"): the
pod time of a run in buckets from its run manifest and stage logs (``wenart.report.podtime``)."""
import json

from wenart.report import podtime as PT


def _run(tmp_path):
    res = tmp_path / "20261028-154514-full" / "results"
    logs = res / "run" / "p" / "logs"
    logs.mkdir(parents=True)
    man = {"job": "20261028-154514-full", "started_utc": "2026-10-28T15:50:00Z", "finished_utc": "2026-10-28T16:50:00Z",
           "phases": [{"phase": 12, "start_utc": "2026-10-28T16:00:00Z", "end_utc": "2026-10-28T16:40:00Z"},
                      {"phase": 11, "seconds": 120.0}]}
    (res / "run_manifest.json").write_text(json.dumps(man))
    (logs / "build.log").write_text(
        "[wenart.run] 2026-10-27T10:00:00Z $ python -m wenart.blender.cli build --x\n"      # an older run's line
        "[wenart.run] 2026-10-27T10:05:00Z rc 0\n"
        "[wenart.run] 2026-10-28T16:00:00Z $ python -m wenart.blender.cli build --x\n"
        "[wenart.run] 2026-10-28T16:10:00Z rc 0\n")
    (logs / "check.log").write_text("[wenart.run] 2026-10-28T16:40:00Z $ python -m wenart.vision_check run\n"
                                    "[wenart.run] 2026-10-28T16:45:00Z rc 0\n")
    return res


def test_the_pod_time_adds_up_to_the_billed_minutes(tmp_path):
    bd = PT.breakdown(str(_run(tmp_path)), "p", minutes=70)
    rows = dict(bd["rows"])
    assert rows["Blender: build the scene"] == 600.0                      # only this run's build
    assert rows[PT.AGENT] == 30 * 60.0                                     # 16:10-16:40, inside the agent phase
    assert rows["pod start and setup (venvs, model downloads)"] == 286.0  # created 15:45:14 by the job id
    assert rows["GPU tests, run manifest"] == 120.0
    assert abs(bd["total_s"] - 70 * 60.0) < 1e-6
    md = PT.markdown(bd, "p")
    assert "| total | 70.0 | |" in md and "| 16:00:00 | 16:10:00 | 10.0 | build |" in md
