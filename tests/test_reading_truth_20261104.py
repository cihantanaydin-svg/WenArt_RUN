"""4 Nov 2026, Milestone 14 track R1 (user: "I want structure recognition to be cumulatively better with the feedbacks
I am giving"): the truth corpus from a building dict, the matching rules of the reading score (a hit, a near miss over
the tolerance, a label fold), the weighted total, the gate, and the correction store's records. CPU only, pure parts,
no LibreDWG."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[1]


def building() -> dict:
    """A two-level house: a salon and a Turkish-labelled bedroom, a door, a window, a passage, walls and a U stair."""
    return {
        "project": {"id": "tiny"}, "status": "ok",
        "levels": [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0},
                   {"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}],
        "rooms": [
            {"id": "r_L0_salon", "level_id": "L0", "label": "Salon", "room_type": "living",
             "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "area_computed": 24.0,
             "evidence": [{"method": "vector", "confidence": 0.9}]},
            {"id": "r_L0_cocuk", "level_id": "L0", "label": "Çocuk Odası", "room_type": "bedroom",
             "polygon": [[6, 0], [10, 0], [10, 4], [6, 4]], "area_computed": 16.0,
             "evidence": [{"method": "ocr", "confidence": 0.8}]},
            {"id": "r_L1_oda", "level_id": "L1", "label": "Oda", "room_type": "bedroom",
             "polygon": [[0, 0], [10, 0], [10, 4], [0, 4]], "area_computed": 40.0, "evidence": []},
        ],
        "openings": [
            {"id": "d_L0_001", "type": "door", "level_id": "L0", "wall_id": "w_L0_003", "center": [6.0, 2.0],
             "width": 0.9, "evidence": [{"method": "vector", "confidence": 0.95}]},
            {"id": "win_L0_001", "type": "window", "level_id": "L0", "wall_id": "w_L0_001", "center": [3.0, 0.0],
             "width": 1.5, "evidence": [{"method": "vector", "confidence": 0.7}]},
            {"id": "op_L0_001", "type": "opening", "level_id": "L0", "wall_id": "w_L0_002", "center": [10.0, 2.0],
             "width": 1.2, "evidence": []},
        ],
        "walls": [
            {"id": "w_L0_001", "level_id": "L0", "start": [0, 0], "end": [10, 0], "thickness": 0.25,
             "status": "verified", "evidence": [{"method": "vector", "confidence": 0.8}]},
            {"id": "w_L0_002", "level_id": "L0", "start": [10, 0], "end": [10, 4], "thickness": 0.25,
             "status": "verified", "evidence": []},
            {"id": "w_L0_003", "level_id": "L0", "start": [6, 0], "end": [6, 4], "thickness": 0.10,
             "status": "inferred", "evidence": []},
            {"id": "w_L1_001", "level_id": "L1", "start": [0, 0], "end": [10, 0], "thickness": 0.25,
             "status": "verified", "evidence": []},
        ],
        "furniture": [
            {"id": "f_L0_001", "level_id": "L0", "room_id": "r_L0_salon", "type": "stair",
             "footprint": {"center": [1.5, 2.0], "size": [2.6, 2.2], "rotation_deg": 0.0},
             "stair": {"turn": "U", "flights": [{"start": [0.8, 1.0], "end": [0.8, 3.0], "width": 1.0, "lines": 6},
                                                {"start": [2.2, 3.0], "end": [2.2, 1.0], "width": 1.0, "lines": 6}]},
             "evidence": [{"method": "rule", "confidence": 0.9}]},
            {"id": "f_L0_002", "level_id": "L0", "room_id": "r_L0_salon", "type": "sofa",
             "footprint": {"center": [4.0, 2.0], "size": [2.0, 0.9], "rotation_deg": 0.0}, "evidence": []},
        ],
    }


def test_truth_extraction_from_a_building_dict():
    t = TR.extract(building(), project="tiny", status="accepted", commit="abc123", date="2026-11-04")
    assert t["project"] == "tiny" and t["source"] == "accepted_reading" and t["commit"] == "abc123"
    assert [lv["id"] for lv in t["levels"]] == ["L0", "L1"] and t["levels"][1]["elevation"] == 3.0
    assert TR.counts(t) == {"levels": 2, "rooms": 3, "doors": 1, "windows": 1, "openings": 1, "walls": 4, "stairs": 1}
    l0 = t["per_level"]["L0"]
    salon = l0["rooms"][0]
    assert salon["centroid"] == [3.0, 2.0] and salon["area"] == 24.0 and salon["confidence"] == 0.9
    assert salon["source"] == "accepted_reading" and salon["room_type"] == "living"
    assert l0["doors"][0]["wall_id"] == "w_L0_003" and l0["doors"][0]["confidence"] == 0.95
    assert l0["openings"][0]["type"] == "opening" and l0["windows"][0]["width"] == 1.5
    assert l0["walls"][2]["status"] == "inferred" and l0["walls"][0]["confidence"] == 0.8
    assert l0["stairs"][0]["turn"] == "U" and len(l0["stairs"][0]["flights"]) == 2       # the sofa is no stair
    assert l0["rooms"][1]["confidence"] == 0.8 and t["per_level"]["L1"]["rooms"][0]["confidence"] is None
    # a level the baseline left out stays out of the truth
    left = TR.extract(building(), leave_out=["1. KAT"])
    assert [lv["id"] for lv in left["levels"]] == ["L0"] and left["levels_left_out"] == ["1. KAT"]


def test_a_reading_against_its_own_truth_scores_100():
    t = TR.extract(building(), project="tiny")
    res = SC.match(t, copy.deepcopy(t))
    assert res["total"] == 100.0
    assert all(res[k]["f1"] == 1.0 for k in SC.TYPES)


def test_rooms_match_by_folded_label_and_centroid_or_by_iou():
    truth = [{"label": "Çocuk Odası", "centroid": [8.0, 2.0], "polygon": [[6, 0], [10, 0], [10, 4], [6, 4]]}]
    hit = [{"label": "COCUK ODASI", "centroid": [8.6, 2.5], "polygon": [[6, 0], [10, 0], [10, 4], [6, 4]]}]
    assert SC.match_rooms(truth, hit) == [(0, 0)]                                  # the label fold, 0.78 m
    far = [{"label": "Çocuk Odası", "centroid": [9.2, 2.0], "polygon": [[9, 1], [9.4, 1], [9.4, 3], [9, 3]]}]
    assert SC.match_rooms(truth, far) == []                                        # 1.2 m off, IoU 0.05
    other = [{"label": "Oda", "centroid": [8.0, 2.0], "polygon": [[6, 0], [10, 0], [10, 4], [6, 4]]}]
    assert SC.match_rooms(truth, other) == [(0, 0)]                                # another label, IoU 1.0
    no_label = [{"label": None, "centroid": [8.5, 2.0], "polygon": [[7, 0], [11, 0], [11, 4], [7, 4]]}]
    assert SC.match_rooms(truth, no_label) == [(0, 0)]                             # IoU 3/5 = 0.6
    assert SC.match_rooms(truth, [{"label": None, "centroid": [9.5, 2.0],
                                   "polygon": [[9, 0], [13, 0], [13, 4], [9, 4]]}]) == []     # IoU 1/7
    assert TR.norm_label("S a l o n") == "SALON" and TR.norm_label("  Çocuk  Odası ") == "COCUK ODASI"


def test_openings_and_stairs_match_by_centre_within_the_tolerance():
    truth = [{"center": [6.0, 2.0]}]
    assert SC.match_points(truth, [{"center": [6.2, 2.2]}], SC.OPENING_CENTER_M) == [(0, 0)]      # 0.28 m
    assert SC.match_points(truth, [{"center": [6.3, 2.2]}], SC.OPENING_CENTER_M) == []            # 0.36 m
    assert SC.match_points(truth, [{"center": [6.6, 2.6]}], SC.STAIR_CENTER_M) == [(0, 0)]        # 0.85 m
    assert SC.match_points(truth, [{"center": [7.0, 2.8]}], SC.STAIR_CENTER_M) == []              # 1.28 m
    # one to one, the nearest first
    two = [{"center": [6.1, 2.0]}, {"center": [6.25, 2.0]}]
    assert sorted(SC.match_points(truth + [{"center": [6.3, 2.0]}], two, SC.OPENING_CENTER_M)) == [(0, 0), (1, 1)]


def test_walls_match_by_overlap_lateral_offset_and_thickness():
    t = {"start": [0, 0], "end": [10, 0], "thickness": 0.25}
    assert SC.wall_overlap(t, {"start": [2, 0.1], "end": [8, 0.1], "thickness": 0.22}) == (1.0, 0.1)
    assert SC.wall_overlap(t, {"start": [4, 0], "end": [16, 0], "thickness": 0.25}) == (0.6, 0.0)  # 6 of 10
    assert SC.wall_overlap(t, {"start": [6, 0], "end": [16, 0], "thickness": 0.25}) is None         # 4 of 10
    assert SC.wall_overlap(t, {"start": [2, 0.2], "end": [8, 0.2], "thickness": 0.25}) is None      # 0.20 m off
    assert SC.wall_overlap(t, {"start": [2, 0], "end": [8, 0], "thickness": 0.32}) is None          # 7 cm thicker
    assert SC.wall_overlap(t, {"start": [5, -3], "end": [5, 3], "thickness": 0.25}) is None         # across it
    assert SC.match_walls([t], [{"start": [8, 0], "end": [2, 0], "thickness": 0.25}]) == [(0, 0)]   # reversed


def test_the_weighted_total_and_the_partial_truth():
    per = {k: {"truth": 1, "read": 1, "matched": 1, "f1": 1.0} for k in SC.TYPES}
    assert SC.total(per) == 100.0
    per["walls"]["f1"] = 0.0                                              # weight 1 of 17
    assert SC.total(per) == pytest.approx(100 * 16 / 17, abs=0.01)
    per["stairs"] = {"truth": 0, "read": 3, "matched": 0, "f1": 0.0}      # the truth has none: not weighed
    assert SC.total(per) == pytest.approx(100 * 13 / 14, abs=0.01)
    # a reading that loses the bedroom's door and adds a wall
    t = TR.extract(building(), project="tiny")
    b = building()
    b["openings"] = [o for o in b["openings"] if o["id"] != "d_L0_001"]
    b["walls"].append({"id": "w_L0_009", "level_id": "L0", "start": [0, 4], "end": [10, 4], "thickness": 0.25})
    res = SC.match(t, TR.extract(b))
    assert res["doors"] == {"truth": 1, "read": 0, "matched": 0, "recall": 0.0, "precision": 0.0, "f1": 0.0}
    assert res["walls"]["precision"] == 0.8 and res["walls"]["recall"] == 1.0
    assert res["total"] == pytest.approx(100 * (17 - 2 - 1 * (1 - res["walls"]["f1"])) / 17, abs=0.01)
    # a partial truth scores only its levels; an accepted one counts the extra level's elements as read
    partial = TR.extract(building(), status="partial", leave_out=["1. Kat"])
    assert SC.match(partial, TR.extract(building()))["total"] == 100.0
    accepted = TR.extract(building(), leave_out=["1. Kat"])
    full = SC.match(accepted, TR.extract(building()))
    assert full["levels"]["precision"] == 0.5 and full["walls"]["read"] == 4 and full["total"] < 100.0


def test_the_gate_falls_and_holds():
    last = {"commit": "a", "overall": 90.0, "projects": {"p1": {"total": 95.0}, "p2": {"total": 85.0}}}
    assert SC.falls(None, last) == []
    held = {"overall": 89.6, "projects": {"p1": {"total": 93.5}, "p2": {"total": 85.7}}}
    assert SC.falls(last, held) == []
    fell = {"overall": 89.4, "projects": {"p1": {"total": 92.9}, "p2": {"total": 85.9}}}
    out = SC.falls(last, fell)
    assert out == ["overall: 90.00 -> 89.40", "p1: 95.00 -> 92.90"]
    gone = {"overall": 95.0, "projects": {"p1": {"total": 95.0}}}
    assert SC.falls(last, gone) == ["p2: 85.00 -> 0.00 (not scored)"]
    assert SC.overall({"p1": {"total": 95.0}, "p2": {"total": 85.0}}) == 90.0


def test_the_correction_records_parse_and_point_at_real_lessons_and_projects():
    records = TR.load_corrections()
    assert len(records) >= 40, "the 3 and 4 Nov 2026 corrections (UL274 to UL328) are backfilled"
    lessons = json.loads((REPO / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    ids = {l["id"] for l in lessons["lessons"]}
    projects = {p.name for p in (REPO / "projects").iterdir() if p.is_dir()}
    assert TR.correction_errors(records, ids, projects) == []
    assert all(r["source"] == "backfill_progress" and r["status"] == "accepted" for r in records)
    assert all(r["id"] == f"C{i + 1:04d}" for i, r in enumerate(records))
    assert {r["project"] for r in records} >= {"real07", "real09", "real10", "real17", "real19"}
    assert all(r["date"] in ("2026-11-03", "2026-11-04") for r in records)
    # the checker itself
    bad = [{"id": "C0001", "date": "2026-11-04", "project": "nowhere", "level": None, "place": {"x": 1},
            "element_kind": "sofa", "reader_answer": "", "right_answer": "", "user_words": "", "lesson": "UL999",
            "source": "backfill_progress", "status": "accepted"}]
    errs = TR.correction_errors(bad, ids, projects)
    assert len(errs) == 4 and any("place" in e for e in errs) and any("UL999" in e for e in errs)
