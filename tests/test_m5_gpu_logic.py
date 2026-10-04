"""CPU tests of the Milestone 5 GPU test logic (tests/gpu/test_polish.py, tests/gpu/test_check.py).

The GPU test modules are imported with their environment pointing at hand-made outputs in
tmp_path (they read the environment at import, like tests/test_blender_render.py does for
test_render.py) and their test functions are called directly: a good set of files passes, and
each defect the GPU tests exist for (a wrong image size, an accepted attempt that the current
thresholds fail, a rejected attempt without reasons, a stale render, a gate calibration short of
its targets, non-deterministic output, an unanswered model, a missed target without the advisory
flag, a wrong style-photo reading) fails with an AssertionError.

``wenart.gate.decide`` is replaced by a small fake with the §4.2 semantics, so these tests do not
depend on the gate implementation; one test also runs the real ``decide`` when it exists.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from wenart import views as V
from wenart.gate.api import load_models_config, load_thresholds
from wenart.polish.config import load_config as load_polish_config
from wenart.vision_check.config import load_config as load_check_config

ROOT = Path(__file__).resolve().parents[1]
W, H = 32, 18
CAMS = ("cam_a", "cam_b")
FAKE_THRESHOLDS = {
    "edges": {"hard": True, "global_min": 0.95, "region_min": 0.85},
    "colour": {"hard": True, "global_max": 10.0},
    "features": {"hard": False, "region_min": 0.80},
    "calibration": {"source": None, "date": None, "separability": {}, "accepted_shortfall": None},
}
GOOD = {"edges": {"global": 0.99, "regions": {"sofa_1": 0.97}, "skipped": {}},
        "colour": {"global": 2.0, "regions": {}, "skipped": {}},
        "features": {"global": None, "regions": {"sofa_1": 0.9}, "skipped": {}}}
BAD = {"edges": {"global": 0.70, "regions": {"sofa_1": 0.40}, "skipped": {}},
       "colour": {"global": 2.0, "regions": {}, "skipped": {}},
       "features": {"global": None, "regions": {"sofa_1": 0.9}, "skipped": {}}}


def fake_decide(metrics: dict, thresholds: dict):
    """§4.2 decision: ``*_min`` passes when value >= limit, ``*_max`` when value <= limit; hard
    failures are reasons, soft ones notes; None values pass; a missing check fails."""
    reasons, notes = [], []
    for check, th in thresholds.items():
        if check == "calibration" or not isinstance(th, dict):
            continue
        target = reasons if th.get("hard", True) else notes
        m = metrics.get(check)
        if not isinstance(m, dict):
            target.append({"check": check, "region": "global", "value": None, "threshold": None, "op": None})
            continue
        for key, limit in th.items():
            scope, _, kind = key.partition("_")
            if scope not in ("global", "region") or kind not in ("min", "max"):
                continue
            items = [("global", m.get("global"))] if scope == "global" else list((m.get("regions") or {}).items())
            for region, value in items:
                if value is None:
                    continue
                ok = value >= limit if kind == "min" else value <= limit
                if not ok:
                    target.append({"check": check, "region": region, "value": value, "threshold": limit,
                                   "op": ">=" if kind == "min" else "<="})
    return ("accept" if not reasons else "reject"), reasons, notes


def _import_gpu_test(monkeypatch, name: str, env: dict):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    spec = importlib.util.spec_from_file_location(f"gpu_{name}_cpu", ROOT / "tests" / "gpu" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png(path: Path, value: int, size=(W, H)) -> Path:
    arr = np.full((size[1], size[0], 3), value, dtype=np.uint8)
    return V.write_png_rgb(path, arr)


def _dump(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Polish outputs
# --------------------------------------------------------------------------

def _models_block() -> dict:
    polish = load_polish_config()["models"]
    gate = load_models_config()["models"]
    pick = ("repo", "revision", "licence")
    return {"base": {k: polish["base"][k] for k in pick} | {"files": []},
            "controlnet": {k: polish["controlnet"][k] for k in pick} | {"files": polish["controlnet"]["files"]},
            "gate": {role: {k: m[k] for k in pick} for role, m in gate.items()}}


def _attempt(k: int, png: str, sha: str, decision: str, metrics: dict, reasons=None) -> dict:
    if reasons is None:
        reasons = [] if decision == "accept" else [{"check": "edges", "region": "global", "value": 0.7,
                                                     "threshold": 0.95, "op": ">="}]
    return {"k": k, "role": "ladder", "strength": 0.375 - 0.125 * (k - 1), "control": "depth", "scale": 0.8,
            "size": "native", "mode": "plain", "seed": k, "steps": 8, "sigmas": [0.643, 0.5, 0.3], "seconds": 3.1,
            "png": png, "sha256": sha, "attempt_key": "a" * 64, "panes_restored": 1, "debug_jpg": f"{png[:-4]}_gate.jpg",
            "gate": {"decision": decision, "reasons": reasons, "notes": [], "metrics": copy.deepcopy(metrics),
                     "gate_key": "g" * 16}}


def make_polish_outputs(root: Path, project: str = "synthetic-01") -> Path:
    """outputs/<p>/renders (2 M5 views), polish/ (cam_a polished by a1, cam_b Cycles after 3 rejects),
    gate/gate_calibration.json (10 benign accepted, 10 negatives of which 9 rejected), determinism.json."""
    out = root / project
    renders = out / "renders"
    entries = []
    for i, cam in enumerate(CAMS):
        _png(renders / f"{cam}.png", 100 + i)
        entries.append({"camera": cam, "png": f"{cam}.png", "resolution": [W, H], "room_id": f"room_{i}",
                        "level_id": "L0", "render_key": "k" * 16, "index_stats": {},
                        "files": {"index": f"{cam}_index.png", "depth_mm": f"{cam}_depth_mm.png",
                                  "normal": f"{cam}_normal.png"}})
    _dump(renders / "render_manifest.json", {"renders": entries})
    polish = out / "polish"
    a1 = _png(polish / "cam_a_a1.png", 120)
    b_attempts = []
    for k in (1, 2, 3):
        p = _png(polish / f"cam_b_a{k}.png", 130 + k)
        b_attempts.append(_attempt(k, p.name, _sha(p), "reject", BAD))
    views = [
        {"camera": "cam_a", "room_id": "room_0", "source_png": "../renders/cam_a.png",
         "source_sha256": _sha(renders / "cam_a.png"), "prompt": "Photorealistic interior photograph ...",
         "controls": {"depth": "cam_a_control_depth.png"},
         "attempts": [_attempt(1, a1.name, _sha(a1), "accept", GOOD)],
         "final": "polished", "final_attempt": 1, "reason": None},
        {"camera": "cam_b", "room_id": "room_1", "source_png": "../renders/cam_b.png",
         "source_sha256": _sha(renders / "cam_b.png"), "prompt": "Photorealistic interior photograph ...",
         "controls": {"depth": "cam_b_control_depth.png"}, "attempts": b_attempts,
         "final": "cycles", "final_attempt": None, "reason": "gate"},
    ]
    _dump(polish / "polish_manifest.json", {
        "schema_version": "0.1", "kind": "run", "project": project, "incomplete": False,
        "models": _models_block(), "config": {}, "thresholds": FAKE_THRESHOLDS, "device": "cuda",
        "torch": "2.9.1", "diffusers": "0.40.0", "memory_mode": "resident", "peak_vram_gib": 18.2,
        "load_seconds": 40.0, "seconds_per_forward": 2.9, "views": views,
        "rooms": {"room_0": {"rule": "ok", "rung": 1}}, "warnings": []})
    _dump(polish / "determinism.json", {"camera": "cam_a", "max_abs_diff": 1, "seconds": 6.0})
    benign = [{"camera": "cam_a", "control": "blur", "magnitude": i, "decision": "accept", "reasons": [],
               "metrics": copy.deepcopy(GOOD)} for i in range(10)]
    negative = [{"camera": "cam_a", "control": "shift", "magnitude": 6 + i, "decision": "reject",
                 "reasons": [{"check": "edges"}], "metrics": copy.deepcopy(BAD)} for i in range(9)]
    negative.append({"camera": "cam_b", "control": "rotate", "magnitude": 2, "decision": "accept", "reasons": [],
                     "metrics": copy.deepcopy(GOOD)})
    _dump(out / "gate" / "gate_calibration.json", {"benign": benign, "negative": negative, "presumed_bad": []})
    return out


def _polish_module(monkeypatch, outputs: Path, thresholds: dict = FAKE_THRESHOLDS, real_decide: bool = False):
    gpu = _import_gpu_test(monkeypatch, "test_polish",
                           {"WENART_OUTPUTS": str(outputs), "POLISH_TEST_PROJECTS": "synthetic-01"})
    if not real_decide:
        monkeypatch.setattr(gpu, "decide", fake_decide)
        monkeypatch.setattr(gpu, "load_thresholds", lambda: copy.deepcopy(thresholds))
    return gpu


def _run_polish_tests(gpu, project: str = "synthetic-01") -> None:
    m = json.loads((gpu.OUTPUTS / project / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    p = (project, m)
    gpu.test_manifest_is_a_complete_run(p)
    gpu.test_manifest_records_the_pinned_models(p)
    gpu.test_every_view_has_a_final_image_of_render_size(p)
    gpu.test_accepted_attempts_pass_every_hard_threshold(p)
    gpu.test_rejected_attempts_have_reasons(p)
    gpu.test_gate_calibration_separates_benign_from_negative(p)
    gpu.test_determinism(p)


def _edit(path: Path, fn) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    _dump(path, data)


def test_polish_gpu_tests_pass_on_good_outputs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    make_polish_outputs(outputs)
    gpu = _polish_module(monkeypatch, outputs)
    assert gpu.PROJECTS == ["synthetic-01"] and gpu.OUTPUTS == outputs
    _run_polish_tests(gpu)


@pytest.mark.parametrize("defect, match", [
    ("polished_wrong_size", "not the render size"),
    ("cycles_wrong_size", "not the render size"),
    ("final_png_changed", "differs from its sha256"),
    ("render_changed", "render changed after the polish"),
    ("view_missing", "without a polish entry"),
    ("accepted_but_fails", "current thresholds fail it"),
    ("rejected_without_reason", "rejected without a reason"),
    ("rejected_but_passes", "current thresholds accept"),
    ("incomplete", "cut by the deadline"),
    ("final_not_accepted", "not accepted by the gate"),
    ("wrong_revision", "not polish.yaml"),
    ("wrong_gate_model", "not models.yaml"),
    ("missing_key", "lacks"),
    ("benign_rejected", "benign accepted"),
    ("negatives_missed", "negatives rejected"),
    ("not_deterministic", "grey levels apart"),
    ("determinism_not_measured", "not measured"),
    ("no_calibration", "gate_calibration.json missing"),
])
def test_polish_gpu_tests_catch_each_defect(tmp_path, monkeypatch, defect, match):
    outputs = tmp_path / "outputs"
    out = make_polish_outputs(outputs)
    manifest = out / "polish" / "polish_manifest.json"
    cal = out / "gate" / "gate_calibration.json"
    if defect == "polished_wrong_size":
        _png(out / "polish" / "cam_a_a1.png", 120, size=(W, H + 2))
        _edit(manifest, lambda m: m["views"][0]["attempts"][0].update(sha256=_sha(out / "polish" / "cam_a_a1.png")))
    elif defect == "cycles_wrong_size":
        _png(out / "renders" / "cam_b.png", 101, size=(W + 4, H))
        _edit(manifest, lambda m: m["views"][1].update(source_sha256=_sha(out / "renders" / "cam_b.png")))
    elif defect == "final_png_changed":
        _png(out / "polish" / "cam_a_a1.png", 121)
    elif defect == "render_changed":
        _png(out / "renders" / "cam_a.png", 99)
    elif defect == "view_missing":
        _edit(manifest, lambda m: m["views"].pop(1))
    elif defect == "accepted_but_fails":
        _edit(manifest, lambda m: m["views"][0]["attempts"][0]["gate"].update(metrics=copy.deepcopy(BAD)))
    elif defect == "rejected_without_reason":
        _edit(manifest, lambda m: m["views"][1]["attempts"][1]["gate"].update(reasons=[]))
    elif defect == "rejected_but_passes":
        _edit(manifest, lambda m: m["views"][1]["attempts"][2]["gate"].update(metrics=copy.deepcopy(GOOD)))
    elif defect == "incomplete":
        _edit(manifest, lambda m: m.update(incomplete=True))
    elif defect == "final_not_accepted":
        _edit(manifest, lambda m: m["views"][1].update(final="polished", final_attempt=2, reason=None))
    elif defect == "wrong_revision":
        _edit(manifest, lambda m: m["models"]["base"].update(revision="main"))
    elif defect == "wrong_gate_model":
        _edit(manifest, lambda m: m["models"]["gate"].pop("dino"))
    elif defect == "missing_key":
        _edit(manifest, lambda m: m["views"][0]["attempts"][0].pop("attempt_key"))
    elif defect == "benign_rejected":
        _edit(cal, lambda c: c["benign"][3].update(metrics=copy.deepcopy(BAD)))
    elif defect == "negatives_missed":
        _edit(cal, lambda c: c["negative"][0].update(metrics=copy.deepcopy(GOOD)))   # 8 of 10 = 80 %
    elif defect == "not_deterministic":
        _dump(out / "polish" / "determinism.json", {"camera": "cam_a", "max_abs_diff": 3, "seconds": 6.0})
    elif defect == "determinism_not_measured":
        _dump(out / "polish" / "determinism.json", {"camera": "cam_a", "max_abs_diff": None, "seconds": None,
                                                    "error": "OOM"})
    elif defect == "no_calibration":
        cal.unlink()
    gpu = _polish_module(monkeypatch, outputs)
    with pytest.raises(AssertionError, match=match):
        _run_polish_tests(gpu)


def test_polish_gpu_tests_fail_on_a_stale_render(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    out = make_polish_outputs(outputs)
    _edit(out / "renders" / "render_manifest.json", lambda m: m["renders"][1].pop("render_key"))
    gpu = _polish_module(monkeypatch, outputs)
    m = json.loads((out / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    with pytest.raises(pytest.fail.Exception, match="no M5 passes"):
        gpu.test_every_view_has_a_final_image_of_render_size(("synthetic-01", m))


def test_accepted_shortfall_needs_metric_rate_and_date(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    out = make_polish_outputs(outputs)
    _edit(out / "gate" / "gate_calibration.json", lambda c: c["negative"][0].update(metrics=copy.deepcopy(GOOD)))
    m = json.loads((out / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    p = ("synthetic-01", m)
    ok = copy.deepcopy(FAKE_THRESHOLDS)
    ok["calibration"]["accepted_shortfall"] = {"metric": "negative_reject", "rate": 0.8, "date": "2026-10-03",
                                               "note": "rotation 2 deg is inside the 3 px radius"}
    _polish_module(monkeypatch, outputs, ok).test_gate_calibration_separates_benign_from_negative(p)
    as_list = copy.deepcopy(ok)
    as_list["calibration"]["accepted_shortfall"] = [ok["calibration"]["accepted_shortfall"]]
    _polish_module(monkeypatch, outputs, as_list).test_gate_calibration_separates_benign_from_negative(p)
    too_low = copy.deepcopy(ok)
    too_low["calibration"]["accepted_shortfall"]["rate"] = 0.85
    with pytest.raises(AssertionError, match="negatives rejected 0.800 < 0.85"):
        _polish_module(monkeypatch, outputs, too_low).test_gate_calibration_separates_benign_from_negative(p)
    for broken, match in (({"metric": "negative_reject", "rate": 0.8}, "date of the user's OK"),
                          ({"rate": 0.8, "date": "2026-10-03"}, "metric must be one of"),
                          ({"metric": "negative_reject", "date": "2026-10-03"}, "rate must be 0..1")):
        th = copy.deepcopy(FAKE_THRESHOLDS)
        th["calibration"]["accepted_shortfall"] = broken
        with pytest.raises((AssertionError, pytest.fail.Exception), match=match):
            _polish_module(monkeypatch, outputs, th).test_gate_calibration_separates_benign_from_negative(p)


def _passing_metrics(thresholds: dict, good: bool = True) -> dict:
    """Metrics that pass (or, with good=False, fail the edges check of) every limit of ``thresholds``."""
    out = {}
    for check, th in thresholds.items():
        if check == "calibration" or not isinstance(th, dict):
            continue
        is_min = "global_min" in th or "region_min" in th
        value = 1.0 if is_min else 0.0
        if not good and check == "edges":
            value = 0.5
        out[check] = {"global": value, "regions": {"sofa_1": value}, "skipped": {}}
    return out


def test_polish_gpu_tests_with_the_real_decide(tmp_path, monkeypatch):
    """The same outputs with metrics shaped for the package thresholds and the real ``decide``."""
    from wenart.gate import decide

    thresholds = load_thresholds()
    try:
        decide(_passing_metrics(thresholds), thresholds)
    except NotImplementedError:
        pytest.skip("wenart.gate.decide is not implemented in this tree (area C)")
    outputs = tmp_path / "outputs"
    out = make_polish_outputs(outputs)
    good, bad = _passing_metrics(thresholds), _passing_metrics(thresholds, good=False)

    def reshape(m):
        for v in m["views"]:
            for a in v["attempts"]:
                a["gate"]["metrics"] = copy.deepcopy(good if a["gate"]["decision"] == "accept" else bad)

    def reshape_cal(c):
        for r in c["benign"]:
            r["metrics"] = copy.deepcopy(good)
        for i, r in enumerate(c["negative"]):
            r["metrics"] = copy.deepcopy(good if i == 9 else bad)

    _edit(out / "polish" / "polish_manifest.json", reshape)
    _edit(out / "gate" / "gate_calibration.json", reshape_cal)
    gpu = _polish_module(monkeypatch, outputs, real_decide=True)
    _run_polish_tests(gpu)


# --------------------------------------------------------------------------
# Vision-check outputs
# --------------------------------------------------------------------------

def _answers(key: str, cfg: dict, n: int = 20, failed: int = 1) -> dict:
    model = cfg["models"][key]
    calls = {}
    for i in range(n):
        ok = i >= failed
        calls[f"call{i:02d}"] = {"camera": f"cam_{i}", "image_kind": "cycles", "prompt_kind": "check",
                                 "prompt": "...", "raw_text": "{}" if ok else "",
                                 "data": {"elements": {}} if ok else None, "latency_s": 2.0,
                                 "error": None if ok else "timeout"}
    return {"model": model["id"], "slug": model["slug"], "calls": calls}


def _style_call(key: str, walls: str = "plaster_charcoal", floor: str = "concrete_polished") -> dict:
    data = {"floor": floor, "walls": walls, "light": "warm daylight", "family": "industrial"}
    return {"file": "../../../tests/fixtures/style_photo_synthetic-03_salon.jpg", "sha256": "s", "model_key": key,
            "model": key, "slug": key, "error": None, "seconds": 2.0,
            "result": {"kind": "style_photo", "file": "style_photo_synthetic-03_salon.jpg",
                       "passes": [{"model_key": key, "model": key, "pass": 1, "data": data, "error": None}]}}


def _metrics(**over) -> dict:
    m = {"fa_missing": 0.02, "fa_extra": 0.05, "count_error": 0.0, "removal_flagged": 0.9,
         "removal_confirmed": 0.7, "insertion": 0.65,
         "models": {"qwen": {"decoy_accept": 0.0, "answer_rate": 1.0}, "glm": {"decoy_accept": 0.05}}}
    m.update(over)
    return m


def make_check_outputs(root: Path, project: str = "synthetic-03", metrics: dict = None,
                       advisory: bool = False, missed: list = None) -> Path:
    cfg = load_check_config()
    check = root / project / "check"
    for key in ("qwen", "glm"):
        _dump(check / f"answers_{cfg['models'][key]['slug']}.json", _answers(key, cfg))
    _dump(check / "check_calibration.json", {
        "schema_version": "0.1", "project": project, "model_keys": ["qwen", "glm"], "single_pass": False,
        "metrics": metrics or _metrics(), "targets": dict(cfg["targets"]), "missed": missed or [],
        "advisory": advisory, "advisory_reasons": [], "plan_ab": {}})
    _dump(check / "check_manifest.json", {"schema_version": "0.1", "project": project, "advisory": advisory,
                                          "views": {}})
    _dump(check / "style_photo_test.json", {"schema_version": "0.1", "kind": "style_photo_passes",
                                            "calls": [_style_call("qwen"), _style_call("glm")]})
    return check


def _check_module(monkeypatch, outputs: Path, models: str = "qwen glm"):
    return _import_gpu_test(monkeypatch, "test_check", {"WENART_OUTPUTS": str(outputs),
                                                        "CHECK_TEST_PROJECTS": "synthetic-03", "CHECK_MODELS": models})


def _run_check_tests(gpu, project: str = "synthetic-03") -> None:
    cfg = load_check_config()
    gpu.test_every_model_answered_its_calls(project, cfg)
    gpu.test_calibration_present(project, cfg)
    gpu.test_advisory_set_exactly_when_a_target_is_missed(project, cfg)
    gpu.test_style_photo_test(project)


def test_check_gpu_tests_pass_on_good_outputs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    make_check_outputs(outputs)
    gpu = _check_module(monkeypatch, outputs)
    assert gpu.PROJECTS == ["synthetic-03"] and gpu.MODEL_KEYS == ["qwen", "glm"]
    _run_check_tests(gpu)


def test_check_gpu_tests_accept_an_advisory_check_that_says_why(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    missed = [{"target": "decoy_accept_max", "metric": "decoy_accept[glm]", "value": 0.2, "threshold": 0.1,
               "op": "<="},
              {"target": "insertion_min", "metric": "insertion", "value": None, "threshold": 0.6, "op": ">=",
               "reason": "no data"}]
    metrics = _metrics(insertion=None, models={"qwen": {"decoy_accept": 0.0}, "glm": {"decoy_accept": 0.2}})
    make_check_outputs(outputs, metrics=metrics, advisory=True, missed=missed)
    _run_check_tests(_check_module(monkeypatch, outputs))


def test_check_gpu_tests_single_model_is_always_advisory(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    make_check_outputs(outputs)
    gpu = _check_module(monkeypatch, outputs, models="qwen")
    cfg = load_check_config()
    with pytest.raises(AssertionError, match="single pass True"):
        gpu.test_advisory_set_exactly_when_a_target_is_missed("synthetic-03", cfg)
    make_check_outputs(outputs, advisory=True)
    gpu.test_advisory_set_exactly_when_a_target_is_missed("synthetic-03", cfg)
    gpu.test_style_photo_test("synthetic-03")


@pytest.mark.parametrize("defect, match", [
    ("low_answer_rate", "answered 90.0%"),
    ("wrong_model", "names"),
    ("no_calls", "no call recorded"),
    ("no_calibration", "check_calibration.json missing"),
    ("targets_changed", "not check.yaml's"),
    ("manifest_advisory_differs", "advisory differs"),
    ("missed_but_not_advisory", "advisory=False but missed targets"),
    ("advisory_without_miss", "advisory=True but missed targets {}"),
    ("missed_not_listed", "not listed"),
    ("decoy_no_data_not_advisory", "decoy_accept_max"),
    ("style_wrong_walls", "read {'walls': 'plaster_white'"),
    ("style_model_missing", "no answer of glm"),
    ("style_failed_pass", "no answer of qwen"),
])
def test_check_gpu_tests_catch_each_defect(tmp_path, monkeypatch, defect, match):
    outputs = tmp_path / "outputs"
    cfg = load_check_config()
    check = make_check_outputs(outputs)
    answers_qwen = check / f"answers_{cfg['models']['qwen']['slug']}.json"
    calibration = check / "check_calibration.json"
    style = check / "style_photo_test.json"
    if defect == "low_answer_rate":
        _dump(answers_qwen, _answers("qwen", cfg, n=20, failed=2))
    elif defect == "wrong_model":
        _edit(answers_qwen, lambda a: a.update(model="Qwen/Qwen2.5-VL-7B-Instruct"))
    elif defect == "no_calls":
        _edit(answers_qwen, lambda a: a.update(calls={}))
    elif defect == "no_calibration":
        calibration.unlink()
    elif defect == "targets_changed":
        _edit(calibration, lambda c: c["targets"].update(fa_missing_max=0.2))
    elif defect == "manifest_advisory_differs":
        _edit(check / "check_manifest.json", lambda m: m.update(advisory=True))
    elif defect == "missed_but_not_advisory":
        _edit(calibration, lambda c: c["metrics"].update(fa_missing=0.08))
    elif defect == "advisory_without_miss":
        _edit(calibration, lambda c: c.update(advisory=True))
        _edit(check / "check_manifest.json", lambda m: m.update(advisory=True))
    elif defect == "missed_not_listed":
        _edit(calibration, lambda c: (c["metrics"].update(removal_flagged=0.5), c.update(advisory=True)))
        _edit(check / "check_manifest.json", lambda m: m.update(advisory=True))
    elif defect == "decoy_no_data_not_advisory":
        _edit(calibration, lambda c: c["metrics"]["models"]["glm"].update(decoy_accept=None))
    elif defect == "style_wrong_walls":
        _dump(style, {"calls": [_style_call("qwen"), _style_call("glm", walls="plaster_white")]})
    elif defect == "style_model_missing":
        _dump(style, {"calls": [_style_call("qwen")]})
    elif defect == "style_failed_pass":
        failed = _style_call("qwen")
        failed["result"]["passes"][0].update(data=None, error="schema: bad answer")
        _dump(style, {"calls": [failed, _style_call("glm")]})
    gpu = _check_module(monkeypatch, outputs)
    with pytest.raises(AssertionError, match=match):
        _run_check_tests(gpu)


def test_style_photo_reader_accepts_the_combined_and_the_direct_layouts():
    gpu_style = importlib.util.spec_from_file_location("gpu_check_reader", ROOT / "tests" / "gpu" / "test_check.py")
    module = importlib.util.module_from_spec(gpu_style)
    gpu_style.loader.exec_module(module)
    direct = {"kind": "style_photo", "passes": [{"model_key": "qwen", "data": {"walls": "brick"}, "error": None},
                                                {"model_key": "glm", "data": None, "error": "timeout"}]}
    assert module.style_passes(direct) == {"qwen": [{"walls": "brick"}]}
    later = {"calls": [_style_call("qwen", walls="plaster_white"), _style_call("qwen")]}
    assert module.style_passes(later)["qwen"][-1]["walls"] == "plaster_charcoal"   # the latest pass counts
    assert module.target_metric("fa_extra_max") == ("fa_extra", "<=")
    assert module.target_metric("insertion_min") == ("insertion", ">=")
    assert module.metric_values({"decoy_accept": {"qwen": 0.1}}, "decoy_accept") == {"decoy_accept[qwen]": 0.1}
    assert module.metric_values({}, "insertion") == {"insertion": None}
