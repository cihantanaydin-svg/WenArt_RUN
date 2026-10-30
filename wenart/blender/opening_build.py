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
import re
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


def glass_named(name: str) -> bool:
    """A material name that says glass (``GLASS_WORDS``, pure). 30 Oct 2026 (UL191): "pane" never inside "panel" (a
    door's "Panel" material read as glass is a see-through slot in the leaf)."""
    low = str(name or "").lower()
    if any(w in low for w in GLASS_WORDS if w != "pane"):
        return True
    return re.search(r"pane(?!l)", low) is not None


def is_glass(mat) -> bool:
    """A model material that is glass: by name (``glass_named``), or a principled shader with transmission > 0.5 or
    alpha < 0.7."""
    if mat is None:
        return False
    if glass_named(mat.name):
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


# 30 Oct 2026 (lesson UL191, user on real04 run 20261030-112241-full: "Something wrong with this door in the
# kitchen"): the kitchen's inside door (HSSD 204-7, open against a slatted wall) had two narrow clear-glass lites, and
# through them the wall 2 cm behind the leaf showed: two slots cut through the leaf. An inside door whose glass covers
# at most ``SATIN_LITE_SHARE`` of the model's surface (narrow lites, a strip, a small vision slit; a glazed leaf's
# pane is far more) takes satin glass (``materials.satin_glass``): a lite reads as a glass insert, the leaf as solid.
SATIN_LITE_SHARE = 0.08


def glass_share(materials, shares) -> float:
    """The share of the model's surface its glass materials (``is_glass``) cover (pure)."""
    return sum(s for m, s in zip(materials, shares or ()) if is_glass(m))


def satin_lites(materials, shares, inside: bool) -> bool:
    """UL191: True for an inside door model whose glass is narrow lites only (some glass, at most
    ``SATIN_LITE_SHARE`` of its surface): they take satin glass (pure)."""
    share = glass_share(materials, shares)
    return bool(inside) and 0.0 < share <= SATIN_LITE_SHARE


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


# 29 Oct 2026 (UL122, user: "Doors looks without frames they need frames"; UL116: inside doors open by default): a
# library door model is measured (``leaf_panel``): its leaf face (the largest face across the wall and the faces in its
# plane) against the model's outer box. A model whose leaf face reaches its outer box at both jambs and the head
# (within ``BARE_LEAF_MARGIN_M``) is a bare leaf: it is fitted into the parametric door's frame (jambs as deep as the
# wall, head, stops, the architrave on its indoor faces) and the whole model is the leaf; a model with a frame of its
# own keeps it and gets only the architrave (never two frames). The leaf (the whole bare model, or the faces of a
# framed model inside its leaf box: ``leaf_mask``) turns open as ``door_states`` decided (numpy, no Python loop over
# the vertices).
BARE_LEAF_MARGIN_M = 0.02          # a leaf face this close to the model's box at both jambs and the head: no own frame
PLANE_TOL_M = 0.003                # faces within this of the leaf face's plane lie in it
GAP_TOL_M = 0.0005                 # coverage intervals closer than this touch
FRAME_EDGE_MAX_M = 0.16            # a gap in the leaf plane this near a jamb or the head is the leaf-frame joint
LEAF_TOL_M = 0.004                 # a leaf face lies inside the leaf box with this tolerance


def local_coords(verts, centre, along, outward, bottom):
    """The verts (world) in an opening's panel frame (numpy ``(N, 3)``): x along the wall (``along``), y towards
    ``outward``, z up from ``bottom``."""
    import numpy as np

    v = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    ax, ay = float(along[0]), float(along[1])
    n = math.hypot(ax, ay) or 1.0
    ax, ay = ax / n, ay / n
    ox, oy = float(outward[0]), float(outward[1])
    dx, dy = v[:, 0] - float(centre[0]), v[:, 1] - float(centre[1])
    return np.stack([dx * ax + dy * ay, dx * ox + dy * oy, v[:, 2] - float(bottom)], axis=1)


def world_coords(local, centre, along, outward, bottom) -> list:
    """The inverse of ``local_coords`` (``along`` and ``outward`` perpendicular unit vectors)."""
    import numpy as np

    loc = np.asarray(local, dtype=np.float64).reshape(-1, 3)
    ax, ay = float(along[0]), float(along[1])
    n = math.hypot(ax, ay) or 1.0
    ax, ay = ax / n, ay / n
    ox, oy = float(outward[0]), float(outward[1])
    x = float(centre[0]) + loc[:, 0] * ax + loc[:, 1] * ox
    y = float(centre[1]) + loc[:, 0] * ay + loc[:, 1] * oy
    return list(zip(x.tolist(), y.tolist(), (loc[:, 2] + float(bottom)).tolist()))


def _face_corners(faces):
    """Four corner indices per face (the first three and the last: every vertex of a triangle or a quad)."""
    import numpy as np

    return np.array([(f[0], f[1], f[2], f[-1]) if len(f) >= 3 else (f[0], f[0], f[0], f[0]) for f in faces],
                    dtype=np.int64).reshape(-1, 4)


def _merged(intervals):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1] + GAP_TOL_M:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def leaf_panel(local, faces) -> dict:
    """The model's leaf face measured against its outer box (pure numpy; module comment): ``{"framed", "x0", "x1",
    "z1", "margins": [left, right, top], "half_t", "box"}``; ``framed`` None when no face lies across the wall."""
    import numpy as np

    loc = np.asarray(local, dtype=np.float64).reshape(-1, 3)
    if not len(faces) or not len(loc):
        return {"framed": None, "why": "no geometry"}
    c = _face_corners(faces)
    p0, p1, p2 = loc[c[:, 0]], loc[c[:, 1]], loc[c[:, 2]]
    cr = np.cross(p1 - p0, p2 - p0)
    area = np.linalg.norm(cr, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ny = np.where(area > 1e-12, np.abs(cr[:, 1]) / np.maximum(area, 1e-12), 0.0)
    across = ny > 0.9
    if not across.any():
        return {"framed": None, "why": "no face lies across the wall"}
    big = int(np.argmax(np.where(across, area, -1.0)))
    cy = loc[c, 1].mean(axis=1)
    plane = across & (np.abs(cy - cy[big]) <= PLANE_TOL_M)
    xs, zs = loc[c[plane], 0], loc[c[plane], 2]
    lo = loc.min(axis=0)
    hi = loc.max(axis=0)
    cover = _merged(zip(xs.min(axis=1).tolist(), xs.max(axis=1).tolist()))
    mid = (lo[0] + hi[0]) / 2.0
    run = next((iv for iv in cover if iv[0] - GAP_TOL_M <= mid <= iv[1] + GAP_TOL_M), max(cover, key=lambda iv: iv[1] - iv[0]))
    x0, x1 = run
    # the leaf's own faces: in the run along x; the head is the highest of them
    inrun = (xs.min(axis=1) >= x0 - GAP_TOL_M) & (xs.max(axis=1) <= x1 + GAP_TOL_M)
    z1 = float(zs[inrun].max()) if inrun.any() else float(hi[2])
    margins = [round(float(x0 - lo[0]), 4), round(float(hi[0] - x1), 4), round(float(hi[2] - z1), 4)]
    framed = any(m >= BARE_LEAF_MARGIN_M for m in margins)
    return {"framed": bool(framed), "x0": round(float(x0), 5), "x1": round(float(x1), 5), "z1": round(float(z1), 5),
            "margins": margins, "half_t": round(float(abs(cy[big])), 5),
            "box": [round(float(v), 5) for v in (lo[0], lo[1], lo[2], hi[0], hi[1], hi[2])]}


def leaf_mask(local, faces, panel: dict):
    """Per face: it belongs to the leaf (every corner inside the measured leaf box ``x0 .. x1`` and under ``z1``)."""
    import numpy as np

    loc = np.asarray(local, dtype=np.float64).reshape(-1, 3)
    c = _face_corners(faces)
    xs, zs = loc[c, 0], loc[c, 2]
    return (xs.min(axis=1) >= panel["x0"] - LEAF_TOL_M) & (xs.max(axis=1) <= panel["x1"] + LEAF_TOL_M) & \
        (zs.max(axis=1) <= panel["z1"] + LEAF_TOL_M)


def turn_leaf(local, faces, mask, pivot, angle_deg: float):
    """``(local verts, faces)`` with the faces of ``mask`` turned about the vertical axis through ``pivot`` (x, y)
    (pure numpy): their vertices are copied first where a face outside the mask shares them, so the frame stays."""
    import numpy as np

    loc = np.asarray(local, dtype=np.float64).reshape(-1, 3).copy()
    mask = np.asarray(mask, dtype=bool)
    faces = [list(f) for f in faces]
    if not mask.any():
        return loc, faces
    leaf_v = np.unique(np.concatenate([np.asarray(faces[i], dtype=np.int64) for i in np.nonzero(mask)[0]]))
    rest = [np.asarray(faces[i], dtype=np.int64) for i in np.nonzero(~mask)[0]]
    frame_v = np.unique(np.concatenate(rest)) if rest else np.zeros(0, dtype=np.int64)
    shared = np.intersect1d(leaf_v, frame_v)
    remap = np.arange(len(loc))
    if len(shared):
        remap[shared] = len(loc) + np.arange(len(shared))
        loc = np.concatenate([loc, loc[shared]], axis=0)
        for i in np.nonzero(mask)[0]:
            faces[i] = remap[np.asarray(faces[i], dtype=np.int64)].tolist()
        leaf_v = remap[leaf_v]
    a = math.radians(angle_deg)
    cos, sin = math.cos(a), math.sin(a)
    px, py = float(pivot[0]), float(pivot[1])
    x, y = loc[leaf_v, 0] - px, loc[leaf_v, 1] - py
    loc[leaf_v, 0] = px + cos * x - sin * y
    loc[leaf_v, 1] = py + sin * x + cos * y
    return loc, faces


def handle_x(local, faces, face_materials, materials, shares=None) -> Optional[float]:
    """The mean x of the model's hardware faces (``is_hardware``: the handle), None when it has none."""
    import numpy as np

    hard = np.array([is_hardware(m, None if shares is None else (shares[i] if i < len(shares) else 0.0))
                     for i, m in enumerate(materials or [])] + [False], dtype=bool)
    fm = np.asarray([-1 if m is None else int(m) for m in face_materials or []], dtype=np.int64)
    if not len(fm):
        return None
    fm = np.where((fm >= 0) & (fm < len(hard) - 1), fm, len(hard) - 1)
    sel = np.nonzero(hard[fm])[0]
    if not len(sel):
        return None
    loc = np.asarray(local, dtype=np.float64).reshape(-1, 3)
    c = _face_corners([faces[k] for k in sel.tolist()])
    return float(loc[c, 0].mean())


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


def _lower_light_height(opening: dict, geo: dict) -> float:
    """The height of a window's fixed lower light (``window_order``'s ``lower_light``: its transom over the floor
    minus the sill), 0 when it has none or it would leave too little of a light below or above the transom."""
    from wenart.blender import parametric as P

    lower = opening.get("lower_light") if isinstance(opening.get("lower_light"), dict) else None
    if opening.get("type") != "window" or not lower or lower.get("at_m") is None or opening.get("sill_height") is None:
        return 0.0
    h = float(lower["at_m"]) - float(opening["sill_height"])
    return h if P.TRANSOM_LIGHT_MIN_M <= h <= float(geo["height"]) - 2 * P.TRANSOM_LIGHT_MIN_M else 0.0


def _lower_light(opening: dict, wall: dict, geo: dict, ctx: dict, mats: dict, look, shift: float, op_assumed: dict,
                 low_h: float) -> list:
    """The parametric fixed lower light under a library window (``parametric.fixed_light_parts``; lesson UL210)."""
    from wenart.blender import parametric as P
    from wenart.blender import shell as SH

    lower = opening["lower_light"]
    side, _room, _assumed = SH.opening_room_side(geo["centre"], wall, ctx["rooms"])
    key = "satin" if lower.get("glass") == "satin" else "glass"
    parts = P.fixed_light_parts(None, geo["width"], low_h, geo["thickness"], side, key)
    library = ctx["library"]
    by = {"frame": look or mats.get("frame") or mats["glass"], "glass": mats["glass"],
          "gasket": library.get(SH.WINDOW_GASKET_MATERIAL)}
    if key == "satin":
        by["satin"] = library.satin_glass()
    ob, used = SH._opening_object(opening, "lower_light", parts, by, geo, ctx, "assumed")
    reason = (f"a fixed lower light {low_h:.2f} m high under the window's transom ({lower.get('why') or 'its sill'}; "
              f"lesson UL210: one sill line with its neighbours)")
    SH._detail_entry(opening, ob, used, geo, ctx, {"detail": "lower_light", "height_m": round(low_h, 3),
                                                   "glass": key, "reason": reason},
                     f"fixed lower light {low_h:.2f} m", "lower_light", shift)
    return [ob]


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
    # 30 Oct 2026 (lesson UL210, window_order): a window of a facade composition with a fixed lower light under a
    # transom: the model fills the light above it, a parametric fixed light in the frame's finish the one below
    low_h = _lower_light_height(opening, geo)
    width, height, thickness = geo["width"], geo["height"] - low_h, geo["thickness"]
    bottom = geo["bottom"] + low_h
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
    glass = mats["glass"]
    satin = kind == "door" and satin_lites(model["materials"], shares, inside) \
        and hasattr(ctx.get("library"), "satin_glass")
    # UL210: a wet room's window of a facade composition takes satin glass (privacy, not a higher sill)
    satin = satin or (kind == "window" and opening.get("glass") == "satin" and hasattr(ctx.get("library"),
                                                                                       "satin_glass"))
    if satin:
        glass = ctx["library"].satin_glass()                 # UL191: narrow lites of an inside door: satin glass
    materials = material_map(model["materials"], glass, look, shares)
    face_materials = list(model["face_materials"])
    if twins:
        if glass not in materials:
            materials.append(glass)
        g = materials.index(glass)
        for k in twins:
            face_materials[k] = g
    repainted = sorted({m.name for m, b in zip(model["materials"], materials) if b is look and m is not look})
    created = []
    (wx0, wy0), (wx1, wy1) = wall["start"][:2], wall["end"][:2]
    along = (wx1 - wx0, wy1 - wy0)
    # 29 Oct 2026: the leaves of a pair meet in the middle (pair_mirrors); any other door its drawn hinge side
    mirrors = pair_mirrors(panels, along, outward, lib.get("handle_side")) if lib.get("pair") and panels > 1 \
        else [bool(lib.get("mirror"))] * panels
    # 29 Oct 2026 (UL122, UL116): a door is framed (its model's own frame, else the parametric door's) and its leaf
    # posed as door_states decided (module comment above ``leaf_panel``)
    framing = kind == "door" and bool(mats.get("framing"))
    state = opening.get("leaf_state") if framing and isinstance(opening.get("leaf_state"), dict) else None
    door_recs: list = []
    for i, (px, py) in enumerate(panel_layout(geo["centre"], wall, width, panels, outward, thickness, depth,
                                              centred=inside)):
        verts, info = F.fit_vertices(model["verts"], asset, {"center": [px, py], "size": [pw, depth],
                                                             "rotation_deg": rot}, bottom,
                                     target_size=[pw, depth, height])
        faces, uvs = model["faces"], model.get("uvs")
        if mirrors[i]:
            # 28 Oct 2026: the drawn hinge side (opening_models.hinge_mirror); 29 Oct 2026: a pair's leaf
            verts, faces, uvs = mirror_across(verts, faces, uvs, (px, py), along)
        mats_i, fm_i = materials, face_materials
        if framing:
            verts, faces, uvs, mats_i, fm_i, drec, info = _frame_and_pose(
                opening, model, asset, geo, along, outward, i, panels, (px, py), verts, faces, uvs, materials,
                face_materials, look, mats.get("door_frame") or look, state, mirrors[i], depth, rot, info, shares)
            door_recs.append(drec)
        ob = F._mesh_object(f"{opening['id']}_lib{i}", verts, faces, mats_i, fm_i,
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
                                    "repainted": repainted, "glass_twins": len(twins), "satin_glass": satin,
                                    # 28 Oct 2026: the role and the audit's fields (Argus: door_variety_problems)
                                    "role": lib.get("role"), "model_role": lib.get("model_role"),
                                    # the model's stated operation: opening_models.model_operation reads it here too
                                    "opening": {"operation": lib.get("model_operation")},
                                    "statement": lib.get("statement"), "quality": lib.get("quality"),
                                    "inside": inside, "mirror": mirrors[i], "hinge": lib.get("hinge"),
                                    # 29 Oct 2026: a pair of one model's leaves; the leaf the audit saw
                                    "pair": bool(lib.get("pair")), "leaf": lib.get("leaf")},
                     inferred={"field": "product", "reason": lib.get("reason")})
        if framing and door_recs:
            entry["library_model"]["measured"] = door_recs[-1].get("measured")
            if door_recs[-1].get("pose"):
                entry["pose"] = door_recs[-1]["pose"]
        ctx["manifest_objects"].append(entry)
    if framing:
        created += _door_frame(opening, wall, geo, ctx, door_recs, mats.get("door_frame") or look, state, shift,
                               op_assumed)
    if low_h > 0:
        created += _lower_light(opening, wall, geo, ctx, mats, look, shift, op_assumed, low_h)
    ctx["assumed"].append({"object": opening["id"], "field": "library_model", "value": asset.get("asset_id"),
                           "reason": lib.get("reason"), "parent": opening["id"], "kind": "library_model"})
    if inside and lib.get("hinge") and "assumed" in str(lib.get("hinge")):
        ctx["assumed"].append({"object": opening["id"], "field": "door_hinge_side", "value": "as modelled",
                               "reason": lib["hinge"], "parent": opening["id"], "kind": "library_model"})
    if lib.get("add_handles") and opening.get("type") == "door":
        created += _library_handles(opening, geo, ctx, lib, door_recs, wall)
    return created


def _frame_and_pose(opening, model, asset, geo, along, outward, i, panels, centre, verts, faces, uvs, materials,
                    face_materials, look, frame_mat, state, mirrored, depth, rot, info, shares):
    """One panel of a library door framed and posed (module comment above ``leaf_panel``): ``(verts, faces, uvs,
    materials, face materials, record, fit info)``. A bare leaf is fitted again into the parametric frame's clear
    opening (its centre on the wall's centre line); a framed model keeps its frame, whose faces take the door frame's
    finish; an open or ajar leaf turns about its hinge edge (``door_states``' hinge; the model mirrored first when its
    handle sits at that hinge)."""
    import numpy as np

    from wenart.blender import furniture as F
    from wenart.blender import parametric as P

    width, height = float(geo["width"]), float(geo["height"])
    fw = P.DOOR_FRAME_W
    lw, lh = width - 2 * fw - 0.01, height - fw - 0.01
    c0 = geo["centre"]
    bottom = geo["bottom"]
    loc = local_coords(verts, c0, along, outward, bottom)
    panel = leaf_panel(loc, faces)
    rec = {"bare": panel.get("framed") is False, "measured": {k: panel.get(k) for k in ("framed", "margins", "half_t",
                                                                                         "why") if k in panel}}
    an = math.hypot(float(along[0]), float(along[1])) or 1.0
    ux, uy = float(along[0]) / an, float(along[1]) / an
    if rec["bare"]:
        off = 0.0 if panels == 1 else (-lw / 4.0 if i == 0 else lw / 4.0)
        ci = (float(c0[0]) + ux * off, float(c0[1]) + uy * off)
        pw = lw / max(1, panels)
        verts, info = F.fit_vertices(model["verts"], asset, {"center": list(ci), "size": [pw, depth],
                                                             "rotation_deg": rot}, bottom, target_size=[pw, depth, lh])
        faces, uvs = model["faces"], model.get("uvs")
        if mirrored:
            verts, faces, uvs = mirror_across(verts, faces, uvs, ci, along)
        loc = local_coords(verts, c0, along, outward, bottom)
        panel = dict(leaf_panel(loc, faces), x0=off - pw / 2.0, x1=off + pw / 2.0, z1=lh)
        rec["measured"]["refit"] = {"leaf_m": [round(pw, 4), round(lh, 4)], "centre_m": round(off, 4)}
    rec["half_t"] = float(panel.get("half_t") or P.DOOR_LEAF_T / 2.0)
    mats_i, fm = list(materials), list(face_materials)
    mask = None
    if panel.get("framed") is not None:
        mask = np.ones(len(faces), dtype=bool) if rec["bare"] else leaf_mask(loc, faces, panel)
    if panel.get("framed") and mask is not None and frame_mat is not None and look is not None:
        is_look = np.array([m is look for m in mats_i], dtype=bool)
        fmi = np.asarray([m if m is not None else -1 for m in fm], dtype=np.int64)
        frame_faces = (~mask) & (fmi >= 0) & np.where(fmi >= 0, is_look[np.clip(fmi, 0, len(is_look) - 1)], False)
        if frame_faces.any():
            mats_i.append(frame_mat)
            k = len(mats_i) - 1
            fmi[frame_faces] = k
            fm = [None if v < 0 else int(v) for v in fmi.tolist()]
            rec["frame_faces"] = int(frame_faces.sum())
    pose = None
    if state is not None and state.get("state") in ("open", "ajar") and float(state.get("angle_deg") or 0.0) > 0 \
            and mask is not None and mask.any():
        hinge = state.get("hinge") if state.get("hinge") in ("start", "end") else ("start" if i == 0 else "end")
        if panels > 1:
            hinge = "start" if i == 0 else "end"                 # a pair: each leaf hinged at its own jamb
        else:
            hx_h = handle_x(loc, faces, fm, model.get("materials"), shares)
            if hx_h is not None and (hx_h < 0) == (hinge == "start"):
                # the model's handle sits at the hinge jamb: mirror the panel so the handle is at the free edge
                verts = world_coords(loc, c0, along, outward, bottom)
                verts, faces, uvs = mirror_across(verts, faces, uvs, c0, along)
                loc = local_coords(verts, c0, along, outward, bottom)
                if not rec["bare"]:
                    panel = dict(panel, x0=-panel["x1"], x1=-panel["x0"])
                    mask = leaf_mask(loc, faces, panel)
                rec["mirrored_for_hinge"] = True
        if rec["bare"]:
            hx = -lw / 2.0 if hinge == "start" else lw / 2.0
        else:
            hx = float(panel["x0"]) if hinge == "start" else float(panel["x1"])
        angle = P.swing_angle(hinge, 1.0, float(state["angle_deg"]))
        loc, faces = turn_leaf(loc, faces, mask, (hx, rec["half_t"]), angle)
        pose = {"state": state["state"], "angle_deg": float(state["angle_deg"]), "hinge": hinge,
                "faces_turned": int(mask.sum()), "source": "bare leaf" if rec["bare"] else "the model's leaf"}
    elif state is not None and state.get("state") in ("open", "ajar"):
        why = panel.get("why") or "the model's leaf is no separate part"
        pose = {"state": "closed", "why": f"built closed: {why}"}
    rec["pose"] = pose
    verts = world_coords(loc, c0, along, outward, bottom)
    return verts, faces, uvs, mats_i, fm, rec, info


def _door_frame(opening, wall, geo, ctx, recs, frame_mat, state, shift, op_assumed) -> list:
    """The frame of a library door (UL122): the parametric door's jambs, head, stops and architrave round a bare
    leaf, the architrave alone round a model with its own frame (``P.door_frame_parts``), one mesh object
    ``<id>_frame``; the manifest entry carries the ``frame`` record (the model review's M20, Argus' U33). A pose the
    build could not make closes the door's ``leaf_state`` with the reason."""
    from wenart.blender import parametric as P
    from wenart.blender import shell as SH

    bare = any(r.get("bare") for r in recs)
    half_t = max([float(r.get("half_t") or 0.0) for r in recs] + [P.DOOR_LEAF_T / 2.0])
    # the side the leaf opens into (+1 the wall's left), as the inside door entry's ``outward`` faces
    side = 1.0
    ls = opening.get("leaf_state") if isinstance(opening.get("leaf_state"), dict) else {}
    if ls.get("side") in (1, -1, 1.0, -1.0):
        side = float(ls["side"])
    else:
        s, _room, _a = SH.opening_room_side(geo["centre"], wall, ctx.get("rooms") or [], opening.get("swing_side"))
        side = float(s)
    faces = SH.architrave_faces(geo["centre"], wall, ctx.get("rooms") or [])
    margins = [m for r in recs for m in ((r.get("measured") or {}).get("margins") or [])[:2]]
    model_fw = min(margins) if margins and not bare else P.DOOR_FRAME_W
    # 30 Oct 2026 (UL179): the family's joinery profiles the architrave round a library door too
    joinery = SH.door_product(getattr(ctx.get("library"), "style", None) or {}).get("joinery")
    parts = P.door_frame_parts(geo["width"], geo["height"], geo["thickness"], half_t if bare else None, side, faces,
                               frame_w=max(0.02, min(P.DOOR_FRAME_W, model_fw)), lining=bare, joinery=joinery)
    created = []
    record = {"lining": True, "head": True, "architrave": sorted({-1 if f < 0 else 1 for f in faces}),
              "indoor_faces": sorted({-1 if f < 0 else 1 for f in faces}),
              "source": "ours (the parametric door's frame round a bare leaf)" if bare else "the model's own frame",
              "frameless": None, "architrave_why": None, "measured": [r.get("measured") for r in recs],
              # 30 Oct 2026 (UL132): the built parts, one height with the opening (M29: door_states.frame_problems)
              "census": P.frame_census(parts, geo["height"])}
    if parts:
        ob, used = SH._opening_object(opening, "frame", parts, {"frame": frame_mat}, geo, ctx, geo["status"])
        created.append(ob)
        entry = SH._opening_entry(opening, ob.name, geo["level_id"], used[0].name, ctx["library"].textured(used[0]),
                                  geo["index"], op_assumed, shift)
        entry["frame"] = record
        ctx["manifest_objects"].append(entry)
    else:
        record["architrave_why"] = "no indoor face"
    for e in ctx["manifest_objects"]:
        if e.get("element_id") == opening["id"] and isinstance(e.get("library_model"), dict):
            e.setdefault("frame", record)
    ctx["assumed"].append({"object": opening["id"], "field": "door_frame", "value": record["source"],
                           "reason": "every door is framed (UL122): " + record["source"]
                                     + f"; architrave on the indoor face(s) {record['architrave']}",
                           "parent": opening["id"], "kind": "door_frame"})
    closed = [r["pose"]["why"] for r in recs if (r.get("pose") or {}).get("state") == "closed"]
    if state is not None and closed and isinstance(opening.get("leaf_state"), dict):
        opening["leaf_state"] = dict(opening["leaf_state"], state="closed", built=False, leaf_polys=[],
                                     reason=str(opening["leaf_state"].get("reason") or "") + "; " + closed[0])
    return created


def posed_handle_parts(pieces: list, recs: list, side: float, lw: float, half_t: float) -> list:
    """The added lever pair of a library door (``(verts, faces)`` pieces in the opening's frame) posed with its open
    leaf (pure; ``recs``: the panels' records of ``_frame_and_pose``): mirrored to the free edge of a leaf hinged at
    the ``end`` jamb, turned with the leaf; a pair's halves with their own leaves."""
    from wenart.blender import parametric as P

    poses = [r.get("pose") for r in recs if (r.get("pose") or {}).get("state") in ("open", "ajar")]
    if not poses:
        return pieces
    parts = [{"verts": list(v), "faces": [list(f) for f in fc], "key": "handle", "role": "handle"} for v, fc in pieces]
    out = []
    if len(recs) > 1:
        for part in parts:
            left = P._centre_x(part) < 0.0
            hinge = "start" if left else "end"
            hx = -lw / 2.0 if left else lw / 2.0
            out += P.turn_parts([part], (hx, side * half_t), P.swing_angle(hinge, side, poses[0]["angle_deg"]))
    else:
        pose = poses[0]
        hinge = pose.get("hinge") or "start"
        if hinge == "end":
            parts = P.mirror_parts_x(parts)
        hx = -lw / 2.0 if hinge == "start" else lw / 2.0
        out = P.turn_parts(parts, (hx, side * half_t), P.swing_angle(hinge, side, pose["angle_deg"]))
    return [(p["verts"], p["faces"]) for p in out]


def _library_handles(opening: dict, geo: dict, ctx: dict, lib: dict, recs: Optional[list] = None,
                     wall: Optional[dict] = None) -> list:
    """The lever pair of the parametric door on a library door whose model has no handle (28 Oct 2026: the audit's
    ``handle_side`` none): a design detail, assumed, with the opening's id and pass index; 29 Oct 2026 (UL116): posed
    with the open leaf (``posed_handle_parts``)."""
    from wenart.blender import common
    from wenart.blender import parametric as P
    from wenart.blender import shell as SH

    library = ctx.get("library")
    steel = library.get(lib.get("handle_material") or "steel_brushed") if library is not None else None
    sill = float(geo["bottom"]) - float(geo.get("floor_z", geo["bottom"]))
    pieces = SH.door_handle_parts(geo["width"], geo["height"], sill, pair=bool(lib.get("pair")))
    if recs and wall is not None:
        ls = opening.get("leaf_state") if isinstance(opening.get("leaf_state"), dict) else {}
        side = float(ls.get("side") or 1.0)
        lw = float(geo["width"]) - 2 * P.DOOR_FRAME_W - 0.01
        half_t = max([float(r.get("half_t") or 0.0) for r in recs] + [P.DOOR_LEAF_T / 2.0])
        pieces = posed_handle_parts(pieces, recs, side, lw, half_t)
    parts = SH._local_to_world(pieces, (*geo["centre"], geo["bottom"]), geo["angle"])
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
