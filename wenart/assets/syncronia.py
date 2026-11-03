"""The Syncronia manufacturer models of the user's zips as a library source (3 Nov 2026, the user: "Include into the
library (the proper ones) and also open up a new ranking tab in the ranking page for them so I can rank them" for
"beds.zip", then "In the Google Drive furniture folder there are 4 more zip files do the same to them"; before:
"Disregard the license things for now").

What: each zip (``ZIPS``: Google Drive ids and sizes; on the volume under ``INBOX`` since the inspection pods of
3 Nov 2026) is a download set of syncronia.com: one folder per product (``<category>/<brand>/<product>/``) with
``meta.json`` (title, brand, category, source page, the site's terms) and the model files in nested zips. ``ingest``:

- reads every member (``zip_inspect.scan``: nested zips opened, unsafe names refused) and takes every model a free
  tool opens: 3DS through Assimp, FBX / OBJ / COLLADA / glTF through Blender (``zip_inspect``); SketchUp files and CAD
  files (IGES, STEP, Rhino, 3ds Max) are listed as not ingested (no open-source mesh reader);
- types each model from its category (``CATEGORY_TYPES``: furniture and decor types), else from its names
  (``warehouse.name_type``), and measures it against the type's real size (``warehouse.choose``: metres, inches, cm,
  mm, feet; up axis): only the models that fit a real product size are taken ("the proper ones");
- fixes units, up axis and origin (``warehouse.fixup``), gives a model without materials its part materials
  (``part_materials.classify_any``: a bed's upholstered base, bedding and feet; any other model's material names, its
  feet, else its type's material) and writes ``<assets>/models/syncronia/<uid>.glb``; the front comes from a bed's
  head end, else the type's geometric rule;
- writes the catalogue entries (``entry``: ``source: syncronia``, furniture in ``entries``, decor in ``decor``,
  licence ``LICENCE`` flagged ``non_commercial``, the credit fields from ``meta.json``, ``audit: pending`` until the
  studio renders are looked at) to ``<out>/syncronia_entries.json`` and every model's record (taken or not, and why)
  to ``<out>/ingest_syncronia.json``. ``workers`` processes share the models; a model whose source, fix version and
  code are unchanged reuses its cached record (``<work>/cache``).

``merge`` puts entries into ``catalog_library.json`` (same id replaced; ``sources``, ``datasets`` and ``counts`` kept
current); ``review`` sets the audit of reviewed entries (keep / removed, the notes, a front).

Licence: the user's decision (3 Nov 2026) is to disregard licences for now; the site's own words in ``meta.json``
("for use in a design project and its renders; the file itself is not cleared for republishing") are kept in each
entry's ``syncronia`` record and in ``notice()``; relaxed licence mode only (``catalog.SOURCE_TEXT_FLAGS``).

CLI::

    python -m wenart.assets.syncronia ingest --zip Z --work DIR --assets DIR --out DIR [--merge-catalog] [--workers N]
    python -m wenart.assets.syncronia merge --entries E.json [--catalog PATH]
    python -m wenart.assets.syncronia review --decisions D.json [--catalog PATH]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path, PurePosixPath
from typing import Optional

SOURCE = "syncronia"
UID_PREFIX = "syncronia_"
UID_HEX = 24
LICENCE = "SYNCRONIA-UNREVIEWED"
LICENCE_FLAG = "non_commercial"
LICENCE_DECLARED_BY = "publisher"
LICENCE_URL = "https://www.syncronia.com/en"
INBOX = "/workspace/library/inbox"
# the user's zips (Google Drive id, bytes, name on the volume); beds.zip first (3 Nov 2026), then the folder Furnitures
ZIPS: tuple[tuple[str, int, str], ...] = (
    ("1iYSSFbHkn1DH2qtAJ7LF44bZccQ_SYwL", 462_846_689, "beds.zip"),
    ("1M82gvUOMzvwzohnjtPq7c0vibHzchXTK", 1_756_089_573, "archive1.zip"),
    ("11vr2z6dp0io9zig4TBC8j6hVa1woZTpF", 1_290_551_975, "archive2.zip"),
    ("1bQO5QfNUbvJFetW6GoOENX8eWq9BQqGx", 1_277_297_596, "archive3.zip"),
    ("10R1cAka9IKwWgRKj1wi2GdU3wl6Fr_41", 4_217_141_161, "archive4.zip"),
)
DRIVE_FILE_ID, ZIP_BYTES, ZIP_NAME = ZIPS[0]
ZIP_PATH = f"{INBOX}/{DRIVE_FILE_ID}/{ZIP_NAME}"
DATASET_NAME = "Syncronia manufacturer models (syncronia.com), the user's zips (beds.zip, the folder Furnitures)"
USER_DECISION = ("user request of 3 Nov 2026: include the proper models of the user's Syncronia zips in the library and "
                 "rank them; licence not reviewed (the user: \"Disregard the license things for now\"): relaxed licence "
                 "mode only, commercial_safe: no")
MIN_TRIANGLES = 100                   # under this a model is a placeholder block (Platek's 24-triangle lights)
FIX_VERSION = "syncronia-4"           # 2: part materials by pieces, name, type; 3: textures re-encoded; 4: missing
                                      # textures unlinked, a valid grey PNG
PENDING_REASON = "new Syncronia model (the user's zips, 3 Nov 2026): waiting for the look at its studio render"
# Syncronia's category folders (meta.json "type") -> the catalogue types (furniture or decor) a model may be
_BEDS = ("bed_double", "bed_single")
CATEGORY_TYPES: dict[str, tuple[str, ...]] = {
    **{k: _BEDS for k in ("beds", "bed", "double-beds", "single-beds", "letti", "upholstered-beds", "wooden-beds")},
    **{k: ("sofa", "sofa_corner") for k in ("sofas", "sofa", "divani", "modular-sofas", "sectional-sofas",
                                            "corner-sofas", "sofa-beds", "divani-letto")},
    **{k: ("armchair",) for k in ("armchairs", "armchair", "poltrone", "poltroncine", "comfort-chair", "lounge-chairs",
                                  "easy-chairs", "small-armchairs", "recliners", "garden-armchairs")},
    **{k: ("chair",) for k in ("chairs", "chair", "sedie", "dining-chairs", "garden-chairs", "chairs-with-armrests")},
    **{k: ("bar_stool",) for k in ("stools", "bar-stools", "sgabelli", "counter-stools")},
    **{k: ("chaise", "armchair") for k in ("chaises-longues", "chaise-longue", "day-beds", "daybeds", "dormeuse")},
    **{k: ("ottoman",) for k in ("poufs", "pouf", "ottomans", "footstools", "pouffes")},
    **{k: ("bench",) for k in ("benches", "bench", "panche", "panchette")},
    **{k: ("table_dining",) for k in ("tables", "table", "dining-tables", "extendable-table", "extendable-tables",
                                      "tavoli", "garden-tables", "round-tables", "rectangular-tables")},
    **{k: ("table_coffee", "side_table") for k in ("coffee-table", "coffee-tables", "tavolini", "low-tables",
                                                   "occasional-tables")},
    **{k: ("side_table", "table_coffee", "console_table") for k in ("side-tables", "side-table", "complemento-giorno",
                                                                    "complementi", "accessories")},
    **{k: ("console_table",) for k in ("console-tables", "consoles", "consolle")},
    **{k: ("desk",) for k in ("desks", "desk", "writing-desks", "scrivanie", "secretary-desks")},
    **{k: ("office_chair",) for k in ("office-chairs", "task-chairs", "executive-chairs")},
    **{k: ("sideboard", "tv_unit") for k in ("sideboards", "sideboard", "madie", "credenze", "buffets", "cabinets",
                                             "storage-units", "contenitori")},
    **{k: ("tv_unit", "sideboard") for k in ("tv-cabinets", "tv-units", "media-units", "porta-tv")},
    **{k: ("bookshelf", "display_cabinet") for k in ("bookcases", "bookshelves", "librerie", "shelving", "shelves",
                                                     "shelving-units", "libreria")},
    **{k: ("nightstand",) for k in ("bedside-tables", "bedside-table", "nightstands", "comodini")},
    **{k: ("dresser",) for k in ("chests-of-drawers", "dressers", "cassettiere", "chest-of-drawers", "settimanali")},
    **{k: ("wardrobe",) for k in ("wardrobes", "armadi", "wardrobe")},
    **{k: ("display_cabinet",) for k in ("display-cabinets", "vetrine", "showcases")},
    **{k: ("ceiling_light", "pendant_light") for k in ("ceiling-lamps", "ceiling-lights", "plafoniere",
                                                       "ceiling-lamp")},
    **{k: ("pendant_light", "ceiling_light") for k in ("pendant-lamps", "suspension-lamps", "sospensioni",
                                                       "pendant-lamp", "chandeliers", "lampadari")},
    **{k: ("table_lamp",) for k in ("table-lamps", "table-lamp", "lampade-da-tavolo", "desk-lamps")},
    **{k: ("floor_lamp",) for k in ("floor-lamps", "floor-lamp", "lampade-da-terra")},
    **{k: ("mirror",) for k in ("mirrors", "mirror", "specchi")},
    **{k: ("vase",) for k in ("vases", "vase", "vasi")},
    **{k: ("bowl", "tray") for k in ("bowls", "dishes", "centrepieces", "centerpieces", "centrotavola", "fruit-bowls")},
    **{k: ("tray", "bowl") for k in ("trays", "vassoi")},
    **{k: ("sculpture", "vase", "bowl") for k in ("decorative-objects", "objects", "oggetti", "sculptures",
                                                  "oggetti-decorativi", "complementi-d-arredo")},
    **{k: ("clock",) for k in ("clocks", "wall-clocks", "orologi")},
    **{k: ("rug",) for k in ("rugs", "carpets", "tappeti")},
    **{k: ("cushion",) for k in ("cushions", "cuscini")},
    **{k: ("basket",) for k in ("baskets", "cestini")},
    **{k: ("candle",) for k in ("candle-holders", "candles", "candelabra", "portacandele")},
    **{k: ("stove",) for k in ("cookers", "ovens", "hobs", "cucine", "range-cookers")},
    **{k: ("fridge",) for k in ("refrigerators", "fridges", "frigoriferi")},
    **{k: ("washbasin",) for k in ("washbasins", "lavabi", "washbasin", "bathroom-sinks")},
    # Syncronia's "sinks" are inset kitchen sinks (Schock, 3 Nov 2026): the kitchen sink type, whose real size (a unit
    # with its cabinet) such a sink never fits, so none is taken as a washbasin
    **{k: ("sink_kitchen",) for k in ("kitchen-sinks", "lavelli", "sinks")},
    # no catalogue type: bathroom accessories (Rexa stools, stands), wall and recessed lamps (3 Nov 2026)
    **{k: () for k in ("bathroom", "bathroom-accessories", "wall-recessed-lamps", "wall-lamps", "recessed-lamps",
                       "outdoor-lamps", "spotlights")},
    **{k: ("bathtub",) for k in ("bathtubs", "vasche", "bathtub")},
    **{k: ("toilet",) for k in ("toilets", "wc", "vasi-wc", "sanitari")},
    **{k: ("shower",) for k in ("showers", "shower-trays", "docce", "shower-cabins")},
}
BRANDS = {"bb-italia": "B&B Italia", "maxalto": "Maxalto (B&B Italia)", "riva1920": "Riva 1920",
          "riva-1920": "Riva 1920", "mdf-italia": "MDF Italia", "horm": "Horm", "et-al": "et al.",
          "molteni": "Molteni&C", "alessi": "Alessi", "platek": "Platek", "panzeri": "Panzeri", "baxter": "Baxter",
          "marte-design": "Marte Design", "tonon": "Tonon", "azucena": "Azucena", "schock": "Schock",
          "civic": "Civic", "cassina": "Cassina", "poltrona-frau": "Poltrona Frau", "flexform": "Flexform",
          "minotti": "Minotti", "kartell": "Kartell", "magis": "Magis", "cappellini": "Cappellini",
          "porro": "Porro", "living-divani": "Living Divani", "gervasoni": "Gervasoni", "pedrali": "Pedrali"}
# what the brands make (their own descriptions): the style families of the catalogue; others: modern
BRAND_STYLES = {"bb-italia": ["modern", "modern minimal"], "maxalto": ["modern", "classic"],
                "riva1920": ["modern", "rustic"], "riva-1920": ["modern", "rustic"], "mdf-italia": ["modern minimal"],
                "horm": ["modern"], "baxter": ["modern", "classic"], "molteni": ["modern", "modern minimal"],
                "alessi": ["modern"], "et-al": ["modern", "minimal"], "tonon": ["modern"]}
NOT_INGESTED = {".skp": "SketchUp file: no open-source reader (export it as COLLADA or glTF from SketchUp)",
                ".igs": "IGES CAD surfaces: no mesh (tessellate it in a CAD tool first)",
                ".iges": "IGES CAD surfaces: no mesh (tessellate it in a CAD tool first)",
                ".stp": "STEP CAD solid: no mesh (tessellate it in a CAD tool first)",
                ".step": "STEP CAD solid: no mesh (tessellate it in a CAD tool first)",
                ".3dm": "Rhino file: no open-source mesh reader here",
                ".max": "3ds Max file: no open-source reader (export it as FBX or 3DS)"}


def uid_of(rel: str) -> str:
    return UID_PREFIX + hashlib.sha256(str(rel).encode("utf-8")).hexdigest()[:UID_HEX]


def model_rel(uid: str) -> str:
    return f"models/{SOURCE}/{uid}.glb"


def brand_of(rel: str, meta: dict) -> str:
    return str(meta.get("brand") or (PurePosixPath(rel).parts[1] if len(PurePosixPath(rel).parts) > 1 else ""))


def brand_name(key: str) -> str:
    return BRANDS.get(key) or " ".join(w.capitalize() for w in str(key or "the manufacturer").split("-"))


def category_of(rel: str, meta: dict) -> str:
    return str(meta.get("type") or PurePosixPath(rel).parts[0]).lower()


def entry_fields() -> dict:
    return {"licence": LICENCE, "licence_url": LICENCE_URL, "licence_flag": LICENCE_FLAG,
            "licence_declared_by": LICENCE_DECLARED_BY, "commercial_safe": False}


def notice() -> str:
    return (f"{DATASET_NAME}: manufacturer product models downloaded from syncronia.com by the user; the site's own "
            "words: for use in a design project and its renders, the files not cleared for republishing. Licence not "
            "reviewed (the user's decision of 3 Nov 2026): relaxed licence mode only, commercial_safe: no. Changes: "
            "converted from 3DS / FBX / OBJ, units, up axis and origin fixed, part materials added, scaled to the "
            "drawn footprint.")


def product_name(meta: dict, rel: str) -> str:
    """The product's own name: ``meta.json``'s title without its category ("Beds, Demetra" -> "Demetra")."""
    from wenart.assets.audit.growth_entries import source_text
    t = source_text(meta.get("title") or PurePosixPath(rel).parent.name)
    return t.split(", ", 1)[1] if ", " in t else t


def variant_title(meta: dict, rel: str, size_m: list, ftype: str = "bed_double") -> str:
    """Brand, product and size: several sizes of one product are told apart (Demetra 1.95 / 2.10 / 2.21 / 2.41 m). A
    bed says "bed W x D"; any other model "(W x D x H cm)"."""
    brand = brand_name(brand_of(rel, meta)) if brand_of(rel, meta) else ""
    name = product_name(meta, rel)
    if ftype in _BEDS:
        w, d = sorted(float(v) for v in size_m[:2])
        return f"{brand} {name} bed {w * 100:.0f} x {d * 100:.0f}".strip()
    w, d, h = (float(v) for v in size_m[:3])
    return f"{brand} {name} ({w * 100:.0f} x {d * 100:.0f} x {h * 100:.0f} cm)".strip()


def entry(rec: dict, m: dict, meta: dict, checked_utc: str) -> dict:
    """A ``catalog_library.json`` entry of an ingested model (``rec`` = its ingest record, ``m`` = ``glbmesh.measure``
    of the written file): furniture, or decor (``type: decor_<t>``, ``decor_type``) for a decor type."""
    from wenart.assets.audit import growth_entries as GE
    from wenart.furniture import catalog as C
    ftype, uid = rec["type"], rec["uid"]
    kind = "decor" if ftype in C.DECOR_TYPES else "furniture"
    if rec.get("front"):
        front, conf, note = rec["front"], rec["front_confidence"], rec["front_note"]
    else:
        front, conf, note = GE.front_of(ftype, m.get("stats"))
    title = variant_title(meta, rec["rel"], m["bbox_model_m"], ftype)
    brand_key = brand_of(rec["rel"], meta)
    author = f"{brand_name(brand_key)} (manufacturer model, via Syncronia)"
    styles = [s for s in BRAND_STYLES.get(brand_key, ["modern"]) if s in C.style_values()] or ["neutral"]
    fmt = str(rec.get("format") or ".3ds").lstrip(".").upper()
    e = {"id": uid, **GE._kind_type(kind, ftype), "source": SOURCE, **entry_fields(), "name": title}
    e.update(GE.frame_fields(m, front, conf, note))
    w, d, h = e["bbox_m"]
    raw = " x ".join(f"{float(v):.4g}" for v in rec.get("raw_box") or [])
    zip_name = rec.get("zip") or ZIP_NAME
    e.update({"unit_scale": 1.0, "units_known": True,
              "unit_note": (f"units known: the {fmt} box {raw} read in {rec['unit']} fits a real {ftype} (size "
                            f"table); written in metres by the syncronia fix-up: {w:.3g} x {d:.3g} x {h:.3g} m"),
              "styles": styles, "style_note": f"the brand {brand_name(brand_key)}: {', '.join(styles)}",
              "glb": model_rel(uid), "sha256_glb": rec["sha256"], "uid": uid, "title": title, "author": author,
              "brand": brand_name(brand_key), "real_product": True,
              "source_url": str(meta.get("source") or LICENCE_URL),
              "via": f"{DATASET_NAME}; converted by wenart/assets/syncronia.py ({FIX_VERSION})",
              "attribution": (f"\"{title}\" by {author}, {meta.get('source') or LICENCE_URL}, from the user's zip "
                              f"\"{zip_name}\" ({rec['rel']}); licence not reviewed ({USER_DECISION}); changes: "
                              f"converted from {fmt}, units, up axis and origin fixed, part materials added, scaled "
                              "to the drawn footprint, re-oriented, rendered; PoC use in relaxed licence mode only")})
    e.update(GE._mesh_fields(m))
    if m.get("pbr"):
        e["pbr_maps"] = dict(m["pbr"])
    classes = rec.get("classes") or {}
    if ftype in _BEDS:
        bedding = bool(classes.get("bedding"))
        e.update({"has_mattress": bedding, "has_bedding": bedding, "has_pillows": bool(rec.get("pillows")),
                  "has_cushions": False, "bed_frame": False,
                  "bed_note": ("the model carries its own mattress and bedding (part classes of "
                               "wenart.assets.part_materials)" if bedding else "no bedding part found")})
    if rec.get("material"):
        from wenart.assets import part_materials as PM
        e.update(PM.material_fields(rec["material"]["slots"]))
        e["material_tags_note"] = ("part materials of wenart.assets.part_materials (the file has no materials): by "
                                   "part (a bed), material names, feet and the type's material")
    e["syncronia"] = {"rel": rec["rel"], "zip": zip_name, "category": rec.get("category"),
                      "format": rec.get("format"), "unit": rec.get("unit"), "factor": rec.get("factor"),
                      "up_fix": rec.get("up_fix"), "raw_box_m": rec.get("raw_box"),
                      "candidates": rec.get("candidates"), "converter": rec.get("converter"),
                      "part_classes": classes, "fix_version": FIX_VERSION, "src_sha256": rec.get("src_sha256"),
                      "meta": {k: meta.get(k) for k in ("title", "brand", "type", "source", "licence", "terms")}}
    e["growth"] = {"pod": "syncronia", "list": "ingest_syncronia.json", "decision": USER_DECISION}
    e["audit"] = {"status": "pending", "reasons": [PENDING_REASON], "fixes": {}, "version": FIX_VERSION,
                  "checked_utc": checked_utc}
    return e


def types_for(rel: str, meta: dict) -> tuple[list[str], str]:
    """The catalogue types a model may be: its category's (``CATEGORY_TYPES``), else its names' (``name_type``)."""
    from wenart.assets import warehouse as WH
    from wenart.furniture import catalog as C
    cat = category_of(rel, meta)
    if cat in CATEGORY_TYPES:
        return list(CATEGORY_TYPES[cat]), (f"category {cat}" if CATEGORY_TYPES[cat] else
                                           f"category {cat}: no catalogue type for it")
    names = WH.name_type(rel)
    valid = set(C.FURNITURE_TYPES) | set(C.DECOR_TYPES)          # a set or object family is no catalogue type
    cands = [c for c in names.get("candidates") or [] if c in valid and c not in ("unknown", "stair")]
    return cands, (f"names ({names.get('where')})" if cands else f"category {cat}: no type")


def _cache_key(src_sha: str) -> str:
    from wenart.assets import part_materials as PM
    code = Path(PM.__file__).read_bytes() + Path(__file__).read_bytes()
    return hashlib.sha256(src_sha.encode() + FIX_VERSION.encode() + code).hexdigest()[:24]


def _one(job: dict) -> dict:
    """One model (a worker process): measure, fix, part materials, front, entry. Returns ``{"rec", "entry"}``."""
    from wenart.assets import part_materials as PM
    from wenart.assets import warehouse as WH
    from wenart.assets import zip_inspect as ZI
    from wenart.assets.audit import glbmesh as GM
    from wenart.assets.audit import growth_entries as GE
    mdl, rec, meta = job["mdl"], dict(job["rec"]), job["meta"]
    work, assets, out = Path(job["work"]), Path(job["assets"]), Path(job["out"])
    cache_dir = Path(job.get("cache") or work / "cache")
    try:
        glb = Path(mdl["src"]) if mdl["format"] == ".glb" else work / "converted" / f"{mdl['id']}.glb"
        rec["src_sha256"] = WH.sha256_file(Path(mdl["src"]))
        key = _cache_key(rec["src_sha256"])
        cache = cache_dir / f"{rec['uid']}.json"
        dest = assets / model_rel(rec["uid"])
        if cache.is_file() and dest.is_file():
            old = json.loads(cache.read_text(encoding="utf-8"))
            if old.get("key") == key and old.get("sha256") == WH.sha256_file(dest):
                return {"rec": dict(old["rec"], cached=True), "entry": old.get("entry")}
        if mdl["format"] == ".3ds":                       # Assimp in the worker: the models convert in parallel
            r = ZI.assimp_convert(Path(mdl["src"]), glb)
            rec["converter"] = "assimp" if r.get("ok") else "none"
            if not r.get("ok"):
                rec["why"] = f"not converted: {r.get('error')}"
                return {"rec": rec, "entry": None}
        types, why = types_for(rec["rel"], meta)
        rec["category"] = category_of(rec["rel"], meta)
        rec["types_from"] = why
        if not types:
            rec["why"] = f"no catalogue type ({why})"
            return {"rec": rec, "entry": None}
        mrec = ZI.measure_one(mdl, glb, work, types)
        rec.update({k: mrec.get(k) for k in ("type", "unit", "factor", "up_fix", "fits", "size_error", "box_m",
                                             "raw_box", "candidates", "triangles", "error")})
        if not mrec.get("ok"):
            rec["why"] = f"not measured: {mrec.get('error')}"
            return {"rec": rec, "entry": None}
        if not mrec.get("fits") or mrec.get("type") not in types:
            rec["why"] = f"size outside every real {'/'.join(types)} size: not a proper model"
            return {"rec": rec, "entry": None}
        if int(mrec.get("triangles") or 0) < MIN_TRIANGLES:
            rec["why"] = f"{mrec.get('triangles')} triangles: a placeholder block, not a product model"
            return {"rec": rec, "entry": None}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(Path(mrec["fixed"]).read_bytes())          # units, up axis, origin (warehouse.fixup)
        doc, _bin = WH.read_glb(dest)
        ps = PM.parts(dest)
        classes = PM.classify_any(ps, rec["type"])
        PM.write_debug(cache_dir.parent / "parts" / f"{rec['uid']}.json", ps, classes)   # beside the cache
        if classes and PM.needs_materials(doc):
            rec["material"] = PM.assign(dest, dest, ps, classes)
            rec["classes"] = rec["material"]["classes"]
        else:
            rec["classes"] = {}
        rec["pillows"] = sum(1 for p, c in zip(ps, classes) if c["class"] == "bedding"
                             and (c["by"] == "geometry:pillow" or (c["by"] == "name" and any(
                                 w in PM._name_tokens(p.get("node"), p.get("mesh_name"), p.get("material_name"))
                                 for w in ("pillow", "cuscin", "guancial", "oreiller", "kissen", "almohad")))))
        rec["split_primitives"] = (rec.get("material") or {}).get("split", 0)
        m = GM.measure(dest)
        g_front, g_conf, g_note = GE.front_of(rec["type"], m.get("stats"))
        fr = PM.front_from_parts(ps, classes) if rec["type"] in PM.BED_TYPES else None
        if fr:
            agree = g_conf != "low" and g_front == fr[0]
            rec.update(front=fr[0], front_confidence="high" if agree else "medium",
                       front_note=fr[1] + (f"; geometry agrees ({g_note})" if agree else f"; geometry: {g_note}"))
        else:
            rec.update(front=g_front, front_confidence=g_conf, front_note=g_note)
        rec["sha256"] = WH.sha256_file(dest)
        rec["taken"] = True
        e = entry(rec, m, meta, job["checked"])
        rec["id"], rec["title"] = e["id"], e["title"]
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"key": key, "sha256": rec["sha256"], "rec": rec, "entry": e},
                                    ensure_ascii=False), encoding="utf-8")
        return {"rec": rec, "entry": e}
    except Exception as exc:  # noqa: BLE001 - one model never stops the intake (3 Nov 2026)
        rec.update(taken=False, why=f"failed: {type(exc).__name__}: {exc}")
        return {"rec": rec, "entry": None}


def ingest(zip_path: Path, work: Path, assets: Path, out: Path, blender: Optional[str] = None,
           workers: int = 1, zip_name: Optional[str] = None, cache: Optional[Path] = None) -> dict:
    """Every model of the zip (module docstring); returns ``{"records": [...], "entries": [...]}``."""
    from wenart.assets import zip_inspect as ZI
    checked = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    zip_name = zip_name or Path(zip_path).name
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    ZI.scan(zip_path, work)
    models = ZI.model_list(work)
    conv: dict = {}
    blender_jobs = []
    for mdl in models:
        if mdl["format"] == ".3ds":
            conv[mdl["id"]] = {"ok": True, "converter": "assimp (in the worker)"}
        elif mdl["format"] not in (".glb", ".skp") and mdl["format"] not in NOT_INGESTED:
            blender_jobs.append({"id": mdl["id"], "src": mdl["src"],
                                 "dst": str(work / "converted" / f"{mdl['id']}.glb")})
    if blender_jobs and blender:
        for k, v in ZI.blender_run(blender, "convert", blender_jobs, work, timeout_s=3600).items():
            if v.get("ok"):
                conv[k] = dict(v, converter="blender")
    records, entries, jobs = [], [], []
    for mdl in models:
        rel = mdl["rel"]
        meta = ZI.meta_for(rel, work)
        rec: dict = {"rel": rel, "zip": zip_name, "format": mdl["format"], "uid": uid_of(rel), "taken": False}
        if mdl["format"] in NOT_INGESTED:
            records.append(dict(rec, why=NOT_INGESTED[mdl["format"]]))
            continue
        if mdl["format"] != ".glb" and mdl["id"] not in conv:
            records.append(dict(rec, why="not converted (no free tool opened it)"))
            continue
        rec["converter"] = (conv.get(mdl["id"]) or {}).get("converter", "none")
        jobs.append({"mdl": mdl, "rec": rec, "meta": meta, "work": str(work), "assets": str(assets),
                     "out": str(out), "checked": checked, "cache": str(cache) if cache else None})
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_one, jobs, chunksize=1))
    else:
        results = [_one(j) for j in jobs]
    for r in results:
        records.append(r["rec"])
        if r.get("entry"):
            entries.append(r["entry"])
    doc = {"zip": str(zip_path), "zip_name": zip_name, "checked_utc": checked, "fix_version": FIX_VERSION,
           "taken": sum(1 for r in records if r.get("taken")), "listed": len(records), "records": records}
    (out / "ingest_syncronia.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "syncronia_entries.json").write_text(json.dumps({"entries": entries}, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    return {"records": records, "entries": entries}


def catalog_path() -> Path:
    from wenart.assets.audit import items as I
    return Path(I.LIBRARY_PATH)


def _write(path: Path, doc: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def merge(entries: list[dict], path: Optional[Path] = None) -> dict:
    """The entries into the library catalogue: furniture into ``entries``, decor into ``decor`` (same id replaced in
    either list, new ids appended); the catalogue's ``sources`` list, a ``datasets`` note and ``counts`` for the
    source. Returns ``{"added", "replaced"}``."""
    path = Path(path) if path else catalog_path()
    doc = json.loads(path.read_text(encoding="utf-8"))
    lists = {"entries": doc.setdefault("entries", []), "decor": doc.setdefault("decor", [])}
    added = replaced = 0
    for e in entries:
        target = "decor" if e.get("kind") == "decor" else "entries"
        for name, rows in lists.items():                          # an id that changed kind leaves its old list
            if name != target:
                rows[:] = [x for x in rows if x.get("id") != e["id"]]
        rows = lists[target]
        at = next((i for i, x in enumerate(rows) if x.get("id") == e["id"]), None)
        old = rows[at] if at is not None else None
        if old and old.get("sha256_glb") == e.get("sha256_glb") and (old.get("audit") or {}).get("reviewed_by"):
            e = dict(e, audit=old["audit"], front_axis=old["front_axis"], bbox_m=old["bbox_m"],
                     front_axis_note=old.get("front_axis_note"),
                     front_axis_confidence=old.get("front_axis_confidence"))   # the same file keeps its review
        if at is None:
            rows.append(e)
            added += 1
        else:
            rows[at] = e
            replaced += 1
    if SOURCE not in (doc.get("sources") or []):
        doc.setdefault("sources", []).append(SOURCE)
    datasets = doc.get("datasets")
    if isinstance(datasets, dict):
        datasets[SOURCE] = {"name": DATASET_NAME, "licence": LICENCE, "licence_url": LICENCE_URL,
                            "decision": USER_DECISION, "notice": notice()}
    counts = doc.get("counts")
    if isinstance(counts, dict):
        counts[SOURCE] = {"entries": sum(1 for e in lists["entries"] if e.get("source") == SOURCE),
                          "decor": sum(1 for e in lists["decor"] if e.get("source") == SOURCE)}
    _write(path, doc)
    return {"added": added, "replaced": replaced}


def review(decisions: dict, path: Optional[Path] = None) -> dict:
    """The audit of reviewed entries (furniture or decor): ``decisions`` = ``{id: {"status": "keep" | "removed",
    "notes": [...], "reasons": [...], "front_axis"?: axis}}``; a new front axis re-orients ``bbox_m``. Returns the
    counts."""
    from wenart.furniture import catalog as C
    path = Path(path) if path else catalog_path()
    doc = json.loads(path.read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    done: dict[str, int] = {}
    for e in list(doc.get("entries") or []) + list(doc.get("decor") or []):
        d = decisions.get(e.get("id"))
        if not d or e.get("source") != SOURCE:
            continue
        if d.get("front_axis") and d["front_axis"] != e["front_axis"]:
            e["front_axis"] = d["front_axis"]
            e["bbox_m"] = [round(float(v), 4) for v in C.oriented_bbox(e["bbox_model_m"], d["front_axis"])]
            e["front_axis_note"] = str(d.get("front_note") or "front set at the review of the studio render")
        if d.get("front_axis_confidence"):
            e["front_axis_confidence"] = d["front_axis_confidence"]
        e["audit"] = {"status": d["status"], "reasons": list(d.get("reasons") or []), "fixes": {},
                      "notes": list(d.get("notes") or []), "version": FIX_VERSION, "checked_utc": now,
                      "reviewed_by": d.get("by") or "Claude (look at the ranking studio render, user request of 3 Nov "
                                                       "2026)"}
        done[d["status"]] = done.get(d["status"], 0) + 1
    _write(path, doc)
    return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.syncronia")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("ingest")
    i.add_argument("--zip", default=ZIP_PATH)
    i.add_argument("--zip-name", default=None)
    i.add_argument("--work", required=True)
    i.add_argument("--assets", required=True)
    i.add_argument("--out", required=True)
    i.add_argument("--blender", default=None)
    i.add_argument("--cache", default=None, help="the per-model cache (default <work>/cache; keep it on the volume)")
    i.add_argument("--workers", type=int, default=max(1, min(16, (os.cpu_count() or 2) - 1)))
    i.add_argument("--merge-catalog", action="store_true", help="also merge the entries into the catalogue (pending)")
    mg = sub.add_parser("merge")
    mg.add_argument("--entries", required=True)
    mg.add_argument("--catalog", default=None)
    rv = sub.add_parser("review")
    rv.add_argument("--decisions", required=True)
    rv.add_argument("--catalog", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "ingest":
        res = ingest(Path(a.zip), Path(a.work), Path(a.assets), Path(a.out), a.blender, a.workers, a.zip_name,
                     Path(a.cache) if a.cache else None)
        types: dict = {}
        for e in res["entries"]:
            types[e.get("decor_type") or e["type"]] = types.get(e.get("decor_type") or e["type"], 0) + 1
        print(json.dumps({"taken": len(res["entries"]), "listed": len(res["records"]), "types": types},
                         ensure_ascii=False))
        if a.merge_catalog and res["entries"]:
            print(json.dumps(merge(res["entries"])))
        return 0 if res["entries"] else 1
    if a.cmd == "merge":
        ents = json.loads(Path(a.entries).read_text(encoding="utf-8"))["entries"]
        print(json.dumps(merge(ents, Path(a.catalog) if a.catalog else None)))
        return 0
    print(json.dumps(review(json.loads(Path(a.decisions).read_text(encoding="utf-8")),
                            Path(a.catalog) if a.catalog else None)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
