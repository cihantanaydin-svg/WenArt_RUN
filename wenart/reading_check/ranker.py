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
   once per process.

``python -m wenart.reading_check.ranker train|eval|explain|label --work DIR [--projects a,b] [--kind k]``: ``train``
labels the readings in ``DIR`` (one folder per project, as ``score --work`` leaves them), fits both models, writes them
with their tables and prints the leave-one-project-out table and the explanation; ``eval`` prints the table without
writing; ``explain`` prints the stored models' top features; ``label`` prints the label counts per kind and source.

Why: a correction used to become one hand-written rule and nothing measured whether it helped the other projects.
The ranker makes the corrections compound: every accept, reject or remark of the user is a labelled example, the
model is retrained in seconds on CPU, the regression set is re-scored, and the gate (``score --gate``) decides.

How: pure functions over lists of dicts and numpy arrays; the geometry of the join is the truth matcher's
(``score.py`` tolerances); the model file is plain JSON; the integration is one call in ``openings.classify_gap``.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import sys
from pathlib import Path
from typing import Optional

import numpy as np

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
LABEL_WEIGHTS = {"user_correction": 10.0, "synthetic": 3.0, "accepted_reading": 1.0}   # docs/milestone14.md R3 (3)
PLACE_TOL_M = 0.5                # a truth opening this close to a gap's place ...
WIDTH_TOL_M = 0.3                # ... and this close in width labels the gap
WALL_LATERAL_M = 0.15            # a truth wall covers a place or a pair within this of its centre line
WALL_END_M = 0.05                # ... inside its extent grown by this
OVERLAP_SHARE = 0.5              # a truth wall covers a pair when they overlap this share of the pair's length
L2 = 1.0                         # ridge on the standardised coefficients (the intercept is free)
NEWTON_ITERATIONS = 25           # Newton steps; the weighted logistic loss with a ridge is convex and converges well before
NO_POSITIVES_INTERCEPT = -10.0   # a class without a positive example scores about 0 everywhere
ROUND = 10                       # the stored numbers' decimals (enough for bit-for-bit reproduction after rounding)
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
    caller reads ``absent``), else None."""
    best = None
    for key, kind in (("doors", "door"), ("windows", "window"), ("openings", "opening")):
        for e in level_truth.get(key) or []:
            if not e.get("center") or e.get("width") is None:
                continue
            d = _dist(e["center"], place)
            if d <= PLACE_TOL_M and abs(float(e["width"]) - width) <= WIDTH_TOL_M and (best is None or d < best[2]):
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


def label_gap(rec: dict, level_truth: dict, truth_source: str, walls: Optional[list] = None) -> Optional[dict]:
    """The label of a ``gap_kind`` record from one level's truth (pure): ``{"label", "weight", "source"}``; a negated
    truth element gives ``{"negative_of": class, ...}``; None for a record without a place. ``walls`` is
    ``_truth_walls(level_truth)`` when the caller has it already."""
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
    return {"label": "open", "weight": LABEL_WEIGHTS.get(truth_source, 1.0), "source": truth_source, "element": None}


def label_wall(rec: dict, level_truth: dict, truth_source: str, walls: Optional[list] = None) -> Optional[dict]:
    """The label of a ``wall_or_notation`` record (pure): ``wall`` when a truth wall covers the pair's centre line,
    else ``notation``; a negated truth wall covering it is a negative of ``wall``."""
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
    return {"label": "notation", "weight": LABEL_WEIGHTS.get(truth_source, 1.0), "source": truth_source,
            "element": None}


def label(decisions: list[dict], truth: dict) -> list[dict]:
    """Every decision record joined with the truth (pure): the record with ``label`` (or ``negative_of``), ``weight``
    and ``source`` added; records on levels the truth does not know, or without a place, are left out. A ``partial``
    truth labels only its levels."""
    per = truth.get("per_level") or {}
    src = truth.get("source") or "accepted_reading"
    walls_of = {lid: _truth_walls(lv) for lid, lv in per.items()}
    out = []
    for rec in decisions:
        lv = per.get(rec.get("level_id"))
        if lv is None or rec.get("final_answer") == "dropped":     # a candidate the reader discarded is no decision
            continue
        lab = label_gap(rec, lv, src, walls_of[rec["level_id"]]) if rec.get("kind") == KIND_GAP \
            else label_wall(rec, lv, src, walls_of[rec["level_id"]])
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
    kind = table["kind"]
    classes = list(CLASSES[kind])
    names = list(table["features"])
    X = np.array(table["rows"], dtype=np.float64).reshape(len(table["rows"]), len(names))
    labels, negs = table["labels"], table.get("negative_of") or [None] * len(labels)
    weights = np.array(table["weights"], dtype=np.float64)
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
           model: Optional[dict] = None) -> tuple[str, str, float, dict]:
    """``(answer, decided_by, margin, scores)`` (step 4; pure given the model): the ranker's answer when the rule's
    confidence is under ``RULE_TRUST``, the ranker has a model, more than one answer is allowed and its margin (top
    share minus second among the allowed answers) is at least ``MARGIN_MIN``; else the rule's answer with
    ``decided_by: rule``. ``scores`` is empty without a model."""
    model = model if model is not None else load_model(kind)
    if model is None:
        return rule_answer, DECIDED_RULE, 0.0, {}
    scores = scores_of(model, features)
    allowed = list(allowed) if allowed else list(scores)
    ranked = sorted(((scores.get(a, 0.0), a) for a in allowed), key=lambda t: (-t[0], t[1]))
    margin = round(ranked[0][0] - (ranked[1][0] if len(ranked) > 1 else 0.0), 4)
    if rule_confidence < RULE_TRUST and len(ranked) > 1 and margin >= MARGIN_MIN:
        return ranked[0][1], DECIDED_RANKER, margin, scores
    return rule_answer, DECIDED_RULE, margin, scores


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
    """The stored model of a kind, read once per process; None when there is none (the rules alone)."""
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
    """Rules, ranker (argmax) and integrated accuracy over labelled rows (negatives are skipped), with the counts."""
    n = rules = rank = integ = 0
    corrections = {"n": 0, "rules": 0, "ranker": 0, "integrated": 0}
    changed = []
    for r in rows:
        lab = r.get("label")
        if lab is None:
            continue
        n += 1
        rules += r["rule_answer"] == lab
        answer, by, margin, scores = decide(r["kind"], r["features"], r["rule_answer"], r["rule_confidence"],
                                            allowed=allowed_answers(r), model=model)
        top = max(scores, key=lambda c: (scores[c], c)) if scores else r["rule_answer"]
        rank += top == lab
        integ += answer == lab
        if by == DECIDED_RANKER and answer != r["rule_answer"]:
            changed.append({"project": r.get("project"), "level_id": r.get("level_id"), "place": r.get("place"),
                            "rule_answer": r["rule_answer"], "ranker_answer": answer, "label": lab,
                            "margin": margin, "right": answer == lab})
        if r.get("source") == "user_correction":
            corrections["n"] += 1
            corrections["rules"] += r["rule_answer"] == lab
            corrections["ranker"] += top == lab
            corrections["integrated"] += answer == lab
    return {"n": n, "rules_acc": round(rules / n, 4) if n else None, "ranker_acc": round(rank / n, 4) if n else None,
            "integrated_acc": round(integ / n, 4) if n else None, "corrections": corrections, "changed": changed}


def lopo(labelled: list[dict], kind: str) -> dict:
    """Leave-one-project-out (pure): for each project with labelled records of ``kind``, a model trained on the other
    projects' records scores it. ``{"per_project": {p: metrics}, "overall": metrics}``."""
    rows = [r for r in labelled if r.get("kind") == kind]
    projects = sorted({r.get("project") for r in rows})
    per = {}
    pooled_n = pooled_rules = pooled_rank = pooled_integ = 0
    pooled_corr = {"n": 0, "rules": 0, "ranker": 0, "integrated": 0}
    changed = []
    for p in projects:
        train_rows = [r for r in rows if r.get("project") != p]
        test_rows = [r for r in rows if r.get("project") == p]
        model = fit(table_of(train_rows, kind)) if train_rows else None
        m = _accuracy(test_rows, model)
        per[p] = {k: v for k, v in m.items() if k != "changed"}
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
    return {"per_project": per, "overall": overall, "changed": changed}


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
    rows = [["project", "n", "rules", "ranker", "integrated", "corrections (n rules/ranker/integrated)"]]
    for p, m in sorted(result["per_project"].items()) + [("overall", result["overall"])]:
        c = m["corrections"]
        rows.append([p, str(m["n"]), f"{(m['rules_acc'] or 0):.3f}", f"{(m['ranker_acc'] or 0):.3f}",
                     f"{(m['integrated_acc'] or 0):.3f}",
                     f"{c['n']} {c['rules']}/{c['ranker']}/{c['integrated']}" if c["n"] else "-"])
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(c.ljust(widths[i]) if i == 0 else c.rjust(widths[i]) for i, c in enumerate(r))
                     for r in rows)


# --- collecting the readings -------------------------------------------------------------------------------------------

def read_decisions(folder: Path) -> list[dict]:
    """The decision records of a reading (``reading_check/decisions_*.json``), each with its project added."""
    out = []
    rc = Path(folder) / "reading_check"
    for path in sorted(rc.glob("decisions_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
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


def train(labelled: list[dict], kind: str, *, commit: Optional[str] = None, date: Optional[str] = None) -> dict:
    """The committed model of a kind from labelled records: the table, the fit, the leave-one-project-out metrics and
    the provenance (pure apart from the git commit lookup when ``commit`` is None). Returns ``{"model", "table"}``."""
    from wenart.reading_check import truth as TR

    table = table_of(labelled, kind)
    model = fit(table)
    rows = [r for r in labelled if r.get("kind") == kind]
    counts: dict = {}
    for r in rows:
        counts[r.get("source")] = counts.get(r.get("source"), 0) + 1
    result = lopo(labelled, kind)
    model["trained_on"] = {"commit": commit or TR.git_head(), "date": date or TR.today(),
                           "projects": sorted({r.get("project") for r in rows}), "rows": len(rows),
                           "counts_per_source": counts, "label_weights": LABEL_WEIGHTS,
                           "labels": label_counts(rows).get(kind, {}).get("by_label", {})}
    model["metrics"] = {"leave_one_project_out": result["per_project"], "overall": result["overall"],
                        "changed_in_lopo": result["changed"], "rule_trust": RULE_TRUST, "margin_min": MARGIN_MIN}
    return {"model": model, "table": table}


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
    ap.add_argument("action", choices=["train", "eval", "evaluate", "explain", "label"],
                    help="evaluate is the same as eval (for shells that treat the word specially)")
    ap.add_argument("--work", default=None, help="the readings, one folder per project (score --work leaves them)")
    ap.add_argument("--projects", default=None, help="comma separated (default: every project with a truth file)")
    ap.add_argument("--kind", default=None, help=f"one of {', '.join(CLASSES)} (default: both)")
    ap.add_argument("--models", default=str(MODELS_DIR), help="the models folder")
    args = ap.parse_args(argv)
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
    labelled, skipped = collect(Path(args.work), projects)
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
        got = train(labelled, kind)
        print(lopo_table({"per_project": got["model"]["metrics"]["leave_one_project_out"],
                          "overall": got["model"]["metrics"]["overall"]}))
        print(explain_text(got["model"]))
        if args.action == "train":
            print(f"{kind}: written to {write_model(kind, got['model'], got['table'], models_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
