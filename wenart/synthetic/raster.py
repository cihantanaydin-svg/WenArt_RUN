"""Raster pages made from the vector PDFs, plus small preview JPEGs.

- ``scan``: ``pdftoppm -r 150 -gray`` of one PDF page, rotated by a small
  seeded angle (-1.5..+1.5 degrees), light Gaussian noise, slight blur, PNG.
- ``photo``: the scan warped by a perspective transform (corners moved inward
  by up to 6 % of the page size), grey background outside the paper, an uneven
  brightness gradient, JPEG quality 80.

Every function returns the transform from PDF points (origin bottom-left) to
pixels (origin top-left) so the generator can chain
building -> PDF points -> pixels and store ``H_building_to_pixels``.

All randomness comes from ``numpy.random.RandomState(seed)``; OpenCV and
Pillow are deterministic for the same input, so the files are reproducible.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from wenart import geometry as G

SCAN_DPI = 150
SCAN_MAX_ANGLE = 1.5
SCAN_NOISE_SIGMA = 4.0
SCAN_BLUR_SIGMA = 0.7
PHOTO_MAX_SHIFT = 0.06
PHOTO_BACKGROUND = 112
PHOTO_JPEG_QUALITY = 80
PREVIEW_WIDTH = 1200
PREVIEW_MAX_BYTES = 300 * 1024


def rasterise_pdf_page(pdf_path: Path, page: int, out_png: Path, dpi: int = SCAN_DPI, gray: bool = True) -> Path:
    """Render one PDF page with poppler's pdftoppm to ``out_png``."""
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    prefix = out_png.with_suffix("")
    cmd = ["pdftoppm", "-r", str(dpi), "-png", "-f", str(page), "-l", str(page), "-singlefile"]
    if gray:
        cmd.append("-gray")
    cmd += [str(pdf_path), str(prefix)]
    subprocess.run(cmd, check=True, capture_output=True)
    rendered = prefix.with_suffix(".png")
    if rendered != out_png:
        rendered.replace(out_png)
    return out_png


def pdf_points_to_pixels(page_height_pt: float, dpi: int) -> list[float]:
    """Affine from PDF points (origin bottom-left, y up) to pixels (origin top-left, y down)."""
    s = dpi / 72.0
    return [s, 0.0, 0.0, 0.0, -s, page_height_pt * s]


def make_scan(pdf_path: Path, page: int, page_height_pt: float, out_png: Path, seed: int,
              dpi: int = SCAN_DPI) -> tuple[list[float], tuple[int, int]]:
    """Scan-like PNG of a PDF page. Returns (affine PDF points -> pixels, (width, height))."""
    rng = np.random.RandomState(seed)
    out_png = Path(out_png)
    rasterise_pdf_page(pdf_path, page, out_png, dpi=dpi, gray=True)
    img = cv2.imread(str(out_png), cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    angle = float(rng.uniform(-SCAN_MAX_ANGLE, SCAN_MAX_ANGLE))
    rot = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
    rotated = cv2.warpAffine(img, rot, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    noisy = rotated.astype(np.float32) + rng.normal(0.0, SCAN_NOISE_SIGMA, size=rotated.shape).astype(np.float32)
    blurred = cv2.GaussianBlur(noisy, (0, 0), SCAN_BLUR_SIGMA)
    final = np.clip(blurred, 0, 255).astype(np.uint8)
    cv2.imwrite(str(out_png), final, [cv2.IMWRITE_PNG_COMPRESSION, 7])
    rot_affine = [float(rot[0, 0]), float(rot[0, 1]), float(rot[0, 2]), float(rot[1, 0]), float(rot[1, 1]), float(rot[1, 2])]
    pts_to_px = G.compose_affine(rot_affine, pdf_points_to_pixels(page_height_pt, dpi))
    return pts_to_px, (w, h)


def make_photo(scan_png: Path, out_jpg: Path, seed: int) -> tuple[list[list[float]], tuple[int, int]]:
    """Phone-photo-like JPEG from a scan PNG. Returns (3x3 homography scan pixels -> photo pixels, (w, h))."""
    rng = np.random.RandomState(seed)
    img = cv2.imread(str(scan_png), cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    # Move every corner inward by a random amount so the whole page stays visible.
    shifts = rng.uniform(0.0, PHOTO_MAX_SHIFT, size=(4, 2)).astype(np.float32)
    inward = np.float32([[1, 1], [-1, 1], [-1, -1], [1, -1]])
    dst = src + inward * shifts * np.float32([w, h])
    persp = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, persp, (w, h), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=PHOTO_BACKGROUND)
    # Uneven lighting: a smooth gradient across the page.
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    gradient = 0.72 + 0.33 * (xs / w) * 0.6 + 0.33 * (1.0 - ys / h) * 0.4
    lit = np.clip(warped.astype(np.float32) * gradient, 0, 255).astype(np.uint8)
    out_jpg = Path(out_jpg)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_jpg), lit, [cv2.IMWRITE_JPEG_QUALITY, PHOTO_JPEG_QUALITY])
    return [[float(v) for v in row] for row in persp], (w, h)


def write_preview(image: Image.Image, out_jpg: Path, width: int = PREVIEW_WIDTH,
                  max_bytes: int = PREVIEW_MAX_BYTES) -> Path:
    """Small JPEG preview (<= max_bytes): resize to ``width`` and lower the quality until it fits."""
    out_jpg = Path(out_jpg)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    img = image.convert("L")
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    for quality in (80, 70, 60, 50, 40):
        img.save(out_jpg, "JPEG", quality=quality, optimize=True)
        if out_jpg.stat().st_size <= max_bytes:
            break
    return out_jpg


def preview_from_pdf(pdf_path: Path, page: int, out_jpg: Path) -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        png = rasterise_pdf_page(pdf_path, page, Path(tmp) / "page.png", dpi=100, gray=True)
        with Image.open(png) as img:
            return write_preview(img, out_jpg)


def preview_from_image(image_path: Path, out_jpg: Path) -> Path:
    with Image.open(image_path) as img:
        return write_preview(img, out_jpg)


def preview_from_dxf(dxf_path: Path, out_jpg: Path) -> Path:
    """Render a DXF with ezdxf's matplotlib backend (so the preview shows the real file)."""
    import matplotlib
    matplotlib.use("Agg")
    import ezdxf
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    doc = ezdxf.readfile(str(dxf_path))
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    # White paper, dark lines (the default renders light lines on a dark background).
    config = Configuration(background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=config).draw_layout(doc.modelspace(), finalize=True)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "dxf.png"
        fig.savefig(png, dpi=100, facecolor="white")
        plt.close(fig)
        with Image.open(png) as img:
            write_preview(img, out_jpg)
    return Path(out_jpg)
