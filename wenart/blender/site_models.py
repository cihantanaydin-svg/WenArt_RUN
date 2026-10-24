"""Library models for the site: trees, palms, shrubs and parked cars (user request of 24 Oct 2026: "start using the
new library items for the outside items, plants cars etc").

What (pure; ``vegetation.tree_object`` and ``site.build_cars`` make the objects):
- ``plant_model(species_rec, extras, mode)``: the audited library tree, palm or bush for a species, or None;
- ``car_models(extras, mode)``: the audited cars that pass the size check, ranked; ``car_slots(platform, n)``: where
  cars stand on a drawn parking.

Why: the catalogue's ``extras`` hold about 160 trees, 30 palms, 20 hedges and 20 cars (3D Warehouse, audited);
the site built Sapling trees and leaf-card shrubs and no cars.

How:
- a plant is a single plant: no collection, set, pot, indoor or group words (``PLANT_NOT``), round in plan (the
  smaller plan side at least ``ROUND_PLAN`` of the larger), standing (height at least ``UPRIGHT`` x the plan size for
  a tree or a palm, ``BUSH_UPRIGHT`` for a bush), textured, ``MIN_POLY`` .. ``MAX_POLY`` faces; its crown proportion
  (plan size over height) fits the species' crown (``CROWN_RATIO``);
- the species' own words (``SPECIES_WORDS``) first, then the crown's words (``CROWN_WORDS``), then any plant of the
  crown's kind (palm, bush or broadleaf tree); within a rank ``keep`` before ``fix``, the proportion closest to the
  crown's middle, then the id. One model per species, so a row of trees matches; the build scales it to the drawn
  height and turns each instance by its seed. A species with no model keeps the earlier sources;
- a car: type ``car``, textured, no turntable / toy / kit words, its width (mirrors included) brought to ``CAR_WIDTH_M``
  by a uniform scale within ``CAR_SCALE``, then a length of ``CAR_LENGTH_M``; ranked ``keep`` before ``fix``, the length closest to
  4.6 m, the id;
- slots: perpendicular bays (``BAY_M``) along the parking's long side when its short side holds a car's length, else
  parallel bays; at most ``MAX_CARS`` cars per parking, the bays nearest the parking's centre, every car inside the
  polygon with ``CAR_MARGIN_M`` to its edge.
Every model records its asset (id, file, frame fields, licence) and why it was picked; the report names it as
``inferred`` (the documents draw a tree symbol or a parking, not a product).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

PLANT_NOT = ("collection", "part ", " set", "pack", "trees", "plants", " pot", "potted", "planter", "vaso", "vase",
             "indoor", "decor", "lamp", "stand", "fountain", "bonsai", "hanger", "christmas", "deer", "basket",
             "lounge", "furniture", "pannel", "panel", "river", "island", "along", "three", "colec", "grass",
             "flower", "dummy", "artificial", "faux", "rattan", "kit", "patio", "wall", "arch", "duraleaf",
             "manufactured", "pvc", "topper", "vine", "lipstick")
ROUND_PLAN = 0.6
UPRIGHT = 0.55
BUSH_UPRIGHT = 0.45
MIN_POLY, MAX_POLY = 500, 400_000
CROWN_RATIO = {                # plan size over height of the crown shape
    "round": (0.45, 1.4), "spreading": (0.6, 1.8), "umbrella": (0.6, 1.8), "conical": (0.2, 0.75),
    "columnar": (0.1, 0.45), "palm": (0.3, 1.6), "shrub": (0.6, 2.2),
}
CONIFER = ("pine", "spruce", "fir ", "redwood", "conifer", "cedar", "juniper", "cypress", "kiefer", "pinheiro")
PALM = ("palm", "palmeira", "palmera", "palme", "cycas")
SPECIES_WORDS = {
    "olive": ("olive",), "stone_pine": ("parasol pine", "stone pine", "umbrella pine"),
    "plane": ("plane", "sycamore", "platanus"), "cypress": ("cypress", "cupressus"), "palm": PALM,
    "oleander": ("oleander", "nerium"), "birch": ("birch",), "maple": ("maple", "acer"),
    "oak": ("oak", "quercus"), "conifer": ("spruce", "fir ", "pine", "conifer"), "jacaranda": ("jacaranda",),
    "privet_shrub": ("privet", "bush", "shrub"),
}
CROWN_WORDS = {"conical": CONIFER, "columnar": ("cypress", "juniper", "poplar"), "palm": PALM,
               "shrub": ("bush", "shrub"), "umbrella": ("parasol", "umbrella", "acacia")}
CAR_NOT = ("turntable", "toy", "kit ", "set", "pack", "parking", "lift", "carport")
CAR_WIDTH_M = 2.0              # body and mirrors
CAR_LENGTH_M = (3.8, 5.4)
BAY_M = (2.6, 5.2)             # a perpendicular bay (along the parking's long side, across it)
PARALLEL_BAY_M = (6.0, 2.4)    # a parallel bay (along, across)
CAR_SCALE = (0.7, 1.4)         # a model further off the real width has broken units: never used
MAX_CARS = 2
CAR_MARGIN_M = 0.25


def _status(e: dict) -> str:
    return str(((e.get("audit") or {}).get("status")) or "").lower()


def usable(e: dict, mode: str) -> bool:
    if _status(e) not in ("keep", "fix") or not e.get("glb"):
        return False
    flag = str(e.get("licence_flag") or "unknown")
    return flag == "none" if mode == "commercial" else flag not in ("no_derivatives", "unknown")


def _title(e: dict) -> str:
    return f" {str(e.get('title') or e.get('name') or '').lower()} "


def _has(title: str, words) -> bool:
    return any(w in title for w in words)


def plant_shape(e: dict) -> Optional[tuple[float, float, float]]:
    """``(plan size, smaller over larger plan side, height)`` of a plant model, or None without a box."""
    box = e.get("bbox_m")
    if not box or len(box) < 3:
        return None
    w, d, h = (float(v) for v in box[:3])
    if min(w, d, h) <= 0:
        return None
    return max(w, d), min(w, d) / max(w, d), h


def plant_kind(e: dict) -> Optional[str]:
    """``tree`` | ``palm`` | ``bush`` of a single-plant model (``PLANT_NOT``, ``ROUND_PLAN``, ``UPRIGHT``,
    textured, the face count), else None."""
    if e.get("type") not in ("tree", "palm", "shrub", "hedge") or not e.get("textured"):
        return None
    shape = plant_shape(e)
    poly = int(e.get("polycount") or 0)
    title = _title(e)
    if shape is None or not (MIN_POLY <= poly <= MAX_POLY) or _has(title, PLANT_NOT):
        return None
    size, round_, h = shape
    if round_ < ROUND_PLAN:
        return None
    if e["type"] in ("shrub", "hedge"):
        return "bush" if h >= BUSH_UPRIGHT * size and _has(title, ("bush", "shrub")) else None
    if h < UPRIGHT * size:
        return None
    return "palm" if e["type"] == "palm" or _has(title, PALM) else "tree"


def _crown_fits(e: dict, crown: str) -> bool:
    size, _r, h = plant_shape(e)
    lo, hi = CROWN_RATIO.get(crown, CROWN_RATIO["round"])
    return lo <= size / h <= hi


def plant_model(species_rec: dict, extras: Sequence[dict], mode: str = "relaxed") -> Optional[dict]:
    """The library model of a species (``vegetation.species_record``): see the module docstring. ``{"asset",
    "kind", "match": species | crown | kind, "reason"}`` or None."""
    name = species_rec.get("name")
    crown = species_rec.get("crown") or "round"
    if crown == "hedge":
        return None
    want = "palm" if crown == "palm" else ("bush" if crown == "shrub" else "tree")
    pool = [e for e in extras if usable(e, mode) and plant_kind(e) == want and _crown_fits(e, crown)]
    if want == "tree" and crown not in ("conical", "columnar"):
        broad = [e for e in pool if not _has(_title(e), CONIFER)]
    else:
        broad = pool
    lo, hi = CROWN_RATIO.get(crown, CROWN_RATIO["round"])
    mid = (lo + hi) / 2.0

    def key(e):
        size, _r, h = plant_shape(e)
        return (0 if _status(e) == "keep" else 1, round(abs(size / h - mid), 3), str(e.get("id")))

    for match, words, cands in (("species", SPECIES_WORDS.get(name, ()), pool),
                                ("crown", CROWN_WORDS.get(crown, ()), pool), ("kind", None, broad)):
        hits = [e for e in cands if words is None or (words and _has(_title(e), words))]
        if hits:
            e = sorted(hits, key=key)[0]
            return {"asset": asset_of(e), "kind": want, "match": match,
                    "reason": f"library {want} {e.get('id')} ({str(e.get('title') or '')[:40]!r}) for {name} "
                              f"(matched by {match}; the documents draw the symbol, not the product)"}
    return None


def asset_of(e: dict) -> dict:
    keys = ("id", "glb", "front_axis", "up_axis", "unit_scale", "origin_offset", "bbox_m", "bbox_min_m", "source",
            "licence", "licence_url", "licence_flag", "commercial_safe", "attribution", "author", "title", "uid",
            "polycount")
    out = {k: e.get(k) for k in keys if e.get(k) is not None}
    out.update(method="library", asset_id=e.get("id"), library=e.get("source") or "3dwh")
    return out


def car_size(e: dict) -> Optional[tuple[float, float, float, float]]:
    """``(width, length, height, scale)`` of a car model brought to ``CAR_WIDTH_M`` (front axis X: x is the length)."""
    box = e.get("bbox_m")
    if not box or len(box) < 3 or min(float(v) for v in box[:3]) <= 0:
        return None
    w, d, h = (float(v) for v in box[:3])
    if str(e.get("front_axis") or "-Y").upper().endswith("X"):
        w, d = d, w
    s = CAR_WIDTH_M / w
    return w * s, d * s, h * s, s


def car_models(extras: Sequence[dict], mode: str = "relaxed") -> list[dict]:
    """The usable cars, ranked (module docstring), each ``{"asset", "size": [w, l, h], "scale"}``."""
    out = []
    for e in extras:
        if e.get("type") != "car" or not usable(e, mode) or not e.get("textured") or _has(_title(e), CAR_NOT):
            continue
        size = car_size(e)
        if size is None:
            continue
        w, length, h, s = size
        if not (CAR_LENGTH_M[0] <= length <= CAR_LENGTH_M[1] and 1.1 <= h <= 2.1 and CAR_SCALE[0] <= s <= CAR_SCALE[1]):
            continue
        out.append((0 if _status(e) == "keep" else 1, round(abs(length - 4.6), 3), str(e.get("id")),
                    {"asset": asset_of(e), "size": [round(w, 3), round(length, 3), round(h, 3)], "scale": round(s, 4)}))
    return [x[-1] for x in sorted(out, key=lambda x: x[:3])]


def _inside(poly, x, y) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i][:2], poly[(i + 1) % n][:2]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _main_axis(poly) -> tuple[float, float]:
    best, axis = -1.0, (1.0, 0.0)
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i][:2], poly[(i + 1) % len(poly)][:2]
        d = math.hypot(x1 - x0, y1 - y0)
        if d > best:
            best, axis = d, ((x1 - x0) / d, (y1 - y0) / d) if d > 1e-9 else (1.0, 0.0)
    return axis


def car_slots(polygon: Sequence[Sequence[float]], n: int = MAX_CARS) -> list[dict]:
    """``[{"center": [x, y], "rotation_deg", "bay": [w, l], "layout": perpendicular | parallel}]``: up to ``n`` bays
    on the parking ``polygon`` (pure; module docstring). The rotation turns the car's front (-Y) along the bay."""
    poly = [(float(p[0]), float(p[1])) for p in polygon]
    if len(poly) < 3:
        return []
    ux, uy = _main_axis(poly)
    vx, vy = -uy, ux
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    us = [(p[0] - cx) * ux + (p[1] - cy) * uy for p in poly]
    vs = [(p[0] - cx) * vx + (p[1] - cy) * vy for p in poly]
    long_, short = max(us) - min(us), max(vs) - min(vs)
    out = []
    for layout, (along, across) in (("perpendicular", BAY_M), ("parallel", PARALLEL_BAY_M)):
        if short < across + 2 * CAR_MARGIN_M or long_ < along + 2 * CAR_MARGIN_M:
            continue
        count = int((long_ - 2 * CAR_MARGIN_M) // along)
        v0 = (min(vs) + max(vs)) / 2.0
        u_mid = (min(us) + max(us)) / 2.0
        centres = sorted(((i - (count - 1) / 2.0) * along + u_mid for i in range(count)), key=lambda u: abs(u - u_mid))
        for u in centres:
            x, y = cx + ux * u + vx * v0, cy + uy * u + vy * v0
            half_a, half_c = along / 2.0 - 0.15, across / 2.0 - 0.15
            corners = [(x + ux * a + vx * c, y + uy * a + vy * c) for a in (-half_a, half_a) for c in (-half_c, half_c)]
            if not all(_inside(poly, px, py) for px, py in corners + [(x, y)]):
                continue
            # perpendicular: the car's length across the long axis (its front -Y along -v); parallel: along it
            fx, fy = (-vx, -vy) if layout == "perpendicular" else (ux, uy)
            out.append({"center": [round(x, 4), round(y, 4)], "rotation_deg": round(math.degrees(math.atan2(fx, -fy)), 3),
                        "bay": [along, across], "layout": layout})
            if len(out) >= n:
                return out
        if out:
            return out
    return out
