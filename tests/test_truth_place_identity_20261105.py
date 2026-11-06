"""The truth does not depend on the reader's ids (5 Nov 2026, review of the stable mirror-copy ids: every reader
improvement renumbers its ids; an absent entry o_Lk_029 then negated the real opening that inherited the id, and the
file held one id for two elements). ``reading_check.truth``: identity is place (the score's rules), every element has
a truth id of its own (``t_L0_door_0012``), the reader's id is a ``reader_id`` hint. CPU, pure."""
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
    """A small reading: three doors, a window, two openings, a wall, a room (the reader's ids)."""
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
    return {"project": "p", "source": TR.SOURCE_ACCEPTED, "status": "accepted", "levels": [{"id": "L0"}],
            "per_level": {"L0": lv}}


def _renumbered(reading):
    """The same reading with every id shifted (what a reader improvement does)."""
    r = copy.deepcopy(reading)
    for els in r["per_level"]["L0"].values():
        ids = [e["id"] for e in els]
        for e, new in zip(els, ids[1:] + ids[:1]):
            e["id"] = new
    return r


def _truth_with_corrections():
    t = TR.merge(None, _reading())
    building = {"levels": [{"id": "L0"}], "openings": [dict(e, level_id="L0") for k in ("doors", "openings")
                                                       for e in _reading()["per_level"]["L0"][k]]}
    # the user confirms a door and negates an opening, by the reader's ids of the reading they looked at
    TR.add_element(t, "door", "L0", {"id": "d_L0_003"}, correction="C0001", reading=building)
    TR.remove_element(t, "opening", "L0", {"id": "o_L0_001"}, correction="C0002", reading=building)
    t.pop("last_added", None)
    t.pop("last_removed", None)
    return t


def _shape(truth):
    """Every element as (level, type, place, source, absent, truth id)."""
    out = []
    for lid, lv in truth["per_level"].items():
        for t, els in lv.items():
            for e in els:
                out.append((lid, t, json.dumps(TR._anchor(t, e)), e.get("source"), bool(e.get("absent")), e["id"]))
    return sorted(out)


def test_a_reading_that_renumbers_every_id_changes_nothing():
    truth = _truth_with_corrections()
    a = TR.merge(truth, _reading())
    b = TR.merge(truth, _renumbered(_reading()))
    assert _shape(a) == _shape(b)                                   # the same elements, the same truth ids
    assert SC.match(truth, _reading())["total"] == SC.match(truth, _renumbered(_reading()))["total"]
    door = [e for e in b["per_level"]["L0"]["doors"] if e["source"] == TR.SOURCE_USER]
    assert len(door) == 1 and door[0]["center"] == [3.0, 0.0] and door[0]["reader_id"] == "d_L0_003"
    assert len(b["per_level"]["L0"]["doors"]) == 3                  # the confirmed door is not held twice


def test_an_absent_entry_never_removes_a_real_element_that_inherited_its_old_id():
    truth = _truth_with_corrections()                               # o_L0_001 at (2, 4) negated
    shifted = _renumbered(_reading())                               # now o_L0_001 names the opening at (6, 4)
    assert next(e for e in shifted["per_level"]["L0"]["openings"] if e["id"] == "o_L0_001")["center"] == [6.0, 4.0]
    merged = TR.merge(truth, shifted)
    ops = merged["per_level"]["L0"]["openings"]
    assert sorted((e["center"], bool(e.get("absent"))) for e in ops) == [([2.0, 4.0], True), ([6.0, 4.0], False)]


def test_add_by_a_readers_id_is_stored_by_place():
    truth = TR.merge(None, _reading())
    shifted = _renumbered(_reading())
    # in the shifted reading 'd_L0_003' is the door at (1, 0) (in the truth, d_L0_003 was the door at 3): resolved to
    # its place in the reading it was taken from, it names the truth's door at 1
    TR.add_element(truth, "door", "L0", {"id": "d_L0_003"}, correction="C0003", reading={
        "levels": [{"id": "L0"}], "openings": [dict(e, level_id="L0") for e in shifted["per_level"]["L0"]["doors"]]})
    got = truth["last_added"]
    assert got["center"] == [1.0, 0.0] and TR.is_truth_id(got["id"]) and got["corrections"] == ["C0003"]
    assert got["reader_id"] == "d_L0_001" and len(truth["per_level"]["L0"]["doors"]) == 3


@pytest.mark.parametrize("path", sorted((ROOT / "results" / "reading_truth").glob("*.json")), ids=lambda p: p.stem)
def test_no_truth_file_holds_one_truth_id_twice(path):
    t = json.loads(path.read_text(encoding="utf-8"))
    ids = Counter(e["id"] for lv in t["per_level"].values() for els in lv.values() if isinstance(els, list)
                  for e in els if TR.is_truth_id(e.get("id")))
    assert [i for i, n in ids.items() if n > 1] == []
    if path.stem in ("real06", "real07", "real10"):                  # moved to truth ids on 5 Nov 2026
        assert all(TR.is_truth_id(e["id"]) for lv in t["per_level"].values() for els in lv.values()
                   if isinstance(els, list) for e in els)
        assert int(t["next_truth_id"]) > max(int(i.rsplit("_", 1)[1]) for i in ids)


# --- the review of round 3 (the verifiers' cases rebuilt as tests) ---------------------------------------------------

REAL = ("real06", "real07", "real10")


def _own_reading(truth, shift=None):
    """A reading made of the truth's own positives, under the reader's ids (the review's identity case); ``shift``:
    ``{level: (dx, dy)}`` moves that level's doors, windows and openings."""
    lv_out = {}
    for lid, lv in truth["per_level"].items():
        lv_out[lid] = {}
        for t in TR.ELEMENT_TYPES:
            els = []
            for e in TR.positives(lv.get(t)):
                r = copy.deepcopy(e)
                r["id"] = e.get("reader_id") or e.get("old_id") or e["id"]
                r.pop("reader_id", None)
                r["source"] = TR.SOURCE_ACCEPTED
                if shift and lid in shift and t in TR.OPENING_TYPES:
                    dx, dy = shift[lid]
                    r["center"] = [round(r["center"][0] + dx, 3), round(r["center"][1] + dy, 3)]
                els.append(r)
            lv_out[lid][t] = els
    return {"project": truth.get("project"), "source": TR.SOURCE_ACCEPTED, "status": "accepted",
            "levels": copy.deepcopy(truth["levels"]), "per_level": lv_out}


def _elements(truth):
    return sorted((lid, t, json.dumps(TR._anchor(t, e)), e["id"], bool(e.get("absent")))
                  for lid, lv in truth["per_level"].items() for t in TR.ELEMENT_TYPES for e in lv.get(t) or [])


@pytest.mark.parametrize("project", REAL)
def test_merging_a_reading_of_the_truths_own_positives_changes_nothing(project):
    """Review of round 3: a negation took a reading element before the accepted element at that place could keep it
    (real10 100 -> 99.75, real07 100 -> 99.96 after one merge). In the score's order the merge is the identity: the
    same elements with the same truth ids, and the reading scores 100 before and after."""
    truth = TR.load_truth(project)
    reading = _own_reading(truth)
    assert SC.match(truth, reading)["total"] == 100.0
    merged = TR.merge(truth, reading)
    assert _elements(merged) == _elements(truth)
    assert SC.match(merged, reading)["total"] == 100.0


@pytest.mark.parametrize("shift", [(0.0, 0.06), (0.0, -0.06), (0.10, 0.05)])
def test_a_shifted_reading_loses_no_opening_and_swaps_no_truth_id(shift):
    """The review's L0 lift case (real10: o_L0_007, o_L0_009 and o_L0_010 stand close together): the reading's L0
    openings moved by a few centimetres keep every opening and every accepted opening's truth id."""
    truth = TR.load_truth("real10")
    merged = TR.merge(truth, _own_reading(truth, {"L0": shift}))
    lv, mv = truth["per_level"]["L0"], merged["per_level"]["L0"]
    for t in TR.OPENING_TYPES:
        assert len(TR.positives(mv[t])) == len(TR.positives(lv[t])), t
        by_id = {e["id"]: e for e in mv[t]}
        for e in TR.positives(lv[t]):
            if e["source"] != TR.SOURCE_ACCEPTED:
                continue
            got = by_id.get(e["id"])
            assert got is not None and got["center"] == [round(e["center"][0] + shift[0], 3),
                                                       round(e["center"][1] + shift[1], 3)], (t, e["id"])
    lift = {e.get("reader_id"): e["id"] for t in TR.OPENING_TYPES for e in mv[t]
            if e.get("reader_id") in ("o_L0_007", "o_L0_009", "o_L0_010")}
    assert lift == {e.get("reader_id"): e["id"] for t in TR.OPENING_TYPES for e in lv[t]
                    if e.get("reader_id") in ("o_L0_007", "o_L0_009", "o_L0_010") and not e.get("absent")}


def test_a_negated_short_span_does_not_remove_a_long_wall():
    """real07 C0053's kind: a negated 2.23 m span (the user: no wall there) inside a 6 m reading wall leaves the wall
    (it is no negation of the whole wall); a reading wall that is that span is suppressed."""
    truth = TR.merge(None, _reading())
    TR.remove_element(truth, "wall", "L0", {"start": "9.752,5.69", "end": "11.982,5.69", "thickness": "0.25"},
                      correction="C0053")
    reading = _reading()
    reading["per_level"]["L0"]["walls"].append({"id": "w_L0_009", "start": [7.0, 5.69], "end": [13.0, 5.69],
                                                "thickness": 0.25, "source": TR.SOURCE_ACCEPTED})
    walls = TR.merge(truth, reading)["per_level"]["L0"]["walls"]
    assert any(w.get("reader_id") == "w_L0_009" and not w.get("absent") for w in walls)
    reading["per_level"]["L0"]["walls"][-1].update(start=[9.75, 5.69], end=[11.98, 5.69])
    walls = TR.merge(truth, reading)["per_level"]["L0"]["walls"]
    assert not any(w.get("reader_id") == "w_L0_009" for w in walls)


def test_a_users_door_wins_its_place_whatever_list_the_reader_put_it_in():
    truth = TR.merge(None, _reading())
    TR.add_element(truth, "door", "L0", {"center": "6,4", "width": "1.0"}, correction="C0004")   # o_L0_002's place
    lv = TR.merge(truth, _reading())["per_level"]["L0"]                 # the reader still reads an opening there
    assert [e["center"] for e in lv["openings"]] == [[2.0, 4.0]]
    assert [e["center"] for e in lv["doors"] if e["source"] == TR.SOURCE_USER] == [[6.0, 4.0]]


def test_a_readers_id_needs_its_reading():
    truth = TR.merge(None, _reading())
    with pytest.raises(ValueError, match="reader's id"):
        TR.add_element(truth, "door", "L0", {"id": "d_L0_003"}, correction="C0005")
    building = {"levels": [{"id": "L0"}],
                "openings": [dict(e, level_id="L0") for e in _reading()["per_level"]["L0"]["doors"]]}
    with pytest.raises(ValueError, match="no such element"):
        TR.add_element(truth, "door", "L0", {"id": "d_L0_999"}, correction="C0005", reading=building)
    with pytest.raises(ValueError, match="holds it as doors"):
        TR.add_element(truth, "window", "L0", {"id": "d_L0_003"}, correction="C0005", reading=building)
    with pytest.raises(ValueError, match="no such truth id"):
        TR.remove_element(truth, "door", "L0", {"id": "t_L0_door_9999"})


def test_remarks_name_truth_ids_and_mark_by_place(tmp_path):
    """A new record names the truth element at the reading element's place (a reader's id stays a hint); its crop
    marks the truth elements at their own places, never by a reader's id."""
    from wenart.reading_check import remark as RM

    truth = TR.merge(None, _reading())
    door3 = next(e for e in truth["per_level"]["L0"]["doors"] if e["center"] == [3.0, 0.0])
    shifted = _renumbered(_reading())                      # here d_L0_005 is the door at (3, 0)
    building = {"levels": [{"id": "L0"}], "project": {"id": "p"},
                "openings": [dict(e, level_id="L0") for e in shifted["per_level"]["L0"]["doors"]]}
    assert RM.truth_ids(truth, building, ["d_L0_005", "d_L0_404"], "L0") == [door3["id"], "d_L0_404"]
    rec = {"element_ids": [door3["id"]]}
    assert RM.truth_marks(rec, truth) == [("doors", door3)]
    out = RM.draw_crop(building, "L0", {"x": 3.0, "y": 0.0}, [], tmp_path / "c.png", marks=RM.truth_marks(rec, truth))
    assert out.is_file()
