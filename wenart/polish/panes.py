"""Paste the Cycles window panes back into a polished image (docs/milestone5.md §3.2, last bullet).

What: after every attempt and before gating, the pixels inside each window
are replaced by the Cycles pixels: the window's index mask eroded by 6 px
(the frame border stays polished), with a 3 px feather outside the eroded
mask so no seam shows. The outside view is therefore always the Cycles HDRI;
the diffusion model never invents a garden, a street or a second building
behind the glass. ``panes_restored`` = the number of windows with pixels
left after the erosion.

The erosion is ``wenart.views.erode`` (the same as the gate's pane mask in
``views.regions``), so the gate excludes exactly the pasted core and checks
the feathered band.
"""
from __future__ import annotations

import numpy as np

from wenart import views as V

PANE_ERODE_PX = 6
PANE_FEATHER_PX = 3


def window_indices(table: dict) -> list[int]:
    """Pass indices of the windows in an ``index_table``."""
    return sorted(int(k) for k, e in table.items() if e.get("kind") == "window")


def pane_alpha(index, table: dict, erode_px: int = PANE_ERODE_PX,
               feather_px: int = PANE_FEATHER_PX) -> tuple[np.ndarray, int]:
    """``(alpha float32 H x W in 0..1, n windows restored)``: 1 on the eroded panes, ramping to 0 over ``feather_px``.

    The ramp is ``1 - d / (feather_px + 1)`` for the exact Euclidean distance d
    (px) to the eroded panes, kept inside the windows' own index masks.
    """
    idx = np.asarray(index)
    windows = np.zeros(idx.shape, dtype=bool)
    core = np.zeros(idx.shape, dtype=bool)
    n = 0
    present = set(np.unique(idx).tolist())
    for value in window_indices(table):
        if value not in present:
            continue
        mask = idx == value
        windows |= mask
        eroded = V.erode(mask, erode_px)
        if eroded.any():
            core |= eroded
            n += 1
    alpha = core.astype(np.float32)
    if n and feather_px > 0:
        import cv2
        dist = cv2.distanceTransform(np.where(core, 0, 1).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        ramp = np.clip(1.0 - dist / float(feather_px + 1), 0.0, 1.0).astype(np.float32)
        alpha = np.where(windows, ramp, 0.0).astype(np.float32)
        alpha[core] = 1.0
    return alpha, n


def restore_panes(polished, cycles, index, table: dict, erode_px: int = PANE_ERODE_PX,
                  feather_px: int = PANE_FEATHER_PX) -> tuple[np.ndarray, int]:
    """``(image, n)``: ``polished`` with the Cycles pixels pasted into every window pane (uint8, render size)."""
    p = np.asarray(polished, dtype=np.uint8)
    c = np.asarray(cycles, dtype=np.uint8)
    if p.shape != c.shape or p.shape[:2] != np.asarray(index).shape:
        raise ValueError(f"shape mismatch: polished {p.shape}, cycles {c.shape}, index {np.asarray(index).shape}")
    alpha, n = pane_alpha(index, table, erode_px, feather_px)
    if n == 0:
        return p.copy(), 0
    a = alpha[:, :, None]
    out = np.rint(c.astype(np.float32) * a + p.astype(np.float32) * (1.0 - a))
    return np.clip(out, 0, 255).astype(np.uint8), n
