"""Drawn demands of the PoC projects, the product size grid and the library's coverage per licence mode
(docs/milestone13.md §5.1 phase 2, §13.2 row ``demands.py``; track T7).

What:

- ``drawn_demands(building_paths) -> [{type, w, d, h, count, projects, drawn, added, kind}]``: every furniture
  piece the three committed buildings (``results/furniture/<p>/building_final.json``) ask the library for: the drawn
  pieces (``source: from_documents``: ``drawn_footprint`` / ``drawn_type`` where the Milestone 13 stages wrote them,
  else the piece's ``footprint.size`` and ``type``) and the pieces the completion added (``added_by_ai``), grouped by
  type and footprint (1 cm); the building's decor pieces (``decor``) count as decor demands (``kind: decor``). Types
  built by rule (counter runs, wall cabinets, stairs, ``unknown``) are no library demand (``SKIP_TYPES``). A height
  the building does not give is the type's default product height (``sizes.real_range``).
- ``size_grid(demands) -> {type: [bins]}``: the bins of real product sizes of every demanded type
  (``wenart.furniture.sizes.PRODUCT_GRID``, the YAML ``grid`` block, else the type's ``products``), each bin
  ``{bin, w, d, h, label, demand, projects}`` with the demands nearest to it (log distance of width and depth, as
  ``sizes.snap_size``); a type without a size row gets one bin per distinct demand.
- ``coverage(catalog, demands, mode) -> {type: {bin: n}}``: how many usable library models (``catalog.usable(entry,
  mode)``, the T1 licence rule: ``commercial`` takes commercial-safe entries, ``relaxed`` every flag but
  no-derivatives) fit each bin within the fit's caps (``COVER``: the mean scale 0.85-1.20 and the non-uniform stretch
  1.10 of ``wenart.furniture.fit``: a model counts when the fit could take it for a piece of the bin's size).
- ``demand_gaps(grid, coverage_by_mode, min_models=2)``: every demand bin with fewer than ``min_models`` usable models
  in a mode (``MIN_MODELS_PER_BIN``), with the sources that could fill it (``gaps.SOURCES_FOR`` plus HSSD in relaxed
  mode): the rows of ``gaps.demand_gaps_markdown``.

Why: the diagnosis (§1.3) found the library thin exactly where the drawings are large (a 3.35 m table, 2.6-3.1 m
wardrobe runs, a 4.4 m corner sofa) and empty for bath and kitchen fixtures of a real look; growth by count per type
(20 models) does not fix that. The picks of pod P2 (ABO by size grid, HSSD by type and bin) follow these demands, and
the gap report says per bin and mode what is still missing after the audit.

How: pure functions over the building JSON, the size table and a catalogue (a ``catalog.Catalog`` or a plain dict
with ``entries`` / ``decor``); deterministic order (types as first demanded, bins in grid order).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from wenart.assets.audit import REPO

PROJECTS = ("real02", "real03", "real04")
BUILDING_PATHS: dict[str, Path] = {p: REPO / "results" / "furniture" / p / "building_final.json" for p in PROJECTS}
# Built by rule, never from the library (wenart.furniture.catalog BY_DESIGN_PARAMETRIC_TYPES minus the fixtures the
# library should hold, PARAMETRIC_ONLY_TYPES, and the untyped pieces).
SKIP_TYPES: tuple[str, ...] = ("unknown", "kitchen_counter", "wall_cabinet", "stair", "book_set")
SKIP_STATUS: tuple[str, ...] = ("removed", "rejected", "not_furniture")
ROUND_M = 0.01
# The fit's caps a model must pass to serve a piece of the bin's size (= wenart.furniture.fit.UNIFORM_RANGE and
# NON_UNIFORM_CAP; tests/test_m13_library.py keeps them equal).
COVER = {"mean_scale": (0.85, 1.20), "non_uniform": 1.10}
MIN_MODELS_PER_BIN = 2
SOURCES_RELAXED_ONLY = ("hssd (relaxed mode only, CC BY-NC 4.0)",)


def _bin_key(w: float, d: float) -> str:
    return f"{w:.2f}x{d:.2f}"


def _size_of(piece: dict) -> Optional[tuple[float, float]]:
    """``(w, d)`` of a piece: the drawn footprint when the Milestone 13 stages kept one, else the footprint size, else
    the decor ``size``."""
    drawn = piece.get("drawn_footprint")
    if isinstance(drawn, dict):
        drawn = drawn.get("size")
    for cand in (drawn, (piece.get("footprint") or {}).get("size") if isinstance(piece.get("footprint"), dict)
                 else None, piece.get("size")):
        if isinstance(cand, (list, tuple)) and len(cand) >= 2:
            try:
                w, d = float(cand[0]), float(cand[1])
            except (TypeError, ValueError):
                continue
            if w > 0 and d > 0:
                return w, d
    return None


def _height_of(piece: dict, ftype: str) -> tuple[Optional[float], str]:
    for key in ("drawn_height", "height"):
        v = piece.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
            return round(float(v), 4), key
    from wenart.furniture import sizes as SZ
    r = SZ.real_range(ftype)
    if r and r.get("product"):
        return float(r["product"][2]), "type default"
    return None, "none"


def _type_of(piece: dict) -> Optional[str]:
    t = piece.get("drawn_type") or piece.get("type")
    return str(t) if t else None


def read_building(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def piece_demands(building: dict, project: str, include_decor: bool = True) -> list[dict]:
    """One row per demanded piece of a building: ``{project, id, type, kind, w, d, h, h_from, source}``."""
    rows = []
    sections = [("furniture", "furniture")] + ([("decor", "decor")] if include_decor else [])
    for section, kind in sections:
        for piece in building.get(section) or []:
            if not isinstance(piece, dict):
                continue
            if str(piece.get("status") or "") in SKIP_STATUS or piece.get("not_furniture"):
                continue
            ftype = _type_of(piece)
            if not ftype or ftype in SKIP_TYPES:
                continue
            size = _size_of(piece)
            if size is None:
                continue
            source = str(piece.get("source") or "")
            if source not in ("from_documents", "added_by_ai"):
                continue
            h, h_from = _height_of(piece, ftype)
            rows.append({"project": project, "id": str(piece.get("id")), "type": ftype, "kind": kind,
                         "w": round(size[0], 4), "d": round(size[1], 4), "h": h, "h_from": h_from, "source": source})
    return rows


def drawn_demands(building_paths=None, include_decor: bool = True) -> list[dict]:
    """The demands of the buildings (module docstring): ``building_paths`` is ``{project: path}`` (default the three
    committed buildings) or a list of paths (the project name is the parent folder's)."""
    if building_paths is None:
        building_paths = BUILDING_PATHS
    if isinstance(building_paths, dict):
        pairs = [(str(k), Path(v)) for k, v in building_paths.items()]
    else:
        pairs = [(Path(p).parent.name, Path(p)) for p in building_paths]
    rows: list[dict] = []
    for project, path in pairs:
        if not path.is_file():
            continue
        rows += piece_demands(read_building(path), project, include_decor)
    groups: dict = {}
    order: list = []
    for r in rows:
        key = (r["type"], max(ROUND_M, round(round(r["w"] / ROUND_M) * ROUND_M, 2)),
               max(ROUND_M, round(round(r["d"] / ROUND_M) * ROUND_M, 2)))
        g = groups.get(key)
        if g is None:
            g = groups[key] = {"type": r["type"], "kind": r["kind"], "w": key[1], "d": key[2], "h": r["h"],
                               "h_from": r["h_from"], "count": 0, "drawn": 0, "added": 0, "projects": [],
                               "ids": []}
            order.append(key)
        g["count"] += 1
        g["drawn" if r["source"] == "from_documents" else "added"] += 1
        if r["project"] not in g["projects"]:
            g["projects"].append(r["project"])
        g["ids"].append(f"{r['project']}:{r['id']}")
        if g["h"] is None and r["h"] is not None:
            g["h"], g["h_from"] = r["h"], r["h_from"]
    out = [groups[k] for k in order]
    out.sort(key=lambda g: (g["kind"] != "furniture", g["type"], -g["count"], g["w"], g["d"]))
    for g in out:
        g["bin"] = _bin_key(g["w"], g["d"])
        g["projects"] = sorted(g["projects"])
    return out


# --------------------------------------------------------------------------
# The size grid
# --------------------------------------------------------------------------

def _log_dist(w: float, d: float, row_w: float, row_d: float) -> float:
    return max(abs(math.log(w / row_w)), abs(math.log(d / row_d)))


def grid_rows(ftype: str) -> list[dict]:
    """The product rows of a type (``sizes.PRODUCT_GRID``, else its ``products`` with the default height); [] for a
    type without a size row."""
    from wenart.furniture import sizes as SZ
    rows = SZ.PRODUCT_GRID.get(ftype)
    if rows:
        return [dict(r) for r in rows]
    r = SZ.real_range(ftype)
    out = []
    for i, p in enumerate(SZ.products(ftype)):
        h = float(p[2]) if len(p) > 2 else (r["product"][2] if r and r.get("product") else None)
        out.append({"w": float(p[0]), "d": float(p[1]), "h": h, "label": "default product" if i == 0 else "product"})
    return out


def nearest_bin(ftype: str, w: float, d: float, rows: Optional[list[dict]] = None) -> Optional[dict]:
    """The grid row nearest to a footprint (either orientation; ties keep the grid order), None without rows."""
    rows = grid_rows(ftype) if rows is None else rows
    if not rows or w <= 0 or d <= 0:
        return None
    best = None
    for i, row in enumerate(rows):
        dist = min(_log_dist(w, d, row["w"], row["d"]), _log_dist(d, w, row["w"], row["d"]))
        if best is None or dist < best[0] - 1e-12:
            best = (dist, i, row)
    return best[2]


def size_grid(demands: list[dict]) -> dict[str, list[dict]]:
    """``{type: [bins]}`` of every demanded type (module docstring)."""
    out: dict[str, list[dict]] = {}
    for dem in demands:
        ftype = dem["type"]
        if ftype not in out:
            rows = grid_rows(ftype)
            out[ftype] = [{"bin": _bin_key(r["w"], r["d"]), "w": r["w"], "d": r["d"], "h": r.get("h"),
                           "label": r.get("label") or "", "demand": 0, "projects": [], "from": "grid"} for r in rows]
        bins = out[ftype]
        if bins and bins[0]["from"] == "grid":
            row = nearest_bin(ftype, dem["w"], dem["d"], bins)
            target = next(b for b in bins if b["w"] == row["w"] and b["d"] == row["d"])
        else:
            target = next((b for b in bins if b["bin"] == _bin_key(dem["w"], dem["d"])), None)
            if target is None:
                target = {"bin": _bin_key(dem["w"], dem["d"]), "w": dem["w"], "d": dem["d"], "h": dem.get("h"),
                          "label": "demand (no product grid for this type)", "demand": 0, "projects": [],
                          "from": "demand"}
                bins.append(target)
        target["demand"] += int(dem.get("count") or 0)
        target["projects"] = sorted(set(target["projects"]) | set(dem.get("projects") or []))
        target.setdefault("demanded_sizes", []).append({"w": dem["w"], "d": dem["d"], "count": dem.get("count", 0)})
    return out


# --------------------------------------------------------------------------
# Coverage per licence mode
# --------------------------------------------------------------------------

def entries_of(catalog) -> list[dict]:
    """The model entries of a ``catalog.Catalog`` or a catalogue dict (parametric rows left out)."""
    if hasattr(catalog, "models") and hasattr(catalog, "decor"):
        return list(catalog.models) + list(catalog.decor)
    data = catalog or {}
    return [e for s in ("entries", "decor") for e in (data.get(s) or []) if isinstance(e, dict)
            and not e.get("parametric")]


def entry_type(entry: dict) -> str:
    """The demand type of an entry: furniture ``type``; decor by ``decor_type`` or the ``decor_`` prefix."""
    if entry.get("decor_type"):
        return str(entry["decor_type"])
    t = str(entry.get("type") or "")
    return t[len("decor_"):] if t.startswith("decor_") else t


def covers(bbox_m, w: float, d: float, h_range=None, caps: Optional[dict] = None,
           h_tolerance: float = 0.15) -> bool:
    """True when a model box ``bbox_m`` (w, d, h) could serve a piece of ``w`` x ``d`` within the fit's caps: the
    width and depth scales inside the mean-scale range with their spread within the non-uniform cap, and the scaled
    height inside the type's height range ``h_range`` (``(lo, hi)`` plus ``h_tolerance``, the fit's HEIGHT_TOLERANCE;
    drawn pieces carry no height, so the range stands in for it)."""
    caps = caps or COVER
    try:
        mw, md, mh = (float(v) for v in bbox_m[:3])
    except (TypeError, ValueError):
        return False
    if min(mw, md, mh) <= 0 or w <= 0 or d <= 0:
        return False
    scales = [w / mw, d / md]
    lo, hi = caps["mean_scale"]
    mean = sum(scales) / len(scales)
    if not lo <= mean <= hi:
        return False
    if max(scales) / min(scales) > caps["non_uniform"] + 1e-9:
        return False
    if h_range:
        h = mh * mean
        if not h_range[0] / (1.0 + h_tolerance) <= h <= h_range[1] * (1.0 + h_tolerance):
            return False
    return True


def height_range(ftype: str):
    """The type's real height range ``(lo, hi)`` or None (``sizes.real_range``)."""
    from wenart.furniture import sizes as SZ
    r = SZ.real_range(ftype)
    return r["height"] if r and r.get("height") else None


def coverage(catalog, demands: list[dict], mode: str = "commercial") -> dict[str, dict[str, int]]:
    """``{type: {bin: n}}``: usable models (``catalog.usable(entry, mode)``) that fit each demand bin (module
    docstring)."""
    return {t: {b: len(ids) for b, ids in bins.items()} for t, bins in coverage_ids(catalog, demands, mode).items()}


def coverage_ids(catalog, demands: list[dict], mode: str = "commercial") -> dict[str, dict[str, list[str]]]:
    """As ``coverage`` with the model ids per bin."""
    from wenart.furniture import catalog as C
    grid = size_grid(demands)
    by_type: dict[str, list[dict]] = {}
    for e in entries_of(catalog):
        if C.usable(e, mode):
            by_type.setdefault(entry_type(e), []).append(e)
    out: dict[str, dict[str, list[str]]] = {}
    for ftype, bins in grid.items():
        out[ftype] = {}
        h_range = height_range(ftype)
        for b in bins:
            ids = [e["id"] for e in by_type.get(ftype, []) if covers(e.get("bbox_m") or [], b["w"], b["d"], h_range)]
            out[ftype][b["bin"]] = sorted(ids)
    return out


def demand_gaps(grid: dict, coverage_by_mode: dict, min_models: int = MIN_MODELS_PER_BIN) -> list[dict]:
    """Rows ``{type, bin, w, d, h, demand, projects, <mode>: n ..., gap_<mode>: n ..., sources}`` of every demanded
    bin that has fewer than ``min_models`` usable models in any mode of ``coverage_by_mode`` (``{mode: coverage}``)."""
    from wenart.assets.audit import gaps as GP
    modes = list(coverage_by_mode)
    rows = []
    for ftype, bins in grid.items():
        for b in bins:
            if not b.get("demand"):
                continue
            counts = {m: int((coverage_by_mode[m].get(ftype) or {}).get(b["bin"], 0)) for m in modes}
            if all(n >= min_models for n in counts.values()):
                continue
            row = {"type": ftype, "bin": b["bin"], "w": b["w"], "d": b["d"], "h": b.get("h"), "label": b.get("label"),
                   "demand": b["demand"], "projects": list(b.get("projects") or [])}
            for m in modes:
                row[m] = counts[m]
                row[f"gap_{m}"] = max(0, min_models - counts[m])
            sources = list(GP.SOURCES_FOR.get(ftype, GP.DEFAULT_SOURCES))
            row["sources"] = sources + [s for s in SOURCES_RELAXED_ONLY if s not in sources]
            rows.append(row)
    return rows


def summary(demands: list[dict]) -> dict:
    """Counts per type (pieces, drawn, added, bins demanded) for reports."""
    out: dict = {}
    for d in demands:
        t = out.setdefault(d["type"], {"kind": d["kind"], "pieces": 0, "drawn": 0, "added": 0, "sizes": 0,
                                       "projects": set()})
        t["pieces"] += d["count"]
        t["drawn"] += d["drawn"]
        t["added"] += d["added"]
        t["sizes"] += 1
        t["projects"] |= set(d["projects"])
    return {t: dict(v, projects=sorted(v["projects"])) for t, v in out.items()}
