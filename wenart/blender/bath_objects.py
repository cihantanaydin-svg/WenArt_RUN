"""The bathroom's styled objects as real products (30 Oct 2026, lesson UL166, user on a bathroom of real04 run
20261030-043021-full: "Here models needs more details": the lit shelf column held a glass box with two black squares
(the perfume), a few pebbles in an invisible jar, three sticks with white balls (the cotton stems), a green egg in a
white cylinder (the plant)). Pure (no ``bpy``): vertex and face lists the bathroom parts (``bath_parts``) put into
their host's one mesh (lesson UL111).

31 Oct 2026 (user on real04 run 20261030-181158-full, a bathroom's open shelf column: "This little items needs a lot
better models, check the library of similar things exist to use if not create them with better texture and more
detailed way"; the render showed two cube-shaped bottles with black pump heads, a ribbed plastic-looking bowl for the
towel basket, cotton balls as plain white spheres, a soap dish, a reed diffuser and a lidded jar): two rules for every
small item of a bathroom host (a column's cubbies, a vanity's top and shelves, a towel shelf, an installation wall's
niches), general for every project:

1. The library first (``wenart.furniture.small_items``): an audited library model of the item's kind that is rated
   good and fits the item's reserved box takes its place; the builders then leave a *library slot* (``placed``,
   ``slot_part``: the reserved box, no faces) that the build fills with the model (``furniture.place_slot_models``).
2. Else our model, now with the details of the real product (designer sizes of real products, assumed), every part
   in a real material (``SMALL_ITEM_KEYS``: solid glass with refraction in clear, frosted, amber or smoke; the liquids
   inside; fluffy cotton wool; a waxy soap; a speckled stoneware glaze; rattan cane and reeds):

- ``pump_bottle``: a glass bottle with its wall, a thick base and the soap gel inside (its meniscus), the dip tube, a
  knurled screw collar, the pump's stem with its lock ring, a rounded actuator and a round nozzle bent down at its tip
  with its opening, a printed paper label on its front (a brand line, text lines, a rule and a mark); an opaque black
  or white bottle keeps the same pump.
- ``perfume_bottle``: a flacon of thick glass (a heavy base, soft chamfered edges, a rounded-rectangle or oval body),
  the scent inside it with the dip tube, a neck with a crimped metal collar, the spray actuator with its nozzle hole
  and a cap (a rounded block or a turned cap), never a glass cube with a black square.
- ``apothecary_jar``: a glass jar with a thick base, a shoulder and a beaded rim, a silicone seal, a wooden lid with
  its grain and a turned knob, filled with fluffy cotton balls (each a lumpy ball in cotton wool, packed in layers),
  cotton pads, pebbles or bath salt.
- ``reed_diffuser``: a glass bottle with the oil inside, a metal collar and ``DIFFUSER["reeds"]`` thin round reeds
  standing in the oil and fanning out, each a little curved, a label.
- ``potted_plant``: a stoneware pot with a foot and a rolled rim, its soil with a top dressing of pebbles and a small
  leafy plant: leaf blades on short stems, arched out and drooping at their tips (``leaf``), the midrib folded.
- ``candle_glass``: a candle poured in a tinted glass tumbler with a thick base: the wax with its melt pool, the wick
  with its charred tip.
- ``soap_dish``: an oval stoneware dish on a foot ring with drainage ribs, a bar of soap with rounded edges and its
  pressed mark.
- ``woven_basket``: a real wicker basket: a woven base, upright stakes and weavers passing over and under them row by
  row, a braided rim, two cane handles, two rolled towels in it.
- ``cotton_stem``: a dried cotton branch: a stem, a dark calyx and three fluffy puffs per boll.

The material keys are the parametric ones (``parametric.MATERIAL_KEYS``): ``SMALL_ITEM_KEYS`` above, ``glass``,
``ceramic`` (glazed white), ``dark`` (black lacquer), ``wood``, ``rattan`` (the Wicker005 photo), ``bedding`` (white
cotton), ``green``, ``stone_light`` (marble), ``worktop`` (dark stone), ``steel``, ``paper`` and ``handle`` (the room's
fixture finish on a piece). Round parts are ``"smooth": True`` (the build shades them smooth, ``furniture.add_bevel``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import parametric as P
from wenart.blender import towel_parts as TP

Part = dict
LESSON = "UL166"
RULE = "small_items (31 Oct 2026)"
LATHE_N = 24                      # segments round a turned object (31 Oct 2026: 12 showed facets on a 7 cm bottle)
JAR_FILL = {"layers": 3, "pads": 7}   # a jar shows three layers of cotton balls (the rest is unseen)
DIFFUSER = {"reeds": 9, "reed_r_m": 0.0016, "spread": 0.30}
PUMP = {"stem_share": 0.06, "head_share": 0.085, "collar_share": 0.085, "nozzle_share": 0.95}
JAR_GLASS_M = 0.003               # an apothecary jar's wall
GLASS_WALL_M = 0.0025             # a bottle's wall
GLASS_BASE_M = 0.006              # ... and its thick base (the glass floor)
LEAF = {"segments": 7, "thickness_m": 0.0012, "fold": 0.18}
JAR_LID_M = 0.027                 # an apothecary jar's lid and knob over its rim
PLANT_REACH = 0.68                # a potted plant's leaves reach this share of its foliage height from its centre
FLUFF = 0.22                      # a cotton ball's lumps: this share of its radius at most
COTTON_STRETCH = 1.12             # ... and drawn out by up to this along its own direction
WEAVE = {"stake_pitch_m": 0.022, "row_pitch_m": 0.007, "stake_r_m": 0.0022, "weaver_t_m": 0.0017,
         "weave_in_m": 0.0031, "base_t_m": 0.007, "rim_r_m": 0.0034, "rim_turns_per_m": 22.0, "handle_r_m": 0.0035}

# 31 Oct 2026: the small items' own material keys (= parametric.SMALL_ITEM_KEYS; furniture.style_material_keys gives
# their slugs, materials.MaterialLibrary.small_item their looks)
GLASS = {"clear": "bottle_glass", "frosted": "frosted_glass", "amber": "amber_glass", "smoke": "smoke_glass"}
SCENT_KEY, SOAP_GEL_KEY, DIFFUSER_OIL_KEY = "scent", "soap_gel", "diffuser_oil"
COTTON_KEY, SOAP_KEY, STONEWARE_KEY, REED_KEY, CANE_KEY = "cotton_wool", "soap", "stoneware", "reed", "cane"
LEAF_KEY = "foliage"              # a glossy leaf, its greens varying (the flat plant green read as pastel card)
SMALL_ITEM_KEYS: tuple[str, ...] = tuple(GLASS.values()) + (SCENT_KEY, SOAP_GEL_KEY, DIFFUSER_OIL_KEY, COTTON_KEY,
                                                            SOAP_KEY, STONEWARE_KEY, REED_KEY, CANE_KEY, LEAF_KEY)
# ... their slugs (wenart.style.vocabulary.FURNITURE_MATERIALS; the records name them)
SLUGS: dict[str, str] = {"bottle_glass": "glass_bottle_clear", "frosted_glass": "glass_bottle_frosted",
                         "amber_glass": "glass_bottle_amber", "smoke_glass": "glass_bottle_smoke",
                         "scent": "liquid_scent", "soap_gel": "liquid_soap", "diffuser_oil": "liquid_diffuser",
                         "cotton_wool": "cotton_wool", "soap": "soap_bar", "stoneware": "stoneware_speckled",
                         "reed": "rattan_reed", "cane": "rattan_cane", "foliage": "plant_leaf"}
# a bottle's body key -> its glass (the older keys of the callers: terracotta was the amber bottle)
_GLASS_OF = {"terracotta": GLASS["amber"], "amber": GLASS["amber"], "glass": GLASS["clear"], "clear": GLASS["clear"],
             "frosted": GLASS["frosted"], "smoke": GLASS["smoke"], **{v: v for v in GLASS.values()}}

# --------------------------------------------------------------------------
# 31 Oct 2026: the library slots (the library first, module docstring rule 1)
# --------------------------------------------------------------------------

# the kinds of small item a library model may stand in for (the towels keep the room's accent colour, B26, and the
# vase of dried stems is ours by design, UL115: neither is a kind)
# (a vanity's stone tray neither: the soap and the jar stand on its floor)
SMALL_ITEM_KINDS: tuple[str, ...] = ("pump_bottle", "perfume_bottle", "apothecary_jar", "reed_diffuser",
                                     "potted_plant", "candle_glass", "soap_dish", "woven_basket")
SLOT_ROLE = "library_slot"        # = parametric.SLOT_ROLE: a part with no faces, its 8 vertices the reserved box
SLOT_KEY = "slot"


class _Every(dict):
    """A picks mapping that holds every kind (``ALL``): the builders then leave a slot for every small item, so the
    fit can read each host's reserved boxes (``parametric.library_slots``) before it picks."""

    def get(self, key, default=None):
        return {"asset_id": None} if key in SMALL_ITEM_KINDS else default

    def __contains__(self, key) -> bool:
        return key in SMALL_ITEM_KINDS


ALL = _Every()


def picks_of(record) -> dict:
    """The ``{kind: asset}`` picks of a host's ``small_items`` record (``wenart.furniture.small_items``), of a plain
    mapping of picks, or ``ALL``; {} for anything else."""
    if record is ALL:
        return ALL
    if isinstance(record, dict) and isinstance(record.get("picks"), dict):
        return {k: v for k, v in record["picks"].items() if isinstance(v, dict) and k in SMALL_ITEM_KINDS}
    if isinstance(record, dict):
        return {k: v for k, v in record.items() if isinstance(v, dict) and k in SMALL_ITEM_KINDS}
    return {}


def slot_part(kind: str, parts: Sequence[Part], pick: Optional[dict] = None) -> Part:
    """A library slot over the box of an item's parts: its 8 corners and no faces (``parametric.world_mesh`` leaves it
    out of the host's mesh; every move of the host's parts moves it too), the kind and the picked asset's id."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    verts = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    return {"verts": verts, "faces": [], "key": SLOT_KEY, "role": SLOT_ROLE,
            "slot": {"kind": kind, "asset_id": (pick or {}).get("asset_id")}}


def placed(kind: str, parts: list[Part], picks=None) -> list[Part]:
    """The parts of one small item of ``kind``, or (when ``picks`` hold a library model of that kind) its library slot
    in their place."""
    pick = picks.get(kind) if isinstance(picks, dict) else None
    if pick is None or not parts:
        return parts
    return [slot_part(kind, parts, pick)]


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def _signed_volume(part: Part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def _outward(part: Part) -> Part:
    if _signed_volume(part) < 0.0:
        part["faces"] = [list(reversed(f)) for f in part["faces"]]
    return part


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


def _r_at(out: Sequence[tuple[float, float]], z: float) -> float:
    """The radius of the profile ``out`` (rings ``(r, z)`` from the bottom up) at the height ``z`` (linear)."""
    for (r0, z0), (r1, z1) in zip(out, out[1:]):
        if z0 - 1e-9 <= z <= z1 + 1e-9 and z1 > z0:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return out[-1][0] if z > out[-1][1] else out[0][0]


def _vessel(cx: float, cy: float, z0: float, out: Sequence[tuple[float, float]], wall: float, floor: float, key: str,
            role: str, n: int = LATHE_N) -> Part:
    """An open turned vessel (glass or a glazed pot with its thickness): the outer profile ``out`` from its foot up to
    its rim, over a rounded lip and down its inside ``wall`` thick (following the outside) to a floor ``floor`` over
    its bottom (a thick base) with a rounded inner corner."""
    top_r, top_z = out[-1]
    prof = list(out) + [(top_r - wall * 0.5, top_z + wall * 0.3)]
    zc = floor + 0.003
    inner = [(max(r - wall, 0.002), z) for r, z in reversed(out[1:]) if z > zc + 1e-6]
    rf = max(_r_at(out, zc) - wall, 0.002)
    prof += inner + [(rf, zc), (rf * 0.97, floor + 0.0011), (rf * 0.90, floor + 0.0002), (max(rf * 0.3, 0.001), floor)]
    return _outward(lathe(cx, cy, z0, prof, key, role, n=n))


def _fill_turned(cx: float, cy: float, z0: float, out: Sequence[tuple[float, float]], wall: float, floor: float,
                 level: float, key: str, role: str, meniscus: bool = True, gap: float = 0.0005,
                 n: int = LATHE_N) -> Part:
    """What fills a ``_vessel`` of the same ``out``, ``wall`` and ``floor`` up to ``level`` (over its bottom): a solid
    ``gap`` inside its inner wall and floor (a liquid with its meniscus climbing the glass, ``meniscus``; else a flat
    top: soil, wax)."""
    zc = floor + 0.003
    rf = max(_r_at(out, zc) - wall - gap, 0.002)
    prof = [(rf * 0.88, floor + gap), (rf * 0.97, floor + 0.0013), (rf, zc)]
    prof += [(max(r - wall - gap, 0.002), z) for r, z in out if zc + 1e-6 < z < level - 0.002]
    rl = max(_r_at(out, level) - wall - gap, 0.002)
    prof.append((rl, level))
    if meniscus:
        prof += [(rl - 0.0018, level - 0.0010), (rl * 0.45, level - 0.0014)]
    else:
        prof += [(rl * 0.96, level + 0.0006), (rl * 0.4, level + 0.0008)]
    return _outward(lathe(cx, cy, z0, prof, key, role, n=n))


def _loft(cx: float, cy: float, z0: float, rings: Sequence[tuple[float, float, float, float]], key: str, role: str,
          n: int = 32, smooth: bool = True) -> Part:
    """A lofted solid of superellipse rings ``(a, b, z, power)`` (half width, half depth, height; power 2: an
    ellipse, 4-6: a rounded rectangle; a ring's power may differ from the next one's: a flacon's square body into its
    round neck), the first ring closed downwards and the last upwards (as ``lathe``; an open vessel's rings go up its
    outside and down its inside)."""
    verts = []
    for a, b, z, pw in rings:
        e = 2.0 / max(float(pw), 1e-3)
        for i in range(n):
            t = 2 * math.pi * i / n
            c, s = math.cos(t), math.sin(t)
            verts.append((cx + a * math.copysign(abs(c) ** e, c), cy + b * math.copysign(abs(s) ** e, s), z0 + z))
    faces = []
    for k in range(len(rings) - 1):
        p, q = k * n, (k + 1) * n
        faces += [[p + i, p + (i + 1) % n, q + (i + 1) % n, q + i] for i in range(n)]
    faces.append(list(range(n - 1, -1, -1)))
    last = (len(rings) - 1) * n
    faces.append([last + i for i in range(n)])
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": smooth})


def _ring_loft(cx: float, cy: float, z0: float, rings: Sequence[tuple[float, float, float]], key: str, role: str,
               power: float = 4.0, n: int = 24, smooth: bool = True) -> Part:
    """A lofted solid of superellipse rings ``(a, b, z)`` of one ``power`` (``_loft``)."""
    return _loft(cx, cy, z0, [(a, b, z, power) for a, b, z in rings], key, role, n=n, smooth=smooth)


def _ribbed(cx: float, cy: float, z0: float, r: float, h: float, ribs: int, depth: float, key: str, role: str,
            chamfer: float = 0.0006) -> Part:
    """A short cylinder with ``ribs`` vertical ribs round it (a knurled screw collar, a crimped neck ring): rings of
    ``2 * ribs`` points alternately on ``r`` and ``r - depth``, the edges chamfered, closed at both ends."""
    m = 2 * ribs
    chamfer = min(chamfer, h / 3.0)
    verts = []
    for z, f in ((0.0, 1.0 - chamfer / r), (chamfer, 1.0), (h - chamfer, 1.0), (h, 1.0 - chamfer / r)):
        for i in range(m):
            t = math.pi * i / ribs
            rr = (r if i % 2 == 0 else r - depth) * f
            verts.append((cx + rr * math.cos(t), cy + rr * math.sin(t), z0 + z))
    faces = []
    for k in range(3):
        p, q = k * m, (k + 1) * m
        faces += [[p + i, p + (i + 1) % m, q + (i + 1) % m, q + i] for i in range(m)]
    faces += [list(range(m - 1, -1, -1)), [3 * m + i for i in range(m)]]
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": False})


def _frame(t):
    up = (0.0, 0.0, 1.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
    e1 = (t[1] * up[2] - t[2] * up[1], t[2] * up[0] - t[0] * up[2], t[0] * up[1] - t[1] * up[0])
    m = math.sqrt(sum(c * c for c in e1)) or 1e-9
    e1 = tuple(c / m for c in e1)
    e2 = (t[1] * e1[2] - t[2] * e1[1], t[2] * e1[0] - t[0] * e1[2], t[0] * e1[1] - t[1] * e1[0])
    return e1, e2


def _tube(points: Sequence[Sequence[float]], radii, key: str, role: str, sides: int = 6, loop: bool = False,
          r_up=None) -> Part:
    """A tube along the 3D polyline ``points`` (a reed, a stake, a handle), ``radii`` one per point or one value;
    ``r_up`` (one value or one per point) its half height along the second frame vector (a flat weaver: wide upright,
    thin across); ``loop``: the last ring joined to the first (a weaver round the basket, a rim), else both ends
    capped. Closed and wound outwards."""
    pts = [tuple(float(v) for v in p) for p in points]
    n = len(pts)
    rs = list(radii) if isinstance(radii, (list, tuple)) else [float(radii)] * n
    ups = (list(r_up) if isinstance(r_up, (list, tuple)) else [float(r_up)] * n) if r_up is not None else rs
    verts, prev = [], None
    for k, p in enumerate(pts):
        a = pts[(k - 1) % n] if loop else pts[max(0, k - 1)]
        b = pts[(k + 1) % n] if loop else pts[min(n - 1, k + 1)]
        d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ln = math.sqrt(sum(c * c for c in d)) or 1e-9
        e1, e2 = _frame(tuple(c / ln for c in d))
        if prev is not None and sum(x * y for x, y in zip(e1, prev)) < 0.0:
            e1, e2 = tuple(-c for c in e1), tuple(-c for c in e2)
        prev = e1
        for i in range(sides):
            ang = 2 * math.pi * i / sides
            ca, sa = math.cos(ang) * max(rs[k], 1e-5), math.sin(ang) * max(ups[k], 1e-5)
            verts.append((p[0] + e1[0] * ca + e2[0] * sa, p[1] + e1[1] * ca + e2[1] * sa,
                          p[2] + e1[2] * ca + e2[2] * sa))
    faces = []
    for k in range(n if loop else n - 1):
        a, b = k * sides, ((k + 1) % n) * sides
        faces += [[a + i, a + (i + 1) % sides, b + (i + 1) % sides, b + i] for i in range(sides)]
    if not loop:
        faces += [list(range(sides - 1, -1, -1)), [(n - 1) * sides + i for i in range(sides)]]
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True})


def _stick(p0, p1, r: float, key: str, role: str) -> Part:
    """A thin round rod from ``p0`` to ``p1`` (3D points; a stem), wound outwards."""
    return _tube([p0, p1], r, key, role, sides=6)


def _blob(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str, e: float = 1.0,
          n_eta: int = 4, n_om: int = 8) -> Part:
    return P._superellipsoid(cx, cy, z0, w, d, h, e, e, key, role, n_eta=n_eta, n_om=n_om)


def _hash(*v: int) -> int:
    h = 2166136261
    for x in v:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _unit(seed: int, *k: int) -> float:
    """A deterministic number in [0, 1) of ``seed`` and ``k``."""
    return (_hash(seed, *k) % 10007) / 10007.0


def _lumpy(cx: float, cy: float, z0: float, r: float, seed: int, key: str, role: str, amp: float = FLUFF,
           lat: int = 7, lon: int = 14, squash: float = 0.9, freq: tuple[int, int, int] = (2, 3, 5),
           stretch: float = 1.0, fine: float = 0.0) -> Part:
    """A lumpy ball of radius ``r`` (at most ``r * (1 + amp) * stretch`` from its centre) resting on ``z0``: a sphere
    of ``lat`` x ``lon`` facets whose radius varies by three waves of seeded phases (a cotton ball's fluff, a pebble's
    shape) and, with ``fine``, two short waves of small tufts on them, a little squashed (``squash``), drawn out along
    a seeded direction by up to ``stretch`` (and pressed in across it), closed and wound outwards."""
    ph = [2 * math.pi * _unit(seed, k) for k in range(10)]
    f1, f2, f3 = freq
    sx = 1.0 + (stretch - 1.0) * (0.4 + 0.6 * _unit(seed, 7))
    ang = 2 * math.pi * _unit(seed, 8)
    ca, sa = math.cos(ang), math.sin(ang)

    def rad(theta: float, phi: float) -> float:
        n = (0.5 * math.sin(f1 * phi + ph[0]) * math.sin(f1 * theta + ph[1])
             + 0.3 * math.sin(f2 * phi + ph[2] + theta) * math.cos(f2 * theta + ph[3])
             + 0.2 * math.sin(f3 * phi + ph[4]) * math.sin(f3 * theta + ph[5]))
        n = max(-1.0, min(1.0, n)) * (1.0 - fine)
        if fine:
            n += fine * (0.6 * math.sin(11 * phi + ph[6]) * math.sin(9 * theta + ph[7])
                         + 0.4 * math.sin(17 * phi + ph[8] + 2 * theta) * math.sin(13 * theta + ph[9]))
        return r * (1.0 + amp * max(-1.0, min(1.0, n)))

    def shape(x: float, y: float, z: float) -> tuple[float, float, float]:
        u, v = x * ca + y * sa, -x * sa + y * ca             # into the stretch's frame, drawn out along u
        u, v = u * sx, v / math.sqrt(sx)
        return (u * ca - v * sa, u * sa + v * ca, z * squash)

    pts = [shape(0.0, 0.0, rad(0.0, 0.0))]
    for i in range(1, lat):
        th = math.pi * i / lat
        for j in range(lon):
            ph_ = 2 * math.pi * j / lon
            rr = rad(th, ph_)
            pts.append(shape(rr * math.sin(th) * math.cos(ph_), rr * math.sin(th) * math.sin(ph_), rr * math.cos(th)))
    pts.append(shape(0.0, 0.0, -rad(math.pi, 0.0)))
    bottom = min(p[2] for p in pts)
    verts = [(cx + x, cy + y, z0 + z - bottom) for x, y, z in pts]
    last = len(verts) - 1
    faces = [[0, 1 + (j + 1) % lon, 1 + j] for j in range(lon)]
    for i in range(lat - 2):
        a, b = 1 + i * lon, 1 + (i + 1) * lon
        faces += [[a + j, a + (j + 1) % lon, b + (j + 1) % lon, b + j] for j in range(lon)]
    base = 1 + (lat - 2) * lon
    faces += [[last, base + j, base + (j + 1) % lon] for j in range(lon)]
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True})


def _patch(cx: float, cy: float, r0: float, za: float, zb: float, deg: float, key: str, role: str, t: float,
           n: int = 8, centre_deg: float = -90.0) -> Part:
    """A thin curved patch ``t`` thick on a round body of radius ``r0`` from ``za`` to ``zb`` over ``deg`` degrees
    round the front (``centre_deg`` -90: towards -Y), closed."""
    a0 = math.radians(centre_deg - deg / 2.0)
    ring = [a0 + math.radians(deg) * i / n for i in range(n + 1)]
    outer = [(cx + (r0 + t) * math.cos(a), cy + (r0 + t) * math.sin(a)) for a in ring]
    inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)) for a in reversed(ring)]
    loop = outer + inner
    m = len(loop)
    verts = [(x, y, za) for x, y in loop] + [(x, y, zb) for x, y in loop]
    faces = [list(range(m - 1, -1, -1)), [m + i for i in range(m)]] + \
        [[i, (i + 1) % m, m + (i + 1) % m, m + i] for i in range(m)]
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role})


def label(cx: float, cy: float, z0: float, r: float, z_lo: float, z_hi: float, key: str = "paper",
          ink: str = "dark", arc_deg: float = 105.0) -> list[Part]:
    """A printed label on the front (-Y) of a round body of radius ``r``: the paper (``label``) from ``z_lo`` to
    ``z_hi`` over ``arc_deg`` of its round, and its print (``print``): a brand line, a fine rule, two text lines, the
    size line at its foot and a small round mark over the brand."""
    hgt = z_hi - z_lo
    za = z0 + z_lo
    parts = [_patch(cx, cy, r, za, z0 + z_hi, arc_deg, key, "label", 0.0005)]
    rp = r + 0.0005
    # 31 Oct 2026 (the smoke render read solid bars as print): each line is a row of words with gaps between them,
    # centred (the brand in a few heavier words, the text lines lighter), so the label reads as type from a metre
    for f0, f1, share, words in ((0.58, 0.68, 0.60, (0.42, 0.58)), (0.505, 0.512, 0.70, (1.0,)),
                                 (0.40, 0.435, 0.62, (0.28, 0.16, 0.34, 0.22)), (0.33, 0.365, 0.52, (0.36, 0.24, 0.40)),
                                 (0.11, 0.145, 0.30, (0.45, 0.55))):
        span = arc_deg * share
        gap = span * 0.06 if len(words) > 1 else 0.0
        total = sum(words)
        a = -90.0 - span / 2.0
        for wd in words:
            deg = (span - gap * (len(words) - 1)) * wd / total
            parts.append(_patch(cx, cy, rp, za + hgt * f0, za + hgt * f1, deg, ink, "print", 0.0002, n=2,
                                centre_deg=a + deg / 2.0))
            a += deg + gap
    m = min(0.004, hgt * 0.06)                                 # the mark: a small dot over the brand line
    parts.append(_patch(cx, cy, rp, za + hgt * 0.76, za + hgt * 0.76 + 2 * m, math.degrees(2 * m / max(r, 1e-6)),
                        ink, "print", 0.0002, n=2))
    return parts


def _glass_of(key: str) -> Optional[str]:
    return _GLASS_OF.get(key)


# --------------------------------------------------------------------------
# the products
# --------------------------------------------------------------------------

def pump_bottle(cx: float, cy: float, z0: float, r: float, h: float, key: str, head_key: str = "dark",
                label_key: Optional[str] = None) -> list[Part]:
    """A pump bottle ``h`` high (to the actuator's top), radius ``r``; ``key`` its body: a glass (``terracotta`` or
    ``amber``, ``clear``, ``frosted``, ``smoke``: the glass with its wall and thick base, the soap gel inside and the
    dip tube) or an opaque body (``dark``, ``ceramic``, ``stoneware``); the knurled collar, the stem with its lock
    ring, the actuator and the nozzle forward (-Y) bent down at its tip, in ``head_key``; a printed label
    (``label_key``; paper by default, black print, white print on a dark label)."""
    hs, hh, hc = PUMP["stem_share"] * h, PUMP["head_share"] * h, PUMP["collar_share"] * h
    bh = h - hs - hh - hc * 0.5                                         # the body to the neck's top
    out = [(r * 0.86, 0.0), (r * 0.95, 0.0015), (r * 0.99, 0.004), (r, 0.008), (r, bh * 0.70), (r * 0.985, bh * 0.76),
           (r * 0.94, bh * 0.82), (r * 0.84, bh * 0.87), (r * 0.66, bh * 0.915), (r * 0.48, bh * 0.95),
           (r * 0.40, bh * 0.975), (r * 0.39, bh)]
    glass = _glass_of(key)
    if glass:
        parts = [_vessel(cx, cy, z0, out, GLASS_WALL_M, GLASS_BASE_M, glass, "bottle")]
        parts.append(_fill_turned(cx, cy, z0, out, GLASS_WALL_M, GLASS_BASE_M, bh * 0.64, SOAP_GEL_KEY, "contents"))
        parts.append(P._cylinder_z(cx, cy, z0 + GLASS_BASE_M + 0.001, 0.0017, 0.0017, bh - GLASS_BASE_M, GLASS["clear"],
                                   "tube", n=8))
    else:
        parts = [_outward(lathe(cx, cy, z0, out, key, "bottle"))]
    # the knurled screw collar over the neck, a lock ring on the stem, the stem
    cz = z0 + bh - hc * 0.5
    parts.append(_ribbed(cx, cy, cz, r * 0.47, hc, 18, r * 0.025, head_key, "cap"))
    sz = cz + hc
    parts.append(_outward(lathe(cx, cy, sz, [(r * 0.20, 0.0), (r * 0.20, hs * 0.22), (r * 0.12, hs * 0.30)], head_key,
                                "pump", n=16)))
    parts.append(P._cylinder_z(cx, cy, sz, r * 0.11, r * 0.11, hs + 0.001, head_key, "pump", n=12))
    # the actuator: a flat top with a rounded edge
    head = [(r * 0.30, 0.0), (r * 0.34, hh * 0.12), (r * 0.355, hh * 0.30), (r * 0.355, hh * 0.70),
            (r * 0.335, hh * 0.86), (r * 0.28, hh * 0.96), (r * 0.15, hh), (0.0004, hh)]
    parts.append(_outward(lathe(cx, cy, sz + hs, head, head_key, "pump")))
    # the nozzle: a round spout forward (-Y), its tip turned down, a dark opening at its end
    nl = PUMP["nozzle_share"] * r
    nz = sz + hs + hh * 0.55
    nr = max(0.0024, r * 0.085)
    parts.append(_tube([(cx, cy - r * 0.2, nz), (cx, cy - nl * 0.70, nz), (cx, cy - nl * 0.90, nz - nr * 0.5),
                        (cx, cy - nl, nz - nr * 1.8), (cx, cy - nl, nz - nr * 3.0)], nr, head_key, "nozzle", sides=10))
    parts.append(P._cylinder_z(cx, cy - nl, nz - nr * 3.0 - 0.0006, nr * 0.55, nr * 0.55, 0.0008, "dark", "nozzle",
                               n=10))
    lk = label_key if label_key in ("paper", "ceramic", "dark") else "paper"
    ink = "ceramic" if lk == "dark" else "dark"
    parts += label(cx, cy, z0, r, bh * 0.28, bh * 0.62, lk, ink)
    return parts


def apothecary_jar(cx: float, cy: float, z0: float, r: float, h: float, lid_key: str = "wood",
                   fill: str = "cotton", seed: int = 0, glass: str = GLASS["clear"]) -> list[Part]:
    """A glass jar ``h`` high to its rim, radius ``r`` (a thick base, a shoulder, a beaded rim), its silicone seal,
    lid and knob on top (``JAR_LID_M`` more), ``fill``: ``cotton`` (fluffy balls), ``pads`` (cotton pads),
    ``pebbles`` or ``salt`` (bath salt)."""
    g = JAR_GLASS_M
    rn = r * 0.86
    out = [(r - 0.004, 0.0), (r - 0.001, 0.0015), (r, 0.004), (r, h - 0.016), (r * 0.97, h - 0.011),
           (r * 0.92, h - 0.0085), (rn, h - 0.0065), (rn, h - 0.0025), (rn + 0.0012, h - 0.0012), (rn, h)]
    parts = [_vessel(cx, cy, z0, out, g, 0.006, glass, "jar")]
    # the seal (a light silicone ring) under the lid, the wooden lid with its rounded edge and a turned knob
    parts.append(_outward(lathe(cx, cy, z0 + h - 0.0028, [(rn + 0.0016, 0.0), (rn + 0.0018, 0.0038),
                                                          (rn - 0.002, 0.0038), (rn - 0.002, 0.0)], "ceramic", "seal")))
    lid = [(rn + 0.0025, 0.0), (rn + 0.0035, 0.002), (rn + 0.0035, 0.0085), (rn + 0.002, 0.0105), (rn * 0.80, 0.0125),
           (rn * 0.30, 0.0135), (0.0005, 0.0135)]
    parts.append(_outward(lathe(cx, cy, z0 + h + 0.001, lid, lid_key, "lid", n=28)))
    kr = min(0.0095, r * 0.27)
    parts.append(_outward(lathe(cx, cy, z0 + h + 0.0135, [(kr * 0.45, 0.0), (kr * 0.38, kr * 0.30),
                                                         (kr * 0.92, kr * 0.62), (kr, kr * 0.88),
                                                         (kr * 0.78, kr * 1.18), (kr * 0.25, kr * 1.32),
                                                         (0.0004, kr * 1.32)], lid_key, "lid", n=16)))
    inner = r - g - 0.0015
    floor = z0 + 0.0062
    top = z0 + h * (0.66 if fill != "salt" else 0.55)
    if fill == "salt":
        mound = [(inner * 0.96, 0.0), (inner, 0.002), (inner, top - floor)]
        k = 6
        for i in range(1, k + 1):                       # a coarse, lumpy top
            f = 1.0 - i / k
            mound.append((inner * f, top - floor + 0.004 * (1.0 - f * f) + 0.0012 * math.sin(i * 2.3 + seed)))
        parts.append(_outward(lathe(cx, cy, floor, mound, "ceramic", "fill")))
        for j in range(5):                              # a few coarse crystals on it
            a = 2 * math.pi * _unit(seed, j, 1)
            rho = inner * 0.55 * _unit(seed, j, 2)
            s = 0.003 + 0.002 * _unit(seed, j, 3)
            parts.append(_blob(cx + rho * math.cos(a), cy + rho * math.sin(a), top + 0.001, s, s * 0.9, s * 0.8,
                               "ceramic", "fill", e=0.35))
    elif fill == "pads":
        pr = min(0.026, inner - 0.002)
        z, k = floor, 0
        while z + 0.006 <= top and k < JAR_FILL["pads"]:
            dx, dy = 0.0015 * math.cos(k * 2.1 + seed), 0.0015 * math.sin(k * 2.1 + seed)
            pad = _lumpy(cx + dx, cy + dy, z, pr, seed * 31 + k, COTTON_KEY, "fill", amp=0.04, lat=5, lon=20,
                         squash=0.12, freq=(3, 5, 7))
            parts.append(pad)
            z += 0.0056
            k += 1
    else:
        cotton = fill == "cotton"
        amp = FLUFF if cotton else 0.12
        stretch = COTTON_STRETCH if cotton else 1.3              # a cotton ball pulled out a little; flat pebbles
        br = min(0.012 if cotton else 0.009, inner * 0.36)
        reach = br * (1.0 + amp) * stretch
        z, layer = floor, 0
        while z + reach * 1.4 <= top + 1e-9 and layer < JAR_FILL["layers"]:
            ring_r = max(0.0, inner - reach - 0.0003)
            k = max(3, int(2 * math.pi * ring_r / (2.0 * br * 1.05))) if ring_r > br else 0
            spots = [(0.0, 0.0)] if ring_r > 2.05 * br or k == 0 else []
            off = math.pi / max(k, 1) * (layer % 2)
            spots += [(ring_r * math.cos(2 * math.pi * j / k + off), ring_r * math.sin(2 * math.pi * j / k + off))
                      for j in range(k)]
            for j, (px, py) in enumerate(spots):
                s = seed * 101 + layer * 13 + j
                f = 0.88 + 0.12 * _unit(s, 1)
                if math.hypot(px, py) + reach * f > inner + 1e-9:
                    continue
                if cotton:
                    # 31 Oct 2026 (the smoke render: smooth balls still read as snowballs): fluffier, irregular balls
                    # of finer lumps, each drawn out a little in its own direction
                    parts.append(_lumpy(cx + px, cy + py, z, br * f, s, COTTON_KEY, "fill", lat=11, lon=22,
                                        squash=0.84, freq=(3, 5, 8), stretch=stretch, fine=0.35))
                else:
                    key = ("stone_light", "worktop", STONEWARE_KEY)[_hash(s) % 3]
                    parts.append(_lumpy(cx + px, cy + py, z, br * f, s, key, "fill", amp=amp, lat=6, lon=10,
                                        squash=0.55, freq=(1, 2, 3), stretch=stretch))
            z += br * (1.5 if cotton else 0.95)
            layer += 1
    return parts


def reed_diffuser(cx: float, cy: float, z0: float, r: float, h: float, reed_len: float, key: str = "terracotta",
                  collar_key: str = "handle", seed: int = 0) -> list[Part]:
    """A diffuser bottle (``h`` high, radius ``r``; ``key`` its glass, an opaque key its body) with the oil inside, a
    metal collar, ``DIFFUSER["reeds"]`` round reeds standing in the oil and fanning out ``reed_len`` from its neck, a
    small label."""
    neck = r * 0.30
    out = [(r * 0.90, 0.0), (r * 0.97, 0.0015), (r, 0.005), (r, h * 0.66), (r * 0.94, h * 0.74), (r * 0.70, h * 0.82),
           (r * 0.42, h * 0.88), (neck, h * 0.92), (neck, h)]
    glass = _glass_of(key)
    if glass:
        parts = [_vessel(cx, cy, z0, out, GLASS_WALL_M, GLASS_BASE_M, glass, "bottle")]
        parts.append(_fill_turned(cx, cy, z0, out, GLASS_WALL_M, GLASS_BASE_M, h * 0.42, DIFFUSER_OIL_KEY, "contents"))
    else:
        parts = [_outward(lathe(cx, cy, z0, out, key, "bottle"))]
    parts.append(_ribbed(cx, cy, z0 + h * 0.90, neck + 0.0022, h * 0.10 + 0.002, 14, 0.0006, collar_key, "cap"))
    n = DIFFUSER["reeds"]
    top = z0 + h
    foot = z0 + GLASS_BASE_M + 0.002                       # the reeds stand on the bottle's floor, in the oil
    for k in range(n):
        a = 2 * math.pi * (k + 0.45 * _unit(seed, k)) / n
        lean = DIFFUSER["spread"] * (0.55 + 0.45 * _unit(seed, k, 1))
        ln = reed_len * (0.86 + 0.14 * _unit(seed, k, 2))
        dx, dy = math.cos(a) * lean, math.sin(a) * lean
        dz = math.sqrt(max(0.0, 1.0 - dx * dx - dy * dy))
        x0, y0 = cx + math.cos(a) * neck * 0.35, cy + math.sin(a) * neck * 0.35
        # from the floor straight up to the neck, then out along the fan, a little curved (the reed's own weight)
        x1, y1 = cx + math.cos(a) * neck * 0.55, cy + math.sin(a) * neck * 0.55
        pts = [(x0 - dx * 0.02, y0 - dy * 0.02, foot), (x1, y1, top - h * 0.02)]
        for j in (1, 2, 3):
            f = j / 3.0
            sag = 0.012 * ln * f * f
            pts.append((x1 + dx * ln * f * (1.0 + 0.05 * f), y1 + dy * ln * f * (1.0 + 0.05 * f),
                        top - h * 0.02 + dz * ln * f - sag))
        parts.append(_tube(pts, DIFFUSER["reed_r_m"], REED_KEY, "reed", sides=6))
    parts += label(cx, cy, z0, r, h * 0.30, h * 0.54, "paper", "dark", arc_deg=80.0)
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
        # 31 Oct 2026 (the smoke render: spoon-like paddles): a lance-shaped blade, narrow where it meets its stem,
        # widest a little before its middle, drawn to a point
        w = max(0.0006, width * math.sin(math.pi * (0.04 + 0.96 * u)) ** 0.75 * (1.08 - 0.25 * u))
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
                 pot_key: str = STONEWARE_KEY, max_r: Optional[float] = None) -> list[Part]:
    """A glazed pot (a foot, a slight taper, a rolled rim) with its soil and a top dressing of pebbles, a small leafy
    plant (``height`` over the floor in all, its leaves within ``max_r`` of its centre): leaf blades on short stems
    arching out round the pot, the inner ones upright."""
    pot = [(pot_r * 0.70, 0.0), (pot_r * 0.74, 0.003), (pot_r * 0.76, 0.006), (pot_r * 0.82, 0.008),
           (pot_r * 0.97, pot_h * 0.84), (pot_r * 1.0, pot_h * 0.88), (pot_r * 1.02, pot_h * 0.95), (pot_r, pot_h)]
    parts = [_vessel(cx, cy, z0, pot, 0.005, pot_h * 0.2, pot_key, "pot", n=28)]
    soil = pot_h * 0.80
    parts.append(_fill_turned(cx, cy, z0, pot, 0.005, pot_h * 0.2, soil, "dark", "soil", meniscus=False, n=20))
    for j in range(7):                                  # the top dressing: pebbles on the soil
        a = 2 * math.pi * (j + 0.4 * _unit(seed, j)) / 7
        rho = pot_r * (0.35 + 0.42 * _unit(seed, j, 1))
        parts.append(_lumpy(cx + rho * math.cos(a), cy + rho * math.sin(a), z0 + soil - 0.002,
                            0.0045 + 0.0015 * _unit(seed, j, 2), seed * 17 + j, ("stone_light", "worktop")[j % 2],
                            "dressing", amp=0.12, lat=5, lon=8, squash=0.55, freq=(1, 2, 3)))
    foliage = max(0.04, height - pot_h)
    if max_r is not None:
        foliage = max(0.04, min(foliage, (max_r - pot_r * 0.2) / PLANT_REACH))
    n = 12
    for k in range(n):
        inner = k % 3 == 0
        az = 2 * math.pi * k / n + 0.4 * (_unit(seed, k) - 0.5)
        stem_l = foliage * (0.36 if inner else 0.22) * (0.9 + 0.2 * _unit(seed, k, 4))
        el = math.radians(78 if inner else 52)
        bx, by = cx + math.cos(az) * pot_r * 0.18, cy + math.sin(az) * pot_r * 0.18
        bz = z0 + soil
        tip = (bx + math.cos(az) * math.cos(el) * stem_l, by + math.sin(az) * math.cos(el) * stem_l,
               bz + math.sin(el) * stem_l)
        parts.append(_tube([(bx, by, bz - 0.004), tip], [0.0018, 0.0013], "green", "stem", sides=5))
        ln = foliage * (0.60 if inner else 0.52) * (0.80 + 0.2 * _unit(seed, k, 3))
        wd = ln * (0.34 + 0.06 * _unit(seed, k, 5))
        parts.append(leaf(tip, az, math.radians(60 if inner else 32), ln, wd, math.radians(55 if inner else 70),
                          key=LEAF_KEY))
    return parts


def perfume_bottle(cx: float, cy: float, z0: float, w: float, d: float, h: float, collar_key: str = "handle",
                   cap_key: str = "dark", liquid_key: str = SCENT_KEY, glass: str = GLASS["clear"],
                   style: int = 0) -> list[Part]:
    """A flacon ``w x d`` and ``h`` high to its cap's top: thick glass (a heavy base, soft chamfered edges; ``style``
    0 a rounded rectangle, 1 an oval) with its cavity, the scent inside it and the dip tube, a neck with a crimped
    metal collar, the spray actuator with its nozzle hole and a cap (style 0 a rounded block, 1 a turned cap)."""
    bh = h * 0.64
    a, b = w / 2.0, d / 2.0
    pw = 5.0 if style == 0 else 2.6
    base, wall = min(0.009, bh * 0.14), min(0.0035, min(a, b) * 0.18)
    cr = min(a, b) * 0.28
    nh = h * 0.05
    rings = [(a - 0.003, b - 0.003, 0.0, pw), (a - 0.0008, b - 0.0008, 0.0008, pw), (a, b, 0.003, pw),
             (a, b, bh - 0.004, pw), (a - 0.0012, b - 0.0012, bh - 0.0008, pw), (a - 0.004, b - 0.004, bh, pw),
             (cr + 0.0006, cr + 0.0006, bh, 2.0), (cr, cr, bh + 0.0006, 2.0), (cr, cr, bh + nh, 2.0),
             (cr - 0.0012, cr - 0.0012, bh + nh + 0.0005, 2.0), (cr - 0.0025, cr - 0.0025, bh + nh, 2.0),
             (cr - 0.0025, cr - 0.0025, bh - wall * 0.6, 2.0),
             (a - wall - 0.002, b - wall - 0.002, bh - wall, pw), (a - wall, b - wall, bh - wall - 0.003, pw),
             (a - wall, b - wall, base + 0.003, pw), (a - wall - 0.003, b - wall - 0.003, base, pw)]
    parts = [_loft(cx, cy, z0, rings, glass, "perfume", n=32)]
    lv = base + (bh - wall - base) * 0.72
    ia, ib = a - wall - 0.0006, b - wall - 0.0006
    parts.append(_loft(cx, cy, z0, [(ia - 0.003, ib - 0.003, base + 0.0006, pw), (ia, ib, base + 0.0036, pw),
                                     (ia, ib, lv, pw), (ia - 0.0015, ib - 0.0015, lv - 0.0008, pw),
                                     (ia * 0.5, ib * 0.5, lv - 0.0011, pw)], liquid_key, "liquid", n=32))
    parts.append(P._cylinder_z(cx, cy, z0 + base + 0.001, 0.0012, 0.0012, bh + nh - base, GLASS["clear"], "tube", n=8))
    # the crimped collar, the actuator with its nozzle hole, the cap over them
    parts.append(_ribbed(cx, cy, z0 + bh + nh * 0.05, cr + 0.0016, nh * 1.15, 20, 0.0004, collar_key, "cap"))
    ah = h * 0.06
    az = z0 + bh + nh * 1.2
    parts.append(_outward(lathe(cx, cy, az, [(cr * 0.62, 0.0), (cr * 0.66, ah * 0.2), (cr * 0.66, ah * 0.85),
                                             (cr * 0.55, ah), (0.0004, ah)], collar_key, "cap", n=16)))
    parts.append(P._cylinder_y(cx, cy - cr * 0.66 - 0.0004, az + ah * 0.55, 0.0006, 0.0006, 0.0006, "dark", "cap",
                               n=8))
    cz = az + ah - 0.004
    ch = z0 + h - cz
    if ch > 0.008:
        if style == 0:
            cw = min(a, b) * 1.45
            parts.append(P._superellipsoid(cx, cy, cz, cw, cw, ch, 0.30, 0.30, cap_key, "cap", n_eta=8, n_om=24))
        else:
            ccr = min(a, b) * 0.62
            parts.append(_outward(lathe(cx, cy, cz, [(ccr * 0.96, 0.0), (ccr, 0.0015), (ccr, ch * 0.70),
                                                     (ccr * 0.92, ch * 0.88), (ccr * 0.65, ch * 0.98),
                                                     (0.0005, ch)], cap_key, "cap", n=24)))
    return parts


def candle_glass(cx: float, cy: float, z0: float, r: float, h: float, glass: str = GLASS["smoke"]) -> list[Part]:
    """A candle poured in a tinted glass tumbler with a thick base: the glass, the wax (its melt pool a little under
    the rim), the wick with its charred tip."""
    out = [(r - 0.003, 0.0), (r - 0.0008, 0.001), (r, 0.004), (r, h - 0.0015), (r - 0.0006, h)]
    parts = [_vessel(cx, cy, z0, out, JAR_GLASS_M, 0.008, glass, "jar")]
    wax = h * 0.78
    ri = _r_at(out, wax) - JAR_GLASS_M - 0.0005
    wx = _fill_turned(cx, cy, z0, out, JAR_GLASS_M, 0.008, wax, SOAP_KEY, "candle", meniscus=False)
    # the melt pool: the wax's top sinks towards the wick
    wx["verts"] = [(x, y, z - 0.0035 * max(0.0, 1.0 - math.hypot(x - cx, y - cy) / max(ri, 1e-6))
                    if z > z0 + wax - 0.001 else z) for x, y, z in wx["verts"]]
    parts.append(wx)
    parts.append(P._cylinder_z(cx, cy, z0 + wax - 0.014, 0.0011, 0.0011, 0.016, "bedding", "wick", n=6))
    parts.append(_lumpy(cx, cy, z0 + wax + 0.0015, 0.0014, 3, "dark", "wick", amp=0.2, lat=4, lon=6, squash=1.4))
    return parts


def soap_dish(cx: float, cy: float, z0: float, r: float, key: str = STONEWARE_KEY) -> list[Part]:
    """An oval glazed dish (``r`` its half depth's scale: ``1.3 r`` x ``0.95 r``) on a foot ring, its rounded rim,
    drainage ribs across its floor and a bar of soap with rounded edges and a pressed mark resting on them."""
    a, b = r * 1.3, r * 0.95
    pw = 2.4
    rings = [(a * 0.62, b * 0.62, 0.0, pw), (a * 0.66, b * 0.66, 0.002, pw), (a * 0.70, b * 0.70, 0.003, pw),
             (a * 0.80, b * 0.80, 0.005, pw), (a * 0.93, b * 0.93, 0.011, pw), (a, b, 0.017, pw),
             (a - 0.0015, b - 0.0015, 0.0195, pw), (a - 0.004, b - 0.004, 0.0185, pw),
             (a - 0.006, b - 0.006, 0.016, pw), (a * 0.84, b * 0.84, 0.009, pw), (a * 0.70, b * 0.70, 0.0065, pw)]
    parts = [_loft(cx, cy, z0, rings, key, "dish", n=36)]
    floor = z0 + 0.0065
    for i in range(5):                                   # the drainage ribs across its floor
        x = cx + (i - 2) * a * 0.22
        span = 2 * b * 0.70 * math.sqrt(max(0.0, 1.0 - ((x - cx) / (a * 0.78)) ** 2))
        parts.append(P._superellipsoid(x, cy, floor - 0.0015, 0.0045, max(0.01, span), 0.0055, 0.6, 0.5, key, "rib",
                                       n_eta=4, n_om=12))
    sw, sd, sh = a * 1.25, b * 1.15, 0.021
    sz = floor + 0.0035
    parts.append(P._superellipsoid(cx, cy, sz, sw, sd, sh, 0.34, 0.42, SOAP_KEY, "soap", n_eta=8, n_om=24))
    parts.append(P._superellipsoid(cx, cy, sz + sh - 0.0009, sw * 0.52, sd * 0.42, 0.0021, 0.7, 0.8, SOAP_KEY, "soap",
                                   n_eta=4, n_om=20))
    return parts


def _basket_ring(a: float, b: float, n: int, power: float = 4.0) -> list[tuple[float, float, float, float]]:
    """``n`` points ``(x, y, nx, ny)`` round a superellipse of half sizes ``a`` x ``b`` (``power`` 4: a rounded
    rectangle), evenly spaced along its perimeter, with their outward normals."""
    e = 2.0 / power
    m = 256
    raw = []
    for i in range(m):
        t = 2 * math.pi * i / m
        c, s = math.cos(t), math.sin(t)
        raw.append((a * math.copysign(abs(c) ** e, c), b * math.copysign(abs(s) ** e, s)))
    cum = [0.0]
    for i in range(m):
        x0, y0 = raw[i]
        x1, y1 = raw[(i + 1) % m]
        cum.append(cum[-1] + math.hypot(x1 - x0, y1 - y0))
    total = cum[-1]
    out = []
    j = 0
    for k in range(n):
        target = total * k / n
        while cum[j + 1] < target:
            j += 1
        f = (target - cum[j]) / max(cum[j + 1] - cum[j], 1e-12)
        x0, y0 = raw[j]
        x1, y1 = raw[(j + 1) % m]
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        tx, ty = x1 - x0, y1 - y0
        ln = math.hypot(tx, ty) or 1.0
        out.append((x, y, ty / ln, -tx / ln))
    return out


def woven_basket(cx: float, cy: float, z0: float, w: float, d: float, h: float, towel_key: str = "towel",
                 key: str = "rattan") -> list[Part]:
    """A real wicker basket ``w x d`` (at most ``h`` high with its towels): a woven base (``key``, the rattan photo),
    upright stakes and weavers passing over and under them row by row (``CANE_KEY``, ``REED_KEY``), a braided rim of
    two twisted canes, two cane handles at its ends and two rolled towels lying in it, their tops over the rim."""
    W = WEAVE
    a, b = w / 2.0 - 0.006, d / 2.0 - 0.006
    taper = 0.92                                               # the base this share of the rim
    wall = W["weave_in_m"] + W["weaver_t_m"]                   # the weave's half thickness round its middle line
    # the two rolls side by side inside the weave at its narrow base (they poked through the walls in the smoke render)
    r = max(0.02, min(h * 0.5 - 0.004, d / 2.0 - 0.012, w / 4.6, (a * taper - wall - 0.005) / 2.0))
    hb = min(h - 0.012, max(0.05, 2 * r * 0.62))              # the rim well under the towels' tops
    bt = W["base_t_m"]
    parts = [_ring_loft(cx, cy, z0, [(a * taper - 0.003, b * taper - 0.003, 0.0), (a * taper, b * taper, 0.002),
                                     (a * taper, b * taper, bt - 0.002), (a * taper - 0.003, b * taper - 0.003, bt)],
                        key, "basket", power=4.0, n=32, smooth=False)]
    perim = 2 * math.pi * math.sqrt((a * a + b * b) / 2.0) * 0.93
    ns = max(12, 2 * int(perim / W["stake_pitch_m"] / 2.0))   # an even number of stakes (the weave alternates)
    z_top = hb - W["rim_r_m"] * 1.6

    def ring_at(z: float) -> list[tuple[float, float, float, float]]:
        f = taper + (1.0 - taper) * min(1.0, max(0.0, z / max(hb, 1e-6)))
        return _basket_ring(a * f, b * f, ns)

    lo, hi = ring_at(bt * 0.5), ring_at(z_top)
    for i in range(ns):                                        # the stakes: from the base up to the rim
        (x0, y0, _a, _b), (x1, y1, _c, _d) = lo[i], hi[i]
        parts.append(_tube([(cx + x0, cy + y0, z0 + bt * 0.5), (cx + x1, cy + y1, z0 + z_top + W["rim_r_m"])],
                           W["stake_r_m"], REED_KEY, "stake", sides=5))
    rows = max(3, int((z_top - bt) / W["row_pitch_m"]))
    pitch = (z_top - bt) / rows
    for k in range(rows):                                      # the weavers: over and under the stakes, row by row
        z = bt + (k + 0.5) * pitch
        ring = ring_at(z)
        pts = []
        for i in range(ns):
            x, y, nx, ny = ring[i]
            s = W["weave_in_m"] * (1.0 if (i + k) % 2 == 0 else -1.0)
            pts.append((cx + x + nx * s, cy + y + ny * s, z0 + z))
            xn, yn, nxn, nyn = ring[(i + 1) % ns]
            pts.append((cx + (x + xn) / 2.0, cy + (y + yn) / 2.0, z0 + z))
        parts.append(_tube(pts, W["weaver_t_m"] / 2.0, CANE_KEY, "basket", sides=6, loop=True, r_up=pitch * 0.47))
    # the braided rim: two canes twisted round each other over the top
    rim = _basket_ring(a, b, 4 * ns)
    zr = z0 + hb - W["rim_r_m"]
    turns = W["rim_turns_per_m"] * perim
    for strand in (0.0, math.pi):
        pts = []
        for i, (x, y, nx, ny) in enumerate(rim):
            t = 2 * math.pi * turns * i / len(rim) + strand
            off = W["rim_r_m"] * 0.75
            pts.append((cx + x + nx * off * math.cos(t), cy + y + ny * off * math.cos(t), zr + off * math.sin(t)))
        parts.append(_tube(pts, W["rim_r_m"], CANE_KEY, "rim", sides=6, loop=True))
    # two cane handles: a loop up from the rim at each short end (inside the box)
    hr, rise = W["handle_r_m"], min(0.03, h - hb - 0.004)
    if rise > 0.012:
        for sx in (-1.0, 1.0):
            pts = []
            for j in range(9):
                t = math.pi * j / 8
                y = -b * 0.32 * math.cos(t)
                pts.append((cx + sx * (a - hr), cy + y, zr + rise * math.sin(t)))
            parts.append(_tube(pts, hr, CANE_KEY, "handle", sides=6))
    length = max(0.05, min(d - 0.03, 2.0 * (b * taper - wall) - 0.004))
    for k, sx in enumerate((-1.0, 1.0)):
        parts.append(TP.rolled_towel(cx + sx * (r + 0.003), cy, z0 + bt, r, length,
                                     towel_key if k == 0 else TP.alt_key(towel_key), "y", 7 + k))
    return parts


def cotton_stem(base, direction, length: float, seed: int = 0) -> list[Part]:
    """A dried cotton branch from ``base`` along the unit ``direction``: its stem and a boll at its tip (a dark calyx
    and three fluffy puffs)."""
    ux, uy, uz = direction
    tip = (base[0] + ux * length, base[1] + uy * length, base[2] + uz * length)
    parts = [_stick(base, tip, 0.0016, "wood", "stem")]
    parts.append(_blob(tip[0], tip[1], tip[2] - 0.006, 0.016, 0.016, 0.010, "dark", "calyx", e=0.7))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4 * (_hash(seed, k) % 3)
        parts.append(_lumpy(tip[0] + math.cos(a) * 0.007, tip[1] + math.sin(a) * 0.007, tip[2] - 0.002, 0.0085,
                            seed * 7 + k, COTTON_KEY, "cotton"))
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
