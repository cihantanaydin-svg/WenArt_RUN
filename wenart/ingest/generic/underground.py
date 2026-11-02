"""A level fully below ground: walled all round, no opening to the outside (2 Nov 2026).

What: ``close_underground(ex, to_building)`` for one level's extraction: when soil labels (``SOIL_RE``: TOPRAK,
"SIKIŞTIRILMIŞ TOPRAK", soil, earth, Erdreich, terre, terreno, dolgu, backfill ...) lie outside its walls on at least
``SOIL_SIDES_MIN`` sides of the building, the level is underground:
- a gap of up to ``GAP_MAX_M`` in its outer wall ring is closed by an inferred wall between the two wall ends (the
  thickness of the thinner one), evidence method ``inferred``;
- every door, window or opening on that ring is removed (an underground wall has no opening to the soil);
it returns the note for the report (None when the level is not underground).

Why: real10's 2nd basement (user: "2n basement is fully underground and fully walled around", "For the second
basement you can enter like this, first from the stairs and than from the door", "Project should be able to understand
this"): the drawing leaves a 1.9 m gap in the right outer wall at its GİRİŞ arrow and draws vents in the top wall; the
model left the passage from the stair to the shelter door open to the outside (no room) and kept the openings.

How: pure on the extraction's walls (building metres) and texts (page units, ``to_building`` maps them).
"""
from __future__ import annotations

import math
import re
from typing import Callable, Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart.ingest.generic import topology as TP

SOIL_RE = re.compile(r"\b(TOPRAK|TOPRAGI|SOIL|EARTH|ERDREICH|ERDE|TERRE|TERRENO|TERRA|DOLGU|BACKFILL)\b")
SOIL_SIDES_MIN = 3
GAP_MAX_M = 3.5
GAP_MIN_M = 0.3
END_REACH_M = 0.8                     # a gap's ends: wall ends this close to them
RING_TOL_M = 0.10                     # an opening this close to the outer ring (beyond its wall's half thickness)


def _fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).upper().split())


def soil_sides(ex, to_building: Callable, outline: Polygon) -> set:
    """The sides (W, E, S, N of the outline's box) with a soil label outside the outline."""
    if outline.is_empty:
        return set()
    x0, y0, x1, y1 = outline.bounds
    sides = set()
    for t in list(getattr(ex, "texts", []) or []) + list(getattr(ex, "labels", []) or []):
        if not SOIL_RE.search(_fold(t.text)):
            continue
        b = t.box
        p = to_building(((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0))
        if outline.contains(Point(p)):
            continue
        dx = min(abs(p[0] - x0), abs(p[0] - x1))
        dy = min(abs(p[1] - y0), abs(p[1] - y1))
        if dx <= dy:
            sides.add("W" if abs(p[0] - x0) < abs(p[0] - x1) else "E")
        else:
            sides.add("S" if abs(p[1] - y0) < abs(p[1] - y1) else "N")
    return sides


def _ends(walls) -> list:
    out = []
    for w in walls:
        out.append((tuple(w.start), w))
        out.append((tuple(w.end), w))
    return out


def close_underground(ex, to_building: Callable) -> Optional[str]:
    """The module docstring; changes ``ex.walls`` and ``ex.openings`` in place."""
    from wenart.ingest.model import WallItem

    walls = list(ex.walls)
    if not walls:
        return None
    union = unary_union([TP.wall_polygon(w) for w in walls])
    closed = union.buffer(GAP_MAX_M / 2.0, join_style=2).buffer(-GAP_MAX_M / 2.0, join_style=2)
    parts = list(getattr(closed, "geoms", [closed]))
    if not parts:
        return None
    outline = Polygon(max(parts, key=lambda p: p.area).exterior)
    sides = soil_sides(ex, to_building, outline)
    if len(sides) < SOIL_SIDES_MIN:
        return None
    ring = LineString(outline.exterior.coords)
    uncovered = ring.difference(union.buffer(0.05))
    pieces = [g for g in getattr(uncovered, "geoms", [uncovered]) if g.length >= GAP_MIN_M]
    ends = _ends(walls)
    added = []
    for g in pieces:
        if g.length > GAP_MAX_M * 1.5:
            continue
        a, b = g.coords[0], g.coords[-1]
        ea = min(ends, key=lambda e: math.dist(e[0], a))
        eb = min((e for e in ends if e[1] is not ea[1]), key=lambda e: math.dist(e[0], b), default=None)
        if eb is None or math.dist(ea[0], a) > END_REACH_M + ea[1].thickness or \
                math.dist(eb[0], b) > END_REACH_M + eb[1].thickness:
            continue
        span = math.dist(ea[0], eb[0])
        if not (GAP_MIN_M <= span <= GAP_MAX_M):
            continue
        t = min(float(ea[1].thickness), float(eb[1].thickness))
        # the evidence of the wall it continues (file, page, entity), as inferred with the rule and the reason
        ev = dict(ea[1].evidence or {})
        ev.update(method="inferred", confidence=0.7, rule="underground_level",
                  reason=f"a level fully below ground (soil outside on {len(sides)} sides): the {span:.2f} m gap in "
                         f"its outer wall closed")
        w = WallItem(start=(round(ea[0][0], 4), round(ea[0][1], 4)), end=(round(eb[0][0], 4), round(eb[0][1], 4)),
                     thickness=t, box=list(ea[1].box), entity=f"inferred:underground:{len(added) + 1}", evidence=ev,
                     exterior=True, status="unverified", inferred=True)
        ex.walls.append(w)
        added.append(span)
    union = unary_union([TP.wall_polygon(w) for w in ex.walls])
    closed = union.buffer(GAP_MAX_M / 2.0, join_style=2).buffer(-GAP_MAX_M / 2.0, join_style=2)
    parts = list(getattr(closed, "geoms", [closed]))
    ring = LineString(Polygon(max(parts, key=lambda p: p.area).exterior).exterior.coords)
    kept, removed = [], []
    for o in ex.openings:
        if getattr(o, "virtual", False):
            kept.append(o)
            continue
        c = Point(o.center)
        host = min(ex.walls, key=lambda w: LineString([tuple(w.start), tuple(w.end)]).distance(c))
        if ring.distance(c) <= float(host.thickness) / 2.0 + RING_TOL_M:
            removed.append(o)
        else:
            kept.append(o)
    ex.openings = kept
    return (f"a level fully below ground (soil labels outside its walls on {len(sides)} sides: "
            f"{', '.join(sorted(sides))}): {len(added)} gap(s) in its outer walls closed "
            f"({', '.join(f'{s:.2f} m' for s in added) or 'none'}), {len(removed)} opening(s) to the soil removed "
            f"({', '.join(sorted({o.kind for o in removed})) or 'none'}); it is entered from the stair core")
