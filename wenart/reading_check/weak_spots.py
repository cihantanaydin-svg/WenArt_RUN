"""The weak-spot hunter (22 Nov 2026, Milestone 14 self-improvement round; user-approved queue item: "the structure
reader and the AI checks improve themselves with as little of the user's time as possible").

What: ``python -m wenart.reading_check weak rank --work DIR`` ranks the reader's error kinds by how often they occur
in four independent sources, each normalised to a share so that no source wins by its size:

- the dataset bench (``results/dataset_bench/*_fix.json``: 107 real-geometry floors, the error classes);
- the AI checks' known errors (``results/critic/known_errors.json``, the after readings);
- the readings in ``--work`` (``score --work`` leaves them): the user's correction entries not satisfied (the sparse
  truth), the synthetic projects' misses and inventions against their exact truth (``reading_check/score.json``), and
  the reader-error checks of their self-check (RC4, RC5, RC14 door_to_air, RC17; ``reading_check.json``; RC18 judges
  the building, not the reading, and stays out).

``weak hunt --work DIR [--kinds a,b,c]`` writes the synthetic projects made for the top kinds
(``wenart.synthetic.weak_projects``), reads them on the CPU and scores them against their exact truth; a project that
reads below 100 exposes a reader fault (listed per element type with the places missed and invented).

Why: the bench, the AI checks and the user point at different faults; a kind that all of them name is where a new
synthetic test pays most, and the test then guards the fix.

How: pure functions over the JSON files (``rank``); the hunt reuses ``failure_classes.generate_failure_project`` and
the score's matcher.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
BENCH = REPO / "results" / "dataset_bench" / "swiss_20261121_fix.json"
KNOWN = REPO / "results" / "critic" / "known_errors.json"

BENCH_KINDS = (("wall split", "wall_split"), ("wall invented", "wall_invented"), ("wall read with another", "wall_thickness"),
               ("wall missed", "wall_missed"), ("thin wall", "wall_missed"), ("parapet wall", "wall_missed"),
               ("angled wall", "angled_wall"), ("door missed", "door_missed"), ("door invented", "door_invented"),
               ("door read as", "opening_type"), ("window missed", "window_missed"),
               ("window invented", "window_invented"), ("window read as", "opening_type"),
               ("room split", "room_split"), ("rooms merged", "room_merged"), ("room invented", "room_invented"),
               ("room missed", "room_missed"), ("room label", "room_label"), ("stair", "stair_missed"),
               ("frame offset", "frame_offset"), ("level", "level_wrong"))
KNOWN_KINDS = {"door_into_air": "door_invented", "opening_type_differs": "opening_type",
               "room_not_in_drawing": "room_invented", "kitchen_no_window": "window_missed",
               "habitable_no_window": "window_missed", "angled_wall_straight": "angled_wall",
               "room_missing": "room_missed", "mirror_twin_missing": "room_missed", "balcony_missing": "room_missed",
               "stair_missing": "stair_missed", "storey_count_differs": "level_wrong"}
CHECK_KINDS = {("RC4", ""): "wall_missed", ("RC5", ""): "wall_invented", ("RC14", "door_to_air"): "door_invented",
               ("RC17", "angled_wall_straight"): "angled_wall", ("RC17", "door_without_opening"): "door_missed",
               ("RC17", "door_into_air"): "door_invented", ("RC17", "inferred_wall_off_facade"): "wall_invented",
               ("RC17", "opening_off_wall"): "opening_off_wall", ("RC17", "core_space_unbuilt"): "room_missed"}
TYPE_WORD = {"rooms": "room", "doors": "door", "windows": "window", "openings": "opening", "walls": "wall",
             "stairs": "stair", "levels": "level", "outdoor": "room"}


def bench_counts(path: Path = BENCH) -> dict:
    out: dict = {}
    if not Path(path).is_file():
        return out
    for e in json.loads(Path(path).read_text(encoding="utf-8")).get("error_classes") or []:
        name = e["class"].lower()
        kind = next((k for pre, k in BENCH_KINDS if name.startswith(pre)), None)
        if kind:
            out[kind] = out.get(kind, 0) + int(e["count"])
    return out


def known_counts(path: Path = KNOWN, prefix: str = "before/") -> dict:
    """The known errors of the readings before the fixes (each an error that occurred; one kind per error)."""
    out: dict = {}
    if not Path(path).is_file():
        return out
    for key, lst in (json.loads(Path(path).read_text(encoding="utf-8")).get("readings") or {}).items():
        if not key.startswith(prefix):
            continue
        for e in lst:
            kinds = {KNOWN_KINDS[k] for k in e.get("kinds") or [] if k in KNOWN_KINDS}
            for k in sorted(kinds)[:1]:
                out[k] = out.get(k, 0) + 1
    return out


def _other_type_near(building: Optional[dict], level: str, at, want: str, tol: float = 0.3) -> bool:
    if not building or not at:
        return False
    for o in building.get("openings") or []:
        c = o.get("center") or o.get("position")
        if o.get("level_id") == level and c and o.get("type") != want and math.dist(c[:2], at[:2]) <= tol:
            return True
    return False


def reading_counts(work: Path, skip: Optional[set] = None) -> tuple:
    """``(user, synthetic, checks)`` counts of the readings in ``work`` (the module docstring); ``skip`` (updated)
    holds the projects already counted from another folder."""
    user, syn, checks = {}, {}, {}
    seen_records: set = set()
    skip = skip if skip is not None else set()
    for folder in sorted(p for p in Path(work).iterdir() if (p / "building.json").is_file()):
        if folder.name in skip:
            continue
        skip.add(folder.name)
        sc_p = folder / "reading_check" / "score.json"
        building = None
        if sc_p.is_file():
            sc = json.loads(sc_p.read_text(encoding="utf-8"))
            if sc.get("sparse"):
                building = json.loads((folder / "building.json").read_text(encoding="utf-8"))
                for e in sc.get("entries") or []:
                    if e.get("satisfied"):
                        continue
                    t = TYPE_WORD.get(e["type"], e["type"])
                    if e.get("absent"):
                        k = f"{t}_invented"
                    elif t in ("door", "window") and _types_at(building, e, t):
                        k = "opening_type"
                    else:
                        k = f"{t}_missed"
                    rec = (tuple(e.get("records") or [e.get("id")]), k)    # a record over typical copies counts once
                    if rec in seen_records:
                        continue
                    seen_records.add(rec)
                    user[k] = user.get(k, 0) + 1
            else:
                for t, st in sc.items():
                    if not isinstance(st, dict) or "truth" not in st or t == "levels":
                        continue
                    w = TYPE_WORD.get(t, t)
                    miss = int(st["truth"]) - int(st["matched"])
                    inv = int(st["read"]) - int(st["matched"])
                    if miss > 0:
                        syn[f"{w}_missed"] = syn.get(f"{w}_missed", 0) + miss
                    if inv > 0:
                        syn[f"{w}_invented"] = syn.get(f"{w}_invented", 0) + inv
        rc_p = folder / "reading_check" / "reading_check.json"
        if rc_p.is_file():
            for f in json.loads(rc_p.read_text(encoding="utf-8")).get("findings") or []:
                key = (f["check"], f.get("rule") or f.get("kind") or "")
                k = CHECK_KINDS.get(key) or CHECK_KINDS.get((f["check"], ""))
                if k and f["check"] in ("RC4", "RC5", "RC14", "RC17") and (f["check"], "") in CHECK_KINDS \
                        and key[1] and key not in CHECK_KINDS:
                    k = None                                    # RC4/RC5 have no rule; other rules of RC14/17 do not count
                if k:
                    checks[k] = checks.get(k, 0) + 1
    return user, syn, checks


def _types_at(building: dict, entry: dict, want: str) -> bool:
    """Another kind of opening read at a door or window entry's metre place (pure): the type is wrong there."""
    sig = entry.get("at")
    at = next((x for x in sig if isinstance(x, list) and len(x) >= 2 and isinstance(x[0], (int, float))), None) \
        if isinstance(sig, list) else None
    if at is None or max(abs(float(at[0])), abs(float(at[1]))) > 500:       # a drawing-frame place: not judged here
        return False
    return _other_type_near(building, entry["level"], at, want, 0.6)


def rank(sources: dict) -> list:
    """``[{kind, score, count, sources: {source: (count, share)}}]`` by the sum of the shares (pure)."""
    kinds = sorted({k for counts in sources.values() for k in counts})
    totals = {s: sum(c.values()) for s, c in sources.items()}
    rows = []
    for k in kinds:
        per = {s: (c.get(k, 0), round(c.get(k, 0) / totals[s], 3) if totals[s] else 0.0)
               for s, c in sources.items() if c.get(k)}
        rows.append({"kind": k, "score": round(sum(v[1] for v in per.values()), 3),
                     "count": sum(v[0] for v in per.values()), "sources": per})
    rows.sort(key=lambda r: (-r["score"], -r["count"], r["kind"]))
    return rows


def all_sources(work: Optional[Path]) -> dict:
    src = {"bench": bench_counts(), "known_errors": known_counts()}
    if work is not None:
        user, syn, checks = {}, {}, {}
        seen: set = set()
        for w in str(work).split(","):                     # several work folders: a project counted once
            if not w.strip() or not Path(w.strip()).is_dir():
                continue
            u, sy, ch = reading_counts(Path(w.strip()), skip=seen)
            for acc, add in ((user, u), (syn, sy), (checks, ch)):
                for k, v in add.items():
                    acc[k] = acc.get(k, 0) + v
        src.update({"user_corrections": user, "synthetic": syn, "checks": checks})
    return {k: v for k, v in src.items() if v}


# --- the hunt -------------------------------------------------------------------------------------------------------

def hunt(work: Path, kinds: Optional[list] = None) -> list:
    """Generate, read and score the weak-spot projects of ``kinds`` (all when None); one result per project."""
    from wenart.ingest import pipeline as PL
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR
    from wenart.synthetic import failure_classes as FC
    from wenart.synthetic import weak_projects as WP

    out = []
    root = Path(work) / "projects"
    for kind, fn in WP.PROJECTS:
        if kinds and kind not in kinds:
            continue
        proj = fn()
        FC.generate_failure_project(proj, root)
        pdir = root / proj.name
        rdir = Path(work) / "readings" / proj.name
        rdir.mkdir(parents=True, exist_ok=True)
        PL.run_project(pdir, rdir, no_ai=True)
        truth = json.loads((pdir / FC.TRUTH_FILE).read_text(encoding="utf-8"))
        b = json.loads((rdir / "building.json").read_text(encoding="utf-8"))
        read = TR.extract(b, project=proj.name)
        res = SC.match(truth, read, b)
        faults = []
        for lid, tl in (truth.get("per_level") or {}).items():
            rl = (read.get("per_level") or {}).get(lid) or {}
            for t in TR.ELEMENT_TYPES:
                tt, rr = TR.positives(tl.get(t) or []), rl.get(t) or []
                m = SC.match_kind(t, tt, rr)
                mi, mj = {i for i, _ in m}, {j for _, j in m}
                faults += [f"{lid} {t} missed: {_where(t, e)}" for i, e in enumerate(tt) if i not in mi]
                faults += [f"{lid} {t} invented: {_where(t, e)}" for j, e in enumerate(rr) if j not in mj]
        out.append({"project": proj.name, "kind": kind, "total": res["total"], "faults": faults,
                    "per_type": {t: {k: res[t][k] for k in ("truth", "read", "matched")} for t in SC.TYPES if t in res}})
    return out


def _where(t: str, e: dict) -> str:
    if t == "walls":
        return f"{e.get('id')} {e['start']}-{e['end']} t={e.get('thickness')}"
    if t == "rooms":
        return f"{e.get('label')} at {e.get('centroid')}"
    return f"{e.get('id')} {e.get('width')} m at {e.get('center')}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check weak", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rank")
    r.add_argument("--work", default=None, help="readings with reading_check/score.json (score --work); several "
                                                "folders comma separated, a project counted once (the first)")
    r.add_argument("--json", default=None)
    h = sub.add_parser("hunt")
    h.add_argument("--work", default=None)
    h.add_argument("--kinds", default=None)
    h.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "rank":
        src = all_sources(args.work or None)
        rows = rank(src)
        if args.json:                                   # written first: a closed pipe never loses the record
            Path(args.json).write_text(json.dumps({"sources": src, "rank": rows}, indent=1) + "\n", encoding="utf-8")
        print("kind | score (sum of shares) | count | " + " | ".join(src))
        for x in rows:
            print(f"{x['kind']} | {x['score']:.3f} | {x['count']} | "
                  + " | ".join(f"{x['sources'].get(s, (0, 0))[0]} ({x['sources'].get(s, (0, 0.0))[1]:.2f})" for s in src))
        return 0
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="weak_spots_"))
    res = hunt(work, [k.strip() for k in (args.kinds or "").split(",") if k.strip()] or None)
    for x in res:
        print(f"{x['project']} ({x['kind']}): total {x['total']}; {len(x['faults'])} faults")
        for f in x["faults"][:30]:
            print("  " + f)
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
