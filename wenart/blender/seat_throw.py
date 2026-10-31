"""A throw on a sofa or an armchair, draped as a stylist drapes it (31 Oct 2026; user on real04 run
20261030-181158-full, the long white corner sofa with four scatter cushions and a 50 x 45 cm cream sheet flat on its
seat: "bedding on this sofa could have been a lot better not just pillows maybe include some comfortals").

What (pure: numpy, ``wenart.blender.rest`` casters and the cover maths of ``textiles`` / ``bedding_parts``; no
``bpy``, so the decor stage and the build both read it):

- ``throw_look``: the look of a seat's throw by style family (``FAMILY_SEAT_THROW``: a chunky knit, a boucle, a wool or
  a washed linen, fringed or not) and its colour: the first of the item's colour, the brief's throw colours and its
  cushion colours that stands out from the sofa's fabric (CIELAB distance at least ``CONTRAST_DE``), else the family's
  contrast for a light or a dark sofa.
- ``measure_seat`` / ``measure_arm``: the seat's top and each end's arm (its top, inner and outer faces, its front)
  measured by rays on the built sofa.
- ``arm_throw``: a throw folded in three lengthwise (``THROW_W_M`` wide, ``THROW_T_M`` thick) laid over an arm: over the
  arm's top with a soft rounded edge, straight down its outer face ``ARM_DROP_M`` with a few soft folds and its fringe
  at the hem, down its inner face onto the seat (its end lies on the seat, never in it).
- ``seat_end_throw``: where an end has no arm (a chaise end, an armless sofa): the folded throw laid across the seat's
  end from the back cushions to the front, hanging ``SEAT_DROP_M`` down the seat's front with its fringe at the hem.
- ``candidates``: the drapes to try in order (the preferred end's arm, the other arm, the seat ends); the build keeps
  the first that rests (``rest.plan_throw``: S5 and the cloth's own checks).

Why: the decor throw of a seat was a flat 5 cm sheet of 50 x 45 cm on the seat in the cushions' cream: on a white sofa
it did not show. A real throw is a 130 x 170 cm blanket, folded and draped over the arm or across a seat end, in a
fabric with texture and a colour that stands out from the sofa (designer rule, assumed: one per seating group, chosen
with the style; ``decor_ai.living_dressing`` moves the room's throw to the main sofa).
"""
from __future__ import annotations

import math
from typing import Iterator, Optional, Sequence

import numpy as np

from wenart.blender import bedding_parts as BP
from wenart.blender import rest

RULE = "seat_throw"
TAG = ("31 Oct 2026, user on the review of run 20261030-181158-full: \"bedding on this sofa could have been a lot better not "
       "just pillows maybe include some comfortals\"")
SEAT_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise")
DRAPES: tuple[str, ...] = ("arm", "seat_end")

# the family's throw (designer values): its look (a ``bedding_parts.LOOKS`` weave with a CC0 scan), a fringe, and the
# contrast colour on a light and on a dark sofa where neither the item nor the brief names one that stands out
FAMILY_SEAT_THROW: dict[str, dict] = {
    "modern": {"look": "knit", "fringe": False, "contrast": ("charcoal", "cream"),
               "why": "a chunky knit throw (modern: a soft texture against clean lines)"},
    "contemporary": {"look": "boucle", "fringe": False, "contrast": ("taupe", "cream"),
                     "why": "a boucle throw (contemporary: a tactile, quiet layer)"},
    "modern minimal": {"look": "wool", "fringe": False, "contrast": ("greige", "light grey"),
                       "why": "a plain wool throw without a fringe (minimal: calm surfaces)"},
    "minimal": {"look": "wool", "fringe": False, "contrast": ("greige", "light grey"),
                "why": "a plain wool throw without a fringe (minimal: calm surfaces)"},
    "scandinavian": {"look": "knit", "fringe": True, "contrast": ("sage", "cream"),
                     "why": "a fringed knit throw (Scandinavian: natural textures)"},
    "japandi": {"look": "linen", "fringe": True, "contrast": ("olive", "beige"),
                "why": "a washed linen throw with a fringe (Japandi: natural, restrained)"},
    "industrial": {"look": "wool", "fringe": True, "contrast": ("rust", "camel"),
                   "why": "a fringed wool throw (industrial: robust textures)"},
    "mediterranean": {"look": "linen", "fringe": True, "contrast": ("terracotta", "sand"),
                      "why": "a fringed linen throw (Mediterranean: sun-washed linen)"},
    "classic": {"look": "wool", "fringe": True, "contrast": ("navy", "cream"),
                "why": "a fringed wool throw (classic: rich, layered)"},
    "rustic": {"look": "knit", "fringe": True, "contrast": ("rust", "cream"),
               "why": "a fringed chunky knit throw (rustic: warm and heavy)"},
}
DEFAULT_FAMILY = "modern"
CONTRAST_DE = 25.0               # a throw's colour this far (CIELAB distance) from the sofa's fabric stands out
LIGHT_SOFA_L = 55.0              # a sofa lighter than this (L*) takes the family's dark contrast

# the folded throw and its drapes (designer values: a 130 x 170 cm throw folded in three lengthwise)
THROW_W_M = 0.50                 # the folded throw's width (along the arm or across the seat's end)
THROW_MIN_W_M = 0.30
THROW_T_M = 0.02                 # three layers of a chunky knit
ROUND_M = 0.035                  # its soft roll over an edge
WRINKLE_M = 0.006                # its few soft folds on the top
ARM_DROP_M = 0.34                # over an arm: it hangs this far down the outer face ...
SEAT_CLEAR_M = 0.006             # ... and down the inner face to this over the seat
SEAT_DROP_M = 0.30               # across a seat end: it hangs this far down the front
ARM_RISE_MIN_M = 0.10            # an arm rises at least this over the seat ...
ARM_W_M = (0.05, 0.40)           # ... and is this wide
ARM_SCAN_M = 0.50                # an end is scanned this far in for its arm
SCAN_STEP_M = 0.02
BACK_RISE_M = 0.10               # the back cushions rise this over the seat (the seat's back limit)


# --------------------------------------------------------------------------
# the look
# --------------------------------------------------------------------------

def _lab(colour: Optional[str]) -> Optional[tuple[float, float, float]]:
    from wenart.style import colours as COL

    if not colour or not COL.known(str(colour)):
        return None
    try:
        return COL.linear_to_lab(COL.linear_rgb(str(colour)))
    except (KeyError, ValueError):
        return None


def colour_distance(a: Optional[str], b: Optional[str]) -> Optional[float]:
    """The CIELAB (CIE76) distance between two colour names (pure), None when one is unknown."""
    la, lb = _lab(a), _lab(b)
    if la is None or lb is None:
        return None
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(la, lb)))


def family_look(family: Optional[str]) -> tuple[dict, str]:
    """``(row, family)`` of ``FAMILY_SEAT_THROW`` (the modern row for a family it does not list)."""
    fam = str(family or "").lower()
    return dict(FAMILY_SEAT_THROW.get(fam) or FAMILY_SEAT_THROW[DEFAULT_FAMILY]), \
        (fam if fam in FAMILY_SEAT_THROW else DEFAULT_FAMILY)


def throw_colour(sofa: Optional[str], candidates: Sequence[Optional[str]], family: Optional[str]) -> tuple[str, str]:
    """``(colour, why)`` of a seat's throw (pure): the first candidate (the item's colour, the brief's throw and cushion
    colours) at least ``CONTRAST_DE`` from the sofa's fabric colour; without a known sofa colour the first known
    candidate; else the family's contrast for a light (L* over ``LIGHT_SOFA_L``) or a dark sofa."""
    row, fam = family_look(family)
    known = [str(c).lower() for c in candidates if c and _lab(str(c).lower()) is not None]
    sofa_lab = _lab(sofa)
    if sofa_lab is None:
        if known:
            return known[0], f"{known[0]}: the item's or the brief's colour (the sofa's colour is not known)"
        return row["contrast"][0], f"{row['contrast'][0]}: the {fam} family's contrast (no colour named)"
    for c in known:
        de = colour_distance(c, sofa)
        if de is not None and de >= CONTRAST_DE - 1e-9:
            return c, f"{c}: stands out from the {sofa} sofa (CIELAB distance {de:.0f} >= {CONTRAST_DE:.0f})"
    dark, light = row["contrast"]
    pick = dark if sofa_lab[0] >= LIGHT_SOFA_L else light
    why = ", ".join(known) if known else "no colour"
    return pick, (f"{pick}: the {fam} family's contrast on a {'light' if pick == dark else 'dark'} {sofa} sofa ({why} "
                  f"too close to it)")


def throw_look(family: Optional[str], sofa_colour: Optional[str] = None,
               candidates: Sequence[Optional[str]] = (), side: Optional[str] = None) -> dict:
    """The ``seat_throw`` record of a seat's throw (pure): ``{"look", "fringe", "colour", "drape": "arm", "side",
    "family", "rule", "why"}`` (``FAMILY_SEAT_THROW``, ``throw_colour``)."""
    row, fam = family_look(family)
    colour, cwhy = throw_colour(sofa_colour, candidates, fam)
    return {"look": row["look"], "fringe": bool(row["fringe"]), "colour": colour, "drape": "arm",
            "side": side if side in ("left", "right") else None, "family": fam, "rule": RULE,
            "why": f"{row['why']} in {cwhy}; folded over the arm, else across the seat's end ({TAG})"}


def sofa_colour(host: dict, style: Optional[dict]) -> Optional[str]:
    """The fabric colour a seat is built in (pure): its design's, else the style's for its type, else the brief's sofa
    colour (``colours.sofa``), else its fabric colour; None when nothing names one."""
    design = host.get("design") if isinstance(host.get("design"), dict) else {}
    for k in ("fabric_colour", "colour"):
        if design.get(k):
            return str(design[k])
    st = style or {}
    furn = st.get("furniture") if isinstance(st.get("furniture"), dict) else {}
    by = (furn.get("by_type") or {}).get(host.get("type")) if isinstance(furn.get("by_type"), dict) else None
    if isinstance(by, dict) and (by.get("fabric_colour") or by.get("colour")):
        return str(by.get("fabric_colour") or by.get("colour"))
    sofa = (st.get("colours") or {}).get("sofa") if isinstance(st.get("colours"), dict) else None
    if isinstance(sofa, list) and sofa:
        return str(sofa[0])
    if furn.get("fabric_colour"):
        return str(furn["fabric_colour"])
    return None


# --------------------------------------------------------------------------
# measuring the seat and its arms (rays on the built host)
# --------------------------------------------------------------------------

def _down_grid(caster, host_fp: dict, lx: np.ndarray, ly: np.ndarray) -> np.ndarray:
    from wenart.blender import textiles as T

    top_from = rest.host_top(caster) + rest.TOP_ABOVE_M
    return T._down(caster, host_fp["center"], float(host_fp["rotation_deg"]), np.asarray(lx, dtype=np.float64),
                   np.asarray(ly, dtype=np.float64), top_from)


def measure_seat(caster, host_fp: dict) -> Optional[float]:
    """The seat's top (pure): the median of the lowest band (12 cm) of ray hits over the seat's front half, out of the
    ends (the arms); None when no ray finds the host."""
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    m = min(0.35, w * 0.25)
    lx, ly = np.meshgrid(np.linspace(-w / 2.0 + m, w / 2.0 - m, 5), -d / 2.0 + d * np.array([0.2, 0.3, 0.4]),
                         indexing="ij")
    z = _down_grid(caster, host_fp, lx, ly)
    found = z[~np.isnan(z)]
    if not len(found):
        return None
    low = found[found <= float(found.min()) + 0.12]
    return float(np.median(low))


def measure_arm(caster, host_fp: dict, side: str, seat_z: float) -> Optional[dict]:
    """The arm at one end of a seat (pure; ``side`` left = -x, right = +x of the host frame): rays down from the end
    inwards over the seat's front-middle find the run that rises ``ARM_RISE_MIN_M`` over the seat (its top: the run's
    median, its inner face: where the run ends), a side ray from outside its outer face, rays down along its middle its
    front. ``{"side", "x_in", "x_out", "x_mid", "width", "top_z", "y_front", "seat_z"}`` or None (no arm there)."""
    w, d = float(host_fp["size"][0]), float(host_fp["size"][1])
    s = 1.0 if side == "right" else -1.0
    n = max(2, int(min(ARM_SCAN_M, w * 0.4) / SCAN_STEP_M))
    xs = s * (w / 2.0 - 0.005 - SCAN_STEP_M * np.arange(n))
    # the seat's depth beside this end (a corner sofa's long part sits behind its chaise's front), else the box's
    depth = seat_depth(caster, host_fp, s * (w / 2.0 - min(0.45, w * 0.25)), seat_z)
    ys = (depth[0] + (depth[1] - depth[0]) * np.array([0.3, 0.6])) if depth else -d / 2.0 + d * np.array([0.3, 0.42])
    lx, ly = np.meshgrid(xs, ys, indexing="ij")
    z = _down_grid(caster, host_fp, lx, ly)
    zx = np.where(np.all(np.isnan(z), axis=1), np.nan, np.nanmax(np.where(np.isnan(z), -np.inf, z), axis=1))
    valid = np.nonzero(~np.isnan(zx))[0]
    if not len(valid):
        return None
    k0 = int(valid[0])
    if zx[k0] < seat_z + ARM_RISE_MIN_M:
        return None
    k1 = k0
    while k1 + 1 < n and not np.isnan(zx[k1 + 1]) and zx[k1 + 1] >= seat_z + ARM_RISE_MIN_M * 0.6:
        k1 += 1
    if k1 + 1 >= n:                                  # high all the way in: a back or a table, no arm
        return None
    top = float(np.median(zx[k0:k1 + 1]))
    x_in = float(xs[k1] - s * SCAN_STEP_M / 2.0)
    # the outer face: side rays from outside at the arm's top less 2 cm
    from wenart.blender import textiles as T

    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    far = w / 2.0 + 0.6
    outs = []
    for y in ys:
        t = T._side_ray(caster, hc, rot, (s * far, float(y)), (-s, 0.0), top - 0.02, far + 0.1)
        if t is not None and t <= far:
            outs.append(s * (far - t))
    x_out = (max(outs) if s > 0 else min(outs)) if outs else float(xs[k0])
    width = abs(x_out - x_in)
    if not ARM_W_M[0] <= width <= ARM_W_M[1]:
        return None
    x_mid = (x_in + x_out) / 2.0
    yy = np.arange(-d / 2.0 - 0.02, d / 2.0 + 1e-9, SCAN_STEP_M)
    zy = _down_grid(caster, host_fp, np.full(len(yy), x_mid), yy)
    front = [float(y) for y, zz in zip(yy, zy) if not np.isnan(zz) and zz >= top - 0.04]
    if not front:
        return None
    return {"side": side, "x_in": round(x_in, 4), "x_out": round(x_out, 4), "x_mid": round(x_mid, 4),
            "width": round(width, 4), "top_z": round(top, 4), "y_front": round(front[0], 4),
            "seat_z": round(float(seat_z), 4)}


def seat_depth(caster, host_fp: dict, x: float, seat_z: float) -> Optional[tuple[float, float]]:
    """``(y_front, y_back)`` of the seat at host-local ``x`` (pure): rays down along the depth; the seat is the run of
    hits within 7 cm of the seat's top from the front, it ends where the back rises ``BACK_RISE_M``."""
    d = float(host_fp["size"][1])
    yy = np.arange(-d / 2.0 - 0.02, d / 2.0 + 1e-9, SCAN_STEP_M)
    zy = _down_grid(caster, host_fp, np.full(len(yy), float(x)), yy)
    y_front, y_back = None, None
    for y, z in zip(yy, zy):
        if np.isnan(z):
            if y_front is not None:
                break
            continue
        if y_front is None:
            if abs(z - seat_z) <= 0.07:
                y_front = float(y)
            continue
        if z > seat_z + BACK_RISE_M:
            y_back = float(y) - 0.03
            break
        y_back = float(y)
    if y_front is None or y_back is None or y_back - y_front < 0.25:
        return None
    return y_front, y_back


# --------------------------------------------------------------------------
# the drapes
# --------------------------------------------------------------------------

def _world_cover(cover: dict, vhost: dict, offset_xy: tuple[float, float]) -> dict:
    """A ``cover_grid`` built in a virtual host's frame (an arm, a seat end) to the world, and its local grid in the
    seat's own frame (the same rotation, moved by ``offset_xy``)."""
    rot = float(vhost["rotation_deg"])
    g = cover["grid"]
    cover["grid_local"] = g + np.array([offset_xy[0], offset_xy[1], 0.0])
    cover["grid"] = BP.to_world_arr(vhost["center"], rot, g.reshape(-1, 3)).reshape(g.shape)
    cover["normals_local"] = cover["normals"]
    cover["normals"] = BP.to_world_arr((0.0, 0.0), rot, cover["normals"].reshape(-1, 3)).reshape(g.shape)
    return cover


def _fringe(cover: dict, host_fp: dict, which: str, key: str, inward: float = 0.0) -> Optional[dict]:
    """The strands at one hem of a throw (pure): ``left`` / ``right`` / ``foot`` (the outermost column or the first
    row of its local grid, in the seat's frame), hanging straight down, or lying flat towards ``inward`` (+1 / -1 along
    x) where the hem rests on the seat."""
    from wenart.blender import textiles as T

    g = np.asarray(cover["grid_local"], dtype=np.float64)
    base = g[0] if which == "left" else g[-1] if which == "right" else g[:, 0]
    step = BP.FRINGE_M / T.FRINGE_COLS
    if inward:
        cols = np.stack([base + np.array([inward * step * k, 0.0, 0.0]) for k in range(T.FRINGE_COLS + 1)], axis=0)
    else:
        cols = np.stack([base + np.array([0.0, 0.0, -step * k]) for k in range(T.FRINGE_COLS + 1)], axis=0)
    world = BP.to_world_arr(host_fp["center"], float(host_fp["rotation_deg"]), cols.reshape(-1, 3))
    return BP.fringe_strands(world.reshape(cols.shape), key)


def arm_throw(caster, host_fp: dict, arm: dict, look: dict, floor_z: float) -> Optional[dict]:
    """The folded throw over an arm (pure; ``measure_arm``'s arm): a cover over the arm's top (``textiles
    .measure_cover`` on the arm as its host: from the arm's front, ``THROW_W_M`` along it), hanging ``ARM_DROP_M`` down
    the outer face and down the inner face to ``SEAT_CLEAR_M`` over the seat beside the arm (``bedding_parts
    .cover_grid`` with a hang per side); the fringe hangs at the outer hem and lies on the seat at the inner one. ``{
    "parts", "drape", "rect" (the top in the seat's frame), "how"}`` or None."""
    from wenart.blender import textiles as T

    d = float(host_fp["size"][1])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    s = 1.0 if arm["side"] == "right" else -1.0
    y0 = float(arm["y_front"]) + 0.01
    tw = min(THROW_W_M, d / 2.0 - 0.12 - y0)
    if tw < THROW_MIN_W_M:
        return None
    aw = float(arm["width"])
    xc, yc = float(arm["x_mid"]), y0 + tw / 2.0
    vc = rest.to_world(hc, rot, xc, yc)
    vhost = {"center": [vc[0], vc[1]], "size": [aw, tw], "rotation_deg": rot}
    sides = {"left": {"free": True}, "right": {"free": True}, "foot": {"free": False}}
    m = T.measure_cover(caster, vhost, (-tw / 2.0, tw / 2.0), floor_z, sides, None, None, drop=ARM_DROP_M)
    if m is None or abs(float(m["top_z"]) - float(arm["top_z"])) > 0.06:
        return None
    # the seat beside the arm, under the inner hang
    ys = np.linspace(y0 + 0.03, y0 + tw - 0.03, 5)
    xi = float(arm["x_in"])
    lx, ly = np.meshgrid(np.array([xi - s * 0.03, xi - s * 0.06]), ys, indexing="ij")
    zs = _down_grid(caster, host_fp, lx, ly)
    zs = zs[~np.isnan(zs) & (zs < float(arm["top_z"]) - 0.03)]
    seat_near = float(zs.max()) if len(zs) else float(arm["seat_z"])
    rho = T.CLOTH_OFFSET_M + THROW_T_M
    R = max(rho, ROUND_M)
    arc = math.pi / 2.0 * R
    H = m["host"]
    edge_top = {"left": float(np.median(H[0])), "right": float(np.median(H[-1]))}
    outer, inner = ("right", "left") if s > 0 else ("left", "right")
    hem = float(m["hem_z"])
    seat_target = seat_near + SEAT_CLEAR_M
    hang = {outer: arc + max(0.0, edge_top[outer] + rho - R - hem),
            inner: arc + max(0.0, edge_top[inner] + rho - R - seat_target), "foot": 0.0}
    # the inner hang ends at the seat: the one hem level (``cover_grid``) is the outer one, the inner side stops short
    # of it at its own length; its drop is scaled to reach the seat exactly
    out_drop = max(1e-6, edge_top[outer] + rho - R - hem)
    in_drop = max(0.0, edge_top[inner] + rho - R - seat_target)
    hang[inner] = arc + min(in_drop, out_drop) * (hang[outer] - arc) / out_drop
    cover = BP.cover_grid(m["xs"], m["ys"], H, hang, hem, T.CLOTH_OFFSET_M, THROW_T_M, WRINKLE_M, side_folds=True,
                          flare=m["flare"], bed_size=(aw, tw), round_m=R)
    cover = _world_cover(cover, vhost, (xc, yc))
    key = BP.textile_key(look.get("look") or "knit")
    parts = [BP.sheet_solid(cover["grid"], cover["thickness"], key, "throw", cover["normals"])]
    if look.get("fringe"):
        for which, inward in ((outer, 0.0), (inner, -s)):
            f = _fringe(cover, host_fp, which, key, inward)
            if f is not None:
                parts.append(f)
    e = cover["edges"]
    rect = (xc + e[0], yc + e[2], xc + e[1], yc + e[3])
    cover.update(top_z=m["top_z"], share=float(np.mean(cover["on_top"])), hem_z=hem)
    return {"parts": parts, "drape": cover, "rect": rect, "how": f"folded over the {arm['side']} arm",
            "drape_kind": "arm", "side": arm["side"],
            "measure": {"arm": arm, "seat_near_z": round(seat_near, 4), "hem_z": round(hem, 4),
                        "hang_m": {k: round(v, 3) for k, v in hang.items()}, "rays": m["rays"]}}


def seat_end_throw(caster, host_fp: dict, side: str, seat_z: float, arm: Optional[dict], look: dict,
                   floor_z: float) -> Optional[dict]:
    """The folded throw across a seat's end (pure): ``THROW_W_M`` wide from the arm's inner face (or the end) inwards,
    from the back cushions over the seat to its front edge, hanging ``SEAT_DROP_M`` down the front (``textiles
    .drape_cover`` on the seat end as its host: its sides held by ``limits``, the foot free); the fringe at the hem.
    ``arm_throw``'s record, or None."""
    from wenart.blender import textiles as T

    w = float(host_fp["size"][0])
    hc, rot = host_fp["center"], float(host_fp["rotation_deg"])
    s = 1.0 if side == "right" else -1.0
    x_edge = float(arm["x_in"]) - s * 0.01 if arm else s * (w / 2.0 - 0.04)
    tw = min(THROW_W_M, w * 0.45)
    if tw < THROW_MIN_W_M:
        return None
    xc = x_edge - s * tw / 2.0
    depth = seat_depth(caster, host_fp, xc, seat_z)
    if depth is None:
        return None
    y_front, y_back = depth
    dv = y_back - y_front
    yc = (y_front + y_back) / 2.0
    vc = rest.to_world(hc, rot, xc, yc)
    vhost = {"center": [vc[0], vc[1]], "size": [tw, dv], "rotation_deg": rot}
    sides = {"left": {"free": False}, "right": {"free": False}, "foot": {"free": True}}
    limits = {"left": -tw / 2.0, "right": tw / 2.0}
    m = T.measure_cover(caster, vhost, (-dv / 2.0, dv / 2.0), floor_z, sides, limits, None, drop=SEAT_DROP_M)
    if m is None or abs(float(m["top_z"]) - float(seat_z)) > 0.08:
        return None
    rho = T.CLOTH_OFFSET_M + THROW_T_M
    R = max(rho, ROUND_M)
    arc = math.pi / 2.0 * R
    H = m["host"]
    edge_top = float(np.median(H[:, 0]))
    hem = float(m["hem_z"])
    hang = {"left": 0.0, "right": 0.0, "foot": (arc + max(0.0, edge_top + rho - R - hem)) if m["hang_free"]["foot"]
            else 0.0}
    cover = BP.cover_grid(m["xs"], m["ys"], H, hang, hem, T.CLOTH_OFFSET_M, THROW_T_M, WRINKLE_M, side_folds=True,
                          flare=m["flare"], bed_size=(tw, dv), round_m=R)
    cover = _world_cover(cover, vhost, (xc, yc))
    key = BP.textile_key(look.get("look") or "knit")
    parts = [BP.sheet_solid(cover["grid"], cover["thickness"], key, "throw", cover["normals"])]
    if look.get("fringe") and hang["foot"] > 0.0:
        f = _fringe(cover, host_fp, "foot", key)
        if f is not None:
            parts.append(f)
    e = cover["edges"]
    rect = (xc + e[0], yc + e[2], xc + e[1], yc + e[3])
    cover.update(top_z=m["top_z"], share=float(np.mean(cover["on_top"])), hem_z=hem)
    return {"parts": parts, "drape": cover, "rect": rect, "how": f"folded across the {side} seat end",
            "drape_kind": "seat_end", "side": side,
            "measure": {"seat_z": round(float(seat_z), 4), "seat_y": [round(y_front, 3), round(y_back, 3)],
                        "hem_z": round(hem, 4), "hang_m": {k: round(v, 3) for k, v in hang.items()},
                        "rays": m["rays"]}}


def preferred_side(item: dict, host_fp: dict) -> str:
    """The end a seat's throw goes to first (pure): the item's ``seat_throw.side``, else the side of its centre in the
    host frame (the decor stage's spot), else the right."""
    look = item.get("seat_throw") if isinstance(item.get("seat_throw"), dict) else {}
    if look.get("side") in ("left", "right"):
        return look["side"]
    if item.get("center"):
        lx, _ly = rest.to_local(host_fp["center"], float(host_fp["rotation_deg"]), float(item["center"][0]),
                                float(item["center"][1]))
        if abs(lx) > 0.05:
            return "right" if lx > 0 else "left"
    return "right"


def candidates(caster, host_fp: dict, item: dict, floor_z: float) -> Iterator[dict]:
    """The drapes of a seat's throw in order (pure; lazily): over the preferred end's arm, over the other arm, across
    the preferred seat end, across the other; each ``arm_throw`` / ``seat_end_throw``'s record plus ``weave`` (what was
    built). Nothing when no seat is found."""
    look = item.get("seat_throw") if isinstance(item.get("seat_throw"), dict) else {}
    seat = measure_seat(caster, host_fp)
    if seat is None:
        return
    first = preferred_side(item, host_fp)
    order = (first, "left" if first == "right" else "right")
    arms = {s: measure_arm(caster, host_fp, s, seat) for s in order}
    tried = []
    for kind in (look.get("drape"), *DRAPES):
        if kind not in DRAPES or kind in tried:
            continue
        tried.append(kind)
        for side in order:
            got = arm_throw(caster, host_fp, arms[side], look, floor_z) if kind == "arm" and arms[side] else \
                seat_end_throw(caster, host_fp, side, seat, arms[side], look, floor_z) if kind == "seat_end" else None
            if got is None:
                continue
            got["weave"] = {"look": look.get("look") or "knit", "fringe": bool(look.get("fringe")),
                            "drape": got["drape_kind"], "side": side, "colour": look.get("colour"),
                            "fringe_strands": int(sum(int(p.get("strands") or 0) for p in got["parts"])),
                            "rule": RULE, "how": got["how"]}
            yield got
