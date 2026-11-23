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


EMPTY_GAP_ROLES_IGNORED = ("dimension", "text", "axis")   # 23 Nov 2026 (UL372): annotations never close a gap
EMPTY_GAP_END_M = 0.05          # the jambs' own face lines at the gap's ends are no evidence
EMPTY_GAP_MIN_HALF_M = 0.05     # the band looked in: half the wall's thickness, at least this
EMPTY_GAP_ANGLE_DEG = 15.0      # a line along the gap (within this angle) ...
EMPTY_GAP_ALONG_SHARE = 0.25    # ... drawn along this share of it (all such lines together) closes the gap


def gap_drawn(start, end, thickness: float, strokes: list, ignore_roles=EMPTY_GAP_ROLES_IGNORED) -> tuple[bool, str]:
    """23 Nov 2026 (UL372, the dataset bench: 128 of the 142 wide-gap bridges that stood where the truth has no wall
    spanned a gap with nothing drawn in it, against 8 of 35 right ones): whether the drawing shows anything closing a
    wide gap: a line on any layer but an annotation (``EMPTY_GAP_ROLES_IGNORED``) running along the gap
    (``EMPTY_GAP_ANGLE_DEG``) inside the wall's band (half its thickness, ``EMPTY_GAP_MIN_HALF_M`` at least) between
    the jambs (``EMPTY_GAP_END_M`` off each), all such lines together along ``EMPTY_GAP_ALONG_SHARE`` of the gap (a
    sliding door's leaves and tracks, a garage door's line, a glazed screen, a sill, a hatch boundary), or an arc
    reaching the gap's band grown by ``EMPTY_GAP_END_M`` (a door's swing: its hinge at one jamb, its end at the other). ``(drawn, why)``; a line across the gap (a wall or railing running into it, a
    jamb) is no evidence. ``ignore_roles``: the layer roles that are no evidence. Pure; ``strokes`` in the walls'
    frame."""
    from wenart.ingest.generic import layer_names as LN

    L = math.dist(tuple(start), tuple(end))
    if L <= 2 * EMPTY_GAP_END_M + 1e-6:
        return True, "a gap too short to look into"
    ux, uy = (end[0] - start[0]) / L, (end[1] - start[1]) / L
    a = (start[0] + ux * EMPTY_GAP_END_M, start[1] + uy * EMPTY_GAP_END_M)
    b = (end[0] - ux * EMPTY_GAP_END_M, end[1] - uy * EMPTY_GAP_END_M)
    half = max(float(thickness) / 2.0, EMPTY_GAP_MIN_HALF_M)
    band = LineString([a, b]).buffer(half, cap_style=2)
    # a door's swing has its hinge at one jamb and ends at the other, on the wall's face: the whole gap, grown a little
    swing_band = LineString([tuple(start), tuple(end)]).buffer(half + EMPTY_GAP_END_M, cap_style=2)
    sin_max = math.sin(math.radians(EMPTY_GAP_ANGLE_DEG))
    along = 0.0
    layers = set()
    for st in strokes:
        pts = list(getattr(st, "pts", []) or [])
        if len(pts) < 2 or LN.layer_role(getattr(st, "layer", None)) in ignore_roles:
            continue
        line = LineString(pts)
        if getattr(st, "arc", None) or getattr(st, "kind", None) in ("arc", "curve"):
            if line.intersects(swing_band):
                return True, f"an arc on '{getattr(st, 'layer', None)}' reaches it (a door's swing)"
            continue
        if not line.intersects(band):
            continue
        for p, q in zip(pts, pts[1:]):
            n = math.dist(p, q)
            if n <= 1e-9 or abs((q[0] - p[0]) * uy - (q[1] - p[1]) * ux) / n > sin_max:
                continue
            part = LineString([p, q]).intersection(band)
            if not part.is_empty:
                along += part.length
                layers.add(getattr(st, "layer", None))
    if along >= EMPTY_GAP_ALONG_SHARE * L:
        return True, f"lines along it on {sorted(str(x) for x in layers)} ({along:.2f} m of {L:.2f} m)"
    return False, f"nothing drawn along it ({along:.2f} m of {L:.2f} m) and no arc across it"


JOINERY_ROLES = ("window", "door", "glass")
JOINERY_M = (0.6, 8.0)          # a glazed run this long (a window band to a storefront)
JOINERY_REACH_M = 0.35          # ... with a wall within this of each of its ends


def joinery_bridges(walls: list, openings: list, strokes: list) -> list[dict]:
    """2 Nov 2026 (real09: the living rooms' facades to the balconies are glazed runs on 'kapı-pencere' with no wall
    faces; real13: 3.35 m glazed facades on 'KAPI-GOR'): a straight line on a window, door or glass layer
    (``layer_names``), ``JOINERY_M`` long, with a wall within ``JOINERY_REACH_M`` of both its ends and its middle in
    no wall or opening, is a bridge along that line (a glazed wall whose frame the drawing shows instead of wall
    faces). The parallel lines of one frame give one bridge."""
    from wenart.ingest.generic import layer_names as LN

    if len(walls) < 2 or not strokes:
        return []
    polys = [TP.wall_polygon(w) for w in walls]
    tree = STRtree(polys)
    covered = TP.bridged_union(walls, openings)
    out: list[dict] = []
    for st in strokes:
        if getattr(st, "arc", None) or LN.layer_role(getattr(st, "layer", None)) not in JOINERY_ROLES:
            continue
        pts = list(getattr(st, "pts", []) or [])
        if len(pts) < 2:
            continue
        a, b = tuple(pts[0]), tuple(pts[-1])
        L = math.dist(a, b)
        if not (JOINERY_M[0] <= L <= JOINERY_M[1]):
            continue
        if len(pts) > 2 and LineString(pts).length > L * 1.02:
            continue                                       # not straight
        mid = Point((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        if covered.contains(mid):
            continue                                       # a window in a wall gap: the openings reader has it
        near_a = [int(i) for i in tree.query(Point(a).buffer(JOINERY_REACH_M), predicate="intersects")]
        near_b = [int(i) for i in tree.query(Point(b).buffer(JOINERY_REACH_M), predicate="intersects")]
        if not near_a or not near_b:
            continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        start = (a[0] - ux * JOINERY_REACH_M, a[1] - uy * JOINERY_REACH_M)
        end = (b[0] + ux * JOINERY_REACH_M, b[1] + uy * JOINERY_REACH_M)
        k = min(near_a + near_b, key=lambda i: polys[i].distance(mid))
        t = min(float(walls[k].thickness), 0.3)
        if any(LineString([x["start"], x["end"]]).buffer(max(t, 0.3)).contains(mid) for x in out):
            continue                                       # another line of the same frame
        out.append({"wall": k, "start": (round(start[0], 4), round(start[1], 4)),
                    "end": (round(end[0], 4), round(end[1], 4)), "width": round(L, 3), "to": None,
                    "from_free_end": None, "entity": getattr(st, "id", None), "layer": getattr(st, "layer", None),
                    "thickness": t, "rule": "glazed_run"})
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
        if b.get("rule") == "glazed_run":
            reason = (f"the outer walls did not close: a {b['width']:.2f} m glazed run on layer '{b.get('layer')}' "
                      f"between two walls stands where the drawing shows no wall faces (a glazed wall or a "
                      f"storefront)")
            ev.update(rule="glazed_run", reason=reason, entity=b.get("entity") or ev.get("entity"),
                      layer=b.get("layer"))
        walls.append(WallItem(start=b["start"], end=b["end"], thickness=float(b.get("thickness") or a.thickness),
                              box=list(a.box),
                              entity=f"inferred:wide_gap:{n}", evidence=ev, exterior=True, status="unverified",
                              inferred=True))
        (x0, y0), (x1, y1) = b["start"], b["end"]
        rot = math.degrees(math.atan2(y1 - y0, x1 - x0))
        oev = dict(ev)
        openings.append(OpeningItem(kind="opening", width=round(b["width"], 3),
                                    center=(round((x0 + x1) / 2.0, 4), round((y0 + y1) / 2.0, 4)), rotation_deg=rot,
                                    box=list(a.box), entity=f"inferred:wide_gap:{n}", evidence=oev,
                                    status="unverified", type_raw=f"wide gap in the outer wall (rule "
                                                                  f"{b.get('rule') or 'wide_gap'})",
                                    operation="unknown", operation_source="assumed"))
    return walls, openings


def on_outline(b: dict, outline) -> bool:
    """A bridge whose middle lies within ``OUTLINE_TOL_M`` of the building outline's boundary."""
    if outline is None or outline.is_empty:
        return False
    mid = Point((b["start"][0] + b["end"][0]) / 2.0, (b["start"][1] + b["end"][1]) / 2.0)
    return outline.boundary.distance(mid) <= OUTLINE_TOL_M
