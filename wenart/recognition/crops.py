"""Deterministic crops of one drawn object for the two VLM passes (docs/milestone7.md §3.1, §1.4).

What: ``render_pair(candidate, context, out_dir, key)`` writes two 512 x 512 grey PNGs per AI candidate and
returns ``{"ctx_png", "iso_png", "input_sha256", "crop"}``:

- ``<key>_ctx.png``: a square of side max(2.5 m, 1.6 x the larger side of the object) around the object, walls
  mid-grey, other drawn objects light grey, the object black, a black dashed box around it;
- ``<key>_iso.png``: the object alone, filling 80 % of the square, with a filled 1 m bar under it (no digits, no
  text anywhere). When the 1 m bar would not fit at that zoom (objects under about 0.9 m) the zoom is capped so the
  bar is 448 px long and the object is drawn smaller than 80 %.

Why a canonical hash: a stored answer is reused only while its ``input_sha256`` matches (answers.py), and the pod
must compute the same hash as the session. PNG bytes depend on the zlib build, so the hash covers a **canonical
description** instead: the object's strokes in page millimetres (integers), the two crop squares, the walls and the
other strokes inside the context square (clipped, rounded to 1 mm, rings without repeated or collinear vertices,
starting at their smallest vertex, counter-clockwise), ``CROP_VERSION`` and the question (system prompt, prompt,
schema, the allowed types, the image labels). The images are drawn **from that description only** (cv2 ``LINE_8``,
no anti-aliasing, fixed sizes) and saved with PIL without metadata, so the hash names exactly what the model saw.

Vector candidates (``context = {"walls": [shapely polygons or outline point lists], "others": [point lists]}``,
page metres, y up) are drawn; raster candidates (``context = {"image": grey uint8 array of the rectified page,
"to_px": [a, b, c, d, e, f]}`` with ``x_px = a*x + b*y + c``, ``y_px = d*x + e*y + f`` from page metres) are pixel
crops of the rectified page in the same layout (the iso crop keeps only the pixels inside the object's box); their
hash covers the sha256 of the decoded grey source crops and their shapes instead of strokes (§1.4).

``candidate`` = ``{"key", "footprint": {"center", "size", "rotation_deg"}, "strokes": [point lists, page metres],
"bbox": [x0, y0, x1, y1]}`` (page metres; ``file``, ``page``, ``level`` and ``room_type`` are optional and unused
here).
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Optional

import numpy as np

from wenart.recognition import prompts, schemas

CROP_VERSION = "m7.1"
CROP_PX = 512                      # both crops are CROP_PX x CROP_PX
CTX_MIN_SIDE_M = 2.5               # context square: max(2.5 m, 1.6 x the larger object side)
CTX_SIDE_FACTOR = 1.6
ISO_FILL = 0.8                     # the object fills 80 % of the iso crop ...
BAR_M = 1.0                        # ... above a 1 m bar
BAR_MARGIN_PX = 32
BAR_THICK_PX = 8
BAR_BOTTOM_PX = 16                 # gap under the bar
BAR_MAX_PX = CROP_PX - 2 * BAR_MARGIN_PX
PAPER = 255
WALL_GREY = 128
OTHER_GREY = 200
INK = 0
OBJECT_THICKNESS = 2
OTHER_THICKNESS = 1
DASH_ON_PX, DASH_OFF_PX = 8, 6
BOX_PAD_PX = 8                     # dashed box: the object's box grown by this
ISO_MASK_PAD_PX = 2                # raster iso crop: pixels further than this outside the object's box are blanked

SYMBOL_TASK = "symbol_type"


# --------------------------------------------------------------------------
# Canonical description and its hash
# --------------------------------------------------------------------------

def canonical_json(description: Any) -> str:
    """The one serialisation that is hashed: sorted keys, no spaces, UTF-8 text."""
    return json.dumps(description, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_sha256(description: Any) -> str:
    return hashlib.sha256(canonical_json(description).encode("utf-8")).hexdigest()


def question_digest(task: str) -> dict:
    """What the model is asked for ``task``: system prompt, prompt, schema, image labels (and the type list)."""
    out = {
        "task": task,
        "system": prompts.M7_SYSTEM_PROMPT,
        "prompt": prompts.m7_prompt(task),
        "schema": schemas.M7_SCHEMAS[task],
    }
    if task == SYMBOL_TASK:
        out["types"] = list(schemas.SYMBOL_TYPE_CHOICES)
        out["image_labels"] = list(prompts.SYMBOL_IMAGE_LABELS)
    return out


def array_sha256(arr: np.ndarray) -> dict:
    """sha256 of a decoded grey pixel array plus its shape (raster crops, §1.4)."""
    a = np.ascontiguousarray(arr, dtype=np.uint8)
    return {"sha256": hashlib.sha256(a.tobytes()).hexdigest(), "shape": list(a.shape)}


def mm(v: float) -> int:
    """Metres -> integer millimetres (the 1 mm rounding of §1.4)."""
    return int(round(float(v) * 1000.0))


def _mm_points(points) -> list[list[int]]:
    """A point list in page metres -> mm integer pairs without consecutive repeats (a dot keeps one point)."""
    out: list[list[int]] = []
    for p in points:
        q = [mm(p[0]), mm(p[1])]
        if not out or out[-1] != q:
            out.append(q)
    return out


def _canonical_ring(coords) -> Optional[list[list[int]]]:
    """A closed ring in metres -> mm vertices: no closing repeat, no repeated or collinear vertex, counter-clockwise,
    starting at the smallest vertex; None when fewer than 3 vertices remain."""
    pts = _mm_points(coords)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    changed = True
    while changed and len(pts) >= 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if cross == 0:
                del pts[i]
                changed = True
                break
    if len(pts) < 3:
        return None
    area2 = sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))
    if area2 < 0:
        pts.reverse()
    start = min(range(len(pts)), key=lambda i: pts[i])
    return pts[start:] + pts[:start]


def _polygons(geom) -> list:
    if geom is None or getattr(geom, "is_empty", True):
        return []
    kind = geom.geom_type
    if kind == "Polygon":
        return [geom]
    if kind in ("MultiPolygon", "GeometryCollection"):
        out = []
        for g in geom.geoms:
            out.extend(_polygons(g))
        return out
    return []


def _wall_rings(walls, box_m: tuple[float, float, float, float]) -> list[dict]:
    """Walls clipped to the context square as canonical rings ``{"outer": ring, "holes": [rings]}`` (sorted)."""
    import shapely
    from shapely.geometry import Polygon, box as sbox

    square = sbox(*box_m)
    out = []
    for wall in walls or []:
        if wall is not None and not hasattr(wall, "geom_type"):
            wall = Polygon([(float(p[0]), float(p[1])) for p in wall])       # an outline given as a point list
        if wall is None or wall.is_empty:
            continue
        if not wall.is_valid:
            wall = shapely.make_valid(wall)                                    # a self-touching outline
        if not wall.intersects(square):
            continue
        for poly in _polygons(shapely.clip_by_rect(wall, *box_m)):
            outer = _canonical_ring(poly.exterior.coords)
            if outer is None:
                continue
            holes = [h for h in (_canonical_ring(r.coords) for r in poly.interiors) if h is not None]
            out.append({"outer": outer, "holes": sorted(holes)})
    return sorted(out, key=canonical_json)


def _others_in(others, box_m: tuple[float, float, float, float]) -> list[list[list[int]]]:
    """The other strokes whose box meets the context square, in mm (whole, not clipped; sorted)."""
    x0, y0, x1, y1 = box_m
    out = []
    for pts in others or []:
        if not len(pts):
            continue
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
            continue
        out.append(_mm_points(pts))
    return sorted(out)


# --------------------------------------------------------------------------
# Crop squares
# --------------------------------------------------------------------------

def _bbox_of(candidate: dict) -> tuple[float, float, float, float]:
    if candidate.get("bbox") is not None:
        x0, y0, x1, y1 = (float(v) for v in candidate["bbox"])
        return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)
    pts = [p for s in candidate.get("strokes") or [] for p in s]
    if not pts:
        raise ValueError(f"candidate {candidate.get('key')!r} has neither bbox nor strokes")
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def crop_squares(candidate: dict) -> dict:
    """The two crop squares in page millimetres: ``{"object_box", "ctx_box", "iso_box"}`` ([x0, y0, x1, y1]).

    Both are centred on the object's box. The context side is max(2.5 m, 1.6 x the larger object side), where the
    side is the larger of the footprint's and the box's (a rotated footprint's box is larger, and the object must
    fit). The iso side makes the larger box side 80 % of the crop, but never less than the side at which the 1 m bar
    is BAR_MAX_PX long.
    """
    x0, y0, x1, y1 = _bbox_of(candidate)
    size = (candidate.get("footprint") or {}).get("size") or [0.0, 0.0]
    larger = max(float(size[0]), float(size[1]), x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    ctx_side = max(CTX_MIN_SIDE_M, CTX_SIDE_FACTOR * larger)
    iso_side = max(max(x1 - x0, y1 - y0) / ISO_FILL, BAR_M * CROP_PX / BAR_MAX_PX)

    def square(side):
        h = side / 2.0
        return [mm(cx - h), mm(cy - h), mm(cx + h), mm(cy + h)]

    return {"object_box": [mm(x0), mm(y0), mm(x1), mm(y1)], "ctx_box": square(ctx_side), "iso_box": square(iso_side)}


# --------------------------------------------------------------------------
# Drawing (from the canonical description only)
# --------------------------------------------------------------------------

def _frame(box_mm: list[int]) -> tuple[float, float, float]:
    """(x0, y1, px per mm) of a square crop: page mm -> image px, y flipped."""
    return float(box_mm[0]), float(box_mm[3]), CROP_PX / float(box_mm[2] - box_mm[0])


def _px(points_mm, frame) -> np.ndarray:
    x0, y1, k = frame
    arr = np.asarray(points_mm, dtype=np.float64).reshape(-1, 2)
    xs = (arr[:, 0] - x0) * k
    ys = (y1 - arr[:, 1]) * k
    return np.rint(np.stack([xs, ys], axis=1)).astype(np.int32)


def _polyline(img, pts: np.ndarray, colour: int, thickness: int) -> None:
    import cv2
    if len(pts) == 1 or (pts == pts[0]).all():
        cv2.circle(img, (int(pts[0][0]), int(pts[0][1])), max(1, thickness // 2), colour, -1, cv2.LINE_8)
    else:
        cv2.polylines(img, [pts.reshape(-1, 1, 2)], False, colour, thickness, cv2.LINE_8)


def _dashed_rect(img, x0: int, y0: int, x1: int, y1: int, colour: int = INK) -> None:
    """A dashed rectangle (cv2 has none): dashes of DASH_ON_PX every DASH_ON_PX + DASH_OFF_PX along each edge."""
    import cv2
    for ax, ay, bx, by in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        length = max(abs(bx - ax), abs(by - ay))
        if length == 0:
            continue
        sx, sy = (bx - ax) / length, (by - ay) / length
        pos = 0
        while pos < length:
            end = min(pos + DASH_ON_PX, length)
            cv2.line(img, (int(round(ax + sx * pos)), int(round(ay + sy * pos))),
                     (int(round(ax + sx * end)), int(round(ay + sy * end))), colour, 1, cv2.LINE_8)
            pos += DASH_ON_PX + DASH_OFF_PX


def _object_box_px(obj_box_mm: list[int], frame) -> tuple[int, int, int, int]:
    corners = _px([[obj_box_mm[0], obj_box_mm[1]], [obj_box_mm[2], obj_box_mm[3]]], frame)
    xs, ys = sorted(corners[:, 0].tolist()), sorted(corners[:, 1].tolist())
    return xs[0], ys[0], xs[1], ys[1]


def _draw_dashed_box(img, obj_box_mm: list[int], frame) -> None:
    x0, y0, x1, y1 = _object_box_px(obj_box_mm, frame)
    lim = CROP_PX - 1
    _dashed_rect(img, max(0, x0 - BOX_PAD_PX), max(0, y0 - BOX_PAD_PX),
                 min(lim, x1 + BOX_PAD_PX), min(lim, y1 + BOX_PAD_PX))


def _draw_bar(img, iso_box_mm: list[int]) -> None:
    """The filled 1 m bar at the bottom left of the iso crop."""
    import cv2
    _, _, k = _frame(iso_box_mm)
    length = int(round(BAR_M * 1000.0 * k))
    y1 = CROP_PX - BAR_BOTTOM_PX - 1
    cv2.rectangle(img, (BAR_MARGIN_PX, y1 - BAR_THICK_PX + 1), (BAR_MARGIN_PX + length - 1, y1), INK, -1, cv2.LINE_8)


def draw_vector_ctx(desc: dict) -> np.ndarray:
    import cv2
    img = np.full((CROP_PX, CROP_PX), PAPER, dtype=np.uint8)
    frame = _frame(desc["ctx_box"])
    for wall in desc["context"]["walls"]:
        cv2.fillPoly(img, [_px(wall["outer"], frame).reshape(-1, 1, 2)], WALL_GREY, cv2.LINE_8)
        for hole in wall["holes"]:
            cv2.fillPoly(img, [_px(hole, frame).reshape(-1, 1, 2)], PAPER, cv2.LINE_8)
    for pts in desc["context"]["others"]:
        _polyline(img, _px(pts, frame), OTHER_GREY, OTHER_THICKNESS)
    for pts in desc["strokes"]:
        _polyline(img, _px(pts, frame), INK, OBJECT_THICKNESS)
    _draw_dashed_box(img, desc["object_box"], frame)
    return img


def draw_vector_iso(desc: dict) -> np.ndarray:
    img = np.full((CROP_PX, CROP_PX), PAPER, dtype=np.uint8)
    frame = _frame(desc["iso_box"])
    for pts in desc["strokes"]:
        _polyline(img, _px(pts, frame), INK, OBJECT_THICKNESS)
    _draw_bar(img, desc["iso_box"])
    return img


def vector_description(candidate: dict, context: dict) -> dict:
    """The canonical description of a vector candidate's two crops (what is hashed and what is drawn)."""
    squares = crop_squares(candidate)
    strokes = sorted(_mm_points(s) for s in candidate.get("strokes") or [] if len(s))
    if not strokes:
        raise ValueError(f"candidate {candidate.get('key')!r} has no strokes")
    ctx_m = tuple(v / 1000.0 for v in squares["ctx_box"])
    return {
        "crop_version": CROP_VERSION,
        "kind": "vector",
        "px": CROP_PX,
        "strokes": strokes,
        **squares,
        "context": {"walls": _wall_rings(context.get("walls"), ctx_m), "others": _others_in(context.get("others"),
                                                                                             ctx_m)},
        "question": question_digest(SYMBOL_TASK),
    }


# --------------------------------------------------------------------------
# Raster candidates: pixel crops of the rectified page
# --------------------------------------------------------------------------

def _affine_px(to_px, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = (float(v) for v in to_px)
    return a * x + b * y + c, d * x + e * y + f


def pixel_rect(box_mm: list[int], to_px) -> list[int]:
    """The pixel rectangle [c0, r0, c1, r1) of a page-mm box (bounds of its four mapped corners)."""
    xs, ys = [], []
    for x in (box_mm[0], box_mm[2]):
        for y in (box_mm[1], box_mm[3]):
            px, py = _affine_px(to_px, x / 1000.0, y / 1000.0)
            xs.append(px)
            ys.append(py)
    return [int(math.floor(min(xs))), int(math.floor(min(ys))), int(math.ceil(max(xs))), int(math.ceil(max(ys)))]


def cut(image: np.ndarray, rect: list[int]) -> np.ndarray:
    """``image[r0:r1, c0:c1]`` with white paper where the rectangle leaves the image."""
    c0, r0, c1, r1 = rect
    h, w = image.shape[:2]
    out = np.full((max(1, r1 - r0), max(1, c1 - c0)), PAPER, dtype=np.uint8)
    sc0, sr0, sc1, sr1 = max(0, c0), max(0, r0), min(w, c1), min(h, r1)
    if sc1 > sc0 and sr1 > sr0:
        out[sr0 - r0:sr1 - r0, sc0 - c0:sc1 - c0] = image[sr0:sr1, sc0:sc1]
    return out


def resize_to(arr: np.ndarray, width: int, height: int) -> np.ndarray:
    """Deterministic resize: area averaging when shrinking, bilinear when enlarging."""
    import cv2
    if arr.shape[1] == width and arr.shape[0] == height:
        return arr.copy()
    shrink = arr.shape[1] > width or arr.shape[0] > height
    return cv2.resize(arr, (width, height), interpolation=cv2.INTER_AREA if shrink else cv2.INTER_LINEAR)


def raster_crops(candidate: dict, context: dict) -> tuple[dict, np.ndarray, np.ndarray]:
    """(description, ctx image, iso image) of a raster candidate (pixel crops of the rectified page)."""
    image = np.asarray(context["image"])
    if image.ndim == 3:
        import cv2
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = image.astype(np.uint8)
    to_px = context["to_px"]
    squares = crop_squares(candidate)
    ctx_rect = pixel_rect(squares["ctx_box"], to_px)
    iso_rect = pixel_rect(squares["iso_box"], to_px)
    obj_rect = pixel_rect(squares["object_box"], to_px)
    ctx_src = cut(image, ctx_rect)
    iso_src = cut(image, iso_rect)
    # The object alone: only the pixels inside its box (grown by ISO_MASK_PAD_PX) are kept.
    keep = np.zeros_like(iso_src, dtype=bool)
    r0 = max(0, obj_rect[1] - ISO_MASK_PAD_PX - iso_rect[1])
    r1 = min(iso_src.shape[0], obj_rect[3] + ISO_MASK_PAD_PX - iso_rect[1])
    c0 = max(0, obj_rect[0] - ISO_MASK_PAD_PX - iso_rect[0])
    c1 = min(iso_src.shape[1], obj_rect[2] + ISO_MASK_PAD_PX - iso_rect[0])
    keep[r0:r1, c0:c1] = True
    iso_src = np.where(keep, iso_src, PAPER).astype(np.uint8)
    desc = {
        "crop_version": CROP_VERSION,
        "kind": "raster",
        "px": CROP_PX,
        **squares,
        "ctx_rect_px": ctx_rect,
        "iso_rect_px": iso_rect,
        "object_rect_px": obj_rect,
        "ctx_pixels": array_sha256(ctx_src),
        "iso_pixels": array_sha256(iso_src),
        "question": question_digest(SYMBOL_TASK),
    }
    ctx = resize_to(ctx_src, CROP_PX, CROP_PX)
    _draw_dashed_box(ctx, squares["object_box"], _frame(squares["ctx_box"]))
    iso = resize_to(iso_src, CROP_PX, CROP_PX)
    _draw_bar(iso, squares["iso_box"])
    return desc, ctx, iso


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------

def save_png(arr: np.ndarray, path: Path) -> Path:
    """A grey PNG written by PIL without metadata (no text, time or pHYs chunks), via a temporary file."""
    from PIL import Image
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    Image.fromarray(np.ascontiguousarray(arr, dtype=np.uint8)).save(tmp, format="PNG", optimize=False,
                                                                     compress_level=6)
    tmp.replace(path)
    return path


def crop_names(key: str) -> tuple[str, str]:
    return f"{key}_ctx.png", f"{key}_iso.png"


def render_pair(candidate: dict, context: dict, out_dir: Path, key: str) -> dict:
    """Write ``<out_dir>/<key>_ctx.png`` and ``<key>_iso.png``; return their paths, the input hash and the crop.

    ``out_dir`` is ``<out>/recognition/crops`` (the request lists the images relative to ``<out>/recognition``).
    """
    if context is not None and context.get("image") is not None:
        desc, ctx, iso = raster_crops(candidate, context)
    else:
        desc = vector_description(candidate, context or {})
        ctx, iso = draw_vector_ctx(desc), draw_vector_iso(desc)
    ctx_name, iso_name = crop_names(key)
    out_dir = Path(out_dir)
    ctx_png = save_png(ctx, out_dir / ctx_name)
    iso_png = save_png(iso, out_dir / iso_name)
    crop = {k: desc[k] for k in ("object_box", "ctx_box", "iso_box")}
    crop.update({"units": "mm", "px": CROP_PX, "kind": desc["kind"], "crop_version": CROP_VERSION})
    return {"ctx_png": str(ctx_png), "iso_png": str(iso_png), "input_sha256": canonical_sha256(desc), "crop": crop}
