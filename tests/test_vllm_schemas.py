"""Every JSON schema the project sends to vLLM as a structured-output grammar uses only keywords xgrammar implements.

Why: on the M7 prep pod (3 Oct 2026) every Objaverse judge call failed with vLLM HTTP 400 "Grammar error:
Unimplemented keys: ["uniqueItems"]" (the judge schema's ``styles`` list). A schema keyword the grammar backend does
not implement fails every call at once, on the pod, after the servers are paid for. This CPU test walks every schema
the code sends (``structured_outputs.json``) and refuses those keywords before a pod starts.

The keyword rules are ``wenart.recognition.schemas.grammar_problems`` (sources there: vLLM
``vllm/v1/structured_output/backend_xgrammar.py`` ``has_xgrammar_unsupported_json_features`` and xgrammar
``cpp/json_schema_converter.cc`` ``WarnUnsupportedKeywords``, checked 3 Oct 2026). A keyword that is in neither the
refused nor the known-good list is refused too, so a new keyword is checked against xgrammar before it reaches a pod.

The schemas sent to vLLM (``VLMClient.run_schema`` / ``run_task`` / ``build_text_request`` callers):

- recognition: the four Milestone 2 page tasks (``schemas.grammar_schema``), ``symbol_type`` (full list and the
  per-item narrowed enum of ``symbol_type_schema``) and ``room_label`` (``wenart.recognition.answers.call_args``);
- vision check: the per-view schema (``vision_check.calls``), the preference schema, realism v1 and realism v2 (both
  orders);
- furniture layout (``furniture.layout``, text-only calls);
- the Objaverse library judge (``assets.objaverse``);
- the style photo reader (``style.photos``);
- Milestone 10: the ``sheet_region`` question of the sheets stage (asked by ``recognition.answers ask`` in the
  recognition sessions) and the recolour judge (``assets.recolour``: one schema per sheet, ``slot_<n>`` ->
  ``{materials: [...]}``, built from the slot indexes of the sheet).
"""
import copy

import pytest

from wenart.recognition import schemas as RS


def _recognition() -> dict:
    from wenart.recognition import answers as A
    from wenart.recognition import crops as C
    out = {f"recognition/{t}": RS.grammar_schema(t) for t in RS.TASKS + RS.M7_TASKS}
    out["recognition/symbol_type narrowed"] = RS.symbol_type_schema(["chair", "nightstand", "unknown",
                                                                     "not_furniture"])
    # What answers.call_args really sends for a request item that carries its question facts.
    facts = {"kind": "vector", "choices": ["chair", "side_table", "unknown", "not_furniture"], "size_m": [0.46, 0.38]}
    item = {"key": "sym_L0_001", "task": "symbol_type", "images": ["crops/a.png", "crops/b.png"], "question": facts,
            "input_sha256": "0" * 64}
    out["recognition/symbol_type call_args"] = A.call_args(item, ".")["schema"]
    out["recognition/symbol_type digest"] = C.question_digest("symbol_type", facts)["schema"]
    room = {"key": "lbl_L0_1", "task": "room_label", "images": ["crops/lbl_L0_1.png"], "input_sha256": "0" * 64}
    out["recognition/room_label call_args"] = A.call_args(room, ".")["schema"]
    # Milestone 10: the sheet_region question (wenart.sheets.question.SCHEMA), as the answer store sends it.
    sheet = {"key": "sheet_a_s1_r1", "task": "sheet_region", "images": ["crops/sheet_a_s1_r1.png"],
             "input_sha256": "0" * 64}
    out["recognition/sheet_region call_args"] = A.call_args(sheet, ".")["schema"]
    out["recognition/sheet_region task_schema"] = A.task_schema("sheet_region")
    return out


def _vision_check() -> dict:
    from wenart.vision_check import preference
    from wenart.vision_check import schemas as VS
    out = {"vision_check/view": VS.view_schema(["el_1", "el_2", "el_3"]),
           "vision_check/preference": VS.preference_schema(),
           "vision_check/preference module": preference.schema(),
           "vision_check/realism": VS.realism_schema()}
    for order in ("ab", "ba"):
        out[f"vision_check/realism2 {order}"] = VS.realism2_schema(order)
    return out


def _furniture() -> dict:
    from wenart.furniture import schemas as FS
    return {"furniture/layout": FS.grammar_schema()}


def _objaverse() -> dict:
    from wenart.assets import objaverse
    return {"assets/objaverse judge": objaverse.judge_schema()}


def _style() -> dict:
    from wenart.style import photos
    return {"style/photo": photos.photo_schema()}


def _recolour() -> dict:
    """The recolour judge (Milestone 10): ``answer_schema(slot indexes)``, from one slot to the largest sheet, and the
    schema the shared judging asks for a request item (``JudgeSpec.schema_of``)."""
    from wenart.assets import recolour as RC
    out = {f"assets/recolour {n} slot(s)": RC.answer_schema(list(range(n))) for n in (1, 3, RC.load_config()[
        "max_slots_per_sheet"])}
    out["assets/recolour sparse slots"] = RC.answer_schema([0, 2, 5])
    item = {"key": "mat_u1", "context": {"uid": "u1", "slots": [1, 4]}}
    out["assets/recolour judge item"] = RC._spec().schema_of(item)
    return out


SOURCES = {"recognition": _recognition, "vision_check": _vision_check, "furniture": _furniture,
           "objaverse": _objaverse, "style": _style, "recolour": _recolour}


@pytest.mark.parametrize("source", sorted(SOURCES))
def test_every_schema_sent_to_vllm_uses_only_keywords_xgrammar_implements(source):
    found = SOURCES[source]()
    assert found, source
    problems = {name: RS.grammar_problems(schema) for name, schema in found.items()}
    bad = {name: p for name, p in problems.items() if p}
    assert not bad, f"schemas with keywords xgrammar does not implement (vLLM answers HTTP 400): {bad}"


# --------------------------------------------------------------------------
# The checker itself
# --------------------------------------------------------------------------

BASE = {"type": "object", "additionalProperties": False, "required": ["a"],
        "properties": {"a": {"type": "array", "items": {"enum": ["x", "y"]}, "maxItems": 2}}}


def test_the_checker_accepts_the_keywords_in_use():
    assert RS.grammar_problems(BASE) == []
    nullable = {"type": "object", "properties": {"box": {"type": ["array", "null"], "items": {"type": "number",
                                                                                              "minimum": 0},
                                                         "minItems": 4, "maxItems": 4}},
                "required": ["box"], "additionalProperties": False, "title": "T", "description": "d"}
    assert RS.grammar_problems(nullable) == []
    # Property NAMES and enum VALUES that happen to be keywords are not keywords.
    names = {"type": "object", "properties": {"uniqueItems": {"type": "string"}, "format": {"enum": ["not", "if"]}},
             "required": ["uniqueItems", "format"]}
    assert RS.grammar_problems(names) == []


@pytest.mark.parametrize("path,patch", [
    (("properties", "a"), {"uniqueItems": True}),                  # the prep pod's failure
    (("properties", "a"), {"contains": {"enum": ["x"]}}),
    (("properties", "a"), {"minContains": 1}),
    (("properties", "a"), {"maxContains": 1}),
    ((), {"patternProperties": {"^x": {"type": "string"}}}),
    ((), {"propertyNames": {"pattern": "^[a-z]+$"}}),
    ((), {"if": {"required": ["a"]}, "then": {"required": ["a"]}}),
    ((), {"else": {"required": ["a"]}}),
    ((), {"not": {"required": ["b"]}}),
    ((), {"dependentRequired": {"a": ["b"]}}),
    ((), {"dependentSchemas": {"a": {"required": ["b"]}}}),
    ((), {"minProperties": 1}),
    ((), {"maxProperties": 3}),
    ((), {"unevaluatedItems": False}),
    ((), {"someNewKeyword": 1}),                                   # unknown: check xgrammar first
])
def test_the_checker_refuses_keywords_xgrammar_does_not_implement(path, patch):
    schema = copy.deepcopy(BASE)
    node = schema
    for key in path:
        node = node[key]
    node.update(patch)
    problems = RS.grammar_problems(schema)
    assert problems and any(next(iter(patch)) in p for p in problems), problems


def test_the_checker_refuses_number_and_string_rules_xgrammar_lacks():
    assert RS.grammar_problems({"type": "number", "multipleOf": 0.5})
    assert RS.grammar_problems({"type": "string", "format": "colour"})
    assert RS.grammar_problems({"type": "string", "format": "date", "maxLength": 10})       # format + length
    assert RS.grammar_problems({"type": "string", "pattern": "^a$", "minLength": 1})         # pattern + length
    assert RS.grammar_problems({"type": "string", "format": "date"}) == []
    assert RS.grammar_problems({"type": "string", "maxLength": 160}) == []
    # Deep inside $defs, anyOf and items.
    deep = {"$defs": {"x": {"anyOf": [{"type": "array", "items": {"type": "array", "uniqueItems": True}}]}},
            "type": "object", "properties": {"a": {"$ref": "#/$defs/x"}}}
    assert any("uniqueItems" in p and "$defs/x/anyOf/0/items" in p for p in RS.grammar_problems(deep))
