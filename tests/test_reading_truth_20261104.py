"""4 Nov 2026, Milestone 14 track R1 (user: "I want structure recognition to be cumulatively better with the feedbacks
I am giving"; review findings of 5 Nov 2026): the truth corpus from a building dict, the user's explicit acceptance,
the drift check, the synthetic truth, the derived truth (the accepted reading plus the replay of the records, 6 Nov
2026), the replayed operations, the matching rules of
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
            "accepted_note": "user: 'yes accept the baselines'", "accepted_seen": "the structure run"}


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
    assert acc == {"scope": "all", "levels": None, "on": "2026-11-04", "note": "user: 'yes accept the baselines'",
                   "seen": "the structure run"}
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


def _record(rid: str, *ops: dict, **kw) -> dict:
    r = {"id": rid, "date": "2026-11-05", "project": "tiny", "level": "L0", "place": None, "element_kind": "door",
         "reader_answer": "", "right_answer": "", "user_words": "the user's words", "lesson": None, "note": "test",
         "source": "user_review", "status": "accepted", "truth_action": {"op": ops[0]["op"], "elements": list(ops)}}
    r.update(kw)
    return r


def test_the_truth_is_the_accepted_reading_and_the_replay_of_the_records():
    """6 Nov 2026 (the derived truth): no merge; the accepted entries get truth ids from a deterministic order, the
    records are replayed by place, a synthetic project's exact truth is its accepted reading."""
    acc = TR.extract(building(), project="tiny", commit="c1", date="2026-11-04")
    t = TR.build_truth("tiny", acc, [])
    assert TR.counts(t) == TR.counts(acc) and t["built_from"] == {"reading": None, "reading_commit": "c1",
                                                                   "records": []}
    l0 = t["per_level"]["L0"]
    assert [d["id"] for d in l0["doors"]] == ["t_L0_door_0001"] and l0["doors"][0]["reader_id"] == "d_L0_001"
    assert [w["id"] for w in l0["walls"]] == ["t_L0_wall_0001", "t_L0_wall_0002", "t_L0_wall_0003"]
    assert all(e["source"] == TR.SOURCE_ACCEPTED for lv in t["per_level"].values() for els in lv.values() for e in els)
    recs = [_record("C0012", {"op": "add", "kind": "door", "level": "L0", "center": [8.0, 4.0], "width": 0.9}),
            _record("C0013", {"op": "remove", "kind": "window", "level": "L0", "center": [3.0, 0.0]}),
            _record("C0014", {"op": "add", "kind": "door", "level": "L2", "center": [1.0, 1.0]}),
            _record("C0015", {"op": "add", "kind": "door", "level": "L0", "center": [1.0, 1.0]}, status="proposed"),
            dict(_record("C0016", {"op": "add", "kind": "door", "level": "L0", "center": [1.0, 1.0]}), project="x")]
    t = TR.build_truth("tiny", acc, recs)
    l0 = t["per_level"]["L0"]
    assert [(d["id"], d["source"]) for d in l0["doors"]] == [("t_L0_door_0001", "accepted_reading"),
                                                             ("u_C0012_1", "user_correction")]
    assert [(w["id"], w.get("absent")) for w in l0["windows"]] == [("u_C0013_1", True)]
    assert l0["windows"][0]["reader_id"] == "win_L0_001"        # the negated element keeps what the reading said
    assert [lv["id"] for lv in t["levels"]] == ["L0", "L1"]                 # C0014's L2 never comes in
    assert t["corrections"] == ["C0012", "C0013"] and t["built_from"]["records"] == ["C0012", "C0013", "C0014"]
    assert [u["record"] for u in t["build_report"]["unmatched"]] == ["C0014"]
    assert [n["record"] for n in t["build_report"]["not_replayed"]] == ["C0015"]   # C0016 is another project's
    assert TR.dumps(TR.build_truth("tiny", acc, recs)) == TR.dumps(t)      # the same inputs, the same bytes
    syn = TR.synthetic_truth("synthetic-06", TR.synthetic_truth_file("synthetic-06"))
    st = TR.build_truth("synthetic-06", syn, [])
    assert st["source"] == "synthetic" and TR.counts(st) == TR.counts(syn)
    assert st["built_from"]["reading"] == "projects/synthetic-06/truth/building.json"


def test_the_replayed_operations_put_a_user_correction_into_the_truth():
    acc = TR.extract(building(), project="tiny")
    ops = [{"op": "add", "kind": "door", "level": "L0", "center": [4.2, 3.6], "width": 0.9, "wall_id": "w_L0_007"},
           {"op": "add", "kind": "room", "level": "L1", "label": "Merdiven", "room_type": "stair",
            "polygon": [[0, 0], [8, 0], [8, 4], [0, 4]]},                                  # IoU 0.8 with r_L1_oda
           {"op": "add", "kind": "wall", "level": "L0", "start": [0, 9], "end": [6, 9], "thickness": 0.25},
           {"op": "add", "kind": "stair", "level": "L1", "center": [1.5, 2], "size": [2.6, 2.2], "turn": "U"},
           {"op": "add", "kind": "level", "level": "L2", "label": "2. Normal Kat", "elevation": 6.0, "order": 2},
           {"op": "add", "kind": "level", "level": "L1", "label": "1. Normal Kat"},
           {"op": "add", "kind": "window", "level": "L0", "width": 1.2},                         # no place
           {"op": "add", "kind": "sofa", "level": "L0", "center": [1, 1]}]                      # no truth kind
    t = TR.build_truth("tiny", acc, [_record("C0012", *ops)])
    d = next(e for e in t["per_level"]["L0"]["doors"] if e["id"] == "u_C0012_1")
    assert d["center"] == [4.2, 3.6] and d["width"] == 0.9 and d["method"] == "user"
    assert d["source"] == "user_correction" and d["corrections"] == ["C0012"] and d["added_on"] == "2026-11-05"
    r = t["per_level"]["L1"]["rooms"]
    assert [(x["label"], x["room_type"], x["polygon"], x["area"]) for x in r] == [
        ("Merdiven", "stair", [[0.0, 0.0], [8.0, 0.0], [8.0, 4.0], [0.0, 4.0]], 32.0)]
    assert r[0]["changed"] == ["label", "polygon", "room_type"]   # the room at the place takes the user's room
    # no correction creates a level (6 Nov 2026, review); a level the accepted reading has takes the user's label
    assert [lv["id"] for lv in t["levels"]] == ["L0", "L1"] and list(t["per_level"]) == ["L0", "L1"]
    assert t["levels"][1] == {"id": "L1", "label": "1. Normal Kat", "elevation": 3.0, "order": 1,
                              "source": "user_correction", "label_source": "assumed", "corrections": ["C0012"],
                              "correction": "C0012"}
    assert [u["why"] for u in t["build_report"]["unmatched"]] == [
        "the level 'L2' is not in the accepted reading: accept the reading first (no correction creates a level)",
        "the operation is refused: a window needs its centre",
        "the operation is refused: kind 'sofa' is no element type of the truth"]
    assert TR.counts(t) == {"levels": 2, "rooms": 3, "doors": 2, "windows": 1, "openings": 1, "walls": 5, "stairs": 2}
    # remove: the element at the place (within the tolerance) goes and a negation is written; nothing there: a
    # negation at the record's place
    rm = [{"op": "remove", "kind": "door", "level": "L0", "center": [6.1, 2.0]},
          {"op": "remove", "kind": "window", "level": "L0", "center": [3.2, 0.1]},             # 0.22 m: the window
          {"op": "remove", "kind": "window", "level": "L0", "center": [9.0, 0.0]}]
    t = TR.build_truth("tiny", acc, [_record("C0020", *rm)])
    l0 = t["per_level"]["L0"]
    assert TR.counts(t)["doors"] == 0 and [e["center"] for e in l0["doors"]] == [[6.1, 2.0]]
    assert l0["doors"][0]["absent"] is True and l0["doors"][0]["width"] == 0.9            # what the reading said
    assert [(w["center"], w["absent"]) for w in l0["windows"]] == [([3.2, 0.1], True), ([9.0, 0.0], True)]
    # the score penalises a reading that has the negated door and misses nothing else
    res = SC.match(t, TR.extract(building()))
    assert res["doors"] == {"truth": 0, "read": 1, "matched": 0, "absent_hits": 1, "recall": 1.0, "precision": 0.0,
                            "f1": 0.0}
    assert res["windows"]["absent_hits"] == 1 and res["rooms"]["f1"] == 1.0 and res["walls"]["f1"] == 1.0


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
    first = [r for r in backfill if r["lesson"] is None or 274 <= int(r["lesson"][2:]) <= 328]
    assert len(first) >= 40 and all(r["status"] == "accepted" for r in first)
    assert all(r["date"] in ("2026-11-03", "2026-11-04") for r in first)
    # 6 Nov 2026 ("there were more than 24 corrections, right?"): the reading lessons outside that window are
    # backfilled too (results/reading_corrections_sources.json sorts the 101 structural ones); each record carries its
    # lesson's date, and one without the user's own words about the place is a proposal with a note saying why
    dates = {l["id"]: l["date"] for l in lessons["lessons"]}
    classes = {row["lesson"]: row["class"] for row in json.loads(
        (REPO / "results" / "reading_corrections_sources.json").read_text(encoding="utf-8"))["lessons"]}
    later = [r for r in backfill if r not in first]
    assert later and all(r["date"] == dates[r["lesson"]] for r in later)
    assert all(classes.get(r["lesson"]) == "reading" for r in later)
    assert all(r["status"] == "accepted" or (r["status"] == "proposed" and r.get("note")) for r in later)
    assert {l for l, c in classes.items() if c == "reading"} <= {r["lesson"] for r in later}
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


def _remark(**kw) -> dict:
    base = {"id": "C0100", "date": "2026-11-05", "project": "real10", "level": "L0", "place": None,
            "element_kind": "wall", "reader_answer": "a wall", "right_answer": "no wall",
            "user_words": "This wall do not exist", "lesson": None, "note": "no lesson yet", "source": "user_review",
            "status": "accepted"}
    base.update(kw)
    return base


def test_a_placeable_remark_of_the_users_review_needs_a_place_or_a_place_note():
    """5 Nov 2026: a correction joins the truth and the ranker's labels only through its place; every future remark
    about a wall, door, window, opening, room or stair is placed at capture (or says why it cannot be)."""
    err = TR.correction_errors([_remark()], [], ["real10"])
    assert len(err) == 1 and "needs a place or a place_note" in err[0] and err[0].startswith("C0100")
    for kind in TR.PLACEABLE_KINDS:
        assert TR.correction_errors([_remark(element_kind=kind)], [], ["real10"]), kind
    ok = [_remark(place={"x": 10.87, "y": 5.69}),
          _remark(place_note="the walls were removed the same day; their places are not recorded"),
          _remark(element_kind="level"), _remark(element_kind="roof"), _remark(element_kind="label"),
          _remark(status="proposed"), _remark(source="machine_review"), _remark(source="backfill_progress")]
    for r in ok:
        assert TR.correction_errors([r], [], ["real10"]) == [], r
    assert TR.correction_errors([_remark(place_note="  ")], [], ["real10"])          # a blank note is no note
    # the located fields of the backfilled records stay consistent too
    assert "neither a place nor a place_note" in TR.correction_errors(
        [_remark(source="backfill_progress", placeable=True)], [], ["real10"])[0]
    assert "without a why" in TR.correction_errors(
        [_remark(source="backfill_progress", element_kind="level", placeable=False)], [], ["real10"])[0]
    assert TR.correction_errors([_remark(source="backfill_progress", element_kind="level", placeable=False,
                                         why="a level elevation")], [], ["real10"]) == []


def test_every_correction_record_is_placed_or_says_why_and_the_replayed_ones_are_in_the_truth():
    """5 Nov 2026: the records located on the current readings say whether they are placeable; a placed one carries
    its level, the reader's ids as hints (``reader_ids``, the one name since 6 Nov 2026: records name places), source,
    confidence and note, and a truth action of the replay's operations. 6 Nov 2026 (the derived truth): every record
    the replay may use is in its project's truth (``built_from.records``) and its operations in the build report; the
    machine's proposals, the session's own notes and the held records never are."""
    from wenart.reading_check import remark as RM

    records = TR.load_corrections()
    assert all(isinstance(r.get("placeable"), bool) for r in records)
    assert all(r.get("why") for r in records if r["placeable"] is False)
    placed = [r for r in records if r["placeable"] and r.get("place")]
    assert all(r.get("place_note") for r in records if r["placeable"])
    assert len(placed) >= 30
    for r in placed:
        assert r["level"] and r["place_source"] in ("located_by_machine", "given_by_user", "user_confirmed"), r["id"]
        assert r.get("reader_ids") or r["place_source"] == "given_by_user", r["id"]
        assert 0.0 <= float(r["place_confidence"]) <= 1.0, r["id"]
        assert RM.validate_truth_action(r["truth_action"]) is None, r["id"]
        for el in TR.record_ops(r):
            assert el["op"] in TR.OPS and el["kind"] in TR.KIND_TO_TYPE and el["level"], r["id"]
    for r in records:
        if r["status"] == "proposed" or r["source"] == "machine_review":
            assert (r.get("truth_applied") or {}).get("status") not in ("applied", "replayed"), r["id"]
    for project in TR.truth_projects():
        truth = TR.load_truth(project)
        for r in records:
            if r["project"] != project:
                continue
            replay = TR.correction_applicable(r) is None and bool(TR.record_ops(r))
            assert (r["id"] in truth["built_from"]["records"]) == replay, (project, r["id"])
    by_id = {r["id"]: r for r in records}
    assert "no user words" in TR.correction_applicable(by_id["C0022"])
    assert "UL287" in TR.correction_applicable(by_id["C0018"])               # held by the review of 5 Nov 2026
    assert "under 0.6" in TR.correction_applicable(by_id["C0021"])           # a low-confidence place waits
    real06 = TR.load_truth("real06")
    assert real06["corrections"] == ["C0063", "C0064", "C0065"]
    # C0047: one door at the drawn centre (the DXF jambs 5.34 and 6.14), the size tag's second door a double read
    doors = TR.load_truth("real07")["per_level"]["L0"]["doors"]
    kat = [e for e in doors if e["center"] == [5.74, 2.19]]
    assert len(kat) == 1 and kat[0]["width"] == 0.8 and kat[0]["evidence"] and not kat[0].get("absent")
    neg = [e for e in doors if e["center"] == [5.36, 2.19]]
    assert len(neg) == 1 and neg[0]["absent"] is True and "double read" in neg[0]["note"]
    # C0034: one lift door per floor, the south one; the reading's east one negated with the drawing's evidence
    real10 = TR.load_truth("real10")
    for lv in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        lift = [e for e in real10["per_level"][lv]["doors"] if e["center"] in ([9.666, 8.45], [10.658, 9.085])]
        assert sorted((e["center"], bool(e.get("absent"))) for e in lift) == [([9.666, 8.45], False),
                                                                              ([10.658, 9.085], True)]
        assert any(ev["layer"] == "kolon" for ev in next(e for e in lift if e.get("absent"))["evidence"])


def test_a_confirm_keeps_the_readings_element_and_collects_every_correction_id():
    """Review of 5 Nov 2026, kept by the replay: a confirm changes only the source and the correction ids (a stair
    keeps its rotation, room and flights); an add on an element replaces what the user gives (listed in
    ``changed``); an element touched by several records keeps all their ids, in record order."""
    acc = TR.extract(building(), project="tiny")
    stair = TR.build_truth("tiny", acc, [])["per_level"]["L0"]["stairs"][0]
    recs = [_record("C0016", {"op": "confirm", "kind": "stair", "level": "L0", "center": [1.6, 2.1]}),
            _record("C0027", {"op": "add", "kind": "door", "level": "L0", "center": [6.0, 2.0]}),
            _record("C0040", {"op": "add", "kind": "door", "level": "L0", "center": [6.05, 2.0], "width": 0.8}),
            _record("C0047", {"op": "remove", "kind": "door", "level": "L0", "center": [6.05, 2.0],
                              "note": "a double read"})]
    t = TR.build_truth("tiny", acc, recs[:1])
    got = t["per_level"]["L0"]["stairs"][0]
    assert {k: v for k, v in got.items() if k not in ("source", "correction", "corrections", "confirmed_on")} == \
        {k: v for k, v in stair.items() if k != "source"}
    assert got["source"] == TR.SOURCE_USER and got["corrections"] == ["C0016"] and "changed" not in got
    t = TR.build_truth("tiny", acc, recs[1:3])
    doors = t["per_level"]["L0"]["doors"]
    assert len(doors) == 1 and doors[0]["corrections"] == ["C0027", "C0040"] and doors[0]["correction"] == "C0040"
    assert doors[0]["changed"] == ["center", "width"] and doors[0]["method"] == "user"
    assert doors[0]["center"] == [6.05, 2.0] and doors[0]["id"] == "t_L0_door_0001"
    t = TR.build_truth("tiny", acc, recs[1:])
    doors = t["per_level"]["L0"]["doors"]
    assert len(doors) == 1 and doors[0]["absent"] is True and doors[0]["note"] == "a double read"
    assert doors[0]["corrections"] == ["C0027", "C0040", "C0047"]          # the negated element keeps every id
    assert TR.build_truth("tiny", acc, [_record("C0050", {"op": "confirm", "kind": "door", "level": "L0",
                                                          "center": [9.0, 9.0]})])["build_report"]["unmatched"]


def test_only_accepted_records_with_the_users_words_reach_the_truth(tmp_path, monkeypatch, capsys):
    """Review of 5 Nov 2026: a backfilled record without user words is the session's own note; a machine proposal
    waits; a remark of the user's review is the user's words itself."""
    base = _remark(source="backfill_progress", place={"x": 1.0, "y": 1.0})
    assert TR.correction_applicable(base) is None
    assert "no user words" in TR.correction_applicable(dict(base, user_words=None))
    assert TR.correction_applicable(dict(base, user_words=None, source="user_review")) is None
    assert "waits" in TR.correction_applicable(dict(base, status="proposed"))
    assert TR.correction_applicable(None) == "no such record in the correction store"
    assert "held: the hall" in TR.correction_applicable(dict(base, hold={"why": "the hall must mirror"}))
    low = dict(base, place_source="located_by_machine", place_confidence=0.5)
    assert "under 0.6" in TR.correction_applicable(low)
    assert TR.correction_applicable(dict(low, place_confidence=0.6)) is None
    err = TR.correction_errors([dict(base, user_words=None, truth_applied={"status": "applied"})], [], ["real10"])
    assert len(err) == 1 and "applied to the truth but no user words" in err[0]
    # the command line refuses it before touching the truth
    corr = tmp_path / "c.jsonl"
    corr.write_text(json.dumps(dict(base, id="C0100", user_words=None)) + "\n", encoding="utf-8")
    monkeypatch.setattr(TR, "CORRECTIONS_PATH", corr)
    monkeypatch.setattr(TR, "load_corrections", lambda path=corr: [json.loads(corr.read_text())])
    monkeypatch.setattr(TR, "TRUTH_DIR", tmp_path)
    import argparse
    args = argparse.Namespace(action="add", project="real10", level="L0", kind="door", source=None,
                              correction="C0100", date=None, id=None, center="1,1", width="0.9")
    assert TR.main(args) == 2 and "no user words" in capsys.readouterr().out
    assert not (tmp_path / "real10.json").exists()


# --- a synthetic failure class against its exact truth (one DXF reading, seconds) -----------------------------------

def test_synthetic_06_against_its_exact_truth_scores_100(tmp_path):
    """Was a strict xfail (Milestone 14 R1: the first honest number); synthetic-06 reads its exact truth since 5 Nov
    2026 (``mirror.halves``: its symmetric shell no longer gets the mirror of two walls, two doors and two windows)."""
    folder = TR.reading("synthetic-06", tmp_path)
    b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
    truth = TR.synthetic_truth("synthetic-06", TR.synthetic_truth_file("synthetic-06"))
    assert TR.read_commit(folder) != "unknown"
    assert SC.match(truth, TR.extract(b))["total"] == 100.0
