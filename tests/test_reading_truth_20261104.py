"""4 Nov 2026, Milestone 14 track R1 (user: "I want structure recognition to be cumulatively better with the feedbacks
I am giving"; review findings of 5 Nov 2026): the truth corpus from a building dict, the user's explicit acceptance,
the drift check, the synthetic truth, the merge that protects user corrections, add / remove, the matching rules of
the reading score (a hit, a near miss over the tolerance, a label fold), the weighted total, the gate, and the
correction store's records. CPU only, pure parts, no LibreDWG (one DXF reading of a synthetic project at the end)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[1]
ACCEPTED = {"accepted_by_user": True, "accepted_on": "2026-11-04", "accepted_scope": "all",
            "accepted_note": "user: 'yes accept the baselines'"}


def building() -> dict:
    """A two-level house: a salon and a Turkish-labelled bedroom, a door, a window, a passage, walls and a U stair."""
    return {
        "project": {"id": "tiny"}, "status": "ok",
        "levels": [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0},
                   {"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0, "label_source": "assumed"}],
        "rooms": [
            {"id": "r_L0_salon", "level_id": "L0", "label": "Salon", "room_type": "living", "status": "verified",
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
             "width": 0.9, "status": "verified", "evidence": [{"method": "vector", "confidence": 0.95}]},
            {"id": "win_L0_001", "type": "window", "level_id": "L0", "wall_id": "w_L0_001", "center": [3.0, 0.0],
             "width": 1.5, "evidence": [{"method": "vector", "confidence": 0.7}]},
            {"id": "op_L0_001", "type": "opening", "level_id": "L0", "wall_id": "w_L0_002", "center": [10.0, 2.0],
             "width": 1.2, "lift_door": True, "evidence": [{"method": "inferred", "confidence": 0.6}]},
        ],
        "walls": [
            {"id": "w_L0_001", "level_id": "L0", "start": [0, 0], "end": [10, 0], "thickness": 0.25,
             "status": "verified", "evidence": [{"method": "vector", "confidence": 0.8}]},
            {"id": "w_L0_002", "level_id": "L0", "start": [10, 0], "end": [10, 4], "thickness": 0.25,
             "status": "verified", "evidence": []},
            {"id": "w_L0_003", "level_id": "L0", "start": [6, 0], "end": [6, 4], "thickness": 0.10,
             "status": "inferred", "inferred": True, "evidence": []},
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


def numbers_of(b: dict) -> dict:
    """The regression set's key numbers of the tiny building (what ``regress.numbers`` returns, without the check)."""
    per = {}
    for lv in b["levels"]:
        lid = lv["id"]
        ops = [o for o in b["openings"] if o["level_id"] == lid]
        rooms = [r for r in b["rooms"] if r["level_id"] == lid]
        per[lid] = {"rooms": len(rooms), "walls": sum(1 for w in b["walls"] if w["level_id"] == lid),
                    "doors": sum(1 for o in ops if o["type"] == "door"),
                    "windows": sum(1 for o in ops if o["type"] == "window"),
                    "openings": sum(1 for o in ops if o["type"] not in ("door", "window")),
                    "room_area": round(sum(r["area_computed"] for r in rooms), 1)}
    return {"project": "tiny", "status": "ok", "levels": [lv["id"] for lv in b["levels"]], "levels_left_out": [],
            "per_level": per, "check": {"verdict": "ready", "counts": {"critical": 0}, "stacking": {}}}


# --- the truth of a building ----------------------------------------------------------------------------------------

def test_truth_extraction_from_a_building_dict():
    t = TR.extract(building(), project="tiny", status="accepted", commit="abc123", date="2026-11-04")
    assert t["project"] == "tiny" and t["source"] == "accepted_reading" and t["commit"] == "abc123"
    assert [lv["id"] for lv in t["levels"]] == ["L0", "L1"] and t["levels"][1]["elevation"] == 3.0
    assert t["levels"][1]["label_source"] == "assumed" and "label_source" not in t["levels"][0]
    assert TR.counts(t) == {"levels": 2, "rooms": 3, "doors": 1, "windows": 1, "openings": 1, "walls": 4, "stairs": 1}
    l0 = t["per_level"]["L0"]
    salon = l0["rooms"][0]
    assert salon["centroid"] == [3.0, 2.0] and salon["area"] == 24.0 and salon["confidence"] == 0.9
    assert salon["source"] == "accepted_reading" and salon["room_type"] == "living"
    assert salon["status"] == "verified" and salon["method"] == "vector"           # kept: status and method
    assert l0["doors"][0]["wall_id"] == "w_L0_003" and l0["doors"][0]["confidence"] == 0.95
    assert l0["openings"][0]["lift_door"] is True and l0["openings"][0]["method"] == "inferred"
    assert l0["windows"][0]["width"] == 1.5 and "lift_door" not in l0["windows"][0]
    assert l0["walls"][2]["status"] == "inferred" and l0["walls"][2]["inferred"] is True
    assert l0["walls"][0]["confidence"] == 0.8 and l0["walls"][1]["method"] is None
    assert l0["stairs"][0]["turn"] == "U" and len(l0["stairs"][0]["flights"]) == 2       # the sofa is no stair
    assert l0["rooms"][1]["confidence"] == 0.8 and t["per_level"]["L1"]["rooms"][0]["confidence"] is None
    # a level the baseline left out stays out of the truth; the source is stamped on every element
    left = TR.extract(building(), leave_out=["1. KAT"], source="synthetic")
    assert [lv["id"] for lv in left["levels"]] == ["L0"] and left["levels_left_out"] == ["1. KAT"]
    assert {e["source"] for lv in left["per_level"].values() for k in TR.ELEMENT_TYPES for e in lv[k]} == {"synthetic"}


def test_a_reading_against_its_own_truth_scores_100():
    t = TR.extract(building(), project="tiny")
    res = SC.match(t, copy.deepcopy(t))
    assert res["total"] == 100.0
    assert all(res[k]["f1"] == 1.0 for k in SC.TYPES)


# --- acceptance, drift, commit, synthetic, merge --------------------------------------------------------------------

def test_the_truth_needs_the_users_explicit_acceptance_not_the_pipelines_ok():
    b = building()
    base = numbers_of(b)                                       # status ok, verdict ready: the pipeline's own word
    assert TR.acceptance(base) is None
    truth, msgs = TR.truth_of("tiny", b, base, numbers=numbers_of(b), commit="c1")
    assert truth is None and "not accepted by the user" in msgs[0]
    acc = TR.acceptance(dict(base, **ACCEPTED))
    assert acc == {"scope": "all", "levels": None, "on": "2026-11-04", "note": "user: 'yes accept the baselines'"}
    truth, msgs = TR.truth_of("tiny", b, dict(base, **ACCEPTED), numbers=numbers_of(b), commit="c1")
    assert msgs == [] and truth["status"] == "accepted" and truth["commit"] == "c1"
    assert truth["accepted"]["on"] == "2026-11-04" and "drift" not in truth
    # a partial acceptance keeps the levels the user saw; levels left out stay out
    part = dict(base, **dict(ACCEPTED, accepted_scope="partial", accepted_levels=["L0"]))
    truth, _ = TR.truth_of("tiny", b, part, commit="c1")
    assert [lv["id"] for lv in truth["levels"]] == ["L0"] and truth["status"] == "partial"
    assert list(truth["per_level"]) == ["L0"]
    truth, _ = TR.truth_of("tiny", b, dict(base, **ACCEPTED, levels_left_out=["1. Kat"]), commit="c1")
    assert truth["status"] == "partial" and [lv["id"] for lv in truth["levels"]] == ["L0"]


def test_a_reading_that_drifted_from_the_accepted_numbers_is_marked():
    b = building()
    base = dict(numbers_of(b), **ACCEPTED)
    drifted = copy.deepcopy(b)
    for i in range(3):                                          # three doors more than the user accepted
        drifted["openings"].append({"id": f"d_L0_x{i}", "type": "door", "level_id": "L0", "center": [1 + i, 4.0],
                                    "width": 0.8, "evidence": []})
    assert TR.drift(base, numbers_of(drifted)) == ["L0 doors: 1 -> 4"]
    truth, msgs = TR.truth_of("tiny", drifted, base, numbers=numbers_of(drifted), commit="c2")
    assert truth["status"] == "drifted" and truth["drift"] == ["L0 doors: 1 -> 4"] and "drifted" in msgs[0]
    fewer = copy.deepcopy(b)
    fewer["walls"] = fewer["walls"][:2]                          # 3 -> 2 walls: within the baseline's tolerance (2)
    assert TR.drift(base, numbers_of(fewer)) == []
    fewer["walls"] = [w for w in fewer["walls"] if w["level_id"] != "L0"]        # 3 -> 0: a drift
    assert TR.drift(base, numbers_of(fewer)) == ["L0 walls: 3 -> 0"]
    # a better verdict or status is no drift of the content; a level the user never saw is
    worse_base = dict(base, status="needs_review", check={"verdict": "fix before a pod run",
                                                           "counts": {"critical": 1}, "stacking": {}})
    assert TR.drift(worse_base, numbers_of(b)) == []
    more = copy.deepcopy(b)
    more["levels"].append({"id": "L2", "label": "2. Kat", "order": 2, "elevation": 6.0})
    assert TR.drift(base, numbers_of(more)) == []                                 # more levels: no count drift
    truth, msgs = TR.truth_of("tiny", more, base, numbers=numbers_of(more), commit="c3")
    assert truth["status"] == "drifted" and truth["drift"] == ["levels not accepted: ['L2']"]
    # a level the baseline left out stays out and is no drift (the user accepted the reading without it)
    truth, msgs = TR.truth_of("tiny", more, dict(base, levels_left_out=["2. Kat"]), numbers=numbers_of(more),
                              commit="c3")
    assert msgs == [] and [lv["id"] for lv in truth["levels"]] == ["L0", "L1"] and truth["status"] == "partial"


def test_the_commit_stamp_of_a_reading(tmp_path):
    assert TR.read_commit(tmp_path) == "unknown"
    (tmp_path / "reading_check").mkdir()
    (tmp_path / "reading_check" / "commit.txt").write_text("abc123def\n", encoding="utf-8")
    assert TR.read_commit(tmp_path) == "abc123def"


def test_a_synthetic_projects_exact_truth_is_the_truth(tmp_path):
    # the new format (synthetic-08 to -22) and a building dict (synthetic-01 to -07)
    p08 = TR.synthetic_truth_file("synthetic-08-spaced-labels")
    assert p08 is not None and p08.name == "reading_truth.json"
    t = TR.synthetic_truth("synthetic-08-spaced-labels", p08)
    assert t["source"] == "synthetic" and t["status"] == "accepted" and t["commit"] is None
    assert t["failure_class"] == "spaced_labels" and t["truth_file"].startswith("projects/synthetic-08")
    assert all(e["source"] == "synthetic" for lv in t["per_level"].values() for k in TR.ELEMENT_TYPES
               for e in lv[k])
    assert all(r.get("centroid") for lv in t["per_level"].values() for r in lv["rooms"])
    p06 = TR.synthetic_truth_file("synthetic-06")
    assert p06 is not None and p06.name == "building.json"
    t6 = TR.synthetic_truth("synthetic-06", p06)
    assert t6["source"] == "synthetic" and TR.counts(t6)["rooms"] == 6
    assert "synthetic-06" in TR.synthetic_projects() and "synthetic-22-curved-stair" in TR.synthetic_projects()
    assert TR.synthetic_truth_file("real10") is None
    # a hand-made file in the new format
    (tmp_path / "truth").mkdir()
    (tmp_path / "truth" / "reading_truth.json").write_text(json.dumps({
        "project": "s", "source": "synthetic", "levels": [{"id": "L0", "label": "Z", "elevation": 0, "order": 0}],
        "per_level": {"L0": {"rooms": [{"id": "r1", "label": "SALON", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}],
                             "doors": [{"id": "d1", "center": [2, 0], "width": 0.9, "type": "door"}],
                             "windows": [], "openings": [], "walls": [], "stairs": []}}}), encoding="utf-8")
    ts = TR.synthetic_truth("s", tmp_path / "truth" / "reading_truth.json")
    assert ts["per_level"]["L0"]["rooms"][0]["centroid"] == [2.0, 2.0] and ts["levels"][0]["source"] == "synthetic"


def test_a_build_never_overwrites_a_user_correction_or_a_synthetic_element():
    new = TR.extract(building(), project="tiny")
    existing = copy.deepcopy(new)
    existing["per_level"]["L0"]["doors"].append({"id": "uc_L0_door_001", "type": "door", "center": [8.0, 4.0],
                                                 "width": 0.9, "source": "user_correction", "correction": "C0012"})
    existing["per_level"]["L0"]["windows"][0] = dict(existing["per_level"]["L0"]["windows"][0], absent=True,
                                                      source="user_correction", correction="C0013")
    existing["per_level"]["L2"] = {k: [] for k in TR.ELEMENT_TYPES}
    existing["per_level"]["L2"]["rooms"].append({"id": "uc_L2_room_001", "label": "Oda", "centroid": [1, 1],
                                                 "polygon": [], "source": "user_correction"})
    existing["levels"].append({"id": "L2", "label": None, "elevation": None, "order": None,
                               "source": "user_correction"})
    existing["corrections"] = ["C0012", "C0013"]
    merged = TR.merge(existing, new)
    l0 = merged["per_level"]["L0"]
    assert [d["id"] for d in l0["doors"]] == ["d_L0_001", "uc_L0_door_001"]
    assert l0["windows"][0]["absent"] is True and len(l0["windows"]) == 1          # the negation wins over the new
    assert [lv["id"] for lv in merged["levels"]] == ["L0", "L1", "L2"] and merged["per_level"]["L2"]["rooms"]
    assert merged["corrections"] == ["C0012", "C0013"] and merged["kept_from_previous"] == 3
    assert TR.merge(None, new) is new
    # a synthetic element is protected against an accepted-reading build (the same id: the synthetic one wins),
    # not against a synthetic one
    syn = TR.extract(building(), project="tiny", source="synthetic")
    walls = TR.merge(syn, new)["per_level"]["L0"]["walls"]
    assert len(walls) == 3 and {w["source"] for w in walls} == {"synthetic"}
    new_only = copy.deepcopy(new)
    new_only["per_level"]["L0"]["walls"][0]["id"] = "w_L0_new"
    assert len(TR.merge(syn, new_only)["per_level"]["L0"]["walls"]) == 4     # 1 new id + 3 protected synthetic
    assert len(TR.merge(syn, syn)["per_level"]["L0"]["walls"]) == 3 and "kept_from_previous" not in TR.merge(syn, syn)


def test_add_and_remove_put_a_user_correction_into_the_truth():
    t = TR.new_truth("real09")
    assert t["status"] == "partial" and t["levels"] == []
    TR.add_element(t, "door", "L0", {"center": "4.2,3.6", "width": "0.9", "wall_id": "w_L0_007"},
                   correction="C0012", date="2026-11-05")
    d = t["last_added"]
    assert d["id"] == "uc_L0_door_001" and d["center"] == [4.2, 3.6] and d["width"] == 0.9
    assert d["source"] == "user_correction" and d["correction"] == "C0012" and d["method"] == "user"
    assert [lv["id"] for lv in t["levels"]] == ["L0"] and t["levels"][0]["source"] == "user_correction"
    assert t["corrections"] == ["C0012"]
    TR.add_element(t, "room", "L0", {"label": "Merdiven", "room_type": "stair", "polygon": "0,0;3,0;3,4;0,4"},
                   correction="C0006")
    r = t["last_added"]
    assert r["centroid"] == [1.5, 2.0] and r["polygon"][2] == [3.0, 4.0] and r["id"] == "uc_L0_room_001"
    TR.add_element(t, "wall", "L0", {"start": "0,0", "end": "6,0", "thickness": "0.25"})
    TR.add_element(t, "stair", "L0", {"center": "1.5,2", "size": "2.6,2.2", "turn": "U"})
    TR.add_element(t, "level", "L1", {"label": "1. Normal Kat", "elevation": "3.0", "order": "1"}, correction="C0005")
    assert t["levels"][1] == {"id": "L1", "label": "1. Normal Kat", "elevation": 3.0, "order": 1,
                              "source": "user_correction", "correction": "C0005"}
    assert TR.counts(t) == {"levels": 2, "rooms": 1, "doors": 1, "windows": 0, "openings": 0, "walls": 1, "stairs": 1}
    with pytest.raises(ValueError):
        TR.add_element(t, "window", "L0", {"width": "1.2"})                       # no place
    with pytest.raises(ValueError):
        TR.add_element(t, "sofa", "L0", {"center": "1,1"})
    # remove: by id, by place (within the tolerance), or a new absent entry
    TR.remove_element(t, "door", "L0", {"id": "uc_L0_door_001"}, correction="C0020")
    assert t["last_removed"]["absent"] is True and t["last_removed"]["correction"] == "C0020"
    assert TR.counts(t)["doors"] == 0 and len(t["per_level"]["L0"]["doors"]) == 1
    TR.add_element(t, "window", "L0", {"center": "3,0", "width": "1.5"})
    TR.remove_element(t, "window", "L0", {"center": "3.2,0.1"})                   # 0.22 m: the same window
    assert len(t["per_level"]["L0"]["windows"]) == 1 and t["per_level"]["L0"]["windows"][0]["absent"] is True
    TR.remove_element(t, "window", "L0", {"center": "9,0"}, correction="C0021")   # nothing there: a new negation
    assert len(t["per_level"]["L0"]["windows"]) == 2 and t["last_removed"]["id"] == "uc_L0_window_absent_001"
    assert t["corrections"] == ["C0005", "C0006", "C0012", "C0020", "C0021"]
    # the score penalises a reading that has the negated door and misses nothing else
    read = {"levels": [{"id": "L0"}, {"id": "L1"}],
            "per_level": {"L0": {"rooms": [dict(r)], "doors": [{"center": [4.25, 3.6]}], "windows": [],
                                 "openings": [], "walls": [t["per_level"]["L0"]["walls"][0]],
                                 "stairs": [t["per_level"]["L0"]["stairs"][0]]},
                          "L1": {k: [] for k in TR.ELEMENT_TYPES}}}
    res = SC.match(t, read)
    assert res["doors"] == {"truth": 0, "read": 1, "matched": 0, "absent_hits": 1, "recall": 1.0, "precision": 0.0,
                            "f1": 0.0}
    assert res["rooms"]["f1"] == 1.0 and res["walls"]["f1"] == 1.0 and res["stairs"]["f1"] == 1.0
    assert res["total"] == pytest.approx(100 * 12 / 14, abs=0.01)             # doors weigh 2 of 14 with F1 0


# --- the matching rules ---------------------------------------------------------------------------------------------

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


def test_the_greedy_assignment_is_no_maximum_matching_a_known_limit():
    truth = [{"center": [0.0, 0.0]}, {"center": [0.25, 0.0]}]
    read = [{"center": [0.20, 0.0]}, {"center": [0.45, 0.0]}]
    assert SC.match_points(truth, read, SC.OPENING_CENTER_M) == [(1, 0)]    # B-X first; A-Y is 0.45, out of reach
    # a maximum matching would give A-X (0.20) and B-Y (0.20): two matches; the greedy choice gives one


def test_walls_match_by_overlap_lateral_offset_and_thickness():
    t = {"start": [0, 0], "end": [10, 0], "thickness": 0.25}
    assert SC.wall_overlap(t, {"start": [2, 0.1], "end": [8, 0.1], "thickness": 0.22}) == (1.0, 0.1)
    assert SC.wall_overlap(t, {"start": [4, 0], "end": [16, 0], "thickness": 0.25}) == (0.6, 0.0)  # 6 of 10
    assert SC.wall_overlap(t, {"start": [6, 0], "end": [16, 0], "thickness": 0.25}) is None         # 4 of 10
    assert SC.wall_overlap(t, {"start": [2, 0.2], "end": [8, 0.2], "thickness": 0.25}) is None      # 0.20 m off
    assert SC.wall_overlap(t, {"start": [2, 0], "end": [8, 0], "thickness": 0.32}) is None          # 7 cm thicker
    assert SC.wall_overlap(t, {"start": [5, -3], "end": [5, 3], "thickness": 0.25}) is None         # across it
    assert SC.match_walls([t], [{"start": [8, 0], "end": [2, 0], "thickness": 0.25}]) == [(0, 0)]   # reversed


# --- the total and the gate -----------------------------------------------------------------------------------------

def test_the_weighted_total_counts_invented_types_and_the_partial_truth():
    per = {k: {"truth": 1, "read": 1, "matched": 1, "f1": 1.0} for k in SC.TYPES}
    assert SC.total(per) == 100.0
    per["walls"]["f1"] = 0.0                                              # weight 1 of 17
    assert SC.total(per) == pytest.approx(100 * 16 / 17, abs=0.01)
    per["stairs"] = {"truth": 0, "read": 3, "matched": 0, "f1": 0.0}      # invented stairs: weight 3 with F1 0
    assert SC.total(per) == pytest.approx(100 * 13 / 17, abs=0.01)
    per["stairs"] = {"truth": 0, "read": 0, "matched": 0, "f1": 1.0}      # neither side has stairs: not weighed
    assert SC.total(per) == pytest.approx(100 * 13 / 14, abs=0.01)
    # a reading that loses the bedroom's door and adds a wall
    t = TR.extract(building(), project="tiny")
    b = building()
    b["openings"] = [o for o in b["openings"] if o["id"] != "d_L0_001"]
    b["walls"].append({"id": "w_L0_009", "level_id": "L0", "start": [0, 4], "end": [10, 4], "thickness": 0.25})
    res = SC.match(t, TR.extract(b))
    assert res["doors"] == {"truth": 1, "read": 0, "matched": 0, "absent_hits": 0, "recall": 0.0, "precision": 0.0,
                            "f1": 0.0}
    assert res["walls"]["precision"] == 0.8 and res["walls"]["recall"] == 1.0
    assert res["total"] == pytest.approx(100 * (17 - 2 - 1 * (1 - res["walls"]["f1"])) / 17, abs=0.01)
    # a partial truth scores only its levels; an accepted one counts the extra level's elements as read
    partial = TR.extract(building(), status="partial", leave_out=["1. Kat"])
    assert SC.match(partial, TR.extract(building()))["total"] == 100.0
    accepted = TR.extract(building(), leave_out=["1. Kat"])
    full = SC.match(accepted, TR.extract(building()))
    assert full["levels"]["precision"] == 0.5 and full["walls"]["read"] == 4 and full["total"] < 100.0


def test_the_gate_falls_and_holds():
    stored = [{"commit": "a", "overall": 90.0, "projects": {"p1": {"total": 95.0}, "p2": {"total": 85.0}}},
              {"commit": "b", "overall": 96.0, "projects": {"p1": {"total": 96.0}}},       # a subset run after
              {"commit": "c", "overall": 0.0, "projects": {"p1": {"total": 0.0, "error": "no DXF"}}}]  # never a base
    last = SC.latest(stored)
    assert last["projects"]["p1"] == {"total": 96.0, "commit": "b"} and last["projects"]["p2"]["commit"] == "a"
    assert last["overall"] == 90.5 and SC.latest([]) is None and SC.falls(None, last) == []
    held = {"overall": 90.1, "projects": {"p1": {"total": 94.5}, "p2": {"total": 85.7}}}
    assert SC.falls(last, held) == []
    fell = {"overall": 89.9, "projects": {"p1": {"total": 93.9}, "p2": {"total": 85.9}}}
    assert SC.falls(last, fell) == ["overall: 90.50 -> 89.90", "p1: 96.00 -> 93.90"]
    subset = {"overall": 95.5, "projects": {"p1": {"total": 95.5}, "p9": {"total": 10.0}}}  # p9 scored first time
    assert SC.falls(last, subset) == []                                                      # a subset run
    assert SC.falls(last, subset, full=True) == ["p2: 85.00 -> not scored"]                  # a full run
    failed = {"overall": 96.0, "projects": {"p1": {"total": 96.0}, "p2": {"total": 0.0, "error": "no DXF"}}}
    assert SC.falls(last, failed) == ["overall: 90.50 -> 48.00", "p2: 85.00 -> 0.00 (reading failed: no DXF)"]
    assert SC.overall({"p1": {"total": 95.0}, "p2": {"total": 85.0}, "p3": {"total": 0.0, "error": "x"}}) == 90.0


def test_the_scores_file_keeps_a_note_and_reads_the_first_versions_list(tmp_path):
    path = tmp_path / "scores.json"
    assert SC.load_scores(path) == []
    path.write_text(json.dumps([{"commit": "a", "projects": {}}]), encoding="utf-8")         # the first version
    assert SC.load_scores(path) == [{"commit": "a", "projects": {}}]
    SC.save_scores([{"commit": "b", "projects": {}}], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "equals the truth by construction" in data["note"] and SC.load_scores(path) == [{"commit": "b",
                                                                                               "projects": {}}]


# --- the correction store -------------------------------------------------------------------------------------------

def test_the_correction_records_parse_and_point_at_real_lessons_and_projects():
    records = TR.load_corrections()
    assert len(records) >= 40, "the 3 and 4 Nov 2026 corrections (UL274 to UL328) are backfilled"
    lessons = json.loads((REPO / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    ids = {l["id"] for l in lessons["lessons"]}
    projects = {p.name for p in (REPO / "projects").iterdir() if p.is_dir()}
    assert TR.correction_errors(records, ids, projects) == []
    # 5 Nov 2026: the store grows (the user's remarks through `remark add`, the machine's proposals); the backfill
    # records keep their shape, every record has a known source and status, the ids stay sequential
    backfill = [r for r in records if r["source"] == "backfill_progress"]
    assert len(backfill) >= 40 and all(r["status"] == "accepted" for r in backfill)
    assert all(r["date"] in ("2026-11-03", "2026-11-04") for r in backfill)
    assert all(r["source"] in ("backfill_progress", "user_review", "machine_review") for r in records)
    assert all(r["status"] in ("accepted", "proposed", "rejected") for r in records)
    assert all(r["id"] == f"C{i + 1:04d}" for i, r in enumerate(records))
    assert {r["project"] for r in records} >= {"real07", "real09", "real10", "real17", "real19"}
    assert all(len(r["date"]) == 10 and r["date"][:4] == "2026" for r in records)
    assert all(r.get("note") for r in records if r["lesson"] is None)          # no lesson: the note says why
    # the checker itself
    bad = [{"id": "C0001", "date": "2026-11-04", "project": "nowhere", "level": None, "place": {"x": 1},
            "element_kind": "sofa", "reader_answer": "", "right_answer": "", "user_words": "", "lesson": "UL999",
            "source": "backfill_progress", "status": "accepted"},
           {"id": "C0002", "date": "2026-11-04", "project": "real10", "level": None, "place": None,
            "element_kind": "door", "reader_answer": "", "right_answer": "", "user_words": "", "lesson": None,
            "source": "backfill_progress", "status": "accepted"}]
    errs = TR.correction_errors(bad, ids, projects)
    assert len(errs) == 5 and any("place" in e for e in errs) and any("UL999" in e for e in errs)
    assert any("null without a note" in e for e in errs)


# --- a synthetic failure class against its exact truth (one DXF reading, seconds) -----------------------------------

@pytest.mark.xfail(strict=True, reason="synthetic-06 scored against its exact truth stays below 100 until the reader "
                                       "handles what it misreads (Milestone 14 R1: the first honest number)")
def test_synthetic_06_against_its_exact_truth_scores_100(tmp_path):
    folder = TR.reading("synthetic-06", tmp_path)
    b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
    truth = TR.synthetic_truth("synthetic-06", TR.synthetic_truth_file("synthetic-06"))
    assert TR.read_commit(folder) != "unknown"
    assert SC.match(truth, TR.extract(b))["total"] == 100.0
