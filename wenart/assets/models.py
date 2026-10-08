"""Furniture models: CC0 Poly Haven downloads and the Objaverse cache, recorded in the manifest.

What: ``fetch_model(asset_id, out_dir, size="1k")`` downloads the glTF of one
Poly Haven model (the ``.gltf`` plus every file it includes: ``.bin`` and the
JPG textures) into ``<out_dir>/models/<id>/`` and records it under
``"models"`` in ``<out_dir>/manifest.json`` with licence CC0, files, sha256
and the bounding box measured from the glTF geometry in metres. Idempotent:
a complete entry with matching sha256 causes no network call.
``verify_catalog(ids)`` lists the model ids on the API without downloading.
``measure_gltf(path)`` is the pure measurement used for the bounding box.

Verified with real calls on 2026-10-01 (``docs/milestone4.md`` section 1):

- ``GET https://api.polyhaven.com/assets?type=models`` -> ``{asset_id:
  {"name", "type": 2, "categories", "tags", "category" (e.g.
  "Furniture/Seating/Sofas & Couches"), "dimensions": [x_mm, y_mm, z_mm],
  "polycount", "authors", "description", "max_resolution", ...}}``;
  521 models at the time. ``dimensions`` is in millimetres and in the
  Blender frame of the source file (x width, y depth, z height).
- ``GET /files/{id}`` -> ``{"gltf": {"1k": {"gltf": {"url", "size", "md5",
  "include": {relative_path: {"url", "size", "md5"}}}}, "2k": ..., "4k":
  ...}, "blend": ..., "fbx": ..., "usd": ..., "Diffuse": ..., ...}``. The
  ``include`` keys are the paths the ``.gltf`` references (``textures/...jpg``
  and ``<id>.bin``); files are served from ``dl.polyhaven.org``.
- The glTF files are Y-up (glTF convention, exported from Blender): glTF
  ``(x, y, z)`` is Blender ``(x, -z, y)``. Blender's importer makes that
  conversion, so the bounding box recorded here is in the Z-up Blender
  frame, metres, which is what the catalogue and the scene builder use.
  Checked on ``sofa_02``: the glTF Y extent (0.709 m) is the API's z
  (height) and the glTF Z extent (0.818 m) the API's y (depth).
- No per-asset licence field exists; every Poly Haven asset is CC0
  (https://polyhaven.com/license), recorded by ``fetch.LICENCES``.

Milestone 7 (docs/milestone7.md §6.3): ``fetch_model(..., source="objaverse",
licence=..., meta=<fit asset>)`` never goes to the network: it reads only
the cache ``<assets>/models/objaverse/<uid>.glb`` the prep pod wrote
(``/workspace/assets/models/objaverse`` on the volume) and checks its sha256
against the catalogue's ``sha256_glb``. A miss or a mismatch raises
``fetch.AssetNotFound`` (the fitter turns it into the parametric fallback
and says why; full runs are offline). The licence gate is the model rule of
``fetch.check_licence`` (CC0 or CC BY 4.0 with the credit fields), and the
manifest entry keeps the credit line.

Milestone 8 (docs/milestone8.md §2): the same cache-only fetch for every
library source, ``fetch_model(..., source="abo" | "generated" | "objaverse",
licence=..., meta=<fit asset>)`` (``fetch_library_cached``): the GLB
``<assets>/models/<source>/<uid>.glb`` the prep pod's ``write-catalog``
wrote, its sha256 checked against the catalogue's ``sha256_glb``; a miss or a
mismatch raises ``fetch.AssetNotFound`` (parametric fallback, full runs are
offline). The licence gate is ``fetch.check_licence`` (Objaverse: any licence
with its flag; ABO: CC BY 4.0; generated: ``generated ...``); the manifest
entry keeps the credit fields, the licence flag and, for a generated model,
its ``generated`` record.
"""
from __future__ import annotations

import base64
import json
import math
import re
import struct
from pathlib import Path
from typing import Iterable, Optional

from wenart.assets import fetch, polyhaven, web

MODELS_DIR = "models"
DEFAULT_SIZE = "1k"
PAGE_URL = "https://polyhaven.com/a/{id}"
OBJAVERSE = "objaverse"
OBJAVERSE_CACHE = f"{MODELS_DIR}/objaverse"     # <assets>/models/objaverse/<uid>.glb, written by the prep pod
# The library sources (docs/milestone8.md §2): cache-only GLBs in <assets>/models/<source>/<uid>.glb.
LIBRARY_SOURCES = ("objaverse", "abo", "generated")
_UID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
# Fields of the fit asset (catalogue entry) kept in the manifest entry of an Objaverse model.
OBJAVERSE_META = ("uid", "title", "author", "source_url", "licence_url", "via", "attribution")
# ... and of every library model (Milestone 8).
LIBRARY_META = OBJAVERSE_META + ("licence_flag",)
# ... and, copied only when the catalogue entry has them (Milestone 10, wenart/assets/recolour.py): the material fields
# of the two judges and the species / pot of a generated large plant.
LIBRARY_OPTIONAL = ("material_slots", "material_tags", "recolourable_fabric", "recolourable_wood", "species", "pot",
                    "attributes_status")

# glTF component types -> struct format and byte size.
_COMPONENT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
_TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


class ModelError(RuntimeError):
    """The glTF cannot be read or has no geometry."""


# --------------------------------------------------------------------------
# File table
# --------------------------------------------------------------------------

def model_gltf(file_table: dict, size: str = DEFAULT_SIZE) -> dict:
    """``{"url", "md5", "size", "include": {rel_path: {"url", "md5", "size"}}}`` of the glTF at ``size``.

    Raises KeyError naming the missing size, so a wrong id or a resolution
    the asset does not have fails loudly instead of half-downloading.
    """
    try:
        entry = file_table["gltf"][size]["gltf"]
    except KeyError as exc:
        have = sorted(file_table.get("gltf", {})) if isinstance(file_table.get("gltf"), dict) else []
        raise KeyError(f"Poly Haven file table has no gltf/{size} (available: {have})") from exc
    if "url" not in entry:
        raise KeyError(f"Poly Haven gltf/{size} entry has no url")
    return {"url": entry["url"], "md5": entry.get("md5"), "size": entry.get("size"),
            "include": dict(entry.get("include") or {})}


# --------------------------------------------------------------------------
# Geometry: bounding box from the glTF accessors (pure, no bpy)
# --------------------------------------------------------------------------

def _mat_mul(a: list[float], b: list[float]) -> list[float]:
    """Column-major 4x4 product a @ b (glTF stores matrices column-major)."""
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = sum(a[k * 4 + row] * b[col * 4 + k] for k in range(4))
    return out


def _trs_matrix(node: dict) -> list[float]:
    """The local matrix of a node (``matrix`` or translation/rotation/scale), column-major."""
    if "matrix" in node:
        return [float(v) for v in node["matrix"]]
    t = node.get("translation", [0.0, 0.0, 0.0])
    q = node.get("rotation", [0.0, 0.0, 0.0, 1.0])
    s = node.get("scale", [1.0, 1.0, 1.0])
    x, y, z, w = q
    r = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w),
         2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w),
         2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y)]  # column-major 3x3
    return [r[0] * s[0], r[1] * s[0], r[2] * s[0], 0.0,
            r[3] * s[1], r[4] * s[1], r[5] * s[1], 0.0,
            r[6] * s[2], r[7] * s[2], r[8] * s[2], 0.0,
            float(t[0]), float(t[1]), float(t[2]), 1.0]


def _apply(m: list[float], v: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = v
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def _load_buffers(gltf: dict, base: Path) -> list[bytes]:
    buffers = []
    for buf in gltf.get("buffers", []):
        uri = buf.get("uri")
        if uri is None:
            raise ModelError("GLB-embedded buffers are not supported; use the .gltf + .bin download")
        if uri.startswith("data:"):
            buffers.append(base64.b64decode(uri.split(",", 1)[1]))
        else:
            path = base / uri
            if not path.is_file():
                raise ModelError(f"glTF buffer missing: {path}")
            buffers.append(path.read_bytes())
    return buffers


def _read_accessor(gltf: dict, buffers: list[bytes], index: int) -> list[tuple[float, ...]]:
    acc = gltf["accessors"][index]
    if "bufferView" not in acc:
        return []  # sparse-only / zero-initialised accessors carry no positions we need
    view = gltf["bufferViews"][acc["bufferView"]]
    fmt, comp_size = _COMPONENT[acc["componentType"]]
    n = _TYPE_COUNT[acc["type"]]
    count = acc["count"]
    stride = view.get("byteStride") or comp_size * n
    data = buffers[view["buffer"]]
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    unpack = struct.Struct("<" + fmt * n).unpack_from
    out = []
    for i in range(count):
        values = unpack(data, start + i * stride)
        if acc.get("normalized"):
            scale = {"b": 127.0, "B": 255.0, "h": 32767.0, "H": 65535.0}.get(fmt)
            if scale:
                values = tuple(max(v / scale, -1.0) for v in values)
        out.append(values)
    return out


def _node_matrices(gltf: dict) -> list[tuple[int, list[float]]]:
    """(node index, world matrix) for every node reachable from the scenes (all nodes when no scene)."""
    nodes = gltf.get("nodes", [])
    identity = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    scenes = gltf.get("scenes") or []
    if scenes:
        roots = []
        for scene in scenes:
            roots.extend(scene.get("nodes", []))
    else:
        children = {c for node in nodes for c in node.get("children", [])}
        roots = [i for i in range(len(nodes)) if i not in children]
    out, stack = [], [(i, identity) for i in roots]
    seen = set()
    while stack:
        index, parent = stack.pop()
        if index in seen:
            continue
        seen.add(index)
        node = nodes[index]
        world = _mat_mul(parent, _trs_matrix(node))
        out.append((index, world))
        stack.extend((c, world) for c in node.get("children", []))
    return out


def measure_gltf(path: Path) -> dict:
    """Bounding box of a ``.gltf`` in the Z-up (Blender) frame, metres.

    Walks the scene graph, transforms every POSITION of every mesh primitive
    by its node's world matrix (glTF Y-up), converts to Z-up and returns
    ``{"bbox_min_m", "bbox_max_m", "bbox_m": [x, y, z extents], "vertices",
    "meshes", "top_centroid_xy", "side_counts"}``. ``top_centroid_xy`` (mean
    x, y of the vertices in the top 30 % of the height, relative to the bbox
    centre) and ``side_counts`` (vertices within 5 % of the bbox extent of
    each side: ``-x, +x, -y, +y``) are the raw numbers behind the
    front-axis decision recorded by hand in the catalogue.
    """
    path = Path(path)
    gltf = json.loads(path.read_text(encoding="utf-8"))
    buffers = _load_buffers(gltf, path.parent)
    meshes = gltf.get("meshes", [])
    points: list[tuple[float, float, float]] = []
    mesh_count = 0
    for index, world in _node_matrices(gltf):
        node = gltf["nodes"][index]
        if "mesh" not in node:
            continue
        mesh_count += 1
        for prim in meshes[node["mesh"]].get("primitives", []):
            if "POSITION" not in prim.get("attributes", {}):
                continue
            for v in _read_accessor(gltf, buffers, prim["attributes"]["POSITION"]):
                x, y, z = _apply(world, (v[0], v[1], v[2]))
                points.append((x, -z, y))  # glTF Y-up -> Blender Z-up
    if not points:
        raise ModelError(f"{path.name}: no mesh positions found")
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    ext = [maxs[i] - mins[i] for i in range(3)]
    cx, cy = (mins[0] + maxs[0]) / 2.0, (mins[1] + maxs[1]) / 2.0
    top = [p for p in points if p[2] >= mins[2] + 0.7 * ext[2]] or points
    top_c = [sum(p[0] for p in top) / len(top) - cx, sum(p[1] for p in top) / len(top) - cy]
    tol = [0.05 * e for e in ext]
    sides = {
        "-x": sum(1 for p in points if p[0] <= mins[0] + tol[0]),
        "+x": sum(1 for p in points if p[0] >= maxs[0] - tol[0]),
        "-y": sum(1 for p in points if p[1] <= mins[1] + tol[1]),
        "+y": sum(1 for p in points if p[1] >= maxs[1] - tol[1]),
    }
    return {
        "bbox_min_m": [round(v, 4) for v in mins], "bbox_max_m": [round(v, 4) for v in maxs],
        "bbox_m": [round(v, 4) for v in ext], "vertices": len(points), "meshes": mesh_count,
        "top_centroid_xy": [round(v, 4) for v in top_c], "side_counts": sides,
    }


# --------------------------------------------------------------------------
# Manifest section
# --------------------------------------------------------------------------

def _manifest_models(manifest: dict) -> dict:
    models = manifest.setdefault("models", {})
    for asset_id, entry in models.items():
        fetch.check_licence(entry.get("source", "?"), entry.get("licence"), kind="models", entry=entry)
    return models


def _entry_ok(assets_dir: Path, entry: dict, size: str) -> bool:
    if entry.get("resolution") != size or not entry.get("files"):
        return False
    for key, rel in entry["files"].items():
        path = Path(assets_dir) / rel
        if not path.is_file() or web.sha256_file(path) != entry.get("sha256", {}).get(key):
            return False
    return bool(entry.get("bbox_m"))


def gltf_relpath(asset_id: str, size: str = DEFAULT_SIZE) -> str:
    """Where ``fetch_model`` puts the ``.gltf`` (relative to the assets dir): ``models/<id>/<id>_<size>.gltf``."""
    return f"{MODELS_DIR}/{asset_id}/{asset_id}_{size}.gltf"


def library_relpath(source: str, uid: str) -> str:
    """Where the prep pod puts a library GLB (relative to the assets dir): ``models/<source>/<uid>.glb``."""
    if source not in LIBRARY_SOURCES:
        raise fetch.AssetNotFound(f"{source}: not a library source {LIBRARY_SOURCES}")
    if not _UID_RE.fullmatch(str(uid or "")):
        raise fetch.AssetNotFound(f"{source}: uid {uid!r} is not a plain object id")
    return f"{MODELS_DIR}/{source}/{uid}.glb"


def objaverse_relpath(uid: str) -> str:
    """Where the prep pod puts an Objaverse GLB (relative to the assets dir): ``models/objaverse/<uid>.glb``."""
    return library_relpath(OBJAVERSE, uid)


def fetch_library_cached(asset_id: str, out_dir: Path, source: str, licence: str, meta: Optional[dict]) -> dict:
    """The cached GLB of one library model (``source`` in ``LIBRARY_SOURCES``), recorded in the manifest (no
    network, ever).

    ``meta`` is the fit's asset dict (or the catalogue entry): ``uid``, ``sha256_glb``, the credit fields, the
    ``licence_flag`` and, for a generated model, ``generated``. Raises ``fetch.AssetNotFound`` when the file is
    missing or its sha256 differs from the catalogue's; the manifest entry is ``{"id", "source", "licence", "files":
    {"glb": rel}, "sha256": {"glb": hex}, "uid", "title", "author", "source_url", "licence_url", "via",
    "attribution", "licence_flag", ["generated",] [the ``LIBRARY_OPTIONAL`` material fields, species, pot,] "cache_only":
    true, "fetched_utc"}``."""
    out_dir = Path(out_dir)
    meta = dict(meta or {})
    sha = str(meta.get("sha256_glb") or "")
    rel = library_relpath(source, meta.get("uid"))
    if len(sha) != 64:
        raise fetch.AssetNotFound(f"{source} {asset_id}: no sha256_glb in the catalogue entry; refused")
    path = out_dir / rel
    if not path.is_file():
        raise fetch.AssetNotFound(f"{source} {asset_id}: {rel} is not in the cache {out_dir / MODELS_DIR / source} "
                                  f"(the prep pod writes it; full runs never download)")
    digest = web.sha256_file(path)
    if digest != sha:
        raise fetch.AssetNotFound(f"{source} {asset_id}: cached {rel} has sha256 {digest[:12]}..., the catalogue "
                                  f"says {sha[:12]}...; refused")
    keep = OBJAVERSE_META if source == OBJAVERSE and "licence_flag" not in meta else LIBRARY_META
    entry = {"id": asset_id, "source": source,
             "licence": fetch.check_licence(source, licence, kind="models", entry=dict(meta, id=asset_id)),
             "files": {"glb": rel}, "sha256": {"glb": digest}, "cache_only": True,
             **{k: meta.get(k) for k in keep}}
    if source == "generated" and meta.get("generated") is not None:
        entry["generated"] = meta["generated"]
    entry.update({k: meta[k] for k in LIBRARY_OPTIONAL if meta.get(k) is not None})
    manifest = fetch.load_manifest(out_dir)
    models = _manifest_models(manifest)
    old = models.get(asset_id)
    if old and {k: v for k, v in old.items() if k != "fetched_utc"} == entry:
        return old                                      # idempotent: the manifest is not rewritten
    entry["fetched_utc"] = fetch._now()
    fetch.check_licence(source, entry["licence"], kind="models", entry=entry)
    models[asset_id] = entry
    fetch.save_manifest(out_dir, manifest)
    return entry


def fetch_objaverse_cached(asset_id: str, out_dir: Path, licence: str, meta: Optional[dict]) -> dict:
    """The cached GLB of one Objaverse model (``fetch_library_cached`` with source objaverse; M7 name)."""
    return fetch_library_cached(asset_id, out_dir, OBJAVERSE, licence, meta)


def fetch_model(asset_id: str, out_dir: Path, size: str = DEFAULT_SIZE, source: str = polyhaven.SOURCE,
                licence: Optional[str] = None, meta: Optional[dict] = None) -> dict:
    """Download one Poly Haven model (glTF + bin + textures) and record it in the manifest; for
    ``source="objaverse"`` take the cached GLB instead (``fetch_objaverse_cached``, ``meta`` = the fit's
    asset dict with ``uid``, ``sha256_glb`` and the credit fields).

    Returns the manifest entry: ``{"id", "source", "licence": "CC0",
    "licence_url", "files": {"gltf": rel, "<include path>": rel, ...},
    "sha256": {key: hex}, "bbox_m": [x, y, z], "bbox_min_m", "bbox_max_m",
    "resolution", "name", "category", "dimensions_api_mm", "polycount",
    "url" (API files url), "page_url", "download_urls", "fetched_utc"}``.
    Paths are relative to ``out_dir``; the box is in the Z-up frame, metres.
    """
    out_dir = Path(out_dir)
    fetch.check_licence(source, licence, kind="models", entry=meta if source in LIBRARY_SOURCES else None)
    if source in LIBRARY_SOURCES:
        return fetch_library_cached(asset_id, out_dir, source, licence, meta)
    if source != polyhaven.SOURCE:
        raise fetch.AssetNotFound(f"models come from Poly Haven or the library cache ({', '.join(LIBRARY_SOURCES)}) "
                                  f"only, not '{source}'")
    manifest = fetch.load_manifest(out_dir)
    cached = _manifest_models(manifest).get(asset_id)
    if cached and _entry_ok(out_dir, cached, size):
        return cached

    try:
        record = polyhaven.info(asset_id)
        table = polyhaven.files(asset_id)
    except web.HTTPStatusError as exc:
        if exc.status == 404:
            raise fetch.AssetNotFound(f"polyhaven: no model '{asset_id}'") from exc
        raise
    item = model_gltf(table, size=size)
    folder = out_dir / MODELS_DIR / asset_id
    gltf_target = folder / f"{asset_id}_{size}.gltf"
    wanted = {"gltf": (gltf_target, item)}
    for rel, inc in item["include"].items():
        rel_clean = Path(rel)
        if rel_clean.is_absolute() or ".." in rel_clean.parts:
            raise ModelError(f"{asset_id}: refusing include path {rel!r}")
        wanted[rel] = (folder / rel_clean, inc)
    files, shas, urls = {}, {}, {}
    for key, (target, inc) in wanted.items():
        if not (target.is_file() and fetch._md5_matches(target, inc.get("md5"))):
            web.download(inc["url"], target, expected_md5=inc.get("md5"))
        files[key] = target.relative_to(out_dir).as_posix()
        shas[key] = web.sha256_file(target)
        urls[key] = inc["url"]
    measured = measure_gltf(gltf_target)
    entry = {
        "id": asset_id, "source": polyhaven.SOURCE, "licence": fetch.LICENCE,
        "licence_url": fetch.LICENCE_URLS[polyhaven.SOURCE], "files": files, "sha256": shas,
        "bbox_m": measured["bbox_m"], "bbox_min_m": measured["bbox_min_m"], "bbox_max_m": measured["bbox_max_m"],
        "vertices": measured["vertices"], "resolution": size, "name": record.get("name"),
        "category": record.get("category"), "dimensions_api_mm": record.get("dimensions"),
        "polycount": record.get("polycount"), "url": f"{polyhaven.API}/files/{asset_id}",
        "page_url": PAGE_URL.format(id=asset_id), "download_urls": urls, "fetched_utc": fetch._now(),
    }
    manifest = fetch.load_manifest(out_dir)
    _manifest_models(manifest)[asset_id] = entry
    fetch.save_manifest(out_dir, manifest)
    return entry


def verify_catalog(ids: Iterable[str]) -> list[dict]:
    """Check model ids against the Poly Haven listing with one API call, no download.

    Rows: ``{"id", "exists", "name", "category", "dimensions_api_mm", "polycount"}``.
    """
    listing = polyhaven.list_assets("models")
    rows = []
    for asset_id in ids:
        record = listing.get(asset_id)
        rows.append({"id": asset_id, "exists": record is not None, "name": (record or {}).get("name"),
                     "category": (record or {}).get("category"),
                     "dimensions_api_mm": (record or {}).get("dimensions"),
                     "polycount": (record or {}).get("polycount")})
    return rows


def api_dimensions_match(entry: dict, tolerance: float = 0.02) -> bool:
    """True when the measured bbox agrees with the API ``dimensions`` (mm) within ``tolerance`` metres."""
    dims = entry.get("dimensions_api_mm")
    if not dims or len(dims) < 3:
        return False
    return all(abs(entry["bbox_m"][i] - dims[i] / 1000.0) <= tolerance for i in range(3))


def total_size_bytes(assets_dir: Path, ids: Optional[Iterable[str]] = None) -> int:
    """Bytes on disk of the manifest's model files (all, or only ``ids``)."""
    manifest = fetch.load_manifest(Path(assets_dir))
    models = manifest.get("models", {})
    total = 0
    for asset_id, entry in models.items():
        if ids is not None and asset_id not in set(ids):
            continue
        for rel in entry.get("files", {}).values():
            path = Path(assets_dir) / rel
            if path.is_file():
                total += path.stat().st_size
    return total


def summarise(entry: dict) -> str:
    bbox = entry.get("bbox_m") or [math.nan] * 3
    return (f"{entry['id']:<28} {bbox[0]:5.3f} x {bbox[1]:5.3f} x {bbox[2]:5.3f} m  "
            f"{entry.get('vertices', '?'):>7} verts  {entry.get('licence')}  {entry['files'].get('gltf', '')}")
