"""Real sizes per furniture type: one table for the audit, the fit, F2/S4, the reader and the solver
(docs/milestone12.md §6.3, contract §13.2; owner: track B).

Contract (frozen 10 Oct 2026); pure:

- ``real_range(ftype: str) -> dict | None``: ``{"width": (min, max), "depth": (min, max), "height": (min, max) | None,
  "product": (w, d, h) | None}`` in metres (width along the front), None for a type without a size.
- ``product_size(ftype: str, drawn: tuple[float, float]) -> tuple[float, float]``: the nearest real product footprint
  (width, depth) to a drawn one (either orientation kept), for misread fixed equipment.
- ``fits(ftype: str, size: tuple[float, float], tolerance: float = 0.15) -> bool``.

Stub (lead): reads today's ``wenart/recognition/size_table.yaml`` (footprints only).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

_TABLE = Path(__file__).resolve().parents[1] / "recognition" / "size_table.yaml"


@lru_cache(maxsize=1)
def _types() -> dict:
    return (yaml.safe_load(_TABLE.read_text(encoding="utf-8")) or {}).get("types") or {}


def real_range(ftype: str) -> Optional[dict]:
    row = _types().get(ftype)
    if not row:
        return None
    return {"width": tuple(row["width"]), "depth": tuple(row["depth"]), "height": None, "product": None}


def fits(ftype: str, size: tuple[float, float], tolerance: float = 0.15) -> bool:
    r = real_range(ftype)
    if r is None:
        return False
    a, b = sorted(size, reverse=True)
    lo_w, hi_w = r["width"]
    lo_d, hi_d = r["depth"]

    def inside(x, lo, hi):
        return lo / (1 + tolerance) <= x <= hi * (1 + tolerance)
    return (inside(a, lo_w, hi_w) and inside(b, lo_d, hi_d)) or (inside(b, lo_w, hi_w) and inside(a, lo_d, hi_d))


def product_size(ftype: str, drawn: tuple[float, float]) -> tuple[float, float]:
    r = real_range(ftype)
    if r is None:
        return tuple(drawn)
    w = min(max(drawn[0], r["width"][0]), r["width"][1])
    d = min(max(drawn[1], r["depth"][0]), r["depth"][1])
    return (w, d)
