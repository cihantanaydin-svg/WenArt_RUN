"""Furniture and site decor of the generic plan core (docs/milestone7.md §2.8, §2.5): clusters, composites, rules.

A real plan draws furniture as loose strokes with no block names (real01) or as DXF INSERTs; either way the
footprint must come from the geometry and the type from a rule, a block name or two agreeing AI passes:

1. **Strokes considered**: every stroke except the wall primitives, the strokes the openings own, the dimension
   strokes and glyph strokes inside text boxes (grown 10 %). Polylines and closed paths are split into segments, and a
   segment is wall outline (dropped) when >= 90 % of its length lies within 20 mm of the bridged wall geometry (wall
   rectangles plus every opening rectangle) - real01's 94.7 m outline polyline runs across every window and door gap,
   so the whole stroke would never pass a 90 % test against the walls alone - or when >= 50 % of it lies inside the
   wall material (jamb lines crossing a wall). Dropped segments that close a piece's contour (a headboard 9 mm off the
   wall face) are given back to that piece. Segments inside the building outline are furniture strokes; the others
   are site strokes.
2. **Clusters**: union-find over segments closer than 20 mm (dots included); a cluster whose bbox lies >= 80 % inside
   another merges into it unless it is a closed polygon with both sides >= 0.3 m that fits a size-table type (a sink or
   hob in a counter stays its own piece) - but not when a closed contour of the container encloses it and it is the
   container's inner outline (>= 40 % of that contour's area: a bed's double outline, a table's inlay) or a detail
   on it (spanning < 60 % of the contour's short side: pillows on a bed). Clusters with both sides < 0.20 m are
   details (counted, dropped).
3. **Deterministic types**: *stair* (merged collinear tread strokes, split at a perpendicular divider crossing >= 80 %
   of them; each side with >= 5 equal, evenly spaced segments 0.20-0.35 m apart is a flight); *kitchen counter* (a
   chained polyline of >= 2 straight legs whose ends lie within 50 mm of a wall face, parallel to walls at 0.45-0.75 m:
   one piece per leg, the corner square to the longer leg; segments with an end on a wall face and perpendicular to
   it are the run's end caps); *block name* (DXF INSERT keywords, checked against the size table).
4. **Composite split**: a cluster that fits no size-table type, or that holds >= 2 top-level closed contours >= 0.20 m
   on both sides, is split. Closed contours are chains of strokes joined end to end (within 5 mm), polygonised and
   filled: a nightstand whose edge merely lies along the bed's edge keeps its own contour; contours overlapping < 15 %
   of the smaller are separate; equal-sized contours that touch each other (sofa cushions, wardrobe doors) are parts of
   one piece. Each top-level contour plus the strokes inside it seeds a piece; the remaining strokes are re-clustered
   at 2 mm (strokes joined end to end stay together) after the seed rings are removed and join the seed whose polygon
   contains them or the piece within 20 mm; edge contact never merges two pieces. Parts that fit no type and cannot
   be split stay **one composite** (``unknown``, ``unverified``, "possible group of N pieces"), never typed as one
   table or bed. A cluster drawn only by DXF block content splits by INSERT instance first (one piece per instance
   of a furniture-named block: a WC's tank and bowl stay one piece, DINING-6 gives its table and each CHAIR).
   Pieces whose outline a circle fits for >= 90 % get ``details`` ``shape "round"`` and ``circle_fit`` (§6.4).
5. Everything else is an **AI candidate** (§3): ``unknown``, ``unverified``, ``type_method "none"`` until two passes
   agree. Clusters > 4.5 m on a side are ``unknown``/``unverified`` and never asked.
6. **Site decor**: clusters outside the building outline: green fills or radial clusters -> ``plant``; edge and
   boundary lines (< 50 mm wide or > 4.5 m long) are not decor; else ``other``.

All coordinates are page metres (y up); ``box`` is in page units when ``units_to_m`` is given.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import polygonize, unary_union
from shapely.strtree import STRtree

from wenart import building as B
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import FurnitureItem, OpeningItem, WallItem

OUTLINE_NEAR_M = 0.02
OUTLINE_SHARE = 0.9
WALL_MATERIAL_SHARE = 0.5
TEXT_GROW = 0.10
CHAIN_M = 0.005
CLUSTER_M = 0.02
RECLUSTER_M = 0.002
CONTAIN_SHARE = 0.8
CONTAIN_KEEP_SIDE_M = 0.3
DETAIL_M = 0.20
MAX_SIDE_M = 4.5
CONTOUR_MIN_M = 0.20
CONTOUR_OVERLAP = 0.15
ATTACH_M = 0.02
SNAP_DEG = 3.0
FOOTPRINT_CONFIDENCE = 0.9
SIZE_TOLERANCE = 0.15

STAIR_MERGE_M = 0.005
STAIR_DIVIDER_SHARE = 0.8
STAIR_MIN_TREADS = 5
STAIR_STEP_M = (0.20, 0.35)
STAIR_STEP_TOL = 0.10
COUNTER_END_M = 0.05
COUNTER_DEPTH_M = (0.45, 0.75)
FRONT_WALL_M = 0.25
ROUND_SHARE = 0.9              # §6.4: round when a circle fits >= 90 % of the outline
ROUND_TOL_M = 0.01
ROUND_TOL_REL = 0.03

# Built-in size table, used when wenart/recognition/size_table.yaml is missing or unreadable: plausible footprint
# (width range, depth range) in metres, either orientation, +15 % tolerance applied by ``fits``. Sources: standard
# furniture sizes (Neufert, manufacturer ranges), the synthetic block table (wenart/synthetic/blocks.py) and the
# real01 reference (tests/fixtures/real01_reference.yaml).
FALLBACK_SIZE_TABLE: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {
    "bed_single": ((0.8, 1.2), (1.8, 2.2)),
    "bed_double": ((1.35, 2.0), (1.85, 2.25)),
    "sofa": ((1.2, 3.0), (0.7, 1.1)),
    "armchair": ((0.6, 1.1), (0.6, 1.1)),
    "table_dining": ((0.7, 1.2), (0.8, 2.6)),
    "table_coffee": ((0.4, 1.2), (0.6, 1.4)),
    "desk": ((0.9, 2.0), (0.5, 0.9)),
    "chair": ((0.35, 0.65), (0.35, 0.65)),
    "wardrobe": ((0.8, 3.0), (0.5, 0.7)),
    "kitchen_counter": ((0.6, 5.0), (0.5, 0.75)),
    "kitchen_island": ((1.0, 2.5), (0.6, 1.2)),
    "fridge": ((0.55, 0.95), (0.55, 0.8)),
    "stove": ((0.45, 0.95), (0.5, 0.7)),
    "sink_kitchen": ((0.45, 1.2), (0.4, 0.6)),
    "washbasin": ((0.4, 0.9), (0.35, 0.6)),
    "toilet": ((0.35, 0.5), (0.55, 0.8)),
    "shower": ((0.7, 1.6), (0.7, 1.2)),
    "bathtub": ((1.4, 1.9), (0.65, 0.9)),
    "tv_unit": ((1.0, 2.4), (0.3, 0.6)),
    "bookshelf": ((0.6, 2.0), (0.25, 0.45)),
    "nightstand": ((0.35, 0.65), (0.3, 0.55)),
    "dresser": ((0.8, 1.6), (0.4, 0.6)),
    "washing_machine": ((0.55, 0.7), (0.55, 0.7)),
    "stair": ((0.7, 3.0), (1.5, 6.0)),
    "side_table": ((0.3, 0.7), (0.3, 0.7)),
    "floor_lamp": ((0.25, 0.6), (0.25, 0.6)),
    "potted_plant": ((0.2, 1.0), (0.2, 1.0)),
}

# DXF block-name keywords (§2.8), English then Turkish (wenart/synthetic/blocks.py); first match wins, so the more
# specific words come first (ARMCHAIR before CHAIR, CHAIR before DINING, BEDSIDE before BED).
BLOCK_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("ARMCHAIR", "armchair"), ("CHAIR", "chair"), ("NIGHTSTAND", "nightstand"), ("BEDSIDE", "nightstand"),
    ("SOFA", "sofa"), ("DINING", "table_dining"), ("COFFEE", "table_coffee"), ("BED-DOUBLE", "bed_double"),
    ("BED_DOUBLE", "bed_double"), ("BED-SINGLE", "bed_single"), ("BED_SINGLE", "bed_single"), ("BED", "bed"),
    ("TABLE", "table"), ("WC", "toilet"), ("TOILET", "toilet"), ("BASIN", "washbasin"), ("SINK", "sink_kitchen"),
    ("WARDROBE", "wardrobe"), ("FRIDGE", "fridge"), ("STOVE", "stove"), ("HOB", "stove"), ("BATH", "bathtub"),
    ("SHOWER", "shower"), ("DESK", "desk"), ("TV", "tv_unit"), ("PLANT", "potted_plant"), ("LAMP", "floor_lamp"),
    ("KANEPE", "sofa"), ("KOLTUK", "armchair"), ("SEHPA", "table_coffee"), ("YEMEK_MASASI", "table_dining"),
    ("SANDALYE", "chair"), ("TV_UNITESI", "tv_unit"), ("KITAPLIK", "bookshelf"), ("YATAK_CIFT", "bed_double"),
    ("YATAK_TEK", "bed_single"), ("KOMIDIN", "nightstand"), ("DOLAP", "wardrobe"), ("SIFONYER", "dresser"),
    ("CALISMA_MASASI", "desk"), ("TEZGAH", "kitchen_counter"), ("BUZDOLABI", "fridge"), ("OCAK", "stove"),
    ("EVIYE", "sink_kitchen"), ("LAVABO", "washbasin"), ("KLOZET", "toilet"), ("DUS", "shower"), ("KUVET", "bathtub"),
    ("CAMASIR_MAK", "washing_machine"),
)


# --------------------------------------------------------------------------
# Size table
# --------------------------------------------------------------------------

def load_size_table() -> tuple[dict, str]:
    """(table, source): ``wenart/recognition/size_table.yaml`` (area Y) when present and readable, else the
    built-in FALLBACK_SIZE_TABLE. Accepted YAML shapes: ``{types: {t: {width: [lo, hi], depth: [lo, hi]}}}`` or the
    same without ``types``; ``width_m``/``depth_m`` keys are accepted too."""
    path = Path(__file__).resolve().parents[2] / "recognition" / "size_table.yaml"
    if path.exists():
        try:
            import yaml

            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            types = data.get("types", data) if isinstance(data, dict) else {}
            table = {}
            for name, spec in types.items():
                if not isinstance(spec, dict):
                    continue
                w = spec.get("width", spec.get("width_m"))
                d = spec.get("depth", spec.get("depth_m"))
                if isinstance(w, (list, tuple)) and isinstance(d, (list, tuple)) and len(w) == 2 and len(d) == 2:
                    table[name] = ((float(w[0]), float(w[1])), (float(d[0]), float(d[1])))
            if table:
                return table, "wenart/recognition/size_table.yaml"
        except Exception:                                  # unreadable: the built-in table, said so in the notes
            pass
    return dict(FALLBACK_SIZE_TABLE), "built-in size table (symbols.FALLBACK_SIZE_TABLE)"


def fits(table: dict, ftype: str, size) -> bool:
    """Whether a footprint (a, b) fits ``ftype``'s range in either orientation (+15 %)."""
    if ftype not in table:
        return False
    (w0, w1), (d0, d1) = table[ftype]
    a, b = size

    def inside(v, lo, hi):
        return lo / (1 + SIZE_TOLERANCE) <= v <= hi * (1 + SIZE_TOLERANCE)
    return (inside(a, w0, w1) and inside(b, d0, d1)) or (inside(a, d0, d1) and inside(b, w0, w1))


def fitting_types(table: dict, size) -> list[str]:
    return [t for t in table if t != "stair" and fits(table, t, size)]


# --------------------------------------------------------------------------
# Segments
# --------------------------------------------------------------------------

@dataclass
class Seg:
    id: str                    # stroke id, "#k" appended for a polyline piece
    stroke: Stroke
    pts: list[tuple[float, float]]
    geom: object
    curve: bool                # an arc / curve kept whole
    dot: bool = False

    @property
    def length(self) -> float:
        return self.geom.length


def _segments(strokes: list[Stroke], drop: set) -> list[Seg]:
    out = []
    for st in strokes:
        if st.id in drop or not st.pts:
            continue
        pts = list(st.pts)
        if len(set(pts)) == 1:
            out.append(Seg(st.id, st, [pts[0]], Point(pts[0]), False, dot=True))
            continue
        curved = st.kind in ("arc", "circle", "curve") or st.arc is not None
        if curved:
            ring = pts + [pts[0]] if st.closed and len(pts) > 2 else pts
            out.append(Seg(st.id, st, ring, LineString(ring), True))
            continue
        if st.closed and len(pts) > 2:
            pts = pts + [pts[0]]
        if len(pts) == 2:
            out.append(Seg(st.id, st, pts, LineString(pts), False))
            continue
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            if a == b:
                continue
            out.append(Seg(f"{st.id}#{k}", st, [a, b], LineString([a, b]), False))
    return out


def _dimension_ids(dims) -> set[str]:
    """Stroke ids of the dimension candidates: G1's ``DimCandidate.stroke_ids`` (line pieces and end marks) and
    ``extension_ids`` (attributes or dict keys; strokes or ids)."""
    out: set[str] = set()
    for d in dims or []:
        for key in ("stroke_ids", "extension_ids"):
            ids = d.get(key) if isinstance(d, dict) else getattr(d, key, None)
            for x in ids or []:
                out.add(x.id if isinstance(x, Stroke) else str(x))
    return out


def _text_boxes(texts) -> list:
    boxes = []
    for t in texts or []:
        x0, y0, x1, y1 = t.box
        gx, gy = (x1 - x0) * TEXT_GROW / 2.0, (y1 - y0) * TEXT_GROW / 2.0
        boxes.append(sbox(x0 - gx, y0 - gy, x1 + gx, y1 + gy))
    return boxes


def _as_polygon(outline):
    if outline is None:
        return None
    if isinstance(outline, (Polygon,)) or hasattr(outline, "geom_type"):
        return outline
    return Polygon(outline)


def _wall_geometry(walls: list, openings: list, site_walls: list):
    polys = [TP.wall_polygon(w) for w in list(walls) + list(site_walls)]
    all_walls = list(walls) + list(site_walls)
    for o in openings or []:
        if getattr(o, "virtual", False):
            continue
        p = TP.opening_polygon(o, all_walls)
        if p is not None:
            polys.append(p)
    return unary_union(polys) if polys else Polygon()


def _drop_outline(segs: list[Seg], wall_geom) -> tuple[list[Seg], int]:
    """Segments with >= 90 % of their length within 20 mm of the bridged wall geometry are wall outline (§2.8).
    Segments with >= 50 % of their length inside the wall or opening material itself are wall drawing too (real01's
    window jamb line runs from the outer wall face to the bed's head edge: 89 % near the wall, 82 % inside it)."""
    if wall_geom.is_empty or not segs:
        return segs, 0
    near = wall_geom.buffer(OUTLINE_NEAR_M, join_style=2)
    shapely.prepare(near)
    shapely.prepare(wall_geom)
    geoms = np.array([s.geom for s in segs], dtype=object)
    inside = shapely.within(geoms, near)
    disjoint = shapely.disjoint(geoms, near)
    keep = []
    dropped = 0
    for i, s in enumerate(segs):
        if inside[i]:
            dropped += 1
            continue
        if disjoint[i] or s.dot or s.length <= 0:
            keep.append(s)
            continue
        share = s.geom.intersection(near).length / s.length
        in_wall = s.geom.intersection(wall_geom).length / s.length
        if share >= OUTLINE_SHARE or in_wall >= WALL_MATERIAL_SHARE:
            dropped += 1
        else:
            keep.append(s)
    return keep, dropped


# --------------------------------------------------------------------------
# Clusters
# --------------------------------------------------------------------------

def _union_find(geoms: list, dist: float) -> list[list[int]]:
    if not geoms:
        return []
    tree = STRtree(geoms)
    left, right = tree.query(np.array(geoms, dtype=object), predicate="dwithin", distance=dist)
    parent = list(range(len(geoms)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in zip(left.tolist(), right.tolist()):
        if i != j:
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
    groups: dict[int, list[int]] = {}
    for i in range(len(geoms)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


@dataclass
class Cluster:
    segs: list[Seg]
    note: list = field(default_factory=list)

    @property
    def geom(self):
        return unary_union([s.geom for s in self.segs])

    def bounds(self) -> tuple[float, float, float, float]:
        xs = [p[0] for s in self.segs for p in s.pts]
        ys = [p[1] for s in self.segs for p in s.pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def size(self) -> tuple[float, float]:
        b = self.bounds()
        return (b[2] - b[0], b[3] - b[1])

    def stroke_ids(self) -> list[str]:
        return sorted({s.stroke.id for s in self.segs}, key=_id_key)


def _id_key(sid: str):
    head, _, tail = sid.partition(":")
    try:
        return (head, int(tail.split("#")[0]))
    except ValueError:
        return (head, 0)


def clusters_of(segs: list[Seg], dist: float = CLUSTER_M) -> list[Cluster]:
    return [Cluster([segs[i] for i in idx]) for idx in _union_find([s.geom for s in segs], dist)]


def chain_clusters(segs: list[Seg], dist: float = RECLUSTER_M) -> list[Cluster]:
    """Clusters at ``dist`` that also keep strokes joined end to end (within 5 mm) together: the 2 mm re-cluster of
    the composite split must separate touching pieces without breaking a shape whose joints carry the 1-3 mm gaps
    of a 0.12 pt coordinate grid."""
    if not segs:
        return []
    groups = _union_find([s.geom for s in segs], dist)
    parent = list(range(len(segs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for idx in groups:
        for k in idx[1:]:
            union(idx[0], k)
    ends, _ = _end_nodes(segs)
    first: dict = {}
    for i, e in enumerate(ends):
        if e is None:
            continue
        for n in e:
            if n in first:
                union(i, first[n])
            else:
                first[n] = i
    out: dict = {}
    for i in range(len(segs)):
        out.setdefault(find(i), []).append(segs[i])
    return [Cluster(v) for v in out.values()]


# --------------------------------------------------------------------------
# Closed contours (endpoint chains) and the containment merge
# --------------------------------------------------------------------------

def _end_nodes(segs: list[Seg], tol: float = CHAIN_M) -> tuple[list, dict]:
    """Stroke ends merged within ``tol`` (5 mm: a CAD PDF on a 0.12 pt grid leaves 1-3 mm between joined ends).
    Returns ``(ends, coords)``: per segment ``(node a, node b)`` or None, and node -> mean coordinate."""
    pts, owner = [], []
    for i, s in enumerate(segs):
        if s.dot or len(s.pts) < 2:
            continue
        pts.extend([s.pts[0], s.pts[-1]])
        owner.extend([i, i])
    parent = list(range(len(pts)))

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    grid: dict = {}
    for k, p in enumerate(pts):
        cx, cy = int(math.floor(p[0] / tol)), int(math.floor(p[1] / tol))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((cx + dx, cy + dy), ()):
                    if math.dist(p, pts[j]) <= tol:
                        ra, rb = find(k), find(j)
                        if ra != rb:
                            parent[ra] = rb
        grid.setdefault((cx, cy), []).append(k)
    members: dict = {}
    for k in range(len(pts)):
        members.setdefault(find(k), []).append(k)
    coords = {r: (sum(pts[k][0] for k in ks) / len(ks), sum(pts[k][1] for k in ks) / len(ks))
              for r, ks in members.items()}
    ends: list = [None] * len(segs)
    for k in range(0, len(pts), 2):
        ends[owner[k]] = (find(k), find(k + 1))
    return ends, coords


def contours(segs: list[Seg]) -> list[tuple[Polygon, list[int]]]:
    """Closed contours of a stroke set: strokes joined end to end (within 5 mm) form chains; the faces of each
    chain component, polygonised and filled, are its contours. Strokes that only touch another stroke's middle (a
    blanket line ending on a bed outline, a nightstand edge lying along the bed's edge) are not joined, so touching
    pieces keep separate contours. Returns ``[(polygon, indices of the ring strokes)]``."""
    ends, coords = _end_nodes(segs)
    parent: dict = {}

    def find(k):
        while parent.setdefault(k, k) != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for e in ends:
        if e is not None:
            ra, rb = find(e[0]), find(e[1])
            if ra != rb:
                parent[ra] = rb
    comps: dict = {}
    for i, e in enumerate(ends):
        if e is not None:
            comps.setdefault(find(e[0]), []).append(i)
    out = []
    for idx in comps.values():
        if len(idx) == 1 and not segs[idx[0]].stroke.closed:
            continue
        lines = []
        for i in idx:
            pts = list(segs[i].pts)
            pts[0], pts[-1] = coords[ends[i][0]], coords[ends[i][1]]
            if len(set(pts)) >= 2:
                lines.append(LineString(pts))
        if not lines:
            continue
        faces = [p for p in polygonize(unary_union(lines)) if p.area > 1e-6]
        if not faces:
            continue
        filled = unary_union([Polygon(f.exterior) for f in faces])
        for poly in getattr(filled, "geoms", [filled]):
            ring = poly.exterior.buffer(CHAIN_M)
            members = [i for i in idx if ring.contains(segs[i].geom)]
            out.append((Polygon(poly.exterior), members or idx))
    return out


def _rect_sides(geom) -> tuple[float, float]:
    rect = geom.minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        b = geom.bounds
        return (b[2] - b[0], b[3] - b[1])
    c = list(rect.exterior.coords)
    return (math.dist(c[0], c[1]), math.dist(c[1], c[2]))


def _closed_outline(cl: Cluster) -> Optional[Polygon]:
    """The cluster's own closed outline: a contour covering >= 80 % of the cluster's bbox area, else None."""
    b = cl.bounds()
    area = max((b[2] - b[0]) * (b[3] - b[1]), 1e-12)
    best = None
    for poly, _ in contours(cl.segs):
        if poly.area >= 0.8 * area and (best is None or poly.area > best.area):
            best = poly
    return best


def _merge_contained(clusters: list[Cluster], table: dict) -> list[Cluster]:
    """A cluster whose bbox lies >= 80 % inside another merges into it, unless it is a closed polygon with both sides
    >= 0.3 m that fits a size-table type and is not an inner outline of the container (a closed contour of the
    container encloses it and it covers >= 40 % of that contour: a bed's double outline, a table's inlay)."""
    order = sorted(range(len(clusters)), key=lambda i: -_bbox_area(clusters[i].bounds()))
    alive = {i: clusters[i] for i in order}
    container_contours: dict[int, list] = {}
    for pos, i in enumerate(order):
        if i not in alive:
            continue
        bi = alive[i].bounds()
        for j in order[pos + 1:]:
            if j not in alive:
                continue
            bj = alive[j].bounds()
            if _inside_share(bj, bi) < CONTAIN_SHARE:
                continue
            if _keeps_own_piece(alive[j], alive[i], table, container_contours, i):
                continue
            alive[i].segs.extend(alive[j].segs)
            del alive[j]
            container_contours.pop(i, None)
            bi = alive[i].bounds()
    return list(alive.values())


def _keeps_own_piece(inner: Cluster, outer: Cluster, table: dict, cache: dict, key) -> bool:
    """The containment exception of §2.8 (a sink or hob in a counter stays its own piece), limited to shapes that
    are not drawn details of the container: when a closed contour of the container encloses the shape, the shape is
    the container's inner outline (>= 40 % of its area: a bed's double outline, a table's inlay) or a detail on it
    (spanning < 60 % of its short side: pillows on a bed); a sink spans most of a counter's depth."""
    w, h = inner.size()
    if min(w, h) < CONTAIN_KEEP_SIDE_M:
        return False
    poly = _closed_outline(inner)
    if poly is None or not fitting_types(table, _rect_sides(poly)):
        return False
    if key not in cache:
        cache[key] = [p for p, _ in contours(outer.segs)]
    for c in cache[key]:
        if not c.buffer(0.005).contains(poly):
            continue
        if poly.area >= 0.4 * c.area:
            return False
        rect = c.minimum_rotated_rectangle
        if rect.geom_type != "Polygon":
            return False
        q = list(rect.exterior.coords)
        e1 = (q[1][0] - q[0][0], q[1][1] - q[0][1])
        e2 = (q[2][0] - q[1][0], q[2][1] - q[1][1])
        short = e1 if math.hypot(*e1) <= math.hypot(*e2) else e2
        n = math.hypot(*short) or 1.0
        u = (short[0] / n, short[1] / n)
        proj = [p[0] * u[0] + p[1] * u[1] for p in poly.exterior.coords]
        if max(proj) - min(proj) < 0.6 * n:
            return False
    return True


def _bbox_area(b) -> float:
    return max(b[2] - b[0], 0.0) * max(b[3] - b[1], 0.0)


def _inside_share(inner, outer) -> float:
    """Share of bbox ``inner`` lying inside bbox ``outer`` (a degenerate box counts by its extent)."""
    ix0, iy0 = max(inner[0], outer[0]), max(inner[1], outer[1])
    ix1, iy1 = min(inner[2], outer[2]), min(inner[3], outer[3])
    if ix1 < ix0 or iy1 < iy0:
        return 0.0
    area = _bbox_area(inner)
    if area <= 1e-12:
        span = max(inner[2] - inner[0], inner[3] - inner[1])
        inside = max(ix1 - ix0, iy1 - iy0)
        return 1.0 if span <= 1e-12 else inside / span
    return _bbox_area((ix0, iy0, ix1, iy1)) / area


# --------------------------------------------------------------------------
# Composite split
# --------------------------------------------------------------------------

def top_contours(cl: Cluster) -> list[tuple[Polygon, list[int]]]:
    """Top-level closed contours >= 0.20 m on both sides: nested ones dropped, ones overlapping >= 15 % of the
    smaller merged, and equal-sized contours that touch each other (sofa cushions, wardrobe doors, cabinet fronts)
    merged into one object."""
    cands = [(p, m) for p, m in contours(cl.segs) if min(_rect_sides(p)) >= CONTOUR_MIN_M]
    cands.sort(key=lambda pm: -pm[0].area)
    tops: list[list] = []
    for poly, members in cands:
        placed = False
        for t in tops:
            inter = t[0].intersection(poly).area
            if inter >= 0.85 * poly.area:
                placed = True                       # nested: part of the bigger one
                break
            if inter >= CONTOUR_OVERLAP * min(poly.area, t[0].area):
                t[0] = t[0].union(poly)
                t[1] = t[1] + members
                placed = True
                break
        if not placed:
            tops.append([poly, list(members), [poly]])
    # Equal neighbours are parts of one piece.
    merged = True
    while merged:
        merged = False
        for a in range(len(tops)):
            for b in range(a + 1, len(tops)):
                pa, pb = tops[a][2][0], tops[b][2][0]
                if tops[a][0].distance(tops[b][0]) > 0.005:
                    continue
                sa, sb = sorted(_rect_sides(pa)), sorted(_rect_sides(pb))
                if all(abs(x - y) <= 0.15 * max(x, y) for x, y in zip(sa, sb)):
                    tops[a][0] = tops[a][0].union(tops[b][0])
                    tops[a][1] += tops[b][1]
                    tops[a][2] += tops[b][2]
                    del tops[b]
                    merged = True
                    break
            if merged:
                break
    return [(t[0], t[1]) for t in tops]


def _block_keyword(name: str) -> Optional[str]:
    upper = name.upper()
    return next((ftype for key, ftype in BLOCK_KEYWORDS if key in upper), None)


def block_instance(st: Stroke) -> tuple[str, bool]:
    """(instance key, named) of a DXF block stroke: the INSERT instance of the innermost block in its chain whose
    name holds a furniture keyword (``INSERT:FF/3`` for a CHAIR nested in DINING-6, ``INSERT:FF`` for the table
    lines of DINING-6 or for a pillow block inside a BED block), else the outermost instance; ``named`` tells
    whether a keyword was found. Ids that do not follow ``dxf_generic``'s ``INSERT:<h>/<k>/...`` form group by the
    block chain."""
    names = (st.block or "").split("/")
    parts = st.id.split("/")
    keyed = [i for i, name in enumerate(names) if _block_keyword(name) is not None]
    if len(parts) < len(names) + 1:
        return f"{st.block}|", bool(keyed)
    i = keyed[-1] if keyed else 0
    return f"{'/'.join(names[:i + 1])}|{'/'.join(parts[:i + 1])}", bool(keyed)


def split_composite(cl: Cluster, table: dict) -> list[tuple[Cluster, int]]:
    """Pieces of a cluster: ``[(cluster, n)]`` where ``n`` > 1 marks an unsplittable composite of n parts.

    A cluster drawn entirely by DXF block content splits by block instance first (one piece per INSERT of a
    furniture-named block: a WC's tank and bowl stay one piece, DINING-6 gives its table and each CHAIR); instances
    whose chain names no furniture go through the geometric split."""
    if cl.segs and all(s.stroke.block for s in cl.segs):
        groups: dict[str, list[Seg]] = {}
        named: dict[str, bool] = {}
        for s in cl.segs:
            key, has_name = block_instance(s.stroke)
            groups.setdefault(key, []).append(s)
            named[key] = has_name
        out: list[tuple[Cluster, int]] = []
        for key in sorted(groups):
            sub = Cluster(groups[key])
            out.extend([(sub, 1)] if named[key] else _split_geometric(sub, table))
        return out
    return _split_geometric(cl, table)


def _split_geometric(cl: Cluster, table: dict) -> list[tuple[Cluster, int]]:
    tops = top_contours(cl)
    corners, _ = min_rect([p for s in cl.segs for p in s.pts])
    size = (math.dist(corners[0], corners[1]), math.dist(corners[1], corners[2]))
    fits_any = bool(fitting_types(table, size))
    if len(tops) < 2 and fits_any:
        return [(cl, 1)]
    if not tops:
        return [(cl, _parts_count(cl))]
    ring_ids = {i for _, members in tops for i in members}
    pieces = [Cluster([cl.segs[i] for i in members]) for _, members in tops]
    polys = [p for p, _ in tops]
    rest = [s for i, s in enumerate(cl.segs) if i not in ring_ids]
    loose: list[Cluster] = []
    for sub in chain_clusters(rest, RECLUSTER_M):
        g = sub.geom
        home = None
        for k, p in enumerate(polys):
            if g.length > 0 and g.intersection(p.buffer(0.003)).length >= 0.9 * g.length:
                home = k
                break
            if g.length == 0 and p.buffer(0.003).contains(g):
                home = k
                break
        if home is None:
            dists = [p.exterior.distance(g) for p in polys]
            k = int(np.argmin(dists))
            if dists[k] <= ATTACH_M:
                home = k
        if home is None:
            loose.append(sub)
        else:
            pieces[home].segs.extend(sub.segs)
    # Loose parts next to a grown piece (a chair back beyond its connector) join that piece.
    changed = True
    while loose and changed:
        changed = False
        geoms = [p.geom for p in pieces]
        for sub in list(loose):
            dists = [g.distance(sub.geom) for g in geoms]
            k = int(np.argmin(dists))
            if dists[k] <= ATTACH_M:
                pieces[k].segs.extend(sub.segs)
                loose.remove(sub)
                changed = True
    out = [(p, 1) for p in pieces]
    if loose:
        for sub in clusters_of([s for c in loose for s in c.segs], CLUSTER_M):
            out.append((sub, 1))
    if len(out) == 1 and not fits_any:
        return [(cl, _parts_count(cl))]
    return out


def _parts_count(cl: Cluster) -> int:
    return max(1, len(top_contours(cl)), len(clusters_of(cl.segs, RECLUSTER_M)) if len(cl.segs) < 50 else 1)


def reclose(cl: Cluster, pool: list[Seg], taken: set) -> int:
    """Give a cluster back the near-wall segments that close its contours.

    The outline rule drops every segment within 20 mm of a wall face, which also removes the back edge of a bed or a
    nightstand standing against the wall (real01: 6-9 mm off the face). A chain of dropped segments that lies inside
    the cluster's bbox (grown 20 mm) and joins two ends of the cluster's strokes is part of the piece, not wall
    outline. Returns the number of segments added."""
    b = cl.bounds()
    grow = OUTLINE_NEAR_M
    box_ = (b[0] - grow, b[1] - grow, b[2] + grow, b[3] + grow)
    near = [s for s in pool if id(s) not in taken and all(box_[0] <= p[0] <= box_[2] and box_[1] <= p[1] <= box_[3]
                                                          for p in s.pts)]
    if not near:
        return 0
    allsegs = cl.segs + near
    ends, _ = _end_nodes(allsegs)
    n0 = len(cl.segs)
    anchored = {n for e in ends[:n0] if e is not None for n in e}
    parent: dict = {}

    def find(k):
        while parent.setdefault(k, k) != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for e in ends[n0:]:
        if e is not None:
            ra, rb = find(e[0]), find(e[1])
            if ra != rb:
                parent[ra] = rb
    comp_segs: dict = {}
    comp_nodes: dict = {}
    for k, e in enumerate(ends[n0:]):
        if e is None:
            continue
        r = find(e[0])
        comp_segs.setdefault(r, []).append(near[k])
        comp_nodes.setdefault(r, set()).update(e)
    added = 0
    for r, members in comp_segs.items():
        if len(comp_nodes[r] & anchored) >= 2:
            for s in members:
                cl.segs.append(s)
                taken.add(id(s))
                added += 1
    return added


# --------------------------------------------------------------------------
# Deterministic types: stair and kitchen counter
# --------------------------------------------------------------------------

def _frame(theta: float):
    """(page -> aligned frame, aligned frame -> page) point maps for the plan's dominant angle ``theta``."""
    t = math.radians(theta)
    c, s = math.cos(t), math.sin(t)

    def to_f(p):
        return (p[0] * c + p[1] * s, -p[0] * s + p[1] * c)

    def from_f(p):
        return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
    return to_f, from_f


def _straight(segs: list[Seg], to_f) -> list[tuple[str, float, float, float, Seg]]:
    """Axis segments in the aligned frame: (axis, offset, lo, hi, seg); axis "h" lies along x."""
    out = []
    for s in segs:
        if s.curve or s.dot:
            continue
        a, b = to_f(s.pts[0]), to_f(s.pts[-1])
        if abs(a[1] - b[1]) <= 0.003 and abs(a[0] - b[0]) > 0.003:
            out.append(("h", (a[1] + b[1]) / 2, min(a[0], b[0]), max(a[0], b[0]), s))
        elif abs(a[0] - b[0]) <= 0.003 and abs(a[1] - b[1]) > 0.003:
            out.append(("v", (a[0] + b[0]) / 2, min(a[1], b[1]), max(a[1], b[1]), s))
    return out


def stair_rule(cl: Cluster, theta: float) -> Optional[dict]:
    """Flights of evenly spaced tread lines (§2.8): ``{"flights", "landing", "bbox_f", "segs"}`` in the aligned
    frame, or None."""
    to_f, from_f = _frame(theta)
    axis_segs = _straight(cl.segs, to_f)
    best = None
    for axis in ("h", "v"):
        treads = _merge_collinear([x for x in axis_segs if x[0] == axis])
        if len(treads) < STAIR_MIN_TREADS:
            continue
        others = [x for x in axis_segs if x[0] != axis]
        # A perpendicular divider crossing >= 80 % of the treads splits them.
        cuts = []
        for o in others:
            # treads: (offset, lo, hi, members); o: (axis, offset, lo, hi, seg)
            crossing = [t for t in treads if t[1] + 0.01 < o[1] < t[2] - 0.01 and o[2] - 0.005 <= t[0] <= o[3] + 0.005]
            if len(crossing) >= STAIR_DIVIDER_SHARE * len(treads):
                cuts.append(o[1])
        cuts = sorted(set(round(c, 3) for c in cuts))
        pieces = []
        for off, lo, hi, members in treads:
            bounds = [lo] + [c for c in cuts if lo + 0.01 < c < hi - 0.01] + [hi]
            for u, v in zip(bounds, bounds[1:]):
                pieces.append((off, u, v, members))
        flights = []
        sides: dict = {}
        for off, u, v, members in pieces:
            key = (round(u / 0.01), round(v / 0.01))
            sides.setdefault(key, []).append((off, u, v, members))
        for key, group in sides.items():
            flight = _flight(sorted(group, key=lambda g: g[0]))
            if flight:
                flights.append(flight)
        if flights and (best is None or sum(f["lines"] for f in flights) > sum(f["lines"] for f in best[1])):
            best = (axis, flights, cuts)
    if best is None:
        return None
    axis, flights, cuts = best
    xs = [p[0] for s in cl.segs for p in map(to_f, s.pts)]
    ys = [p[1] for s in cl.segs for p in map(to_f, s.pts)]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    lo_off = min(f["offsets"][0] for f in flights)
    hi_off = max(f["offsets"][-1] for f in flights)
    lo_end, hi_end = (bbox[1], bbox[3]) if axis == "h" else (bbox[0], bbox[2])
    landing = None
    if hi_end - hi_off >= 0.3 and hi_end - hi_off >= lo_off - lo_end:
        landing = (hi_off, hi_end)
    elif lo_off - lo_end >= 0.3:
        landing = (lo_end, lo_off)

    def pt(along_axis_pos, off):
        return from_f((along_axis_pos, off)) if axis == "h" else from_f((off, along_axis_pos))

    out_flights = []
    for f in sorted(flights, key=lambda f: f["u"]):
        mid = (f["u"] + f["v"]) / 2.0
        out_flights.append({"start": _r(pt(mid, f["offsets"][0])), "end": _r(pt(mid, f["offsets"][-1])),
                            "width": round(f["v"] - f["u"], 4), "lines": f["lines"],
                            "spacing": round(f["spacing"], 4)})
    land = None
    if landing:
        u = min(f["u"] for f in flights)
        v = max(f["v"] for f in flights)
        corners = [pt(u, landing[0]), pt(v, landing[0]), pt(v, landing[1]), pt(u, landing[1])]
        land = {"polygon": [list(_r(c)) for c in corners], "depth": round(landing[1] - landing[0], 4)}
    used = {id(s) for f in flights for s in f["segs"]}
    return {"flights": out_flights, "landing": land, "axis": axis, "bbox_f": bbox, "theta": theta,
            "tread_segs": used, "dividers": cuts}


def _r(p) -> tuple[float, float]:
    return (round(p[0], 4), round(p[1], 4))


def _merge_collinear(items) -> list[tuple[float, float, float, list]]:
    """Strokes on one line (within 5 mm) with overlapping or touching extents become one (union extent)."""
    out: list[list] = []
    for axis, off, lo, hi, s in sorted(items, key=lambda x: (x[1], x[2])):
        for m in out:
            if abs(m[0] - off) <= STAIR_MERGE_M and lo <= m[2] + STAIR_MERGE_M and hi >= m[1] - STAIR_MERGE_M:
                m[1], m[2] = min(m[1], lo), max(m[2], hi)
                m[3].append(s)
                break
        else:
            out.append([off, lo, hi, [s]])
    return [tuple(m) for m in out]


def _flight(group) -> Optional[dict]:
    """>= 5 equal, evenly spaced (0.20-0.35 m +- 10 %) tread segments."""
    if len(group) < STAIR_MIN_TREADS:
        return None
    offs = [g[0] for g in group]
    steps = [b - a for a, b in zip(offs, offs[1:])]
    if not steps:
        return None
    med = statistics.median(steps)
    if not STAIR_STEP_M[0] * (1 - STAIR_STEP_TOL) <= med <= STAIR_STEP_M[1] * (1 + STAIR_STEP_TOL):
        return None
    if any(abs(st - med) > STAIR_STEP_TOL * med for st in steps):
        return None
    return {"offsets": offs, "u": group[0][1], "v": group[0][2], "lines": len(group), "spacing": med,
            "segs": [s for g in group for s in g[3]]}


def _chains(segs: list[Seg], to_f) -> list[list[Seg]]:
    """Straight axis segments joined end to end (within 5 mm) into simple chains, in order."""
    straight = [s for s in segs if not s.curve and not s.dot]
    ends, coords = _end_nodes(straight)
    adj: dict = {}
    for i, e in enumerate(ends):
        if e is None:
            continue
        adj.setdefault(e[0], []).append(i)
        adj.setdefault(e[1], []).append(i)
    seen = set()
    chains = []
    for i in range(len(straight)):
        if i in seen or ends[i] is None:
            continue
        # Walk to one end of the chain, then collect forward.
        comp = []
        stack = [i]
        while stack:
            k = stack.pop()
            if k in seen:
                continue
            seen.add(k)
            comp.append(k)
            for n in ends[k]:
                stack.extend(j for j in adj[n] if j not in seen)
        degrees = {}
        for k in comp:
            for n in ends[k]:
                degrees[n] = degrees.get(n, 0) + 1
        if any(d > 2 for d in degrees.values()):
            continue
        start_nodes = [n for n, d in degrees.items() if d == 1]
        if len(start_nodes) != 2:
            continue
        order, node, used = [], start_nodes[0], set()
        while True:
            nxt = [k for k in adj[node] if k in comp and k not in used]
            if not nxt:
                break
            k = nxt[0]
            used.add(k)
            order.append(straight[k])
            a, b = ends[k]
            node = b if a == node else a
        chains.append((order, coords[start_nodes[0]], coords[node]))
    return chains


def counter_rule(cl: Cluster, walls: list, openings: list, theta: float) -> list[dict]:
    """Kitchen counter legs (§2.8): a chain of >= 2 straight segments whose two ends lie within 50 mm of a wall
    face (openings included) with segments parallel to a wall face at 0.45-0.75 m. Returns one dict per leg
    ``{"rect_f", "front_f", "wall", "segs", "length", "depth"}`` (aligned frame)."""
    to_f, from_f = _frame(theta)
    faces = _wall_faces(walls, openings, to_f)
    out = []
    for chain, a_end, b_end in _chains(cl.segs, to_f):
        if len(chain) < 2:
            continue
        if not (_near_face(to_f(a_end), faces) and _near_face(to_f(b_end), faces)):
            continue
        legs = []
        for s in chain:
            p, q = to_f(s.pts[0]), to_f(s.pts[-1])
            if _is_cap(p, q, faces):
                continue
            for f in faces:
                if f["axis"] == "h" and abs(p[1] - q[1]) <= 0.003:
                    d = (p[1] + q[1]) / 2 - f["pos"]
                    lo, hi = sorted((p[0], q[0]))
                    if COUNTER_DEPTH_M[0] <= abs(d) <= COUNTER_DEPTH_M[1] and math.copysign(1, d) == f["normal"] \
                            and min(hi, f["hi"]) - max(lo, f["lo"]) >= 0.8 * (hi - lo):
                        legs.append({"seg": s, "axis": "h", "lo": lo, "hi": hi, "front": (p[1] + q[1]) / 2,
                                     "back": f["pos"], "face": f})
                        break
                if f["axis"] == "v" and abs(p[0] - q[0]) <= 0.003:
                    d = (p[0] + q[0]) / 2 - f["pos"]
                    lo, hi = sorted((p[1], q[1]))
                    if COUNTER_DEPTH_M[0] <= abs(d) <= COUNTER_DEPTH_M[1] and math.copysign(1, d) == f["normal"] \
                            and min(hi, f["hi"]) - max(lo, f["lo"]) >= 0.8 * (hi - lo):
                        legs.append({"seg": s, "axis": "v", "lo": lo, "hi": hi, "front": (p[0] + q[0]) / 2,
                                     "back": f["pos"], "face": f})
                        break
        if not legs:
            continue
        # The corner square goes to the longer leg: extend it to the other leg's wall face.
        for i in range(len(legs)):
            for j in range(len(legs)):
                if i == j or legs[i]["axis"] == legs[j]["axis"]:
                    continue
                li, lj = legs[i], legs[j]
                if (li["hi"] - li["lo"]) < (lj["hi"] - lj["lo"]):
                    continue
                # Does lj's front line meet li's extent end? Extend li to lj's back face.
                if abs(lj["front"] - li["hi"]) <= COUNTER_END_M and abs(lj["back"] - li["hi"]) <= COUNTER_DEPTH_M[1]:
                    li["hi"] = max(li["hi"], lj["back"])
                elif abs(lj["front"] - li["lo"]) <= COUNTER_END_M:
                    li["lo"] = min(li["lo"], lj["back"])
        for leg in legs:
            f0, f1 = sorted((leg["front"], leg["back"]))
            rect = (leg["lo"], f0, leg["hi"], f1) if leg["axis"] == "h" else (f0, leg["lo"], f1, leg["hi"])
            front_dir = (0.0, math.copysign(1.0, leg["front"] - leg["back"])) if leg["axis"] == "h" else \
                (math.copysign(1.0, leg["front"] - leg["back"]), 0.0)
            out.append({"rect_f": rect, "front_f": front_dir, "segs": chain, "leg": leg["seg"],
                        "length": leg["hi"] - leg["lo"], "depth": abs(leg["front"] - leg["back"]),
                        "wall_face": leg["face"]})
    return out


def _wall_faces(walls: list, openings: list, to_f) -> list[dict]:
    """Both long faces of every axis wall in the aligned frame: {"axis", "pos", "lo", "hi", "normal"} where
    ``normal`` is the side of the face away from the wall (+1 / -1)."""
    faces = []
    for w in walls:
        start, end, t = (w["start"], w["end"], w["thickness"]) if isinstance(w, dict) else (w.start, w.end, w.thickness)
        a, b = to_f(start), to_f(end)
        if abs(a[1] - b[1]) <= 0.01:
            c, lo, hi = (a[1] + b[1]) / 2, min(a[0], b[0]), max(a[0], b[0])
            faces.append({"axis": "h", "pos": c + t / 2, "lo": lo, "hi": hi, "normal": 1.0})
            faces.append({"axis": "h", "pos": c - t / 2, "lo": lo, "hi": hi, "normal": -1.0})
        elif abs(a[0] - b[0]) <= 0.01:
            c, lo, hi = (a[0] + b[0]) / 2, min(a[1], b[1]), max(a[1], b[1])
            faces.append({"axis": "v", "pos": c + t / 2, "lo": lo, "hi": hi, "normal": 1.0})
            faces.append({"axis": "v", "pos": c - t / 2, "lo": lo, "hi": hi, "normal": -1.0})
    return faces


def _is_cap(p, q, faces: list[dict]) -> bool:
    """A segment with one end on a wall face, perpendicular to that face: the end of a counter run, not a leg."""
    horizontal = abs(p[1] - q[1]) <= 0.003
    for end in (p, q):
        for f in faces:
            if f["axis"] == "h" and not horizontal and abs(end[1] - f["pos"]) <= COUNTER_END_M \
                    and f["lo"] - COUNTER_END_M <= end[0] <= f["hi"] + COUNTER_END_M:
                return True
            if f["axis"] == "v" and horizontal and abs(end[0] - f["pos"]) <= COUNTER_END_M \
                    and f["lo"] - COUNTER_END_M <= end[1] <= f["hi"] + COUNTER_END_M:
                return True
    return False


def _near_face(p, faces: list[dict]) -> bool:
    """Whether point ``p`` (aligned frame) lies within 50 mm of a wall face."""
    for f in faces:
        across, along = (p[1], p[0]) if f["axis"] == "h" else (p[0], p[1])
        if abs(across - f["pos"]) <= COUNTER_END_M and f["lo"] - COUNTER_END_M <= along <= f["hi"] + COUNTER_END_M:
            return True
    return False


# --------------------------------------------------------------------------
# Footprints, fronts, evidence
# --------------------------------------------------------------------------

def min_rect(pts) -> tuple[list[tuple[float, float]], float]:
    """Corners and area of the minimum-area rectangle of a point set (cv2.minAreaRect, fast on thousands of
    points; coordinates are shifted to the first point to keep float32 precision)."""
    import cv2

    arr = np.asarray(pts, dtype=np.float64)
    o = arr[0]
    box = cv2.boxPoints(cv2.minAreaRect((arr - o).astype(np.float32)))
    corners = [(float(x) + o[0], float(y) + o[1]) for x, y in box]
    return corners, math.dist(corners[0], corners[1]) * math.dist(corners[1], corners[2])


def circle_fit(segs: list[Seg]) -> Optional[dict]:
    """``{"share", "radius"}`` of a least-squares circle through the piece's outline: the convex hull of its stroke
    points, sampled every ~1 cm (sampling the outline, not the vertices: a rectangle's 4 corners lie on a circle
    too). ``share`` = the fraction of the outline within max(10 mm, 3 % r) of the circle."""
    from shapely.geometry import MultiPoint

    pts = [p for s in segs for p in s.pts]
    if len(set(pts)) < 3:
        return None
    hull = MultiPoint(pts).convex_hull
    if hull.geom_type != "Polygon" or hull.area <= 0:
        return None
    ring = hull.exterior
    n = max(64, min(2000, int(ring.length / 0.01)))
    samples = np.array([ring.interpolate(k * ring.length / n).coords[0] for k in range(n)])
    o = samples.mean(axis=0)
    xs, ys = samples[:, 0] - o[0], samples[:, 1] - o[1]
    a = np.c_[2.0 * xs, 2.0 * ys, np.ones(n)]
    sol, *_ = np.linalg.lstsq(a, xs * xs + ys * ys, rcond=None)
    cx, cy, c = sol
    r2 = c + cx * cx + cy * cy
    if r2 <= 0:
        return None
    r = math.sqrt(r2)
    d = np.hypot(xs - cx, ys - cy)
    share = float(np.mean(np.abs(d - r) <= max(ROUND_TOL_M, ROUND_TOL_REL * r)))
    return {"share": round(share, 3), "radius": round(r, 4)}


def round_shape(segs: list[Seg]) -> dict:
    """``{"shape": "round", "circle_fit": {...}}`` when a circle fits >= 90 % of the piece's outline
    (docs/milestone7.md §6.4: a round side table), else ``{}``."""
    fit = circle_fit(segs)
    if fit is None or fit["share"] < ROUND_SHARE:
        return {}
    return {"shape": "round", "circle_fit": fit}


def footprint(pts, theta: float) -> tuple[tuple[float, float], float, float, float, list]:
    """(centre, extent along u, extent along v, angle of u in deg, corners): the minimum-area rectangle, snapped to
    the plan's dominant orientation when within 3 deg of it."""
    to_f, from_f = _frame(theta)
    fp = [to_f(p) for p in pts]
    xs = [p[0] for p in fp]
    ys = [p[1] for p in fp]
    frame_area = (max(xs) - min(xs)) * (max(ys) - min(ys))
    c, area = min_rect(pts)
    if len(pts) >= 3 and area > 1e-12 and frame_area > 1.02 * area:     # round pieces stay in the frame
        c = c + [c[0]]
        ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0]))
        off = (ang - theta) % 90.0
        off = min(off, 90.0 - off)
        if off > SNAP_DEG:
            angle_u = ang % 180.0
            ext_u, ext_v = math.dist(c[0], c[1]), math.dist(c[1], c[2])
            centre = ((c[0][0] + c[2][0]) / 2.0, (c[0][1] + c[2][1]) / 2.0)
            return centre, ext_u, ext_v, angle_u, [tuple(p) for p in c[:4]]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    centre = from_f(((x0 + x1) / 2.0, (y0 + y1) / 2.0))
    return centre, x1 - x0, y1 - y0, theta % 180.0, corners


def size_rotation(ext_u: float, ext_v: float, angle_u: float, front_deg: Optional[float]):
    """(size [width, depth], rotation_deg) in the codebase convention: an unrotated piece faces -Y, width across
    the front; without a front the width is the longer side."""
    if front_deg is None:
        if ext_u >= ext_v:
            return (round(ext_u, 4), round(ext_v, 4)), round(angle_u % 180.0, 3)
        return (round(ext_v, 4), round(ext_u, 4)), round((angle_u + 90.0) % 180.0, 3)
    rotation = (front_deg + 90.0) % 360.0
    d = abs((front_deg - angle_u + 90.0) % 180.0 - 90.0)      # 0 when the front is along u
    if d < 45.0:
        return (round(ext_v, 4), round(ext_u, 4)), round(rotation, 3)
    return (round(ext_u, 4), round(ext_v, 4)), round(rotation, 3)


def id_ranges(ids) -> str:
    """``line:3,line:4,line:5,curve:9`` -> ``curve:9,line:3-5`` (segment suffixes dropped). Numeric ids are
    grouped into ranges per prefix; other ids (``INSERT:4B/3``) follow sorted, so the text does not depend on the
    cluster order (a DWG and its DXF give the same evidence)."""
    groups: dict[str, list[int]] = {}
    other: list[str] = []
    for sid in ids:
        base = sid.split("#", 1)[0]
        head, _, tail = base.partition(":")
        if tail.isdigit():
            groups.setdefault(head, []).append(int(tail))
        elif base not in other:
            other.append(base)
    parts = []
    for head in sorted(groups):
        nums = sorted(set(groups[head]))
        start = prev = nums[0]
        for n in nums[1:] + [None]:
            if n is not None and n == prev + 1:
                prev = n
                continue
            parts.append(f"{head}:{start}" if start == prev else f"{head}:{start}-{prev}")
            if n is not None:
                start = prev = n
    return ",".join(parts + sorted(other))


def _sides(corners) -> list[tuple[tuple, tuple]]:
    return [(corners[i], corners[(i + 1) % 4]) for i in range(4)]


def _outward_deg(side, centre) -> float:
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    return math.degrees(math.atan2(my - centre[1], mx - centre[0])) % 360.0


def _snap_deg(deg: float, theta: float) -> float:
    k = round((deg - theta) / 90.0)
    return round((theta + 90.0 * k) % 360.0, 3)


def front_candidates(piece_segs: list[Seg], centre, corners, wall_polys: list, others: list, theta: float,
                     table: dict) -> list[dict]:
    """Deterministic front candidates (§2.8): the only side within 0.25 m of a wall is the back; the side holding
    >= 2 small closed shapes is a bed's head (pillows); a chair-sized piece faces the nearest table-sized piece."""
    out = []
    sides = _sides(corners)
    near = []
    for side in sides:
        seg = LineString(side)
        mid = seg.interpolate(0.5, normalized=True)
        if any(w.distance(mid) <= FRONT_WALL_M for w in wall_polys):
            near.append(side)
    if len(near) == 1:
        back = _outward_deg(near[0], centre)
        out.append({"front_deg": _snap_deg(back + 180.0, theta),
                    "rule": "only side within 0.25 m of a wall is the back"})
    # Pillows: >= 2 small closed contours next to one side.
    small = [p for p, _ in contours(piece_segs) if 0.15 <= max(_rect_sides(p)) <= 0.8 and min(_rect_sides(p)) >= 0.08]
    if len(small) >= 2:
        best = None
        for k, side in enumerate(sides):
            line = LineString(side)
            reach = 0.3 * math.dist(*sides[(k + 1) % 4])          # 30 % of the piece's extent away from the side
            n = sum(1 for p in small if line.distance(p.centroid) <= reach)
            if n >= 2 and (best is None or n > best[0]):
                best = (n, side)
        if best is not None:
            head = _outward_deg(best[1], centre)
            out.append({"front_deg": _snap_deg(head + 180.0, theta),
                        "rule": "head = side with >= 2 small closed shapes"})
    # A chair faces the nearest table.
    u = math.dist(*sides[0])
    v = math.dist(*sides[1])
    if max(u, v) <= 0.7:
        best = None
        for o in others:
            if o["poly"] is None:
                continue
            if not (fits(table, "table_dining", o["size"]) or fits(table, "table_coffee", o["size"])):
                continue
            seats = [x for x in others
                     if x is not o and max(x["size"]) <= 0.7 and x["poly"].distance(o["poly"]) <= 0.5]
            if len(seats) + 1 < 2:                    # a table has at least two seats around it
                continue
            d = o["poly"].distance(Point(centre))
            if d <= 0.5 + max(u, v) / 2 and (best is None or d < best[0]):
                best = (d, o)
        if best is not None:
            tc = best[1]["poly"].centroid
            deg = math.degrees(math.atan2(tc.y - centre[1], tc.x - centre[0]))
            out.append({"front_deg": _snap_deg(deg, theta), "rule": "chair faces the nearest table"})
    uniq: list[dict] = []
    for c in out:
        same = [u for u in uniq if abs(c["front_deg"] - u["front_deg"]) < 1e-6]
        if same:
            same[0]["rule"] += "; " + c["rule"]          # rules that agree are kept together
        else:
            uniq.append(dict(c))
    return uniq


# --------------------------------------------------------------------------
# Main entry
# --------------------------------------------------------------------------

@dataclass
class _Ctx:
    file_rel: str
    page_no: Optional[int]
    units_to_m: Optional[float]
    theta: float
    level_id: Optional[str]

    def evidence(self, ids, confidence: float = FOOTPRINT_CONFIDENCE, raster: bool = False, box=None,
                 method: Optional[str] = None, note: Optional[str] = None) -> dict:
        m = method or ("raster" if raster else "vector")
        if m == "raster":
            confidence = min(confidence, 0.7)
        ev = B.evidence(self.file_rel, m, round(confidence, 3), page=self.page_no, entity=id_ranges(ids) or None,
                        pixel_box=box if (m == "raster" and box) else None)
        if note:
            ev["note"] = note
        return ev

    def box(self, corners) -> list[float]:
        xs = [p[0] for p in corners]
        ys = [p[1] for p in corners]
        bx = [min(xs), min(ys), max(xs), max(ys)]
        if self.units_to_m:
            bx = [v / self.units_to_m for v in bx]
        return [round(v, 3) for v in bx]


def _face_info(faces, point) -> tuple[Optional[str], Optional[str]]:
    """(room_type, label) of the face containing ``point``; faces are polygons, point lists or dicts with
    ``polygon`` and optional ``room_type``/``label``."""
    for f in faces or []:
        if isinstance(f, dict):
            poly = f.get("polygon")
            poly = poly if hasattr(poly, "contains") else Polygon(poly)
            if poly.contains(Point(point)):
                return f.get("room_type"), f.get("label")
        else:
            poly = f if hasattr(f, "contains") else Polygon(f)
            if poly.contains(Point(point)):
                return None, None
    return None, None


def furniture(strokes_m: list[Stroke], owned: set, walls: list[WallItem], openings: list[OpeningItem], texts_m: list,
              dims: list, outline, faces: list, *, wall_strokes=(), site_walls=(), level_id: Optional[str] = None,
              file_rel: Optional[str] = None, page_no: Optional[int] = None, units_to_m: Optional[float] = None,
              size_table: Optional[dict] = None, notes: Optional[list] = None
              ) -> tuple[list[FurnitureItem], list[dict], list[dict]]:
    """Furniture pieces typed by rules or block names, AI candidates and site decor (all page metres).

    ``owned``: stroke ids the openings own; ``wall_strokes``: ids of the wall primitives (hatch lines, fills) that are
    walls; ``site_walls``: the plot/other walls (WallItems or ``site.boundary_walls`` dicts) so their outline strokes
    are not decor; ``outline``: the building outline (shapely polygon or point list; None -> from ``walls``);
    ``faces``: room faces (polygons, or dicts with ``polygon``, ``room_type``, ``label``) for room checks and hints;
    ``dims``: dimension candidates exposing ``stroke_ids``. ``notes`` (a list) receives report lines.
    Returns ``(pieces, candidates, decor)``: rule/block-name typed pieces plus the unknown composites and oversize
    clusters (never asked); AI candidate dicts ``{key, footprint, strokes, bbox, room_hint, front_candidates, fits,
    item}`` whose ``item`` is the FurnitureItem (``unknown``, ``unverified``, ``type_method "none"``) to keep until
    answers exist; site decor dicts ``{kind, center, size, evidence[, id]}``.
    """
    notes = notes if notes is not None else []
    if size_table is None:
        table, source = load_size_table()
    else:
        table, source = size_table, "given size table"
    notes.append(f"furniture size checks use the {source}")
    ref = walls[0].evidence if walls else {}
    ctx = _Ctx(file_rel or ref.get("file", ""), page_no if page_no is not None else ref.get("page"), units_to_m,
               _dominant(walls), level_id)
    raster_page = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)

    drop = set(owned or ()) | set(wall_strokes or ()) | _dimension_ids(dims)
    segs = _segments(strokes_m, drop)
    boxes = _text_boxes(texts_m)
    if boxes:
        tree = STRtree(boxes)
        kept = []
        glyphs = 0
        for s in segs:
            hits = tree.query(s.geom, predicate="within")
            if len(hits):
                glyphs += 1
            else:
                kept.append(s)
        segs = kept
        if glyphs:
            notes.append(f"{glyphs} glyph strokes inside text boxes ignored")
    wall_geom = _wall_geometry(walls, openings, list(site_walls or ()))
    kept, n_outline = _drop_outline(segs, wall_geom)
    kept_ids = {id(s) for s in kept}
    near_wall = [s for s in segs if id(s) not in kept_ids]
    notes.append(f"{n_outline} stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)")

    poly = _as_polygon(outline)
    if poly is None or poly.is_empty:
        poly = TP.building_outline(walls, openings)
    inside_poly = poly.buffer(0.001)
    shapely.prepare(inside_poly)
    mids = np.array([s.geom.centroid if not s.dot else s.geom for s in kept], dtype=object)
    inside_mask = shapely.contains(inside_poly, mids) if len(mids) else np.zeros(0, bool)
    inside = [s for s, m in zip(kept, inside_mask) if m]
    outside = [s for s, m in zip(kept, inside_mask) if not m]
    pool = [s for s in near_wall if inside_poly.contains(s.geom.centroid if not s.dot else s.geom)]

    clusters = clusters_of(inside)
    taken: set = set()
    for cl in sorted(clusters, key=lambda c: -_bbox_area(c.bounds())):
        reclose(cl, pool, taken)
    clusters = _merge_contained(clusters, table)

    wall_polys = [TP.wall_polygon(w) for w in walls]
    pieces: list[FurnitureItem] = []
    cands: list[dict] = []
    details = 0
    parts_all: list[tuple[Cluster, int]] = []
    for cl in clusters:
        w, h = cl.size()
        if max(w, h) < DETAIL_M:
            details += 1
            continue
        fp = footprint([p for s in cl.segs for p in s.pts], ctx.theta)
        if max(fp[1], fp[2]) > MAX_SIDE_M:
            pieces.append(_unknown(cl, fp, ctx, raster_page, f"cluster larger than {MAX_SIDE_M} m on a side",
                                   {"oversize": True}))
            notes.append(f"cluster {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}) larger than "
                         f"{MAX_SIDE_M} m: unknown, unverified, not asked")
            continue
        stair = stair_rule(cl, ctx.theta)
        if stair is not None:
            pieces.append(_stair_item(cl, stair, fp, ctx, raster_page, notes))
            continue
        legs = counter_rule(cl, walls, openings, ctx.theta)
        if legs:
            used = set()
            for leg in legs:
                pieces.append(_counter_item(leg, walls, ctx, raster_page))
                used.update(id(s) for s in leg["segs"])
            rest = [s for s in cl.segs if id(s) not in used]
            for sub in clusters_of(rest, CLUSTER_M):
                if max(sub.size()) >= DETAIL_M:
                    parts_all.extend(split_composite(sub, table))
                else:
                    details += 1
            continue
        parts_all.extend(split_composite(cl, table))

    # Footprints of all parts first (the chair rule looks at the tables).
    infos = []
    for part, n in parts_all:
        if max(part.size()) < DETAIL_M:
            details += 1
            continue
        pts = [p for s in part.segs for p in s.pts]
        fp = footprint(pts, ctx.theta)
        infos.append({"part": part, "n": n, "fp": fp, "size": (fp[1], fp[2]), "poly": Polygon(fp[4])})
    for info in infos:
        part, n, fp = info["part"], info["n"], info["fp"]
        shape = round_shape(part.segs) if n == 1 else {}
        block_item = _block_item(part, fp, ctx, raster_page, table)
        if block_item is not None:
            block_item.details.update(shape)
            pieces.append(block_item)
            continue
        types = fitting_types(table, (fp[1], fp[2]))
        if n > 1 or not types:
            reason = (f"possible group of {n} pieces" if n > 1 else "fits no size-table type")
            pieces.append(_unknown(part, fp, ctx, raster_page, reason,
                                   dict({"composite": n} if n > 1 else {}, **shape)))
            notes.append(f"unknown piece {fp[1]:.2f} x {fp[2]:.2f} m at ({fp[0][0]:.2f}, {fp[0][1]:.2f}): {reason}")
            continue
        others = [o for o in infos if o is not info]
        fronts = front_candidates(part.segs, fp[0], fp[4], wall_polys, others, ctx.theta, table)
        cand = _candidate(part, fp, ctx, raster_page, faces, fronts, types, len(cands) + 1)
        cand["item"].details.update(shape)
        cands.append(cand)
    if details:
        notes.append(f"{details} drawn details smaller than {DETAIL_M} m ignored")
    decor = _site_decor(outside, ctx, raster_page, notes, wall_geom)
    apply_room_checks(pieces, cands, faces, notes)
    return pieces, cands, decor


def apply_room_checks(pieces: list[FurnitureItem], candidates: list[dict], faces: list, notes: list) -> None:
    """Room-dependent parts of §2.8, also callable again once the separators are known: a kitchen counter is
    ``verified`` only in a kitchen; a rule stair in a face that is neither hall nor unlabelled is ``unverified``;
    candidates get their ``room_hint``. ``faces``: dicts with ``polygon``, ``room_type``, ``label`` (or bare
    polygons, which carry no room type)."""
    for p in pieces:
        room_type, label = _face_info(faces, p.center)
        if p.type == "kitchen_counter" and p.type_method == "rule":
            p.status = "verified" if room_type == "kitchen" else "unverified"
            if p.status == "unverified" and faces:
                notes.append(f"kitchen counter at ({p.center[0]:.2f}, {p.center[1]:.2f}) not in a kitchen "
                             f"({label or 'unlabelled'}): unverified")
        elif p.type == "stair" and p.type_method == "rule":
            if label is not None and room_type not in (None, "hall", "unknown"):
                if p.status != "unverified":
                    notes.append(f"stair drawn in the labelled room '{label}' ({room_type}): unverified")
                p.status = "unverified"
    for c in candidates:
        room_type, label = _face_info(faces, c["footprint"]["center"])
        c["room_hint"] = label or room_type


def _dominant(walls) -> float:
    from wenart.ingest.generic.openings import dominant_angle
    return dominant_angle(walls) if walls else 0.0


def _unknown(cl: Cluster, fp, ctx: _Ctx, raster: bool, reason: str, details: dict) -> FurnitureItem:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    ev = ctx.evidence(cl.stroke_ids(), raster=raster, box=box, note=reason)
    return FurnitureItem(type="unknown", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=cl.stroke_ids()[0], evidence=ev, status="unverified",
                         type_method="none", details=dict(details, reason=reason))


def _stair_item(cl: Cluster, stair: dict, fp, ctx: _Ctx, raster: bool, notes: list) -> FurnitureItem:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    status = "verified"
    flights = stair["flights"]
    turn = "U" if len(flights) == 2 else ("straight" if len(flights) == 1 else "other")
    a = flights[0]
    d = (a["end"][0] - a["start"][0], a["end"][1] - a["start"][1])
    n = math.hypot(*d) or 1.0
    reason = ("no UP arrow, break line or riser text drawn: rise direction and flight order are assumed"
              + ("; two side-by-side flights read as a U-turn (dog-leg) stair" if len(flights) == 2 else ""))
    details = {"stair": {"flights": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in f.items()}
                                     for f in flights],
                         "landing": stair["landing"], "direction": [round(d[0] / n, 4), round(d[1] / n, 4)],
                         "direction_assumed": True, "turn": turn, "turn_assumed": True, "void_assumed": True,
                         "riser_m": None, "riser_source": None, "reason": reason}}
    ev = ctx.evidence(cl.stroke_ids(), raster=raster, box=box,
                      note=f"stair rule: {len(flights)} flight(s), {', '.join(str(f['lines']) for f in flights)} "
                           f"tread lines")
    widths = ", ".join(f"{f['width']:.3f}" for f in flights)
    notes.append(f"stair at ({fp[0][0]:.2f}, {fp[0][1]:.2f}): {len(flights)} flight(s) of {widths} m")
    return FurnitureItem(type="stair", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=cl.stroke_ids()[0], evidence=ev, status=status,
                         type_method="rule", details=details)


def _counter_item(leg: dict, walls: list, ctx: _Ctx, raster: bool) -> FurnitureItem:
    to_f, from_f = _frame(ctx.theta)
    x0, y0, x1, y1 = leg["rect_f"]
    corners = [from_f(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    centre = from_f(((x0 + x1) / 2, (y0 + y1) / 2))
    fdir = from_f(leg["front_f"])
    front_deg = round(math.degrees(math.atan2(fdir[1], fdir[0])) % 360.0, 3)
    size, rotation = size_rotation(x1 - x0, y1 - y0, ctx.theta % 180.0, front_deg)
    box = ctx.box(corners)
    status = "unverified"                      # verified by apply_room_checks when it stands in a kitchen
    ids = sorted({s.stroke.id for s in leg["segs"]}, key=_id_key)
    wall_index = None
    best = math.inf
    for k, w in enumerate(walls):
        d = TP.wall_polygon(w).distance(Polygon(corners))
        if d < best:
            best, wall_index = d, k
    ev = ctx.evidence(ids, raster=raster, box=box, note="kitchen counter rule: chained legs between wall faces")
    return FurnitureItem(type="kitchen_counter", type_raw=None, center=_r(centre), size=size, rotation_deg=rotation,
                         front_deg=front_deg, box=box, entity=ids[0], evidence=ev, status=status, type_method="rule",
                         details={"counter_run": {"wall_id": None, "wall_index": wall_index, "strokes": ids,
                                                  "depth": round(leg["depth"], 4), "length": round(x1 - x0 if
                                                  abs(leg["front_f"][1]) > 0 else y1 - y0, 4)}})


def block_type(names: list[str], size, table: dict) -> Optional[str]:
    """Furniture type from DXF block names (innermost first) by the keyword table, resolved by the size table for
    the generic words BED and TABLE; None when no keyword matches."""
    for name in names:
        upper = name.upper()
        for key, ftype in BLOCK_KEYWORDS:
            if key in upper:
                if ftype == "bed":
                    return "bed_double" if fits(table, "bed_double", size) else "bed_single"
                if ftype == "table":
                    for t in ("table_dining", "table_coffee", "desk"):
                        if fits(table, t, size):
                            return t
                    return "table_dining"
                return ftype
    return None


def _block_item(part: Cluster, fp, ctx: _Ctx, raster: bool, table: dict) -> Optional[FurnitureItem]:
    chains = [s.stroke.block for s in part.segs if s.stroke.block]
    if not chains or len(chains) < 0.6 * len(part.segs):
        return None
    chain = max(set(chains), key=chains.count)
    if chains.count(chain) < 0.6 * len(part.segs):
        return None
    names = list(reversed(chain.split("/")))
    ftype = block_type(names, (fp[1], fp[2]), table)
    if ftype is None:
        return None
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    ok = fits(table, ftype, (fp[1], fp[2]))
    note = None if ok else f"block name says {ftype} but {fp[1]:.2f} x {fp[2]:.2f} m does not fit its size range"
    ev = ctx.evidence(part.stroke_ids(), confidence=0.9, raster=raster, box=box, note=note)
    ev["block"] = chain
    return FurnitureItem(type=ftype, type_raw=chain, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=part.stroke_ids()[0], evidence=ev,
                         status="verified" if ok else "unverified", type_method="block_name")


def _candidate(part: Cluster, fp, ctx: _Ctx, raster: bool, faces, fronts: list, types: list, n: int) -> dict:
    size, rotation = size_rotation(fp[1], fp[2], fp[3], None)
    box = ctx.box(fp[4])
    key = f"sym_{ctx.level_id}_{n:03d}" if ctx.level_id else f"sym_{n:03d}"
    room_type, label = _face_info(faces, fp[0])        # apply_room_checks refreshes it
    ev = ctx.evidence(part.stroke_ids(), raster=raster, box=box)
    item = FurnitureItem(type="unknown", type_raw=None, center=_r(fp[0]), size=size, rotation_deg=rotation,
                         front_deg=None, box=box, entity=part.stroke_ids()[0], evidence=ev, status="unverified",
                         type_method="none", details={"candidate_key": key, "front_candidates": fronts})
    xs = [p[0] for s in part.segs for p in s.pts]
    ys = [p[1] for s in part.segs for p in s.pts]
    return {"key": key, "footprint": {"center": list(_r(fp[0])), "size": list(size), "rotation_deg": rotation},
            "strokes": [[list(_r(p)) for p in s.pts] for s in part.segs],
            "bbox": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
            "room_hint": label or room_type, "front_candidates": fronts, "fits": types, "item": item}


def raster_clusters(segs: list[Seg], dist: float = CLUSTER_M, px: float = 0.01) -> list[Cluster]:
    """Clusters of strokes closer than about ``dist``, from connected components of the strokes drawn on a ``px``
    raster with a line width reaching ``dist``. Used for site decor, where dense plant fills (real01: 9 x ~2,500
    segments) make the exact pairwise clustering slow and stroke-exact grouping is not needed."""
    import cv2

    if not segs:
        return []
    xs = [p[0] for s in segs for p in s.pts]
    ys = [p[1] for s in segs for p in s.pts]
    x0, y0 = min(xs) - 3 * px, min(ys) - 3 * px
    w = int((max(xs) - x0) / px) + 4
    h = int((max(ys) - y0) / px) + 4
    while w * h > 6e7:
        px *= 2.0
        w = int((max(xs) - x0) / px) + 4
        h = int((max(ys) - y0) / px) + 4
    img = np.zeros((h, w), np.uint8)
    thick = max(1, int(math.ceil(dist / px)))
    polys = []
    for s in segs:
        arr = np.array([[int((p[0] - x0) / px), int((p[1] - y0) / px)] for p in s.pts], np.int32)
        polys.append(arr)
    cv2.polylines(img, polys, False, 255, thick, cv2.LINE_8)
    n, lab = cv2.connectedComponents(img, connectivity=8)
    groups: dict = {}
    for s, arr in zip(segs, polys):
        c, r = arr[0]
        groups.setdefault(int(lab[r, c]), []).append(s)
    return [Cluster(v) for v in groups.values()]


def _site_decor(segs: list[Seg], ctx: _Ctx, raster: bool, notes: list, wall_geom=None) -> list[dict]:
    """Clusters outside the building: green fills or radial clusters -> plant; edge lines -> not decor; else other.
    Footprints leave out the parts of strokes lying on a wall face (an edge line continuing a house face)."""
    clusters = raster_clusters(segs)
    near = wall_geom.buffer(OUTLINE_NEAR_M, join_style=2) if wall_geom is not None and not wall_geom.is_empty else None
    out = []
    lines = 0
    for cl in clusters:
        w, h = cl.size()
        if max(w, h) < DETAIL_M:
            continue
        pts = [p for s in cl.segs for p in s.pts]
        if near is not None:
            clipped = []
            for s in cl.segs:
                g = s.geom.difference(near) if s.geom.intersects(near) else s.geom
                for part in getattr(g, "geoms", [g]):
                    if not part.is_empty:
                        clipped.extend(part.coords)
            pts = clipped or pts
        fp = footprint(pts, ctx.theta)
        if min(fp[1], fp[2]) < 0.05 or max(fp[1], fp[2]) > MAX_SIDE_M:
            lines += 1                                   # a boundary, edge or extension line, not an object
            continue
        fills = [s.stroke.fill for s in cl.segs if s.stroke.fill is not None]
        green = [f for f in fills if f[1] >= f[0] + 0.05 and f[1] >= f[2] + 0.05]
        kind = "plant" if fills and len(green) >= 0.3 * len(fills) else ("plant" if _radial(cl) else "other")
        box = ctx.box(fp[4])
        item = {"kind": kind, "center": list(_r(fp[0])), "size": [round(fp[1], 4), round(fp[2], 4)],
                "evidence": [ctx.evidence(cl.stroke_ids(), raster=raster, box=box)], "box": box}
        out.append(item)
    out.sort(key=lambda d: (d["center"][1], d["center"][0]))
    for n, item in enumerate(out, start=1):
        if ctx.level_id:
            item["id"] = f"sd_{ctx.level_id}_{n:03d}"
    if lines:
        notes.append(f"{lines} site edge or boundary line groups outside the building (not decor)")
    return out


def _radial(cl: Cluster) -> bool:
    """>= 8 straight strokes whose lines pass within 5 % of the cluster size of its centre (a drawn tree/plant)."""
    b = cl.bounds()
    c = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    tol = 0.05 * max(b[2] - b[0], b[3] - b[1])
    n = 0
    for s in cl.segs:
        if s.curve or s.dot:
            continue
        a, q = s.pts[0], s.pts[-1]
        length = math.dist(a, q)
        if length < 0.2 * max(b[2] - b[0], b[3] - b[1]):
            continue
        d = abs((q[0] - a[0]) * (a[1] - c[1]) - (a[0] - c[0]) * (q[1] - a[1])) / length
        if d <= tol:
            n += 1
    return n >= 8
