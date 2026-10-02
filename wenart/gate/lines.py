"""Added-lines check of the change gate (docs/milestone5.md §4.2 ``added_lines``).

What: straight lines the polish drew on bare structure (a painted frame, a
shelf, a window on a bare wall). On each structure region (floor, ceiling,
walls; window panes and background removed) the test image's Canny edges
are turned into straight segments with ``cv2.HoughLinesP``; a segment of
length >= ``min_len_frac`` x W counts when its pixels have no reference
edge within ``match_px`` (3 px) over >= ``unmatched_frac`` of their length.
Value per region = the unmatched length of the counted segments / W.

Why: edge recall only sees reference edges that disappear; a new edge on a
bare wall leaves recall at 1.0. Long straight new segments are what painted
additions look like.

Reference edges for the matching:

- Canny on the Cycles image (full thresholds) plus the view's geometry
  edges, so a line along a real but low-contrast boundary (white frame on a
  white wall) is not counted as new;
- plus the *oriented* low-threshold Canny edges of the Cycles image
  (thresholds x ``ref_factor``, 0.2; ``edges.edge_angles``): a segment
  pixel is also matched by such an edge within ``match_px`` whose gradient
  orientation is within ``ref_angle_deg`` (10 deg) of the segment's normal.
  Texture is not only short and scattered: plank seams, tile grout and
  herringbone spines are long straight lines that sit just below the Canny
  thresholds in the Cycles image and rise above them when the polish (or a
  benign unsharp mask, +0.3 EV) makes the texture crisper. Without this
  term such views were rejected although nothing moved (review finding G2:
  real parquet / tile textures at 1920 x 1080 gave 0.05-0.72 for the benign
  unsharp control, limit 0.04). The orientation test keeps the check
  sensitive on textured floors: a rug outline or a stripe painted across
  the grout finds no parallel reference edge (0.13-0.95 on the same floors,
  where matching any low-threshold edge regardless of orientation gave
  0.0-0.32). Like the Hough settings and ``match_px`` these are code
  constants (``REF_FACTOR``, ``ANGLE_TOL_DEG``) that ``added_lines.ref_factor``
  / ``ref_angle_deg`` in thresholds.yaml override (then part of the gate
  key); ``ref_factor`` 0 turns the term off. Calibrated in run 1a.

OpenCV is imported inside the functions.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from wenart.gate.edges import NO_ANGLE

MATCH_PX = 3.0                # a segment pixel is matched when a reference edge is within 3 px
REF_FACTOR = 0.2              # Canny thresholds x this for the oriented reference edges (0 = off)
ANGLE_TOL_DEG = 10.0          # an oriented reference edge matches a segment within this angle
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


def _disk(radius: float) -> list[tuple[int, int]]:
    """Integer offsets ``(dx, dy)`` with dx^2 + dy^2 <= radius^2 (the pixels within ``radius``)."""
    r = int(math.floor(float(radius)))
    return [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= radius * radius]


def segment_normal_deg(seg) -> float:
    """Orientation (degrees mod 180) of a segment's normal: the gradient direction of an edge along it."""
    x0, y0, x1, y1 = (int(v) for v in seg)
    return math.degrees(math.atan2(x1 - x0, -(y1 - y0))) % 180.0


def oriented_hits(seg, xs, ys, ref_angle, match_px: float = MATCH_PX,
                  angle_tol_deg: float = ANGLE_TOL_DEG) -> np.ndarray:
    """bool per sample: an edge of ``ref_angle`` lies within ``match_px`` with an orientation within the tolerance."""
    angle = np.asarray(ref_angle)
    h, w = angle.shape
    normal = segment_normal_deg(seg)
    hit = np.zeros(len(xs), dtype=bool)
    for dx, dy in _disk(match_px):
        xx, yy = xs + dx, ys + dy
        inside = (xx >= 0) & (xx < w) & (yy >= 0) & (yy < h)
        a = angle[np.clip(yy, 0, h - 1), np.clip(xx, 0, w - 1)].astype(np.float32)
        diff = np.abs(np.mod(a - normal + 90.0, 180.0) - 90.0)
        hit |= inside & (a != NO_ANGLE) & (diff <= float(angle_tol_deg))
    return hit


def unmatched_pixels(seg, match_dist, match_px: float = MATCH_PX, ref_angle=None,
                     angle_tol_deg: float = ANGLE_TOL_DEG) -> np.ndarray:
    """bool per segment sample: no reference edge within ``match_px`` (``match_dist``), nor a parallel
    oriented reference edge (``ref_angle``, when given)."""
    xs, ys = segment_pixels(seg)
    unmatched = np.asarray(match_dist)[ys, xs] > float(match_px)
    if ref_angle is not None and unmatched.any():
        sel = np.flatnonzero(unmatched)
        unmatched[sel] = ~oriented_hits(seg, xs[sel], ys[sel], ref_angle, match_px, angle_tol_deg)
    return unmatched


def unmatched_share(seg, match_dist, match_px: float = MATCH_PX, ref_angle=None,
                    angle_tol_deg: float = ANGLE_TOL_DEG) -> float:
    """Share of the segment's pixels with no matching reference edge (see ``unmatched_pixels``)."""
    return float(unmatched_pixels(seg, match_dist, match_px, ref_angle, angle_tol_deg).mean())


def added_lines(test_edges, match_dist, region_masks: dict, region_ids: Iterable[str], width: int,
                min_len_frac: float, unmatched_frac: float, exclude=None,
                match_px: float = MATCH_PX, ref_angle=None,
                angle_tol_deg: float = ANGLE_TOL_DEG) -> tuple[dict, list]:
    """``({"global", "regions", "skipped"}, lines)`` for the structure regions of one test image.

    ``test_edges``: bool Canny map of the test image; ``match_dist``: distance
    to the nearest reference edge (``edges.distance_to``); ``ref_angle``: the
    oriented low-threshold reference edges (``edges.edge_angles``; None = not
    used); ``exclude``: bool mask removed from every region (panes,
    background). ``lines`` lists every counted segment ``{"region", "seg":
    [x0, y0, x1, y1], "length", "unmatched"}`` for the debug image.
    ``global`` = all regions together.
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
            share = unmatched_share(seg, match_dist, match_px, ref_angle, angle_tol_deg)
            if share >= float(unmatched_frac):
                length_sum += length * share
                lines.append({"region": rid, "seg": [x0, y0, x1, y1], "length": round(length, 1),
                              "unmatched": round(share, 3)})
        out["regions"][rid] = round(length_sum / float(width), 4)
        total += length_sum
    out["global"] = round(total / float(width), 4)
    return out, lines
