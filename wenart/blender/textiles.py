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
without rays, a deep duvet with a rounded edge and the overhang on its free sides, the turn-down);
``woven_throw_parts`` makes a bed's throw pair (the woven blanket, the fringed throw over it; ``_cloth`` drapes a cloth
with its fringe columns). ``duvet_and_pillows`` and the plain throw stay for a call without the family's set.

30 Oct 2026 (user on real04 run 20261029-201533-full; lessons UL136, UL137, UL146): a real made bed. The duvet is
``drape_cover`` (``measure_cover``: the host's top, its edges, its own rail or footboard, its width down to the hem, by
rays; ``bedding_parts.cover_grid``: a smooth top with a few soft wide folds, a rounded edge, straight down to one
level hem), the turned-down sheet a thin band folded round its head edge (``bedding_parts.turn_down_band``); the shams
and pillows stand on what lies at the head against the headboard first (``_lean_pose``), a gap between the mattress
and the headboard is bridged (``rest.bed_head``) and closed by a sheet (``gap_sheet``); a bed's layered throw pair lies
as the photo P14 lays it (``p14_throw_parts``: the blanket over the foot, the patterned throw at one side).

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
EDGE_PROBE_DZ_M = 0.015          # 30 Oct 2026 (UL136): a host's edge is measured this far under its top ...
EDGE_PROBES = 7                  # ... by this many side rays along it (the outermost hit: the cloth clears it all)
OWN_RAIL_DZ_M = 0.08             # rays from the bed's middle this far over its top: the bed's own rail or footboard
DROP_PROBE_DZ_M = 0.04           # the hanging zone's side rays every this much down to the hem


def _down(caster, hc, rot: float, lx: np.ndarray, ly: np.ndarray, z_from: float) -> np.ndarray:
    """The hit heights of rays down at bed-local points (NaN for a miss; a point beside the host's bounds is not
    cast)."""
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    wx, wy = hc[0] + c * lx - s * ly, hc[1] + s * lx + c * ly
    (bx0, by0, _z0), (bx1, by1, _z1) = caster.bounds
    out = np.full(np.shape(lx), np.nan)
    over = (wx >= bx0 - 0.02) & (wx <= bx1 + 0.02) & (wy >= by0 - 0.02) & (wy <= by1 + 0.02)
    for idx in np.argwhere(over):
        k = tuple(idx)
        h = caster.ray((float(wx[k]), float(wy[k]), float(z_from)), (0.0, 0.0, -1.0))
        if h is not None:
            out[k] = h[1][2]
    return out


def _side_ray(caster, hc, rot: float, origin_local, direction_local, z: float, reach: float) -> Optional[float]:
    """The distance to the first hit of a horizontal ray from a bed-local point in a bed-local direction (None)."""
    ox, oy = rest.to_world(hc, rot, float(origin_local[0]), float(origin_local[1]))
    dx, dy = rest.direction_world(rot, float(direction_local[0]), float(direction_local[1]))
    h = caster.ray((ox, oy, float(z)), (dx, dy, 0.0), float(reach))
    return None if h is None else float(h[0])


SIDE_DIRS = {"left": (-1.0, 0.0), "right": (1.0, 0.0), "foot": (0.0, -1.0)}


def measure_cover(caster, host_fp: dict, span: Sequence[float], floor_z: float, sides: Optional[dict] = None,
                  limits: Optional[dict] = None, hem_z: Optional[float] = None, step: float = SHAPED_STEP_M,
                  drop: Optional[float] = None) -> dict:
    """30 Oct 2026 (UL136): what a cover lies on, measured by rays (the pure ``bedding_parts.cover_grid`` builds it).

    ``span`` = (y0, y1): the cover's rows along the bed (bed-local; y0 at or before the host's foot edge means the cover
    reaches the foot edge); ``sides``: ``{"left"|"right"|"foot": {"free"}}`` (a blocked side takes no hang); ``limits``:
    ``{"left"|"right": x}`` a cover narrower than the host (its top ends there, no hang on that side). Steps: the
    host's top (the median of a coarse grid of rays down), each edge (``EDGE_PROBES`` side rays from outside
    ``EDGE_PROBE_DZ_M`` under the top: the outermost hit), the bed's own rail or footboard over its top (rays from the
    middle ``OWN_RAIL_DZ_M`` over it: a side such a rail closes takes no hang and the cover ends before it), the top's
    rows and columns between the edges (``bedding_parts.COVER_STEP_M``) and its heights there (rays down,
    ``bedding_parts.envelope``), and on each hanging side the host's width at every ``DROP_PROBE_DZ_M`` down to the
    hem (``flare``). ``{"xs", "ys", "host", "top_z", "edges", "hang_free", "flare", "own_rails", "rays"}`` or None
    (no top)."""
    from wenart.blender import bedding_parts as BP

    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    y0, y1 = (float(v) for v in span)
    top_from = rest.host_top(caster) + rest.TOP_ABOVE_M
    rays = 0
    gx, gy = np.meshgrid(np.linspace(-w / 2.0 + 0.1, w / 2.0 - 0.1, 7),
                         np.linspace(max(y0, -d / 2.0) + 0.1, y1 - 0.05, 7), indexing="ij")
    coarse = _down(caster, hc, rot, gx, gy, top_from)
    rays += coarse.size
    found = coarse[~np.isnan(coarse)]
    if not len(found):
        return None
    top_z = float(np.median(found))
    sides = sides or {s: {"free": True} for s in BP.SIDES}
    limits = limits or {}
    zp = top_z - EDGE_PROBE_DZ_M
    ys_probe = np.linspace(max(y0, -d / 2.0) + 0.05, y1 - 0.05, EDGE_PROBES)
    xs_probe = np.linspace(-w / 2.0 + 0.1, w / 2.0 - 0.1, EDGE_PROBES)
    edges, own = {}, {}
    for side, (dx, dy) in SIDE_DIRS.items():
        far = (w / 2.0 + 0.6) if side != "foot" else (d / 2.0 + 0.6)
        probes = ys_probe if side != "foot" else xs_probe
        hits = []
        for p in probes:
            o = (dx * far, p) if side != "foot" else (p, -far)
            t = _side_ray(caster, hc, rot, o, (-dx, -dy), zp, far)
            rays += 1
            if t is not None and t <= far - 0.05:
                hits.append(far - t)                  # the edge's distance out of the middle line
        nominal = w / 2.0 if side != "foot" else d / 2.0
        edges[side] = max(hits) if hits else nominal
        # the bed's own rail or footboard rising over its top: rays from the middle outwards over the top
        inner = []
        for p in probes[1:-1:2]:
            o = (0.0, p) if side != "foot" else (p, 0.0)
            t = _side_ray(caster, hc, rot, o, (dx, dy), top_z + OWN_RAIL_DZ_M, edges[side] + 0.02)
            rays += 1
            if t is not None:
                inner.append(t)
        if len(inner) >= 2:
            own[side] = min(inner)
    x0 = -edges["left"]
    x1 = edges["right"]
    yf = -edges["foot"]
    hang_free = {}
    for side in BP.SIDES:
        free = bool((sides.get(side) or {}).get("free", True)) and side not in own and side not in limits
        if side == "foot" and y0 > yf + 0.05:
            free = False                              # a cover that starts mid-bed has no foot edge to hang over
        hang_free[side] = free
    if "left" in own:
        x0 = -own["left"] + 0.01
    if "right" in own:
        x1 = own["right"] - 0.01
    if "foot" in own:
        yf = -own["foot"] + 0.01
    x0 = max(x0, float(limits["left"])) if "left" in limits else x0
    x1 = min(x1, float(limits["right"])) if "right" in limits else x1
    ys_start = yf if y0 <= yf + 0.05 else y0
    nx = max(2, int(math.ceil((x1 - x0) / BP.COVER_STEP_M)))
    ny = max(2, int(math.ceil((y1 - ys_start) / BP.COVER_STEP_M)))
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(ys_start, y1, ny + 1)
    lx, ly = np.meshgrid(xs, ys, indexing="ij")
    raw = _down(caster, hc, rot, lx, ly, top_from)
    rays += raw.size
    raw = np.where(raw >= top_z - rest.TOP_BAND_M, raw, np.nan)       # a hit far under the top: the cloth bridges it
    host = BP.envelope(raw, top_z)
    # the hanging zone: the host's width at each depth under its edge (a frame wider than the top below it)
    flare = {}
    hem = float(floor_z) + 0.05 if hem_z is None else float(hem_z)
    if drop is not None:                              # a blanket: it hangs this far under the top
        hem = max(float(floor_z) + 0.05, top_z - float(drop))
    for side, (dx, dy) in SIDE_DIRS.items():
        if not hang_free[side]:
            continue
        far = (w / 2.0 + 0.6) if side != "foot" else (d / 2.0 + 0.6)
        probes = ys_probe[::2] if side != "foot" else xs_probe[::2]
        edge = edges[side]
        depths, need = [], []
        depth = DROP_PROBE_DZ_M
        while top_z - depth > hem + 0.01:
            out = 0.0
            for p in probes:
                o = (dx * far, p) if side != "foot" else (p, -far)
                t = _side_ray(caster, hc, rot, o, (-dx, -dy), top_z - depth, far)
                rays += 1
                if t is not None and t <= far - 0.05:
                    out = max(out, (far - t) - edge)
            depths.append(depth)
            need.append(out)
            depth += DROP_PROBE_DZ_M
        if depths and max(need) > 1e-3:
            flare[side] = (np.asarray(depths), np.asarray(need))
    return {"xs": xs, "ys": ys, "host": host, "top_z": top_z, "edges": {"left": x0, "right": x1, "foot": yf},
            "hang_free": hang_free, "flare": flare, "own_rails": own, "rays": rays, "hem_z": hem}


def drape_cover(caster, host_fp: dict, span: Sequence[float], floor_z: float, thickness: float, hem_z: float,
                sides: Optional[dict] = None, wrinkle_m: float = 0.0, limits: Optional[dict] = None,
                offset: float = CLOTH_OFFSET_M, side_folds: bool = True, drop: Optional[float] = None,
                round_m: float = 0.0) -> Optional[dict]:
    """30 Oct 2026 (UL136, UL146: "a smooth duvet with a few soft wide folds, a straight even hem with a gentle drape
    where it falls over the mattress edge"): a cover over the bed (``measure_cover`` then ``bedding_parts.cover_grid``):
    on every free side it hangs down to ``hem_z`` (the hanging length: the rounded edge plus the drop from the side's
    top to the hem). The ``cover_grid`` record in the world (``grid``; ``local`` stays in the bed's frame) plus
    ``top_z``, ``share``, ``measure`` (edges, free sides, rails, rays); None without a top."""
    from wenart.blender import bedding_parts as BP

    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    m = measure_cover(caster, host_fp, span, floor_z, sides, limits, hem_z, drop=drop)
    if m is None:
        return None
    rho = float(offset) + float(thickness)
    R = max(rho, float(round_m or 0.0))
    arc = math.pi / 2.0 * R
    H = m["host"]
    edge_top = {"left": float(np.median(H[0])), "right": float(np.median(H[-1])), "foot": float(np.median(H[:, 0]))}
    hem_z = m["hem_z"]
    hang = {s: (arc + max(0.0, edge_top[s] + rho - R - float(hem_z)) if m["hang_free"][s] else 0.0)
            for s in BP.SIDES}
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    cover = BP.cover_grid(m["xs"], m["ys"], H, hang, hem_z, offset, thickness, wrinkle_m, side_folds=side_folds,
                          flare=m["flare"], bed_size=(w, d), round_m=R)
    cover["grid_local"] = cover["grid"]
    cover["grid"] = BP.to_world_arr(hc, rot, cover["grid"].reshape(-1, 3)).reshape(cover["grid"].shape)
    cover["normals_local"] = cover["normals"]
    nw = BP.to_world_arr((0.0, 0.0), rot, cover["normals"].reshape(-1, 3))
    cover["normals"] = nw.reshape(cover["normals_local"].shape)
    cover.update(top_z=m["top_z"], share=float(np.mean(cover["on_top"])),
                 measure={"edges": {k: round(v, 4) for k, v in m["edges"].items()}, "hang_free": m["hang_free"],
                          "own_rails": {k: round(v, 3) for k, v in m["own_rails"].items()},
                          "flare": sorted(m["flare"]), "rays": m["rays"]})
    return cover


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


BLANKET_T_M = 0.012              # 30 Oct 2026 (UL146, P14): the folded wool blanket over the duvet's foot ...
BLANKET_DROP_M = 0.30            # ... hanging this far under the bed's top on its free sides and its foot ...
BLANKET_ROUND_M = 0.045          # ... rolling softly over the duvet's edge (a folded blanket, not a board)
SIDE_THROW_W_M = 0.60            # the patterned throw draped at one side: this wide along the bed ...
SIDE_THROW_ON_M = 0.70           # ... lying this far over the top ...
SIDE_THROW_DROP_M = 0.42         # ... and hanging this far down the side ...
SIDE_THROW_T_M = 0.008
SIDE_THROW_ROUND_M = 0.035
SIDE_THROW_OVERLAP_M = 0.18      # ... over the blanket's head edge by this (the layers overlap)
FRINGE_COLS = 2                  # the strands: this many drape steps past the throw's end


def _strand_columns(cover: dict, end: str) -> np.ndarray:
    """The paths of a throw's fringe past one end of its cover (pure, bed-local): ``inner`` = its top end (the strands
    lie on, continuing inwards), ``hem`` = its hanging end (they hang straight on). ``(FRINGE_COLS + 1, rows, 3)``."""
    from wenart.blender import bedding_parts as BP

    g = np.asarray(cover["grid_local"], dtype=np.float64)
    step = BP.FRINGE_M / FRINGE_COLS
    if end == "hem":
        base = g[-1] if cover["split"]["right"] else g[0]
        return np.stack([base + np.array([0.0, 0.0, -step * k]) for k in range(FRINGE_COLS + 1)], axis=0)
    base = g[0] if cover["split"]["right"] else g[-1]
    sign = -1.0 if cover["split"]["right"] else 1.0
    return np.stack([base + np.array([sign * step * k, 0.0, 0.0]) for k in range(FRINGE_COLS + 1)], axis=0)


def p14_throw_parts(caster, host_fp: dict, item: dict, floor_z: float, sides: Optional[dict] = None
                    ) -> Optional[dict]:
    """30 Oct 2026 (lesson UL146, P14 R38: "a brown blanket folded over it at the foot half, a houndstooth throw draped
    at one side"): a bed's layered throw pair as the photo layers it. (1) The blanket (``parts[0]``, what S5 measures):
    the plain ``runner_<look>`` in the item's accent colour over the item's rectangle along the bed, the whole width,
    draped as the duvet is (``drape_cover``: a smooth top, a rounded edge, straight down) ``BLANKET_DROP_M`` under the
    top on each free side and over the foot when it starts there. (2) The throw in its woven pattern
    (``textile_<pattern>``: the item's colour, the accent colour as its ink) draped at one free side (the right one
    first): ``SIDE_THROW_ON_M`` on the top, ``SIDE_THROW_DROP_M`` down the side, over the blanket's head edge, with its
    fringe at both ends (on the top and below its hem). None when neither the left nor the right side is free (the
    pair across the foot of before follows) or no top is found. ``throw_parts``'s record plus ``weave``."""
    from wenart.blender import bedding_parts as BP

    weave = item["weave"]
    pattern = weave.get("pattern") if weave.get("pattern") in BP.PATTERN_SLUGS else None
    look = weave.get("runner_look") if weave.get("runner_look") in BP.LOOK_SLUGS else "knit"
    fringe = bool(weave.get("fringe"))
    ends = [s for s in ("right", "left") if s in (weave.get("fringe_ends") or ("left", "right"))]
    sd = {s: dict((sides or {}).get(s) or {"free": True}) for s in BP.SIDES}
    for s in ("left", "right"):
        sd[s]["free"] = bool(sd[s].get("free", True)) and s in ends
    side = next((s for s in ("right", "left") if sd[s]["free"]), None)
    if side is None:
        return None
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    lx, ly = rest.to_local(hc, rot, float(item["center"][0]), float(item["center"][1]))
    d_i = float(item["size"][1])
    bw, bd = float(host_fp["size"][0]), float(host_fp["size"][1])
    y0, y1 = ly - d_i / 2.0, ly + d_i / 2.0
    span = (-bd / 2.0 - 0.3 if y0 <= -bd / 2.0 + 0.12 else y0, y1)
    blanket = drape_cover(caster, host_fp, span, floor_z, BLANKET_T_M, None, sd, 0.006, drop=BLANKET_DROP_M,
                          round_m=BLANKET_ROUND_M)
    if blanket is None:
        return None
    bkey = BP.runner_key(look)
    first = BP.sheet_solid(blanket["grid"], blanket["thickness"], bkey, "throw", blanket["normals"])
    parts, strands = [first], []
    out = {"parts": parts, "drape": dict(blanket, grid=blanket["grid"]), "rect": (-bw / 2.0, y0, bw / 2.0, y1)}
    tkey = BP.textile_key(pattern) if pattern else "colour_fabric"
    both = rest.MultiCaster([caster, rest.mesh_caster(first["verts"], first["faces"])])
    edge = blanket["edges"][1] if side == "right" else blanket["edges"][0]
    yt0 = y1 - SIDE_THROW_OVERLAP_M - SIDE_THROW_W_M / 2.0
    t_span = (yt0, yt0 + SIDE_THROW_W_M)
    lim = {"left": edge - SIDE_THROW_ON_M} if side == "right" else {"right": edge + SIDE_THROW_ON_M}
    t_sides = {s: {"free": s == side} for s in BP.SIDES}
    throw = drape_cover(both, host_fp, t_span, floor_z, SIDE_THROW_T_M, None, t_sides, 0.005, limits=lim,
                        drop=SIDE_THROW_DROP_M, round_m=SIDE_THROW_ROUND_M)
    if throw is not None:
        parts.append(BP.sheet_solid(throw["grid"], throw["thickness"], tkey, RUNNER_FOLD_ROLE, throw["normals"]))
        out["runner"] = {"rect": (round(float(throw["local"][0, 0, 0]), 3), round(t_span[0], 3),
                                  round(float(throw["local"][-1, 0, 0]), 3), round(t_span[1], 3)),
                         "share": round(float(throw["share"]), 3), "side": side}
        if fringe:
            for end in ("inner", "hem"):
                cols = BP.to_world_arr(hc, rot, _strand_columns(throw, end).reshape(-1, 3))
                part = BP.fringe_strands(cols.reshape(FRINGE_COLS + 1, -1, 3), tkey)
                if part is not None:
                    strands.append(part)
    parts += strands
    out["weave"] = {"pattern": pattern, "runner_look": look, "fringe": fringe, "fringe_ends": [side] if fringe else [],
                    "fringe_strands": int(sum(int(p.get("strands") or 0) for p in strands)),
                    "rule": weave.get("rule") or BP.RULE, "layout": "p14", "layout_rule": BP.RULE_LOOK,
                    "throw_side": side, "blanket_drop_m": BLANKET_DROP_M,
                    "blanket_look": BP.cover_smoothness(blanket["grid_local"], blanket["local"], blanket["on_top"],
                                                        blanket["edges"])}
    return out


def woven_throw_parts(caster, host_fp: dict, item: dict, floor_z: float, kw: dict,
                      sides: Optional[dict] = None) -> Optional[dict]:
    """29 Oct 2026 (UL121, R35: "a fringed throw folded over the foot and a houndstooth blanket under it"): a throw
    with its ``weave`` (``bedding_parts.throw_weave``, the decor stage's or the family's): the throw itself is the
    blanket in its woven pattern (key ``textile_<pattern>``: the item's colour with the accent colour as its ink), the
    layered second blanket over it the plain throw (``runner_<look>``, the accent colour) with the fringe at its two
    ends; a throw in one layer carries both. ``throw_parts``'s record plus ``weave`` (what was built).

    30 Oct 2026 (UL146, P14): a layered pair on a bed with a free side is laid as the photo lays it
    (``p14_throw_parts``: the plain blanket folded over the foot hanging down the free sides, the patterned fringed
    throw draped at one side); the pair across the foot of before stays for a bed with both sides blocked."""
    from wenart.blender import bedding_parts as BP

    weave = item["weave"]
    pattern = weave.get("pattern") if weave.get("pattern") in BP.PATTERN_SLUGS else None
    look = weave.get("runner_look") if weave.get("runner_look") in BP.LOOK_SLUGS else "knit"
    fringe = bool(weave.get("fringe"))
    ends = tuple(weave.get("fringe_ends") or ("left", "right"))
    layered = int(item.get("layers") or 1) >= 2
    if layered:
        p14 = p14_throw_parts(caster, host_fp, item, floor_z, sides)
        if p14 is not None:
            return p14
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
                offset: Optional[float] = None, sides: Optional[dict] = None) -> Optional[dict]:
    """A throw on a seat end or across a bed's foot (§4.7): its rectangle (the item's centre and size in the host
    frame) draped on the host; a rolled fold along its front edge. Returns ``{"parts", "drape", "rect"}`` or None
    when the cloth finds no top under it. ``step`` / ``offset``: a finer grid and a higher offset for a host that
    shows through the cloth (``rest.plan_throw``).

    29 Oct 2026 (UL106; the professional reference: a knit throw and a second blanket across the bed's foot): an item
    with ``layers`` 2 gets a second, narrower blanket (``layered_runner``: ``RUNNER_SHARE`` of the throw's depth, at
    its foot end) draped on the bed and the first throw together (``rest.MultiCaster``), key ``RUNNER_KEY`` (the
    item's ``accent_colour``, else its colour); the first throw is what S5 measures (``parts[0]``).

    29 Oct 2026 (UL121): an item with a ``weave`` is the woven pair (``woven_throw_parts``: the patterned blanket, the
    fringed throw over it). 30 Oct 2026 (UL146): ``sides`` (the bed's, ``bedding_parts.bed_sides``) for its P14
    layers."""
    kw = {k: v for k, v in (("step", step), ("offset", offset)) if v is not None}
    if isinstance(item.get("weave"), dict):
        return woven_throw_parts(caster, host_fp, item, floor_z, kw, sides)
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


def _lean_pose(caster, host_fp: dict, planned, size, lean_deg: float, stand: bool) -> Optional[dict]:
    """``rest.place_leaning`` on a bed: with ``stand`` (30 Oct 2026, UL137) first standing on what lies at the head
    against the headboard behind the item's upper part (a model's own flat pillows, a gap or posts under a raised
    headboard panel), then the lean of before."""
    pose = rest.place_leaning(caster, host_fp, planned, size, lean_deg=lean_deg, bed=True, stand=True) if stand \
        else None
    return pose if pose is not None else rest.place_leaning(caster, host_fp, planned, size, lean_deg=lean_deg,
                                                             bed=True)


def euro_shams(caster, host_fp: dict, count: int = 2, size: Optional[Sequence[float]] = None, key: str = "bedding",
               mesh_fn=None, colour: Optional[str] = None, stand: bool = False) -> Optional[dict]:
    """``{"parts", "poses"}`` of up to two euro shams against the bed's headboard (pure numpy; ``rest.place_leaning``
    leaned ``SHAM_LEAN_DEG``), None when the bed is narrower than ``SHAM_MIN_BED_W`` or no headboard is hit (a sham
    never stands against nothing). 29 Oct 2026 (UL121): the family set's ``size``, part ``key``, mesh maker
    (``bedding_parts.plump_cushion``) and ``colour``. 30 Oct 2026 (UL137): ``stand`` (``_lean_pose``)."""
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
        pose = _lean_pose(caster, host_fp, planned, (sw, st, sh), SHAM_LEAN_DEG, stand)
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
             key: str = "bedding", mesh_fn=None, colour: Optional[str] = None,
             stand: bool = False) -> Optional[tuple[list, list]]:
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    d = float(host_fp["size"][1])
    lean = 90.0 - PILLOW_TILT_DEG if lean_deg is None else float(lean_deg)
    make = mesh_fn or cushion_mesh
    parts, poses = [], []
    for k in range(n):
        lx = 0.0 if n == 1 else (-1 if k == 0 else 1) * (pw / 2.0 + 0.02)
        planned = rest.to_world(hc, rot, lx, d / 2.0 - ph / 2.0)
        pose = _lean_pose(caster, host_fp, planned, (pw, pt, ph), lean, stand)
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
    y_head = min(y_head, pillow_foot - head_room(poses))   # the duvet ends just before the pillows
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
GAP_SHEET_T_M = 0.004            # 30 Oct 2026 (UL137): the sheet over a gap between the mattress and the headboard ...
GAP_SHEET_ON_M = 0.10            # ... from this far on the mattress before its head edge ...
GAP_SHEET_SAG = (0.3, 0.03)      # ... to the headboard's face, sagging this share of the gap (at most 3 cm) over it
GAP_SHEET_ROLE = "sheet"


def gap_sheet(head: dict, x_span: Sequence[float], key: str) -> Part:
    """30 Oct 2026 (UL137: "there is a gap between the mattress and the headboard ... the gap is closed"): the fitted
    sheet over the mattress's head edge and the gap behind it (pure; bed-local): from ``GAP_SHEET_ON_M`` on the mattress
    to 4 mm before the headboard's face (``rest.bed_head``'s ``head``), across ``x_span``, ``CLOTH_OFFSET_M`` over the
    mattress, sagging a little over the gap. The shams and pillows stand on it at the headboard."""
    from wenart.blender import bedding_parts as BP

    ym, yf, z0 = float(head["mattress_y"]), float(head["face_y"]), float(head["mattress_z"])
    x0, x1 = (float(v) for v in x_span)
    xs = np.linspace(x0, x1, max(2, int(math.ceil((x1 - x0) / 0.05))) + 1)
    gap = max(1e-3, yf - 0.004 - ym)
    ys = np.concatenate([np.linspace(ym - GAP_SHEET_ON_M, ym, 3), ym + gap * np.arange(1, 5) / 4.0])
    sag = min(GAP_SHEET_SAG[1], GAP_SHEET_SAG[0] * gap)
    z = z0 + CLOTH_OFFSET_M + GAP_SHEET_T_M - sag * np.sin(np.pi * np.clip((ys - ym) / gap, 0.0, 1.0))
    grid = np.stack(np.broadcast_arrays(xs[:, None], ys[None, :], z[None, :]), axis=-1)
    return BP.sheet_solid(grid, GAP_SHEET_T_M, key, GAP_SHEET_ROLE)


def bedding_set(caster, host_fp: dict, floor_z: float, spec: dict, sides: Optional[dict] = None,
                mode: str = "full", colours: Optional[Sequence[str]] = None) -> Optional[dict]:
    """29 Oct 2026 (lesson UL121, R35: "a full, soft bed"): the bedding of the family's set (``bedding_parts.
    FAMILY_BEDDING``, ``counts`` by the bed's width) on a bed model, every piece one part of the bed's one dressing
    mesh: (1) the euro shams against the headboard (``euro_shams``; none without a headboard, said in ``explained``),
    (2) the sleeping pillows standing against them (``bedding_parts.PILLOW_UPRIGHT_LEAN_DEG``), else lying against the
    headboard as before, (3) the duvet (``mode`` full): ``drape_cover`` over the foot ``DUVET_SHARE`` with the family's
    thickness (30 Oct 2026, UL136: a smooth top with a few soft wide folds, a rounded edge, straight down to one level
    hem almost at the floor, the family's hem, on each side ``sides`` says is free, ``bedding_parts.bed_sides``, and not
    past a blocked one; its look measured, ``bedding_parts.cover_smoothness``), the thin turned-down sheet band folded
    round its head edge (``bedding_parts.turn_down_band``), (4) the accent cushions and the lumbar standing on the band
    and leaning on the pillows and on each other (``bedding_parts.stack_cushion``: no ray). 30 Oct 2026 (UL137): the
    shams and pillows stand on what lies at the head first; a gap between the mattress and the headboard
    (``rest.bed_head``) is closed by a sheet over it (``gap_sheet``), the head recorded (``record["head"]``).
    ``colours``: the decor stage's cushion colours (the AI's), used for the accent cushions and the lumbar before the
    family's. ``mode`` pillows: the set without our duvet (the model's own duvet kept). ``{"parts", "pillows": [pose],
    "duvet", "record"}`` or None when no pillow finds a place."""
    from wenart.blender import bedding_parts as BP

    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    want = BP.counts(spec, w)
    explained: dict[str, str] = {}
    colours = [c for c in (colours or []) if c]
    # 1. euro shams: standing on what lies at the head against the headboard (30 Oct 2026, UL137: a headboard behind
    # a gap or on posts, a model's own flat pillows), else leaning as before
    sham = None
    if want["euro_shams"]:
        sham = euro_shams(caster, host_fp, want["euro_shams"], size=BP.SHAM_SIZE,
                          key=BP.textile_key(spec["shams"]["look"]), mesh_fn=BP.plump_cushion,
                          colour=spec["shams"].get("colour"), stand=True)
    # 2. sleeping pillows: standing against the shams, else lying against the headboard
    n = want["pillows"]
    pw = min(BP.PILLOW_SIZE[0], (w - 0.1) / n - 0.04)
    pt, ph = BP.PILLOW_SIZE[1], BP.PILLOW_SIZE[2]
    pkey, pcol = BP.textile_key(spec["pillows"]["look"]), spec["pillows"].get("colour")
    got = None
    if sham is not None:
        sv, sf = _merged(sham["parts"])
        got = _pillows(rest.MultiCaster([caster, rest.mesh_caster(sv, sf)]), host_fp, n, pw, pt, ph,
                       lean_deg=BP.PILLOW_UPRIGHT_LEAN_DEG, key=pkey, mesh_fn=BP.plump_cushion, colour=pcol,
                       stand=True)
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
    y_head = min(-d / 2.0 + DUVET_SHARE * d, float(pillow_loc[:, 1].min()) - head_room(poses))
    record = {"rule": BP.RULE, "lesson": BP.LESSON, "family": spec.get("family"), "mode": mode,
              "pillows": n, "pillow_size_m": [round(pw, 3), pt, ph], "pillows_upright": upright,
              "euro_shams": len(sham["parts"]) if sham else 0, "duvet_share": DUVET_SHARE,
              "pillow_local_y": [round(rest.to_local(hc, rot, p["center"][0], p["center"][1])[1], 3) for p in poses],
              "expected": want, "look_rule": BP.RULE_LOOK}
    # 2b. 30 Oct 2026 (UL137: "a gap between the mattress and the headboard"): the head as the shams and pillows found
    # it; a gap between the mattress and the headboard is closed by a sheet over it (the shams stand at the headboard)
    heads = [p["head"] for p in (sham["poses"] if sham else []) + list(poses) if isinstance(p.get("head"), dict)]
    head = max(heads, key=lambda hd: hd["gap_m"]) if heads else None
    record["head"] = dict(head, headboard=bool(sham is not None or upright)) if head else \
        {"headboard": bool(sham is not None or upright), "gap_m": 0.0}
    sheet_x = None
    support = np.zeros((0, 3))
    duvet_got = None
    # 3. the duvet (30 Oct 2026, UL136, UL146): a smooth cover, a level hem, the turned-down sheet band
    if mode == "full":
        ds = spec["duvet"]
        thick, hem = float(ds["thickness_m"]), float(ds.get("hem_m") or 0.08)
        sides = sides or {s: {"free": True} for s in BP.SIDES}
        rtop = CLOTH_OFFSET_M + thick
        wrinkle = float(ds.get("wrinkle_m") or 0.01)
        duvet_got = drape_cover(caster, host_fp, (-d / 2.0 - 0.3, y_head), floor_z, thick, float(floor_z) + hem,
                                sides, wrinkle)
        if duvet_got is None:
            return None
        grid = duvet_got["grid"]
        dkey, dcol = BP.textile_key(ds["look"]), ds.get("colour")
        parts.append(dict(BP.sheet_solid(grid, duvet_got["thickness"], dkey, "duvet", duvet_got["normals"]),
                          colour=dcol))
        loc = duvet_got["local"]
        band = BP.turn_down_band(dict(duvet_got, grid=duvet_got["grid_local"], normals=duvet_got["normals_local"]),
                                 TURN_DOWN_M)
        if band is not None:
            bw = BP.to_world_arr(hc, rot, band.reshape(-1, 3)).reshape(band.shape)
            parts.append(dict(BP.sheet_solid(bw, BP.band_thickness(band), dkey, "turndown"), colour=dcol))
        on = np.asarray(duvet_got["on_top"], dtype=bool)
        support = duvet_got["grid_local"][on]
        if band is not None:
            support = np.concatenate([support, band.reshape(-1, 3)], axis=0)
        e = duvet_got["edges"]
        sheet_x = (e[0], e[1])
        look = BP.cover_smoothness(duvet_got["grid_local"], loc, on, e)
        X, Y = loc[:, 0, 0], loc[0, :, 1]
        rect = (float(X[0]), float(Y[0]), float(X[-1]), float(Y[-1]))
        fold = float(np.max(duvet_got["thickness"][:, -1])) + 2.0 * (BP.BAND_GAP_M + BP.SHEET_T_M)
        record.update(duvet_rect_local=[round(v, 3) for v in rect], top_z=round(float(duvet_got["top_z"]), 4),
                      on_top_share=round(duvet_got["share"], 3),
                      duvet={"look": ds["look"], "colour": dcol, "thickness_m": thick, "rounded_m": round(rtop, 3),
                             "wrinkle_m": ds.get("wrinkle_m"), "hem_m": hem,
                             "grid": [duvet_got["nu"], duvet_got["nv"]],
                             "band": ({"width_m": TURN_DOWN_M, "sheet_m": BP.SHEET_T_M, "fold_m": round(fold, 3)}
                                      if band is not None else None),
                             "smoothness": look, "measure": duvet_got["measure"], "rule": BP.RULE_LOOK},
                      sides=sides, drops=BP.side_drops(grid, loc, w, d, float(duvet_got["top_z"]), floor_z))
    if head and head["gap_m"] >= rest.BED_GAP_MIN_M:
        sheet = gap_sheet(head, sheet_x or (-w / 2.0 + 0.03, w / 2.0 - 0.03), pkey)
        world = BP.to_world_arr(hc, rot, np.asarray(sheet["verts"]))
        parts.append(dict(sheet, verts=[tuple(q) for q in world.tolist()], colour=pcol))
        record["head"]["closed_by"] = "a sheet over the gap, the shams and pillows standing at the headboard"
    if mode != "full":
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


LYING_ROOM_M = 0.26              # 30 Oct 2026 (UL136): before pillows lying at a bed's head edge (no headboard) the
#                                  duvet leaves this much of the mattress: a cushion stands there leaning on them


def head_room(poses) -> float:
    """How far before the pillows the duvet's head ends (pure): 3 cm, ``LYING_ROOM_M`` before pillows lying with
    no headboard (``rest.place_leaning``'s back edge: their head end at the bed's head edge, 30 Oct 2026; they lay
    20 cm further back before, into the wall or the headboard, and left that room)."""
    lying = any(str(p.get("how") or "").startswith("no backrest hit") for p in poses or [])
    return LYING_ROOM_M if lying else 0.03


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

