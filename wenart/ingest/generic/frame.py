"""Sheet frame blocks: the drawing frame and title block inserted as one block around the plan (real03).

What: ``frame_blocks(page) -> list[dict]`` finds the top-level block inserts of a page that are a sheet frame with
its title block (a legend block: ``MYD - LEJAND`` / ``*U62`` on real03), so the core never reads their lines as
walls, openings or furniture.

Why: a CAD sheet often inserts the frame and title block as one block whose box is the whole sheet. The sheets
stage clusters whole inserts, so such a block is not split off as a title-block region (it holds the plan's box);
its title rows are thin closed rectangles (0.5 m x 4.9 m at the drawing unit) that pass the outline-wall rule, and
real03's only "walls" were title-block rows.

How (all in page units; every rule is geometry, no layer or block name):
- strokes are grouped by their top-level entity (``INSERT:7C135/3`` -> ``INSERT:7C135``); only groups drawn inside a
  block insert (strokes with a block chain) are candidates;
- the group holds a closed axis-aligned rectangle that spans >= ``FRAME_COVER`` (90 %) of the page's extent both
  ways (the sheet frame);
- the frame holds another entity's drawing (a stroke of another group whose box centre lies inside it);
- every other stroke of the group lies in the frame's edge band: within ``FRAME_BAND`` (25 %) of the frame's shorter
  side from one of its edges (title block rows, a logo, notes along the border), or is a frame rectangle itself.

A block whose strokes reach into the middle of the frame is a drawing, not a frame block: it stays.
"""
from __future__ import annotations

import re
from typing import Optional

from wenart.ingest.generic.model import GenericPage, Stroke

FRAME_COVER = 0.90
FRAME_BAND = 0.25
_INDEX_RE = re.compile(r"\[\d+\]$")


def top_entity(stroke_id: str) -> str:
    """``INSERT:4B[2]/3`` -> ``INSERT:4B``, ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``
    (the same grouping as ``dxf_generic.stroke_entity``)."""
    head = _INDEX_RE.sub("", stroke_id.split("/")[0].split("#")[0])
    return ":".join(head.split(":")[:2])


def _rect(st: Stroke) -> Optional[tuple[float, float, float, float]]:
    """Box of a closed stroke whose corners form an axis-aligned rectangle."""
    pts = list(st.pts)
    if len(pts) == 5 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if not st.closed and not (len(st.pts) == 5 and st.pts[0] == st.pts[-1]):
        return None
    if len(pts) != 4:
        return None
    xs = sorted({round(p[0], 6) for p in pts})
    ys = sorted({round(p[1], 6) for p in pts})
    if len(xs) != 2 or len(ys) != 2:
        return None
    return (xs[0], ys[0], xs[1], ys[1])


def _in_band(b, frame, band: float) -> bool:
    x0, y0, x1, y1 = frame
    inside = b[0] >= x0 - band * 0.01 and b[1] >= y0 - band * 0.01 and b[2] <= x1 + band * 0.01 and \
        b[3] <= y1 + band * 0.01
    if not inside:
        return False
    return b[2] <= x0 + band or b[0] >= x1 - band or b[3] <= y0 + band or b[1] >= y1 - band


def frame_blocks(page: GenericPage) -> list[dict]:
    """The sheet frame blocks of a page (see the module docstring): ``[{"entity", "block", "layer", "stroke_ids",
    "frame_box", "strokes"}]`` in page units."""
    strokes = [st for st in page.strokes if st.pts]
    if not strokes:
        return []
    boxes = [st.bbox() for st in strokes]
    px0, py0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    px1, py1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    pw, ph = px1 - px0, py1 - py0
    if pw <= 0 or ph <= 0:
        return []
    groups: dict[str, list[int]] = {}
    for k, st in enumerate(strokes):
        if st.block:
            groups.setdefault(top_entity(st.id), []).append(k)
    out = []
    for key, idx in groups.items():
        frames = []
        for k in idx:
            r = _rect(strokes[k])
            if r is not None and r[2] - r[0] >= FRAME_COVER * pw and r[3] - r[1] >= FRAME_COVER * ph:
                frames.append((k, r))
        if not frames:
            continue
        frame = max((r for _, r in frames), key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
        own = set(idx)
        holds = any(frame[0] <= (boxes[k][0] + boxes[k][2]) / 2.0 <= frame[2]
                    and frame[1] <= (boxes[k][1] + boxes[k][3]) / 2.0 <= frame[3]
                    for k in range(len(strokes)) if k not in own)
        if not holds:
            continue
        band = FRAME_BAND * min(frame[2] - frame[0], frame[3] - frame[1])
        frame_ids = {k for k, _ in frames}
        if not all(k in frame_ids or _in_band(boxes[k], frame, band) for k in idx):
            continue
        first = strokes[idx[0]]
        out.append({"entity": key, "block": (first.block or "").split("/")[0] or None, "layer": first.layer,
                    "stroke_ids": [strokes[k].id for k in idx], "frame_box": [round(v, 3) for v in frame],
                    "strokes": len(idx)})
    return out


# --------------------------------------------------------------------------
# The sheet frame read as walls (6 Nov 2026, Milestone 14 reader target 2)
# --------------------------------------------------------------------------
# real19 L1-L3: four walls on the drawing's region box covering 99 % of its perimeter (and a 441 m2 room named from the
# sheet text); the frame was drawn as plain lines, not as a block. Moved here from RC14 (``wenart.reading_check.sense``,
# rule 3, which imports them), so the reader and the checker find the frame by one rule: walls whose outer face lies
# on the region box (within FRAME_TOL_M) covering FRAME_SHARE_MIN of its perimeter, with at most FRAME_OPENINGS_MAX
# openings and FRAME_JOINS_MAX other walls ending on them (a region box cut tight around a building puts its real outer
# walls on the box too, but those carry windows and doors and the inner walls end on them).
FRAME_TOL_M = 0.10            # a wall's outer face this close to the region box's edge lies on it
FRAME_SHARE_MIN = 0.60        # frame walls covering this share of the box perimeter: the sheet frame read as walls
FRAME_OPENINGS_MAX = 0        # openings on the edge walls of a frame
FRAME_JOINS_MAX = 2           # other walls with an end on the edge walls of a frame
JOIN_REACH_M = 0.30           # a wall end this close to an edge wall's centre line ends on it
FRAME_MIN_WALL_M = 0.3        # shorter walls are not looked at
EPS = 1e-6


def frame_walls(walls: list, box) -> tuple[list, float]:
    """``(wall ids, share)`` (pure): the walls (dicts ``{id, start, end, thickness}``) whose outer face lies on an edge
    of the box (a shapely polygon) within ``FRAME_TOL_M`` (both ends; the face is the centre line moved out by half the
    thickness) and the share of the box perimeter their projections cover."""
    from shapely.geometry import LineString, Point

    pts = list(box.exterior.coords)[:-1]
    ids, covered = [], 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        edge = LineString([a, b])
        if edge.length <= 0:
            continue
        spans = []
        for w in walls:
            reach = FRAME_TOL_M + float(w.get("thickness") or 0.0) / 2.0
            p, q = Point(w["start"][:2]), Point(w["end"][:2])
            if edge.distance(p) > reach + EPS or edge.distance(q) > reach + EPS or p.distance(q) < FRAME_MIN_WALL_M:
                continue
            # the line through the edge, not only the segment: a wall a little longer than the box still lies on it
            s, t = sorted((edge.project(p), edge.project(q)))
            spans.append((max(0.0, s), min(edge.length, t)))
            if w.get("id") not in ids:
                ids.append(w.get("id"))
        spans.sort()
        run_end = -1.0
        for s, t in spans:
            if t <= run_end:
                continue
            covered += t - max(s, run_end)
            run_end = t
    return ids, (covered / box.length if box.length > 0 else 0.0)


def frame_joins(walls: list, ids) -> int:
    """How many other walls (dicts) have an end within ``JOIN_REACH_M`` of the walls ``ids`` (pure)."""
    from shapely.geometry import LineString, Point

    ids = set(ids)
    lines = [LineString([w["start"][:2], w["end"][:2]]) for w in walls if w.get("id") in ids]
    joins = 0
    for w in walls:
        if w.get("id") in ids:
            continue
        if any(ln.distance(Point(e[:2])) <= JOIN_REACH_M + EPS for e in (w["start"], w["end"]) for ln in lines):
            joins += 1
    return joins


def sheet_frame_walls(walls: list, openings: list, box) -> Optional[dict]:
    """The reader's side (page or building metres alike): ``{"ids", "share", "openings", "joins", "frame"}`` for the
    walls (``WallItem``-like: ``start``, ``end``, ``thickness``) on the region box (a shapely polygon) when they cover
    ``FRAME_SHARE_MIN`` of its perimeter, ``frame`` True when they carry no more openings and joins than a frame; None
    when they cover less. An opening (``center``, not ``virtual``) counts on an edge wall when its centre lies within
    half the wall's thickness plus 5 cm of the wall's centre line."""
    from shapely.geometry import LineString, Point

    if box is None or box.area <= 0 or not walls:
        return None
    dicts = [{"id": k, "start": tuple(w.start), "end": tuple(w.end), "thickness": float(w.thickness)}
             for k, w in enumerate(walls)]
    ids, share = frame_walls(dicts, box)
    if share < FRAME_SHARE_MIN:
        return None
    edge = [(LineString([dicts[k]["start"], dicts[k]["end"]]), dicts[k]["thickness"]) for k in ids]
    n_open = sum(1 for o in openings if not getattr(o, "virtual", False) and getattr(o, "center", None) is not None
                 and any(ln.distance(Point(o.center)) <= t / 2.0 + 0.05 for ln, t in edge))
    joins = frame_joins(dicts, ids)
    return {"ids": ids, "share": round(share, 3), "openings": n_open, "joins": joins,
            "frame": n_open <= FRAME_OPENINGS_MAX and joins <= FRAME_JOINS_MAX}
