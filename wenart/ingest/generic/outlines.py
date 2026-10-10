"""Walls inferred from labelled room outlines (CLAUDE.md evidence and inference rules: open outer walls -> infer).

What: ``labelled_outlines(strokes_m, blocks)`` finds the closed outlines that each hold exactly one room label (and,
when the label prints an area, match it within ``AREA_TOL``); ``infer_walls(outlines, drawn_walls, ...)`` builds the
walls along them when the drawn walls do not close (``core.extract`` step 4). Both work in page metres.

Why: some plans draw the rooms but not (all) their walls. real03's ground floor inserts its flats as external
references that are empty in the file: the walls layer of the shared core holds four jamb fragments, but every room
of the core is drawn as a closed net-area outline (``MYD - ALAN-NET``) with its label and printed area inside.
The outlines are the room faces; the walls lie between and around them.

How:
1. *Outlines*: closed, unfilled strokes (or polylines whose ends meet) that make a valid polygon of >= 0.5 m², hold
   exactly one label block, an indoor one, and match its printed area within 8 % when it has one. A label held by
   several outlines keeps the one closest to its printed area (else the smallest: a net outline inside a gross
   one). Overlapping outlines keep the better match. At least ``MIN_OUTLINES`` (2) are needed.
2. *Wall region*: the outlines' union is closed over gaps up to ``MAX_INNER_M`` (0.60 m: two outlines that far apart
   have one wall between them, inner wall = the gap, so the rooms keep their drawn net areas); the closed union grown
   by the outer thickness minus the rooms is the wall material. Outlines that share an edge (gap < 5 cm) get an inner
   wall of the inner thickness centred on that edge. Outer thickness = the median of the drawn wall fragments along
   the outlines, else ``OUTER_DEFAULT_M`` (0.25 m, assumed); inner default ``INNER_DEFAULT_M`` (0.10 m).
3. *Walls*: drawn walls that lie on the wall region (>= 50 % of their area) stay as drawn (``vector``); the rest of
   the region is rasterised and cut into wall rectangles by ``walls.walls_from_mask`` (the faces snap to the
   outlines). Every such wall gets evidence method ``inferred`` (rule ``room_outlines``, the outline entities, the
   reason in the note), ``inferred = True`` and status ``unverified``.
4. *Openings*: the door and window symbols drawn across the inferred walls are read by the continuous-wall rule of
   ``openings`` (``openings_on_walls``); nothing is invented. A room without any door gets a warning (the agent may
   add one; never silent).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import OpeningItem, WallItem

AREA_TOL = 0.08                # an outline matches its label's printed area within 8 %
MIN_OUTLINE_M2 = 0.5
MIN_OUTLINES = 2
MAX_INNER_M = 0.60             # outlines up to this far apart have one wall between them (walls.OUTLINE_WIDTH_M)
SHARED_GAP_M = 0.05            # closer outlines share an edge: an inner wall of the inner thickness centred on it
OUTER_DEFAULT_M = 0.25
INNER_DEFAULT_M = 0.10
DRAWN_COVER = 0.5              # a drawn wall with >= 50 % of its area on the wall region stays as drawn
DRAWN_NEAR_M = 0.05            # drawn wall fragments this close to an outline give the outer thickness
INFERRED_CONFIDENCE = 0.6
RULE = "room_outlines"
MITRE = 2                      # shapely join_style mitre


@dataclass
class RoomOutline:
    """A closed outline that holds exactly one room label (page metres)."""
    stroke: Stroke
    polygon: Polygon
    block: object                              # labels.LabelBlock
    area_off: Optional[float] = None           # |area - printed| / printed, None without a printed area


@dataclass
class Inference:
    walls: list[WallItem] = field(default_factory=list)      # drawn walls kept + inferred walls
    inferred: list[WallItem] = field(default_factory=list)
    kept: list[WallItem] = field(default_factory=list)        # drawn walls that lie on the wall region
    openings: list[OpeningItem] = field(default_factory=list) # door/window symbols read on the inferred walls
    owned: set = field(default_factory=set)
    outer_thickness: float = OUTER_DEFAULT_M
    thickness_source: str = "assumed"
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _closed_polygon(st: Stroke) -> Optional[Polygon]:
    if st.fill is not None or st.arc is not None or len(st.pts) < 3:
        return None
    if not (st.closed or W.ends_meet(st)):
        return None
    poly = Polygon(st.pts)
    if not poly.is_valid or poly.area < MIN_OUTLINE_M2:
        return None
    return poly


def labelled_outlines(strokes_m: list[Stroke], blocks: list) -> list[RoomOutline]:
    """Closed outlines holding exactly one indoor room label whose printed area (if any) they match (page metres)."""
    cands: list[RoomOutline] = []
    for st in strokes_m:
        poly = _closed_polygon(st)
        if poly is None:
            continue
        inside = [b for b in blocks if poly.contains(Point(b.anchor))]
        if len(inside) != 1 or getattr(inside[0], "exterior", False):
            continue
        b = inside[0]
        off = None
        area = getattr(b, "area_m2", None)
        if area:
            off = abs(poly.area - float(area)) / float(area)
            if off > AREA_TOL:
                continue
        cands.append(RoomOutline(stroke=st, polygon=poly, block=b, area_off=off))
    # One outline per label: the best area match, else the smallest.
    best: dict[int, RoomOutline] = {}
    for c in cands:
        key = id(c.block)
        cur = best.get(key)
        rank = (c.area_off if c.area_off is not None else 0.0, c.polygon.area)
        if cur is None or rank < (cur.area_off if cur.area_off is not None else 0.0, cur.polygon.area):
            best[key] = c
    chosen = sorted(best.values(), key=lambda c: (c.area_off if c.area_off is not None else 0.0, c.polygon.area))
    out: list[RoomOutline] = []
    for c in chosen:
        if any(c.polygon.intersection(o.polygon).area > 0.01 * min(c.polygon.area, o.polygon.area) for o in out):
            continue
        out.append(c)
    return sorted(out, key=lambda c: (-c.polygon.centroid.y, c.polygon.centroid.x))


def _parts(geom) -> list[Polygon]:
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon" and g.area > 0]


def _rings(poly: Polygon) -> list[list[tuple[float, float]]]:
    return [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]


def _shared_strips(outlines: list[RoomOutline], thickness: float) -> list:
    """Inner walls of the inner thickness centred on the edges two outlines share (gap < 5 cm)."""
    strips = []
    for i, a in enumerate(outlines):
        for b in outlines[i + 1:]:
            if a.polygon.distance(b.polygon) >= SHARED_GAP_M:
                continue
            line = a.polygon.exterior.intersection(b.polygon.buffer(SHARED_GAP_M, join_style=MITRE))
            for g in getattr(line, "geoms", [line]):
                if g.is_empty or g.length < 0.1 or g.geom_type not in ("LineString", "MultiLineString"):
                    continue
                strips.append(g.buffer(thickness / 2.0, cap_style=2, join_style=MITRE))
    return strips


def infer_walls(outlines: list[RoomOutline], drawn_walls: list[WallItem], strokes_m: list[Stroke], file_rel: str,
                page_no: Optional[int], units_to_m: Optional[float] = None,
                owned: Optional[set] = None) -> Optional[Inference]:
    """Walls along the labelled room outlines (see the module docstring), or None with fewer than 2 outlines.

    ``drawn_walls`` are the page's wall rectangles (page metres); ``strokes_m`` the non-wall strokes for the door and
    window symbols; ``owned`` the stroke ids the drawn openings own already."""
    if len(outlines) < MIN_OUTLINES:
        return None
    from wenart.ingest.generic import openings as O

    inf = Inference()
    rooms = [o.polygon for o in outlines]
    rooms_u = unary_union(rooms)
    near = [w for w in drawn_walls if TP.wall_polygon(w).distance(rooms_u) <= DRAWN_NEAR_M]
    if near:
        inf.outer_thickness = round(statistics.median(w.thickness for w in near), 4)
        inf.thickness_source = f"median of {len(near)} drawn wall fragments along the outlines"
    inner_t = inf.outer_thickness if near else INNER_DEFAULT_M
    t_out = inf.outer_thickness
    g = MAX_INNER_M / 2.0
    closed = rooms_u.buffer(g, join_style=MITRE).buffer(-g, join_style=MITRE)
    region = closed.buffer(t_out, join_style=MITRE).difference(rooms_u)
    strips = _shared_strips(outlines, inner_t)
    if strips:
        region = unary_union([region] + strips)
    # Drawn walls on the wall region stay as drawn; the rest of the region is inferred.
    for w in drawn_walls:
        poly = TP.wall_polygon(w)
        if poly.area > 0 and poly.intersection(region).area >= DRAWN_COVER * poly.area:
            inf.kept.append(w)
    if inf.kept:
        region = region.difference(unary_union([TP.wall_polygon(w) for w in inf.kept]))
    polys = _parts(region)
    if not polys:
        return None
    ids = [o.stroke.id for o in outlines]
    rings = [r for p in polys for r in _rings(p)]
    # The region's own edges are the snap targets of the faces (the mask alone is off by a pixel on two sides);
    # ends that stop a pixel short of a perpendicular face are joined (``walls.walls_from_mask``).
    edges = [(ring[k], ring[(k + 1) % len(ring)]) for ring in rings for k in range(len(ring))]
    prim = W.WallPrim(kind="inferred", entity=RULE, stroke_ids=[], method="inferred",
                      confidence=INFERRED_CONFIDENCE, polygons=rings, faces=edges)
    mask = W.wall_mask(None, [prim], 1.0)
    walls, info = W.walls_from_mask(mask, [o.stroke for o in outlines], file_rel, page_no,
                                    units_to_m=units_to_m)
    inf.notes.extend(info.get("notes", []))
    inf.warnings.extend(info.get("warnings", []))
    layers = {o.stroke.layer for o in outlines}
    layer = next(iter(layers)) if len(layers) == 1 else None
    for w in walls:
        wp = TP.wall_polygon(w).buffer(0.03, join_style=MITRE)
        touching = [o for o in outlines if wp.intersects(o.polygon.exterior)]
        sides = _sides(w, outlines)
        inner = len(sides) == 2
        kind = "inner wall between two room outlines" if inner else "outer wall along a room outline"
        if inner and len({id(o) for o in sides}) == 2 and abs(w.thickness - inner_t) > 0.005:
            how = f"thickness {w.thickness:.3f} m = the gap between the outlines"
        elif inner:
            how = f"thickness {w.thickness:.3f} m ({inf.thickness_source if near else 'inner default, assumed'})"
        else:
            how = f"thickness {w.thickness:.3f} m ({inf.thickness_source})"
        names = ", ".join(f"'{o.block.name}'" for o in (sides or touching)) or "none"
        ev = B.evidence(file_rel, "inferred", INFERRED_CONFIDENCE, page=page_no,
                        entity=",".join(o.stroke.id for o in touching) or ",".join(ids),
                        layer=layer, rule=RULE)
        ev["note"] = (f"inferred from the labelled room outlines ({kind}: {names}); {how}; the drawn walls do not "
                      f"close")
        w.evidence = ev
        w.entity = ev["entity"]
        w.status = "unverified"
        w.inferred = True
        inf.inferred.append(w)
    inf.walls = list(inf.kept) + inf.inferred
    # Door and window symbols drawn across the inferred walls (continuous-wall rule); nothing is invented.
    taken = set(owned or set())
    outline_ids = set(ids)
    symbol_strokes = [st for st in strokes_m if st.id not in outline_ids]
    inf.openings = O.openings_on_walls(inf.inferred, symbol_strokes, file_rel, page_no, units_to_m, taken)
    inf.owned = taken - set(owned or set())
    return inf


def _sides(w: WallItem, outlines: list[RoomOutline]) -> list[RoomOutline]:
    """The outlines just beyond both faces of a wall at its middle (two for an inner wall)."""
    (x0, y0), (x1, y1) = w.start, w.end
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 0:
        return []
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    d = w.thickness / 2.0 + 0.02
    out = []
    for sgn in (1.0, -1.0):
        p = Point(mx + sgn * nx * d, my + sgn * ny * d)
        hit = next((o for o in outlines if o.polygon.contains(p)), None)
        if hit is not None:
            out.append(hit)
    return out


def doorless_rooms(outlines: list[RoomOutline], walls: list[WallItem], openings: list[OpeningItem]) -> list[str]:
    """Names of the outlines with no door or opening on their boundary (within the host wall's half thickness)."""
    out = []
    for o in outlines:
        ring = o.polygon.exterior
        hit = False
        for op in openings:
            if op.kind == "window":
                continue
            k = TP.host_wall(op, walls) if not op.virtual else None
            reach = (walls[k].thickness if k is not None else 0.3) + 0.05
            if ring.distance(Point(op.center)) <= reach:
                hit = True
                break
        if not hit:
            out.append(o.block.name)
    return out


def summary(inf: Inference) -> str:
    """One line for the warnings: how many walls were inferred, their thicknesses."""
    lengths = sum(math.dist(w.start, w.end) for w in inf.inferred)
    kept = f"; {len(inf.kept)} drawn walls on them kept as drawn" if inf.kept else ""
    return (f"walls inferred from room outlines: {len(inf.inferred)} ({lengths:.1f} m; outer thickness "
            f"{inf.outer_thickness:.2f} m, {inf.thickness_source}){kept}; evidence method inferred, status unverified")


def outline_line(o: RoomOutline) -> str:
    area = getattr(o.block, "area_m2", None)
    printed = f", printed {area:g} m²" if area else ""
    return f"'{o.block.name}' {o.stroke.id} ({o.polygon.area:.2f} m²{printed})"


__all__ = ["RoomOutline", "Inference", "labelled_outlines", "infer_walls", "doorless_rooms", "summary",
           "outline_line"]
