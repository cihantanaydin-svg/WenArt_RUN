"""The bathroom's styled objects as real products (30 Oct 2026, lesson UL166, user on a bathroom of real04 run
20261030-043021-full: "Here models needs more details": the lit shelf column held a glass box with two black squares
(the perfume), a few pebbles in an invisible jar, three sticks with white balls (the cotton stems), a green egg in a
white cylinder (the plant)). Pure (no ``bpy``): vertex and face lists the bathroom parts (``bath_parts``) put into
their host's one mesh (lesson UL111).

Every object is turned (``lathe``: a profile of rings round a vertical axis, closed, wound outwards) or lofted, with
the real details a stylist's product has (designer sizes of real products, assumed):

- ``pump_bottle``: a bottle with rounded shoulders and a neck, a ribbed screw collar, the pump's stem, its rounded
  actuator and the nozzle reaching forward with its tip turned down, a label band round the body.
- ``apothecary_jar``: a glass jar with a rounded shoulder and a rim, a lid with a knob (wood, steel or ceramic), filled
  with cotton balls, cotton pads or pebbles (``fill``); the glass is see-through, the contents and the lid make it read.
- ``reed_diffuser``: a glass bottle (amber or dark) with a metal collar and ``DIFFUSER["reeds"]`` thin reeds fanned out
  (no balls).
- ``potted_plant``: a ceramic pot with a rim, its soil and a small leafy plant: leaf blades on short stems, arched out
  and drooping at their tips (``leaf``), the midrib folded.
- ``perfume_bottle``: a thick glass flacon with rounded edges, the amber scent inside it (``liquid``), a metal collar
  and a cap.
- ``candle_glass``: a candle poured in a glass tumbler: the glass, the wax under its rim, the wick.
- ``soap_dish``: a shallow stone dish with a bar of soap.
- ``woven_basket``: a rounded-rectangular rattan basket with a rolled rim and two rolled towels in it.
- ``cotton_stem``: a dried cotton branch: a stem, a dark calyx and three white puffs per boll.

The material keys are the parametric ones (``parametric.MATERIAL_KEYS``): ``glass``, ``ceramic`` (glazed white),
``dark`` (black lacquer), ``terracotta`` (amber), ``wood``, ``rattan``, ``bedding`` (white cotton), ``green``,
``stone_light`` (marble), ``worktop`` (dark stone), ``steel`` and ``handle`` (the room's fixture finish on a piece).
Round parts are ``"smooth": True`` (the build shades them smooth, ``furniture.add_bevel``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import parametric as P
from wenart.blender import towel_parts as TP

Part = dict
LESSON = "UL166"
LATHE_N = 12                      # segments round a turned object (a 6-7 cm bottle: 1.7 cm per facet, shaded smooth)
JAR_FILL = {"layers": 2, "pads": 6}   # a jar shows two layers of cotton balls or pebbles (the rest is unseen)
DIFFUSER = {"reeds": 7, "reed_r_m": 0.0015, "spread": 0.30}
PUMP = {"stem_share": 0.07, "head_share": 0.07, "nozzle_share": 0.95}
JAR_GLASS_M = 0.003               # an apothecary jar's wall
LEAF = {"segments": 6, "thickness_m": 0.0012, "fold": 0.18}
JAR_LID_M = 0.027                 # an apothecary jar's lid and knob over its rim
PLANT_REACH = 0.68                # a potted plant's leaves reach this share of its foliage height from its centre


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def lathe(cx: float, cy: float, z0: float, profile: Sequence[tuple[float, float]], key: str, role: str,
          n: int = LATHE_N, smooth: bool = True, close_start: bool = True, close_end: bool = True) -> Part:
    """A turned solid: the rings ``(r, z)`` of ``profile`` (from its bottom, up and over its top, an open vessel down
    its inside to its floor) round the vertical axis at ``(cx, cy)`` from ``z0``; the first ring closed downwards, the
    last upwards (wound outwards: the face of a profile step points along ``e_phi x step``)."""
    verts = []
    for r, z in profile:
        r = max(float(r), 1e-4)
        verts += [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z0 + float(z))
                  for i in range(n)]
    faces = []
    for k in range(len(profile) - 1):
        a, b = k * n, (k + 1) * n
        faces += [[a + i, a + (i + 1) % n, b + (i + 1) % n, b + i] for i in range(n)]
    if close_start:
        faces.append(list(range(n - 1, -1, -1)))
    if close_end:
        last = (len(profile) - 1) * n
        faces.append([last + i for i in range(n)])
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": smooth}


def _ring_loft(cx: float, cy: float, z0: float, rings: Sequence[tuple[float, float, float]], key: str, role: str,
               power: float = 4.0, n: int = 24, smooth: bool = True) -> Part:
    """A lofted solid of superellipse rings ``(a, b, z)`` (half width, half depth, height; ``power`` 2: an ellipse, 4:
    a rounded rectangle), closed like ``lathe``."""
    verts = []
    for a, b, z in rings:
        for i in range(n):
            t = 2 * math.pi * i / n
            c, s = math.cos(t), math.sin(t)
            verts.append((cx + a * math.copysign(abs(c) ** (2.0 / power), c),
                          cy + b * math.copysign(abs(s) ** (2.0 / power), s), z0 + z))
    faces = []
    for k in range(len(rings) - 1):
        p, q = k * n, (k + 1) * n
        faces += [[p + i, p + (i + 1) % n, q + (i + 1) % n, q + i] for i in range(n)]
    faces.append(list(range(n - 1, -1, -1)))
    last = (len(rings) - 1) * n
    faces.append([last + i for i in range(n)])
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": smooth}


def _stick(p0, p1, r: float, key: str, role: str) -> Part:
    """A thin square prism from ``p0`` to ``p1`` (3D points; a reed, a stem), wound outwards."""
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    ln = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
    ux, uy, uz = dx / ln, dy / ln, dz / ln
    ax = (1.0, 0.0, 0.0) if abs(ux) < 0.9 else (0.0, 1.0, 0.0)
    e1 = (ax[1] * uz - ax[2] * uy, ax[2] * ux - ax[0] * uz, ax[0] * uy - ax[1] * ux)
    m = math.sqrt(sum(c * c for c in e1)) or 1e-9
    e1 = tuple(c / m for c in e1)
    e2 = (uy * e1[2] - uz * e1[1], uz * e1[0] - ux * e1[2], ux * e1[1] - uy * e1[0])
    ring = [(r, 0.0), (0.0, r), (-r, 0.0), (0.0, -r)]
    verts = [(x0 + e1[0] * a + e2[0] * b, y0 + e1[1] * a + e2[1] * b, z0 + e1[2] * a + e2[2] * b) for a, b in ring]
    verts += [(x1 + e1[0] * a + e2[0] * b, y1 + e1[1] * a + e2[1] * b, z1 + e1[2] * a + e2[2] * b) for a, b in ring]
    faces = [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)] + [[4, 5, 6, 7], [3, 2, 1, 0]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _blob(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str, e: float = 1.0,
          n_eta: int = 4, n_om: int = 8) -> Part:
    return P._superellipsoid(cx, cy, z0, w, d, h, e, e, key, role, n_eta=n_eta, n_om=n_om)


def _hash(*v: int) -> int:
    h = 2166136261
    for x in v:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


# --------------------------------------------------------------------------
# the products
# --------------------------------------------------------------------------

def pump_bottle(cx: float, cy: float, z0: float, r: float, h: float, key: str, head_key: str = "dark",
                label_key: Optional[str] = None) -> list[Part]:
    """A pump bottle ``h`` high (to the actuator's top), radius ``r``: rounded body and shoulder, neck, ribbed collar,
    stem, actuator, a nozzle forward (-Y) with its tip turned down, a label band (``label_key``; default white on a
    dark or amber bottle, black on a white one)."""
    hs, hh = PUMP["stem_share"] * h, PUMP["head_share"] * h
    bh = h - hs - hh - 0.10 * h                                          # body to the neck's top
    body = [(r * 0.90, 0.0), (r, 0.006), (r, bh * 0.74), (r * 0.94, bh * 0.83), (r * 0.70, bh * 0.92),
            (r * 0.42, bh * 0.96), (r * 0.38, bh)]
    parts = [lathe(cx, cy, z0, body, key, "bottle")]
    cz = z0 + bh
    collar = [(r * 0.45, 0.0), (r * 0.47, 0.01 * h)]
    for k in range(2):                                                   # the screw collar's ribs
        z = 0.01 * h + k * 0.025 * h
        collar += [(r * 0.47, z + 0.010 * h), (r * 0.44, z + 0.018 * h), (r * 0.47, z + 0.025 * h)]
    collar += [(r * 0.44, 0.10 * h), (r * 0.16, 0.10 * h)]
    parts.append(lathe(cx, cy, cz, collar, head_key, "cap", smooth=False))
    sz = cz + 0.10 * h
    parts.append(P._cylinder_z(cx, cy, sz, r * 0.12, r * 0.12, hs, head_key, "pump", n=8))
    head = [(r * 0.30, 0.0), (r * 0.34, hh * 0.25), (r * 0.34, hh * 0.65), (r * 0.26, hh * 0.92), (r * 0.10, hh)]
    parts.append(lathe(cx, cy, sz + hs, head, head_key, "pump"))
    nl = PUMP["nozzle_share"] * r
    nz = sz + hs + hh * 0.55
    nr = max(0.0025, r * 0.09)
    parts.append(P._cylinder_y(cx, cy - nl, nz, nr, nr, nl - r * 0.25, head_key, "nozzle", n=8))
    parts.append(P._cylinder_z(cx, cy - nl + nr, nz - nr * 2.6, nr, nr, nr * 2.6, head_key, "nozzle", n=8))
    # 30 Oct 2026 (lesson UL184, user: "Better models with more details is needed"): a printed paper label on the
    # bottle's front (a curved patch with lines of print), not a band round it; an amber bottle is glass with the soap
    # in it
    from wenart.blender import small_parts as SM

    if key == "terracotta":
        parts[0] = SM._vessel(body, SM.GLASS_M, 0.004, "glass", "bottle", c=(cx, cy, z0), n=LATHE_N)
        parts.insert(1, SM.turned([(r - SM.GLASS_M - 0.001, 0.0), (r - SM.GLASS_M - 0.001, bh * 0.66),
                                   (r - SM.GLASS_M - 0.003, bh * 0.68)], SM.OIL_KEY, "contents",
                                  c=(cx, cy, z0 + 0.0045), n=LATHE_N))
    lk = label_key if label_key in ("paper", "ceramic", "dark") else "paper"
    ink = "ceramic" if lk == "dark" else "dark"
    parts += SM.label(cx, cy, z0, r, bh * 0.30, bh * 0.62, lk, ink)
    return parts


def apothecary_jar(cx: float, cy: float, z0: float, r: float, h: float, lid_key: str = "wood",
                   fill: str = "cotton", seed: int = 0) -> list[Part]:
    """A glass jar ``h`` high to its rim, radius ``r``, its lid and knob on top (about ``0.02`` m more), ``fill``:
    ``cotton`` (balls), ``pads`` (cotton pads), ``pebbles`` or ``salt`` (a fill of bath salt)."""
    g = JAR_GLASS_M
    rn = r * 0.86
    shell = [(r - 0.004, 0.0), (r, 0.004), (r, h - 0.016), (r * 0.94, h - 0.009), (rn, h - 0.004), (rn, h),
             (rn - g, h), (rn - g, h - 0.004), (r * 0.94 - g, h - 0.009), (r - g, h - 0.016), (r - g, g + 0.002),
             (r - g - 0.003, g)]
    parts = [lathe(cx, cy, z0, shell, "glass", "jar")]
    lid = [(rn + 0.002, 0.0), (rn + 0.003, 0.004), (rn + 0.003, 0.010), (rn * 0.80, 0.014), (rn * 0.30, 0.016)]
    parts.append(lathe(cx, cy, z0 + h - 0.002, lid, lid_key, "lid"))
    kr = min(0.010, r * 0.28)
    # 30 Oct 2026 (UL184): a turned knob on a short neck
    parts.append(lathe(cx, cy, z0 + h + 0.011, [(kr * 0.45, 0.0), (kr * 0.40, kr * 0.35), (kr * 0.95, kr * 0.75),
                                                (kr, kr * 1.05), (kr * 0.75, kr * 1.45), (kr * 0.15, kr * 1.6)],
                       lid_key, "lid", n=8))
    inner = r - g - 0.002
    top = h * (0.62 if fill != "salt" else 0.55)
    if fill == "salt":
        parts.append(lathe(cx, cy, z0 + g, [(inner, 0.0), (inner, top), (inner * 0.4, top + 0.004)], "bedding",
                           "fill"))
    elif fill == "pads":
        pr = min(0.026, inner - 0.002)
        z = z0 + g
        k = 0
        while z + 0.006 <= z0 + top and k < JAR_FILL["pads"]:
            dx = 0.002 * math.cos(k * 2.1)
            parts.append(_blob(cx + dx, cy + 0.002 * math.sin(k * 2.1), z, 2 * pr, 2 * pr, 0.006, "bedding", "fill",
                               e=0.35, n_eta=4, n_om=12))
            z += 0.0055
            k += 1
    else:
        br = min(0.013 if fill == "cotton" else 0.011, inner * 0.36)
        ring = [(0.0, 0.0)] + [((inner - br) * math.cos(2 * math.pi * j / 5 + 0.3), (inner - br) * math.sin(
            2 * math.pi * j / 5 + 0.3)) for j in range(5)]
        z, layer = z0 + g, 0
        while z + br * 1.6 <= z0 + top and layer < JAR_FILL["layers"]:
            for j, (px, py) in enumerate(ring):
                if math.hypot(px, py) + br > inner + 1e-9:
                    continue
                s = _hash(seed, layer, j)
                if fill == "cotton":
                    parts.append(_blob(cx + px, cy + py, z, 2 * br, 2 * br * 0.95, 2 * br * 0.9, "bedding", "fill"))
                else:
                    k = ("stone_light", "worktop", "ceramic")[s % 3]
                    f = 0.75 + 0.25 * (s % 5) / 4.0
                    parts.append(_blob(cx + px, cy + py, z, 2 * br * f, 1.6 * br * f, 1.1 * br * f, k, "fill",
                                       e=0.8))
            z += br * (1.7 if fill == "cotton" else 1.1)
            layer += 1
    return parts


def reed_diffuser(cx: float, cy: float, z0: float, r: float, h: float, reed_len: float, key: str = "terracotta",
                  collar_key: str = "handle", seed: int = 0) -> list[Part]:
    """A diffuser bottle (``h`` high, radius ``r``) with a collar and fanned reeds ``reed_len`` long from its neck."""
    body = [(r * 0.92, 0.0), (r, 0.005), (r, h * 0.70), (r * 0.80, h * 0.82), (r * 0.36, h * 0.90),
            (r * 0.32, h)]
    parts = [lathe(cx, cy, z0, body, key, "bottle")]
    parts.append(lathe(cx, cy, z0 + h * 0.86, [(r * 0.40, 0.0), (r * 0.40, h * 0.14), (r * 0.30, h * 0.15)],
                       collar_key, "cap", smooth=False))
    n = DIFFUSER["reeds"]
    top = z0 + h
    for k in range(n):
        a = 2 * math.pi * (k + 0.5 * (_hash(seed, k) % 3) / 3.0) / n
        lean = DIFFUSER["spread"] * (0.6 + 0.4 * ((_hash(seed, k, 1) % 5) / 4.0))
        ln = reed_len * (0.88 + 0.12 * ((_hash(seed, k, 2) % 4) / 3.0))
        dx, dy = math.cos(a) * lean, math.sin(a) * lean
        dz = math.sqrt(max(0.0, 1.0 - dx * dx - dy * dy))
        x0, y0 = cx + math.cos(a) * r * 0.12, cy + math.sin(a) * r * 0.12
        parts.append(_stick((x0, y0, top - h * 0.25), (x0 + dx * ln, y0 + dy * ln, top - h * 0.25 + dz * ln),
                            DIFFUSER["reed_r_m"], "wood", "reed"))
    return parts


def leaf(base, az: float, el0: float, length: float, width: float, droop: float, key: str = "green",
         role: str = "leaf") -> Part:
    """One leaf blade from ``base`` towards the compass angle ``az`` (radians, from +X), rising at ``el0`` and
    drooping by ``droop`` towards its tip; widest past its middle, the midrib folded up, ``LEAF["thickness_m"]``
    thick (a closed thin solid)."""
    segs, t = LEAF["segments"], LEAF["thickness_m"]
    side = (-math.sin(az), math.cos(az), 0.0)
    pts, x, y, z = [], float(base[0]), float(base[1]), float(base[2])
    ds = length / segs
    for k in range(segs + 1):
        u = k / segs
        el = el0 - droop * u
        d = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
        nrm = (d[1] * side[2] - d[2] * side[1], d[2] * side[0] - d[0] * side[2], d[0] * side[1] - d[1] * side[0])
        if nrm[2] < 0:
            nrm = tuple(-c for c in nrm)
        w = max(0.0006, width * math.sin(math.pi * min(1.0, 0.15 + 0.85 * u)) ** 0.7)
        pts.append(((x, y, z), w, nrm))
        x, y, z = x + d[0] * ds, y + d[1] * ds, z + d[2] * ds
    verts = []
    for (c, w, nrm) in pts:
        fold = LEAF["fold"] * w
        for sgn_t in (0.0, -1.0):                          # top surface, then the underside
            off = (nrm[0] * t * sgn_t, nrm[1] * t * sgn_t, nrm[2] * t * sgn_t)
            verts += [(c[0] + side[0] * w / 2 + off[0], c[1] + side[1] * w / 2 + off[1], c[2] + off[2]),
                      (c[0] + nrm[0] * fold + off[0], c[1] + nrm[1] * fold + off[1], c[2] + nrm[2] * fold + off[2]),
                      (c[0] - side[0] * w / 2 + off[0], c[1] - side[1] * w / 2 + off[1], c[2] + off[2])]
    faces, cents = [], []
    for k in range(segs):
        a, b = 6 * k, 6 * (k + 1)
        mid = tuple((pts[k][0][i] + pts[k + 1][0][i]) / 2.0 - pts[k][2][i] * t / 2.0 for i in range(3))
        for f in ([a, a + 1, b + 1, b], [a + 1, a + 2, b + 2, b + 1], [a + 3, b + 3, b + 4, a + 4],
                  [a + 4, b + 4, b + 5, a + 5], [a, b, b + 3, a + 3], [a + 2, a + 5, b + 5, b + 2]):
            faces.append(f)
            cents.append(mid)
    first = tuple(pts[0][0][i] + (pts[1][0][i] - pts[0][0][i]) / 2.0 for i in range(3))
    faces += [[0, 3, 4, 1], [1, 4, 5, 2]]
    cents += [first, first]
    e = 6 * segs
    last = tuple(pts[-1][0][i] - (pts[-1][0][i] - pts[-2][0][i]) / 2.0 for i in range(3))
    faces += [[e, e + 1, e + 4, e + 3], [e + 1, e + 2, e + 5, e + 4]]
    cents += [last, last]
    return {"verts": verts, "faces": _orient(verts, faces, cents), "key": key, "role": role, "smooth": True}


def _orient(verts, faces, cents) -> list[list[int]]:
    """Each face wound so its normal points away from its reference point (a thin solid's local middle)."""
    out = []
    for f, c in zip(faces, cents):
        a, b, cc = verts[f[0]], verts[f[1]], verts[f[2]]
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (cc[0] - a[0], cc[1] - a[1], cc[2] - a[2])
        nrm = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        fc = [sum(verts[i][k] for i in f) / len(f) for k in range(3)]
        out.append(f if sum(nrm[k] * (fc[k] - c[k]) for k in range(3)) >= 0 else f[::-1])
    return out


def potted_plant(cx: float, cy: float, z0: float, pot_r: float, pot_h: float, height: float, seed: int = 0,
                 pot_key: str = "ceramic", max_r: Optional[float] = None) -> list[Part]:
    """A ceramic pot with a rolled rim and its soil, a small leafy plant (``height`` over the floor in all, its leaves
    within ``max_r`` of its centre): leaf blades on short stems arching out round the pot, the inner ones upright."""
    pot = [(pot_r * 0.78, 0.0), (pot_r * 0.84, 0.004), (pot_r * 0.97, pot_h * 0.86), (pot_r, pot_h * 0.9),
           (pot_r, pot_h), (pot_r - 0.005, pot_h), (pot_r * 0.95 - 0.005, pot_h * 0.86)]
    parts = [lathe(cx, cy, z0, pot, pot_key, "pot"),
             P._cylinder_z(cx, cy, z0 + pot_h * 0.78, pot_r * 0.92, pot_r * 0.92, pot_h * 0.08, "dark", "soil", n=14)]
    foliage = max(0.04, height - pot_h)
    if max_r is not None:
        foliage = max(0.04, min(foliage, (max_r - pot_r * 0.2) / PLANT_REACH))
    n = 9
    for k in range(n):
        inner = k % 3 == 0
        az = 2 * math.pi * k / n + 0.35 * ((_hash(seed, k) % 5) / 4.0 - 0.5)
        stem_l = foliage * (0.35 if inner else 0.22)
        el = math.radians(78 if inner else 52)
        bx, by = cx + math.cos(az) * pot_r * 0.2, cy + math.sin(az) * pot_r * 0.2
        bz = z0 + pot_h * 0.84
        tip = (bx + math.cos(az) * math.cos(el) * stem_l, by + math.sin(az) * math.cos(el) * stem_l,
               bz + math.sin(el) * stem_l)
        parts.append(_stick((bx, by, bz), tip, 0.0015, "green", "stem"))
        ln = foliage * (0.62 if inner else 0.55) * (0.85 + 0.15 * ((_hash(seed, k, 3) % 4) / 3.0))
        wd = ln * 0.42
        parts.append(leaf(tip, az, math.radians(60 if inner else 32), ln, wd, math.radians(55 if inner else 70)))
    return parts


def perfume_bottle(cx: float, cy: float, z0: float, w: float, d: float, h: float, collar_key: str = "handle",
                   cap_key: str = "dark", liquid_key: str = "terracotta") -> list[Part]:
    """A thick glass flacon ``w x d`` and ``h`` high to its cap's top: the glass body with rounded edges, the scent
    inside it, a metal collar and a cap."""
    bh = h * 0.68
    parts = [P._superellipsoid(cx, cy, z0, w, d, bh, 0.25, 0.3, "glass", "perfume", n_eta=6, n_om=16),
             P._superellipsoid(cx, cy, z0 + 0.006, w - 0.012, d - 0.010, bh * 0.62, 0.3, 0.3, liquid_key, "liquid",
                               n_eta=6, n_om=16)]
    cr = min(w, d) * 0.16
    parts.append(lathe(cx, cy, z0 + bh - 0.002, [(cr, 0.0), (cr, h * 0.08), (cr * 0.6, h * 0.085)], collar_key,
                       "cap", smooth=False))
    ch = h - bh - h * 0.08
    if ch > 0.008:
        parts.append(P._superellipsoid(cx, cy, z0 + bh + h * 0.08, cr * 2.6, cr * 2.6, ch, 0.35, 0.35, cap_key, "cap",
                                       n_eta=6, n_om=12))
    return parts


def candle_glass(cx: float, cy: float, z0: float, r: float, h: float) -> list[Part]:
    """A candle poured in a glass tumbler: the glass, the wax a little under its rim, the wick."""
    g = JAR_GLASS_M
    shell = [(r - 0.003, 0.0), (r, 0.003), (r, h), (r - g, h), (r - g, g + 0.006), (r - g - 0.004, g + 0.004)]
    wax = h * 0.78
    return [lathe(cx, cy, z0, shell, "glass", "jar"),
            lathe(cx, cy, z0 + g + 0.004, [(r - g - 0.001, 0.0), (r - g - 0.001, wax - g - 0.006),
                                         (r * 0.3, wax - g - 0.004)], "ceramic", "candle"),
            P._cylinder_z(cx, cy, z0 + wax - 0.002, 0.0012, 0.0012, 0.010, "dark", "wick", n=6)]


def soap_dish(cx: float, cy: float, z0: float, r: float, key: str = "stone_light") -> list[Part]:
    """A shallow round stone dish (radius ``r``) with a bar of soap on it."""
    dish = [(r * 0.82, 0.0), (r * 0.9, 0.004), (r, 0.016), (r - 0.005, 0.018), (r * 0.80, 0.008),
            (r * 0.5, 0.006)]
    return [lathe(cx, cy, z0, dish, key, "dish", n=20),
            P._superellipsoid(cx, cy, z0 + 0.006, r * 1.25, r * 0.8, 0.022, 0.45, 0.55, "ceramic", "soap",
                              n_eta=6, n_om=16)]


def woven_basket(cx: float, cy: float, z0: float, w: float, d: float, h: float, towel_key: str = "towel",
                 key: str = "rattan") -> list[Part]:
    """A rounded-rectangular woven basket ``w x d`` (at most ``h`` high with its towels) with woven ribs round its
    sides and a rolled rim, two rolled towels lying in it, their tops over the rim."""
    a, b = w / 2.0 - 0.006, d / 2.0 - 0.006
    t = 0.006
    r = max(0.02, min(h * 0.5 - 0.004, d / 2.0 - 0.012, w / 4.6))
    hb = min(h, max(0.05, 2 * r * 0.6))                       # the rim well under the towels' tops
    body = [(a * 0.9, b * 0.9, 0.0), (a * 0.94, b * 0.94, 0.006)]
    ribs = max(3, int((hb - 0.02) / 0.018))
    for k in range(ribs):                                     # the weave's horizontal ribs: a bulge every rib
        f = (k + 0.5) / ribs
        z = 0.006 + (hb - 0.02) * f
        s = 0.94 + 0.06 * f
        body += [(a * s - 0.0015, b * s - 0.0015, z - 0.006), (a * s + 0.0015, b * s + 0.0015, z),
                 (a * s - 0.0015, b * s - 0.0015, z + 0.006)]
    body += [(a, b, hb - 0.014), (a + 0.005, b + 0.005, hb - 0.008), (a + 0.004, b + 0.004, hb),
             (a - t, b - t, hb), (a - t, b - t, t + 0.004), (a * 0.9 - t, b * 0.9 - t, t)]
    parts = [_ring_loft(cx, cy, z0, body, key, "basket")]
    length = max(0.05, d - 0.03)
    for k, sx in enumerate((-1.0, 1.0)):
        parts.append(TP.rolled_towel(cx + sx * (r + 0.003), cy, z0 + t, r, length,
                                     towel_key if k == 0 else TP.alt_key(towel_key), "y", 7 + k))
    return parts


def cotton_stem(base, direction, length: float, seed: int = 0) -> list[Part]:
    """A dried cotton branch from ``base`` along the unit ``direction``: its stem and a boll at its tip (a dark calyx
    and three white puffs)."""
    ux, uy, uz = direction
    tip = (base[0] + ux * length, base[1] + uy * length, base[2] + uz * length)
    parts = [_stick(base, tip, 0.0016, "wood", "stem")]
    parts.append(_blob(tip[0], tip[1], tip[2] - 0.006, 0.016, 0.016, 0.010, "dark", "calyx", e=0.7))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4 * (_hash(seed, k) % 3)
        parts.append(_blob(tip[0] + math.cos(a) * 0.007, tip[1] + math.sin(a) * 0.007, tip[2] - 0.002, 0.017, 0.016,
                           0.016, "bedding", "cotton", e=1.0))
    return parts


# --------------------------------------------------------------------------
# the WC's dual-flush plate (lesson UL168)
# --------------------------------------------------------------------------

# 30 Oct 2026 (lesson UL168, user on the same bathroom: "These switches requires a rework": the flush plate read as a
# black picture frame with two flat white panes): a real dual-flush actuator plate (the Geberit Sigma size, 246 x 164
# mm, 8 mm proud): a slim plate with rounded corners and a chamfered front edge, a small (half-flush) and a large
# (full-flush) button side by side with a fine shadow gap round each, the buttons a little proud and pillowed, a fine
# line on each (one on the small, two on the large), all in the room's fixture finish
FLUSH = {"size_m": (0.246, 0.164), "proud_m": 0.008, "corner_r_m": 0.008, "chamfer_m": 0.0015, "border_m": 0.018,
         "button_gap_m": 0.004, "small_share": 0.38, "button_proud_m": 0.0015, "button_r_m": 0.004,
         "shadow_m": 0.0009, "line_m": (0.0012, 0.0005)}


def rounded_rect(a: float, b: float, rc: float, n: int = 4) -> list[tuple[float, float]]:
    """A counter-clockwise rounded rectangle (half sizes ``a`` x ``b``, corner radius ``rc``) in a plane ``(u, v)``."""
    rc = max(1e-4, min(rc, a - 1e-5, b - 1e-5))
    out = []
    for (sx, sy, a0) in ((1, -1, -0.5 * math.pi), (1, 1, 0.0), (-1, 1, 0.5 * math.pi), (-1, -1, math.pi)):
        ccx, ccy = sx * (a - rc), sy * (b - rc)
        out += [(ccx + rc * math.cos(a0 + 0.5 * math.pi * k / n), ccy + rc * math.sin(a0 + 0.5 * math.pi * k / n))
                for k in range(n + 1)]
    return out


def wall_slab(cx: float, y_back: float, zc: float, a: float, b: float, rc: float,
              rings: Sequence[tuple[float, float]], key: str, role: str, n: int = 4) -> Part:
    """A slab on a wall (its back on ``y_back``, standing out towards -Y): rounded-rectangle rings ``(inset, depth)``
    (an inset of the half sizes and the radius, the depth from ``y_back``), closed at its back and its front; the
    front face (-Y) and the sides wound outwards."""
    verts = []
    for inset, depth in rings:
        verts += [(cx + u, y_back - depth, zc + v) for u, v in rounded_rect(a - inset, b - inset, rc - inset, n)]
    m = 4 * (n + 1)
    faces = []
    for k in range(len(rings) - 1):
        p, q = k * m, (k + 1) * m
        faces += [[p + i, p + (i + 1) % m, q + (i + 1) % m, q + i] for i in range(m)]
    faces.append(list(range(m - 1, -1, -1)))                     # the back, towards the wall (+Y)
    last = (len(rings) - 1) * m
    faces.append([last + i for i in range(m)])                    # the front (-Y)
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def flush_plate(cx: float, y_wall: float, z_bottom: float, finish_key: str = "handle",
                button_key: Optional[str] = None, line_key: str = "steel", shadow_key: str = "dark") -> list[Part]:
    """The dual-flush plate on the wall at ``y_wall`` (its bottom at ``z_bottom``): the plate (first part, role
    ``plate``), the shadow gaps, the two buttons (role ``button``: small left, large right) and their lines."""
    (pw, ph), t = FLUSH["size_m"], FLUSH["proud_m"]
    a, b = pw / 2.0, ph / 2.0
    zc = z_bottom + b
    c = FLUSH["chamfer_m"]
    parts = [wall_slab(cx, y_wall, zc, a, b, FLUSH["corner_r_m"], [(0.0, 0.0), (0.0, t - c), (c, t)], finish_key,
                       "plate")]
    bk = button_key or finish_key
    inner_w, inner_h = pw - 2 * FLUSH["border_m"], ph - 2 * FLUSH["border_m"]
    g = FLUSH["button_gap_m"]
    ws = (inner_w - g) * FLUSH["small_share"]
    wl = inner_w - g - ws
    x_s = cx - inner_w / 2.0 + ws / 2.0
    x_l = cx + inner_w / 2.0 - wl / 2.0
    front = y_wall - t
    bp, rb, sh = FLUSH["button_proud_m"], FLUSH["button_r_m"], FLUSH["shadow_m"]
    lh, lp = FLUSH["line_m"]
    for k, (x, w) in enumerate(((x_s, ws), (x_l, wl))):
        ba, bb = w / 2.0, inner_h / 2.0
        parts.append(wall_slab(x, front + 0.001, zc, ba + sh, bb + sh, rb + sh, [(0.0, 0.0), (0.0, 0.0013)],
                               shadow_key, "gap"))
        parts.append(wall_slab(x, front + 0.001, zc, ba, bb, rb, [(0.0, 0.0), (0.0, 0.001 + bp * 0.7),
                                                                   (0.0012, 0.001 + bp)], bk, "button"))
        for j in range(k + 1):                                   # one line on the small button, two on the large
            lw = w * (0.30 if k == 0 else 0.22)
            lx = x if k == 0 else x + (j - 0.5) * lw * 1.5
            parts.append(wall_slab(lx, front - bp + 0.0004, zc, lw / 2.0, lh / 2.0, lh / 2.0 - 1e-5,
                                   [(0.0, 0.0), (0.0, lp + 0.0004)], line_key, "symbol", n=2))
    return parts
