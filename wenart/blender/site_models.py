"""Library models for the site: trees, palms, shrubs and parked cars (user request of 24 Oct 2026: "start using the
new library items for the outside items, plants cars etc").

What (pure; ``vegetation.tree_object`` and ``site.build_cars`` make the objects):
- ``plant_model(species_rec, extras, mode)``: the audited library tree, palm or bush for a species, or None;
- ``car_models(extras, mode)``: the audited cars that pass the size check, ranked; ``car_slots(platform, n)``: where
  cars stand on a drawn parking.

Why: the catalogue's ``extras`` hold about 160 trees, 30 palms, 20 hedges and 20 cars (3D Warehouse, audited);
the site built Sapling trees and leaf-card shrubs and no cars.

How:
- every model: audit ``keep`` / ``fix``, usable in the licence mode, not rated under ``MIN_VISION_QUALITY`` by the
  audit's vision check (``vision_quality``);
- a plant is a single plant: no collection, set, pot, indoor or group words (``PLANT_NOT``), round in plan (the
  smaller plan side at least ``ROUND_PLAN`` of the larger), standing (height at least ``UPRIGHT`` x the plan size for
  a tree or a palm, ``BUSH_UPRIGHT`` for a bush), textured, ``MIN_POLY`` .. ``MAX_POLY`` faces; its crown proportion
  (plan size over height) fits the species' crown (``CROWN_RATIO``);
- the species' own words (``SPECIES_WORDS``) first, then the crown's words (``CROWN_WORDS``), then any plant of the
  crown's kind (palm, bush or broadleaf tree); within a rank ``keep`` before ``fix``, the proportion closest to the
  crown's middle, then the id. One model per species, so a row of trees matches; the build scales it to the drawn
  height and turns each instance by its seed. A species with no model keeps the earlier sources;
- a car: type ``car``, no turntable / toy / kit words, well made (``car_quality``: textured, at least ``MIN_CAR_POLY``
  faces, no toy-sized texture); its front on the long side of its own box (``car_frame``: 30 Oct 2026, lesson UL129,
  the audit had turned real04's car onto its side and the build stretched it 2 x across); scaled uniformly into a real
  car's size (``car_scale``: 4.2-4.9 m long, at most 2.1 m wide with the mirrors, 1.25-1.75 m high); ranked ``keep``
  before ``fix``, full textures, detailed models, the length closest to 4.6 m, the id; one model per bay in turn;
- slots: bays along the parking's edges (any shape), perpendicular (``BAY_M``) where it is deep enough, else parallel,
  each inside the polygon with ``CAR_MARGIN_M`` to its edge and clear of the flights cut into it and the paths
  arriving at it; at most ``MAX_CARS`` cars per parking, the bays nearest the drawn label first.
Every model records its asset (id, file, frame fields, licence) and why it was picked; the report names it as
``inferred`` (the documents draw a tree symbol or a parking, not a product).
"""
from __future__ import annotations

import math
import re
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
MAX_CARS = 3                   # 30 Oct 2026 (UL129): up to three bays, each its own model where the library has three
CAR_MARGIN_M = 0.25
PARALLEL_PENALTY_M = 3.0
SLOT_STEP_M = 0.5              # the bays tried along an edge


def _status(e: dict) -> str:
    return str(((e.get("audit") or {}).get("status")) or "").lower()


MIN_VISION_QUALITY = 3          # the library audit's vision score (1-5): 2 or less is never picked here


def vision_quality(e: dict) -> Optional[int]:
    """The audit's vision quality of a model when it noted one (``audit.vision_doubt``: "vision quality N ..."),
    else None (24 Oct 2026: real04's library bushes, rated 2, rendered white)."""
    for d in (e.get("audit") or {}).get("vision_doubt") or []:
        m = re.search(r"vision quality (\d)", str(d))
        if m:
            return int(m.group(1))
    return None


def usable(e: dict, mode: str) -> bool:
    if _status(e) not in ("keep", "fix") or not e.get("glb"):
        return False
    q = vision_quality(e)
    if q is not None and q < MIN_VISION_QUALITY:
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
    """The build's record of a site model (29 Oct 2026: with every credit field, ``opening_models.CREDIT_FIELDS``:
    the build refuses a CC BY model without ``source_url`` and ``via``, as it refused the HSSD doors)."""
    from wenart.blender.opening_models import CREDIT_FIELDS

    keys = ("id", "glb", "front_axis", "up_axis", "unit_scale", "origin_offset", "bbox_m", "bbox_min_m", "source",
            "licence", "licence_url", "licence_flag", "licence_declared_by", "commercial_safe", "uid",
            "polycount") + CREDIT_FIELDS
    out = {k: e.get(k) for k in keys if e.get(k) is not None}
    out.update(method="library", asset_id=e.get("id"), library=e.get("source") or "3dwh")
    return out


# 30 Oct 2026 (lesson UL129, user on real04: "maybe include some better car models"): the one car of the run was the
# 3D Warehouse "CAR" fitted to 2.0 m along its length and 4.5 m across it (fit scale 0.40 x 2.05): the library audit had
# turned its front 90 degrees ("the vision check sees the front on the right of view 0") onto the car's side, and
# car_size swapped the catalogue box once more. A car's front is an end of its length: the build takes the front on the
# long plan side of the model's own box (``car_frame``), scales the model uniformly into a real car's size
# (``car_scale``) and never uses a low-poly, toy-textured or wrongly sized model.
CAR_LENGTH_FIT = (4.2, 4.9)    # a real car's length (body), the model is scaled into it
CAR_WIDTH_MAX = 2.1            # with its mirrors
CAR_HEIGHT_FIT = (1.25, 1.75)
CAR_PROPORTION = (1.9, 2.9)    # length over width (with mirrors): no toy or truck
MIN_CAR_POLY = 15_000          # a car of fewer faces has the low-poly look
MIN_CAR_TEXTURE_PX = 200       # the audit's "largest texture N px" under this: a toy's texture
GOOD_CAR_POLY = 30_000


def car_frame(e: dict) -> tuple[str, list[float], str]:
    """``(front_axis, [width, length, height] in the piece frame, note)`` of a car model (pure): its front lies on the
    long plan side of the model's own box (``bbox_model_m``, the frame the build imports; else the catalogue's piece
    box). The catalogue's front axis stands when it lies on that side; a front across the long side (a misread turn)
    goes back to the audit's earlier front when that lies on it, else to the long axis with the catalogue's sign."""
    fa = str(e.get("front_axis") or "-Y").upper()
    model = e.get("bbox_model_m")
    if model and len(model) >= 3 and min(float(v) for v in model[:3]) > 0:
        mx, my, mz = (float(v) for v in model[:3])
    else:                                                  # only the piece box: back to the model frame
        w, d, mz = (float(v) for v in (e.get("bbox_m") or [0, 0, 0])[:3])
        mx, my = (d, w) if fa.endswith("X") else (w, d)
    long_axis = "X" if mx >= my else "Y"
    note = ""
    if not fa.endswith(long_axis):
        before = str(((e.get("audit") or {}).get("before") or {}).get("front_axis") or "").upper()
        if before.endswith(long_axis):
            fa = before
        else:
            fa = fa[0] + long_axis if fa[:1] in "+-" else "-" + long_axis
        note = (f"front {str(e.get('front_axis'))} lay across the car's long side: turned back to {fa} (a car's "
                f"front is an end of its length)")
    width, length = (my, mx) if fa.endswith("X") else (mx, my)
    return fa, [width, length, mz], note


def car_scale(width: float, length: float, height: float) -> Optional[float]:
    """The uniform scale that brings a car's box into a real car's size (pure): its length into ``CAR_LENGTH_FIT``
    (the nearest end), its width with the mirrors at most ``CAR_WIDTH_MAX``; None when the height then falls outside
    ``CAR_HEIGHT_FIT``, the proportion outside ``CAR_PROPORTION`` or the scale outside ``CAR_SCALE`` (broken units)."""
    if min(width, length, height) <= 0:
        return None
    s = 1.0
    if length * s > CAR_LENGTH_FIT[1]:
        s = CAR_LENGTH_FIT[1] / length
    elif length * s < CAR_LENGTH_FIT[0]:
        s = CAR_LENGTH_FIT[0] / length
    if width * s > CAR_WIDTH_MAX:
        s = CAR_WIDTH_MAX / width
    if not (CAR_SCALE[0] <= s <= CAR_SCALE[1]):
        return None
    if not (CAR_HEIGHT_FIT[0] <= height * s <= CAR_HEIGHT_FIT[1]):
        return None
    if not (CAR_PROPORTION[0] <= length / width <= CAR_PROPORTION[1]) or length * s < CAR_LENGTH_FIT[0] - 0.3:
        return None
    return s


def car_size(e: dict) -> Optional[tuple[float, float, float, float]]:
    """``(width, length, height, scale)`` of a car model at a real car's size (``car_frame``, ``car_scale``)."""
    _fa, (w, length, h), _note = car_frame(e)
    if min(w, length, h) <= 0:
        return None
    s = car_scale(w, length, h)
    if s is None:
        return None
    return w * s, length * s, h * s, s


def _texture_px(e: dict) -> Optional[int]:
    for n in (e.get("audit") or {}).get("notes") or []:
        m = re.search(r"largest texture (\d+) px", str(n))
        if m:
            return int(m.group(1))
    return None


def car_quality(e: dict) -> tuple[bool, str]:
    """``(ok, why)``: a car model well made enough to park on a render (pure): textured, at least ``MIN_CAR_POLY``
    faces, no texture under ``MIN_CAR_TEXTURE_PX``, a real product when the audit says so."""
    poly = int(e.get("polycount") or 0)
    if not e.get("textured"):
        return False, "untextured (flat colours)"
    if poly < MIN_CAR_POLY:
        return False, f"{poly} faces: the low-poly look"
    px = _texture_px(e)
    if px is not None and px < MIN_CAR_TEXTURE_PX:
        return False, f"its largest texture is {px} px: a toy's texture"
    if e.get("real_product") is False:
        return False, "no real product"
    return True, "well made"


def car_models(extras: Sequence[dict], mode: str = "relaxed") -> list[dict]:
    """The usable cars, ranked (module docstring), each ``{"asset", "size": [w, l, h], "scale", "frame_note"}``:
    audited, usable in the licence mode, made well (``car_quality``), at a real size (``car_size``); ``keep`` before
    ``fix``, a full texture before a small one, a detailed model before a plain one, the length nearest 4.6 m, the id.
    The asset carries the corrected front (``car_frame``) and its piece box, so the build's fit is uniform."""
    out = []
    for e in extras:
        if e.get("type") != "car" or not usable(e, mode) or _has(_title(e), CAR_NOT):
            continue
        ok, _why = car_quality(e)
        size = car_size(e) if ok else None
        if size is None:
            continue
        w, length, h, s = size
        fa, box, note = car_frame(e)
        asset = asset_of(e)
        asset.update(front_axis=fa, bbox_m=[round(v, 4) for v in box], scaling="uniform")
        px = _texture_px(e)
        out.append((0 if _status(e) == "keep" else 1, 0 if px is None else 1,
                    0 if int(e.get("polycount") or 0) >= GOOD_CAR_POLY else 1, round(abs(length - 4.6), 3),
                    str(e.get("id")),
                    {"asset": asset, "size": [round(w, 3), round(length, 3), round(h, 3)], "scale": round(s, 4),
                     "frame_note": note}))
    return [x[-1] for x in sorted(out, key=lambda x: x[:5])]


def _inside(poly, x, y) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i][:2], poly[(i + 1) % n][:2]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _rect_inside(poly, corners, keep_out) -> bool:
    if not all(_inside(poly, px, py) for px, py in corners):
        return False
    xs, ys = [p[0] for p in corners], [p[1] for p in corners]
    for k in keep_out:
        kx, ky = [p[0] for p in k], [p[1] for p in k]
        if max(kx) < min(xs) or min(kx) > max(xs) or max(ky) < min(ys) or min(ky) > max(ys):
            continue
        # a keep-out overlaps the bay: a corner of one inside the other, or the centres
        if any(_inside(k, px, py) for px, py in corners) or any(_inside(corners_ccw(corners), px, py)
                                                                 for px, py in k):
            return False
        cx, cy = sum(xs) / 4.0, sum(ys) / 4.0
        if _inside(k, cx, cy):
            return False
    return True


def corners_ccw(corners) -> list[tuple[float, float]]:
    cx = sum(p[0] for p in corners) / len(corners)
    cy = sum(p[1] for p in corners) / len(corners)
    return sorted(corners, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def _overlap(a, b) -> bool:
    """Whether two convex quads overlap (separating axes; pure)."""
    for poly in (a, b):
        for i in range(len(poly)):
            ex, ey = poly[(i + 1) % len(poly)][0] - poly[i][0], poly[(i + 1) % len(poly)][1] - poly[i][1]
            nx, ny = -ey, ex
            pa = [p[0] * nx + p[1] * ny for p in a]
            pb = [p[0] * nx + p[1] * ny for p in b]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return False
    return True


def car_slots(polygon: Sequence[Sequence[float]], n: int = MAX_CARS, anchor: Optional[Sequence[float]] = None,
              keep_out: Sequence = ()) -> list[dict]:
    """``[{"center": [x, y], "rotation_deg", "bay": [w, l], "layout": perpendicular | parallel, "edge"}]``: up to ``n``
    bays on the parking ``polygon`` (pure; module docstring). 30 Oct 2026 (lesson UL129: real04's L-shaped parking got
    one car, behind the second house, where its main axis's middle line crossed it): the bays line the parking's
    edges, each fully inside the polygon (any shape) and clear of ``keep_out`` (the flights cut into it and their
    landings, the paths arriving at it): perpendicular bays (``BAY_M``, the car's nose to the edge) where the parking
    is deep enough, else parallel ones (``PARALLEL_BAY_M``, along the edge); the bays nearest the drawn label
    (``anchor``), else the parking's middle, first; no two bays overlap. The rotation turns the car's front (-Y) along
    the bay."""
    raw = [(float(p[0]), float(p[1])) for p in polygon]
    if len(raw) < 3:
        return []
    area = sum(raw[i][0] * raw[(i + 1) % len(raw)][1] - raw[(i + 1) % len(raw)][0] * raw[i][1] for i in range(len(raw)))
    poly = raw if area > 0 else list(reversed(raw))
    keep = [[(float(q[0]), float(q[1])) for q in k] for k in keep_out if len(k) >= 3]
    ref = tuple(anchor) if anchor is not None else (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    cands = []
    for layout, (along, across) in (("perpendicular", BAY_M), ("parallel", PARALLEL_BAY_M)):
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < along + 2 * CAR_MARGIN_M:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            nx, ny = -uy, ux                                # counter-clockwise: the left is inside
            lo, hi = CAR_MARGIN_M + along / 2.0, length - CAR_MARGIN_M - along / 2.0
            count = max(0, int((hi - lo) / SLOT_STEP_M)) + 1
            for j in range(count):
                s = (lo + hi) / 2.0 if count == 1 else lo + (hi - lo) * j / (count - 1)
                d = CAR_MARGIN_M + across / 2.0
                x, y = a[0] + ux * s + nx * d, a[1] + uy * s + ny * d
                ha, hc = along / 2.0 - 0.05, across / 2.0 - 0.05
                corners = [(x + ux * p + nx * q, y + uy * p + ny * q) for p, q in ((-ha, -hc), (ha, -hc), (ha, hc),
                                                                                  (-ha, hc))]
                if not _rect_inside(poly, corners, keep) or not _inside(poly, x, y):
                    continue
                fx, fy = (-nx, -ny) if layout == "perpendicular" else (ux, uy)
                # a parallel bay counts PARALLEL_PENALTY_M farther: perpendicular bays line an edge where they fit
                cands.append((0 if layout == "perpendicular" else 1,
                              round(math.hypot(x - ref[0], y - ref[1]) + (0.0 if layout == "perpendicular"
                                                                          else PARALLEL_PENALTY_M), 3),
                              {"center": [round(x, 4), round(y, 4)],
                               "rotation_deg": round(math.degrees(math.atan2(fx, -fy)), 3), "bay": [along, across],
                               "layout": layout, "edge": i, "corners": [[round(c[0], 4), round(c[1], 4)]
                                                                        for c in corners]}))
    out: list[dict] = []
    for _rank, _dist, c in sorted(cands, key=lambda x: (x[1], x[0])):
        if any(_overlap(c["corners"], o["corners"]) for o in out):
            continue
        out.append(c)
        if len(out) >= n:
            break
    return [{k: v for k, v in c.items() if k != "corners"} for c in out]
