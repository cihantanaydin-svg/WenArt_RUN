"""Split a sheet into drawing regions (docs/milestone10.md §3.1 item 1).

What: ``split_sheet(sheet, n_doc_entities) -> SplitResult`` turns the entities and texts of one sheet into regions
(each drawing, title box and title block), the frames, and the stray entities far away from the drawings.

Why: one CAD sheet often holds several drawings (real02: four plans and a section in one frame); the pipeline must
read each plan on its own, in its own place, and know what the other drawings are.

How:
1. Sheet box and gap: the frame (the largest closed axis-aligned rectangle that holds >= 50 % of the entity centres),
   else the 2-98 % box of the entity centres. The clustering gap is ``GAP_REL`` (1.5 %) of its diagonal (real02:
   149 units; its drawings are 500-665 units apart).
2. Entities (texts excluded) are clustered by their boxes: two entities whose boxes are within the gap join. An
   INSERT is one entity with the box of its block geometry. Closed rectangles with both sides >= 5 % of the sheet
   are frame candidates and stay out of the first clustering; a candidate that holds >= 2 clusters is a **frame**
   (never part of a region: frames never bridge drawings) unless it lies inside another frame and holds fewer than
   two drawing titles: then it is a drawing's own boundary (a site plan's plot line) and everything it holds joins
   it; any other candidate joins the clustering again, through its four edges (so a title box that holds only
   texts is a region of its own, and the roof outline around a plan joins that plan).
   A cluster inside another drawing's box (a table in the middle of a room) joins it; a small cluster (<= 5 % of a
   drawing's box, or thin like a dimension chain) within half the drawing's shorter side and with 10 x fewer
   entities joins it too (a single drawing on a sheet without a frame stays one region).
3. Texts never bridge: each joins the region whose box holds its point (the smallest), else the nearest region of
   the same frame within ``TEXT_REACH`` gaps or 0.3 x that region's height (its title); texts left over are grouped
   among themselves (a notes block).
4. Strays: a cluster outside every frame (or, without a frame, more than ``STRAY_FAR`` x the median region size
   from every other region) with < 1 % of the document's entities is stray: listed, never read.
5. Region ids follow the reading order of the schema (``$defs/region.id``): top to bottom by the top of the region's
   box (its non-text entities), then left to right.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from wenart.sheets import titles as T
from wenart.sheets.model import (Box, Ent, Sheet, Txt, box_distance, box_inside, box_size, box_union, in_box,
                                 point_box_distance)

GAP_REL = 0.015            # clustering gap: 1.5 % of the sheet diagonal (§3.1 item 1; tested 0.5-3 %)
FRAME_MIN_REL = 0.05       # frame / title box candidates: both sides >= 5 % of the sheet's shorter side
FRAME_HOLD_SHARE = 0.5     # the sheet frame holds >= 50 % of the entity centres
FRAME_TOUCH_SHARE = 0.1    # a frame: < 10 % of the entities it holds lie within the gap of its edges
TEXT_REACH = 4.0           # a text joins the nearest region within this many gaps ...
TITLE_REACH = 0.3          # ... or within 0.3 x that region's height (a title above or below it, §3.1 item 2)
SATELLITE_AREA = 0.05      # a small cluster (<= 5 % of a drawing's box, or thin) ...
SATELLITE_THIN = 0.02      # ... (shorter side <= 2 % of the longer: a dimension chain) ...
SATELLITE_REACH = 0.5      # ... within 0.5 x the drawing's shorter side ...
SATELLITE_COUNT = 10       # ... with 10 x fewer entities joins that drawing
STRAY_SHARE = 0.01         # strays hold < 1 % of the document's entities
STRAY_FAR = 10.0           # ... and (no frame) lie > 10 x the median region size from every other region
PERCENTILES = (2.0, 98.0)
RASTER_STEPS = 8           # clustering raster: cells of gap / 8 ...
RASTER_MAX = 6000          # ... at most this many cells per side


@dataclass
class Cluster:
    ents: list[Ent] = field(default_factory=list)
    texts: list[Txt] = field(default_factory=list)
    frame: Optional[str] = None
    kind: str = "drawing"            # drawing | box | text

    @property
    def geometry_box(self) -> Optional[Box]:
        return box_union(e.box for e in self.ents) if self.ents else box_union(t.box for t in self.texts)

    @property
    def box(self) -> Box:
        boxes = [e.box for e in self.ents] + [(t.point[0], t.point[1], t.point[0], t.point[1]) for t in self.texts]
        return box_union(boxes)

    @property
    def size(self) -> int:
        return len(self.ents) + len(self.texts)


@dataclass
class SplitResult:
    box: Box
    gap: float
    frames: list[dict]               # [{"entity", "box"}]
    clusters: list[Cluster]          # regions in reading order
    strays: list[tuple[Cluster, float]]   # (cluster, distance to the nearest region in source units)


# --------------------------------------------------------------------------
# Union-find over boxes
# --------------------------------------------------------------------------

class _UF:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def _cluster_boxes(items: list[tuple[int, Box]], n: int, gap: float) -> _UF:
    """Union-find over ``n`` entities; ``items`` are (entity index, box) pairs (an entity may give several boxes).
    Two boxes whose gaps along x and along y are both <= ``gap`` join their entities.

    The boxes near the drawings (inside the 2-98 % box of the item centres grown by its own size) are painted, grown
    by half the gap, onto a raster of ``gap / RASTER_STEPS`` cells and joined by its connected components (exact to
    one cell, ~0.13 gap; dense CAD pages with tens of thousands of hatch paths stay fast). Boxes farther out (strays)
    are compared pairwise among themselves."""
    import cv2

    uf = _UF(n)
    if not items:
        return uf
    centres = np.asarray([((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0) for _, b in items], dtype=float)
    lo = np.percentile(centres, PERCENTILES[0], axis=0)
    hi = np.percentile(centres, PERCENTILES[1], axis=0)
    grow = np.maximum(hi - lo, gap) * 1.0 + gap
    core = (lo[0] - grow[0], lo[1] - grow[1], hi[0] + grow[0], hi[1] + grow[1])
    inner = [k for k, (_, b) in enumerate(items) if _overlap_or_touch(b, core)]
    outer = [k for k in range(len(items)) if not _overlap_or_touch(items[k][1], core)]
    cell = max(gap / RASTER_STEPS, 1e-9)
    if inner:
        x0 = min(max(items[k][1][0], core[0]) for k in inner) - gap
        y0 = min(max(items[k][1][1], core[1]) for k in inner) - gap
        x1 = max(min(items[k][1][2], core[2]) for k in inner) + gap
        y1 = max(min(items[k][1][3], core[3]) for k in inner) + gap
        cols = int(math.ceil((x1 - x0) / cell)) + 1
        rows = int(math.ceil((y1 - y0) / cell)) + 1
        scale = min(1.0, RASTER_MAX / max(cols, rows))
        if scale < 1.0:
            cell /= scale
            cols = int(math.ceil((x1 - x0) / cell)) + 1
            rows = int(math.ceil((y1 - y0) / cell)) + 1
        mask = np.zeros((rows, cols), dtype=np.uint8)
        half = gap / 2.0
        spans = []
        for k in inner:
            b = items[k][1]
            c0 = max(0, int((max(b[0], core[0]) - half - x0) // cell))
            c1 = min(cols - 1, int((min(b[2], core[2]) + half - x0) // cell))
            r0 = max(0, int((max(b[1], core[1]) - half - y0) // cell))
            r1 = min(rows - 1, int((min(b[3], core[3]) + half - y0) // cell))
            mask[r0:r1 + 1, c0:c1 + 1] = 1
            spans.append((k, r0, c0))
        _, labels = cv2.connectedComponents(mask, connectivity=4)
        first: dict[int, int] = {}
        for k, r0, c0 in spans:
            lab = int(labels[r0, c0])
            i = items[k][0]
            if lab in first:
                uf.union(first[lab], i)
            else:
                first[lab] = i
    for a in range(len(outer)):
        i, b = items[outer[a]]
        for c_ in range(a + 1, len(outer)):
            j, c = items[outer[c_]]
            if c[0] - gap <= b[2] and b[0] - gap <= c[2] and c[1] - gap <= b[3] and b[1] - gap <= c[3]:
                uf.union(i, j)
    return uf


def _edge_distance(b: Box, rect: Box) -> float:
    """Distance from a box inside a rectangle to the rectangle's nearest edge."""
    return min(b[0] - rect[0], rect[2] - b[2], b[1] - rect[1], rect[3] - b[3])


def _overlap_or_touch(b: Box, c: Box) -> bool:
    return b[0] <= c[2] and c[0] <= b[2] and b[1] <= c[3] and c[1] <= b[3]


def _edges(rect: Box) -> list[Box]:
    x0, y0, x1, y1 = rect
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x0, y1, x1, y1), (x0, y0, x0, y1)]


def _groups(uf: _UF, idx: list[int]) -> list[list[int]]:
    out: dict[int, list[int]] = {}
    for i in idx:
        out.setdefault(uf.find(i), []).append(i)
    return [sorted(v) for v in out.values()]


# --------------------------------------------------------------------------
# Sheet box
# --------------------------------------------------------------------------

def sheet_box(ents: list[Ent], texts: list[Txt]) -> tuple[Box, Optional[Ent]]:
    """The frame's box (the largest rectangle holding >= 50 % of the entity centres) or the 2-98 % box."""
    centres = [e.centre for e in ents] + [t.point for t in texts]
    if not centres:
        return (0.0, 0.0, 1.0, 1.0), None
    for e in sorted((e for e in ents if e.rect is not None), key=lambda e: -_area(e.rect)):
        inside = sum(1 for c in centres if in_box(c, e.rect))
        if inside >= FRAME_HOLD_SHARE * len(centres) and inside >= 3:
            return e.rect, e
    arr = np.asarray(centres, dtype=float)
    lo = np.percentile(arr, PERCENTILES[0], axis=0)
    hi = np.percentile(arr, PERCENTILES[1], axis=0)
    box = (float(lo[0]), float(lo[1]), float(hi[0]), float(hi[1]))
    if box[2] - box[0] <= 0 or box[3] - box[1] <= 0:
        allb = box_union(e.box for e in ents) if ents else box_union(t.box for t in texts)
        box = allb
    return box, None


def _area(b: Box) -> float:
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def _diag(b: Box) -> float:
    return math.hypot(b[2] - b[0], b[3] - b[1])


# --------------------------------------------------------------------------
# Split
# --------------------------------------------------------------------------

def split_sheet(sheet: Sheet, n_doc_entities: Optional[int] = None, gap_rel: float = GAP_REL) -> SplitResult:
    ents, texts = sheet.ents, sheet.texts
    box, frame_ent = sheet_box(ents, texts)
    gap = gap_rel * max(_diag(box), 1e-9)
    total = n_doc_entities if n_doc_entities is not None else len(ents) + len(texts)
    short = max(min(box_size(box)), 1e-9)
    cand = [k for k, e in enumerate(ents) if e.rect is not None
            and min(box_size(e.rect)) >= FRAME_MIN_REL * short]
    cand_set = set(cand)
    others = [k for k in range(len(ents)) if k not in cand_set]

    # First clustering without the candidates.
    uf = _cluster_boxes([(k, ents[k].box) for k in others], len(ents), gap)
    first = _groups(uf, others)
    first_boxes = [box_union(ents[k].box for k in g) for g in first]

    # Frames: candidates holding >= 2 first-pass clusters apart from their edges (largest first; nested frames
    # allowed), with what touches their edges (an attached title block) < 10 % of what they hold: a sheet frame holds
    # drawings with paper around them, a building outline drawn as one closed polyline holds the walls that run into
    # it. A frame missed this way costs little: only what lies within the gap of its lines joins it.
    frames: list[int] = []
    boundaries: list[int] = []
    # A candidate box that holds texts of its own (a title block drawn as one rectangle) counts as a held drawing.
    text_boxes = [ents[j].rect for j in cand
                  if any(in_box(t.point, ents[j].rect) and not any(in_box(t.point, b) for b in first_boxes)
                         for t in texts)]
    for k in sorted(cand, key=lambda k: -_area(ents[k].rect)):
        rect = ents[k].rect
        held = [(b, len(g)) for b, g in zip(first_boxes, first) if box_inside(b, rect, tol=gap * 0.5)]
        held += [(b, 1) for b in text_boxes if b != rect and box_inside(b, rect, tol=gap * 0.5)
                 and _edge_distance(b, rect) > gap]
        apart = [n for b, n in held if _edge_distance(b, rect) > gap]
        touching = sum(n for b, n in held if _edge_distance(b, rect) <= gap)
        if len(apart) >= 2 and touching < FRAME_TOUCH_SHARE * sum(n for _, n in held):
            nested = any(box_inside(rect, ents[f].rect, tol=gap * 0.5) for f in frames)
            titled = sum(1 for t in texts if in_box(t.point, rect) and T.class_of(t.text) is not None)
            if nested and titled < 2:
                boundaries.append(k)
                continue
            frames.append(k)
    frame_set = set(frames)

    # Second clustering: every non-frame entity; non-frame candidates take part through their edges, and a candidate
    # that holds exactly one cluster joins it.
    items = [(k, ents[k].box) for k in others]
    rest = [k for k in cand if k not in frame_set]
    for k in rest:
        items.extend((k, e) for e in _edges(ents[k].rect))
    uf = _cluster_boxes(items, len(ents), gap)
    members = others + rest
    groups = _groups(uf, members)
    for k in rest:
        rect = ents[k].rect
        inside = [g for g in groups if k not in g and box_inside(box_union(ents[i].box for i in g), rect,
                                                                   tol=gap * 0.5)]
        if len(inside) == 1 or (inside and k in boundaries):
            for g in inside:
                uf.union(k, g[0])
            groups = _groups(uf, members)

    frame_boxes = [(ents[k].id, ents[k].rect) for k in frames]

    def frame_of(b: Box) -> Optional[str]:
        best = None
        for fid, fb in frame_boxes:
            if box_inside(b, fb, tol=gap * 0.5) and (best is None or _area(fb) < _area(best[1])):
                best = (fid, fb)
        return best[0] if best else None

    clusters = []
    for g in groups:
        c = Cluster(ents=[ents[i] for i in g])
        c.frame = frame_of(c.geometry_box)
        if len(g) == 1 and ents[g[0]].rect is not None and g[0] in cand_set:
            c.kind = "box"
        clusters.append(c)

    clusters = _absorb_satellites(clusters)

    # Texts by their point (never bridging).
    left: list[Txt] = []
    for t in texts:
        p = t.point
        holders = [c for c in clusters if in_box(p, c.geometry_box)]
        if holders:
            min(holders, key=lambda c: _area(c.geometry_box)).texts.append(t)
            continue
        tframe = frame_of((p[0], p[1], p[0], p[1]))
        near = [(point_box_distance(p, c.geometry_box), k) for k, c in enumerate(clusters) if c.frame == tframe]
        near = [n for n in near if n[0] <= max(TEXT_REACH * gap, TITLE_REACH * _height(clusters[n[1]]) + t.height)]
        if near:
            clusters[min(near)[1]].texts.append(t)
        else:
            left.append(t)
    if left:
        tuf = _cluster_boxes([(k, t.box) for k, t in enumerate(left)], len(left), gap)
        for g in _groups(tuf, list(range(len(left)))):
            c = Cluster(texts=[left[i] for i in g], kind="text")
            c.frame = frame_of(c.box)
            clusters.append(c)

    # Strays.
    regions, strays = _strays(clusters, frame_boxes, total, gap)
    sheet.box = tuple(float(v) for v in box)
    sheet.gap = gap
    sheet.frames = [{"entity": fid, "box": list(fb)} for fid, fb in frame_boxes]
    return SplitResult(box=sheet.box, gap=gap, frames=sheet.frames, clusters=reading_order(regions), strays=strays)


def _height(c: Cluster) -> float:
    b = c.geometry_box
    return b[3] - b[1]


def _absorb_satellites(clusters: list[Cluster]) -> list[Cluster]:
    """Small clusters next to a drawing (its dimension chains, a north arrow, a door drawn apart) join it: a cluster
    whose box is <= 5 % of the drawing's (or thin), within half the drawing's shorter side, with 10 x fewer entities.
    Title boxes and other lone rectangles never join."""
    out = list(clusters)
    for c in sorted(clusters, key=lambda c: c.size):
        if c.kind != "drawing" or c not in out:
            continue
        cb = c.geometry_box
        holders = [host for host in out if host is not c and host.kind == "drawing" and host.frame == c.frame
                   and box_inside(cb, host.geometry_box) and _area(host.geometry_box) > _area(cb)]
        if holders:
            # Furniture in the middle of a room, farther than the gap from every wall: inside the drawing's box.
            min(holders, key=lambda h_: _area(h_.geometry_box)).ents.extend(c.ents)
            out.remove(c)
    for c in sorted(list(out), key=lambda c: c.size):
        if c.kind != "drawing" or c not in out:
            continue
        cb = c.geometry_box
        w, h = cb[2] - cb[0], cb[3] - cb[1]
        best = None
        for host in out:
            if host is c or host.kind != "drawing" or host.frame != c.frame or host.size < SATELLITE_COUNT * c.size:
                continue
            hb = host.geometry_box
            hw, hh = hb[2] - hb[0], hb[3] - hb[1]
            small = w * h <= SATELLITE_AREA * hw * hh or min(w, h) <= SATELLITE_THIN * max(w, h)
            d = box_distance(cb, hb)
            if small and d <= SATELLITE_REACH * min(hw, hh) and (best is None or d < best[0]):
                best = (d, host)
        if best is not None:
            best[1].ents.extend(c.ents)
            out.remove(c)
    return out


def _strays(clusters: list[Cluster], frame_boxes: list, total: int, gap: float):
    small = [c for c in clusters if c.size < STRAY_SHARE * max(total, 1)]
    if frame_boxes:
        far = [c for c in small if c.frame is None and not any(box_distance(c.box, fb) == 0.0 and
                                                                  _overlap(c.box, fb) for _, fb in frame_boxes)]
    else:
        sizes = [max(box_size(c.box)) for c in clusters if c.size >= STRAY_SHARE * max(total, 1)]
        median = statistics.median(sizes) if sizes else 0.0
        far = []
        for c in small:
            others = [box_distance(c.box, o.box) for o in clusters if o is not c]
            if others and min(others) > STRAY_FAR * median and median > 0:
                far.append(c)
    far_ids = {id(c) for c in far}
    regions = [c for c in clusters if id(c) not in far_ids]
    strays = []
    for c in far:
        d = min((box_distance(c.box, r.box) for r in regions), default=0.0)
        strays.append((c, d))
    return regions, strays


def _overlap(a: Box, b: Box) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def reading_order(clusters: list[Cluster]) -> list[Cluster]:
    """Top to bottom by the top of the region box (y up), then left to right (sheets.schema ``$defs/region.id``)."""
    return sorted(clusters, key=lambda c: (-round(c.geometry_box[3], 6), round(c.geometry_box[0], 6)))
