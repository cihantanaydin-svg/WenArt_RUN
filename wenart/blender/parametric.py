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
)
DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant")
MATERIAL_KEYS: tuple[str, ...] = ("wood", "fabric", "bedding", "ceramic", "steel", "painted", "worktop", "dark",
                                  "glass", "green", "terracotta")

# How far a handle or a door may stand proud of the footprint (metres);
# the tests allow 1 cm.
PROUD = 0.008
# Largest decor dimension (docs/milestone4.md, Conventions: never larger than 0.6 m).
DECOR_MAX_M = 0.6
DECOR_DEFAULT_HEIGHT = {"cushion": 0.12, "book_set": 0.22, "plant": 0.6}
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

def _bed(w: float, d: float, h: float) -> list[Part]:
    t = min(0.06, d * 0.05)                       # headboard thickness
    frame_h = min(0.3, h * 0.55)
    top = max(1.0, h + 0.4)                        # headboard top
    parts = [
        _box(0.0, 0.0, 0.0, w, d, frame_h, "wood", "body"),
        _box(0.0, d / 2.0 - t / 2.0, 0.0, w, t, top, "wood", "back"),
        _box(0.0, -t / 2.0, frame_h, w - 0.06, d - t - 0.06, h - frame_h, "bedding", "top"),
    ]
    n = 2 if w >= 1.3 else 1
    pw = (w - 0.1) / n - 0.05
    pd = min(0.45, d * 0.22)
    py = d / 2.0 - t - 0.08 - pd / 2.0
    for i in range(n):
        px = 0.0 if n == 1 else (-1 if i == 0 else 1) * (pw / 2.0 + 0.025)
        parts.append(_box(px, py, h, pw, pd, 0.1, "bedding", "pillow"))
    return parts


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
    for c in range(cols):
        cx = -w / 2.0 + cw * (c + 0.5)
        parts.append(_box(cx, front_y + 0.01, plinth_h + 0.01, cw - 0.02, 0.02, h - top_t - plinth_h - 0.03,
                          "painted", "front"))
        parts.append(_box(cx, front_y - PROUD / 2.0, h - top_t - 0.06, min(0.12, cw * 0.5), PROUD, 0.015,
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


_BUILDERS = {
    "bed": _bed, "bed_single": _bed, "bed_double": _bed,
    "sofa": _sofa, "armchair": lambda w, d, h: _sofa(w, d, h, cushions=1),
    "table_dining": _table, "table_coffee": _table, "desk": lambda w, d, h: _table(w, d, h, desk=True),
    "chair": _chair, "wardrobe": _wardrobe, "dresser": _drawers, "nightstand": _drawers, "tv_unit": _tv_unit,
    "bookshelf": _bookshelf, "kitchen_counter": _counter, "kitchen_island": lambda w, d, h: _counter(w, d, h, True),
    "fridge": _fridge, "stove": _stove, "sink_kitchen": _sink, "washbasin": _washbasin, "toilet": _toilet,
    "shower": _shower, "bathtub": _bathtub, "washing_machine": _washing_machine,
}


def build_parts(ftype: str, w: float, d: float, h: float) -> list[Part]:
    """Parts of a parametric piece in its local frame. ``KeyError`` for a
    type without a builder (``unknown`` keeps the proxy box)."""
    try:
        builder = _BUILDERS[ftype]
    except KeyError:
        raise KeyError(f"no parametric builder for furniture type {ftype!r}") from None
    return builder(float(w), float(d), float(h))


# --------------------------------------------------------------------------
# Decor (cushion, book_set, plant)
# --------------------------------------------------------------------------

def decor_size(dtype: str, size) -> tuple[float, float, float]:
    """``(w, d, h)`` of a decor item from its ``size`` (2 or 3 values),
    the type default height, every dimension capped at ``DECOR_MAX_M``."""
    w, d = float(size[0]), float(size[1])
    h = float(size[2]) if len(size) > 2 and size[2] else DECOR_DEFAULT_HEIGHT.get(dtype, 0.2)
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
    raise KeyError(f"no decor builder for {dtype!r}")


def decor_rest_height(host_type: str | None, host_height: float, dtype: str) -> float:
    """Height above the floor where a decor item rests on its host: cushions
    on the sofa seat or the mattress, books on a shelf or a top, plants on
    the floor."""
    if dtype == "plant" or not host_type:
        return 0.0
    if host_type in ("sofa", "armchair"):
        return sofa_seat_height(host_height) if dtype == "cushion" else host_height
    if host_type == "bookshelf":
        shelves = shelf_heights(host_height)
        return shelves[1] if len(shelves) > 1 else (shelves[0] if shelves else host_height)
    return host_height


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


def parametric_bbox(ftype: str, w: float, d: float, h: float) -> tuple[float, float, float]:
    """``(width, depth, height)`` of the parametric mesh (its real box)."""
    x0, y0, z0, x1, y1, z1 = _bbox(build_parts(ftype, w, d, h))
    return (x1 - x0, y1 - y0, z1 - z0)


def piece_bbox(piece: dict) -> tuple[float, float, float, str]:
    """``(width, depth, height, source)`` of the box a piece occupies in its
    own frame, as the scene will build it: the catalogue box times the fit
    scale for a fitted library asset, the parametric box otherwise, the
    proxy box for ``unknown``. The camera planner uses this (docs/
    milestone4.md §2: free points from fitted boxes, not only footprints)."""
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    h, _ = proxy_height(piece["type"], piece.get("height"))
    asset = piece.get("asset") or {}
    if asset.get("method") == "library" and asset.get("bbox_m"):
        sx, sy, sz = (list(asset.get("fit_scale") or [1.0, 1.0, 1.0]) + [1.0, 1.0, 1.0])[:3]
        bw, bd, bh = (float(v) for v in asset["bbox_m"][:3])
        return (bw * float(sx), bd * float(sy), bh * float(sz), "library")
    if piece["type"] in _BUILDERS:
        bw, bd, bh = parametric_bbox(piece["type"], w, d, h)
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
