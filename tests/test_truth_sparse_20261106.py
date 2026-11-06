"""The sparse truth of a real project (6 Nov 2026, Milestone 14 R1; user: "I have never reviewed real21 with my eyes",
"Only consider my revision with the screenshot I have given into previous projects others I have not seen"): a real
project's truth starts empty and holds only what the user's applicable correction records assert, replayed in record
order by place (a later record overrides an earlier one at the same place); the score judges each entry satisfied or
not on a reading, nothing else; the gate falls when an entry satisfied before is no longer satisfied, whatever the
percentage, and never compares numbers of another truth kind. CPU, pure (the command line in a temp folder)."""
from __future__ import annotations

import argparse
import json

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR


def _rec(rid: str, *ops: dict, project: str = "p", **kw) -> dict:
    r = {"id": rid, "date": "2026-11-06", "project": project, "level": ops[0].get("level") if ops else None,
         "place": None, "element_kind": ops[0].get("kind") if ops else "level", "reader_answer": "",
         "right_answer": "", "user_words": "the user's words", "lesson": None, "note": "test", "source": "user_review",
         "status": "accepted"}
    if ops:
        r["truth_action"] = {"op": ops[0]["op"], "elements": list(ops)}
    r.update(kw)
    return r


def _read(levels=("L0",), **per) -> dict:
    """A reading in the truth's shape: ``per`` maps ``"<level>_<type>"`` to its elements."""
    out = {"levels": [{"id": lid, "elevation": 3.0 * i} for i, lid in enumerate(levels)],
           "per_level": {lid: {t: [] for t in TR.ELEMENT_TYPES} for lid in levels}}
    for key, els in per.items():
        lid, t = key.split("_", 1)
        out["per_level"][lid][t] = list(els)
    return out


def _sq(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _entries(truth, lid, t):
    return truth["per_level"][lid][t]


# --- the build ------------------------------------------------------------------------------------------------------

def test_a_remove_record_gives_an_absent_entry_on_an_empty_base():
    t = TR.build_sparse("p", [_rec("C0001", {"op": "remove", "kind": "window", "level": "L0", "center": [3.0, 0.0],
                                             "width": 1.2})])
    assert TR.is_sparse(t) and t["source"] == TR.SOURCE_CORRECTIONS and t["status"] == "sparse"
    (w,) = _entries(t, "L0", "windows")
    assert w["absent"] is True and w["center"] == [3.0, 0.0] and w["width"] == 1.2 and w["corrections"] == ["C0001"]
    assert w["id"] == "u_C0001_1" and w["source"] == TR.SOURCE_USER
    assert [lv["id"] for lv in t["levels"]] == ["L0"] and t["built_from"]["records"] == ["C0001"]
    assert t["build_report"]["applied"][0]["state"] == "negated" and TR.entry_count(t) == 1
    # nothing else: no element of the reading enters the truth
    assert all(not _entries(t, "L0", k) for k in TR.ELEMENT_TYPES if k != "windows")


def test_a_later_add_at_the_same_place_cancels_the_negation():
    recs = [_rec("C0001", {"op": "remove", "kind": "door", "level": "L0", "center": [3.0, 0.0]}),
            _rec("C0002", {"op": "add", "kind": "door", "level": "L0", "center": [3.1, 0.05], "width": 0.9})]
    t = TR.build_sparse("p", recs)
    (d,) = _entries(t, "L0", "doors")
    assert not d.get("absent") and d["center"] == [3.1, 0.05] and d["corrections"] == ["C0001", "C0002"]
    assert t["build_report"]["applied"][1]["state"] == "replaced a negation"
    # the order decides: the add first, then the remove, leaves the negation (the newer record wins)
    t2 = TR.build_sparse("p", [dict(recs[1], id="C0001"), dict(recs[0], id="C0002")])
    (d2,) = _entries(t2, "L0", "doors")
    assert d2["absent"] is True and d2["corrections"] == ["C0001", "C0002"] and d2["center"] == [3.0, 0.0]
    assert d2["width"] == 0.9                                       # what the remove left out, from the replaced one


def test_a_retype_by_remove_and_add_keeps_both_assertions():
    """real07 C0045's kind: "no window here" (remove window) and "a garage door here" (add door) at one place are two
    assertions: a door at the place and no window there."""
    t = TR.build_sparse("p", [_rec("C0045", {"op": "remove", "kind": "window", "level": "L0", "center": [2.03, 0.24]},
                                   {"op": "add", "kind": "door", "level": "L0", "center": [2.03, 0.24],
                                    "width": 3.41})])
    assert [e.get("absent") for e in _entries(t, "L0", "windows")] == [True]
    assert [(e.get("absent"), e["width"]) for e in _entries(t, "L0", "doors")] == [(None, 3.41)]
    door = _read(L0_doors=[{"id": "d", "center": [2.0, 0.24]}])
    window = _read(L0_windows=[{"id": "w", "center": [2.0, 0.24]}])
    assert SC.match(t, door)["total"] == 100.0
    res = SC.match(t, window)
    assert res["total"] == 0.0 and sorted(res["unsatisfied"]) == ["u_C0045_1", "u_C0045_2"]


def test_a_newer_add_of_another_opening_type_replaces_the_present_entry():
    recs = [_rec("C0001", {"op": "add", "kind": "window", "level": "L0", "center": [5.0, 0.0], "width": 1.5}),
            _rec("C0002", {"op": "add", "kind": "door", "level": "L0", "center": [5.0, 0.1]})]
    t = TR.build_sparse("p", recs)
    assert _entries(t, "L0", "windows") == []
    (d,) = _entries(t, "L0", "doors")
    assert d["width"] == 1.5 and d["corrections"] == ["C0001", "C0002"]


def test_a_negated_wall_span_cuts_an_earlier_wall_entry_and_a_later_wall_takes_the_span_back():
    recs = [_rec("C0001", {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0], "end": [10, 0],
                           "thickness": 0.2}),
            _rec("C0002", {"op": "remove", "kind": "wall", "level": "L0", "start": [4, 0], "end": [6, 0]})]
    t = TR.build_sparse("p", recs)
    walls = [(w["start"], w["end"], bool(w.get("absent")), w["corrections"]) for w in _entries(t, "L0", "walls")]
    assert walls == [([0.0, 0.0], [4.0, 0.0], False, ["C0001"]), ([4.0, 0.0], [6.0, 0.0], True, ["C0002"]),
                     ([6.0, 0.0], [10.0, 0.0], False, ["C0001"])]
    t2 = TR.build_sparse("p", recs + [_rec("C0003", {"op": "add", "kind": "wall", "level": "L0", "start": [4, 0],
                                                     "end": [6, 0], "thickness": 0.2})])
    walls2 = [(w["start"], w["end"], bool(w.get("absent"))) for w in _entries(t2, "L0", "walls")]
    assert ([4.0, 0.0], [6.0, 0.0], True) not in walls2 and ([4.0, 0.0], [6.0, 0.0], False) in walls2
    # two negated spans that touch are one negation
    t3 = TR.build_sparse("p", [_rec("C0001", {"op": "remove", "kind": "wall", "level": "L0", "start": [0, 0],
                                              "end": [2, 0]}),
                               _rec("C0002", {"op": "remove", "kind": "wall", "level": "L0", "start": [2, 0],
                                              "end": [3, 0]})])
    assert [(w["start"], w["end"], w["corrections"]) for w in _entries(t3, "L0", "walls")] == [
        ([0.0, 0.0], [3.0, 0.0], ["C0001", "C0002"])]


def test_rooms_override_by_overlap():
    recs = [_rec("C0001", {"op": "remove", "kind": "room", "level": "L0", "label": "Oda", "polygon": _sq(0, 0, 2, 2)}),
            _rec("C0002", {"op": "add", "kind": "room", "level": "L0", "label": "Depo", "room_type": "storage",
                           "polygon": _sq(0, 0, 2, 2.2)}),
            _rec("C0003", {"op": "retype", "kind": "room", "level": "L0", "center": [1.0, 1.0], "room_type": "wc"})]
    t = TR.build_sparse("p", recs)
    (r,) = _entries(t, "L0", "rooms")
    assert not r.get("absent") and r["label"] == "Depo" and r["room_type"] == "wc"
    assert r["polygon"] == _sq(0, 0, 2, 2.2) and r["corrections"] == ["C0001", "C0002", "C0003"]
    bad = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "room", "level": "L0", "center": [9, 9]})])
    assert bad["build_report"]["unmatched"] and bad["per_level"] == {}       # nothing of it stays


def test_records_that_wait_or_give_nothing_to_check_are_reported():
    recs = [_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [1, 0]}, status="proposed"),
            _rec("C0002", {"op": "add", "kind": "door", "level": "L0", "center": [1, 0]},
                 place_source="located_by_machine", place_confidence=0.5),
            _rec("C0003", element_kind="roof", why="a roof rule (gable ends)"),
            _rec("C0004", element_kind="level", why="storey heights",
                 truth_assert=[{"what": "level_count", "value": 3}, {"what": "storey_heights", "values": [0, 3, 6]}]),
            _rec("C0005", element_kind="site", truth_assert=[{"what": "level_count", "value": 2}])]
    t = TR.build_sparse("p", recs)
    assert [x["record"] for x in t["not_measurable"]] == ["C0003"]
    assert "not measurable yet: a roof rule" in t["not_measurable"][0]["why"]
    nr = {x["record"]: x["why"] for x in t["build_report"]["not_replayed"]}
    assert "proposed" in nr["C0001"] and "under 0.6" in nr["C0002"] and "C0004" not in nr
    # the newer record's level count replaces the older one's; the storey heights stay
    got = {(a["what"], a["id"]): a["corrections"] for a in t["project_assertions"]}
    assert got == {("level_count", "a_C0005_1"): ["C0004", "C0005"], ("storey_heights", "a_C0004_2"): ["C0004"]}
    assert t["built_from"] == {"reading": None, "reading_commit": None, "records": [], "asserted": ["C0004", "C0005"]}
    assert TR.applied_of(recs[3], t)["status"] == "asserted"
    assert TR.applied_of(recs[2], t) == {"status": "not_replayed", "why": t["not_measurable"][0]["why"]}
    assert TR.dumps(TR.build_sparse("p", list(reversed(recs)))) == TR.dumps(t)        # record order, not list order


def test_the_store_checks_the_assertions():
    base = _rec("C0001", element_kind="level", placeable=False, why="heights")
    assert TR.correction_errors([dict(base, truth_assert=[{"what": "level_count", "value": 5}])], [], ["p"]) == []
    for bad in ([{"what": "level_count", "value": 0}], [{"what": "storey_heights", "values": [1, 3]}],
                [{"what": "ground_z"}], [{"what": "roof_pitch", "value": 30}], []):
        assert TR.correction_errors([dict(base, truth_assert=bad)], [], ["p"]), bad


def test_the_repository_records_with_a_project_level_check():
    """The records that state a project-level check explicitly carry it (real09's five storeys and their heights,
    real19's four plans, real10's ground at -3.00 m); the other unplaced records are listed not measurable."""
    by_id = {r["id"]: r for r in TR.load_corrections()}
    assert {a["what"] for a in TR.record_asserts(by_id["C0005"])} == {"level_count", "storey_heights"}
    assert TR.record_asserts(by_id["C0025"]) == [dict(TR.record_asserts(by_id["C0025"])[0], what="level_count",
                                                      value=4)]
    assert TR.record_asserts(by_id["C0031"])[0]["value"] == -3.0
    t = TR.load_truth("real20")
    assert TR.entry_count(t) == 0 and [x["record"] for x in t["not_measurable"]] == ["C0026"]


# --- the score ------------------------------------------------------------------------------------------------------

def test_sparse_scoring_ignores_unlisted_elements():
    t = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [1.0, 0.0]},
                                   {"op": "remove", "kind": "window", "level": "L0", "center": [4.0, 0.0]})])
    lean = _read(L0_doors=[{"id": "d1", "center": [1.1, 0.0]}])
    busy = _read(("L0", "L1"), L0_doors=[{"id": "d1", "center": [1.1, 0.0]}, {"id": "d2", "center": [7.0, 0.0]}],
                 L0_windows=[{"id": "w9", "center": [9.0, 0.0]}],
                 L0_walls=[{"id": "x", "start": [0, 0], "end": [9, 0], "thickness": 0.2}],
                 L1_rooms=[{"id": "r", "label": "Oda", "polygon": _sq(0, 0, 3, 3), "centroid": [1.5, 1.5]}])
    assert SC.match(t, lean)["total"] == SC.match(t, busy)["total"] == 100.0       # no precision term
    res = SC.match(t, busy)
    assert res["doors"] == {"present": 1, "present_ok": 1, "absent": 0, "absent_ok": 0}
    assert res["windows"] == {"present": 0, "present_ok": 0, "absent": 1, "absent_ok": 1}
    assert res["records"] == {"C0001": [2, 2]} and res["unsatisfied"] == []
    hit = _read(L0_doors=[{"id": "d1", "center": [1.1, 0.0]}], L0_windows=[{"id": "w", "center": [4.2, 0.0]}])
    res = SC.match(t, hit)                                    # the negated window read: weight 2 of 4 lost
    assert res["total"] == 50.0 and res["unsatisfied"] == ["u_C0001_2"] and res["records"] == {"C0001": [1, 2]}


def test_the_weights_follow_the_types():
    t = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "stair", "level": "L0", "center": [0, 0]},
                                   {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0], "end": [4, 0]})])
    res = SC.match(t, _read(L0_walls=[{"id": "w", "start": [0, 0], "end": [4, 0]}]))
    assert res["total"] == pytest.approx(100 * 1 / 4, abs=0.01)                  # a wall weighs 1, a stair 3


def test_present_and_absent_walls():
    t = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "wall", "level": "L0", "start": [0, 0],
                                             "end": [10, 0], "thickness": 0.2},
                                   {"op": "remove", "kind": "wall", "level": "L0", "start": [0, 5], "end": [2, 5],
                                    "thickness": 0.2})])
    w = lambda s, e, th=0.2: {"id": f"w{s}{e}", "start": s, "end": e, "thickness": th}   # noqa: E731
    pieces = _read(L0_walls=[w([0, 0], [4, 0]), w([4, 0], [10, 0.02])])                # a long wall read in pieces
    stub = _read(L0_walls=[w([0, 0], [1, 0])])                                          # 10 % of the span
    across = _read(L0_walls=[w([0, 0], [10, 0]), w([-1, 5], [5, 5], 0.22)])            # a wall through the span
    assert SC.match(t, pieces)["total"] == 100.0
    assert SC.match(t, stub)["unsatisfied"] == ["u_C0001_1"]
    assert SC.match(t, across)["unsatisfied"] == ["u_C0001_2"]
    # real07 C0051's kind: the reader keeps the wall whole and puts the passage on it as a doorless opening; what
    # stands over the span is checked, so the passage satisfies "no wall here" and a door there does not
    gap = {"id": "o1", "type": "opening", "center": [1.0, 5.0], "width": 2.2, "wall_id": "w[-1, 5][5, 5]"}
    door = dict(gap, id="d1", type="door")
    passage = dict(across, per_level={"L0": dict(across["per_level"]["L0"], openings=[gap])})
    doorway = dict(across, per_level={"L0": dict(across["per_level"]["L0"], doors=[door])})
    assert SC.match(t, passage)["total"] == 100.0
    assert SC.match(t, doorway)["unsatisfied"] == ["u_C0001_2"]
    # real07 C0053's kind: a 4 cm jamb stub, 14 cm thick, at the end of the negated span is a joint, not a wall
    jamb = _read(L0_walls=[w([0, 0], [10, 0]), w([1.96, 5.02], [2.0, 5.02], 0.18)])
    assert SC.match(t, jamb)["total"] == 100.0
    pieces_of = SC.solid_pieces({"start": [0, 0], "end": [10, 0]}, [{"center": [3.0, 0.0], "width": 2.0},
                                                                    {"center": [3.5, 0.0], "width": 1.0}])
    assert [(p["start"], p["end"]) for p in pieces_of] == [([0.0, 0.0], [2.0, 0.0]), ([4.0, 0.0], [10.0, 0.0])]


def test_room_types_and_a_level_the_reading_lacks():
    t = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "room", "level": "L0", "label": "Merdiven",
                                             "room_type": "stair", "polygon": _sq(0, 0, 2, 3)},
                                   {"op": "remove", "kind": "room", "level": "L1", "label": "Oda",
                                    "polygon": _sq(5, 5, 6, 6)})])
    room = lambda ty: {"id": "r", "label": "Merdiven", "room_type": ty, "polygon": _sq(0, 0, 2, 3),   # noqa: E731
                       "centroid": [1.0, 1.5]}
    assert SC.match(t, _read(("L0", "L1"), L0_rooms=[room("stair")]))["total"] == 100.0
    assert SC.match(t, _read(("L0", "L1"), L0_rooms=[room("storage")]))["unsatisfied"] == ["u_C0001_1"]
    res = SC.match(t, _read(("L0",), L0_rooms=[room("stair")]))       # no L1 read: its negation cannot be confirmed
    assert res["unsatisfied"] == ["u_C0001_2"]
    assert "the reading has no level L1" in next(e["why"] for e in res["entries"] if not e["satisfied"])


def test_project_level_assertions():
    t = TR.build_sparse("p", [_rec("C0001", element_kind="level", truth_assert=[
        {"what": "level_count", "value": 3}, {"what": "storey_heights", "values": [0, 2.5, 5.5]},
        {"what": "level_elevation", "level": "L0", "value": 0.0}, {"what": "ground_z", "value": -3.0}])])
    read = {"levels": [{"id": "L-1", "elevation": -2.5}, {"id": "L0", "elevation": 0.0},
                       {"id": "L1", "elevation": 3.04}],
            "per_level": {}}
    b = {"site": {"ground": {"levels": [{"side": "all", "z": {"value": -3.02}}]}}}
    res = SC.match(t, read, b)
    assert res["total"] == 100.0 and [a["satisfied"] for a in res["assertions"]] == [True] * 4
    res = SC.match(t, dict(read, levels=read["levels"][:2]))           # two levels, no ground read
    assert {a["what"]: a["satisfied"] for a in res["assertions"]} == {
        "ground_z": False, "level_count": False, "level_elevation": True, "storey_heights": False}
    assert res["levels"] == {"present": 4, "present_ok": 1, "absent": 0, "absent_ok": 0}


def test_a_truth_that_asserts_nothing_is_not_read(tmp_path):
    t = TR.build_sparse("q", [_rec("C0001", project="q", element_kind="level", why="a project split")])
    TR.write_truth("q", t, tmp_path)
    got = SC.score_project("q", tmp_path / "work", truth_dir=tmp_path)
    assert got["total"] is None and got["measurable"] is False and got["not_measurable"] == ["C0001"]
    assert not (tmp_path / "work").exists()
    assert SC.overall({"q": got, "s": {"total": 80.0}}) == 80.0
    assert "nothing measurable yet" in SC.table({"projects": {"q": dict(got, truth_source="user_corrections")},
                                                 "overall": 0.0})


# --- the gate -------------------------------------------------------------------------------------------------------

def _stored(total, entries, kind=SC.TRUTH_KIND):
    return {"commit": "a", "truth_kind": kind, "overall": total,
            "projects": {"real": {"total": total, "sparse": True, "entries": entries, "assertions": []},
                         "syn": {"total": 90.0}}}


def _e(eid, ok, *recs):
    return {"id": eid, "level": "L0", "type": "doors", "absent": False, "records": list(recs), "satisfied": ok}


def test_the_gate_falls_on_a_lost_record_even_when_the_share_rises():
    last = SC.latest([_stored(50.0, [_e("u_C0001_1", True, "C0001"), _e("u_C0002_1", False, "C0002")])])
    assert last["truth_kind"] == SC.TRUTH_KIND and last["projects"]["real"]["sparse"] is True
    new = {"truth_kind": SC.TRUTH_KIND, "projects": {
        "real": {"total": 66.67, "sparse": True, "assertions": [],
                 "entries": [_e("u_C0001_1", False, "C0001"), _e("u_C0002_1", True, "C0002"),
                             _e("u_C0003_1", True, "C0003")]},
        "syn": {"total": 90.0}}}
    assert SC.falls(last, new) == ["real: no longer satisfied: C0001 (u_C0001_1)"]
    held = {"truth_kind": SC.TRUTH_KIND, "projects": {
        "real": {"total": 33.33, "sparse": True, "assertions": [],   # the share falls: a new record, not yet met
                 "entries": [_e("u_C0001_1", True, "C0001"), _e("u_C0002_1", False, "C0002"),
                             _e("u_C0004_1", False, "C0004")]},
        "syn": {"total": 90.0}}}
    # no record of the project fell; the overall keeps today's rule (the mean of the totals over the projects both
    # entries have), so a new record the reader does not meet yet lowers it like any other fall of a total
    assert SC.falls(last, held) == ["overall: 70.00 -> 61.66"]
    gone = {"truth_kind": SC.TRUTH_KIND, "projects": {                  # the entry left the truth: not compared
        "real": {"total": 0.0, "sparse": True, "assertions": [], "entries": [_e("u_C0002_1", False, "C0002")]},
        "syn": {"total": 90.0}}}
    assert [x for x in SC.falls(last, gone) if not x.startswith("overall")] == []
    failed = {"truth_kind": SC.TRUTH_KIND, "projects": {"real": {"total": 0.0, "error": "no DXF"},
                                                        "syn": {"total": 90.0}}}
    assert SC.falls(last, failed) == ["overall: 70.00 -> 45.00", "real: 50.00 -> 0.00 (reading failed: no DXF)"]


def test_old_kind_entries_are_never_compared():
    old = {"commit": "z", "overall": 100.0, "projects": {"real": {"total": 100.0}, "syn": {"total": 99.0}}}
    assert SC.latest([old]) is None                                  # the accepted-reading series is history only
    assert SC.latest([old], truth_kind=None)["projects"]["real"]["total"] == 100.0
    new_entry = _stored(10.0, [_e("u_C0001_1", False, "C0001")])
    new_entry["projects"]["syn"]["total"] = 50.0
    assert SC.latest([new_entry, old])["projects"]["syn"]["total"] == 50.0      # the newest of the kind, not the old
    assert SC.falls(SC.latest([old], truth_kind=None), new_entry) == []         # another kind: nothing compared
    mixed = SC.latest([new_entry])
    mixed["projects"]["syn"]["truth_kind"] = "accepted_reading"                  # a project of another kind
    assert SC.falls(mixed, dict(new_entry, projects={"syn": {"total": 1.0}})) == []


def test_a_project_that_changes_between_sparse_and_f1_is_not_compared():
    last = SC.latest([_stored(50.0, [_e("u_C0001_1", True, "C0001")])])
    new = {"truth_kind": SC.TRUTH_KIND, "projects": {"real": {"total": 10.0}, "syn": {"total": 90.0}}}
    assert [x for x in SC.falls(last, new) if x.startswith("real")] == []


# --- the command line -----------------------------------------------------------------------------------------------

def test_truth_add_on_a_project_without_acceptance_builds_its_sparse_truth(tmp_path):
    dirs = {k: tmp_path / k for k in ("truth", "accepted", "baseline", "projects")}
    for d in dirs.values():
        d.mkdir()
    (dirs["projects"] / "p").mkdir()
    (dirs["baseline"] / "p.json").write_text(json.dumps({"accepted_by_user": False, "levels": ["L0"]}))
    store = tmp_path / "c.jsonl"
    TR.save_corrections([], store)
    ns = argparse.Namespace(action="remove", project="p", level="L0", kind="window", center="3.0,0.0",
                            text="there is no window here")
    code, msg = TR.correct(ns, corrections=store, truth_dir=dirs["truth"], accepted_dir=dirs["accepted"],
                           baseline_dir=dirs["baseline"], projects_dir=dirs["projects"])
    assert code == 0, msg
    t = TR.load_truth("p", dirs["truth"])
    assert TR.is_sparse(t) and [e["absent"] for e in _entries(t, "L0", "windows")] == [True]
    (rec,) = TR.load_corrections(store)
    assert rec["truth_applied"]["status"] == "replayed" and rec["user_words"] == "there is no window here"


def test_the_full_build_removes_a_real_truth_without_records(tmp_path, capsys):
    dirs = {k: tmp_path / k for k in ("truth", "accepted", "baseline", "projects")}
    for d in dirs.values():
        d.mkdir()
    for name in ("p", "gone"):
        (dirs["projects"] / name).mkdir()
    TR.write_truth("gone", {"project": "gone", "per_level": {}}, dirs["truth"])
    store = tmp_path / "c.jsonl"
    TR.save_corrections([dict(_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [1, 0]}))], store)
    kw = dict(truth_dir=dirs["truth"], accepted_dir=dirs["accepted"], baseline_dir=dirs["baseline"],
              projects_dir=dirs["projects"], corrections=store)
    done = TR.build(["p"], prune=True, **kw)
    assert list(done) == ["p"] and TR.truth_projects(dirs["truth"]) == ["p"]
    assert "gone: truth file removed" in capsys.readouterr().out
