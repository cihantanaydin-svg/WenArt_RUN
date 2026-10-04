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
    vocabulary's ``size_m``, ``size_ok``) or ``hdri``.
    """
    ph_textures = polyhaven.list_assets("textures")
    ph_hdris = polyhaven.list_assets("hdris")
    entries = [(slug, e, "texture") for slug, e in V.MATERIALS.items()]
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
        if kind == "furniture_texture":
            row["size_ok"] = size is not None and [round(v, 4) for v in size] == list(entry.get("size_m") or [])
        rows.append(row)
    for hdri_id, entry in V.HDRIS.items():
        record = ph_hdris.get(hdri_id)
        rows.append({"slug": entry["mood"], "source": entry["source"], "id": hdri_id, "kind": "hdri",
                     "exists": record is not None, "size_m": None})
    return rows
