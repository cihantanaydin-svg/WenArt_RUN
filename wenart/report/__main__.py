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
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.report",
                                     description="final report (milestones 5 and 6) and sweep report")
    parser.add_argument("command", choices=["final", "sweep"])
    parser.add_argument("--project-out", required=True, help="outputs/<p>")
    parser.add_argument("--out", default=None, help="output folder (default <project-out>/final)")
    parser.add_argument("--private", action="store_true",
                        help="private project: name plan crops and debug images, never copy them (§7.4)")
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


if __name__ == "__main__":
    raise SystemExit(main())
