"""Poly Haven API client (textures and HDRIs, all CC0).

Verified with real calls on 2026-10-01 (``docs/milestone3.md`` section 2):

- ``GET https://api.polyhaven.com/assets?type=textures`` (or ``hdris``) ->
  ``{asset_id: {"name", "type", "categories", "tags", "dimensions": [w_mm, h_mm]
  (textures only), "whitebalance" (HDRIs, Kelvin, may be missing), "attributes",
  "max_resolution", ...}}``. 863 textures and 997 HDRIs at the time.
- ``GET /info/{id}`` -> the same record for one asset; 404 for unknown ids.
- ``GET /files/{id}`` -> textures: ``{"Diffuse": {"1k": {"jpg": {"url", "size",
  "md5"}, "png": ..., "exr": ...}, "2k": ..., "4k": ..., "8k": ...}, "nor_gl": ...,
  "nor_dx": ..., "Rough": ..., "Displacement": ..., "AO", "arm", "blend", "gltf",
  "mtlx"}``; HDRIs: ``{"hdri": {"1k": {"hdr": {"url", "size", "md5"}, "exr": ...},
  ...}, "tonemapped": ...}``. Files are served from ``dl.polyhaven.org``.
- ``dimensions`` is in millimetres (``wood_floor_deck`` -> 1800 = 1.8 m).
- The listing has no per-asset licence field: every Poly Haven asset is CC0
  (https://polyhaven.com/license), which ``fetch.LICENCES`` records.
"""
from __future__ import annotations

from typing import Optional

from wenart.assets import web

API = "https://api.polyhaven.com"
SOURCE = "polyhaven"

# Our map name -> Poly Haven map key (OpenGL normal convention).
TEXTURE_MAPS = {"albedo": "Diffuse", "normal": "nor_gl", "roughness": "Rough"}
OPTIONAL_MAPS = {"displacement": "Displacement"}


def list_assets(asset_type: str = "textures") -> dict:
    """``{asset_id: record}`` for ``textures``, ``hdris`` or ``models``."""
    return web.get_json(f"{API}/assets?type={asset_type}")


def info(asset_id: str) -> dict:
    """The record of one asset (``HTTPStatusError`` 404 when it does not exist)."""
    return web.get_json(f"{API}/info/{asset_id}")


def files(asset_id: str) -> dict:
    """The file table of one asset (see module docstring)."""
    return web.get_json(f"{API}/files/{asset_id}")


def size_m(record: dict) -> Optional[list[float]]:
    """Real-world size ``[w, h]`` in metres from the ``dimensions`` field (mm), or None."""
    dims = record.get("dimensions")
    if not dims or len(dims) < 2 or not all(isinstance(d, (int, float)) and d > 0 for d in dims[:2]):
        return None
    return [round(dims[0] / 1000.0, 4), round(dims[1] / 1000.0, 4)]


def texture_urls(file_table: dict, size: str = "2k", fmt: str = "jpg") -> dict:
    """``{"albedo": {"url", "md5", "size"}, "normal": ..., "roughness": ..., ["displacement"]}``.

    Raises KeyError naming the missing map or size, so a wrong id or an
    asset without a roughness map fails loudly instead of half-downloading.
    """
    out = {}
    for name, key in TEXTURE_MAPS.items():
        try:
            out[name] = file_table[key][size][fmt]
        except KeyError as exc:
            raise KeyError(f"Poly Haven file table has no {key}/{size}/{fmt} ({name})") from exc
    for name, key in OPTIONAL_MAPS.items():
        entry = file_table.get(key, {}).get(size, {}).get(fmt)
        if entry:
            out[name] = entry
    return out


def hdri_url(file_table: dict, size: str = "2k", fmt: str = "hdr") -> dict:
    """``{"url", "md5", "size"}`` of the HDRI file at ``size`` (``1k`` ... ``24k``)."""
    try:
        return file_table["hdri"][size][fmt]
    except KeyError as exc:
        raise KeyError(f"Poly Haven file table has no hdri/{size}/{fmt}") from exc
