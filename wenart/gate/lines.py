"""Added-lines check of the change gate (docs/milestone5.md §4.2 ``added_lines``).

What: straight lines the polish drew on bare structure (a painted frame, a
shelf, a window on a bare wall). On each structure region (floor, ceiling,
walls; window panes and background removed) the test image's Canny edges
are turned into straight segments with ``cv2.HoughLinesP``; a segment of
length >= ``min_len_frac`` x W counts when its pixels have no reference
edge within ``match_px`` (3 px) over >= ``unmatched_frac`` of its length.
Value per region = the unmatched length of the counted segments / W.

Why: edge recall only sees reference edges that disappear; a new edge on a
bare wall leaves recall at 1.0. Long straight new segments are what painted
additions look like, while texture gives short, scattered edges.

Reference edges for the matching = Canny on the Cycles image plus the
view's geometry edges, so a line along a real but low-contrast boundary
(white frame on a white wall) is not counted as new.

OpenCV is imported inside the functions.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np

MATCH_PX = 3.0                # a segment pixel is matched when a reference edge is within 3 px
HOUGH_RHO = 1.0               # px
HOUGH_THETA = math.pi / 180.0
HOUGH_VOTES_FRAC = 0.5        # accumulator votes needed = 0.5 x the minimum length (at least 20)
HOUGH_MIN_VOTES = 20
HOUGH_MAX_GAP_PX = 3          # largest gap bridged inside one segment


def segments(edges, min_len_px: float, max_gap_px: int = HOUGH_MAX_GAP_PX) -> np.ndarray:
    """int N x 4 ``[x0, y0, x1, y1]`` straight segments of a bool edge map (``cv2.HoughLinesP``)."""
    import cv2
    e = np.asarray(edges, dtype=bool)
    if not e.any():
        return np.zeros((0, 4), dtype=np.int32)
    votes = max(HOUGH_MIN_VOTES, int(HOUGH_VOTES_FRAC * float(min_len_px)))
    found = cv2.HoughLinesP(e.astype(np.uint8) * 255, HOUGH_RHO, HOUGH_THETA, votes,
                            minLineLength=float(min_len_px), maxLineGap=float(max_gap_px))
    if found is None:
        return np.zeros((0, 4), dtype=np.int32)
    return np.asarray(found, dtype=np.int32).reshape(-1, 4)    # OpenCV 4 gives N x 1 x 4, OpenCV 5 N x 4


def segment_pixels(seg) -> tuple[np.ndarray, np.ndarray]:
    """``(xs, ys)`` integer pixel samples along a segment, one per pixel of its longer axis."""
    x0, y0, x1, y1 = (int(v) for v in seg)
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.rint(np.linspace(x0, x1, n)).astype(np.int64)
    ys = np.rint(np.linspace(y0, y1, n)).astype(np.int64)
    return xs, ys


def unmatched_share(seg, match_dist, match_px: float = MATCH_PX) -> float:
    """Share of the segment's pixels whose nearest reference edge is farther than ``match_px``."""
    xs, ys = segment_pixels(seg)
    d = np.asarray(match_dist)[ys, xs]
    return float((d > float(match_px)).mean())


def added_lines(test_edges, match_dist, region_masks: dict, region_ids: Iterable[str], width: int,
                min_len_frac: float, unmatched_frac: float, exclude=None,
                match_px: float = MATCH_PX) -> tuple[dict, list]:
    """``({"global", "regions", "skipped"}, lines)`` for the structure regions of one test image.

    ``test_edges``: bool Canny map of the test image; ``match_dist``: distance
    to the nearest reference edge (``edges.distance_to``); ``exclude``: bool
    mask removed from every region (panes, background). ``lines`` lists
    every counted segment ``{"region", "seg": [x0, y0, x1, y1], "length",
    "unmatched"}`` for the debug image. ``global`` = all regions together.
    """
    edges = np.asarray(test_edges, dtype=bool)
    keep_out = None if exclude is None else np.asarray(exclude, dtype=bool)
    min_len = float(min_len_frac) * float(width)
    out = {"global": 0.0, "regions": {}, "skipped": {}}
    lines: list = []
    total = 0.0
    for rid in region_ids:
        mask = np.asarray(region_masks[rid], dtype=bool)
        if keep_out is not None:
            mask = mask & ~keep_out
        if not mask.any():
            out["skipped"][rid] = "too_small"
            continue
        length_sum = 0.0
        for seg in segments(edges & mask, min_len):
            x0, y0, x1, y1 = (int(v) for v in seg)
            length = math.hypot(x1 - x0, y1 - y0)
            share = unmatched_share(seg, match_dist, match_px)
            if share >= float(unmatched_frac):
                length_sum += length * share
                lines.append({"region": rid, "seg": [x0, y0, x1, y1], "length": round(length, 1),
                              "unmatched": round(share, 3)})
        out["regions"][rid] = round(length_sum / float(width), 4)
        total += length_sum
    out["global"] = round(total / float(width), 4)
    return out, lines
