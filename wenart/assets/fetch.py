"""Download CC0 texture sets and HDRIs into the assets folder with a manifest.

What: ``fetch_texture(asset_id, out_dir, size)`` and ``fetch_hdri(...)`` get
one asset from Poly Haven or ambientCG and record it in
``<out_dir>/manifest.json``; ``fetch_for_style(style, out_dir)`` fetches
everything a ``style.json`` needs plus the furniture texture maps of
``vocabulary.FURNITURE_MATERIALS`` (Milestone 6); ``verify_vocabulary()`` only
lists (no download) and reports whether every id in the vocabulary exists.

Shared interface (both the asset code and the Blender code follow it): a
texture set is ``{"id", "source", "licence": "CC0", "size_m": [w, h],
"files": {"albedo", "normal", "roughness"[, "displacement"]}}`` with paths
relative to the assets dir; the manifest keeps them under ``"textures"``
and HDRIs under ``"hdris": {id: {"file", "licence", "source"}}``. Models
(Milestone 4, ``wenart/assets/models.py``) live under ``"models": {id:
{"files", "sha256", "licence", "bbox_m", ...}}``.

Licence rule: only CC0 is accepted. Neither API carries a per-asset licence
field; the site-wide CC0 statements are recorded in ``LICENCES`` and anything
from another source, with another licence string, or a manifest entry that
is not CC0, is refused with ``LicenceError``.

Milestone 7 (docs/milestone7.md §6.3): the rule is per kind
(``check_licence(..., kind=...)``): textures and HDRIs stay CC0 only, from
the CC0 sources; models may also come from Objaverse with the object's own
licence, CC0 or CC BY 4.0 (``MODEL_SOURCE_LICENCES``; NC, ND, SA and
anything else refused), and a CC BY 4.0 model needs its credit fields
(``CC_BY_FIELDS``). ``load_manifest`` checks every entry against the rule
of its section.

Milestone 8 (docs/milestone8.md §1, §2; user decisions 3 and 4: any licence
for now, recorded and flagged): models may also come from ABO (CC BY 4.0)
and from the generated library (licence ``generated (...)``); an Objaverse
model may carry any licence of ``wenart.furniture.catalog.LICENCE_FLAGS``
(an entry's ``licence_flag``, when given, must be that licence's flag). Every
non-CC0 model of Objaverse or ABO needs its credit fields. Textures and
HDRIs stay CC0 only.

Milestone 10 (docs/milestone10.md §4.3, §4.8, §4.9; track C): the vocabulary also holds ``procedural`` entries
(``source: "procedural"``, ``asset: None``: tiles, wallpaper patterns, slats, a standing-seam roof, flat window-frame
metals). They have nothing to download: every function below skips an entry whose ``asset`` is empty.
``check_assets`` / ``python -m wenart.assets.fetch check`` verify every textured slug of the vocabulary and every HDRI
against the live APIs (id exists, map names, real-world size, download sizes) and may measure the mean colour of the
Poly Haven Diffuse maps; ``wenart/style/asset_checks_m10.json`` is the committed result and ``tests/test_assets.py``
keeps it equal to the vocabulary. Fetching the new ids needs no new code: ``fetch_texture`` already reads any Poly
Haven or ambientCG id (ambientCG downloads need ``acg-download.struffelproductions.com`` on the proxy list).

Idempotent: an asset whose manifest entry and files are present with the
recorded sha256 is returned without any network call.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from wenart.assets import ambientcg, polyhaven, web
from wenart.style import vocabulary as V

MANIFEST_NAME = "manifest.json"
MANIFEST_VERSION = "0.1"
LICENCE = "CC0"
# Source -> licence of everything it serves (checked 2026-10-01):
# https://polyhaven.com/license and the ambientcg.com footer / asset pages ("CC0 1.0 Universal").
LICENCES = {"polyhaven": "CC0", "ambientcg": "CC0"}
LICENCE_URLS = {"polyhaven": "https://polyhaven.com/license", "ambientcg": "https://ambientcg.com/"}
CC_BY = "CC-BY-4.0"
# Model sources whose objects carry their own licence (Milestone 7; Milestone 8 adds ABO, generated models and every
# Objaverse licence, flagged): these licences are taken. Generated models: any licence starting with "generated".
_FLAGS = {"CC0": None, "CC-BY-4.0": None, "CC-BY-NC-4.0": "non_commercial", "CC-BY-NC-SA-4.0": "non_commercial",
          "CC-BY-NC-ND-4.0": "non_commercial", "CC-BY-SA-4.0": "share_alike", "CC-BY-ND-4.0": "no_derivatives",
          "Sketchfab-Editorial": "non_commercial", "Sketchfab-Standard": "unknown",
          "Sketchfab-Free-Standard": "unknown", "unknown": "unknown"}   # = wenart.furniture.catalog.LICENCE_FLAGS
MODEL_SOURCE_LICENCES = {"objaverse": tuple(_FLAGS), "abo": (CC_BY,)}
GENERATED = "generated"                     # model source; its licence starts with this word
# Manifest sections; the licence rule depends on the kind.
KINDS = ("textures", "hdris", "models")
# The credit line of a CC BY 4.0 model (CC BY 4.0 §3(a)(1)): every field must be non-empty.
CC_BY_FIELDS = ("title", "author", "source_url", "licence_url", "via", "attribution")


class LicenceError(RuntimeError):
    """The asset is not CC0 (or comes from a source with no CC0 guarantee)."""


class AssetNotFound(RuntimeError):
    """The source API does not know the asset id."""


# --------------------------------------------------------------------------
# Licence and manifest
# --------------------------------------------------------------------------

def check_licence(source: str, licence: Optional[str] = None, kind: str = "textures",
                  entry: Optional[dict] = None) -> str:
    """Return the licence (``"CC0"``, ``"CC-BY-4.0"``, a flagged licence name or a generated licence) or raise
    ``LicenceError``.

    Every kind: a CC0 source (``LICENCES``) with no licence string or exactly
    ``CC0``. Kind ``models`` only: an Objaverse object whose ``licence`` (required)
    is one of ``MODEL_SOURCE_LICENCES`` (CC0 / CC BY 4.0, or a flagged one: then an
    ``entry`` that has ``licence_flag`` must carry that licence's flag), an ABO object
    (CC BY 4.0) or a generated model (licence ``generated ...``); a non-CC0 Objaverse
    or ABO model with ``entry`` given must carry every ``CC_BY_FIELDS`` field.
    Textures and HDRIs are CC0 only.
    """
    if kind not in KINDS:
        raise ValueError(f"unknown asset kind {kind!r} (expected one of {KINDS})")
    expected = LICENCES.get(source)
    if expected is not None:
        if licence is not None and str(licence).strip().upper() != LICENCE:
            raise LicenceError(f"{source}: licence '{licence}' is not {LICENCE}; refused")
        return expected
    if kind == "models" and source == GENERATED:
        text = str(licence or "").strip()
        if not text.startswith(GENERATED):
            raise LicenceError(f"{source}: licence '{licence}' does not start with '{GENERATED}'; refused")
        return text
    allowed = MODEL_SOURCE_LICENCES.get(source) if kind == "models" else None
    if allowed is None:
        sources = sorted(LICENCES) + (sorted(MODEL_SOURCE_LICENCES) + [GENERATED] if kind == "models" else [])
        raise LicenceError(f"source '{source}' is not a {kind} source {sources}; refused")
    if licence is None:
        raise LicenceError(f"{source}: no per-object licence given; refused")
    text = str(licence).strip()
    text = {a.upper(): a for a in allowed}.get(text.upper(), text)
    if text not in allowed:
        raise LicenceError(f"{source}: licence '{licence}' is not one of {', '.join(allowed)}; refused")
    if entry is not None and "licence_flag" in entry and entry.get("licence_flag") != _FLAGS[text]:
        raise LicenceError(f"{source}: model {entry.get('id', '?')!r} with licence {text} has licence_flag "
                           f"{entry.get('licence_flag')!r}, not {_FLAGS[text]!r}; refused")
    if text != LICENCE and entry is not None:
        missing = [k for k in CC_BY_FIELDS if not str(entry.get(k) or "").strip()]
        if missing:
            raise LicenceError(f"{source}: {text} model {entry.get('id', '?')!r} without {', '.join(missing)} "
                               f"(no credit line); refused")
    return text


def manifest_path(assets_dir: Path) -> Path:
    return Path(assets_dir) / MANIFEST_NAME


def empty_manifest() -> dict:
    return {"schema_version": MANIFEST_VERSION, "textures": {}, "hdris": {}, "models": {}}


def load_manifest(assets_dir: Path) -> dict:
    """The manifest (empty when missing). Every entry's licence is checked by the rule of its kind
    (``check_licence``); a refused entry -> LicenceError."""
    path = manifest_path(assets_dir)
    if not path.is_file():
        return empty_manifest()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.setdefault("textures", {})
    manifest.setdefault("hdris", {})
    manifest.setdefault("models", {})
    for kind in KINDS:
        for asset_id, entry in manifest[kind].items():
            check_licence(entry.get("source", "?"), entry.get("licence"), kind=kind, entry=entry)
    return manifest


def save_manifest(assets_dir: Path, manifest: dict) -> Path:
    path = manifest_path(assets_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _files_ok(assets_dir: Path, entry: dict, size: str) -> bool:
    """True when the entry was fetched at ``size`` and every file is present with the recorded sha256."""
    if entry.get("resolution") != size:
        return False
    files = entry["files"] if "files" in entry else {"file": entry["file"]}
    for key, rel in files.items():
        path = Path(assets_dir) / rel
        if not path.is_file() or web.sha256_file(path) != entry.get("sha256", {}).get(key):
            return False
    return True


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# Source inference
# --------------------------------------------------------------------------

def source_of_texture(asset_id: str) -> str:
    """The source of a texture id: the vocabulary (style and furniture tables) first, then the id shape."""
    for entry in list(V.MATERIALS.values()) + list(V.FURNITURE_MATERIALS.values()):
        if entry.get("asset") == asset_id:
            return entry["source"]
    return ambientcg.SOURCE if ambientcg.looks_like_id(asset_id) else polyhaven.SOURCE


# --------------------------------------------------------------------------
# Textures
# --------------------------------------------------------------------------

def fetch_texture(asset_id: str, out_dir: Path, size: str = "2k", source: Optional[str] = None,
                  licence: Optional[str] = None) -> dict:
    """Fetch a PBR texture set (albedo, normal GL, roughness, optional displacement).

    ``size`` is ``1k`` / ``2k`` / ``4k`` (JPG maps). The returned dict is the
    manifest entry (paths relative to ``out_dir``).
    """
    out_dir = Path(out_dir)
    source = source or source_of_texture(asset_id)
    check_licence(source, licence)
    manifest = load_manifest(out_dir)
    cached = manifest["textures"].get(asset_id)
    if cached and cached.get("source") == source and _files_ok(out_dir, cached, size):
        return cached

    if source == polyhaven.SOURCE:
        entry = _fetch_polyhaven_texture(asset_id, out_dir, size)
    else:
        entry = _fetch_ambientcg_texture(asset_id, out_dir, size)
    manifest = load_manifest(out_dir)  # re-read: another fetch may have written meanwhile
    manifest["textures"][asset_id] = entry
    save_manifest(out_dir, manifest)
    return entry


def _fetch_polyhaven_texture(asset_id: str, out_dir: Path, size: str) -> dict:
    try:
        record = polyhaven.info(asset_id)
        table = polyhaven.files(asset_id)
    except web.HTTPStatusError as exc:
        if exc.status == 404:
            raise AssetNotFound(f"polyhaven: no asset '{asset_id}'") from exc
        raise
    urls = polyhaven.texture_urls(table, size=size, fmt="jpg")
    size_m = polyhaven.size_m(record)
    size_assumed = size_m is None
    if size_assumed:
        size_m = [ambientcg.DEFAULT_SIZE_M, ambientcg.DEFAULT_SIZE_M]
    folder = out_dir / "textures" / asset_id
    files, shas, src_urls = {}, {}, {}
    for name, item in urls.items():
        target = folder / item["url"].rsplit("/", 1)[-1]
        if not (target.is_file() and _md5_matches(target, item.get("md5"))):
            web.download(item["url"], target, expected_md5=item.get("md5"))
        files[name] = target.relative_to(out_dir).as_posix()
        shas[name] = web.sha256_file(target)
        src_urls[name] = item["url"]
    return _texture_entry(asset_id, polyhaven.SOURCE, size, size_m, size_assumed, files, shas,
                          api_url=f"{polyhaven.API}/files/{asset_id}", urls=src_urls,
                          name=record.get("name"), fetched=_now())


def _md5_matches(path: Path, md5: Optional[str]) -> bool:
    if not md5:
        return False
    digest = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest() == md5


def _fetch_ambientcg_texture(asset_id: str, out_dir: Path, size: str) -> dict:
    record = ambientcg.info(asset_id)
    if record is None:
        raise AssetNotFound(f"ambientcg: no asset '{asset_id}'")
    item = ambientcg.zip_download(record, size=size, fmt="JPG")
    size_m, size_assumed = ambientcg.size_m(record)
    folder = out_dir / "textures" / asset_id
    zip_path = out_dir / "downloads" / item["fileName"]
    try:
        web.download(item["downloadLink"], zip_path)
    except web.NetworkError as exc:
        # The get?file= link redirects to the download host; a proxy allow-list must include it.
        raise web.NetworkError(f"{exc} (ambientCG downloads redirect to {ambientcg.DOWNLOAD_HOST}; "
                               f"that host must be reachable)") from exc
    try:
        paths = ambientcg.extract_set(zip_path, folder)
    finally:
        zip_path.unlink(missing_ok=True)  # the maps are what we keep; the manifest makes this idempotent
    files = {name: p.relative_to(out_dir).as_posix() for name, p in paths.items()}
    shas = {name: web.sha256_file(p) for name, p in paths.items()}
    return _texture_entry(asset_id, ambientcg.SOURCE, size, size_m, size_assumed, files, shas,
                          api_url=f"{ambientcg.API}?id={asset_id}&include={ambientcg.INCLUDE}",
                          urls={"zip": item["downloadLink"]}, name=record.get("displayName"), fetched=_now())


def _texture_entry(asset_id, source, size, size_m, size_assumed, files, shas, *, api_url, urls, name, fetched) -> dict:
    entry = {
        "id": asset_id, "source": source, "licence": LICENCE, "licence_url": LICENCE_URLS[source],
        "size_m": size_m, "files": files, "sha256": shas, "resolution": size, "name": name,
        "url": api_url, "download_urls": urls, "fetched_utc": fetched,
    }
    if size_assumed:
        entry["size_assumed"] = True  # no real-world size on the API; 1 m x 1 m assumed
    return entry


# --------------------------------------------------------------------------
# HDRIs
# --------------------------------------------------------------------------

def fetch_hdri(asset_id: str, out_dir: Path, size: str = "2k", source: str = polyhaven.SOURCE,
               licence: Optional[str] = None) -> dict:
    """Fetch an HDRI (``.hdr``) from Poly Haven and record it in the manifest."""
    out_dir = Path(out_dir)
    check_licence(source, licence)
    if source != polyhaven.SOURCE:
        raise AssetNotFound(f"HDRIs come from Poly Haven only, not '{source}'")
    manifest = load_manifest(out_dir)
    cached = manifest["hdris"].get(asset_id)
    if cached and _files_ok(out_dir, cached, size):
        return cached

    try:
        record = polyhaven.info(asset_id)
        table = polyhaven.files(asset_id)
    except web.HTTPStatusError as exc:
        if exc.status == 404:
            raise AssetNotFound(f"polyhaven: no HDRI '{asset_id}'") from exc
        raise
    item = polyhaven.hdri_url(table, size=size, fmt="hdr")
    target = out_dir / "hdris" / item["url"].rsplit("/", 1)[-1]
    if not (target.is_file() and _md5_matches(target, item.get("md5"))):
        web.download(item["url"], target, expected_md5=item.get("md5"))
    entry = {
        "id": asset_id, "source": polyhaven.SOURCE, "licence": LICENCE, "licence_url": LICENCE_URLS[polyhaven.SOURCE],
        "file": target.relative_to(out_dir).as_posix(), "sha256": {"file": web.sha256_file(target)},
        "resolution": size, "name": record.get("name"), "whitebalance_k": record.get("whitebalance"),
        "url": f"{polyhaven.API}/files/{asset_id}", "download_urls": {"file": item["url"]}, "fetched_utc": _now(),
    }
    manifest = load_manifest(out_dir)
    manifest["hdris"][asset_id] = entry
    save_manifest(out_dir, manifest)
    return entry


# --------------------------------------------------------------------------
# Whole style, vocabulary check
# --------------------------------------------------------------------------

def fetch_for_style(style: dict, out_dir: Path, size: str = "2k", hdri_size: Optional[str] = None,
                    log=print) -> dict:
    """Fetch every texture set and the HDRI a style profile uses, plus the
    furniture texture maps (``vocabulary.furniture_textures``: the veneers and
    the linen weave every parametric piece and wood door uses, docs/milestone6.md
    §5 row 8).

    Failures (blocked host, unknown id, licence) do not stop the run: they are
    returned under ``"failed"`` so the scene builder can fall back to flat
    colours and record that in its manifest.
    """
    from wenart.style.profile import assets_in_profile

    wanted = assets_in_profile(style)
    textures = list(wanted["textures"])
    seen = {asset_id for _, asset_id, _ in textures}
    for row in V.furniture_textures():
        if row[1] not in seen:
            seen.add(row[1])
            textures.append(row)
    result = {"textures": {}, "hdris": {}, "failed": {}}
    for source, asset_id, slug in textures:
        try:
            entry = fetch_texture(asset_id, out_dir, size=size, source=source)
            result["textures"][asset_id] = entry
            log(f"texture {asset_id:<28} {source:<10} {slug:<20} {entry['size_m'][0]} x {entry['size_m'][1]} m  ok")
        except (web.NetworkError, web.HTTPStatusError, AssetNotFound, LicenceError, KeyError, RuntimeError) as exc:
            result["failed"][asset_id] = f"{type(exc).__name__}: {exc}"
            log(f"texture {asset_id:<28} {source:<10} {slug:<20} FAILED: {exc}")
    for source, hdri_id in wanted["hdris"]:
        try:
            entry = fetch_hdri(hdri_id, out_dir, size=hdri_size or size, source=source)
            result["hdris"][hdri_id] = entry
            log(f"hdri    {hdri_id:<28} {source:<10} {'':<20} {entry['file']}  ok")
        except (web.NetworkError, web.HTTPStatusError, AssetNotFound, LicenceError, KeyError, RuntimeError) as exc:
            result["failed"][hdri_id] = f"{type(exc).__name__}: {exc}"
            log(f"hdri    {hdri_id:<28} {source:<10} {'':<20} FAILED: {exc}")
    return result


def verify_vocabulary() -> list[dict]:
    """Check every asset id of the vocabulary against the APIs without downloading.

    Three API calls in total (Poly Haven textures, Poly Haven HDRIs, one
    ambientCG query with all ids). Rows: ``{"slug", "source", "id", "kind",
    "exists", "size_m"}``; kind ``texture`` (style materials), ``furniture_texture``
    (``vocabulary.FURNITURE_MATERIALS`` with an asset; ``size_m`` must equal the
    vocabulary's ``size_m``, ``size_ok``) or ``hdri``. Procedural entries (no asset id)
    have nothing to check and are left out; a style material with a recorded ``size_m``
    (Milestone 10) is size-checked like a furniture texture.
    """
    ph_textures = polyhaven.list_assets("textures")
    ph_hdris = polyhaven.list_assets("hdris")
    entries = [(slug, e, "texture") for slug, e in V.MATERIALS.items() if e.get("asset")]
    entries += [(slug, e, "furniture_texture") for slug, e in V.FURNITURE_MATERIALS.items() if e.get("asset")]
    acg_ids = sorted({e["asset"] for _, e, _ in entries if e["source"] == ambientcg.SOURCE})
    acg = ambientcg.infos(acg_ids)
    rows = []
    for slug, entry, kind in entries:
        asset_id, source = entry["asset"], entry["source"]
        if source == polyhaven.SOURCE:
            record = ph_textures.get(asset_id)
            size = polyhaven.size_m(record) if record else None
        else:
            record = acg.get(asset_id)
            size = ambientcg.size_m(record)[0] if record else None
        row = {"slug": slug, "source": source, "id": asset_id, "kind": kind, "exists": record is not None,
               "size_m": size}
        if entry.get("size_m"):
            row["size_ok"] = size is not None and [round(v, 4) for v in size] == [round(v, 4) for v in entry["size_m"]]
        rows.append(row)
    for hdri_id, entry in V.HDRIS.items():
        record = ph_hdris.get(hdri_id)
        rows.append({"slug": entry["mood"], "source": entry["source"], "id": hdri_id, "kind": "hdri",
                     "exists": record is not None, "size_m": None})
    return rows


# --------------------------------------------------------------------------
# Milestone 10: the committed record of what was checked (wenart/style/asset_checks_m10.json)
# --------------------------------------------------------------------------

CHECKS_PATH = Path(__file__).resolve().parents[1] / "style" / "asset_checks_m10.json"
CHECKS_SCHEMA = "wenart-asset-checks-m10/1"
PH_MAPS = ("Diffuse", "nor_gl", "Rough", "Displacement", "AO", "arm")
PH_TEXTURE_TYPE = 1                    # ``type`` of /info: 0 = HDRI, 1 = texture, 2 = model
REQUIRED_PH_MAPS = ("Diffuse", "nor_gl", "Rough")
REQUIRED_ACG_MAPS = ("color", "normal", "roughness")
MEASURE_SIDE = 64


def texture_rows() -> list[dict]:
    """One row per (source, asset id) the vocabulary references: ``{"source", "asset", "slugs": [...], "size_m"}``
    (``size_m``: the vocabulary's own value or None). Procedural entries (no ``asset``) are left out."""
    rows: dict[tuple, dict] = {}
    for table in (V.MATERIALS, V.FURNITURE_MATERIALS):
        for slug, entry in table.items():
            if not entry.get("asset"):
                continue
            row = rows.setdefault((entry["source"], entry["asset"]),
                                  {"source": entry["source"], "asset": entry["asset"], "slugs": [],
                                   "size_m": entry.get("size_m")})
            row["slugs"].append(slug)
            row["size_m"] = row["size_m"] or entry.get("size_m")
    return sorted(rows.values(), key=lambda r: (r["source"], r["asset"]))


def mean_linear_rgb(path: Path, side: int = MEASURE_SIDE) -> list[float]:
    """Mean linear RGB of an sRGB image (box-filtered to ``side`` x ``side`` first; 3 decimals)."""
    import numpy as np
    from PIL import Image

    with Image.open(path) as img:
        small = np.asarray(img.convert("RGB").resize((side, side), Image.BOX), dtype=np.float64) / 255.0
    lin = np.where(small <= 0.04045, small / 12.92, ((small + 0.055) / 1.055) ** 2.4)
    return [round(float(v), 3) for v in lin.reshape(-1, 3).mean(axis=0)]


def _check_polyhaven_texture(asset_id: str, measure: bool, cache: Optional[Path]) -> dict:
    out: dict = {"source": polyhaven.SOURCE, "asset": asset_id, "licence": LICENCE}
    try:
        record = polyhaven.info(asset_id)
        table = polyhaven.files(asset_id)
    except web.HTTPStatusError as exc:
        if exc.status == 404:
            return {**out, "exists": False}
        raise
    maps = {key: sorted(table[key], key=lambda k: int(k.rstrip("k"))) for key in PH_MAPS if key in table}
    size = polyhaven.size_m(record)
    out.update({"exists": True, "name": record.get("name"), "api_type": record.get("type"),
                "categories": record.get("categories"), "size_m": size,
                "size_note": "dimensions of /info (millimetres) / 1000" if size else "the API gives no size",
                "maps": maps,
                "has_required_maps": all(k in table and "1k" in table[k] and "2k" in table[k] for k in REQUIRED_PH_MAPS),
                "jpg_1k_2k": all("jpg" in table[k].get("1k", {}) and "jpg" in table[k].get("2k", {})
                                 for k in REQUIRED_PH_MAPS if k in table),
                "max_resolution": record.get("max_resolution"), "measured_flat_linear": None})
    if measure and "Diffuse" in table:
        item = table["Diffuse"]["1k"]["jpg"]
        target = Path(cache or Path.cwd()) / f"{asset_id}_diff_1k.jpg"
        if not (target.is_file() and _md5_matches(target, item.get("md5"))):
            web.download(item["url"], target, expected_md5=item.get("md5"))
        out["measured_flat_linear"] = mean_linear_rgb(target)
        out["measure_note"] = (f"mean of the linear values of the 1k Diffuse jpg, box-filtered to "
                               f"{MEASURE_SIDE} x {MEASURE_SIDE}")
    return out


def _check_ambientcg_textures(asset_ids: list[str]) -> dict:
    records = ambientcg.infos(asset_ids) if asset_ids else {}
    out = {}
    for asset_id in asset_ids:
        record = records.get(asset_id)
        if record is None:
            out[asset_id] = {"source": ambientcg.SOURCE, "asset": asset_id, "licence": LICENCE, "exists": False}
            continue
        size, assumed = ambientcg.size_m(record)
        try:
            downloads = [d.get("attribute") for d in
                         record["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"]]
        except KeyError:
            downloads = []
        maps = sorted(record.get("maps") or [])
        out[asset_id] = {
            "source": ambientcg.SOURCE, "asset": asset_id, "licence": LICENCE, "exists": True,
            "name": record.get("displayName"), "category": record.get("displayCategory"),
            "size_m": None if assumed else size,
            "size_note": ("dimensionX / dimensionY of the API (centimetres) / 100" if not assumed else
                          "the API gives 0 x 0: the fetcher assumes 1 x 1 m and flags the entry size_assumed"),
            "maps": maps, "has_required_maps": all(m in maps for m in REQUIRED_ACG_MAPS),
            "downloads": downloads, "jpg_1k_2k": all(a in downloads for a in ("1K-JPG", "2K-JPG")),
            "measured_flat_linear": None,
            "measure_note": f"not measured: the download host {ambientcg.DOWNLOAD_HOST} is not reachable from the "
                            f"cloud session; the vocabulary's flat colour is an estimate (flat_source in the entry)"}
    return out


def check_assets(rows: Optional[list[dict]] = None, measure: bool = False, cache: Optional[Path] = None,
                 log=print) -> dict:
    """Verify every textured slug and every HDRI of the vocabulary against the live APIs (no texture download unless
    ``measure``: the Poly Haven 1k Diffuse maps are fetched into ``cache`` and their mean linear colour recorded).

    Returns the document of ``wenart/style/asset_checks_m10.json``: ``{"schema", "checked", "textures":
    {"<source>:<id>": record}, "hdris": {id: record}, "problems": [...]}``; ``problems`` lists every id that does
    not exist or lacks a required map or whose size differs from the vocabulary's ``size_m``."""
    rows = rows if rows is not None else texture_rows()
    by_key = {f"{r['source']}:{r['asset']}": r for r in rows}
    textures: dict[str, dict] = {}
    for row in rows:
        if row["source"] == polyhaven.SOURCE:
            record = _check_polyhaven_texture(row["asset"], measure, cache)
            textures[f"{row['source']}:{row['asset']}"] = record
            log(f"polyhaven {row['asset']:<32} {'ok' if record.get('exists') else 'MISSING'}")
    acg_ids = [r["asset"] for r in rows if r["source"] == ambientcg.SOURCE]
    for asset_id, record in _check_ambientcg_textures(acg_ids).items():
        textures[f"{ambientcg.SOURCE}:{asset_id}"] = record
        log(f"ambientcg {asset_id:<32} {'ok' if record.get('exists') else 'MISSING'}")
    for key, record in textures.items():
        record["slugs"] = by_key[key]["slugs"]
    hdris: dict[str, dict] = {}
    for hdri_id, entry in V.HDRIS.items():
        try:
            record, table = polyhaven.info(hdri_id), polyhaven.files(hdri_id)
        except web.HTTPStatusError as exc:
            if exc.status != 404:
                raise
            hdris[hdri_id] = {"source": polyhaven.SOURCE, "asset": hdri_id, "exists": False, "moods": [entry["mood"]]}
            continue
        sizes = sorted(table.get("hdri", {}), key=lambda k: int(k.rstrip("k")))
        hdris[hdri_id] = {"source": polyhaven.SOURCE, "asset": hdri_id, "licence": LICENCE, "exists": True,
                          "name": record.get("name"), "moods": [entry["mood"]], "sizes": sizes,
                          "hdr_1k_2k": all("hdr" in table["hdri"].get(s, {}) for s in ("1k", "2k")),
                          "whitebalance_k": record.get("whitebalance"), "attributes": record.get("attributes"),
                          "max_resolution": record.get("max_resolution")}
    problems = []
    for key, record in textures.items():
        want = by_key[key].get("size_m")
        if not record.get("exists"):
            problems.append(f"{key}: not found")
        elif record["source"] == polyhaven.SOURCE and record.get("api_type") != PH_TEXTURE_TYPE:
            problems.append(f"{key}: Poly Haven lists it as type {record.get('api_type')}, not a texture ({PH_TEXTURE_TYPE})")
        elif not (record.get("has_required_maps") and record.get("jpg_1k_2k")):
            problems.append(f"{key}: missing map or jpg size")
        elif want and (record.get("size_m") is None or
                       [round(v, 4) for v in record["size_m"]] != [round(v, 4) for v in want]):
            problems.append(f"{key}: API size {record.get('size_m')} differs from the vocabulary's {want}")
    for hdri_id, record in hdris.items():
        if not record.get("exists") or not record.get("hdr_1k_2k"):
            problems.append(f"polyhaven:{hdri_id} (hdri): not found or no 1k/2k hdr")
    return {"schema": CHECKS_SCHEMA, "checked": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "apis": {"polyhaven": "https://api.polyhaven.com/assets?type=textures, /info/<id>, /files/<id>",
                     "ambientcg": f"{ambientcg.API}?id=<ids>&include={ambientcg.INCLUDE}"},
            "textures": textures, "hdris": hdris, "problems": problems}


def write_checks(checks: dict, path: Path = CHECKS_PATH) -> Path:
    """Write the check record (sorted keys, 2-space indent, trailing newline)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checks, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_checks(path: Path = CHECKS_PATH) -> dict:
    """The committed check record (``{}`` when the file is missing)."""
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main(argv=None) -> int:
    """``python -m wenart.assets.fetch check [--out PATH] [--measure] [--cache DIR]``: write the check record."""
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description="verify the vocabulary's texture and HDRI ids against the live APIs")
    parser.add_argument("action", choices=["check"])
    parser.add_argument("--out", default=str(CHECKS_PATH), help="where to write the record")
    parser.add_argument("--measure", action="store_true", help="also measure the mean colour of the Poly Haven maps")
    parser.add_argument("--cache", default=None, help="folder for the measured 1k Diffuse maps (default: a temp folder)")
    args = parser.parse_args(argv)
    cache = Path(args.cache) if args.cache else Path(tempfile.mkdtemp(prefix="wenart_checks_"))
    checks = check_assets(measure=args.measure, cache=cache)
    path = write_checks(checks, Path(args.out))
    print(f"{len(checks['textures'])} textures, {len(checks['hdris'])} HDRIs checked, "
          f"{len(checks['problems'])} problems -> {path}")
    for problem in checks["problems"]:
        print(f"  problem: {problem}")
    return 1 if checks["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
