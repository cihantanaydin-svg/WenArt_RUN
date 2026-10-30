"""Small objects as real products (30 Oct 2026; user on real04 run 20261030-112241-full: "Better toilet paper roll model
is needed" (UL183: a white cylinder on a chrome arm), "More detailed models would be nice here" / "Better models with
more details is needed" (UL184: the vanity's dried stems read as lollipops, the jar's cotton as pebbles), "Better quality
models with more details needed for the little items fruit ball etc" (UL186: a white bowl of smooth balls, a plain
utensil pot, plain bottles, a plain pot on the hob)). Pure (no ``bpy``): vertex and face lists in the item's own frame
(bottom on z = 0, front -Y, centred), the parts of ``parametric`` (``verts``, ``faces``, ``key``, ``role``).

Every product has the details its real counterpart shows at a close view (designer sizes of real products, assumed):

- fruit (``apple``, ``orange``, ``pear``, ``lemon``, ``banana_bunch``): turned or lofted with their own shapes (an
  apple's stalk dimple and stalk, an orange's navel, a pear's neck, a lemon's pointed ends lying on its side, a bunch of
  five-sided curved bananas joined at a crown), in waxy fruit colours (``FRUIT_KEYS``);
- ``fruit_bowl``: a turned bowl with a foot ring, a wall with its thickness and a rounded rim, its fruit resting in it;
- ``utensil_crock``: a stoneware crock with its wall and rim, a wooden spoon, a spatula, a ladle and a balloon whisk;
- ``chopping_board``: a rounded board with its hanging hole cut through;
- ``oil_set``: oil and vinegar bottles of glass with their thickness, the oil inside (``oil``), a steel pourer and a
  cork, a lidded salt pot, on a small board with a rounded edge;
- ``cookware``: a pot with a rolled rim, two loop handles and a glass lid with a steel rim and knob, a pan with a sloped
  wall and a long riveted handle;
- ``paper_holder``: a wall rose, a bent arm with an end cap and a cover flap in the room's fixture finish, a roll with a
  cardboard core showing at its ends and soft edges, its sheet hanging over the front with a torn, perforated edge;
- ``stems_vase``: a turned ceramic vase (a foot, a belly, a neck and a lip, open) with dried pampas: thin stems with
  feathery plumes of fine wisps, never a ball on a stick;
- ``tray``: a small rounded tray with a raised lip (a vanity's soap and jar stand on it).

Turned parts use ``LATHE_N`` segments and are shaded smooth; every closed part is wound outwards (``outward``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import parametric as P
from wenart.blender import print_labels as PL

Part = dict
LESSONS: tuple[str, ...] = ("UL183", "UL184", "UL186")
LATHE_N = 16
# The fruit colours (material keys; vocabulary slugs ``fruit_*``: waxy, slightly glossy skins)
FRUIT_KEYS: dict[str, str] = {"red": "fruit_red", "orange": "fruit_orange", "yellow": "fruit_yellow",
                              "green": "fruit_green"}
OIL_KEY = "oil"                   # the oil in a bottle (vocabulary ``oil_amber``: a clear golden liquid)
CARDBOARD_KEY = "cardboard"       # a paper roll's core (vocabulary ``cardboard``)
PAPER_ROLL_KEY = "bedding"        # the tissue: the white cotton key (a soft matte white)
GLASS_M = 0.0025                  # a bottle's or a jar's wall
ROLL = {"r_m": 0.055, "core_r_m": 0.021, "core_t_m": 0.0015, "length_m": 0.10, "edge_m": 0.005,
        "tail_m": 0.045, "tear_m": 0.003, "teeth": 9, "sheet_t_m": 0.0008}
PLUME = {"wisps": 6, "length_m": 0.10, "spread": 0.16, "wisp_r_m": 0.0018}


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def signed_volume(part: Part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def outward(part: Part) -> Part:
    """The part with its faces wound outwards (a closed mesh whose signed volume is negative is turned over)."""
    if signed_volume(part) < 0.0:
        part["faces"] = [list(reversed(f)) for f in part["faces"]]
    return part


def _map(verts, axis: str, c) -> list[tuple[float, float, float]]:
    """Turned vertices about the local z axis moved onto ``axis`` (``z``, ``x``: along +X, ``-y``: out of a wall at +Y
    towards -Y) through ``c``; the maps are rotations (the winding stays outwards)."""
    cx, cy, cz = c
    if axis == "x":
        return [(cx + z, cy + x, cz + y) for x, y, z in verts]
    if axis == "-y":
        return [(cx + x, cy - z, cz + y) for x, y, z in verts]
    return [(cx + x, cy + y, cz + z) for x, y, z in verts]


def turned(profile: Sequence[tuple[float, float]], key: str, role: str, c=(0.0, 0.0, 0.0), axis: str = "z",
           n: int = LATHE_N, loop: bool = False, close_start: bool = True, close_end: bool = True,
           smooth: bool = True) -> Part:
    """A solid turned from the rings ``(r, t)`` of ``profile`` (``t`` along the axis from ``c``); ``loop``: the
    profile is a closed loop (a ring, a roll), the last ring joined to the first, no caps."""
    verts = []
    for r, t in profile:
        r = max(float(r), 1e-4)
        verts += [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), float(t)) for i in range(n)]
    m = len(profile)
    faces = []
    for k in range(m if loop else m - 1):
        a, b = k * n, ((k + 1) % m) * n
        faces += [[a + i, a + (i + 1) % n, b + (i + 1) % n, b + i] for i in range(n)]
    if not loop:
        if close_start:
            faces.append(list(range(n - 1, -1, -1)))
        if close_end:
            faces.append([(m - 1) * n + i for i in range(n)])
    return outward({"verts": _map(verts, axis, c), "faces": faces, "key": key, "role": role, "smooth": smooth})


def _frame(t):
    """Two unit vectors normal to the unit direction ``t``."""
    up = (0.0, 0.0, 1.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
    e1 = (t[1] * up[2] - t[2] * up[1], t[2] * up[0] - t[0] * up[2], t[0] * up[1] - t[1] * up[0])
    m = math.sqrt(sum(c * c for c in e1)) or 1e-9
    e1 = tuple(c / m for c in e1)
    e2 = (t[1] * e1[2] - t[2] * e1[1], t[2] * e1[0] - t[0] * e1[2], t[0] * e1[1] - t[1] * e1[0])
    return e1, e2


def tube(points: Sequence[Sequence[float]], radii, key: str, role: str, sides: int = 6, smooth: bool = True,
         squash: float = 1.0) -> Part:
    """A closed tube along the 3D polyline ``points`` (a handle, a wire, a stem, a banana), ``radii`` one per point
    (or one value), ``sides`` round it; ``squash`` flattens it along its second frame vector."""
    pts = [tuple(float(v) for v in p) for p in points]
    rs = list(radii) if isinstance(radii, (list, tuple)) else [float(radii)] * len(pts)
    verts = []
    for k, p in enumerate(pts):
        a = pts[max(0, k - 1)]
        b = pts[min(len(pts) - 1, k + 1)]
        d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ln = math.sqrt(sum(c * c for c in d)) or 1e-9
        e1, e2 = _frame(tuple(c / ln for c in d))
        r = max(float(rs[k]), 1e-4)
        for i in range(sides):
            ang = 2 * math.pi * i / sides
            ca, sa = math.cos(ang) * r, math.sin(ang) * r * squash
            verts.append((p[0] + e1[0] * ca + e2[0] * sa, p[1] + e1[1] * ca + e2[1] * sa, p[2] + e1[2] * ca + e2[2] * sa))
    faces = []
    for k in range(len(pts) - 1):
        a, b = k * sides, (k + 1) * sides
        faces += [[a + i, a + (i + 1) % sides, b + (i + 1) % sides, b + i] for i in range(sides)]
    faces.append(list(range(sides - 1, -1, -1)))
    faces.append([(len(pts) - 1) * sides + i for i in range(sides)])
    return outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": smooth})


def slab(outline: Sequence[tuple[float, float]], z0: float, t: float, key: str, role: str,
         hole: Optional[Sequence[tuple[float, float]]] = None) -> Part:
    """A flat plate of thickness ``t`` from ``z0`` with the ``outline`` (counter-clockwise); with ``hole`` (a loop of as
    many points, each paired with the outline point at its angle) the plate is cut through."""
    n = len(outline)
    if hole is None:
        verts = [(x, y, z0) for x, y in outline] + [(x, y, z0 + t) for x, y in outline]
        faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
        faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    else:
        verts = ([(x, y, z0) for x, y in outline] + [(x, y, z0 + t) for x, y in outline]
                 + [(x, y, z0) for x, y in hole] + [(x, y, z0 + t) for x, y in hole])
        o0, o1, h0, h1 = 0, n, 2 * n, 3 * n
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces.append([o1 + i, o1 + j, h1 + j, h1 + i])           # the top
            faces.append([o0 + j, o0 + i, h0 + i, h0 + j])           # the bottom
            faces.append([o0 + i, o0 + j, o1 + j, o1 + i])           # the outer edge
            faces.append([h0 + j, h0 + i, h1 + i, h1 + j])           # the hole's edge
    return outward({"verts": verts, "faces": faces, "key": key, "role": role})


def rounded_rect(a: float, b: float, rc: float, n: int = 4) -> list[tuple[float, float]]:
    """A rounded rectangle of half sizes ``a`` x ``b`` and corner radius ``rc`` (counter-clockwise)."""
    rc = max(0.0005, min(rc, a, b))
    pts = []
    for qx, qy, start in ((a - rc, b - rc, 0.0), (-a + rc, b - rc, 90.0), (-a + rc, -b + rc, 180.0),
                          (a - rc, -b + rc, 270.0)):
        for k in range(n + 1):
            t = math.radians(start + 90.0 * k / n)
            pts.append((qx + rc * math.cos(t), qy + rc * math.sin(t)))
    return pts


def _hash(*v: int) -> int:
    h = 2166136261
    for x in v:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _vessel(rings_out: Sequence[tuple[float, float]], wall: float, floor: float, key: str, role: str,
            c=(0.0, 0.0, 0.0), n: int = LATHE_N) -> Part:
    """An open turned vessel: the outer profile ``rings_out`` from its foot up to its rim, over a rounded lip and down
    its inside (``wall`` thick) to a floor ``floor`` over the bottom."""
    top_r, top_z = rings_out[-1]
    prof = list(rings_out) + [(top_r - wall * 0.5, top_z + wall * 0.35)]
    # the inside follows the outside down to the floor; the rings under the floor are left out (no folded faces)
    inner = [(max(r - wall, 0.002), z) for r, z in reversed(rings_out[1:]) if z > floor + 1e-6]
    r_floor = max(rings_out[0][0] - wall, 0.002) if not inner else inner[-1][0]
    prof += inner + [(r_floor, floor), (max(r_floor * 0.6, 0.002), floor)]
    return turned(prof, key, role, c=c, n=n)


# --------------------------------------------------------------------------
# fruit (UL186)
# --------------------------------------------------------------------------

def apple(cx: float, cy: float, z0: float, dia: float, key: str = "fruit_red", seed: int = 0) -> list[Part]:
    """An apple ``dia`` across resting at ``z0``: its body with the dimples at the stalk and the calyx, a short
    stalk leaning a little."""
    R, H = dia / 2.0, dia * 0.88
    prof = [(0.10 * R, 0.07 * H), (0.32 * R, 0.015 * H), (0.62 * R, 0.0), (0.88 * R, 0.10 * H), (1.0 * R, 0.36 * H),
            (0.99 * R, 0.58 * H), (0.90 * R, 0.80 * H), (0.70 * R, 0.95 * H), (0.42 * R, 1.0 * H),
            (0.20 * R, 0.95 * H), (0.08 * R, 0.86 * H)]
    parts = [turned(prof, key, "fruit", c=(cx, cy, z0))]
    lean = 0.25 * (1 if seed % 2 else -1)
    top = z0 + 0.86 * H
    parts.append(tube([(cx, cy, top - 0.004), (cx + lean * 0.004, cy, top + 0.010), (cx + lean * 0.010, cy,
                                                                                         top + 0.018)],
                      [0.0018, 0.0015, 0.0012], "wood", "stalk", sides=5))
    return parts


def orange(cx: float, cy: float, z0: float, dia: float, key: str = "fruit_orange") -> list[Part]:
    """An orange a little flattened at its poles, its navel a small dimple on top."""
    R, H = dia / 2.0, dia * 0.94
    prof = [(0.12 * R, 0.02 * H), (0.55 * R, 0.0), (0.86 * R, 0.10 * H), (1.0 * R, 0.33 * H), (1.0 * R, 0.62 * H),
            (0.88 * R, 0.86 * H), (0.55 * R, 0.99 * H), (0.16 * R, 1.0 * H), (0.05 * R, 0.975 * H)]
    return [turned(prof, key, "fruit", c=(cx, cy, z0))]


def pear(cx: float, cy: float, z0: float, dia: float, key: str = "fruit_green") -> list[Part]:
    """A pear: its broad base, the waist and the neck to the stalk."""
    R, H = dia / 2.0, dia * 1.45
    prof = [(0.10 * R, 0.04 * H), (0.55 * R, 0.0), (0.90 * R, 0.08 * H), (1.0 * R, 0.24 * H), (0.92 * R, 0.42 * H),
            (0.68 * R, 0.60 * H), (0.50 * R, 0.76 * H), (0.40 * R, 0.90 * H), (0.22 * R, 0.99 * H),
            (0.06 * R, 0.985 * H)]
    parts = [turned(prof, key, "fruit", c=(cx, cy, z0))]
    top = z0 + 0.98 * H
    parts.append(tube([(cx, cy, top - 0.003), (cx + 0.003, cy, top + 0.014), (cx + 0.008, cy, top + 0.022)],
                      [0.0018, 0.0015, 0.0012], "wood", "stalk", sides=5))
    return parts


def lemon(cx: float, cy: float, z0: float, length: float, key: str = "fruit_yellow", along: str = "x") -> list[Part]:
    """A lemon lying on its side along X: an oval with a pointed tip at each end."""
    R = length * 0.33
    prof = [(0.02 * R, 0.0), (0.18 * R, 0.035 * length), (0.62 * R, 0.16 * length), (0.92 * R, 0.33 * length),
            (1.0 * R, 0.50 * length), (0.92 * R, 0.67 * length), (0.62 * R, 0.84 * length),
            (0.18 * R, 0.965 * length), (0.02 * R, length)]
    return [turned(prof, key, "fruit", c=(cx - length / 2.0, cy, z0 + R), axis="x")]


def banana_bunch(cx: float, cy: float, z0: float, length: float, fingers: int = 3,
                 key: str = "fruit_yellow") -> list[Part]:
    """A bunch of ``fingers`` bananas side by side, each a five-sided curved finger tapering to its tip, joined at
    a dark crown at one end; lying with its curve rising at both ends (on a pile of fruit)."""
    parts = []
    r = length * 0.085
    crown = (cx - length * 0.45, cy, z0 + r * 2.4)
    for k in range(fingers):
        off = (k - (fingers - 1) / 2.0) * r * 1.9
        pts, rs = [], []
        for j in range(8):
            t = j / 7.0
            x = cx - length * 0.42 + length * 0.86 * t
            z = z0 + r + length * 0.22 * (2.0 * t - 1.0) ** 2 * 0.5 + (r * 1.2 if j == 0 else 0.0)
            pts.append((x, cy + off * (0.35 + 0.65 * math.sin(math.pi * min(t * 1.6, 1.0) / 2.0)), z))
            rs.append(r * (0.45 if j == 0 else 1.0 if t < 0.75 else 1.0 - (t - 0.75) * 2.6))
        parts.append(tube(pts, rs, key, "fruit", sides=5))
        parts.append(tube([pts[-1], (pts[-1][0] + 0.006, pts[-1][1], pts[-1][2] + 0.002)], [r * 0.32, r * 0.25],
                          "dark", "tip", sides=5))
    parts.append(tube([(crown[0] - 0.012, cy, crown[2] + 0.004), crown, (crown[0] + 0.02, cy, crown[2] - r)],
                      [r * 0.55, r * 0.6, r * 0.5], "wood", "crown", sides=6))
    return parts


def fruit_bowl(w: float, d: float, h: float) -> list[Part]:
    """A turned bowl (foot ring, curved wall, rounded rim) in the box ``w x d x h`` (bottom on z = 0) with its fruit
    resting in it: apples, oranges, a pear and lemons, a banana bunch over them in a bowl at least 26 cm across."""
    R = min(w, d) / 2.0
    hb = min(h * 0.55, R * 0.48, 0.075)
    foot = R * 0.42
    out = [(foot, 0.0), (foot, hb * 0.10), (foot * 1.12, hb * 0.16), (R * 0.70, hb * 0.40), (R * 0.90, hb * 0.72),
           (R * 0.985, hb)]
    floor = hb * 0.20
    parts = [_vessel(out, 0.006, floor, "ceramic", "bowl", n=32)]
    room = h - floor
    dia = max(0.03, min(0.072, R * 0.46, room * 0.95))

    def bottom_at(rho: float) -> float:              # the bowl's inside at a radius (its floor, rising to the rim)
        s = min(1.0, rho / max(R * 0.95, 1e-6))
        return floor + (hb - floor) * s * s * 0.85

    # five fruit in a ring round a lemon lying in the middle, each clear of the others; a banana bunch over them only
    # where the box leaves room over the fruit
    dia = max(0.03, min(0.068, R * 0.46, room * 0.95))
    rr = max(R * 0.50, dia * 0.88)
    ring = (("apple", "fruit_red"), ("orange", "fruit_orange"), ("pear", "fruit_green"), ("apple", "fruit_green"),
            ("orange", "fruit_orange"))
    tops = []
    for k, (kind, key) in enumerate(ring):
        a = math.radians(-72.0 + 72.0 * k)
        x, y = rr * math.cos(a), rr * math.sin(a)
        z = bottom_at(rr + dia * 0.25)
        size = dia * (0.94 + 0.03 * (k % 3))
        if kind == "pear" and z + size * 0.95 * 1.45 + 0.022 > h:
            kind, key = "apple", "fruit_green"
        if kind == "apple":
            parts += apple(x, y, z, size, key, seed=k)
            tops.append(z + size * 0.88 + 0.018)
        elif kind == "orange":
            parts += orange(x, y, z, size, key)
            tops.append(z + size * 0.94)
        else:
            parts += pear(x, y, z, size * 0.95, key)
            tops.append(z + size * 0.95 * 1.45 + 0.022)
    ln = min(dia * 1.15, (rr - dia * 0.5) * 2.0 + dia * 0.4)
    parts += lemon(0.0, 0.0, bottom_at(0.0) + 0.002, ln, "fruit_yellow")
    blen = min(R * 1.4, 0.19)
    if R >= 0.13 and max(tops) + blen * 0.085 * 2.0 + blen * 0.11 <= h:
        parts += banana_bunch(0.0, -R * 0.05, max(tops) - blen * 0.04, blen)
    return _fit(parts, w, d, h)


# --------------------------------------------------------------------------
# kitchen tools and vessels (UL186)
# --------------------------------------------------------------------------

def wooden_spoon(p0, p1, bowl_len: float = 0.06, key: str = "wood") -> list[Part]:
    """A wooden spoon from its handle's end ``p0`` up to its bowl's tip ``p1``: a round handle and an oval bowl."""
    d = [p1[i] - p0[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in d)) or 1e-9
    u = [c / ln for c in d]
    neck = [p1[i] - u[i] * bowl_len for i in range(3)]
    parts = [tube([p0, neck], [0.0055, 0.0045], key, "tool", sides=6)]
    mid = [p1[i] - u[i] * bowl_len * 0.5 for i in range(3)]
    pts = [neck, mid, p1]
    parts.append(tube(pts, [0.008, 0.021, 0.006], key, "tool", sides=8, squash=0.35))
    return parts


def spatula(p0, p1, key: str = "wood") -> list[Part]:
    """A wooden spatula: a round handle and a flat, slightly wider blade with a squared end."""
    d = [p1[i] - p0[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in d)) or 1e-9
    u = [c / ln for c in d]
    neck = [p1[i] - u[i] * 0.075 for i in range(3)]
    return [tube([p0, neck], [0.0055, 0.0048], key, "tool", sides=6),
            tube([neck, [p1[i] - u[i] * 0.004 for i in range(3)], p1], [0.012, 0.026, 0.025], key, "tool", sides=4,
                 squash=0.18)]


def ladle(p0, p1, key: str = "steel") -> list[Part]:
    """A steel ladle hanging bowl-up in a crock: its handle and a deep round bowl at the top end."""
    parts = [tube([p0, p1], [0.004, 0.0035], key, "tool", sides=6)]
    parts.append(turned([(0.002, 0.0), (0.020, 0.004), (0.031, 0.016), (0.033, 0.030), (0.030, 0.031),
                         (0.028, 0.017), (0.018, 0.007), (0.002, 0.005)], key, "tool",
                        c=(p1[0], p1[1], p1[2] - 0.012), n=12))
    return parts


def whisk(p0, p1, key: str = "steel") -> list[Part]:
    """A balloon whisk: a round handle and six wire loops bulging out over the top."""
    parts = [tube([p0, [p0[i] + (p1[i] - p0[i]) * 0.45 for i in range(3)]], [0.0065, 0.0058], key, "tool",
                  sides=8)]
    base = [p0[i] + (p1[i] - p0[i]) * 0.45 for i in range(3)]
    d = [p1[i] - base[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in d)) or 1e-9
    u = tuple(c / ln for c in d)
    e1, e2 = _frame(u)
    for k in range(3):                               # three wires, each a loop through the top: six arcs
        a = math.pi * k / 3.0
        ex = [math.cos(a) * e1[i] + math.sin(a) * e2[i] for i in range(3)]
        pts = []
        for j in range(9):
            s = -1.0 + 2.0 * j / 8.0                 # one side, over the top, down the other
            t = 1.0 - s * s                          # along the axis: 0 at the ends, 1 at the top
            bulge = 0.032 * math.sin(math.pi * (0.5 + 0.5 * s)) * (0.35 + 0.65 * t) * (1 if s >= 0 else -1)
            along = ln * (0.1 + 0.9 * math.sqrt(max(t, 0.0)))
            pts.append([base[i] + u[i] * along + ex[i] * (bulge if abs(s) < 1.0 else 0.004 * (1 if s > 0 else -1))
                        for i in range(3)])
        parts.append(tube(pts, 0.0011, key, "wire", sides=4, smooth=False))
    return parts


def utensil_crock(w: float, d: float, h: float, key: str = "ceramic") -> list[Part]:
    """A stoneware crock (its wall, a rolled rim) with a wooden spoon, a spatula, a steel ladle and a balloon whisk
    leaning out of it, in the box ``w x d x h``."""
    r = min(w, d) / 2.0 * 0.86
    ch = min(h * 0.55, 0.17)
    out = [(r * 0.88, 0.0), (r * 0.95, 0.006), (r, ch * 0.12), (r * 0.97, ch * 0.80), (r * 1.0, ch * 0.96),
           (r * 1.02, ch)]
    parts = [_vessel(out, 0.007, 0.010, key, "pot", n=28)]
    top = h - 0.004
    lean = r * 0.55
    tools = ((-1.0, 0.25, "spoon"), (0.9, -0.35, "spatula"), (0.15, 0.95, "whisk"), (-0.35, -0.9, "ladle"))
    for k, (sx, sy, kind) in enumerate(tools):
        p0 = (sx * r * 0.25, sy * r * 0.25, 0.02)
        p1 = (sx * lean, sy * lean, top - 0.012 * k)
        if kind == "spoon":
            parts += wooden_spoon(p0, p1)
        elif kind == "spatula":
            parts += spatula(p0, p1)
        elif kind == "whisk":
            parts += whisk(p0, p1)
        else:
            parts += ladle(p0, (p1[0], p1[1], p1[2] - 0.03))
    return _fit(parts, w, d, h)


def chopping_board(w: float, d: float, h: float, key: str = "wood") -> list[Part]:
    """A wooden board with rounded corners and its hanging hole cut through near one end."""
    a, b = w / 2.0, d / 2.0
    n = 40
    hr = min(0.012, b * 0.3)
    hx = a - max(0.03, hr * 2.6)
    outline, hole = [], []
    p = 8.0                                          # a superellipse: a rectangle with rounded corners
    for i in range(n):
        t = 2 * math.pi * i / n
        dx, dy = math.cos(t), math.sin(t)
        lo, hi = 0.0, 2.0 * (a + b)                  # the ray from the hole's centre to the board's edge
        for _ in range(40):
            m = (lo + hi) / 2.0
            x, y = hx + dx * m, dy * m
            if abs(x / a) ** p + abs(y / b) ** p <= 1.0:
                lo = m
            else:
                hi = m
        outline.append((hx + dx * lo, dy * lo))
        hole.append((hx + dx * hr, dy * hr))
    return [slab(outline, 0.0, h, key, "board", hole=hole)]


def glass_bottle(cx: float, cy: float, z0: float, r: float, hgt: float, fill_key: Optional[str], fill: float = 0.7,
                 key: str = "glass") -> list[Part]:
    """A glass bottle (``r`` radius, ``hgt`` to its lip) with its wall and the liquid inside to ``fill`` of its body:
    a round body, sloping shoulders, a long neck and a lip."""
    body = hgt * 0.60
    out = [(r * 0.92, 0.0), (r, 0.006), (r, body), (r * 0.80, body + hgt * 0.07), (r * 0.42, body + hgt * 0.14),
           (r * 0.30, body + hgt * 0.19), (r * 0.30, hgt * 0.95), (r * 0.36, hgt * 0.965), (r * 0.36, hgt)]
    parts = [_vessel(out, GLASS_M, 0.005, key, "bottle", c=(cx, cy, z0))]
    if fill_key:
        lv = body * fill
        parts.append(turned([(r - GLASS_M - 0.001, 0.0), (r - GLASS_M - 0.0005, lv - 0.002),
                             (r - GLASS_M - 0.002, lv)], fill_key, "contents", c=(cx, cy, z0 + 0.0055)))
    return parts


def pourer(cx: float, cy: float, z0: float, r: float) -> list[Part]:
    """A bottle's steel pourer: a rubber stopper in the neck and a thin spout angled up and out."""
    return [turned([(r * 0.95, 0.0), (r * 1.05, 0.004), (r * 1.05, 0.014), (r * 0.6, 0.016)], "dark", "stopper",
                   c=(cx, cy, z0 - 0.006)),
            tube([(cx, cy, z0 + 0.012), (cx, cy - 0.006, z0 + 0.030), (cx, cy - 0.018, z0 + 0.046)],
                 [0.0035, 0.003, 0.0025], "steel", "spout", sides=8)]


def cork(cx: float, cy: float, z0: float, r: float) -> list[Part]:
    """A cork stopper standing a little out of the neck, its top rounded."""
    return [turned([(r * 0.92, 0.0), (r * 1.08, 0.012), (r * 1.10, 0.020), (r * 0.9, 0.024), (r * 0.3, 0.025)],
                   "wood", "cork", c=(cx, cy, z0 - 0.010))]


def oil_set(w: float, d: float, h: float) -> list[Part]:
    """Oil and vinegar bottles (glass with the liquid in it, a pourer and a cork) and a lidded salt pot on a small
    board with a rounded edge, in the box ``w x d x h``."""
    bt = 0.015
    parts = [_round_slab(w / 2.0, d / 2.0, 0.0, bt, "wood", "tray", rc=0.012)]
    z = bt
    br = min(d / 2.0 - 0.012, 0.03, w / 7.0)
    room = h - z
    tall = room - 0.05
    xa = -w / 2.0 + br + 0.01
    parts += glass_bottle(xa, 0.0, z, br, tall, OIL_KEY, 0.72)
    parts += pourer(xa, 0.0, z + tall, br * 0.36)
    # 30 Oct 2026 (UL199, user: "Also wine vineger salt paper you can write them when you see needed"): their printed
    # paper labels (print_labels: invented, brand-free words)
    parts.append(PL.bottle_label(xa, 0.0, z, br, tall * 0.16, tall * 0.44, "olive_oil"))
    xb = xa + 2 * br + 0.012
    short = tall * 0.84
    parts += glass_bottle(xb, 0.0, z, br * 0.9, short, "dark", 0.6)
    parts += cork(xb, 0.0, z + short, br * 0.9 * 0.36)
    parts.append(PL.bottle_label(xb, 0.0, z, br * 0.9, short * 0.16, short * 0.44, "vinegar"))
    sr = min(0.032, d / 2.0 - 0.01, (w / 2.0 - (xb + br * 0.9) - 0.01) / 2.0)
    if sr >= 0.018:
        sx = w / 2.0 - sr - 0.006
        ph = min(0.075, room - 0.02)
        parts.append(_vessel([(sr * 0.85, 0.0), (sr * 0.95, 0.004), (sr, 0.012), (sr, ph * 0.85)], 0.004, 0.006,
                             "ceramic", "salt", c=(sx, 0.0, z)))
        parts.append(turned([(sr + 0.002, 0.0), (sr + 0.002, 0.008), (sr * 0.85, 0.012), (0.006, 0.014)], "wood",
                            "lid", c=(sx, 0.0, z + ph * 0.85 - 0.002)))
        parts.append(turned([(0.004, 0.0), (0.008, 0.004), (0.007, 0.010), (0.002, 0.012)], "wood", "knob",
                            c=(sx, 0.0, z + ph * 0.85 + 0.010), n=10))
        parts.append(PL.bottle_label(sx, 0.0, z, sr, ph * 0.22, ph * 0.22 + min(ph * 0.5, sr * 1.6), "salt"))
    return _fit(parts, w, d, h)


WINE = {"r_m": 0.037, "h_m": 0.30}


def wine_bottle(cx: float, cy: float, z0: float, r: float = WINE["r_m"], hgt: float = WINE["h_m"],
                label: str = "wine_1") -> list[Part]:
    """30 Oct 2026 (UL199): a wine bottle: dark glass with the wine in it, a foil capsule over its neck and a printed
    front label (``print_labels.WINE_LABELS``: an invented winery, a vintage year, the wine's kind)."""
    parts = glass_bottle(cx, cy, z0, r, hgt, "dark", 0.85, key="glass")
    neck = r * 0.36
    parts.append(turned([(neck + 0.0008, 0.0), (neck + 0.0008, hgt * 0.13), (neck * 0.9, hgt * 0.135),
                         (0.002, hgt * 0.137)], "dark", "capsule", c=(cx, cy, z0 + hgt * 0.87)))
    body = hgt * 0.60
    parts.append(PL.bottle_label(cx, cy, z0, r, body * 0.30, body * 0.30 + min(body * 0.6, r * 1.9), label))
    return parts


def cookware(w: float, d: float, h: float) -> list[Part]:
    """A pot with a rolled rim, two loop handles and a glass lid (steel rim, knob) and a pan with a sloped wall and a
    long riveted handle, side by side in the box ``w x d x h`` (on the hob)."""
    pot_r = min(d / 2.0 - 0.015, w * 0.19)
    pot_x = -w / 2.0 + pot_r + 0.025
    ph = min(h - 0.035, 0.14)
    parts = [_vessel([(pot_r * 0.96, 0.0), (pot_r, 0.008), (pot_r, ph - 0.006), (pot_r + 0.002, ph)], 0.0025, 0.004,
                     "steel", "pot", c=(pot_x, 0.0, 0.0), n=24)]
    parts.append(turned([(pot_r + 0.004, 0.0), (pot_r + 0.004, 0.004), (pot_r * 0.6, 0.016), (0.012, 0.022)],
                        "glass", "lid", c=(pot_x, 0.0, ph - 0.002), n=24))
    parts.append(turned([(pot_r + 0.005, 0.0), (pot_r + 0.005, 0.005), (pot_r - 0.001, 0.005), (pot_r - 0.001, 0.0)],
                        "steel", "lid_rim", c=(pot_x, 0.0, ph - 0.003), n=24, loop=True))
    parts.append(turned([(0.010, 0.0), (0.016, 0.006), (0.016, 0.014), (0.010, 0.020), (0.003, 0.021)], "dark",
                        "knob", c=(pot_x, 0.0, ph + 0.018), n=12))
    for sx in (-1.0, 1.0):                            # loop handles riveted to the pot's sides
        x0 = pot_x + sx * pot_r
        zc = ph * 0.80
        parts.append(tube([(x0 - sx * 0.002, -0.022, zc), (x0 + sx * 0.016, -0.018, zc + 0.004),
                           (x0 + sx * 0.022, 0.0, zc + 0.006), (x0 + sx * 0.016, 0.018, zc + 0.004),
                           (x0 - sx * 0.002, 0.022, zc)], 0.004, "steel", "handle", sides=6))
    handle = 0.10
    pan_r = min(d / 2.0 - 0.01, (w - 2.0 * pot_r - 0.06 - handle) / 2.0, 0.13)
    pan_x = pot_x + pot_r + 0.035 + pan_r
    handle = max(0.04, min(handle, w / 2.0 - (pan_x + pan_r)))
    if pan_r >= 0.05:
        parts.append(_vessel([(pan_r * 0.80, 0.0), (pan_r * 0.84, 0.004), (pan_r * 0.93, 0.025), (pan_r, 0.045)],
                             0.003, 0.004, "dark", "pan", c=(pan_x, 0.0, 0.0), n=28))
        x0 = pan_x + pan_r - 0.004
        parts.append(tube([(x0, 0.0, 0.036), (x0 + handle * 0.35, 0.0, 0.045), (x0 + handle, 0.0, 0.055)],
                          [0.007, 0.008, 0.009], "steel", "handle", sides=8, squash=0.6))
        for sy in (-1.0, 1.0):
            parts.append(P._cylinder_x(x0 - 0.003, sy * 0.008, 0.038, 0.0025, 0.0025, 0.004, "steel", "rivet", n=8))
    return _fit(parts, w, d, h)


# --------------------------------------------------------------------------
# the bathroom (UL183, UL184)
# --------------------------------------------------------------------------

def roll_radius(d: float, h: float) -> float:
    """A paper roll's radius in a holder's box (``ROLL``; a shallow box takes a smaller roll)."""
    return min(ROLL["r_m"], (d - 0.03) / 2.0, h * 0.42)


def paper_roll_z(w: float, d: float, h: float) -> float:
    """The height of a paper roll's axis over its holder box's bottom (the roll near the top, its sheet below)."""
    return h - roll_radius(d, h) - 0.012


def paper_holder_height(d: float) -> float:
    """The height of a holder's box that holds its roll and the sheet ``ROLL["tail_m"]`` under it."""
    return round(2.0 * min(ROLL["r_m"], (d - 0.03) / 2.0) + 0.012 + ROLL["tail_m"], 4)


def paper_holder(w: float, d: float, h: float, finish: str = "colour_steel") -> list[Part]:
    """A toilet roll holder in its box ``w x d x h`` (the wall at +Y, front -Y, bottom z = 0): a wall rose, an arm out
    of the wall bent along it with an end cap, a cover flap over the roll, all in ``finish``; the roll near the box's
    top with a cardboard core showing at its ends and soft edges, its sheet hanging over the front down to the box's
    bottom with a torn, perforated edge."""
    back = d / 2.0
    R = roll_radius(d, h)
    L = min(ROLL["length_m"], w - 0.05)
    zc = paper_roll_z(w, d, h)
    ry = back - 0.014 - R
    x_ros = -w / 2.0 + 0.026
    parts = [turned([(0.0005, 0.0), (0.024, 0.0), (0.025, 0.002), (0.025, 0.006), (0.021, 0.010), (0.0005, 0.010)],
                    finish, "rosette", c=(x_ros, back, zc), axis="-y", n=20)]
    x0 = x_ros + 0.012
    parts.append(tube([(x_ros, back - 0.009, zc), (x_ros, ry + 0.012, zc), (x_ros + 0.004, ry + 0.002, zc),
                       (x_ros + 0.014, ry, zc), (x0 + L + 0.012, ry, zc)], 0.0055, finish, "arm", sides=10))
    parts.append(turned([(0.0005, 0.0), (0.0065, 0.0), (0.007, 0.003), (0.006, 0.006), (0.0005, 0.007)], finish,
                        "cap", c=(x0 + L + 0.010, ry, zc), axis="x", n=12))
    # the cover flap: a curved plate over the roll's top, from the rose along the roll
    fr = R + 0.008
    arc = []
    for k in range(9):
        t = math.radians(40.0 + 100.0 * k / 8.0)
        arc.append((math.cos(t), math.sin(t)))
    outer = [(ry + fr * c, zc + fr * s) for c, s in arc]
    inner = [(ry + (fr - 0.0015) * c, zc + (fr - 0.0015) * s) for c, s in arc]
    loop = outer + list(reversed(inner))
    xs0, xs1 = x_ros + 0.006, x0 + L * 0.85
    verts = [(xs0, y, z) for y, z in loop] + [(xs1, y, z) for y, z in loop]
    m = len(loop)
    faces = [list(range(m)), [m + i for i in reversed(range(m))]] + \
        [[i, m + i, m + (i + 1) % m, (i + 1) % m] for i in range(m)]
    parts.append(outward({"verts": verts, "faces": faces, "key": finish, "role": "flap"}))
    # the roll: tissue round a cardboard core, its edges soft
    e, rc, ct = ROLL["edge_m"], ROLL["core_r_m"], ROLL["core_t_m"]
    rin = rc + ct
    prof = [(rin, 0.0015), (R - e, 0.0015), (R - e * 0.3, 0.0025), (R, e), (R, L - e), (R - e * 0.3, L - 0.0025),
            (R - e, L - 0.0015), (rin, L - 0.0015)]
    parts.append(turned(prof, PAPER_ROLL_KEY, "roll", c=(x0, ry, zc), axis="x", n=24, loop=True))
    parts.append(turned([(rc, 0.0), (rin, 0.0), (rin, L), (rc, L)], CARDBOARD_KEY, "core", c=(x0, ry, zc), axis="x",
                        n=20, loop=True))
    # the sheet over the front: from the roll's front down past it, torn along a perforation
    tail = max(0.01, zc - R)                       # the sheet's torn edge at the box's bottom (ROLL["tail_m"] under the roll)
    yf = ry - R - ROLL["sheet_t_m"]
    teeth = ROLL["teeth"]
    sx0, sx1 = x0 + 0.004, x0 + L - 0.004
    bottom = []
    for k in range(teeth * 2 + 1):
        x = sx1 - (sx1 - sx0) * k / (teeth * 2)
        bottom.append((x, zc - R - tail + (ROLL["tear_m"] if k % 2 else 0.0)))
    face = [(sx0, zc), (sx1, zc)] + bottom[0:1] + bottom[1:-1] + bottom[-1:]
    t = ROLL["sheet_t_m"]
    n = len(face)
    sv = [(x, yf, z) for x, z in face] + [(x, yf + t, z) for x, z in face]
    sf = [list(range(n)), [n + i for i in reversed(range(n))]] + \
        [[i, n + i, n + (i + 1) % n, (i + 1) % n] for i in range(n)]
    parts.append(outward({"verts": sv, "faces": sf, "key": PAPER_ROLL_KEY, "role": "sheet"}))
    return parts


def label(cx: float, cy: float, z0: float, r: float, z_lo: float, z_hi: float, key: str = "paper",
          ink: str = "dark", arc_deg: float = 110.0) -> list[Part]:
    """A printed label on the front (-Y) of a round bottle of radius ``r``: a thin curved patch from ``z_lo`` to
    ``z_hi`` over ``arc_deg`` of its round, two lines of print on it (the brand and a text line)."""
    def patch(r0: float, za: float, zb: float, deg: float, k: str, role: str, t: float, n: int = 6) -> Part:
        a0 = math.radians(-90.0 - deg / 2.0)
        ring = [a0 + math.radians(deg) * i / n for i in range(n + 1)]
        outer = [(cx + (r0 + t) * math.cos(a), cy + (r0 + t) * math.sin(a)) for a in ring]
        inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)) for a in reversed(ring)]
        loop = outer + inner
        m = len(loop)
        verts = [(x, y, za) for x, y in loop] + [(x, y, zb) for x, y in loop]
        faces = [list(range(m - 1, -1, -1)), [m + i for i in range(m)]] + \
            [[i, (i + 1) % m, m + (i + 1) % m, m + i] for i in range(m)]
        return outward({"verts": verts, "faces": faces, "key": k, "role": role})

    hgt = z_hi - z_lo
    parts = [patch(r, z0 + z_lo, z0 + z_hi, arc_deg, key, "label", 0.0005)]
    for k, (f0, f1, deg) in enumerate(((0.60, 0.76, arc_deg * 0.55), (0.34, 0.42, arc_deg * 0.62))):
        parts.append(patch(r + 0.0005, z0 + z_lo + hgt * f0, z0 + z_lo + hgt * f1, deg, ink, "print", 0.0002, n=3))
    return parts


def plume(top, direction, length: float, seed: int = 0, key: str = "pampas") -> list[Part]:
    """A dried pampas plume at a stem's ``top``: ``PLUME["wisps"]`` fine tapering wisps fanning out of it along
    ``direction`` and drooping a little (a feathery head, never a ball)."""
    parts = []
    dx, dy, dz = direction
    ln = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
    u = (dx / ln, dy / ln, dz / ln)
    e1, e2 = _frame(u)
    for k in range(PLUME["wisps"]):
        a = 2 * math.pi * k / PLUME["wisps"] + 0.4 * ((_hash(seed, k) % 7) / 7.0)
        sp = PLUME["spread"] * (0.4 + 0.6 * ((_hash(seed, k, 1) % 5) / 4.0))
        wl = length * (0.65 + 0.35 * ((_hash(seed, k, 2) % 4) / 3.0))
        start = [top[i] - u[i] * length * 0.55 * (k % 3) / 3.0 for i in range(3)]
        side = [math.cos(a) * e1[i] + math.sin(a) * e2[i] for i in range(3)]
        pts = [start]
        for j in (1, 2, 3):
            f = j / 3.0
            pts.append([start[i] + (u[i] + side[i] * sp * f) * wl * f - (0.0, 0.0, 0.01 * f * f)[i] for i in range(3)])
        parts.append(tube(pts, [PLUME["wisp_r_m"] * 2.6, PLUME["wisp_r_m"] * 2.2, PLUME["wisp_r_m"] * 1.4,
                                PLUME["wisp_r_m"] * 0.5], key, "plume", sides=3))
    return parts


def stems_vase(cx: float, cy: float, z0: float, vase_r: float, vase_h: float, height: float,
               key: str = "ceramic") -> list[Part]:
    """A turned ceramic vase (a foot, a full belly, a narrow neck, a flared lip; open) with five dried pampas stems
    leaning out of it, each a thin stem with a feathery plume."""
    r = vase_r
    out = [(r * 0.55, 0.0), (r * 0.60, 0.006), (r * 0.92, vase_h * 0.22), (r, vase_h * 0.45), (r * 0.82, vase_h * 0.70),
           (r * 0.40, vase_h * 0.86), (r * 0.36, vase_h * 0.95), (r * 0.46, vase_h)]
    parts = [_vessel(out, 0.004, 0.012, key, "vase", c=(cx, cy, z0), n=12)]
    for k, (dx, dy) in enumerate(((-0.22, 0.05), (0.18, -0.06), (0.03, 0.2), (-0.08, -0.16), (0.25, 0.12))):
        length = height * (0.80 + 0.05 * k)
        lean = (dx * 0.35, dy * 0.35, 1.0)
        n = math.sqrt(sum(c * c for c in lean))
        u = tuple(c / n for c in lean)
        base = (cx + dx * 0.02, cy + dy * 0.02, z0 + 0.02)
        top = tuple(base[i] + u[i] * length for i in range(3))
        mid = tuple(base[i] + u[i] * length * 0.55 + (0.004 * (1 if k % 2 else -1) if i == 0 else 0.0)
                    for i in range(3))
        parts.append(tube([base, mid, top], [0.0019, 0.0016, 0.0013], "wood", "stem", sides=5))
        parts += plume(top, u, PLUME["length_m"], seed=k)
    return parts


def _round_slab(a: float, b: float, z0: float, t: float, key: str, role: str, rc: float = 0.01) -> Part:
    return slab(rounded_rect(a, b, rc), z0, t, key, role)


def tray(cx: float, cy: float, z0: float, a: float, b: float, key: str = "stone_light", lip: float = 0.010,
         t: float = 0.012) -> Part:
    """A small rounded tray (half sizes ``a`` x ``b``) with a raised lip ``lip`` wide; its floor ``t`` - 0.006 over
    ``z0`` (items stand on ``tray_floor``)."""
    ring_out = rounded_rect(a, b, min(a, b) * 0.45, n=4)
    ring_in = rounded_rect(a - lip, b - lip, max(0.002, min(a, b) * 0.45 - lip), n=4)
    floor = z0 + t - 0.006
    m = len(ring_out)
    verts = [(cx + x, cy + y, z0) for x, y in ring_out] + [(cx + x, cy + y, z0 + t) for x, y in ring_out] + \
        [(cx + x, cy + y, z0 + t) for x, y in ring_in] + [(cx + x, cy + y, floor) for x, y in ring_in]
    faces = [list(range(m - 1, -1, -1)), [3 * m + i for i in range(m)]]
    for k in range(3):
        a0, b0 = k * m, (k + 1) * m
        faces += [[a0 + i, a0 + (i + 1) % m, b0 + (i + 1) % m, b0 + i] for i in range(m)]
    return outward({"verts": verts, "faces": faces, "key": key, "role": "tray"})


def tray_floor(z0: float, t: float = 0.012) -> float:
    """The height of a ``tray``'s floor over its bottom ``z0``."""
    return z0 + t - 0.006


def _fit(parts: list[Part], w: float, d: float, h: float) -> list[Part]:
    """The parts moved (never scaled) so their box sits centred in ``w x d`` on z = 0; a part reaching past ``h`` is
    scaled down about the bottom so the set stays in its box."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    dx, dy = -(x0 + x1) / 2.0, -(y0 + y1) / 2.0
    sx = min(1.0, w / max(x1 - x0, 1e-9))
    sy = min(1.0, d / max(y1 - y0, 1e-9))
    sz = min(1.0, h / max(z1 - z0, 1e-9))
    s = min(sx, sy, sz)
    out = []
    for p in parts:
        out.append(dict(p, verts=[((vx + dx) * s, (vy + dy) * s, (vz - z0) * s) for vx, vy, vz in p["verts"]]))
    return out
