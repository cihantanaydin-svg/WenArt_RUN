"""Real sizes per furniture and decor type: one table for the audit, the fit, F2/S4, the reader and the solver
(docs/milestone12.md §6.3 D23, contract §13.2; owner: track B).

What: the real-size table ``wenart/recognition/size_table.yaml`` (footprint ranges since Milestone 7; Milestone 12 adds
heights, a default product, standard product footprints and the library decor types) behind three frozen functions
and a few helpers.

Contract (frozen 10 Oct 2026); pure, deterministic:

- ``real_range(ftype: str) -> dict | None``: ``{"width": (min, max), "depth": (min, max), "height": (min, max) | None,
  "product": (w, d, h) | None}`` in metres (width along the front), None for a type without a size (``unknown``, a
  word that is no type). Decor types are found by their name (``cushion``) or their catalogue type
  (``decor_cushion``).
- ``product_size(ftype: str, drawn: tuple[float, float]) -> tuple[float, float]``: the nearest real product footprint
  to a drawn one, returned in the drawn orientation (a drawn 0.70 x 0.40 toilet becomes 0.65 x 0.38, not 0.38 x
  0.65), for misread fixed equipment (CLAUDE.md: "then the size of a real product of that type"). Run types
  (``run: true``: kitchen counters, wall cabinets) keep the drawn length inside the width range and snap the depth.
  A type without a size gives the drawn footprint back unchanged.
- ``fits(ftype: str, size, tolerance: float = 0.15) -> bool``: a footprint (w, d) or a box (w, d, h) inside the
  type's ranges with ``tolerance`` on top (``min / (1 + t) <= v <= max * (1 + t)``), the footprint in either
  orientation (as the readers), the height when the size has one and the type a height range.

Helpers (track B's; others may read them): ``types()``, ``decor_types()``, ``products(ftype)``,
``range_error(ftype, box, oriented=True)`` (how far a box is outside the ranges), ``scale_to_fit(ftype, box)`` (the
uniform scale nearest 1 that puts a box inside the ranges, or None when its proportions cannot fit) and
``oriented_fits(ftype, box, tolerance)`` (the footprint in the front convention, not either way).

Why: the reader, the layout checks, the solver, the fit and the library audit each had their own size numbers
(``size_table.yaml``, ``objaverse.yaml`` heights and library ranges, ``schemas.SIZE_OPTIONS``,
``catalog.PARAMETRIC_HEIGHTS``); the diagnosis (§1.6) found 114 library models with a wrong height that no table
caught. One table, read here, keeps them consistent.

How: the YAML is read once (``lru_cache``); ``reload()`` clears the cache (tests). Every function is pure and gives the
same answer for the same input; ties go to the first product of the list (the default product comes first).
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

_TABLE = Path(__file__).resolve().parents[1] / "recognition" / "size_table.yaml"
DECOR_PREFIX = "decor_"
TOLERANCE = 0.15


@lru_cache(maxsize=1)
def _data() -> dict:
    return yaml.safe_load(_TABLE.read_text(encoding="utf-8")) or {}


def _types() -> dict:
    return _data().get("types") or {}


def _decor() -> dict:
    return _data().get("decor") or {}


def reload() -> None:
    """Forget the cached table (after the YAML changed; tests)."""
    _data.cache_clear()


def table_tolerance() -> float:
    return float(_data().get("tolerance", TOLERANCE))


def types() -> tuple[str, ...]:
    """The furniture types with a size, in the table's order."""
    return tuple(_types())


def decor_types() -> tuple[str, ...]:
    """The decor types with a size (names without ``decor_``), in the table's order."""
    return tuple(_decor())


def _row(ftype: str) -> Optional[dict]:
    if not isinstance(ftype, str):
        return None
    row = _types().get(ftype)
    if row is None:
        name = ftype[len(DECOR_PREFIX):] if ftype.startswith(DECOR_PREFIX) else ftype
        row = _decor().get(name)
    return row if isinstance(row, dict) else None


def _pair(v) -> Optional[tuple[float, float]]:
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return (float(v[0]), float(v[1]))
    return None


def real_range(ftype: str) -> Optional[dict]:
    row = _row(ftype)
    if not row:
        return None
    product = row.get("product")
    return {"width": _pair(row["width"]), "depth": _pair(row["depth"]), "height": _pair(row.get("height")),
            "product": tuple(float(v) for v in product) if isinstance(product, (list, tuple)) and len(product) == 3
            else None}


def products(ftype: str) -> list[tuple[float, ...]]:
    """The standard real footprints (w, d) or boxes (w, d, h) of a type, the default product first; the default
    product alone when the table lists none; [] for a type without a size or a product."""
    row = _row(ftype)
    if not row:
        return []
    out = [tuple(float(v) for v in p) for p in (row.get("products") or []) if isinstance(p, (list, tuple))
           and len(p) in (2, 3)]
    r = real_range(ftype)
    if not out and r and r["product"]:
        out = [r["product"]]
    return out


def is_run(ftype: str) -> bool:
    row = _row(ftype)
    return bool(row and row.get("run"))


def _inside(v: float, lo: float, hi: float, tol: float) -> bool:
    return lo / (1.0 + tol) <= v <= hi * (1.0 + tol)


def fits(ftype: str, size, tolerance: float = 0.15) -> bool:
    r = real_range(ftype)
    if r is None:
        return False
    vals = [float(v) for v in size]
    a, b = vals[0], vals[1]
    (lo_w, hi_w), (lo_d, hi_d) = r["width"], r["depth"]
    foot = ((_inside(a, lo_w, hi_w, tolerance) and _inside(b, lo_d, hi_d, tolerance))
            or (_inside(b, lo_w, hi_w, tolerance) and _inside(a, lo_d, hi_d, tolerance)))
    if not foot:
        return False
    if len(vals) >= 3 and r["height"] is not None:
        return _inside(vals[2], *r["height"], tolerance)
    return True


def oriented_fits(ftype: str, box, tolerance: float = 0.15) -> bool:
    """``fits`` with the footprint in the front convention only (width along the front, as ``bbox_m``)."""
    r = real_range(ftype)
    if r is None:
        return False
    return range_error(ftype, box, oriented=True) <= tolerance + 1e-12


def _axis_error(v: float, lo: float, hi: float) -> float:
    """0 inside [lo, hi], else the relative excess (lo / v - 1 below, v / hi - 1 above)."""
    if v <= 0:
        return math.inf
    if v < lo:
        return lo / v - 1.0
    if v > hi:
        return v / hi - 1.0
    return 0.0


def range_error(ftype: str, box, oriented: bool = True) -> float:
    """How far a footprint (w, d) or box (w, d, h) is outside the type's ranges: the largest relative excess over
    the axes (0 inside, 0.2 = 20 % off). ``oriented``: width against the width range (``bbox_m`` order); else the
    better of both orientations. ``inf`` for a type without a size."""
    r = real_range(ftype)
    if r is None:
        return math.inf
    vals = [float(v) for v in box]
    h_err = _axis_error(vals[2], *r["height"]) if len(vals) >= 3 and r["height"] is not None else 0.0

    def foot(a, b):
        return max(_axis_error(a, *r["width"]), _axis_error(b, *r["depth"]))
    f = foot(vals[0], vals[1])
    if not oriented:
        f = min(f, foot(vals[1], vals[0]))
    return max(f, h_err)


def scale_to_fit(ftype: str, box, oriented: bool = True, slack: float = 0.0) -> Optional[float]:
    """The uniform scale nearest 1 that puts the box inside the type's ranges (each widened by ``slack``, e.g.
    0.05), or None when no single scale does (the proportions are outside the real ranges). ``oriented`` as in
    ``range_error`` (False: the better orientation)."""
    r = real_range(ftype)
    if r is None:
        return None
    vals = [float(v) for v in box]
    if any(v <= 0 for v in vals):
        return None

    def interval(order) -> Optional[tuple[float, float]]:
        ranges = [r["width"], r["depth"]] + ([r["height"]] if len(vals) >= 3 and r["height"] is not None else [])
        lo, hi = 0.0, math.inf
        for v, (a, b) in zip(order, ranges):
            lo = max(lo, a / (1.0 + slack) / v)
            hi = min(hi, b * (1.0 + slack) / v)
        return (lo, hi) if lo <= hi else None

    orders = [vals] if oriented else [vals, [vals[1], vals[0]] + vals[2:]]
    best = None
    for order in orders:
        iv = interval(order)
        if iv is None:
            continue
        s = min(max(1.0, iv[0]), iv[1])
        if best is None or abs(math.log(s)) < abs(math.log(best)) - 1e-12:
            best = s
    return best


def _log_distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return abs(math.log(a[0] / b[0])) + abs(math.log(a[1] / b[1]))


def product_size(ftype: str, drawn: tuple[float, float]) -> tuple[float, float]:
    r = real_range(ftype)
    d0, d1 = float(drawn[0]), float(drawn[1])
    if r is None or d0 <= 0 or d1 <= 0:
        return (d0, d1)
    if is_run(ftype):
        # the long side is the run: keep it (inside the width range), snap the other side to a product depth
        long_first = d0 >= d1
        length, depth = (d0, d1) if long_first else (d1, d0)
        length = min(max(length, r["width"][0]), r["width"][1])
        depths = sorted({p[1] for p in products(ftype)}) or [min(max(depth, r["depth"][0]), r["depth"][1])]
        depth = min(depths, key=lambda v: (abs(math.log(v / depth)), v))
        return (length, depth) if long_first else (depth, length)
    best = None
    for p in products(ftype):
        w, d = float(p[0]), float(p[1])
        for cand in ((w, d), (d, w)):          # the product in the drawn orientation, either way
            dist = _log_distance((d0, d1), cand)
            if best is None or dist < best[0] - 1e-12:
                best = (dist, cand)
    if best is None:
        w = min(max(d0, r["width"][0]), r["width"][1])
        d = min(max(d1, r["depth"][0]), r["depth"][1])
        return (w, d)
    return best[1]
