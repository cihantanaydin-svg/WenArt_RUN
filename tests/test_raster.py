"""Raster adapter (wenart/ingest/raster.py) and the raster path of the pipeline (docs/milestone7.md §4, §11 S).

Page level (synthetic-02 scan, read once): text blanking keeps the wall ink, dimension strokes are erased before the
outline-wall bands, the outline-wall mask has IoU >= 0.85 with the truth walls, door swings become arcs at the truth
doors. Filled walls: the real01 scan fixture (thick-framed objects dropped, IoU with the reference walls).

Project level (``--no-ai``): synthetic-02 (scan master, photo evidence only) and its photo alone against the §4.4
targets, synthetic-01 with its scan as an evidence-only page, the raster debug image on the original, a plan point on
the photo at its truth pixel, the real01 raster fixtures (size, deterministic regeneration). The real01 §4.4 runs with
fake label answers (two pipeline runs per fixture) are ``slow``.

§4.4 targets that the CPU path does not reach yet are ``xfail`` tests that print the measured value (furniture
footprint recall: the generic furniture clustering works with vector tolerances of 2-20 mm, below one raster pixel).

Metrics (building frame, metres):
- walls F1: the share of each side's centre-line length (sampled every 5 cm) that lies within 0.10 m of a parallel
  wall of the other side whose thickness is within 0.05 m (raster and vector pages split walls differently, so the
  match is by length, not by wall count);
- openings recall: kind (door / window / doorless) and centre within 0.20 m, one to one;
- furniture footprint recall: centre within 0.15 m and both sides within 0.15 m (sides sorted), one to one.
"""
import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np
import pytest
import yaml

from wenart import geometry as G
from wenart.ingest import pipeline as P
from wenart.ingest import raster as RA
from wenart.ingest import rectify as RF

from conftest import PROJECTS, ROOT, load_pages, load_truth

FIXTURES = ROOT / "tests" / "fixtures" / "real01_raster"
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"
PT_PER_FT = 12.4352                       # real01 reference scale
REF_ORIGIN_PT = (165.64, 459.84)          # house min corner: x from the left, y from the top of the page (points)


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def _cover(walls, others, centre_tol=0.10, thick_tol=0.05, step=0.05) -> float:
    total = hit = 0.0
    for w in walls:
        a, e = np.array(w["start"], float), np.array(w["end"], float)
        length = float(np.linalg.norm(e - a))
        if length <= 0:
            continue
        u = (e - a) / length
        for t in np.arange(step / 2, length, step):
            p = a + u * t
            total += step
            for o in others:
                if abs(o["thickness"] - w["thickness"]) > thick_tol:
                    continue
                oa, oe = np.array(o["start"], float), np.array(o["end"], float)
                olen = float(np.linalg.norm(oe - oa))
                if olen <= 0:
                    continue
                ou = (oe - oa) / olen
                if abs(u[0] * ou[1] - u[1] * ou[0]) > math.sin(math.radians(5)):
                    continue
                d = p - oa
                along, off = float(d @ ou), abs(float(d[0] * ou[1] - d[1] * ou[0]))
                if off <= centre_tol and -centre_tol <= along <= olen + centre_tol:
                    hit += step
                    break
    return hit / total if total else 0.0


def walls_f1(pred: dict, ref: dict) -> float:
    recall, precision = _cover(ref["walls"], pred["walls"]), _cover(pred["walls"], ref["walls"])
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _kind(o) -> str:
    return o["type"] if o["type"] in ("door", "window") else "opening"


def openings_recall(pred: dict, ref: dict, tol=0.20) -> tuple[float, list[str]]:
    used, missed = set(), []
    for o in ref["openings"]:
        best = min(((math.dist(p["center"], o["center"]), i) for i, p in enumerate(pred["openings"])
                    if i not in used and _kind(p) == _kind(o)), default=None)
        if best is not None and best[0] <= tol:
            used.add(best[1])
        else:
            missed.append(o["id"])
    n = len(ref["openings"])
    return (n - len(missed)) / n if n else 0.0, missed


def furniture_recall(pred: dict, ref: dict, tol=0.15, size_tol=0.15) -> tuple[float, list[str]]:
    used, missed = set(), []
    pieces = [f for f in ref["furniture"] if f.get("source", "from_documents") == "from_documents"]
    for f in pieces:
        fp = f["footprint"]
        best = None
        for i, p in enumerate(pred["furniture"]):
            pp = p["footprint"]
            d = math.dist(pp["center"], fp["center"])
            if i in used or d > tol or any(abs(x - y) > size_tol
                                          for x, y in zip(sorted(pp["size"]), sorted(fp["size"]))):
                continue
            if best is None or d < best[0]:
                best = (d, i)
        if best is None:
            missed.append(f["id"])
        else:
            used.add(best[1])
    return (len(pieces) - len(missed)) / len(pieces) if pieces else 0.0, missed


def _scale_error(building: dict, file: str, truth_mpu: float) -> float:
    page = next(p for d in building["documents"] if d["file"] == file for p in d["pages"])
    return abs(page["scale"]["metres_per_unit"] / truth_mpu - 1.0)


def _truth_px_per_m(project: str, file: str, rect: RF.Rectified) -> float:
    """Rectified pixels per metre of the truth (building x axis)."""
    h = np.linalg.inv(np.array(rect.to_original)) @ np.array(
        next(p for p in load_pages(project) if p["file"] == file)["H_building_to_pixels"])
    return math.dist(G.apply_homography(h.tolist(), (0.0, 0.0)), G.apply_homography(h.tolist(), (1.0, 0.0)))


def _truth_wall_mask(project: str, file: str, rect: RF.Rectified) -> np.ndarray:
    page = next(p for p in load_pages(project) if p["file"] == file)
    h = (np.linalg.inv(np.array(rect.to_original)) @ np.array(page["H_building_to_pixels"])).tolist()
    mask = np.zeros(rect.image.shape, np.uint8)
    for w in load_truth(project)["walls"]:
        if w["level_id"] != page["level_id"]:
            continue
        poly = [G.apply_homography(h, p) for p in G.centerline_to_rectangle(w["start"], w["end"], w["thickness"])]
        cv2.fillPoly(mask, [np.round(np.array(poly) * 16).astype(np.int32)], 1, shift=4)
    return mask > 0


# --------------------------------------------------------------------------
# Page level: synthetic-02 scan
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def s02_scan():
    return RA.read_page(PROJECTS / "synthetic-02" / "plan_scan.png", 1, "plan_scan.png", "scan")


def test_scan_page_reads_scale_and_texts(s02_scan):
    rp = s02_scan
    assert rp.rect.review is None and not rp.review
    truth_ppm = _truth_px_per_m("synthetic-02", "plan_scan.png", rp.rect)
    assert abs(rp.info["px_per_m"] / truth_ppm - 1.0) <= 0.02
    texts = {t.text for t in rp.page.texts}
    assert {"4,50", "3,90", "8,40", "6,60"} <= texts
    assert {"SALON", "MUTFAK", "BANYO"} <= {t.upper() for t in texts}
    # Every text run carries OCR evidence with its box in the original image.
    for run in rp.page.texts:
        ev = run.evidence[0]
        assert ev["method"] == "ocr" and len(ev["pixel_box"]) == 4 and run.source == "ocr"


def test_text_blanking_keeps_wall_ink(s02_scan):
    rp = s02_scan
    ink = RF.ink_mask(rp.image)
    blanked, n = RA.blank_texts(ink, rp.texts)
    walls = _truth_wall_mask("synthetic-02", "plan_scan.png", rp.rect)
    on_walls = ink & walls
    assert n >= 8
    assert (on_walls & ~blanked).sum() <= 0.002 * on_walls.sum()
    # The room names are gone; in a box whose letters touch a drawn line or swing only that line stays.
    names = [it for it in rp.texts if str(it["text"]).upper() in ("SALON", "MUTFAK", "BANYO", "ANTRE", "YATAK ODASI")]
    assert len(names) == 5 and all(it["blanked"] for it in names)
    for it in names:
        x0, y0, x1, y1 = (int(round(v)) for v in it["box"])
        assert blanked[y0:y1, x0:x1].sum() <= 0.2 * ink[y0:y1, x0:x1].sum(), it["text"]


def test_dimension_strokes_are_erased_before_the_wall_bands(s02_scan):
    rp = s02_scan
    dims = rp.info["dims"]
    assert len(dims) >= 5
    ids = {i for d in dims for i in d.stroke_ids}
    ink = RA.blank_texts(RF.ink_mask(rp.image), rp.texts)[0]
    erased = RA._erase_strokes(ink, rp.page.strokes, ids, rp.image.shape[0])
    h = rp.image.shape[0]
    for d in dims:
        (x1, y1), (x2, y2) = d.p1, d.p2
        n = int(math.dist(d.p1, d.p2))
        pts = [(x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n) for k in range(int(0.2 * n), int(0.8 * n))]
        before = sum(ink[int(round(h - y - 0.5)), int(round(x - 0.5))] for x, y in pts)
        after = sum(erased[int(round(h - y - 0.5)), int(round(x - 0.5))] for x, y in pts)
        assert before >= 0.8 * len(pts) and after <= 0.1 * len(pts), d.text


def test_outline_wall_mask_iou(s02_scan):
    rp = s02_scan
    assert rp.info["wall_style"] == "outline"
    mask = np.asarray(rp.page.wall_mask.mask, bool)
    truth = _truth_wall_mask("synthetic-02", "plan_scan.png", rp.rect)
    iou = (mask & truth).sum() / (mask | truth).sum()
    assert iou >= 0.85, iou


def test_door_swings_are_arcs_at_the_truth_doors(s02_scan):
    rp = s02_scan
    page = next(p for p in load_pages("synthetic-02") if p["file"] == "plan_scan.png")
    back = np.linalg.inv(np.array(rp.rect.to_original))
    h = rp.image.shape[0]
    arcs = [st for st in rp.page.strokes if st.arc]
    doors = [s for s in page["symbols"] if s["type"] == "door"]
    found = 0
    for door in doors:
        x0, y0, x1, y1 = door["box"]
        corners = [RF.apply_h(back, x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        cx0, cy0 = min(c[0] for c in corners) - 4, min(c[1] for c in corners) - 4
        cx1, cy1 = max(c[0] for c in corners) + 4, max(c[1] for c in corners) + 4
        size = max(cx1 - cx0, cy1 - cy0) - 8
        for st in arcs:
            cx, cy = st.arc["center"][0] - 0.5, h - st.arc["center"][1] - 0.5
            if cx0 <= cx <= cx1 and cy0 <= cy <= cy1 and abs(st.arc["radius"] / size - 1.0) <= 0.15:
                found += 1
                break
    assert found >= len(doors) - 1 and len(doors) == 5


# --------------------------------------------------------------------------
# Filled walls: the real01 scan fixture
# --------------------------------------------------------------------------

def _reference_walls_px(raster_json: dict, rect: RF.Rectified) -> np.ndarray:
    """The reference's wall rectangles minus its door and window spans (the drawing leaves those unfilled), in
    rectified pixels."""
    ref = yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))
    page_h = raster_json["page_size_pt"][1]
    to_px = (np.linalg.inv(np.array(rect.to_original)) @ np.array(raster_json["pdf_points_to_pixels"])).tolist()
    mask = np.zeros(rect.image.shape, np.uint8)

    def fill(x0, y0, x1, y1, value):
        pts = [G.apply_homography(to_px, (REF_ORIGIN_PT[0] + fx * PT_PER_FT,
                                          page_h - REF_ORIGIN_PT[1] + fy * PT_PER_FT))
               for fx, fy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        cv2.fillPoly(mask, [np.round(np.array(pts) * 16).astype(np.int32)], value, shift=4)

    for group in ref["walls"].values():
        for w in group if isinstance(group, list) else []:
            fill(*w["rect"], 1)
    for o in ref["doors"] + ref["windows"]:
        cx, cy = o["centre_ft"]
        if "span_x_ft" in o:
            fill(o["span_x_ft"][0], cy - 0.6, o["span_x_ft"][1], cy + 0.6, 0)
        elif "span_y_ft" in o:
            fill(cx - 0.6, o["span_y_ft"][0], cx + 0.6, o["span_y_ft"][1], 0)
    return mask > 0


@pytest.fixture(scope="module")
def r01_scan():
    return RA.read_page(FIXTURES / "real01-scan" / "real01_scan.png", 1, "real01_scan.png", "scan")


def test_filled_walls_of_the_real01_scan(r01_scan):
    rp = r01_scan
    raster_json = json.loads((FIXTURES / "real01-scan" / "truth" / "raster.json").read_text(encoding="utf-8"))
    assert rp.info["wall_style"] == "filled"
    # The coffee table's frame (thick on two sides) is a closed ink ring of < 2 m²: no wall.
    assert rp.info["filled_rings_dropped"] >= 1
    mask = np.asarray(rp.page.wall_mask.mask, bool)
    truth = _reference_walls_px(raster_json, rp.rect)
    ys, xs = np.nonzero(truth)
    house = np.zeros_like(truth)
    house[ys.min() - 5:ys.max() + 6, xs.min() - 5:xs.max() + 6] = True     # the plot wall lies outside the house
    iou = (mask & truth & house).sum() / ((mask & house) | truth).sum()
    assert iou >= 0.85, iou
    # Scale from the one readable dimension ('30') at 150 dpi: 12.4352 pt/ft.
    truth_ppm = 150.0 / 72.0 * PT_PER_FT / 0.3048
    assert abs(rp.info["px_per_m"] / truth_ppm - 1.0) <= 0.02


# --------------------------------------------------------------------------
# Project level
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def s02_project(tmp_path_factory):
    out = tmp_path_factory.mktemp("s02")
    building, build = P.run_project(PROJECTS / "synthetic-02", out, no_ai=True)
    return building, build, out


def test_synthetic_02_is_a_normal_project(s02_project):
    building, build, out = s02_project
    truth = load_truth("synthetic-02")
    assert building["status"] == "ok" and P.exit_code(building, build, no_ai=True) == P.EXIT_OK
    assert _scale_error(building, "plan_scan.png", 0.016933333333333335) <= 0.02
    assert walls_f1(building, truth) >= 0.9
    recall, missed = openings_recall(building, truth)
    assert recall >= 0.8 and "d_L0_001" not in missed, missed
    # --no-ai: the room labels are Tesseract's alone, unverified, with a room_label question each (§3.4).
    labels = {r["label"].upper() for r in building["rooms"] if r.get("label")}
    assert {"SALON", "MUTFAK", "BANYO", "ANTRE"} <= labels
    assert all(r["status"] == "unverified" for r in building["rooms"])
    tasks = [q["task"] for q in build.questions]
    assert tasks.count("room_label") == 5 and build.pending == []
    # The photo is evidence only: no question comes from it.
    assert not [q for q in build.questions if (q.get("context") or {}).get("file") == "plan_photo.jpg"]
    assert {(q.get("context") or {}).get("file") for q in build.questions} == {"plan_scan.png"}
    assert any("plan_photo.jpg (photo) is evidence only" in w for w in building["warnings"])
    # Raster evidence: method raster for the geometry, ocr for the scale.
    assert all(w["evidence"][0]["method"] == "raster" for w in building["walls"])
    page = next(p for d in building["documents"] if d["file"] == "plan_scan.png" for p in d["pages"])
    assert page["scale"]["method"] == "dimension_text" and page["scale"]["evidence"]["method"] == "ocr"


@pytest.mark.xfail(reason="§4.4 furniture footprint recall >= 0.8 on the synthetic-02 scan is not reached on the CPU "
                          "path (measured 0.63: kitchen sink/stove inside the counter, washbasin, nightstand and chair "
                          "merge with their neighbours)", strict=False)
def test_synthetic_02_scan_furniture_target(s02_project):
    building, _, _ = s02_project
    recall, missed = furniture_recall(building, load_truth("synthetic-02"))
    print("synthetic-02 scan furniture recall", round(recall, 3), missed)
    assert recall >= 0.8


def test_raster_debug_images_and_rectified_page(s02_project):
    building, _, out = s02_project
    for file in ("plan_scan.png", "plan_photo.jpg"):
        page = next(p for d in building["documents"] if d["file"] == file for p in d["pages"])
        stem = file.replace(".", "_")
        assert page["rectified_image"] == f"rectified/{stem}_p1.png" and (out / page["rectified_image"]).is_file()
        assert len(page["to_original"]) == 3
        debug = out / page["debug_image"]
        assert debug.is_file() and (out / "debug" / f"{stem}_p1_rectified.png").is_file()
        original = cv2.imread(str(PROJECTS / "synthetic-02" / file), cv2.IMREAD_GRAYSCALE)
        drawn = cv2.imread(str(debug))
        # Drawn on the original image (the photo keeps its perspective), scaled to the debug width.
        oh, ow = original.shape
        dh, dw = drawn.shape[:2]
        assert abs(dh - oh * dw / ow) <= 60
        small = cv2.resize(original, (dw, int(round(oh * dw / ow))), interpolation=cv2.INTER_AREA)
        grey = cv2.cvtColor(drawn, cv2.COLOR_BGR2GRAY)[60:small.shape[0]]
        assert np.corrcoef(grey.ravel().astype(float), small[60:grey.shape[0] + 60].ravel().astype(float))[0, 1] > 0.5


def test_synthetic_02_photo_alone(tmp_path):
    """The photo as the only page (§4.4 photo row) and a plan point on it at its truth pixel."""
    project = tmp_path / "s02photo"
    (project / "truth").mkdir(parents=True)
    shutil.copy(PROJECTS / "synthetic-02" / "plan_photo.jpg", project / "plan_photo.jpg")
    building, build = P.run_project(project, tmp_path / "out", no_ai=True)
    truth = load_truth("synthetic-02")
    assert building["status"] == "ok"
    assert walls_f1(building, truth) >= 0.8
    recall, missed = openings_recall(building, truth)
    assert recall >= 0.7, missed
    page = next(p for d in building["documents"] for p in d["pages"])
    rect = RF.rectify(cv2.imread(str(project / "plan_photo.jpg"), cv2.IMREAD_GRAYSCALE), "photo")
    truth_ppm = _truth_px_per_m("synthetic-02", "plan_photo.jpg", rect)
    assert abs(1.0 / page["scale"]["metres_per_unit"] / truth_ppm - 1.0) <= 0.03
    # Review cross-2: the photo's sheet ratio, snapped to ISO 2.7 % off the quad, is an assumed value: in the page
    # entry, the building warnings and report.md's assumed values; the page's notes are in report.md.
    aspect = page["aspect"]
    assert aspect["assumed"] is True and aspect["snapped"] == pytest.approx(math.sqrt(2.0), abs=1e-4)
    assert abs(aspect["measured"] / aspect["snapped"] - 1.0) == pytest.approx(aspect["off_pct"] / 100.0, abs=1e-3)
    assert any(w.startswith("plan_photo.jpg p1: photo aspect assumed") for w in building["warnings"])
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assumed = report.split("## Assumed values", 1)[1].split("\n## ", 1)[0]
    assert "plan_photo.jpg p1: photo aspect assumed" in assumed and "ISO" in assumed
    notes = report.split("## Notes", 1)[1].split("\n## ", 1)[0]
    assert "### plan_photo.jpg p1" in notes and "- aspect snapped to ISO" in notes
    assert "drawn details smaller than 0.2 m ignored" in notes
    # Review cross-5: --no-ai applies no answer; the questions are unanswered all the same (none pending).
    assert build.pending == [] and sorted(build.unanswered) == sorted(q["key"] for q in build.questions)
    assert (f"{len(build.questions)} without a complete pair of answers (--no-ai: not applied, they stay "
            f"unknown/unverified)") in report
    # Building metres -> page units (inverse transform) -> original photo pixels (to_original): the outer corners
    # of the building land on their truth pixels (the building frames agree within the wall tolerance).
    to_page = G.invert_affine(page["transform_to_building"])
    h_truth = next(p for p in load_pages("synthetic-02") if p["file"] == "plan_photo.jpg")["H_building_to_pixels"]
    xs = [c for w in building["walls"] for c in (w["start"][0], w["end"][0])]
    ys = [c for w in building["walls"] for c in (w["start"][1], w["end"][1])]
    ext = [w for w in building["walls"] if w.get("exterior")]
    t = max(w["thickness"] for w in ext) / 2.0
    corners = [(min(xs) + t, min(ys) + t), (max(xs) - t, max(ys) - t)]
    truth_corners = [(0.125, 0.125), (8.275, 6.475)]                    # outer wall centre lines in the truth
    for p, q in zip(corners, truth_corners):
        px = G.apply_homography(page["to_original"], G.apply_affine(to_page, p))
        qx = G.apply_homography(h_truth, q)
        assert math.dist(px, qx) <= 0.15 * truth_ppm, (p, px, qx)


@pytest.mark.xfail(reason="§4.4 photo furniture footprint recall >= 0.7 not reached on the CPU path (measured 0.47)",
                   strict=False)
def test_synthetic_02_photo_furniture_target(tmp_path):
    project = tmp_path / "s02photo"
    (project / "truth").mkdir(parents=True)
    shutil.copy(PROJECTS / "synthetic-02" / "plan_photo.jpg", project / "plan_photo.jpg")
    building, _ = P.run_project(project, tmp_path / "out", no_ai=True)
    recall, missed = furniture_recall(building, load_truth("synthetic-02"))
    print("synthetic-02 photo furniture recall", round(recall, 3), missed)
    assert recall >= 0.7


def test_synthetic_01_scan_is_evidence_only(tmp_path):
    building, build = P.run_project(PROJECTS / "synthetic-01", tmp_path / "out")
    truth = load_truth("synthetic-01")
    assert building["status"] == "ok" and P.exit_code(building, build) == P.EXIT_OK
    assert [c["kind"] for c in building["conflicts"]] == [c["kind"] for c in truth["conflicts"]]
    assert any("1_kat_scan.png (scan) is evidence only" in w for w in building["warnings"])
    # Evidence only: no questions from the scan (§0), and its evidence is attached to the PDF's elements.
    assert not [q for q in build.questions if (q.get("context") or {}).get("file") == "1_kat_scan.png"]
    raster_ev = [e for w in building["walls"] for e in w["evidence"] if e["file"] == "1_kat_scan.png"]
    assert raster_ev and all(e["method"] == "raster" for e in raster_ev)
    page = next(p for d in building["documents"] if d["file"] == "1_kat_scan.png" for p in d["pages"])
    assert page["class"] == "floor_plan" and page["level_id"] == "L1"


# --------------------------------------------------------------------------
# real01 raster fixtures
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name,file", [("real01-scan", "real01_scan.png"), ("real01-photo", "real01_photo.jpg")])
def test_real01_fixture_size_and_truth(name, file):
    path = FIXTURES / name / file
    total = sum(p.stat().st_size for p in (FIXTURES / name).rglob("*") if p.is_file())
    assert path.is_file() and total <= 1.5 * 1024 * 1024
    raster_json = json.loads((FIXTURES / name / "truth" / "raster.json").read_text(encoding="utf-8"))
    assert raster_json["file"] == file and raster_json["source_pdf"] == "projects/real01/real01.pdf"
    assert len(raster_json["pdf_points_to_pixels"]) == 3


def test_real01_fixtures_regenerate(tmp_path, monkeypatch):
    """``python -m wenart.synthetic.raster fixtures --pdf projects/real01/real01.pdf --page 1 --name real01`` gives
    the committed fixtures again (rasters by content, truth JSON exactly)."""
    from test_synthetic import rasters_match
    from wenart.synthetic import raster as SR

    monkeypatch.chdir(ROOT)
    SR.make_raster_fixtures(Path("projects/real01/real01.pdf"), 1, tmp_path, "real01")
    for name, file in (("real01-scan", "real01_scan.png"), ("real01-photo", "real01_photo.jpg")):
        assert rasters_match(FIXTURES / name / file, tmp_path / name / file), name
        a = json.loads((FIXTURES / name / "truth" / "raster.json").read_text(encoding="utf-8"))
        b = json.loads((tmp_path / name / "truth" / "raster.json").read_text(encoding="utf-8"))
        assert a == b


# --------------------------------------------------------------------------
# real01 raster fixtures against the vector result, fake label answers (slow)
# --------------------------------------------------------------------------

def _fake_label_answers(kind: str, out: Path) -> int:
    """Both passes answer each room_label request with the reference room under the crop centre (§3.4)."""
    from wenart.recognition import answers as A

    project = FIXTURES / f"real01-{kind}"
    raster_json = json.loads((project / "truth" / "raster.json").read_text(encoding="utf-8"))
    ref = yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))
    gray = cv2.imread(str(project / raster_json["file"]), cv2.IMREAD_GRAYSCALE)
    rect = RF.rectify(gray, kind)
    to_pt = np.linalg.inv(np.array(raster_json["pdf_points_to_pixels"]))
    page_h = raster_json["page_size_pt"][1]
    items = [it for it in A.read_requests(out / "recognition")["items"] if it["task"] == "room_label"]
    models = A.load_models()
    stores = {key: A.AnswerStore.for_model(out / "recognition", key, models) for key in A.MODEL_KEYS}
    for it in items:
        c0, r0, c1, r1 = it["context"]["crop"]["rect_px"]
        x, y = RF.apply_h(rect.to_original, (c0 + c1) / 2.0 - 0.5, (r0 + r1) / 2.0 - 0.5)
        xp, yp = G.apply_homography(to_pt.tolist(), (x, y))
        fx, fy = (xp - REF_ORIGIN_PT[0]) / PT_PER_FT, (yp - (page_h - REF_ORIGIN_PT[1])) / PT_PER_FT
        room = next((r for r in ref["rooms"] if r["bbox_ft"][0] <= fx <= r["bbox_ft"][2]
                     and r["bbox_ft"][1] <= fy <= r["bbox_ft"][3]), None)
        data = {"label": room["label"] if room else None, "size_text": room.get("label_size_text") if room else None,
                "area_text": None, "box": None}
        for store in stores.values():
            store.put(it["key"], {"task": it["task"], "input_sha256": it["input_sha256"], "data": data,
                                  "raw_text": json.dumps(data), "error": None, "attempts": 1, "latency_s": 0.0,
                                  "model": store.data["model"], "seed": 0, "images": it["images"]}, save=False)
    for store in stores.values():
        store.data["fake"] = True
        store.save()
    return len(items)


@pytest.fixture(scope="module")
def real01_vector(tmp_path_factory):
    return P.run_project(ROOT / "projects" / "real01", tmp_path_factory.mktemp("r01vec"), no_ai=True)[0]


@pytest.fixture(scope="module")
def real01_raster(tmp_path_factory):
    """kind -> (first run, building after the fake label answers), each computed once."""
    cache: dict = {}

    def get(kind: str):
        if kind not in cache:
            project = FIXTURES / f"real01-{kind}"
            out = tmp_path_factory.mktemp(f"r01{kind}")
            first, _ = P.run_project(project, out, no_ai=True)
            n = _fake_label_answers(kind, out)
            building, _ = P.run_project(project, out, answers=out / "recognition", no_ai=True)
            cache[kind] = (first, n, building)
        return cache[kind]
    return get


@pytest.mark.slow
@pytest.mark.parametrize("kind,targets", [("scan", (0.9, 0.8, 0.02)), ("photo", (0.8, 0.7, 0.03))])
def test_real01_raster_targets(kind, targets, real01_vector, real01_raster):
    project = FIXTURES / f"real01-{kind}"
    first, n_questions, building = real01_raster(kind)
    # One readable dimension: the provisional scale waits for >= 3 room-size labels, asked as questions (§3.4).
    assert first["status"] == "needs_review" and n_questions >= 7
    assert building["status"] == "ok", building["warnings"][-3:]
    walls_min, open_min, scale_max = targets
    assert walls_f1(building, real01_vector) >= walls_min
    recall, missed = openings_recall(building, real01_vector)
    assert recall >= open_min, missed
    raster_json = json.loads((project / "truth" / "raster.json").read_text(encoding="utf-8"))
    page = next(p for d in building["documents"] for p in d["pages"])
    rect = RF.rectify(cv2.imread(str(project / raster_json["file"]), cv2.IMREAD_GRAYSCALE), kind)
    h = np.linalg.inv(np.array(rect.to_original)) @ np.array(raster_json["pdf_points_to_pixels"])
    ppm = math.dist(G.apply_homography(h.tolist(), (0.0, 0.0)),
                    G.apply_homography(h.tolist(), (PT_PER_FT / 0.3048, 0.0)))
    assert abs(1.0 / page["scale"]["metres_per_unit"] / ppm - 1.0) <= scale_max
    labelled = [r for r in building["rooms"] if r.get("label") and r["status"] == "verified"]
    assert len(labelled) >= 6


@pytest.mark.slow
@pytest.mark.xfail(reason="§4.4 real01 raster furniture footprint recall (>= 0.8 scan, >= 0.7 photo) is not reached on "
                          "the CPU path (measured 0.30 scan, 0.20 photo: touching pieces stay one cluster)",
                   strict=False)
@pytest.mark.parametrize("kind,target", [("scan", 0.8), ("photo", 0.7)])
def test_real01_raster_furniture_target(kind, target, real01_vector, real01_raster):
    building = real01_raster(kind)[2]
    recall, missed = furniture_recall(building, real01_vector)
    print(f"real01-{kind} furniture recall", round(recall, 3), missed)
    assert recall >= target


# --------------------------------------------------------------------------
# Review fixes (M7 review 2): AI label boxes, size-pair pieces, transparent PNGs, resolution
# --------------------------------------------------------------------------

def _stroke(sid, pts):
    from wenart.ingest.generic.model import Stroke
    return Stroke(id=sid, kind="line", pts=list(pts), source="raster")


def test_an_ai_label_box_blanks_only_checked_glyph_ink():
    """raster-2: an agreed VLM label box removes strokes only when it is text-sized, inside its face and holds only
    letter-sized strokes; no box is ever invented; a refused box says why."""
    from shapely.geometry import box as sbox
    from wenart.ingest.generic import core

    s, height, text_h = 0.01, 1000.0, 20.0                  # 1 px = 1 cm, OCR texts 20 px (0.2 m) tall
    face = sbox(0.0, 0.0, 4.0, 4.0)
    label_box = [100.0, 870.0, 200.0, 900.0]                # page metres (1.0, 1.0)-(2.0, 1.3)
    glyphs = [_stroke(f"g{k}", [(1.1 + 0.1 * k, 1.05), (1.1 + 0.1 * k, 1.2)]) for k in range(5)]
    sofa_edge = _stroke("sofa", [(1.02, 1.02), (1.95, 1.02)])                  # 0.93 m: no letter
    ev = [{"method": "ai", "pass": 1}, {"method": "ai", "pass": 2}]

    run, why = core._blank_run("Drawing Room", "lbl_L0_4", label_box, face, s, height, glyphs, text_h, ev)
    assert why is None and run.source == "ai" and run.id == "ai:lbl_L0_4"
    assert run.box == pytest.approx((1.0, 1.0, 2.0, 1.3))
    # No box: nothing blanked, nothing invented.
    assert core._blank_run("Drawing Room", "k", None, face, s, height, glyphs, text_h, ev) == (None, None)
    # The whole crop (a loose box around the room) is not a label.
    run, why = core._blank_run("Drawing Room", "k", [0.0, 0.0, 1000.0, 1000.0], face, s, height, glyphs, text_h, ev)
    assert run is None and "larger than the label's text" in why
    # A text-sized box over a drawn piece would delete it: refused, the strokes stay.
    run, why = core._blank_run("Drawing Room", "k", label_box, face, s, height, glyphs + [sofa_edge], text_h, ev)
    assert run is None and "1 drawn strokes larger than a letter" in why and "sofa" in why
    # Outside the face, or without an OCR text height to compare with: refused.
    assert core._blank_run("Drawing Room", "k", [500.0, 870.0, 600.0, 900.0], face, s, height, glyphs, text_h,
                           ev)[1] == "the box lies outside its room face"
    assert core._blank_run("Drawing Room", "k", label_box, face, s, height, glyphs, 0.0, ev)[0] is None


def test_the_agreed_label_box_is_where_both_passes_point():
    """raster-2: on the two-pass path the box is the intersection of the passes' boxes (keep what agrees)."""
    from wenart.ingest.generic import core

    def decision(path, boxes, match=None):
        return {"fields": {"label": {"path": path, "tesseract_match": match}},
                "evidence": [{"method": "ai", "pixel_box": b} for b in boxes]}

    assert core._agreed_box_px(decision("two_pass", [[0, 0, 100, 50], [20, 10, 200, 40]])) == [20, 10, 100, 40]
    assert core._agreed_box_px(decision("two_pass", [[0, 0, 100, 50], None])) is None
    assert core._agreed_box_px(decision("two_pass", [[0, 0, 10, 10], [20, 20, 30, 30]])) is None
    assert core._agreed_box_px(decision("tesseract", [None, None], {"box": [5, 6, 7, 8]})) == [5, 6, 7, 8]
    assert core._agreed_box_px(decision(None, [[0, 0, 1, 1]])) is None


def test_size_pair_pieces_never_become_dimension_texts():
    """raster-6: "11' x 10'" read in two pieces ("11" at 0.96, then "x 10") is one size text, never the length 11."""
    from wenart import units as U

    rect = RF.Rectified(image=np.full((400, 600), 255, np.uint8), to_original=np.eye(3).tolist(), kind="scan",
                        original_size=(600, 400))
    items = [{"text": "11", "box": [100.0, 100.0, 124.0, 121.0], "confidence": 0.96, "rotation": 0, "source": "page"},
             {"text": "x 10", "box": [131.0, 101.0, 172.0, 121.0], "confidence": 0.92, "rotation": 0,
              "source": "page"},
             {"text": "30", "box": [300.0, 300.0, 324.0, 321.0], "confidence": 0.97, "rotation": 0, "source": "page"},
             {"text": "x 9", "box": [400.0, 300.0, 430.0, 321.0], "confidence": 0.9, "rotation": 0, "source": "page"}]
    runs, _ = RA.text_runs(items, rect, "scan.png", 1)
    lengths = [r.text for r in runs if U.parse_length(r.text) is not None]
    assert "11" not in lengths and lengths == ["30"]                  # "x 9" is too far from the "30" to join
    pair = next(r for r in runs if r.text == "11 x 10")
    assert U.parse_size_pair(pair.text) is not None and pair.evidence[0]["confidence"] == 0.92
    # Vertical texts (rotation 90) read bottom to top.
    vertical = [{"text": "11", "box": [100.0, 300.0, 121.0, 324.0], "confidence": 0.96, "rotation": 90},
                {"text": "x 10", "box": [100.0, 252.0, 121.0, 294.0], "confidence": 0.92, "rotation": 90}]
    assert [i["text"] for i in RA.join_size_pairs(vertical)] == ["11 x 10"]


def test_a_transparent_png_is_read_on_white_paper(tmp_path):
    """raster-8: ink opaque, paper fully transparent (RGB 0 under alpha 0) is a normal page, not all ink."""
    from wenart.ingest import classify as CL

    grey = cv2.imread(str(FIXTURES / "real01-scan" / "real01_scan.png"), cv2.IMREAD_GRAYSCALE)
    small = cv2.resize(grey, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    rgba = np.zeros(small.shape + (4,), np.uint8)
    rgba[..., 3] = 255 - small                                      # ink opaque, paper transparent, colour black
    path = tmp_path / "transparent.png"
    cv2.imwrite(str(path), rgba)
    assert cv2.imread(str(path), cv2.IMREAD_GRAYSCALE).mean() < 10   # the plain grey read: all ink
    page, _, _ = RA.load_image(path)
    assert abs(float(page.mean()) - float(small.mean())) < 2.0 and RF.ink_mask(page).mean() < 0.2
    assert np.abs(page.astype(int) - small.astype(int)).max() <= 1
    # An image without alpha is read exactly as before; the classifier sees the transparent page like it.
    plain = tmp_path / "plain.png"
    cv2.imwrite(str(plain), small)
    assert np.array_equal(RA.load_image(plain)[0], small)
    assert CL.raster_kind(path) == CL.raster_kind(plain) and CL.raster_kind(path)[1] != "no paper outline found"


def test_a_page_twice_the_resolution_is_read_at_the_working_resolution(tmp_path):
    """raster-6: the real01 scan at 2x its pixels (a 300 dpi scan) is resampled to the working resolution; the
    rectification still maps to the file as given (pixel centres)."""
    grey = cv2.imread(str(FIXTURES / "real01-scan" / "real01_scan.png"), cv2.IMREAD_GRAYSCALE)
    assert RA.working_resolution(grey)[1] == (1.0, 1.0)              # the 150 dpi fixture stays as it is
    big = cv2.resize(grey, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    work, (fx, fy), note = RA.working_resolution(big)
    assert 0.4 <= fx <= 0.6 and abs(fx - fy) < 0.002 and "working resolution" in note
    assert work.shape == (int(round(big.shape[0] * fy)), int(round(big.shape[1] * fx)))
    rect = RF.rectify(work, "scan")
    full = RA._in_original(rect, (fx, fy), (big.shape[1], big.shape[0]))
    assert full.original_size == (big.shape[1], big.shape[0])
    # A work pixel centre maps to the original through the rectification and the resampling.
    x, y = 400.0, 300.0
    wx, wy = RF.apply_h(rect.to_original, x, y)
    ox, oy = RF.apply_h(full.to_original, x, y)
    assert ox == pytest.approx((wx + 0.5) / fx - 0.5, abs=1e-6) and oy == pytest.approx((wy + 0.5) / fy - 0.5, abs=1e-6)


def _fake_symbol_answers(out: Path, stores: dict) -> int:
    """Both passes answer every symbol_type request "unknown" (a complete, non-agreeing-on-a-type answer set)."""
    from wenart.recognition import answers as A

    n = 0
    data = {"type": "unknown", "front": "none", "confidence": 0.2, "reason": "fake answer"}
    for it in A.read_requests(out / "recognition")["items"]:
        if it["task"] != "symbol_type":
            continue
        n += 1
        for store in stores.values():
            store.put(it["key"], {"task": it["task"], "input_sha256": it["input_sha256"], "data": dict(data),
                                  "raw_text": json.dumps(data), "error": None, "attempts": 1, "latency_s": 0.0,
                                  "model": store.data["model"], "seed": 0, "images": it["images"]}, save=False)
    return n


@pytest.mark.slow
def test_real01_scan_two_rounds_with_complete_answers_never_exit_4(tmp_path):
    """raster-1 / ingest-1: a one-dimension raster scale waits for the room-size labels, yet round 1 asks every
    question (§1.4: one round), so the run with complete answers exits 0. The same run checks raster-2 (a loose VLM
    label box deletes no drawn furniture), raster-3 (two passes against Tesseract's name: a conflict, OCR kept) and
    raster-5 (room-label evidence boxes in the original image's pixels)."""
    from wenart.recognition import answers as A
    from wenart.recognition import room_labels as RL

    project = FIXTURES / "real01-scan"
    out = tmp_path / "out"
    first, build1 = P.run_project(project, out)
    tasks = [q["task"] for q in build1.questions]
    assert first["status"] == "needs_review" and P.exit_code(first, build1) == P.EXIT_QUESTIONS
    assert tasks.count("room_label") >= 7 and tasks.count("symbol_type") >= 5
    assert sorted(build1.pending) == sorted(q["key"] for q in build1.questions)

    _fake_label_answers("scan", out)
    items = {it["key"]: it for it in A.read_requests(out / "recognition")["items"]}
    models = A.load_models()
    stores = {key: A.AnswerStore.for_model(out / "recognition", key, models) for key in A.MODEL_KEYS}
    by_label = {stores["qwen"].calls[k]["data"]["label"]: k for k, it in items.items() if it["task"] == "room_label"}
    pooja_box = [250, 300, 750, 700]
    for store in stores.values():
        store.calls[by_label["Drawing Room"]]["data"]["box"] = [0, 0, 1000, 1000]   # a loose box: the whole crop
        store.calls[by_label["Kitchen"]]["data"]["label"] = "Pantry"                # both passes vs Tesseract
        store.calls[by_label["Pooja"]]["data"]["box"] = list(pooja_box)
    assert _fake_symbol_answers(out, stores) == tasks.count("symbol_type")
    for store in stores.values():
        store.save()
    assert A.is_complete(A.load(out / "recognition"))

    building, build2 = P.run_project(project, out, answers=out / "recognition")
    assert building["status"] == "ok", [w for w in building["warnings"] if "review" in w]
    assert P.exit_code(building, build2) == P.EXIT_OK and build2.pending == []
    # raster-3: OCR outranks AI.
    kitchen = next(r for r in building["rooms"] if r["label_raw"] == "Kitchen")
    assert kitchen["status"] == "unverified" and not any(r["label_raw"] == "Pantry" for r in building["rooms"])
    assert any(c["kind"] == "other" and kitchen["id"] in c["element_ids"] and "'Pantry'" in c["description"]
               and "'Kitchen'" in c["description"] for c in building["conflicts"])
    # raster-2: the loose box of the drawing room removed none of its drawn pieces.
    drawing = next(r for r in building["rooms"] if (r["label_raw"] or "").startswith("Drawing Room"))
    assert sum(1 for f in building["furniture"] if f["room_id"] == drawing["id"]) >= 5
    # raster-5: the passes' box of the pooja label points at the original scan, not the rectified page.
    rect = RF.rectify(cv2.imread(str(project / "real01_scan.png"), cv2.IMREAD_GRAYSCALE), "scan")
    rectified = RL.box_to_page(pooja_box, items[by_label["Pooja"]]["context"]["crop"])
    expected = RA._to_original_box(rect, rectified)
    assert max(abs(a - b) for a, b in zip(expected, rectified)) > 2.0
    pooja = next(r for r in building["rooms"] if r["label_raw"] == "Pooja")
    ai = [e for e in pooja["evidence"] if e["method"] == "ai"]
    assert len(ai) == 2 and all(e["pixel_box"] == pytest.approx(expected, abs=0.11) for e in ai)


def test_a_raster_page_without_furniture_still_asks_its_room_labels(tmp_path, monkeypatch):
    """raster-4: the room_label questions of a raster master page are written (and pending) when the page draws no
    furniture: the pipeline exits 4 instead of keeping every room on Tesseract alone."""
    from wenart.ingest.generic import core

    real = core.SY.furniture

    def no_furniture(*args, **kwargs):
        _, _, decor = real(*args, **kwargs)
        return [], [], decor

    monkeypatch.setattr(core.SY, "furniture", no_furniture)
    project = tmp_path / "s02scan"
    project.mkdir()
    shutil.copy(PROJECTS / "synthetic-02" / "plan_scan.png", project / "plan_scan.png")
    building, build = P.run_project(project, tmp_path / "out")
    assert building["status"] == "ok" and building["furniture"] == []
    assert [q["task"] for q in build.questions] == ["room_label"] * 5 and len(build.pending) == 5
    assert P.exit_code(building, build) == P.EXIT_QUESTIONS
    from wenart.recognition import answers as A
    assert len(A.read_requests(tmp_path / "out" / "recognition")["items"]) == 5


@pytest.mark.slow
def test_real01_scanned_at_300_dpi_reads_like_the_150_dpi_fixture(tmp_path):
    """raster-6: the same real01 page scanned at 300 dpi (the fixture's seed, noise and rotation) is read at the
    working resolution: its dimension texts give the provisional scale (within 2 % of the truth) and every room
    face is asked for its label, as at 150 dpi (needs_review waiting for the answers, exit 4); the review names no
    unreadable dimension."""
    from wenart.synthetic import raster as SR

    pdf = ROOT / "projects" / "real01" / "real01.pdf"
    _, page_h = SR._page_size_pt(pdf, 1)
    project = tmp_path / "r01_300"
    project.mkdir()
    SR.make_scan(pdf, 1, page_h, project / "real01_scan_300.png", seed=SR.FIXTURE_SCAN_SEED, dpi=300)
    building, build = P.run_project(project, tmp_path / "out")
    tasks = [q["task"] for q in build.questions]
    assert P.exit_code(building, build) == P.EXIT_QUESTIONS and tasks.count("room_label") >= 7
    assert not any("no dimension readable" in r for r in build.review_reasons)
    ex = build.question_only[0]
    rp = ex.report["raster_page"]
    assert any("working resolution" in n for n in rp.notes)
    fx = 1.0 / math.hypot(rp.rect.to_original[0][0], rp.rect.to_original[1][0])     # work / original pixels
    truth_m_per_work_px = 0.3048 / (300.0 / 72.0 * PT_PER_FT) / fx
    assert abs(ex.report["units_to_m"] / truth_m_per_work_px - 1.0) <= 0.02


def test_raster_wall_joints_a_pixel_open_are_closed():
    """P7 (real01 scan: the bath wall ended 5 mm short of the bath's west wall, so the bath and the hall were one
    face and the bath's label went to the wrong room): a raster wall end that stops <= 1.5 px short of another
    wall's face is moved onto it; door-wide gaps, parallel neighbours and joined ends stay."""
    from wenart.ingest.generic import core
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import WallItem

    def wall(a, b, t=0.15):
        return WallItem(start=a, end=b, thickness=t, box=[0, 0, 0, 0], entity="raster", evidence={})

    s = 0.012                                                   # metres per pixel: tolerance 18 mm
    west, east = wall((0.0, 0.0), (0.0, 4.0)), wall((3.0, 0.0), (3.0, 4.0))     # faces at x = 0.075 and 2.925
    south, north = wall((0.0, 0.0), (3.0, 0.0)), wall((0.0, 4.0), (3.0, 4.0))
    short = wall((0.08, 2.0), (2.925, 2.0))                     # 5 mm short of the west wall
    room = [west, east, south, north, short]
    assert len([f for f in TP.faces(room) if f.area > 0.5]) == 1                 # one face through the slit
    run_a, run_b = wall((5.0, 2.0), (6.0, 2.0)), wall((6.005, 2.0), (7.0, 2.0))  # a run, 5 mm apart: no joint
    far = wall((5.0, 0.0), (5.0, 1.0)), wall((5.825, 0.5), (7.0, 0.5))           # 0.75 m short: a passage
    walls = room + [run_a, run_b, *far]
    moved = core._close_raster_joints(walls, core.RASTER_JOINT_PX * s)
    assert moved == ["wall 4 start +5 mm"]
    assert short.start == pytest.approx((0.075, 2.0)) and short.end == (2.925, 2.0)
    assert run_a.end == (6.0, 2.0) and run_b.start == (6.005, 2.0) and far[1].start == (5.825, 0.5)
    # The bath and the hall are two faces now.
    assert len([f for f in TP.faces(room) if f.area > 0.5]) == 2
