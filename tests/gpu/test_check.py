"""Milestone 5 GPU tests of the final vision check (docs/milestone5.md §5, §6, §9).

Run on the pod by scripts/jobs/polish.sh (tests phase): ``pytest -m gpu tests/gpu/test_check.py``.
They only read what the check phase wrote under $WENART_OUTPUTS (default
/workspace/repo/outputs) for the projects in $CHECK_TEST_PROJECTS (the job exports the
projects whose check ran or whose ``check/check_manifest.json`` exists; default synthetic-01
synthetic-03), with the model keys of $CHECK_MODELS (default ``qwen glm``):

- every model answered >= 95 % of its calls (``check/answers_<slug>.json``: an answer is a call
  with data and no error) and the file names the model id of ``check.yaml``;
- ``check/check_calibration.json`` is present with the targets of ``check.yaml``;
- ``advisory`` is set exactly when a target is missed: recomputed here from the calibration
  metrics and the ``check.yaml`` targets (a metric without data counts as missed; a single-model
  check is always advisory), and ``check_manifest.json`` carries the same flag;
- ``check/style_photo_test.json`` (each model read ``tests/fixtures/style_photo_synthetic-03_salon.jpg``,
  §6): every model gives walls ``plaster_charcoal`` and floor ``concrete_polished``;
- insertion measured in every run (docs/milestone7.md §8.1, the check runs ``--kinds
  cycles,polished,controls``): a project whose ``check/controls.json`` lists controls has every
  insertion control in ``check_manifest.json`` and an insertion rate in the calibration (two
  models); when the ``detect`` stage detected control renders, the detector's insertion rate
  (``detector_insertion``) is recorded too. The rates are printed, never asserted (they are
  measurements of the judges).
"""
import json
import os
from pathlib import Path

import pytest

from wenart.vision_check.config import load_config

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("CHECK_TEST_PROJECTS", "synthetic-01 synthetic-03").split() if p]
MODEL_KEYS = [k for k in os.environ.get("CHECK_MODELS", "qwen glm").split() if k]
# The projects whose detect stage ran in this run (the orchestrator's list); None when run by hand (every project).
DETECT_RAN = (None if "DETECT_TEST_PROJECTS" not in os.environ
              else set(os.environ["DETECT_TEST_PROJECTS"].split()))

MIN_ANSWER_RATE = 0.95
STYLE_PHOTO_EXPECTED = {"walls": "plaster_charcoal", "floor": "concrete_polished"}


def _load(project: str, rel: str) -> dict:
    path = OUTPUTS / project / rel
    assert path.is_file(), (f"{path} missing: did the check phase run for {project}? "
                            f"(CHECK_TEST_PROJECTS={' '.join(PROJECTS)}, CHECK_MODELS={' '.join(MODEL_KEYS)})")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cfg():
    return load_config()


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    return request.param


def answered(call: dict) -> bool:
    """A call counts as answered when it has data and no error."""
    return isinstance(call, dict) and call.get("data") is not None and not call.get("error")


def target_metric(target: str) -> tuple[str, str]:
    """``(metric, op)`` of a ``check.yaml`` target key: ``fa_missing_max`` -> (``fa_missing``, ``<=``)."""
    if target.endswith("_max"):
        return target[:-4], "<="
    if target.endswith("_min"):
        return target[:-4], ">="
    raise ValueError(f"target {target!r} ends neither in _max nor in _min")


def metric_values(metrics: dict, name: str) -> dict:
    """``{label: value}`` of one metric: a plain number, a per-model mapping, or per model under
    ``metrics.models.<key>.<name>`` (the decoy acceptance is measured per model)."""
    value = metrics.get(name)
    if isinstance(value, dict):
        return {f"{name}[{k}]": v for k, v in value.items()}
    if value is not None or name in metrics:
        return {name: value}
    models = metrics.get("models") or {}
    per_model = {f"{name}[{k}]": m.get(name) for k, m in models.items() if isinstance(m, dict)}
    return per_model or {name: None}


def expected_missed(metrics: dict, targets: dict) -> dict:
    """``{target: [metric labels that miss it]}``; a missing value (no data) misses."""
    out = {}
    for target, limit in targets.items():
        metric, op = target_metric(target)
        bad = []
        for label, value in metric_values(metrics, metric).items():
            ok = value is not None and (value <= limit if op == "<=" else value >= limit)
            if not ok:
                bad.append(label)
        if bad:
            out[target] = bad
    return out


def recorded_names(missed: list) -> set:
    """Target and metric names of the calibration's ``missed`` list (entries are mappings or names)."""
    names = set()
    for m in missed or []:
        if isinstance(m, str):
            names.add(m)
        elif isinstance(m, dict):
            names.update(str(m[k]) for k in ("target", "metric") if m.get(k) is not None)
    return names


def style_passes(doc) -> dict:
    """``{model_key: [answer dicts]}`` of every pass record (``{model_key, data}``) anywhere in ``doc``."""
    out: dict = {}

    def walk(node):
        if isinstance(node, dict):
            if "model_key" in node and isinstance(node.get("data"), dict) and not node.get("error"):
                out.setdefault(str(node["model_key"]), []).append(node["data"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(doc)
    return out


def test_every_model_answered_its_calls(project, cfg):
    for key in MODEL_KEYS:
        model = cfg["models"][key]
        data = _load(project, f"check/answers_{model['slug']}.json")
        assert data.get("model") == model["id"], f"{project}: answers_{model['slug']}.json names {data.get('model')}"
        calls = data.get("calls") or {}
        calls = list(calls.values()) if isinstance(calls, dict) else list(calls)
        assert calls, f"{project}: no call recorded for {key}"
        rate = sum(answered(c) for c in calls) / len(calls)
        errors = sorted({str(c.get("error"))[:80] for c in calls if not answered(c)})
        assert rate >= MIN_ANSWER_RATE, f"{project}: {key} answered {rate:.1%} of {len(calls)} calls; errors {errors[:5]}"


def test_calibration_present(project, cfg):
    cal = _load(project, "check/check_calibration.json")
    for key in ("metrics", "targets", "missed", "advisory"):
        assert key in cal, f"{project}: check_calibration.json lacks {key}"
    assert {k: float(v) for k, v in cal["targets"].items()} == \
        {k: float(v) for k, v in cfg["targets"].items()}, f"{project}: calibration targets are not check.yaml's"
    manifest = _load(project, "check/check_manifest.json")
    assert manifest.get("advisory") == cal["advisory"], f"{project}: check_manifest.json advisory differs"


def test_advisory_set_exactly_when_a_target_is_missed(project, cfg):
    cal = _load(project, "check/check_calibration.json")
    missed = expected_missed(cal["metrics"], cfg["targets"])
    single = bool(cal.get("single_pass")) or len(MODEL_KEYS) < 2
    assert cal["advisory"] is (bool(missed) or single), \
        f"{project}: advisory={cal['advisory']} but missed targets {missed} (single pass {single})"
    names = recorded_names(cal["missed"])
    for target, labels in missed.items():
        assert target in names or any(label in names for label in labels), \
            f"{project}: target {target} is missed ({labels}) but not listed in check_calibration.json missed"


def test_style_photo_test(project):
    passes = style_passes(_load(project, "check/style_photo_test.json"))
    for key in MODEL_KEYS:
        answers = passes.get(key)
        assert answers, f"{project}: no answer of {key} on the style test photo"
        got = {slot: answers[-1].get(slot) for slot in STYLE_PHOTO_EXPECTED}
        assert got == STYLE_PHOTO_EXPECTED, f"{project}: {key} read {got}, expected {STYLE_PHOTO_EXPECTED}"


def test_insertion_measured(project, cfg):
    controls = _load(project, "check/controls.json").get("controls") or []
    rendered = [c for c in controls if (OUTPUTS / project / c["dir"] / "render_manifest.json").is_file()]
    if not rendered:
        pytest.skip(f"{project}: no rendered insertion control")
    manifest = _load(project, "check/check_manifest.json")
    kinds = {kind for v in manifest["views"].values() for kind in v if kind.startswith("insertion:")}
    missing = sorted({"insertion:" + c["id"] for c in rendered} - kinds)
    assert not missing, f"{project}: insertion controls not checked (--kinds without controls?): {missing}"
    cal = _load(project, "check/check_calibration.json")
    ins = cal["metrics"]["controls"]["insertion"]
    assert ins["n"] >= len(rendered), f"{project}: {ins['n']} insertion rows for {len(rendered)} controls"
    single = bool(cal.get("single_pass")) or len(MODEL_KEYS) < 2
    assert (cal["metrics"]["insertion"] is None) is single, f"{project}: insertion rate {cal['metrics']['insertion']}"
    det = cal["metrics"].get("detector_insertion") or {}
    # M8 F1: real01's gate disabled the polish, so its detect stage did not run; the detect/*.json files of an earlier
    # run (M7) are on the volume and must not count.
    ran = DETECT_RAN is None or project in DETECT_RAN
    detected = ran and any(json.loads(f.read_text(encoding="utf-8")).get("controls")
                           for f in (OUTPUTS / project / "detect").glob("*.json") if f.name != "detect_manifest.json")
    if detected:
        assert det.get("n", 0) > 0, f"{project}: control renders were detected but no detector insertion recorded"
    print(f"{project}: insertion VLM {cal['metrics']['insertion']} ({ins['n']} controls); detector found "
          f"{det.get('found')} flagged {det.get('flagged')} confirmed {det.get('confirmed')} ({det.get('n', 0)})")
