"""Debug images: the page raster with the recognised elements drawn over it.

One PNG per page (``outputs/<project>/debug/<doc>_p<page>.png``). Colour by
method (vector green, ocr blue, ai orange, derived grey), alpha by confidence,
unverified items dashed red, each with a small ID label. The page raster is
the PDF page rendered at 100 dpi (pdftoppm), the DXF rendered with ezdxf's
matplotlib backend at a known model-space window, or the image itself
(downscaled). Drawing is done with Pillow on an RGBA overlay.

``PageRaster`` carries ``to_pixels`` so callers pass geometry in page units
(DXF drawing units, PDF points with origin bottom-left, image pixels).
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from PIL import Image, ImageDraw, ImageFont

from wenart import geometry as G
from wenart.synthetic.raster import rasterise_pdf_page

COLOURS = {
    "vector": (0, 150, 0),
    "ocr": (30, 90, 220),
    "ai": (235, 130, 0),
    "derived": (120, 120, 120),
}
UNVERIFIED_COLOUR = (220, 20, 20)
PDF_DPI = 100
DXF_WIDTH_PX = 1800
IMAGE_MAX_WIDTH = 1600
DXF_MARGIN = 0.03   # fraction of the model-space extent


@dataclass
class DebugItem:
    """One overlay: a polygon (page units), how it was found and what to write next to it."""
    polygon: list              # [(x, y), ...] in page units; a box is given as its 4 corners
    method: str                # vector | ocr | ai | derived
    confidence: float
    label: str = ""
    status: str = "verified"   # unverified -> dashed red
    width: int = 2


@dataclass
class PageRaster:
    image: Image.Image
    to_pixels: Callable[[tuple], tuple]
    note: str = ""
    items: list = field(default_factory=list)


# --------------------------------------------------------------------------
# Page rasters
# --------------------------------------------------------------------------

def raster_from_pdf(path: Path, page: int, dpi: int = PDF_DPI) -> PageRaster:
    with tempfile.TemporaryDirectory() as tmp:
        png = rasterise_pdf_page(path, page, Path(tmp) / "page.png", dpi=dpi, gray=False)
        image = Image.open(png).convert("RGB")
        image.load()
    scale = dpi / 72.0
    height_px = image.height

    def to_pixels(p):
        return (p[0] * scale, height_px - p[1] * scale)

    return PageRaster(image=image, to_pixels=to_pixels)


def raster_from_dxf(path: Path, width_px: int = DXF_WIDTH_PX) -> PageRaster:
    """Render the DXF model space into an image whose pixel mapping is known:
    the figure is sized to the extents' aspect ratio so the axes fill it."""
    import matplotlib
    matplotlib.use("Agg")
    import ezdxf
    import matplotlib.pyplot as plt
    from ezdxf import bbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    extents = bbox.extents(msp)
    if not extents.has_data:
        image = Image.new("RGB", (width_px, width_px // 2), "white")
        return PageRaster(image=image, to_pixels=lambda p: (p[0], p[1]), note="empty DXF")
    x0, y0 = extents.extmin.x, extents.extmin.y
    x1, y1 = extents.extmax.x, extents.extmax.y
    mx, my = (x1 - x0) * DXF_MARGIN, (y1 - y0) * DXF_MARGIN
    x0, y0, x1, y1 = x0 - mx, y0 - my, x1 + mx, y1 + my
    height_px = max(200, int(round(width_px * (y1 - y0) / (x1 - x0))))
    fig = plt.figure(figsize=(width_px / 100.0, height_px / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    config = Configuration(background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=config).draw_layout(msp, finalize=True)
    # ezdxf's finalize step resizes the figure; restore our size and window so
    # the pixel mapping below stays exact.
    fig.set_size_inches(width_px / 100.0, height_px / 100.0)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("auto")
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "dxf.png"
        fig.savefig(png, dpi=100, facecolor="white")
        plt.close(fig)
        image = Image.open(png).convert("RGB")
        image.load()
    w_img, h_img = image.size

    def to_pixels(p):
        return ((p[0] - x0) / (x1 - x0) * w_img, (y1 - p[1]) / (y1 - y0) * h_img)

    return PageRaster(image=image, to_pixels=to_pixels)


def raster_from_image(path: Path, max_width: int = IMAGE_MAX_WIDTH) -> PageRaster:
    with Image.open(path) as im:
        image = im.convert("RGB")
        image.load()
    factor = 1.0
    if image.width > max_width:
        factor = max_width / image.width
        image = image.resize((max_width, round(image.height * factor)), Image.LANCZOS)

    def to_pixels(p):
        return (p[0] * factor, p[1] * factor)

    return PageRaster(image=image, to_pixels=to_pixels)


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

def _font(size: int = 13):
    try:
        return ImageFont.load_default(size=size)
    except Exception:  # noqa: BLE001 - very old Pillow
        return ImageFont.load_default()


def _dashed_line(draw: ImageDraw.ImageDraw, a, b, fill, width: int, dash: float = 8.0, gap: float = 5.0) -> None:
    length = G.distance(a, b)
    if length < 1e-6:
        return
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line([G.point_at_distance(a, b, pos), G.point_at_distance(a, b, end)], fill=fill, width=width)
        pos = end + gap


def draw_items(image: Image.Image, items: list[DebugItem], to_pixels: Callable, note: str = "") -> Image.Image:
    """Return a copy of ``image`` with the items drawn on it."""
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _font()
    for item in items:
        pts = [to_pixels(p) for p in item.polygon]
        if len(pts) < 2:
            continue
        colour = COLOURS.get(item.method, COLOURS["derived"])
        alpha = int(255 * (0.35 + 0.65 * max(0.0, min(1.0, item.confidence))))
        if item.status == "unverified":
            fill = UNVERIFIED_COLOUR + (alpha,)
            closed = pts + [pts[0]]
            for a, b in zip(closed[:-1], closed[1:]):
                _dashed_line(draw, a, b, fill, item.width)
        else:
            fill = colour + (alpha,)
            draw.polygon(pts, outline=fill, width=item.width)
        if item.label:
            x = min(p[0] for p in pts) + 2
            y = min(p[1] for p in pts) + 1
            draw.text((x, y), item.label, fill=fill, font=font)
    if note:
        draw.rectangle([0, 0, base.width, 22], fill=(255, 255, 255, 200))
        draw.text((6, 4), note, fill=(0, 0, 0, 255), font=font)
    return Image.alpha_composite(base, overlay).convert("RGB")


def write_debug_image(raster: PageRaster, items: list[DebugItem], out_path: Path, note: str = "") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image = draw_items(raster.image, items, raster.to_pixels, note=note or raster.note)
    image.save(out_path, "PNG", optimize=True)
    return out_path


def box_polygon(box) -> list[tuple[float, float]]:
    return G.box_corners(box)


def legend_note(prefix: str = "") -> str:
    base = "green = vector, blue = ocr, orange = ai, grey = derived, dashed red = unverified"
    return f"{prefix} | {base}" if prefix else base
