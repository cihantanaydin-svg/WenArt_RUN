"""Argus, the auditor (26 Oct 2026, user: "we need a big smart auditor to check everything in the project ... develop
a system to understand the problem kinds and prevent it happening ... this auditor should have no limits").

The deterministic lines on small buildings: conservation (nothing lost between stages, labelled outdoor spaces built,
drawn symbols typed, every not-built reason listed), the process line (warnings nobody acted on, failed stages and
tests, blocked openings, unused time), the report (one row per problem, kinds, score) and the problem log."""
from __future__ import annotations

import json
from pathlib import Path

from wenart.audit import conservation as CV
from wenart.audit import inputs as I
from wenart.audit import kinds as K
from wenart.audit import process as PR
from wenart.audit import report as R

EV = [{"file": "p.dwg", "method": "vector", "entity": "CIRCLE:1F"}]


def _building(**kw) -> dict:
    b = {"rooms": [{"id": "r_L0_a", "level_id": "L0", "room_type": "living"}],
         "walls": [{"id": "w_L0_001", "level_id": "L0"}],
         "openings": [{"id": "d_L0_001", "type": "door", "level_id": "L0"}],
         "furniture": [{"id": "f_L0_001", "type": "sofa", "asset": {"method": "library"}, "evidence": EV}],
         "site": {"areas": [], "decor": []}}
    b.update(kw)
    return b


def test_kinds_cover_every_check_prefix_and_line():
    for check, kind in K.CHECK_KIND.items():
        assert kind in K.KINDS, check
    for kind in list(K.PREFIX_KIND.values()) + list(K.LINE_KIND.values()):
        assert kind in K.KINDS
    f = K.finding("conservation", "C5", "critical", "sa_x", "lost")
    assert f["kind"] == "lost" and set(K.FINDING_KEYS) <= set(f)
    assert K.kind_of({"check": "Q5"}) == "taste" and K.kind_of({"check": "X9", "line": "process"}) == "no_sense"
    assert K.kind_of({"check": "", "line": "plan_vs_model"}) == "lost"


def test_conservation_lost_between_stages_unless_named():
    a = _building()
    b = _building(furniture=[])
    found = CV.between("decor", a, "agent", b)
    assert [f["check"] for f in found] == ["C1"] and found[0]["owner"] == "agent" and found[0]["kind"] == "lost"
    named = _building(furniture=[], agent_overrides=[{"removed": "f_L0_001"}])
    assert CV.between("decor", a, "agent", named) == []


def test_conservation_not_built_needs_a_reason():
    a = _building()
    b = _building(furniture=[dict(a["furniture"][0], build=False)])
    assert [f["check"] for f in CV.between("decor", a, "agent", b)] == ["C2"]
    c = _building(furniture=[dict(a["furniture"][0], build=False, not_built_reason="through a wall")])
    assert CV.between("decor", a, "agent", c) == []


def test_conservation_labelled_outdoor_space_not_built_is_critical():
    b = _building(site={"areas": [{"id": "sa_L0_veranda", "label": "VERANDA", "build": False}], "decor": []})
    found = CV.untyped(b)
    assert len(found) == 1 and found[0]["check"] == "C5" and found[0]["severity"] == "critical"
    assert found[0]["fix"] == "build_outdoor_space" and "VERANDA" in found[0]["message"]
    built = _building(site={"areas": [{"id": "sa_L0_veranda", "label": "VERANDA", "polygon": [[0, 0], [1, 0], [1, 1]]}],
                            "decor": []})
    assert CV.untyped(built) == []


def test_conservation_untyped_drawn_symbols_are_one_finding_with_every_id():
    decor = [{"id": f"sd_L0_{i:03d}", "kind": "other", "evidence": EV} for i in range(1, 43)]
    found = CV.untyped(_building(site={"areas": [], "decor": decor}))
    assert len(found) == 1 and found[0]["check"] == "C4" and found[0]["kind"] == "untyped"
    assert len(found[0]["evidence"]["ids"]) == 42 and found[0]["fix"] == "type_site_symbols"
    # walls and rooms carry no type: never C4
    assert CV.untyped(_building(walls=[{"id": "w1", "evidence": EV}])) == []


def test_conservation_scene_objects_and_explained_ids():
    final = _building()
    manifest = {"objects": [{"name": "wall_w_L0_001", "wenart_id": "w_L0_001"}, {"wenart_id": "r_L0_a"},
                            {"wenart_id": "d_L0_001"}],
                "furniture": {"not_built": [], "decor_skipped": []}}
    found = CV.in_scene(final, manifest)
    assert [f["target"] for f in found] == ["f_L0_001"] and found[0]["check"] == "C3"
    manifest["furniture"]["not_built"] = [{"id": "f_L0_001", "type": "sofa", "reason": "through a wall"}]
    assert CV.in_scene(final, manifest) == []
    res = CV.audit([("final", final), ("build", final)], manifest)
    c6 = [f for f in res["findings"] if f["check"] == "C6"]
    assert len(c6) == 1 and c6[0]["severity"] == "info" and "through a wall" in c6[0]["message"]


def _inputs(tmp_path: Path, final: dict, manifest: dict, run_manifest=None, junit: str = "") -> I.Inputs:
    inp = I.Inputs(project="p", layout="pod", root=tmp_path, stages=[("final", final)], manifest=manifest,
                   run_manifest=run_manifest)
    if junit:
        p = tmp_path / "junit-full.xml"
        p.write_text(junit, encoding="utf-8")
        inp.junit = [p]
    return inp


def test_process_warnings_nobody_acted_on(tmp_path):
    final = _building(warnings=[
        "p.dwg: balcony 'VERANDA' at (1.0, 2.0) m lies outside the outer walls: an open balcony, recorded in site, "
        "not a room",
        "inferred trees: placed 0 of 3 (74 candidates)",
        "inferred shrubs: placed 4 of 4",
        "roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm)",
        "roof vs the drawn section at s 8.55 m: 7.608 m built, 6.246 m drawn (+136 cm)",
        "roof vs the drawn section at s 9.00 m: 6.000 m built, 6.070 m drawn (-7 cm)",
        "site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0)",
        "sym_L1_004: both passes say front 180 deg, but that side stands within 0.25 m of a wall: the AI front is not "
        "used"])
    found, counts = PR.warnings(_inputs(tmp_path, final, {}))
    by = {f["evidence"]["rule"]: f for f in found}
    assert by["outside_not_room"]["target"] == "VERANDA" and by["outside_not_room"]["fix"] == "build_outdoor_space"
    assert by["shortfall"]["kind"] == "silent" and "0 of 3" in by["shortfall"]["message"]
    assert by["drawn_mismatch"]["severity"] == "major" and len(by["drawn_mismatch"]["evidence"]["cases"]) == 2
    assert by["not_used"]["kind"] == "lost"
    assert counts["shortfall"] == 1 and counts["drawn_mismatch"] == 3 and sum(counts.values()) == 8
    assert "sym_L1_004" not in {f["target"] for f in found if f["evidence"]["rule"] == "not_used"}
    # the site stage built it after all: a note, not a finding
    built = dict(final, site={"areas": [{"id": "sa", "label": "VERANDA", "polygon": [[0, 0], [1, 0], [1, 1]]}]})
    found2, counts2 = PR.warnings(_inputs(tmp_path, built, {}))
    assert "outside_not_room" not in {f["evidence"]["rule"] for f in found2} and counts2["outside_built"] == 1


def test_process_stages_tests_rays_views_time(tmp_path):
    rm = {"run_id": "r1", "deadline": 10_000.0, "finished_utc": "1970-01-01T01:00:00Z",
          "projects": [{"name": "p", "stages": [{"stage": "pipeline", "status": "pending"},
                                                {"stage": "pipeline_final", "status": "ok"},
                                                {"stage": "decor", "status": "failed", "note": "boom"},
                                                {"stage": "photos", "status": "skipped", "note": "no photos"}]}]}
    junit = ('<testsuite><testcase classname="t" name="ok"/><testcase classname="t" name="bad">'
             '<failure message="pane saturation"/></testcase></testsuite>')
    manifest = {"checks": {"door_rays": [{"opening_id": "o_L0_001", "hit": True, "hit_object": "splashback_r",
                                          "hit_kind": "splashback"}, {"opening_id": "d_L0_001", "hit": False}]},
                "rooms_without_view": [{"room_id": "r_L0_x", "label": "Oda", "area_m2": 9.0, "reason": "no camera"}],
                "furniture": {"scene_checks": {"L0": {"S2": {"checked": 4, "failed": 1}, "failed_build": False}},
                              "fallbacks": [{"id": "f1", "type": "sink_kitchen", "reason": "parametric"}]}}
    inp = _inputs(tmp_path, _building(), manifest, rm, junit)
    inp.model_review = {"findings": [{"check": "M3", "severity": "major", "target": "d_L0_001"}]}
    res = PR.audit(inp)
    checks = {(f["check"], f["target"]) for f in res["findings"]}
    assert ("P1", "decor") in checks and ("P1", "pipeline") not in checks and ("P1", "photos") not in checks
    assert ("P4", "bad") in checks and ("P5", "o_L0_001") in checks and ("P5", "L0:S2") in checks
    assert ("P6", "r_L0_x") in checks and ("P7", "f1") in checks and ("P8", "run") in checks


def test_process_big_loop_that_did_not_improve(tmp_path):
    inp = _inputs(tmp_path, _building(), {})
    inp.big_loop = {"cycles": [{"cycle": 0, "score": {"score": 50.0}, "verdict": "first"},
                               {"cycle": 1, "score": {"score": 44.0}, "verdict": "worse", "note": "rolled back"}],
                    "stop": "cycle 1: worse, rolled back"}
    found = PR.loop_result(inp)
    assert {f["severity"] for f in found} == {"minor", "major"}
    inp.big_loop["cycles"][1].update(score={"score": 61.0}, verdict="better")
    assert PR.loop_result(inp) == []


def test_report_merges_one_problem_seen_by_many_lines_and_scores(tmp_path):
    a = K.finding("inspector", "F7", "major", "f_L0_032", "kitchen_counter blocks door o_L0_001")
    b = K.finding("inspector", "G11", "critical", "f_L0_032", "no walkway past f_L0_032", kind="geometry")
    c = K.finding("process", "P5", "major", "o_L0_001", "ray hits the splashback")
    rows = R.merge([a, b, c])
    assert len(rows) == 2 and rows[0]["severity"] == "critical" and rows[0]["seen_by"] == ["inspector:F7",
                                                                                         "inspector:G11"]
    assert R.score([]) == 100.0 and R.score(rows) < R.score(rows[1:]) < 100.0


def test_report_run_write_and_problem_log(tmp_path):
    final = _building(site={"areas": [{"id": "sa_L0_veranda", "label": "VERANDA", "build": False}], "decor": []},
                      warnings=["inferred trees: placed 0 of 3"])
    inp = _inputs(tmp_path, final, {"objects": [{"wenart_id": "w_L0_001"}, {"wenart_id": "r_L0_a"},
                                                {"wenart_id": "d_L0_001"}, {"wenart_id": "f_L0_001"}]},
                  {"run_id": "run1"})
    rep = R.run(inp)
    assert rep["name"] == "Argus" and rep["severity"]["critical"] >= 1 and "lost" in rep["by_kind"]
    assert set(rep["lines"]) >= {"conservation", "process", "model", "inspector", "judge"}
    assert rep["lines"]["judge"]["note"]                              # a line that could not run says why
    log_path = tmp_path / "log.json"
    log = R.update_log(rep, log_path)
    assert not R.recurring(log)
    rep2 = dict(rep, run_id="run2")
    log = R.update_log(rep2, log_path)
    rec = R.recurring(log, "p")
    assert rec and all(len(v["runs"]) == 2 for _s, v in rec)
    log = R.update_log(rep2, log_path)                                 # the same run again: replaced, not counted twice
    assert max(len(v["runs"]) for v in log["signatures"].values()) == 2 and len(log["runs"]) == 2
    prev = R.prevention(rep2, log)
    lost = next(p for p in prev if p["kind"] == "lost")
    assert lost["needs_guard"] and any(n["recurring"] for n in lost["needs_guard"])
    R.write(rep2, tmp_path / "orchestrator", prev)
    md = (tmp_path / "orchestrator" / R.REPORT_MD).read_text(encoding="utf-8")
    assert md.startswith("# Argus") and "VERANDA" in md and "## Prevention" in md
    assert json.loads((tmp_path / "orchestrator" / R.REPORT_JSON).read_text(encoding="utf-8"))["prevention"]


def test_inputs_read_both_layouts(tmp_path):
    out = tmp_path / "outputs" / "p"
    (out / "scene").mkdir(parents=True)
    (out / "building.json").write_text(json.dumps(_building()), encoding="utf-8")
    (out / "scene" / "building_built.json").write_text(json.dumps(_building()), encoding="utf-8")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps({"objects": []}), encoding="utf-8")
    inp = I.pod(out)
    assert [n for n, _b in inp.stages] == ["reading", "build"] and inp.manifest == {"objects": []}
    assert "architect" in inp.missing and "model_review" in inp.missing
    res = tmp_path / "results"
    (res / "furniture" / "p").mkdir(parents=True)
    (res / "renders" / "p").mkdir(parents=True)
    (res / "furniture" / "p" / "building_final.json").write_text(json.dumps(_building()), encoding="utf-8")
    (res / "run_manifest.json").write_text(json.dumps({"run_id": "x"}), encoding="utf-8")
    inp2 = I.collected(res, "p")
    assert [n for n, _b in inp2.stages] == ["final"] and inp2.run_manifest == {"run_id": "x"}


# --------------------------------------------------------------------------
# Argus AI (user, 26 Oct 2026: "use open weight AI models for this auditor, it needs to be smart, it needs to solve
# the problems even without me telling it"): every finding triaged, decisions code-checked, claims verified
# --------------------------------------------------------------------------
import re  # noqa: E402

import pytest  # noqa: E402
from PIL import Image  # noqa: E402

from wenart.agent.model import MockModel  # noqa: E402
from wenart.audit import argus_ai as AX  # noqa: E402

REAL06 = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "real06_building_20261025.json"


def _real06_out(tmp_path: Path) -> Path:
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    b["warnings"] = ["inferred trees: placed 0 of 3 (74 candidates)"]
    out = tmp_path / "real06"
    (out / "scene").mkdir(parents=True)
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    Image.new("RGB", (64, 48), (200, 200, 200)).save(out / "scene" / "top_L1_plan.jpg")
    return out


def test_argus_ai_triages_every_finding_acts_through_code_and_drops_unverifiable_claims(tmp_path, monkeypatch):
    monkeypatch.setattr(AX, "TRIAGE_BATCH", 2)                     # several batches: every finding is still triaged
    out = _real06_out(tmp_path)
    calls = {"triage": 0, "discover": []}

    def reply(body):
        name = MockModel.schema_name(body)
        content = body["messages"][-1]["content"]
        text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
        assert body["chat_template_kwargs"]["enable_thinking"] is True          # Argus thinks
        if name == "argus_triage":
            calls["triage"] += 1
            batch = json.loads(text.split("):\n", 1)[1].split("\n\nArchitect actions", 1)[0])
            items = []
            for it in batch:
                v = {"id": it["id"], "real": True, "kind": "lost", "cause": "site", "fix": "rule_needed",
                     "element": "", "value": "", "rule": "a labelled outdoor space is always built",
                     "why": "the documents label it"}
                if it["check"] in ("conservation:C5", "process:P2"):
                    # a closet decision: it cannot remove the veranda (the dry re-check refuses it), it may settle the
                    # process finding (no code line re-checks that: the architect's verdicts decide)
                    v.update(kind="misread", cause="reading", fix="retype_room", element="r_L1_soyunma_odasi",
                             value="closet", rule="", why="a dressing room off the bedroom is a walk-in closet")
                if it["check"] == "conservation:C4":
                    v.update(real=False, fix="not_a_problem", rule="", why="the circles are the hedge of L0")
                items.append(v)
            return {"items": items}
        calls["discover"].append("image_url" in text)
        return {"found": [
            {"target": "VERANDA", "kind": "lost", "severity": "critical", "what": "the labelled veranda is missing",
             "cause": "site", "fix": "rule_needed", "element": "", "value": "", "rule": "build every labelled space"},
            {"target": "garage_north", "kind": "lost", "severity": "major", "what": "a garage is missing",
             "cause": "reading", "fix": "rule_needed", "element": "", "value": "", "rule": ""}]}

    rec = AX.investigate(out, MockModel(critic=[reply] * 40), out=lambda s: None)
    assert rec["items"] >= 3 and rec["triaged"] == rec["items"] and calls["triage"] == (rec["items"] + 1) // 2
    assert calls["discover"] == [False, True]                      # one call per floor, the floor's image when there is one
    by = {(e["aid"], e["verdict"]) for e in rec["decisions"]}
    checks = {v["id"]: v for v in rec["verdicts"]}
    assert len(rec["decisions"]) == 2 and {v for _a, v in by} == {"accepted", "refused"}
    refused = next(e for e in rec["decisions"] if e["verdict"] == "refused")
    assert "still there" in refused["why"]                         # the veranda is not fixed by a closet
    saved = json.loads((out / "orchestrator" / "architect_answers.json").read_text(encoding="utf-8"))["answers"]
    assert saved["AI.retype_room:r_L1_soyunma_odasi"]["by"] == "argus"
    assert len(rec["disputed"]) == 1 and checks[rec["disputed"][0]["aid"]]["real"] is False
    assert {f["target"] for f in rec["findings"] if f["check"] == "AI1"} == {"sa_L0_veranda"}
    assert [d["target"] for d in rec["dropped"]] == ["garage_north", "garage_north"]
    assert any("labelled" in g["rule"] for g in rec["guards"])
    assert (out / "orchestrator" / AX.LOG_MD).read_text(encoding="utf-8").startswith("# Argus AI")
    # the report reads Argus AI's line: its veranda is the same problem as conservation's C5 (one row, seen by both)
    rep = R.run(I.pod(out))
    row = next(f for f in rep["findings"] if f["target"] == "sa_L0_veranda")
    assert "argus_ai" in rep["lines"] and set(row["seen_by"]) == {"conservation:C5", "argus_ai:AI1"}


def test_argus_ai_at_the_end_proposes_and_keeps_the_first_record(tmp_path):
    out = _real06_out(tmp_path)

    def reply(body):
        if MockModel.schema_name(body) == "argus_triage":
            text = body["messages"][-1]["content"]
            return {"items": [{"id": aid, "real": True, "kind": "misread", "cause": "reading", "fix": "retype_room",
                               "element": "r_L1_soyunma_odasi", "value": "closet", "rule": "", "why": "a closet"}
                              for aid in re.findall(r'"id": "(F\d+)"', text)[-1:]]}
        return {"found": []}

    rec = AX.investigate(out, MockModel(critic=[reply] * 40), out=lambda s: None, act_on=False)
    assert rec["decisions"] and {e["verdict"] for e in rec["decisions"]} == {"proposed"}
    assert (out / "orchestrator" / AX.FINAL_JSON).is_file() and not (out / "orchestrator" / AX.LOG_JSON).is_file()
    assert not (out / "orchestrator" / "architect_answers.json").is_file()


def test_argus_target_gone_and_work_for_the_agent(tmp_path):
    lost = K.finding("conservation", "C5", "critical", "sa_L0_veranda", "not built")
    open_ = {"building": {"site": {"areas": [{"id": "sa_L0_veranda", "label": "VERANDA", "build": False}]}}}
    built = {"building": {"site": {"areas": [{"id": "sa_L0_veranda", "label": "VERANDA",
                                              "polygon": [[0, 0], [2, 0], [2, 2]]}]}}}
    assert AX.target_gone(lost, open_) is False and AX.target_gone(lost, built) is True
    assert AX.target_gone(K.finding("judge", "J1", "major", "cam_1", "ugly"), built) is None
    odir = tmp_path / "orchestrator"
    odir.mkdir()
    (odir / AX.LOG_JSON).write_text(json.dumps({"work": [
        {"fix": "agent_round", "severity": "major", "target": "f_L0_032", "check": "F7", "message": "blocks a door"},
        {"fix": "agent_round", "severity": "minor", "target": "f1", "message": "small"},
        {"fix": "rerun_stage", "severity": "major", "target": "decor", "message": "failed"}]}), encoding="utf-8")
    work = AX.work_findings(tmp_path)
    assert [w["target"] for w in work] == ["f_L0_032"] and work[0]["source"] == "argus"


def test_argus_facts_and_known_targets_name_the_labels():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    lines = AX.facts(b)
    assert any("site area sa_L0_veranda 'VERANDA'" in x and "NOT built" in x for x in lines)
    assert any(x.startswith("site symbols drawn: other 42") for x in lines)
    known = AX.known_targets(b)
    assert known["veranda"] == "sa_L0_veranda" and known["l1"] == "L1" and known["r_l0_salon"] == "r_L0_salon"


def test_house_findings_are_the_defects_of_the_house():
    rows = [K.finding("conservation", "C5", "critical", "sa", "lost"),
            K.finding("process", "P4", "major", "t", "a test failed", kind="process"),
            K.finding("process", "P2", "major", "roof", "differs from the section", kind="misread"),
            K.finding("process", "P8", "major", "run", "time left", kind="process"),
            K.finding("inspector", "F7", "critical", "f1", "blocks a door"),
            K.finding("conservation", "C6", "info", "x", "not built: reason")]
    assert [f["target"] for f in R.house_findings({"findings": rows})] == ["sa", "roof"]


# --------------------------------------------------------------------------
# The sense line: the house can be walked through
# --------------------------------------------------------------------------
from wenart.audit import sense as SN  # noqa: E402


def _sq(rid, x0, x1, rtype, level="L0"):
    return {"id": rid, "level_id": level, "room_type": rtype, "label": rid,
            "polygon": [[x0, 0], [x1, 0], [x1, 4], [x0, 4]]}


def _wall(wid, a, b, level="L0"):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": 0.2}


def _house(first="living", door_bc=False):
    rooms = [_sq("A", 0, 4, first), _sq("B", 4.2, 8, "bedroom"), _sq("C", 8.2, 12, "kitchen")]
    walls = [_wall("w_out", (0, -0.1), (12, -0.1)), _wall("w_ab", (4.1, 0), (4.1, 4)), _wall("w_bc", (8.1, 0), (8.1, 4))]
    ops = [{"id": "d_out", "type": "door", "level_id": "L0", "wall_id": "w_out", "center": [2, -0.1], "width": 0.9},
           {"id": "d_ab", "type": "door", "level_id": "L0", "wall_id": "w_ab", "center": [4.1, 2], "width": 0.8},
           {"id": "w_c", "type": "window", "level_id": "L0", "wall_id": "w_out", "center": [10, -0.1], "width": 1.2}]
    if door_bc:
        ops.append({"id": "d_bc", "type": "door", "level_id": "L0", "wall_id": "w_bc", "center": [8.1, 2], "width": 0.8})
    return {"levels": [{"id": "L0", "elevation": 0.0}], "rooms": rooms, "walls": walls, "openings": ops,
            "furniture": []}


def test_sense_a_room_nobody_can_enter_and_a_bathroom_as_a_corridor():
    found = SN.audit(_house())["findings"]
    assert [(f["check"], f["target"]) for f in found] == [("N1", "C")] and found[0]["severity"] == "critical"
    assert "window" not in str(SN.graph(_house())[1].values())          # a window is no way in
    assert SN.audit(_house(door_bc=True))["findings"] == []
    wet = SN.audit(_house(first="bathroom", door_bc=True))["findings"]
    assert {(f["check"], f["target"]) for f in wet} == {("N2", "B"), ("N2", "C")}


def test_sense_open_plan_and_stairs_join_rooms_and_levels():
    b = _house()
    b["rooms"][2]["polygon"] = [[8.0, 0], [12, 0], [12, 4], [8.0, 4]]   # C touches B: one open plan
    b["walls"] = b["walls"][:2]
    assert SN.audit(b)["findings"] == []
    up = _house(door_bc=True)
    up["levels"].append({"id": "L1", "elevation": 3.0})
    up["rooms"].append(_sq("U", 0, 4, "bedroom", "L1"))
    found = SN.audit(up)["findings"]
    assert {(f["check"], f["target"]) for f in found} == {("N1", "U"), ("N3", "L1")}
    up["furniture"].append({"id": "f_st", "type": "stair", "room_id": "A", "level_id": "L0",
                            "footprint": {"center": [2, 2], "size": [1, 3]}})
    assert SN.audit(up)["findings"] == []
    no_way = _house(door_bc=True)
    no_way["openings"] = [o for o in no_way["openings"] if o["id"] != "d_out"]
    assert "N4" in {f["check"] for f in SN.audit(no_way)["findings"]}
