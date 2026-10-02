"""CPU tests of the realism A/B (docs/milestone6.md §6, §9 'realism').

(Named ``test_realism_ab.py``: ``tests/`` has no ``__init__.py``, so pytest imports test files by
their base name, and ``tests/gpu/test_realism.py`` already takes ``test_realism``.)

Covered: the prompts (verbatim from the spec) and the strict answer schema,
the post-validation, outcomes W/L/T/NC per order pair, the graded score, the
consensus, sign-test values, room outcomes, the room-cluster bootstrap
(deterministic), the controls evaluation with signal per model and
``single_model``, the decision rules (made only by ``realism-summary``),
unique pair ids, the pairs file (kept cameras, dropped list, skipped pairs,
``null_reencode`` files, control views), ``control_views``, a fake client
end to end on hand-made ``ab/`` folders with tiny JPEGs, resumable answers
(reuse, changed image, failed call, past deadline, set selection), stale
answers in combine, contact sheets, the summary table header of §6.3, the
system prompt reaching the request, CLI usage errors and the ``check.yaml``
realism block.
"""
import json
import re
import time
from pathlib import Path

import jsonschema
import numpy as np
import pytest
from PIL import Image

from wenart.recognition import vlm_client
from wenart.recognition.vlm_client import VLMResult, schema_errors
from wenart.vision_check import realism as RZ
from wenart.vision_check import schemas as S
from wenart.vision_check.cli import main

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "milestone6.md"
MODELS = ["qwen", "glm"]
DEGRADES = {"ctl_flat": "materials", "ctl_proxy": "furniture", "ctl_direct": "lighting", "ctl_lowspp": "photo"}


# --------------------------------------------------------------------------
# Helpers: spec text, answers, rows, hand-made AB folders, fake judges
# --------------------------------------------------------------------------

def spec_section(heading: str) -> str:
    text = SPEC.read_text(encoding="utf-8")
    start = text.index(heading)
    end = text.find("\n### ", start + len(heading))
    return text[start:end if end > 0 else None]


def code_blocks(section: str) -> list[str]:
    return re.findall(r"```\n(.*?)\n```", section, re.S)


def unwrap(block: str) -> str:
    """The spec wraps long lines (continuations are indented or do not start a bullet): one line per paragraph."""
    out: list[str] = []
    for line in block.split("\n"):
        if out and out[-1] != "" and line != "" and (line.startswith("  ") or not line.startswith("- ")):
            out[-1] += " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)


def aspect_answer(winner="image_1", margin="slight", cues=()):
    return {"winner": winner, "margin": margin, "cues": list(cues)}


def answer(**per_aspect):
    """A valid pair answer; ``per_aspect``: aspect -> (winner, margin[, cues])."""
    out = {}
    for a in RZ.ASPECTS:
        spec = per_aspect.get(a, ("image_1", "slight"))
        out[a] = aspect_answer(*spec)
    return out


OUTCOME_WINNERS = {"W": ["image_2", "image_1"], "L": ["image_1", "image_2"], "T": ["image_1", "image_1"],
                   "NC": [None, None]}


def mk_row(set_name, cam, room, outcomes, project="p", delta_ev=None, models=MODELS):
    """A ``realism_ab.json`` row; ``outcomes``: model -> outcome (every aspect) or {aspect: outcome}."""
    row = {"pair_id": RZ.pair_id(set_name, cam), "set": set_name, "cam": cam, "room_id": room,
           "room": RZ.room_key(project, room, cam), "project": project, "a": "a.jpg", "b": "b.jpg",
           "expected": RZ.SETS[set_name].expected, "target_aspect": RZ.SETS[set_name].target_aspect,
           "delta_ev": delta_ev, "models": {}}
    for m in models:
        per = outcomes.get(m, "NC")
        per = per if isinstance(per, dict) else {a: per for a in RZ.ASPECTS}
        aspects = {}
        for a in RZ.ASPECTS:
            o = per.get(a, "NC")
            graded = {"W": 4, "L": -4, "T": 0, "NC": None}[o]
            aspects[a] = {"outcome": o, "graded": graded, "winners": list(OUTCOME_WINNERS[o]),
                          "margins": ["clear", "clear"] if o != "NC" else [None, None],
                          "cues": [["material_texture"], ["material_texture"]] if o != "NC" else [None, None]}
        row["models"][m] = {"calls": {"ab": "answered", "ba": "answered"}, "aspects": aspects}
    row["consensus"] = {a: RZ.row_consensus(row, a, models) for a in RZ.ASPECTS}
    return row


def jpeg(path: Path, value: int, size=(32, 18)) -> Path:
    """A tiny JPEG of grey level ``value`` with thin brighter stripes (so a re-encode changes the bytes)."""
    arr = np.full((size[1], size[0], 3), value, np.uint8)
    arr[:, ::4] = min(255, value + 40)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path, format="JPEG", quality=85)
    return path


def cams_of(rooms: int, per_room: int) -> list[tuple[str, str]]:
    return [(f"cam_r{r}_{i}", f"r_{r}") for r in range(rooms) for i in range(1, per_room + 1)]


def write_ab(root: Path, name: str, rooms: int = 6, per_room: int = 3, controls: bool = False, alt: bool = True,
             kept=None, dropped=(), skip_m5=(), scene: bool = True) -> Path:
    """``root/outputs/<name>/ab/`` as the orchestrator leaves it before ``realism-pairs`` (§6.3)."""
    out = root / "outputs" / name
    cams = cams_of(rooms, per_room)
    entries = []
    for k, (cam, room) in enumerate(cams):
        jpeg(out / "ab" / "renders" / f"{cam}_preview.jpg", 120)
        if alt:
            jpeg(out / "ab" / "renders" / f"{cam}_alt_preview.jpg", 135)
        if cam not in skip_m5:
            jpeg(out / "ab" / "m5" / f"{cam}_preview.jpg", 100)
        entries.append({"camera": cam, "room_id": room, "level_id": "L0", "resolution": [32, 18],
                        "preview": f"{cam}_preview.jpg",
                        "index_stats": {"1": {"pixels": 10 + k, "box": [0, 0, 8, 8]},
                                        "2": {"pixels": 300, "box": [0, 0, 32, 18]}}})
    (out / "ab" / "renders" / "render_manifest.json").write_text(
        json.dumps({"schema_version": "0.1", "renders": entries}), encoding="utf-8")
    if scene:
        objects = [{"name": "furn_f_1", "wenart_id": "f_1", "kind": "furniture", "type": "sofa", "pass_index": 1,
                    "room_id": "r_0"},
                   {"name": "d_1_frame", "wenart_id": "d_1", "kind": "door", "pass_index": 2, "room_ids": ["r_0"]}]
        sm = {"project": name, "objects": objects, "cameras": [{"name": c, "room_id": r} for c, r in cams]}
        (out / "ab" / "scene").mkdir(parents=True, exist_ok=True)
        (out / "ab" / "scene" / "scene_manifest.json").write_text(json.dumps(sm), encoding="utf-8")
    kept = [c for c, _ in cams if c not in {d[0] for d in dropped}] if kept is None else kept
    check = {"kept": kept, "dropped": [{"cam": c, "reason": r} for c, r in dropped]}
    (out / "ab" / "cameras_check.json").write_text(json.dumps(check), encoding="utf-8")
    if controls:
        for s in list(DEGRADES) + ["nuisance_ev"]:
            for cam, _ in cams:
                jpeg(out / "ab" / s / "renders" / f"{cam}_preview.jpg", 150 if s == "nuisance_ev" else 120)
    return out


def smart_score(path, aspect: str) -> int:
    """A judge that sees every degradation and prefers the M6 look on every aspect."""
    parts = Path(str(path)).parts
    for s, a in DEGRADES.items():
        if s in parts:
            return 0 if a == aspect else 1
    return 0 if "m5" in parts else 1


class FakeJudge:
    """``.model`` + ``.run_schema``: per aspect the image with the higher score wins (large margin); equal scores
    pick image 1 (position bias, slight). ``blind``: always image 1. ``fail``: image paths whose call fails."""

    def __init__(self, model="fake/judge", blind=False, fail=(), score=smart_score, delay=0.0):
        self.model = model
        self.blind = blind
        self.fail = set(fail)
        self.score = score
        self.delay = delay
        self.calls = []

    def run_schema(self, images, prompt, schema, *, seed=0, task="custom", max_side=None, labels=None,
                   system_prompt=None):
        names = [Path(str(i)).relative_to(Path(str(i)).parents[2]).as_posix() for i in images]
        self.calls.append({"images": [str(i) for i in images], "names": names, "task": task, "labels": labels,
                           "prompt": prompt, "system_prompt": system_prompt, "seed": seed})
        if self.delay:
            time.sleep(self.delay)
        if any(str(i) in self.fail for i in images):
            return VLMResult(task=task, model=self.model, data=None, raw_text="", latency_s=0.01, attempts=3,
                             error="cannot reach http://fake: refused")
        data = {}
        for a in RZ.ASPECTS:
            if self.blind:
                data[a] = aspect_answer("image_1", "slight", [])
                continue
            s1, s2 = self.score(images[0], a), self.score(images[1], a)
            if s1 == s2:
                data[a] = aspect_answer("image_1", "slight", ["camera_look"])
            else:
                data[a] = aspect_answer("image_1" if s1 > s2 else "image_2", "large",
                                        ["material_texture", "material_texture", "contact_shadows"])
        problems = schema_errors(schema, data)
        assert not problems, problems
        return VLMResult(task=task, model=self.model, data=data, raw_text=json.dumps(data), latency_s=0.01,
                         attempts=1)


def factory_for(judges: dict):
    def factory(key, url):
        judges[key].url = url
        return judges[key]
    return factory


def read(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def keys_named(node, name: str) -> list:
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == name:
                found.append(v)
            found += keys_named(v, name)
    elif isinstance(node, list):
        for v in node:
            found += keys_named(v, name)
    return found


@pytest.fixture()
def rc():
    return RZ.realism_cfg()


# --------------------------------------------------------------------------
# Prompts and schema
# --------------------------------------------------------------------------

def test_prompts_are_verbatim_from_the_spec():
    blocks = code_blocks(spec_section("### 6.1"))
    assert unwrap(blocks[0]) == RZ.SYSTEM_PROMPT
    assert unwrap(blocks[1]) == RZ.PROMPT
    assert RZ.PROMPT.count("\n\n") == 5 and RZ.PROMPT.endswith("Answer only with JSON that follows the schema.")
    # The cue list in the prompt is the schema's enum, in order.
    cues = re.search(r"^Cues: (.*)\.$", RZ.PROMPT, re.M).group(1).split(", ")
    assert tuple(cues) == S.REALISM_CUES and len(cues) == 12
    assert RZ.LABELS == ("Image 1:", "Image 2:")
    # Not the vision-check system prompt ("When unsure, say so" invited the "same" answer in M5).
    assert "unsure" not in RZ.SYSTEM_PROMPT and RZ.SYSTEM_PROMPT != vlm_client.SCHEMA_SYSTEM_PROMPT


def test_schema_is_strict():
    schema = S.realism_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["required"] == ["materials", "lighting", "furniture", "photo"] == list(schema["properties"])
    assert "$ref" not in json.dumps(schema) and "uniqueItems" not in json.dumps(schema)
    assert schema["additionalProperties"] is False
    for a in RZ.ASPECTS:
        sub = schema["properties"][a]
        assert sub["additionalProperties"] is False and sub["required"] == ["winner", "margin", "cues"]
        assert sub["properties"]["winner"]["enum"] == ["image_1", "image_2"]
        assert sub["properties"]["margin"]["enum"] == ["slight", "clear", "large"]
        assert sub["properties"]["cues"]["maxItems"] == 3
    good = answer(photo=("image_2", "clear", ["camera_look"]))
    assert schema_errors(schema, good) == []
    bad = []
    for mutate in (lambda d: d["photo"].update(winner="same"),          # no tie
                   lambda d: d["photo"].update(winner="both"),
                   lambda d: d["lighting"].update(margin="huge"),
                   lambda d: d["materials"].update(cues=["material_texture"] * 4),
                   lambda d: d["materials"].update(cues=["shiny"]),
                   lambda d: d["materials"].update(note="x"),
                   lambda d: d.update(overall="image_1"),
                   lambda d: d.pop("furniture"),
                   lambda d: d["photo"].pop("cues")):
        d = json.loads(json.dumps(good))
        mutate(d)
        bad.append(schema_errors(schema, d))
    assert all(bad), bad


def test_post_validation_removes_repeated_cues_and_rejects_bad_answers():
    raw = answer(materials=("image_2", "large", ["material_texture", "material_response", "material_texture"]))
    data, error = RZ.post_validate(raw)
    assert error is None and data["materials"]["cues"] == ["material_texture", "material_response"]
    assert raw["materials"]["cues"] == ["material_texture", "material_response", "material_texture"]   # not changed
    data, error = RZ.post_validate({"photo": {"winner": "same"}})
    assert data is None and error.startswith("schema: ")


def test_realism_client_sends_the_system_prompt_and_post_validates(monkeypatch, tmp_path):
    bodies = []
    reply = answer(photo=("image_2", "clear", ["fewer_artifacts", "fewer_artifacts"]))

    def post_json(url, body, timeout_s):
        bodies.append(body)
        return {"choices": [{"message": {"content": json.dumps(reply)}}], "usage": {}}

    monkeypatch.setattr(vlm_client, "post_json", post_json)
    a, b = jpeg(tmp_path / "a.jpg", 90), jpeg(tmp_path / "b.jpg", 140)
    client = RZ.RealismClient(vlm_client.VLMClient("http://127.0.0.1:9/v1", model="x", retries=1, timeout_s=1))
    client.deadline = time.time() + 60                        # handed on to the VLMClient
    assert client.client.deadline == client.deadline
    res = client.run_schema([a, b], RZ.PROMPT, S.realism_schema(), seed=0, labels=list(RZ.LABELS))
    assert res.error is None and res.data["photo"]["cues"] == ["fewer_artifacts"]
    body = bodies[0]
    assert body["messages"][0]["content"] == RZ.SYSTEM_PROMPT and body["temperature"] == 0.0 and body["seed"] == 0
    content = body["messages"][1]["content"]
    assert [c["type"] for c in content] == ["text", "image_url", "text", "image_url", "text"]
    assert (content[0]["text"], content[2]["text"], content[-1]["text"]) == ("Image 1:", "Image 2:", RZ.PROMPT)
    # A schema-valid answer of the server that the post-validation refuses never happens; an invalid one is an error.
    reply = {"photo": {"winner": "same"}}
    res = client.run_schema([a, b], RZ.PROMPT, S.realism_schema(), labels=list(RZ.LABELS))
    assert res.data is None and res.error.startswith("schema: ")


# --------------------------------------------------------------------------
# Outcomes, graded score, consensus
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ab, ba, outcome", [
    ("image_2", "image_1", "W"),        # B picked in both orders
    ("image_1", "image_2", "L"),        # A picked in both orders
    ("image_1", "image_1", "T"),        # follows the position
    ("image_2", "image_2", "T"),
])
def test_outcomes_per_order_pair(ab, ba, outcome):
    rec = RZ.model_outcome(answer(photo=(ab, "clear")), answer(photo=(ba, "clear")), "photo")
    assert rec["outcome"] == outcome and rec["winners"] == [ab, ba]
    assert RZ.picks_b("ab", "image_2") and RZ.picks_b("ba", "image_1") and not RZ.picks_b("ab", "image_1")
    assert RZ.picks_b("ab", None) is None


def test_a_missing_call_is_not_computed_never_a_tie_or_loss():
    rec = RZ.model_outcome(answer(photo=("image_2", "large")), None, "photo")
    assert rec["outcome"] == "NC" and rec["graded"] is None and rec["winners"] == ["image_2", None]
    assert RZ.model_outcome(None, None, "photo")["outcome"] == "NC"


@pytest.mark.parametrize("ab, ba, graded", [
    (("image_2", "large"), ("image_1", "large"), 6),     # B, large, both orders
    (("image_1", "large"), ("image_2", "large"), -6),
    (("image_1", "clear"), ("image_2", "slight"), -3),
    (("image_1", "large"), ("image_1", "large"), 0),     # pure position bias cancels
    (("image_2", "large"), ("image_2", "slight"), 2),    # T, but leaning toward B
])
def test_graded_score(ab, ba, graded):
    assert RZ.model_outcome(answer(lighting=ab), answer(lighting=ba), "lighting")["graded"] == graded


def test_consensus_rules():
    assert RZ.consensus(["W", "W"]) == "W" and RZ.consensus(["L", "L"]) == "L"
    assert RZ.consensus(["W", "L"]) == "T" and RZ.consensus(["W", "T"]) == "T" and RZ.consensus(["T", "T"]) == "T"
    assert RZ.consensus(["W", "NC"]) == "NC" and RZ.consensus(["NC", "T"]) == "NC"
    assert RZ.consensus(["W"]) == "W" and RZ.consensus([]) == "NC"


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def test_sign_test_values():
    assert RZ.sign_test_p(9, 1) == pytest.approx(22 / 1024)
    assert RZ.sign_test_p(1, 9) == pytest.approx(22 / 1024)
    assert RZ.sign_test_p(8, 2) == pytest.approx(112 / 1024)
    assert RZ.sign_test_p(6, 0) == pytest.approx(2 / 64) and RZ.sign_test_p(5, 0) == pytest.approx(2 / 32)
    assert RZ.sign_test_p(5, 5) == 1.0 and RZ.sign_test_p(0, 0) == 1.0 and RZ.sign_test_p(1, 0) == 1.0
    # The power table of the research: 21 of 30 decisive pairs is the smallest win count with p < 0.05.
    assert RZ.sign_test_p(21, 9) == pytest.approx(0.0427739, rel=1e-5)
    assert RZ.sign_test_p(21, 9) < 0.05 < RZ.sign_test_p(20, 10)
    assert 0 < RZ.sign_test_p(300, 0) < 1e-80                     # no overflow for large n


def test_room_outcomes():
    assert RZ.room_outcome(["W", "W", "L"]) == "W" and RZ.room_outcome(["L", "T"]) == "L"
    assert RZ.room_outcome(["W", "L"]) == "T" and RZ.room_outcome(["T", "NC"]) == "T"
    assert RZ.room_outcome(["NC", "NC"]) == "NC" and RZ.room_outcome(["W", "NC", "NC"]) == "W"


def test_bootstrap_is_deterministic_and_resamples_rooms():
    items = [(f"room{i % 7}", o) for i, o in enumerate("WWLTWWNCWLTW".replace("NC", "N"))]
    items = [(r, "NC" if o == "N" else o) for r, o in items]
    first = RZ.room_bootstrap(items, 2000, 0)
    assert first == RZ.room_bootstrap(list(reversed(items)), 2000, 0)          # item order does not matter
    assert first == RZ.room_bootstrap(items, 2000, 0)
    assert first[0] <= first[1] and -1 <= first[0] and first[1] <= 1
    assert RZ.room_bootstrap([("a", "W"), ("a", "W"), ("b", "W")]) == [1.0, 1.0]
    assert RZ.room_bootstrap([("a", "L"), ("b", "L")]) == [-1.0, -1.0]
    assert RZ.room_bootstrap([]) == [None, None] and RZ.room_bootstrap([("a", "NC")]) == [None, None]
    assert RZ.room_bootstrap([("a", "W"), ("b", "L"), ("c", "W"), ("d", "T")]) == [-0.5, 1.0]
    # One room with many W views among rooms with one L each: the views are not independent.
    clustered = [("big", "W")] * 30 + [(f"r{i}", "L") for i in range(9)]
    lo, hi = RZ.room_bootstrap(clustered)
    assert lo < 0 < hi


def test_aspect_stats_counts_consistency_graded_and_rooms(rc):
    rows = [mk_row("m5_vs_m6", "c1", "r1", {"qwen": "W", "glm": "W"}),
            mk_row("m5_vs_m6", "c2", "r1", {"qwen": "W", "glm": "T"}),
            mk_row("m5_vs_m6", "c3", "r2", {"qwen": "L", "glm": "L"}),
            mk_row("m5_vs_m6", "c4", "r3", {"qwen": "T", "glm": "NC"})]
    st = RZ.aspect_stats(rows, "photo", MODELS, MODELS, rc)
    assert {k: st["models"]["qwen"][k] for k in "WLT"} == {"W": 2, "L": 1, "T": 1}
    assert st["models"]["qwen"]["consistency"] == 0.75 and st["models"]["qwen"]["mean_graded"] == 1.0
    assert st["models"]["glm"]["NC"] == 1 and st["models"]["glm"]["consistency"] == pytest.approx(2 / 3, abs=1e-4)
    assert st["consensus"] == {"W": 1, "L": 1, "T": 1, "NC": 1}
    assert (st["n"], st["decisive"], st["decisive_rooms"], st["win_rate"]) == (3, 2, 2, pytest.approx(1 / 3, abs=1e-4))
    assert st["rooms"] == {"W": 1, "L": 1, "T": 0, "NC": 1}          # r1: W+T -> W; r2: L; r3: only NC
    assert st["sign_p"] == 1.0 and st["net_win"] == 0.0
    # Consensus of one model only (single_model).
    st1 = RZ.aspect_stats(rows, "photo", MODELS, ["qwen"], rc)
    assert st1["consensus"] == {"W": 2, "L": 1, "T": 1, "NC": 0}


def test_position_bias_and_top_cues():
    rows = [mk_row("m5_vs_m6", f"c{i}", f"r{i}", {"qwen": "T", "glm": "W"}) for i in range(3)]
    assert RZ.position_bias(rows, "qwen") == {"image_1": 24, "picks": 24, "index": 1.0}
    assert RZ.position_bias(rows, "glm") == {"image_1": 12, "picks": 24, "index": 0.5}
    top = RZ.top_cues(rows, "materials", ["glm"])
    assert top == {"W": [["material_texture", 6]], "L": []}
    assert RZ.top_cues(rows, "materials", MODELS) == {"W": [], "L": []}      # consensus T: nothing decisive


# --------------------------------------------------------------------------
# Controls, signal, single_model, decisions
# --------------------------------------------------------------------------

def control_rows(qwen_sees=True, glm_sees=False, flips=0, reencode_wins=0, brighter=True):
    """Rows of the seven control sets on 8 views: a model that 'sees' wins the target aspect, else follows
    the position."""
    rows = []
    for s, target in DEGRADES.items():
        for i in range(8):
            per = {}
            for m, sees in (("qwen", qwen_sees), ("glm", glm_sees)):
                per[m] = {a: ("W" if sees and a == target else "T") for a in RZ.ASPECTS}
            rows.append(mk_row(s, f"cam_{i}", f"r{i % 4}", per))
    for i in range(8):
        o = "W" if i < flips else "T"
        rows.append(mk_row("null_identical", f"cam_{i}", f"r{i % 4}", {"qwen": {"photo": o, "materials": "T",
                                                                                 "lighting": "T", "furniture": "T"},
                                                                        "glm": "T"}))
        rows.append(mk_row("null_reencode", f"cam_{i}", f"r{i % 4}",
                           {"qwen": "W" if i < reencode_wins else "T", "glm": "T"}))
        rows.append(mk_row("nuisance_ev", f"cam_{i}", f"r{i % 4}", {"qwen": "W" if brighter else "T", "glm": "T"},
                           delta_ev=0.27))
    return rows


def test_controls_evaluation_signal_and_single_model(rc):
    ctl = RZ.evaluate_controls(control_rows(flips=1, reencode_wins=1), MODELS, rc)
    flat = ctl["sets"]["ctl_flat"]
    assert flat["target_aspect"] == "materials" and flat["pairs"] == 8
    assert flat["models"]["qwen"] == {"n": 8, "correct": 8, "wrong": 0, "tie": 0, "nc": 0, "correct_rate": 1.0,
                                      "wrong_rate": 0.0, "pass": True}
    assert flat["models"]["glm"]["pass"] is False and flat["models"]["glm"]["tie"] == 8
    assert flat["consensus"]["pass"] is False                         # glm never agrees
    assert ctl["signal"] == {"qwen": True, "glm": False} and ctl["no_signal"] == ["glm"]
    assert "no signal from GLM" in ctl["notes"]
    ni = ctl["sets"]["null_identical"]["models"]["qwen"]
    assert ni["n"] == 32 and ni["tie"] == 31 and ni["flips"] == ["null_identical:cam_0/photo: W"] and ni["pass"]
    nr = ctl["sets"]["null_reencode"]["models"]["qwen"]
    assert nr["win_rate"] == pytest.approx(4 / 32) and nr["pass"] is False          # 12.5 % > 10 %
    nu = ctl["sets"]["nuisance_ev"]
    assert nu["models"]["qwen"]["share"] == 1.0 and nu["models"]["qwen"]["flag"] and nu["flag"]
    assert nu["models"]["glm"]["share"] == 0.0 and nu["mean_delta_ev"] == 0.27
    assert ctl["halo"]["qwen"] == {"n": 96, "follow": 0, "share": 0.0, "note": None}
    assert ctl["halo"]["glm"]["n"] == 0 and ctl["halo"]["glm"]["share"] is None
    # A known-direction set where the wrong image wins too often fails the model even with 70 % correct.
    rows = control_rows(qwen_sees=True, glm_sees=True)
    for r in rows:
        if r["set"] == "ctl_proxy" and r["cam"] == "cam_0":
            r["models"]["qwen"]["aspects"]["furniture"]["outcome"] = "L"
    ctl = RZ.evaluate_controls(rows, MODELS, rc)
    assert ctl["sets"]["ctl_proxy"]["models"]["qwen"]["wrong_rate"] == 0.125
    assert ctl["signal"] == {"qwen": False, "glm": True}
    # Halo: every other aspect follows the target winner.
    rows = control_rows()
    for r in rows:
        if r["set"] in DEGRADES:
            for a in RZ.ASPECTS:
                r["models"]["qwen"]["aspects"][a]["outcome"] = "W"
    halo = RZ.evaluate_controls(rows, MODELS, rc)["halo"]["qwen"]
    assert halo["share"] == 1.0 and halo["note"] == RZ.HALO_NOTE
    assert RZ.evaluate_controls([mk_row("m5_vs_m6", "c", "r", {"qwen": "W"})], MODELS, rc) is None


def ab_rows(n_w=36, n_l=0, rooms=12, other=None, models=MODELS, set_name="m5_vs_m6"):
    rows = []
    for i in range(n_w + n_l):
        o = "W" if i < n_w else "L"
        per = {a: o for a in RZ.ASPECTS}
        per.update(other or {})
        rows.append(mk_row(set_name, f"c{i}", f"r{i % rooms}", {m: per for m in models}))
    return rows


def test_decision_rules(rc):
    def decision(rows, measurable=True, cons=MODELS):
        return RZ.decide(RZ.set_stats(rows, MODELS, cons, rc), measurable, rc)

    d, per = decision(ab_rows(36, 0, 12))
    assert d == "better" and per == {a: "better" for a in RZ.ASPECTS}
    assert decision(ab_rows(0, 36, 12))[0] == "worse"
    assert decision(ab_rows(29, 0, 12))[0] == "no_detectable_difference"      # < 30 decisive pairs
    assert decision(ab_rows(36, 0, 9))[0] == "no_detectable_difference"       # < 10 rooms
    assert decision(ab_rows(18, 18, 12))[0] == "no_detectable_difference"
    # Photo better, but lighting significantly worse: no "better" for the set; the aspects keep their own.
    d, per = decision(ab_rows(36, 0, 12, other={"lighting": "L"}))
    assert d == "no_detectable_difference" and per["photo"] == "better" and per["lighting"] == "worse"
    # Significant at view level, but the room-level interval reaches below 0 (one room carries the wins).
    rows = [mk_row("m5_vs_m6", f"c{i}", "big", {m: "W" for m in MODELS}) for i in range(30)]
    rows += [mk_row("m5_vs_m6", f"d{i}", f"r{i}", {m: "L" for m in MODELS}) for i in range(9)]
    st = RZ.set_stats(rows, MODELS, MODELS, rc)
    assert st["aspects"]["photo"]["sign_p"] < 0.05 and st["aspects"]["photo"]["decisive_rooms"] == 10
    assert st["aspects"]["photo"]["net_win_ci95"][0] < 0
    assert RZ.decide(st, True, rc)[0] == "no_detectable_difference"
    # Controls failing for every model: not measurable, whatever the pairs say.
    d, per = decision(ab_rows(36, 0, 12), measurable=False)
    assert d == "not_measurable" and set(per.values()) == {"not_measurable"}
    # The consensus of two models where one only follows the position: no decisive pair at all.
    rows = ab_rows(36, 0, 12, models=["qwen"])
    for r in rows:
        r["models"]["glm"] = mk_row("m5_vs_m6", "x", "x", {"glm": "T"})["models"]["glm"]
    assert decision(rows)[0] == "no_detectable_difference" and decision(rows, cons=["qwen"])[0] == "better"


# --------------------------------------------------------------------------
# control_views and the pairs file
# --------------------------------------------------------------------------

def test_control_views_rank_by_furniture_share_then_name():
    scene = {"objects": [
        {"wenart_id": "f_1", "kind": "furniture", "pass_index": 1},
        {"wenart_id": "proxy:f_2", "kind": "furniture_proxy", "pass_index": 2},     # counts as furniture
        {"wenart_id": "d_1", "kind": "door", "pass_index": 3},
        {"wenart_id": "dec_1", "kind": "decor", "type": "plant", "pass_index": 4, "host_id": None}]}

    def entry(cam, stats, res=(100, 10)):
        return {"camera": cam, "resolution": list(res),
                "index_stats": {str(k): {"pixels": v, "box": [0, 0, 1, 1]} for k, v in stats.items()}}

    manifest = {"renders": [
        entry("cam_b", {1: 100}), entry("cam_a", {1: 100}),          # tie: by name
        entry("cam_c", {2: 300}), entry("cam_d", {3: 900, 4: 900}),  # doors and decor do not count
        entry("cam_e", {1: 50, 2: 50}, res=(10, 10)),                # share 1.0 at a smaller size
        entry("cam_f", {}), {"camera": "cam_g", "resolution": [100, 10]}]}
    assert RZ.control_views(manifest, scene, 8) == ["cam_e", "cam_c", "cam_a", "cam_b", "cam_d", "cam_f", "cam_g"]
    assert RZ.control_views(manifest, scene, 2) == ["cam_e", "cam_c"]
    assert RZ.control_views(manifest, {}, 3) == ["cam_a", "cam_b", "cam_c"]        # no table: all 0, by name
    assert RZ.furniture_share(manifest["renders"][2], {2: {"kind": "furniture"}}) == pytest.approx(0.3)


def test_pairs_file(tmp_path):
    out = write_ab(tmp_path, "proj", rooms=4, per_room=3, controls=True, dropped=[("cam_r0_2", "moved 4 mm")],
                   skip_m5=["cam_r1_1"])
    assert main(["realism-pairs", "--project-out", str(out), "--controls"]) == 0
    doc = read(out / "ab" / "pairs.json")
    jsonschema.validate(doc, S.realism_pairs_file_schema())
    pairs = doc["pairs"]
    ids = [p["pair_id"] for p in pairs]
    assert len(ids) == len(set(ids))
    assert doc["project"] == "proj" and doc["controls"] is True
    assert doc["dropped"] == [{"cam": "cam_r0_2", "reason": "moved 4 mm"}]
    assert {"set": "m5_vs_m6", "cam": "cam_r1_1", "reason": "missing ab/m5/cam_r1_1_preview.jpg"} in doc["skipped"]
    m5 = [p for p in pairs if p["set"] == "m5_vs_m6"]
    assert [p["cam"] for p in m5] == [c for c, _ in cams_of(4, 3) if c not in ("cam_r0_2", "cam_r1_1")]
    # The 8 control views: the highest furniture share (the later cameras in write_ab), ties by name.
    assert doc["control_views"] == [c for c, _ in cams_of(4, 3)][::-1][:8]
    assert doc["sets"] == {"ctl_flat": 8, "ctl_proxy": 8, "ctl_direct": 8, "ctl_lowspp": 8, "null_identical": 8,
                           "null_reencode": 8, "nuisance_ev": 8, "m5_vs_m6": 10, "look_alt": 12}
    # Sets in the asking order, pair fields as in §6.3.
    order = [RZ.SET_ORDER.index(p["set"]) for p in pairs]
    assert order == sorted(order)
    p = next(p for p in pairs if p["set"] == "ctl_flat")
    assert (p["a"], p["b"]) == (f"ab/ctl_flat/renders/{p['cam']}_preview.jpg", f"ab/renders/{p['cam']}_preview.jpg")
    assert (p["expected"], p["target_aspect"], p["room_id"]) == ("b", "materials", "r_3")
    assert p["a_bytes"] == (out / p["a"]).stat().st_size and p["b_sha256"] == RZ.sha256_file(out / p["b"])
    targets = {q["set"]: q["target_aspect"] for q in pairs if q["set"] in DEGRADES}
    assert targets == DEGRADES
    ni = next(q for q in pairs if q["set"] == "null_identical")
    assert ni["a"] == ni["b"] and ni["a_sha256"] == ni["b_sha256"] and ni["expected"] == "tie" and ni["delta_ev"] == 0
    nr = next(q for q in pairs if q["set"] == "null_reencode")
    assert nr["a"] == f"ab/null_reencode/{nr['cam']}_reencode.jpg" and nr["expected"] == "tie"
    assert nr["a_sha256"] != nr["b_sha256"]
    with Image.open(out / nr["a"]) as img:
        assert img.format == "JPEG" and img.size == (32, 18)
    nu = next(q for q in pairs if q["set"] == "nuisance_ev")
    assert nu["delta_ev"] > 0 and nu["expected"] is None                    # B is the brighter render
    assert next(q for q in pairs if q["set"] == "m5_vs_m6")["delta_ev"] > 0
    la = next(q for q in pairs if q["set"] == "look_alt")
    assert la["b"].endswith("_alt_preview.jpg") and la["expected"] is None
    # Re-running rewrites nothing that did not change (the re-encode is deterministic).
    mtime = (out / nr["a"]).stat().st_mtime_ns
    time.sleep(0.01)
    assert main(["realism-pairs", "--project-out", str(out), "--controls"]) == 0
    assert (out / nr["a"]).stat().st_mtime_ns == mtime and read(out / "ab" / "pairs.json") == doc
    # Without --controls: only the A/B sets.
    assert main(["realism-pairs", "--project-out", str(out)]) == 0
    assert read(out / "ab" / "pairs.json")["sets"] == {"m5_vs_m6": 10, "look_alt": 12}


def test_pairs_file_edge_cases(tmp_path, capsys):
    out = write_ab(tmp_path, "noalt", rooms=1, per_room=2, alt=False, scene=False, kept=["cam_r0_1", "cam_zz"])
    doc = RZ.build_pairs(out)
    assert doc["sets"] == {"m5_vs_m6": 1} and doc["project"] == "noalt"
    assert any("look_alt: no alt previews" in w for w in doc["warnings"])
    assert {"set": "m5_vs_m6", "cam": "cam_zz", "reason": "kept camera not in the AB render manifest"} in doc["skipped"]
    assert doc["pairs"][0]["room_id"] == "r_0"                         # from the render manifest entry
    (out / "ab" / "cameras_check.json").unlink()
    assert main(["realism-pairs", "--project-out", str(out)]) == 1
    assert "cameras_check.json" in capsys.readouterr().err
    with pytest.raises(FileNotFoundError):
        RZ.build_pairs(tmp_path / "nothing")
    # No pair at all: exit 1.
    out = write_ab(tmp_path, "empty", rooms=1, per_room=1, alt=False, kept=[])
    assert main(["realism-pairs", "--project-out", str(out)]) == 1


def test_unique_pair_ids():
    RZ.check_unique([{"pair_id": "a:1"}, {"pair_id": "b:1"}])
    with pytest.raises(ValueError, match="m5_vs_m6:c1"):
        RZ.check_unique([{"pair_id": "m5_vs_m6:c1"}, {"pair_id": "m5_vs_m6:c1"}])
    assert RZ.call_key(RZ.pair_id("ctl_flat", "cam_1"), "ba") == "realism|ctl_flat:cam_1|ba"
    # Seven control sets on the same 8 cameras give 7 different keys per camera and order.
    keys = {RZ.call_key(RZ.pair_id(s, "cam_1"), "ab") for s in RZ.SET_ORDER}
    assert len(keys) == len(RZ.SET_ORDER) == 9


# --------------------------------------------------------------------------
# End to end with fake judges
# --------------------------------------------------------------------------

def run_all(tmp_path, judges, glm_blind=True, workers="2"):
    """Two A/B projects (6 + 6 rooms, 18 + 18 cameras), controls on the first; pairs, calls, combine, summary."""
    p1 = write_ab(tmp_path, "synthetic-01", rooms=6, per_room=3, controls=True)
    p2 = write_ab(tmp_path, "synthetic-03", rooms=6, per_room=3)
    f = factory_for(judges)
    assert main(["realism-pairs", "--project-out", str(p1), "--controls"]) == 0
    assert main(["realism-pairs", "--project-out", str(p2)]) == 0
    for out in (p1, p2):
        for key in MODELS:
            assert main(["realism", "--project-out", str(out), "--model-key", key, "--server", "http://x:8001/v1",
                         "--workers", workers], client_factory=f) == 0
        assert main(["realism-combine", "--project-out", str(out), "--models", "qwen,glm"]) == 0
    dest = tmp_path / "results" / "realism"
    assert main(["realism-summary", "--project-outs", str(p1), str(p2), "--controls-project", "synthetic-01",
                 "--out", str(dest), "--models", "qwen,glm"]) == 0
    return p1, p2, dest


def test_fake_client_end_to_end(tmp_path):
    judges = {"qwen": FakeJudge("fake/qwen"), "glm": FakeJudge("fake/glm", blind=True)}
    p1, p2, dest = run_all(tmp_path, judges, workers="1")
    # Calls: every pair in both orders, controls first, then m5_vs_m6, then look_alt; own system prompt.
    calls = judges["qwen"].calls
    assert len(calls) == 2 * (7 * 8 + 18 + 18) + 2 * (18 + 18)
    sets = [c["task"].split(":", 1)[1] for c in calls[:2 * (7 * 8 + 36)]]
    assert sets == sorted(sets, key=RZ.SET_ORDER.index) and sets[0] == "ctl_flat" and sets[-1] == "look_alt"
    assert all(c["system_prompt"] == RZ.SYSTEM_PROMPT and c["labels"] == ["Image 1:", "Image 2:"]
               and c["prompt"] == RZ.PROMPT and c["seed"] == 0 for c in calls)
    assert judges["qwen"].url == "http://x:8001/v1"
    first = calls[0]
    assert first["names"] == [f"ctl_flat/renders/{Path(first['images'][0]).name}",
                              f"ab/renders/{Path(first['images'][1]).name}"]                # ab: A first
    assert calls[1]["images"] == list(reversed(first["images"]))                              # ba: B first
    # Answers file: M5 AnswerStore format, call keys per pair and order, cues de-duplicated.
    ans = read(p1 / "check" / "realism" / "answers_qwen3-vl-8b.json")
    assert ans["model"] == "fake/qwen" and ans["slug"] == "qwen3-vl-8b" and ans["incomplete"] is False
    rec = ans["calls"]["realism|m5_vs_m6:cam_r0_1|ab"]
    assert rec["prompt_kind"] == "realism" and rec["image_kind"] == "m5_vs_m6" and rec["order"] == "ab"
    assert rec["camera"] == "cam_r0_1" and rec["labels"] == {"image_1": "a", "image_2": "b"}
    assert rec["images"] == ["../../ab/m5/cam_r0_1_preview.jpg", "../../ab/renders/cam_r0_1_preview.jpg"]
    assert rec["data"]["photo"]["winner"] == "image_2" and rec["data"]["photo"]["cues"] == ["material_texture",
                                                                                           "contact_shadows"]
    assert ans["calls"]["realism|m5_vs_m6:cam_r0_1|ba"]["labels"] == {"image_1": "b", "image_2": "a"}
    # Per project: outcomes and statistics, controls table for the control project, no decision.
    ab1 = read(p1 / "check" / "realism" / "realism_ab.json")
    jsonschema.validate(ab1, S.realism_ab_schema())
    assert keys_named(ab1, "decision") == []
    assert "**" not in (p1 / "check" / "realism" / "realism_report.md").read_text(encoding="utf-8")
    assert ab1["controls"]["signal"] == {"qwen": True, "glm": False}
    row = next(r for r in ab1["rows"] if r["pair_id"] == "m5_vs_m6:cam_r0_1")
    assert row["models"]["qwen"]["aspects"]["photo"]["outcome"] == "W" and row["models"]["qwen"]["calls"] == {
        "ab": "answered", "ba": "answered"}
    assert row["models"]["glm"]["aspects"]["photo"]["outcome"] == "T" and row["consensus"]["photo"] == "T"
    assert ab1["sets"]["m5_vs_m6"]["aspects"]["photo"]["models"]["qwen"]["mean_graded"] == 6.0
    assert ab1["models"]["glm"]["position_bias"]["index"] == 1.0
    assert {c["status"] for c in ab1["calls"]} == {"complete"}
    ab2 = read(p2 / "check" / "realism" / "realism_ab.json")
    assert ab2["controls"] is None and set(ab2["sets"]) == {"m5_vs_m6", "look_alt"}
    # Contact sheets: rows A | B | outcomes, <= 300 KB each, 10 pairs per sheet.
    sheets = ab1["contact_sheets"]
    assert sheets["m5_vs_m6"] == ["contact_realism_m5_vs_m6_1.jpg", "contact_realism_m5_vs_m6_2.jpg"]
    assert sheets["ctl_flat"] == ["contact_realism_ctl_flat_1.jpg"] and len(sheets) == 9
    for names in sheets.values():
        for name in names:
            path = p1 / "check" / "realism" / name
            assert path.stat().st_size <= 300_000
            with Image.open(path) as img:
                assert img.format == "JPEG" and img.width > 2 * RZ.THUMB_W
    # Summary: glm has no signal -> the consensus is qwen alone (single_model); M6 better, look_alt not.
    summary = read(dest / "realism_summary.json")
    jsonschema.validate(summary, S.realism_summary_schema())
    assert summary["signal"] == {"qwen": True, "glm": False} and summary["single_model"] is True
    assert summary["consensus_models"] == ["qwen"] and summary["measurable"] is True
    m5 = summary["sets"]["m5_vs_m6"]
    assert m5["decision"] == "better" and m5["single_model"] is True and m5["pairs"] == 36 and m5["rooms"] == 12
    assert m5["aspects"]["photo"]["consensus"] == {"W": 36, "L": 0, "T": 0, "NC": 0}
    assert m5["aspects"]["photo"]["net_win_ci95"] == [1.0, 1.0] and m5["projects"] == ["synthetic-01", "synthetic-03"]
    assert summary["sets"]["look_alt"]["decision"] == "no_detectable_difference"
    assert "no signal from GLM" in summary["notes"]
    assert summary["controls_project"] == "synthetic-01" and summary["controls"]["sets"]["ctl_flat"]["pairs"] == 8
    assert summary["ev_flags"]["active"] is False                       # the smart judge ignores brightness
    assert summary["position_bias"]["glm"]["index"] == 1.0
    assert summary["top_cues"]["m5_vs_m6"]["photo"] == {"W": [["contact_shadows", 72], ["material_texture", 72]],
                                                         "L": []}                    # ties by name, repeats removed
    md = (dest / "realism_summary.md").read_text(encoding="utf-8")
    header = next(line for line in spec_section("### 6.3").splitlines() if line.startswith("| Aspect |"))
    assert header in md and RZ.table_header(MODELS)[0] == header
    assert "| m5_vs_m6 | **better** | yes | 36 | 12 |" in md and "## Controls (synthetic-01)" in md
    assert "| photo | 36/0/0 (1.00) | 0/0/36 (0.00) | 36/0/0 | 1.00 (36/36) |" in md


def test_end_to_end_two_models_with_signal_and_none(tmp_path):
    judges = {"qwen": FakeJudge("fake/qwen"), "glm": FakeJudge("fake/glm")}
    _, _, dest = run_all(tmp_path / "both", judges)
    summary = read(dest / "realism_summary.json")
    assert summary["signal"] == {"qwen": True, "glm": True} and summary["single_model"] is False
    assert summary["sets"]["m5_vs_m6"]["decision"] == "better"
    assert summary["controls"]["sets"]["null_identical"]["models"]["qwen"]["tie_rate"] == 1.0
    judges = {"qwen": FakeJudge("fake/qwen", blind=True), "glm": FakeJudge("fake/glm", blind=True)}
    _, _, dest = run_all(tmp_path / "none", judges)
    summary = read(dest / "realism_summary.json")
    assert summary["measurable"] is False and summary["single_model"] is False
    assert {st["decision"] for st in summary["sets"].values()} == {"not_measurable"}
    assert "not measurable: the controls fail for every model" in summary["notes"]


def test_summary_without_controls_or_projects(tmp_path, capsys):
    out = write_ab(tmp_path, "solo", rooms=2, per_room=1)
    judges = {"qwen": FakeJudge("fake/qwen"), "glm": FakeJudge("fake/glm")}
    assert main(["realism-pairs", "--project-out", str(out)]) == 0
    for key in MODELS:
        assert main(["realism", "--project-out", str(out), "--model-key", key], client_factory=factory_for(judges)) == 0
    assert main(["realism-combine", "--project-out", str(out), "--models", "qwen glm", "--no-debug"]) == 0
    assert not list((out / "check" / "realism").glob("contact_*.jpg"))
    dest = tmp_path / "r"
    assert main(["realism-summary", "--project-outs", f"{out},{tmp_path / 'missing'}", "--out", str(dest),
                 "--controls-project", "nope", "--models", "qwen,glm"]) == 0
    summary = read(dest / "realism_summary.json")
    assert summary["measurable"] is False and summary["controls"] is None
    assert [p["found"] for p in summary["projects"]] == [True, False]
    assert any("controls project nope" in w for w in summary["warnings"])
    assert main(["realism-summary", "--project-outs", str(tmp_path / "missing"), "--out", str(dest)]) == 1
    assert (dest / "realism_summary.md").is_file()


# --------------------------------------------------------------------------
# Resumable answers, deadline, set selection, stale answers
# --------------------------------------------------------------------------

def test_answers_are_resumable(tmp_path):
    out = write_ab(tmp_path, "proj", rooms=2, per_room=2)
    judge = FakeJudge("fake/qwen")
    judges = {"qwen": judge}
    args = ["realism", "--project-out", str(out), "--model-key", "qwen"]
    assert main(["realism-pairs", "--project-out", str(out)]) == 0
    assert main(args, client_factory=factory_for(judges)) == 0
    assert len(judge.calls) == 2 * (4 + 4)
    assert main(args, client_factory=factory_for(judges)) == 0
    assert len(judge.calls) == 16                                                 # nothing asked again
    # A changed M5 image: only that pair is asked again (both orders), with a warning to re-pair.
    jpeg(out / "ab" / "m5" / "cam_r0_1_preview.jpg", 60)
    assert main(args, client_factory=factory_for(judges)) == 0
    assert [c["task"] for c in judge.calls[16:]] == ["realism:m5_vs_m6"] * 2
    # A failed call is recorded and asked again by the next run.
    judge.fail = {str(out / "ab" / "renders" / "cam_r1_2_alt_preview.jpg")}
    jpeg(out / "ab" / "renders" / "cam_r1_2_alt_preview.jpg", 140)
    assert main(args, client_factory=factory_for(judges)) == 0
    ans = read(out / "check" / "realism" / "answers_qwen3-vl-8b.json")
    assert ans["calls"]["realism|look_alt:cam_r1_2|ab"]["data"] is None
    assert ans["calls"]["realism|look_alt:cam_r1_2|ab"]["error"].startswith("cannot reach")
    judge.fail = set()
    n = len(judge.calls)
    assert main(args, client_factory=factory_for(judges)) == 0
    assert len(judge.calls) == n + 2
    # A changed model id makes every answer stale.
    judges["qwen"] = FakeJudge("fake/qwen-2")
    assert main(args, client_factory=factory_for(judges)) == 0
    assert len(judges["qwen"].calls) == 16


def test_deadline_and_set_selection(tmp_path, capsys):
    out = write_ab(tmp_path, "proj", rooms=2, per_room=2, controls=True)
    assert main(["realism-pairs", "--project-out", str(out), "--controls"]) == 0
    judge = FakeJudge("fake/qwen")
    f = factory_for({"qwen": judge})
    base = ["realism", "--project-out", str(out), "--model-key", "qwen"]
    # Deadline already past: nothing asked, the file says incomplete, exit 0.
    assert main(base + ["--deadline", str(time.time() - 1)], client_factory=f) == 0
    assert judge.calls == [] and "deadline: incomplete" in capsys.readouterr().out
    assert read(out / "check" / "realism" / "answers_qwen3-vl-8b.json")["incomplete"] is True
    # Only ctl_flat: complete there, every other set not started.
    assert main(base + ["--sets", "ctl_flat"], client_factory=f) == 0
    assert {c["task"] for c in judge.calls} == {"realism:ctl_flat"} and len(judge.calls) == 8
    assert read(out / "check" / "realism" / "answers_qwen3-vl-8b.json")["incomplete"] is False
    # Everything but look_alt (the orchestrator near the deadline).
    assert main(base + ["--skip-sets", "look_alt,ctl_flat"], client_factory=f) == 0
    assert "realism:look_alt" not in {c["task"] for c in judge.calls}
    assert main(["realism-combine", "--project-out", str(out), "--models", "qwen", "--no-debug"]) == 0
    calls = {c["set"]: c for c in read(out / "check" / "realism" / "realism_ab.json")["calls"]}
    assert calls["ctl_flat"]["status"] == "complete" and calls["m5_vs_m6"]["status"] == "complete"
    assert calls["look_alt"] == {"project": "proj", "set": "look_alt", "model": "qwen", "expected": 8, "answered": 0,
                                 "failed": 0, "stale": 0, "missing": 8, "answered_rate": 0.0,
                                 "status": "not_started"}
    # A slow judge cut by the deadline: some calls answered, the rest left for the next run.
    slow = FakeJudge("fake/qwen", delay=0.3)
    t0 = time.time()
    assert main(base + ["--sets", "look_alt", "--deadline", str(t0 + 1.0), "--workers", "1"],
                client_factory=factory_for({"qwen": slow})) == 0
    assert time.time() - t0 < 3.0 and 1 <= len(slow.calls) < 8
    assert read(out / "check" / "realism" / "answers_qwen3-vl-8b.json")["incomplete"] is True
    assert main(["realism-combine", "--project-out", str(out), "--models", "qwen", "--no-debug"]) == 0
    calls = {c["set"]: c for c in read(out / "check" / "realism" / "realism_ab.json")["calls"]}
    assert calls["look_alt"]["status"] == "incomplete" and 0 < calls["look_alt"]["answered"] < 8


def test_stale_answers_are_not_used_by_combine(tmp_path):
    out = write_ab(tmp_path, "proj", rooms=1, per_room=2)
    judges = {"qwen": FakeJudge("fake/qwen"), "glm": FakeJudge("fake/glm")}
    assert main(["realism-pairs", "--project-out", str(out)]) == 0
    for key in MODELS:
        assert main(["realism", "--project-out", str(out), "--model-key", key], client_factory=factory_for(judges)) == 0
    jpeg(out / "ab" / "m5" / "cam_r0_2_preview.jpg", 70)
    doc = RZ.combine(out, MODELS)
    row = next(r for r in doc["rows"] if r["pair_id"] == "m5_vs_m6:cam_r0_2")
    assert row["models"]["qwen"]["calls"] == {"ab": "stale", "ba": "stale"}
    assert row["consensus"] == {a: "NC" for a in RZ.ASPECTS}
    assert any("stale answer for realism|m5_vs_m6:cam_r0_2|ab" in w for w in doc["warnings"])
    assert any("changed after realism-pairs" in w for w in doc["warnings"])
    other = next(r for r in doc["rows"] if r["pair_id"] == "m5_vs_m6:cam_r0_1")
    assert other["consensus"]["photo"] == "W"
    # A deleted image: the pair is not computed, never a tie or a loss.
    (out / "ab" / "renders" / "cam_r0_1_alt_preview.jpg").unlink()
    doc = RZ.combine(out, MODELS)
    row = next(r for r in doc["rows"] if r["pair_id"] == "look_alt:cam_r0_1")
    assert row["models"]["glm"]["calls"] == {"ab": "missing", "ba": "missing"} and row["consensus"]["photo"] == "NC"


# --------------------------------------------------------------------------
# CLI usage, report formats, config
# --------------------------------------------------------------------------

def test_cli_usage_errors(tmp_path, capsys):
    out = write_ab(tmp_path, "proj", rooms=1, per_room=1)
    f = factory_for({"qwen": FakeJudge()})
    assert main(["realism", "--project-out", str(out), "--model-key", "qwen"], client_factory=f) == 1   # no pairs
    assert main(["realism-combine", "--project-out", str(out)]) == 1
    assert main(["realism-pairs", "--project-out", str(out)]) == 0
    assert main(["realism", "--project-out", str(out), "--model-key", "llava"], client_factory=f) == 2
    assert main(["realism", "--project-out", str(out), "--model-key", "qwen", "--sets", "bogus"],
                client_factory=f) == 2
    assert main(["realism-combine", "--project-out", str(out), "--models", "qwen,llava"]) == 2
    assert main(["realism-summary", "--project-outs", str(out), "--out", str(tmp_path / "r"),
                 "--models", "llava"]) == 2
    with pytest.raises(SystemExit) as exc:
        main(["realism-summary", "--project-outs", str(out)])                      # no --out
    assert exc.value.code == 2
    with pytest.raises(SystemExit) as exc:
        main(["realism-pairs"])                                                    # no --project-out
    assert exc.value.code == 2
    assert RZ.select_sets("look_alt, m5_vs_m6") == ["m5_vs_m6", "look_alt"]
    assert RZ.select_sets(None, "look_alt") == list(RZ.SET_ORDER[:-1])


def test_report_formats():
    assert RZ._fmt_ci([None, None]) == "-" and RZ._fmt_ci([-0.05, 0.4]) == "[-0.05, +0.40]"
    assert RZ._fmt_p(0.0427739) == "0.0428" and RZ._fmt_p(None) == "-"
    st = {"models": {"qwen": {"W": 3, "L": 1, "T": 2, "NC": 1, "consistency": 0.6667, "mean_graded": 1.5}},
          "consensus": {"W": 3, "L": 1, "T": 2, "NC": 0}, "n": 6, "win_rate": 0.5, "sign_p": 0.625,
          "net_win_ci95": [0.0, 0.5]}
    assert RZ.table_row("photo", st, ["qwen"]) == \
        "| photo | 3/1/2 (0.67; NC 1) | 3/1/2 | 0.50 (3/6) | 0.625 | [+0.00, +0.50] | +1.50 |"
    assert RZ.table_header(["qwen"])[0] == ("| Aspect | Qwen W/L/T (consistency) | Consensus W/L/T | Win rate W/N | "
                                            "Sign p | Net win 95 % (rooms) | Mean graded Qwen |")


def test_check_yaml_realism_block():
    from wenart.vision_check.config import load_config
    block = load_config()["realism"]
    assert (block["min_decisive"], block["min_rooms"], block["control_views"]) == (30, 10, 8)
    assert (block["alpha"], block["bootstrap_resamples"], block["bootstrap_seed"], block["reencode_quality"]) == \
        (0.05, 2000, 0, 70)
    assert block["targets"] == {"correct_min": 0.70, "wrong_max": 0.05, "consensus_correct_min": 0.60,
                                "null_identical_tie_min": 0.90, "null_reencode_win_max": 0.10,
                                "nuisance_brighter_max": 0.30, "delta_ev_flag": 0.3, "halo_max": 0.80}
    assert RZ.realism_cfg() == {**RZ.DEFAULTS, "targets": RZ.DEFAULTS["targets"]}
    assert RZ.realism_cfg({"models": {}}) == RZ.DEFAULTS
    assert RZ.realism_cfg({"realism": {"min_rooms": 5, "targets": {"wrong_max": 0.1}}})["targets"]["wrong_max"] == 0.1
