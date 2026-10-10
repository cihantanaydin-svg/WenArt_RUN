"""Contact sheets per type with keep / fix / remove marked (docs/milestone12.md §6.1 output).

What: ``contact_sheet(type, tiles, out)`` writes ``contact/<type>.jpg``: one tile per model (the front 3/4 view of its
audit sheet; before the render, the M10 thumbnail of ``results/library/thumbs``; else a grey tile), a coloured border
(keep green, fix amber, removed red, pending grey) and two label lines (the id and the status with its first
reason).

Why: the user approves the removals and the delete list from pictures, not from a table.

How: ``grid(n, cols)`` and ``label_lines`` are pure (tests); the drawing uses PIL and cv2 (Hershey font, ASCII).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

STATUS_RGB = {"keep": (40, 160, 60), "fix": (230, 160, 20), "removed": (210, 40, 40), "pending": (140, 140, 140)}


def grid(n: int, cols: int = 6) -> tuple[int, int]:
    """(columns, rows) of a sheet of ``n`` tiles."""
    cols = max(1, min(int(cols), max(1, n)))
    return cols, max(1, math.ceil(n / cols))


def status_key(status: str) -> str:
    s = str(status or "pending").rstrip("?")
    return s if s in STATUS_RGB else "pending"


def label_lines(iid: str, status: str, reasons: list, width_chars: int = 34) -> list[str]:
    from wenart.assets.audit.render import ascii_text
    first = ascii_text(reasons[0], width_chars) if reasons else ""
    return [ascii_text(iid, width_chars), ascii_text(f"{status}: {first}" if first else str(status), width_chars)]


def tile_image(source: Optional[Path], px: int, crop_first_view: bool):
    """The tile picture: the first view of an audit sheet (its top-left quarter below the header), a thumbnail, or
    grey."""
    from PIL import Image
    if source is None or not Path(source).is_file():
        return Image.new("RGB", (px, px), (200, 200, 200))
    img = Image.open(source).convert("RGB")
    if crop_first_view:
        w, h = img.size
        tile = w // 2
        band = h - 2 * tile
        img = img.crop((0, band, tile, band + tile))
    return img.resize((px, px), Image.LANCZOS)


def contact_sheet(ftype: str, tiles: list[dict], out: Path, px: int = 256, cols: int = 6, quality: int = 85) -> Path:
    """``tiles``: ``[{"id", "status", "reasons", "source": path or None, "crop": bool}]`` in the order to show."""
    import cv2
    import numpy as np
    from PIL import Image
    c, r = grid(len(tiles), cols)
    label_h, border, head = 40, 6, 34
    cell_w, cell_h = px + 2 * border, px + 2 * border + label_h
    sheet = np.full((head + r * cell_h, c * cell_w, 3), 255, dtype=np.uint8)
    counts: dict = {}
    for t in tiles:
        counts[status_key(t["status"])] = counts.get(status_key(t["status"]), 0) + 1
    summary = ", ".join(f"{k} {counts[k]}" for k in STATUS_RGB if counts.get(k))
    cv2.putText(sheet, f"{ftype}: {len(tiles)} model(s): {summary}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 0), 2, cv2.LINE_8)
    for i, t in enumerate(tiles):
        row, col = divmod(i, c)
        x0, y0 = col * cell_w, head + row * cell_h
        rgb = STATUS_RGB[status_key(t["status"])]
        sheet[y0:y0 + px + 2 * border, x0:x0 + cell_w] = rgb
        img = tile_image(t.get("source"), px, bool(t.get("crop")))
        sheet[y0 + border:y0 + border + px, x0 + border:x0 + border + px] = np.asarray(img, dtype=np.uint8)
        for n, line in enumerate(label_lines(t["id"], t["status"], t.get("reasons") or [])):
            cv2.putText(sheet, line, (x0 + 4, y0 + px + 2 * border + 15 + 17 * n), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                        (0, 0, 0), 1, cv2.LINE_8)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.ascontiguousarray(sheet)).save(out, format="JPEG", quality=int(quality))
    return out
