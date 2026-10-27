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
  other outside door narrower than ``WIDE_DOOR_M``), ``glazed_door`` (wider), ``terrace_door`` (a door the architect
  marked ``outside_door``: to a terrace or balcony room; glazed, one leaf) and ``window``;
- candidates: audit ``keep`` / ``fix``, not rated low by the audit's vision check (``site_models.vision_quality``),
  usable in the licence mode, a plausible size for the category (``SIZES``), no
  pack, set or inside door (``INSIDE_WORDS``) in the title, depth under ``MAX_DEPTH_M``; ranked textured first, the
  title's category words (``WORDS``), ``keep`` before ``fix``, then the smallest proportion error over the
  category's openings, then the id;
- one model per category, so a building's windows match: an opening takes the category's model when one panel's
  proportions (panel width over height) lie within ``ASPECT_TOL`` (a log ratio) of the model's, with the number of
  panels (1 .. ``MAX_PANELS``) that fits best and its height lies within ``MAX_SCALE`` of the model's (a scaled-down
  model gets toy frames); else (until 26 Oct 2026) the next ranked candidate that fits, (since 26 Oct 2026) another
  member of the same family, else none (the parametric opening).
Every entry records the asset (id, file, frame fields, licence), ``panels``, ``category``, ``aspect_error``, the
``outward`` plan direction and the reason; the build marks the object ``inferred`` (the documents draw the opening, not its product).

26 Oct 2026 (user on real06, a Scandinavian house: "The house needs to make sense and needs to look very stylish"; a
glazed door with a busy black-and-white lattice, dark six-panel doors on the facade, one black-framed traditional sash
window among white sliding ones):

- What: the house's style picks the openings. ``OPENING_LOOK`` says per style family what a designer puts in
  (``FAMILY_LOOK``: Scandinavian, Japandi, modern, minimal, contemporary -> ``light``: clear glass, no or few glazing
  bars, a flush or glazed leaf; industrial -> ``industrial``: glazing bars allowed; classic, rustic, Mediterranean ->
  ``period``: panelled leaves and bars allowed). ``look_fit`` leaves a model out when its title names the other look
  (``PERIOD_WORDS``, a panelled leaf ``_panelled``, or ``MODERN_WORDS``), when half or more of its audited styles are
  the look's ``avoid`` styles, or (with the files, ``glb_panes``) when its glass is patterned (an image on a glass
  material) or divided by glazing bars (``BARS_MIN_LITES`` lites and ``BARS_PER_M2`` per square metre) where the look
  wants clear glass; it ranks the rest (0 the house's own family, 1 a style of the look, 2 unknown, 3 a minority of
  avoided styles). The audited styles reach the catalogue's extras in ``load_extras`` (the audit's vision answers,
  ``growth_entries.apply_audit_styles``).
- One door and window language: the openings of a category take one model family (``family_key``: one model, or the
  size and colour variants of one series), the family whose best model ranks first by style, then covers the most
  openings, then the old order. An opening no member fits stays the parametric opening in the style's finish (listed
  in ``notes``) instead of a model of another family; ``opening_build`` paints every frame in the style's finish.
- Why: the choice ranked textured models first and fell back to any model that fitted, so the house got a
  traditional sash beside modern sliders and dark panelled doors in a Scandinavian facade.
"""
from __future__ import annotations

import json
import math
import re
import struct
from pathlib import Path
from typing import Optional, Sequence

WIDE_DOOR_M = 1.4
MAX_DEPTH_M = 0.45
ASPECT_TOL = 0.25                  # |log(panel w/h over model w/h)| <= 0.25: about 28 % either way
MAX_SCALE = 1.8                    # the opening's height within 1/1.8 .. 1.8 x the model's (frames keep real sizes)
MAX_PANELS = 8
RANK_STEP = 0.05                   # 25 Oct 2026: the mean proportion error ranks in steps: a few new windows of odd
                                   # proportions no longer swap the building's model (real04: aluminium -> leaded)
SIZES = {                          # (width range, height range) of one model, metres
    "entrance": ((0.75, 1.5), (1.9, 2.8)),
    "door": ((0.65, 1.4), (1.9, 2.7)),
    "glazed_door": ((1.2, 4.0), (1.9, 2.9)),
    "terrace_door": ((0.7, 1.6), (1.9, 2.7)),
    "window": ((0.4, 3.0), (0.4, 2.6)),
}
WORDS = {                          # title words that say a model is meant for the category
    "entrance": ("front", "entrance", "entry", "main", "pivot", "exterior"),
    "door": ("front", "entry", "exterior", "door"),
    "glazed_door": ("sliding", "glass", "french", "patio", "folding", "balcony", "terrace"),
    "terrace_door": ("balcony", "glass", "glazed", "french", "patio", "terrace", "lite"),
    "window": ("window", "casement", "sliding", "awning", "tilt"),
}
INSIDE_WORDS = ("interior", "internal", "toilet", "elevator", "japanese", "closet", "wardrobe", "shower", "barn")
# 27 Oct 2026: a one-leaf category (entrance, door, terrace door) never takes a model whose title names a sliding
# system ("Lift Slide") or a pair ("Double ...", "Duble"): the build scales one model into the whole opening
PAIR_WORDS = ("slide", "double", "duble", "pair")
NOT_WORDS = {                      # title words that rule a model out of the category (an outer opening)
    "entrance": ("sliding", "folding", "glass", "garage", "pack", "set", "window") + PAIR_WORDS + INSIDE_WORDS,
    "door": ("sliding", "folding", "garage", "pack", "set", "window") + PAIR_WORDS + INSIDE_WORDS,
    "glazed_door": ("garage", "pack", "set") + INSIDE_WORDS,
    "terrace_door": ("garage", "pack", "set", "sliding", "folding") + PAIR_WORDS + INSIDE_WORDS,
    "window": ("pack", "set", "door", "curtain", "blind", "shutter", "wall"),
}
NEVER_FLAGS = ("no_derivatives", "unknown")

# 26 Oct 2026: the doors and windows a designer puts in each style family (``wenart.style.vocabulary.STYLE_FAMILIES``;
# "contemporary" as ``details.STYLE_KINDS`` names it). ``styles``: the audited styles that suit the look; ``avoid``: the
# ones that do not; ``not_words``: title words of the other look; ``panelled``: a panelled leaf is out; ``clear_glass``:
# a patterned pane is out; ``bars``: glazing bars allowed; ``leaf`` and ``frames``: what the look builds (the build
# paints every frame in the style's own finish, ``opening_build``).
PERIOD_WORDS = ("colonial", "victorian", "georgian", "edwardian", "regency", "sash", "double hung", "carriage",
                "craftsman", "bungalow", "bungelow", "traditional", "cottage", "arched", "arch ", "leaded",
                "classical", "classic", "rustic", "antique", "ornate", "gothic", "castle", "wrought", "decorative",
                "raised panel", "louver", "louvre", "jali")
MODERN_WORDS = ("aluminium", "aluminum", "frameless", "glass wall", "pivot", "contemporary", "minimal", "modern",
                "industrial", "steel")
GLASS_SYSTEM_WORDS = ("sliding", "slide", "folding", "bifold", "bi-fold", "glass", "contemporary", "modern", "minimal",
                      "pivot", "patio")
LIGHT_STYLES = ("scandinavian", "japandi", "modern", "modern minimal", "minimal", "contemporary")
PERIOD_STYLES = ("classic", "rustic", "mediterranean", "traditional", "ornate")
OPENING_LOOK = {
    "light": {"styles": LIGHT_STYLES, "avoid": PERIOD_STYLES, "not_words": PERIOD_WORDS, "panelled": True,
              "clear_glass": True, "bars": False, "leaf": ("flush", "glazed"),
              "frames": ("white", "black", "light wood", "aluminium")},
    "industrial": {"styles": ("industrial",) + LIGHT_STYLES, "avoid": PERIOD_STYLES, "not_words": PERIOD_WORDS,
                   "panelled": True, "clear_glass": True, "bars": True, "leaf": ("flush", "glazed"),
                   "frames": ("black steel", "dark aluminium")},
    "period": {"styles": ("classic", "rustic", "mediterranean"), "avoid": ("industrial", "minimal", "modern minimal"),
               "not_words": MODERN_WORDS, "panelled": False, "clear_glass": False, "bars": True,
               "leaf": ("panelled", "glazed", "flush"), "frames": ("white", "wood", "dark wood")},
}
FAMILY_LOOK = {"scandinavian": "light", "japandi": "light", "modern": "light", "modern minimal": "light",
               "minimal": "light", "contemporary": "light", "industrial": "industrial", "classic": "period",
               "rustic": "period", "mediterranean": "period"}
BARS_MIN_LITES = 6                 # glazing bars: at least this many lites ...
BARS_PER_M2 = 2.0                  # ... and this many per square metre of the model's face (a French door: 16 / 3.9)
MIN_LITE_M2 = 0.01                 # glass pieces smaller than this are no lite (a peephole, a sliver)
AUDIT_FILES = ("results/library/audit/3dwh/audit.json",)     # audits whose vision answers style the extras


def load_extras(path, audits: Optional[Sequence] = None) -> list[dict]:
    """The catalogue's ``extras`` (doors, windows, ... of the 3D Warehouse layer); [] when the file or key is missing.
    26 Oct 2026: an entry that still carries the ``neutral`` placeholder takes the styles of its audit's vision answer
    (``audits``: audit result files; default ``AUDIT_FILES`` under the repository of the catalogue), the rule of
    ``growth_entries.apply_vision_fields``: the catalogue copy was written before that rule read the extras."""
    p = Path(path)
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    # 27 Oct 2026: a door or window audited with its front along the leaf gets the leaf's face as its front
    extras = [leaf_front(e) if isinstance(e, dict) else e for e in data.get("extras") or []]
    if audits is None:
        parents = p.resolve().parents
        audits = [parents[2] / a for a in AUDIT_FILES] if len(parents) > 2 else []
    for a in audits:
        if not Path(a).is_file():
            continue
        try:
            audit_styles(extras, json.loads(Path(a).read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError, AttributeError):   # a broken audit file never stops the build
            continue
    return extras


AUDIT_STYLE_MAX = 3             # = growth_entries.STYLE_MAX: styles taken from one vision answer


def audit_styles(extras: list, audit_doc: Optional[dict]) -> int:
    """The audit's vision styles (at most ``AUDIT_STYLE_MAX``) on the extras that carry only the ``neutral``
    placeholder (pure, in place; the rule of ``growth_entries.apply_vision_fields``, kept here so the build does not
    import the library growth code). Returns how many entries were styled."""
    answers = {str(it["id"]): it["vision"] for it in (audit_doc or {}).get("items") or []
               if isinstance(it, dict) and it.get("id") and isinstance(it.get("vision"), dict)}
    n = 0
    for e in extras:
        if not isinstance(e, dict) or e.get("id") not in answers:
            continue
        if [x for x in e.get("styles") or [] if x != "neutral"]:
            continue
        seen = [x for x in answers[e["id"]].get("styles") or [] if isinstance(x, str) and x and x != "neutral"]
        if not seen:
            continue
        e["styles"] = sorted(set(seen[:AUDIT_STYLE_MAX]))
        e["style_note"] = f"the audit's vision answer names {seen[:AUDIT_STYLE_MAX]} (26 Oct 2026, at load)"
        n += 1
    return n


def style_family(style) -> Optional[str]:
    """The style family of a style (``style.json``'s ``family``) or a family name, lower case; None without one."""
    fam = style.get("family") if isinstance(style, dict) else style
    fam = str(fam or "").strip().lower()
    return fam or None


def look_of(style) -> Optional[dict]:
    """``OPENING_LOOK`` of a style (with its ``name`` and the ``family``), None for no or an unknown family."""
    fam = style_family(style)
    name = FAMILY_LOOK.get(fam or "")
    return dict(OPENING_LOOK[name], name=name, family=fam) if name else None


def entry_styles(entry: dict) -> list[str]:
    """The audited styles of a model without the ``neutral`` placeholder, lower case, each once, in order."""
    out = []
    for s in entry.get("styles") or []:
        s = str(s or "").strip().lower()
        if s and s != "neutral" and s not in out:
            out.append(s)
    return out


def _word(title: str, words) -> Optional[str]:
    """The first of ``words`` that starts a word of ``title`` (" arch " matches "arched", never "search")."""
    for w in words:
        if re.search(r"(?<![a-z0-9])" + re.escape(w.strip()) + (r"(?![a-z0-9])" if w.endswith(" ") else ""), title):
            return w.strip()
    return None


def _panelled(title: str) -> bool:
    """A title that names a panelled leaf ("6 Panel", "2 Panels", "panelled"); "3-panel" or "4 Panel" of a sliding or
    folding glass system counts its leaves, not raised panels."""
    if not re.search(r"panel", title) or re.search(r"\d\s*-\s*panel", title):
        return False
    return _word(title, GLASS_SYSTEM_WORDS) is None


def look_fit(entry: dict, look: Optional[dict], panes: Optional[dict] = None,
             category: Optional[str] = None) -> tuple[Optional[int], str]:
    """``(rank, why)`` of a model for the house's look (pure): rank None = left out, else 0 (the house's own family
    among its audited styles, none avoided), 1 (a style of the look, none avoided), 2 (no audited style), 3 (a style of
    the look and a minority of avoided ones). ``panes``: ``glb_panes`` of its file (None: not judged). Without a look
    every model ranks 0."""
    if look is None:
        return 0, "no style family: every look"
    title = _title(entry)
    w = _word(title, look["not_words"])
    if w:
        return None, f"its title says {w!r}: not the {look['family']} look"
    if look["panelled"] and _panelled(title):
        return None, f"a panelled leaf: not the {look['family']} look"
    styles = entry_styles(entry)
    avoid = [s for s in styles if s in look["avoid"]]
    if styles and 2 * len(avoid) >= len(styles):
        return None, f"audited styles {styles}: mostly {', '.join(avoid)}, not the {look['family']} look"
    if panes:
        if look["clear_glass"] and panes.get("patterned") and category in GLAZED:
            return None, f"patterned glass (an image on its glass): the {look['family']} look wants clear glass"
        if not look["bars"] and int(panes.get("lites") or 0) >= BARS_MIN_LITES \
                and float(panes.get("per_m2") or 0.0) >= BARS_PER_M2:
            return None, (f"glazing bars ({panes['lites']} lites, {panes['per_m2']:.1f} per m2): the "
                          f"{look['family']} look wants no or few bars")
    good = [s for s in styles if s in look["styles"]]
    if look["family"] in styles and not avoid:
        return 0, f"audited styles {styles} name {look['family']}"
    if good and not avoid:
        return 1, f"audited styles {styles} suit the {look['family']} look"
    if not avoid:
        return 2, f"audited styles {styles or ['none']}: look unknown"
    return 3, f"audited styles {styles}: partly {', '.join(avoid)}"


FAMILY_DROP = ("white", "black", "grey", "gray", "timber", "oak", "walnut", "wood", "wooden", "door", "doors", "panel",
               "panels", "leaf", "leaves")


def family_key(entry: dict) -> str:
    """The model family of a door or window (pure): the variants of one series share it ("Window1 1" and "Window1 3",
    "Valdi - Folding Sliding Door - 3 Door White" and "- 4 Door Timber": the title without its numbers, colours and
    leaf counts, the first two parts of a "brand - product - variant" title); a title with nothing to strip is its own
    family (seven different "Front Door" models are seven families)."""
    title = re.sub(r"\[[^\]]*\]", " ", str(entry.get("title") or entry.get("name") or "").lower())
    title = " ".join(title.replace("_", " ").split())
    parts = [p.strip() for p in title.split(" - ") if p.strip()]
    stem = " - ".join(parts[:2]) if len(parts) >= 3 else title
    words = [w for w in re.split(r"\s+", stem) if w]
    kept = [w for w in words if not re.match(r"^\d", w)]
    if len(parts) >= 3:
        tail = [w for w in " ".join(parts[2:]).split() if not re.match(r"^\d", w) and w not in FAMILY_DROP]
        if not tail:
            return f"{entry.get('type')}:{' '.join(kept)}"
        return f"id:{entry.get('id')}"
    if kept != words and kept:
        return f"{entry.get('type')}:{' '.join(kept)}"
    return f"id:{entry.get('id')}"


GLASS_NAME_WORDS = ("glass", "glas", "glazing", "pane", "vidro", "vitre", "cam_", "camlar", "transparent",
                    "translucent", "window_glass")  # = opening_build.GLASS_WORDS
GLAZED = ("window", "glazed_door", "terrace_door")


def glb_glass(path) -> Optional[bool]:
    """Whether a GLB model has a see-through material (pure: the file's JSON chunk): a material named like glass, one
    with a blended alpha under 0.7, or with ``KHR_materials_transmission`` over 0.5. None when the file cannot be
    read. 25 Oct 2026: real04's "Window1 1" (3D Warehouse) has panes painted on an opaque texture: chosen for every
    window it shut the daylight out of the south rooms (+4..+7 EV)."""
    import struct

    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] != b"glTF":
                return None
            n, kind = struct.unpack("<II", f.read(8))
            if kind != 0x4E4F534A:                     # "JSON"
                return None
            doc = json.loads(f.read(n).decode("utf-8"))
    except (OSError, ValueError, struct.error):
        return None
    for m in doc.get("materials") or []:
        name = str(m.get("name") or "").lower()
        if any(w in name for w in GLASS_NAME_WORDS):
            return True
        pbr = m.get("pbrMetallicRoughness") or {}
        alpha = (pbr.get("baseColorFactor") or [1, 1, 1, 1])[3:4] or [1.0]
        if m.get("alphaMode") == "BLEND" and float(alpha[0]) < 0.7:
            return True
        trans = ((m.get("extensions") or {}).get("KHR_materials_transmission") or {}).get("transmissionFactor")
        if trans is not None and float(trans) > 0.5:
            return True
    return False


GLAZED_DOOR_MIN_SHARE = 0.45     # a terrace or glazed door model is at least this much glass (25 Oct 2026)


def _glb_json(path) -> Optional[dict]:
    import struct

    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] != b"glTF":
                return None
            n, kind = struct.unpack("<II", f.read(8))
            if kind != 0x4E4F534A:                     # "JSON"
                return None
            return json.loads(f.read(n).decode("utf-8"))
    except (OSError, ValueError, struct.error):
        return None


def _glass_material(m: dict) -> bool:
    name = str(m.get("name") or "").lower()
    if any(w in name for w in GLASS_NAME_WORDS):
        return True
    pbr = m.get("pbrMetallicRoughness") or {}
    alpha = (pbr.get("baseColorFactor") or [1, 1, 1, 1])[3:4] or [1.0]
    if m.get("alphaMode") == "BLEND" and float(alpha[0]) < 0.7:
        return True
    trans = ((m.get("extensions") or {}).get("KHR_materials_transmission") or {}).get("transmissionFactor")
    return trans is not None and float(trans) > 0.5


def glb_glass_share(path) -> Optional[float]:
    """The share of a door or window model's face that is glass (pure: the GLB's JSON chunk; 25 Oct 2026, user on
    real04's roof terrace door, a wood door with four small panes: "is the door to the terrace ok?"): the summed
    face areas (the two largest sides of the box) of the glass primitives' position bounds over the model's. None
    when the file cannot be read or holds no bounds."""
    doc = _glb_json(path)
    if doc is None:
        return None
    mats = doc.get("materials") or []
    acc = doc.get("accessors") or []
    glass, lo, hi = 0.0, [math.inf] * 3, [-math.inf] * 3
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            a = (prim.get("attributes") or {}).get("POSITION")
            if a is None or a >= len(acc) or not acc[a].get("min") or not acc[a].get("max"):
                continue
            mn, mx = [float(v) for v in acc[a]["min"][:3]], [float(v) for v in acc[a]["max"][:3]]
            lo = [min(x, y) for x, y in zip(lo, mn)]
            hi = [max(x, y) for x, y in zip(hi, mx)]
            m = prim.get("material")
            if m is not None and m < len(mats) and _glass_material(mats[m]):
                e = sorted((y - x for x, y in zip(mn, mx)), reverse=True)
                glass += e[0] * e[1]
    if not math.isfinite(lo[0]):
        return None
    e = sorted((y - x for x, y in zip(lo, hi)), reverse=True)
    face = e[0] * e[1]
    return None if face <= 0 else round(min(1.0, glass / face), 3)


# --- the panes of a model (26 Oct 2026) ---------------------------------------------------------------------------

def _glb_parts(path) -> Optional[tuple[dict, bytes]]:
    """``(json, bin)`` chunks of a GLB file; None when it cannot be read."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if len(data) < 20 or data[:4] != b"glTF":
        return None
    off, doc, binc = 12, None, b""
    try:
        while off + 8 <= len(data):
            n, kind = struct.unpack_from("<II", data, off)
            off += 8
            chunk = data[off:off + n]
            off += n
            if kind == 0x4E4F534A and doc is None:            # "JSON"
                doc = json.loads(chunk.decode("utf-8"))
            elif kind == 0x004E4942 and not binc:             # "BIN"
                binc = chunk
    except (ValueError, struct.error):
        return None
    return (doc, binc) if isinstance(doc, dict) else None


_FORMATS = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _accessor(doc: dict, binc: bytes, index) -> Optional[list]:
    """The values of a glTF accessor in the BIN chunk (tuples for vectors, ints / floats for scalars); None for one
    this reader does not take (sparse, quantised, another buffer, out of range)."""
    accs = doc.get("accessors") or []
    if not isinstance(index, int) or not 0 <= index < len(accs):
        return None
    acc = accs[index]
    views = doc.get("bufferViews") or []
    bv_i = acc.get("bufferView")
    if not isinstance(bv_i, int) or not 0 <= bv_i < len(views) or acc.get("sparse"):
        return None
    bv = views[bv_i]
    fmt = _FORMATS.get(acc.get("componentType"))
    width = _WIDTH.get(acc.get("type"))
    if fmt is None or width is None or int(bv.get("buffer", 0)) != 0 or (acc.get("normalized") and fmt[0] != "f"):
        return None
    count = int(acc.get("count") or 0)
    size = fmt[1] * width
    stride = int(bv.get("byteStride") or size)
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    if count <= 0 or base + stride * (count - 1) + size > len(binc):
        return None
    if stride == size:
        flat = struct.unpack_from(f"<{count * width}{fmt[0]}", binc, base)
    else:
        flat = []
        for i in range(count):
            flat.extend(struct.unpack_from(f"<{width}{fmt[0]}", binc, base + i * stride))
    return list(flat) if width == 1 else [tuple(flat[i:i + width]) for i in range(0, len(flat), width)]


def _node_matrix(node: dict) -> list:
    """The 4 x 4 row-major local matrix of a glTF node (``matrix`` or translation, rotation, scale)."""
    m = node.get("matrix")
    if isinstance(m, list) and len(m) == 16:
        return [[float(m[c * 4 + r]) for c in range(4)] for r in range(4)]
    t = [float(v) for v in (node.get("translation") or [0.0, 0.0, 0.0])]
    x, y, z, w = [float(v) for v in (node.get("rotation") or [0.0, 0.0, 0.0, 1.0])]
    s = [float(v) for v in (node.get("scale") or [1.0, 1.0, 1.0])]
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[r[i][0] * s[0], r[i][1] * s[1], r[i][2] * s[2], t[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]


def _mul(a: list, b: list) -> list:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _identity() -> list:
    return [[1.0 if r == c else 0.0 for c in range(4)] for r in range(4)]


def _mesh_nodes(doc: dict) -> list[tuple[int, list]]:
    """``[(mesh index, world matrix)]`` of every node that draws a mesh (the default scene, else every root node)."""
    nodes = doc.get("nodes") or []
    scenes = doc.get("scenes") or []
    if scenes:
        roots = list((scenes[int(doc.get("scene") or 0)] if int(doc.get("scene") or 0) < len(scenes)
                      else scenes[0]).get("nodes") or [])
    else:
        children = {c for n in nodes for c in n.get("children") or []}
        roots = [i for i in range(len(nodes)) if i not in children]
    out, stack = [], [(root, _identity()) for root in roots]
    seen = set()
    while stack:
        i, parent = stack.pop()
        if not isinstance(i, int) or not 0 <= i < len(nodes) or i in seen:
            continue
        seen.add(i)
        world = _mul(parent, _node_matrix(nodes[i]))
        if isinstance(nodes[i].get("mesh"), int):
            out.append((nodes[i]["mesh"], world))
        stack.extend((c, world) for c in nodes[i].get("children") or [])
    if not out and not nodes:                                  # meshes without nodes: one each, unmoved
        out = [(k, _identity()) for k in range(len(doc.get("meshes") or []))]
    return out


def _textured_glass(m: dict) -> bool:
    """A glass material with an image on its colour (a patterned or frosted pane)."""
    if not _glass_material(m):
        return False
    pbr = m.get("pbrMetallicRoughness") or {}
    sg = (m.get("extensions") or {}).get("KHR_materials_pbrSpecularGlossiness") or {}
    return bool(pbr.get("baseColorTexture") or sg.get("diffuseTexture"))


def glb_panes(path) -> Optional[dict]:
    """The panes of a door or window model (pure; 26 Oct 2026, real06's "French Door": eight small lites per leaf
    under a dark lattice in a Scandinavian house): ``{"lites": n, "per_m2": n per square metre of the model's face,
    "patterned": a glass material carries an image, "glass_m2"}``. A lite is a connected piece of the glass triangles
    (vertices joined within 1 mm, so a pane's two faces are one piece), pieces whose outlines on the model's face
    overlap by half merged (a pane of two loose faces), pieces under ``MIN_LITE_M2`` left out. The face is the plane
    of the model's two longest sides (its depth is the shortest). None when the file cannot be read; ``lites`` None
    when its geometry cannot be read (only the materials are judged)."""
    parts = _glb_parts(path)
    if parts is None:
        return None
    doc, binc = parts
    mats = doc.get("materials") or []
    patterned = any(_textured_glass(m) for m in mats if isinstance(m, dict))
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    tris = []
    meshes = doc.get("meshes") or []
    for mi, world in _mesh_nodes(doc):
        if not 0 <= mi < len(meshes):
            continue
        for prim in meshes[mi].get("primitives") or []:
            if int(prim.get("mode", 4)) != 4:
                continue
            a = (prim.get("attributes") or {}).get("POSITION")
            m = prim.get("material")
            glassy = isinstance(m, int) and 0 <= m < len(mats) and _glass_material(mats[m])
            acc = (doc.get("accessors") or [])[a] if isinstance(a, int) and a < len(doc.get("accessors") or []) \
                else {}
            if not glassy and acc.get("min") and acc.get("max"):
                mn, mx = acc["min"][:3], acc["max"][:3]       # a frame part: the corners of its box are enough
                pos = [(x, y, z) for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])]
            else:
                pos = _accessor(doc, binc, a)
            if not pos:
                continue
            pts = [tuple(world[r][0] * p[0] + world[r][1] * p[1] + world[r][2] * p[2] + world[r][3]
                         for r in range(3)) for p in pos]
            for p in pts:
                for k in range(3):
                    lo[k], hi[k] = min(lo[k], p[k]), max(hi[k], p[k])
            if not glassy:
                continue
            idx = _accessor(doc, binc, prim.get("indices")) if prim.get("indices") is not None \
                else list(range(len(pts)))
            if not idx:
                continue
            tris += [(pts[idx[i]], pts[idx[i + 1]], pts[idx[i + 2]]) for i in range(0, len(idx) - 2, 3)
                     if max(idx[i], idx[i + 1], idx[i + 2]) < len(pts)]
    if not math.isfinite(lo[0]):
        return {"lites": None, "per_m2": None, "patterned": patterned, "glass_m2": None}
    ext = [hi[k] - lo[k] for k in range(3)]
    depth = min(range(3), key=lambda k: ext[k])
    u, v = [k for k in range(3) if k != depth]
    face = ext[u] * ext[v]
    parent: dict = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def key(p):
        return tuple(int(round(c * 1000.0)) for c in p)

    for t in tris:
        ks = [key(p) for p in t]
        for k in ks[1:]:
            ra, rb = find(ks[0]), find(k)
            if ra != rb:
                parent[ra] = rb
    boxes: dict = {}
    for t in tris:
        root = find(key(t[0]))
        b = boxes.setdefault(root, [math.inf, math.inf, -math.inf, -math.inf])
        for p in t:
            b[0], b[1] = min(b[0], p[u]), min(b[1], p[v])
            b[2], b[3] = max(b[2], p[u]), max(b[3], p[v])
    pieces = list(boxes.values())
    merged = True
    while merged:                                   # a pane of two loose faces: one lite
        merged = False
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                a, b = pieces[i], pieces[j]
                w = min(a[2], b[2]) - max(a[0], b[0])
                h = min(a[3], b[3]) - max(a[1], b[1])
                small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                if w > 0 and h > 0 and w * h >= 0.5 * small:
                    pieces[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del pieces[j]
                    merged = True
                    break
            if merged:
                break
    lites = [b for b in pieces if (b[2] - b[0]) * (b[3] - b[1]) >= MIN_LITE_M2]
    glass = sum((b[2] - b[0]) * (b[3] - b[1]) for b in lites)
    return {"lites": len(lites), "per_m2": round(len(lites) / face, 3) if face > 1e-9 else None,
            "patterned": patterned, "glass_m2": round(glass, 4)}


def _usable(entry: dict, mode: str) -> bool:
    from wenart.blender.site_models import MIN_VISION_QUALITY, vision_quality

    status = str(((entry.get("audit") or {}).get("status")) or "").lower()
    if status not in ("keep", "fix"):
        return False
    q = vision_quality(entry)
    if q is not None and q < MIN_VISION_QUALITY:
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
    """(width, depth, height) of a model in metres in its front frame: the catalogue box ``bbox_m``, which the
    catalogue writes in the piece frame already (``catalog.oriented_bbox``: the model box turned by its front axis;
    ``furniture.fit_vertices`` builds in that frame).

    27 Oct 2026 (user on real06's entrance: "correct the door"): this read swapped width and depth once more for a front
    along x, so a door whose audit put its front along the leaf ("Modern Single Door", front -X: the piece box 0.13 m
    wide and 1.07 m deep) passed as a 1.07 m leaf and was built turned 90 degrees, its 13 cm edge stretched to the
    opening's width (fit scale 6.1 x 0.1 x 0.9: a narrow oak strip beside a dark gap), while every door modelled with
    its face across x (front +X: "Front Door", "PVC Doors") was read 0.25 m wide and never used."""
    box = entry.get("bbox_m")
    if not box or len(box) < 3 or min(float(v) for v in box[:3]) <= 0.0:
        return None
    w, d, h = (float(v) for v in box[:3])
    return w, d, h


FRONT_TURN = {"-X": "-Y", "+X": "+Y", "-Y": "-X", "+Y": "+X"}


def leaf_front(entry: dict) -> dict:
    """A door or window model whose piece box is deeper than wide has its front along its leaf (an audit that read "a
    door has no front" and turned it, 27 Oct 2026): the front is turned 90 degrees (``FRONT_TURN``: the leaf's face
    becomes the front, the sign kept) and the box with it, noted ``front_axis_fixed``; any other entry is returned as
    it is (pure; a new dict when changed). A door or a window is always wider than its frame is deep."""
    box = entry.get("bbox_m")
    if entry.get("type") not in ("door", "window") or not box or len(box) < 3:
        return entry
    try:
        w, d, h = (float(v) for v in box[:3])
    except (TypeError, ValueError):
        return entry
    front = str(entry.get("front_axis") or "-Y").upper()
    if not (d > w > 0.0) or front not in FRONT_TURN:
        return entry
    out = dict(entry, front_axis=FRONT_TURN[front], bbox_m=[d, w, h] + list(box[3:]))
    out["front_axis_fixed"] = {"was": front, "box_was": list(box[:3]),
                               "reason": f"its piece box was {w:.2f} m wide and {d:.2f} m deep with the front {front}: "
                                         f"the front ran along the leaf; turned to {FRONT_TURN[front]} (the leaf's "
                                         f"face)"}
    return out


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
        if category in ("glazed_door", "terrace_door") and not (_has(title, WORDS[category])
                                                                or "glass" in (e.get("material_tags") or [])):
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
            0 if status == "keep" else 1, RANK_STEP * round(sum(min(e, 1.0) for e in errs) / len(errs) / RANK_STEP),
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
            "licence_url", "licence_flag", "commercial_safe", "attribution", "author", "title", "uid",
            "front_axis_fixed")
    out = {k: entry.get(k) for k in keys if entry.get(k) is not None}
    out.update(method="library", asset_id=entry.get("id"), library=entry.get("source") or "3dwh")
    return out


# 26 Oct 2026 (architect D5, ``architect_actions.DOOR_KINDS``): the door kinds no library category holds (a sectional
# garage door, a pair or a row of solid leaves: the categories' doors are one solid leaf or glass): the parametric door
NO_LIBRARY_KINDS = ("garage_sectional", "double", "sliding_pair", "folding")
GLAZED_KINDS = ("french", "glazed_sliding", "glazed_folding")


def door_kind_of(o: dict) -> Optional[str]:
    """The kind the architect gave a door (D5: ``door_type``, else ``door_decision.kind``), None without one."""
    dec = o.get("door_decision") if isinstance(o.get("door_decision"), dict) else {}
    return o.get("door_type") or dec.get("kind")


def is_glazed_door(o: dict) -> bool:
    """A door the architect made glazed (D5's glazed kinds, or ``glazed``: a gap made a glazed door)."""
    return o.get("type") == "door" and (bool(o.get("glazed")) or door_kind_of(o) in GLAZED_KINDS)


def categorise(building: dict, outer: Sequence[dict]) -> dict[str, str]:
    """``{opening id: category}`` of the outer openings (``site.outer_openings`` records). 26 Oct 2026 (architect
    D5): a door's decided kind first: a glazed door is a ``glazed_door`` (``WIDE_DOOR_M`` or wider) or a
    ``terrace_door``; a sectional garage door or a pair of solid leaves has no category (the parametric door); the
    main entrance is an ``entrance`` when its kind is ``entrance`` or it has none (real06: a 2.95 m drawn sliding door
    was the main entrance record, was matched against single front doors, none fitted, and the parametric builder
    made one flat leaf as wide as the opening; D5 makes it a glazed sliding door)."""
    entrances = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
                 and not r.get("into_air") and not r.get("below_ground")]
    main = next((r.get("door_id") for r in entrances if r.get("main")), None)
    if main is None and entrances:
        main = entrances[0].get("door_id")
    out = {}
    for rec in outer:
        o = rec["opening"]
        width = _number(o.get("width")) or 0.0
        kind = door_kind_of(o) if o.get("type") == "door" else None
        if kind in NO_LIBRARY_KINDS:
            continue
        if is_glazed_door(o):
            out[o["id"]] = "glazed_door" if width >= WIDE_DOOR_M else "terrace_door"
        elif o.get("type") == "door" and o.get("outside_door") and o["id"] != main:
            # 25 Oct 2026 (architect A3): a door to a terrace or balcony room is a glazed outside door
            out[o["id"]] = "glazed_door" if width >= WIDE_DOOR_M else "terrace_door"
        elif o.get("type") == "door":
            entrance = kind == "entrance" or (o["id"] == main and kind is None)
            out[o["id"]] = "entrance" if entrance else ("glazed_door" if width >= WIDE_DOOR_M else "door")
        elif o.get("type") == "window":
            out[o["id"]] = "window"
    return out


SINGLE_LEAF = ("entrance", "door", "terrace_door")       # one panel: the model is one door
CATEGORIES = ("entrance", "door", "glazed_door", "terrace_door", "window")
SINGLE_LEAF_MAX_M = 1.25           # = parametric.SINGLE_LEAF_MAX_M: no one-leaf model is stretched wider (27 Oct 2026)


def fit(entry: dict, category: str, width: float, height: float) -> Optional[tuple[int, float]]:
    """``(panels, log proportion error)`` of a model in an opening ``width`` x ``height`` (pure), None when it does
    not fit: the error over ``ASPECT_TOL`` or the height beyond ``MAX_SCALE`` of the model's. 27 Oct 2026 (user on
    real06's entrance: "correct the door"): a one-leaf model fills its opening as a real door does, so an opening wider
    than ``SINGLE_LEAF_MAX_M`` takes no one-leaf model (the parametric door: the entrance's leaf with glazed side
    lights, D5's pair or glazed door), never one leaf stretched past a real leaf's width."""
    size = model_size(entry)
    if size is None or width <= 0 or height <= 0:
        return None
    w, _d, h = size
    if category in SINGLE_LEAF:
        if width > SINGLE_LEAF_MAX_M + 1e-6:
            return None
        n, err = 1, abs(math.log((width / height) / (w / h)))
    else:
        n, err = best_panels(width, height, w / h)
    if err <= ASPECT_TOL and abs(math.log(height / h)) <= math.log(MAX_SCALE):
        return n, err
    return None


def _checked(cands: list, category: str, look: Optional[dict], assets_dir, cache: dict
             ) -> tuple[list, dict, dict]:
    """``(kept, left out {id: why}, look rank {id: rank})`` of a category's candidates: see-through glass and the
    glass share with the files (25 Oct 2026), then the house's look (``look_fit``; the panes with the files)."""
    kept, left, rank = [], {}, {}

    def cached(what, fn, path):
        if (what, str(path)) not in cache:
            cache[(what, str(path))] = fn(path)
        return cache[(what, str(path))]

    for e in cands:
        path = Path(assets_dir) / str(e.get("glb") or "") if assets_dir is not None else None
        if path is not None and category in GLAZED:
            if cached("glass", glb_glass, path) is False:
                left[e["id"]] = "no see-through glass"
                continue
        if path is not None and category in ("glazed_door", "terrace_door"):
            # a door to a terrace is mostly glass (a wood door with small panes is an inside or a front door)
            share = cached("share", glb_glass_share, path)
            if share is not None and share < GLAZED_DOOR_MIN_SHARE:
                left[e["id"]] = f"glass {share:.0%} of its face (< {GLAZED_DOOR_MIN_SHARE:.0%})"
                continue
        panes = None
        if path is not None and look is not None:
            panes = cached("panes", glb_panes, path)
        r, why = look_fit(e, look, panes, category)
        if r is None:
            left[e["id"]] = why
            continue
        kept.append(e)
        rank[e["id"]] = (r, why)
    return kept, left, rank


def plan(building: dict, outer: Sequence[dict], extras: Sequence[dict], mode: str = "relaxed",
         assets_dir=None, style=None, notes: Optional[list] = None) -> dict[str, dict]:
    """``{opening id: {"asset", "panels", "category", "aspect_error", "family", "look", "reason"}}`` for the outer
    openings ``outer`` (``site.outer_openings`` records: ``opening``, ``bottom``, ``top``). With ``assets_dir`` a
    window or glazed door model must have see-through glass (``glb_glass``; a model whose file is not there is not
    judged) and its panes are judged (``glb_panes``).

    26 Oct 2026: ``style`` (the style profile or its family name) picks the look (``look_of``, ``look_fit``); every
    category takes one model family (``family_key``): the family whose best model ranks first by look, then covers
    the most of the category's openings, then by ``_rank_key``; each opening takes the family's member that fits it
    best, and an opening no member fits keeps the parametric opening in the style's finish. ``notes`` (a list) gets
    ``{"kind": "left_out", "category", "models": {id: why}}`` per category and ``{"kind": "parametric", "id",
    "category", "reason"}`` per opening left to the parametric build."""
    look = look_of(style)
    cats = categorise(building, outer)
    # 26 Oct 2026 (architect D5): a glazed door narrower than WIDE_DOOR_M tries the house's glazed door family first,
    # so the glazed doors share one look where a model fits within its stretch caps; else its terrace door
    narrow_glazed = [rec["opening"]["id"] for rec in outer if is_glazed_door(rec["opening"])
                     and cats.get(rec["opening"]["id"]) == "terrace_door"]
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
    cache: dict = {}
    notes = notes if notes is not None else []
    for category in CATEGORIES:
        ids = [i for i, c in cats.items() if c == category and i in sizes and i not in out]
        also = [i for i in narrow_glazed if i in sizes and i not in out] if category == "glazed_door" else []
        if not ids and not also:
            continue
        cands, left, look_rank = _checked(candidates(extras, category, mode), category, look, assets_dir, cache)
        if left:
            notes.append({"kind": "left_out", "category": category, "models": left})
        if not cands:
            continue
        openings = [sizes[i] for i in ids + also]
        ranked = sorted(cands, key=lambda e: (look_rank[e["id"]][0], _rank_key(e, category, openings)))
        families: dict[str, list] = {}
        for e in ranked:
            families.setdefault(family_key(e), []).append(e)
        best = None
        for key, members in families.items():
            covered = sum(1 for w, h in openings if any(fit(m, category, w, h) for m in members))
            if not covered:
                continue
            head = members[0]
            order = (look_rank[head["id"]][0], -covered, _rank_key(head, category, openings))
            if best is None or order < best[0]:
                best = (order, key, members)
        if best is None:
            for oid in ids:
                notes.append({"kind": "parametric", "id": oid, "category": category,
                              "reason": f"no library {category.replace('_', ' ')} fits {sizes[oid][0]:.2f} x "
                                        f"{sizes[oid][1]:.2f} m: the parametric opening in the style's finish"})
            continue
        _order, key, members = best
        for oid in ids + also:
            width, height = sizes[oid]
            fits = [(look_rank[m["id"]][0], f[1], i, m, f) for i, m in enumerate(members)
                    for f in [fit(m, category, width, height)] if f is not None]
            if not fits and oid in also:
                continue                         # no member of the glazed door family fits: its terrace door next
            if not fits:
                head = members[0]
                notes.append({"kind": "parametric", "id": oid, "category": category, "family": key,
                              "reason": f"no model of the building's {category.replace('_', ' ')} family "
                                        f"{str(head.get('title') or head.get('id'))[:40]!r} fits {width:.2f} x "
                                        f"{height:.2f} m: the parametric opening in the style's finish keeps one "
                                        f"door and window language"})
                continue
            _r, err, _i, e, (n, err) = min(fits, key=lambda t: t[:3])
            rank, why = look_rank[e["id"]]
            styled = f"; {look['family']} look: {why}" if look is not None else ""
            out[oid] = {"asset": asset_of(e), "panels": n, "category": category,
                        "aspect_error": round(err, 4), "outward": outward.get(oid), "family": key,
                        "look": None if look is None else {"family": look["family"], "name": look["name"],
                                                           "rank": rank, "styles": entry_styles(e)},
                        "reason": f"library {category.replace('_', ' ')} {e.get('id')} "
                                  f"({str(e.get('title') or '')[:40]!r}) in {n} panel(s) of "
                                  f"{width / n:.2f} x {height:.2f} m (proportions off by "
                                  f"{(math.exp(err) - 1) * 100:.0f} %; the documents draw the opening, "
                                  f"not its product); the building's one {category.replace('_', ' ')} family"
                                  f"{styled}; frames in the style's finish"}
    return out
