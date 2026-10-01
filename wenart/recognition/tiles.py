"""Crop-to-drawing and tiling for the symbol pass of the vision-language models.

Why: the synthetic A3 scans are 2481 x 1754 px, the drawing itself fills only a
quarter of the sheet, and the client downscales the whole page to 1600 px
before sending it (``vlm_client.DEFAULT_MAX_SIDE``). A chair is then ~15 px
and the models miss most symbols (Milestone 2 bake-off). Sending the drawing
area at full resolution, in overlapping tiles, keeps the symbols large.

Three pure functions (OpenCV + numpy only, no network, no model):

- ``drawing_extent(image)``: ink bounding box of the drawing on the page.
  Binarise (adaptive threshold, so a photographed page with shading works),
  close with a 25 px kernel so the lines of one drawing join into blobs, label
  the connected components, drop the page frame (a component that spans
  almost the whole page), then take the largest components until they cover
  >= 60 % of the remaining ink and return their joint bounding box plus a
  margin. Removing the title block or the dimension strip is NOT attempted.
- ``tiles(box, tile_px, overlap)``: square tiles that cover ``box`` with the
  given overlap; the last tile of a row / column is shifted so it ends at the
  box edge, so no tile reaches outside the box.
- ``merge_tile_items(items, iou)``: duplicates of one symbol seen in two
  overlapping tiles are merged (same type, IoU >= 0.5, the higher confidence
  wins); proposals of different types that overlap are both kept and counted
  as a type conflict, so nothing is dropped silently.

Boxes are ``[x0, y0, x1, y1]`` in page pixels, origin top-left, x1/y1 exclusive
for tiles (so ``image.crop(tile)`` is the tile).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from wenart import geometry as G

CLOSE_KERNEL_PX = 25          # docs/milestone3.md section 5
INK_SHARE = 0.60              # the group of components must cover this share of the ink
FRAME_SPAN = 0.80             # a component spanning >= this share of BOTH page sides is the page frame
ANALYSIS_MAX_SIDE = 2600      # pages are analysed at this size or smaller (speed), boxes are scaled back
ADAPTIVE_BLOCK_PX = 51        # adaptive threshold window (odd) and offset: ink is darker than
ADAPTIVE_OFFSET = 15          # the local mean by at least this much (paper shading survives)
DEFAULT_MARGIN = 0.05         # extent margin as a share of the longer extent side ...
MIN_MARGIN_PX = 24            # ... but at least this many pixels
DEFAULT_TILE_PX = 1024
DEFAULT_OVERLAP = 0.2
MERGE_IOU = 0.5

Box = list[float]


# --------------------------------------------------------------------------
# Image loading and binarisation
# --------------------------------------------------------------------------

def load_gray(image) -> np.ndarray:
    """``image`` (path, PIL image or numpy array) as an 8-bit grayscale array."""
    if isinstance(image, np.ndarray):
        arr = image
        if arr.ndim == 3:
            import cv2
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY) if arr.shape[2] == 3 else cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
        return arr.astype(np.uint8)
    if isinstance(image, (str, Path)):
        from PIL import Image
        with Image.open(image) as img:
            return np.asarray(img.convert("L"))
    return np.asarray(image.convert("L"))


def ink_mask(gray: np.ndarray, block_px: int = ADAPTIVE_BLOCK_PX, offset: int = ADAPTIVE_OFFSET) -> np.ndarray:
    """Binary ink mask (255 = ink): pixels darker than their local mean by ``offset``.

    Adaptive thresholding is used instead of Otsu because a photographed page
    has a dark table around it and a brightness gradient over the paper; the
    uniform dark surround is not ink to a local threshold, only its edge is.
    """
    import cv2
    block = max(3, block_px | 1)  # must be odd
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, offset)


# --------------------------------------------------------------------------
# Drawing extent
# --------------------------------------------------------------------------

def ink_components(mask: np.ndarray, close_px: int = CLOSE_KERNEL_PX) -> list[dict]:
    """Connected components of the closed ink mask, largest ink count first.

    Each entry: ``{"box": [x0, y0, x1, y1], "ink": n_ink_pixels, "span": (w/W, h/H)}``.
    ``ink`` counts the pixels of the ORIGINAL mask inside the closed component,
    so the closing (which fills blobs) does not inflate thin lines.
    """
    import cv2
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_px, close_px))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    ink_per_label = np.bincount(labels[mask > 0].ravel(), minlength=n)
    height, width = mask.shape
    comps = []
    for i in range(1, n):
        x, y, w, h, _area = (int(v) for v in stats[i])
        comps.append({"box": [x, y, x + w, y + h], "ink": int(ink_per_label[i]),
                      "span": (w / width, h / height)})
    comps.sort(key=lambda c: c["ink"], reverse=True)
    return comps


def is_page_frame(comp: dict, frame_span: float = FRAME_SPAN) -> bool:
    """True for a component that spans almost the whole page in both directions.

    A sheet border, the paper edge in a photo or a title-block frame runs
    along the page edges; a drawing never reaches both page edges, it has
    margins. Such a component holds a lot of ink (a long thin rectangle) and
    would otherwise win the "largest component" rule.
    """
    sw, sh = comp["span"]
    return sw >= frame_span and sh >= frame_span


def drawing_extent(image, *, margin: float = DEFAULT_MARGIN, min_margin_px: int = MIN_MARGIN_PX,
                   ink_share: float = INK_SHARE, close_px: int = CLOSE_KERNEL_PX) -> Box:
    """Ink bounding box of the drawing on ``image`` (page pixels, integers).

    Steps: binarise, close with ``close_px``, label components, drop the page
    frame, take the largest components until they hold >= ``ink_share`` of the
    remaining ink, return the union box grown by ``margin`` (a share of the
    longer side, at least ``min_margin_px``) and clamped to the page. A page
    without ink returns the whole page, so the caller still gets one tile.

    Pages larger than ``ANALYSIS_MAX_SIDE`` are analysed downscaled (the
    kernel and threshold window are in analysis pixels); the box is scaled back.
    """
    import cv2
    gray = load_gray(image)
    height, width = gray.shape
    scale = 1.0
    if max(height, width) > ANALYSIS_MAX_SIDE:
        scale = ANALYSIS_MAX_SIDE / max(height, width)
        gray = cv2.resize(gray, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)
    comps = [c for c in ink_components(ink_mask(gray), close_px) if not is_page_frame(c)]
    total_ink = sum(c["ink"] for c in comps)
    if total_ink == 0:
        return [0, 0, width, height]
    chosen, covered = [], 0
    for comp in comps:                       # largest first
        chosen.append(comp)
        covered += comp["ink"]
        if covered >= ink_share * total_ink:
            break
    x0 = min(c["box"][0] for c in chosen) / scale
    y0 = min(c["box"][1] for c in chosen) / scale
    x1 = max(c["box"][2] for c in chosen) / scale
    y1 = max(c["box"][3] for c in chosen) / scale
    pad = max(min_margin_px, margin * max(x1 - x0, y1 - y0))
    return [int(max(0, np.floor(x0 - pad))), int(max(0, np.floor(y0 - pad))),
            int(min(width, np.ceil(x1 + pad))), int(min(height, np.ceil(y1 + pad)))]


def box_contains(outer: Sequence[float], inner: Sequence[float], margin: float = 0.0) -> bool:
    """True when ``inner`` lies inside ``outer`` with at least ``margin`` pixels to spare on every side."""
    return (inner[0] - outer[0] >= margin and inner[1] - outer[1] >= margin
            and outer[2] - inner[2] >= margin and outer[3] - inner[3] >= margin)


# --------------------------------------------------------------------------
# Tiles
# --------------------------------------------------------------------------

def _starts(length: int, tile: int, step: int) -> list[int]:
    """Start offsets of tiles of size ``tile`` with stride ``step`` covering ``length``."""
    if length <= tile:
        return [0]
    starts = list(range(0, length - tile, step))
    starts.append(length - tile)  # the last tile ends exactly at the edge
    return starts


def tiles(box: Sequence[float], tile_px: int = DEFAULT_TILE_PX, overlap: float = DEFAULT_OVERLAP) -> list[Box]:
    """Square tiles of ``tile_px`` covering ``box`` with ``overlap`` (share of the tile side).

    Tiles are ``[x0, y0, x1, y1]`` integer page pixels, x1/y1 exclusive, row by
    row. A box side shorter than ``tile_px`` gives one tile of the box's size
    in that direction (never a tile outside the box); otherwise the stride is
    ``tile_px * (1 - overlap)`` and the last tile is shifted onto the edge, so
    the last two tiles may overlap more than asked, never less.
    """
    if not 0.0 <= overlap < 1.0:
        raise ValueError(f"overlap must be in [0, 1), got {overlap}")
    if tile_px < 1:
        raise ValueError(f"tile_px must be >= 1, got {tile_px}")
    x0, y0, x1, y1 = int(box[0]), int(box[1]), int(np.ceil(box[2])), int(np.ceil(box[3]))
    width, height = max(1, x1 - x0), max(1, y1 - y0)
    tile_w, tile_h = min(tile_px, width), min(tile_px, height)
    step = max(1, int(round(tile_px * (1.0 - overlap))))
    out = []
    for ty in _starts(height, tile_h, step):
        for tx in _starts(width, tile_w, step):
            out.append([x0 + tx, y0 + ty, x0 + tx + tile_w, y0 + ty + tile_h])
    return out


def offset_box(box: Sequence[float], dx: float, dy: float) -> Box:
    """Crop-pixel box -> page-pixel box of a crop whose top-left corner is at (dx, dy)."""
    return [round(box[0] + dx, 1), round(box[1] + dy, 1), round(box[2] + dx, 1), round(box[3] + dy, 1)]


# --------------------------------------------------------------------------
# Merge across tiles
# --------------------------------------------------------------------------

def merge_tile_items(items: Sequence[dict], iou_thresh: float = MERGE_IOU) -> tuple[list[dict], dict]:
    """Merge duplicate proposals from overlapping tiles.

    ``items`` are symbol proposals in page pixels (``type``, ``box``,
    ``confidence``, ``rotation_deg``, plus ``tile``: the index of the tile they
    came from). Two proposals of the SAME type with IoU >= ``iou_thresh`` are
    one symbol: the one with the higher confidence is kept and its ``tiles``
    list records every tile that saw it. Proposals of DIFFERENT types that
    overlap that much are both kept (the two-pass stage decides type clashes)
    and counted in ``stats["type_conflicts"]``.

    Returns ``(merged_items, stats)`` with ``stats = {"n_input", "n_merged",
    "n_duplicates", "type_conflicts"}``.
    """
    ordered = sorted(enumerate(items), key=lambda p: (-float(p[1].get("confidence", 0.0)), p[0]))
    kept: list[dict] = []
    duplicates = 0
    for _, item in ordered:
        twin = None
        for cand in kept:
            if cand["type"] == item["type"] and G.box_iou(cand["box"], item["box"]) >= iou_thresh:
                twin = cand
                break
        if twin is None:
            new = dict(item)
            new["tiles"] = sorted({int(t) for t in ([item["tile"]] if "tile" in item else item.get("tiles", []))})
            new.pop("tile", None)
            kept.append(new)
        else:
            duplicates += 1
            seen = set(twin["tiles"]) | ({int(item["tile"])} if "tile" in item else set(item.get("tiles", [])))
            twin["tiles"] = sorted(seen)
    conflicts = 0
    for i, a in enumerate(kept):
        for b in kept[i + 1:]:
            if a["type"] != b["type"] and G.box_iou(a["box"], b["box"]) >= iou_thresh:
                conflicts += 1
    stats = {"n_input": len(items), "n_merged": len(kept), "n_duplicates": duplicates, "type_conflicts": conflicts}
    return kept, stats
