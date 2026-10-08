"""Colour and neutral-wall checks of the change gate (docs/milestone5.md §4.2 ``colour``, ``neutral``).

What:
- ``colour``: CIELAB (sRGB, D65) mean per region and ΔE76 between the
  reference and test means; global = mean per-pixel ΔE76 over valid pixels
  (no background, no window panes).
- ``neutral``: |ΔC*ab| (change of chroma of the region's mean colour) for the
  wall and ceiling structure regions whose rendered material is
  ``albedo_mode: flat`` (white must stay white; a textured material such as
  tiles or brick may change hue a little without being wrong).

The albedo mode of the rendered wall/ceiling material comes from the scene
manifest (the material records written by the build, area A adds
``albedo_mode``), else from ``wenart.style.vocabulary.MATERIALS``; when
neither names it, the region is skipped as ``albedo_unknown`` (never guessed).

Milestone 10 (docs/milestone10.md §3.3 items 4-5): an exterior view has no room, so the walls are the facade
(``exterior_albedo``: the scene manifest's ``exterior_looks.facade``) and the ceiling region is skipped.

Milestone 10 (docs/milestone10.md §4.1, the style profile of track C): the walls slot may carry a ``colour`` (a
phrase of ``wenart.style.colours``, e.g. "warm greige") and the profile a ``wall_accent``. The wall record of
``structure_albedo`` then holds the expected colour (``colour``, its linear RGB, CIELAB and chroma; the gate
compares the polished walls with the Cycles walls, which show that colour, so the chroma of a coloured wall is
a value to keep, not zero). A paint colour is a flat colour by construction (``COLOUR_FLAT``): such a wall is
measured by ``neutral`` even when the vocabulary does not name the material. An accent wall built from a
textured material makes the walls region ``texture`` in the rooms that have it (``accent``); a colour phrase
nobody knows is listed (``colour_unknown``), never guessed.

Conversions are numpy only (``lab_planes`` uses ``cv2.LUT``, imported
inside); ``lab_to_srgb`` is the exact inverse used by the colour controls
(``controls.py``). The gate runs ``lab_planes`` / ``colour_metrics_layout``
on the valid pixels only (``layout.Layout``); ``region_means`` /
``colour_metrics`` are the same numbers from whole-image masks.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

# sRGB (D65) linear RGB -> XYZ (IEC 61966-2-1) and the D65 reference white.
RGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                       [0.2126729, 0.7151522, 0.0721750],
                       [0.0193339, 0.1191920, 0.9503041]], dtype=np.float64)
XYZ_TO_RGB = np.linalg.inv(RGB_TO_XYZ)
WHITE_D65 = np.array([0.95047, 1.0, 1.08883], dtype=np.float64)
_EPS = (6.0 / 29.0) ** 3
_KAPPA = 3.0 * (6.0 / 29.0) ** 2

WALL_REGION = "struct:walls"
CEILING_REGION = "struct:ceiling"
NEUTRAL_REGIONS = (WALL_REGION, CEILING_REGION)


# --------------------------------------------------------------------------
# Conversions
# --------------------------------------------------------------------------

def srgb_to_linear(v) -> np.ndarray:
    """sRGB-encoded values in 0..1 -> linear light (float64)."""
    v = np.asarray(v, dtype=np.float64)
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(v) -> np.ndarray:
    """Linear light in 0..1 -> sRGB-encoded values (float64, clipped to 0..1 first)."""
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1.0 / 2.4) - 0.055)


_LUT = srgb_to_linear(np.arange(256) / 255.0)
_LUT32 = _LUT.astype(np.float32)


def to_linear(rgb) -> np.ndarray:
    """uint8 RGB -> linear float64 (LUT); float input is taken as sRGB in 0..1."""
    a = np.asarray(rgb)
    if a.dtype == np.uint8:
        return _LUT[a]
    return srgb_to_linear(a)


def to_uint8(linear) -> np.ndarray:
    """Linear RGB -> uint8 sRGB (rounded, clipped)."""
    return np.clip(np.rint(linear_to_srgb(linear) * 255.0), 0, 255).astype(np.uint8)


def _f(t: np.ndarray) -> np.ndarray:
    return np.where(t > _EPS, np.cbrt(t), t / _KAPPA + 4.0 / 29.0)


def _f_inv(t: np.ndarray) -> np.ndarray:
    return np.where(t > 6.0 / 29.0, t ** 3, _KAPPA * (t - 4.0 / 29.0))


def linear_to_lab(lin) -> np.ndarray:
    """Linear sRGB (... x 3) -> CIELAB (D65) float32 (computed in the input's float precision)."""
    lin = np.asarray(lin)
    dt = np.float32 if lin.dtype == np.float32 else np.float64
    m = (RGB_TO_XYZ.T / WHITE_D65).astype(dt)
    xyz = lin.astype(dt, copy=False) @ m
    fx, fy, fz = _f(xyz[..., 0]), _f(xyz[..., 1]), _f(xyz[..., 2])
    return np.stack([116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)], axis=-1).astype(np.float32)


def srgb_to_lab(rgb) -> np.ndarray:
    """uint8 (or 0..1 float) sRGB (... x 3) -> CIELAB (D65) float32 (uint8 input runs in float32)."""
    a = np.asarray(rgb)
    if a.dtype == np.uint8:
        return linear_to_lab(_LUT32[a])
    return linear_to_lab(to_linear(a))


# xyz_j / white_j = sum_i _M32[j, i] * linear_i: the float32 matrix of ``linear_to_lab``, transposed.
_M32 = np.ascontiguousarray((RGB_TO_XYZ.T / WHITE_D65).astype(np.float32).T)


def lab_planes(planes) -> np.ndarray:
    """CIELAB (D65) float32 3 x N of uint8 sRGB planes 3 x N (``layout.Layout.planes``).

    The same conversion as ``srgb_to_lab`` (float32 LUT, the float32 matrix,
    cbrt / linear branch), channel by channel on contiguous rows, without
    BLAS (no threads) and without full-image temporaries.
    """
    import cv2
    p = np.ascontiguousarray(planes, dtype=np.uint8)
    if p.shape[1] == 0:
        return np.zeros((3, 0), dtype=np.float32)
    lin = cv2.LUT(p, _LUT32)                                   # exact table lookup, float32
    f = np.empty_like(lin)
    tmp = np.empty_like(lin[0])
    for j in range(3):
        np.multiply(lin[0], _M32[j, 0], out=f[j])
        np.multiply(lin[1], _M32[j, 1], out=tmp)
        f[j] += tmp
        np.multiply(lin[2], _M32[j, 2], out=tmp)
        f[j] += tmp
    small = f <= _EPS
    t_small = f[small]
    np.cbrt(f, out=f)
    f[small] = t_small / _KAPPA + 4.0 / 29.0
    out = np.empty_like(f)
    np.multiply(f[1], 116.0, out=out[0])
    out[0] -= 16.0
    np.subtract(f[0], f[1], out=out[1])
    out[1] *= 500.0
    np.subtract(f[1], f[2], out=out[2])
    out[2] *= 200.0
    return out


def layout_means(lab_planes_, layout) -> dict:
    """``{region id: [L, a, b] | None}``: mean of each region's slice of a 3 x N Lab array (float64 sums)."""
    out = {}
    for k, rid in enumerate(layout.ids):
        seg = lab_planes_[:, layout.span(k)]
        n = seg.shape[1]
        out[rid] = None if n == 0 else [round(float(x), 4) for x in seg.sum(axis=1, dtype=np.float64) / n]
    return out


def colour_metrics_layout(ref_lab, test_lab, ref_means: dict, layout, min_frac: float) -> tuple[dict, dict]:
    """``colour_metrics`` on 3 x N Lab arrays of the layout's valid pixels (same numbers, no full-image pass)."""
    out: dict = {"global": None, "regions": {}, "skipped": {}}
    if layout.n_valid:
        d = np.subtract(ref_lab, test_lab, dtype=np.float32)
        np.multiply(d, d, out=d)
        de = d[0] + d[1]
        de += d[2]
        np.sqrt(de, out=de)
        out["global"] = round(float(de.mean(dtype=np.float64)), 4)
    test_means = layout_means(test_lab, layout)
    counts = layout.counts()
    total = layout.size
    for k, rid in enumerate(layout.ids):
        if ref_means.get(rid) is None or test_means.get(rid) is None or int(counts[k]) / total < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(delta_e76(ref_means[rid], test_means[rid])), 4)
    return out, test_means


def lab_to_linear(lab) -> np.ndarray:
    """CIELAB (D65) -> linear sRGB float64 (not clipped)."""
    lab = np.asarray(lab, dtype=np.float64)
    fy = (lab[..., 0] + 16.0) / 116.0
    fx = fy + lab[..., 1] / 500.0
    fz = fy - lab[..., 2] / 200.0
    xyz = np.stack([_f_inv(fx), _f_inv(fy), _f_inv(fz)], axis=-1) * WHITE_D65
    return xyz @ XYZ_TO_RGB.T


def lab_to_srgb(lab) -> np.ndarray:
    """CIELAB (D65) -> uint8 sRGB (out-of-gamut values clipped)."""
    return to_uint8(lab_to_linear(lab))


def delta_e76(lab1, lab2) -> np.ndarray:
    """CIE76 colour difference (Euclidean distance in Lab)."""
    d = np.asarray(lab1, dtype=np.float64) - np.asarray(lab2, dtype=np.float64)
    return np.sqrt((d * d).sum(axis=-1))


def chroma(lab) -> np.ndarray:
    """C*ab = sqrt(a*^2 + b*^2)."""
    lab = np.asarray(lab, dtype=np.float64)
    return np.hypot(lab[..., 1], lab[..., 2])


# --------------------------------------------------------------------------
# Region means and metrics
# --------------------------------------------------------------------------

def region_labels(region_masks: dict, region_ids: Iterable[str], valid) -> np.ndarray:
    """int32 H x W: the position of each valid pixel's region in ``region_ids``, -1 elsewhere.

    The regions of ``views.regions`` are disjoint (one index per pixel;
    structure splits index-0 pixels by the normal); on an overlap the later
    region wins.
    """
    v = np.asarray(valid, dtype=bool)
    labels = np.full(v.shape, -1, dtype=np.int32)
    for k, rid in enumerate(region_ids):
        labels[np.asarray(region_masks[rid], dtype=bool) & v] = k
    return labels


def _label_means(lab, labels, n: int) -> tuple[np.ndarray, np.ndarray]:
    """``(counts n, means n x 3)`` of Lab per label (bincount)."""
    flat = np.asarray(labels).ravel()
    sel = flat >= 0
    idx = flat[sel]
    counts = np.bincount(idx, minlength=n)[:n]
    lab2 = np.asarray(lab).reshape(-1, 3)[sel].astype(np.float64)
    sums = np.stack([np.bincount(idx, weights=lab2[:, c], minlength=n)[:n] for c in range(3)], axis=1)
    means = sums / np.maximum(counts, 1)[:, None]
    return counts, means


def region_means(lab, region_masks: dict, region_ids: Iterable[str], valid, labels=None) -> dict:
    """``{region id: [L, a, b] | None}`` mean colour over the region's valid pixels.

    ``labels`` = ``region_labels(region_masks, region_ids, valid)`` when the
    caller has it already (same order of ``region_ids``).
    """
    ids = list(region_ids)
    if labels is None:
        labels = region_labels(region_masks, ids, valid)
    counts, means = _label_means(lab, labels, len(ids))
    return {rid: None if counts[k] == 0 else [round(float(x), 4) for x in means[k]] for k, rid in enumerate(ids)}


def colour_metrics(ref_lab, test_lab, ref_means: dict, region_masks: dict, region_ids: Iterable[str], valid,
                   min_frac: float, labels=None) -> tuple[dict, dict]:
    """``({"global", "regions", "skipped"}, test_means)``: ΔE76 of region means, global mean per-pixel ΔE76."""
    v = np.asarray(valid, dtype=bool)
    total = v.size
    out: dict = {"global": None, "regions": {}, "skipped": {}}
    if v.any():
        d = np.asarray(ref_lab, dtype=np.float32)[v] - np.asarray(test_lab, dtype=np.float32)[v]
        out["global"] = round(float(np.sqrt((d * d).sum(axis=1)).mean(dtype=np.float64)), 4)
    ids = list(region_ids)
    if labels is None:
        labels = region_labels(region_masks, ids, v)
    counts, means = _label_means(test_lab, labels, len(ids))
    test_means = {rid: None if counts[k] == 0 else [round(float(x), 4) for x in means[k]] for k, rid in enumerate(ids)}
    for k, rid in enumerate(ids):
        n = int(counts[k])
        if ref_means.get(rid) is None or test_means.get(rid) is None or n / total < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(delta_e76(ref_means[rid], test_means[rid])), 4)
    return out, test_means


def neutral_metrics(ref_means: dict, test_means: dict, region_pixels: dict, total_px: int, albedo: dict,
                    min_frac: float) -> dict:
    """``{"global": None, "regions": {id: |ΔC*ab|}, "skipped", "albedo"}`` for the wall/ceiling regions.

    Only regions whose rendered material is ``albedo_mode: flat`` are
    measured; others are skipped as ``albedo_texture`` or ``albedo_unknown``.
    ``region_pixels`` are the valid pixel counts used for ``min_frac``.
    """
    out: dict = {"global": None, "regions": {}, "skipped": {}, "albedo": albedo}
    for rid in NEUTRAL_REGIONS:
        if rid not in region_pixels:
            continue
        mode = (albedo.get(rid) or {}).get("albedo_mode")
        if mode != "flat":
            out["skipped"][rid] = "albedo_texture" if mode == "texture" else "albedo_unknown"
            continue
        ref, test = ref_means.get(rid), test_means.get(rid)
        if ref is None or test is None or region_pixels[rid] / float(total_px) < float(min_frac):
            out["skipped"][rid] = "too_small"
            continue
        out["regions"][rid] = round(float(abs(chroma(test) - chroma(ref))), 4)
    return out


# --------------------------------------------------------------------------
# Albedo mode of the rendered wall/ceiling materials
# --------------------------------------------------------------------------

def _vocabulary_mode(slug: Optional[str]) -> Optional[str]:
    if not slug:
        return None
    try:
        from wenart.style import vocabulary
    except ImportError:          # pragma: no cover - the package always has it
        return None
    entry = vocabulary.MATERIALS.get(slug) or {}
    return entry.get("albedo_mode")


#: Materials whose look is the paint colour itself (docs/milestone10.md §1.4): flat by construction.
COLOUR_FLAT = ("paint", "lime_plaster", "microcement", "venetian_plaster")


def expected_colour(phrase) -> Optional[dict]:
    """``{"name", "linear_rgb", "lab", "chroma"}`` of a style colour phrase ("warm greige") through
    ``wenart.style.colours.linear_rgb``; None for no phrase, a phrase the table does not know, or a colour module
    that is not filled yet (the caller lists ``colour_unknown``)."""
    if not phrase or not isinstance(phrase, str):
        return None
    try:
        from wenart.style import colours as COL
        rgb = [float(v) for v in COL.linear_rgb(phrase)]
    except (ImportError, AttributeError, KeyError, ValueError, TypeError):
        return None
    lab = linear_to_lab(np.asarray(rgb, dtype=np.float64))
    return {"name": phrase, "linear_rgb": [round(v, 5) for v in rgb], "lab": [round(float(v), 3) for v in lab],
            "chroma": round(float(np.hypot(lab[1], lab[2])), 3)}


def _mode_of(materials: dict, slug: Optional[str], name: Optional[str] = None,
             colour: Optional[dict] = None) -> tuple[Optional[str], Optional[str]]:
    """``(albedo_mode, source)`` of a slug: the scene manifest's material record, the vocabulary, else ``flat``
    for a ``COLOUR_FLAT`` material that has a known colour."""
    mode, source = _record_mode(materials, slug, name)
    if mode is None:
        mode = _vocabulary_mode(slug)
        source = "vocabulary.MATERIALS" if mode else None
    if mode is None and slug in COLOUR_FLAT and colour is not None:
        mode, source = "flat", "gate.colour.COLOUR_FLAT"
    return mode, source


def _accent_record(scene: dict, profile: dict, room_id: Optional[str], materials: dict) -> Optional[dict]:
    """The profile's accent wall and whether this room has it. The scene manifest marks an accent wall object
    ``accent: true`` with the rooms that carry the accent face in ``room_ids`` and the material slot it uses in
    ``accent_material`` (track F's contract, ``wenart/blender/schemas.py``): the room has the accent when it is
    in such an object's ``room_ids``. The mode of the accent comes from the material record of that slot, else
    of the profile's material. None without an accent wall."""
    acc = profile.get("wall_accent")
    if not isinstance(acc, dict) or not acc.get("material"):
        return None
    slug = acc["material"]
    colour = expected_colour(acc.get("colour"))
    in_room, slot_name = False, None
    for obj in scene.get("objects") or []:
        if obj.get("kind") == "wall" and obj.get("accent") and room_id is not None \
                and room_id in (obj.get("room_ids") or []):
            in_room, slot_name = True, obj.get("accent_material")
            break
    mode, source = _mode_of(materials, slug, slot_name, colour)
    return {"material": slug, "colour": acc.get("colour"), "albedo_mode": mode, "source": source,
            "in_room": in_room, "slot": slot_name}


def _record_mode(materials: dict, slug: Optional[str], name: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """``(albedo_mode, source)`` from the scene manifest's material records (by record name, then by slug)."""
    if name and isinstance(materials.get(name), dict) and materials[name].get("albedo_mode"):
        return materials[name]["albedo_mode"], f"scene manifest materials.{name}"
    for key, rec in materials.items():
        if isinstance(rec, dict) and rec.get("slug") == slug and rec.get("albedo_mode"):
            return rec["albedo_mode"], f"scene manifest materials.{key}"
    return None, None


#: Exterior facade slugs (docs/milestone10.md §1.4, §4.8) and whether their render is a flat colour (white must
#: stay white) or a texture (a brick or a cladding may shift a little). A slug in neither list is not guessed.
EXTERIOR_FLAT = ("render", "fibre_cement", "paint", "plaster_exterior", "microcement")
EXTERIOR_TEXTURE_PREFIXES = ("brick", "stone", "wood", "slat", "cladding", "concrete_exposed")


def is_exterior(scene_manifest: Optional[dict], camera: Optional[str] = None, room_id: Optional[str] = None) -> bool:
    """True for a camera of kind ``exterior`` in the scene manifest (Milestone 10: no room, no level); without a
    kind, a camera named ``ext_<n>`` that has no room."""
    cam = next((c for c in (scene_manifest or {}).get("cameras") or [] if c.get("name") == camera), None)
    if cam is not None and cam.get("kind"):
        return cam["kind"] == "exterior"
    return not (room_id or (cam or {}).get("room_id")) and str(camera or "").startswith("ext_")


def exterior_albedo(scene_manifest: Optional[dict]) -> dict:
    """``structure_albedo`` of an exterior view: the walls are the facade (the scene manifest's
    ``exterior_looks.facade``: a render in a colour is flat, a brick, stone or wood cladding is a texture; a slug
    nobody classified is ``albedo_unknown``, never guessed); there is no ceiling (the region is the soffit)."""
    scene = scene_manifest or {}
    look = (scene.get("exterior_looks") or {}).get("facade") or {}
    slug = look.get("material")
    materials = scene.get("materials") or {}
    mode, source = _record_mode(materials, slug, None)
    if mode is None and slug:
        if slug in EXTERIOR_FLAT:
            mode, source = "flat", "gate.colour.EXTERIOR_FLAT"
        elif any(str(slug).startswith(p) for p in EXTERIOR_TEXTURE_PREFIXES):
            mode, source = "texture", "gate.colour.EXTERIOR_TEXTURE_PREFIXES"
        else:
            mode = _vocabulary_mode(slug)
            source = "vocabulary.MATERIALS" if mode else None
    return {WALL_REGION: {"material": slug, "albedo_mode": mode, "source": source,
                          "slot": "exterior_looks.facade", "wet": None},
            CEILING_REGION: {"material": None, "albedo_mode": None, "source": None,
                             "slot": "exterior view: no ceiling", "wet": None}}


def structure_albedo(scene_manifest: Optional[dict], room_id: Optional[str], exterior: bool = False) -> dict:
    """``{"struct:walls"|"struct:ceiling": {"material", "albedo_mode", "source", "wet"}}`` for a camera's room.

    Walls: the profile slot ``wet_walls`` in a wet room (the room's floor or
    ceiling object says ``wet: true``), else ``walls``, of the rendered style
    profile (``scene_manifest["style_profile"]``). Ceiling: the material of
    the room's ceiling object, else the profile's ``ceiling`` slot. The mode
    comes from the material record, else the vocabulary, else None.
    ``exterior`` (Milestone 10): the facade's look instead (``exterior_albedo``).
    """
    if exterior:
        return exterior_albedo(scene_manifest)
    scene = scene_manifest or {}
    profile = scene.get("style_profile") or {}
    materials = scene.get("materials") or {}
    wet = None
    ceiling_name = None
    for obj in scene.get("objects") or []:
        if room_id is None or obj.get("element_id") != room_id or obj.get("kind") not in ("floor", "ceiling"):
            continue
        if obj.get("wet") is not None and wet is None:
            wet = bool(obj.get("wet"))
        if obj.get("kind") == "ceiling" and ceiling_name is None:
            ceiling_name = obj.get("material")
    out = {}
    slot = "wet_walls" if wet else "walls"
    wall_slot = profile.get(slot) or profile.get("walls") or {}
    wall_slug = wall_slot.get("material")
    wall_colour = expected_colour(wall_slot.get("colour"))
    ceiling_slug = None
    if ceiling_name:
        rec = materials.get(ceiling_name) or {}
        ceiling_slug = rec.get("slug") or ceiling_name.split("__")[0]
    if not ceiling_slug:
        ceiling_slug = (profile.get("ceiling") or {}).get("material")
    for rid, slug, name, where in ((WALL_REGION, wall_slug, None, f"style_profile.{slot}"),
                                   (CEILING_REGION, ceiling_slug, ceiling_name,
                                    "ceiling object" if ceiling_name else "style_profile.ceiling")):
        mode, source = _mode_of(materials, slug, name, wall_colour if rid == WALL_REGION else None)
        out[rid] = {"material": slug, "albedo_mode": mode, "source": source, "slot": where, "wet": wet}
    walls = out[WALL_REGION]
    if wall_slot.get("colour"):
        walls["colour"] = wall_colour["name"] if wall_colour else wall_slot["colour"]
        if wall_colour:
            walls.update(colour_linear_rgb=wall_colour["linear_rgb"], colour_lab=wall_colour["lab"],
                         colour_chroma=wall_colour["chroma"])
        else:
            walls["colour_unknown"] = True
    accent = _accent_record(scene, profile, room_id, materials) if not wet else None
    if accent is not None:
        walls["accent"] = accent
        if accent["in_room"] and accent["albedo_mode"] != "flat":
            # One wall of this room is textured (or its mode is not known): the region is not a flat colour.
            walls["albedo_mode"] = "texture" if accent["albedo_mode"] == "texture" else None
            walls["source"] = "wall_accent in this room (" + (accent["source"] or "mode unknown") + ")"
    return out
