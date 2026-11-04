"""Synthetic failure classes: small CAD-office plans, each carrying ONE way real drawings broke the reader.

What (4 Nov 2026, Milestone 14 track R7, docs/milestone14.md §3 R7, docs/synthetic.md): a set of small houses and flats
drawn the way Turkish CAD offices draw (centimetres, layers DUVAR, KAPI, PENCERE, YAZI, OLCU, AKS, Turkish labels),
each with exactly one failure class the user found in the real drawings of 3 and 4 Nov 2026 (spaced labels, two-stub
jambs, glazed facades, dimension chains, mirrored halves, typical floors, elevation titles, winder stairs, open
recesses, garages and lifts, sheet frames), and its truth written exactly from the same layout data. The user's goal:
"I want structure recognition to be cumulatively better with the feedbacks I am giving".

Why: a lesson the user taught on a real drawing is only proven when a drawing with that failure is read right, and a
real drawing with known truth comes rarely. A synthetic case per class gives the truth without waiting for a new DWG,
and every reader change is measured against it (``tests/test_synthetic_failure_classes_20261104.py``; the cases the
reader does not handle yet are strict xfails, so they become targets).

How: a ``Plan`` holds the layout in building metres (outer wall faces from the origin): walls as centre lines with a
thickness, openings on walls, labels, stairs and extra primitives (dimension chains, axes, titles, frames, sections).
``write_dxf`` draws it as one R2000 DXF in centimetres with fixed metadata (byte-identical on every run): the walls as
the closed rings of the wall union with the opening gaps cut (what a drafter's wall outlines are), doors as a swing arc
and an open leaf, windows as four lines across the gap, labels as TEXT. ``reading_truth`` computes the truth from the
same data: the rooms are the holes of the union of the uncut walls (the walls run on through doors and windows), the
openings and walls come from the plan, levels and stairs from the project. A project may draw several plans (levels)
side by side on one sheet; each sits at its own sheet offset and its truth is in building metres.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import ezdxf
import yaml
from shapely.geometry import Point as SPoint, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G

CM = 100.0                       # drawing units (cm) per metre
INSUNITS = 5                     # centimetres
_FIXED_META_OPTION = "write_fixed_meta_data_for_testing"
DXF_FILE = "plan.dxf"
TRUTH_FILE = "truth/reading_truth.json"
PREVIEW = "{name}_plan_p1.jpg"

L_WALL, L_DOOR, L_WINDOW, L_TEXT, L_DIM, L_AXIS = "DUVAR", "KAPI", "PENCERE", "YAZI", "OLCU", "AKS"
L_STAIR, L_FRAME, L_SECTION, L_LEVEL = "MERDIVEN", "PAFTA", "KESIT", "KOT"
LAYERS = ((L_WALL, 7), (L_DOOR, 2), (L_WINDOW, 4), (L_TEXT, 7), (L_DIM, 3), (L_AXIS, 1), (L_STAIR, 6),
          (L_FRAME, 8), (L_SECTION, 7), (L_LEVEL, 1))
LABEL_H = 0.25                   # m, room labels
TITLE_H = 0.40                   # m, plan titles


def r6(v: float) -> float:
    return G.snap(float(v), 6)


def rp(p) -> list[float]:
    return [r6(p[0]), r6(p[1])]


# --------------------------------------------------------------------------
# The layout
# --------------------------------------------------------------------------

@dataclass
class Wall:
    """A straight wall: centre line ``a`` -> ``b`` (building metres), ``t`` thick. ``drawn=False``: the wall stands
    in the truth but the drafter drew no wall faces for it (a glazed facade drawn only by its frames)."""
    id: str
    a: tuple
    b: tuple
    t: float
    drawn: bool = True

    @property
    def length(self) -> float:
        return math.dist(self.a, self.b)

    @property
    def u(self) -> tuple:
        L = self.length
        return ((self.b[0] - self.a[0]) / L, (self.b[1] - self.a[1]) / L)

    @property
    def n(self) -> tuple:                 # left normal of a -> b
        ux, uy = self.u
        return (-uy, ux)

    def at(self, s: float, off: float = 0.0) -> tuple:
        ux, uy = self.u
        nx, ny = self.n
        return (self.a[0] + ux * s + nx * off, self.a[1] + uy * s + ny * off)

    def rect(self, s0: float = None, s1: float = None, grow: float = 0.0) -> Polygon:
        s0 = 0.0 if s0 is None else s0
        s1 = self.length if s1 is None else s1
        h = self.t / 2 + grow
        return Polygon([self.at(s0, -h), self.at(s1, -h), self.at(s1, h), self.at(s0, h)])


@dataclass
class Opening:
    """An opening in wall ``wall``: centre ``s`` metres along the wall from its start, ``width`` clear.
    ``kind``: door | window | opening (a doorless gap) | sliding (a sliding door, two leaves on tracks) | garage
    (a wide door, drawn as a dashed overhead line). A door hinges at the ``hinge`` end (start | end) of the gap and
    swings to ``side`` (+1 = the wall's left normal). ``draw_symbol=False`` leaves the gap without its symbol;
    ``cut=False`` keeps the wall faces running across (no gap)."""
    id: str
    kind: str
    wall: str
    s: float
    width: float
    hinge: str = "start"
    side: int = 1
    draw_symbol: bool = True
    cut: bool = True
    truth_type: Optional[str] = None      # the truth's "type" (default from kind)
    jamb_start: str = "closed"            # closed | stubs (two short stubs side by side) | cap (a frame cap)
    jamb_end: str = "closed"


@dataclass
class Label:
    text: str
    at: tuple
    height: float = LABEL_H
    spaced: bool = False                  # written letter by letter, one TEXT per letter
    layer: str = L_TEXT


@dataclass
class Prim:
    """One extra drawing primitive in building metres (text height in metres)."""
    kind: str                             # line | poly | circle | arc | text
    layer: str
    pts: list = field(default_factory=list)
    closed: bool = False
    radius: float = 0.0
    angles: tuple = ()
    text: str = ""
    height: float = 0.0
    linetype: str = ""
    align: str = "MIDDLE_CENTER"


@dataclass
class StairTruth:
    id: str
    kind: str
    center: tuple
    risers: int
    extra: dict = field(default_factory=dict)


@dataclass
class Plan:
    """One drawn plan (one level, or one typical plan standing for several levels)."""
    key: str
    origin: tuple                         # sheet position of the building origin, metres
    walls: list = field(default_factory=list)
    openings: list = field(default_factory=list)
    labels: list = field(default_factory=list)
    prims: list = field(default_factory=list)
    stairs: list = field(default_factory=list)
    title: Optional[str] = None
    title_at: Optional[tuple] = None      # building metres (default: centred below the plan)
    truth_rooms: Optional[dict] = None    # label text of the room at a point that carries no label: {(x, y): label}
    not_rooms: list = field(default_factory=list)   # holes that are open air in the truth (points inside them)

    def wall(self, wid: str) -> Wall:
        return next(w for w in self.walls if w.id == wid)

    def bounds(self) -> tuple:
        u = unary_union([w.rect() for w in self.walls])
        return u.bounds


@dataclass
class TruthLevel:
    id: str
    label: str
    elevation: float
    order: int
    plan: str                             # the plan key drawing it


@dataclass
class FailureProject:
    name: str
    failure_class: str
    lesson: str
    summary: str
    plans: list
    levels: list
    brief: dict
    sheet_prims: list = field(default_factory=list)   # in sheet metres (sections, frames, notes)
    extra_truth: dict = field(default_factory=dict)    # class-specific truth (site, sections, recesses ...)


# --------------------------------------------------------------------------
# Layout helpers
# --------------------------------------------------------------------------

EXT_T = 0.25
INT_T = 0.15


def outer_walls(prefix: str, w: float, h: float, t: float = EXT_T) -> list[Wall]:
    """The four outer walls of a w x h rectangle (outer faces at 0 and w / h), each running to the outer corners."""
    c = t / 2
    return [Wall(f"{prefix}1", (0.0, c), (w, c), t), Wall(f"{prefix}2", (w - c, 0.0), (w - c, h), t),
            Wall(f"{prefix}3", (w, h - c), (0.0, h - c), t), Wall(f"{prefix}4", (c, h), (c, 0.0), t)]


def outline_walls(prefix: str, pts: list, t: float = EXT_T) -> list[Wall]:
    """Outer walls along a counter-clockwise axis-aligned outline of outer faces: one wall per edge, on the inner
    side, running to the outer corner at a convex vertex and on to the inner corner (one wall thickness past the
    vertex) at a reflex vertex, so the union of the walls is one closed ring (the rule of ``LevelBuilder``)."""
    out = []
    c = t / 2
    n = len(pts)
    for i in range(n):
        a, b, nxt = pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        vx, vy = nxt[0] - b[0], nxt[1] - b[1]
        reflex = ux * vy - uy * vx < 0               # a right turn on a counter-clockwise outline
        ext = t if reflex else 0.0
        nx, ny = -uy, ux                             # left normal = inside
        out.append(Wall(f"{prefix}{i + 1}", (r6(a[0] + nx * c), r6(a[1] + ny * c)),
                        (r6(b[0] + nx * c + ux * ext), r6(b[1] + ny * c + uy * ext)), t))
    return out


def place(plan: "Plan", oid: str, kind: str, wall: str, at: tuple, width: float, **kw) -> "Opening":
    """An opening on ``wall`` centred at the point ``at`` (building metres; projected onto the wall line)."""
    w = plan.wall(wall)
    ux, uy = w.u
    s_ = (at[0] - w.a[0]) * ux + (at[1] - w.a[1]) * uy
    op = Opening(oid, kind, wall, r6(s_), width, **kw)
    plan.openings.append(op)
    return op


# --------------------------------------------------------------------------
# Notation and symbols (dimension chains, axes, stairs, sections)
# --------------------------------------------------------------------------

TICK_R = 0.035                   # m, the 7 cm tick circles of a dimension chain
TICK_SLASH = 0.10                # m, the tick slash


def dim_chain(points: list, offset_line: tuple, axis: str, ext_from: Optional[float] = None) -> list[Prim]:
    """An exploded dimension chain on OLCU (the way most offices draw them): one line through the chain, a 7 cm
    tick circle and a slash at every point, extension lines from ``ext_from`` and the segment lengths in
    centimetres above the line. ``axis`` 'x': the chain runs along x at y = ``offset_line[0]`` through the x values
    ``points``; 'y': along y at x = ``offset_line[0]``."""
    c = offset_line[0]
    pts = sorted(points)
    P = (lambda v: (v, c)) if axis == "x" else (lambda v: (c, v))
    out = [Prim("line", L_DIM, [P(pts[0] - 0.2), P(pts[-1] + 0.2)])]
    for v in pts:
        q = P(v)
        out.append(Prim("circle", L_DIM, [q], radius=TICK_R))
        d = TICK_SLASH / 2
        out.append(Prim("line", L_DIM, [(q[0] - d, q[1] - d), (q[0] + d, q[1] + d)]))
        if ext_from is not None:
            e = (v, ext_from) if axis == "x" else (ext_from, v)
            beyond = c + (0.15 if c > ext_from else -0.15)
            far = (v, beyond) if axis == "x" else (beyond, v)
            out.append(Prim("line", L_DIM, [e, far]))
    for v0, v1 in zip(pts, pts[1:]):
        mid = P((v0 + v1) / 2)
        at = (mid[0], mid[1] + 0.12) if axis == "x" else (mid[0] - 0.12, mid[1])
        out.append(Prim("text", L_DIM, [at], text=f"{round((v1 - v0) * 100):d}", height=0.12,
                        align="BOTTOM_CENTER" if axis == "x" else "MIDDLE_RIGHT"))
    return out


def axis_grid(xs: list, ys: list, box: tuple, names_x: list, names_y: list, bubble_r: float = 0.4) -> list[Prim]:
    """A grid of solid axis lines on AKS over ``box`` (x0, y0, x1, y1), a lettered or numbered bubble at both ends."""
    x0, y0, x1, y1 = box
    out = []
    for x, name in zip(xs, names_x):
        out.append(Prim("line", L_AXIS, [(x, y0), (x, y1)]))
        for y, d in ((y0, -1), (y1, 1)):
            cy = y + d * bubble_r
            out += [Prim("circle", L_AXIS, [(x, cy)], radius=bubble_r),
                    Prim("text", L_AXIS, [(x, cy)], text=name, height=0.35)]
    for y, name in zip(ys, names_y):
        out.append(Prim("line", L_AXIS, [(x0, y), (x1, y)]))
        for x, d in ((x0, -1), (x1, 1)):
            cx = x + d * bubble_r
            out += [Prim("circle", L_AXIS, [(cx, y)], radius=bubble_r),
                    Prim("text", L_AXIS, [(cx, y)], text=name, height=0.35)]
    return out


def u_stair(x0: float, y0: float, x1: float, y1: float, going: float, flight1: int, flight2: int,
            winders: int = 0, numbers: bool = False, well: float = 0.2) -> tuple[list[Prim], dict]:
    """A U stair in the box (x0, y0)-(x1, y1) on MERDIVEN: the first flight along +x in the lower half
    (``flight1`` treads of ``going``), the turn at the right end (a landing, or ``winders`` winder treads radiating
    from the well's end), the second flight back along -x in the upper half, the well between them, the walking
    arrow, and (``numbers``) every tread numbered from 1 at the bottom. Returns the prims and the truth record
    (risers = all treads + 1 per flight start ... counted as the numbered treads)."""
    ym = (y0 + y1) / 2
    wy0, wy1 = ym - well / 2, ym + well / 2
    xt = x0 + flight1 * going                    # the end of the first flight (and of the second)
    out = [Prim("poly", L_STAIR, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True),
           Prim("poly", L_STAIR, [(x0, wy0), (xt, wy0), (xt, wy1), (x0, wy1)], closed=True)]
    centres = []
    for k in range(flight1 + 1):
        x = x0 + k * going
        out.append(Prim("line", L_STAIR, [(x, y0), (x, wy0)]))
    for k in range(flight1):
        centres.append((x0 + (k + 0.5) * going, (y0 + wy0) / 2))
    cx, cy = xt, ym
    if winders:
        # radial winder lines from the well's end, splitting the half turn into ``winders`` treads
        for k in range(winders + 1):
            ang = math.radians(-90 + 180 * k / winders)
            dx, dy = math.cos(ang), math.sin(ang)
            ts = []
            if dx > 1e-9:
                ts.append((x1 - cx) / dx)
            if dy > 1e-9:
                ts.append((y1 - cy) / dy)
            if dy < -1e-9:
                ts.append((y0 - cy) / dy)
            t = min(ts)
            r0 = well / 2 if abs(dx) < 1e-9 else 0.0
            out.append(Prim("line", L_STAIR, [(r6(cx + dx * r0), r6(cy + dy * r0)),
                                              (r6(cx + dx * t), r6(cy + dy * t))]))
        for k in range(winders):
            ang = math.radians(-90 + 180 * (k + 0.5) / winders)
            r = 0.6 * min(x1 - cx, (y1 - y0) / 2)
            centres.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    else:
        centres.append(((xt + x1) / 2, ym))      # the landing (not a tread: no number)
    for k in range(flight2 + 1):
        x = xt - k * going
        out.append(Prim("line", L_STAIR, [(x, wy1), (x, y1)]))
    for k in range(flight2):
        centres.append((xt - (k + 0.5) * going, (wy1 + y1) / 2))
    # the walking line with its arrow head at the top
    walk = [((x0 + 0.1), (y0 + wy0) / 2), (xt, (y0 + wy0) / 2), ((xt + x1) / 2, ym), (xt, (wy1 + y1) / 2),
            (x0 + 0.1, (wy1 + y1) / 2)]
    out.append(Prim("poly", L_STAIR, walk))
    tip = walk[-1]
    out += [Prim("line", L_STAIR, [tip, (tip[0] + 0.15, tip[1] + 0.08)]),
            Prim("line", L_STAIR, [tip, (tip[0] + 0.15, tip[1] - 0.08)])]
    treads = flight1 + flight2 + winders
    if numbers:
        tread_centres = centres if winders else centres[:flight1] + centres[flight1 + 1:]
        for i, c in enumerate(tread_centres):
            out.append(Prim("text", L_STAIR, [(r6(c[0]), r6(c[1]))], text=str(i + 1), height=0.12))
    arms = [{"kind": "straight", "treads": [1, flight1], "box": [rp((x0, y0)), rp((xt, wy0))]}]
    if winders:
        arms.append({"kind": "winder", "treads": [flight1 + 1, flight1 + winders], "box": [rp((xt, y0)), rp((x1, y1))]})
    else:
        arms.append({"kind": "landing", "box": [rp((xt, y0)), rp((x1, y1))]})
    arms.append({"kind": "straight", "treads": [flight1 + winders + 1, treads], "box": [rp((x0, wy1)), rp((xt, y1))]})
    truth = {"treads": treads, "arms": arms, "box": [rp((x0, y0)), rp((x1, y1))]}
    return out, truth


def section_prims(origin: tuple, width: float, storeys: list, roof: tuple, title: str) -> list[Prim]:
    """A building section on KESIT / KOT in sheet metres: the two outer walls, a 20 cm slab at every floor mark,
    the roof slab, the ground line, at the right of every slab its level mark ('±0.00', '+3.00', ...) with the
    mark's triangle, at the left the storey's name (``storeys`` = [(name, elevation)], ``roof`` = (name,
    elevation)), the title below."""
    ox, oy = origin
    top = roof[1]
    out = [Prim("line", L_SECTION, [(ox - 2.0, oy), (ox + width + 2.0, oy)]),
           Prim("poly", L_SECTION, [(ox, oy - 0.5), (ox + 0.25, oy - 0.5), (ox + 0.25, oy + top + 0.6),
                                    (ox, oy + top + 0.6)], closed=True),
           Prim("poly", L_SECTION, [(ox + width - 0.25, oy - 0.5), (ox + width, oy - 0.5),
                                    (ox + width, oy + top + 0.6), (ox + width - 0.25, oy + top + 0.6)], closed=True)]
    for name, z in list(storeys) + [roof]:
        y = oy + z
        out.append(Prim("poly", L_SECTION, [(ox + 0.25, y - 0.2), (ox + width - 0.25, y - 0.2),
                                             (ox + width - 0.25, y), (ox + 0.25, y)], closed=True))
        mark = "±0.00" if abs(z) < 1e-9 else f"{z:+.2f}"
        mx = ox + width + 0.8
        out += [Prim("poly", L_LEVEL, [(mx, y), (mx - 0.15, y + 0.2), (mx + 0.15, y + 0.2)], closed=True),
                Prim("line", L_LEVEL, [(mx - 0.4, y), (mx + 1.6, y)]),
                Prim("text", L_LEVEL, [(mx + 0.25, y + 0.08)], text=mark, height=0.25, align="BOTTOM_LEFT"),
                Prim("text", L_TEXT, [(ox - 0.5, y + 0.3)], text=name, height=0.25, align="BOTTOM_RIGHT")]
    out.append(Prim("text", L_TEXT, [(ox + width / 2, oy - 1.7)], text=title, height=TITLE_H))
    out.append(Prim("text", L_TEXT, [(ox + width / 2, oy - 2.3)], text="ÖLÇEK 1/100", height=0.2))
    return out


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

def _gap(plan: Plan, op: Opening) -> tuple[float, float]:
    return op.s - op.width / 2, op.s + op.width / 2


STUB_L = 0.05                    # m, the length of a jamb stub along its wall
STUB_W = (0.07, 0.03)            # m, the two stubs side by side across the wall (real10: 7 and 3 cm of 16 cm)


def _cut_span(op: "Opening") -> tuple[float, float]:
    s0, s1 = op.s - op.width / 2, op.s + op.width / 2
    return (s0 - (STUB_L if op.jamb_start == "stubs" else 0.0), s1 + (STUB_L if op.jamb_end == "stubs" else 0.0))


def wall_body(plan: Plan) -> Polygon:
    """The drawn walls: the union of the drawn walls' rectangles minus the cut opening gaps (a stub jamb's gap runs
    on by ``STUB_L``: the stubs stand there)."""
    body = unary_union([w.rect() for w in plan.walls if w.drawn])
    cuts = []
    for op in plan.openings:
        w = plan.wall(op.wall)
        if not op.cut or not w.drawn:
            continue
        s0, s1 = _cut_span(op)
        cuts.append(w.rect(s0, s1, grow=0.002))
    if cuts:
        body = body.difference(unary_union(cuts))
    return body


def _open_ends(plan: Plan) -> list[tuple]:
    """The jamb ends drawn without the wall's closing line: (wall, along-position) of every stub or cap jamb."""
    out = []
    for op in plan.openings:
        if not op.cut:
            continue
        w = plan.wall(op.wall)
        s0, s1 = _cut_span(op)
        if op.jamb_start != "closed":
            out.append((w, s0))
        if op.jamb_end != "closed":
            out.append((w, s1))
    return out


def _is_end_segment(p, q, w: Wall, s_: float) -> bool:
    """Is the ring edge p-q the closing line across wall ``w`` at along-position ``s_``?"""
    ux, uy = w.u
    nx, ny = w.n
    for a in (p, q):
        along = (a[0] - w.a[0]) * ux + (a[1] - w.a[1]) * uy
        across = (a[0] - w.a[0]) * nx + (a[1] - w.a[1]) * ny
        if abs(along - s_) > 0.004 or abs(across) > w.t / 2 + 0.004:
            return False
    return True


def wall_prims(plan: Plan) -> list[Prim]:
    """The wall outlines: every ring of ``wall_body`` as a closed polyline on DUVAR, except where a jamb is drawn
    as stubs or a frame cap: there the ring's closing line is left out (an open polyline) and the stubs (two small
    rectangles side by side on DUVAR) or the cap (one line on KAPI) are drawn."""
    body = wall_body(plan)
    ends = _open_ends(plan)
    prims = []
    if body.is_empty:
        return prims
    for ring in _rings(body):
        n = len(ring)
        cut = [i for i in range(n) if any(_is_end_segment(ring[i], ring[(i + 1) % n], w, s_) for w, s_ in ends)]
        if not cut:
            prims.append(Prim("poly", L_WALL, ring, closed=True))
            continue
        for k, i in enumerate(cut):
            j = cut[(k + 1) % len(cut)]
            seq = [ring[(i + 1 + m) % n] for m in range(((j - i) % n) or n)]   # ring[i + 1] ... ring[j]
            if len(seq) >= 2:
                prims.append(Prim("poly", L_WALL, seq))
    for op in plan.openings:
        if not op.cut:
            continue
        w = plan.wall(op.wall)
        s0, s1 = op.s - op.width / 2, op.s + op.width / 2
        for style, edge, outward in ((op.jamb_start, s0, -1), (op.jamb_end, s1, 1)):
            if style == "stubs":
                lo = -w.t / 2
                for sw in STUB_W:
                    a0, a1 = sorted((edge, edge + outward * STUB_L))
                    prims.append(Prim("poly", L_WALL, [w.at(a0, lo), w.at(a1, lo), w.at(a1, lo + sw),
                                                       w.at(a0, lo + sw)], closed=True))
                    lo += sw
            elif style == "cap":
                prims.append(Prim("line", L_DOOR, [w.at(edge, -w.t / 2), w.at(edge, w.t / 2)]))
    return prims


def _rings(geom) -> list[list[tuple]]:
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    rings = []
    for p in sorted(polys, key=lambda q: (round(q.bounds[0], 4), round(q.bounds[1], 4))):
        p = p.simplify(1e-6)
        rings.append(_canon(list(p.exterior.coords)[:-1]))
        for hole in sorted(p.interiors, key=lambda h: (round(h.bounds[0], 4), round(h.bounds[1], 4))):
            rings.append(_canon(list(hole.coords)[:-1]))
    return rings


def _canon(ring: list) -> list:
    """A ring starting at its lowest-left vertex, counter-clockwise (deterministic across shapely versions)."""
    pts = [(r6(x), r6(y)) for x, y in ring]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    k = min(range(len(pts)), key=lambda i: (pts[i][1], pts[i][0]))
    return pts[k:] + pts[:k]


def door_prims(plan: Plan, op: Opening) -> list[Prim]:
    w = plan.wall(op.wall)
    s0, s1 = _gap(plan, op)
    face = op.side * w.t / 2
    if op.kind == "door":
        hs, other = (s0, s1) if op.hinge == "start" else (s1, s0)
        hinge = w.at(hs, face)
        closed = w.at(other, face)
        nx, ny = w.n
        open_end = (hinge[0] + nx * op.side * op.width, hinge[1] + ny * op.side * op.width)
        a_open = math.degrees(math.atan2(open_end[1] - hinge[1], open_end[0] - hinge[0]))
        a_closed = math.degrees(math.atan2(closed[1] - hinge[1], closed[0] - hinge[0]))
        # the 90 degree sweep counter-clockwise
        start, end = (a_closed, a_open) if (a_open - a_closed) % 360 == 90 else (a_open, a_closed)
        return [Prim("line", L_DOOR, [hinge, open_end]),
                Prim("arc", L_DOOR, [hinge], radius=op.width, angles=(start % 360, end % 360))]
    frame = []
    if not w.drawn:
        # a glazed facade: no wall faces, every opening drawn as its frame (a rectangle across the wall band)
        h = w.t / 2
        frame = [Prim("poly", L_WINDOW if op.kind == "window" else L_DOOR,
                      [w.at(s0, -h), w.at(s1, -h), w.at(s1, h), w.at(s0, h)], closed=True)]
    if op.kind == "sliding":
        q = w.t / 6
        half = (s0 + s1) / 2
        return frame + [Prim("poly", L_DOOR, [w.at(s0, -q), w.at(half + 0.05, -q), w.at(half + 0.05, -q + 0.04),
                                      w.at(s0, -q + 0.04)], closed=True),
                Prim("poly", L_DOOR, [w.at(half - 0.05, q - 0.04), w.at(s1, q - 0.04), w.at(s1, q),
                                      w.at(half - 0.05, q)], closed=True)]
    if op.kind == "garage":
        return [Prim("line", L_DOOR, [w.at(s0, 0.0), w.at(s1, 0.0)], linetype="DASHED"),
                Prim("line", L_DOOR, [w.at(s0, -w.t / 2), w.at(s1, -w.t / 2)])]
    if op.kind == "window":
        h = w.t / 2
        offs = (-h / 3, h / 3) if frame else (-h, -h / 3, h / 3, h)
        return frame + [Prim("line", L_WINDOW, [w.at(s0, o), w.at(s1, o)]) for o in offs]
    return []


def plan_prims(plan: Plan) -> list[Prim]:
    """Every primitive of a plan in building metres, in drawing order: walls, openings, stairs and extras, labels,
    title."""
    prims = wall_prims(plan)
    for op in plan.openings:
        if op.draw_symbol:
            prims += door_prims(plan, op)
    prims += plan.prims
    for lb in plan.labels:
        prims += label_prims(lb)
    if plan.title:
        x0, y0, x1, y1 = plan.bounds()
        at = plan.title_at or ((x0 + x1) / 2, y0 - 1.2)
        prims.append(Prim("text", L_TEXT, [at], text=plan.title, height=TITLE_H))
        prims.append(Prim("text", L_TEXT, [(at[0], at[1] - 0.6)], text="ÖLÇEK 1/50", height=0.2))
    return prims


def label_prims(lb: Label) -> list[Prim]:
    if not lb.spaced:
        return [Prim("text", lb.layer, [lb.at], text=lb.text, height=lb.height)]
    # letter by letter: one TEXT per non-blank character, 1.6 letter heights apart (the drafter's spaced title)
    chars = [c for c in lb.text]
    pitch = lb.height * 1.6
    x = lb.at[0] - pitch * (len(chars) - 1) / 2
    out = []
    for i, c in enumerate(chars):
        if c != " ":
            out.append(Prim("text", lb.layer, [(x + i * pitch, lb.at[1])], text=c, height=lb.height))
    return out


def _emit(msp, p: Prim, origin) -> None:
    def pt(q):
        return (r6((origin[0] + q[0]) * CM), r6((origin[1] + q[1]) * CM))

    attribs = {"layer": p.layer}
    if p.linetype:
        attribs["linetype"] = p.linetype
    if p.kind == "line":
        msp.add_line(pt(p.pts[0]), pt(p.pts[1]), dxfattribs=attribs)
    elif p.kind == "poly":
        msp.add_lwpolyline([pt(q) for q in p.pts], close=p.closed, dxfattribs=attribs)
    elif p.kind == "circle":
        msp.add_circle(pt(p.pts[0]), r6(p.radius * CM), dxfattribs=attribs)
    elif p.kind == "arc":
        msp.add_arc(pt(p.pts[0]), r6(p.radius * CM), r6(p.angles[0]), r6(p.angles[1]), dxfattribs=attribs)
    elif p.kind == "text":
        e = msp.add_text(p.text, height=r6(p.height * CM), dxfattribs=attribs)
        from ezdxf.enums import TextEntityAlignment
        e.set_placement(pt(p.pts[0]), align=TextEntityAlignment[p.align])
    else:
        raise ValueError(p.kind)


def write_dxf(project: FailureProject, path: Path) -> tuple:
    """Write the project's DXF; returns its extents (x0, y0, x1, y1) in drawing units."""
    previous = getattr(ezdxf.options, _FIXED_META_OPTION)
    setattr(ezdxf.options, _FIXED_META_OPTION, True)
    try:
        doc = ezdxf.new("R2000", setup=True)
        doc.header["$INSUNITS"] = INSUNITS
        doc.header["$MEASUREMENT"] = 1
        doc.header["$LUNITS"] = 2
        doc.header["$LTSCALE"] = 20.0
        drawn = [(plan, plan_prims(plan)) for plan in project.plans]
        known = {name for name, _ in LAYERS}
        extra = sorted({p.layer for _, prims in drawn for p in prims} | {p.layer for p in project.sheet_prims})
        for name, colour in list(LAYERS) + [(name, 7) for name in extra if name not in known]:
            doc.layers.add(name, color=colour)      # the class's own layers (KOLON, HAVUZ, ASANSOR ...) too
        msp = doc.modelspace()
        xs, ys = [], []
        for plan, prims in drawn:
            for p in prims:
                _emit(msp, p, plan.origin)
                for q in p.pts:
                    xs.append(plan.origin[0] + q[0])
                    ys.append(plan.origin[1] + q[1])
        for p in project.sheet_prims:
            _emit(msp, p, (0.0, 0.0))
            for q in p.pts:
                xs.append(q[0])
                ys.append(q[1])
        doc.header["$EXTMIN"] = (r6(min(xs) * CM), r6(min(ys) * CM), 0.0)
        doc.header["$EXTMAX"] = (r6(max(xs) * CM), r6(max(ys) * CM), 0.0)
        for dxftype in sorted(doc.entitydb.dxf_types_in_use()):
            doc.classes.add_class(dxftype)
        path.parent.mkdir(parents=True, exist_ok=True)
        doc.saveas(path)
        return (r6(min(xs) * CM), r6(min(ys) * CM), r6(max(xs) * CM), r6(max(ys) * CM))
    finally:
        setattr(ezdxf.options, _FIXED_META_OPTION, previous)


# --------------------------------------------------------------------------
# Truth
# --------------------------------------------------------------------------

def room_faces(plan: Plan) -> list[Polygon]:
    """The rooms: the holes of the union of every wall (drawn or not, uncut: walls run on through openings)."""
    u = unary_union([w.rect() for w in plan.walls])
    polys = [u] if u.geom_type == "Polygon" else list(u.geoms)
    faces = [Polygon(h.coords) for p in polys for h in p.interiors]
    return [f for f in faces if f.area > 0.5]


def plan_truth(plan: Plan, lid: str) -> dict:
    faces = room_faces(plan)
    rooms = []
    for face in sorted(faces, key=lambda f: (round(f.centroid.y, 3), round(f.centroid.x, 3))):
        if any(face.contains(SPoint(p)) for p in plan.not_rooms):
            continue
        texts = [lb.text for lb in plan.labels if face.contains(SPoint(lb.at))]
        for p, t in (plan.truth_rooms or {}).items():
            if face.contains(SPoint(p)):
                texts.append(t)
        label = texts[0] if texts else ""
        ring = _canon(list(face.exterior.coords)[:-1])
        rooms.append({"id": "", "label": label, "room_type": B.room_type_for(label) if label else "other",
                      "area": round(face.area, 4), "centroid": rp((face.centroid.x, face.centroid.y)),
                      "polygon": [rp(q) for q in ring]})
    for i, r in enumerate(rooms):
        r["id"] = f"r_{lid}_{i + 1:03d}"
    doors, windows, openings = [], [], []
    for op in plan.openings:
        w = plan.wall(op.wall)
        c = w.at(op.s)
        kind = op.truth_type or {"door": "door", "sliding": "door", "garage": "door", "window": "window",
                                 "opening": "opening"}[op.kind]
        rec = {"id": "", "width": r6(op.width), "center": rp(c), "type": kind}
        if op.kind in ("sliding", "garage"):
            rec["subtype"] = {"sliding": "sliding_door", "garage": "garage_door"}[op.kind]
        {"door": doors, "window": windows, "opening": openings}[kind].append(rec)
    for prefix, items in (("d", doors), ("win", windows), ("o", openings)):
        for i, rec in enumerate(items):
            rec["id"] = f"{prefix}_{lid}_{i + 1:03d}"
    walls = [{"id": f"w_{lid}_{i + 1:03d}", "start": rp(w.a), "end": rp(w.b), "thickness": r6(w.t),
              **({} if w.drawn else {"drawn": False})} for i, w in enumerate(plan.walls)]
    stairs = [{"id": s.id.replace("{L}", lid), "kind": s.kind, "center": rp(s.center), "risers": s.risers, **s.extra}
              for s in plan.stairs]
    return {"rooms": rooms, "doors": doors, "windows": windows, "openings": openings, "walls": walls, "stairs": stairs}


def reading_truth(project: FailureProject) -> dict:
    plans = {p.key: p for p in project.plans}
    per_level = {}
    for lv in project.levels:
        per_level[lv.id] = plan_truth(plans[lv.plan], lv.id)
    return {"project": project.name, "source": "synthetic", "status": "accepted",
            "units": "building metres (outer wall faces from the origin of each plan)",
            "levels": [{"id": lv.id, "label": lv.label, "elevation": r6(lv.elevation), "order": lv.order}
                       for lv in project.levels],
            "per_level": per_level, "failure_class": project.failure_class, "lesson": project.lesson,
            "summary": project.summary, **project.extra_truth,
            "drawing": {"file": DXF_FILE, "insunits": INSUNITS, "units_per_metre": CM,
                        "plans": [{"key": p.key, "origin_m": rp(p.origin), "title": p.title,
                                   "levels": [lv.id for lv in project.levels if lv.plan == p.key]}
                                  for p in project.plans]}}


def counts(truth: dict) -> dict:
    """Per-level counts of rooms, doors, windows and stairs (what the tests compare with the reader)."""
    return {lid: {k: len(v[k]) for k in ("rooms", "doors", "windows", "stairs")}
            for lid, v in truth["per_level"].items()}


def generate_failure_project(project: FailureProject, out_root: Path, results_dir: Optional[Path] = None) -> dict:
    """Write ``plan.dxf``, ``brief.yaml`` and ``truth/reading_truth.json`` (and the preview into ``results_dir``)."""
    project_dir = Path(out_root) / project.name
    (project_dir / "truth").mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = write_dxf(project, project_dir / DXF_FILE)
    (project_dir / "brief.yaml").write_text(yaml.safe_dump(project.brief, allow_unicode=True, sort_keys=False),
                                            encoding="utf-8")
    truth = reading_truth(project)
    (project_dir / TRUTH_FILE).write_text(json.dumps(truth, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if results_dir is not None:
        from wenart.synthetic.raster import preview_from_dxf
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        m = 200.0                       # 2 m of paper round the drawings; a window also decodes the Turkish letters
        preview_from_dxf(project_dir / DXF_FILE, Path(results_dir) / PREVIEW.format(name=project.name),
                         window=(x0 - m, y0 - m, x1 + m, y1 + m))
    return truth
