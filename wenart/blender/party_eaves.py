"""No eaves on a party side (12 Nov 2026; stage 2 of the building-sense audit, R46: "Party walls get no openings and no
eaves overhang").

What: ``clip(outline, building, level_id)`` cuts a roof outline that the builder grew from the walls by the overhang
(``roof.py``, no roof outline drawn) back to the outer face line of every external party wall of that level
(``party_wall`` on the wall, not ``internal``): the neighbour's building stands there, so the eaves stop at the line.
A drawn roof outline is never clipped (the builder does not call this then). Returns ``(outline, notes)``.

Why: real21's two attached sides: a pitched or overhanging roof must not reach over the neighbour's plot.

How: pure (shapely): the outline is intersected with the half-plane on the building's side of each party line.
"""
from __future__ import annotations

import math
from typing import Sequence

from shapely.geometry import Polygon


def clip(outline: Sequence, building: dict, level_id) -> tuple:
    """The module docstring."""
    if not outline or len(outline) < 3 or not level_id:
        return list(outline or []), []
    poly = Polygon([tuple(p[:2]) for p in outline]).buffer(0)
    if poly.is_empty:
        return list(outline), []
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level_id
             and isinstance(w.get("party_wall"), dict) and not w["party_wall"].get("internal")
             and w.get("start") and w.get("end")]
    if not walls:
        return list(outline), []
    rooms = [Polygon(r["polygon"]) for r in building.get("rooms") or []
             if r.get("level_id") == level_id and len(r.get("polygon") or []) >= 3]
    inside = Polygon(poly.exterior).centroid if not rooms else \
        Polygon(max(rooms, key=lambda p: p.area).exterior).centroid
    notes = []
    big = 1e4
    for w in walls:
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 0.3:
            continue
        u = ((x1 - x0) / length, (y1 - y0) / length)
        n = (-u[1], u[0])
        side = 1.0 if (inside.x - x0) * n[0] + (inside.y - y0) * n[1] > 0 else -1.0
        # the wall's outer face line: the axis moved half the thickness away from the building
        off = -side * float(w.get("thickness") or 0.15) / 2.0
        ox, oy = x0 + n[0] * off, y0 + n[1] * off
        half = Polygon([(ox - u[0] * big, oy - u[1] * big), (ox + u[0] * big, oy + u[1] * big),
                        (ox + u[0] * big + n[0] * side * big, oy + u[1] * big + n[1] * side * big),
                        (ox - u[0] * big + n[0] * side * big, oy - u[1] * big + n[1] * side * big)])
        cut = poly.intersection(half)
        if cut.is_empty or cut.geom_type != "Polygon" or cut.area >= poly.area - 1e-4:
            continue
        notes.append(f"eaves cut at the party wall {w['id']}'s outer face ({poly.area - cut.area:.2f} m2 of overhang "
                     f"removed: no eaves over the neighbour, R46)")
        poly = cut
    return [(round(x, 4), round(y, 4)) for x, y in list(poly.exterior.coords)[:-1]], notes
