"""Feature check of the change gate (docs/milestone5.md §4.2 ``features``).

What: DINOv2-base patch tokens of the reference and the test image
(518 x 924 for a 16:9 view, no centre crop; ``models.py``); cosine
similarity per patch; per object the mean over the patches that lie at
least 50 % inside the object mask. Soft (a note, not a reason) until the
calibration shows it separates benign from negative controls.

Why: the other checks look at outlines, depth and masks; a polished object
can keep its outline and still turn into another object (a cabinet into a
fridge). Patch features see such a change of identity.

numpy + OpenCV (resize with INTER_AREA for the patch shares).
"""
from __future__ import annotations

from typing import Iterable

import numpy as np

PATCH_INSIDE_MIN = 0.5     # a patch counts for an object when >= 50 % of it lies inside the mask


def cosine_map(ref_tokens, test_tokens) -> np.ndarray:
    """float32 gh x gw cosine similarity of two gh x gw x C token grids."""
    a = np.asarray(ref_tokens, dtype=np.float64)
    b = np.asarray(test_tokens, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"token grids differ: {a.shape} vs {b.shape}")
    num = (a * b).sum(axis=-1)
    den = np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1)
    return np.where(den > 0, num / np.where(den > 0, den, 1.0), 0.0).astype(np.float32)


def patch_shares(mask, grid_hw: tuple[int, int]) -> np.ndarray:
    """float32 gh x gw: share of each patch covered by ``mask`` (area-weighted resize)."""
    import cv2
    gh, gw = int(grid_hw[0]), int(grid_hw[1])
    m = np.asarray(mask, dtype=np.float32)
    return cv2.resize(m, (gw, gh), interpolation=cv2.INTER_AREA)


def feature_metrics(ref_tokens, test_tokens, region_masks: dict, region_ids: Iterable[str], total_px: int,
                    min_frac: float, inside_min: float = PATCH_INSIDE_MIN) -> tuple[dict, np.ndarray]:
    """``({"global", "regions", "skipped"}, cosine map)``.

    Global = mean cosine over all patches. Regions below ``min_frac`` of the
    image, or without a patch at least ``inside_min`` inside, are skipped as
    ``too_small``.
    """
    cos = cosine_map(ref_tokens, test_tokens)
    grid = cos.shape
    out: dict = {"global": round(float(cos.mean()), 4) if cos.size else None, "regions": {}, "skipped": {}}
    for rid in region_ids:
        m = np.asarray(region_masks[rid], dtype=bool)
        n = int(m.sum())
        if n == 0 or n / float(total_px) < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        sel = patch_shares(m, grid) >= float(inside_min)
        if not sel.any():
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(cos[sel].mean()), 4)
    return out, cos
