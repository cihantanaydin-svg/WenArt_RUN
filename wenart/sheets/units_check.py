"""The unit check of a DXF/DWG before any wall is read (docs/milestone10.md §3.1 item 6; user decision 8 of §9).

What: ``check_units(insunits, regions, file_rel) -> UnitResult``: the drawing unit of a CAD document from what is
drawn, compared with the ``$INSUNITS`` header.

Why: real02's header says millimetres while its geometry is in centimetres (its section's slab lines are 300 units
apart where the level marks read 40.00 and 43.00); read at 1 mm per unit the building was 1 m wide and no wall rule
could fire. A header is used only when what is drawn does not contradict it.

How: five candidate units (mm, cm, m, in, ft) are scored by independent checks; each check decides one unit or
none (``unit: null``: too few samples, or two units fit equally well, e.g. cm and inch for a 15-unit text):

- ``area_labels``: room-area labels (``SALON 46M2``) vs the area they label: the closed outline they sit in alone
  (0.75-1.25 of it) and the sum of a region's labels vs its box (0.35-1.05 of it, when it holds >= 2 labels);
- ``level_marks``: pairs of level marks (``43.00``, ``±0.00``) vs the distance between the levels they point at
  (the apex of the mark triangle under the text), within 15 %;
- ``door_widths``: quarter arcs with a door leaf line from their centre to one end (door swings): radius 0.6-1.2 m;
- ``wall_thickness``: the distance of each long straight stroke to its nearest parallel neighbour (face pairs):
  0.08-0.6 m;
- ``text_height``: the median height of the texts on the drawings: 0.08-0.6 m (only when one unit alone fits);
- ``dimensions``: DIMENSION entities with a printed length vs their measured span, within 15 %.

A check decides the unit with the highest share of passing samples when that share is >= 0.5 and every other unit's
share is lower by >= 0.3. The header is used when no check decides another unit (``dxf_insunits``). When >= 2 checks
agree on another unit and none supports the header, that unit is used (``unit_check``) and ``unit_mismatch`` is
listed. When checks contradict the header without that agreement, the document needs review (``needs_review``). A
header without a unit (``$INSUNITS`` 0) takes the agreed unit of >= 2 checks; otherwise the scale is left to the
dimension texts of the generic core (M7).
"""
from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B
from wenart import units as U
from wenart.sheets import titles as T

UNITS = {"mm": 0.001, "cm": 0.01, "m": 1.0, "in": 0.0254, "ft": 0.3048}
INSUNITS_NAME = {1: "in", 2: "ft", 4: "mm", 5: "cm", 6: "m"}
NAME_INSUNITS = {v: k for k, v in INSUNITS_NAME.items()}
DECIDE_SHARE = 0.5
DECIDE_MARGIN = 0.3
RATIO_TOL = 1.15                    # level marks and dimensions: within 15 % (units differ by >= 2.54 x)
ROOM_AREA = (0.75, 1.25)            # label / outline area of the closed outline a label sits in alone
REGION_AREA = (0.35, 1.05)          # sum of a region's labels / its box area
DOOR_RADIUS_M = (0.6, 1.2)
QUARTER_SPAN_DEG = (80.0, 100.0)
LEAF_TOL = 0.08                     # leaf line ends within 8 % of the radius of the arc centre and an arc end
LEAF_LENGTH = (0.85, 1.15)          # leaf length / radius
WALL_M = (0.08, 0.6)
WALL_STROKE_REL = 0.02              # long strokes: >= 2 % of the region diagonal
WALL_OVERLAP = 0.5
TEXT_HEIGHT_M = (0.08, 0.6)
MIN_SAMPLES = {"area_labels": 1, "level_marks": 1, "door_widths": 3, "wall_thickness": 5, "text_height": 3,
               "dimensions": 2}
MARK_RE = re.compile(r"^\s*(?:KOT\s*)?([±+\-]?)\s*(\d{1,4}[.,]\d{2,3})\s*(?:M)?\s*$", re.IGNORECASE)
MARK_REACH = 6.0                    # the mark's apex lies within 6 text heights of the text


@dataclass
class Check:
    check: str
    unit: Optional[str]
    score: Optional[float]
    samples: int
    note: Optional[str] = None
    shares: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return {"check": self.check, "unit": self.unit, "score": None if self.score is None else round(self.score, 3),
                "samples": self.samples, "note": self.note}


@dataclass
class UnitResult:
    insunits: Optional[int]
    metres_per_unit: Optional[float]
    method: str                       # dxf_insunits | unit_check | none
    unit: Optional[str]
    checks: list[Check]
    conflict: Optional[str] = None
    review: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {"insunits": self.insunits, "metres_per_unit": self.metres_per_unit, "method": self.method,
                "checks": [c.to_json() for c in self.checks], "conflict": self.conflict}


# --------------------------------------------------------------------------
# Decision rule
# --------------------------------------------------------------------------

def _decide(name: str, passed: dict[str, int], samples: int, note: Optional[str] = None) -> Check:
    """One check's unit from per-unit pass counts."""
    if samples < MIN_SAMPLES.get(name, 1):
        return Check(name, None, None, samples, note or f"{samples} sample(s), fewer than {MIN_SAMPLES.get(name, 1)}")
    shares = {u: passed.get(u, 0) / samples for u in UNITS}
    best = max(UNITS, key=lambda u: (shares[u], -list(UNITS).index(u)))
    others = [shares[u] for u in UNITS if u != best]
    if shares[best] >= DECIDE_SHARE and all(s <= shares[best] - DECIDE_MARGIN for s in others):
        return Check(name, best, shares[best], samples, note, shares)
    fitting = [u for u in UNITS if shares[u] >= DECIDE_SHARE]
    why = (f"{' and '.join(fitting)} fit equally well" if len(fitting) > 1 else
           f"no unit fits {DECIDE_SHARE:.0%} of the samples")
    return Check(name, None, shares[best], samples, (note + "; " if note else "") + why, shares)


def _in(v: float, lo_hi: tuple[float, float]) -> bool:
    return lo_hi[0] <= v <= lo_hi[1]


def _ratio_ok(mpu: float, unit_m: float) -> bool:
    return mpu > 0 and abs(math.log(mpu / unit_m)) <= math.log(RATIO_TOL)


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def area_label_texts(texts) -> list[tuple[object, float]]:
    """(text, m²) of the room-area labels among ``texts`` (titles such as ``ZEMİN KAT PLANI BRÜT 92M2`` excluded)."""
    out = []
    for t in texts:
        if T.class_of(t.text) is not None or T.level_of(t.text) is not None:
            continue
        _, area = B.parse_area_label(t.text)
        if area is not None and area > 0:
            out.append((t, float(area)))
    return out


def _polygon_area(pts) -> float:
    a = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def _point_in_polygon(p, pts) -> bool:
    x, y = p
    inside = False
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if xi > x:
                inside = not inside
    return inside


def check_area_labels(regions) -> Check:
    samples: list[tuple[str, float, float]] = []      # (kind, label m², area in units²)
    for r in regions:
        labels = area_label_texts(r.texts)
        if not labels:
            continue
        outlines = []
        for st in r.strokes():
            if st.closed and len(st.pts) >= 3 and st.fill is None:
                a = _polygon_area(list(st.pts))
                if a > 0:
                    outlines.append((a, list(st.pts)))
        for t, m2 in labels:
            holders = [o for o in outlines if _point_in_polygon(t.point, o[1])]
            if not holders:
                continue
            area, pts = min(holders, key=lambda o: o[0])
            if sum(1 for t2, _ in labels if _point_in_polygon(t2.point, pts)) == 1:
                samples.append(("room", m2, area))
        if len(labels) >= 2:
            b = r.geometry_box
            area = (b[2] - b[0]) * (b[3] - b[1])
            if area > 0:
                samples.append(("region", sum(m2 for _, m2 in labels), area))
    passed = {u: 0 for u in UNITS}
    for kind, m2, area in samples:
        for u, f in UNITS.items():
            ratio = m2 / (area * f * f)
            if _in(ratio, ROOM_AREA if kind == "room" else REGION_AREA):
                passed[u] += 1
    rooms = sum(1 for s in samples if s[0] == "room")
    note = f"{rooms} labels alone in a closed outline, {len(samples) - rooms} regions with >= 2 labels"
    return _decide("area_labels", passed, len(samples), note)


def _straight(st) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
    if st.arc is not None or len(st.pts) < 2:
        return None
    a, b = st.pts[0], st.pts[-1]
    length = math.dist(a, b)
    if length <= 0:
        return None
    if len(st.pts) > 2:
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        if any(abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) > 1e-3 * length for p in st.pts[1:-1]):
            return None
    return a, b


def segments(strokes) -> list[tuple[tuple[float, float], tuple[float, float], object]]:
    """Straight pieces of the strokes: open straight strokes, and each edge of polylines and closed outlines."""
    out = []
    for st in strokes:
        if st.arc is not None or len(st.pts) < 2:
            continue
        s = _straight(st)
        if s is not None and not st.closed:
            out.append((s[0], s[1], st))
            continue
        pts = list(st.pts) + ([st.pts[0]] if st.closed else [])
        for a, b in zip(pts, pts[1:]):
            if a != b:
                out.append((a, b, st))
    return out


def mark_texts(texts) -> list[tuple[object, float]]:
    """(text, value in metres) of level-mark texts (``43.00``, ``+3.00``, ``±0.00``, ``-3,00``)."""
    out = []
    for t in texts:
        m = MARK_RE.match(t.text.replace(" ", ""))
        if not m:
            continue
        value = float(m.group(2).replace(",", "."))
        if m.group(1) == "-":
            value = -value
        out.append((t, value))
    return out


def mark_point(t, segs) -> Optional[tuple[float, float, str]]:
    """The point a level mark points at: the apex of the mark triangle (two short sloped strokes meeting at their
    lowest point) below the text within ``MARK_REACH`` text heights; else the nearest horizontal line below it
    whose x-range holds the text. (x, y, how) or None."""
    h = max(t.height, 1e-9)
    px, py = t.point
    ends: dict[tuple, list] = {}
    for a, b, st in segs:
        length = math.dist(a, b)
        if length > 4 * h or length <= 0:
            continue
        ang = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) % 180.0
        if not (20.0 <= ang <= 70.0 or 110.0 <= ang <= 160.0):
            continue
        low, high = (a, b) if a[1] <= b[1] else (b, a)
        ends.setdefault((round(low[0] / (h * 0.02)), round(low[1] / (h * 0.02))), []).append((low, high))
    best = None
    for key, pairs in ends.items():
        if len(pairs) < 2:
            continue
        lows = [p[0] for p in pairs]
        highs = [p[1] for p in pairs]
        if not (any(hh[0] < lows[0][0] for hh in highs) and any(hh[0] > lows[0][0] for hh in highs)):
            continue                                # one stroke goes up-left, the other up-right: a V
        ax, ay = lows[0]
        if ay > py or py - ay > MARK_REACH * h or abs(ax - px) > MARK_REACH * h:
            continue
        d = math.hypot(ax - px, ay - py)
        if best is None or d < best[0]:
            best = (d, ax, ay)
    if best is not None:
        return best[1], best[2], "triangle"
    lines = []
    for a, b, st in segs:
        if abs(a[1] - b[1]) > 1e-6 * max(1.0, abs(a[1])) or a[1] > py or py - a[1] > 3 * h:
            continue
        if min(a[0], b[0]) - 2 * h <= px <= max(a[0], b[0]) + 2 * h:
            lines.append((py - a[1], a[1]))
    if lines:
        return px, min(lines)[1], "line"
    return None


def check_level_marks(regions) -> tuple[Check, list[dict]]:
    pairs = []
    found = []
    for r in regions:
        marks = mark_texts(r.texts)
        if len(marks) < 2:
            continue
        segs = segments(r.strokes())
        pts = []
        for t, value in marks:
            mp = mark_point(t, segs)
            if mp is not None:
                pts.append((t, value, mp))
                found.append({"region": r.id, "text": t.text, "entity": t.id, "value": value, "y": mp[1],
                              "how": mp[2]})
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dv = abs(pts[i][1] - pts[j][1])
                dy = abs(pts[i][2][1] - pts[j][2][1])
                if dv > 0 and dy > 0:
                    pairs.append(dv / dy)
    passed = {u: sum(1 for m in pairs if _ratio_ok(m, f)) for u, f in UNITS.items()}
    note = (f"{len(pairs)} mark pair(s): " + ", ".join(f"{m:.4g} m/unit" for m in pairs[:4])) if pairs else None
    return _decide("level_marks", passed, len(pairs), note), found


def door_arcs(strokes) -> list[float]:
    """Radii (source units) of door swings: quarter arcs with a straight leaf from the arc centre to one arc end."""
    arcs = []
    lines = []
    for st in strokes:
        if st.arc is not None and st.kind == "arc":
            span = (st.arc["end_deg"] - st.arc["start_deg"]) % 360.0
            if _in(span, QUARTER_SPAN_DEG):
                arcs.append(st)
        elif st.arc is None and len(st.pts) >= 2:
            lines.append(st)
    arcs = [a for a in arcs if a.arc["radius"] > 0]
    if not arcs:
        return []
    cell = max(LEAF_TOL * a.arc["radius"] for a in arcs) or 1.0
    grid: dict[tuple, list] = {}
    for a, b, st in segments(lines):
        for p, q in ((a, b), (b, a)):
            grid.setdefault((int(p[0] // cell), int(p[1] // cell)), []).append((p, q))
    radii = []
    for st in arcs:
        c = st.arc["center"]
        r = st.arc["radius"]
        tol = LEAF_TOL * r
        ends = (st.pts[0], st.pts[-1])
        gx, gy = int(c[0] // cell), int(c[1] // cell)
        hit = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for p, q in grid.get((gx + dx, gy + dy), []):
                    if not _in(math.dist(p, q) / r, LEAF_LENGTH):
                        continue
                    if math.dist(p, c) <= tol and any(math.dist(q, e) <= tol for e in ends):
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            radii.append(r)
    return radii


def check_door_widths(regions) -> Check:
    radii = [r for reg in regions for r in door_arcs(reg.strokes())]
    passed = {u: sum(1 for r in radii if _in(r * f, DOOR_RADIUS_M)) for u, f in UNITS.items()}
    note = f"median door radius {statistics.median(radii):.4g} units" if radii else None
    return _decide("door_widths", passed, len(radii), note)


def face_pair_distances(strokes, diag: float) -> list[float]:
    """Distance of each long straight stroke to its nearest parallel neighbour that overlaps it by >= 50 %."""
    segs = []
    for a, b, _ in segments(strokes):
        length = math.dist(a, b)
        if length < WALL_STROKE_REL * diag:
            continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0
        segs.append((ang, a, b, length))
    by_bucket: dict[int, list] = {}
    for s in segs:
        by_bucket.setdefault(int(round(s[0])) % 180, []).append(s)
    out = []
    reach = 0.05 * diag
    for bucket, items in by_bucket.items():
        t = math.radians(bucket)
        ux, uy = math.cos(t), math.sin(t)
        proj = []
        for ang, a, b, length in items:
            o = -a[0] * uy + a[1] * ux
            t0, t1 = sorted((a[0] * ux + a[1] * uy, b[0] * ux + b[1] * uy))
            proj.append((o, t0, t1))
        proj.sort()
        for i, (o, t0, t1) in enumerate(proj):
            for j in range(i + 1, len(proj)):
                o2, s0, s1 = proj[j]
                d = o2 - o
                if d > reach:
                    break
                if d <= 1e-9 * max(1.0, abs(o)):
                    continue
                overlap = min(t1, s1) - max(t0, s0)
                if overlap >= WALL_OVERLAP * min(t1 - t0, s1 - s0):
                    out.append(d)
                    break
    return out


def check_wall_thickness(regions) -> Check:
    ds = []
    for r in regions:
        b = r.geometry_box
        diag = math.hypot(b[2] - b[0], b[3] - b[1])
        ds.extend(face_pair_distances(r.strokes(), diag))
    passed = {u: sum(1 for d in ds if _in(d * f, WALL_M)) for u, f in UNITS.items()}
    note = f"median face-pair distance {statistics.median(ds):.4g} units" if ds else None
    return _decide("wall_thickness", passed, len(ds), note)


def check_text_height(regions) -> Check:
    hs = [t.height for r in regions for t in r.texts
          if t.height > 0 and T.class_of(t.text) is None and T.level_of(t.text) is None]
    if len(hs) < MIN_SAMPLES["text_height"]:
        return Check("text_height", None, None, len(hs), f"{len(hs)} text(s)")
    median = statistics.median(hs)
    fitting = [u for u, f in UNITS.items() if _in(median * f, TEXT_HEIGHT_M)]
    note = f"median text height {median:.4g} units"
    if len(fitting) == 1:
        return Check("text_height", fitting[0], 1.0, len(hs), note)
    return Check("text_height", None, None, len(hs),
                 note + ("; " + " and ".join(fitting) + " fit equally well" if fitting else "; no unit fits"))


def check_dimensions(regions) -> Check:
    ratios = []
    for r in regions:
        for e in r.ents:
            d = e.dim
            if d is None or not d.text or d.measured_units <= 0:
                continue
            length = U.parse_length(d.text)
            if length is not None and length.metres > 0:
                ratios.append(length.metres / d.measured_units)
    passed = {u: sum(1 for m in ratios if _ratio_ok(m, f)) for u, f in UNITS.items()}
    return _decide("dimensions", passed, len(ratios))


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def check_units(insunits: Optional[int], regions, file_rel: str) -> UnitResult:
    """The unit of one CAD document from its drawing regions (strays excluded)."""
    drawings = [r for r in regions if r.kind == "drawing"]
    marks_check, _ = check_level_marks(drawings)
    checks = [check_area_labels(drawings), marks_check, check_door_widths(drawings),
              check_wall_thickness(drawings), check_text_height(drawings), check_dimensions(drawings)]
    header = INSUNITS_NAME.get(int(insunits)) if insunits is not None else None
    decided = [c for c in checks if c.unit is not None]
    support = [c for c in decided if c.unit == header]
    against = [c for c in decided if c.unit != header]
    votes: dict[str, list[Check]] = {}
    for c in against:
        votes.setdefault(c.unit, []).append(c)
    top = max(votes.items(), key=lambda kv: len(kv[1]), default=(None, []))
    result = UnitResult(insunits=insunits, metres_per_unit=UNITS.get(header) if header else None,
                        method="dxf_insunits" if header else "none", unit=header, checks=checks)
    names = lambda cs: ", ".join(c.check for c in cs)  # noqa: E731 - a short local formatter
    if header is not None and not against:
        if not support:
            result.warnings.append(f"{file_rel}: no unit check could decide (too few samples); $INSUNITS "
                                   f"{insunits} ({header}) used")
        return result
    if len(top[1]) >= 2 and not support and len(votes) == 1:
        unit = top[0]
        result.unit, result.metres_per_unit, result.method = unit, UNITS[unit], "unit_check"
        if header is not None:
            result.conflict = (f"$INSUNITS {insunits} says {header}, but {len(top[1])} independent checks "
                               f"({names(top[1])}) agree on {unit} and none supports {header}: {unit} used")
        else:
            result.warnings.append(f"{file_rel}: $INSUNITS {insunits} names no unit; {len(top[1])} checks "
                                   f"({names(top[1])}) agree on {unit}: {unit} used")
        return result
    if header is None:
        result.warnings.append(f"{file_rel}: $INSUNITS {insunits} names no unit and the checks do not agree on one "
                               f"({names(decided) or 'none decided'}); the scale is left to the dimension texts")
        return result
    if support:
        result.warnings.append(f"{file_rel}: $INSUNITS {insunits} ({header}) used: {names(support)} support it, "
                               f"{names(against)} " + ", ".join(f"say {c.unit}" for c in against))
        return result
    result.review = (f"{file_rel}: unit check: $INSUNITS {insunits} says {header}, "
                     + ", ".join(f"{c.check} says {c.unit}" for c in against)
                     + "; no two independent checks agree on one unit")
    result.metres_per_unit, result.method, result.unit = None, "none", None
    return result
