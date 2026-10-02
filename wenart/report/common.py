"""Small helpers of the Milestone 5 reports (docs/milestone5.md §7): JSON input, JPEG size limit, markdown.

What:
- ``read_json(path, warnings)``: a manifest or None when it is missing; a
  broken file is reported in ``warnings`` and read as missing (the report
  must still be written, saying what was not available).
- ``save_jpeg_under(image, path, max_bytes)``: JPEG <= ``max_bytes`` (300 KB
  by default, the repo's limit for committed images): the quality steps down
  first, then the image shrinks in 0.85 steps; returns what it did.
- markdown helpers in the style of ``wenart/furniture/fit.py`` and
  ``wenart/ingest/pipeline.py`` (pipe tables, ``-`` for empty cells).
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Optional

MAX_IMAGE_BYTES = 300_000
JPEG_QUALITIES = (88, 80, 72, 64, 56, 48, 40, 32, 25)
SHRINK_STEP = 0.85


def read_json(path, warnings: Optional[list] = None) -> Optional[Any]:
    """The JSON at ``path``, or None when it does not exist or cannot be parsed (then a warning is added)."""
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        if warnings is not None:
            warnings.append(f"{path.name}: unreadable ({type(exc).__name__}: {exc}); treated as missing")
        return None


def write_json(path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def sha256_file(path) -> Optional[str]:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def rel(path, start) -> str:
    """POSIX path of ``path`` relative to the folder ``start`` (§1.1: paths in M5 JSON are relative to the JSON)."""
    return Path(os.path.relpath(Path(path).resolve(), Path(start).resolve())).as_posix()


def save_jpeg_under(image, path, max_bytes: int = MAX_IMAGE_BYTES, qualities: Iterable[int] = JPEG_QUALITIES,
                    min_side: int = 64) -> dict:
    """Write ``image`` (PIL image or uint8 HxWx3 array) as a JPEG of at most ``max_bytes``.

    Quality steps down through ``qualities``; if the lowest still does not
    fit, the image shrinks by ``SHRINK_STEP`` and the steps repeat. Returns
    ``{"bytes", "quality", "scale", "size": [W, H]}``. Raises ValueError only
    when even a ``min_side`` image does not fit.
    """
    from PIL import Image

    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    image = image.convert("RGB")
    qualities = tuple(qualities)
    W, H = image.size
    scale = 1.0
    while True:
        img = image if scale == 1.0 else image.resize((max(1, round(W * scale)), max(1, round(H * scale))),
                                                      Image.Resampling.LANCZOS)
        for quality in qualities:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            if buf.tell() <= max_bytes:
                path = Path(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(buf.getvalue())
                return {"bytes": buf.tell(), "quality": quality, "scale": round(scale, 4), "size": list(img.size)}
        if min(img.size) <= min_side:
            raise ValueError(f"{path}: cannot fit a JPEG under {max_bytes} bytes")
        scale *= SHRINK_STEP


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

def cell(value: Any, digits: int = 2) -> str:
    """One table cell: ``-`` for None/empty, numbers rounded, lists joined, pipes escaped."""
    if value is None or value == "" or value == [] or value == {}:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        if math.isnan(value):
            return "-"
        return f"{value:.{digits}f}"
    if isinstance(value, (list, tuple)):
        return ", ".join(cell(v, digits) for v in value) or "-"
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text


def table(header: list[str], rows: list[list[Any]]) -> list[str]:
    """Markdown pipe table lines."""
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for row in rows:
        lines.append("| " + " | ".join(cell(v) for v in row) + " |")
    return lines


def bullets(items: Iterable[str], empty: str = "None.") -> list[str]:
    items = [f"- {i}" for i in items]
    return items or [empty]


def pct(num: Optional[float]) -> str:
    return "-" if num is None else f"{100.0 * num:.0f} %"


def seconds_text(value: Optional[float]) -> str:
    if value is None:
        return "-"
    value = float(value)
    if value >= 120:
        return f"{value / 60.0:.1f} min"
    return f"{value:.1f} s"
