"""Vector PDF page -> ``LevelExtraction`` by geometry (docs/milestone2.md §2).

pdfplumber (pdfminer) gives us path objects (rects, lines, curves) and
characters, but no block names or layers, so elements are recognised by how
they are drawn:

- Walls: closed 4-corner paths with the wall line width (0.5 pt).
- Furniture: closed 4-corner paths with the furniture line width (0.25 pt)
  plus the short front-marker line inside; type stays ``unknown`` and the
  piece ``unverified`` because a PDF carries no block name (footprint clear,
  type unclear). The marker gives the front side and hence the rotation.
- Doors: the only curves on a plan are door swing arcs; the leaf is the line
  that ends where the arc ends (the hinge is the other leaf end).
- Windows: four opening-width lines forming a thin closed rectangle (two
  parallel lines of the clear width joined by two short end lines).
- Dimensions: number texts (``3,45``) next to a parallel line with 45-degree
  ticks at its ends. The ``ÖLÇEK 1/100`` note gives the scale; the ratios
  printed value / line length cross-check it (a disagreement is a
  ``scale_disagreement`` conflict, the note still wins). Without a note the
  ratios give the scale (``method: dimension_text``) only when at least
  ``MIN_AGREEING_DIMENSIONS`` of them agree, because a dimension text can be
  an override that must not rescale the drawn geometry.

Coordinates: page points, origin bottom-left (pdfminer's user space), which
is what ``truth/pages.json`` uses. Path indices (``path:<n>``) count the
rect/line/curve objects in content-stream order, which pdfminer preserves
when iterating ``page.layout``; char indices (``char:<n>``) index
``page.chars`` in the same order.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pdfplumber
from pdfminer.layout import LTCurve, LTLine, LTRect

from wenart import building as B
from wenart import geometry as G
from wenart.ingest.model import (DOOR_SWING_PROBE, METRES_PER_POINT, DimensionItem, FurnitureItem, LevelExtraction,
                                 OpeningItem, TextItem, WallItem, parse_number, parse_scale_text, text_role)

LW_WALL = 0.5
LW_OPENING = 0.35
LW_FURNITURE = 0.25
LW_TOLERANCE = 0.06
POINT_TOLERANCE = 0.5          # points: endpoints "touch" when closer than this
MAX_WINDOW_DEPTH_M = 0.5       # a window symbol is a thin rectangle on the wall
MAX_FURNITURE_INSET_M = 0.08   # the front marker lies within this distance of the front edge
SCALE_AGREEMENT = 0.01         # dimension ratio vs ÖLÇEK text or vs the other ratios (1 %)
MIN_AGREEING_DIMENSIONS = 3    # without a scale note, this many agreeing ratios set the scale
SCALE_NOTE_DISPUTED_CONFIDENCE = 0.5  # note kept although the dimension texts disagree


@dataclass
class PathObj:
    """One drawing path from the page, in content-stream order."""
    index: int
    kind: str                      # rect | line | curve
    pts: list[tuple[float, float]] # page points, origin bottom-left
    linewidth: float
    bezier: bool                   # has curve segments (door arcs)
    used: bool = False

    @property
    def entity(self) -> str:
        return f"path:{self.index}"

    def box(self) -> list[float]:
        return [round(v, 3) for v in G.bbox(self.pts)]

    def corners(self) -> Optional[list[tuple[float, float]]]:
        """Four corners when this path is a closed quadrilateral, else None."""
        pts = list(self.pts)
        if len(pts) == 5 and G.distance(pts[0], pts[-1]) < 1e-6:
            pts = pts[:4]
        return pts if len(pts) == 4 and not self.bezier else None

    def length(self) -> float:
        return G.distance(self.pts[0], self.pts[-1])


@dataclass
class PageObjects:
    paths: list[PathObj]
    texts: list[TextItem]
    width: float
    height: float
    n_chars: int = 0
    n_images: int = 0
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
# Reading the page
# --------------------------------------------------------------------------

def _has_bezier(obj) -> bool:
    path = getattr(obj, "original_path", None)
    if path:
        return any(op[0] == "c" for op in path)
    return isinstance(obj, LTCurve) and not isinstance(obj, (LTLine, LTRect))


def read_page_objects(page) -> PageObjects:
    """Paths (stream order) and merged text runs of one pdfplumber page."""
    paths: list[PathObj] = []
    index = 0
    for obj in page.layout:
        if isinstance(obj, (LTRect, LTLine, LTCurve)):
            kind = "rect" if isinstance(obj, LTRect) else "line" if isinstance(obj, LTLine) else "curve"
            pts = [(float(x), float(y)) for x, y in obj.pts]
            paths.append(PathObj(index=index, kind=kind, pts=pts, linewidth=float(obj.linewidth or 0.0),
                                 bezier=_has_bezier(obj)))
            index += 1
    texts = merge_chars(page.chars)
    return PageObjects(paths=paths, texts=texts, width=float(page.width), height=float(page.height),
                       n_chars=len(page.chars), n_images=len(page.images))


def merge_chars(chars: list[dict]) -> list[TextItem]:
    """Group consecutive chars into text runs: same rotation and each char
    starting where the previous one ends (within a fraction of the size)."""
    runs: list[TextItem] = []
    current: Optional[dict] = None
    for i, ch in enumerate(chars):
        a, b, _, _, e, f = ch["matrix"]
        norm = math.hypot(a, b) or 1.0
        direction = (a / norm, b / norm)
        rotation = G.normalise_angle(math.degrees(math.atan2(b, a)))
        size = max(float(ch.get("width", 0.0)), float(ch.get("height", 0.0)), float(ch.get("size", 0.0)))
        start = (float(e), float(f))
        box = [float(ch["x0"]), float(ch["y0"]), float(ch["x1"]), float(ch["y1"])]
        joins = False
        if current is not None and G.angle_difference_deg(rotation, current["rotation"]) < 1.0:
            expected = (current["next"][0], current["next"][1])
            joins = G.distance(start, expected) < 0.35 * max(size, current["size"])
        if not joins:
            if current is not None:
                runs.append(_finish_run(current))
            current = {"first": i, "chars": [], "rotation": rotation, "size": size, "start": start,
                       "boxes": [], "dir": direction}
        current["chars"].append(ch["text"])
        current["boxes"].append(box)
        current["size"] = max(current["size"], size)
        adv = float(ch.get("adv", 0.0))
        current["next"] = (start[0] + direction[0] * adv, start[1] + direction[1] * adv)
    if current is not None:
        runs.append(_finish_run(current))
    return [r for r in runs if r.text.strip()]


def _finish_run(run: dict) -> TextItem:
    text = "".join(run["chars"])
    xs0 = [b[0] for b in run["boxes"]]
    ys0 = [b[1] for b in run["boxes"]]
    xs1 = [b[2] for b in run["boxes"]]
    ys1 = [b[3] for b in run["boxes"]]
    box = [round(min(xs0), 3), round(min(ys0), 3), round(max(xs1), 3), round(max(ys1), 3)]
    stripped = text.strip()
    return TextItem(text=stripped, start=run["start"], box=box, rotation_deg=run["rotation"],
                    entity=f"char:{run['first']}", height=run["size"], role=text_role(stripped))


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def _lw_is(obj: PathObj, width: float) -> bool:
    return abs(obj.linewidth - width) <= LW_TOLERANCE


def extract_pdf_page(path: str | Path, page_number: int, level_id: str,
                     file_rel: Optional[str] = None) -> LevelExtraction:
    """Read page ``page_number`` (1-based) of a vector PDF into a ``LevelExtraction``."""
    path = Path(path)
    file_rel = file_rel or path.name
    with pdfplumber.open(str(path)) as pdf:
        page = pdf.pages[page_number - 1]
        objects = read_page_objects(page)
    return extract_from_objects(objects, page_number, level_id, file_rel)


def extract_from_objects(objects: PageObjects, page_number: int, level_id: str, file_rel: str) -> LevelExtraction:
    ex = LevelExtraction(file=file_rel, page=page_number, level_id=level_id, units="pt",
                         page_size=[objects.width, objects.height])
    ex.texts = objects.texts

    def ev(entity: str, text: Optional[str] = None) -> dict:
        return B.evidence(file_rel, "vector", 1.0, page=page_number, entity=entity, text=text)

    for item in ex.texts:
        item.evidence = ev(item.entity, item.text)
        if item.role == "title":
            if ex.title is None or item.height > ex.title.height:
                ex.title = item
        elif item.role == "scale":
            ex.scale_text = item
        elif item.role == "room_label":
            ex.labels.append(item)

    paths = objects.paths
    wall_paths = [p for p in paths if _lw_is(p, LW_WALL) and p.corners()]
    furniture_rects = [p for p in paths if _lw_is(p, LW_FURNITURE) and p.corners()]
    furniture_lines = [p for p in paths if _lw_is(p, LW_FURNITURE) and p.kind == "line"]
    thin_lines = [p for p in paths if _lw_is(p, LW_OPENING) and p.kind == "line"]
    arcs = [p for p in paths if _lw_is(p, LW_OPENING) and p.bezier]

    # Dimensions in page points first: they give the scale.
    raw_dims = _find_dimensions(ex.texts, thin_lines)
    ex.scale = _resolve_scale(raw_dims, ex.scale_text, ex, file_rel, page_number)
    if ex.scale is None:
        ex.warnings.append(f"{file_rel} p{page_number}: no scale source (no ÖLÇEK text, no dimension texts)")
        return ex
    mpu = ex.scale["metres_per_unit"]

    if wall_paths:
        box = G.bbox([c for p in wall_paths for c in p.corners()])
        origin = (box[0], box[1])
    else:
        origin = (0.0, 0.0)
        ex.warnings.append(f"{file_rel} p{page_number}: no wall rectangles ({LW_WALL} pt closed paths)")
    ex.transform_to_building = [mpu, 0.0, -mpu * origin[0] + 0.0, 0.0, mpu, -mpu * origin[1] + 0.0]

    def tb(p) -> tuple[float, float]:
        # 0.1 mm is far below the PDF coordinate precision (about 4 um at 1:100).
        return G.snap_point(G.apply_affine(ex.transform_to_building, p), 4)

    for p in wall_paths:
        start, end, thickness = G.rectangle_to_centerline([tb(c) for c in p.corners()])
        p.used = True
        ex.walls.append(WallItem(start=start, end=end, thickness=G.snap(thickness, 6), box=p.box(),
                                 entity=p.entity, evidence=ev(p.entity)))

    for arc in arcs:
        item = _door_from_arc(arc, thin_lines, tb, ev)
        if item is None:
            ex.warnings.append(f"{file_rel} p{page_number}: curve {arc.entity} has no door leaf; ignored")
        else:
            ex.openings.append(item)

    for item in _windows_from_lines(thin_lines, tb, ev, mpu, ex.walls):
        ex.openings.append(item)

    for rect in furniture_rects:
        ex.furniture.append(_furniture_from_rect(rect, furniture_lines, tb, ev, mpu))

    for raw in raw_dims:
        line, text, ticks = raw["line"], raw["text"], raw["ticks"]
        p1, p2 = tb(line.pts[0]), tb(line.pts[-1])
        if p2 < p1:
            p1, p2 = p2, p1
        measured = G.snap(G.distance(p1, p2), 6)
        ex.dimensions.append(DimensionItem(p1=p1, p2=p2, measured=measured, printed=text.text,
                                           printed_value=parse_number(text.text), box=text.box, entity=line.entity,
                                           evidence=ev(text.entity, text.text), tick_count=ticks))
    return ex


# --------------------------------------------------------------------------
# Dimensions and scale
# --------------------------------------------------------------------------

def _find_dimensions(texts: list[TextItem], lines: list[PathObj]) -> list[dict]:
    """Number texts with their dimension line: the closest parallel line whose
    span covers the text centre, within two text heights. Returns
    ``[{"text", "line", "ticks", "length_pt"}]``."""
    found = []
    for text in texts:
        if text.role != "dimension":
            continue
        center = G.box_center(text.box)
        best = None
        for line in lines:
            if line.used or line.length() < 1e-6:
                continue
            angle = G.segment_angle_deg(line.pts[0], line.pts[-1])
            diff = G.angle_difference_deg(angle, text.rotation_deg)
            if min(diff, 180.0 - diff) > 1.0:
                continue
            # Perpendicular distance and projection onto the line.
            a, b = line.pts[0], line.pts[-1]
            dist = G.point_segment_distance(center, a, b)
            if dist > 2.5 * text.height + 2.0:
                continue
            ux, uy = (b[0] - a[0]) / line.length(), (b[1] - a[1]) / line.length()
            t = (center[0] - a[0]) * ux + (center[1] - a[1]) * uy
            if t < -1.0 or t > line.length() + 1.0:
                continue
            if best is None or dist < best[0]:
                best = (dist, line)
        if best is None:
            continue
        line = best[1]
        line.used = True
        ticks = 0
        for end in (line.pts[0], line.pts[-1]):
            for tick in lines:
                if tick is line or tick.used or tick.length() > 12.0:
                    continue
                mid = G.segment_midpoint(tick.pts[0], tick.pts[-1])
                if G.distance(mid, end) < POINT_TOLERANCE:
                    ticks += 1
                    break
        found.append({"text": text, "line": line, "ticks": ticks, "length_pt": line.length()})
    return found


def _resolve_scale(raw_dims: list[dict], scale_text: Optional[TextItem], ex: LevelExtraction,
                   file_rel: str, page_number: int) -> Optional[dict]:
    """Scale block for the page: the ÖLÇEK note first, dimension texts as cross-check or fallback.

    A dimension ratio is printed text divided by drawn length, so a text override moves
    every scale derived from it, and the overridden dimension would then measure exactly
    its printed value and hide its own conflict. Hence:

    - With a note, the note is the scale. Ratios whose median agrees with it (within
      ``SCALE_AGREEMENT``) confirm it (confidence 1.0). A disagreeing set lowers the
      confidence and raises a ``scale_disagreement`` conflict naming the odd texts; the
      pipeline then checks every dimension text against its measured length.
    - Without a note, the median of the ratios is the scale only when at least
      ``MIN_AGREEING_DIMENSIONS`` ratios agree with it and they are the majority. A lone
      or split set gives no scale source (``needs_review`` downstream).
    """
    where = f"{file_rel} p{page_number}"
    ratios: list[tuple[TextItem, float]] = []   # (dimension text, metres per point it implies)
    for raw in raw_dims:
        value = parse_number(raw["text"].text)
        if value and raw["length_pt"] > 0:
            ratios.append((raw["text"], value / raw["length_pt"]))
    from_text = None
    if scale_text is not None:
        denominator = parse_scale_text(scale_text.text)
        if denominator:
            from_text = denominator * METRES_PER_POINT

    def off_pct(ratio: float, reference: float) -> float:
        return (ratio - reference) / reference * 100.0

    def disagreeing(reference: float) -> list[tuple[TextItem, float]]:
        return [(t, r) for t, r in ratios if abs(off_pct(r, reference)) > SCALE_AGREEMENT * 100.0]

    def describe(items, reference: float) -> str:
        return ", ".join(f"'{t.text}' ({off_pct(r, reference):+.1f}%)" for t, r in items)

    if from_text is not None:
        def note_scale(confidence: float) -> dict:
            return {"metres_per_unit": from_text, "method": "pdf_scale_text", "confidence": confidence,
                    "evidence": B.evidence(file_rel, "vector", confidence, page=page_number, entity=scale_text.entity,
                                           text=scale_text.text)}
        if not ratios:
            return note_scale(0.9)
        median = statistics.median(r for _, r in ratios)
        if abs(off_pct(median, from_text)) <= SCALE_AGREEMENT * 100.0:
            # The dimension texts confirm the note; keep its exact value.
            return note_scale(1.0)
        ex.conflicts.append({
            "kind": "scale_disagreement", "element_ids": [],
            "description": f"{where}: '{scale_text.text}' gives {from_text:.6f} m/pt but the median of {len(ratios)} "
                           f"dimension texts gives {median:.6f} m/pt ({off_pct(median, from_text):+.1f}%); "
                           f"disagreeing texts: {describe(disagreeing(from_text), from_text)}",
            "resolution": "scale note kept (drawn standard scale); every dimension text is checked against "
                          "the length measured at that scale"})
        return note_scale(SCALE_NOTE_DISPUTED_CONFIDENCE)

    if not ratios:
        return None
    median = statistics.median(r for _, r in ratios)
    odd = disagreeing(median)
    agreeing = [(t, r) for t, r in ratios if abs(off_pct(r, median)) <= SCALE_AGREEMENT * 100.0]
    if len(agreeing) < MIN_AGREEING_DIMENSIONS or len(agreeing) * 2 <= len(ratios):
        ex.warnings.append(f"{where}: no scale note and only {len(agreeing)} of {len(ratios)} dimension texts agree "
                           f"on a scale (need {MIN_AGREEING_DIMENSIONS})"
                           + (f"; disagreeing: {describe(odd, median)}" if odd else ""))
        return None
    confidence = 0.9 if not odd else 0.7
    if odd:
        ex.warnings.append(f"{where}: scale from {len(agreeing)} of {len(ratios)} agreeing dimension texts; "
                           f"disagreeing: {describe(odd, median)}")
    best = agreeing[0][0]
    return {"metres_per_unit": median, "method": "dimension_text", "confidence": confidence,
            "evidence": B.evidence(file_rel, "vector", confidence, page=page_number, entity=best.entity, text=best.text)}


# --------------------------------------------------------------------------
# Openings and furniture
# --------------------------------------------------------------------------

def _door_from_arc(arc: PathObj, lines: list[PathObj], tb, ev) -> Optional[OpeningItem]:
    """Door = swing arc + leaf line ending at the arc end; hinge = other leaf end."""
    arc_start, arc_end = arc.pts[0], arc.pts[-1]
    for leaf in lines:
        if leaf.used:
            continue
        for tip, hinge in ((leaf.pts[0], leaf.pts[-1]), (leaf.pts[-1], leaf.pts[0])):
            if G.distance(tip, arc_end) > POINT_TOLERANCE:
                continue
            w_pt = G.distance(hinge, tip)
            if w_pt < 1e-6 or abs(G.distance(hinge, arc_start) - w_pt) > 2 * POINT_TOLERANCE:
                continue
            leaf.used = True
            arc.used = True
            local_x = ((arc_start[0] - hinge[0]) / w_pt, (arc_start[1] - hinge[1]) / w_pt)
            local_y = ((tip[0] - hinge[0]) / w_pt, (tip[1] - hinge[1]) / w_pt)
            rotation = G.normalise_angle(math.degrees(math.atan2(local_x[1], local_x[0])))
            center_pt = (hinge[0] + local_x[0] * w_pt / 2, hinge[1] + local_x[1] * w_pt / 2)
            center = tb(center_pt)
            tip_b = tb(tip)
            hinge_b = tb(hinge)
            width = G.snap(G.distance(hinge_b, tip_b), 4)
            swing = (center[0] + local_y[0] * DOOR_SWING_PROBE, center[1] + local_y[1] * DOOR_SWING_PROBE)
            corners = [hinge, (hinge[0] + local_x[0] * w_pt, hinge[1] + local_x[1] * w_pt),
                       (hinge[0] + (local_x[0] + local_y[0]) * w_pt, hinge[1] + (local_x[1] + local_y[1]) * w_pt), tip]
            first = min(leaf, arc, key=lambda p: p.index)
            return OpeningItem(kind="door", width=width, center=center, rotation_deg=round(rotation, 3),
                               box=[round(v, 3) for v in G.bbox(corners)], entity=first.entity,
                               evidence=ev(first.entity), swing_point=swing, block=None)
    return None


def _windows_from_lines(lines: list[PathObj], tb, ev, mpu: float, walls: list[WallItem]) -> list[OpeningItem]:
    """Thin closed rectangles made of four opening-width lines, centred on a wall."""
    out = []
    max_depth_pt = MAX_WINDOW_DEPTH_M / mpu
    candidates = [l for l in lines if not l.used and l.length() > 1e-6]
    for a in candidates:
        if a.used:
            continue
        la = a.length()
        ang_a = G.segment_angle_deg(a.pts[0], a.pts[-1])
        for b in candidates:
            if b is a or b.used or abs(b.length() - la) > POINT_TOLERANCE:
                continue
            diff = G.angle_difference_deg(ang_a, G.segment_angle_deg(b.pts[0], b.pts[-1]))
            if min(diff, abs(diff - 180.0)) > 0.5:
                continue
            depth = G.point_segment_distance(b.pts[0], a.pts[0], a.pts[-1])
            if depth < POINT_TOLERANCE or depth > max_depth_pt:
                continue
            # Pair the end points and look for the two connecting lines.
            if G.distance(a.pts[0], b.pts[0]) < G.distance(a.pts[0], b.pts[-1]):
                pairs = [(a.pts[0], b.pts[0]), (a.pts[-1], b.pts[-1])]
            else:
                pairs = [(a.pts[0], b.pts[-1]), (a.pts[-1], b.pts[0])]
            ends = []
            for p, q in pairs:
                hit = next((c for c in candidates if c not in (a, b) and not c.used and
                            ((G.distance(c.pts[0], p) < POINT_TOLERANCE and G.distance(c.pts[-1], q) < POINT_TOLERANCE) or
                             (G.distance(c.pts[0], q) < POINT_TOLERANCE and G.distance(c.pts[-1], p) < POINT_TOLERANCE))),
                           None)
                if hit is None:
                    break
                ends.append(hit)
            if len(ends) != 2:
                continue
            corners = [a.pts[0], a.pts[-1], b.pts[-1], b.pts[0]]
            center_pt = (sum(c[0] for c in corners) / 4, sum(c[1] for c in corners) / 4)
            center = tb(center_pt)
            if walls and not _on_a_wall(center, walls):
                continue
            for part in (a, b, *ends):
                part.used = True
            rotation = ang_a % 180.0
            first = min((a, b, *ends), key=lambda p: p.index)
            out.append(OpeningItem(kind="window", width=G.snap(la * mpu, 4), center=center,
                                   rotation_deg=round(rotation, 3), box=[round(v, 3) for v in G.bbox(corners)],
                                   entity=first.entity, evidence=ev(first.entity), block=None))
            break
    out.sort(key=lambda o: int(o.entity.split(":")[1]))
    return out


def _on_a_wall(point, walls: list[WallItem], slack: float = 0.02) -> bool:
    return any(G.point_segment_distance(point, w.start, w.end) <= w.thickness / 2 + slack for w in walls)


def _furniture_from_rect(rect: PathObj, lines: list[PathObj], tb, ev, mpu: float) -> FurnitureItem:
    """Footprint from a furniture rectangle; the front marker line fixes the rotation."""
    corners = rect.corners()
    rect.used = True
    center_pt = (sum(c[0] for c in corners) / 4, sum(c[1] for c in corners) / 4)
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    marker = None
    for line in lines:
        if line.used:
            continue
        if all(G.point_in_polygon(p, corners) for p in (line.pts[0], line.pts[-1])):
            marker = line
            break
    front_deg = None
    rotation = 0.0
    if marker is not None:
        marker.used = True
        m_angle = G.segment_angle_deg(marker.pts[0], marker.pts[-1])
        m_mid = G.segment_midpoint(marker.pts[0], marker.pts[-1])
        best = None
        for a, b in edges:
            e_angle = G.segment_angle_deg(a, b)
            diff = G.angle_difference_deg(m_angle, e_angle)
            if min(diff, abs(diff - 180.0)) > 2.0:
                continue
            dist = G.point_segment_distance(m_mid, a, b)
            if best is None or dist < best[0]:
                best = (dist, a, b)
        if best is not None and best[0] * mpu <= MAX_FURNITURE_INSET_M:
            _, a, b = best
            edge_mid = G.segment_midpoint(a, b)
            # Outward normal of the front edge = direction the piece faces.
            front_deg = G.normalise_angle(math.degrees(math.atan2(edge_mid[1] - center_pt[1], edge_mid[0] - center_pt[0])))
            front_deg = round(front_deg, 3)
            rotation = G.normalise_angle(front_deg - 270.0)
            width_pt = G.distance(a, b)
            depth_pt = G.distance(corners[0], corners[1]) if abs(G.distance(corners[0], corners[1]) - width_pt) > 1e-6 \
                else G.distance(corners[1], corners[2])
            size = (G.snap(width_pt * mpu, 4), G.snap(depth_pt * mpu, 4))
        else:
            size = _axis_size(corners, mpu)
    else:
        size = _axis_size(corners, mpu)
    if front_deg is None:
        rotation = G.normalise_angle(G.segment_angle_deg(corners[0], corners[1]))
    return FurnitureItem(type="unknown", type_raw=None, center=tb(center_pt), size=size, rotation_deg=round(rotation, 3),
                         front_deg=front_deg, box=rect.box(), entity=rect.entity, evidence=ev(rect.entity),
                         status="unverified")


def _axis_size(corners, mpu: float) -> tuple[float, float]:
    """Size along the first edge and the second edge (no front information)."""
    return (G.snap(G.distance(corners[0], corners[1]) * mpu, 4), G.snap(G.distance(corners[1], corners[2]) * mpu, 4))
