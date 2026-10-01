"""CPU tests for wenart.recognition (docs/milestone2.md, section 3).

No GPU, no vLLM, no PaddleOCR here: the modules must import without them. The
tests cover the schemas (accept/reject), prompt/schema consistency, the request
body of the vLLM client, box conversion, the two-pass matching logic, the
metrics on hand-made data, OCR normalisation and Tesseract TSV parsing, the
bake-off page discovery / resumability / summary, and the DWG round-trip
bookkeeping with stand-in converters.
"""
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

from wenart import building as B
from wenart.recognition import bakeoff, detect, metrics, ocr, prompts, schemas, vlm_client

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
HAS_TESSERACT = shutil.which("tesseract") is not None


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------

def test_schema_enums_come_from_building_schema():
    assert "floor_plan" in schemas.PAGE_CLASSES and "photo_of_plan" in schemas.PAGE_CLASSES
    assert set(schemas.FURNITURE_TYPES) == set(B.load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"])
    assert set(schemas.SYMBOL_TYPES) == set(schemas.FURNITURE_TYPES) | {"door", "window"}
    assert set(schemas.TASKS) == {"page_class", "text_items", "symbols", "room_labels"}


def test_page_class_accepts_and_rejects():
    good = {"class": "floor_plan", "level_label_raw": "ZEMİN KAT PLANI", "scale_text": "ÖLÇEK 1/100", "confidence": 0.9}
    assert schemas.is_valid("page_class", good)
    assert schemas.is_valid("page_class", dict(good, level_label_raw=None, scale_text=None))
    assert not schemas.is_valid("page_class", dict(good, **{"class": "plan"}))        # unknown class
    assert not schemas.is_valid("page_class", dict(good, confidence=1.5))             # out of range
    assert not schemas.is_valid("page_class", dict(good, extra="x"))                  # additionalProperties
    missing = dict(good)
    del missing["scale_text"]
    assert not schemas.is_valid("page_class", missing)                                # required


def test_list_schemas_accept_and_reject():
    assert schemas.is_valid("text_items", {"items": [{"text": "SALON", "box": [0, 0, 10, 10]}]})
    assert schemas.is_valid("text_items", {"items": []})
    assert not schemas.is_valid("text_items", [{"text": "SALON", "box": [0, 0, 10, 10]}])     # root must be an object
    assert not schemas.is_valid("text_items", {"items": [{"text": "SALON", "box": [0, 0, 10]}]})  # 3 numbers
    assert not schemas.is_valid("text_items", {"items": [{"text": "SALON", "box": [0, 0, 10, 1001]}]})  # > 1000

    sym = {"type": "sofa", "box": [100, 100, 300, 180], "rotation_deg": 90, "confidence": 0.8}
    assert schemas.is_valid("symbols", {"items": [sym, dict(sym, type="door", rotation_deg=None)]})
    assert not schemas.is_valid("symbols", {"items": [dict(sym, type="couch")]})
    assert not schemas.is_valid("symbols", {"items": [dict(sym, rotation_deg=400)]})
    assert not schemas.is_valid("symbols", {"items": [dict(sym, note="x")]})

    assert schemas.is_valid("room_labels", {"items": [{"label_raw": "YATAK ODASI", "box": [1, 2, 3, 4]}]})
    assert not schemas.is_valid("room_labels", {"items": [{"label": "YATAK ODASI", "box": [1, 2, 3, 4]}]})
    assert schemas.validation_errors("room_labels", {"items": [{"label_raw": 5, "box": [1, 2, 3, 4]}]})


def test_grammar_schema_has_no_dollar_schema():
    g = schemas.grammar_schema("symbols")
    assert "$schema" not in g and g["additionalProperties"] is False
    assert "$schema" in schemas.SYMBOLS  # the original is untouched


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------

@pytest.mark.parametrize("task", schemas.TASKS)
def test_prompt_matches_schema(task):
    text = prompts.prompt_for(task, 2481, 1754)
    assert text.rstrip().endswith("Answer only with JSON.")
    assert "2481 x 1754" in text and str(schemas.BOX_MAX) in text
    schema = schemas.SCHEMAS[task]
    if task == "page_class":
        fields = schema["properties"]
        for value in fields["class"]["enum"]:
            assert value in text
    else:
        fields = schema["properties"]["items"]["items"]["properties"]
        if task == "symbols":
            for value in schemas.SYMBOL_TYPES:
                assert value in text
                assert value in prompts.SYMBOL_HINTS
    for name in fields:
        assert name in text, f"prompt for {task} does not mention field {name}"
    assert "KAT PLANI" in text and "YATAK ODASI" in text  # Turkish vocabulary explained


# --------------------------------------------------------------------------
# vLLM client (no network)
# --------------------------------------------------------------------------

def test_build_request_uses_vllm_structured_outputs():
    schema = schemas.grammar_schema("page_class")
    body = vlm_client.build_request("m", "prompt", "data:image/png;base64,AAAA", schema)
    assert body["structured_outputs"] == {"json": schema}
    assert body["temperature"] == 0.0 and body["seed"] == 0
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert body["messages"][0]["role"] == "system"
    user = body["messages"][1]
    assert user["role"] == "user"
    assert user["content"][0] == {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAAA"}}
    assert user["content"][1] == {"type": "text", "text": "prompt"}
    assert "guided_json" not in json.dumps(body)


def test_encode_image_downscales_and_keeps_original_size():
    data_url, sent, original = vlm_client.encode_image(PROJECTS / "synthetic-02" / "plan_scan.png", max_side=800)
    assert data_url.startswith("data:image/png;base64,")
    assert original == (2481, 1754) and max(sent) == 800
    _, sent_full, _ = vlm_client.encode_image(PROJECTS / "synthetic-02" / "plan_scan.png", max_side=0)
    assert sent_full == (2481, 1754)


def test_boxes_to_pixels_and_parse_answer():
    assert vlm_client.norm1000_to_pixels([100, 500, 200, 1000], 2000, 1000) == [200.0, 500.0, 400.0, 1000.0]
    assert vlm_client.norm1000_to_pixels([200, 1000, 100, 500], 2000, 1000) == [200.0, 500.0, 400.0, 1000.0]  # sorted
    data = {"items": [{"label_raw": "SALON", "box": [0, 0, 500, 500]}]}
    out = vlm_client.boxes_to_pixels(data, 2481, 1754)
    assert out["items"][0]["box"] == [0.0, 0.0, 1240.5, 877.0]
    assert data["items"][0]["box"] == [0, 0, 500, 500]  # input unchanged
    assert vlm_client.parse_answer('```json\n{"a": 1}\n```') == {"a": 1}
    assert vlm_client.server_root("http://127.0.0.1:8000/v1") == "http://127.0.0.1:8000"


def test_client_reports_unreachable_server_without_raising():
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1)
    assert client.health() is False
    assert vlm_client.served_models("http://127.0.0.1:9/v1") == []
    res = client.run_task("page_class", PROJECTS / "synthetic-02" / "plan_scan.png")
    assert res.data is None and res.error and res.attempts == 1
    assert res.page_size == (2481, 1754)


# --------------------------------------------------------------------------
# Two-pass agreement
# --------------------------------------------------------------------------

def _sym(type_, box, conf=0.9, rot=None):
    return {"type": type_, "box": box, "rotation_deg": rot, "confidence": conf}


def test_two_pass_verified_unverified_and_type_clash():
    a = [_sym("sofa", [100, 100, 300, 190], 0.9, 0), _sym("bed_double", [500, 500, 660, 700], 0.8),
         _sym("chair", [900, 900, 945, 945], 0.7)]
    b = [_sym("sofa", [105, 102, 305, 195], 0.6, None), _sym("wardrobe", [500, 500, 660, 700], 0.85),
         _sym("door", [50, 700, 140, 790], 0.9)]
    runs = {"A": a, "B": b}
    out = detect.two_pass("page.png", "A", "B", run=lambda model, page: runs[model], file="plan_scan.png")
    symbols = out["symbols"]
    by_status = {s["status"] for s in symbols}
    assert by_status == {"verified", "unverified"}
    verified = [s for s in symbols if s["status"] == "verified"]
    assert len(verified) == 1 and verified[0]["type"] == "sofa"
    assert verified[0]["confidence"] == 0.6 and verified[0]["rotation_deg"] == 0
    assert {e["pass"] for e in verified[0]["evidence"]} == {1, 2}
    assert {e["model"] for e in verified[0]["evidence"]} == {"A", "B"}
    assert all(e["method"] == "ai" and e["file"] == "plan_scan.png" for e in verified[0]["evidence"])
    clash = [s for s in symbols if len(s["type_candidates"]) == 2]
    assert len(clash) == 1 and set(clash[0]["type_candidates"]) == {"bed_double", "wardrobe"}
    assert clash[0]["status"] == "unverified" and len(clash[0]["evidence"]) == 2
    singles = [s for s in symbols if s["status"] == "unverified" and len(s["evidence"]) == 1]
    assert {(s["type"], s["evidence"][0]["pass"]) for s in singles} == {("chair", 1), ("door", 2)}
    assert len(symbols) == 4


def test_match_proposals_is_one_to_one_and_prefers_high_iou():
    a = [_sym("chair", [0, 0, 10, 10])]
    b = [_sym("chair", [1, 1, 11, 11]), _sym("chair", [0, 0, 10, 10])]
    agreed, clashes, rest_a, rest_b = detect.match_proposals(a, b)
    assert agreed == [(0, 1, 1.0)] and clashes == [] and rest_a == [] and rest_b == [0]
    assert detect.match_proposals([_sym("chair", [0, 0, 10, 10])], [_sym("chair", [20, 20, 30, 30])])[2:] == ([0], [0])


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def test_text_scores_normalise_case_and_decimal_comma():
    s = metrics.text_scores(["salon 24.50 m2", "Yatak Odası", "ZEMIN KAT PLANI", "noise"],
                            ["SALON 24,50 m²", "YATAK ODASI", "ZEMİN KAT PLANI", "MUTFAK"])
    assert (s["tp"], s["fp"], s["fn"]) == (2, 2, 2)      # ZEMIN != ZEMİN on purpose
    assert s["missed"] == ["mutfak", "zemin kat planı"]
    assert s["recall"] == 0.5 and s["precision"] == 0.5
    assert metrics.text_scores([], [])["recall"] == 0.0


def test_symbol_scores_per_type_at_iou():
    truth = [{"type": "sofa", "box": [0, 0, 100, 50]}, {"type": "chair", "box": [200, 200, 220, 220]},
             {"type": "door", "box": [300, 300, 350, 350]}]
    pred = [{"type": "sofa", "box": [5, 2, 105, 52]},        # IoU ~0.87 -> tp
            {"type": "chair", "box": [230, 230, 250, 250]},  # no overlap -> fp, chair fn
            {"type": "window", "box": [300, 300, 350, 350]}]  # right place, wrong type -> fp + door fn
    s = metrics.symbol_scores(pred, truth)
    assert s["overall"]["tp"] == 1 and s["overall"]["fp"] == 2 and s["overall"]["fn"] == 2
    assert s["per_type"]["sofa"]["recall"] == 1.0 and s["per_type"]["chair"]["recall"] == 0.0
    assert s["per_type"]["window"]["fp"] == 1 and s["per_type"]["door"]["fn"] == 1


def test_truth_boxes_mapped_with_the_page_transform_match_pages_json():
    page = [p for p in bakeoff.raster_pages(PROJECTS) if p.slug == "synthetic-02_plan_photo"][0]
    building = json.loads((PROJECTS / "synthetic-02" / "truth" / "building.json").read_text(encoding="utf-8"))
    mapped = metrics.furniture_boxes_from_building(building, "L0", page.truth["transform"]["building_to_page"])
    truth = {s["id"]: s["box"] for s in page.truth["symbols"]}
    assert len(mapped) == 19
    for item in mapped:
        assert max(abs(a - b) for a, b in zip(item["box"], truth[item["id"]])) < 1.0
    perfect = metrics.symbol_scores(mapped, page.truth_symbols())
    assert perfect["overall"]["precision"] == 1.0


def test_page_class_scores_and_level_label_normalisation():
    truth_page = {"class": "floor_plan", "level_label_raw": "ZEMİN KAT PLANI",
                  "texts": [{"text": "ÖLÇEK 1/100", "role": "scale"}]}
    pred = {"class": "floor_plan", "level_label_raw": "Zemin Kat Plani", "scale_text": "ölçek 1/100", "confidence": 1}
    s = metrics.page_class_scores(pred, truth_page)
    assert s["class_correct"] and s["level_label_correct"] and s["scale_text_correct"]
    wrong = metrics.page_class_scores(dict(pred, level_label_raw="1. KAT PLANI", **{"class": "other"}), truth_page)
    assert not wrong["class_correct"] and not wrong["level_label_correct"]
    assert not metrics.page_class_scores(None, truth_page)["class_correct"]
    assert metrics.level_label_matches(None, None) and not metrics.level_label_matches("x", None)


def _fake_page_results():
    return [{
        "project": "p", "file": "scan.png", "page": 1, "kind": "scan",
        "ocr": {"paddleocr": {"all_texts": metrics.precision_recall(8, 2, 2), "room_labels": metrics.precision_recall(4, 0, 1), "latency_s": 0.5},
                "tesseract": {"all_texts": metrics.precision_recall(5, 5, 5), "room_labels": metrics.precision_recall(1, 3, 4), "latency_s": 2.0}},
        "models": {"M1": {"page_class": {"class_correct": True, "level_label_correct": True, "scale_text_correct": False, "pred_class": "floor_plan", "truth_class": "floor_plan"},
                          "room_labels": metrics.precision_recall(5, 1, 0),
                          "symbols": {"per_type": {"sofa": metrics.precision_recall(1, 0, 0), "door": metrics.precision_recall(2, 1, 1)},
                                      "overall": metrics.precision_recall(3, 1, 1)},
                          "latency_s": {"page_class": 2.0, "room_labels": 4.0, "symbols": 9.0}, "errors": {}}},
        "two_pass": {"verified": {"overall": metrics.precision_recall(2, 0, 2)}, "all": {"overall": metrics.precision_recall(3, 2, 1)},
                     "n_verified": 2, "n_unverified": 3},
    }, {
        "project": "p", "file": "photo.jpg", "page": 1, "kind": "photo",
        "ocr": {"paddleocr": {"all_texts": metrics.precision_recall(6, 4, 4), "room_labels": metrics.precision_recall(2, 1, 3), "latency_s": 0.7}},
        "models": {"M1": {"page_class": {"class_correct": False, "level_label_correct": True, "scale_text_correct": True, "pred_class": "other", "truth_class": "floor_plan"},
                          "room_labels": metrics.precision_recall(3, 0, 2),
                          "symbols": {"per_type": {"sofa": metrics.precision_recall(0, 1, 1)}, "overall": metrics.precision_recall(0, 1, 1)},
                          "latency_s": {"page_class": 1.0, "room_labels": 3.0, "symbols": 5.0}, "errors": {"symbols": "timeout"}}},
        "two_pass": None,
    }]


def test_aggregate_and_summarise_on_hand_made_results():
    agg = metrics.aggregate(_fake_page_results())
    m = agg["models"]["M1"]
    assert m["pages"] == 2 and m["page_class_accuracy"] == 0.5 and m["level_label_accuracy"] == 1.0
    assert m["room_labels"]["recall"] == 0.8 and m["symbols"]["tp"] == 3 and m["symbols"]["fn"] == 2
    assert m["symbols_per_type"]["sofa"]["tp"] == 1 and m["symbols_per_type"]["sofa"]["fn"] == 1
    assert m["latency"]["n"] == 6 and m["latency"]["mean_s"] == 4.0 and m["errors"] == 1
    assert agg["ocr"]["paddleocr"]["room_labels"]["tp"] == 6 and agg["ocr"]["tesseract"]["pages"] == 1
    assert agg["two_pass"]["n_verified"] == 2 and agg["two_pass"]["verified"]["precision"] == 1.0
    md = metrics.summarise(_fake_page_results())
    assert "| paddleocr | 2 |" in md and "| M1 | 2 | 50 % | 100 % |" in md
    assert "## Symbols per type" in md and "| door |" in md and "## Two-pass agreement" in md
    assert "## Per page" in md and "photo.jpg" in md
    assert "(no OCR results)" in metrics.summarise([])


# --------------------------------------------------------------------------
# OCR helpers
# --------------------------------------------------------------------------

def test_normalise_text():
    assert ocr.normalise_text("SALON 24,50 m2") == "salon 24.50 m²"
    assert ocr.normalise_text("  ÇOCUK   ODASI ") == "çocuk odası"
    assert ocr.normalise_text("ZEMİN KAT PLANI") == "zemin kat planı"
    assert ocr.normalise_text("3,45") == "3.45" and ocr.normalise_text("a, b") == "a, b"
    assert ocr.normalise_text("| HOL |") == "hol"


def test_parse_tesseract_tsv_merges_words_into_lines():
    tsv = "\n".join([
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext",
        "1\t1\t0\t0\t0\t0\t0\t0\t100\t100\t-1\t",
        "5\t1\t1\t1\t1\t1\t10\t10\t40\t12\t90\tYATAK",
        "5\t1\t1\t1\t1\t2\t55\t11\t40\t11\t80\tODASI",
        "5\t1\t2\t1\t1\t1\t200\t200\t30\t10\t95\t3,45",
        "5\t1\t2\t1\t1\t2\t240\t200\t5\t10\t-1\t",
    ])
    items = ocr.parse_tesseract_tsv(tsv)
    assert [i["text"] for i in items] == ["YATAK ODASI", "3,45"]
    assert items[0]["box"] == [10.0, 10.0, 95.0, 22.0] and items[0]["confidence"] == 0.85
    assert items[0]["text_norm"] == "yatak odası" and items[1]["text_norm"] == "3.45"
    assert items[0]["engine"] == "tesseract"
    assert ocr.parse_tesseract_tsv("") == []


def test_paddle_items_from_result_dict():
    res = {"rec_texts": ["SALON", "", "4,50"], "rec_scores": [0.99, 0.1, 0.9],
           "rec_boxes": [[10, 10, 60, 25], [0, 0, 1, 1], [100, 100, 130, 115]]}
    items = ocr.paddle_items_from_result(res)
    assert [i["text"] for i in items] == ["SALON", "4,50"] and items[1]["box"] == [100.0, 100.0, 130.0, 115.0]
    polys = {"rec_texts": ["HOL"], "rec_scores": [0.5], "rec_polys": [[[5, 5], [20, 6], [20, 15], [5, 14]]]}
    assert ocr.paddle_items_from_result(polys)[0]["box"] == [5.0, 5.0, 20.0, 15.0]


def test_cross_check_marks_agreement():
    primary = [ocr.make_item("SALON", [0, 0, 50, 20], 0.9, "p"), ocr.make_item("MUTFAK", [100, 0, 160, 20], 0.9, "p")]
    secondary = [ocr.make_item("salon", [1, 1, 51, 21], 0.5, "t"), ocr.make_item("MUTFAX", [100, 0, 160, 20], 0.5, "t")]
    out = ocr.cross_check(primary, secondary)
    assert out[0]["agrees"] and out[0]["cross_text"] == "salon"
    assert not out[1]["agrees"] and out[1]["cross_text"] == "MUTFAX"
    assert "agrees" not in primary[0]


@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract binary not installed")
def test_tesseract_reads_title_and_scale_of_synthetic_scan():
    page = [p for p in bakeoff.raster_pages(PROJECTS) if p.slug == "synthetic-01_1_kat_scan"][0]
    result = ocr.ocr_page(page.image_path, use_paddle=False)
    assert result["primary"] == "tesseract" and "paddle" not in result["errors"]
    texts = {i["text_norm"] for i in result["items"]}
    assert "1. kat planı" in texts and "ölçek 1/100" in texts
    labels = metrics.text_scores([i["text"] for i in result["items"]], page.truth_texts("room_label"))
    assert labels["tp"] >= 1  # Tesseract is the weak cross-check; PaddleOCR is measured on the pod


def test_ocr_page_without_engines_reports_errors_instead_of_raising(monkeypatch):
    monkeypatch.setattr(ocr, "ocr_tesseract", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("no tesseract")))
    result = ocr.ocr_page(PROJECTS / "synthetic-02" / "plan_scan.png", use_paddle=False)
    assert result["items"] == [] and "tesseract" in result["errors"]


# --------------------------------------------------------------------------
# Bake-off CLI pieces
# --------------------------------------------------------------------------

def test_raster_pages_finds_the_three_synthetic_raster_pages():
    pages = bakeoff.raster_pages(PROJECTS)
    assert [p.slug for p in pages] == ["synthetic-01_1_kat_scan", "synthetic-02_plan_scan", "synthetic-02_plan_photo"]
    assert [p.kind for p in pages] == ["scan", "scan", "photo"]
    photo = pages[2]
    assert photo.truth_texts("room_label") == ["SALON", "YATAK ODASI", "MUTFAK", "ANTRE", "BANYO"]
    assert len(photo.truth_symbols()) == 29 and photo.image_path.is_file()
    assert bakeoff.model_slug("Qwen/Qwen3-VL-8B-Instruct") == "Qwen3-VL-8B-Instruct"


class _FakeClient:
    """Answers every task with a fixed, schema-valid payload in page pixels."""
    model = "fake/Model-A"

    def __init__(self, page_truth):
        self.calls = 0
        self.truth = page_truth

    def run_task(self, task, image):
        self.calls += 1
        if task == "page_class":
            data = {"class": self.truth["class"], "level_label_raw": self.truth["level_label_raw"],
                    "scale_text": "ÖLÇEK 1/100", "confidence": 0.9}
        elif task == "room_labels":
            data = {"items": [{"label_raw": t["text"], "box": t["box"]} for t in self.truth["texts"] if t["role"] == "room_label"][:3]}
        else:
            data = {"items": [{"type": s["type"], "box": s["box"], "rotation_deg": None, "confidence": 0.8}
                              for s in self.truth["symbols"][:10]]}
        return vlm_client.VLMResult(task=task, model=self.model, data=data, raw_text=json.dumps(data),
                                    latency_s=0.01, attempts=1, image_size=(1600, 1131), page_size=(2481, 1754))


def test_bakeoff_model_stage_is_resumable_and_scored(tmp_path):
    page = bakeoff.raster_pages(PROJECTS)[1]
    client = _FakeClient(page.truth)
    rec = bakeoff.run_model_page(page, client.model, client, tmp_path, retry_errors=False)
    assert client.calls == 3 and not rec["has_errors"]
    assert rec["scores"]["page_class"]["class_correct"] and rec["scores"]["page_class"]["level_label_correct"]
    assert rec["scores"]["room_labels"]["tp"] == 3 and rec["scores"]["room_labels"]["fn"] == 2
    assert rec["scores"]["symbols"]["overall"]["tp"] == 10 and rec["scores"]["symbols"]["overall"]["precision"] == 1.0
    out_json = tmp_path / "synthetic-02_plan_scan_Model-A.json"
    out_jpg = tmp_path / "synthetic-02_plan_scan_Model-A.jpg"
    assert out_json.is_file() and out_jpg.is_file() and out_jpg.stat().st_size <= bakeoff.DEBUG_MAX_BYTES
    # Second run: skipped, no new calls.
    again = bakeoff.run_model_page(page, client.model, client, tmp_path, retry_errors=False)
    assert client.calls == 3 and again["model"] == client.model
    # A result with errors is re-run only with retry_errors.
    data = json.loads(out_json.read_text(encoding="utf-8"))
    data["has_errors"] = True
    out_json.write_text(json.dumps(data), encoding="utf-8")
    bakeoff.run_model_page(page, client.model, client, tmp_path, retry_errors=False)
    assert client.calls == 3
    bakeoff.run_model_page(page, client.model, client, tmp_path, retry_errors=True)
    assert client.calls == 6


def test_bakeoff_two_pass_and_summary_from_saved_answers(tmp_path):
    pages = bakeoff.raster_pages(PROJECTS)
    page = pages[1]
    client_a = _FakeClient(page.truth)
    client_b = _FakeClient(page.truth)
    client_b.model = "fake/Model-B"
    bakeoff.run_model_page(page, client_a.model, client_a, tmp_path, retry_errors=False)
    bakeoff.run_model_page(page, client_b.model, client_b, tmp_path, retry_errors=False)
    two = bakeoff.run_two_pass_page(page, client_a.model, client_b.model, tmp_path)
    assert two["n_verified"] == 10 and two["n_unverified"] == 0
    assert two["verified"]["overall"]["precision"] == 1.0
    assert bakeoff.run_two_pass_page(pages[0], client_a.model, client_b.model, tmp_path) is None
    agg = bakeoff.write_summary(pages, tmp_path)
    assert set(agg["models"]) == {"fake/Model-A", "fake/Model-B"} and agg["two_pass"]["n_verified"] == 10
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "fake/Model-A" in summary and "synthetic-02_plan_scan" not in summary  # per-page rows use the file name
    assert "plan_scan.png" in summary
    assert (tmp_path / "summary.json").is_file()


@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract binary not installed")
def test_bakeoff_ocr_stage_without_paddle(tmp_path):
    page = bakeoff.raster_pages(PROJECTS)[0]
    rec = bakeoff.run_ocr_page(page, tmp_path, use_paddle=False, use_tesseract=True, device=None, retry_errors=False)
    assert "tesseract" in rec["engines"] and not rec["has_errors"]
    assert rec["engines"]["tesseract"]["scores"]["all_texts"]["tp"] >= 2
    assert (tmp_path / "synthetic-01_1_kat_scan_ocr.json").is_file() and (tmp_path / "synthetic-01_1_kat_scan_ocr.jpg").is_file()
    results = bakeoff.collect_page_results([page], tmp_path)
    assert "tesseract" in results[0]["ocr"] and results[0]["ocr"]["tesseract"]["latency_s"] is not None


def test_main_summary_stage_runs_without_server(tmp_path):
    rc = bakeoff.main(["--projects", str(PROJECTS), "--out", str(tmp_path), "--stage", "summary", "--models", "a/b"])
    assert rc == 0 and (tmp_path / "summary.md").is_file()
    rc = bakeoff.main(["--projects", str(PROJECTS), "--out", str(tmp_path), "--stage", "vlm", "--models", "a/b",
                       "--server", "http://127.0.0.1:9/v1"])
    assert rc == 0  # no server: reported and skipped, nothing invented


def _write_tool(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def test_dwg_roundtrip_bookkeeping_with_stand_in_converters(tmp_path):
    # Stand-ins: "dxf2dwg" copies the DXF (pretending it is a DWG), "dwg2dxf" copies it back.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    copier = 'out=""; for a in "$@"; do [ "$prev" = "-o" ] && out="$a"; prev="$a"; done; cp "${@: -1}" "$out"\n'
    _write_tool(bin_dir / "dxf2dwg", 'if [ "$1" = "--version" ]; then echo "dxf2dwg stand-in 0.0"; exit 0; fi\n' + copier)
    _write_tool(bin_dir / "dwg2dxf", 'if [ "$1" = "--version" ]; then echo "dwg2dxf stand-in 0.0"; exit 0; fi\n' + copier)
    dxfs = sorted(PROJECTS.glob("*/*.dxf"))
    report = bakeoff.dwg_roundtrip(dxfs, tmp_path / "dwg_roundtrip.json", bin_dir, tmp_path / "work")
    assert report["all_ok"] and len(report["files"]) == 2
    first = report["files"][0]
    assert first["counts_in"] == first["counts_back"] and "LWPOLYLINE@DUVAR" in first["counts_in"]
    assert first["dwg_bytes"] > 0 and first["missing"] == {} and first["extra"] == {}
    assert report["dxf2dwg"].startswith("dxf2dwg stand-in")
    # A converter that drops everything is reported, not hidden.
    _write_tool(bin_dir / "dwg2dxf", 'if [ "$1" = "--version" ]; then echo v; exit 0; fi\nexit 3\n')
    report = bakeoff.dwg_roundtrip(dxfs[:1], tmp_path / "dwg_roundtrip2.json", bin_dir, tmp_path / "work2")
    assert not report["all_ok"] and "dwg2dxf failed" in report["files"][0]["error"]
    assert json.loads((tmp_path / "dwg_roundtrip2.json").read_text(encoding="utf-8"))["all_ok"] is False


def test_job_scripts_follow_the_conventions():
    for name in ("scripts/jobs/bakeoff.sh", "scripts/pod_setup_recognition.sh"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert text.startswith("#!/usr/bin/env bash")
        assert "set -Eeuo pipefail" in text and "trap '" in text
        assert "LOGS=$WS/logs" in text and "WS=/workspace" in text
        assert os.access(ROOT / name, os.X_OK)
        assert subprocess.run(["bash", "-n", str(ROOT / name)], capture_output=True).returncode == 0
    job = (ROOT / "scripts/jobs/bakeoff.sh").read_text(encoding="utf-8")
    assert "pytest -m gpu tests/gpu/test_recognition.py" in job and "--stage dwg" in job
    assert "--limit-mm-per-prompt '{\"image\":2}'" in job and "--max-model-len 16384" in job
    assert "--gpu-memory-utilization 0.90" in job and "WENART_RESULTS" in job
