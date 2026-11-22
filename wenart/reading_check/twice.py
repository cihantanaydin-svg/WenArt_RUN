"""Read twice: the reading's own uncertainty from a harmless change of the drawing (22 Nov 2026, Milestone 14
self-improvement round; user-approved queue item: "the structure reader and the AI checks improve themselves with as
little of the user's time as possible, and every gain is measured").

What: ``python -m wenart.reading_check twice run --projects real09,real10 --work DIR [--variants layers,mirror]
[--write]`` reads each project again after a change that must not change the building (the R8 stability variants:
``layers`` renames every layer, ``mirror`` mirrors the drawing; ``rotate90`` and ``mm`` are available) and marks every
element of the original reading that the second reading does not reproduce, and every place where the second reading
adds one, as low reading confidence with the reason (``reading_check/read_twice.json`` in the reading folder; with
``--write`` the elements of ``building.json`` also get ``reading_confidence: low`` and a ``reading_review`` reason).
``twice value --work DIR`` measures what the signal is worth: how many of the user's past corrections (the sparse
truth's entries, ``results/reading_truth/``) fall on such a low-confidence place, against chance (per project the
share of the reading's own elements of the kinds the truth judges within the same reach of a low place, times its
entries), and apart for the entries today's reading still gets wrong. 22 Nov 2026, measured on the five projects with
corrections: lift 0.99 (107 of 162 entries against 108.0 by chance), 0.13 on the 12 still wrong: no value yet, so the
question picker's bonus applies only to readings someone read twice (``results/read_twice/value_20261122.json``).

The question picker (``bandit.question_list``) reads ``read_twice.json`` of the readings in its work folder
(``bandit.all_labels`` -> ``labels["unstable"]``): a question within ``REACH_M`` of a low place on its level gets
``INSTABILITY_BONUS`` more uncertainty, and says why.

Why: a rule keyed on one drafter's habits (a layer name, the drawing's orientation) is fragile exactly where the
reading is likely wrong; reading twice finds those places with no user time and no GPU.

How: ``stability.stability_project`` (the matcher of ``score.py``, the variants mapped back into the original frame);
pure functions for the low places, the marking and the value; nothing is written under ``projects/`` or ``results/``
(the value table is printed and, with ``--json``, written where asked).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Optional

from wenart.reading_check import stability as ST
from wenart.reading_check import truth as TR

DEFAULT_VARIANTS = ("layers", "mirror")
OUT_FILE = "reading_check/read_twice.json"
REACH_M = 1.0                 # a correction (or a question) this near a low place falls on it
ROOM_REACH_M = 1.5            # a room's place (its centroid) this near a low room's place
INSTABILITY_BONUS = 0.25      # the extra uncertainty of a question at a low place (bandit.question_list)
KIND_OF = {"rooms": "room", "doors": "door", "windows": "window", "openings": "opening", "walls": "wall",
           "stairs": "stair", "levels": "level"}
ELEMENT_LISTS = {"rooms": "rooms", "doors": "openings", "windows": "openings", "openings": "openings",
                 "walls": "walls", "stairs": "stairs"}


# --- the low places (pure) ------------------------------------------------------------------------------------------

def low_places(result: dict) -> list:
    """The low-confidence places of a stability result (``stability.stability_project``): one per fragile finding,
    ``{level, kind, change, id, at, variants, reason}``; ``id`` is the original reading's element for a ``lost``
    finding (the second reading does not reproduce it), None for ``added`` (the second reading has an element there
    that the first has not)."""
    out = []
    for lid, items in sorted((result.get("fragile") or {}).items()):
        for f in items:
            place = f.get("place") or {}
            vs = sorted(set(f.get("variants") or []))
            what = KIND_OF.get(f.get("kind"), f.get("kind"))
            if f["change"] == "lost":
                reason = f"read twice: the {what} is not read again when the drawing is read with " + ", ".join(vs)
            elif f["change"] == "added":
                reason = f"read twice: a {what} is read here only when the drawing is read with " + ", ".join(vs)
            else:
                reason = f"read twice: the level {f['change'].replace('level_', '')} with " + ", ".join(vs)
            out.append({"level": lid, "kind": f.get("kind"), "change": f["change"],
                        "id": place.get("id") if f["change"] == "lost" else None, "at": place.get("at"),
                        "label": place.get("label"), "variants": vs, "reason": reason})
    return out


def mark(building: dict, low: list) -> int:
    """Set ``reading_confidence: low`` and a ``reading_review`` reason on every element of ``building`` that a low
    place names by id (in place); returns how many elements were marked."""
    by_id: dict = {}
    for p in low:
        if p.get("id"):
            by_id.setdefault(p["id"], []).append(p["reason"])
    n = 0
    for key in ("rooms", "openings", "walls", "stairs"):
        for el in building.get(key) or []:
            reasons = by_id.get(el.get("id"))
            if not reasons:
                continue
            el["reading_confidence"] = "low"
            rr = list(el.get("reading_review") or [])
            el["reading_review"] = rr + [r for r in reasons if r not in rr]
            n += 1
    return n


def _seg_dist(p, a, b) -> float:
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 <= 0 else max(0.0, min(1.0, ((float(p[0]) - ax) * dx + (float(p[1]) - ay) * dy) / L2))
    return math.hypot(float(p[0]) - (ax + t * dx), float(p[1]) - (ay + t * dy))


def place_point(kind: str, e: dict) -> Optional[list]:
    """One point of a truth or reading element (a room's centroid or polygon centre, a wall's mid-point)."""
    if kind == "walls" and e.get("start") and e.get("end"):
        return [(float(e["start"][0]) + float(e["end"][0])) / 2, (float(e["start"][1]) + float(e["end"][1])) / 2]
    if e.get("center"):
        return [float(e["center"][0]), float(e["center"][1])]
    if e.get("centroid"):
        return [float(e["centroid"][0]), float(e["centroid"][1])]
    poly = e.get("polygon") or []
    if poly:
        return [sum(float(p[0]) for p in poly) / len(poly), sum(float(p[1]) for p in poly) / len(poly)]
    return None


def near_low(kind: str, e: dict, low: list, *, same_kind: bool = True, skip_id: Optional[str] = None) -> Optional[dict]:
    """The nearest low place of a level within reach of the element ``e`` of ``kind`` (pure): a wall by the distance
    from the low place to its centre line, a room by its polygon holding the place or its centroid within
    ``ROOM_REACH_M``, anything else by its point within ``REACH_M``; ``same_kind`` keeps to low places of its kind."""
    pt = place_point(kind, e)
    best, best_d = None, None
    for p in low:
        if p.get("at") is None or (same_kind and p.get("kind") != kind) or (skip_id and p.get("id") == skip_id):
            continue
        if kind == "walls" and e.get("start") and e.get("end"):
            d = _seg_dist(p["at"], e["start"], e["end"])
            reach = REACH_M / 2
        elif kind == "rooms":
            d = math.dist(pt, p["at"]) if pt else 1e9
            reach = ROOM_REACH_M
            if e.get("polygon") and _inside(p["at"], e["polygon"]):
                d = 0.0
        else:
            d = math.dist(pt, p["at"]) if pt else 1e9
            reach = REACH_M
        if d <= reach and (best_d is None or d < best_d):
            best, best_d = p, d
    return best


def _inside(pt, poly) -> bool:
    x, y = float(pt[0]), float(pt[1])
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = float(poly[i][0]), float(poly[i][1])
        x2, y2 = float(poly[(i + 1) % n][0]), float(poly[(i + 1) % n][1])
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / ((y2 - y1) or 1e-12):
            inside = not inside
    return inside


def value(truths: dict, lows: dict, readings: dict, buildings: Optional[dict] = None,
          unsatisfied: Optional[dict] = None) -> dict:
    """What the signal is worth (pure but for ``truth.place_from_frame``): per project, the sparse truth's entries
    (the user's corrections, by record) that fall on a low place of their level (``near_low``, same kind and any
    kind), against chance: the share of the reading's own elements of the kinds the truth judges within reach of a low
    place (themselves included: a correction may fall on the very element that is low), so a project expects
    ``entries x chance`` hits and the lift is the hits over the sum of those expectations. ``unsatisfied``
    (``{project: {entry id}}``, the entries today's reading still gets wrong) are counted apart: they are where the
    reader is wrong now. ``truths``: ``{project: sparse truth}``; ``lows``: ``{project: [low place]}``; ``readings``:
    ``{project: truth.extract of the reading}``."""
    rows = {}
    tot = {"entries": 0, "on_low_same": 0, "on_low_any": 0, "expected": 0.0, "wrong": 0, "wrong_on_low": 0,
           "wrong_expected": 0.0, "records": set(), "records_on_low": set()}
    for p, truth in sorted(truths.items()):
        low = lows.get(p) or []
        read = readings.get(p) or {}
        building = (buildings or {}).get(p)
        wrong_ids = set((unsatisfied or {}).get(p) or ())
        r = {"entries": 0, "on_low_same": 0, "on_low_any": 0, "wrong": 0, "wrong_on_low": 0, "hits": []}
        for lid, lv in (truth.get("per_level") or {}).items():
            lv_low = [x for x in low if x.get("level") == lid]
            for kind in TR.ELEMENT_TYPES:
                for e in lv.get(kind) or []:
                    if building is not None:
                        e, _why = TR.place_from_frame(e, building, lid)
                    if place_point(kind, e) is None:
                        continue
                    r["entries"] += 1
                    same = near_low(kind, e, lv_low)
                    anyk = same or near_low(kind, e, lv_low, same_kind=False)
                    r["on_low_same"] += int(same is not None)
                    r["on_low_any"] += int(anyk is not None)
                    if e.get("id") in wrong_ids:
                        r["wrong"] += 1
                        r["wrong_on_low"] += int(anyk is not None)
                    recs = list(e.get("corrections") or [])
                    tot["records"].update(recs)
                    if anyk is not None:
                        tot["records_on_low"].update(recs)
                        r["hits"].append({"level": lid, "kind": kind, "records": recs, "absent": bool(e.get("absent")),
                                          "low": {k: anyk.get(k) for k in ("kind", "change", "id", "at", "variants")}})
        kinds = {k for lv in (truth.get("per_level") or {}).values() for k in TR.ELEMENT_TYPES if lv.get(k)}
        n = hit = 0
        for lid, rl in (read.get("per_level") or {}).items():
            lv_low = [x for x in low if x.get("level") == lid]
            for kind in kinds:
                for el in rl.get(kind) or []:
                    n += 1
                    hit += int(near_low(kind, el, lv_low, same_kind=False) is not None)
        chance = hit / n if n else 0.0
        r["chance"], r["chance_n"] = round(chance, 3), n
        rows[p] = r
        for k in ("entries", "on_low_same", "on_low_any", "wrong", "wrong_on_low"):
            tot[k] += r[k]
        tot["expected"] += r["entries"] * chance
        tot["wrong_expected"] += r["wrong"] * chance

    def lift(obs, exp):
        return round(obs / exp, 2) if exp else None
    return {"projects": rows, "entries": tot["entries"], "on_low_same": tot["on_low_same"],
            "on_low_any": tot["on_low_any"], "expected": round(tot["expected"], 1),
            "lift": lift(tot["on_low_any"], tot["expected"]), "wrong": tot["wrong"], "wrong_on_low": tot["wrong_on_low"],
            "wrong_expected": round(tot["wrong_expected"], 1), "wrong_lift": lift(tot["wrong_on_low"], tot["wrong_expected"]),
            "records": len(tot["records"]), "records_on_low": sorted(tot["records_on_low"], key=TR._record_key)}


# --- running --------------------------------------------------------------------------------------------------------

def run_project(project: str, work: Path, variants=DEFAULT_VARIANTS, fresh: bool = False, write: bool = False) -> dict:
    """Read ``project`` (or use ``work/<project>``) and again with each variant; write ``read_twice.json`` (and, with
    ``write``, the marked ``building.json``) in the reading folder."""
    res = ST.stability_project(project, Path(work), tuple(variants), fresh=fresh)
    folder = Path(work) / project
    low = low_places(res)
    doc = {"project": project, "variants": list(variants), "skipped": res.get("skipped"),
           "variant_errors": {v: e.get("error") or e.get("skipped") for v, e in (res.get("variants") or {}).items()
                              if e.get("error") or e.get("skipped")},
           "counts": {"original": (res.get("original") or {}).get("counts"),
                      "low": len(low), "low_lost": sum(1 for x in low if x["change"] == "lost"),
                      "low_added": sum(1 for x in low if x["change"] == "added")},
           "low": low}
    out = folder / OUT_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if write and (folder / "building.json").is_file():
        b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
        doc["marked"] = mark(b, low)
        (folder / "building.json").write_text(json.dumps(b, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return doc


def load_low(folder: Path) -> Optional[list]:
    """The low places of a reading folder (``read_twice.json``), None when it was not read twice."""
    path = Path(folder) / OUT_FILE
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("low") or []


def value_of_work(work: Path, projects: Optional[list] = None, variants: Optional[list] = None) -> dict:
    """``value`` of the readings in ``work`` that were read twice; ``variants`` keeps the low places one of those
    variants found (the signal of one change alone)."""
    truths, lows, readings, buildings, wrong = {}, {}, {}, {}, {}
    for p in projects or TR.truth_projects():
        truth = TR.load_truth(p)
        folder = Path(work) / p
        low = load_low(folder)
        if truth is None or not TR.is_sparse(truth) or low is None or not (folder / "building.json").is_file():
            continue
        b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
        if variants:
            low = [x for x in low if set(x.get("variants") or []) & set(variants)]
        truths[p], lows[p], buildings[p] = truth, low, b
        readings[p] = TR.extract(b, project=p)
        sc = folder / "reading_check" / "score.json"
        if sc.is_file():
            res = json.loads(sc.read_text(encoding="utf-8"))
            wrong[p] = {x["id"] for x in res.get("entries") or [] if not x.get("satisfied")}
    return value(truths, lows, readings, buildings, wrong)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check twice", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="read each project again with harmless changes and mark what differs")
    r.add_argument("--projects", required=True)
    r.add_argument("--work", default=None)
    r.add_argument("--variants", default=",".join(DEFAULT_VARIANTS))
    r.add_argument("--fresh", action="store_true")
    r.add_argument("--write", action="store_true", help="also mark the elements in the reading's building.json")
    v = sub.add_parser("value", help="how many of the user's corrections fall on low-confidence places")
    v.add_argument("--work", required=True)
    v.add_argument("--projects", default=None)
    v.add_argument("--json", default=None)
    v.add_argument("--variants", default=None, help="keep the low places these variants found (comma separated)")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_twice_"))
        variants = [x.strip() for x in args.variants.split(",") if x.strip()]
        for p in [x.strip() for x in args.projects.split(",") if x.strip()]:
            try:
                doc = run_project(p, work, variants, fresh=args.fresh, write=args.write)
                print(f"{p}: {doc['counts']['low']} low places ({doc['counts']['low_lost']} lost, "
                      f"{doc['counts']['low_added']} added)" + (f"; {doc['skipped']}" if doc.get("skipped") else "")
                      + (f"; variant problems {doc['variant_errors']}" if doc.get("variant_errors") else ""),
                      flush=True)
            except Exception as exc:                     # one project must not stop the others
                print(f"{p}: not read twice: {type(exc).__name__}: {exc}", flush=True)
        return 0
    projects = [x.strip() for x in (args.projects or "").split(",") if x.strip()] or None
    res = value_of_work(Path(args.work), projects,
                        [x.strip() for x in (args.variants or "").split(",") if x.strip()] or None)
    for p, r in res["projects"].items():
        print(f"{p}: {r['on_low_any']}/{r['entries']} correction entries on a low place ({r['on_low_same']} of their "
              f"own kind; still wrong today {r['wrong_on_low']}/{r['wrong']}); chance {r['chance']} of {r['chance_n']} "
              f"reading elements")
    print(f"all: {res['on_low_any']}/{res['entries']} on a low place (own kind {res['on_low_same']}) against "
          f"{res['expected']} by chance: lift {res['lift']}; still wrong today {res['wrong_on_low']}/{res['wrong']} "
          f"against {res['wrong_expected']}: lift {res['wrong_lift']}; records on a low place "
          f"{len(res['records_on_low'])} of {res['records']}: {', '.join(res['records_on_low'])}")
    if args.json:
        Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
