"""Raster page rectification (docs/milestone7.md §4.1): deskewed scans and rectified phone photos.

What: one grey image in, one *rectified* grey image out, plus the 3 x 3 homography ``to_original`` that maps a
rectified pixel (x right, y down, OpenCV pixel-centre coordinates) back to the original image. Everything the raster
adapter finds (walls, openings, texts) is found on the rectified image and mapped back to the original through it, so
the debug image and every ``pixel_box`` point at the file the user gave.

- **Scans** (``deskew``): the dominant long-stroke direction is measured (probabilistic Hough on the ink, then each long
  line refitted by least squares to the ink pixels within 1.5 px of it; length-weighted median) and undone when it is
  within ``MAX_DESKEW_DEG`` (5°) of the image axes; the canvas grows so nothing is cut off (new paper is white).
- **Photos** (``page_quad`` + ``rectify_photo``): the page quadrilateral is the largest 4-corner contour of the bright
  paper covering >= 30 % of the image; each side is refitted to its contour points (sub-pixel corners). The page's
  aspect ratio is measured from the quad with the pinhole model of Zhang & He (2007, "Whiteboard scanning and image
  enhancement": principal point at the image centre, square pixels; the focal length follows from the two right
  angles) and, when that model has no real solution, from the mean side lengths. A measured ratio within
  ``SNAP_TOLERANCE`` (4 %) of a standard sheet ratio (ISO √2, ANSI 1.294 / 1.545, ARCH 1.333 / 1.5) is snapped to it
  (the closest; recorded as ``assumed``); otherwise the photo is rectified with the measured ratio and the caller must
  solve it from the dimension texts (``aspect["snapped"] is None``, §4.1) or stop with ``needs_review`` ("photo aspect
  unknown"). The rectified page keeps the quad's mean long side in pixels. A rectified photo is deskewed as well (the
  plan may sit slightly turned on the paper).
- ``rescale_y`` re-warps a rectified photo when the dimension groups give the true aspect.

No page quadrilateral → ``Rectified.review = "no page quadrilateral found"``; the caller decides (needs_review, or
evidence only when another page of the level exists).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np

MAX_DESKEW_DEG = 5.0
HOUGH_MIN_LEN_REL = 0.04          # long strokes: >= 4 % of the image's short side (>= 60 px)
HOUGH_MIN_LEN_PX = 60
REFIT_BAND_PX = 1.5               # ink pixels this close to a Hough line refit it
MIN_DESKEW_DEG = 0.02             # smaller angles are left alone (no resampling)
QUAD_MIN_AREA = 0.30              # the page quad covers >= 30 % of the image
FRAME_SHARE = 0.02                 # a quad corner within 2 % of the image size of the border lies on the frame
SNAP_TOLERANCE = 0.04             # a measured aspect within 4 % of a standard sheet ratio is snapped
SHEET_RATIOS = (                  # long side / short side
    ("ISO (sqrt 2)", math.sqrt(2.0)),
    ("ANSI A (11 x 8.5 in)", 11.0 / 8.5),
    ("ANSI B (17 x 11 in)", 17.0 / 11.0),
    ("ARCH (4:3)", 4.0 / 3.0),
    ("ARCH (3:2)", 1.5),
)
WHITE = 255

# Ink: adaptive threshold (block 51 px, C 10) united with Otsu (docs/milestone7.md §4.2).
ADAPTIVE_BLOCK = 51
ADAPTIVE_C = 10


@dataclass
class Rectified:
    """A rectified raster page."""
    image: np.ndarray                          # grey uint8 (rows, cols)
    to_original: list[list[float]]             # 3 x 3: rectified pixel (x right, y down) -> original image pixel
    kind: str                                  # scan | photo
    original_size: tuple[int, int]             # (width, height) of the original image
    angle_deg: float = 0.0                     # deskew rotation applied (degrees, image frame)
    quad: Optional[list[list[float]]] = None   # photo: page corners in original pixels (TL, TR, BR, BL)
    aspect: Optional[dict] = None              # photo: {"measured", "method", "side_ratio", "snapped", "name", "assumed"}
    notes: list[str] = field(default_factory=list)
    review: Optional[str] = None               # why the page cannot be used (needs_review)

    @property
    def size(self) -> tuple[int, int]:
        return int(self.image.shape[1]), int(self.image.shape[0])


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def flatten_illumination(gray: np.ndarray) -> np.ndarray:
    """The page with uneven lighting divided out: the paper level is a grey closing (max then min filter, removes
    the ink) of a 1/8 copy with a 25 px kernel (200 px at full size, far wider than any wall), blurred and scaled
    back; the page is divided by it (paper -> 255)."""
    g = np.asarray(gray, dtype=np.uint8)
    h, w = g.shape
    small = cv2.resize(g, (max(1, w // 8), max(1, h // 8)), interpolation=cv2.INTER_AREA)
    paper = cv2.morphologyEx(small, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    paper = cv2.GaussianBlur(paper, (0, 0), 3)
    paper = cv2.resize(paper, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    out = g.astype(np.float32) * 255.0 / np.maximum(paper, 1.0)
    return np.clip(out, 0, 255).astype(np.uint8)


def ink_mask(gray: np.ndarray) -> np.ndarray:
    """Dark ink as a bool mask: adaptive threshold (block 51, C 10) united with Otsu (§4.2); Otsu runs on the page
    with its lighting flattened (``flatten_illumination``), so a photo's brightness gradient is not ink."""
    g = np.asarray(gray, dtype=np.uint8)
    adaptive = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, ADAPTIVE_BLOCK,
                                     ADAPTIVE_C)
    _, otsu = cv2.threshold(flatten_illumination(g), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return (adaptive > 0) | (otsu > 0)


def _h3(m23) -> np.ndarray:
    out = np.eye(3)
    out[:2, :] = np.asarray(m23, dtype=np.float64)
    return out


def _as_list(h: np.ndarray) -> list[list[float]]:
    return [[float(v) for v in row] for row in np.asarray(h, dtype=np.float64)]


def apply_h(h, x: float, y: float) -> tuple[float, float]:
    """A homography (3 x 3 nested list or array) applied to one point."""
    m = np.asarray(h, dtype=np.float64)
    w = m[2, 0] * x + m[2, 1] * y + m[2, 2]
    return (float((m[0, 0] * x + m[0, 1] * y + m[0, 2]) / w), float((m[1, 0] * x + m[1, 1] * y + m[1, 2]) / w))


# --------------------------------------------------------------------------
# Deskew
# --------------------------------------------------------------------------

def _fold(angle_deg: float) -> float:
    """An undirected line angle folded into (-45, 45] (the offset from the nearest image axis)."""
    a = angle_deg % 90.0
    return a - 90.0 if a > 45.0 else a


def deskew_angle(gray: np.ndarray, max_deg: float = MAX_DESKEW_DEG) -> tuple[float, int]:
    """(angle, lines used): the length-weighted median direction of the long ink strokes, image frame (y down),
    folded to the nearest axis; 0 when no long stroke lies within ``max_deg`` of an axis."""
    ink = ink_mask(gray)
    h, w = ink.shape
    min_len = max(HOUGH_MIN_LEN_PX, int(HOUGH_MIN_LEN_REL * min(h, w)))
    found = cv2.HoughLinesP(ink.astype(np.uint8) * 255, 1, math.pi / 1800.0, threshold=min_len // 2,
                            minLineLength=min_len, maxLineGap=2)
    if found is None:
        return 0.0, 0
    ys, xs = np.nonzero(ink)
    pts = np.column_stack([xs, ys]).astype(np.float64)
    order = np.argsort(xs)
    xs_sorted = xs[order]
    rows = []
    for x1, y1, x2, y2 in np.asarray(found).reshape(-1, 4):
        ang = _fold(math.degrees(math.atan2(y2 - y1, x2 - x1)))
        if abs(ang) > max_deg:
            continue
        length = math.hypot(x2 - x1, y2 - y1)
        # Refit to the ink pixels within REFIT_BAND_PX of the line (between its ends).
        lo, hi = np.searchsorted(xs_sorted, [min(x1, x2) - 2, max(x1, x2) + 2], side="left")
        cand = pts[order[lo:hi]]
        if len(cand) < 10:
            continue
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        rel = cand - np.array([x1, y1], dtype=np.float64)
        along = rel[:, 0] * ux + rel[:, 1] * uy
        off = rel[:, 0] * -uy + rel[:, 1] * ux
        sel = cand[(np.abs(off) <= REFIT_BAND_PX) & (along >= 0) & (along <= length)]
        if len(sel) < 0.5 * length:
            continue
        vx, vy, _, _ = cv2.fitLine(sel.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01).ravel()
        fine = _fold(math.degrees(math.atan2(float(vy), float(vx))))
        if abs(fine - ang) > 0.5:
            continue
        rows.append((fine, length))
    if not rows:
        return 0.0, 0
    rows.sort()
    total = sum(r[1] for r in rows)
    acc = 0.0
    median = rows[-1][0]
    for a, wt in rows:
        acc += wt
        if acc >= total / 2.0:
            median = a
            break
    near = [(a, wt) for a, wt in rows if abs(a - median) <= 0.15]
    angle = sum(a * wt for a, wt in near) / sum(wt for _, wt in near)
    return float(angle), len(rows)


def rotate_expand(gray: np.ndarray, angle_deg: float) -> tuple[np.ndarray, np.ndarray]:
    """Rotate by ``angle_deg`` (OpenCV convention: positive = counter-clockwise on screen) about the centre on a canvas
    grown to hold the whole image (new paper white). Returns (image, 3 x 3 forward matrix original -> new)."""
    h, w = gray.shape[:2]
    m = cv2.getRotationMatrix2D(((w - 1) / 2.0, (h - 1) / 2.0), angle_deg, 1.0)
    corners = np.array([[-0.5, -0.5, 1], [w - 0.5, -0.5, 1], [w - 0.5, h - 0.5, 1], [-0.5, h - 0.5, 1]]).T
    moved = m @ corners
    x0, y0 = moved[0].min(), moved[1].min()
    new_w = int(math.ceil(moved[0].max() - x0))
    new_h = int(math.ceil(moved[1].max() - y0))
    m[0, 2] -= x0 + 0.5
    m[1, 2] -= y0 + 0.5
    out = cv2.warpAffine(gray, m, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                         borderValue=WHITE)
    return out, _h3(m)


def deskew(gray: np.ndarray, kind: str = "scan", base: Optional[np.ndarray] = None,
           original_size: Optional[tuple[int, int]] = None) -> Rectified:
    """Deskew a grey page. ``base`` (3 x 3, current image -> original) chains an earlier rectification."""
    gray = np.asarray(gray, dtype=np.uint8)
    base_h = np.eye(3) if base is None else np.asarray(base, dtype=np.float64)
    size = original_size or (int(gray.shape[1]), int(gray.shape[0]))
    angle, n = deskew_angle(gray)
    notes = []
    if abs(angle) < MIN_DESKEW_DEG or n == 0:
        notes.append(f"deskew: {angle:+.3f} deg from {n} long strokes, not rotated" if n else
                     "deskew: no long straight strokes found, not rotated")
        return Rectified(image=gray, to_original=_as_list(base_h), kind=kind, original_size=size, angle_deg=0.0,
                         notes=notes)
    out, fwd = rotate_expand(gray, angle)
    notes.append(f"deskew: rotated by {-angle:+.3f} deg (dominant direction of {n} long strokes)")
    return Rectified(image=out, to_original=_as_list(base_h @ np.linalg.inv(fwd)), kind=kind, original_size=size,
                     angle_deg=float(angle), notes=notes)


# --------------------------------------------------------------------------
# Photos: page quad and aspect
# --------------------------------------------------------------------------

def _order_corners(pts: np.ndarray) -> np.ndarray:
    """TL, TR, BR, BL (image frame)."""
    pts = np.asarray(pts, dtype=np.float64).reshape(4, 2)
    s = pts.sum(axis=1)
    d = pts[:, 0] - pts[:, 1]
    return np.array([pts[np.argmin(s)], pts[np.argmax(d)], pts[np.argmax(s)], pts[np.argmin(d)]])


def _line_through(points: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]:
    if len(points) < 5:
        return None
    vx, vy, x0, y0 = cv2.fitLine(points.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    return np.array([x0, y0], dtype=np.float64), np.array([vx, vy], dtype=np.float64)


def _intersect(l1, l2) -> Optional[np.ndarray]:
    (p, u), (q, v) = l1, l2
    den = u[0] * v[1] - u[1] * v[0]
    if abs(den) < 1e-9:
        return None
    t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
    return p + t * u


def page_quad(gray: np.ndarray, min_area: float = QUAD_MIN_AREA) -> Optional[np.ndarray]:
    """The page quadrilateral (TL, TR, BR, BL, sub-pixel) of a photo, or None: the largest 4-corner contour of the
    bright paper (Otsu) covering >= ``min_area`` of the image, each side refitted to its contour points. A contour
    whose four corners are the image corners is no sheet (paper filling the frame, or no paper at all)."""
    g = np.asarray(gray, dtype=np.uint8)
    h, w = g.shape
    blur = cv2.GaussianBlur(g, (5, 5), 0)
    _, paper = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k = max(3, int(round(min(h, w) * 0.01)) | 1)
    kernel = np.ones((k, k), np.uint8)
    paper = cv2.morphologyEx(paper, cv2.MORPH_CLOSE, kernel)      # drawn lines on the paper
    paper = cv2.morphologyEx(paper, cv2.MORPH_OPEN, kernel)       # bright specks off the paper
    contours, _ = cv2.findContours(paper, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    biggest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(biggest) < min_area * h * w:
        return None
    peri = cv2.arcLength(biggest, True)
    approx = None
    for eps in (0.02, 0.01, 0.03, 0.04, 0.05):
        a = cv2.approxPolyDP(biggest, eps * peri, True)
        if len(a) == 4 and cv2.isContourConvex(a):
            approx = a.reshape(4, 2).astype(np.float64)
            break
    if approx is None:
        return None
    corners = _order_corners(approx)
    frame = FRAME_SHARE * min(h, w)
    on_border = [min(x, y, w - 1 - x, h - 1 - y) <= frame for x, y in corners]
    if all(on_border):
        return None                                   # the image frame itself: no sheet edge is visible
    contour = biggest.reshape(-1, 2).astype(np.float64)
    lines = []
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        length = float(np.linalg.norm(b - a))
        u = (b - a) / length
        rel = contour - a
        along = rel @ u
        off = rel @ np.array([-u[1], u[0]])
        sel = contour[(np.abs(off) <= 6.0) & (along >= 0.1 * length) & (along <= 0.9 * length)]
        line = _line_through(sel)
        if line is None:
            return corners
        lines.append(line)
    refined = []
    for i in range(4):
        p = _intersect(lines[i - 1], lines[i])
        if p is None or np.linalg.norm(p - corners[i]) > 0.02 * max(h, w):
            return corners
        refined.append(p)
    return np.array(refined)


def quad_aspect(quad: np.ndarray, image_size: tuple[int, int]) -> dict:
    """The page's width / height from its quad (TL, TR, BR, BL): Zhang & He's pinhole estimate (principal point at
    the image centre, square pixels) when it has a real solution, else the ratio of the mean side lengths."""
    q = np.asarray(quad, dtype=np.float64)
    top, bottom = np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])
    left, right = np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])
    side_ratio = (top + bottom) / (left + right)
    u0, v0 = image_size[0] / 2.0, image_size[1] / 2.0
    # Zhang & He's corner order: m1 = TL, m2 = TR, m3 = BL, m4 = BR (homogeneous, principal point removed).
    m1, m2, m3, m4 = (np.array([p[0] - u0, p[1] - v0, 1.0]) for p in (q[0], q[1], q[3], q[2]))
    out = {"side_ratio": float(side_ratio), "method": "side_ratio", "measured": float(side_ratio), "focal_px": None}
    try:
        k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
        k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
        n2 = k2 * m2 - m1
        n3 = k3 * m3 - m1
        if abs(n2[2] * n3[2]) < 1e-12:
            ratio = math.sqrt((n2[0] ** 2 + n2[1] ** 2) / (n3[0] ** 2 + n3[1] ** 2))
            out.update(measured=float(ratio), method="affine")
            return out
        f2 = -(n2[0] * n3[0] + n2[1] * n3[1]) / (n2[2] * n3[2])
        if f2 <= 0:
            return out
        a_inv = np.diag([1.0 / f2, 1.0 / f2, 1.0])
        ratio = math.sqrt(float(n2 @ a_inv @ n2) / float(n3 @ a_inv @ n3))
        if not math.isfinite(ratio) or ratio <= 0:
            return out
        out.update(measured=float(ratio), method="pinhole", focal_px=round(math.sqrt(f2), 1))
    except (ZeroDivisionError, FloatingPointError, ValueError):
        pass
    return out


def snap_ratio(ratio: float, tolerance: float = SNAP_TOLERANCE) -> tuple[Optional[float], Optional[str], float]:
    """(standard ratio, name, relative difference) of the closest standard sheet ratio within ``tolerance`` of the
    long / short ``ratio``, else (None, None, difference to the closest)."""
    r = max(ratio, 1.0 / ratio)
    best = min(SHEET_RATIOS, key=lambda item: abs(r / item[1] - 1.0))
    diff = abs(r / best[1] - 1.0)
    if diff <= tolerance:
        return best[1], best[0], diff
    return None, None, diff


def _warp_quad(gray: np.ndarray, quad: np.ndarray, width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    """Warp the quad onto a ``width`` x ``height`` image; returns (image, 3 x 3 rectified -> original)."""
    dst = np.array([[-0.5, -0.5], [width - 0.5, -0.5], [width - 0.5, height - 0.5], [-0.5, height - 0.5]],
                   dtype=np.float64)
    fwd = cv2.getPerspectiveTransform(np.asarray(quad, dtype=np.float32), dst.astype(np.float32))
    out = cv2.warpPerspective(gray, fwd, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                              borderValue=WHITE)
    return out, np.linalg.inv(fwd)


def rectify_photo(gray: np.ndarray, quad: Optional[np.ndarray] = None) -> Rectified:
    """Rectify a phone photo of a sheet: page quad -> homography onto a rectangle of the (snapped) sheet ratio,
    then deskew. Without a quad the result has ``review`` set and the original image."""
    gray = np.asarray(gray, dtype=np.uint8)
    size = (int(gray.shape[1]), int(gray.shape[0]))
    if quad is None:
        quad = page_quad(gray)
    if quad is None:
        return Rectified(image=gray, to_original=_as_list(np.eye(3)), kind="photo", original_size=size,
                         notes=["no page quadrilateral covering >= 30 % of the image"],
                         review="no page quadrilateral found")
    quad = _order_corners(quad)
    aspect = quad_aspect(quad, size)
    measured = aspect["measured"]
    snapped, name, diff = snap_ratio(measured)
    landscape = measured >= 1.0
    q = np.asarray(quad)
    long_px = max((np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2.0,
                  (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2.0)
    ratio = snapped if snapped is not None else max(measured, 1.0 / measured)
    width, height = (long_px, long_px / ratio) if landscape else (long_px / ratio, long_px)
    width, height = int(round(width)), int(round(height))
    image, to_orig = _warp_quad(gray, quad, width, height)
    aspect.update(snapped=snapped, name=name, off_pct=round(diff * 100.0, 2), assumed=snapped is not None,
                  landscape=landscape, output=[width, height])
    notes = [f"page quad {', '.join(f'({p[0]:.1f}, {p[1]:.1f})' for p in q)}",
             f"aspect measured {measured:.4f} ({aspect['method']}; side ratio {aspect['side_ratio']:.4f})"]
    if snapped is not None:
        notes.append(f"aspect snapped to {name} {snapped:.4f} ({diff * 100:.1f} % off): assumed")
    else:
        notes.append(f"aspect {measured:.4f} is {diff * 100:.1f} % from the nearest standard sheet ratio: not snapped "
                     f"(to be solved from the dimension texts)")
    rect = deskew(image, kind="photo", base=to_orig, original_size=size)
    rect.quad = [[round(float(v), 2) for v in p] for p in q]
    rect.aspect = aspect
    rect.notes = notes + rect.notes
    return rect


def rescale_y(rect: Rectified, original: np.ndarray, factor: float) -> Rectified:
    """Re-warp a rectified photo with its height multiplied by ``factor`` (the aspect solved from the dimension
    groups, §4.1). The quad and the deskew angle are kept."""
    quad = np.asarray(rect.quad, dtype=np.float64)
    w0, h0 = rect.aspect["output"]
    width, height = int(w0), int(round(h0 * factor))
    image, to_orig = _warp_quad(np.asarray(original, dtype=np.uint8), quad, width, height)
    if abs(rect.angle_deg) >= MIN_DESKEW_DEG:
        image, fwd = rotate_expand(image, rect.angle_deg)
        to_orig = to_orig @ np.linalg.inv(fwd)
    out = Rectified(image=image, to_original=_as_list(to_orig), kind="photo", original_size=rect.original_size,
                    angle_deg=rect.angle_deg, quad=rect.quad, aspect=dict(rect.aspect, output=[width, height]),
                    notes=list(rect.notes))
    return out


def rectify(gray: np.ndarray, kind: str) -> Rectified:
    """Scans are deskewed; photos are rectified (quad, aspect) and then deskewed."""
    if kind == "photo":
        return rectify_photo(gray)
    return deskew(gray, kind="scan")


def page_flip(height: int) -> np.ndarray:
    """3 x 3: page units (pixel-corner coordinates of the rectified image, y up: pixel (row r, col c) covers
    x in [c, c + 1], y in [H - r - 1, H - r], as ``MaskLayer`` with origin (0, H) and px 1) -> OpenCV pixel-centre
    coordinates of the rectified image (x right, y down)."""
    return np.array([[1.0, 0.0, -0.5], [0.0, -1.0, height - 0.5], [0.0, 0.0, 1.0]])


def page_to_original(rect: Rectified) -> list[list[float]]:
    """3 x 3: page units of the ``GenericPage`` (rectified pixels, y up, ``page_flip``) -> original image pixels
    (OpenCV pixel-centre coordinates)."""
    return _as_list(np.asarray(rect.to_original, dtype=np.float64) @ page_flip(rect.image.shape[0]))
