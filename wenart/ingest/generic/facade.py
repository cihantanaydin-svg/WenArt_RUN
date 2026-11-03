"""Facades of glass and joinery (3 Nov 2026; user: "go ahead with the glazed facades").

What: ``close_rooms(walls, strokes, anchors)`` -> the faces of rooms whose walls do not close, closed along their
glazed facades, and ``facade_walls(walls, faces)`` -> the inferred walls on the parts of those faces where no wall
stands (the caller reads the windows and doors drawn across them with ``openings.openings_on_walls``: nothing is
invented).

- *Material*: the walls and the lines of the window, door and glass layers (``layer_names``; no swing arcs), each line
  a band ``BAND_M`` wide (a frame stands in a wall's place).
- *Links*: from each open room's label ``RAYS`` rays are cast; a run of rays that escapes (no material within
  ``REACH_M``) leaves through a gap; the two hit points beside the run bound it, and a gap of at most ``LINK_M`` is
  linked by a band (a piece of wall the drawing shows on another layer, or not at all, between two frames). Rounds
  repeat until the label is closed in or nothing more links (``ROUNDS``).
- *Face*: the hole of material and links holding the label. A face larger than ``MAX_FACE_M2`` is no room.
- *Walls*: each straight piece of a face's boundary that lies on no drawn wall (and on no other closed face's wall
  already made) becomes an inferred wall, its face side on the boundary, ``thickness`` that of the drawn walls the face
  touches (median), evidence of the nearest drawn wall with method ``inferred``, rule ``glazed_facade``.

Why: real09, real11, real13, real14: the living rooms' facades are runs of windows and balcony doors on 'kapı-pencere'
/ 'KAPI-GOR', a column and short wall pieces on layers that are no wall layer: no wall face, so the walls never
closed and every floor was left out. Bridging one gap at a time (``wide_gaps``) cannot follow a facade of frames,
doors and short pieces; a dilate-and-erode closing bridges straight gaps along the axes only (an L-shaped gap between a
balcony door and a window stays open).

How: pure geometry in page metres.
"""
from __future__ import annotations

import math
import statistics
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

from wenart.ingest.generic import topology as TP

JOINERY_ROLES = ("window", "door", "glass")
BAND_M = 0.24                   # a frame line as a band this wide
MIN_LINE_M = 0.15               # shorter joinery lines (hinge ticks, handles) are left out
LEAF_END_M = 0.05               # a line ending this close to a swing arc's end is a door leaf
AXIS_TOL_DEG = 5.0              # frame lines run along or across the plan's walls within this
RAYS = 360
REACH_M = 30.0
LINK_M = 1.6                    # a gap a room's rays escape through is linked up to this wide
LINK_BAND_M = 0.2
SLIT_M = 0.12                   # slits narrower than twice this (a frame stopping short of a wall) are closed
ROUNDS = 4
MAX_FACE_M2 = 400.0             # a closed face larger than this is no room (a courtyard, the whole site)
ON_WALL_M = 0.06                # a face edge this close to a drawn wall lies on it
MIN_PIECE_M = 0.25              # a free stretch of a face's edge shorter than this makes no wall ...
MIN_SEGMENT_M = 0.02            # ... but within a longer stretch every segment does (no gap is left at a step)
SIMPLIFY_M = 0.06
DEFAULT_T_M = 0.2


def joinery_lines(strokes: list, theta: Optional[float] = None) -> list:
    """The frame lines of the window, door and glass layers, page metres: no swing arcs, no door leaf (a straight
    line from the end of a swing arc), and, given the plan's dominant wall direction ``theta`` (degrees), only lines
    along it or across it within ``AXIS_TOL_DEG`` (a casement drawn open stands at an angle into the room)."""
    from wenart.ingest.generic import layer_names as LN

    joinery = [st for st in strokes or [] if LN.layer_role(getattr(st, "layer", None)) in JOINERY_ROLES]
    arc_ends = []
    for st in joinery:
        pts = getattr(st, "pts", None) or []
        if getattr(st, "arc", None) and len(pts) >= 2:
            arc_ends += [tuple(pts[0]), tuple(pts[-1])]
    out = []
    for st in joinery:
        if getattr(st, "arc", None):
            continue
        pts = [tuple(p) for p in (getattr(st, "pts", None) or [])]
        if len(pts) < 2:
            continue
        line = LineString(pts)
        if line.length < MIN_LINE_M:
            continue
        a, b = pts[0], pts[-1]
        if any(math.dist(a, q) <= LEAF_END_M or math.dist(b, q) <= LEAF_END_M for q in arc_ends):
            continue                                       # a door leaf
        if theta is not None:
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            off = abs((ang - theta + 45.0) % 90.0 - 45.0)
            if off > AXIS_TOL_DEG:
                continue                                   # a leaf drawn open
        out.append(line)
    return out


def material(walls: list, lines: list) -> list:
    """The pieces of material: the wall rectangles and the joinery bands."""
    polys = [TP.wall_polygon(w) for w in walls]
    polys += [ln.buffer(BAND_M / 2.0, cap_style=3, join_style=2) for ln in lines]     # square ends: a frame's jamb
    return [p for p in polys if p is not None and not p.is_empty]


def _hit(tree, pieces, origin, angle) -> Optional[tuple[float, tuple]]:
    ox, oy = origin
    ray = LineString([origin, (ox + REACH_M * math.cos(angle), oy + REACH_M * math.sin(angle))])
    best = None
    for i in tree.query(ray, predicate="intersects"):
        inter = ray.intersection(pieces[int(i)])
        for g in getattr(inter, "geoms", [inter]):
            for c in getattr(getattr(g, "exterior", g), "coords", []):
                d = math.hypot(c[0] - ox, c[1] - oy)
                if best is None or d < best[0]:
                    best = (d, (c[0], c[1]))
    return best


def _axis_link(p1, p2, anchor, theta: Optional[float]):
    """The link of a gap: straight when it runs along or across the walls; else an L along the walls' two directions
    with its corner on the side away from the room (``anchor``): the facade turns a corner there."""
    if theta is None:
        return LineString([p1, p2])
    t = math.radians(theta)
    c, s = math.cos(t), math.sin(t)
    to = lambda p: (p[0] * c + p[1] * s, -p[0] * s + p[1] * c)          # noqa: E731 - into the walls' frame
    back = lambda q: (q[0] * c - q[1] * s, q[0] * s + q[1] * c)         # noqa: E731
    a, b = to(p1), to(p2)
    dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
    if min(dx, dy) <= math.tan(math.radians(AXIS_TOL_DEG)) * max(dx, dy):
        return LineString([p1, p2])
    corners = [back((a[0], b[1])), back((b[0], a[1]))]
    corner = max(corners, key=lambda q: math.dist(q, anchor))
    return LineString([p1, corner, p2])


def gap_links(pieces: list, anchor, theta: Optional[float] = None) -> list:
    """The links of the gaps the rays from ``anchor`` escape through (the module docstring)."""
    if not pieces:
        return []
    tree = STRtree(pieces)
    if any(pieces[int(i)].contains(Point(anchor)) for i in tree.query(Point(anchor))):
        return []                                          # the label stands in material
    hits = [_hit(tree, pieces, anchor, 2.0 * math.pi * k / RAYS) for k in range(RAYS)]
    if all(h is None for h in hits) or all(h is not None for h in hits):
        return []
    links = []
    k0 = next(k for k in range(RAYS) if hits[k] is not None)
    k = k0
    seen = 0
    while seen < RAYS:
        j = (k + 1) % RAYS
        if hits[k] is not None and hits[j] is None:
            # an escape run starts after k; it ends before the next ray with a hit
            m = j
            steps = 0
            while hits[m] is None and steps < RAYS:
                m = (m + 1) % RAYS
                steps += 1
            p1, p2 = hits[k][1], hits[m][1]
            if math.dist(p1, p2) <= LINK_M:
                links.append(_axis_link(p1, p2, anchor, theta))
        k = j
        seen += 1
    return links


def face_of(pieces: list, anchor) -> Optional[Polygon]:
    """The hole of the material holding ``anchor`` (None when the label is in no hole or the hole is no room)."""
    u = unary_union(pieces)
    u = unary_union([u, u.buffer(SLIT_M, join_style=2).buffer(-SLIT_M, join_style=2)])   # slits a ray cannot see
    pt = Point(anchor)
    for part in getattr(u, "geoms", [u]):
        if part.geom_type != "Polygon":
            continue
        for ring in part.interiors:
            hole = Polygon(ring)
            if hole.contains(pt):
                return hole if hole.area <= MAX_FACE_M2 else None
    return None


def close_rooms(walls: list, strokes: list, anchors: list) -> tuple[dict, list]:
    """``({anchor index: face}, links)``: the faces of the open rooms the links close and the link lines (the module
    docstring)."""
    from wenart.ingest.generic import openings as O

    theta = O.dominant_angle(walls) if walls else None
    lines = joinery_lines(strokes, theta)
    pieces = material(walls, lines)
    faces: dict = {}
    links_all: list = []
    for k, anchor in enumerate(anchors):
        local = list(pieces)
        face = face_of(local, anchor)
        rounds = 0
        while face is None and rounds < ROUNDS:
            links = gap_links(local, anchor, theta)
            if not links:
                break
            local += [ln.buffer(LINK_BAND_M / 2.0, cap_style=2, join_style=2) for ln in links]
            links_all += links
            face = face_of(local, anchor)
            rounds += 1
        if face is not None:
            faces[k] = face
    return faces, links_all


def _straight_pieces(line) -> list:
    """The straight segments of a (simplified) boundary piece."""
    simple = line.simplify(SIMPLIFY_M)
    coords = list(simple.coords)
    return [(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]


def facade_walls(walls: list, faces: list, openings: list = ()) -> list[dict]:
    """``[{"start", "end", "thickness", "near"}]``: the inferred walls on the parts of the faces' boundaries where no
    drawn wall or opening stands (the module docstring); ``near`` = the index of the nearest drawn wall (its
    evidence)."""
    if not walls or not faces:
        return []
    polys = [TP.wall_polygon(w) for w in walls]
    drawn = TP.bridged_union(walls, openings).buffer(ON_WALL_M, join_style=2)
    tree = STRtree(polys)
    out: list[dict] = []
    made = []
    for face in faces:
        touching = [float(walls[int(i)].thickness) for i in tree.query(face.buffer(ON_WALL_M), predicate="intersects")]
        t = statistics.median(touching) if touching else DEFAULT_T_M
        t = min(max(t, 0.1), 0.35)
        free = LineString(face.exterior.coords).difference(drawn)
        for g in getattr(free, "geoms", [free]):
            if g.is_empty or g.length < MIN_PIECE_M:
                continue
            for a, b in _straight_pieces(g):
                L = math.dist(a, b)
                if L < MIN_SEGMENT_M:
                    continue
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                nx, ny = -uy, ux
                mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
                if face.contains(Point(mid[0] + nx * 0.02, mid[1] + ny * 0.02)):
                    nx, ny = -nx, -ny                       # the normal pointing out of the room
                off = t / 2.0
                ext = ON_WALL_M + t / 2.0                    # into the neighbouring walls (and over the corners)
                s = (a[0] + nx * off - ux * ext, a[1] + ny * off - uy * ext)
                e = (b[0] + nx * off + ux * ext, b[1] + ny * off + uy * ext)
                seg = LineString([s, e])
                if any(m.distance(seg) < t / 2.0 and m.buffer(t).contains(seg.interpolate(0.5, normalized=True))
                       for m in made):
                    continue                                # the neighbouring room made this wall already
                near = min(range(len(polys)), key=lambda i: polys[i].distance(Point(mid)))
                out.append({"start": (round(s[0], 4), round(s[1], 4)), "end": (round(e[0], 4), round(e[1], 4)),
                            "thickness": round(t, 3), "near": near, "length": round(L, 3)})
                made.append(seg)
    return out


def to_walls(walls: list, rows: list[dict]) -> list:
    """The inferred ``WallItem``s of ``facade_walls`` rows."""
    from wenart.ingest.model import WallItem

    out = []
    for n, r in enumerate(rows, start=1):
        a = walls[r["near"]]
        ev = dict(a.evidence or {})
        ev.update(method="inferred", confidence=0.6, rule="glazed_facade",
                  reason=(f"the room's walls did not close: its facade is drawn as window, door and glass frames and "
                          f"short pieces on other layers; a {r['length']:.2f} m wall inferred where the frames stand"))
        out.append(WallItem(start=r["start"], end=r["end"], thickness=float(r["thickness"]), box=list(a.box),
                            entity=f"inferred:glazed_facade:{n}", evidence=ev, exterior=True, status="unverified",
                            inferred=True))
    return out


FRAME_COVER_M = 0.6             # frames along a facade wall covering this much (and no symbol read) make a window
DOOR_RADIUS_M = (0.75, 1.3)     # ... a door when a swing of this radius on a door / window layer (a casement's
                                # swing is 0.4-0.7 m: real09) ...
SWING_REACH_M = 0.35            # ... is hinged within this of the wall band and of the frames' extent


def frame_windows(new_walls: list, strokes: list, read: list, walls: list) -> list:
    """Unverified windows on the inferred facade walls where frame lines run along them and the openings reader read no
    door or window symbol there: the frames' extent along the wall (at least ``FRAME_COVER_M``)."""
    from wenart.ingest.generic import openings as O
    from wenart.ingest.model import OpeningItem

    from wenart.ingest.generic import layer_names as LN

    lines = joinery_lines(strokes, O.dominant_angle(walls) if walls else None)
    swings = [(tuple(st.arc["center"]), float(st.arc["radius"])) for st in strokes or []
              if getattr(st, "arc", None) and LN.layer_role(getattr(st, "layer", None)) in JOINERY_ROLES
              and DOOR_RADIUS_M[0] <= float(st.arc["radius"]) <= DOOR_RADIUS_M[1]]
    out = []
    for n, w in enumerate(new_walls, start=1):
        (x0, y0), (x1, y1) = tuple(w.start), tuple(w.end)
        L = math.hypot(x1 - x0, y1 - y0)
        if L < FRAME_COVER_M:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        band = LineString([(x0, y0), (x1, y1)]).buffer(float(w.thickness) / 2.0 + BAND_M / 2.0, cap_style=2)
        spans = []
        for ln in lines:
            part = ln.intersection(band)
            if part.is_empty or part.length < MIN_LINE_M:
                continue
            for g in getattr(part, "geoms", [part]):
                cs = list(getattr(g, "coords", []))
                if len(cs) < 2:
                    continue
                ts = [(c[0] - x0) * ux + (c[1] - y0) * uy for c in cs]
                if abs(max(ts) - min(ts)) >= 0.8 * g.length:          # along the wall
                    spans.append((max(0.0, min(ts)), min(L, max(ts))))
        if not spans:
            continue
        lo, hi = min(a for a, _ in spans), max(b for _, b in spans)
        if hi - lo < FRAME_COVER_M:
            continue
        mine = LineString([(x0, y0), (x1, y1)]).buffer(float(w.thickness))
        if any(mine.contains(Point(o.center)) for o in read):
            continue                                       # the reader read this wall's opening
        c = ((lo + hi) / 2.0)
        # a swing hinged on the wall within the frames' extent: a door (a balcony door), else a window
        reach = float(w.thickness) / 2.0 + SWING_REACH_M
        door = any(abs(-(q[0] - x0) * uy + (q[1] - y0) * ux) <= reach
                   and lo - SWING_REACH_M <= (q[0] - x0) * ux + (q[1] - y0) * uy <= hi + SWING_REACH_M
                   for q, _r in swings)
        kind = "door" if door else "window"
        ev = dict(w.evidence or {})
        ev.update(rule="glazed_facade", reason=(f"{'door' if door else 'window'} frames drawn along the inferred facade "
                                                f"wall{' with a door swing hinged on it' if door else ''}, no symbol "
                                                f"the openings reader knows: an unverified {kind} as wide as the "
                                                f"frames"))
        out.append(OpeningItem(kind=kind, width=round(hi - lo, 3),
                               center=(round(x0 + ux * c, 4), round(y0 + uy * c, 4)),
                               rotation_deg=math.degrees(math.atan2(uy, ux)), box=list(w.box),
                               entity=f"inferred:glazed_facade_{kind}:{n}", evidence=ev, status="unverified",
                               type_raw=f"{kind} frames on an inferred facade wall (rule glazed_facade)",
                               assumed=["height"] if door else ["height", "sill"],
                               operation="swing" if door else None, operation_source="geometry" if door else None))
    return out


RULE = "glazed_facade"
MIN_REGION_M2 = 0.01            # wall-region slivers smaller than this are left out
MITRE = 2


def facade_wall_items(walls: list, faces: list, openings: list, file_rel: str, page_no: Optional[int],
                      units_to_m: Optional[float] = None) -> list:
    """The inferred facade walls of the closed faces as ``WallItem``s, cut from a wall region the way the room
    outlines' walls are (``outlines.infer_walls``): each face grown by the thickness of the drawn walls it touches
    (median), less the faces and the drawn walls and openings; ``walls.walls_from_mask`` cuts the region into wall
    rectangles whose faces snap to its edges (no gap at a step, no tilted wall)."""
    from wenart import building as B
    from wenart.ingest.generic import walls as W

    if not walls or not faces:
        return []
    polys = [TP.wall_polygon(w) for w in walls]
    tree = STRtree(polys)
    touching = [float(walls[int(i)].thickness) for f in faces
                for i in tree.query(f.buffer(ON_WALL_M), predicate="intersects")]
    t = statistics.median(touching) if touching else DEFAULT_T_M
    t = min(max(t, 0.1), 0.35)
    rooms = unary_union(faces)
    drawn = TP.bridged_union(walls, openings)
    region = rooms.buffer(t, join_style=MITRE).difference(rooms).difference(drawn)
    parts = [g for g in getattr(region, "geoms", [region]) if g.geom_type == "Polygon" and g.area >= MIN_REGION_M2]
    if not parts:
        return []
    rings = [list(g.exterior.coords)[:-1] for g in parts] + [list(r.coords)[:-1] for g in parts for r in g.interiors]
    edges = [(ring[k], ring[(k + 1) % len(ring)]) for ring in rings for k in range(len(ring))]
    prim = W.WallPrim(kind="inferred", entity=RULE, stroke_ids=[], method="inferred", confidence=0.6,
                      polygons=rings, faces=edges)
    mask = W.wall_mask(None, [prim], 1.0)
    new, _info = W.walls_from_mask(mask, [], file_rel, page_no, units_to_m=units_to_m)
    out = []
    for w in new:
        if float(w.thickness) < 0.05:
            continue                                        # a sliver along a drawn wall's face
        mid = ((w.start[0] + w.end[0]) / 2.0, (w.start[1] + w.end[1]) / 2.0)
        near = min(range(len(polys)), key=lambda i: polys[i].distance(Point(mid)))
        src = dict(walls[near].evidence or {})
        ev = B.evidence(src.get("file") or file_rel, "inferred", 0.6, page=page_no, entity=src.get("entity"),
                        layer=src.get("layer"), rule=RULE)
        ev["note"] = ("the room's walls did not close: its facade is drawn as window and door frames and short "
                      "pieces on other layers; the wall is inferred where the frames stand (thickness "
                      f"{t:.2f} m, the median of the drawn walls the room touches)")
        w.evidence = ev
        w.entity = f"inferred:{RULE}"
        w.status = "unverified"
        w.inferred = True
        w.exterior = True
        out.append(w)
    return out
