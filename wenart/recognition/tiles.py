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
  almost the whole page AND is a thin ring: nearly all of its ink lies in a
  band along its bounding box), then take the largest components until they
  cover >= 60 % of the remaining ink and return their joint bounding box plus
  a margin. A plan that fills the sheet spans the page like a frame but has
  its ink inside the box, so it is kept. ``drawing_extent_info`` returns the
  same box plus the dropped frames, so the caller can record them. Removing
  the title block or the dimension strip is NOT attempted.
- ``tiles(box, tile_px, overlap)``: square tiles that cover ``box`` with the
  given overlap; the last tile of a row / column is shifted so it ends at the
  box edge, so no tile reaches outside the box.
- ``merge_tile_items(items, iou)``: duplicates of one symbol seen in two
  overlapping tiles are merged (same type, IoU >= 0.5, the higher confidence
  wins). A proposal marked ``edge_clipped`` (its box touches an inner tile
  edge, so the tile saw only part of the symbol) is also merged into a
  same-type proposal that contains >= 80 % of the smaller box, and the whole
  view wins over the fragment. Proposals of different types that overlap are
  both kept and counted as a type conflict, so nothing is dropped silently.

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
FRAME_SPAN = 0.80             # a page frame spans >= this share of BOTH page sides ...
FRAME_BAND_SHARE = 0.03       # ... and keeps its ink in a band along its box: band = max(3 % of the
FRAME_BAND_MIN_CLOSE = 3      #     side, 3 x the closing kernel), ink inside the band-eroded box ...
FRAME_INNER_INK_SHARE = 0.15  # ... is < 15 % of the component's ink (a drawing has its ink inside)
ANALYSIS_MAX_SIDE = 2600      # pages are analysed at this size or smaller (speed), boxes are scaled back
ADAPTIVE_BLOCK_PX = 51        # adaptive threshold window (odd) and offset: ink is darker than
ADAPTIVE_OFFSET = 15          # the local mean by at least this much (paper shading survives)
DEFAULT_MARGIN = 0.05         # extent margin as a share of the longer extent side ...
MIN_MARGIN_PX = 24            # ... but at least this many pixels
DEFAULT_TILE_PX = 1024
DEFAULT_OVERLAP = 0.2
MERGE_IOU = 0.5
EDGE_TOUCH_PX = 3             # a box this close to an inner tile edge was clipped by the tile
CLIPPED_CONTAIN = 0.80        # a clipped fragment merges into a same-type box holding this share of the smaller box

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

def ink_components(mask: np.ndarray, close_px: int = CLOSE_KERNEL_PX, frame_span: float = FRAME_SPAN) -> list[dict]:
    """Connected components of the closed ink mask, largest ink count first.

    Each entry: ``{"box": [x0, y0, x1, y1], "ink": n_ink_pixels, "span": (w/W, h/H),
    "inner_ink_share": share of the ink inside the box eroded by the frame band,
    or None}``. ``ink`` counts the pixels of the ORIGINAL mask inside the closed
    component, so the closing (which fills blobs) does not inflate thin lines.
    ``inner_ink_share`` is computed only for components that span >= ``frame_span``
    of both page sides (the frame candidates); it tells a thin ring (~0) from a
    drawing that fills the sheet (its walls and symbols lie inside the band).
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
        span = (w / width, h / height)
        inner_share = None
        if span[0] >= frame_span and span[1] >= frame_span and ink_per_label[i] > 0:
            band_x = max(int(FRAME_BAND_SHARE * w), FRAME_BAND_MIN_CLOSE * close_px)
            band_y = max(int(FRAME_BAND_SHARE * h), FRAME_BAND_MIN_CLOSE * close_px)
            inner = 0
            if w > 2 * band_x and h > 2 * band_y:
                sub_labels = labels[y + band_y:y + h - band_y, x + band_x:x + w - band_x]
                sub_mask = mask[y + band_y:y + h - band_y, x + band_x:x + w - band_x]
                inner = int(np.count_nonzero((sub_labels == i) & (sub_mask > 0)))
            inner_share = round(inner / int(ink_per_label[i]), 4)
        comps.append({"box": [x, y, x + w, y + h], "ink": int(ink_per_label[i]), "span": span,
                      "inner_ink_share": inner_share})
    comps.sort(key=lambda c: c["ink"], reverse=True)
    return comps


def is_page_frame(comp: dict, frame_span: float = FRAME_SPAN, inner_share: float = FRAME_INNER_INK_SHARE) -> bool:
    """True for a thin ring that spans almost the whole page in both directions.

    A sheet border, the paper edge in a photo or a title-block frame runs
    along the page edges and holds a lot of ink (a long thin rectangle), so
    it would otherwise win the "largest component" rule. The span alone is
    not enough: a plan with 5-10 % margins spans the page just the same. What
    tells them apart is the shape: a frame keeps (almost) all of its ink in a
    band along its bounding box, a drawing has walls and symbols inside it.
    A component without ``inner_ink_share`` (span too small) is never a frame.
    """
    sw, sh = comp["span"]
    share = comp.get("inner_ink_share")
    return sw >= frame_span and sh >= frame_span and share is not None and share < inner_share


def drawing_extent_info(image, *, margin: float = DEFAULT_MARGIN, min_margin_px: int = MIN_MARGIN_PX,
                        ink_share: float = INK_SHARE, close_px: int = CLOSE_KERNEL_PX) -> dict:
    """``drawing_extent`` plus what it decided, for the caller's record.

    Returns ``{"extent": box, "frames": [dropped frame components, page pixels],
    "n_components": components considered, "n_chosen": components in the box,
    "ink_share_in_extent": share of the non-frame ink held by the chosen ones}``.
    """
    import cv2
    gray = load_gray(image)
    height, width = gray.shape
    scale = 1.0
    if max(height, width) > ANALYSIS_MAX_SIDE:
        scale = ANALYSIS_MAX_SIDE / max(height, width)
        gray = cv2.resize(gray, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)
    all_comps = ink_components(ink_mask(gray), close_px)
    frames = [c for c in all_comps if is_page_frame(c)]
    comps = [c for c in all_comps if not is_page_frame(c)]
    info = {"frames": [{"box": [int(round(v / scale)) for v in c["box"]], "ink": c["ink"],
                        "span": [round(c["span"][0], 3), round(c["span"][1], 3)],
                        "inner_ink_share": c["inner_ink_share"]} for c in frames],
            "n_components": len(comps), "n_chosen": 0, "ink_share_in_extent": 0.0}
    total_ink = sum(c["ink"] for c in comps)
    if total_ink == 0:
        info["extent"] = [0, 0, width, height]
        return info
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
    info["extent"] = [int(max(0, np.floor(x0 - pad))), int(max(0, np.floor(y0 - pad))),
                      int(min(width, np.ceil(x1 + pad))), int(min(height, np.ceil(y1 + pad)))]
    info["n_chosen"] = len(chosen)
    info["ink_share_in_extent"] = round(covered / total_ink, 4)
    return info


def drawing_extent(image, *, margin: float = DEFAULT_MARGIN, min_margin_px: int = MIN_MARGIN_PX,
                   ink_share: float = INK_SHARE, close_px: int = CLOSE_KERNEL_PX) -> Box:
    """Ink bounding box of the drawing on ``image`` (page pixels, integers).

    Steps: binarise, close with ``close_px``, label components, drop the page
    frame (span and thin-ring shape, see ``is_page_frame``), take the largest
    components until they hold >= ``ink_share`` of the remaining ink, return
    the union box grown by ``margin`` (a share of the longer side, at least
    ``min_margin_px``) and clamped to the page. A page without ink returns the
    whole page, so the caller still gets one tile.

    Pages larger than ``ANALYSIS_MAX_SIDE`` are analysed downscaled (the
    kernel and threshold window are in analysis pixels); the box is scaled back.
    """
    return drawing_extent_info(image, margin=margin, min_margin_px=min_margin_px, ink_share=ink_share,
                               close_px=close_px)["extent"]


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

def touches_inner_edge(box: Sequence[float], tile: Sequence[float], extent: Sequence[float],
                       tol_px: float = EDGE_TOUCH_PX) -> bool:
    """True when a crop-pixel ``box`` lies within ``tol_px`` of a side of ``tile`` that is
    not a side of ``extent`` (page pixels): the tile cut the symbol, the drawing did not end."""
    tile_w, tile_h = tile[2] - tile[0], tile[3] - tile[1]
    return ((box[0] <= tol_px and tile[0] != extent[0])
            or (box[1] <= tol_px and tile[1] != extent[1])
            or (box[2] >= tile_w - tol_px and tile[2] != extent[2])
            or (box[3] >= tile_h - tol_px and tile[3] != extent[3]))


def _overlap_share_of_smaller(a: Sequence[float], b: Sequence[float]) -> float:
    """Intersection area over the area of the smaller box (1.0 = the smaller lies inside the larger)."""
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    smaller = min(G.box_area(a), G.box_area(b))
    return inter / smaller if smaller > 0 else 0.0


def _tiles_of(item: dict) -> set[int]:
    return {int(item["tile"])} if "tile" in item else {int(t) for t in item.get("tiles", [])}


def merge_tile_items(items: Sequence[dict], iou_thresh: float = MERGE_IOU,
                     clipped_contain: float = CLIPPED_CONTAIN) -> tuple[list[dict], dict]:
    """Merge duplicate proposals from overlapping tiles.

    ``items`` are symbol proposals in page pixels (``type``, ``box``,
    ``confidence``, ``rotation_deg``, plus ``tile``: the index of the tile they
    came from, and optionally ``edge_clipped``: the box touches an inner tile
    edge, so that tile saw only part of the symbol). Two proposals of the SAME
    type are one symbol when their IoU is >= ``iou_thresh``, or when one of
    them is ``edge_clipped`` and the other contains >= ``clipped_contain`` of
    the smaller box (a fragment under half the symbol never reaches the IoU).
    The kept proposal is the one with the higher confidence, except that a
    whole view always wins over a clipped fragment (its box is the better
    geometry); the ``tiles`` list records every tile that saw the symbol.
    Proposals of DIFFERENT types that overlap are both kept (the two-pass
    stage decides type clashes) and counted in ``stats["type_conflicts"]``.

    Returns ``(merged_items, stats)`` with ``stats = {"n_input", "n_merged",
    "n_duplicates", "n_clipped", "n_clipped_absorbed", "type_conflicts"}``.
    """
    ordered = sorted(enumerate(items), key=lambda p: (-float(p[1].get("confidence", 0.0)), p[0]))
    kept: list[dict] = []
    duplicates = absorbed = 0
    for _, item in ordered:
        twin, by_containment = None, False
        for cand in kept:
            if cand["type"] != item["type"]:
                continue
            if G.box_iou(cand["box"], item["box"]) >= iou_thresh:
                twin = cand
                break
            if ((cand.get("edge_clipped") or item.get("edge_clipped"))
                    and _overlap_share_of_smaller(cand["box"], item["box"]) >= clipped_contain):
                twin, by_containment = cand, True
                break
        if twin is None:
            new = dict(item)
            new["tiles"] = sorted(_tiles_of(item))
            new["edge_clipped"] = bool(item.get("edge_clipped", False))
            new.pop("tile", None)
            kept.append(new)
            continue
        duplicates += 1
        absorbed += by_containment
        seen = set(twin["tiles"]) | _tiles_of(item)
        if twin["edge_clipped"] and not item.get("edge_clipped"):
            # The kept one is a fragment: take the whole view's geometry and confidence.
            twin.update({k: v for k, v in item.items() if k not in ("tile", "tiles")})
            twin["edge_clipped"] = False
        twin["tiles"] = sorted(seen)
    conflicts = 0
    for i, a in enumerate(kept):
        for b in kept[i + 1:]:
            if a["type"] != b["type"] and G.box_iou(a["box"], b["box"]) >= iou_thresh:
                conflicts += 1
    stats = {"n_input": len(items), "n_merged": len(kept), "n_duplicates": duplicates,
             "n_clipped": sum(1 for it in items if it.get("edge_clipped")), "n_clipped_absorbed": absorbed,
             "type_conflicts": conflicts}
    return kept, stats
