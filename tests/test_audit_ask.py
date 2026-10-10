"""Milestone 12 track B: the audit's vision question (docs/milestone12.md §6.1, ``ask.py``): strict schemas, the
question's facts, the request hash, the answer store (reuse after a cut) with a fake client, the model key."""
import json
from types import SimpleNamespace

import pytest
from PIL import Image

from wenart.assets.audit import ask as A

ITEM = {"id": "abo_x", "type": "bed_double", "kind": "furniture", "source": "abo",
        "title": "Intex Premaire Luchtbed", "bbox_m": [1.52, 2.04, 0.46]}
GOOD = {"is_type": False, "type_guess": "other", "single_object": True, "real_product": True, "indoor": "both",
        "upright": True, "size_plausible": True, "parts_open": False, "styles": [], "quality": 3,
        "front_shown": "unclear", "has_bedding": False, "has_pillows": False, "has_cushions": None, "contact": None}


def test_schemas_are_strict():
    for kind in ("furniture", "decor"):
        s = A.schema(kind)
        assert s["additionalProperties"] is False and set(s["required"]) == set(s["properties"])
        assert "uniqueItems" not in json.dumps(s)                    # vLLM's xgrammar refuses it (M7)
    assert A.valid(GOOD, "furniture")
    assert not A.valid(dict(GOOD, quality=6), "furniture")
    assert not A.valid({k: v for k, v in GOOD.items() if k != "indoor"}, "furniture")
    assert not A.valid(dict(GOOD, extra=1), "furniture")
    assert A.valid({"type_guess": "bed_double"}, "furniture", second=True)
    assert not A.valid({"type_guess": "spaceship"}, "furniture", second=True)
    assert "cushion" in A.schema("decor")["properties"]["type_guess"]["enum"]


def test_the_question_names_the_facts_and_the_scale_reference():
    p = A.prompt(ITEM, [1.52, 2.04, 0.46])
    assert "Intex Premaire Luchtbed" in p and "double bed" in p and "1.52 x 2.04 x 0.46 m" in p
    assert "1.75 m person" in p and "0.45 m seat-height bar" in p
    assert "has_bedding: true when" in p and "contact: null" in p
    p2 = A.prompt2(ITEM)
    assert "Which one of these is it?" in p2 and "Luchtbed" not in p2            # pass 2 is independent of the title


def test_request_hash_follows_the_sheet_pixels_and_the_question():
    a = A.request_item(ITEM, "../sheets/bed_double/abo_x.jpg", "a" * 64, ITEM["bbox_m"], "m12.1")
    b = A.request_item(ITEM, "../sheets/bed_double/abo_x.jpg", "b" * 64, ITEM["bbox_m"], "m12.1")
    c = A.request_item(ITEM, "../sheets/bed_double/abo_x.jpg", "a" * 64, ITEM["bbox_m"], "m12.2")
    assert len({a["input_sha256"], b["input_sha256"], c["input_sha256"]}) == 3
    assert a["key"] == "audit_abo_x" and a["context"]["pass"] == 1


def test_model_keys():
    m = A.model_of("agent")
    assert m.key == "agent" and m.id and m.slug
    assert A.model_of("x", model_id="org/Some-Model-7B").slug == "some-model-7b"
    with pytest.raises(KeyError):
        A.model_of("no_such_key")


def test_dotted_model_keys_name_nested_entries(tmp_path):
    y = tmp_path / "check.yaml"
    y.write_text("models:\n  agent: {id: org/A, slug: a}\n  bakeoff:\n    fp8: {id: org/B-FP8, slug: b-fp8}\n",
                 encoding="utf-8")
    assert A.model_of("bakeoff.fp8", check_yaml=y) == A.Model("bakeoff.fp8", "org/B-FP8", "b-fp8")
    with pytest.raises(KeyError):
        A.model_of("bakeoff", check_yaml=y)


def test_ask_with_a_fake_client_stores_and_reuses(tmp_path):
    audit = tmp_path / "audit"
    sheet = audit / "sheets" / "bed_double" / "abo_x.jpg"
    sheet.parent.mkdir(parents=True)
    Image.new("RGB", (32, 32), (100, 100, 100)).save(sheet)
    mdoc = {"sheets": {"abo_x": "sheets/bed_double/abo_x.jpg"},
            "measures": {"abo_x": {"ok": True, "size": [1.52, 2.04, 0.46], "sheet_sha256": "c" * 64}}}
    doc = A.build_requests([ITEM], mdoc, audit, "m12.1")
    assert len(doc["items"]) == 1
    calls = []

    class Client:
        model = "fake/model"

        def run_schema(self, images, prompt, schema, **kw):
            calls.append(images)
            assert images[0].endswith("abo_x.jpg") and kw["system_prompt"] == A.SYSTEM
            return SimpleNamespace(data=GOOD, raw_text=json.dumps(GOOD), error=None, attempts=1, latency_s=0.1)
    model = A.Model("fake", "fake/model", "fake")
    rc = A.ask(audit, model, "http://x", workers=1, client_factory=lambda m, s: Client(), log=lambda *a: None)
    assert rc == 0 and len(calls) == 1
    assert A.load_answers(audit, model) == {"abo_x": GOOD}
    rc = A.ask(audit, model, "http://x", workers=1, client_factory=lambda m, s: Client(), log=lambda *a: None)
    assert rc == 0 and len(calls) == 1                               # answered: not asked again
    A.build_requests([ITEM], dict(mdoc, measures={"abo_x": dict(mdoc["measures"]["abo_x"], sheet_sha256="d" * 64)}),
                     audit, "m12.1")
    assert A.load_answers(audit, model) == {}                        # a new sheet: the old answer is stale
