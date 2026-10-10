"""Milestone 12 track B: the audit render's pure parts (docs/milestone12.md §6.1 thumbnails, ``render.py``): the scale
reference, the cameras, the jobs and resume, the worker split, the sheet with its printed header, the texture grid.
Blender itself runs on the pod (``tests/gpu/test_library.py``)."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from wenart.assets.audit import load_config
from wenart.assets.audit import render as R

S = load_config()["render"]


def test_person_and_seat_bar_heights_are_exact():
    person = R.person_boxes(1.75, x=-1.0)
    assert max(b["max"][2] for b in person) == 1.75
    assert min(b["min"][2] for b in person) == 0.0
    width = max(b["max"][0] for b in person) - min(b["min"][0] for b in person)
    assert 0.5 < width < 0.65
    bar = R.seat_bar_boxes(0.45, x=0.3)
    assert max(b["max"][2] for b in bar) == 0.45


def test_grid_lines_are_on_the_step():
    lines = R.grid_lines(-1.2, 1.2, -0.7, 0.7, 0.5, 0.01)
    xs = sorted({round((b["min"][0] + b["max"][0]) / 2, 3) for b in lines if b["max"][1] - b["min"][1] > 1.0})
    assert xs == [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]


def test_layout_puts_the_references_left_of_the_model_and_skips_the_person_for_small_items():
    lay = R.reference_layout([2.0, 0.9, 0.85], S)
    assert lay["grid_m"] == 0.5 and lay["person"] and not lay["small"]
    model_left = lay["model"]["min"][0]
    assert max(b["max"][0] for b in lay["person"] + lay["bar"]) < model_left
    assert lay["frame"]["max"][2] == 1.75
    small = R.reference_layout([0.15, 0.15, 0.25], S)
    assert small["small"] and small["person"] == [] and small["grid_m"] == 0.1


def test_four_cameras_front_side_top_back():
    lay = R.reference_layout([2.0, 0.9, 0.85], S)
    cams = R.camera_specs(lay, S)
    assert [c["view"] for c in cams] == list(R.VIEWS)
    front, side, top, back = cams
    assert front["type"] == "persp" and front["location"][1] < 0 and front["location"][0] < front["target"][0]
    assert side["type"] == "ortho" and side["location"][0] > lay["frame"]["max"][0]
    assert top["type"] == "ortho" and top["location"][2] > lay["frame"]["max"][2]
    assert back["location"][1] > 0
    ext = [b - a for a, b in zip(lay["frame"]["min"], lay["frame"]["max"])]
    assert top["ortho_scale"] >= max(ext[0], ext[1]) and side["ortho_scale"] >= max(ext[1], ext[2])


def test_deal_is_round_robin():
    assert R.deal(list(range(7)), 3) == [[0, 3, 6], [1, 4], [2, 5]]
    assert R.deal([1], 4) == [[1]]
    assert R.deal([], 2) == []


def test_jobs_skip_missing_files_and_current_measurements(tmp_path):
    assets, work = tmp_path / "assets", tmp_path / "work"
    (assets / "models" / "abo").mkdir(parents=True)
    (assets / "models" / "abo" / "a.glb").write_bytes(b"glTF")
    items = [{"id": "a", "type": "sofa", "kind": "furniture", "glb": "models/abo/a.glb", "sha256_glb": "1" * 64,
              "bbox_m": [2.0, 0.9, 0.85], "unit_scale": 1.0, "origin_offset": [0, 0, 0], "front_axis": "-Y"},
             {"id": "b", "type": "sofa", "kind": "furniture", "glb": "models/abo/b.glb", "bbox_m": [2, 1, 1]}]
    doc = R.render_jobs(items, assets, work, S)
    assert [j["id"] for j in doc["jobs"]] == ["a"] and doc["missing"][0]["id"] == "b"
    job = doc["jobs"][0]
    assert len(job["cameras"]) == 4 and len(job["views"]) == 4 and job["rot_deg"] == 0.0
    assert job["attempt"] == 1
    R.measure_path(work, "a").parent.mkdir(parents=True)
    R.measure_path(work, "a").write_text(json.dumps({"id": "a", "job_sha": job["job_sha"], "ok": False,
                                                     "attempts": 1}))
    again = R.render_jobs(items, assets, work, S)["jobs"]
    assert [(j["id"], j["attempt"]) for j in again] == [("a", 2)]          # a failure is tried once more
    R.measure_path(work, "a").write_text(json.dumps({"id": "a", "job_sha": job["job_sha"], "ok": False,
                                                     "attempts": 2}))
    assert R.render_jobs(items, assets, work, S)["skipped"] == ["a"]           # resume: current, not again
    items[0]["unit_scale"] = 0.5
    assert [j["id"] for j in R.render_jobs(items, assets, work, S)["jobs"]] == ["a"]   # changed scale: again


def fake_blender(tmp_path, started, crash_on=None):
    """A Popen stand-in: it 'renders' its chunk (writes the measurements) and dies on ``crash_on``."""
    class P:
        def __init__(self, cmd, stdout=None, stderr=None):
            started.append(cmd)
            doc = json.loads(Path(cmd[-1]).read_text())
            self.code = 0
            for job in doc["jobs"]:
                if job["id"] == crash_on:
                    self.code = -11
                    break
                R.measure_path(tmp_path, job["id"]).parent.mkdir(parents=True, exist_ok=True)
                R.measure_path(tmp_path, job["id"]).write_text(json.dumps({"id": job["id"], "job_sha": job["job_sha"],
                                                                           "ok": True}))

        def wait(self):
            return self.code
    return P


def test_run_render_starts_one_process_per_chunk(tmp_path):
    started = []
    doc = {"jobs": [{"id": str(i), "job_sha": "s"} for i in range(5)], "settings": {}, "work": str(tmp_path)}
    P = fake_blender(tmp_path, started)
    assert R.run_render(doc, "blender", tmp_path, workers=2, log=lambda *a: None, popen=P) == 0
    assert len(started) == 2 and started[0][-1].endswith("jobs_0.json")
    assert [j["id"] for j in json.loads((tmp_path / "jobs" / "jobs_1.json").read_text())["jobs"]] == ["1", "3"]


def test_a_model_that_crashes_blender_is_recorded_and_the_rest_rendered(tmp_path):
    started = []
    doc = {"jobs": [{"id": str(i), "job_sha": "s"} for i in range(5)], "settings": {}, "work": str(tmp_path)}
    P = fake_blender(tmp_path, started, crash_on="2")
    assert R.run_render(doc, "blender", tmp_path, workers=2, log=lambda *a: None, popen=P) == 0   # recorded
    rec = json.loads(R.measure_path(tmp_path, "2").read_text())
    assert rec["ok"] is False and "Blender stopped" in rec["error"] and rec["attempts"] >= R.MAX_ATTEMPTS
    assert json.loads(R.measure_path(tmp_path, "4").read_text())["ok"] is True     # dealt again in round 2
    assert len(started) == 3


def test_sheet_has_four_views_and_a_printed_header(tmp_path):
    views = []
    for i, c in enumerate([(200, 0, 0), (0, 200, 0), (0, 0, 200), (200, 200, 0)]):
        p = tmp_path / f"v{i}.png"
        Image.new("RGB", (64, 64), c).save(p)
        views.append(p)
    it = {"id": "abo_x", "type": "sofa", "source": "abo", "licence": "CC-BY-4.0", "title": "Çift kişilik kanepe"}
    lines = R.header_lines(it, [1.97, 0.83, 0.83], 0.5, False)
    assert "W 1.97 x D 0.83 x H 0.83 m" in lines[1] and "person 1.75 m" in lines[1]
    assert lines[2] == "Cift kisilik kanepe"
    out = tmp_path / "s.jpg"
    px = R.compose_sheet(views, lines, out, tile=128)
    img = np.asarray(Image.open(out).convert("RGB"))
    band = 26 * 3 + 12
    assert img.shape == (band + 256, 256, 3) and len(px["sha256"]) == 64
    assert (img[:band] < 100).any()                                   # text printed in the header band
    assert img[band + 100, 100, 0] > 150 and img[band + 100, 100, 1] < 80   # the first view, red, top left


def test_texture_overlay_draws_a_line_every_10_cm():
    arr = R.texture_overlay(np.zeros((100, 100, 3), dtype=np.uint8), 100, 0.1)
    cols = [x for x in range(100) if arr[50, x].sum() > 0]
    assert len(cols) >= 11 and 0 in cols and 99 in cols and 49 in cols
