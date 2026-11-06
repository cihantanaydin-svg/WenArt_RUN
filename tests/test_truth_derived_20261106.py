"""The derived reading truth (6 Nov 2026, Milestone 14 R1; decided by the session organizer after four rounds of
merge fixes left 18 verified breaks): truth(project) = the accepted reading's elements + a replay of the project's
applicable correction records in record order, by place. Each of the 18 breaks of the adversarial test is a test of
the build here: the build from (accepted reading, records) gives the right truth, and scoring the break's reading
against it gives the right counts. The breaks that only concerned how a later reading was merged (1-7, 9, 17) cannot
happen any more: no reading but the accepted one enters the truth. CPU, pure (the CLI ones in a temp folder)."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

ROOT = Path(__file__).resolve().parents[1]
RECORDS = {r["id"]: r for r in TR.load_corrections()}


def _acc(per_level: dict, project: str = "p") -> dict:
    """An accepted reading (the truth's shape, the reader's ids) from ``{level: {type: [elements]}}``."""
    per = {}
    for lid, lv in per_level.items():
        per[lid] = {t: [] for t in TR.ELEMENT_TYPES}
        for t, els in lv.items():
            for e in els:
                e = dict(e, source=TR.SOURCE_ACCEPTED)
                if t == "rooms":
                    e.setdefault("centroid", TR.centroid(e["polygon"]))
                elif t in TR.OPENING_TYPES:
                    e.setdefault("type", {"doors": "door", "windows": "window"}.get(t, "opening"))
                per[lid][t].append(e)
    return {"project": project, "source": TR.SOURCE_ACCEPTED, "status": "accepted", "commit": "c0", "date": "d0",
            "levels": [{"id": lid, "label": lid, "elevation": 0.0, "order": i, "source": TR.SOURCE_ACCEPTED}
                       for i, lid in enumerate(per_level)], "levels_left_out": [], "per_level": per}


def _rec(rid: str, *ops: dict, project: str = "p", **kw) -> dict:
    r = {"id": rid, "date": "2026-11-06", "project": project, "level": ops[0].get("level") if ops else None,
         "place": None, "element_kind": ops[0].get("kind") if ops else "other", "reader_answer": "",
         "right_answer": "", "user_words": "the user's words", "lesson": None, "note": "test",
         "source": "user_review", "status": "accepted", "truth_action": {"op": ops[0]["op"], "elements": list(ops)}}
    r.update(kw)
    return r


def _reading(truth: dict, extra: dict | None = None, drop=()) -> dict:
    """A reading made of the truth's positives (the reader's ids), plus ``extra`` ``{(level, type): [elements]}``,
    without the elements whose place is in ``drop`` (``(level, type, centre)``)."""
    per = {}
    for lid, lv in truth["per_level"].items():
        per[lid] = {}
        for t in TR.ELEMENT_TYPES:
            per[lid][t] = [dict(e, source=TR.SOURCE_ACCEPTED) for e in TR.positives(lv.get(t))
                           if (lid, t, tuple(e.get("center") or ())) not in drop]
    for (lid, t), els in (extra or {}).items():
        per[lid][t] = list(els) + per[lid][t] if t == "walls" else per[lid][t] + list(els)
    return {"levels": copy.deepcopy(truth["levels"]), "per_level": per}


def _at(truth, lid, t, center, absent=None):
    return [e for e in truth["per_level"][lid][t] if e.get("center") and TR._dist(e["center"], center) < 1e-6
            and (absent is None or bool(e.get("absent")) == absent)]


def _real(project, *rids):
    acc, why = TR.accepted_of(project)
    assert acc is not None, why
    return acc, [RECORDS[r] for r in rids]


def _counts(res, t):
    return {k: res[t][k] for k in ("truth", "read", "matched", "absent_hits")}


# --- 1. a negated wall span read again (real07 L1, C0051) -----------------------------------------------------------

LONG = {"id": "w_L1_056", "start": [7.542, 7.68], "end": [7.542, 11.6], "thickness": 0.18}
SPAN = {"op": "remove", "kind": "wall", "level": "L1", "start": [7.542, 7.78], "end": [7.542, 8.5], "thickness": 0.18}


def test_01_a_negated_span_read_again_is_an_absent_hit_and_the_long_wall_is_cut():
    truth = TR.build_truth("p", _acc({"L1": {"walls": [LONG]}}), [_rec("C0051", SPAN)])
    walls = truth["per_level"]["L1"]["walls"]
    pos, neg = TR.positives(walls), [w for w in walls if w.get("absent")]
    assert [(w["start"], w["end"]) for w in pos] == [([7.542, 8.5], [7.542, 11.6])]     # cut; the 10 cm joint goes
    assert [(w["start"], w["end"]) for w in neg] == [([7.542, 7.78], [7.542, 8.5])]
    assert pos[0]["source"] == TR.SOURCE_ACCEPTED and pos[0]["cut_by"] == ["C0051"]
    # the reading moves the long wall 1 cm and reads the span again
    read = {"levels": [{"id": "L1"}], "per_level": {"L1": {t: [] for t in TR.ELEMENT_TYPES}}}
    read["per_level"]["L1"]["walls"] = [dict(LONG, start=[7.552, 7.68], end=[7.552, 11.6]),
                                        {"id": "w_x", "start": [7.542, 7.78], "end": [7.542, 8.5], "thickness": 0.18}]
    assert _counts(SC.match(truth, read), "walls") == {"truth": 1, "read": 2, "matched": 1, "absent_hits": 1}
    # the stored real07 truth holds the same
    real = TR.load_truth("real07")["per_level"]["L1"]["walls"]
    assert any(w.get("absent") and w["start"] == [7.542, 7.78] and w["end"] == [7.542, 8.5] for w in real)
    assert not any(not w.get("absent") and SC.wall_overlap(w, SPAN) for w in real)


# --- 2. a user element missing from a reading never takes its neighbour (real10 L2, C0035) --------------------------

def test_02_the_replay_decides_on_the_accepted_reading_both_elements_stay():
    acc, recs = _real("real10", "C0035")
    truth = TR.build_truth("real10", acc, recs)
    door = _at(truth, "L2", "doors", [11.19, 6.29], absent=False)
    assert len(door) == 1 and door[0]["width"] == 1.4 and door[0]["source"] == TR.SOURCE_USER
    neighbour = _at(truth, "L2", "openings", [11.19, 6.065], absent=False)
    assert len(neighbour) == 1 and neighbour[0]["width"] == 1.72 and neighbour[0]["source"] == TR.SOURCE_ACCEPTED
    assert len(_at(truth, "L2", "openings", [11.19, 6.29], absent=True)) == 1
    # a reading that has only the opening: the user's door is missed, the opening matched; the truth is the truth
    read = _reading(truth, drop={("L2", "doors", (11.19, 6.29))})
    res = SC.match(truth, read)
    assert res["doors"]["matched"] == res["doors"]["truth"] - 1 and res["openings"]["matched"] == res["openings"]["truth"]
    assert TR.dumps(TR.build_truth("real10", acc, recs)) == TR.dumps(truth)


# --- 3. a negated element read twice (real07 L0, C0047) -------------------------------------------------------------

def test_03_a_negated_element_read_twice_stays_negated():
    acc, recs = _real("real07", "C0047")
    truth = TR.build_truth("real07", acc, recs)
    assert len(_at(truth, "L0", "doors", [5.36, 2.19], absent=True)) == 1
    assert not _at(truth, "L0", "doors", [5.36, 2.19], absent=False)
    user = _at(truth, "L0", "doors", [5.74, 2.19], absent=False)
    assert len(user) == 1 and user[0]["width"] == 0.8 and user[0]["changed"] == ["center", "width"]
    assert not _at(truth, "L0", "doors", [5.815, 2.19])                  # the reading's door moved to the drawn centre
    extra = [{"id": "dx1", "type": "door", "center": [5.36, 2.19], "width": 0.8},
             {"id": "dx2", "type": "door", "center": [5.39, 2.19], "width": 0.8}]
    res = SC.match(truth, _reading(truth, {("L0", "doors"): extra}))
    n = res["doors"]["truth"]
    assert _counts(res, "doors") == {"truth": n, "read": n + 2, "matched": n, "absent_hits": 1}


# --- 4. an accepted element missing from a reading never takes a re-read negated one (real10 L6, C0034) -------------

def test_04_an_accepted_element_missing_from_a_reading_does_not_change_the_truth():
    acc, recs = _real("real10", "C0034")
    truth = TR.build_truth("real10", acc, recs)
    kept = _at(truth, "L6", "openings", [9.666, 8.487], absent=False)       # the accepted stacked gap beside the lift
    assert len(kept) == 1 and kept[0]["source"] == TR.SOURCE_ACCEPTED
    assert len(_at(truth, "L6", "openings", [9.666, 8.45], absent=True)) == 1
    assert len(_at(truth, "L6", "doors", [10.658, 9.085], absent=True)) == 1
    read = _reading(truth, {("L6", "openings"): [{"id": "o_re", "type": "opening", "center": [9.666, 8.45],
                                                  "width": 0.9}]}, drop={("L6", "openings", (9.666, 8.487))})
    res = SC.match(truth, read)
    # the score's own rule (kept): the re-read gap stands within 0.30 m of the missing accepted one and is matched to
    # it; the truth itself does not change with the reading
    assert _counts(res, "openings")["matched"] == res["openings"]["truth"]
    assert TR.dumps(TR.build_truth("real10", acc, recs)) == TR.dumps(truth)


# --- 5. a short wall inside a longer one (real06 L0) -----------------------------------------------------------------

def test_05_wall_ids_follow_the_accepted_reading_only():
    w1 = {"id": "w_a", "start": [8.526, 0.95], "end": [8.526, 13.8], "thickness": 0.3}
    w2 = {"id": "w_b", "start": [8.5, 6.0], "end": [8.5, 6.75], "thickness": 0.3}
    t1 = TR.build_truth("p", _acc({"L0": {"walls": [w1, w2]}}), [])
    t2 = TR.build_truth("p", _acc({"L0": {"walls": [dict(w2, id="w_x"), dict(w1, id="w_y")]}}), [])
    ids = lambda t: {(tuple(w["start"]), tuple(w["end"])): w["id"] for w in t["per_level"]["L0"]["walls"]}  # noqa
    assert ids(t1) == ids(t2) and len(set(ids(t1).values())) == 2
    moved = {"levels": [{"id": "L0"}], "per_level": {"L0": {t: [] for t in TR.ELEMENT_TYPES}}}
    moved["per_level"]["L0"]["walls"] = [dict(w, start=[w["start"][0] + 0.008, w["start"][1]],
                                              end=[w["end"][0] + 0.008, w["end"][1]]) for w in (w2, w1)]
    assert _counts(SC.match(t1, moved), "walls") == {"truth": 2, "read": 2, "matched": 2, "absent_hits": 0}


# --- 6. the build does not depend on the order of the accepted reading's lists (real07 L0) ---------------------------

def test_06_a_permuted_accepted_reading_builds_the_same_bytes():
    acc, _ = _real("real07")
    records = list(RECORDS.values())
    perm = copy.deepcopy(acc)
    for lv in perm["per_level"].values():
        for t in TR.ELEMENT_TYPES:
            lv[t] = list(reversed(lv[t]))
    assert TR.dumps(TR.build_truth("real07", perm, records)) == TR.dumps(TR.build_truth("real07", acc, records))


# --- 7. a double read at a user element (real07 L0, C0054 stair; C0045 door with a negated window) -------------------

def test_07_a_double_read_at_a_user_element_adds_nothing_to_the_truth():
    acc, recs = _real("real07", "C0045", "C0054")
    truth = TR.build_truth("real07", acc, recs)
    stairs = truth["per_level"]["L0"]["stairs"]
    assert len(stairs) == 1 and stairs[0]["source"] == TR.SOURCE_USER and stairs[0]["center"] == [8.668, 4.541]
    door = _at(truth, "L0", "doors", [2.03, 0.24])
    window = _at(truth, "L0", "windows", [2.03, 0.24])
    assert len(door) == 1 and not door[0].get("absent") and len(window) == 1 and window[0]["absent"]
    read = _reading(truth, {("L0", "stairs"): [dict(stairs[0], id="f_x", center=[8.698, 4.541])],
                            ("L0", "windows"): [{"id": "win_x", "type": "window", "center": [2.03, 0.24],
                                                 "width": 3.41}]})
    res = SC.match(truth, read)
    assert _counts(res, "stairs") == {"truth": 1, "read": 2, "matched": 1, "absent_hits": 0}
    assert res["windows"]["absent_hits"] == 1 and res["doors"]["matched"] == res["doors"]["truth"]


# --- the command line (8, 12-16, 18) ---------------------------------------------------------------------------------

@pytest.fixture
def cli(tmp_path):
    """A project ``p`` with an accepted baseline, a stored accepted reading (a long wall, a door, a room) and a store
    with an accepted record C0001 of ``p`` (the user's words), a proposed C0002 and a record C0003 of ``q``."""
    dirs = {k: tmp_path / k for k in ("truth", "accepted", "baseline", "projects")}
    for d in dirs.values():
        d.mkdir()
    for name in ("p", "q"):
        (dirs["projects"] / name).mkdir()
    (dirs["baseline"] / "p.json").write_text(json.dumps({"accepted_by_user": True, "levels": ["L0"]}))
    acc = _acc({"L0": {"walls": [{"id": "w_L0_001", "start": [7.542, 7.68], "end": [7.542, 11.6],
                                  "thickness": 0.18}],
                       "doors": [{"id": "d_L0_001", "center": [4.0, 0.0], "width": 0.9}],
                       "rooms": [{"id": "r_L0_a", "label": "Oda", "room_type": "bedroom",
                                  "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}]}})
    TR.write_accepted("p", acc, dirs["accepted"])
    store = tmp_path / "c.jsonl"
    TR.save_corrections([dict(_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [4.0, 0.0]}),
                              truth_action=None),
                         dict(_rec("C0002", {"op": "add", "kind": "door", "level": "L0", "center": [1.0, 0.0]}),
                              status="proposed", truth_action=None),
                         dict(_rec("C0003", {"op": "add", "kind": "door", "level": "L0", "center": [1.0, 0.0]}),
                              project="q", truth_action=None)], store)

    def run(**kw):
        ns = argparse.Namespace(**dict({"action": "add", "project": "p", "level": "L0"}, **kw))
        return TR.correct(ns, corrections=store, truth_dir=dirs["truth"], accepted_dir=dirs["accepted"],
                          baseline_dir=dirs["baseline"], projects_dir=dirs["projects"])

    run.store, run.dirs = store, dirs
    run.truth = lambda: TR.load_truth("p", dirs["truth"])                     # noqa: E731
    run.records = lambda: TR.load_corrections(store)                           # noqa: E731
    return run


def test_08_remove_of_a_short_span_cuts_the_long_wall(cli):
    code, msg = cli(action="remove", kind="wall", start="7.542,7.78", end="7.542,8.5", thickness="0.18",
                    correction="C0001")
    assert code == 0, msg
    walls = cli.truth()["per_level"]["L0"]["walls"]
    assert [(w["start"], w["end"], bool(w.get("absent"))) for w in walls] == [
        ([7.542, 7.78], [7.542, 8.5], True), ([7.542, 8.5], [7.542, 11.6], False)]
    ops = TR.record_ops(next(r for r in cli.records() if r["id"] == "C0001"))
    assert ops == [{"op": "remove", "kind": "wall", "level": "L0", "start": [7.542, 7.78], "end": [7.542, 8.5],
                    "thickness": 0.18}]


def test_09_the_span_piece_listed_first_never_takes_the_long_wall():
    truth = TR.build_truth("p", _acc({"L1": {"walls": [LONG]}}), [_rec("C0051", SPAN)])
    span = {"id": "w_s", "start": [7.542, 7.78], "end": [7.542, 8.5], "thickness": 0.18}
    for order in ([span, LONG], [LONG, span]):
        read = {"levels": [{"id": "L1"}], "per_level": {"L1": {t: [] for t in TR.ELEMENT_TYPES}}}
        read["per_level"]["L1"]["walls"] = copy.deepcopy(order)
        assert _counts(SC.match(truth, read), "walls") == {"truth": 1, "read": 2, "matched": 1, "absent_hits": 1}


def test_10_a_negated_window_read_as_an_opening_is_no_new_opening():
    acc = _acc({"L0": {"windows": [{"id": "win_1", "center": [3.0, 0.0], "width": 1.2}]}})
    truth = TR.build_truth("p", acc, [_rec("C0010", {"op": "remove", "kind": "window", "level": "L0",
                                                     "center": [3.0, 0.0]})])
    lv = truth["per_level"]["L0"]
    assert lv["openings"] == [] and [w.get("absent") for w in lv["windows"]] == [True]
    read = {"levels": [{"id": "L0"}], "per_level": {"L0": {t: [] for t in TR.ELEMENT_TYPES}}}
    read["per_level"]["L0"]["openings"] = [{"id": "o_1", "type": "opening", "center": [3.0, 0.0], "width": 1.2}]
    res = SC.match(truth, read)
    assert _counts(res, "openings") == {"truth": 0, "read": 1, "matched": 0, "absent_hits": 0}


def test_11_a_level_left_out_never_comes_back_through_a_correction():
    acc = _acc({"L0": {"doors": [{"id": "d1", "center": [1.0, 0.0], "width": 0.9}]}})
    truth = TR.build_truth("p", acc, [_rec("C0011", {"op": "remove", "kind": "door", "level": "L1",
                                                     "center": [1.0, 0.0]})])
    assert [lv["id"] for lv in truth["levels"]] == ["L0"] and list(truth["per_level"]) == ["L0"]
    assert truth["build_report"]["unmatched"][0]["record"] == "C0011"
    assert "not in the truth" in truth["build_report"]["unmatched"][0]["why"]
    real17 = TR.load_truth("real17")                       # C0038 names L0, a level real17's acceptance leaves out
    assert "L0" not in real17["per_level"] and {u["record"] for u in real17["build_report"]["unmatched"]} == {"C0038"}


def test_12_a_readers_id_needs_its_reading(cli):
    code, msg = cli(kind="door", id="d_L0_001", correction="C0001")
    assert code == 2 and "reader's id" in msg and cli.truth() is None
    code, msg = cli(kind="door", id="t_L0_door_0042", correction="C0001")
    assert code == 2 and "no such truth id" in msg


def test_13_remove_by_a_readers_id_negates_like_a_centre(cli, tmp_path):
    reading = {"levels": [{"id": "L0"}], "openings": [{"id": "d_L0_009", "type": "door", "level_id": "L0",
                                                       "center": [9.0, 9.0], "width": 0.8}]}
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "building.json").write_text(json.dumps(reading))
    code, msg = cli(action="remove", kind="door", id="d_L0_009", reading=str(tmp_path / "r"), correction="C0001")
    assert code == 0, msg
    neg = _at(cli.truth(), "L0", "doors", [9.0, 9.0], absent=True)
    assert len(neg) == 1 and neg[0]["reader_id"] == "d_L0_009" and neg[0]["width"] == 0.8


def test_14_add_on_an_existing_element_replaces_or_confirms_never_duplicates(cli):
    assert cli(kind="door", center="4.05,0.0", width="0.9", correction="C0001")[0] == 0
    assert cli(kind="door", center="4.05,0.0", width="0.9", correction="C0001")[0] == 0    # the same again
    code, msg = cli(kind="door", center="4.0,0.02", width="1.0", text="this door is 1.0 m wide")
    assert code == 0, msg
    doors = cli.truth()["per_level"]["L0"]["doors"]
    assert len(doors) == 1 and doors[0]["width"] == 1.0 and doors[0]["center"] == [4.0, 0.02]
    assert doors[0]["corrections"] == ["C0001", "C0004"] and doors[0]["source"] == TR.SOURCE_USER
    assert len(TR.record_ops(next(r for r in cli.records() if r["id"] == "C0001"))) == 1


def test_15_the_record_check_cannot_be_bypassed(cli):
    assert cli(kind="door", center="1,0", correction="C0002")[0] == 2                     # proposed
    code, msg = cli(kind="door", center="1,0", correction="C0003")                        # another project's record
    assert code == 2 and "record of q" in msg
    code, msg = cli(kind="door", center="1,0", correction="C0002", source="synthetic")
    assert code == 2
    code, msg = cli(kind="door", center="1,0")                                             # no words, no record
    assert code == 2 and "user's words" in msg
    assert cli.truth() is None and len(cli.records()) == 3


def test_16_a_room_by_its_centre_alone_needs_a_room_there(cli):
    code, msg = cli(action="remove", kind="room", center="9,9", correction="C0001")
    assert code == 2 and "could never match" in msg and cli.truth() is None
    code, msg = cli(kind="room", center="9,9", label="Depo", correction="C0001")
    assert code == 2 and "could never match" in msg
    code, msg = cli(kind="room", center="2,2", label="Depo", room_type="storage", correction="C0001")
    assert code == 0, msg
    room = cli.truth()["per_level"]["L0"]["rooms"]
    assert len(room) == 1 and room[0]["label"] == "Depo" and room[0]["polygon"] == [[0, 0], [4, 0], [4, 4], [0, 4]]


def test_17_ids_are_derived_and_never_shared():
    acc = _acc({"L0": {"doors": [{"id": "d1", "center": [1.0, 0.0], "width": 0.9}]}})
    r1 = _rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [5.0, 0.0], "width": 0.8})
    r2 = _rec("C0002", {"op": "add", "kind": "door", "level": "L0", "center": [7.0, 0.0], "width": 0.8})
    both = TR.build_truth("p", acc, [r1, r2])
    only2 = TR.build_truth("p", acc, [r2])                  # C0001 dropped (rejected later)
    ids = lambda t: {tuple(e["center"]): e["id"] for e in t["per_level"]["L0"]["doors"]}   # noqa: E731
    assert ids(both) == {(1.0, 0.0): "t_L0_door_0001", (5.0, 0.0): "u_C0001_1", (7.0, 0.0): "u_C0002_1"}
    assert ids(only2) == {(1.0, 0.0): "t_L0_door_0001", (7.0, 0.0): "u_C0002_1"}
    for path in sorted((ROOT / "results" / "reading_truth").glob("*.json")):
        t = json.loads(path.read_text(encoding="utf-8"))
        every = [e["id"] for lv in t["per_level"].values() for els in lv.values() for e in els]
        assert len(every) == len(set(every)) and all(TR.is_truth_id(i) for i in every), path.stem
        assert "next_truth_id" not in t


def test_18_the_command_line_answers_instead_of_raising(cli, capsys, tmp_path):
    code, msg = cli(kind="door", id="d_L0_001", reading="/nowhere/at/all", correction="C0001")
    assert code == 2 and "no building.json" in msg
    ns = argparse.Namespace(action="add")                    # a namespace without the optional fields
    assert TR.main(ns) == 2 and "--project, --level and --kind are needed" in capsys.readouterr().out
    (tmp_path / "bad.json").write_text("{not json")
    code, msg = cli(kind="door", id="d_L0_001", reading=str(tmp_path / "bad.json"), correction="C0001")
    assert code == 2 and msg.startswith("JSONDecodeError")
    reading = {"levels": [{"id": "L0"}], "openings": [{"id": "d_L0_001", "type": "door", "level_id": "L0",
                                                       "center": [4.0, 0.0], "width": 0.9}]}
    (tmp_path / "r.json").write_text(json.dumps(reading))
    code, msg = cli(action="remove", kind="window", id="d_L0_001", reading=str(tmp_path / "r.json"),
                    correction="C0001")
    assert code == 2 and "is a door in the given reading, not a window: give --kind door" in msg
    assert cli.truth() is None


# --- the derived files ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("project", TR.truth_projects())
def test_every_truth_file_is_its_build(project):
    """A truth file is the build of its stored inputs (the accepted reading, the correction store), byte for byte."""
    acc, why = TR.accepted_of(project)
    assert acc is not None, why
    built = TR.build_truth(project, acc, TR.load_corrections())
    assert (ROOT / "results" / "reading_truth" / f"{project}.json").read_text(encoding="utf-8") == TR.dumps(built)


@pytest.mark.parametrize("project", sorted(p.stem for p in (ROOT / "results" / "reading_accepted").glob("*.json")))
def test_the_accepted_reading_scores_100_against_its_own_truth(project):
    acc, why = TR.accepted_of(project)
    assert acc is not None, why
    assert SC.match(TR.build_truth(project, acc, []), acc)["total"] == 100.0


def test_records_join_by_place_never_by_id():
    """Scrambled id hints (``reader_ids``, an operation's ``id``) change nothing but the hints."""
    acc, _ = _real("real10")
    recs = [RECORDS[r] for r in RECORDS if RECORDS[r]["project"] == "real10"]
    scrambled = copy.deepcopy(recs)
    for r in scrambled:
        r["reader_ids"] = ["x_" + str(i) for i in range(len(r.get("reader_ids") or []))]
        for el in (r.get("truth_action") or {}).get("elements") or [r.get("truth_action") or {}]:
            if isinstance(el, dict) and el.get("id"):
                el["id"] = "zz_" + el["id"]
    strip = lambda t: json.dumps({lid: {k: [{f: v for f, v in e.items() if f != "reader_id"} for e in els]  # noqa
                                        for k, els in lv.items()} for lid, lv in t["per_level"].items()},
                                 sort_keys=True)
    assert strip(TR.build_truth("real10", acc, recs)) == strip(TR.build_truth("real10", acc, scrambled))


def test_every_applicable_record_is_replayed_or_reported():
    """Each applicable record with a truth action of a project that has a truth is in the truth's ``built_from``;
    each of its operations is in the build report (by record, operation number and place), applied or unmatched; a
    record with an applied operation is named in the ``corrections`` of an element of the truth (a later record that
    removes the element keeps the earlier ids on the negation)."""
    for project in TR.truth_projects():
        truth = TR.load_truth(project)
        rep = truth["build_report"]
        tagged = {c for lv in truth["per_level"].values() for els in lv.values() for e in els
                  for c in (e.get("corrections") or [])} | {c for lv in truth["levels"] for c in lv.get("corrections")
                                                            or []}
        for rid, r in RECORDS.items():
            if r["project"] != project or TR.correction_applicable(r) or not TR.record_ops(r):
                continue
            assert rid in truth["built_from"]["records"], (project, rid)
            mine = sorted((x for x in rep["applied"] + rep["unmatched"] if x["record"] == rid), key=lambda x: x["n"])
            assert [x["n"] for x in mine] == list(range(1, len(TR.record_ops(r)) + 1)), (project, rid)
            assert all("ids" not in x for x in mine)
            if any(x["state"] != "unmatched" for x in mine):
                assert rid in tagged, (project, rid)
