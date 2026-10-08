"""``python -m wenart.sheets`` and the ``sheet_region`` questions (docs/milestone10.md §1.5, §1.6a, §3.1 item 2):
exit codes, only the regions neither title nor geometry classified are asked (the fall-through), the request file in
the M7 format, answers from a fake vLLM server through ``wenart.recognition.answers ask`` on the ``<out>/sheets``
folder, the merge rules (AI-only classes stay unverified and are never read), and fake answers written by hand."""
from __future__ import annotations

import json

import jsonschema
import pytest

import wenart.sheets as SH
from _sheets_fixture import write_sheet
from wenart.recognition import answers as A
from wenart.recognition import schemas
from wenart.sheets import __main__ as CLI
from wenart.sheets import question as Q

MODELS = A.load_models()


@pytest.fixture()
def project(tmp_path):
    """The fixture sheet with one untitled drawing (r7) no title or geometry rule classifies."""
    folder = tmp_path / "proj"
    folder.mkdir()
    write_sheet(folder / "sheet.dxf", detail=True)
    return folder


@pytest.fixture()
def decided(tmp_path):
    """The fixture sheet: title or geometry decides every region."""
    folder = tmp_path / "decided"
    folder.mkdir()
    write_sheet(folder / "sheet.dxf")
    return folder


def test_schema_is_strict_and_grammar_safe():
    jsonschema.Draft202012Validator.check_schema(Q.SCHEMA)
    grammar = dict(Q.SCHEMA)
    grammar.pop("$schema")
    assert schemas.grammar_problems(grammar) == []
    ok = {"class": "section", "level_word": None, "variant_word": None, "confidence": 0.8, "reason": "slabs"}
    assert A.valid_answer("sheet_region", ok)
    assert not A.valid_answer("sheet_region", dict(ok, cls="x"))
    assert not A.valid_answer("sheet_region", dict(ok, **{"class": "plan"}))
    assert A.task_errors("sheet_region", {"class": "section"})


def test_exit_codes(project, tmp_path):
    out = tmp_path / "out"
    assert CLI.main([str(project), "--out", str(out)]) == CLI.EXIT_QUESTIONS
    doc = json.loads((out / "sheets.json").read_text(encoding="utf-8"))
    assert doc["questions"] == 1 and doc["answers"] is None
    requests = A.read_requests(out / "sheets")
    assert len(requests["items"]) == 1 and requests["crop_version"] == Q.CROP_VERSION
    assert requests["items"][0]["context"]["region"] == "r7"
    assert all(it["task"] == "sheet_region" and (out / "sheets" / it["images"][0]).is_file()
               for it in requests["items"])
    report = (out / "sheets_report.md").read_text(encoding="utf-8")
    assert "Only regions whose class neither the title nor the geometry decided are asked" in report
    assert "questions (`sheets/requests.json`) for r7" in report
    assert CLI.main([str(project), "--out", str(out), "--no-ai"]) == CLI.EXIT_OK
    assert CLI.main([str(tmp_path / "missing"), "--out", str(out)]) == CLI.EXIT_USAGE
    empty = tmp_path / "empty"
    empty.mkdir()
    assert CLI.main([str(empty), "--out", str(tmp_path / "empty_out"), "--no-ai"]) == CLI.EXIT_REVIEW
    assert SH.load(tmp_path / "empty_out")["needs_review"][0]["reason"] == SH.NO_PLAN_REASON


def test_decided_regions_ask_nothing(decided, tmp_path):
    # §3.1 item 2 is a fall-through: title, then geometry, then two AI passes. Every region of the fixture sheet is
    # decided by its title or geometry: exit 0 without --no-ai, no question, no model-server start.
    out = tmp_path / "out"
    assert CLI.main([str(decided), "--out", str(out)]) == CLI.EXIT_OK
    doc = SH.load(out)
    assert doc["questions"] == 0 and all(r["class_method"] in ("title", "geometry") for r in doc["regions"])
    assert all(r["ai"] == [] for r in doc["regions"])
    assert not (out / "sheets" / "requests.json").exists()
    # A stale request file of an earlier run is emptied, so nothing waits for answers.
    A.write_requests(out / "sheets", "decided", [{"key": "old", "task": "sheet_region", "page": 1,
                                                  "images": ["crops/old.png"], "context": {},
                                                  "input_sha256": "0" * 64}], crop_version=Q.CROP_VERSION)
    assert CLI.main([str(decided), "--out", str(out)]) == CLI.EXIT_OK
    assert A.read_requests(out / "sheets")["items"] == []


def test_a_plan_without_its_level_word_is_not_asked(tmp_path):
    # Titled as a plan but no level word: the AI could never make it a plan, so it is not asked either.
    folder = tmp_path / "nolevel"
    folder.mkdir()
    write_sheet(folder / "sheet.dxf", titles={"ground": "KAT PLANI"})
    res = SH.run(folder, tmp_path / "out")
    assert res.questions == 0 and res.pending == []
    r2 = next(r for r in res.doc["regions"] if r["id"] == "r2")
    assert r2["class"] == "floor_plan" and r2["class_method"] == "title"


def test_input_hash_is_stable_and_names_the_region(project, tmp_path):
    a = SH.run(project, tmp_path / "a", no_ai=True)
    SH.run(project, tmp_path / "b", no_ai=True)
    ha = [it["input_sha256"] for it in A.read_requests(tmp_path / "a" / "sheets")["items"]]
    hb = [it["input_sha256"] for it in A.read_requests(tmp_path / "b" / "sheets")["items"]]
    assert ha == hb and len(ha) == 1
    assert a.doc["regions"][1]["id"] == "r2"
    assert A.read_requests(tmp_path / "a" / "sheets")["items"][0]["key"] == Q.key_of(a.regions[6])


def test_answers_from_a_fake_server_then_merge(project, tmp_path):
    from fakes.fake_vlm import FakeVLM

    out = tmp_path / "out"
    assert CLI.main([str(project), "--out", str(out)]) == CLI.EXIT_QUESTIONS
    with FakeVLM() as url:
        for key in ("qwen", "glm"):
            assert A.main(["ask", str(out / "sheets"), "--model-key", key, "--server", url]) == 0
    assert A.is_complete(A.load(out / "sheets"))
    assert CLI.main([str(project), "--out", str(out), "--answers", str(out / "sheets")]) == CLI.EXIT_OK
    doc = SH.load(out)
    assert doc["answers"] == str(out / "sheets")
    asked = [r for r in doc["regions"] if r["ai"]]
    assert [r["id"] for r in asked] == ["r7"]
    assert [a["pass"] for a in asked[0]["ai"]] == [1, 2]
    assert asked[0]["ai"][0]["model"] == MODELS["qwen"]["id"] and asked[0]["ai"][1]["model"] == MODELS["glm"]["id"]
    # The fake answers the schema's first class (floor_plan): AI only, so unverified and never read as a plan.
    assert asked[0]["class"] == "floor_plan" and asked[0]["class_method"] == "ai" and asked[0]["use"] == "ignored"
    assert not [c for c in doc["conflicts"] if c["kind"] == "region_class_disagreement"]
    assert doc["regions"][0]["class"] == "title_block" and doc["regions"][5]["class"] == "section"


def _write_answers(rec_dir, items, data_of) -> None:
    for key in A.MODEL_KEYS:
        store = A.AnswerStore.for_model(rec_dir, key, MODELS)
        for it in items:
            store.put(it["key"], {"task": it["task"], "input_sha256": it["input_sha256"], "data": data_of(it, key),
                                  "raw_text": "", "error": None, "attempts": 1, "latency_s": 0.0,
                                  "model": MODELS[key]["id"], "seed": 0, "images": it["images"]}, save=False)
        store.data["fake"] = True
        store.save()


def test_an_ai_only_class_is_unverified_and_never_read(tmp_path):
    import ezdxf

    project = tmp_path / "untitled"
    project.mkdir()
    doc = ezdxf.new("R2013")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()
    for k in range(5):
        msp.add_circle((k * 400.0, 0.0), 120.0)
    doc.saveas(project / "art.dxf")
    out = tmp_path / "out"
    SH.run(project, out, no_ai=True)
    items = A.read_requests(out / "sheets")["items"]
    _write_answers(out / "sheets", items, lambda it, key: {"class": "floor_plan", "level_word": "ZEMİN KAT",
                                                           "variant_word": None, "confidence": 0.7,
                                                           "reason": "rooms"})
    res = SH.run(project, out, answers=out / "sheets")
    r = res.doc["regions"][0]
    assert r["class"] == "floor_plan" and r["class_method"] == "ai" and r["status"] == "unverified"
    assert r["use"] == "ignored" and "AI-only" in r["ignored_reason"]
    assert res.doc["levels"] == [] and res.review == [SH.NO_PLAN_REASON]
    assert [e["pass"] for e in r["evidence"] if e["method"] == "ai"] == [1, 2]


def test_disagreeing_passes_give_no_class(tmp_path, project):
    out = tmp_path / "out"
    SH.run(project, out, no_ai=True)
    items = A.read_requests(out / "sheets")["items"]
    _write_answers(out / "sheets", items, lambda it, key: {"class": "section" if key == "qwen" else "detail",
                                                           "level_word": None, "variant_word": None,
                                                           "confidence": 0.5, "reason": "x"})
    res = SH.run(project, out, answers=out / "sheets")
    r7 = next(r for r in res.doc["regions"] if r["id"] == "r7")
    assert r7["class"] == "other" and r7["class_method"] == "none" and r7["use"] == "ignored"
    assert any("r7: the AI passes disagree (section / detail)" in w for w in res.doc["warnings"])
    assert res.pending == []
