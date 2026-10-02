"""Control images for the ControlNet (docs/milestone5.md §3.4; numpy / OpenCV, CPU-tested).

What: one control image per attempt (diffusers 0.40.0 takes a single
``control_image``; the Union model reads the control type from the image
itself). Three types, all uint8 RGB at the render size:

- ``depth`` (VideoX-Fun convention, near = bright; comfyui/annotator/nodes.py
  ImageToDepth): from the Cycles depth pass (exact, not estimated). Valid =
  depth_mm > 0; vmin = 2nd and vmax = 85th percentile of the valid depths;
  x = 1 - clip((d - vmin) / (vmax - vmin), 0, 1); pixels with no surface
  (background) are 0.
- ``canny``: ``cv2.Canny(gray(render), 100, 200)``, white edges on black
  (the VideoX-Fun Canny node defaults).
- ``geometry``: ``wenart.views.geometry_edges`` (the one definition of
  geometry edges, also the gate's reference edges) dilated to 2 px, white on
  black. These edges come from the index/depth/normal passes, so texture never
  adds an edge.

``write_control`` writes ``<cam>_control_<type>.png`` once per view at the
render size (rewritten only when the pixels change, so its sha256, part of
every attempt key, stays stable); each attempt pads or resizes it with the
same plan as the render (``wenart.polish.sizing``).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from wenart import views as V

CONTROL_TYPES = ("depth", "canny", "geometry")
DEPTH_P_LOW = 2.0
DEPTH_P_HIGH = 85.0
CANNY_LOW = 100
CANNY_HIGH = 200
GEOMETRY_WIDTH_PX = 2


def _rgb(grey: np.ndarray) -> np.ndarray:
    return np.repeat(np.asarray(grey, dtype=np.uint8)[:, :, None], 3, axis=2)


def depth_control(depth_mm) -> np.ndarray:
    """Near = bright depth image from the uint16 millimetre depth pass (0 where no surface)."""
    d = np.asarray(depth_mm).astype(np.float64)
    valid = d > 0
    out = np.zeros(d.shape, dtype=np.float64)
    if valid.any():
        vals = d[valid]
        vmin = float(np.percentile(vals, DEPTH_P_LOW))
        vmax = float(np.percentile(vals, DEPTH_P_HIGH))
        span = max(vmax - vmin, 1e-6)
        out[valid] = 1.0 - np.clip((vals - vmin) / span, 0.0, 1.0)
    return _rgb(np.rint(out * 255.0).astype(np.uint8))


def canny_control(rgb) -> np.ndarray:
    """``cv2.Canny(gray, 100, 200)`` of the render, white on black, RGB."""
    import cv2
    a = np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)[:, :, :3])
    gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    return _rgb(cv2.Canny(gray, CANNY_LOW, CANNY_HIGH))


def geometry_control(index, depth_mm, normal) -> np.ndarray:
    """``views.geometry_edges`` dilated to 2 px, white on black, RGB."""
    import cv2
    edges = V.geometry_edges(index, depth_mm, normal).astype(np.uint8)
    kernel = np.ones((GEOMETRY_WIDTH_PX, GEOMETRY_WIDTH_PX), dtype=np.uint8)
    wide = cv2.dilate(edges, kernel)
    return _rgb(np.where(wide > 0, 255, 0).astype(np.uint8))


def make_control(kind: str, rgb=None, index=None, depth_mm=None, normal=None) -> np.ndarray:
    """The control image of type ``kind`` (``depth``/``canny``/``geometry``) at the render size."""
    if kind == "depth":
        return depth_control(depth_mm)
    if kind == "canny":
        return canny_control(rgb)
    if kind == "geometry":
        return geometry_control(index, depth_mm, normal)
    raise ValueError(f"unknown control type {kind!r} (expected one of {', '.join(CONTROL_TYPES)})")


def control_filename(camera: str, kind: str) -> str:
    return f"{camera}_control_{kind}.png"


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_control(arr: np.ndarray, path) -> tuple[Path, str]:
    """Write the control PNG unless an identical one exists; returns (path, sha256 of the file)."""
    path = Path(path)
    if path.is_file():
        try:
            same = np.array_equal(V.read_rgb(path), arr)
        except (OSError, ValueError):
            same = False
        if same:
            return path, sha256_file(path)
    V.write_png_rgb(path, arr)
    return path, sha256_file(path)
