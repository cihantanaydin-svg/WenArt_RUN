#!/usr/bin/env python3
"""Count and check the correction store (results/reading_corrections.jsonl), read-only.

What: prints the records per project, per element kind, per status and per source, how many are placed (a place and
a truth action), placed with no place (``place: null`` and a note) and not placeable (``placeable: false`` and a
why), and runs ``truth.correction_errors`` against the lessons file and ``projects/``. ``--upto C0058`` counts only
the records up to that id (the store before a backfill), ``--from C0059`` only those from it, ``--json`` prints the
same numbers as JSON. It also checks the lesson classification file (``results/reading_corrections_sources.json``)
against the store: every ``reading`` lesson there has at least one record, and every backfilled record of a
classified lesson points at a ``reading`` lesson.

Why (6 Nov 2026, Milestone 14 R1): the user asked about a recall figure of 24, "there were more than 24 corrections,
right?"; the store held only the 3 and 4 Nov reviews. The store grows by backfills and the user's remarks, and the
counts before and after each step must be one command, not a hand count.

How: ``python scripts/correction_store_counts.py [--upto Cnnnn] [--from Cnnnn] [--json]``. Pure reading of the
repository's files; writes nothing.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from wenart.reading_check import truth as TR  # noqa: E402

LESSONS = REPO / "wenart" / "blender" / "architect_lessons.json"
SOURCES = REPO / "results" / "reading_corrections_sources.json"


def _num(rid: str) -> int:
    return int(str(rid)[1:]) if str(rid)[1:].isdigit() else -1


def place_state(rec: dict) -> str:
    """placed | place_null | not_placeable (pure)."""
    if rec.get("placeable") is False:
        return "not_placeable"
    if rec.get("place") and rec.get("truth_action"):
        return "placed"
    return "place_null"


def counts(records: list[dict]) -> dict:
    """The store's numbers (pure)."""
    c = {k: collections.Counter() for k in ("project", "element_kind", "status", "source", "place")}
    for r in records:
        c["project"][r.get("project")] += 1
        c["element_kind"][r.get("element_kind")] += 1
        c["status"][r.get("status")] += 1
        c["source"][r.get("source")] += 1
        c["place"][place_state(r)] += 1
    out = {k: dict(sorted(v.items(), key=lambda kv: (-kv[1], str(kv[0])))) for k, v in c.items()}
    out["records"] = len(records)
    return out


def source_errors(records: list[dict], sources: dict) -> list[str]:
    """What disagrees between the lesson classification and the store (pure)."""
    out = []
    classes = {row["lesson"]: row["class"] for row in sources.get("lessons") or []}
    with_records = {r.get("lesson") for r in records}
    for lesson, cls in classes.items():
        if cls == "reading" and lesson not in with_records:
            out.append(f"{lesson}: classified reading but no record")
    for r in records:
        cls = classes.get(r.get("lesson"))
        if cls is not None and cls != "reading" and r.get("source") == "backfill_progress":
            out.append(f"{r['id']}: lesson {r['lesson']} is classified {cls}, not reading")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--upto", help="count only the records up to this id (e.g. C0058)")
    ap.add_argument("--from", dest="start", help="count only the records from this id (e.g. C0059)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    records = TR.load_corrections()
    lessons = {lesson["id"] for lesson in json.loads(LESSONS.read_text(encoding="utf-8"))["lessons"]}
    projects = {p.name for p in (REPO / "projects").iterdir() if p.is_dir()}
    errors = TR.correction_errors(records, lessons, projects)
    if SOURCES.is_file():
        errors += source_errors(records, json.loads(SOURCES.read_text(encoding="utf-8")))
    chosen = [r for r in records if (not args.upto or _num(r["id"]) <= _num(args.upto))
              and (not args.start or _num(r["id"]) >= _num(args.start))]
    numbers = counts(chosen)
    numbers["errors"] = errors
    if args.json:
        print(json.dumps(numbers, ensure_ascii=False, indent=1))
    else:
        print(f"records: {numbers['records']}")
        for key in ("project", "element_kind", "status", "source", "place"):
            print(f"{key}: " + ", ".join(f"{k} {v}" for k, v in numbers[key].items()))
        print("errors: " + ("none" if not errors else "; ".join(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
