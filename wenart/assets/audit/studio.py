"""The ranking studio (31 Oct 2026, lesson UL217; user: "Is it possible to do furniture ranking system? we render the
furnitures and I ranked them from 10 to 0 based purely on the look? ... pod renders for example 10 beds or 20 and give
alphabetic order I gave that order a rank from 0 to 10?", then "page with score buttons, start with beds sofas
armchairs").

What:

- ``rank_entries(types)``: the models the fit may use of each type (``catalog.usable`` in the licence mode, the fit's
  bed rule ``fit.bed_usable``, a model file), in a fixed order (type, then id);
- ``studio_piece(entry)``: the piece the scene builder builds for a model: its catalogue size at scale 1, the fit's
  own asset record (``fit.model_asset``), so a bed frame gets its bedding and a sofa its fabric dressing exactly as
  in a house render;
- ``plan(...)``: one Blender job per model whose image is not current (``job_sha``), the sheets of ``PER_SHEET``
  models with the letters ``A``-``T``, the index (``ranking_index.json``: type -> sheets -> letter -> id, title,
  source);
- ``fit_distance(...)``, ``camera(...)``: the front 3/4 view that frames the built model's box (the same camera for
  every model: azimuth, elevation, lens; only the distance follows the size);
- ``compose_sheets(...)``: the lettered sheets (``sheets/<type>-NN.jpg``) and one tile per model
  (``tiles/<type>/<id>.jpg``) for the scoring page;
- ``--batch remaining`` (31 Oct 2026, user: "include all remaining library models for ranking after the real04 run"):
  ``remaining_entries`` = every library model the pipeline may use that no committed sheet shows (the decor models,
  the extras the fit takes first, the small items' models, any furniture type outside ``ALL_TYPES``), each built by
  the scene builder as a decor item with the fit's own asset at its own size on the stage of its kind
  (``decor_stage``: a plinth, the floor, a backdrop wall, a ceiling panel); its own index
  (``ranking_index_remaining.json``) and sheets named by type, the committed ids, sheets and letters untouched.

Why: the user ranks the models on their look alone: one studio, one light, one camera angle, a neutral floor and
backdrop; the score goes to ``results/library/user_ranks.json`` and the fit prefers the higher rank
(``wenart.furniture.user_ranks``).

How: pure Python but the drawing (PIL); the Blender side is ``blender_studio.py`` run by ``render.run_render``
(``script=STUDIO_SCRIPT``: workers, resume, a model that kills Blender recorded as failed). CLI:
``python -m wenart.assets.audit.studio plan|render|sheets``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import string
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import HERE

STUDIO_SCRIPT = HERE / "blender_studio.py"
STUDIO_VERSION = "ul217.1"
RANK_TYPES = ("bed_double", "sofa", "armchair")      # the user's first three types
# 31 Oct 2026 (user: "Give some other items for me to rank"): every other furniture type, by room (living, dining,
# bedroom, work, hall, plants, bathroom, kitchen), the first three last (already ranked)
ALL_TYPES = ("sofa_corner", "table_coffee", "side_table", "tv_unit", "floor_lamp", "ottoman", "bookshelf",
             "console_table", "sideboard", "display_cabinet", "chaise", "table_dining", "chair", "bar_stool", "bench",
             "nightstand", "wardrobe", "dresser", "bed_single", "bunk_bed", "crib", "desk", "office_chair",
             "shoe_cabinet", "tall_cabinet", "potted_plant", "washbasin", "toilet", "bathtub", "shower",
             "washing_machine", "stove", "sink_kitchen", "fridge") + RANK_TYPES
PER_SHEET = 20
LETTERS = string.ascii_uppercase[:PER_SHEET]          # A .. T
SETTINGS = {"resolution": 640, "samples": 96, "lens_mm": 50.0, "sensor_mm": 36.0, "azimuth_deg": 35.0,
            "elevation_deg": 16.0, "margin": 1.12, "floor_rgb": [0.72, 0.70, 0.67], "world": 0.5,
            "tile_px": 480, "sheet_tile_px": 384, "jpeg_quality": 86, "device": "auto"}
STYLE = {"source_text": "ranking studio: neutral", "family": "", "floor": {"material": "wood_oak_light"},
         "walls": {"material": "plaster_white"}, "ceiling": {"material": "plaster_white"},
         "lighting": {"mood": "studio"}}


# --------------------------------------------------------------------------
# The models and their pieces (pure)
# --------------------------------------------------------------------------

def catalogue_entries(library: Optional[dict] = None, polyhaven: Optional[dict] = None) -> list[dict]:
    """The furniture model entries of both catalogues (library ``entries``, then the Poly Haven models)."""
    from wenart.assets.audit import items as I
    library = library if library is not None else I.read_json(I.LIBRARY_PATH)
    polyhaven = polyhaven if polyhaven is not None else I.read_json(I.POLYHAVEN_PATH)
    out = []
    for doc in (library, polyhaven):
        for e in (doc or {}).get("entries") or []:
            if isinstance(e, dict) and e.get("id") and not e.get("parametric") and (e.get("glb") or e.get("gltf")):
                out.append(e)
    return out


def rank_entries(types=RANK_TYPES, mode: str = "relaxed", entries: Optional[list[dict]] = None) -> list[dict]:
    """The models of ``types`` the fit may use in licence ``mode``, ordered by the order of ``types``, then id."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F
    types = list(types)
    rows = [e for e in (entries if entries is not None else catalogue_entries())
            if e.get("type") in types and e.get("bbox_m") and C.usable(e, mode) and F.bed_usable(e)]
    return sorted(rows, key=lambda e: (types.index(e["type"]), str(e["id"])))


def studio_piece(entry: dict) -> dict:
    """The piece of a model in the studio: its catalogue box at scale 1, centred on the origin, front -Y, with the
    fit's asset record (``fit.model_asset``)."""
    from wenart.furniture import fit as F
    w, d, h = (float(v) for v in entry["bbox_m"])
    asset = F.model_asset(entry, entry["type"], w, d, [1.0, 1.0, 1.0])
    return {"id": "studio_piece", "type": entry["type"], "level_id": "L0", "room_id": "studio",
            "footprint": {"center": [0.0, 0.0], "size": [round(w, 4), round(d, 4)], "rotation_deg": 0.0},
            "height": round(h, 4), "front_deg": 270.0, "status": "verified", "source": "from_documents",
            "evidence": {"method": "inferred", "file": "ranking studio", "confidence": 1.0}, "asset": asset}


# --------------------------------------------------------------------------
# Our builds (31 Oct 2026, the user: "yes start with 1 and 2": score our procedural builds next to the library)
# --------------------------------------------------------------------------

PROC_TAG = "ours"
PROC_EXCLUDE = ("bed", "stair", "unknown")        # an alias, a piece of the building, no type
PROC_STYLE_DIR = Path(__file__).resolve().parents[3] / "results" / "baseline" / "latest" / "run"
RANKING_DIR = Path(__file__).resolve().parents[3] / "results" / "library" / "ranking"   # the committed sheets
# the code that shapes our builds and their materials: a change re-renders them (the "after" sheets)
PROC_CODE = ("wenart/blender/parametric.py", "wenart/blender/modules.py", "wenart/blender/materials.py",
             "wenart/blender/furniture.py", "wenart/blender/textiles.py", "wenart/style/vocabulary.py")
PROC_CODE_GLOBS = ("wenart/blender/*parts*.py",)


def proc_code_sha() -> str:
    root = Path(__file__).resolve().parents[3]
    files = sorted({*(root / f for f in PROC_CODE), *(q for g in PROC_CODE_GLOBS for q in root.glob(g))})
    h = hashlib.sha256()
    for f in files:
        if f.is_file():
            h.update(f.relative_to(root).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def procedural_styles(folder: Optional[Path] = None) -> list[tuple[str, dict]]:
    """``[(project, style)]`` of the latest runs (``results/baseline/latest/run/<p>/style.json``): our builds look as
    they do in each project; the neutral studio style when none is there."""
    folder = Path(folder) if folder is not None else PROC_STYLE_DIR
    out = []
    for f in sorted(folder.glob("*/style.json")):
        try:
            st = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out.append((f.parent.name, st[0] if isinstance(st, list) and st else st))
    return out or [("studio", STYLE)]


def procedural_types() -> list[str]:
    from wenart.blender import parametric as P
    order = list(ALL_TYPES)
    types = [t for t in P._BUILDERS if t not in PROC_EXCLUDE]
    return sorted(types, key=lambda t: (order.index(t) if t in order else len(order), t))


def procedural_entries(types: Optional[list[str]] = None, styles: Optional[list[tuple[str, dict]]] = None,
                       tag: str = PROC_TAG) -> list[dict]:
    """One entry per builder and project style: ``{"id": "<tag>:<type>:<project>", "type", "group": tag,
    "procedural": True, "style_name", "style", "bbox_m": the type's typical product size, "method": module when a
    module builder plans the piece, else parametric, "title", "code_sha"}``."""
    from wenart.blender import modules as MOD
    from wenart.furniture import sizes as SZ
    styles = styles if styles is not None else procedural_styles()
    code = proc_code_sha()
    out = []
    for t in types or procedural_types():
        rng = SZ.real_range(t) or {}
        box = [float(v) for v in (rng.get("product") or (1.0, 0.6, 0.8))]
        for name, style in styles:
            e = {"id": f"{tag}:{t}:{name}", "type": t, "group": tag, "procedural": True, "style_name": name,
                 "style": style, "bbox_m": box, "source": "procedural", "code_sha": code}
            piece = _proc_piece_base(e)
            e["method"] = "module" if MOD.module_plan(piece, style) is not None else "parametric"
            out.append(dict(e, title=f"our {t.replace('_', ' ')} ({e['method']}, {name} style)"))
    return out


def _proc_piece_base(e: dict) -> dict:
    w, d, h = (float(v) for v in e["bbox_m"])
    return {"id": "studio_piece", "type": e["type"], "level_id": "L0", "room_id": "studio",
            "footprint": {"center": [0.0, 0.0], "size": [round(w, 4), round(d, 4)], "rotation_deg": 0.0},
            "height": round(h, 4), "front_deg": 270.0, "status": "verified", "source": "from_documents",
            "evidence": {"method": "inferred", "file": "ranking studio", "confidence": 1.0}}


def procedural_piece(e: dict) -> dict:
    """The piece of one of our builds: the fit's module record (the build plans its modules) or its parametric
    record (``fit.parametric_fit``)."""
    from wenart.furniture import fit as F
    piece = _proc_piece_base(e)
    if e.get("method") == "module":
        asset = {"library": "module", "asset_id": f"module:{e['type']}", "licence": "n/a", "license": "n/a",
                 "method": "module", "fit_scale": [1.0, 1.0, 1.0], "bbox_m": list(e["bbox_m"]),
                 "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0]}
    else:
        asset = F.parametric_fit(piece, "ranking studio: our own build")
    return dict(piece, asset=asset)


# --------------------------------------------------------------------------
# The remaining library models (31 Oct 2026, user: "include all remaining library models for ranking after the real04
# run"): the decor models, the extras the fit takes first, the small items' models and any furniture type not on the
# sheets yet, each on a stage of its kind
# --------------------------------------------------------------------------

REMAINING = "remaining"            # the batch: ranking_index_remaining.json, studio_results_remaining.json
DECOR_STUDIO_VERSION = "ul217.decor1"
STUDIO_ITEM_ID = "studio_item"
SMALL_PREFIX = "small_"            # a small item's kind as a sheet type (small_potted_plant: never a furniture name)
SMALL_BUILD_TYPE = "vase"          # ... built as a tabletop decor item within its own box
# the page's groups of tabs, in this order (a type in none: Furniture; a procedural group: Our builds)
TAB_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Textiles", ("cushion", "throw", "rug", "curtain", "blind")),
    ("Lights", ("table_lamp", "pendant_light", "ceiling_light")),
    ("Wall decor", ("wall_art", "mirror", "clock")),
    ("Plants", ("plant", "plant_large", "plant_small")),
    ("Tabletop", ("vase", "bowl", "books", "candle", "basket", "tray", "sculpture")),
    ("Electronics", ("tv", "monitor", "laptop", "microwave")),
)
GROUP_OURS, GROUP_FURNITURE, GROUP_SMALL = "Our builds", "Furniture", "Small items"
# --types names a type or one of these (the pod job's RANK_TYPES with RANK_BATCH=remaining)
TYPE_ALIASES: dict[str, tuple[str, ...]] = {
    "decor": tuple(t for name, ts in TAB_GROUPS if name != "Electronics" for t in ts),
    "textiles": TAB_GROUPS[0][1], "lights": TAB_GROUPS[1][1], "wall": TAB_GROUPS[2][1], "plants": TAB_GROUPS[3][1],
    "tabletop": TAB_GROUPS[4][1], "electronics": TAB_GROUPS[5][1], "extras": TAB_GROUPS[5][1]}
# the stage of each kind (heights in metres over the studio floor)
STAGE = {"plinth_h_m": 0.45, "plinth_margin": 1.25, "plinth_min_m": 0.30, "wall_eye_m": 1.50, "wall_full_m": 1.40,
         "full_bottom_m": 0.02, "textile_top_m": 2.30, "textile_bottom_min_m": 0.01, "light_bottom_m": 1.20,
         "cord_m": 0.35, "backdrop_gap_m": 0.03, "backdrop_depth_m": 0.05, "ceiling_min_m": 3.0, "headroom_m": 0.6,
         "rug_lift_m": 0.001, "panel_min_m": 0.6, "panel_margin": 1.4, "panel_t_m": 0.02}
# the camera of each stage (azimuth / elevation over the furniture studio's; the distance still follows the box)
STAGE_CAMERAS: dict[str, dict] = {"plinth": {}, "floor": {}, "rug": {"elevation_deg": 55.0},
                                  "wall": {"azimuth_deg": 18.0, "elevation_deg": 4.0},
                                  "window": {"azimuth_deg": 25.0, "elevation_deg": 6.0},
                                  "pendant": {"azimuth_deg": 30.0, "elevation_deg": -4.0},
                                  "flush": {"azimuth_deg": 30.0, "elevation_deg": -10.0}}
PROP_RGB = {"plinth": [0.62, 0.60, 0.57], "backdrop": [0.80, 0.78, 0.75], "panel": [0.86, 0.85, 0.83]}


def tab_group(rank_type: str, procedural: bool = False) -> str:
    """The page's group of a sheet type: ``Our builds`` (our procedural builds), a decor or extras group
    (``TAB_GROUPS``), ``Small items`` (``small_<kind>``), else ``Furniture``."""
    if procedural:
        return GROUP_OURS
    if str(rank_type).startswith(SMALL_PREFIX):
        return GROUP_SMALL
    for name, types in TAB_GROUPS:
        if rank_type in types:
            return name
    return GROUP_FURNITURE


def committed_ids(folder: Optional[Path] = None, skip: tuple = (REMAINING,)) -> set:
    """The model ids on the committed sheets (``ranking_index.json`` and every ``ranking_index_<tag>.json`` but the
    ``skip`` batches): a model there is never put on a new sheet (its id, sheet and letter stay)."""
    folder = Path(folder) if folder is not None else RANKING_DIR
    ids: set = set()
    for f in sorted(folder.glob("ranking_index*.json")):
        tag = f.stem[len("ranking_index_"):] if f.stem.startswith("ranking_index_") else ""
        if tag in skip:
            continue
        try:
            ids.update((json.loads(f.read_text(encoding="utf-8")).get("models") or {}).keys())
        except ValueError:
            continue
    return ids


def committed_sheets(folder: Optional[Path] = None, skip: tuple = (REMAINING,)) -> set:
    """The sheet names of the committed indexes (but the ``skip`` batches): a new sheet never takes one."""
    folder = Path(folder) if folder is not None else RANKING_DIR
    names: set = set()
    for f in sorted(folder.glob("ranking_index*.json")):
        tag = f.stem[len("ranking_index_"):] if f.stem.startswith("ranking_index_") else ""
        if tag in skip:
            continue
        try:
            names.update(s.get("sheet") for s in json.loads(f.read_text(encoding="utf-8")).get("sheets") or [])
        except ValueError:
            continue
    return {n for n in names if n}


def _studio_entry(entry: dict, rank_type: str, studio: str, build_type: str) -> dict:
    """A catalogue entry as a studio row: ``type`` = the sheet type (the decor type, the extras type, ``small_<kind>``),
    ``catalog_type`` its catalogue type, ``studio`` (decor | extra | small) and ``build_type`` (the decor type the
    scene builder builds it as)."""
    return dict(entry, type=rank_type, catalog_type=entry.get("type"), studio=studio, build_type=build_type)


def remaining_types() -> list[str]:
    """Every sheet type of the remaining batch in page order (the decor and extras groups; small items and furniture
    types follow as found)."""
    return [t for _name, ts in TAB_GROUPS for t in ts]


def remaining_entries(mode: str = "relaxed", catalog=None, done: Optional[set] = None,
                      types: Optional[list[str]] = None) -> list[dict]:
    """The library models the pipeline may use that no committed sheet shows (``committed_ids``), as studio rows:

    - the decor models of every decor type the fit takes a library model for (``fit.DECOR_LIBRARY_TYPES``), the
      curtains and blinds (``fit.TEXTILE_LIBRARY_FIRST``) and the throws: ``fit.decor_entries`` (usable in ``mode``;
      a model the user ranked 0-2 is out there already);
    - the extras the fit takes first (``fit.LIBRARY_FIRST``: laptops, monitors, microwaves, TVs; usable, with a GLB);
    - the small items' models (``small_items.candidates`` of every kind) that no decor type lists (``small_<kind>``);
    - the furniture models (``rank_entries``) of any type not in ``ALL_TYPES``.

    Each id once (the first type of the page order), in page order, then by id. ``types``: sheet types or the names of
    ``TYPE_ALIASES`` (None: all)."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F
    from wenart.furniture import small_items as SI
    catalog = catalog if catalog is not None else C.load()
    done = committed_ids() if done is None else set(done)
    want = None
    if types:
        want = {x for t in types for x in TYPE_ALIASES.get(t, (t,))}
    rows: list[dict] = []
    seen: set = set(done)

    def add(e: dict, rank_type: str, studio: str, build_type: str) -> None:
        if str(e["id"]) in seen or (want is not None and rank_type not in want):
            return
        seen.add(str(e["id"]))
        rows.append(_studio_entry(e, rank_type, studio, build_type))

    for t in remaining_types():
        if t in F.LIBRARY_FIRST:
            etype = F.LIBRARY_FIRST[t][0]
            pool = [e for e in getattr(catalog, "extras", None) or [] if e.get("type") == etype and e.get("id")
                    and e.get("glb") and e.get("bbox_m") and C.usable(e, mode)]
            for e in sorted(pool, key=lambda x: str(x["id"])):
                add(e, t, "extra", t)
        else:
            for e in F.decor_entries(catalog, t, mode):
                add(e, t, "decor", t)
    for kind in sorted(SI.ITEMS):
        for e in SI.candidates(kind, catalog, mode):
            add(e, SMALL_PREFIX + kind, "small", SMALL_BUILD_TYPE)
    known = set(ALL_TYPES) | set(PROC_EXCLUDE)
    models = [e for e in getattr(catalog, "entries", None) or [] if isinstance(e, dict) and e.get("id")
              and not e.get("parametric") and (e.get("glb") or e.get("gltf"))]
    others = sorted({str(e.get("type")) for e in models
                     if e.get("type") not in known and not str(e.get("type")).startswith("decor_")})
    for e in rank_entries(others, mode, [e for e in models if e.get("type") in others]) if others else []:
        if str(e["id"]) not in seen and (want is None or e["type"] in want):
            seen.add(str(e["id"]))
            rows.append(e)
    return rows


def _box(entry: dict) -> list[float]:
    return [float(v) for v in entry["bbox_m"][:3]]


def studio_asset(e: dict) -> dict:
    """The fit's own asset record of a decor or extras model at its own size: ``fit.decor_model_asset`` (a rug flat at
    its thickness cap and a wall piece hung at its width by ``fit._decor_fit``, every other piece ``within`` its own
    box; a wall piece narrower than the build's least width is scaled up to it, as a house's item would be), or
    ``fit.library_first_asset`` at the fit's scale for an extras model."""
    from wenart.blender import furniture as BF
    from wenart.furniture import fit as F
    dtype = e["build_type"]
    if e.get("studio") == "extra":
        return F.library_first_asset(e, dtype, F.library_first_scale(e, dtype))
    w, d, h = _box(e)
    f = None
    if dtype == "rug":
        f = F._decor_fit(e, {"size": [w, d]}, dtype)
    elif dtype in F.WALL_DECOR_TYPES:
        width = max(w, BF.WALL_ART_MIN_WIDTH_M + 0.001)        # the build refuses a narrower wall piece
        f = F._decor_fit(e, {"size": [width, d]}, dtype)
    if f is None:
        f = F.own_size_fit(e)
    return F.decor_model_asset(e, dtype, f)


def stage_kind(e: dict, asset: Optional[dict] = None) -> str:
    """The stage of a studio row (pure): ``wall`` (wall art, mirror, clock), ``window`` (curtain, blind), ``pendant``
    or ``flush`` (the ceiling lights), ``rug``, ``floor`` (a floor-class piece tall enough to stand there:
    ``rest.floor_class_problem`` of its height and title is None), else ``plinth`` (tabletop pieces, small items,
    cushions, throws, baskets, the extras)."""
    from wenart.blender import rest as RS
    from wenart.furniture import fit as F
    dtype = e["build_type"]
    if dtype in F.WALL_DECOR_TYPES:
        return "wall"
    if dtype in F.TEXTILE_LIBRARY_FIRST:
        return "window"
    if dtype == "pendant_light":
        return "pendant"
    if dtype == "ceiling_light":
        return "flush"
    if dtype == "rug":
        return "rug"
    if dtype in RS.FLOOR_MIN_H_M:
        h = float((asset or {}).get("bbox_m", _box(e))[2])
        if RS.floor_class_problem(dtype, h, e.get("title") or e.get("name")) is None:
            return "floor"
    return "plinth"


def _prop(kind: str, lo: list, hi: list, shadow: bool = True) -> dict:
    return {"kind": kind, "min": [round(v, 4) for v in lo], "max": [round(v, 4) for v in hi], "shadow": shadow,
            "rgb": PROP_RGB[kind]}


def decor_stage(e: dict) -> dict:
    """The studio job of a decor or extras model (pure): ``{"kind", "item", "props", "ceiling_m", "camera"}``. The item
    is a decor item as the decor stage writes it (``id`` ``studio_item``, no host, the fit's asset at its own size,
    ``studio_asset``) that the scene builder builds as in a house (``furniture.create_furniture``: ``_create_decor``,
    ``_create_wall_art``):

    - ``plinth``: on a plain plinth (``STAGE["plinth_h_m"]`` high, a little wider than the piece): the item's
      ``center[2]`` is the plinth's top, so it stands there (never "on the floor": UL151);
    - ``floor``: on the studio floor; ``rug``: flat on the floor (lifted ``rug_lift_m``), seen from higher up;
    - ``wall``: on a plain backdrop wall (``wall_point`` on its face), its centre at eye height ``wall_eye_m`` (a
      mirror taller than ``wall_full_m``: just above the floor, a full-length mirror);
    - ``window``: hung in front of the backdrop wall at its real height, its top at ``textile_top_m`` (a longer one
      to the floor);
    - ``pendant`` / ``flush``: hung from a small ceiling panel at the level's ceiling (``ceiling_m``) with its bottom
      at ``light_bottom_m``: a pendant gets ``cord_m`` of cord and its canopy, a ceiling light sits flush.

    The camera keeps the furniture studio's lens and margin; its angle is the stage's (``STAGE_CAMERAS``)."""
    st = STAGE
    asset = studio_asset(e)
    w, d, h = (float(v) for v in asset["bbox_m"][:3])
    kind = stage_kind(e, asset)
    item = {"id": STUDIO_ITEM_ID, "type": e["build_type"], "level_id": "L0", "room_id": "studio",
            "status": "verified", "method": "rule", "rotation_deg": 0.0, "size": [round(w, 4), round(d, 4),
                                                                                round(h, 4)], "asset": asset}
    props: list[dict] = []
    top = h
    if kind == "plinth":
        side = max(st["plinth_min_m"], st["plinth_margin"] * max(w, d))
        ph = st["plinth_h_m"]
        item["center"] = [0.0, 0.0, ph]
        props.append(_prop("plinth", [-side / 2, -side / 2, 0.0], [side / 2, side / 2, ph]))
        top = ph + h
    elif kind == "floor":
        item["center"] = [0.0, 0.0]
    elif kind == "rug":
        item["center"] = [0.0, 0.0, st["rug_lift_m"]]
    elif kind in ("wall", "window"):
        if kind == "wall":                                   # a full-length mirror stands just above the floor
            full = e["build_type"] == "mirror" and h > st["wall_full_m"]
            bottom = st["full_bottom_m"] if full else max(st["full_bottom_m"], st["wall_eye_m"] - h / 2)
            item.update({"center": [0.0, 0.0], "wall_point": [0.0, 0.0], "bottom_m": round(bottom, 4), "gap_m": 0.0})
        else:
            bottom = max(st["textile_bottom_min_m"], st["textile_top_m"] - h)
            item["center"] = [0.0, round(-(d / 2.0 + st["backdrop_gap_m"]), 4), round(bottom, 4)]
        top = bottom + h
    else:                                                     # pendant, flush
        bottom = st["light_bottom_m"]
        item["center"] = [0.0, 0.0, bottom]
        top = bottom + h + (st["cord_m"] if kind == "pendant" else 0.0)
    ceiling = round(top if kind in ("pendant", "flush") else max(st["ceiling_min_m"], top + st["headroom_m"]), 4)
    if kind in ("wall", "window"):
        half = max(2.0, 1.5 * w)
        props.append(_prop("backdrop", [-half, 0.0, 0.0], [half, st["backdrop_depth_m"], ceiling]))
    if kind in ("pendant", "flush"):
        half = max(st["panel_min_m"], st["panel_margin"] * max(w, d)) / 2.0
        props.append(_prop("panel", [-half, -half, ceiling], [half, half, ceiling + st["panel_t_m"]], shadow=False))
    return {"kind": kind, "item": item, "props": props, "ceiling_m": ceiling, "camera": dict(STAGE_CAMERAS[kind])}


def is_decor_row(entry: dict) -> bool:
    return entry.get("studio") in ("decor", "extra", "small")


def check_sheet_names(sheets: list[dict], taken: set) -> None:
    """A new batch's sheet never takes a committed sheet's name (ids, sheets and letters of the committed batches stay
    as they are)."""
    clash = sorted({s["sheet"] for s in sheets} & set(taken))
    if clash:
        raise ValueError(f"the new sheets would take committed sheet names: {clash[:8]}")


def job_sha(entry: dict, settings: dict) -> str:
    keys = ("glb", "gltf", "sha256_glb", "bbox_m", "unit_scale", "origin_offset", "front_axis", "up_axis",
            "bed_frame", "deck_height_m", "has_mattress", "has_bedding", "has_cushions", "material_slots")
    body = {"v": STUDIO_VERSION, "entry": {k: entry.get(k) for k in keys}, "settings": settings}
    if entry.get("procedural"):                   # our build: its code and its style decide the picture
        body["procedural"] = {"code": entry.get("code_sha"), "style": entry.get("style_name"), "id": entry["id"]}
    if is_decor_row(entry):                       # a decor or extras model: its stage decides the picture
        body["decor"] = {"v": DECOR_STUDIO_VERSION, "type": entry["type"], "stage": decor_stage(entry)}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def image_path(work: Path, iid: str) -> Path:
    return Path(work) / "studio" / f"{iid}.png"


def sheet_plan(entries: list[dict], per_sheet: int = PER_SHEET) -> list[dict]:
    """``[{"sheet": "<type>-NN", "type", "number", "of", "letters": {letter: id}}]``: each type's models in order,
    ``per_sheet`` to a sheet, lettered from ``A``."""
    sheets: list[dict] = []
    by_type: dict[str, list[dict]] = {}
    for e in entries:
        by_type.setdefault(e.get("group") or e["type"], []).append(e)
    for ftype, rows in by_type.items():
        count = math.ceil(len(rows) / per_sheet)
        for n in range(count):
            chunk = rows[n * per_sheet:(n + 1) * per_sheet]
            sheets.append({"sheet": f"{ftype}-{n + 1:02d}", "type": ftype, "number": n + 1, "of": count,
                           "letters": {LETTERS[i]: e["id"] for i, e in enumerate(chunk)}})
    return sheets


def index_doc(entries: list[dict], sheets: list[dict]) -> dict:
    """``ranking_index.json``: the sheets and every model's letter, title, source and size."""
    from wenart.assets.audit.render import ascii_text
    by_id = {e["id"]: e for e in entries}
    models = {}
    for s in sheets:
        for letter, iid in s["letters"].items():
            e = by_id[iid]
            models[iid] = {"type": e["type"], "sheet": s["sheet"], "letter": letter, "source": e.get("source"),
                           "title": ascii_text(e.get("title") or e.get("name") or "", 90),
                           "size_m": [round(float(v), 2) for v in e["bbox_m"]]}
            if e.get("procedural"):
                models[iid].update({"group": e.get("group"), "procedural": True, "style": e.get("style_name"),
                                    "method": e.get("method")})
            if is_decor_row(e):                   # the remaining batch: its catalogue type and kind
                models[iid].update({"catalog_type": e.get("catalog_type"), "studio": e.get("studio")})
    return {"schema_version": 1, "kind": "ranking_index", "version": STUDIO_VERSION, "lesson": "UL217",
            "per_sheet": PER_SHEET, "types": list(dict.fromkeys(s["type"] for s in sheets)), "sheets": sheets,
            "models": models}


def plan(entries: list[dict], assets: Path, work: Path, settings: Optional[dict] = None,
         deadline: Optional[float] = None) -> dict:
    """The Blender jobs (``render.run_render``'s doc) for the models whose image is not current, the sheets and the
    models whose file is missing."""
    from wenart.assets.audit import render as R
    settings = dict(SETTINGS, **(settings or {}))
    jobs, skipped, missing = [], [], []
    for e in entries:
        rel = e.get("glb") or e.get("gltf")
        path = Path(assets) / rel if rel else None
        if e.get("procedural"):
            path = None
        elif path is None or not path.is_file():
            missing.append({"id": e["id"], "file": str(rel)})
            continue
        sha = job_sha(e, settings)
        rec = R.read_measure(work, e["id"])
        if rec and rec.get("job_sha") == sha and (
                (rec.get("ok") and image_path(work, e["id"]).is_file())
                or (not rec.get("ok") and int(rec.get("attempts", 1)) >= R.MAX_ATTEMPTS)):
            skipped.append(e["id"])
            continue
        attempt = int(rec.get("attempts", 1)) + 1 if rec and rec.get("job_sha") == sha and not rec.get("ok") else 1
        job = {"id": e["id"], "type": e["type"], "file": str(path) if path else None, "job_sha": sha,
               "attempt": attempt, "measure": str(R.measure_path(work, e["id"])),
               "image": str(image_path(work, e["id"]))}
        if e.get("procedural"):
            job.update({"procedural": True, "piece": procedural_piece(e), "style": e["style"]})
        elif is_decor_row(e):                     # a decor or extras model on its stage (decor_stage)
            job["stage"] = decor_stage(e)
        else:
            job["piece"] = studio_piece(e)
        jobs.append(job)
    return {"version": STUDIO_VERSION, "settings": settings, "style": STYLE, "deadline": deadline,
            "work": str(work), "assets": str(assets), "jobs": jobs, "skipped": skipped, "missing": missing}


# --------------------------------------------------------------------------
# The camera (pure)
# --------------------------------------------------------------------------

def view_basis(azimuth_deg: float, elevation_deg: float) -> tuple[list[float], list[float], list[float]]:
    """``(forward, right, up)`` unit vectors of a camera looking at the model from the front (-Y) turned
    ``azimuth_deg`` toward the model's left (-X) and ``elevation_deg`` down."""
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    to_cam = [-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)]
    forward = [-v for v in to_cam]
    right = [forward[1], -forward[0], 0.0]                     # forward x Z, horizontal
    n = math.hypot(right[0], right[1]) or 1.0
    right = [right[0] / n, right[1] / n, 0.0]
    up = [right[1] * forward[2] - right[2] * forward[1], right[2] * forward[0] - right[0] * forward[2],
          right[0] * forward[1] - right[1] * forward[0]]
    return forward, right, up


def fit_distance(corners: list, target: list, basis, lens_mm: float, sensor_mm: float, margin: float) -> float:
    """The distance from ``target`` along the view at which every corner lies inside the square frame with
    ``margin`` (pinhole camera, square sensor of ``sensor_mm``)."""
    forward, right, up = basis
    tan_half = (sensor_mm / 2.0) / lens_mm
    need = 0.0
    for c in corners:
        rel = [float(c[i]) - float(target[i]) for i in range(3)]
        x = sum(rel[i] * right[i] for i in range(3))
        y = sum(rel[i] * up[i] for i in range(3))
        z = sum(rel[i] * forward[i] for i in range(3))   # toward the far side: further from the camera
        need = max(need, z + abs(x) * margin / tan_half, z + abs(y) * margin / tan_half)
    return need


def camera(box_min: list, box_max: list, settings: Optional[dict] = None) -> dict:
    """``{"location", "target", "lens_mm"}`` of the front 3/4 view that frames the box."""
    s = dict(SETTINGS, **(settings or {}))
    target = [(float(a) + float(b)) / 2.0 for a, b in zip(box_min, box_max)]
    corners = [[x, y, z] for x in (box_min[0], box_max[0]) for y in (box_min[1], box_max[1])
               for z in (box_min[2], box_max[2])]
    basis = view_basis(float(s["azimuth_deg"]), float(s["elevation_deg"]))
    dist = fit_distance(corners, target, basis, float(s["lens_mm"]), float(s["sensor_mm"]), float(s["margin"]))
    loc = [target[i] - basis[0][i] * dist for i in range(3)]
    return {"location": [round(v, 4) for v in loc], "target": [round(v, 4) for v in target],
            "lens_mm": float(s["lens_mm"]), "distance": round(dist, 4)}


# --------------------------------------------------------------------------
# Sheets and tiles (PIL)
# --------------------------------------------------------------------------

def _font(size: int):
    from PIL import ImageFont
    for name in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _tile(path: Optional[Path], px: int):
    from PIL import Image
    if path is None or not Path(path).is_file():
        img = Image.new("RGB", (px, px), (205, 205, 205))
        from PIL import ImageDraw
        ImageDraw.Draw(img).text((px // 2 - 60, px // 2 - 10), "not rendered", fill=(90, 90, 90), font=_font(20))
        return img
    return Image.open(path).convert("RGB").resize((px, px), Image.LANCZOS)


def compose_sheets(index: dict, work: Path, out: Path, settings: Optional[dict] = None,
                   log: Callable = print) -> dict:
    """``sheets/<sheet>.jpg`` (5 x 4 tiles, the letter in each corner, the sheet name on top) and
    ``tiles/<type>/<id>.jpg``; returns ``{"sheets": n, "tiles": n, "missing": [ids]}``."""
    from PIL import Image, ImageDraw
    s = dict(SETTINGS, **(settings or {}))
    out = Path(out)
    px, tpx, q = int(s["sheet_tile_px"]), int(s["tile_px"]), int(s["jpeg_quality"])
    cols, rows, head = 5, 4, 56
    missing: list[str] = []
    tiles = 0
    for sheet in index["sheets"]:
        img = Image.new("RGB", (cols * px, head + rows * px), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((12, 12), f"{sheet['type']}  sheet {sheet['number']} of {sheet['of']}  ({sheet['sheet']})",
                  fill=(0, 0, 0), font=_font(28))
        for i, (letter, iid) in enumerate(sheet["letters"].items()):
            src = image_path(work, iid)
            if not src.is_file():
                missing.append(iid)
            t = _tile(src if src.is_file() else None, px)
            r, c = divmod(i, cols)
            img.paste(t, (c * px, head + r * px))
            draw.rectangle((c * px + 8, head + r * px + 8, c * px + 62, head + r * px + 62), fill=(20, 20, 20))
            draw.text((c * px + 20, head + r * px + 14), letter, fill=(255, 255, 255), font=_font(36))
            if src.is_file():
                tile_out = out / "tiles" / sheet["type"] / f"{iid}.jpg"
                tile_out.parent.mkdir(parents=True, exist_ok=True)
                _tile(src, tpx).save(tile_out, format="JPEG", quality=q)
                tiles += 1
        for c in range(1, cols):
            draw.line((c * px, head, c * px, head + rows * px), fill=(255, 255, 255), width=2)
        for r in range(1, rows):
            draw.line((0, head + r * px, cols * px, head + r * px), fill=(255, 255, 255), width=2)
        path = out / "sheets" / f"{sheet['sheet']}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format="JPEG", quality=q)
    log(f"ranking studio: {len(index['sheets'])} sheet(s), {tiles} tile(s), {len(missing)} model(s) not rendered "
        f"-> {out}")
    return {"sheets": len(index["sheets"]), "tiles": tiles, "missing": missing}


def results_doc(index: dict, work: Path) -> dict:
    """The run's record (``studio_results.json``): per model ok / failed with the Blender record's method, warnings
    and seconds."""
    from wenart.assets.audit import render as R
    rows = {}
    for iid in index["models"]:
        rec = R.read_measure(work, iid) or {}
        rows[iid] = {k: rec.get(k) for k in ("ok", "error", "method", "fallback_reason", "seconds", "warnings",
                                             "dressing", "box_min", "box_max") if k in rec}
        rows[iid]["rendered"] = image_path(work, iid).is_file()
    ok = sum(1 for r in rows.values() if r.get("ok") and r.get("rendered"))
    return {"version": STUDIO_VERSION, "models": len(rows), "ok": ok, "failed": len(rows) - ok, "rows": rows}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def batch_entries(batch: str = "", types: Optional[list[str]] = None, mode: str = "relaxed",
                  procedural: bool = False, proc_tag: str = PROC_TAG) -> list[dict]:
    """The models of one studio run: our builds (``procedural``), the ``remaining`` batch (``remaining_entries``,
    ``types`` narrowing it), else the furniture of ``types`` (default ``RANK_TYPES``)."""
    if procedural:
        return procedural_entries(tag=proc_tag)
    if batch == REMAINING:
        return remaining_entries(mode, types=list(types) if types else None)
    if batch:
        raise ValueError(f"unknown batch {batch!r} (known: {REMAINING})")
    return rank_entries(list(types) if types else RANK_TYPES, mode)


def main(argv: Optional[list[str]] = None) -> int:
    from wenart.assets.audit import EXIT_OK
    from wenart.assets.audit import render as R
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.audit.studio", description=__doc__.split("\n\n")[0])
    ap.add_argument("action", choices=("plan", "render", "sheets"))
    ap.add_argument("--types", default="",
                    help="comma list of types (default: bed_double,sofa,armchair; with --batch every type of the batch;"
                         f" there also the groups {', '.join(sorted(TYPE_ALIASES))})")
    ap.add_argument("--batch", default="", choices=("", REMAINING),
                    help="remaining: every library model the pipeline may use that no committed sheet shows (decor, "
                         "the extras the fit takes first, small items, other furniture types)")
    ap.add_argument("--mode", default="relaxed")
    ap.add_argument("--assets", default="/workspace/assets")
    ap.add_argument("--work", default="/workspace/library-ranking/work")
    ap.add_argument("--out", default="results/library/ranking")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--blender", default=None)
    ap.add_argument("--deadline", default=None)
    ap.add_argument("--limit", type=int, default=0, help="at most this many models per type (a smoke run)")
    ap.add_argument("--samples", type=int, default=None)
    ap.add_argument("--procedural", action="store_true",
                    help="our builds only (every parametric and module builder in the projects' styles)")
    ap.add_argument("--proc-tag", default=PROC_TAG, help="the group, id prefix and file suffix of our builds")
    a = ap.parse_args(argv)
    types = [t for t in a.types.split(",") if t]
    entries = batch_entries(a.batch, types, a.mode, procedural=a.procedural, proc_tag=a.proc_tag)
    suffix = f"_{a.proc_tag}" if a.procedural else (f"_{a.batch}" if a.batch else "")
    if a.batch:
        types = types or ["all"]
    if a.limit:
        kept: dict = {}
        entries = [e for e in entries if kept.setdefault(e.get("group") or e["type"], []).append(e)
                   or len(kept[e.get("group") or e["type"]]) <= a.limit]
    sheets = sheet_plan(entries)
    if a.batch:                                   # a new batch never takes a committed sheet's name
        check_sheet_names(sheets, committed_sheets(skip=(a.batch,)))
    index = index_doc(entries, sheets)
    out, work = Path(a.out), Path(a.work)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"ranking_index{suffix}.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    settings = {"samples": a.samples} if a.samples else None
    doc = plan(entries, Path(a.assets), work, settings, R.deadline_of(a.deadline))
    print(f"ranking studio: {len(entries)} model(s) of {types}: {len(doc['jobs'])} to render, {len(doc['skipped'])} "
          f"current, {len(doc['missing'])} file(s) missing; {len(sheets)} sheet(s)")
    if a.action == "plan":
        (out / f"studio_plan{suffix}.json").write_text(json.dumps({k: v for k, v in doc.items() if k != "jobs"} | {
            "jobs": [j["id"] for j in doc["jobs"]]}, indent=1) + "\n", encoding="utf-8")
        return EXIT_OK
    code = EXIT_OK
    if a.action == "render":
        t0 = time.time()
        code = R.run_render(doc, a.blender or R.default_blender(), work, a.workers, script=STUDIO_SCRIPT)
        print(f"ranking studio: render exit {code} in {time.time() - t0:.0f} s")
    compose_sheets(index, work, out, settings)
    res = results_doc(index, work)
    res["missing_files"] = doc["missing"]
    (out / f"studio_results{suffix}.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(f"ranking studio: {res['ok']} of {res['models']} model(s) rendered, {res['failed']} failed")
    return code


if __name__ == "__main__":
    sys.exit(main())
