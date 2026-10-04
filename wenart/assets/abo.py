"""Amazon Berkeley Objects (ABO) as a furniture library source: the survey (docs/milestone8.md §1, §2).

What: ABO (https://amazon-berkeley-objects.s3.amazonaws.com/index.html, CC BY 4.0, credit "Amazon.com") has 7,953
glTF models of real products with PBR textures and real sizes in metres. ``survey`` picks the candidates of our
furniture and decor types and downloads their GLBs; the shared library steps of ``wenart/assets/objaverse.py``
(thumbnails, judging, acceptance, catalogue, report) then read ``survey_abo.json`` next to the other sources' survey
files. Nothing here runs in the session except on canned metadata (tests) or with ``--no-download``.

    python -m wenart.assets.abo survey --out DIR [--cache /opt/wenart/abo] [--metadata DIR] [--no-download]
        [--workers N] [--config abo.yaml]

1. Metadata: ``3dmodels/metadata/3dmodels.csv.gz``, the 16 listings shards ``listings/metadata/listings_<s>.json.gz``
   and ``3dmodels/README.md``, read from ``--metadata DIR`` (the files side by side) or from ``<cache>/metadata/``,
   where missing files are downloaded first (cached; never with ``--no-download``). Every file's sha256 is recorded;
   the README must state the CC BY 4.0 licence and the Amazon.com credit (``readme_checked``; a README that does not
   is recorded and warned about, the licence of ``abo.yaml`` was verified from the session).
2. Listings with a ``3dmodel_id``, one per model (deduplicated by ``3dmodel_id``: the listing with an English name,
   then the lowest item id), mapped to a type by the first matching rule of ``abo.yaml`` (product type, English
   ``item_name`` words, height; the rule's types in order, the first whose size range holds the box; beds split by
   the width). Models outside every listed type's range are refused ``size_range`` (units are known: never
   normalised); product types no rule takes are counted (``unmapped_product_types``).
3. Pick order per type: round robin over the English ``style`` values, colour variants of one product last, larger
   textures first (``pick_order``); downloads in that order (``<cache>/original/<path>``, at most 60 MB, a readable
   GLB 2.0 with an image texture or vertex colours) until 24 pass; ``--no-download`` lists the first 24 without files.
4. ``<out>/survey_abo.json``: the candidates in the shared record shape (``uid`` ``abo_<3dmodel_id>``, ``group``,
   ``types``, ``categories`` (the product type), ``title`` (the item name), ``author`` "Amazon.com", ``source_url``
   (the ABO index page and the item id), ``licence`` CC-BY-4.0, ``licence_raw``, ``licence_flag`` null,
   ``face_count``, ``glb``, ``glb_sha256``, ``glb_bytes``, ``glb_info``, ``rank``) plus ``source`` abo,
   ``style_hint`` (the English style text), ``kind``, ``decor_type``, ``units_known`` true, ``extents_raw`` (the csv
   extents in the importer's Z-up frame: x, z, y of the csv), ``front_documented`` -Y (README convention 2: glTF +Z
   is the product's natural front) and the credit line ``attribution`` (docs/milestone8.md §2), the counts per type
   and every refusal with its reason.

Exit codes: 0 candidates found, 1 none, 2 usage error or metadata missing.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

from wenart.assets import objaverse as OV

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "abo.yaml"
SOURCE = "abo"
SURVEY_NAME = OV.SURVEY_FILES[SOURCE]                      # survey_abo.json
UID_PREFIX = "abo_"
DEFAULT_CACHE = Path("/opt/wenart/abo")                    # container disk (CLAUDE.md: never the volume for caches)
USER_AGENT = "wenart-run/0.1 (ABO furniture library survey)"
TIMEOUT_S = 120
EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2
_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,56}")                # 3dmodel ids (uid = abo_<id> fits objaverse._UID_RE)
_PATH_RE = re.compile(r"[A-Za-z0-9]/[A-Za-z0-9_-]+\.glb")  # csv paths: <one char>/<3dmodel_id>.glb

REASONS: dict[str, str] = {
    "no_model_row": "3dmodel_id not in 3dmodels.csv.gz",
    "bad_model_row": "3dmodels.csv.gz row with a bad id, path or extent",
    "size_range": "box outside the size range of every type of its rule (units known: never normalised)",
    "glb_size": "GLB larger than 60 MB",
    "download_failed": "download failed",
    "glb_unreadable": "GLB header unreadable",
    "untextured": "no image texture and no vertex colours",
}


class UsageError(ValueError):
    """Missing metadata or a wrong argument: the CLI prints it and exits 2."""


class TooLarge(RuntimeError):
    """A download went over the byte limit."""


def load_config(path: Optional[Path] = None) -> dict:
    """``abo.yaml`` as a dict."""
    import yaml
    return yaml.safe_load(Path(CONFIG_PATH if path is None else path).read_text(encoding="utf-8")) or {}


# --------------------------------------------------------------------------
# Credits
# --------------------------------------------------------------------------

def notice(cfg: Optional[dict] = None) -> str:
    """The ABO credit of every library output that holds ABO models (README: credit for the data and the dataset)."""
    ds = (cfg or load_config())["dataset"]
    return (f"Contains 3D models and product data from {ds['name']} ({ds['index_url']}), (c) {ds['credit_data']}, "
            f"licensed CC BY 4.0 ({ds['licence_url']}). Credit for the data, including all images and 3D models: "
            f"{ds['credit_data']}; for building the dataset: {' '.join(str(ds['credit_dataset']).split())}. Changes: "
            f"{ds['changes']}.")


def source_url(item_id: str, cfg: dict) -> str:
    """The ABO index page and the item id (docs/milestone8.md §2)."""
    return f"{cfg['dataset']['index_url']}#{item_id}"


def attribution(title: str, cfg: dict) -> str:
    """The credit line of docs/milestone8.md §2, ``"<item name>" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0),
    https://amazon-berkeley-objects.s3.amazonaws.com/index.html``, plus the changes CC BY 4.0 asks for."""
    ds = cfg["dataset"]
    return ds["attribution"].format(title=title, index_url=ds["index_url"]) + f"; changes: {ds['changes']}"


# --------------------------------------------------------------------------
# Metadata files
# --------------------------------------------------------------------------

def metadata_names(cfg: dict) -> dict:
    """``{key: bucket path}`` of the metadata files: ``csv``, ``readme`` and ``listings_<s>`` per shard."""
    ds = cfg["dataset"]
    names = {"csv": ds["csv"], "readme": ds["readme"]}
    for shard in str(ds["shards"]):
        names[f"listings_{shard}"] = ds["listings"].format(shard=shard)
    return names


def download(url: str, dest: Path, max_bytes: Optional[float] = None, timeout: float = TIMEOUT_S) -> Path:
    """Stream ``url`` into ``dest`` (via ``.part``); ``TooLarge`` past ``max_bytes`` (the part file is removed)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    got = 0
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp, part.open("wb") as fh:
            length = resp.headers.get("Content-Length")
            if max_bytes is not None and length and length.isdigit() and int(length) > max_bytes:
                raise TooLarge(f"{int(length) / 1048576:.1f} MB (Content-Length)")
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                got += len(chunk)
                if max_bytes is not None and got > max_bytes:
                    raise TooLarge(f"over {max_bytes / 1048576:.0f} MB")
                fh.write(chunk)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    part.replace(dest)
    return dest


class Metadata:
    """The metadata files: ``--metadata DIR`` (side by side, read only) or ``<cache>/metadata`` (downloaded when
    missing, unless ``download`` is False). ``fetcher(url, dest)`` replaces the download (tests)."""

    def __init__(self, cfg: dict, metadata_dir: Optional[Path] = None, cache: Optional[Path] = None,
                 download_missing: bool = True, fetcher: Optional[Callable] = None):
        self.cfg = cfg
        self.local = Path(metadata_dir) if metadata_dir else None
        self.folder = self.local or (Path(cache or DEFAULT_CACHE) / "metadata")
        self.download_missing = download_missing and self.local is None
        self.fetcher = fetcher or (lambda url, dest: download(url, dest))

    def path(self, rel: str) -> Path:
        p = self.folder / Path(rel).name
        if p.is_file():
            return p
        if not self.download_missing:
            raise UsageError(f"{Path(rel).name} is not in {self.folder} (metadata missing; no download)")
        url = f"{self.cfg['dataset']['base_url']}/{rel}"
        return Path(self.fetcher(url, p))

    def describe(self) -> str:
        return f"{self.folder}" + (" (local copy)" if self.local else " (cache, downloaded when missing)")


def read_models_csv(path: Path) -> dict:
    """``{3dmodel_id: row}`` of ``3dmodels.csv.gz`` (numbers converted; a bad row keeps ``bad`` with the reason)."""
    rows = {}
    with gzip.open(Path(path), "rt", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            mid = str(row.get("3dmodel_id") or "")
            rec = dict(row)
            try:
                for key in ("meshes", "materials", "textures", "images", "image_height_max", "image_width_max",
                            "vertices", "faces"):
                    rec[key] = int(float(row.get(key) or 0))
                rec["extents"] = [float(row["extent_x"]), float(row["extent_y"]), float(row["extent_z"])]
                if not _ID_RE.fullmatch(mid) or not _PATH_RE.fullmatch(str(row.get("path") or "")):
                    rec["bad"] = f"id {mid!r} / path {row.get('path')!r}"
                elif not all(v > 0 for v in rec["extents"]):
                    rec["bad"] = f"extents {rec['extents']}"
            except (TypeError, ValueError, KeyError) as exc:
                rec["bad"] = f"{type(exc).__name__}: {exc}"
            rows[mid] = rec
    return rows


def read_listings(paths: list[Path]) -> list[dict]:
    """The listings (one JSON object per line) of every shard that carry a ``3dmodel_id``."""
    out = []
    for path in paths:
        with gzip.open(Path(path), "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if isinstance(rec, dict) and rec.get("3dmodel_id"):
                    out.append(rec)
    return out


def file_info(path: Path) -> dict:
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {"sha256": digest, "bytes": Path(path).stat().st_size}


def readme_checked(text: str, cfg: dict) -> bool:
    """The README states the CC BY 4.0 licence and the credit "Amazon.com" (as abo.yaml records them)."""
    flat = " ".join(text.split())
    return "Creative Commons Attribution 4.0" in flat and cfg["dataset"]["credit_data"] in flat


# --------------------------------------------------------------------------
# Listing fields and the mapping
# --------------------------------------------------------------------------

def english(values, tags) -> tuple[Optional[str], Optional[str]]:
    """``(value, language tag)`` of the first value whose ``language_tag`` is in ``tags`` (in that order), else of
    any ``en_*`` one; ``(None, None)`` without an English value."""
    vals = [v for v in values or [] if isinstance(v, dict) and isinstance(v.get("value"), str) and v["value"].strip()]
    for tag in tags:
        for v in vals:
            if v.get("language_tag") == tag:
                return " ".join(v["value"].split()), tag
    for v in vals:
        if str(v.get("language_tag") or "").startswith("en"):
            return " ".join(v["value"].split()), v["language_tag"]
    return None, None


def any_value(values) -> tuple[Optional[str], Optional[str]]:
    for v in values or []:
        if isinstance(v, dict) and isinstance(v.get("value"), str) and v["value"].strip():
            return " ".join(v["value"].split()), v.get("language_tag")
    return None, None


def product_type(listing: dict) -> Optional[str]:
    values = listing.get("product_type") or []
    for v in values:
        if isinstance(v, dict) and v.get("value"):
            return str(v["value"])
    return None


def word_hit(words, text: str) -> bool:
    """True when ``text`` holds one of ``words`` as whole words (case-insensitive; a plural s / es allowed)."""
    low = text.casefold()
    return any(re.search(r"\b" + re.escape(str(w).casefold()) + r"(?:s|es)?\b", low) for w in words or ())


def match_rule(ptype: Optional[str], name_en: Optional[str], height: float, rules: list[dict]) -> Optional[dict]:
    """The first rule of ``abo.yaml`` that takes a listing (module docstring, step 2); None when none does."""
    for rule in rules:
        if ptype not in (rule.get("product_types") or []):
            continue
        if rule.get("words") and not (name_en and word_hit(rule["words"], name_en)):
            continue
        if rule.get("not_words") and name_en and word_hit(rule["not_words"], name_en):
            continue
        if rule.get("min_height") is not None and height < float(rule["min_height"]):
            continue
        return rule
    return None


def zup_extents(csv_extents) -> list[float]:
    """The csv extents (glTF: x, y up, z front) in the importer's Z-up frame: (x, z, y)."""
    x, y, z = (float(v) for v in csv_extents)
    return [x, z, y]


def resolve_type(rule: dict, dims, ocfg: dict, table: dict, tol: float) -> tuple[Optional[str], str, str]:
    """``(type | None, named type, detail)``: the first of the rule's types whose size range (footprint + tolerance,
    height range) holds ``dims`` (metres, Z up); ``bed`` is bed_single / bed_double by the width (the shorter
    footprint side) at objaverse.yaml ``bed_split_width_m``."""
    heights = OV.heights_of(ocfg)
    tried = []
    for t in rule["types"]:
        if t == "bed":
            width = min(dims[0], dims[1])
            split = float(ocfg["bed_split_width_m"])
            t = "bed_single" if width <= split else "bed_double"
        tried.append(t)
        if OV.fits_type(dims, t, table, tol, heights):
            return t, tried[0], f"{OV._fmt_dims(dims)} m in the {t} range"
    return None, tried[0], (f"{OV._fmt_dims(dims)} m (x, y, height) is outside the range of "
                            f"{' and '.join(tried)}")


def variant_key(brand: Optional[str], name: Optional[str]) -> str:
    """One product's key across its colour variants: the brand and the item name without its last comma-separated
    part (``"..., 66"W, Spinnsol Cocoa"`` -> ``"..., 66"W"``) and without an "Amazon Brand –" prefix."""
    text = " ".join(str(name or "").casefold().split())
    text = re.sub(r"^amazon brand\s*[-–]\s*", "", text)
    parts = [p.strip() for p in text.split(",")]
    stem = ", ".join(parts[:-1]) if len(parts) > 1 else text
    return f"{str(brand or '').casefold().strip()}|{stem}"


def style_key(style: Optional[str]) -> str:
    return " ".join(str(style or "").casefold().split())


def pick_order(pool: list[dict]) -> list[dict]:
    """The pick order of one type (abo.yaml survey): round robin over the style groups (largest first, then by
    name; no style is a group of its own); inside a group the colour variants of one product after the other
    products, then the larger texture, then the id."""
    groups: dict[str, list[dict]] = {}
    for rec in pool:
        groups.setdefault(style_key(rec.get("style_hint")), []).append(rec)
    ordered = []
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        items = sorted(groups[key], key=lambda r: (-(r.get("texture_px") or 0), r["abo_3dmodel_id"]))
        seen: dict[str, int] = {}
        for r in items:
            r["_variant"] = seen.get(r["_vkey"], 0)
            seen[r["_vkey"]] = r["_variant"] + 1
        ordered.append(sorted(items, key=lambda r: (r["_variant"], -(r.get("texture_px") or 0),
                                                    r["abo_3dmodel_id"])))
    out = []
    n = 0
    while any(n < len(g) for g in ordered):
        for g in ordered:
            if n < len(g):
                out.append(g[n])
        n += 1
    return out


# --------------------------------------------------------------------------
# The survey
# --------------------------------------------------------------------------

def _refusal(rec: dict, code: str, detail: str = "") -> dict:
    return {"uid": rec.get("uid"), "abo_3dmodel_id": rec.get("abo_3dmodel_id"), "item_id": rec.get("item_id"),
            "group": rec.get("group"), "code": code, "detail": detail, "source": SOURCE}


def fetch_glb(rec: dict, cache: Path, cfg: dict, max_bytes: float, fetcher: Optional[Callable] = None
              ) -> Optional[tuple[str, str]]:
    """Download one candidate's GLB into ``<cache>/original/<path>`` (a file already there is reused) and run the
    file checks; fills ``glb``, ``glb_sha256``, ``glb_bytes``, ``glb_info`` or returns ``(code, detail)``.
    ``fetcher(url, dest, max_bytes)`` replaces ``download`` (tests)."""
    ds = cfg["dataset"]
    dest = Path(cache) / "original" / rec["abo_path"]
    url = f"{ds['base_url']}/{ds['glb'].format(path=rec['abo_path'])}"
    if not dest.is_file():
        try:
            (fetcher or download)(url, dest, max_bytes)
        except TooLarge as exc:
            return "glb_size", str(exc)
        except (urllib.error.URLError, OSError, ValueError, RuntimeError) as exc:
            return "download_failed", f"{type(exc).__name__}: {exc}"
    size = dest.stat().st_size
    if size > max_bytes:
        return "glb_size", f"{size / 1048576:.1f} MB (file)"
    try:
        info = OV.glb_info(dest)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        return "glb_unreadable", str(exc)
    if not (info["textured"] or info["vertex_colours"]):
        return "untextured", f"{info['images']} images, {info['textures']} textures, no COLOR_0"
    rec.update({"glb": str(dest), "glb_sha256": OV.sha256_file(dest), "glb_bytes": size, "glb_info": info})
    return None


def survey(meta: Metadata, out: Path, cfg: Optional[dict] = None, ocfg: Optional[dict] = None,
           download_glbs: bool = True, cache: Optional[Path] = None, fetcher: Optional[Callable] = None,
           workers: Optional[int] = None, log: Callable = print) -> dict:
    """The ABO survey (module docstring) -> ``<out>/survey_abo.json``."""
    cfg = cfg or load_config()
    ocfg = ocfg or OV.load_config()
    out = Path(out)
    cache = Path(cache) if cache else DEFAULT_CACHE
    scfg, ds = cfg["survey"], cfg["dataset"]
    tags = list(scfg.get("english_tags") or ["en_US", "en_GB"])
    names = metadata_names(cfg)
    files = {key: meta.path(rel) for key, rel in names.items()}
    rows = read_models_csv(files["csv"])
    listings = read_listings([files[k] for k in names if k.startswith("listings_")])
    readme_ok = readme_checked(Path(files["readme"]).read_text(encoding="utf-8", errors="replace"), cfg)
    if not readme_ok:
        log("abo survey: WARNING: README.md does not state CC BY 4.0 and the Amazon.com credit as abo.yaml records")
    log(f"abo survey: {len(rows)} models in the csv, {len(listings)} listings with a 3D model ({meta.describe()})")

    by_model: dict[str, list[dict]] = {}
    for rec in listings:
        by_model.setdefault(str(rec["3dmodel_id"]), []).append(rec)
    table, tol = OV.library_size_table(ocfg)
    rules = cfg["rules"]
    counts: dict[str, dict] = {}
    unmapped: dict[str, int] = {}
    refused: list[dict] = []
    pools: dict[str, list[dict]] = {}
    stats = {"listings_with_model": len(listings), "models": len(by_model),
             "listed_twice": sum(1 for v in by_model.values() if len(v) > 1), "no_english_name": 0}
    for mid in sorted(by_model):
        group = sorted(by_model[mid], key=lambda r: (english(r.get("item_name"), tags)[0] is None,
                                                     str(r.get("item_id"))))
        listing = group[0]
        ptype = product_type(listing)
        name_en, tag = english(listing.get("item_name"), tags)
        if name_en is None:
            stats["no_english_name"] += 1
        row = rows.get(mid)
        base = {"uid": f"{UID_PREFIX}{mid}", "abo_3dmodel_id": mid, "item_id": listing.get("item_id")}
        if row is None:
            refused.append(_refusal(base, "no_model_row"))
            continue
        if row.get("bad"):
            refused.append(_refusal(base, "bad_model_row", row["bad"]))
            continue
        dims = [round(v, 4) for v in zup_extents(row["extents"])]
        rule = match_rule(ptype, name_en, dims[2], rules)
        if rule is None:
            unmapped[str(ptype)] = unmapped.get(str(ptype), 0) + 1
            continue
        ftype, named, detail = resolve_type(rule, dims, ocfg, table, tol)
        key = ftype or named
        c = counts.setdefault(key, {"mapped": 0, "in_size": 0, "tried": 0, "candidates": 0, "not_selected": 0})
        c["mapped"] += 1
        title = name_en or any_value(listing.get("item_name"))[0] or f"ABO item {listing.get('item_id')}"
        style_en = english(listing.get("style"), tags)[0]
        brand = english(listing.get("brand"), tags)[0] or any_value(listing.get("brand"))[0]
        rec = dict(base, group=key, types=[key], categories=[ptype], product_type=ptype, rule=rule["name"],
                   title=title, name_language=tag, author=ds["credit_data"], source_url=source_url(
                       str(listing.get("item_id")), cfg),
                   licence=ds["licence"], licence_raw="CC BY 4.0 (3dmodels/README.md)", licence_flag=None,
                   licence_url=ds["licence_url"], via=ds["via"], attribution=attribution(title, cfg),
                   face_count=row["faces"], glb_size_meta=None, texture_count=row["textures"],
                   texture_px=row["image_width_max"] * row["image_height_max"], likes=None, views=None,
                   prefer_hit=False, object_path=ds["glb"].format(path=row["path"]), abo_path=row["path"],
                   source=SOURCE, style_hint=style_en, kind="decor" if key in OV.DECOR_TYPES else "furniture",
                   decor_type=key if key in OV.DECOR_TYPES else None, units_known=True, extents_raw=dims,
                   csv_extents=[round(v, 6) for v in row["extents"]], front_documented=ds["front_axis"],
                   front_note=("ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front "
                               f"= {ds['front_axis']} in the importer's Z-up frame"),
                   brand=brand, color=english(listing.get("color"), tags)[0],
                   material=english(listing.get("material"), tags)[0])
        if ftype is None:
            refused.append(_refusal(rec, "size_range", detail))
            continue
        c["in_size"] += 1
        rec["_vkey"] = variant_key(brand, title)
        pools.setdefault(ftype, []).append(rec)

    per_type = int(scfg["per_type_limit"])
    max_dl = int(scfg.get("max_downloads_per_type", 2 * per_type))
    max_bytes = float(scfg["max_glb_mb"]) * 1024 * 1024
    workers = int(workers or scfg.get("workers") or 8)
    candidates: list[dict] = []
    for ftype in sorted(pools):
        order = pick_order(pools[ftype])
        for rank, rec in enumerate(order, 1):
            rec["rank"] = rank
            rec.pop("_vkey", None)
            rec.pop("_variant", None)
        c = counts[ftype]
        chosen: list[dict] = []
        if not download_glbs:
            chosen = order[:per_type]
        else:
            pos = 0
            while len(chosen) < per_type and pos < len(order) and c["tried"] < max_dl:
                batch = order[pos:pos + min(per_type - len(chosen), max_dl - c["tried"])]
                pos += len(batch)
                c["tried"] += len(batch)
                with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
                    problems = list(pool.map(lambda r: fetch_glb(r, cache, cfg, max_bytes, fetcher), batch))
                for rec, problem in zip(batch, problems):
                    if problem is None and len(chosen) < per_type:
                        chosen.append(rec)
                    elif problem is not None:
                        refused.append(_refusal(rec, problem[0], problem[1]))
            chosen.sort(key=lambda r: r["rank"])
        c["candidates"] = len(chosen)
        c["not_selected"] = len(order) - c["tried"] if download_glbs else len(order) - len(chosen)
        candidates += chosen
        log(f"abo survey: {ftype}: {c['mapped']} mapped, {c['in_size']} in the size range, {len(chosen)} candidates")

    refused_counts: dict[str, int] = {}
    for r in refused:
        refused_counts[r["code"]] = refused_counts.get(r["code"], 0) + 1
    doc = {
        "schema_version": OV.SCHEMA_VERSION, "kind": "abo_survey", "source": SOURCE, "generated_utc": OV.now_utc(),
        "dataset": {k: ds[k] for k in ("name", "base_url", "index_url", "licence", "licence_url", "credit_data",
                                       "credit_dataset")},
        "metadata": {"where": meta.describe(), "files": {Path(names[k]).name: file_info(p) for k, p in files.items()},
                     "readme_checked": readme_ok},
        "downloaded": bool(download_glbs), "cache": str(cache), "config_sha256": OV.canonical_sha256(cfg),
        "listings": stats, "unmapped_product_types": dict(sorted(unmapped.items(), key=lambda kv: (-kv[1], kv[0]))),
        "counts": dict(sorted(counts.items())), "refused_counts": dict(sorted(refused_counts.items())),
        "candidates": candidates, "refused": refused,
    }
    OV.write_json(out / SURVEY_NAME, doc)
    return doc


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.assets.abo",
                                     description="ABO furniture library source (docs/milestone8.md §2)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("survey", help="map the ABO listings to types, pick and download the candidates")
    p.add_argument("--out", required=True, help="library folder (the prep job's <prep-root>/library)")
    p.add_argument("--cache", default=str(DEFAULT_CACHE),
                   help=f"metadata and GLB cache (default {DEFAULT_CACHE}, container disk)")
    p.add_argument("--metadata", default=None, help="read the metadata files from this folder (no download)")
    p.add_argument("--no-download", action="store_true", help="no network: list the candidates without GLBs")
    p.add_argument("--workers", type=int, default=None, help="parallel GLB downloads (default abo.yaml)")
    p.add_argument("--config", default=None, help="abo.yaml (default: next to this module)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    t0 = time.time()
    try:
        cfg = load_config(Path(args.config) if args.config else None)
        meta = Metadata(cfg, Path(args.metadata) if args.metadata else None, Path(args.cache),
                        download_missing=not args.no_download)
        doc = survey(meta, Path(args.out), cfg, download_glbs=not args.no_download, cache=Path(args.cache),
                     workers=args.workers)
    except (UsageError, OV.UsageError, FileNotFoundError) as exc:
        print(f"abo {args.command}: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(f"abo survey: {len(doc['candidates'])} candidate(s) in {time.time() - t0:.0f} s -> "
          f"{Path(args.out) / SURVEY_NAME}")
    return EXIT_OK if doc["candidates"] else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
