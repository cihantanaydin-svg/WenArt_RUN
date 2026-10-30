"""A desk's stationery (30 Oct 2026; user on real04 run 20261030-043021-full, two bedroom desks with bare tops: "A laptop
on this table could have even nice, also some stationary", "Same stationary and laptop here also"; lesson UL164).

What (pure: parts in the item's local frame, bottom on z = 0, the front towards -Y, the user's side): ``stationery_parts``
(the ``stationery`` decor item, one mesh): two closed notebooks lying stacked and a little turned (hard covers over a
cream page block, an elastic band round the upper one), a pen pot (a ceramic cylinder) with pens and pencils standing in
it at slight angles. ``wenart.furniture.tabletop.work_set`` places it on every desk beside its laptop.

Sizes are designer values of real products (assumed): A5 notebooks 21 x 14.8 cm, 1.4-1.8 cm thick; a pen pot 8 cm
across, 10 cm high; pens 14 cm, pencils 17.5 cm. Every part stays inside the item's box (``detail_parts.contain``).
Material keys are the parametric ones (``parametric.MATERIAL_KEYS``): ``dark`` (a black notebook, the pens, the elastic),
``terracotta`` (a second notebook), ``painted`` (the page edges), ``ceramic`` (the pot), ``wood`` (the pencils),
``steel`` (the pens' clips).
"""
from __future__ import annotations

import math
from typing import Optional

Part = dict

STATIONERY_SIZE = (0.30, 0.22, 0.17)          # the item's box (w, d, h): the notebooks and the pot side by side
NOTEBOOK = (0.21, 0.148, 0.016)               # A5, lying: length, width, thickness
POT = (0.04, 0.10)                            # radius, height
PEN_LEN, PENCIL_LEN = 0.14, 0.175
BOARD_M = 0.0018                              # a notebook's cover board


def _notebook(cx: float, cy: float, z0: float, L: float, W: float, T: float, turn_deg: float, cover: str,
              band: bool) -> list[Part]:
    """A closed notebook lying flat: two cover boards over a page block inset on three sides, its spine on -X; an
    elastic band along its length near the fore-edge (``band``); turned ``turn_deg`` about its centre."""
    from wenart.blender.parametric import _box

    b = min(BOARD_M, T * 0.15)
    o = 0.003
    parts = [_box(0.0, 0.0, 0.0, L, W, b, cover, "book"),
             _box(0.0, 0.0, T - b, L, W, b, cover, "book"),
             _box(-L / 2.0 + 0.004, 0.0, b, 0.008, W, T - 2 * b, cover, "book"),          # the spine
             _box(o / 2.0, 0.0, b, L - o, W - 2 * o, T - 2 * b, "painted", "pages")]
    if band:
        parts.append(_box(L / 2.0 - 0.03, 0.0, -0.0005, 0.006, W + 0.002, T + 0.001, "dark", "strap"))
    a = math.radians(turn_deg)
    c, s = math.cos(a), math.sin(a)
    for p in parts:
        p["verts"] = [(cx + x * c - y * s, cy + x * s + y * c, z0 + z) for x, y, z in p["verts"]]
    return parts


def _stick(x: float, y: float, z0: float, length: float, r: float, tilt_deg: float, dir_deg: float, key: str,
           tip_key: str) -> list[Part]:
    """A pen or a pencil standing in the pot: a slim body tilted ``tilt_deg`` towards ``dir_deg`` and its tip end."""
    from wenart.blender.detail_parts import _rod

    a, d = math.radians(tilt_deg), math.radians(dir_deg)
    ux, uy, uz = math.sin(a) * math.cos(d), math.sin(a) * math.sin(d), math.cos(a)
    body = length * 0.9
    p0 = (x, y, z0)
    p1 = (x + ux * body, y + uy * body, z0 + uz * body)
    p2 = (x + ux * length, y + uy * length, z0 + uz * length)
    return [_rod(p0, p1, r, key, "rod", n=6), _rod(p1, p2, r * 0.75, tip_key, "rod", n=6)]


def stationery_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The stationery set in the box ``w x d x h`` (module docstring): the notebooks on the left of the box, the pen
    pot on its right."""
    from wenart.blender.detail_parts import contain
    from wenart.blender.parametric import _cylinder_z

    L, W, T = NOTEBOOK
    nx = -w / 2.0 + W / 2.0 + 0.01               # the notebooks lie turned a quarter: their width along X
    parts = _notebook(nx, -0.005, 0.0, L, W, T, 92.0, "dark", band=True)
    parts += _notebook(nx + 0.006, 0.004, T, L * 0.96, W * 0.96, T * 0.85, 84.0, "terracotta", band=False)
    r, ph = POT
    px, py = w / 2.0 - r - 0.012, 0.02
    parts.append(_cylinder_z(px, py, 0.0, r, r, ph, "ceramic", "body", n=20))
    parts.append(_cylinder_z(px, py, ph - 0.004, r * 0.86, r * 0.86, 0.003, "dark", "groove", n=20))   # its inside
    sticks = ((PEN_LEN, 0.0045, 8.0, 30.0, "dark", "steel"), (PENCIL_LEN, 0.0038, 11.0, 150.0, "wood", "dark"),
              (PEN_LEN * 1.02, 0.0045, 6.0, 260.0, "steel", "dark"), (PENCIL_LEN * 0.95, 0.0038, 13.0, 200.0, "wood",
                                                                     "dark"),
              (PEN_LEN * 0.97, 0.0045, 9.0, 330.0, "dark", "steel"))
    for k, (ln, rr, tilt, ang, key, tip) in enumerate(sticks):
        a = math.radians(ang)
        sx, sy = px + math.cos(a) * r * 0.45, py + math.sin(a) * r * 0.45
        parts += _stick(sx, sy, 0.012, ln, rr, tilt, ang, key, tip)
    return contain(parts, w, d, h)
