"""CPU tests for wenart.recognition (docs/milestone2.md, section 3).

No GPU, no vLLM, no PaddleOCR here: the modules must import without them. The
tests cover the schemas (accept/reject), prompt/schema consistency, the request
body of the vLLM client, box conversion, the two-pass matching logic, the
metrics on hand-made data, OCR normalisation and Tesseract TSV parsing, the
bake-off page discovery / resumability / summary, and the DWG round-trip
bookkeeping with stand-in converters. Milestone 7 (docs/milestone7.md §3.3,
§3.4): the strict ``symbol_type`` / ``room_label`` schemas and their prompts
(the requests, answers and two-pass rule are in tests/test_recognition_answers.py
and tests/test_symbols.py).
"""
import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

from wenart import building as B
from wenart.recognition import bakeoff, detect, metrics, ocr, prompts, schemas, vlm_client

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


def tesseract_has_lang(lang: str, binary: str = "tesseract") -> bool:
    """True when the tesseract ``binary`` exists and ``--list-langs`` names ``lang``.

    ``ocr.ocr_tesseract`` always passes ``-l tur``; a tesseract without the
    language pack exits 1, so the tests must skip, not fail, without it.
    """
    if shutil.which(binary) is None:
        return False
    try:
        proc = subprocess.run([binary, "--list-langs"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    langs = {line.strip() for line in (proc.stdout + proc.stderr).splitlines()}
    return lang in langs


HAS_TESSERACT_TUR = tesseract_has_lang("tur")


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
    for task in schemas.M7_TASKS:
        g = schemas.grammar_schema(task)
        assert "$schema" not in g and g["additionalProperties"] is False
        assert "$schema" in schemas.M7_SCHEMAS[task]


def test_m7_schema_enums_and_tasks():
    """docs/milestone7.md §3.3: every furniture type of the building schema plus not_furniture; the M2 page tasks
    stay as they were."""
    assert schemas.SYMBOL_TYPE_CHOICES == schemas.FURNITURE_TYPES + ("not_furniture",)
    for t in ("stair", "side_table", "floor_lamp", "potted_plant", "unknown"):
        assert t in schemas.SYMBOL_TYPE_CHOICES
    assert "door" not in schemas.SYMBOL_TYPE_CHOICES and "window" not in schemas.SYMBOL_TYPE_CHOICES
    assert schemas.FRONT_CHOICES == ("top", "right", "bottom", "left", "none")
    assert set(schemas.M7_TASKS) == {"symbol_type", "room_label"}
    assert not set(schemas.M7_TASKS) & set(schemas.TASKS)
    assert schemas.SYMBOL_TYPE["properties"]["type"]["enum"] == list(schemas.SYMBOL_TYPE_CHOICES)


def test_m7_symbol_type_schema_is_strict():
    good = {"type": "sofa", "front": "bottom", "confidence": 0.8, "reason": "three seats and a back"}
    assert schemas.is_valid("symbol_type", good)
    assert schemas.is_valid("symbol_type", dict(good, type="not_furniture", front="none", reason=""))
    assert not schemas.is_valid("symbol_type", dict(good, type="couch"))                 # not in the enum
    assert not schemas.is_valid("symbol_type", dict(good, type="door"))                  # openings are not asked
    assert not schemas.is_valid("symbol_type", dict(good, front="up"))
    assert not schemas.is_valid("symbol_type", dict(good, confidence=1.2))
    assert not schemas.is_valid("symbol_type", dict(good, reason="x" * 161))            # <= 160 chars
    assert schemas.is_valid("symbol_type", dict(good, reason="x" * 160))
    assert not schemas.is_valid("symbol_type", dict(good, room="bedroom"))              # additionalProperties
    for name in good:
        missing = dict(good)
        del missing[name]
        assert not schemas.is_valid("symbol_type", missing), name                       # all required
    assert not schemas.is_valid("symbol_type", None)


def test_m7_room_label_schema_is_strict():
    good = {"label": "Bed Room", "size_text": "11' x 10'", "area_text": None, "box": [100, 200, 400, 260]}
    assert schemas.is_valid("room_label", good)
    assert schemas.is_valid("room_label", {"label": None, "size_text": None, "area_text": None, "box": None})
    assert not schemas.is_valid("room_label", dict(good, box=[1, 2, 3]))
    assert not schemas.is_valid("room_label", dict(good, box=[0, 0, 10, 1001]))
    assert not schemas.is_valid("room_label", dict(good, label=5))
    assert not schemas.is_valid("room_label", dict(good, extra="x"))
    missing = dict(good)
    del missing["area_text"]
    assert not schemas.is_valid("room_label", missing)


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


def test_m7_symbol_type_prompt_matches_its_schema():
    text = prompts.m7_prompt("symbol_type")
    assert text.startswith(prompts.SYMBOL_QUESTION)
    assert prompts.SYMBOL_QUESTION == (                                     # docs/milestone7.md §3.3, verbatim
        "Two crops of an architectural floor plan seen from above. The dashed box in the first image (shown alone "
        "in the second, with a 1 m bar) marks one drawn object. Which object type is it?")
    assert text.rstrip().endswith("Answer only with JSON.")
    for value in schemas.SYMBOL_TYPE_CHOICES:
        assert value in text
        assert value in prompts.SYMBOL_HINTS or value == "not_furniture"
    for value in schemas.FRONT_CHOICES:
        assert value in text
    for name in schemas.SYMBOL_TYPE["properties"]:
        assert f"- {name}:" in text, name
    assert str(schemas.REASON_MAX_CHARS) in text
    # Without item facts: the generic text (full type list, vector crops). The question of a real request carries
    # its item's facts (prep pod finding P5, changed on purpose: room, fitting types, neighbours; see below).
    assert prompts.symbol_type_prompt() == text == prompts.symbol_type_prompt(None)
    assert len(prompts.SYMBOL_IMAGE_LABELS) == 2


DINING_CHAIR = {"kind": "vector", "choices": ["chair", "nightstand", "side_table", "floor_lamp", "potted_plant",
                                              "unknown", "not_furniture"],
                "size_m": [0.46, 0.38], "room": {"label": "Dining", "type": "dining"},
                "neighbours": {"similar": 6, "next_to": [1.24, 0.74], "around": 6}}


def _allowed_line(text: str) -> str:
    return next(line for line in text.splitlines() if line.startswith("Allowed values for type:"))


def test_m7_symbol_prompt_carries_the_item_facts():
    """Prep pod P5: the room's documented label and type, only the types whose size range fits the drawn footprint
    (plus unknown and not_furniture), the neighbours; deterministic text, so it can be hashed."""
    text = prompts.symbol_type_prompt(DINING_CHAIR)
    assert text == prompts.symbol_type_prompt(dict(DINING_CHAIR)) == prompts.m7_prompt("symbol_type", DINING_CHAIR)
    assert text.startswith(prompts.SYMBOL_QUESTION) and text.rstrip().endswith("Answer only with JSON.")
    assert 'labelled "Dining"' in text and "dining room" in text
    assert "0.46 x 0.38 m" in text
    assert "one of 6 objects" in text and "1.24 x 0.74 m" in text
    allowed = _allowed_line(text)
    for value in DINING_CHAIR["choices"]:
        assert value in allowed
    for value in ("armchair", "bed_double", "sofa", "tv_unit", "stove"):
        assert value not in allowed and f"- {value}:" not in text
    assert "- not_furniture:" in text and "- unknown:" in text
    # Each fact changes the text (and so the hash).
    assert prompts.symbol_type_prompt(dict(DINING_CHAIR, room={"label": "Kitchen", "type": "kitchen"})) != text
    assert prompts.symbol_type_prompt(dict(DINING_CHAIR, neighbours=None)) != text
    assert prompts.symbol_type_prompt(dict(DINING_CHAIR, choices=["chair", "unknown", "not_furniture"])) != text
    # An unlabelled room says so; no room says nothing about a room.
    bare = prompts.symbol_type_prompt(dict(DINING_CHAIR, room={"label": None, "type": "hall"}, neighbours=None))
    assert "unlabelled room" in bare and "hall or corridor" not in bare      # no guessed type for an unlabelled room
    none = prompts.symbol_type_prompt(dict(DINING_CHAIR, room=None, neighbours=None))
    assert "labelled" not in none and "same size and shape" not in none


def test_m7_symbol_prompt_defines_the_front_and_the_symbols_on_top():
    """Prep pod P5 (c), (e): small symbols drawn on a piece belong to it; the front in image terms, unambiguous."""
    for text in (prompts.symbol_type_prompt(), prompts.symbol_type_prompt(DINING_CHAIR)):
        assert "belong to it" in text and "telephone" in text and "lamp" in text
        assert "opposite the headboard" in text and "opposite the backrest" in text
        assert "edge of the second image" in text
        for side in ("top", "right", "bottom", "left", "none"):
            assert side in text


def test_m7_symbol_prompt_raster_variant():
    """Review raster-7: a raster crop is a pixel copy of the scan: every line is ink and text may appear, so the
    vector wording (grey coding, no text) is never sent with it."""
    vector = prompts.symbol_type_prompt(DINING_CHAIR)
    raster = prompts.symbol_type_prompt(dict(DINING_CHAIR, kind="raster", room=None, neighbours=None))
    assert "mid-grey" in vector and "There is no text in the images." in vector
    assert "mid-grey" not in raster and "light grey" not in raster and "no text" not in raster
    assert "scanned or photographed" in raster and "dark ink" in raster and "ignore" in raster
    assert "1 m long" in raster and "dashed box" in raster
    with pytest.raises(ValueError):
        prompts.symbol_type_prompt(dict(DINING_CHAIR, kind="photo"))


def test_m7_symbol_type_schema_narrows_the_type_enum():
    """The grammar of one item offers exactly the item's choices; stored answers are still checked against the full
    schema (``schemas.SYMBOL_TYPE``)."""
    narrow = schemas.symbol_type_schema(["chair", "unknown", "not_furniture"])
    assert narrow["properties"]["type"]["enum"] == ["chair", "unknown", "not_furniture"]
    assert {k: v for k, v in narrow["properties"].items() if k != "type"} == \
        {k: v for k, v in schemas.SYMBOL_TYPE["properties"].items() if k != "type"}
    assert schemas.symbol_type_schema() == schemas.symbol_type_schema(None) == schemas.SYMBOL_TYPE
    assert schemas.SYMBOL_TYPE["properties"]["type"]["enum"] == list(schemas.SYMBOL_TYPE_CHOICES)    # untouched
    import jsonschema
    good = {"type": "chair", "front": "top", "confidence": 0.7, "reason": "seat and back"}
    jsonschema.validate(good, narrow)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(good, type="armchair"), narrow)
    # The order is the schema's, whatever order the caller gives; unknown names are refused.
    assert schemas.symbol_type_schema(["not_furniture", "chair", "unknown"])["properties"]["type"]["enum"] == \
        ["chair", "unknown", "not_furniture"]
    for bad in (["couch"], [], ["door"]):
        with pytest.raises(ValueError):
            schemas.symbol_type_schema(bad)


def test_m7_room_label_prompt_matches_its_schema():
    text = prompts.m7_prompt("room_label")
    assert text.rstrip().endswith("Answer only with JSON.")
    for name in schemas.ROOM_LABEL["properties"]:
        assert f"- {name}:" in text, name
    assert str(schemas.BOX_MAX) in text and "null" in text and "Do not translate" in text
    assert prompts.room_label_prompt.__code__.co_argcount == 0


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


def _stub_symbol_answer(box_1000, sent_sizes: list) -> callable:
    """A ``post_json`` stand-in: records the size of the image sent and answers one symbol."""
    def post_json(url, body, timeout_s):
        data_url = body["messages"][1]["content"][0]["image_url"]["url"]
        from io import BytesIO
        import base64
        from PIL import Image
        with Image.open(BytesIO(base64.b64decode(data_url.split(",", 1)[1]))) as img:
            sent_sizes.append(img.size)
        answer = {"items": [{"type": "sofa", "box": box_1000, "rotation_deg": None, "confidence": 0.9}]}
        return {"choices": [{"message": {"content": json.dumps(answer)}}], "usage": {}}
    return post_json


def test_run_task_on_a_crop_returns_crop_pixels_and_the_tiled_stage_offsets_them(monkeypatch):
    # The crop-pixel contract the tiled stage relies on (bakeoff.tiled_symbol_items adds the
    # tile origin): for a PIL crop the real client reports page_size = crop size and maps the
    # 0..1000 grid to it, whatever downscale was applied to the image as sent.
    sent = []
    monkeypatch.setattr(vlm_client, "post_json", _stub_symbol_answer([100, 200, 300, 400], sent))
    img = vlm_client.load_image(PROJECTS / "synthetic-01" / "1_kat_scan.png")
    crop = img.crop((880, 633, 1599, 1200))
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1)
    res = client.run_task("symbols", crop)
    assert res.error is None and res.page_size == (719, 567) and res.image_size == (719, 567)
    assert res.data["items"][0]["box"] == [71.9, 113.4, 215.7, 226.8]
    # A tile larger than max_side is downscaled for sending, the boxes stay in crop pixels.
    small = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1, max_side=300)
    res = small.run_task("symbols", crop)
    assert res.image_size == (300, 237) and sent[-1] == (300, 237) and res.page_size == (719, 567)
    assert res.data["items"][0]["box"] == [71.9, 113.4, 215.7, 226.8]
    # Through the tiled stage: the extent of this page is one tile at [880, 633, 1599, 1200].
    run = bakeoff.tiled_symbol_items(PROJECTS / "synthetic-01" / "1_kat_scan.png", client)
    assert run["extent"] == [880, 633, 1599, 1200] and len(run["tiles"]) == 1
    assert run["tiles"][0]["crop_size"] == [719, 567] and run["items"][0]["box"] == [951.9, 746.4, 1095.7, 859.8]
    assert run["items"][0]["edge_clipped"] is False and run["items"][0]["tiles"] == [0]


# --------------------------------------------------------------------------
# vLLM client: several images and caller-made schemas (docs/milestone5.md §1.5)
# --------------------------------------------------------------------------

def test_build_request_with_several_images_and_labels():
    body = vlm_client.build_request("m", "prompt", None, {"type": "object"}, images=["data:a", "data:b"],
                                    labels=["Image 1 (render):", None])
    content = body["messages"][1]["content"]
    assert content == [{"type": "text", "text": "Image 1 (render):"},
                       {"type": "image_url", "image_url": {"url": "data:a"}},
                       {"type": "image_url", "image_url": {"url": "data:b"}},
                       {"type": "text", "text": "prompt"}]
    one = vlm_client.build_request("m", "p", "data:x", {}, labels=["Image 1:"])
    assert [c["type"] for c in one["messages"][1]["content"]] == ["text", "image_url", "text"]
    assert vlm_client.build_request("m", "p", None, {}, images=["data:x"]) == \
        vlm_client.build_request("m", "p", "data:x", {})
    with pytest.raises(ValueError):
        vlm_client.build_request("m", "p", "data:x", {}, images=["data:y"])
    with pytest.raises(ValueError):
        vlm_client.build_request("m", "p", None, {}, images=["data:x", "data:y"], labels=["only one"])


CHECK_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "additionalProperties": False, "required": ["status", "box"],
    "properties": {"status": {"enum": ["present", "absent"]},
                   "box": {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": 1000},
                           "minItems": 4, "maxItems": 4}},
}


def _stub_answers(answers: list, bodies: list) -> callable:
    """A ``post_json`` stand-in: records every body, answers the next text of ``answers``."""
    def post_json(url, body, timeout_s):
        bodies.append(body)
        text = answers[min(len(bodies), len(answers)) - 1]
        return {"choices": [{"message": {"content": text}}], "usage": {"prompt_tokens": 7}}
    return post_json


def _sent_sizes(body: dict) -> list:
    import base64
    from io import BytesIO
    from PIL import Image
    sizes = []
    for part in body["messages"][1]["content"]:
        if part["type"] == "image_url":
            with Image.open(BytesIO(base64.b64decode(part["image_url"]["url"].split(",", 1)[1]))) as img:
                sizes.append(img.size)
    return sizes


def test_run_schema_sends_images_in_order_and_validates_without_box_conversion(monkeypatch):
    bodies = []
    answer = {"status": "present", "box": [100, 200, 300, 400]}
    monkeypatch.setattr(vlm_client, "post_json", _stub_answers([json.dumps(answer)], bodies))
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1, max_side=800)
    page = PROJECTS / "synthetic-02" / "plan_scan.png"
    crop = vlm_client.load_image(page).crop((0, 0, 300, 200))
    res = client.run_schema([page, crop], "Check the elements.", CHECK_SCHEMA, seed=2, task="check",
                            labels=["Image 1 (render):", "Image 2 (plan):"])
    assert res.error is None and res.data == answer                  # boxes stay on the 0..1000 grid
    assert res.task == "check" and res.model == "x" and res.attempts == 1 and res.usage == {"prompt_tokens": 7}
    assert res.image_size == (800, 566) and res.page_size == (2481, 1754)
    body = bodies[0]
    assert body["seed"] == 2 and body["temperature"] == 0.0
    assert body["structured_outputs"] == {"json": vlm_client.grammar_of(CHECK_SCHEMA)}
    assert "$schema" not in body["structured_outputs"]["json"] and "$schema" in CHECK_SCHEMA
    assert body["messages"][0]["content"] == vlm_client.SCHEMA_SYSTEM_PROMPT
    content = body["messages"][1]["content"]
    assert [c["type"] for c in content] == ["text", "image_url", "text", "image_url", "text"]
    assert content[0]["text"] == "Image 1 (render):" and content[2]["text"] == "Image 2 (plan):"
    assert content[-1]["text"] == "Check the elements."
    assert _sent_sizes(body) == [(800, 566), (300, 200)]
    # max_side per call and a custom system prompt.
    client.run_schema([page], "p", CHECK_SCHEMA, max_side=0, system_prompt="sys")
    assert _sent_sizes(bodies[1]) == [(2481, 1754)] and bodies[1]["messages"][0]["content"] == "sys"


def test_run_schema_failures_give_no_data_and_an_error(monkeypatch):
    page = PROJECTS / "synthetic-02" / "plan_scan.png"
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=2, timeout_s=1, max_side=200)
    bodies = []
    monkeypatch.setattr(vlm_client, "post_json",
                        _stub_answers([json.dumps({"status": "maybe", "box": [0, 0, 1, 1]})], bodies))
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.data is None and res.error.startswith("schema: ") and "status" in res.error
    assert res.raw_text and res.attempts == 1
    bodies.clear()
    monkeypatch.setattr(vlm_client, "post_json", _stub_answers(["not json", "still not json"], bodies))
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.data is None and res.error.startswith("bad answer") and res.attempts == 2 and len(bodies) == 2
    bodies.clear()
    monkeypatch.setattr(vlm_client, "post_json", _stub_answers(["null"], bodies))
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.data is None and res.error.startswith("schema: ")
    # A later valid answer after a broken one is used.
    bodies.clear()
    good = json.dumps({"status": "absent", "box": [0, 0, 1000, 1000]})
    monkeypatch.setattr(vlm_client, "post_json", _stub_answers(["oops", good], bodies))
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.error is None and res.data["status"] == "absent" and res.attempts == 2
    # Programming errors raise before any call.
    import jsonschema
    with pytest.raises(jsonschema.exceptions.SchemaError):
        client.run_schema([page], "p", {"type": "no-such-type"})
    with pytest.raises(ValueError):
        client.run_schema([page], "p", CHECK_SCHEMA, labels=["a", "b"])


def test_a_client_deadline_caps_each_request_and_ends_the_retries(monkeypatch):
    """Review G4 (a stuck vision-check call): the check abandons a call still running at WENART_DEADLINE,
    but the HTTP request kept its vLLM slot for up to ``timeout_s`` x ``retries`` (30 min). With
    ``deadline`` (epoch s) each request's timeout is capped to the time left, no pause or retry runs past
    it, and no request starts after it. Without one nothing changes."""
    import time
    page = PROJECTS / "synthetic-02" / "plan_scan.png"
    timeouts = []

    def refused(url, body, timeout_s):
        timeouts.append(timeout_s)
        raise vlm_client.VLMError("connection refused")
    monkeypatch.setattr(vlm_client, "post_json", refused)
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=3, timeout_s=600, max_side=100)
    assert client.deadline is None
    client.deadline = time.time() + 1.0
    t0 = time.monotonic()
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    # One request with at most the 1 s left; the 2 s pause before the retry would pass the deadline.
    assert len(timeouts) == 1 and 0 < timeouts[0] <= 1.0 and time.monotonic() - t0 < 0.9
    assert res.data is None and res.attempts == 1 and "connection refused" in res.error and "deadline" in res.error
    timeouts.clear()
    client.deadline = time.time() - 1.0                       # already past: nothing is sent
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert timeouts == [] and res.attempts == 0 and res.data is None and "deadline" in res.error
    good = json.dumps({"status": "absent", "box": [0, 0, 1000, 1000]})
    bodies = []
    stub = _stub_answers([good], bodies)
    monkeypatch.setattr(vlm_client, "post_json", lambda url, body, timeout_s: (timeouts.append(timeout_s),
                                                                             stub(url, body, timeout_s))[1])
    client.deadline = None
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.error is None and timeouts == [600] and res.attempts == 1
    client.deadline = time.time() + 300.0
    res = client.run_schema([page], "p", CHECK_SCHEMA)
    assert res.error is None and 299.0 < timeouts[-1] <= 300.0


def test_encode_image_is_lossless_without_the_slow_png_optimize_pass(monkeypatch):
    """Review G4: ``optimize=True`` made each 1600x900 image cost 0.6 s of encoding (0.13 s without, file
    5 % larger) for every check call; the PNG stays lossless."""
    import base64
    from io import BytesIO

    import numpy as np
    from PIL import Image
    saved = []
    real_save = Image.Image.save

    def save(self, fp, format=None, **params):
        saved.append(params)
        return real_save(self, fp, format, **params)
    monkeypatch.setattr(Image.Image, "save", save)
    rgb = np.random.default_rng(0).integers(0, 256, (90, 160, 3), dtype=np.uint8)
    data_url, sent, original = vlm_client.encode_image(Image.fromarray(rgb), max_side=0)
    assert sent == original == (160, 90) and saved and not saved[-1].get("optimize")
    with Image.open(BytesIO(base64.b64decode(data_url.split(",", 1)[1]))) as img:
        assert img.format == "PNG" and np.array_equal(np.asarray(img.convert("RGB")), rgb)


def test_run_schema_reports_an_unreachable_server_without_raising():
    client = vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1, max_side=100)
    res = client.run_schema([PROJECTS / "synthetic-02" / "plan_scan.png"], "p", CHECK_SCHEMA)
    assert res.data is None and res.error and res.attempts == 1 and res.page_size == (2481, 1754)
    no_model = vlm_client.VLMClient("http://127.0.0.1:9/v1", retries=1, timeout_s=1)
    res = no_model.run_schema([], "p", CHECK_SCHEMA)
    assert res.data is None and res.model == "?" and "no model served" in res.error


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


def test_two_pass_rotation_disagreement_is_unverified():
    """Same box and type but rotations 0 vs 180: type/box agree, the rotation does not."""
    a = [_sym("bed_double", [500, 500, 660, 700], 0.8, 0), _sym("sofa", [100, 100, 300, 190], 0.9, 90),
         _sym("chair", [900, 900, 945, 945], 0.7, 270)]
    b = [_sym("bed_double", [500, 500, 660, 700], 0.7, 180), _sym("sofa", [100, 100, 300, 190], 0.6, 100),
         _sym("chair", [900, 900, 945, 945], 0.9, None)]
    out = detect.combine(a, b, "A", "B", "plan_scan.png")
    by_type = {s["type"]: s for s in out}
    assert len(out) == 3
    bed = by_type["bed_double"]
    assert bed["status"] == "unverified" and bed["rotation_deg"] is None
    assert bed["rotation_candidates"] == [0, 180] and bed["type_candidates"] == ["bed_double"]
    assert bed["agreement"] == "type_box" and len(bed["evidence"]) == 2
    assert [e.get("rotation_deg") for e in bed["evidence"]] == [0, 180]
    # Within the tolerance (10 degrees apart): verified, pass 1 rotation kept.
    sofa = by_type["sofa"]
    assert sofa["status"] == "verified" and sofa["rotation_deg"] == 90 and "rotation_candidates" not in sofa
    assert sofa["agreement"] == "type_box_rotation"
    # Only one pass gave a rotation: verified, that rotation is used.
    chair = by_type["chair"]
    assert chair["status"] == "verified" and chair["rotation_deg"] == 270
    assert detect.ROTATION_TOL_DEG == 15.0


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


def test_tesseract_gate_needs_the_tur_language_pack(tmp_path):
    """The skip condition reads ``tesseract --list-langs``: eng-only installs skip, not fail."""
    eng_only = _write_tool(tmp_path / "tess-eng", 'echo "List of available languages (2):"; echo eng; echo osd\n')
    with_tur = _write_tool(tmp_path / "tess-tur", 'echo "List of available languages (3):"; echo eng; echo osd; echo tur\n')
    assert not tesseract_has_lang("tur", str(eng_only))
    assert tesseract_has_lang("tur", str(with_tur)) and tesseract_has_lang("eng", str(with_tur))
    assert not tesseract_has_lang("tur", str(tmp_path / "no-such-binary"))


@pytest.mark.skipif(not HAS_TESSERACT_TUR, reason="tesseract with the tur language pack (tesseract-ocr-tur) not installed")
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


class _FailingSymbolsClient(_FakeClient):
    """Like _FakeClient, but the symbols call fails (transport error, data None)."""
    model = "fake/Model-B"

    def run_task(self, task, image):
        if task != "symbols":
            return super().run_task(task, image)
        self.calls += 1
        return vlm_client.VLMResult(task=task, model=self.model, data=None, raw_text="", latency_s=0.01, attempts=1,
                                    error="HTTP 400 Bad Request", image_size=(1600, 1131), page_size=(2481, 1754))


def test_bakeoff_two_pass_with_failed_answer_is_not_computed(tmp_path):
    """A pass that never happened must not produce an agreement score."""
    pages = bakeoff.raster_pages(PROJECTS)
    page = pages[1]
    client_a = _FakeClient(page.truth)
    client_b = _FailingSymbolsClient(page.truth)
    bakeoff.run_model_page(page, client_a.model, client_a, tmp_path, retry_errors=False)
    rec_b = bakeoff.run_model_page(page, client_b.model, client_b, tmp_path, retry_errors=False)
    assert rec_b["has_errors"] and rec_b["tasks"]["symbols"]["data"] is None
    two = bakeoff.run_two_pass_page(page, client_a.model, client_b.model, tmp_path)
    assert two is not None and "fake/Model-B" in two["not_computed"] and "HTTP 400" in two["not_computed"]
    assert "n_verified" not in two and "verified" not in two and two["symbols"] == []
    assert (tmp_path / "synthetic-02_plan_scan_twopass.json").is_file()
    assert not (tmp_path / "synthetic-02_plan_scan_twopass.jpg").exists()
    results = bakeoff.collect_page_results(pages, tmp_path)
    entry = next(r for r in results if r["file"] == page.file)
    assert entry["two_pass"] is None and "fake/Model-B" in entry["two_pass_not_computed"]
    agg = bakeoff.write_summary(pages, tmp_path)
    assert agg["two_pass"] is None                       # no page could be computed
    assert agg["two_pass_not_computed"]["pages"] == 1
    assert agg["two_pass_not_computed"]["reasons"][0]["file"] == page.file
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "not computed" in summary and "fake/Model-B" in summary
    written = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert written["aggregate"]["two_pass_not_computed"]["pages"] == 1


@pytest.mark.skipif(not HAS_TESSERACT_TUR, reason="tesseract with the tur language pack (tesseract-ocr-tur) not installed")
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
    assert report["all_ok"] and len(report["files"]) == len(dxfs) == 6        # synthetic-07 (M10): sheet.dxf
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


def _bash_function_body(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}\(\) \{{\n(.*?)^\}}", text, re.S | re.M)
    assert match, f"function {name} not found"
    return match.group(1)


def test_bakeoff_job_flushes_results_after_every_stage_and_on_exit():
    """A watchdog stop mid-run must not lose the finished stages' results."""
    job = (ROOT / "scripts/jobs/bakeoff.sh").read_text(encoding="utf-8")
    assert "copy_results" in _bash_function_body(job, "run_stage")
    exit_trap = re.search(r"^trap '([^']*)' EXIT", job, re.M)
    assert exit_trap, "no EXIT trap"
    handler = exit_trap.group(1).split()[0]
    assert "copy_results" in _bash_function_body(job, handler)
    # The ERR path exits through the same EXIT trap.
    assert "exit 1" in _bash_function_body(job, "on_error")


def test_pod_setup_stamps_paddle_only_after_a_real_gpu_op():
    """The venv-paddle stamp depends on a kernel launch on gpu:0, not on an import."""
    text = (ROOT / "scripts/pod_setup_recognition.sh").read_text(encoding="utf-8")
    check = re.search(r"^\s*PADDLE_CHECK=\$\(cat <<'PY'\n(.*?)^PY\n\s*\)", text, re.S | re.M)
    assert check, "PADDLE_CHECK python snippet not found"
    snippet = check.group(1)
    compile(snippet, "PADDLE_CHECK", "exec")  # must be valid Python
    assert 'paddle.set_device("gpu:0")' in snippet and "@" in snippet and ".numpy()" in snippet
    assert "import paddleocr" in snippet
    # The stamp is written only when the check passed; the check sees whether a GPU is present.
    stamp = text.index('touch "$VENV_PADDLE/.paddleocr-$PADDLEOCR_VERSION"')
    check_call = text.index('-c "$PADDLE_CHECK"')
    assert check_call < stamp
    assert "no GPU" in snippet or "cpu" in snippet.lower()


# --------------------------------------------------------------------------
# Milestone 3 follow-ups: tiled symbol column, --tiled flag; LibreDWG (0.14 from git since M7, §5.1)
# --------------------------------------------------------------------------

def test_summary_has_a_tiled_symbols_column_that_is_empty_without_the_pass():
    """The ``symbols (tiled)`` column exists for every model; '-' when the pass was not run."""
    plain = _fake_page_results()
    agg = metrics.aggregate(plain)
    assert agg["models"]["M1"]["symbols_tiled"] is None and agg["models"]["M1"]["tiled_pages"] == 0
    md = metrics.summarise(plain)
    assert "Symbols (tiled) R / P" in md
    assert "| M1 | 2 | 50 % | 100 % | 50 % | 80 % / 89 % | 60 % / 60 % | - | 4.0 s | 1 |" in md
    # Tiled results on one page: their own totals, not mixed into the plain symbol scores.
    tiled = _fake_page_results()
    tiled[0]["tiled"] = {"M1": {"symbols": {"per_type": {}, "overall": metrics.precision_recall(4, 0, 1)},
                                "latency_s": {"symbols_tiled": 12.0}, "errors": {}, "n_tiles": 4,
                                "merge": {"n_input": 6, "n_merged": 4, "n_duplicates": 2, "type_conflicts": 0}}}
    agg = metrics.aggregate(tiled)
    m = agg["models"]["M1"]
    assert m["symbols"]["tp"] == 3 and m["symbols_tiled"]["tp"] == 4 and m["symbols_tiled"]["recall"] == 0.8
    assert m["tiled_pages"] == 1 and m["tiled_latency"]["mean_s"] == 12.0 and m["latency"]["n"] == 6
    md = metrics.summarise(tiled)
    assert "| 60 % / 60 % | 80 % / 100 % (1 p, 12.0 s / page) | 4.0 s | 1 |" in md
    assert "| 80 % / 100 % (4 tiles) | floor_plan (ok) | 27.0 s |" in md      # per-page row: plain + tiled latency
    assert "| - | other (wrong) | 9.0 s |" in md                               # the page without a tiled pass


def test_bakeoff_cli_has_the_tiled_flags_and_runs_without_a_server(tmp_path):
    a = bakeoff.parse_args(["--stage", "vlm", "--tiled", "--tile-px", "768", "--tile-overlap", "0.25"])
    assert a.tiled and a.tile_px == 768 and a.tile_overlap == 0.25
    assert not bakeoff.parse_args([]).tiled and bakeoff.parse_args([]).tile_px == 1024
    rc = bakeoff.main(["--projects", str(PROJECTS), "--out", str(tmp_path), "--stage", "vlm", "--tiled",
                       "--models", "a/b", "--server", "http://127.0.0.1:9/v1"])
    assert rc == 0 and not list(tmp_path.glob("*_tiled.json"))   # no server: nothing invented


def test_pod_setup_builds_libredwg_0_14_from_git_static():
    """docs/milestone7.md §5.1: tag 0.14 pinned by commit (no 0.14.1 exists), a static cmake/ninja build on the
    container disk, three programs + VERSION installed into /workspace/tools/libredwg/bin."""
    text = (ROOT / "scripts/pod_setup_recognition.sh").read_text(encoding="utf-8")
    for pin in ("LIBREDWG_GIT=https://github.com/LibreDWG/libredwg.git", "LIBREDWG_TAG=0.14",
                "LIBREDWG_COMMIT=d9468ae948b8f07a08efa756c19f8916052358c0", 'LIBREDWG_VERSION_STRING="0.14 d9468ae p1"',
                "LIBREDWG_BIN=$TOOLS/libredwg/bin", "LIBREDWG_SRC=$FAST/build/libredwg",
                "submodule update --init --depth 1 jsmn", "-G Ninja -DCMAKE_BUILD_TYPE=Release -DDISABLE_WERROR=ON",
                "-DENABLE_LTO=OFF -DBUILD_SHARED_LIBS=OFF", 'ninja -C "$LIBREDWG_SRC/build" dwg2dxf dwgread dxf2dwg',
                '"$LIBREDWG_BIN/dwg2dxf" --help', "build-essential cmake ninja-build git"):
        assert pin in text, pin
    for gone in ("LIBREDWG_VERSION=0.14.1", "LIBREDWG_FALLBACK_VERSION", "ftp.gnu.org", "./configure", "--as "):
        assert gone not in text, gone
    assert 'RECOG_PARTS_ALL="vllm paddle libredwg models"' in text
    assert subprocess.run(["bash", "-n", str(ROOT / "scripts/pod_setup_recognition.sh")], capture_output=True).returncode == 0


def _libredwg_script(tmp_path: Path, body: str, fake_head: str = "") -> subprocess.CompletedProcess:
    """Run ``body`` after the setup script's two LibreDWG functions, with the folders under ``tmp_path`` and fake
    ``git`` (clone makes the folder, ``rev-parse HEAD`` prints ``fake_head``), ``cmake`` (logs its arguments) and
    ``ninja`` (writes three stand-in programs into the build folder)."""
    text = (ROOT / "scripts/pod_setup_recognition.sh").read_text(encoding="utf-8")
    functions = "\n".join(f"{name}() {{\n{_bash_function_body(text, name)}}}"
                          for name in ("libredwg_usable", "patch_libredwg", "build_libredwg"))
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    _write_tool(bin_dir / "git", f"""case "$1" in
  clone) mkdir -p "${{@: -1}}"; echo "$@" > "{tmp_path}/git-clone.txt";;
  -C) case "$3" in rev-parse) echo "$FAKE_HEAD";; esac;;
esac
""")
    _write_tool(bin_dir / "cmake", f'echo "$@" > "{tmp_path}/cmake.txt"\n')
    _write_tool(bin_dir / "ninja", """dir="$2"; mkdir -p "$dir"
for t in dwg2dxf dwgread dxf2dwg; do printf '#!/usr/bin/env bash\\nexit 0\\n' > "$dir/$t"; chmod +x "$dir/$t"; done
""")
    script = "\n".join([
        "set -Eeuo pipefail", f'export PATH="{bin_dir}:$PATH"', f'export FAKE_HEAD="{fake_head}"',
        'log() { echo "log: $*"; }', f'LOGS="{tmp_path}/logs"', 'mkdir -p "$LOGS"',
        "LIBREDWG_GIT=https://github.com/LibreDWG/libredwg.git", "LIBREDWG_TAG=0.14",
        "LIBREDWG_COMMIT=d9468ae948b8f07a08efa756c19f8916052358c0", 'LIBREDWG_VERSION_STRING="0.14 d9468ae p1"',
        f'LIBREDWG_BIN="{tmp_path}/tools/libredwg/bin"', f'LIBREDWG_SRC="{tmp_path}/fast/build/libredwg"',
        functions, body,
    ])
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)


def test_libredwg_is_reused_only_when_complete_pinned_and_working(tmp_path):
    def check(case: str) -> str:
        proc = _libredwg_script(tmp_path / case, 'if libredwg_usable; then echo REUSE; else echo BUILD; fi')
        assert proc.returncode == 0, proc.stderr
        return proc.stdout.strip()

    def install(case: str, version: str = "0.14 d9468ae p1", tools=("dwg2dxf", "dwgread", "dxf2dwg"), rc: int = 0):
        bin_dir = tmp_path / case / "tools" / "libredwg" / "bin"
        bin_dir.mkdir(parents=True)
        for name in tools:
            _write_tool(bin_dir / name, f"exit {rc}\n")
        (bin_dir / "VERSION").write_text(version + "\n", encoding="utf-8")

    assert check("none") == "BUILD"
    install("ok")
    assert check("ok") == "REUSE"
    install("old", version="0.13.3")
    assert check("old") == "BUILD"
    install("broken", rc=127)                                  # dwg2dxf --help does not run
    assert check("broken") == "BUILD"
    install("partial", tools=("dwg2dxf", "dxf2dwg"))           # dwgread missing
    assert check("partial") == "BUILD"


def test_libredwg_build_checks_the_commit_before_installing(tmp_path):
    body = 'if build_libredwg; then echo BUILT; else echo FAILED; fi'
    wrong = _libredwg_script(tmp_path / "wrong", body, fake_head="0123456789abcdef")
    assert wrong.returncode == 0 and wrong.stdout.strip().endswith("FAILED")
    assert "expected d9468ae948b8f07a08efa756c19f8916052358c0: not built" in wrong.stdout
    assert not (tmp_path / "wrong" / "tools").exists() and not (tmp_path / "wrong" / "cmake.txt").exists()
    good = _libredwg_script(tmp_path / "good", body, fake_head="d9468ae948b8f07a08efa756c19f8916052358c0")
    assert good.returncode == 0 and good.stdout.strip() == "BUILT", good.stdout + good.stderr
    clone = (tmp_path / "good" / "git-clone.txt").read_text(encoding="utf-8")
    assert "--depth 1 --branch 0.14 https://github.com/LibreDWG/libredwg.git" in clone
    cmake = (tmp_path / "good" / "cmake.txt").read_text(encoding="utf-8")
    assert "-G Ninja" in cmake and "-DBUILD_SHARED_LIBS=OFF" in cmake and "fast/build/libredwg" in cmake
    bin_dir = tmp_path / "good" / "tools" / "libredwg" / "bin"
    assert sorted(p.name for p in bin_dir.iterdir()) == ["VERSION", "dwg2dxf", "dwgread", "dxf2dwg"]
    assert (bin_dir / "VERSION").read_text(encoding="utf-8") == "0.14 d9468ae p1\n"
