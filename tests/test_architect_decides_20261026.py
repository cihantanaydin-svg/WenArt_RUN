"""The architect decides (user, 26 Oct 2026: "make the AI architect a lot more smart and let it take decisions more"):
every open point that has a chain of safe fixes ends with one (the next fix is tried when one cannot be done or opens
a major point), a refused AI pick is asked again with the reason, and the AI looks at each floor of the model and may
take decisions of its own, which code carries out and keeps only when nothing new breaks (CPU, scripted model)."""
import json
from pathlib import Path

import pytest
from PIL import Image

from wenart.agent import architect_ai as AI
from wenart.agent.model import MockModel
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RU
from wenart.blender import build as BB

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"
PLAY = "r_L1_oyun_aktivite_ve_dinlenme_odasi"


def _real06() -> dict:
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"          # no user answers
    return b


@pytest.fixture(scope="module")
def prep():
    return BB.prepare(_real06(), "base", None)


def _opening(prep, oid):
    return next(o for o in prep["building"]["openings"] if o["id"] == oid)


def test_a_window_that_cannot_move_is_kept_as_a_borrowed_light_window(prep):
    by = {q["id"]: q for q in prep["architect"]["questions"]}
    kitchen = _opening(prep, "win_L0_001")             # kitchen <-> living room, no free outer wall for 1.95 m
    assert kitchen["type"] == "window" and kitchen["interior_glazing"]["kind"] == "clear"
    assert prep["architect_defaults"]["W2:win_L0_001"]["option"] == "interior_glazing"
    shower = _opening(prep, "win_L1_004")              # dressing room <-> shower room: privacy by height
    assert shower["interior_glazing"]["kind"] == "high" and shower["sill_height"] == pytest.approx(AA.HIGH_SILL_M)
    assert shower["drawn_sill_height"] < AA.HIGH_SILL_M
    assert "move_window_to_outer_wall could not be done" in prep["architect_defaults"]["W2:win_L1_004"]["answer"]
    assert not any(a.get("open") for a in by["W2"]["answers"])


def test_the_chain_moves_on_and_never_overrides_the_ai_or_the_user():
    rec = {"questions": [{"id": "W2", "answers": [
        {"element": "w1", "open": True, "default": "move_window_to_outer_wall", "fallback": ["interior_glazing"],
         "options": [AA.option("move_window_to_outer_wall"), AA.option("interior_glazing"), AA.option("keep")]}]}]}
    assert AR.defaults_of(rec, {})["W2:w1"]["option"] == "move_window_to_outer_wall"
    failed = {"W2:w1": {"by": "architect", "choice": "move_window_to_outer_wall"}}
    nxt = AR.defaults_of(rec, failed)["W2:w1"]
    assert nxt["option"] == "interior_glazing" and "could not be done" in nxt["answer"]
    assert AR.defaults_of(rec, {"W2:w1": {"by": "ai", "choice": "keep"}}) == {}
    assert AR.defaults_of(rec, failed, {"W2:w1": ["interior_glazing"]}) == {}       # the chain is spent


def test_a_default_that_opens_a_major_point_is_refused_and_the_next_one_is_tried(monkeypatch):
    """A point with the chain a, b: carrying out ``a`` opens the major point M (a room no door reaches), ``b`` settles
    it with nothing new: the architect keeps ``b`` and reports ``a`` refused."""
    def fake(building_all, variant="base", brief=None, style_family=None):
        defs = building_all.get("architect_defaults") or {}
        choice = (defs.get("F2:d1") or {}).get("choice")
        p = {"element": "d1", "open": choice is None, "default": "a", "fallback": ["b"],
             "options": [dict(AA.option("keep"), id="keep", choice="a"), dict(AA.option("keep"), choice="b")]}
        qs = [{"id": "F2", "severity": "minor", "answers": [p]},
              {"id": "C1", "severity": "major", "answers": [{"element": "r1", "open": choice == "a", "options": []}]}]
        return {"whole": True, "architect": {"questions": qs}, "architect_answers": dict(defs)}

    monkeypatch.setattr(BB, "prepare_once", fake)
    out = BB.prepare({"architect_defaults": {}}, "base", None)
    assert out["architect_defaults"]["F2:d1"]["choice"] == "b"
    assert out["architect_refused_defaults"]["F2:d1"] == {"choice": "a", "opened": ["C1:r1"]}


def test_a_doorway_a_drawn_counter_fills_becomes_a_serving_window():
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}],
         "rooms": [{"id": "k", "level_id": "L0", "room_type": "kitchen", "polygon": [[0, 0], [3, 0], [3, 3], [0, 3]]},
                   {"id": "l", "level_id": "L0", "room_type": "living", "polygon": [[3, 0], [8, 0], [8, 3], [3, 3]]}],
         "walls": [{"id": "w", "level_id": "L0", "start": [3, 0], "end": [3, 3], "thickness": 0.1}],
         "openings": [{"id": "d", "type": "door", "level_id": "L0", "wall_id": "w", "center": [3, 1.5],
                       "width": 1.2, "height": 2.1}],
         "furniture": [{"id": "c", "type": "kitchen_counter", "room_id": "k", "source": "from_documents",
                        "footprint": {"center": [2.7, 1.5], "size": [0.6, 2.4], "rotation_deg": 0.0}},
                       {"id": "s", "type": "sofa", "room_id": "l", "source": "added_by_ai",
                        "footprint": {"center": [5, 1.5], "size": [2, 0.9], "rotation_deg": 0.0}}]}
    plan = AA.Plan(b)
    chain = RU._blocked_chain(plan, "c", b["openings"][0], {"a": "k", "b": "l"}, door=True)
    assert [o["id"] for o in chain] == ["pass_through"]
    assert [o["id"] for o in RU._blocked_chain(plan, "s", b["openings"][0], {"a": "k", "b": "l"}, door=True)] == \
        ["remove_piece"]                                  # a piece the AI added gives way; a drawn one never
    res = AA.apply_answers(b, {"F2:d": {"option": "pass_through", "by": "architect"}})
    o = b["openings"][0]
    assert res[0]["ok"] and o["type"] == "window" and o["drawn_type"] == "door"
    assert o["sill_height"] == pytest.approx(AA.PASS_SILL_M) and o["interior_glazing"]["kind"] == "pass_through"


def test_a_refused_ai_pick_is_asked_again_with_the_reason(tmp_path):
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    (tmp_path / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    key = f"L1:{PLAY}"

    def reply(body):
        enum = body["response_format"]["json_schema"]["schema"]["properties"]["answers"]["items"]["properties"]
        if key not in enum["key"]["enum"]:
            return {"answers": []}
        text = body["messages"][-1]["content"]
        if "tried_and_refused" in text:                  # the retry: the reason is given, keep is gone
            assert "a major question is settled only by a change" in text
            return {"answers": [{"key": key, "choice": "enlarge_windows", "reason": "the room is dark"}]}
        return {"answers": [{"key": key, "choice": "keep", "reason": "it is fine"}]}

    rec = AI.answer_open(tmp_path, MockModel(critic=[reply] * 30), out=lambda s: None)
    e = next(x for x in rec["entries"] if x["key"] == key)
    assert e["verdict"] == "accepted" and [a["choice"] for a in e["attempts"]] == ["keep", "enlarge_windows"]
    assert rec["retried"] >= 1


def test_the_ai_looks_at_each_floor_and_decides(tmp_path):
    b = _real06()
    (tmp_path / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    (tmp_path / "renders").mkdir()
    Image.new("RGB", (64, 48), (200, 200, 200)).save(tmp_path / "renders" / "top_L1_plan.jpg")
    seen = {}

    def reply(body):
        text = json.dumps(body["messages"][-1]["content"])
        level = "L1" if "level L1" in text else "L0"
        seen[level] = ("image_url" in text, "Part B" in text, "E1:d_L1_001" in text)
        if level == "L0":
            return {"answers": [], "decisions": [
                {"action": "door_to_window", "element": "d_L0_004", "value": "", "reason": "a small door"}]}  # an entrance
        return {"answers": [{"key": "E1:d_L1_001", "choice": "french_window", "reason": "a French balcony facade"},
                            {"key": "E1:d_L1_004", "choice": "confirm", "reason": "nothing outside"}],
                "decisions": [{"action": "remove_piece", "element": "f_L1_012", "value": "", "reason": "the bed is too big"},
                              {"action": "retype_room", "element": "r_L1_soyunma_odasi", "value": "closet",
                               "reason": "a walk-in closet off the bedroom"},
                              {"action": "widen_door", "element": "no_such", "value": "", "reason": "a narrow door"}]}

    rec = AI.look(tmp_path, MockModel(critic=[reply] * 10), out=lambda s: None, retries=0)
    assert seen["L1"] == (True, True, True) and seen["L0"][0] is False      # the image of the floor when there is one
    by = {e["key"]: e for e in rec["entries"]}
    assert by["E1:d_L1_001"]["verdict"] == "accepted"                       # the AI's choice wins over the default
    assert by["E1:d_L1_004"]["verdict"] == "confirmed"
    assert by["AI.remove_piece:f_L1_012"]["verdict"] == "refused" and "drawn" in by["AI.remove_piece:f_L1_012"]["why"]
    assert by["AI.door_to_window:d_L0_004"]["verdict"] == "refused" and "entrance" in by["AI.door_to_window:d_L0_004"]["why"]
    assert by["AI.retype_room:r_L1_soyunma_odasi"]["verdict"] == "accepted"
    assert by["AI.widen_door:no_such"]["verdict"] == "refused"
    saved = json.loads((tmp_path / "orchestrator" / "architect_answers.json").read_text(encoding="utf-8"))["answers"]
    assert saved["E1:d_L1_001"]["option"] == "french_window" and saved["E1:d_L1_001"]["by"] == "ai"
    # the build carries them out and the architect's report lists the AI's own decision
    after = BB.prepare(dict(b, agent_overrides={"architect": saved}), "base", None)
    d = next(o for o in after["building"]["openings"] if o["id"] == "d_L1_001")
    assert d.get("guard") and d["type"] != "window"
    a0 = next(q for q in after["architect"]["questions"] if q["id"] == "A0")
    assert any(a["element"] == "r_L1_soyunma_odasi" for a in a0["answers"])
    assert "looks at the model" in (tmp_path / "orchestrator" / AI.LOOK_MD).read_text(encoding="utf-8")


def test_the_critics_read_the_doors_and_windows_as_built():
    """The architect's changes reach the critics: a door the build made a window is no door any more for the room
    checks (real06: "sink blocks door o_L0_004" for a window); the model checks need a build, so a dry re-check
    carries them and never counts them removed."""
    from wenart.agent import critic_code as CC
    from wenart.agent import loop as LP
    b = {"openings": [{"id": "d1", "type": "door"}], "rooms": []}
    built = {"openings": [{"id": "d1", "type": "window", "drawn_type": "door"}]}
    assert CC.with_built_openings(b, built)["openings"][0]["type"] == "window" and b["openings"][0]["type"] == "door"
    assert CC.with_built_openings(b, None) is b
    assert {"M1", "M2", "M7", "M8"} <= LP.NOT_REMEASURED
