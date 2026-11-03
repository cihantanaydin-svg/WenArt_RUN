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
  Italian, French, German, Spanish), then a material name that says metal (``MATERIAL_WORDS``: the feet or a metal
  base); geometry decides the rest (``bed_geometry``): a small foot under ``LEG_TOP_M``, a tall thin panel on one
  side, a covering part that reaches the top and is tall (the upholstered base with its headboard in one mesh), the
  soft parts that float above the floor and cover most of the footprint, pillows near the head end, the rest the
  frame. Another type gets no classes (nothing is guessed);
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

# words in material names that say a part's material (3 Nov 2026, the Maxalto 3DS files name their materials "fabric"
# and "metal"): a metal part of a bed is its feet or its metal base frame
MATERIAL_WORDS: dict[str, tuple[str, ...]] = {
    "legs": ("metal", "steel", "chrome", "brass", "bronze", "iron", "alumin", "acciaio", "metallo", "ottone", "ferro",
             "inox"),
}
BASE_SPAN_H = 0.5                      # a covering part at least this share of the model's height tall that reaches
                                       # its top is the base with its headboard (upholstery), not bedding

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
    # 3 Nov 2026 (the user's Furnitures zips: chairs, tables, sofas, lamps, decor): the materials a material name or a
    # type gives (``MATERIAL_NAME_WORDS``, ``TYPE_MATERIAL``)
    "fabric": {"name": "wenart_fabric", "srgb": [150, 139, 126], "roughness": 0.95, "metallic": 0.0,
               "material": "fabric", "materials": ["fabric"], "note": "taupe upholstery fabric"},
    "leather": {"name": "wenart_leather", "srgb": [120, 78, 52], "roughness": 0.5, "metallic": 0.0,
                "material": "other", "materials": ["other"], "note": "cognac leather"},
    "wood": {"name": "wenart_wood_oak", "srgb": [168, 128, 88], "roughness": 0.55, "metallic": 0.0,
             "material": "wood", "materials": ["wood"], "note": "oiled oak"},
    "wood_dark": {"name": "wenart_wood_walnut", "srgb": [92, 62, 42], "roughness": 0.5, "metallic": 0.0,
                  "material": "wood", "materials": ["wood"], "note": "walnut"},
    "metal": {"name": "wenart_metal_dark", "srgb": [58, 56, 54], "roughness": 0.4, "metallic": 1.0,
              "material": "metal", "materials": ["metal"], "note": "dark painted metal"},
    "chrome": {"name": "wenart_chrome", "srgb": [210, 210, 212], "roughness": 0.12, "metallic": 1.0,
               "material": "metal", "materials": ["metal"], "note": "polished chrome or steel"},
    "brass": {"name": "wenart_brass", "srgb": [196, 160, 98], "roughness": 0.3, "metallic": 1.0,
              "material": "metal", "materials": ["metal"], "note": "brushed brass"},
    "glass": {"name": "wenart_glass", "srgb": [225, 232, 232], "roughness": 0.04, "metallic": 0.0, "alpha": 0.25,
              "material": "glass", "materials": ["glass"], "note": "clear glass"},
    "marble": {"name": "wenart_marble", "srgb": [226, 222, 214], "roughness": 0.22, "metallic": 0.0,
               "material": "marble", "materials": ["marble"], "note": "light marble"},
    "plastic": {"name": "wenart_plastic", "srgb": [232, 230, 226], "roughness": 0.45, "metallic": 0.0,
                "material": "other", "materials": ["other"], "note": "matte white plastic"},
    "lacquer": {"name": "wenart_lacquer", "srgb": [222, 219, 212], "roughness": 0.3, "metallic": 0.0,
                "material": "other", "materials": ["other"], "note": "white lacquer"},
    "ceramic": {"name": "wenart_ceramic", "srgb": [236, 232, 224], "roughness": 0.25, "metallic": 0.0,
                "material": "other", "materials": ["other"], "note": "glazed white ceramic"},
    "rattan": {"name": "wenart_rattan", "srgb": [190, 156, 108], "roughness": 0.8, "metallic": 0.0,
               "material": "rattan", "materials": ["rattan"], "note": "natural rattan or cord"},
}
# material-name words (English, Italian, French, German, Spanish; lower case, parts of words), first match wins
MATERIAL_NAME_WORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("glass", ("glass", "vetro", "verre", "glas", "cristal", "vidrio", "mirror", "specchio")),
    ("chrome", ("chrome", "cromo", "cromat", "inox", "steel", "acciaio", "stainless", "nickel", "nichel", "alumin",
                "allumin", "silver", "argento")),
    ("brass", ("brass", "ottone", "bronze", "bronzo", "gold", "oro", "copper", "rame", "laiton")),
    ("metal", ("metal", "iron", "ferro", "fer ", "eisen", "hierro", "verniciat")),
    ("leather", ("leather", "pelle", "cuoio", "cuir", "leder", "cuero", "nabuk", "nubuck")),
    ("marble", ("marble", "marmo", "marbre", "marmor", "stone", "pietra", "granit", "travertin", "onyx")),
    ("rattan", ("rattan", "wicker", "vimini", "cane", "paglia", "rope", "corda", "cord", "rush")),
    ("wood_dark", ("walnut", "noce", "wenge", "ebony", "ebano", "smoked", "termotrattat", "dark wood")),
    ("wood", ("wood", "legno", "bois", "holz", "madera", "oak", "rovere", "ash", "frassino", "teak", "beech",
              "faggio", "pine", "pino", "birch", "betulla", "cherry", "ciliegio", "veneer", "impiallacc", "plywood")),
    ("fabric", ("fabric", "tessuto", "stoffa", "tissu", "stoff", "textil", "tela", "velvet", "velluto", "boucle",
                "linen", "lino", "wool", "lana", "cotton", "cotone", "felt", "feltro", "cushion", "cuscin",
                "upholster", "imbott")),
    ("lacquer", ("lacquer", "laccat", "laque", "lack", "matt", "opaco")),
    ("plastic", ("plastic", "plastica", "polyprop", "polipropil", "polycarb", "policarb", "abs", "resin", "resina",
                 "nylon", "pvc")),
    ("ceramic", ("ceramic", "ceramica", "porcelain", "porcellana", "gres", "terracotta")),
)
# the material of a part no name speaks for, by the model's type (its feet: ``legs``, dark metal)
UPHOLSTERED = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "office_chair")
WOODEN = ("chair", "bar_stool", "table_dining", "table_coffee", "side_table", "console_table", "desk", "sideboard",
          "tv_unit", "bookshelf", "nightstand", "dresser", "wardrobe", "display_cabinet", "tall_cabinet",
          "shoe_cabinet", "wall_cabinet", "crib", "bunk_bed")
LIGHTS = ("pendant_light", "ceiling_light", "table_lamp", "floor_lamp")


def type_material(ftype: str) -> str:
    if ftype in UPHOLSTERED or ftype in BED_TYPES:
        return "fabric"
    if ftype in WOODEN:
        return "wood"
    if ftype in LIGHTS:
        return "lacquer"
    return "ceramic"


def material_of_name(name: str) -> Optional[str]:
    """The palette class a material or part name says (``MATERIAL_NAME_WORDS``), else None."""
    text = " " + _name_tokens(name) + " "
    for cls, words in MATERIAL_NAME_WORDS:
        if any(w in text for w in words):
            return cls
    return None


def srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _name_tokens(*names) -> str:
    return " ".join(re.sub(r"[^a-z]+", " ", str(n or "").lower()) for n in names)


MERGE_M = 1e-4                         # vertices this close are one point (a mesh cut by the 3DS vertex limit)
SMALL_SHARE = 0.003                    # a piece under this share of the model's surface (stitches, seams, buttons)
                                       # takes the class of the piece it sits on


def _components(n_verts: int, tris: np.ndarray) -> np.ndarray:
    """The connected piece of every vertex (label propagation over the triangles, then pointer jumping)."""
    labels = np.arange(n_verts, dtype=np.int64)
    if not len(tris):
        return labels
    for _ in range(10000):
        m = np.minimum(np.minimum(labels[tris[:, 0]], labels[tris[:, 1]]), labels[tris[:, 2]])
        new = labels.copy()
        for k in range(3):
            np.minimum.at(new, tris[:, k], m)
        new = new[new]
        if np.array_equal(new, labels):
            break
        labels = new
    return labels


def parts(path) -> list[dict]:
    """The connected pieces of a model (3 Nov 2026, the second syncronia pod: a 3DS export cuts meshes at its vertex
    limit, so one mesh holds part of the base and part of the duvet): every primitive's triangles in the Z-up frame,
    vertices closer than ``MERGE_M`` merged across primitives, then the connected pieces. Each piece: ``{"key":
    [piece], "prims": {(mesh, prim): triangle indices of that primitive}, "node", "mesh_name", "material",
    "material_name" (of the primitive with most of its triangles), "min", "max", "tris", "area"}``."""
    from wenart.assets.audit import glbmesh as GM
    from wenart.assets.models import _node_matrices
    doc, buffers = GM.read(path)
    meshes = doc.get("meshes") or []
    mats = doc.get("materials") or []
    pos_all, tri_all, owner, local, info = [], [], [], [], []
    offset = 0
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
            mi = prim.get("material")
            pid = len(info)
            info.append({"key": (int(node["mesh"]), pi), "node": str(node.get("name") or ""),
                         "mesh_name": str(mesh.get("name") or ""), "material": mi,
                         "material_name": str((mats[mi] or {}).get("name") or "") if isinstance(mi, int)
                         and mi < len(mats) else ""})
            pos_all.append(pos)
            tri_all.append(tris + offset)
            owner.append(np.full(len(tris), pid, dtype=np.int64))
            local.append(np.arange(len(tris), dtype=np.int64))
            offset += len(pos)
    if not pos_all:
        return []
    pos = np.concatenate(pos_all)
    tris = np.concatenate(tri_all) if tri_all else np.zeros((0, 3), dtype=np.int64)
    owner = np.concatenate(owner)
    local = np.concatenate(local)
    _u, canon = np.unique(np.round(pos / MERGE_M).astype(np.int64), axis=0, return_inverse=True)
    canon = canon.reshape(-1)
    ct = canon[tris]
    vlab = _components(int(canon.max()) + 1, ct)
    tlab = vlab[ct[:, 0]]
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    tarea = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    out = []
    order = np.argsort(tlab, kind="stable")
    labs, starts = np.unique(tlab[order], return_index=True)
    ends = list(starts[1:]) + [len(order)]
    for k, (s0, s1) in enumerate(zip(starts, ends)):
        sel = order[s0:s1]
        vs = pos[tris[sel].reshape(-1)]
        prims: dict = {}
        for pid in np.unique(owner[sel]):
            prims[info[int(pid)]["key"]] = local[sel[owner[sel] == pid]]
        main = info[int(np.bincount(owner[sel]).argmax())]
        out.append({"key": [k], "prims": prims, "node": main["node"], "mesh_name": main["mesh_name"],
                    "material": main["material"], "material_name": main["material_name"],
                    "min": [round(float(v), 4) for v in vs.min(axis=0)],
                    "max": [round(float(v), 4) for v in vs.max(axis=0)],
                    "tris": int(len(sel)), "area": round(float(tarea[sel].sum()), 5)})
    return out


def _uses_texture(doc: dict) -> bool:
    """A material links a texture (an image in the file that no material uses says nothing)."""
    def has(obj) -> bool:
        if isinstance(obj, dict):
            return any((k.endswith("Texture") and isinstance(v, dict) and isinstance(v.get("index"), int))
                       or has(v) for k, v in obj.items())
        return False
    return any(has(m) for m in doc.get("materials") or [])


def needs_materials(doc: dict) -> bool:
    """No texture, and the base colours say nothing about the parts: every one near white or missing
    (``WHITE_MIN``), or one colour for the whole model (an exporter's default material, e.g. Assimp's grey)."""
    if _uses_texture(doc):
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
    """The class the names give: the part words (``NAME_WORDS``) in the node, mesh and material names, then the
    material words (``MATERIAL_WORDS``) in the material name; None when no name says it."""
    text = _name_tokens(p.get("node"), p.get("mesh_name"), p.get("material_name"))
    for cls in ("bedding", "legs", "headboard", "frame"):
        if any(w in text for w in NAME_WORDS[cls]):
            return cls
    mat = _name_tokens(p.get("material_name"))
    for cls, words in MATERIAL_WORDS.items():
        if any(w in mat for w in words):
            return cls
    return None


def bed_geometry(p: dict, box_min: list, box_max: list, why: bool = False):
    """The class of one part of a bed from its box (``box_*`` = the whole model's); ``why``: ``(class, rule)``."""
    def ret(cls, rule):
        return (cls, rule) if why else cls
    pmin, pmax = p["min"], p["max"]
    w, d = box_max[0] - box_min[0], box_max[1] - box_min[1]
    h = box_max[2] - box_min[2]
    pw, pd, ph = (pmax[i] - pmin[i] for i in range(3))
    if pmax[2] - box_min[2] <= LEG_TOP_M and pw <= LEG_FOOT_M and pd <= LEG_FOOT_M:
        return ret("legs", "foot")
    thin = min(pw, pd)
    span = max(pw / w if pw >= pd else 0.0, pd / d if pd > pw else 0.0)
    if pmax[2] - box_min[2] >= HEAD_MIN_TOP * h and thin <= HEAD_THIN_M and span >= HEAD_SPAN:
        return ret("headboard", "panel")
    floats = pmin[2] - box_min[2] >= FLOAT_MIN_M
    covers = pw >= COVER_SPAN * w and pd >= COVER_SPAN * d
    if covers and pmax[2] - box_min[2] >= HEAD_MIN_TOP * h and ph >= BASE_SPAN_H * h:
        return ret("frame", "base_headboard")   # the upholstered base with its headboard (Maxalto Demetra, Selene)
    if floats and covers:
        return ret("bedding", "cover")
    if floats and min(pw, pd) >= PILLOW_MIN_M and ph <= PILLOW_MAX_H_M and max(pw, pd) <= 0.9:
        return ret("bedding", "pillow")
    return ret("frame", "rest")


def _metal_fits(p: dict, box_min: list) -> bool:
    """A metal-named part a bed's metal can be: low (its top under ``LEG_TOP_M`` + 5 cm: feet, a base frame)."""
    return p["max"][2] - box_min[2] <= LEG_TOP_M + 0.05


def _inside(c: list, big: dict, tol: float = 0.01) -> bool:
    return all(big["min"][i] - tol <= c[i] <= big["max"][i] + tol for i in range(3))


def classify_any(ps: list[dict], ftype: str) -> list[dict]:
    """The classes of any model (3 Nov 2026): a bed by ``classify``; any other type piece by piece: the material its
    names say (``material_of_name``: material, mesh, node), else an upholstered piece's thin foot on the floor is dark
    metal, else the type's material (``type_material``)."""
    if ftype in BED_TYPES:
        return classify(ps, ftype)
    if not ps:
        return []
    lo = [min(p["min"][i] for p in ps) for i in range(3)]
    h = max(p["max"][2] for p in ps) - lo[2]
    upholstered = type_material(ftype) == "fabric"
    out = []
    for p in ps:
        cls = (material_of_name(p.get("material_name") or "") or material_of_name(p.get("mesh_name") or "")
               or material_of_name(p.get("node") or ""))
        if cls:
            out.append({"key": p["key"], "class": cls, "by": "name"})
            continue
        pw, pd = p["max"][0] - p["min"][0], p["max"][1] - p["min"][1]
        # an upholstered piece's unnamed feet: thin, on the floor, in the lower part (a wooden piece's legs keep wood)
        if (upholstered and len(ps) > 1 and pw <= LEG_FOOT_M and pd <= LEG_FOOT_M and p["min"][2] - lo[2] <= 0.02
                and p["max"][2] - lo[2] <= max(LEG_TOP_M, 0.5 * h)):
            out.append({"key": p["key"], "class": "metal", "by": "geometry:foot"})
            continue
        out.append({"key": p["key"], "class": type_material(ftype), "by": "type"})
    return out


def classify(ps: list[dict], ftype: str) -> list[dict]:
    """``[{"key", "class", "by"}]`` for a bed (``"name"``, ``"geometry:<rule>"``, ``"base"``, ``"sits on"``); [] for
    another type. After the per-part rules: when no covering part is the frame yet, the lowest covering soft part is
    the base (it carries the mattress); a piece under ``SMALL_SHARE`` of the surface that only the last rule typed
    takes the class of the smallest larger piece whose box holds its centre."""
    if ftype not in BED_TYPES or not ps:
        return []
    lo = [min(p["min"][i] for p in ps) for i in range(3)]
    hi = [max(p["max"][i] for p in ps) for i in range(3)]
    total = sum(p["area"] for p in ps) or 1.0
    out = []
    for p in ps:
        cls = by_name(p)
        if cls == "legs" and not _metal_fits(p, lo) and not any(
                w in _name_tokens(p.get("node"), p.get("mesh_name")) for w in NAME_WORDS["legs"]):
            cls = None                                   # a metal name on a high part: the geometry decides
        if cls:
            out.append({"key": p["key"], "class": cls, "by": "name"})
            continue
        g, rule = bed_geometry(p, lo, hi, why=True)
        out.append({"key": p["key"], "class": g, "by": f"geometry:{rule}"})
    covering = [(p, c) for p, c in zip(ps, out) if c["by"] in ("geometry:cover", "geometry:base_headboard")
                or (c["class"] == "frame" and (p["max"][0] - p["min"][0]) >= COVER_SPAN * (hi[0] - lo[0])
                    and (p["max"][1] - p["min"][1]) >= COVER_SPAN * (hi[1] - lo[1]))]
    if covering and not any(c["class"] == "frame" for _p, c in covering):
        soft = [(p, c) for p, c in covering if c["by"] == "geometry:cover"]
        if len(soft) >= 2:
            p0, c0 = min(soft, key=lambda pc: pc[0]["min"][2])
            if all(p0["min"][2] < p["min"][2] - 0.02 for p, _c in soft if p is not p0):
                c0.update({"class": "frame", "by": "base"})
    big = [(p, c) for p, c in zip(ps, out) if p["area"] >= SMALL_SHARE * total]
    for p, c in zip(ps, out):
        if p["area"] >= SMALL_SHARE * total or c["by"] != "geometry:rest":
            continue
        centre = [(p["min"][i] + p["max"][i]) / 2 for i in range(3)]
        hosts = [(bp, bc) for bp, bc in big if bp is not p and _inside(centre, bp)]
        if hosts:
            hp, hc = min(hosts, key=lambda pc: np.prod([max(pc[0]["max"][i] - pc[0]["min"][i], 1e-4)
                                                        for i in range(3)]))
            c.update({"class": hc["class"], "by": "sits on"})
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
    """The GLB with one material per class (``PALETTE``); a primitive whose triangles fall in several classes is split
    into one primitive per class (the same vertex attributes, a new index accessor each). Returns ``{"slots":
    material_slots, "classes": {class: pieces}, "materials": n, "split": primitives split}``. ``src`` may equal
    ``dst``."""
    from wenart.assets import warehouse as WH
    from wenart.assets.audit import glbmesh as GM
    doc, binary = WH.read_glb(src)
    gdoc, buffers = GM.read(src)
    binary = bytearray(binary or b"")
    cls_of = {tuple(c["key"]): c["class"] for c in classes}
    names: list[str] = []
    mats = []
    present = list(CLASSES) + sorted({c["class"] for c in classes} - set(CLASSES))
    for c in present:
        pal = PALETTE[c]
        if pal["name"] in names:
            continue
        names.append(pal["name"])
        mat = {"name": pal["name"], "doubleSided": True,
               "pbrMetallicRoughness": {"baseColorFactor": [round(srgb_to_linear(v), 5) for v in pal["srgb"]]
                                        + [float(pal.get("alpha", 1.0))], "metallicFactor": pal["metallic"],
                                        "roughnessFactor": pal["roughness"]}}
        if pal.get("alpha", 1.0) < 1.0:
            mat["alphaMode"] = "BLEND"
        mats.append(mat)
    by_prim: dict = {}
    area_of: dict[str, float] = {}
    counts: dict[str, int] = {}
    for p in ps:
        c = cls_of.get(tuple(p["key"]), "frame")
        counts[c] = counts.get(c, 0) + 1
        area_of[PALETTE[c]["name"]] = area_of.get(PALETTE[c]["name"], 0.0) + float(p["area"])
        for key, idx in (p.get("prims") or {}).items():
            by_prim.setdefault(tuple(key), {}).setdefault(c, []).append(np.asarray(idx, dtype=np.int64))
    split = 0
    views = doc.setdefault("bufferViews", [])
    accessors = doc.setdefault("accessors", [])
    for mi, mesh in enumerate(doc.get("meshes") or []):
        new_prims = []
        for pi, prim in enumerate(mesh.get("primitives") or []):
            groups = by_prim.get((mi, pi)) or {(classes[0]["class"] if classes else "frame"): []}
            if len(groups) == 1:
                prim["material"] = names.index(PALETTE[next(iter(groups))]["name"])
                new_prims.append(prim)
                continue
            split += 1
            if "indices" in prim:
                idx = GM.accessor(gdoc, buffers, prim["indices"], as_float=False).reshape(-1).astype(np.int64)
            else:
                n = int(accessors[prim["attributes"]["POSITION"]]["count"])
                idx = np.arange(n, dtype=np.int64)
            tri = GM._triangles(int(prim.get("mode", 4)), idx)
            for c, lists in groups.items():
                sel = tri[np.concatenate(lists)].reshape(-1).astype(np.uint32)
                binary += b"\x00" * (-len(binary) % 4)
                views.append({"buffer": 0, "byteOffset": len(binary), "byteLength": int(sel.nbytes),
                              "target": 34963})
                binary += sel.tobytes()
                accessors.append({"bufferView": len(views) - 1, "componentType": 5125, "count": int(len(sel)),
                                  "type": "SCALAR"})
                q = {k: v for k, v in prim.items() if k not in ("indices", "material", "mode")}
                q.update(indices=len(accessors) - 1, material=names.index(PALETTE[c]["name"]), mode=4)
                new_prims.append(q)
        mesh["primitives"] = new_prims
    doc["materials"] = mats
    bufs = doc.setdefault("buffers", [{}])
    bufs[0].pop("uri", None)
    bufs[0]["byteLength"] = len(binary)
    WH.write_glb(dst, doc, bytes(binary))
    total = sum(area_of.values()) or 1.0
    slots = []
    for i, name in enumerate(names):
        if name not in area_of:
            continue
        pal = next(PALETTE[c] for c in present if PALETTE[c]["name"] == name)
        slots.append({"index": i, "name": name, "material": pal["material"], "materials": list(pal["materials"]),
                      "agreed": True, "separable": True, "share": round(area_of[name] / total, 4), "textured": False,
                      "base_colour": [round(srgb_to_linear(v), 4) for v in pal["srgb"]] + [1.0],
                      "colour_rgb": list(pal["srgb"]), "note": pal["note"], "by": "wenart.assets.part_materials"})
    return {"slots": slots, "classes": counts, "materials": len(mats), "split": split}


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
    rows = [dict({k: v for k, v in p.items() if k != "prims"}, prims=[list(k) for k in (p.get("prims") or {})],
                 **{k: cls.get(tuple(p["key"]), {}).get(k) for k in ("class", "by")}) for p in ps]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(rows, indent=1), encoding="utf-8")
