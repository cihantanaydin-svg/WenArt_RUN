"""Raster rectification (wenart/ingest/rectify.py, docs/milestone7.md §4.1, §11 S).

- Photo: the page quad of the synthetic-02 photo lies within 1 % of the side of the true sheet corners (the
  generator's scan -> photo homography, recovered from ``truth/pages.json``); after rectification the building's
  x and y axes have the same pixels per metre within 0.5 % and stay axis-parallel.
- Scan: deskew undoes the generator's rotation, and ``to_original`` maps the rectified image back onto the original:
  the truth label boxes found again in the original lie within 2 px of where ``to_original`` puts them.
- Small units: sheet-ratio snapping, the deskew limit, a photo without a sheet, the page frame (y up).
"""
import math

import cv2
import numpy as np
import pytest

from wenart import geometry as G
from wenart.ingest import rectify as RF

from conftest import PROJECTS, load_pages


def _page(project: str, file: str) -> dict:
    return next(p for p in load_pages(project) if p["file"] == file)


def _gray(project: str, file: str) -> np.ndarray:
    return cv2.imread(str(PROJECTS / project / file), cv2.IMREAD_GRAYSCALE)


@pytest.fixture(scope="module")
def photo():
    gray = _gray("synthetic-02", "plan_photo.jpg")
    return gray, RF.rectify(gray, "photo")


@pytest.fixture(scope="module")
def scan():
    gray = _gray("synthetic-02", "plan_scan.png")
    return gray, RF.rectify(gray, "scan")


def test_photo_quad_corners_within_one_percent(photo):
    gray, rect = photo
    h_photo = np.array(_page("synthetic-02", "plan_photo.jpg")["H_building_to_pixels"])
    h_scan = np.array(_page("synthetic-02", "plan_scan.png")["H_building_to_pixels"])
    persp = h_photo @ np.linalg.inv(h_scan)                      # scan pixels -> photo pixels (the generator's warp)
    h, w = gray.shape
    truth = [RF.apply_h(persp, x, y) for x, y in ((0, 0), (w, 0), (w, h), (0, h))]
    assert rect.review is None and rect.quad is not None
    quad = rect.quad
    for k in range(4):
        side = max(math.dist(truth[k], truth[(k + 1) % 4]), math.dist(truth[k], truth[(k - 1) % 4]))
        assert math.dist(quad[k], truth[k]) <= 0.01 * side, (k, quad[k], truth[k])


def test_photo_rectified_axes_have_equal_scale(photo):
    _, rect = photo
    h_photo = _page("synthetic-02", "plan_photo.jpg")["H_building_to_pixels"]
    back = np.linalg.inv(np.array(rect.to_original)).tolist()

    def b2r(p):
        return G.apply_homography(back, G.apply_homography(h_photo, p))

    o, x, y = b2r((0.0, 0.0)), b2r((8.4, 0.0)), b2r((0.0, 6.6))
    sx, sy = math.dist(o, x) / 8.4, math.dist(o, y) / 6.6
    assert abs(sx / sy - 1.0) <= 0.005, (sx, sy)
    # Axis-parallel after the deskew: x runs right, y (building up) runs up the image.
    assert abs(math.degrees(math.atan2(x[1] - o[1], x[0] - o[0]))) <= 0.3
    assert abs(math.degrees(math.atan2(o[0] - y[0], o[1] - y[1]))) <= 0.3
    assert rect.aspect["snapped"] == pytest.approx(math.sqrt(2.0), rel=1e-6) and rect.aspect["assumed"]


def test_scan_deskew_undoes_the_generator_rotation(scan):
    _, rect = scan
    h_scan = _page("synthetic-02", "plan_scan.png")["H_building_to_pixels"]
    rotation = math.degrees(math.atan2(h_scan[1][0], h_scan[0][0]))
    back = np.linalg.inv(np.array(rect.to_original)).tolist()
    o = G.apply_homography(back, G.apply_homography(h_scan, (0.0, 0.0)))
    x = G.apply_homography(back, G.apply_homography(h_scan, (8.4, 0.0)))
    assert abs(rotation) > 0.3                                    # the fixture really is rotated
    assert abs(math.degrees(math.atan2(x[1] - o[1], x[0] - o[0]))) <= 0.1
    assert abs(abs(rect.angle_deg) - abs(rotation)) <= 0.1


@pytest.mark.parametrize("project,file", [("synthetic-02", "plan_scan.png"), ("synthetic-02", "plan_photo.jpg"),
                                          ("synthetic-01", "1_kat_scan.png")])
def test_to_original_maps_label_boxes_back_within_2px(project, file):
    """The rectified image carried back to the original frame through ``to_original``: each truth text box's patch
    is found in the original image within 2 px of the box."""
    gray = _gray(project, file)
    kind = "photo" if file.endswith(".jpg") else "scan"
    rect = RF.rectify(gray, kind)
    h, w = gray.shape
    # to_original maps rectified pixels onto the original: warping by it carries the rectified image back.
    back = cv2.warpPerspective(rect.image, np.array(rect.to_original, dtype=np.float64), (w, h),
                               flags=cv2.INTER_LINEAR, borderValue=255)
    page = _page(project, file)
    checked = 0
    for t in page["texts"]:
        x0, y0, x1, y1 = (int(round(v)) for v in t["box"])
        if x1 - x0 < 20 or not any(ch.isalpha() for ch in t["text"]):
            continue
        tpl = back[y0 - 2:y1 + 3, x0 - 2:x1 + 3].astype(np.float32)
        pad = 8
        area = gray[y0 - 2 - pad:y1 + 3 + pad, x0 - 2 - pad:x1 + 3 + pad].astype(np.float32)
        score = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED)
        _, best, _, loc = cv2.minMaxLoc(score)
        assert best >= 0.8, (t["text"], best)
        assert math.hypot(loc[0] - pad, loc[1] - pad) <= 2.0, (t["text"], loc)
        checked += 1
    assert checked >= 3


def test_page_to_original_is_the_y_up_page_frame(scan):
    _, rect = scan
    h = rect.image.shape[0]
    m = RF.page_to_original(rect)
    # Page point (c + 0.5, H - r - 0.5) is the centre of rectified pixel (c, r).
    for c, r in ((10, 20), (400, 1200)):
        assert RF.apply_h(m, c + 0.5, h - r - 0.5) == pytest.approx(RF.apply_h(rect.to_original, c, r), abs=1e-6)


def test_snap_ratio():
    assert RF.snap_ratio(1.40)[0] == pytest.approx(math.sqrt(2.0)) and RF.snap_ratio(1.40)[1].startswith("ISO")
    ratio, name, diff = RF.snap_ratio(1.0 / 1.43)
    assert ratio == pytest.approx(math.sqrt(2.0)) and diff < 0.04
    assert RF.snap_ratio(1.20)[0] is None                        # 7 % from 1.294, 10 % from 1.333: not snapped


def _lines_image(angle_deg: float) -> np.ndarray:
    img = np.full((600, 800), 255, np.uint8)
    for y in range(100, 520, 60):
        cv2.line(img, (80, y), (720, y), 0, 2)
    for x in (80, 400, 720):
        cv2.line(img, (x, 100), (x, 520), 0, 2)
    rot = cv2.getRotationMatrix2D((400, 300), angle_deg, 1.0)
    return cv2.warpAffine(img, rot, (800, 600), borderValue=255)


def test_deskew_finds_small_rotations_and_respects_the_limit():
    rect = RF.deskew(_lines_image(2.0))
    assert abs(abs(rect.angle_deg) - 2.0) <= 0.1
    drawn = cv2.getRotationMatrix2D((400, 300), 2.0, 1.0).tolist() + [[0.0, 0.0, 1.0]]   # drawing -> image
    back = np.linalg.inv(np.array(rect.to_original))                                     # image -> rectified
    a = RF.apply_h(back, *RF.apply_h(drawn, 80, 100))
    b = RF.apply_h(back, *RF.apply_h(drawn, 720, 100))
    assert abs(a[1] - b[1]) <= 1.0                               # the drawn horizontal is horizontal again
    assert RF.deskew(_lines_image(8.0)).angle_deg == 0.0         # beyond 5 deg: not a skew, left alone


def test_photo_without_a_sheet_needs_review():
    clutter = np.random.RandomState(3).randint(0, 256, (400, 600)).astype(np.uint8)   # no bright sheet anywhere
    rect = RF.rectify(clutter, "photo")
    assert rect.review == "no page quadrilateral found" and rect.quad is None
