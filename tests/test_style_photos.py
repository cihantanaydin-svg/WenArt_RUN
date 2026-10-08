"""CPU tests for the style reference photos (docs/milestone5.md §6): schema, prompt, fake two-model passes,
agreement, combine CLI, photo terms in the style profile (the brief always wins) and the style CLI flag."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import jsonschema
import pytest

from wenart.style import photos as SP
from wenart.style import profile as P
from wenart.style import vocabulary as V
from wenart.style.__main__ import main as style_main

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "tests" / "fixtures" / "style_photo_synthetic-03_salon.jpg"
CHARCOAL = {"floor": "concrete_polished", "walls": "plaster_charcoal", "light": "cool daylight",
            "family": "modern minimal"}


@dataclass
class FakeResult:
    """The fields of vlm_client.VLMResult that photos.py reads."""
    model: str
    data: Optional[dict]
    error: Optional[str] = None
    raw_text: str = ""
    latency_s: float = 0.5
    usage: dict = field(default_factory=dict)


class FakeClient:
    """Implements only ``.model`` and ``.run_schema`` (§1.5); answers from a fixed dict or fails."""

    def __init__(self, model: str, answer=None, error: Optional[str] = None, raises: bool = False):
        self.model = model
        self.answer = answer
        self.error = error
        self.raises = raises
        self.calls = []

    def run_schema(self, images, prompt, schema, *, seed=0, task="custom", max_side=None, labels=None,
                   system_prompt=None):
        self.calls.append({"images": list(images), "prompt": prompt, "schema": schema, "seed": seed, "task": task})
        if self.raises:
            raise ConnectionError("server gone")
        if self.error:
            return FakeResult(self.model, None, error=self.error)
        return FakeResult(self.model, dict(self.answer), raw_text=json.dumps(self.answer))


def clients(qwen_answer=CHARCOAL, glm_answer=CHARCOAL, **kw):
    return {"qwen": FakeClient("Qwen/Qwen3-VL-8B-Instruct", qwen_answer, **kw.get("qwen", {})),
            "glm": FakeClient("zai-org/GLM-4.6V-Flash", glm_answer, **kw.get("glm", {}))}


# --------------------------------------------------------------------------
# Schema and prompt
# --------------------------------------------------------------------------

def test_schema_enums_come_from_the_vocabulary():
    schema = SP.photo_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    props = schema["properties"]
    assert schema["required"] == ["floor", "walls", "light", "family"] and schema["additionalProperties"] is False
    assert {k: len(v["enum"]) - 1 for k, v in props.items()} == {"floor": 8, "walls": 5, "light": 5, "family": 9}
    assert all(v["enum"][-1] == "unclear" for v in props.values())
    # Milestone 10: the vocabulary grew (30+ floors, 20+ wall finishes, 9 moods) but the photo question keeps the
    # Milestone 5 option lists, in the order of the vocabulary's first appearance.
    assert props["floor"]["enum"][:-1] == list(SP.PHOTO_FLOORS) == [
        "wood_oak_light", "wood_walnut", "wood_parquet", "concrete_polished", "terracotta", "marble", "tiles_light", "carpet"]
    assert props["walls"]["enum"][:-1] == list(SP.PHOTO_WALLS) == [
        "plaster_white", "plaster_cream", "plaster_charcoal", "wood_panel", "brick"]
    assert props["light"]["enum"][:-1] == list(SP.PHOTO_LIGHTS) == [
        "warm daylight", "cool daylight", "golden evening", "overcast", "night"]
    assert set(SP.PHOTO_FLOORS) <= {s for _, s in V.FLOOR_WORDS} and set(SP.PHOTO_WALLS) <= {s for _, s in V.WALL_WORDS}
    assert set(SP.PHOTO_LIGHTS) <= set(V.LIGHTING) and len(V.LIGHTING) == 9
    assert props["family"]["enum"][:-1] == [n for n, _ in V.STYLE_FAMILIES]
    for slug in props["floor"]["enum"][:-1] + props["walls"]["enum"][:-1]:
        assert slug in V.MATERIALS


@pytest.mark.parametrize("answer, ok", [
    (CHARCOAL, True),
    ({**CHARCOAL, "walls": "unclear", "family": "unclear"}, True),
    ({**CHARCOAL, "walls": "concrete_polished"}, False),        # a floor slug is not a wall value
    ({**CHARCOAL, "extra": "x"}, False),
    ({k: v for k, v in CHARCOAL.items() if k != "light"}, False),
    ({**CHARCOAL, "light": "sunny"}, False),
    ({**CHARCOAL, "family": None}, False),
])
def test_schema_is_strict(answer, ok):
    errors = list(jsonschema.Draft202012Validator(SP.photo_schema()).iter_errors(answer))
    assert (not errors) == ok


def test_prompt_lists_every_option_and_unclear():
    prompt = SP.photo_prompt()
    for slot, values in SP.SLOT_VALUES.items():
        line = next(l for l in prompt.splitlines() if l.startswith(f"{slot} ("))
        for v in values + ["unclear"]:
            assert v in line, (slot, v)
    assert "light oak" in prompt and "herringbone" in prompt and "Do not guess" in prompt
    assert "layout" in prompt


# --------------------------------------------------------------------------
# Passes and agreement
# --------------------------------------------------------------------------

def test_two_models_agree_and_terms_carry_evidence():
    cl = clients()
    out = SP.read_style_photo(PHOTO, cl)
    assert out["file"] == PHOTO.name and len(out["sha256"]) == 64 and out["kind"] == "style_photo"
    assert [p["pass"] for p in out["passes"]] == [1, 2] and [p["model_key"] for p in out["passes"]] == ["qwen", "glm"]
    assert out["agreed"] == CHARCOAL and not out["single_pass"] and out["not_computed"] == []
    walls = next(t for t in out["terms"] if t["slot"] == "walls")
    assert walls["value"] == "plaster_charcoal" and walls["files"] == [PHOTO.name]
    assert walls["evidence"] == [
        {"method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": 1, "file": PHOTO.name},
        {"method": "ai", "model": "zai-org/GLM-4.6V-Flash", "pass": 2, "file": PHOTO.name}]
    call = cl["qwen"].calls[0]
    assert call["images"] == [PHOTO] and call["schema"] == SP.photo_schema() and call["task"] == "style_photo"
    assert json.loads(json.dumps(out)) == out                      # JSON-serialisable as stored


def test_disagreement_unclear_and_failures_give_no_term():
    glm = {**CHARCOAL, "floor": "marble", "walls": "unclear"}
    out = SP.read_style_photo(PHOTO, clients(glm_answer=glm))
    assert out["agreed"] == {"light": "cool daylight", "family": "modern minimal"}
    assert out["disagreements"] == {"floor": {"qwen": "concrete_polished", "glm": "marble"}}
    assert out["unclear"] == {"walls": {"qwen": "plaster_charcoal", "glm": "unclear"}}
    both_unclear = {k: "unclear" for k in CHARCOAL}
    assert SP.read_style_photo(PHOTO, clients(both_unclear, both_unclear))["terms"] == []
    # A failed call is not computed, never read as unclear or absent.
    failed = SP.read_style_photo(PHOTO, clients(glm={"error": "HTTP 500"}))
    assert failed["not_computed"] == ["glm"] and failed["single_pass"] and failed["terms"] == []
    assert failed["single"]["walls"] == {"qwen": "plaster_charcoal"}
    assert failed["passes"][1]["error"] == "HTTP 500" and failed["passes"][1]["data"] is None
    raised = SP.read_style_photo(PHOTO, clients(qwen={"raises": True}))
    assert raised["passes"][0]["error"].startswith("ConnectionError") and raised["not_computed"] == ["qwen"]


def test_invalid_answer_from_a_client_is_a_schema_error():
    bad = {**CHARCOAL, "walls": "pink"}
    out = SP.read_style_photo(PHOTO, clients(qwen_answer=bad))
    assert out["passes"][0]["data"] is None and out["passes"][0]["error"].startswith("schema:")
    assert out["not_computed"] == ["qwen"] and out["terms"] == []


def test_real_client_request_is_strict_and_temperature_zero(monkeypatch):
    """Through wenart.recognition.vlm_client.VLMClient (F0) with post_json stubbed: one image, then the prompt;
    temperature 0; the schema (without $schema) as the structured-output grammar; the answer validated."""
    from wenart.recognition import vlm_client

    bodies = []

    def post_json(url, body, timeout_s):
        bodies.append(body)
        return {"choices": [{"message": {"content": json.dumps(CHARCOAL)}}], "usage": {}}

    monkeypatch.setattr(vlm_client, "post_json", post_json)
    client = vlm_client.VLMClient("http://127.0.0.1:8001/v1", model="Qwen/Qwen3-VL-8B-Instruct")
    rec = SP.read_pass(PHOTO, client, "qwen")
    assert rec["data"] == CHARCOAL and rec["error"] is None and rec["model"] == "Qwen/Qwen3-VL-8B-Instruct"
    body = bodies[0]
    assert body["temperature"] == 0 and body["structured_outputs"]["json"] == vlm_client.grammar_of(SP.photo_schema())
    content = body["messages"][-1]["content"]
    assert [part["type"] for part in content] == ["image_url", "text"] and content[1]["text"] == SP.photo_prompt()
    # A grammar-breaking answer is a schema error, never a term.
    monkeypatch.setattr(vlm_client, "post_json", lambda url, body, timeout_s: {
        "choices": [{"message": {"content": json.dumps({**CHARCOAL, "walls": "pink"})}}]})
    bad = SP.read_pass(PHOTO, client, "qwen")
    assert bad["data"] is None and bad["error"].startswith("schema:")


def test_single_client_is_one_pass_with_the_check_yaml_number():
    out = SP.read_style_photo(PHOTO, {"glm": FakeClient("zai-org/GLM-4.6V-Flash", CHARCOAL)})
    assert out["passes"][0]["pass"] == 2 and out["single_pass"] and out["terms"] == []
    assert SP.pass_numbers(["glm", "qwen", "other"]) == {"glm": 2, "qwen": 1, "other": 3}


def vision_check_calls_file(tmp_path, glm_answer=CHARCOAL, photo=PHOTO) -> Path:
    """The layout ``python -m wenart.vision_check style-photo`` appends to: one call per photo and model."""
    calls = []
    for key, answer in (("qwen", CHARCOAL), ("glm", glm_answer)):
        client = FakeClient("model-" + key, answer)
        calls.append({"file": str(photo), "sha256": SP.file_sha256(photo), "model_key": key, "model": client.model,
                      "slug": key, "result": SP.read_style_photo(photo, {key: client}), "error": None, "seconds": 1.0})
    path = tmp_path / "style_photo_test.json"
    path.write_text(json.dumps({"schema_version": "0.1", "kind": "style_photo_passes", "calls": calls}),
                    encoding="utf-8")
    return path


def test_combine_agrees_passes_stored_in_separate_calls(tmp_path):
    data = json.loads(vision_check_calls_file(tmp_path).read_text(encoding="utf-8"))
    terms = SP.combine([data])
    assert {t["slot"]: t["value"] for t in terms["terms"]} == CHARCOAL
    assert terms["photos"][PHOTO.name]["single_pass"] is False
    assert [e["pass"] for e in terms["terms"][0]["evidence"]] == [1, 2]
    # A later re-run of one model replaces its earlier pass.
    rerun = {"file": str(PHOTO), "model_key": "glm", "model": "model-glm",
             "result": SP.read_style_photo(PHOTO, {"glm": FakeClient("model-glm", {**CHARCOAL, "floor": "marble"})})}
    terms2 = SP.combine([data, {"calls": [rerun]}])
    assert "floor" not in {t["slot"] for t in terms2["terms"]}
    assert terms2["photos"][PHOTO.name]["disagreements"]["floor"] == {"qwen": "concrete_polished", "glm": "marble"}
    # A failed call (no result) is a not-computed pass.
    failed = {"file": str(PHOTO), "model_key": "glm", "model": "model-glm", "result": None, "error": "timeout"}
    terms3 = SP.combine([data, {"calls": [failed]}])
    assert terms3["terms"] == [] and terms3["photos"][PHOTO.name]["not_computed"] == ["glm"]
    assert any("not computed" in w for w in terms3["warnings"])


def test_combine_photos_that_disagree_give_a_conflict(tmp_path):
    other = tmp_path / "kitchen.jpg"
    other.write_bytes(PHOTO.read_bytes()[::-1])
    a = SP.read_style_photo(PHOTO, clients())
    b = SP.read_style_photo(other, clients({**CHARCOAL, "walls": "plaster_white"},
                                           {**CHARCOAL, "walls": "plaster_white"}))
    terms = SP.combine([a, b])
    by_slot = {t["slot"]: t for t in terms["terms"]}
    assert "walls" not in by_slot and terms["conflicts"] == [
        {"slot": "walls", "values": {"kitchen.jpg": "plaster_white", PHOTO.name: "plaster_charcoal"}}]
    assert by_slot["floor"]["files"] == ["kitchen.jpg", PHOTO.name] and len(by_slot["floor"]["evidence"]) == 4


def test_cli_read_and_combine(tmp_path, capsys):
    out = tmp_path / "passes.json"
    for key in ("qwen", "glm"):
        def factory(model_key, base_url, _key=key):
            assert model_key == _key and base_url == "http://x:8001/v1"
            return FakeClient("model-" + model_key, CHARCOAL)
        assert SP.main(["read", str(PHOTO), str(tmp_path / "missing.jpg"), "--model-key", key, "--server",
                        "http://x:8001/v1", "--out", str(out)], client_factory=factory) == 0
    stored = json.loads(out.read_text(encoding="utf-8"))
    assert len(stored["calls"]) == 4 and stored["kind"] == "style_photo_passes"
    terms_path = tmp_path / "terms.json"
    assert SP.main(["combine", str(out), "--out", str(terms_path)]) == 0
    terms = json.loads(terms_path.read_text(encoding="utf-8"))
    assert {t["slot"]: t["value"] for t in terms["terms"]} == CHARCOAL
    assert terms["photos"]["missing.jpg"]["not_computed"] == ["qwen", "glm"]
    assert SP.main(["combine", str(tmp_path / "nope.json"), "--out", str(terms_path)]) == 2
    assert "term walls = plaster_charcoal" in capsys.readouterr().out


def test_style_photo_paths(tmp_path):
    folder = tmp_path / "style_photos"
    folder.mkdir()
    for n in ("b.jpg", "a.PNG", "notes.txt"):
        (folder / n).write_bytes(b"x")
    paths, warnings = SP.style_photo_paths(tmp_path, None)
    assert [p.name for p in paths] == ["a.PNG", "b.jpg"] and warnings == []
    paths, warnings = SP.style_photo_paths(tmp_path, {"values": {"style_photos": ["b.jpg", "gone.jpg"]}})
    assert [p.name for p in paths] == ["b.jpg"] and "gone.jpg" in warnings[0]
    assert SP.style_photo_paths(tmp_path / "none", None) == ([], [])


# --------------------------------------------------------------------------
# Photo terms in the style profile
# --------------------------------------------------------------------------

def terms(**slots):
    return {"terms": [{"slot": k, "value": v, "file": "salon.jpg", "files": ["salon.jpg"],
                       "evidence": [{"method": "ai", "model": "m", "pass": 1, "file": "salon.jpg"}]}
                      for k, v in slots.items()]}


def test_photo_terms_fill_only_open_slots_and_the_brief_wins():
    brief = {"style": "Scandinavian, oak floor"}
    plain = P.profile_from_brief(brief)
    assert plain["walls"]["material"] == "plaster_white"         # assumed from the family word
    out = P.profile_from_brief(brief, photo_terms=terms(floor="marble", walls="plaster_charcoal",
                                                        light="overcast"))
    assert out["floor"]["material"] == "wood_oak_light"          # the brief names the floor: it wins
    assert out["walls"]["material"] == "plaster_charcoal"        # family fill replaced by the photo
    assert out["lighting"]["mood"] == "overcast" and out["lighting"]["hdri"] == V.LIGHTING["overcast"]["hdri"]
    assert out["matched_terms"] == ["Scandinavian", "oak floor", "photo:salon.jpg:plaster_charcoal",
                                    "photo:salon.jpg:overcast"]
    assert any(w.startswith("photo: walls plaster_charcoal from style photo salon.jpg") for w in out["warnings"])
    assert any("not used (the brief names wood_oak_light)" in w for w in out["warnings"])
    assert not any(w.startswith("assumed: walls") or w.startswith("assumed: light") for w in out["warnings"])
    assert tuple(out) == P.PROFILE_KEYS


def test_photo_family_fills_the_family_slot_only():
    out = P.profile_from_brief({"style": "polished concrete floor"}, photo_terms=terms(family="industrial"))
    assert out["walls"]["material"] == "brick"                   # industrial family fill
    assert "photo:salon.jpg:industrial" in out["matched_terms"]
    assert any(w.startswith("assumed: walls brick from style family 'industrial'") for w in out["warnings"])
    with_brief_family = P.profile_from_brief({"style": "Mediterranean"}, photo_terms=terms(family="industrial"))
    assert with_brief_family["floor"]["material"] == "terracotta"


def test_no_style_in_the_brief_photo_terms_replace_the_default_text():
    out = P.profile_from_brief({}, photo_terms=terms(floor="concrete_polished", walls="plaster_charcoal"))
    assert out["floor"]["material"] == "concrete_polished" and out["walls"]["material"] == "plaster_charcoal"
    assert out["lighting"]["mood"] == "warm daylight"            # default text, no photo term for light
    assert out["warnings"][0].startswith("assumed: no style in the brief")
    assert any("replaces wood_oak_light of the default style text" in w for w in out["warnings"])


def test_bad_or_duplicate_photo_terms_are_ignored_loudly():
    bad = {"terms": [{"slot": "walls", "value": "pink", "file": "x.jpg"}, {"slot": "roof", "value": "tiles"},
                     {"slot": "walls", "value": "brick", "file": "a.jpg"},
                     {"slot": "walls", "value": "plaster_cream", "file": "b.jpg"}]}
    out = P.profile_from_brief({"style": "oak floor"}, photo_terms=bad)
    assert out["walls"]["material"] == "brick"
    assert sum("ignored photo term" in w for w in out["warnings"]) == 3


def test_no_photo_terms_changes_nothing():
    for brief in (None, {}, {"style": "Scandinavian, warm daylight"}):
        assert P.profile_from_brief(brief, photo_terms=None) == P.profile_from_brief(brief)
        assert P.profile_from_brief(brief, photo_terms={"terms": []}) == P.profile_from_brief(brief)
    assert P.profile_from_brief({}, photo_terms=terms()) == P.profile_from_brief({})


def test_style_cli_with_photo_terms(tmp_path):
    terms_path = tmp_path / "terms.json"
    terms_path.write_text(json.dumps(terms(walls="plaster_charcoal")), encoding="utf-8")
    out = tmp_path / "style.json"
    assert style_main([str(ROOT / "projects" / "synthetic-01"), "--out", str(out),
                       "--photo-terms", str(terms_path)]) == 0
    profile = json.loads(out.read_text(encoding="utf-8"))
    assert profile["walls"]["material"] == "plaster_white"       # the brief names white walls: it wins
    assert "photo:salon.jpg:plaster_charcoal" not in profile["matched_terms"]
    assert style_main([str(ROOT / "projects" / "synthetic-02"), "--out", str(out),
                       "--photo-terms", str(terms_path)]) == 0
    profile = json.loads(out.read_text(encoding="utf-8"))
    assert profile["walls"]["material"] == "plaster_charcoal"    # no brief at all: the photo fills walls
    assert "photo:salon.jpg:plaster_charcoal" in profile["matched_terms"]
    assert style_main([str(ROOT / "projects" / "synthetic-01"), "--out", str(out),
                       "--photo-terms", str(tmp_path / "missing.json")]) == 2


def test_combine_output_feeds_the_profile(tmp_path):
    data = json.loads(vision_check_calls_file(tmp_path).read_text(encoding="utf-8"))
    combined = SP.combine([data])
    out = P.profile_from_brief({"style": "Scandinavian"}, photo_terms=combined)
    assert out["floor"]["material"] == "concrete_polished" and out["walls"]["material"] == "plaster_charcoal"
    assert f"photo:{PHOTO.name}:concrete_polished" in out["matched_terms"]
