"""The Blender objects of a library door or window (user request of 24 Oct 2026; the plan is
``opening_models.plan``).

What: ``build_library_opening(opening, wall, lib, geo, ctx, mats, op_assumed, shift)`` -> the created objects, or []
when the model cannot be loaded (the caller then builds the parametric opening).

How: the model is imported once per file (``furniture._cached_geometry``), turned into its front frame and scaled
into each of the ``panels`` side by side (``furniture.fit_vertices``: width and height to the panel, depth by the
mean of the two scales, at most the wall less 2 cm), its front facing ``lib.outward``, set ``OUTSIDE_SET_M`` back
from the outer wall face. Its glass materials (``is_glass``) become the scene's window glass (camera-only, so the
sun still lights the rooms); its plain untextured, non-metal materials take the style's frame or leaf look, so the
model keeps its profile and the building keeps its colours; textures and metals stay. Each panel is one object
with the opening's id and pass index; the manifest entry records the asset, the panels and the ``inferred`` reason.
"""
from __future__ import annotations

import math

GLASS_WORDS = ("glass", "glas", "glazing", "pane", "vidro", "vitre", "cam_", "camlar", "transparent", "window_glass")
METAL_WORDS = ("metal", "chrome", "steel", "inox", "alu", "brass", "handle", "knob", "lock", "hinge")
OUTSIDE_SET_M = 0.04
WALL_GAP_M = 0.02


def _principled(mat):
    if mat is None or not getattr(mat, "use_nodes", False) or mat.node_tree is None:
        return None
    return next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)


def _value(node, *names):
    for name in names:
        sock = node.inputs.get(name)
        if sock is not None:
            v = sock.default_value
            return float(v) if not hasattr(v, "__len__") else float(v[3]) if len(v) > 3 else float(v[0])
    return None


def is_glass(mat) -> bool:
    """A model material that is glass: by name, or a principled shader with transmission > 0.5 or alpha < 0.7."""
    if mat is None:
        return False
    name = mat.name.lower()
    if any(w in name for w in GLASS_WORDS):
        return True
    node = _principled(mat)
    if node is None:
        return False
    trans = _value(node, "Transmission Weight", "Transmission")
    alpha = _value(node, "Alpha")
    return (trans is not None and trans > 0.5) or (alpha is not None and alpha < 0.7)


def has_image(mat) -> bool:
    return bool(mat is not None and getattr(mat, "use_nodes", False) and mat.node_tree is not None
                and any(n.type == "TEX_IMAGE" and n.image is not None for n in mat.node_tree.nodes))


def is_metal(mat) -> bool:
    if mat is None:
        return False
    if any(w in mat.name.lower() for w in METAL_WORDS):
        return True
    node = _principled(mat)
    metallic = _value(node, "Metallic") if node is not None else None
    return metallic is not None and metallic > 0.5


def material_map(materials, glass, look):
    """The model's materials as built: glass -> the scene glass; plain (no image, not metal) -> the style look."""
    out = []
    for m in materials:
        if is_glass(m):
            out.append(glass)
        elif look is not None and not has_image(m) and not is_metal(m):
            out.append(look)
        else:
            out.append(m)
    return out


def panel_layout(centre, wall, width: float, panels: int, outward, thickness: float, depth: float):
    """``[(x, y)]``: the plan centres of ``panels`` equal panels across ``width`` on the wall through ``centre``,
    moved outward so the model's outer face sits ``OUTSIDE_SET_M`` inside the outer wall face (pure)."""
    (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    ox, oy = outward
    push = max(0.0, thickness / 2.0 - OUTSIDE_SET_M - depth / 2.0)
    pw = width / panels
    return [(centre[0] + ux * (-width / 2.0 + pw * (i + 0.5)) + ox * push,
             centre[1] + uy * (-width / 2.0 + pw * (i + 0.5)) + oy * push) for i in range(panels)]


def front_rotation_deg(outward) -> float:
    """The footprint rotation that turns the piece front (-Y) to ``outward`` (pure)."""
    return math.degrees(math.atan2(float(outward[0]), -float(outward[1])))


def build_library_opening(opening: dict, wall: dict, lib: dict, geo: dict, ctx: dict, mats: dict,
                          op_assumed: dict, shift: float) -> list:
    from wenart.blender import furniture as F
    from wenart.blender import shell as SH

    warnings = ctx["warnings"]
    path, why = F.resolve_asset(lib.get("asset"), ctx.get("assets_dir"))
    outward = lib.get("outward")
    if path is None or not outward:
        warnings.append(f"{opening['id']}: library {lib.get('category')} not built ({why or 'no outward side'}); "
                        f"parametric opening")
        return []
    try:
        model = F._cached_geometry(path, ctx["collection"], ctx.setdefault("geo_cache", {}))
    except Exception as exc:  # a broken file must never stop the build
        warnings.append(f"{opening['id']}: library model {path.name} failed to load ({exc}); parametric opening")
        return []
    if not model.get("verts") or not model.get("faces"):
        warnings.append(f"{opening['id']}: library model {path.name} has no geometry; parametric opening")
        return []
    asset = lib["asset"]
    panels = max(1, int(lib.get("panels") or 1))
    width, height, thickness = geo["width"], geo["height"], geo["thickness"]
    box = asset.get("bbox_m") or [1.0, 0.1, 1.0]
    mw, md, mh = (float(v) for v in box[:3])
    if str(asset.get("front_axis") or "-Y").upper().endswith("X"):
        mw, md = md, mw
    pw = width / panels
    depth = min(md * (pw / mw + height / mh) / 2.0, max(0.03, thickness - WALL_GAP_M))
    rot = front_rotation_deg(outward)
    kind = "door" if opening["type"] == "door" else "window"
    look = mats.get("leaf") if kind == "door" else mats.get("frame")
    materials = material_map(model["materials"], mats["glass"], look)
    created = []
    for i, (px, py) in enumerate(panel_layout(geo["centre"], wall, width, panels, outward, thickness, depth)):
        verts, info = F.fit_vertices(model["verts"], asset, {"center": [px, py], "size": [pw, depth],
                                                             "rotation_deg": rot}, geo["bottom"],
                                     target_size=[pw, depth, height])
        ob = F._mesh_object(f"{opening['id']}_lib{i}", verts, model["faces"], materials, model["face_materials"],
                            ctx["collection"], opening["id"], kind, geo["status"], uvs=model.get("uvs"),
                            uv_name=model.get("uv_name"), fallback_material=look or mats["glass"])
        ob.pass_index = geo["index"]
        created.append(ob)
        entry = SH._opening_entry(opening, ob.name, geo["level_id"], (look or mats["glass"]).name,
                                  any(has_image(m) for m in materials), geo["index"], op_assumed, shift)
        entry.update(library_model={"asset_id": asset.get("asset_id"), "title": asset.get("title"),
                                    "licence": asset.get("licence"), "licence_flag": asset.get("licence_flag"),
                                    "attribution": asset.get("attribution"), "category": lib.get("category"),
                                    "panel": i, "panels": panels, "fit": info},
                     inferred={"field": "product", "reason": lib.get("reason")})
        ctx["manifest_objects"].append(entry)
    ctx["assumed"].append({"object": opening["id"], "field": "library_model", "value": asset.get("asset_id"),
                           "reason": lib.get("reason"), "parent": opening["id"], "kind": "library_model"})
    return created
