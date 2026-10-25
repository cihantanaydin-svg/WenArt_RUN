"""A tasteful furniture selection (25 Oct 2026, user: "there is no taste in the furniture selection; make something to
develop a tasteful selection of furniture, search the internet if needed to see what is tasteful").

What designers do (interior design rules, e.g. the 60-30-10 rule and the wood-tone rules of thumb: one dominant wood
tone, usually the floor's, repeated across the room, with at most one contrasting tone repeated in a few pieces; one
metal finish per room; the colours of the room from a palette, loud colours only as small accents): a room's pieces
look chosen together.

What this module does (pure; numpy and Pillow when they are there):

- ``glb_palette(path)``: the materials of a library model with their colours (base colour factor x the mean colour of
  its base colour texture), metalness and surface share (triangle areas from the GLB's buffers; the bounding boxes
  without numpy), and their kind (wood, metal, fabric, glass, stone, other) from the material name, else from the
  colour (a brown textured material is wood) and the metalness.
- ``attributes(palette)``: the model's ``wood_tone`` (light / medium / dark by the CIE L* of its wood), ``metal``
  (black / brass / silver), its ``main`` colour (the largest non-glass surface) and ``fabric`` colour, as Lab.
- ``TasteCache(assets_dir)``: the attributes of every model the fit looks at, computed once from
  ``<assets>/models/...`` and kept in ``<assets>/taste/attributes.json``.
- ``targets(style)``: the project's wood tone (the style's furniture wood, else its floor), its metal (the style's
  furniture metal, else the window frames' finish when it is a metal colour) and its palette (the style's fabric and
  accent colours).
- ``steps(attrs, room, target)``: how far a model is from the room's set: 0 fits; a second wood tone is allowed once
  (the contrast), a third or a light-dark jump costs more; a second metal finish costs; a loud colour that is not in
  the palette costs. The fit adds ``TASTE_STEP`` size steps per taste step to its rank (``fit.rank_key``) and fits
  the anchors of a room first, so the side tables follow the sofa and the nightstands the bed.
"""
from __future__ import annotations

import io
import json
import math
import struct
from pathlib import Path
from typing import Optional

TASTE_STEP = 2                       # rank size steps per taste step (2 x 5 cm)
ANCHOR_ORDER = ("sofa_corner", "sofa", "bed_double", "bed_single", "table_dining", "kitchen_island", "desk",
                "wardrobe", "sideboard", "tv_unit", "dresser", "bookshelf", "armchair", "table_coffee", "chair",
                "nightstand", "side_table", "console_table", "bench", "ottoman", "floor_lamp")
WOOD_WORDS = ("wood", "oak", "walnut", "timber", "teak", "pine", "ash", "birch", "beech", "maple", "cherry", "veneer",
              "plywood", "bamboo", "acacia", "mahogany", "rosewood", "elm", "holz", "madera", "legno")
METAL_WORDS = ("metal", "steel", "iron", "chrome", "brass", "gold", "alumin", "bronze", "copper", "nickel", "inox",
               "silver")
FABRIC_WORDS = ("fabric", "cloth", "textile", "linen", "velvet", "cushion", "upholst", "leather", "boucle", "cotton",
                "wool", "felt", "tweed", "suede", "seat", "pillow")
GLASS_WORDS = ("glass", "mirror", "crystal", "acrylic", "transparent")
STONE_WORDS = ("marble", "stone", "granite", "concrete", "terrazzo", "travertine", "ceramic")
TONES = ("light", "medium", "dark")
LOUD_CHROMA = 38.0                  # a colour this saturated (CIE C*) is an accent, not a base


# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------

def _lin(c: float) -> float:
    c = max(0.0, min(1.0, float(c)))
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(c: float) -> float:
    c = max(0.0, min(1.0, float(c)))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lab(rgb) -> tuple[float, float, float]:
    """CIE Lab (D65) of an sRGB colour in 0..1 (or 0..255)."""
    r, g, b = (float(v) for v in rgb[:3])
    if max(r, g, b) > 1.0:
        r, g, b = r / 255.0, g / 255.0, b / 255.0
    r, g, b = _lin(r), _lin(g), _lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def chroma(lab_) -> float:
    return math.hypot(lab_[1], lab_[2])


def hue(lab_) -> float:
    return math.degrees(math.atan2(lab_[2], lab_[1])) % 360.0


def tone_of(lab_) -> str:
    return "light" if lab_[0] >= 62.0 else ("dark" if lab_[0] < 42.0 else "medium")


def metal_of(lab_, rgb_lin_mean: Optional[float] = None) -> str:
    if lab_[0] < 32.0:
        return "black"
    if chroma(lab_) > 18.0 and 50.0 <= hue(lab_) <= 100.0:
        return "brass"
    return "silver"


# --------------------------------------------------------------------------
# A GLB's materials
# --------------------------------------------------------------------------

def _chunks(path) -> tuple[Optional[dict], bytes]:
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None, b""
    if len(data) < 20 or data[:4] != b"glTF":
        return None, b""
    off, doc, binary = 12, None, b""
    while off + 8 <= len(data):
        n, kind = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + n]
        if kind == 0x4E4F534A:
            try:
                doc = json.loads(chunk.decode("utf-8"))
            except ValueError:
                return None, b""
        elif kind == 0x004E4942:
            binary = chunk
        off += 8 + n
    return doc, binary


def _view(doc: dict, binary: bytes, index: int) -> bytes:
    v = (doc.get("bufferViews") or [])[index]
    start = int(v.get("byteOffset") or 0)
    return binary[start: start + int(v["byteLength"])]


def _image_mean(doc: dict, binary: bytes, tex_index: int) -> Optional[tuple[float, float, float]]:
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        tex = (doc.get("textures") or [])[tex_index]
        img = (doc.get("images") or [])[tex["source"]]
        raw = _view(doc, binary, img["bufferView"]) if img.get("bufferView") is not None else None
        if not raw:
            return None
        im = Image.open(io.BytesIO(raw)).convert("RGB").resize((16, 16))
        px = list(im.getdata())
        return tuple(sum(p[k] for p in px) / (255.0 * len(px)) for k in range(3))
    except (IndexError, KeyError, OSError, ValueError, TypeError):
        return None


def _areas(doc: dict, binary: bytes) -> dict[int, float]:
    """Surface area per material index (triangle areas with numpy, else the primitives' box faces)."""
    try:
        import numpy as np
    except ImportError:
        np = None
    acc = doc.get("accessors") or []
    out: dict[int, float] = {}
    sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    dtypes = {5121: "u1", 5123: "u2", 5125: "u4", 5126: "f4"}
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            m = prim.get("material", -1)
            a = (prim.get("attributes") or {}).get("POSITION")
            if a is None or a >= len(acc):
                continue
            area = None
            if np is not None and binary and prim.get("mode", 4) == 4:
                try:
                    pa = acc[a]
                    pv = (doc.get("bufferViews") or [])[pa["bufferView"]]
                    stride = int(pv.get("byteStride") or 12)
                    buf = _view(doc, binary, pa["bufferView"])
                    start = int(pa.get("byteOffset") or 0)
                    count = int(pa["count"])
                    pos = np.ndarray((count, 3), dtype="<f4", buffer=buf, offset=start, strides=(stride, 4))
                    if prim.get("indices") is not None:
                        ia = acc[prim["indices"]]
                        ib = _view(doc, binary, ia["bufferView"])
                        idx = np.frombuffer(ib, dtype="<" + dtypes[ia["componentType"]],
                                            count=int(ia["count"]), offset=int(ia.get("byteOffset") or 0))
                    else:
                        idx = np.arange(count)
                    tri = pos[idx[: len(idx) // 3 * 3].astype(np.int64)].reshape(-1, 3, 3).astype(np.float64)
                    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
                    area = float(0.5 * np.linalg.norm(cr, axis=1).sum())
                except (KeyError, IndexError, ValueError, TypeError):
                    area = None
            if area is None and acc[a].get("min") and acc[a].get("max"):
                e = sorted((float(y) - float(x) for x, y in zip(acc[a]["min"], acc[a]["max"])), reverse=True)
                area = e[0] * e[1]
            out[m] = out.get(m, 0.0) + float(area or 0.0)
            _ = sizes
    return out


def _kind(name: str, rgb, metallic: float, textured: bool) -> str:
    n = name.lower()
    for kind, words in (("glass", GLASS_WORDS), ("metal", METAL_WORDS), ("wood", WOOD_WORDS),
                        ("fabric", FABRIC_WORDS), ("stone", STONE_WORDS)):
        if any(w in n for w in words):
            return kind
    if metallic >= 0.5:
        return "metal"
    L = lab(rgb)
    if textured and 20.0 <= hue(L) <= 80.0 and 8.0 <= chroma(L) <= 50.0 and 20.0 <= L[0] <= 85.0:
        return "wood"
    return "other"


def glb_palette(path) -> Optional[list[dict]]:
    """``[{"name", "kind", "rgb", "lab", "metallic", "share"}]`` of a GLB's materials, the largest first; None when
    the file cannot be read."""
    doc, binary = _chunks(path)
    if doc is None:
        return None
    mats = doc.get("materials") or []
    areas = _areas(doc, binary)
    total = sum(v for v in areas.values() if v > 0) or 1.0
    out = []
    for i, m in enumerate(mats):
        pbr = m.get("pbrMetallicRoughness") or {}
        factor = [float(v) for v in (pbr.get("baseColorFactor") or [1, 1, 1, 1])[:3]]
        tex = (pbr.get("baseColorTexture") or {}).get("index")
        mean = _image_mean(doc, binary, tex) if tex is not None else None
        # the factor is linear, the texture sRGB: the colour is the texture's light scaled by the factor, in sRGB
        rgb = [_srgb(f * (_lin(mean[k]) if mean else 1.0)) for k, f in enumerate(factor)]
        metallic = float(pbr.get("metallicFactor", 1.0 if tex is None and "metallicFactor" in pbr else 0.0) or 0.0)
        alpha = float((pbr.get("baseColorFactor") or [1, 1, 1, 1])[3]) if len(pbr.get("baseColorFactor") or []) > 3 \
            else 1.0
        kind = "glass" if (m.get("alphaMode") == "BLEND" and alpha < 0.7) else _kind(str(m.get("name") or ""), rgb,
                                                                                     metallic, mean is not None)
        out.append({"name": m.get("name"), "kind": kind, "rgb": [round(v, 4) for v in rgb],
                    "lab": [round(v, 2) for v in lab(rgb)], "metallic": round(metallic, 3),
                    "share": round(areas.get(i, 0.0) / total, 4)})
    out.sort(key=lambda x: -x["share"])
    return out


def attributes(palette: Optional[list[dict]]) -> dict:
    """The model's taste attributes from its palette (pure): ``wood_tone``, ``metal``, ``main`` (Lab), ``fabric``
    (Lab), ``loud`` (its largest surface is a saturated colour), the shares of wood / metal / fabric."""
    if not palette:
        return {}
    by: dict[str, float] = {}
    for p in palette:
        by[p["kind"]] = by.get(p["kind"], 0.0) + p["share"]

    def mean_lab(kind):
        xs = [p for p in palette if p["kind"] == kind and p["share"] > 0]
        w = sum(p["share"] for p in xs)
        if w <= 0:
            return None
        return [round(sum(p["lab"][k] * p["share"] for p in xs) / w, 2) for k in range(3)]

    wood, metal, fabric = mean_lab("wood"), mean_lab("metal"), mean_lab("fabric")
    main = next((p["lab"] for p in palette if p["kind"] != "glass" and p["share"] > 0), None)
    out = {"shares": {k: round(v, 3) for k, v in sorted(by.items())}}
    if wood is not None and by.get("wood", 0) >= 0.08:
        out["wood_tone"] = tone_of(wood)
        out["wood_lab"] = wood
    if metal is not None and by.get("metal", 0) >= 0.03:
        out["metal"] = metal_of(metal)
    if fabric is not None and by.get("fabric", 0) >= 0.1:
        out["fabric"] = fabric
    if main is not None:
        out["main"] = main
        out["loud"] = chroma(main) > LOUD_CHROMA
    return out


class TasteCache:
    """The attributes of the library models under ``assets_dir`` (``<assets>/models/...``), computed once and kept
    in ``<assets>/taste/attributes.json`` (keyed by the model file and its size)."""

    def __init__(self, assets_dir, autosave: int = 50):
        self.root = Path(assets_dir)
        self.path = self.root / "taste" / "attributes.json"
        self.data: dict = {}
        self.dirty = 0
        self.autosave = autosave
        if self.path.is_file():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self.data = {}

    def get(self, entry: dict) -> dict:
        glb = entry.get("glb")
        if not glb:
            return {}
        f = self.root / str(glb)
        if not f.is_file():
            return {}
        key = f"{entry.get('id')}:{f.stat().st_size}"
        if key not in self.data:
            self.data[key] = attributes(glb_palette(f))
            self.dirty += 1
            if self.dirty >= self.autosave:
                self.save()
        return self.data[key]

    def save(self) -> None:
        if not self.dirty:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, sort_keys=True), encoding="utf-8")
            tmp.replace(self.path)
            self.dirty = 0
        except OSError:
            pass


# --------------------------------------------------------------------------
# The project's target and the room's set
# --------------------------------------------------------------------------

def _slot_lab(slug: Optional[str], colour: Optional[str] = None) -> Optional[tuple]:
    try:
        from wenart.style import vocabulary as V
    except ImportError:
        return None
    if colour:
        try:
            from wenart.style import colours as SC
            lin = SC.linear_rgb(str(colour))
            if lin is not None:
                return lab([(float(v) ** (1 / 2.2)) for v in list(lin)[:3]])
        except Exception:  # noqa: BLE001 - a colour phrase the vocabulary does not know
            pass
    for table in ("FURNITURE_MATERIALS", "MATERIALS"):
        flat = ((getattr(V, table, {}) or {}).get(str(slug)) or {}).get("flat")
        if flat:
            return lab(flat)
    return None


def targets(style: Optional[dict]) -> dict:
    """The project's set (pure): ``wood_tone`` (the style's furniture wood, else its floor wood), ``metal`` (the
    style's furniture metal, else the window frames' finish when it is a metal colour), ``palette`` (Lab of the
    style's fabric, decor and accent colours)."""
    style = style or {}
    out: dict = {"palette": []}
    furn = style.get("furniture") if isinstance(style.get("furniture"), dict) else {}
    wood = _slot_lab(furn.get("wood")) or _slot_lab((style.get("floor") or {}).get("material"))
    if wood is not None:
        out["wood_tone"] = tone_of(wood)
    metal_slug = furn.get("metal") or (style.get("window_frame") or {}).get("material")
    words = str(metal_slug or "").lower()
    if any(w in words for w in ("black", "bronze", "anthracite", "graphite")):
        out["metal"] = "black"
    elif any(w in words for w in ("brass", "gold")):
        out["metal"] = "brass"
    elif any(w in words for w in ("chrome", "steel", "alumin", "silver", "nickel")):
        out["metal"] = "silver"
    for slot in (furn.get("by_type") or {}).values():
        if isinstance(slot, dict):
            c = _slot_lab(None, slot.get("fabric_colour") or slot.get("colour"))
            if c is not None:
                out["palette"].append(c)
    dec = style.get("decor") if isinstance(style.get("decor"), dict) else {}
    for key in ("cushion_colours", "throw_colours", "rug_colours", "accent_colours"):
        for name in dec.get(key) or []:
            c = _slot_lab(None, name)
            if c is not None:
                out["palette"].append(c)
    return out


def steps(attrs: dict, room: dict, target: dict) -> int:
    """Taste steps of a model in a room (pure; module docstring). ``room``: ``{"tones": [...], "metal": ...}`` of
    the pieces fitted there so far."""
    if not attrs:
        return 0
    n = 0
    tone = attrs.get("wood_tone")
    if tone:
        main = target.get("wood_tone")
        used = list(room.get("tones") or [])
        allowed = set(used[:2]) | ({main} if main else set())
        if tone not in allowed:
            extra = len(allowed | {tone}) > 2
            jump = main is not None and {tone, main} == {"light", "dark"}
            n += 1 + int(extra) + int(jump)
    metal = attrs.get("metal")
    want = room.get("metal") or target.get("metal")
    if metal and want and metal != want:
        n += 2 if room.get("metal") else 1
    if attrs.get("loud") and attrs.get("main"):
        h = hue(attrs["main"])
        if not any(chroma(c) > 15 and min(abs(h - hue(c)), 360 - abs(h - hue(c))) < 30 for c in target.get("palette") or []):
            n += 1
    return n


def note(room: dict, attrs: dict) -> None:
    """Record a fitted model's wood tone and metal in its room's set (in place)."""
    if not attrs:
        return
    tone = attrs.get("wood_tone")
    if tone and tone not in room.setdefault("tones", []):
        room["tones"].append(tone)
    if attrs.get("metal") and not room.get("metal"):
        room["metal"] = attrs["metal"]


def anchor_rank(ftype: str) -> int:
    return ANCHOR_ORDER.index(ftype) if ftype in ANCHOR_ORDER else len(ANCHOR_ORDER)
