"""The derived truth, review of 6 Nov 2026 (7,596 property cases and 64 command-line and data cases, each finding
checked by two refuters; 18 confirmed edge findings, grouped by the session organizer into 16 items). Each item is a
test here. CPU, pure (the command line in a temp folder)."""
from __future__ import annotations

import argparse
import copy
import itertools
import json
from pathlib import Path

import pytest

from tests.test_truth_derived_20261106 import _acc, _rec, cli  # noqa: F401 - cli is a fixture
from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

ROOT = Path(__file__).resolve().parents[1]
RECORDS = TR.load_corrections()


def _sq(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _real(project):
    acc, why = TR.accepted_of(project)
    assert acc is not None, why
    return acc


def _body(truth):
    return TR.dumps({"levels": truth["levels"], "per_level": truth["per_level"]})


def _walls_read(*walls):
    read = {"levels": [{"id": "L0"}], "per_level": {"L0": {t: [] for t in TR.ELEMENT_TYPES}}}
    read["per_level"]["L0"]["walls"] = [dict(w, id=f"w{i}") for i, w in enumerate(walls)]
    return read


# --- 1. an unmatched operation changes nothing; the store's check reads the fields --------------------------------

@pytest.mark.parametrize("op", [
    {"op": "remove", "kind": "window", "level": "L0", "center": [0.326, 6.725], "width": "1,6"},
    {"op": "add", "kind": "door", "level": "L0", "center": [0.326, 6.725], "width": "1,6"},
    {"op": "remove", "kind": "stair", "level": "L0", "center": [4.676, 12.938], "size": "2.2x2.7"},
    {"op": "add", "kind": "door", "level": "L0", "center": ["0.326", 6.725]},
    {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0], "end": [4, 0], "thickness": -0.2},
])
def test_01_an_operation_reported_unmatched_changes_nothing(op):
    acc = _real("real06")
    base = TR.build_truth("real06", acc, [])
    rec = _rec("C9001", op, project="real06")
    t = TR.build_truth("real06", acc, [rec])
    assert [u["record"] for u in t["build_report"]["unmatched"]] == ["C9001"] and not t["build_report"]["applied"]
    assert "refused" in t["build_report"]["unmatched"][0]["why"]
    assert _body(t) == _body(base)
    errs = TR.correction_errors([dict(rec, place={"x": 1.0, "y": 1.0})], [], ["real06"])
    assert len(errs) == 1 and "truth_action operation 1" in errs[0]


def test_01_a_failure_inside_an_operation_puts_its_level_back(monkeypatch):
    acc = _real("real06")
    base = TR.build_truth("real06", acc, [])

    def broken(self, rec, op, entry, unmatched, lv, kind, t):
        lv["windows"].clear()                         # half done ...
        raise ValueError("boom")                      # ... then fails
    monkeypatch.setattr(TR._Replay, "_point", broken)
    t = TR.build_truth("real06", acc, [_rec("C9001", {"op": "remove", "kind": "window", "level": "L0",
                                                      "center": [0.326, 6.725]}, project="real06")])
    assert t["build_report"]["unmatched"][0]["why"] == "the operation could not be applied: boom"
    assert _body(t) == _body(base)


# --- 2. no correction creates a level ----------------------------------------------------------------------------

@pytest.mark.parametrize("project", ["real04", "real06", "real07", "real10"])
def test_02_a_level_add_never_creates_a_level(project):
    acc = _real(project)
    ops = [{"op": "add", "kind": "level", "level": "L99", "label": "Ghost"},
           {"op": "add", "kind": "room", "level": "L99", "polygon": _sq(0, 0, 3, 3), "label": "Oda"}]
    t = TR.build_truth(project, acc, [_rec("C9001", *ops, project=project)])
    assert "L99" not in [lv["id"] for lv in t["levels"]] and "L99" not in t["per_level"]
    assert [u["n"] for u in t["build_report"]["unmatched"]] == [1, 2]
    assert "accept the reading first" in t["build_report"]["unmatched"][0]["why"]


def test_02_a_left_out_level_stays_out_and_no_record_adds_a_level():
    acc = _real("real17")
    ops = [{"op": "add", "kind": "level", "level": "L0", "label": "Zemin Kat"},
           {"op": "add", "kind": "door", "level": "L0", "center": [9.152, 9.505], "width": 0.9}]
    t = TR.build_truth("real17", acc, [_rec("C9001", *ops, project="real17")])
    assert [lv["id"] for lv in t["levels"]] == ["L-1"] and SC.match(t, acc)["total"] == 100.0
    # the store holds no level operation today
    assert not [r["id"] for r in RECORDS for op in TR.record_ops(r) if op.get("kind") == "level"]


def test_02_the_command_line_refuses_a_new_level(cli):
    code, msg = cli(kind="level", level="L9", label="L9", text="there is a ninth floor")
    assert code == 2 and "accept the reading first" in msg and cli.truth() is None and len(cli.records()) == 3


# --- 3. a room operation by polygon: the overlap decides -----------------------------------------------------------

@pytest.mark.parametrize("what", ["remove", "retype", "add"])
def test_03_a_polygon_names_the_room_it_covers_not_a_neighbour_of_the_same_label(what):
    acc = _acc({"L0": {"rooms": [{"id": "r_wc", "label": "WC", "room_type": "bathroom", "polygon": _sq(0, 0, 1, 1)},
                                 {"id": "r_oda", "label": "Oda", "room_type": "bedroom",
                                  "polygon": _sq(1, 0, 2, 1)}]}})
    t = TR.build_truth("p", acc, [_rec("C9001", {"op": what, "kind": "room", "level": "L0", "label": "Oda",
                                                 "polygon": _sq(0, 0, 1, 1)})])
    rooms = {e["reader_id"]: e for e in t["per_level"]["L0"]["rooms"] if e.get("reader_id")}
    assert rooms["r_oda"]["source"] == TR.SOURCE_ACCEPTED and not rooms["r_oda"].get("absent")
    wc = rooms["r_wc"]
    assert wc.get("corrections") == ["C9001"]
    if what == "remove":
        assert wc["absent"] and wc["polygon"] == _sq(0, 0, 1, 1)
    else:
        assert wc["label"] == "Oda" and not wc.get("absent")


def test_03_on_real10_the_polygon_of_the_wc_names_the_wc():
    acc = _real("real10")
    base = TR.build_truth("real10", acc, [])
    wc = next(e for e in base["per_level"]["L6"]["rooms"] if e.get("reader_id") == "r_L6_oda_6")
    t = TR.build_truth("real10", acc, [_rec("C9001", {"op": "retype", "kind": "room", "level": "L6", "label": "Oda",
                                                      "polygon": wc["polygon"]}, project="real10")])
    got = next(e for e in t["per_level"]["L6"]["rooms"] if e["id"] == wc["id"])
    assert got["label"] == "Oda" and got["corrections"] == ["C9001"]
    assert all(e.get("source") == TR.SOURCE_ACCEPTED for e in t["per_level"]["L6"]["rooms"] if e["id"] != wc["id"])


# --- 4, 5. a user's wall covers its span; one wall on one line -----------------------------------------------------

def test_04_a_wall_add_longer_than_the_drawn_wall_extends_it():
    acc = _acc({"L0": {"walls": [{"id": "w1", "start": [0, 0], "end": [1, 0], "thickness": 0.2}]}})
    t = TR.build_truth("p", acc, [_rec("C9001", {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0],
                                                 "end": [10, 0], "thickness": 0.2})])
    walls = t["per_level"]["L0"]["walls"]
    assert [(w["start"], w["end"]) for w in walls] == [([0.0, 0.0], [10.0, 0.0])]
    assert t["build_report"]["applied"][0]["state"] == "extended" and walls[0]["corrections"] == ["C9001"]
    assert SC.match(t, _walls_read({"start": [0, 0], "end": [10, 0], "thickness": 0.2}))["walls"]["f1"] == 1.0


def test_04_a_wall_add_over_a_gap_joins_the_walls_and_closes_it():
    acc = _acc({"L0": {"walls": [{"id": "w1", "start": [0, 0], "end": [3, 0], "thickness": 0.2},
                                 {"id": "w2", "start": [5, 0], "end": [8, 0], "thickness": 0.2}]}})
    t = TR.build_truth("p", acc, [_rec("C9001", {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0],
                                                 "end": [8, 0], "thickness": 0.2})])
    walls = t["per_level"]["L0"]["walls"]
    assert [(w["start"], w["end"]) for w in walls] == [([0.0, 0.0], [8.0, 0.0])]
    assert t["build_report"]["applied"][0] == {"record": "C9001", "n": 1, "op": "add", "kind": "wall", "level": "L0",
                                               "place": [0.0, 0.0], "state": "joined",
                                               "changed": ["end", "joined", "start"], "joined": 1}
    closed = _walls_read({"start": [0, 0], "end": [8, 0], "thickness": 0.2})
    gap = _walls_read({"start": [0, 0], "end": [3, 0], "thickness": 0.2}, {"start": [5, 0], "end": [8, 0],
                                                                         "thickness": 0.2})
    assert SC.match(t, closed)["total"] == 100.0 and SC.match(t, gap)["total"] < 100.0


def test_04_a_drawn_piece_inside_the_wall_and_a_column_beside_it_stay():
    """real10 L-2's case (C0068): a 0.2 m piece inside the outer wall, on its line, and thick column pieces 0.07 to
    0.14 m off its line stay as drawn when the user confirms the outer wall."""
    acc = _acc({"L0": {"walls": [{"id": "outer", "start": [2.831, 16.57], "end": [19.551, 16.57], "thickness": 0.32},
                                 {"id": "piece", "start": [13.111, 16.55], "end": [13.271, 16.55], "thickness": 0.28},
                                 {"id": "col", "start": [10.011, 16.435], "end": [12.371, 16.435],
                                  "thickness": 0.6}]}})
    t = TR.build_truth("p", acc, [_rec("C0068", {"op": "add", "kind": "wall", "level": "L0", "start": [2.8311, 16.57],
                                                 "end": [19.5511, 16.57], "thickness": 0.32})])
    assert len(t["per_level"]["L0"]["walls"]) == 3 and t["build_report"]["applied"][0]["state"] == "confirmed"


def test_05_a_wall_add_of_another_thickness_on_a_drawn_wall_is_that_wall():
    acc = _acc({"L0": {"walls": [{"id": "w1", "start": [0, 0], "end": [4, 0], "thickness": 0.2}]}})
    t = TR.build_truth("p", acc, [_rec("C9001", {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0],
                                                 "end": [4, 0], "thickness": 0.3})])
    walls = t["per_level"]["L0"]["walls"]
    assert [(w["thickness"], w["source"]) for w in walls] == [(0.3, TR.SOURCE_USER)]
    assert t["build_report"]["applied"][0]["changed"] == ["thickness"]
    assert SC.match(t, _walls_read({"start": [0, 0], "end": [4, 0], "thickness": 0.3}))["total"] == 100.0


# --- 6. overlapping negated spans are one negation ------------------------------------------------------------------

def test_06_overlapping_negated_spans_make_their_union():
    acc = _acc({"L0": {"walls": [{"id": "w1", "start": [0, 0], "end": [10, 0], "thickness": 0.2}]}})
    recs = [_rec("C9001", {"op": "remove", "kind": "wall", "level": "L0", "start": [1, 0], "end": [2, 0],
                           "thickness": 0.2}),
            _rec("C9002", {"op": "remove", "kind": "wall", "level": "L0", "start": [1.2, 0], "end": [3, 0],
                           "thickness": 0.2})]
    t = TR.build_truth("p", acc, recs)
    walls = [(w["start"], w["end"], bool(w.get("absent"))) for w in t["per_level"]["L0"]["walls"]]
    assert walls == [([0.0, 0.0], [1.0, 0.0], False), ([1.0, 0.0], [3.0, 0.0], True), ([3.0, 0.0], [10.0, 0.0], False)]
    neg = next(w for w in t["per_level"]["L0"]["walls"] if w.get("absent"))
    assert neg["corrections"] == ["C9001", "C9002"]
    res = SC.match(t, _walls_read({"start": [0, 0], "end": [1, 0], "thickness": 0.2},
                                  {"start": [2, 0], "end": [3, 0], "thickness": 0.2},
                                  {"start": [3, 0], "end": [10, 0], "thickness": 0.2}))
    assert res["walls"]["absent_hits"] == 1 and res["walls"]["matched"] == 2


# --- 7. a confidence that is no number ------------------------------------------------------------------------------

def test_07_a_place_confidence_that_is_no_number_never_raises():
    rec = _rec("C9001", {"op": "add", "kind": "door", "level": "L0", "center": [1, 1]}, project="real06",
               place_source="located_by_machine", place_confidence="low")
    assert "no number" in TR.correction_applicable(rec)
    t = TR.build_truth("real06", _real("real06"), RECORDS + [rec])
    assert any(n["record"] == "C9001" for n in t["build_report"]["not_replayed"])
    assert any("place_confidence 'low'" in e for e in TR.correction_errors([rec], [], ["real06"]))


# --- 8. the command line decides on the new operation only ----------------------------------------------------------

def test_08_a_record_with_an_unmatched_operation_still_takes_a_valid_one(cli):
    store = cli.records()
    store[0]["truth_action"] = {"op": "add", "elements": [{"op": "add", "kind": "door", "level": "L9",
                                                           "center": [1.0, 1.0]}]}
    TR.save_corrections(store, cli.store)
    code, msg = cli(kind="door", center="4.0,0.0", confirm=True, correction="C0001")
    assert code == 0, msg
    t = cli.truth()
    assert [(x["n"], x["state"]) for x in t["build_report"]["applied"] + t["build_report"]["unmatched"]] == \
        [(2, "confirmed"), (1, "unmatched")]


# --- 9. accept never replaces a reading silently -------------------------------------------------------------------

def test_09_accept_needs_the_users_acceptance_of_this_reading_and_keeps_the_old_one(tmp_path, monkeypatch):
    from tests.test_reading_truth_20261104 import building, numbers_of
    from wenart.reading_check import regress as RG

    b = building()
    folder = tmp_path / "work" / "tiny"
    (folder / "reading_check").mkdir(parents=True)
    (folder / "building.json").write_text(json.dumps(b))
    (folder / "reading_check" / "commit.txt").write_text("bbb222\n")
    base = tmp_path / "base"
    base.mkdir()
    (base / "tiny.json").write_text(json.dumps(dict(numbers_of(b), accepted_by_user=True, accepted_on="2026-11-04")))
    monkeypatch.setattr(RG, "numbers", lambda folder: numbers_of(b))
    acc_dir = tmp_path / "acc"
    TR.write_accepted("tiny", {"project": "tiny", "commit": "aaa111", "date": "2026-11-04", "per_level": {}},
                      acc_dir)
    later = lambda commit: "2026-11-06"                                           # noqa: E731
    assert TR.accept(["tiny"], tmp_path / "work", accepted_dir=acc_dir, baseline_dir=base, projects_dir=tmp_path,
                     date_of=later) == {}
    assert TR.load_accepted("tiny", acc_dir)["commit"] == "aaa111"                # untouched
    assert TR.accept(["tiny"], tmp_path / "work", accepted_dir=acc_dir, baseline_dir=base, projects_dir=tmp_path,
                     date_of=lambda commit: None) == {}                           # an unknown date is no proof
    got = TR.accept(["tiny"], tmp_path / "work", accepted_dir=acc_dir, baseline_dir=base, projects_dir=tmp_path,
                    date_of=later, user_said="yes, this reading is right")
    stored = TR.load_accepted("tiny", acc_dir)
    assert got and stored["commit"] == "bbb222" and stored["user_said"]["words"] == "yes, this reading is right"
    kept = sorted((acc_dir / "previous").glob("*.json"))
    assert [p.name for p in kept] == ["tiny.2026-11-04.json"] and json.loads(kept[0].read_text())["commit"] == "aaa111"
    TR.accept(["tiny"], tmp_path / "work", accepted_dir=acc_dir, baseline_dir=base, projects_dir=tmp_path,
              date_of=later, user_said="yes again")
    assert len(list((acc_dir / "previous").glob("*.json"))) == 2                 # never overwritten


# --- 10. remove then add: the element names both records ------------------------------------------------------------

@pytest.mark.parametrize("kind,first,then", [
    ("window", {"center": [3.0, 0.0]}, {"center": [3.0, 0.0], "width": 1.2}),
    ("door", {"center": [3.0, 0.0], "kind": "window"}, {"center": [3.0, 0.0], "width": 1.2}),
    ("room", {"polygon": _sq(0, 0, 4, 4)}, {"polygon": _sq(0, 0, 4, 4), "label": "BBB"}),
    ("wall", {"start": [2, 0], "end": [3, 0], "thickness": 0.2}, {"start": [2, 0], "end": [3, 0], "thickness": 0.2}),
])
def test_10_remove_then_add_on_one_element_names_both_records(kind, first, then):
    acc = _acc({"L0": {"windows": [{"id": "win1", "center": [3.0, 0.0], "width": 1.2}],
                       "rooms": [{"id": "r1", "label": "Oda", "polygon": _sq(0, 0, 4, 4)}],
                       "walls": [{"id": "w1", "start": [0, 0], "end": [10, 0], "thickness": 0.2}]}})
    rm = dict({"op": "remove", "kind": kind, "level": "L0"}, **first)
    add = dict({"op": "add", "kind": kind, "level": "L0"}, **then)
    t = TR.build_truth("p", acc, [_rec("C9001", rm), _rec("C9002", add)])
    t_ = TR.KIND_TO_TYPE[kind]
    final = [e for e in TR.positives(t["per_level"]["L0"][t_]) if "C9002" in (e.get("corrections") or [])]
    assert len(final) == 1 and final[0]["corrections"] == ["C9001", "C9002"]


# --- 11. no wall of no length, no room of no area -------------------------------------------------------------------

@pytest.mark.parametrize("op", [
    {"op": "add", "kind": "wall", "level": "L0", "start": [30, 30], "end": [30, 30], "thickness": 0.2},
    {"op": "remove", "kind": "wall", "level": "L0", "start": [1, 1], "end": [1, 1]},
    {"op": "add", "kind": "room", "level": "L0", "polygon": [[30, 30], [31, 30], [32, 30]]},
    {"op": "add", "kind": "door", "level": "L0", "center": [float("nan"), 1.0]},
])
def test_11_degenerate_operations_are_refused(op):
    acc = _real("real06")
    t = TR.build_truth("real06", acc, [_rec("C9001", op, project="real06")])
    assert t["build_report"]["unmatched"] and SC.match(t, _own(t))["total"] == 100.0
    assert _body(t) == _body(TR.build_truth("real06", acc, []))


def _own(truth):
    return {"levels": truth["levels"], "per_level": {lid: {t: TR.positives(lv.get(t)) for t in TR.ELEMENT_TYPES}
                                                     for lid, lv in truth["per_level"].items()}}


def test_11_the_command_line_refuses_them(cli):
    code, msg = cli(action="remove", kind="wall", start="1,1", end="1,1", correction="C0001")
    assert code == 2 and "no length" in msg
    code, msg = cli(kind="door", center="nan,inf", text="a door")
    assert code == 2 and "finite" in msg and cli.truth() is None and len(cli.records()) == 3


# --- 12. the score's matching never depends on the order of the lists ----------------------------------------------

def test_12_contained_collinear_walls_match_in_every_order():
    walls = [{"start": [0, 0], "end": [10, 0], "thickness": 0.2}, {"start": [1, 0], "end": [2, 0], "thickness": 0.2},
             {"start": [5, 0], "end": [6, 0], "thickness": 0.2}]
    for t_order in itertools.permutations(walls):
        truth = {"status": "accepted", "levels": [{"id": "L0"}], "per_level": {"L0": {"walls": list(t_order)}}}
        for r_order in itertools.permutations(walls):
            assert SC.match(truth, _walls_read(*r_order))["total"] == 100.0


def test_12_points_at_equal_distances_match_in_every_order():
    truth_pts = [{"center": [0.0, 0.0]}, {"center": [0.25, 0.0]}]
    read_pts = [{"center": [0.125, 0.0]}, {"center": [0.4, 0.0]}]
    got = {len(SC.match_points(list(a), list(b), SC.OPENING_CENTER_M))
           for a in itertools.permutations(truth_pts) for b in itertools.permutations(read_pts)}
    assert len(got) == 1


@pytest.mark.parametrize("project", ["real06", "real07", "real10"])
def test_12_a_reversed_reading_of_the_truth_scores_100(project):
    truth = TR.load_truth(project)
    read = _own(truth)
    rev = {"levels": read["levels"], "per_level": {lid: {t: list(reversed(els)) for t, els in lv.items()}
                                                   for lid, lv in read["per_level"].items()}}
    assert SC.match(truth, read)["total"] == 100.0 and SC.match(truth, rev)["total"] == 100.0


# --- 13. the user releases a record that waits on the machine's place -----------------------------------------------

def test_13_remark_confirm_lifts_the_wait(tmp_path):
    from wenart.reading_check import remark as RM

    rec = next(r for r in RECORDS if r["id"] == "C0021")
    assert "under 0.6" in TR.correction_applicable(rec)
    store = tmp_path / "c.jsonl"
    TR.save_corrections([copy.deepcopy(rec)], store)
    got = RM.confirm("C0021", store, date="2026-11-06")
    assert got["place_source"] == "user_confirmed" and got["history"][-1]["old_place_source"] == "located_by_machine"
    assert TR.correction_applicable(TR.load_corrections(store)[0]) is None
    with pytest.raises(ValueError):
        RM.confirm("C9999", store)


# --- 14. the command line writes only records the store accepts ----------------------------------------------------

def test_14_the_command_line_refuses_a_record_the_checks_reject(cli):
    code, msg = cli(kind="door", center="4.0,0.0", text="a door", lesson="UL999")
    assert code == 2 and "UL999" in msg
    code, msg = cli(kind="door", center="4.0,0.0", text="a door", date="last week")
    assert code == 2 and "YYYY-MM-DD" in msg
    assert cli.truth() is None and len(cli.records()) == 3
    store = cli.records()                                     # a record without a place or level takes the user's
    store[0].update(level=None, place=None, placeable=True, place_note="none yet")
    TR.save_corrections(store, cli.store)
    code, msg = cli(kind="door", center="4.0,0.0", confirm=True, correction="C0001")
    assert code == 0, msg
    rec = cli.records()[0]
    assert rec["level"] == "L0" and rec["place"] == {"x": 4.0, "y": 0.0} and rec["place_source"] == "given_by_user"
    assert TR.correction_errors([rec], [], ["p"]) == []


# --- 15. the store's truth_applied is what the build did ------------------------------------------------------------

def test_15_truth_applied_in_the_store_is_recomputed_from_the_build():
    truths = {p: TR.load_truth(p) for p in TR.truth_projects()}
    for rec in RECORDS:
        p = rec["project"]
        want = TR.applied_of(rec, truths.get(p), None if p in truths else TR.why_no_truth(p))
        assert rec.get("truth_applied") == want, rec["id"]


def test_15_the_command_line_keeps_the_store_in_step(cli):
    assert cli(kind="door", center="4.0,0.0", confirm=True, correction="C0001")[0] == 0
    recs = {r["id"]: r for r in cli.records()}
    assert recs["C0001"]["truth_applied"] == {"status": "replayed", "results": [
        {"n": 1, "op": "confirm", "kind": "door", "level": "L0", "place": [4.0, 0.0], "state": "confirmed"}]}
    assert recs["C0002"]["truth_applied"]["status"] == "not_replayed"


# --- 16. the report names records and places, never element ids -----------------------------------------------------

def test_16_a_later_removal_leaves_no_dangling_report(cli):
    assert cli(kind="door", center="4.0,0.0", confirm=True, text="this door is right")[0] == 0
    assert cli(action="remove", kind="door", center="4.0,0.0", text="on second look there is no door here")[0] == 0
    t = cli.truth()
    assert all("ids" not in x for x in t["build_report"]["applied"])
    neg = [e for e in t["per_level"]["L0"]["doors"] if e.get("absent")]
    assert len(neg) == 1 and neg[0]["corrections"] == ["C0004", "C0005"]
