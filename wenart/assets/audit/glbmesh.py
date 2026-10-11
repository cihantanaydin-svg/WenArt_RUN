"""Read a glTF or GLB model with numpy, without Blender (docs/milestone12.md §6.4, pod P4: library growth).

What: ``measure(path)`` -> the box of the model in the Z-up frame of Blender's glTF importer (metres times
``unit_scale``), the vertex and triangle counts, the texture use and the raw numbers of the geometric front check
(``front_stats``, the same dict as ``wenart.assets.objaverse.front_stats``, computed with numpy).

Why: the catalogue entries of the new models (box, ``origin_offset``, front) are needed before the audit render
measures them in Blender (``render.py`` takes the catalogue box for its layout and checks the pivot against the
measured box, 1 cm). ``wenart.assets.models.measure_gltf`` reads ``.gltf`` files only and loops in Python (too slow
for ABO GLBs with 10^5-10^6 vertices).

How: the scene graph of every scene (``models._node_matrices``: node TRS or matrix, parents first), every primitive's
``POSITION`` accessor (float or normalized integers, ``byteStride``, sparse values) transformed by its node's world
matrix, then glTF Y-up -> Blender Z-up: ``(x, y, z) -> (x, -z, y)`` (as the importer and ``measure_gltf``).
Triangles from the index accessor (or the implicit order) for modes 4, 5 and 6; points and lines count for the box
only. Draco / meshopt compressed primitives raise ``MeshError`` (the importer would decode them; no growth source
uses them). Pure: no network, no Blender.
"""
from __future__ import annotations

import base64
import json
import struct
from pathlib import Path
from typing import Optional

import numpy as np

GLB_MAGIC = 0x46546C67           # "glTF"
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
COMPONENT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NORMALIZED = {5120: 127.0, 5121: 255.0, 5122: 32767.0, 5123: 65535.0}
TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
COMPRESSION = ("KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_meshopt_compression")
SIDES = ("-x", "+x", "-y", "+y")


class MeshError(ValueError):
    """The file is no readable glTF 2.0 / GLB, or its geometry cannot be read without a decoder."""


# --------------------------------------------------------------------------
# Container
# --------------------------------------------------------------------------

def read(path) -> tuple[dict, list]:
    """``(gltf json, [buffer bytes])`` of a ``.glb`` (the BIN chunk is the buffer without ``uri``) or a ``.gltf``
    (external ``.bin`` files next to it, or data URIs)."""
    path = Path(path)
    data = path.read_bytes()
    if data[:4] == b"glTF":
        if len(data) < 20:
            raise MeshError(f"{path.name}: shorter than a GLB header")
        magic, version, _length = struct.unpack_from("<III", data, 0)
        if magic != GLB_MAGIC or version != 2:
            raise MeshError(f"{path.name}: GLB version {version}, expected 2")
        off, doc, binary = 12, None, None
        while off + 8 <= len(data):
            clen, ctype = struct.unpack_from("<II", data, off)
            chunk = data[off + 8:off + 8 + clen]
            if ctype == CHUNK_JSON and doc is None:
                doc = json.loads(chunk.decode("utf-8"))
            elif ctype == CHUNK_BIN and binary is None:
                binary = chunk
            off += 8 + clen + (-clen % 4 if clen % 4 else 0)
        if doc is None:
            raise MeshError(f"{path.name}: GLB without a JSON chunk")
    else:
        try:
            doc = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise MeshError(f"{path.name}: neither GLB nor glTF JSON ({exc})") from exc
        binary = None
    buffers = []
    for buf in doc.get("buffers") or []:
        uri = buf.get("uri")
        if uri is None:
            if binary is None:
                raise MeshError(f"{path.name}: a buffer without uri and no GLB BIN chunk")
            buffers.append(binary)
        elif uri.startswith("data:"):
            buffers.append(base64.b64decode(uri.split(",", 1)[1]))
        else:
            rel = Path(uri)
            if rel.is_absolute() or ".." in rel.parts:
                raise MeshError(f"{path.name}: buffer uri {uri!r} leaves the model folder")
            p = path.parent / rel
            if not p.is_file():
                raise MeshError(f"{path.name}: buffer {uri} missing")
            buffers.append(p.read_bytes())
    return doc, buffers


def accessor(doc: dict, buffers: list, index: int, as_float: bool = True) -> np.ndarray:
    """The values of one accessor as an ``(count, n)`` array (normalized integers scaled to -1..1 / 0..1 when
    ``as_float``; sparse values applied)."""
    acc = doc["accessors"][index]
    ctype, n, count = acc["componentType"], TYPE_COUNT[acc["type"]], int(acc["count"])
    dtype = np.dtype(COMPONENT[ctype]).newbyteorder("<")
    if "bufferView" in acc:
        view = doc["bufferViews"][acc["bufferView"]]
        if any(k in (view.get("extensions") or {}) for k in COMPRESSION):
            raise MeshError("meshopt-compressed buffer view (no decoder here)")
        data = buffers[view["buffer"]]
        start = int(view.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
        item = dtype.itemsize * n
        stride = int(view.get("byteStride") or item)
        if count and start + stride * (count - 1) + item > len(data):
            raise MeshError(f"accessor {index} runs past its buffer")
        raw = np.frombuffer(data, dtype=np.uint8, count=stride * (count - 1) + item if count else 0, offset=start)
        if stride == item:
            arr = raw.view(dtype).reshape(count, n).copy()
        else:
            rows = np.lib.stride_tricks.as_strided(raw, shape=(count, item), strides=(stride, 1))
            arr = np.ascontiguousarray(rows).view(dtype).reshape(count, n)
    else:
        arr = np.zeros((count, n), dtype=dtype)
    sparse = acc.get("sparse")
    if sparse:
        k = int(sparse["count"])
        iacc = sparse["indices"]
        iview = doc["bufferViews"][iacc["bufferView"]]
        idt = np.dtype(COMPONENT[iacc["componentType"]]).newbyteorder("<")
        idx = np.frombuffer(buffers[iview["buffer"]], dtype=idt, count=k,
                            offset=int(iview.get("byteOffset", 0)) + int(iacc.get("byteOffset", 0)))
        vacc = sparse["values"]
        vview = doc["bufferViews"][vacc["bufferView"]]
        vals = np.frombuffer(buffers[vview["buffer"]], dtype=dtype, count=k * n,
                             offset=int(vview.get("byteOffset", 0)) + int(vacc.get("byteOffset", 0))).reshape(k, n)
        arr = arr.copy()
        arr[idx.astype(np.int64)] = vals
    if not as_float:
        return arr
    out = arr.astype(np.float64)
    if acc.get("normalized") and ctype in NORMALIZED:
        out = np.maximum(out / NORMALIZED[ctype], -1.0)
    return out


def _triangles(mode: int, idx: np.ndarray) -> np.ndarray:
    if mode == 4:
        n = len(idx) - len(idx) % 3
        return idx[:n].reshape(-1, 3)
    if mode == 5 and len(idx) >= 3:                       # strip: every other triangle flipped
        t = np.stack([idx[:-2], idx[1:-1], idx[2:]], axis=1)
        odd = np.arange(len(t)) % 2 == 1
        t[odd] = t[odd][:, [1, 0, 2]]
        return t
    if mode == 6 and len(idx) >= 3:                       # fan
        return np.stack([np.full(len(idx) - 2, idx[0]), idx[1:-1], idx[2:]], axis=1)
    return np.zeros((0, 3), dtype=np.int64)


def mesh_arrays(doc: dict, buffers: list) -> tuple[np.ndarray, np.ndarray]:
    """``(vertices (N, 3) in the Z-up importer frame, triangles (M, 3))`` of every mesh node of every scene."""
    from wenart.assets.models import _node_matrices
    meshes = doc.get("meshes") or []
    verts, tris, offset = [], [], 0
    for index, world in _node_matrices(doc):
        node = doc["nodes"][index]
        if "mesh" not in node:
            continue
        m = np.array(world, dtype=np.float64).reshape(4, 4).T          # column-major -> row-major
        for prim in meshes[node["mesh"]].get("primitives") or []:
            if any(k in (prim.get("extensions") or {}) for k in COMPRESSION):
                raise MeshError("Draco-compressed primitive (no decoder here)")
            attrs = prim.get("attributes") or {}
            if "POSITION" not in attrs:
                continue
            pos = accessor(doc, buffers, attrs["POSITION"])[:, :3]
            pos = pos @ m[:3, :3].T + m[:3, 3]
            pos = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], axis=1)     # glTF Y-up -> Blender Z-up
            mode = int(prim.get("mode", 4))
            if "indices" in prim:
                idx = accessor(doc, buffers, prim["indices"], as_float=False).reshape(-1).astype(np.int64)
            else:
                idx = np.arange(len(pos), dtype=np.int64)
            t = _triangles(mode, idx)
            if len(t) and (t.min() < 0 or t.max() >= len(pos)):
                raise MeshError("an index points past its vertices")
            verts.append(pos)
            tris.append(t + offset)
            offset += len(pos)
    if not verts:
        raise MeshError("no mesh positions found")
    return np.concatenate(verts), np.concatenate(tris) if tris else np.zeros((0, 3), dtype=np.int64)


def _uses_texture(value) -> bool:
    if isinstance(value, dict):
        return any((k.endswith("Texture") and isinstance(v, dict) and "index" in v) or _uses_texture(v)
                   for k, v in value.items())
    if isinstance(value, list):
        return any(_uses_texture(v) for v in value)
    return False


def info(doc: dict) -> dict:
    """Counts of the glTF JSON: images, materials, meshes, primitives, ``textured`` (an image a material uses),
    ``vertex_colours`` (a primitive with ``COLOR_0``), the extensions required."""
    meshes = doc.get("meshes") or []
    prims = [p for m in meshes for p in (m.get("primitives") or [])]
    materials = doc.get("materials") or []
    images = len(doc.get("images") or [])
    return {"images": images, "materials": len(materials), "meshes": len(meshes), "primitives": len(prims),
            "textured": bool(images and (doc.get("textures") or []) and any(_uses_texture(m) for m in materials)),
            "vertex_colours": any("COLOR_0" in (p.get("attributes") or {}) for p in prims),
            "extensions_required": sorted(doc.get("extensionsRequired") or [])}


# --------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------

def front_stats(verts: np.ndarray, tris: np.ndarray, top_fraction: float = 0.3, side_fraction: float = 0.05,
                normal_dot: float = 0.9) -> dict:
    """``wenart.assets.objaverse.front_stats`` with numpy: the top centroid (normalised by the extents), the vertex
    counts near each side and the closed panel fraction of each side (triangles as the polygons)."""
    mins, maxs = verts.min(axis=0), verts.max(axis=0)
    ext = maxs - mins
    centre = (mins + maxs) / 2.0
    top = verts[verts[:, 2] >= mins[2] + (1.0 - top_fraction) * ext[2]]
    if not len(top):
        top = verts
    tc = top[:, :2].mean(axis=0) - centre[:2]
    top_n = [float(tc[i] / ext[i]) if ext[i] > 0 else 0.0 for i in range(2)]
    tol = side_fraction * ext
    counts = {"-x": int((verts[:, 0] <= mins[0] + tol[0]).sum()), "+x": int((verts[:, 0] >= maxs[0] - tol[0]).sum()),
              "-y": int((verts[:, 1] <= mins[1] + tol[1]).sum()), "+y": int((verts[:, 1] >= maxs[1] - tol[1]).sum())}
    panel = {s: 0.0 for s in SIDES}
    if len(tris):
        t = verts[tris]
        c = t.mean(axis=1)
        cr = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        length = np.linalg.norm(cr, axis=1)
        area = 0.5 * length
        nrm = np.divide(cr, length[:, None], out=np.zeros_like(cr), where=length[:, None] > 0)
        face_x, face_y = ext[1] * ext[2], ext[0] * ext[2]
        for s, axis, sel in (("-x", 0, (c[:, 0] <= mins[0] + tol[0]) & (nrm[:, 0] <= -normal_dot)),
                             ("+x", 0, (c[:, 0] >= maxs[0] - tol[0]) & (nrm[:, 0] >= normal_dot)),
                             ("-y", 1, (c[:, 1] <= mins[1] + tol[1]) & (nrm[:, 1] <= -normal_dot)),
                             ("+y", 1, (c[:, 1] >= maxs[1] - tol[1]) & (nrm[:, 1] >= normal_dot))):
            face = face_x if axis == 0 else face_y
            panel[s] = round(float(area[sel].sum() / face), 4) if face > 0 else 0.0
    return {"bbox_min": [float(v) for v in mins], "bbox_max": [float(v) for v in maxs],
            "extents": [float(v) for v in ext], "vertices": int(len(verts)), "polygons": int(len(tris)),
            "top_centroid_n": [round(v, 4) for v in top_n], "side_counts": counts, "panel_fraction": panel}


def measure(path, unit_scale: float = 1.0, rules: Optional[dict] = None) -> dict:
    """The box (``bbox_min_m``, ``bbox_max_m``, ``bbox_model_m``: metres in the importer's Z-up frame, times
    ``unit_scale``), ``vertices``, ``triangles``, ``info`` and ``stats`` (``front_stats`` with the fractions of
    ``rules`` = ``objaverse.yaml front_rules``) of one model file; the arrays stay out of the result."""
    doc, buffers = read(path)
    verts, tris = mesh_arrays(doc, buffers)
    verts = verts * float(unit_scale)
    r = rules or {}
    stats = front_stats(verts, tris, float(r.get("top_fraction", 0.3)), float(r.get("side_fraction", 0.05)),
                        float((r.get("open_side") or {}).get("normal_dot", 0.9)))
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    return {"bbox_min_m": [round(float(v), 4) + 0.0 for v in mn], "bbox_max_m": [round(float(v), 4) + 0.0 for v in mx],
            "bbox_model_m": [round(float(b - a), 4) for a, b in zip(mn, mx)], "vertices": int(len(verts)),
            "triangles": int(len(tris)), "info": info(doc), "stats": stats}


def triangles_of(path, unit_scale: float = 1.0) -> np.ndarray:
    """The triangles of a model as an ``(M, 3, 3)`` array of world vertices (the footprint of a corner sofa)."""
    doc, buffers = read(path)
    verts, tris = mesh_arrays(doc, buffers)
    return (verts * float(unit_scale))[tris]
