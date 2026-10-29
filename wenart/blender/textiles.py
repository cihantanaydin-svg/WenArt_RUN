"""Procedural textiles: cushions and pillows, throws and duvets draped on the built host, curtains and blinds
(docs/milestone12.md §4.7, §6.4, D13 and D24 "procedural textiles"; track S).

What: pure functions (numpy, no ``bpy``) that make our own soft furnishings as meshes:

- ``cushion_mesh``: a filled cushion or pillow (two quilted faces bulging to ``t`` in the middle and meeting in a
  thin seam, the edges drawn in a little between the corners), item frame: width along X, thickness along Y,
  height along Z from 0; a lying pillow is the same mesh leaned back (``rest.pose_vertices``).
- ``drape``: a cloth sheet (a throw or a duvet) laid over the built host like a deterministic shrinkwrap: every
  vertex of a grid over the cloth's rectangle (host frame) is projected down onto the host by a ray (``offset``
  5 mm above the hit, with modelled folds: smooth fixed wrinkles), vertices beyond the top hang down over the
  edge by the length they reach past it and are pushed out of the host's side by horizontal rays.
- ``cloth_solid``: the draped sheet with a thickness (two layers along the vertex normals, closed at the rim).
- ``duvet_and_pillows``: the bedding of a bed whose model has none (§4.7: "every bed whose model has no bedding
  gets a duvet and two pillows"; a single bed narrower than ``TWO_PILLOW_MIN_W`` gets one, two do not fit side by
  side): a duvet over the foot ``DUVET_SHARE`` of the mattress hanging over the sides and the foot, a turned-down
  band at its head, the pillows against the headboard (``rest.place_leaning``) on the mattress.
- ``curtain_parts``: an open pair of pleated panels under a rod (one per window, the panels' pleats a sine of
  ``PLEAT_PITCH_M``); ``blind_parts``: a roller blind (tube, panel, bottom bar) or a slatted blind (``SLAT_M``
  slats tilted ``SLAT_TILT_DEG`` with two ladder tapes).

Why: Milestone 11 used library objects for throws squashed to 5 cm (a juice machine, a bench, a "corpse": B7) and
left library beds as bare mattresses (§1.3). Our own cloth has no licence question and real proportions.

How: parts are the ``parametric`` part dicts (``verts``, ``faces``, ``key``, ``role``, ``smooth``); fabric keys use
``colour_fabric`` so the item's colour (brief or AI) applies; any CC0 fabric look of the style (``materials``).
Deterministic: fixed grids, fold phases from the sizes only. The mesh makers that need no host (``cushion_mesh``,
``lying_cushion_mesh``, ``flat_cloth``, ``cloth_solid``, ``curtain_parts``, ``blind_parts``) live in
``wenart.blender.parametric`` (its ``decor_parts`` builds them; the fit and gate stages read it without this module)
and are re-exported here; this module drapes cloth on a built host (``rest``).

29 Oct 2026 (lesson UL121, R35: "look how realistic the bed is looking full and nice"): ``bedding_set`` dresses a bed
in its style family's full set (``bedding_parts``: shams, standing pillows, accent cushions and a lumbar stacked
without rays, a deep duvet from ``drape_shaped`` with a rounded edge, folds, flutes and the overhang on its free sides,
the rolled turn-down); ``woven_throw_parts`` makes a bed's throw pair (the woven blanket, the fringed throw over it;
``_cloth`` drapes a cloth with its fringe columns). ``duvet_and_pillows`` and the plain throw stay for a call without
the family's set.

Fix round after P4b (17 Oct 2026; integration of the furniture track's ask): the pillows look for the headboard in
the bed's head half (``rest.place_leaning(bed=True)``: a footboard or a duvet roll at the foot is no headboard; P4b
real03 laid oda_01's pillow at the foot and 7 of 10 beds got no bedding). The dressing record adds each pillow's
local y (``pillow_local_y``, + = the head half) and ``head_problems`` (``bedding_head_problems``: a pillow or the
duvet's head edge in the foot half), so the scene manifest shows a misplaced bedding.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart.blender import rest
from wenart.blender.parametric import (  # noqa: F401 (the mesh makers, re-exported)
    BLIND_KINDS, CLOTH_OFFSET_M, CLOTH_STEP_M, CLOTH_THICKNESS_M, CURTAIN_LAYER_M, CURTAIN_PANEL_SHARE,
    CUSHION_GRID, EDGE_DRAW, FOLD_AMPLITUDE_M, PLEAT_DEPTH_M, PLEAT_PITCH_M, SEAM_M, SLAT_GAP_M, SLAT_M,
    SLAT_TILT_DEG, blind_parts, cloth_solid, curtain_parts, cushion_mesh, flat_cloth, fold,
    lying_cushion_mesh)
# Milestone 13: the bedding numbers live in ``parametric`` (the pure bed family v2 drapes its own duvet with them,
# ``parametric.bed_bedding_parts`` / ``box_drape_grid``); re-exported here under their Milestone 12 names.
from wenart.blender.parametric import (  # noqa: F401
    DUVET_SHARE, DUVET_SIDE_DROP_M, DUVET_THICKNESS_M, PILLOW_SIZE, PILLOW_TILT_DEG, TURN_DOWN_M, TWO_PILLOW_MIN_W,
    bed_bedding_parts, box_drape_grid)

Part = dict


# --------------------------------------------------------------------------
# Cloth draped on the host
# --------------------------------------------------------------------------


def drape(caster, host_fp: dict, rect: Sequence[float], floor_z: float, step: float = CLOTH_STEP_M,
          offset: float = CLOTH_OFFSET_M, top_band: float = rest.TOP_BAND_M,
          thickness: float = CLOTH_THICKNESS_M, nu: Optional[int] = None, nv: Optional[int] = None) -> dict:
    """A cloth over the rectangle ``rect`` = (x0, y0, x1, y1) in the host frame, draped on the host mesh.

    Returns ``{"grid": (nu + 1) x (nv + 1) x 3 world points, "on_top": bool grid, "top_z": the median top, "share":
    on-top share}``. A grid point is on top when its downward ray hits the host within ``top_band`` of the median
    top (the grid is the cloth's top: its underside, ``thickness`` lower, rests 5 mm ``offset`` + folds above the
    hit); the others hang: from the nearest on-top point (grid distance) the cloth falls by the plan length it
    reaches past it, pushed out of the host's side by a horizontal ray (offset + thickness outside the hit), never
    below the floor + 2 cm. ``nu`` / ``nv`` (29 Oct 2026, UL121): the grid's cells given (a fringed throw's columns
    fall on its ends), else ``step``."""
    x0, y0, x1, y1 = (float(v) for v in rect)
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    nu = int(nu) if nu else max(2, int(round((x1 - x0) / step)))
    nv = int(nv) if nv else max(2, int(round((y1 - y0) / step)))
    top_from = rest.host_top(caster) + rest.TOP_ABOVE_M
    local = np.zeros((nu + 1, nv + 1, 2))
    hit_z = np.full((nu + 1, nv + 1), np.nan)
    for i in range(nu + 1):
        for j in range(nv + 1):
            lx = x0 + (x1 - x0) * i / nu
            ly = y0 + (y1 - y0) * j / nv
            local[i, j] = (lx, ly)
            wx, wy = rest.to_world(hc, rot, lx, ly)
            h = caster.ray((wx, wy, top_from), (0.0, 0.0, -1.0))
            if h is not None:
                hit_z[i, j] = h[1][2]
    found = hit_z[~np.isnan(hit_z)]
    if not len(found):
        return {"grid": None, "on_top": None, "top_z": None, "share": 0.0}
    top_z = float(np.median(found))
    on_top = (~np.isnan(hit_z)) & (hit_z >= top_z - top_band)
    grid = np.zeros((nu + 1, nv + 1, 3))
    tops = [(i, j) for i in range(nu + 1) for j in range(nv + 1) if on_top[i, j]]
    if not tops:
        return {"grid": None, "on_top": on_top, "top_z": top_z, "share": 0.0}
    w, d = x1 - x0, y1 - y0
    for i, j in tops:
        lx, ly = local[i, j]
        wx, wy = rest.to_world(hc, rot, lx, ly)
        grid[i, j] = (wx, wy, hit_z[i, j] + offset + thickness + fold(lx - x0, ly - y0, w, d))
    top_arr = np.array(tops)
    for i in range(nu + 1):
        for j in range(nv + 1):
            if on_top[i, j]:
                continue
            k = int(np.argmin((top_arr[:, 0] - i) ** 2 + (top_arr[:, 1] - j) ** 2))
            ei, ej = top_arr[k]
            lx, ly = local[i, j]
            ex, ey = local[ei, ej]
            reach = math.hypot(lx - ex, ly - ey)
            ux, uy = ((lx - ex) / reach, (ly - ey) / reach) if reach > 1e-9 else (0.0, -1.0)
            z = max(float(floor_z) + 0.02, grid[ei, ej, 2] - reach)
            ox, oy = rest.direction_world(rot, ux, uy)
            ewx, ewy = rest.to_world(hc, rot, ex, ey)
            far = (ewx + ox * 1.0, ewy + oy * 1.0, z)
            side = caster.ray(far, (-ox, -oy, 0.0), 1.2)
            if side is not None and side[0] <= 1.05:          # the side at most 5 cm inside the edge
                px, py = side[1][0] + ox * (offset + thickness), side[1][1] + oy * (offset + thickness)
            else:
                px, py = ewx + ox * (offset + thickness), ewy + oy * (offset + thickness)
            grid[i, j] = (px, py, z)
    return {"grid": grid, "on_top": on_top, "top_z": top_z, "share": float(on_top.mean())}


SHAPED_STEP_M = 0.04             # 29 Oct 2026 (UL121): the duvet's grid (its rounded edge spans ~3 points)


def drape_shaped(caster, host_fp: dict, rect: Sequence[float], floor_z: float, thickness: float,
                 hem_m: float = 0.08, step: float = SHAPED_STEP_M, offset: float = CLOTH_OFFSET_M,
                 top_band: float = rest.TOP_BAND_M, rounded: bool = True) -> Optional[dict]:
    """29 Oct 2026 (UL121, R35: "a deep duvet with soft rounded edges ... hanging down the sides almost to the
    floor"): the duvet's drape. As ``drape`` (one ray down per grid point, one side ray per hanging point: no other
    ray), but every hanging point is placed at once from its nearest on-top point (numpy): it hangs by its level
    (Chebyshev) reach past it, so the corners fall as a level skirt, never piled at the floor; over the mattress edge
    the cloth rounds on an arc of the duvet's own height (``offset + thickness``) about the edge (its underside stays
    ``offset`` off the host), then falls straight; its hem stops ``hem_m`` over the floor. The side rays run just
    under the mattress top for the arc. Returns ``drape``'s record plus ``local`` (bed-local grid points),
    ``hang_s`` (the reach), ``out_dir`` (world, horizontal), ``edge_local`` (the on-top point each hangs from),
    ``arc_m``; None when no top is found."""
    x0, y0, x1, y1 = (float(v) for v in rect)
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    nu = max(2, int(round((x1 - x0) / step)))
    nv = max(2, int(round((y1 - y0) / step)))
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    lx, ly = np.meshgrid(x0 + (x1 - x0) * np.arange(nu + 1) / nu, y0 + (y1 - y0) * np.arange(nv + 1) / nv,
                         indexing="ij")
    wx, wy = hc[0] + c * lx - s * ly, hc[1] + s * lx + c * ly
    top_from = rest.host_top(caster) + rest.TOP_ABOVE_M
    hit_z = np.full((nu + 1, nv + 1), np.nan)
    (bx0, by0, _bz0), (bx1, by1, _bz1) = caster.bounds
    over = (wx >= bx0 - 0.02) & (wx <= bx1 + 0.02) & (wy >= by0 - 0.02) & (wy <= by1 + 0.02)   # a ray beside the
    for i, j in np.argwhere(over):                                                            # host hits nothing
        h = caster.ray((float(wx[i, j]), float(wy[i, j]), top_from), (0.0, 0.0, -1.0))
        if h is not None:
            hit_z[i, j] = h[1][2]
    found = hit_z[~np.isnan(hit_z)]
    if not len(found):
        return None
    top_z = float(np.median(found))
    on_top = (~np.isnan(hit_z)) & (hit_z >= top_z - top_band)
    if not on_top.any():
        return None
    rtop = float(offset) + float(thickness)
    grid = np.zeros((nu + 1, nv + 1, 3))
    grid[..., 0], grid[..., 1] = wx, wy
    grid[..., 2] = np.where(on_top, hit_z + rtop, 0.0)
    local = np.stack([lx, ly], axis=-1)
    hang_s = np.zeros((nu + 1, nv + 1))
    out_dir = np.zeros((nu + 1, nv + 1, 2))
    edge_local = local.copy()
    rho = rtop if rounded else 0.0
    arc = math.pi / 2.0 * rho
    tops = np.argwhere(on_top)
    hang = np.argwhere(~on_top)
    if len(hang):
        k = np.empty(len(hang), dtype=np.int64)
        for a in range(0, len(hang), 256):
            hh = hang[a:a + 256]
            d2 = (hh[:, 0, None] - tops[None, :, 0]) ** 2 + (hh[:, 1, None] - tops[None, :, 1]) ** 2
            k[a:a + 256] = np.argmin(d2, axis=1)
        e = tops[k]
        dl = local[hang[:, 0], hang[:, 1]] - local[e[:, 0], e[:, 1]]
        eu = np.hypot(dl[:, 0], dl[:, 1])
        u = np.where(eu[:, None] > 1e-9, dl / np.maximum(eu, 1e-9)[:, None], np.array([0.0, -1.0]))
        reach = np.maximum(np.abs(dl[:, 0]), np.abs(dl[:, 1]))
        ez = hit_z[e[:, 0], e[:, 1]] + rtop
        if rho > 0.0:
            th = np.clip(reach / rho, 0.0, math.pi / 2.0)
            on_arc = reach < arc
            out = np.where(on_arc, rho * np.sin(th), rtop)
            z = np.where(on_arc, ez - rho * (1.0 - np.cos(th)), ez - rho - (reach - arc))
        else:
            out, z = np.full(len(hang), rtop), ez - reach
        z = np.maximum(z, float(floor_z) + float(hem_m))
        ox, oy = c * u[:, 0] - s * u[:, 1], s * u[:, 0] + c * u[:, 1]
        ewx, ewy = wx[e[:, 0], e[:, 1]], wy[e[:, 0], e[:, 1]]
        z_ray = np.minimum(z, hit_z[e[:, 0], e[:, 1]] - 0.01)
        bx, by = ewx.copy(), ewy.copy()
        for q in range(len(hang)):
            side = caster.ray((float(ewx[q] + ox[q]), float(ewy[q] + oy[q]), float(z_ray[q])),
                              (float(-ox[q]), float(-oy[q]), 0.0), 1.2)
            if side is not None and side[0] <= 1.05:
                bx[q], by[q] = side[1][0], side[1][1]
        hi, hj = hang[:, 0], hang[:, 1]
        grid[hi, hj, 0], grid[hi, hj, 1], grid[hi, hj, 2] = bx + ox * out, by + oy * out, z
        hang_s[hi, hj] = reach
        out_dir[hi, hj, 0], out_dir[hi, hj, 1] = ox, oy
        edge_local[hi, hj] = local[e[:, 0], e[:, 1]]
    return {"grid": grid, "on_top": on_top, "top_z": top_z, "share": float(on_top.mean()), "local": local,
            "hang_s": hang_s, "out_dir": out_dir, "edge_local": edge_local, "arc_m": arc, "nu": nu, "nv": nv}


def _cloth(caster, host_fp: dict, rect, floor_z: float, key: str, role: str, fringe: bool, kw: dict,
           ends: Sequence[str] = ("left", "right")) -> Optional[dict]:
    """29 Oct 2026 (UL121): one draped cloth of a throw pair, ``fringe`` with strands at its two ends across the bed
    (``bedding_parts.fringe_strands``): the drape reaches ``FRINGE_M`` past each end on whole grid columns (no other
    ray), the cloth is the columns inside its rectangle, each end's strands the columns past it (they lie on the bed or
    hang over its side as the drape did); ``ends``: the bed's sides that take strands (a side against a wall or a
    piece, ``bedding_parts.bed_sides``, takes none). ``{"part", "fringe": [parts], "drape", "rect"}`` or None."""
    from wenart.blender import bedding_parts as BP

    x0, y0, x1, y1 = (float(v) for v in rect)
    step = kw.get("step") or CLOTH_STEP_M
    nu = max(2, int(round((x1 - x0) / step)))
    nv = max(2, int(round((y1 - y0) / step)))
    k = int(math.ceil(BP.FRINGE_M / ((x1 - x0) / nu) - 1e-9)) if fringe else 0
    sx = (x1 - x0) / nu
    dk = {kk: v for kk, v in kw.items() if kk in ("offset",)}
    got = drape(caster, host_fp, (x0 - k * sx, y0, x1 + k * sx, y1), floor_z, nu=nu + 2 * k, nv=nv, **dk)
    if got["grid"] is None:
        return None
    grid = got["grid"]
    sheet = cloth_solid(grid[k:k + nu + 1], key=key, role=role)
    strands = []
    if k:
        for end, cols in (("left", grid[k::-1]), ("right", grid[k + nu:])):
            part = BP.fringe_strands(cols, key) if end in ends else None
            if part is not None:
                strands.append(part)
    main = dict(got, grid=grid[k:k + nu + 1], on_top=got["on_top"][k:k + nu + 1])
    main["share"] = float(main["on_top"].mean()) if main["on_top"] is not None else 0.0
    return {"part": sheet, "fringe": strands, "drape": main, "rect": (x0, y0, x1, y1)}


def woven_throw_parts(caster, host_fp: dict, item: dict, floor_z: float, kw: dict) -> Optional[dict]:
    """29 Oct 2026 (UL121, R35: "a fringed throw folded over the foot and a houndstooth blanket under it"): a throw
    with its ``weave`` (``bedding_parts.throw_weave``, the decor stage's or the family's): the throw itself is the
    blanket in its woven pattern (key ``textile_<pattern>``: the item's colour with the accent colour as its ink), the
    layered second blanket over it the plain throw (``runner_<look>``, the accent colour) with the fringe at its two
    ends; a throw in one layer carries both. ``throw_parts``'s record plus ``weave`` (what was built)."""
    from wenart.blender import bedding_parts as BP

    weave = item["weave"]
    pattern = weave.get("pattern") if weave.get("pattern") in BP.PATTERN_SLUGS else None
    look = weave.get("runner_look") if weave.get("runner_look") in BP.LOOK_SLUGS else "knit"
    fringe = bool(weave.get("fringe"))
    ends = tuple(weave.get("fringe_ends") or ("left", "right"))
    layered = int(item.get("layers") or 1) >= 2
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    lx, ly = rest.to_local(hc, rot, float(item["center"][0]), float(item["center"][1]))
    w, d = float(item["size"][0]), float(item["size"][1])
    rect = (lx - w / 2.0, ly - d / 2.0, lx + w / 2.0, ly + d / 2.0)
    key = BP.textile_key(pattern) if pattern else "colour_fabric"
    first = _cloth(caster, host_fp, rect, floor_z, key, "throw", fringe and not layered, kw, ends)
    if first is None:
        return None
    parts = [first["part"]]
    strands = list(first["fringe"])
    out = {"parts": parts, "drape": first["drape"], "rect": rect}
    if layered:
        x0, y0, x1, y1 = rect
        cx, rw = (x0 + x1) / 2.0, (x1 - x0) * RUNNER_WIDTH_SHARE
        r_rect = (cx - rw / 2.0, y0 + 0.02, cx + rw / 2.0, y0 + 0.02 + (y1 - y0) * RUNNER_SHARE)
        both = rest.MultiCaster([caster, rest.MeshCaster(first["part"]["verts"], first["part"]["faces"])])
        second = _cloth(both, host_fp, r_rect, floor_z, BP.runner_key(look), RUNNER_FOLD_ROLE, fringe, kw, ends)
        if second is not None:
            parts.append(second["part"])
            strands += second["fringe"]
            out["runner"] = {"rect": second["rect"], "share": second["drape"]["share"]}
    parts += strands
    out["weave"] = {"pattern": pattern, "runner_look": look if layered else None, "fringe": fringe,
                    "fringe_ends": list(ends), "fringe_strands": int(sum(int(p.get("strands") or 0) for p in strands)),
                    "rule": weave.get("rule") or BP.RULE}
    return out


def throw_parts(caster, host_fp: dict, item: dict, floor_z: float, step: Optional[float] = None,
                offset: Optional[float] = None) -> Optional[dict]:
    """A throw on a seat end or across a bed's foot (§4.7): its rectangle (the item's centre and size in the host
    frame) draped on the host; a rolled fold along its front edge. Returns ``{"parts", "drape", "rect"}`` or None
    when the cloth finds no top under it. ``step`` / ``offset``: a finer grid and a higher offset for a host that
    shows through the cloth (``rest.plan_throw``).

    29 Oct 2026 (UL106; the professional reference: a knit throw and a second blanket across the bed's foot): an item
    with ``layers`` 2 gets a second, narrower blanket (``layered_runner``: ``RUNNER_SHARE`` of the throw's depth, at
    its foot end) draped on the bed and the first throw together (``rest.MultiCaster``), key ``RUNNER_KEY`` (the
    item's ``accent_colour``, else its colour); the first throw is what S5 measures (``parts[0]``).

    29 Oct 2026 (UL121): an item with a ``weave`` is the woven pair (``woven_throw_parts``: the patterned blanket, the
    fringed throw over it)."""
    kw = {k: v for k, v in (("step", step), ("offset", offset)) if v is not None}
    if isinstance(item.get("weave"), dict):
        return woven_throw_parts(caster, host_fp, item, floor_z, kw)
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    lx, ly = rest.to_local(hc, rot, float(item["center"][0]), float(item["center"][1]))
    w, d = float(item["size"][0]), float(item["size"][1])
    rect = (lx - w / 2.0, ly - d / 2.0, lx + w / 2.0, ly + d / 2.0)
    got = drape(caster, host_fp, rect, floor_z, **kw)
    if got["grid"] is None:
        return None
    sheet = cloth_solid(got["grid"], key="colour_fabric", role="throw")
    out = {"parts": [sheet], "drape": got, "rect": rect}
    if int(item.get("layers") or 1) >= 2:
        runner = layered_runner(caster, host_fp, rect, sheet, floor_z, **kw)
        if runner is not None:
            out["parts"].append(runner["part"])
            out["runner"] = {"rect": runner["rect"], "share": runner["drape"]["share"]}
    return out


RUNNER_SHARE = 0.55              # the second blanket: this share of the throw's depth ...
RUNNER_WIDTH_SHARE = 1.06        # ... and a little wider than it, hanging further over the bed's sides
RUNNER_FOLD_ROLE = "runner"
RUNNER_KEY = "colour_duvet"      # the duvet's fabric in the item's accent colour (furniture: _part_colour)


def layered_runner(caster, host_fp: dict, rect, sheet: dict, floor_z: float, step: Optional[float] = None,
                   offset: Optional[float] = None) -> Optional[dict]:
    """The second blanket of a layered throw (``throw_parts``): ``{"part", "rect", "drape"}`` draped over the host
    and the first throw (pure numpy: a ``rest.MeshCaster`` of the sheet with the host's caster), None when it finds
    no top."""
    x0, y0, x1, y1 = (float(v) for v in rect)
    cx, w = (x0 + x1) / 2.0, (x1 - x0) * RUNNER_WIDTH_SHARE
    depth = (y1 - y0) * RUNNER_SHARE
    r_rect = (cx - w / 2.0, y0 + 0.02, cx + w / 2.0, y0 + 0.02 + depth)
    both = rest.MultiCaster([caster, rest.MeshCaster(sheet["verts"], sheet["faces"])])
    kw = {k: v for k, v in (("step", step), ("offset", offset)) if v is not None}
    got = drape(both, host_fp, r_rect, floor_z, **kw)
    if got["grid"] is None:
        return None
    return {"part": cloth_solid(got["grid"], key=RUNNER_KEY, role=RUNNER_FOLD_ROLE), "rect": r_rect,
            "drape": got}


# --------------------------------------------------------------------------
# Bedding of a bed whose model has none
# --------------------------------------------------------------------------

def mattress_rect(host_fp: dict, inset: float = 0.0) -> tuple[float, float, float, float]:
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    return (-w / 2.0 + inset, -d / 2.0 + inset, w / 2.0 - inset, d / 2.0 - inset)


def pillow_count(width: float) -> int:
    return 2 if float(width) >= TWO_PILLOW_MIN_W - 1e-9 else 1


# 29 Oct 2026 (UL106; the professional reference: two sleeping pillows in front of two large square euro shams against
# the headboard): a double bed's euro shams stand upright on the mattress against a real headboard (``euro_shams``);
# a bed with no headboard the rays find (a platform bed against the wall) gets none. Designer values (a 65 x 65 cm sham).
SHAM_SIZE = (0.65, 0.12, 0.60)    # width across the bed, thickness, height (slim: the pillows stay in the head zone)
SHAM_LEAN_DEG = 6.0
SHAM_MIN_BED_W = 1.35
SHAM_ROLE = "euro_sham"


def _merged(parts: list) -> tuple[list, list]:
    verts, faces = [], []
    for part in parts or []:
        off = len(verts)
        verts.extend(part["verts"])
        faces.extend([[i + off for i in f] for f in part["faces"]])
    return verts, faces


def euro_shams(caster, host_fp: dict, count: int = 2, size: Optional[Sequence[float]] = None, key: str = "bedding",
               mesh_fn=None, colour: Optional[str] = None) -> Optional[dict]:
    """``{"parts", "poses"}`` of up to two euro shams against the bed's headboard (pure numpy; ``rest.place_leaning``
    leaned ``SHAM_LEAN_DEG``), None when the bed is narrower than ``SHAM_MIN_BED_W`` or no headboard is hit (a sham
    never stands against nothing). 29 Oct 2026 (UL121): the family set's ``size``, part ``key``, mesh maker
    (``bedding_parts.plump_cushion``) and ``colour``."""
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    if w < SHAM_MIN_BED_W - 1e-9 or int(count) < 1:
        return None
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    n = min(2, int(count))
    size = tuple(size) if size else SHAM_SIZE
    sw = min(size[0], (w - 0.1) / n - 0.04)
    st, sh = size[1], size[2]
    make = mesh_fn or cushion_mesh
    parts, poses = [], []
    for k in range(n):
        lx = 0.0 if n == 1 else (-1 if k == 0 else 1) * (sw / 2.0 + 0.02)
        planned = rest.to_world(hc, rot, lx, d / 2.0 - st)
        pose = rest.place_leaning(caster, host_fp, planned, (sw, st, sh), lean_deg=SHAM_LEAN_DEG, bed=True)
        if pose is None or str(pose.get("how") or "").startswith("no backrest hit"):
            return None
        mesh = make(pose["size"][0], st, sh, key=key, role=SHAM_ROLE)
        placed = dict(mesh, verts=rest.pose_vertices(mesh["verts"], pose))
        parts.append(dict(placed, colour=colour) if colour else placed)
        poses.append(pose)
    return {"parts": parts, "poses": poses}


def sham_mesh(parts: list) -> tuple[list, list]:
    """The world mesh of a bedding's euro shams (pure): what a decor cushion stands against on a dressed bed."""
    return _merged([p for p in parts or [] if p.get("role") == SHAM_ROLE])


def _pillows(caster, host_fp: dict, n: int, pw: float, pt: float, ph: float, lean_deg: Optional[float] = None,
             key: str = "bedding", mesh_fn=None, colour: Optional[str] = None) -> Optional[tuple[list, list]]:
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    d = float(host_fp["size"][1])
    lean = 90.0 - PILLOW_TILT_DEG if lean_deg is None else float(lean_deg)
    make = mesh_fn or cushion_mesh
    parts, poses = [], []
    for k in range(n):
        lx = 0.0 if n == 1 else (-1 if k == 0 else 1) * (pw / 2.0 + 0.02)
        planned = rest.to_world(hc, rot, lx, d / 2.0 - ph / 2.0)
        pose = rest.place_leaning(caster, host_fp, planned, (pw, pt, ph), lean_deg=lean, bed=True)
        if pose is None:
            return None
        mesh = make(pose["size"][0], pt, ph, key=key, role="pillow")
        placed = dict(mesh, verts=rest.pose_vertices(mesh["verts"], pose))
        parts.append(dict(placed, colour=colour) if colour else placed)
        poses.append(pose)
    return parts, poses


def duvet_and_pillows(caster, host_fp: dict, floor_z: float, shams: int = 0) -> Optional[dict]:
    """The bedding of a bed model without bedding (§4.7): ``{"parts", "pillows": [pose], "duvet": drape record,
    "record"}``; None when no mattress top is found. The pillows are placed first against the headboard
    (``rest.place_leaning`` with the pillow leaned ``90 - PILLOW_TILT_DEG``: lying, its head end raised); the duvet
    covers the foot ``DUVET_SHARE`` of the bed, ``DUVET_SIDE_DROP_M`` past the sides and the foot, with a turned-down
    band at its head end lying on it. 29 Oct 2026 (UL106): ``shams`` euro shams (``euro_shams``) stand against the
    headboard first and the pillows lean on them; when they cannot (no headboard) or the pillows then find no place,
    the bed is dressed without them (``record["euro_shams"]`` says how many)."""
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    n = pillow_count(w)
    pw = min(PILLOW_SIZE[0], (w - 0.1) / n - 0.04)
    pt, ph = PILLOW_SIZE[1], PILLOW_SIZE[2]
    sham = euro_shams(caster, host_fp, shams) if shams else None
    got = None
    if sham is not None:
        sv, sf = _merged(sham["parts"])
        got = _pillows(rest.MultiCaster([caster, rest.MeshCaster(sv, sf)]), host_fp, n, pw, pt, ph)
        if got is None or any(str(p.get("how") or "").startswith("no backrest hit") for p in got[1]):
            got, sham = None, None                 # the pillows must lean on the shams, else no shams
    if got is None:
        got = _pillows(caster, host_fp, n, pw, pt, ph)
    if got is None:
        return None
    parts, poses = got
    if sham is not None:
        parts = sham["parts"] + parts
    y_head = -d / 2.0 + DUVET_SHARE * d
    pillow_foot = min(rest.to_local(hc, rot, v[0], v[1])[1] for p in parts if p.get("role") == "pillow"
                      for v in p["verts"])
    y_head = min(y_head, pillow_foot - 0.03)            # the duvet ends just before the pillows
    rect = (-w / 2.0 - DUVET_SIDE_DROP_M, -d / 2.0 - DUVET_SIDE_DROP_M, w / 2.0 + DUVET_SIDE_DROP_M, y_head)
    got = drape(caster, host_fp, rect, floor_z, thickness=DUVET_THICKNESS_M)
    if got["grid"] is None:
        return None
    parts.append(cloth_solid(got["grid"], DUVET_THICKNESS_M, key="duvet", role="duvet"))
    band_rect = (-w / 2.0 - 0.01, y_head - TURN_DOWN_M, w / 2.0 + 0.01, y_head)
    band = _turn_down(got, rect, band_rect, host_fp)
    if band is not None:
        parts.append(band)
    record = {"pillows": n, "pillow_size_m": [round(pw, 3), pt, ph], "duvet_rect_local": [round(v, 3) for v in rect],
              "euro_shams": len(sham["parts"]) if sham else 0,
              "duvet_share": DUVET_SHARE, "top_z": round(float(got["top_z"]), 4), "on_top_share": round(got["share"], 3),
              "rule": "procedural bedding: the bed model has no bedding (docs/milestone12.md §4.7)",
              # fix round after P4b: where the pillows lie along the bed (local y, + = the head half) and the check
              "pillow_local_y": [round(rest.to_local(hc, rot, p["center"][0], p["center"][1])[1], 3) for p in poses]}
    record["head_problems"] = bedding_head_problems(record)
    return {"parts": parts, "pillows": poses, "duvet": got, "record": record}


ACCENT_ROLE = "accent_cushion"       # 29 Oct 2026 (UL121): the family set's cushions in front of the pillows
LUMBAR_ROLE = "lumbar"


def bedding_set(caster, host_fp: dict, floor_z: float, spec: dict, sides: Optional[dict] = None,
                mode: str = "full", colours: Optional[Sequence[str]] = None) -> Optional[dict]:
    """29 Oct 2026 (lesson UL121, R35: "a full, soft bed"): the bedding of the family's set (``bedding_parts.
    FAMILY_BEDDING``, ``counts`` by the bed's width) on a bed model, every piece one part of the bed's one dressing
    mesh: (1) the euro shams against the headboard (``euro_shams``; none without a headboard, said in ``explained``),
    (2) the sleeping pillows standing against them (``bedding_parts.PILLOW_UPRIGHT_LEAN_DEG``), else lying against the
    headboard as before, (3) the duvet (``mode`` full): ``drape_shaped`` over the foot ``DUVET_SHARE`` with the family's
    thickness, its rounded edge, the top's folds and the sides' flutes (``bedding_parts.shape_duvet``), hanging almost
    to the floor (the family's hem) on each side ``sides`` says is free (``bedding_parts.bed_sides``) and not past a
    blocked one, its turn-down band with a rolled edge, (4) the accent cushions and the lumbar standing on the band and
    leaning on the pillows and on each other (``bedding_parts.stack_cushion``: no ray). ``colours``: the decor stage's
    cushion colours (the AI's), used for the accent cushions and the lumbar before the family's. ``mode`` pillows: the
    set without our duvet (the model's own duvet kept). ``{"parts", "pillows": [pose], "duvet", "record"}`` or None
    when no pillow finds a place."""
    from wenart.blender import bedding_parts as BP

    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    want = BP.counts(spec, w)
    explained: dict[str, str] = {}
    colours = [c for c in (colours or []) if c]
    # 1. euro shams
    sham = None
    if want["euro_shams"]:
        sham = euro_shams(caster, host_fp, want["euro_shams"], size=BP.SHAM_SIZE,
                          key=BP.textile_key(spec["shams"]["look"]), mesh_fn=BP.plump_cushion,
                          colour=spec["shams"].get("colour"))
    # 2. sleeping pillows: standing against the shams, else lying against the headboard
    n = want["pillows"]
    pw = min(BP.PILLOW_SIZE[0], (w - 0.1) / n - 0.04)
    pt, ph = BP.PILLOW_SIZE[1], BP.PILLOW_SIZE[2]
    pkey, pcol = BP.textile_key(spec["pillows"]["look"]), spec["pillows"].get("colour")
    got = None
    if sham is not None:
        sv, sf = _merged(sham["parts"])
        got = _pillows(rest.MultiCaster([caster, rest.MeshCaster(sv, sf)]), host_fp, n, pw, pt, ph,
                       lean_deg=BP.PILLOW_UPRIGHT_LEAN_DEG, key=pkey, mesh_fn=BP.plump_cushion, colour=pcol)
        if got is None or any(str(p.get("how") or "").startswith("no backrest hit") for p in got[1]):
            got, sham = None, None
            explained["euro_shams"] = "the sleeping pillows found no place against the shams: no shams"
    if want["euro_shams"] and sham is None:
        explained.setdefault("euro_shams", "no headboard the rays find: no shams (a sham never stands against "
                                           "nothing)")
    upright = got is not None
    if got is None:
        got = _pillows(caster, host_fp, n, pw, pt, ph, key=pkey, mesh_fn=BP.plump_cushion, colour=pcol)
    if got is None:
        return None
    parts, poses = got
    if sham is not None:
        parts = sham["parts"] + parts
    seats = sorted(float(p.get("seat_z") or p["z"]) for p in poses)
    top_est = seats[len(seats) // 2]
    pillow_loc = BP.to_local_arr(hc, rot, BP.face_points([p for p in parts if p.get("role") == "pillow"]))
    y_head = min(-d / 2.0 + DUVET_SHARE * d, float(pillow_loc[:, 1].min()) - 0.03)
    record = {"rule": BP.RULE, "lesson": BP.LESSON, "family": spec.get("family"), "mode": mode,
              "pillows": n, "pillow_size_m": [round(pw, 3), pt, ph], "pillows_upright": upright,
              "euro_shams": len(sham["parts"]) if sham else 0, "duvet_share": DUVET_SHARE,
              "pillow_local_y": [round(rest.to_local(hc, rot, p["center"][0], p["center"][1])[1], 3) for p in poses],
              "expected": want}
    support = np.zeros((0, 3))
    duvet_got = None
    # 3. the duvet
    if mode == "full":
        ds = spec["duvet"]
        thick, hem = float(ds["thickness_m"]), float(ds.get("hem_m") or 0.08)
        sides = sides or {s: {"free": True} for s in BP.SIDES}
        rtop = CLOTH_OFFSET_M + thick
        free_ext = max(0.0, top_est - float(floor_z) - hem) + math.pi / 2.0 * rtop
        ext = {s: (free_ext if (sides.get(s) or {}).get("free", True) else 0.0) for s in BP.SIDES}
        rect = (-w / 2.0 - ext["left"], -d / 2.0 - ext["foot"], w / 2.0 + ext["right"], y_head)
        duvet_got = drape_shaped(caster, host_fp, rect, floor_z, thick, hem_m=hem)
        if duvet_got is None:
            return None
        grid = BP.shape_duvet(duvet_got, w, d, float(ds.get("wrinkle_m") or 0.01))
        dkey, dcol = BP.textile_key(ds["look"]), ds.get("colour")
        parts.append(dict(cloth_solid(grid, thick, key=dkey, role="duvet"), colour=dcol))
        loc = duvet_got["local"]
        rows = loc[0, :, 1] >= y_head - TURN_DOWN_M - 1e-9
        cols = np.abs(loc[:, 0, 0]) <= w / 2.0 + 0.01
        band = None
        if rows.sum() >= 2 and cols.sum() >= 2:
            sub = grid[np.ix_(cols, rows)]
            band = BP.turn_down(sub, thick, CLOTH_OFFSET_M)
            parts.append(dict(cloth_solid(band, thick * 0.6, key=dkey, role="turndown"), colour=dcol))
        on = np.asarray(duvet_got["on_top"], dtype=bool)
        support = BP.to_local_arr(hc, rot, grid[on])
        if band is not None:
            support = np.concatenate([support, BP.to_local_arr(hc, rot, band.reshape(-1, 3))], axis=0)
        record.update(duvet_rect_local=[round(v, 3) for v in rect], top_z=round(float(duvet_got["top_z"]), 4),
                      on_top_share=round(duvet_got["share"], 3),
                      duvet={"look": ds["look"], "colour": dcol, "thickness_m": thick, "rounded_m": round(rtop, 3),
                             "wrinkle_m": ds.get("wrinkle_m"), "hem_m": hem, "grid": [duvet_got["nu"],
                                                                                    duvet_got["nv"]]},
                      sides=sides, drops=BP.side_drops(grid, loc, w, d, float(duvet_got["top_z"]), floor_z))
    else:
        record.update(duvet_rect_local=[-w / 2.0, -d / 2.0, w / 2.0, round(y_head, 3)], top_z=round(top_est, 4),
                      duvet=None, sides=sides)
    # 4. accent cushions and the lumbar, stacked in front of the pillows (no ray)
    behind = BP.to_local_arr(hc, rot, BP.face_points([p for p in parts if p.get("role") in ("pillow", SHAM_ROLE)]))
    accents = list(spec.get("accent") or [])[:want["accent"]]
    na = len(accents)
    cw = min(BP.ACCENT_SIZE[0], (w - 0.1) / max(1, na) - 0.03)
    placed_acc, front = [], []
    for k, acc in enumerate(accents):
        cx = 0.0 if na == 1 else (-1 if k == 0 else 1) * (cw / 2.0 + 0.015)
        res = BP.stack_cushion(behind, support, top_est, cx, (cw, BP.ACCENT_SIZE[1], BP.ACCENT_SIZE[2]),
                               BP.textile_key(acc["look"]), ACCENT_ROLE)
        if res is None:
            explained.setdefault("accent", "nothing behind the cushion's upper part to lean on (the pillows lie low)")
            continue
        colour = colours[len(placed_acc)] if len(placed_acc) < len(colours) else acc.get("colour")
        world = BP.to_world_arr(hc, rot, np.asarray(res["part"]["verts"]))
        parts.append(dict(res["part"], verts=[tuple(p) for p in world.tolist()], colour=colour))
        placed_acc.append({"look": acc["look"], "colour": colour, "lean_deg": res["lean_deg"],
                           "contact_m": res["contact_m"], "upper_gap_m": res["upper_gap_m"]})
        front.append(res["part"])                     # bed-local: what the lumbar leans on
    lumbar = None
    if want["lumbar"]:
        lum = spec["lumbar"]
        stack = np.concatenate([behind, BP.face_points(front)], axis=0) if front else behind
        lw = min(BP.LUMBAR_SIZE[0], w - 0.2)
        res = BP.stack_cushion(stack, support, top_est, 0.0, (lw, BP.LUMBAR_SIZE[1], BP.LUMBAR_SIZE[2]),
                               BP.textile_key(lum["look"]), LUMBAR_ROLE)
        if res is None:
            explained["lumbar"] = "nothing behind the lumbar's upper part to lean on"
        else:
            k = len(placed_acc)
            colour = colours[k] if k < len(colours) else lum.get("colour")
            world = BP.to_world_arr(hc, rot, np.asarray(res["part"]["verts"]))
            parts.append(dict(res["part"], verts=[tuple(p) for p in world.tolist()], colour=colour))
            lumbar = {"look": lum["look"], "colour": colour, "lean_deg": res["lean_deg"],
                      "contact_m": res["contact_m"], "upper_gap_m": res["upper_gap_m"]}
    record.update(set={"euro_shams": record["euro_shams"], "pillows": n, "accent": len(placed_acc),
                       "lumbar": 1 if lumbar else 0},
                  explained=explained, accent=placed_acc, lumbar=lumbar,
                  looks={"shams": spec["shams"]["look"], "pillows": spec["pillows"]["look"],
                         "duvet": spec["duvet"]["look"] if mode == "full" else None})
    record["head_problems"] = bedding_head_problems(record)
    return {"parts": parts, "pillows": poses, "duvet": duvet_got, "record": record}


LEAN_ROLES = ("pillow", SHAM_ROLE,   # the bedding a decor cushion may lean against (never the duvet or its fold)
              ACCENT_ROLE, LUMBAR_ROLE)


def lean_parts(parts: list) -> tuple[list, list]:
    """The world mesh ``(verts, faces)`` of the bedding parts a decor cushion leans against (pure; 27 Oct 2026, user on
    real06: "flying pillows"): the pillows only. The cushions of a dressed bed without a headboard took the duvet's
    turn-down fold in the middle of the bed for the backrest and stood upright on the duvet in front of the pillows."""
    verts, faces = [], []
    for part in parts or []:
        if part.get("role") in LEAN_ROLES:
            off = len(verts)
            verts.extend(part["verts"])
            faces.extend([[i + off for i in f] for f in part["faces"]])
    return verts, faces


def bedding_head_problems(record: dict) -> list[str]:
    """Fix round after P4b (17 Oct 2026; integration of the furniture track's ask): why the bedding of a dressing
    record is not at the head of the bed: a pillow centre at local y <= 0 (the foot half) or the duvet's head edge
    (``duvet_rect_local`` y1) at local y <= 0; [] when it is right. P4b real03 laid oda_01's pillow at the foot."""
    out = []
    for k, y in enumerate(record.get("pillow_local_y") or []):
        if float(y) <= 0.0:
            out.append(f"pillow {k + 1} lies in the foot half (local y {float(y):.2f} m)")
    rect = record.get("duvet_rect_local") or []
    if len(rect) == 4 and float(rect[3]) <= 0.0:
        out.append(f"the duvet's head edge is in the foot half (local y {float(rect[3]):.2f} m)")
    return out


def _turn_down(got: dict, rect, band_rect, host_fp: dict) -> Optional[Part]:
    """The folded-back band at the duvet's head end: the duvet grid's rows inside ``band_rect`` lifted by the
    duvet's thickness (it lies on the duvet)."""
    grid = got["grid"]
    nu, nv = grid.shape[0] - 1, grid.shape[1] - 1
    x0, y0, x1, y1 = rect
    js = [j for j in range(nv + 1) if y0 + (y1 - y0) * j / nv >= band_rect[1] - 1e-9]
    is_ = [i for i in range(nu + 1) if band_rect[0] - 1e-9 <= x0 + (x1 - x0) * i / nu <= band_rect[2] + 1e-9]
    if len(js) < 2 or len(is_) < 2:
        return None
    sub = grid[is_[0]:is_[-1] + 1, js[0]:js[-1] + 1].copy()
    sub[..., 2] += DUVET_THICKNESS_M * 0.5 + CLOTH_OFFSET_M
    return cloth_solid(sub, DUVET_THICKNESS_M * 0.6, key="bedding", role="turndown")

