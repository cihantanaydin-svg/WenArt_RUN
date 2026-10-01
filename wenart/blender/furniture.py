"""Furniture objects for the scene (docs/milestone4.md §2): fitted library
glTF assets on the drawn footprints, parametric meshes as the fallback, the
Milestone 3 proxy box for ``unknown`` pieces and behind ``--proxies``, and
decor items on their host pieces.

Per piece of ``building.furniture`` on the level:

- ``asset`` with ``method: library`` and a readable, CC0 glTF/GLB file ->
  the file is imported (``bpy.ops.import_scene.gltf``), its meshes merged
  into one object, re-oriented from the catalogue frame (``front_axis``,
  ``up_axis``) into the piece frame (width X, depth Y, front -Y, Z up),
  re-centred so the bounding box centre sits on the footprint centre and
  its bottom on the floor, scaled by ``fit_scale``, rotated by
  ``footprint.rotation_deg`` and placed at ``footprint.center`` on the
  floor of the level. The asset's own materials are kept.
- otherwise -> the parametric mesh of ``wenart.blender.parametric`` with
  materials from the style, and the manifest says why
  (``method: "parametric (fallback: <reason>)"``).
- ``type == "unknown"`` (and every piece with ``use_proxies``) -> the
  Milestone 3 proxy box of ``wenart.blender.proxies`` (name ``proxy_<id>``,
  kind ``furniture_proxy``, pass index key ``proxy:<id>``), unchanged.

Objects are named ``furn_<id>`` with ``wenart_id = <id>``, ``wenart_kind =
furniture``, ``wenart_status``, ``wenart_source`` (from_documents /
added_by_ai), ``wenart_asset`` (asset id or ``parametric``) and
``wenart_type``. Unverified pieces get the red emission stripes as an
overlay on every material. Each piece has one pass index (``pass_indices[
<id>]``); its decor shares the index and the ``wenart_id``, like a door's
frame and leaf (``decor_<host id>_<n>``, kind ``decor``).

Nothing is moved: footprint centre, size and rotation are taken from the
JSON as they are; a fitted asset whose box does not match the footprint
within 1 cm after the fit is reported as a warning, never adjusted.

The glTF importer of Blender 5.2.2 (checked with ``get_rna_type``):
``filepath``, ``import_shading`` (NORMALS/FLAT/SMOOTH), ``merge_vertices``,
``import_pack_images``, ``import_scene_as_collection`` (default True: a new
collection per file; set False here, the objects are re-linked into the
level collection), ``import_select_created_objects``. glTF files are Y-up
and the importer converts them to Blender's Z-up, so ``front_axis`` /
``up_axis`` of the catalogue are read in the imported (Z-up) frame.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from wenart import geometry as G
from wenart.blender import parametric as P
from wenart.blender import proxies
from wenart.blender.proxies import COINCIDENT_LIFT, footprints_overlap, proxy_height

CC0 = "CC0"
LIBRARIES = ("polyhaven", "parametric")
# A fitted box may differ from the footprint by this much before a warning.
FIT_TOLERANCE_M = 0.01
AXES = {"+X": (1.0, 0.0, 0.0), "-X": (-1.0, 0.0, 0.0), "+Y": (0.0, 1.0, 0.0), "-Y": (0.0, -1.0, 0.0),
        "+Z": (0.0, 0.0, 1.0), "-Z": (0.0, 0.0, -1.0)}
PIECE_FRONT = (0.0, -1.0, 0.0)
PIECE_UP = (0.0, 0.0, 1.0)


# --------------------------------------------------------------------------
# Pure helpers (no bpy): asset resolution, frame rotation, fitting maths
# --------------------------------------------------------------------------

def asset_licence(asset: dict) -> str | None:
    return asset.get("licence", asset.get("license"))


def resolve_asset(asset: dict | None, assets_dir: str | None) -> tuple[Path | None, str | None]:
    """``(file, reason)``: the glTF/GLB file of a fitted library asset, or
    None and why the parametric fallback is used (docs/milestone4.md §2:
    missing ``asset`` or missing file -> parametric)."""
    if not asset:
        return None, "no asset in the building JSON"
    method = asset.get("method") or ("library" if asset.get("file") or asset.get("asset_id") else None)
    if method == "parametric" or asset.get("library") == "parametric":
        return None, "fitting chose the parametric mesh"
    if method != "library":
        return None, f"asset method {method!r} is not 'library'"
    licence = asset_licence(asset)
    if str(licence or "").strip().upper() != CC0:
        return None, f"asset {asset.get('asset_id')!r} licence {licence!r} is not {CC0}; refused"
    file = asset.get("file")
    candidates: list[Path] = []
    if file:
        p = Path(file)
        if not p.is_absolute() and assets_dir:
            p = Path(assets_dir) / p
        candidates.append(p)
    elif asset.get("asset_id") and assets_dir:
        base = Path(assets_dir) / "models" / str(asset["asset_id"])
        candidates += [base / f"{asset['asset_id']}.gltf", base / f"{asset['asset_id']}.glb"]
    for p in candidates:
        if p.is_file():
            return p, None
    if not candidates:
        return None, f"asset {asset.get('asset_id')!r} has no file and no assets dir to look in"
    return None, f"asset file missing: {candidates[0]}"


def frame_rotation(front_axis: str | None, up_axis: str | None) -> list[list[float]]:
    """3x3 rotation that turns the asset's ``front_axis`` into the piece
    front (-Y) and its ``up_axis`` into +Z (row-major, applied as R @ v)."""
    f = AXES[(front_axis or "-Y").upper()]
    u = AXES[(up_axis or "+Z").upper()]
    if abs(_dot(f, u)) > 1e-9:
        raise ValueError(f"front_axis {front_axis!r} and up_axis {up_axis!r} are not perpendicular")
    src = (f, u, _cross(f, u))
    dst = (PIECE_FRONT, PIECE_UP, _cross(PIECE_FRONT, PIECE_UP))
    # R = D @ S^T with S = [f u f×u] and D = [-Y +Z (-Y)×(+Z)] as columns.
    return [[sum(dst[k][i] * src[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b) -> tuple[float, float, float]:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def apply_rotation(R: Sequence[Sequence[float]], v: Sequence[float]) -> tuple[float, float, float]:
    return tuple(R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2] for i in range(3))


def fit_vertices(verts: Sequence[Sequence[float]], asset: dict, footprint: dict, floor_z: float,
                 target_size: Sequence[float] | None = None) -> tuple[list, dict]:
    """Asset-frame vertices -> world vertices on the footprint.

    Steps: rotate into the piece frame, re-centre (XY box centre to the
    origin, bottom to z = 0), scale by ``fit_scale`` (or to ``target_size``
    for decor), rotate by ``footprint.rotation_deg`` and move to
    ``footprint.center`` at ``floor_z``. Returns the vertices and a record
    with the measured boxes before and after the fit, the offsets applied
    and the scale used."""
    R = frame_rotation(asset.get("front_axis"), asset.get("up_axis"))
    local = [apply_rotation(R, v) for v in verts]
    x0, y0, z0, x1, y1, z1 = _bounds(local)
    raw_bbox = [x1 - x0, y1 - y0, z1 - z0]
    offset = (-(x0 + x1) / 2.0, -(y0 + y1) / 2.0, -z0)
    local = [(x + offset[0], y + offset[1], z + offset[2]) for x, y, z in local]
    if target_size is not None:
        sx = float(target_size[0]) / raw_bbox[0] if raw_bbox[0] > 1e-9 else 1.0
        sy = float(target_size[1]) / raw_bbox[1] if raw_bbox[1] > 1e-9 else 1.0
        if len(target_size) > 2 and target_size[2]:
            sz = float(target_size[2]) / raw_bbox[2] if raw_bbox[2] > 1e-9 else 1.0
        else:
            sz = (sx + sy) / 2.0
        scale = [sx, sy, sz]
    else:
        scale = [float(v) for v in (list(asset.get("fit_scale") or [1.0, 1.0, 1.0]) + [1.0, 1.0, 1.0])[:3]]
    local = [(x * scale[0], y * scale[1], z * scale[2]) for x, y, z in local]
    fx0, fy0, fz0, fx1, fy1, fz1 = _bounds(local)
    fitted = [fx1 - fx0, fy1 - fy0, fz1 - fz0]
    rot = float(footprint["rotation_deg"])
    rad = math.radians(rot)
    c, s = math.cos(rad), math.sin(rad)
    cx, cy = float(footprint["center"][0]), float(footprint["center"][1])
    world = [(cx + c * x - s * y, cy + s * x + c * y, floor_z + z) for x, y, z in local]
    info = {
        "front_axis": asset.get("front_axis") or "-Y", "up_axis": asset.get("up_axis") or "+Z",
        "origin_offset_catalog": asset.get("origin_offset"),
        "origin_offset_applied": [round(v, 4) for v in offset],
        "bbox_raw_m": [round(v, 4) for v in raw_bbox], "bbox_m": [round(v, 4) for v in fitted],
        "fit_scale": [round(v, 4) for v in scale],
    }
    return world, info


def _bounds(points) -> tuple[float, float, float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def style_material_keys(style: dict) -> tuple[dict, list[dict]]:
    """Map the parametric material keys to ``(slug, asset_id, tint)`` from
    the style: wood from the floor when it is wood (textured when the floor
    is), fabric from the ``textiles`` slot (the Milestone 3 profile has none:
    ``DEFAULT_TEXTILE_MATERIAL``, recorded as assumed), painted fronts from
    the trim, and fixed slugs for bedding, ceramic, steel, worktop, dark
    lacquer, plant green and terracotta. Returns ``(keys, assumed)``."""
    try:
        from wenart.style import vocabulary as V
        materials, default_textile = V.MATERIALS, V.DEFAULT_TEXTILE_MATERIAL
    except Exception:  # noqa: BLE001 - the local fallback of materials.py applies
        materials, default_textile = {}, "fabric_linen"
    assumed: list[dict] = []
    floor = style.get("floor") or {}
    floor_slug = floor.get("material")
    if floor_slug and materials.get(floor_slug, {}).get("kind") == "wood":
        wood = (floor_slug, floor.get("asset"), None)
    else:
        wood = ("wood_oak_light", None, None)
        assumed.append({"object": "furniture", "field": "wood", "value": "wood_oak_light",
                        "reason": f"style floor {floor_slug!r} is not wood; default wood for furniture frames"})
    textiles = style.get("textiles") or {}
    if textiles.get("material"):
        fabric = (textiles["material"], textiles.get("asset"), textiles.get("tint"))
    else:
        fabric = (default_textile, None, None)
        assumed.append({"object": "furniture", "field": "fabric", "value": default_textile,
                        "reason": "style profile has no textiles slot; default fabric for sofas and chairs"})
    trim = (style.get("trim") or {}).get("material") or "painted_wood_white"
    keys = {
        "wood": wood, "fabric": fabric, "painted": (trim, None, None),
        "bedding": ("fabric_white", None, None), "ceramic": ("ceramic_white", None, None),
        "steel": ("steel_brushed", None, None), "worktop": ("stone_worktop", None, None),
        "dark": ("lacquer_dark", None, None), "green": ("plant_green", None, None),
        "terracotta": ("terracotta", None, None), "glass": ("glass", None, None),
    }
    return keys, assumed


def collect_decor(building: dict, level_id: str) -> list[tuple[dict, dict]]:
    """``(decor item, host piece)`` pairs for a level: the top-level
    ``building.decor`` list (by ``host_id``) and per-piece ``decor`` lists.
    Items whose host is unknown or on another level are left out (the
    caller warns about unknown hosts via ``unknown_decor_hosts``)."""
    pieces = {p["id"]: p for p in building.get("furniture", [])}
    out = []
    for item in building.get("decor") or []:
        host = pieces.get(item.get("host_id"))
        if host is not None and host["level_id"] == level_id:
            out.append((item, host))
    for piece in building.get("furniture", []):
        if piece["level_id"] != level_id:
            continue
        for item in piece.get("decor") or []:
            out.append((dict(item, host_id=piece["id"]), piece))
    return out


def unknown_decor_hosts(building: dict) -> list[str]:
    pieces = {p["id"] for p in building.get("furniture", [])}
    return [str(item.get("host_id")) for item in building.get("decor") or [] if item.get("host_id") not in pieces]


def decor_height_above_floor(item: dict, host: dict) -> tuple[float, str]:
    """Rest height of a decor item: its own ``center[2]`` when given, else
    the host's seat / mattress / shelf / top (``parametric.decor_rest_height``)."""
    center = item.get("center") or []
    if len(center) > 2 and center[2] is not None:
        return float(center[2]), "center[2]"
    host_h, _ = proxy_height(host["type"], host.get("height"))
    return P.decor_rest_height(host["type"], host_h, item["type"]), f"on {host['type']} {host['id']}"


# --------------------------------------------------------------------------
# bpy: import, merge, objects
# --------------------------------------------------------------------------

def import_gltf_geometry(path: Path, collection) -> dict:
    """Import a glTF/GLB and return its merged geometry in the file's
    (Z-up) frame: ``{"verts", "faces", "materials", "face_materials", "uvs",
    "uv_name", "objects"}``. The imported objects are deleted again; the
    materials (and packed images) stay in ``bpy.data`` for the new object."""
    import bpy

    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=str(path), import_shading="NORMALS", import_scene_as_collection=False,
                              import_select_created_objects=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    for ob in new:
        for col in list(ob.users_collection):
            col.objects.unlink(ob)
        collection.objects.link(ob)
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    for ob in meshes:  # keep world transforms, drop the parents
        mw = ob.matrix_world.copy()
        ob.parent = None
        ob.matrix_world = mw
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts, faces, materials, face_materials, uvs = [], [], [], [], []
    uv_name = None
    for ob in meshes:
        ev = ob.evaluated_get(depsgraph)
        me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=depsgraph)
        mw = ob.matrix_world
        offset = len(verts)
        verts.extend([tuple(mw @ v.co) for v in me.vertices])
        slot_map = []
        for mat in me.materials:
            if mat is None:
                slot_map.append(None)
                continue
            if mat not in materials:
                materials.append(mat)
            slot_map.append(materials.index(mat))
        layer = me.uv_layers.active
        if layer is not None and uv_name is None:
            uv_name = layer.name
        for poly in me.polygons:
            faces.append([offset + me.loops[li].vertex_index for li in poly.loop_indices])
            slot = slot_map[poly.material_index] if poly.material_index < len(slot_map) else None
            face_materials.append(slot)
            uvs.append([tuple(layer.data[li].uv) for li in poly.loop_indices] if layer is not None else None)
        bpy.data.meshes.remove(me)
    names = [o.name for o in new]
    for ob in new:
        _delete_object(ob)
    return {"verts": verts, "faces": faces, "materials": materials, "face_materials": face_materials,
            "uvs": uvs, "uv_name": uv_name or "UVMap", "objects": names}


def _cached_geometry(path: Path, collection, geo_cache: dict) -> dict:
    """``import_gltf_geometry`` once per file and build: pieces that share an
    asset share its materials and packed images instead of importing it
    again (the importer makes ``name.001`` material copies otherwise)."""
    key = str(path.resolve())
    if key not in geo_cache:
        geo_cache[key] = import_gltf_geometry(path, collection)
    return geo_cache[key]


def _delete_object(ob) -> None:
    from wenart.blender import common

    for child in list(ob.children):
        child.parent = None
    common.delete_object(ob)


def _material_is_textured(mat) -> bool:
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return False
    return any(n.bl_idname == "ShaderNodeTexImage" and n.image is not None for n in mat.node_tree.nodes)


def _unverified_copies(materials_list: list, cache: dict) -> list:
    """Copies of the asset materials with the red stripes mixed over the
    surface shader (the overlay of docs/milestone4.md §2)."""
    from wenart.blender.materials import add_unverified_overlay

    out = []
    for mat in materials_list:
        if mat is None:
            out.append(None)
            continue
        if mat.name not in cache:
            copy = mat.copy()
            copy.name = f"{mat.name}__unverified"
            add_unverified_overlay(copy)
            cache[mat.name] = copy
        out.append(cache[mat.name])
    return out


def _mesh_object(name: str, verts, faces, materials_list, face_materials, collection, wenart_id, kind, status,
                 uvs=None, uv_name: str | None = None, fallback_material=None):
    """Mesh object from world geometry with per-face materials; empty slots
    get ``fallback_material``; asset UVs (when given) become the active
    layer and ``box_m`` stays as a second layer."""
    from wenart.blender import common

    slots = [m if m is not None else fallback_material for m in materials_list]
    if not slots:
        slots = [fallback_material]
    indices = [i if i is not None else len(slots) - 1 for i in face_materials]
    if any(i is None for i in face_materials) and fallback_material not in slots:
        slots.append(fallback_material)
        indices = [i if i is not None else len(slots) - 1 for i in face_materials]
    ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=wenart_id, kind=kind,
                                status=status, materials=slots, face_material_indices=indices)
    if uvs is not None and any(u is not None for u in uvs):
        mesh = ob.data
        layer = mesh.uv_layers.new(name=uv_name or "UVMap")
        for poly, uv in zip(mesh.polygons, uvs):
            if uv is None:
                continue
            for li, co in zip(poly.loop_indices, uv):
                layer.data[li].uv = co
        mesh.uv_layers.active = layer
    return ob


class _Materials:
    """Style materials per parametric key, cached per (key, unverified)."""

    def __init__(self, library, style: dict, assumed: list):
        self.library = library
        self.keys, extra = style_material_keys(style)
        assumed.extend(extra)
        self._cache: dict = {}

    def get(self, key: str, unverified: bool = False):
        ck = (key, unverified)
        if ck in self._cache:
            return self._cache[ck]
        slug, asset, tint = self.keys[key]
        if asset and self.library.texture_set(asset)[0] is None:
            asset = None  # no usable texture: share the flat material of the same slug
        if slug == "glass":
            mat = self.library.glass()
        else:
            mat = self.library.get(slug, asset, tint, unverified=unverified)
        self._cache[ck] = mat
        return mat

    def slug(self, key: str) -> str:
        return self.keys[key][0]


def create_furniture(building: dict, level: dict, collection, library, style: dict, assets_dir: str | None,
                     pass_indices: dict, manifest_objects: list, assumed: list, warnings: list,
                     use_proxies: bool = False) -> dict:
    """Create the furniture and decor objects of ``level``; returns a
    summary for the manifest (``pieces``, ``by_method``, ``fallbacks``,
    ``proxies``, ``decor``)."""
    floor_z = float(level["elevation"])
    mats = _Materials(library, style, assumed)
    pieces = [p for p in building.get("furniture", []) if p["level_id"] == level["id"]]
    proxy_pieces = [p for p in pieces if use_proxies or p["type"] == "unknown" or p["type"] not in P.PARAMETRIC_TYPES]
    for p in proxy_pieces:
        if p["type"] != "unknown" and not use_proxies:
            warnings.append(f"{p['id']}: furniture type {p['type']!r} has no parametric builder; proxy box used")
    summary = {"pieces": len(pieces), "by_method": {}, "fallbacks": [], "proxies": len(proxy_pieces), "decor": 0,
               "proxies_forced": bool(use_proxies)}
    if proxy_pieces:
        proxies.create_proxies({"furniture": proxy_pieces}, level, collection, {
            "proxy": library.proxy("proxy"), "proxy_glass": library.proxy("proxy_glass"),
            "proxy_unverified": library.proxy("proxy_unverified")}, pass_indices, manifest_objects, assumed)
        for p in proxy_pieces:
            summary["by_method"]["proxy"] = summary["by_method"].get("proxy", 0) + 1

    entries: dict[str, dict] = {}
    placed: list[tuple[dict, float]] = []
    unverified_cache: dict = {}
    geo_cache: dict = {}  # file -> imported geometry: one import per asset file, materials shared
    proxy_ids = {p["id"] for p in proxy_pieces}
    for piece in pieces:
        height, height_assumed = proxy_height(piece["type"], piece.get("height"))
        lift = 0.0
        for other_fp, other_h in placed:
            if abs(other_h - height) < 1e-3 and footprints_overlap(piece["footprint"], other_fp):
                lift = COINCIDENT_LIFT
                break
        placed.append((piece["footprint"], height))
        if piece["id"] in proxy_ids:
            continue
        entry = _create_piece(piece, level, floor_z, height, height_assumed, lift, collection, library, mats,
                              assets_dir, pass_indices, assumed, warnings, unverified_cache, geo_cache)
        manifest_objects.append(entry)
        entries[piece["id"]] = entry
        method = "library" if entry["method"] == "library" else "parametric"
        summary["by_method"][method] = summary["by_method"].get(method, 0) + 1
        if entry["fallback_reason"]:
            summary["fallbacks"].append({"id": piece["id"], "type": piece["type"], "reason": entry["fallback_reason"]})

    for host_id in unknown_decor_hosts(building):
        if host_id not in {p["id"] for p in building.get("furniture", [])}:
            msg = f"decor host {host_id!r} is not a furniture piece; item skipped"
            if msg not in warnings:
                warnings.append(msg)
    manifest_by_id = {o["wenart_id"]: o for o in manifest_objects if o.get("kind") in ("furniture", "furniture_proxy")}
    for n, (item, host) in enumerate(collect_decor(building, level["id"]), start=1):
        host_entry = entries.get(host["id"]) or manifest_by_id.get(f"proxy:{host['id']}")
        if host_entry is None:
            continue
        entry = _create_decor(item, host, n, level, floor_z, collection, library, mats, assets_dir, pass_indices,
                              host_entry, warnings, geo_cache)
        if entry is None:
            continue
        manifest_objects.append(entry)
        host_entry.setdefault("decor", []).append({"name": entry["name"], "type": entry["type"],
                                                   "method": entry["method"]})
        summary["decor"] += 1
    return summary


def _base_entry(piece: dict, name: str, wenart_id: str, kind: str, status: str, level: dict, index: int) -> dict:
    return {
        "name": name, "wenart_id": wenart_id, "kind": kind, "status": status, "level_id": level["id"],
        "element_id": piece["id"], "room_id": piece.get("room_id"), "type": piece["type"],
        "source": piece.get("source"), "evidence": piece.get("evidence", []), "pass_index": index, "assumed": {},
        "decor": [],
    }


def _create_piece(piece, level, floor_z, height, height_assumed, lift, collection, library, mats, assets_dir,
                  pass_indices, assumed, warnings, unverified_cache, geo_cache) -> dict:
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = float(fp["rotation_deg"])
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    status = piece.get("status", "verified")
    unverified = status == "unverified"
    name = f"furn_{piece['id']}"
    index = len(pass_indices) + 1
    pass_indices[piece["id"]] = index
    entry = _base_entry(piece, name, piece["id"], "furniture", status, level, index)
    entry.update({"center": [cx, cy, floor_z + height / 2.0], "size": [w, d, height], "rotation_deg": rot,
                  "front_deg": None if piece.get("front_deg") is None else float(piece["front_deg"]),
                  "asset": piece.get("asset"), "fit_scale": [1.0, 1.0, 1.0], "method": None, "bbox_m": None,
                  "fallback_reason": None, "materials": [], "material": None, "textured": False})

    file, reason = resolve_asset(piece.get("asset"), assets_dir)
    if file is None and (piece.get("asset") or {}).get("method") == "library":
        warnings.append(f"{piece['id']}: {reason}; parametric mesh used")  # a fit was made but cannot be built
    ob = None
    if file is not None:
        try:
            ob = _library_object(piece, file, name, status, floor_z, collection, library, entry, warnings,
                                 unverified_cache, geo_cache)
        except Exception as exc:  # noqa: BLE001 - a broken file falls back, loudly
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"{piece['id']}: {reason}; parametric mesh used")
            ob = None
    if ob is None:
        ob = _parametric_object(piece, name, status, floor_z, height + lift, collection, mats, entry)
        entry["method"] = f"parametric (fallback: {reason})"
        entry["fallback_reason"] = reason
        if lift:
            entry["assumed"]["height_lift"] = lift
            assumed.append({"object": name, "field": "height_lift", "value": lift,
                            "reason": "footprint overlaps another piece of the same height; "
                                      "lifted so the top faces do not coincide"})
    if height_assumed:
        entry["assumed"]["height"] = height
        assumed.append({"object": name, "field": "height", "value": height,
                        "reason": f"no height in the JSON; type height for {piece['type']}"})
    ob["wenart_type"] = piece["type"]
    ob["wenart_room"] = piece.get("room_id") or ""
    ob["wenart_source"] = piece.get("source") or "from_documents"
    ob["wenart_asset"] = (piece.get("asset") or {}).get("asset_id") if entry["method"] == "library" else "parametric"
    ob.pass_index = index
    return entry


def _library_object(piece, file: Path, name, status, floor_z, collection, library, entry, warnings,
                    unverified_cache, geo_cache):
    asset = piece["asset"]
    geo = _cached_geometry(file, collection, geo_cache)
    if not geo["faces"]:
        raise ValueError("file has no mesh faces")
    verts, info = fit_vertices(geo["verts"], asset, piece["footprint"], floor_z)
    mats_list = geo["materials"]
    if status == "unverified":
        mats_list = _unverified_copies(mats_list, unverified_cache)
    fallback = library.proxy("proxy_unverified" if status == "unverified" else "proxy")
    ob = _mesh_object(name, verts, geo["faces"], mats_list, geo["face_materials"], collection, piece["id"],
                      "furniture", status, uvs=geo["uvs"], uv_name=geo["uv_name"], fallback_material=fallback)
    fp = piece["footprint"]
    for axis, want, got in (("width", float(fp["size"][0]), info["bbox_m"][0]),
                            ("depth", float(fp["size"][1]), info["bbox_m"][1])):
        if abs(want - got) > FIT_TOLERANCE_M:
            warnings.append(f"{piece['id']}: fitted asset {asset.get('asset_id')!r} {axis} {got:.3f} m differs "
                            f"from the footprint {want:.3f} m by more than {FIT_TOLERANCE_M} m (not adjusted)")
    entry.update({"method": "library", "fit_scale": info["fit_scale"], "bbox_m": info["bbox_m"],
                  "fit": info, "file": str(file),
                  "materials": [m.name for m in ob.data.materials if m is not None],
                  "material": ob.data.materials[0].name if ob.data.materials and ob.data.materials[0] else None,
                  "textured": any(_material_is_textured(m) for m in geo["materials"]),
                  "imported_objects": geo["objects"]})
    return ob


def _parametric_object(piece, name, status, floor_z, height, collection, mats, entry):
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    parts = P.build_parts(piece["type"], w, d, height)
    verts, faces, keys = P.world_mesh(parts, fp["center"], float(fp["rotation_deg"]), floor_z)
    unverified = status == "unverified"
    used_keys = sorted(set(keys), key=keys.index)
    slots = [mats.get(k, unverified and k != "glass") for k in used_keys]
    indices = [used_keys.index(k) for k in keys]
    ob = _mesh_object(name, verts, faces, slots, indices, collection, piece["id"], "furniture", status)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    entry.update({"bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)],
                  "materials": [m.name for m in slots], "material": slots[0].name,
                  "textured": any(mats.library.textured(m) for m in slots),
                  "material_keys": {k: mats.slug(k) for k in used_keys}})
    return ob


def _create_decor(item, host, n, level, floor_z, collection, library, mats, assets_dir, pass_indices, host_entry,
                  warnings, geo_cache) -> dict | None:
    dtype = item.get("type")
    if dtype not in P.DECOR_TYPES:
        warnings.append(f"decor on {host['id']}: unknown decor type {dtype!r}; skipped")
        return None
    center = item.get("center") or host["footprint"]["center"]
    rot = float(item.get("rotation_deg", host["footprint"]["rotation_deg"]))
    w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
    size_in = item.get("size") or []
    if any(float(v) > P.DECOR_MAX_M for v in size_in if v):
        warnings.append(f"decor {dtype} on {host['id']}: size {size_in} capped at {P.DECOR_MAX_M} m")
    z_above, z_how = decor_height_above_floor(item, host)
    name = f"decor_{host['id']}_{n}"
    index = pass_indices.get(host["id"]) or pass_indices.get(f"proxy:{host['id']}") or 0
    status = item.get("status") or "assumed"
    if status not in ("verified", "unverified", "assumed"):
        status = "assumed"
    footprint = {"center": [float(center[0]), float(center[1])], "size": [w, d], "rotation_deg": rot}
    entry = {
        "name": name, "wenart_id": host["id"], "kind": "decor", "status": status, "level_id": level["id"],
        "element_id": host["id"], "host_id": host["id"], "room_id": host.get("room_id"), "type": dtype,
        "source": "added_by_ai",
        "evidence": [{"file": "decor", "method": "rule", "confidence": 1.0,
                      "text": f"{dtype} on {host['type']} {host['id']} ({z_how})"}],
        "pass_index": index, "assumed": {"rest_height": z_above} if z_how != "center[2]" else {},
        "center": [footprint["center"][0], footprint["center"][1], floor_z + z_above + h / 2.0],
        "size": [w, d, h], "rotation_deg": rot, "asset": item.get("asset"), "method": None, "bbox_m": None,
        "fit_scale": [1.0, 1.0, 1.0], "materials": [], "material": None, "textured": False, "fallback_reason": None,
    }
    file, reason = resolve_asset(item.get("asset"), assets_dir)
    ob = None
    if file is not None:
        try:
            geo = _cached_geometry(file, collection, geo_cache)
            if not geo["faces"]:
                raise ValueError("file has no mesh faces")
            verts, info = fit_vertices(geo["verts"], item["asset"], footprint, floor_z + z_above,
                                       target_size=[w, d, h] if len(size_in) > 2 else [w, d])
            fallback = library.proxy("proxy")
            ob = _mesh_object(name, verts, geo["faces"], geo["materials"], geo["face_materials"], collection,
                              host["id"], "decor", status, uvs=geo["uvs"], uv_name=geo["uv_name"],
                              fallback_material=fallback)
            entry.update({"method": "library", "fit_scale": info["fit_scale"], "bbox_m": info["bbox_m"], "fit": info,
                          "file": str(file), "materials": [m.name for m in ob.data.materials if m is not None],
                          "material": ob.data.materials[0].name if ob.data.materials else None,
                          "textured": any(_material_is_textured(m) for m in geo["materials"])})
            entry["size"] = [w, d, info["bbox_m"][2]]
            entry["center"][2] = floor_z + z_above + info["bbox_m"][2] / 2.0
        except Exception as exc:  # noqa: BLE001
            reason = f"import of {file} failed: {type(exc).__name__}: {exc}"
            warnings.append(f"decor {dtype} on {host['id']}: {reason}; parametric mesh used")
            ob = None
    if ob is None:
        parts = P.decor_parts(dtype, w, d, h)
        verts, faces, keys = P.world_mesh(parts, footprint["center"], rot, floor_z + z_above)
        used_keys = sorted(set(keys), key=keys.index)
        slots = [mats.get(k) for k in used_keys]
        ob = _mesh_object(name, verts, faces, slots, [used_keys.index(k) for k in keys], collection, host["id"],
                          "decor", status)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        entry.update({"method": f"parametric (fallback: {reason})", "fallback_reason": reason,
                      "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)],
                      "materials": [m.name for m in slots], "material": slots[0].name,
                      "textured": any(mats.library.textured(m) for m in slots)})
    ob["wenart_type"] = dtype
    ob["wenart_room"] = host.get("room_id") or ""
    ob["wenart_source"] = "added_by_ai"
    ob["wenart_host"] = host["id"]
    ob["wenart_asset"] = (item.get("asset") or {}).get("asset_id") if entry["method"] == "library" else "parametric"
    ob.pass_index = index
    return entry
