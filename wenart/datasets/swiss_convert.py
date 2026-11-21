"""Draw a converted Swiss Dwellings building as a Turkish-style DXF project (21 Nov 2026, user OK).

What: ``convert_building(floors, out_root, name)`` -> ``out_root/name/{plan.dxf, brief.yaml, truth/reading_truth.json,
ATTRIBUTION.md}`` (the layout and the truth: ``wenart.datasets.swiss_dwellings``; the style:
``wenart.datasets.style``). Per floor: walls as the outline of the wall union with the opening gaps cut, hatched;
columns on the column layer with a solid hatch; doors as a leaf and a 90 degree arc, swinging into the room (not into
a hall, a stair or a balcony), with a size tag; windows as three or four lines across the gap, an optional sill line
and a size tag outside; room labels and area texts; stairs with their treads and a walking line; sanitary and kitchen
pieces; exterior dimension chains (DIMENSION entities or exploded chains); an optional axis grid shared by every
floor; a title, a scale note and a level mark. The floors stand side by side on one sheet.

``python -m wenart.datasets.swiss_convert <geometries.csv[.gz]> <out_root> <building_id> [...]`` converts buildings.

Why: the dataset bench (``wenart.datasets.bench``) needs many real layouts drawn the way the user's offices draw.

How: building metres throughout; ``write_dxf`` scales to the style's units (cm, mm or paper metres at 1/50) and
writes R2010 with fixed metadata (byte-identical on every run).
"""
from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import ezdxf
import yaml
from shapely.geometry import Point
from shapely.ops import unary_union

from wenart.datasets import style as ST
from wenart.datasets import swiss_dwellings as SD
from wenart.datasets import turkish_profile as TP
from wenart.synthetic import failure_classes as FC

PLAN_SPACING_M = 14.0
CIRCULATION = {"hall", "stair", "balcony"}
SANITARY = {"TOILET", "BATHTUB", "SHOWER", "SINK", "WASHING_MACHINE"}
LAYER_COLOURS = {"wall": 7, "hatch": 8, "structure": 1, "door": 2, "window": 4, "stair": 6, "furniture": 9,
                 "sanitary": 9, "dimension": 3, "axis": 1, "text": 7, "room_label": 7, "area": 7, "door_tag": 2,
                 "window_tag": 4, "level": 1, "title": 7}


class NotOrthogonal(ValueError):
    """A building the bench does not convert: its walls are not on two orthogonal directions (or it has none)."""


@dataclass
class D:
    """One drawing primitive in building metres; ``role`` is a ``Style.layers`` key."""
    kind: str                     # line | poly | circle | arc | text | hatch | dim
    role: str
    pts: list = field(default_factory=list)
    closed: bool = False
    radius: float = 0.0
    angles: tuple = ()
    text: str = ""
    height: float = 0.0
    rot: float = 0.0
    align: str = "MIDDLE_CENTER"
    holes: list = field(default_factory=list)
    linetype: str = ""


def _from_fc(p: FC.Prim, role: str) -> D:
    return D(p.kind, role, list(p.pts), p.closed, p.radius, tuple(p.angles), p.text, p.height, 0.0, p.align)


class _PlanShim:
    """What ``failure_classes.door_prims`` needs of a plan: its walls by id."""

    def __init__(self, fl: SD.Floor):
        self._w = {w.id: w for w in fl.walls}

    def wall(self, wid: str) -> FC.Wall:
        return self._w[wid]


def _face_at(fl: SD.Floor, p) -> Optional[tuple]:
    pt = Point(p)
    return next((item for item in fl.faces if item[0].contains(pt)), None)


def _readable(deg: float) -> float:
    d = deg % 180.0
    return d - 180.0 if d > 90.0 + 1e-9 else d


def _polys(geom) -> list:
    polys = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    return sorted(polys, key=lambda q: (round(q.bounds[0], 4), round(q.bounds[1], 4)))


def _ring(geom) -> list:
    return FC._canon(list(geom.coords)[:-1])


def wall_prims(fl: SD.Floor, style: ST.Style) -> list:
    body = unary_union([w.rect() for w in fl.walls]).buffer(SD.CLOSE_M, join_style=2).buffer(-SD.CLOSE_M,
                                                                                            join_style=2)
    walls = {w.id: w for w in fl.walls}
    cuts = [walls[op.wall].rect(op.s - op.width / 2, op.s + op.width / 2, grow=0.002) for op in fl.openings]
    if cuts:
        body = body.difference(unary_union(cuts))
    out = []
    hatch_role = "wall" if style.hatch_on_wall_layer else "hatch"
    for p in _polys(body.simplify(0.0005)):
        ext, holes = _ring(p.exterior), [_ring(h) for h in p.interiors]
        out.append(D("poly", "wall", ext, closed=True))
        out += [D("poly", "wall", h, closed=True) for h in holes]
        out.append(D("hatch", hatch_role, ext, holes=holes))
    for c in fl.columns:
        ring = _ring(c.exterior)
        out += [D("poly", "structure", ring, closed=True), D("hatch", "structure", ring, text="SOLID")]
    return out


def opening_prims(fl: SD.Floor, style: ST.Style, rng: random.Random) -> list:
    shim = _PlanShim(fl)
    out = []
    for op in fl.openings:
        w = shim.wall(op.wall)
        h = w.t / 2
        ang = _readable(math.degrees(math.atan2(w.u[1], w.u[0])))
        plus = _face_at(fl, w.at(op.s, h + 0.3))
        minus = _face_at(fl, w.at(op.s, -h - 0.3))
        if op.kind == "door":
            sides = [(1, plus), (-1, minus)]
            rooms = [(sd, f) for sd, f in sides if f and f[2] not in CIRCULATION]
            if len(rooms) == 1:
                op.side = rooms[0][0]
            elif len(rooms) == 2:
                op.side = min(rooms, key=lambda q: q[1][0].area)[0]
            else:
                found = [q for q in sides if q[1]]
                op.side = min(found, key=lambda q: q[1][0].area)[0] if found else 1
            near_start = op.s - op.width / 2 < w.length - (op.s + op.width / 2)
            op.hinge = "start" if near_start != (rng.random() < 0.2) else "end"
            out += [_from_fc(p, "door") for p in FC.door_prims(shim, op)]
            tag_side = op.side
            h_cm = rng.choice((210, 220)) if getattr(op, "entrance", False) else 210
            texts = ST.tag_texts("door", int(round(op.width * 100)), h_cm, style)
            hh, role = style.heights["door_tag"], "door_tag"
        else:
            s0, s1 = op.s - op.width / 2, op.s + op.width / 2
            offs = (-h, 0.0, h) if style.window_lines == 3 else (-h, -h / 3, h / 3, h)
            out += [D("line", "window", [w.at(s0, o), w.at(s1, o)]) for o in offs]
            outside = -1 if plus else 1
            if style.window_sill:
                out.append(D("line", "window", [w.at(s0 - 0.05, outside * (h + 0.04)),
                                                w.at(s1 + 0.05, outside * (h + 0.04))]))
            tag_side = outside
            texts = ST.tag_texts("window", int(round(op.width * 100)), rng.choice((120, 140, 150, 160)), style)
            hh, role = style.heights["window_tag"], "window_tag"
        d0 = h + 0.12 + hh
        for k, t in enumerate(texts):
            out.append(D("text", role, [w.at(op.s, tag_side * (d0 + k * hh * 1.5))], text=t, height=hh, rot=ang))
    return out


def label_prims(fl: SD.Floor, style: ST.Style) -> list:
    out = []
    hl, ha = style.heights["room_label"], style.heights["area"]
    for f, text, _rtype, at in fl.faces:
        if not text or at is None:
            continue
        out.append(D("text", "room_label", [at], text=text, height=hl))
        below = (at[0], at[1] - hl * 0.8 - ha * 0.9)
        if not f.contains(Point(below)):
            below = (at[0], at[1] + hl * 0.8 + ha * 0.9)
        out.append(D("text", "area", [below], text=ST.area_text(f.area, style), height=ha))
    return out


def stair_prims(fl: SD.Floor) -> list:
    out = []
    polys = [g for st, g in fl.features if st == "STAIRS"]
    for p in polys:
        out.append(D("poly", "stair", _ring(p.simplify(0.002).exterior), closed=True))
        out += [D("line", "stair", [a, b]) for a, b in SD.stair_treads(p, polys)]
    for grp, _risers in SD.stair_groups(fl):
        r = SD._rect(grp if grp.geom_type == "Polygon" else grp.convex_hull)
        if r:                                       # the walking line with its arrow head, up the long axis
            cx, cy, ux, uy, L, _t = r
            a = (cx - ux * L * 0.4, cy - uy * L * 0.4)
            b = (cx + ux * L * 0.4, cy + uy * L * 0.4)
            nx, ny = -uy, ux
            out += [D("line", "stair", [a, b]),
                    D("line", "stair", [b, (b[0] - ux * 0.15 + nx * 0.08, b[1] - uy * 0.15 + ny * 0.08)]),
                    D("line", "stair", [b, (b[0] - ux * 0.15 - nx * 0.08, b[1] - uy * 0.15 - ny * 0.08)])]
    return out


def feature_prims(fl: SD.Floor) -> list:
    out = []
    for st, g in fl.features:
        if st == "STAIRS":
            continue
        role = "sanitary" if st in SANITARY else "furniture"
        out.append(D("poly", role, _ring(g.simplify(0.005).exterior), closed=True))
        r = SD._rect(g)
        if not r:
            continue
        cx, cy, ux, uy, L, t = r
        if st in ("TOILET", "SINK", "WASHING_MACHINE"):
            out.append(D("circle", role, [(cx, cy)], radius=max(0.05, min(L, t) * 0.3)))
        elif st == "BATHTUB":
            inner = g.buffer(-0.06, join_style=1)
            if inner.geom_type == "Polygon" and not inner.is_empty:
                out.append(D("poly", role, _ring(inner.simplify(0.005).exterior), closed=True))
        elif st in ("SHOWER", "ELEVATOR", "BUILT_IN_FURNITURE"):
            c = list(SD._rect_poly(r).exterior.coords)
            out += [D("line", role, [c[0], c[2]]), D("line", role, [c[1], c[3]])]
    return out


def level_mark_prims(fl: SD.Floor, z: float, style: ST.Style) -> list:
    cands = [x for x in fl.faces if x[1] and x[2] in ("hall", "living")] or [x for x in fl.faces if x[1]]
    if not cands:
        return []
    f, _t, _r, at = max(cands, key=lambda x: (x[2] == "hall", x[0].area))
    hl = style.heights["room_label"]
    for dx, dy in ((0.0, -2.6 * hl - 0.3), (0.0, 2.6 * hl + 0.3), (1.2, 0.0), (-1.2, 0.0)):
        p = (at[0] + dx, at[1] + dy)
        if f.buffer(-0.3).contains(Point(p)):
            break
    else:
        return []
    mx, y = p
    hz = style.heights["level"]
    return [D("poly", "level", [(mx, y), (mx - hz * 0.8, y + hz * 1.1), (mx + hz * 0.8, y + hz * 1.1)], closed=True),
            D("line", "level", [(mx - hz * 1.5, y), (mx + hz * 6.0, y)]),
            D("text", "level", [(mx + hz * 1.2, y + hz * 0.4)], text=ST.level_text(z, style), height=hz,
              align="BOTTOM_LEFT")]


def dim_points(fl: SD.Floor, side: str, bounds: tuple) -> list:
    """The first chain of one side: the building's extent and the edges of the openings in the walls whose outer face
    lies within 0.6 m of that side."""
    x0, y0, x1, y1 = bounds
    horiz = side in ("bottom", "top")
    pts = {round(x0, 3), round(x1, 3)} if horiz else {round(y0, 3), round(y1, 3)}
    walls = {w.id: w for w in fl.walls}
    for op in fl.openings:
        w = walls[op.wall]
        ux, uy = w.u
        if (horiz and abs(uy) > 1e-9) or (not horiz and abs(ux) > 1e-9):
            continue
        r = w.rect().bounds
        face = {"bottom": r[1] - y0, "top": y1 - r[3], "left": r[0] - x0, "right": x1 - r[2]}[side]
        if face > 0.6:
            continue
        a, b = w.at(op.s - op.width / 2), w.at(op.s + op.width / 2)
        pts |= {round(a[0], 3), round(b[0], 3)} if horiz else {round(a[1], 3), round(b[1], 3)}
    return sorted(pts)


def dim_chain_prims(points: list, side: str, line_at: float, style: ST.Style) -> list:
    """One chain: DIMENSION entities, or exploded (line, tick slashes, extension stubs, lengths in centimetres)."""
    horiz = side in ("bottom", "top")
    P = (lambda v: (v, line_at)) if horiz else (lambda v: (line_at, v))
    hd = style.heights["dimension"]
    if style.dims_as_entities:
        return [D("dim", "dimension", [P(v0), P(v1)], angles=(0.0 if horiz else 90.0,), height=hd)
                for v0, v1 in zip(points, points[1:]) if v1 - v0 >= 0.05]
    out = [D("line", "dimension", [P(points[0] - 0.15), P(points[-1] + 0.15)])]
    for v in points:
        q = P(v)
        out.append(D("line", "dimension", [(q[0] - 0.05, q[1] - 0.05), (q[0] + 0.05, q[1] + 0.05)]))
        out.append(D("line", "dimension", [q, (q[0], q[1] + 0.12) if horiz else (q[0] + 0.12, q[1])]))
    for v0, v1 in zip(points, points[1:]):
        if v1 - v0 < 0.05:
            continue
        mid = P((v0 + v1) / 2)
        at = (mid[0], mid[1] + hd * 0.6) if horiz else (mid[0] - hd * 0.6, mid[1])
        out.append(D("text", "dimension", [at], text=f"{round((v1 - v0) * 100):d}", height=hd,
                     rot=0.0 if horiz else 90.0, align="BOTTOM_CENTER"))
    return out


def axis_lines(ref: SD.Floor) -> tuple:
    """The axis grid of a building from its reference floor: the centre lines with >= 4 m of walls on them, at most 8
    per direction (numbered 1.. along x, lettered A.. along y)."""
    acc: dict = {"x": {}, "y": {}}
    for w in ref.walls:
        if w.truth.get("parapet") or w.length < 1.0:
            continue
        ux, uy = w.u
        if abs(uy) < 1e-9:
            acc["y"].setdefault(round(w.a[1] / 0.3), []).append((w.a[1], w.length))
        elif abs(ux) < 1e-9:
            acc["x"].setdefault(round(w.a[0] / 0.3), []).append((w.a[0], w.length))
    out = {}
    for d, groups in acc.items():
        lines = [(sum(v * L for v, L in g) / sum(L for _, L in g), sum(L for _, L in g)) for g in groups.values()]
        out[d] = sorted(round(v, 3) for v, L in sorted(lines, key=lambda q: -q[1])[:8] if L >= 4.0)
    return out["x"], out["y"]


def axis_prims(xs: list, ys: list, bounds: tuple) -> list:
    x0, y0, x1, y1 = bounds
    m, r = 2.6, 0.35
    out = []
    for i, x in enumerate(xs):
        out.append(D("line", "axis", [(x, y0 - m), (x, y1 + m)], linetype="CENTER"))
        for cy in (y0 - m - r, y1 + m + r):
            out += [D("circle", "axis", [(x, cy)], radius=r), D("text", "axis", [(x, cy)], text=str(i + 1),
                                                               height=0.3)]
    for i, y in enumerate(ys):
        out.append(D("line", "axis", [(x0 - m, y), (x1 + m, y)], linetype="CENTER"))
        for cx in (x0 - m - r, x1 + m + r):
            out += [D("circle", "axis", [(cx, y)], radius=r),
                    D("text", "axis", [(cx, y)], text=chr(ord("A") + i % 26), height=0.3)]
    return out


def floor_prims(fl: SD.Floor, order: int, z: float, style: ST.Style, rng: random.Random, axes: tuple,
                bounds: tuple) -> list:
    prims = wall_prims(fl, style) + opening_prims(fl, style, rng) + stair_prims(fl) + feature_prims(fl)
    prims += label_prims(fl, style) + level_mark_prims(fl, z, style)
    b = fl.union.bounds
    for side, at1, at2 in (("bottom", b[1] - 1.0, b[1] - 1.6), ("left", b[0] - 1.0, b[0] - 1.6),
                           ("top", b[3] + 1.0, b[3] + 1.6), ("right", b[2] + 1.0, b[2] + 1.6)):
        pts = dim_points(fl, side, b)
        if len(pts) > 2 and side in ("bottom", "left"):
            prims += dim_chain_prims(pts, side, at1, style)
        prims += dim_chain_prims([pts[0], pts[-1]], side, at2, style)
    if style.axes and (axes[0] or axes[1]):
        prims += axis_prims(axes[0], axes[1], bounds)
    ht = style.heights["title"]
    ty = b[1] - (3.8 if style.axes else 2.6) - ht
    title = ST.title_text(order, z, style)
    cx = (b[0] + b[2]) / 2
    prims.append(D("text", "title", [(cx, ty)], text=title, height=ht))
    half = len(title) * ht * 0.45
    prims.append(D("line", "title", [(cx - half, ty - ht * 0.9), (cx + half, ty - ht * 0.9)]))
    if not style.scale_inline:
        scale = style.scale_text if style.turkish_letters else ST.fold_ascii(style.scale_text).upper()
        prims.append(D("text", "title", [(cx, ty - ht * 2.2)], text=scale, height=ht * 0.6))
    return prims


def _layer(style: ST.Style, role: str) -> str:
    return style.layers.get(role) or style.layers.get("text") or "0"


def write_dxf(plans: list, style: ST.Style, path: Path) -> None:
    """``plans``: [(origin_m, prims)], drawn in the style's units on its layers, R2010, fixed metadata."""
    from ezdxf.enums import TextEntityAlignment

    upm = style.units_per_metre
    previous = getattr(ezdxf.options, FC._FIXED_META_OPTION)
    setattr(ezdxf.options, FC._FIXED_META_OPTION, True)
    try:
        doc = ezdxf.new("R2010", setup=True)
        doc.header["$INSUNITS"] = style.insunits
        doc.header["$MEASUREMENT"] = 1
        doc.header["$LTSCALE"] = 0.5 * upm
        for role in sorted({p.role for _, prims in plans for p in prims}):
            name = _layer(style, role)
            if name not in doc.layers:
                doc.layers.add(name, color=LAYER_COLOURS.get(role, 7))
        msp = doc.modelspace()
        for origin, prims in plans:
            def pt(q, o=origin):
                return (round((o[0] + q[0]) * upm, 4), round((o[1] + q[1]) * upm, 4))

            for p in prims:
                at = {"layer": _layer(style, p.role)}
                if p.linetype:
                    at["linetype"] = p.linetype
                if p.kind == "line":
                    msp.add_line(pt(p.pts[0]), pt(p.pts[1]), dxfattribs=at)
                elif p.kind == "poly":
                    msp.add_lwpolyline([pt(q) for q in p.pts], close=p.closed, dxfattribs=at)
                elif p.kind == "circle":
                    msp.add_circle(pt(p.pts[0]), round(p.radius * upm, 4), dxfattribs=at)
                elif p.kind == "arc":
                    msp.add_arc(pt(p.pts[0]), round(p.radius * upm, 4), round(p.angles[0], 4), round(p.angles[1], 4),
                                dxfattribs=at)
                elif p.kind == "text":
                    e = msp.add_text(p.text, height=round(p.height * upm, 4), rotation=round(p.rot, 3),
                                     dxfattribs=at)
                    e.set_placement(pt(p.pts[0]), align=TextEntityAlignment[p.align])
                elif p.kind == "hatch":
                    h = msp.add_hatch(color=LAYER_COLOURS.get(p.role, 8), dxfattribs=at)
                    pattern = p.text or style.hatch_pattern
                    if pattern == "SOLID":
                        h.set_solid_fill(color=1 if p.role == "structure" else 8)
                    else:
                        h.set_pattern_fill(pattern, scale=0.025 * upm)
                    h.paths.add_polyline_path([pt(q) for q in p.pts], is_closed=True,
                                              flags=ezdxf.const.BOUNDARY_PATH_EXTERNAL)
                    for hole in p.holes:
                        h.paths.add_polyline_path([pt(q) for q in hole], is_closed=True)
                elif p.kind == "dim":
                    a, b = pt(p.pts[0]), pt(p.pts[1])
                    hu = p.height * upm
                    msp.add_linear_dim(base=a, p1=a, p2=b, angle=p.angles[0], dimstyle="EZDXF",
                                       override={"dimtxt": hu, "dimasz": hu * 0.6, "dimtsz": hu * 0.5,
                                                 "dimlfac": 100.0 / upm, "dimexo": 0.0, "dimexe": hu * 0.5,
                                                 "dimdec": 0, "dimgap": hu * 0.3},
                                       dxfattribs=at).render()
                else:
                    raise ValueError(p.kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        doc.saveas(path)
    finally:
        setattr(ezdxf.options, FC._FIXED_META_OPTION, previous)


def convert_building(floors: dict, out_root: Path, name: str, profile: Optional[dict] = None,
                     seed: Optional[int] = None, max_floors: int = 4, overrides: Optional[dict] = None,
                     min_orthogonal: float = 0.0) -> dict:
    """``floors``: {floor_id: [csv rows]} of one building -> the project ``out_root/name``; returns its truth.
    ``overrides``: style fields set after sampling (a test of one convention, e.g. ``{"unit": "cm"}``);
    ``min_orthogonal``: the least share of wall length on the axes (``NotOrthogonal`` below it, nothing written)."""
    profile = profile or TP.load()
    fids = sorted(floors, key=lambda f: int(float(f)))[:max_floors]
    first = floors[fids[0]]
    bid = str(first[0]["building_id"]) if first else "0"
    if seed is None:
        seed = int(float(bid)) if bid.replace(".", "", 1).isdigit() else 0
    rng = random.Random(seed)
    style = ST.sample_style(profile, rng, seed)
    for k, v in (overrides or {}).items():
        setattr(style, k, v)
    layout = SD.building_layout({f: floors[f] for f in fids}, profile, style, rng)
    if layout["orthogonal_share"] < min_orthogonal:
        raise NotOrthogonal(f"building {bid}: {layout['orthogonal_share']:.0%} of the wall length on the axes")
    built = layout["floors"]
    if not built:
        raise NotOrthogonal(f"building {bid}: no walls")
    axes = axis_lines(built[0]) if built else ([], [])
    bx = [fl.union.bounds for fl in built]
    allb = (min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx))
    span = allb[2] - allb[0]
    plans = []
    for k, fl in enumerate(built):
        origin = (round(10.0 - allb[0] + k * (span + PLAN_SPACING_M), 3), round(10.0 - allb[1], 3))
        plans.append((origin, floor_prims(fl, k, k * style.storey_m, style, rng, axes, allb)))
    pdir = Path(out_root) / name
    (pdir / "truth").mkdir(parents=True, exist_ok=True)
    write_dxf(plans, style, pdir / FC.DXF_FILE)
    truth = SD.truth_of(name, layout, style)
    truth["drawing"] = {"file": FC.DXF_FILE, "insunits": style.insunits, "units_per_metre": style.units_per_metre,
                        "plans": [{"key": f"p{k}", "origin_m": [o[0], o[1]],
                                   "title": ST.title_text(k, k * style.storey_m, style), "levels": [f"L{k}"]}
                                  for k, (o, _p) in enumerate(plans)]}
    (pdir / FC.TRUTH_FILE).write_text(json.dumps(truth, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (pdir / "brief.yaml").write_text(yaml.safe_dump({"style": "Modern, oak floor, white walls, warm daylight"},
                                                    allow_unicode=True, sort_keys=False), encoding="utf-8")
    ds = SD.DATASET
    (pdir / "ATTRIBUTION.md").write_text(
        f"# Attribution\n\n- Source: {ds['name']} ({ds['url']}), building {bid}, floors "
        f"{', '.join(layout['floor_ids'])}.\n- Licence: {ds['licence']} ({ds['licence_url']}), declared by the "
        f"publisher; licence_flag: none; commercial-safe: yes.\n- {ds['attribution']}\n- Changes: rotated "
        f"{layout['rotation_deg']:.2f} degrees, walls regularised to rectangles on a 5 mm grid and merged, room labels "
        f"translated to Turkish, drafting style sampled from wenart/datasets/turkish_style.json.\n", encoding="utf-8")
    return truth


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    rows = SD.read_rows(Path(argv[0]))
    for bid in argv[2:]:
        truth = convert_building(rows[bid], Path(argv[1]), f"swiss-b{bid}")
        print(bid, {lid: {k: len(v) for k, v in lv.items()} for lid, lv in truth["per_level"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
