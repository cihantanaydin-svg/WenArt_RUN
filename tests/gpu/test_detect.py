"""Milestone 7 GPU tests of the added-object detector (docs/milestone7.md §8.1, §11 GPU).

Run on the pod (``pytest -m gpu tests/gpu/test_detect.py``): by the prep job after
``detect-calibrate``, and by the full job after the ``detect`` stage.

- the real OWLv2 (``wenart.gate.models.Detector``, the pinned snapshot of
  ``gate/models.yaml detect``) on the committed salon render
  (``tests/fixtures/style_photo_synthetic-03_salon.jpg``, 1920 x 1080): the
  window is found where it is drawn (the box convention of the padded square
  holds on the real model), scores are probabilities, boxes lie in the
  image, and two runs give the same boxes;
- the calibration is recorded: ``detector_calibration.json`` at
  ``$DETECT_CALIBRATION`` (default ``$WENART_RESULTS/detect/detector_calibration.json``;
  skipped when neither is set) has the pinned model, positives and
  negatives, the grid, and ``t_det``/``t_strong``/``usable`` recomputed
  from its own per-pair scores (whatever the rates are: they are a
  measurement, reported, not a target of this test);
- per project of ``$DETECT_TEST_PROJECTS`` (exported by the orchestrator for
  the projects whose ``detect`` stage ran; empty -> skipped) under
  ``$WENART_OUTPUTS``: ``detect/detect_manifest.json`` names the pinned model
  and every polished view has a ``detect/<cam>.json`` whose images are the
  current files (sha256).
"""
import json
import os
from pathlib import Path

import numpy as np
import pytest

from wenart import views as V
from wenart.gate import detect as D
from wenart.gate.api import load_models_config

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("DETECT_TEST_PROJECTS", "").replace(",", " ").split() if p]
SALON = ROOT / "tests" / "fixtures" / "style_photo_synthetic-03_salon.jpg"
SALON_WINDOW = [680, 200, 1160, 670]          # the glazed window of the salon render (pixels, by eye, +-10 px)

needs_projects = pytest.mark.skipif(not PROJECTS, reason="DETECT_TEST_PROJECTS is empty: no detect stage in this run")


def calibration_path():
    if os.environ.get("DETECT_CALIBRATION"):
        return Path(os.environ["DETECT_CALIBRATION"])
    if os.environ.get("WENART_RESULTS"):
        return Path(os.environ["WENART_RESULTS"]) / "detect" / D.CALIBRATION_JSON
    return None


@pytest.fixture(scope="module")
def detector():
    from wenart.gate.models import Detector
    return Detector(device="cuda")


def test_owlv2_finds_the_salon_window_where_it_is(detector):
    rgb = V.read_rgb(SALON)
    found = D.detect_rgb(detector, rgb)
    assert found["size"] == [1920, 1080] and found["model_size"] == [960, 540]
    boxes = found["boxes"]
    assert boxes, "OWLv2 found nothing at the record floor"
    for b in boxes:
        assert 0.0 <= b["score"] <= 1.0 and b["group"] in D.GROUP_BY_NAME
        x0, y0, x1, y1 = b["box_px"]
        assert 0 <= x0 < x1 <= 1920 and 0 <= y0 < y1 <= 1080
    windows = sorted((b for b in boxes if b["group"] == "window"), key=lambda b: -b["score"])
    top = sorted(boxes, key=lambda b: -b["score"])[:8]
    print("salon top boxes:", [(b["group"], b["score"], [round(v) for v in b["box_px"]]) for b in top])
    assert windows, "no window box on the salon render"
    best = windows[0]
    assert D.box_iou(best["box_px"], SALON_WINDOW) >= 0.5, (best, SALON_WINDOW)
    assert best["score"] >= 0.1, best
    print(f"OWLv2 load {detector.load_seconds} s, one image {found['seconds']} s")


def test_detection_is_deterministic(detector):
    rgb = V.read_rgb(SALON)
    a = D.detect_rgb(detector, rgb)["boxes"]
    b = D.detect_rgb(detector, rgb)["boxes"]
    assert [(x["group"], x["box_px"]) for x in a] == [(x["group"], x["box_px"]) for x in b]
    assert np.allclose([x["score"] for x in a], [x["score"] for x in b], atol=1e-3)


def test_calibration_recorded():
    path = calibration_path()
    if path is None:
        pytest.skip("set DETECT_CALIBRATION or WENART_RESULTS (detect-calibrate writes $RESULTS/detect/)")
    assert path.is_file(), f"{path} missing: did detect-calibrate run?"
    cal = json.loads(path.read_text(encoding="utf-8"))
    pinned = load_models_config()["detect"]
    assert cal["kind"] == "detector_calibration" and cal["model"]["revision"] == pinned["revision"]
    assert cal["positives"] > 0 and cal["negatives"] > 0, (cal["positives"], cal["negatives"])
    assert len(cal["grid"]) == len(D.GRID) and cal["settings"]["detect_version"] == D.DETECT_VERSION
    hits = [r["hit"] for r in cal["per_pair"] if r["kind"] == "positive"]
    falses = [r["false"] for r in cal["per_pair"] if r["kind"] == "negative"]
    again = D.calibrate_scores(hits, falses, targets=cal["targets"])
    for key in ("t_det", "t_strong", "rates", "usable", "targets_met"):
        assert cal[key] == again[key], key
    assert (cal["check_yaml_block"] is None) is (not cal["usable"])
    print(f"detector calibration: {cal['positives']} positives, {cal['negatives']} negatives, t_det {cal['t_det']}, "
          f"t_strong {cal['t_strong']}, rates {cal['rates']}, usable {cal['usable']}, by source "
          f"{cal['pairs_by_source']}")


@pytest.fixture(scope="module", params=PROJECTS or ["-"])
def project(request):
    return request.param


@needs_projects
def test_detect_files_of_the_run(project):
    det_dir = OUTPUTS / project / D.DETECT_DIR
    manifest = det_dir / D.DETECT_MANIFEST
    assert manifest.is_file(), f"{manifest} missing: did the detect stage run for {project}?"
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    assert doc["model"]["revision"] == load_models_config()["detect"]["revision"]
    if doc.get("skipped"):
        pytest.skip(f"{project}: detect skipped ({doc['skipped']})")
    assert not doc["incomplete"], f"{project}: detection cut by the deadline"
    pm = json.loads((OUTPUTS / project / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    chosen, _ = D.polished_views(pm, OUTPUTS / project / "polish" / "polish_manifest.json")
    for cam, pol in chosen.items():
        view = json.loads((det_dir / f"{cam}.json").read_text(encoding="utf-8"))
        assert view["images"]["polished"]["sha256"] == D.sha256_file(pol["png"]), cam
        cycles = det_dir / view["images"]["cycles"]["file"]
        assert view["images"]["cycles"]["sha256"] == D.sha256_file(cycles), cam
        assert isinstance(view["images"]["polished"]["boxes"], list)
    print(f"{project}: {len(chosen)} polished view(s) detected, {doc['detected_images']} image(s) this run")
