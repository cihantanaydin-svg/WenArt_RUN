"""CPU tests of the per-project gate validation (docs/milestone6.md §7.3, §9): ``wenart.gate.validate``,
``python -m wenart.gate validate`` and the logic of ``tests/gpu/test_polish.py::test_gate_validation_recorded``.

Calibrations are made the way ``gate calibrate`` makes them: records decided by the real
``wenart.gate.decide`` with the package thresholds, rates from ``wenart.gate.calibrate.summarise``.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from wenart.gate import decide
from wenart.gate import validate as GV
from wenart.gate.__main__ import main as gate_main
from wenart.gate.api import load_thresholds
from wenart.gate.calibrate import summarise

ROOT = Path(__file__).resolve().parents[1]
LIMITS = {"benign_accept_min": 0.95, "negative_reject_min": 0.90}


def metrics(thresholds: dict, good: bool) -> dict:
    """Metrics that pass every limit of ``thresholds`` (good) or fail the edges limits (bad)."""
    out = {}
    for check, th in thresholds.items():
        if check == "calibration" or not isinstance(th, dict):
            continue
        value = 1.0 if ("global_min" in th or "region_min" in th) else 0.0
        if not good and check == "edges":
            value = 0.5
        out[check] = {"global": value, "regions": {"f_1": value}, "skipped": {}}
    return out


def record(camera: str, control: str, magnitude, good: bool, thresholds: dict) -> dict:
    m = metrics(thresholds, good)
    decision, reasons, notes = decide(m, thresholds)
    return {"camera": camera, "control": control, "magnitude": magnitude, "object": None, "family": "benign",
            "small": False, "decision": decision, "reasons": reasons, "notes": notes, "metrics": m}


def calibration(n_benign=20, benign_bad=0, n_negative=20, negative_missed=0, thresholds=None, **extra) -> dict:
    """A calibration dict as ``gate calibrate`` writes it (rates from ``summarise``)."""
    th = load_thresholds() if thresholds is None else thresholds
    benign = [record("cam_a", "jpeg", i, i >= benign_bad, th) for i in range(n_benign)]
    negative = [record("cam_a", "shift", i, i < negative_missed, th) for i in range(n_negative)]
    cal = {"schema_version": "0.1", "kind": "gate_calibration", "project": "toy", "incomplete": False,
           "gate_code": "m5.2", "thresholds": copy.deepcopy(th), "views": ["cam_a"], "benign": benign,
           "negative": negative, "presumed_bad": [], "skipped": [], "warnings": [], "seconds": 1.0}
    cal.update(summarise(cal, th))
    cal.update(extra)
    return cal


def write_cal(out: Path, cal) -> Path:
    path = out / "gate" / "gate_calibration.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cal) if not isinstance(cal, str) else cal, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Decisions
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kw, decision", [
    ({}, "ok"),
    ({"n_benign": 20, "benign_bad": 1}, "ok"),                         # 0.95 = the limit: passes
    ({"n_benign": 20, "benign_bad": 2}, "flagged"),                    # 0.90 < 0.95, negatives fine
    ({"n_negative": 20, "negative_missed": 2}, "ok"),                  # 0.90 = the limit: passes
    ({"n_negative": 20, "negative_missed": 3}, "polish_disabled"),     # 0.85 < 0.90
    ({"benign_bad": 5, "negative_missed": 5}, "polish_disabled"),      # both fail: the negative limit decides
    ({"n_benign": 0}, "not_validated"),
    ({"n_negative": 0}, "not_validated"),
])
def test_decision_rules(kw, decision):
    out = GV.decide_validation(calibration(**kw), LIMITS, load_thresholds())
    assert out["decision"] == decision, out
    assert out["thresholds_match"] is True
    assert bool(out["reasons"]) is (decision != "ok")
    if decision == "flagged":
        assert out["pass_negative"] and not out["pass_benign"] and "benign" in out["reasons"][0]
    if decision == "polish_disabled":
        assert not out["pass_negative"] and any("geometry changes through" in r for r in out["reasons"])


def test_not_validated_cases():
    th = load_thresholds()
    missing = GV.decide_validation(None, LIMITS, th)
    assert missing["decision"] == "not_validated" and "missing" in missing["reasons"][0]
    cut = GV.decide_validation(calibration(incomplete=True), LIMITS, th)
    assert cut["decision"] == "not_validated" and "deadline" in cut["reasons"][0]
    assert cut["benign_accept"] == 1.0                     # the rates are still reported
    no_rates = calibration()
    no_rates.pop("rates")
    assert GV.decide_validation(no_rates, LIMITS, th)["decision"] == "not_validated"
    assert GV.decide_validation([1, 2], LIMITS, th)["decision"] == "not_validated"
    other = copy.deepcopy(th)
    other["edges"]["global_min"] = 0.5
    stale = GV.decide_validation(calibration(thresholds=other), LIMITS, th)
    assert stale["decision"] == "not_validated" and stale["thresholds_match"] is False
    assert "other thresholds" in stale["reasons"][-1]
    # Only the calibration notes changed (e.g. the user's OK): still the same thresholds.
    notes = copy.deepcopy(th)
    notes["calibration"]["user_ok"] = "2026-10-05"
    assert GV.decide_validation(calibration(thresholds=notes), LIMITS, th)["decision"] == "ok"
    # Without thresholds to compare (None) the recorded ones are not checked.
    assert GV.decide_validation(calibration(thresholds=other), LIMITS, None)["decision"] == "ok"


def test_rates_are_read_not_recomputed():
    cal = calibration()
    cal["rates"]["benign_accept"] = 0.5                    # the file's own number is what counts
    out = GV.decide_validation(cal, LIMITS, load_thresholds())
    assert out["decision"] == "flagged" and out["benign_accept"] == 0.5 and out["n_benign"] == 20


def test_validation_config():
    assert GV.load_validation_config() == LIMITS
    assert GV.DECISIONS == ("ok", "flagged", "polish_disabled", "not_validated")


@pytest.mark.parametrize("text", ["benign_accept_min: 1.5\nnegative_reject_min: 0.9\n",
                                  "negative_reject_min: 0.9\n", "benign_accept_min: yes\nnegative_reject_min: 0.9\n"])
def test_bad_validation_config(tmp_path, text):
    path = tmp_path / "v.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="validation.yaml"):
        GV.load_validation_config(path)


# --------------------------------------------------------------------------
# Files and CLI
# --------------------------------------------------------------------------

def test_validate_writes_the_file(tmp_path):
    out = tmp_path / "outputs" / "synthetic-04"
    cal_path = write_cal(out, calibration(benign_bad=2, project="synthetic-04"))
    data = GV.validate(out)
    path = out / "gate" / "gate_validation.json"
    assert json.loads(path.read_text(encoding="utf-8")) == data
    for key in ("benign_accept", "negative_reject", "n_benign", "n_negative", "pass_benign", "pass_negative",
                "decision", "reasons"):
        assert key in data, key
    assert data["kind"] == "gate_validation" and data["schema_version"] == "0.1" and data["project"] == "synthetic-04"
    assert data["decision"] == "flagged" and data["polish_allowed"] is True
    assert (data["benign_accept"], data["negative_reject"], data["n_benign"], data["n_negative"]) == (0.9, 1.0, 20, 20)
    assert data["limits"] == LIMITS
    from wenart.canonical import canonical_sha256
    assert data["calibration"] == {"path": "gate_calibration.json", "sha256": canonical_sha256(cal_path),
                                   "incomplete": False, "thresholds_match": True}


def test_validate_missing_and_broken_calibration(tmp_path):
    out = tmp_path / "outputs" / "p"
    out.mkdir(parents=True)
    data = GV.validate(out)
    assert data["decision"] == "not_validated" and data["polish_allowed"] is False and data["project"] == "p"
    assert data["calibration"]["path"] is None and data["calibration"]["sha256"] is None
    write_cal(out, "{broken")
    data = GV.validate(out)
    assert data["decision"] == "not_validated" and data["reasons"] == ["gate/gate_calibration.json unreadable "
                                                                      "(JSONDecodeError)"]


def test_cli(tmp_path, capsys):
    out = tmp_path / "outputs" / "toy"
    write_cal(out, calibration(negative_missed=5))
    assert gate_main(["validate", "--project-out", str(out)]) == 0
    text = capsys.readouterr().out
    assert text.startswith("GATE VALIDATION toy polish_disabled: benign accepted 1.000 (>= 0.95, 20), negatives "
                           "rejected 0.750 (>= 0.90, 20); polish off")
    assert "reason: negative controls rejected 0.750 < 0.90" in text
    cfg = tmp_path / "loose.yaml"
    cfg.write_text("benign_accept_min: 0.5\nnegative_reject_min: 0.7\n", encoding="utf-8")
    assert gate_main(["validate", "--project-out", str(out), "--config", str(cfg)]) == 0
    assert json.loads((out / "gate" / "gate_validation.json").read_text(encoding="utf-8"))["decision"] == "ok"
    other = tmp_path / "elsewhere"                         # --out: the gate folder read and written
    other.mkdir()
    (other / "gate_calibration.json").write_text(json.dumps(calibration()), encoding="utf-8")
    assert gate_main(["validate", "--project-out", str(out), "--out", str(other)]) == 0
    assert json.loads((other / "gate_validation.json").read_text(encoding="utf-8"))["decision"] == "ok"
    assert gate_main(["validate", "--project-out", str(tmp_path / "missing")]) == 2


def _git_show(rev_path: str):
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "show", rev_path], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return json.loads(out.stdout.decode("utf-8"))


def test_m5_calibration_needs_a_new_calibration():
    """The M5 calibration of synthetic-01 (commit a2adcef) was made with the start thresholds: not valid for the
    current ones; judged with its own thresholds it is flagged (benign 0.875 < 0.95, negatives 0.909 >= 0.90)."""
    cal = _git_show("a2adcef:results/gate/synthetic-01/gate_calibration.json")
    if cal is None:
        pytest.skip("git history with the M5 calibration not available")
    assert GV.decide_validation(cal, LIMITS, load_thresholds())["decision"] == "not_validated"
    own = GV.decide_validation(cal, LIMITS, cal["thresholds"])
    assert own["decision"] == "flagged" and own["benign_accept"] == 0.875 and own["negative_reject"] == 0.9086


@pytest.mark.parametrize("project", ["synthetic-01", "synthetic-03"])
def test_committed_calibrations_validate_as_recorded(project):
    """The committed calibrations (results/gate: the last full run of the project) validate with the current
    thresholds to the decision their run recorded in gate_validation.json: M7 pod C2 synthetic-03 ok; M8 pod F1
    synthetic-01 flagged (benign 0.938 < 0.95: the polish runs, the report flags it). Without a record: ok."""
    path = ROOT / "results" / "gate" / project / "gate_calibration.json"
    if not path.is_file():
        pytest.skip("committed calibration not present")
    cal = json.loads(path.read_text(encoding="utf-8"))
    got = GV.decide_validation(cal, LIMITS, load_thresholds())
    record = path.with_name("gate_validation.json")
    if not record.is_file():
        assert got["decision"] == "ok", got
        return
    want = json.loads(record.read_text(encoding="utf-8"))
    assert (got["decision"], got["benign_accept"], got["negative_reject"]) == \
        (want["decision"], want["benign_accept"], want["negative_reject"]), got
    assert got["decision"] in ("ok", "flagged"), got
