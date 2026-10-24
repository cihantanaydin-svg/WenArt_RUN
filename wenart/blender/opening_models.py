"""Library doors and windows for the outer openings (user request of 24 Oct 2026: "start using outside doors ... there
are new windows you can try to use").

What: ``plan(building, levels, outlines, extras, mode)`` -> ``{opening id: entry}``: for every door and window on the
outside of the building, the audited library model of its category, scaled into the opening (side by side in
``panels`` for a long window or a wide glazed door), or nothing (the parametric opening stays). ``load_extras(path)``
reads the catalogue's ``extras`` (the 3D Warehouse doors and windows).

Why: the parametric doors and windows are plain frames and slabs; the library holds about 90 audited doors and 50
windows (``wenart/furniture/catalog_library.json`` extras, types ``door`` and ``window``).

How (pure; ``opening_build.build_library_opening`` makes the Blender objects):
- categories: ``entrance`` (the main entrance of ``site.entrances``, else the first door at grade), ``door`` (any
  other outside door narrower than ``WIDE_DOOR_M``), ``glazed_door`` (wider) and ``window``;
- candidates: audit ``keep`` / ``fix``, usable in the licence mode, a plausible size for the category (``SIZES``), no
  pack, set or inside door (``INSIDE_WORDS``) in the title, depth under ``MAX_DEPTH_M``; ranked textured first, the
  title's category words (``WORDS``), ``keep`` before ``fix``, then the smallest proportion error over the
  category's openings, then the id;
- one model per category, so a building's windows match: an opening takes the category's model when one panel's
  proportions (panel width over height) lie within ``ASPECT_TOL`` (a log ratio) of the model's, with the number of
  panels (1 .. ``MAX_PANELS``) that fits best and its height lies within ``MAX_SCALE`` of the model's (a scaled-down
  model gets toy frames); else the next ranked candidate that fits; else none.
Every entry records the asset (id, file, frame fields, licence), ``panels``, ``category``, ``aspect_error``, the
``outward`` plan direction and the reason; the build marks the object ``inferred`` (the documents draw the opening, not its product).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional, Sequence

WIDE_DOOR_M = 1.4
MAX_DEPTH_M = 0.45
ASPECT_TOL = 0.25                  # |log(panel w/h over model w/h)| <= 0.25: about 28 % either way
MAX_SCALE = 1.8                    # the opening's height within 1/1.8 .. 1.8 x the model's (frames keep real sizes)
MAX_PANELS = 8
SIZES = {                          # (width range, height range) of one model, metres
    "entrance": ((0.75, 1.5), (1.9, 2.8)),
    "door": ((0.65, 1.4), (1.9, 2.7)),
    "glazed_door": ((1.2, 4.0), (1.9, 2.9)),
    "window": ((0.4, 3.0), (0.4, 2.6)),
}
WORDS = {                          # title words that say a model is meant for the category
    "entrance": ("front", "entrance", "entry", "main", "pivot", "exterior"),
    "door": ("front", "entry", "exterior", "door"),
    "glazed_door": ("sliding", "glass", "french", "patio", "folding", "balcony", "terrace"),
    "window": ("window", "casement", "sliding", "awning", "tilt"),
}
INSIDE_WORDS = ("interior", "internal", "toilet", "elevator", "japanese", "closet", "wardrobe", "shower", "barn")
NOT_WORDS = {                      # title words that rule a model out of the category (an outer opening)
    "entrance": ("sliding", "folding", "glass", "garage", "pack", "set", "window") + INSIDE_WORDS,
    "door": ("sliding", "folding", "garage", "pack", "set", "window") + INSIDE_WORDS,
    "glazed_door": ("garage", "pack", "set") + INSIDE_WORDS,
    "window": ("pack", "set", "door", "curtain", "blind", "shutter", "wall"),
}
NEVER_FLAGS = ("no_derivatives", "unknown")


def load_extras(path) -> list[dict]:
    """The catalogue's ``extras`` (doors, windows, ... of the 3D Warehouse layer); [] when the file or key is missing."""
    p = Path(path)
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return list(data.get("extras") or [])


def _usable(entry: dict, mode: str) -> bool:
    status = str(((entry.get("audit") or {}).get("status")) or "").lower()
    if status not in ("keep", "fix"):
        return False
    flag = str(entry.get("licence_flag") or "unknown")
    if mode == "commercial":
        return flag == "none"
    return flag not in NEVER_FLAGS


def _title(entry: dict) -> str:
    return f" {str(entry.get('title') or entry.get('name') or '').lower()} "


def _has(title: str, words) -> bool:
    return any(f" {w}" in title or f"{w} " in title for w in words)


def model_size(entry: dict) -> Optional[tuple[float, float, float]]:
    """(width, depth, height) of a model in metres in its front frame: the catalogue box (already in metres, x along
    the front, y the depth, z up for an entry whose front axis is -Y or +Y; a front along x swaps width and depth)."""
    box = entry.get("bbox_m")
    if not box or len(box) < 3 or min(float(v) for v in box[:3]) <= 0.0:
        return None
    w, d, h = (float(v) for v in box[:3])
    if str(entry.get("front_axis") or "-Y").upper().endswith("X"):
        w, d = d, w
    return w, d, h


def candidates(extras: Sequence[dict], category: str, mode: str) -> list[dict]:
    """The usable models of a category (see the module docstring), unranked."""
    kind = "window" if category == "window" else "door"
    (w0, w1), (h0, h1) = SIZES[category]
    out = []
    for e in extras:
        if e.get("type") != kind or not _usable(e, mode) or not e.get("glb"):
            continue
        size = model_size(e)
        if size is None:
            continue
        w, d, h = size
        title = _title(e)
        if not (w0 <= w <= w1 and h0 <= h <= h1 and d <= MAX_DEPTH_M) or _has(title, NOT_WORDS[category]):
            continue
        if category == "glazed_door" and not (_has(title, WORDS["glazed_door"]) or "glass" in (e.get("material_tags") or [])):
            continue
        out.append(e)
    return out


def best_panels(width: float, height: float, model_aspect: float) -> tuple[int, float]:
    """``(panels, error)``: how many panels side by side give the opening's panels the model's proportions best, and
    the remaining log error."""
    if width <= 0 or height <= 0 or model_aspect <= 0:
        return 1, math.inf
    best = (1, math.inf)
    for n in range(1, MAX_PANELS + 1):
        err = abs(math.log((width / n / height) / model_aspect))
        if err < best[1] - 1e-9:
            best = (n, err)
    return best


def _rank_key(entry: dict, category: str, openings: Sequence[tuple[float, float]]):
    w, _d, h = model_size(entry)
    errs = [best_panels(ow, oh, w / h)[1] for ow, oh in openings] or [0.0]
    title = _title(entry)
    status = str((entry.get("audit") or {}).get("status") or "").lower()
    return (0 if entry.get("textured") else 1, 0 if _has(title, WORDS[category]) else 1,
            0 if status == "keep" else 1, round(sum(min(e, 1.0) for e in errs) / len(errs), 4),
            str(entry.get("id")))


def _number(v) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def asset_of(entry: dict) -> dict:
    """The fields the build needs to load and frame a model (``furniture.resolve_asset`` / ``fit_vertices``) and the
    report needs to credit it."""
    keys = ("id", "glb", "front_axis", "up_axis", "unit_scale", "origin_offset", "bbox_m", "source", "licence",
            "licence_url", "licence_flag", "commercial_safe", "attribution", "author", "title", "uid")
    out = {k: entry.get(k) for k in keys if entry.get(k) is not None}
    out.update(method="library", asset_id=entry.get("id"), library=entry.get("source") or "3dwh")
    return out


def categorise(building: dict, outer: Sequence[dict]) -> dict[str, str]:
    """``{opening id: category}`` of the outer openings (``site.outer_openings`` records)."""
    entrances = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
                 and not r.get("into_air") and not r.get("below_ground")]
    main = next((r.get("door_id") for r in entrances if r.get("main")), None)
    if main is None and entrances:
        main = entrances[0].get("door_id")
    out = {}
    for rec in outer:
        o = rec["opening"]
        width = _number(o.get("width")) or 0.0
        if o.get("type") == "door":
            out[o["id"]] = "entrance" if o["id"] == main else ("glazed_door" if width >= WIDE_DOOR_M else "door")
        elif o.get("type") == "window":
            out[o["id"]] = "window"
    return out


def plan(building: dict, outer: Sequence[dict], extras: Sequence[dict], mode: str = "relaxed") -> dict[str, dict]:
    """``{opening id: {"asset", "panels", "category", "aspect_error", "reason"}}`` for the outer openings ``outer``
    (``site.outer_openings`` records: ``opening``, ``bottom``, ``top``)."""
    cats = categorise(building, outer)
    sizes: dict[str, tuple[float, float]] = {}
    outward = {rec["opening"]["id"]: [round(float(v), 6) for v in rec["outward"][:2]] for rec in outer
               if rec.get("outward") is not None}
    for rec in outer:
        o = rec["opening"]
        width = _number(o.get("width")) or 0.0
        height = float(rec["top"]) - float(rec["bottom"])
        if width > 0 and height > 0:
            sizes[o["id"]] = (width, height)
    out: dict[str, dict] = {}
    for category in ("entrance", "door", "glazed_door", "window"):
        ids = [i for i, c in cats.items() if c == category and i in sizes]
        if not ids:
            continue
        cands = candidates(extras, category, mode)
        if not cands:
            continue
        ranked = sorted(cands, key=lambda e: _rank_key(e, category, [sizes[i] for i in ids]))
        for oid in ids:
            width, height = sizes[oid]
            for e in ranked:
                w, _d, h = model_size(e)
                n, err = best_panels(width, height, w / h)
                if category in ("entrance", "door"):
                    n, err = 1, abs(math.log((width / height) / (w / h)))
                if err <= ASPECT_TOL and abs(math.log(height / h)) <= math.log(MAX_SCALE):
                    out[oid] = {"asset": asset_of(e), "panels": n, "category": category,
                                "aspect_error": round(err, 4), "outward": outward.get(oid),
                                "reason": f"library {category.replace('_', ' ')} {e.get('id')} "
                                          f"({str(e.get('title') or '')[:40]!r}) in {n} panel(s) of "
                                          f"{width / n:.2f} x {height:.2f} m (proportions off by "
                                          f"{(math.exp(err) - 1) * 100:.0f} %; the documents draw the opening, "
                                          f"not its product)"}
                    break
    return out
