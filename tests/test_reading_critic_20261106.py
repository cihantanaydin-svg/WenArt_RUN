"""6 Nov 2026 (Milestone 14 R6, RC15): the vision critic of the reading check.

What: the two panels of a level rendered from a synthetic reading in one exact frame and the mapping of a point
through them (a red dot drawn at a known wall end comes back within 0.2 m; the normalised-point mapping round trip);
the strict JSON schemas (the fake server's grammar check, the answers validated); the client against the fake vLLM
server (two calls per level, the answers file, the deadline, a failed call recorded); the calibration on hand-made
findings (precision per kind against the truth's disagreements, recall of the user's records, the out-of-sample
verdicts); the trust file lowering a kind; and the wiring into ``reading_check.check`` as advisory findings.
Why: the user (4 Nov 2026): "some AI or something else to give the feedbacks by itself instead of me at some point";
the critic must be measured before it is trusted, and its inputs must be exact so its findings land on the right wall.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from wenart import reading_check as RC
from wenart.reading_check import critic as CR

REPO = Path(__file__).resolve().parents[1]
FAKES = REPO / "tests" / "fakes"


# ------------------------------------------------------------------------------------------------- a reading fixture
@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    """A CPU reading of the smallest synthetic project with a DXF (no AI), made once for the module."""
    from wenart.ingest import pipeline as PL

    project = "synthetic-16-open-recess"
    out = tmp_path_factory.mktemp("critic_reading") / project
    out.mkdir(parents=True)
    PL.run_project(REPO / "projects" / project, out, no_ai=True)
    assert (out / "building.json").is_file()
    return out


def test_panels_share_one_exact_frame_and_a_wall_end_comes_back_within_20_cm(reading, tmp_path):
    import numpy as np
    from PIL import Image

    b = json.loads((reading / "building.json").read_text(encoding="utf-8"))
    lid = next(iter(RC.level_pages(b)))
    e = CR.render_level(reading, lid, tmp_path / "panels", max_side=1200)
    assert e is not None and e["level"] == lid
    d, m = Image.open(tmp_path / "panels" / e["drawing"]), Image.open(tmp_path / "panels" / e["model"])
    assert d.size == m.size == tuple(e["size"]) and max(d.size) == 1200
    # a red dot at a wall end, drawn in the same frame, found in the image, mapped back
    w = next(w for w in b["walls"] if w["level_id"] == lid)
    pt = tuple(w["end"])
    img = CR.draw_mark(e["box"], tuple(e["size"]), pt, e["tf"], tmp_path / "dot.jpg")
    a = np.asarray(Image.open(img).convert("RGB")).astype(int)
    mask = (a[:, :, 0] > 180) & (a[:, :, 1] < 120) & (a[:, :, 2] < 120)
    ys, xs = np.nonzero(mask)
    assert len(xs) > 20
    nx, ny = xs.mean() / e["size"][0], ys.mean() / e["size"][1]
    back = CR.norm_to_metres(nx, ny, e["box"], e["tf"])
    assert ((back[0] - pt[0]) ** 2 + (back[1] - pt[1]) ** 2) ** 0.5 < 0.2
    # the pure round trip, and the model's 0-1000 integers through answers_to_findings
    n = CR.metres_to_norm(*pt, e["box"], e["tf"])
    assert abs(n[0] - nx) < 0.01 and abs(n[1] - ny) < 0.01
    again = CR.norm_to_metres(*n, e["box"], e["tf"])
    assert abs(again[0] - pt[0]) < 1e-6 and abs(again[1] - pt[1]) < 1e-6


def test_prepare_writes_the_index_with_every_frame(reading, tmp_path):
    dest = tmp_path / "inputs"
    idx = CR.prepare([{"set": "c", "project": "synthetic-16-open-recess", "tag": "current", "out_dir": reading,
                       "failure_class": "open_recess"}], dest, max_side=800)
    entries = idx["entries"]
    assert entries and all(e["set"] == "c" and e["project"] == "synthetic-16-open-recess" for e in entries)
    e = entries[0]
    assert (dest / e["folder"] / e["drawing"]).is_file() and (dest / e["folder"] / e["model"]).is_file()
    assert len(e["box"]) == 4 and len(e["tf"]) == 6 and e["failure_class"] == "open_recess"
    assert json.loads((dest / "index.json").read_text(encoding="utf-8"))["entries"] == entries
    # a second prepare of the same reading replaces, never doubles
    idx2 = CR.prepare([{"set": "c", "project": "synthetic-16-open-recess", "tag": "current", "out_dir": reading}],
                      dest, max_side=800)
    assert len(idx2["entries"]) == len(entries)


# ----------------------------------------------------------------------------------------------------------- schema
def test_the_schemas_pass_the_fake_servers_grammar_check_and_validate_answers():
    import sys

    sys.path.insert(0, str(FAKES))
    import fake_vlm as FV
    from wenart.recognition import vlm_client as VC

    qs = CR.reading_questions()
    assert len(qs) >= 30 and all(q["ask"].endswith("?") for q in qs)
    for schema in (CR.DIFFERENCES_SCHEMA, CR.questions_schema(qs)):
        assert FV.grammar_error(schema) is None
        inst = FV.minimal_instance(schema)
        assert VC.schema_errors(schema, inst) == []
    good = {"findings": [{"kind": "missing_wall", "x": 500, "y": 250, "description": "a wall", "confidence": 80}],
            "summary": "one"}
    assert VC.schema_errors(CR.DIFFERENCES_SCHEMA, good) == []
    bad = {"findings": [{"kind": "lost_wall", "x": 500, "y": 250, "description": "a wall", "confidence": 80}],
           "summary": "one"}
    assert VC.schema_errors(CR.DIFFERENCES_SCHEMA, bad)
    prompt = CR.differences_prompt({"level": "L0", "label": "Zemin Kat", "title": "ZEMIN KAT PLANI", "copies": ["L1"]})
    assert "L1" in prompt and all(k in prompt for k in CR.KINDS)


def test_the_question_bank_reads_as_questions():
    lessons = [{"id": "UL1", "area": "reading", "status": "built",
                "lesson": "4 Nov 2026 (user, real10: 'x: y'): a recess is open air; the rest of the text. More."},
               {"id": "UL2", "area": "plan", "status": "open", "question": "Is every wall drawn?"},
               {"id": "UL3", "area": "reading", "status": "process", "lesson": "how we work"},
               {"id": "UL4", "area": "decor", "status": "built", "lesson": "cushions"}]
    qs = CR.reading_questions(lessons)
    assert [q["id"] for q in qs] == ["UL1", "UL2"]
    assert qs[0]["ask"] == "Rule: a recess is open air; the rest of the text. Does the model keep this rule here?"
    assert qs[1]["ask"] == "Is every wall drawn?"


# ----------------------------------------------------------------------------------------------------------- client
def _index(tmp_path, reading, max_side=600):
    return CR.prepare([{"set": "c", "project": "synthetic-16-open-recess", "tag": "current", "out_dir": reading}],
                      tmp_path / "inputs", max_side=max_side), tmp_path / "inputs"


def test_the_client_asks_two_calls_per_level_against_the_fake_server(reading, tmp_path):
    import sys

    sys.path.insert(0, str(FAKES))
    from fake_vlm import FakeVLM
    from wenart.agent import model as AM

    index, inputs = _index(tmp_path, reading)
    with FakeVLM() as url:
        model = AM.from_check_yaml(url, "agent", parallel=2)
        res = CR.ask(index, model, inputs, tmp_path / "out", log=lambda *_a: None)
    n = len(index["entries"])
    assert res["stats"]["answered"] == 2 * n and res["stats"]["failed"] == 0
    saved = json.loads((tmp_path / "out" / "answers.json").read_text(encoding="utf-8"))
    assert len(saved["answers"]) == 2 * n and saved["model"] == model.model
    assert {a["which"] for a in saved["answers"]} == {"differences", "questions"}
    assert all(a["data"] is not None for a in saved["answers"])
    assert len(saved["calls"]) == 2 * n and all(c["images"] == 2 for c in saved["calls"])
    # the fake's minimal answers hold no finding: nothing to map
    assert CR.answers_to_findings(index, saved) == []
    # asked again, nothing is sent (every answer is there)
    with FakeVLM() as url:
        model = AM.from_check_yaml(url, "agent")
        res2 = CR.ask(index, model, inputs, tmp_path / "out", log=lambda *_a: None)
    assert res2["stats"]["asked"] == 0


def test_a_passed_deadline_skips_every_call_and_a_failed_call_is_recorded(reading, tmp_path):
    from wenart.agent import model as AM

    index, inputs = _index(tmp_path, reading)
    model = AM.AgentModel("http://127.0.0.1:9/v1", "x/model", retries=0, parallel=1)
    res = CR.ask(index, model, inputs, tmp_path / "late", deadline=time.time() - 1, log=lambda *_a: None)
    assert res["stats"]["skipped"] == 2 * len(index["entries"]) and res["stats"]["asked"] == 0
    # no server at all: the call fails and is recorded, the run goes on
    res = CR.ask(index, model, inputs, tmp_path / "down", which=("differences",), log=lambda *_a: None)
    assert res["stats"]["failed"] == len(index["entries"]) and res["stats"]["answered"] == 0
    saved = json.loads((tmp_path / "down" / "answers.json").read_text(encoding="utf-8"))
    assert all(a["data"] is None and a["errors"] for a in saved["answers"])


def test_answers_are_mapped_to_metres_through_the_entrys_frame():
    entry = {"id": "a/p/L0", "set": "a", "project": "p", "tag": "current", "level": "L0", "folder": "a/p",
             "box": [0.0, 0.0, 2000.0, 1000.0], "tf": [0.01, 0.0, 0.0, 0.0, 0.01, 0.0], "size": [1600, 800],
             "drawing": "L0_drawing.jpg", "model": "L0_model.jpg"}
    answers = {"model": "m", "answers": [
        {"id": "a/p/L0", "which": "differences", "data": {"findings": [
            {"kind": "missing_wall", "x": 500, "y": 0, "description": "top middle", "confidence": 90},
            {"kind": "false_stair", "x": 1000, "y": 1000, "description": "bottom right", "confidence": 40}],
            "summary": ""}},
        {"id": "a/p/L0", "which": "questions", "data": {"answers": [
            {"id": "UL313", "answer": "problem", "x": 0, "y": 1000, "note": "a recess closed"},
            {"id": "UL315", "answer": "ok", "x": 0, "y": 0, "note": ""}]}}]}
    found = CR.answers_to_findings({"entries": [entry]}, answers, "agent")
    assert [f["kind"] for f in found] == ["missing_wall", "false_stair", "question"]
    assert found[0]["at"] == [10.0, 10.0] and found[1]["at"] == [20.0, 0.0] and found[2]["at"] == [0.0, 0.0]
    assert found[0]["confidence"] == 0.9 and found[2]["lesson"] == "UL313" and found[0]["level_id"] == "L0"
    assert CR.question_table(answers) == {"UL313": {"ok": 0, "problem": 1, "cannot_see": 0},
                                          "UL315": {"ok": 1, "problem": 0, "cannot_see": 0}}


# ------------------------------------------------------------------------------------------------------ calibration
def _truth_and_reading():
    """A one-level truth and a reading that differs from it in four known ways: a truth wall the reading lacks, a
    reading room the truth negates, a truth door read as a window, a room with another label."""
    truth_level = {
        "rooms": [{"id": "t1", "label": "Salon", "centroid": [2.0, 2.0], "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]},
                  {"id": "t2", "label": "Mutfak", "centroid": [6.0, 2.0], "polygon": [[4, 0], [8, 0], [8, 4], [4, 4]]},
                  {"id": "t3", "label": "Oda", "centroid": [12.0, 2.0], "polygon": [[10, 0], [14, 0], [14, 4], [10, 4]],
                   "absent": True}],
        "doors": [{"id": "td", "center": [4.0, 2.0], "width": 0.9}],
        "windows": [],
        "openings": [],
        "walls": [{"id": "tw1", "start": [0.0, 0.0], "end": [8.0, 0.0], "thickness": 0.2},
                  {"id": "tw2", "start": [0.0, 10.0], "end": [8.0, 10.0], "thickness": 0.2}],
        "stairs": []}
    read_level = {
        "rooms": [{"id": "r1", "label": "Salon", "centroid": [2.0, 2.0], "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]},
                  {"id": "r2", "label": "Banyo", "centroid": [6.0, 2.0], "polygon": [[4, 0], [8, 0], [8, 4], [4, 4]]},
                  {"id": "r3", "label": "Oda", "centroid": [12.0, 2.0], "polygon": [[10, 0], [14, 0], [14, 4], [10, 4]]}],
        "doors": [],
        "windows": [{"id": "rw", "center": [4.0, 2.0], "width": 0.9}],
        "openings": [],
        "walls": [{"id": "rw1", "start": [0.0, 0.0], "end": [8.0, 0.0], "thickness": 0.2}],
        "stairs": []}
    truth = {"project": "p", "status": "accepted", "levels": [{"id": "L0"}], "per_level": {"L0": truth_level}}
    read = {"project": "p", "levels": [{"id": "L0"}], "per_level": {"L0": read_level}}
    return truth, read


def test_disagreements_name_the_four_planted_differences():
    truth, read = _truth_and_reading()
    ds = CR.disagreements(truth["per_level"]["L0"], read["per_level"]["L0"])
    kinds = {(d["class"], d["side"], d["id"]) for d in ds}
    assert ("walls", "truth_only", "tw2") in kinds
    assert ("rooms", "read_only", "r3") in kinds and any(d.get("negated") for d in ds if d["id"] == "r3")
    assert ("doors", "truth_only", "td") in kinds and ("windows", "read_only", "rw") in kinds
    assert ("rooms", "label", "r2") in kinds
    assert ("walls", "truth_only", "tw1") not in kinds and ("rooms", "read_only", "r1") not in kinds


def test_judge_counts_a_finding_right_only_at_a_disagreement_of_its_kind():
    truth, read = _truth_and_reading()
    ds = CR.disagreements(truth["per_level"]["L0"], read["per_level"]["L0"])
    right = CR.judge({"kind": "missing_wall", "at": [3.0, 10.4]}, ds)
    assert right["right"] and right["matched"]["id"] == "tw2" and right["distance"] <= 0.5
    assert not CR.judge({"kind": "missing_wall", "at": [3.0, 0.3]}, ds)["right"]       # a wall that is read: no
    assert CR.judge({"kind": "door_as_window", "at": [4.5, 2.5]}, ds)["right"]
    assert CR.judge({"kind": "closed_open_air", "at": [11.5, 2.5]}, ds)["right"]       # the negated room
    assert CR.judge({"kind": "wrong_label", "at": [6.5, 2.0]}, ds)["right"]
    far = CR.judge({"kind": "extra_wall", "at": [40.0, 40.0]}, ds)
    assert not far["right"] and far["nearest"]["distance"] > 10


def test_calibrate_gives_precision_recall_and_the_out_of_sample_table(tmp_path):
    truth, read = _truth_and_reading()
    building = {"project": {"id": "p"}, "levels": [{"id": "L0", "label": "Zemin", "order": 0}],
                "rooms": [dict(r, level_id="L0", room_type=None, area_computed=16.0) for r in read["per_level"]["L0"]["rooms"]],
                "openings": [dict(w, level_id="L0", type="window") for w in read["per_level"]["L0"]["windows"]],
                "walls": [dict(w, level_id="L0") for w in read["per_level"]["L0"]["walls"]], "furniture": []}
    frame = {"box": [0.0, 0.0, 2000.0, 1000.0], "tf": [0.01, 0, 0, 0, 0.01, 0], "size": [1600, 800],
             "drawing": "d.jpg", "model": "m.jpg", "level": "L0", "tag": "current"}
    index = {"entries": [dict(frame, id="a/p/L0", set="a", project="p", folder="a/p"),
                         dict(frame, id="c/s/L0", set="c", project="s", folder="c/s", failure_class="x"),
                         dict(frame, id="b/q@old/L0", set="b", project="q", tag="old", folder="b/q@old")]}
    found = [
        {"check": "RC15", "kind": "missing_wall", "at": [3.0, 10.2], "entry": "a/p/L0", "set": "a", "project": "p",
         "level_id": "L0", "confidence": 0.9},
        {"check": "RC15", "kind": "missing_wall", "at": [3.0, 0.2], "entry": "a/p/L0", "set": "a", "project": "p",
         "level_id": "L0", "confidence": 0.9},
        {"check": "RC15", "kind": "wrong_label", "at": [6.0, 2.0], "entry": "a/p/L0", "set": "a", "project": "p",
         "level_id": "L0", "confidence": 0.6},
        {"check": "RC15", "kind": "extra_wall", "at": [3.0, 0.0], "entry": "c/s/L0", "set": "c", "project": "s",
         "level_id": "L0", "confidence": 0.5},
        {"check": "RC15", "kind": "closed_open_air", "at": [1.0, 1.0], "entry": "b/q@old/L0", "set": "b",
         "project": "q", "level_id": "L0", "confidence": 0.7, "description": "a recess closed"},
        {"check": "RC15", "kind": "false_stair", "at": [9.0, 9.0], "entry": "b/q@old/L0", "set": "b",
         "project": "q", "level_id": "L1", "confidence": 0.7, "description": "tiles"}]
    records = [{"id": "C1", "project": "q", "level": "L0", "place": {"x": 1.5, "y": 1.5}, "element_kind": "region",
                "status": "accepted", "right_answer": "open air"},
               {"id": "C2", "project": "q", "level": "L0", "place": {"x": 9.0, "y": 9.0}, "element_kind": "stair",
                "status": "accepted", "right_answer": "no stair"},                    # the finding is on L1: no
               {"id": "C3", "project": "q", "level": None, "place": None, "element_kind": "stair",
                "status": "accepted", "right_answer": "tiles are no stair"},          # by kind: yes
               {"id": "C9", "project": "zzz", "level": "L0", "place": {"x": 1, "y": 1}, "element_kind": "wall"}]
    rc14 = {"C1": "no", "C2": "yes (circulation)", "C3": "no"}
    # set c: the same reading as its truth with a wall the truth lacks, so one real error at (3, 0)
    s_truth = json.loads(json.dumps(truth))
    s_truth["per_level"]["L0"]["walls"] = [s_truth["per_level"]["L0"]["walls"][1]]
    s_truth["per_level"]["L0"]["rooms"][2].pop("absent")
    s_truth["per_level"]["L0"]["rooms"][1]["label"] = "Banyo"
    s_truth["per_level"]["L0"]["doors"] = []
    s_truth["per_level"]["L0"]["windows"] = [{"id": "tw", "center": [4.0, 2.0], "width": 0.9}]
    s_truth["per_level"]["L0"]["walls"].append({"id": "x", "start": [0.0, 10.0], "end": [8.0, 10.0], "thickness": 0.2})
    tr = CR.calibrate(index, found, readings={"a/p": building, "c/s": building},
                      truths={"p": truth, "s": s_truth}, records=records, rc14=rc14, model_key="agent")
    k = tr["kinds"]
    assert k["missing_wall"] == {"findings": 2, "judged_right": 1, "precision": 0.5, "trusted": True, "small_sample": True}
    assert k["wrong_label"]["precision"] == 1.0 and k["extra_wall"]["findings"] == 0      # set c is not precision
    assert k["all"]["findings"] == 3 and k["all"]["judged_right"] == 2
    r = tr["recall"]
    assert r["rc14_records"] == 3 and r["critic_raised"] == 2 and r["rc14_raised"] == 1
    assert r["only_critic"] == ["C1", "C3"] and r["only_rc14"] == ["C2"]
    rows = {x["id"]: x for x in r["records"]}
    assert rows["C1"]["how"] == "place" and rows["C3"]["how"] == "kind" and not rows["C2"]["raised"]
    assert "C9" not in rows
    o = tr["out_of_sample"]
    assert o["projects"] == 1 and o["rows"][0]["verdict"] == "caught" and o["rows"][0]["errors"] >= 1
    assert "missing_wall" in CR.trust_summary(tr)
    # the chance baseline runs on the critic's own counts and kinds, and the density is reported
    assert tr["chance"]["draws"] == 30 and 0.0 <= tr["chance"]["precision"] <= 1.0
    assert tr["density"] == {"levels": 3, "findings": 6, "per_level": 2.0}
    # 6 Nov 2026: a judgement from the drawing replaces the truth's for that finding, and a record's recall by meaning
    for f in found:
        f["rank"] = 0
    found[1]["rank"] = 1
    eye = {"findings": {"a/p/L0#1": {"right": True, "reason": "the drawing has that wall"}},
           "recall": {"C1": {"raised": False, "reason": "the finding names another problem"},
                      "C2": {"raised": True, "reason": "names the tiles"}}}
    tr2 = CR.calibrate(index, found, readings={"a/p": building, "c/s": building},
                       truths={"p": truth, "s": s_truth}, records=records, rc14=rc14, by_eye=eye)
    assert tr2["kinds"]["missing_wall"]["judged_right"] == 2 and tr2["kinds_by_truth_only"]["missing_wall"]["judged_right"] == 1
    j = next(x for x in tr2["judgements"] if x["kind"] == "missing_wall" and x["at"] == [3.0, 0.2])
    assert j["right"] and j["right_by_truth"] is False and j["by_eye"]
    r2 = tr2["recall"]
    assert r2["critic_raised"] == 2 and r2["critic_raised_by_meaning"] == 1 and r2["judged_by_meaning"] == 2
    assert r2["only_critic_by_meaning"] == [] and "by meaning" in CR.trust_summary(tr2)


def test_out_of_sample_verdicts_cover_all_four_cases():
    err = {"L0": [{"class": "walls", "side": "truth_only", "at": [1.0, 1.0], "id": "w", "seg": None}]}
    f_near = [{"project": "s", "kind": "missing_wall", "level_id": "L0", "at": [1.5, 1.0]}]
    f_far = [{"project": "s", "kind": "missing_wall", "level_id": "L0", "at": [9.0, 9.0]}]
    assert CR.out_of_sample_row("s", "x", err, f_near)["verdict"] == "caught"
    assert CR.out_of_sample_row("s", "x", err, f_far)["verdict"] == "missed"
    assert CR.out_of_sample_row("s", "x", {"L0": []}, f_far)["verdict"] == "false_alarm"
    assert CR.out_of_sample_row("s", "x", {"L0": []}, [])["verdict"] == "clean"


# ------------------------------------------------------------------------------------------------- trust and wiring
def _stored(tmp_path, kinds):
    out = tmp_path / "reading"
    out.mkdir()
    b = {"project": {"id": "p"}, "levels": [{"id": "L0", "label": "Zemin", "order": 0, "elevation": 0.0}],
         "rooms": [], "walls": [], "openings": [], "furniture": [], "documents": [], "site": {}}
    (out / "building.json").write_text(json.dumps(b), encoding="utf-8")
    CR.store(out, [{"kind": k, "level_id": "L0", "at": [1.0, 2.0], "description": f"a {k}", "confidence": 0.9,
                    "model": "m", "lesson": "UL313" if k == "question" else None} for k in kinds],
             source={"model": "m"})
    return out


def test_a_kind_below_the_threshold_writes_info_and_one_above_keeps_its_severity(tmp_path):
    out = _stored(tmp_path, ["missing_wall", "false_stair", "merged_rooms", "question"])
    trust = {"threshold": 0.5, "kinds": {"missing_wall": {"findings": 10, "judged_right": 8, "precision": 0.8},
                                         "false_stair": {"findings": 10, "judged_right": 2, "precision": 0.2},
                                         "question": {"findings": 4, "judged_right": 3, "precision": 0.75}}}
    found = {f["kind"]: f for f in CR.findings(out, trust)}
    assert found["missing_wall"]["severity"] == "major" and "precision 0.80" in found["missing_wall"]["message"]
    assert found["false_stair"]["severity"] == "info" and "info only" in found["false_stair"]["message"]
    assert found["merged_rooms"]["severity"] == "info" and "not calibrated" in found["merged_rooms"]["message"]
    assert found["question"]["severity"] == "major" and "lesson UL313" in found["question"]["message"]
    assert all(f["check"] == "RC15" and f["at"] == [1.0, 2.0] and f["level_id"] == "L0" for f in found.values())
    assert CR.findings(tmp_path / "nowhere") == []


def test_check_carries_rc15_as_advisory_findings_outside_the_verdict(tmp_path):
    out = _stored(tmp_path, ["missing_wall"])
    res = RC.check(out)
    rc15 = [f for f in res["findings"] if f["check"] == "RC15"]
    assert len(rc15) == 1 and rc15[0]["advisory"] is True and rc15[0]["kind"] == "missing_wall"
    assert res["verdict"] == "ready" and res["counts"]["critical"] == 0
    assert sum(res["counts"]["advisory"].values()) >= 1
    assert res["counts"]["major"] == sum(1 for f in res["findings"] if f["severity"] == "major" and not f.get("advisory"))
    md = (RC.write(out, res) / "reading_check.md").read_text(encoding="utf-8")
    assert "| RC15 vision critic (advisory) |" in md and "the vision critic RC15" in md


def test_a_failure_of_the_critic_module_is_one_info_finding(tmp_path, monkeypatch):
    out = _stored(tmp_path, ["missing_wall"])

    def boom(out_dir):
        raise RuntimeError("no luck")
    monkeypatch.setattr(CR, "findings", boom)
    res = RC.check(out)
    rc15 = [f for f in res["findings"] if f["check"] == "RC15"]
    assert len(rc15) == 1 and rc15[0]["severity"] == "info" and "no luck" in rc15[0]["message"]
    assert rc15[0]["advisory"] is True and res["verdict"] == "ready"


def test_the_pod_job_declares_its_memory_and_disk_and_the_delegated_command_exists():
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("gpu_run", REPO / "scripts" / "gpu_run.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gpu_run"] = mod
    spec.loader.exec_module(mod)
    assert mod.job_min_vram("scripts/jobs/critic.sh") == 48 and mod.job_disk("scripts/jobs/critic.sh", None) == 80
    job = (REPO / "scripts" / "jobs" / "critic.sh").read_text(encoding="utf-8")
    assert "set -Eeuo pipefail" in job and "wenart.reading_check critic ask" in job and "WENART_DEADLINE" in job
    from wenart.reading_check.__main__ import DELEGATED
    assert DELEGATED["critic"] == ("wenart.reading_check.critic", "main")
