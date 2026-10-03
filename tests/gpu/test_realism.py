"""Milestone 6 GPU tests of the realism A/B (docs/milestone6.md §6, §9).

Run on the pod by scripts/jobs/full.sh after the last server stopped:
``pytest -m gpu tests/gpu/test_realism.py``. They only read what the run wrote:

- per project of ``$AB_TEST_PROJECTS`` (exported by the orchestrator; empty -> every test is
  skipped, so a test never falls back to old outputs on the volume), under ``$WENART_OUTPUTS``
  (default /workspace/repo/outputs): ``ab/pairs.json``, ``check/realism/answers_<slug>.json``
  and ``check/realism/realism_ab.json``;
- ``realism_summary.json`` at ``$REALISM_SUMMARY``, default
  ``$WENART_RESULTS/realism/realism_summary.json`` (``realism-summary --out $RESULTS/realism``);
- the model keys of ``$CHECK_MODELS`` (default ``qwen glm``).

Checks:

- ``realism_summary.json`` is valid (``schemas.realism_summary_schema``), found every A/B test
  project and gives a decision for ``m5_vs_m6`` (``not_measurable`` exactly when no model has signal);
- every model answered >= 95 % of its calls over the sets that were started (counted by
  ``realism-combine``, which leaves out stale answers); ``look_alt`` is not counted: its state
  (complete, cut by the deadline, not started) is printed;
- the controls table is present for the control project: the four ``ctl_*`` sets, the null and
  nuisance sets, a signal flag per model;
- ``null_identical``: every model with answers gives T on >= 90 % of the pair-aspects (flips printed).
"""
import json
import os
from pathlib import Path

import jsonschema
import pytest

from wenart.vision_check import schemas as S
from wenart.vision_check.config import load_config

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("AB_TEST_PROJECTS", "").replace(",", " ").split() if p]
MODEL_KEYS = [k for k in os.environ.get("CHECK_MODELS", "qwen glm").replace(",", " ").split() if k]

MIN_ANSWER_RATE = 0.95
NULL_IDENTICAL_TIE_MIN = 0.90
NOT_COUNTED = ("look_alt",)          # asked last, skipped or cut at the deadline: reported, never counted
CONTROL_SETS = ("ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp")
OTHER_CONTROL_SETS = ("null_identical", "null_reencode", "nuisance_ev")

needs_projects = pytest.mark.skipif(not PROJECTS, reason="AB_TEST_PROJECTS is empty: no realism A/B in this run")


def summary_path() -> Path:
    if os.environ.get("REALISM_SUMMARY"):
        return Path(os.environ["REALISM_SUMMARY"])
    results = os.environ.get("WENART_RESULTS")
    assert results, "set REALISM_SUMMARY or WENART_RESULTS (realism-summary writes $RESULTS/realism/)"
    return Path(results) / "realism" / "realism_summary.json"


def _load(path: Path) -> dict:
    assert path.is_file(), f"{path} missing: did the realism A/B run? (AB_TEST_PROJECTS={' '.join(PROJECTS)})"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def summary():
    return _load(summary_path())


@pytest.fixture(scope="module")
def cfg():
    return load_config()


@pytest.fixture(scope="module", params=PROJECTS or ["-"])
def project(request):
    return request.param


@needs_projects
def test_summary_is_valid(summary):
    jsonschema.validate(summary, S.realism_summary_schema())
    found = {p["project"] for p in summary["projects"] if p["found"]}
    assert set(PROJECTS) <= found, f"projects without realism_ab.json: {sorted(set(PROJECTS) - found)}"
    assert "m5_vs_m6" in summary["sets"], "no m5_vs_m6 pairs in the summary"
    for name, st in summary["sets"].items():
        assert st["decision"] in S.REALISM_DECISIONS
        assert (st["decision"] == "not_measurable") is (not summary["measurable"]), name
        assert st["single_model"] is summary["single_model"]
    assert summary["measurable"] is any(summary["signal"].values())
    decisions = ", ".join(f"{name} {st['decision']}" for name, st in summary["sets"].items())
    print(f"realism decisions: {decisions}; signal {summary['signal']}; notes {summary['notes']}")


@needs_projects
def test_pairs_files_are_valid(project):
    pairs = _load(OUTPUTS / project / "ab" / "pairs.json")
    jsonschema.validate(pairs, S.realism_pairs_file_schema())
    ids = [p["pair_id"] for p in pairs["pairs"]]
    assert len(ids) == len(set(ids)), f"{project}: duplicate pair ids"


@needs_projects
def test_every_model_answered_the_started_sets(project, cfg):
    ab = _load(OUTPUTS / project / "check" / "realism" / "realism_ab.json")
    for key in MODEL_KEYS:
        model = cfg["models"][key]
        answers = _load(OUTPUTS / project / "check" / "realism" / f"answers_{model['slug']}.json")
        assert answers.get("model") == model["id"], \
            f"{project}: answers_{model['slug']}.json names {answers.get('model')}"
        calls = [c for c in ab["calls"] if c["model"] == key]
        for c in calls:
            if c["set"] in NOT_COUNTED:
                print(f"{project} {key} {c['set']}: {c['status']} ({c['answered']}/{c['expected']} answered; "
                      "not counted)")
        started = [c for c in calls if c["set"] not in NOT_COUNTED and c["status"] != "not_started"]
        assert any(c["set"] == "m5_vs_m6" for c in started), f"{project}: {key} never started m5_vs_m6"
        expected = sum(c["expected"] for c in started)
        answered = sum(c["answered"] for c in started)
        rate = answered / expected
        short = [f"{c['set']} {c['answered']}/{c['expected']} ({c['status']})" for c in started
                 if c["answered"] < c["expected"]]
        assert rate >= MIN_ANSWER_RATE, f"{project}: {key} answered {rate:.1%} of {expected} calls; {short}"


@needs_projects
def test_controls_table_present(summary):
    controls = summary["controls"]
    assert controls is not None, f"no controls in the summary (controls project {summary['controls_project']})"
    assert summary["controls_project"] in PROJECTS, summary["controls_project"]
    for name in CONTROL_SETS + OTHER_CONTROL_SETS:
        assert name in controls["sets"], f"controls table lacks {name}"
        assert controls["sets"][name]["pairs"] > 0, f"no {name} pairs"
    for name in CONTROL_SETS:
        for key in MODEL_KEYS:
            assert key in controls["sets"][name]["models"], f"{name}: no entry for {key}"
    assert set(MODEL_KEYS) <= set(controls["signal"]), controls["signal"]


@needs_projects
def test_null_controls_are_recorded_and_decide_the_signal(summary):
    """The null sets are a measurement of the judges, not of our code: each model's null_identical ties (with
    every flip listed) and null_reencode wins are recorded, and a model that misses a null target has no signal
    (M6 pod C: GLM tied 88 % of the identical pair-aspects, target 90 %)."""
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