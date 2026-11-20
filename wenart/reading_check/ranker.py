"""The ranker of the reader's decisions (5 Nov 2026, Milestone 14 track R3; user: "I want structure recognition to be
cumulatively better with the feedbacks I am giving").

What: a small model per decision kind (``gap_kind``: door | window | opening | closed | open; ``wall_or_notation``:
wall | notation) that scores the code-built candidates of a decision from the features the rules looked at
(``wenart.ingest.generic.decisions``). Four steps (docs/milestone14.md R3):

1. **instrument**: the reader writes one record per decision (``reading_check/decisions_<level>.json``).
2. **label** (``label``): a pure join of the records with the truth (``results/reading_truth/<p>.json``): the nearest
   truth opening within ``PLACE_TOL_M`` and ``WIDTH_TOL_M`` gives a gap its class; a truth wall covering the place makes
   it ``closed``; nothing in the truth makes it ``open`` (open air, or two walls); a truth wall covering a pair's
   centre line within ``WALL_LATERAL_M`` makes it a ``wall``, else ``notation``; an ``absent`` truth entry is a negative
   of its class. The label's weight follows its source (``LABEL_WEIGHTS``): a user correction 10, a synthetic truth 3,
   an accepted reading 1, because the accepted readings are the reader's own answers (training on them alone teaches
   the ranker to copy the rules); the corrections are where the rules were wrong and the synthetic cases are exact.
3. **learn** (``train``): one-vs-rest logistic regression in numpy (no new dependency): features standardised, L2 on
   the coefficients (``L2``), Newton's method (IRLS) with a fixed number of iterations (``NEWTON_ITERATIONS``), no
   randomness anywhere: the committed model is reproduced from the committed table bit for bit (the test does it).
   Leave-one-project-out evaluation (``lopo``): per project the rules' accuracy, the ranker's and the integrated one
   (the ranker under its gates), and the same on the user-correction labels alone. Stored as JSON in
   ``wenart/reading_check/models/<kind>.json`` with the features, the standardisation, the classes, the coefficients,
   what it was trained on (commit, projects, counts per source) and the metrics; ``explain`` prints which features
   carry which class (the largest standardised coefficients): a feature that no longer matters is a rule that can go.
4. **integrate** (``decide``): after the rule cascade the ranker answers only when the rule's confidence is under
   ``RULE_TRUST`` and its own margin (the top score minus the second) is at least ``MARGIN_MIN``; otherwise the rule's
   answer stands. Hard constraints stay rules and are never overridden (``allowed_answers``: a gap with a swing arc is
   a door; a gap wider than its wall run is never a door; an end gap makes no element; closed and open are never the
   ranker's answers because they make or remove a wall; a pair on a dimension or axis layer, in a dimension chain or
   an axis grid is never a wall). A missing model file means the rules alone, never an error. The models are loaded
   once per process. The gap ranker re-types an opening element in ``openings.classify_gap``; the wall ranker only
   advises (``ranker_advice`` on the pair's record, counted in the level's summary): moving a pair into or out of the
   wall network is geometry the network rules build (joins, columns, the mask), so v1 measures what it would say and
   applies nothing there.

``python -m wenart.reading_check ranker retrain|train|evaluate|explain|label --work DIR [--projects a,b] [--kind k]``
(also ``python -m wenart.reading_check.ranker``): ``retrain`` is the whole retrain in one command (every project with a
truth file read with the rules alone into ``DIR`` unless its reading is there, ``--fresh`` to read again, then
``train``); ``train`` labels the readings in ``DIR`` (one folder per project, as ``score --work`` leaves them), fits
both models, writes them with their tables and prints the leave-one-project-out table, the held-out changes, the
transition trust and the explanation; ``evaluate`` (or ``eval``) prints the same without writing; ``explain`` prints
the stored models' top features; ``label`` prints the label counts per kind and source.

Why: a correction used to become one hand-written rule and nothing measured whether it helped the other projects.
The ranker makes the corrections compound: every accept, reject or remark of the user is a labelled example, the
model is retrained in seconds on CPU, the regression set is re-scored, and the gate (``score --gate``) decides.

How: pure functions over lists of dicts and numpy arrays; the model file is plain JSON; the integration is one call in
``openings.gaps_and_openings``. The join's opening tolerances are R3's own (docs/milestone14.md R3 step 2: 0.5 m and
0.3 m of width), not the score's 0.30 m centre rule: a gap's place is the middle of the drawn gap, and the element a
later pass builds for it can stand off that middle (a tagged window moves up to 0.35 m to clear a column); the width
check keeps a wide gap from taking a narrow element beside it. A truth element without a width (a user negation that
names only its place) joins by the score's own rule, the centre within ``score.OPENING_CENTER_M``. The wall join uses
the score's numbers (0.15 m lateral, half the length overlapping).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import sys
from pathlib import Path
from typing import Optional

# 6 Nov 2026: one BLAS thread when this module brings numpy in (the command line). On the shared 4-core machine a
# threaded BLAS made one 1,562-row fit take 9.2 s instead of 0.13 s, and the leave-one-group-out runs (hundreds of small
# fits) did not finish in 50 minutes; one thread is also the deterministic choice. A value the user set is kept.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
MODELS_DIR = REPO / "wenart" / "reading_check" / "models"
KIND_GAP = "gap_kind"
KIND_WALL = "wall_or_notation"
CLASSES = {KIND_GAP: ("door", "window", "opening", "closed", "open"), KIND_WALL: ("wall", "notation")}
RANKER_ANSWERS = {KIND_GAP: ("door", "window", "opening"), KIND_WALL: ("wall", "notation")}
DECIDED_RULE = "rule"
DECIDED_RANKER = "ranker"
RULE_TRUST = 0.6                 # a rule at or above this confidence is trusted; the ranker answers below it only
MARGIN_MIN = 0.3                 # the ranker's top score must lead the second by this much to decide
# 5 Nov 2026 (measured on the first model): with RULE_TRUST and MARGIN_MIN alone the committed gap model changed 21
# decisions on accepted real projects (real06, real07, real10, real15, real17; real10's repeated on its six typical
# floors) and held out it was right on 2 of 8 changes there. A change is made only for a transition (the weak rule ->
# the ranker's answer, ``transition_key``) whose held-out changes on the leave-one-project-out run were right often
# enough (``transition_trust``); the trusted transitions are stored with the model and re-measured on every retrain.
TRANSITION_MIN = 3               # at least this many held-out changes of a transition ...
TRANSITION_PRECISION = 0.6       # ... and at least this share of them right
TRUST_NOTE = ("The integration (ranker.decide) applies a ranker change only when the rule's confidence is under "
              "rule_trust, the ranker's margin is at least margin_min, the answer is allowed by the hard constraints "
              "(a swing arc is a door, a gap wider than its run is never a door, an end gap makes no element, closed "
              "and open are never the ranker's) and its transition (the weak rule -> the ranker's answer) is trusted in "
              "'transitions': right on at least transition_precision of at least transition_min held-out changes of "
              "the leave-one-project-out run. Why (5 Nov 2026, the first model, before the trust check): the gates "
              "alone changed 26 decisions on the 28 readings, 21 of them on accepted real projects, and held out the "
              "ranker was right on 2 of its 8 changes on real projects; on real10 L0-L6 its window at the 1.50 m "
              "bedroom window gaps (the type is right: C0032) came before the later furniture rule that types the same "
              "window, which then left an extra opening beside it on seven floors. "
              "With the trust check: 5 changes (synthetic-12's four bare door gaps, one real07 gap). On the merged "
              "reader with the derived truth (6 Nov 2026) the margin is taken against every class (top_and_margin: "
              "real10's doorless mirror-axis gap had door 0.43, closed 0.29) and no transition is trusted, so the "
              "model changes no decision; it records its scores, its untrusted answers and the undecided places. The "
              "wall_or_notation model only advises (ranker_advice on the pair's record): held out it beats the rules "
              "by 0.004 and its integrated changes were right on 123 of 277; moving a pair into or out of the wall "
              "network is geometry.")
LABEL_WEIGHTS = {"user_correction": 10.0, "synthetic": 3.0, "accepted_reading": 1.0,   # docs/milestone14.md R3 (3)
                 "user_corrections": 10.0}      # 6 Nov 2026: the sparse truth's file-level source (the user's records)
PLACE_TOL_M = 0.5                # a truth opening this close to a gap's place ...
WIDTH_TOL_M = 0.3                # ... and this close in width labels the gap
WALL_LATERAL_M = 0.15            # a truth wall covers a place or a pair within this of its centre line
WALL_END_M = 0.05                # ... inside its extent grown by this
OVERLAP_SHARE = 0.5              # a truth wall covers a pair when they overlap this share of the pair's length
L2 = 10.0                        # ridge on the standardised coefficients (the intercept is free); 5 Nov 2026: ridge 1,
                                 # 3 and 10 gave the same leave-one-project-out accuracy, 10 the fewest wrong changes
                                 # (gap_kind held out: 23 changes 5 right at 1, 13 / 5 at 3, 12 / 5 at 10)
NEWTON_ITERATIONS = 25           # Newton steps; the weighted logistic loss with a ridge is convex and converges well before
NO_POSITIVES_INTERCEPT = -10.0   # a class without a positive example scores about 0 everywhere
ROUND = 10                       # the stored numbers' decimals (enough for bit-for-bit reproduction after rounding)
# 6 Nov 2026 (review): projects that draw one building are one hold-out group in the leave-one-group-out run, or holding
# one out still trains on its near copy. real02 (one_building.dwg) and real04 (deneme1.dwg) are two DWGs of one house
# (projects/real04/brief.yaml: "the real02 twin villa on its plot"; their truths have the same walls, doors and
# openings on L-1, L-1b, L0 and L1, and 37 of real04's 43 gap rows equal a real02 row). The synthetic projects share a
# base house but each draws its own failure class; they stay apart.
PROJECT_GROUPS: tuple = (("real02", "real04"),)
OTHER_ADAPTER = ("synthetic-01", "synthetic-02", "synthetic-03", "synthetic-04", "synthetic-05")
                                 # read by the synthetic adapter, not the generic core: no decision records (retrain
                                 # keeps their reading for the score and does not read them again for want of records)
TABLE_MAX_ROWS = 6000            # the committed table keeps every synthetic and user-correction row and thins the
                                 # accepted-reading rows to this total with a fixed stride (the files stay small)
_MODELS: dict[str, Optional[dict]] = {}


# --- labels (step 2) -------------------------------------------------------------------------------------------------

def _dist(a, b) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def _wall_covers_point(w: dict, p) -> bool:
    (x0, y0), (x1, y1) = w["start"], w["end"]
    dx, dy = float(x1) - float(x0), float(y1) - float(y0)
    n = math.hypot(dx, dy)
    if n < 1e-9:
        return False
    ux, uy = dx / n, dy / n
    px, py = float(p[0]) - float(x0), float(p[1]) - float(y0)
    along, lateral = px * ux + py * uy, abs(px * uy - py * ux)
    t = float(w.get("thickness") or 0.0)
    return -WALL_END_M <= along <= n + WALL_END_M and lateral <= max(WALL_LATERAL_M, t / 2.0)


def _wall_covers_segment(w: dict, a, b) -> bool:
    (x0, y0), (x1, y1) = w["start"], w["end"]
    dx, dy = float(x1) - float(x0), float(y1) - float(y0)
    n = math.hypot(dx, dy)
    la = _dist(a, b)
    if n < 1e-9 or la < 1e-9:
        return False
    ux, uy = dx / n, dy / n
    t = float(w.get("thickness") or 0.0)
    alongs = []
    for p in (a, b):
        px, py = float(p[0]) - float(x0), float(p[1]) - float(y0)
        if abs(px * uy - py * ux) > max(WALL_LATERAL_M, t / 2.0):
            return False
        alongs.append(px * ux + py * uy)
    return min(n, max(alongs)) - max(0.0, min(alongs)) >= OVERLAP_SHARE * la


def _nearest_opening(place, width: float, level_truth: dict) -> Optional[tuple]:
    """``(element, kind, distance)`` of the nearest truth opening within the tolerances (absent entries included: the
    caller reads ``absent``), else None. An element without a width joins by its centre within the score's
    ``OPENING_CENTER_M`` (6 Nov 2026, review: real04's two width-less user negations were dropped)."""
    from wenart.reading_check import score as SC

    best = None
    for key, kind in (("doors", "door"), ("windows", "window"), ("openings", "opening")):
        for e in level_truth.get(key) or []:
            if not e.get("center"):
                continue
            d = _dist(e["center"], place)
            if e.get("width") is None:
                ok = d <= SC.OPENING_CENTER_M
            else:
                ok = d <= PLACE_TOL_M and abs(float(e["width"]) - width) <= WIDTH_TOL_M
            if ok and (best is None or d < best[2]):
                best = (e, kind, d)
    return best


def _truth_walls(level_truth: dict) -> list[tuple]:
    """``[(box, wall)]`` of a level's truth walls with their boxes grown by the matching tolerance (one pass per level;
    the per-record loops skip the walls whose box misses the place)."""
    out = []
    for w in level_truth.get("walls") or []:
        if not (w.get("start") and w.get("end")):
            continue
        (x0, y0), (x1, y1) = w["start"], w["end"]
        g = max(WALL_LATERAL_M, float(w.get("thickness") or 0.0) / 2.0) + WALL_END_M
        out.append(((min(x0, x1) - g, min(y0, y1) - g, max(x0, x1) + g, max(y0, y1) + g), w))
    return out


def _in_box(box, p) -> bool:
    return box[0] <= float(p[0]) <= box[2] and box[1] <= float(p[1]) <= box[3]


def label_gap(rec: dict, level_truth: dict, truth_source: str, walls: Optional[list] = None,
              sparse: bool = False) -> Optional[dict]:
    """The label of a ``gap_kind`` record from one level's truth (pure): ``{"label", "weight", "source"}``; a negated
    truth element gives ``{"negative_of": class, ...}`` (a negated wall across the gap: ``negative_of closed``); None
    for a record without a place. ``walls`` is ``_truth_walls(level_truth)`` when the caller has it already.

    ``sparse`` (6 Nov 2026, the user: "Only consider my revision with the screenshot I have given into previous
    projects others I have not seen"): a real project's truth holds only what the user's records assert at their
    places, so a gap no entry covers gets no label (nothing in such a truth means "not seen", never "open air")."""
    place = rec.get("place")
    if not place:
        return None
    width = float(rec["features"].get("width") or 0.0)
    hit = _nearest_opening(place, width, level_truth)
    if hit is not None:
        e, kind, _d = hit
        src = e.get("source") or truth_source
        out = {"weight": LABEL_WEIGHTS.get(src, 1.0), "source": src, "element": e.get("id")}
        if e.get("absent"):
            out["negative_of"] = kind
        else:
            out["label"] = kind
        return out
    walls = _truth_walls(level_truth) if walls is None else walls
    covered = next((w for box, w in walls if not w.get("absent") and _in_box(box, place)
                    and _wall_covers_point(w, place)), None)
    if covered is not None:
        src = covered.get("source") or truth_source
        return {"label": "closed", "weight": LABEL_WEIGHTS.get(src, 1.0), "source": src, "element": covered.get("id")}
    negated = next((w for box, w in walls if w.get("absent") and _in_box(box, place)
                    and _wall_covers_point(w, place)), None)
    if negated is not None:
        src = negated.get("source") or truth_source
        return {"negative_of": "closed", "weight": LABEL_WEIGHTS.get(src, 1.0), "source": src,
                "element": negated.get("id")}
    if sparse:
        return None
    return {"label": "open", "weight": LABEL_WEIGHTS.get(truth_source, 1.0), "source": truth_source, "element": None}


def label_wall(rec: dict, level_truth: dict, truth_source: str, walls: Optional[list] = None,
               sparse: bool = False) -> Optional[dict]:
    """The label of a ``wall_or_notation`` record (pure): ``wall`` when a truth wall covers the pair's centre line,
    else ``notation``; a negated truth wall covering it is a negative of ``wall``. In a ``sparse`` truth a pair no
    entry covers gets no label (see ``label_gap``)."""
    line = rec.get("line")
    if not line:
        return None
    a, b = line
    walls = _truth_walls(level_truth) if walls is None else walls
    for box, w in walls:
        if _in_box(box, a) and _in_box(box, b) and _wall_covers_segment(w, a, b):
            src = w.get("source") or truth_source
            out = {"weight": LABEL_WEIGHTS.get(src, 1.0), "source": src, "element": w.get("id")}
            if w.get("absent"):
                out["negative_of"] = "wall"
            else:
                out["label"] = "wall"
            return out
    if sparse:
        return None
    return {"label": "notation", "weight": LABEL_WEIGHTS.get(truth_source, 1.0), "source": truth_source,
            "element": None}


def label(decisions: list[dict], truth: dict) -> list[dict]:
    """Every decision record joined with the truth (pure): the record with ``label`` (or ``negative_of``), ``weight``
    and ``source`` added; records on levels the truth does not know, or without a place, are left out. A ``partial``
    truth labels only its levels; a ``sparse`` truth (the user's records only) labels only the decisions an entry
    covers. The weight is the element's own ``source`` (``LABEL_WEIGHTS``), the truth's when the element has none."""
    per = truth.get("per_level") or {}
    src = truth.get("source") or "accepted_reading"
    sparse = bool(truth.get("sparse"))
    walls_of = {lid: _truth_walls(lv) for lid, lv in per.items()}
    out = []
    for rec in decisions:
        lv = per.get(rec.get("level_id"))
        if lv is None or rec.get("final_answer") == "dropped":     # a candidate the reader discarded is no decision
            continue
        lab = label_gap(rec, lv, src, walls_of[rec["level_id"]], sparse) if rec.get("kind") == KIND_GAP \
            else label_wall(rec, lv, src, walls_of[rec["level_id"]], sparse)
        if lab is None:
            continue
        out.append(dict(rec, **lab))
    return out


def label_counts(labelled: list[dict]) -> dict:
    """``{kind: {source: n}}`` and ``{kind: {label: n}}`` of labelled records (the report's table)."""
    out: dict = {}
    for r in labelled:
        k = out.setdefault(r["kind"], {"by_source": {}, "by_label": {}, "negatives": 0})
        k["by_source"][r["source"]] = k["by_source"].get(r["source"], 0) + 1
        if r.get("negative_of"):
            k["negatives"] += 1
        else:
            k["by_label"][r["label"]] = k["by_label"].get(r["label"], 0) + 1
    return out


# --- the table and the learner (step 3) -----------------------------------------------------------------------------

def feature_names(records: list[dict]) -> list[str]:
    """The sorted union of the feature keys (a fixed order makes the model reproducible)."""
    names: set = set()
    for r in records:
        names.update(r.get("features") or {})
    return sorted(names)


def design(records: list[dict], names: list[str]) -> np.ndarray:
    """The feature matrix (rows x names) of records; a missing feature is 0, a bool is 0/1."""
    X = np.zeros((len(records), len(names)), dtype=np.float64)
    for i, r in enumerate(records):
        f = r.get("features") or {}
        for j, name in enumerate(names):
            v = f.get(name)
            X[i, j] = 0.0 if v is None else float(v)
    return X


def thin(rows: list[dict], max_rows: int = TABLE_MAX_ROWS) -> list[dict]:
    """The rows of a table thinned to ``max_rows`` (pure, deterministic): every synthetic and user-correction row is
    kept; the accepted-reading rows, in their order, are taken with a fixed stride so every project keeps its share.
    Nothing is thinned under the cap."""
    if len(rows) <= max_rows:
        return list(rows)
    keep = [r for r in rows if r.get("source") != "accepted_reading"]
    rest = [r for r in rows if r.get("source") == "accepted_reading"]
    room = max(0, max_rows - len(keep))
    if room == 0 or not rest:
        return keep
    stride = len(rest) / room
    chosen = {id(r) for r in keep} | {id(rest[int(i * stride)]) for i in range(room)}
    return [r for r in rows if id(r) in chosen]


def table_of(labelled: list[dict], kind: str, max_rows: int = TABLE_MAX_ROWS) -> dict:
    """The committed training table of one kind (pure): the feature names, one row per labelled record (thinned to
    ``max_rows``, ``thin``), its label (or the class it negates), its weight, project and source."""
    rows = thin([r for r in labelled if r.get("kind") == kind], max_rows)
    names = feature_names(rows)
    X = design(rows, names)
    return {"kind": kind, "features": names, "rows": [[round(float(v), 6) for v in row] for row in X.tolist()],
            "labels": [r.get("label") for r in rows], "negative_of": [r.get("negative_of") for r in rows],
            "weights": [float(r.get("weight") or 1.0) for r in rows],
            "projects": [r.get("project") for r in rows], "sources": [r.get("source") for r in rows]}


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35.0, 35.0)))


def fit_binary(X: np.ndarray, y: np.ndarray, w: np.ndarray, l2: float = L2,
               iterations: int = NEWTON_ITERATIONS) -> tuple[np.ndarray, float]:
    """Weighted logistic regression with a ridge on the coefficients (not the intercept) by Newton's method, a fixed
    number of steps, deterministic (pure). ``X`` standardised (n x d), ``y`` in {0, 1}, ``w`` the sample weights.
    Returns ``(coef (d), intercept)``."""
    n, d = X.shape
    if n == 0 or not y.any():
        return np.zeros(d), NO_POSITIVES_INTERCEPT
    if y.all():
        return np.zeros(d), -NO_POSITIVES_INTERCEPT
    Xb = np.hstack([X, np.ones((n, 1))])
    beta = np.zeros(d + 1)
    ridge = np.diag(np.array([l2] * d + [0.0]))
    for _ in range(iterations):
        p = _sigmoid(Xb @ beta)
        grad = Xb.T @ (w * (p - y)) + ridge @ beta
        s = w * p * (1.0 - p)
        hess = (Xb * s[:, None]).T @ Xb + ridge
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(hess, grad, rcond=None)[0]
        beta = beta - step
    return beta[:d], float(beta[d])


def fit(table: dict, *, l2: float = L2, iterations: int = NEWTON_ITERATIONS) -> dict:
    """The one-vs-rest model of a committed table (pure, deterministic): standardisation from the table, one binary
    classifier per class (a record that negates a class is a 0 of that class only), the numbers rounded to
    ``ROUND`` decimals. ``trained_on`` and ``metrics`` are added by ``train``."""
    names = list(table["features"])
    X = np.array(table["rows"], dtype=np.float64).reshape(len(table["rows"]), len(names))
    labels = list(table["labels"])
    negs = list(table.get("negative_of") or [None] * len(labels))      # (6 Nov 2026, review: read labels first)
    weights = np.array(table["weights"], dtype=np.float64)
    return _fit_arrays(table["kind"], names, X, labels, negs, weights, l2=l2, iterations=iterations)


def _fit_arrays(kind: str, names: list, X: np.ndarray, labels: list, negs: list, weights: np.ndarray, *,
                l2: float = L2, iterations: int = NEWTON_ITERATIONS) -> dict:
    """``fit`` on arrays (the leave-one-group-out runs fit hundreds of models on row subsets of one design matrix)."""
    classes = list(CLASSES[kind])
    if len(X):
        mean = X.mean(axis=0)
        std = X.std(axis=0)
    else:
        mean, std = np.zeros(len(names)), np.ones(len(names))
    std = np.where(std < 1e-12, 1.0, std)
    Z = (X - mean) / std
    coef, intercept = [], []
    for c in classes:
        keep = np.array([lab is not None or neg == c for lab, neg in zip(labels, negs)], dtype=bool)
        y = np.array([1.0 if lab == c else 0.0 for lab in labels], dtype=np.float64)[keep]
        b, b0 = fit_binary(Z[keep], y, weights[keep], l2=l2, iterations=iterations)
        coef.append([round(float(v), ROUND) for v in b])
        intercept.append(round(b0, ROUND))
    return {"kind": kind, "features": names, "mean": [round(float(v), ROUND) for v in mean],
            "std": [round(float(v), ROUND) for v in std], "classes": classes, "coef": coef, "intercept": intercept,
            "l2": l2, "iterations": iterations}


def scores_of(model: dict, features: dict) -> dict:
    """The normalised class scores of a feature dict under a model (pure): the sigmoid of each one-vs-rest classifier,
    divided by their sum (so a margin is the gap between two shares)."""
    x = np.array([float(features.get(n) or 0.0) for n in model["features"]], dtype=np.float64)
    z = (x - np.array(model["mean"])) / np.array(model["std"])
    raw = _sigmoid(np.array(model["coef"], dtype=np.float64) @ z + np.array(model["intercept"], dtype=np.float64))
    total = float(raw.sum())
    shares = raw / total if total > 1e-12 else np.full(len(raw), 1.0 / len(raw))
    return {c: round(float(s), 4) for c, s in zip(model["classes"], shares)}


def allowed_answers(rec: dict) -> list[str]:
    """The answers the ranker may give for a record (the hard constraints of the module docstring; pure): the rule's
    answer is always among them. A list of one means the rule decides."""
    kind, f, rule = rec.get("kind"), rec.get("features") or {}, rec.get("rule_answer")
    if kind == KIND_GAP:
        if rec.get("gap") == "end" or (f.get("arcs_swing") or 0) > 0:
            return [rule]
        out = [a for a in RANKER_ANSWERS[KIND_GAP]
               if not (a == "door" and (f.get("run_length") or 0) > 0 and (f.get("width") or 0) > f["run_length"])]
    elif kind == KIND_WALL:
        if f.get("in_dimension_chain") or f.get("in_axis_grid") or f.get("role_dimension") or f.get("role_axis") \
                or f.get("role_text"):
            return [rule] if rule == "notation" else ["notation"]
        out = list(RANKER_ANSWERS[KIND_WALL])
    else:
        return [rule]
    if rule not in out:
        out.append(rule)
    return out


def decide(kind: str, features: dict, rule_answer: str, rule_confidence: float, allowed=None,
           model: Optional[dict] = None, rule: Optional[str] = None) -> tuple[str, str, float, dict]:
    """``(answer, decided_by, margin, scores)`` (step 4; pure given the model): the ranker's answer when the rule's
    confidence is under ``RULE_TRUST``, the ranker has a model, more than one answer is allowed, its margin (top share
    minus second among the allowed answers) is at least ``MARGIN_MIN`` and its answer differs from the rule's through a
    trusted transition (the model's ``transitions``, ``transition_trust``; a model without them, such as a fresh fit in
    the leave-one-project-out run, trusts every transition); else the rule's answer with ``decided_by: rule`` (a ranker
    that agrees with the rule decides nothing: the rule built the element). ``scores`` is empty without a model.

    Why the transition must be trusted (5 Nov 2026, decided with the coordinator): with ``RULE_TRUST`` and
    ``MARGIN_MIN`` alone the first committed gap model changed 26 decisions on the 28 readings, 21 of them on accepted
    real projects, and on held-out real projects it was right on 2 of its 8 changes; on real10 L0-L6 its window at the
    1.50 m bedroom window gaps (the type is right, the user's C0032) came before the later furniture rule that types the
    same window, which then left an extra opening beside it on seven floors. A
    change the ranker has not been shown to get right on other projects (at least ``TRANSITION_PRECISION`` of at least
    ``TRANSITION_MIN`` held-out changes) is recorded, never applied; with the check the same model changed 5 decisions.
    The model JSON says the same in its ``note`` (``TRUST_NOTE``)."""
    model = model if model is not None else load_model(kind)
    if model is None:
        return rule_answer, DECIDED_RULE, 0.0, {}
    scores = scores_of(model, features)
    allowed = list(allowed) if allowed else list(scores)
    top, margin = top_and_margin(scores, allowed)
    if rule_confidence < RULE_TRUST and len(allowed) > 1 and margin >= MARGIN_MIN and top != rule_answer:
        trust = model.get("transitions")
        if trust is None or (trust.get(transition_key(rule, top)) or {}).get("trusted"):
            return top, DECIDED_RANKER, margin, scores
    return rule_answer, DECIDED_RULE, margin, scores


def explore_choice(rec: dict, allowed, margin: float) -> Optional[tuple]:
    """20 Nov 2026 (``bandit``, user: "A bit RL for AI please it needs to teach itself"): an exploration run's other
    answer for a low-margin decision, or None. Only with ``WENART_RANKER_EXPLORE=seed:eps`` (never in a normal
    reading), only where the rule is weak (under ``RULE_TRUST``) and the ranker's margin under ``MARGIN_MIN``, only
    door or window (the answers that type a gap the drawing has; closed and open stay the rules'), with probability
    ``eps`` from a hash of the seed and the place (reproducible). Returns ``(answer, propensity)``."""
    import hashlib

    spec = os.environ.get("WENART_RANKER_EXPLORE")
    if not spec or rec.get("kind") != KIND_GAP or float(rec.get("rule_confidence") or 0) >= RULE_TRUST \
            or margin >= MARGIN_MIN:
        return None
    alts = [a for a in allowed if a in ("door", "window") and a != rec.get("rule_answer")]
    if not alts:
        return None
    seed, _, eps = spec.partition(":")
    eps_f = float(eps or 0.1)
    p = rec.get("place_page") or rec.get("place") or [0.0, 0.0]
    h = hashlib.sha256(f"{seed}|{rec.get('level_id')}|{round(float(p[0]), 2)}|{round(float(p[1]), 2)}".encode())
    u = int(h.hexdigest()[:12], 16) / float(16 ** 12)
    if u >= eps_f:
        return None
    return alts[int(u / eps_f * len(alts)) % len(alts)], round(eps_f / len(alts), 4)


def top_and_margin(scores: dict, allowed) -> tuple[str, float]:
    """The best allowed answer and its margin (pure): its share minus the best share of any OTHER class, allowed or
    not. 6 Nov 2026 (measured on the merged reader): the margin taken among the allowed answers only let the ranker type
    real10's 1.8 m doorless gap on the mirror axis a door (door 0.43 against opening's few percent, margin 0.31) while the
    model gave closed 0.29 there: a ranker unsure whether a gap is an opening at all must not decide its type. The
    door re-ran the later passes differently (32 walls merged, 14 rooms and 28 openings more on L0-L6); the truth has
    nothing there."""
    ranked_allowed = sorted(((scores.get(a, 0.0), a) for a in allowed), key=lambda t: (-t[0], t[1]))
    top_share, top = ranked_allowed[0]
    second = max((v for c, v in scores.items() if c != top), default=0.0)
    return top, round(top_share - second, 4)


def untrusted_change(model: Optional[dict], rule: Optional[str], rule_answer: str, rule_confidence: float,
                     scores: dict, margin: float, allowed) -> Optional[str]:
    """The answer the ranker would have given if its transition were trusted (for the record; pure), else None."""
    if not model or not scores or model.get("transitions") is None or rule_confidence >= RULE_TRUST \
            or margin < MARGIN_MIN or len(list(allowed)) < 2:
        return None
    top, _margin = top_and_margin(scores, allowed)
    return top if top != rule_answer else None


def model_path(kind: str, models_dir: Path = MODELS_DIR) -> Path:
    return Path(models_dir) / f"{kind}.json"


def table_path(kind: str, models_dir: Path = MODELS_DIR) -> Path:
    return Path(models_dir) / f"{kind}_table.json.gz"


def read_table(kind: str, models_dir: Path = MODELS_DIR) -> Optional[dict]:
    """The committed training table of a kind (gzip JSON), None when there is none."""
    import gzip

    path = table_path(kind, models_dir)
    if not path.is_file():
        return None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def load_model(kind: str, models_dir: Path = MODELS_DIR) -> Optional[dict]:
    """The stored model of a kind, read once per process; None when there is none (the rules alone). 20 Nov 2026
    (``bandit ship``): ``WENART_RANKER_MODELS`` names another folder (a candidate gated before it ships)."""
    if models_dir == MODELS_DIR and os.environ.get("WENART_RANKER_MODELS"):
        models_dir = Path(os.environ["WENART_RANKER_MODELS"])
    key = f"{models_dir}:{kind}"
    if key not in _MODELS:
        path = model_path(kind, models_dir)
        try:
            _MODELS[key] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        except (OSError, ValueError):
            _MODELS[key] = None
    return _MODELS[key]


def reset_models() -> None:
    _MODELS.clear()


# --- evaluation ------------------------------------------------------------------------------------------------------

def _accuracy(rows: list[dict], model: Optional[dict]) -> dict:
    """Rules, ranker (argmax) and integrated accuracy over labelled rows, with the counts and the changes the
    integrated ranker made. 6 Nov 2026 (review): a row that negates a class (a user's ``absent`` entry) is in no
    accuracy (its right class is unknown), but a change INTO the negated class is a wrong change (``negative: true``):
    it counts in ``changed`` and so in ``transition_trust``."""
    n = rules = rank = integ = 0
    corrections = {"n": 0, "rules": 0, "ranker": 0, "integrated": 0, "negatives": 0, "changed_into_negation": 0}
    changed = []
    for r in rows:
        lab = r.get("label")
        answer, by, margin, scores = decide(r["kind"], r["features"], r["rule_answer"], r["rule_confidence"],
                                            allowed=allowed_answers(r), model=model, rule=r.get("rule"))
        base = {"project": r.get("project"), "level_id": r.get("level_id"), "place": r.get("place"),
                "rule": r.get("rule"), "rule_answer": r["rule_answer"], "ranker_answer": answer, "margin": margin,
                "source": r.get("source")}
        if lab is None:
            neg = r.get("negative_of")
            if neg is None:
                continue
            if r.get("source") == "user_correction":
                corrections["negatives"] += 1
            if by == DECIDED_RANKER and answer != r["rule_answer"] and answer == neg:
                changed.append(dict(base, label=None, negated=neg, right=False, rule_right=None, negative=True))
                if r.get("source") == "user_correction":
                    corrections["changed_into_negation"] += 1
            continue
        n += 1
        rules += r["rule_answer"] == lab
        top = max(scores, key=lambda c: (scores[c], c)) if scores else r["rule_answer"]
        rank += top == lab
        integ += answer == lab
        if by == DECIDED_RANKER and answer != r["rule_answer"]:
            changed.append(dict(base, label=lab, right=answer == lab, rule_right=r["rule_answer"] == lab))
        if r.get("source") == "user_correction":
            corrections["n"] += 1
            corrections["rules"] += r["rule_answer"] == lab
            corrections["ranker"] += top == lab
            corrections["integrated"] += answer == lab
    return {"n": n, "rules_acc": round(rules / n, 4) if n else None, "ranker_acc": round(rank / n, 4) if n else None,
            "integrated_acc": round(integ / n, 4) if n else None, "corrections": corrections, "changed": changed}


def group_of(project: Optional[str], groups=None) -> str:
    """The hold-out group of a project: the joined names of its group in ``PROJECT_GROUPS``, else the project."""
    for g in (PROJECT_GROUPS if groups is None else groups):
        if project in g:
            return "+".join(g)
    return str(project)


def lopo(labelled: list[dict], kind: str, l2: float = L2, groups=None, nested: bool = True) -> dict:
    """Leave-one-group-out (pure): for each hold-out group (a project, or the projects of one building together,
    ``PROJECT_GROUPS``), a model trained on the other groups' records scores the group's projects. Per project the
    rules', the ranker's and the integrated accuracy; ``changed`` holds every held-out change (the trust of the
    committed model is measured on them, ``train``).

    ``trusted_acc`` (``nested``, 6 Nov 2026 review): the integrated accuracy when a change counts only through a
    transition trusted WITHOUT the group: for each group G the trust comes from a second level of models, each trained
    without G and without one other group H and scoring H, so G's labels shape neither its own changes nor the changes
    that earn their trust. ``{"per_project", "overall", "changed", "groups"}``."""
    rows = [r for r in labelled if r.get("kind") == kind]
    gkey = {id(r): group_of(r.get("project"), groups) for r in rows}
    group_names = sorted(set(gkey.values()))
    # one design matrix for every fit of this run (rounded as the committed tables are); a fit takes a row subset,
    # thinned by the table's own rule (``thin``)
    names = feature_names(rows)
    X_all = np.array([[round(float(v), 6) for v in row] for row in design(rows, names).tolist()],
                     dtype=np.float64).reshape(len(rows), len(names))
    labels_all = [r.get("label") for r in rows]
    negs_all = [r.get("negative_of") for r in rows]
    weights_all = np.array([float(r.get("weight") or 1.0) for r in rows], dtype=np.float64)
    group_all = [gkey[id(r)] for r in rows]

    def fit_without(*left_out) -> Optional[dict]:
        idx = [i for i, g in enumerate(group_all) if g not in left_out]
        if not idx:
            return None
        kept = {id(r) for r in thin([rows[i] for i in idx])}
        idx = [i for i in idx if id(rows[i]) in kept]
        return _fit_arrays(kind, names, X_all[idx], [labels_all[i] for i in idx], [negs_all[i] for i in idx],
                           weights_all[idx], l2=l2)

    per = {}
    pooled_n = pooled_rules = pooled_rank = pooled_integ = 0
    pooled_corr = {"n": 0, "rules": 0, "ranker": 0, "integrated": 0, "negatives": 0, "changed_into_negation": 0}
    changed = []
    for g in group_names:
        model = fit_without(g)
        for p in sorted({r.get("project") for r in rows if gkey[id(r)] == g}):
            m = _accuracy([r for r in rows if r.get("project") == p], model)
            per[p] = {k: v for k, v in m.items() if k != "changed"}
            per[p]["group"] = g
            changed.extend(m["changed"])
            pooled_n += m["n"]
            pooled_rules += round((m["rules_acc"] or 0) * m["n"])
            pooled_rank += round((m["ranker_acc"] or 0) * m["n"])
            pooled_integ += round((m["integrated_acc"] or 0) * m["n"])
            for k in pooled_corr:
                pooled_corr[k] += m["corrections"][k]
    overall = {"n": pooled_n, "rules_acc": round(pooled_rules / pooled_n, 4) if pooled_n else None,
               "ranker_acc": round(pooled_rank / pooled_n, 4) if pooled_n else None,
               "integrated_acc": round(pooled_integ / pooled_n, 4) if pooled_n else None, "corrections": pooled_corr}
    if nested:
        pooled_trusted = 0
        trusted_in: dict = {}
        for g in group_names:
            inner = []
            for h in group_names:
                if h == g:
                    continue
                inner_model = fit_without(g, h)
                if inner_model is None:
                    continue
                inner.extend(_accuracy([r for r in rows if gkey[id(r)] == h], inner_model)["changed"])
            trust = transition_trust(inner)
            for k, t in trust.items():
                if t["trusted"]:
                    trusted_in.setdefault(k, []).append(g)
            for p in sorted({r.get("project") for r in rows if gkey[id(r)] == g}):
                m = per[p]
                delta = sum(int(c["right"]) - int(bool(c["rule_right"])) for c in changed
                            if c["project"] == p and not c.get("negative")
                            and (trust.get(transition_key(c["rule"], c["ranker_answer"])) or {}).get("trusted"))
                right = round((m["rules_acc"] or 0) * m["n"]) + delta
                m["trusted_acc"] = round(right / m["n"], 4) if m["n"] else None
                pooled_trusted += right
        overall["trusted_acc"] = round(pooled_trusted / pooled_n, 4) if pooled_n else None
        overall["nested_trusted_in_groups"] = {k: len(v) for k, v in sorted(trusted_in.items())}
    return {"per_project": per, "overall": overall, "changed": changed, "groups": group_names}


def transition_key(rule: Optional[str], answer: str) -> str:
    """The name of a ranker change: the rule that gave the weak answer and the ranker's answer (``doorless->door``)."""
    return f"{rule}->{answer}"


def transition_trust(changed: list[dict]) -> dict:
    """``{transition: {"right", "wrong", "trusted"}}`` from held-out changes (pure): a transition is trusted when at least
    ``TRANSITION_MIN`` held-out changes of it exist and at least ``TRANSITION_PRECISION`` of them were right. The R9
    trust ledger's idea applied to the ranker: a change the ranker has not been shown to get right on other projects is
    not made."""
    out: dict = {}
    for c in changed:
        k = transition_key(c.get("rule"), c["ranker_answer"])
        t = out.setdefault(k, {"right": 0, "wrong": 0})
        t["right" if c["right"] else "wrong"] += 1
    for t in out.values():
        n = t["right"] + t["wrong"]
        t["trusted"] = n >= TRANSITION_MIN and t["right"] >= TRANSITION_PRECISION * n
    return dict(sorted(out.items()))


def explain(model: dict, top: int = 8) -> dict:
    """``{class: [(feature, standardised coefficient)]}``: the largest coefficients per class (pure)."""
    out = {}
    for c, coefs in zip(model["classes"], model["coef"]):
        pairs = sorted(zip(model["features"], coefs), key=lambda t: -abs(t[1]))
        out[c] = [(n, round(float(v), 3)) for n, v in pairs[:top] if abs(v) > 1e-9]
    return out


def explain_text(model: dict, top: int = 8) -> str:
    lines = [f"{model['kind']}: {len(model['features'])} features, classes {', '.join(model['classes'])}"]
    for c, pairs in explain(model, top).items():
        lines.append(f"  {c:<9} " + ", ".join(f"{n} {v:+.2f}" for n, v in pairs))
    return "\n".join(lines)


def lopo_table(result: dict) -> str:
    rows = [["project", "n", "rules", "ranker", "integrated", "trusted", "corrections (n rules/ranker/integrated)"]]
    for p, m in sorted(result["per_project"].items()) + [("overall", result["overall"])]:
        c = m["corrections"]
        rows.append([p, str(m["n"]), f"{(m['rules_acc'] or 0):.3f}", f"{(m['ranker_acc'] or 0):.3f}",
                     f"{(m['integrated_acc'] or 0):.3f}", f"{(m.get('trusted_acc') or 0):.3f}",
                     f"{c['n']} {c['rules']}/{c['ranker']}/{c['integrated']}" if c["n"] else "-"])
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(c.ljust(widths[i]) if i == 0 else c.rjust(widths[i]) for i, c in enumerate(r))
                     for r in rows)


# --- collecting the readings -------------------------------------------------------------------------------------------

def read_decisions(folder: Path) -> list[dict]:
    """The decision records of a reading (``reading_check/decisions_*.json``). A level that is a typical-floor copy
    of another (``typical_of`` in building.json, real10's L1 to L6 of L0) repeats the original's decisions: its file
    is left out, so one drawing counts once (the file itself says ``typical_of``)."""
    out = []
    folder = Path(folder)
    copies: set = set()
    try:
        b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
        copies = {lv["id"] for lv in b.get("levels") or [] if lv.get("typical_of")}
    except (OSError, ValueError):
        pass
    for path in sorted((folder / "reading_check").glob("decisions_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("typical_of") or data.get("level_id") in copies:
            continue
        out.extend(data.get("records") or [])
    return out


def collect(work: Path, projects: Optional[list[str]] = None) -> tuple[list[dict], dict]:
    """The labelled records of every project with a truth file and a reading in ``work`` (``work/<p>/``):
    ``(labelled, skipped)`` where ``skipped`` names the projects without a reading or without decisions."""
    from wenart.reading_check import truth as TR

    names = projects or TR.truth_projects()
    labelled, skipped = [], {}
    for p in names:
        truth = TR.load_truth(p)
        folder = Path(work) / p
        if truth is None:
            skipped[p] = "no truth file"
            continue
        if not (folder / "building.json").is_file():
            skipped[p] = "no reading in the work folder"
            continue
        recs = read_decisions(folder)
        if not recs:
            skipped[p] = "no decision records (a reading made before the instrumentation?)"
            continue
        for r in recs:
            r["project"] = p
        labelled.extend(label(recs, truth))
    return labelled, skipped


def train(labelled: list[dict], kind: str, *, commit: Optional[str] = None, date: Optional[str] = None,
          l2: float = L2) -> dict:
    """The committed model of a kind from labelled records: the table, the fit, the leave-one-project-out metrics and
    the provenance (pure apart from the git commit lookup when ``commit`` is None). Returns ``{"model", "table"}``."""
    from wenart.reading_check import truth as TR

    table = table_of(labelled, kind)
    model = fit(table, l2=l2)
    rows = [r for r in labelled if r.get("kind") == kind]
    counts: dict = {}
    for r in rows:
        counts[r.get("source")] = counts.get(r.get("source"), 0) + 1
    result = lopo(labelled, kind, l2=l2)
    model["trained_on"] = {"commit": commit or TR.git_head(), "date": date or TR.today(),
                           "projects": sorted({r.get("project") for r in rows}), "rows": len(table["rows"]),
                           "labelled_rows": len(rows), "counts_per_source": counts, "label_weights": LABEL_WEIGHTS,
                           "labels": label_counts(rows).get(kind, {}).get("by_label", {})}
    model["metrics"] = {"leave_one_project_out": result["per_project"], "overall": result["overall"],
                        "changed_in_lopo": result["changed"], "rule_trust": RULE_TRUST, "margin_min": MARGIN_MIN,
                        "transition_min": TRANSITION_MIN, "transition_precision": TRANSITION_PRECISION}
    # the transitions the integration trusts (decide): measured on the held-out changes of every project
    model["transitions"] = transition_trust(result["changed"])
    model["note"] = TRUST_NOTE
    return {"model": model, "table": table}


def keep_sources(labelled: list[dict], sources: Optional[list[str]]) -> list[dict]:
    """The labelled records whose label source is in ``sources`` (all when None; 6 Nov 2026: the user's ruling that
    only the corrections he made count as truth for the real projects, so the accepted-reading labels can be left out,
    ``--sources user_correction,synthetic``)."""
    return list(labelled) if not sources else [r for r in labelled if r.get("source") in set(sources)]


def retrain(work: Path, projects: Optional[list[str]] = None, *, fresh: bool = False, l2: float = L2,
            models_dir: Path = MODELS_DIR, kinds: Optional[list[str]] = None, log=print,
            sources: Optional[list[str]] = None) -> dict:
    """The whole retrain in one call (``python -m wenart.reading_check ranker retrain --work DIR``): every project with
    a truth file is read with the rules alone (``WENART_RANKER=0``; its decision records do not depend on the ranker,
    and one reading at a time) into ``work/<p>`` unless a reading with decision records is there already (``--fresh``
    reads again), the records are labelled, both models are fitted with their leave-one-project-out metrics and
    transition trust and written to ``models_dir``. Returns ``{kind: model}``."""
    import os

    from wenart.reading_check import regress as RG
    from wenart.reading_check import truth as TR

    names = projects or TR.truth_projects()
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    old = os.environ.get("WENART_RANKER")
    os.environ["WENART_RANKER"] = "0"
    try:
        for p in names:
            folder = work / p
            if not fresh and (folder / "building.json").is_file() and \
                    (any((folder / "reading_check").glob("decisions_*.json")) or p in OTHER_ADAPTER):
                continue
            log(f"{p}: reading (rules alone)")
            try:
                RG.read_project(p, work)
                # 6 Nov 2026 (review): stamped like the score's own readings (truth.reading), so a score made on these
                # readings knows their commit
                (folder / TR.COMMIT_FILE).write_text((TR.git_head() or TR.UNKNOWN_COMMIT) + "\n", encoding="utf-8")
            except Exception as exc:                           # one failed reading must not hide the others
                log(f"{p}: reading failed: {type(exc).__name__}: {str(exc)[:200]}")
    finally:
        if old is None:
            os.environ.pop("WENART_RANKER", None)
        else:
            os.environ["WENART_RANKER"] = old
    labelled, skipped = collect(work, names)
    labelled = keep_sources(labelled, sources)
    for p, why in sorted(skipped.items()):
        log(f"{p}: skipped ({why})")
    out = {}
    for kind in kinds or list(CLASSES):
        if not any(r.get("kind") == kind for r in labelled):
            log(f"{kind}: nothing to train on")
            continue
        got = train(labelled, kind, l2=l2)
        write_model(kind, got["model"], got["table"], models_dir)
        log(f"{kind}: written to {model_path(kind, models_dir)}")
        log(lopo_table({"per_project": got["model"]["metrics"]["leave_one_project_out"],
                        "overall": got["model"]["metrics"]["overall"]}))
        out[kind] = got["model"]
    return out


def write_model(kind: str, model: dict, table: dict, models_dir: Path = MODELS_DIR) -> Path:
    """The model as readable JSON and its table as gzip JSON (``mtime`` fixed so the archive is reproducible)."""
    import gzip

    Path(models_dir).mkdir(parents=True, exist_ok=True)
    model_path(kind, models_dir).write_text(json.dumps(model, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with gzip.GzipFile(table_path(kind, models_dir), "wb", mtime=0) as fh:
        fh.write((json.dumps(table, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
    reset_models()
    return model_path(kind, models_dir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check.ranker", description=__doc__.split("\n")[0])
    ap.add_argument("action", choices=["retrain", "train", "eval", "evaluate", "explain", "label"],
                    help="retrain: read every truth project with the rules alone (or reuse the readings in --work) and "
                         "write both models, one command; evaluate is the same as eval")
    ap.add_argument("--fresh", action="store_true", help="retrain: read every project again")
    ap.add_argument("--work", default=None, help="the readings, one folder per project (score --work leaves them)")
    ap.add_argument("--projects", default=None, help="comma separated (default: every project with a truth file)")
    ap.add_argument("--kind", default=None, help=f"one of {', '.join(CLASSES)} (default: both)")
    ap.add_argument("--models", default=str(MODELS_DIR), help="the models folder")
    ap.add_argument("--l2", type=float, default=L2, help=f"the ridge on the standardised coefficients (default {L2})")
    ap.add_argument("--changes", type=int, default=40, help="how many held-out changed decisions to print")
    ap.add_argument("--sources", default=None,
                    help="comma separated label sources to keep (e.g. user_correction,synthetic); default: all")
    args = ap.parse_args(argv)
    sources = [s.strip() for s in (args.sources or "").split(",") if s.strip()] or None
    kinds = [args.kind] if args.kind else list(CLASSES)
    models_dir = Path(args.models)
    if args.action == "explain":
        for kind in kinds:
            m = load_model(kind, models_dir)
            print(explain_text(m) if m else f"{kind}: no model in {models_dir}")
        return 0
    if not args.work:
        print("ranker: --work DIR is needed (the readings to label)")
        return 2
    projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or None
    if args.action == "retrain":
        got = retrain(Path(args.work), projects, fresh=args.fresh, l2=args.l2, models_dir=models_dir, kinds=kinds,
                      sources=sources)
        for kind, model in got.items():
            print(f"{kind}: labels per source {model['trained_on']['counts_per_source']}")
            print(f"{kind}: transitions: " + "; ".join(
                f"{k} {t['right']} right / {t['wrong']} wrong{' TRUSTED' if t['trusted'] else ''}"
                for k, t in model["transitions"].items()))
            print(f"{kind}: nested (two-level) trust per group: "
                  f"{model['metrics']['overall'].get('nested_trusted_in_groups')}")
            print(explain_text(model))
        return 0 if got else 1
    labelled, skipped = collect(Path(args.work), projects)
    labelled = keep_sources(labelled, sources)
    for p, why in sorted(skipped.items()):
        print(f"{p}: skipped ({why})")
    counts = label_counts(labelled)
    for kind in kinds:
        c = counts.get(kind, {"by_source": {}, "by_label": {}, "negatives": 0})
        print(f"{kind}: {sum(c['by_source'].values())} labelled decisions; per source {c['by_source']}; per label "
              f"{c['by_label']}; negatives {c['negatives']}")
    if args.action == "label":
        return 0
    for kind in kinds:
        if not any(r.get("kind") == kind for r in labelled):
            print(f"{kind}: nothing to train on")
            continue
        got = train(labelled, kind, l2=args.l2)
        print(f"{kind}: ridge l2 {args.l2:g}")
        print(lopo_table({"per_project": got["model"]["metrics"]["leave_one_project_out"],
                          "overall": got["model"]["metrics"]["overall"]}))
        changed = got["model"]["metrics"]["changed_in_lopo"]
        right = sum(1 for c in changed if c["right"])
        print(f"{kind}: {len(changed)} decisions the held-out ranker changed, {right} right, {len(changed) - right} wrong")
        print(f"{kind}: transitions (held out): " + "; ".join(
            f"{k} {t['right']} right / {t['wrong']} wrong{' TRUSTED' if t['trusted'] else ''}"
            for k, t in got["model"]["transitions"].items()))
        print(f"{kind}: nested (two-level) trust per group: "
              f"{got['model']['metrics']['overall'].get('nested_trusted_in_groups')}")
        for c in changed[:max(0, args.changes)]:
            place = f"({c['place'][0]:.2f}, {c['place'][1]:.2f})" if c.get("place") else "?"
            truth = f"negated {c['negated']}" if c.get("negative") else f"truth {c['label']}"
            print(f"  {c['project']} {c['level_id']} at {place} m: {c['rule_answer']} -> {c['ranker_answer']} "
                  f"(margin {c['margin']:.2f}; {truth}: {'right' if c['right'] else 'wrong'})")
        print(explain_text(got["model"]))
        if args.action == "train":
            print(f"{kind}: written to {write_model(kind, got['model'], got['table'], models_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
