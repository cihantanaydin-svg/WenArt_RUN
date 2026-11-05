"""Tests of wenart.reading_check.remark (5 Nov 2026, R9): records and crops from the user's remarks. Pure; every
file is in a temp folder, the real corrections file is never touched."""
import argparse
import json

import pytest

from wenart.reading_check import remark
from wenart.reading_check.truth import correction_errors

B = {"project": {"id": "real10"},
     "walls": [{"id": "w_L0_001", "level_id": "L0", "start": [0, 0], "end": [4, 0], "thickness": 0.25},
               {"id": "w_L0_002", "level_id": "L0", "start": [4, 0], "end": [4, 3], "thickness": 0.25}],
     "openings": [{"id": "o_L0_001", "type": "door", "level_id": "L0", "wall_id": "w_L0_001", "center": [1, 0],
                   "width": 0.9},
                  {"id": "o_L0_002", "type": "window", "level_id": "L0", "wall_id": "w_L0_002", "center": [4, 1.5],
                   "width": 1.2}],
     "rooms": [{"id": "r_L0_a", "level_id": "L0", "label": "Hall", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}],
     "furniture": []}
OLD = [{"id": "C0001"}, {"id": "C0007"}]


def rec(**kw):
    base = dict(project="real10", text="no wall here", projects=["real10"], date="2026-11-05")
    base.update(kw)
    return remark.build_record(OLD, **base)


def test_next_id_follows_the_highest():
    assert remark.next_id(OLD) == "C0008" and remark.next_id([]) == "C0001"


def test_record_fields_match_the_truth_format():
    r = rec(kind="wall", level="L0", place={"x": 1.0, "y": 2.0})
    assert r["id"] == "C0008" and r["source"] == "user_review" and r["status"] == "accepted"
    assert correction_errors([r], [], ["real10"]) == []
    assert rec()["place"] is None


def test_validation():
    with pytest.raises(ValueError, match="projects"):
        rec(project="nope")
    with pytest.raises(ValueError, match="op"):
        rec(truth_action={"kind": "door"})
    with pytest.raises(ValueError, match="object"):
        rec(truth_action=[1])
    with pytest.raises(ValueError, match="kind"):
        rec(kind="sofa")
    assert rec(truth_action={"op": "add", "kind": "door"})["truth_action"]["op"] == "add"


def test_place_and_level_from_element_and_unknown_refused():
    r = rec(element_ids=["w_L0_002"], building=B)
    assert r["place"] == {"x": 4.0, "y": 1.5} and r["level"] == "L0" and r["element_ids"] == ["w_L0_002"]
    assert rec(element_ids=["o_L0_002"], building=B)["place"] == {"x": 4.0, "y": 1.5}
    assert rec(element_ids=["r_L0_a"], building=B)["place"] == {"x": 2.0, "y": 1.5}
    with pytest.raises(ValueError, match="nearest"):
        rec(element_ids=["w_L0_09"], level="L0", building=B)


def test_crop_written(tmp_path):
    p = remark.draw_crop(B, "L0", {"x": 2, "y": 1}, ["w_L0_001"], tmp_path / "C0001.png")
    assert p.is_file() and p.stat().st_size > 1000
    q = remark.draw_crop(B, "L0", None, [], tmp_path / "whole.png")
    assert q.stat().st_size > 1000


def test_add_redo_list(tmp_path, monkeypatch):
    f, crops = tmp_path / "c.jsonl", tmp_path / "crops"
    (tmp_path / "building.json").write_text(json.dumps(B))
    monkeypatch.setattr(remark, "project_names", lambda: ["real10"])
    monkeypatch.setattr(remark, "lesson_ids", lambda: [])
    ns = argparse.Namespace(project="real10", text="window here", level=None, place=None, element=["w_L0_002"],
                            kind="window", reader_answer="a", right_answer="b", lesson=None,
                            out=str(tmp_path), truth_action=None)
    r, crop = remark.add(ns, f, crops)
    assert r["id"] == "C0001" and crop.is_file()
    r2, _ = remark.add(ns, f, crops)
    assert r2["id"] == "C0002"
    r3, c3 = remark.redo("C0001", {"x": 1.0, "y": 1.0}, f, crops, building=B, date="2026-11-06")
    assert r3["place"] == {"x": 1.0, "y": 1.0}
    assert r3["history"] == [{"date": "2026-11-06", "old_place": {"x": 4.0, "y": 1.5}}]
    assert remark.load(f)[0]["history"] and c3.is_file()
    got = remark.select(remark.load(f), "real10", "2026-01-01")
    assert [x["id"] for x in got] == ["C0001", "C0002"]
    assert remark.select(remark.load(f), "real09") == []
    assert remark.select(remark.load(f), since="2999-01-01") == []
    assert "window here" in remark.table(remark.load(f))


def test_a_placeable_remark_is_refused_without_a_place_or_a_place_note(tmp_path, monkeypatch):
    """Review of 5 Nov 2026: `remark add` enforces the place rule of truth.correction_errors at capture: a wall,
    door, window, opening, room or stair remark needs --place, --element (its place is taken) or --place-note."""
    for kind in remark.PLACEABLE_KINDS:
        with pytest.raises(ValueError, match="needs its place"):
            rec(kind=kind)
    r = rec(kind="wall", place_note="the walls were removed the same day; their places are not recorded")
    assert r["place"] is None and r["place_note"].startswith("the walls")
    assert correction_errors([r], [], ["real10"]) == []
    with pytest.raises(ValueError, match="--place-note"):
        rec(kind="door", place_note="   ")                                  # a blank note is no note
    assert rec(kind="wall", element_ids=["w_L0_002"], building=B)["place"] == {"x": 4.0, "y": 1.5}
    assert rec(kind="level")["place"] is None and "place_note" not in rec(kind="level")
    # the command line: --place-note reaches the record; without it the record is not written
    f, crops = tmp_path / "c.jsonl", tmp_path / "crops"
    monkeypatch.setattr(remark, "project_names", lambda: ["real10"])
    monkeypatch.setattr(remark, "lesson_ids", lambda: [])
    monkeypatch.setattr(remark, "CORRECTIONS_PATH", f)
    assert remark.main(["add", "--project", "real10", "--text", "This wall do not exist", "--kind", "wall"]) == 2
    assert not f.exists()
    ns = argparse.Namespace(project="real10", text="This wall do not exist", level="L1", place=None, element=None,
                            kind="wall", reader_answer="", right_answer="", lesson=None, out=None,
                            truth_action=None, place_note="removed the same day")
    rec_, crop = remark.add(ns, f, crops)
    assert rec_["place_note"] == "removed the same day" and crop is None and remark.load(f)[0]["id"] == "C0001"


def test_the_crop_can_show_the_drawing(tmp_path):
    """Review of 5 Nov 2026: a crop may carry the drawing's own strokes (the jambs and swings a place was taken
    from); without a converted DXF there are none."""
    assert remark.drawing_lines(tmp_path, B, "L0", {"x": 1, "y": 1}) == []
    p = remark.draw_crop(B, "L0", {"x": 2, "y": 1}, [], tmp_path / "C0002.png",
                         lines=[((1.0, 0.0), (1.0, 0.1)), ((1.9, 0.0), (1.9, 0.1))])
    assert p.is_file() and p.stat().st_size > 1000
