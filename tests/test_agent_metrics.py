"""Agent metrics (docs/milestone12.md §5.5 D20): from the decision log and the memory of a run, and across runs in
``results/compare/<p>/agent_metrics.md``. The M11 baseline is computed from the committed real03 log (run 3 =
events from seq 184, §1.4: 5 accepted, 73 rejected, 35 rooms with open critical or major findings, edits in 11)."""
from __future__ import annotations

import json
from pathlib import Path

from wenart.agent import metrics as MX

ROOT = Path(__file__).resolve().parents[1]


def test_the_m11_real03_run3_baseline():
    log = json.loads((ROOT / "results" / "agent" / "real03" / "log.json").read_text())
    m = MX.compute(log, since_seq=184)
    assert (m["edits"]["accepted"], m["edits"]["rejected"]) == (5, 73)
    assert m["rooms"]["fixable"] == 35 and m["rooms"]["planner"] == 11 and m["rounds"] == 2
    assert m["edits"]["rejected_by_reason"]["drawn_lock"] == 39 and m["edits"]["rejected_by_reason"]["max_tries"] == 8
    assert m["edits"]["by_tool"]["move_piece"] == {"accepted": 1, "rejected": 30}
    assert m["memory"]["repeats_refused"] == 0 and m["memory"]["plans"] == 0
    assert m["findings"]["before_totals"]["critical"] == 18


def test_reason_keys():
    assert MX.reason_of(["memory: the same edit was rejected in round 1: x"]) == "memory"
    assert MX.reason_of(["f_L0_043: no_overlap"]) == "no_overlap"
    assert MX.reason_of(["score: plausibility 67 -> 60 (F3 f1: x)"]) == "score" and MX.reason_of([]) == "rejected"


def test_compare_rows_across_runs(tmp_path):
    log = json.loads((ROOT / "results" / "agent" / "real03" / "log.json").read_text())
    base = MX.compute(log, since_seq=184)
    md = tmp_path / "agent_metrics.md"
    MX.update_compare(md, "M11 run 3 (oesbppzw7hsnmb)", base)
    better = json.loads(json.dumps(base))
    better["edits"].update(accepted=30, rejected=10, accepted_share=0.75)
    MX.update_compare(md, "M12 P5", better)
    MX.update_compare(md, "M12 P5", better)                 # the same label replaces its row
    text = md.read_text()
    assert text.count("| M12 P5 |") == 1 and "| M11 run 3 (oesbppzw7hsnmb) |" in text
    assert "| 5 / 73 | 6 | 11 / 35 | 18 -> 17 |" in text and "| 30 / 10 | 75 |" in text
    rows = json.loads((tmp_path / "agent_metrics.json").read_text())["rows"]
    assert [r["label"] for r in rows] == ["M11 run 3 (oesbppzw7hsnmb)", "M12 P5"]
