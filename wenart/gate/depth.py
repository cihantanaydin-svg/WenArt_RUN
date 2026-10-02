"""Monocular depth check of the change gate (docs/milestone5.md §4.2 ``depth``).

What: Depth Anything V2 Small gives a relative disparity for the Cycles
image and for the polished image (``models.py``). The test disparity is
fitted to the reference by least squares (scale + shift), refitted three
times on the 90 % of pixels with the smallest residuals, so a changed object
does not pull the fit. Error = mean |aligned test - reference| / (p98 - p2
of the reference) over valid pixels (no background, no window panes), for
the whole view and per object/structure region.

Why scale + shift: a monocular model gives disparity only up to an affine
transform, which differs between two images of the same room; after the
fit, the residual is what changed in the geometry the model sees.

numpy only (no model code here; the model wrapper lives in ``models.py``).
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

REFITS = 3           # trimmed refits after the first fit
KEEP = 0.90          # share of pixels kept in each refit (smallest residuals)
RANGE_LO, RANGE_HI = 2.0, 98.0   # percentiles of the reference for the error scale


def _lsq(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Closed-form least squares ``y ~ s * x + t`` (s = 0 when x is constant)."""
    mx, my = float(x.mean()), float(y.mean())
    dx = x - mx
    var = float(np.einsum("i,i->", dx, dx))          # sums of products without temporaries (and without BLAS)
    if var <= 0.0:
        return 0.0, my
    dx *= y - my
    s = float(dx.sum()) / var
    return s, my - s * mx


def fit_scale_shift(pred, ref, mask=None, refits: int = REFITS, keep: float = KEEP) -> tuple[float, float]:
    """``(s, t)`` so that ``s * pred + t`` fits ``ref`` on ``mask`` (one fit + ``refits`` trimmed refits).

    Each refit uses the pixels of ``mask`` whose residual of the previous
    fit is at most the ``keep`` quantile. ValueError when the mask is empty.
    """
    p = np.asarray(pred, dtype=np.float64)
    r = np.asarray(ref, dtype=np.float64)
    m = np.ones(p.shape, dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    m = m & np.isfinite(p) & np.isfinite(r)
    if not m.any():
        raise ValueError("fit_scale_shift: no valid pixels")
    return fit_1d(p[m], r[m], refits, keep)


def fit_1d(x: np.ndarray, y: np.ndarray, refits: int = REFITS, keep: float = KEEP) -> tuple[float, float]:
    """``fit_scale_shift`` on 1-D float64 samples (all finite, at least one)."""
    s, t = _lsq(x, y)
    for _ in range(int(refits)):
        res = np.abs(s * x + t - y)
        sel = res <= np.quantile(res, float(keep))
        if np.count_nonzero(sel) < 2:
            break
        s, t = _lsq(x[sel], y[sel])
    return s, t


def error_map(ref, test, valid) -> tuple[np.ndarray, dict]:
    """``(err, info)``: per-pixel |aligned test - ref| / (p98 - p2 of ref), NaN outside ``valid``.

    ``info`` = ``{"scale", "shift", "range"}`` of the fit.
    """
    r = np.asarray(ref, dtype=np.float64)
    t = np.asarray(test, dtype=np.float64)
    v = np.asarray(valid, dtype=bool) & np.isfinite(r) & np.isfinite(t)
    err = np.full(r.shape, np.nan, dtype=np.float32)
    if not v.any():
        return err, {"scale": None, "shift": None, "range": None}
    s, sh = fit_scale_shift(t, r, v)
    lo, hi = np.percentile(r[v], [RANGE_LO, RANGE_HI])
    rng = max(float(hi - lo), 1e-6)
    err[v] = (np.abs(s * t[v] + sh - r[v]) / rng).astype(np.float32)
    return err, {"scale": round(s, 6), "shift": round(sh, 6), "range": round(rng, 6)}


def depth_metrics(ref_disp, test_disp, valid, region_masks: dict, region_ids: Iterable[str],
                  min_frac: float) -> tuple[dict, np.ndarray]:
    """``({"global", "regions", "skipped", "fit"}, err)`` for one test image.

    Regions whose valid pixels are below ``min_frac`` of the image are
    skipped as ``too_small``.
    """
    err, info = error_map(ref_disp, test_disp, valid)
    finite = np.isfinite(err)
    total = err.size
    out: dict = {"global": None, "regions": {}, "skipped": {}, "fit": info}
    if finite.any():
        out["global"] = round(float(err[finite].mean()), 5)
    for rid in region_ids:
        sel = np.asarray(region_masks[rid], dtype=bool) & finite
        n = int(sel.sum())
        if n == 0 or n / total < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(err[sel].mean()), 5)
    return out, err


def reference_range(ref_valid) -> float:
    """``p98 - p2`` of the reference disparity (at least 1e-6): the error scale of ``error_map``."""
    lo, hi = np.percentile(ref_valid, [RANGE_LO, RANGE_HI])
    return max(float(hi - lo), 1e-6)


def depth_metrics_layout(ref_valid, test_valid, layout, min_frac: float,
                         ref_range: Optional[float] = None) -> tuple[dict, np.ndarray]:
    """``depth_metrics`` on the layout's valid pixels (``layout.Layout``; same numbers, no full-image pass).

    ``ref_valid``: float64 reference disparity gathered in layout order;
    ``test_valid``: the test disparity gathered the same way; ``ref_range``:
    ``reference_range(ref_valid)`` when the caller cached it (used only when
    every sample is finite). Returns the metrics and the float32 per-sample
    error (NaN where a sample is not finite; ``layout.scatter`` makes the map).
    """
    r = np.asarray(ref_valid, dtype=np.float64)
    t = np.asarray(test_valid, dtype=np.float64)
    fin = np.isfinite(r) & np.isfinite(t)
    every = bool(fin.all())
    err = np.full(r.shape, np.nan, dtype=np.float32)
    out: dict = {"global": None, "regions": {}, "skipped": {}, "fit": {"scale": None, "shift": None, "range": None}}
    if fin.any():
        x, y = (t, r) if every else (t[fin], r[fin])
        s, sh = fit_1d(x, y)
        rng = float(ref_range) if (every and ref_range is not None) else reference_range(y)
        e = (np.abs(s * x + sh - y) / rng).astype(np.float32)
        if every:
            err = e
        else:
            err[fin] = e
        out["fit"] = {"scale": round(s, 6), "shift": round(sh, 6), "range": round(rng, 6)}
        out["global"] = round(float(e.mean()), 5)
    total = layout.size
    for k, rid in enumerate(layout.ids):
        span = layout.span(k)
        seg = err[span]
        if every:
            n = int(seg.size)
        else:
            f = fin[span]
            n = int(np.count_nonzero(f))
            seg = seg[f]
        if n == 0 or n / total < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(seg.mean()), 5)
    return out, err

