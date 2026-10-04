"""Test helper: real01's page as a ``GenericPage`` for the G2 geometry tests (docs/milestone7.md §1.5, §2.10).

G3 owns the real CAD-PDF adapter (``wenart.ingest.cad_pdf``); until it is wired, the geometry tests read
``projects/real01/real01.pdf`` here with pdfplumber, the same way the spec describes the adapter (§2.2):

- lines, rects and curves become ``Stroke``s in PDF points with **y up** (pdfplumber's ``top`` space is y down);
- curves are flattened from ``curve['path']`` (ops ``m``, ``l``, ``c``, ``h``; Béziers split until the chord error
  is below 0.25 pt), never from ``curve['pts']``, which only hold the path vertices;
- a flattened curve that fits a circle within 1 % of its radius gets ``arc``;
- texts are pdfplumber words (one ``TextRun`` per word, box y up).

``page_metres`` scales everything by the reference scale (0.024511 m/pt) the way ``core.to_metres`` will, and
``ref_point``/``ref_box`` map the reference's feet (origin = min corner of the house walls) to page metres. The page
is read once per test session (about 5 s); ``g2_chain`` runs walls -> openings -> plot/separators -> furniture on it
once. The section at the end builds small synthetic pages (in metres) for the G2 unit tests.
"""
from __future__ import annotations

import functools
import math
from pathlib import Path

import yaml

from wenart.ingest.generic.model import GenericPage, Stroke, TextRun

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "projects" / "real01" / "real01.pdf"
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"

PT_PER_FT = 12.4352                      # reference scale (tests/fixtures/real01_reference.yaml)
M_PER_PT = 0.3048 / PT_PER_FT            # 0.024511 m/pt
ORIGIN_PT = (165.64, 595.0 - 459.84)     # min corner of the house walls, PDF points, y up
CHORD_PT = 0.25                          # max chord error when flattening Béziers


def _colour(value):
    """pdfplumber colour (gray, RGB or CMYK tuple, or None) -> RGB 0..1; None stays None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return (float(value),) * 3
    vals = tuple(float(v) for v in value)
    if len(vals) == 1:
        return vals * 3
    if len(vals) == 4:
        c, m, y, k = vals
        return ((1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))
    return vals[:3]


def _bezier(p0, p1, p2, p3, n: int = 0) -> list[tuple[float, float]]:
    """Points of one cubic Bézier (without p0): ``n`` of them, or enough that the chord error stays below
    CHORD_PT (the control polygon's length bounds the curve's)."""
    if n <= 0:
        span = max(math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3), 1e-9)
        n = max(2, min(64, int(math.ceil(math.sqrt(span / (8 * CHORD_PT)) * 2))))
    out = []
    for k in range(1, n + 1):
        t = k / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def _flatten(path, height: float):
    """(points y up, closed, has Bézier, dense points for the circle fit) of one pdfplumber path."""
    pts: list[tuple[float, float]] = []
    dense: list[tuple[float, float]] = []
    closed = False
    bezier = False
    cur = None
    for op in path:
        if op[0] in ("m", "l"):
            cur = op[1]
            pts.append(cur)
            dense.append(cur)
        elif op[0] == "c":
            bezier = True
            pts.extend(_bezier(cur, op[1], op[2], op[3]))
            dense.extend(_bezier(cur, op[1], op[2], op[3], 16))
            cur = op[3]
        elif op[0] == "h":
            closed = True
    pts = [(float(x), float(height - y)) for x, y in pts]
    dense = [(float(x), float(height - y)) for x, y in dense]
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        closed = True
        pts = pts[:-1]
    return pts, closed, bezier, dense


def _circle_fit(pts):
    """(cx, cy, r, max residual) of a least-squares circle, or None."""
    n = len(pts)
    if n < 3:
        return None
    sx = sum(p[0] for p in pts) / n
    sy = sum(p[1] for p in pts) / n
    u = [p[0] - sx for p in pts]
    v = [p[1] - sy for p in pts]
    suu = sum(a * a for a in u)
    svv = sum(b * b for b in v)
    suv = sum(a * b for a, b in zip(u, v))
    suuu = sum(a ** 3 for a in u)
    svvv = sum(b ** 3 for b in v)
    suvv = sum(a * b * b for a, b in zip(u, v))
    svuu = sum(b * a * a for a, b in zip(u, v))
    det = suu * svv - suv * suv
    if abs(det) < 1e-12:
        return None
    uc = (0.5 * (suuu + suvv) * svv - 0.5 * (svvv + svuu) * suv) / det
    vc = (0.5 * (svvv + svuu) * suu - 0.5 * (suuu + suvv) * suv) / det
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    cx, cy = uc + sx, vc + sy
    resid = max(abs(math.dist(p, (cx, cy)) - r) for p in pts)
    return cx, cy, r, resid


@functools.lru_cache(maxsize=1)
def real01_page() -> GenericPage:
    """real01 page 1 as a GenericPage in PDF points, y up (read once)."""
    import pdfplumber

    with pdfplumber.open(str(PDF)) as pdf:
        page = pdf.pages[0]
        height = float(page.height)
        strokes: list[Stroke] = []
        for i, obj in enumerate(page.lines):
            pts = [(float(x), float(height - y)) for x, y in obj["pts"]]
            strokes.append(Stroke(id=f"line:{i}", kind="line", pts=pts,
                                  colour=_colour(obj.get("stroking_color")) or (0.0, 0.0, 0.0),
                                  width=float(obj.get("linewidth") or 0.0)))
        for i, obj in enumerate(page.rects):
            x0, x1 = float(obj["x0"]), float(obj["x1"])
            y0, y1 = height - float(obj["bottom"]), height - float(obj["top"])
            strokes.append(Stroke(id=f"rect:{i}", kind="polyline", pts=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                                  closed=True, colour=_colour(obj.get("stroking_color")) or (0.0, 0.0, 0.0),
                                  fill=_colour(obj.get("non_stroking_color")) if obj.get("fill") else None,
                                  width=float(obj.get("linewidth") or 0.0)))
        for i, obj in enumerate(page.curves):
            pts, closed, bezier, dense = _flatten(obj["path"], height)
            if not pts:
                continue
            arc = None
            if bezier and len(dense) >= 5:
                fit = _circle_fit(dense)
                if fit and fit[2] > 0 and fit[3] <= 0.01 * fit[2]:
                    cx, cy, r, _ = fit
                    arc = {"center": (cx, cy), "radius": r,
                           "start_deg": math.degrees(math.atan2(pts[0][1] - cy, pts[0][0] - cx)),
                           "end_deg": math.degrees(math.atan2(pts[-1][1] - cy, pts[-1][0] - cx))}
            if len(pts) == 1:
                pts = [pts[0], pts[0]]
            strokes.append(Stroke(id=f"curve:{i}", kind="curve" if bezier else "polyline", pts=pts, closed=closed,
                                  colour=_colour(obj.get("stroking_color")) if obj.get("stroke") else None,
                                  fill=_colour(obj.get("non_stroking_color")) if obj.get("fill") else None,
                                  width=float(obj.get("linewidth") or 0.0), arc=arc))
        texts = []
        for i, word in enumerate(page.extract_words(keep_blank_chars=True)):
            box = (float(word["x0"]), height - float(word["bottom"]), float(word["x1"]), height - float(word["top"]))
            texts.append(TextRun(id=f"word:{i}", text=word["text"], box=box, height=box[3] - box[1],
                                 rotation_deg=0.0 if word.get("upright", True) else 90.0))
        return GenericPage(file="projects/real01/real01.pdf", page=1, source_kind="cad_pdf", units="pt",
                           units_to_m=None, size=(float(page.width), height), strokes=strokes, texts=texts)


def _scale_stroke(st: Stroke, s: float) -> Stroke:
    arc = None
    if st.arc:
        arc = dict(st.arc, center=(st.arc["center"][0] * s, st.arc["center"][1] * s), radius=st.arc["radius"] * s)
    return Stroke(id=st.id, kind=st.kind, pts=[(x * s, y * s) for x, y in st.pts], closed=st.closed, colour=st.colour,
                  fill=st.fill, width=st.width * s, layer=st.layer, block=st.block, arc=arc, source=st.source)


@functools.lru_cache(maxsize=1)
def page_metres() -> tuple[list[Stroke], list[TextRun]]:
    """Strokes and texts of real01 in page metres (y up, no offset), as ``core.to_metres`` gives them."""
    page = real01_page()
    s = M_PER_PT
    strokes = [_scale_stroke(st, s) for st in page.strokes]
    texts = [TextRun(id=t.id, text=t.text, box=tuple(v * s for v in t.box), height=t.height * s,
                     rotation_deg=t.rotation_deg) for t in page.texts]
    return strokes, texts


def ref_point(x_ft: float, y_ft: float) -> tuple[float, float]:
    """Reference feet (house frame) -> page metres."""
    return ((ORIGIN_PT[0] + x_ft * PT_PER_FT) * M_PER_PT, (ORIGIN_PT[1] + y_ft * PT_PER_FT) * M_PER_PT)


def to_ref(p) -> tuple[float, float]:
    """Page metres -> reference feet (house frame)."""
    return ((p[0] / M_PER_PT - ORIGIN_PT[0]) / PT_PER_FT, (p[1] / M_PER_PT - ORIGIN_PT[1]) / PT_PER_FT)


def ref_box(box_ft) -> tuple[float, float, float, float]:
    x0, y0 = ref_point(box_ft[0], box_ft[1])
    x1, y1 = ref_point(box_ft[2], box_ft[3])
    return (x0, y0, x1, y1)


@functools.lru_cache(maxsize=1)
def reference() -> dict:
    return yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))


def dimension_stroke_ids() -> set[str]:
    """The red dimension strokes (lines, arrowheads, extension lines): what G1's finder hands to §2.8."""
    page = real01_page()
    red = (1.0, 0.0, 0.0)
    return {st.id for st in page.strokes if st.colour == red or st.fill == red}


# --------------------------------------------------------------------------
# The G2 geometry chain on real01, run once per session (docs/milestone7.md §1.5 order)
# --------------------------------------------------------------------------

from dataclasses import dataclass, field as _field  # noqa: E402


@dataclass
class LabelBlockStub:
    """Minimal stand-in for G1's ``labels.LabelBlock`` (the fields G2 reads)."""
    name: str
    anchor: tuple
    room_type: str = "other"
    exterior: bool = False
    size_text: str = None
    area_text: str = None
    name_runs: list = _field(default_factory=list)
    evidence: list = _field(default_factory=list)


@dataclass
class DimStub:
    """Stand-in for G1's dimension candidates: §2.8 only reads ``stroke_ids``."""
    stroke_ids: set


def label_blocks() -> list[LabelBlockStub]:
    """The reference's room labels (name-line anchors) plus the exterior Parking label, in page metres."""
    ref = reference()
    blocks = [LabelBlockStub(r["label"], ref_point(*r["label_name_anchor_ft"]), r["room_type"], False,
                             r["label_size_text"]) for r in ref["rooms"]]
    parking = ref["site"]["areas"][0]
    blocks.append(LabelBlockStub("Parking", ref_point(*parking["label_name_anchor_ft"]), "other", True,
                                 parking["label_size_text"]))
    return blocks


@functools.lru_cache(maxsize=1)
def g2_chain() -> dict:
    """Walls, openings, plot split, faces, separators and furniture of real01 (page metres)."""
    from shapely.geometry import Point

    from wenart.ingest.generic import openings as O
    from wenart.ingest.generic import symbols as SY
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.generic import walls as W

    page = real01_page()
    strokes, texts = page_metres()
    file_rel = page.file
    prims = W.wall_primitives(page, M_PER_PT)
    mask = W.wall_mask(page, prims, M_PER_PT)
    prim_ids = {i for p in prims for i in p.stroke_ids}
    outline_strokes = [s for s in strokes if s.id not in prim_ids]
    walls, wall_info = W.walls_from_mask(mask, outline_strokes, file_rel, 1, units_to_m=M_PER_PT)
    free = set(wall_info["dropped_strokes"])
    wall_strokes = prim_ids - free
    non_wall = [s for s in strokes if s.id not in wall_strokes]
    walls2, openings, gap_log, owned = O.gaps_and_openings(walls, non_wall, file_rel, 1, units_to_m=M_PER_PT)
    blocks = label_blocks()
    bwalls, site, site_warnings = TP.split_plot(walls2, openings, blocks, level_id="L0")
    site_idx = {o["index"] for o in site["openings"]}
    b_openings = [o for k, o in enumerate(openings) if k not in site_idx]
    outline = TP.building_outline(bwalls, b_openings)
    notes: list = []
    pieces, cands, decor = SY.furniture(non_wall, owned, bwalls, b_openings, texts, [DimStub(dimension_stroke_ids())],
                                        outline, [], wall_strokes=wall_strokes, site_walls=site["boundary_walls"],
                                        level_id="L0", file_rel=file_rel, page_no=1, units_to_m=M_PER_PT,
                                        notes=notes)
    stairs = [p for p in pieces if p.type == "stair"]
    seps, sep_log = TP.separators(bwalls, b_openings, gap_log, blocks, stairs, units_to_m=M_PER_PT)
    faces = []
    for f in TP.faces(bwalls, b_openings, seps):
        names = [b for b in blocks if not b.exterior and f.contains(Point(b.anchor))]
        faces.append({"polygon": f, "room_type": names[0].room_type if names else None,
                      "label": names[0].name if names else None})
    SY.apply_room_checks(pieces, cands, faces, notes)
    return {"page": page, "strokes": strokes, "texts": texts, "prims": prims, "mask": mask, "walls_raw": walls,
            "wall_info": wall_info, "walls": walls2, "openings": openings, "gap_log": gap_log, "owned": owned,
            "blocks": blocks, "building_walls": bwalls, "site": site, "site_warnings": site_warnings,
            "building_openings": b_openings, "outline": outline, "pieces": pieces, "candidates": cands,
            "decor": decor, "notes": notes, "separators": seps, "separator_log": sep_log, "faces": faces}


# --------------------------------------------------------------------------
# Synthetic pages for the G2 unit tests (page units = metres)
# --------------------------------------------------------------------------

_ids = {"n": 0}


def sid(prefix: str = "s") -> str:
    _ids["n"] += 1
    return f"{prefix}:{_ids['n']}"


def stroke(pts, closed=False, colour=(0.0, 0.0, 0.0), fill=None, kind=None, block=None, prefix="s") -> Stroke:
    pts = [tuple(map(float, p)) for p in pts]
    if kind is None:
        kind = "line" if len(pts) == 2 and not closed else "polyline"
    return Stroke(id=sid(prefix), kind=kind, pts=pts, closed=closed, colour=colour, fill=fill, block=block)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def edges(poly, prefix="e", colour=(0.0, 0.0, 0.0)) -> list[Stroke]:
    """One line stroke per polygon edge."""
    n = len(poly)
    return [stroke([poly[i], poly[(i + 1) % n]], colour=colour, prefix=prefix) for i in range(n)]


def hatch(poly, step=0.003, angle_deg=45.0, colour=(0.0, 0.0, 0.0), prefix="h") -> list[Stroke]:
    """Parallel lines at ``angle_deg`` every ``step`` clipped to ``poly`` (shapely polygon or point list)."""
    from shapely.geometry import LineString as _LS, Polygon as _P

    shape = poly if hasattr(poly, "bounds") else _P(poly)
    x0, y0, x1, y1 = shape.bounds
    t = math.radians(angle_deg)
    d = (math.cos(t), math.sin(t))
    nrm = (-d[1], d[0])
    reach = math.hypot(x1 - x0, y1 - y0) + 1.0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    k = -int(reach / step)
    while k * step <= reach:
        ox, oy = cx + nrm[0] * k * step, cy + nrm[1] * k * step
        line = _LS([(ox - d[0] * reach, oy - d[1] * reach), (ox + d[0] * reach, oy + d[1] * reach)])
        inter = line.intersection(shape)
        for part in getattr(inter, "geoms", [inter]):
            if part.geom_type == "LineString" and part.length > 1e-6:
                out.append(stroke(list(part.coords), colour=colour, prefix=prefix))
        k += 1
    return out


def arc(center, radius, a0_deg, a1_deg, n=24, prefix="a") -> Stroke:
    pts = [(center[0] + radius * math.cos(math.radians(a0_deg + (a1_deg - a0_deg) * i / n)),
            center[1] + radius * math.sin(math.radians(a0_deg + (a1_deg - a0_deg) * i / n))) for i in range(n + 1)]
    st = stroke(pts, kind="curve", prefix=prefix)
    st.arc = {"center": tuple(center), "radius": radius, "start_deg": a0_deg, "end_deg": a1_deg}
    return st


def synthetic_page(strokes, texts=(), wall_hint_layers=()) -> GenericPage:
    xs = [p[0] for s in strokes for p in s.pts] or [0.0]
    ys = [p[1] for s in strokes for p in s.pts] or [0.0]
    return GenericPage(file="test.pdf", page=1, source_kind="cad_pdf", units="m", units_to_m=1.0,
                       size=(max(xs) + 1.0, max(ys) + 1.0), strokes=list(strokes), texts=list(texts),
                       wall_hint_layers=tuple(wall_hint_layers))


def wall(start, end, t=0.2, entity="w"):
    from wenart import building as _B
    from wenart.ingest.model import WallItem

    xs = [start[0], end[0]]
    ys = [start[1], end[1]]
    box = [min(xs) - t / 2, min(ys) - t / 2, max(xs) + t / 2, max(ys) + t / 2]
    return WallItem(start=tuple(start), end=tuple(end), thickness=t, box=box, entity=entity,
                    evidence=_B.evidence("test.pdf", "vector", 0.95, page=1, entity=entity))


def wall_faces(w) -> list[Stroke]:
    """The outline strokes of a wall rectangle."""
    from shapely.geometry import LineString as _LS

    poly = _LS([w.start, w.end]).buffer(w.thickness / 2, cap_style=2, join_style=2)
    return edges(list(poly.exterior.coords)[:-1], prefix="f")
