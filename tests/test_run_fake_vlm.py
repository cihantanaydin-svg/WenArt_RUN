"""The fake VLM server of the smoke profile (docs/milestone6.md §2.5): minimal schema-valid answers, and the
real clients (vision check, style photos, layout) talking to it."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import jsonschema
import pytest

from fakes.fake_vlm import FakeVLM, minimal_instance, request_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("schema, want", [
    ({"type": "string", "enum": ["b", "a"]}, "b"),
    ({"const": 7}, 7),
    ({"type": "integer", "minimum": 3}, 3),
    ({"type": "integer"}, 0),
    ({"type": "number", "exclusiveMinimum": 0}, 1e-6),
    ({"type": "number", "maximum": -2}, -2),
    ({"type": "string"}, ""),
    ({"type": "string", "minLength": 2}, "xx"),
    ({"type": "boolean"}, False),
    ({"type": ["null", "integer"], "minimum": 1}, 1),
    ({"type": "array", "items": {"type": "integer", "minimum": 2}, "minItems": 2}, [2, 2]),
    ({"type": "array", "items": {"type": "string"}}, []),
    ({"type": "object", "required": ["a"], "properties": {"a": {"enum": ["x"]}, "b": {"type": "string"}}},
     {"a": "x"}),
    ({"anyOf": [{"type": "integer", "minimum": 5}, {"type": "string"}]}, 5),
    ({"$defs": {"w": {"enum": ["image_1", "image_2"]}}, "type": "object", "required": ["winner"],
      "properties": {"winner": {"$ref": "#/$defs/w"}}}, {"winner": "image_1"}),
])
def test_minimal_instances(schema, want):
    got = minimal_instance(schema)
    assert got == want
    jsonschema.Draft202012Validator(schema).validate(got)


def test_request_schema_sources():
    s = {"type": "object"}
    assert request_schema({"structured_outputs": {"json": s}}) is s
    assert request_schema({"response_format": {"type": "json_schema", "json_schema": {"schema": s}}}) is s
    assert request_schema({"guided_json": s}) is s and request_schema({}) is None


def test_endpoints_and_determinism():
    with FakeVLM(models=["m/one", "m/two"]) as url:
        root = url[:-3]
        with urllib.request.urlopen(root + "/health", timeout=5) as resp:
            assert resp.status == 200
        with urllib.request.urlopen(url + "/models", timeout=5) as resp:
            assert [m["id"] for m in json.loads(resp.read())["data"]] == ["m/one", "m/two"]
        body = {"model": "m/two", "messages": [], "structured_outputs": {"json": {
            "type": "object", "required": ["n"], "properties": {"n": {"type": "integer", "minimum": 4}}}}}
        answers = []
        for _ in range(2):
            req = urllib.request.Request(url + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            answers.append(data["choices"][0]["message"]["content"])
            assert data["model"] == "m/two"
        assert answers == ['{"n": 4}', '{"n": 4}']


def test_real_clients_against_the_fake(tmp_path):
    from wenart.furniture import layout as L
    from wenart.style import photos as P
    from wenart.vision_check.config import client_factory, load_config

    models = load_config()["models"]
    with FakeVLM() as url:
        for key in ("qwen", "glm"):
            client = client_factory(key, url)
            result = client.run_schema([ROOT / "tests/fixtures/style_photo_synthetic-03_salon.jpg"], P.photo_prompt(),
                                       P.photo_schema(), task="style_photo")
            assert result.error is None and result.model == models[key]["id"]
            assert set(result.data) == set(P.SLOTS)
        # The style-photo CLI appends a valid pass per model; combine agrees them.
        passes = tmp_path / "passes.json"
        photo = str(ROOT / "tests/fixtures/style_photo_synthetic-03_salon.jpg")
        for key in ("glm", "qwen"):
            assert P.main(["read", photo, "--model-key", key, "--server", url, "--out", str(passes)]) == 0
        data = json.loads(passes.read_text())
        assert {c["model"] for c in data["calls"]} == {models["qwen"]["id"], models["glm"]["id"]}
        assert all(c["error"] is None for c in data["calls"])
        assert P.main(["combine", str(passes), "--out", str(tmp_path / "terms.json")]) == 0
        assert json.loads((tmp_path / "terms.json").read_text())["terms"]
        # The layout client: an empty layout is an answer, not a transport error.
        p = L.LayoutClient(url, model=models["qwen"]["id"], retries=1).propose("prompt", 1)
        assert not p.transport_error and p.data == {"pieces": []}


def test_fake_answers_the_milestone_7_questions(tmp_path):
    """M7 §1.4, §8.2: the recognition questions (symbol_type, room_label) asked by the real
    ``wenart.recognition.answers ask`` CLI, and the realism v2 schema, get schema-valid answers from the fake. Its
    answers are the first enum values (the two passes agree), so the smoke profile runs pipeline_final with
    ``--no-ai`` (the states then never depend on them)."""
    import hashlib

    from PIL import Image

    from wenart.recognition import answers as A
    from wenart.recognition import schemas as RS
    from wenart.vision_check import schemas as VS

    rec = tmp_path / "recognition"
    (rec / "crops").mkdir(parents=True)
    for name in ("sym_L0_001_ctx.png", "sym_L0_001_iso.png", "room_L0_001.png"):
        Image.new("L", (64, 64), 255).save(rec / "crops" / name)
    items = [{"key": "sym_L0_001", "task": "symbol_type", "page": 1,
              "images": ["crops/sym_L0_001_ctx.png", "crops/sym_L0_001_iso.png"], "context": {},
              "input_sha256": hashlib.sha256(b"sym").hexdigest()},
             {"key": "room_L0_001", "task": "room_label", "page": 1, "images": ["crops/room_L0_001.png"],
              "context": {}, "input_sha256": hashlib.sha256(b"room").hexdigest()}]
    A.write_requests(rec, "toy", items)
    with FakeVLM() as url:
        for key in ("glm", "qwen"):
            assert A.main(["ask", str(rec), "--model-key", key, "--server", url, "--workers", "2"]) == 0
    loaded = A.load(rec, items)
    assert A.is_complete(loaded)
    for item in items:
        for key in ("qwen", "glm"):
            data = loaded[item["key"]][key]
            assert not RS.validation_errors(item["task"], data), (item["key"], key, data)
    assert loaded["sym_L0_001"]["qwen"] == loaded["sym_L0_001"]["glm"]   # the fake's passes agree
    for order in ("ab", "ba"):
        schema = VS.realism2_schema(order)
        jsonschema.Draft202012Validator(schema).validate(minimal_instance(schema))


# --------------------------------------------------------------------------
# Schemas vLLM's xgrammar backend refuses (the M7 prep pod: every Objaverse judge call got HTTP 400)
# --------------------------------------------------------------------------

def _post(url: str, schema: dict) -> tuple[int, dict]:
    import urllib.error
    body = {"model": "m/one", "messages": [], "structured_outputs": {"json": schema}}
    req = urllib.request.Request(url + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


UNSUPPORTED = {
    "uniqueItems": {"type": "array", "items": {"enum": ["a", "b"]}, "uniqueItems": True},
    "patternProperties": {"type": "object", "patternProperties": {"^x": {"type": "string"}}},
    "if": {"type": "object", "if": {"required": ["a"]}, "then": {"required": ["b"]}},
    "else": {"type": "object", "else": {"required": ["b"]}},
    "not": {"type": "object", "not": {"required": ["decision"]}},
    "contains": {"type": "array", "contains": {"const": 1}},
    "minContains": {"type": "array", "contains": {"const": 1}, "minContains": 1},
    "maxContains": {"type": "array", "maxContains": 2},
    "dependentRequired": {"type": "object", "dependentRequired": {"a": ["b"]}},
    "propertyNames": {"type": "object", "propertyNames": {"pattern": "^[a-z]+$"}},
}


@pytest.mark.parametrize("keyword", sorted(UNSUPPORTED))
def test_fake_refuses_keywords_xgrammar_does_not_implement(keyword):
    """Every keyword of GRAMMAR_UNSUPPORTED, also deep inside the schema (a property, an anyOf branch, $defs, array
    items), gives vLLM's HTTP 400 "Grammar error: Unimplemented keys: [...]" and no answer."""
    from fakes.fake_vlm import GRAMMAR_UNSUPPORTED
    assert set(UNSUPPORTED) <= set(GRAMMAR_UNSUPPORTED) | {"then"}
    inner = UNSUPPORTED[keyword]
    wrapped = [inner,
               {"type": "object", "required": ["x"], "properties": {"x": inner}},
               {"anyOf": [{"type": "integer"}, inner]},
               {"$defs": {"d": inner}, "type": "object", "properties": {"x": {"$ref": "#/$defs/d"}}},
               {"type": "array", "items": inner},
               {"type": "array", "prefixItems": [{"type": "string"}, inner]}]
    with FakeVLM(models=["m/one"]) as url:
        for schema in wrapped:
            code, data = _post(url, schema)
            assert code == 400, schema
            assert data["error"]["type"] == "BadRequestError" and data["error"]["code"] == 400
            assert data["error"]["message"].startswith("Grammar error: Unimplemented keys: [")
            assert f'"{keyword}"' in data["error"]["message"]


def test_fake_accepts_keyword_names_used_as_property_names_and_lists_every_refused_key():
    """A property *named* "not" or "contains" is no keyword; several refused keywords are all listed, like vLLM."""
    from fakes.fake_vlm import unsupported_keys
    schema = {"type": "object", "required": ["not", "contains"],
              "properties": {"not": {"type": "boolean"}, "contains": {"enum": ["x"]}, "if": {"type": "integer"}}}
    with FakeVLM(models=["m/one"]) as fake_url:
        code, data = _post(fake_url, schema)
    assert code == 200 and json.loads(data["choices"][0]["message"]["content"]) == {"not": False, "contains": "x"}
    both = {"type": "object", "properties": {"a": {"type": "array", "uniqueItems": True, "contains": {"const": 1}}},
            "not": {"required": ["b"]}}
    assert unsupported_keys(both) == ["not", "uniqueItems", "contains"]
    with FakeVLM(models=["m/one"]) as fake_url:
        code, data = _post(fake_url, both)
    assert code == 400 and data["error"]["message"] == 'Grammar error: Unimplemented keys: ["not", "uniqueItems", ' \
                                                      '"contains"]'


def test_the_real_client_gets_the_refusal_as_an_error(tmp_path):
    """wenart.recognition.vlm_client: the 400 is an error with no data (as on the pod), never an answer."""
    from PIL import Image

    from wenart.recognition import vlm_client
    img = tmp_path / "a.png"
    Image.new("L", (32, 32), 255).save(img)
    schema = {"type": "object", "required": ["styles"], "additionalProperties": False,
              "properties": {"styles": {"type": "array", "items": {"enum": ["a", "b"]}, "uniqueItems": True}}}
    with FakeVLM(models=["m/one"]) as url:
        res = vlm_client.VLMClient(url, model="m/one", retries=1).run_schema([img], "styles?", schema, task="t")
        ok = vlm_client.VLMClient(url, model="m/one", retries=1).run_schema(
            [img], "styles?", dict(schema, properties={"styles": {"type": "array", "items": {"enum": ["a", "b"]}}}),
            task="t")
    assert res.data is None and "HTTP 400" in res.error and 'Unimplemented keys: [\\"uniqueItems\\"]' in res.error
    assert ok.error is None and ok.data == {"styles": []}


def test_the_objaverse_judge_cli_gets_answers_from_the_fake(tmp_path):
    """The real ``objaverse judge`` CLI against the fake: its schema must be one vLLM compiles (the prep pod's judge
    failed every call with uniqueItems), so this fails as long as the judge schema uses a refused keyword."""
    from PIL import Image

    from wenart.assets import objaverse as OV
    lib = tmp_path / "library"
    (lib / "judge" / "sheets").mkdir(parents=True)
    Image.new("RGB", (64, 64), (200, 200, 200)).save(lib / "judge" / "sheets" / "u1.jpg")
    item = {"key": "lib_u1", "task": OV.TASK, "images": ["sheets/u1.jpg"], "prompt": "Judge this sofa.",
            "context": {"uid": "u1", "type": "sofa"}, "input_sha256": "a" * 64}
    OV.write_json(lib / "judge" / "requests.json", {"schema_version": "0.1", "kind": "objaverse_judge_requests",
                                                    "task": OV.TASK, "items": [item]})
    with FakeVLM() as url:
        rc = OV.main(["judge", "--out", str(lib), "--model-key", "qwen", "--server", url, "--workers", "1",
                      "--retries", "1"])
    store = OV.judge_store(lib, "qwen")
    rec = store.get("lib_u1") or {}
    assert rc == 0, rec.get("error")
    assert store.valid(item) is not None and OV.valid_judgement(rec["data"])
