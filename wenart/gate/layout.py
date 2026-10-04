"""Valid pixels of a view grouped by region, built once per reference (docs/milestone5.md §4).

What: ``Layout`` lists the flat indices of the valid pixels of a view (not
background, not a window pane), sorted by region (pixels of no region
first, then the regions in ``ids`` order; row-major inside each group).
The colour and depth checks gather a test image's valid pixels once in this
order and take every region's sum, mean or count from a contiguous slice.

Why: a comparison used to make one or more full-image passes per region
(``mask & valid``, boolean gathers, bincounts over the whole image) and
float64 copies of whole images; with 15 objects and 3 structure regions at
1920 x 1080 that was most of the gate's CPU time (pod run 0b: the colour and
depth checks took 6-24 s per comparison on a contended pod). The slices give
the same pixels in the same order, so the region values are the same
(``tests/test_gate.py`` compares them with the mask-based functions).

numpy (and OpenCV for ``planes``) only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class Layout:
    """``order``: flat indices of the valid pixels, region by region; ``offsets``: group bounds.

    Group 0 holds the valid pixels of no region, group ``k + 1`` region
    ``ids[k]``: ``order[offsets[g]:offsets[g + 1]]``. ``shape`` = (H, W).
    """
    ids: list
    order: np.ndarray
    offsets: np.ndarray
    shape: tuple

    @classmethod
    def build(cls, region_masks: dict, region_ids: Iterable[str], valid) -> "Layout":
        """The layout of ``region_masks`` (disjoint bool H x W) restricted to ``valid``.

        On an overlap the later region wins (as ``colour.region_labels``).
        """
        ids = list(region_ids)
        v = np.asarray(valid, dtype=bool)
        group = np.zeros(v.shape, dtype=np.int16 if len(ids) < 32000 else np.int32)
        for k, rid in enumerate(ids):
            group[np.asarray(region_masks[rid], dtype=bool)] = k + 1
        vidx = np.flatnonzero(v)
        key = group.reshape(-1)[vidx]
        order = vidx[np.argsort(key, kind="stable")]         # radix sort for int16 keys
        counts = np.bincount(key, minlength=len(ids) + 1)
        offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)
        return cls(ids=ids, order=order, offsets=offsets, shape=tuple(v.shape))

    @property
    def size(self) -> int:
        """H x W."""
        return int(self.shape[0] * self.shape[1])

    @property
    def n_valid(self) -> int:
        return int(self.order.size)

    def span(self, k: int) -> slice:
        """The slice of region ``ids[k]`` in the gathered arrays."""
        return slice(int(self.offsets[k + 1]), int(self.offsets[k + 2]))

    def counts(self) -> np.ndarray:
        """Valid pixels per region (``ids`` order)."""
        return np.diff(self.offsets)[1:]

    def gather(self, image) -> np.ndarray:
        """The valid pixels of an H x W image (1-D, in layout order)."""
        return np.asarray(image).reshape(-1)[self.order]

    def planes(self, rgb) -> np.ndarray:
        """uint8 3 x N: the valid pixels of an H x W x 3 image, one row per channel (layout order)."""
        import cv2
        return np.stack([p.reshape(-1)[self.order] for p in cv2.split(np.ascontiguousarray(rgb[:, :, :3]))])

    def scatter(self, values, fill=np.nan, dtype=np.float32) -> np.ndarray:
        """H x W map with ``values`` (layout order) at the valid pixels and ``fill`` elsewhere."""
        out = np.full(self.size, fill, dtype=dtype)
        out[self.order] = values
        return out.reshape(self.shape)
