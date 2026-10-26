"""``python -m wenart.audit``: Argus on a collected run or a project's output folder (``wenart.audit`` docstring)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wenart.audit import inputs as I
from wenart.audit import report as R


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.audit", description="Argus, the auditor")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="audit one project and write argus.json / argus.md")
    src = run.add_mutually_exclusive_group(required=True)
    src.add_argument("--results", type=Path, help="a collected run (runs/<job>/results)")
    src.add_argument("--pod", type=Path, help="a project's output folder (outputs/<p>)")
    run.add_argument("--project", help="the project (with --results)")
    run.add_argument("--job-results", type=Path, help="with --pod: the job's results folder (run manifest, tests)")
    run.add_argument("--out", type=Path, help="where to write the report (default: the orchestrator folder)")
    run.add_argument("--log", type=Path, nargs="?", const=R.LOG_FILE, default=None,
                     help=f"add the run to the problem log (default path {R.LOG_FILE})")
    args = ap.parse_args(argv)
    if args.results is not None:
        if not args.project:
            ap.error("--results needs --project")
        inp = I.collected(args.results, args.project)
    else:
        inp = I.pod(args.pod, args.job_results)
    rep = R.run(inp)
    log = R.update_log(rep, args.log) if args.log else None
    prev = R.prevention(rep, log)
    odir = args.out or R.out_dir(inp)
    R.write(rep, odir, prev)
    sev = rep["severity"]
    print(f"Argus {inp.project}: score {rep['score']}; {sev['critical']} critical, {sev['major']} major, "
          f"{sev['minor']} minor; kinds: " + ", ".join(f"{k} {v['critical'] + v['major']}" for k, v in
                                                       sorted(rep['by_kind'].items()))
          + f"; report {Path(odir) / R.REPORT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
