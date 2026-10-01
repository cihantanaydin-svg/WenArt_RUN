"""Milestone 2 GPU tests for the recognition bake-off (``pytest -m gpu``).

Run on the pod by scripts/jobs/bakeoff.sh after it started ``vllm serve`` for
the first model (``VLM_SERVER``, default http://127.0.0.1:8001/v1) and inside
/workspace/venv-paddle (PaddleOCR 3.7 installed, GPU visible).

- the vLLM server answers ``/health`` and lists a model;
- one page-class call on a synthetic scan returns schema-valid JSON;
- PaddleOCR reads at least 80 % of the room labels of synthetic-02/plan_scan.png.
"""
import json
import os
from pathlib import Path

import pytest

from wenart.recognition import bakeoff, metrics, ocr, schemas, vlm_client

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT / "projects"
RESULTS = Path(os.environ.get("WENART_RESULTS", "/tmp/wenart-results"))
RESULTS.mkdir(parents=True, exist_ok=True)
SERVER = os.environ.get("VLM_SERVER", "http://127.0.0.1:8001/v1")


def test_vllm_server_health_and_model():
    assert vlm_client.health(SERVER), f"vLLM server at {SERVER} does not answer /health"
    models = vlm_client.served_models(SERVER)
    assert models, "no model listed at /v1/models"
    (RESULTS / "vllm_models.txt").write_text("\n".join(models) + "\n")


def test_page_class_call_returns_schema_valid_json():
    client = vlm_client.VLMClient(SERVER, timeout_s=600, retries=2)
    page = [p for p in bakeoff.raster_pages(PROJECTS) if p.slug == "synthetic-01_1_kat_scan"][0]
    res = client.run_task("page_class", page.image_path)
    (RESULTS / "vllm_page_class.json").write_text(json.dumps(res.to_dict(), ensure_ascii=False, indent=1))
    assert res.error is None, res.error
    assert res.data is not None and schemas.is_valid("page_class", res.data)
    assert res.data["class"] in schemas.PAGE_CLASSES
    assert res.latency_s < 300


def test_paddleocr_reads_80_percent_of_room_labels():
    page = [p for p in bakeoff.raster_pages(PROJECTS) if p.slug == "synthetic-02_plan_scan"][0]
    items = ocr.ocr_paddle(page.image_path)
    truth = page.truth_texts("room_label")
    scores = metrics.text_scores([i["text"] for i in items], truth)
    (RESULTS / "paddleocr_plan_scan.json").write_text(
        json.dumps({"items": items, "scores": scores}, ensure_ascii=False, indent=1))
    assert items, "PaddleOCR returned no text"
    assert scores["recall"] >= 0.8, f"room labels read: {scores['tp']}/{len(truth)}, missed {scores['missed']}"
