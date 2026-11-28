"""The drawn edge ring of a roof-terrace plan (27 Nov 2026, audit fix round 5b, rule R23).

What: ``rings(region)`` lists the closed rings the lines of each layer of a roof-terrace plan close (``polygonize`` per
layer, any layer), larger than ``RING_MIN_M2``, in the sheets frame: ``[{"layer", "points", "area_m2"}]``, largest
first (at most ``RING_MAX``). ``choose(rings, below, core)`` picks the terrace's edge in the building stage: a ring
around the core (it holds the stair house's rooms) whose boundary runs within ``NEAR_M`` of the outline of the floor
below along at least ``NEAR_SHARE`` of its length, its area within ``AREA_RANGE`` of that outline's; the largest such
ring is the edge's outer face, a second one just inside it (within ``DOUBLE_M``) its inner face (the parapet's
thickness). ``wenart.sheets.to_building.roof_terrace`` takes the slab, the terrace rooms and the parapets from it.

Why: real10's TERAS KAT plan draws a continuous double-line parapet ring on layer '0.3' (23.0 x 19.05 m, a 1.30 x
0.70 m slot over the light well, a 1.80 x 2.70 m recess at the escape stair); none of it was read as walls, so the
terrace took the floor below's outline: the light well stayed a hole through the terrace, the stair recess was roofed
and about 90 parapets were inferred on lines nothing draws.

How: pure geometry (shapely); nothing is decided in the sheets stage.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

RING_MIN_M2 = 30.0           # a ring smaller than this is a room, a shaft or a symbol, no terrace edge
RING_MAX = 12
NEAR_M = 1.0                 # the edge runs this close to the outline of the floor below ...
NEAR_SHARE = 0.6             # ... along at least this share of its length (a light well or a recess may differ)
AREA_RANGE = (0.8, 1.4)      # its area within this share of that outline's
DOUBLE_M = 0.40              # a second ring this close inside the edge is its inner face (the parapet's thickness)


def rings(region) -> list:
    """The large rings each layer's lines close (module docstring), sheets frame, largest first."""
    from wenart.sheets import units_check as UC
    tf = region.transform_to_building
    if tf is None:
        return []
    by = defaultdict(list)
    for e in region.ents:
        if getattr(e, "dim", None) is not None:
            continue
        for a, b, _st in UC.segments(e.strokes):
            pa = (tf[0] * a[0] + tf[1] * a[1] + tf[2], tf[3] * a[0] + tf[4] * a[1] + tf[5])
            pb = (tf[0] * b[0] + tf[1] * b[1] + tf[2], tf[3] * b[0] + tf[4] * b[1] + tf[5])
            if pa != pb:
                by[e.layer].append(LineString([pa, pb]))
    out = []
    for layer, lines in by.items():
        try:
            faces = [p for p in polygonize(unary_union(lines)) if p.is_valid]
        except Exception:  # noqa: BLE001 - a layer whose lines do not polygonize closes no ring
            continue
        # 28 Nov 2026 (fix-up, GENERAL-6: a double-line parapet on one layer is a band face whose own area is small):
        # every face's outer ring counts by the area it encloses; its holes are candidate inner faces
        seen = set()
        for p in faces:
            for ring in [p.exterior] + list(p.interiors):
                q = Polygon(ring)
                key = tuple(round(v, 3) for v in q.bounds) + (round(q.area, 2),)
                if q.area < RING_MIN_M2 or key in seen:
                    continue
                seen.add(key)
                out.append({"layer": layer, "area_m2": round(q.area, 3),
                            "points": [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(ring.coords)[:-1]]})
    return sorted(out, key=lambda r: -r["area_m2"])[:RING_MAX]


def _near_share(ring: Polygon, below: Polygon) -> float:
    edge = LineString(ring.exterior.coords)
    near = edge.intersection(below.exterior.buffer(NEAR_M))
    return near.length / edge.length if edge.length > 0 else 0.0


def choose(candidates: list, below: Optional[Polygon], core: list, shift=(0.0, 0.0)) -> Optional[dict]:
    """The terrace's drawn edge (module docstring) in the building frame (``shift`` subtracted), or None:
    ``{"polygon": Polygon, "inner": Polygon | None, "thickness", "layer", "near_share", "area_m2"}``."""
    if below is None or below.is_empty or not candidates:
        return None
    ok = []
    for c in candidates:
        p = Polygon([(x - shift[0], y - shift[1]) for x, y in c["points"]])
        p = p if p.is_valid else p.buffer(0)
        if p.is_empty or p.geom_type != "Polygon":
            continue
        if not AREA_RANGE[0] * below.area <= p.area <= AREA_RANGE[1] * below.area:
            continue
        if core and not all(p.buffer(0.05).contains(Point(q)) for q in core):
            continue
        share = _near_share(p, below)
        if share < NEAR_SHARE:
            continue
        ok.append((p, c, share))
    if not ok:
        return None
    p, c, share = max(ok, key=lambda t: t[0].area)
    inner, thick = None, None
    for q, d, _s in sorted(ok, key=lambda t: -t[0].area):
        if q is p or q.area >= p.area or q.area < 0.85 * p.area:
            continue
        # 28 Nov 2026 (fix-up, GENERAL-6): the inner face by its mean offset (a corner is t * sqrt 2 off, never Hausdorff)
        mean = (p.area - q.area) / max(LineString(p.exterior.coords).length, 1e-9)
        if 0.0 < mean <= DOUBLE_M and p.buffer(0.01).contains(q):
            inner, thick = q, round(max(0.05, mean), 3)
            break
    return {"polygon": p, "inner": inner, "thickness": thick, "layer": c["layer"], "near_share": round(share, 3),
            "area_m2": round(p.area, 3)}
