"""The contents of a see-through wardrobe as a designer's photo shows them (30 Oct 2026, lesson UL135; user on real04 run
20261029-201533-full, the black slatted run f_L0_023 of r_L0_e_yatak_odasi: "I like this but the clothes inside needs
more detail"; earlier the Argus inspector's D2 "a dark, flat wall panel with a window frame embedded in it";
docs/reference_details_20261029.md R31, R37: "hanging garments on a rail, folded stacks, drawers, a light inside").

What the run had (``modules.garment_parts`` of 29 Oct 2026): every garment one flat four-level prism under a straight
bar, all in the style's one fabric; folded stacks plain boxes; the LED strip a 12 x 6 mm glowing bar with no light of
its own, so the bays were dark behind the slats and the garments read as flat coloured strips.

What (pure; part lists of vertex / face lists, one mesh with the wardrobe, no modifier or boolean per garment):

- ``garments``: shirts, jackets, dresses, long coats, knits and trousers folded over the hanger's bar
  (``GARMENT_TYPES``: each its length, thickness, shoulder and hem, sleeves and collar, its fabric look), each a body
  lofted through rounded rings (neck, shoulders, chest, waist, hem; a dress flares, a knit has a ribbed hem), two
  sleeves hanging from the shoulders to the cuffs, a collar band, on a wooden hanger (a hook over the rail, two sloped
  arms; a trouser hanger's bar under them); lengths vary a few per cent, the gaps along the rail 1-4 cm with an
  occasional wider one, each garment swings and turns a few degrees (``random.Random(seed)``: one wardrobe always gets
  the same garments).
- the fabrics: each part key is ``cloth:<look>:<colour>`` (``cloth_key``): the bedding's woven fabric of that look
  (``textile_<look>``: the ``wenart_weave`` node group's cotton, wool, knit or linen weave normals, UL121) in a colour
  of the wardrobe's palette (``wardrobe_fronts.garment_palette``: the style family's wardrobe colours with the room
  scheme's colour; denim is a cotton twill in its blues).
- ``folded``: folded stacks with a rounded fold edge to the front, layers of uneven width, depth and thickness, each
  a little off and turned; ``shoes``: pairs with a rounded toe lower than the heel; ``boxes``: lidded storage boxes and
  rattan baskets on the lower shelves.
- ``bay_light``: the light of a bay's LED strip at the top of its front (``LED_LM_PER_M`` of a high-output wardrobe
  profile, ``LED_K``), so the contents read through the slats; ``modules.see_through_parts`` builds the strip's mesh
  (the ``led`` key), ``furniture`` the light (a rig light of the room: hidden while the daylight white point is
  metered).
- ``faces_per_bay``: the faces of each bay's contents (a cost record; every content part carries its ``bay``).

Why: the user likes the slats and asked for real clothes behind them: a garment reads by its shoulders, sleeves and
collar and its fabric, a stack by its folds, and only with a light inside.
"""
from __future__ import annotations

import math
import random
from typing import Optional, Sequence

LESSON = "UL135"
CLOTH_PREFIX = "cloth:"        # = modules.CLOTH_PREFIX: ``cloth:<look>:<colour>`` (or the old ``cloth:<colour>``)
LOOKS: tuple[str, ...] = ("cotton", "wool", "knit", "linen")          # = bedding_parts.LOOK_SLUGS keys used here
LED_LM_PER_M = 1000.0          # a high-output wardrobe LED profile (800-1400 lm per metre)
LED_K = 3000.0                 # warm white wardrobe LED
# kind: (length m, thickness m, shoulder half width m, hem half width m, sleeve length m (0: none), look, weight,
# collar: band | lapel | rib | None)
GARMENT_TYPES: dict[str, tuple] = {
    "shirt": (0.78, 0.026, 0.215, 0.200, 0.60, "cotton", 5, "band"),
    "jacket": (0.80, 0.058, 0.230, 0.215, 0.62, "wool", 2, "lapel"),
    "coat": (1.12, 0.068, 0.235, 0.255, 0.63, "wool", 1, "lapel"),
    "dress": (1.02, 0.032, 0.160, 0.275, 0.0, "linen", 1, None),
    "knit": (0.68, 0.050, 0.220, 0.205, 0.58, "knit", 2, "rib"),
    "trousers": (0.50, 0.024, 0.150, 0.150, 0.0, "cotton", 2, None),
}
# colours a kind is not worn in (a white coat, a mustard shirt read as wrong in a wardrobe)
TROUSER_COLOURS: tuple[str, ...] = ("navy", "dusty blue", "charcoal", "black", "sand", "camel", "olive", "taupe")
SHOE_COLOURS: tuple[str, ...] = ("black", "camel", "white", "charcoal", "taupe", "navy")
BOX_COLOURS: tuple[str, ...] = ("off white", "greige", "sand", "charcoal")


def cloth_key(look: str, colour: str) -> str:
    """The part key of a fabric in a colour (module docstring)."""
    return f"{CLOTH_PREFIX}{look}:{colour}"


def parse_cloth_key(key: str) -> tuple[Optional[str], Optional[str]]:
    """``(look, colour)`` of a ``cloth:`` key (``cloth:<look>:<colour>``, or ``cloth:<colour>``: look None)."""
    rest = key[len(CLOTH_PREFIX):] if key.startswith(CLOTH_PREFIX) else key
    look, sep, colour = rest.partition(":")
    if sep and look in LOOKS:
        return look, colour or None
    return None, rest or None


# --------------------------------------------------------------------------
# small meshes
# --------------------------------------------------------------------------

def _ring(cx: float, cy: float, z: float, hx: float, hy: float) -> list[tuple[float, float, float]]:
    """A rounded rectangle of 8 points (counter-clockwise seen from above): a garment's section."""
    return [(cx + hx, cy - 0.82 * hy, z), (cx + hx, cy + 0.82 * hy, z), (cx + 0.5 * hx, cy + hy, z),
            (cx - 0.5 * hx, cy + hy, z), (cx - hx, cy + 0.82 * hy, z), (cx - hx, cy - 0.82 * hy, z),
            (cx - 0.5 * hx, cy - hy, z), (cx + 0.5 * hx, cy - hy, z)]


def _ellipse(cx: float, cy: float, z: float, rx: float, ry: float, n: int = 6) -> list[tuple[float, float, float]]:
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def _loft(rings: Sequence[Sequence[tuple]], key: str, role: str, top: bool = True, bottom: bool = True) -> dict:
    """A closed (or open-ended) tube through horizontal rings from the top down, outward normals."""
    n = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = [[0 + i for i in range(n)]] if top else []
    for k in range(len(rings) - 1):
        a, b = n * k, n * (k + 1)
        for i in range(n):
            j = (i + 1) % n
            faces.append([a + i, b + i, b + j, a + j])
    if bottom:
        last = n * (len(rings) - 1)
        faces.append([last + i for i in range(n - 1, -1, -1)])
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}


def _beam(p0, p1, wx: float, wz: float, key: str, role: str) -> dict:
    """A box from ``p0`` to ``p1`` (both at one x; a hanger's arm in the y-z plane), ``wx`` across, ``wz`` thick."""
    (x0, y0, z0), (_x1, y1, z1) = p0, p1
    dy, dz = y1 - y0, z1 - z0
    ln = math.hypot(dy, dz) or 1e-9
    ny, nz = -dz / ln * wz / 2.0, dy / ln * wz / 2.0
    verts = []
    for (py, pz) in ((y0, z0), (y1, z1)):
        verts += [(x0 - wx / 2.0, py - ny, pz - nz), (x0 + wx / 2.0, py - ny, pz - nz),
                  (x0 + wx / 2.0, py + ny, pz + nz), (x0 - wx / 2.0, py + ny, pz + nz)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _box(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str) -> dict:
    x0, x1, y0, y1, z1 = cx - w / 2.0, cx + w / 2.0, cy - d / 2.0, cy + d / 2.0, z0 + h
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
             (x0, y1, z1)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _prism_xz(profile: Sequence[tuple[float, float]], y0: float, y1: float, key: str, role: str) -> dict:
    """A profile in the x-z plane (counter-clockwise seen from -y) extruded from ``y0`` to ``y1``."""
    n = len(profile)
    verts = [(x, y0, z) for x, z in profile] + [(x, y1, z) for x, z in profile]
    faces = [list(range(n - 1, -1, -1)), [n + i for i in range(n)]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}


def _prism_yz(profile: Sequence[tuple[float, float]], x0: float, x1: float, key: str, role: str) -> dict:
    """A profile in the y-z plane extruded along x from ``x0`` to ``x1``."""
    n = len(profile)
    verts = [(x0, y, z) for y, z in profile] + [(x1, y, z) for y, z in profile]
    faces = [list(range(n)), [n + i for i in range(n - 1, -1, -1)]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, n + i, n + j, j])
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}


def _transform(parts: list[dict], origin, swing_deg: float, turn_deg: float) -> list[dict]:
    """Turn parts about ``origin``: ``swing_deg`` about the x axis (the rail: the hem moves along y), then ``turn_deg``
    about the vertical (pure)."""
    ox, oy, oz = origin
    cs, ss = math.cos(math.radians(swing_deg)), math.sin(math.radians(swing_deg))
    ct, st = math.cos(math.radians(turn_deg)), math.sin(math.radians(turn_deg))
    out = []
    for p in parts:
        verts = []
        for x, y, z in p["verts"]:
            y1, z1 = (y - oy) * cs - (z - oz) * ss, (y - oy) * ss + (z - oz) * cs
            x1 = x - ox
            x2, y2 = x1 * ct - y1 * st, x1 * st + y1 * ct
            verts.append((round(ox + x2, 6), round(oy + y2, 6), round(oz + z1, 6)))
        out.append(dict(p, verts=verts))
    return out


# --------------------------------------------------------------------------
# garments
# --------------------------------------------------------------------------

def _hanger(cx: float, y: float, rail_z: float, hz: float, arm: float, bar: Optional[float]) -> list[dict]:
    """A wooden hanger: a steel hook over the rail, a neck, two sloped arms, a bar under them for trousers."""
    parts = [_box(cx, y, hz + 0.004, 0.004, 0.004, rail_z + 0.026 - hz - 0.004, "steel", "hanger"),
             _box(cx, y + 0.009, rail_z + 0.022, 0.004, 0.022, 0.004, "steel", "hanger"),
             _box(cx, y + 0.018, rail_z + 0.004, 0.004, 0.004, 0.022, "steel", "hanger"),
             _box(cx, y, hz - 0.012, 0.012, 0.03, 0.018, "wood", "hanger")]
    for s in (-1.0, 1.0):
        parts.append(_beam((cx, y, hz - 0.004), (cx, y + s * arm, hz - 0.042), 0.012, 0.018, "wood", "hanger"))
    if bar is not None:
        parts.append(_box(cx, y, bar - 0.006, 0.010, 2.0 * arm * 0.95, 0.012, "wood", "hanger"))
        for s in (-1.0, 1.0):
            parts.append(_box(cx, y + s * arm * 0.95, bar, 0.006, 0.006, hz - 0.042 - bar, "steel", "hanger"))
    return parts


def garment(kind: str, cx: float, y: float, rail_z: float, colour: str, rng: random.Random,
            max_len: Optional[float] = None) -> list[dict]:
    """One garment on its hanger (module docstring): the parts, swung and turned a few degrees about its hook."""
    length, thick, sh, hem, sleeve, look, _w, collar = GARMENT_TYPES[kind]
    length *= rng.uniform(0.94, 1.06)
    thick *= rng.uniform(0.85, 1.15)
    if max_len is not None:
        length = min(length, max_len)
    key = cloth_key(look, colour)
    hz = rail_z - 0.045
    if kind == "trousers":
        bar = hz - 0.13
        g, t = 0.007, thick
        drop = min(length, (max_len or length))
        prof = [(-(g + t), bar - drop), (-(g + t), bar), (-(g + t) * 0.7, bar + (g + t) * 0.7), (0.0, bar + g + t),
                ((g + t) * 0.7, bar + (g + t) * 0.7), (g + t, bar), (g + t, bar - drop * rng.uniform(0.82, 0.95)),
                (g, bar - drop * 0.8), (g, bar), (0.0, bar + g), (-g, bar), (-g, bar - drop)]
        prof = [(cx + px, pz) for px, pz in prof]
        w = 2.0 * sh * rng.uniform(0.9, 1.05)
        parts = _hanger(cx, y, rail_z, hz, 0.20, bar) + [dict(_prism_xz(prof, y - w / 2.0, y + w / 2.0, key,
                                                                      "garment"), garment=kind)]
        return _transform(parts, (cx, y, rail_z), rng.uniform(-2.0, 2.0), rng.uniform(-4.0, 4.0))
    top = hz - 0.03
    t = thick
    if kind == "dress":
        levels = [(top, 0.35 * t, 0.055), (top - 0.04, 0.5 * t, sh), (top - 0.20, 0.55 * t, sh * 0.92),
                  (top - 0.38 * length, 0.5 * t, sh * 0.78), (top - 0.62 * length, 0.55 * t, (sh + hem) / 2.0),
                  (top - length, 0.5 * t, hem)]
    else:
        levels = [(top, 0.35 * t, 0.06), (top - 0.045, 0.5 * t, sh), (top - 0.22, 0.55 * t, sh * 0.97),
                  (top - 0.55 * length, 0.5 * t, (sh + hem) / 2.0 * 0.96), (top - length, 0.42 * t, hem)]
        if kind == "knit":                                       # a ribbed hem band
            levels.insert(-1, (top - length + 0.05, 0.5 * t, hem * 1.03))
    rings = [_ring(cx + 0.012 * k / len(levels), y, z, hx, hy) for k, (z, hx, hy) in enumerate(levels)]
    parts = _hanger(cx, y, rail_z, hz, sh * 0.92, None) + [dict(_loft(rings, key, "garment"), garment=kind)]
    if sleeve > 0:
        r0 = 0.06 if kind in ("jacket", "coat") else 0.05
        sl = min(sleeve * rng.uniform(0.95, 1.05), length - 0.06)
        for s in (-1.0, 1.0):
            pts = [(top - 0.06, sh - 0.03, r0), (top - 0.06 - 0.5 * sl, sh + 0.004, r0 * 0.85),
                   (top - 0.06 - sl + 0.05, sh - 0.004, r0 * 0.72), (top - 0.06 - sl, sh - 0.008, r0 * 0.66)]
            srings = [_ellipse(cx + 0.006, y + s * yy, z, 0.5 * t + 0.006, rr) for z, yy, rr in pts]
            parts.append(_loft(srings, key, "sleeve", top=False))
    if collar == "band":
        parts.append(_loft([_ring(cx, y, top + 0.022, 0.35 * t + 0.003, 0.055),
                            _ring(cx, y, top - 0.004, 0.42 * t + 0.004, 0.07)], key, "collar", top=False,
                           bottom=False))
    elif collar in ("lapel", "rib"):
        wide = 0.10 if collar == "lapel" else 0.075
        parts.append(_loft([_ring(cx, y, top + 0.012, 0.45 * t + 0.004, wide * 0.8),
                            _ring(cx, y, top - 0.05, 0.55 * t + 0.004, wide)], key, "collar", top=False,
                           bottom=False))
    return _transform(parts, (cx, y, rail_z), rng.uniform(-2.5, 2.5), rng.uniform(-5.0, 5.0))


def _inside(parts: list[dict], y: float, half: Optional[float]) -> list[dict]:
    """The parts with every vertex within ``half`` of ``y`` across the wardrobe (a swung hem or a wide hanger stays
    inside the carcass; pure)."""
    if half is None:
        return parts
    lo, hi = y - half, y + half
    return [dict(p, verts=[(vx, min(hi, max(lo, vy)), vz) for vx, vy, vz in p["verts"]]) for p in parts]


def garments(x0: float, x1: float, y: float, rail_z: float, seed: int, max_len: float,
             palette: Optional[Sequence[str]] = None, half_depth: Optional[float] = None) -> list[dict]:
    """The garments on a rail from ``x0`` to ``x1`` (module docstring): kinds by weight among those whose length fits
    ``max_len`` (trousers always fit: they fold over the bar), colours from ``palette``, deterministic by ``seed``;
    ``half_depth``: the room across the carcass each side of the rail (``_inside``)."""
    from wenart.blender import wardrobe_fronts as WF

    rng = random.Random(seed)
    colours = list(palette or WF.GARMENT_COLOURS)
    kinds = [k for k, g in GARMENT_TYPES.items() if g[0] * 0.94 <= max_len + 1e-9 or k == "trousers"]
    weights = [GARMENT_TYPES[k][6] for k in kinds]
    parts: list[dict] = []
    x = x0 + 0.02
    while True:
        kind = rng.choices(kinds, weights=weights)[0]
        thick = GARMENT_TYPES[kind][1] * 1.15 + (0.016 if GARMENT_TYPES[kind][4] else 0.0)
        if x + thick > x1 - 0.01:
            break
        pool = [c for c in colours if c in TROUSER_COLOURS] if kind == "trousers" else colours
        colour = (pool or colours)[rng.randrange(len(pool or colours))]
        parts += _inside(garment(kind, x + thick / 2.0, y, rail_z, colour, rng, max_len), y, half_depth)
        x += thick + rng.uniform(0.010, 0.040) + (0.06 if rng.random() < 0.1 else 0.0)
    return parts


# --------------------------------------------------------------------------
# shelves: folded stacks, shoes, boxes and baskets
# --------------------------------------------------------------------------

def folded_piece(cx: float, cy: float, z: float, w: float, d: float, h: float, turn_deg: float, key: str) -> dict:
    """A folded piece: a slab with its rounded fold edge to the front (-y), turned ``turn_deg`` about its centre."""
    r = h / 2.0
    yf, yb = cy - d / 2.0, cy + d / 2.0
    prof = [(yb, z), (yb, z + h)] + [(yf + r + r * math.cos(math.radians(a)), z + r + r * math.sin(math.radians(a)))
                                     for a in (90, 135, 180, 225, 270)]
    part = _prism_yz(prof, cx - w / 2.0, cx + w / 2.0, key, "folded")
    return _transform([part], (cx, cy, z), 0.0, turn_deg)[0]


def folded(x0: float, x1: float, y: float, z: float, room: float, seed: int,
           palette: Optional[Sequence[str]] = None, depth: float = 0.28) -> list[dict]:
    """Folded stacks on a shelf from ``x0`` to ``x1`` at ``z`` with ``room`` over it (module docstring): one stack per
    0.33 m, 3-6 pieces of 3.5-5.5 cm, each a little off, turned and of its own size; knits and cottons."""
    from wenart.blender import wardrobe_fronts as WF

    rng = random.Random(seed)
    colours = list(palette or WF.GARMENT_COLOURS)
    n = max(1, int((x1 - x0) / 0.33))
    pitch = (x1 - x0) / n
    parts: list[dict] = []
    for i in range(n):
        cx = x0 + pitch * (i + 0.5)
        zz = z
        for _k in range(rng.randint(3, 6)):
            h = rng.uniform(0.035, 0.055)
            if zz + h > z + room - 0.03:
                break
            look = rng.choice(("knit", "cotton", "cotton", "wool"))
            colour = colours[rng.randrange(len(colours))]
            w = min(0.31, pitch - 0.03) * rng.uniform(0.93, 1.0)
            parts.append(folded_piece(cx + rng.uniform(-0.012, 0.012), y + rng.uniform(-0.01, 0.01), zz, w,
                                      depth * rng.uniform(0.92, 1.0), h, rng.uniform(-2.5, 2.5),
                                      cloth_key(look, colour)))
            zz += h + 0.001
    return parts


def shoe(cx: float, cy: float, z: float, length: float, width: float, height: float, key: str) -> dict:
    """One shoe: a rounded footprint, toe to the front (-y), its toe lower than its heel."""
    hl, hw = length / 2.0, width / 2.0
    foot = [(0.0, -hl), (hw * 0.75, -hl * 0.82), (hw, -hl * 0.35), (hw * 0.95, hl * 0.55), (hw * 0.6, hl),
            (-hw * 0.6, hl), (-hw * 0.95, hl * 0.55), (-hw, -hl * 0.35), (-hw * 0.75, -hl * 0.82)]
    n = len(foot)
    tops = [height * (0.45 if fy < -hl * 0.3 else 0.75 if fy < hl * 0.3 else 1.0) for _fx, fy in foot]
    verts = [(cx + fx, cy + fy, z) for fx, fy in foot] + [(cx + fx, cy + fy, z + t) for (fx, fy), t in zip(foot, tops)]
    faces = [list(range(n - 1, -1, -1)), [n + i for i in range(n)]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return {"verts": verts, "faces": faces, "key": key, "role": "shoe", "smooth": True}


def shoes(x0: float, x1: float, y: float, z: float, seed: int) -> list[dict]:
    """Pairs of shoes from ``x0`` to ``x1`` at ``z`` (a pair every 0.22 m, an occasional gap, each in one colour)."""
    rng = random.Random(seed)
    parts: list[dict] = []
    n = max(1, int(round((x1 - x0) / 0.22)))
    pitch = (x1 - x0) / n
    for i in range(n):
        if n > 2 and rng.random() < 0.2:
            continue
        cx = x0 + pitch * (i + 0.5)
        colour = SHOE_COLOURS[rng.randrange(len(SHOE_COLOURS))]
        look = "wool" if colour in ("white", "taupe") else "cotton"
        h = rng.choice((0.08, 0.10, 0.12))
        for s in (-1, 1):
            parts.append(shoe(cx + s * 0.052, y - 0.02 + rng.uniform(-0.01, 0.01), z, 0.26, 0.092, h,
                              cloth_key(look, colour)))
    return parts


def boxes(x0: float, x1: float, y: float, z: float, room: float, seed: int, depth: float = 0.30) -> list[dict]:
    """A lidded storage box and a rattan basket in turn along a shelf (``room`` over it), a stack of two where it fits."""
    rng = random.Random(seed)
    parts: list[dict] = []
    n = max(1, int((x1 - x0) / 0.36))
    pitch = (x1 - x0) / n
    for i in range(n):
        cx = x0 + pitch * (i + 0.5)
        w = min(0.33, pitch - 0.03)
        h = min(0.20, room - 0.04)
        if h < 0.08:
            break
        if (i + seed) % 2 == 0:                       # a linen storage box with its lid
            key = cloth_key("linen", BOX_COLOURS[rng.randrange(len(BOX_COLOURS))])
            parts.append(_box(cx, y, z, w, depth, h - 0.025, key, "box"))
            parts.append(_box(cx, y, z + h - 0.03, w + 0.006, depth + 0.006, 0.03, key, "box"))
        else:
            parts.append(_box(cx, y, z, w, depth, h * 0.8, "rattan", "basket"))
            parts.append(_box(cx, y, z + h * 0.8, w + 0.01, depth + 0.01, 0.015, "rattan", "basket"))
    return parts


# --------------------------------------------------------------------------
# the light and the cost record
# --------------------------------------------------------------------------

def bay_light(x: float, y: float, z: float, inner_w: float) -> dict:
    """The light of a bay's LED strip (module docstring): an area light under the bay's top at its front, pointing
    down, ``LED_LM_PER_M`` over its length, ``LED_K``; in the wardrobe's own frame."""
    from wenart.blender import lighting as L

    length = max(0.2, inner_w - 0.04)
    lumens = LED_LM_PER_M * length
    watts = L.watts_for_lumens(lumens) * L.RIG_GAIN
    return {"center": [round(x, 4), round(y, 4), round(z, 4)], "size_m": [round(length, 4), 0.03],
            "lumens": round(lumens, 1), "watts_radiometric": L.watts_for_lumens(lumens), "energy_w": round(watts, 4),
            "gain": L.RIG_GAIN, "temperature_k": LED_K, "direction": [0.0, 0.0, -1.0],
            "source": f"a high-output wardrobe LED profile, {LED_LM_PER_M:.0f} lm per metre (UL135)"}


def faces_per_bay(parts: Sequence[dict]) -> dict[int, int]:
    """``{bay: faces}`` of the parts that carry a ``bay`` (the contents of each bay; a cost record)."""
    out: dict[int, int] = {}
    for p in parts:
        if p.get("bay") is not None:
            out[int(p["bay"])] = out.get(int(p["bay"]), 0) + len(p["faces"])
    return out
