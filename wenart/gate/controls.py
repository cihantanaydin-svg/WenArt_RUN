"""Benign and negative controls for the gate calibration (docs/milestone5.md §4.3).

What: CPU edits of a Cycles render with known meaning.

- Benign (the gate must accept them): exposure +-0.3 EV and white balance
  x(1.03, 1, 0.97) in linear light, Gaussian blur sigma 1, JPEG quality 75,
  unsharp mask (sigma 2, amount 0.5), local contrast x1.5 (sigma 6: crisper
  texture, as a polish renders grout and plank seams; added after review
  finding G2), Gaussian noise sigma 3/255.
- Negatives (the gate must reject them): on one object (cut by its index
  mask) shift 6 / 12 / 25 px, scale x1.04 / x1.08 / x1.15 (about the bottom
  centre of its box), rotation 2 deg (about the box centre), erase; the hole
  is filled with ``cv2.inpaint`` (TELEA) and the moved object is pasted only
  where no nearer object covers it (depth test). A window/door crop from
  another view pasted onto a wall region. Colour: white balance R x1.15 /
  B x0.85, wall region b* +10, floor region L* -15.

Every generator is deterministic (the noise uses a seeded generator; the
shift direction, the paste position and the anchors follow fixed rules) and
changes only the pixels it names: an object edit changes the object's mask
grown by 1 px plus the pasted footprint, a region colour edit only that
region. ``cv2.inpaint`` changes only the pixels of its mask.

Small negatives (used for the threshold proposal, §4.3): shift 6 and 12 px,
scale x1.04 and x1.08, rotation 2 deg and the three colour edits; the others
are gross.
"""
from __future__ import annotations

import hashlib
import io
from typing import Optional

import numpy as np

from wenart.gate import colour as C

EXPOSURE_EV = 0.3
WB_BENIGN = (1.03, 1.0, 0.97)
WB_NEGATIVE = (1.15, 1.0, 0.85)
BLUR_SIGMA = 1.0
JPEG_QUALITY = 75
UNSHARP_SIGMA = 2.0
UNSHARP_AMOUNT = 0.5
LOCAL_CONTRAST_GAIN = 1.5       # crisper texture (review finding G2: grout / plank seams)
LOCAL_CONTRAST_SIGMA = 6.0
NOISE_SIGMA = 3.0               # in 0..255 units (3/255)
SHIFTS_PX = (6, 12, 25)
SCALES = (1.04, 1.08, 1.15)
ROTATION_DEG = 2.0
WALL_DB = 10.0
FLOOR_DL = -15.0
INPAINT_RADIUS = 3
HOLE_GROW_PX = 1                # the hole is the object mask grown by 1 px (anti-aliased rim)
PASTE_MAX_FRAC = (0.35, 0.5)    # pasted crop at most 35 % of W and 50 % of H
PASTE_STEP_FRAC = 0.05
PASTE_MIN_COVER = 0.95          # share of the crop footprint that must lie on the wall region
PASTE_SCALES = (1.0, 0.75, 0.5)

SMALL = {("shift", 6), ("shift", 12), ("scale", 1.04), ("scale", 1.08), ("rotate", 2.0),
         ("white_balance_strong", "1.15,1,0.85"), ("wall_b", 10.0), ("floor_L", -15.0)}


def seed_for(*parts) -> int:
    """A stable 32-bit seed from text parts (sha1), so every control is reproducible."""
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


def is_small(control: str, magnitude) -> bool:
    """True for the small negatives of §4.3 (the basis of the threshold proposal)."""
    return (control, magnitude) in SMALL


# --------------------------------------------------------------------------
# Benign
# --------------------------------------------------------------------------

def exposure(rgb, ev: float) -> np.ndarray:
    """Exposure change of ``ev`` stops in linear light."""
    return C.to_uint8(C.to_linear(rgb) * (2.0 ** float(ev)))


def white_balance(rgb, gains) -> np.ndarray:
    """Per-channel gains in linear light (R, G, B)."""
    return C.to_uint8(C.to_linear(rgb) * np.asarray(gains, dtype=np.float64))


def blur(rgb, sigma: float = BLUR_SIGMA) -> np.ndarray:
    """Gaussian blur."""
    import cv2
    return cv2.GaussianBlur(np.ascontiguousarray(rgb), (0, 0), float(sigma))


def jpeg(rgb, quality: int = JPEG_QUALITY) -> np.ndarray:
    """JPEG round trip at ``quality`` (Pillow, 4:2:0 subsampling as Pillow's default)."""
    from PIL import Image
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(rgb)).save(buf, format="JPEG", quality=int(quality))
    buf.seek(0)
    with Image.open(buf) as img:
        return np.array(img.convert("RGB"), dtype=np.uint8)


def unsharp(rgb, sigma: float = UNSHARP_SIGMA, amount: float = UNSHARP_AMOUNT) -> np.ndarray:
    """Unsharp mask: img + amount * (img - blur(img))."""
    import cv2
    a = np.asarray(rgb, dtype=np.float32)
    b = cv2.GaussianBlur(a, (0, 0), float(sigma))
    return np.clip(np.rint(a + float(amount) * (a - b)), 0, 255).astype(np.uint8)


def local_contrast(rgb, gain: float = LOCAL_CONTRAST_GAIN, sigma: float = LOCAL_CONTRAST_SIGMA) -> np.ndarray:
    """Local contrast x ``gain``: blur + gain * (img - blur(img)) with a wide blur (``sigma`` 6 px).

    Stands for a polish that renders the texture of floors and walls crisper
    (plank seams, tile grout) without moving anything.
    """
    import cv2
    a = np.asarray(rgb, dtype=np.float32)
    b = cv2.GaussianBlur(a, (0, 0), float(sigma))
    return np.clip(np.rint(b + float(gain) * (a - b)), 0, 255).astype(np.uint8)


def noise(rgb, sigma: float = NOISE_SIGMA, seed: int = 0) -> np.ndarray:
    """Additive Gaussian noise (sigma in 0..255 units) from a seeded generator."""
    rng = np.random.default_rng(int(seed))
    n = rng.normal(0.0, float(sigma), np.asarray(rgb).shape)
    return np.clip(np.rint(np.asarray(rgb, dtype=np.float64) + n), 0, 255).astype(np.uint8)


def benign_controls(rgb, seed: int = 0) -> list[dict]:
    """``[{"control", "magnitude", "image"}]`` of the seven benign edits (exposure in both directions)."""
    return [
        {"control": "exposure", "magnitude": EXPOSURE_EV, "image": exposure(rgb, EXPOSURE_EV)},
        {"control": "exposure", "magnitude": -EXPOSURE_EV, "image": exposure(rgb, -EXPOSURE_EV)},
        {"control": "white_balance", "magnitude": "1.03,1,0.97", "image": white_balance(rgb, WB_BENIGN)},
        {"control": "blur", "magnitude": BLUR_SIGMA, "image": blur(rgb)},
        {"control": "jpeg", "magnitude": JPEG_QUALITY, "image": jpeg(rgb)},
        {"control": "unsharp", "magnitude": UNSHARP_AMOUNT, "image": unsharp(rgb)},
        {"control": "local_contrast", "magnitude": LOCAL_CONTRAST_GAIN, "image": local_contrast(rgb)},
        {"control": "noise", "magnitude": NOISE_SIGMA, "image": noise(rgb, NOISE_SIGMA, seed)},
    ]


# --------------------------------------------------------------------------
# Object edits
# --------------------------------------------------------------------------

def _grow(mask, r: int) -> np.ndarray:
    import cv2
    m = np.asarray(mask, dtype=bool)
    if r <= 0:
        return m.copy()
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0


def remove_object(rgb, mask) -> np.ndarray:
    """The image with the object's pixels (mask grown by 1 px) filled by ``cv2.inpaint`` TELEA."""
    import cv2
    hole = _grow(mask, HOLE_GROW_PX).astype(np.uint8)
    return cv2.inpaint(np.ascontiguousarray(rgb), hole, INPAINT_RADIUS, cv2.INPAINT_TELEA)


def _paste(base, src_rgb, ys, xs, ty, tx, src_depth, index, depth_mm, pass_index) -> np.ndarray:
    """Copy src pixels (ys, xs) to (ty, tx) where they are inside the image and no nearer object covers them."""
    h, w = base.shape[:2]
    inside = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
    ys, xs, ty, tx, src_depth = ys[inside], xs[inside], ty[inside], tx[inside], src_depth[inside]
    tgt_index = index[ty, tx]
    tgt_depth = depth_mm[ty, tx].astype(np.int64)
    occluded = (tgt_index > 0) & (tgt_index != pass_index) & (tgt_depth > 0) & (tgt_depth < src_depth)
    out = base.copy()
    keep = ~occluded
    out[ty[keep], tx[keep]] = src_rgb[ys[keep], xs[keep]]
    return out


def object_box(mask) -> list[int]:
    """``[x0, y0, x1, y1]`` (x1/y1 exclusive) of a non-empty mask."""
    m = np.asarray(mask, dtype=bool)
    rows = np.flatnonzero(m.any(axis=1))
    cols = np.flatnonzero(m.any(axis=0))
    if rows.size == 0:
        raise ValueError("empty object mask")
    return [int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1]


def shift_direction(mask, width: int) -> int:
    """+1 (right) when the object's box centre is in the left half of the image, else -1."""
    x0, _y0, x1, _y1 = object_box(mask)
    return 1 if (x0 + x1) / 2.0 < width / 2.0 else -1


def shift_object(rgb, index, depth_mm, pass_index: int, px: int) -> np.ndarray:
    """The object moved ``px`` pixels horizontally (towards the wider side), hole inpainted."""
    rgb = np.asarray(rgb)
    index = np.asarray(index)
    depth_mm = np.asarray(depth_mm)
    mask = index == int(pass_index)
    dx = int(px) * shift_direction(mask, rgb.shape[1])
    base = remove_object(rgb, mask)
    ys, xs = np.nonzero(mask)
    return _paste(base, rgb, ys, xs, ys, xs + dx, depth_mm[ys, xs].astype(np.int64), index, depth_mm,
                  int(pass_index))


def warp_object(rgb, index, depth_mm, pass_index: int, scale: float = 1.0, angle_deg: float = 0.0) -> np.ndarray:
    """The object scaled about its box's bottom centre (scale) or rotated about its box centre (angle)."""
    import cv2
    rgb = np.asarray(rgb)
    index = np.asarray(index)
    depth_mm = np.asarray(depth_mm)
    h, w = rgb.shape[:2]
    mask = index == int(pass_index)
    x0, y0, x1, y1 = object_box(mask)
    cx = (x0 + x1 - 1) / 2.0
    # Scaling keeps the object standing where it stands (bottom centre); rotation turns it about its centre.
    centre = (cx, float(y1 - 1)) if angle_deg == 0.0 else (cx, (y0 + y1 - 1) / 2.0)
    m = cv2.getRotationMatrix2D(centre, float(angle_deg), float(scale))
    warped = cv2.warpAffine(np.ascontiguousarray(rgb), m, (w, h), flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REPLICATE)
    wmask = cv2.warpAffine(mask.astype(np.uint8), m, (w, h), flags=cv2.INTER_NEAREST) > 0
    src_depth = np.where(mask, depth_mm, 0).astype(np.float32)
    wdepth = cv2.warpAffine(src_depth, m, (w, h), flags=cv2.INTER_NEAREST)
    base = remove_object(rgb, mask)
    ty, tx = np.nonzero(wmask)
    return _paste(base, warped, ty, tx, ty, tx, wdepth[ty, tx].astype(np.int64), index, depth_mm, int(pass_index))


def erase_object(rgb, index, pass_index: int) -> np.ndarray:
    """The object removed (inpainted)."""
    return remove_object(rgb, np.asarray(index) == int(pass_index))


# --------------------------------------------------------------------------
# Paste a window/door crop onto a wall
# --------------------------------------------------------------------------

def crop_of(rgb, index, pass_index: int) -> tuple[np.ndarray, np.ndarray]:
    """``(crop_rgb, crop_mask)`` of one indexed element in its box."""
    mask = np.asarray(index) == int(pass_index)
    x0, y0, x1, y1 = object_box(mask)
    return np.asarray(rgb)[y0:y1, x0:x1].copy(), mask[y0:y1, x0:x1].copy()


def paste_position(wall_mask, crop_mask, step: tuple[int, int],
                   min_cover: float = PASTE_MIN_COVER) -> Optional[tuple[int, int, float]]:
    """``(x, y, cover)`` of the grid position where the crop footprint lies best on the wall (None if < min_cover).

    Best = the largest cover; ties go to the position whose centre is
    nearest the wall region's centroid, then the lowest y, then the lowest x
    (deterministic, and the crop lands in the middle of the wall).
    """
    wall = np.asarray(wall_mask, dtype=bool)
    cm = np.asarray(crop_mask, dtype=bool)
    h, w = wall.shape
    ch, cw = cm.shape
    n = int(cm.sum())
    if n == 0 or ch > h or cw > w or not wall.any():
        return None
    ys, xs = np.nonzero(wall)
    cy, cx = float(ys.mean()), float(xs.mean())
    best, best_key = None, None
    for y in range(0, h - ch + 1, max(1, step[1])):
        for x in range(0, w - cw + 1, max(1, step[0])):
            cover = float(wall[y:y + ch, x:x + cw][cm].sum()) / n
            if cover < min_cover:
                continue
            key = (-round(cover, 6), (x + cw / 2.0 - cx) ** 2 + (y + ch / 2.0 - cy) ** 2, y, x)
            if best_key is None or key < best_key:
                best, best_key = (x, y, cover), key
    return best


def paste_crop(rgb, wall_mask, crop_rgb, crop_mask) -> Optional[tuple[np.ndarray, dict]]:
    """``(image, info)`` with the crop pasted on the wall region, or None when it fits nowhere.

    The crop is scaled to at most 35 % of W and 50 % of H (never enlarged),
    then tried at 1, 0.75 and 0.5 of that size on a 5 % grid.
    """
    import cv2
    rgb = np.asarray(rgb)
    h, w = rgb.shape[:2]
    crop_rgb = np.asarray(crop_rgb)
    crop_mask = np.asarray(crop_mask, dtype=bool)
    ch, cw = crop_mask.shape
    base_scale = min(1.0, PASTE_MAX_FRAC[0] * w / cw, PASTE_MAX_FRAC[1] * h / ch)
    step = (max(1, int(round(PASTE_STEP_FRAC * w))), max(1, int(round(PASTE_STEP_FRAC * h))))
    for factor in PASTE_SCALES:
        s = base_scale * factor
        size = (max(1, int(round(cw * s))), max(1, int(round(ch * s))))
        c_rgb = cv2.resize(np.ascontiguousarray(crop_rgb), size, interpolation=cv2.INTER_AREA)
        c_mask = cv2.resize(crop_mask.astype(np.uint8), size, interpolation=cv2.INTER_NEAREST) > 0
        pos = paste_position(wall_mask, c_mask, step)
        if pos is None:
            continue
        x, y, cover = pos
        out = rgb.copy()
        region = out[y:y + size[1], x:x + size[0]]
        region[c_mask] = c_rgb[c_mask]
        return out, {"box": [x, y, x + size[0], y + size[1]], "scale": round(s, 4), "cover": round(cover, 4)}
    return None


# --------------------------------------------------------------------------
# Colour edits
# --------------------------------------------------------------------------

def lab_edit(rgb, mask, d_l: float = 0.0, d_a: float = 0.0, d_b: float = 0.0) -> np.ndarray:
    """Shift L*, a*, b* of the pixels in ``mask`` (others untouched)."""
    out = np.asarray(rgb).copy()
    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return out
    lab = C.srgb_to_lab(out[m]).astype(np.float64)
    lab[:, 0] += float(d_l)
    lab[:, 1] += float(d_a)
    lab[:, 2] += float(d_b)
    out[m] = C.lab_to_srgb(lab)
    return out


# --------------------------------------------------------------------------
# All negatives of one view
# --------------------------------------------------------------------------

def object_negatives(rgb, index, depth_mm, pass_index: int, object_id: str) -> list[dict]:
    """Shift, scale, rotation and erase of one object: ``[{"control", "magnitude", "object", "image"}]``."""
    out = []
    for px in SHIFTS_PX:
        out.append({"control": "shift", "magnitude": px, "object": object_id,
                    "image": shift_object(rgb, index, depth_mm, pass_index, px)})
    for s in SCALES:
        out.append({"control": "scale", "magnitude": s, "object": object_id,
                    "image": warp_object(rgb, index, depth_mm, pass_index, scale=s)})
    out.append({"control": "rotate", "magnitude": ROTATION_DEG, "object": object_id,
                "image": warp_object(rgb, index, depth_mm, pass_index, angle_deg=ROTATION_DEG)})
    out.append({"control": "erase", "magnitude": None, "object": object_id,
                "image": erase_object(rgb, index, pass_index)})
    return out


def view_negatives(rgb, region_masks: dict, donor: Optional[dict] = None) -> list[dict]:
    """Paste (when a donor crop fits a wall) and the three colour edits of one view.

    ``donor`` = ``{"rgb", "mask", "camera", "object"}`` (a window/door crop of
    another view). A control that cannot be made (no wall, no floor, no
    fitting position) is returned with ``image: None`` and a ``skipped`` text.
    """
    out = []
    walls = region_masks.get("struct:walls")
    floor = region_masks.get("struct:floor")
    if donor is None or walls is None:
        out.append({"control": "paste", "magnitude": None, "object": None, "image": None,
                    "skipped": "no donor crop" if donor is None else "no wall region"})
    else:
        made = paste_crop(rgb, walls, donor["rgb"], donor["mask"])
        if made is None:
            out.append({"control": "paste", "magnitude": None, "object": donor.get("object"), "image": None,
                        "skipped": "the crop fits on no wall position"})
        else:
            image, info = made
            out.append({"control": "paste", "magnitude": info["scale"], "object": donor.get("object"),
                        "image": image, "info": dict(info, donor_camera=donor.get("camera"))})
    out.append({"control": "white_balance_strong", "magnitude": "1.15,1,0.85", "object": None,
                "image": white_balance(rgb, WB_NEGATIVE)})
    if walls is None:
        out.append({"control": "wall_b", "magnitude": WALL_DB, "object": None, "image": None,
                    "skipped": "no wall region"})
    else:
        out.append({"control": "wall_b", "magnitude": WALL_DB, "object": "struct:walls",
                    "image": lab_edit(rgb, walls, d_b=WALL_DB)})
    if floor is None:
        out.append({"control": "floor_L", "magnitude": FLOOR_DL, "object": None, "image": None,
                    "skipped": "no floor region"})
    else:
        out.append({"control": "floor_L", "magnitude": FLOOR_DL, "object": "struct:floor",
                    "image": lab_edit(rgb, floor, d_l=FLOOR_DL)})
    return out
