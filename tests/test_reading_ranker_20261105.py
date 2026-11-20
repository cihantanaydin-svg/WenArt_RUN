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


def test_a_sparse_truth_labels_only_what_its_entries_cover():
    """6 Nov 2026 (the user: "Only consider my revision with the screenshot I have given into previous projects others
    I have not seen"): a real project's truth holds only the user's records; nothing there means "not seen", so a gap
    or a pair no entry covers gets no label, an entry gives its class, and a negated wall across a gap is a negative of
    closed."""
    truth = _truth(doors=[{"id": "u1", "center": [2.45, 0.0], "width": 0.9, "source": "user_correction"}],
                   absent=[("walls", {"id": "u2", "start": [10.0, 0.0], "end": [14.0, 0.0], "thickness": 0.2})])
    truth.update(source="user_corrections", sparse=True)
    recs = [_gap_record((2.5, 0.05), 0.9), _gap_record((12.0, 0.0), 0.8), _gap_record((20.0, 0.0), 1.0)]
    pair = {"kind": DEC.KIND_WALL, "level_id": "L0", "place": [30.0, 0.0], "line": [[29.0, 0.0], [31.0, 0.0]],
            "features": {}, "rule": "layer_not_chosen", "rule_answer": "notation", "rule_confidence": 0.7,
            "final_answer": "notation", "decided_by": "rule"}
    got = RK.label(recs + [pair], truth)
    assert [(g.get("label"), g.get("negative_of"), g["weight"]) for g in got] == \
        [("door", None, 10.0), (None, "closed", 10.0)]
    # the same truth, complete: nothing there is open air, an uncovered pair notation
    truth["sparse"] = False
    assert [g.get("label") for g in RK.label(recs + [pair], truth)] == ["door", None, "open", "notation"]


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
    m1 = RK.fit(table, l2=1.0)                    # the stored numbers below were fitted at ridge 1
    m2 = RK.fit(copy.deepcopy(table), l2=1.0)
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
    m = RK.fit(table, l2=1.0)
    base = RK.fit(_tiny_table(), l2=1.0)
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
@pytest.fixture(scope="module")
def s12_reading(tmp_path_factory):
    """synthetic-12 read once with the committed models (the ranker on)."""
    from wenart.ingest import pipeline as PL

    out = tmp_path_factory.mktemp("s12")
    building, _ = PL.run_project(REPO / "projects" / "synthetic-12-mirrored-halves", out, no_ai=True)
    return building, out


@pytest.mark.skipif(not RK.model_path(DEC.KIND_GAP).is_file(), reason="no committed gap_kind model")
def test_synthetic_12_bare_door_gaps_are_numbered_places_with_the_rankers_answer(s12_reading):
    """synthetic-12 (mirrored halves, UL276): the unlabelled flat's four door gaps are drawn without swings; the
    cascade calls them doorless (0.5). On the merged reader the committed model scores them door (their mirror twins
    are drawn doors) but changes nothing: doorless->door is no trusted transition and one gap's margin is weak. The
    three the built level still holds as openings are low-confidence places with the ranker's answer and the reason,
    numbered by RC7, and the building stays valid (status ok: the schema knows undecided_gap)."""
    building, out = s12_reading
    assert building["status"] == "ok"
    records = json.loads((out / "reading_check" / "decisions_L0.json").read_text(encoding="utf-8"))
    bare = [r for r in records["records"] if r["kind"] == DEC.KIND_GAP and r["rule"] == "doorless"
            and r["place"][0] > 7.0]
    assert len(bare) == 4
    for r in bare:
        assert r["decided_by"] == "rule" and r["features"]["twin_door"] is True and r["scores"]["door"] > 0.5
        assert r["low_confidence"] and r["final_answer"] in ("opening", "window")
    assert sum(1 for r in bare if r.get("ranker_untrusted") == "door") == 3
    # 6 Nov 2026 (review): the places come from the built level; the gap at (10.00, 8.88) is a window there (a later
    # pass typed it), so it is resolved and no place; its final answer says so, the core's stays beside it
    resolved = [r for r in bare if r["final_answer"] == "window"]
    assert [tuple(round(v, 1) for v in r["place"]) for r in resolved] == [(10.0, 8.9)]
    assert resolved[0]["core_final_answer"] == "opening"
    places = [p for lv in building["levels"] for p in lv.get("reading_places") or []]
    assert sorted((round(p["at"][0], 1), round(p["at"][1], 1)) for p in places if p["kind"] == "undecided_gap") == \
        [(9.0, 6.0), (10.0, 4.6), (11.0, 6.0)]
    assert all(p["text"] == "opening" for p in places)
    rc = json.loads((out / "reading_check" / "reading_check.json").read_text(encoding="utf-8"))
    assert sum(1 for f in rc["findings"] if f.get("check") == "RC7" and f.get("kind") == "undecided_gap") == 3
    assert records["summary"]["gap_kind"]["low_confidence"] == 4 and records["summary"]["final_changed_after_core"] >= 1


@pytest.mark.xfail(strict=True, reason="failure class mirrored_halves (UL276): the ranker v1 does not re-type the "
                                       "unlabelled flat's bare door gaps (doorless->door untrusted on the merged reader)")
def test_synthetic_12_bare_door_gaps_become_doors(s12_reading):
    building, _out = s12_reading
    doors = [o for o in building["openings"] if o["type"] == "door"]
    assert len(doors) == 8 and not [o for o in building["openings"] if o["type"] == "opening"]


# ------------------------------------------------------------------------------------------- the transition trust
def test_transition_trust_needs_enough_right_held_out_changes():
    changed = ([{"rule": "doorless", "ranker_answer": "door", "right": True}] * 3
               + [{"rule": "doorless", "ranker_answer": "door", "right": False}]
               + [{"rule": "unclassified", "ranker_answer": "door", "right": r} for r in (True, False, False, False)]
               + [{"rule": "unclassified", "ranker_answer": "window", "right": True}] * 2)
    trust = RK.transition_trust(changed)
    assert trust["doorless->door"] == {"right": 3, "wrong": 1, "trusted": True}           # 3 of 4 >= 0.6
    assert trust["unclassified->door"]["trusted"] is False                              # 1 of 4
    assert trust["unclassified->window"]["trusted"] is False                            # 2 < TRANSITION_MIN


def test_decide_applies_only_a_trusted_transition_and_an_agreeing_ranker_decides_nothing():
    model = _model_saying(DEC.KIND_GAP, "door")
    model["transitions"] = {"doorless->door": {"right": 3, "wrong": 0, "trusted": True},
                            "unclassified->door": {"right": 1, "wrong": 3, "trusted": False}}
    allowed = ["door", "window", "opening"]
    assert RK.decide(DEC.KIND_GAP, {}, "opening", 0.5, allowed=allowed, model=model, rule="doorless")[:2] == \
        ("door", "ranker")
    got = RK.decide(DEC.KIND_GAP, {}, "opening", 0.2, allowed=allowed, model=model, rule="unclassified")
    assert got[:2] == ("opening", "rule") and got[2] >= RK.MARGIN_MIN
    assert RK.untrusted_change(model, "unclassified", "opening", 0.2, got[3], got[2], allowed) == "door"
    # an agreeing ranker: the rule built the element
    assert RK.decide(DEC.KIND_GAP, {}, "door", 0.5, allowed=allowed, model=model, rule="door_sliding_leaf")[:2] == \
        ("door", "rule")


def test_the_margin_counts_every_class_not_only_the_allowed_answers():
    """real10's 1.8 m doorless gap on the mirror axis (6 Nov 2026): door 0.43, closed 0.29 (not allowed), opening a
    few percent. Among the allowed answers alone the margin was 0.31; against every class it is 0.14: no decision."""
    scores = {"door": 0.4281, "window": 0.1203, "opening": 0.0339, "closed": 0.285, "open": 0.1327}
    top, margin = RK.top_and_margin(scores, ["door", "window", "opening"])
    assert top == "door" and margin == pytest.approx(0.1431, abs=1e-4)
    assert RK.top_and_margin({"door": 0.74, "closed": 0.17, "window": 0.09}, ["door", "window", "opening"]) == \
        ("door", 0.57)
    # the best allowed answer below a disallowed class gives a negative margin
    assert RK.top_and_margin({"closed": 0.7, "door": 0.2, "window": 0.1}, ["door", "window"])[1] < 0


def test_an_untrusted_change_is_recorded_and_becomes_a_low_confidence_place(monkeypatch):
    model = _model_saying(DEC.KIND_GAP, "door")
    model["transitions"] = {}
    monkeypatch.setattr(RK, "load_model", lambda kind, models_dir=None: model)
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    log = DEC.DecisionLog("L0", ranker=True)
    out_walls, openings, gap_log, owned = O.gaps_and_openings(walls, [], "t.pdf", 1, decisions=log)
    records = log.finalize((0.0, 0.0), out_walls, openings)
    assert [o.kind for o in openings] == ["opening"]
    rec = [r for r in records if r["kind"] == DEC.KIND_GAP][0]
    assert rec["decided_by"] == "rule" and rec["ranker_untrusted"] == "door"
    assert "not been shown" in rec["low_confidence"]
    places = DEC.places_from_records(records)
    assert len(places) == 1 and places[0]["kind"] == "undecided_gap" and places[0]["at"] == pytest.approx([2.45, 0.0])
    assert places[0]["text"] == "opening"


def test_places_and_final_answers_come_from_the_built_level():
    """6 Nov 2026 (review): a later pass that types the gap (a facade gap's window) or removes it (an opening to the
    soil) resolves it: no place; the final answer is what the final building holds; a dropped candidate stays."""
    rec = {"kind": DEC.KIND_GAP, "place": [2.45, 0.0], "features": {"width": 0.9}, "rule": "unclassified",
           "rule_answer": "opening", "rule_confidence": 0.2, "final_answer": "opening", "low_confidence": "weak"}
    dropped = dict(rec, place=[8.0, 0.0], final_answer=DEC.DROPPED)
    wall = {"kind": DEC.KIND_WALL, "place": [5.0, 0.0], "line": [[4.0, 0.0], [6.0, 0.0]], "features": {},
            "rule": "layer_not_chosen", "rule_answer": "notation", "final_answer": "notation"}
    walls = [{"start": [0.0, 0.0], "end": [10.0, 0.0], "thickness": 0.2}]
    # the facade-gap pass made it a window
    records = [dict(rec), dict(dropped), dict(wall)]
    n = DEC.final_answers_from_building(records, walls, [{"type": "window", "center": [2.45, 0.0], "width": 0.9}])
    assert n == 2 and records[0]["final_answer"] == "window" and records[0]["core_final_answer"] == "opening"
    assert records[1]["final_answer"] == DEC.DROPPED and records[2]["final_answer"] == "wall"
    assert DEC.places_from_records(records) == []
    # the underground pass removed it and closed the wall: closed, no place
    records = [dict(rec)]
    DEC.final_answers_from_building(records, walls, [])
    assert records[0]["final_answer"] == "closed" and DEC.places_from_records(records) == []
    # still the weak opening: a place that says so
    records = [dict(rec)]
    DEC.final_answers_from_building(records, walls, [{"type": "opening", "center": [2.45, 0.0], "width": 0.9}])
    assert DEC.places_from_records(records)[0]["text"] == "opening"


def test_lopo_reports_the_nested_trusted_accuracy():
    """Three projects whose bare gaps are doors where a twin says so: held out, each project's changes count only when
    a transition is trusted by models trained without it (two levels: without it and without the scored project)."""
    rows = []
    for p in ("a", "b", "c"):
        for k in range(6):
            twin = k % 2 == 0
            rows.append({"kind": DEC.KIND_GAP, "project": p, "level_id": "L0", "place": [k, 0.0], "gap": "run",
                         "features": {"twin_door": twin, "width": 0.9, "run_length": 9.0, "glass_lines": 0},
                         "rule": "doorless", "rule_answer": "opening", "rule_confidence": 0.5,
                         "label": "door" if twin else "opening", "weight": 3.0, "source": "synthetic"})
    res = RK.lopo(rows, DEC.KIND_GAP, l2=1.0)
    for p in ("a", "b", "c"):
        m = res["per_project"][p]
        assert m["rules_acc"] == 0.5 and m["integrated_acc"] == 1.0          # the ranker learns the twin
        assert m["trusted_acc"] == 1.0                                         # 3 of 3 changes of an inner model
    assert all(c["rule"] == "doorless" and c["right"] for c in res["changed"])
    assert RK.transition_trust(res["changed"])["doorless->door"]["trusted"] is True
    assert res["overall"]["nested_trusted_in_groups"] == {"doorless->door": 3}
    # with two projects only, nothing is left to earn a held-out trust at the second level
    two = RK.lopo([r for r in rows if r["project"] != "c"], DEC.KIND_GAP, l2=1.0)
    assert all(two["per_project"][p]["trusted_acc"] == 0.5 for p in ("a", "b"))


def test_the_ranker_is_a_subcommand_and_the_models_say_why_a_change_needs_trust(capsys):
    from wenart.reading_check import __main__ as M

    assert M.DELEGATED["ranker"] == ("wenart.reading_check.ranker", "main")
    assert M.main(["ranker", "explain"]) == 0
    assert "gap_kind:" in capsys.readouterr().out
    for kind in RK.CLASSES:
        if RK.model_path(kind).is_file():
            note = json.loads(RK.model_path(kind).read_text(encoding="utf-8"))["note"]
            assert "26 decisions" in note and "2 of its 8" in note
    assert "26 decisions" in RK.decide.__doc__ and "2 of its 8" in RK.decide.__doc__


def test_no_typical_floor_feature_is_recorded():
    """A level a typical floor plan stands for reads that plan's extraction again, so its answer is the record's own:
    no feature of it is written (a leak, not a second opinion)."""
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    out_walls, openings, gap_log, records = _read(walls, [])
    assert not any(k.startswith("typical") for r in records for k in r["features"])


def _row(project, k, door, *, label=None, negative_of=None, f=None):
    feats = {"f": 1.0 if door else 0.0, "width": 0.9, "run_length": 9.0} if f is None else f
    return {"kind": DEC.KIND_GAP, "project": project, "level_id": "L0", "place": [float(k), 0.0], "gap": "run",
            "features": feats, "rule": "unclassified", "rule_answer": "opening", "rule_confidence": 0.2,
            "label": label if label is not None or negative_of else ("door" if door else "opening"),
            "negative_of": negative_of, "weight": 3.0, "source": "synthetic"}


def test_fit_takes_an_empty_table_and_one_without_negative_of():
    """6 Nov 2026 (review): ``labels`` was read before it was bound."""
    m = RK.fit({"kind": DEC.KIND_GAP, "features": ["width"], "rows": [[0.9], [2.0]], "labels": ["door", "opening"],
                "weights": [1.0, 1.0]})
    assert m["classes"] == list(RK.CLASSES[DEC.KIND_GAP])
    empty = RK.fit({"kind": DEC.KIND_GAP, "features": ["width"], "rows": [], "labels": [], "negative_of": [],
                    "weights": []})
    assert empty["mean"] == [0.0] and empty["std"] == [1.0]
    assert all(b == RK.NO_POSITIVES_INTERCEPT for b in empty["intercept"])


def test_a_width_less_user_negation_joins_by_its_centre():
    """real04's two user negations (C0059) name only a place: they join by the score's centre rule."""
    truth = _truth(absent=[("windows", {"id": "w-no", "center": [2.335, 7.094], "width": None})])
    got = RK.label([_gap_record((2.4, 7.1), 1.2)], truth)
    assert got[0].get("negative_of") == "window" and got[0]["weight"] == 10.0
    far = RK.label([_gap_record((2.8, 7.1), 1.2)], truth)                 # 0.47 m off: beyond OPENING_CENTER_M
    assert far[0].get("negative_of") is None


def test_real02_and_real04_are_held_out_together():
    assert RK.group_of("real02") == RK.group_of("real04") == "real02+real04"
    assert RK.group_of("real06") == "real06"
    rows = [_row(p, k, k % 2 == 0) for p in ("real02", "real04", "a", "b") for k in range(6)]
    res = RK.lopo(rows, DEC.KIND_GAP, l2=1.0, nested=False)
    assert res["per_project"]["real02"]["group"] == res["per_project"]["real04"]["group"] == "real02+real04"
    assert res["groups"] == ["a", "b", "real02+real04"]


def test_a_change_into_a_negated_class_is_a_wrong_change():
    """6 Nov 2026 (review): a user's negation has no class of its own, but a held-out change INTO the negated class is
    wrong, in the changes and in the trust."""
    model = _model_saying(DEC.KIND_GAP, "door")
    rows = [_row("p", 0, True, negative_of="door", label=None)]
    rows[0]["source"] = "user_correction"
    m = RK._accuracy(rows, model)
    assert m["n"] == 0 and m["corrections"]["negatives"] == 1 and m["corrections"]["changed_into_negation"] == 1
    assert len(m["changed"]) == 1 and m["changed"][0]["right"] is False and m["changed"][0]["negative"] is True
    assert RK.transition_trust(m["changed"])["unclassified->door"] == {"right": 0, "wrong": 1, "trusted": False}


def test_the_nested_trust_is_held_out_at_two_levels():
    """Only projects A and B draw the door rows. Held out at one level, A's trust would come from B's changes, made by a
    model trained on A's rows (right, trusted). At two levels the models that earn A's trust are trained without A:
    with B held out too, nothing teaches door, no change, no trust, and A's trusted accuracy stays the rules'."""
    rows = [_row(p, k, True) for p in ("A", "B") for k in range(4)]
    rows += [_row(p, k, False) for p in ("C", "D") for k in range(4)]
    res = RK.lopo(rows, DEC.KIND_GAP, l2=1.0)
    a = res["per_project"]["A"]
    assert a["rules_acc"] == 0.0 and a["integrated_acc"] == 1.0          # the held-out ranker gets A right ...
    assert a["trusted_acc"] == 0.0                                         # ... but no trust is earned without A
    one_level = RK.transition_trust([c for c in res["changed"] if c["project"] != "A"])
    assert one_level["unclassified->door"]["trusted"] is True             # the old, one-level estimate trusted it
    # only C and D (no door rows of their own) find the transition trusted, from models trained on A and B
    assert res["overall"]["nested_trusted_in_groups"] == {"unclassified->door": 2}


def test_rc7_numbers_an_undecided_gap_with_its_own_words():
    import wenart.reading_check as RCK

    b = {"levels": [{"id": "L0", "label": "Zemin", "reading_places": [
        {"kind": "undecided_gap", "text": "opening", "at": [2.45, 0.0], "note": "rule unclassified at 0.20 and ..."}]}],
        "walls": []}
    got = RCK.low_confidence_findings(b)
    assert len(got) == 1 and got[0]["severity"] == "minor"
    assert "gap at (2.45, 0.00) m kept as opening on weak evidence" in got[0]["message"]
