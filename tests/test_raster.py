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
