"""Debug image of one gate comparison (docs/milestone5.md §4.4).

Layout (2 x 2 tiles, each W/3 wide, so 1280 x 720 for a 1920 x 1080 view):

    Cycles                       | polished
    missed reference edges (red) | depth error heat (black = 0,
    + added lines (blue) over    |   bright = 2 x the region limit)
    the darkened polished image  |

Regions that fail a check (reasons and notes) are outlined on the two lower
tiles with ``<id> <check> <value>``; a title bar gives the decision. Saved as
JPEG, the quality lowered (and finally the size) until the file is at most
300 KB, the size rule of every committed image.

OpenCV draws, Pillow writes; both imported inside the function.
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np

MAX_BYTES = 300_000
TILE_DIV = 3                  # tile width = W / 3
TITLE_PX = 28
RED = (230, 30, 30)
BLUE = (40, 110, 255)
FAIL = (255, 200, 0)
WHITE = (255, 255, 255)


def _resize(img, size, nearest: bool = False):
    import cv2
    return cv2.resize(img, size, interpolation=cv2.INTER_NEAREST if nearest else cv2.INTER_AREA)


def _label(tile, text: str, org=(6, 18), color=WHITE, scale: float = 0.5) -> None:
    import cv2
    cv2.putText(tile, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(tile, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def _heat(err, size, scale: float) -> np.ndarray:
    import cv2
    tw, th = size
    if err is None:
        tile = np.full((th, tw, 3), 40, dtype=np.uint8)
        _label(tile, "depth error not available", (6, th // 2))
        return tile
    e = np.nan_to_num(np.asarray(err, dtype=np.float32), nan=0.0)
    v = np.clip(e / max(scale, 1e-6), 0.0, 1.0)
    grey = (_resize(v, size) * 255.0).astype(np.uint8)
    bgr = cv2.applyColorMap(grey, cv2.COLORMAP_INFERNO)
    return np.ascontiguousarray(bgr[:, :, ::-1])


def failing_regions(result: dict) -> dict:
    """``{region id: "check value; check value"}`` of the region-level reasons and notes."""
    out: dict[str, list] = {}
    for item in list(result.get("reasons") or []) + list(result.get("notes") or []):
        region = item.get("region")
        if not region or region == "global":
            continue
        value = item.get("value")
        text = f"{item['check']} {value:.3g}" if isinstance(value, (int, float)) else item["check"]
        out.setdefault(region, []).append(text)
    return {k: "; ".join(v) for k, v in out.items()}


def write_debug_image(path, ref_rgb, test_rgb, missed, lines: list, depth_err, regions, result: dict,
                      depth_scale: float = 0.10, max_bytes: int = MAX_BYTES) -> Path:
    """Compose and save the debug JPEG; returns the path (parent folders are created)."""
    import cv2
    from PIL import Image

    ref = np.asarray(ref_rgb, dtype=np.uint8)[:, :, :3]
    test = np.asarray(test_rgb, dtype=np.uint8)[:, :, :3]
    h, w = ref.shape[:2]
    tw = max(64, w // TILE_DIV)
    th = max(36, int(round(h * tw / float(w))))
    size = (tw, th)

    overlay = (test.astype(np.float32) * 0.45).astype(np.uint8)
    if missed is not None and np.asarray(missed).any():
        grown = cv2.dilate(np.asarray(missed, dtype=np.uint8), np.ones((5, 5), np.uint8)) > 0
        overlay[grown] = RED
    for line in lines:
        x0, y0, x1, y1 = line["seg"]
        cv2.line(overlay, (x0, y0), (x1, y1), BLUE, max(2, w // 480), cv2.LINE_AA)
    tiles = [_resize(ref, size), _resize(test, size), _resize(overlay, size), _heat(depth_err, size, depth_scale)]
    tiles = [np.ascontiguousarray(t) for t in tiles]

    fails = failing_regions(result)
    if regions is not None:
        for rid, text in fails.items():
            mask = regions.masks.get(rid)
            if mask is None:
                continue
            small = _resize(np.asarray(mask, dtype=np.uint8), size, nearest=True)
            contours, _ = cv2.findContours(small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
            ys, xs = np.nonzero(small)
            org = (int(max(2, xs.min())), int(min(th - 4, max(12, ys.min() + 12))))
            for tile in tiles[2:]:
                cv2.drawContours(tile, contours, -1, FAIL, 1)
                _label(tile, f"{rid} {text}", org, FAIL, 0.4)
    bottom = (6, th - 8)
    _label(tiles[0], "Cycles", bottom)
    _label(tiles[1], "polished", bottom)
    _label(tiles[2], "missed edges (red), added lines (blue)", bottom)
    _label(tiles[3], f"depth error 0..{depth_scale:.2f}", bottom)

    grid = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])])
    bar = np.full((TITLE_PX, grid.shape[1], 3), 24, dtype=np.uint8)
    decision = result.get("decision", "?")
    n_reasons = len(result.get("reasons") or [])
    checks = sorted({r["check"] for r in result.get("reasons") or []})
    title = f"gate: {decision}"
    if n_reasons:
        title += f" ({n_reasons} reason{'s' if n_reasons > 1 else ''}: {', '.join(checks)})"
    _label(bar, title, (6, 19), (255, 120, 120) if decision == "reject" else (140, 255, 140), 0.55)
    img = Image.fromarray(np.vstack([bar, grid]))

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = b""
    for _attempt in range(4):
        for quality in (88, 80, 72, 64, 56, 48, 40):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= max_bytes:
                path.write_bytes(data)
                return path
        img = img.resize((max(64, img.width * 3 // 4), max(36, img.height * 3 // 4)), Image.LANCZOS)
    path.write_bytes(data)
    return path

