"""Self-tuning of the reader's structure thresholds (22 Nov 2026, Milestone 14 self-improvement round; user-approved
queue item: "the structure reader and the AI checks improve themselves with as little of the user's time as possible,
and every gain is measured").

What: ``python -m wenart.reading_check tune search [--params a,b] [--work DIR] [--jobs N] [--out FILE]`` searches a
small set of the reader's numeric thresholds that decide structure (``PARAMS``: gap widths, the door-arc zone, wall
join and corner reach, size-tag reach, the pairing of wall faces) against the truth the project already has: the
synthetic projects' exact truth (F1, ``score.match``) and the user's correction records (the sparse truth,
``score.match_sparse``, entry by entry). ``tune list`` prints the parameters with their current values and candidates;
``tune read`` is the worker (one project read with settings overridden, scored, written as JSON).

The split (``split``): the synthetic projects sorted by their baseline total, every ``HOLD_EVERY``-th held out (a
stratified split, so the held-out set has weak projects too); the real records by a stable hash of the record id
(``held_record``), every ``HOLD_EVERY``-th held out. The search never looks at a held-out number to choose: per
parameter (coordinate search, one pass) the candidate with the best tuning score is taken when it beats the baseline
tuning score by ``MIN_GAIN``; it is kept only when the held-out score (the mean of the held-out synthetic totals and the
held-out records' satisfied share) rises by ``MIN_GAIN`` and no held-out project or record falls (``held_falls``).
A kept setting is a code change: the module constant is edited by hand afterwards and must pass
``python -m wenart.reading_check score --gate`` and ``regress``; the search prints the command to check it.

Why: the reader's thresholds were set by hand on one project at a time; a search with a held-out split says whether a
value is better for the drawings it was not tuned on, with no user time.

How: each candidate reads every scored project in its own process (``tune read``: the module attributes are set
before the reading, so only thresholds read as module globals at call time are tunable; ``PARAMS`` lists only those),
``--jobs`` at a time; the debug images are deleted after scoring to keep the disk free. The result
(``results/tuning/<date>.json``) keeps every evaluation: the settings, the per-project totals, the per-record
satisfaction, the tuning and held-out scores and the decision.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as _dt
import hashlib
import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
PROJECTS_DIR = REPO / "projects"
OUT_DIR = REPO / "results" / "tuning"
HOLD_EVERY = 3                # every third synthetic project (by baseline total) and record (by hash) is held out
MIN_GAIN = 0.05               # a score must rise by this much (points on 0-100) to count as a rise
DELETE_AFTER = ("debug", "sheets_debug", "recognition", "sheets", "converted")   # heavy folders of a scored reading


@dataclass(frozen=True)
class Param:
    module: str
    name: str
    candidates: tuple
    what: str

    @property
    def key(self) -> str:
        return f"{self.module.rsplit('.', 1)[-1]}.{self.name}"

    def current(self):
        return getattr(importlib.import_module(self.module), self.name)


# Each threshold is read as a module global at call time (no default argument, no import by value; checked by
# ``tests/test_tune_20261122.py``), so setting the attribute before a reading changes it.
G = "wenart.ingest.generic."
PARAMS = (
    Param(G + "openings", "GAP_MIN_M", (0.20, 0.30), "the narrowest gap in a wall that is an opening"),
    Param(G + "openings", "ZONE_M", (0.25, 0.45), "how far from a gap a door arc or leaf is looked for"),
    Param(G + "openings", "RADIUS_TOL", (0.08, 0.16), "a swing radius within this share of the gap width"),
    Param(G + "openings", "DOOR_FRAME_M", (0.18, 0.32), "a leaf up to this much narrower than its gap (frames)"),
    Param(G + "core", "JOIN_MAX_M", (0.30, 0.50), "a free wall end this close to a wall on its line joins it"),
    Param(G + "core", "CORNER_MAX_M", (0.45, 0.75), "two free ends whose lines cross this close meet in a corner"),
    Param(G + "core", "TAG_REACH_M", (0.6, 1.0), "a window size tag stands this close to its wall"),
    Param(G + "core", "DOOR_TAG_REACH_M", (0.9, 1.5), "a door size tag stands this close to its gap"),
    Param(G + "walls", "PAIR_OVERLAP_M", (0.3, 0.5), "two parallel faces overlapping this much make a wall piece"),
    Param(G + "core", "JOINT_MAX_M", (0.10, 0.20), "a slit this narrow between two walls is filled"),
)


def params_by_key(keys: Optional[list] = None) -> list:
    if not keys:
        return list(PARAMS)
    found = {p.key: p for p in PARAMS}
    bad = [k for k in keys if k not in found]
    if bad:
        raise SystemExit(f"unknown parameters {bad}; known: {sorted(found)}")
    return [found[k] for k in keys]


def apply_settings(settings: dict) -> None:
    """Set ``{"module.NAME": value}`` (the ``Param.key`` form, or a full module path) on the imported modules."""
    full = {p.key: p for p in PARAMS}
    for key, value in (settings or {}).items():
        if key in full:
            mod, name = full[key].module, full[key].name
        else:
            mod, name = key.rsplit(".", 1)
        m = importlib.import_module(mod)
        if not hasattr(m, name):
            raise AttributeError(f"{mod} has no {name}")
        setattr(m, name, value)


# --- the split (pure) -----------------------------------------------------------------------------------------------

def held_record(record_id: str) -> bool:
    """True for a held-out record: a stable hash of its id (sha1), every ``HOLD_EVERY``-th."""
    return int(hashlib.sha1(str(record_id).encode("utf-8")).hexdigest(), 16) % HOLD_EVERY == 0


def split(baseline: dict) -> dict:
    """``{"tune": [synthetic], "held": [synthetic]}`` from a baseline evaluation (``{project: result}``): the synthetic
    projects sorted by (total, name), every ``HOLD_EVERY``-th (starting with the second) held out (pure)."""
    syn = sorted((p for p, r in baseline.items() if not r.get("sparse") and r.get("total") is not None),
                 key=lambda p: (float(baseline[p]["total"]), p))
    held = [p for i, p in enumerate(syn) if i % HOLD_EVERY == 1]
    return {"tune": [p for p in syn if p not in held], "held": held}


def entry_record(row: dict) -> Optional[str]:
    recs = row.get("records") or []
    return str(recs[0]) if recs else None


def record_share(results: dict, held: bool) -> tuple:
    """``(satisfied weight, total weight, {record: [ok, n]})`` over the sparse entries whose first record is (not)
    held out (pure)."""
    from wenart.reading_check import score as SC

    num = den = 0.0
    per: dict = {}
    for p, r in sorted(results.items()):
        if not r.get("sparse"):
            continue
        for row in (r.get("entries") or []) + (r.get("assertions") or []):
            rid = entry_record(row)
            if rid is None or held_record(rid) != held:
                continue
            w = SC.WEIGHTS.get(row.get("type") or "levels", SC.WEIGHTS["rooms"])
            den += w
            num += w * int(bool(row.get("satisfied")))
            got = per.setdefault(f"{p}:{rid}", [0, 0])
            got[0] += int(bool(row.get("satisfied")))
            got[1] += 1
    return num, den, per


def scores(results: dict, sp: dict) -> dict:
    """The tuning and the held-out score of one evaluation (pure): the mean of the split's synthetic totals and the
    records' satisfied share (on 0-100) as one more member; a failed reading counts 0."""
    def part(projects: list, held: bool) -> float:
        vals = [float((results.get(p) or {}).get("total") or 0.0) for p in projects]
        num, den, _ = record_share(results, held)
        if den:
            vals.append(100.0 * num / den)
        return round(sum(vals) / len(vals), 3) if vals else 0.0
    return {"tune": part(sp["tune"], False), "held": part(sp["held"], True)}


def held_falls(base: dict, cand: dict, sp: dict, tol: float = MIN_GAIN) -> list:
    """What falls on the held-out side from ``base`` to ``cand`` (pure): a held-out synthetic project's total lower by
    more than ``tol``, a held-out record that held and no longer holds (fewer satisfied entries), a failed reading."""
    out = []
    for p in sp["held"]:
        b, c = (base.get(p) or {}), (cand.get(p) or {})
        if c.get("error"):
            out.append(f"{p}: the reading failed ({c['error'][:80]})")
        elif float(c.get("total") or 0) < float(b.get("total") or 0) - tol:
            out.append(f"{p}: {b.get('total')} -> {c.get('total')}")
    _, _, bper = record_share(base, True)
    _, _, cper = record_share(cand, True)
    for rid, (ok, n) in sorted(bper.items()):
        now = cper.get(rid, [0, n])[0]
        if now < ok:
            out.append(f"record {rid}: {ok}/{n} -> {now}/{n} entries hold")
    for p, c in sorted(cand.items()):
        if c.get("error") and p not in sp["held"]:
            out.append(f"{p}: the reading failed ({c['error'][:80]})")
    return out


def decide(base: dict, cand: dict, sp: dict) -> dict:
    """The keep decision of a candidate whose tuning score won (pure): kept when the held-out score rises by
    ``MIN_GAIN`` and nothing held out falls."""
    b, c = scores(base, sp), scores(cand, sp)
    fell = held_falls(base, cand, sp)
    rise = c["held"] - b["held"]
    keep = rise >= MIN_GAIN and not fell
    why = ("kept: the held-out score rises and nothing held out falls" if keep else
           "refused: " + ("; ".join(fell[:4]) if fell else f"the held-out score moves {rise:+.3f} (needs +{MIN_GAIN})"))
    return {"base": b, "cand": c, "held_rise": round(rise, 3), "held_falls": fell, "keep": keep, "why": why}


# --- reading (the worker and the pool) ------------------------------------------------------------------------------

def score_reading(project: str, folder: Path) -> dict:
    """The score result of a reading folder against the project's truth (``score.match`` or ``match_sparse``)."""
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    truth = TR.load_truth(project)
    b = json.loads((Path(folder) / "building.json").read_text(encoding="utf-8"))
    res = SC.match(truth, SC.reading_for(truth, b, project), b)
    out = {"total": res.get("total"), "sparse": TR.is_sparse(truth)}
    if out["sparse"]:
        out["entries"] = [{k: e.get(k) for k in ("id", "type", "records", "satisfied")} for e in res["entries"]]
        out["assertions"] = [{k: a.get(k) for k in ("id", "records", "satisfied")} for a in res["assertions"]]
    else:
        out["per_type"] = {t: {k: res[t][k] for k in ("truth", "read", "matched")} for t in SC.TYPES if t in res}
    return out


def worker(project: str, out_dir: Path, settings: dict, keep: bool = False) -> dict:
    """Read ``project`` with ``settings`` applied, score it, delete the heavy folders (unless ``keep``)."""
    apply_settings(settings)
    from wenart.ingest import pipeline as PL

    out = Path(out_dir) / project
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    try:
        PL.run_project(PROJECTS_DIR / project, out, no_ai=True)
        res = score_reading(project, out)
    except Exception as exc:                                   # a failed reading is a result, never a crash
        res = {"total": 0.0, "error": f"{type(exc).__name__}: {exc}"}
    if not keep:
        for name in DELETE_AFTER:
            shutil.rmtree(out / name, ignore_errors=True)
    return res


def _run_one(project: str, out_dir: Path, settings: dict, timeout: int) -> tuple:
    cmd = [sys.executable, "-m", "wenart.reading_check.tune", "read", "--project", project, "--out", str(out_dir),
           "--settings", json.dumps(settings)]
    try:
        cp = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout)
        line = [x for x in cp.stdout.splitlines() if x.startswith("{")]
        if cp.returncode != 0 or not line:
            return project, {"total": 0.0, "error": (cp.stderr or cp.stdout).strip()[-300:] or f"exit {cp.returncode}"}
        return project, json.loads(line[-1])
    except subprocess.TimeoutExpired:
        return project, {"total": 0.0, "error": f"timeout after {timeout} s"}


def evaluate(projects: list, settings: dict, work: Path, jobs: int = 3, timeout: int = 1200) -> dict:
    """``{project: result}`` of every project read with ``settings`` (``jobs`` processes at a time)."""
    out_dir = Path(work) / hashlib.sha1(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:10]
    out_dir.mkdir(parents=True, exist_ok=True)
    res: dict = {}
    # the slow real projects first, so the pool ends together
    order = sorted(projects, key=lambda p: (not p.startswith("real"), p))
    with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        for p, r in ex.map(lambda p: _run_one(p, out_dir, settings, timeout), order):
            res[p] = r
    shutil.rmtree(out_dir, ignore_errors=True)
    return res


def scored_projects() -> list:
    from wenart.reading_check import truth as TR
    return TR.truth_projects()


def search(params: list, work: Path, jobs: int = 3, projects: Optional[list] = None, log=print,
           save: Optional[Path] = None, baseline: Optional[dict] = None) -> dict:
    """The coordinate search (the module docstring); returns the whole record (also written to ``save`` after every
    evaluation, so a stopped search keeps what it measured)."""
    def _save():
        if save is not None:
            Path(save).parent.mkdir(parents=True, exist_ok=True)
            Path(save).write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    projects = projects or scored_projects()
    record: dict = {"date": _dt.date.today().isoformat(), "commit": _head(), "projects": projects,
                    "hold_every": HOLD_EVERY, "min_gain": MIN_GAIN, "evaluations": [], "kept": {}}
    if baseline is not None and baseline.get("commit") == (record["commit"] or baseline.get("commit")) and \
            sorted((baseline.get("baseline") or {}).get("results") or {}) == sorted(projects):
        base = baseline["baseline"]["results"]                 # the same commit and projects: measured already
        log(f"tune: baseline of the record of {baseline.get('date')} (commit {baseline.get('commit')}) used again")
    else:
        log(f"tune: baseline on {len(projects)} projects ...")
        base = evaluate(projects, {}, work, jobs)
    sp = split(base)
    record["split"] = sp
    record["baseline"] = {"results": base, "scores": scores(base, sp)}
    log(f"tune: baseline tune {record['baseline']['scores']['tune']:.3f}, held {record['baseline']['scores']['held']:.3f}"
        f" (held out: {', '.join(sp['held'])} and every {HOLD_EVERY}rd record)")
    _save()
    settings: dict = {}
    for prm in params:
        best = None
        for v in prm.candidates:
            cand_settings = dict(settings, **{prm.key: v})
            res = evaluate(projects, cand_settings, work, jobs)
            sc = scores(res, sp)
            ev = {"param": prm.key, "value": v, "current": prm.current(), "settings": cand_settings, "scores": sc,
                  "results": res}
            record["evaluations"].append(ev)
            _save()
            log(f"tune: {prm.key} = {v} (now {prm.current()}): tune {sc['tune']:.3f}, held {sc['held']:.3f}")
            if best is None or sc["tune"] > best["scores"]["tune"]:
                best = ev
        if best is None or best["scores"]["tune"] < scores(base, sp)["tune"] + MIN_GAIN:
            log(f"tune: {prm.key}: no candidate beats the tuning score")
            continue
        d = decide(base, best["results"], sp)
        best["decision"] = d
        log(f"tune: {prm.key} = {best['value']}: {d['why']}")
        if d["keep"]:
            settings = best["settings"]
            base = best["results"]
            record["kept"][prm.key] = {"value": best["value"], "was": prm.current(), "decision": d}
    record["final"] = {"settings": settings, "scores": scores(base, sp)}
    _save()
    return record


def _head() -> Optional[str]:
    """The commit of the code (``WENART_TUNE_COMMIT`` for a copy of the code outside the repository)."""
    import os
    if os.environ.get("WENART_TUNE_COMMIT"):
        return os.environ["WENART_TUNE_COMMIT"]
    try:
        return subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], cwd=str(REPO), capture_output=True,
                              text=True).stdout.strip() or None
    except OSError:
        return None


def summary(record: dict) -> str:
    """A short table of a search record."""
    b = record["baseline"]["scores"]
    lines = [f"baseline: tune {b['tune']:.2f}, held {b['held']:.2f} (held out: {', '.join(record['split']['held'])})",
             "param | value | was | tune | held | decision", "--- | --- | --- | --- | --- | ---"]
    for ev in record["evaluations"]:
        d = ev.get("decision")
        lines.append(f"{ev['param']} | {ev['value']} | {ev['current']} | {ev['scores']['tune']:.2f} | "
                     f"{ev['scores']['held']:.2f} | {d['why'] if d else '-'}")
    if record["kept"]:
        lines.append("kept: " + ", ".join(f"{k} {v['was']} -> {v['value']}" for k, v in record["kept"].items())
                     + "; edit the constants and run `python -m wenart.reading_check score --gate` and `regress`")
    else:
        lines.append("kept: none (no setting raised the held-out score without a fall)")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check tune", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="the tunable thresholds, their values and candidates")
    s = sub.add_parser("search", help="the coordinate search with the held-out split")
    s.add_argument("--params", default=None, help="comma separated Param keys (default: all)")
    s.add_argument("--projects", default=None, help="comma separated (default: every project with a truth)")
    s.add_argument("--work", default=None)
    s.add_argument("--jobs", type=int, default=3)
    s.add_argument("--out", default=None, help="the record (default results/tuning/<date>.json)")
    s.add_argument("--baseline", default=None, help="a record of the same commit and projects: its baseline is used")
    r = sub.add_parser("read", help="worker: read one project with settings and print its score as JSON")
    r.add_argument("--project", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--settings", default="{}")
    r.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "list":
        for p in PARAMS:
            print(f"{p.key:28s} now {p.current()!s:6s} candidates {p.candidates}  ({p.what})")
        return 0
    if args.cmd == "read":
        res = worker(args.project, Path(args.out), json.loads(args.settings), keep=args.keep)
        print(json.dumps(res, ensure_ascii=False))
        return 0
    params = params_by_key([k.strip() for k in (args.params or "").split(",") if k.strip()])
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_tune_"))
    projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or None
    out = Path(args.out) if args.out else OUT_DIR / f"{_dt.date.today().isoformat()}.json"
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8")) if args.baseline else None
    rec = search(params, work, args.jobs, projects, log=lambda m: print(m, flush=True), save=out, baseline=base)
    print(summary(rec))
    print(f"tune: record -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
