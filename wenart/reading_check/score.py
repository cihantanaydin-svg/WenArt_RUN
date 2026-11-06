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

6 Nov 2026 (user: "Only consider my revision with the screenshot I have given into previous projects others I have
not seen"): a real project's truth is SPARSE (``truth.build_sparse``: the user's correction records only) and is judged
entry by entry (``match_sparse``): a present entry is satisfied when the reading has an element of its kind on its
level within the kind's tolerance (and of its type where it gives one; a wall when the reading's walls on its line
cover ``WALL_OVERLAP_SHARE`` of its span), an absent entry when nothing matches; the project's total is 100 x the
weighted share of the satisfied entries (``WEIGHTS``; no precision term: what the truth does not list is not judged).
The stored entry keeps every entry's result with its record ids, and the gate falls for a sparse project when an entry
satisfied before is no longer satisfied, whatever the total, naming the records. The stored entries carry
``truth_kind`` (``TRUTH_KIND``); ``latest`` and ``falls`` compare only within one kind, so the entries made against the
withdrawn accepted readings (no ``truth_kind``) stay as history. The synthetic projects keep F1 against their exact
truth; the gate's overall is theirs alone (``synthetic_overall``), while the overall of all projects, which mixes
satisfied shares with F1, is printed and stored as information. A sparse project's total is reported, never gated.

``results/reading_scores.json`` holds ``{"note", "entries": [{commit, date, projects: {p: {<type>: {truth, read,
matched, absent_hits, recall, precision, f1}, total, truth_status, truth_commit, read_commit}}, overall}]}``;
``--update`` appends the new entry, never one with a failed reading (an ``error`` entry is printed and the command
exits 1); ``--gate`` compares the new numbers with the newest stored number of each project (``latest``, errored
entries skipped) and exits 1 when the synthetic overall falls by more than ``GATE_OVERALL_DROP``, a synthetic project
by more than ``GATE_PROJECT_DROP`` or a sparse project loses a satisfied entry (``falls``); a full run (no
``--projects``) also fails when a stored project is not scored. With ``--update``
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
TRUTH_KIND = "user_corrections_v1"        # the series of the stored entries since 6 Nov 2026
SCORES_NOTE = ("Reading score per commit against results/reading_truth/ (python -m wenart.reading_check score). "
               "Since 6 Nov 2026 (truth_kind user_corrections_v1; user: \"Only consider my revision with the "
               "screenshot I have given into previous projects others I have not seen\") a real project's truth is "
               "sparse: the user's correction records only, each entry present or absent; its total is 100 x the "
               "weighted share of the satisfied entries, stored per entry with its record ids, and it falls when an "
               "entry satisfied before is no longer satisfied (named by record); its total is reported, never "
               "gated. The synthetic projects are scored with F1 against their exact truth (projects/<p>/truth); a "
               "failure class below 100 is expected until the reader handles it; the gate's overall is theirs "
               "(overall_synthetic), the overall of all projects is information. The entries without truth_kind were made against the accepted readings "
               "(withdrawn on 6 Nov 2026): history only, never compared. Entries with a failed reading are never "
               "stored.")
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


def match(truth: dict, read: dict, building: Optional[dict] = None) -> dict:
    """The per-type numbers and the total of a reading (a truth-shaped dict, ``truth.extract``) against a truth
    (pure): ``{<type>: {truth, read, matched, absent_hits, recall, precision, f1}, "total": 0-100}``. A sparse truth
    (a real project's: the user's corrections only) is judged entry by entry instead (``match_sparse``)."""
    if TR.is_sparse(truth):
        return match_sparse(truth, read, building)
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


# --- the sparse truth (a real project's: the user's corrections only, 6 Nov 2026) -----------------------------------

def wall_cover(entry: dict, read: list) -> float:
    """The share of a truth wall span covered by the reading's walls on its line (pure): the union, along the span,
    of the reading walls that match it by the pair rule's lateral offset and thickness (``wall_overlap`` without its
    share test), over the span's length. A long wall read in pieces covers its span as one wall does."""
    s, e = entry["start"], entry["end"]
    ls = _dist(s, e)
    if ls < 1e-6:
        return 0.0
    ux, uy = (float(e[0]) - float(s[0])) / ls, (float(e[1]) - float(s[1])) / ls
    spans = []
    for r in read:
        lr = _dist(r["start"], r["end"])
        if lr < 1e-6:
            continue
        long_, short, ll = (entry, r, ls) if ls >= lr else (r, entry, lr)
        ox, oy = float(long_["start"][0]), float(long_["start"][1])
        vx, vy = (float(long_["end"][0]) - ox) / ll, (float(long_["end"][1]) - oy) / ll
        if max(abs((float(p[0]) - ox) * vy - (float(p[1]) - oy) * vx) for p in (short["start"], short["end"])) \
                > WALL_LATERAL_M:
            continue
        ta, tb = entry.get("thickness"), r.get("thickness")
        if ta is not None and tb is not None and abs(float(ta) - float(tb)) > WALL_THICKNESS_M:
            continue
        along = sorted((float(p[0]) - float(s[0])) * ux + (float(p[1]) - float(s[1])) * uy
                       for p in (r["start"], r["end"]))
        lo, hi = max(0.0, along[0]), min(ls, along[1])
        if hi > lo:
            spans.append((lo, hi))
    covered, end = 0.0, 0.0
    for lo, hi in sorted(spans):
        lo = max(lo, end)
        if hi > lo:
            covered += hi - lo
            end = hi
    return round(covered / ls, 4)


def solid_pieces(wall: dict, gaps: list) -> list:
    """The solid pieces of a reading wall (pure): the wall less its doorless openings (``gaps``: the reading's
    ``openings`` on it, each its centre and width along the wall). The reader keeps a wall whole through a passage and
    puts the passage on it as an opening, so "no wall here" is checked on what stands, not on the wall's line; a door
    or a window stands in a wall and cuts nothing."""
    s, e = wall["start"], wall["end"]
    lw = _dist(s, e)
    if lw < 1e-6:
        return []
    ux, uy = (float(e[0]) - float(s[0])) / lw, (float(e[1]) - float(s[1])) / lw
    cuts = []
    for g in gaps:
        if not g.get("center") or not g.get("width"):
            continue
        a = (float(g["center"][0]) - float(s[0])) * ux + (float(g["center"][1]) - float(s[1])) * uy
        cuts.append((max(0.0, a - float(g["width"]) / 2.0), min(lw, a + float(g["width"]) / 2.0)))
    pieces, at = [], 0.0
    for lo, hi in sorted(c for c in cuts if c[1] > c[0]):
        if lo > at:
            pieces.append((at, lo))
        at = max(at, hi)
    if lw > at:
        pieces.append((at, lw))
    return [dict(wall, start=[float(s[0]) + ux * a, float(s[1]) + uy * a],
                 end=[float(s[0]) + ux * b, float(s[1]) + uy * b]) for a, b in pieces if b - a > 1e-6]


def _type_of(room: dict) -> str:
    return " ".join(str(room.get("room_type") or "").lower().split())


def ground_heights(building: Optional[dict]) -> list:
    """The ground heights a reading drew (``site.ground.levels[].z.value``), sorted; empty without any."""
    ground = ((building or {}).get("site") or {}).get("ground")
    out = []
    for g in (ground.get("levels") or []) if isinstance(ground, dict) else []:
        z = g.get("z") if isinstance(g, dict) else None
        v = z.get("value") if isinstance(z, dict) else None
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v)):
            out.append(round(float(v), 3))
    return sorted(out)


def check_assertion(a: dict, read: dict, building: Optional[dict] = None) -> tuple[bool, str]:
    """``(satisfied, what the reading has)`` of a project-level assertion (``truth.parse_assert``'s form; pure)."""
    levels = read.get("levels") or []
    what = a["what"]
    if what == "level_count":
        return len(levels) == a["value"], f"{len(levels)} levels"
    if what == "storey_heights":
        el = sorted({round(float(lv["elevation"]), 2) for lv in levels
                     if isinstance(lv.get("elevation"), (int, float))})
        rel = [round(x - el[0], 2) for x in el] if el else []
        ok = len(rel) == len(a["values"]) and all(abs(x - v) <= a["tolerance"] + 1e-9 for x, v in zip(rel, a["values"]))
        return ok, f"storeys at {rel}"
    if what == "level_elevation":
        lv = next((x for x in levels if x.get("id") == a["level"]), None)
        if lv is None or not isinstance(lv.get("elevation"), (int, float)):
            return False, f"no level {a['level']}" if lv is None else f"{a['level']} without an elevation"
        return abs(float(lv["elevation"]) - a["value"]) <= a["tolerance"] + 1e-9, f"{a['level']} at {lv['elevation']}"
    if what == "ground_z":
        g = ground_heights(building)
        if not g:
            return False, "no ground height read"
        return all(abs(x - a["value"]) <= a["tolerance"] + 1e-9 for x in g), f"ground at {g}"
    return False, f"unknown assertion {what}"


def match_sparse(truth: dict, read: dict, building: Optional[dict] = None) -> dict:
    """A reading against a sparse truth (pure): every entry satisfied or not, nothing else judged.

    - present: an element of that kind on that level within the kind's tolerance (the score's own one-to-one matching:
      ``match_points`` for doors, windows, openings and stairs, ``match_rooms`` for rooms among the reading's rooms of
      the entry's room type when it gives one); a wall when the reading's walls on its line cover at least
      ``WALL_OVERLAP_SHARE`` of its span (``wall_cover``);
    - absent: no element of that kind matches (the elements matched to a present entry of the level excepted, as in
      ``match``); a wall when no solid piece of a reading wall (``solid_pieces``: the wall less the doorless openings
      the reader put on it; a piece shorter than its thickness or ``truth.WALL_PIECE_MIN_M`` is a joint) matches the
      span by ``wall_overlap``;
    - an entry on a level the reading does not have is not satisfied (an absent one cannot be confirmed either);
    - an asserted level: the reading has it, with the label, elevation (within ``truth.ASSERT_TOL_M``) and order
      given; a project-level assertion: ``check_assertion``.

    Returns ``{"entries": [{id, level, type, absent, records, satisfied}], "assertions": [...], <type>: {present,
    present_ok, absent, absent_ok}, "records": {record id: [satisfied, entries]}, "unsatisfied": [entry ids],
    "total"}``: the total is 100 x the weighted share of the satisfied entries (``WEIGHTS`` by type; an asserted level
    and a project-level assertion weigh as ``levels``), None when the truth asserts nothing."""
    out_entries, assertions = [], []
    per_type = {t: {"present": 0, "present_ok": 0, "absent": 0, "absent_ok": 0} for t in TYPES}
    r_levels = {lv["id"]: lv for lv in read.get("levels") or []}
    rper = read.get("per_level") or {}

    def note(e, lid, t, ok, why=None):
        row = {"id": e.get("id"), "level": lid, "type": t, "absent": bool(e.get("absent")),
               "records": list(e.get("corrections") or []), "satisfied": bool(ok)}
        if why and not ok:
            row["why"] = why
        out_entries.append(row)
        k = "absent" if e.get("absent") else "present"
        per_type[t][k] += 1
        per_type[t][k + "_ok"] += int(bool(ok))

    for lid, lv in (truth.get("per_level") or {}).items():
        have = lid in r_levels
        rl = rper.get(lid) or {}
        for t in TR.ELEMENT_TYPES:
            ents = lv.get(t) or []
            pres, absn = TR.positives(ents), [e for e in ents if e.get("absent")]
            rr = rl.get(t) or [] if have else []
            if not have:
                for e in ents:
                    note(e, lid, t, False, f"the reading has no level {lid}")
                continue
            used: set = set()
            if t == "walls":
                for e in pres:
                    c = wall_cover(e, rr)
                    note(e, lid, t, c >= WALL_OVERLAP_SHARE, f"covered {c:.2f} of the span")
                if absn:
                    gaps: dict = {}
                    for o in rl.get("openings") or []:
                        if o.get("wall_id"):
                            gaps.setdefault(o["wall_id"], []).append(o)
                    # a piece shorter than its own thickness (or ``truth.WALL_PIECE_MIN_M``) is a joint, as in the
                    # truth's own cut: a jamb stub at the end of a passage is no wall across it
                    solid = [(r, piece) for r in rr for piece in solid_pieces(r, gaps.get(r.get("id"), []))
                             if _dist(piece["start"], piece["end"]) >= max(TR.WALL_PIECE_MIN_M,
                                                                          float(piece.get("thickness") or 0.0))]
                for e in absn:
                    hit = next((r for r, piece in solid if wall_overlap(e, piece) is not None), None)
                    note(e, lid, t, hit is None, f"read: {hit.get('id') if hit else ''}")
                continue
            if t == "rooms":
                groups: dict = {}
                for i, e in enumerate(pres):
                    groups.setdefault(_type_of(e), []).append(i)
                ok_idx = set()
                for ty, idx in sorted(groups.items()):
                    cand = [j for j, r in enumerate(rr) if not ty or _type_of(r) == ty]
                    for i, j in match_rooms([pres[i] for i in idx], [rr[j] for j in cand]):
                        ok_idx.add(idx[i])
                        used.add(cand[j])
                for i, e in enumerate(pres):
                    note(e, lid, t, i in ok_idx, "no room of its type at its place" if _type_of(e) else
                         "no room at its place")
                left = [r for j, r in enumerate(rr) if j not in used]
                for e in absn:
                    hit = match_rooms([e], left)
                    note(e, lid, t, not hit, f"read: {left[hit[0][1]].get('id')}" if hit else None)
                continue
            tol = STAIR_CENTER_M if t == "stairs" else OPENING_CENTER_M
            pairs = match_points(pres, rr, tol)
            ok_idx = {i for i, _j in pairs}
            used = {j for _i, j in pairs}
            for i, e in enumerate(pres):
                note(e, lid, t, i in ok_idx, f"no {TR.TYPE_KIND[t]} within {tol} m")
            left = [r for j, r in enumerate(rr) if j not in used]
            for e in absn:
                hit = next((r for r in left if r.get("center") and e.get("center")
                            and _dist(r["center"], e["center"]) <= tol), None)
                note(e, lid, t, hit is None, f"read: {hit.get('id')}" if hit else None)
    for lv in truth.get("levels") or []:
        if not lv.get("asserted"):
            continue
        r = r_levels.get(lv["id"])
        ok = r is not None
        if ok and lv.get("label") is not None:
            ok = TR.norm_label(lv["label"]) == TR.norm_label(r.get("label"))
        if ok and lv.get("elevation") is not None:
            ok = isinstance(r.get("elevation"), (int, float)) and \
                abs(float(r["elevation"]) - float(lv["elevation"])) <= TR.ASSERT_TOL_M + 1e-9
        if ok and lv.get("order") is not None:
            ok = r.get("order") == lv["order"]
        note({"id": f"level_{lv['id']}", "corrections": lv.get("corrections")}, lv["id"], "levels", ok,
             "the reading's level differs" if r is not None else f"the reading has no level {lv['id']}")
    for a in truth.get("project_assertions") or []:
        ok, has = check_assertion(a, read, building)
        assertions.append({"id": a["id"], "what": a["what"], "records": list(a.get("corrections") or []),
                           "satisfied": bool(ok), "read": has})
        per_type["levels"]["present"] += 1
        per_type["levels"]["present_ok"] += int(bool(ok))
    num = den = 0.0
    records: dict = {}
    for row in out_entries + assertions:
        w = WEIGHTS[row.get("type") or "levels"]
        den += w
        num += w * int(row["satisfied"])
        for rid in row["records"]:
            got = records.setdefault(rid, [0, 0])
            got[0] += int(row["satisfied"])
            got[1] += 1
    out = {"entries": sorted(out_entries, key=lambda x: (TR._level_key(x["level"]), x["type"], str(x["id"]))),
           "assertions": assertions, "records": {k: records[k] for k in sorted(records, key=TR._record_key)},
           "unsatisfied": [x["id"] for x in sorted(out_entries + assertions, key=lambda x: str(x["id"]))
                           if not x["satisfied"]],
           "total": round(100.0 * num / den, 2) if den else None}
    out.update(per_type)
    return out


def satisfied_ids(result: dict) -> dict:
    """``{entry or assertion id: (satisfied, records)}`` of a stored sparse result (pure)."""
    return {x["id"]: (bool(x.get("satisfied")), list(x.get("records") or []))
            for x in (result.get("entries") or []) + (result.get("assertions") or []) if x.get("id")}


def overall(projects: dict) -> float:
    """The mean total of the projects (a failed reading and a truth that asserts nothing yet left out): information
    since 6 Nov 2026 (it mixes the sparse projects' satisfied shares with the synthetic projects' F1); the gate uses
    ``synthetic_overall``."""
    totals = [float(v["total"]) for v in projects.values() if not v.get("error") and v.get("total") is not None]
    return round(sum(totals) / len(totals), 2) if totals else 0.0


def synthetic_overall(projects: dict) -> float:
    """The mean total of the projects with an F1 truth (the synthetic ones; no sparse truth, no failed reading): the
    overall the gate compares (``falls``)."""
    return overall({p: v for p, v in projects.items() if not v.get("sparse")})


# --- the gate and the files -----------------------------------------------------------------------------------------

def latest(stored: list, truth_kind: Optional[str] = TRUTH_KIND) -> Optional[dict]:
    """The newest stored numbers per project folded into one entry (pure): ``{"projects": {p: {..., "commit",
    "truth_kind"}}, "overall", "truth_kind"}``; None when nothing is stored. Only the entries of ``truth_kind`` count
    (6 Nov 2026: the entries made against the withdrawn accepted readings carry none and are never compared with the
    series of the user's corrections). A subset run (``--projects``) stores only what it scored, so the gate compares
    each project with the last entry that has it; a project entry with an ``error`` is skipped."""
    projects: dict = {}
    for entry in reversed(stored or []):
        if entry.get("truth_kind") != truth_kind:
            continue
        for p, v in (entry.get("projects") or {}).items():
            if p not in projects and not v.get("error"):
                projects[p] = dict(v, commit=entry.get("commit"), truth_kind=entry.get("truth_kind"))
    return {"projects": projects, "overall": overall(projects), "overall_synthetic": synthetic_overall(projects),
            "truth_kind": truth_kind} if projects else None


def _lost(was: dict, now: dict) -> list[str]:
    """The record ids of a sparse project whose entries were satisfied in ``was`` and are not in ``now`` (pure), each
    with those entries: ``["C0034 (u_C0034_2, u_C0034_5)", ...]``. An entry the new truth no longer has (the truth
    changed) is not compared."""
    before, after = satisfied_ids(was), satisfied_ids(now)
    by_record: dict = {}
    for eid, (ok, recs) in before.items():
        if ok and eid in after and not after[eid][0]:
            for rid in sorted(set(recs) | set(after[eid][1]), key=TR._record_key):
                by_record.setdefault(rid, []).append(eid)
    return [f"{rid} ({', '.join(sorted(ids))})" for rid, ids in sorted(by_record.items(),
                                                                       key=lambda kv: TR._record_key(kv[0]))]


def falls(last: Optional[dict], new: dict, full: bool = False, withdrawn=()) -> list[str]:
    """What fell against the stored numbers (pure; ``last`` is ``latest(stored)``), over the projects both have:

    - the synthetic overall (``synthetic_overall``: the mean total of the projects with an F1 truth, the synthetic
      ones) by more than ``GATE_OVERALL_DROP``, and such a project by more than ``GATE_PROJECT_DROP``;
    - a project with a sparse truth (a real project's: the user's corrections) only when an entry satisfied in the
      stored numbers is no longer satisfied, named by its record ids. Its total is reported, never gated: a new entry
      or a new record not in the stored numbers never falls (6 Nov 2026, the coordinator's decision: the overall of
      all projects mixes satisfied shares with F1 and fell whenever a new record of the user was not met yet; it is
      printed as information only).

    Numbers of another truth kind are never compared (``latest`` folds one kind; an entry or a project of another kind
    is left out here too). A project whose reading failed stands at 0 with its error and falls; a project scored for
    the first time is not compared; in a ``full`` run (no ``--projects``) a stored project that was not scored falls
    too, unless it left the truth (``withdrawn``: the user's acceptance was withdrawn, or no applicable record is
    left)."""
    if not last or last.get("truth_kind") != new.get("truth_kind"):
        return []
    was_all, now_all = last.get("projects") or {}, new.get("projects") or {}
    kind = new.get("truth_kind")

    def comparable(p) -> bool:                           # one truth kind, and both sparse or both F1
        w, n = was_all[p], now_all[p]
        if w.get("truth_kind", kind) != kind:
            return False
        return bool(n.get("error")) or bool(w.get("sparse")) == bool(n.get("sparse"))

    common = [p for p in now_all if p in was_all and comparable(p)]
    out = []
    f1 = [p for p in common if not was_all[p].get("sparse") and was_all[p].get("total") is not None]
    if f1:
        def _mean(projects):                             # a failed reading counts as 0 here (it is a fall)
            return round(sum(float(projects[p].get("total") or 0) for p in f1) / len(f1), 2)
        w_over, n_over = _mean(was_all), _mean(now_all)
        n_f1 = sum(1 for v in was_all.values() if not v.get("sparse"))
        if n_over < w_over - GATE_OVERALL_DROP:
            out.append(f"synthetic overall: {w_over:.2f} -> {n_over:.2f}" + (f" ({len(f1)} projects)"
                                                                            if len(f1) < n_f1 else ""))
    for p in common:
        err = now_all[p].get("error")
        if err:
            out.append(f"{p}: {float(was_all[p].get('total') or 0):.2f} -> 0.00 (reading failed: {err})")
            continue
        if was_all[p].get("sparse"):
            lost = _lost(was_all[p], now_all[p])
            if lost:
                out.append(f"{p}: no longer satisfied: " + "; ".join(lost))
            continue
        w, n = float(was_all[p].get("total") or 0), float(now_all[p].get("total") or 0)
        if n < w - GATE_PROJECT_DROP:
            out.append(f"{p}: {w:.2f} -> {n:.2f}")
    if full:
        for p in was_all:
            if p not in now_all and p not in set(withdrawn):
                t = was_all[p].get("total")
                out.append(f"{p}: {float(t):.2f} -> not scored" if t is not None else f"{p}: not scored")
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


def _cell(v: dict, t: str) -> str:
    st = v.get(t) or {}
    if v.get("sparse"):
        n = int(st.get("present") or 0) + int(st.get("absent") or 0)
        return f"{int(st.get('present_ok') or 0) + int(st.get('absent_ok') or 0)}/{n}" if n else "-"
    return f"{st['f1']:.2f}" if st and (st.get("truth") or st.get("read")) else "-"


def table(entry: dict) -> str:
    """The score table as text: project, total, per type the F1 (an F1 truth) or the satisfied entries over the
    entries (a sparse truth), the truth's source and status."""
    cols = ["project", "total"] + list(TYPES) + ["truth"]
    rows = [cols]
    for p, v in sorted((entry.get("projects") or {}).items()):
        if v.get("error"):
            rows.append([p, "error"] + ["-"] * len(TYPES) + [str(v["error"])[:40]])
            continue
        rows.append([p, f"{float(v['total']):.1f}" if v.get("total") is not None else "-"]
                    + [_cell(v, t) for t in TYPES]
                    + [f"{v.get('truth_source') or '?'} {v.get('truth_status') or ''}".strip()
                       + (" (nothing measurable yet)" if v.get("measurable") is False else "")])
    rows.append(["overall (information)", f"{float(entry.get('overall') or 0):.1f}"] + [""] * (len(TYPES) + 1))
    syn = entry.get("overall_synthetic")
    if syn is None:
        syn = synthetic_overall(entry.get("projects") or {})
    rows.append(["synthetic overall (gated)", f"{float(syn):.1f}"] + [""] * (len(TYPES) + 1))
    widths = [max(len(r[i]) for r in rows) for i in range(len(cols))]
    return "\n".join("  ".join(c.ljust(widths[i]) if i in (0, len(cols) - 1) else c.rjust(widths[i])
                               for i, c in enumerate(r)) for r in rows)


def score_project(project: str, work: Path, *, fresh: bool = False, truth_dir: Path = TR.TRUTH_DIR) -> dict:
    """Read one project (or use its reading in ``work``), match it against its truth, write the reading folder's
    ``reading_check/score.json`` and return the numbers with the truth's and the reading's provenance."""
    truth = TR.load_truth(project, truth_dir)
    if truth is None:
        raise FileNotFoundError(f"no truth file for {project} in {truth_dir}")
    sparse = TR.is_sparse(truth)
    if sparse and not TR.entry_count(truth):            # nothing to check: no reading needed
        return {"total": None, "measurable": False, "sparse": True, "truth_status": truth.get("status"),
                "truth_source": truth.get("source"), "truth_commit": None,
                "not_measurable": [x.get("record") for x in truth.get("not_measurable") or []]}
    folder = TR.reading(project, work, fresh)
    b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
    read = TR.extract(b, project=project, leave_out=truth.get("levels_left_out") or [])
    res = match(truth, read, b)
    if sparse:
        res["sparse"] = True
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
    entry = {"commit": TR.git_head(), "date": _dt.date.today().isoformat(), "truth_kind": TRUTH_KIND,
             "projects": {}, "overall": 0.0}
    for p in projects:
        try:
            entry["projects"][p] = score_project(p, work, fresh=bool(getattr(args, "fresh", False)))
        except Exception as exc:                                  # one failed reading must not hide the others
            print(f"{p}: not scored: {exc}")
            entry["projects"][p] = {"total": 0.0, "error": str(exc)}
    entry["overall"] = overall(entry["projects"])
    entry["overall_synthetic"] = synthetic_overall(entry["projects"])
    print(table(entry))
    for p, v in sorted(entry["projects"].items()):
        if v.get("sparse") and v.get("unsatisfied"):
            print(f"{p}: not satisfied: " + ", ".join(v["unsatisfied"]))
    errors = sorted(p for p, v in entry["projects"].items() if v.get("error"))
    stored = load_scores()
    last = latest(stored, TRUTH_KIND)
    if last is None and any(e.get("truth_kind") != TRUTH_KIND for e in stored):
        print(f"gate: no stored entry of truth kind {TRUTH_KIND} yet (the older entries were made against another "
              f"truth and are never compared)")
    records = TR.load_corrections()
    withdrawn = []
    for p in (last or {}).get("projects", {}):
        if p in entry["projects"]:
            continue
        why = (TR.load_baseline(p) or {}).get("acceptance_withdrawn")
        if why:
            print(f"{p}: left the truth (the user's acceptance was withdrawn on {why.get('on') or '?'}: "
                  f"{why.get('reason') or '?'})")
            withdrawn.append(p)
        elif TR.load_truth(p) is None and TR.synthetic_truth_file(p) is None \
                and p not in TR.sparse_projects(records):
            print(f"{p}: left the truth (no applicable correction record of the user is left)")
            withdrawn.append(p)
    fell = falls(last, entry, full=not named, withdrawn=withdrawn) if args.gate else []
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
