"""CLI: ``python -m wenart.report final|sweep --project-out outputs/<p> [--out DIR]``.

- ``final``: everything of ``<project-out>/final/`` (docs/milestone5.md §7);
  exit 1 when there is no render manifest (nothing to report), else 0, also
  when the polish or the vision check did not run (the report says so).
- ``sweep``: ``<project-out>/final/sweep_report.md`` (polish sweep, gate and
  vision-check calibration); exit 0 even when nothing ran yet.
Exit 2 for a missing ``--project-out`` folder.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.report",
                                     description="Milestone 5 final report and sweep report")
    parser.add_argument("command", choices=["final", "sweep"])
    parser.add_argument("--project-out", required=True, help="outputs/<p>")
    parser.add_argument("--out", default=None, help="output folder (default <project-out>/final)")
    args = parser.parse_args(argv)

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
    manifest = write_final(project_out, args.out)
    s = manifest["summary"]
    out_dir = Path(args.out) if args.out else project_out / "final"
    reasons = ", ".join(f"{k} {n}" for k, n in s["cycles_by_reason"].items()) or "none"
    print(f"report final {manifest['project']}: {s['views']} views, {s['polished']} polished, {s['cycles']} Cycles "
          f"({reasons}), {s['needs_review']} needs_review -> {out_dir / REPORT_NAME}, {out_dir / MANIFEST_NAME}")
    for flag in manifest["advisory_flags"]:
        print(f"  open: {flag}")
    for w in manifest["warnings"]:
        print(f"  warning: {w}")
    return 0 if manifest["stages"]["render"] == "run" else 1


if __name__ == "__main__":
    raise SystemExit(main())
