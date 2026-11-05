"""``python -m wenart.reading_check check --out <pipeline output> [--sheets]`` (the reading self-check, its comparison
sheets), ``python -m wenart.reading_check regress [--projects ...] [--update]`` (the reading regression set),
``python -m wenart.reading_check zip --out <reading> --results <run results> --project <p> --dest <zip>`` (a structure
run's zip: renders and comparison sheets together, ``pack``), ``python -m wenart.reading_check truth build
[--projects ...] [--work DIR] [--fresh] [--allow-drift]`` (the truth corpus from the accepted readings and the
synthetic projects' exact truth; ``truth add`` / ``truth remove`` put a user correction into it, ``truth``) and
``python -m wenart.reading_check score [--projects ...] [--work DIR] [--fresh] [--update] [--gate]`` (the reading
score against the truth, ``score``; Milestone 14 R1, 4 Nov 2026). ``--fresh`` reads a project again even when
``--work`` already holds its reading."""
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
    t = sub.add_parser("truth", help="the truth corpus: `truth build` reads the accepted projects (accepted_by_user "
                                     "in the baseline) and takes the synthetic projects' exact truth, writing "
                                     "results/reading_truth/<project>.json; `truth add` / `truth remove` put a user "
                                     "correction into it")
    t.add_argument("action", choices=["build", "add", "remove"])
    t.add_argument("--projects", default=None, help="build: comma separated (default: every accepted baseline and "
                                                    "every synthetic project with a truth)")
    t.add_argument("--work", default=None, help="work folder for the readings (a reading already there is used again)")
    t.add_argument("--fresh", action="store_true", help="read again even when --work holds a reading")
    t.add_argument("--allow-drift", action="store_true",
                   help="build: write a reading that drifted from the accepted baseline, marked status drifted")
    t.add_argument("--project", default=None, help="add/remove: the project")
    t.add_argument("--level", default=None, help="add/remove: the level id (L0, L-1 ...)")
    t.add_argument("--kind", default=None, choices=["room", "door", "window", "opening", "wall", "stair", "level"],
                   help="add/remove: the element kind")
    t.add_argument("--source", default=None, choices=["user_correction", "synthetic"],
                   help="add/remove: the element's source (default user_correction)")
    t.add_argument("--correction", default=None, help="add/remove: the correction record id (C0012)")
    t.add_argument("--date", default=None, help="add/remove: the date of the correction (default today)")
    t.add_argument("--id", default=None, help="add/remove: the element id (remove: the element to negate)")
    t.add_argument("--center", default=None, help="x,y in building metres (door, window, opening, stair, room)")
    t.add_argument("--width", default=None, help="door / window / opening width in metres")
    t.add_argument("--wall-id", dest="wall_id", default=None)
    t.add_argument("--label", default=None, help="room label (or the level's label with --kind level)")
    t.add_argument("--room-type", dest="room_type", default=None)
    t.add_argument("--area", default=None, help="room area in m2")
    t.add_argument("--polygon", default=None, help="room polygon 'x,y;x,y;...' in building metres")
    t.add_argument("--start", default=None, help="wall start x,y")
    t.add_argument("--end", default=None, help="wall end x,y")
    t.add_argument("--thickness", default=None, help="wall thickness in metres")
    t.add_argument("--size", default=None, help="stair footprint 'w,d' in metres")
    t.add_argument("--turn", default=None, help="stair turn: straight, U, other")
    t.add_argument("--elevation", default=None, help="level elevation (with --kind level)")
    t.add_argument("--order", default=None, help="level order (with --kind level)")
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
