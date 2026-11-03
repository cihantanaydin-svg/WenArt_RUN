"""Part materials for library models that arrive without materials (3 Nov 2026, the user's request to include the
proper beds of "beds.zip" in the library; the 3DS exports of the manufacturer models render plain white).

What:

- ``parts(path)``: every primitive of a fixed GLB (metres, Z up, origin at the floor centre, ``warehouse.fixup``) with
  its node, mesh and material names, its box in the importer's Z-up frame, triangles and surface area;
- ``needs_materials(doc)``: True when the model carries no texture and its base colours say nothing (every one near
  white or missing, ``WHITE_MIN``, or one colour for the whole model): the parts get ours; a model with real
  materials keeps them;
- ``classify(parts, ftype)``: each primitive's part class for a bed (``BED_TYPES``): ``bedding`` (mattress, duvet,
  sheets, pillows, throws), ``legs``, ``headboard``, ``frame``. The names decide first (``NAME_WORDS``: English,
  Italian, French, German, Spanish); geometry decides the rest (``bed_geometry``): a small foot under ``LEG_TOP_M``,
  a tall thin panel on one side, the soft parts that float above the floor and cover most of the footprint, pillows
  near the head end, the rest the frame. Another type gets no classes (nothing is guessed);
- ``assign(src, dst, classes)``: the GLB rewritten with one material per class (``PALETTE``: a white linen for the
  bedding, a taupe upholstery fabric for the frame and the headboard, a bronze metal for the legs; glTF PBR factors,
  roughness and metallic set), the primitives pointed at them; returns the ``material_slots`` record of the catalogue
  (``wenart.assets.recolour`` field names: the upholstery slot ``fabric``, separable, so the fit recolours it to the
  brief's fabric colour; the bedding slot ``other``, so it stays white);
- ``front_from_parts(parts, classes)``: the bed's front axis from the head end (the headboard, else the pillows): the
  front is the side opposite the head; ``None`` when neither is clear.

Why: a white model reads as a grey box in a render, and the library rule asks for real materials (CLAUDE.md, library
rules); the builder already recolours a separable fabric slot (``fit.look_of``), so the upholstery takes the
project's colour like the other upholstered models.

How: pure Python and numpy on the glTF JSON and its binary chunk (``glbmesh.accessor``, ``models._node_matrices``);
no Blender.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import numpy as np

BED_TYPES = ("bed_single", "bed_double")
CLASSES = ("bedding", "frame", "headboard", "legs")
WHITE_MIN = 0.85                       # every base colour channel at least this (or none): the file says nothing
LEG_TOP_M = 0.35                       # a foot ends below this height
LEG_FOOT_M = 0.15                      # ... and is at most this wide and deep
HEAD_MIN_TOP = 0.75                    # a headboard reaches at least this share of the model's height
HEAD_THIN_M = 0.25                     # ... is at most this thick
HEAD_SPAN = 0.6                        # ... and spans at least this share of the bed's width
FLOAT_MIN_M = 0.12                     # a soft part (mattress, duvet, pillow) starts at least this high
COVER_SPAN = 0.6                       # a mattress or duvet covers at least this share of both footprint sides
PILLOW_MIN_M = 0.25                    # a pillow is at least this wide and deep (a rail is thinner)
PILLOW_MAX_H_M = 0.35                  # ... and at most this tall
FRONT_OFFSET = 0.15                    # the head end sits at least this share of the footprint off the centre

# words in node, mesh and material names (lower case, matched as parts of words)
NAME_WORDS: dict[str, tuple[str, ...]] = {
    "bedding": ("pillow", "cushion", "duvet", "quilt", "blanket", "sheet", "linen", "mattress", "bedding", "plaid",
                "throw", "bedspread", "comforter", "cuscin", "guancial", "piumon", "coperta", "lenzuol", "materass",
                "trapunt", "copriletto", "oreiller", "coussin", "couette", "drap", "matelas", "kissen", "decke",
                "matratze", "almohad", "colchon", "edred", "sabana"),
    "legs": ("leg", "feet", "foot", "piede", "piedi", "gamba", "gambe", "pied", "fuss", "pata", "patas"),
    "headboard": ("headboard", "testata", "testiera", "spalliera", "tete", "kopfteil", "cabecero"),
    "frame": ("frame", "giroletto", "struttura", "telaio", "base", "sommier", "rete", "rail", "fianc", "cadre",
              "rahmen", "estructura"),
}

# glTF PBR factors (linear base colour) of each class; the colour in sRGB for the catalogue's colour_rgb
PALETTE: dict[str, dict] = {
    "bedding": {"name": "wenart_bedding_linen", "srgb": [236, 233, 226], "roughness": 0.92, "metallic": 0.0,
                "material": "other", "materials": ["other"], "note": "white linen bedding (mattress, duvet, pillows)"},
    "frame": {"name": "wenart_upholstery_fabric", "srgb": [150, 139, 126], "roughness": 0.95, "metallic": 0.0,
              "material": "fabric", "materials": ["fabric"], "note": "taupe upholstery fabric (frame)"},
    "headboard": {"name": "wenart_upholstery_fabric", "srgb": [150, 139, 126], "roughness": 0.95, "metallic": 0.0,
                  "material": "fabric", "materials": ["fabric"], "note": "taupe upholstery fabric (headboard)"},
    "legs": {"name": "wenart_legs_bronze", "srgb": [74, 61, 50], "roughness": 0.38, "metallic": 1.0,
             "material": "metal", "materials": ["metal"], "note": "bronze metal feet"},
}


def srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _name_tokens(*names) -> str:
    return " ".join(re.sub(r"[^a-z]+", " ", str(n or "").lower()) for n in names)


def parts(path) -> list[dict]:
    """``[{"key": (mesh, prim), "node", "mesh_name", "material", "material_name", "min", "max", "tris", "area"}]``."""
    from wenart.assets.audit import glbmesh as GM
    from wenart.assets.models import _node_matrices
    doc, buffers = GM.read(path)
    meshes = doc.get("meshes") or []
    mats = doc.get("materials") or []
    out = []
    for index, world in _node_matrices(doc):
        node = doc["nodes"][index]
        if "mesh" not in node:
            continue
        m = np.array(world, dtype=np.float64).reshape(4, 4).T
        mesh = meshes[node["mesh"]]
        for pi, prim in enumerate(mesh.get("primitives") or []):
            attrs = prim.get("attributes") or {}
            if "POSITION" not in attrs:
                continue
            pos = GM.accessor(doc, buffers, attrs["POSITION"])[:, :3]
            pos = pos @ m[:3, :3].T + m[:3, 3]
            pos = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], axis=1)
            if "indices" in prim:
                idx = GM.accessor(doc, buffers, prim["indices"], as_float=False).reshape(-1).astype(np.int64)
            else:
                idx = np.arange(len(pos), dtype=np.int64)
            tris = GM._triangles(int(prim.get("mode", 4)), idx)
            area = 0.0
            if len(tris):
                a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
                area = float(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum())
            mi = prim.get("material")
            out.append({"key": [int(node["mesh"]), pi], "node": str(node.get("name") or ""),
                        "mesh_name": str(mesh.get("name") or ""), "material": mi,
                        "material_name": str((mats[mi] or {}).get("name") or "") if isinstance(mi, int)
                        and mi < len(mats) else "",
                        "min": [round(float(v), 4) for v in pos.min(axis=0)],
                        "max": [round(float(v), 4) for v in pos.max(axis=0)],
                        "tris": int(len(tris)), "area": round(area, 5)})
    return out


def needs_materials(doc: dict) -> bool:
    """No texture, and the base colours say nothing about the parts: every one near white or missing
    (``WHITE_MIN``), or one colour for the whole model (an exporter's default material, e.g. Assimp's grey)."""
    if doc.get("images") or doc.get("textures"):
        return False
    colours = set()
    white = True
    for mat in doc.get("materials") or []:
        pbr = (mat or {}).get("pbrMetallicRoughness") or {}
        col = pbr.get("baseColorFactor")
        if isinstance(col, list) and len(col) >= 3:
            colours.add(tuple(round(float(v), 3) for v in col[:3]))
            if min(float(v) for v in col[:3]) < WHITE_MIN:
                white = False
    return white or len(colours) <= 1


def by_name(p: dict) -> Optional[str]:
    text = _name_tokens(p.get("node"), p.get("mesh_name"), p.get("material_name"))
    for cls in ("bedding", "legs", "headboard", "frame"):
        if any(w in text for w in NAME_WORDS[cls]):
            return cls
    return None


def bed_geometry(p: dict, box_min: list, box_max: list) -> str:
    """The class of one part of a bed from its box (``box_*`` = the whole model's)."""
    pmin, pmax = p["min"], p["max"]
    w, d = box_max[0] - box_min[0], box_max[1] - box_min[1]
    h = box_max[2] - box_min[2]
    pw, pd, ph = (pmax[i] - pmin[i] for i in range(3))
    if pmax[2] - box_min[2] <= LEG_TOP_M and pw <= LEG_FOOT_M and pd <= LEG_FOOT_M:
        return "legs"
    thin = min(pw, pd)
    span = max(pw / w if pw >= pd else 0.0, pd / d if pd > pw else 0.0)
    if pmax[2] - box_min[2] >= HEAD_MIN_TOP * h and thin <= HEAD_THIN_M and span >= HEAD_SPAN:
        return "headboard"
    floats = pmin[2] - box_min[2] >= FLOAT_MIN_M
    if floats and pw >= COVER_SPAN * w and pd >= COVER_SPAN * d:
        return "bedding"
    if floats and min(pw, pd) >= PILLOW_MIN_M and ph <= PILLOW_MAX_H_M and max(pw, pd) <= 0.9:
        return "bedding"
    return "frame"


def classify(ps: list[dict], ftype: str) -> list[dict]:
    """``[{"key", "class", "by": "name" | "geometry"}]`` for a bed; [] for another type."""
    if ftype not in BED_TYPES or not ps:
        return []
    lo = [min(p["min"][i] for p in ps) for i in range(3)]
    hi = [max(p["max"][i] for p in ps) for i in range(3)]
    out = []
    for p in ps:
        cls = by_name(p)
        out.append({"key": p["key"], "class": cls or bed_geometry(p, lo, hi), "by": "name" if cls else "geometry"})
    return out


def front_from_parts(ps: list[dict], classes: list[dict]) -> Optional[tuple[str, str]]:
    """``(front axis, why)``: the side opposite the head end (the headboard, else the pillows: small bedding parts);
    None when no head end stands ``FRONT_OFFSET`` off the centre on one axis."""
    if not ps:
        return None
    lo = [min(p["min"][i] for p in ps) for i in range(2)]
    hi = [max(p["max"][i] for p in ps) for i in range(2)]
    centre = [(lo[i] + hi[i]) / 2 for i in range(2)]
    size = [max(hi[i] - lo[i], 1e-6) for i in range(2)]
    cls = {tuple(c["key"]): c["class"] for c in classes}
    full = [p for p in ps if cls.get(tuple(p["key"])) == "bedding"]
    big = max((p["area"] for p in full), default=0.0)
    for what, rows in (("headboard", [p for p in ps if cls.get(tuple(p["key"])) == "headboard"]),
                       ("pillows", [p for p in full if p["area"] < 0.25 * big])):
        if not rows:
            continue
        area = sum(p["area"] for p in rows) or 1.0
        c = [sum(((p["min"][i] + p["max"][i]) / 2) * p["area"] for p in rows) / area for i in range(2)]
        off = [(c[i] - centre[i]) / size[i] for i in range(2)]
        axis = 0 if abs(off[0]) > abs(off[1]) else 1
        if abs(off[axis]) < FRONT_OFFSET:
            continue
        head = ("+X" if off[0] > 0 else "-X") if axis == 0 else ("+Y" if off[1] > 0 else "-Y")
        front = {"+X": "-X", "-X": "+X", "+Y": "-Y", "-Y": "+Y"}[head]
        return front, f"the {what} sit on the {head} side (offset {off[axis]:+.2f} of the footprint): front {front}"
    return None


def assign(src, dst, ps: list[dict], classes: list[dict]) -> dict:
    """The GLB with one material per class (``PALETTE``); returns ``{"slots": material_slots, "classes": {class:
    parts}, "materials": n}``. ``src`` may equal ``dst``."""
    from wenart.assets import warehouse as WH
    doc, binary = WH.read_glb(src)
    cls = {tuple(c["key"]): c["class"] for c in classes}
    names: list[str] = []
    mats = []
    for c in CLASSES:
        pal = PALETTE[c]
        if pal["name"] in names:
            continue
        names.append(pal["name"])
        mats.append({"name": pal["name"], "doubleSided": True,
                     "pbrMetallicRoughness": {"baseColorFactor": [round(srgb_to_linear(v), 5) for v in pal["srgb"]]
                                              + [1.0], "metallicFactor": pal["metallic"],
                                              "roughnessFactor": pal["roughness"]}})
    used: dict[str, float] = {}
    counts: dict[str, int] = {}
    area = {tuple(p["key"]): p["area"] for p in ps}
    for mi, mesh in enumerate(doc.get("meshes") or []):
        for pi, prim in enumerate(mesh.get("primitives") or []):
            c = cls.get((mi, pi), "frame")
            prim["material"] = names.index(PALETTE[c]["name"])
            used[PALETTE[c]["name"]] = used.get(PALETTE[c]["name"], 0.0) + area.get((mi, pi), 0.0)
            counts[c] = counts.get(c, 0) + 1
    doc["materials"] = mats
    WH.write_glb(dst, doc, binary)
    total = sum(used.values()) or 1.0
    slots = []
    for i, name in enumerate(names):
        pal = next(PALETTE[c] for c in CLASSES if PALETTE[c]["name"] == name)
        if name not in used:
            continue
        slots.append({"index": i, "name": name, "material": pal["material"], "materials": list(pal["materials"]),
                      "agreed": True, "separable": True, "share": round(used[name] / total, 4), "textured": False,
                      "base_colour": [round(srgb_to_linear(v), 4) for v in pal["srgb"]] + [1.0],
                      "colour_rgb": list(pal["srgb"]), "note": pal["note"], "by": "wenart.assets.part_materials"})
    return {"slots": slots, "classes": counts, "materials": len(mats)}


def material_fields(slots: list[dict], min_share: float = 0.05) -> dict:
    """The catalogue's material fields from the slots (``recolour.py`` names): ``material_tags`` (the slot materials of
    at least ``min_share`` but ``other``), ``recolourable_fabric`` / ``recolourable_wood``."""
    tags = sorted({s["material"] for s in slots if s["material"] not in ("other", "mixed")
                   and float(s["share"]) >= min_share})
    fabric = any(s["material"] == "fabric" and s["separable"] and float(s["share"]) >= min_share for s in slots)
    return {"material_slots": slots, "material_tags": tags, "recolourable_fabric": fabric,
            "recolourable_wood": False}


def write_debug(path: Path, ps: list[dict], classes: list[dict]) -> None:
    import json
    cls = {tuple(c["key"]): c for c in classes}
    rows = [dict(p, **{k: cls.get(tuple(p["key"]), {}).get(k) for k in ("class", "by")}) for p in ps]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(rows, indent=1), encoding="utf-8")
