"""``python -m wenart.reading_check check --out <pipeline output> [--sheets]`` (the reading self-check, its comparison
sheets) and ``python -m wenart.reading_check regress [--projects ...] [--update]`` (the reading regression set)."""
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
    args = ap.parse_args(argv)
    import wenart.reading_check as RC
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
