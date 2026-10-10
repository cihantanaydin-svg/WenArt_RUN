"""Exterior cameras of the whole building (docs/milestone10.md §3.3 item 1).

What: ``plan_exterior(model, building, ...)`` places the exterior views of a variant: four eye-level corner
views (1.6 m above the ground, from the plot corners, else 10-15 m from each building corner along its
diagonal, aimed so both facades show), one 3/4 aerial view (30 degrees down) from the corner whose two
facades carry the most openings, and one view per drawn elevation (``facade.elevations[]``: looking along its
``view_bearing_deg``, counter-clockwise from +X, else square to its side; its ``region_id``). Camera ids
``ext_<n>`` (corners 1-4, aerial 5, elevations from 6 on), kind ``exterior``, with the scene manifest's camera
fields (``variant``, ``view``, ``sides``, ``region_id``, ``dropped_reason``; docs/milestone10.md §1.6b row 11).
``create_cameras`` (bpy) makes the camera objects. ``resolve_looks`` (pure, §1.6b row 12) decides the outside
looks: documents > the brief's ``exterior:`` words > the style's ``exterior`` slots > ``style.exterior_fallback``.

Why: Feature 2 of Milestone 10: renders of the building from outside per variant (acceptance: >= 5 exterior
views per variant).

How: ``ExteriorModel`` is a triangle model of what stands outside (pure numpy, as ``camsearch``): the levels
as prisms of their outline (the level under the roof cut by the roof underside: gable ends and knee walls),
the roof's top faces, the plot walls, the trees and a coarse ground. A candidate camera is refused when it
stands inside the building, the roof, a tree crown or trunk, within ``CLEARANCE`` of a plot wall, or when its
view of the building is blocked: a 32 x 18 ray grid over its frame (``camsearch.ray_grid``, the §1.3 lens
shift convention) must see the building on at least ``MIN_BUILDING_SHARE`` of the rays, at most
``MAX_BLOCKED`` of the building rays may end on a tree or plot wall first, and the ray to the aim point must
reach the building. A refused camera moves along its diagonal (10-15 m) or towards / away from its facade;
when no place works it is dropped and listed with the reason. Eye-level cameras stay level (pitch 0) and
frame the building with a vertical lens shift (straight verticals); the lens is chosen so the building fills
at most ``FRAME_FILL`` of the frame (``LENS_RANGE_MM``). Every plan lists the outer openings it sees
(facing the camera, centre in the frame, the ray to it unblocked): the expected openings of the checks.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import roof as R
from wenart.blender import site as S

EYE_HEIGHT = 1.6
AERIAL_PITCH_DEG = 30.0
DIAGONAL_M = (12.0, 10.0, 11.0, 13.0, 14.0, 15.0)      # nominal first, then along the diagonal
PLOT_CORNER_INSET = 0.6
ELEVATION_STEPS = (1.0, 0.85, 0.7, 0.55, 0.4)          # fractions of the fit distance tried for an elevation
SENSOR_MM = 36.0
RESOLUTION = (1920, 1080)
LENS_RANGE_MM = (14.0, 50.0)
FRAME_FILL = 0.85
MAX_SHIFT_Y = 0.35
RAY_GRID = (32, 18)
MIN_BUILDING_SHARE = 0.08
MAX_BLOCKED = 0.35
CLEARANCE = 0.3
CLIP_END = 3000.0                                       # beyond the flat ground (site.HORIZON_M)
# Milestone 11 (docs/milestone11.md §1.1 E14, §4.1 X6, §7): the eye-level views of the main (entrance) facade.
EYE_LENS_MM = 26.0                                      # 24-28 mm
CORNER_ANGLE_DEG = 30.0                                 # off the facade a corner view faces (30/60 instead of 45)
FILL_RANGE = (0.6, 0.8)                                 # the building's share of the frame width
FILL_TARGET = 0.7
DISTANCE_SCAN_M = (6.0, 80.0, 0.5)
MOVE_STEPS_M = (0.0, 2.0, 4.0, -1.5, 6.0, 9.0, 12.0)      # a blocked eye-level view moves out (or a little in)
KIND = "exterior"
LABELS = {"nothing": 0, "building": 1, "plot_wall": 2, "tree": 3, "ground": 4}


# --------------------------------------------------------------------------
# The outside looks (docs/milestone10.md §1.6b rows 12, 14; §4.8)
# --------------------------------------------------------------------------

EXTERIOR_SLOTS = ("facade", "roof", "window_frame", "door", "paving", "garden")
# wenart/defaults.yaml ``style.exterior_fallback`` (Blender's Python has no PyYAML; tests/test_blender_exterior.py
# keeps this copy equal to the file). Colour "walls" = the interior wall colour of the style; "interior" = the
# interior slot's look, seen from outside.
EXTERIOR_FALLBACK = {"facade": {"material": "render", "colour": "walls"},
                     "roof": {"material": "concrete_tiles", "colour": "anthracite"},
                     "window_frame": "interior", "door": "interior",
                     "paving": {"material": "paving", "colour": "grey"},
                     "garden": {"material": "grass", "colour": None}}
# Looks of the details the build adds (no drawing, brief or style names them): slug, colour, reason.
BUILD_LOOKS = {"sill": ("stone", None, "exterior sill not drawn"),
               "light_well": ("concrete", None, "light well: concrete (not drawn)"),
               "railing": ("steel_brushed", None, "railing not drawn: steel rail and glass panel"),
               "soffit": ("soffit", None, "roof soffit: painted (not drawn)"),
               "bark": ("bark", None, "parametric tree"), "foliage": ("foliage", None, "parametric tree"),
               "ground": ("soil", None, "neutral ground (brief site: ground)")}


def look_from_words(slot: str, phrase: str) -> Optional[dict]:
    """``{"material", "colour"}`` of a brief phrase for an exterior slot, None when no material word matches: track
    C's tables (``wenart.style.profile.exterior_look_from_words``: vocabulary slugs such as
    ``aluminium_anthracite``, ``steel_black``, ``paving_stone``; colours of ``wenart/style/colours.py``; track F
    switched to them, docs/milestone10.md §1.6b row 20)."""
    from wenart.style.profile import exterior_look_from_words

    look, _notes = exterior_look_from_words(slot, str(phrase or ""))
    if not look or not look.get("material"):
        return None
    return {"material": look["material"], "colour": look.get("colour")}


def _asset_of(slug: Optional[str]) -> Optional[str]:
    """The vocabulary's asset id of a slug (``wenart.style.profile.asset_of``), None when it has none."""
    from wenart.style.profile import asset_of

    return asset_of(slug)


def _wall_colour(style: dict) -> tuple[Optional[str], Optional[list], str]:
    """``(colour name, linear rgb, how)`` of the style's interior walls: the slot's ``colour`` name, else the
    flat colour of its material (``vocabulary.MATERIALS``)."""
    walls = style.get("walls") if isinstance(style.get("walls"), dict) else {}
    if walls.get("colour"):
        return str(walls["colour"]), None, f"the style's wall colour {walls['colour']!r}"
    slug = walls.get("material") or "plaster_white"
    try:
        from wenart.style.vocabulary import MATERIALS
        flat = (MATERIALS.get(slug) or {}).get("flat")
    except ImportError:
        flat = None
    if flat:
        return None, [round(float(v), 4) for v in flat], f"the flat colour of the style's wall material {slug!r}"
    return "white", None, f"the style's wall material {slug!r} has no flat colour: white"


def _look(material, colour, source: str, reason: str, rgb=None, asset=None, evidence=None) -> dict:
    return {"material": material, "colour": colour, "rgb": rgb, "asset": asset, "source": source,
            "assumed": source in ("fallback", "build"), "reason": reason, "evidence": list(evidence or [])}


def resolve_looks(building: dict, style: dict, brief=None) -> dict:
    """The outside looks of the whole building (pure; §1.6b row 12): per slot of ``EXTERIOR_SLOTS`` the first
    of the documents (``facade.faces`` with side ``all`` and no wall or z band: the whole facade;
    ``roof.covering``), the brief's ``exterior:`` words (``look_from_words``; ``brief`` a ``load_brief`` result
    or a values dict, None = the building's stored brief), the style profile's ``exterior`` slot (track C:
    ``{material|slug, colour, source, assumed}``; an assumed entry counts as the fallback) and
    ``style.exterior_fallback`` (the style's copy, else ``EXTERIOR_FALLBACK``; colour ``walls`` = the interior
    wall colour, ``interior`` = the inside slot); then the looks the build adds (``BUILD_LOOKS``, the plot wall
    = the facade's). Each look: ``{"material", "colour", "rgb", "asset", "source": documents | brief | style |
    fallback | build, "assumed", "reason", "evidence"}``; a brief phrase that names no material adds
    ``warnings``. Recorded in the scene manifest (``exterior_looks``), never written back."""
    from wenart import views as V

    facade = building.get("facade") if isinstance(building.get("facade"), dict) else {}
    roof = building.get("roof") if isinstance(building.get("roof"), dict) else {}
    style = style or {}
    ext = style.get("exterior") if isinstance(style.get("exterior"), dict) else {}
    fallback = style.get("exterior_fallback") if isinstance(style.get("exterior_fallback"), dict) else EXTERIOR_FALLBACK
    words, _ = V.brief_value(building, brief, "exterior")
    words = words if isinstance(words, dict) else {}
    out: dict = {}
    for slot in EXTERIOR_SLOTS:
        look, warnings = None, []
        if slot == "facade":
            whole = [f for f in facade.get("faces") or [] if isinstance(f, dict) and f.get("material")
                     and (f.get("side") or "all") == "all" and not f.get("wall_id") and not f.get("z_range")]
            if whole:
                f = whole[0]
                look = _look(f["material"], f.get("colour"), "documents", f"facade.faces: the whole facade "
                             f"({f.get('source') or 'drawn'})", evidence=f.get("evidence"))
        elif slot == "roof" and roof.get("covering"):
            look = _look(roof["covering"], roof.get("covering_colour"), "documents",
                         f"roof.covering ({roof.get('covering_source') or 'drawn'})")
        phrase = str(words.get(slot) or "").strip()
        e = ext.get(slot)
        if look is None and phrase:
            if isinstance(e, dict) and e.get("source") == "brief" and (e.get("material") or e.get("slug")) \
                    and not e.get("assumed"):
                # The style profile read the same words (track C): its entry, with the asset it fetched (review
                # #29/#34: the scene, style.json and the fetched assets agree).
                look = _look(e.get("material") or e.get("slug"), e.get("colour"), "brief",
                             f"brief exterior.{slot}: {phrase!r} (as the style profile reads it)", asset=e.get("asset"))
            else:
                found = look_from_words(slot, phrase)
                if found:
                    look = _look(found["material"], found["colour"], "brief", f"brief exterior.{slot}: {phrase!r}",
                                 asset=_asset_of(found["material"]))
                else:
                    warnings.append(f"brief exterior.{slot} {phrase!r}: no known material word; the next source "
                                    f"decides")
        if look is None and isinstance(e, dict) and (e.get("material") or e.get("slug")) and not e.get("assumed"):
            src = "brief" if e.get("source") == "brief" else "style"
            look = _look(e.get("material") or e.get("slug"), e.get("colour"), src, f"style profile exterior.{slot}",
                         asset=e.get("asset"))
        if look is None and isinstance(e, dict) and (e.get("material") or e.get("slug")):
            look = _look(e.get("material") or e.get("slug"), e.get("colour"), "fallback",
                         f"style profile exterior.{slot} (assumed)", asset=e.get("asset"))
        if look is None:
            fb = fallback.get(slot, EXTERIOR_FALLBACK.get(slot))
            if fb == "interior":
                inside = style.get(slot) if isinstance(style.get(slot), dict) else {}
                default = "painted_metal_white" if slot == "window_frame" else "wood_oak_light"
                look = _look(inside.get("material") or default, inside.get("colour"), "fallback",
                             f"style.exterior_fallback: the interior {slot} seen from outside",
                             asset=inside.get("asset"))
            else:
                fb = fb if isinstance(fb, dict) else {}
                colour, rgb, how = fb.get("colour"), None, None
                if colour == "walls":
                    colour, rgb, how = _wall_colour(style)
                reason = f"style.exterior_fallback: {fb.get('material')}" + (f" in {colour}" if colour else "") + \
                         (f" ({how})" if how else "")
                look = _look(fb.get("material") or "render", colour, "fallback", reason, rgb=rgb)
        if warnings:
            look["warnings"] = warnings
        out[slot] = look
    for name, (slug, colour, reason) in BUILD_LOOKS.items():
        out[name] = _look(slug, colour, "build", reason)
    out["plot_wall"] = dict(out["facade"], source="build", assumed=True, evidence=[],
                            reason="plot wall finish not drawn: the facade's look")
    return out


# --------------------------------------------------------------------------
# The model
# --------------------------------------------------------------------------

class ExteriorModel:
    """Triangles with labels (``LABELS``) plus the solids used for the inside tests (pure numpy)."""

    def __init__(self):
        self.tris: list = []
        self.labels: list[int] = []
        self.prisms: list[tuple] = []          # (outline, z0, top planes or None, z1) of the building
        self.roof: Optional[dict] = None        # the roof model
        self.walls: list[tuple] = []            # plot walls: (start, end, half thickness, z top)
        self.trees: list[tuple] = []            # (centre, rx, ry, z0 crown, z1 crown, trunk radius, ground z)
        self.terrain: Optional[dict] = None
        self.outline: list = []
        self.z_range = (0.0, 0.0)
        self._arrays = None

    def add_mesh(self, verts, faces, label: str) -> None:
        code = LABELS[label]
        for f in faces:
            for k in range(1, len(f) - 1):
                self.tris.append((verts[f[0]], verts[f[k]], verts[f[k + 1]]))
                self.labels.append(code)
        self._arrays = None

    def arrays(self):
        if self._arrays is None:
            t = np.asarray(self.tris, dtype=np.float64).reshape(-1, 3, 3)
            self._arrays = (t[:, 0], t[:, 1] - t[:, 0], t[:, 2] - t[:, 0], np.asarray(self.labels, dtype=np.int32))
        return self._arrays

    def cast(self, origin, dirs: np.ndarray, skip: Sequence[str] = ()) -> tuple[np.ndarray, np.ndarray]:
        """``(labels, t)`` of rays ``origin + t d`` (Moller-Trumbore over every triangle); label 0 and t = inf
        where nothing is hit. ``skip``: labels to look through."""
        v0, e1, e2, lab = self.arrays()
        d = np.asarray(dirs, dtype=np.float64).reshape(-1, 3)
        n = d.shape[0]
        best_t = np.full(n, np.inf)
        best_l = np.zeros(n, dtype=np.int32)
        if not len(lab):
            return best_l, best_t
        keep = ~np.isin(lab, [LABELS[s] for s in skip]) if skip else np.ones(len(lab), dtype=bool)
        v0, e1, e2, lab = v0[keep], e1[keep], e2[keep], lab[keep]
        o = np.asarray(origin, dtype=np.float64)
        for start in range(0, len(lab), 4096):
            sl = slice(start, start + 4096)
            a0, a1, a2, al = v0[sl], e1[sl], e2[sl], lab[sl]
            p = np.cross(d[:, None, :], a2[None, :, :])                     # n x m x 3
            det = np.einsum("ijk,jk->ij", p, a1)
            with np.errstate(divide="ignore", invalid="ignore"):
                inv = 1.0 / det
                s = o[None, :] - a0                                           # m x 3
                u = np.einsum("ijk,jk->ij", p, s) * inv
                q = np.cross(s, a1)                                           # m x 3
                v = np.einsum("ik,jk->ij", d, q) * inv
                t = np.einsum("jk,jk->j", a2, q)[None, :] * inv
                ok = (np.abs(det) > 1e-12) & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
            t = np.where(ok, t, np.inf)
            j = np.argmin(t, axis=1)
            tj = t[np.arange(n), j]
            closer = tj < best_t
            best_t = np.where(closer, tj, best_t)
            best_l = np.where(closer, al[j], best_l)
        return best_l, best_t

    # ------------------------------------------------------------------
    def inside(self, p) -> Optional[str]:
        """What solid ``p`` is in (or within ``CLEARANCE`` of a plot wall), None when free."""
        x, y, z = (float(v) for v in p)
        for outline, z0, planes, z1 in self.prisms:
            if z0 - CLEARANCE <= z <= z1 + CLEARANCE and (G.point_in_polygon((x, y), outline)
                                                          or geom2d.distance_to_polygon_edges((x, y), outline) < CLEARANCE):
                top = z1 if planes is None else min(z1, R.surface_z(planes, x, y))
                if z <= top + CLEARANCE:
                    return "building"
        if self.roof is not None and self.roof.get("equations") and G.point_in_polygon((x, y), self.roof["outline"]):
            top = R.surface_z(self.roof["equations"], x, y)
            if top - self.roof["thickness"] - CLEARANCE <= z <= top + CLEARANCE:
                return "roof"
        for (a, b, half, ztop) in self.walls:
            if G.point_segment_distance((x, y), a, b) < half + CLEARANCE and z <= ztop + CLEARANCE:
                return "plot_wall"
        for (cx, cy), rx, ry, z0, z1, trunk, gz in self.trees:
            zc, rz = (z0 + z1) / 2.0, (z1 - z0) / 2.0
            if ((x - cx) / (rx + CLEARANCE)) ** 2 + ((y - cy) / (ry + CLEARANCE)) ** 2 + \
                    ((z - zc) / (rz + CLEARANCE)) ** 2 <= 1.0:
                return "tree"
            if math.hypot(x - cx, y - cy) < trunk + CLEARANCE and gz <= z <= z0:
                return "tree"
        if self.terrain is not None and z < S.ground_z(self.terrain, x, y) + 0.5:
            return "ground"
        return None


def level_prisms(building: dict, levels: Sequence[dict], roof_model: Optional[dict]) -> list[tuple]:
    """``[(outline, z0, top planes or None, z1)]``: per level its outer outline (``geom2d.wall_outline``)
    from its floor (minus the slab under it) to the next floor; the level under the roof up to the roof
    underside (clipped by its planes), a top level without roof to its ceiling + 0.3 m."""
    out = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    slabs = {s.get("above_level_id"): s for s in building.get("slabs") or []}
    for i, lv in enumerate(order):
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lv["id"]]
        outline, _ = geom2d.wall_outline(walls)
        if len(outline) < 3:
            continue
        z0 = float(lv["elevation"]) - float((slabs.get(lv["id"]) or {}).get("thickness") or 0.0)
        planes = None
        if i + 1 < len(order):
            z1 = float(order[i + 1]["elevation"])
        elif roof_model is not None and roof_model.get("convex") and roof_model.get("over_level_id") == lv["id"]:
            planes = R.underside(roof_model)
            # the highest underside point is a plane corner (the ridge), not an outline corner
            z1 = max(R.surface_z(planes, float(p[0]), float(p[1])) for pl in roof_model["planes"] for p in pl["points"])
        else:
            z1 = float(lv["elevation"]) + float(lv["ceiling_height"]) + 0.3
        out.append((outline, z0, planes, z1))
    return out


def build_model(building: dict, levels: Sequence[dict], roof_model: Optional[dict], site_plan: Optional[dict]
                ) -> ExteriorModel:
    """The ``ExteriorModel`` of a variant (pure): its levels, roof, plot walls, trees and a coarse ground."""
    m = ExteriorModel()
    m.roof = roof_model if roof_model and roof_model.get("convex") else None
    for outline, z0, planes, z1 in level_prisms(building, levels, roof_model):
        m.prisms.append((outline, z0, planes, z1))
        for piece in geom2d.convex_pieces(outline):
            v, f = geom2d.prism(piece, z0, z1)
            if planes is not None:
                v, f = R.clip_solid_below(v, f, planes)
            m.add_mesh(v, f, "building")
        m.outline = outline if not m.outline or G.polygon_area(outline) > G.polygon_area(m.outline) else m.outline
    if m.roof is not None:
        v, f, slots = R.roof_solid(m.roof)
        m.add_mesh(v, [face for face, s in zip(f, slots) if s != R.SLOT_SOFFIT], "building")
    zs = [z for p in m.prisms for z in (p[1], p[3])] + ([m.roof["ridge_z"]] if m.roof and m.roof.get("ridge_z") else [])
    m.z_range = (min(zs), max(zs)) if zs else (0.0, 3.0)
    if site_plan is not None:
        m.terrain = site_plan["terrain"]
        ext = site_plan["extent"]
        v, f = S.draped_faces(ext, [site_plan["outline"]], m.terrain, step=max(4.0, S.grid_step(ext)))
        m.add_mesh(v, f, "ground")
        for wall in site_plan["plot_walls"]:
            v, f, info = S.plot_wall_parts(wall, m.terrain)
            m.add_mesh(v, f, "plot_wall")
            m.walls.append((tuple(wall["start"]), tuple(wall["end"]), info["thickness"] / 2.0, info["z_range"][1]))
        for seg in (site_plan.get("inferred") or {}).get("boundary") or []:     # Milestone 11: hedge or fence
            v, f, info = S.boundary_parts(seg, m.terrain)
            m.add_mesh(v, f, "plot_wall")
            half = (S.INFERRED["hedge_thickness"] if seg["kind"] == "hedge" else S.INFERRED["fence_post"]) / 2.0
            m.walls.append((tuple(seg["start"]), tuple(seg["end"]), half, info["z_range"][1]))
        for item in site_plan["trees"]:
            parts = S.tree_parts(item, m.terrain)
            for mesh in (parts["trunk"], parts["crown"]):
                if mesh is not None:
                    m.add_mesh(*mesh, "tree")
            if parts["trunk"] is not None:
                size = [float(v) for v in (item.get("size") or [1.0, 1.0])[:2]]
                z0, z1 = parts["crown_z"]
                m.trees.append(((float(item["center"][0]), float(item["center"][1])), size[0] / 2.0, size[1] / 2.0,
                                z0, z1, S.DEFAULTS["trunk_radius"], parts["ground_z"]))
    return m


# --------------------------------------------------------------------------
# Framing and checks
# --------------------------------------------------------------------------

def _basis(position, target) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f = np.asarray(target, dtype=np.float64) - np.asarray(position, dtype=np.float64)
    f /= np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    r = np.array([1.0, 0.0, 0.0]) if np.linalg.norm(r) < 1e-9 else r / np.linalg.norm(r)
    return f, r, np.cross(r, f)


def building_points(model: ExteriorModel) -> np.ndarray:
    """Corner points of the building (every prism corner at its bottom and top, the roof outline at the
    eaves and the ridge points) for the framing."""
    pts = []
    for outline, z0, planes, z1 in model.prisms:
        for x, y in outline:
            top = z1 if planes is None else min(z1, R.surface_z(planes, x, y))
            # The lowest ground just outside the corner: a facade open to a lower side shows down to it.
            gz = min(S.ground_z(model.terrain, x + dx, y + dy) for dx in (-0.3, 0.3) for dy in (-0.3, 0.3)) \
                if model.terrain is not None else z0
            pts += [(x, y, max(z0, gz)), (x, y, top)]
    if model.roof is not None:
        for plane in model.roof["planes"]:
            pts += [tuple(float(c) for c in p) for p in plane["points"]]
    return np.asarray(pts, dtype=np.float64)


def frame(position, target, points: np.ndarray, level: bool = True) -> tuple[float, float, list, Optional[str]]:
    """``(lens_mm, shift_y, target, warning)`` that fit ``points`` into the frame from ``position``: the yaw
    re-centred on the points' horizontal extent; a level camera (``level``) keeps pitch 0 and centres the
    points vertically with the lens shift (at most ``MAX_SHIFT_Y``); the lens is the longest one in
    ``LENS_RANGE_MM`` with the points within ``FRAME_FILL`` of the frame."""
    pos = np.asarray(position, dtype=np.float64)
    tgt = np.asarray(target, dtype=np.float64)
    if level:
        tgt = np.array([tgt[0], tgt[1], pos[2]])
    for _ in range(2):                                       # re-centre the yaw on the horizontal extent
        f, r, u = _basis(pos, tgt)
        v = points - pos
        depth = v @ f
        ok = depth > 0.1
        if not ok.any():
            return LENS_RANGE_MM[0], 0.0, tgt.tolist(), "the building is behind the camera"
        a = (v[ok] @ r) / depth[ok]
        ac = (a.min() + a.max()) / 2.0
        dist = np.linalg.norm(tgt - pos)
        yaw_turn = math.atan(ac)
        c, s = math.cos(-yaw_turn), math.sin(-yaw_turn)
        d = tgt - pos
        tgt = pos + np.array([c * d[0] - s * d[1], s * d[0] + c * d[1], d[2]]) * (dist / max(np.linalg.norm(d), 1e-9))
    f, r, u = _basis(pos, tgt)
    v = points - pos
    depth = v @ f
    ok = depth > 0.1
    a = (v[ok] @ r) / depth[ok]
    b = (v[ok] @ u) / depth[ok]
    warning = None
    th_h = max(abs(a.min()), abs(a.max())) / FRAME_FILL
    aspect = RESOLUTION[1] / RESOLUTION[0]
    shift_y = 0.0
    if level:
        bc = (b.min() + b.max()) / 2.0
        hb = (b.max() - b.min()) / 2.0 / FRAME_FILL
        th = max(th_h, hb / aspect, 1e-6)
        lens = SENSOR_MM / (2.0 * th)
        lens = min(LENS_RANGE_MM[1], max(LENS_RANGE_MM[0], lens))
        shift_y = bc * lens / SENSOR_MM
        if abs(shift_y) > MAX_SHIFT_Y:
            warning = f"lens shift {shift_y:+.2f} limited to {math.copysign(MAX_SHIFT_Y, shift_y):+.2f}"
            shift_y = math.copysign(MAX_SHIFT_Y, shift_y)
    else:
        hb = max(abs(b.min()), abs(b.max())) / FRAME_FILL
        th = max(th_h, hb / aspect, 1e-6)
        lens = min(LENS_RANGE_MM[1], max(LENS_RANGE_MM[0], SENSOR_MM / (2.0 * th)))
    if SENSOR_MM / (2.0 * th) < LENS_RANGE_MM[0] - 1e-6:
        warning = (warning + "; " if warning else "") + f"the building does not fit at {LENS_RANGE_MM[0]:g} mm"
    return round(float(lens), 2), round(float(shift_y), 4), [round(float(c), 4) for c in tgt], warning


def frame_fixed(position, target, points: np.ndarray, lens: float) -> dict:
    """A level camera with a fixed ``lens`` (Milestone 11 E14): the yaw re-centred on the points' horizontal extent
    (as ``frame``), the vertical lens shift that centres them (at most ``MAX_SHIFT_Y``). Returns ``{"lens_mm",
    "shift_y", "target", "fill": the share of the frame width the points span, "fits": every point in the frame,
    "warning"}``."""
    pos = np.asarray(position, dtype=np.float64)
    tgt = np.array([float(target[0]), float(target[1]), pos[2]])
    for _ in range(2):
        f, r, u = _basis(pos, tgt)
        v = points - pos
        depth = v @ f
        ok = depth > 0.1
        if not ok.any():
            return {"lens_mm": lens, "shift_y": 0.0, "target": tgt.tolist(), "fill": 0.0, "fits": False,
                    "warning": "the building is behind the camera"}
        a = (v[ok] @ r) / depth[ok]
        ac = (a.min() + a.max()) / 2.0
        dist = np.linalg.norm(tgt - pos)
        c, s_ = math.cos(-math.atan(ac)), math.sin(-math.atan(ac))
        d = tgt - pos
        tgt = pos + np.array([c * d[0] - s_ * d[1], s_ * d[0] + c * d[1], d[2]]) * (dist / max(np.linalg.norm(d), 1e-9))
    f, r, u = _basis(pos, tgt)
    v = points - pos
    depth = v @ f
    ok = depth > 0.1
    a = (v[ok] @ r) / depth[ok]
    b = (v[ok] @ u) / depth[ok]
    tan_h = SENSOR_MM / (2.0 * lens)
    tan_v = tan_h * RESOLUTION[1] / RESOLUTION[0]
    fill = float((a.max() - a.min()) / (2.0 * tan_h))
    bc = (b.min() + b.max()) / 2.0
    shift_y = bc * lens / SENSOR_MM
    warning = None
    if abs(shift_y) > MAX_SHIFT_Y:
        warning = f"lens shift {shift_y:+.2f} limited to {math.copysign(MAX_SHIFT_Y, shift_y):+.2f}"
        shift_y = math.copysign(MAX_SHIFT_Y, shift_y)
    centre_b = shift_y * SENSOR_MM / lens
    fits = bool(ok.all() and fill <= 1.0 and b.max() - centre_b <= tan_v and centre_b - b.min() <= tan_v)
    return {"lens_mm": float(lens), "shift_y": round(float(shift_y), 4), "target": [round(float(c), 4) for c in tgt],
            "fill": round(fill, 4), "fits": fits, "warning": warning}


def fill_distance(model: "ExteriorModel", origin, direction, aim, points: np.ndarray, lens: float = EYE_LENS_MM
                  ) -> tuple[float, dict]:
    """The distance along ``direction`` from ``origin`` (a building corner or a facade centre) at which a level
    camera with ``lens`` sees the whole building filling about ``FILL_TARGET`` of the frame width (the first scanned
    distance with the fill at most ``FILL_TARGET`` and every point in the frame); ``(distance, frame_fixed
    record)``."""
    lo, hi, step = DISTANCE_SCAN_M
    best = None
    dist = lo
    while dist <= hi + 1e-9:
        p = (origin[0] + direction[0] * dist, origin[1] + direction[1] * dist)
        pos = (p[0], p[1], _eye(model, *p))
        rec = frame_fixed(pos, aim, points, lens)
        best = (dist, rec)
        if rec["fits"] and rec["fill"] <= FILL_TARGET + 1e-9:
            return dist, rec
        dist += step
    return best


def view_check(model: ExteriorModel, position, target, lens: float, shift_y: float, aim) -> dict:
    """The ray check of a camera: ``{"building_share", "blocked", "aim_visible", "ok", "why"}``."""
    from wenart.blender import camsearch

    a, b = camsearch.ray_grid(RAY_GRID, lens_mm=lens, sensor_mm=SENSOR_MM, resolution=RESOLUTION, shift_y=shift_y)
    dirs = camsearch.camera_directions(position, target, a, b)
    labels, _t = model.cast(position, dirs)
    clear, _ = model.cast(position, dirs, skip=("plot_wall", "tree"))
    building = labels == LABELS["building"]
    reach = clear == LABELS["building"]
    blocked = float(((labels != LABELS["building"]) & reach).sum()) / max(1, int(reach.sum()))
    share = float(building.mean())
    d = np.asarray(aim, dtype=np.float64) - np.asarray(position, dtype=np.float64)
    lab, _ = model.cast(position, d[None, :] / np.linalg.norm(d))
    aim_ok = int(lab[0]) == LABELS["building"]
    why = None
    if blocked > MAX_BLOCKED:
        why = f"{blocked:.0%} of the view of the building is blocked by trees or the plot wall"
    elif share < MIN_BUILDING_SHARE:
        why = f"the building fills {share:.0%} of the frame (< {MIN_BUILDING_SHARE:.0%})"
    elif not aim_ok:
        names = {v: k for k, v in LABELS.items()}
        why = f"the line of sight to the building ends on {names.get(int(lab[0]), 'nothing')}"
    return {"building_share": round(share, 4), "blocked": round(blocked, 4), "aim_visible": aim_ok,
            "ok": why is None, "why": why}


def visible_openings(model: ExteriorModel, building: dict, levels: Sequence[dict], position, target, lens: float,
                     shift_y: float) -> list[str]:
    """Outer openings the camera sees: on a wall face turned to the camera, centre inside the frame, the
    ray to it reaching the building first (it may cross nothing else)."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    ids = {lv["id"]: lv for lv in levels}
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    tangents = geom2d.frustum_tangents(lens, SENSOR_MM, RESOLUTION)
    out = []
    pos = np.asarray(position, dtype=np.float64)
    for o in building.get("openings") or []:
        wall = walls.get(o.get("wall_id"))
        lv = ids.get(o.get("level_id"))
        if wall is None or lv is None or o.get("type") not in ("door", "window"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        outward = S.outward_side(wall, model.outline, (cx, cy)) if model.outline else None
        if outward is None:
            continue
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = opening_vertical(o, lv, above)
        half = float(wall["thickness"]) / 2.0
        p = np.array([cx + outward[0] * (half + 0.02), cy + outward[1] * (half + 0.02), (bottom + top) / 2.0])
        if (pos[0] - p[0]) * outward[0] + (pos[1] - p[1]) * outward[1] <= 0.0:
            continue
        if not geom2d.point_in_frustum(p, position, target, tangents, shift_y=shift_y):
            continue
        d = p - pos
        dist = float(np.linalg.norm(d))
        lab, t = model.cast(pos, (d / dist)[None, :])
        if not np.isfinite(t[0]) or t[0] >= dist - 0.05 or int(lab[0]) == LABELS["building"] and t[0] >= dist - 0.4:
            out.append(o["id"])
    return out


# --------------------------------------------------------------------------
# Candidates
# --------------------------------------------------------------------------

def _rect(model: ExteriorModel) -> dict:
    return geom2d.oriented_rectangle(model.outline)


def _eye(model: ExteriorModel, x: float, y: float) -> float:
    gz = S.ground_z(model.terrain, x, y) if model.terrain is not None else model.z_range[0]
    return gz + EYE_HEIGHT


def _plot_corner(plot: Sequence, centre, direction) -> Optional[tuple[float, float]]:
    """The plot corner along ``direction`` from the building centre (within 35 degrees), moved
    ``PLOT_CORNER_INSET`` towards the plot's inside."""
    best, best_dot = None, math.cos(math.radians(35.0))
    pts = geom2d.ccw(plot)
    for i, p in enumerate(pts):
        d = (p[0] - centre[0], p[1] - centre[1])
        n = math.hypot(*d)
        if n < 1e-6:
            continue
        dot = (d[0] * direction[0] + d[1] * direction[1]) / n
        if dot > best_dot:
            prev, nxt = pts[i - 1], pts[(i + 1) % len(pts)]
            bis = (prev[0] - p[0]) / max(G.distance(prev, p), 1e-9) + (nxt[0] - p[0]) / max(G.distance(nxt, p), 1e-9), \
                  (prev[1] - p[1]) / max(G.distance(prev, p), 1e-9) + (nxt[1] - p[1]) / max(G.distance(nxt, p), 1e-9)
            bn = math.hypot(*bis) or 1.0
            inset = PLOT_CORNER_INSET * math.sqrt(2.0)
            best, best_dot = (p[0] + bis[0] / bn * inset, p[1] + bis[1] / bn * inset), dot
    return best


def _opening_counts(building: dict, levels: Sequence[dict], outline) -> dict[str, int]:
    """Outer openings per facade axis (``+x``, ``-x``, ``+y``, ``-y``)."""
    from wenart.blender.shell import opening_centre_on_wall

    ids = {lv["id"] for lv in levels}
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    counts = {k: 0 for k in S.AXES}
    for o in building.get("openings") or []:
        wall = walls.get(o.get("wall_id"))
        if wall is None or o.get("level_id") not in ids:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        out = S.outward_side(wall, outline, (cx, cy))
        if out is not None:
            counts[S.nearest_axis(out)] += 1
    return counts


def _try(model, building, levels, name, view, candidates, aim, level_cam=True, extra=None,
         lens_mm: Optional[float] = None) -> dict:
    """The first candidate position that is free and sees the building; the plan or the drop record (the
    camera record with ``dropped: true`` and ``dropped_reason``). ``lens_mm`` (Milestone 11): a fixed lens for a
    level camera (``frame_fixed``; the plan records the ``fill``)."""
    extra = dict({"sides": [], "region_id": None, "variant": None}, **(extra or {}))
    pts = building_points(model)
    reasons = []
    for k, (pos, how) in enumerate(candidates):
        inside = model.inside(pos)
        if inside:
            reasons.append(f"{how}: inside the {inside}")
            continue
        fill = None
        if lens_mm is not None and level_cam:
            rec = frame_fixed(pos, aim, pts, lens_mm)
            lens, shift_y, target, warn, fill = rec["lens_mm"], rec["shift_y"], rec["target"], rec["warning"], rec["fill"]
            if not rec["fits"]:
                warn = "; ".join(w for w in (warn, "the building does not fit the frame") if w)
        else:
            lens, shift_y, target, warn = frame(pos, aim, pts, level=level_cam)
        check = view_check(model, pos, target, lens, shift_y, aim)
        if not check["ok"]:
            reasons.append(f"{how}: {check['why']}")
            continue
        warning = "; ".join([w for w in ([warn] + ([f"moved: {reasons[-1]}"] if reasons else [])) if w]) or None
        pitch = math.degrees(math.atan2(target[2] - pos[2], math.hypot(target[0] - pos[0], target[1] - pos[1])))
        plan = {"name": name, "kind": KIND, "view": view, "room_id": None, "level_id": None,
                "index": int(name.split("_")[1]), "position": [round(float(c), 4) for c in pos], "target": target,
                "lens_mm": lens, "sensor_mm": SENSOR_MM, "resolution": list(RESOLUTION), "shift_x": 0.0,
                "shift_y": shift_y, "pitch_deg": round(pitch, 2), "placement": how, "warning": warning,
                "visible_openings": visible_openings(model, building, levels, pos, target, lens, shift_y),
                "visible_furniture": [], "score": {**check, "tried": k + 1}, "status": "assumed",
                "dropped_reason": None}
        if fill is not None:
            plan["fill"] = fill
        plan.update(extra)
        return plan
    return {"name": name, "kind": KIND, "view": view, "room_id": None, "level_id": None,
            "index": int(name.split("_")[1]), "dropped": True, "dropped_reason": "; ".join(reasons) or "no candidate",
            **extra}


def elevation_views(building: dict) -> tuple[list[dict], list[str]]:
    """``([{"region_id", "side", "view", "outward"}], warnings)`` of the drawn elevations (``facade.elevations``,
    pure): ``view`` the direction the camera looks (building frame, unit; ``view_bearing_deg``: counter-clockwise
    from +X, else the opposite of the side's outward direction), ``outward`` its opposite. An elevation with
    neither a known side nor a bearing is a warning."""
    north, _ = S.north_deg(building)
    out, warnings = [], []
    for e in (building.get("facade") or {}).get("elevations") or []:
        if not isinstance(e, dict):
            continue
        side = e.get("side")
        bearing = e.get("view_bearing_deg")
        if bearing is not None:
            a = math.radians(float(bearing))
            view = (math.cos(a), math.sin(a))
        else:
            d = S.side_direction(side, north)
            if d is None:
                warnings.append(f"elevation {e.get('region_id')}: side {side!r} without a view bearing: no view")
                continue
            view = (-d[0], -d[1])
        out.append({"region_id": e.get("region_id"), "side": side, "view": view, "outward": (-view[0], -view[1])})
    return out, warnings


def plan_exterior(model: ExteriorModel, building: dict, levels: Sequence[dict], plot: Sequence = (),
                  variant: Optional[str] = None) -> tuple[list[dict], list[dict]]:
    """``(plans, dropped)`` of the exterior cameras of a variant (pure; module docstring). Every record has
    the scene manifest's camera fields (§1.6b row 11): ``kind`` exterior, ``room_id`` / ``level_id`` null,
    ``index``, ``variant``, ``view`` (corner / aerial / elevation), ``sides`` (the ``$defs/side`` names of the
    facades it looks at), ``region_id`` (the drawn elevation's) and ``dropped_reason`` (null for a plan)."""
    if len(model.outline) < 3:
        return [], [{"name": "ext_*", "kind": KIND, "view": None, "room_id": None, "level_id": None, "sides": [],
                     "region_id": None, "variant": variant, "dropped": True, "dropped_reason": "no building outline"}]
    rect = _rect(model)
    corners = geom2d.rectangle_corners(rect)
    cx, cy = rect["center"]
    zmid = (model.z_range[0] + model.z_range[1]) / 2.0
    north, north_src = S.north_deg(building)
    north_known = not north_src.startswith("assumed")
    plans, dropped = [], []

    def keep(plan):
        (dropped if plan.get("dropped") else plans).append(plan)

    def sides_at(corner):
        return [S.side_of(v, north, north_known) for v in _corner_axes(corner, rect)]

    terrain = model.terrain or {"kind": "flat", "z": {a: model.z_range[0] for a in S.AXES}}
    main = S.main_facade(building, levels, terrain, model.outline)
    md = main["direction"]
    pts_all = building_points(model)
    for k, corner in enumerate(corners):
        # Milestone 11 E14: the camera stands CORNER_ANGLE_DEG off the facade it faces (the main facade at the two
        # front corners, the back facade at the two back ones), at the distance where the building fills about
        # FILL_TARGET of the frame through EYE_LENS_MM (straight verticals: level, lens shift).
        n1, n2 = _corner_axes(corner, rect)
        if abs(n1[0] * md[0] + n1[1] * md[1]) < abs(n2[0] * md[0] + n2[1] * md[1]):
            n1, n2 = n2, n1
        ang = math.radians(CORNER_ANGLE_DEG)
        d = (math.cos(ang) * n1[0] + math.sin(ang) * n2[0], math.cos(ang) * n1[1] + math.sin(ang) * n2[1])
        aim = (corner[0], corner[1], zmid)
        d0, _rec = fill_distance(model, corner, d, aim, pts_all)
        facing = S.side_of(n1, north, north_known)
        cands = []
        for step in MOVE_STEPS_M:
            dist = d0 + step
            if dist < DISTANCE_SCAN_M[0]:
                continue
            p = (corner[0] + d[0] * dist, corner[1] + d[1] * dist)
            cands.append(((p[0], p[1], _eye(model, *p)), f"{dist:.1f} m from the building corner, "
                                                         f"{CORNER_ANGLE_DEG:g} degrees off the {facing} facade"))
        keep(_try(model, building, levels, f"ext_{k + 1}", "corner", cands, aim, lens_mm=EYE_LENS_MM,
                  extra={"corner": k + 1, "sides": sides_at(corner), "variant": variant,
                         "faces": facing, "main_facade": main["axis"]}))

    counts = _opening_counts(building, levels, model.outline)
    best = max(range(4), key=lambda k: (sum(counts[S.nearest_axis(v)] for v in _corner_axes(corners[k], rect)), -k))
    corner = corners[best]
    d = (corner[0] - cx, corner[1] - cy)
    n = math.hypot(*d)
    d = (d[0] / n, d[1] / n)
    pts = building_points(model)
    radius = float(np.max(np.linalg.norm(pts - np.array([cx, cy, zmid]), axis=1)))
    cands = []
    for scale in (1.0, 1.2, 1.5):
        dist = radius / math.tan(math.radians(20.0)) * scale
        h = dist * math.sin(math.radians(AERIAL_PITCH_DEG))
        horiz = dist * math.cos(math.radians(AERIAL_PITCH_DEG))
        cands.append(((cx + d[0] * horiz, cy + d[1] * horiz, zmid + h), f"aerial {dist:.1f} m from the centre"))
    if flat_cut(building):
        # Milestone 12 (docs/milestone12.md §3.4, U2): a single drawn ground floor: no aerial view (it would show the
        # cut roof of a building whose upper floors are not drawn); eye-level views of the entrances instead.
        dropped.append({"name": "ext_5", "kind": KIND, "view": "aerial", "room_id": None, "level_id": None,
                        "index": 5, "dropped": True, "corner": best + 1, "sides": sides_at(corner),
                        "region_id": None, "variant": variant,
                        "dropped_reason": "flat_cut roof (upper floors not drawn): no aerial view"})
    else:
        keep(_try(model, building, levels, "ext_5", "aerial", cands, (cx, cy, zmid), level_cam=False,
                  extra={"corner": best + 1, "sides": sides_at(corner), "variant": variant}))

    views, _warnings = elevation_views(building)
    height = model.z_range[1] - model.z_range[0]
    tan_h = SENSOR_MM / 2.0 / 28.0
    for i, ev in enumerate(views):
        name = f"ext_{6 + i}"
        u = ev["outward"]
        w = (-u[1], u[0])
        along = [p[0] * u[0] + p[1] * u[1] for p in model.outline]
        across = [p[0] * w[0] + p[1] * w[1] for p in model.outline]
        a, b = max(along), (min(across) + max(across)) / 2.0
        face = (u[0] * a + w[0] * b, u[1] * a + w[1] * b)
        width = max(across) - min(across)
        fit = max(width / 2.0 / tan_h / FRAME_FILL, height / 2.0 / (tan_h * RESOLUTION[1] / RESOLUTION[0]) / FRAME_FILL)
        side = ev["side"] or S.side_of(u, north, north_known)
        cands = []
        for frac in ELEVATION_STEPS:
            dist = max(4.0, fit * frac)
            p = (face[0] + u[0] * dist, face[1] + u[1] * dist)
            cands.append(((p[0], p[1], _eye(model, *p)), f"{dist:.1f} m in front of the {side} facade"))
        keep(_try(model, building, levels, name, "elevation", cands, (face[0], face[1], zmid),
                  extra={"side": side, "sides": [side], "region_id": ev["region_id"], "variant": variant}))

    # Milestone 11 E14: one frontal view of the entrance facade, unless a drawn elevation already looks at it.
    main_side = S.side_of(md, north, north_known)
    if not any(ev["outward"][0] * md[0] + ev["outward"][1] * md[1] > math.cos(math.radians(30.0)) for ev in views):
        along = [p[0] * md[0] + p[1] * md[1] for p in model.outline]
        w = (-md[1], md[0])
        across = [p[0] * w[0] + p[1] * w[1] for p in model.outline]
        a, b = max(along), (min(across) + max(across)) / 2.0
        face = (md[0] * a + w[0] * b, md[1] * a + w[1] * b)
        aim = (face[0], face[1], zmid)
        d0, _rec = fill_distance(model, face, md, aim, pts_all)
        cands = []
        for step in MOVE_STEPS_M:
            dist = d0 + step
            if dist < DISTANCE_SCAN_M[0]:
                continue
            p = (face[0] + md[0] * dist, face[1] + md[1] * dist)
            cands.append(((p[0], p[1], _eye(model, *p)), f"{dist:.1f} m in front of the {main_side} (entrance) facade"))
        keep(_try(model, building, levels, f"ext_{6 + len(views)}", "frontal", cands, aim, lens_mm=EYE_LENS_MM,
                  extra={"side": main_side, "sides": [main_side], "variant": variant, "main_facade": main["axis"],
                         "main_facade_source": main["source"]}))
    if flat_cut(building):
        nxt = max([p["index"] for p in plans + dropped if isinstance(p.get("index"), int)] + [5]) + 1
        for k, (pos_cands, aim, ent) in enumerate(entrance_views(building, model)):
            side = S.side_of(ent["outward"], north, north_known)
            keep(_try(model, building, levels, f"ext_{nxt + k}", "entrance", pos_cands, aim, lens_mm=EYE_LENS_MM,
                      extra={"side": side, "sides": [side], "variant": variant, "entrance": ent["door_id"]}))
    return plans, dropped


ENTRANCE_VIEWS_MAX = 3
ENTRANCE_VIEW_M = (8.0, 10.0, 12.0, 6.0)             # eye-level distances tried in front of an entrance


def flat_cut(building: dict) -> bool:
    """True for a building that ends with a ``flat_cut`` roof (Milestone 12: a single drawn ground floor)."""
    roof = building.get("roof")
    return isinstance(roof, dict) and roof.get("kind") == "flat_cut"


def entrance_views(building: dict, model: "ExteriorModel") -> list[tuple[list, tuple, dict]]:
    """Milestone 12 (pure): ``[(candidates, aim, entrance)]`` of the eye-level views framing the entrances of
    ``site.entrances`` (the main one first, at most ``ENTRANCE_VIEWS_MAX``): the camera 20 degrees off the door's
    axis at ``ENTRANCE_VIEW_M``, aimed at the door's middle 1.2 m above its threshold."""
    recs = [r for r in ((building.get("site") or {}).get("entrances") or [])
            if isinstance(r, dict) and r.get("centre") and r.get("outward") and not r.get("into_air")
            and not r.get("below_ground")]
    recs.sort(key=lambda r: (not r.get("main"), r["door_id"]))
    out = []
    ang = math.radians(20.0)
    for r in recs[:ENTRANCE_VIEWS_MAX]:
        o = (float(r["outward"][0]), float(r["outward"][1]))
        u = (-o[1], o[0])
        d = (math.cos(ang) * o[0] + math.sin(ang) * u[0], math.cos(ang) * o[1] + math.sin(ang) * u[1])
        face = r.get("face") or r["centre"]
        aim = (float(face[0]), float(face[1]), float(r["threshold_z"]) + 1.2)
        cands = []
        for dist in ENTRANCE_VIEW_M:
            p = (float(face[0]) + d[0] * dist, float(face[1]) + d[1] * dist)
            cands.append(((p[0], p[1], _eye(model, *p)), f"{dist:.1f} m in front of the entrance {r['door_id']}"))
        out.append((cands, aim, r))
    return out


def _corner_axes(corner, rect) -> list[tuple[float, float]]:
    """The two outward facade directions that meet at a rectangle corner."""
    (cx, cy), u, v = rect["center"], rect["u"], rect["v"]
    su = 1.0 if (corner[0] - cx) * u[0] + (corner[1] - cy) * u[1] > 0 else -1.0
    sv = 1.0 if (corner[0] - cx) * v[0] + (corner[1] - cy) * v[1] > 0 else -1.0
    return [(u[0] * su, u[1] * su), (v[0] * sv, v[1] * sv)]


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

def create_cameras(plans: Sequence[dict], collection, manifest_objects: list) -> list:
    """One camera object per exterior plan (kind ``camera``, ``wenart_camera_kind`` = ``exterior``; no room,
    no level): lens, sensor, the vertical lens shift, clip end ``CLIP_END``."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common

    created = []
    for plan in plans:
        cam = bpy.data.cameras.new(plan["name"])
        cam.lens = plan["lens_mm"]
        cam.sensor_width = plan["sensor_mm"]
        cam.sensor_fit = "HORIZONTAL"
        cam.shift_x = float(plan.get("shift_x") or 0.0)
        cam.shift_y = float(plan.get("shift_y") or 0.0)
        cam.clip_start = 0.1
        cam.clip_end = CLIP_END
        ob = bpy.data.objects.new(plan["name"], cam)
        ob.location = Vector(plan["position"])
        direction = Vector(plan["target"]) - Vector(plan["position"])
        ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        collection.objects.link(ob)
        common.set_props(ob, wenart_id=plan["name"], kind="camera", status="assumed")
        ob["wenart_camera_kind"] = KIND
        ob["wenart_view"] = plan["view"]
        manifest_objects.append({
            "name": plan["name"], "wenart_id": plan["name"], "kind": "camera", "status": "assumed",
            "level_id": None, "element_id": None, "evidence": [], "material": None, "textured": False,
            "pass_index": None, "assumed": {"view": plan["view"], "placement": plan["placement"]},
            "camera_kind": KIND, "sides": list(plan.get("sides") or []), "region_id": plan.get("region_id"),
        })
        created.append(ob)
    return created
