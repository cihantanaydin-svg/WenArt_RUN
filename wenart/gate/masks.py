"""Object-mask check of the change gate (docs/milestone5.md §4.2 ``masks``).

What: SAM 2.1 segments every object from its index box on the Cycles image
and on the polished image (``models.py``: one image encoding per image, all
boxes in one batch, ``multimask_output=False``); the metric per object is
IoU(SAM mask on the reference, SAM mask on the test). Objects where SAM
does not reproduce the object on the reference (IoU(SAM ref, index mask) <
``sam_reliable_min``) are skipped as ``sam_unreliable``: comparing SAM with
itself cancels its errors on thin legs, but only where SAM finds the object
at all.

numpy only.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np


def iou(a, b) -> Optional[float]:
    """Intersection over union of two bool masks (None when both are empty)."""
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    union = int((a | b).sum())
    if union == 0:
        return None
    return int((a & b).sum()) / union


def mask_box(mask) -> Optional[list[int]]:
    """``[x0, y0, x1, y1]`` (x1/y1 exclusive) of a bool mask, None when empty."""
    m = np.asarray(mask, dtype=bool)
    rows = np.flatnonzero(m.any(axis=1))
    if rows.size == 0:
        return None
    cols = np.flatnonzero(m.any(axis=0))
    return [int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1]


def sam_objects(region_masks: dict, object_ids: Iterable[str], total_px: int, min_frac: float) -> tuple[dict, dict]:
    """``(boxes, skipped)``: the SAM box of every object region at least ``min_frac`` of the image."""
    boxes, skipped = {}, {}
    for rid in object_ids:
        m = np.asarray(region_masks[rid], dtype=bool)
        n = int(m.sum())
        if n == 0 or n / float(total_px) < float(min_frac):
            skipped[rid] = "too_small"
            continue
        boxes[rid] = mask_box(m)
    return boxes, skipped


def reliability(ref_sam: dict, region_masks: dict) -> dict:
    """``{object id: IoU(SAM on the reference, index mask)}``."""
    out = {}
    for rid, m in ref_sam.items():
        v = iou(m, region_masks[rid])
        out[rid] = None if v is None else round(float(v), 4)
    return out


def mask_metrics(ref_sam: dict, test_sam: dict, reliable: dict, skipped_small: dict, reliable_min: float) -> dict:
    """``{"global": None, "regions": {id: IoU}, "skipped", "reliability"}``.

    ``ref_sam``/``test_sam``: ``{object id: bool mask}`` for the same boxes;
    ``reliable``: ``reliability(...)``; ``skipped_small`` the too-small
    objects of ``sam_objects``. Global is None (the check is per object).
    """
    out: dict = {"global": None, "regions": {}, "skipped": dict(skipped_small), "reliability": dict(reliable)}
    for rid, ref in ref_sam.items():
        rel = reliable.get(rid)
        if rel is None or rel < float(reliable_min):
            out["skipped"][rid] = "sam_unreliable"
            continue
        if rid not in test_sam:
            out["skipped"][rid] = "no_reference_px"
            continue
        v = iou(ref, test_sam[rid])
        out["regions"][rid] = 0.0 if v is None else round(float(v), 4)
    return out
