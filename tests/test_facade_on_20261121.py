"""21 Nov 2026: the facade-line rule switched on with the user's OK ("Yes, use the right one"), and the user's answers of
21 Nov. CPU only, synthetic data (the real projects are measured by the score gate and the regression set).

- ``truth move``: a record's machine-located geometry moves with the user's OK, the user's words kept and the move
  logged in the record; the score gate judges a moved record at its new place (``score.moved_with_ok``) and never
  excuses a loss without a logged move, after the stored numbers, of a record that holds entirely at its new place;
- a window's glass drawn as panes end to end on one line with mullions between them is a window, never a sliding door
  (``openings._window_panes``; real09's kitchen windows, the user: "There is a window and there is a door");
- the ground rule counts drawn windows buried under the section's ground and, with no drawn door to the outside, takes
  the line read on both sides at the lowest storey's floor (``ground_lines``); the facade gaps typed over the new
  ground follow it (``ground_lines.facade_gap_types``);
- a level the user excluded (``truth exclude``: a brief input, never truth) is skipped by the AI checks' question
  picker and the critic's calibration; a checks calibration made after the trust file's stale mark counts.
"""
from __future__ import annotations

import argparse
import json
from types import SimpleNamespace

import pytest

import _real01_page as R
from wenart.ingest import ground_lines as GL
from wenart.ingest.generic import facade as FC
from wenart.ingest.generic import openings as O
from wenart.reading_check import bandit as BD
from wenart.reading_check import critic as CR
from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR


def test_the_facade_line_rule_is_on():
    assert FC.FACADE_LINE_SNAP is True


# ------------------------------------------------------------------------------------------------- truth move
TF = [50.0, 0.0, -100.0, 0.0, 50.0, -200.0]           # building metres = 50 x page units + shift


def _reading(tmp_path, walls):
    b = {"levels": [{"id": "L0", "label": "Z", "region_id": "r2", "order": 0, "elevation": 0.0}],
         "documents": [{"file": "p.dwg", "pages": [{"page": 1, "region_id": "r2", "level_id": "L0", "variant": "base",
                                                     "transform_to_building": TF}]}],
         "walls": [dict(w, level_id="L0") for w in walls], "rooms": [], "openings": [], "furniture": []}
    d = tmp_path / "reading"
    d.mkdir(exist_ok=True)
    (d / "building.json").write_text(json.dumps(b), encoding="utf-8")
    return d


def _store(tmp_path, ops):
    rec = {"id": "C0001", "date": "2026-11-03", "project": "px", "level": "L0", "place": {"x": 1.0, "y": 0.0},
           "element_kind": "wall", "reader_answer": "open", "right_answer": "closed along the frames",
           "user_words": "go ahead with the glazed facades", "lesson": None, "note": "test", "source": "user_review",
           "status": "accepted", "placeable": True, "place_source": "located_by_machine", "place_confidence": 0.7,
           "reader_ids": ["w_old_1", "w_old_2"],
           "truth_action": {"op": "add", "kind": "wall", "elements": ops}}
    path = tmp_path / "corrections.jsonl"
    path.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    (tmp_path / "projects" / "px").mkdir(parents=True, exist_ok=True)
    for d in ("truth", "accepted", "baseline"):
        (tmp_path / d).mkdir(exist_ok=True)
    return path


def _dirs(tmp_path, path):
    return dict(corrections=path, truth_dir=tmp_path / "truth", accepted_dir=tmp_path / "accepted",
                baseline_dir=tmp_path / "baseline", projects_dir=tmp_path / "projects")


OLD = [{"op": "add", "kind": "wall", "level": "L0", "id": "w_old_1", "start": [0.0, 0.2], "end": [2.0, 0.2],
        "thickness": 0.26},
       {"op": "add", "kind": "wall", "level": "L0", "id": "w_old_2", "start": [3.0, 0.2], "end": [4.0, 0.2],
        "thickness": 0.26}]


def _move_args(reading, **kw):
    base = {"project": "px", "level": "L0", "kind": "wall", "correction": "C0001", "reading": str(reading),
            "id": "w_new_1,w_new_2", "text": "Yes, use the right one", "why": "walls moved onto the drawn facade line",
            "date": "2026-11-21", "ops": None}
    base.update(kw)
    return argparse.Namespace(**base)


def test_a_move_replaces_the_geometry_keeps_the_words_and_logs_the_change(tmp_path):
    path = _store(tmp_path, OLD)
    reading = _reading(tmp_path, [{"id": "w_new_1", "start": [0.0, 0.05], "end": [2.0, 0.05], "thickness": 0.3},
                                  {"id": "w_new_2", "start": [3.0, 0.05], "end": [4.0, 0.05], "thickness": 0.3}])
    code, msg = TR.move(_move_args(reading, start="5.0,1.0", end="6.0,1.0", thickness="0.16"), **_dirs(tmp_path, path))
    assert code == 0, msg
    rec = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert rec["user_words"] == "go ahead with the glazed facades" and rec["right_answer"] == "closed along the frames"
    ops = rec["truth_action"]["elements"]
    assert [o.get("id") for o in ops] == ["w_new_1", "w_new_2", None]
    assert ops[0]["start"] == [0.0, 0.05] and ops[2]["start"] == [5.0, 1.0]
    assert ops[0]["frame"]["start"] == pytest.approx([2.0, 4.001], abs=1e-6)       # (0 + 100) / 50, (0.05 + 200) / 50
    assert rec["reader_ids"] == ["w_new_1", "w_new_2"]
    (h,) = [x for x in rec["history"] if x.get("by") == TR.MOVE_BY]
    assert h["user_words"] == "Yes, use the right one" and h["reason"] == "walls moved onto the drawn facade line"
    assert [o["n"] for o in h["old_ops"]] == [1, 2] and h["old_ops"][0]["start"] == [0.0, 0.2]
    assert h["new_numbers"] == [1, 2, 3]
    assert TR.moved_ops(rec) == [{"date": "2026-11-21", "old_numbers": [1, 2], "new_numbers": [1, 2, 3],
                                  "user_words": "Yes, use the right one"}]
    truth = json.loads((tmp_path / "truth" / "px.json").read_text(encoding="utf-8"))
    ys = sorted(round(e["start"][1], 2) for e in truth["per_level"]["L0"]["walls"])
    assert ys == [0.05, 0.05, 1.0]                              # w_new_1, w_new_2 (1 m apart) and the given place


def test_a_move_needs_the_users_words_a_reason_and_elements_of_its_kind(tmp_path):
    path = _store(tmp_path, OLD)
    reading = _reading(tmp_path, [{"id": "w_new_1", "start": [0.0, 0.05], "end": [2.0, 0.05], "thickness": 0.3}])
    before = path.read_text(encoding="utf-8")
    for kw, why in (({"text": " "}, "user's words"), ({"why": None}, "reason"), ({"id": "w_nope"}, "no such element"),
                    ({"correction": "C0099"}, "not applied")):
        code, msg = TR.move(_move_args(reading, **kw), **_dirs(tmp_path, path))
        assert code == 2 and why in msg, msg
    assert path.read_text(encoding="utf-8") == before                          # nothing written


def test_moves_count_only_with_the_users_words_and_an_applicable_record():
    rec = {"id": "C0001", "project": "px", "status": "accepted", "user_words": "x", "source": "user_review",
           "history": [{"by": TR.MOVE_BY, "date": "2026-11-21", "user_words": "", "old_ops": [{"n": 1}]},
                       {"by": TR.MOVE_BY, "date": "2026-11-21", "user_words": "ok", "old_ops": [{"n": 2}],
                        "new_numbers": [2]},
                       {"by": "something else", "date": "2026-11-21", "user_words": "ok", "old_ops": [{"n": 3}]}]}
    assert [m["old_numbers"] for m in TR.moved_ops(rec)] == [[2]]
    assert TR.moves_by_project([rec]) == {"px": {"C0001": TR.moved_ops(rec)}}
    assert TR.moves_by_project([dict(rec, status="proposed")]) == {}


# ------------------------------------------------------------------------------------ the gate and a moved record
def _row(eid, ok, recs, at):
    return {"id": eid, "level": "L0", "type": "walls", "absent": False, "records": list(recs), "satisfied": ok,
            "at": at}


def _sparse(rows, vs=None, records=None):
    v = {"total": 100.0, "sparse": True, "entries": rows, "assertions": [], "records": records or {}}
    if vs is not None:
        v["vs_stored_truth"] = {"entries": vs, "assertions": []}
    return v


OLD_AT, NEW_AT = ["walls", False, [1.0, 0.2], [2.0, 0.2]], ["walls", False, [1.0, 0.05], [2.0, 0.05]]
MOVE = {"date": "2026-11-21", "old_numbers": [1, 2], "new_numbers": [1, 2], "user_words": "Yes, use the right one"}


def _gate(now_records, moved, stored_on="2026-11-12", recs=("C0001",), old_rows=None):
    stored = {"commit": "a", "date": stored_on, "truth_kind": SC.TRUTH_KIND,
              "projects": {"real": _sparse(old_rows or [_row("u_C0001_1", True, recs, OLD_AT)])}}
    last = SC.latest([stored])
    new = {"truth_kind": SC.TRUTH_KIND,
           "projects": {"real": _sparse([_row("u_C0001_1", now_records["C0001"][0] > 0, recs, NEW_AT)],
                                        vs=[_row("u_C0001_1", False, recs, OLD_AT)], records=now_records)}}
    notes = []
    return SC.falls(last, new, moved=moved, notes=notes), notes


def test_a_record_moved_with_the_users_ok_is_judged_at_its_new_place():
    fell, notes = _gate({"C0001": [1, 1]}, {"real": {"C0001": [MOVE]}})
    assert fell == [] and len(notes) == 1
    assert "C0001 moved with the user's OK on 2026-11-21" in notes[0] and "u_C0001_1" in notes[0] and "(1/1)" in notes[0]


@pytest.mark.parametrize("now_records,moved,stored_on,recs", [
    ({"C0001": [0, 1]}, {"real": {"C0001": [MOVE]}}, "2026-11-12", ("C0001",)),       # fails at its new place too
    ({"C0001": [1, 1]}, None, "2026-11-12", ("C0001",)),                                # no move logged
    ({"C0001": [1, 1]}, {"real": {"C0001": [MOVE]}}, "2026-11-22", ("C0001",)),       # moved before the stored numbers
    ({"C0001": [1, 1]}, {"real": {"C0001": [dict(MOVE, old_numbers=[3])]}}, "2026-11-12", ("C0001",)),  # another op
    ({"C0001": [1, 1]}, {"other": {"C0001": [MOVE]}}, "2026-11-12", ("C0001",)),      # another project's record
])
def test_a_loss_without_a_move_that_holds_still_falls(now_records, moved, stored_on, recs):
    fell, notes = _gate(now_records, moved, stored_on, recs)
    assert fell == ["real: no longer satisfied: C0001 (u_C0001_1)"] and notes == []


def test_an_entry_of_two_records_still_falls_for_the_record_not_moved():
    fell, notes = _gate({"C0001": [1, 1], "C0002": [1, 1]}, {"real": {"C0001": [MOVE]}}, recs=("C0001", "C0002"))
    assert fell == ["real: no longer satisfied: C0002 (u_C0001_1)"] and len(notes) == 1


# ---------------------------------------------------------------------------------------------- window panes
def _run(walls, strokes):
    return O.gaps_and_openings(walls, strokes, "test.pdf", 1)


def _pane(x0, x1, ys=(0.02, 0.05)):
    return [R.stroke([(x0, y), (x1, y)]) for y in ys]


def test_panes_end_to_end_with_a_mullion_are_a_window_not_a_sliding_door():
    """real09 L2: a 0.60 m and a 0.80 m casement in a 1.50 m gap, a 5 cm post between them, each pane drawn as two
    lines in the wall band: one window as wide as the gap."""
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.5, 0), (5.5, 0))]
    strokes = _pane(2.05, 2.65) + _pane(2.70, 3.45)
    _, openings, log, _ = _run(walls, strokes)
    assert [o.kind for o in openings] == ["window"] and openings[0].width == pytest.approx(1.5)
    assert [e["class"] for e in log if e["kind"] == "run"] == ["window"]
    three = _pane(2.05, 2.50) + _pane(2.55, 3.0) + _pane(3.05, 3.45)                # three panes, two mullions
    assert [o.kind for o in _run(walls, three)[1]] == ["window"]


def test_leaves_on_two_tracks_or_meeting_without_a_mullion_stay_a_sliding_door():
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.5, 0), (5.5, 0))]
    tracks = _pane(2.0, 2.85, (-0.04, -0.01)) + _pane(2.65, 3.5, (0.01, 0.04))      # overlapping, two tracks
    meeting = _pane(2.0, 2.75) + _pane(2.75, 3.5)                                    # bi-parting: they touch
    # real10's entrance '140/230' on the window layer: two leaves 3 cm apart along, on tracks shifted 3 cm across
    # (a line of each 5 mm apart: no shared frame line)
    shifted = _pane(2.0, 2.6, (0.03, 0.055, 0.08)) + _pane(2.63, 3.4, (0.0, 0.025, 0.05))
    # ... its lines ending at other points (each leaf's middle line shorter): still two leaves, never two panes
    ragged = _pane(2.0, 2.6, (0.03, 0.08)) + _pane(2.075, 2.6, (0.055,)) + _pane(2.63, 3.4, (0.0,)) \
        + _pane(2.655, 3.37, (0.05,))
    for strokes in (tracks, meeting, shifted):
        _, openings, _, _ = _run(walls, strokes)
        assert [o.kind for o in openings] == ["door"] and openings[0].operation == "sliding"
    assert [o.kind for o in _run(walls, ragged)[1]] != ["window"]                    # (no leaf of equal lines either)


def test_a_pane_too_short_or_a_chain_short_of_the_gap_is_no_window():
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.5, 0), (5.5, 0))]
    short = _pane(2.05, 2.65) + _pane(2.70, 3.0)                    # covers 0.95 of 1.5 m: no window of panes
    assert [o.kind for o in _run(walls, short)[1]] != ["window"]


def test_a_window_read_on_an_inferred_facade_wall_with_its_doors_swing_is_that_door():
    """real13 L0: with the facade line on, a 'K2 90/210' door drawn closed lies in the inferred wall's band and its
    handle strokes read as a window; its swing hinged at a jamb, as wide as the opening, makes it the door. A casement's
    small swing, or a door hinged past a pier beside a window, leaves the window."""
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import OpeningItem, WallItem

    wall = WallItem(start=(0.0, 0.0), end=(3.0, 0.0), thickness=0.16, box=[0, 0, 0, 0], evidence={}, entity="W")

    def window(c, w):
        return OpeningItem(kind="window", width=w, center=(c, 0.0), rotation_deg=0.0, box=[0, 0, 0, 0], entity="L",
                           evidence={"method": "vector"}, height=1.2, sill=0.9, assumed=["height", "sill_height"])

    def swing(hinge, r, layer="KAPI"):
        return Stroke(id=f"ARC:{hinge}", kind="arc", pts=[(hinge, 0.08), (hinge + r, 0.08 + r)], layer=layer,
                      arc={"center": (hinge, 0.08), "radius": r, "start_deg": 0.0, "end_deg": 90.0})

    (o,) = FC.swing_doors([wall], [swing(0.60, 0.85)], [window(1.01, 0.82)])
    assert o.kind == "door" and o.operation == "swing" and o.sill is None and "door swing" in o.evidence["note"]
    (o,) = FC.swing_doors([wall], [swing(0.72, 0.71)], [window(1.01, 0.82)])          # real13: a 0.71 m leaf
    assert o.kind == "door"
    (o,) = FC.swing_doors([wall], [swing(0.60, 0.50)], [window(1.01, 0.82)])          # a casement's swing
    assert o.kind == "window"
    (o,) = FC.swing_doors([wall], [swing(2.05, 0.80)], [window(1.20, 1.20)])          # a door past a 0.25 m pier
    assert o.kind == "window"
    (o,) = FC.swing_doors([wall], [swing(0.60, 0.85, layer="MOBILYA")], [window(1.01, 0.82)])   # no door layer
    assert o.kind == "window"


# ---------------------------------------------------------------------------------------- the ground and windows
def _storey(lid, order, z, doors, windows, kind=None):
    walls = [{"id": f"w_{lid}_{s}", "level_id": lid, "start": list(a), "end": list(e), "thickness": 0.2,
              "exterior": True}
             for s, a, e in (("s", (0, 0), (10, 0)), ("e", (10, 0), (10, 8)), ("n", (10, 8), (0, 8)),
                             ("w", (0, 8), (0, 0)))]
    rooms = [{"id": f"r_{lid}", "level_id": lid, "label": "SALON", "room_type": "living",
              "polygon": [[0, 0], [10, 0], [10, 8], [0, 8]]}]
    ops = []
    if doors:
        ops.append({"id": f"d_{lid}_1", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_s", "center": [5.0, 0.0],
                    "width": 1.0, "height": 2.1, "evidence": [{"method": "vector"}]})
    if windows:
        ops.append({"id": f"win_{lid}_1", "type": "window", "level_id": lid, "wall_id": f"w_{lid}_n",
                    "center": [5.0, 8.0], "width": 1.5, "height": 1.2, "sill_height": 0.9,
                    "evidence": [{"method": "vector"}]})
    lv = {"id": lid, "label": lid, "order": order, "elevation": z, "ceiling_height": 2.7}
    if kind:
        lv["kind"] = kind
    return lv, walls, rooms, ops


def _ground(lines, doors_on=()):
    parts = [_storey("L-1", -1, -2.5, "L-1" in doors_on, True, "basement"),
             _storey("L0", 0, 0.0, "L0" in doors_on, True), _storey("L1", 1, 3.0, "L1" in doors_on, True)]
    b = {"levels": [p[0] for p in parts], "walls": [w for p in parts for w in p[1]],
         "rooms": [r for p in parts for r in p[2]], "openings": [o for p in parts for o in p[3]], "furniture": [],
         "warnings": [], "level_inference": {},
         "site": {"ground": {"levels": [{"side": "all", "azimuth_deg": None,
                                         "z": {"value": 11.11, "method": "vector", "confidence": 1.0,
                                               "evidence": [{"file": "x.dwg", "entity": "LINE:TOP"}], "lines": lines}}],
                             "surface": {"kind": "flat", "flat_z": 11.11, "source": "section"}}}}
    return SimpleNamespace(building=b, conflict=lambda *a: None, warn=b["warnings"].append)


LINES = [{"side": s, "z": z, "entity": f"LINE:{s[0]}{k}"} for k, z in enumerate((11.11, 6.03, 3.03, 0.03, -2.47))
         for s in ("left", "right")]


def test_buried_windows_refuse_the_ground_and_the_lowest_storeys_line_is_taken():
    """real09: no drawn door to the outside (its 'doors' were windows read as sliding doors), the section's +11.11 m
    line buries the windows of L0 and L1: refused; the line on both sides at the lowest storey's floor is the ground."""
    build = _ground(LINES)
    rec = GL.apply(build)
    assert rec is not None and rec["doors"] == [] and rec["windows"] == ["win_L0_1", "win_L1_1"]
    assert rec["z"] == -2.47 and rec["at"] == "L-1" and rec["chosen"]["both_sides"]
    assert "lowest storey L-1" in rec["reason"] and "window(s)" in rec["reason"]


def test_buried_windows_with_no_line_at_the_lowest_floor_assume_a_step_under_the_first_buried_storey():
    build = _ground([ln for ln in LINES if ln["z"] > 0])
    rec = GL.apply(build)
    assert rec["chosen"] is None and rec["z"] == -0.15
    assert [x["kind"] for x in build.building["needs_review"]] == ["ground_doors"]


def test_doors_at_grade_still_decide_where_the_ground_goes():
    rec = GL.apply(_ground(LINES, doors_on=("L0", "L1")))
    assert rec["z"] == 0.03 and rec["at"] == "L0" and rec["doors"] == ["d_L0_1", "d_L1_1"]
    assert "beside the doors at grade of L0" in rec["reason"]


def test_the_facade_gaps_typed_over_the_new_ground_follow_it():
    b = {"openings": [{"id": "o1", "type": "opening", "height": 2.1, "threshold_z": 0.0},
                      {"id": "o2", "type": "opening", "drawn_type": "door"},
                      {"id": "o3", "type": "opening"}]}
    new = {"openings": [{"id": "o1", "type": "window", "drawn_type": "opening", "sill_height": 0.9, "height": 1.2,
                         "drawn_height": 2.1, "type_inferred": {"method": "facade_gap", "reason": "over a drop"}},
                        {"id": "o2", "type": "window", "type_inferred": {"method": "facade_gap"}},
                        {"id": "o3", "type": "opening"}]}
    assert GL.facade_gap_types(b, new) == 1
    o1, o2, o3 = b["openings"]
    assert o1["type"] == "window" and o1["sill_height"] == 0.9 and o1["type_inferred"]["method"] == "facade_gap"
    assert "threshold_z" not in o1 and o2["type"] == "opening" and o3 == {"id": "o3", "type": "opening"}


# ---------------------------------------------------------------------------------------- an excluded level
def test_an_excluded_level_is_a_brief_input_and_never_truth(tmp_path):
    path = tmp_path / "c.jsonl"
    path.write_text("", encoding="utf-8")
    (tmp_path / "projects" / "px").mkdir(parents=True)
    args = argparse.Namespace(project="px", level="L3", text="this drawing is not good we can ignore this drawing",
                              date="2026-11-21", lesson=None, why=None, reader_answer=None, right_answer=None)
    code, msg = TR.exclude_level(args, corrections=path, projects_dir=tmp_path / "projects")
    assert code == 0, msg
    recs = TR.load_corrections(path)
    assert TR.excluded_levels(recs) == {"px": {"L3": recs[0]["id"]}}
    assert recs[0]["truth_role"] == TR.TRUTH_ROLE_BRIEF and "brief input" in TR.correction_applicable(recs[0])
    assert TR.correction_errors(recs, [], ["px"]) == []
    assert TR.exclude_level(args, corrections=path, projects_dir=tmp_path / "projects")[1].endswith(
        f"already excluded by {recs[0]['id']}")
    assert TR.build_sparse("px", recs)["build_report"]["not_replayed"][0]["record"] == recs[0]["id"]
    assert TR.is_excluded(TR.excluded_levels(recs), "px", "L2") is None


def _gap_rec(level):
    return {"kind": "gap", "project": "px", "level_id": level, "place": [1.0, 1.0], "gap": "run",
            "rule_confidence": 0.4, "final_answer": "door" if level == "L2" else "opening"}


def test_the_question_picker_and_the_calibration_skip_an_excluded_level():
    lab = {"disagreements": [{"rec": _gap_rec(lv), "ai": {"drawing": "window", "entry": "e", "qid": "q"}}
                             for lv in ("L2", "L3")]}
    excluded = {"px": {"L3": "C0095"}}
    assert [q["level_id"] for q in BD.question_list(lab, top=5, include_findings=False, excluded=excluded)] == ["L2"]
    assert len(BD.question_list(lab, top=5, include_findings=False, excluded={})) == 2
    found = [{"id": "a", "project": "px", "level_id": "L3"}, {"id": "b", "folder": "after/px", "level_id": "L3"},
             {"id": "c", "project": "px", "level_id": "L2"}]
    kept, out = CR.skip_excluded(found, excluded)
    assert [f["id"] for f in kept] == ["c"] and out == [("px", "L3"), ("px", "L3")]
    known = {"before/px@abc": [{"level": "L3", "id": "k1"}, {"level": "L2", "id": "k2"}], "after/py": [{"level": "L3"}]}
    assert CR.known_without_excluded(known, excluded) == {"before/px@abc": [{"level": "L2", "id": "k2"}],
                                                          "after/py": [{"level": "L3"}]}


def test_a_checks_calibration_after_the_stale_mark_counts():
    def finding():
        return [{"check": CR.CHECK, "call": "plausibility", "kind": "storey_no_stair_access", "severity": "major",
                 "message": "m"}]
    checks = {"plausibility": {"storey_no_stair_access": {"findings": 25, "judged": 3, "precision": 0.0}}}
    stale = {"on": "2026-11-12", "reason": "withdrawn readings"}
    after = {"stale": stale, "checks": checks, "checks_calibration": {"date": "2026-11-21"}}
    (f,) = CR.apply_trust(finding(), after)
    assert f["severity"] == "info" and "precision 0.00 on 3 judged" in f["message"]
    before = {"stale": stale, "checks": checks, "checks_calibration": {"date": "2026-11-10"}}
    (g,) = CR.apply_trust(finding(), before)
    assert g["severity"] == "info" and "not calibrated" in g["message"]
    trusted = {"stale": stale, "checks": {"plausibility": {"storey_no_stair_access": {"findings": 9, "judged": 9,
                                                                                       "precision": 1.0}}},
               "checks_calibration": {"date": "2026-11-21"}}
    (h,) = CR.apply_trust(finding(), trusted)
    assert h["severity"] == "major"


# ------------------------------------------------------- 21 Nov 2026 (coordinator review): no closed space is opened
@pytest.mark.parametrize("name", ["real13_L0_union_20261121.json", "real13_L3_union_20261121.json"])
def test_the_slit_closing_never_fills_a_room(name):
    """real13 with the facade line on: GEOS's mitred erosion of the grown wall union (L0), or its buffer itself (L3),
    filled the lift shaft's hole and no lift room was built. ``topology.close_slits`` keeps every hole the raw union has
    (an erosion never reaches past what was grown; no closing reaches a hole's core)."""
    from pathlib import Path

    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union

    from wenart.ingest.generic import topology as TP

    doc = json.loads((Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8"))
    u = unary_union([Polygon(p) for p in doc["polygons"]])
    label = Point(doc["label"])
    raw = [Polygon(r).area for g in getattr(u, "geoms", [u]) for r in g.interiors if Polygon(r).contains(label)]
    closed = TP.close_slits(u)
    kept = [Polygon(r).area for g in getattr(closed, "geoms", [closed]) for r in g.interiors
            if Polygon(r).contains(label)]
    assert raw and kept and kept[0] == pytest.approx(raw[0], abs=0.12)                # (L3: the core, 1.5 cm in)
    assert closed.difference(u.buffer(TP.SLIT_CLOSE_M, join_style=2)).area <= TP.CLOSE_ARTEFACT_M2


def test_a_lift_shaft_against_a_glazed_facade_stays_a_room():
    """A lift shaft beside a living room whose facade is drawn as frames: the room is closed on the drawn facade line
    and the shaft stays a closed face holding its label."""
    from shapely.geometry import Point

    from wenart.ingest.generic import topology as TP
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import WallItem

    def wall(s, e, t=0.2):
        return WallItem(start=s, end=e, thickness=t, box=[0, 0, 0, 0], evidence={"file": "x.dwg", "entity": "W"},
                        entity="W")

    def line(k, a, b):
        return Stroke(id=f"LINE:{k}", kind="line", pts=[a, b], layer="kapı-pencere")

    walls = [wall((-0.2, 4.1), (6.2, 4.1)), wall((4.1, 4.2), (4.1, -0.2)), wall((4.2, -0.1), (-0.2, -0.1)),
             wall((-0.1, -0.2), (-0.1, 0.6)), wall((-0.1, 3.4), (-0.1, 4.2)),
             wall((4.0, 1.9), (6.2, 1.9)), wall((6.1, 1.8), (6.1, 4.2))]                      # the lift shaft
    strokes = [line(1, (-0.15, 0.7), (-0.15, 3.3)), line(2, (-0.1, 0.7), (-0.1, 3.3)),
               line(3, (-0.05, 0.7), (-0.05, 3.3)), line(4, (0.03, 0.7), (0.03, 3.3))]
    lift = Point(5.1, 3.0)
    assert any(f.contains(lift) for f in TP.faces(walls))
    for snap in (True, False):
        faces, _ = FC.close_rooms(walls, strokes, [(2.0, 2.0)], snap=snap)
        new = FC.facade_wall_items(walls, [faces[0]], [], "x.dwg", None)
        after = TP.faces(walls + new)
        assert any(f.contains(lift) for f in after) and any(f.contains(Point(2.0, 2.0)) for f in after)


def test_a_lift_stair_or_shaft_label_outside_every_room_is_raised():
    from wenart.reading_check import structure as SR

    def bld(places, rooms=()):
        return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "reading_places": places}], "rooms": list(rooms),
                "walls": [], "openings": []}

    lift = {"kind": "unplaced_label", "text": "HİDROLİK ASANSÖR", "at": [1.0, 1.0]}
    (f,) = SR.core_spaces_unbuilt(bld([lift]))
    assert f["check"] == "RC17" and f["rule"] == "core_space_unbuilt" and f["severity"] == "major"
    assert f["place"] == [1.0, 1.0] and f in SR.findings(bld([lift]))
    for text in ("MERDİVEN", "ŞAFT", "Stairs", "lift lobby"):
        assert len(SR.core_spaces_unbuilt(bld([dict(lift, text=text)]))) == 1, text
    assert SR.core_spaces_unbuilt(bld([dict(lift, text="SALON")])) == []
    room = {"id": "r", "level_id": "L0", "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}
    assert SR.core_spaces_unbuilt(bld([lift], [room])) == []                    # it found its room later
    assert SR.core_spaces_unbuilt(bld([dict(lift, kind="undecided_gap")])) == []


def test_an_empty_gap_with_one_wall_face_drawn_across_is_the_wall():
    """real09 L3, C0090 ("it is a drawing mistake"): the wall's outer face runs on across a 1.25 m gap, its inner face is
    missing there and nothing else is drawn: the wall continues, no opening of any kind. Without the face line, or with
    a line on another layer, the gap stays an opening."""
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.25, 0), (5.25, 0))]
    face = R.stroke([(-0.5, 0.1), (5.75, 0.1)])
    face.layer = "duvar"
    _, openings, log, _ = _run(walls, [face])
    assert openings == [] and [e["class"] for e in log if e["kind"] == "run"] == ["closed"]
    assert [o.kind for o in _run(walls, [])[1]] == ["opening"]
    other = R.stroke([(-0.5, 0.1), (5.75, 0.1)])                                # a railing on another layer
    other.layer = "korkuluk"
    assert [o.kind for o in _run(walls, [other])[1]] == ["opening"]


def test_a_negated_opening_holds_only_with_no_door_window_or_opening_there():
    """C0090: the user's 'neither a window nor an opening' fails on a window read at the place, as on an opening; a
    door a present entry of the truth takes there is the user's own and does not count."""
    def rec(rid, op):
        return {"id": rid, "date": "2026-11-21", "project": "p", "level": "L0", "place": None,
                "element_kind": op["kind"], "reader_answer": "", "right_answer": "", "user_words": "w", "lesson": None,
                "note": "t", "source": "user_review", "status": "accepted",
                "truth_action": {"op": op["op"], "elements": [op]}}

    def read(**per):
        out = {"levels": [{"id": "L0", "label": "Z", "order": 0, "elevation": 0.0}],
               "per_level": {"L0": {t: [] for t in TR.ELEMENT_TYPES + TR.SPARSE_KINDS}}}
        for t, els in per.items():
            out["per_level"]["L0"][t] = list(els)
        return out

    neg = rec("C0090", {"op": "remove", "kind": "opening", "level": "L0", "center": [1.0, 0.0]})
    t = TR.build_sparse("p", [neg])
    assert SC.match(t, read())["total"] == 100.0
    for kind in ("windows", "doors", "openings"):
        assert SC.match(t, read(**{kind: [{"id": "x", "center": [1.1, 0.0]}]}))["total"] == 0.0, kind
    door = rec("C0091", {"op": "add", "kind": "door", "level": "L0", "center": [1.1, 0.0]})
    t2 = TR.build_sparse("p", [neg, door])
    assert SC.match(t2, read(doors=[{"id": "d", "center": [1.1, 0.0]}]))["total"] == 100.0


def test_one_own_face_running_across_a_span_is_solid_wall_for_a_mirror_copy():
    """real09 L3: the reader closes the gap C0090 names (one face drawn across); the mirror step must not copy the twin
    half's opening back onto it. One of the wall's own face lines running across the span is solid wall; a span both
    faces break at is not."""
    from types import SimpleNamespace

    from wenart.ingest.generic import mirror as MR
    from wenart.ingest.model import WallItem

    host = WallItem(start=(0.0, 0.0), end=(6.0, 0.0), thickness=0.2, box=[0, 0, 1, 1], entity="LINE:a,LINE:b,LINE:c",
                    evidence={"method": "vector", "entity": "LINE:a,LINE:b,LINE:c"})
    outer = SimpleNamespace(id="LINE:a", pts=[(0.0, 0.1), (6.0, 0.1)])                 # runs across the span
    inner_l = SimpleNamespace(id="LINE:b", pts=[(0.0, -0.1), (2.0, -0.1)])             # breaks at the span
    inner_r = SimpleNamespace(id="LINE:c", pts=[(3.25, -0.1), (6.0, -0.1)])
    assert MR.solid_span(host, (2.625, 0.0), 1.25, [outer, inner_l, inner_r])
    outer_l = SimpleNamespace(id="LINE:a", pts=[(0.0, 0.1), (2.0, 0.1)])
    outer_r = SimpleNamespace(id="LINE:b", pts=[(3.25, 0.1), (6.0, 0.1)])
    assert not MR.solid_span(host, (2.625, 0.0), 1.25, [outer_l, outer_r, inner_l, inner_r])


def test_a_closed_face_of_another_size_at_a_labelled_rooms_mirror_place_takes_its_label():
    """real09 L2: once the light wells stayed open the plan was two mirrored halves at the strict share; the left
    kitchen (drawn 2.44 m wide, its twin 'MUTFAK' 1.84 m) closed at a mirror seed and lost the label the loose-axis twin
    seed gave it. A face with no label of its own at a labelled room's mirror place, of another size (the same size is
    ``twins.mirror_labels``'s), that passes ``twin_evidence`` is the twin, whichever step closed it."""
    from shapely.geometry import box

    from wenart.ingest.generic import core as GC

    axis = ("x", 10.0)
    twin = box(14.0, 0.0, 15.84, 3.0)                       # 'MUTFAK', its label at (14.9, 1.5)
    face = box(4.16, 0.0, 6.6, 3.0)                         # the left kitchen, 0.6 m wider toward the axis
    blocks = [SimpleNamespace(name="MUTFAK", anchor=(14.9, 1.5))]
    door = SimpleNamespace(kind="door", virtual=False, center=(6.6, 1.5))
    got = GC._closed_mirror_twins([face], [face, twin], blocks, [(14.9, 1.5)], axis, [], [door], [], [])
    assert len(got) == 1 and got[0]["label"] == "MUTFAK" and got[0]["seed"] == [5.1, 1.5] \
        and got[0]["of"] == [14.9, 1.5] and any("door" in e for e in got[0]["evidence"])
    # the same size: left to twins.mirror_labels
    same = box(4.16, 0.0, 6.0, 3.0)
    assert GC._closed_mirror_twins([same], [same, twin], blocks, [(14.9, 1.5)], axis, [], [door], [], []) == []
    # a face with a label of its own, or with nothing drawn that marks a room there, is not the twin
    own = [SimpleNamespace(name="MUTFAK", anchor=(14.9, 1.5)), SimpleNamespace(name="ODA", anchor=(5.5, 1.0))]
    assert GC._closed_mirror_twins([face], [face, twin], own, [(14.9, 1.5), (5.5, 1.0)], axis, [], [door], [], []) == []
    assert GC._closed_mirror_twins([face], [face, twin], blocks, [(14.9, 1.5)], axis, [], [], [], []) == []
