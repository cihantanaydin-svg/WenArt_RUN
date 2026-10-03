"""GPU tests of the recognition (``pytest -m gpu``): Milestone 2 bake-off and Milestone 7 AI typing.

Milestone 2: run on the pod by scripts/jobs/bakeoff.sh after it started
``vllm serve`` for the first model (``VLM_SERVER``, default
http://127.0.0.1:8001/v1) and inside /workspace/venv-paddle (PaddleOCR 3.7
installed, GPU visible).

- the vLLM server answers ``/health`` and lists a model;
- one page-class call on a synthetic scan returns schema-valid JSON;
- PaddleOCR reads at least 80 % of the room labels of synthetic-02/plan_scan.png.

Milestone 7 (docs/milestone7.md §9.2, §11 GPU; tests named ``test_m7_*``): run by
the prep job after both VLM sessions answered the recognition requests and
``pipeline_final`` re-ran the prep projects. ``WENART_PREP_OUTPUTS`` = the
folder holding the pipeline outputs ``<project>/`` (``/workspace/outputs-prep``);
without it these tests skip (the bake-off job runs this file too).
``WENART_PREP_PROJECTS`` overrides the project list. No server is needed:
they read the answer files and the final building JSONs.

- every project with requests has a current, schema-valid answer of both models
  for every item;
- real01: >= 80 % of the AI-typed pieces (matched to the reference) end with a
  reference-accepted type and no piece is ``verified`` with a wrong type;
- raster room labels: synthetic-02 5/5, the real01 raster fixtures >= 7/8 rooms
  with the right label (§4.4).
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


@pytest.mark.xfail(
    strict=True,
    reason="Measured on 1 Oct 2026 (RTX PRO 4000 and L4): PaddleOCR PP-OCRv5 reads 3/5 room labels on the "
           "synthetic-02 scan; SALON and YATAK ODASI are crossed by furniture lines. The 80 % target from "
           "docs/milestone2.md stays here as a strict xfail so the test flips when OCR (or a furniture mask) "
           "reaches it. Both VLMs read 5/5 on the same page (results/bakeoff/summary.md).",
)
def test_paddleocr_reads_80_percent_of_room_labels():
    page = [p for p in bakeoff.raster_pages(PROJECTS) if p.slug == "synthetic-02_plan_scan"][0]
    items = ocr.ocr_paddle(page.image_path)
    truth = page.truth_texts("room_label")
    scores = metrics.text_scores([i["text"] for i in items], truth)
    (RESULTS / "paddleocr_plan_scan.json").write_text(
        json.dumps({"items": items, "scores": scores}, ensure_ascii=False, indent=1))
    assert items, "PaddleOCR returned no text"
    assert scores["recall"] >= 0.8, f"room labels read: {scores['tp']}/{len(truth)}, missed {scores['missed']}"


# --------------------------------------------------------------------------
# Milestone 7: answers of the prep pod, AI typing on real01, raster room labels
# --------------------------------------------------------------------------

PREP_OUTPUTS = os.environ.get("WENART_PREP_OUTPUTS", "").strip()
PREP_PROJECTS = (os.environ.get("WENART_PREP_PROJECTS", "").split()
                 or ["real01", "synthetic-02", "synthetic-06", "real01-scan", "real01-photo"])
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"
FT = 0.3048
RASTER_LABEL_TARGETS = {"synthetic-02": 5, "real01-scan": 7, "real01-photo": 7}   # §4.4 "rooms with right label"
needs_prep = pytest.mark.skipif(not PREP_OUTPUTS, reason="WENART_PREP_OUTPUTS not set (prep pod only)")


def _prep(project: str) -> Path:
    return Path(PREP_OUTPUTS) / project


def _building(project: str) -> dict:
    path = _prep(project) / "building.json"
    assert path.is_file(), f"{path} missing (pipeline_final did not run?)"
    return json.loads(path.read_text(encoding="utf-8"))


def _reference() -> dict:
    import yaml
    return yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))


def _accepted(types: list) -> set:
    """Reference ``type_accept`` -> schema types (the reference's ``plant`` is the schema's ``potted_plant``)."""
    return {"potted_plant" if t == "plant" else t for t in types or []}


@needs_prep
def test_m7_recognition_answers_complete():
    from wenart.recognition import answers as A
    summary, with_requests = {}, []
    for project in PREP_PROJECTS:
        rec = _prep(project) / "recognition"
        if not (rec / A.REQUESTS_NAME).is_file():
            summary[project] = None
            continue
        with_requests.append(project)
        summary[project] = A.status(rec)
    (RESULTS / "m7_recognition_status.json").write_text(json.dumps(summary, indent=1))
    assert "real01" in with_requests, "real01 wrote no recognition requests"
    incomplete = {p: s["models"] for p, s in summary.items() if s is not None and not s["complete"]}
    assert not incomplete, f"answers incomplete: {incomplete}"


@needs_prep
def test_m7_real01_ai_typing_is_mostly_right_and_never_verified_wrong():
    building = _building("real01")
    ref = [p for p in _reference()["furniture"] if not p.get("not_a_piece") and "centre_ft" in p]

    def match(piece):
        cx, cy = piece["footprint"]["center"]
        best, best_d = None, None
        for r in ref:
            rx, ry = (v * FT for v in r["centre_ft"])
            d = ((cx - rx) ** 2 + (cy - ry) ** 2) ** 0.5
            if d <= r["tol"]["centre"] * FT and (best_d is None or d < best_d):
                best, best_d = r, d
        return best

    asked, right, unmatched, wrong_verified, rows = 0, 0, [], [], []
    for piece in building["furniture"]:
        r = match(piece)
        ai = piece.get("type_method") == "ai_two_pass" or (piece.get("type_method") == "none"
                                                           and piece.get("type_candidates"))
        ok = r is not None and piece["type"] in _accepted(r.get("type_accept"))
        if r is not None and piece["status"] == "verified" and not ok:
            wrong_verified.append((piece["id"], piece["type"], r["id"]))
        if ai:
            if r is None:
                unmatched.append(piece["id"])
            else:
                asked += 1
                right += int(ok)
            rows.append({"id": piece["id"], "ref": r["id"] if r else None, "type": piece["type"],
                         "status": piece["status"], "candidates": piece.get("type_candidates")})
    (RESULTS / "m7_real01_ai_typing.json").write_text(json.dumps(
        {"asked_matched": asked, "right": right, "unmatched": unmatched, "wrong_verified": wrong_verified,
         "pieces": rows}, indent=1))
    assert not wrong_verified, f"verified with a type the reference does not accept: {wrong_verified}"
    assert asked >= 1, f"no AI-typed piece matched the reference (unmatched: {unmatched})"
    assert right >= 0.8 * asked, f"{right}/{asked} AI-typed pieces with an accepted type"


def _truth_rooms(project: str) -> list[dict]:
    """``[{"label", "bbox" (metres, building frame)}]`` of the labelled truth rooms of a raster project."""
    if project.startswith("real01"):
        return [{"label": r["label"], "bbox": [v * FT for v in r["bbox_ft"]]} for r in _reference()["rooms"]
                if r.get("label")]
    truth = json.loads((PROJECTS / project / "truth" / "building.json").read_text(encoding="utf-8"))
    out = []
    for r in truth["rooms"]:
        xs = [p[0] for p in r["polygon"]]
        ys = [p[1] for p in r["polygon"]]
        out.append({"label": r.get("label_raw") or r["label"], "bbox": [min(xs), min(ys), max(xs), max(ys)]})
    return out


@needs_prep
@pytest.mark.parametrize("project", [
    # Only the prep projects run (WENART_PREP_PROJECTS: the prep job leaves out a project it could not find);
    # the other raster projects are skipped, not failed.
    p if p in PREP_PROJECTS else pytest.param(p, marks=pytest.mark.skip(reason=f"{p} not in WENART_PREP_PROJECTS"))
    for p in sorted(RASTER_LABEL_TARGETS)])
def test_m7_raster_room_labels(project):
    from wenart.recognition.room_labels import norm_value
    if not (_prep(project) / "building.json").is_file():
        pytest.fail(f"{project}: no building.json in {_prep(project)}")
    building = _building(project)
    rooms = []
    for room in building["rooms"]:
        xs = [p[0] for p in room["polygon"]]
        ys = [p[1] for p in room["polygon"]]
        rooms.append((room, sum(xs) / len(xs), sum(ys) / len(ys)))
    right, rows = 0, []
    for t in _truth_rooms(project):
        x0, y0, x1, y1 = t["bbox"]
        inside = [r for r, cx, cy in rooms if x0 <= cx <= x1 and y0 <= cy <= y1]
        got = inside[0].get("label_raw") if inside else None
        ok = got is not None and norm_value(got) == norm_value(t["label"])
        right += int(ok)
        rows.append({"truth": t["label"], "got": got, "ok": ok})
    (RESULTS / f"m7_room_labels_{project}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    assert right >= RASTER_LABEL_TARGETS[project], f"{project}: {right}/{len(rows)} rooms with the right label: {rows}"
