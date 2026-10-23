"""3D Warehouse (SketchUp) models as a library source for the relaxed licence mode (user request of 23 Oct 2026).

What: the user's Google Drive file "3D Warehouse Furniture.zip" (``DRIVE_FILE_ID``, ``ZIP_BYTES``) holds GLB exports of
3D Warehouse models in folders (furniture, decor, trees, doors, windows). The user's decision of 23 Oct 2026: ignore the
licence questions, use the source in ``relaxed`` mode only, ``commercial_safe: no``; pick the whole zip. So every entry
carries the licence text ``LICENCE`` (``3DWH-UNREVIEWED``), ``licence_flag: non_commercial`` (the flag the commercial
mode leaves out), ``licence_declared_by: uploader`` and the credit fields; ``wenart.furniture.catalog`` maps the text
onto the flag.

- ``download_url`` (``drive.usercontent.google.com``, ``confirm=t``: the large-file form without the virus-scan page;
  the file must be shared as "anyone with the link"), ``approval`` (``results/library/growth/approved_3dwh.json``: the
  user's OK of the whole zip, the ingest gate), ``extract`` (only ``.glb`` members, no absolute path, no ``..``, no
  link; UTF-8 names stored without the zip's UTF-8 flag read as UTF-8; each model written as ``<uid>.glb`` with
  ``members.json`` mapping it to its member path, so no long or foreign name reaches the file system; complete files
  kept: resume), ``list_glbs``. The zip holds one folder per model (``Lamps/<model name> [hex id]/model.glb``): a
  file name that names no model (``GENERIC_STEMS``) takes its folder's name.
- ``name_type(rel)``: the type of a model from its folder and file name, never guessed silently. The deepest folder
  that names a group (``GROUP_WORDS``: furniture, decor, trees, doors, windows) gives the group; the file name, then
  the folders (deepest first), give the candidate types through ``wenart.assets.audit.keywords`` (the library's title
  words in many languages) plus the vegetation and opening words here (``EXTRA_KEYWORDS``). A model whose names give no
  type is ``unmapped`` and goes to the review list.
- ``choose(cands, extents)``: the candidate type, unit and up axis that put the measured box inside the type's real
  size range (``wenart.furniture.sizes``; ``EXTRA_RANGES`` for trees, doors and windows): metres first (glTF's unit),
  then inches (SketchUp's own unit), centimetres, millimetres, feet; a model exported Z-up without the glTF turn is
  turned only when that is the only way it fits. Units count as known only when a unit puts the box inside the range.
- ``fixup``: the SketchUp export fixes written into a new GLB (``<assets>/models/3dwh/<uid>.glb``): a new root node
  with the unit scale, the up-axis turn and the move that puts the origin at the floor centre (bounding-box centre in
  plan, bottom at 0); every material ``doubleSided`` (SketchUp faces are one-sided and often reversed); roughness and
  metallic by material name and type (``MATERIAL_RULES``, ``TYPE_ROUGHNESS``: these files carry only colour and
  textures, and glTF's defaults, metallic 1 and roughness 1 when the factors are left out, render as dark metal); an
  alpha below 1 blends. The front is not turned in the file: the catalogue entry records it (``growth_entries
  .front_of``: the type's geometric rule, else SketchUp's Front-view convention, -Y, with low confidence, and the
  audit's vision answer names it).
- ``process(job)``: one model end to end (name, measure, choose, fix-up), resumable by the source file's sha256 and
  ``FIX_VERSION``; ``entry_fields``, ``attribution``, ``DATASET``, ``notice``.

Why: the user's 3D Warehouse picks add real products (sanitary ware, kitchens, designer furniture) the open sources
lack; SketchUp exports need the fixes above before the audit and the fit can use them.

How: pure Python and numpy (``wenart.assets.audit.glbmesh`` reads the GLB); the GLB is rewritten with the same binary
chunk and a new JSON chunk, so the meshes and textures stay byte-identical. Trees, doors and windows get their fixed
file and a record (``extras``) for the later hooks (doors and windows scaled to the drawn openings, trees picked by
crown size: not built yet); the furniture and decor go through the library audit.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable, Optional

SOURCE = "3dwh"
UID_PREFIX = "3dwh_"
UID_HEX = 24                                     # uid = prefix + 24 hex digits of sha256(path in the zip)
DRIVE_FILE_ID = "1nSHF5dvjLLcpruowus8zZUx8kSiDxkjD"
ZIP_NAME = "3D Warehouse Furniture.zip"
ZIP_ROOT = "3D Warehouse Furniture"               # the zip's top folder: no group ("Furniture" named every model)
ZIP_BYTES = 6_261_344_770                         # the Drive file's size (Drive metadata, read on 23 Oct 2026)
DOWNLOAD_URL = "https://drive.usercontent.google.com/download?id={id}&export=download&confirm=t"
DRIVE_PAGE = "https://drive.google.com/file/d/{id}/view"
LIBRARY_ROOT = "/workspace/library/3dwh"          # zip/ (the download), glb/ (the extracted models) on the volume
LICENCE = "3DWH-UNREVIEWED"                    # all caps: wenart.blender.furniture compares upper-case
LICENCE_FLAG = "non_commercial"
LICENCE_DECLARED_BY = "uploader"
LICENCE_URL = "https://3dwarehouse.sketchup.com/"
DATASET_NAME = "3D Warehouse models (SketchUp), the user's zip \"3D Warehouse Furniture.zip\""
USER_DECISION = ("user decision of 23 Oct 2026: licence not reviewed; relaxed licence mode only, commercial_safe: no; "
                 "the whole zip picked")
FIX_VERSION = "3dwh-fix-1"                        # part of the resume key: bump when a fix-up rule changes
MIN_FILE_BYTES = 256                              # a GLB below this holds no model (header and an empty scene)
MAX_FILE_BYTES = 400_000_000

# --------------------------------------------------------------------------
# Groups, extra keywords and size ranges
# --------------------------------------------------------------------------

GROUPS = ("furniture", "decor", "vegetation", "door", "window")
# Folder words of the groups (folded tokens; a plural "s" matches). Folders only: a file name never sets the group.
GROUP_WORDS: dict[str, tuple[str, ...]] = {
    "furniture": ("furniture", "furnishing", "furnishings", "mobilya", "mobel", "moebel", "meubles", "mobili",
                  "muebles"),
    "decor": ("decor", "deco", "decoration", "decorative", "accessory", "accessories", "ornament", "dekor",
              "dekorasyon", "aksesuar"),
    "vegetation": ("tree", "vegetation", "landscape", "landscaping", "shrub", "bush", "hedge", "agac", "bitki",
                   "peyzaj"),
    "door": ("door", "kapi"),
    "window": ("window", "pencere"),
}
# The vegetation and opening words (keyword syntax of wenart.assets.audit.keywords: phrases, ~stems).
EXTRA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "tree": ("tree", "agac", "~baum", "arbre", "arbol", "albero", "conifer", "pine tree", "fir tree", "spruce",
             "cypress tree", "oak tree", "birch tree", "maple tree", "olive tree", "willow", "poplar", "cedar",
             "plane tree", "linden", "lime tree"),
    "shrub": ("shrub", "bush", "shrubbery", "cali", "~strauch", "~busch", "arbuste", "arbusto", "topiary"),
    "hedge": ("hedge", "hedgerow", "cit", "~hecke", "haie", "seto"),
    "palm_tree": ("palm tree", "palmiye", "~palme", "palmier", "palmera"),
    "cooktop": ("cooktop", "cook top", "cooktops"),
    "door": ("door", "doors", "doorway", "front door", "entrance door", "interior door", "sliding door",
             "double door", "french door", "barn door", "garage door", "pocket door", "kapi", "~haustur", "porte",
             "puerta", "deur", "dorr"),
    "window": ("window", "windows", "casement", "sash window", "skylight", "pencere", "fenster", "fenetre",
               "ventana", "finestra", "raam"),
}
EXTRA_FAMILY_TYPES: dict[str, tuple[str, ...]] = {"tree": ("tree",), "shrub": ("shrub",), "hedge": ("hedge",),
                                                  "palm_tree": ("palm",), "door": ("door",), "window": ("window",),
                                                  "cooktop": ("stove",)}
VEGETATION_TYPES = ("tree", "shrub", "hedge", "palm")
OPENING_TYPES = ("door", "window")
GROUP_DEFAULT = {"vegetation": "tree", "door": "door", "window": "window"}
# Real sizes of the types outside the size table (designer values: interior and front doors 0.6-2.4 m wide with their
# frame, 1.9-3.0 m high; windows 0.3-6 m; a tree 2-35 m high, a shrub 0.2-3 m, a hedge segment any length): width,
# depth (either orientation), height.
EXTRA_RANGES: dict[str, dict] = {
    "door": {"width": (0.5, 2.6), "depth": (0.02, 0.7), "height": (1.8, 3.2)},
    "window": {"width": (0.25, 6.0), "depth": (0.02, 0.8), "height": (0.25, 3.6)},
    "tree": {"width": (0.5, 30.0), "depth": (0.5, 30.0), "height": (1.5, 40.0)},
    "palm": {"width": (0.5, 15.0), "depth": (0.5, 15.0), "height": (1.5, 30.0)},
    "shrub": {"width": (0.15, 6.0), "depth": (0.15, 6.0), "height": (0.15, 4.0)},
    "hedge": {"width": (0.2, 30.0), "depth": (0.2, 30.0), "height": (0.2, 4.0)},
}
GENERIC_MAX_M = (0.02, 4.0)        # a type without a range: the largest side must lie here
FIT_TOL = 0.15                     # = wenart.furniture.sizes fits() tolerance (the size table's +15 %)
# (factor, unit) tried in this order: glTF says metres; SketchUp's own unit is the inch.
UNIT_FACTORS: tuple[tuple[float, str], ...] = ((1.0, "metres"), (0.0254, "inches"), (0.01, "centimetres"),
                                               (0.001, "millimetres"), (0.3048, "feet"))
UNIT_PENALTY = {"metres": 0, "inches": 1, "centimetres": 2, "millimetres": 2, "feet": 2}
APPLY_UNFIT_RATIO = 0.5            # an unfitting box takes another unit only when its error drops below half

# --------------------------------------------------------------------------
# Materials: roughness / metallic by material name, then by type
# --------------------------------------------------------------------------

# (rule, words, roughness, metallic): the first rule with a word in the folded material name wins.
MATERIAL_RULES: tuple[tuple[str, tuple[str, ...], float, float], ...] = (
    ("mirror", ("mirror", "ayna", "spiegel", "miroir", "espejo", "specchio"), 0.03, 1.0),
    ("glass", ("glass", "glazing", "translucent", "transparent", "crystal", "cam", "glas", "verre", "vidrio", "vetro",
               "plexi", "perspex"), 0.05, 0.0),
    ("chrome", ("chrome", "chromed", "krom", "inox", "stainless", "nickel", "silver", "polished steel",
                "polished metal", "polished aluminium", "polished aluminum"), 0.12, 1.0),
    ("metal", ("metal", "metallic", "steel", "iron", "aluminium", "aluminum", "alu", "brass", "bronze", "copper",
               "gold", "golden", "zinc", "titanium", "celik", "demir", "metall"), 0.35, 1.0),
    ("ceramic", ("ceramic", "porcelain", "enamel", "china", "sanitary", "seramik", "porselen", "keramik"), 0.12, 0.0),
    ("stone_polished", ("marble", "granite", "quartz", "terrazzo", "onyx", "mermer", "granit"), 0.25, 0.0),
    ("gloss", ("gloss", "glossy", "lacquer", "lacquered", "varnish", "varnished", "parlak"), 0.2, 0.0),
    ("plastic", ("plastic", "acrylic", "vinyl", "pvc", "resin", "polypropylene", "abs", "plastik", "akrilik"), 0.4,
     0.0),
    ("leather", ("leather", "leatherette", "deri", "leder", "cuir", "cuero", "pelle"), 0.45, 0.0),
    ("rattan", ("rattan", "wicker", "cane", "hasir", "jute", "seagrass"), 0.75, 0.0),
    ("wood", ("wood", "wooden", "oak", "walnut", "ash", "pine", "teak", "birch", "maple", "beech", "cherry",
              "mahogany", "veneer", "mdf", "plywood", "parquet", "bamboo", "ahsap", "mese", "ceviz", "holz", "bois",
              "madera", "legno", "laminate", "chipboard"), 0.55, 0.0),
    ("fabric", ("fabric", "textile", "cloth", "linen", "cotton", "velvet", "wool", "felt", "upholstery", "boucle",
                "chenille", "tweed", "canvas", "carpet", "rug", "kumas", "stoff", "tissu", "tela", "tessuto", "suede",
                "microfiber", "microfibre", "polyester", "cushion", "pillow", "blanket", "curtain", "drape"), 0.9, 0.0),
    ("paper", ("paper", "cardboard", "kagit", "book", "page"), 0.85, 0.0),
    ("rubber", ("rubber", "silicone"), 0.85, 0.0),
    ("stone", ("stone", "concrete", "cement", "brick", "plaster", "stucco", "beton", "travertine", "slate"), 0.8, 0.0),
    ("bark", ("bark", "trunk", "branch", "kabuk"), 0.9, 0.0),
    ("foliage", ("leaf", "leaves", "foliage", "grass", "plant", "needle", "yaprak", "flower", "petal", "moss"), 0.6,
     0.0),
    ("matte", ("matte", "matt", "mat"), 0.8, 0.0),
    ("paint", ("paint", "painted", "boya"), 0.5, 0.0),
)
# The roughness of a material whose name says nothing (SketchUp's "Color_A01", "Material3"), by the model's type
# (metallic 0: a painted or coloured surface).
TYPE_ROUGHNESS: dict[str, float] = {
    **{t: 0.15 for t in ("toilet", "washbasin", "bathtub", "shower", "vase")},
    **{t: 0.85 for t in ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bed_single", "bed_double",
                         "bunk_bed", "cushion", "throw", "rug", "curtain", "blind")},
    **{t: 0.55 for t in ("table_dining", "table_coffee", "desk", "wardrobe", "dresser", "nightstand", "bookshelf",
                         "tv_unit", "sideboard", "console_table", "side_table", "tall_cabinet", "display_cabinet",
                         "shoe_cabinet", "crib", "chair", "bench", "bar_stool")},
    **{t: 0.3 for t in ("fridge", "stove", "washing_machine", "sink_kitchen")},
    **{t: 0.4 for t in ("floor_lamp", "table_lamp", "pendant_light", "ceiling_light", "clock", "sculpture", "tray",
                        "mirror", "office_chair", "window")},
    **{t: 0.6 for t in ("plant", "plant_small", "plant_large", "potted_plant", "wall_art", "candle")},
    **{t: 0.65 for t in VEGETATION_TYPES},
    "books": 0.8, "basket": 0.75, "bowl": 0.3, "door": 0.5,
}
DEFAULT_ROUGHNESS = 0.6
DEFAULT_MATERIAL = "wenart_3dwh_default"
FIX_ROOT_NAME = "wenart_3dwh_fixup"

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942


class WarehouseError(ValueError):
    """A zip member or GLB that cannot be taken (the reason is the message)."""


# --------------------------------------------------------------------------
# Download, approval, extraction, listing
# --------------------------------------------------------------------------

def download_url(file_id: str = DRIVE_FILE_ID) -> str:
    return DOWNLOAD_URL.format(id=file_id)


def approval(lists) -> dict:
    """The user's OK of the whole zip (``<lists>/growth/approved_3dwh.json``): ``approved_by``, ``approved_utc``,
    ``drive_file_id`` = ``DRIVE_FILE_ID`` and ``rule: whole_zip``; ``PermissionError`` otherwise (nothing is taken)."""
    path = Path(lists) / "growth" / "approved_3dwh.json"
    if not path.is_file():
        raise PermissionError(f"{path} not found: the user has not approved the 3D Warehouse zip; nothing is taken")
    doc = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ("approved_by", "approved_utc") if not doc.get(k)]
    if missing or doc.get("source") != SOURCE:
        raise PermissionError(f"{path}: missing {', '.join(missing) or 'source 3dwh'}: not an approval")
    if doc.get("drive_file_id") != DRIVE_FILE_ID or doc.get("rule") != "whole_zip":
        raise PermissionError(f"{path}: approves {doc.get('drive_file_id')!r} / {doc.get('rule')!r}, not the whole "
                              f"zip {DRIVE_FILE_ID}")
    return doc


def safe_member(name: str) -> Optional[str]:
    """The relative POSIX path of a zip member to extract, or None (a folder, a non-GLB file, an absolute path, a
    ``..`` part, a drive letter or a backslash path that leaves the folder)."""
    text = str(name).replace("\\", "/")
    if text.endswith("/") or not text.lower().endswith(".glb"):
        return None
    p = PurePosixPath(text)
    if p.is_absolute() or any(part in ("..", "") for part in p.parts) or re.match(r"^[A-Za-z]:", text):
        return None
    if any(part.startswith("__MACOSX") or part.startswith("._") for part in p.parts):
        return None
    return str(p)


def _is_link(info: zipfile.ZipInfo) -> bool:
    return (info.external_attr >> 16) & 0o170000 == 0o120000


UTF8_FLAG = 0x800                                 # zip general-purpose flag bit 11: the name is UTF-8
MEMBERS = "members.json"                          # the extraction's map: uid file -> the member's own path


def member_name(info: zipfile.ZipInfo) -> str:
    """A member's name: Python reads a name without the UTF-8 flag as CP437; the user's zip stores UTF-8 names
    (Cyrillic, Turkish, ...) without the flag (pod of 23 Oct 2026: a Russian lamp name became 3-byte CP437 mojibake
    and its folder passed the 255-byte name limit), so such a name is read again as UTF-8 when it decodes as UTF-8."""
    name = info.filename
    if not info.flag_bits & UTF8_FLAG:
        try:
            name = name.encode("cp437").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return name


def extract(zip_path, dest, log: Callable = print) -> dict:
    """The GLB members of the zip into ``dest``, each as ``<uid>.glb`` (``uid_of`` its ``safe_member`` path: a long
    or foreign name never reaches the file system), and ``dest/members.json`` (``[{"id", "rel", "file", "bytes"}]``:
    the member's own path for the typing); a complete file of the same size is kept. Returns ``{"glb", "extracted",
    "kept", "refused": [names], "other": {extension: n}, "bytes", "duplicates": [paths]}``."""
    dest = Path(dest)
    out: dict = {"glb": 0, "extracted": 0, "kept": 0, "refused": [], "other": {}, "bytes": 0, "duplicates": []}
    members: dict[str, dict] = {}
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = member_name(info)
            rel = safe_member(name)
            if rel is None:
                if name.lower().endswith(".glb"):
                    out["refused"].append(name)
                else:
                    ext = PurePosixPath(name.replace("\\", "/")).suffix.lower() or "(none)"
                    out["other"][ext] = out["other"].get(ext, 0) + 1
                continue
            if _is_link(info):
                out["refused"].append(name)
                continue
            uid = uid_of(rel)
            if uid in members:
                out["duplicates"].append(rel)             # the same path twice in the zip: the later one wins
            out["glb"] += 1
            target = dest / f"{uid}.glb"
            members[uid] = {"id": uid, "rel": rel, "file": target.name, "bytes": info.file_size}
            if target.is_file() and target.stat().st_size == info.file_size:
                out["kept"] += 1
                out["bytes"] += info.file_size
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            part = target.with_name(target.name + ".part")
            with zf.open(info) as src, part.open("wb") as fh:
                while True:
                    chunk = src.read(1 << 22)
                    if not chunk:
                        break
                    fh.write(chunk)
            part.replace(target)
            out["extracted"] += 1
            out["bytes"] += info.file_size
    dest.mkdir(parents=True, exist_ok=True)
    (dest / MEMBERS).write_text(json.dumps(sorted(members.values(), key=lambda m: m["rel"]), ensure_ascii=False,
                                           indent=0), encoding="utf-8")
    if out["refused"]:
        log(f"3dwh extract: {len(out['refused'])} member(s) refused (unsafe path or link): {out['refused'][:5]}")
    return out


def uid_of(rel: str) -> str:
    return UID_PREFIX + hashlib.sha256(str(rel).encode("utf-8")).hexdigest()[:UID_HEX]


def list_glbs(root) -> list[dict]:
    """``[{"id", "rel", "file", "folders", "stem", "bytes"}]`` of the models under ``root`` (sorted by ``rel``, the
    member's own path): from ``members.json`` of ``extract`` (``file`` = ``<uid>.glb``, present files only), else
    every ``.glb`` below ``root`` (``file`` = ``rel``)."""
    root = Path(root)
    out = []
    man = root / MEMBERS
    if man.is_file():
        for m in json.loads(man.read_text(encoding="utf-8")):
            p = root / m["file"]
            if p.is_file():
                rel = m["rel"]
                out.append({"id": m["id"], "rel": rel, "file": m["file"],
                            "folders": list(PurePosixPath(rel).parent.parts), "stem": PurePosixPath(rel).stem,
                            "bytes": p.stat().st_size})
        return sorted(out, key=lambda r: r["rel"])
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() != ".glb":
            continue
        rel = p.relative_to(root).as_posix()
        out.append({"id": uid_of(rel), "rel": rel, "file": rel, "folders": list(PurePosixPath(rel).parent.parts),
                    "stem": p.stem, "bytes": p.stat().st_size})
    return out


HASH_SUFFIX = re.compile(r"\s*\[[0-9A-Fa-f]{6,}\]\s*$")     # "lamp chandelier [2693fa00]": the zip's model id
# File names that name no model: the model is its folder ("Lamps/<model name> [2693fa00]/model.glb", pod of 23 Oct)
GENERIC_STEMS = ("model", "scene", "untitled", "mesh", "object", "export", "default", "file", "asset")
TITLE_MAX = 120


def clean_title(stem: str) -> str:
    """A file or folder name as a title: underscores and runs of spaces folded, the zip's ``[hex]`` model id cut
    (``Sofa_IKEA__Kivik [2693fa00]`` -> ``Sofa IKEA Kivik``), at most ``TITLE_MAX`` characters (at a word)."""
    text = HASH_SUFFIX.sub("", re.sub(r"[_]+", " ", str(stem or "")))
    text = " ".join(text.split()).strip(" -.")
    if len(text) > TITLE_MAX:
        text = text[:TITLE_MAX].rsplit(" ", 1)[0].rstrip(" -.,")
    return text


def generic_stem(stem: str) -> bool:
    """``model``, ``Scene``: a file name that is one of ``GENERIC_STEMS`` alone (``Model_123`` keeps its own name)."""
    from wenart.assets.audit import keywords as K
    toks = K.tokens(stem)
    return len(toks) == 1 and toks[0] in GENERIC_STEMS


# --------------------------------------------------------------------------
# Types from names
# --------------------------------------------------------------------------

def _folded_tokens(text: str) -> list[str]:
    from wenart.assets.audit import keywords as K
    return K.tokens(text)


def folder_group(folders: list[str]) -> tuple[Optional[str], Optional[str]]:
    """``(group, folder)``: the deepest folder that names a group (``GROUP_WORDS``), or ``(None, None)``."""
    from wenart.assets.audit import keywords as K
    for folder in reversed(list(folders)):
        toks = _folded_tokens(folder)
        for group, words in GROUP_WORDS.items():
            if any(K._token_eq(t, w) for t in toks for w in words):
                return group, folder
    return None, None


def _family_types(family: str) -> tuple[str, ...]:
    from wenart.assets.audit import growth as G
    from wenart.assets.audit import keywords as K
    if family in EXTRA_FAMILY_TYPES:
        return EXTRA_FAMILY_TYPES[family]
    known = G.known_types()
    return tuple(t for t in K.FAMILY_TYPES.get(family, ()) if t in known)


def named(text: str) -> list[dict]:
    """The families a name gives (library title words plus ``EXTRA_KEYWORDS``), each with its types:
    ``[{"family", "word", "types"}]`` in name order; families with no type of ours left out."""
    from wenart.assets.audit import keywords as K
    out = []
    for f in K.named_families(text, extra=EXTRA_KEYWORDS):
        if f["family"] in K.IGNORED_FAMILIES or f["family"] == "room":
            continue
        types = _family_types(f["family"])
        if types:
            out.append({"family": f["family"], "word": f["word"], "types": list(types)})
    return out


def _group_of_type(ftype: str) -> str:
    from wenart.furniture import catalog as C
    if ftype in VEGETATION_TYPES:
        return "vegetation"
    if ftype in OPENING_TYPES:
        return ftype
    return "decor" if ftype in C.DECOR_TYPES else "furniture"


def kind_of(ftype: str) -> str:
    """``furniture`` | ``decor`` (catalogue kinds) | ``vegetation`` | ``opening`` (the extras: no catalogue entry)."""
    group = _group_of_type(ftype)
    return group if group in ("furniture", "decor", "vegetation") else "opening"


# Words after which a name describes what the piece has or where it goes ("Sofa with cushions", "Lamp for bedside
# table"): the head noun is the last type word before the first of them ("Bedside table lamp": a lamp).
PREPOSITIONS = ("with", "for", "and", "in", "on", "w", "avec", "con", "mit", "ile", "icin", "und", "et", "y", "e")
# Families that name a tree in a vegetation folder (a potted plant elsewhere): "Olive tree" in "Trees" is a tree.
PLANT_FAMILIES = ("plant",)


def head_ordered(text: str) -> list[dict]:
    """``named(text)`` with the head family first: the last family named before the first ``PREPOSITIONS`` word
    (the whole name when it has none), the rest in name order."""
    from wenart.assets.audit import keywords as K
    found = named(text)
    if len(found) < 2:
        return found
    toks = K.tokens(text)
    cut = next((i for i, t in enumerate(toks) if t in PREPOSITIONS and i > 0), len(toks))
    head = named(" ".join(toks[:cut]))
    if not head:
        return found
    lead = head[-1]["family"]
    return [f for f in found if f["family"] == lead] + [f for f in found if f["family"] != lead]


def name_type(rel: str) -> dict:
    """The candidate types of one model from its names (module docstring): ``{"group", "group_folder",
    "candidates": [types], "families": [...], "where": "file" | "folder <name>" | "group folder <name>",
    "word", "title", "mapped"}``. Inside a vegetation, door or window folder the file name may name a type of that
    group, else a furniture or decor type (in a vegetation folder a plant word names a tree: ``PLANT_FAMILIES``),
    else the group's own type (the folder's evidence); elsewhere the file name, then the folders deepest first; the
    head family leads (``head_ordered``). ``mapped`` False: no name gives a type (the review list)."""
    p = PurePosixPath(str(rel))
    folders = list(p.parent.parts)
    if folders and folders[0] == ZIP_ROOT:
        folders = folders[1:]                            # the zip's top folder names no group (second pod, 23 Oct)
    stem = clean_title(p.stem)
    if generic_stem(p.stem) and folders:
        stem = clean_title(folders[-1])                  # the model's folder is its name
        folders = folders[:-1]
    group, gfolder = folder_group(folders)
    rec: dict = {"group": group, "group_folder": gfolder, "candidates": [], "families": [], "where": None,
                 "word": None, "title": stem, "mapped": False}

    def take(found: list[dict], where: str, allowed: Optional[tuple] = None, exclude: tuple = ()) -> bool:
        types: list[str] = []
        for f in found:
            for t in f["types"]:
                if (allowed is None or t in allowed) and t not in exclude and t not in types:
                    types.append(t)
        if not types:
            return False
        rec.update(candidates=types, families=[f["family"] for f in found], where=where,
                   word=", ".join(f["word"] for f in found), mapped=True)
        return True

    file_found = head_ordered(stem)
    special = group in ("vegetation", "door", "window")
    if special:
        own = VEGETATION_TYPES if group == "vegetation" else (group,)
        rest = [f for f in file_found if not (group == "vegetation" and f["family"] in PLANT_FAMILIES)]
        # the head noun decides: "Alfreton 4 Door Cabinet" in Doors is a cabinet, "Oak door" a door
        head_furniture = bool(rest) and rest[0] is file_found[0] and not set(rest[0]["types"]) & set(own)
        if head_furniture and take(rest, "file", None, tuple(own)):
            pass
        elif take(file_found, "file", own) or take(rest, "file", None):
            pass
        else:
            rec.update(candidates=[GROUP_DEFAULT[group]], families=[], where=f"group folder {gfolder}",
                       word=gfolder, mapped=True)
    else:
        # inside a furniture or decor folder a tree, door or window word names no site tree or opening (a "coat
        # tree", a "wardrobe with sliding doors"): only furniture and decor types count there
        exclude = VEGETATION_TYPES + OPENING_TYPES if group in ("furniture", "decor") else ()
        if not take(file_found, "file", None, exclude):
            for folder in reversed(folders):
                if folder == gfolder:
                    continue
                if take(head_ordered(folder), f"folder {folder}", None, exclude):
                    break
        if group is None and rec["mapped"] and set(rec["families"]) & set(PLANT_FAMILIES) \
                and "tree" not in rec["candidates"]:
            # outside a furniture or decor folder a plant word may name a garden tree ("Outdoor/Olive tree"): the
            # size decides (choose: a 6 m olive tree fits no potted plant; a 1.6 m one stays a potted plant)
            rec["candidates"] = rec["candidates"] + ["tree"]
    if rec["mapped"] and str(rec["where"] or "").startswith("folder "):
        # the file name names no type: the title carries the folder that does (a code-evidence title for the audit)
        rec["title"] = f"{stem} ({rec['where'][len('folder '):]})" if stem else rec["where"][len("folder "):]
    rec["group"] = _group_of_type(rec["candidates"][0]) if rec["candidates"] else group
    return rec


# --------------------------------------------------------------------------
# Unit, up axis and type from the box
# --------------------------------------------------------------------------

def _axis_error(v: float, lo: float, hi: float) -> float:
    if v <= 0:
        return math.inf
    if v < lo:
        return lo / v - 1.0
    if v > hi:
        return v / hi - 1.0
    return 0.0


def box_error(ftype: str, box) -> float:
    """How far a box (w, d, h) is outside the type's real ranges (``sizes.range_error`` in either orientation;
    ``EXTRA_RANGES`` for trees, doors and windows; a type without a range: its largest side against
    ``GENERIC_MAX_M``)."""
    from wenart.furniture import sizes as SZ
    vals = [float(v) for v in box]
    if SZ.real_range(ftype) is not None:
        return SZ.range_error(ftype, vals, oriented=False)
    r = EXTRA_RANGES.get(ftype)
    if r is None:
        return _axis_error(max(vals), *GENERIC_MAX_M)

    def foot(a, b):
        return max(_axis_error(a, *r["width"]), _axis_error(b, *r["depth"]))
    return max(min(foot(vals[0], vals[1]), foot(vals[1], vals[0])), _axis_error(vals[2], *r["height"]))


def choose(cands: list[str], extents) -> dict:
    """The type, unit and up axis of a model (module docstring). ``extents`` = the box (x, y, z) in the importer's
    Z-up frame before any fix. Returns ``{"type", "factor", "unit", "up_fix", "fits", "error", "units_known",
    "type_from", "box_m", "tried"}``: among the candidates, the first key wins of (fits within ``FIT_TOL``, else the
    error), no turn before a turn, metres before inches before the other units, the name's order. A box that fits no
    candidate keeps metres and no turn unless another unit cuts the error below ``APPLY_UNFIT_RATIO`` of it."""
    ex, ey, ez = (float(v) for v in extents)
    if not cands:
        raise WarehouseError("no candidate type")
    rows = []
    for ci, t in enumerate(cands):
        for up in (None, "z_up"):
            base = (ex, ey, ez) if up is None else (ex, ez, ey)     # z_up: the model's up was glTF +Z (importer -Y)
            for f, unit in UNIT_FACTORS:
                err = box_error(t, [v * f for v in base])
                rows.append({"type": t, "ci": ci, "up_fix": up, "factor": f, "unit": unit, "error": err,
                             "box_m": [round(v * f, 4) for v in base]})

    def key(r):
        fit = r["error"] <= FIT_TOL + 1e-9
        return (0.0 if fit else r["error"], 0 if r["up_fix"] is None else 1, UNIT_PENALTY[r["unit"]], r["ci"])
    best = min(rows, key=key)
    fits = best["error"] <= FIT_TOL + 1e-9
    if not fits:
        # no candidate fits: keep the file as drawn (metres, no turn) unless another unit is clearly better
        plain = min((r for r in rows if r["up_fix"] is None and r["factor"] == 1.0),
                    key=lambda r: (r["error"], r["ci"]))
        unit_rows = [r for r in rows if r["up_fix"] is None and r["type"] == plain["type"]]
        better = min(unit_rows, key=lambda r: (r["error"], UNIT_PENALTY[r["unit"]]))
        best = better if (math.isfinite(better["error"]) and better["error"] < plain["error"] * APPLY_UNFIT_RATIO) \
            else plain
    # every unit and up axis tried for the chosen type (the review list shows them for a box that fits nothing)
    tried = [{k: (round(v, 4) if isinstance(v, float) and math.isfinite(v) else v) for k, v in r.items() if k != "ci"}
             for r in rows if r["type"] == best["type"]]
    return {"type": best["type"], "factor": best["factor"], "unit": best["unit"], "up_fix": best["up_fix"],
            "fits": fits, "error": round(best["error"], 4) if math.isfinite(best["error"]) else None,
            "units_known": fits, "type_from": "name" if len(cands) == 1 else "name+size", "box_m": best["box_m"],
            "tried": tried[:40]}


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

def material_rule(name: str, ftype: str) -> tuple[str, float, float]:
    """``(rule, roughness, metallic)`` of a material: the first ``MATERIAL_RULES`` word in its folded name, else the
    type's roughness (``TYPE_ROUGHNESS``) with metallic 0."""
    from wenart.assets.audit import keywords as K
    toks, folded = K.tokens(name or ""), K.fold(name or "")
    for rule, words, rough, metal in MATERIAL_RULES:
        for w in words:
            if K._matches(toks, folded, w):
                return rule, rough, metal
    return f"type:{ftype}" if ftype in TYPE_ROUGHNESS else "default", TYPE_ROUGHNESS.get(ftype, DEFAULT_ROUGHNESS), 0.0


def fix_materials(doc: dict, ftype: str) -> dict:
    """Every material double-sided, roughness and metallic set where no metallic-roughness texture drives them
    (``material_rule``), an alpha below 1 blended, a default material for primitives without one. Returns the record
    ``{"materials": [...], "double_sided": n, "default_added": n_primitives, "blend": n}``."""
    mats = doc.setdefault("materials", [])
    rec: dict = {"materials": [], "double_sided": 0, "default_added": 0, "blend": 0}
    for i, m in enumerate(mats):
        if not isinstance(m, dict):
            continue
        if not m.get("doubleSided"):
            m["doubleSided"] = True
            rec["double_sided"] += 1
        name = str(m.get("name") or f"material_{i}")
        exts = m.get("extensions") if isinstance(m.get("extensions"), dict) else {}
        pbr = m.setdefault("pbrMetallicRoughness", {})
        row = {"index": i, "name": name, "was": {"metallic": pbr.get("metallicFactor", "default 1.0"),
                                                  "roughness": pbr.get("roughnessFactor", "default 1.0")}}
        if "KHR_materials_pbrSpecularGlossiness" in exts:
            row.update(rule="spec_gloss (kept: the importer converts it)")
        elif isinstance(pbr.get("metallicRoughnessTexture"), dict):
            row.update(rule="texture (kept: a metallic-roughness map drives it)")
        else:
            rule, rough, metal = material_rule(name, ftype)
            pbr["roughnessFactor"] = rough
            pbr["metallicFactor"] = metal
            row.update(rule=rule, roughness=rough, metallic=metal)
        colour = pbr.get("baseColorFactor")
        if isinstance(colour, list) and len(colour) == 4 and float(colour[3]) < 1.0 and not m.get("alphaMode"):
            m["alphaMode"] = "BLEND"
            rec["blend"] += 1
        rec["materials"].append(row)
    missing = [(mi, pi) for mi, mesh in enumerate(doc.get("meshes") or [])
               for pi, prim in enumerate(mesh.get("primitives") or []) if "material" not in prim]
    if missing:
        rough = TYPE_ROUGHNESS.get(ftype, DEFAULT_ROUGHNESS)
        mats.append({"name": DEFAULT_MATERIAL, "doubleSided": True,
                     "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0], "metallicFactor": 0.0,
                                              "roughnessFactor": rough}})
        idx = len(mats) - 1
        for mi, pi in missing:
            doc["meshes"][mi]["primitives"][pi]["material"] = idx
        rec["default_added"] = len(missing)
        rec["materials"].append({"index": idx, "name": DEFAULT_MATERIAL, "rule": f"added for {len(missing)} "
                                 "primitive(s) without a material", "roughness": rough, "metallic": 0.0})
    return rec


# --------------------------------------------------------------------------
# GLB rewrite
# --------------------------------------------------------------------------

def read_glb(path) -> tuple[dict, Optional[bytes]]:
    """``(json, BIN chunk bytes or None)`` of a GLB 2.0 file."""
    data = Path(path).read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise WarehouseError(f"{Path(path).name}: not a GLB file")
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC or version != 2:
        raise WarehouseError(f"{Path(path).name}: GLB version {version}, expected 2")
    off, doc, binary = 12, None, None
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8:off + 8 + clen]
        if ctype == CHUNK_JSON and doc is None:
            doc = json.loads(chunk.decode("utf-8"))
        elif ctype == CHUNK_BIN and binary is None:
            binary = bytes(chunk)
        off += 8 + clen + (-clen % 4)
    if doc is None:
        raise WarehouseError(f"{Path(path).name}: GLB without a JSON chunk")
    return doc, binary


def write_glb(path, doc: dict, binary: Optional[bytes]) -> Path:
    """A GLB 2.0 file of ``doc`` and the binary chunk (both padded to 4 bytes: JSON with spaces, BIN with zeros)."""
    js = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    body = struct.pack("<II", len(js), CHUNK_JSON) + js
    if binary is not None:
        b = binary + b"\x00" * (-len(binary) % 4)
        body += struct.pack("<II", len(b), CHUNK_BIN) + b
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    part.write_bytes(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + body)
    part.replace(path)
    return path


def external_files(doc: dict) -> list[str]:
    """The external URIs a GLB names (buffers and images that are no data URI): such a file is not self-contained."""
    out = []
    for key in ("buffers", "images"):
        for item in doc.get(key) or []:
            uri = item.get("uri") if isinstance(item, dict) else None
            if uri and not str(uri).startswith("data:"):
                out.append(str(uri))
    return out


Q_Z_UP = [-math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5)]     # -90 degrees about glTF X: glTF +Z -> +Y


def root_transform(verts_zup, factor: float, up_fix: Optional[str]) -> dict:
    """The new root node's TRS (glTF frame) for vertices in the importer's Z-up frame: the scale, the up turn and the
    translation that puts the bounding-box centre at x = z = 0 and the bottom at y = 0 (glTF Y up)."""
    import numpy as np
    v = np.asarray(verts_zup, dtype=np.float64)
    g = np.stack([v[:, 0], v[:, 2], -v[:, 1]], axis=1)          # importer Z-up -> glTF Y-up
    if up_fix == "z_up":
        g = np.stack([g[:, 0], g[:, 2], -g[:, 1]], axis=1)       # the turn Q_Z_UP applied: (x, y, z) -> (x, z, -y)
    g = g * float(factor)
    mn, mx = g.min(axis=0), g.max(axis=0)
    t = [-(mn[0] + mx[0]) / 2.0, -mn[1], -(mn[2] + mx[2]) / 2.0]
    node: dict = {"name": FIX_ROOT_NAME}
    if any(abs(x) > 1e-9 for x in t):
        node["translation"] = [round(float(x), 6) + 0.0 for x in t]
    if up_fix == "z_up":
        node["rotation"] = list(Q_Z_UP)
    if abs(factor - 1.0) > 1e-12:
        node["scale"] = [float(factor)] * 3
    return node


def wrap_scenes(doc: dict, node: dict) -> int:
    """Put every scene's root nodes under ``node`` (one copy per scene; scenes that share nodes: the default scene
    only). Returns the number of scenes wrapped."""
    nodes = doc.setdefault("nodes", [])
    scenes = doc.get("scenes") or []
    if not scenes:
        children = {c for n in nodes for c in n.get("children", [])}
        roots = [i for i in range(len(nodes)) if i not in children]
        doc["scenes"] = [{"nodes": roots}]
        doc["scene"] = 0
        scenes = doc["scenes"]
    sets = [set(s.get("nodes") or []) for s in scenes]
    disjoint = sum(len(s) for s in sets) == len(set().union(*sets)) if sets else True
    targets = range(len(scenes)) if disjoint else [int(doc.get("scene", 0) or 0)]
    n = 0
    for si in targets:
        scene = scenes[si]
        nodes.append(dict(node, children=list(scene.get("nodes") or [])))
        scene["nodes"] = [len(nodes) - 1]
        n += 1
    return n


def fixup(src, dest, ftype: str, factor: float, up_fix: Optional[str]) -> dict:
    """The fixed GLB of one model (module docstring) at ``dest``; returns ``{"root", "materials", "scenes"}``."""
    from wenart.assets.audit import glbmesh as GM
    doc, binary = read_glb(src)
    ext = external_files(doc)
    if ext:
        raise WarehouseError(f"names external file(s) {ext[:3]}: not a self-contained GLB")
    gdoc, buffers = GM.read(src)
    verts, _tris = GM.mesh_arrays(gdoc, buffers)
    node = root_transform(verts, factor, up_fix)
    mats = fix_materials(doc, ftype)
    scenes = wrap_scenes(doc, node)
    doc.setdefault("asset", {}).setdefault("version", "2.0")
    doc["asset"]["extras"] = dict(doc["asset"].get("extras") or {}, wenart_fix=FIX_VERSION)
    write_glb(dest, doc, binary)
    return {"root": node, "materials": mats, "scenes": scenes}


# --------------------------------------------------------------------------
# One model end to end
# --------------------------------------------------------------------------

def sha256_file(path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def model_rel(uid: str) -> str:
    return f"models/{SOURCE}/{uid}.glb"


def process(job: dict) -> dict:
    """One model (``job``: ``{"id", "rel", "raw", "assets", "cache"}``): its names typed, measured, its type, unit
    and up axis chosen, the fixed GLB written to ``<assets>/models/3dwh/<uid>.glb``. Returns the ingest record
    ``{"id", "rel", "title", "ok", "group", "type", "kind", "mapped", ...}``; ``ok`` False with ``dropped`` (data:
    unmapped, not a GLB, empty, external files) or ``error`` (an unexpected failure). Reused when the cache record
    has the same source sha256 and ``FIX_VERSION`` and the fixed file is there."""
    from wenart.assets.audit import glbmesh as GM
    rel, uid = job["rel"], job["id"]
    src = Path(job["raw"]) / job.get("file", rel)
    assets = Path(job["assets"])
    dest = assets / model_rel(uid)
    cache = Path(job["cache"]) / f"{uid}.json"
    rec: dict = {"id": uid, "rel": rel, "ok": False, "fix_version": FIX_VERSION}
    try:
        size = src.stat().st_size
        rec["bytes"] = size
        names = name_type(rel)
        rec.update(title=names["title"], group=names["group"], mapped=names["mapped"], names=names)
        if not names["mapped"]:
            rec["dropped"] = "unmapped: no folder or file name gives a type (review list)"
            return rec
        if size < MIN_FILE_BYTES or size > MAX_FILE_BYTES:
            rec["dropped"] = f"file size {size} bytes outside {MIN_FILE_BYTES}-{MAX_FILE_BYTES}"
            return rec
        src_sha = sha256_file(src)
        rec["src_sha256"] = src_sha
        if cache.is_file() and dest.is_file():
            old = json.loads(cache.read_text(encoding="utf-8"))
            if old.get("src_sha256") == src_sha and old.get("fix_version") == FIX_VERSION and old.get("ok") \
                    and old.get("names") == names:
                return dict(old, kept=True)
        doc0, _bin = read_glb(src)
        rec["generator"] = str((doc0.get("asset") or {}).get("generator") or "")
        rec["copyright"] = str((doc0.get("asset") or {}).get("copyright") or "")
        if external_files(doc0):
            rec["dropped"] = f"names external file(s) {external_files(doc0)[:3]}: not a self-contained GLB"
            return rec
        m0 = GM.measure(src)
        pick = choose(names["candidates"], m0["bbox_model_m"])
        choice = {k: v for k, v in pick.items() if k != "tried" or not pick["fits"]}   # the tries of a misfit only
        rec.update(choice=choice, type=pick["type"], group=_group_of_type(pick["type"]), kind=kind_of(pick["type"]),
                   raw_box_m=m0["bbox_model_m"])
        fix = fixup(src, dest, pick["type"], pick["factor"], pick["up_fix"])
        m1 = GM.measure(dest)
        rec.update(ok=True, glb=model_rel(uid), sha256=sha256_file(dest), fix=fix, box_m=m1["bbox_model_m"],
                   bbox_min_m=m1["bbox_min_m"], bbox_max_m=m1["bbox_max_m"], triangles=m1["triangles"],
                   vertices=m1["vertices"])
        if rec["group"] == "vegetation":
            rec["crown_m"] = round(max(m1["bbox_model_m"][0], m1["bbox_model_m"][1]), 3)
            rec["height_m"] = m1["bbox_model_m"][2]
    except (GM.MeshError, WarehouseError) as exc:
        rec["dropped"] = f"{type(exc).__name__}: {exc}"
    except json.JSONDecodeError as exc:                   # a GLB whose JSON chunk is no JSON (first pod: 6 models)
        rec["dropped"] = f"the GLB's JSON chunk does not parse: {exc}"
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    if rec.get("ok"):
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return rec


# --------------------------------------------------------------------------
# Catalogue fields
# --------------------------------------------------------------------------

def entry_fields() -> dict:
    """The licence fields of every 3D Warehouse catalogue entry (the user's decision of 23 Oct 2026)."""
    return {"licence": LICENCE, "licence_flag": LICENCE_FLAG, "licence_declared_by": LICENCE_DECLARED_BY,
            "licence_url": LICENCE_URL, "commercial_safe": False}


def author_of(rec: dict) -> str:
    text = " ".join(str(rec.get("copyright") or "").split())
    return text or "unknown 3D Warehouse uploader (the GLB names no author)"


def source_url(rel: str) -> str:
    return f"{DRIVE_PAGE.format(id=DRIVE_FILE_ID)} (zip member {rel})"


def attribution(title: str, rel: str, author: str) -> str:
    return (f"\"{title or PurePosixPath(rel).stem}\" by {author}, 3D Warehouse (SketchUp), from the user's zip "
            f"\"{ZIP_NAME}\" ({rel}); licence not reviewed ({USER_DECISION}); changes: units, up axis, origin, "
            "double-sided faces and roughness fixed, scaled to the drawn footprint, re-oriented, rendered; PoC use in "
            "relaxed licence mode only")


DATASET = {"name": DATASET_NAME, "owner": "the 3D Warehouse uploaders (SketchUp 3D Warehouse)",
           "page": LICENCE_URL, "file": f"{ZIP_NAME} (Google Drive {DRIVE_FILE_ID}, {ZIP_BYTES} bytes)",
           "licence": LICENCE, "licence_flag": LICENCE_FLAG, "licence_url": LICENCE_URL,
           "note": f"{USER_DECISION}; every render that shows a 3D Warehouse model is commercial-safe: no"}


def notice() -> str:
    """The ATTRIBUTION.md dataset notice of the 3D Warehouse models."""
    return (f"3D Warehouse models (SketchUp, {LICENCE_URL}) from the user's zip \"{ZIP_NAME}\": the licences of the "
            f"models were not reviewed ({USER_DECISION}); they are PoC-only assets and never part of a commercial "
            "deliverable.")
