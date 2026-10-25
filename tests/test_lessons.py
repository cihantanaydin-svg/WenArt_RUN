"""The user's lessons for the architect (wenart/blender/architect_lessons.py, wenart/agent/lessons.py; user request of
25 Oct 2026: "the architect should ask the questions and corrections I was asking all along the build; use AI to
understand what I was asking and keep developing with the future requests"). CPU, a scripted model."""
import json
import shutil
from pathlib import Path

import pytest

from wenart.agent import lessons as LA
from wenart.agent.model import MockModel
from wenart.blender import architect as AR
from wenart.blender import architect_details as AD
from wenart.blender import architect_lessons as L

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"


def test_every_lesson_is_well_formed_and_its_rules_exist():
    xs = L.lessons()
    assert len(xs) >= 25 and len({x["id"] for x in xs}) == len(xs)
    known = set(AR.ORDER) | {"build"}
    for x in xs:
        assert x["status"] in L.STATUSES and x["area"] in L.AREAS and x["request"] and x["lesson"], x["id"]
        assert set(x.get("checks") or []) <= known, (x["id"], x["checks"])
        assert x["status"] == "process" or x["checks"], x["id"]          # a lesson is checked, or how we work
    # the user's requests of this round are there: taste, decor, groups, pillows, terraces, details, the pool deck
    words = " ".join(x["request"] for x in xs).lower()
    for w in ("taste", "decor", "groups", "pillows", "terrace", "stairs", "making any sense", "clashing"):
        assert w in words, w
    assert {"S2", "S3", "S4", "U1", "D3", "K1", "K2", "K3"} <= {c for x in xs for c in x.get("checks") or []}


def test_the_ai_prompt_and_the_report_carry_the_lessons():
    text = L.prompt_text()
    assert text.startswith("What the user has taught us") and "terrace" in text and "process" not in text
    review = {"questions": [{"id": "F5", "status": "fixed", "counts": {"open": 0}},
                            {"id": "U1", "status": "open", "counts": {"open": 2}}]}
    rows = {r["id"]: r for r in L.status_rows(review)}
    assert rows["UL14"]["result"] == "F5 fixed" and "U1 open (2 open)" in rows["UL20"]["result"]
    md = "\n".join(L.report_md(review))
    assert "## What the user taught me" in md and "| UL14 |" in md
    from wenart.agent import architect_ai as AI
    assert "What the user has taught us" in AI.system_prompt()


def test_a_new_request_becomes_a_lesson_with_or_without_ai(tmp_path):
    path = tmp_path / "lessons.json"
    shutil.copy(L.LESSONS_FILE, path)
    n = len(L.lessons(path))
    raw = LA.add_with_ai("the bathrooms need towels", None, path=path)
    assert raw["id"] == f"UL{n + 1:02d}" and raw["status"] == "open" and raw["lesson"] == "the bathrooms need towels"

    def reply(body):
        enum = body["response_format"]["json_schema"]["schema"]["properties"]["checks"]["items"]["enum"]
        assert "S3" in enum and "the kitchen needs" in body["messages"][-1]["content"]
        return {"lesson": "Every kitchen counter is styled with a few useful objects (a board, a bowl, a plant).",
                "area": "decor", "question": "Is every kitchen counter styled?", "checks": ["S3"]}

    model = MockModel(critic=[reply])
    rec = LA.add_with_ai("the kitchen needs some things on the counter", model, path=path)
    # an answer outside the schema is refused by the model wrapper: the request is kept as it is, open
    bad = LA.add_with_ai("the hall needs a mirror", MockModel(critic=[{"lesson": "x"}] * 2), path=path)
    assert bad["status"] == "open" and bad["lesson"] == "the hall needs a mirror"
    assert rec["status"] == "rule" and rec["checks"] == ["S3"] and rec["area"] == "decor"
    assert [x["id"] for x in L.lessons(path)][-3:] == [raw["id"], rec["id"], bad["id"]]


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_the_ai_checks_the_open_lessons_on_a_building(tmp_path):
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    (tmp_path / "building_final.json").write_text(json.dumps(b), encoding="utf-8")

    def reply(body):
        data = json.loads(body["messages"][-1]["content"])
        ids = [x["id"] for x in data["lessons"]]
        assert data["building"]["rooms"] and "UL16" in ids
        return {"verdicts": [{"lesson": "UL16", "verdict": "issue", "elements": ["r_L-1_salon"],
                              "finding": "a dark walnut table beside light oak"}]}

    rec = LA.review_lessons(tmp_path, MockModel(critic=[reply]), out=lambda s: None)
    assert [v["lesson"] for v in rec["verdicts"]] == ["UL16"]
    md = (tmp_path / "orchestrator" / LA.REVIEW_MD).read_text(encoding="utf-8")
    assert "| UL16 | issue |" in md and "r_L-1_salon" in md


def test_the_rooms_are_checked_as_a_set_styled_and_complete():
    room = {"id": "r", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    pieces = [{"id": "s", "type": "sofa", "room_id": "r", "asset": {"taste": {"wood_tone": "light", "metal": "black"}}},
              {"id": "t", "type": "table_coffee", "room_id": "r", "asset": {"taste": {"wood_tone": "dark"}}},
              {"id": "a", "type": "armchair", "room_id": "r", "asset": {"taste": {"wood_tone": "medium",
                                                                               "metal": "brass"}}}]
    b = {"rooms": [room], "furniture": pieces, "decor": [{"id": "d", "type": "vase", "room_id": "r"}]}
    s2, s3, s4 = AD.styled_rooms(b)
    assert s2["status"] == "open" and "3 wood tones" in s2["answers"][0]["found"] and "2 metal" in s2["answers"][0]["found"]
    assert s3["status"] == "open" and "holds 1 decor" in s3["answers"][0]["found"]
    assert s4["status"] == "open" and "side_table or floor_lamp" in s4["answers"][0]["found"]
    assert "a rug" in s4["answers"][0]["found"]


def test_the_ai_gets_the_checks_evidence_and_the_rooms_facts():
    """25 Oct 2026 pod run: the AI answered "unknown" for 11 of 13 lessons (it saw room names and furniture types
    only). Each lesson now carries what its code checks found, the open findings first, and the rooms their area,
    open-air flag and the models' wood tone and metal."""
    arch = {"questions": [{"id": "U1", "question": "Is the furniture on the terrace made for outside?",
                           "status": "open", "counts": {"ok": 1, "open": 1},
                           "answers": [{"element": "f1", "found": "teak table", "status": "ok"},
                                       {"element": "f2", "found": "an upholstered armchair outside",
                                        "status": "open"}]}]}
    ev = LA.check_evidence(arch, ["U1", "Z9"])
    assert list(ev) == ["U1"] and ev["U1"]["found"][0].startswith("f2: an upholstered armchair")
    b = {"rooms": [{"id": "t", "room_type": "terrace", "level_id": "L1", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}],
         "furniture": [{"id": "f1", "type": "table_dining", "room_id": "t", "source": "added_by_ai",
                        "asset": {"taste": {"wood_tone": "medium", "metal": "black"}}}]}
    room = LA.building_facts(b, arch)["rooms"][0]
    assert room["area_m2"] == 12.0 and room["open_air"] is True
    assert room["furniture"] == [{"id": "f1", "type": "table_dining", "source": "added_by_ai", "wood_tone": "medium",
                                  "metal": "black"}]
