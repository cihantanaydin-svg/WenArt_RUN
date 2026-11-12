"""The sparse truth after its review (12 Nov 2026; the review of branch c1b06249: "the gate must not be foolable").
Each case is a way the first version could be fooled or could fail in the user's name: an absent wall of another
thickness or behind a lintel (G1, F1, F2), a missing truth file excused as withdrawn (G2), a truth edited in the same
commit as the reader (G3, G8, F6, F10), an attribute the user corrected (G4), an inserted storey (G5), a negated room
swallowed by its neighbour (G6), --update without --gate (G7), an origin shift (the frame place), a re-acceptance of a
withdrawn reading (F7), stale trust files (F8). CPU, pure (main() with its inputs patched)."""
from __future__ import annotations

import argparse
import copy
import json

import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR


def _rec(rid, *ops, project="p", **kw):
    r = {"id": rid, "date": "2026-11-12", "project": project, "level": ops[0].get("level") if ops else None,
         "place": None, "element_kind": ops[0].get("kind") if ops else "level", "reader_answer": "",
         "right_answer": "", "user_words": "the user's words", "lesson": None, "note": "test", "source": "user_review",
         "status": "accepted"}
    if ops:
        r["truth_action"] = {"op": ops[0]["op"], "elements": list(ops)}
    r.update(kw)
    return r


def _sq(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _read(levels=(("L0", "Zemin Kat", 0, 0.0),), **per):
    out = {"levels": [{"id": i, "label": lbl, "order": o, "elevation": z} for i, lbl, o, z in levels],
           "per_level": {lv[0]: {t: [] for t in TR.ELEMENT_TYPES + TR.SPARSE_KINDS} for lv in levels}}
    for key, els in per.items():
        lid, t = key.split("_", 1)
        out["per_level"][lid][t] = list(els)
    return out


# --- G6: a negated room swallowed by its neighbour ------------------------------------------------------------------

def test_a_negated_room_swallowed_by_its_neighbour_is_read():
    t = TR.build_sparse("p", [_rec("C0037", {"op": "remove", "kind": "room", "level": "L0", "label": "Oda",
                                             "polygon": _sq(4, 0, 5, 3)})])
    bedroom = {"id": "r1", "label": "Yatak Odası", "polygon": _sq(0, 0, 4, 3), "centroid": [2.0, 1.5]}
    merged = dict(bedroom, polygon=_sq(0, 0, 5, 3), centroid=[2.5, 1.5])               # IoU 0.2, another label
    assert SC.match(t, _read(L0_rooms=[bedroom]))["total"] == 100.0                     # the recess is outside
    res = SC.match(t, _read(L0_rooms=[merged]))
    assert res["unsatisfied"] == ["u_C0037_1"] and "covers 1.00" in res["entries"][0]["why"]


# --- G5: an inserted storey -----------------------------------------------------------------------------------------

def test_an_inserted_storey_does_not_move_a_check_onto_another_floor():
    recs = [_rec("C0001", {"op": "remove", "kind": "door", "level": "L1", "center": [1, 0]},
                 {"op": "add", "kind": "stair", "level": "L1", "center": [5, 5]})]
    anchors = {"L1": {"label": "1. Kat", "order": 1, "elevation": 3.0, "source": "test"}}
    t = TR.build_sparse("p", recs, anchors)
    assert t["levels"][0] == {"id": "L1", "source": "user_correction", "label": "1. Kat", "elevation": 3.0,
                              "order": 1, "anchor_source": "test"}
    door, stair = {"id": "d", "center": [1, 0]}, {"id": "s", "center": [5, 5]}
    # the reader inserts a storey: the old 1. Kat is now L2 and has the wrong door back; the new L1 has a stair
    inserted = _read((("L0", "Zemin Kat", 0, 0.0), ("L1", "Ara Kat", 1, 1.5), ("L2", "1. Kat", 2, 4.5)),
                     L1_stairs=[stair], L2_doors=[door])
    res = SC.match(t, inserted)
    assert res["level_map"] == {"L1": "L2"}
    assert res["unsatisfied"] == ["u_C0001_1", "u_C0001_2"]                              # checked on 1. Kat
    renamed = _read((("L0", "Zemin Kat", 0, 0.0), ("L1", "Birinci Kat", 1, 3.0)), L1_stairs=[stair])
    assert SC.match(t, renamed)["total"] == 100.0                                        # same order and elevation
    gone = _read((("L0", "Zemin Kat", 0, 0.0), ("L1", "Ara Kat", 1, 1.5)), L1_stairs=[stair])
    res = SC.match(t, gone)
    assert res["total"] == 0.0 and "the reading has no level L1 (1. Kat)" in res["entries"][0]["why"]


# --- G4: an attribute the user corrected ---------------------------------------------------------------------------

def test_a_corrected_attribute_must_match():
    recs = [_rec("C0040", {"op": "add", "kind": "door", "level": "L0", "center": [1, 0],
                           "attrs": {"flat_entrance": True}}),
            _rec("C0063", {"op": "add", "kind": "stair", "level": "L0", "center": [5, 5],
                           "attrs": {"landing_toward": [0, 1]}}),
            _rec("C0019", {"op": "add", "kind": "door", "level": "L0", "center": [9, 0],
                           "attrs": {"main_entrance": True}})]
    t = TR.build_sparse("p", recs)
    inside = {"id": "d1", "center": [1, 0], "door_style": "inside"}
    entrance = dict(inside, flat_entrance=True)
    south = {"id": "s1", "center": [5, 5], "landing_center": [5, 4]}
    north = dict(south, landing_center=[5, 6])
    main = {"id": "d9", "center": [9, 0]}
    res = SC.match(t, _read(L0_doors=[inside, main], L0_stairs=[south]), {"_main_entrance": "dX"})
    assert res["unsatisfied"] == ["u_C0019_1", "u_C0040_1", "u_C0063_1"]                # the reading the user corrected
    assert SC.match(t, _read(L0_doors=[entrance, main], L0_stairs=[north]), {"_main_entrance": "d9"})["total"] == 100
    with pytest.raises(ValueError, match="no attribute the score can check"):
        TR.parse_op({"op": "add", "kind": "door", "level": "L0", "center": [1, 0], "attrs": {"colour": "red"}})


def test_a_balcony_is_an_outdoor_space():
    t = TR.build_sparse("p", [_rec("C0008", {"op": "add", "kind": "outdoor", "level": "L0", "label": "Balkon",
                                             "outdoor_kind": "balcony", "polygon": _sq(0, 0, 2, 1)})])
    assert [e["outdoor_kind"] for e in t["per_level"]["L0"]["outdoor"]] == ["balcony"]
    os_ = {"id": "os1", "label": "BALKON", "outdoor_kind": "balcony", "polygon": _sq(0, 0, 2, 1), "centroid": [1, 0.5]}
    assert SC.match(t, _read(L0_outdoor=[os_]))["total"] == 100.0
    assert SC.match(t, _read(L0_outdoor=[dict(os_, outdoor_kind="terrace")]))["total"] == 0.0
    b = {"levels": [{"id": "L0", "label": "Z"}], "site": {"outdoor_spaces": [
        {"id": "os1", "level_id": "L0", "kind": "balcony", "label": "BALKON", "polygon": _sq(0, 0, 2, 1)}]}}
    assert TR.extract(b, attrs=True)["per_level"]["L0"]["outdoor"][0]["outdoor_kind"] == "balcony"
    assert "outdoor" not in TR.extract(b)["per_level"]["L0"]                             # F1 truths unchanged


# --- the frame place: an origin shift ------------------------------------------------------------------------------

def test_a_frame_place_follows_an_origin_shift():
    def building(shift):
        return {"levels": [{"id": "L0", "label": "Z", "region_id": "r2"}],
                "documents": [{"file": "p.dwg", "pages": [{"page": 1, "region_id": "r2", "level_id": "L0",
                                                           "variant": "base",
                                                           "transform_to_building": [50, 0, -100 + shift, 0, 50,
                                                                                     -200]}]}]}
    b0, b1 = building(0.0), building(6.7)
    frame = TR.frame_of({"center": [3.0, 1.0]}, b0, "L0")
    assert frame["file"] == "p.dwg" and frame["region"] == "r2"
    t = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [3.0, 1.0],
                                             "frame": frame})])
    shifted_door = {"id": "d", "center": [9.7, 1.0]}                                    # the same door, 6.7 m on
    assert SC.match(t, _read(L0_doors=[shifted_door]), b1)["total"] == 100.0
    assert SC.match(t, _read(L0_doors=[{"id": "d", "center": [3.0, 1.0]}]), b1)["total"] == 0.0
    plain = TR.build_sparse("p", [_rec("C0001", {"op": "add", "kind": "door", "level": "L0", "center": [3.0, 1.0]})])
    assert SC.match(plain, _read(L0_doors=[shifted_door]), b1)["total"] == 0.0        # metres only: it moved


# --- the gate ------------------------------------------------------------------------------------------------------

def _row(eid, ok, rec, at):
    return {"id": eid, "level": "L0", "type": "doors", "absent": False, "records": [rec], "satisfied": ok, "at": at}


def _entry(rows, total, vs=None, syn=90.0):
    real = {"total": total, "sparse": True, "entries": rows, "assertions": []}
    if vs is not None:
        real["vs_stored_truth"] = {"entries": vs, "assertions": []}
    return {"truth_kind": SC.TRUTH_KIND, "projects": {"real": real, "syn": {"total": syn}}}


def test_a_truth_edited_in_the_same_commit_cannot_hide_a_lost_correction():
    """G3: inserting an op renumbers the ids, so the same id names another door; the stored truth re-scored on the new
    reading keeps the identity and the lost correction falls. G8: a re-placed record whose old place still holds is
    a change, not a fall."""
    x, z = ["doors", False, [1.0, 0.0]], ["doors", False, [5.0, 0.0]]
    stored = dict(_entry([_row("u_C0001_1", True, "C0001", x)], 100.0), commit="a")
    last = SC.latest([stored])
    # the new truth inserted Z before X: u_C0001_1 is now Z (met), X is u_C0001_2 (lost); compared by id it hides
    new_rows = [_row("u_C0001_1", True, "C0001", z), _row("u_C0001_2", False, "C0001", x)]
    assert SC.falls(last, _entry(new_rows, 50.0)) == []                                # the signature differs: no pair
    vs = [_row("u_C0001_1", False, "C0001", x)]                                        # the stored truth on it: lost
    assert SC.falls(last, _entry(new_rows, 50.0, vs)) == ["real: no longer satisfied: C0001 (u_C0001_1)"]
    # a re-placed record: the new place fails, the old one still holds on the new reading: a change, not a fall
    moved = [_row("u_C0001_1", False, "C0001", ["doors", False, [3.0, 0.0]])]
    new = _entry(moved, 0.0, [_row("u_C0001_1", True, "C0001", x)])
    assert SC.falls(last, new) == []
    assert SC.changed(last, new) == ["real: the truth changed at u_C0001_1 (still held against the stored truth)"]


def test_the_stored_truth_is_loaded_at_the_entrys_commit(tmp_path):
    """The gate reads the truth file of the stored entry's commit; a file whose hash is not the stored one is not the
    truth the numbers were made of."""
    head = TR.git_head()
    path = TR.TRUTH_DIR / "real06.json"
    sha = SC.truth_sha("real06")
    assert SC.stored_truth("real06", head, sha) is not None or path.read_bytes() != _git_bytes(head, "real06")
    assert SC.stored_truth("real06", head, "0" * 64) is None
    assert SC.stored_truth("real06", None) is None and SC.stored_truth("nowhere", head) is None


def _git_bytes(commit, project):
    import subprocess
    res = subprocess.run(["git", "show", f"{commit}:results/reading_truth/{project}.json"], cwd=str(TR.REPO),
                         capture_output=True)
    return res.stdout


@pytest.fixture
def gate(monkeypatch, tmp_path):
    """main() over two stored projects (a sparse one, a synthetic one) with its inputs patched: no reading, no
    write; ``gate.run(**args)`` returns (exit code, entries handed to save_scores)."""
    stored = [{"commit": "a", "truth_kind": SC.TRUTH_KIND, "overall": 95.0, "projects": {
        "real06": {"total": 100.0, "sparse": True, "entries": [_row("u_C0063_1", True, "C0063", ["stairs"])],
                   "assertions": []},
        "synthetic-01": {"total": 90.0}}}]
    saved = []
    scored = {"real06": {"total": 100.0, "sparse": True, "assertions": [],
                         "entries": [_row("u_C0063_1", True, "C0063", ["stairs"])]},
              "synthetic-01": {"total": 90.0}}
    monkeypatch.setattr(SC, "load_scores", lambda path=None: copy.deepcopy(stored))
    monkeypatch.setattr(SC, "save_scores", lambda entries, path=None: saved.append(entries) or SC.SCORES_PATH)
    monkeypatch.setattr(SC, "stored_truth", lambda *a, **k: None)
    monkeypatch.setattr(TR, "git_head", lambda repo=None: "b")

    def run(present=("real06", "synthetic-01"), **kw):
        monkeypatch.setattr(TR, "truth_projects", lambda truth_dir=None: list(present))
        monkeypatch.setattr(SC, "score_project", lambda p, work, **k: copy.deepcopy(scored[p]))
        ns = argparse.Namespace(**dict({"projects": None, "work": str(tmp_path), "fresh": False, "update": False,
                                        "gate": False}, **kw))
        return SC.main(ns), saved

    run.scored = scored
    return run


def test_a_sparse_project_whose_truth_file_is_missing_falls_in_a_full_gate(gate, capsys):
    """G2: every real baseline carries acceptance_withdrawn since 6 Nov 2026; that alone excuses nothing while the
    project still has applicable records."""
    assert "real06" in TR.sparse_projects(TR.load_corrections())
    assert (TR.load_baseline("real06") or {}).get("acceptance_withdrawn")
    code, _ = gate(present=("synthetic-01",), gate=True)
    out = capsys.readouterr().out
    assert code == 1 and "real06: 100.00 -> not scored" in out and "left the truth" not in out


def test_update_always_runs_the_gate(gate, capsys):
    """G7: --update without --gate stores nothing that falls."""
    gate.scored["real06"]["entries"][0]["satisfied"] = False
    code, saved = gate(update=True)
    out = capsys.readouterr().out
    assert code == 1 and saved == [] and "C0063 (u_C0063_1)" in out and "not stored, the gate fell" in out
    gate.scored["real06"]["entries"][0]["satisfied"] = True
    code, saved = gate(update=True)
    assert code == 0 and len(saved) == 1 and "vs_stored_truth" not in json.dumps(saved[0][-1])


# --- F7: a re-acceptance --------------------------------------------------------------------------------------------

def test_a_reacceptance_needs_a_fresh_reading_and_a_new_seen_reading():
    hist = [{"on": "2026-11-06", "was": {"accepted_seen": "the sheets of 2 Nov", "accepted_on": "2026-11-02"}}]
    base = {"accepted_by_user": True, "accepted_on": "2026-11-20", "accepted_scope": "all",
            "accepted_seen": "the structure run of 20 Nov", "acceptance_history": hist}
    fresh = {"accepted": {"on": "2026-11-20"}}
    assert TR.reacceptance_problem(base, fresh) is None
    assert "not the one stored" in TR.reacceptance_problem(base, {"accepted": {"on": "2026-11-02"}})
    assert "withdrawn" in TR.reacceptance_problem(dict(base, accepted_seen="the sheets of 2 Nov"), fresh)
    assert "not newer" in TR.reacceptance_problem(dict(base, accepted_on="2026-11-05"), fresh)
    assert TR.reacceptance_problem({"accepted_on": "2026-11-02"}, {"accepted": {}}) is None   # no withdrawal
    # the withdrawn baselines keep the old fields only under acceptance_withdrawn.was
    for p in ("real07", "real10", "real19", "real21"):
        b = TR.load_baseline(p)
        assert not any(k in b for k in ("accepted_on", "accepted_seen", "accepted_note")), p
        assert b["acceptance_withdrawn"]["was"]["accepted_on"] and b["acceptance_withdrawn"]["user_said"], p


# --- F8: stale trust files ------------------------------------------------------------------------------------------

def test_stale_trust_files_count_as_not_calibrated():
    from wenart.reading_check import critic as CR
    from wenart.reading_check import raster_opinion as RO
    for mod in (CR, RO):
        trust = mod.load_trust()
        assert trust["stale"]["on"] == "2026-11-12" and "withdrawn" in trust["stale"]["reason"]
    found = [{"check": CR.CHECK, "kind": k, "message": "m", "severity": "major", "confidence": 0.9}
             for k, v in CR.load_trust()["kinds"].items() if v.get("trusted")]
    assert found
    CR.apply_trust(found, CR.load_trust())
    assert {f["severity"] for f in found} == {"info"}
