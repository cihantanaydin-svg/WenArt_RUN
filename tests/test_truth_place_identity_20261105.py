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
    TR.add_element(t, "door", "L0", {"id": "d_L0_003"}, correction="C0001")          # the user confirms a door
    TR.remove_element(t, "opening", "L0", {"id": "o_L0_001"}, correction="C0002")    # and negates an opening
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
