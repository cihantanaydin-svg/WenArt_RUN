"""The reading score against the truth (4 Nov 2026, Milestone 14 track R1; user: "I want structure recognition to be
cumulatively better with the feedbacks I am giving"; review findings of 5 Nov 2026 built in).

What: ``python -m wenart.reading_check score [--projects a,b] [--work DIR] [--fresh] [--update] [--gate]`` reads every
project that has a truth file (``results/reading_truth/``, the CPU pipeline; a reading already in ``--work`` is used
again unless ``--fresh``), matches the reading against the truth and prints a table. Per element type the recall
(matched truth / truth), the precision (matched read / read) and the F1; per project a weighted total on 0-100
(``WEIGHTS``: levels 5, rooms 3, stairs 3, doors 2, windows 2, openings 1, walls 1); overall the mean over the
projects. A type enters the total when the truth or the reading has it: with truth 0 and read > 0 it enters with F1 0
and its weight (invented elements count); with both 0 it stays out. The matching (constants below, ``match``):

- levels by id;
- rooms on the same level by normalised label (``truth.norm_label``) and centroid within ``ROOM_CENTROID_M``, or by
  polygon IoU >= ``ROOM_IOU_MIN`` (labels differing, missing, or the centroids further apart);
- doors, windows and the other openings on the same level, each class by itself, by centre within ``OPENING_CENTER_M``;
- walls by centre-line overlap >= ``WALL_OVERLAP_SHARE`` of the shorter one, both ends of the shorter one within
  ``WALL_LATERAL_M`` of the longer one's line, thickness within ``WALL_THICKNESS_M``;
- stairs on the same level by centre within ``STAIR_CENTER_M``;
- one to one, best pairs first (``_greedy``: a greedy assignment, not a maximum matching; see its docstring);
- a truth element the user negated (``absent: true``) is no truth element; a read element that matches it is an
  ``absent_hit``: counted as read, never as matched (the reading is penalised for having it);
- a ``partial`` truth (the user accepted some levels, not the whole building) scores only the levels it has: a level
  the reading adds is neither right nor wrong there.

``results/reading_scores.json`` holds ``{"note", "entries": [{commit, date, projects: {p: {<type>: {truth, read,
matched, absent_hits, recall, precision, f1}, total, truth_status, truth_commit, read_commit}}, overall}]}``;
``--update`` appends the new entry, never one with a failed reading (an ``error`` entry is printed and the command
exits 1); ``--gate`` compares the new numbers with the newest stored number of each project (``latest``, errored
entries skipped) and exits 1 when the overall falls by more than ``GATE_OVERALL_DROP`` or any project by more than
``GATE_PROJECT_DROP``; a full run (no ``--projects``) also fails when a stored project is not scored. With ``--update``
the entry is appended only when the gate holds. Each reading's folder gets ``reading_check/score.json``.

Why: the regression set (``regress.py``) stops a reading from changing its counts; it cannot say how far a reading is
from the truth, nor whether a new rule brought a project nearer to it. The score per commit is the gate every change
of the reader (R2), the ranker (R3) and the reviewers (R4 to R6) must pass: the total rises, no project falls. The
synthetic projects are scored against their exact truth, so their numbers are the first honest ones: a synthetic
failure class below 100 is expected until the reader handles it (``tests/test_synthetic_failure_classes_20261104``).

How: pure functions over the truth dicts (``truth.extract`` of the new reading against the truth file); shapely for
the room IoU only; no AI, no pod.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
from pathlib import Path
from typing import Optional

from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[2]
SCORES_PATH = REPO / "results" / "reading_scores.json"
SCORES_NOTE = ("Reading score per commit against results/reading_truth/ (python -m wenart.reading_check score). "
               "A real project's truth is its accepted reading, so the first entry made right after `truth build` "
               "equals the truth by construction (100) for those projects; the synthetic projects are scored against "
               "their exact truth (projects/<p>/truth), so their first numbers are real and a failure class below "
               "100 is expected until the reader handles it. Entries with a failed reading are never stored.")
ROOM_CENTROID_M = 1.0
ROOM_IOU_MIN = 0.5
OPENING_CENTER_M = 0.30
WALL_OVERLAP_SHARE = 0.5
WALL_LATERAL_M = 0.15
WALL_THICKNESS_M = 0.05
STAIR_CENTER_M = 1.0
WEIGHTS = {"levels": 5, "rooms": 3, "stairs": 3, "doors": 2, "windows": 2, "openings": 1, "walls": 1}
TYPES = tuple(WEIGHTS)
GATE_OVERALL_DROP = 0.5
GATE_PROJECT_DROP = 2.0


# --- geometry -------------------------------------------------------------------------------------------------------

def _dist(a, b) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def polygon_iou(a: list, b: list) -> float:
    """Intersection over union of two polygons (0 when either is empty or invalid)."""
    if len(a or []) < 3 or len(b or []) < 3:
        return 0.0
    try:
        from shapely.geometry import Polygon
        pa, pb = Polygon(a).buffer(0), Polygon(b).buffer(0)
        union = pa.union(pb).area
        return pa.intersection(pb).area / union if union > 1e-9 else 0.0
    except Exception:
        return 0.0


def wall_overlap(a: dict, b: dict) -> Optional[tuple]:
    """``(share, lateral_m)`` when two walls match by the rules of the module docstring, else None: the overlap of
    the shorter one's centre line along the longer one's axis as a share of the shorter length, and the larger
    lateral offset of the shorter one's ends from the longer one's line."""
    la, lb = _dist(a["start"], a["end"]), _dist(b["start"], b["end"])
    if la < 1e-6 or lb < 1e-6:
        return None
    long_, short, ll, ls = (a, b, la, lb) if la >= lb else (b, a, lb, la)
    ox, oy = float(long_["start"][0]), float(long_["start"][1])
    ux, uy = (float(long_["end"][0]) - ox) / ll, (float(long_["end"][1]) - oy) / ll
    along, lateral = [], 0.0
    for p in (short["start"], short["end"]):
        dx, dy = float(p[0]) - ox, float(p[1]) - oy
        along.append(dx * ux + dy * uy)
        lateral = max(lateral, abs(dx * uy - dy * ux))
    if lateral > WALL_LATERAL_M:
        return None
    overlap = min(ll, max(along)) - max(0.0, min(along))
    share = overlap / ls if overlap > 0 else 0.0
    if share < WALL_OVERLAP_SHARE:
        return None
    ta, tb = a.get("thickness"), b.get("thickness")
    if ta is not None and tb is not None and abs(float(ta) - float(tb)) > WALL_THICKNESS_M:
        return None
    return (round(share, 4), round(lateral, 4))


# --- matching -------------------------------------------------------------------------------------------------------

def _greedy(pairs: list) -> list:
    """One-to-one assignment of ``(key, i, j)`` candidates, best key first; the chosen ``(i, j)`` pairs.

    Known limit: greedy, not a maximum matching. In a chain where the best pair blocks two others (truth A at 0 and
    B at 0.25; read X at 0.20 and Y at 0.45, tolerance 0.30) it takes B-X (0.05) and leaves A and Y unmatched (one
    match), where a maximum matching gives A-X and B-Y (two). Elements of one level rarely stand that close, and a
    greedy choice is the same for truth and reading, so the loss is accepted and tested
    (``test_reading_truth_20261104``)."""
    used_i, used_j, out = set(), set(), []
    for _key, i, j in sorted(pairs, key=lambda t: t[0]):
        if i in used_i or j in used_j:
            continue
        used_i.add(i)
        used_j.add(j)
        out.append((i, j))
    return out


def _at(e: dict, *keys) -> tuple:
    """An element's place as a sortable tuple (the tie-break of equal pairs, so the matching never depends on the
    order of the lists; 6 Nov 2026)."""
    out = []
    for k in keys:
        v = e.get(k)
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
            out.append(tuple(sorted((round(float(q[0]), 6), round(float(q[1]), 6)) for q in v)))
        elif isinstance(v, (list, tuple)):
            out.append(tuple(round(float(q), 6) for q in v))
        else:
            out.append((float(v),) if isinstance(v, (int, float)) else ())
    return tuple(out)


def match_rooms(truth: list, read: list) -> list:
    """The matched ``(truth index, read index)`` pairs of one level's rooms (the module docstring's rules)."""
    pairs = []
    for i, t in enumerate(truth):
        tl, tc = TR.norm_label(t.get("label")), t.get("centroid")
        for j, r in enumerate(read):
            rl, rc = TR.norm_label(r.get("label")), r.get("centroid")
            tie = (_at(t, "centroid", "polygon"), _at(r, "centroid", "polygon"))
            if tl and tl == rl and tc and rc and _dist(tc, rc) <= ROOM_CENTROID_M:
                pairs.append(((0, round(_dist(tc, rc), 9)) + tie, i, j))
                continue
            iou = polygon_iou(t.get("polygon"), r.get("polygon"))
            if iou >= ROOM_IOU_MIN:
                pairs.append(((1, round(1.0 - iou, 9)) + tie, i, j))
    return _greedy(pairs)


def match_points(truth: list, read: list, tol: float, key: str = "center") -> list:
    """Matched pairs of elements with a point (openings, stairs): same class lists in, centres within ``tol``."""
    pairs = []
    for i, t in enumerate(truth):
        if not t.get(key):
            continue
        for j, r in enumerate(read):
            if r.get(key) and _dist(t[key], r[key]) <= tol:
                pairs.append(((round(_dist(t[key], r[key]), 9), _at(t, key, "width"), _at(r, key, "width")), i, j))
    return _greedy(pairs)


def match_walls(truth: list, read: list) -> list:
    """The matched pairs of one level's walls: the largest overlap share of the shorter wall first, then (6 Nov 2026,
    review: a long wall took a short wall it contains and left the short truth wall alone, depending on the order of
    the reading) the largest share of the longer wall, the smaller lateral offset, then the places; never the order."""
    pairs = []
    for i, t in enumerate(truth):
        for j, r in enumerate(read):
            ov = wall_overlap(t, r)
            if ov is not None:
                lt, lr = _dist(t["start"], t["end"]), _dist(r["start"], r["end"])
                long_share = round(ov[0] * min(lt, lr) / max(lt, lr), 4)
                pairs.append(((-ov[0], -long_share, ov[1], _at(t, "start", "end", "thickness"),
                               _at(r, "start", "end", "thickness")), i, j))
    return _greedy(pairs)


def match_kind(kind: str, truth: list, read: list) -> list:
    if kind == "rooms":
        return match_rooms(truth, read)
    if kind == "walls":
        return match_walls(truth, read)
    if kind == "stairs":
        return match_points(truth, read, STAIR_CENTER_M)
    return match_points(truth, read, OPENING_CENTER_M)


def _stats(n_truth: int, n_read: int, matched: int, absent_hits: int = 0) -> dict:
    recall = matched / n_truth if n_truth else 1.0
    precision = matched / n_read if n_read else (1.0 if not n_truth else 0.0)
    f1 = 2 * recall * precision / (recall + precision) if recall + precision > 0 else 0.0
    return {"truth": n_truth, "read": n_read, "matched": matched, "absent_hits": absent_hits,
            "recall": round(recall, 4), "precision": round(precision, 4), "f1": round(f1, 4)}


def match(truth: dict, read: dict) -> dict:
    """The per-type numbers and the total of a reading (a truth-shaped dict, ``truth.extract``) against a truth
    (pure): ``{<type>: {truth, read, matched, absent_hits, recall, precision, f1}, "total": 0-100}``."""
    partial = truth.get("status") == "partial"
    t_levels = [lv["id"] for lv in truth.get("levels") or []]
    r_levels = [lv["id"] for lv in read.get("levels") or []]
    r_counted = [lid for lid in r_levels if lid in t_levels] if partial else r_levels
    out = {"levels": _stats(len(t_levels), len(r_counted), len(set(t_levels) & set(r_levels)))}
    sums = {t: [0, 0, 0, 0] for t in TR.ELEMENT_TYPES}
    for lid in t_levels:
        tl = (truth.get("per_level") or {}).get(lid) or {}
        rl = (read.get("per_level") or {}).get(lid) or {}
        for kind in TR.ELEMENT_TYPES:
            all_t, rr = tl.get(kind) or [], rl.get(kind) or []
            tt = TR.positives(all_t)
            absent = [e for e in all_t if e.get("absent")]
            m = match_kind(kind, tt, rr)
            hits = 0
            if absent:
                left = [r for j, r in enumerate(rr) if j not in {j for _i, j in m}]
                hits = len(match_kind(kind, absent, left))
            sums[kind][0] += len(tt)
            sums[kind][1] += len(rr)
            sums[kind][2] += len(m)
            sums[kind][3] += hits
    if not partial:                       # elements the reading puts on levels the truth has not: read, unmatched
        for lid in r_levels:
            if lid in t_levels:
                continue
            for kind in TR.ELEMENT_TYPES:
                sums[kind][1] += len(((read.get("per_level") or {}).get(lid) or {}).get(kind) or [])
    for kind, (nt, nr, nm, nh) in sums.items():
        out[kind] = _stats(nt, nr, nm, nh)
    out["total"] = total(out)
    return out


def total(per_type: dict) -> float:
    """The weighted total on 0-100 (``WEIGHTS``; pure) over the types the truth or the reading has: truth 0 with
    read > 0 enters with its weight and F1 0 (invented elements count); both 0 stays out."""
    num = den = 0.0
    for kind, w in WEIGHTS.items():
        st = per_type.get(kind)
        if not st or (not st.get("truth") and not st.get("read")):
            continue
        num += w * (float(st["f1"]) if st.get("truth") else 0.0)
        den += w
    return round(100.0 * num / den, 2) if den else 0.0


def overall(projects: dict) -> float:
    totals = [float(v.get("total") or 0.0) for v in projects.values() if not v.get("error")]
    return round(sum(totals) / len(totals), 2) if totals else 0.0


# --- the gate and the files -----------------------------------------------------------------------------------------

def latest(stored: list) -> Optional[dict]:
    """The newest stored numbers per project folded into one entry (pure): ``{"projects": {p: {..., "commit"}},
    "overall"}``; None when nothing is stored. A subset run (``--projects``) stores only what it scored, so the
    gate compares each project with the last entry that has it; a project entry with an ``error`` is skipped."""
    projects: dict = {}
    for entry in reversed(stored or []):
        for p, v in (entry.get("projects") or {}).items():
            if p not in projects and not v.get("error"):
                projects[p] = dict(v, commit=entry.get("commit"))
    return {"projects": projects, "overall": overall(projects)} if projects else None


def falls(last: Optional[dict], new: dict, full: bool = False) -> list[str]:
    """What fell against the stored numbers (pure; ``last`` is ``latest(stored)``): over the projects both have,
    the overall by more than ``GATE_OVERALL_DROP`` or a project by more than ``GATE_PROJECT_DROP``. A project whose
    reading failed stands at 0 with its error and falls; a project scored for the first time is not compared; in a
    ``full`` run (no ``--projects``) a stored project that was not scored falls too."""
    if not last:
        return []
    was_all, now_all = last.get("projects") or {}, new.get("projects") or {}
    common = [p for p in now_all if p in was_all]
    out = []
    if common:
        def _mean(projects):                             # a failed reading counts as 0 here (it is a fall)
            return round(sum(float(projects[p].get("total") or 0) for p in common) / len(common), 2)
        w_over, n_over = _mean(was_all), _mean(now_all)
        if n_over < w_over - GATE_OVERALL_DROP:
            out.append(f"overall: {w_over:.2f} -> {n_over:.2f}" + (f" ({len(common)} projects)" if len(common)
                                                                      < len(was_all) else ""))
        for p in common:
            w, n = float(was_all[p].get("total") or 0), float(now_all[p].get("total") or 0)
            if n < w - GATE_PROJECT_DROP:
                err = now_all[p].get("error")
                out.append(f"{p}: {w:.2f} -> {n:.2f}" + (f" (reading failed: {err})" if err else ""))
    if full:
        for p in was_all:
            if p not in now_all:
                out.append(f"{p}: {float(was_all[p].get('total') or 0):.2f} -> not scored")
    return out


def load_scores(path: Path = SCORES_PATH) -> list:
    """The stored entries (the file holds ``{"note", "entries"}``; a plain list from the first version is read too)."""
    path = Path(path)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("entries") or []) if isinstance(data, dict) else list(data)


def save_scores(entries: list, path: Path = SCORES_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"note": SCORES_NOTE, "entries": entries}, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
    return path


def table(entry: dict) -> str:
    """The score table (project, total, F1 per type, the truth's status and source) as text."""
    cols = ["project", "total"] + list(TYPES) + ["truth"]
    rows = [cols]
    for p, v in sorted((entry.get("projects") or {}).items()):
        if v.get("error"):
            rows.append([p, "error"] + ["-"] * len(TYPES) + [str(v["error"])[:40]])
            continue
        rows.append([p, f"{float(v.get('total') or 0):.1f}"]
                    + [f"{v[t]['f1']:.2f}" if v.get(t) and (v[t].get("truth") or v[t].get("read")) else "-"
                       for t in TYPES]
                    + [f"{v.get('truth_source') or '?'} {v.get('truth_status') or ''}".strip()])
    rows.append(["overall", f"{float(entry.get('overall') or 0):.1f}"] + [""] * (len(TYPES) + 1))
    widths = [max(len(r[i]) for r in rows) for i in range(len(cols))]
    return "\n".join("  ".join(c.ljust(widths[i]) if i in (0, len(cols) - 1) else c.rjust(widths[i])
                               for i, c in enumerate(r)) for r in rows)


def score_project(project: str, work: Path, *, fresh: bool = False, truth_dir: Path = TR.TRUTH_DIR) -> dict:
    """Read one project (or use its reading in ``work``), match it against its truth, write the reading folder's
    ``reading_check/score.json`` and return the numbers with the truth's and the reading's provenance."""
    truth = TR.load_truth(project, truth_dir)
    if truth is None:
        raise FileNotFoundError(f"no truth file for {project} in {truth_dir}")
    folder = TR.reading(project, work, fresh)
    b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
    read = TR.extract(b, project=project, leave_out=truth.get("levels_left_out") or [])
    res = match(truth, read)
    res.update(truth_status=truth.get("status"), truth_source=truth.get("source"), truth_commit=truth.get("commit"),
               read_commit=TR.read_commit(folder))
    rc = folder / "reading_check"
    rc.mkdir(parents=True, exist_ok=True)
    (rc / "score.json").write_text(json.dumps(dict({"project": project}, **res), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
    return res


def main(args) -> int:
    import tempfile
    named = [p.strip() for p in (args.projects or "").split(",") if p.strip()]
    projects = named or TR.truth_projects()
    if not projects:
        print("reading score: no truth file in results/reading_truth/ (run `truth build` first) and no --projects")
        return 2
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_score_"))
    entry = {"commit": TR.git_head(), "date": _dt.date.today().isoformat(), "projects": {}, "overall": 0.0}
    for p in projects:
        try:
            entry["projects"][p] = score_project(p, work, fresh=bool(getattr(args, "fresh", False)))
        except Exception as exc:                                  # one failed reading must not hide the others
            print(f"{p}: not scored: {exc}")
            entry["projects"][p] = {"total": 0.0, "error": str(exc)}
    entry["overall"] = overall(entry["projects"])
    print(table(entry))
    errors = sorted(p for p, v in entry["projects"].items() if v.get("error"))
    stored = load_scores()
    last = latest(stored)
    fell = falls(last, entry, full=not named) if args.gate else []
    if args.gate:
        against = sorted({(v.get("commit") or "?")[:12] for p, v in (last or {}).get("projects", {}).items()
                          if p in entry["projects"]})
        print(("GATE: fell" if fell else "GATE: holds") + " against " + (", ".join(against) or "nothing stored")
              + ("\n  " + "\n  ".join(fell) if fell else ""))
    if args.update:
        if errors:
            print(f"scores: not stored, the reading of {', '.join(errors)} failed (an entry with an error is never "
                  f"a baseline)")
        elif not fell:
            print(f"scores: entry {len(stored) + 1} written to {save_scores(stored + [entry]).relative_to(REPO)}")
    return 1 if fell or errors else 0
