"""20 Nov 2026 (loops A and B; user: "Make the best AI for the building structure", "A bit RL for AI please it needs
to teach itself").

What: the rewards (full information from truth labels, the AI's trusted answers, the code checks of an exploration
run), the training rows (trust-weighted sums, inverse propensity, negations), the agreement labels and their place in
the trust order (never over a truth label), the question score (uncertainty x impact), the exploration choice
(reproducible, only on weak rules with low margins, only door or window), and the held-out comparison of the code
alone with the code plus the ranker.
Why: a self-teaching loop must learn only from signals it does not make itself, and must never ship a model the
held-out truth and the reading-score gate do not back.
"""
from __future__ import annotations

import os

from wenart.reading_check import bandit as BD
from wenart.reading_check import ranker as RK


def _rec(project="p", place=(1.0, 1.0), rule_answer="door", final="door", conf=0.4, **f):
    feats = dict({"width": 0.9, "run_length": 3.0, "arcs_swing": 0, "tag_distance": 99.0}, **f)
    return {"kind": RK.KIND_GAP, "project": project, "level_id": "L0", "place": list(place), "gap": "run",
            "features": feats, "rule": "doorless", "rule_answer": rule_answer, "rule_confidence": conf,
            "final_answer": final}


def test_truth_labels_give_full_information_rewards_and_accepted_readings_none():
    r = dict(_rec(), label="window", source="synthetic")
    ev = BD.events_from_labels([r, dict(_rec(place=(5, 5)), label="door", source="accepted_reading")])
    assert {(e["action"], e["reward"]) for e in ev} == {("door", -1.0), ("window", 1.0), ("opening", -1.0)}
    assert all(e["source"] == "synthetic" and e["weight"] == BD.TRUST["synthetic"] for e in ev)
    neg = BD.events_from_labels([dict(_rec(), negative_of="door", source="user_correction")])
    assert [(e["action"], e["reward"]) for e in neg] == [("door", -1.0)]


def test_rows_weigh_rewards_by_trust_and_propensity():
    rec = _rec()
    key = BD._rec_key(rec)
    events = [{"key": key, "action": "window", "reward": 1.0, "weight": 3.0, "source": "synthetic"},
              {"key": key, "action": "door", "reward": -1.0, "weight": 3.0, "source": "synthetic"},
              {"key": key, "action": "door", "reward": 1.0, "weight": 1.0, "source": "code_check", "propensity": 0.5}]
    rows = BD.rows_from_events([rec], events)
    assert len(rows) == 1 and rows[0]["label"] == "window" and rows[0]["weight"] == 3.0
    assert rows[0]["source"] == "synthetic"
    only_neg = BD.rows_from_events([rec], [dict(events[1])])
    assert only_neg[0]["label"] is None and only_neg[0]["negative_of"] == "door"


def test_agreement_labels_need_two_independent_signals_and_never_override_truth():
    ai = [{"project": "p", "level": "L0", "levels": ["L0"], "at": [1.1, 1.0], "drawing": "window", "fact": "door",
           "read_right": True, "trusted": True, "entry": "e", "qid": "q1"}]
    flag = [{"check": "RC11", "kind": "", "level": "L0", "at": [1.2, 1.0], "key": "RC11|x"}]
    lab, dis = BD.agreement_labels([_rec()], ai, flag)
    assert [(r["label"], r["label_source"]) for r in lab] == [("window", "agreement_error")] and not dis
    lab, dis = BD.agreement_labels([_rec()], ai, [])                     # the AI alone: a question, no label
    assert lab == [] and len(dis) == 1
    tagged = _rec(tag_distance=0.4, tag_height=1.5, tag_door_like=False)
    lab, _dis = BD.agreement_labels([tagged], ai, [])                    # the drawing's own size tag agrees
    assert lab[0]["label"] == "window"
    agree_ai = [dict(ai[0], drawing="door")]
    door_tag = _rec(tag_distance=0.4, tag_height=2.1, tag_door_like=True)
    lab, _dis = BD.agreement_labels([door_tag], agree_ai, [])
    assert lab[0]["label_source"] == "agreement_correct"


def test_ai_rewards_and_exploration_rewards():
    ai = [{"project": "p", "level": "L0", "levels": ["L0"], "at": [1.0, 1.0], "drawing": "window", "fact": "door",
           "read_right": True, "trusted": True, "entry": "e", "qid": "q1"}]
    ev = BD.events_from_ai([_rec()], ai)
    assert {(e["action"], e["reward"]) for e in ev} == {("door", -1.0), ("window", 0.5)}
    assert BD.events_from_ai([_rec()], [dict(ai[0], trusted=False)]) == []
    base = [_rec()]
    explored = [dict(_rec(), explored={"answer": "window", "propensity": 0.15})]
    new = [{"key": "RC17|door_into_air|L0|1.0,1.0", "level": "L0", "at": [1.0, 1.2]}]
    ev = BD.events_from_exploration(base, explored, [], new, "p")
    assert ev[0]["action"] == "window" and ev[0]["reward"] == -1.0 and ev[0]["propensity"] == 0.15
    ev = BD.events_from_exploration(base, explored, new, [], "p")
    assert ev[0]["reward"] == 1.0                                        # a code finding cleared


def test_exploration_is_reproducible_and_only_on_low_margin_weak_rules(monkeypatch):
    rec = dict(_rec(), place_page=[3.0, 4.0])
    allowed = ["door", "window", "opening"]
    monkeypatch.delenv("WENART_RANKER_EXPLORE", raising=False)
    assert RK.explore_choice(rec, allowed, 0.1) is None                  # never in a normal reading
    monkeypatch.setenv("WENART_RANKER_EXPLORE", "7:1.0")
    a = RK.explore_choice(rec, allowed, 0.1)
    assert a is not None and a[0] == "window" and a[1] == 1.0
    assert RK.explore_choice(rec, allowed, 0.1) == a                     # the same seed and place: the same choice
    assert RK.explore_choice(rec, allowed, 0.5) is None                  # a clear margin is not explored
    assert RK.explore_choice(dict(rec, rule_confidence=0.9), allowed, 0.1) is None
    monkeypatch.setenv("WENART_RANKER_EXPLORE", "7:0.0")
    assert RK.explore_choice(rec, allowed, 0.1) is None
    assert os.environ.get("WENART_RANKER_EXPLORE") == "7:0.0"


def test_held_out_compares_the_code_with_the_code_plus_ranker():
    # 2 groups; the rule says door on doorless gaps that are windows when a window tag is near
    rows, truth = [], []
    for p in ("synthetic-a", "synthetic-b"):
        for k in range(12):
            win = k % 2 == 0
            r = _rec(project=p, place=(k, 0), rule_answer="door", final="door", tag_height=1.5 if win else 2.1,
                     tag_distance=0.3, tag_door_like=not win)
            lab = dict(r, label="window" if win else "door", source="synthetic", weight=3.0)
            rows.append(lab)
            truth.append(lab)
    h = BD.held_out(rows, truth, RK.KIND_GAP)
    assert h["n"] == 24 and h["code_acc"] == 0.5 and h["ranker_acc"] > h["code_acc"] and BD.beats_code(h)


def test_questions_rank_uncertainty_times_impact():
    rec = dict(_rec(), scores={"door": 0.5, "window": 0.45}, margin=0.05)
    lab = {"disagreements": [{"rec": rec, "ai": {"drawing": "window", "entry": "e", "qid": "q1"}, "flagged": [],
                              "tag": None}]}
    qs = BD.question_list(lab, top=5, include_findings=False)
    gap = next(q for q in qs if q["type"] == "gap")
    assert gap["ai_answer"] == "window" and gap["reading_answer"] == "door"
    assert abs(gap["score"] - 0.95 * BD.IMPACT["gap_door"]) < 1e-6
    assert [q["score"] for q in qs] == sorted((q["score"] for q in qs), reverse=True)
    marks = {gap["id"]: {"right": True}}
    um = BD.user_mark_labels([rec], {"questions": {gap["id"]: gap}}, marks)
    assert um[0]["label"] == "window" and um[0]["source"] == "user_mark"
