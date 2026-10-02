"""Milestone 5 GPU tests of the AI polish and the change gate (docs/milestone5.md §9).

Run on the pod by scripts/jobs/polish.sh (tests phase) with the polish venv:
``/opt/wenart/venv-polish/bin/python -m pytest -m gpu tests/gpu/test_polish.py``. They only
read what the job wrote under $WENART_OUTPUTS (default /workspace/repo/outputs) for the
projects in $POLISH_TEST_PROJECTS (the job exports the projects whose polish run ran or whose
``polish/polish_manifest.json`` exists; default synthetic-01 synthetic-03):

- ``polish/polish_manifest.json`` is a complete run manifest of the §3.6 shape that records the
  pinned models of ``polish.yaml`` and ``models.yaml``;
- every rendered view has a final image of the render size (the accepted attempt's PNG with its
  recorded sha256, or the Cycles PNG), polished from the current Cycles render;
- every accepted attempt passes every hard threshold, recomputed with ``wenart.gate.decide`` from
  its stored metrics and the current ``thresholds.yaml``; every rejected attempt has reasons and
  ``decide`` rejects it again;
- ``gate/gate_calibration.json`` (from the sweep run): benign controls accepted 100 % and
  negatives rejected >= 90 %, both recomputed with ``decide`` and the current thresholds, unless
  ``thresholds.yaml: calibration.accepted_shortfall`` names the metric, the accepted rate and the
  date of the user's OK. Format: one mapping or a list of mappings ``{metric: benign_accept |
  negative_reject, rate: <the accepted rate, 0..1>, date: YYYY-MM-DD}`` (extra keys allowed);
- ``polish/determinism.json``: the same view polished twice with the same seed differs by at most
  2 grey levels (``max_abs_diff <= 2``).
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import pytest

from wenart import views as V
from wenart.gate import decide
from wenart.gate.api import load_models_config, load_thresholds
from wenart.polish.config import load_config as load_polish_config

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("POLISH_TEST_PROJECTS", "synthetic-01 synthetic-03").split() if p]

BENIGN_ACCEPT_MIN = 1.0
NEGATIVE_REJECT_MIN = 0.90
DETERMINISM_MAX_DIFF = 2
SHORTFALL_METRICS = ("benign_accept", "negative_reject")
# §3.6 manifest shape (extra keys are allowed).
MANIFEST_KEYS = ("schema_version", "kind", "project", "incomplete", "models", "config", "thresholds", "device",
                 "torch", "diffusers", "memory_mode", "peak_vram_gib", "load_seconds", "seconds_per_forward",
                 "views", "rooms", "warnings")
VIEW_KEYS = ("camera", "room_id", "source_png", "source_sha256", "prompt", "controls", "attempts", "final",
             "final_attempt", "reason")
ATTEMPT_KEYS = ("k", "role", "strength", "control", "scale", "size", "mode", "seed", "steps", "sigmas", "seconds",
                "png", "sha256", "attempt_key", "panes_restored", "gate", "debug_jpg")
GATE_KEYS = ("decision", "reasons", "notes", "metrics", "gate_key")
CYCLES_REASONS = ("gate", "brief", "room", "error", "deadline")


def _load(project: str, rel: str) -> dict:
    path = OUTPUTS / project / rel
    assert path.is_file(), (f"{path} missing: did the job run the polish (and, for the gate calibration, the "
                            f"sweep run 1a) for {project}? (POLISH_TEST_PROJECTS={' '.join(PROJECTS)})")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def current_thresholds() -> dict:
    """The thresholds the decisions are recomputed with: the package ``thresholds.yaml`` of this commit."""
    return load_thresholds()


def gated(attempt: dict) -> bool:
    """True when the attempt produced an image and the gate compared it."""
    return bool(attempt.get("gate")) and not attempt.get("error")


def shortfalls(thresholds: dict) -> dict:
    """``{metric: accepted rate}`` from ``calibration.accepted_shortfall`` (AssertionError when an entry is
    incomplete: it must name the metric, the rate and the date of the user's OK)."""
    raw = (thresholds.get("calibration") or {}).get("accepted_shortfall")
    if raw in (None, {}, []):
        return {}
    entries = raw if isinstance(raw, list) else [raw]
    out = {}
    for e in entries:
        assert isinstance(e, dict), f"accepted_shortfall entry {e!r} is not a mapping"
        metric, rate, date = e.get("metric"), e.get("rate"), e.get("date")
        assert metric in SHORTFALL_METRICS, f"accepted_shortfall {e}: metric must be one of {SHORTFALL_METRICS}"
        assert isinstance(rate, (int, float)) and 0 <= rate <= 1, f"accepted_shortfall {e}: rate must be 0..1"
        try:
            dt.date.fromisoformat(str(date))
        except ValueError:
            pytest.fail(f"accepted_shortfall {e}: date of the user's OK must be YYYY-MM-DD")
        out[metric] = float(rate)
    return out


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    return request.param, _load(request.param, "polish/polish_manifest.json")


def test_manifest_is_a_complete_run(project):
    name, m = project
    missing = [k for k in MANIFEST_KEYS if k not in m]
    assert not missing, f"{name}: polish_manifest.json lacks {missing}"
    assert m["schema_version"] == "0.1" and m["kind"] == "run" and m["project"] == name
    assert m["incomplete"] is False, f"{name}: the polish run was cut by the deadline (incomplete)"
    assert m["memory_mode"] in ("resident", "offload")
    assert m["views"], f"{name}: no view polished"
    for v in m["views"]:
        cam = v.get("camera")
        assert not [k for k in VIEW_KEYS if k not in v], f"{name}/{cam}: view entry lacks keys"
        ks = [a.get("k") for a in v["attempts"]]
        assert len(ks) == len(set(ks)), f"{name}/{cam}: attempt numbers repeat: {ks}"
        for a in v["attempts"]:
            assert not [k for k in ATTEMPT_KEYS if k not in a], f"{name}/{cam} a{a.get('k')}: attempt lacks keys"
            assert a["role"] == "ladder", f"{name}/{cam} a{a['k']}: role {a['role']} in a run manifest"
            if gated(a):
                assert not [k for k in GATE_KEYS if k not in a["gate"]], f"{name}/{cam} a{a['k']}: gate lacks keys"
                assert a["gate"]["decision"] in ("accept", "reject")
        assert v["final"] in ("polished", "cycles"), f"{name}/{cam}: final {v['final']!r}"
        if v["final"] == "polished":
            chosen = [a for a in v["attempts"] if a["k"] == v["final_attempt"]]
            assert chosen, f"{name}/{cam}: final_attempt {v['final_attempt']} is not an attempt"
            assert gated(chosen[0]) and chosen[0]["gate"]["decision"] == "accept", \
                f"{name}/{cam}: the final attempt a{v['final_attempt']} was not accepted by the gate"
        else:
            assert v["final_attempt"] is None and v["reason"] in CYCLES_REASONS, \
                f"{name}/{cam}: Cycles final with final_attempt {v['final_attempt']} and reason {v['reason']!r}"


def test_manifest_records_the_pinned_models(project):
    name, m = project
    polish = load_polish_config()["models"]
    for role in ("base", "controlnet"):
        got = m["models"].get(role) or {}
        want = polish[role]
        assert (got.get("repo"), got.get("revision"), got.get("licence")) == \
            (want["repo"], want["revision"], want["licence"]), f"{name}: models.{role} is not polish.yaml's"
    gate = m["models"].get("gate") or {}
    got_gate = {(e.get("repo"), e.get("revision")) for e in gate.values() if isinstance(e, dict)}
    want_gate = {(e["repo"], e["revision"]) for e in load_models_config()["models"].values()}
    assert got_gate == want_gate, f"{name}: gate models {sorted(got_gate)} are not models.yaml's {sorted(want_gate)}"


def test_every_view_has_a_final_image_of_render_size(project):
    from PIL import Image

    name, m = project
    try:
        views = V.load_views(OUTPUTS / name / "renders")
    except V.StaleRender as exc:
        pytest.fail(f"{name}: render {exc.camera} has no M5 passes ({exc.missing}): re-render before polishing")
    by_cam = {v["camera"]: v for v in m["views"]}
    missing = sorted(set(views) - set(by_cam))
    assert not missing, f"{name}: rendered views without a polish entry: {missing}"
    polish_dir = OUTPUTS / name / "polish"
    for cam, view in views.items():
        entry = by_cam[cam]
        source = (polish_dir / entry["source_png"]).resolve()
        assert source == view.png.resolve(), f"{name}/{cam}: source_png {entry['source_png']} is not the render"
        assert entry["source_sha256"] == _sha256(view.png), \
            f"{name}/{cam}: the render changed after the polish (source_sha256 differs): polish again"
        if entry["final"] == "polished":
            attempt = next(a for a in entry["attempts"] if a["k"] == entry["final_attempt"])
            final = polish_dir / attempt["png"]
            assert final.is_file(), f"{name}/{cam}: final image {final} missing"
            assert _sha256(final) == attempt["sha256"], f"{name}/{cam}: {final.name} differs from its sha256"
        else:
            final = view.png
        with Image.open(final) as im:
            assert im.size == tuple(view.size), f"{name}/{cam}: final image {im.size} is not the render size {view.size}"


def test_accepted_attempts_pass_every_hard_threshold(project):
    name, m = project
    thresholds = current_thresholds()
    checked = 0
    for v in m["views"]:
        for a in v["attempts"]:
            if not gated(a) or a["gate"]["decision"] != "accept":
                continue
            decision, reasons, _notes = decide(a["gate"]["metrics"], thresholds)
            assert decision == "accept" and not reasons, \
                f"{name}/{v['camera']} a{a['k']}: accepted, but the current thresholds fail it: {reasons}"
            checked += 1
    finals = sum(1 for v in m["views"] if v["final"] == "polished")
    assert checked >= finals, f"{name}: {finals} polished views but only {checked} accepted attempts"


def test_rejected_attempts_have_reasons(project):
    name, m = project
    thresholds = current_thresholds()
    for v in m["views"]:
        for a in v["attempts"]:
            if not gated(a) or a["gate"]["decision"] != "reject":
                continue
            assert a["gate"]["reasons"], f"{name}/{v['camera']} a{a['k']}: rejected without a reason"
            decision, reasons, _notes = decide(a["gate"]["metrics"], thresholds)
            assert decision == "reject" and reasons, \
                f"{name}/{v['camera']} a{a['k']}: rejected, but the current thresholds accept its metrics"


def test_gate_calibration_separates_benign_from_negative(project):
    name, _m = project
    cal = _load(name, "gate/gate_calibration.json")
    thresholds = current_thresholds()
    allowed = shortfalls(thresholds)
    benign = [r for r in cal.get("benign") or [] if isinstance(r.get("metrics"), dict)]
    negative = [r for r in cal.get("negative") or [] if isinstance(r.get("metrics"), dict)]
    assert benign and negative, f"{name}: gate_calibration.json has no benign or no negative comparisons"
    benign_ok = [r for r in benign if decide(r["metrics"], thresholds)[0] == "accept"]
    negative_ok = [r for r in negative if decide(r["metrics"], thresholds)[0] == "reject"]
    rates = {"benign_accept": len(benign_ok) / len(benign), "negative_reject": len(negative_ok) / len(negative)}
    targets = {"benign_accept": allowed.get("benign_accept", BENIGN_ACCEPT_MIN),
               "negative_reject": allowed.get("negative_reject", NEGATIVE_REJECT_MIN)}
    failed_benign = sorted({f"{r['camera']}:{r['control']}:{r.get('magnitude')}" for r in benign if r not in benign_ok})
    missed = sorted({f"{r['camera']}:{r['control']}:{r.get('magnitude')}" for r in negative if r not in negative_ok})
    assert rates["benign_accept"] >= targets["benign_accept"], \
        f"{name}: benign accepted {rates['benign_accept']:.3f} < {targets['benign_accept']}: {failed_benign[:10]}"
    assert rates["negative_reject"] >= targets["negative_reject"], \
        f"{name}: negatives rejected {rates['negative_reject']:.3f} < {targets['negative_reject']}: {missed[:10]}"


def test_determinism(project):
    name, _m = project
    d = _load(name, "polish/determinism.json")
    assert d.get("camera"), f"{name}: determinism.json names no camera"
    assert d.get("max_abs_diff") is not None, f"{name}: determinism was not measured ({d.get('error')})"
    assert d["max_abs_diff"] <= DETERMINISM_MAX_DIFF, \
        f"{name}: the same seed gave images {d['max_abs_diff']} grey levels apart on {d['camera']}"
