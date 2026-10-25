"""Before / after against the project's latest run (wenart/report/latest.py; user rule of 25 Oct 2026: "From now on
every run is against its latest run compare not according to milestones"). CPU, files only."""
import json
import sys

from wenart.report import __main__ as RM
from wenart.report import latest as LT


def _run(root, job, project="p", previews=("cam_a", "ext_1"), building=True, stamp="T000000Z"):
    """A collected run in the committed results layout: ``<root>/final/<p>`` with a final manifest."""
    final = root / "final" / project
    final.mkdir(parents=True, exist_ok=True)
    (final / "final_manifest.json").write_text(json.dumps({"run_id": f"{job}-{job[:8]}{stamp}",
                                                           "views": [{"camera": c} for c in previews]}))
    for c in previews:
        (final / f"{c}_final_preview.jpg").write_bytes(b"\xff\xd8jpg")
    if building:
        (root / "furniture" / project).mkdir(parents=True, exist_ok=True)
        (root / "furniture" / project / "building_final.json").write_text("{}")
    (root / "run" / project).mkdir(parents=True, exist_ok=True)
    (root / "run" / project / "build.json").write_text("{}")
    return final


def test_the_latest_run_before_this_one_is_the_baseline(tmp_path):
    runs, committed = tmp_path / "runs", tmp_path / "latest"
    m13 = _run(tmp_path / "m13", "20261023-135954-full")
    old = _run(runs / "20261024-083434-full" / "results", "20261024-083434-full")
    _run(runs / "20261025-072303-full" / "results", "20261025-072303-full", previews=())   # stopped: no renders
    cut = _run(runs / "20261025-115105-full" / "results", "20261025-115105-full", building=False)
    fetched = _run(runs / "20261025-141109-fetch_results" / "results", "20261025-115105-full")
    new = _run(runs / "20261025-180008-full" / "results", "20261025-180008-full")
    dirs = (committed, tmp_path / "m13")
    found = LT.latest_run(new, runs_dir=runs, committed=dirs)
    assert found.job == "20261025-115105-full" and found.final_dir == fetched     # the more complete folder
    assert LT.latest_run(cut, runs_dir=runs, committed=dirs).final_dir == old    # never itself, never a later run
    assert LT.latest_run(old, runs_dir=runs, committed=dirs).final_dir == m13    # only the milestone run is older
    assert LT.latest_run(m13, runs_dir=runs, committed=dirs) is None


def test_a_run_becomes_the_latest_and_a_new_session_finds_it(tmp_path):
    runs, latest = tmp_path / "runs", tmp_path / "latest"
    _run(runs / "20261025-115105-full" / "results", "20261025-115105-full", building=False)
    fetched = _run(runs / "20261025-141109-fetch_results" / "results", "20261025-115105-full")
    rec = LT.promote(runs / "20261025-115105-full" / "results" / "final" / "p", runs_dir=runs, latest=latest)
    assert rec["job"] == "20261025-115105-full" and rec["previews"] == 2
    assert (latest / "furniture" / "p" / "building_final.json").is_file()      # filled from the fetch job's folder
    assert (latest / "final" / "p" / "cam_a_final_preview.jpg").is_file() and (latest / "run" / "p" / "build.json").is_file()
    assert json.loads((latest / LT.INDEX).read_text())["p"]["run_id"].startswith("20261025-115105-full")
    # a new session: no runs/ folder; the committed copy is the "before" of the next run
    new = _run(tmp_path / "new" / "results", "20261025-180008-full")
    found = LT.latest_run(new, runs_dir=tmp_path / "no-runs", committed=(latest,))
    assert found.source == "latest" and found.job == "20261025-115105-full"
    assert fetched.is_dir()
    # promoting the next run replaces the project's copy (git keeps the old one)
    (latest / "final" / "p" / "old_only_final_preview.jpg").write_bytes(b"x")
    LT.promote(new, runs_dir=tmp_path / "no-runs", latest=latest)
    assert not (latest / "final" / "p" / "old_only_final_preview.jpg").exists()
    assert json.loads((latest / LT.INDEX).read_text())["p"]["job"] == "20261025-180008-full"


def test_the_report_takes_the_latest_run_by_default(tmp_path, monkeypatch, capsys):
    runs = tmp_path / "runs"
    _run(runs / "20261024-053145-full" / "results", "20261024-053145-full")
    new = _run(runs / "20261025-200000-full" / "results", "20261025-200000-full")
    monkeypatch.setattr(LT, "RUNS", runs)
    monkeypatch.setattr(LT, "COMMITTED", ())
    monkeypatch.setattr(sys, "argv", ["wenart.report", "sheets13", "--out", str(new), "--dir", str(tmp_path / "s")])
    assert RM.main() == 0
    assert "the latest run before this one, run 20261024-053145-full" in capsys.readouterr().out
    index = json.loads((tmp_path / "s" / "sheets13.json").read_text())
    assert index["labels"] == ["before: run 20261024-053145-full", "after: run 20261025-200000-full"]
    assert LT.job_of("20261025-115105-full-20261025T115639Z") == "20261025-115105-full"
