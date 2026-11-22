"""Loops A and B of the structure reader's self-teaching (20 Nov 2026; user: "Make the best AI for the building
structure, do your best and then a bit more please", "A bit RL for AI please it needs to teach itself").

What: the R3 ranker (``ranker.py``: a small model per decision kind that may decide where the rule is weak) learns as a
contextual bandit with verifiable rewards. A decision record (``reading_check/decisions_<level>.json``) is the
context, its allowed answers (``ranker.allowed_answers``) are the actions, and the rewards come only from signals the
model does not make itself, each logged with its source (``results/ranker/rewards.jsonl``):

- ``user_correction`` / ``user_mark`` (trust 10): the user's screenshot corrections (the sparse truth) and the user's
  marks of the question sheet (loop A); the labelled answer +1, every other allowed answer -1 (a negation: -1 for it);
- ``synthetic`` (trust 3): the synthetic projects' exact truth, the same way;
- ``agreement`` (trust 1, loop A): a trusted AI kind and an independent signal flag the same place the same way (an
  error: the AI's answer +1, the reading's -1), or the reading, the AI and the drawing's own size tag agree (correct:
  the reading's answer +1); kept apart (``label_source``), never over a user label;
- ``ai_trusted`` (trust 0.5): a trusted AI kind alone (``critic_trust.json``): a trusted finding newly firing on an
  answer -1, an AI answer that agrees with the reading +0.5 (the finding cleared);
- ``code_check`` (trust 1): exploration (below): a code check (``reading_check``) that newly fires near an explored
  decision -1, one that clears +1;
- ``reading_score`` / ``section0_grade``: the change of the reading score and the section-0 grade of a candidate
  model; whole-model rewards that decide whether it ships (``ship``).

Exploration is off in every reading but an exploration run: with ``WENART_RANKER_EXPLORE=seed:eps`` a decision whose
rule is weak (under ``ranker.RULE_TRUST``) and whose ranker margin is low (under ``ranker.MARGIN_MIN``) takes another
allowed answer with probability ``eps`` (a hash of the seed and the place, so a run is reproducible), recorded with
its propensity (``ranker.explore_choice``). Geometry still comes only from the drawings: an action only types a gap
the drawing has (door, window); closed and open stay the rules'.

The update (``learn``): per decision, the trust-weighted rewards of each action; the best positive action is the
row's label, an action with a negative sum and no positive one its negation; one-vs-rest logistic regression
(``ranker._fit_arrays``). It ships (``ship``) only when its decisions on held-out truth labels (leave one project
group out; user and synthetic labels only, never the agreement ones) beat the code alone, the reading-score gate holds
(``score --gate`` with the candidate models) and no project's section-0 grade falls; otherwise the old model stays.

Loop A also writes the question list (``questions``): the disagreements no truth settles (an AI answer against the
reading at a decision, an AI finding no truth or known error judged), ranked by uncertainty times impact (a storey, a
room, an entrance or a lift outranks a window), the top ones as one numbered crop-pair sheet
(``critic_checks.review_sheets``) the user marks with ``critic mark``; each mark becomes a ``user_mark`` label.

``python -m wenart.reading_check bandit labels|questions|explore|learn|ship --work DIR [--projects a,b]``
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import numpy as np

from wenart.reading_check import ranker as RK

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results" / "ranker"
REWARDS_PATH = RESULTS / "rewards.jsonl"
CANDIDATE_DIR = RESULTS / "candidate"
QUESTIONS_DIR = REPO / "results" / "critic" / "questions"
TRUST = {"user_correction": 10.0, "user_mark": 10.0, "synthetic": 3.0, "agreement": 1.0, "code_check": 1.0,
         "ai_trusted": 0.5}
TRUTH_SOURCES = ("user_correction", "user_mark", "synthetic")
AI_PLACE_M = 0.4               # an AI answer this near a gap's place is about that gap
FLAG_PLACE_M = 1.0             # a code check this near a decision flags it
# the code checks that speak about an opening's type (an independent signal for loop A): drawn symbols and size tags
# against the openings read, a door into the air or without its opening; RC7 (the reading's own doubt) and the
# level-wide checks are none
OPENING_CHECKS = {"RC8": None, "RC11": None, "RC17": ("door_into_air", "door_without_opening")}
EXPLORE_REACH_M = 1.5          # a code check this near an explored decision is its reward
SELF_CHECKS = ("RC7", "RC15")  # the reading's own low-confidence places and the AI critic: never a reward
IMPACT = {"storey_count_differs": 5.0, "plan_not_read": 5.0, "room_missing": 4.0, "mirror_twin_missing": 4.0,
          "entrance_missing": 4.0, "lift_missing": 4.0, "flat_no_entrance": 4.0, "stair_missing": 3.5,
          "storey_no_stair_access": 3.5, "stair_no_landing_door": 3.0, "room_not_in_drawing": 3.0,
          "balcony_missing": 3.0, "door_into_air": 3.0, "angled_wall_straight": 3.0, "lift_door_into_flat": 3.0,
          "bedroom_through_bathroom": 2.5, "gap_door": 2.0, "opening_type_differs": 2.0, "window_missing": 2.0,
          "kitchen_no_window": 2.0, "habitable_no_window": 2.0, "balcony_no_door": 1.5, "opening_not_in_drawing": 1.5,
          "gap_window": 1.0}


# ============================================================================================== 1. signals
def ai_signals(index: dict, answers: dict, trust: Optional[dict] = None) -> list:
    """The AI's opening answers at the compare marks (pure): ``[{project, levels, at, drawing, fact, read_right,
    trusted, entry}]``: what the drawing has at a reading's opening according to the model (``drawing``: door, window,
    opening, none), the reading's type there (``fact``), whether the model read image 2 right there, and whether
    ``opening_type_differs`` is a trusted kind (``trust``, the critic's trust file)."""
    from wenart.reading_check import critic_checks as CC

    trusted = bool((((trust or {}).get("checks") or {}).get("compare") or {}).get("opening_type_differs", {})
                   .get("trusted"))
    entries = {e["id"]: e for e in index.get("entries") or []}
    sf = CC.stands_for(index) if index.get("readings") else {}
    out = []
    for a in answers.get("answers") or []:
        if a.get("which") != "compare" or not isinstance(a.get("data"), dict):
            continue
        e = entries.get(a.get("id"))
        if e is None:
            continue
        chunks = CC.chunks_of(e)
        part = int(a.get("part") or 0)
        if part >= len(chunks):
            continue
        byq = {q["qid"]: q for q in chunks[part]}
        for x in CC._first_answers(a["data"]):
            q = byq.get(x.get("id"))
            if q is None or q["kind"] != "opening":
                continue
            if int(e.get("mark_layout") or 1) == 1 and CC.label_cut_pod1(q["point"], e.get("size") or [1600, 1600],
                                                                       q["n"]):
                continue
            out.append({"project": e["project"], "tag": e.get("tag"), "level": e["level"],
                        "levels": sorted(sf.get(e["id"]) or {e["level"]}), "at": q["at"], "drawing": x.get("drawing"),
                        "fact": q["model_fact"], "read_right": x.get("model") == q["model_fact"], "trusted": trusted,
                        "entry": e["id"], "qid": q["qid"]})
    return out


def finding_place(f: dict, building: Optional[dict] = None) -> Optional[list]:
    """A code-check finding's place in building metres (pure): ``at`` / ``place``, the middle of its first piece, or
    its first element's centre (an opening) or middle (a wall)."""
    for k in ("at", "place"):
        p = f.get(k)
        if isinstance(p, (list, tuple)) and len(p) >= 2 and all(isinstance(v, (int, float)) for v in p[:2]):
            return [float(p[0]), float(p[1])]
    pieces = f.get("pieces")
    if pieces and isinstance(pieces[0], (list, tuple)) and len(pieces[0]) == 2:
        a, b = pieces[0]
        return [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]
    if building is not None:
        ids = list(f.get("element_ids") or []) + ([f["wall_id"]] if f.get("wall_id") else [])
        for o in building.get("openings") or []:
            if o.get("id") in ids and o.get("center"):
                return list(o["center"][:2])
        for w in building.get("walls") or []:
            if w.get("id") in ids and w.get("start") and w.get("end"):
                return [(w["start"][0] + w["end"][0]) / 2.0, (w["start"][1] + w["end"][1]) / 2.0]
    return None


def code_flags(folder: Path) -> list:
    """The code checks' findings of a reading with a place (``reading_check/reading_check.json``): ``[{check, kind,
    severity, level, at, key}]``; ``key`` names a finding across two readings of the same project."""
    p = Path(folder) / "reading_check" / "reading_check.json"
    if not p.is_file():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    try:
        b = json.loads((Path(folder) / "building.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        b = None
    out = []
    for f in d.get("findings") or []:
        at = finding_place(f, b)
        if at is None or f.get("severity") == "info":
            continue
        kind = f.get("rule") or f.get("kind") or f.get("name") or ""
        out.append({"check": f.get("check"), "kind": kind, "severity": f.get("severity"), "level": f.get("level_id"),
                    "at": [round(at[0], 2), round(at[1], 2)],
                    "key": f"{f.get('check')}|{kind}|{f.get('level_id')}|{round(at[0], 1)},{round(at[1], 1)}"})
    return out


# ================================================================================================ 2. labels
def _near(rec: dict, items: list, reach: float, levels_of=lambda x: [x.get("level")]) -> list:
    p = rec.get("place")
    if not p:
        return []
    return sorted(((math.dist(p, x["at"]), x) for x in items if rec.get("level_id") in levels_of(x)
                   and x.get("at") and math.dist(p, x["at"]) <= reach), key=lambda t: t[0])


def opening_check(flag: dict) -> bool:
    """Whether a code finding speaks about an opening's type (``OPENING_CHECKS``)."""
    if flag.get("check") not in OPENING_CHECKS:
        return False
    kinds = OPENING_CHECKS[flag["check"]]
    return kinds is None or flag.get("kind") in kinds


def _tag_says(rec: dict) -> Optional[str]:
    """What the drawing's own size tag near a gap says (pure): door (a door-high piece), window, or None."""
    f = rec.get("features") or {}
    if float(f.get("tag_distance") or 99) >= 1.5 or not f.get("tag_height"):
        return None
    return "door" if f.get("tag_door_like") else "window"


def agreement_labels(records: list, ai: list, flags: list) -> tuple:
    """Loop A (pure): ``(labels, disagreements)``. A gap record (door, window or opening built) with an AI answer at
    its place: an ERROR when the answer is a trusted kind's other type and an independent signal says the same (a code
    check flags the place, or the drawing's size tag names the AI's type): label the AI's type; CORRECT when the reading,
    the AI (having read image 2 right there) and the size tag agree: label the reading's type; any other disagreement
    is a question candidate. Labels carry ``source: agreement`` and ``label_source`` (``agreement_error`` /
    ``agreement_correct``)."""
    labels, disagreements = [], []
    for rec in records:
        if rec.get("kind") != RK.KIND_GAP or rec.get("final_answer") not in ("door", "window", "opening"):
            continue
        near = _near(rec, ai, AI_PLACE_M, levels_of=lambda x: x.get("levels") or [x.get("level")])
        if not near:
            continue
        sig = near[0][1]
        answer, drawn, tag = rec["final_answer"], sig.get("drawing"), _tag_says(rec)
        if drawn not in ("door", "window", "opening"):
            continue
        flagged = _near(rec, [f for f in flags if opening_check(f)], FLAG_PLACE_M)
        if drawn != answer:
            if sig.get("trusted") and (flagged or tag == drawn):
                labels.append(dict(rec, label=drawn, source="agreement", label_source="agreement_error",
                                   weight=TRUST["agreement"], evidence={"ai": sig["entry"], "qid": sig["qid"],
                                                                        "flag": flagged[0][1]["key"] if flagged else None,
                                                                        "tag": tag}))
            else:
                disagreements.append({"rec": rec, "ai": sig, "flagged": [f[1]["key"] for f in flagged], "tag": tag})
        elif sig.get("read_right") and tag == answer and not flagged:
            labels.append(dict(rec, label=answer, source="agreement", label_source="agreement_correct",
                               weight=TRUST["agreement"], evidence={"ai": sig["entry"], "qid": sig["qid"], "tag": tag}))
    return labels, disagreements


def user_mark_labels(records: list, questions: dict, marks: dict) -> list:
    """The user's marks on the question sheet as labels (pure): a question about a gap marked right (the AI is right)
    labels the AI's answer, marked wrong labels the reading's (``source: user_mark``)."""
    by_key = {}
    for rec in records:
        if rec.get("place"):
            by_key[_rec_key(rec)] = rec
    out = []
    for fid, q in (questions.get("questions") or {}).items():
        m = marks.get(fid)
        if m is None or q.get("type") != "gap":
            continue
        rec = by_key.get(q.get("record"))
        if rec is None:
            continue
        lab = q["ai_answer"] if m.get("right") else q["reading_answer"]
        out.append(dict(rec, label=lab, source="user_mark", label_source="user_mark", weight=TRUST["user_mark"]))
    return out


def _rec_key(rec: dict) -> str:
    p = rec.get("place") or [0, 0]
    return f"{rec.get('project')}|{rec.get('level_id')}|{rec.get('kind')}|{round(p[0], 1)},{round(p[1], 1)}"


# =============================================================================================== 3. rewards
def events_from_labels(labelled: list) -> list:
    """Full-information rewards of labelled records (pure): the labelled answer +1 and every other allowed answer -1;
    a negation -1 for the negated answer. The withdrawn accepted readings give none (the user's ruling of 6 Nov)."""
    out = []
    for r in labelled:
        src = r.get("source")
        if src not in TRUST or src == "accepted_reading":
            continue
        allowed = RK.allowed_answers(r)
        base = {"key": _rec_key(r), "project": r.get("project"), "kind": r.get("kind"), "level": r.get("level_id"),
                "place": r.get("place"), "source": src, "label_source": r.get("label_source") or src,
                "weight": TRUST[src]}
        if r.get("label") is not None:
            # a label outside the allowed answers (closed, open) still rewards the allowed ones -1
            for a in allowed:
                out.append(dict(base, action=a, reward=1.0 if a == r["label"] else -1.0, label=r["label"]))
            if r["label"] not in allowed:
                out.append(dict(base, action=r["label"], reward=1.0, label=r["label"]))
        elif r.get("negative_of") is not None:
            out.append(dict(base, action=r["negative_of"], reward=-1.0, label=None))
    return out


def events_from_ai(records: list, ai: list) -> list:
    """``ai_trusted`` rewards (pure): at a gap with an AI answer, a trusted kind that would fire (the AI's type differs
    from the answer) -1 for the reading's answer and +0.5 for the AI's; an AI answer that agrees with the reading,
    having read image 2 right there, +0.5 for it (the finding cleared)."""
    out = []
    for rec in records:
        if rec.get("kind") != RK.KIND_GAP or rec.get("final_answer") not in ("door", "window", "opening"):
            continue
        near = _near(rec, ai, AI_PLACE_M, levels_of=lambda x: x.get("levels") or [x.get("level")])
        if not near or not near[0][1].get("trusted"):
            continue
        sig = near[0][1]
        base = {"key": _rec_key(rec), "project": rec.get("project"), "kind": rec["kind"], "level": rec.get("level_id"),
                "place": rec.get("place"), "source": "ai_trusted", "label_source": "ai_trusted",
                "weight": TRUST["ai_trusted"], "evidence": sig["entry"] + "#" + sig["qid"]}
        if sig["drawing"] in ("door", "window", "opening") and sig["drawing"] != rec["final_answer"]:
            out.append(dict(base, action=rec["final_answer"], reward=-1.0))
            out.append(dict(base, action=sig["drawing"], reward=0.5))
        elif sig["drawing"] == rec["final_answer"] and sig.get("read_right"):
            out.append(dict(base, action=rec["final_answer"], reward=0.5))
    return out


def events_from_exploration(base_records: list, explored_records: list, base_flags: list, explored_flags: list,
                            project: str) -> list:
    """``code_check`` rewards of an exploration run (pure): per explored decision (``explored`` on its record), the
    code findings within ``EXPLORE_REACH_M`` on its level that are new in the explored reading (-1 each for the
    explored answer) or gone from it (+1 each), at least one event per explored decision (reward 0 when nothing
    changed), with the decision's propensity."""
    # the reading's own doubt (RC7 places) and the AI's findings (RC15) are no verifiable signal: left out
    base_flags = [f for f in base_flags if f.get("check") not in SELF_CHECKS]
    explored_flags = [f for f in explored_flags if f.get("check") not in SELF_CHECKS]
    base_keys = {f["key"] for f in base_flags}
    exp_keys = {f["key"] for f in explored_flags}
    out = []
    for rec in explored_records:
        ex = rec.get("explored")
        if not ex or not rec.get("place"):
            continue
        rec = dict(rec, project=project)
        new = [f for _d, f in _near(rec, [f for f in explored_flags if f["key"] not in base_keys], EXPLORE_REACH_M)]
        gone = [f for _d, f in _near(rec, [f for f in base_flags if f["key"] not in exp_keys], EXPLORE_REACH_M)]
        reward = float(len(gone) - len(new))
        out.append({"key": _rec_key(rec), "project": project, "kind": rec["kind"], "level": rec.get("level_id"),
                    "place": rec.get("place"), "action": ex["answer"], "reward": max(-1.0, min(1.0, reward)),
                    "source": "code_check", "label_source": "code_check", "weight": TRUST["code_check"],
                    "propensity": ex.get("propensity"), "new": [f["key"] for f in new], "gone": [f["key"] for f in gone]})
    return out


def rows_from_events(records: list, events: list) -> list:
    """Training rows (ranker format) from reward events (pure): per decision and action the trust-weighted reward sum
    (an explored action's divided by its propensity, the inverse-propensity estimate, capped at 10); the best positive
    action is the label, weight its sum; with no positive action, a row negating each action with a negative sum."""
    by_key = {_rec_key(r): r for r in records if r.get("place")}
    sums: dict = {}
    srcs: dict = {}
    for ev in events:
        rec = by_key.get(ev["key"])
        if rec is None:
            continue
        w = float(ev["weight"]) * float(ev["reward"])
        if ev.get("propensity"):
            w = w / max(0.1, float(ev["propensity"]))
        sums.setdefault(ev["key"], {})
        sums[ev["key"]][ev["action"]] = sums[ev["key"]].get(ev["action"], 0.0) + w
        srcs.setdefault(ev["key"], set()).add(ev["source"])
    rows = []
    for key, acts in sums.items():
        rec = by_key[key]
        src = max(srcs[key], key=lambda s: TRUST.get(s, 0.0))
        best = max(acts.items(), key=lambda t: (t[1], t[0]))
        if best[1] > 0:
            rows.append(dict(rec, label=best[0], negative_of=None, weight=min(30.0, best[1]), source=src))
        else:
            for a, v in acts.items():
                if v < 0:
                    rows.append(dict(rec, label=None, negative_of=a, weight=min(30.0, -v), source=src))
    return rows


# ================================================================================================ 4. learning
def fit_rows(rows: list, kind: str, l2: float = RK.L2) -> Optional[dict]:
    rows = [r for r in rows if r.get("kind") == kind]
    if not rows:
        return None
    names = RK.feature_names(rows)
    X = RK.design(rows, names)
    return RK._fit_arrays(kind, names, X, [r.get("label") for r in rows], [r.get("negative_of") for r in rows],
                          np.array([float(r.get("weight") or 1.0) for r in rows], dtype=np.float64), l2=l2)


def held_out(rows: list, truth_rows: list, kind: str, l2: float = RK.L2) -> dict:
    """Leave one project group out (``ranker.group_of``): a model fitted on every other group's rows (all sources)
    decides the held-out group's truth rows (user and synthetic labels only); the code alone (the rule's answer) and
    the code plus the ranker (``ranker.decide``: only where the rule is weak and the margin clear) against the label.
    Returns ``{n, code, ranker, changed, right_changes, per_source}``."""
    # a negation (the user's absent entry, or a fall of the score gate pinned on a decision) is in no accuracy, but a
    # change INTO the negated answer is a wrong change: it counts against its transition (as ``ranker._accuracy``)
    negs = [r for r in truth_rows if r.get("kind") == kind and r.get("label") is None and r.get("negative_of")]
    truth_rows = [r for r in truth_rows if r.get("kind") == kind and r.get("label") is not None]
    groups = sorted({RK.group_of(r.get("project")) for r in truth_rows + negs})
    n = code = integ = changed = right = 0
    changes: list = []
    rows_out: list = []
    per: dict = {}
    for g in groups:
        model = fit_rows([r for r in rows if RK.group_of(r.get("project")) != g], kind, l2)
        if model is None:
            continue
        for r in negs:
            if RK.group_of(r.get("project")) != g:
                continue
            ans, by, _m, _s = RK.decide(kind, r["features"], r["rule_answer"], r["rule_confidence"],
                                        allowed=RK.allowed_answers(r), model=model, rule=r.get("rule"))
            if by == RK.DECIDED_RANKER and ans != r["rule_answer"] and ans == r["negative_of"]:
                changes.append({"rule": r.get("rule"), "ranker_answer": ans, "right": False, "group": g,
                                "negative": True})
        for r in truth_rows:
            if RK.group_of(r.get("project")) != g:
                continue
            ans, by, _m, _s = RK.decide(kind, r["features"], r["rule_answer"], r["rule_confidence"],
                                        allowed=RK.allowed_answers(r), model=model, rule=r.get("rule"))
            n += 1
            code += r["rule_answer"] == r["label"]
            integ += ans == r["label"]
            if by == RK.DECIDED_RANKER and ans != r["rule_answer"]:
                changed += 1
                right += ans == r["label"]
                changes.append({"rule": r.get("rule"), "ranker_answer": ans, "right": ans == r["label"]})
                changes[-1]["group"] = g
            s = per.setdefault(r.get("source"), {"n": 0, "code": 0, "ranker": 0, "trusted": 0})
            s["n"] += 1
            s["code"] += r["rule_answer"] == r["label"]
            s["ranker"] += ans == r["label"]
            rows_out.append((g, r, ans))
    # two-level trust (the R3 gate, nested): a held-out change counts only through a transition the OTHER groups'
    # held-out changes trusted (``ranker.transition_trust``), so the trust is never measured on the rows it decides
    trusted_n = 0
    trust_of = {g: RK.transition_trust([c for c in changes if c["group"] != g]) for g in groups}
    for g, r, ans in rows_out:
        use = ans if ans != r["rule_answer"] and (trust_of[g].get(RK.transition_key(r.get("rule"), ans)) or {}) \
            .get("trusted") else r["rule_answer"]
        trusted_n += use == r["label"]
        per[r.get("source")]["trusted"] += use == r["label"]
    return {"kind": kind, "n": n, "code_acc": round(code / n, 4) if n else None,
            "ranker_acc": round(integ / n, 4) if n else None,
            "trusted_acc": round(trusted_n / n, 4) if n else None, "changed": changed, "right_changes": right,
            "per_source": per, "transitions": RK.transition_trust(changes)}


def beats_code(h: dict) -> bool:
    """A candidate beats the code alone on held-out truth (its decisions through the nested transition trust, what
    ships): more right decisions in all and no fewer on the user's
    labels."""
    if not h.get("n") or h.get("ranker_acc") is None:
        return False
    user = [v for k, v in (h.get("per_source") or {}).items() if k in ("user_correction", "user_mark")]
    user_ok = all(v.get("trusted", v["ranker"]) >= v["code"] for v in user)
    return float(h.get("trusted_acc") or 0) > float(h["code_acc"]) and user_ok


def log_events(events: list, run: str, path: Path = REWARDS_PATH) -> Path:
    from wenart.reading_check import truth as TR

    path.parent.mkdir(parents=True, exist_ok=True)
    commit, date = TR.git_head(), _dt.date.today().isoformat()
    have = {_event_key(e) for e in read_events(path)}
    with path.open("a", encoding="utf-8") as fh:
        for ev in events:
            if _event_key(ev) in have:                          # a reward already logged is not logged again
                continue
            have.add(_event_key(ev))
            fh.write(json.dumps(dict(ev, run=run, commit=commit, date=date), ensure_ascii=False) + "\n")
    return path


def _event_key(e: dict) -> tuple:
    return (e.get("key"), e.get("action"), e.get("source"), e.get("reward"), str(e.get("evidence")))


def read_events(path: Path = REWARDS_PATH) -> list:
    if not Path(path).is_file():
        return []
    out, seen = [], set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        k = _event_key(e)
        if k in seen:                                           # one reward counts once, however often logged
            continue
        seen.add(k)
        out.append(e)
    return out


# ============================================================================================ 5. collecting
def collect_records(work: Path, projects: Optional[list] = None) -> list:
    """Every decision record of the readings in ``work`` (``work/<project>/``), the project on each."""
    out = []
    for p in projects or sorted(x.name for x in Path(work).iterdir() if (x / "building.json").is_file()):
        for r in RK.read_decisions(Path(work) / p):
            r["project"] = p
            out.append(r)
    return out


def critic_inputs() -> list:
    """``[(index, answers)]`` of the RC15 pods whose answers are on this machine (newest first)."""
    from wenart.reading_check import critic as CR

    out = []
    base = REPO.parent.parent.parent if (REPO.parent.name == "worktrees") else REPO
    runs = sorted((Path(base) / "runs").glob("*-critic"), reverse=True) if (Path(base) / "runs").is_dir() else []
    for run in runs:
        ans = run / "results" / "critic" / "agent" / "answers.json"
        if not ans.is_file():
            continue
        answers = json.loads(ans.read_text(encoding="utf-8"))
        if not any(a.get("which") == "compare" for a in answers.get("answers") or []):
            continue
        idx_p = CR.INPUTS_DIR / ("index_pod1.json" if run.name.startswith("20261120-153410") else "index.json")
        out.append((json.loads(idx_p.read_text(encoding="utf-8")), answers))
    return out


def all_labels(work: Path, projects: Optional[list] = None) -> dict:
    """Every label of loop A for the readings in ``work``: ``{truth, agreement, user_marks, ai, flags, records,
    disagreements}`` (truth: the user's corrections and the synthetic truth, ``ranker.collect``)."""
    from wenart.reading_check import critic as CR

    truth, _skipped = RK.collect(Path(work), projects)
    truth = [r for r in truth if r.get("source") in TRUTH_SOURCES]
    records = collect_records(Path(work), projects)
    trust = CR.load_trust()
    ai = []
    for index, answers in critic_inputs():
        ai += ai_signals(index, answers, trust)
    flags = []
    for p in sorted({r["project"] for r in records}):
        flags += [dict(f, project=p) for f in code_flags(Path(work) / p)]
    agree, dis = [], []
    for p in sorted({r["project"] for r in records}):
        recs = [r for r in records if r["project"] == p]
        a, d = agreement_labels(recs, [x for x in ai if x["project"] == p], [f for f in flags if f["project"] == p])
        agree += a
        dis += d
    truth_keys = {_rec_key(r) for r in truth}
    agree = [r for r in agree if _rec_key(r) not in truth_keys]         # never over a truth label
    qdir = latest_questions()
    marks_p = REPO / "results" / "critic" / "user_marks.json"
    marks = json.loads(marks_p.read_text(encoding="utf-8")).get("marks") if marks_p.is_file() else {}
    questions = json.loads((qdir / "questions.json").read_text(encoding="utf-8")) if qdir else {}
    um = user_mark_labels(records, questions, marks or {})
    return {"truth": truth, "agreement": agree, "user_marks": um, "ai": ai, "flags": flags, "records": records,
            "disagreements": dis, "unstable": unstable_places(Path(work), projects)}


def unstable_places(work: Path, projects: Optional[list] = None) -> dict:
    """``{project: [low place]}`` of the readings in ``work`` that were read twice (``twice.py``,
    ``reading_check/read_twice.json``; 22 Nov 2026): the places a harmless change of the drawing changes."""
    from wenart.reading_check import twice as TW

    out = {}
    names = projects or (sorted(x.name for x in Path(work).iterdir() if x.is_dir()) if Path(work).is_dir() else [])
    for p in names:
        low = TW.load_low(Path(work) / p)
        if low:
            out[p] = low
    return out


def instability(q: dict, unstable: Optional[dict]) -> Optional[dict]:
    """The low place (read twice) a question stands at: on its level within ``twice.REACH_M`` of its place (pure)."""
    from wenart.reading_check import twice as TW

    at = q.get("at")
    if not unstable or not isinstance(at, (list, tuple)) or len(at) < 2 or not isinstance(at[0], (int, float)):
        return None
    best, best_d = None, None
    for p in unstable.get(q.get("project")) or []:
        if p.get("level") != q.get("level_id") or p.get("at") is None:
            continue
        d = math.dist([float(at[0]), float(at[1])], [float(p["at"][0]), float(p["at"][1])])
        if d <= TW.REACH_M and (best_d is None or d < best_d):
            best, best_d = p, d
    return best


def latest_questions() -> Optional[Path]:
    runs = sorted(p for p in QUESTIONS_DIR.glob("*") if (p / "questions.json").is_file()) if QUESTIONS_DIR.is_dir() else []
    return runs[-1] if runs else None


# ============================================================================================ 6. questions
def question_list(labels: dict, top: int = 15, include_findings: bool = True,
                  excluded: Optional[dict] = None) -> list:
    """Loop A's questions (pure given the labels and ``excluded``): every gap disagreement and every unjudged RC15
    finding of the newest calibration, scored by uncertainty (1 - the decision's margin; for a finding, nearness of its
    confidence to 0.5) times impact (``IMPACT``), the highest ``top``; a question at a place the reading does not
    reproduce when read twice (``labels["unstable"]``, ``twice.py``; 22 Nov 2026) gets ``twice.INSTABILITY_BONUS`` more
    uncertainty (capped at 1) and says why (``unstable``). 21 Nov 2026 (real09 L3, the user: "this drawing
    is not good we can ignore this drawing"): nothing is asked about a level the user excluded (``excluded``:
    ``truth.excluded_levels()``, ``{project: {level: record}}``; the store's when None)."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import truth as TR

    excluded = TR.excluded_levels() if excluded is None else excluded
    qs = []
    for d in labels["disagreements"]:
        rec, sig = d["rec"], d["ai"]
        margin = float(rec.get("margin") or 0.0) if rec.get("scores") else float(rec.get("rule_confidence") or 0.5)
        u = max(0.05, 1.0 - min(1.0, abs(margin)))
        kind = "gap_door" if "door" in (rec["final_answer"], sig["drawing"]) else "gap_window"
        qs.append({"id": f"question|{_rec_key(rec)}", "type": "gap", "record": _rec_key(rec), "project": rec["project"],
                   "level_id": rec["level_id"], "at": rec["place"], "image_entry": sig["entry"], "kind": kind,
                   "ai_answer": sig["drawing"], "reading_answer": rec["final_answer"], "score": round(u * IMPACT[kind], 3),
                   "description": f"is it a {sig['drawing']} (the AI) or a {rec['final_answer']} (the reading)?"})
    cal_p = REPO / "results" / "critic" / "calibration_checks_r2.json"
    if include_findings and cal_p.is_file():
        cal = json.loads(cal_p.read_text(encoding="utf-8"))
        found = {f["id"]: f for f in cal.get("findings") or []}
        for j in cal.get("judgements") or []:
            f = found.get(j["id"])
            # the newest readings only (the before readings are history), never a judged or dropped finding
            if f is None or j.get("right") is not None or j.get("dropped") or f.get("set") != "after":
                continue
            c = float(f.get("confidence") or 0.5)
            u = max(0.05, 1.0 - 2.0 * abs(c - 0.5))
            imp = IMPACT.get(f["kind"], 1.0)
            qs.append({"id": f["id"], "type": "finding", "project": f.get("project"), "level_id": f.get("level_id"),
                       "at": f.get("at"), "point": f.get("point"), "image_entry": f.get("image_entry"),
                       "kind": f["kind"], "call": f.get("call"), "score": round(u * imp, 3),
                       "description": str(f.get("description") or "")[:110]})
    _ = CR
    qs = [q for q in qs if not TR.is_excluded(excluded, q.get("project"), q.get("level_id"))]
    # 22 Nov 2026 (read twice): a question at a place a harmless change of the drawing changes is more uncertain
    from wenart.reading_check import twice as TW
    for q in qs:
        low = instability(q, labels.get("unstable"))
        if low is None:
            continue
        imp = IMPACT.get(q["kind"], 1.0)
        u = q["score"] / imp if imp else 0.0
        q["score"] = round(min(1.0, u + TW.INSTABILITY_BONUS) * imp, 3)
        q["unstable"] = low["reason"]
    qs.sort(key=lambda q: (-q["score"], q["id"]))
    # one question settles its like: at most two of a kind per project and four of a kind in all, no repeated text
    out, per, seen = [], {}, set()
    for q in qs:
        k1, k2 = (q.get("project"), q["kind"]), q["kind"]
        text = (q.get("project"), q["description"][:60])
        if per.get(k1, 0) >= 2 or per.get(k2, 0) >= 4 or text in seen:
            continue
        per[k1], per[k2] = per.get(k1, 0) + 1, per.get(k2, 0) + 1
        seen.add(text)
        out.append(q)
        if len(out) >= top:
            break
    # a third of the sheet, at least, asks about the ranker's own decisions (each mark there is a label it learns from)
    gaps = [q for q in qs if q["type"] == "gap" and q not in out][:max(0, top // 3 - sum(q["type"] == "gap" for q in out))]
    if gaps:
        keep = [q for q in out if q["type"] == "gap"] + [q for q in out if q["type"] != "gap"][:top - len(gaps)
                                                                                            - sum(q["type"] == "gap" for q in out)]
        out = sorted(keep + gaps, key=lambda q: (-q["score"], q["id"]))
    return out


def write_questions(qs: list, index: dict, dest: Path) -> dict:
    """The question sheet (``critic_checks.review_sheets``: numbered crop pairs, the table, ``findings_index.json``)
    and ``questions.json`` (each question's id, what it asks and the answers it weighs) in ``dest``."""
    from wenart.reading_check import critic as CR
    from wenart.reading_check import critic_checks as CC

    found = []
    for k, q in enumerate(qs):
        found.append({"id": q["id"], "call": q.get("call") or "compare", "kind": q["kind"], "folder": "questions",
                      "entry": q.get("image_entry"), "image_entry": q.get("image_entry"), "level_id": q.get("level_id"),
                      "at": q.get("at"), "point": q.get("point"),
                      "confidence": round(1.0 - k / max(1, len(qs)), 3),          # the rank, so the sheet keeps it
                      "description": f"{q.get('project')}: {q['description']}"})
    dest.mkdir(parents=True, exist_ok=True)
    sheets = CC.review_sheets(index, found, CR.INPUTS_DIR, dest, per_sheet=max(20, len(found)))
    doc = {"note": ("Loop A's questions for the user (uncertainty x impact, the highest first). Mark the sheet with "
                    "`python -m wenart.reading_check critic mark --review " + str(dest.relative_to(REPO)) +
                    " --folder questions --sheet 1 --right N,.. --wrong N,..`: right = the AI is right (the reading is "
                    "wrong), wrong = the reading is right. Each mark becomes a user label (loop B learns from it)."),
           "made": _dt.date.today().isoformat(), "questions": {q["id"]: q for q in qs}, "sheets": sheets}
    (dest / "questions.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return doc


# ================================================================================================= 7. ship
GATE_REACH_M = 2.5             # a score entry this near a changed decision is pinned on it


def _score_entries(folder: Path) -> tuple:
    p = Path(folder) / "reading_check" / "score.json"
    if not p.is_file():
        return {}, None
    d = json.loads(p.read_text(encoding="utf-8"))
    return {e["id"]: e for e in d.get("entries") or [] if e.get("id")}, (None if d.get("sparse") else d.get("total"))


def events_from_gate(base_work: Path, cand_work: Path, changed: list) -> list:
    """``reading_score`` rewards pinned on decisions (pure but for reading the two score files per project): for a
    sparse truth, a user entry the candidate's reading no longer satisfies -1, one it newly satisfies +1, for every
    changed decision within ``GATE_REACH_M`` of the entry (any storey: a typical floor repeats the drawn one's
    places); for an exact (synthetic) truth the project's total falling or rising, -1 or +1 for each of its changed
    decisions. Weighted as the truth they come from."""
    out = []
    for p in sorted({c["project"] for c in changed}):
        (b, bt), (c, ct) = _score_entries(Path(base_work) / p), _score_entries(Path(cand_work) / p)
        mine = [dict(x, key=x.get("key") or _rec_key({"project": p, "level_id": x["level"], "kind": RK.KIND_GAP,
                                                     "place": x["place"]}))
                for x in changed if x["project"] == p and x.get("place")]
        if bt is not None and ct is not None:
            if abs(ct - bt) >= 0.05:
                for ch in mine:
                    out.append({"key": ch["key"], "project": p, "kind": RK.KIND_GAP, "level": ch["level"],
                                "place": ch["place"], "action": ch["new"], "reward": 1.0 if ct > bt else -1.0,
                                "source": "reading_score", "label_source": "reading_score",
                                "weight": TRUST["synthetic"], "evidence": f"{p} total {bt} -> {ct}"})
            continue
        moved = [(e, -1.0) for i, e in c.items() if (b.get(i) or {}).get("satisfied") and not e.get("satisfied")]
        moved += [(e, 1.0) for i, e in c.items() if i in b and not b[i].get("satisfied") and e.get("satisfied")]
        for e, r in moved:
            sig = e.get("at")
            at = sig[2] if isinstance(sig, (list, tuple)) and len(sig) >= 3 else None
            if not at or max(abs(float(at[0])), abs(float(at[1]))) > 500:
                continue
            for ch in mine:
                if math.dist(ch["place"], at) <= GATE_REACH_M:
                    out.append({"key": ch["key"], "project": p, "kind": RK.KIND_GAP, "level": ch["level"],
                                "place": ch["place"], "action": ch["new"], "reward": r, "source": "reading_score",
                                "label_source": "reading_score", "weight": TRUST["user_correction"],
                                "evidence": f"{e['id']} {'fell' if r < 0 else 'held newly'}"})
    return out


def gate_rows(records: list, events: list) -> list:
    """Truth-like rows from pinned gate rewards (pure): a decision whose candidate answer made a user entry fall
    negates that answer; one that made entries hold labels it (only when nothing fell there)."""
    by_key = {_rec_key(r): r for r in records if r.get("place")}
    acc: dict = {}
    for ev in events:
        if ev.get("source") != "reading_score" or ev.get("key") not in by_key:
            continue
        acc.setdefault((ev["key"], ev["action"]), []).append(float(ev["reward"]))
    out = []
    for (key, action), rs in sorted(acc.items()):
        rec = by_key[key]
        if min(rs) < 0:
            out.append(dict(rec, label=None, negative_of=action, source="reading_score", weight=TRUST["synthetic"]))
        else:
            out.append(dict(rec, label=action, negative_of=None, source="reading_score", weight=TRUST["synthetic"]))
    return out


def run_gate(models_dir: Optional[Path], work: Path, log: Path) -> bool:
    """``score --gate`` with the models of ``models_dir`` (``WENART_RANKER_MODELS``); True when it holds."""
    env = dict(os.environ)
    if models_dir is not None:
        env["WENART_RANKER_MODELS"] = str(models_dir)
    with open(log, "w", encoding="utf-8") as fh:
        r = subprocess.run(["python3", "-m", "wenart.reading_check", "score", "--gate", "--fresh", "--work", str(work)],
                           cwd=str(REPO), env=env, stdout=fh, stderr=subprocess.STDOUT)
    return r.returncode == 0


def changed_decisions(records: list, model: dict, kind: str) -> list:
    """The decisions a model would change against the committed one (pure): ``[{project, level, place, old, new}]``."""
    old = RK.load_model(kind)
    out = []
    for r in records:
        if r.get("kind") != kind or not r.get("place"):
            continue
        allowed = RK.allowed_answers(r)
        a_old = RK.decide(kind, r["features"], r["rule_answer"], r["rule_confidence"], allowed=allowed, model=old,
                          rule=r.get("rule"))[0] if old else r["rule_answer"]
        a_new = RK.decide(kind, r["features"], r["rule_answer"], r["rule_confidence"], allowed=allowed, model=model,
                          rule=r.get("rule"))[0]
        if a_old != a_new:
            out.append({"project": r.get("project"), "level": r.get("level_id"), "place": r.get("place"),
                        "old": a_old, "new": a_new, "key": _rec_key(r)})

    return out


# =================================================================================================== CLI
def _cmd_labels(args) -> dict:
    lab = all_labels(Path(args.work), _projects(args))
    counts: dict = {}
    for name in ("truth", "agreement", "user_marks"):
        for r in lab[name]:
            k = (r.get("label_source") or r.get("source"), r.get("kind"), r.get("label") or f"not {r.get('negative_of')}")
            counts[k] = counts.get(k, 0) + 1
    print("labels by source, kind and answer:")
    for (s, k, a), n in sorted(counts.items()):
        print(f"  {s:18} {k:18} {a:14} {n}")
    print(f"AI signals {len(lab['ai'])}, code flags {len(lab['flags'])}, disagreements {len(lab['disagreements'])}")
    return lab


def _projects(args) -> Optional[list]:
    return [p for p in (args.projects or "").split(",") if p] or None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check bandit", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("labels", "questions", "explore", "learn", "ship"):
        p = sub.add_parser(name)
        p.add_argument("--work", required=True, help="the readings (one folder per project, as score --work leaves)")
        p.add_argument("--projects", default=None)
        if name == "questions":
            p.add_argument("--top", type=int, default=15)
        if name == "explore":
            p.add_argument("--seed", type=int, default=1)
            p.add_argument("--eps", type=float, default=0.3)
            p.add_argument("--out", required=True, help="where the explored readings go")
        if name in ("learn", "ship"):
            p.add_argument("--l2", type=float, default=RK.L2)
            p.add_argument("--explored", default=None, help="the explore run's folder (its rewards are logged)")
        if name == "ship":
            p.add_argument("--gate-work", required=True, help="a folder for the gate's fresh readings")
    args = ap.parse_args(argv)
    if args.cmd == "labels":
        _cmd_labels(args)
        return 0
    if args.cmd == "questions":
        from wenart.reading_check import critic as CR

        lab = all_labels(Path(args.work), _projects(args))
        qs = question_list(lab, args.top)
        dest = QUESTIONS_DIR / _dt.date.today().strftime("%Y%m%d")
        doc = write_questions(qs, CR.load_index(), dest)
        for k, q in enumerate(qs, 1):
            print(f"{k:>2} {q['score']:.2f} {q['kind']:24} {q.get('project')} {q['description'][:80]}")
        print(f"written {dest} ({len(doc['questions'])} questions)")
        return 0
    if args.cmd == "explore":
        return _cmd_explore(args)
    if args.cmd in ("learn", "ship"):
        return _cmd_learn(args, ship=args.cmd == "ship")
    return 2


def _cmd_explore(args) -> int:
    """An exploration run: every project read again with ``WENART_RANKER_EXPLORE`` into ``--out``, its reading check
    compared with the greedy reading's in ``--work``; the rewards logged (``code_check``)."""
    from wenart.reading_check import regress as RG

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    events = []
    os.environ["WENART_RANKER_EXPLORE"] = f"{args.seed}:{args.eps}"
    for p in _projects(args) or []:
        folder = out / p if (out / p / "building.json").is_file() else RG.read_project(p, out)   # a run resumed
        base = Path(args.work) / p
        ev = events_from_exploration(RK.read_decisions(base), RK.read_decisions(folder), code_flags(base),
                                     code_flags(folder), p)
        events += ev
        print(f"{p}: {sum(1 for r in RK.read_decisions(folder) if r.get('explored'))} explored decision(s), "
              f"{len(ev)} reward(s): {sum(1 for e in ev if e['reward'] < 0)} negative, "
              f"{sum(1 for e in ev if e['reward'] > 0)} positive")
    os.environ.pop("WENART_RANKER_EXPLORE", None)
    (out / "exploration_rewards.json").write_text(json.dumps(events, indent=1) + "\n", encoding="utf-8")
    log_events(events, f"explore:{args.seed}:{args.eps}")
    return 0


def _cmd_learn(args, ship: bool) -> int:
    lab = all_labels(Path(args.work), _projects(args))
    records = lab["records"]
    events = events_from_labels(lab["truth"] + lab["user_marks"] + lab["agreement"]) + events_from_ai(records, lab["ai"])
    explored = [e for e in read_events() if e.get("source") == "code_check"]
    if args.explored:
        explored = json.loads((Path(args.explored) / "exploration_rewards.json").read_text(encoding="utf-8"))
    events += explored
    # the gate's own verdicts on earlier candidates, pinned on the decisions they changed (``events_from_gate``)
    gate_events = [e for e in read_events() if e.get("source") == "reading_score" and e.get("key") not in (None, "*")]
    events += gate_events
    rows = rows_from_events(records, events)
    truth_rows = [dict(r, weight=r.get("weight")) for r in lab["truth"] + lab["user_marks"]] + \
        gate_rows(records, gate_events)
    report = {"date": _dt.date.today().isoformat(), "events": len(events),
              "events_by_source": {}, "kinds": {}}
    for ev in events:
        report["events_by_source"][ev["source"]] = report["events_by_source"].get(ev["source"], 0) + 1
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    ok_kinds = []
    for kind in (RK.KIND_GAP, RK.KIND_WALL):
        h = held_out(rows, truth_rows, kind, args.l2)
        model = fit_rows(rows, kind, args.l2)
        if model is None:
            continue
        # the R3 gate: a change ships only through a transition its held-out changes trusted
        model["transitions"] = h["transitions"]
        model["trained_on"] = {"by": "bandit", "date": report["date"], "rows": len(rows),
                               "events_by_source": report["events_by_source"], "trust": TRUST}
        model["metrics"] = {"held_out_truth": h}
        model["note"] = RK.TRUST_NOTE
        ch = changed_decisions(records, model, kind)
        report["kinds"][kind] = {"held_out": h, "beats_code": beats_code(h), "changed_decisions": ch}
        (CANDIDATE_DIR / f"{kind}.json").write_text(json.dumps(model, indent=1) + "\n", encoding="utf-8")
        print(f"{kind}: held out on {h['n']} truth labels: code alone {h['code_acc']}, code + ranker "
              f"{h['ranker_acc']} ({h['right_changes']} of {h['changed']} changes right), through the nested trust "
              f"{h['trusted_acc']}; per source {h['per_source']}; trusted transitions "
              f"{[k for k, v in h['transitions'].items() if v['trusted']]}; beats the code: {beats_code(h)}; "
              f"{len(ch)} decision(s) would change on these readings")
        if beats_code(h):
            ok_kinds.append(kind)
    # the exploration and gate rewards were logged by their own runs: only the label and AI rewards are new here
    log_events([e for e in events if e.get("source") not in ("code_check", "reading_score")], "learn")
    (RESULTS / "bandit_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    if not ship:
        return 0
    if not ok_kinds:
        print("ship: no kind beats the code alone on held-out truth: the committed models stay")
        return 0
    stage = RESULTS / "stage"
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)
    for kind in (RK.KIND_GAP, RK.KIND_WALL):
        src = CANDIDATE_DIR / f"{kind}.json" if kind in ok_kinds else RK.model_path(kind)
        if src.is_file():
            shutil.copy(src, stage / f"{kind}.json")
    holds = run_gate(stage, Path(args.gate_work), RESULTS / "gate_candidate.log")
    changed = [c for k in ok_kinds for c in report["kinds"][k]["changed_decisions"]]
    pinned = events_from_gate(Path(args.work), Path(args.gate_work), changed)
    log_events([{"key": "*", "project": "*", "kind": ",".join(ok_kinds), "action": "ship", "reward": 1.0 if holds
                 else -1.0, "source": "reading_score", "label_source": "reading_score", "weight": 1.0}] + pinned,
               "ship")
    print(f"ship: {len(pinned)} gate reward(s) pinned on changed decisions: "
          f"{sum(1 for e in pinned if e['reward'] < 0)} negative, {sum(1 for e in pinned if e['reward'] > 0)} positive")
    if not holds:
        print("ship: the reading-score gate falls with the candidate: the committed models stay")
        return 1
    for kind in ok_kinds:
        shutil.copy(CANDIDATE_DIR / f"{kind}.json", RK.model_path(kind))
    print(f"ship: the gate holds; shipped {', '.join(ok_kinds)} (check the section-0 grades of the changed projects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
