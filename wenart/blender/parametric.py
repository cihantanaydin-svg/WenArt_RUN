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
"""
from __future__ import annotations

import math
from typing import Sequence

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
)
# Built by shell.build_stairs with the walls (fixed equipment), never by furniture.create_furniture.
SHELL_TYPES: tuple[str, ...] = ("stair",)
DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant", "rug")   # parametric decor builders (M8: rug)
# Decor without the 0.6 m cap (Milestone 8): a rug under a group of pieces, a picture over a sofa.
LARGE_DECOR_TYPES: tuple[str, ...] = ("rug", "wall_art")
MATERIAL_KEYS: tuple[str, ...] = ("wood", "fabric", "bedding", "ceramic", "steel", "painted", "worktop", "dark",
                                  "glass", "green", "terracotta", "duvet")
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
}
BEVEL_SOFT_KEYS: dict[str, float] = {"fabric": 0.03, "bedding": 0.03, "duvet": 0.03}
BEVEL_BY_KEY: dict[str, float] = {"ceramic": 0.012}

# How far a handle or a door may stand proud of the footprint (metres);
# the tests allow 1 cm.
PROUD = 0.008
# Largest decor dimension (docs/milestone4.md, Conventions: never larger than 0.6 m).
DECOR_MAX_M = 0.6
DECOR_DEFAULT_HEIGHT = {"cushion": 0.12, "book_set": 0.22, "plant": 0.6, "rug": 0.012, "wall_art": 0.6}
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


def _fridge(w: float, d: float, h: float) -> list[Part]:
    hx = w / 2.0 - 0.08
    return [
        _box(0.0, 0.0, 0.0, w, d, h, "steel", "body"),
        _box(0.0, -d / 2.0 - PROUD / 4.0, h * 0.7, w, PROUD / 2.0, 0.01, "dark", "front"),   # door split line
        _box(hx, -d / 2.0 - PROUD / 2.0, h * 0.72, 0.02, PROUD, h * 0.2, "dark", "handle"),  # freezer handle
        _box(hx, -d / 2.0 - PROUD / 2.0, h * 0.3, 0.02, PROUD, h * 0.35, "dark", "handle"),  # fridge handle
    ]


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
    tray_h = 0.05
    return [
        _box(0.0, 0.0, 0.0, w, d, tray_h, "ceramic", "tray"),
        _box(0.0, -d / 2.0 + 0.005, tray_h, w, 0.01, h - tray_h, "glass", "front"),
        _box(-(w / 2.0 - 0.005), 0.005, tray_h, 0.01, d - 0.01, h - tray_h, "glass", "side"),
        _box((w / 2.0 - 0.005), 0.005, tray_h, 0.01, d - 0.01, h - tray_h, "glass", "side"),
        _cylinder_z(0.0, d / 2.0 - 0.1, h - 0.15, 0.03, 0.03, 0.01, "steel", "head", n=12),
    ]


def _bathtub(w: float, d: float, h: float) -> list[Part]:
    t = min(0.08, w * 0.08, d * 0.12)
    parts = _basin(0.0, 0.0, 0.0, w, d, h, t, "ceramic")
    parts[-1] = _box(0.0, 0.0, 0.0, w - 2 * t, d - 2 * t, min(0.1, h * 0.2), "ceramic", "basin")
    parts.append(_cylinder_z(w / 2.0 - t / 2.0, 0.0, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    return parts


def _washing_machine(w: float, d: float, h: float) -> list[Part]:
    r = min(w, d) * 0.28
    return [
        _box(0.0, 0.0, 0.0, w, d, h, "painted", "body"),
        _cylinder_y(0.0, -d / 2.0 - PROUD / 2.0, h * 0.45, r + 0.02, r + 0.02, PROUD / 2.0, "steel", "front", n=28),
        _cylinder_y(0.0, -d / 2.0 - PROUD, h * 0.45, r, r, PROUD / 2.0, "dark", "front", n=28),
        _box(0.0, -d / 2.0 - PROUD / 4.0, h - 0.12, w - 0.04, PROUD / 2.0, 0.08, "dark", "front"),
    ]


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


_BUILDERS = {
    "bed": _bed, "bed_single": _bed, "bed_double": _bed,
    "sofa": _sofa, "armchair": lambda w, d, h: _sofa(w, d, h, cushions=1),
    "table_dining": _table, "table_coffee": _table, "desk": lambda w, d, h: _table(w, d, h, desk=True),
    "chair": _chair, "wardrobe": _wardrobe, "dresser": _drawers, "nightstand": _drawers, "tv_unit": _tv_unit,
    "bookshelf": _bookshelf, "kitchen_counter": _counter, "kitchen_island": lambda w, d, h: _counter(w, d, h, True),
    "fridge": _fridge, "stove": _stove, "sink_kitchen": _sink, "washbasin": _washbasin, "toilet": _toilet,
    "shower": _shower, "bathtub": _bathtub, "washing_machine": _washing_machine,
    "stair": _stair, "side_table": _side_table, "floor_lamp": _floor_lamp, "potted_plant": _potted_plant,
}
# Builders that read the piece itself (drawn flights, round shape); the others take only the box.
_PIECE_BUILDERS = ("stair", "side_table")


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


def decor_parts(dtype: str, w: float, d: float, h: float) -> list[Part]:
    if dtype == "cushion":
        return [_box(0.0, 0.0, 0.0, w, d, h, "fabric", "body")]
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
    raise KeyError(f"no decor builder for {dtype!r}")


def decor_rest_height(host_type: str | None, host_height: float, dtype: str,
                      host_size: Sequence[float] | None = None) -> float:
    """Height above the floor where a decor item rests on its host: cushions
    on the sofa seat, books on a shelf or a top, plants on the floor. On a
    bed built parametrically (``host_size`` = its footprint ``(w, d)``) the
    item rests on the bedding top (``bedding_top``: the soft pillows rise
    above the type height, docs/milestone6.md §5 row 8); without
    ``host_size`` (a library bed, a proxy) on the type height as before."""
    if dtype == "plant" or not host_type:
        return 0.0
    if host_type in ("sofa", "armchair"):
        return sofa_seat_height(host_height) if dtype == "cushion" else host_height
    if host_type == "bookshelf":
        shelves = shelf_heights(host_height)
        return shelves[1] if len(shelves) > 1 else (shelves[0] if shelves else host_height)
    if host_type in BED_TYPES and host_size is not None:
        return round(bedding_top(float(host_size[0]), float(host_size[1]), float(host_height)), 4)
    return host_height


# --------------------------------------------------------------------------
# Bevel radius per part (the Bevel modifier itself is added by furniture.py)
# --------------------------------------------------------------------------

def part_bevel_radius(part: Part) -> float:
    """Bevel radius (metres) of one part: 0 for smooth (superellipsoid) parts
    and glass, ``BEVEL_SOFT_KEYS`` for fabric and bedding, else
    ``BEVEL_BY_ROLE`` / ``BEVEL_BY_KEY`` / ``BEVEL_DEFAULT_M``; never more
    than a third of the part's smallest side (nor ``BEVEL_WIDTH_M``)."""
    if part.get("smooth") or part["key"] == "glass":
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
