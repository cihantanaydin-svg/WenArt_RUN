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

26 Oct 2026 (user on real06, a Scandinavian house: dark brown and black frames, "a glazed door with a busy
black-and-white triangle lattice in its glass"; "The house needs to make sense and needs to look very stylish"):

- What: every material of the model but its glass and its metal hardware takes the style's finish
  (``material_map`` with ``material_shares``): textured frames and leaves too, and a metal over
  ``HARDWARE_MAX_SHARE`` of the model's surface (an aluminium or steel frame); hardware is a metal named so
  (``HARDWARE_WORDS``) or a small one. A glazed or terrace door takes the windows' frame finish (one frame finish
  for the facade). A face lying on a glass face turned the other way (``glass_twins``: a SketchUp pane exported
  as its glass front and an opaque back of another colour, 0.2 mm apart since ``furniture.separate_twins``) is glass
  too, so the pane is clear from both sides and lets the sun in.
- Why: the model's own colours beat the style (textured materials were kept), so dark frames stood in a white
  house; the doubled pane faces fought in the render (black and white triangles), and after their separation the
  opaque back face would shut the pane from inside.

28 Oct 2026 (user: "I want better doors inside the house and the outside ..."): an inside door's library model
(``opening_models.plan_inside``: ``lib["inside"]``) is centred in its wall (``panel_layout(centred=True)``) with its
front toward the room it opens into (``lib["outward"]``), its leaf in the style's door look like the parametric
inside doors; ``lib["mirror"]`` mirrors it across its panel's centre along the wall (``mirror_across``: the drawn
hinge side) and ``lib["add_handles"]`` (the audit sees no handle on the model) adds the lever pair of the parametric
door (``shell.door_handle_parts``), a design detail with its manifest entry.
"""
from __future__ import annotations

import math
from typing import Optional

GLASS_WORDS = ("glass", "glas", "glazing", "pane", "vidro", "vitre", "cam_", "camlar", "transparent", "translucent",
               "window_glass")
METAL_WORDS = ("metal", "chrome", "steel", "inox", "alu", "brass", "handle", "knob", "lock", "hinge")
HARDWARE_WORDS = ("handle", "knob", "lock", "hinge", "lever", "pull", "bolt", "letter", "hardware", "screw")
HARDWARE_MAX_SHARE = 0.05          # a metal over this share of the model's surface is a frame: it takes the finish
TWIN_TOL_M = 0.001                 # a face this near a glass face, turned the other way, is that pane's back
OUTSIDE_SET_M = 0.04
WALL_GAP_M = 0.02
STRETCH_TOL = 0.30                 # |log(width scale / height scale)| a library fit may carry (opening_models.ASPECT_TOL
                                   # 0.25 plus a margin: the plan's own fit always passes)


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


def is_hardware(mat, share: float | None = None) -> bool:
    """A metal the style's finish leaves as it is: named like hardware (``HARDWARE_WORDS``), or a metal covering at
    most ``HARDWARE_MAX_SHARE`` of the model's surface (``share`` None: every metal, the rule before 26 Oct 2026)."""
    if not is_metal(mat):
        return False
    if any(w in mat.name.lower() for w in HARDWARE_WORDS):
        return True
    return share is None or share <= HARDWARE_MAX_SHARE


def material_map(materials, glass, look, shares=None):
    """The model's materials as built: glass -> the scene glass; metal hardware keeps its own; every other material
    -> the style's ``look`` (26 Oct 2026: textured frames and leaves and large metals too, when ``shares``, the
    ``material_shares`` of the model, are given; without them plain non-metal materials only, as before)."""
    out = []
    for i, m in enumerate(materials):
        share = None if shares is None else (shares[i] if i < len(shares) else 0.0)
        if is_glass(m):
            out.append(glass)
        elif look is None or is_hardware(m, share) or (shares is None and has_image(m)):
            out.append(m)
        else:
            out.append(look)
    return out


def _area_normal(verts, face) -> tuple[float, float, float]:
    """Newell's vector of a polygon: its normal times twice its area."""
    nx = ny = nz = 0.0
    pts = [verts[k] for k in face]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return nx, ny, nz


def material_shares(n_materials: int, verts, faces, face_materials) -> list[float]:
    """The share of the model's surface each material slot covers (pure)."""
    areas = [0.0] * n_materials
    for f, m in zip(faces, face_materials):
        if m is not None and 0 <= m < n_materials:
            areas[m] += math.sqrt(sum(c * c for c in _area_normal(verts, f))) / 2.0
    total = sum(areas)
    return [a / total if total > 0 else 0.0 for a in areas]


def glass_twins(verts, faces, face_glass, tol: float = TWIN_TOL_M) -> set:
    """Indices of the faces that are not glass but lie on a glass face turned the other way (pure): centres within
    ``tol``, normals opposite (dot under -0.9), areas within 25 %: the opaque back of a pane exported twice."""
    info, grid = [], {}
    for i, f in enumerate(faces):
        n = _area_normal(verts, f)
        a = math.sqrt(sum(c * c for c in n))
        pts = [verts[k] for k in f]
        c = tuple(sum(p[k] for p in pts) / len(pts) for k in range(3)) if pts else (0.0, 0.0, 0.0)
        info.append((c, tuple(x / a for x in n) if a > 0 else (0.0, 0.0, 0.0), a))
        if face_glass[i] and a > 0:
            grid.setdefault(tuple(int(math.floor(x / tol)) for x in c), []).append(i)
    out = set()
    for i in range(len(faces)):
        c, n, a = info[i]
        if face_glass[i] or a <= 0:
            continue
        cell = tuple(int(math.floor(x / tol)) for x in c)
        hit = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in grid.get((cell[0] + dx, cell[1] + dy, cell[2] + dz), ()):
                        cj, nj, aj = info[j]
                        if math.dist(c, cj) <= tol and sum(p * q for p, q in zip(n, nj)) < -0.9 \
                                and 0.8 <= a / aj <= 1.25:
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    break
        if hit:
            out.add(i)
    return out


def glass_faces(materials, face_materials) -> list[bool]:
    """Per face: its material is glass (``is_glass``)."""
    glassy = [is_glass(m) for m in materials]
    return [m is not None and 0 <= m < len(glassy) and glassy[m] for m in face_materials]


def panel_layout(centre, wall, width: float, panels: int, outward, thickness: float, depth: float,
                 centred: bool = False):
    """``[(x, y)]``: the plan centres of ``panels`` equal panels across ``width`` on the wall through ``centre``,
    moved outward so the model's outer face sits ``OUTSIDE_SET_M`` inside the outer wall face (pure); ``centred``
    (an inside door, 28 Oct 2026): on the wall's centre line."""
    (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    ox, oy = outward
    push = 0.0 if centred else max(0.0, thickness / 2.0 - OUTSIDE_SET_M - depth / 2.0)
    pw = width / panels
    return [(centre[0] + ux * (-width / 2.0 + pw * (i + 0.5)) + ox * push,
             centre[1] + uy * (-width / 2.0 + pw * (i + 0.5)) + oy * push) for i in range(panels)]


def mirror_across(verts, faces, uvs, centre, axis) -> tuple[list, list, Optional[list]]:
    """``(verts, faces, uvs)`` mirrored across the vertical plane through ``centre`` (x, y) whose normal is the plan
    direction ``axis`` (pure; 28 Oct 2026: a door turned to its drawn hinge side). Each face's corners (and their
    UVs) are reversed, so its normal still points out."""
    ax, ay = float(axis[0]), float(axis[1])
    n = math.hypot(ax, ay) or 1.0
    ax, ay = ax / n, ay / n
    cx, cy = float(centre[0]), float(centre[1])
    out = []
    for v in verts:
        d = (v[0] - cx) * ax + (v[1] - cy) * ay
        out.append((v[0] - 2.0 * d * ax, v[1] - 2.0 * d * ay, v[2]))
    rfaces = [list(reversed(list(f))) for f in faces]
    ruvs = None if uvs is None else [None if uv is None else list(reversed(list(uv))) for uv in uvs]
    return out, rfaces, ruvs


def pair_mirrors(panels: int, along, outward, handle_side: Optional[str]) -> list[bool]:
    """Per panel (in ``panel_layout`` order, along the wall from its start): mirror it or not, so the leaves of a
    hinged pair built of one one-leaf model meet in the middle with their handles there and their hinges at the
    jambs (pure; 29 Oct 2026, user: "Better door models needed"; ``opening_models`` ``pair``). ``handle_side``: the
    model's handle in its front view (the audit: left, right; else unknown). Seen from the front (the side ``outward``
    points to) a leaf left of the middle wants its handle on its right, a leaf right of it on its left; a middle leaf
    of an odd count stays as modelled. A model whose handle side is unknown keeps the left half as modelled and
    mirrors the right half (the two halves mirror images: a pair either way)."""
    n = max(1, int(panels))
    ax, ay = float(along[0]), float(along[1])
    ox, oy = float(outward[0]), float(outward[1])
    # the viewer in front looks along -outward; their right hand is (-oy, ox): the panels run from their left when
    # the wall's direction points to their right
    first_left = ax * -oy + ay * ox > 0.0
    out = []
    for i in range(n):
        pos = i if first_left else n - 1 - i             # 0 = the viewer's leftmost leaf
        if 2 * pos + 1 == n:
            out.append(False)
            continue
        left = 2 * pos + 1 < n
        if handle_side in ("left", "right"):
            out.append(handle_side == ("left" if left else "right"))
        else:
            out.append(not left)
    return out


def front_rotation_deg(outward) -> float:
    """The footprint rotation that turns the piece front (-Y) to ``outward`` (pure)."""
    return math.degrees(math.atan2(float(outward[0]), -float(outward[1])))


def _window_finish(opening: dict, ctx: dict):
    """The windows' frame finish of the style (``shell.window_frame_look``; the style of ``ctx["library"]``), the
    finish of a glazed door; None when it cannot be made."""
    from wenart.blender import shell as SH

    library = ctx.get("library")
    try:
        return SH.look_material(library, SH.window_frame_look(getattr(library, "style", None) or {}, opening))
    except Exception:  # noqa: BLE001 - the door's own look stays
        return None


def stretch_problem(box, panel_w: float, height: float) -> Optional[str]:
    """Why a library model of piece box ``box`` (width, depth, height: ``catalog.oriented_bbox``) is no real product in
    a panel ``panel_w`` x ``height`` (pure), None when it fits. 27 Oct 2026 (user on real06's entrance: "correct the
    door"): a model is scaled into its opening keeping its proportions within the plan's tolerance; a fit that stretches
    its width and its height by very different factors (more than ``STRETCH_TOL`` as a log ratio: a model turned on
    its frame, its 13 cm leaf edge stretched to 0.80 m, fit scale 6.1 x 0.1 x 0.9) or a box deeper than wide (its front
    along its leaf) is refused."""
    try:
        mw, md, mh = (float(v) for v in list(box)[:3])
    except (TypeError, ValueError):
        return "has no box"
    if mw <= 0 or mh <= 0 or panel_w <= 0 or height <= 0:
        return "has no size"
    if md > mw:
        return f"is deeper ({md:.2f} m) than wide ({mw:.2f} m): its front runs along its leaf"
    sx, sz = panel_w / mw, height / mh
    if abs(math.log(sx / sz)) > STRETCH_TOL:
        return (f"would be stretched {sx:.2f} x across and {sz:.2f} x up (box {mw:.2f} x {md:.2f} x {mh:.2f} m): not "
                f"a real product in this opening")
    return None


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
    inside = bool(lib.get("inside"))
    if (opening.get("type") != "door" or lib.get("category") in ("glazed_door", "terrace_door")
            or (inside and lib.get("role") == "glazed")) \
            and not any(is_glass(m) for m in model.get("materials") or []):
        # 25 Oct 2026: a window whose panes are an opaque picture of glass shuts the daylight out (real04's
        # "Window1 1": the south rooms went +4..+7 EV darker); the parametric window has real glass
        warnings.append(f"{opening['id']}: library model {path.name} has no see-through glass; parametric opening")
        return []
    asset = lib["asset"]
    panels = max(1, int(lib.get("panels") or 1))
    width, height, thickness = geo["width"], geo["height"], geo["thickness"]
    box = asset.get("bbox_m") or [1.0, 0.1, 1.0]
    mw, md, mh = (float(v) for v in box[:3])        # the piece frame (catalog.oriented_bbox): width, depth, height
    pw = width / panels
    why = stretch_problem(box, pw, height)
    if why:
        warnings.append(f"{opening['id']}: library model {path.name} {why}; parametric opening")
        return []
    depth = min(md * (pw / mw + height / mh) / 2.0, max(0.03, thickness - WALL_GAP_M))
    rot = front_rotation_deg(outward)
    kind = "door" if opening["type"] == "door" else "window"
    look = mats.get("leaf") if kind == "door" else mats.get("frame")
    if lib.get("category") in ("glazed_door", "terrace_door"):
        # 26 Oct 2026: a glazed door is joinery of the facade: the windows' frame finish
        look = mats.get("frame") or _window_finish(opening, ctx) or look
    # 26 Oct 2026: textured frames and large metals take the style's finish too; the opaque back of a pane is glass
    shares = model.get("_material_shares")
    if shares is None:
        shares = model["_material_shares"] = material_shares(len(model["materials"]), model["verts"],
                                                             model["faces"], model["face_materials"])
    twins = model.get("_glass_twins")
    if twins is None:
        twins = model["_glass_twins"] = glass_twins(model["verts"], model["faces"],
                                                    glass_faces(model["materials"], model["face_materials"]))
    materials = material_map(model["materials"], mats["glass"], look, shares)
    face_materials = list(model["face_materials"])
    if twins:
        if mats["glass"] not in materials:
            materials.append(mats["glass"])
        g = materials.index(mats["glass"])
        for k in twins:
            face_materials[k] = g
    repainted = sorted({m.name for m, b in zip(model["materials"], materials) if b is look and m is not look})
    created = []
    (wx0, wy0), (wx1, wy1) = wall["start"][:2], wall["end"][:2]
    along = (wx1 - wx0, wy1 - wy0)
    # 29 Oct 2026: the leaves of a pair meet in the middle (pair_mirrors); any other door its drawn hinge side
    mirrors = pair_mirrors(panels, along, outward, lib.get("handle_side")) if lib.get("pair") and panels > 1 \
        else [bool(lib.get("mirror"))] * panels
    for i, (px, py) in enumerate(panel_layout(geo["centre"], wall, width, panels, outward, thickness, depth,
                                              centred=inside)):
        verts, info = F.fit_vertices(model["verts"], asset, {"center": [px, py], "size": [pw, depth],
                                                             "rotation_deg": rot}, geo["bottom"],
                                     target_size=[pw, depth, height])
        faces, uvs = model["faces"], model.get("uvs")
        if mirrors[i]:
            # 28 Oct 2026: the drawn hinge side (opening_models.hinge_mirror); 29 Oct 2026: a pair's leaf
            verts, faces, uvs = mirror_across(verts, faces, uvs, (px, py), along)
        ob = F._mesh_object(f"{opening['id']}_lib{i}", verts, faces, materials, face_materials,
                            ctx["collection"], opening["id"], kind, geo["status"], uvs=uvs,
                            uv_name=model.get("uv_name"), fallback_material=look or mats["glass"])
        ob.pass_index = geo["index"]
        created.append(ob)
        entry = SH._opening_entry(opening, ob.name, geo["level_id"], (look or mats["glass"]).name,
                                  any(has_image(m) for m in materials), geo["index"], op_assumed, shift)
        entry.update(library_model={"asset_id": asset.get("asset_id"), "title": asset.get("title"),
                                    "licence": asset.get("licence"), "licence_flag": asset.get("licence_flag"),
                                    "attribution": asset.get("attribution"), "category": lib.get("category"),
                                    "panel": i, "panels": panels, "fit": info, "family": lib.get("family"),
                                    "look": lib.get("look"), "finish": None if look is None else look.name,
                                    "repainted": repainted, "glass_twins": len(twins),
                                    # 28 Oct 2026: the role and the audit's fields (Argus: door_variety_problems)
                                    "role": lib.get("role"), "model_role": lib.get("model_role"),
                                    # the model's stated operation: opening_models.model_operation reads it here too
                                    "opening": {"operation": lib.get("model_operation")},
                                    "statement": lib.get("statement"), "quality": lib.get("quality"),
                                    "inside": inside, "mirror": mirrors[i], "hinge": lib.get("hinge"),
                                    # 29 Oct 2026: a pair of one model's leaves; the leaf the audit saw
                                    "pair": bool(lib.get("pair")), "leaf": lib.get("leaf")},
                     inferred={"field": "product", "reason": lib.get("reason")})
        ctx["manifest_objects"].append(entry)
    ctx["assumed"].append({"object": opening["id"], "field": "library_model", "value": asset.get("asset_id"),
                           "reason": lib.get("reason"), "parent": opening["id"], "kind": "library_model"})
    if inside and lib.get("hinge") and "assumed" in str(lib.get("hinge")):
        ctx["assumed"].append({"object": opening["id"], "field": "door_hinge_side", "value": "as modelled",
                               "reason": lib["hinge"], "parent": opening["id"], "kind": "library_model"})
    if lib.get("add_handles") and opening.get("type") == "door":
        created += _library_handles(opening, geo, ctx, lib)
    return created


def _library_handles(opening: dict, geo: dict, ctx: dict, lib: dict) -> list:
    """The lever pair of the parametric door on a library door whose model has no handle (28 Oct 2026: the audit's
    ``handle_side`` none): a design detail, assumed, with the opening's id and pass index."""
    from wenart.blender import common
    from wenart.blender import shell as SH

    library = ctx.get("library")
    steel = library.get("steel_brushed") if library is not None else None
    sill = float(geo["bottom"]) - float(geo.get("floor_z", geo["bottom"]))
    parts = SH._local_to_world(SH.door_handle_parts(geo["width"], geo["height"], sill, pair=bool(lib.get("pair"))),
                               (*geo["centre"], geo["bottom"]), geo["angle"])
    ob = common.new_mesh_object(f"{opening['id']}_handle", *parts, collection=ctx["collection"],
                                wenart_id=opening["id"], kind="door", status="assumed",
                                materials=[steel] if steel is not None else ())
    ob.pass_index = geo["index"]
    reason = (f"design detail of the documented door: lever handles on both faces of the library model "
              f"{(lib.get('asset') or {}).get('asset_id')} (the audit sees no handle on it); not in the documents")
    entry = SH._opening_entry(opening, ob.name, geo["level_id"], steel.name if steel is not None else None, False,
                              geo["index"], {}, 0.0)
    entry.update(status="assumed", evidence=[], parent=opening["id"],
                 assumed={"detail": "door_handles", "lever_height_m": SH.HANDLE_HEIGHT, "reason": reason})
    ctx["manifest_objects"].append(entry)
    ctx["assumed"].append({"object": ob.name, "field": "door_handles", "value": "steel lever pair",
                           # its own kind: "door_handles" belongs to the parametric leaves (<id>_leaf)
                           "reason": reason, "parent": opening["id"], "kind": "library_door_handles"})
    return [ob]
