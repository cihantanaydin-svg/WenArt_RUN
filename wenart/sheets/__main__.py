"""CLI of the sheets stage (docs/milestone10.md §1.6a).

``python -m wenart.sheets <project_dir> --out outputs/<p> [--answers <out>/sheets] [--no-ai] [--work DIR]``

Exit codes: 0 done (answers complete, or ``--no-ai``), 4 questions written and answers missing, 1 needs review (no
readable plan region or no unit agreement in a document; ``sheets.json`` is still written), 2 usage or crash.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

EXIT_OK, EXIT_REVIEW, EXIT_USAGE, EXIT_QUESTIONS = 0, 1, 2, 4


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.sheets",
                                     description="sheet analysis: drawing regions, units, levels, heights")
    parser.add_argument("project_dir")
    parser.add_argument("--out", default=None, help="output folder (default: outputs/<project name>)")
    parser.add_argument("--answers", default=None, help="folder with the sheet_region answers (<out>/sheets)")
    parser.add_argument("--no-ai", action="store_true", help="do not wait for AI answers")
    parser.add_argument("--work", default=None, help="work folder for DWG conversions (default <out>/converted)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    project = Path(args.project_dir)
    if not project.is_dir():
        print(f"sheets: {project} is not a folder", file=sys.stderr)
        return EXIT_USAGE
    out = Path(args.out) if args.out else Path("outputs") / project.name
    try:
        from wenart.sheets import run
        result = run(project, out, answers=Path(args.answers) if args.answers else None, no_ai=args.no_ai,
                     work_dir=Path(args.work) if args.work else None)
    except Exception:  # noqa: BLE001 - the stage reports a crash as exit 2 with the traceback
        traceback.print_exc()
        return EXIT_USAGE
    doc = result.doc
    plans = sum(1 for r in doc["regions"] if r["use"] == "read")
    print(f"{doc['project']}: {len(doc['regions'])} regions ({plans} plans), {len(doc['levels'])} levels, "
          f"{len(doc['variants'])} variants, {len(doc['stray'])} strays, {len(doc['conflicts'])} conflicts, "
          f"{result.questions} questions ({len(result.pending)} waiting) -> {out / 'sheets.json'}")
    if result.review:
        for reason in result.review:
            print(f"needs review: {reason}")
        return EXIT_REVIEW
    if result.pending:
        print(f"questions written to {out / 'sheets' / 'requests.json'}; answers missing (exit 4)")
        return EXIT_QUESTIONS
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
