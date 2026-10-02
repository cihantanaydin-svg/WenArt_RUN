"""Lost-edge check of the change gate (docs/milestone5.md §4.2 ``edges``).

What: the reference edges are the geometry edges of the view
(``wenart.views.geometry_edges``: index changes, depth jumps, normal turns)
kept only where Canny on the Cycles image also sees an edge within
``radius_px``. Recall = the share of those reference pixels that have a
Canny edge of the test image within ``radius_px`` (exact Euclidean distance
from ``cv2.distanceTransform``), for the whole view and per object.

Why recall and not edge IoU: texture added by the polish creates many new
Canny edges, which drops a raw edge IoU to about 0.47 while recall stays
1.0 (CPU experiment in the spec research); a moved, scaled or removed
object loses its outline, which recall sees. New edges are the job of the
added-lines check (``lines.py``).

Test edges for the recall use the Canny thresholds x ``TEST_FACTOR`` (0.5;
``edges.test_factor`` in thresholds.yaml overrides it): an edge that is
only weaker in the test image is not lost. With the same thresholds on both
sides a white frame on a white wall (a step of about 36 grey levels sits
right at Canny high 75 after the sigma-1.5 blur) vanished under the benign
blur (sigma 1) and exposure (-0.3 EV) controls (window recall 0.0), while
the factor 0.5 keeps every benign control at recall 1.0 and leaves the
shift/scale negatives unchanged (synthetic room, 960 and 1920 px wide).

OpenCV is imported inside the functions so ``wenart.gate`` imports without it.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

# Pixels of a region outline can be marked on either side of the boundary
# (views.geometry_edges marks the nearer pixel), so a region's reference
# edges are taken inside the region mask grown by this many pixels.
REGION_GROW_PX = 1
TEST_FACTOR = 0.5


def to_gray(rgb) -> np.ndarray:
    """uint8 H x W grey from an RGB uint8 image (a 2-D array is returned as uint8)."""
    import cv2
    a = np.asarray(rgb)
    if a.ndim == 2:
        return a.astype(np.uint8, copy=False)
    return cv2.cvtColor(np.ascontiguousarray(a[:, :, :3], dtype=np.uint8), cv2.COLOR_RGB2GRAY)


def blurred_gray(rgb, sigma: float = 1.5) -> np.ndarray:
    """uint8 H x W: grey, Gaussian-blurred with ``sigma`` (the input of every Canny of the gate)."""
    import cv2
    g = to_gray(rgb)
    if sigma and sigma > 0:
        g = cv2.GaussianBlur(g, (0, 0), float(sigma))
    return g


def canny_blurred(gray, low: float = 25, high: float = 75) -> np.ndarray:
    """bool H x W Canny edges (aperture 3, L2 gradient) of an already blurred grey image."""
    import cv2
    return cv2.Canny(gray, float(low), float(high), apertureSize=3, L2gradient=True) > 0


def canny(rgb, sigma: float = 1.5, low: float = 25, high: float = 75) -> np.ndarray:
    """bool H x W Canny edges: grey -> Gaussian blur (sigma) -> Canny(low, high, aperture 3, L2 gradient)."""
    return canny_blurred(blurred_gray(rgb, sigma), low, high)


NO_ANGLE = 255                 # edge_angles value of a pixel without an edge


def edge_angles(gray, low: float, high: float) -> np.ndarray:
    """uint8 H x W: gradient orientation (degrees mod 180, rounded) of each Canny edge pixel, else NO_ANGLE.

    ``gray`` is the blurred grey image (``blurred_gray``); the orientation is
    ``atan2(gy, gx)`` of the 3 x 3 Sobel gradient (the one Canny uses), so a
    vertical edge (a step along x) is 0 and a horizontal edge is 90.
    """
    import cv2
    out = np.full(gray.shape, NO_ANGLE, dtype=np.uint8)
    idx = np.flatnonzero(canny_blurred(gray, low, high))
    if idx.size:
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3).reshape(-1)[idx]
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3).reshape(-1)[idx]
        deg = np.mod(np.rint(np.degrees(np.arctan2(gy, gx))), 180.0)
        out.reshape(-1)[idx] = deg.astype(np.uint8)
    return out


def distance_to(mask) -> np.ndarray:
    """float32 H x W: Euclidean distance (px) to the nearest True pixel of ``mask`` (inf when there is none).

    ``cv2.distanceTransform`` measures the distance to the nearest ZERO pixel,
    so the mask is inverted first; DIST_MASK_PRECISE gives exact distances.
    """
    import cv2
    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return np.full(m.shape, np.inf, dtype=np.float32)
    return cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def grow(mask, radius_px: int) -> np.ndarray:
    """bool mask dilated with a (2r+1) square."""
    import cv2
    m = np.asarray(mask, dtype=bool)
    r = int(radius_px)
    if r <= 0:
        return m.copy()
    kernel = np.ones((2 * r + 1, 2 * r + 1), np.uint8)
    return cv2.dilate(m.astype(np.uint8), kernel) > 0


def reference_edges(geometry, ref_canny_dist, radius_px: float, valid=None) -> np.ndarray:
    """Geometry edges that Canny on the reference sees within ``radius_px`` (and inside ``valid``)."""
    ref = np.asarray(geometry, dtype=bool) & (np.asarray(ref_canny_dist) <= float(radius_px))
    if valid is not None:
        ref &= np.asarray(valid, dtype=bool)
    return ref


def recall(ref_edges, test_dist, radius_px: float, within=None) -> tuple[Optional[float], int]:
    """``(share of reference pixels with a test edge within radius_px, reference pixel count)``.

    The share is None when there is no reference pixel (inside ``within``).
    """
    ref = np.asarray(ref_edges, dtype=bool)
    if within is not None:
        ref = ref & np.asarray(within, dtype=bool)
    n = int(ref.sum())
    if n == 0:
        return None, 0
    hits = int((np.asarray(test_dist)[ref] <= float(radius_px)).sum())
    return hits / n, n


def edge_metrics(ref_edges, test_dist, regions, object_ids: Iterable[str], radius_px: float,
                 min_ref_px: int) -> tuple[dict, np.ndarray]:
    """``({"global", "regions", "skipped", "ref_px"}, missed)`` for one test image.

    ``regions`` is a ``views.Regions``; per object the reference pixels are
    those inside the object mask grown by ``REGION_GROW_PX`` (its outline,
    whichever side it was marked on). Objects with fewer than ``min_ref_px``
    reference pixels are skipped as ``no_reference_px``. ``missed`` is the
    bool map of reference pixels without a test edge (for the debug image).
    """
    ref = np.asarray(ref_edges, dtype=bool)
    dist = np.asarray(test_dist)
    value, _n = recall(ref, dist, radius_px)
    out = {"global": None if value is None else round(float(value), 4), "regions": {}, "skipped": {},
           "ref_px": {"global": int(ref.sum())}}
    for rid in object_ids:
        within = grow(regions.masks[rid], REGION_GROW_PX)
        val, n = recall(ref, dist, radius_px, within=within)
        out["ref_px"][rid] = n
        if n < int(min_ref_px) or val is None:
            out["skipped"][rid] = "no_reference_px"
            continue
        out["regions"][rid] = round(float(val), 4)
    missed = ref & (dist > float(radius_px))
    return out, missed
