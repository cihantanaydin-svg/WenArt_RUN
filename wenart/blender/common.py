"""Small bpy helpers shared by the scene builders (runs inside Blender only).

- ``new_mesh_object``: mesh from plain vertex/face lists in world metres,
  with box-projected UVs in metres so one Mapping node (scale 1/size_m) tiles
  every texture at its real size, including tangent-space normal maps, which
  need a UV layer.
- ``set_props``: the three custom properties every WenArt object carries.
- ``evaluated_mesh``: the mesh of an object with its modifiers applied, taken
  from the depsgraph (no operator context needed in background mode).
"""
from __future__ import annotations

from typing import Sequence

from wenart.blender import geom2d

KINDS = ("wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "camera", "light")
STATUSES = ("verified", "unverified", "assumed")


def set_props(ob, wenart_id: str, kind: str, status: str) -> None:
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind}")
    if status not in STATUSES:
        raise ValueError(f"unknown status {status}")
    ob["wenart_id"] = wenart_id
    ob["wenart_kind"] = kind
    ob["wenart_status"] = status


def new_mesh_object(name: str, verts: Sequence, faces: Sequence, *, collection, wenart_id: str,
                    kind: str, status: str, materials: Sequence = (), face_material_indices=None):
    """Create a mesh object at the world origin from world-space geometry."""
    import bpy

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], [list(f) for f in faces])
    mesh.update()
    for mat in materials:
        mesh.materials.append(mat)
    if face_material_indices is not None:
        for poly, idx in zip(mesh.polygons, face_material_indices):
            poly.material_index = idx
    assign_box_uvs(mesh)
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    set_props(ob, wenart_id, kind, status)
    return ob


def assign_box_uvs(mesh, layer_name: str = "box_m") -> None:
    """(Re)write a UV layer with box-projected coordinates in metres."""
    layer = mesh.uv_layers.get(layer_name) or mesh.uv_layers.new(name=layer_name)
    uv_data = layer.data
    verts = mesh.vertices
    loops = mesh.loops
    for poly in mesh.polygons:
        n = tuple(poly.normal)
        for li in poly.loop_indices:
            co = verts[loops[li].vertex_index].co
            uv_data[li].uv = geom2d.box_uv((co.x, co.y, co.z), n)
    if mesh.uv_layers.active != layer:
        mesh.uv_layers.active = layer


def evaluated_mesh(ob):
    """A new mesh datablock with the object's modifiers applied."""
    import bpy

    depsgraph = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=depsgraph)
    return mesh


def replace_mesh(ob, mesh) -> None:
    """Swap the object's mesh and drop the old datablock and all modifiers."""
    import bpy

    old = ob.data
    ob.modifiers.clear()
    ob.data = mesh
    mesh.name = old.name
    if old.users == 0:
        bpy.data.meshes.remove(old)


def delete_object(ob) -> None:
    import bpy

    data = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Camera):
            bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Light):
            bpy.data.lights.remove(data)


def get_or_make_collection(name: str, parent=None):
    import bpy

    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col
