"""Per-project gate validation (docs/milestone6.md §0, §7.3).

What: ``python -m wenart.gate validate --project-out outputs/<p> [--out DIR] [--config validation.yaml]
[--thresholds thresholds.yaml]`` reads ``gate/gate_calibration.json`` (written by ``gate calibrate`` on
the same project right before, §2.3 phase 6) and writes ``gate/gate_validation.json``::

    {"schema_version": "0.1", "kind": "gate_validation", "project", "decision",
     "benign_accept", "negative_reject", "n_benign", "n_negative", "pass_benign", "pass_negative",
     "reasons": [...], "limits": {"benign_accept_min", "negative_reject_min"}, "polish_allowed",
     "calibration": {"path", "sha256", "incomplete", "thresholds_match"}, "created_utc"}

Decisions (limits from ``wenart/gate/validation.yaml``, value >= limit passes):

- ``ok``: both limits pass; the polish runs;
- ``flagged``: only the benign limit fails (the gate also rejects some harmless edits, so more views
  stay Cycles); the polish runs and the final report flags the project;
- ``polish_disabled``: the negative limit fails (the gate lets too many geometry changes through);
  no polish, every final image is the Cycles render;
- ``not_validated``: ``gate_calibration.json`` is missing, unreadable, cut by the deadline
  (``incomplete: true``), has no benign or no negative comparison, has no rates, or was made with other
  thresholds than the current ``thresholds.yaml``; treated like ``polish_disabled``.

Why: the M6 look changes the textures the gate sees, and new projects were never calibrated
(synthetic-01 was at 0.903 negatives with the current thresholds), so every project with polish on
is calibrated and validated before its polish (§0).

How: nothing is recomputed on the CPU. The rates are the calibration's own (each comparison decided
with the thresholds in use, which the calibration records); this module compares them with the
limits and checks that the recorded thresholds equal the current ``thresholds.yaml`` (every check;
the ``calibration:`` notes block is ignored). The GPU test
``tests/gpu/test_polish.py::test_gate_validation_recorded`` recomputes the rates from the stored
metrics with the current thresholds and checks this file against them.

Exit code 0 whenever ``gate_validation.json`` was written, whatever the decision (it is data: the
orchestrator reads ``decision``); 2 when ``--project-out`` is not a folder.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Optional

GATE_DIR = Path(__file__).resolve().parent
VALIDATION_PATH = GATE_DIR / "validation.yaml"
CALIBRATION_NAME = "gate_calibration.json"
VALIDATION_NAME = "gate_validation.json"
DECISIONS = ("ok", "flagged", "polish_disabled", "not_validated")
POLISH_DECISIONS = ("ok", "flagged")


def load_validation_config(path: Optional[str | Path] = None) -> dict:
    """``{"benign_accept_min", "negative_reject_min"}`` from ``validation.yaml``."""
    import yaml
    with open(VALIDATION_PATH if path is None else path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    for key in ("benign_accept_min", "negative_reject_min"):
        value = cfg.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise ValueError(f"validation.yaml: {key} must be a number in 0..1, got {value!r}")
    return {"benign_accept_min": float(cfg["benign_accept_min"]),
            "negative_reject_min": float(cfg["negative_reject_min"])}


def limit_thresholds(thresholds: Any) -> dict:
    """The thresholds that decide (every check, without the ``calibration:`` notes block)."""
    from wenart.gate.api import NOT_THRESHOLDS
    if not isinstance(thresholds, dict):
        return {}
    return {k: v for k, v in thresholds.items() if k not in NOT_THRESHOLDS}


def decide_validation(cal: Optional[dict], limits: dict, thresholds: Optional[dict] = None) -> dict:
    """The validation result of one calibration dict (pure; ``cal`` None = no calibration file).

    ``thresholds``: the thresholds the polish will use; None skips the comparison with the ones the
    calibration recorded.
    """
    out: dict[str, Any] = {"decision": "not_validated", "benign_accept": None, "negative_reject": None,
                           "n_benign": 0, "n_negative": 0, "pass_benign": False, "pass_negative": False,
                           "reasons": [], "thresholds_match": None}
    reasons = out["reasons"]
    if cal is None:
        reasons.append(f"gate/{CALIBRATION_NAME} missing: gate calibrate did not run or failed")
        return out
    if not isinstance(cal, dict):
        reasons.append(f"gate/{CALIBRATION_NAME} is not a calibration (not a JSON object)")
        return out
    benign, negative = cal.get("benign") or [], cal.get("negative") or []
    out["n_benign"], out["n_negative"] = len(benign), len(negative)
    rates = cal.get("rates") if isinstance(cal.get("rates"), dict) else {}
    b, n = rates.get("benign_accept"), rates.get("negative_reject")
    out["benign_accept"] = float(b) if isinstance(b, (int, float)) and not isinstance(b, bool) else None
    out["negative_reject"] = float(n) if isinstance(n, (int, float)) and not isinstance(n, bool) else None
    if out["benign_accept"] is not None:
        out["pass_benign"] = out["benign_accept"] >= limits["benign_accept_min"]
    if out["negative_reject"] is not None:
        out["pass_negative"] = out["negative_reject"] >= limits["negative_reject_min"]
    blocking = []
    if cal.get("incomplete"):
        blocking.append("calibration incomplete (cut by the deadline): not every control was compared")
    if not benign or out["benign_accept"] is None:
        blocking.append("no benign comparison recorded")
    if not negative or out["negative_reject"] is None:
        blocking.append("no negative comparison recorded")
    if thresholds is not None:
        out["thresholds_match"] = limit_thresholds(cal.get("thresholds")) == limit_thresholds(thresholds)
        if not out["thresholds_match"]:
            blocking.append("the calibration was made with other thresholds than the current thresholds.yaml: "
                            "run gate calibrate again")
    if blocking:
        reasons.extend(blocking)
        return out
    if not out["pass_benign"]:
        reasons.append(f"benign controls accepted {out['benign_accept']:.3f} < {limits['benign_accept_min']:.2f} "
                       f"({out['n_benign']} comparisons): the gate also rejects harmless edits")
    if not out["pass_negative"]:
        reasons.append(f"negative controls rejected {out['negative_reject']:.3f} < "
                       f"{limits['negative_reject_min']:.2f} ({out['n_negative']} comparisons): the gate lets "
                       f"geometry changes through")
    if out["pass_benign"] and out["pass_negative"]:
        out["decision"] = "ok"
    elif out["pass_negative"]:
        out["decision"] = "flagged"
    else:
        out["decision"] = "polish_disabled"
    return out


def validate(project_out, out_dir=None, config=None, thresholds=None) -> dict:
    """Write ``gate_validation.json`` for one project output folder and return it."""
    from wenart.canonical import canonical_sha256
    from wenart.gate.api import load_thresholds

    project_out = Path(project_out)
    gate_dir = Path(out_dir) if out_dir else project_out / "gate"
    cal_path = gate_dir / CALIBRATION_NAME
    limits = load_validation_config(config)
    current = thresholds if isinstance(thresholds, dict) else load_thresholds(thresholds)
    cal: Any = None
    unreadable = None
    if cal_path.is_file():
        try:
            cal = json.loads(cal_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            unreadable = f"gate/{CALIBRATION_NAME} unreadable ({type(exc).__name__})"
    result = decide_validation(cal, limits, current)
    if unreadable:
        result["reasons"] = [unreadable]
    project = (cal.get("project") if isinstance(cal, dict) else None) or project_out.resolve().name
    data = {
        "schema_version": "0.1",
        "kind": "gate_validation",
        "project": project,
        "decision": result["decision"],
        "benign_accept": result["benign_accept"],
        "negative_reject": result["negative_reject"],
        "n_benign": result["n_benign"],
        "n_negative": result["n_negative"],
        "pass_benign": result["pass_benign"],
        "pass_negative": result["pass_negative"],
        "reasons": result["reasons"],
        "limits": limits,
        "polish_allowed": result["decision"] in POLISH_DECISIONS,
        "calibration": {"path": CALIBRATION_NAME if cal_path.is_file() else None,
                        "sha256": canonical_sha256(cal_path),
                        "incomplete": bool(cal.get("incomplete")) if isinstance(cal, dict) else None,
                        "thresholds_match": result["thresholds_match"]},
        "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    gate_dir.mkdir(parents=True, exist_ok=True)
    path = gate_dir / VALIDATION_NAME
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return data


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-out", required=True, help="outputs/<p> (reads gate/gate_calibration.json)")
    parser.add_argument("--out", default=None, help="gate folder (default <project-out>/gate)")
    parser.add_argument("--config", default=None, help="validation.yaml (default: the package one)")
    parser.add_argument("--thresholds", default=None, help="thresholds.yaml the polish uses (default: the package one)")


def _fmt(value) -> str:
    return "-" if value is None else f"{value:.3f}"


def run_from_args(args) -> int:
    project_out = Path(args.project_out)
    if not project_out.is_dir():
        print(f"gate validate: {project_out} is not a folder")
        return 2
    data = validate(project_out, args.out, args.config, args.thresholds)
    lim = data["limits"]
    print(f"GATE VALIDATION {data['project']} {data['decision']}: benign accepted {_fmt(data['benign_accept'])} "
          f"(>= {lim['benign_accept_min']:.2f}, {data['n_benign']}), negatives rejected "
          f"{_fmt(data['negative_reject'])} (>= {lim['negative_reject_min']:.2f}, {data['n_negative']}); "
          f"polish {'allowed' if data['polish_allowed'] else 'off'}")
    for reason in data["reasons"]:
        print(f"  reason: {reason}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="validate a project's gate calibration (docs/milestone6.md §7.3)")
    add_arguments(parser)
    return run_from_args(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
