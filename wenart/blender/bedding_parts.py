"""Bed realism: the family's bedding set, a soft duvet with volume, folds and a side overhang, fringed and patterned
throws, the nightstand's decor set (29 Oct 2026, lesson UL121; user, sending a photo of a full, soft bed: "look how
realistic the bed is looking full and nice I want this much detail in our models"; docs/reference_details_20261029.md
R35, R36).

What (pure: numpy and ``wenart.geometry``, no ``bpy`` and no shapely, so the build, the decor stage and both reviews
import it):

- ``FAMILY_BEDDING``: one row per style family, with its reason: the duvet (fabric look, colour, thickness, folds, the
  hem's height over the floor), the euro shams, the sleeping pillows, the accent cushions (boucle, knit, velvet ...),
  the lumbar, the throw pair (the woven pattern of the lower blanket, the fringed throw over it). ``family_spec`` and
  ``counts`` (what a bed of a width takes: two shams and two pillows from a double bed's width, one pillow on a single).
- ``bed_sides``: each side of a bed (left, right, foot) free or blocked by a wall or a piece (a nightstand, a bench, a
  wardrobe) along the duvet's span, from the building's walls and pieces; the duvet hangs almost to the floor on a
  free side only, never through a nightstand or a wall (``SIDE_FREE_M``).
- the meshes (numpy vertex arrays, one part per pillow or cloth, no Python loop per vertex): ``plump_cushion`` (a
  filled pillow: a plump body, drawn-in sides, soft corners and, 30 Oct 2026, the pillowcase's flange: a crisp edge;
  never a box), ``cover_grid`` (30 Oct 2026, UL136: a duvet or a blanket over the host's smooth top, ``envelope``,
  with a few soft wide folds, ``soft_folds``, a rounded edge, then straight down one plane per side to one level hem,
  a few soft wide folds growing to it; ``textiles.drape_cover`` measures the host for it), ``sheet_solid`` (a cloth
  with its thickness, thinned to its seam), ``turn_down_band`` (the thin turned-down sheet folded round the duvet's
  head edge), ``fringe_strands`` (the strands at a throw's two ends), ``stack_cushion`` (an accent cushion or a lumbar
  leaning on what stands behind it, placed on the meshes' own profiles: no ray), ``bedside_set_parts`` (R36: white
  faceted vases, a dried palm leaf in one, a black and white box).
- ``cover_smoothness``: the look of a built cover, measured (30 Oct 2026, UL136: a lumpy duvet, a wavy hem).
- ``bedding_relief`` / ``dress_mode``: a library bed's own bedding measured on its mesh (the pillow bump at the head,
  the relief of the folds and the vertex density over the duvet): a bed whose bedding is flat or poorer than ours is
  dressed too (``full``: flat or no cover; ``pillows``: a modelled duvet without pillows, or with pillows lying flat
  on a bed that takes euro shams (30 Oct 2026, UL137), gets our pillow set only).
- ``review``: what a built bed lacks against its family's set (model review M30, Argus U34; kind ``taste``), and since
  30 Oct 2026 a lumpy duvet or blanket, a wavy hem, a gap between the mattress and the headboard left open.

Why: the reference photo (P11) shows a deep duvet with soft rounded edges and natural wrinkles hanging down the sides
almost to the floor, many pillows of different sizes and fabrics, a fringed throw over a houndstooth blanket; our beds
had a 4 cm duvet with a sharp fold, 30 cm of overhang into walls and nightstands alike, two pillows and plain throws.

How: every number is a designer value of real products (assumed): a 65 x 65 cm euro sham, a 65 x 45 cm pillow, a
45 cm accent cushion, a 50 x 30 cm lumbar, a 6 cm duvet. Folds are fixed functions of the cloth's own coordinates
(the same every build); every displacement moves the cloth away from the host, never into it.

30 Oct 2026 (user on real04 run 20261029-201533-full; lessons UL136 "I did not like this bed", UL137 "head section of
this bed needs a rework", UL146 the photo P14, R38): the 29 Oct duvet followed every ray hit of the host and fluted its
sides (they rippled "like melted foam", the hem was wavy), its turned-down band was a 4 cm slab, the pillows were
squashed; now a real made bed (``cover_grid``, ``turn_down_band``, the flanged ``plump_cushion``) and the P14 layers
(``textiles.p14_throw_parts``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G

Part = dict
RULE = "bedding.ul121"
LESSON = "UL121"
RULE_LOOK = "bedding.ul136"      # 30 Oct 2026: a real made bed (UL136 the look, UL137 the head, UL146 the P14 layers)
LESSONS_LOOK = ("UL136", "UL137", "UL146")
TAG = ("29 Oct 2026, user: \"look how realistic the bed is looking full and nice I want this much detail in our "
       "models\"")

# --------------------------------------------------------------------------
# Fabric looks (materials: the ``wenart_weave`` group, ``materials.weave_group``; the vocabulary's fabric slugs)
# --------------------------------------------------------------------------

LOOKS: tuple[str, ...] = ("linen", "cotton", "velvet", "knit", "boucle", "wool")
PATTERNS: tuple[str, ...] = ("houndstooth", "stripe", "herringbone")
# the slug of each look: linen keeps the Poly Haven rough_linen scan (its photographed weave and normal map); the others
# are procedural weaves (``finishes.FURNITURE_MATERIALS``)
LOOK_SLUGS: dict[str, str] = {"linen": "fabric_linen", "cotton": "fabric_cotton", "velvet": "fabric_velvet",
                              "knit": "fabric_knit", "boucle": "fabric_boucle", "wool": "fabric_wool"}
PATTERN_SLUGS: dict[str, str] = {"houndstooth": "fabric_houndstooth", "stripe": "fabric_stripe",
                                 "herringbone": "fabric_herringbone"}
TEXTILE_PREFIX = "textile_"      # a part key ``textile_<look or pattern>`` (furniture.style_material_keys)
RUNNER_PREFIX = "runner_"        # the second blanket's key ``runner_<look>``: its colour is the item's accent colour
COLOUR_PREFIX = "colour_"        # = parametric.COLOUR_PREFIX: the part takes a colour phrase


def textile_key(look: str, coloured: bool = True) -> str:
    """The part key of a fabric look or pattern (``colour_textile_boucle``)."""
    return (COLOUR_PREFIX if coloured else "") + TEXTILE_PREFIX + str(look)


def runner_key(look: str) -> str:
    return COLOUR_PREFIX + RUNNER_PREFIX + str(look)


def key_slug(key: str) -> Optional[str]:
    """The vocabulary slug of a textile or runner key (with or without the colour prefix), None for another key."""
    k = key[len(COLOUR_PREFIX):] if key.startswith(COLOUR_PREFIX) else key
    for prefix in (TEXTILE_PREFIX, RUNNER_PREFIX):
        if k.startswith(prefix):
            name = k[len(prefix):]
            return LOOK_SLUGS.get(name) or PATTERN_SLUGS.get(name)
    return None


def material_keys() -> dict[str, str]:
    """``{key (without the colour prefix): slug}`` of every textile and runner key the bedding parts use."""
    out = {}
    for name, slug in list(LOOK_SLUGS.items()) + list(PATTERN_SLUGS.items()):
        out[TEXTILE_PREFIX + name] = slug
        out[RUNNER_PREFIX + name] = slug
    return out


# per look: the Principled sheen (weight, roughness) and the weave bump (strength, distance m, thread pitch m), designer
# values: velvet has the strongest, tightest sheen (its pile); cotton percale a faint one; boucle and knit the deepest
# relief (loops, ribs); linen keeps its scan's own normal map (no procedural bump)
LOOK_LAYERS: dict[str, dict] = {
    "linen": {"sheen": (0.5, 0.5), "bump": (0.25, 0.0008, 0.002), "roughness": 0.85},   # (the kind's sheen)
    "cotton": {"sheen": (0.25, 0.6), "bump": (0.12, 0.0004, 0.0012), "roughness": 0.75},
    "velvet": {"sheen": (1.0, 0.3), "bump": (0.10, 0.002, 0.15), "roughness": 0.6},
    "knit": {"sheen": (0.45, 0.5), "bump": (0.6, 0.003, 0.007), "roughness": 0.9},
    "boucle": {"sheen": (0.5, 0.6), "bump": (0.75, 0.003, 0.004), "roughness": 0.95},
    "wool": {"sheen": (0.55, 0.5), "bump": (0.35, 0.0015, 0.004), "roughness": 0.9},
    # 30 Oct 2026 (UL138): the towels' terry (no bedding look): a deep loop pile, a faint sheen on the loops' tips
    "terry": {"sheen": (0.3, 0.7), "bump": (0.9, 0.0025, 0.0028), "roughness": 0.97},
}
PATTERN_WEAVE = "wool"           # a patterned blanket is a woven wool (its twill bump)
PATTERN_REPEAT_M: dict[str, float] = {"houndstooth": 0.028, "stripe": 0.06, "herringbone": 0.04}


def pattern_share(pattern: str, x: float, y: float, repeat: float) -> float:
    """The ink share (0 or 1) of a woven pattern at ``(x, y)`` metres on the cloth (pure; the ``wenart_weave`` group
    computes the same with math nodes, tested on a fake bpy): ``stripe`` bands 35 % of each repeat across x;
    ``houndstooth`` a check of half-repeat squares whose mixed squares carry diagonal teeth; ``herringbone`` short
    diagonal bands turning every column of a quarter repeat."""
    r = float(repeat)
    if pattern == "stripe":
        return 1.0 if (x / r) % 1.0 < 0.35 else 0.0
    if pattern == "houndstooth":
        a = 1.0 if (x / r) % 1.0 >= 0.5 else 0.0
        b = 1.0 if (y / r) % 1.0 >= 0.5 else 0.0
        teeth = 1.0 if ((x + y) / (r * 0.25)) % 1.0 < 0.5 else 0.0
        return a * b + (a + b - 2.0 * a * b) * teeth
    if pattern == "herringbone":
        column = math.floor(x / (r * 0.5))
        turn = 1.0 - 2.0 * (column % 2)
        return 1.0 if ((x + y * turn) / (r * 0.25)) % 1.0 < 0.5 else 0.0
    return 0.0


# --------------------------------------------------------------------------
# The family's set (designer values, assumed; colours are wenart/style/colours.py names)
# --------------------------------------------------------------------------

SHAM_SIZE = (0.65, 0.14, 0.62)          # a 65 x 65 cm euro sham standing (width, thickness, height)
PILLOW_SIZE = (0.65, 0.15, 0.45)        # a 65 x 45 cm sleeping pillow (width, thickness, length / standing height)
ACCENT_SIZE = (0.45, 0.15, 0.45)        # a 45 x 45 cm accent cushion
LUMBAR_SIZE = (0.50, 0.13, 0.30)        # a 50 x 30 cm lumbar
SHAM_MIN_BED_W = 1.35                   # = textiles.SHAM_MIN_BED_W: a double bed's width takes two shams
TWO_PILLOW_MIN_W = 1.30                 # = parametric.TWO_PILLOW_MIN_W
LUMBAR_MIN_BED_W = 0.85
PILLOW_UPRIGHT_LEAN_DEG = 14.0          # sleeping pillows stand against the shams, leaned back this much

FAMILY_BEDDING: dict[str, dict] = {
    "scandinavian": {
        "duvet": {"look": "linen", "colour": "off white", "thickness_m": 0.06, "wrinkle_m": 0.012, "hem_m": 0.08},
        "shams": {"look": "linen", "colour": "sand"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "boucle", "colour": "cream"}],
        "lumbar": {"look": "knit", "colour": "sage"},
        "throw": {"pattern": "stripe", "runner_look": "knit", "fringe": True},
        "why": "light linen layers in soft neutrals, a boucle and a knit cushion, a striped wool blanket under a "
               "fringed knit throw (Scandinavian: natural textures, little pattern)"},
    "japandi": {
        "duvet": {"look": "linen", "colour": "off white", "thickness_m": 0.055, "wrinkle_m": 0.014, "hem_m": 0.10},
        "shams": {"look": "linen", "colour": "greige"},
        "pillows": {"look": "linen", "colour": "off white"},
        "accent": [{"look": "boucle", "colour": "beige"}],
        "lumbar": None,
        "throw": {"pattern": "herringbone", "runner_look": "linen", "fringe": True},
        "why": "washed linen with few pieces (no lumbar), one boucle cushion, a quiet herringbone wool and a fringed "
               "linen throw (Japandi: calm, natural, restrained)"},
    "modern": {
        "duvet": {"look": "cotton", "colour": "white", "thickness_m": 0.065, "wrinkle_m": 0.009, "hem_m": 0.06},
        "shams": {"look": "velvet", "colour": "charcoal"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "boucle", "colour": "ivory"}, {"look": "knit", "colour": "light grey"}],
        "lumbar": {"look": "velvet", "colour": "charcoal"},
        "throw": {"pattern": "houndstooth", "runner_look": "knit", "fringe": True},
        "why": "crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket "
               "under a fringed knit throw (the reference photo's set)"},
    "contemporary": {
        "duvet": {"look": "cotton", "colour": "off white", "thickness_m": 0.065, "wrinkle_m": 0.01, "hem_m": 0.06},
        "shams": {"look": "linen", "colour": "greige"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "boucle", "colour": "cream"}, {"look": "velvet", "colour": "dusty blue"}],
        "lumbar": {"look": "knit", "colour": "greige"},
        "throw": {"pattern": "houndstooth", "runner_look": "knit", "fringe": True},
        "why": "soft cotton and linen, a boucle and a velvet cushion, a knit lumbar, a houndstooth blanket under a "
               "fringed knit throw"},
    "modern minimal": {
        "duvet": {"look": "cotton", "colour": "white", "thickness_m": 0.055, "wrinkle_m": 0.006, "hem_m": 0.05},
        "shams": {"look": "cotton", "colour": "light grey"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "boucle", "colour": "light grey"}],
        "lumbar": None,
        "throw": {"pattern": "stripe", "runner_look": "wool", "fringe": False},
        "why": "fewer pieces and no fringe: the shams, the sleeping pillows, one boucle cushion, a fine-striped "
               "blanket under a plain wool throw (minimal: calm surfaces)"},
    "minimal": {
        "duvet": {"look": "cotton", "colour": "white", "thickness_m": 0.055, "wrinkle_m": 0.006, "hem_m": 0.05},
        "shams": {"look": "cotton", "colour": "light grey"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "boucle", "colour": "light grey"}],
        "lumbar": None,
        "throw": {"pattern": "stripe", "runner_look": "wool", "fringe": False},
        "why": "fewer pieces and no fringe: the shams, the sleeping pillows, one boucle cushion, a fine-striped "
               "blanket under a plain wool throw (minimal: calm surfaces)"},
    "industrial": {
        "duvet": {"look": "linen", "colour": "light grey", "thickness_m": 0.06, "wrinkle_m": 0.014, "hem_m": 0.08},
        "shams": {"look": "linen", "colour": "charcoal"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "knit", "colour": "grey"}],
        "lumbar": {"look": "wool", "colour": "rust"},
        "throw": {"pattern": "herringbone", "runner_look": "wool", "fringe": True},
        "why": "washed grey linen, charcoal shams, a chunky knit cushion, a rust wool lumbar, a herringbone blanket "
               "under a fringed wool throw (industrial: robust textures)"},
    "mediterranean": {
        "duvet": {"look": "linen", "colour": "white", "thickness_m": 0.055, "wrinkle_m": 0.014, "hem_m": 0.08},
        "shams": {"look": "linen", "colour": "sand"},
        "pillows": {"look": "linen", "colour": "white"},
        "accent": [{"look": "knit", "colour": "cream"}, {"look": "linen", "colour": "terracotta"}],
        "lumbar": {"look": "linen", "colour": "dusty blue"},
        "throw": {"pattern": "stripe", "runner_look": "linen", "fringe": True},
        "why": "white linen, sand shams, a knit and a terracotta linen cushion, a blue lumbar, a striped blanket under "
               "a fringed linen throw (Mediterranean: sun-washed linen)"},
    "classic": {
        "duvet": {"look": "cotton", "colour": "ivory", "thickness_m": 0.07, "wrinkle_m": 0.008, "hem_m": 0.05},
        "shams": {"look": "velvet", "colour": "navy"},
        "pillows": {"look": "cotton", "colour": "white"},
        "accent": [{"look": "velvet", "colour": "cream"}, {"look": "velvet", "colour": "navy"}],
        "lumbar": {"look": "velvet", "colour": "cream"},
        "throw": {"pattern": "houndstooth", "runner_look": "wool", "fringe": True},
        "why": "a deep ivory sateen duvet, velvet shams and cushions, a velvet lumbar, a houndstooth blanket under a "
               "fringed wool throw (classic: rich, layered)"},
    "rustic": {
        "duvet": {"look": "linen", "colour": "cream", "thickness_m": 0.07, "wrinkle_m": 0.014, "hem_m": 0.08},
        "shams": {"look": "linen", "colour": "rust"},
        "pillows": {"look": "cotton", "colour": "cream"},
        "accent": [{"look": "knit", "colour": "cream"}],
        "lumbar": {"look": "wool", "colour": "rust"},
        "throw": {"pattern": "herringbone", "runner_look": "wool", "fringe": True},
        "why": "a deep cream linen duvet, rust shams, a chunky knit cushion, a wool lumbar, a herringbone blanket "
               "under a fringed wool throw (rustic: warm and heavy)"},
}
DEFAULT_FAMILY = "modern"


def family_spec(family: Optional[str]) -> tuple[dict, str]:
    """``(spec, reason)`` of a style family's bedding (``FAMILY_BEDDING``; the modern row for a family it does not
    list, said in the reason). The spec is a copy (``family`` in it)."""
    fam = str(family or "").lower()
    row = FAMILY_BEDDING.get(fam)
    why = row["why"] if row else (f"no bedding row for the family {fam or '(none)'}: the {DEFAULT_FAMILY} set "
                                  f"({FAMILY_BEDDING[DEFAULT_FAMILY]['why']})")
    row = row or FAMILY_BEDDING[DEFAULT_FAMILY]
    spec = {k: (dict(v) if isinstance(v, dict) else [dict(a) for a in v] if isinstance(v, list) else v)
            for k, v in row.items()}
    spec["family"] = fam if fam in FAMILY_BEDDING else DEFAULT_FAMILY
    return spec, why


def counts(spec: dict, width: float) -> dict[str, int]:
    """What a bed of ``width`` takes of its family's set: two euro shams on a double bed (``SHAM_MIN_BED_W``; only
    against a headboard, the build decides), one or two sleeping pillows (``TWO_PILLOW_MIN_W``), the family's accent
    cushions (one on a single bed), its lumbar on a bed from ``LUMBAR_MIN_BED_W``."""
    w = float(width)
    accent = len(spec.get("accent") or [])
    return {"euro_shams": 2 if w >= SHAM_MIN_BED_W - 1e-9 else 0,
            "pillows": 2 if w >= TWO_PILLOW_MIN_W - 1e-9 else 1,
            "accent": accent if w >= TWO_PILLOW_MIN_W - 1e-9 else min(1, accent),
            "lumbar": 1 if spec.get("lumbar") and w >= LUMBAR_MIN_BED_W - 1e-9 else 0}


def throw_weave(family: Optional[str]) -> dict:
    """The weave of a bed's throw pair by family (``FAMILY_BEDDING[...]["throw"]``): ``{"pattern", "runner_look",
    "fringe", "rule", "why"}``; the woven pattern is on the lower blanket (the throw itself), the fringe on the throw
    over it (the layered runner), both on a throw in one layer."""
    spec, why = family_spec(family)
    t = dict(spec["throw"])
    t.update(rule=RULE, why=f"the {spec['family']} throw pair: a {t['pattern']} blanket under a "
                            f"{'fringed ' if t['fringe'] else ''}{t['runner_look']} throw (R35; {why})")
    return t


# --------------------------------------------------------------------------
# The bed's sides: free or blocked (walls, pieces) along the duvet's span
# --------------------------------------------------------------------------

SIDE_FREE_M = 0.12               # a side this clear takes the full overhang (the cloth hangs 6-9 cm out of the bed)
SIDE_LOOK_M = 0.60               # obstacles farther than this from a side do not matter
FLAT_TYPES: tuple[str, ...] = ("rug",)
SIDES: tuple[str, ...] = ("left", "right", "foot")


def bed_frame(bed: dict) -> tuple[tuple[float, float], float, tuple[float, float]]:
    """``(centre, rotation, (width, depth))`` of a bed in the frame of its front (``geometry.front_frame``: local -Y is
    the foot, +Y the head; the build turns every model by it)."""
    fp = bed["footprint"]
    rot, size = G.front_frame(fp, bed.get("front_deg"))
    return (float(fp["center"][0]), float(fp["center"][1])), float(rot), (float(size[0]), float(size[1]))


def _local(centre, rot: float, pts) -> list[tuple[float, float]]:
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = float(x) - centre[0], float(y) - centre[1]
        out.append((c * dx + s * dy, -s * dx + c * dy))
    return out


def _clip(poly: list, axis: int, value: float, keep_below: bool) -> list:
    """Sutherland-Hodgman: the part of a polygon with ``p[axis] <= value`` (``keep_below``) or ``>= value``."""
    if not poly:
        return []

    def inside(p):
        return p[axis] <= value + 1e-12 if keep_below else p[axis] >= value - 1e-12
    out = []
    for k, cur in enumerate(poly):
        prev = poly[k - 1]
        if inside(cur):
            if not inside(prev):
                out.append(_cut(prev, cur, axis, value))
            out.append(cur)
        elif inside(prev):
            out.append(_cut(prev, cur, axis, value))
    return out


def _cut(a, b, axis: int, value: float):
    t = (value - a[axis]) / (b[axis] - a[axis]) if abs(b[axis] - a[axis]) > 1e-12 else 0.0
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _obstacles(bed: dict, building: dict) -> list[tuple[str, list]]:
    """``[(id, world polygon)]`` of what stands around a bed on its level: the other pieces (not a rug, not unbuilt)
    and the walls (their thick outline)."""
    out = []
    lid = bed.get("level_id")
    for p in building.get("furniture") or []:
        if p is bed or p.get("id") == bed.get("id") or p.get("level_id") != lid or not p.get("footprint") \
                or p.get("build", True) is False or p.get("type") in FLAT_TYPES:
            continue
        fp = p["footprint"]
        out.append((str(p.get("id")), G.rotated_rectangle(fp["center"], fp["size"][:2], float(fp.get("rotation_deg")
                                                                                              or 0.0))))
    for w in building.get("walls") or []:
        if w.get("level_id") not in (None, lid) or not w.get("start") or not w.get("end"):
            continue
        if G.distance(w["start"], w["end"]) < 1e-6:
            continue
        out.append((str(w.get("id")), G.centerline_to_rectangle(w["start"], w["end"], float(w.get("thickness")
                                                                                          or 0.1))))
    return out


def bed_sides(bed: dict, building: dict, span: Optional[tuple[float, float]] = None) -> dict:
    """``{"left"|"right"|"foot": {"clear_m", "by", "free"}}`` of a bed (pure; its front frame, ``bed_frame``): the
    clear distance from each side to the nearest wall or piece (``_obstacles``) that overlaps the duvet's span along
    that side (``span`` = its local y range, default the foot ``DUVET_SHARE`` of the bed; the foot's span is the bed's
    width), None when nothing is within ``SIDE_LOOK_M``; a side is ``free`` from ``SIDE_FREE_M``. A piece that touches
    or overlaps the bed on a side blocks it (clear 0)."""
    centre, rot, (w, d) = bed_frame(bed)
    y0, y1 = span if span is not None else (-d / 2.0, -d / 2.0 + DUVET_SHARE * d)
    out = {s: {"clear_m": None, "by": None} for s in SIDES}
    for oid, poly in _obstacles(bed, building):
        loc = _local(centre, rot, poly)
        # left and right: the obstacle's part in the duvet's span along the bed, beside the side
        band = _clip(_clip(loc, 1, y0, False), 1, y1, True)
        for side, sign in (("left", -1.0), ("right", 1.0)):
            part = _clip(band, 0, sign * w / 2.0 + (-sign) * 0.05, sign < 0) if band else []
            if not part:
                continue
            near = max(p[0] for p in part) if sign < 0 else min(p[0] for p in part)
            clear = max(0.0, (-w / 2.0 - near) if sign < 0 else (near - w / 2.0))
            if clear <= SIDE_LOOK_M and (out[side]["clear_m"] is None or clear < out[side]["clear_m"]):
                out[side] = {"clear_m": round(clear, 3), "by": oid}
        foot = _clip(_clip(loc, 0, -w / 2.0, False), 0, w / 2.0, True)
        part = _clip(foot, 1, -d / 2.0 + 0.05, True) if foot else []
        if part:
            clear = max(0.0, -d / 2.0 - max(p[1] for p in part))
            if clear <= SIDE_LOOK_M and (out["foot"]["clear_m"] is None or clear < out["foot"]["clear_m"]):
                out["foot"] = {"clear_m": round(clear, 3), "by": oid}
    for side in SIDES:
        c = out[side]["clear_m"]
        out[side]["free"] = c is None or c >= SIDE_FREE_M - 1e-9
    return out


# --------------------------------------------------------------------------
# Meshes
# --------------------------------------------------------------------------

DUVET_SHARE = 0.75               # = parametric.DUVET_SHARE: the duvet covers the foot 75 % of the mattress
CUSHION_P = 3.0                  # a pillow's face profile ((1 - |u|^p)(1 - |v|^p))^q: full and plump to near its edge
CUSHION_Q = 0.45                 # (30 Oct 2026, UL136: p 2.4 and q 0.55 read as squashed, "crumpled" pillows)
CUSHION_DRAW = 0.035             # its sides drawn in a little between the corners (soft "ears" at the corners)
CUSHION_GRID = (12, 12)
SEAM_M = 0.006
SAG_SHARE = 0.015                # a standing pillow's top edge sags this share of its height in the middle
# 30 Oct 2026 (UL136, UL146: "plump pillows with crisp pillowcase edges"): a pillowcase's flat border round the
# filled body: a euro sham's flange, a pillowcase's seam, a cushion's piping (designer values); 3 mm thick at the
# body, nothing at the seam: a crisp edge under smooth shading
FLANGE_M: dict[str, float] = {"euro_sham": 0.04, "pillow": 0.015, "accent_cushion": 0.008, "lumbar": 0.008}
FLANGE_T_M = 0.006


def _part(verts: np.ndarray, faces: np.ndarray, key: str, role: str) -> Part:
    return {"verts": [tuple(p) for p in np.asarray(verts, dtype=np.float64).tolist()],
            "faces": np.asarray(faces, dtype=np.int64).tolist(), "key": key, "role": role, "smooth": True}


def _grid_faces(idx: np.ndarray, flip: bool = False) -> np.ndarray:
    """The quads of an index grid ``(nu + 1, nv + 1)``: (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)."""
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    quads = np.stack([a, b, c, d], axis=-1).reshape(-1, 4)
    return quads[:, ::-1] if flip else quads


def plump_cushion(w: float, t: float, h: float, key: str = "bedding", role: str = "pillow",
                  grid: tuple[int, int] = CUSHION_GRID, sag: float = SAG_SHARE, flange: Optional[float] = None) -> Part:
    """A filled pillow or cushion in the box ``w x t x h`` (item frame: width X, thickness Y, height Z from 0; front
    -Y): two faces bulging to ``t / 2`` with a full, plump profile (``CUSHION_P``, ``CUSHION_Q``), meeting at a seam
    ring both faces share (a closed mesh), its sides drawn in between the corners (``CUSHION_DRAW``) and its top edge
    sagging a little in the middle (``sag``). 30 Oct 2026 (UL136): the pillowcase's ``flange`` (default by ``role``,
    ``FLANGE_M``) round the body, ``FLANGE_T_M`` thick at the body and closing at the seam: a crisp edge. Never a
    box."""
    nu, nv = grid
    w, t, h = float(w), float(t), float(h)
    fl = FLANGE_M.get(role, 0.0) if flange is None else float(flange)
    fl = max(0.0, min(fl, 0.2 * min(w, h)))
    ub = np.linspace(-1.0, 1.0, nu + 1)
    vb = np.linspace(-1.0, 1.0, nv + 1)
    if fl > 0.0:                                  # the body inside, one more ring at the seam outside it
        fu, fv = fl / (w / 2.0), fl / (h / 2.0)
        uu = np.concatenate([[-1.0], ub * (1.0 - fu), [1.0]])
        vv = np.concatenate([[-1.0], vb * (1.0 - fv), [1.0]])
        bu, bv = np.clip(uu / (1.0 - fu), -1.0, 1.0), np.clip(vv / (1.0 - fv), -1.0, 1.0)
        nu, nv = nu + 2, nv + 2
    else:
        uu, vv, bu, bv = ub, vb, ub, vb
    u, v = uu[:, None], vv[None, :]
    x = u * w / 2.0 * (1.0 - CUSHION_DRAW * np.sin(np.pi * (v + 1.0) / 2.0))
    z = h / 2.0 + v * h / 2.0 * (1.0 - CUSHION_DRAW * np.sin(np.pi * (u + 1.0) / 2.0))
    z = z - sag * h * (1.0 - u ** 2) * np.clip(v, 0.0, 1.0) ** 2
    prof = np.clip((1.0 - np.abs(bu[:, None]) ** CUSHION_P) * (1.0 - np.abs(bv[None, :]) ** CUSHION_P), 0.0,
                   1.0) ** CUSHION_Q
    half = np.maximum(FLANGE_T_M / 2.0 if fl > 0.0 else SEAM_M, t / 2.0 * prof)
    boundary = np.zeros((nu + 1, nv + 1), dtype=bool)
    boundary[0, :] = boundary[-1, :] = boundary[:, 0] = boundary[:, -1] = True
    half = np.where(boundary, 0.0, half)
    n = (nu + 1) * (nv + 1)
    front_idx = np.arange(n).reshape(nu + 1, nv + 1)
    inner = ~boundary
    back_idx = front_idx.copy()
    back_idx[inner] = n + np.arange(int(inner.sum()))
    front = np.stack([x, -half, z], axis=-1).reshape(-1, 3)
    back = np.stack([x, half, z], axis=-1)[inner]
    verts = np.concatenate([front, back], axis=0)
    verts[:, 2] -= verts[:, 2].min()
    faces = np.concatenate([_grid_faces(front_idx), _grid_faces(back_idx, flip=True)], axis=0)
    return _part(verts, faces, key, role)


def lean_verts(verts, lean_deg: float) -> np.ndarray:
    """Item-local vertices leaned ``lean_deg`` about X (top towards +Y), lifted so the lowest point is on z = 0 (as
    ``rest.pose_vertices`` before its turn and move)."""
    v = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    a = math.radians(float(lean_deg))
    ca, sa = math.cos(a), math.sin(a)
    out = np.stack([v[:, 0], v[:, 1] * ca + v[:, 2] * sa, -v[:, 1] * sa + v[:, 2] * ca], axis=1)
    out[:, 2] -= out[:, 2].min()
    return out


def to_world_arr(centre, rot: float, local: np.ndarray) -> np.ndarray:
    """Bed-local ``(x, y, z)`` points to world (rotation ``rot`` about +Z, then the centre)."""
    r = math.radians(float(rot))
    c, s = math.cos(r), math.sin(r)
    p = np.asarray(local, dtype=np.float64).reshape(-1, 3)
    return np.stack([float(centre[0]) + c * p[:, 0] - s * p[:, 1], float(centre[1]) + s * p[:, 0] + c * p[:, 1],
                     p[:, 2]], axis=1)


def to_local_arr(centre, rot: float, world) -> np.ndarray:
    r = math.radians(float(rot))
    c, s = math.cos(r), math.sin(r)
    p = np.asarray(world, dtype=np.float64).reshape(-1, 3)
    dx, dy = p[:, 0] - float(centre[0]), p[:, 1] - float(centre[1])
    return np.stack([c * dx + s * dy, -s * dx + c * dy, p[:, 2]], axis=1)


# -- the duvet: a smooth cover with a level hem (30 Oct 2026, lessons UL136, UL146) ---------------------------------
#
# 30 Oct 2026 (user on real04 run 20261029-201533-full, f_L0_021: "I did not like this bed"): the duvet of 29 Oct
# followed every ray hit of the host (a library mattress's own quilting, a jagged edge: neighbouring rows hung from
# edge points of different heights), its hanging sides got flutes of 22 mm every 18 cm and every side ray's jump, and
# it was a 6.5 cm slab to its cut rim: the sides rippled "like melted foam" with a wavy hem. Now (P14, R38: "a smooth
# grey duvet with gentle natural folds that hangs straight down the sides almost to the floor"): the top is a smooth
# envelope over the host (a cloth bridges the host's dips, never cuts a bump) with a few soft wide folds; over each
# edge it rounds on the duvet's own height, then hangs straight down one plane per side (outside the host at every
# height: a wider frame below is cleared by a gentle flare), each edge point's drop scaled to end on one level hem; a
# few wide soft folds grow towards the hem; the cloth thins to its seam over its last 6 cm (a rounded hem).

COVER_STEP_M = 0.04              # the top's grid pitch (the host's top is sampled there)
ARC_SEGMENTS = 5                 # rows of the rounded edge over the host's side
HANG_STEP_M = 0.05               # rows of the hanging part
RIM_M = 0.06                     # the cloth thins over this towards its seam ...
RIM_SHARE = 0.3                  # ... to this share of its thickness (a duvet's seam: a rounded hem, never a cut slab)
ENVELOPE_ROUNDS = 6              # the top: rounds of a Gaussian blur (sigma in cells), each kept over the host ...
ENVELOPE_SIGMA = 1.5
ENVELOPE_GIVE_M = 0.004          # ... less this (the loft gives on a small bump: its underside still 1 mm off the host)
TOP_FOLD_EDGE_M = 0.15           # the top's folds fade out within this of its edges and rim
SIDE_FOLD_PITCH_M = 0.46         # a few soft wide folds down the hanging sides ...
SIDE_FOLD_AMP_M = (0.010, 0.018)  # ... their depth at the hem (1.6 x the family's wrinkle, within these)
FLARE_M = 0.08                   # the hanging cloth leaves the side this far above a wider frame below it


def smoothstep(x) -> np.ndarray:
    x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def blur2d(a: np.ndarray, sigma: float) -> np.ndarray:
    """A separable Gaussian blur of a 2-D array (pure numpy; ``sigma`` in cells, the edges padded)."""
    a = np.asarray(a, dtype=np.float64)
    r = max(1, int(math.ceil(2.5 * float(sigma))))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / float(sigma)) ** 2)
    k /= k.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        n = out.shape[axis]
        out = sum(k[i] * np.take(p, np.arange(i, i + n), axis=axis) for i in range(2 * r + 1))
    return out


def envelope(raw: np.ndarray, fill: float) -> np.ndarray:
    """The smooth top a cloth makes over the host's top heights ``raw`` (pure; NaN where a ray found nothing: filled
    from its neighbours, ``fill`` to start): ``ENVELOPE_ROUNDS`` blurs, each kept at least at the host's top. A cloth
    bridges the host's dips (a quilted mattress, the seam between two mattresses) and never cuts its bumps."""
    raw = np.asarray(raw, dtype=np.float64)
    base = np.where(np.isnan(raw), -np.inf, raw - ENVELOPE_GIVE_M)
    z = np.where(np.isnan(raw), float(fill), raw)
    for _round in range(ENVELOPE_ROUNDS):
        z = np.maximum(base, blur2d(z, ENVELOPE_SIGMA))
    return z


def soft_folds(x, y, w: float, d: float, amp: float) -> np.ndarray:
    """The top's few soft wide folds (pure; >= 0, at most ``amp``; the same every build; ``x``, ``y`` from the bed's
    middle): two long low ridges along the bed, one across its foot, each about 25 cm wide and fading along its length,
    over a broad swell of 1.2-1.6 m wavelength. Never a wrinkle shorter than a hand."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    W, D = max(float(w), 0.5), max(float(d), 0.5)
    r1 = np.exp(-((x + 0.22 * W - 0.10 * y) / 0.10) ** 2) * np.exp(-((y + 0.05 * D) / (0.30 * D)) ** 2)
    r2 = 0.8 * np.exp(-((x - 0.20 * W + 0.07 * y) / 0.09) ** 2) * np.exp(-((y + 0.25 * D) / (0.22 * D)) ** 2)
    r3 = 0.6 * np.exp(-((y + 0.36 * D - 0.06 * x) / 0.11) ** 2) * np.exp(-(x / (0.35 * W)) ** 2)
    swell = 0.35 * (0.5 + 0.5 * np.sin(2.0 * np.pi * x / (1.4 * W) + 0.7) * np.sin(2.0 * np.pi * y / (1.2 * D) + 1.1))
    return float(amp) * np.clip((r1 + r2 + r3 + swell) / 1.35, 0.0, 1.0)


def hang_rows(length: float, rho: float) -> np.ndarray:
    """The hanging part's cloth distances past an edge (pure): ``ARC_SEGMENTS`` over the rounded edge (a quarter turn
    of radius ``rho``), then about ``HANG_STEP_M`` apart down to ``length``; empty for no hang."""
    length = float(length)
    if length <= 1e-9:
        return np.zeros(0)
    arc = math.pi / 2.0 * float(rho)
    if length <= arc + 1e-9:
        n = max(1, int(math.ceil(ARC_SEGMENTS * length / arc)))
        return length * np.arange(1, n + 1) / n
    s_arc = arc * np.arange(1, ARC_SEGMENTS + 1) / ARC_SEGMENTS
    n = max(1, int(math.ceil((length - arc) / HANG_STEP_M)))
    return np.concatenate([s_arc, arc + (length - arc) * np.arange(1, n + 1) / n])


def cover_grid(xs, ys, host, hang: dict, hem_z: float, offset: float, thickness: float, wrinkle_m: float = 0.0,
               side_folds: bool = True, flare: Optional[dict] = None, top_folds: bool = True,
               bed_size: Optional[Sequence[float]] = None, round_m: float = 0.0) -> dict:
    """A draped cover (a duvet, a blanket) in the bed's frame (pure numpy; x across, -y the foot, z up).

    ``xs`` / ``ys``: the columns and rows of its top (ascending; the top spans the host from ``xs[0]`` to ``xs[-1]`` and
    from ``ys[0]`` (its foot edge) to ``ys[-1]`` (its head end)), ``host`` ``(len(xs), len(ys))``: the host's smooth top
    there (``envelope``); ``hang``: ``{"left"|"right"|"foot": length}`` the cloth past that edge (0: it ends on the
    edge, thinned to its seam), the rounded edge included; ``hem_z``: the one level every hanging edge point's drop is
    scaled to end on; ``flare``: ``{side: (depths below the edge top, extra out)}`` a frame or a base wider than the
    top below it (cleared ``FLARE_M`` before it). The top: the host + ``offset`` + the cloth's thickness +
    ``soft_folds`` (fading within ``TOP_FOLD_EDGE_M`` of the edges; ``bed_size`` places them, default the top's own
    size); past an edge: a quarter turn of radius ``offset + thickness`` (its underside ``offset`` off the host's
    corner; or ``round_m`` when larger: a blanket's soft roll over the duvet's edge), then
    straight down that side's plane (one level hem, a straight side), a few soft folds (``SIDE_FOLD_PITCH_M``) growing
    to the hem; at a foot corner the cloth turns round the corner on the same radius (a level skirt). The cloth thins
    to ``RIM_SHARE`` of its thickness over its last ``RIM_M``.

    ``{"grid" (nu + 1, nv + 1, 3) its top surface, "local" (flat cloth coordinates: past an edge, the edge plus the
    cloth's distance), "thickness" (per point), "on_top", "hang_s", "out_dir", "edge_local", "arc_m", "nu", "nv",
    "edges": (x0, x1, y0, y1), "split": {"left", "right", "foot"} columns or rows past each edge, "side", "hem_z"}``."""
    xs = np.asarray(xs, dtype=np.float64)
    ys = np.asarray(ys, dtype=np.float64)
    H = np.asarray(host, dtype=np.float64)
    rho = float(offset) + float(thickness)
    R = max(rho, float(round_m or 0.0))
    arc = math.pi / 2.0 * R
    sl, sr, sf = (hang_rows(float(hang.get(k) or 0.0), R) for k in ("left", "right", "foot"))
    X = np.concatenate([xs[0] - sl[::-1], xs, xs[-1] + sr])
    Y = np.concatenate([ys[0] - sf[::-1], ys])
    nl, nx, nf, ny = len(sl), len(xs), len(sf), len(ys)
    ones = np.ones((len(X), len(Y)))
    ix = np.clip(np.arange(len(X)) - nl, 0, nx - 1)
    iy = np.clip(np.arange(len(Y)) - nf, 0, ny - 1)
    vx = np.where(X < xs[0], X - xs[0], np.where(X > xs[-1], X - xs[-1], 0.0))[:, None] * ones
    vy = np.where(Y < ys[0], Y - ys[0], 0.0)[None, :] * ones
    s = np.maximum(np.abs(vx), np.abs(vy))                     # Chebyshev: a level skirt round a corner
    nrm = np.hypot(vx, vy)
    ux = np.where(nrm > 1e-12, vx / np.maximum(nrm, 1e-12), 0.0)
    uy = np.where(nrm > 1e-12, vy / np.maximum(nrm, 1e-12), 0.0)
    EX = xs[ix][:, None] * ones
    EY = ys[iy][None, :] * ones
    HE = H[np.ix_(ix, iy)]
    # the seam: the cloth thins over its last RIM_M (its flat distance to its rim)
    rim = np.minimum(np.minimum((X - X[0])[:, None], (X[-1] - X)[:, None]),
                     np.minimum((Y - Y[0])[None, :], (Y[-1] - Y)[None, :]))
    t = float(thickness) * (RIM_SHARE + (1.0 - RIM_SHARE) * smoothstep(rim / RIM_M))
    on_top = s <= 1e-12
    # the top: the host's smooth top, the cloth's thickness and its few soft folds
    z = HE + float(offset) + t
    if top_folds and wrinkle_m > 0.0:
        inside = np.minimum(np.minimum(EX - xs[0], xs[-1] - EX), np.minimum(EY - ys[0], ys[-1] - EY))
        bw, bd = (float(v) for v in (bed_size or (xs[-1] - xs[0], (ys[-1] - ys[0]) / DUVET_SHARE)))
        folds = soft_folds(EX - (xs[0] + xs[-1]) / 2.0, EY - (ys[0] + bd / 2.0), bw, bd, wrinkle_m)
        z = z + np.where(on_top, folds * smoothstep(np.minimum(inside, rim) / TOP_FOLD_EDGE_M), 0.0)
    out = np.zeros_like(s)
    on_arc = (~on_top) & (s <= arc + 1e-12)
    th = np.clip(s / R, 0.0, math.pi / 2.0)
    z = np.where(on_arc, HE + rho - R * (1.0 - np.cos(th)), z)
    out = np.where(on_arc, R * np.sin(th), out)
    z_start = HE + rho - R                              # the rounded edge's end
    down = (~on_top) & ~on_arc
    length = max([float(hang.get(k) or 0.0) for k in ("left", "right", "foot")] + [arc + 1e-6])
    f = np.clip((s - arc) / max(length - arc, 1e-6), 0.0, 1.0)
    z = np.where(down, z_start - f * (z_start - float(hem_z)), z)
    side = np.where(np.abs(vy) > np.abs(vx), 2, np.where(vx < 0.0, 0, 1))      # 0 left, 1 right, 2 foot
    extra = np.zeros_like(s)
    for k, name in enumerate(("left", "right", "foot")):
        prof = (flare or {}).get(name)
        if prof is None:
            continue
        depths, need = (np.asarray(v, dtype=np.float64) for v in prof)
        if not len(depths):
            continue
        delta = np.maximum(0.0, z_start - z)
        # the cloth over a wider part below: out by its width from FLARE_M above it (a gentle flare, never a step)
        ramp = smoothstep((delta[..., None] + FLARE_M - depths[None, None, :]) / FLARE_M)
        got = np.max(np.maximum(need, 0.0)[None, None, :] * ramp, axis=-1)
        extra = np.where(down & (side == k), np.maximum(extra, got), extra)
    fold = np.zeros_like(s)
    if side_folds:
        span_y, span_x = float(ys[-1] - ys[0]), float(xs[-1] - xs[0])
        c = arc
        phi = np.arctan2(np.abs(vy), np.abs(vx))                 # 0 along the side, pi/2 along the foot
        per = np.where(side == 0, ys[-1] - EY, 0.0)
        per = np.where(side == 1, span_y + 2.0 * c + span_x + (EY - ys[0]), per)
        per = np.where(side == 2, span_y + c + (EX - xs[0]), per)
        corner = (np.abs(vx) > 1e-12) & (np.abs(vy) > 1e-12)
        per = np.where(corner & (vx < 0.0), span_y + c * phi / (math.pi / 2.0), per)
        per = np.where(corner & (vx > 0.0), span_y + c + span_x + c * (1.0 - phi / (math.pi / 2.0)), per)
        amp = min(SIDE_FOLD_AMP_M[1], max(SIDE_FOLD_AMP_M[0], 1.6 * float(wrinkle_m or 0.01)))
        fold = np.where(down, amp * smoothstep(f) * (0.5 - 0.5 * np.cos(2.0 * np.pi * per / SIDE_FOLD_PITCH_M + 0.9)),
                        0.0)
    out = np.where(down, R + extra + fold, out)
    grid = np.stack([np.where(on_top, X[:, None] * ones, EX + ux * out),
                     np.where(on_top, Y[None, :] * ones, EY + uy * out), z], axis=-1)
    local = np.stack([X[:, None] * ones, Y[None, :] * ones], axis=-1)
    # the normals: the surface's own on the top; past an edge the turn's (a grid's gradient folds at a foot corner,
    # where the hem's rows meet: a hem point's underside would drop under the hem)
    normals = grid_normals(grid)
    sin_t = np.where(on_arc, np.sin(th), 1.0)
    cos_t = np.where(on_arc, np.cos(th), 0.0)
    turned = np.stack([ux * sin_t, uy * sin_t, cos_t], axis=-1)
    normals = np.where((~on_top)[..., None], turned, normals)
    return {"grid": grid, "local": local, "thickness": t, "on_top": on_top, "hang_s": s, "normals": normals,
            "out_dir": np.stack([ux, uy], axis=-1), "edge_local": np.stack([EX, EY], axis=-1), "arc_m": arc,
            "nu": len(X) - 1, "nv": len(Y) - 1, "edges": (float(xs[0]), float(xs[-1]), float(ys[0]), float(ys[-1])),
            "split": {"left": nl, "right": len(sr), "foot": nf}, "side": side, "hem_z": float(hem_z)}


def grid_normals(grid: np.ndarray) -> np.ndarray:
    """Unit normals of a grid surface (pure): ``d/du x d/dv`` (a cover's grid: up on its top, out of the bed on its
    hanging sides)."""
    g = np.asarray(grid, dtype=np.float64)
    n = np.cross(np.gradient(g, axis=0), np.gradient(g, axis=1))
    ln = np.linalg.norm(n, axis=-1, keepdims=True)
    return n / np.where(ln < 1e-12, 1.0, ln)


def sheet_solid(grid: np.ndarray, thickness, key: str, role: str, normals: Optional[np.ndarray] = None) -> Part:
    """A grid surface as a closed solid (pure numpy, no Python loop per face): its top layer the grid, its underside
    ``thickness`` (a number or one per point) in along the normals (``normals``, default ``grid_normals``), joined at
    the rim; outward faces."""
    g = np.asarray(grid, dtype=np.float64)
    nu1, nv1 = g.shape[:2]
    n = grid_normals(g) if normals is None else np.asarray(normals, dtype=np.float64)
    t = np.broadcast_to(np.asarray(thickness, dtype=np.float64), (nu1, nv1))
    verts = np.concatenate([g.reshape(-1, 3), (g - n * t[..., None]).reshape(-1, 3)], axis=0)
    N = nu1 * nv1
    idx = np.arange(N).reshape(nu1, nv1)
    ring = np.concatenate([idx[:-1, 0], idx[-1, :-1], idx[:0:-1, -1], idx[0, :0:-1]])
    nxt = np.roll(ring, -1)
    rim = np.stack([ring, ring + N, nxt + N, nxt], axis=1)
    faces = np.concatenate([_grid_faces(idx), _grid_faces(idx + N, flip=True), rim], axis=0)
    return _part(verts, faces, key, role)


SHEET_T_M = 0.007                # the turned-down sheet: doubled cotton percale (designer value)
BAND_GAP_M = 0.003               # it lies this far over the duvet
BAND_FOLD_DEG = 135.0            # it wraps the duvet's head edge this far (its end tucked under, never into the bed)


def turn_down_band(cover: dict, band_m: float, sheet_t: float = SHEET_T_M) -> Optional[np.ndarray]:
    """30 Oct 2026 (UL136: "the turned-down band at the head is a thick rigid slab"): the top sheet folded back over
    the duvet's head end (pure): the duvet's rows within ``band_m`` of its head end, every column (it hangs down the
    sides with the duvet), lifted ``BAND_GAP_M`` + ``sheet_t`` along the duvet's normals, then wrapped round the
    duvet's thinned head edge (``BAND_FOLD_DEG``, radius half the edge's thickness + the gap + the sheet): a band
    2-3 cm thick at its neat fold. The band's outer surface grid, None when the duvet has fewer than two rows there."""
    g = np.asarray(cover["grid"], dtype=np.float64)
    loc = np.asarray(cover["local"], dtype=np.float64)
    t = np.asarray(cover["thickness"], dtype=np.float64)
    J = g.shape[1] - 1
    rows = np.nonzero(loc[0, :, 1] >= loc[0, J, 1] - float(band_m) - 1e-9)[0]
    if len(rows) < 2:
        return None
    n = np.asarray(cover["normals"], dtype=np.float64) if cover.get("normals") is not None else grid_normals(g)
    band = g[:, rows] + n[:, rows] * (BAND_GAP_M + float(sheet_t))
    head = g[:, J] - g[:, J - 1]
    head /= np.maximum(np.linalg.norm(head, axis=-1, keepdims=True), 1e-12)
    mid = g[:, J] - n[:, J] * (t[:, J] / 2.0)[:, None]
    r = t[:, J] / 2.0 + BAND_GAP_M + float(sheet_t)
    phi = np.radians(np.linspace(0.0, BAND_FOLD_DEG, 6)[1:])
    fold = mid[:, None, :] + r[:, None, None] * (np.cos(phi)[None, :, None] * n[:, J][:, None, :]
                                                 + np.sin(phi)[None, :, None] * head[:, None, :])
    return np.concatenate([band, fold], axis=1)


def band_thickness(band: np.ndarray, sheet_t: float = SHEET_T_M) -> np.ndarray:
    """The band's thickness per point (pure): the sheet's, half of it on its first row (its neat hem on the duvet)."""
    t = np.full(np.asarray(band).shape[:2], float(sheet_t))
    t[:, 0] *= 0.5
    return t


def side_drops(grid: np.ndarray, local: np.ndarray, w: float, d: float, top_z: float, floor_z: float) -> dict:
    """``{"left"|"right"|"foot": {"drop_m", "hem_over_floor_m"}}`` of a built duvet grid: how far it hangs below the
    mattress top past each side (0 where it does not hang)."""
    g, loc = np.asarray(grid), np.asarray(local)
    out = {}
    masks = {"left": loc[..., 0] < -w / 2.0 - 1e-6, "right": loc[..., 0] > w / 2.0 + 1e-6,
             "foot": (loc[..., 1] < -d / 2.0 - 1e-6) & (np.abs(loc[..., 0]) <= w / 2.0 + 1e-6)}
    for side, m in masks.items():
        if not m.any():
            out[side] = {"drop_m": 0.0, "hem_over_floor_m": round(float(top_z) - float(floor_z), 3)}
            continue
        low = float(g[..., 2][m].min())
        out[side] = {"drop_m": round(max(0.0, float(top_z) - low), 3), "hem_over_floor_m": round(low - float(floor_z),
                                                                                                   3)}
    return out


# -- the look, measured: a lumpy duvet, a wavy hem (30 Oct 2026, UL136) ----------------------------------------------

LUMP_WINDOW_M = 0.30             # a fold narrower than this is a lump (the 29 Oct flutes: 18 cm)
LUMP_MAX_M = 0.006               # the cloth off its own smooth surface (over that window) at most this much ...
HEM_WAVE_MAX_M = 0.012           # ... and its hem at most this much off a level, straight line (height and plan)


def _smooth_1d(a: np.ndarray, pos: np.ndarray, window: float) -> np.ndarray:
    """A moving average over ``window`` metres along ``pos`` (pure; per point)."""
    a, pos = np.asarray(a, dtype=np.float64), np.asarray(pos, dtype=np.float64)
    near = np.abs(pos[:, None] - pos[None, :]) <= window / 2.0
    return (near * a[None, :]).sum(axis=1) / np.maximum(near.sum(axis=1), 1)


def _residual(a: np.ndarray, pos: np.ndarray) -> float:
    """The largest offset of a profile off its ``LUMP_WINDOW_M`` moving average, its ends left out (half a window: the
    average is one-sided there)."""
    a, pos = np.asarray(a, dtype=np.float64), np.asarray(pos, dtype=np.float64)
    if len(a) < 3:
        return 0.0
    keep = (pos >= pos.min() + LUMP_WINDOW_M / 2.0) & (pos <= pos.max() - LUMP_WINDOW_M / 2.0)
    if not keep.any():
        return 0.0
    return float(np.max(np.abs(a - _smooth_1d(a, pos, LUMP_WINDOW_M))[keep]))


def cover_smoothness(grid, local, on_top, edges, side=None, hem_z=None, arc_rows: int = ARC_SEGMENTS) -> dict:
    """The look of a built cover, measured (pure; 30 Oct 2026, UL136: "the duvet's hanging sides ripple in big lumpy
    waves like melted foam, the hem is uneven and wavy"; any cover grid: ``grid`` its top surface (bed frame), ``local``
    its flat cloth coordinates, ``on_top``, ``edges`` = (x0, x1, y0, y1) of its top): ``top_lump_m`` = the top's
    largest height off its own ``LUMP_WINDOW_M`` moving average along and across the bed (out of
    ``TOP_FOLD_EDGE_M`` of its edges); per hanging side (left, right: the columns past x0 / x1; foot: the rows past y0)
    ``side_lump_m`` = the hanging cloth's largest plan offset off its moving average along the side (below the
    ``arc_rows`` of its rounded edge, above the hem), ``hem_wave_m`` = the hem's spread in height and its plan offset
    off its moving average along the side. A lumpy duvet or a wavy hem: over ``LUMP_MAX_M`` / ``HEM_WAVE_MAX_M``
    (``review``: ``lumpy_duvet``, ``wavy_hem``)."""
    g = np.asarray(grid, dtype=np.float64)
    loc = np.asarray(local, dtype=np.float64)
    on = np.asarray(on_top, dtype=bool)
    x0, x1, y0, y1 = (float(v) for v in edges)
    inner = on & (loc[..., 0] >= x0 + TOP_FOLD_EDGE_M) & (loc[..., 0] <= x1 - TOP_FOLD_EDGE_M) \
        & (loc[..., 1] >= y0 + TOP_FOLD_EDGE_M) & (loc[..., 1] <= y1 - TOP_FOLD_EDGE_M)
    lump = 0.0
    for i in range(g.shape[0]):                      # along the bed
        m = inner[i]
        if m.sum() >= 3:
            lump = max(lump, _residual(g[i, m, 2], loc[i, m, 1]))
    for j in range(g.shape[1]):                      # across it
        m = inner[:, j]
        if m.sum() >= 3:
            lump = max(lump, _residual(g[m, j, 2], loc[m, j, 0]))
    cols_l = np.nonzero(loc[:, 0, 0] < x0 - 1e-9)[0]
    cols_r = np.nonzero(loc[:, 0, 0] > x1 + 1e-9)[0]
    rows_f = np.nonzero(loc[0, :, 1] < y0 - 1e-9)[0]
    top_rows = np.nonzero(loc[0, :, 1] >= y0 - 1e-9)[0]
    top_cols = np.nonzero((loc[:, 0, 0] >= x0 - 1e-9) & (loc[:, 0, 0] <= x1 + 1e-9))[0]
    parts = {}
    if len(cols_l) > arc_rows:        # hem first: the leftmost column; along the side: the rows on the top
        parts["left"] = (-g[cols_l[:len(cols_l) - arc_rows]][:, top_rows, 0], g[cols_l[0], top_rows, 2],
                         loc[0, top_rows, 1])
    if len(cols_r) > arc_rows:
        sel = cols_r[arc_rows:][::-1]
        parts["right"] = (g[sel][:, top_rows, 0], g[cols_r[-1], top_rows, 2], loc[0, top_rows, 1])
    if len(rows_f) > arc_rows:
        sel = rows_f[:len(rows_f) - arc_rows]
        parts["foot"] = (-g[top_cols][:, sel, 1].T, g[top_cols, rows_f[0], 2], loc[top_cols, 0, 0])
    sides = {}
    for name, (offs, hem, pos) in parts.items():
        side_lump = max([_residual(offs[k], pos) for k in range(1, offs.shape[0])] or [0.0])
        hem_spread = float(np.ptp(hem)) if len(hem) else 0.0
        sides[name] = {"side_lump_m": round(side_lump, 4), "hem_wave_m": round(max(hem_spread, _residual(offs[0], pos)),
                                                                                 4)}
    out = {"top_lump_m": round(lump, 4), "sides": sides, "rule": RULE_LOOK,
           "max_m": {"lump": LUMP_MAX_M, "hem_wave": HEM_WAVE_MAX_M}}
    out["lumpy"] = bool(lump > LUMP_MAX_M or any(v["side_lump_m"] > LUMP_MAX_M for v in sides.values()))
    out["wavy_hem"] = bool(any(v["hem_wave_m"] > HEM_WAVE_MAX_M for v in sides.values()))
    return out


# -- the throw's fringe ----------------------------------------------------------

FRINGE_M = 0.08                  # the strands' length (2 drape columns of 4 cm)
FRINGE_PITCH_M = 0.014           # one strand every 1.4 cm along the throw's end
FRINGE_W_M = 0.005
FRINGE_T_M = 0.0025
FRINGE_LIFT_M = 0.003            # over the surface the strand lies on


def fringe_strands(columns: np.ndarray, key: str, role: str = "fringe", pitch: float = FRINGE_PITCH_M,
                   width: float = FRINGE_W_M, thick: float = FRINGE_T_M) -> Optional[Part]:
    """The strands of one end of a throw (pure): ``columns`` = the draped grid's columns past the cloth's end
    ``(k + 1, nv + 1, 3)``, column 0 on the cloth's edge, the last at the strands' tips (they lie on the bed or hang
    over its side as the drape did). Strands every ``pitch`` along the end (interpolated between the drape's rows),
    each a thin flat ribbon (``width`` x ``thick``) along its column path; one part for the whole end."""
    cols = np.asarray(columns, dtype=np.float64)
    if cols.ndim != 3 or cols.shape[0] < 2 or cols.shape[1] < 2:
        return None
    k1, nv1 = cols.shape[0], cols.shape[1]
    seg = np.linalg.norm(np.diff(cols[0], axis=0), axis=1)
    length = float(seg.sum())
    n = max(2, int(length / pitch))
    pos = np.concatenate([[0.0], np.cumsum(seg)])
    targets = np.linspace(pitch * 0.5, max(pitch * 0.5, length - pitch * 0.5), n)
    jj = np.clip(np.searchsorted(pos, targets, side="right") - 1, 0, nv1 - 2)
    f = ((targets - pos[jj]) / np.maximum(seg[jj], 1e-9))[:, None]
    path = cols[:, jj, :] * (1.0 - f)[None] + cols[:, jj + 1, :] * f[None]        # (k1, n, 3)
    path[..., 2] += FRINGE_LIFT_M
    along = np.diff(cols[0], axis=0)[jj]
    along /= np.maximum(np.linalg.norm(along, axis=1, keepdims=True), 1e-9)
    side = along * (width / 2.0)                                                   # (n, 3) across the strand
    up = np.array([0.0, 0.0, thick / 2.0])
    corners = np.stack([path - side[None] - up, path + side[None] - up, path + side[None] + up,
                        path - side[None] + up], axis=2)                          # (k1, n, 4, 3)
    verts = corners.transpose(1, 0, 2, 3).reshape(-1, 3)                          # strand-major
    base = (np.arange(n) * k1 * 4)[:, None, None]
    seg_i = np.arange(k1 - 1)[None, :, None] * 4
    faces = []
    for q in range(4):                                                             # the four long sides
        a, b = q, (q + 1) % 4
        faces.append(np.concatenate([base + seg_i + a, base + seg_i + 4 + a, base + seg_i + 4 + b,
                                     base + seg_i + b], axis=2).reshape(-1, 4))
    caps0 = (np.arange(n) * k1 * 4)[:, None] + np.array([3, 2, 1, 0])[None, :]
    caps1 = (np.arange(n) * k1 * 4 + (k1 - 1) * 4)[:, None] + np.array([0, 1, 2, 3])[None, :]
    allf = np.concatenate(faces + [caps0, caps1], axis=0)
    return _part(verts, allf, key, role) | {"strands": int(n)}


# -- the accent cushions and the lumbar: stacked on the meshes' profiles ---------

STACK_DZ_M = 0.015               # the height bins the back and front profiles are compared in
STACK_PRESS_M = 0.008            # a cushion presses this far into the soft pillow behind it
STACK_SINK_M = 0.02              # = rest.SOFT_SINK_M: it sinks this far into the bedding it stands on
STACK_LEANS: tuple[float, ...] = (16.0, 22.0, 30.0, 38.0, 46.0)
STACK_UPPER_SHARE = 0.45         # its upper part (this share of its height) rests on what is behind it ...
STACK_BACK_GAP_M = 0.015         # ... within this (= rest.REST_TOLERANCES decor_back_gap_m)


def _profile(points: np.ndarray, z0: float, top: float, dz: float, use_max: bool) -> np.ndarray:
    """Per height bin of ``dz`` from ``z0`` up to ``top``: the max (back) or min (front) y of the points in it, NaN
    where none."""
    nb = max(1, int(math.ceil((top - z0) / dz)))
    out = np.full(nb, np.nan)
    if not len(points):
        return out
    k = np.floor((points[:, 2] - z0) / dz).astype(np.int64)
    ok = (k >= 0) & (k < nb)
    k, y = k[ok], points[ok, 1]
    if not len(k):
        return out
    order = np.argsort(k, kind="stable")
    k, y = k[order], y[order]
    uniq, start = np.unique(k, return_index=True)
    red = np.maximum.reduceat(y, start) if use_max else np.minimum.reduceat(y, start)
    out[uniq] = red
    return out


def stack_cushion(behind: np.ndarray, support: np.ndarray, floor_top: float, cx: float, size, key: str,
                  role: str, leans: Sequence[float] = STACK_LEANS) -> Optional[dict]:
    """An accent cushion or a lumbar standing on the bedding and leaning on what stands behind it (pure, bed-local
    frame: x across, -y the foot, z up): ``behind`` = the points of the pillows (and cushions) behind it ``(N, 3)``,
    ``support`` = the points of the duvet and its band under it ``(M, 3)`` (``floor_top`` = the mattress top where
    none is under it). For each lean of ``leans``: the cushion slides towards the head until its back profile meets
    the front profile of what is behind it in its width (``STACK_PRESS_M`` in), its base on the highest support under
    its foot (``STACK_SINK_M`` in), twice; taken when its upper part rests on something (``STACK_UPPER_SHARE``,
    ``STACK_BACK_GAP_M``). ``{"part" (bed-local verts), "y", "z", "lean_deg", "contact_m", "upper_gap_m"}`` or None
    (nothing to lean on)."""
    w, t, h = (float(v) for v in size)
    mesh = plump_cushion(w, t, h, key=key, role=role, sag=0.0)
    base = np.asarray(mesh["verts"], dtype=np.float64)
    behind = np.asarray(behind, dtype=np.float64).reshape(-1, 3)
    support = np.asarray(support, dtype=np.float64).reshape(-1, 3)
    sel = behind[np.abs(behind[:, 0] - cx) <= w / 2.0 - 0.02]
    if not len(sel):
        return None
    for lean in leans:
        L = lean_verts(base, lean)
        L[:, 0] += cx
        z0 = float(floor_top) - STACK_SINK_M
        y = None
        for _round in range(3):
            top = z0 + float(L[:, 2].max())
            back = _profile(np.c_[L[:, 0], L[:, 1], L[:, 2] + z0], z0, top, STACK_DZ_M, True)
            front = _profile(sel, z0, top, STACK_DZ_M, False)
            both = ~np.isnan(back) & ~np.isnan(front)
            if not both.any():
                break
            y = float(np.min(front[both] - back[both])) + STACK_PRESS_M
            foot = L[L[:, 2] <= 0.03]
            y_lo, y_hi = y + float(foot[:, 1].min()), y + float(foot[:, 1].max())
            under = support[(np.abs(support[:, 0] - cx) <= w / 2.0) & (support[:, 1] >= y_lo - 0.01)
                            & (support[:, 1] <= y_hi + 0.01)]
            z_new = (float(under[:, 2].max()) if len(under) else float(floor_top)) - STACK_SINK_M
            if abs(z_new - z0) < 1e-3:
                z0 = z_new
                break
            z0 = z_new
        if y is None:
            continue
        top = z0 + float(L[:, 2].max())
        back = _profile(np.c_[L[:, 0], L[:, 1] + y, L[:, 2] + z0], z0, top, STACK_DZ_M, True)
        front = _profile(sel, z0, top, STACK_DZ_M, False)
        both = ~np.isnan(back) & ~np.isnan(front)
        gaps = front - back
        upper = np.arange(len(back)) >= int(len(back) * (1.0 - STACK_UPPER_SHARE))
        upper_gap = float(np.min(gaps[both & upper])) if (both & upper).any() else None
        if upper_gap is None or upper_gap > STACK_BACK_GAP_M:
            continue
        verts = np.c_[L[:, 0], L[:, 1] + y, L[:, 2] + z0]
        part = dict(mesh, verts=[tuple(p) for p in verts.tolist()])
        return {"part": part, "y": round(y, 4), "z": round(z0, 4), "lean_deg": float(lean),
                "contact_m": round(float(np.min(gaps[both])), 4), "upper_gap_m": round(upper_gap, 4)}
    return None


def face_points(parts: Sequence[Part]) -> np.ndarray:
    """The vertices and face centres of parts ``(N, 3)`` (a denser sample of their surfaces than the vertices)."""
    out = []
    for p in parts or []:
        v = np.asarray(p["verts"], dtype=np.float64).reshape(-1, 3)
        out.append(v)
        quads = [f for f in p["faces"] if len(f) == 4]
        if quads:
            out.append(v[np.asarray(quads, dtype=np.int64)].mean(axis=1))
    return np.concatenate(out, axis=0) if out else np.zeros((0, 3))


# -- R36: the nightstand's decor set -------------------------------------------------

BEDSIDE_SET_SIZES: tuple[tuple[float, float], ...] = ((0.30, 0.18), (0.26, 0.16), (0.22, 0.14))
BEDSIDE_SET_H_M = 0.55           # the palm leaf's top
BEDSIDE_SET_MIN_H_M = 0.28
BEDSIDE_SET_KEYS = ("ceramic", "pampas", "dark", "painted")


def _lathe(cx: float, cy: float, rings: Sequence[tuple[float, float]], n: int, key: str, role: str,
           twist: float = 0.5) -> Part:
    """A faceted body of revolution (pure): ``rings`` = ``[(z, radius)]`` bottom to top, ``n`` sides, every second
    ring turned by ``twist`` of a side (diamond facets: the geometric vases of R36), closed at both ends."""
    zs = np.array([r[0] for r in rings], dtype=np.float64)
    rs = np.array([r[1] for r in rings], dtype=np.float64)
    m = len(rings)
    turn = (np.arange(m) % 2) * twist * 2.0 * np.pi / n
    a = 2.0 * np.pi * np.arange(n)[None, :] / n + turn[:, None]
    ring = np.stack([cx + rs[:, None] * np.cos(a), cy + rs[:, None] * np.sin(a), np.repeat(zs[:, None], n, 1)],
                    axis=-1).reshape(-1, 3)
    verts = np.concatenate([ring, [[cx, cy, zs[0]], [cx, cy, zs[-1]]]], axis=0)
    idx = np.arange(m * n).reshape(m, n)
    faces = []
    for r in range(m - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append([idx[r, k], idx[r, k1], idx[r + 1, k1], idx[r + 1, k]])
    bot, top = m * n, m * n + 1
    faces += [[bot, idx[0, (k + 1) % n], idx[0, k]] for k in range(n)]
    faces += [[top, idx[-1, k], idx[-1, (k + 1) % n]] for k in range(n)]
    return {"verts": [tuple(p) for p in verts.tolist()], "faces": [[int(i) for i in f] for f in faces], "key": key,
            "role": role}


def _blade(base, tip, width: float, fold: float, key: str) -> tuple[list, list]:
    """One narrow blade of a dried palm fan: a thin folded strip from ``base`` to ``tip`` (V cross-section)."""
    b, t = np.asarray(base, dtype=np.float64), np.asarray(tip, dtype=np.float64)
    along = t - b
    ln = float(np.linalg.norm(along)) or 1e-6
    u = along / ln
    side = np.cross(u, [0.0, 0.0, 1.0])
    if np.linalg.norm(side) < 1e-6:
        side = np.array([1.0, 0.0, 0.0])
    side /= np.linalg.norm(side)
    up = np.cross(side, u)
    pts = []
    for s in (0.0, 0.35, 0.7, 1.0):
        c = b + along * s
        half = width / 2.0 * (math.sin(math.pi * min(1.0, s + 0.15)) if s < 1.0 else 0.15)
        pts += [c - side * half, c + up * fold * (1.0 - s * 0.5), c + side * half]
    faces = []
    for r in range(3):
        a0 = r * 3
        faces += [[a0, a0 + 3, a0 + 4, a0 + 1], [a0 + 1, a0 + 4, a0 + 5, a0 + 2]]
    return [tuple(map(float, p)) for p in pts], faces


def bedside_set_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """R36 (P11): a nightstand's decor set in its box ``w x d x h`` (bottom on z = 0, front -Y): a tall white faceted
    vase at the back left holding a dried palm leaf (a thin stem and a fan of narrow folded blades up to ``h``), a
    short round faceted vase at the front right, a small black box with a white lid at the front left. Keys:
    ``ceramic`` (white glaze), ``pampas`` (the dried leaf), ``dark`` (the box), ``painted`` (its lid)."""
    w, d, h = float(w), float(d), float(h)
    parts: list[Part] = []
    ra = min(0.055, d / 3.2)
    ha = min(0.24, h * 0.45)
    ax, ay = -w / 2.0 + ra + 0.005, d / 2.0 - ra - 0.005
    parts.append(_lathe(ax, ay, [(0.0, ra * 0.62), (ha * 0.18, ra), (ha * 0.55, ra * 0.86), (ha * 0.86, ra * 0.52),
                                 (ha, ra * 0.58)], 8, "ceramic", "vase"))
    rb = min(0.06, d / 3.0, w / 5.0)
    hb = min(0.14, h * 0.26)
    bx, by = w / 2.0 - rb - 0.005, -d / 2.0 + rb + 0.005
    parts.append(_lathe(bx, by, [(0.0, rb * 0.5), (hb * 0.3, rb * 0.95), (hb * 0.62, rb), (hb * 0.9, rb * 0.7),
                                 (hb, rb * 0.42)], 7, "ceramic", "vase"))
    bw, bd = min(0.10, w * 0.32), min(0.08, d * 0.42)
    bxx, byy = -w / 2.0 + bw / 2.0 + 0.005, -d / 2.0 + bd / 2.0 + 0.005
    from wenart.blender import geom2d

    v, f = geom2d.box((bxx, byy, 0.0225), (bw, bd, 0.045), 0.0)
    parts.append({"verts": v, "faces": f, "key": "dark", "role": "box"})
    v, f = geom2d.box((bxx, byy, 0.045 + 0.0075), (bw + 0.004, bd + 0.004, 0.015), 0.0)
    parts.append({"verts": v, "faces": f, "key": "painted", "role": "lid"})
    # the dried palm leaf: a stem from the tall vase's mouth, a fan of blades at its top (inside the box)
    stem_top = (ax + min(0.05, w * 0.15), ay - 0.01, h * 0.62)
    stem_base = (ax, ay, ha * 0.9)
    from wenart.blender.detail_parts import _rod

    parts.append(_rod(stem_base, stem_top, 0.0025, "pampas", "stem", n=5))
    fan_r = min(0.20, h - stem_top[2] - 0.005, w * 0.6)
    nb = 11
    verts, faces = [], []
    for k in range(nb):
        a = math.radians(-70.0 + 140.0 * k / (nb - 1))
        tip = (stem_top[0] + math.sin(a) * fan_r * 0.9, stem_top[1] - 0.02 * math.cos(a),
               stem_top[2] + math.cos(a) * fan_r)
        tip = (min(max(tip[0], -w / 2.0 + 0.003), w / 2.0 - 0.003), tip[1], min(tip[2], h - 0.003))
        bv, bf = _blade(stem_top, tip, 0.022, 0.006, "pampas")
        off = len(verts)
        verts += bv
        faces += [[i + off for i in q] for q in bf]
    parts.append({"verts": verts, "faces": faces, "key": "pampas", "role": "leaf"})
    return parts


# --------------------------------------------------------------------------
# A library bed's own bedding, measured on its mesh (item 5 of UL121)
# --------------------------------------------------------------------------

BUMP_MIN_M = 0.06                # pillows rise at least this over the duvet at the head of a made-up bed
RELIEF_MIN_M = 0.006             # a modelled duvet's folds (p90 - p10 of the top over the middle of the bed)
FLAT_DENSITY = 50.0              # vertices per m2 on the top under which a cover is a few big faces (flat)
RELIEF_CELL_M = 0.10


TOP_BAND_M = 0.12                # a cell whose top is this far under the cover's top lies under one big face
TOP_SHARE_MIN = 0.5              # under this share of the middle's cells on the top, the cover is a few big faces
PILLOW_BAND_M = (0.02, 0.40)     # pillows rise this far over the cover; a headboard's top lies above the band
PILLOW_VERTS_MIN = 40            # vertices in that band at the head a modelled pillow set has at least
HEADBOARD_SKIP_M = 0.12          # the head edge's strip a headboard stands in (never a pillow)


def surface_samples(verts, tris, step: float = RELIEF_CELL_M):
    """Points on the large faces of a mesh (pure numpy): every triangle larger than a ``step`` square gets points on a
    barycentric grid about ``step`` apart, so a cover of a few big faces shows its top where it has no vertex (30 Oct
    2026: a storage bed's mattress of two faces over its drawers). ``tris``: ``(T, 3)`` vertex indices."""
    v = np.asarray(verts, dtype=float).reshape(-1, 3)
    t = np.asarray(tris, dtype=int).reshape(-1, 3)
    if not len(v) or not len(t):
        return np.empty((0, 3))
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    big = np.nonzero(area > step * step)[0]
    out = []
    for k in big:                               # few faces: a dense mesh has next to none this large
        n = int(min(60, max(2, math.ceil(math.sqrt(2.0 * area[k]) / step))))
        i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing="ij")
        m = (i + j) <= n
        u, w = i[m] / n, j[m] / n
        out.append(a[k] + u[:, None] * (b[k] - a[k]) + w[:, None] * (c[k] - a[k]))
    return np.concatenate(out) if out else np.empty((0, 3))


def bedding_relief(world_verts, centre, rot: float, size) -> dict:
    """The top of a bed model's bedding (pure, numpy on its vertices: no ray): over a ``RELIEF_CELL_M`` grid of its
    footprint (10 cm in from the sides) the highest vertex per cell. ``top_m`` = the cover's top (p95 of the
    middle's cells: the middle half of the bed; ``world_verts`` with ``surface_samples`` of its big faces), ``top_share`` = the share of the middle's cells on that top (within
    ``TOP_BAND_M``; a mattress of a few big faces leaves its middle cells to the frame or drawers under it),
    ``relief_m`` = p90 - p10 of the top cells, ``density`` = vertices per m2 within 3 cm of the top, ``pillow_bump_m`` =
    the highest of the head zone's vertices ``PILLOW_BAND_M`` over the top (out of the headboard's strip), with
    ``pillow_vertices`` of them.

    30 Oct 2026 (user on real04 run 20261029-201533-full: "this bed model needs fixing some sheets etc"): the cover's
    top was the middle's median cell top; a storage bed whose mattress is two big faces had only its drawers' vertices
    in the middle (top 0.02 m, relief 111 mm, 12,719 vertices/m2) and was taken for a folded duvet: it got our pillows
    only. And a headboard counted as pillows (bump 0.82 m on another bed)."""
    w, d = float(size[0]), float(size[1])
    loc = to_local_arr(centre, rot, world_verts)
    keep = (np.abs(loc[:, 0]) <= w / 2.0 - 0.10) & (np.abs(loc[:, 1]) <= d / 2.0 - 0.05)
    p = loc[keep]
    rec = {"pillow_bump_m": None, "relief_m": None, "density": 0.0, "top_m": None, "vertices": int(len(p))}
    if not len(loc):
        return rec
    if not len(p):        # not one vertex over the bed's inner top: a cover of a few big faces, flat, no pillows
        rec.update(pillow_bump_m=0.0, relief_m=0.0, top_share=0.0,
                   note="no vertex over the inner top: a flat cover of a few faces")
        return rec
    nx = max(1, int((w - 0.2) / RELIEF_CELL_M))
    ny = max(1, int((d - 0.1) / RELIEF_CELL_M))
    ix = np.clip(((p[:, 0] + w / 2.0 - 0.10) / (w - 0.2) * nx).astype(int), 0, nx - 1)
    iy = np.clip(((p[:, 1] + d / 2.0 - 0.05) / (d - 0.1) * ny).astype(int), 0, ny - 1)
    tops = np.full((nx, ny), np.nan)
    np.fmax.at(tops, (ix, iy), p[:, 2])
    ymid = (np.arange(ny) + 0.5) / ny * (d - 0.1) - (d / 2.0 - 0.05)
    middle = np.abs(ymid) <= d * 0.25
    head = ymid >= d / 2.0 - 0.55
    mid_cells = tops[:, middle]
    if not mid_cells.size:                      # a bed too short for a middle: the cells out of the head zone
        mid_cells = tops[:, ~head]
    mid_tops = mid_cells[~np.isnan(mid_cells)]
    if not len(mid_tops):
        rec.update(pillow_bump_m=0.0, relief_m=0.0, top_share=0.0,
                   note="no vertex over the duvet's part of the top: a flat cover")
        return rec
    top = float(np.percentile(mid_tops, 95))     # the cover's top (a book or a tray on it is no top)
    on_top = mid_tops[mid_tops >= top - TOP_BAND_M]
    share = float(len(on_top)) / float(max(1, mid_cells.size))
    in_mid = (np.abs(p[:, 1]) <= d * 0.25) & (p[:, 2] >= top - 0.03)
    area = max(1e-6, (w - 0.2) * d * 0.5)
    lo, hi = PILLOW_BAND_M
    at_head = (p[:, 1] >= d / 2.0 - 0.55) & (p[:, 1] <= d / 2.0 - 0.05 - HEADBOARD_SKIP_M) \
        & (p[:, 2] >= top + lo) & (p[:, 2] <= top + hi)
    bump = float(p[at_head, 2].max()) - top if at_head.any() else 0.0
    rec.update(top_m=round(top, 4), top_share=round(share, 3),
               relief_m=round(float(np.percentile(on_top, 90) - np.percentile(on_top, 10)), 4),
               density=round(float(in_mid.sum()) / area, 1),
               pillow_bump_m=round(bump, 4), pillow_vertices=int(at_head.sum()))
    return rec


STAND_BUMP_M = 0.22             # 30 Oct 2026 (UL137): pillows lower than this over the cover lie flat (no sham stands)


def dress_mode(asset: Optional[dict], relief: Optional[dict], width: Optional[float] = None
               ) -> tuple[Optional[str], str]:
    """Whether a library bed with its own bedding is dressed by us (UL121, item 5; pure): ``("full" | "pillows" |
    None, reason)``. ``full``: its cover is flat (relief under ``RELIEF_MIN_M``, or fewer vertices on top than
    ``FLAT_DENSITY``: a few big faces) or it has none; ``pillows``: a modelled duvet without pillows (no bump at the
    head over ``BUMP_MIN_M``, or the audit's ``has_pillows`` false): our pillow set only, its duvet kept; None: made
    up as well as ours (its pillows and folds kept).

    30 Oct 2026 (UL137, user on real04's f_L0_007: "head section of this bed needs a rework": two flat pillows lying low
    in front of the headboard, no euro shams, no standing pillows): a bed whose width takes euro shams (``width`` from
    ``SHAM_MIN_BED_W``; None: any) and whose own pillows lie flat (their bump under ``STAND_BUMP_M``) is poorer than
    our set: ``pillows`` (our shams and pillows stand against its headboard, its duvet kept)."""
    a = asset or {}
    r = relief or {}
    bump, rel, dens = r.get("pillow_bump_m"), r.get("relief_m"), float(r.get("density") or 0.0)
    if bump is None or rel is None:
        if a.get("has_bedding") is True and a.get("has_pillows") is False:
            return "pillows", "the audit says the model's bedding has no pillows (no mesh to measure)"
        return None, "the model's bedding could not be measured: kept as made up"
    share = r.get("top_share")
    flat = rel < RELIEF_MIN_M or dens < FLAT_DENSITY or (share is not None and float(share) < TOP_SHARE_MIN)
    few = r.get("pillow_vertices") is not None and int(r["pillow_vertices"]) < PILLOW_VERTS_MIN
    no_pillows = bump < BUMP_MIN_M or few or a.get("has_pillows") is False
    if flat:
        return "full", (f"its cover is flat (relief {rel * 1000:.0f} mm, {dens:.0f} vertices/m2 on top: under "
                        f"{RELIEF_MIN_M * 1000:.0f} mm or {FLAT_DENSITY:.0f}"
                        + (f"; {float(share):.0%} of the middle on the top: under {TOP_SHARE_MIN:.0%}"
                           if share is not None else "") + "): poorer than our duvet")
    if no_pillows:
        return "pillows", (f"its duvet has folds (relief {rel * 1000:.0f} mm) but no pillows (bump {bump:.2f} m < "
                           f"{BUMP_MIN_M} m at the head): our pillow set on it, its duvet kept")
    if bump < STAND_BUMP_M and (width is None or float(width) >= SHAM_MIN_BED_W - 1e-9):
        return "pillows", (f"its pillows lie flat (bump {bump:.2f} m < {STAND_BUMP_M} m: no euro shams, no standing "
                           "pillows; UL137): our shams and pillows stand against its headboard, its duvet kept")
    return None, (f"made up as well as ours: pillows (bump {bump:.2f} m) and folds (relief {rel * 1000:.0f} mm, "
                  f"{dens:.0f} vertices/m2)")


# --------------------------------------------------------------------------
# The review (model review M30, Argus U34)
# --------------------------------------------------------------------------

PROBLEM_LESSONS = {"lumpy_duvet": "UL136", "wavy_hem": "UL136", "head_gap": "UL137"}   # 30 Oct 2026: else UL121
BED_TYPES: tuple[str, ...] = ("bed_single", "bed_double")
BED_ROOM_TYPES: tuple[str, ...] = ("bedroom", "child")
HEM_MAX_M = 0.18                 # a free side's hem at most this over the floor ("almost to the floor")


def _family(built: dict, manifest: Optional[dict]) -> str:
    fam = ((built.get("dressing") or {}).get("family") if isinstance(built.get("dressing"), dict) else None)
    if not fam and isinstance((manifest or {}).get("style_profile"), dict):
        fam = manifest["style_profile"].get("family")
    if not fam:
        for p in built.get("furniture") or []:
            bl = p.get("bedding_layers") if isinstance(p.get("bedding_layers"), dict) else {}
            if bl.get("family"):
                fam = bl["family"]
                break
    return str(fam or "").lower()


def look_problems(look: Optional[dict], what: str) -> list[tuple[str, str]]:
    """30 Oct 2026 (UL136): the problems of a cover's measured look (``cover_smoothness``; pure): ``lumpy_duvet`` (its
    top or a hanging side off its own smooth surface by more than ``LUMP_MAX_M``), ``wavy_hem`` (a hem off a level,
    straight line by more than ``HEM_WAVE_MAX_M``); none for a cover built before the measure."""
    if not isinstance(look, dict):
        return []
    out = []
    sides = look.get("sides") or {}
    if look.get("lumpy"):
        worst = max([float(look.get("top_lump_m") or 0.0)]
                    + [float(v.get("side_lump_m") or 0.0) for v in sides.values()])
        out.append(("lumpy_duvet", f"its {what} is lumpy ({worst * 1000:.0f} mm off its own smooth surface over "
                                   f"{LUMP_WINDOW_M:.2f} m, at most {LUMP_MAX_M * 1000:.0f} mm; UL136)"))
    if look.get("wavy_hem"):
        worst = max(float(v.get("hem_wave_m") or 0.0) for v in sides.values())
        out.append(("wavy_hem", f"its {what}'s hem is wavy ({worst * 1000:.0f} mm off a level straight line, at most "
                                f"{HEM_WAVE_MAX_M * 1000:.0f} mm; UL136)"))
    return out


def review(built: dict, manifest: Optional[dict] = None, check: str = "U34") -> tuple[list[dict], int]:
    """What each bed of a bedroom lacks against its family's set (pure; ``(findings, beds checked)``). With a scene
    manifest, the beds as built: a dressed bed (``dressing.record``) with fewer pillows than its family's set (euro
    shams with no headboard to stand on are explained), a free side (``bed_sides``) whose duvet hangs short of the
    floor (hem over ``HEM_MAX_M``), an old dressing without the family's set, a library bed whose measured bedding was
    poorer than ours left undressed; and every bed's throw: none where the bed takes one, its woven pattern or its
    fringe (where the family has one) missing. Without one, the plan (``bedding_layers.set`` and the throws' weave).
    A finding: ``{check, severity, target, room_id, message, problem, lesson}``; minor, kind ``taste``."""
    fam = _family(built, manifest)
    if not fam:
        return [], 0
    spec, _why = family_spec(fam)
    rooms = {r.get("id"): r for r in built.get("rooms") or [] if r.get("id")}
    entries = {o.get("wenart_id"): o for o in (manifest or {}).get("objects") or []
               if o.get("kind") == "furniture" and o.get("type") in BED_TYPES}
    built_throws: dict[str, list] = {}
    for o in (manifest or {}).get("objects") or []:
        if o.get("kind") == "decor" and o.get("type") == "throw" and o.get("host_id"):
            built_throws.setdefault(o["host_id"], []).append(o)
    out, n = [], 0
    for bed in built.get("furniture") or []:
        room = rooms.get(bed.get("room_id")) or {}
        if bed.get("type") not in BED_TYPES or room.get("room_type") not in BED_ROOM_TYPES or not bed.get("footprint") \
                or bed.get("build", True) is False:
            continue
        n += 1
        _c, _r, (w, _d) = bed_frame(bed)
        want = counts(spec, w)
        problems: list[tuple[str, str]] = []
        if manifest is not None:
            entry = entries.get(bed["id"]) or {}
            rec = (entry.get("dressing") or {}).get("record") or {}
            test = entry.get("bedding_test") or {}
            if rec.get("set"):
                got = rec["set"]
                explained = rec.get("explained") or {}
                short = [f"{want[k] - int(got.get(k) or 0)} {k.replace('_', ' ')}" for k in want
                         if int(got.get(k) or 0) < want[k] and k not in explained]
                if short:
                    problems.append(("too_few_pillows", f"too few pillows for its {fam} set: {', '.join(short)} "
                                                        "missing"))
                for side, sd in (rec.get("sides") or {}).items():
                    drop = (rec.get("drops") or {}).get(side) or {}
                    if sd.get("free") and rec.get("mode") != "pillows" and \
                            float(drop.get("hem_over_floor_m") or 9.0) > HEM_MAX_M:
                        problems.append(("no_overhang", f"no overhang on its free {side} side (the duvet's hem "
                                                        f"{float(drop.get('hem_over_floor_m') or 0.0):.2f} m over the "
                                                        "floor)"))
                problems += look_problems((rec.get("duvet") or {}).get("smoothness"), "duvet")
                head = rec.get("head") or {}
                if float(head.get("gap_m") or 0.0) >= 0.02 and not head.get("closed_by"):
                    problems.append(("head_gap", f"a {float(head['gap_m']):.2f} m gap between the mattress and the "
                                                 "headboard left open (UL137)"))
            elif rec:
                problems.append(("too_few_pillows", f"an old dressing: {rec.get('pillows')} pillow(s), no {fam} set "
                                                    "(shams, accent cushions, lumbar)"))
            elif test.get("poorer"):
                problems.append(("flat_bedding", f"its model's bedding is poorer than ours ({test.get('reason')}) "
                                                 "and was not dressed"))
            throws = built_throws.get(bed["id"]) or []
            asset = bed.get("asset") if isinstance(bed.get("asset"), dict) else {}
            own = test.get("own_bedding") if test else bool(asset.get("has_bedding") or asset.get("has_pillows"))
            dressed = bool(rec) or not own
            if not throws and dressed and entry:
                problems.append(("no_throw", "no throw across its foot"))
            for t in throws:
                weave = t.get("weave") or {}
                problems += look_problems(weave.get("blanket_look"), "blanket")
                if spec["throw"].get("pattern") and not weave.get("pattern"):
                    problems.append(("throw_pattern", f"its throw has no woven pattern (the {fam} set: "
                                                      f"{spec['throw']['pattern']})"))
                ends = weave.get("fringe_ends")
                if spec["throw"].get("fringe") and not weave.get("fringe_strands") and (ends is None or ends):
                    problems.append(("throw_fringe", "its throw has no fringe"))
        else:
            layers = bed.get("bedding_layers") if isinstance(bed.get("bedding_layers"), dict) else {}
            if not layers.get("set"):
                problems.append(("too_few_pillows", f"no {fam} bedding set planned (bedding_layers.set)"))
            throws = [d for d in built.get("decor") or [] if d.get("type") == "throw" and d.get("host_id") == bed["id"]]
            for t in throws:
                if spec["throw"].get("pattern") and not (t.get("weave") or {}).get("pattern"):
                    problems.append(("throw_pattern", "its throw has no woven pattern planned"))
        for problem, text in problems:
            lesson = PROBLEM_LESSONS.get(problem, LESSON)
            out.append({"check": check, "severity": "minor", "target": bed["id"], "room_id": bed.get("room_id"),
                        "problem": problem, "lesson": lesson, "family": fam,
                        "message": f"the bed {bed['id']} misses its {fam} bedding ({lesson}, R35): {text}"})
    return out, n
