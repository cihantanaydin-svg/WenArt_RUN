"""Model input size of a polish attempt and the way back to the render size (docs/milestone5.md §3.3).

What: Z-Image needs height and width divisible by 16 (``vae_scale_factor *
2``; the pipeline raises otherwise) and the renders are 1920x1080 (1080 % 16 =
8). Two ways to get there, chosen per attempt by ``size``:

- ``native``: reflect-pad to the next multiple of 16, split evenly between
  the two sides (1920x1080 -> 1920x1088, 4 px top and bottom), and crop the
  same pixels away afterwards. No resampling, so every rendered pixel keeps
  its place.
- ``WxH`` (multiples of 16, e.g. ``1536x864``): Lanczos resize to that size
  and Lanczos back to the render size afterwards.

The control image goes through the same plan as the render, and the gate
always compares at the render size (never at the model size).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MULTIPLE = 16


@dataclass(frozen=True)
class SizePlan:
    """How one attempt maps the render to the model input and back.

    ``mode`` "native" or "resize"; ``render`` and ``model`` are (W, H);
    ``pad`` is (left, top, right, bottom) in pixels (native only, else zeros).
    """
    mode: str
    render: tuple[int, int]
    model: tuple[int, int]
    pad: tuple[int, int, int, int] = (0, 0, 0, 0)

    def to_dict(self) -> dict:
        return {"mode": self.mode, "render": list(self.render), "model": list(self.model), "pad": list(self.pad)}


def parse_size(size) -> tuple[int, int] | None:
    """``"native"`` -> None; ``"1536x864"`` -> (1536, 864); anything else (or not multiples of 16) -> ValueError."""
    if size is None or str(size).strip().lower() == "native":
        return None
    text = str(size).strip().lower()
    parts = text.split("x")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        raise ValueError(f"size must be 'native' or 'WxH', got {size!r}")
    w, h = int(parts[0]), int(parts[1])
    if w <= 0 or h <= 0 or w % MULTIPLE or h % MULTIPLE:
        raise ValueError(f"size {size!r}: width and height must be positive multiples of {MULTIPLE}")
    return w, h


def _split(total: int) -> tuple[int, int]:
    first = total // 2
    return first, total - first


def plan_size(size, render_wh) -> SizePlan:
    """The size plan of one attempt for a render of ``render_wh`` = (W, H)."""
    W, H = (int(v) for v in render_wh)
    target = parse_size(size)
    if target is None:
        left, right = _split((-W) % MULTIPLE)
        top, bottom = _split((-H) % MULTIPLE)
        if max(left, right) >= W or max(top, bottom) >= H:
            raise ValueError(f"render {W}x{H} is too small to reflect-pad to a multiple of {MULTIPLE}")
        return SizePlan("native", (W, H), (W + left + right, H + top + bottom), (left, top, right, bottom))
    return SizePlan("resize", (W, H), target)


def _lanczos(arr: np.ndarray, wh: tuple[int, int]) -> np.ndarray:
    from PIL import Image
    a = np.asarray(arr)
    if a.dtype != np.uint8:
        raise ValueError(f"uint8 image expected, got {a.dtype}")
    img = Image.fromarray(np.ascontiguousarray(a))
    return np.asarray(img.resize((int(wh[0]), int(wh[1])), Image.LANCZOS), dtype=np.uint8)


def _check(arr: np.ndarray, wh: tuple[int, int], what: str) -> np.ndarray:
    a = np.asarray(arr)
    if a.shape[:2] != (wh[1], wh[0]):
        raise ValueError(f"{what}: expected {wh[0]}x{wh[1]}, got {a.shape[1]}x{a.shape[0]}")
    return a


def to_model(arr, plan: SizePlan) -> np.ndarray:
    """Render-size uint8 image (H x W or H x W x C) -> model size (reflect pad or Lanczos)."""
    a = _check(arr, plan.render, "to_model")
    if plan.mode == "native":
        left, top, right, bottom = plan.pad
        widths = [(top, bottom), (left, right)] + [(0, 0)] * (a.ndim - 2)
        return np.pad(a, widths, mode="reflect")
    return _lanczos(a, plan.model)


def from_model(arr, plan: SizePlan) -> np.ndarray:
    """Model-size uint8 image -> render size (crop the padding or Lanczos back)."""
    a = _check(arr, plan.model, "from_model")
    if plan.mode == "native":
        left, top, right, bottom = plan.pad
        H, W = a.shape[:2]
        return np.ascontiguousarray(a[top:H - bottom, left:W - right])
    return _lanczos(a, plan.render)
