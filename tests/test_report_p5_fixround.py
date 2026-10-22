"""Fix round after P5 (22 Oct 2026), track P_report: the final report after pod P5 (real04).

- The AI orchestrator section reads only the latest run of the appended ``orchestrator/log.json`` (events from
  ``run_first_seq``, calls from ``run_first_call``, the overrides of this run), compares the measured findings removed
  with the dry re-checks' prediction of the same rounds, adds the new findings and the net, and says when the "after"
  totals precede the last round's edits (P5: M12 and P3 edits listed next to P5's, 7 rounds over 3 runs, "33
  measured; 40 predicted" over rounds 1-3 against 1-4).
- Metric 10 reads the L-1b sofas from the variant's scene and counts module / parametric fabric slots (P5: "0 of 26").
- The report's texts follow the final building: the advisory "not typed" names only pieces still untyped, the
  recognition table gives the actual reason a piece is not built, the drawn-piece check counts the adjusted pieces.
- The pieces changed under the user's decisions of 22 Oct 2026 (code retypes of vision-typed pieces, bath / shower
  shrinks) are listed in the inferred / AI-changed section, also without the orchestrator, and an unlabelled one is
  an advisory flag.
- Fix round after P5 (22 Oct 2026), review (section 5): a code retype the agent moved later keeps the code's reason and
  its plan crop; a bath / shower shrunk across its depth is a wet shrink; a cut run's edits replayed into this building
  stay in the section; "measured" and "net" share one finding key; the agent's not-furniture mark follows the
  reading's reason; Metric 10 counts a module / parametric fabric slot only when a colour was asked. Each of these
  tests failed before its fix.

Every test fails on BASE (29e54d0)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from test_m13_report import asset_abo, make_run, obj, piece
from test_report import make_m7_project, make_project
from test_report_agent import write_agent_run
from wenart.report import agent as AG
from wenart.report import final as F
from wenart.report import m10 as M
from wenart.report import metrics13 as MX

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "runs" / "20261017-224848-full" / "results"


# --------------------------------------------------------------------------
# 1. The orchestrator section: the latest run of an appended log
# --------------------------------------------------------------------------

def _finding(seq, rnd, check, target, severity="major"):
    return {"seq": seq, "round": rnd, "kind": "finding", "source": "code", "checklist": check, "severity": severity,
            "target": target, "room_id": "r1", "finding": f"{check} on {target}", "evidence": {"metrics": {}}}


def _edit(seq, rnd, check, target, kind="edit"):
    return {"seq": seq, "round": rnd, "kind": kind, "tool": "move_piece", "target": target, "checklist": check,
            "validation": {"accepted": kind == "edit", "failed_checks": [] if kind == "edit" else ["no_overlap"]},
            "label": "adjusted_by_ai", "reason": f"fix {target}"}


def _round(seq, rnd, predicted):
    return {"seq": seq, "round": rnd, "kind": "round", "seconds": 60.0,
            "counts": {"rooms_code": 1, "findings_removed": predicted},
            "evidence": {"rooms_vision": ["r1"], "rooms_planner": ["r1"], "rooms_fixable": ["r1"]}}


def appended_log() -> dict:
    """An earlier run (seq 1-5: an F3 critical, an accepted and a rejected edit) and this run from seq 10: round 1
    with F4:f1 and S2:f2 and an accepted edit on f1, round 2 with S2:f2 and a new G6:f3 and one accepted edit."""
    old = [_round(1, 1, 3), _finding(2, 1, "F3", "f_old", "critical"), _edit(3, 1, "F3", "f_old"),
           _edit(4, 1, "F3", "f_old", "rejected_edit"),
           {"seq": 5, "round": 1, "kind": "stop", "reason": "max rounds reached"}]
    new = [_finding(10, 1, "F4", "f1"), _finding(11, 1, "S2", "f2"), _edit(12, 1, "F4", "f1"), _round(13, 1, 1),
           _finding(14, 2, "S2", "f2"), _finding(15, 2, "G6", "f3"), _edit(16, 2, "S2", "f2"), _round(17, 2, 4),
           {"seq": 18, "round": 2, "kind": "stop", "reason": "final round for critical findings done"}]
    return {"schema_version": "0.1", "kind": "agent_log", "project": "toy", "model": "Qwen/Qwen3.8-27B-FP8",
            "revision": "0" * 40, "stop": {"round": 2, "reason": "final round for critical findings done", "seq": 18},
            "run_first_seq": 10, "run_first_call": 1, "events": old + new,
            "calls": [{"call_id": "r1-old", "kind": "chat", "prompt_tokens": 1000, "completion_tokens": 100},
                      {"call_id": "r1-new", "kind": "chat", "prompt_tokens": 10, "completion_tokens": 2}]}


def write_appended(out: Path) -> None:
    orch = out / "orchestrator"
    orch.mkdir(parents=True, exist_ok=True)
    (orch / "log.json").write_text(json.dumps(appended_log()), encoding="utf-8")
    edits = [{"seq": 1, "round": 1, "tool": "report_library_gap", "args": {"type": "stair", "reason": "old run"},
              "result": {"accepted": True, "log_seq": 3}},
             {"seq": 2, "round": 1, "tool": "move_piece", "args": {"piece_id": "f_old"},
              "result": {"accepted": False, "rolled_back": "refit failed", "log_seq": 4}},
             {"seq": 3, "round": 1, "tool": "report_library_gap", "args": {"type": "chair", "reason": "this run"},
              "result": {"accepted": True, "log_seq": 12}}]
    (orch / "overrides.json").write_text(json.dumps({"project": "toy", "edits": edits}), encoding="utf-8")
    # an earlier run's metrics.json left on the volume: computed again for this run
    (orch / "metrics.json").write_text(json.dumps({"first_seq": 1, "edits": {}}), encoding="utf-8")


def test_the_orchestrator_section_reads_only_the_latest_run_of_an_appended_log(tmp_path):
    out = tmp_path / "toy"
    write_appended(out)
    block = AG.agent_block(out, out / "final", building={})
    assert [r["round"] for r in block["rounds"]] == [1, 2]
    assert block["rounds"][0]["findings"] == {"critical": 0, "major": 2, "minor": 0}       # not the old F3 critical
    assert [e["seq"] for e in block["edits"]] == [12, 16] and block["rejected"] == []
    assert "F3" not in block["findings_by_check"] and block["findings_by_check"]["S2"]["major"] == 2
    assert block["calls"] == 1 and block["tokens"] == 12
    assert [g["type"] for g in block["library_gaps"]] == ["chair"] and block["rolled_back"] == []
    assert block["first_seq"] == 10 and block["earlier"] == {"events": 5, "calls": 1, "edits": 2, "replayed": 0}
    assert block["metrics"]["first_seq"] == 10 and block["metrics"]["edits"]["accepted"] == 2
    # round 1 -> 2: F4:f1 gone, G6:f3 new (the dry re-checks predicted 1 for round 1 and 4 for the last round)
    assert block["removed_net"] == {"per_round": {"1": {"gone": 1, "new": 1}}, "gone": 1, "new": 1, "net": 0,
                                    "rounds_measured": [1], "last_round": 2}
    assert block["last_round_accepted"] == {"round": 2, "accepted": 1}
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "This run only (log events from seq 10): earlier runs of the appended log are left out (5 events, " \
           "1 model calls, 2 stored edits)" in md
    assert "| critical/major findings removed in round 1 (measured by the next round; predicted by the dry " \
           "re-checks of the same rounds) | 1 measured; 1 predicted (the last round's dry re-checks predicted 4 " \
           "more, not measured) |" in md
    assert "| new critical/major findings in round 1; net removed (gone - new) | 1 new; net 0 |" in md
    assert "| major before -> after (after: round 2's critics, before its 1 accepted edit(s)) | 2 -> 2 |" in md
    assert "f_old" not in md and "stair" not in md


def test_a_log_without_run_first_seq_keeps_every_run():
    log = appended_log()
    log.pop("run_first_seq")
    log.pop("run_first_call")
    scope = AG.run_scope(log, {"edits": [{"seq": 1, "result": {"log_seq": 3}}]})
    assert len(scope["events"]) == len(log["events"]) and len(scope["calls"]) == 2 and len(scope["edits"]) == 1
    assert scope["earlier"] == {"events": 0, "calls": 0, "edits": 0, "replayed": 0}
    # an override without a log_seq counts when it was made on the current building_decor.json
    log = appended_log()
    edits = {"edits": [{"seq": 1, "source_sha": "old"}, {"seq": 2, "source_sha": "now"}, {"seq": 3}]}
    assert [e["seq"] for e in AG.run_scope(log, edits, "now")["edits"]] == [2, 3]
    assert AG.removed_net([_finding(1, 1, "F4", "f1")]) is None              # one round: nothing measured


@pytest.mark.skipif(not (P5 / "agent" / "real04" / "log.json").is_file(),
                    reason="the P5 run folder is not here (runs/ is not committed)")
def test_the_orchestrator_section_on_the_p5_results(tmp_path):
    out = tmp_path / "real04"
    out.mkdir()
    os.symlink(P5 / "agent" / "real04", out / "orchestrator")
    os.symlink(P5 / "run" / "real04", out / "run")
    for name in ("building_final.json", "building_decor.json"):
        os.symlink(P5 / "furniture" / "real04" / name, out / name)
    block = AG.agent_block(out, tmp_path / "final", private=True)
    # P5 alone: 4 rounds, 27 accepted (the old section: 7 rounds, 249 accepted from seq 297 on)
    assert len(block["rounds"]) == 4 and len(block["edits"]) == 27 and min(e["seq"] for e in block["edits"]) >= 4364
    assert block["findings_by_check"]["X2"]["critical"] == 5          # the old section: 70 over three runs
    assert block["earlier"]["edits"] == 222 and len(block["library_gaps"]) == 1
    assert (block["removed_net"]["gone"], block["removed_net"]["new"], block["removed_net"]["net"]) == (33, 6, 27)
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "33 measured; 38 predicted (the last round's dry re-checks predicted 2 more, not measured)" in md


# --------------------------------------------------------------------------
# 2. Metric 10: the variant's scene and the module fabric slots
# --------------------------------------------------------------------------

def test_metric_10_reads_the_variant_scene_and_counts_module_fabric_slots(tmp_path):
    out = make_run(tmp_path)
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    sofa_l = {"library": "module", "asset_id": "module:sofa_corner:sofa_l", "method": "module", "licence": "n/a",
              "licence_flag": "none", "fabric_colour": "light grey"}
    asked = dict(asset_abo("abo_B0SOFA0001", "Grey Sofa"), fabric_colour="light grey")
    b["furniture"] += [piece("f_8", "sofa_corner", "r_salon", asset=sofa_l),
                       dict(piece("f_9", "sofa", "r_salon", asset=dict(asked)), level_id="L-1b"),
                       piece("f_10", "sofa", "r_salon", asset=dict(asked)),
                       piece("f_11", "ottoman", "r_salon", asset=asset_abo("abo_B0OTTO0001", "Ottoman"))]
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    sc = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    sc["objects"] += [obj("furn_f_8", "f_8", "furniture", 9, type="sofa_corner", asset=sofa_l,
                          material_keys={"fabric": "fabric_linen", "wood": "wood_veneer_oak_light"}),
                      obj("furn_f_10", "f_10", "furniture", 10, type="sofa", asset=asked)]
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(sc), encoding="utf-8")
    variant = out / "variants" / "alt" / "scene"
    variant.mkdir(parents=True)
    (variant / "scene_manifest.json").write_text(json.dumps({"objects": [
        obj("furn_f_9", "f_9", "furniture", 3, type="sofa", asset=asked,
            recolour={"fabric": {"colour": "light grey"}})]}), encoding="utf-8")
    m = MX.metric_10(MX.locate(out))
    p = m["parts"]
    assert p["fabric_recoloured"] == ["f_1", "f_9"] and p["fabric_slot"] == ["f_8"]
    assert p["not_recolourable"] == {"f_10": "abo_B0SOFA0001"} and p["not_recolourable_models"] == ["abo_B0SOFA0001"]
    assert p["no_colour_asked"] == {"f_7": "abo_B0CHAIR01"} and p["no_scene"] == ["f_11"]
    assert p["from_variant"] == {"f_9": "alt"} and p["upholstered_built"] == 6 and p["upholstered_in_scene"] == 5
    assert p["fabric_applied_n"] == 3 and p["fabric_applied"] == 60.0
    assert "fabric colour applied: 3 of 5 (60 %) (recoloured 2, module / parametric fabric slot 1" in m["text"]
    assert "in no scene: f_11" in m["text"]


@pytest.mark.skipif(not (P5 / "renders" / "real04" / "variants").is_dir(),
                    reason="the P5 run folder is not here (runs/ is not committed)")
def test_metric_10_on_the_p5_results():
    m = MX.metric_10(MX.locate(P5 / "final" / "real04"))
    assert m["parts"]["fabric_applied_n"] == 4 and m["parts"]["upholstered_in_scene"] == 26      # was 0 of 26
    assert m["parts"]["fabric_recoloured"] == ["f_L-1b_041"]
    assert m["parts"]["fabric_slot"] == ["f_L-1_053", "f_L-1_054", "f_L-1b_045"]
    assert len(m["parts"]["from_variant"]) == 4 and "abo_B075X4F5CS" in m["parts"]["not_recolourable_models"]


# --------------------------------------------------------------------------
# 3. The report's texts follow the final building
# --------------------------------------------------------------------------

def _cand(t1, t2):
    return [{"type": t1, "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": 1, "confidence": 0.95},
            {"type": t2, "model": "zai-org/GLM-4.6V-Flash", "pass": 2, "confidence": 0.9}]


def _drawn(pid, ftype, **extra):
    return {"id": pid, "type": ftype, "level_id": "L0", "room_id": "r_L0_salon", "source": "from_documents",
            "status": "unverified", "footprint": {"center": [1.0, 1.0], "size": [0.6, 0.6], "rotation_deg": 0.0},
            **extra}


def test_report_texts_follow_the_final_building(tmp_path):
    out = make_m7_project(tmp_path)
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    b["furniture"] += [
        # the passes disagreed, a rule typed it afterwards (P5: f_L-1_069..072): typed, not an open item
        _drawn("f_20", "armchair", type_method="rule", type_candidates=_cand("table_coffee", "armchair")),
        # an A-BA column the passes typed ottoman (P5: f_L-1_079)
        _drawn("f_21", "ottoman", type_method="ai_two_pass", type_candidates=_cand("ottoman", "ottoman"), build=False,
               inferred_reason="drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not "
                               "built)"),
        # the agent's mark (P5: f_L1_021)
        _drawn("f_22", "table_coffee", type_method="ai_two_pass", type_candidates=_cand("table_coffee", "table_coffee"),
               build=False, adjusted_by_ai={"reason": "the crop shows a stair", "model": "Qwen/Qwen3.8-27B-FP8",
                                            "round": 2, "not_furniture": "other"}),
        _drawn("f_23", "unknown", type_method="none", type_candidates=_cand("not_furniture", "not_furniture"),
               build=False)]
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    m = F.write_final(out)
    flags = [f for f in m["advisory_flags"] if "not typed" in f]
    assert flags == ["1 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; "
                     "footprint kept): f_9"]
    ai = {p["id"]: p for p in m["recognition"]["ai_typed"]}
    assert ai["f_20"]["typed"] and not ai["f_9"]["typed"]
    assert ai["f_21"]["not_built_reason"].startswith("drawn on the 'A-BA' layer(s)")
    assert ai["f_22"]["not_built_reason"] == ("marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: the "
                                              "crop shows a stair")
    assert ai["f_23"]["not_built_reason"] == "both recognition passes call it not_furniture"
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| f_20 | r_L0_salon | armchair | no (typed by rule) |" in md
    assert "| no (marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: the crop shows a stair) |" in md
    assert "drawn symbol, not built" not in md


def test_the_drawn_piece_check_counts_the_changes_of_the_final_building():
    check = {"drawn_check": {"reference": "source building.json", "mode": "complete", "tolerance_m": 0.05,
                             "tolerance_deg": 1.0, "pieces": [{"id": "f_1"}, {"id": "f_2"}, {"id": "f_3"}],
                             "checked": 3, "ok": 3, "failed": [], "modified": [], "violations": [], "notes": []}}
    building = {"furniture": [_drawn("f_1", "sofa", adjusted_by_ai={"reason": "size snap"}),
                              _drawn("f_2", "bed_double", modified_by_ai=True), _drawn("f_3", "wardrobe"),
                              dict(_drawn("f_4", "chair", adjusted_by_ai={"reason": "x"}), source="added_by_ai")]}
    block = M.drawn_block(check, building)
    assert block["changed"] == ["f_1", "f_2"] and block["modified"] == 0
    assert "3 ok, 0 failed; 2 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai " \
           "label in the final building" in M.drawn_lines(block)[3]
    assert M.drawn_lines(M.drawn_block(check))[3].endswith("0 changed by the AI.")       # no building: as before


# --------------------------------------------------------------------------
# 4. The pieces changed under the user's decisions of 22 Oct 2026
# --------------------------------------------------------------------------

def decision_building() -> dict:
    fp = {"center": [1.0, 1.0], "size": [0.5, 0.45], "rotation_deg": 0.0}
    return {"furniture": [
        # code retyped a vision "floor_lamp" at a bed head to its nightstand (labelled, with the plan crop)
        _drawn("f_a", "nightstand", drawn_type="floor_lamp", type_method="nightstand_symbol",
               type_candidates=_cand("floor_lamp", "floor_lamp"), footprint=fp, drawn_footprint=fp,
               adjusted_by_ai={"by": "code", "rule": "nightstand_symbol", "reason": "a lamp of a nightstand's size",
                               "plan_crop": "recognition/crops/sym_L0_031_ctx.png"}),
        # the same retype without its label (must still be listed)
        _drawn("f_b", "nightstand", type_method="twin", type_candidates=_cand("floor_lamp", "floor_lamp"),
               evidence=[{"method": "inferred", "rule": "twin", "text": "nightstand: the twin's type (plan crop "
                                                                        "recognition/crops/sym_L0_032_ctx.png)"}]),
        # the agent's retype_piece: not a code retype
        _drawn("f_c", "sofa", drawn_type="armchair", type_method="ai_two_pass",
               type_candidates=_cand("armchair", "armchair"),
               adjusted_by_ai={"model": "Qwen/Qwen3.8-27B-FP8", "round": 1, "reason": "a sofa",
                               "retype": {"to": "sofa"}}),
        # a bathtub 5 cm longer than its bay, shrunk to a real product
        _drawn("f_d", "bathtub", footprint={"center": [1.0, 1.0], "size": [1.70, 0.75], "rotation_deg": 0.0},
               drawn_footprint={"center": [1.0, 1.0], "size": [1.75, 0.75], "rotation_deg": 0.0},
               adjusted_by_ai={"by": "code", "rule": "wet_bay_fit", "reason": "misread size: 1.75 m in a 1.70 m bay"}),
        _drawn("f_e", "shower", footprint=fp, drawn_footprint=fp),
        # both passes not_furniture: nothing was typed, nothing retyped
        _drawn("f_f", "unknown", type_method="none", type_candidates=_cand("not_furniture", "not_furniture"),
               build=False)]}


def test_decision_changes_and_the_inferred_rows():
    changes = {c["id"]: c for c in AG.decision_changes(decision_building())}
    assert set(changes) == {"f_a", "f_b", "f_d"}
    assert changes["f_a"]["decision"] == "code_retype" and changes["f_a"]["labelled"] is True
    assert changes["f_a"]["change"] == "type floor_lamp -> nightstand" and changes["f_a"]["by"] == "code"
    assert changes["f_a"]["rule"] == "nightstand_symbol"
    assert changes["f_a"]["plan_crop"] == "recognition/crops/sym_L0_031_ctx.png"
    assert changes["f_b"]["labelled"] is False and changes["f_b"]["rule"] == "twin"
    assert changes["f_b"]["plan_crop"] == "recognition/crops/sym_L0_032_ctx.png"       # from the piece's evidence
    assert changes["f_d"]["decision"] == "wet_shrink"
    assert changes["f_d"]["change"] == "size 1.75 x 0.75 m -> 1.70 x 0.75 m"
    rows = {i["id"]: i for i in AG.inferred_items(decision_building(), None)}
    assert set(rows) == {"f_a", "f_b", "f_c", "f_d"}
    assert rows["f_b"]["labels"] == ["unlabelled"] and rows["f_b"]["decision"] == "code_retype"
    assert rows["f_c"]["decision"] is None and rows["f_c"]["by"] == "Qwen/Qwen3.8-27B-FP8"
    assert rows["f_c"]["change"] == "type armchair -> sofa"
    md = "\n".join(AG.inferred_lines(list(rows.values())))
    assert "| f_b | piece | nightstand | r_L0_salon | unlabelled (code retype of a vision-typed piece, decision of " \
           "22 Oct 2026) | type floor_lamp -> nightstand | code (twin) |" in md
    assert "| f_d | piece | bathtub | r_L0_salon | adjusted_by_ai (bath/shower longer than its bay shrunk, decision " \
           "of 22 Oct 2026) | size 1.75 x 0.75 m -> 1.70 x 0.75 m | code (wet_bay_fit) |" in md


def test_the_final_report_lists_them_without_and_with_the_orchestrator(tmp_path):
    out = make_project(tmp_path)
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    b["furniture"] += decision_building()["furniture"]
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    m = F.write_final(out)
    assert m["agent"] is None and [c["id"] for c in m["decision_changes"]] == ["f_a", "f_b", "f_d"]
    assert F.validate_final_manifest(m) == []
    assert ("1 drawn piece(s) retyped or resized by code without an adjusted_by_ai label (listed under Inferred and "
            "AI-changed items): f_b") in m["advisory_flags"]
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    section = md.split("\n## Inferred and AI-changed items\n")[1].split("\n## ")[0]
    assert "| f_b | piece | nightstand |" in section and "| f_d | piece | bathtub |" in section
    write_agent_run(out)
    F.write_final(out)
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "\n## Inferred and AI-changed items\n" not in md                   # the orchestrator's section lists them
    section = md.split("### Inferred and AI-changed items")[1].split("\n### ")[0]
    assert "| f_b | piece | nightstand |" in section and "code retype of a vision-typed piece" in section


# --------------------------------------------------------------------------
# 5. Fix round after P5 (22 Oct 2026), review of the report track
# --------------------------------------------------------------------------

NIGHTSTAND_TEXT = ("nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the "
                   "drawn bed_double f_L0_007's head: the bed's nightstand drawn with its table lamp, not a floor lamp "
                   "(plan crop recognition/crops/sym_L0_016_ctx.png)")
MOVE_TEXT = "Shift the lower nightstand away from the bed edge to clear the 0.06 m² overlap"


def moved_retypes() -> list[dict]:
    """P5 f_L0_032: retyped by the nightstand_symbol rule, then moved by the agent, whose record replaced the code's
    (data written before edit_ops kept ``previous``); f_g: the same with the code's record under ``previous``."""
    fp = {"center": [1.0, 1.0], "size": [0.5, 0.45], "rotation_deg": 0.0}
    move = {"reason": MOVE_TEXT, "round": 1, "log_seq": 4639, "model": "Qwen/Qwen3.8-27B-FP8",
            "changed": {"type": "floor_lamp", "footprint": fp}}
    old = _drawn("f_L0_032", "nightstand", drawn_type="floor_lamp", type_method="nightstand_symbol",
                 type_candidates=_cand("floor_lamp", "floor_lamp"), footprint=fp, drawn_footprint=fp, inferred=True,
                 inferred_reason=NIGHTSTAND_TEXT, adjusted_by_ai=dict(move),
                 evidence=[{"method": "inferred", "rule": "furniture.infer.nightstand_symbols", "text": NIGHTSTAND_TEXT,
                            "crop": "recognition/crops/sym_L0_016_ctx.png"}])
    code = {"by": "code", "stage": "reading", "rule": "nightstand_symbol", "reason": "a lamp of a nightstand's size",
            "plan_crop": "recognition/crops/sym_L0_017_ctx.png", "changed": {"type": "floor_lamp"}}
    new = _drawn("f_g", "nightstand", drawn_type="floor_lamp", type_method="nightstand_symbol",
                 type_candidates=_cand("floor_lamp", "floor_lamp"), footprint=fp, drawn_footprint=fp,
                 adjusted_by_ai=dict(move, previous=[code]))
    return [old, new]


def test_a_code_retype_moved_later_keeps_its_own_reason_and_plan_crop():
    """Review finding: the row of a code retype the agent moved later showed the move's reason and no plan crop."""
    rows = {i["id"]: i for i in AG.inferred_items({"furniture": moved_retypes()}, None)}
    assert rows["f_L0_032"]["reason"] == f"{NIGHTSTAND_TEXT}; then: {MOVE_TEXT}"
    assert rows["f_L0_032"]["plan_crop"] == "recognition/crops/sym_L0_016_ctx.png"
    assert rows["f_L0_032"]["by"] == "code, then Qwen/Qwen3.8-27B-FP8"
    assert rows["f_g"]["reason"] == f"a lamp of a nightstand's size; then: {MOVE_TEXT}"
    assert rows["f_g"]["plan_crop"] == "recognition/crops/sym_L0_017_ctx.png" and rows["f_g"]["rule"] == \
        "nightstand_symbol"
    changes = {c["id"]: c for c in AG.decision_changes({"furniture": moved_retypes()})}
    assert changes["f_L0_032"]["reason"] == rows["f_L0_032"]["reason"]
    assert changes["f_g"]["plan_crop"] == "recognition/crops/sym_L0_017_ctx.png"
    md = "\n".join(AG.inferred_lines(list(rows.values())))
    # the crop already named in the reason is not repeated; one only in the record is added
    assert md.count("sym_L0_016_ctx.png") == 1
    assert f"a lamp of a nightstand's size; then: {MOVE_TEXT} (plan crop recognition/crops/sym_L0_017_ctx.png) |" in md
    labelled = {i["id"]: i for i in AG.inferred_items(decision_building(), None)}
    assert labelled["f_a"]["plan_crop"] == "recognition/crops/sym_L0_031_ctx.png"
    assert labelled["f_a"]["reason"] == "a lamp of a nightstand's size"           # the code's own record: as before


@pytest.mark.skipif(not (P5 / "furniture" / "real04" / "building_final.json").is_file(),
                    reason="the P5 run folder is not here (runs/ is not committed)")
def test_the_moved_nightstand_retypes_on_the_p5_building():
    b = json.loads((P5 / "furniture" / "real04" / "building_final.json").read_text(encoding="utf-8"))
    rows = {i["id"]: i for i in AG.inferred_items(b, None)}
    for pid, crop in (("f_L0_032", "sym_L0_016"), ("f_L0_034", "sym_L0_018"), ("f_L0_036", "sym_L0_020"),
                      ("f_L0_038", "sym_L0_022")):
        row = rows[pid]
        assert row["decision"] == "code_retype" and row["reason"].startswith("nightstand: a drawn floor_lamp")
        assert "; then: " in row["reason"] and row["plan_crop"] == f"recognition/crops/{crop}_ctx.png"
        assert row["by"] == "code, then Qwen/Qwen3.8-27B-FP8" and row["rule"] == "nightstand_symbol"
    assert rows["f_L0_031"]["reason"].startswith("nightstand:") and "; then:" not in rows["f_L0_031"]["reason"]
    assert rows["f_L0_031"]["plan_crop"] == "recognition/crops/sym_L0_015_ctx.png"


def test_a_bath_or_shower_shrunk_across_its_depth_is_a_wet_shrink():
    """Review finding: only the longest sides were compared (a 1.70 x 0.78 m bath in a 0.75 m deep bay)."""
    from wenart.ingest.generic import reading as R

    assert R.bay_product("bathtub", (1.70, 0.78), (1.70, 0.75)) == (1.7, 0.75)
    assert R.bay_product("shower", (1.00, 0.83), (1.00, 0.80)) == (1.0, 0.8)

    def wet(ftype, drawn, now):
        return _drawn("f_w", ftype, footprint={"center": [1.0, 1.0], "size": now, "rotation_deg": 0.0},
                      drawn_footprint={"center": [1.0, 1.0], "size": drawn, "rotation_deg": 0.0})

    assert AG.decision_kind(wet("bathtub", [1.70, 0.78], [1.70, 0.75])) == "wet_shrink"
    assert AG.decision_kind(wet("shower", [1.00, 0.83], [1.00, 0.80])) == "wet_shrink"
    assert AG.decision_kind(wet("bathtub", [0.78, 1.70], [1.70, 0.75])) == "wet_shrink"      # either way round
    assert AG.decision_kind(wet("bathtub", [1.70, 0.75], [1.70, 0.75])) is None
    assert AG.decision_kind(wet("bathtub", [1.70, 0.752], [1.70, 0.75])) is None             # rounding
    assert AG.decision_kind(wet("bathtub", [1.68, 0.75], [1.70, 0.75])) is None              # grown, not shrunk
    changes = AG.decision_changes({"furniture": [wet("bathtub", [1.70, 0.78], [1.70, 0.75])]})
    assert [(c["decision"], c["change"], c["labelled"]) for c in changes] == [
        ("wet_shrink", "size 1.70 x 0.78 m -> 1.70 x 0.75 m", False)]


def test_edits_of_a_cut_run_replayed_into_this_building_stay_in_the_section(tmp_path):
    """Review finding: a resumed run on the same building_decor.json replays the cut run's accepted edits; the
    section left them out as "earlier runs"."""
    from wenart.agent import overrides as OV

    out = tmp_path / "toy"
    write_appended(out)
    (out / "building_decor.json").write_text(json.dumps({"furniture": []}), encoding="utf-8")
    sha = OV.source_sha(out)
    edits = [{"seq": 1, "round": 1, "tool": "move_piece", "args": {"piece_id": "f_old"}, "source_sha": sha,
              "result": {"accepted": True, "log_seq": 3}},                                # replayed: kept
             {"seq": 2, "round": 1, "tool": "report_library_gap", "args": {"type": "stair", "reason": "cut run"},
              "source_sha": sha, "result": {"accepted": True, "log_seq": 2}},             # replayed: kept
             {"seq": 3, "round": 1, "tool": "report_library_gap", "args": {"type": "bed", "reason": "other run"},
              "source_sha": "other", "result": {"accepted": True, "log_seq": 2}},         # another reading: left out
             {"seq": 4, "round": 1, "tool": "move_piece", "args": {"piece_id": "f_old"}, "source_sha": sha,
              "result": {"accepted": False, "rolled_back": "refit failed", "log_seq": 4}},  # not accepted: left out
             {"seq": 5, "round": 1, "tool": "rotate_piece", "args": {"piece_id": "f_old"}, "source_sha": sha,
              "result": {"accepted": True, "log_seq": 1}},                                # failed its replay: left out
             {"seq": 6, "round": 1, "tool": "report_library_gap", "args": {"type": "chair", "reason": "this run"},
              "source_sha": sha, "result": {"accepted": True, "log_seq": 12}}]
    (out / "orchestrator" / "overrides.json").write_text(json.dumps({"project": "toy", "edits": edits}),
                                                         encoding="utf-8")
    building = {"furniture": [], "agent_overrides": {"not_replayed": [{"seq": 5, "failed_checks": ["no_overlap"]}]}}
    block = AG.agent_block(out, out / "final", building=building)
    assert [g["type"] for g in block["library_gaps"]] == ["stair", "chair"]
    assert [e["seq"] for e in block["edits"]] == [12, 16]                    # this run's accepted edits, as before
    assert [e["seq"] for e in block["replayed"]] == [3] and block["replayed"][0]["target"] == "f_old"
    assert block["earlier"]["edits"] == 3 and block["earlier"]["replayed"] == 2
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "2 accepted edit(s) of an earlier run on the same `building_decor.json` were replayed into this building " \
           "(listed under Replayed edits and the library gaps)" in md
    assert "### Replayed edits of an earlier run on the same building" in md and "| 3 | 1 | move_piece | f_old |" in md
    # no sha now (no building_decor.json): nothing counts as replayed, as before
    scope = AG.run_scope(appended_log(), {"edits": edits}, "")
    assert [e["seq"] for e in scope["edits"]] == [6] and scope["replayed"] == []


def test_the_measured_and_net_rows_come_from_one_finding_key(tmp_path):
    """Review finding: a stored metrics.json written with an older finding key (real02: total 24) sat next to the net
    computed with the current key (gone 27): "24 measured" and "4 new; net 23" contradicted each other."""
    out = tmp_path / "toy"
    write_appended(out)
    log = appended_log()
    log.pop("run_first_seq")
    log.pop("run_first_call")
    (out / "orchestrator" / "log.json").write_text(json.dumps(log), encoding="utf-8")
    from wenart.agent import metrics as AM
    stale = AM.compute(log)
    stale["findings_removed"]["total"] = 5                                   # an older key's count
    (out / "orchestrator" / "metrics.json").write_text(json.dumps(stale), encoding="utf-8")
    block = AG.agent_block(out, out / "final", building={})
    net = block["removed_net"]
    assert block["metrics"]["findings_removed"]["total"] == net["gone"]
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert f"| {net['gone']} measured;" in md and f"{net['new']} new; net {net['net']} |" in md
    assert "| 5 measured;" not in md
    # metrics_lines alone: the net row's own gone count leads
    lines = "\n".join(AG.metrics_lines(stale, net, None))
    assert f"| {net['gone']} measured;" in lines


P4A = ROOT / "runs" / "20261017-072801-full" / "results"


@pytest.mark.skipif(not (P4A / "agent" / "real02" / "log.json").is_file(),
                    reason="the P4a run folder is not here (runs/ is not committed)")
def test_the_measured_and_net_rows_agree_on_the_p4a_results(tmp_path):
    p4a = P4A
    out = tmp_path / "real02"
    out.mkdir()
    os.symlink(p4a / "agent" / "real02", out / "orchestrator")
    os.symlink(p4a / "run" / "real02", out / "run")
    for name in ("building_final.json", "building_decor.json"):
        os.symlink(p4a / "furniture" / "real02" / name, out / name)
    block = AG.agent_block(out, tmp_path / "final", private=True)
    net = block["removed_net"]
    assert (net["gone"], net["new"], net["net"]) == (27, 4, 23)
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "| 27 measured; " in md and "| 4 new; net 23 |" in md                # was "24 measured" next to "net 23"


def test_the_agent_mark_follows_the_reading_reason_of_a_piece_not_built():
    """Review finding: P5 f_L1_017/018 read "untyped" in the recognition table; the agent's later mark (a rug
    outline, round 3) was hidden."""
    f = _drawn("f_L1_017", "unknown", type_method="none", type_candidates=_cand("sofa", "rug"), build=False,
               not_built_reason="untyped (CLAUDE.md: no untyped piece is built)",
               adjusted_by_ai={"reason": "a decorative rug/area outline", "model": "Qwen/Qwen3.8-27B-FP8", "round": 3,
                               "not_furniture": "other"})
    assert F.not_built_text(f) == ("untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) "
                                   "by Qwen/Qwen3.8-27B-FP8, round 3: a decorative rug/area outline")
    g = dict(f, not_built_reason=None, inferred_reason="drawn on the 'A-BA' layer(s): structure")
    assert F.not_built_text(g).startswith("drawn on the 'A-BA' layer(s): structure; then marked not furniture")
    # an agent record that is no mark (a move) does not replace the reading's reason
    h = dict(f, adjusted_by_ai={"reason": "moved", "model": "m", "round": 1})
    assert F.not_built_text(h) == "untyped (CLAUDE.md: no untyped piece is built)"
    assert F.not_built_text(dict(f, not_built_reason=None)) == (
        "marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 3: a decorative rug/area outline")


@pytest.mark.skipif(not (P5 / "furniture" / "real04" / "building_final.json").is_file(),
                    reason="the P5 run folder is not here (runs/ is not committed)")
def test_the_agent_marks_on_the_p5_building():
    b = json.loads((P5 / "furniture" / "real04" / "building_final.json").read_text(encoding="utf-8"))
    pieces = {f["id"]: f for f in b["furniture"]}
    for pid, rnd in (("f_L1_017", 3), ("f_L1_018", 2)):
        text = F.not_built_text(pieces[pid])
        assert text.startswith("untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by "
                               f"Qwen/Qwen3.8-27B-FP8, round {rnd}: ")


def test_metric_10_counts_a_module_or_parametric_fabric_slot_only_when_a_colour_was_asked(tmp_path):
    """Review finding: a parametric armchair or ottoman (a library gap) always has a fabric key with the default
    fabric; it counted as "colour applied" although the style asks no colour for it."""
    out = make_run(tmp_path)
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    para = {"library": "parametric", "asset_id": "parametric:armchair", "method": "parametric", "licence": "n/a",
            "licence_flag": "none"}
    sofa_l = {"library": "module", "asset_id": "module:sofa_corner:sofa_l", "method": "module", "licence": "n/a",
              "licence_flag": "none", "fabric_colour": "light grey"}
    b["furniture"] += [piece("f_8", "sofa_corner", "r_salon", asset=sofa_l),
                       piece("f_9", "armchair", "r_salon", asset=dict(para)),
                       piece("f_10", "armchair", "r_salon", asset=dict(para), design={"fabric_colour": "ochre"})]
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    sc = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    keys = {"fabric": "fabric_linen", "wood": "wood_veneer_oak_light"}
    sc["objects"] += [obj("furn_f_8", "f_8", "furniture", 9, type="sofa_corner", asset=sofa_l, material_keys=keys),
                      obj("furn_f_9", "f_9", "furniture", 10, type="armchair", asset=para, material_keys=keys),
                      obj("furn_f_10", "f_10", "furniture", 11, type="armchair", asset=para, material_keys=keys)]
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(sc), encoding="utf-8")
    p = MX.metric_10(MX.locate(out))["parts"]
    assert p["fabric_slot"] == ["f_10", "f_8"]
    assert p["no_colour_asked"]["f_9"] == "parametric:armchair" and "f_9" not in p["fabric_slot"]
