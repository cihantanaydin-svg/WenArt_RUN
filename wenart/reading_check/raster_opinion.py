"""The raster second opinion RC13: the same plan read again by the project's own raster reader (5 Nov 2026, Milestone 14
track R4; user, 4 Nov 2026: "some AI or something else to give the feedbacks by itself instead of me").

What: ``opinion(out_dir)`` takes a pipeline output (``building.json``, ``sheets.json``, the converted DXF), and for each
level read from a CAD region (``reading_check.level_pages``; a typical floor's copies share its plan):

1. **Render**: the level's region of the DXF is drawn to a grey PNG by ezdxf's matplotlib backend (black lines on
   white, texts drawn, no colours) at ``PX_PER_M`` pixels per building metre, the long side capped at ``MAX_SIDE_PX``.
   The grid and the dimensions are left out as on the sheets' first panel (``RENDER_CLEAN``,
   ``sheets.is_grid_or_dimension``: entities and layers that say so; dimension chains on layers with other names
   stay). The pixel -> building-metre transform is exact (the page transform of the level, ``transform_to_building``),
   so no registration is guessed: ``render_level`` returns it as ``pixel_to_building`` (OpenCV pixel centres;
   matplotlib snaps a line to whole pixels, so a drawn line lies within one pixel, 1 cm, of it).
2. **Read**: the PNG is a one-page raster project in a temporary folder, read by ``pipeline.run_project(no_ai=True)``
   (the raster adapter ``ingest.raster`` and the generic core, as for a scan). The raster API takes no scale argument,
   so the known pixel size goes in the way the reader accepts a verified one (``raster.load_image``, ``generic.scale
   ._provisional_scale``): the PNG carries its pixel size as metadata (pHYs, ``dpi`` = 0.0254 x px_per_m x
   ``NOTE_RATIO``) and a printed scale note ``SCALE 1:<NOTE_RATIO>`` in a white band above the drawing, which the OCR
   reads; the drawing's own scale notes are left out of the render (several different notes would cancel each other).
   The reader may still prefer the dimension texts when they disagree by more than 1 % (its rule for a raster page);
   the scale it used is recorded (``scale_used``), and the mapping back never depends on it: raster building metres
   -> its page pixels (its ``transform_to_building``) -> the PNG's pixels (its ``to_original``) -> the level's building
   metres (``pixel_to_building``).
3. **Compare** per level with the matcher of ``score.py`` (walls by centre-line overlap, openings by centre and type
   class, rooms by label and centroid or IoU; its constants untouched). What the matcher leaves is a finding only
   when the other reading does not cover it either (a wall the other side reads in two pieces, a room it splits in
   two, is no disagreement): rooms by the share of the area inside the other side's rooms (``room_cover_share``);
   walls by the pieces of their centre lines that run along none of the other side's walls (``uncovered_pieces``,
   for every wall: one the matcher pairs with a shorter piece still has its uncovered rest). Kinds (``KINDS``): a wall only the raster or only the
   vector reading has (the uncovered pieces >= ``WALL_PIECE_MIN_M``), a room only one closes, an opening only one has,
   an opening both have with another type. Virtual separators are no drawn element and are not compared.
   Findings of one kind on one level within ``GROUP_M`` of each other that describe one place are one finding (its
   members listed; ``near``: wall pieces on one line, openings by centre, rooms that overlap or share a centroid;
   walls meeting at a corner stay two findings, else a plan's walls chain into one). A level whose raster walls
   cover less than ``WEAK_WALL_SHARE`` of the vector wall length is a weak raster reading: its vector-only
   differences are counted in one ``raster_weak`` info finding instead of one finding each (the raster reader could
   not read the plan; that is not a reading error of the vector reader); its raster-only findings stay listed.
   Each finding is shaped like ``reading_check._finding`` / ``crossdoc._finding``: ``check`` RC13, ``severity`` info |
   minor | major, ``advisory: true``, ``place`` ``{x, y}`` (building metres), ``element_ids`` (raster ids prefixed
   ``raster:``), ``sources`` ``["vector", "raster"]``, plus ``kind``, ``what`` (what each side read) and ``trust``.
4. **Trust** (``calibrate``): on the projects with a truth (``results/reading_truth/``) the raster reading is scored
   against the truth (``score.match``) and every finding is judged: right when the truth agrees with the raster side
   (a raster-only wall the truth has, a vector-only wall the truth has not ...). The precision per kind is stored in
   ``models/raster_trust.json`` with the commit, the projects and the counts; a kind below ``TRUST_MIN`` (or never
   calibrated) writes its findings with severity ``info`` and says so in the message (``apply_trust``). The opinion
   gates nothing (Milestone 14 §3 R4: "it gates nothing until it earns it").

Writes ``reading_check/raster_opinion.json`` and ``.md`` and, per level, ``reading_check/raster_<level>.jpg`` (the
render in grey, the vector walls red, the raster walls blue, the findings numbered). Command line:
``python -m wenart.reading_check raster check --out DIR``, ``raster calibrate [--projects ...] --work DIR [--write]``,
``raster projects --projects real13,real18 --work DIR``.

Why: a disagreement between two independent readers of one drawing is a finding nobody had to look for. The known risk
(docs/milestone14.md §3 R4): on a plan drawn as face lines the raster wall mask may miss what the vector reader sees,
so the opinion is calibrated against the accepted readings before it is trusted, and the numbers are reported as they
come out (no tuning of the raster reader to look good; the reader code is not touched here).

How: ezdxf (MIT) matplotlib backend for the render, Pillow for the note and the metadata, the existing pipeline for the
raster reading (Tesseract, OpenCV), shapely for coverage; pure functions for the mapping, the comparison, the grouping,
the judging and the trust; no AI, no pod.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import json
import math
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[2]
TRUST_PATH = Path(__file__).resolve().parent / "models" / "raster_trust.json"
CHECK = "RC13"
NAME = "raster second opinion"
SOURCES = ["vector", "raster"]
# 1. render
PX_PER_M = 100.0               # pixels per building metre (the raster reader's constants are tuned on 150 dpi 1:50 scans,
                               # about 118 px/m)
MAX_SIDE_PX = 8000             # ... the long side capped (the pixel size then drops; it is recorded)
FIG_DPI = 100                  # matplotlib's dots per inch for the figure (line widths are in points)
LINEWEIGHT_SCALING = 1.5       # a 0.25 mm pen is drawn about 1.5 px wide, as on a 150 dpi scan
NOTE_RATIO = 100               # the printed scale note: SCALE 1:100 ...
NOTE_BAND_PX = 110             # ... in a white band this tall above the drawing
NOTE_TEXT_PX = 40              # ... its letters this tall
NOTE_FONT = "DejaVuSans.ttf"
TEXT_TYPES = ("TEXT", "MTEXT", "ATTRIB")
RENDER_CLEAN = True            # the grid and the dimensions left out (``sheets.is_grid_or_dimension``, the sheets'
                               # panel 1): the vector reader leaves them out before it reads walls too
ONE_PLAN_MARGIN = 0.15         # a one-plan document: the drawing's extents, or the model's box with this margin ...
ONE_PLAN_MARGIN_M = 2.0        # ... and at least this many metres, when the extents are far larger (stray entities)
ONE_PLAN_EXTENT_FACTOR = 3.0
# 3. compare
WALL_PIECE_MIN_M = 0.5         # an uncovered wall piece shorter than this is a junction difference, no finding
WALL_ANGLE_DEG = 10.0          # two walls cover each other only when this parallel ...
COVER_MIN = 0.5                # an element covered this much by the other side is no disagreement
GROUP_M = 0.5                  # findings of one kind within this distance are one finding
WALL_MAJOR_M = 3.0             # severity by size: wall length (as RC4's MISSING_MAJOR_M) ...
WALL_MINOR_M = 1.0
ROOM_MAJOR_M2 = 6.0            # ... room area
ROOM_MINOR_M2 = 2.0
OPENING_TYPES = ("doors", "windows", "openings")
KINDS = ("wall_raster_only", "wall_vector_only", "room_raster_only", "room_vector_only", "opening_raster_only",
         "opening_vector_only", "opening_type_differs")
VECTOR_ONLY_KINDS = ("wall_vector_only", "room_vector_only", "opening_vector_only")
WEAK_WALL_SHARE = 0.3          # a level whose raster walls cover less of the vector wall length than this is a weak
                               # raster reading: its vector-only differences are folded into one info finding
                               # (``raster_weak``); what the raster sees and the vector does not stays listed
# 4. trust
TRUST_MIN = 0.5                # a kind below this precision writes its findings as info
SEVERITY_ORDER = {"major": 0, "minor": 1, "info": 2}
OVERLAY_LONG_PX = 2000         # the evidence image per level
TRUST_NOTE = ("Precision of the raster second opinion (RC13) per finding kind against results/reading_truth/ "
              "(python -m wenart.reading_check raster calibrate --write). A finding is right when the truth agrees "
              "with the raster side. A kind below the threshold (or with no calibrated finding) writes its findings "
              "with severity info. The truth of a real project is its accepted reading, so there every finding is a "
              "disagreement with what the user accepted.")


# ------------------------------------------------------------------------------------------------------------ geometry
def _apply(tf, p) -> tuple:
    return (tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5])


def _invert(tf) -> list:
    """The inverse of an affine ``[a, b, c, d, e, f]`` (x' = a x + b y + c, y' = d x + e y + f)."""
    a, b, c, d, e, f = (float(v) for v in tf)
    det = a * e - b * d
    if abs(det) < 1e-15:
        raise ValueError("singular transform")
    return [e / det, -b / det, (b * f - c * e) / det, -d / det, a / det, (c * d - a * f) / det]


def _compose(outer, inner) -> list:
    """``outer`` after ``inner`` (both affine 6-lists)."""
    a, b, c, d, e, f = outer
    g, h, i, j, k, m = inner
    return [a * g + b * j, a * h + b * k, a * i + b * m + c, d * g + e * j, d * h + e * k, d * i + e * m + f]


def _apply_h(h, p) -> tuple:
    """A 3 x 3 homography applied to one point."""
    w = h[2][0] * p[0] + h[2][1] * p[1] + h[2][2]
    return ((h[0][0] * p[0] + h[0][1] * p[1] + h[0][2]) / w, (h[1][0] * p[0] + h[1][1] * p[1] + h[1][2]) / w)


def pixel_transform(box: list, units_per_px: float, band_px: int, tf: list) -> list:
    """The affine from PNG pixel centres (OpenCV: column u, row v, y down) to the level's building metres (pure): the
    drawing's top-left corner ``(box[0], box[3])`` is the top-left corner of the pixel below the note band, one pixel
    is ``units_per_px`` drawing units, ``tf`` the level's page transform (drawing units -> building metres)."""
    s = float(units_per_px)
    to_drawing = [s, 0.0, float(box[0]) + 0.5 * s, 0.0, -s, float(box[3]) + (band_px - 0.5) * s]
    return _compose([float(v) for v in tf], to_drawing)


def _seg_len(a, b) -> float:
    return math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def _shoelace(poly) -> float:
    pts = [(float(p[0]), float(p[1])) for p in poly or []]
    if len(pts) < 3:
        return 0.0
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2.0


def _angle_deg(a0, a1, b0, b1) -> float:
    """The angle between two undirected segments, 0-90 degrees."""
    ua = math.atan2(a1[1] - a0[1], a1[0] - a0[0])
    ub = math.atan2(b1[1] - b0[1], b1[0] - b0[0])
    d = abs(math.degrees(ua - ub)) % 180.0
    return min(d, 180.0 - d)


def _wall_tol(a: dict, b: dict) -> float:
    """Two wall centre lines read from one wall body lie within the score's lateral tolerance, or within half the
    thicker wall (a thick wall read at its faces by one reader and at its core by the other)."""
    ta, tb = float(a.get("thickness") or 0.0), float(b.get("thickness") or 0.0)
    return max(SC.WALL_LATERAL_M, 0.5 * max(ta, tb))


def covered_intervals(wall: dict, others: list) -> list:
    """The parameter intervals ``[t0, t1]`` (metres along ``wall`` from its start) where its centre line runs along
    one of ``others`` (pure): parallel within ``WALL_ANGLE_DEG``, the other's line within ``_wall_tol`` of both ends
    of the overlap, merged."""
    a, b = wall["start"], wall["end"]
    length = _seg_len(a, b)
    if length < 1e-9:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    spans = []
    for o in others:
        p, q = o["start"], o["end"]
        lo = _seg_len(p, q)
        if lo < 1e-9 or _angle_deg(a, b, p, q) > WALL_ANGLE_DEG:
            continue
        tp = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
        tq = (q[0] - a[0]) * ux + (q[1] - a[1]) * uy
        t0, t1 = max(0.0, min(tp, tq)), min(length, max(tp, tq))
        if t1 - t0 <= 1e-6:
            continue
        # lateral distance of the overlap's two ends (on the wall) from the other's line
        vx, vy = (q[0] - p[0]) / lo, (q[1] - p[1]) / lo
        tol = _wall_tol(wall, o)
        ok = True
        for t in (t0, t1):
            x, y = a[0] + ux * t, a[1] + uy * t
            if abs((x - p[0]) * vy - (y - p[1]) * vx) > tol:
                ok = False
                break
        if ok:
            spans.append((t0, t1))
    spans.sort()
    merged: list = []
    for s0, s1 in spans:
        if merged and s0 <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], s1)
        else:
            merged.append([s0, s1])
    return merged


def uncovered_pieces(wall: dict, others: list, min_len: float = WALL_PIECE_MIN_M) -> list:
    """The pieces ``[[x0, y0], [x1, y1]]`` of ``wall``'s centre line that no wall of ``others`` covers
    (``covered_intervals``), each at least ``min_len`` long (pure)."""
    a, b = wall["start"], wall["end"]
    length = _seg_len(a, b)
    if length < 1e-9:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    out, t = [], 0.0
    for s0, s1 in covered_intervals(wall, others) + [[length, length]]:
        if s0 - t >= min_len:
            out.append([[round(a[0] + ux * t, 3), round(a[1] + uy * t, 3)],
                        [round(a[0] + ux * s0, 3), round(a[1] + uy * s0, 3)]])
        t = max(t, s1)
    return out


def wall_length_share(walls: list, others: list) -> Optional[float]:
    """The share of the total centre-line length of ``walls`` that ``others`` cover (pure); None without walls."""
    total = sum(_seg_len(w["start"], w["end"]) for w in walls)
    if total < 1e-9:
        return None
    return sum(_seg_len(w["start"], w["end"]) * wall_cover_share(w, others) for w in walls) / total


def wall_cover_share(wall: dict, others: list) -> float:
    """The share of ``wall``'s centre line covered by ``others`` (0-1, pure)."""
    length = _seg_len(wall["start"], wall["end"])
    if length < 1e-9:
        return 1.0
    return min(1.0, sum(s1 - s0 for s0, s1 in covered_intervals(wall, others)) / length)


def _polygon(poly):
    from shapely.geometry import Polygon

    try:
        p = Polygon([(float(x), float(y)) for x, y in poly]).buffer(0)
        return p if not p.is_empty else None
    except Exception:  # noqa: BLE001 - an invalid outline covers nothing
        return None


def room_cover_share(room: dict, others: list) -> float:
    """The share of ``room``'s area inside the union of ``others``' polygons (0-1, pure)."""
    from shapely.ops import unary_union

    p = _polygon(room.get("polygon") or [])
    if p is None or p.area < 1e-9:
        return 1.0
    polys = [q for q in (_polygon(o.get("polygon") or []) for o in others) if q is not None]
    if not polys:
        return 0.0
    return min(1.0, p.intersection(unary_union(polys)).area / p.area)


# ------------------------------------------------------------------------------------------------------------ findings
def _finding(severity: str, level: Optional[str], message: str, kind: str, place=None, element_ids=None,
             **extra) -> dict:
    """An RC13 finding, shaped like ``reading_check._finding`` and ``crossdoc._finding`` (advisory, both sources)."""
    out = {"check": CHECK, "name": NAME, "severity": severity, "level_id": level, "message": message,
           "advisory": True, "sources": list(SOURCES), "kind": kind, "place": None, "element_ids": []}
    if place is not None:
        out["place"] = {"x": round(float(place[0]), 3), "y": round(float(place[1]), 3)}
    if element_ids:
        out["element_ids"] = list(element_ids)
    out.update(extra)
    return out


def _rid(e: dict) -> str:
    return f"raster:{e.get('id')}"


def _kind_class(kind: str) -> str:
    return {"doors": "door", "windows": "window"}.get(kind, "opening")


def raw_differences(vec: dict, ras: dict) -> list:
    """The elements one reading of a level has and the other has not (pure): ``vec`` and ``ras`` are truth-shaped
    level dicts (``truth.extract``'s ``per_level`` entries) in the same frame. Returns raw items ``{kind, side,
    geom, size, ids, what}`` (``geom``: ``("seg", a, b)``, ``("poly", pts)`` or ``("pt", p)``), before grouping."""
    out = []
    # walls: the pieces of every wall the other side does not cover; a wall the matcher pairs with a shorter piece
    # of the other side still has its uncovered rest (the matcher's pairs are the agreement numbers, ``SC.match``)
    vw, rw = vec.get("walls") or [], ras.get("walls") or []
    for w in rw:
        for a, b in uncovered_pieces(w, vw):
            out.append({"kind": "wall_raster_only", "geom": ("seg", a, b), "size": _seg_len(a, b), "ids": [_rid(w)],
                        "what": {"raster": f"wall {_rid(w)} ({float(w.get('thickness') or 0):.2f} m thick)",
                                 "vector": "no wall"}})
    for w in vw:
        for a, b in uncovered_pieces(w, rw):
            out.append({"kind": "wall_vector_only", "geom": ("seg", a, b), "size": _seg_len(a, b),
                        "ids": [w.get("id")],
                        "what": {"vector": f"wall {w.get('id')} ({float(w.get('thickness') or 0):.2f} m thick)",
                                 "raster": "no wall"}})
    vr, rr = vec.get("rooms") or [], ras.get("rooms") or []
    m = SC.match_rooms(vr, rr)
    mv, mr = {i for i, _ in m}, {j for _, j in m}
    for j, r in enumerate(rr):
        if j in mr or len(r.get("polygon") or []) < 3:
            continue
        share = room_cover_share(r, vr)
        if share < COVER_MIN:
            area = _shoelace(r["polygon"])
            out.append({"kind": "room_raster_only", "geom": ("poly", r["polygon"]), "size": area, "ids": [_rid(r)],
                        "cover": round(share, 3),
                        "what": {"raster": f"room {_rid(r)} '{r.get('label') or '?'}' {area:.1f} m2 (OCR label)",
                                 "vector": f"no room ({share * 100:.0f} % inside its rooms)"}})
    for i, r in enumerate(vr):
        if i in mv or len(r.get("polygon") or []) < 3:
            continue
        share = room_cover_share(r, rr)
        if share < COVER_MIN:
            area = _shoelace(r["polygon"])
            out.append({"kind": "room_vector_only", "geom": ("poly", r["polygon"]), "size": area,
                        "ids": [r.get("id")], "cover": round(share, 3),
                        "what": {"vector": f"room {r.get('id')} '{r.get('label') or '?'}' {area:.1f} m2",
                                 "raster": f"no closed room ({share * 100:.0f} % inside its rooms)"}})
    left_v, left_r = [], []
    for kind in OPENING_TYPES:
        vo = [o for o in vec.get(kind) or [] if not o.get("virtual") and o.get("center")]
        ro = [o for o in ras.get(kind) or [] if not o.get("virtual") and o.get("center")]
        m = SC.match_points(vo, ro, SC.OPENING_CENTER_M)
        mv, mr = {i for i, _ in m}, {j for _, j in m}
        left_v += [(kind, o) for i, o in enumerate(vo) if i not in mv]
        left_r += [(kind, o) for j, o in enumerate(ro) if j not in mr]
    cross = SC.match_points([o for _, o in left_v], [o for _, o in left_r], SC.OPENING_CENTER_M)
    cv, cr = {i for i, _ in cross}, {j for _, j in cross}
    for i, j in cross:
        (kv, ov), (kr, orr) = left_v[i], left_r[j]
        out.append({"kind": "opening_type_differs", "geom": ("pt", ov["center"]), "size": 1.0,
                    "ids": [ov.get("id"), _rid(orr)], "raster_class": _kind_class(kr),
                    "what": {"vector": f"{_kind_class(kv)} {ov.get('id')} ({float(ov.get('width') or 0):.2f} m)",
                             "raster": f"{_kind_class(kr)} {_rid(orr)} ({float(orr.get('width') or 0):.2f} m)"}})
    for j, (kr, o) in enumerate(left_r):
        if j in cr:
            continue
        out.append({"kind": "opening_raster_only", "geom": ("pt", o["center"]), "size": 1.0, "ids": [_rid(o)],
                    "raster_class": _kind_class(kr),
                    "what": {"raster": f"{_kind_class(kr)} {_rid(o)} ({float(o.get('width') or 0):.2f} m)",
                             "vector": "no opening"}})
    for i, (kv, o) in enumerate(left_v):
        if i in cv:
            continue
        out.append({"kind": "opening_vector_only", "geom": ("pt", o["center"]), "size": 1.0, "ids": [o.get("id")],
                    "vector_class": _kind_class(kv),
                    "what": {"vector": f"{_kind_class(kv)} {o.get('id')} ({float(o.get('width') or 0):.2f} m)",
                             "raster": "no opening"}})
    return out


def _shape(geom):
    from shapely.geometry import LineString, Point

    if geom[0] == "seg":
        return LineString([tuple(geom[1]), tuple(geom[2])])
    if geom[0] == "pt":
        return Point(tuple(geom[1]))
    return _polygon(geom[1]) or Point(tuple(geom[1][0]))


def near(a: dict, b: dict, dist: float = GROUP_M) -> bool:
    """Whether two raw differences of one kind describe one place (pure): wall pieces on one line (parallel within
    ``WALL_ANGLE_DEG``, the line within ``dist`` across and the gap within ``dist`` along: a wall read in fragments),
    openings with their centres within ``dist``, rooms that overlap or whose centroids lie within ``dist``. Walls
    meeting at a corner or a T, and rooms side by side across a wall, stay apart: grouping by plain distance chains a
    plan's walls into one finding at its middle (synthetic-06: nine interior walls, 23.8 m, one place)."""
    if a["kind"] != b["kind"]:
        return False
    ga, gb = a["geom"], b["geom"]
    if ga[0] == "seg":
        (p, q), (r, s) = ga[1:], gb[1:]
        if _angle_deg(p, q, r, s) > WALL_ANGLE_DEG:
            return False
        ln = _seg_len(p, q)
        if ln < 1e-9:
            return _shape(ga).distance(_shape(gb)) <= dist
        ux, uy = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
        lat = max(abs((x - p[0]) * uy - (y - p[1]) * ux) for x, y in (r, s))
        t = sorted(((r[0] - p[0]) * ux + (r[1] - p[1]) * uy, (s[0] - p[0]) * ux + (s[1] - p[1]) * uy))
        gap = max(0.0, t[0] - ln, -t[1])
        return lat <= dist and gap <= dist
    if ga[0] == "pt":
        return _seg_len(ga[1], gb[1]) <= dist
    pa, pb = _shape(ga), _shape(gb)
    try:
        if pa.intersection(pb).area > 0.05 * min(pa.area, pb.area):
            return True
    except Exception:  # noqa: BLE001 - invalid outlines: by centroid only
        pass
    return pa.centroid.distance(pb.centroid) <= dist


def group(items: list, dist: float = GROUP_M) -> list:
    """Raw differences joined into groups of one place (pure; union-find over ``near``); a list of lists of items,
    every item in exactly one group, in the items' order."""
    parent = list(range(len(items)))

    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if near(items[i], items[j], dist):
                parent[root(j)] = root(i)
    groups: dict = {}
    for k in range(len(items)):
        groups.setdefault(root(k), []).append(items[k])
    return list(groups.values())


def _centre(members: list) -> tuple:
    """The place of a group: a point on its largest member (a piece's middle, a room's representative point)."""
    big = max(members, key=lambda m: float(m["size"]))
    g = big["geom"]
    if g[0] == "seg":
        return ((g[1][0] + g[2][0]) / 2.0, (g[1][1] + g[2][1]) / 2.0)
    if g[0] == "pt":
        return (float(g[1][0]), float(g[1][1]))
    c = _shape(g).representative_point()
    return (c.x, c.y)


def severity_by_size(kind: str, size: float) -> str:
    """The severity a finding would have by its size alone (pure): wall metres, room square metres; openings minor
    (a type difference info)."""
    if kind.startswith("wall"):
        return "major" if size >= WALL_MAJOR_M else "minor" if size >= WALL_MINOR_M else "info"
    if kind.startswith("room"):
        return "major" if size >= ROOM_MAJOR_M2 else "minor" if size >= ROOM_MINOR_M2 else "info"
    return "info" if kind == "opening_type_differs" else "minor"


def _message(level: str, kind: str, members: list, size: float, at: tuple) -> str:
    where = f"at ({at[0]:.2f}, {at[1]:.2f})"
    n = len(members)
    if kind == "wall_raster_only":
        ids = sorted({i for m in members for i in m["ids"]})
        return (f"{level}: the raster reading sees {size:.2f} m of wall ({n} piece{'s' if n > 1 else ''}) {where} that "
                f"the vector reading does not have ({', '.join(ids[:4])}{' ...' if len(ids) > 4 else ''})")
    if kind == "wall_vector_only":
        ids = sorted({i for m in members for i in m["ids"]})
        return (f"{level}: the vector reading has {size:.2f} m of wall {where} ({', '.join(ids[:4])}"
                f"{' ...' if len(ids) > 4 else ''}) that the raster reading does not see")
    if kind == "room_raster_only":
        names = ", ".join(m["what"]["raster"] for m in members[:3])
        return f"{level}: the raster reading closes {n} room{'s' if n > 1 else ''} ({size:.1f} m2) {where} that the " \
               f"vector reading does not have: {names}"
    if kind == "room_vector_only":
        names = ", ".join(m["what"]["vector"] for m in members[:3])
        return f"{level}: the raster reading does not close {names} {where} ({members[0]['what']['raster']})"
    if kind == "opening_raster_only":
        names = ", ".join(m["what"]["raster"] for m in members[:3])
        return f"{level}: the raster reading has {names} {where}; the vector reading has no opening there"
    if kind == "opening_vector_only":
        names = ", ".join(m["what"]["vector"] for m in members[:3])
        return f"{level}: the vector reading has {names} {where}; the raster reading has no opening there"
    a = members[0]["what"]
    return f"{level}: {where} the vector reading has a {a['vector']}, the raster reading a {a['raster']}"


def findings_of(level: str, raw: list) -> list:
    """The RC13 findings of one level from its raw differences (pure): grouped per kind (``group``), severity by size
    (``severity_by_size``; ``apply_trust`` lowers it afterwards), largest first within a kind."""
    out = []
    for kind in KINDS:
        items = [r for r in raw if r["kind"] == kind]
        for members in group(items):
            size = sum(float(m["size"]) for m in members)
            at = _centre(members)
            sev = severity_by_size(kind, size)
            ids = []
            for m in members:
                ids += [i for i in m["ids"] if i and i not in ids]
            extra = {"size": round(size, 3), "severity_by_size": sev, "members": len(members),
                     "what": {"vector": "; ".join(sorted({m["what"]["vector"] for m in members}))[:300],
                              "raster": "; ".join(sorted({m["what"]["raster"] for m in members}))[:300]}}
            if kind.startswith("wall"):
                extra["pieces"] = [[list(m["geom"][1]), list(m["geom"][2])] for m in members]
            elif kind.startswith("room"):
                extra["polygons"] = [m["geom"][1] for m in members]
            else:
                extra["points"] = [list(m["geom"][1]) for m in members]
                if kind in ("opening_raster_only", "opening_type_differs"):
                    extra["raster_class"] = members[0].get("raster_class")
                if kind == "opening_vector_only":
                    extra["vector_class"] = members[0].get("vector_class")
            out.append(_finding(sev, level, _message(level, kind, members, size, at), kind, place=at,
                                element_ids=ids, **extra))
    out.sort(key=lambda f: (KINDS.index(f["kind"]), -f["size"]))
    return out


# --------------------------------------------------------------------------------------------------------------- trust
def load_trust(path: Path = TRUST_PATH) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def apply_trust(findings: list, trust: Optional[dict]) -> list:
    """Each finding gets ``trust`` ``{precision, findings}`` of its kind; a kind below ``TRUST_MIN`` precision, or
    not calibrated, is written with severity ``info`` and its message says so (in place; returns the list)."""
    kinds = (trust or {}).get("kinds") or {}
    threshold = float((trust or {}).get("threshold") or TRUST_MIN)
    for f in findings:
        if f["kind"] not in KINDS:                  # a level's note (no reading, a weak reading): info by itself
            continue
        k = kinds.get(f["kind"]) or {}
        n, prec = int(k.get("findings") or 0), k.get("precision")
        f["trust"] = {"precision": prec, "findings": n, "threshold": threshold}
        if prec is None or n == 0:
            if f["severity"] != "info":
                f["severity"] = "info"
            f["message"] += " [info only: this kind of raster finding is not calibrated yet]"
        elif float(prec) < threshold:
            f["severity"] = "info"
            f["message"] += (f" [info only: raster precision for this kind {float(prec):.2f} on {n} calibrated "
                             f"findings < {threshold:g}]")
    return findings


def judge(finding: dict, truth_level: dict) -> Optional[bool]:
    """Whether the truth agrees with the raster side of a finding (pure): a raster-only wall piece the truth's walls
    cover (>= ``COVER_MIN`` of the group's length), a vector-only wall piece they do not; a raster-only room inside the
    truth's rooms, a vector-only room outside them (area-weighted); a raster-only opening with a truth opening of its
    class within the score's tolerance, a vector-only opening with none; a type difference where the truth has the
    raster's class. None when the finding cannot be judged."""
    kind = finding["kind"]
    tw = TR.positives(truth_level.get("walls") or [])
    if kind in ("wall_raster_only", "wall_vector_only"):
        total = covered = 0.0
        for a, b in finding.get("pieces") or []:
            w = {"start": a, "end": b, "thickness": None}
            ln = _seg_len(a, b)
            total += ln
            covered += ln * wall_cover_share(w, tw)
        if total <= 0:
            return None
        has = covered / total >= COVER_MIN
        return has if kind == "wall_raster_only" else not has
    if kind in ("room_raster_only", "room_vector_only"):
        tr = TR.positives(truth_level.get("rooms") or [])
        total = inside = 0.0
        for poly in finding.get("polygons") or []:
            area = _shoelace(poly)
            total += area
            inside += area * room_cover_share({"polygon": poly}, tr)
        if total <= 0:
            return None
        has = inside / total >= COVER_MIN
        return has if kind == "room_raster_only" else not has
    pts = finding.get("points") or []
    if not pts:
        return None

    def near(cls: Optional[str], p) -> bool:
        kinds = [k for k in OPENING_TYPES if cls is None or _kind_class(k) == cls]
        return any(o.get("center") and not o.get("virtual") and SC._dist(o["center"], p) <= SC.OPENING_CENTER_M
                   for k in kinds for o in TR.positives(truth_level.get(k) or []))

    if kind == "opening_raster_only":
        votes = [near(finding.get("raster_class"), p) for p in pts]
    elif kind == "opening_vector_only":
        votes = [not near(finding.get("vector_class"), p) for p in pts]
    else:
        votes = [near(finding.get("raster_class"), p) for p in pts]
    return sum(votes) * 2 >= len(votes)


# ---------------------------------------------------------------------------------------------------------- the render
def _cad_page(building: dict, lid: str, page: dict) -> dict:
    """The level's page from ``level_pages``, or a CAD page of the same level when that one is a PDF or an image
    (a level drawn by several documents)."""
    if Path(page.get("file") or "").suffix.lower() in (".dxf", ".dwg"):
        return page
    for doc in building.get("documents") or []:
        if Path(doc.get("file") or "").suffix.lower() not in (".dxf", ".dwg"):
            continue
        for pg in doc.get("pages") or []:
            if pg.get("level_id") == lid and pg.get("transform_to_building"):
                return {"region": pg.get("region_id"), "file": doc.get("file"), "tf": pg["transform_to_building"]}
    return page


def source_dxf(out_dir: Path, building: dict, file_rel: Optional[str]) -> Optional[Path]:
    """The converted DXF of a CAD document (``reading_check.source_dxf``), or the project's own DXF file."""
    from wenart import reading_check as RC

    p = RC.source_dxf(out_dir, file_rel)
    if p is not None:
        return p
    if file_rel and Path(file_rel).suffix.lower() == ".dxf":
        folder = (building.get("project") or {}).get("source_folder")
        for base in [Path(folder)] if folder else []:
            cand = base / file_rel
            if cand.is_file():
                return cand
        cand = REPO / "projects" / str((building.get("project") or {}).get("id")) / file_rel
        if cand.is_file():
            return cand
    return None


def level_box(doc, building: dict, lid: str, page: dict, regions: dict) -> Optional[list]:
    """The drawing-unit box to render: the level's sheet region, or for a one-plan document the drawing's extents
    (the model's box with a margin when the extents are far larger: stray entities)."""
    from ezdxf import bbox

    reg = regions.get(page.get("region"))
    if reg is not None:
        return [float(v) for v in reg["box"]]
    if page.get("region"):
        return None
    tf = page["tf"]
    inv = _invert(tf)
    pts = [_apply(inv, p) for w in building.get("walls") or [] if w.get("level_id") == lid for p in (w["start"], w["end"])]
    pts += [_apply(inv, p) for r in building.get("rooms") or [] if r.get("level_id") == lid
            for p in r.get("polygon") or []]
    model = None
    if pts:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        mpu = math.hypot(tf[0], tf[3]) or 1.0
        m = max(ONE_PLAN_MARGIN * max(max(xs) - min(xs), max(ys) - min(ys)), ONE_PLAN_MARGIN_M / mpu)
        model = [min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m]
    try:
        ext = bbox.extents(doc.modelspace(), fast=True)
        drawing = [ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y] if ext.has_data else None
    except Exception:  # noqa: BLE001 - no extents: the model's box
        drawing = None
    if drawing is None:
        return model
    if model is None:
        return drawing
    dw, dh = drawing[2] - drawing[0], drawing[3] - drawing[1]
    mw, mh = model[2] - model[0], model[3] - model[1]
    if max(dw, dh) > ONE_PLAN_EXTENT_FACTOR * max(mw, mh):
        return model
    return drawing


def render_level(doc, ents: list, box: list, tf: list, dest: Path, px_per_m: float = PX_PER_M,
                 max_side: int = MAX_SIDE_PX, clean: bool = None) -> dict:
    """The level's region drawn to a grey PNG ``dest`` (module docstring, step 1). Returns the render record:
    ``png``, ``size`` [w, h], ``px_per_m`` (after the cap), ``units_per_px``, ``box`` (the drawing box covered, its
    right and bottom edges moved to whole pixels), ``band_px``, ``dpi`` (the pHYs metadata), ``note``, ``scale_notes_hidden``
    and ``pixel_to_building`` (``pixel_transform``)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from PIL import Image, ImageDraw, ImageFont

    from wenart.ingest.generic import scale as GS

    clean = RENDER_CLEAN if clean is None else bool(clean)
    mpu = math.hypot(float(tf[0]), float(tf[3]))
    bw, bh = float(box[2]) - float(box[0]), float(box[3]) - float(box[1])
    if mpu <= 0 or bw <= 0 or bh <= 0:
        raise ValueError(f"empty box or transform: {box}, {tf}")
    ppm = float(px_per_m)
    if max(bw, bh) * mpu * ppm > max_side:
        ppm = math.floor(max_side / (max(bw, bh) * mpu) * 100.0) / 100.0      # ppm x NOTE_RATIO stays a whole number
    ppu = ppm * mpu
    upp = 1.0 / ppu
    w, h = int(math.ceil(bw * ppu)), int(math.ceil(bh * ppu))
    fig = plt.figure(figsize=(w / FIG_DPI, h / FIG_DPI), dpi=FIG_DPI)
    w, h = fig.canvas.get_width_height()                 # the canvas matplotlib really makes (a pixel may be lost)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        lineweight_scaling=LINEWEIGHT_SCALING)
    fe = Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg)
    hidden: list = []
    n_ents = len(ents)
    if clean:
        from wenart.reading_check import sheets as SH

        marks = SH.grid_and_dimension_marks(doc, ents)
        ents = [e for e in ents if id(e) not in marks]

    def hide(entity, properties):
        if clean and SH.is_grid_or_dimension(entity.dxftype(), properties.layer, properties.linetype_name):
            properties.is_visible = False
            return
        if entity.dxftype() in TEXT_TYPES:
            try:
                text = entity.plain_text() if entity.dxftype() == "MTEXT" else entity.dxf.get("text", "")
            except Exception:  # noqa: BLE001 - a text without content stays as it is
                return
            if text and GS.note_ratio(str(text)):
                properties.is_visible = False
                hidden.append(str(text)[:60])

    fe.push_property_override_function(hide)
    fe.draw_entities(ents)
    ax.set_xlim(float(box[0]), float(box[0]) + w * upp)
    ax.set_ylim(float(box[3]) - h * upp, float(box[3]))
    ax.axis("off")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    grey = Image.fromarray(rgba[..., :3]).convert("L")
    sheet = Image.new("L", (grey.width, grey.height + NOTE_BAND_PX), 255)
    sheet.paste(grey, (0, NOTE_BAND_PX))
    note = f"SCALE 1:{NOTE_RATIO}"
    try:
        font = ImageFont.truetype(NOTE_FONT, NOTE_TEXT_PX)
    except OSError:
        font = ImageFont.load_default()
    ImageDraw.Draw(sheet).text((30, (NOTE_BAND_PX - NOTE_TEXT_PX) // 2), note, fill=0, font=font)
    dpi = round(0.0254 * ppm * NOTE_RATIO, 4)
    sheet.save(dest, dpi=(dpi, dpi))
    right, bottom = float(box[0]) + grey.width * upp, float(box[3]) - grey.height * upp
    return {"png": str(dest), "size": [sheet.width, sheet.height], "px_per_m": ppm, "units_per_px": upp,
            "box": [float(box[0]), bottom, right, float(box[3])], "band_px": NOTE_BAND_PX, "dpi": dpi, "note": note,
            "scale_notes_hidden": hidden, "entities": n_ents, "entities_drawn": len(ents), "clean": clean,
            "pixel_to_building": pixel_transform([box[0], bottom, right, box[3]], upp, NOTE_BAND_PX, tf)}


# ------------------------------------------------------------------------------------------------------- the reading
@contextlib.contextmanager
def _env(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update({k: str(v) for k, v in values.items()})
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def read_raster(png: Path, work: Path) -> dict:
    """The raster reading of one PNG as a one-page raster project (``pipeline.run_project(no_ai=True)``, the reading
    check of that project off): ``{"building", "page", "seconds", "status", "reasons", "scale_used"}``; ``page`` is
    the image's page entry (``transform_to_building``, ``to_original``) or None when no level was read."""
    from wenart.ingest import pipeline as PL

    work = Path(work)
    proj, out = work / "project", work / "out"
    shutil.rmtree(work, ignore_errors=True)
    proj.mkdir(parents=True)
    shutil.copy(png, proj / Path(png).name)
    t = time.time()
    with _env(WENART_READING_CHECK="0"):
        building, build = PL.run_project(proj, out, no_ai=True)
    secs = round(time.time() - t, 1)
    page = None
    for doc in building.get("documents") or []:
        for pg in doc.get("pages") or []:
            if pg.get("transform_to_building") and pg.get("to_original") and pg.get("level_id"):
                page = dict(pg, file=doc.get("file"))
    reasons = list(getattr(build, "review_reasons", []) or [])
    scale = (page or {}).get("scale") or {}
    return {"building": building, "page": page, "seconds": secs, "status": building.get("status"),
            "reasons": [str(r)[:300] for r in reasons][:12],
            "warnings": [str(w)[:300] for w in building.get("warnings") or []][:40],
            "scale_used": {"method": scale.get("method"), "metres_per_unit": scale.get("metres_per_unit"),
                           "confidence": scale.get("confidence")} if scale else None}


def raster_to_level(page: dict, pixel_to_building: list) -> Callable:
    """The map from the raster reading's building metres to the vector level's building metres (pure): raster metres
    -> its page units (inverse of its ``transform_to_building``) -> the PNG's pixel centres (``to_original``) -> the
    level's metres (``pixel_to_building``)."""
    inv = _invert(page["transform_to_building"])
    h = page["to_original"]

    def f(p):
        return _apply(pixel_to_building, _apply_h(h, _apply(inv, p)))
    return f


def original_px_per_page_unit(page: dict) -> float:
    """PNG pixels per page unit of the raster reading (1 unless the reader resampled the page to its working
    resolution, ``raster.working_resolution``)."""
    h = page["to_original"]
    return math.hypot(float(h[0][0]), float(h[1][0])) / abs(float(h[2][2]) or 1.0)


def scale_off_pct(rr: dict, render: dict) -> Optional[float]:
    """How far the scale the raster reader used lies from the known pixel size, in % (pure; None without a scale):
    its metres per page unit over the PNG pixels per page unit, against 1 / px_per_m."""
    mpu = (rr.get("scale_used") or {}).get("metres_per_unit")
    if not mpu or not rr.get("page"):
        return None
    per_px = float(mpu) / original_px_per_page_unit(rr["page"])
    return round((per_px * float(render["px_per_m"]) - 1.0) * 100.0, 3)


def _length_factor(f: Callable, at=(0.0, 0.0)) -> float:
    a, b = f(at), f((at[0] + 1.0, at[1]))
    c = f((at[0], at[1] + 1.0))
    return 0.5 * (_seg_len(a, b) + _seg_len(a, c))


def map_building(rb: dict, f: Callable, level: str) -> dict:
    """The raster building's walls, openings, rooms and stairs in the vector level's frame, all on ``level`` (a
    one-page reading has one level; its own level id is the OCR's guess), as a building dict ``truth.extract`` reads."""
    k = _length_factor(f)

    def pt(p):
        x, y = f(p)
        return [round(x, 4), round(y, 4)]

    walls = []
    for w in rb.get("walls") or []:
        if not w.get("start") or not w.get("end"):
            continue
        walls.append(dict(w, level_id=level, start=pt(w["start"]), end=pt(w["end"]),
                          thickness=round(float(w["thickness"]) * k, 4) if w.get("thickness") is not None else None))
    openings = []
    for o in rb.get("openings") or []:
        if not o.get("center"):
            continue
        openings.append(dict(o, level_id=level, center=pt(o["center"]),
                             width=round(float(o["width"]) * k, 4) if o.get("width") is not None else None))
    rooms = []
    for r in rb.get("rooms") or []:
        poly = [pt(p) for p in r.get("polygon") or []]
        rooms.append(dict(r, level_id=level, polygon=poly, area_computed=round(_shoelace(poly), 3)))
    furniture = []
    for fp in TR.stairs_of(rb):
        fpr = dict(fp.get("footprint") or {})
        if fpr.get("center"):
            fpr["center"] = pt(fpr["center"])
        if fpr.get("size"):
            fpr["size"] = [float(s) * k for s in fpr["size"]]
        furniture.append(dict(fp, level_id=level, footprint=fpr))
    return {"project": rb.get("project"), "levels": [{"id": level, "label": level}], "walls": walls,
            "openings": openings, "rooms": rooms, "furniture": furniture}


# ---------------------------------------------------------------------------------------------------------- per level
def _overlay(png: Path, render: dict, vec: dict, ras: dict, findings: list, dest: Path) -> Optional[Path]:
    """The evidence image of a level: the render in light grey, the vector walls red, the raster walls blue, each
    finding's place circled and numbered (its index in the level's findings), at most ``OVERLAY_LONG_PX`` long."""
    from PIL import Image, ImageDraw, ImageFont

    try:
        im = Image.open(png).convert("L")
    except OSError:
        return None
    s = min(1.0, OVERLAY_LONG_PX / float(max(im.size)))
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
    base = Image.eval(im, lambda v: 170 + v * 85 // 255).convert("RGB")
    d = ImageDraw.Draw(base)
    inv = _invert(render["pixel_to_building"])

    def px(p):
        u, v = _apply(inv, p)
        return (u * s, v * s)

    width = max(2, int(round(3 * s * render["px_per_m"] / 100.0)))
    for w in vec.get("walls") or []:
        d.line([px(w["start"]), px(w["end"])], fill=(200, 30, 30), width=width + 2)
    for w in ras.get("walls") or []:
        d.line([px(w["start"]), px(w["end"])], fill=(30, 80, 220), width=width)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for k, f in enumerate(findings, 1):
        if not f.get("place"):
            continue
        u, v = px((f["place"]["x"], f["place"]["y"]))
        col = {"major": (230, 0, 0), "minor": (230, 120, 0)}.get(f.get("severity_by_size"), (120, 120, 120))
        d.ellipse([u - 9, v - 9, u + 9, v + 9], outline=col, width=2)
        d.text((u + 10, v - 10), str(k), fill=col, font=font)
    base.save(dest, quality=82)
    return dest


def level_opinion(out_dir: Path, building: dict, lid: str, page: dict, doc, regions: dict, work: Path,
                  keep_images: bool = False) -> dict:
    """The raster opinion of one level: render, read, map, compare (module docstring steps 1-3). Returns
    ``{level, render, raster: {status, seconds, scale_used, counts ...}, agreement, findings, vector, raster_level}``
    (``vector`` and ``raster_level``: the truth-shaped level dicts, for the calibration)."""
    from wenart.reading_check import sheets as SH

    t0 = time.time()
    rec: dict = {"level": lid, "file": page.get("file"), "region": page.get("region")}
    box = level_box(doc, building, lid, page, regions)
    if box is None:
        rec.update(status="skipped", reason="no box for the level's region")
        return rec
    ents = SH._entities(doc, box)
    wd = Path(work) / lid
    png = wd / f"plan_{lid}.png"
    render = render_level(doc, ents, box, page["tf"], png)
    rec["render"] = {k: v for k, v in render.items() if k != "png"}
    rec["render"]["seconds"] = round(time.time() - t0, 1)
    vec_all = TR.extract(building)
    vec = (vec_all.get("per_level") or {}).get(lid) or {t: [] for t in TR.ELEMENT_TYPES}
    try:
        rr = read_raster(png, wd / "read")
    except Exception as exc:  # noqa: BLE001 - a failed raster reading is the level's result, never a stop
        rr = {"building": {}, "page": None, "seconds": None, "status": "error",
              "reasons": [f"{type(exc).__name__}: {str(exc)[:240]}"], "warnings": [], "scale_used": None}
    rec["raster"] = {k: rr[k] for k in ("status", "seconds", "reasons", "scale_used")}
    rec["raster"]["warnings"] = rr.get("warnings") or []
    if rr["page"] is None:
        ras = {t: [] for t in TR.ELEMENT_TYPES}
        rec["raster"]["read"] = False
    else:
        f = raster_to_level(rr["page"], render["pixel_to_building"])
        mapped = map_building(rr["building"], f, lid)
        ras = TR.extract(mapped, source="raster_opinion")["per_level"][lid]
        rec["raster"]["read"] = True
        rec["raster"]["level_read_as"] = rr["page"].get("level_id")
        rec["raster"]["length_factor"] = round(_length_factor(f), 5)
        off = scale_off_pct(rr, render)
        if off is not None:
            rec["raster"]["scale_off_pct"] = off
    rec["raster"]["counts"] = {t: len(ras.get(t) or []) for t in TR.ELEMENT_TYPES}
    rec["vector_counts"] = {t: len(vec.get(t) or []) for t in TR.ELEMENT_TYPES}
    agreement = SC.match({"levels": [{"id": lid}], "per_level": {lid: vec}},
                         {"levels": [{"id": lid}], "per_level": {lid: ras}})
    rec["agreement"] = {t: agreement[t] for t in TR.ELEMENT_TYPES}
    seen = wall_length_share(vec.get("walls") or [], ras.get("walls") or [])
    rec["raster_sees_vector_walls"] = round(seen, 3) if seen is not None else None
    back = wall_length_share(ras.get("walls") or [], vec.get("walls") or [])
    rec["vector_sees_raster_walls"] = round(back, 3) if back is not None else None
    rec["findings"] = []
    if rr["page"] is not None:
        raw = raw_differences(vec, ras)
        if seen is not None and seen < WEAK_WALL_SHARE:
            folded = [r for r in raw if r["kind"] in VECTOR_ONLY_KINDS]
            raw = [r for r in raw if r["kind"] not in VECTOR_ONLY_KINDS]
            rec["folded"] = {k: sum(1 for r in folded if r["kind"] == k) for k in VECTOR_ONLY_KINDS}
            rec["findings"].append(_finding(
                "info", lid, f"{lid}: the raster reading sees only {seen * 100:.0f} % of the vector reading's wall "
                f"length (below {WEAK_WALL_SHARE * 100:.0f} %): it is too weak here to say what the vector reading "
                f"has too much; {len(folded)} vector-only differences are not listed one by one ("
                + ", ".join(f"{k} {n}" for k, n in rec["folded"].items() if n) + "); what the raster sees and the "
                "vector does not is listed", "raster_weak", severity_by_size="info", size=0.0,
                raster_sees_vector_walls=round(seen, 3)))
        rec["findings"] += findings_of(lid, raw)
    if rr["page"] is None:
        rec["findings"] = [_finding("info", lid, f"{lid}: the raster reader read no level from the render ("
                                    f"{'; '.join(rr['reasons'][:2]) or rr['status']}): no second opinion",
                                    "no_raster_reading", severity_by_size="info", size=0.0)]
    ov = Path(out_dir) / "reading_check" / f"raster_{lid}.jpg"
    ov.parent.mkdir(parents=True, exist_ok=True)
    made = _overlay(png, render, vec, ras, rec["findings"], ov)
    rec["overlay"] = ov.relative_to(out_dir).as_posix() if made else None
    rec["vector"], rec["raster_level"] = vec, ras
    rec["seconds"] = round(time.time() - t0, 1)
    if not keep_images:
        shutil.rmtree(wd, ignore_errors=True)
    return rec


def opinion(out_dir, work: Optional[Path] = None, levels: Optional[list] = None, trust: Optional[dict] = None,
            keep_images: bool = False, log: Optional[Callable] = None) -> dict:
    """The raster opinion of a pipeline output (module docstring): per level the render, the raster reading, the
    agreement numbers and the findings (trust applied); writes ``reading_check/raster_opinion.json`` and ``.md``."""
    import ezdxf

    from wenart import reading_check as RC

    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sp = out_dir / "sheets.json"
    sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    regions = {r["id"]: r for r in sheets.get("regions") or []}
    trust = trust if trust is not None else load_trust()
    own_work = work is None
    work = Path(work) if work is not None else Path(tempfile.mkdtemp(prefix="raster_opinion_"))
    docs: dict = {}
    res: dict = {"project": (building.get("project") or {}).get("id"), "commit": TR.git_head(),
                 "date": _dt.date.today().isoformat(), "levels": [], "notes": []}
    t0 = time.time()
    for lid, pg in RC.level_pages(building).items():
        if levels and lid not in levels:
            continue
        pg = _cad_page(building, lid, pg)
        dxf = source_dxf(out_dir, building, pg.get("file"))
        if dxf is None:
            res["notes"].append(f"{lid}: no CAD source (a PDF or raster page): no raster opinion")
            continue
        if dxf not in docs:
            docs = {dxf: ezdxf.readfile(str(dxf))}                  # one document in memory at a time
        try:
            rec = level_opinion(out_dir, building, lid, pg, docs[dxf], regions, work, keep_images=keep_images)
        except Exception as exc:  # noqa: BLE001 - one level must not stop the others
            rec = {"level": lid, "status": "error", "reason": f"{type(exc).__name__}: {str(exc)[:300]}",
                   "findings": []}
        apply_trust(rec.get("findings") or [], trust)
        res["levels"].append(rec)
        if log:
            log(f"{res['project']} {lid}: {len(rec.get('findings') or [])} findings, "
                f"{(rec.get('raster') or {}).get('seconds')} s raster, {rec.get('seconds')} s in all")
    res["seconds"] = round(time.time() - t0, 1)
    res["findings"] = [f for rec in res["levels"] for f in rec.get("findings") or []]
    res["counts"] = {s: sum(1 for f in res["findings"] if f["severity"] == s) for s in ("major", "minor", "info")}
    res["counts_by_kind"] = {k: sum(1 for f in res["findings"] if f["kind"] == k) for k in KINDS}
    res["trust"] = {"commit": (trust or {}).get("commit"), "threshold": (trust or {}).get("threshold", TRUST_MIN),
                    "kinds": {k: (v.get("precision"), v.get("findings"))
                              for k, v in ((trust or {}).get("kinds") or {}).items()}}
    write(out_dir, res)
    if own_work:
        shutil.rmtree(work, ignore_errors=True)
    return res


def _public(res: dict) -> dict:
    """The result without the truth-shaped level dicts (kept in memory for the calibration only)."""
    out = dict(res)
    out["levels"] = [{k: v for k, v in rec.items() if k not in ("vector", "raster_level")} for rec in res["levels"]]
    return out


def write(out_dir: Path, res: dict) -> Path:
    """``reading_check/raster_opinion.json`` and ``.md``."""
    d = Path(out_dir) / "reading_check"
    d.mkdir(parents=True, exist_ok=True)
    (d / "raster_opinion.json").write_text(json.dumps(_public(res), ensure_ascii=False, indent=1) + "\n",
                                           encoding="utf-8")
    lines = [f"# Raster second opinion (RC13, advisory): {res.get('project')}", "",
             f"Every level read from a CAD region was drawn to an image and read again by the raster reader "
             f"(``wenart.reading_check.raster_opinion``). Findings: {res['counts']['major']} major, "
             f"{res['counts']['minor']} minor, {res['counts']['info']} info; {res.get('seconds')} s. "
             f"Advisory: they gate nothing until the trust file shows the kind earned it.", "",
             "| level | px/m | raster read | scale used | raster s | walls v/r | rooms v/r | doors v/r | windows v/r | "
             "wall F1 | room F1 | findings |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for rec in res["levels"]:
        r, v, a = rec.get("raster") or {}, rec.get("vector_counts") or {}, rec.get("agreement") or {}
        rc = r.get("counts") or {}
        sc = r.get("scale_used") or {}
        lines.append(f"| {rec['level']} | {(rec.get('render') or {}).get('px_per_m', '-')} | "
                     f"{'yes' if r.get('read') else 'no: ' + str(rec.get('reason') or r.get('status'))} | "
                     f"{sc.get('method') or '-'} ({r.get('scale_off_pct', '-')} %) | {r.get('seconds', '-')} | "
                     f"{v.get('walls', 0)}/{rc.get('walls', 0)} | {v.get('rooms', 0)}/{rc.get('rooms', 0)} | "
                     f"{v.get('doors', 0)}/{rc.get('doors', 0)} | {v.get('windows', 0)}/{rc.get('windows', 0)} | "
                     f"{(a.get('walls') or {}).get('f1', '-')} | {(a.get('rooms') or {}).get('f1', '-')} | "
                     f"{len(rec.get('findings') or [])} |")
    lines += ["", "| # | level | kind | severity (by size) | finding |", "|---|---|---|---|---|"]
    for rec in res["levels"]:
        for k, f in enumerate(rec.get("findings") or [], 1):
            lines.append(f"| {k} | {f.get('level_id')} | {f['kind']} | {f['severity']} ({f.get('severity_by_size')}) "
                         f"| {f['message'].replace('|', '/')} |")
    if res.get("notes"):
        lines += ["", "Notes:"] + [f"- {n}" for n in res["notes"]]
    (d / "raster_opinion.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


# ------------------------------------------------------------------------------------------------------- calibration
def calibrate_project(project: str, res: dict, truth: dict) -> dict:
    """The raster reading of one project scored against its truth and its findings judged (pure over the opinion's
    result and the truth dict): ``{raster_score, raster_types, findings: {kind: n}, right: {kind: n},
    unjudged: {kind: n}, judged: [(level, kind, right)]}``. Levels the truth does not have are left out."""
    t_levels = {lv["id"] for lv in truth.get("levels") or []}
    read = {"levels": [], "per_level": {}}
    for rec in res["levels"]:
        if rec["level"] in t_levels and "raster_level" in rec:
            read["levels"].append({"id": rec["level"]})
            read["per_level"][rec["level"]] = rec["raster_level"]
    scored = dict(truth, levels=[lv for lv in truth.get("levels") or [] if lv["id"] in read["per_level"]])
    m = SC.match(scored, read) if read["levels"] else None
    counts = {k: 0 for k in KINDS}
    right = {k: 0 for k in KINDS}
    unjudged = {k: 0 for k in KINDS}
    judged = []
    for rec in res["levels"]:
        tl = (truth.get("per_level") or {}).get(rec["level"])
        if tl is None:
            continue
        for f in rec.get("findings") or []:
            if f["kind"] not in counts:
                continue
            ok = judge(f, tl)
            if ok is None:
                unjudged[f["kind"]] += 1
                continue
            counts[f["kind"]] += 1
            right[f["kind"]] += int(ok)
            judged.append((rec["level"], f["kind"], bool(ok)))
    return {"raster_score": m["total"] if m else None,
            "raster_types": {t: m[t]["f1"] for t in SC.TYPES} if m else None,
            "levels_scored": sorted(read["per_level"]), "findings": counts, "right": right, "unjudged": unjudged,
            "judged": judged}


def trust_from(per_project: dict, commit: Optional[str] = None) -> dict:
    """The trust file's content from the calibration of several projects (pure)."""
    kinds = {}
    for k in KINDS:
        n = sum(int(v["findings"].get(k, 0)) for v in per_project.values() if v.get("findings"))
        r = sum(int(v["right"].get(k, 0)) for v in per_project.values() if v.get("right"))
        kinds[k] = {"findings": n, "right": r, "precision": round(r / n, 4) if n else None,
                    "trusted": bool(n) and r / n >= TRUST_MIN}
    return {"note": TRUST_NOTE, "commit": commit, "date": _dt.date.today().isoformat(), "threshold": TRUST_MIN,
            "projects": sorted(per_project), "kinds": kinds,
            "per_project": {p: {k: v.get(k) for k in ("raster_score", "vector_score", "findings", "right", "unjudged",
                                                       "seconds", "levels_scored", "error")
                                if v.get(k) is not None}
                            for p, v in sorted(per_project.items())}}


def save_trust(trust: dict, path: Path = TRUST_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trust, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def calibration_table(per_project: dict) -> str:
    """The calibration table as text: project, raster score, vector score, findings per kind (right / judged)."""
    short = {"wall_raster_only": "wall r", "wall_vector_only": "wall v", "room_raster_only": "room r",
             "room_vector_only": "room v", "opening_raster_only": "open r", "opening_vector_only": "open v",
             "opening_type_differs": "type"}
    rows = [["project", "raster", "vector", "s"] + [short[k] for k in KINDS]]
    for p, v in sorted(per_project.items()):
        if v.get("error"):
            rows.append([p, "error", "-", "-"] + ["-"] * len(KINDS))
            continue
        rows.append([p, f"{v['raster_score']:.1f}" if v.get("raster_score") is not None else "-",
                     f"{v['vector_score']:.1f}" if v.get("vector_score") is not None else "-",
                     f"{v.get('seconds', 0):.0f}"]
                    + [f"{v['right'][k]}/{v['findings'][k]}" for k in KINDS])
    tot = trust_from(per_project)["kinds"]
    rows.append(["precision", "", "", ""] + [f"{tot[k]['precision']:.2f}" if tot[k]["precision"] is not None else "-"
                                             for k in KINDS])
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(c.rjust(widths[i]) if i else c.ljust(widths[i]) for i, c in enumerate(r))
                     for r in rows)


def calibrate(projects: list, work: Path, fresh: bool = False, log: Callable = print) -> dict:
    """Read every project (``truth.reading``), run the opinion with no trust applied, score and judge against the
    truth; returns ``{project: calibration}`` (an error per project instead of a stop)."""
    per: dict = {}
    for p in projects:
        t = time.time()
        try:
            truth = TR.load_truth(p)
            if truth is None:
                raise FileNotFoundError(f"no truth file for {p}")
            folder = TR.reading(p, Path(work), fresh)
            b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
            vscore = SC.match(truth, TR.extract(b, project=p, leave_out=truth.get("levels_left_out") or []))["total"]
            res = opinion(folder, work=Path(work) / "_raster" / p, trust={}, log=log,
                          levels=[lv["id"] for lv in truth.get("levels") or []])   # only what the truth can judge
            cal = calibrate_project(p, res, truth)
            cal.update(vector_score=vscore, seconds=round(time.time() - t, 1), opinion_seconds=res.get("seconds"))
        except Exception as exc:  # noqa: BLE001 - one project must not stop the others
            cal = {"error": f"{type(exc).__name__}: {str(exc)[:300]}", "seconds": round(time.time() - t, 1)}
        per[p] = cal
        log(f"{p}: raster {cal.get('raster_score')} vector {cal.get('vector_score')} findings "
            f"{sum((cal.get('findings') or {}).values())} right {sum((cal.get('right') or {}).values())} "
            f"({cal.get('seconds')} s){' ' + cal['error'] if cal.get('error') else ''}")
    return per


def telling(findings: list, n: int = 10) -> list:
    """The ``n`` most telling findings (pure): the kinds the trust file trusts first, then by severity by size and by
    size (walls in metres, rooms in m2 / 4, openings 1)."""
    def weight(f):
        size = float(f.get("size") or 0.0)
        if f["kind"].startswith("room"):
            size /= 4.0
        trusted = (f.get("trust") or {}).get("precision")
        return (0 if trusted is not None and float(trusted) >= TRUST_MIN else 1,
                SEVERITY_ORDER.get(f.get("severity_by_size"), 3), -size)
    return sorted(findings, key=weight)[:n]


# ------------------------------------------------------------------------------------------------------ command line
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check raster", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="the raster opinion of one pipeline output")
    c.add_argument("--out", required=True, help="the pipeline output folder (building.json, sheets.json, converted/)")
    c.add_argument("--levels", default=None, help="comma separated level ids (default: every CAD level)")
    c.add_argument("--work", default=None, help="work folder for the renders and raster readings (default: temporary)")
    c.add_argument("--keep-images", action="store_true", help="keep the renders and the raster readings in --work")
    k = sub.add_parser("calibrate", help="score the raster readings and judge the findings against the truth")
    k.add_argument("--projects", default=None, help="comma separated (default: every project with a truth file)")
    k.add_argument("--work", required=True, help="work folder (a vector reading already there is used again)")
    k.add_argument("--fresh", action="store_true", help="read the projects again")
    k.add_argument("--write", action="store_true", help=f"store the precision per kind in {TRUST_PATH.name}")
    k.add_argument("--json", default=None, help="write the per-project calibration to this file")
    p = sub.add_parser("projects", help="read projects and run the opinion on each; the most telling findings")
    p.add_argument("--projects", required=True, help="comma separated")
    p.add_argument("--work", required=True, help="work folder (a vector reading already there is used again)")
    p.add_argument("--fresh", action="store_true")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--json", default=None, help="write the findings of every project to this file")
    args = ap.parse_args(argv)

    def log(msg):
        print(msg, file=sys.stderr, flush=True)

    if args.cmd == "check":
        res = opinion(args.out, work=Path(args.work) if args.work else None,
                      levels=[x.strip() for x in args.levels.split(",")] if args.levels else None,
                      keep_images=args.keep_images, log=log)
        print(f"raster opinion {res['project']}: {res['counts']} in {res['seconds']} s -> "
              f"{Path(args.out) / 'reading_check' / 'raster_opinion.md'}")
        return 0
    if args.cmd == "calibrate":
        projects = [x.strip() for x in (args.projects or "").split(",") if x.strip()] or TR.truth_projects()
        per = calibrate(projects, Path(args.work), fresh=args.fresh, log=log)
        print(calibration_table(per))
        if args.json:
            Path(args.json).write_text(json.dumps(per, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if args.write:
            ok = {q: v for q, v in per.items() if not v.get("error")}
            print(f"trust: {save_trust(trust_from(ok, TR.git_head()))}")
        return 0
    trust = load_trust()
    every = []
    for q in [x.strip() for x in args.projects.split(",") if x.strip()]:
        t = time.time()
        try:
            folder = TR.reading(q, Path(args.work), args.fresh)
            res = opinion(folder, work=Path(args.work) / "_raster" / q, trust=trust, log=log)
        except Exception as exc:  # noqa: BLE001 - one project must not stop the others
            log(f"{q}: {type(exc).__name__}: {exc}")
            continue
        log(f"{q}: {res['counts']} ({round(time.time() - t, 1)} s, opinion {res['seconds']} s)")
        for f in res["findings"]:
            every.append(dict(f, project=q))
    for f in telling(every, args.top):
        print(f"{f['project']} {f['level_id']} {f['kind']} [{f['severity']}/{f.get('severity_by_size')}] "
              f"{f['message']}")
    if args.json:
        Path(args.json).write_text(json.dumps(every, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
