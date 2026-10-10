"""Parametric fallback furniture (docs/milestone4.md, Conventions): simple
but recognisable shapes built from the footprint and the type height, used
when a piece has no fitted library asset or its file is missing.

Pure Python (no ``bpy``): the parts are plain vertex/face lists in the
piece's local frame of Milestone 2 (``wenart/synthetic/blocks.py``): width
along X, depth along Y, front = -Y, back (headboard, sofa back, shelf back
panel) = +Y, origin at the footprint centre on the floor, Z up. Every part
carries a material *key* (``wood``, ``fabric``, ``bedding``, ``ceramic``,
``steel``, ``painted``, ``worktop``, ``dark``, ``glass``, ``green``,
``terracotta``) that ``wenart.blender.furniture`` maps to a style slug, and a
``role`` (``body``, ``back``, ``front``, ``handle``, ``top``, ``leg``, ...)
that the tests use to check which side things are on.

Guarantees (checked in tests/test_blender_furniture.py): the XY bounding
box of the parts equals the footprint within 1 cm (handles may stand 8 mm
proud of the front), the lowest vertex is at z = 0 (the floor) and the
``back`` parts touch the +Y side while ``front`` parts touch the -Y side.
The total height may exceed the type height of ``proxies.PROXY_HEIGHTS``
(a bed headboard rises above the mattress, a toilet tank above the seat):
``piece_bbox`` reports the real box, which the camera planner uses.

Milestone 6 (docs/milestone6.md §5 rows 2 and 8), every box unchanged (the
``m5`` cameras depend on ``piece_bbox`` / ``obstacle_rect``; tests pin them
for every type):

- kitchen counter and island fronts stand 1 mm proud of the carcass (their
  front faces were coplanar with it and rendered black), the handles sit on
  the fronts;
- beds have soft bedding inside their own box: a superellipsoid mattress, a
  duvet draped over the sides with smooth deterministic wrinkles, a
  turn-down band and pillows leaning 14 degrees on the headboard (material
  keys ``bedding`` and ``duvet``); parts made of superellipsoids carry
  ``"smooth": True``;
- ``part_bevel_radius``: the bevel radius of each part for the one Bevel
  modifier furniture.py adds (per role, at most a third of the part's
  smallest side, 0 for smooth parts);
- ``decor_rest_height`` puts decor on a parametric bed on the bedding top
  (``bedding_top``), not inside the pillows.

Milestone 7 (docs/milestone7.md §6.4), four documented-only types:

- ``stair`` (fixed equipment, built by ``shell.build_stairs`` like the walls):
  ``stair_plan`` reads the drawn flights and landing (``piece["stair"]``, or
  ``piece["details"]["stair"]`` as the recognition core writes it); every
  drawn tread line is a nosing, so a flight of n lines has n risers and
  n - 1 treads, never one more or less; riser height = rise / all risers
  (rise = ceiling height + the assumed 0.15 m slab, ``riser_source``
  "derived from assumed ceiling and slab"), a warning outside 0.15-0.20 m;
  the rise direction comes from ``stair.direction`` (else +local Y, noted);
  side-by-side flights rise in turn (a U-turn): the flight rising towards
  the landing climbs first. Steps are convex prisms on a 0.15 m waist slab
  (``stair_parts``), a riser plate closes the last riser of each flight, a
  steel handrail runs 0.90 m above the nosings on every side that is not
  against a wall. The ceiling opening (``void``) covers the last flight and
  the landing only, offset 2 mm so the shaft faces never touch the steps;
  ``void_shaft`` closes it with neutral walls and a cap 0.5 m above the
  ceiling. Every assumption is listed in ``plan["assumed"]`` (the scene
  manifest's ``assumed`` entries). Without drawn flights (an AI-typed stair)
  one straight flight along +local Y with an assumed riser count fills the
  footprint, recorded as such.
- ``side_table``: round (``piece_is_round``: the piece says ``shape:
  "round"`` or a circle fits >= 90 % of its drawn points) or square.
- ``floor_lamp``: base, pole and a fabric drum shade; no light.
- ``potted_plant``: the decor plant (pot, soil, stem, crown) filling the drawn
  footprint.

``build_parts`` takes the piece for the two types that read it (``stair``,
``side_table``); the others ignore it.

Milestone 8 (docs/milestone8.md §4):

- ``frame_bedding``: the soft bedding of the parametric bed (superellipsoid
  mattress, draped duvet, turn-down band, pillows leaning back) for a
  library bed frame (``bed_frame: true``): sized to the frame's inner box
  (the footprint minus ``FRAME_INSET`` = 4 % per side, centred), the
  mattress from the fitted deck height up ``FRAME_MATTRESS_M`` (0.20 m), the
  pillows at the back (+Y) end, the duvet from the foot (-Y) end; in the
  piece frame like every part here. ``frame_bedding_info`` is its record
  (deck, mattress top, bedding top, inner box) for the fit and the manifest.
- Decor ``rug``: a flat parametric rug (``RUG_THICKNESS_M``, fabric key)
  at the size the decor rule gives (rugs and wall art are exempt from the
  0.6 m decor cap: ``LARGE_DECOR_TYPES``). ``wall_art`` has no parametric
  shape (``decor_parts`` raises): without a library model it is not built.

Milestone 10 (docs/milestone10.md §4.4-§4.7, §1.6b row 15; track F):

- The 14 new types: the corner sofa (``l_parts``: the main seat along the back
  and the chaise on ``chaise_side``, one arm at the far end), chaise, ottoman,
  bench, bar stool, office chair (a five-star base inside the seat's
  footprint), console table, crib, bunk bed (guard rail, ladder), sideboard,
  shoe, display, tall and wall cabinets (a wall cabinet is built from z = 0 of
  its frame; ``furniture.py`` hangs it at ``mount_bottom_m``).
- Cabinet fronts (``cabinet_fronts``) in the design's front style: flat slab,
  shaker (a frame on a recessed panel), slatted (vertical slats on a dark
  backing), glass (a pane in a frame); bar handles on every front (key
  ``handle``), the fronts on key ``front``; the kitchen counter run and island
  keep their Milestone 6 boxes with these fronts; a washbasin with
  ``design.vanity`` is a wall-hung vanity under a ceramic top, a wardrobe
  with ``design.built_in`` has fronts from wall to wall; ``glass`` / ``marble``
  material tags give a table its top, ``metal`` steel legs. Builders that read
  the piece (its design, its L shape) are in ``_PIECE_BUILDERS``; every box of
  the Milestone 5 types is unchanged.
- Doors and windows (``door_parts``, ``window_parts``): pure parts in the
  opening's frame for the shell (every door style of ``DOOR_STYLES``; frames by
  material with mullions, transoms and an inside sill).
- The 12 new decor types (``_new_decor_parts``): open pleated curtains under a
  rod, a roller blind, a throw, a book stack, candles (a ``bulb`` flame each),
  a basket, a tray, a wall clock, a sculpture, a large plant of its species in
  its pot (key ``pot``), a pendant on its cord and a flush ceiling light; keys
  ``colour_*`` take the item's colour name.

Milestone 12 (docs/milestone12.md §4.7, §6.4; track S):

- Our kitchen and bath fixtures in standard sizes (the fit builds them when no audited model fits, by design):
  a full-size fridge-freezer (carcass, ventilation plinth, freezer and fridge doors with 3 mm gaps and bar handles
  inside the footprint), a front-loading washing machine (top plate, kick plate, control panel with drawer, display
  and dial, a porthole of glass over the dark drum in a chrome ring) and a shower (white tray with a drain, a glass
  front of a fixed panel and a door, glass sides in chrome profiles, a stabiliser rail, a riser, an arm with a rain
  head and a mixer).
- Cushions, throws, curtains and blinds are our procedural textiles (``wenart.blender.textiles``: a filled cushion,
  standing or lying; a cloth with folds; pleated curtain panels; roller or slatted blinds).
- No type-table rest height for decor (``decor_rest_height`` removed): decor rests on the built mesh
  (``wenart.blender.rest``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.proxies import proxy_height

Part = dict  # {"verts": [(x, y, z)], "faces": [[i, ...]], "key": str, "role": str}

# Furniture types with a parametric builder (every type of the building
# schema except ``unknown``, which keeps the striped Milestone 3 proxy box).
PARAMETRIC_TYPES: tuple[str, ...] = (
    "bed", "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk", "chair",
    "wardrobe", "dresser", "nightstand", "tv_unit", "bookshelf", "kitchen_counter", "kitchen_island",
    "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "washing_machine",
    # Milestone 7 documented-only types (docs/milestone7.md §6.4).
    "stair", "side_table", "floor_lamp", "potted_plant",
    # Milestone 10 (docs/milestone10.md §1.1): the corner sofa, seating, tables, children's beds and cabinets.
    "sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib", "bunk_bed",
    "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet",
)
# Built by shell.build_stairs with the walls (fixed equipment), never by furniture.create_furniture.
SHELL_TYPES: tuple[str, ...] = ("stair",)
DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant", "rug",   # parametric decor builders (M8: rug)
                                 # Milestone 9 (docs/milestone9.md §3): tabletop decor and the framed wall mirror
                                 "vase", "bowl", "plant_small", "table_lamp", "mirror",
                                 # Milestone 10 (docs/milestone10.md §4.6)
                                 "curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture",
                                 "plant_large", "pendant_light", "ceiling_light")
_NEW_DECOR: tuple[str, ...] = DECOR_TYPES[DECOR_TYPES.index("curtain"):]
# Milestone 10 storage built with the cabinet fronts of the design (a design detail of the piece).
CABINET_LOOK_TYPES: tuple[str, ...] = ("sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
# Decor without the 0.6 m cap (Milestone 8): a rug under a group of pieces, a picture over a sofa; M9: a mirror;
# M10: curtains and blinds by window size, a throw over a bed's foot, large plants and floor sculptures, pendants
# on their cord.
LARGE_DECOR_TYPES: tuple[str, ...] = ("rug", "wall_art", "mirror", "curtain", "blind", "throw", "plant_large",
                                      "sculpture", "pendant_light")
# Decor that rests on its host's built top (Milestone 9: the builder casts a ray down onto the host mesh).
SURFACE_DECOR_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp",
                                        "candle", "tray", "books", "sculpture", "basket")   # M10, with a host
# Seats decor rests on at seat height (cushions, a throw): Milestone 10 adds the corner sofa, chaise and bench.
SEAT_HOST_TYPES: tuple[str, ...] = ("sofa", "armchair", "sofa_corner", "chaise")
MATERIAL_KEYS: tuple[str, ...] = ("wood", "fabric", "bedding", "ceramic", "steel", "painted", "worktop", "dark",
                                  "glass", "green", "terracotta", "duvet", "mirror",
                                  # Milestone 10: cabinet fronts and handles of the design, table tops of a material
                                  # tag, plant pots, lamp bulbs (lit in the interior evening mood), rattan
                                  "front", "handle", "marble", "pot", "bulb", "rattan")
# Milestone 10 doors and windows (``door_parts`` / ``window_parts``; shell.py maps them to the looks).
OPENING_KEYS: tuple[str, ...] = ("frame", "leaf", "glass", "handle", "rail", "sill")
# Parts whose key starts with this take the item's colour (Milestone 9 AI decor: ``decor.colour``) as a tint of
# the key's material: ``accent_ceramic`` = the ceramic material tinted.
ACCENT_PREFIX = "accent_"
# The colours the AI decor names (docs/milestone9.md §4), linear RGB; a tint of the white ceramic or fabric.
DECOR_COLOURS: dict[str, tuple[float, float, float]] = {
    "white": (0.80, 0.80, 0.78), "cream": (0.74, 0.68, 0.55), "beige": (0.60, 0.52, 0.40),
    "sand": (0.55, 0.45, 0.30), "light grey": (0.50, 0.50, 0.50), "grey": (0.25, 0.25, 0.25),
    "charcoal": (0.06, 0.06, 0.065), "black": (0.02, 0.02, 0.02), "natural wood": (0.42, 0.26, 0.13),
    "terracotta": (0.45, 0.14, 0.06), "rust": (0.35, 0.09, 0.03), "mustard": (0.60, 0.40, 0.04),
    "olive": (0.18, 0.20, 0.06), "sage green": (0.30, 0.38, 0.27), "forest green": (0.04, 0.12, 0.05),
    "navy": (0.02, 0.04, 0.13), "dusty blue": (0.25, 0.33, 0.45), "teal": (0.02, 0.20, 0.20),
    "blush": (0.70, 0.42, 0.38), "burgundy": (0.18, 0.02, 0.04), "brass": (0.55, 0.40, 0.12),
    "copper": (0.55, 0.25, 0.12),
}
BED_TYPES: tuple[str, ...] = ("bed", "bed_single", "bed_double")
COUNTER_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
# Kitchen fronts: this gap between the carcass front face and the back of a front.
FRONT_GAP = 0.001
FRONT_THICKNESS = 0.018
# Pillows lean back on the headboard by this angle.
PILLOW_TILT_DEG = 14.0
# Bevel (docs/milestone6.md §5 row 8): one Bevel modifier per piece, limit
# method WEIGHT, width BEVEL_WIDTH_M, BEVEL_SEGMENTS segments; every edge gets
# weight = radius / BEVEL_WIDTH_M from its part (furniture.py). Radii in
# metres per part role; fabric and bedding parts are soft whatever their role.
BEVEL_WIDTH_M = 0.05
BEVEL_SEGMENTS = 3
BEVEL_DEFAULT_M = 0.004
BEVEL_BY_ROLE: dict[str, float] = {
    "pillow": 0.045, "cushion": 0.035, "top": 0.004, "body": 0.006, "back": 0.008, "arm": 0.03, "front": 0.003,
    "handle": 0.002, "leg": 0.003, "shelf": 0.002, "side": 0.003, "bottom": 0.002, "drawers": 0.003,
    "plinth": 0.002, "tray": 0.01, "basin": 0.008, "pedestal": 0.02,
    # Milestone 7
    "step": 0.003, "riser": 0.002, "landing": 0.003, "rail": 0.008, "post": 0.004, "base": 0.006,
    "pole": 0.0, "shade": 0.004,
    # Milestone 10
    "panel": 0.002, "rod": 0.0, "roller": 0.0, "slat": 0.002, "castor": 0.004, "rest": 0.003, "ladder": 0.004,
    "leaf": 0.003, "frame": 0.002, "mullion": 0.002, "transom": 0.002, "sill": 0.003, "rim": 0.003, "book": 0.003,
    "candle": 0.0, "plate": 0.0, "canopy": 0.0, "cord": 0.0,
}
BEVEL_SOFT_KEYS: dict[str, float] = {"fabric": 0.03, "bedding": 0.03, "duvet": 0.03}
BEVEL_BY_KEY: dict[str, float] = {"ceramic": 0.012}

# How far a handle or a door may stand proud of the footprint (metres);
# the tests allow 1 cm.
PROUD = 0.008
# Largest decor dimension (docs/milestone4.md, Conventions: never larger than 0.6 m).
DECOR_MAX_M = 0.6
DECOR_DEFAULT_HEIGHT = {"cushion": 0.12, "book_set": 0.22, "plant": 0.6, "rug": 0.012, "wall_art": 0.6,
                        # Milestone 9
                        "vase": 0.30, "bowl": 0.10, "plant_small": 0.35, "table_lamp": 0.50, "mirror": 0.80,
                        # Milestone 10 (typical sizes, assumed)
                        "curtain": 2.4, "blind": 1.3, "throw": 0.05, "books": 0.12, "candle": 0.2, "basket": 0.35,
                        "tray": 0.04, "clock": 0.35, "sculpture": 0.4, "plant_large": 1.6, "pendant_light": 0.6,
                        "ceiling_light": 0.12}
MIRROR_FRAME_M = 0.03            # the parametric mirror: frame width and depth; the glass sits on its front
RUG_THICKNESS_M = 0.012
# Bed frames (Milestone 8): the mattress on the deck and the inner box the bedding fills.
FRAME_MATTRESS_M = 0.20
FRAME_INSET = 0.04
SHELF_PITCH = 0.35


# --------------------------------------------------------------------------
# Primitive helpers (local frame, z from the floor)
# --------------------------------------------------------------------------

def _box(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str = "body") -> Part:
    verts, faces = geom2d.box((cx, cy, z0 + h / 2.0), (w, d, h), 0.0)
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _cylinder_z(cx: float, cy: float, z0: float, rx: float, ry: float, h: float, key: str, role: str = "body",
                n: int = 24) -> Part:
    """Elliptic cylinder along Z (outward normals: side quads ccw, top cap ccw
    seen from above, bottom cap reversed)."""
    bottom = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    top = [(x, y, z0 + h) for x, y, _ in bottom]
    verts = bottom + top
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))           # top, ccw from above
    faces.append(list(range(n - 1, -1, -1)))      # bottom, reversed
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _cylinder_y(cx: float, y0: float, cz: float, rx: float, rz: float, length: float, key: str,
                role: str = "body", n: int = 24) -> Part:
    """Elliptic cylinder along +Y from ``y0`` to ``y0 + length`` (a rotated
    Z cylinder: the rotation keeps the winding, so normals stay outward)."""
    part = _cylinder_z(0.0, 0.0, 0.0, rx, rz, length, key, role, n)
    # rotate about X by -90 degrees: (x, y, z) -> (x, z, -y), so +Z -> +Y
    part["verts"] = [(cx + x, y0 + z, cz - y) for x, y, z in part["verts"]]
    return part


def _bbox(parts: Sequence[Part]) -> tuple[float, float, float, float, float, float]:
    xs = [v[0] for p in parts for v in p["verts"]]
    ys = [v[1] for p in parts for v in p["verts"]]
    zs = [v[2] for p in parts for v in p["verts"]]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def parts_bbox(parts: Sequence[Part]) -> tuple[float, float, float, float, float, float]:
    """``(min_x, min_y, min_z, max_x, max_y, max_z)`` of the parts."""
    return _bbox(parts)


# --------------------------------------------------------------------------
# Type builders. All take (w, d, h) = footprint width, depth, type height.
# --------------------------------------------------------------------------

def _sgnpow(v: float, e: float) -> float:
    return math.copysign(abs(v) ** e, v)


def _superellipsoid(cx: float, cy: float, z0: float, w: float, d: float, h: float, e_vert: float, e_horiz: float,
                    key: str, role: str, n_eta: int = 12, n_om: int = 32, wrinkle: float = 0.0, seed: float = 0.0,
                    tilt_deg: float = 0.0) -> Part:
    """Closed superellipsoid in the box ``w x d x h`` standing on ``z0`` and
    centred on ``(cx, cy)``; the box is exact (the rings pass through the
    poles, the equator and the four axis directions: ``n_eta`` even,
    ``n_om`` a multiple of 4). ``e_vert`` < 1 flattens the top and bottom
    (duvet 0.18, pillow 0.55), ``e_horiz`` < 1 squares the corners.
    ``wrinkle`` (metres) adds a smooth deterministic bump field to the upper
    half, clamped inside the box. ``tilt_deg`` turns the part about its
    centre's X axis so its +Y end rises (a pillow propped up on the
    headboard) and lifts it back onto ``z0`` (its box then turns with it).
    Outward normals; ``"smooth": True``."""
    a, b, c = w / 2.0, d / 2.0, h / 2.0
    t = math.radians(tilt_deg)
    ct, st = math.cos(t), math.sin(t)

    def place(x: float, y: float, z: float) -> tuple[float, float, float]:
        if tilt_deg:
            y, z = y * ct - z * st, y * st + z * ct
        return (cx + x, cy + y, z0 + c + z)

    verts = [place(0.0, 0.0, -c)]                  # bottom pole
    rings = []
    for i in range(1, n_eta):
        eta = -math.pi / 2.0 + math.pi * i / n_eta
        ring = []
        for j in range(n_om):
            om = -math.pi + 2.0 * math.pi * j / n_om
            x = a * _sgnpow(math.cos(eta), e_vert) * _sgnpow(math.cos(om), e_horiz)
            y = b * _sgnpow(math.cos(eta), e_vert) * _sgnpow(math.sin(om), e_horiz)
            z = c * _sgnpow(math.sin(eta), e_vert)
            if wrinkle and z > 0:
                bump = (math.sin(7.0 * x / max(a, 1e-6) + seed) * math.sin(5.0 * y / max(b, 1e-6) + 1.3 * seed)
                        + 0.5 * math.sin(13.0 * (x + y) / max(a + b, 1e-6) + 2.1 * seed))
                z = max(-c, min(c, z + wrinkle * bump * (z / c)))
            ring.append(len(verts))
            verts.append(place(x, y, z))
        rings.append(ring)
    top = len(verts)
    verts.append(place(0.0, 0.0, c))               # top pole
    faces = []
    first = rings[0]
    for j in range(n_om):                          # bottom fan (outward = down)
        faces.append([0, first[(j + 1) % n_om], first[j]])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n_om):
            faces.append([r0[j], r0[(j + 1) % n_om], r1[(j + 1) % n_om], r1[j]])
    last = rings[-1]
    for j in range(n_om):
        faces.append([last[j], last[(j + 1) % n_om], top])
    if tilt_deg:                                   # keep the lowest point on z0 after the lean
        zmin = min(v[2] for v in verts)
        verts = [(x, y, z - (zmin - z0)) for x, y, z in verts]
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}


def _bed(w: float, d: float, h: float) -> list[Part]:
    """Bed: frame and headboard boxes (as in Milestone 4), a superellipsoid
    mattress in the Milestone 4 mattress box, a duvet draped over the sides
    with soft wrinkles over the foot 72 % of the mattress, a turn-down band
    at its head end and puffy pillows leaning on the headboard. Everything
    stays inside the frame / headboard box (``piece_bbox`` unchanged)."""
    t = min(0.06, d * 0.05)                       # headboard thickness
    frame_h = min(0.3, h * 0.55)
    top = max(1.0, h + 0.4)                        # headboard top
    inner_d = d - t
    parts = [
        _box(0.0, 0.0, 0.0, w, d, frame_h, "wood", "body"),
        _box(0.0, d / 2.0 - t / 2.0, 0.0, w, t, top, "wood", "back"),
        _superellipsoid(0.0, -t / 2.0, frame_h, w - 0.06, inner_d - 0.06, h - frame_h, 0.12, 0.08, "bedding",
                        "mattress"),
    ]
    duvet_d = inner_d * 0.72
    duvet_y = -d / 2.0 + 0.005 + duvet_d / 2.0
    drape = min(0.18, (h - frame_h) * 0.9)
    parts.append(_superellipsoid(0.0, duvet_y, h - drape, w - 0.01, duvet_d, drape + 0.05, 0.18, 0.06, "duvet",
                                 "duvet", n_eta=14, n_om=48, wrinkle=0.012, seed=1.7))
    parts.append(_superellipsoid(0.0, duvet_y + duvet_d / 2.0 - 0.13, h + 0.02, w - 0.03, 0.26, 0.05, 0.35, 0.1,
                                 "bedding", "turndown", n_om=40))
    n = 2 if w >= 1.3 else 1
    pw = (w - 0.1) / n - 0.05
    pd = min(0.45, d * 0.22)
    py = d / 2.0 - t - 0.05 - pd / 2.0
    for i in range(n):
        px = 0.0 if n == 1 else (-1 if i == 0 else 1) * (pw / 2.0 + 0.025)
        parts.append(_superellipsoid(px, py, h - 0.01, pw, pd, 0.16, 0.55, 0.25, "bedding", "pillow",
                                     tilt_deg=PILLOW_TILT_DEG))
    return parts


def bedding_top(w: float, d: float, h: float) -> float:
    """Height of the highest bedding point of a parametric bed (pillows, duvet, band)."""
    return max(v[2] for p in _bed(float(w), float(d), float(h)) if p["key"] in ("bedding", "duvet")
               for v in p["verts"])


def frame_inner_box(w: float, d: float, inset: float = FRAME_INSET) -> tuple[float, float]:
    """``(width, depth)`` of a bed frame's inner box: the footprint minus ``inset`` (a share) per side."""
    return (float(w) * (1.0 - 2.0 * inset), float(d) * (1.0 - 2.0 * inset))


def frame_bedding(w: float, d: float, deck_z: float, mattress_h: float = FRAME_MATTRESS_M,
                  inset: float = FRAME_INSET) -> list[Part]:
    """The parametric bedding on a library bed frame of footprint ``w x d`` (docs/milestone8.md §4), in the
    piece frame (origin at the footprint centre on the floor, foot = -Y, head = +Y): the ``_bed`` mattress,
    duvet, turn-down band and pillows with the same shapes, keys and roles, but the mattress fills the
    frame's inner box (``frame_inner_box``, centred) from ``deck_z`` up ``mattress_h`` (its top at
    ``deck_z + mattress_h``), the duvet drapes 2.5 cm past the mattress sides (never past the footprint)
    over its foot 72 %, the pillows lean at the head end of the inner box."""
    iw, idp = frame_inner_box(w, d, inset)
    deck_z, mattress_h = float(deck_z), float(mattress_h)
    top = deck_z + mattress_h
    parts = [_superellipsoid(0.0, 0.0, deck_z, iw, idp, mattress_h, 0.12, 0.08, "bedding", "mattress")]
    duvet_w = min(float(w), iw + 0.05)
    duvet_d = idp * 0.72
    duvet_y = -idp / 2.0 + 0.005 + duvet_d / 2.0
    drape = min(0.18, mattress_h * 0.9)
    parts.append(_superellipsoid(0.0, duvet_y, top - drape, duvet_w, duvet_d, drape + 0.05, 0.18, 0.06, "duvet",
                                 "duvet", n_eta=14, n_om=48, wrinkle=0.012, seed=1.7))
    parts.append(_superellipsoid(0.0, duvet_y + duvet_d / 2.0 - 0.13, top + 0.02, duvet_w - 0.02, 0.26, 0.05, 0.35,
                                 0.1, "bedding", "turndown", n_om=40))
    n = 2 if float(w) >= 1.3 else 1
    pw = (iw - 0.1) / n - 0.05
    pd = min(0.45, idp * 0.22)
    py = idp / 2.0 - 0.05 - pd / 2.0
    for i in range(n):
        px = 0.0 if n == 1 else (-1 if i == 0 else 1) * (pw / 2.0 + 0.025)
        parts.append(_superellipsoid(px, py, top - 0.01, pw, pd, 0.16, 0.55, 0.25, "bedding", "pillow",
                                     tilt_deg=PILLOW_TILT_DEG))
    return parts


def frame_bedding_info(w: float, d: float, deck_z: float, mattress_h: float = FRAME_MATTRESS_M,
                       inset: float = FRAME_INSET) -> dict:
    """The record of ``frame_bedding`` (the fit's ``asset.bedding``, the manifest's ``bedding``): deck and
    mattress top above the floor, the highest bedding point (pillows), the inner box and the rule."""
    parts = frame_bedding(w, d, deck_z, mattress_h, inset)
    iw, idp = frame_inner_box(w, d, inset)
    mattress = next(p for p in parts if p["role"] == "mattress")
    return {"deck_z_m": round(float(deck_z), 4), "mattress_m": float(mattress_h),
            "mattress_top_m": round(max(v[2] for v in mattress["verts"]), 4),
            "top_m": round(max(v[2] for p in parts for v in p["verts"]), 4),
            "inner_box_m": [round(iw, 4), round(idp, 4)], "inset": inset,
            "pillows": sum(1 for p in parts if p["role"] == "pillow")}


def _sofa(w: float, d: float, h: float, cushions: int | None = None) -> list[Part]:
    back_t = min(0.2, d * 0.25)
    arm_w = min(0.15, w * 0.1)
    seat_h = sofa_seat_height(h)
    arm_h = min(0.65, h * 0.8)
    seat_w = w - 2 * arm_w
    seat_d = d - back_t
    parts = [
        _box(0.0, -back_t / 2.0, 0.0, seat_w, seat_d, seat_h - 0.1, "fabric", "body"),
        _box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, "fabric", "back"),
        _box(-(w / 2.0 - arm_w / 2.0), -back_t / 2.0, 0.0, arm_w, seat_d, arm_h, "fabric", "arm"),
        _box((w / 2.0 - arm_w / 2.0), -back_t / 2.0, 0.0, arm_w, seat_d, arm_h, "fabric", "arm"),
    ]
    n = cushions or max(1, round(seat_w / 0.75))
    cw = seat_w / n
    for i in range(n):
        cx = -seat_w / 2.0 + cw * (i + 0.5)
        parts.append(_box(cx, -back_t / 2.0, seat_h - 0.1, cw - 0.03, seat_d - 0.04, 0.1, "fabric", "cushion"))
    return parts


def sofa_seat_height(h: float) -> float:
    return min(0.45, h * 0.55)


def _chair(w: float, d: float, h: float) -> list[Part]:
    seat_h = min(0.45, h / 2.0)
    leg = min(0.04, w * 0.1)
    t = min(0.04, d * 0.1)
    parts = [_box(0.0, 0.0, seat_h - 0.04, w, d, 0.04, "wood", "top"),
             _box(0.0, d / 2.0 - t / 2.0, seat_h, w, t, h - seat_h, "wood", "back")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - leg / 2.0), sy * (d / 2.0 - leg / 2.0), 0.0, leg, leg, seat_h - 0.04,
                              "wood", "leg"))
    return parts


def _table(w: float, d: float, h: float, desk: bool = False) -> list[Part]:
    top_t = 0.04
    leg = min(0.06, w * 0.08, d * 0.08)
    inset = min(0.04, w * 0.05, d * 0.05)
    parts = [_box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - inset - leg / 2.0), sy * (d / 2.0 - inset - leg / 2.0), 0.0, leg, leg,
                              h - top_t, "wood", "leg"))
    if desk:
        dw, dd, dh = w * 0.3, d - 2 * inset - 0.02, min(0.35, h * 0.45)
        dx = w / 2.0 - inset - leg - 0.01 - dw / 2.0
        parts.append(_box(dx, 0.0, h - top_t - dh, dw, dd, dh, "painted", "drawers"))
        parts.append(_box(dx, -d / 2.0 + inset + 0.01 - PROUD / 2.0, h - top_t - dh / 2.0, min(0.12, dw * 0.6),
                          PROUD, 0.015, "steel", "handle"))
    return parts


def _cabinet(w: float, d: float, h: float, rows: int, cols: int, doors: bool) -> list[Part]:
    """Box with drawer fronts (or door panels) and handles on the front."""
    parts = [_box(0.0, 0.01, 0.0, w, d - 0.02, h, "wood", "body")]
    gap = 0.02
    rh = (h - 0.1) / rows if doors else h / rows
    cw = w / cols
    z_base = 0.05 if doors else 0.0
    for r in range(rows):
        for c in range(cols):
            cx = -w / 2.0 + cw * (c + 0.5)
            z0 = z_base + rh * r
            parts.append(_box(cx, -d / 2.0 + 0.01, z0 + gap / 2.0, cw - gap, 0.02, rh - gap, "painted", "front"))
            if doors:
                hx = cx + (0.03 if c % 2 == 0 else -0.03)
                parts.append(_box(hx, -d / 2.0 - PROUD / 2.0, h / 2.0 - 0.075, 0.015, PROUD, 0.15, "steel", "handle"))
            else:
                parts.append(_box(cx, -d / 2.0 - PROUD / 2.0, z0 + rh / 2.0, min(0.12, (cw - gap) * 0.5), PROUD,
                                  0.015, "steel", "handle"))
    return parts


def _wardrobe(w: float, d: float, h: float) -> list[Part]:
    return _cabinet(w, d, h, rows=1, cols=max(2, round(w / 0.5)), doors=True)


def _drawers(w: float, d: float, h: float) -> list[Part]:
    rows = max(1, int(h / 0.25))
    return _cabinet(w, d, h, rows=rows, cols=1, doors=False)


def _tv_unit(w: float, d: float, h: float) -> list[Part]:
    return _cabinet(w, d, h, rows=1, cols=max(1, round(w / 0.6)), doors=False)


def shelf_heights(h: float, t: float = 0.02) -> list[float]:
    """Top faces of the inner shelves of a bookshelf of height ``h``."""
    out = []
    z = SHELF_PITCH
    while z < h - t - 0.15:
        out.append(round(z, 4))
        z += SHELF_PITCH
    return out


def _bookshelf(w: float, d: float, h: float) -> list[Part]:
    t = 0.02
    parts = [
        _box(-(w / 2.0 - t / 2.0), 0.0, 0.0, t, d, h, "wood", "side"),
        _box((w / 2.0 - t / 2.0), 0.0, 0.0, t, d, h, "wood", "side"),
        _box(0.0, 0.0, 0.0, w, d, t, "wood", "bottom"),
        _box(0.0, 0.0, h - t, w, d, t, "wood", "top"),
        _box(0.0, d / 2.0 - 0.005, 0.0, w, 0.01, h, "wood", "back"),
    ]
    for z in shelf_heights(h, t):
        parts.append(_box(0.0, -0.005, z - t, w - 2 * t, d - 0.01, t, "wood", "shelf"))
    return parts


def _counter(w: float, d: float, h: float, island: bool = False) -> list[Part]:
    top_t = 0.04
    plinth_h = min(0.1, h * 0.12)
    inset = 0.03
    if island:
        carcass = _box(0.0, 0.0, plinth_h, w - 2 * inset, d - 2 * inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, 0.0, 0.0, w - 4 * inset, d - 4 * inset, plinth_h, "dark", "plinth")
        front_y = -d / 2.0 + inset
    else:
        carcass = _box(0.0, inset / 2.0, plinth_h, w, d - inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, inset, 0.0, w, d - 2 * inset, plinth_h, "dark", "plinth")
        front_y = -d / 2.0 + inset
    parts = [plinth, carcass, _box(0.0, 0.0, h - top_t, w, d, top_t, "worktop", "top")]
    cols = max(1, round(w / 0.6))
    cw = w / cols
    # Fronts stand FRONT_GAP proud of the carcass face at front_y (Milestone 5 put them
    # inside the carcass with coplanar front faces: rendered black); handles on the fronts.
    front_face = front_y - FRONT_GAP - FRONT_THICKNESS
    for c in range(cols):
        cx = -w / 2.0 + cw * (c + 0.5)
        parts.append(_box(cx, front_y - FRONT_GAP - FRONT_THICKNESS / 2.0, plinth_h + 0.01, cw - 0.02,
                          FRONT_THICKNESS, h - top_t - plinth_h - 0.03, "painted", "front"))
        parts.append(_box(cx, front_face - PROUD / 2.0, h - top_t - 0.06, min(0.12, cw * 0.5), PROUD, 0.015,
                          "steel", "handle"))
    return parts


# Milestone 12 (docs/milestone12.md §6.4 D24, track S): our full-size fridge, washing machine and shower in standard
# sizes, built from the footprint (the fit takes them when no audited model fits: kitchen and bath fixtures come
# from code). Real proportions: doors inset in front of the carcass with 3 mm gaps, handles inside the footprint.
FIXTURE_GAP_M = 0.003
FRIDGE_DOOR_T = 0.045            # the doors' thickness in front of the carcass
FRIDGE_FREEZER_SHARE = 0.36      # a bottom freezer: this share of the height under the fridge door
FRIDGE_PLINTH_M = 0.08
WASHER_PANEL_M = 0.14            # the control panel strip at the top front
WASHER_FRONT_T = 0.012
SHOWER_TRAY_M = 0.04
SHOWER_GLASS_T = 0.008
SHOWER_PROFILE_M = 0.02          # the chrome profiles at the glass edges


def _fridge(w: float, d: float, h: float) -> list[Part]:
    """A full-size fridge-freezer (Milestone 12): carcass, a dark ventilation plinth, a bottom freezer door and the
    fridge door above it with 3 mm gaps, a vertical bar handle on each door (inside the footprint), a top cap."""
    t = min(FRIDGE_DOOR_T, d * 0.1)
    face = -d / 2.0 + t                            # the doors' back = the carcass front
    plinth = min(FRIDGE_PLINTH_M, h * 0.06)
    split = plinth + (h - plinth) * FRIDGE_FREEZER_SHARE
    g = FIXTURE_GAP_M
    hx = w / 2.0 - 0.06
    parts = [
        _box(0.0, face + (d / 2.0 - face) / 2.0, 0.0, w, d / 2.0 - face, h, "steel", "body"),
        _box(0.0, (-d / 2.0 + 0.02 + face) / 2.0, 0.0, w - 0.02, face - (-d / 2.0 + 0.02), plinth - g, "dark",
             "plinth"),
        _box(0.0, -d / 2.0 + 0.012 + (t - 0.012) / 2.0, plinth, w - 2 * g, t - 0.012, split - plinth - g / 2.0,
             "steel", "front"),
        _box(0.0, -d / 2.0 + 0.012 + (t - 0.012) / 2.0, split + g / 2.0, w - 2 * g, t - 0.012,
             h - split - g / 2.0 - g, "steel", "front"),
    ]
    for z0, z1 in ((plinth + 0.06, split - 0.12), (split + 0.12, split + 0.12 + (h - split) * 0.45)):
        parts.append(_box(hx, -d / 2.0 + 0.006, z0, 0.022, 0.012, max(0.1, z1 - z0), "steel", "handle"))
    return parts


def _stove(w: float, d: float, h: float) -> list[Part]:
    r = min(w, d) * 0.14
    parts = [
        _box(0.0, 0.0, 0.0, w, d, h - 0.02, "steel", "body"),
        _box(0.0, 0.0, h - 0.02, w, d, 0.02, "dark", "top"),
        _box(0.0, -d / 2.0 - PROUD / 2.0, h * 0.55, w - 0.08, PROUD, 0.02, "steel", "handle"),  # oven handle
        _box(0.0, -d / 2.0 - PROUD / 4.0, h * 0.2, w - 0.1, PROUD / 2.0, h * 0.3, "dark", "front"),  # oven glass
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_cylinder_z(sx * w / 4.0, sy * d / 4.0, h, r, r, PROUD, "steel", "ring", n=20))
    return parts


def _basin(cx: float, cy: float, z0: float, bw: float, bd: float, depth: float, wall: float, key: str) -> list[Part]:
    """Open basin: four walls and a bottom around an inner void."""
    return [
        _box(cx, cy - bd / 2.0 + wall / 2.0, z0, bw, wall, depth, key, "basin"),
        _box(cx, cy + bd / 2.0 - wall / 2.0, z0, bw, wall, depth, key, "basin"),
        _box(cx - bw / 2.0 + wall / 2.0, cy, z0, wall, bd - 2 * wall, depth, key, "basin"),
        _box(cx + bw / 2.0 - wall / 2.0, cy, z0, wall, bd - 2 * wall, depth, key, "basin"),
        _box(cx, cy, z0, bw - 2 * wall, bd - 2 * wall, wall, key, "basin"),
    ]


def _sink(w: float, d: float, h: float) -> list[Part]:
    top_t = 0.02
    bw = min(w - 0.16, 0.5)
    bd = min(d - 0.16, 0.4)
    sx, sy = (w - bw) / 2.0, (d - bd) / 2.0  # strip widths around the basin hole
    parts = [
        _box(0.0, 0.01, 0.0, w, d - 0.02, h - top_t, "painted", "body"),
        _box(0.0, -d / 2.0 + 0.01, 0.02, w - 0.04, 0.02, h - top_t - 0.04, "painted", "front"),
        _box(0.0, -d / 2.0 + sy / 2.0, h - top_t, w, sy, top_t, "steel", "top"),
        _box(0.0, d / 2.0 - sy / 2.0, h - top_t, w, sy, top_t, "steel", "top"),
        _box(-w / 2.0 + sx / 2.0, 0.0, h - top_t, sx, bd, top_t, "steel", "top"),
        _box(w / 2.0 - sx / 2.0, 0.0, h - top_t, sx, bd, top_t, "steel", "top"),
    ]
    parts += _basin(0.0, 0.0, h - 0.18, bw, bd, 0.18, 0.01, "steel")
    tap_y = min(bd / 2.0 + 0.04, d / 2.0 - 0.03)
    parts.append(_cylinder_z(0.0, tap_y, h, 0.015, 0.015, 0.25, "steel", "tap", n=12))
    return parts


def _washbasin(w: float, d: float, h: float) -> list[Part]:
    basin_h = min(0.15, h * 0.2)
    ped = min(0.18, w * 0.4, d * 0.4)
    parts = [_box(0.0, d / 2.0 - 0.05 - ped / 2.0, 0.0, ped, ped, h - basin_h, "ceramic", "pedestal")]
    parts += _basin(0.0, 0.0, h - basin_h, w, d, basin_h, 0.03, "ceramic")
    parts.append(_cylinder_z(0.0, d / 2.0 - 0.04, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    return parts


def _toilet(w: float, d: float, h: float) -> list[Part]:
    tank_d = min(0.18, d * 0.3)
    bowl_d = d - tank_d
    return [
        _box(0.0, d / 2.0 - tank_d / 2.0, 0.2, w, tank_d, h + 0.4 - 0.2, "ceramic", "back"),
        _cylinder_z(0.0, -tank_d / 2.0, 0.0, w / 2.0, bowl_d / 2.0, h - 0.03, "ceramic", "bowl"),
        _cylinder_z(0.0, -tank_d / 2.0, h - 0.03, w / 2.0 * 0.98, bowl_d / 2.0 * 0.98, 0.03, "painted", "seat"),
    ]


def _shower(w: float, d: float, h: float) -> list[Part]:
    """A shower (Milestone 12): a low white tray with a steel drain, clear glass on the front (a fixed panel and a
    door with a 6 mm gap) and both sides in chrome profiles with a top stabiliser rail, and on the back a riser
    pipe, an arm and a round rain head with a mixer at hand height."""
    tray = min(SHOWER_TRAY_M, h * 0.05)
    gt, pm = SHOWER_GLASS_T, SHOWER_PROFILE_M
    gh = h - tray
    parts = [
        _box(0.0, 0.0, 0.0, w, d, tray, "ceramic", "tray"),
        _cylinder_z(0.0, 0.0, tray, min(0.05, w / 8.0), min(0.05, d / 8.0), 0.002, "steel", "drain", n=20),
    ]
    door = w * 0.5
    fixed = w - door - 0.006 - 2 * pm
    yf = -d / 2.0 + gt / 2.0
    parts.append(_box(-w / 2.0 + pm + fixed / 2.0, yf, tray, fixed, gt, gh - 0.01, "glass", "front"))
    parts.append(_box(w / 2.0 - pm - door / 2.0, yf, tray + 0.005, door - 0.006, gt, gh - 0.02, "glass", "front"))
    for sx in (-1, 1):
        parts.append(_box(sx * (w / 2.0 - gt / 2.0), pm / 2.0, tray, gt, d - pm, gh - 0.01, "glass", "side"))
        parts.append(_box(sx * (w / 2.0 - pm / 2.0), -d / 2.0 + pm / 2.0, tray, pm, pm, gh, "steel", "frame"))
        parts.append(_box(sx * (w / 2.0 - pm / 2.0), d / 2.0 - pm / 2.0, tray, pm, pm, gh, "steel", "frame"))
    parts.append(_box(0.0, -d / 2.0 + pm / 2.0, h - pm, w - 2 * pm, pm, pm, "steel", "rail"))
    riser_y = d / 2.0 - 0.03
    head_r = min(0.12, w / 5.0, d / 5.0)
    parts.append(_cylinder_z(0.0, riser_y, 1.0, 0.012, 0.012, h - 0.12 - 1.0, "steel", "pipe", n=12))
    parts.append(_cylinder_y(0.0, riser_y - 0.25, h - 0.13, 0.01, 0.01, 0.25, "steel", "arm", n=12))
    parts.append(_cylinder_z(0.0, riser_y - 0.25, h - 0.16, head_r, head_r, 0.015, "steel", "head", n=32))
    parts.append(_box(0.0, riser_y + 0.005, 1.05, 0.08, 0.04, 0.16, "steel", "mixer"))
    return parts


def _bathtub(w: float, d: float, h: float) -> list[Part]:
    t = min(0.08, w * 0.08, d * 0.12)
    parts = _basin(0.0, 0.0, 0.0, w, d, h, t, "ceramic")
    parts[-1] = _box(0.0, 0.0, 0.0, w - 2 * t, d - 2 * t, min(0.1, h * 0.2), "ceramic", "basin")
    parts.append(_cylinder_z(w / 2.0 - t / 2.0, 0.0, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    return parts


def _washing_machine(w: float, d: float, h: float) -> list[Part]:
    """A front-loading washing machine (Milestone 12): a white body with a top plate, a dark kick plate, the control
    panel strip with a detergent drawer, a dark display and a steel dial, and the porthole door: a chrome ring
    around a glass window in front of the dark drum."""
    ft = min(WASHER_FRONT_T, d * 0.03)
    face = -d / 2.0 + ft
    r = min(w, h) * 0.25
    zc = h * 0.42
    panel = min(WASHER_PANEL_M, h * 0.18)
    parts = [
        _box(0.0, face + (d / 2.0 - face) / 2.0, 0.0, w, d / 2.0 - face, h - 0.02, "painted", "body"),
        _box(0.0, 0.0, h - 0.02, w, d, 0.02, "painted", "top"),
        _box(0.0, face - ft / 4.0, 0.0, w - 0.04, ft / 2.0, 0.07, "dark", "plinth"),
        _box(-w / 2.0 + 0.11, face - ft / 2.0, h - panel + 0.015, 0.18, ft, panel - 0.05, "painted", "front"),
        _box(w * 0.05, face - ft / 4.0, h - panel + 0.035, w * 0.22, ft / 2.0, panel * 0.4, "dark", "front"),
        _cylinder_y(w / 2.0 - 0.08, face - ft, h - panel / 2.0 - 0.01, 0.028, 0.028, ft, "steel", "front", n=24),
        # the porthole, front to back: the glass, the dark drum seen through it, the chrome ring around them
        _cylinder_y(0.0, face - ft, zc, r, r, ft / 3.0, "glass", "front", n=40),
        _cylinder_y(0.0, face - ft * 2.0 / 3.0, zc, r, r, ft / 3.0, "dark", "front", n=40),
        _cylinder_y(0.0, face - ft / 3.0, zc, r + 0.035, r + 0.035, ft / 3.0, "steel", "front", n=40),
    ]
    return parts


# --------------------------------------------------------------------------
# Milestone 7: side table, floor lamp, potted plant (docs/milestone7.md §6.4)
# --------------------------------------------------------------------------

# A drawn piece is round when a circle fits at least this share of its points (the recognition core
# records ``shape: "round"`` or ``circle_fit: {"share": s}`` on the piece or in its ``details``).
ROUND_FIT_SHARE = 0.9
ROUND_SHAPES = ("round", "circle", "circular")


def piece_is_round(piece: dict | None) -> bool:
    """True when the building says the drawn piece is round: ``shape`` in
    ``ROUND_SHAPES`` or ``circle_fit.share >= ROUND_FIT_SHARE`` on the piece
    or in its ``details``. Nothing is guessed from the footprint (a square
    footprint is the box of a round and of a square table alike)."""
    if not piece:
        return False
    for src in (piece, piece.get("details") or {}):
        shape = src.get("shape")
        if isinstance(shape, str) and shape.strip().lower() in ROUND_SHAPES:
            return True
        fit = src.get("circle_fit")
        share = fit.get("share") if isinstance(fit, dict) else None
        if isinstance(share, (int, float)) and not isinstance(share, bool) and share >= ROUND_FIT_SHARE:
            return True
    return False


def _frustum_z(cx: float, cy: float, z0: float, rx0: float, ry0: float, rx1: float, ry1: float, h: float,
               key: str, role: str, n: int = 32) -> Part:
    """Elliptic truncated cone along Z (bottom radii ``rx0, ry0``, top ``rx1, ry1``), wound outwards."""
    bottom = [(cx + rx0 * math.cos(2 * math.pi * i / n), cy + ry0 * math.sin(2 * math.pi * i / n), z0)
              for i in range(n)]
    top = [(cx + rx1 * math.cos(2 * math.pi * i / n), cy + ry1 * math.sin(2 * math.pi * i / n), z0 + h)
           for i in range(n)]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))
    faces.append(list(range(n - 1, -1, -1)))
    return {"verts": bottom + top, "faces": faces, "key": key, "role": role}


def _side_table(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Round side table (top disc, pedestal, base disc) when ``piece_is_round``,
    else a square one (top, four legs, a lower shelf)."""
    top_t = min(0.03, h * 0.1)
    if piece_is_round(piece):
        base_t = min(0.025, h * 0.08)
        col = min(0.035, w * 0.12, d * 0.12)
        return [
            _cylinder_z(0.0, 0.0, h - top_t, w / 2.0, d / 2.0, top_t, "wood", "top", n=40),
            _cylinder_z(0.0, 0.0, base_t, col, col, h - top_t - base_t, "wood", "leg", n=16),
            _cylinder_z(0.0, 0.0, 0.0, w * 0.3, d * 0.3, base_t, "wood", "base", n=32),
        ]
    leg = min(0.035, w * 0.1, d * 0.1)
    inset = min(0.02, w * 0.05, d * 0.05)
    parts = [_box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - inset - leg / 2.0), sy * (d / 2.0 - inset - leg / 2.0), 0.0, leg, leg,
                              h - top_t, "wood", "leg"))
    shelf_w, shelf_d = w - 2 * (inset + leg), d - 2 * (inset + leg)
    if shelf_w > 0.05 and shelf_d > 0.05:
        parts.append(_box(0.0, 0.0, min(0.15, h * 0.3), shelf_w, shelf_d, 0.02, "wood", "shelf"))
    return parts


def _floor_lamp(w: float, d: float, h: float) -> list[Part]:
    """Floor lamp: a dark base disc, a steel pole and a fabric drum shade
    whose bottom rim fills the footprint. Geometry only: no light."""
    base_t = 0.025
    shade_h = min(0.4, h * 0.3)
    r = min(w, d)
    return [
        _cylinder_z(0.0, 0.0, 0.0, max(0.05, r * 0.35), max(0.05, r * 0.35), base_t, "dark", "base", n=32),
        _cylinder_z(0.0, 0.0, base_t, 0.012, 0.012, h - shade_h + 0.05 - base_t, "steel", "pole", n=12),
        _frustum_z(0.0, 0.0, h - shade_h, w / 2.0, d / 2.0, w / 2.0 * 0.8, d / 2.0 * 0.8, shade_h, "bedding",
                   "shade"),
    ]


def _potted_plant(w: float, d: float, h: float) -> list[Part]:
    """The decor plant (``decor_parts("plant")``: terracotta pot, soil, stem,
    green crown) at the drawn size: the crown fills the footprint."""
    rx, ry = w / 2.0, d / 2.0
    pot_h = h * 0.35
    return [
        _cylinder_z(0.0, 0.0, 0.0, rx * 0.7, ry * 0.7, pot_h, "terracotta", "pot", n=24),
        _cylinder_z(0.0, 0.0, pot_h - 0.01, rx * 0.62, ry * 0.62, 0.01, "dark", "soil", n=24),
        _cylinder_z(0.0, 0.0, pot_h, 0.012, 0.012, (h - pot_h) * 0.4, "wood", "stem", n=8),
        _cylinder_z(0.0, 0.0, pot_h + (h - pot_h) * 0.35, rx, ry, (h - pot_h) * 0.65, "green", "crown", n=16),
    ]


# --------------------------------------------------------------------------
# Milestone 7: stair (docs/milestone7.md §6.4)
# --------------------------------------------------------------------------

STAIR_SLAB_M = 0.15                # assumed slab between the ceiling and the floor above
STAIR_WAIST_M = 0.15               # assumed waist slab under the steps; also the landing slab
STAIR_RISER_RANGE = (0.15, 0.20)   # a derived riser outside this range is a warning
STAIR_GENERIC_RISER_M = 0.175      # riser of a stair without drawn flights (count assumed)
STAIR_RAIL_HEIGHT = 0.90           # handrail top above the nosing line
STAIR_RAIL_W = 0.04
STAIR_RAIL_T = 0.05
STAIR_RAIL_INSET = 0.04            # rail centre this far inside the flight side
STAIR_RAIL_MIN_M = 0.3             # a rail shorter than this (cut by the cap) is left out
STAIR_POST = 0.04
STAIR_RISER_PLATE = 0.02           # closes the last riser of a flight, standing on its last tread
STAIR_SHAFT_CAP_M = 0.5            # the neutral cap of the ceiling opening, above the ceiling
STAIR_SHAFT_GAP = 0.002            # the void stands this far outside the steps and the landing
STAIR_SHAFT_LIP = 0.02             # shaft faces reach this far below the ceiling: a slab edge, no slit
STAIR_CAP_CLEARANCE = 0.03         # rails stay this far below the cap
STAIR_HEADROOM_M = 2.0             # below this under the ceiling at a flight's top: a warning
STAIR_WALL_PROBE = 0.05            # a side is against a wall when points this far outside it lie in one
STAIR_RISER_SOURCE = "derived from assumed ceiling and slab"


def stair_data(piece: dict | None) -> dict | None:
    """The stair record of a piece: ``piece["stair"]`` (building JSON,
    docs/milestone7.md §1.3) or ``piece["details"]["stair"]`` (recognition
    core output); None when there is none."""
    if not piece:
        return None
    data = piece.get("stair")
    if not isinstance(data, dict):
        data = (piece.get("details") or {}).get("stair")
    return data if isinstance(data, dict) else None


def _v(a, b) -> tuple[float, float]:
    return (float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def _d2(a, b) -> float:
    return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1])


def _unit2(v) -> tuple[float, float] | None:
    n = math.hypot(float(v[0]), float(v[1]))
    return None if n < 1e-9 else (float(v[0]) / n, float(v[1]) / n)


def _local_to_world2(p, center, rot) -> tuple[float, float]:
    return G.rotate_point((float(center[0]) + p[0], float(center[1]) + p[1]), rot, (float(center[0]),
                                                                                     float(center[1])))


def stair_plan(piece: dict, rise: float, ceiling_height: float | None = None, cap_height: float | None = None,
               walls: Sequence[dict] = (), rise_source: str = STAIR_RISER_SOURCE) -> dict:
    """How a stair piece is built (pure; world XY, z above the level floor).

    ``rise`` = floor to the floor above (the caller: ceiling height + the
    assumed ``STAIR_SLAB_M``, or the level elevations); ``ceiling_height``
    (default ``rise - STAIR_SLAB_M``) and ``cap_height`` (default ceiling +
    ``STAIR_SHAFT_CAP_M``) place the void's shaft; ``walls`` decide which
    flight sides get a handrail. Returns ``{"flights": [...] (climbing
    order; per flight ``lines``, ``width``, ``going``, ``rise_dir``,
    ``nosings``, ``base_z``, ``top_z``), "risers", "riser_m",
    "riser_source", "rise_m", "landing", "void", "void_raw", "ceiling_z",
    "cap_z", "rails", "direction", "turn", "generic", "assumed", "warnings",
    "notes"}``. ``assumed`` entries are ``{"field", "kind", "value",
    "reason"}`` for the scene manifest."""
    fp = piece["footprint"]
    center = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    fw, fd = float(fp["size"][0]), float(fp["size"][1])
    local_y = G.rotate_point((0.0, 1.0), rot)
    data = stair_data(piece) or {}
    rise = float(rise)
    ceiling = float(ceiling_height) if ceiling_height is not None else rise - STAIR_SLAB_M
    cap = float(cap_height) if cap_height is not None else ceiling + STAIR_SHAFT_CAP_M
    assumed: list[dict] = []
    warnings: list[str] = []
    notes: list[str] = []

    flights = []
    raw = data.get("flights") or []
    for k, f in enumerate(raw):
        try:
            s = (float(f["start"][0]), float(f["start"][1]))
            e = (float(f["end"][0]), float(f["end"][1]))
            n, width = int(f["lines"]), float(f["width"])
        except (KeyError, TypeError, ValueError, IndexError):
            warnings.append(f"flight {k + 1}: start, end, width or lines missing; not built")
            continue
        length = G.distance(s, e)
        if n < 2 or length < 1e-6 or width <= 0:
            warnings.append(f"flight {k + 1}: {n} tread line(s) over {length:.3f} m, width {width:.3f} m: "
                            f"no direction to build; not built")
            continue
        flights.append({"index": k, "start": s, "end": e, "lines": n, "width": width,
                        "axis": _unit2(_v(s, e)), "going": length / (n - 1)})
    generic = not flights
    if generic:
        n = max(2, int(round(rise / STAIR_GENERIC_RISER_M)))
        s = _local_to_world2((0.0, -fd / 2.0), center, rot)
        e = _local_to_world2((0.0, fd / 2.0), center, rot)
        flights = [{"index": 0, "start": s, "end": e, "lines": n, "width": fw, "axis": local_y,
                    "going": fd / (n - 1)}]
        why = "no drawn flights" if not raw else "no buildable drawn flight"
        assumed.append({"field": "flights", "kind": "stair_flights",
                        "value": f"one straight flight of {n} risers along +local Y filling the footprint",
                        "reason": f"{why}: the riser count is assumed ({rise:.2f} m / {STAIR_GENERIC_RISER_M} m)"})
        warnings.append(f"{why}: one straight flight of {n} assumed risers fills the footprint")

    # Rise direction: the recorded one (assumed by the recognition rule unless drawn), else +local Y.
    a0 = flights[0]["axis"]
    rec = data.get("direction")
    d_vec = _unit2(rec) if isinstance(rec, (list, tuple)) and len(rec) >= 2 else None
    if d_vec is None:
        d_vec, d_src = local_y, "no direction recorded: steps rise along +local Y of the footprint"
    elif data.get("direction_assumed", True) is not False:
        d_src = str(data.get("reason") or "rise direction assumed by the recognition rule (no UP arrow drawn)")
    else:
        d_src = None                                       # drawn
    dot0 = _d2(a0, d_vec)
    if abs(dot0) < 0.5:
        if abs(_d2(a0, local_y)) >= 0.5:
            dot0 = _d2(a0, local_y)
            notes.append("the recorded direction does not run along the flights: +local Y used")
        else:
            dot0 = 1.0
            notes.append("neither the recorded direction nor +local Y runs along the flights: "
                         "first to last drawn line used")
        d_src = d_src or "recorded direction not along the flights"
    r0 = a0 if dot0 >= 0 else (-a0[0], -a0[1])
    rdirs = [r0]
    for f in flights[1:]:
        a, prev = f["axis"], rdirs[-1]
        if abs(_d2(a, prev)) >= 0.9:                        # side by side: a U-turn rises the other way
            rdirs.append(a if _d2(a, prev) < 0 else (-a[0], -a[1]))
        else:
            rdirs.append(a if _d2(a, d_vec) >= 0 else (-a[0], -a[1]))
            notes.append(f"flight {f['index'] + 1} is not parallel to flight 1: it rises along the recorded direction")
    if d_src is not None:
        assumed.append({"field": "direction", "kind": "stair_direction", "value": [round(r0[0], 4), round(r0[1], 4)],
                        "reason": d_src})
    turn = data.get("turn") or ("straight" if len(flights) == 1 else "U" if len(flights) == 2 else "other")
    if len(flights) >= 2 and data.get("turn_assumed", True) is not False:
        assumed.append({"field": "turn", "kind": "stair_turn", "value": turn,
                        "reason": "flights side by side read as a turning stair, climbed in turn; nothing drawn "
                                  "says which flight starts at the floor"})

    # Landing and climbing order: with a landing the flight rising towards it climbs first.
    land = data.get("landing")
    poly = land.get("polygon") if isinstance(land, dict) else land
    landing_poly = [(float(p[0]), float(p[1])) for p in poly] if isinstance(poly, (list, tuple)) and len(poly) >= 3 \
        else None
    order = list(range(len(flights)))
    if landing_poly is not None and len(flights) >= 2:
        c = G.polygon_centroid(landing_poly)
        mid0 = G.segment_midpoint(flights[0]["start"], flights[0]["end"])
        if _d2(_v(mid0, c), rdirs[0]) <= 0:
            order.reverse()
    elif landing_poly is None and len(flights) >= 2:
        notes.append("no landing drawn: the flights are climbed in the drawn order without a landing slab")

    # Risers: every drawn line is a nosing; riser = rise / all risers (or a documented riser).
    total = sum(f["lines"] for f in flights)
    documented = data.get("riser_m")
    doc_source = str(data.get("riser_source") or "")
    if isinstance(documented, (int, float)) and not isinstance(documented, bool) and documented > 0 \
            and not doc_source.startswith("derived"):
        riser, riser_source = float(documented), doc_source or "documented"
        if abs(riser * total - rise) > 0.02:
            warnings.append(f"documented riser {riser:.3f} m x {total} risers = {riser * total:.3f} m differs from "
                            f"the rise {rise:.3f} m")
    else:
        riser, riser_source = rise / total, rise_source
        assumed.append({"field": "riser_m", "kind": "stair_riser", "value": round(riser, 4),
                        "reason": f"{riser_source}: {rise:.3f} m / {total} drawn risers"
                                  + (" (assumed count)" if generic else "")})
    lo, hi = STAIR_RISER_RANGE
    if not lo - 1e-9 <= riser <= hi + 1e-9:
        warnings.append(f"riser {riser:.3f} m outside {lo:.2f}-{hi:.2f} m ({riser_source}, {total} risers)")

    z = 0.0
    planned = []
    for idx in order:
        f = dict(flights[idx])
        r = rdirs[idx]
        n, g, a = f["lines"], f["going"], f["axis"]
        first = f["start"] if _d2(a, r) > 0 else f["end"]
        f.update({"rise_dir": r, "base_z": z, "top_z": z + n * riser,
                  "nosings": [(first[0] + r[0] * g * i, first[1] + r[1] * g * i) for i in range(n)]})
        z = f["top_z"]
        planned.append(f)

    landing = None
    if landing_poly is not None:
        if len(planned) >= 2:
            role, z_l = "mid", planned[0]["top_z"]
        else:
            f = planned[0]
            towards = _d2(_v(G.segment_midpoint(f["start"], f["end"]), G.polygon_centroid(landing_poly)),
                          f["rise_dir"]) > 0
            role, z_l = ("top", f["top_z"]) if towards else ("floor", 0.0)
            if role == "floor":
                notes.append("the landing lies at the foot of the flight: it is the floor, no slab")
        landing = {"polygon": landing_poly, "z": z_l, "role": role, "thickness": STAIR_WAIST_M}

    # The ceiling opening: the last flight and the landing (in the frame of flight 1).
    void, void_raw = [], []
    if rise > ceiling + 1e-6:
        o = flights[0]["start"]
        u = a0
        vx, vy = -u[1], u[0]

        def to_f(p):
            q = _v(o, p)
            return (q[0] * vx + q[1] * vy, _d2(q, u))

        def from_f(q):
            return (o[0] + vx * q[0] + u[0] * q[1], o[1] + vy * q[0] + u[1] * q[1])

        last = planned[-1]
        hw = last["width"] / 2.0
        lp = (-last["axis"][1], last["axis"][0])
        corners = [(p[0] + lp[0] * s * hw, p[1] + lp[1] * s * hw) for p in (last["start"], last["end"]) for s in (-1, 1)]
        rects = [_frame_box([to_f(c) for c in corners])]
        if landing is not None and landing["role"] in ("mid", "top"):
            rects.append(_frame_box([to_f(p) for p in landing_poly]))
        g = STAIR_SHAFT_GAP
        void_raw = [[from_f(p) for p in loop] for loop in geom2d.rect_union_outline(rects)]
        void = [[from_f(p) for p in loop]
                for loop in geom2d.rect_union_outline([(b[0] - g, b[1] - g, b[2] + g, b[3] + g) for b in rects])]
        what = "the last flight" + (" and the landing" if len(rects) > 1 else "")
        reason = "nothing drawn above the stair; the opening is assumed" if data.get("void_assumed", True) \
            is not False else "drawn"
        assumed.append({"field": "void", "kind": "stair_void",
                        "value": f"ceiling opening over {what}, closed by a neutral shaft cap "
                                 f"{cap - ceiling:.2f} m above the ceiling",
                        "reason": f"{reason}; the floor above is not modelled, so the cap hides the shaft"})
        for f in planned[:-1]:
            headroom = ceiling - f["top_z"]
            if headroom < STAIR_HEADROOM_M:
                warnings.append(f"flight {f['index'] + 1}: {headroom:.2f} m under the ceiling at its top "
                                f"(the opening covers {what} only, assumed)")

    # Handrails: every flight side that is not against a wall.
    wall_rects = [G.centerline_to_rectangle(w["start"], w["end"], float(w["thickness"])) for w in walls
                  if G.distance(w["start"], w["end"]) > 1e-9]
    rails = []
    for f in planned:
        r = f["rise_dir"]
        p = (-r[1], r[0])
        hw = f["width"] / 2.0
        a_, b_ = f["nosings"][0], f["nosings"][-1]
        for side, sgn in (("left", 1.0), ("right", -1.0)):
            reach = sgn * (hw + STAIR_WALL_PROBE)
            probes = [(a_[0] + (b_[0] - a_[0]) * t + p[0] * reach, a_[1] + (b_[1] - a_[1]) * t + p[1] * reach)
                      for t in (0.25, 0.5, 0.75)]
            if sum(1 for q in probes if any(G.point_in_polygon(q, rect) for rect in wall_rects)) >= 2:
                continue
            rails.append({"flight": f["index"], "side": side, "offset": sgn * (hw - STAIR_RAIL_INSET)})
    if rails:
        assumed.append({"field": "handrail", "kind": "stair_handrail",
                        "value": f"{len(rails)} steel rail(s) {STAIR_RAIL_HEIGHT:.2f} m above the nosings",
                        "reason": "design detail on every flight side not against a wall; not in the documents"})
    assumed.append({"field": "waist", "kind": "stair_structure",
                    "value": f"{STAIR_WAIST_M:.2f} m waist slab under the steps and landing slab",
                    "reason": "the documents show the stair in plan only"})
    # A cap lowered under the floor of a level above: the last riser (and a top landing) stop just under it.
    top_limit = cap - STAIR_CAP_CLEARANCE / 3.0 if rise > cap - STAIR_CAP_CLEARANCE / 3.0 else None
    if top_limit is not None:
        notes.append(f"the last riser stops at {top_limit:.3f} m, under the shaft cap ({cap:.3f} m)")
    return {"flights": planned, "risers": total, "riser_m": riser, "riser_source": riser_source, "rise_m": rise,
            "landing": landing, "void": void, "void_raw": void_raw, "ceiling_z": ceiling, "cap_z": cap,
            "top_limit": top_limit, "rails": rails, "direction": [round(r0[0], 4), round(r0[1], 4)], "turn": turn,
            "generic": generic, "assumed": assumed, "warnings": warnings, "notes": notes}


def _frame_box(points) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _part(mesh: tuple, key: str, role: str, **extra) -> Part:
    verts, faces = mesh
    return dict({"verts": verts, "faces": faces, "key": key, "role": role}, **extra)


def stair_parts(plan: dict) -> list[Part]:
    """The parts of a planned stair (world XY, z above the level floor):
    per flight ``n - 1`` step prisms (tread between two drawn nosings, on a
    ``STAIR_WAIST_M`` waist slab, never below the floor) and the riser plate
    of the last riser; the landing slab (``mid`` / ``top`` landings); the
    rails and their two posts, cut ``STAIR_CAP_CLEARANCE`` below the cap.
    Steps, plates and the landing carry ``rise_dir`` for ``stair_face_slots``."""
    riser = float(plan["riser_m"])
    limit = plan.get("top_limit")
    parts: list[Part] = []
    rails = {}
    for rail in plan["rails"]:
        rails.setdefault(rail["flight"], []).append(rail)
    for f in plan["flights"]:
        n, g, width, base = f["lines"], f["going"], f["width"], f["base_z"]
        r, origin = f["rise_dir"], f["nosings"][0]
        k = riser / g
        t_v = STAIR_WAIST_M * math.sqrt(1.0 + k * k)            # waist measured square to the soffit
        extra = {"flight": f["index"], "rise_dir": [r[0], r[1]]}
        for i in range(1, n):
            s0, s1 = (i - 1) * g, i * g
            top = base + i * riser
            z0, z1 = base + s0 * k - t_v, base + s1 * k - t_v       # soffit under the root line
            if z0 < 0.0 < z1:
                sc = (t_v - base) / k
                profile = [(s0, 0.0), (sc, 0.0), (s1, z1), (s1, top), (s0, top)]
            else:
                profile = [(s0, max(0.0, z0)), (s1, max(0.0, z1)), (s1, top), (s0, top)]
            parts.append(_part(geom2d.extrude_profile(profile, origin, r, width), "worktop", "step", **extra))
        sn = (n - 1) * g
        z_lo = base + (n - 1) * riser
        z_hi = base + n * riser if limit is None else min(base + n * riser, limit)
        if z_hi - z_lo > 1e-4:
            parts.append(_part(geom2d.extrude_profile(
                [(sn - STAIR_RISER_PLATE, z_lo), (sn, z_lo), (sn, z_hi), (sn - STAIR_RISER_PLATE, z_hi)],
                origin, r, width), "worktop", "riser", **extra))
        for rail in rails.get(f["index"], []):
            parts.extend(_rail_parts(f, rail["offset"], riser, plan["cap_z"] - STAIR_CAP_CLEARANCE))
    landing = plan.get("landing")
    if landing is not None and landing["role"] in ("mid", "top"):
        z_top = landing["z"] if limit is None else min(landing["z"], limit)
        parts.append(_part(geom2d.prism(landing["polygon"], z_top - landing["thickness"], z_top),
                           "worktop", "landing", flight=None, rise_dir=None))
    return parts


def _rail_parts(f: dict, offset: float, riser: float, limit: float) -> list[Part]:
    """A sloped rail bar ``STAIR_RAIL_HEIGHT`` above the nosing line of a
    flight, ``offset`` metres left of its centre line, and a post at each end
    standing on its tread; cut where its top would pass ``limit``."""
    n, g, base = f["lines"], f["going"], f["base_z"]
    r, o = f["rise_dir"], f["nosings"][0]
    p = (-r[1], r[0])
    k = riser / g

    def rail_top(s):
        return base + riser + s * k + STAIR_RAIL_HEIGHT

    s_a, s_b = 0.05, (n - 1) * g - 0.05
    if rail_top(s_b) > limit:
        s_b = (limit - STAIR_RAIL_HEIGHT - base - riser) / k
    if s_b - s_a < STAIR_RAIL_MIN_M:
        return []

    def at(s, q, z):
        return (o[0] + r[0] * s + p[0] * q, o[1] + r[1] * s + p[1] * q, z)

    verts = [at(s, offset + dq, rail_top(s) + dz) for s in (s_a, s_b) for dq in (-STAIR_RAIL_W / 2.0, STAIR_RAIL_W / 2.0)
             for dz in (-STAIR_RAIL_T, 0.0)]
    # index = 4 * s + 2 * q + z
    faces = [[0, 2, 6, 4], [1, 5, 7, 3], [0, 4, 5, 1], [2, 3, 7, 6], [0, 1, 3, 2], [4, 6, 7, 5]]
    parts = [_part(geom2d.convex_solid(verts, faces), "steel", "rail", flight=f["index"])]
    for s in (s_a + STAIR_POST / 2.0, s_b - STAIR_POST / 2.0):
        tread = base + (min(n - 1, int(s / g)) + 1) * riser
        cx, cy, _ = at(s, offset, 0.0)
        z_top = rail_top(s) - STAIR_RAIL_T
        if z_top - tread > 0.02:
            parts.append(_part(geom2d.box((cx, cy, (tread + z_top) / 2.0), (STAIR_POST, STAIR_POST, z_top - tread),
                                          math.degrees(math.atan2(r[1], r[0]))), "steel", "post", flight=f["index"]))
    return parts


# Material slots of a built stair (shell.build_stairs): treads and risers, structure, steel.
STAIR_SLOTS = ("tread", "structure", "steel")


def stair_face_slots(parts: Sequence[Part]) -> list[int]:
    """Slot per face of ``stair_parts`` (``STAIR_SLOTS``): the top and the
    climbing-side face of steps, riser plates and the landing are ``tread``
    (the floor finish), their other faces ``structure`` (soffit, sides), rails
    and posts ``steel``."""
    slots = []
    for part in parts:
        if part["key"] == "steel":
            slots.extend([2] * len(part["faces"]))
            continue
        r = part.get("rise_dir")
        for f in part["faces"]:
            nx, ny, nz = geom2d.face_normal(part["verts"], f)
            front = r is not None and -(nx * r[0] + ny * r[1]) > 0.5
            slots.append(0 if nz > 0.5 or front else 1)
    return slots


def void_shaft(plan: dict) -> tuple[list, list]:
    """``(verts, faces)`` closing the ceiling opening (z above the level
    floor): one inward-facing quad per edge of every void loop, from
    ``STAIR_SHAFT_LIP`` below the ceiling up to the cap, and the cap faces
    (facing down). Empty when the stair needs no opening."""
    parts = []
    z0, z1 = plan["ceiling_z"] - STAIR_SHAFT_LIP, plan["cap_z"]
    for loop in plan["void"]:
        pts = list(loop)
        if G.polygon_signed_area(pts) < 0:
            pts = pts[::-1]
        n = len(pts)
        verts, faces = [], []
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            j = len(verts)
            verts += [(ax, ay, z0), (ax, ay, z1), (bx, by, z1), (bx, by, z0)]   # normal to the left: inwards
            faces.append([j, j + 1, j + 2, j + 3])
        parts.append((verts, faces))
        parts.append(geom2d.polygon_faces(pts, [], z1, facing_up=False))
    return geom2d.merge(parts)


def _stair(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Stair parts in the piece's local frame (``build_parts``): the drawn
    flights of ``piece`` (or one assumed flight filling ``w x d``) with ``h``
    as the rise; no walls, so every side gets a rail."""
    fp = dict((piece or {}).get("footprint") or {"center": [0.0, 0.0], "rotation_deg": 0.0})
    fp["size"] = [w, d]
    center = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    plan = stair_plan(dict(piece or {}, footprint=fp), h)
    out = []
    for part in stair_parts(plan):
        verts = [(*G.rotate_point((x - center[0], y - center[1]), -rot), z) for x, y, z in part["verts"]]
        rd = part.get("rise_dir")
        local = dict(part, verts=verts)
        if rd is not None:
            local["rise_dir"] = list(G.rotate_point((rd[0], rd[1]), -rot))
        out.append(local)
    return out


# --------------------------------------------------------------------------
# Milestone 10 (docs/milestone10.md §4.4-§4.7): cabinets with fronts, the new furniture types, doors, windows
# --------------------------------------------------------------------------

# Cabinet looks (``furniture.design``, docs/milestone10.md §1.1, §4.4). The builders read the design of the piece
# they get (``build_parts(..., piece=)``); ``furniture.py`` fills a missing design from ``style.json`` first
# (``wenart.blender.looks.design_for``), so a design here is complete or empty (defaults below, recorded there).
FRONT_STYLES: tuple[str, ...] = ("flat", "shaker", "slatted", "glass")
DEFAULT_FRONT_STYLE = "flat"
SHAKER_FRAME_M = 0.065           # shaker stiles and rails (at most 18 % of the front's side)
SHAKER_PANEL_M = 0.012           # the recessed panel; the frame stands FRONT_THICKNESS
SLAT_W_M = 0.03                  # slatted fronts: slat width and gap on a dark backing
SLAT_GAP_M = 0.012
SLAT_BACKING_M = 0.008
GLASS_FRAME_M = 0.05             # glass fronts: the frame around the pane
GLASS_PANE_M = 0.006
HANDLE_BAR = (0.012, 0.16)       # bar handle cross-section and length (doors vertical, drawers horizontal)
CABINET_DOOR_W = 0.6             # one door per this much width (at least one)
WALL_CABINET_PLINTH_M = 0.0
LEG_M = 0.035
# Glass and stone tops for tables with design.material_tags (§4.10: "glass coffee table": the parametric glass top).
TOP_TAG_KEYS: dict[str, str] = {"glass": "glass", "marble": "marble"}
TABLE_TYPES_WITH_TOP_TAGS: tuple[str, ...] = ("table_coffee", "table_dining", "side_table", "console_table", "desk")


def piece_design(piece: dict | None) -> dict:
    """The piece's ``design`` dict ({} when there is none)."""
    design = (piece or {}).get("design")
    return design if isinstance(design, dict) else {}


def front_style_of(design: dict, default: str = DEFAULT_FRONT_STYLE) -> str:
    style = design.get("front_style")
    return style if style in FRONT_STYLES else default


def _front_panel(cx: float, y_face: float, z0: float, fw: float, fh: float, style: str) -> list[Part]:
    """One cabinet front (door or drawer) of ``fw x fh`` standing in front of the carcass face at ``y_face``
    (towards -Y), its bottom at ``z0``: flat slab, shaker frame on a recessed panel, vertical slats on a dark
    backing, or a glass pane in a frame. Every part has role ``front``."""
    y0 = y_face - FRONT_GAP                        # back of the front
    t = FRONT_THICKNESS
    if style == "shaker":
        f = min(SHAKER_FRAME_M, fw * 0.18, fh * 0.18)
        parts = [_box(cx, y0 - SHAKER_PANEL_M / 2.0, z0, fw, SHAKER_PANEL_M, fh, "front", "front")]
        yc = y0 - t / 2.0
        parts += [_box(cx - fw / 2.0 + f / 2.0, yc, z0, f, t, fh, "front", "front"),
                  _box(cx + fw / 2.0 - f / 2.0, yc, z0, f, t, fh, "front", "front"),
                  _box(cx, yc, z0, fw - 2 * f, t, f, "front", "front"),
                  _box(cx, yc, z0 + fh - f, fw - 2 * f, t, f, "front", "front")]
        return parts
    if style == "slatted":
        parts = [_box(cx, y0 - SLAT_BACKING_M / 2.0, z0, fw, SLAT_BACKING_M, fh, "dark", "front")]
        n = max(1, int((fw + SLAT_GAP_M) // (SLAT_W_M + SLAT_GAP_M)))
        sw = (fw - (n - 1) * SLAT_GAP_M) / n
        st = t - SLAT_BACKING_M
        for i in range(n):
            x = cx - fw / 2.0 + sw / 2.0 + i * (sw + SLAT_GAP_M)
            parts.append(_box(x, y0 - SLAT_BACKING_M - st / 2.0, z0, sw, st, fh, "front", "front"))
        return parts
    if style == "glass":
        f = min(GLASS_FRAME_M, fw * 0.2, fh * 0.2)
        yc = y0 - t / 2.0
        return [_box(cx - fw / 2.0 + f / 2.0, yc, z0, f, t, fh, "front", "front"),
                _box(cx + fw / 2.0 - f / 2.0, yc, z0, f, t, fh, "front", "front"),
                _box(cx, yc, z0, fw - 2 * f, t, f, "front", "front"),
                _box(cx, yc, z0 + fh - f, fw - 2 * f, t, f, "front", "front"),
                _box(cx, yc, z0 + f, fw - 2 * f, GLASS_PANE_M, fh - 2 * f, "glass", "front")]
    return [_box(cx, y0 - t / 2.0, z0, fw, t, fh, "front", "front")]


def _handle(cx: float, y_face: float, zc: float, vertical: bool) -> Part:
    """A bar handle on a front whose face is at ``y_face - FRONT_GAP - FRONT_THICKNESS`` (centre ``zc``)."""
    y = y_face - FRONT_GAP - FRONT_THICKNESS - PROUD / 2.0
    t, length = HANDLE_BAR
    if vertical:
        return _box(cx, y, zc - length / 2.0, t, PROUD, length, "handle", "handle")
    return _box(cx, y, zc - t / 2.0, length, PROUD, t, "handle", "handle")


def cabinet_fronts(w: float, y_face: float, z0: float, z1: float, rows: int, cols: int, design: dict,
                   doors: bool = True, handle_at: str = "top") -> list[Part]:
    """The fronts (and handles) of a cabinet face from ``z0`` to ``z1`` in ``rows`` x ``cols`` with 3 mm gaps, in
    the design's front style; door handles stand vertically near the meeting edges (``handle_at`` ``top``: in the
    upper part of the door, a base cabinet; ``bottom``: a wall cabinet), drawer handles horizontally centred."""
    style = front_style_of(design)
    gap = 0.003
    rh = (z1 - z0) / rows
    cw = w / cols
    parts: list[Part] = []
    for r in range(rows):
        for c in range(cols):
            cx = -w / 2.0 + cw * (c + 0.5)
            fz0 = z0 + rh * r + gap / 2.0
            fw, fh = cw - gap, rh - gap
            parts += _front_panel(cx, y_face, fz0, fw, fh, style)
            if doors:
                side = 1.0 if c % 2 == 0 else -1.0          # pairs of doors: handles at the meeting edges
                if cols == 1:
                    side = 1.0
                hx = cx + side * (fw / 2.0 - 0.04)
                hz = fz0 + fh - 0.1 - HANDLE_BAR[1] / 2.0 if handle_at == "top" else fz0 + 0.1 + HANDLE_BAR[1] / 2.0
                hz = min(max(hz, fz0 + HANDLE_BAR[1] / 2.0 + 0.01), fz0 + fh - HANDLE_BAR[1] / 2.0 - 0.01)
                parts.append(_handle(hx, y_face, hz, vertical=fh >= HANDLE_BAR[1] + 0.04))
            else:
                parts.append(_handle(cx, y_face, fz0 + fh / 2.0, vertical=False))
    return parts


def _carcass(w: float, d: float, z0: float, h: float, key: str = "wood") -> tuple[Part, float]:
    """The carcass box (its front face FRONT_GAP + FRONT_THICKNESS behind the footprint's front edge) and that
    face's y."""
    inset = FRONT_GAP + FRONT_THICKNESS
    return _box(0.0, inset / 2.0, z0, w, d - inset, h, key, "body"), -d / 2.0 + inset


def _cols(w: float) -> int:
    return max(1, round(w / CABINET_DOOR_W))


def _sideboard(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Sideboard: wooden legs, a carcass, a row of doors (the design's fronts) and a top."""
    design = piece_design(piece)
    legs = min(0.15, h * 0.2)
    top_t = 0.025
    body, face = _carcass(w, d, legs, h - legs - top_t)
    parts = [body, _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.04 - LEG_M / 2.0), sy * (d / 2.0 - 0.04 - LEG_M / 2.0), 0.0, LEG_M,
                              LEG_M, legs, "wood", "leg"))
    parts += cabinet_fronts(w, face, legs + 0.005, h - top_t - 0.005, 1, max(2, _cols(w)), design)
    return parts


def _shoe_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Shoe cabinet: plinth, carcass and two or three tilt-out flaps over the whole width (horizontal handles)."""
    design = piece_design(piece)
    plinth = min(0.06, h * 0.08)
    body, face = _carcass(w, d, plinth, h - plinth)
    rows = 3 if h >= 0.9 else 2
    return ([_box(0.0, 0.02, 0.0, w - 0.04, d - 0.06, plinth, "dark", "plinth"), body]
            + cabinet_fronts(w, face, plinth + 0.003, h - 0.003, rows, 1, design, doors=False))


def _display_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Display cabinet: plinth, carcass, shelves seen through the fronts (glass unless the design says another
    front style), two doors."""
    design = dict(piece_design(piece))
    design.setdefault("front_style", "glass")
    if design.get("front_style") is None:
        design["front_style"] = "glass"
    plinth = min(0.08, h * 0.05)
    inset = FRONT_GAP + FRONT_THICKNESS
    t = 0.018
    face = -d / 2.0 + inset
    parts = [_box(0.0, 0.0, 0.0, w - 0.04, d - 0.06, plinth, "dark", "plinth"),
             _box(-(w / 2.0 - t / 2.0), inset / 2.0, plinth, t, d - inset, h - plinth, "wood", "side"),
             _box(w / 2.0 - t / 2.0, inset / 2.0, plinth, t, d - inset, h - plinth, "wood", "side"),
             _box(0.0, d / 2.0 - t / 2.0, plinth, w - 2 * t, t, h - plinth, "wood", "back"),
             _box(0.0, inset / 2.0, plinth, w - 2 * t, d - inset - t, t, "wood", "bottom"),
             _box(0.0, inset / 2.0, h - t, w - 2 * t, d - inset - t, t, "wood", "top")]
    z = plinth + SHELF_PITCH
    while z < h - t - 0.2:
        parts.append(_box(0.0, inset / 2.0 - t / 2.0, z, w - 2 * t, d - inset - 2 * t, 0.012, "glass", "shelf"))
        z += SHELF_PITCH
    parts += cabinet_fronts(w, face, plinth + 0.003, h - 0.003, 1, 2 if w >= 0.7 else 1, design)
    return parts


def _tall_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Tall (pantry) cabinet: plinth, carcass, a lower door of two thirds and an upper one per column."""
    design = piece_design(piece)
    plinth = min(0.1, h * 0.05)
    body, face = _carcass(w, d, plinth, h - plinth, "painted")
    parts = [_box(0.0, 0.03, 0.0, w, d - 0.06, plinth, "dark", "plinth"), body]
    split = plinth + (h - plinth) * 2.0 / 3.0
    cols = max(1, round(w / 0.45))
    parts += cabinet_fronts(w, face, plinth + 0.003, split, 1, cols, design)
    parts += cabinet_fronts(w, face, split, h - 0.003, 1, cols, design, handle_at="bottom")
    return parts


def _wall_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Wall cabinet (its bottom at z = 0 of its own frame; ``furniture.py`` hangs it at ``mount_bottom_m``):
    carcass and a row of doors with their handles low."""
    design = piece_design(piece)
    body, face = _carcass(w, d, 0.0, h, "painted")
    return [body] + cabinet_fronts(w, face, 0.003, h - 0.003, 1, _cols(w), design, handle_at="bottom")


def _counter_m10(w: float, d: float, h: float, island: bool = False, piece: dict | None = None) -> list[Part]:
    """Kitchen counter run or island (Milestone 6 boxes): plinth, carcass, worktop, and the design's fronts and
    handles over the base (one door per 0.6 m; handles in the upper part)."""
    design = piece_design(piece)
    top_t = 0.04
    plinth_h = min(0.1, h * 0.12)
    inset = 0.03
    if island:
        carcass = _box(0.0, 0.0, plinth_h, w - 2 * inset, d - 2 * inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, 0.0, 0.0, w - 4 * inset, d - 4 * inset, plinth_h, "dark", "plinth")
    else:
        carcass = _box(0.0, inset / 2.0, plinth_h, w, d - inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, inset, 0.0, w, d - 2 * inset, plinth_h, "dark", "plinth")
    front_y = -d / 2.0 + inset
    parts = [plinth, carcass, _box(0.0, 0.0, h - top_t, w, d, top_t, "worktop", "top")]
    parts += cabinet_fronts(w, front_y, plinth_h + 0.01, h - top_t - 0.02, 1, _cols(w), design)
    return parts


def _vanity(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """A washbasin with the vanity look (docs/milestone10.md §4.4: a drawn washbasin at least 0.45 m deep; its
    type stays ``washbasin``): a wall-hung cabinet with the design's fronts under a ceramic top with an inset
    basin and a tap."""
    design = piece_design(piece)
    top_t = 0.03
    basin_h = min(0.15, h * 0.2)
    bottom = min(0.3, h * 0.35)                     # wall-hung: free floor under the cabinet
    body, face = _carcass(w, d, bottom, h - top_t - bottom)
    parts = [body, _box(0.0, d / 2.0 - 0.01, 0.0, w * 0.3, 0.02, bottom, "dark", "back")]   # the wall bracket
    bw, bd = min(w - 0.12, 0.5), min(d - 0.12, 0.36)
    sx, sy = (w - bw) / 2.0, (d - bd) / 2.0
    z_top = h - top_t
    parts += [_box(0.0, -d / 2.0 + sy / 2.0, z_top, w, sy, top_t, "ceramic", "top"),
              _box(0.0, d / 2.0 - sy / 2.0, z_top, w, sy, top_t, "ceramic", "top"),
              _box(-w / 2.0 + sx / 2.0, 0.0, z_top, sx, bd, top_t, "ceramic", "top"),
              _box(w / 2.0 - sx / 2.0, 0.0, z_top, sx, bd, top_t, "ceramic", "top")]
    parts += _basin(0.0, 0.0, h - basin_h, bw, bd, basin_h, 0.012, "ceramic")
    parts.append(_cylinder_z(0.0, d / 2.0 - sy / 2.0, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    parts += cabinet_fronts(w, face, bottom + 0.003, z_top - 0.003, 1, 1 if w < 0.8 else 2, design, doors=w >= 0.8)
    return parts


def _washbasin_m10(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 4 pedestal basin, or the vanity look when the design says ``vanity``."""
    if piece_design(piece).get("vanity"):
        return _vanity(w, d, h, piece)
    return _washbasin(w, d, h)


def _built_in_wardrobe(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """A built-in wardrobe (docs/milestone10.md §4.4: a drawn wardrobe spanning wall to wall; its type stays
    ``wardrobe``): fronts over the whole width (no carcass sides showing), a recessed plinth and a filler
    panel at the top."""
    design = piece_design(piece)
    plinth = 0.08
    filler = 0.06
    body, face = _carcass(w, d, plinth, h - plinth)
    parts = [_box(0.0, 0.04, 0.0, w, d - 0.08, plinth, "dark", "plinth"), body,
             _box(0.0, face - FRONT_GAP - FRONT_THICKNESS / 2.0, h - filler, w, FRONT_THICKNESS, filler, "front",
                  "front")]
    parts += cabinet_fronts(w, face, plinth + 0.003, h - filler - 0.003, 1, max(2, round(w / 0.5)), design)
    return parts


def _wardrobe_m10(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 4 wardrobe, built-in when the design says ``built_in``, with the design's fronts when it
    names a front style."""
    design = piece_design(piece)
    if design.get("built_in"):
        return _built_in_wardrobe(w, d, h, piece)
    if design.get("front_style") in FRONT_STYLES:
        body, face = _carcass(w, d, 0.0, h)
        return [body] + cabinet_fronts(w, face, 0.05, h - 0.05, 1, max(2, round(w / 0.5)), design)
    return _wardrobe(w, d, h)


def _table_m10(w: float, d: float, h: float, piece: dict | None = None, desk: bool = False) -> list[Part]:
    """The Milestone 4 table; a ``glass`` or ``marble`` material tag of the design (§4.10: "glass coffee table")
    gives that top, ``metal`` steel legs."""
    parts = _table(w, d, h, desk=desk)
    tags = piece_design(piece).get("material_tags") or ()
    top_key = next((TOP_TAG_KEYS[t] for t in tags if t in TOP_TAG_KEYS), None)
    for p in parts:
        if p["role"] == "top" and top_key:
            p["key"] = top_key
        if p["role"] == "leg" and "metal" in tags:
            p["key"] = "steel"
    if top_key == "glass" and not desk:             # a glass top shows its frame: a lower wooden shelf
        leg = min(0.06, w * 0.08, d * 0.08)
        inset = min(0.04, w * 0.05, d * 0.05)
        sw, sd = w - 2 * (inset + leg), d - 2 * (inset + leg)
        if sw > 0.1 and sd > 0.1:
            parts.append(_box(0.0, 0.0, min(0.12, h * 0.25), sw, sd, 0.02, "wood", "shelf"))
    return parts


def _console_table(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Console table: a narrow top, four slim legs and a lower shelf (tags as ``_table_m10``)."""
    parts = _table_m10(w, d, h, piece)
    leg = min(0.06, w * 0.08, d * 0.08)
    inset = min(0.04, w * 0.05, d * 0.05)
    sw, sd = w - 2 * (inset + leg), d - 2 * (inset + leg)
    if sw > 0.1 and sd > 0.05 and not any(p["role"] == "shelf" for p in parts):
        parts.append(_box(0.0, 0.0, min(0.15, h * 0.2), sw, sd, 0.02, "wood", "shelf"))
    return parts


# Corner sofa: the two rectangles of wenart.furniture.schemas.l_parts (the one geometry source, docs/milestone10.md
# §1.6b row 15). That module needs jsonschema, which Blender's Python lacks, and the build's fingerprint covers only
# the scene code, so the builder keeps this copy of the formula; tests/test_blender_furniture.py checks that both
# give the same rectangles (schemas.L_SEAT_DEPTH_M / L_CHAISE_WIDTH_M equal these defaults).
L_SEAT_DEPTH_M = 0.9
L_CHAISE_WIDTH_M = 0.9


def l_parts(size, chaise_side, chaise_depth, seat_depth=None, chaise_width=None):
    """``[(x0, x1, y0, y1) main seat, (x0, x1, y0, y1) chaise]`` of a corner sofa in its frame
    (``wenart.furniture.schemas.l_parts``): the main seat along the back (+Y) over the whole width, ``seat_depth``
    deep, the chaise ``chaise_width`` wide on ``chaise_side`` (right = +X) over ``chaise_depth`` from the back."""
    w, d = float(size[0]), float(size[1])
    depth = min(float(chaise_depth), d) if chaise_depth else d
    seat = min(float(seat_depth) if seat_depth else L_SEAT_DEPTH_M, depth)
    cw = min(float(chaise_width) if chaise_width else L_CHAISE_WIDTH_M, w / 2.0)
    main = (-w / 2.0, w / 2.0, d / 2.0 - seat, d / 2.0)
    if chaise_side == "left":
        chaise = (-w / 2.0, -w / 2.0 + cw, d / 2.0 - depth, d / 2.0)
    else:
        chaise = (w / 2.0 - cw, w / 2.0, d / 2.0 - depth, d / 2.0)
    return [main, chaise]


def _sofa_corner(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Corner sofa (``shape: L``): the main seat along the back over the whole width and the long seat (chaise) on
    ``chaise_side`` from ``l_parts`` (default right, the schema's default sizes); a back along +Y, an arm at the
    end away from the chaise, seat cushions on both parts."""
    piece = piece or {}
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    main, chaise = l_parts((w, d), side, piece.get("chaise_depth"), piece.get("seat_depth"),
                           piece.get("chaise_width"))
    back_t = min(0.2, (main[3] - main[2]) * 0.25)
    arm_w = min(0.15, w * 0.06)
    seat_h = sofa_seat_height(h)
    arm_h = min(0.65, h * 0.8)
    mx0, mx1, my0, my1 = main
    cx0, cx1, cy0, cy1 = chaise
    seat_y0, seat_y1 = my0, my1 - back_t
    parts = [_box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, "fabric", "back")]
    # The arm on the side away from the chaise; the main seat base between the arm and the chaise.
    if side == "right":
        arm_x = mx0 + arm_w / 2.0
        base_x0, base_x1 = mx0 + arm_w, cx0
    else:
        arm_x = mx1 - arm_w / 2.0
        base_x0, base_x1 = cx1, mx1 - arm_w
    parts.append(_box(arm_x, (seat_y0 + seat_y1) / 2.0, 0.0, arm_w, seat_y1 - seat_y0, arm_h, "fabric", "arm"))
    parts.append(_box((base_x0 + base_x1) / 2.0, (seat_y0 + seat_y1) / 2.0, 0.0, base_x1 - base_x0,
                      seat_y1 - seat_y0, seat_h - 0.1, "fabric", "body"))
    ch_y1 = my1 - back_t
    parts.append(_box((cx0 + cx1) / 2.0, (cy0 + ch_y1) / 2.0, 0.0, cx1 - cx0, ch_y1 - cy0, seat_h - 0.1, "fabric",
                      "body"))
    seat_w = base_x1 - base_x0
    n = max(1, round(seat_w / 0.75))
    cw = seat_w / n
    for i in range(n):
        parts.append(_box(base_x0 + cw * (i + 0.5), (seat_y0 + seat_y1) / 2.0, seat_h - 0.1, cw - 0.03,
                          seat_y1 - seat_y0 - 0.04, 0.1, "fabric", "cushion"))
    parts.append(_box((cx0 + cx1) / 2.0, (cy0 + ch_y1) / 2.0, seat_h - 0.1, cx1 - cx0 - 0.03, ch_y1 - cy0 - 0.04,
                      0.1, "fabric", "cushion"))
    return parts


def sofa_corner_parts_info(piece: dict) -> dict:
    """The corner sofa's record for the manifest: the side and both rectangles (piece frame)."""
    fp = piece["footprint"]
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    rects = l_parts(fp["size"], side, piece.get("chaise_depth"), piece.get("seat_depth"), piece.get("chaise_width"))
    return {"chaise_side": side, "chaise_side_assumed": piece.get("chaise_side") not in ("left", "right"),
            "rectangles": [[round(v, 4) for v in r] for r in rects]}


def _chaise(w: float, d: float, h: float) -> list[Part]:
    """Chaise longue: a seat along the depth, a raised back at the head end (+Y), one arm and a long cushion."""
    back_t = min(0.15, d * 0.1)
    seat_h = sofa_seat_height(h)
    arm_w = min(0.12, w * 0.15)
    seat_d = d - back_t
    return [_box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, "fabric", "back"),
            _box(-(w / 2.0 - arm_w / 2.0), -back_t / 2.0 + seat_d * 0.2, 0.0, arm_w, seat_d * 0.6, seat_h + 0.12,
                 "fabric", "arm"),
            _box(arm_w / 2.0, -back_t / 2.0, 0.0, w - arm_w, seat_d, seat_h - 0.1, "fabric", "body"),
            _box(arm_w / 2.0, -back_t / 2.0, seat_h - 0.1, w - arm_w - 0.03, seat_d - 0.04, 0.1, "fabric", "cushion")]


def _ottoman(w: float, d: float, h: float) -> list[Part]:
    """Upholstered ottoman on four short legs."""
    legs = min(0.08, h * 0.2)
    parts = [_box(0.0, 0.0, legs, w, d, h - legs - 0.06, "fabric", "body"),
             _box(0.0, 0.0, h - 0.06, w - 0.02, d - 0.02, 0.06, "fabric", "cushion")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.05), sy * (d / 2.0 - 0.05), 0.0, LEG_M, LEG_M, legs, "wood", "leg"))
    return parts


def _bench(w: float, d: float, h: float) -> list[Part]:
    """Bench: a padded seat on a wooden frame with four legs."""
    pad = min(0.06, h * 0.15)
    frame_t = 0.03
    leg = min(0.045, d * 0.15)
    parts = [_box(0.0, 0.0, h - pad - frame_t, w, d, frame_t, "wood", "top"),
             _box(0.0, 0.0, h - pad, w - 0.01, d - 0.01, pad, "fabric", "cushion")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.04 - leg / 2.0), sy * (d / 2.0 - 0.03 - leg / 2.0), 0.0, leg, leg,
                              h - pad - frame_t, "wood", "leg"))
    return parts


def _bar_stool(w: float, d: float, h: float) -> list[Part]:
    """Bar stool: a round seat, four legs inside the seat's footprint and footrest bars."""
    seat_t = 0.05
    leg = 0.025
    r = min(w, d) / 2.0
    off = r * 0.62
    parts = [_cylinder_z(0.0, 0.0, h - seat_t, w / 2.0, d / 2.0, seat_t, "fabric", "top", n=32)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * off / math.sqrt(2.0), sy * off / math.sqrt(2.0), 0.0, leg, leg, h - seat_t,
                              "steel", "leg"))
    span = 2.0 * off / math.sqrt(2.0)
    rest = min(0.3, h * 0.4)
    for sy in (-1, 1):
        parts.append(_box(0.0, sy * off / math.sqrt(2.0), rest, span, 0.015, 0.015, "steel", "rest"))
    return parts


def _office_chair(w: float, d: float, h: float) -> list[Part]:
    """Office chair: a five-star base with castors, a gas lift, a seat, a back at +Y and two armrests; the seat
    fills the footprint (the star stays inside it)."""
    seat_h = min(0.48, h * 0.5)
    seat_t = 0.08
    r = min(w, d) / 2.0 - 0.02
    parts = []
    for k in range(5):
        a = math.radians(90.0 + 72.0 * k)
        mid = (math.cos(a) * r / 2.0, math.sin(a) * r / 2.0)
        verts, faces = geom2d.box((mid[0], mid[1], 0.06), (r, 0.04, 0.03), math.degrees(a))
        parts.append({"verts": verts, "faces": faces, "key": "dark", "role": "base"})
        parts.append(_cylinder_z(math.cos(a) * (r - 0.02), math.sin(a) * (r - 0.02), 0.0, 0.022, 0.022, 0.045,
                                 "dark", "castor", n=10))
    parts.append(_cylinder_z(0.0, 0.0, 0.045, 0.025, 0.025, seat_h - seat_t - 0.045, "steel", "pole", n=12))
    back_t = 0.05
    parts.append(_box(0.0, -back_t / 2.0, seat_h - seat_t, w - 0.06, d - back_t, seat_t, "fabric", "cushion"))
    parts.append(_box(0.0, d / 2.0 - back_t / 2.0, seat_h + 0.05, w * 0.85, back_t, h - seat_h - 0.05, "fabric",
                      "back"))
    for sx in (-1, 1):
        parts.append(_box(sx * (w / 2.0 - 0.02), -0.02, seat_h + 0.18, 0.04, d * 0.5, 0.03, "dark", "arm"))
        parts.append(_box(sx * (w / 2.0 - 0.02), 0.0, seat_h, 0.02, 0.03, 0.18, "dark", "arm"))
    return parts


def _crib(w: float, d: float, h: float) -> list[Part]:
    """Crib (cot): four corner posts, top and bottom rails, vertical slats on all sides, a mattress base and a
    mattress (bedding) about 0.3 m above the floor."""
    post = 0.045
    rail = 0.035
    base_z = min(0.3, h * 0.35)
    parts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - post / 2.0), sy * (d / 2.0 - post / 2.0), 0.0, post, post, h, "wood",
                              "post"))
    for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
        for z in (base_z - rail, h - rail):
            parts.append(_box(0.0, y, z, w - 2 * post, rail * 0.8, rail, "wood", "rail"))
    for x in (-(w / 2.0 - post / 2.0), w / 2.0 - post / 2.0):
        for z in (base_z - rail, h - rail):
            parts.append(_box(x, 0.0, z, rail * 0.8, d - 2 * post, rail, "wood", "rail"))
    slat, pitch = 0.02, 0.085
    for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
        n = max(1, int((w - 2 * post) / pitch))
        for i in range(n):
            x = -w / 2.0 + post + (i + 0.5) * (w - 2 * post) / n
            parts.append(_box(x, y, base_z, slat, slat, h - rail - base_z, "wood", "slat"))
    parts.append(_box(0.0, 0.0, base_z - rail, w - 2 * post, d - 2 * post, 0.02, "wood", "bottom"))
    parts.append(_superellipsoid(0.0, 0.0, base_z - rail + 0.02, w - 2 * post - 0.02, d - 2 * post - 0.02, 0.1, 0.15,
                                 0.1, "bedding", "mattress"))
    return parts


def _bunk_bed(w: float, d: float, h: float) -> list[Part]:
    """Bunk bed: four posts, two frames with mattresses (lower 0.3 m, upper 1.3 m or 60 % of the height), a guard
    rail on the upper bunk's front (-Y) and a ladder at the foot end of the front."""
    post = 0.06
    frame_t = 0.12
    lower = min(0.3, h * 0.2)
    upper = max(lower + 0.9, min(1.3, h * 0.6)) if h > lower + 1.0 else h * 0.6
    parts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - post / 2.0), sy * (d / 2.0 - post / 2.0), 0.0, post, post, h, "wood",
                              "post"))
    for z in (lower, upper):
        for x in (-(w / 2.0 - post / 2.0), w / 2.0 - post / 2.0):
            parts.append(_box(x, 0.0, z - frame_t, post * 0.8, d - 2 * post, frame_t, "wood", "rail"))
        for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
            parts.append(_box(0.0, y, z - frame_t, w - 2 * post, post * 0.8, frame_t, "wood", "rail"))
        parts.append(_box(0.0, 0.0, z - 0.03, w - 2 * post, d - 2 * post, 0.02, "wood", "bottom"))
        parts.append(_superellipsoid(0.0, 0.0, z - 0.01, w - 2 * post - 0.02, d - 2 * post - 0.02, 0.15, 0.15, 0.1,
                                     "bedding", "mattress"))
    # Guard rail of the upper bunk along the long side; the ladder at the foot end.
    for z in (upper + 0.15, h - 0.04):
        parts.append(_box(-w / 2.0 + post + 0.01, 0.0, z, 0.03, d - 2 * post, 0.03, "wood", "rail"))
    lx = w / 2.0 - post - 0.03
    ly0, ly1 = -d / 2.0 + post, -d / 2.0 + post + 0.4
    for y in (ly0 + 0.015, ly1 - 0.015):
        parts.append(_box(lx, y, 0.0, 0.03, 0.03, upper + 0.3, "wood", "ladder"))
    z = 0.3
    while z < upper:
        parts.append(_box(lx, (ly0 + ly1) / 2.0, z, 0.025, ly1 - ly0 - 0.06, 0.025, "wood", "ladder"))
        z += 0.27
    return parts


# --------------------------------------------------------------------------
# Doors and windows (docs/milestone10.md §4.7): pure parts in the opening's frame
# --------------------------------------------------------------------------
#
# Frame of an opening (as wenart.blender.shell builds them): x along the wall (the opening from -width/2 to
# +width/2), y across the wall (0 = the wall centre line, the wall from -thickness/2 to +thickness/2), z up from the
# opening's bottom. Keys: ``frame`` (door frame, window frame), ``leaf``, ``glass``, ``handle``, ``rail``
# (sliding / barn track), ``sill`` (inside window sill). shell.build_openings calls ``door_parts`` /
# ``window_parts`` with the looks of ``wenart.blender.looks`` (docs/milestone10.md §1.6b row 20).

DOOR_STYLES: tuple[str, ...] = ("flush", "shaker_panel", "glazed", "pocket", "sliding", "barn", "double", "entrance",
                                "folding")
DOOR_FRAME_W = 0.05
DOOR_LEAF_T = 0.04
ENTRANCE_LEAF_T = 0.065
DOOR_PANEL_FRAME_M = 0.11        # shaker panel door: stiles and rails
DOOR_PANEL_PROUD_M = 0.006
GLAZED_FRAME_M = 0.09
SLIDING_OVERLAP_M = 0.05         # a surface-mounted sliding / barn leaf covers the opening plus this per side
SLIDING_STANDOFF_M = 0.012       # off the wall face
RAIL_H = 0.04
LEVER_HEIGHT_M = 1.0
# Window frames by material (docs/milestone10.md §4.7): (frame width, frame depth) in metres, typical profiles
# (assumed; no drawing gives them).
WINDOW_PROFILES: dict[str, tuple[float, float]] = {
    "pvc_white": (0.065, 0.07), "aluminium_anthracite": (0.05, 0.065), "steel_black": (0.035, 0.045),
    "dark_bronze": (0.045, 0.06), "oak": (0.068, 0.068), "painted_metal_white": (0.05, 0.06),
}
DEFAULT_WINDOW_PROFILE = (0.05, 0.06)
MULLION_W = 0.04
INSIDE_SILL = {"depth_proud": 0.03, "thickness": 0.025, "ears": 0.02}


def door_style_of(look: dict | None) -> str:
    style = (look or {}).get("door_style")
    return style if style in DOOR_STYLES else "flush"


def _leaf_box(cx: float, z0: float, lw: float, lh: float, t: float, y: float = 0.0) -> Part:
    return _box(cx, y, z0, lw, t, lh, "leaf", "leaf")


def _lever_pair(x: float, z: float, t: float, y: float = 0.0) -> list[Part]:
    """Lever handles on both faces of a leaf of thickness ``t`` centred on ``y``."""
    out = []
    for s in (-1, 1):
        yy = y + s * (t / 2.0 + 0.03)
        out.append(_box(x, yy, z - 0.035, 0.02, 0.06, 0.07, "handle", "handle"))              # rose and neck
        out.append(_box(x - 0.06, yy + s * 0.02, z - 0.01, 0.13, 0.02, 0.02, "handle", "handle"))       # lever
    return out


def door_parts(look: dict | None, width: float, height: float, thickness: float,
               frame_w: float = DOOR_FRAME_W) -> tuple[list[Part], dict]:
    """``(parts, record)`` of a door in the opening's frame (see above) for a door look
    (``wenart.blender.looks.door_look``: ``door_style`` decided with the drawn operation first). Swing styles
    (flush, shaker panel, glazed, entrance) and double / folding doors sit in a frame as deep as the wall;
    pocket doors are a flush leaf with a recessed pull; sliding and barn doors hang on the room face of the wall
    (``look["side"]``: +1 / -1, the y side of the room; default -1) from a rail and overlap the opening. A drawn
    ``fixed`` door (``look["operation"]``) has no handles."""
    style = door_style_of(look)
    side = -1.0 if float((look or {}).get("side") or -1.0) < 0 else 1.0
    w, h, t = float(width), float(height), float(thickness)
    parts: list[Part] = []
    surface = style in ("sliding", "barn")
    if not surface:
        parts += [_box(-(w / 2.0 - frame_w / 2.0), 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(w / 2.0 - frame_w / 2.0, 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(0.0, 0.0, h - frame_w, w - 2 * frame_w, t, frame_w, "frame", "frame")]
    lw, lh = w - 2 * frame_w - 0.01, h - frame_w - 0.01
    leaf_t = ENTRANCE_LEAF_T if style == "entrance" else DOOR_LEAF_T
    lever_z = min(LEVER_HEIGHT_M, lh - 0.1)
    if style in ("flush", "pocket", "entrance", "shaker_panel", "glazed"):
        if style == "glazed":
            f = min(GLAZED_FRAME_M, lw * 0.2)
            parts += [_box(-(lw / 2.0 - f / 2.0), 0.0, 0.0, f, leaf_t, lh, "leaf", "leaf"),
                      _box(lw / 2.0 - f / 2.0, 0.0, 0.0, f, leaf_t, lh, "leaf", "leaf"),
                      _box(0.0, 0.0, 0.0, lw - 2 * f, leaf_t, f * 1.6, "leaf", "leaf"),
                      _box(0.0, 0.0, lh - f, lw - 2 * f, leaf_t, f, "leaf", "leaf"),
                      _box(0.0, 0.0, f * 1.6, lw - 2 * f, 0.008, lh - f * 2.6, "glass", "glass")]
        else:
            parts.append(_leaf_box(0.0, 0.0, lw, lh, leaf_t))
        if style == "shaker_panel":
            f = min(DOOR_PANEL_FRAME_M, lw * 0.2)
            for s in (-1, 1):
                y = s * (leaf_t / 2.0 + DOOR_PANEL_PROUD_M / 2.0)
                parts += [_box(-(lw / 2.0 - f / 2.0), y, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                          _box(lw / 2.0 - f / 2.0, y, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                          _box(0.0, y, 0.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f * 1.5, "leaf", "panel"),
                          _box(0.0, y, lh * 0.5 - f / 2.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel"),
                          _box(0.0, y, lh - f, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel")]
        if style == "entrance":
            for z in (lh * 0.3, lh * 0.5, lh * 0.7):
                for s in (-1, 1):
                    parts.append(_box(0.0, s * (leaf_t / 2.0 + 0.002), z, lw - 0.16, 0.004, 0.012, "frame", "groove"))
            for s in (-1, 1):                                            # a long bar pull on both faces
                parts.append(_box(lw / 2.0 - 0.1, s * (leaf_t / 2.0 + 0.04), lever_z - 0.4, 0.025, 0.025, 0.8,
                                  "handle", "handle"))
        elif style == "pocket":
            for s in (-1, 1):                                            # recessed flush pulls
                parts.append(_box(lw / 2.0 - 0.06, s * (leaf_t / 2.0 + 0.001), lever_z - 0.08, 0.03, 0.002, 0.16,
                                  "handle", "handle"))
        else:
            parts += _lever_pair(lw / 2.0 - 0.07, lever_z, leaf_t)
    elif style in ("double", "folding"):
        half = lw / 2.0 - 0.002
        for s in (-1, 1):
            parts.append(_leaf_box(s * (half / 2.0 + 0.001), 0.0, half, lh, DOOR_LEAF_T))
        if style == "double":
            for s in (-1, 1):
                parts += _lever_pair(s * 0.06, lever_z, DOOR_LEAF_T)
        else:
            parts += _lever_pair(lw / 2.0 - 0.07, lever_z, DOOR_LEAF_T)
    else:                                                                # sliding / barn: on the room face
        sw = w + 2 * SLIDING_OVERLAP_M
        sh = h + 0.02
        y = side * (t / 2.0 + SLIDING_STANDOFF_M + DOOR_LEAF_T / 2.0)
        if style == "barn":
            n = max(3, int(sw / 0.16))
            pw = sw / n
            for i in range(n):
                parts.append(_box(-sw / 2.0 + pw * (i + 0.5), y, 0.0, pw - 0.004, DOOR_LEAF_T, sh, "leaf", "leaf"))
            for z in (0.15, sh - 0.3):                                   # the ledges
                parts.append(_box(0.0, y + side * (DOOR_LEAF_T / 2.0 + 0.01), z, sw - 0.04, 0.02, 0.15, "leaf",
                                  "ledge"))
        else:
            parts.append(_box(0.0, y, 0.0, sw, DOOR_LEAF_T, sh, "leaf", "leaf"))
        rail_y = side * (t / 2.0 + 0.02)
        parts.append(_box(w / 2.0 - 0.05, rail_y, sh + 0.02, 2.0 * sw, 0.02, RAIL_H, "rail", "rail"))
        parts.append(_box(-sw / 2.0 + 0.08, y + side * (DOOR_LEAF_T / 2.0 + 0.01), lever_z - 0.15, 0.03, 0.02, 0.3,
                          "handle", "handle"))
    fixed = (look or {}).get("operation") == "fixed"
    if fixed:                                                            # a drawn fixed leaf: nothing to open it
        parts = [p for p in parts if p["key"] != "handle"]
    record = {"door_style": style, "leaf_thickness": leaf_t, "frame_width": None if surface else frame_w,
              "surface_mounted": surface, "side": side if surface else None, "handles": not fixed,
              "parts": sorted({p["role"] for p in parts})}
    return parts, record


def window_profile(material: str | None) -> tuple[float, float]:
    """``(frame width, frame depth)`` of a window frame material (``WINDOW_PROFILES``, assumed typical sizes)."""
    return WINDOW_PROFILES.get(str(material or ""), DEFAULT_WINDOW_PROFILE)


def window_parts(look: dict | None, width: float, height: float, wall_thickness: float, mullions: int = 0,
                 transoms: int = 0, inside: int = -1) -> tuple[list[Part], dict]:
    """``(parts, record)`` of a window in the opening's frame: the frame (the material's profile), ``mullions``
    vertical and ``transoms`` horizontal bars when the building gives them (none otherwise), the glass pane(s)
    and an inside sill on the room side (``inside``: -1 / +1, the y side of the room; the outside sill is the
    shell's), lying on the reveal from the frame to past the wall face. Profiles: ``window_profile``."""
    fw, depth = window_profile((look or {}).get("material"))
    w, h = float(width), float(height)
    depth = min(depth, float(wall_thickness))
    parts = [_box(-(w / 2.0 - fw / 2.0), 0.0, 0.0, fw, depth, h, "frame", "frame"),
             _box(w / 2.0 - fw / 2.0, 0.0, 0.0, fw, depth, h, "frame", "frame"),
             _box(0.0, 0.0, h - fw, w - 2 * fw, depth, fw, "frame", "frame"),
             _box(0.0, 0.0, 0.0, w - 2 * fw, depth, fw, "frame", "frame")]
    m, tr = max(0, int(mullions or 0)), max(0, int(transoms or 0))
    for i in range(1, m + 1):
        x = -w / 2.0 + fw + (w - 2 * fw) * i / (m + 1)
        parts.append(_box(x, 0.0, fw, MULLION_W, depth * 0.9, h - 2 * fw, "frame", "mullion"))
    for j in range(1, tr + 1):
        z = fw + (h - 2 * fw) * j / (tr + 1)
        parts.append(_box(0.0, 0.0, z - MULLION_W / 2.0, w - 2 * fw, depth * 0.9, MULLION_W, "frame", "transom"))
    parts.append(_box(0.0, 0.0, fw, w - 2 * fw, 0.006, h - 2 * fw, "glass", "glass"))
    s = -1.0 if inside < 0 else 1.0
    t = float(wall_thickness)
    proud = INSIDE_SILL["depth_proud"]
    sill_d = t / 2.0 - depth / 2.0 + proud
    parts.append(_box(0.0, s * (depth / 2.0 + sill_d / 2.0), 0.0, w + 2 * INSIDE_SILL["ears"],     # on the reveal
                      sill_d, INSIDE_SILL["thickness"], "sill", "sill"))
    record = {"material": (look or {}).get("material"), "frame_width": fw, "frame_depth": depth, "mullions": m,
              "transoms": tr, "inside_sill": {"depth": round(sill_d, 4), "proud": proud,
                                              "thickness": INSIDE_SILL["thickness"]},
              "profile_assumed": True}
    return parts, record


# --------------------------------------------------------------------------
# Milestone 10 decor (docs/milestone10.md §4.6): parametric fallbacks of the 12 new types
# --------------------------------------------------------------------------
#
# Item frame as every decor item: width X, depth Y, front = local -Y (curtains, blinds and clocks face the room
# with it; their back is +Y, on the wall side), origin at the box centre on its rest height. Keys starting with
# ``colour_`` take the item's colour name (``decor.colour``: the brief's or the AI's) as the base colour of their
# material (``furniture._Materials``); ``pot`` takes the plant's pot material and colour; ``bulb`` emits when the
# item's ``light_on`` is true (the interior evening mood).

COLOUR_PREFIX = "colour_"
CURTAIN_PANEL_SHARE = 0.22       # each curtain panel covers this share of the rod width (open curtains)
CURTAIN_PLEATS = 5
BLIND_DOWN_SHARE = 0.35          # a roller blind is drawn down this share of its window (decor_ai sizes its box)
PLANT_SPECIES: tuple[str, ...] = ("palm", "monstera", "fiddle_leaf_fig", "olive", "fern", "other")
PLANT_POT_SHARE = 0.55           # pot diameter / the smaller side of the item box
LIGHT_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light", "table_lamp")


def _cylinder_x(x0: float, cy: float, cz: float, ry: float, rz: float, length: float, key: str, role: str = "body",
                n: int = 16) -> Part:
    """Elliptic cylinder along +X from ``x0`` to ``x0 + length`` (a turned Z cylinder: (x, y, z) -> (z, y, -x),
    a proper rotation, so the faces stay wound outwards)."""
    part = _cylinder_z(0.0, 0.0, 0.0, rz, ry, length, key, role, n)
    part["verts"] = [(x0 + z, cy + y, cz - x) for x, y, z in part["verts"]]
    return part


def _leaf(bx: float, by: float, bz: float, length: float, width: float, thick: float, yaw_deg: float,
          pitch_deg: float, key: str = "green", role: str = "leaf") -> Part:
    """A flat leaf (a superellipsoid ``width x length x thick``) from the point ``(bx, by, bz)`` outwards along the
    direction ``yaw_deg`` (counter-clockwise from +Y), raised by ``pitch_deg`` (negative: drooping)."""
    part = _superellipsoid(0.0, length / 2.0, -thick / 2.0, width, length, thick, 0.5, 0.6, key, role, n_eta=6, n_om=12)
    p, yw = math.radians(pitch_deg), math.radians(yaw_deg)
    cp, sp, cy, sy = math.cos(p), math.sin(p), math.cos(yw), math.sin(yw)
    verts = []
    for x, y, z in part["verts"]:
        y1, z1 = y * cp - z * sp, y * sp + z * cp
        verts.append((bx + x * cy - y1 * sy, by + x * sy + y1 * cy, bz + z1))
    part["verts"] = verts
    part["smooth"] = True
    return part


def _leaf_length(reach: float, pitch_deg: float, room_above: float) -> float:
    """The longest leaf that stays within ``reach`` sideways and ``room_above`` upwards at ``pitch_deg``."""
    p = math.radians(pitch_deg)
    out = reach / max(math.cos(p), 0.2)
    if p > 0:
        out = min(out, room_above / max(math.sin(p), 1e-3))
    return max(0.05, out)


def _pot(w: float, d: float, h: float) -> tuple[list[Part], float, float]:
    """``(parts, pot top, crown radius)``: a tapered pot (key ``pot``) with soil."""
    r = min(w, d) / 2.0
    pr = r * PLANT_POT_SHARE
    pot_h = min(0.45, max(0.2, h * 0.22))
    parts = [_frustum_z(0.0, 0.0, 0.0, pr * 0.78, pr * 0.78, pr, pr, pot_h, "pot", "pot"),
             _cylinder_z(0.0, 0.0, pot_h - 0.015, pr * 0.92, pr * 0.92, 0.012, "dark", "soil", n=24)]
    return parts, pot_h, r


def _plant_large(w: float, d: float, h: float, species: str | None = None) -> list[Part]:
    """A large floor plant (``plant_large``) of its species (docs/milestone10.md §4.6: palm, monstera,
    fiddle-leaf fig, olive, fern; anything else a plain crown) in a pot, inside its ``w x d x h`` box."""
    parts, top, r = _pot(w, d, h)
    reach = r - 0.01
    crown_h = h - top
    sp = species if species in PLANT_SPECIES else "other"
    if sp == "palm":
        for k, (dx, dy, f) in enumerate(((0.03, 0.0, 0.75), (-0.025, 0.02, 0.9), (0.0, -0.03, 1.0))):
            stem_top = top + crown_h * 0.55 * f
            parts.append(_cylinder_z(dx, dy, top - 0.01, 0.012, 0.012, stem_top - top + 0.01, "wood", "stem", n=8))
            for j in range(6):
                pitch = 35.0 if j % 2 == 0 else -5.0
                length = _leaf_length(reach - math.hypot(dx, dy), pitch, h - stem_top - 0.02)
                parts.append(_leaf(dx, dy, stem_top, length, length * 0.16, 0.01, 60.0 * j + 20.0 * k, pitch))
    elif sp == "monstera":
        for j in range(7):
            base = top + crown_h * (0.15 + 0.07 * j)
            yaw = 51.4 * j
            off = (-0.04 * math.sin(math.radians(yaw)), 0.04 * math.cos(math.radians(yaw)))
            parts.append(_cylinder_z(off[0] * 0.5, off[1] * 0.5, top - 0.01, 0.008, 0.008, base - top + 0.01, "green",
                                     "stem", n=6))
            length = min(_leaf_length(reach - 0.04, 20.0, h - base - 0.02), 0.5)
            parts.append(_leaf(off[0], off[1], base, length, length * 0.8, 0.012, yaw, 20.0))
    elif sp == "fiddle_leaf_fig":
        trunk_top = top + crown_h * 0.95
        parts.append(_cylinder_z(0.0, 0.0, top - 0.01, 0.018, 0.018, trunk_top - top, "wood", "trunk", n=10))
        n = 14
        for j in range(n):
            base = top + crown_h * (0.4 + 0.5 * j / n)
            length = min(_leaf_length(reach - 0.02, 35.0, h - base - 0.02), 0.28)
            parts.append(_leaf(0.0, 0.0, base, length, length * 0.6, 0.01, 137.5 * j, 35.0))
    elif sp == "olive":
        trunk_top = top + crown_h * 0.45
        parts.append(_cylinder_z(0.0, 0.0, top - 0.01, 0.025, 0.025, trunk_top - top + 0.05, "wood", "trunk", n=10))
        blob = min(reach * 1.1, crown_h * 0.45)
        blobs = ((0.0, 0.0, 0.25), (reach * 0.35, 0.0, 0.0), (-reach * 0.3, reach * 0.2, 0.1))
        for dx, dy, dz in blobs:
            bw = min(blob, 2 * (reach - abs(dx)), 2 * (reach - abs(dy)))
            z0 = min(trunk_top + dz * crown_h * 0.3, h - bw * 0.8)
            parts.append(_superellipsoid(dx, dy, z0, bw, bw, bw * 0.8, 0.9, 0.9, "green", "crown", n_eta=8, n_om=16))
    elif sp == "fern":
        for j in range(12):
            pitch = 25.0 if j % 2 == 0 else -12.0
            length = _leaf_length(reach, pitch, h - top - 0.02)
            parts.append(_leaf(0.0, 0.0, top + 0.02, length, length * 0.3, 0.01, 30.0 * j, pitch))
    else:
        parts += [_cylinder_z(0.0, 0.0, top, 0.015, 0.015, crown_h * 0.4, "wood", "stem", n=8),
                  _cylinder_z(0.0, 0.0, top + crown_h * 0.35, reach, reach, crown_h * 0.65, "green", "crown", n=16)]
    return parts


def _new_decor_parts(dtype: str, w: float, d: float, h: float, item: dict | None = None) -> list[Part]:
    """The parametric fallback of a Milestone 10 decor type (``decor_parts``)."""
    r = min(w, d) / 2.0
    # Milestone 12 (§6.4): our procedural textiles (the mesh makers at the end of this module)
    if dtype == "curtain":                    # an open pair of pleated panels under a rod (one per window)
        return curtain_parts(w, d, h)
    if dtype == "blind":                      # a roller blind (default) or a slatted blind (item ``blind_kind``)
        return blind_parts(w, d, h, kind=str((item or {}).get("blind_kind") or "roller"))
    if dtype == "throw":                      # without a host: a flat cloth with its folds (on a host: textiles.drape)
        return [flat_cloth(w, d, min(h, CLOTH_THICKNESS_M * 2.0))]
    if dtype == "books":                      # a stack of three books lying flat
        keys = ("dark", "painted", "terracotta")
        parts, z = [], 0.0
        bh = h / 3.0
        for i in range(3):
            s = 1.0 - 0.08 * i
            parts.append(_box(0.01 * (i % 2), 0.0, z, w * s, d * s, bh - 0.002, keys[i], "book"))
            z += bh
        return parts
    if dtype == "candle":                     # three pillar candles on a plate, a flame each (lit at evening)
        rr = r * 0.32
        plate = 0.012
        parts = [_cylinder_z(0.0, 0.0, 0.0, w / 2.0, d / 2.0, plate, "colour_ceramic", "plate", n=24)]
        for (dx, dy), f in zip(((-w * 0.22, -d * 0.12), (w * 0.2, -d * 0.1), (0.0, d * 0.22)), (1.0, 0.75, 0.55)):
            ch = (h - plate - 0.03) * f
            parts.append(_cylinder_z(dx, dy, plate, rr, rr, ch, "ceramic", "candle", n=16))
            parts.append(_superellipsoid(dx, dy, plate + ch + 0.004, 0.01, 0.01, 0.022, 0.8, 1.0, "bulb", "flame",
                                         n_eta=6, n_om=8))
        return parts
    if dtype == "basket":                     # a woven basket, its open top shown dark
        return [_frustum_z(0.0, 0.0, 0.0, w / 2.0 * 0.85, d / 2.0 * 0.85, w / 2.0, d / 2.0, h * 0.98, "rattan", "body"),
                _cylinder_z(0.0, 0.0, h * 0.98, w / 2.0 * 0.9, d / 2.0 * 0.9, h * 0.02, "dark", "inside", n=24)]
    if dtype == "tray":                       # a flat tray with low rims
        t, rim = 0.008, min(0.012, w * 0.05, d * 0.05)
        return [_box(0.0, 0.0, 0.0, w, d, t, "colour_wood", "base"),
                _box(0.0, -d / 2.0 + rim / 2.0, t, w, rim, h - t, "colour_wood", "rim"),
                _box(0.0, d / 2.0 - rim / 2.0, t, w, rim, h - t, "colour_wood", "rim"),
                _box(-w / 2.0 + rim / 2.0, 0.0, t, rim, d - 2 * rim, h - t, "colour_wood", "rim"),
                _box(w / 2.0 - rim / 2.0, 0.0, t, rim, d - 2 * rim, h - t, "colour_wood", "rim")]
    if dtype == "clock":                      # a wall clock facing -Y: rim, face, hands
        cr = min(w, h) / 2.0
        hands = min(0.006, d / 4.0)
        face = min(0.01, d / 4.0)
        y0 = -d / 2.0 + hands                       # the face sits behind the hands
        parts = [_cylinder_y(0.0, y0 + face, cr, cr, cr, d - hands - face, "colour_steel", "rim", n=40),
                 _cylinder_y(0.0, y0, cr, cr * 0.9, cr * 0.9, face, "ceramic", "face", n=40)]
        parts.append(_box(0.0, -d / 2.0 + hands * 0.75, cr - 0.005, cr * 0.55, hands / 2.0, 0.01, "dark", "hand"))
        parts.append(_box(0.0, -d / 2.0 + hands * 0.25, cr, 0.008, hands / 2.0, cr * 0.75, "dark", "hand"))
        return parts
    if dtype == "sculpture":                  # an abstract piece: stacked smooth forms on a plinth
        base_h = min(0.05, h * 0.12)
        parts = [_box(0.0, 0.0, 0.0, w * 0.8, d * 0.8, base_h, "dark", "base")]
        z, s = base_h, 1.0
        for i in range(3):
            bh = (h - base_h) * (0.45 if i == 0 else 0.3 if i == 1 else 0.25)
            parts.append(_superellipsoid(0.0, 0.0, z, w * 0.7 * s, d * 0.7 * s, bh, 0.8, 0.9, "colour_ceramic", "form",
                                         n_eta=8, n_om=20))
            z += bh
            s *= 0.75
        return parts
    if dtype == "plant_large":
        return _plant_large(w, d, h, (item or {}).get("species"))
    if dtype == "pendant_light":              # a ceiling canopy, a cord and a cone shade with its bulb
        shade_h = min(0.3, h * 0.6)
        canopy = min(0.06, r)
        parts = [_cylinder_z(0.0, 0.0, h - 0.025, canopy, canopy, 0.025, "colour_steel", "canopy", n=16),
                 _cylinder_z(0.0, 0.0, shade_h, 0.004, 0.004, h - 0.025 - shade_h, "dark", "cord", n=6),
                 _frustum_z(0.0, 0.0, 0.0, w / 2.0, d / 2.0, w * 0.12, d * 0.12, shade_h, "colour_steel", "shade")]
        bulb = min(0.06, r * 0.4)
        parts.append(_superellipsoid(0.0, 0.0, 0.01, bulb, bulb, bulb, 1.0, 1.0, "bulb", "bulb", n_eta=6, n_om=12))
        return parts
    if dtype == "ceiling_light":              # a flush canopy with a dome diffuser
        canopy = min(0.03, h * 0.3)
        return [_cylinder_z(0.0, 0.0, h - canopy, w / 2.0 * 0.8, d / 2.0 * 0.8, canopy, "colour_steel", "canopy",
                            n=32),
                _superellipsoid(0.0, 0.0, 0.0, w, d, h - canopy + 0.004, 0.6, 1.0, "bulb", "bulb", n_eta=8, n_om=32)]
    raise KeyError(f"no decor builder for {dtype!r}")


_BUILDERS = {
    "bed": _bed, "bed_single": _bed, "bed_double": _bed,
    "sofa": _sofa, "armchair": lambda w, d, h: _sofa(w, d, h, cushions=1),
    "table_dining": _table_m10, "table_coffee": _table_m10,
    "desk": lambda w, d, h, piece=None: _table_m10(w, d, h, piece, desk=True),
    "chair": _chair, "wardrobe": _wardrobe_m10, "dresser": _drawers, "nightstand": _drawers, "tv_unit": _tv_unit,
    "bookshelf": _bookshelf, "kitchen_counter": lambda w, d, h, piece=None: _counter_m10(w, d, h, False, piece),
    "kitchen_island": lambda w, d, h, piece=None: _counter_m10(w, d, h, True, piece),
    "fridge": _fridge, "stove": _stove, "sink_kitchen": _sink, "washbasin": _washbasin_m10, "toilet": _toilet,
    "shower": _shower, "bathtub": _bathtub, "washing_machine": _washing_machine,
    "stair": _stair, "side_table": _side_table, "floor_lamp": _floor_lamp, "potted_plant": _potted_plant,
    # Milestone 10 (docs/milestone10.md §1.1, §4.4, §4.5)
    "sofa_corner": _sofa_corner, "chaise": _chaise, "ottoman": _ottoman, "bench": _bench, "bar_stool": _bar_stool,
    "office_chair": _office_chair, "console_table": _console_table, "crib": _crib, "bunk_bed": _bunk_bed,
    "sideboard": _sideboard, "shoe_cabinet": _shoe_cabinet, "display_cabinet": _display_cabinet,
    "tall_cabinet": _tall_cabinet, "wall_cabinet": _wall_cabinet,
}
# Builders that read the piece itself (drawn flights, round shape; Milestone 10: the design, the L shape); the
# others take only the box.
_PIECE_BUILDERS = ("stair", "side_table", "table_dining", "table_coffee", "desk", "wardrobe", "kitchen_counter",
                   "kitchen_island", "washbasin", "sofa_corner", "console_table", "sideboard", "shoe_cabinet",
                   "display_cabinet", "tall_cabinet", "wall_cabinet")


def build_parts(ftype: str, w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Parts of a parametric piece in its local frame. ``KeyError`` for a
    type without a builder (``unknown`` keeps the proxy box). ``piece``
    (optional) is read by the stair (its drawn flights) and the side table
    (round or square); without it a stair is one assumed flight."""
    try:
        builder = _BUILDERS[ftype]
    except KeyError:
        raise KeyError(f"no parametric builder for furniture type {ftype!r}") from None
    if ftype in _PIECE_BUILDERS:
        return builder(float(w), float(d), float(h), piece)
    return builder(float(w), float(d), float(h))


# --------------------------------------------------------------------------
# Decor (cushion, book_set, plant)
# --------------------------------------------------------------------------

def decor_size(dtype: str, size) -> tuple[float, float, float]:
    """``(w, d, h)`` of a decor item from its ``size`` (2 or 3 values),
    the type default height, every dimension capped at ``DECOR_MAX_M``
    (rugs and wall art, ``LARGE_DECOR_TYPES``, are not capped)."""
    w, d = float(size[0]), float(size[1])
    h = float(size[2]) if len(size) > 2 and size[2] else DECOR_DEFAULT_HEIGHT.get(dtype, 0.2)
    if dtype in LARGE_DECOR_TYPES:
        return tuple(max(0.005, v) for v in (w, d, h))
    return tuple(min(DECOR_MAX_M, max(0.02, v)) for v in (w, d, h))


def decor_parts(dtype: str, w: float, d: float, h: float, item: dict | None = None) -> list[Part]:
    """Parts of a parametric decor item of box ``w x d x h`` (``item``: the decor entry, read for a large
    plant's species)."""
    if dtype in _NEW_DECOR:
        return _new_decor_parts(dtype, w, d, h, item)
    if dtype == "cushion":                         # Milestone 12: a filled cushion, not a box
        if d > h:                                  # lying (an ottoman's, a bench's): thickness = the height
            return [lying_cushion_mesh(w, d, h, key="fabric", role="body")]
        return [cushion_mesh(w, d, h, key="fabric", role="body")]
    if dtype == "book_set":
        parts = []
        n = max(2, min(6, int(w / 0.04)))
        bw = w / n
        keys = ("dark", "painted", "wood", "terracotta")
        for i in range(n):
            bh = h * (0.75 + 0.25 * ((i * 7) % 3) / 2.0)
            parts.append(_box(-w / 2.0 + bw * (i + 0.5), 0.0, 0.0, bw - 0.004, d, bh, keys[i % len(keys)], "book"))
        return parts
    if dtype == "plant":
        r = min(w, d) / 2.0
        pot_h = h * 0.35
        return [
            _cylinder_z(0.0, 0.0, 0.0, r * 0.8, r * 0.8, pot_h, "terracotta", "pot", n=16),
            _cylinder_z(0.0, 0.0, pot_h - 0.01, r * 0.7, r * 0.7, 0.01, "dark", "soil", n=16),
            _cylinder_z(0.0, 0.0, pot_h, 0.012, 0.012, h - pot_h, "wood", "stem", n=8),
            _cylinder_z(0.0, 0.0, pot_h + (h - pot_h) * 0.35, r, r, (h - pot_h) * 0.65, "green", "crown", n=10),
        ]
    if dtype == "rug":                             # Milestone 8: a flat fabric rug at the rule's size
        return [_box(0.0, 0.0, 0.0, w, d, h, "fabric", "rug")]
    r = min(w, d) / 2.0                            # Milestone 9 (docs/milestone9.md §3)
    if dtype == "vase":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.9, r * 0.9, h * 0.72, "accent_ceramic", "body", n=20),
                _cylinder_z(0.0, 0.0, h * 0.72, r * 0.5, r * 0.5, h * 0.28, "accent_ceramic", "neck", n=20)]
    if dtype == "bowl":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.55, r * 0.55, h * 0.3, "accent_ceramic", "base", n=24),
                _cylinder_z(0.0, 0.0, h * 0.3, r, r, h * 0.7, "accent_ceramic", "body", n=24)]
    if dtype == "plant_small":
        pot_h = h * 0.4
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.7, r * 0.7, pot_h, "accent_ceramic", "pot", n=16),
                _cylinder_z(0.0, 0.0, pot_h - 0.01, r * 0.62, r * 0.62, 0.01, "dark", "soil", n=16),
                _cylinder_z(0.0, 0.0, pot_h, r, r, h - pot_h, "green", "crown", n=10)]
    if dtype == "table_lamp":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.45, r * 0.45, h * 0.06, "accent_ceramic", "base", n=20),
                _cylinder_z(0.0, 0.0, h * 0.06, 0.012, 0.012, h * 0.52, "steel", "pole", n=8),
                _cylinder_z(0.0, 0.0, h * 0.55, r, r, h * 0.45, "fabric", "shade", n=24)]
    if dtype == "mirror":                          # a framed mirror: the glass on the front (local -Y) of the frame
        f = min(MIRROR_FRAME_M, w / 6.0, h / 6.0)
        g = min(0.004, d / 4.0)                    # the glass: the front 4 mm of the box, the frame behind it
        return [_box(0.0, g / 2.0, 0.0, w, d - g, h, "accent_wood", "frame"),
                _box(0.0, -d / 2.0 + g / 2.0, f, max(0.01, w - 2 * f), g, max(0.01, h - 2 * f), "mirror",
                     "glass")]
    raise KeyError(f"no decor builder for {dtype!r}")


# Milestone 12 (docs/milestone12.md §4.7, D13): ``decor_rest_height`` (the type-table rest height: a library bed's
# decor at 0.55 m, a sofa's at 0.45 m, a parametric bed's on the pillow top) is gone; decor rests on the built,
# scaled host mesh (``wenart.blender.rest``).


# --------------------------------------------------------------------------
# Bevel radius per part (the Bevel modifier itself is added by furniture.py)
# --------------------------------------------------------------------------

def part_bevel_radius(part: Part) -> float:
    """Bevel radius (metres) of one part: 0 for smooth (superellipsoid) parts
    and glass, ``BEVEL_SOFT_KEYS`` for fabric and bedding, else
    ``BEVEL_BY_ROLE`` / ``BEVEL_BY_KEY`` / ``BEVEL_DEFAULT_M``; never more
    than a third of the part's smallest side (nor ``BEVEL_WIDTH_M``)."""
    if part.get("smooth") or part["key"] in ("glass", "bulb"):
        return 0.0
    key, role = part["key"], part["role"]
    if key in BEVEL_SOFT_KEYS:
        r = BEVEL_SOFT_KEYS[key]
    elif role in BEVEL_BY_ROLE:
        r = BEVEL_BY_ROLE[role]
    else:
        r = BEVEL_BY_KEY.get(key, BEVEL_DEFAULT_M)
    xs, ys, zs = zip(*part["verts"])
    smallest = min(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return max(0.0, min(r, smallest / 3.0, BEVEL_WIDTH_M))


# --------------------------------------------------------------------------
# Placement into the world and bounding boxes
# --------------------------------------------------------------------------

def world_mesh(parts: Sequence[Part], center: Sequence[float], rotation_deg: float, floor_z: float,
               scale: Sequence[float] = (1.0, 1.0, 1.0)) -> tuple[list, list, list[str]]:
    """``(verts, faces, face_keys)``: the parts scaled in the local frame,
    rotated about +Z and moved to ``center`` on the floor ``floor_z``."""
    verts, faces, keys = [], [], []
    rad = math.radians(rotation_deg)
    c, s = math.cos(rad), math.sin(rad)
    for part in parts:
        offset = len(verts)
        for x, y, z in part["verts"]:
            x, y, z = x * scale[0], y * scale[1], z * scale[2]
            verts.append((center[0] + c * x - s * y, center[1] + s * x + c * y, floor_z + z))
        for f in part["faces"]:
            faces.append([i + offset for i in f])
            keys.append(part["key"])
    return verts, faces, keys


def parametric_bbox(ftype: str, w: float, d: float, h: float, piece: dict | None = None) -> tuple[float, float, float]:
    """``(width, depth, height)`` of the parametric mesh (its real box);
    ``piece`` as in ``build_parts``."""
    x0, y0, z0, x1, y1, z1 = _bbox(build_parts(ftype, w, d, h, piece=piece))
    return (x1 - x0, y1 - y0, z1 - z0)


def piece_bbox(piece: dict) -> tuple[float, float, float, str]:
    """``(width, depth, height, source)`` of the box a piece occupies in its
    own frame, as the scene will build it: the fitted box recorded by the
    fitter (``asset.bbox_m`` is already scaled: footprint width and depth,
    catalogue height times the z scale) for a library asset, the parametric
    box otherwise, the proxy box for ``unknown``. The camera planner uses
    this (docs/milestone4.md §2: free points from fitted boxes, not only
    footprints)."""
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    h, _ = proxy_height(piece["type"], piece.get("height"))
    asset = piece.get("asset") or {}
    if asset.get("method") == "library" and asset.get("bbox_m"):
        bw, bd, bh = (float(v) for v in asset["bbox_m"][:3])
        return (bw, bd, bh, "library")
    if piece["type"] in _BUILDERS:
        bw, bd, bh = parametric_bbox(piece["type"], w, d, h, piece=piece)
        return (bw, bd, bh, "parametric")
    return (w, d, h, "proxy")


def obstacle_rect(piece: dict) -> dict:
    """Footprint-shaped rectangle of the fitted box (never smaller than the
    drawn footprint), for the free-point search."""
    fp = piece["footprint"]
    bw, bd, _, _ = piece_bbox(piece)
    return {"center": list(fp["center"]), "size": [max(float(fp["size"][0]), bw), max(float(fp["size"][1]), bd)],
            "rotation_deg": float(fp["rotation_deg"])}


def local_bbox_of_world_points(points: Sequence[Sequence[float]], center: Sequence[float], rotation_deg: float
                               ) -> tuple[float, float, float, float, float, float]:
    """Bounding box of world points in the frame rotated by ``rotation_deg``
    about ``center`` (used by the tests to check rotated pieces)."""
    local = [(*G.rotate_point((p[0], p[1]), -rotation_deg, (center[0], center[1])), p[2]) for p in points]
    xs, ys, zs = [p[0] for p in local], [p[1] for p in local], [p[2] for p in local]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


# --------------------------------------------------------------------------
# Milestone 12 (docs/milestone12.md §4.7, §6.4; track S): textile meshes (cushions, cloth, curtains, blinds);
# ``wenart.blender.textiles`` drapes the cloth on a built host with them
# --------------------------------------------------------------------------

CUSHION_GRID = (10, 10)
SEAM_M = 0.006                    # the half thickness left at a cushion's seam
EDGE_DRAW = 0.035                 # a cushion's edges are drawn in by this share of the side between the corners
CLOTH_OFFSET_M = 0.005            # the shrinkwrap offset (§4.7: 5 mm)
CLOTH_THICKNESS_M = 0.008
FOLD_AMPLITUDE_M = 0.006          # modelled wrinkles (never into the host: added above the offset)
CLOTH_STEP_M = 0.05               # cloth grid pitch
PLEAT_PITCH_M = 0.12
PLEAT_DEPTH_M = 0.035
CURTAIN_LAYER_M = 0.003
SLAT_M = 0.025
SLAT_GAP_M = 0.022
SLAT_TILT_DEG = 20.0
BLIND_KINDS = ("roller", "slats")


def _cloth_part(verts, faces, key: str, role: str, smooth: bool = True) -> Part:
    return {"verts": [tuple(float(c) for c in v) for v in verts], "faces": [list(f) for f in faces], "key": key,
            "role": role, "smooth": smooth}


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
    return _cloth_part(verts, faces, key, role)


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


def fold(x: float, y: float, w: float, d: float) -> float:
    """Modelled wrinkles (>= 0, at most ``FOLD_AMPLITUDE_M``): smooth fixed sines over the cloth's own frame."""
    a = math.sin(7.3 * x / max(w, 1e-6) + 0.7) * math.sin(5.1 * y / max(d, 1e-6) + 1.9)
    b = math.sin(13.0 * (x + 0.6 * y) / max(w + d, 1e-6) + 2.3)
    return FOLD_AMPLITUDE_M * (0.5 + 0.3 * a + 0.2 * b)


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
    return _cloth_part(verts, faces, key, role)


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
    parts = [_cylinder_x(-w / 2.0, 0.0, h - 0.02, 0.012, 0.012, w, "steel", "rod", n=12)]
    pw = w * CURTAIN_PANEL_SHARE
    parts.append(_pleated_panel(-w / 2.0, -w / 2.0 + pw, h - 0.05, d, key))
    parts.append(_pleated_panel(w / 2.0 - pw, w / 2.0, h - 0.05, d, key))
    return parts


def blind_parts(w: float, d: float, h: float, kind: str = "roller", key: str = "colour_fabric") -> list[Part]:
    """A roller blind (a tube at the top, the fabric panel down to a bottom bar) or a slatted blind (``SLAT_M``
    slats every ``SLAT_M + SLAT_GAP_M`` tilted ``SLAT_TILT_DEG``, a head rail, two ladder tapes) in the box
    ``w x d x h`` (bottom at 0)."""
    if kind not in BLIND_KINDS:
        kind = "roller"
    if kind == "roller":
        tube = min(0.03, d / 2.0, h / 4.0)
        bar = min(0.02, h / 8.0)
        return [_cylinder_x(-w / 2.0, 0.0, h - tube, tube, tube, w, key, "roller", n=16),
                _box(0.0, -tube * 0.4, bar, w - 0.02, 0.004, h - tube - bar, key, "panel"),
                _box(0.0, -tube * 0.4, 0.0, w - 0.02, min(0.012, d), bar, "dark", "bar")]
    head = min(0.04, h / 6.0)
    parts = [_box(0.0, 0.0, h - head, w, min(d, 0.04), head, "painted", "rail")]
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
        parts.append(_cloth_part(verts, faces, key, "slat", smooth=False))
    for sx in (-w / 3.0, w / 3.0):
        parts.append(_box(sx, 0.0, 0.0, 0.012, 0.002, h - head, "dark", "tape"))
    return parts
