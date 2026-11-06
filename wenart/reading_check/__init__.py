"""The reading self-check: the model the reading made, checked against the drawing, before any pod run (2 Nov 2026).

What: ``check(out_dir)`` reads a pipeline output (``building.json``, ``sheets.json`` and the converted DXF of each
CAD document) and returns the findings, each with its check, severity, level and place:

- RC1 a level left out of the model (critical);
- RC2 floors that do not stack: the shared axis grid's axes (the labelled bubbles) and the core's stair (the same
  concentric arcs) of each level against the reference level's, in the building frame (critical over 0.30 m, major
  over ``STACK_TOL_M``);
- RC3 a room whose area differs from the drawing's own area text in it (``220.60 m2``; major over 5 % and 1 m2);
- RC4 drawn wall lines the model does not build (the strokes of the layers whose name means wall, plaster or column,
  ``generic.layer_names``; major over ``MISSING_MAJOR_M`` of wall face per level);
- RC5 model walls on no drawn wall line (major; inferred walls are listed apart);
- RC6 the reading's own review reasons (needs review) and the labels it found outside the building (major); the
  sheets' review reasons (critical: a pod's sheets stage stops the project) and their schema errors (major);
- RC7 low-confidence places (4 Nov 2026, Milestone 14 R2; user: "never leave a level out; carry confidence instead"):
  a level built with ``reading_confidence: low`` (its ``reading_review`` reasons; major), every room label the level
  left in no closed face (``reading_places``; minor) and every wall the outline closure inferred (evidence rule
  ``outline_closure``, confidence 0.3; minor). The places with a position are numbered ("place 7") so the user can
  name them on the comparison sheets, where they are drawn in their own colour; RC7 is listed first in the markdown.
  RC7 alone never changes the verdict: these are places to check, not a stop.

- RC8 to RC12 (5 Nov 2026, Milestone 14 R5, ``wenart.reading_check.crossdoc``): the cross-document checks, advisory
  (reported, counted under ``counts["advisory"]``, never in the verdict until they earn it).
- RC14 (6 Nov 2026, Milestone 14 R6, ``wenart.reading_check.sense``): the architectural-sense checks (a room type
  implausible for its area, a small room's label naming a larger face, the sheet frame read as walls, unread walls,
  circulation, notation in room names), advisory like RC8-RC12; a rule below its judged precision writes info.

``verdict``: ``ready`` without a critical finding, else ``fix before a pod run``. ``write(out_dir, result)`` writes
``reading_check/reading_check.json`` and ``.md``; ``wenart.reading_check.sheets`` draws the comparison sheets (the
drawing, the model in the drawing's orientation, the model's walls over the drawing, the findings marked).

Why: real10 (user: "We need to improve this initial project reading part currently it is requiring a lot of fixing",
"go ahead with all 4"): the floors did not stack, the 2nd basement was left out and the axis lines were read as walls,
and nothing saw it until a pod had rendered the model ($10+, 5 h). The check runs here, on the CPU, in minutes.

How: pure reading of the files; the drawing's strokes come from the same DXF reader as the reading
(``ingest.dxf_generic``), mapped by each level's page transform from ``building.json`` (what the model used).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Optional

STACK_TOL_M = 0.05
STACK_CRITICAL_M = 0.30
AREA_TOL_SHARE = 0.05
AREA_TOL_M2 = 1.0
WALL_NEAR_M = 0.12            # a drawn face line this far beyond a model wall's half thickness still counts as built
MISSING_MAJOR_M = 3.0         # a level's drawn wall face the model lacks, in metres, before it is a major finding
MISSING_PIECE_M = 1.0         # pieces shorter than this are not listed one by one
DRAWN_SHARE_MIN = 0.5         # a model wall with less than this share of its length along drawn lines is not drawn
SEGMENT_MIN_M = 0.3
AREA_RE = re.compile(r"(\d{1,4}[.,]\d{1,2})\s*(?:M2|M²|M\^2)\b", re.IGNORECASE)
CHECKS = {"RC1": "level left out", "RC2": "floors do not stack", "RC3": "room area against the drawing's area text",
          "RC4": "drawn walls the model does not build", "RC5": "model walls on no drawn wall line",
          "RC6": "the reading's own review reasons", "RC7": "low-confidence places"}
# 4 Nov 2026 (RC7): the evidence rule of the walls the outline closure inferred (``generic.core.OUTLINE_CLOSURE_RULE``,
# the same word; tests/test_reading_closure_20261104.py pins it) and the confidence a level built with review reasons
# carries (``pipeline.READING_CONFIDENCE_LOW``)
CLOSURE_RULE = "outline_closure"
CONFIDENCE_LOW = "low"


def _finding(check: str, severity: str, level: Optional[str], message: str, **extra) -> dict:
    return dict({"check": check, "name": CHECKS[check], "severity": severity, "level_id": level,
                 "message": message}, **extra)


def _apply(tf, p):
    return (tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5])


def level_pages(building: dict) -> dict:
    """``{level_id: {"region", "file", "tf"}}`` of the levels read from a CAD region (the page transform the model
    used); a typical floor's copies are left out (their plan is the typical floor's)."""
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    out = {}
    for doc in building.get("documents") or []:
        for pg in doc.get("pages") or []:
            lid, tf = pg.get("level_id"), pg.get("transform_to_building")
            if not lid or not tf or lid in out:
                continue
            if (levels.get(lid) or {}).get("typical_of"):
                continue
            out[lid] = {"region": pg.get("region_id"), "file": doc.get("file"), "tf": tf}
    return out


def source_dxf(out_dir: Path, file_rel: Optional[str]) -> Optional[Path]:
    """The converted DXF of a CAD document in the pipeline output (``converted/<stem>.dxf``), else the DXF itself.

    6 Nov 2026 (found by the out-of-sample calibration of RC14): a project drawn in DXF has no ``converted/`` copy, and
    this returned None for it, so every check that reads the drawing (RC2 stacking, RC4/RC5 walls, RC14's text rules)
    was silent on DXF projects. Now the project's own DXF is used: ``file_rel`` is relative to the project folder,
    found from ``building.json``'s project id under ``projects/`` (or ``file_rel`` itself when it exists)."""
    if not file_rel:
        return None
    stem = Path(file_rel).stem
    cand = Path(out_dir) / "converted" / f"{stem}.dxf"
    if cand.is_file():
        return cand
    if Path(file_rel).suffix.lower() != ".dxf":
        return None
    own = Path(file_rel)
    if own.is_absolute() and own.is_file():
        return own
    try:
        building = json.loads((Path(out_dir) / "building.json").read_text(encoding="utf-8"))
        project = (building.get("project") or {}).get("id")
    except (OSError, ValueError):
        project = None
    if project:
        cand = Path(__file__).resolve().parents[2] / "projects" / project / file_rel
        if cand.is_file():
            return cand
    return None


def read_level_page(out_dir: Path, sheets: dict, page: dict):
    """The generic page of a level's region (the strokes and texts, source units), or None."""
    from wenart.ingest import dxf_generic

    regions = {r["id"]: r for r in sheets.get("regions") or []}
    reg = regions.get(page.get("region"))
    dxf = source_dxf(out_dir, page.get("file"))
    if dxf is None:
        return None
    if reg is None:
        # a document of one plan (no multi-plan sheet): the whole drawing, at the page transform's scale
        if page.get("region"):
            return None
        tf = page.get("tf") or [1.0, 0, 0, 0, 1.0, 0]
        return dxf_generic.read_page(str(dxf), page["file"], units_to_m_override=math.hypot(tf[0], tf[3]))
    return dxf_generic.read_page(str(dxf), page["file"], region_box=tuple(reg["box"]),
                                 units_to_m_override=reg.get("metres_per_unit"))


# ---------------------------------------------------------------------------------------------------- anchors (RC2)
def page_axes(page, tf) -> dict:
    """``{label: ("v", x) | ("h", y)}`` in building metres: the labelled bubbles of the axis grid (two of a label
    along one line)."""
    from wenart.ingest.generic import axes as AX

    bub = AX.bubbles(page.strokes, page.texts)
    if not bub:
        return {}
    pts: dict = {}
    for t in page.texts:
        label = " ".join(str(t.text or "").upper().split())
        if not AX.GRID_LABEL_RE.match(label):
            continue
        c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        for cx, cy, r in bub:
            if math.dist(c, (cx, cy)) <= 0.6 * r:
                pts.setdefault(label, []).append(_apply(tf, (cx, cy)))
                break
    out = {}
    for label, ps in pts.items():
        if len(ps) < 2:
            continue
        xs, ys = [p[0] for p in ps], [p[1] for p in ps]
        if max(xs) - min(xs) <= 0.10 and max(ys) - min(ys) >= 3.0:
            out[label] = ("v", sum(xs) / len(xs))
        elif max(ys) - min(ys) <= 0.10 and max(xs) - min(xs) >= 3.0:
            out[label] = ("h", sum(ys) / len(ys))
    return out


# 3 Nov 2026 (real07: the WCs and basins of two different floors, on 'S-TEF' and 'TEFRIŞ', made the upper floor
# "5.67 m off" though its outline lies exactly on the ground floor's): arcs on these layers move from floor to floor
NOT_ANCHOR_ROLES = ("furniture", "sanitary", "finish", "dimension", "text", "hatch", "site", "door", "window", "glass")


def page_stairs(page, tf) -> list:
    """``[((x, y), radii)]`` in building metres: sets of concentric arcs (a spiral stair's eye, a newel) with at
    least three radii; arcs on a layer whose name means furniture, sanitary ware, a finish, a door or a window
    (``NOT_ANCHOR_ROLES``) are no anchors."""
    from wenart.ingest.generic import layer_names as LN

    s = math.hypot(tf[0], tf[3])
    groups: dict = {}
    for st in page.strokes:
        arc = getattr(st, "arc", None)
        if not arc or LN.layer_role(getattr(st, "layer", None)) in NOT_ANCHOR_ROLES:
            continue
        r = float(arc["radius"]) * s
        if not (0.05 <= r <= 1.5):
            continue
        c = _apply(tf, arc["center"])
        key = (round(c[0], 2), round(c[1], 2))
        g = groups.setdefault(key, {"radii": set(), "pts": []})
        g["radii"].add(round(r, 2))
        g["pts"].append(c)
    return [((sum(p[0] for p in g["pts"]) / len(g["pts"]), sum(p[1] for p in g["pts"]) / len(g["pts"])), g["radii"])
            for g in groups.values() if len(g["radii"]) >= 3]


def page_stair_lines(page, tf):
    """The line segments on the stair layers (``layer_names`` role ``stair``) in building metres (an ``(m, 2, 2)``
    array)."""
    import numpy as np

    from wenart.ingest.generic import layer_names as LN

    out = []
    for st in page.strokes:
        if LN.layer_role(getattr(st, "layer", None)) != "stair":
            continue
        pts = [_apply(tf, p) for p in getattr(st, "pts", []) or []]
        out += [(a, b) for a, b in zip(pts[:-1], pts[1:])]
    return np.array(out, dtype=float).reshape(-1, 2, 2)


def stair_line_gap(lines, other) -> Optional[float]:
    """3 Nov 2026 (real09: the attic's three stairs on 'merdiven' lay 3.70 m off the duplex floor's): how far a level's
    stair-layer lines (segments) lie from the same stairs on the level next to it (``register.stair_layer_fit``: a clear
    fit of at least half of them), None without a clear fit."""
    from wenart.sheets import register as RG

    if lines is None or other is None or not len(lines) or not len(other):
        return None
    fit = RG.stair_layer_fit(other, RG.sample_segments(lines))
    if fit is None or fit["share"] < RG.STAIR_LAYER_SHARE or fit["second"] >= RG.STAIR_LAYER_UNIQUE:
        return None
    return math.hypot(*fit["shift"])


def stacking(anchors: dict, reference: str, orders: Optional[dict] = None) -> list:
    """RC2 findings: each level's axes and stairs against the reference level's, and its stair-layer lines against
    the level's next to it (below, else above; ``orders``: ``{level: order}``) (``anchors``: ``{level: {"axes",
    "stairs", "stair_lines"}}``)."""
    out = []
    ref = anchors.get(reference) or {}
    orders = orders or {}
    by_order = {o: lid for lid, o in orders.items() if lid in anchors}
    ref_order = orders.get(reference)
    for lid, a in anchors.items():
        if lid == reference:
            continue
        gaps = []
        lo = orders.get(lid)
        if lo is not None and ref_order is not None and lo != ref_order:
            nxt = by_order.get(lo - 1 if lo > ref_order else lo + 1)   # the level next to it, toward the reference
            if nxt is not None:
                g = stair_line_gap(a.get("stair_lines"), (anchors.get(nxt) or {}).get("stair_lines"))
                if g is not None:
                    gaps.append((g, f"the stair lines on {nxt}"))
        for label, (o, c) in (a.get("axes") or {}).items():
            ro = (ref.get("axes") or {}).get(label)
            if ro and ro[0] == o:
                gaps.append((abs(c - ro[1]), f"axis {label}"))
        # each arc set against the nearest set of the same radii on the reference (fixtures repeat their arcs)
        for c0, r0 in a.get("stairs") or []:
            near = [math.dist(c0, c1) for c1, r1 in ref.get("stairs") or [] if len(r0 & r1) >= 3]
            if near:
                gaps.append((min(near), "the arc sets (stair, fixtures)"))
        if not gaps:
            continue
        ds = sorted(g[0] for g in gaps)
        typical = ds[len(ds) // 2]                       # the median: one moved fixture does not move the level
        if typical > STACK_TOL_M:
            sev = "critical" if typical > STACK_CRITICAL_M else "major"
            axis_off = [g for g in gaps if g[1].startswith("axis") and g[0] > STACK_TOL_M]
            lines = [g for g in gaps if g[1].startswith("the stair lines")]
            out.append(_finding("RC2", sev, lid, f"{lid} does not stack on {reference}: its anchors are {typical:.2f} m "
                                f"off (median of {len(gaps)}: {len(axis_off)} axes, "
                                f"{sum(1 for g in gaps if g[1].startswith('the arc sets'))} arc sets"
                                + (f", {lines[0][1]} {lines[0][0]:.2f} m" if lines else "") + ")",
                                offset_m=round(typical, 3)))
    return out


# ------------------------------------------------------------------------------------------------- areas (RC3)
def _runs(texts) -> list:
    """The page's texts as generic ``TextRun``s (a test's plain objects too)."""
    from wenart.ingest.generic.model import TextRun

    out = []
    for k, t in enumerate(texts):
        if isinstance(t, TextRun):
            out.append(t)
        elif getattr(t, "text", None) and getattr(t, "box", None):
            b = tuple(t.box)
            out.append(TextRun(id=str(getattr(t, "id", k)), text=str(t.text), box=b,
                               height=float(getattr(t, "height", None) or (b[3] - b[1]) or 1e-3),
                               rotation_deg=float(getattr(t, "rotation_deg", 0.0) or 0.0)))
    return out


def area_findings(page, tf, rooms: list, level: str) -> list:
    """RC3: the printed areas of the labelled spaces in a model room against its area. 2 Nov 2026 (real03): the areas
    are read with their labels (``labels.merge_label_blocks``) and summed per room: an open-plan room that joins two
    labelled spaces (``YAŞAMA 16.68`` + ``GİRİŞ HOLÜ 2.16`` + ``HOL 3.85``) matches their sum; area-summary notes
    (``Net Alan = 54.20 m2``) are no space. A room of several labelled spaces where one has no printed area cannot be
    summed: a minor finding names them. An area text with no name above it counts for the room it stands in."""
    from shapely.geometry import Point, Polygon

    from wenart.ingest.generic import labels as LB

    polys = [(r, Polygon(r["polygon"])) for r in rooms if r.get("polygon") and len(r["polygon"]) >= 3]
    runs = _runs(page.texts)
    try:
        blocks = LB.merge_label_blocks(runs)
    except Exception:  # noqa: BLE001 - texts the label reader cannot take: the loose area texts only
        blocks = []
    in_block = {id(r) for b in blocks for r in b.runs}
    spaces = [(b.name, b.area_m2, b.anchor) for b in blocks if not b.exterior]
    for t in runs:
        m = AREA_RE.search(t.text)
        if m and id(t) not in in_block and not LB.is_annotation(t.text):
            spaces.append((None, float(m.group(1).replace(",", ".")), ((t.box[0] + t.box[2]) / 2.0,
                                                                        (t.box[1] + t.box[3]) / 2.0)))
    per_room: dict = {}
    for name, area, anchor in spaces:
        p = _apply(tf, anchor)
        room = next((r for r, poly in polys if poly.contains(Point(p))), None)
        if room is not None:
            per_room.setdefault(room["id"], (room, []))[1].append((name, area, p))
    out = []
    for rid, (room, items) in per_room.items():
        named = [(n, a) for n, a, _ in items if n]
        with_area = [(n, a, p) for n, a, p in items if a]
        if not with_area:
            continue
        model = float(room.get("area_computed") or Polygon(room["polygon"]).area)
        label = room.get("label") or rid
        if len(named) > 1 and any(a is None for _, a in named):
            out.append(_finding("RC3", "minor", level, f"{label} ({rid}) joins {len(named)} labelled spaces ("
                                + ", ".join(f"{n} {a:.2f} m2" if a else f"{n} (no area)" for n, a in named)
                                + f"): the model has {model:.1f} m2", room_id=rid, model_m2=round(model, 2),
                                spaces=[n for n, _ in named]))
            continue
        drawn = sum(a for _, a, _ in with_area)
        if abs(model - drawn) > max(AREA_TOL_SHARE * drawn, AREA_TOL_M2):
            parts = " + ".join(f"{n or 'area'} {a:.2f}" for n, a, _ in with_area)
            at = with_area[0][2]
            out.append(_finding("RC3", "major", level, f"{label} ({rid}): the drawing says "
                                + (f"{parts} = {drawn:.2f}" if len(with_area) > 1 else f"{drawn:.2f}")
                                + f" m2, the model has {model:.1f} m2", room_id=rid, drawn_m2=round(drawn, 2),
                                model_m2=round(model, 2), at=[round(at[0], 2), round(at[1], 2)],
                                spaces=[n for n, _, _ in with_area]))
    return out


# ------------------------------------------------------------------------------------------------- walls (RC4, RC5)
def model_wall_layers(walls: list) -> set:
    """The layers the reading took a level's walls from (their evidence), upper case."""
    out = set()
    for w in walls:
        for ev in w.get("evidence") or []:
            if isinstance(ev, dict) and ev.get("layer"):
                out.add(str(ev["layer"]).upper())
    return out


def drawn_wall_segments(page, tf, layers: set = frozenset()) -> list:
    """The straight strokes (building metres) of the layers whose name means wall, plaster or column and of the
    layers the reading took the walls from (``layers``, upper case: real02's face-line layer has no such name), the
    axis lines left out."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import layer_names as LN

    axis = AX.axis_line_ids(page.strokes, page.texts)
    out = []
    for st in page.strokes:
        layer = getattr(st, "layer", None)
        if st.id in axis or getattr(st, "arc", None) or not (LN.draws_walls(layer) or str(layer or "").upper() in layers):
            continue
        pts = [_apply(tf, p) for p in st.pts] + ([_apply(tf, st.pts[0])] if st.closed else [])
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) >= SEGMENT_MIN_M:
                out.append((a, b))
    return out


PAIR_GAP_M = (0.05, 0.60)     # a wall face has a parallel partner this far away (the other face)
PAIR_OVERLAP_M = 0.3


def paired(segs: list) -> list:
    """The segments with a parallel partner ``PAIR_GAP_M`` away, overlapping it by ``PAIR_OVERLAP_M``: wall faces; a
    lone line (a spiral stair's tread, a hatch edge, a leader) is no wall face (pure)."""
    from shapely.geometry import LineString
    from shapely.strtree import STRtree

    if not segs:
        return []
    lines = [LineString(s) for s in segs]
    tree = STRtree(lines)
    keep = []
    for i, (a, b) in enumerate(segs):
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for j in tree.query(lines[i].buffer(PAIR_GAP_M[1])):
            if j == i:
                continue
            c, d = segs[j]
            L2 = math.dist(c, d)
            vx, vy = (d[0] - c[0]) / L2, (d[1] - c[1]) / L2
            if abs(ux * vy - uy * vx) > 0.02:             # not parallel (about 1 degree)
                continue
            gap = abs((c[0] - a[0]) * uy - (c[1] - a[1]) * ux)
            if not (PAIR_GAP_M[0] <= gap <= PAIR_GAP_M[1]):
                continue
            s0, s1 = sorted(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy))
            if min(L, s1) - max(0.0, s0) >= PAIR_OVERLAP_M:
                keep.append((a, b))
                break
    return keep


def wall_findings(segs: list, walls: list, level: str, built: list = ()) -> list:
    """RC4 on the paired drawn faces (``paired``), RC5 on every drawn wall line (one face is enough)."""
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union

    if not segs:
        return []
    every = unary_union([LineString([a, b]) for a, b in segs])
    segs = paired(segs)
    if not segs:
        segs = []
    out = []
    model = [w for w in walls if w.get("start") and w.get("end")]
    bands = unary_union([LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
        float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2) for w in model] + list(built)) \
        if model or built else None
    drawn = unary_union([LineString([a, b]) for a, b in segs]) if segs else LineString()
    missing = drawn.difference(bands) if bands is not None else drawn
    pieces = [g for g in getattr(missing, "geoms", [missing]) if g.length >= MISSING_PIECE_M]   # no jamb scraps
    total = sum(g.length for g in pieces)
    if total > MISSING_MAJOR_M:
        big = sorted(pieces, key=lambda g: -g.length)
        out.append(_finding("RC4", "major", level, f"{total:.1f} m of drawn wall face the model does not build "
                            f"({len(big)} piece(s) of {MISSING_PIECE_M:g} m or more)", missing_m=round(total, 1),
                            pieces=[[[round(c, 2) for c in g.coords[0]], [round(c, 2) for c in g.coords[-1]]]
                                    for g in big[:20]]))
    for w in model:
        line = LineString([tuple(w["start"]), tuple(w["end"])])
        if line.length < 0.5:
            continue
        band = every.intersection(line.buffer(float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2))
        covered = 0.0
        for g in getattr(band, "geoms", [band]):
            if g.length > 0:
                proj = [line.project(Point(c)) for c in g.coords]
                covered += max(proj) - min(proj)
        share = min(1.0, covered / line.length)
        if share < DRAWN_SHARE_MIN:
            inferred = bool(w.get("inferred"))
            out.append(_finding("RC5", "minor" if inferred else "major", level,
                                f"wall {w.get('id')} ({line.length:.2f} m) lies on drawn wall lines for "
                                f"{share:.0%} of its length" + (" (an inferred wall)" if inferred else ""),
                                wall_id=w.get("id"), share=round(share, 2), inferred=inferred))
    return out


def built_elsewhere(building: dict, level: str) -> list:
    """Shapes (building metres) where drawn wall faces are built as something else than a wall of the building: the
    site's boundary walls of the level (a balcony's parapet), its outdoor spaces (balconies, terraces), its stairs."""
    from shapely.geometry import LineString, Polygon

    out = []
    site = building.get("site") or {}
    for w in site.get("boundary_walls") or []:
        if w.get("level_id") == level and w.get("start") and w.get("end"):
            out.append(LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
                float(w.get("thickness") or 0.2) / 2.0 + WALL_NEAR_M, cap_style=2))
    for sp in site.get("outdoor_spaces") or []:
        if sp.get("level_id") == level and sp.get("polygon") and len(sp["polygon"]) >= 3:
            out.append(Polygon(sp["polygon"]).buffer(WALL_NEAR_M + 0.3, join_style=2))
    for f in building.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("level_id") == level and f.get("type") == "stair" and fp.get("center"):
            cx, cy = fp["center"][:2]
            w, d = fp["size"][:2]
            r = math.radians(float(fp.get("rotation_deg") or 0.0))
            pts = [(cx + sx * w / 2 * math.cos(r) - sy * d / 2 * math.sin(r),
                    cy + sx * w / 2 * math.sin(r) + sy * d / 2 * math.cos(r)) for sx, sy in ((-1, -1), (1, -1), (1, 1),
                                                                                            (-1, 1))]
            out.append(Polygon(pts).buffer(0.1))
    return out


# ------------------------------------------------------------------------------------------- low confidence (RC7)
def is_closure_wall(wall: dict) -> bool:
    """A wall the outline closure inferred (evidence rule ``CLOSURE_RULE``): drawn in its own colour on the sheets."""
    return any(isinstance(e, dict) and e.get("rule") == CLOSURE_RULE for e in wall.get("evidence") or [])


def low_confidence_findings(building: dict) -> list:
    """RC7 (pure): per level with ``reading_confidence: low`` one major finding with its ``reading_review`` reasons;
    per room label the level left in no closed face (``reading_places``) and per outline-closure wall one minor
    finding with its place (``at``, building metres) and a number ``place`` (1, 2, ... in the levels' order, the
    closure walls of a level before its labels) for the sheets and the user's remarks ("place 7")."""
    out = []
    n = 0
    walls_of: dict = {}
    for w in building.get("walls") or []:
        if is_closure_wall(w):
            walls_of.setdefault(w.get("level_id"), []).append(w)
    for lv in building.get("levels") or []:
        lid = lv["id"]
        reasons = list(lv.get("reading_review") or [])
        if lv.get("reading_confidence") == CONFIDENCE_LOW:
            out.append(_finding("RC7", "major", lid, f"{lid} {lv.get('label') or ''}: built with low reading "
                                f"confidence (failed_levels build_marked): " + ("; ".join(reasons) or "no reason "
                                                                                                      "recorded"),
                                reasons=reasons, region=lv.get("region_id")))
        for w in walls_of.get(lid) or []:
            ev = next((e for e in w.get("evidence") or [] if isinstance(e, dict) and e.get("rule") == CLOSURE_RULE),
                      {})
            (x0, y0), (x1, y1) = w["start"], w["end"]
            n += 1
            out.append(_finding("RC7", "minor", lid, f"place {n}: wall {w.get('id')} ({math.dist(w['start'], w['end']):.2f} m)"
                                f" inferred by the outline closure at confidence {ev.get('confidence', 0.3):g}: "
                                f"{ev.get('note') or ev.get('reason') or 'the outer ring did not close'}",
                                place=n, wall_id=w.get("id"), at=[round((x0 + x1) / 2.0, 2), round((y0 + y1) / 2.0, 2)],
                                confidence=ev.get("confidence")))
        for p in lv.get("reading_places") or []:
            if not p.get("at"):
                continue
            n += 1
            out.append(_finding("RC7", "minor", lid, f"place {n}: room label '{p.get('text') or '?'}' at "
                                f"({p['at'][0]:.2f}, {p['at'][1]:.2f}) m in no closed face: "
                                f"{p.get('note') or 'the walls around that room do not close'}",
                                place=n, at=[round(float(p["at"][0]), 2), round(float(p["at"][1]), 2)],
                                kind=p.get("kind"), text=p.get("text")))
    return out


# ------------------------------------------------------------------------------------------------------- the check
def check(out_dir, reference: Optional[str] = None) -> dict:
    """The findings of a pipeline output (the module docstring)."""
    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sheets_path = out_dir / "sheets.json"
    sheets = json.loads(sheets_path.read_text(encoding="utf-8")) if sheets_path.is_file() else {}
    findings = low_confidence_findings(building)                   # RC7 first (the module docstring)
    for lo in building.get("levels_left_out") or []:
        findings.append(_finding("RC1", "critical", f"order {lo.get('order')}", f"level {lo.get('label')} left out "
                                 f"of the model: {lo.get('reason')}", region=lo.get("region_id")))
    carried = [r for lv in building.get("levels") or [] for r in lv.get("reading_review") or []]
    # 5 Nov 2026 (review): the per-label "lies outside the building" warnings of a level marked for those labels are
    # RC7's places too (the quoted names of the level's reasons)
    carried_names = {n for r in carried for n in re.findall(r"'([^']+)'", r)}
    for w in building.get("warnings") or []:
        if "lies outside the building" in w or "outer walls do not close" in w:
            if any(r in w for r in carried):
                continue                                # 4 Nov 2026: a reason a low-confidence level carries is RC7's
            if "lies outside the building" in w and any(f"'{n}'" in w for n in carried_names):
                continue
            findings.append(_finding("RC6", "major", None, w[:300]))
    # 3 Nov 2026 (real10 structure run 20261103-073227-full built nothing: sheets.json failed its schema on the new
    # registration methods, and a pod's sheets stage stops a project whose sheets need review): the sheets' own
    # review reasons are critical
    for n in sheets.get("needs_review") or []:
        reason = n.get("reason") if isinstance(n, dict) else str(n)
        findings.append(_finding("RC6", "critical", None, f"the sheets need review (a pod's sheets stage stops the "
                                                          f"project): {str(reason)[:240]}", region=(n or {}).get(
                                                              "region") if isinstance(n, dict) else None))
    for w in sheets.get("warnings") or []:
        if str(w).startswith("schema: "):
            findings.append(_finding("RC6", "major", None, f"sheets.json: {str(w)[:280]}"))
    pages = level_pages(building)
    anchors, checked, notes = {}, [], []
    conv = {"layers": {}, "levels": {}}
    for lid, pg in pages.items():
        page = read_level_page(out_dir, sheets, pg)
        if page is None:
            notes.append(f"{lid}: no CAD source to check against (a PDF or a raster page)")
            continue
        tf = pg["tf"]
        checked.append(lid)
        anchors[lid] = {"axes": page_axes(page, tf), "stairs": page_stairs(page, tf),
                        "stair_lines": page_stair_lines(page, tf)}
        _note_conventions(conv, lid, page, anchors[lid], sheets, pg, building)
        rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid]
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
        findings += area_findings(page, tf, rooms, lid)
        segs = drawn_wall_segments(page, tf, model_wall_layers(walls))
        if segs:
            findings += wall_findings(segs, walls, lid, built_elsewhere(building, lid))
        else:
            notes.append(f"{lid}: no layer named wall, plaster or column: walls not compared")
    ref = reference or next((lid for lid in ("L0", "L1") if lid in anchors), next(iter(anchors), None))
    if ref:
        findings += stacking(anchors, ref, {lv["id"]: lv.get("order") for lv in building.get("levels") or []})
    # 5 Nov 2026 (Milestone 14 R5): the cross-document checks RC8-RC12 (elevations against the plans per floor,
    # sections against the levels, the site plan against the model, size tags against the openings read, twins and
    # typical floors against each other) join the reading check as ADVISORY findings: reported and counted apart,
    # never part of the verdict until the trust ledger (R9) shows they earned it; their ``info`` severity is a note.
    # A failure of the module is one info finding, never a stop of the reading check.
    try:
        from wenart.reading_check import crossdoc as CD
        cross = CD.findings(out_dir)
    except Exception as exc:  # noqa: BLE001 - an advisory check never stops the reading check
        cross = [{"check": "RC8", "name": "cross-document checks", "severity": "info", "level_id": None,
                  "message": f"the cross-document checks did not run: {type(exc).__name__}: {str(exc)[:200]}"}]
    for f in cross:
        f["advisory"] = True
    findings += cross
    # 6 Nov 2026 (Milestone 14 R6; user, 4 Nov 2026: "some AI or something else to give the feedbacks by itself instead
    # of me at some point"): the architectural-sense checks RC14 (a room type implausible for its area, a small room's
    # label naming a larger face, the sheet frame read as walls, unread walls, levels, rooms and flats that cannot be
    # reached, notation in room names) join as ADVISORY findings like RC8-RC12: counted under counts["advisory"],
    # never in the verdict; a rule below its judged precision (models/sense_trust.json) writes info. A failure of the
    # module is one info finding.
    try:
        from wenart.reading_check import sense as SN
        sense = SN.findings(out_dir)
    except Exception as exc:  # noqa: BLE001 - an advisory check never stops the reading check
        sense = [{"check": "RC14", "name": "architectural sense", "rule": None, "severity": "info", "level_id": None,
                  "message": f"the architectural-sense checks did not run: {type(exc).__name__}: {str(exc)[:200]}",
                  "place": None, "element_ids": []}]
    for f in sense:
        f["advisory"] = True
    findings += sense
    advisory = cross + sense
    counts = {s: sum(1 for f in findings if f["severity"] == s and not f.get("advisory"))
              for s in ("critical", "major", "minor")}
    counts["advisory"] = {s: sum(1 for f in advisory if f["severity"] == s) for s in ("major", "minor", "info")}
    return {"project": (building.get("project") or {}).get("id"), "levels_checked": checked, "reference": ref,
            "conventions": conv,
            "findings": findings, "counts": counts, "notes": notes,
            "verdict": "ready" if not counts["critical"] else "fix before a pod run",
            "levels": [lv["id"] for lv in building.get("levels") or []],
            "levels_left_out": [lo.get("label") for lo in building.get("levels_left_out") or []]}


def _note_conventions(conv: dict, lid: str, page, anchors: dict, sheets: dict, pg: dict, building: dict) -> None:
    """What the reading understood about a level's drawing (2 Nov 2026, the conventions record): every layer with its
    meaning by name (``generic.layer_names``), its linetypes and strokes, the axis lines; the grid's axes, the core's
    arc sets, how the level was placed (``sheets.json`` registration) and whether it lies fully below ground."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import layer_names as LN

    axis = AX.axis_line_ids(page.strokes, page.texts)
    for st in page.strokes:
        name = getattr(st, "layer", None) or "0"
        row = conv["layers"].setdefault(name, {"role": LN.layer_role(name), "strokes": 0, "linetypes": [],
                                               "axis_lines": 0, "levels": []})
        row["strokes"] += 1
        lt = getattr(st, "linetype", None)
        if lt and lt not in row["linetypes"]:
            row["linetypes"].append(lt)
        if st.id in axis:
            row["axis_lines"] += 1
        if lid not in row["levels"]:
            row["levels"].append(lid)
    reg = next((r for r in sheets.get("regions") or [] if r.get("id") == pg.get("region")), {}) or {}
    under = any("fully below ground" in w and f"({lid})" in w for w in building.get("warnings") or [])
    conv["levels"][lid] = {"region": pg.get("region"), "axes": len(anchors.get("axes") or {}),
                           "arc_sets": len(anchors.get("stairs") or []), "axis_lines": len(axis),
                           "placed_by": (reg.get("registration") or {}).get("method"),
                           "placement_note": (reg.get("registration") or {}).get("note"), "underground": under}


def write(out_dir, result: dict) -> Path:
    """``reading_check/reading_check.json`` and ``.md`` in the pipeline output."""
    d = Path(out_dir) / "reading_check"
    d.mkdir(parents=True, exist_ok=True)
    (d / "reading_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    adv = (result.get("counts") or {}).get("advisory") or {}
    adv_text = (f" Cross-document checks RC8-RC12 and architectural-sense checks RC14, advisory: {adv.get('major', 0)} "
                f"major, {adv.get('minor', 0)} minor, {adv.get('info', 0)} info (not in the verdict)." if adv else "")
    lines = [f"# Reading check: {result.get('project')}", "",
             f"Verdict: **{result['verdict']}** ({result['counts']['critical']} critical, {result['counts']['major']} "
             f"major, {result['counts']['minor']} minor). Levels checked against the drawing: "
             f"{', '.join(result['levels_checked']) or 'none'}; reference {result.get('reference')}.{adv_text}", "",
             "| check | severity | level | finding |", "|---|---|---|---|"]
    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    # 4 Nov 2026: RC7's low-confidence places first (the user checks them on the sheets), then by severity
    for f in sorted(result["findings"], key=lambda f: (0 if f["check"] == "RC7" else 1, order.get(f["severity"], 3),
                                                       1 if f.get("advisory") else 0, f["check"],
                                                       str(f.get("level_id")), str(f.get("place") or 0))):
        lines.append(f"| {f['check']} {f['name']}{' (advisory)' if f.get('advisory') else ''} | {f['severity']} | "
                     f"{f.get('level_id') or '-'} | {f['message'].replace('|', '/')} |")
    if result.get("notes"):
        lines += ["", "Notes:"] + [f"- {n}" for n in result["notes"]]
    conv = result.get("conventions") or {}
    if conv.get("levels"):
        lines += ["", "## What the reading understood about the drawing", "",
                  "| level | placed by | axes | arc sets | axis lines left out | fully below ground |",
                  "|---|---|---|---|---|---|"]
        for lid, c in conv["levels"].items():
            lines.append(f"| {lid} | {c.get('placed_by') or '-'} | {c['axes']} | {c['arc_sets']} | {c['axis_lines']} | "
                         f"{'yes' if c['underground'] else 'no'} |")
        lines += ["", "| layer | meaning (by its name) | linetypes | strokes | axis lines |", "|---|---|---|---|---|"]
        for name, c in sorted(conv["layers"].items(), key=lambda kv: -kv[1]["strokes"])[:40]:
            lines.append(f"| {name} | {c['role'] or '-'} | {', '.join(c['linetypes']) or '-'} | {c['strokes']} | "
                         f"{c['axis_lines']} |")
        (d / "conventions.json").write_text(json.dumps(conv, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "reading_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d
