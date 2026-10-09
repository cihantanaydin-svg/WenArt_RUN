"""Debug images: the page raster with the recognised elements drawn over it.

One PNG per page (``outputs/<project>/debug/<doc>_p<page>.png``). Colour by
method (vector green, ocr blue, ai orange, derived grey), alpha by confidence,
unverified items dashed red, each with a small ID label. The page raster is
the PDF page rendered at 100 dpi (pdftoppm), the DXF rendered with ezdxf's
matplotlib backend at a known model-space window, or the image itself
(downscaled). Drawing is done with Pillow on an RGBA overlay.

``PageRaster`` carries ``to_pixels`` so callers pass geometry in page units
(DXF drawing units, PDF points with origin bottom-left, image pixels).

Generic core pages (docs/milestone7.md §2.9) are rendered at 150 dpi and add:
the wall mask as a translucent layer (``overlay_mask``), open polylines
(wall centre lines, door swings, separators, dimensions), dashed outlines
(doorless openings, separators in magenta), fixed colours per meaning
(furniture by ``type_method``: rule green, block_name blue, ai_two_pass
cyan, none red striped; site grey; scale dimensions orange).
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from wenart import geometry as G
from wenart.synthetic.raster import rasterise_pdf_page

COLOURS = {
    "vector": (0, 150, 0),
    "raster": (0, 120, 120),
    "ocr": (30, 90, 220),
    "ai": (235, 130, 0),
    "derived": (120, 120, 120),
}
UNVERIFIED_COLOUR = (220, 20, 20)
# Generic pages (§2.9): furniture by how its type was decided, separators, site elements, scale dimensions.
TYPE_METHOD_COLOURS = {
    "rule": (0, 170, 0),
    "block_name": (30, 60, 230),
    "ai_two_pass": (0, 190, 210),
    "none": (220, 20, 20),
}
SEPARATOR_COLOUR = (220, 0, 220)
SITE_COLOUR = (150, 150, 150)
DIMENSION_COLOUR = (255, 140, 0)
MASK_COLOUR = (90, 90, 255)
MASK_ALPHA = 70
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
    colour: Optional[tuple] = None   # fixed colour instead of the method colour (generic pages)
    dashed: bool = False             # dashed outline (doorless openings, separators)
    closed: bool = True              # False: an open polyline (centre line, swing arc, separator, dimension)
    striped: bool = False            # diagonal stripes inside (furniture whose type nothing decided)


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
    """The PDF page rendered by pdftoppm at ``dpi`` (100 for the synthetic pages, 150 for generic ones)."""
    with tempfile.TemporaryDirectory() as tmp:
        png = rasterise_pdf_page(path, page, Path(tmp) / "page.png", dpi=dpi, gray=False)
        image = Image.open(png).convert("RGB")
        image.load()
    scale = dpi / 72.0
    height_px = image.height

    def to_pixels(p):
        return (p[0] * scale, height_px - p[1] * scale)

    return PageRaster(image=image, to_pixels=to_pixels)


def raster_from_dxf(path: Path, width_px: int = DXF_WIDTH_PX, clip_box=None) -> PageRaster:
    """Render the DXF model space into an image whose pixel mapping is known:
    the figure is sized to the extents' aspect ratio so the axes fill it.

    ``clip_box`` (Milestone 10, docs/milestone10.md §1.6b row 2): ``(x0, y0, x1, y1)`` in drawing units, a region of a
    multi-drawing sheet (``documents[].pages[].region_box``): only the entities whose box meets it are drawn and the
    window is that box grown by ``DXF_MARGIN``."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf import bbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    # recover.readfile, as the pipeline reads: it decodes the \U+XXXX escapes of R2000 files (synthetic-07's
    # Turkish texts), which plain ezdxf.readfile leaves as they are.
    from ezdxf import recover
    doc, _auditor = recover.readfile(str(path))
    msp = doc.modelspace()
    filter_func = None
    note = ""
    if clip_box is not None:
        x0, y0, x1, y1 = (float(v) for v in clip_box)
        cache = bbox.Cache()

        def filter_func(entity) -> bool:
            try:
                b = bbox.extents([entity], fast=True, cache=cache)
            except Exception:          # an entity ezdxf cannot measure: drawn (clipped by the window)
                return True
            return bool(b.has_data) and not (b.extmax.x < x0 or b.extmin.x > x1 or b.extmax.y < y0
                                             or b.extmin.y > y1)
    else:
        # The window is the drawing without its strays (``drawing_window``): one hatch 318 m off a 60 m sheet
        # (real02, HATCH:6633) shrank the whole sheet into a corner of the debug image.
        cache = bbox.Cache()
        ids, boxes = [], []
        for entity in msp:
            try:
                b = bbox.extents([entity], fast=True, cache=cache)
            except Exception:          # an entity ezdxf cannot measure: drawn, not part of the window
                continue
            if b.has_data:
                ids.append(f"{entity.dxftype()}:{entity.dxf.handle}")
                boxes.append((b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y))
        window = drawing_window(boxes)
        if window is None:
            image = Image.new("RGB", (width_px, width_px // 2), "white")
            return PageRaster(image=image, to_pixels=lambda p: (p[0], p[1]), note="empty DXF")
        (x0, y0, x1, y1), dropped = window
        if dropped:
            stray = {ids[i] for i in dropped}
            names = ", ".join(sorted(stray)[:5]) + (", ..." if len(stray) > 5 else "")
            note = (f"{len(stray)} stray entit{'y' if len(stray) == 1 else 'ies'} far outside the drawing "
                    f"left out of the window: {names}")

            def filter_func(entity) -> bool:
                return f"{entity.dxftype()}:{entity.dxf.handle}" not in stray
    mx, my = (x1 - x0) * DXF_MARGIN, (y1 - y0) * DXF_MARGIN
    x0, y0, x1, y1 = x0 - mx, y0 - my, x1 + mx, y1 + my
    height_px = max(200, int(round(width_px * (y1 - y0) / (x1 - x0))))
    fig = plt.figure(figsize=(width_px / 100.0, height_px / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    config = Configuration(background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=config).draw_layout(msp, finalize=True,
                                                                                    filter_func=filter_func)
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

    return PageRaster(image=image, to_pixels=to_pixels, note=note)


STRAY_QUANTILE = 0.02     # drawing_window: the core of the drawing is the 2-98 % range of the entity centres ...
STRAY_SPANS = 2.0         # ... and an entity whose box lies more than this many core spans beyond it is a stray


def drawing_window(boxes, quantile: float = STRAY_QUANTILE, spans: float = STRAY_SPANS):
    """``((x0, y0, x1, y1), dropped indices)`` of entity boxes ``(x0, y0, x1, y1)``: the union of the boxes that
    meet the drawing's core grown by ``spans`` times its size on every side; None without boxes.

    The core is the ``quantile`` .. ``1 - quantile`` range of the box centres per axis (the inner order statistics,
    so a single far entity never moves it, even in a small file). A stray entity far off the sheet (a hatch 318 m
    from a 60 m sheet) is dropped; the sheet frame, title block and dimensions around the drawing are kept. With
    fewer than 5 boxes every box is kept."""
    boxes = [tuple(float(v) for v in b) for b in boxes]
    if not boxes:
        return None
    arr = np.asarray(boxes, dtype=np.float64)
    keep = np.ones(len(boxes), dtype=bool)
    if len(boxes) >= 5:
        for lo_col, hi_col in ((0, 2), (1, 3)):
            centres = np.sort((arr[:, lo_col] + arr[:, hi_col]) / 2.0)
            n = len(centres)
            lo = centres[int(np.ceil(quantile * (n - 1)))]
            hi = centres[int(np.floor((1.0 - quantile) * (n - 1)))]
            span = max(hi - lo, 1e-9)
            band_lo, band_hi = lo - spans * span, hi + spans * span
            keep &= (arr[:, hi_col] >= band_lo) & (arr[:, lo_col] <= band_hi)
        if not keep.any():
            keep[:] = True
    kept = arr[keep]
    window = (float(kept[:, 0].min()), float(kept[:, 1].min()), float(kept[:, 2].max()), float(kept[:, 3].max()))
    return window, [int(i) for i in np.flatnonzero(~keep)]


def raster_from_page(page, box, width_px: int = DXF_WIDTH_PX) -> PageRaster:
    """Milestone 10: one drawing region of a large sheet, drawn from its strokes with Pillow (dark grey lines on
    white) inside ``box`` (page units, y up) grown by ``DXF_MARGIN``: the sheets' regions of real02 need no
    ezdxf rendering of the whole 59 MB sheet per region."""
    x0, y0, x1, y1 = (float(v) for v in box)
    mx, my = (x1 - x0) * DXF_MARGIN, (y1 - y0) * DXF_MARGIN
    x0, y0, x1, y1 = x0 - mx, y0 - my, x1 + mx, y1 + my
    w, h = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    height_px = max(200, int(round(width_px * h / w)))
    image = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(image)

    def to_pixels(p):
        return ((p[0] - x0) / w * width_px, (y1 - p[1]) / h * height_px)

    for st in page.strokes:
        pts = [to_pixels(p) for p in st.pts]
        if len(pts) >= 2:
            draw.line(pts + ([pts[0]] if st.closed and len(pts) > 2 else []), fill=(90, 90, 90), width=1)
    font = _font(11)
    for t in page.texts:
        draw.text(to_pixels((t.box[0], t.box[3])), t.text, fill=(60, 60, 60), font=font)
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


def _stripes(draw: ImageDraw.ImageDraw, pts: list, fill, step: float = 7.0) -> None:
    """45-degree stripes clipped to the polygon ``pts`` (pixels)."""
    from shapely.geometry import LineString, Polygon

    poly = Polygon(pts)
    if not poly.is_valid or poly.area <= 0:
        return
    x0, y0, x1, y1 = poly.bounds
    k = x0 - (y1 - y0)
    while k <= x1:
        line = LineString([(k, y1), (k + (y1 - y0), y0)])
        part = line.intersection(poly)
        for seg in getattr(part, "geoms", [part]):
            if seg.geom_type == "LineString" and seg.length > 0:
                draw.line(list(seg.coords), fill=fill, width=1)
        k += step


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
        colour = item.colour or COLOURS.get(item.method, COLOURS["derived"])
        alpha = int(255 * (0.35 + 0.65 * max(0.0, min(1.0, item.confidence))))
        unverified = item.status == "unverified"
        if unverified and item.colour is None:
            colour = UNVERIFIED_COLOUR
        fill = colour + (alpha,)
        path = pts + [pts[0]] if item.closed else pts
        if item.striped and item.closed:
            _stripes(draw, pts, colour + (110,))
        if unverified or item.dashed:
            for a, b in zip(path[:-1], path[1:]):
                _dashed_line(draw, a, b, fill, item.width)
        elif item.closed:
            draw.polygon(pts, outline=fill, width=item.width)
        else:
            draw.line(pts, fill=fill, width=item.width)
        if item.label:
            x = min(p[0] for p in pts) + 2
            y = min(p[1] for p in pts) + 1
            draw.text((x, y), item.label, fill=fill, font=font)
    if note:
        draw.rectangle([0, 0, base.width, 22], fill=(255, 255, 255, 200))
        draw.text((6, 4), note, fill=(0, 0, 0, 255), font=font)
    return Image.alpha_composite(base, overlay).convert("RGB")


def overlay_mask(raster: PageRaster, mask, units_to_m: float, colour=MASK_COLOUR, alpha: int = MASK_ALPHA) -> None:
    """Draw a wall mask (``MaskLayer`` in page metres) translucently onto ``raster.image`` (in place).

    The mask grid maps to page units (``/ units_to_m``) and from there to pixels by the raster's affine
    ``to_pixels``; the image is resampled nearest-neighbour."""
    arr = np.asarray(mask.mask).astype(np.uint8) * 255
    if arr.size == 0 or not arr.any():
        return
    rows, cols = arr.shape
    x0, y1 = mask.origin
    px = mask.px
    s = float(units_to_m) or 1.0

    def grid_to_pixel(c: float, r: float):
        return raster.to_pixels(((x0 + c * px) / s, (y1 - r * px) / s))

    o = grid_to_pixel(0.0, 0.0)
    ax = grid_to_pixel(1.0, 0.0)
    ay = grid_to_pixel(0.0, 1.0)
    a, d = ax[0] - o[0], ax[1] - o[1]          # pixel per grid column
    b, e = ay[0] - o[0], ay[1] - o[1]          # pixel per grid row
    det = a * e - b * d
    if abs(det) < 1e-12:
        return
    # Inverse affine (image pixel -> grid cell) for PIL's transform.
    inv = (e / det, -b / det, (b * o[1] - e * o[0]) / det, -d / det, a / det, (d * o[0] - a * o[1]) / det)
    src = Image.fromarray(arr, mode="L")
    layer = src.transform(raster.image.size, Image.AFFINE, inv, resample=Image.NEAREST)
    tint = Image.new("RGBA", raster.image.size, colour + (0,))
    tint.putalpha(layer.point(lambda v: alpha if v else 0))
    raster.image = Image.alpha_composite(raster.image.convert("RGBA"), tint).convert("RGB")


def write_debug_image(raster: PageRaster, items: list[DebugItem], out_path: Path, note: str = "") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image = draw_items(raster.image, items, raster.to_pixels, note=note or raster.note)
    image.save(out_path, "PNG", optimize=True)
    return out_path


def box_polygon(box) -> list[tuple[float, float]]:
    return G.box_corners(box)


def legend_note(prefix: str = "", generic: bool = False) -> str:
    base = "green = vector, blue = ocr, orange = ai, grey = derived, dashed red = unverified"
    if generic:
        base = ("blue tint = wall mask, lines = wall centres, dashed = doorless / magenta separator, furniture: green "
                "rule, blue block name, cyan AI, red striped none; grey = site; orange = scale dimensions")
    return f"{prefix} | {base}" if prefix else base
