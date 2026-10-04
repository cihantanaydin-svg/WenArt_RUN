"""Sweep report of Milestone 5 (docs/milestone5.md §3.6, §4.3, §5.5, §8.3): numbers for the thresholds and ladder.

What: ``python -m wenart.report sweep --project-out outputs/<p>`` summarises
into ``outputs/<p>/final/sweep_report.md``:

- the polish sweep (``polish/sweep/polish_manifest.json``, ``kind: sweep``):
  per setting (strength, control, scale, size, mode, role) the views, gate
  accept rate, failing checks, median global gate metrics, seconds and the
  realism preference (``check_manifest.json`` image kinds ``sweep:a<k>``);
  the decision of every view and setting; the settings accepted on every
  view (information for the ladder, which is set by hand, §8.3);
- the gate calibration (``gate/gate_calibration.json``): benign accept and
  negative reject rates, per control, per metric (worst benign, best small
  negative, proposal next to the current ``thresholds.yaml``), the smallest
  detected shift/scale, misses and the presumed-bad attempts;
- the vision-check calibration (``check/check_calibration.json``, when
  present): metrics against the ``check.yaml`` targets, missed targets,
  advisory, per model answer rate and decoy acceptance, plan A/B.

A missing input is reported as "not run"; nothing is computed from images
here (only from the manifests).
"""
from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any, Optional

from wenart.report import common as C

REPORT_NAME = "sweep_report.md"
CHECK_ORDER = ("edges", "added_lines", "depth", "masks", "colour", "neutral", "features")


def setting_key(a: dict) -> tuple:
    return (a.get("role") or "grid", a.get("strength"), a.get("control"), a.get("scale"), a.get("size") or "native",
            a.get("mode") or "plain")


def setting_label(key: tuple) -> str:
    role, strength, control, scale, size, mode = key
    bits = [f"s {strength}", str(control or "no control")]
    if scale is not None:
        bits.append(f"x{scale}")
    if size != "native":
        bits.append(str(size))
    if mode != "plain":
        bits.append(str(mode))
    if role != "grid":
        bits.append(f"[{role}]")
    return " ".join(bits)


def _failing_checks(gate: Optional[dict]) -> list[str]:
    return sorted({str(r.get("check")) for r in (gate or {}).get("reasons") or [] if isinstance(r, dict)})


def _median(values: list) -> Optional[float]:
    vals = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return statistics.median(vals) if vals else None


def sweep_settings(manifest: dict, check: Optional[dict] = None) -> list[dict]:
    """Per setting: views, accepted, rate, failing checks, medians, seconds, preference; in first-seen order."""
    check_views = (check or {}).get("views") or {}
    rows: dict[tuple, dict] = {}
    for view in manifest.get("views") or []:
        cam = view.get("camera")
        for a in view.get("attempts") or []:
            key = setting_key(a)
            row = rows.setdefault(key, {"key": key, "label": setting_label(key), "ks": [], "views": 0, "gated": 0,
                                        "accepted": 0, "errors": 0, "failing": {}, "metrics": {}, "seconds": [],
                                        "preferred": 0, "preference_asked": 0, "decisions": {}})
            if a.get("k") not in row["ks"]:
                row["ks"].append(a.get("k"))
            row["views"] += 1
            if a.get("seconds") is not None:
                row["seconds"].append(a["seconds"])
            gate = a.get("gate")
            if a.get("error") or not isinstance(gate, dict):
                row["errors"] += bool(a.get("error"))
                row["decisions"][cam] = "err" if a.get("error") else "-"
                continue
            row["gated"] += 1
            accepted = gate.get("decision") == "accept"
            row["accepted"] += accepted
            fails = _failing_checks(gate)
            for f in fails:
                row["failing"][f] = row["failing"].get(f, 0) + 1
            row["decisions"][cam] = "A" if accepted else "R" + (f" ({', '.join(fails)})" if fails else "")
            for check_name, m in (gate.get("metrics") or {}).items():
                if isinstance(m, dict) and "global" in m:
                    row["metrics"].setdefault(check_name, []).append(m.get("global"))
            pref = ((check_views.get(cam) or {}).get(f"sweep:a{a.get('k')}") or {}).get("preference")
            if isinstance(pref, dict):
                row["preference_asked"] += 1
                row["preferred"] += bool(pref.get("preferred"))
    out = []
    for row in rows.values():
        row["rate"] = row["accepted"] / row["gated"] if row["gated"] else None
        row["medians"] = {k: _median(v) for k, v in row["metrics"].items()}
        row["mean_seconds"] = sum(row["seconds"]) / len(row["seconds"]) if row["seconds"] else None
        out.append(row)
    return out


def candidate_ladder(rows: list[dict]) -> list[dict]:
    """Grid settings accepted on every gated view, strongest first (information only)."""
    ok = [r for r in rows if r["key"][0] == "grid" and r["gated"] and r["accepted"] == r["gated"]]
    # Strongest first; at the same strength the plain native settings (the simplest) first.
    return sorted(ok, key=lambda r: (-(r["key"][1] or 0), r["key"][4] != "native", r["key"][5] != "plain",
                                     str(r["key"][2]), str(r["key"][4]), str(r["key"][5])))


def _kv(value: Any, digits: int = 3) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{k} {_kv(v, digits)}" for k, v in value.items()) or "-"
    return C.cell(value, digits)


def _group_controls(items: list) -> list[list]:
    """Rows ``[control, n, accepted, rejected]`` of a benign/negative list."""
    groups: dict[str, list[int]] = {}
    for it in items or []:
        if not isinstance(it, dict):
            continue
        g = groups.setdefault(str(it.get("control")), [0, 0, 0])
        g[0] += 1
        g[1 if it.get("decision") == "accept" else 2] += 1
    return [[k, *v] for k, v in groups.items()]


def _polish_ladder() -> list:
    """The ladder of the package's ``polish.yaml`` (when the sweep manifest does not record its config)."""
    try:
        from wenart.polish.config import load_config
        return list(load_config().get("ladder") or [])
    except Exception:  # noqa: BLE001 - the report then shows no current ladder
        return []


def _current_thresholds(manifest: Optional[dict]) -> dict:
    th = (manifest or {}).get("thresholds")
    if isinstance(th, dict) and th:
        return th
    try:
        from wenart.gate.api import load_thresholds
        return load_thresholds()
    except Exception:  # noqa: BLE001 - the report then shows no current thresholds
        return {}


def report_markdown(project: str, sweep: Optional[dict], gate_cal: Optional[dict], check_cal: Optional[dict],
                    check: Optional[dict] = None, warnings: Optional[list] = None) -> str:
    """``sweep_report.md`` from the sweep manifest, the gate calibration and the check calibration."""
    warnings = list(warnings or [])
    lines = [f"# Sweep report: {project}", ""]
    rows = sweep_settings(sweep, check) if sweep else []
    n_views = len((sweep or {}).get("views") or [])
    n_att = sum(r["views"] for r in rows)
    done = "not run" if sweep is None else f"{n_views} views, {len(rows)} settings, {n_att} attempts"
    lines.append(f"Polish sweep: {done}"
                 f"{' (incomplete: deadline)' if (sweep or {}).get('incomplete') else ''}. "
                 f"Gate calibration: {'not run' if gate_cal is None else 'run'}. "
                 f"Vision-check calibration: {'not run' if check_cal is None else 'run'}. "
                 "Thresholds and the ladder are set by hand from these numbers and committed with them (§8.3); "
                 "a threshold looser than §4.2 needs the user's OK.")

    lines += ["", "## Polish sweep", ""]
    if sweep is None:
        lines.append("Not run (polish/sweep/polish_manifest.json not found).")
    else:
        checks = [c for c in CHECK_ORDER if any(c in r["medians"] for r in rows)]
        checks += sorted({c for r in rows for c in r["medians"]} - set(checks))
        table_rows = []
        for i, r in enumerate(rows, 1):
            pref = f"{r['preferred']}/{r['preference_asked']}" if r["preference_asked"] else "-"
            fails = ", ".join(f"{k} {n}" for k, n in sorted(r["failing"].items(), key=lambda kv: (-kv[1], kv[0])))
            table_rows.append([f"S{i}", r["label"], r["ks"], r["views"], r["gated"], r["accepted"], C.pct(r["rate"]),
                               fails or "-", C.seconds_text(r["mean_seconds"]), pref, r["errors"]])
        lines += C.table(["id", "setting", "k", "views", "gated", "accepted", "rate", "failing checks",
                          "mean time", "preferred", "errors"], table_rows)
        if checks:
            lines += ["", "Median global gate metrics per setting:", ""]
            lines += C.table(["id"] + checks, [[f"S{i}"] + [C.cell(r["medians"].get(c), 3) for c in checks]
                                                for i, r in enumerate(rows, 1)])
        cams = [v.get("camera") for v in sweep.get("views") or []]
        lines += ["", "### Decisions per view", "", "A accepted, R rejected (failing checks), err failed, - not gated.",
                  ""]
        lines += C.table(["view"] + [f"S{i}" for i in range(1, len(rows) + 1)],
                         [[cam] + [r["decisions"].get(cam, "-") for r in rows] for cam in cams])
        ladder = candidate_ladder(rows)
        lines += ["", "### Settings accepted on every view (information for the ladder)", ""]
        lines += C.bullets([f"S{rows.index(r) + 1}: {r['label']}" for r in ladder],
                           empty="None: no grid setting passed the gate on every view.")
        current = ((sweep.get("config") or {}).get("ladder")) or _polish_ladder()
        if current:
            lines += ["", "Current ladder (polish.yaml): " + "; ".join(
                setting_label(setting_key({**a, "role": "grid"})) for a in current) + "."]
        warnings += [f"sweep: {w}" for w in sweep.get("warnings") or []]

    lines += ["", "## Gate calibration", ""]
    if gate_cal is None:
        lines.append("Not run (gate/gate_calibration.json not found).")
    else:
        rates = gate_cal.get("rates") or {}
        lines += C.table(["rate", "value"], [["benign accepted", C.pct(rates.get("benign_accept"))],
                                             ["negatives rejected", C.pct(rates.get("negative_reject"))]])
        by_control = rates.get("by_control") or {}
        if by_control:
            lines += ["", "By control:", ""]
            lines += C.table(["control", "value"], [[k, _kv(v)] for k, v in by_control.items()])
        for name, title in (("benign", "Benign controls (must be accepted)"),
                            ("negative", "Negative controls (must be rejected)"),
                            ("presumed_bad", "Presumed-bad polish attempts (reported only)")):
            items = gate_cal.get(name)
            if items is None:
                continue
            lines += ["", f"{title}:", ""]
            grouped = _group_controls(items)
            lines += C.table(["control", "n", "accepted", "rejected"], grouped) if grouped else ["None."]
        misses = [it for it in gate_cal.get("benign") or [] if isinstance(it, dict) and it.get("decision") != "accept"]
        misses += [it for it in gate_cal.get("negative") or []
                   if isinstance(it, dict) and it.get("decision") == "accept"]
        lines += ["", "Misses (benign rejected, negative accepted):", ""]
        lines += C.bullets([f"{it.get('camera')}: {it.get('control')} {C.cell(it.get('magnitude'))} -> "
                            f"{it.get('decision')}" + (f" ({', '.join(_failing_checks(it))})" if _failing_checks(it)
                                                       else "") for it in misses])
        per_metric = gate_cal.get("per_metric") or {}
        if per_metric:
            current = _current_thresholds(sweep)
            lines += ["", "Per metric (proposal = worst benign + 25 % of the gap to the best small negative):", ""]
            lines += C.table(["check", "worst benign", "best small negative", "best negative", "separates",
                              "proposed", "current"],
                             [[k, _kv(m.get("worst_benign")), _kv(m.get("best_small_negative")),
                               _kv(m.get("best_negative")), C.cell(m.get("separates")), _kv(m.get("proposed")),
                               _kv({kk: vv for kk, vv in (current.get(k) or {}).items() if kk != "hard"})]
                              for k, m in per_metric.items() if isinstance(m, dict)])
        sd = gate_cal.get("smallest_detected")
        if sd:
            lines += ["", f"Smallest detected change: {_kv(sd)}."]
        lines += ["", "Explanations:", ""]
        lines += C.bullets([str(e) for e in gate_cal.get("explanations") or []])

    lines += ["", "## Vision-check calibration", ""]
    if check_cal is None:
        lines.append("Not run (check/check_calibration.json not found).")
    else:
        metrics = check_cal.get("metrics") or {}
        targets = check_cal.get("targets") or {}
        missed = {m.get("target") + ":" + str(m.get("metric")) for m in check_cal.get("missed") or []
                  if isinstance(m, dict) and m.get("target")}
        rows_t = []
        for tkey, limit in targets.items():
            metric = tkey[:-4] if tkey.endswith(("_max", "_min")) else tkey
            op = "<=" if tkey.endswith("_max") else ">=" if tkey.endswith("_min") else "?"
            value = metrics.get(metric)
            if metric == "decoy_accept":
                value = {k: (m or {}).get("decoy_accept") for k, m in (metrics.get("models") or {}).items()}
            ok = not any(x.startswith(tkey + ":") for x in missed)
            rows_t.append([metric, _kv(value), f"{op} {limit}", "met" if ok else "MISSED"])
        lines += C.table(["metric", "value", "target", "result"], rows_t)
        lines += ["", f"Advisory: {'yes' if check_cal.get('advisory') else 'no'}"
                  + (f" ({'; '.join(check_cal.get('advisory_reasons') or [])})"
                     if check_cal.get("advisory_reasons") else "") + "."]
        models = metrics.get("models") or {}
        if models:
            lines += ["", "Per model (Cycles views):", ""]
            lines += C.table(["model", "answer rate", "decoy accepted", "false missing (single pass)"],
                             [[k, C.pct(m.get("answer_rate")), C.pct(m.get("decoy_accept")),
                               C.pct(m.get("fa_missing_single"))] for k, m in models.items() if isinstance(m, dict)])
        pab = check_cal.get("plan_ab")
        if isinstance(pab, dict):
            # Calibrations written before plan_image existed said "adopted" for an A/B that only favoured the crop.
            favours = pab.get("favours_plan", pab.get("adopted"))
            if pab.get("used"):
                state = "used (check.yaml plan_image: true)"
            elif favours:
                state = "favours the plan crop, not adopted (check.yaml plan_image: false)"
            else:
                state = "not adopted"
            lines += ["", f"Plan A/B: {state}" + (f": {pab['text']}" if pab.get("text") else "") + "."]
            keys = [k for k in ("fa_missing_without", "fa_missing_with", "fa_extra_without", "fa_extra_with",
                                "removal_confirmed_without", "removal_confirmed_with") if k in pab]
            if keys:
                lines += C.table(["metric", "value"], [[k, C.cell(pab.get(k), 3)] for k in keys])
    lines += ["", "## Warnings", ""]
    lines += C.bullets(warnings)
    return "\n".join(lines) + "\n"


def write_sweep(project_out, out_dir=None) -> Path:
    """Read the sweep inputs of a project output folder and write ``final/sweep_report.md``."""
    out = Path(project_out).resolve()
    out_dir = Path(out_dir).resolve() if out_dir else out / "final"
    warnings: list[str] = []
    sweep = C.read_json(out / "polish" / "sweep" / "polish_manifest.json", warnings)
    if sweep is not None and sweep.get("kind") not in (None, "sweep"):
        warnings.append(f"polish/sweep/polish_manifest.json has kind {sweep.get('kind')!r}, not sweep")
    gate_cal = C.read_json(out / "gate" / "gate_calibration.json", warnings)
    check_cal = C.read_json(out / "check" / "check_calibration.json", warnings)
    check = C.read_json(out / "check" / "check_manifest.json", warnings)
    project = str((sweep or check or {}).get("project") or out.name)
    text = report_markdown(project, sweep, gate_cal, check_cal, check, warnings)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / REPORT_NAME
    path.write_text(text, encoding="utf-8")
    return path
