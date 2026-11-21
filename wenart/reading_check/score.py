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
the entry is appended only when the gate holds. Each reading's folder gets ``reading_check/score.json``. 21 Nov 2026
(C0001, the user's OK "Yes, use the right one"): a record whose machine-located geometry the user's OK moved
(``truth move``, logged in the record) is judged at its new place: its old place's loss against the stored truth is a
note, not a fall, only while every entry of the record holds at the new place (``moved_with_ok``).

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
               "(overall_synthetic), the overall of all projects is information. The entries without truth_kind "
               "were made against the accepted readings "
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
#
# Review of 6 Nov 2026 (the gate must not be foolable): a wall is judged on what stands (the reading's walls less the
# doorless openings that reach their wall's height: a gap with a lintel leaves the wall over it), the same view for
# "a wall here" and "no wall here"; thickness decides only when the user stated it (never so far); an entry's level is
# found by its anchor (label, order, elevation), not by the reader's id alone; a negated room is read when a reading
# room covers half of it, whatever its label (a recess swallowed by its neighbour); an asserted attribute (a door's
# role, a lift door, a stair's landing end ...) must match.

WALL_PRESENT_SHARE = 0.8      # a wall the user asserted: what stands on its line covers this share of its span
WALL_ABSENT_SHARE = 0.5       # "no wall here": what stands on its line over this share of the span is a wall read
FULL_HEIGHT_TOL_M = 0.05      # a doorless opening this close to its wall's height is a passage: no wall over it
ROOM_SWALLOW_SHARE = 0.5      # a negated room is read when one reading room covers this share of its area
LEVEL_ELEVATION_TOL_M = 0.10  # a level found by its order and elevation (its label renamed) within this


def _on_line(entry: dict, r: dict) -> bool:
    """A reading wall lies on a truth span's line: parallel within ``truth.WALL_ANGLE_DEG`` and the shorter one's ends
    within ``WALL_LATERAL_M`` of the longer one's line (the pair rule's lateral test, with an angle test)."""
    ls, lr = _dist(entry["start"], entry["end"]), _dist(r["start"], r["end"])
    if ls < 1e-6 or lr < 1e-6:
        return False
    ux = (float(entry["end"][0]) - float(entry["start"][0])) / ls
    uy = (float(entry["end"][1]) - float(entry["start"][1])) / ls
    vx, vy = (float(r["end"][0]) - float(r["start"][0])) / lr, (float(r["end"][1]) - float(r["start"][1])) / lr
    if abs(ux * vy - uy * vx) > math.sin(math.radians(TR.WALL_ANGLE_DEG)):
        return False
    long_, short, ll = (entry, r, ls) if ls >= lr else (r, entry, lr)
    ox, oy = float(long_["start"][0]), float(long_["start"][1])
    wx, wy = (float(long_["end"][0]) - ox) / ll, (float(long_["end"][1]) - oy) / ll
    return max(abs((float(p[0]) - ox) * wy - (float(p[1]) - oy) * wx) for p in (short["start"], short["end"])) \
        <= WALL_LATERAL_M


def wall_cover(entry: dict, read: list) -> float:
    """The share of a truth wall span covered by reading walls on its line (pure): the union, along the span, of the
    reading pieces on its line (``_on_line``), over the span's length; the thickness counts only when the entry states
    one (a user's thickness: none so far). A long wall read in pieces covers its span as one wall does."""
    s, e = entry["start"], entry["end"]
    ls = _dist(s, e)
    if ls < 1e-6:
        return 0.0
    ux, uy = (float(e[0]) - float(s[0])) / ls, (float(e[1]) - float(s[1])) / ls
    spans = []
    for r in read:
        if not _on_line(entry, r):
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


def is_passage(gap: dict, wall_height: Optional[float]) -> bool:
    """A doorless opening with no wall over it: marked an open passage, or as high as its wall (within
    ``FULL_HEIGHT_TOL_M``). A gap without a height, or one with a lintel, leaves the wall standing over it."""
    if gap.get("open_passage"):
        return True
    h = gap.get("height")
    return (isinstance(h, (int, float)) and wall_height is not None
            and float(h) >= float(wall_height) - FULL_HEIGHT_TOL_M)


def solid_pieces(wall: dict, gaps: list, wall_height: Optional[float] = None) -> list:
    """What stands of a reading wall (pure): the wall less its doorless openings that are passages (``is_passage``:
    floor to ceiling); a door, a window or a gap with a lintel stands in the wall and cuts nothing. The reader keeps a
    wall whole through a passage and puts the passage on it as an opening, so the checks read what stands."""
    s, e = wall["start"], wall["end"]
    lw = _dist(s, e)
    if lw < 1e-6:
        return []
    height = wall.get("height") if wall_height is None else wall_height
    ux, uy = (float(e[0]) - float(s[0])) / lw, (float(e[1]) - float(s[1])) / lw
    cuts = []
    for g in gaps:
        if not g.get("center") or not g.get("width") or not is_passage(g, height):
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


def standing_walls(rl: dict, ceiling: Optional[float] = None) -> list:
    """``[(reading wall, piece)]``: what stands of a reading level's walls (``solid_pieces`` with the level's doorless
    openings; a wall without a height takes the level's ceiling height)."""
    gaps: dict = {}
    for o in rl.get("openings") or []:
        if o.get("wall_id"):
            gaps.setdefault(o["wall_id"], []).append(o)
    return [(r, piece) for r in rl.get("walls") or []
            for piece in solid_pieces(r, gaps.get(r.get("id"), []), r.get("height") or ceiling)]


def _type_of(room: dict) -> str:
    return " ".join(str(room.get("room_type") or "").lower().split())


def _norm(v):
    return " ".join(str(v).lower().split()) if isinstance(v, str) else v


def attrs_ok(attrs: Optional[dict], r: dict, building: Optional[dict] = None) -> bool:
    """A reading element carries every asserted attribute (pure but for ``main_entrance``, which asks the architect's
    own rule of the reading): ``landing_toward`` a direction, the half landing on that side of the stair's centre;
    ``main_entrance`` true, the reading's main entrance is this door; any other key, the element's own value."""
    for k, v in (attrs or {}).items():
        if k == "landing_toward":
            lc, c = r.get("landing_center"), r.get("center")
            if not lc or not c or (lc[0] - c[0]) * v[0] + (lc[1] - c[1]) * v[1] <= 0:
                return False
        elif k == "main_entrance":
            if bool(v) != (r.get("id") is not None and r.get("id") == _main_entrance(building)):
                return False
        elif _norm(r.get(k)) != _norm(v) and not (v is False and not r.get(k)):
            return False
    return True


def _main_entrance(building: Optional[dict]) -> Optional[str]:
    if not building:
        return None
    if "_main_entrance" not in building:
        try:
            from wenart.blender import architect_actions as AA
            building["_main_entrance"] = AA.main_entrance_id(building)
        except Exception:                                   # noqa: BLE001 - no answer is no main entrance
            building["_main_entrance"] = None
    return building["_main_entrance"]


def level_map(truth: dict, read: dict) -> dict:
    """``{truth level id: reading level id or None}`` (pure): a level with an anchor (its label, order, elevation from
    the reading the records were made on) is the reading level of that label (the same id first when several share
    it), else the level of the same id with the same order and elevation (a renamed label), else none; a level
    without an anchor is the reading level of its id. An inserted storey renumbers the ids; the anchor keeps every
    check on the floor the user corrected."""
    r_levels = read.get("levels") or []
    out = {}
    for lv in truth.get("levels") or []:
        lid = lv["id"]
        if lv.get("label") is None and lv.get("order") is None:
            out[lid] = lid if any(r["id"] == lid for r in r_levels) else None
            continue
        lbl = TR.norm_label(lv.get("label"))
        same = [r for r in r_levels if lbl and TR.norm_label(r.get("label")) == lbl]
        if same:
            out[lid] = next((r["id"] for r in same if r["id"] == lid), same[0]["id"])
            continue
        r = next((r for r in r_levels if r["id"] == lid), None)
        if r is not None and r.get("order") == lv.get("order") and isinstance(r.get("elevation"), (int, float)) \
                and lv.get("elevation") is not None \
                and abs(float(r["elevation"]) - float(lv["elevation"])) <= LEVEL_ELEVATION_TOL_M:
            out[lid] = lid
        else:
            out[lid] = None
    return out


def signature(t: str, e: dict) -> list:
    """What an entry asserts, as stored with its result (pure): its type, polarity, place rounded to 1 cm (a frame
    place if it has one) and attributes. An entry whose id names another signature in a later truth is another
    entry (a record re-placed or re-ordered), never compared by its id."""
    frame = e.get("frame") or {}
    place = frame or e
    key = [t, bool(e.get("absent"))]
    for k in ("center", "start", "end"):
        if place.get(k):
            key.append([round(float(place[k][0]), 2), round(float(place[k][1]), 2)])
    if (place.get("polygon") or []) and not any(place.get(k) for k in ("center", "start", "end")):
        c = centroid_of(place["polygon"])
        key.append([round(c[0], 2), round(c[1], 2)])
    if e.get("attrs"):                      # lists, never tuples: a stored (JSON) signature must compare equal
        key.append([[k, str(v)] for k, v in sorted(e["attrs"].items())])
    return key


def centroid_of(poly: list) -> list:
    return TR.centroid(poly) or [0.0, 0.0]


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
    """``(satisfied, what the reading has)`` of a project-level assertion (``truth.parse_assert``'s form; pure). The
    ground height holds when one of the reading's ground heights is the asserted one (a reading may draw one per
    side)."""
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
        return any(abs(x - a["value"]) <= a["tolerance"] + 1e-9 for x in g), f"ground at {g}"
    return False, f"unknown assertion {what}"


def _covered_share(poly: list, by: list) -> float:
    """The share of a polygon's area that one polygon of ``by`` covers at most (0 when invalid)."""
    if len(poly or []) < 3:
        return 0.0
    try:
        from shapely.geometry import Polygon
        p = Polygon(poly).buffer(0)
        if p.area <= 1e-9:
            return 0.0
        return max((p.intersection(Polygon(q).buffer(0)).area / p.area for q in by if len(q or []) >= 3),
                   default=0.0)
    except Exception:                                       # noqa: BLE001 - an invalid polygon covers nothing
        return 0.0


def reading_for(truth: dict, building: dict, project: Optional[str] = None) -> dict:
    """The reading as the score matches it against ``truth`` (pure): ``truth.extract`` with the truth's levels left
    out and, for a sparse truth, the sparse fields (the outdoor spaces, the openings' attributes, the walls' heights).
    21 Nov 2026: the critic's known errors (``critic_checks.sparse_known``) matched the user's corrections on an extract
    without the sparse fields, so every outdoor space the user asked for read as missing (C0008, real09's left balcony,
    'does not hold' on the after reading that has it, while the score said it holds); both read the reading here."""
    return TR.extract(building, project=project, leave_out=truth.get("levels_left_out") or [], attrs=TR.is_sparse(truth))


def match_sparse(truth: dict, read: dict, building: Optional[dict] = None) -> dict:
    """A reading against a sparse truth (pure but for ``attrs_ok``'s main entrance): every entry satisfied or not,
    nothing else judged.

    - an entry's level is the reading level its anchor finds (``level_map``); an entry whose level the reading lacks is
      not satisfied (an absent one cannot be confirmed either);
    - an entry with a drawing-frame place takes its metre place from the reading's transform
      (``truth.place_from_frame``);
    - present: doors, windows, openings and stairs by the score's one-to-one matching within the kind's tolerance among
      the reading elements of the entry's class carrying its asserted attributes (``attrs_ok``); rooms and outdoor
      spaces by ``match_rooms`` among those of the entry's type; a wall when what stands on its line covers
      ``WALL_PRESENT_SHARE`` of its span;
    - absent: no element of the class at the place (the elements matched to a present entry excepted, as in
      ``match``); a room or outdoor space when no reading one covers ``ROOM_SWALLOW_SHARE`` of it and none matches it
      by label and centre; a wall when what stands on its line covers less than ``WALL_ABSENT_SHARE`` of the span,
      whatever its thickness;
    - an asserted level and a project-level assertion: as before (``check_assertion``).

    Returns ``{"entries": [{id, level, type, absent, records, satisfied, at}], "assertions": [...], <type>: {present,
    present_ok, absent, absent_ok}, "records": {record id: [satisfied, entries]}, "unsatisfied": [entry ids],
    "level_map": {truth level: reading level} (where they differ), "total"}``: the total is 100 x the weighted share of
    the satisfied entries (``WEIGHTS``; an outdoor space weighs as a room, an asserted level and a project-level
    assertion as ``levels``), None when the truth asserts nothing."""
    out_entries, assertions = [], []
    per_type = {t: {"present": 0, "present_ok": 0, "absent": 0, "absent_ok": 0} for t in TYPES + ("outdoor",)}
    r_levels = {lv["id"]: lv for lv in read.get("levels") or []}
    rper = read.get("per_level") or {}
    lmap = level_map(truth, read)

    def note(e, lid, t, ok, why=None):
        row = {"id": e.get("id"), "level": lid, "type": t, "absent": bool(e.get("absent")),
               "records": list(e.get("corrections") or []), "satisfied": bool(ok), "at": signature(t, e)}
        if why and not ok:
            row["why"] = why
        out_entries.append(row)
        k = "absent" if e.get("absent") else "present"
        per_type[t][k] += 1
        per_type[t][k + "_ok"] += int(bool(ok))

    for lid, lv in (truth.get("per_level") or {}).items():
        rid = lmap.get(lid, lid if lid in r_levels else None)
        have = rid is not None and rid in r_levels
        rl = rper.get(rid) or {} if have else {}
        ceiling = (r_levels.get(rid) or {}).get("ceiling_height") if have else None
        for t in TR.ELEMENT_TYPES + TR.SPARSE_KINDS:
            ents = []
            for e in lv.get(t) or []:
                mapped, why = TR.place_from_frame(e, building, rid)
                ents.append(mapped)
            if not ents:
                continue
            if not have:
                for e in ents:
                    note(e, lid, t, False, f"the reading has no level {lv_label(truth, lid)}")
                continue
            pres, absn = TR.positives(ents), [e for e in ents if e.get("absent")]
            rr = rl.get(t) or []
            if t == "walls":
                stand = standing_walls(rl, ceiling)
                pieces = [p for _r, p in stand]
                for e in pres:
                    c = wall_cover(e, pieces)
                    note(e, lid, t, c >= WALL_PRESENT_SHARE, f"what stands covers {c:.2f} of the span")
                for e in absn:
                    solid = [p for p in pieces if _dist(p["start"], p["end"])
                             >= max(TR.WALL_PIECE_MIN_M, float(p.get("thickness") or 0))]   # joints left out
                    c = wall_cover(dict(e, thickness=None), solid)
                    note(e, lid, t, c < WALL_ABSENT_SHARE, f"a wall stands over {c:.2f} of the span")
                continue
            used: set = set()
            if t in ("rooms",) + TR.SPARSE_KINDS:
                type_key = "room_type" if t == "rooms" else "outdoor_kind"
                groups: dict = {}
                for i, e in enumerate(pres):
                    groups.setdefault(_norm(e.get(type_key) or ""), []).append(i)
                ok_idx = set()
                for ty, idx in sorted(groups.items()):
                    cand = [j for j, r in enumerate(rr) if not ty or _norm(r.get(type_key) or "") == ty]
                    for i, j in match_rooms([pres[i] for i in idx], [rr[j] for j in cand]):
                        ok_idx.add(idx[i])
                        used.add(cand[j])
                for i, e in enumerate(pres):
                    note(e, lid, t, i in ok_idx, f"no {t[:-1] if t == 'rooms' else 'outdoor space'} of its type at its "
                                                 f"place" if e.get(type_key) else "nothing at its place")
                left = [r for j, r in enumerate(rr) if j not in used]
                for e in absn:
                    share = _covered_share(e.get("polygon") or [], [r.get("polygon") for r in rr])
                    hit = match_rooms([e], left)
                    note(e, lid, t, share < ROOM_SWALLOW_SHARE and not hit,
                         f"a reading {t[:-1]} covers {share:.2f} of it" if share >= ROOM_SWALLOW_SHARE else
                         f"read: {left[hit[0][1]].get('id')}" if hit else None)
                continue
            tol = STAIR_CENTER_M if t == "stairs" else OPENING_CENTER_M
            groups = {}
            for i, e in enumerate(pres):
                groups.setdefault(json.dumps(e.get("attrs") or {}, sort_keys=True), []).append(i)
            ok_idx = set()
            for key, idx in sorted(groups.items()):
                a = json.loads(key)
                cand = [j for j, r in enumerate(rr) if j not in used and attrs_ok(a, r, building)]
                for i, j in match_points([pres[i] for i in idx], [rr[j] for j in cand], tol):
                    ok_idx.add(idx[i])
                    used.add(cand[j])
            for i, e in enumerate(pres):
                note(e, lid, t, i in ok_idx, f"no {TR.TYPE_KIND[t]} within {tol} m" + (
                    f" with {', '.join(sorted(e['attrs']))}" if e.get("attrs") else ""))
            left = [r for j, r in enumerate(rr) if j not in used]
            for e in absn:
                hit = next((r for r in left if r.get("center") and e.get("center")
                            and _dist(r["center"], e["center"]) <= tol), None)
                note(e, lid, t, hit is None, f"read: {hit.get('id')}" if hit else None)
    for lv in truth.get("levels") or []:
        if not lv.get("asserted"):
            continue
        r = r_levels.get(lmap.get(lv["id"]) or "")
        ok = r is not None
        if ok and lv.get("elevation") is not None:
            ok = isinstance(r.get("elevation"), (int, float)) and \
                abs(float(r["elevation"]) - float(lv["elevation"])) <= TR.ASSERT_TOL_M + 1e-9
        note({"id": f"level_{lv['id']}", "corrections": lv.get("corrections")}, lv["id"], "levels", ok,
             "the reading's level differs" if r is not None else f"the reading has no level {lv['id']}")
    for a in truth.get("project_assertions") or []:
        ok, has = check_assertion(a, read, building)
        assertions.append({"id": a["id"], "what": a["what"], "records": list(a.get("corrections") or []),
                           "satisfied": bool(ok), "read": has, "at": [a["what"], a.get("level")]})
        per_type["levels"]["present"] += 1
        per_type["levels"]["present_ok"] += int(bool(ok))
    num = den = 0.0
    records: dict = {}
    for row in out_entries + assertions:
        w = WEIGHTS.get(row.get("type") or "levels", WEIGHTS["rooms"])
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
           "level_map": {k: v for k, v in lmap.items() if v != k},
           "total": round(100.0 * num / den, 2) if den else None}
    out.update(per_type)
    if not per_type["outdoor"]["present"] and not per_type["outdoor"]["absent"]:
        out.pop("outdoor")
    return out


def lv_label(truth: dict, lid: str) -> str:
    lv = next((x for x in truth.get("levels") or [] if x["id"] == lid), {})
    return f"{lid} ({lv['label']})" if lv.get("label") else lid


def satisfied_ids(result: dict) -> dict:
    """``{entry or assertion id: (satisfied, records, signature)}`` of a stored sparse result (pure)."""
    return {x["id"]: (bool(x.get("satisfied")), list(x.get("records") or []), x.get("at"))
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
                projects[p] = dict(v, commit=entry.get("commit"), truth_kind=entry.get("truth_kind"),
                                   **({"stored_on": entry["date"]} if entry.get("date") else {}))
    return {"projects": projects, "overall": overall(projects), "overall_synthetic": synthetic_overall(projects),
            "truth_kind": truth_kind} if projects else None


def _lost(was: dict, now: dict) -> list[str]:
    """The record ids of a sparse project whose entries were satisfied in ``was`` and are not in ``now`` (pure), each
    with those entries: ``["C0034 (u_C0034_2, u_C0034_5)", ...]``. An entry is the same entry only by its id AND what
    it asserts (``signature``): an id that names another place, polarity or attribute in ``now`` (a record re-placed or
    its operations re-ordered), or an id ``now`` no longer has, is not compared here (``changed`` reports it, and the
    gate's re-score against the stored truth catches a loss behind it)."""
    return _fmt_lost(_lost_by_record(was, now))


def _lost_by_record(was: dict, now: dict) -> dict:
    """``_lost`` as ``{record id: [entry ids]}`` (pure)."""
    before, after = satisfied_ids(was), satisfied_ids(now)
    by_record: dict = {}
    for eid, (ok, recs, sig) in before.items():
        if not ok or eid not in after:
            continue
        ok2, recs2, sig2 = after[eid]
        if sig is not None and sig2 is not None and sig != sig2:
            continue
        if not ok2:
            for rid in sorted(set(recs) | set(recs2), key=TR._record_key):
                by_record.setdefault(rid, []).append(eid)
    return by_record


def _fmt_lost(by_record: dict) -> list[str]:
    return [f"{rid} ({', '.join(sorted(ids))})" for rid, ids in sorted(by_record.items(),
                                                                       key=lambda kv: TR._record_key(kv[0]))]


def _op_number(eid: str, rid: str) -> Optional[int]:
    """The operation number of a record's entry id ``u_<record>_<n>`` (``truth.USER_ID_PREFIX``), None for another id."""
    head = f"{TR.USER_ID_PREFIX}{rid}_"
    tail = str(eid)[len(head):] if str(eid).startswith(head) else ""
    return int(tail) if tail.isdigit() else None


def moved_with_ok(p: str, by_record: dict, was: dict, now: dict, moved: Optional[dict]) -> dict:
    """21 Nov 2026 (C0001: the user let the machine-located walls move onto the drawn facade line, "Yes, use the right
    one"): the lost entries the gate does not count as a fall because the user's OK moved them (pure): ``{record id:
    (entry ids, the move)}``. A record's lost entries are excused only when every one is an operation that a move
    logged by ``truth move`` (``truth.moves_by_project``: the user's words of the OK in the record's history) took away
    on or after the day the stored numbers were made, AND every entry of the record holds on the new reading at its new
    place (``now["records"]``: all satisfied). An entry that also names another record stays a fall for that record."""
    out: dict = {}
    mine = (moved or {}).get(p) or {}
    since = str(was.get("stored_on") or "")
    for rid, ids in by_record.items():
        mv = [m for m in mine.get(rid) or [] if str(m.get("date") or "") >= since]
        if not mv:
            continue
        nums = {n for m in mv for n in m.get("old_numbers") or []}
        held = (now.get("records") or {}).get(rid)
        if not held or int(held[1]) <= 0 or int(held[0]) != int(held[1]):
            continue
        if all(_op_number(eid, rid) in nums for eid in ids):
            out[rid] = (sorted(ids), mv[-1])
    return out


def changed(last: Optional[dict], new: dict) -> list[str]:
    """Information, never a fall (pure): the satisfied entries of the stored numbers that the current truth no longer
    holds, or holds as another assertion (a record re-placed, re-ordered or made inapplicable), and that still hold
    against the stored truth (``vs_stored_truth``) or could not be checked against it."""
    if not last or last.get("truth_kind") != new.get("truth_kind"):
        return []
    out = []
    for p, now in sorted((new.get("projects") or {}).items()):
        was = (last.get("projects") or {}).get(p) or {}
        if not was.get("sparse") or not now.get("sparse"):
            continue
        before, after = satisfied_ids(was), satisfied_ids(now)
        held = satisfied_ids(now["vs_stored_truth"]) if now.get("vs_stored_truth") else {}
        ids = []
        for eid, (ok, _recs, sig) in sorted(before.items()):
            if not ok:
                continue
            gone = eid not in after or (sig is not None and after[eid][2] is not None and after[eid][2] != sig)
            if gone and (not held or held.get(eid, (True,))[0]):
                ids.append(eid)
        if ids:
            out.append(f"{p}: the truth changed at {', '.join(ids)} (still held against the stored truth)")
    return out


def falls(last: Optional[dict], new: dict, full: bool = False, withdrawn=(), moved: Optional[dict] = None,
          notes: Optional[list] = None) -> list[str]:
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
    left). ``moved`` (``truth.moves_by_project``): the records whose geometry the user's OK moved since the stored
    numbers; their old places' losses go to ``notes`` instead (``moved_with_ok``: only while the whole record holds at
    its new place)."""
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
            # the stored truth re-scored on the new reading (main: ``vs_stored_truth``) keeps every entry's identity:
            # a correction that held there and fails now is a fall, whatever the truth's edits since; the current
            # truth adds the entries both truths assert alike
            vs = _lost_by_record(was_all[p], now_all[p]["vs_stored_truth"]) if now_all[p].get("vs_stored_truth") \
                else {}
            cur = _lost_by_record(was_all[p], now_all[p])
            # 21 Nov 2026: a record whose geometry the user's OK moved (``truth move``) is judged at its new place: its
            # old place's loss is a note, not a fall, only while the whole record holds there (``moved_with_ok``)
            ok = moved_with_ok(p, {r: sorted(set(vs.get(r, [])) | set(cur.get(r, []))) for r in set(vs) | set(cur)},
                               was_all[p], now_all[p], moved)
            for rid, (ids, mv) in sorted(ok.items(), key=lambda kv: TR._record_key(kv[0])):
                held = (now_all[p].get("records") or {}).get(rid) or [0, 0]
                if notes is not None:
                    notes.append(f"{p}: {rid} moved with the user's OK on {mv['date']} (\"{mv['user_words']}\"): its "
                                 f"old place no longer holds ({', '.join(ids)}), every entry at its new place holds "
                                 f"({held[0]}/{held[1]})")
            lost = _fmt_lost({r: v for r, v in vs.items() if r not in ok})
            lost += [x for x in _fmt_lost({r: v for r, v in cur.items() if r not in ok}) if x not in lost]
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


def truth_sha(project: str, truth_dir: Path = TR.TRUTH_DIR) -> Optional[str]:
    """The sha256 of a project's truth file as scored (stored with a sparse result: which truth the numbers are of)."""
    import hashlib
    path = Path(truth_dir) / f"{project}.json"
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def stored_truth(project: str, commit: Optional[str], sha: Optional[str] = None, repo: Path = REPO) -> Optional[dict]:
    """The project's truth file as it was at a stored entry's commit (``git show <commit>:results/reading_truth/
    <p>.json``), None when git or the file is not there, or when it is not the truth the stored numbers were made
    of (``sha``: the stored truth_sha, when the entry has one)."""
    import hashlib
    import subprocess
    if not commit:
        return None
    try:
        res = subprocess.run(["git", "show", f"{commit}:results/reading_truth/{project}.json"], cwd=str(repo),
                             capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    if sha and hashlib.sha256(res.stdout).hexdigest() != sha:
        return None
    try:
        return json.loads(res.stdout.decode("utf-8"))
    except ValueError:
        return None


def score_project(project: str, work: Path, *, fresh: bool = False, truth_dir: Path = TR.TRUTH_DIR,
                  old_truth: Optional[dict] = None) -> dict:
    """Read one project (or use its reading in ``work``), match it against its truth, write the reading folder's
    ``reading_check/score.json`` and return the numbers with the truth's and the reading's provenance. A sparse truth
    is matched on the reading with the sparse fields (``truth.extract(attrs=True)``); ``old_truth`` (the truth at the
    stored entry's commit, for the gate) is matched on the same reading too (``vs_stored_truth``)."""
    truth = TR.load_truth(project, truth_dir)
    if truth is None:
        raise FileNotFoundError(f"no truth file for {project} in {truth_dir}")
    sparse = TR.is_sparse(truth)
    if sparse and not TR.entry_count(truth) and not (old_truth and TR.entry_count(old_truth)):
        return {"total": None, "measurable": False, "sparse": True, "truth_status": truth.get("status"),
                "truth_source": truth.get("source"), "truth_commit": None, "truth_sha": truth_sha(project, truth_dir),
                "not_measurable": [x.get("record") for x in truth.get("not_measurable") or []]}
    folder = TR.reading(project, work, fresh)
    b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
    read = reading_for(truth, b, project)
    res = match(truth, read, b)
    if sparse:
        res["sparse"] = True
        res["truth_sha"] = truth_sha(project, truth_dir)
        if old_truth is not None and TR.is_sparse(old_truth):
            old = match_sparse(old_truth, read, b)
            res["vs_stored_truth"] = {"entries": old["entries"], "assertions": old["assertions"]}
    res.update(truth_status=truth.get("status"), truth_source=truth.get("source"), truth_commit=truth.get("commit"),
               read_commit=TR.read_commit(folder))
    rc = folder / "reading_check"
    rc.mkdir(parents=True, exist_ok=True)
    (rc / "score.json").write_text(json.dumps(dict({"project": project}, **res), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
    return res


def left_the_truth(project: str, records: list) -> Optional[str]:
    """Why a stored project may go unscored in a full run, None when it may not (it falls as not scored): only a
    project with no truth file, no synthetic truth and no applicable correction record has left the truth (review
    G2: every real baseline carries ``acceptance_withdrawn`` since 6 Nov 2026, so that alone excuses nothing)."""
    if TR.load_truth(project) is not None or TR.synthetic_truth_file(project) is not None \
            or project in TR.sparse_projects(records):
        return None
    why = (TR.load_baseline(project) or {}).get("acceptance_withdrawn")
    if why:
        return (f"no applicable correction record of the user is left (and the user's acceptance was withdrawn on "
                f"{why.get('on') or '?'})")
    return "no applicable correction record of the user is left"


def main(args) -> int:
    import tempfile
    named = [p.strip() for p in (args.projects or "").split(",") if p.strip()]
    projects = named or TR.truth_projects()
    if not projects:
        print("reading score: no truth file in results/reading_truth/ (run `truth build` first) and no --projects")
        return 2
    gate = bool(args.gate or args.update)          # review G7: an entry is stored only after the gate held
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_score_"))
    stored = load_scores()
    last = latest(stored, TRUTH_KIND)
    entry = {"commit": TR.git_head(), "date": _dt.date.today().isoformat(), "truth_kind": TRUTH_KIND,
             "projects": {}, "overall": 0.0}
    for p in projects:
        was = ((last or {}).get("projects") or {}).get(p) or {}
        old = stored_truth(p, was.get("commit"), was.get("truth_sha")) if gate and was.get("sparse") else None
        if gate and was.get("sparse") and old is None:
            print(f"{p}: the truth of the stored entry ({(was.get('commit') or '?')[:12]}) could not be loaded: "
                  f"compared with the current truth by entry and assertion only")
        try:
            entry["projects"][p] = score_project(p, work, fresh=bool(getattr(args, "fresh", False)), old_truth=old)
        except Exception as exc:                                  # one failed reading must not hide the others
            print(f"{p}: not scored: {exc}")
            entry["projects"][p] = {"total": 0.0, "error": str(exc)}
    entry["overall"] = overall(entry["projects"])
    entry["overall_synthetic"] = synthetic_overall(entry["projects"])
    print(table(entry))
    for p, v in sorted(entry["projects"].items()):
        if v.get("sparse") and v.get("unsatisfied"):
            print(f"{p}: not satisfied: " + ", ".join(v["unsatisfied"]))
        if v.get("level_map"):
            print(f"{p}: levels found by their anchor: " + ", ".join(f"{a} -> {b}" for a, b in v["level_map"].items()))
    errors = sorted(p for p, v in entry["projects"].items() if v.get("error"))
    if last is None and any(e.get("truth_kind") != TRUTH_KIND for e in stored):
        print(f"gate: no stored entry of truth kind {TRUTH_KIND} yet (the older entries were made against another "
              f"truth and are never compared)")
    records = TR.load_corrections()
    withdrawn = []
    for p in (last or {}).get("projects", {}):
        if p in entry["projects"]:
            continue
        why = left_the_truth(p, records)
        if why:
            print(f"{p}: left the truth ({why})")
            withdrawn.append(p)
    moved_notes: list = []
    fell = falls(last, entry, full=not named, withdrawn=withdrawn, moved=TR.moves_by_project(records),
                 notes=moved_notes) if gate else []
    for line in (changed(last, entry) + moved_notes) if gate else []:
        print(f"note: {line}")
    for v in entry["projects"].values():
        v.pop("vs_stored_truth", None)                           # a gate's working number, never stored
    if gate:
        against = sorted({(v.get("commit") or "?")[:12] for p, v in (last or {}).get("projects", {}).items()
                          if p in entry["projects"]})
        print(("GATE: fell" if fell else "GATE: holds") + " against " + (", ".join(against) or "nothing stored")
              + ("\n  " + "\n  ".join(fell) if fell else ""))
    if args.update:
        if errors:
            print(f"scores: not stored, the reading of {', '.join(errors)} failed (an entry with an error is never "
                  f"a baseline)")
        elif fell:
            print("scores: not stored, the gate fell")
        else:
            print(f"scores: entry {len(stored) + 1} written to {save_scores(stored + [entry]).relative_to(REPO)}")
    return 1 if fell or errors else 0
