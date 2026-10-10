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
Deterministic: fixed grids, fold phases from the sizes only.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart.blender import rest

Part = dict

CUSHION_GRID = (10, 10)
SEAM_M = 0.006                    # the half thickness left at a cushion's seam
EDGE_DRAW = 0.035                 # a cushion's edges are drawn in by this share of the side between the corners
CLOTH_OFFSET_M = 0.005            # the shrinkwrap offset (§4.7: 5 mm)
CLOTH_THICKNESS_M = 0.008
FOLD_AMPLITUDE_M = 0.006          # modelled wrinkles (never into the host: added above the offset)
CLOTH_STEP_M = 0.05               # cloth grid pitch
DUVET_SHARE = 0.75                # the duvet covers the foot 75 % of the mattress
DUVET_SIDE_DROP_M = 0.30          # it reaches this far past the mattress sides and the foot (hangs down)
DUVET_THICKNESS_M = 0.04
TURN_DOWN_M = 0.28                # the band folded back at the duvet's head end
PILLOW_SIZE = (0.65, 0.15, 0.45)  # a sleeping pillow: width across the bed, thickness, length along the bed
PILLOW_TILT_DEG = 14.0            # lying, its head end raised against the headboard
TWO_PILLOW_MIN_W = 1.30           # beds at least this wide take two pillows side by side
PLEAT_PITCH_M = 0.12
PLEAT_DEPTH_M = 0.035
CURTAIN_PANEL_SHARE = 0.22        # each open panel covers this share of the rod (= parametric.CURTAIN_PANEL_SHARE)
CURTAIN_LAYER_M = 0.003
SLAT_M = 0.025
SLAT_GAP_M = 0.022
SLAT_TILT_DEG = 20.0
BLIND_KINDS = ("roller", "slats")


def _part(verts, faces, key: str, role: str, smooth: bool = True) -> Part:
    return {"verts": [tuple(float(c) for c in v) for v in verts], "faces": [list(f) for f in faces], "key": key,
            "role": role, "smooth": smooth}


# --------------------------------------------------------------------------
# Cushions and pillows
# --------------------------------------------------------------------------

def cushion_mesh(w: float, t: float, h: float, grid: tuple[int, int] = CUSHION_GRID, key: str = "colour_fabric",
                 role: str = "cushion") -> Part:
    """A filled cushion in the box ``w x t x h`` (item frame: width X, thickness Y, height Z from 0): two faces
    bulging to ``t / 2`` in the middle (``(1 - u^4)(1 - v^4)`` profile), meeting at a ``SEAM_M`` seam; the seam
    ring is shared, so the mesh is closed; the edges are drawn in by ``EDGE_DRAW`` between the corners."""
    nu, nv = grid
    w, t, h = float(w), float(t), float(h)
    verts: list[tuple[float, float, float]] = []
    index: dict[tuple[int, int, int], int] = {}

    def vid(i: int, j: int, side: int) -> int:
        boundary = i in (0, nu) or j in (0, nv)
        key_ = (i, j, 0 if boundary else side)
        if key_ in index:
            return index[key_]
        u = -1.0 + 2.0 * i / nu
        v = -1.0 + 2.0 * j / nv
        draw_x = 1.0 - EDGE_DRAW * math.sin(math.pi * (v + 1.0) / 2.0)   # sides drawn in between the corners
        draw_z = 1.0 - EDGE_DRAW * math.sin(math.pi * (u + 1.0) / 2.0)
        x = u * w / 2.0 * draw_x
        z = h / 2.0 + v * h / 2.0 * draw_z
        half = max(SEAM_M, t / 2.0 * (1.0 - u ** 4) * (1.0 - v ** 4)) if not boundary else min(SEAM_M, t / 2.0)
        y = 0.0 if boundary else side * half
        index[key_] = len(verts)
        verts.append((x, y, z))
        return index[key_]

    faces = []
    for i in range(nu):
        for j in range(nv):
            # back face (+Y) outward = +Y; front face (-Y) outward = -Y
            faces.append([vid(i, j, 1), vid(i, j + 1, 1), vid(i + 1, j + 1, 1), vid(i + 1, j, 1)])
            faces.append([vid(i, j, -1), vid(i + 1, j, -1), vid(i + 1, j + 1, -1), vid(i, j + 1, -1)])
    zmin = min(v[2] for v in verts)
    verts = [(x, y, z - zmin) for x, y, z in verts]
    return _part(verts, faces, key, role)


def lying_cushion_mesh(w: float, d: float, t: float, key: str = "colour_fabric", role: str = "cushion") -> Part:
    """A cushion lying flat in the box ``w x d x t`` (thickness along Z from 0): ``cushion_mesh`` turned so its
    faces look up and down."""
    part = cushion_mesh(w, t, d, key=key, role=role)
    part["verts"] = [(x, z - d / 2.0, y + t / 2.0) for x, y, z in part["verts"]]
    # (x, y, z) -> (x, z, y) mirrors the winding: reverse the faces to keep them outward
    part["faces"] = [list(reversed(f)) for f in part["faces"]]
    zmin = min(v[2] for v in part["verts"])
    part["verts"] = [(x, y, z - zmin) for x, y, z in part["verts"]]
    return part


def flat_cloth(w: float, d: float, t: float, key: str = "colour_fabric", role: str = "throw") -> Part:
    """A cloth lying on a flat top (no host to drape over): its modelled folds on a plane, ``t`` at most high."""
    nu = max(2, int(round(w / CLOTH_STEP_M)))
    nv = max(2, int(round(d / CLOTH_STEP_M)))
    grid = np.zeros((nu + 1, nv + 1, 3))
    for i in range(nu + 1):
        for j in range(nv + 1):
            x, y = -w / 2.0 + w * i / nu, -d / 2.0 + d * j / nv
            grid[i, j] = (x, y, min(t, CLOTH_THICKNESS_M + fold(x + w / 2.0, y + d / 2.0, w, d) * 0.5))
    part = cloth_solid(grid, CLOTH_THICKNESS_M, key=key, role=role, along=(0.0, 0.0, 1.0))
    zmin = min(v[2] for v in part["verts"])
    part["verts"] = [(x, y, z - zmin) for x, y, z in part["verts"]]
    return part


# --------------------------------------------------------------------------
# Cloth draped on the host
# --------------------------------------------------------------------------

def fold(x: float, y: float, w: float, d: float) -> float:
    """Modelled wrinkles (>= 0, at most ``FOLD_AMPLITUDE_M``): smooth fixed sines over the cloth's own frame."""
    a = math.sin(7.3 * x / max(w, 1e-6) + 0.7) * math.sin(5.1 * y / max(d, 1e-6) + 1.9)
    b = math.sin(13.0 * (x + 0.6 * y) / max(w + d, 1e-6) + 2.3)
    return FOLD_AMPLITUDE_M * (0.5 + 0.3 * a + 0.2 * b)


def drape(caster, host_fp: dict, rect: Sequence[float], floor_z: float, step: float = CLOTH_STEP_M,
          offset: float = CLOTH_OFFSET_M, top_band: float = rest.TOP_BAND_M,
          thickness: float = CLOTH_THICKNESS_M) -> dict:
    """A cloth over the rectangle ``rect`` = (x0, y0, x1, y1) in the host frame, draped on the host mesh.

    Returns ``{"grid": (nu + 1) x (nv + 1) x 3 world points, "on_top": bool grid, "top_z": the median top, "share":
    on-top share}``. A grid point is on top when its downward ray hits the host within ``top_band`` of the median
    top (the grid is the cloth's top: its underside, ``thickness`` lower, rests 5 mm ``offset`` + folds above the
    hit); the others hang: from the nearest on-top point (grid distance) the cloth falls by the plan length it
    reaches past it, pushed out of the host's side by a horizontal ray (offset + thickness outside the hit), never
    below the floor + 2 cm."""
    x0, y0, x1, y1 = (float(v) for v in rect)
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    nu = max(2, int(round((x1 - x0) / step)))
    nv = max(2, int(round((y1 - y0) / step)))
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


def _vertex_normals(grid: np.ndarray) -> np.ndarray:
    """Unit vertex normals of a grid surface, turned so that they point up on average (the cloth's outside)."""
    gu = np.gradient(grid, axis=0)
    gv = np.gradient(grid, axis=1)
    n = np.cross(gu, gv)
    ln = np.linalg.norm(n, axis=2, keepdims=True)
    n = n / np.where(ln < 1e-12, 1.0, ln)
    return -n if n.reshape(-1, 3).mean(axis=0)[2] < 0 else n


def cloth_solid(grid: np.ndarray, thickness: float = CLOTH_THICKNESS_M, key: str = "colour_fabric",
                role: str = "throw", along: Optional[Sequence[float]] = None) -> Part:
    """The draped sheet as a thin closed solid: the top layer = the grid, the bottom layer ``thickness`` below it
    along the vertex normals (or along the fixed direction ``along``: a flat cloth, a curtain panel, so the solid
    stays inside its box), joined at the rim; outward normals."""
    nu, nv = grid.shape[0] - 1, grid.shape[1] - 1
    normals = _vertex_normals(grid) if along is None else np.broadcast_to(np.asarray(along, dtype=np.float64),
                                                                           grid.shape)
    top = grid
    bottom = grid - normals * thickness
    verts = [tuple(p) for p in top.reshape(-1, 3)] + [tuple(p) for p in bottom.reshape(-1, 3)]
    n = (nu + 1) * (nv + 1)

    def t(i, j):
        return i * (nv + 1) + j

    faces = []
    for i in range(nu):
        for j in range(nv):
            faces.append([t(i, j), t(i + 1, j), t(i + 1, j + 1), t(i, j + 1)])
            faces.append([n + t(i, j), n + t(i, j + 1), n + t(i + 1, j + 1), n + t(i + 1, j)])
    rim = [(i, 0) for i in range(nu)] + [(nu, j) for j in range(nv)] + [(i, nv) for i in range(nu, 0, -1)] + \
          [(0, j) for j in range(nv, 0, -1)]
    for k in range(len(rim)):
        a, b = rim[k], rim[(k + 1) % len(rim)]
        faces.append([t(*a), n + t(*a), n + t(*b), t(*b)])
    return _part(verts, faces, key, role)


def throw_parts(caster, host_fp: dict, item: dict, floor_z: float) -> Optional[dict]:
    """A throw on a seat end or across a bed's foot (§4.7): its rectangle (the item's centre and size in the host
    frame) draped on the host; a rolled fold along its front edge. Returns ``{"parts", "drape", "rect"}`` or None
    when the cloth finds no top under it."""
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    lx, ly = rest.to_local(hc, rot, float(item["center"][0]), float(item["center"][1]))
    w, d = float(item["size"][0]), float(item["size"][1])
    rect = (lx - w / 2.0, ly - d / 2.0, lx + w / 2.0, ly + d / 2.0)
    got = drape(caster, host_fp, rect, floor_z)
    if got["grid"] is None:
        return None
    sheet = cloth_solid(got["grid"], key="colour_fabric", role="throw")
    return {"parts": [sheet], "drape": got, "rect": rect}


# --------------------------------------------------------------------------
# Bedding of a bed whose model has none
# --------------------------------------------------------------------------

def mattress_rect(host_fp: dict, inset: float = 0.0) -> tuple[float, float, float, float]:
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    return (-w / 2.0 + inset, -d / 2.0 + inset, w / 2.0 - inset, d / 2.0 - inset)


def pillow_count(width: float) -> int:
    return 2 if float(width) >= TWO_PILLOW_MIN_W - 1e-9 else 1


def duvet_and_pillows(caster, host_fp: dict, floor_z: float) -> Optional[dict]:
    """The bedding of a bed model without bedding (§4.7): ``{"parts", "pillows": [pose], "duvet": drape record,
    "record"}``; None when no mattress top is found. The pillows are placed first against the headboard
    (``rest.place_leaning`` with the pillow leaned ``90 - PILLOW_TILT_DEG``: lying, its head end raised); the duvet
    covers the foot ``DUVET_SHARE`` of the bed, ``DUVET_SIDE_DROP_M`` past the sides and the foot, with a turned-down
    band at its head end lying on it."""
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    n = pillow_count(w)
    pw = min(PILLOW_SIZE[0], (w - 0.1) / n - 0.04)
    pt, ph = PILLOW_SIZE[1], PILLOW_SIZE[2]
    parts, poses = [], []
    for k in range(n):
        lx = 0.0 if n == 1 else (-1 if k == 0 else 1) * (pw / 2.0 + 0.02)
        planned = rest.to_world(hc, rot, lx, d / 2.0 - ph / 2.0)
        pose = rest.place_leaning(caster, host_fp, planned, (pw, pt, ph), lean_deg=90.0 - PILLOW_TILT_DEG)
        if pose is None:
            return None
        mesh = cushion_mesh(pose["size"][0], pt, ph, key="bedding", role="pillow")
        parts.append(dict(mesh, verts=rest.pose_vertices(mesh["verts"], pose)))
        poses.append(pose)
    y_head = -d / 2.0 + DUVET_SHARE * d
    pillow_foot = min(rest.to_local(hc, rot, v[0], v[1])[1] for p in parts for v in p["verts"])
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
              "duvet_share": DUVET_SHARE, "top_z": round(float(got["top_z"]), 4), "on_top_share": round(got["share"], 3),
              "rule": "procedural bedding: the bed model has no bedding (docs/milestone12.md §4.7)"}
    return {"parts": parts, "pillows": poses, "duvet": got, "record": record}


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


# --------------------------------------------------------------------------
# Window dressings
# --------------------------------------------------------------------------

def _pleated_panel(x0: float, x1: float, h: float, depth: float, key: str) -> Part:
    """A pleated curtain panel from x0 to x1 (item frame), hanging from h down to 0: a sine of ``PLEAT_PITCH_M`` in
    Y (depth ``PLEAT_DEPTH_M``, a little deeper at the hem), two layers ``CURTAIN_LAYER_M`` apart, closed."""
    width = x1 - x0
    nu = max(4, int(round(width / (PLEAT_PITCH_M / 4.0))))
    nv = 6
    grid = np.zeros((nu + 1, nv + 1, 3))
    amp = min(PLEAT_DEPTH_M, depth / 2.0 - CURTAIN_LAYER_M)
    for i in range(nu + 1):
        x = x0 + width * i / nu
        for j in range(nv + 1):
            z = h * j / nv
            flare = 1.0 + 0.25 * (1.0 - j / nv)
            grid[i, j] = (x, amp * flare * math.sin(2.0 * math.pi * (x - x0) / PLEAT_PITCH_M) * 0.5, z)
    part = cloth_solid(grid, CURTAIN_LAYER_M, key=key, role="panel", along=(0.0, 1.0, 0.0))
    part["smooth"] = True
    return part


def curtain_parts(w: float, d: float, h: float, key: str = "colour_fabric") -> list[Part]:
    """An open pair of pleated panels under a rod (item frame: width X along the wall, the curtain's front -Y, from
    the floor gap up to the rod at ``h``): each panel covers ``CURTAIN_PANEL_SHARE`` of the rod."""
    from wenart.blender import parametric as P

    parts = [P._cylinder_x(-w / 2.0, 0.0, h - 0.02, 0.012, 0.012, w, "steel", "rod", n=12)]
    pw = w * CURTAIN_PANEL_SHARE
    parts.append(_pleated_panel(-w / 2.0, -w / 2.0 + pw, h - 0.05, d, key))
    parts.append(_pleated_panel(w / 2.0 - pw, w / 2.0, h - 0.05, d, key))
    return parts


def blind_parts(w: float, d: float, h: float, kind: str = "roller", key: str = "colour_fabric") -> list[Part]:
    """A roller blind (a tube at the top, the fabric panel down to a bottom bar) or a slatted blind (``SLAT_M``
    slats every ``SLAT_M + SLAT_GAP_M`` tilted ``SLAT_TILT_DEG``, a head rail, two ladder tapes) in the box
    ``w x d x h`` (bottom at 0)."""
    from wenart.blender import parametric as P

    if kind not in BLIND_KINDS:
        kind = "roller"
    if kind == "roller":
        tube = min(0.03, d / 2.0, h / 4.0)
        bar = min(0.02, h / 8.0)
        return [P._cylinder_x(-w / 2.0, 0.0, h - tube, tube, tube, w, key, "roller", n=16),
                P._box(0.0, -tube * 0.4, bar, w - 0.02, 0.004, h - tube - bar, key, "panel"),
                P._box(0.0, -tube * 0.4, 0.0, w - 0.02, min(0.012, d), bar, "dark", "bar")]
    head = min(0.04, h / 6.0)
    parts = [P._box(0.0, 0.0, h - head, w, min(d, 0.04), head, "painted", "rail")]
    pitch = SLAT_M + SLAT_GAP_M
    n = max(1, int((h - head) / pitch))
    a = math.radians(SLAT_TILT_DEG)
    sw = min(d * 0.9, SLAT_M * 1.6)
    for k in range(n):
        zc = h - head - (k + 0.5) * pitch
        if zc - SLAT_M < 0:
            break
        verts = []
        for dy, dz in ((-sw / 2.0, 0.0), (sw / 2.0, 0.0)):
            y, z = dy * math.cos(a), zc + dy * math.sin(a)
            verts += [(-w / 2.0 + 0.01, y, z - 0.0007), (w / 2.0 - 0.01, y, z - 0.0007),
                      (w / 2.0 - 0.01, y, z + 0.0007), (-w / 2.0 + 0.01, y, z + 0.0007)]
        faces = [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
        parts.append(_part(verts, faces, key, "slat", smooth=False))
    for sx in (-w / 3.0, w / 3.0):
        parts.append(P._box(sx, 0.0, 0.0, 0.012, 0.002, h - head, "dark", "tape"))
    return parts
