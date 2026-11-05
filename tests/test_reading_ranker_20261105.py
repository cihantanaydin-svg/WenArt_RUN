"""5 Nov 2026, Milestone 14 track R3 (user: "I want structure recognition to be cumulatively better with the feedbacks
I am giving"): the reader's decision records (one per gap, the rule table), the label join with a hand-made truth (a
hit, a width miss, an absent negative, the weights), the numpy one-vs-rest learner on a tiny separable table
(deterministic, reproducing its stored numbers), ``decide`` (the rule trusted, the ranker above its margin, a hard
constraint never overridden, a missing model falls back), the committed models reproduced bit for bit from their
committed tables, and the end-to-end reading of synthetic-12. CPU only."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _real01_page as R
from wenart.ingest.generic import decisions as DEC
from wenart.ingest.generic import openings as O
from wenart.ingest.generic.model import TextRun
from wenart.reading_check import ranker as RK

REPO = Path(__file__).resolve().parents[1]


def _door(hinge, radius, closed_deg, open_deg):
    return [R.arc(hinge, radius, closed_deg, open_deg)]


def _window(x0, x1, y=0.0, t=0.2):
    """The synthetic window convention: the two faces and one glass line, ending at the jambs."""
    return [R.stroke([(x0, y - t / 2), (x1, y - t / 2)]), R.stroke([(x0, y + t / 2), (x1, y + t / 2)]),
            R.stroke([(x0, y), (x1, y)])]


def _texts(items):
    return [TextRun(id=f"T{k}", text=text, box=(x - 0.3, y - 0.1, x + 0.3, y + 0.1), height=0.2)
            for k, (text, x, y) in enumerate(items)]


def _read(walls, strokes, texts=(), ranker=False):
    log = DEC.DecisionLog("L0", texts=list(texts), ranker=ranker)
    out_walls, openings, gap_log, owned = O.gaps_and_openings(walls, strokes, "t.pdf", 1, decisions=log)
    records = log.finalize((0.0, 0.0), out_walls, openings)
    return out_walls, openings, gap_log, records


# ---------------------------------------------------------------------------------------------- step 1: instrument
def test_one_record_per_gap_with_the_rule_table_and_the_final_answer():
    """A run of three gaps: a door (swing arc), a window (three lines with glass), a doorless passage; plus a gap open
    by its width. Each is one record with its features, the table's rule and confidence, and the final answer read off
    the built level; nothing in the reading changes."""
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0)), R.wall((6.2, 0), (8, 0)), R.wall((9.0, 0), (11, 0)),
             R.wall((15.0, 0), (17, 0))]
    strokes = _door((2.88, 0.08), 0.88, 180, 90) + _window(5.0, 6.2)
    texts = _texts([("SALON", 1.0, 1.5), ("MUTFAK", 1.0, -1.5), ("90/210", 2.45, 0.6)])
    out_walls, openings, gap_log, records = _read(walls, strokes, texts)
    assert [o.kind for o in openings] == ["door", "window", "opening"]
    gaps = [r for r in records if r["kind"] == DEC.KIND_GAP]
    assert len(gaps) == 4 and all(r["decided_by"] == "rule" for r in gaps)
    by_rule = {r["rule"]: r for r in gaps}
    assert set(by_rule) == {"door_swing_arc", "window_glass_3_lines", "doorless", "open_wide"}
    for r in gaps:
        assert r["rule_confidence"] == DEC.RULE_CONFIDENCE[r["rule"]]
        assert r["level_id"] == "L0" and len(r["place"]) == 2 and r["axis"] == 0.0
        assert isinstance(r["features"]["width"], float) and isinstance(r["features"]["exterior"], bool)
    door = by_rule["door_swing_arc"]
    assert door["rule_answer"] == door["final_answer"] == "door" and door["rule_confidence"] == 0.95
    assert door["features"]["arcs_swing"] == 1 and door["features"]["labels_both_sides"] is True
    assert door["features"]["tag_distance"] < 1.0 and door["features"]["tag_door_like"] is True
    assert door["features"]["tag_width_ratio"] == pytest.approx(1.0, abs=0.02)
    assert door["place"] == pytest.approx([2.45, 0.0])
    window = by_rule["window_glass_3_lines"]
    assert window["final_answer"] == "window" and window["features"]["glass_lines"] == 1
    assert window["features"]["parallel_offsets"] == 3 and window["rule_confidence"] == 0.9
    passage = by_rule["doorless"]
    assert passage["rule_answer"] == passage["final_answer"] == "opening" and passage["rule_confidence"] == 0.5
    wide = by_rule["open_wide"]
    assert wide["rule_answer"] == wide["final_answer"] == "open" and wide["features"]["width"] == pytest.approx(4.0)
    # the gap log is unchanged in shape (no ranker, no decided_by)
    assert [e["class"] for e in gap_log if e["kind"] == "run"] == ["door", "window", "empty", "open"]
    assert not any("decided_by" in e for e in gap_log)


def test_the_rule_table_names_every_rule_the_classifier_can_give():
    """Every rule name ``gap_rule`` returns is in the table, with a confidence between 0 and 1 and a reason."""
    names = {"door_swing_arc", "door_named", "door_open_leaf", "door_sliding_leaf", "window_glass_3_lines",
             "window_2_lines", "window_named", "window_raster", "closed_narrow", "closed_inside_wall",
             "closed_wall_faces", "open_wide", "open_lined", "open_split", "doorless", "unclassified",
             "notation_layer", "axis_grid", "tread_run", "wide_band", "flight", "wall_chosen_layer",
             "wall_document_layer", "secondary_pair", "layer_not_chosen", "layer_not_chosen_undecided"}
    assert names <= set(DEC.RULE_CONFIDENCE)
    assert all(0.0 < v <= 1.0 for v in DEC.RULE_CONFIDENCE.values())
    assert DEC.RULE_CONFIDENCE["door_swing_arc"] == 0.95 and DEC.RULE_CONFIDENCE["unclassified"] == 0.2
    assert DEC.RULE_CONFIDENCE["window_2_lines"] == 0.6 and DEC.RULE_CONFIDENCE["doorless"] == 0.5
    with pytest.raises(KeyError):
        DEC.rule_confidence("a rule nobody wrote")


def test_without_a_log_the_classifier_is_the_old_one():
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    out_walls, openings, log, owned = O.gaps_and_openings(walls, _door((2.88, 0.08), 0.88, 180, 90), "t.pdf", 1)
    assert [o.kind for o in openings] == ["door"] and len(out_walls) == 1


def test_a_mirror_twin_gives_its_answer_as_a_feature():
    """Two flats mirrored about x = 6: the left flat's door has a swing, the right flat's gap is bare (synthetic-12's
    failure class). The bare gap's record knows its twin is a door; the drawn door's twin is an opening."""
    walls = [R.wall((0, 0), (2.5, 0)), R.wall((3.4, 0), (8.6, 0)), R.wall((9.5, 0), (12, 0)),
             R.wall((0, 4), (12, 4)), R.wall((0, 0), (0, 4)), R.wall((12, 0), (12, 4)), R.wall((6, 0), (6, 4))]
    out_walls, openings, gap_log, records = _read(walls, _door((3.38, 0.08), 0.88, 180, 90))
    assert sorted(o.kind for o in openings) == ["door", "opening"]
    gaps = {r["rule"]: r for r in records if r["kind"] == DEC.KIND_GAP}
    assert gaps["door_swing_arc"]["features"]["twin_opening"] is True
    assert gaps["doorless"]["features"]["twin_door"] is True and gaps["doorless"]["features"]["twin_known"] is True


# ---------------------------------------------------------------------------------------------------- step 2: label
def _truth(doors=(), windows=(), walls=(), absent=()):
    lv = {"doors": [dict(e, source=e.get("source", "synthetic")) for e in doors],
          "windows": [dict(e, source=e.get("source", "synthetic")) for e in windows],
          "openings": [], "walls": [dict(w, source=w.get("source", "synthetic")) for w in walls], "rooms": [],
          "stairs": []}
    for kind, e in absent:
        lv[kind].append(dict(e, absent=True, source="user_correction"))
    return {"project": "t", "source": "synthetic", "status": "accepted", "levels": [{"id": "L0"}],
            "per_level": {"L0": lv}}


def _gap_record(place, width, rule="doorless", answer="opening", level="L0"):
    return {"kind": DEC.KIND_GAP, "gap": "run", "level_id": level, "place": list(place), "axis": 0.0,
            "features": {"width": width, "run_length": 10.0, "arcs_swing": 0}, "rule": rule, "rule_answer": answer,
            "rule_confidence": DEC.RULE_CONFIDENCE[rule], "final_answer": answer, "decided_by": "rule"}


def test_label_join_hit_width_miss_absent_negative_and_weights():
    truth = _truth(doors=[{"id": "d1", "center": [2.45, 0.0], "width": 0.9},
                          {"id": "d2", "center": [8.0, 0.0], "width": 0.9, "source": "user_correction"}],
                   windows=[{"id": "w1", "center": [5.6, 0.0], "width": 1.2, "source": "accepted_reading"}],
                   walls=[{"id": "wa", "start": [10.0, 0.0], "end": [14.0, 0.0], "thickness": 0.2}],
                   absent=[("windows", {"id": "w-no", "center": [16.0, 0.0], "width": 1.0})])
    recs = [_gap_record((2.5, 0.05), 0.9),                    # a hit within 0.5 m and 0.3 m of width -> door
            _gap_record((5.6, 0.0), 1.9),                     # the width misses by 0.7 m -> not the window
            _gap_record((8.0, 0.0), 0.9),                     # the user's correction -> weight 10
            _gap_record((12.0, 0.0), 0.8),                    # a truth wall covers the place -> closed
            _gap_record((16.0, 0.0), 1.0),                    # negated window -> a negative of "window"
            _gap_record((20.0, 0.0), 1.0),                    # nothing -> open
            _gap_record((2.5, 0.0), 0.9, level="L9")]         # a level the truth has not -> left out
    got = RK.label(recs, truth)
    assert len(got) == 6
    assert (got[0]["label"], got[0]["weight"], got[0]["source"]) == ("door", 3.0, "synthetic")
    assert got[1]["label"] == "open" and got[1]["element"] is None       # no element matched at that width
    assert (got[2]["label"], got[2]["weight"], got[2]["source"]) == ("door", 10.0, "user_correction")
    assert (got[3]["label"], got[3]["element"]) == ("closed", "wa")
    assert got[4].get("label") is None and got[4]["negative_of"] == "window" and got[4]["weight"] == 10.0
    assert got[5]["label"] == "open" and got[5]["weight"] == 3.0
    counts = RK.label_counts(got)
    assert counts[DEC.KIND_GAP]["by_source"] == {"synthetic": 4, "user_correction": 2}
    assert counts[DEC.KIND_GAP]["negatives"] == 1


def test_label_join_of_a_pair_with_a_truth_wall():
    truth = _truth(walls=[{"id": "wa", "start": [0.0, 0.0], "end": [5.0, 0.0], "thickness": 0.2}])
    rec = {"kind": DEC.KIND_WALL, "level_id": "L0", "place": [2.0, 0.05], "line": [[1.0, 0.05], [3.0, 0.05]],
           "features": {"length": 2.0}, "rule": "layer_not_chosen", "rule_answer": "notation",
           "rule_confidence": 0.7, "final_answer": "wall", "decided_by": "rule"}
    off = dict(rec, place=[2.0, 0.5], line=[[1.0, 0.5], [3.0, 0.5]])
    got = RK.label([rec, off], truth)
    assert got[0]["label"] == "wall" and got[0]["element"] == "wa"
    assert got[1]["label"] == "notation" and got[1]["element"] is None


# ---------------------------------------------------------------------------------------------------- step 3: learn
def _tiny_table():
    """A separable table: wide gaps with a tag are doors, narrow bare gaps are openings, glass makes a window."""
    names = ["glass_lines", "tag_door_like", "width"]
    rows, labels = [], []
    for w in (0.8, 0.9, 1.0, 1.1):
        rows.append([0.0, 1.0, w])
        labels.append("door")
        rows.append([0.0, 0.0, w - 0.2])
        labels.append("opening")
        rows.append([2.0, 0.0, w + 0.5])
        labels.append("window")
    return {"kind": DEC.KIND_GAP, "features": names, "rows": rows, "labels": labels,
            "negative_of": [None] * len(rows), "weights": [1.0] * len(rows), "projects": ["t"] * len(rows),
            "sources": ["synthetic"] * len(rows)}


def test_the_learner_is_deterministic_and_separates_the_tiny_table():
    table = _tiny_table()
    m1 = RK.fit(table)
    m2 = RK.fit(copy.deepcopy(table))
    assert json.dumps(m1, sort_keys=True) == json.dumps(m2, sort_keys=True)
    assert m1["classes"] == list(RK.CLASSES[DEC.KIND_GAP]) and m1["features"] == table["features"]
    for row, lab in zip(table["rows"], table["labels"]):
        scores = RK.scores_of(m1, dict(zip(table["features"], row)))
        assert max(scores, key=scores.get) == lab
    # a class without an example scores about nothing
    assert m1["intercept"][m1["classes"].index("closed")] == RK.NO_POSITIVES_INTERCEPT
    assert all(abs(v) < 1e-9 for v in m1["coef"][m1["classes"].index("closed")])
    # the stored numbers of this very table (the learner must not drift silently)
    stored = {"door": {"tag_door_like": 1.5820881841, "glass_lines": -0.4581235654, "width": -0.0055080752},
              "window": {"glass_lines": 1.1208742743, "tag_door_like": -0.4605893076, "width": 0.9277180648},
              "opening": {"glass_lines": -0.7336800261, "tag_door_like": -1.1860086751, "width": -0.948409814}}
    for cls, want in stored.items():
        got = dict(zip(m1["features"], m1["coef"][m1["classes"].index(cls)]))
        for name, v in want.items():
            assert got[name] == pytest.approx(v, abs=1e-9), (cls, name, got[name])


def test_a_negative_only_label_teaches_one_classifier():
    table = _tiny_table()
    table["rows"].append([0.0, 1.0, 1.0])
    table["labels"].append(None)
    table["negative_of"].append("door")
    table["weights"].append(10.0)
    table["projects"].append("t")
    table["sources"].append("user_correction")
    m = RK.fit(table)
    base = RK.fit(_tiny_table())
    names = table["features"]
    # the door classifier learnt the negative: that row scores lower as a door than before
    row = dict(zip(names, [0.0, 1.0, 1.0]))
    assert RK.scores_of(m, row)["door"] < RK.scores_of(base, row)["door"]
    # the other classifiers did not see it (only the standardisation did): every decision of the table stands
    for r, lab in zip(_tiny_table()["rows"], _tiny_table()["labels"]):
        s = RK.scores_of(m, dict(zip(names, r)))
        assert max(s, key=s.get) == lab


def test_the_committed_models_reproduce_from_their_committed_tables():
    """The committed model equals a fresh fit of its committed table, bit for bit (no randomness anywhere)."""
    seen = 0
    for kind in RK.CLASSES:
        mp = RK.model_path(kind)
        table = RK.read_table(kind)
        if not mp.is_file() or table is None:
            continue
        seen += 1
        model = json.loads(mp.read_text(encoding="utf-8"))
        fresh = RK.fit(table, l2=model["l2"], iterations=model["iterations"])
        for key in ("features", "mean", "std", "classes", "coef", "intercept"):
            assert fresh[key] == model[key], (kind, key)
        assert model["trained_on"]["rows"] == len(table["rows"])
        assert set(model["trained_on"]["counts_per_source"]) <= set(RK.LABEL_WEIGHTS)
    assert seen >= 1, "no committed model found (python -m wenart.reading_check.ranker train --work DIR writes them)"


# --------------------------------------------------------------------------------------------------- step 4: decide
def _model_saying(kind, answer, share=0.9):
    """A hand-made model whose scores favour ``answer`` by a fixed share whatever the features."""
    classes = list(RK.CLASSES[kind])
    return {"kind": kind, "features": ["width"], "mean": [0.0], "std": [1.0], "classes": classes,
            "coef": [[0.0] for _ in classes],
            "intercept": [10.0 if c == answer else -10.0 + (0.0 if c != "opening" else 2.0) for c in classes],
            "l2": 1.0, "iterations": 1}


def test_decide_trusts_the_rule_decides_above_the_margin_and_falls_back_without_a_model():
    model = _model_saying(DEC.KIND_GAP, "door")
    scores = RK.scores_of(model, {"width": 0.9})
    assert scores["door"] > 0.9
    # the rule is trusted at or above RULE_TRUST
    assert RK.decide(DEC.KIND_GAP, {"width": 0.9}, "window", 0.6, model=model)[:2] == ("window", "rule")
    # a weak rule: the ranker decides with its margin
    answer, by, margin, got = RK.decide(DEC.KIND_GAP, {"width": 0.9}, "opening", 0.5,
                                        allowed=["door", "window", "opening"], model=model)
    assert (answer, by) == ("door", "ranker") and margin >= RK.MARGIN_MIN and got == scores
    # a weak ranker (two classes tied) leaves the rule's answer
    tied = _model_saying(DEC.KIND_GAP, "door")
    tied["intercept"][tied["classes"].index("window")] = 10.0
    answer, by, margin, _ = RK.decide(DEC.KIND_GAP, {"width": 0.9}, "opening", 0.5,
                                      allowed=["door", "window", "opening"], model=tied)
    assert (answer, by) == ("opening", "rule") and margin < RK.MARGIN_MIN


def test_without_a_model_file_the_rules_alone_decide(monkeypatch, tmp_path):
    """A missing model file means the rules alone, never an error; the lookup is cached per process."""
    RK.reset_models()
    assert RK.load_model(DEC.KIND_GAP, tmp_path) is None                 # an empty models folder
    monkeypatch.setattr(RK, "load_model", lambda kind, models_dir=None: None)
    assert RK.decide(DEC.KIND_GAP, {"width": 0.9}, "opening", 0.2, allowed=["door", "opening"]) == \
        ("opening", "rule", 0.0, {})
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    out_walls, openings, gap_log, records = _read(walls, [], ranker=True)
    assert [o.kind for o in openings] == ["opening"]
    rec = [r for r in records if r["kind"] == DEC.KIND_GAP][0]
    assert rec["decided_by"] == "rule" and "scores" not in rec
    RK.reset_models()


def test_hard_constraints_are_never_overridden():
    """A swing arc is a door; a gap wider than its run is never a door; an end gap makes no element; closed and open
    are never the ranker's answers; a dimension-layer pair is never a wall."""
    rec = _gap_record((2.0, 0.0), 0.9)
    rec["features"].update(arcs_swing=1)
    rec.update(rule="door_swing_arc", rule_answer="door", rule_confidence=0.95)
    assert RK.allowed_answers(rec) == ["door"]
    wide = _gap_record((2.0, 0.0), 2.5)
    wide["features"]["run_length"] = 2.0
    assert "door" not in RK.allowed_answers(wide) and "opening" in RK.allowed_answers(wide)
    end = _gap_record((2.0, 0.0), 0.9)
    end["gap"] = "end"
    assert RK.allowed_answers(end) == ["opening"]
    plain = _gap_record((2.0, 0.0), 0.9)
    assert set(RK.allowed_answers(plain)) == {"door", "window", "opening"}
    model = _model_saying(DEC.KIND_GAP, "closed")
    answer, by, _m, _s = RK.decide(DEC.KIND_GAP, plain["features"], "opening", 0.5,
                                   allowed=RK.allowed_answers(plain), model=model)
    assert (answer, by) == ("opening", "rule")
    pair = {"kind": DEC.KIND_WALL, "features": {"role_dimension": True, "length": 1.0}, "rule_answer": "notation"}
    assert RK.allowed_answers(pair) == ["notation"]
    pair["features"] = {"in_axis_grid": True}
    assert RK.allowed_answers(pair) == ["notation"]


def test_the_ranker_retypes_a_bare_gap_in_the_classifier_and_logs_it(monkeypatch):
    """A bare 0.9 m gap (doorless, 0.5) under a model that says door: the gap becomes an unverified door with the
    margin as its confidence, ``decided_by`` in its evidence, the record and the gap log; a gap wider than its run
    stays what the rule said."""
    monkeypatch.setattr(RK, "load_model", lambda kind, models_dir=None: _model_saying(DEC.KIND_GAP, "door"))
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    out_walls, openings, gap_log, records = _read(walls, [], ranker=True)
    assert [o.kind for o in openings] == ["door"]
    d = openings[0]
    assert d.status == "unverified" and d.evidence["method"] == "inferred" and d.evidence["decided_by"] == "ranker"
    assert d.evidence["confidence"] <= O.CONF_DOORLESS and d.evidence["margin"] >= RK.MARGIN_MIN
    assert d.swing_point is None and d.width == pytest.approx(0.9)
    rec = [r for r in records if r["kind"] == DEC.KIND_GAP][0]
    assert rec["decided_by"] == "ranker" and rec["ranker_answer"] == "door" and rec["rule_answer"] == "opening"
    assert rec["final_answer"] == "door" and rec["scores"]["door"] > 0.9
    entry = [e for e in gap_log if e["kind"] == "run"][0]
    assert entry["class"] == "door" and entry["decided_by"] == "ranker" and entry["rule_class"] == "empty"
    # the same gap with a swing arc: the rule (door_swing_arc 0.95) stands whatever the model says; the element keeps
    # the openings reader's own confidence (an arc without a leaf: CONF_DOOR)
    monkeypatch.setattr(RK, "load_model", lambda kind, models_dir=None: _model_saying(DEC.KIND_GAP, "window"))
    out_walls, openings, gap_log, records = _read(walls, _door((2.88, 0.08), 0.88, 180, 90), ranker=True)
    assert [o.kind for o in openings] == ["door"] and openings[0].evidence["confidence"] == O.CONF_DOOR
    assert openings[0].evidence["method"] == "vector" and "decided_by" not in openings[0].evidence
    rec = [r for r in records if r["kind"] == DEC.KIND_GAP][0]
    assert rec["decided_by"] == "rule"
    # an end gap stays bare: no element from the ranker
    end_walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, -2), (2.9, 2))]
    monkeypatch.setattr(RK, "load_model", lambda kind, models_dir=None: _model_saying(DEC.KIND_GAP, "door"))
    out_walls, openings, gap_log, records = _read(end_walls, [], ranker=True)
    assert openings == []
    assert all(r["decided_by"] == "rule" for r in records if r["kind"] == DEC.KIND_GAP)


# ------------------------------------------------------------------------------------------------------ end to end
@pytest.mark.skipif(not RK.model_path(DEC.KIND_GAP).is_file(), reason="no committed gap_kind model")
def test_synthetic_12_bare_gaps_of_the_mirrored_flat_become_doors_by_the_ranker(tmp_path):
    """synthetic-12 (mirrored halves, UL276): the unlabelled flat's four door gaps are drawn without swings; the
    cascade calls them doorless (0.5) and the pipeline made three openings and a window of them. With the committed
    model the ranker re-types them (their mirror twins are drawn doors, no label stands beside them): the reading has
    the truth's 8 doors, each ranker door is unverified with decided_by in its evidence, the gap log and the decision
    records say so with the margin, and the records file is written per level. (The committed model has seen this
    project's labels; the held-out number is in the model's metrics.)"""
    from wenart.ingest import pipeline as PL

    out = tmp_path / "s12"
    building, _ = PL.run_project(REPO / "projects" / "synthetic-12-mirrored-halves", out, no_ai=True)
    doors = [o for o in building["openings"] if o["type"] == "door"]
    assert len(doors) == 8 and not [o for o in building["openings"] if o["type"] == "opening"]
    by_ranker = [o for o in doors if any(e.get("decided_by") == "ranker" for e in o["evidence"])]
    assert len(by_ranker) == 4
    for o in by_ranker:
        ev = next(e for e in o["evidence"] if e.get("decided_by") == "ranker")
        assert o["status"] == "unverified" and ev["method"] == "inferred" and ev["rule"] == "ranker"
        assert RK.MARGIN_MIN <= ev["margin"] and ev["confidence"] <= O.CONF_DOORLESS
        assert o["center"][0] > 7.0                           # the right (unlabelled) flat
    records = json.loads((out / "reading_check" / "decisions_L0.json").read_text(encoding="utf-8"))
    ranked = [r for r in records["records"] if r["kind"] == DEC.KIND_GAP and r["decided_by"] == "ranker"]
    assert len(ranked) == 4 and all(r["ranker_answer"] == "door" and r["margin"] >= RK.MARGIN_MIN for r in ranked)
    assert all(r["features"]["twin_door"] is True and r["rule"] == "doorless" for r in ranked)
    assert records["summary"]["gap_kind"]["decided_by"]["ranker"] == 4
    report = (out / "report.md").read_text(encoding="utf-8")
    assert report.count("the ranker decided door") == 4        # never silent: one page note per ranker decision
