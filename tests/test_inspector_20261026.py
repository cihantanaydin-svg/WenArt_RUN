"""The AI inspector (26 Oct 2026, user: "I need ai models to see understand and fix everything before even I look at
it"): the visitor checks Q1-Q8 the vision critic is asked on every room and exterior view, where their findings go
(a tool, or the stage that owns them), the final round's time share, and the report of what the AI saw (CPU)."""
import json

from wenart.agent import causes as CS
from wenart.agent import critic_vision as CV
from wenart.agent import inspector as INS
from wenart.agent import loop as LP
from wenart.agent import prompts as P


def test_the_vision_critic_is_asked_the_visitor_checks_on_rooms_and_exteriors():
    room = set(CV.LOOK_SCHEMA["properties"]["findings"]["items"]["properties"]["check"]["enum"])
    ext = set(CV.EXTERIOR_SCHEMA["properties"]["findings"]["items"]["properties"]["check"]["enum"])
    assert {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"} <= room and {"Q1", "Q3", "Q7", "Q8"} <= ext
    assert all(P.CHECKLIST[q]["how"] == "V" for q in P.VISITOR_CHECKS)     # never dropped as code-only
    prompt = P.room_look_prompt({"id": "r1", "label": "Mutfak", "room_type": "kitchen", "area_computed": 12.0},
                                [{"id": "f1", "type": "washbasin"}], ["cam_1"], ["render of cam_1"], [],
                                openings=[{"id": "d1", "type": "door", "width": 0.8}])
    assert "d1: door 0.80 m wide" in prompt and "client" in prompt and "Q2" in prompt


def test_visitor_findings_go_to_a_tool_or_to_the_stage_that_owns_them():
    b = {"furniture": [{"id": "f_L0_038", "type": "washbasin", "room_id": "r1"},
                       {"id": "f_L0_017", "type": "table_dining", "room_id": "r1"}], "rooms": [{"id": "r1"}]}

    def cause(check, target, message):
        return CS.cause_of({"check": check, "target": target, "message": message, "source": "vision"}, b)

    assert cause("Q2", "f_L0_038", "the basin rim is at knee height") == "wrong_model"     # swap_model
    assert cause("Q1", "d_L1_001", "a door high in the facade opens onto nothing") == "opening_sense"
    assert CS.REPORT_TO["opening_sense"] == "architect" and CS.CAUSE_TOOLS["opening_sense"] == ()
    assert cause("Q4", "r1", "a kitchen with no counters, sink or hob") == "empty_room"      # place_group
    assert cause("Q4", "f_L0_017", "a dining table in a bedroom") == "wrong_type"
    assert cause("Q5", "f_L0_017", "three tables where one belongs: an extra table") == "wrong_type"
    assert cause("Q6", "f_L0_017", "the cabinet stands in front of the window") == "blocked_opening"
    assert cause("Q8", "building", "a downpipe at every pier") == "rain_water"
    for q in P.VISITOR_CHECKS:
        c = CS.CHECK_CAUSE[q]
        assert CS.CAUSE_TOOLS.get(c) or CS.REPORT_TO.get(c), q          # never silent


def test_the_final_round_needs_time_for_its_own_rerender_only():
    loop = LP.AgentLoop.__new__(LP.AgentLoop)
    loop.deadline, loop.margin_s, loop.clock = 1000.0, 0.0, (lambda: 600.0)
    loop.final_estimate = 700.0
    assert not loop.time_ok() and loop.time_ok(LP.FINAL_ROUND_SHARE)


def test_the_inspector_reports_what_it_saw_fixed_handed_on_and_left(tmp_path):
    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "architect.json").write_text(json.dumps({"questions": [
        {"id": "H1", "topic": "working heights", "severity": "major", "answers": [
            {"element": "f_L1_029", "open": True, "found": "a 0.10 m bowl on the floor"}]}]}), encoding="utf-8")
    findings = {"code": [{"check": "G9", "severity": "major", "target": "r_kitchen", "message": "no sink"}],
                "vision_kept": [
                    {"check": "Q2", "severity": "major", "target": "f_basin", "message": "basin at knee height",
                     "source": "vision", "room_id": "r_bath"},
                    {"check": "Q1", "severity": "critical", "target": "d_up", "message": "a door into the air",
                     "source": "vision", "evidence": {"view": "ext_1"}}],
                "vision_dropped": [{"check": "D2", "severity": "minor", "target": "f_x", "message": "odd",
                                    "dropped": "duplicate of a code finding"}]}
    accepted = [{"tool": "swap_model", "args": {"piece_id": "f_basin"}}]
    rec = INS.report(tmp_path, 4, findings, accepted)
    rows = {r["target"]: r for r in rec["vision"] + rec["code"]}
    assert rows["f_basin"]["outcome"].startswith("fixed")
    assert rows["d_up"]["outcome"].startswith("handed to the architect")
    assert rows["r_kitchen"]["outcome"].startswith("open")
    assert rec["counts"]["architect_open_major"] == 1 and rec["counts"]["dropped"] == 1
    path = INS.write(tmp_path, rec, "p")
    md = path.read_text(encoding="utf-8")
    assert "What the AI inspector saw" in md and "f_L1_029" in md and "d_up" in md
    assert (tmp_path / "orchestrator" / INS.REPORT_JSON).is_file()


def test_the_final_round_takes_a_visitor_major_and_writes_the_inspectors_report(tmp_path):
    """The final round asks every room again (no cached answer), works on a visitor check's major finding (a basin
    at knee height) next to the criticals, and writes orchestrator/inspector.md."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from test_agent_loop_p4a import make
    from test_m13_agent import FINISH

    basin = {"check": "Q2", "severity": "major", "target": "f1", "room_id": "r1",
             "message": "the washbasin's rim is at knee height", "metrics": {}}
    loop, out, model = make(tmp_path, [FINISH], [[basin], []], recheck=lambda b, s, m: [])
    loop.stale_keys = {"room:r1"}
    res = loop.final_round(4)
    assert res["stop"] != "no_finding"                      # the visitor major is the final round's work
    md = (out / "orchestrator" / INS.REPORT_MD).read_text(encoding="utf-8")
    assert "What the AI inspector saw" in md and "knee height" in md


def test_the_model_review_measures_what_the_user_saw_on_the_old_real06_model():
    """26 Oct 2026 (user: "reviewing the 3d model itself could be better"): the review of real06's model of 25 Oct as
    it was built finds every first-look problem, with the element and the number: the doors 0.5 m up, the basins at
    knee height, the upper-floor doors and gaps onto nothing, the empty kitchen, the four dining tables, two window
    models."""
    from pathlib import Path
    from wenart.blender import build as BB
    from wenart.blender import model_review as MR
    from wenart.agent import critic_code as CC
    root = Path(__file__).resolve().parents[1]
    b = json.loads((root / "tests" / "fixtures" / "real06_building_20261025.json").read_text(encoding="utf-8"))
    manifest = {"objects": [
        {"kind": "furniture", "element_id": "f_L0_038", "type": "washbasin", "room_id": "r_L0_banyo",
         "box3d": {"center": [6.22, 12.62, 0.2713], "size": [0.5, 0.4, 0.5426], "rotation_deg": 90.0}},
        {"kind": "furniture", "element_id": "f_L0_031", "type": "toilet", "room_id": "r_L0_banyo",
         "box3d": {"center": [8.05, 12.43, 0.44], "size": [0.45, 0.74, 0.88], "rotation_deg": 270.0}},
        *({"kind": "furniture", "element_id": t, "type": "table_dining", "room_id": "r_L0_salon",
           "box3d": {"center": [5.0, 3.0, 0.395], "size": [0.8, 0.8, 0.79], "rotation_deg": 0.0}}
          for t in ("f_L0_004", "f_L0_017", "f_L0_020", "f_L0_023")),
        {"kind": "window", "element_id": "win_L0_001", "library_model": {"asset_id": "a", "category": "window"}},
        {"kind": "window", "element_id": "win_L0_002", "library_model": {"asset_id": "b", "category": "window"}}]}
    prep = BB.prepare_once(b, "base", None)              # the old build: no architect defaults
    rec = MR.review(prep["building"], manifest, prep)
    got = {(f["check"], f["target"]) for f in rec["findings"]}
    assert ("M1", "d_L0_007") in got                     # the bathroom door 0.5 m up from the bathroom
    assert ("M2", "f_L0_038") in got                     # the basin's top at 0.54 m
    assert ("M4", "d_L1_001") in got and ("M4", "o_L1_006") in got
    assert ("M7", "r_L0_mutfak") in got and ("M7", "f_L0_017") in got
    assert any(f["check"] == "M6" for f in rec["findings"])
    assert "Review of the 3D model" in MR.report_md(rec, "real06")
    # the same building after the architect's defaults: the doors into the air are windows, no M4 is left
    after = BB.prepare(b, "base", None)
    assert not [f for f in MR.review(after["building"], None, after)["findings"] if f["check"] == "M4"]
    # the code critic reads it as its family "model", each finding with a cause and a route
    code = CC.run(b, manifest, None, built=prep["building"], plausibility_fn=lambda b: {}, exterior_fn=lambda *a: {},
                  views_fn=lambda *a: {}, groups_fn=lambda b: {}, levels_fn=lambda *a: [])
    fams = {c["source"]: c["status"] for c in code["checks"]}
    assert fams.get("model") == "ok" and any(f["check"] == "M2" for f in code["findings"])
    for f in code["findings"]:
        if f["check"].startswith("M"):
            c = CS.cause_of(f, b)
            assert CS.CAUSE_TOOLS.get(c) or CS.REPORT_TO.get(c), (f["check"], c)


def test_the_critic_looks_at_a_floor_of_the_model_from_above(tmp_path):
    """26 Oct 2026: the final round's look at the model: a level's top-down view, every room of the floor, targets
    the rooms and their pieces (a claim on an id of another floor is dropped)."""
    from PIL import Image
    from wenart.agent.model import MockModel
    img = tmp_path / "top_L0_plan.jpg"
    Image.new("RGB", (64, 48), (200, 200, 200)).save(img)
    b = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}],
         "rooms": [{"id": "r_kitchen", "level_id": "L0", "room_type": "kitchen", "label": "Mutfak"},
                   {"id": "r_bed", "level_id": "L1", "room_type": "bedroom"}],
         "furniture": [{"id": "f_tab", "room_id": "r_kitchen", "type": "table_dining", "level_id": "L0"}],
         "openings": []}
    reply = {"findings": [
        {"check": "Q4", "severity": "critical", "target": "r_kitchen", "message": "a kitchen with no counters",
         "evidence_image": 1},
        {"check": "Q6", "severity": "major", "target": "r_bed", "message": "a room of another floor",
         "evidence_image": 1}]}
    model = MockModel(critic=[reply])
    res = CV.critique_model_view(model, b, "L0", image=img, code={"findings": []}, call_id="t")
    assert [f["target"] for f in res["kept"]] == ["r_kitchen"] and res["kept"][0]["room_id"] == "r_kitchen"
    assert res["kept"][0]["evidence"]["model_view"] == "L0"
    assert [f["target"] for f in res["dropped"]] == ["r_bed"]
    text = json.dumps(model.critic_requests()[0]["messages"][-1]["content"])
    assert "f_tab table_dining" in text and "ceilings are off" in text
