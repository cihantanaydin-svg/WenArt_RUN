"""``python -m wenart.reading_check check --out <pipeline output> [--sheets]`` (the reading self-check, its comparison
sheets), ``python -m wenart.reading_check regress [--projects ...] [--update]`` (the reading regression set),
``python -m wenart.reading_check zip --out <reading> --results <run results> --project <p> --dest <zip>`` (a structure
run's zip: renders and comparison sheets together, ``pack``), ``python -m wenart.reading_check truth build
[--projects ...] [--work DIR]`` (the truth corpus from the accepted readings, ``truth``) and ``python -m
wenart.reading_check score [--projects ...] [--work DIR] [--update] [--gate]`` (the reading score against the truth,
``score``; Milestone 14 R1, 4 Nov 2026)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a pipeline output against its drawing")
    c.add_argument("--out", required=True, help="the pipeline output folder (building.json, sheets.json, converted/)")
    c.add_argument("--sheets", action="store_true", help="also draw the comparison sheets (a few minutes)")
    r = sub.add_parser("regress", help="read the regression projects and compare their key numbers with the baseline")
    r.add_argument("--projects", default=None, help="comma separated (default: every baseline)")
    r.add_argument("--update", action="store_true", help="write the new numbers as the baseline")
    r.add_argument("--work", default=None, help="work folder for the readings (default: a temporary folder)")
    z = sub.add_parser("zip", help="a structure run's zip: the pod's renders with the comparison sheets")
    z.add_argument("--out", required=True, help="the local reading of the run's commit (building.json, converted/)")
    z.add_argument("--results", required=True, help="the run's collected results folder (runs/<job>/results)")
    z.add_argument("--project", required=True)
    z.add_argument("--dest", required=True, help="the zip to write")
    t = sub.add_parser("truth", help="the truth corpus: `truth build` reads the accepted projects and writes "
                                     "results/reading_truth/<project>.json")
    t.add_argument("action", choices=["build"])
    t.add_argument("--projects", default=None, help="comma separated (default: every baseline with status ok)")
    t.add_argument("--work", default=None, help="work folder for the readings (a reading already there is used again)")
    t.add_argument("--fresh", action="store_true", help="read again even when --work holds a reading")
    s = sub.add_parser("score", help="score the readings against the truth (results/reading_truth/)")
    s.add_argument("--projects", default=None, help="comma separated (default: every project with a truth file)")
    s.add_argument("--work", default=None, help="work folder for the readings (a reading already there is used again)")
    s.add_argument("--fresh", action="store_true", help="read again even when --work holds a reading")
    s.add_argument("--update", action="store_true", help="append the entry to results/reading_scores.json")
    s.add_argument("--gate", action="store_true", help="exit 1 when the score fell against the last stored entry")
    args = ap.parse_args(argv)
    import wenart.reading_check as RC
    if args.cmd == "truth":
        from wenart.reading_check import truth as TR
        return TR.main(args)
    if args.cmd == "score":
        from wenart.reading_check import score as SC
        return SC.main(args)
    if args.cmd == "zip":
        from wenart.reading_check import pack as PK
        print(PK.pack(args.out, args.results, args.project, args.dest))
        return 0
    if args.cmd == "check":
        res = RC.check(args.out)
        d = RC.write(args.out, res)
        if args.sheets:
            from wenart.reading_check import sheets as SH
            SH.draw(args.out, res)
        print(f"reading check {res.get('project')}: {res['verdict']} ({res['counts']}) -> {d}")
        return 0 if res["verdict"] == "ready" else 1
    from wenart.reading_check import regress as RG
    return RG.main(args)


if __name__ == "__main__":
    sys.exit(main())
