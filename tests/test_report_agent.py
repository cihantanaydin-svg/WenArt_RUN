"""The "AI orchestrator" section of the final report (docs/milestone11.md §8 "report", §13 step 7): rounds, findings
by check, accepted / rejected / rolled-back edits with reasons, every inferred or AI-changed item, before/after
images copied into final/ (names only for a private project), minutes, and the old-pipeline vs orchestrator table
hook. Without an orchestrator log the report is the M10 one."""
from __future__ import annotations

import json

from test_agent_helpers import jpg, write_json
from test_report import links, make_project
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.report import agent as AG
from wenart.report import final as F


def write_agent_run(out):
    log = LG.AgentLog(out, "toy", "Qwen/Qwen3.8-27B-FP8", "017b", clock=lambda: 1_760_000_000.0)
    img = log.images_dir
    for name in ("r1_001_rotate_before.png", "r1_002_rotate_after.png", "r1_cam_salon_1_before.jpg",
                 "r1_cam_salon_1_after.jpg"):
        jpg(img / name)
    log.event("check", 1, source="code", tool="plausibility", status="ok", counts={"critical": 1})
    log.event("finding", 1, source="code", checklist="F3", severity="critical", target="f1", finding="bed floats")
    log.event("finding", 1, source="vision", checklist="F4", severity="major", target="f2", finding="sofa faces wall",
              model="m", revision="r", call_id="r1-v1")
    log.event("finding", 1, source="vision", checklist="F9", severity="minor", target="f99", finding="ghost",
              dropped="target 'f99' is not an id of what was shown")
    log.event("edit", 1, model="m", tool="rotate_piece", args={"piece_id": "f1", "front_deg": 90}, target="f1",
              validation={"accepted": True, "failed_checks": [], "score_before": 40, "score_after": 75},
              label="adjusted_by_ai", reason="headboard on the wall", before="images/r1_001_rotate_before.png",
              after="images/r1_002_rotate_after.png", rerun_from="refit", checklist="F3")
    log.event("rejected_edit", 1, model="m", tool="move_piece", args={"piece_id": "f2"}, target="f2",
              validation={"accepted": False, "failed_checks": ["door_swing"], "score_before": 60, "score_after": 60},
              reason="closer to the TV")
    log.event("rerun", 1, rerun_from="refit", status="ok", views=["cam_salon_1"])
    log.event("render", 1, views=["cam_salon_1"], before="images/r1_cam_salon_1_before.jpg",
              after="images/r1_cam_salon_1_after.jpg", status="preview")
    log.event("stop", 2, reason="no critical or major finding left", status="no_finding")
    log.call({"call_id": "r1-v1", "kind": "critic", "model": "m", "revision": "r", "seconds": 4.0, "attempts": 1,
              "prompt_tokens": 900, "completion_tokens": 100})
    log.save(final=True)
    ov = OV.Overrides(out, "toy")
    ov.add(1, "rotate_piece", {"piece_id": "f1", "front_deg": 90, "reason": "headboard on the wall"},
           {"accepted": True})
    ov.add(1, "correct_geometry", {"kind": "fix_opening_on_wall", "opening_id": "win2", "evidence": "6 cm",
                                   "reason": "off its wall"}, {"accepted": True, "applied": False})
    ov.add(2, "move_piece", {"piece_id": "f9", "reason": "x"}, {"accepted": False, "rolled_back": "refit failed"})
    write_json(out / "run" / "agent.json", {"stage": "agent", "status": "ok", "seconds": 300.0})
    write_json(out / "run" / "agent_previews.json", {"stage": "agent_previews", "status": "ok", "seconds": 60.0})
    assert LG.validate_log(json.loads((out / "orchestrator" / "log.json").read_text())) == []


def test_agent_block_and_lines(tmp_path):
    out = tmp_path / "toy"
    write_agent_run(out)
    building = {"furniture": [{"id": "f1", "type": "bed_double", "room_id": "r1", "adjusted_by_ai": {
        "reason": "headboard on the wall", "round": 1}}, {"id": "f5", "type": "rug", "inferred": True},
        {"id": "f6", "type": "sofa"}], "rooms": [{"id": "r1", "room_type": "bedroom", "corrected_by_ai": {
            "reason": "gap"}}]}
    block = AG.agent_block(out, out / "final", building=building)
    assert block["model"] == "Qwen/Qwen3.8-27B-FP8" and block["minutes"] == 6.0 and block["tokens"] == 1000
    assert block["rounds"][0]["findings"] == {"critical": 1, "major": 1, "minor": 0}
    assert block["rounds"][0]["dropped"] == 1 and block["rounds"][0]["accepted"] == 1
    assert block["rounds"][0]["rejected"] == 1 and block["rounds"][0]["rerun_from"] == "refit"
    assert block["findings_by_check"]["F9"]["dropped"] == 1
    assert block["edits"][0]["before"] == "agent/r1_001_rotate_before.png"
    assert (out / "final" / "agent" / "r1_002_rotate_after.png").is_file()
    assert block["rejected"][0]["failed_checks"] == ["door_swing"] and block["rolled_back"][0]["seq"] == 3
    kinds = {(i["id"], i["kind"]) for i in block["inferred"]}
    assert kinds == {("f1", "piece"), ("f5", "piece"), ("r1", "room"), ("win2", "geometry")}
    assert block["before_after"][0]["after"] == "agent/r1_cam_salon_1_after.jpg" and block["comparison"] is None
    md = "\n".join(AG.agent_lines({"agent": block}))
    for text in ("## AI orchestrator", "### Rounds", "### Findings by check", "### Accepted edits",
                 "### Rejected edits", "Rolled back", "### Inferred and AI-changed items", "record-only",
                 "### Before and after", "### Old pipeline vs orchestrator", "Not made yet", "40 -> 75"):
        assert text in md, text
    assert AG.agent_lines({"agent": None}) == [] and AG.agent_block(tmp_path / "none", tmp_path) is None


def test_private_projects_keep_the_images_on_the_volume(tmp_path):
    out = tmp_path / "real-01"
    write_agent_run(out)
    block = AG.agent_block(out, out / "final", private=True, building={})
    assert block["edits"][0]["before"] == "orchestrator/images/r1_001_rotate_before.png"
    assert not (out / "final" / "agent").exists()


def test_the_comparison_table(tmp_path):
    out = tmp_path / "toy"
    write_agent_run(out)
    old = tmp_path / "old_final"
    jpg(old / "cam_salon_1_final_preview.jpg", (10, 10, 10))
    jpg(out / "final" / "cam_salon_1_final_preview.jpg")
    data = AG.write_compare(out, old, "pod F1b (M10)")
    assert data["views"] == [{"view": "cam_salon_1", "old": "orchestrator/compare/cam_salon_1_old.jpg",
                              "new": "final/cam_salon_1_final_preview.jpg"}]
    block = AG.agent_block(out, out / "final", building={})
    assert block["comparison"]["views"][0]["old"] == "agent/cam_salon_1_old.jpg"
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "Old run: pod F1b (M10)." in md and "![](agent/cam_salon_1_old.jpg)" in md


def test_the_final_report_has_the_section_only_with_an_orchestrator_log(tmp_path):
    out = make_project(tmp_path)
    manifest = F.write_final(out)
    assert manifest["agent"] is None
    assert "AI orchestrator" not in (out / "final" / "final_report.md").read_text()
    write_agent_run(out)
    manifest = F.write_final(out)
    assert manifest["agent"]["edits"] and F.validate_final_manifest(manifest) == []
    md = (out / "final" / "final_report.md").read_text()
    assert "## AI orchestrator" in md and md.index("## AI orchestrator") < md.index("## Warnings")
    for link in links(md):
        if link.startswith("agent/"):
            assert (out / "final" / link).is_file(), link
