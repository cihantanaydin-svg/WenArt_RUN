"""GPU tests of the realism A/B v2 (docs/milestone7.md §8.2, §11 GPU; the M6 protocol of docs/milestone6.md §6
ran in Milestone 6 and its results are committed, its files are not written by M7 runs).

Run on the pod by scripts/jobs/full.sh after the last server stopped:
``pytest -m gpu tests/gpu/test_realism.py``. They only read what the run wrote:

- per project of ``$AB_TEST_PROJECTS`` (the A/B projects, exported by the orchestrator; empty ->
  every test is skipped, so a test never falls back to old outputs on the volume) and the control
  project ``$AB_CONTROL_PROJECT`` (default: the summary's), under ``$WENART_OUTPUTS`` (default
  /workspace/repo/outputs): ``ab/pairs_v2.json``, ``check/realism/answers_realism2_<slug>.json`` and
  ``check/realism/realism2_ab.json``;
- ``realism2_summary.json`` at ``$REALISM2_SUMMARY``, default
  ``$WENART_RESULTS/realism/realism2_summary.json`` (``realism2-summary --out $RESULTS/realism``);
- the model keys of ``$CHECK_MODELS`` (default ``qwen glm``).

Checks:

- ``realism2_summary.json`` is valid (``schemas.realism_summary_schema(2)``), found every A/B test
  project and gives a decision for ``look_alt`` (``not_measurable`` exactly when no model has signal);
- every model answered >= 95 % of its calls over every set (8 calls per pair: 4 aspects x 2 orders;
  ``look_alt`` is the decided set in v2 and counts), its answers file names the pinned model id;
- the pair files are valid v2 files with unique pair ids; the A/B projects together hold at most
  ``check.yaml realism2.look_alt_cameras`` look_alt pairs, at most 2 per room;
- the controls table is present (the four ``ctl_*`` sets, the null and nuisance sets, a signal flag
  per model); ``null_identical`` ties and flips are recorded and a model that misses a null target
  has no signal (a measurement of the judges, printed, not asserted beyond the rule).
"""
import json
import os
from collections import Counter
from pathlib import Path

import jsonschema
import pytest

from wenart.vision_check import realism as RZ
from wenart.vision_check import schemas as S
from wenart.vision_check.config import load_config

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("AB_TEST_PROJECTS", "").replace(",", " ").split() if p]
CONTROL = os.environ.get("AB_CONTROL_PROJECT", "").strip()
MODEL_KEYS = [k for k in os.environ.get("CHECK_MODELS", "qwen glm").replace(",", " ").split() if k]

MIN_ANSWER_RATE = 0.95
NULL_IDENTICAL_TIE_MIN = 0.90
CONTROL_SETS = ("ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp")
OTHER_CONTROL_SETS = ("null_identical", "null_reencode", "nuisance_ev")

needs_projects = pytest.mark.skipif(not PROJECTS, reason="AB_TEST_PROJECTS is empty: no realism A/B in this run")


def summary_path() -> Path:
    if os.environ.get("REALISM2_SUMMARY"):
        return Path(os.environ["REALISM2_SUMMARY"])
    results = os.environ.get("WENART_RESULTS")
    assert results, "set REALISM2_SUMMARY or WENART_RESULTS (realism2-summary writes $RESULTS/realism/)"
    return Path(results) / "realism" / RZ.V2.summary_json


def _load(path: Path) -> dict:
    assert path.is_file(), f"{path} missing: did the realism A/B v2 run? (AB_TEST_PROJECTS={' '.join(PROJECTS)})"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary():
    return _load(summary_path())


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def all_projects(summary=None) -> list[str]:
    control = CONTROL or ((summary or {}).get("controls_project") or "")
    return list(dict.fromkeys(PROJECTS + ([control] if control else [])))


@pytest.fixture(scope="module", params=list(dict.fromkeys(PROJECTS + ([CONTROL] if CONTROL and PROJECTS else [])))
                or ["-"])
def project(request):
    return request.param


@needs_projects
def test_summary_is_valid(summary):
    jsonschema.validate(summary, S.realism_summary_schema(2))
    found = {p["project"] for p in summary["projects"] if p["found"]}
    assert set(PROJECTS) <= found, f"projects without realism2_ab.json: {sorted(set(PROJECTS) - found)}"
    assert set(summary["sets"]) == {"look_alt"}, f"sets decided: {sorted(summary['sets'])}"
    for name, st in summary["sets"].items():
        assert st["decision"] in S.REALISM_DECISIONS
        assert (st["decision"] == "not_measurable") is (not summary["measurable"]), name
        assert st["single_model"] is summary["single_model"]
    assert summary["measurable"] is any(summary["signal"].values())
    decisions = ", ".join(f"{name} {st['decision']}" for name, st in summary["sets"].items())
    print(f"realism v2 decisions: {decisions}; signal {summary['signal']}; notes {summary['notes']}")


@needs_projects
def test_pair_files_are_valid_and_look_alt_has_its_32_cameras(summary, cfg):
    limit = int(RZ.realism2_cfg(cfg)["look_alt_cameras"])
    look_alt = []
    for name in all_projects(summary):
        pairs = _load(OUTPUTS / name / RZ.V2.pairs_json)
        jsonschema.validate(pairs, S.realism_pairs_file_schema(2))
        ids = [p["pair_id"] for p in pairs["pairs"]]
        assert len(ids) == len(set(ids)), f"{name}: duplicate pair ids"
        look_alt += [(name, p) for p in pairs["pairs"] if p["set"] == "look_alt"]
    assert 0 < len(look_alt) <= limit, f"{len(look_alt)} look_alt pairs (limit {limit})"
    rooms = Counter((name, p["room_id"] or p["cam"]) for name, p in look_alt)
    assert max(rooms.values()) <= int(RZ.realism2_cfg(cfg)["look_alt_per_room"]), rooms.most_common(3)
    print(f"look_alt: {len(look_alt)} pairs over {len({n for n, _ in look_alt})} project(s)")


@needs_projects
def test_every_model_answered_its_calls(project, cfg):
    """Every A/B project and the control project (``$AB_CONTROL_PROJECT``)."""
    ab = _load(OUTPUTS / project / "check" / "realism" / RZ.V2.ab_json)
    for key in MODEL_KEYS:
        model = cfg["models"][key]
        answers = _load(RZ.answers_path(OUTPUTS / project, model["slug"], RZ.V2))
        assert answers.get("model") == model["id"], \
            f"{project}: answers_realism2_{model['slug']}.json names {answers.get('model')}"
        calls = [c for c in ab["calls"] if c["model"] == key]
        assert calls, f"{project}: no realism2 call of {key}"
        assert all(c["expected"] % RZ.V2.calls_per_pair == 0 for c in calls)
        expected = sum(c["expected"] for c in calls)
        answered = sum(c["answered"] for c in calls)
        short = [f"{c['set']} {c['answered']}/{c['expected']} ({c['status']})" for c in calls
                 if c["answered"] < c["expected"]]
        assert answered / expected >= MIN_ANSWER_RATE, \
            f"{project}: {key} answered {answered / expected:.1%} of {expected} calls; {short}"


@needs_projects
def test_controls_table_present(summary):
    controls = summary["controls"]
    assert controls is not None, f"no controls in the summary (controls project {summary['controls_project']})"
    if CONTROL:
        assert summary["controls_project"] == CONTROL, summary["controls_project"]
    for name in CONTROL_SETS + OTHER_CONTROL_SETS:
        assert name in controls["sets"], f"controls table lacks {name}"
        assert controls["sets"][name]["pairs"] > 0, f"no {name} pairs"
    for name in CONTROL_SETS:
        for key in MODEL_KEYS:
            assert key in controls["sets"][name]["models"], f"{name}: no entry for {key}"
    assert set(MODEL_KEYS) <= set(controls["signal"]), controls["signal"]
    print(f"halo (one aspect per call): {controls['halo']}")


@needs_projects
def test_null_controls_are_recorded_and_decide_the_signal(summary):
    """The null sets measure the judges: each model's null_identical ties (every flip listed, asked one call at a
    time) and null_reencode wins are recorded, and a model that misses a null target has no signal."""
    controls = summary["controls"]
    assert controls is not None, "no controls in the summary"
    asked = {k: v for k, v in controls["sets"]["null_identical"]["models"].items() if k in MODEL_KEYS and v["n"] > 0}
    assert asked, "null_identical: no model has answers"
    for key, v in asked.items():
        assert len(v["flips"]) == v["n"] - v["tie"], key
        assert v["pass"] == (v["tie_rate"] >= NULL_IDENTICAL_TIE_MIN), key
        if v["flips"]:
            print(f"null_identical {key} T {v['tie_rate']:.0%}; flips: {', '.join(v['flips'])}")
        reenc = controls["sets"]["null_reencode"]["models"][key]
        if not (v["pass"] and (reenc["n"] == 0 or reenc["pass"])):
            assert controls["signal"][key] is False, f"{key} misses a null target but has signal"
