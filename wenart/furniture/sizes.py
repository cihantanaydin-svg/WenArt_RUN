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

Milestone 13 (docs/milestone13.md §3.0 K1, §5.3, §13.2; track T1; user OK D5 of 12 Oct 2026): the product grid.

- What: ``PRODUCT_GRID`` = ``{type: [{"w", "d", "h", "label"}]}`` from the YAML's ``grid:`` block (5 cm size classes of
  real products with their sources: ABO titles and boxes, Poly Haven boxes, the layout sizes, the drawings), falling
  back to the type's ``products`` rows (with the default product's height) where the block has none;
  ``snap_size(ftype, footprint, height=None) -> {footprint, height, product, changed, reason}``: the nearest grid row
  of a drawn footprint that lies outside the type's width / depth ranges by more than ``SNAP_TOLERANCE`` (5 %;
  ``changed`` false inside: a drawn size inside the ranges is never changed); a height outside the height range takes
  the row's height; a footprint that fits the ranges turned by 90 degrees (or is far closer to them turned,
  ``ORIENTATION_RATIO``) is an orientation question for the solver, not a size snap.
- Why: the diagnosis (§1.3) found that 21-33 of real04's 43 unbuilt pieces had doubtful drawn sizes (a bed block with
  its nightstands 2.55 x 2.00, split-artefact chairs 0.71 x 0.45) that no library product could match; CLAUDE.md
  allows "change its size to a real product size" (``adjusted_by_ai`` with the reason, ``drawn_footprint`` kept). The
  fit (``wenart.furniture.fit.fit_building``) snaps before it fits; the snap is off with ``furnished_rooms: keep`` or
  ``furnished_rooms_keep_size``.
- How: nearest = the smallest largest-axis change in log space (``max(|ln(w / w_row)|, |ln(d / d_row)|)``), ties by
  the sum of both, then the row order; the drawn orientation is kept (the reader decided the front; no swap); a square
  drawn footprint (within ``SQUARE_EPS``) takes square rows only (a round symbol is a round product); a run type keeps
  its drawn length (clamped to the width range) and snaps the depth to the nearest row depth, as ``product_size``,
  and so does a long piece (``KEEP_LENGTH_TYPES``: consoles, sideboards, shelves, benches) whose length is inside
  its range (a 1.80 x 0.25 m hall console stays 1.80 m long).
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Optional

_TABLE = Path(__file__).resolve().parents[1] / "recognition" / "size_table.yaml"
# Blender's own Python has no PyYAML (the scene checks S4 read this table inside Blender): a JSON copy of the YAML,
# kept equal by tests/test_library_sizes.py (``write_json_mirror`` rewrites it after the YAML changed).
_TABLE_JSON = _TABLE.with_suffix(".json")
DECOR_PREFIX = "decor_"
TOLERANCE = 0.15


def _load_yaml() -> dict:
    import yaml
    return yaml.safe_load(_TABLE.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=1)
def _data() -> dict:
    try:
        return _load_yaml()
    except ImportError:
        import json
        return json.loads(_TABLE_JSON.read_text(encoding="utf-8"))


def write_json_mirror() -> Path:
    """Rewrite ``size_table.json`` from the YAML (run after editing the YAML)."""
    import json
    _TABLE_JSON.write_text(json.dumps(_load_yaml(), indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                           encoding="utf-8")
    return _TABLE_JSON


def _types() -> dict:
    return _data().get("types") or {}


def _decor() -> dict:
    return _data().get("decor") or {}


def reload() -> None:
    """Forget the cached table (after the YAML changed; tests) and rebuild ``PRODUCT_GRID``."""
    _data.cache_clear()
    PRODUCT_GRID.clear()
    PRODUCT_GRID.update(_build_grid())


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


# --------------------------------------------------------------------------
# Milestone 13 (track T1): the product grid and the size snap
# --------------------------------------------------------------------------

SQUARE_EPS = 0.03                # |ln(w / d)| below this: a square (or round) drawn footprint
# Turned by 90 degrees the drawn box is inside the ranges (within SNAP_TOLERANCE) or four times closer to them than as
# drawn: a front error for the solver (a 0.40 x 2.17 m shelf unit), not a size to snap. The YATAK block 2.55 x 2.00
# (27 % over the bed width as drawn, 13 % over the depth turned) is still a size snap.
ORIENTATION_RATIO = 0.25
# A drawn side this far outside its range (relative) is a drawing tolerance, not a misread: no snap. One 5 % size step
# of the fit's rank (wenart.furniture.fit.SIZE_BUCKET): a 1.80 x 0.25 m shelf unit 2 % shallower than the range stays
# a 1.80 m unit; the 0.71 x 0.45 m split-artefact chair (9 % over) and the 2.55 m YATAK block (27 %) are snapped.
SNAP_TOLERANCE = 0.05
# Long pieces whose drawn length is a real length when it lies inside the width range: only a misread depth is snapped
# (to the nearest product depth), as for a run; a 1.80 x 0.25 m hall console stays 1.80 m long, it never becomes the
# 1.20 m default product. Not for chairs, tables, sofas or beds: those take a whole product (the task's 0.71 x 0.45
# split-artefact chair becomes a 0.50 x 0.50 one).
KEEP_LENGTH_TYPES: tuple[str, ...] = ("console_table", "sideboard", "tv_unit", "bookshelf", "bench", "shoe_cabinet",
                                      "dresser", "display_cabinet", "tall_cabinet", "desk", "kitchen_island")
GRID_KEY = "grid"


def _grid_rows(ftype: str) -> list[dict]:
    """The grid rows of a type: the YAML ``grid`` block, else its ``products`` with the default product's height."""
    block = (_data().get(GRID_KEY) or {}).get(ftype)
    rows: list[dict] = []
    if isinstance(block, list):
        for row in block:
            if isinstance(row, (list, tuple)) and len(row) >= 3:
                rows.append({"w": float(row[0]), "d": float(row[1]), "h": float(row[2]),
                             "label": str(row[3]) if len(row) > 3 else ""})
        return rows
    r = real_range(ftype)
    default_h = r["product"][2] if r and r["product"] else None
    for i, p in enumerate(products(ftype)):
        h = float(p[2]) if len(p) > 2 else default_h
        rows.append({"w": float(p[0]), "d": float(p[1]), "h": h, "label": "default product" if i == 0 else "product"})
    return rows


def _build_grid() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for t in types():
        rows = _grid_rows(t)
        if rows:
            out[t] = rows
    return out


def grid_sources(ftype: str) -> list[str]:
    """The labels (size class and sources) of a type's grid rows, for reports."""
    return [row["label"] for row in PRODUCT_GRID.get(ftype, [])]


def _fmt(v: Optional[float]) -> str:
    return "-" if v is None else f"{v:.2f}"


def _row_text(row: dict) -> str:
    return (f"{_fmt(row['w'])} x {_fmt(row['d'])} x {_fmt(row.get('h'))} m"
            + (f" ({row['label'].split(':')[0].strip()})" if row.get("label") else ""))


def snap_size(ftype: str, footprint, height: Optional[float] = None) -> dict:
    """The nearest real product of ``ftype`` for a drawn ``footprint`` (w, d) outside the type's ranges (pure;
    docs/milestone13.md §13.2). Returns ``{"footprint": (w, d), "height": h | None, "product": text | None,
    "changed": bool, "reason": text}``: ``changed`` is False (and the footprint comes back as given) when the footprint
    lies inside the width and depth ranges in the drawn orientation, or the type has no size row, or a side is not
    positive. A ``height`` outside the height range (when given) takes the row's height and counts as a change too."""
    r = real_range(ftype)
    try:
        w, d = float(footprint[0]), float(footprint[1])
    except (TypeError, ValueError, IndexError):
        return {"footprint": tuple(footprint) if isinstance(footprint, (list, tuple)) else footprint, "height": height,
                "product": None, "changed": False, "reason": "no footprint"}
    h = float(height) if isinstance(height, (int, float)) and not isinstance(height, bool) else None
    unchanged = {"footprint": (w, d), "height": h, "product": None, "changed": False}
    if r is None:
        return dict(unchanged, reason=f"no size row for type {ftype!r}")
    if w <= 0 or d <= 0:
        return dict(unchanged, reason="footprint side not positive")
    rows = PRODUCT_GRID.get(ftype) or _grid_rows(ftype)
    (lo_w, hi_w), (lo_d, hi_d) = r["width"], r["depth"]
    err_w, err_d = _axis_error(w, lo_w, hi_w), _axis_error(d, lo_d, hi_d)
    h_err = _axis_error(h, *r["height"]) if h is not None and r["height"] is not None else 0.0
    if err_w <= SNAP_TOLERANCE + 1e-9 and err_d <= SNAP_TOLERANCE + 1e-9:
        if h_err > SNAP_TOLERANCE + 1e-9 and rows:
            nearest = min(rows, key=lambda row: (abs(math.log(row["w"] / w)) + abs(math.log(row["d"] / d))))
            new_h = nearest["h"] if nearest.get("h") is not None else h
            return {"footprint": (w, d), "height": new_h, "product": _row_text(nearest), "changed": new_h != h,
                    "reason": f"height {h:.2f} m is {h_err * 100:.0f} % outside the {ftype} range "
                              f"{r['height'][0]:g}-{r['height'][1]:g} m: the product height {new_h:.2f} m"}
        return dict(unchanged, reason="inside the product range" + (
            f" (within the {SNAP_TOLERANCE * 100:.0f} % drawing tolerance)" if max(err_w, err_d) > 1e-9 else ""))
    outside = []
    if err_w > SNAP_TOLERANCE + 1e-9:
        outside.append(f"width {w:.2f} m is {err_w * 100:.0f} % outside {lo_w:g}-{hi_w:g} m")
    if err_d > SNAP_TOLERANCE + 1e-9:
        outside.append(f"depth {d:.2f} m is {err_d * 100:.0f} % outside {lo_d:g}-{hi_d:g} m")
    err_turned = max(_axis_error(d, lo_w, hi_w), _axis_error(w, lo_d, hi_d))
    if not is_run(ftype) and (err_turned <= SNAP_TOLERANCE + 1e-9
                              or err_turned <= max(err_w, err_d) * ORIENTATION_RATIO):
        # turned by 90 degrees the drawn box is a product of the type (or far closer to one): the front (the reader's,
        # the solver's F2) is the question, not the size; a snap in the drawn orientation would make a wrong product
        # (a 0.40 x 2.17 m bookshelf read with its front along the long side is a 2.17 m shelf unit, not a 1.00 m one)
        return dict(unchanged, reason="; ".join(outside) + (
            "; fits the ranges turned by 90 degrees" if err_turned <= SNAP_TOLERANCE + 1e-9 else
            f"; turned by 90 degrees it is only {err_turned * 100:.0f} % outside") + ": an orientation question, not "
                                                                                   "a size snap")
    if not rows:
        nw, nd = min(max(w, lo_w), hi_w), min(max(d, lo_d), hi_d)
        return {"footprint": (nw, nd), "height": h, "product": f"{nw:.2f} x {nd:.2f} m (range limit)", "changed": True,
                "reason": "; ".join(outside) + "; no product grid: clamped to the range"}
    if is_run(ftype) or (ftype in KEEP_LENGTH_TYPES and err_w <= SNAP_TOLERANCE + 1e-9):
        long_first = w >= d
        length, depth = (w, d) if long_first else (d, w)
        length = min(max(length, lo_w), hi_w)
        depths = sorted({row["d"] for row in rows})
        depth = min(depths, key=lambda v: (abs(math.log(v / depth)), v))
        nw, nd = (length, depth) if long_first else (depth, length)
        row = next(x for x in rows if abs(x["d"] - depth) < 1e-9)
        what = "a run" if is_run(ftype) else "a long piece"
        return {"footprint": (round(nw, 4), round(nd, 4)), "height": _snap_height(h, h_err, row),
                "product": f"{length:.2f} m long x {depth:.2f} m deep ({row['label'].split(':')[0].strip()})",
                "changed": True, "reason": "; ".join(outside) + f"; {what} keeps its length and takes the product depth"}
    square = abs(math.log(w / d)) <= SQUARE_EPS
    pool = [row for row in rows if abs(math.log(row["w"] / row["d"])) <= SQUARE_EPS] if square else []
    pool = pool or rows

    def key(item):
        i, row = item
        dw, dd = abs(math.log(w / row["w"])), abs(math.log(d / row["d"]))
        return (round(max(dw, dd), 6), round(dw + dd, 6), i)
    _i, best = min(enumerate(pool), key=key)
    return {"footprint": (best["w"], best["d"]), "height": _snap_height(h, h_err, best), "product": _row_text(best),
            "changed": True, "reason": "; ".join(outside) + (" (square symbol: square products only)" if square and
                                                              len(pool) < len(rows) else "")
            + f"; nearest real product {best['w']:.2f} x {best['d']:.2f} m"}


def _snap_height(h: Optional[float], h_err: float, row: dict) -> Optional[float]:
    """The height after a snap: the drawn one when it is inside the range (or None), else the row's."""
    if h is None or h_err <= SNAP_TOLERANCE + 1e-9 or row.get("h") is None:
        return h
    return float(row["h"])


PRODUCT_GRID: dict[str, list[dict]] = _build_grid()


# 29 Oct 2026 (user on real06 run 20261028-154514-full, the master bedroom's floor lamp f_L1_020: "I did not like
# this light", lesson UL94): the plan symbol of a small decor-like piece is drawn larger than the product (a floor lamp
# is a 0.5-0.6 m circle with a cross); fitted to that circle, the fit took a lamp with a 0.58 m black drum shade. A
# drawn symbol of such a type wider than ``SYMBOL_MAX_M`` (the largest product of the type a designer would choose
# for a room, seen from above) is fitted at the type's default product (``real_range(...)["product"]``), centred where
# it is drawn; a drawn size up to the cap stays as drawn. Off with the size snap (``furnished_rooms: keep`` /
# ``furnished_rooms_keep_size``): the fit's ``apply_size_snap`` calls it.
SYMBOL_MAX_M: dict[str, float] = {
    "floor_lamp": 0.45,    # std: floor lamps are 0.30-0.45 m from above (base or shade); the grid's wide 0.60 m row is
                           # a 5-arm lamp, never a reason to fit a drawn 0.58 m circle with a heavy drum shade
}


def symbol_snap(ftype: str, footprint) -> dict:
    """The real product of a drawn plan symbol (pure; note above): ``{"footprint": (w, d), "product", "changed",
    "reason"}``; ``changed`` False (the footprint as given) for a type without a symbol cap or a footprint within it."""
    try:
        w, d = float(footprint[0]), float(footprint[1])
    except (TypeError, ValueError, IndexError):
        return {"footprint": footprint, "product": None, "changed": False, "reason": "no footprint"}
    cap = SYMBOL_MAX_M.get(str(ftype))
    r = real_range(ftype) if cap is not None else None
    if cap is None or r is None or not r.get("product") or max(w, d) <= cap + 1e-9:
        return {"footprint": (w, d), "product": None, "changed": False,
                "reason": "no symbol cap" if cap is None else f"within the {cap:.2f} m a {ftype} takes from above"}
    pw, pd = float(r["product"][0]), float(r["product"][1])
    name = str(ftype).replace("_", " ")
    return {"footprint": (pw, pd), "product": f"{pw:.2f} x {pd:.2f} m ({name}, default product)", "changed": True,
            "reason": (f"the drawn {name} {w:.2f} x {d:.2f} m is a plan symbol larger than the product (a {name} takes "
                       f"at most {cap:.2f} m from above): fitted at the real product {pw:.2f} x {pd:.2f} m, centred "
                       "where it is drawn")}
