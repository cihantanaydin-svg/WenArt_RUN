"""The truth does not depend on the reader's ids (5 Nov 2026, review of the stable mirror-copy ids: every reader
improvement renumbers its ids; an absent entry o_Lk_029 then negated the real opening that inherited the id). Since
6 Nov 2026 the truth is derived (``truth.build_truth``: the accepted reading plus a replay of the correction records
by place), so identity is place by construction: the accepted entries are numbered by place (``t_<level>_<kind>_n``),
the entries of a record by the record (``u_<record>_<n>``), the reader's id is a ``reader_id`` hint, and nothing
joins on an id. CPU, pure."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

ROOT = Path(__file__).resolve().parents[1]


def _reading():
    """A small accepted reading: three doors, a window, two openings, a wall, a room (the reader's ids)."""
    lv = {"rooms": [{"id": "r_L0_salon", "label": "Salon", "centroid": [2.0, 2.0],
                     "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}],
          "doors": [{"id": f"d_L0_00{k}", "type": "door", "center": [float(k), 0.0], "width": 0.9} for k in (1, 3, 5)],
          "windows": [{"id": "win_L0_001", "type": "window", "center": [8.0, 0.0], "width": 1.2}],
          "openings": [{"id": "o_L0_001", "type": "opening", "center": [2.0, 4.0], "width": 1.0},
                       {"id": "o_L0_002", "type": "opening", "center": [6.0, 4.0], "width": 1.0}],
          "walls": [{"id": "w_L0_001", "start": [0.0, 0.0], "end": [10.0, 0.0], "thickness": 0.25}],
          "stairs": []}
    for els in lv.values():
        for e in els:
            e["source"] = TR.SOURCE_ACCEPTED
    return {"project": "p", "source": TR.SOURCE_ACCEPTED, "status": "accepted", "commit": "c", "date": "d",
            "levels": [{"id": "L0"}], "levels_left_out": [], "per_level": {"L0": lv}}


def _renumbered(reading):
    """The same reading with every id shifted (what a reader improvement does)."""
    r = copy.deepcopy(reading)
    for els in r["per_level"]["L0"].values():
        ids = [e["id"] for e in els]
        for e, new in zip(els, ids[1:] + ids[:1]):
            e["id"] = new
    return r


def _rec(rid, *ops):
    return {"id": rid, "date": "2026-11-06", "project": "p", "level": "L0", "place": None, "element_kind": "door",
            "reader_answer": "", "right_answer": "", "user_words": "words", "lesson": None, "note": "test",
            "source": "user_review", "status": "accepted", "truth_action": {"op": ops[0]["op"], "elements": list(ops)}}


# the user confirms the door at 3 and negates the opening at (2, 4); the operations carry the reader's ids of the
# reading the user looked at as hints only
CORRECTIONS = [_rec("C0001", {"op": "confirm", "kind": "door", "level": "L0", "center": [3.0, 0.0], "id": "d_L0_003"}),
               _rec("C0002", {"op": "remove", "kind": "opening", "level": "L0", "center": [2.0, 4.0],
                              "id": "o_L0_001"})]


def _shape(truth):
    """Every element as (level, type, place, source, absent, truth id)."""
    return sorted((lid, t, json.dumps(TR._anchor(t, e)), e.get("source"), bool(e.get("absent")), e["id"])
                  for lid, lv in truth["per_level"].items() for t, els in lv.items() for e in els)


def test_an_accepted_reading_that_renumbers_every_id_builds_the_same_truth():
    a = TR.build_truth("p", _reading(), CORRECTIONS)
    b = TR.build_truth("p", _renumbered(_reading()), CORRECTIONS)
    assert _shape(a) == _shape(b)                                   # the same elements, the same truth ids
    door = [e for e in b["per_level"]["L0"]["doors"] if e["source"] == TR.SOURCE_USER]
    assert len(door) == 1 and door[0]["center"] == [3.0, 0.0] and door[0]["id"] == "t_L0_door_0002"
    assert len(b["per_level"]["L0"]["doors"]) == 3                  # the confirmed door is not held twice


def test_a_negation_never_removes_a_real_element_that_inherited_its_old_id():
    shifted = _renumbered(_reading())                               # now o_L0_001 names the opening at (6, 4)
    assert next(e for e in shifted["per_level"]["L0"]["openings"] if e["id"] == "o_L0_001")["center"] == [6.0, 4.0]
    ops = TR.build_truth("p", shifted, CORRECTIONS)["per_level"]["L0"]["openings"]
    assert sorted((e["center"], bool(e.get("absent"))) for e in ops) == [([2.0, 4.0], True), ([6.0, 4.0], False)]


def test_an_id_given_on_the_command_line_becomes_its_place():
    shifted = _renumbered(_reading())
    # in the shifted reading 'd_L0_003' is the door at (1, 0): resolved to its place in the reading it was taken from
    building = {"levels": [{"id": "L0"}],
                "openings": [dict(e, level_id="L0") for e in shifted["per_level"]["L0"]["doors"]]}
    assert TR.resolve_id("d_L0_003", "door", "L0", "add", truth=None, building=building)["center"] == [1.0, 0.0]
    truth = TR.build_truth("p", _reading(), [])
    tid = next(e["id"] for e in truth["per_level"]["L0"]["doors"] if e["center"] == [5.0, 0.0])
    assert TR.resolve_id(tid, "door", "L0", "remove", truth=truth, building=None)["center"] == [5.0, 0.0]
    with pytest.raises(ValueError, match="reader's id"):
        TR.resolve_id("d_L0_003", "door", "L0", "add", truth=truth, building=None)
    with pytest.raises(ValueError, match="no such element"):
        TR.resolve_id("d_L0_999", "door", "L0", "add", truth=None, building=building)
    with pytest.raises(ValueError, match="is a door in the given reading"):
        TR.resolve_id("d_L0_003", "wall", "L0", "add", truth=None, building=building)
    with pytest.raises(ValueError, match="no such truth id"):
        TR.resolve_id("t_L0_door_9999", "door", "L0", "remove", truth=truth, building=None)


@pytest.mark.parametrize("path", sorted((ROOT / "results" / "reading_truth").glob("*.json")), ids=lambda p: p.stem)
def test_no_truth_file_holds_one_truth_id_twice(path):
    t = json.loads(path.read_text(encoding="utf-8"))
    ids = Counter(e["id"] for lv in t["per_level"].values() for els in lv.values() if isinstance(els, list)
                  for e in els)
    assert [i for i, n in ids.items() if n > 1] == []
    assert all(TR.is_truth_id(i) for i in ids) and "next_truth_id" not in t     # no counter: ids are derived


REAL = ("real06", "real07", "real10")


def _own_reading(truth, shift=None):
    """A reading made of the truth's own positives, under the reader's ids; ``shift``: ``{level: (dx, dy)}`` moves
    that level's doors, windows and openings."""
    lv_out = {}
    for lid, lv in truth["per_level"].items():
        lv_out[lid] = {}
        for t in TR.ELEMENT_TYPES:
            els = []
            for e in TR.positives(lv.get(t)):
                r = copy.deepcopy(e)
                r["id"] = e.get("reader_id") or e["id"]
                if shift and lid in shift and t in TR.OPENING_TYPES:
                    dx, dy = shift[lid]
                    r["center"] = [round(r["center"][0] + dx, 3), round(r["center"][1] + dy, 3)]
                els.append(r)
            lv_out[lid][t] = els
    return {"levels": copy.deepcopy(truth["levels"]), "per_level": lv_out}


@pytest.mark.parametrize("project", REAL)
def test_a_reading_of_the_truths_own_positives_scores_100(project):
    truth = TR.load_truth(project)
    assert SC.match(truth, _own_reading(truth))["total"] == 100.0


@pytest.mark.parametrize("shift", [(0.0, 0.06), (0.0, -0.06), (0.10, 0.05)])
def test_a_shifted_reading_changes_nothing_in_the_truth(shift):
    """The review's L0 lift case (real10: the stacked gaps beside the lift stand 4 to 15 cm apart): the truth does not
    see any later reading, and the score matches the shifted openings by place."""
    truth = TR.load_truth("real10")
    res = SC.match(truth, _own_reading(truth, {"L0": shift}))
    for t in TR.OPENING_TYPES:
        assert res[t]["matched"] == res[t]["truth"], t
    acc, _ = TR.accepted_of("real10")
    assert TR.dumps(TR.build_truth("real10", acc, TR.load_corrections())) == TR.dumps(truth)


def test_a_negated_short_span_cuts_a_long_wall_and_never_removes_it_whole():
    """real07 C0053's kind: a negated 2.23 m span (the user: no wall there) inside a 6 m wall cuts it; the pieces
    outside the span stay accepted walls."""
    acc = _reading()
    acc["per_level"]["L0"]["walls"].append({"id": "w_L0_009", "start": [7.0, 5.69], "end": [13.0, 5.69],
                                            "thickness": 0.25, "source": TR.SOURCE_ACCEPTED})
    t = TR.build_truth("p", acc, [_rec("C0053", {"op": "remove", "kind": "wall", "level": "L0",
                                                 "start": [9.752, 5.69], "end": [11.982, 5.69], "thickness": 0.25})])
    walls = [(w["start"], w["end"], bool(w.get("absent")), w["source"]) for w in t["per_level"]["L0"]["walls"]
             if w["start"][1] == 5.69]
    assert walls == [([7.0, 5.69], [9.752, 5.69], False, TR.SOURCE_ACCEPTED),
                     ([9.752, 5.69], [11.982, 5.69], True, TR.SOURCE_USER),
                     ([11.982, 5.69], [13.0, 5.69], False, TR.SOURCE_ACCEPTED)]
    read = _own_reading(TR.build_truth("p", acc, []))               # a reading with the whole 6 m wall
    res = SC.match(t, read)
    assert res["walls"]["truth"] == 3 and res["walls"]["matched"] == 2 and res["walls"]["absent_hits"] == 0


def test_a_users_door_wins_its_place_whatever_list_the_reader_put_it_in():
    t = TR.build_truth("p", _reading(), [_rec("C0004", {"op": "add", "kind": "door", "level": "L0",
                                                        "center": [6.0, 4.0], "width": 1.0})])
    lv = t["per_level"]["L0"]
    assert [e["center"] for e in lv["openings"]] == [[2.0, 4.0]]
    door = [e for e in lv["doors"] if e["source"] == TR.SOURCE_USER]
    assert [(e["center"], e["changed"], e["reader_id"]) for e in door] == [([6.0, 4.0], ["type"], "o_L0_002")]
    res = SC.match(t, _own_reading(TR.build_truth("p", _reading(), [])))   # the reader still reads an opening there
    assert res["doors"]["matched"] == 3 and res["doors"]["truth"] == 4 and res["openings"]["read"] == 2


def test_remarks_mark_by_place(tmp_path):
    """A record's crop marks the truth elements the build put its operations on, or, before a build, the places its
    truth action names; never a reader's id."""
    from wenart.reading_check import remark as RM

    t = TR.build_truth("p", _reading(), CORRECTIONS)
    marks = RM.truth_marks(CORRECTIONS[0], t)
    assert [(k, e["center"]) for k, e in marks] == [("doors", [3.0, 0.0])]
    fresh = _rec("C0009", {"op": "remove", "kind": "window", "level": "L0", "center": [8.0, 0.0], "id": "d_L0_001"})
    assert [(k, e["center"]) for k, e in RM.truth_marks(fresh, t)] == [("windows", [8.0, 0.0])]
    building = {"levels": [{"id": "L0"}], "project": {"id": "p"},
                "openings": [dict(e, level_id="L0") for e in _renumbered(_reading())["per_level"]["L0"]["doors"]]}
    out = RM.draw_crop(building, "L0", {"x": 3.0, "y": 0.0}, [], tmp_path / "c.png", marks=marks)
    assert out.is_file()
