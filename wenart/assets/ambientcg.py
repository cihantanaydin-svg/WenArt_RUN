"""ambientCG API v2 client (PBR materials, all CC0), the second texture source.

Verified with real calls on 2026-10-01:

- ``GET https://ambientcg.com/api/v2/full_json?id=WoodFloor051,Plaster001
  &include=dimensionsData,downloadData,tagData,displayData&limit=100`` ->
  ``{"searchQuery", "numberOfResults", "currentPageHttp", "foundAssets": [...]}``.
  Unknown ids are simply absent (``numberOfResults`` 0, no error).
  Other query parameters seen working: ``q=<words>``, ``type=Material``,
  ``sort=Popular``, ``limit``, ``offset``.
- Each found asset: ``assetId``, ``dataType`` ("Material"), ``displayName``,
  ``displayCategory``, ``tags``, ``maps`` (["color", "normal", "roughness",
  "displacement", ...]), ``dimensionX`` / ``dimensionY`` / ``dimensionZ``
  (centimetres; 0 when unknown: ``WoodFloor051`` = 180 -> 1.8 m) and
  ``downloadFolders.default.downloadFiletypeCategories.zip.downloads`` = list
  of ``{"attribute": "1K-JPG" | "2K-JPG" | "4K-JPG" | "8K-JPG" | "1K-PNG" ...,
  "downloadLink": "https://ambientcg.com/get?file=<id>_<attr>.zip",
  "fileName", "size"}``.
- ``get?file=...`` answers 302 to ``https://acg-download.struffelproductions.com/...``
  (that host must be reachable; the sandbox proxy of this repo blocks it).
- The zip holds ``<id>_<attr>_Color.jpg``, ``_NormalGL.jpg``, ``_NormalDX.jpg``,
  ``_Roughness.jpg``, ``_Displacement.jpg`` (+ ``_AmbientOcclusion`` / ``_Metalness``
  when present). The map names are matched by suffix, case-insensitive.
- No licence field in the API: all ambientCG assets are CC0 1.0 (stated on
  every asset page and in the site terms), which ``fetch.LICENCES`` records.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Optional

from wenart.assets import web

API = "https://ambientcg.com/api/v2/full_json"
SOURCE = "ambientcg"
DOWNLOAD_HOST = "acg-download.struffelproductions.com"  # where get?file= redirects (seen 2026-10-01)
INCLUDE = "dimensionsData,downloadData,tagData,displayData"
DEFAULT_SIZE_M = 1.0  # when dimensionX / dimensionY are 0 (docs/milestone3.md section 2)

# Our map name -> file-name suffix inside the zip (without extension).
MAP_SUFFIXES = {"albedo": "_Color", "normal": "_NormalGL", "roughness": "_Roughness"}
OPTIONAL_SUFFIXES = {"displacement": "_Displacement"}

_ID_RE = re.compile(r"^[A-Z][A-Za-z]*\d{3}[A-Z]?$")


def looks_like_id(asset_id: str) -> bool:
    """ambientCG ids are CamelCase + 3 digits (+ optional variant letter): ``WoodFloor051``."""
    return bool(_ID_RE.match(asset_id))


def infos(asset_ids: list[str]) -> dict:
    """``{asset_id: record}`` for the ids that exist (missing ids are absent)."""
    if not asset_ids:
        return {}
    url = f"{API}?id={','.join(asset_ids)}&include={INCLUDE}&limit={max(100, len(asset_ids))}"
    data = web.get_json(url)
    return {a["assetId"]: a for a in data.get("foundAssets", [])}


def info(asset_id: str) -> Optional[dict]:
    """The record of one asset, or None when ambientCG does not know the id."""
    return infos([asset_id]).get(asset_id)


def size_m(record: dict) -> tuple[list[float], bool]:
    """``([w, h] in metres, assumed)``; ``assumed`` is True when the API has no size (0)."""
    w, h = record.get("dimensionX") or 0, record.get("dimensionY") or 0
    if w > 0 and h > 0:
        return [round(w / 100.0, 4), round(h / 100.0, 4)], False
    return [DEFAULT_SIZE_M, DEFAULT_SIZE_M], True


def zip_download(record: dict, size: str = "2k", fmt: str = "JPG") -> dict:
    """The download entry (``downloadLink``, ``fileName``, ``size``, ``attribute``) of the ``<size>-<fmt>`` zip."""
    attribute = f"{size.upper()}-{fmt.upper()}"
    try:
        downloads = record["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"]
    except KeyError as exc:
        raise KeyError(f"ambientCG record {record.get('assetId')} has no zip downloads") from exc
    for entry in downloads:
        if entry.get("attribute") == attribute:
            return entry
    raise KeyError(f"ambientCG {record.get('assetId')} has no {attribute} zip "
                   f"(available: {[d.get('attribute') for d in downloads]})")


def extract_set(zip_path: Path, out_dir: Path) -> dict:
    """Unpack the map files of an ambientCG zip into ``out_dir``; ``{"albedo": path, ...}``.

    Only the files we use are extracted (Color, NormalGL, Roughness and, when
    present, Displacement). Raises KeyError when a required map is missing.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    found: dict[str, Path] = {}
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        for name, suffix in {**MAP_SUFFIXES, **OPTIONAL_SUFFIXES}.items():
            match = _match_suffix(names, suffix)
            if match is None:
                continue
            target = out_dir / Path(match).name
            with zf.open(match) as src, target.open("wb") as dst:
                dst.write(src.read())
            found[name] = target
    missing = [name for name in MAP_SUFFIXES if name not in found]
    if missing:
        raise KeyError(f"{zip_path.name}: maps {missing} not found in {names}")
    return found


def _match_suffix(names: list[str], suffix: str) -> Optional[str]:
    pattern = re.compile(re.escape(suffix) + r"\.(jpg|jpeg|png)$", re.IGNORECASE)
    for name in sorted(names):
        if pattern.search(Path(name).name):
            return name
    return None
