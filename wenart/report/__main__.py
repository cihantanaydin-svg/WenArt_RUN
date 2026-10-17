"""CLI: ``python -m wenart.report final|sweep --project-out outputs/<p> [--out DIR] [--private]``.

- ``final``: everything of ``<project-out>/final/`` (docs/milestone5.md §7,
  docs/milestone6.md §7.4). Exit 0 for a report of rendered views (also when
  the polish, the gate validation or the vision check did not run, or a stage
  was cut by the deadline after the renders: the report says so) and for the
  needs-review report of a project that stopped with ``needs_review``
  (``final_manifest.json`` ``status: needs_review``). Exit 1 only when there
  is nothing to report: no render manifest and the project is not
  ``needs_review`` (``status: not_rendered``, ``status_note: "no renders in
  this run"``; the report and stdout name this run's ``incomplete`` or
  ``failed`` stages, e.g. a deadline cut before the build); the report and the
  manifest are still written (the manifest last), so the orchestrator tells
  this exit 1 from a crash (a Python traceback, exit 1 with no new
  ``final_manifest.json``) and records the report of a project that was
  already cut as a ``warning``. ``--private`` treats the project as private (no
  plan crop or debug image copied into ``final/``) even when nothing in the
  project output says so.
- ``sweep``: ``<project-out>/final/sweep_report.md`` (polish sweep, gate and
  vision-check calibration); exit 0 even when nothing ran yet.
Exit 2 for a missing ``--project-out`` folder.

Milestone 13 (docs/milestone13.md §7, §13.2; track T8):

- ``metrics13 --out <project_out> [--baseline <dir>] --json <path> [--md <path>]``: the 17 metrics of §7
  (``wenart.report.metrics13``) of a run, before | after when a baseline run is given; either folder may be the
  volume's project output or a committed ``results/<area>/<p>`` folder. Exit 0; exit 2 for a missing folder.
- ``sheets13 --out <project_out> --baseline <dir> --dir <out_dir>``: one before | after JPEG per camera
  (``wenart.report.sheets13``). Exit 0; exit 2 for a missing folder.

Fix round after P4a (17 Oct 2026; the report track's ask, applied at integration): the metrics13 line names why a
metric has no data (its text, e.g. "m11 (no drawn tree; no tree in the scene)"), so a run without trees does not read
like a missing input; the sheets13 line counts the baseline previews left out (``before_left_out``).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

M13_COMMANDS = ("metrics13", "sheets13")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.report",
                                     description="final report (milestones 5 and 6), sweep report, Milestone 13 "
                                                 "metrics and before/after sheets")
    parser.add_argument("command", choices=["final", "sweep", *M13_COMMANDS])
    parser.add_argument("--project-out", default=None, help="outputs/<p> (final, sweep)")
    parser.add_argument("--out", default=None,
                        help="final, sweep: output folder (default <project-out>/final); metrics13, sheets13: the "
                             "run (outputs/<p> or results/<area>/<p>)")
    parser.add_argument("--private", action="store_true",
                        help="private project: name plan crops and debug images, never copy them (§7.4)")
    parser.add_argument("--baseline", default=None, help="metrics13, sheets13: the baseline run's folder")
    parser.add_argument("--json", default=None, help="metrics13: where the JSON goes")
    parser.add_argument("--md", default=None, help="metrics13: where the markdown goes (optional)")
    parser.add_argument("--dir", default=None, help="sheets13: the folder of the sheets")
    args = parser.parse_args(argv)

    if args.command in M13_COMMANDS:
        return _m13(args, parser)
    if not args.project_out:
        parser.error(f"{args.command} needs --project-out")
    project_out = Path(args.project_out)
    if not project_out.is_dir():
        print(f"report {args.command}: {project_out} is not a folder", file=sys.stderr)
        return 2
    if args.command == "sweep":
        from wenart.report.sweep import write_sweep
        path = write_sweep(project_out, args.out)
        print(f"report sweep -> {path}")
        return 0
    from wenart.report.final import MANIFEST_NAME, REPORT_NAME, write_final
    manifest = write_final(project_out, args.out, private=args.private)
    out_dir = Path(args.out) if args.out else project_out / "final"
    if manifest.get("status") == "needs_review":
        print(f"report final {manifest['project']}: needs_review ({len(manifest['reasons'])} reason(s)) "
              f"-> {out_dir / REPORT_NAME}, {out_dir / MANIFEST_NAME}")
        for reason in manifest["reasons"]:
            print(f"  reason: {reason}")
        return 0
    if manifest.get("status") == "not_rendered":
        print(f"report final {manifest['project']}: not_rendered: {manifest.get('status_note')} "
              f"-> {out_dir / REPORT_NAME}, {out_dir / MANIFEST_NAME}")
        for r in manifest.get("stopped_stages") or []:
            print(f"  stopped: {r['stage']} {r['status']}" + (f" ({r['note']})" if r.get("note") else ""))
        for w in manifest["warnings"]:
            print(f"  warning: {w}")
        return 1
    s = manifest["summary"]
    reasons = ", ".join(f"{k} {n}" for k, n in s["cycles_by_reason"].items()) or "none"
    print(f"report final {manifest['project']}: {s['views']} views, {s['polished']} polished, {s['cycles']} Cycles "
          f"({reasons}), {s['needs_review']} needs_review -> {out_dir / REPORT_NAME}, {out_dir / MANIFEST_NAME}")
    for flag in manifest["advisory_flags"]:
        print(f"  open: {flag}")
    for w in manifest["warnings"]:
        print(f"  warning: {w}")
    return 0


def _no_data_reason(metric: dict, no_data: str) -> str:
    """Fix round after P4a: `` (<why>)`` for a metric without data: its text without the "no data" words, or ""."""
    text = str(metric.get("text") or "").strip()
    if text.startswith(no_data):
        text = text[len(no_data):].strip(" :;,-()")
    return f" ({text})" if text else ""


def _m13(args, parser) -> int:
    """``metrics13`` and ``sheets13`` (Milestone 13)."""
    run = args.out or args.project_out
    if not run:
        parser.error(f"{args.command} needs --out <project_out>")
    if not Path(run).is_dir():
        print(f"report {args.command}: {run} is not a folder", file=sys.stderr)
        return 2
    if args.baseline and not Path(args.baseline).is_dir():
        print(f"report {args.command}: baseline {args.baseline} is not a folder", file=sys.stderr)
        return 2
    if args.command == "metrics13":
        if not args.json:
            parser.error("metrics13 needs --json <path>")
        from wenart.report import metrics13 as MX
        result = MX.write(run, args.baseline, args.json, args.md)
        no_data = [k for k, m in result["metrics"].items() if m["value"] == MX.NO_DATA]
        named = [k + _no_data_reason(result["metrics"][k], MX.NO_DATA)
                 for k in sorted(no_data, key=lambda k: int(k[1:]))]
        print(f"report metrics13 {result['project']}: {len(result['metrics'])} metrics, {len(result['views'])} views"
              + (f", baseline {result['baseline_project']}" if result.get("baseline_out") else "")
              + (f", no data: {', '.join(named)}" if no_data else "")
              + f" -> {args.json}" + (f", {args.md}" if args.md else ""))
        for w in result["warnings"]:
            print(f"  warning: {w}")
        return 0
    if not args.baseline:
        parser.error("sheets13 needs --baseline <dir>")
    if not args.dir:
        parser.error("sheets13 needs --dir <out_dir>")
    from wenart.report import sheets13 as SH
    result = SH.sheets(run, args.baseline, args.dir)
    print(f"report sheets13 {result['project']}: {len(result['sheets'])} sheet(s) -> {args.dir}"
          + (f"; no baseline preview: {len(result['missing_before'])}" if result["missing_before"] else "")
          + (f"; no preview of the run: {len(result['missing_after'])}" if result["missing_after"] else "")
          + (f"; baseline only: {len(result['baseline_only'])}" if result["baseline_only"] else "")
          + (f"; baseline previews left out: {len(result['before_left_out'])}" if result.get("before_left_out")
             else ""))
    for w in result["warnings"]:
        print(f"  warning: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
