"""Growth scaffolding of the library (docs/milestone12.md §6.4 D24): candidate LISTS for the user's OK; nothing is
downloaded before an approved list exists.

What (``python -m wenart.assets growth <source> list | ingest``):

- ``polyhaven list``: the Poly Haven models (API ``https://api.polyhaven.com/assets?t=models``, CC0) not in
  ``catalog.json``, in our furniture and decor types (title, category and tag words, ``keywords.py``), with the
  download size of the 2k glTF (``/files/<id>``) -> ``results/library/growth/candidates_polyhaven.json``.
- ``abo list``: the ABO style pass (metadata only: the models csv, the 16 listings shards and the bucket listing for
  the GLB sizes): unused models of our types whose listing style is rustic / farmhouse, industrial or classic /
  traditional, and the decor pass (pillows, rugs, wall art) and headboards -> ``candidates_abo.json``.
- ``gso list``: Google Scanned Objects small decor (bowls, pots, vases, baskets, trays, candles, mugs, towels) from the
  Hugging Face mirror's file list -> ``candidates_gso.json``.
- ``infinigen plan``: the test batch of procedural fixtures (Infinigen Indoors, BSD-3) -> ``plan_infinigen.json``.
- ``<source> ingest``: refuses to run unless ``results/library/growth/approved_<source>.json`` exists (the lead
  commits it after the user's OK of the list) and holds ``approved_by``, ``approved_utc`` and the ``ids``; then it
  downloads exactly those ids (Poly Haven: ``wenart.assets.models.fetch_model``; ABO: the GLBs into the cache) for the
  library steps (thumbnails, audit, catalogue) of pod P4. GSO and Infinigen ingest are P4 work (not built here).

Every list holds per candidate: source, id, title, type, kind, licence, size in MB (and the totals), plus what decided
the type. Lists are sorted (type, id) and carry the query time given by the caller.

Why: CLAUDE.md library rules and D22/D24: growth only after the user's OK of a list (source, licence, count,
download size).

How: the list builders are pure (``*_candidates``: tests feed canned API answers); the network helpers cache every
answer under ``--cache`` (default ``~/.cache/wenart/growth``) and fetch metadata only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import DEFAULT_OUT, EXIT_NOTHING, EXIT_OK, GROWTH_DIR
from wenart.assets.audit import keywords as K

PH_API = "https://api.polyhaven.com"
ABO_BASE = "https://amazon-berkeley-objects.s3.amazonaws.com"
GSO_REPO = "suvadityamuk/google-scanned-objects-raw"
HF_API = "https://huggingface.co/api/datasets/"
SOURCES = ("polyhaven", "abo", "gso", "infinigen")
USER_AGENT = "wenart-run/0.1 (library growth lists)"
STYLE_WORDS = (("rustic", "rustic"), ("farmhouse", "rustic"), ("industrial", "industrial"), ("traditional", "classic"),
               ("classic", "classic"), ("victorian", "classic"), ("baroque", "classic"), ("antique", "classic"),
               ("vintage", "classic"), ("chinese", "classic"), ("scandinavian", "scandinavian"),
               ("japanese", "japandi"), ("mid century", "modern"), ("modern", "modern"), ("mediterranean",
                                                                                         "mediterranean"))
ABO_FAMILIES = ("rustic", "industrial", "classic")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def growth_dir(out=None) -> Path:
    return Path(out or DEFAULT_OUT) / GROWTH_DIR


def known_types() -> dict:
    """``{type: kind}`` of our furniture and decor types (stair, counters and wall cabinets are parametric)."""
    from wenart.furniture import catalog as C
    out = {t: "furniture" for t in C.FURNITURE_TYPES if t not in ("unknown", "stair", "kitchen_counter",
                                                                   "kitchen_island", "wall_cabinet")}
    out.update({t: "decor" for t in C.DECOR_TYPES})
    return out


def type_from_text(*texts: str) -> tuple[Optional[str], str]:
    """The first of our types the texts name (title first, then category, then tags): ``(type, word)``."""
    known = known_types()
    for text in texts:
        for f in K.named_families(text or ""):
            types = [t for t in K.FAMILY_TYPES.get(f["family"], ()) if t in known]
            if types:
                return types[0], f["word"]
    return None, ""


def styles_from_text(text: str) -> list[str]:
    folded = " " + K.fold(text) + " "
    out = []
    for word, fam in STYLE_WORDS:
        if f" {word} " in folded and fam not in out:
            out.append(fam)
    return out


# --------------------------------------------------------------------------
# Poly Haven
# --------------------------------------------------------------------------

def ph_size_mb(files: Optional[dict], res: str = "2k") -> Optional[float]:
    g = ((files or {}).get("gltf") or {}).get(res) or {}
    g = g.get("gltf") or {}
    if not g:
        return None
    total = int(g.get("size") or 0) + sum(int(v.get("size") or 0) for v in (g.get("include") or {}).values())
    return round(total / 1e6, 2)


# Poly Haven category path (``category`` of the API) -> our types, tried in order against the real-size table.
PH_CATEGORY_TYPES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Furniture/Beds", ("bed_double", "bed_single", "chaise", "sofa")),
    ("Furniture/Seating/Benches", ("bench",)),
    ("Furniture/Seating/Chairs", ("chair", "armchair", "office_chair")),
    ("Furniture/Seating/Ottomans & Footstools", ("ottoman",)),
    ("Furniture/Seating/Sofas & Couches", ("sofa", "sofa_corner", "chaise")),
    ("Furniture/Seating/Stools & Bar Seating", ("bar_stool", "ottoman")),
    ("Furniture/Storage Furniture/Cabinets & Cupboards", ("sideboard", "tall_cabinet", "display_cabinet", "wardrobe",
                                                          "dresser", "nightstand")),
    ("Furniture/Storage Furniture/Drawers & Dressers", ("dresser", "nightstand", "tall_cabinet")),
    ("Furniture/Storage Furniture/Shelving & Bookcases", ("bookshelf",)),
    ("Furniture/Storage Furniture/Sideboards", ("sideboard", "tv_unit")),
    ("Furniture/Tables/Coffee Tables", ("table_coffee", "side_table")),
    ("Furniture/Tables/Console Tables", ("console_table",)),
    ("Furniture/Tables/Desks", ("desk",)),
    ("Furniture/Tables/Dining Tables", ("table_dining",)),
    ("Furniture/Tables/Side & End Tables", ("side_table", "nightstand", "table_coffee")),
    ("Lighting/Ceiling/Chandeliers", ("pendant_light",)),
    ("Lighting/Ceiling/Industrial Pendants", ("pendant_light",)),
    ("Lighting/Ceiling/Pendant Lights", ("pendant_light", "ceiling_light")),
    ("Lighting/Floor & Desk/Desk Lamps", ("table_lamp",)),
    ("Lighting/Floor & Desk/Floor Lamps", ("floor_lamp",)),
    ("Lighting/Portable/Candles & Candlesticks", ("candle",)),
    ("Lighting/Portable/Lanterns", ("candle",)),
    ("Decor & Art/Ornaments/Cushions & Pillows", ("cushion",)),
    ("Decor & Art/Sculptures & Figurines", ("sculpture",)),
    ("Decor & Art/Vases & Vessels", ("vase", "plant_small")),
    ("Decor & Art/Wall Decor/Mirrors", ("mirror",)),
    ("Decor & Art/Wall Decor/Picture Frames & Art", ("wall_art",)),
    ("Decor & Art/Wall Decor/Wall Clocks", ("clock",)),
    ("Containers & Storage/Baskets & Buckets/Baskets", ("basket",)),
    ("Office & Stationery/Books & Documents/Books", ("books",)),
    ("Food & Kitchen/Tableware/Bowls", ("bowl",)),
    ("Nature/Plants/Potted Plants", ("plant_large", "potted_plant", "plant_small")),
)


def ph_types(category: Optional[str]) -> tuple[str, ...]:
    """The types of the longest category prefix of ``PH_CATEGORY_TYPES`` (empty: none of ours)."""
    cat = str(category or "")
    best = ""
    types: tuple[str, ...] = ()
    for prefix, ts in PH_CATEGORY_TYPES:
        if (cat == prefix or cat.startswith(prefix + "/")) and len(prefix) > len(best):
            best, types = prefix, ts
    return types


def pick_by_size(types, box) -> tuple[Optional[str], bool]:
    """The first type whose real size holds the box (either orientation, +15 %), else the first type."""
    from wenart.furniture import sizes as SZ
    if not types:
        return None, False
    if box:
        for t in types:
            if SZ.fits(t, box, 0.15):
                return t, True
    return types[0], False


def polyhaven_candidates(assets: dict, used_ids: set, files_of: Optional[Callable[[str], Optional[dict]]] = None,
                         res: str = "2k") -> list[dict]:
    """The unused Poly Haven models of our types (pure but for ``files_of``, which gives ``/files/<id>``): the type
    from the category path (``PH_CATEGORY_TYPES``, the first that fits the API dimensions), outdoor and low-poly
    words left out."""
    used = {u.lower() for u in used_ids}
    known = known_types()
    out = []
    for aid in sorted(assets):
        a = assets[aid]
        if aid.lower() in used or int(a.get("type", 2)) != 2:
            continue
        name, tags = str(a.get("name") or aid), " ".join(str(t) for t in a.get("tags") or [])
        dims = [round(float(v) / 1000.0, 3) for v in a.get("dimensions") or []]
        box = dims if len(dims) == 3 else None          # x, y, z (up) of the model, metres
        ftype, fits = pick_by_size([t for t in ph_types(a.get("category")) if t in known], box)
        if ftype is None:
            continue
        fl = K.flags(" ".join([name, tags]))
        if fl.get("outdoor") or fl.get("crude"):
            continue
        rec = {"source": "polyhaven", "id": aid, "title": name, "type": ftype, "kind": known[ftype],
               "licence": "CC0", "category": a.get("category"), "styles_hint": styles_from_text(name + " " + tags),
               "dims_m": dims or None, "fits_real_size": fits, "polycount": a.get("polycount"),
               "url": f"https://polyhaven.com/a/{aid}"}
        rec["size_mb"] = ph_size_mb(files_of(aid) if files_of else None, res)
        out.append(rec)
    out.sort(key=lambda r: (r["kind"], r["type"], r["id"]))
    return out


# --------------------------------------------------------------------------
# ABO
# --------------------------------------------------------------------------

def abo_family(style: Optional[str]) -> Optional[str]:
    fams = [f for f in styles_from_text(style or "") if f in ABO_FAMILIES]
    return fams[0] if fams else None


def abo_candidates(models: dict, listings: list[dict], glb_sizes: dict, used_models: set, *, per_type_family: int = 8,
                   decor_per_type: int = 40, headboards: int = 30) -> list[dict]:
    """The ABO style pass, decor pass and headboards (module docstring); ``pick`` marks the capped selection."""
    from wenart.assets import abo as AB
    from wenart.assets import objaverse as OV
    cfg, ocfg = AB.load_config(), OV.load_config()
    table, tol = OV.library_size_table(ocfg)
    known = known_types()
    tags = list((cfg.get("survey") or {}).get("english_tags") or ["en_US", "en_GB"])
    seen: set = set()
    out = []
    for lst in sorted(listings, key=lambda r: (str(r.get("3dmodel_id")), str(r.get("item_id")))):
        mid = str(lst.get("3dmodel_id"))
        if mid in seen or mid in used_models or mid not in models or models[mid].get("bad"):
            continue
        name, _ = AB.english(lst.get("item_name"), tags)
        style, _ = AB.english(lst.get("style"), tags)
        ptype = AB.product_type(lst)
        row = models[mid]
        dims = AB.zup_extents(row["extents"])
        rule = AB.match_rule(ptype, name, float(row["extents"][1]), cfg.get("rules") or [])
        ftype = None
        if rule is not None:
            ftype, _code, _detail = AB.resolve_type(rule, dims, ocfg, table, tol)
        if ftype is None and name and "headboard" in K.tokens(name):
            ftype = "headboard"
        if ftype is None or (ftype not in known and ftype != "headboard"):
            continue
        seen.add(mid)
        fam = abo_family(style)
        kind = known.get(ftype, "furniture")
        if ftype == "headboard":
            group = "headboards"
        elif kind == "decor" and ftype in ("cushion", "rug", "wall_art"):
            group = "decor pass"
        elif kind == "furniture" and fam:
            group = "style pass"
        else:
            continue
        path = row.get("path")
        size = glb_sizes.get(f"3dmodels/original/{path}")
        out.append({"source": "abo", "id": f"abo_{mid}", "item_id": lst.get("item_id"), "title": name or "",
                    "type": ftype, "kind": kind, "group": group, "family": fam, "style": style,
                    "product_type": ptype, "licence": "CC-BY-4.0", "dims_m": [round(float(v), 3) for v in dims],
                    "image_px": row.get("image_width_max"), "glb": path,
                    "size_mb": round(size / 1e6, 2) if size else None,
                    "variant": AB.variant_key(AB.english(lst.get("brand"), tags)[0]
                                              or AB.any_value(lst.get("brand"))[0], name)})
    # picks: per (type, family) for the style pass, per type for the decor pass, headboards; colour variants last,
    # larger textures first, then the id (deterministic)
    out.sort(key=lambda r: (r["group"], r["type"], r["family"] or "", r["id"]))
    counts: dict = {}
    variants: set = set()
    for r in sorted(out, key=lambda r: (r["group"], r["type"], r["family"] or "", -(r["image_px"] or 0), r["id"])):
        key = (r["group"], r["type"], r["family"] if r["group"] == "style pass" else None)
        cap = {"style pass": per_type_family, "decor pass": decor_per_type, "headboards": headboards}[r["group"]]
        vkey = (r["type"], r["variant"])
        if counts.get(key, 0) >= cap or (r["variant"] and vkey in variants):
            r["pick"] = False
            continue
        counts[key] = counts.get(key, 0) + 1
        if r["variant"]:
            variants.add(vkey)
        r["pick"] = True
    return out


# --------------------------------------------------------------------------
# GSO
# --------------------------------------------------------------------------

GSO_FAMILIES = {"bowl": "bowl", "pot": "plant_small", "vase": "vase", "basket": "basket", "tray": "tray",
                "candle": "candle", "books": "books", "kitchenware": None, "towel": None}


# Words of GSO archive names that are no decor of ours (bins, electric pots, shoes named "cup", pet items).
GSO_NOT = {"waste", "trash", "electric", "shoe", "shoes", "boot", "sneaker", "venetian", "slipper", "sandal", "pet",
           "dog", "cat", "toy"}


def gso_candidates(files: list[dict], per_type: int = 20) -> list[dict]:
    """Small decor of the GSO mirror's object archives (``[{"rfilename", "size"}]``), ``pick`` <= ``per_type``."""
    out = []
    for f in sorted(files, key=lambda f: str(f.get("rfilename"))):
        name = str(f.get("rfilename") or "")
        if not name.endswith(".zip"):
            continue
        title = name[:-4].replace("_", " ")
        if K.flags(title).get("crude") or set(K.tokens(title)) & GSO_NOT:
            continue
        fams = [x["family"] for x in K.named_families(title) if x["family"] in GSO_FAMILIES]
        if not fams:
            continue
        fam = fams[0]
        size = (f.get("lfs") or {}).get("size") or f.get("size")
        out.append({"source": "gso", "id": f"gso_{name[:-4]}", "title": title, "family": fam,
                    "type": GSO_FAMILIES[fam], "kind": "decor", "licence": "CC-BY-4.0",
                    "licence_note": "Google Scanned Objects (CC BY 4.0, Google LLC); the mirror carries no licence "
                                    "tag: check the object on the GSO page before the ingest",
                    "file": name, "size_mb": round(int(size) / 1e6, 2) if size else None})
    counts: dict = {}
    for r in out:
        key = r["type"] or r["family"]
        r["pick"] = r["type"] is not None and counts.get(key, 0) < per_type
        if r["pick"]:
            counts[key] = counts.get(key, 0) + 1
    out.sort(key=lambda r: (r["type"] or "~" + r["family"], r["id"]))
    return out


# --------------------------------------------------------------------------
# Infinigen
# --------------------------------------------------------------------------

def infinigen_plan() -> dict:
    """The test batch of procedural fixtures (docs/milestone12.md §6.4, step 3 of the growth order)."""
    wanted = [("toilet", "toilet"), ("bathtub", "bathtub"), ("bathroom sink", "washbasin"),
              ("kitchen sink", "sink_kitchen"), ("oven", "stove"), ("beverage fridge", "fridge"),
              ("dishwasher", None), ("microwave", None), ("kitchen cabinet", None), ("books", "books"),
              ("bowl", "bowl"), ("pot", "plant_small")]
    return {
        "kind": "library_growth_plan", "source": "infinigen", "repo": "princeton-vl/infinigen",
        "licence": "BSD-3-Clause (LICENSE read 10 Oct 2026: Copyright (c) 2023, Princeton University)",
        "environment": {"python": "3.11 (pyproject.toml requires-python ==3.11.*)", "bpy": "4.2.0 (pyproject.toml)",
                        "venv": "/opt/wenart/venv-infinigen (container disk; never the volume)",
                        "note": "the factory module paths moved on main (version attribute infinigen2.__version__): "
                                "the pod pins a commit and lists the factories it finds before generating"},
        "batch": [{"factory": f, "type": t, "count": 3 if t else 1, "seeds": [0, 1, 2] if t else [0],
                   "note": "" if t else "no type of ours: generated once to see it"} for f, t in wanted],
        "steps": ["clone at a pinned commit, record it", "venv with Python 3.11 and bpy 4.2.0",
                  "list the asset factories of the commit (python -c ...); match the wanted names; stop when one is "
                  "missing", "generate count x seeds per factory, export GLB at real scale (metres, Z up)",
                  "python -m wenart.assets audit render / code / ask on the new GLBs; the user sees the sheets"],
        "estimate_min": 40, "pod": "P4 (after the user's OK of this plan)", "downloads_mb": "about 1,500 (repo, "
        "venv, bpy wheel); no model files"}


# --------------------------------------------------------------------------
# Network (metadata only) with a cache
# --------------------------------------------------------------------------

def cache_dir(value: Optional[str] = None) -> Path:
    return Path(value or os.environ.get("WENART_GROWTH_CACHE") or "~/.cache/wenart/growth").expanduser()


def fetch(url: str, cache: Path, name: str, timeout: float = 60.0) -> bytes:
    path = Path(cache) / name
    if path.is_file():
        return path.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def s3_sizes(base: str, prefix: str, cache: Path) -> dict:
    """``{key: bytes}`` of a public S3 bucket prefix (ListObjectsV2 pages, cached)."""
    out, token, page = {}, None, 0
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    while True:
        q = {"list-type": "2", "prefix": prefix}
        if token:
            q["continuation-token"] = token
        data = fetch(base + "/?" + urllib.parse.urlencode(q), cache, f"s3_{prefix.replace('/', '_')}{page}.xml")
        root = ET.fromstring(data)
        for c in root.findall("s3:Contents", ns):
            out[c.find("s3:Key", ns).text] = int(c.find("s3:Size", ns).text)
        token_el = root.find("s3:NextContinuationToken", ns)
        if token_el is None or not token_el.text:
            break
        token, page = token_el.text, page + 1
    return out


# --------------------------------------------------------------------------
# Lists, approval gate, ingest
# --------------------------------------------------------------------------

def list_doc(source: str, cands: list[dict], queried_utc: str, query: dict, notes: list[str]) -> dict:
    picks = [c for c in cands if c.get("pick", True)]
    by_type: dict = {}
    for c in picks:
        k = c.get("type") or f"({c.get('family')})"
        by_type[k] = by_type.get(k, 0) + 1
    return {"kind": "library_growth_candidates", "source": source, "queried_utc": queried_utc, "query": query,
            "licences": sorted({c["licence"] for c in cands}), "count": len(cands), "picked": len(picks),
            "picked_size_mb": round(sum(c.get("size_mb") or 0 for c in picks), 1),
            "picked_by_type": dict(sorted(by_type.items())), "notes": notes,
            "approval": f"nothing is downloaded before results/library/growth/approved_{source}.json exists (the "
                        "lead commits it after the user's OK: approved_by, approved_utc, ids)",
            "candidates": cands}


def approved(source: str, out=None) -> dict:
    """The approved list of a source; ``PermissionError`` when it is missing or incomplete (the ingest gate)."""
    path = growth_dir(out) / f"approved_{source}.json"
    if not path.is_file():
        raise PermissionError(f"{path} not found: the user has not approved a {source} list (D24); nothing is "
                              "downloaded")
    doc = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ("approved_by", "approved_utc", "ids") if not doc.get(k)]
    if missing or doc.get("source", source) != source:
        raise PermissionError(f"{path}: missing {', '.join(missing) or 'the right source'}: not an approval")
    return doc


def cmd_list(args) -> int:
    out = growth_dir(args.out)
    cache = cache_dir(args.cache)
    stamp = args.queried_utc or now_utc()
    if args.source == "infinigen":
        doc = dict(infinigen_plan(), written_utc=stamp)
        path = out / "plan_infinigen.json"
    elif args.source == "polyhaven":
        assets = json.loads(fetch(f"{PH_API}/assets?t=models", cache, "ph_assets_models.json"))
        from wenart.furniture import catalog as C
        cat = C.load(library=False)
        used = {e["id"] for e in cat.data.get("entries", []) + cat.data.get("decor", []) if e.get("id")}

        def files_of(aid):
            return json.loads(fetch(f"{PH_API}/files/{aid}", cache, f"ph_files_{aid}.json"))
        cands = polyhaven_candidates(assets, used, files_of)
        doc = list_doc("polyhaven", cands, stamp, {"api": f"{PH_API}/assets?t=models", "files": f"{PH_API}/files/<id>",
                                                   "resolution": "2k glTF"},
                       [f"{len(assets)} Poly Haven models; {len(used)} ids already in catalog.json",
                        "type from the category path (growth.PH_CATEGORY_TYPES: the first type whose real size holds "
                        "the API dimensions); outdoor and low-poly words left out; fits_real_size false: no type of "
                        "the category holds the dimensions (the audit decides)"])
        path = out / "candidates_polyhaven.json"
    elif args.source == "abo":
        from wenart.assets import abo as AB
        cfg = AB.load_config()
        names = AB.metadata_names(cfg)
        base = cfg["dataset"]["base_url"]
        files = {k: fetch(f"{base}/{v}", cache, "abo_" + v.replace("/", "_")) for k, v in names.items()
                 if k != "readme"}
        tmp = cache / "abo_parsed"
        tmp.mkdir(parents=True, exist_ok=True)
        for k, data in files.items():
            (tmp / f"{k}.gz").write_bytes(data)
        models = AB.read_models_csv(tmp / "csv.gz")
        listings = AB.read_listings(sorted(tmp.glob("listings_*.gz")))
        sizes = s3_sizes(base, "3dmodels/original/", cache)
        from wenart.assets.audit import items as I
        used = {str(i.get("abo_3dmodel_id") or i["id"][4:]) for i in I.load_items()
                if i.get("source") == "abo"}
        cat = I.read_json(I.LIBRARY_PATH) or {}
        used |= {str(e.get("abo_3dmodel_id")) for s in ("entries", "decor") for e in cat.get(s) or []
                 if e.get("abo_3dmodel_id")}
        found = abo_candidates(models, listings, sizes, used)
        cands = [c for c in found if c["pick"]]
        skipped: dict = {}
        for c in found:
            if not c["pick"]:
                key = f"{c['group']}: {c['type']}" + (f" ({c['family']})" if c["family"] else "")
                skipped[key] = skipped.get(key, 0) + 1
        doc = list_doc("abo", cands, stamp, {"bucket": base, "metadata": sorted(names.values()),
                                             "sizes": "ListObjectsV2 3dmodels/original/"},
                       [f"{len(models)} models, {len(listings)} listings with a model; {len(used)} already used",
                        "style pass: furniture of our types whose English listing style says rustic / farmhouse, "
                        "industrial or classic / traditional (<= 8 per type and family); decor pass: pillows, rugs, "
                        "wall art (<= 40 per type); headboards (<= 30; no type of ours yet: bed frames)",
                        "colour variants of one product are picked once",
                        f"{len(found)} candidates found, {len(cands)} picked (listed below); not picked per group: "
                        + json.dumps(dict(sorted(skipped.items())))])
        path = out / "candidates_abo.json"
    else:
        meta = json.loads(fetch(f"{HF_API}{GSO_REPO}?blobs=true", cache, "gso_raw.json"))
        cands = gso_candidates(meta.get("siblings") or [])
        doc = list_doc("gso", cands, stamp, {"repo": GSO_REPO, "revision": meta.get("sha")},
                       ["object archives named after the product; small decor of our decor types picked (<= 20 per "
                        "type); mugs and towels listed without a type"])
        path = out / "candidates_gso.json"
    out.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if "candidates" in doc:
        print(f"growth {args.source}: {doc['count']} candidate(s), {doc['picked']} picked, "
              f"{doc['picked_size_mb']} MB -> {path}")
    else:
        print(f"growth {args.source}: plan -> {path}")
    return EXIT_OK


def cmd_ingest(args) -> int:
    try:
        doc = approved(args.source, args.out)
    except PermissionError as exc:
        print(f"growth {args.source} ingest refused: {exc}")
        return EXIT_NOTHING
    ids = list(doc["ids"])
    if args.source == "polyhaven":
        from wenart.assets import models as M
        for aid in ids:
            M.fetch_model(aid, Path(args.assets), size="2k")
            print(f"growth polyhaven: {aid} -> {args.assets}")
        return EXIT_OK
    if args.source == "abo":
        from wenart.assets import abo as AB
        cand = json.loads((growth_dir(args.out) / "candidates_abo.json").read_text(encoding="utf-8"))
        by_id = {c["id"]: c for c in cand["candidates"]}
        cfg = AB.load_config()
        for cid in ids:
            c = by_id[cid]
            dest = Path(args.cache_glb) / "original" / c["glb"]
            AB.download(f"{cfg['dataset']['base_url']}/3dmodels/original/{c['glb']}", dest, max_bytes=80e6)
            print(f"growth abo: {cid} -> {dest}")
        return EXIT_OK
    print(f"growth {args.source} ingest: approved ({len(ids)} id(s)); the {args.source} ingest is pod P4 work "
          "(not built in this step)")
    return EXIT_NOTHING


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m wenart.assets growth", description="library growth lists (D24)")
    p.add_argument("source", choices=SOURCES)
    p.add_argument("action", choices=["list", "plan", "ingest"])
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--cache", default=None, help="metadata cache (default ~/.cache/wenart/growth)")
    p.add_argument("--queried-utc", default=None)
    p.add_argument("--assets", default="/workspace/assets", help="ingest: assets folder (Poly Haven)")
    p.add_argument("--cache-glb", default="/workspace/prep/cache/abo", help="ingest: ABO GLB cache")
    args = p.parse_args(argv)
    if args.action == "ingest":
        return cmd_ingest(args)
    return cmd_list(args)


if __name__ == "__main__":
    sys.exit(main())
