"""The committed Milestone 13 runs (results/baseline/m13/final/<p>) stay, asked for with ``--baseline m13``; since the
user rule of 25 Oct 2026 the default "before" is the project's latest run (tests/test_report_latest.py); sheets13
refuses a project without any earlier run."""
import json
import sys
from pathlib import Path

from wenart.report import __main__ as RM

ROOT = Path(__file__).resolve().parents[1]


def test_the_committed_m13_baseline_of_real04_is_kept():
    found = RM.m13_baseline(ROOT / "runs" / "any-job" / "results" / "final" / "real04")
    assert found == ROOT / "results" / "baseline" / "m13" / "final" / "real04"
    for rel in ("furniture/real04/building_final.json", "renders/real04/scene_manifest.json",
                "final/real04/final_manifest.json", "agent/real04/log.json"):
        assert (RM.M13_BASELINE / rel).is_file(), rel
    final = json.loads((RM.M13_BASELINE / "final" / "real04" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final                                            # the Milestone 13 run (2799c88), never a later one
    assert RM.m13_baseline(ROOT / "x" / "final" / "no-such-project") is None


def test_sheets13_without_a_baseline_refuses_a_project_without_one(tmp_path, monkeypatch, capsys):
    run = tmp_path / "final" / "no-such-project"
    run.mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["wenart.report", "sheets13", "--out", str(run), "--dir", str(tmp_path / "s")])
    assert RM.main() == 2
    assert "no earlier run of no-such-project" in capsys.readouterr().err
