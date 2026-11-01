"""Bedding and cushion sets with variety, real sizes and real detail (1 Nov 2026, lessons UL236 and UL238).

User on real04 run 20261031-194116-full: "bedding seem to be using the same set of pillows sheets etc, use better
models better textures, more details and more variants, consider the size of the bedding and previous beddings that
already exist in the models" (UL236), and on the sofas: "This pillow going over the sofa, when you are bedding the sofas
or beds consider the sizes and the final look, try to use better more detailed models with better textures, and
realistic looking pillows" (UL238), "Same comment as before related to bedding on this sofa, better model better
texture, more logical placement" (the white corner sofa of the living room).

What (pure: numpy and ``wenart.blender.bedding_parts``; no ``bpy``, no shapely; the decor stage and the build read it):

- ``bed_variant`` / ``house_bed_variants``: every bed of a house gets its own set, chosen deterministically from its id
  (``stable_hash``, never a random number) out of its style family's palette (``FAMILY_TEXTILES``,
  ``FAMILY_PALETTE``): the arrangement (``ARRANGEMENTS``: one pillow on a single bed, two sleeping pillows with a
  lumbar, two to three accents, four stacked pillows, euro shams with a lumbar or an accent, three shams on a king),
  the textiles (washed linen, cotton percale, sateen, waffle, knit, chunky knit, velvet, boucle, wool), a quilted
  coverlet's stitching (channel, box, diamond) or a plain duvet, the fold-back at the head (the top sheet or the duvet
  itself), the colourway (the room's scheme first: the brief's cushion and throw colours) and the throw (folded
  across the foot, a bed runner, a corner drape, a quilt folded at the foot, the P14 pair). No two beds of a house get
  the same signature; a master bedroom (``bed_rank``: a bedroom with its own bathroom, else the widest bed in the
  largest bedroom) takes the richest arrangements, a child's room or a single bed the plainest.
- ``bed_sizes``: every piece sized to the bed's mattress (``mattress_class``: single, small double, queen, king):
  pillow widths and counts follow the width (a single bed: one pillow, never two squeezed in; a king: king pillows),
  the shams, the accents and the lumbar by class.
- ``expected``: what a bed's set holds (the variant's arrangement; ``bedding_parts.counts`` for a set without one) and
  its fallback when no headboard holds the shams (``shams=False``: never more than ``bedding_parts.PIECES_MAX``).
- the meshes: ``cushion_parts`` (a filled cushion with its finish: a flange, piping (a cord along the seam in the
  accent colour), a knife edge, a tufted centre with buttons, corner tassels), ``quilt_depth`` (the stitching grooves
  of a quilted coverlet), ``folded_throw_parts`` (a throw folded flat in layers with soft rounded folds).
- ``seat_cushion_plan``: the cushions of a sofa, a corner sofa, a chaise or an armchair: arranged for the piece's shape
  (symmetric graded pairs at the ends of a straight sofa, a group in the corner of an L and a pair at its open end, one
  on an armchair), sized in proportion to the back's height and the seat's depth (``seat_cushion_size``), in a set of
  its own (looks, finishes, colours; deterministic per piece, no two seats of a house alike).

Why: every bed of the run got the same set (two white euro shams, two white pillows, one mustard cushion, a grey band,
a gingham throw laid flat across the foot), a library bed with its own pillows got ours in front of them, the throw
read
as a flat printed sheet, the duvet as a plain slab; a sofa cushion stood on the back of a low sofa (oversized, its top
far over the back), four cushions stood evenly spaced along a 4.4 m corner sofa.

How: every number is a designer value of real products (assumed): a 65 x 45 cm pillow on a double bed, 85 x 50 cm on
a king, 60 x 45 cm on a small double; a 65 cm euro sham (60 cm on a small double), a 40-50 cm accent cushion by bed
class, a lumbar of 40-60 x 26-32 cm; a sofa cushion 30-55 cm by its back's height (``SEAT_SIZES``), its top at most
``BACK_OVER_M`` (or ``BACK_OVER_SHARE`` of its height) over the back.
"""
from __future__ import annotations

import hashlib
import math
from typing import Iterable, Optional, Sequence

import numpy as np

from wenart.blender import bedding_parts as BP

RULE_BED = "bedding.ul236"
RULE_SEAT = "cushions.ul238"
LESSON_BED = "UL236"
LESSON_SEAT = "UL238"
TAG_BED = ("1 Nov 2026, user: \"bedding seem to be using the same set of pillows sheets etc, use better models better "
           "textures, more details and more variants, consider the size of the bedding\"")
TAG_SEAT = ("1 Nov 2026, user: \"when you are bedding the sofas or beds consider the sizes and the final look, try to "
            "use better more detailed models with better textures, and realistic looking pillows\"")
Part = dict


def stable_hash(*parts) -> int:
    """A stable integer of ``parts`` (sha256 of their text; the same every run, unlike ``hash``)."""
    return int(hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:12], 16)


# --------------------------------------------------------------------------
# The mattress and its sizes
# --------------------------------------------------------------------------

MATTRESS_CLASSES: tuple[tuple[str, float], ...] = (("single", 1.20), ("small_double", 1.45), ("queen", 1.75),
                                                   ("king", 99.0))
PILLOW_MAX_W: dict[str, float] = {"single": 0.65, "small_double": 0.60, "queen": 0.65, "king": 0.85}
PILLOW_TH: dict[str, tuple[float, float]] = {"single": (0.14, 0.42), "small_double": (0.15, 0.45),
                                              "queen": (0.15, 0.45), "king": (0.16, 0.50)}
SHAM_MAX_W: dict[str, float] = {"single": 0.60, "small_double": 0.60, "queen": 0.65, "king": 0.65}
SHAM_T_M = 0.14
ACCENT_W: dict[str, float] = {"single": 0.40, "small_double": 0.42, "queen": 0.45, "king": 0.50}
ACCENT_T_M = 0.15
LUMBAR: dict[str, tuple[float, float, float]] = {"single": (0.40, 0.12, 0.26), "small_double": (0.45, 0.13, 0.28),
                                                 "queen": (0.50, 0.13, 0.30), "king": (0.60, 0.14, 0.32)}
MATTRESS_MARGIN_M = 0.10        # the pillows stay this far inside the bed's width (both sides together) ...
PILLOW_GAP_M = 0.04             # ... and this far apart
PILLOW_MIN_W_M = 0.40


def mattress_class(width: float) -> str:
    """The mattress class of a bed of ``width`` (its fitted footprint, m; pure): single (under 1.20), small double
    (under 1.45), queen (under 1.75), king."""
    w = float(width)
    for name, upper in MATTRESS_CLASSES:
        if w < upper - 1e-9:
            return name
    return "king"


def bed_sizes(width: float, want: dict, stacked: bool = False, single: bool = False) -> dict:
    """The sizes of a bed's pieces (pure; ``(width, thickness, height)`` each, m): the sleeping pillows share the width
    (``PILLOW_MAX_W`` by class, ``MATTRESS_MARGIN_M``, ``PILLOW_GAP_M``: a single bed's one pillow is at most its width
    less 20 cm), the euro shams share it too (``SHAM_MAX_W``, nearly square), the accents and the lumbar by class (the
    lumbar never wider than the bed less 20 cm). ``stacked`` (four stacked pillows): the back row is the pillows'
    size."""
    w = float(width)
    c = "single" if single else mattress_class(w)
    n = max(1, int(want.get("pillows") or 1))
    pw = min(PILLOW_MAX_W[c], (w - MATTRESS_MARGIN_M) / n - PILLOW_GAP_M)
    if n == 1:
        pw = min(PILLOW_MAX_W[c], w - 0.20)
    pw = max(PILLOW_MIN_W_M, pw)
    pt, ph = PILLOW_TH[c]
    ns = max(1, int(want.get("euro_shams") or 0))
    sw = min(SHAM_MAX_W[c], (w - MATTRESS_MARGIN_M) / ns - PILLOW_GAP_M)
    sham = [round(pw, 3), pt, ph] if stacked else [round(sw, 3), SHAM_T_M, round(sw * 0.95, 3)]
    aw = min(ACCENT_W[c], max(0.30, (w - MATTRESS_MARGIN_M) / max(1, int(want.get("accent") or 1)) - 0.03))
    lw, lt, lh = LUMBAR[c]
    return {"class": c, "pillow": [round(pw, 3), pt, ph], "sham": sham, "accent": [round(aw, 3), ACCENT_T_M,
                                                                                  round(aw, 3)],
            "lumbar": [round(min(lw, w - 0.20), 3), lt, lh]}


# --------------------------------------------------------------------------
# Arrangements (counts of each row; at most ``bedding_parts.PIECES_MAX`` pieces, UL195)
# --------------------------------------------------------------------------

ARRANGEMENTS: dict[str, dict] = {
    "single_plain": {"classes": ("single",), "rank": 1, "euro_shams": 0, "pillows": 1, "accent": 0, "lumbar": 0,
                     "why": "one sleeping pillow (a single bed)"},
    "single_accent": {"classes": ("single",), "rank": 2, "euro_shams": 0, "pillows": 1, "accent": 1, "lumbar": 0,
                      "why": "one sleeping pillow and one accent cushion"},
    "single_sham": {"classes": ("single",), "rank": 3, "euro_shams": 1, "pillows": 1, "accent": 0, "lumbar": 0,
                    "why": "one euro sham behind one sleeping pillow"},
    "pair_plain": {"classes": ("small_double", "queen", "king"), "rank": 1, "euro_shams": 0, "pillows": 2,
                   "accent": 0, "lumbar": 0, "why": "two sleeping pillows"},
    "pair_lumbar": {"classes": ("small_double", "queen", "king"), "rank": 2, "euro_shams": 0, "pillows": 2,
                    "accent": 0, "lumbar": 1, "why": "two sleeping pillows and a lumbar"},
    "pair_two_accents": {"classes": ("small_double", "queen", "king"), "rank": 2, "euro_shams": 0, "pillows": 2,
                         "accent": 2, "lumbar": 0, "why": "two sleeping pillows and two accent cushions"},
    "stacked_four": {"classes": ("small_double", "queen", "king"), "rank": 2, "euro_shams": 2, "pillows": 2,
                     "accent": 0, "lumbar": 0, "stacked": True,
                     "why": "four sleeping pillows stacked in two rows (a hotel bed)"},
    "pair_three_accents": {"classes": ("queen", "king"), "rank": 3, "euro_shams": 0, "pillows": 2, "accent": 3,
                           "lumbar": 0, "why": "two sleeping pillows and three accent cushions"},
    "shams_lumbar": {"classes": ("small_double", "queen", "king"), "rank": 3, "euro_shams": 2, "pillows": 2,
                     "accent": 0, "lumbar": 1, "why": "two euro shams, two sleeping pillows and a lumbar"},
    "shams_accent": {"classes": ("small_double", "queen", "king"), "rank": 3, "euro_shams": 2, "pillows": 2,
                     "accent": 1, "lumbar": 0, "why": "two euro shams, two sleeping pillows and an accent cushion"},
    "king_three_shams": {"classes": ("king",), "rank": 3, "euro_shams": 3, "pillows": 2, "accent": 0, "lumbar": 0,
                         "why": "three euro shams behind two king pillows"},
}
COUNT_KEYS: tuple[str, ...] = ("euro_shams", "pillows", "accent", "lumbar")


def arrangement_counts(name: str) -> dict:
    a = ARRANGEMENTS[name]
    return {k: int(a[k]) for k in COUNT_KEYS}


def expected(spec: dict, width: float, shams: bool = True) -> dict:
    """What a bed's set holds (pure): the variant's arrangement (``spec["arrangement"]``), else
    ``bedding_parts.counts``.
    Without shams (no headboard holds them: ``shams`` False) the arrangement's shams leave and accent cushions stand in
    for them in front of the pillows (at most two, never past ``bedding_parts.pieces_max``); a stacked arrangement
    keeps its pillows only."""
    name = spec.get("arrangement") if isinstance(spec, dict) else None
    if name not in ARRANGEMENTS:
        return BP.counts(spec, width, shams=shams)
    out = arrangement_counts(name)
    if not shams and out["euro_shams"]:
        lost = out["euro_shams"]
        out["euro_shams"] = 0
        if not ARRANGEMENTS[name].get("stacked"):
            room = BP.pieces_max(width) - sum(out.values())
            add = min(lost, 2, room, max(0, 3 - out["accent"]))
            if len(spec.get("accent") or []) >= out["accent"] + add:
                out["accent"] += add
    return out


# --------------------------------------------------------------------------
# The families' textiles and palettes (designer values, assumed; colours are wenart/style/colours.py names)
# --------------------------------------------------------------------------

# the looks every textile role may take (``bedding_parts.LOOK_SLUGS``: each a vocabulary fabric with its weave or scan)
BASE_TEXTILES: dict[str, tuple] = {
    "duvet": ("linen", "cotton", "sateen", "waffle"),
    "sheet": ("cotton", "sateen", "linen"),
    "pillows": ("cotton", "sateen", "linen"),
    "shams": ("linen", "velvet", "cotton"),
    "accent": ("boucle", "velvet", "knit", "linen"),
    "lumbar": ("velvet", "knit", "linen", "wool"),
    "quilt": (None, None, "channel", "box", "diamond"),       # a plain duvet more often than a quilted coverlet
    "throw_looks": ("chunky_knit", "wool", "waffle", "knit"),
    "patterns": ("houndstooth", "stripe", "herringbone", None),
    "fringe": (True, False),
}
FAMILY_TEXTILES: dict[str, dict] = {
    "scandinavian": {"duvet": ("linen", "cotton", "waffle"), "shams": ("linen", "cotton"),
                     "accent": ("boucle", "knit", "linen"), "lumbar": ("knit", "linen", "wool"),
                     "throw_looks": ("chunky_knit", "knit", "waffle"), "patterns": ("stripe", None)},
    "japandi": {"duvet": ("linen", "waffle"), "sheet": ("linen", "cotton"), "pillows": ("linen", "cotton"),
                "shams": ("linen",), "accent": ("boucle", "linen"), "lumbar": ("linen", "wool"),
                "throw_looks": ("waffle", "linen", "wool"), "patterns": ("herringbone", None),
                "quilt": (None, None, "channel")},
    "modern minimal": {"duvet": ("cotton", "sateen", "linen"), "shams": ("cotton", "linen"),
                       "accent": ("boucle", "linen"), "lumbar": ("linen",), "throw_looks": ("wool", "waffle"),
                       "patterns": ("stripe", None), "fringe": (False,), "quilt": (None, None, "channel")},
    "minimal": {"duvet": ("cotton", "sateen", "linen"), "shams": ("cotton", "linen"), "accent": ("boucle", "linen"),
                "lumbar": ("linen",), "throw_looks": ("wool", "waffle"), "patterns": ("stripe", None),
                "fringe": (False,), "quilt": (None, None, "channel")},
    "industrial": {"duvet": ("linen", "cotton"), "shams": ("linen", "velvet"), "accent": ("knit", "wool", "velvet"),
                   "lumbar": ("wool", "velvet"), "throw_looks": ("wool", "chunky_knit"),
                   "patterns": ("herringbone", "stripe")},
    "mediterranean": {"duvet": ("linen", "cotton", "waffle"), "sheet": ("linen", "cotton"), "shams": ("linen",),
                      "accent": ("linen", "knit"), "lumbar": ("linen",), "throw_looks": ("linen", "waffle", "knit"),
                      "patterns": ("stripe", None)},
    "classic": {"duvet": ("sateen", "cotton"), "sheet": ("sateen", "cotton"), "pillows": ("sateen", "cotton"),
                "shams": ("velvet", "sateen"), "accent": ("velvet", "boucle"), "lumbar": ("velvet",),
                "throw_looks": ("wool", "knit"), "patterns": ("houndstooth", "herringbone"),
                "quilt": (None, "diamond", "box")},
    "rustic": {"duvet": ("linen", "waffle"), "shams": ("linen", "wool"), "accent": ("knit", "wool", "linen"),
               "lumbar": ("wool", "knit"), "throw_looks": ("chunky_knit", "wool"),
               "patterns": ("herringbone", "stripe")},
}
NEUTRAL_PALETTE: dict[str, tuple[str, ...]] = {
    "duvet": ("greige", "off white", "light grey", "sand", "white", "ivory"),
    "sheet": ("white", "off white", "light grey", "ivory"),
    "pillows": ("white", "off white", "ivory"),
    "shams": ("charcoal", "greige", "taupe", "sand", "dark grey", "beige"),
    "accent": ("mustard", "cream", "dusty blue", "rust", "sage", "terracotta"),
    "throw": ("charcoal", "camel", "rust", "sage", "greige", "navy"),
}
FAMILY_PALETTE: dict[str, dict] = {
    "scandinavian": {"duvet": ("sand", "off white", "light grey", "white"), "shams": ("greige", "sand", "light grey"),
                     "accent": ("sage", "cream", "dusty blue", "mustard"), "throw": ("sage", "greige", "camel")},
    "japandi": {"duvet": ("beige", "off white", "sand", "greige"), "shams": ("greige", "taupe", "beige"),
                "accent": ("olive", "sand", "rust", "charcoal"), "throw": ("olive", "taupe", "charcoal")},
    "modern minimal": {"duvet": ("off white", "white", "light grey"), "shams": ("light grey", "greige", "charcoal"),
                       "accent": ("light grey", "greige", "charcoal"), "throw": ("greige", "light grey", "charcoal")},
    "minimal": {"duvet": ("off white", "white", "light grey"), "shams": ("light grey", "greige", "charcoal"),
                "accent": ("light grey", "greige", "charcoal"), "throw": ("greige", "light grey", "charcoal")},
    "industrial": {"duvet": ("grey", "light grey", "greige"), "shams": ("charcoal", "dark grey", "camel"),
                   "accent": ("rust", "camel", "grey", "olive"), "throw": ("rust", "charcoal", "camel")},
    "mediterranean": {"duvet": ("off white", "white", "sand"), "shams": ("sand", "beige", "dusty blue"),
                      "accent": ("terracotta", "dusty blue", "cream", "ochre"),
                      "throw": ("terracotta", "sand", "navy")},
    "classic": {"duvet": ("ivory", "white", "cream"), "shams": ("navy", "taupe", "burgundy"),
                "accent": ("navy", "cream", "gold", "burgundy"), "throw": ("navy", "camel", "burgundy")},
    "rustic": {"duvet": ("cream", "sand", "off white"), "shams": ("rust", "camel", "olive"),
               "accent": ("rust", "cream", "mustard", "olive"), "throw": ("rust", "camel", "olive")},
}
DEFAULT_FAMILY = "modern"
# the finishes each piece may take (a sham's flange, a pillowcase's seam or piping, a cushion's piping, tufting,
# tassels or knife edge)
FINISHES: dict[str, tuple[str, ...]] = {
    "shams": ("flange", "flange", "piping"),
    "pillows": ("flange", "piping", "knife"),
    "accent": ("piping", "knife", "buttons", "tassels", "flange"),
    "lumbar": ("piping", "knife", "buttons", "tassels"),
}
QUILT_PITCH_M: dict[str, float] = {"channel": 0.22, "box": 0.30, "diamond": 0.18}
# duvet thickness by look (a down duvet in sateen is the deepest, a waffle coverlet the thinnest; a quilted coverlet
# 3.5 cm); wrinkles by look (washed linen creases most)
DUVET_T_M: dict[str, float] = {"linen": 0.06, "cotton": 0.065, "sateen": 0.075, "waffle": 0.05}
QUILTED_T_M = 0.035
DUVET_WRINKLE_M: dict[str, float] = {"linen": 0.014, "cotton": 0.010, "sateen": 0.008, "waffle": 0.009}
THROW_STYLES_BY_RANK: dict[int, tuple[str, ...]] = {3: ("p14", "quilt_fold", "corner_drape", "foot_fold"),
                                                    2: ("foot_fold", "runner", "corner_drape", "p14"),
                                                    1: ("foot_fold", "runner")}
VARIANT_TRIES = 96


def family_name(family: Optional[str]) -> str:
    fam = str(family or "").lower()
    return fam if fam in BP.FAMILY_BEDDING else DEFAULT_FAMILY


def textiles_of(family: Optional[str]) -> dict:
    fam = family_name(family)
    return dict(BASE_TEXTILES, **FAMILY_TEXTILES.get(fam, {}))


def palette_of(family: Optional[str], scheme: Sequence[str] = ()) -> dict:
    """The family's palette with the room's scheme colours (the brief's cushion and throw colours) first in the accents
    and the throw (pure; each colour once)."""
    fam = family_name(family)
    pal = dict(NEUTRAL_PALETTE, **FAMILY_PALETTE.get(fam, {}))
    row = BP.FAMILY_BEDDING.get(fam) or BP.FAMILY_BEDDING[BP.DEFAULT_FAMILY]
    first = {"duvet": row["duvet"].get("colour"), "sheet": (row.get("sheet") or {}).get("colour"),
             "pillows": row["pillows"].get("colour"), "shams": row["shams"].get("colour")}
    out = {}
    for k, v in pal.items():
        seq = ([first[k]] if first.get(k) else []) + list(v)
        if k in ("accent", "throw"):
            seq = list(scheme or ()) + seq
        uniq: list[str] = []
        for c in seq:
            if c and c not in uniq:
                uniq.append(c)
        out[k] = tuple(uniq)
    return out


# --------------------------------------------------------------------------
# A bed's rank (master, guest, child) and its variant
# --------------------------------------------------------------------------

BATH_TYPES: tuple[str, ...] = ("bathroom", "wc", "toilet", "shower")
DOOR_REACH_M = 0.35              # a door within this of two rooms' outlines joins them


def _room_area(room: dict) -> float:
    from wenart import geometry as G

    if room.get("area_computed"):
        return float(room["area_computed"])
    poly = room.get("polygon") or []
    return abs(G.polygon_area(poly)) if len(poly) >= 3 else 0.0


def _near_room(point, room: dict) -> bool:
    from wenart import geometry as G

    poly = room.get("polygon") or []
    if len(poly) < 3:
        return False
    if G.point_in_polygon(point, poly):
        return True
    return min(G.point_segment_distance(point, poly[k - 1], poly[k]) for k in range(len(poly))) <= DOOR_REACH_M


def ensuite(room: dict, building: dict) -> Optional[str]:
    """The bathroom a bedroom opens into by a door of its own (pure: a door within ``DOOR_REACH_M`` of both rooms'
    outlines on the level), None when it has none."""
    baths = [r for r in building.get("rooms") or [] if r.get("level_id") == room.get("level_id")
             and r.get("room_type") in BATH_TYPES]
    if not baths:
        return None
    for op in building.get("openings") or []:
        if op.get("type") != "door" or op.get("level_id") not in (None, room.get("level_id")) or not op.get("center"):
            continue
        c = op["center"][:2]
        if not _near_room(c, room):
            continue
        for b in baths:
            if _near_room(c, b):
                return str(b.get("id"))
    return None


def bed_rank(bed: dict, building: dict) -> tuple[int, str]:
    """``(rank, why)`` of a bed (pure): 3 for the master bedroom's (a bedroom with its own bathroom, else the widest
    double bed in the largest bedroom), 1 for a child's room or a single bed, 2 for a guest double bed."""
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    room = rooms.get(bed.get("room_id")) or {}
    if room.get("room_type") == "child":
        return 1, "a child's room: the plainest set"
    if bed.get("type") == "bed_single":
        return 1, "a single bed: the plainest set"
    bath = ensuite(room, building)
    if bath:
        return 3, f"the master bedroom (its own bathroom {bath}): the richest set"
    doubles = [b for b in building.get("furniture") or [] if b.get("type") == "bed_double" and b.get("footprint")
               and (rooms.get(b.get("room_id")) or {}).get("room_type") == "bedroom"
               and b.get("build", True) is not False]
    if doubles and not any(ensuite(rooms.get(b.get("room_id")) or {}, building) for b in doubles):
        def key(b):
            return (-float(b["footprint"]["size"][0]), -_room_area(rooms.get(b.get("room_id")) or {}),
                    str(b.get("id")))
        if sorted(doubles, key=key)[0].get("id") == bed.get("id"):
            return 3, "the master bedroom (the widest bed in the largest bedroom): the richest set"
    return 2, "a guest bedroom: a medium set"


def _pick(seq: Sequence, seed: int, salt: str):
    seq = list(seq)
    return seq[stable_hash(seed, salt) % len(seq)] if seq else None


def _arrangements_for(width: float, rank: int, single: bool = False) -> list[str]:
    c = "single" if single else mattress_class(width)
    names = [n for n, a in ARRANGEMENTS.items() if c in a["classes"]]
    if c == "small_double" and float(width) < BP.SHAM_MIN_BED_W - 1e-9:
        names = [n for n in names if not ARRANGEMENTS[n]["euro_shams"] or ARRANGEMENTS[n].get("stacked")]
    same = [n for n in names if ARRANGEMENTS[n]["rank"] == rank]
    if same:
        return same
    best = min(abs(ARRANGEMENTS[n]["rank"] - rank) for n in names)
    return [n for n in names if abs(ARRANGEMENTS[n]["rank"] - rank) == best]


def signature(spec: dict) -> tuple:
    """What tells two sets apart (pure): the arrangement, the duvet's look, quilting and colour, the shams' and
    accents' looks and colours, the throw's style and look."""
    t = spec.get("throw") or {}
    return (spec.get("arrangement"), spec["duvet"]["look"], spec["duvet"].get("quilt"), spec["duvet"].get("colour"),
            spec["shams"]["look"], spec["shams"].get("colour"),
            tuple((a.get("look"), a.get("colour")) for a in spec.get("accent") or []),
            t.get("style"), t.get("look"), t.get("pattern"))


def bed_variant(bed_id: str, family: Optional[str], width: float, rank: int = 2, scheme: Sequence[str] = (),
                taken: Iterable[tuple] = (), single: bool = False) -> dict:
    """The bedding set of one bed (pure; deterministic from ``bed_id``): a ``bedding_parts.FAMILY_BEDDING``-shaped spec
    (``duvet``, ``sheet``, ``shams``, ``pillows``, ``accent``, ``lumbar``, ``throw``) plus ``arrangement``,
    ``expected``, ``sizes``, ``stacked`` and ``variant`` (its id, rank, signature, seed). The first candidate (in the
    order the bed's id hashes them) whose ``signature`` is not ``taken`` by another bed of the house; the arrangement
    of the bed's rank and mattress (``_arrangements_for``; ``single``: a single bed whatever its width), the family's
    textiles and palette (``textiles_of``, ``palette_of``)."""
    fam = family_name(family)
    tex = textiles_of(fam)
    pal = palette_of(fam, scheme)
    taken = set(taken)
    names = _arrangements_for(width, rank, single)
    spec = None
    for k in range(VARIANT_TRIES):
        seed = stable_hash(bed_id, k)
        spec = _variant_spec(seed, k, fam, tex, pal, names, width, rank, single)
        if signature(spec) not in taken:
            break
    spec["variant"]["signature"] = list(signature(spec))
    return spec


def _variant_spec(seed: int, k: int, fam: str, tex: dict, pal: dict, names: list, width: float, rank: int,
                  single: bool = False) -> dict:
    arrangement = _pick(names, seed, "arrangement")
    a = ARRANGEMENTS[arrangement]
    stacked = bool(a.get("stacked"))
    quilt = _pick(tex["quilt"] if rank >= 2 else (None,), seed, "quilt")
    dlook = "cotton" if quilt else _pick(tex["duvet"], seed, "duvet")
    if rank == 3 and dlook == "cotton" and "sateen" in tex["duvet"]:
        dlook = "sateen"                            # the master's duvet: the family's richest cotton
    dcol = _pick(pal["duvet"], seed, "duvet_colour")
    plook = _pick(tex["pillows"], seed, "pillow")
    pcol = _pick([c for c in pal["pillows"]], seed, "pillow_colour")
    slook = plook if stacked else _pick(tex["shams"] if rank >= 2 else ("cotton", "linen"), seed, "sham")
    shams_pal = [c for c in pal["shams"] if c != dcol] or list(pal["shams"])
    scol = pcol if stacked else _pick(shams_pal, seed, "sham_colour")
    sheet_look = _pick(tex["sheet"], seed, "sheet")
    sheet_col = _pick([c for c in pal["sheet"] if c != dcol] or list(pal["sheet"]), seed, "sheet_colour")
    accents_pal = [c for c in pal["accent"] if c not in (scol, dcol)] or list(pal["accent"])
    start = stable_hash(seed, "accent_start") % len(accents_pal)
    accent_cols = [accents_pal[(start + i) % len(accents_pal)] for i in range(3)]
    accent_looks = list(tex["accent"])
    a0 = stable_hash(seed, "accent_look") % len(accent_looks)
    accents = [{"look": accent_looks[(a0 + i) % len(accent_looks)], "colour": accent_cols[i],
                "finish": _pick(FINISHES["accent"], seed, f"accent_finish{i}")} for i in range(3)]
    lumbar = {"look": _pick(tex["lumbar"], seed, "lumbar"), "colour": accent_cols[0],
              "finish": _pick(FINISHES["lumbar"], seed, "lumbar_finish")}
    style = _pick(THROW_STYLES_BY_RANK.get(rank, THROW_STYLES_BY_RANK[2]), seed, "throw_style")
    pattern = _pick(tex["patterns"], seed, "pattern")
    tlook = _pick(tex["throw_looks"], seed, "throw_look")
    throw_cols = [c for c in pal["throw"] if c not in (dcol,)] or list(pal["throw"])
    tcol = _pick(throw_cols, seed, "throw_colour")
    fringe = bool(_pick(tex["fringe"], seed, "fringe")) and style not in ("quilt_fold",)
    t_dk = QUILTED_T_M if quilt else DUVET_T_M.get(dlook, 0.06)
    want = arrangement_counts(arrangement)
    spec = {
        "family": fam,
        "duvet": {"look": dlook, "colour": dcol, "thickness_m": t_dk,
                  "wrinkle_m": 0.008 if quilt else DUVET_WRINKLE_M.get(dlook, 0.012),
                  "hem_m": 0.06 if rank == 3 else 0.08 if rank == 2 else 0.10, "quilt": quilt,
                  "quilt_pitch_m": QUILT_PITCH_M.get(quilt or "", None),
                  "fold_back": "duvet" if (not quilt and _pick(("sheet", "duvet", "sheet"), seed, "fold") == "duvet")
                  else "sheet"},
        "sheet": {"look": sheet_look, "colour": sheet_col},
        "shams": {"look": slook, "colour": scol, "finish": "flange" if stacked else _pick(FINISHES["shams"], seed,
                                                                                            "sham_finish")},
        "pillows": {"look": plook, "colour": pcol, "finish": _pick(FINISHES["pillows"], seed, "pillow_finish")},
        "accent": accents,
        "lumbar": lumbar,
        "throw": {"style": style, "pattern": pattern if style in ("p14", "runner", "corner_drape") else None,
                  "runner_look": tlook, "look": tlook, "fringe": fringe, "colour": tcol,
                  "accent_colour": _pick([c for c in pal["throw"] if c != tcol] or [tcol], seed, "throw_accent")},
        "arrangement": arrangement, "expected": want, "stacked": stacked,
        "sizes": bed_sizes(width, want, stacked, single),
        "variant": {"id": f"{fam}:{arrangement}:{seed % 100000:05d}", "rank": rank, "seed": k, "rule": RULE_BED,
                    "lesson": LESSON_BED},
    }
    spec["why"] = (f"{a['why']}; a {'quilted ' + quilt + ' coverlet' if quilt else dlook + ' duvet'} in {dcol}, "
                   f"{slook} {'pillows' if stacked else 'shams'} in {scol}, {spec['pillows']['look']} pillows, the "
                   f"throw {style.replace('_', ' ')} in {tlook} ({TAG_BED})")
    return spec


def house_bed_variants(beds: Sequence[dict], building: dict, family: Optional[str],
                       scheme: Sequence[str] = ()) -> dict:
    """``{bed id: spec}`` for the beds of a house (pure): the master first, then by rank and id, each with a signature
    no other bed has (``bed_variant``)."""
    ranked = []
    for bed in beds:
        rank, why = bed_rank(bed, building)
        ranked.append((rank, str(bed.get("id")), bed, why))
    ranked.sort(key=lambda r: (-r[0], r[1]))
    taken: set = set()
    out = {}
    for rank, bid, bed, why in ranked:
        w = float(BP.bed_frame(bed)[2][0])
        spec = bed_variant(bid, family, w, rank, scheme, taken, single=bed.get("type") == "bed_single")
        spec["variant"]["rank_why"] = why
        taken.add(tuple(spec["variant"]["signature"]))
        out[bid] = spec
    return out


def throw_weave(spec: dict, sides: Optional[dict] = None) -> dict:
    """The ``weave`` of a bed's throw from its variant (pure; ``textiles.throw_parts`` builds it): the style, its
    pattern and look, the fringe (over free sides only), the colours."""
    t = dict(spec.get("throw") or {})
    sides = sides or {}
    ends = [s for s in ("left", "right") if (sides.get(s) or {}).get("free", True)]
    return {"style": t.get("style") or "foot_fold", "pattern": t.get("pattern"), "runner_look": t.get("runner_look"),
            "look": t.get("look"), "fringe": bool(t.get("fringe")), "fringe_ends": ends if t.get("fringe") else [],
            "colour": t.get("colour"), "accent_colour": t.get("accent_colour"), "rule": RULE_BED,
            "variant": (spec.get("variant") or {}).get("id"),
            "why": f"the bed's own throw: {str(t.get('style') or 'foot_fold').replace('_', ' ')} in {t.get('look')} "
                   f"({TAG_BED})"}


# --------------------------------------------------------------------------
# Meshes: a cushion's finish, a quilted coverlet's stitching, a folded throw
# --------------------------------------------------------------------------

PIPING_R_M = 0.0045              # a piping cord's radius
PIPING_SIDES = 6
FLANGE_BY_FINISH: dict[str, float] = {"flange": 0.025, "piping": 0.0, "knife": 0.0, "buttons": 0.0, "tassels": 0.0}
TUFT_DEPTH = 0.55                # a tufted cushion's centre is pulled in to this share of its half thickness ...
TUFT_R_M = 0.05                  # ... over this radius
BUTTON_R_M = 0.012
TASSEL_L_M = 0.06


def _seam_ring(w: float, h: float, n_side: int = 12) -> np.ndarray:
    """The seam outline of ``bedding_parts.plump_cushion`` (no sag) as a closed ring in its x-z plane ``(N, 3)``."""
    t = np.linspace(-1.0, 1.0, n_side + 1)[:-1]
    us = np.concatenate([t, np.ones(n_side), -t, -np.ones(n_side)])
    vs = np.concatenate([-np.ones(n_side), t, np.ones(n_side), -t])
    x = us * w / 2.0 * (1.0 - BP.CUSHION_DRAW * np.sin(np.pi * (vs + 1.0) / 2.0))
    z = h / 2.0 + vs * h / 2.0 * (1.0 - BP.CUSHION_DRAW * np.sin(np.pi * (us + 1.0) / 2.0))
    return np.stack([x, np.zeros_like(x), z], axis=1)


def tube(ring: np.ndarray, radius: float, key: str, role: str, closed: bool = True,
         sides: int = PIPING_SIDES) -> Part:
    """A round cord of ``radius`` along a polyline ``ring`` ``(N, 3)`` (pure): a circle swept along it in the plane of
    its tangent's normal (a closed ring joins its ends)."""
    p = np.asarray(ring, dtype=np.float64)
    n = len(p)
    nxt = np.roll(p, -1, axis=0) if closed else np.concatenate([p[1:], p[-1:] + (p[-1:] - p[-2:-1])])
    prv = np.roll(p, 1, axis=0) if closed else np.concatenate([p[:1] - (p[1:2] - p[:1]), p[:-1]])
    tng = nxt - prv
    tng /= np.maximum(np.linalg.norm(tng, axis=1, keepdims=True), 1e-12)
    ref = np.where(np.abs(tng[:, 1:2]) > 0.9, np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 1.0, 0.0]]))
    nrm = np.cross(tng, ref)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    bnm = np.cross(tng, nrm)
    a = 2.0 * np.pi * np.arange(sides) / sides
    verts = (p[:, None, :] + radius * (np.cos(a)[None, :, None] * nrm[:, None, :]
                                       + np.sin(a)[None, :, None] * bnm[:, None, :])).reshape(-1, 3)
    faces = []
    segs = n if closed else n - 1
    for i in range(segs):
        j = (i + 1) % n
        for s in range(sides):
            s1 = (s + 1) % sides
            faces.append([i * sides + s, i * sides + s1, j * sides + s1, j * sides + s])
    if not closed:
        faces.append([s for s in range(sides)][::-1])
        faces.append([(n - 1) * sides + s for s in range(sides)])
    return {"verts": [tuple(v) for v in verts.tolist()], "faces": faces, "key": key, "role": role, "smooth": True}


def _disc(cx: float, cy: float, cz: float, r: float, t: float, axis_y: float, key: str, role: str,
          n: int = 10) -> Part:
    """A small button: a flat round disc of radius ``r`` and thickness ``t`` facing along y (``axis_y`` = +1 / -1)."""
    a = 2.0 * np.pi * np.arange(n) / n
    ring0 = np.stack([cx + r * np.cos(a), np.full(n, cy), cz + r * np.sin(a)], axis=1)
    ring1 = ring0 + np.array([0.0, axis_y * t, 0.0])
    verts = np.concatenate([ring0, ring1, [[cx, cy + axis_y * t, cz]]], axis=0)
    faces = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    faces += [[n + k, n + (k + 1) % n, 2 * n] for k in range(n)]
    if axis_y < 0:
        faces = [f[::-1] for f in faces]
    return {"verts": [tuple(v) for v in verts.tolist()], "faces": faces, "key": key, "role": role, "smooth": False}


def _tassel(corner, out_dir, key: str) -> Part:
    """A corner tassel: a small cone hanging from the cushion's corner along ``out_dir`` (x-z plane)."""
    c = np.asarray(corner, dtype=np.float64)
    d = np.asarray(out_dir, dtype=np.float64)
    d /= max(float(np.linalg.norm(d)), 1e-9)
    tip = c + d * TASSEL_L_M
    ring = []
    for k in range(4):
        s = k / 3.0
        p = c + d * (TASSEL_L_M * s)
        ring.append(p)
    radius = [0.004, 0.006, 0.009, 0.004]
    parts_v, faces = [], []
    n = 8
    a = 2.0 * np.pi * np.arange(n) / n
    side = np.cross(d, [0.0, 1.0, 0.0])
    side /= max(float(np.linalg.norm(side)), 1e-9)
    up = np.array([0.0, 1.0, 0.0])
    for p, r in zip(ring, radius):
        parts_v.append(p[None, :] + r * (np.cos(a)[:, None] * side[None, :] + np.sin(a)[:, None] * up[None, :]))
    verts = np.concatenate(parts_v + [tip[None, :]], axis=0)
    for i in range(len(ring) - 1):
        for k in range(n):
            faces.append([i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k])
    last = len(ring) * n
    faces += [[(len(ring) - 1) * n + k, (len(ring) - 1) * n + (k + 1) % n, last] for k in range(n)]
    return {"verts": [tuple(v) for v in verts.tolist()], "faces": faces, "key": key, "role": "tassel",
            "smooth": True}


def cushion_parts(w: float, t: float, h: float, look: str = "linen", finish: str = "piping",
                  trim_look: Optional[str] = None, role: str = "cushion", sag: float = BP.SAG_SHARE) -> list[Part]:
    """A filled cushion with its finish (pure; item frame as ``bedding_parts.plump_cushion``: width X, thickness Y,
    height Z from 0, front -Y): the body (key ``colour_textile_<look>``) and, by ``finish``: ``flange`` (a 2.5 cm
    flat border), ``piping`` (a cord along the seam, ``PIPING_R_M``), ``knife`` (a plain seam), ``buttons`` (the centre
    pulled in on both faces with a button in each dimple), ``tassels`` (a tassel at each corner). The trim (piping,
    buttons, tassels) is key ``colour_runner_<trim look>``: the item's accent colour where it has one."""
    # a flange: the piece's own (a euro sham's 4 cm, a pillowcase's 1.5 cm seam), else ``FLANGE_BY_FINISH``
    fl = BP.FLANGE_M.get(role, FLANGE_BY_FINISH["flange"]) if finish == "flange" else FLANGE_BY_FINISH.get(finish, 0.0)
    body = BP.plump_cushion(w, t, h, key=BP.textile_key(look), role=role, flange=fl, sag=sag)
    parts = [body]
    tkey = BP.runner_key(trim_look or look)
    if finish == "piping":
        parts.append(tube(_seam_ring(w, h), PIPING_R_M, tkey, "piping"))
    elif finish == "buttons":
        v = np.asarray(body["verts"], dtype=np.float64)
        r = np.hypot(v[:, 0], v[:, 2] - h / 2.0)
        pull = 1.0 - TUFT_DEPTH * np.exp(-(r / TUFT_R_M) ** 2)
        v[:, 1] *= pull
        body = dict(body, verts=[tuple(p) for p in v.tolist()])
        parts = [body]
        front = float(v[np.argmin(r), 1]) if len(v) else -t / 2.0
        depth = abs(front)
        for sign in (-1.0, 1.0):
            parts.append(_disc(0.0, sign * max(0.0, depth - 0.002), h / 2.0, BUTTON_R_M, 0.005, sign, tkey,
                               "button"))
    elif finish == "tassels":
        for sx in (-1.0, 1.0):
            for sz in (0.0, 1.0):
                corner = (sx * w / 2.0, 0.0, sz * h)
                parts.append(_tassel(corner, (sx, 0.0, 1.0 if sz else -1.0), tkey))
    return parts


def seat_cushion_parts(w: float, t: float, h: float, spec: dict) -> list[Part]:
    """A seat's decor cushion from its ``cushion_set`` (pure; ``cushion_parts``): its look, finish and trim; a lumbar
    is the same filled body at its own proportions."""
    return cushion_parts(w, t, h, str(spec.get("look") or "linen"), str(spec.get("finish") or "piping"),
                         spec.get("trim_look"), role="body")


def quilt_depth(x, y, kind: Optional[str], pitch: Optional[float], groove_w: float = 0.012) -> np.ndarray:
    """The stitching grooves of a quilted coverlet (pure; 0..1 at each point, 1 on a stitch line): ``channel`` lines
    across the bed every ``pitch``, ``box`` lines both ways, ``diamond`` lines along both diagonals; 0 for a plain
    duvet. A soft groove (a Gaussian of ``groove_w``), never a cut."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if not kind or not pitch:
        return np.zeros(np.broadcast(x, y).shape)
    p = float(pitch)

    def line(u):
        d = p * np.abs(((u / p) + 0.5) % 1.0 - 0.5)
        return np.exp(-(d / groove_w) ** 2)
    if kind == "channel":
        return line(y) + 0.0 * x
    if kind == "box":
        return np.maximum(line(x), line(y))
    if kind == "diamond":
        s = math.sqrt(0.5)
        return np.maximum(line((x + y) * s), line((x - y) * s))
    return np.zeros(np.broadcast(x, y).shape)


FOLD_BACK_M = 0.30               # a duvet folded back over its head end: this deep
QUILT_DEPTH_M = 0.007            # a stitch line sinks this far into the coverlet
QUILT_EDGE_M = 0.06              # ... fading out this close to the top's edges


def quilt_grid(grid_local: np.ndarray, local: np.ndarray, on_top: np.ndarray, edges, kind: Optional[str],
               pitch: Optional[float], depth: float = QUILT_DEPTH_M) -> np.ndarray:
    """A cover's top grid (bed frame) with its stitching (pure): the top's points sink ``depth`` x ``quilt_depth``
    (fading within ``QUILT_EDGE_M`` of its edges); the hanging sides are left as they are. A copy."""
    g = np.array(grid_local, dtype=np.float64)
    if not kind or not pitch:
        return g
    loc = np.asarray(local, dtype=np.float64)
    on = np.asarray(on_top, dtype=bool)
    x0, x1, y0, y1 = (float(v) for v in edges)
    inside = np.minimum(np.minimum(loc[..., 0] - x0, x1 - loc[..., 0]), np.minimum(loc[..., 1] - y0,
                                                                                   y1 - loc[..., 1]))
    fade = BP.smoothstep(inside / QUILT_EDGE_M)
    q = quilt_depth(loc[..., 0], loc[..., 1], kind, pitch)
    g[..., 2] = np.where(on, g[..., 2] - float(depth) * q * fade, g[..., 2])
    return g


def folded_throw_parts(w: float, d: float, layers: int = 3, t: float = 0.012, key: str = "colour_textile_knit",
                       nx: int = 16, nr: int = 8) -> list[Part]:
    """A throw folded flat (pure; item frame: width X, depth Y, bottom on z = 0): ``layers`` cloth layers of ``t``
    stacked into a soft slab with rounded folds along its two long edges (a stadium section swept along x), its top
    sagging a little between the folds and its ends drawn in where the layers part. One part, key ``key``."""
    w, d = float(w), float(d)
    H = max(2.0 * t, float(layers) * float(t))
    r = H / 2.0
    half = max(0.0, d / 2.0 - r)
    # the section: a stadium (two half circles of radius r joined by flats), counter-clockwise from the bottom middle
    pts = []
    for k in range(nr + 1):                         # the front fold (-y), bottom to top
        a = -math.pi / 2.0 - math.pi * k / nr
        pts.append((-half + r * math.cos(a), r + r * math.sin(a)))
    for k in range(nr + 1):                         # the back fold (+y), top to bottom
        a = math.pi / 2.0 - math.pi * k / nr
        pts.append((half + r * math.cos(a), r + r * math.sin(a)))
    sec = np.asarray(pts, dtype=np.float64)
    xs = np.linspace(-w / 2.0, w / 2.0, nx + 1)
    m = len(sec)
    rings = []
    for x in xs:
        u = abs(2.0 * x / w)
        draw = 1.0 - 0.06 * BP.smoothstep((u - 0.85) / 0.15)        # the layers part a little at the ends
        sag = 0.15 * H * (1.0 - u ** 2)                              # the top sags between the folds
        y = sec[:, 0] * (1.0 - 0.02 * math.cos(3.0 * x / max(w, 1e-6)))
        z = r + (sec[:, 1] - r) * draw - np.where(sec[:, 1] > r, sag * (1.0 - np.abs(sec[:, 0]) / max(d / 2.0, 1e-6)),
                                                   0.0)
        rings.append(np.stack([np.full(m, x), y, np.maximum(z, 0.0)], axis=1))
    verts = np.concatenate(rings, axis=0)
    faces = []
    for i in range(nx):
        for k in range(m):
            k1 = (k + 1) % m
            faces.append([i * m + k, i * m + k1, (i + 1) * m + k1, (i + 1) * m + k])
    c0 = len(verts)
    verts = np.concatenate([verts, [[xs[0], 0.0, r], [xs[-1], 0.0, r]]], axis=0)
    faces += [[c0, (k + 1) % m, k] for k in range(m)]
    faces += [[c0 + 1, nx * m + k, nx * m + (k + 1) % m] for k in range(m)]
    verts[:, 2] -= verts[:, 2].min()
    return [{"verts": [tuple(v) for v in verts.tolist()], "faces": faces, "key": key, "role": "throw",
             "smooth": True, "layers": int(layers)}]


# --------------------------------------------------------------------------
# Sofa and armchair cushions (UL238)
# --------------------------------------------------------------------------

SEAT_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise")
SEAT_H_M = 0.43                  # a seat's top when nothing says otherwise ...
SEAT_H_SHARE = 0.78              # ... at most this share of a low piece's height
BACK_TOP_DEFAULT_M = 0.80
ARM_W_M = {"sofa": 0.15, "sofa_corner": 0.15, "armchair": 0.12, "chaise": 0.0}
SEAT_SIZES: tuple[float, ...] = (0.55, 0.50, 0.45, 0.42, 0.40, 0.35, 0.30)
LUMBAR_SEAT: tuple[float, float, float] = (0.50, 0.13, 0.30)
LUMBAR_MIN_H_M = 0.22
SEAT_LEAN_DEG = 20.0
SEAT_STEEP_LEANS: tuple[float, ...] = (20.0, 30.0, 38.0, 46.0)
BACK_OVER_M = 0.12               # a cushion's top at most this over the back's top ...
BACK_OVER_SHARE = 0.35           # ... or this share of its own height (the larger)
SINK_M = 0.02                    # = rest.SOFT_SINK_M
CUSHION_GAP_M = 0.03             # neighbouring cushions of a group stand this far apart
SEAT_LOOKS: dict[str, tuple[str, ...]] = {
    "modern": ("velvet", "boucle", "linen", "knit"), "contemporary": ("boucle", "velvet", "linen"),
    "modern minimal": ("boucle", "linen", "wool"), "minimal": ("boucle", "linen", "wool"),
    "scandinavian": ("boucle", "knit", "linen", "wool"), "japandi": ("linen", "boucle", "wool"),
    "industrial": ("velvet", "wool", "knit"), "mediterranean": ("linen", "knit", "cotton"),
    "classic": ("velvet", "sateen", "boucle"), "rustic": ("knit", "wool", "linen")}
SEAT_FINISHES: tuple[str, ...] = ("piping", "knife", "flange", "buttons", "tassels", "piping")


def over_back(h: float, t: float, lean_deg: float) -> float:
    """How high a cushion of height ``h`` and thickness ``t`` stands over the seat leaning ``lean_deg`` (pure; its
    sink into the seat taken off)."""
    a = math.radians(float(lean_deg))
    return float(h) * math.cos(a) + float(t) * math.sin(a) - SINK_M


def allowance(h: float) -> float:
    """How far a cushion of height ``h`` may stand over the back's top (``BACK_OVER_M``, ``BACK_OVER_SHARE``)."""
    return max(BACK_OVER_M, BACK_OVER_SHARE * float(h))


def seat_cushion_size(back_rise: float, seat_depth: Optional[float] = None,
                      sizes: Sequence[float] = SEAT_SIZES) -> dict:
    """The cushion a seat takes (pure): the largest square of ``sizes`` whose top, leaning at one of
    ``SEAT_STEEP_LEANS``, stays within ``allowance`` over a back rising ``back_rise`` over the seat (a seat shallower
    than twice the cushion's thickness plus 0.35 m takes the next smaller), else a lumbar (``LUMBAR_SEAT``, its height
    down to ``LUMBAR_MIN_H_M``); ``{"kind", "size", "lean_deg", "top_over_back_m", "why"}``, ``kind`` None when not even
    a lumbar fits (the back is too low for a cushion)."""
    rise = float(back_rise)
    depth_cap = None if seat_depth is None else max(0.30, float(seat_depth) - 0.35)
    # the natural leans first (the largest cushion that stands at 20 degrees), steeper ones only for a low back
    for lean in SEAT_STEEP_LEANS:
        for s in sizes:
            if depth_cap is not None and s > depth_cap + 0.10:
                continue
            top = over_back(s, ACCENT_T_M, lean) - rise
            if top <= allowance(s) + 1e-9:
                return {"kind": "square", "size": [s, ACCENT_T_M, s], "lean_deg": lean,
                        "top_over_back_m": round(top, 3),
                        "why": f"a {s * 100:.0f} cm cushion: its top {top:+.2f} m over the back (rising {rise:.2f} m "
                               f"over the seat) at {lean:.0f} deg (at most {allowance(s):.2f} m)"}
    lw, lt, lh = LUMBAR_SEAT
    for lean in SEAT_STEEP_LEANS:
        h = lh
        while h >= LUMBAR_MIN_H_M - 1e-9:
            top = over_back(h, lt, lean) - rise
            if top <= allowance(h) + 1e-9:
                return {"kind": "lumbar", "size": [lw, lt, round(h, 3)], "lean_deg": lean,
                        "top_over_back_m": round(top, 3),
                        "why": f"a lumbar {lw * 100:.0f} x {h * 100:.0f} cm at {lean:.0f} deg: the back rises only "
                               f"{rise:.2f} m over the seat"}
            h = round(h - 0.02, 3)
    return {"kind": None, "size": None, "lean_deg": None, "top_over_back_m": None,
            "why": f"the back rises only {rise:.2f} m over the seat: no cushion stands against it"}


def seat_layout(host: dict) -> dict:
    """What the decor stage knows of a seat's shape (pure; its fitted footprint and model): ``{"kind": straight |
    corner | armchair | chaise, "w", "d", "chaise_side", "chaise_w", "back_top_m", "seat_h_m", "back_rise_m",
    "seat_depth_m", "arm_m"}``. The back's top is the model's height (``asset.bbox_m``, else the piece's height,
    else ``BACK_TOP_DEFAULT_M``), the seat ``SEAT_H_M`` (at most ``SEAT_H_SHARE`` of a low piece's height); the
    build measures both on the mesh (``rest.place_leaning``)."""
    fp = host["footprint"]
    w, d = (float(v) for v in fp["size"][:2])
    asset = host.get("asset") if isinstance(host.get("asset"), dict) else {}
    bbox = asset.get("bbox_m") if isinstance(asset.get("bbox_m"), (list, tuple)) else None
    top = float(bbox[2]) if bbox and len(bbox) > 2 and bbox[2] else float(host.get("height") or BACK_TOP_DEFAULT_M)
    seat = min(SEAT_H_M, SEAT_H_SHARE * top)
    htype = host.get("type")
    kind = {"sofa_corner": "corner", "armchair": "armchair", "chaise": "chaise"}.get(htype, "straight")
    side = asset.get("chaise_side") or host.get("chaise_side")
    side = side if side in ("left", "right") else None
    chaise_w = min(0.95, max(0.70, w * 0.25)) if kind == "corner" else 0.0
    return {"kind": kind, "w": w, "d": d, "chaise_side": side, "chaise_w": round(chaise_w, 3),
            "back_top_m": round(top, 3), "seat_h_m": round(seat, 3), "back_rise_m": round(top - seat, 3),
            "seat_depth_m": round(min(d, 0.95) - 0.20, 3), "arm_m": ARM_W_M.get(htype, 0.12)}


def _group_from(end_x: float, inward: float, sizes: Sequence[float]) -> list[tuple[float, float]]:
    """Cushion centres of a group standing side by side from ``end_x`` inwards (``inward`` = +1 / -1)."""
    out, x = [], float(end_x)
    for s in sizes:
        out.append((x + inward * s / 2.0, float(s)))
        x += inward * (s + CUSHION_GAP_M)
    return out


SEAT_MAX_CUSHIONS: dict[str, int] = {"straight": 5, "corner": 5, "armchair": 1, "chaise": 1}


def seat_slots(lay: dict, n: int, size: dict) -> tuple[str, list[tuple[float, float, str, str]]]:
    """``(arrangement, [(lx, width, kind, group)])`` of ``n`` cushions on a seat (pure; ``seat_layout``,
    ``seat_cushion_size``), logical for its shape: a straight sofa: one in the middle, a pair at its ends inside the
    arms, a pair and a lumbar in the middle, graded pairs (the larger at each end), graded pairs and a middle one; a
    corner sofa: one at each end, a pair in its corner (the chaise's end of the back) and one at its open end, a pair at
    each, a trio in the corner and a pair at the open end; an armchair or a chaise one. A back too low for a square
    cushion takes lumbars (one, or one at each end). At most ``SEAT_MAX_CUSHIONS``; a group never wider than the
    seat."""
    w = lay["w"]
    inner = w / 2.0 - lay["arm_m"] - 0.02
    n = max(0, min(int(n), SEAT_MAX_CUSHIONS[lay["kind"]]))
    if n == 0:
        return "none", []
    if size["kind"] == "lumbar":
        lw = min(LUMBAR_SEAT[0], max(0.30, inner))
        if n >= 2 and lay["kind"] in ("straight", "corner") and 2.0 * inner >= 2.0 * lw + 0.4:
            return "lumbar_pair", [(-inner + lw / 2.0, lw, "lumbar", "left"), (inner - lw / 2.0, lw, "lumbar", "right")]
        return "lumbar", [(0.0, min(LUMBAR_SEAT[0], max(0.30, 2.0 * inner)), "lumbar", "middle")]
    base = float(size["size"][0])
    small = max(0.30, round(base - 0.08, 2))
    if lay["kind"] in ("armchair", "chaise") or n == 1:
        return "single", [(0.0, min(base, 2.0 * inner), "square", "middle")]
    if lay["kind"] == "straight":
        graded = n >= 4 and inner >= base + small + CUSHION_GAP_M + 0.1
        sizes = [base, small] if graded else [base]
        slots = [(x, s, "square", grp) for sign, grp in ((-1.0, "left"), (1.0, "right"))
                 for x, s in _group_from(sign * inner, -sign, sizes)]
        name = "graded_pairs" if graded else "pair"
        if n in (3, 5) and 2.0 * inner - 2.0 * sum(sizes) - 2 * CUSHION_GAP_M >= LUMBAR_SEAT[0]:
            slots.append((0.0, LUMBAR_SEAT[0], "lumbar", "middle"))
            name += "_lumbar"
        return name, slots
    corner = lay["chaise_side"] or "right"
    cs = 1.0 if corner == "right" else -1.0
    c_sizes = {2: [base], 3: [base, small], 4: [base, small], 5: [base, base, small]}[n]
    o_sizes = {2: [base], 3: [base], 4: [base, small], 5: [base, small]}[n]
    slots = [(x, s, "square", "corner") for x, s in _group_from(cs * inner, -cs, c_sizes)]
    slots += [(x, s, "square", "open") for x, s in _group_from(-cs * inner, cs, o_sizes)]
    names = {2: "one_at_each_end", 3: "corner_pair_open_single", 4: "corner_pair_open_pair",
             5: "corner_trio_open_pair"}
    return names[n], slots


def seat_cushion_plan(host: dict, family: Optional[str], colours: Sequence[str] = (), scheme: Sequence[str] = (),
                      taken: Iterable[tuple] = (), count: Optional[int] = None) -> dict:
    """The cushions of one seat (pure; ``seat_layout``, ``seat_cushion_size``, ``seat_slots``): ``{"items": [{"lx",
    "size", "kind", "look", "finish", "trim_look", "colour", "accent_colour", "group", "lean_deg"}], "arrangement",
    "size", "signature", "why"}``; ``items`` empty when the back takes no cushion. ``lx`` is along the seat's width
    (host frame, + = its right). ``count``: how many the decor stage gave it (its arrangement follows the count and the
    shape: a mirrored twin keeps its partner's count), else 2 (4 on a corner sofa, 1 on an armchair or a chaise). The
    look, the finish and the trim are the seat's own (``SEAT_LOOKS``, ``SEAT_FINISHES``; deterministic from its id, the
    first whose signature is not ``taken``: no two seats of the house alike); the colours are ``colours`` (the decor
    stage's, in order), then the scheme's, then the family's accents."""
    lay = seat_layout(host)
    fam = family_name(family)
    size = seat_cushion_size(lay["back_rise_m"], lay["seat_depth_m"])
    taken = set(taken)
    if size["kind"] is None:
        return {"items": [], "arrangement": None, "size": size, "signature": None, "layout": lay,
                "why": size["why"]}
    n = count if count is not None else {"straight": 2, "corner": 4}.get(lay["kind"], 1)
    arrangement, slots = seat_slots(lay, n, size)
    plan = None
    for k in range(VARIANT_TRIES):
        seed = stable_hash(host.get("id"), "seat", k)
        plan = _seat_plan(seed, lay, fam, size, slots, arrangement, list(colours), list(scheme))
        if tuple(plan["signature"]) not in taken:
            break
    plan["layout"] = lay
    plan["size"] = size
    return plan


def _seat_plan(seed: int, lay: dict, fam: str, size: dict, slots: list, arrangement: str, colours: list,
               scheme: list) -> dict:
    looks = SEAT_LOOKS.get(fam, SEAT_LOOKS["modern"])
    palette = [c for c in list(colours) + list(scheme) + list(palette_of(fam, scheme)["accent"]) if c]
    uniq: list[str] = []
    for c in palette:
        if c not in uniq:
            uniq.append(c)
    l0 = stable_hash(seed, "look") % len(looks)
    c0 = 0 if colours else stable_hash(seed, "colour") % max(1, len(uniq))
    finish = _pick(SEAT_FINISHES, seed, "finish")
    trim = _pick(("linen", "velvet", "cotton"), seed, "trim")
    # the decor stage's colours in turn over the cushions; a group alternates two looks from its end inwards, the
    # middle lumbar takes a third
    items = []
    by_group: dict[str, int] = {}
    for k, (lx, s, kind, grp) in enumerate(slots):
        i = by_group.get(grp, 0)
        by_group[grp] = i + 1
        look = looks[(l0 + i) % len(looks)] if kind == "square" else looks[(l0 + 2) % len(looks)]
        colour = uniq[(c0 + k) % len(uniq)] if uniq else None
        accent = uniq[(c0 + k + 1) % len(uniq)] if len(uniq) > 1 else colour
        if kind == "square":
            dims = [s, ACCENT_T_M, s]
        else:
            dims = [s, LUMBAR_SEAT[1], size["size"][2] if size["kind"] == "lumbar" else LUMBAR_SEAT[2]]
        items.append({"lx": round(lx, 3), "size": [round(v, 3) for v in dims], "kind": kind, "look": look,
                      "finish": finish if i % 2 == 0 else ("knife" if finish != "knife" else "piping"),
                      "trim_look": trim, "colour": colour, "accent_colour": accent, "group": grp,
                      "lean_deg": size["lean_deg"]})
    sig = (arrangement, tuple((it["look"], it["finish"], it["trim_look"]) for it in items))
    why = (f"{arrangement.replace('_', ' ')} on the {lay['kind']} seat ({len(items)} cushion(s)); {size['why']} "
           f"({TAG_SEAT})")
    return {"items": items, "arrangement": arrangement, "signature": list(sig), "why": why}

