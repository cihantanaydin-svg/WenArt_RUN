"""The AI architect on the pod (wenart/agent/architect_ai.py; user request of 25 Oct 2026): the model picks a choice
per open question, code carries it out and re-asks the questions; only answers that settle their question are kept
(CPU, a scripted model)."""
import json
from pathlib import Path

from wenart.agent import architect_ai as AI
from wenart.agent.model import MockModel
from wenart.blender import architect_actions as AA

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"
PLAY = "r_L1_oyun_aktivite_ve_dinlenme_odasi"


def test_the_ai_answers_are_checked_by_code_and_written_beside_the_building(tmp_path):
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"          # no user answers: the AI gets them all
    (tmp_path / "building_final.json").write_text(json.dumps(b), encoding="utf-8")

    def reply(body):
        text = body["messages"][-1]["content"]
        assert "win_L0_005" in text and "outside_glass_m2" in text               # the element's facts are given
        enum = body["response_format"]["json_schema"]["schema"]["properties"]["answers"]["items"]["properties"]
        assert "ask_user" in enum["choice"]["enum"] and "W2:win_L0_005" in enum["key"]["enum"]
        return {"answers": [
            {"key": "W2:win_L0_005", "choice": "move_window_to_outer_wall", "reason": "the dark bedroom has no window"},
            {"key": f"L1:{PLAY}", "choice": "keep", "reason": "fine"},             # major: keep is refused
            {"key": f"L1:{PLAY}_2", "choice": "enlarge_windows", "reason": "1/25 of the floor is too dark"},
            {"key": "X1:w_L1_005", "choice": "keep", "reason": "a thin wall onto the roof terrace"},
            {"key": "C2:r_L-1_mutfak", "choice": "ask_user", "reason": "the drawing does not say"},
            {"key": "W2:win_L0_006", "choice": "retype_room:storage", "reason": "not a choice of it"}]}

    model = MockModel(critic=[reply])
    rec = AI.answer_open(tmp_path, model, out=lambda s: None)
    by = {e["key"]: e for e in rec["entries"]}
    assert by["W2:win_L0_005"]["verdict"] == "accepted"
    assert by[f"L1:{PLAY}_2"]["verdict"] == "accepted"
    assert by[f"L1:{PLAY}"]["verdict"] == "refused" and "major" in by[f"L1:{PLAY}"]["why"]
    assert by["X1:w_L1_005"]["verdict"] == "accepted"
    assert by["C2:r_L-1_mutfak"]["verdict"] == "ask_user"
    assert by["W2:win_L0_006"]["verdict"] == "refused"
    saved = json.loads((tmp_path / "orchestrator" / "architect_answers.json").read_text(encoding="utf-8"))["answers"]
    assert set(saved) == {"W2:win_L0_005", f"L1:{PLAY}_2", "X1:w_L1_005"}
    assert all(a["by"] == "ai" and a["model"] == "mock/agent" and a["where"] for a in saved.values())
    md = (tmp_path / "orchestrator" / "architect_ai.md").read_text(encoding="utf-8")
    assert "3 answered and carried out" in md
    # the build reads them beside the building (through the build brief); the user's answers win
    both = AA.answers_for_build(tmp_path / "building_final.json", b)
    assert both["W2:win_L0_005"]["by"] == "ai"
    # a second run asks only what is still open and keeps the earlier answers
    model2 = MockModel(critic=[{"answers": []}])
    rec2 = AI.answer_open(tmp_path, model2, out=lambda s: None)
    asked = json.loads(json.dumps(model2.critic_requests()[0]["response_format"]))
    keys = asked["json_schema"]["schema"]["properties"]["answers"]["items"]["properties"]["key"]["enum"]
    assert "W2:win_L0_005" not in keys and rec2["accepted"] == 0
    saved2 = json.loads((tmp_path / "orchestrator" / "architect_answers.json").read_text(encoding="utf-8"))["answers"]
    assert set(saved2) == set(saved)
