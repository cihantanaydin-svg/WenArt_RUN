"""The source-plan crop of a raster project lands on the drawn plan (review cross-1; milestone7.md §4.1).

A raster page's units are the pixel corners of its *rectified* image with y up (``wenart.ingest.rectify.page_flip``),
so ``plan_crop`` draws on ``<project_out>/<rectified_image>``. Before the fix it drew on the original file with
``(x, y)`` as pixels: no y flip, no deskew, no photo homography, and the crops were 2-4 m off.

synthetic-02 (a scan and a phone photo of one plan) runs through the ingest once (no AI, about 1.5 min on the
cloud CPU). For both pages, building points mapped by ``PlanMapping`` land on the truth pixel of the generator
(``truth/pages.json`` ``H_building_to_pixels``, original image -> rectified image by the page's ``to_original``),
the exterior walls land on dark (drawn) pixels of the raster, and a room citing both files gets the scan.
"""
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pytest

from wenart import geometry as G
from wenart.ingest import pipeline as P
from wenart.ingest import rectify as RF
from wenart.vision_check import plan_crop as PC

ROOT = Path(__file__).resolve().parents[1]
S02 = ROOT / "projects" / "synthetic-02"
FILES = ("plan_scan.png", "plan_photo.jpg")
TRUTH_CORNERS = [(0.125, 0.125), (8.275, 6.475)]          # outer wall centre lines in the generator's frame


@pytest.fixture(scope="module")
def s02(tmp_path_factory):
    root = tmp_path_factory.mktemp("s02")
    project = root / "synthetic-02"
    (project / "truth").mkdir(parents=True)
    for f in FILES:
        shutil.copy(S02 / f, project / f)
    out = root / "out"
    building, _ = P.run_project(project, out, no_ai=True)
    assert building["status"] == "ok"
    return project, out, building


def truth_h(file: str) -> list:
    pages = json.loads((S02 / "truth" / "pages.json").read_text(encoding="utf-8"))["pages"]
    return next(p for p in pages if p["file"] == file)["H_building_to_pixels"]


def raster_px_of_original(page: dict, raster, xy) -> tuple:
    """An original-image pixel (OpenCV pixel centres) -> pixel corners of the plan-crop raster of ``page``, through
    the ingest's own conventions: ``to_original`` = rectified -> original @ ``page_flip(H)``."""
    H = int(page["_rect_size"][1])
    rect_to_orig = np.asarray(page["to_original"], np.float64) @ np.linalg.inv(RF.page_flip(H))
    cx, cy = G.apply_homography(np.linalg.inv(rect_to_orig).tolist(), xy)
    f = raster.image.width / float(page["_rect_size"][0])
    return ((cx + 0.5) * f, (cy + 0.5) * f)


def outer_corners(building: dict) -> list:
    xs = [c for w in building["walls"] for c in (w["start"][0], w["end"][0])]
    ys = [c for w in building["walls"] for c in (w["start"][1], w["end"][1])]
    t = max(w["thickness"] for w in building["walls"] if w.get("exterior")) / 2.0
    return [(min(xs) + t, min(ys) + t), (max(xs) - t, max(ys) - t)]


@pytest.mark.parametrize("file", FILES)
def test_a_raster_page_crop_puts_building_points_on_their_truth_pixels(s02, file):
    from PIL import Image

    project, out, building = s02
    doc = next(d for d in building["documents"] if d["file"] == file)
    page = dict(doc["pages"][0])
    assert page.get("rectified_image") and (out / page["rectified_image"]).is_file()
    with Image.open(out / page["rectified_image"]) as im:
        page["_rect_size"] = im.size
    path = PC.source_file(doc, project, out, page)
    assert path == out / page["rectified_image"]                          # never the original file
    raster = PC.load_raster(doc, page, path, out)
    room = next(r for r in building["rooms"] if r["id"].endswith("salon"))
    image, mapping = PC.render_plan_crop(raster, page, room, None, [], building)
    assert image is not None, mapping
    # The ingest's own convention, exactly: page point -> rectified pixel centre by ``page_flip`` (+ 0.5 for the
    # corner), times the downscale.
    W, H = page["_rect_size"]
    f = raster.image.width / float(W)
    to_page = G.invert_affine(page["transform_to_building"])
    for p in outer_corners(building) + [tuple(room["polygon"][0][:2])]:
        cx, cy = G.apply_homography(RF.page_flip(H).tolist(), G.apply_affine(to_page, p))
        assert mapping.to_raster_px(p) == pytest.approx(((cx + 0.5) * f, (cy + 0.5) * f), abs=1e-6)
    # The truth: the outer wall corners land on the generator's pixels (the bug put them 2-4 m off; 0.25 m covers
    # the extraction's own wall offsets, as test_raster's 0.15 m in original pixels).
    m_per_px = page["scale"]["metres_per_unit"] / f
    for p, q in zip(outer_corners(building), TRUTH_CORNERS):
        got = mapping.to_raster_px(p)
        want = raster_px_of_original(page, raster, G.apply_homography(truth_h(file), q))
        assert math.dist(got, want) * m_per_px <= 0.25, (file, p, got, want)
    # Independent of every convention: the exterior walls land on the drawn wall lines of the raster.
    grey = np.asarray(raster.image.convert("L"))
    dark = float(np.median(grey)) - 50.0                                # paper ~255 (scan) or ~225 (photo)
    for w in (w for w in building["walls"] if w.get("exterior")):
        hits = [dark_across(grey, dark, mapping, w, q) for q in wall_samples(building, w)]
        assert hits and sum(hits) >= 0.8 * len(hits), (file, w["id"], hits)


def wall_samples(building: dict, wall: dict) -> list:
    """Points on a wall's centre line (10 %, 20 %, ... 90 %) at least 0.1 m away from its openings."""
    a, b = wall["start"], wall["end"]
    gaps = [(o["center"], float(o["width"]) / 2.0 + 0.1) for o in building["openings"]
            if o.get("wall_id") == wall["id"]]
    out = []
    for k in range(1, 10):
        q = (a[0] + (b[0] - a[0]) * k / 10.0, a[1] + (b[1] - a[1]) * k / 10.0)
        if all(math.dist(q, c[:2]) > r for c, r in gaps):
            out.append(q)
    return out


def dark_across(grey, dark: float, mapping, wall: dict, q) -> bool:
    """A raster pixel darker than ``dark`` on the profile across the wall at ``q`` (its drawn faces at +- thickness
    / 2: the plans draw walls as two lines, grey after the downscale)."""
    (ax, ay), (bx, by) = wall["start"][:2], wall["end"][:2]
    n = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / n, (bx - ax) / n
    reach = float(wall["thickness"]) / 2.0 + 0.06
    for k in range(-15, 16):
        d = reach * k / 15.0
        x, y = (int(round(v)) for v in mapping.to_raster_px((q[0] + nx * d, q[1] + ny * d)))
        if 0 <= y < grey.shape[0] and 0 <= x < grey.shape[1] and grey[y, x] < dark:
            return True
    return False


def test_a_room_citing_the_scan_and_the_photo_gets_the_scan(s02):
    _, _, building = s02
    kinds = {d["file"]: d.get("source_kind") for d in building["documents"]}
    assert kinds == {"plan_scan.png": "raster_scan", "plan_photo.jpg": "raster_photo"}
    both = [r for r in building["rooms"]
            if {e.get("file") for e in r.get("evidence") or []} >= {"plan_scan.png", "plan_photo.jpg"}]
    assert both                                                          # e.g. the kitchen cites both
    for room in building["rooms"]:
        doc, _ = PC.plan_page(building, room["level_id"], room)
        assert doc["file"] == "plan_scan.png", room["id"]
