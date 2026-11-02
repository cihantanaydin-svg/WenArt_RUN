"""Wide openings in the outer walls (2 Nov 2026; user: "improve the best of your abilities the initial reading phase").

What: ``bridges(walls)`` -> the candidate bridges of a plan whose outer walls do not close: from every free wall end
(an end touching no other wall within ``FREE_END_M``), or from a corner along the wall running on past it, a band of
the wall's thickness reaches the next wall within ``WIDE_GAP_M``; when the band meets that wall at its free end (the
other jamb), the band up to it is a bridge. ``apply(walls, openings, chosen)`` adds each
chosen bridge as an inferred wall (evidence of the wall it continues, method ``inferred``, rule ``wide_gap``, status
``unverified``) carrying an unverified opening as wide as the gap (``kind`` opening, ``type_raw`` naming the rule).
The caller (``core``) keeps only the bridges on the building's outline and only when they close in more labelled
rooms (``outer_gaps`` there).

Why: real07 (a villa, ground floor): the 1.9 m sliding door to the terrace ('SÜRGÜ KAPI', two leaves on tracks and no
swing), the 3.6 m garage door (from the end of the front wall to the corner of the side wall) and the entrance were
gaps without a symbol the openings reader knows, wider than its run gaps (``openings.GAP_MAX_M``, 3 m) or between two
walls of different directions: the outer walls never closed and the whole floor was left out. A wide gap in the outer
ring is an opening whose kind the drawing does not say; the floor is kept and the opening listed.

How: pure geometry on ``WallItem``s (building metres).
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

from wenart.ingest.generic import topology as TP

WIDE_GAP_M = (0.5, 6.0)         # a bridge spans this much (a sliding door to a double garage door)
FREE_END_M = 0.05               # a wall end touching no other wall within this is free
OVERLAP_M = 0.01                # a bridge reaches this far into the wall it meets
END_REACH_M = 0.15              # ... at its free end: the free end within this of the band (beyond both half widths)
OUTLINE_TOL_M = 0.35            # the caller keeps a bridge whose middle lies this close to the building's outline


def _ends(walls: list, polys: list, tree) -> list:
    """``[(k, end_point, direction, touching)]``: every wall end, the direction pointing out of the wall, and the walls
    it touches (within ``FREE_END_M``; none: a free end)."""
    out = []
    for k, w in enumerate(walls):
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= 1e-9:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        for p, d in (((x1, y1), (ux, uy)), ((x0, y0), (-ux, -uy))):
            probe = Point(p).buffer(FREE_END_M + float(w.thickness) / 2.0)
            near = {int(i) for i in tree.query(probe, predicate="intersects") if int(i) != k}
            # a piece of the same run lying behind the end (real07: the garage wall's last 5 cm as its own piece) does
            # not hold the end
            near = {i for i in near if not (_straight_on(walls[i], d) and _ahead(walls[i], p, d) <= FREE_END_M)}
            out.append((k, p, d, near))
    return out


def _ahead(w, p, u) -> float:
    """How far a wall reaches ahead of point ``p`` in direction ``u``."""
    return max((q[0] - p[0]) * u[0] + (q[1] - p[1]) * u[1] for q in (tuple(w.start), tuple(w.end)))


def _straight_on(w, u) -> bool:
    """A wall running on in direction ``u`` (parallel within about 5 degrees)."""
    (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
    L = math.hypot(x1 - x0, y1 - y0)
    return L > 1e-9 and abs((x1 - x0) / L * u[1] - (y1 - y0) / L * u[0]) < 0.09


def bridges(walls: list) -> list[dict]:
    """The candidate bridges (the module docstring): ``{"wall": k, "start", "end", "width", "to": j}``. A bridge
    starts at a free wall end, or at a corner by running on along the wall past it, and ends at a free end of the
    wall it meets (``END_REACH_M``): the two jambs of one opening. A band that meets a wall's side instead (a hall
    wall run on to the kitchen wall, a facade run on to a garden wall) is no opening."""
    if len(walls) < 2:
        return []
    polys = [TP.wall_polygon(w) for w in walls]
    tree = STRtree(polys)
    ends = _ends(walls, polys, tree)
    free = {}
    for k, p, d, near in ends:
        if not near:
            free.setdefault(k, []).append(p)
    out: list[dict] = []
    ends.sort(key=lambda e: bool(e[3]))                    # free ends first: their bridge is the opening itself
    for k, p, (ux, uy), near in ends:
        t = float(walls[k].thickness)
        if near and any(_straight_on(walls[i], (ux, uy)) for i in near):
            continue                                       # a joint in one wall run, not a corner
        far = (p[0] + ux * WIDE_GAP_M[1], p[1] + uy * WIDE_GAP_M[1])
        band = LineString([p, far]).buffer(t / 2.0, cap_style=2)
        axis = LineString([p, far])
        hits = []
        for j in tree.query(band, predicate="intersects"):
            j = int(j)
            if j == k or j in near:
                continue
            hit = band.intersection(polys[j])
            if hit.is_empty:
                continue
            pts = [c for g in getattr(hit, "geoms", [hit]) for c in getattr(getattr(g, "exterior", g), "coords", [])]
            if not pts:
                continue
            dist = min((q[0] - p[0]) * ux + (q[1] - p[1]) * uy for q in pts)
            if dist > 1e-6:
                hits.append((dist, j))
        if not hits:
            continue
        d = min(hits)[0]
        if not (WIDE_GAP_M[0] <= d <= WIDE_GAP_M[1]):
            continue
        met = [j for dist, j in hits if dist <= d + FREE_END_M]
        if not any(axis.distance(Point(q)) <= (t + float(walls[j].thickness)) / 2.0 + END_REACH_M
                   for j in met for q in free.get(j, [])):
            continue                                       # the band meets a wall's side, not its free end
        j = met[0]
        end = (p[0] + ux * (d + OVERLAP_M), p[1] + uy * (d + OVERLAP_M))
        mid = Point((p[0] + end[0]) / 2.0, (p[1] + end[1]) / 2.0)
        if any(LineString([b["start"], b["end"]]).buffer(t / 2.0 + 0.05).contains(mid) for b in out):
            continue                                       # the same gap seen from its other end
        out.append({"wall": k, "start": (round(p[0], 4), round(p[1], 4)), "end": (round(end[0], 4), round(end[1], 4)),
                    "width": round(d, 3), "to": j, "from_free_end": not near})
    return out


def apply(walls: list, openings: list, chosen: list[dict]) -> tuple[list, list]:
    """``(walls, openings)`` with the chosen bridges as inferred walls carrying unverified openings."""
    from wenart.ingest.model import OpeningItem, WallItem

    walls, openings = list(walls), list(openings)
    for n, b in enumerate(chosen, start=1):
        a = walls[b["wall"]]
        reason = (f"the outer walls did not close: a {b['width']:.2f} m gap from the free end of a wall to the next "
                  f"wall along its axis is an opening whose kind the drawing does not say (a sliding door, a garage "
                  f"door or an entrance)")
        ev = dict(a.evidence or {})
        ev.update(method="inferred", confidence=0.6, rule="wide_gap", reason=reason)
        walls.append(WallItem(start=b["start"], end=b["end"], thickness=float(a.thickness), box=list(a.box),
                              entity=f"inferred:wide_gap:{n}", evidence=ev, exterior=True, status="unverified",
                              inferred=True))
        (x0, y0), (x1, y1) = b["start"], b["end"]
        rot = math.degrees(math.atan2(y1 - y0, x1 - x0))
        oev = dict(ev)
        openings.append(OpeningItem(kind="opening", width=round(b["width"], 3),
                                    center=(round((x0 + x1) / 2.0, 4), round((y0 + y1) / 2.0, 4)), rotation_deg=rot,
                                    box=list(a.box), entity=f"inferred:wide_gap:{n}", evidence=oev,
                                    status="unverified", type_raw="wide gap in the outer wall (rule wide_gap)",
                                    operation="unknown", operation_source="assumed"))
    return walls, openings


def on_outline(b: dict, outline) -> bool:
    """A bridge whose middle lies within ``OUTLINE_TOL_M`` of the building outline's boundary."""
    if outline is None or outline.is_empty:
        return False
    mid = Point((b["start"][0] + b["end"][0]) / 2.0, (b["start"][1] + b["end"][1]) / 2.0)
    return outline.boundary.distance(mid) <= OUTLINE_TOL_M
