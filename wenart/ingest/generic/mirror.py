"""Mirrored halves check each other (3 Nov 2026; user: "Most of these drawings are mirrored it can help to fix the
issues", "use my vision and understanding to reinforce the decision").

What: ``consistency(walls, openings)`` -> ``(walls, openings, log)`` for a plan of two mirrored halves (the flats of
an apartment floor, a semi-detached pair: ``facade.mirror_axis``). Every wall is paired with its mirror twin (parallel,
the mirror of one's centre line within half the thicker wall of the other's, overlapping ``PAIR_OVERLAP`` of the
shorter); then:

1. *Thickness*: twins differing by more than ``THICK_DIFF_M`` (and ``THICK_RATIO``): the thicker one swallowed what
   stands along it (a kitchen counter, a lining) on its own side only; it takes its twin's mirrored centre line and
   thickness (``corrected_by_ai``, the twin as evidence). Its openings with no twin on the other side were read from
   that furniture (a counter's lines as windows): they go.
2. *Missing walls*: a drawn wall (evidence ``vector`` or ``derived``) at least ``MISSING_MIN_M`` long with no twin,
   whose mirror crosses no opening and lies in no wall, gets its mirror as an inferred wall (rule ``mirror_twin``).
3. *Openings*: a drawn opening whose mirror lies on a wall with only an inferred opening there, or none, gives that
   wall the mirrored opening (type, width; inferred, rule ``mirror_twin``; the inferred one it replaces goes).

The caller keeps the result only when more rooms pair as mirror images and no labelled room is left open.

Why: real09 (the user's mirrored flats): the right kitchen's wall read 0.76 m thick with three 'windows' (the counter
fused with the wall), its left twin 0.16 m with none; the right kitchen's balcony door, drawn on the left as a 1.45 m
door, was an unverified window on the inferred facade wall.

How: pure geometry on ``WallItem`` / ``OpeningItem`` (page metres).
"""
from __future__ import annotations

import copy
import math
from typing import Optional

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from wenart.ingest.generic import topology as TP

PAIR_OVERLAP = 0.5
PAIR_ANGLE = 0.05               # |sin| of the angle between twins
THICK_DIFF_M = 0.15
THICK_RATIO = 1.8
MISSING_MIN_M = 0.6
OPENING_TOL_M = 0.25            # an opening's twin: its centre within this of the mirrored centre
SPAN_OVERLAP_M = 0.05           # a copied opening may overlap an opening of its host wall by at most this
FACE_TOL_M = 0.03               # a drawn line on a wall face: within this (or 15 % of the thickness) of the face line
FACE_COVER = 0.9                # a face drawn along this share of a copy's span is solid wall there
AXIS_CLEAR_M = 0.3              # walls on the axis (the party wall) are their own twins
INNER_CLEAR_M = 0.05            # a wall this close to the building's outline is the shell, not the halves' layout
CORE_KEEP_OUT_M = 3.0           # no mirror fix within this of a lift label (core.CORE_KEEP_OUT_M, the same value)
MIRROR_MAX_NEW_WALLS = 3        # core.MIRROR_MAX_NEW_WALLS (the same value): the halves differ by at most this many walls
RULE = "mirror_twin"


def _mirror(p, axis):
    return (2.0 * axis[1] - p[0], p[1]) if axis[0] == "x" else (p[0], 2.0 * axis[1] - p[1])


def _seg(w):
    return tuple(w.start), tuple(w.end)


def _dir(a, b):
    L = math.dist(a, b)
    return ((b[0] - a[0]) / L, (b[1] - a[1]) / L) if L > 1e-9 else (1.0, 0.0)


def _on_axis(w, axis) -> bool:
    a, b = _seg(w)
    k = 0 if axis[0] == "x" else 1
    return abs(a[k] - axis[1]) <= AXIS_CLEAR_M and abs(b[k] - axis[1]) <= AXIS_CLEAR_M


def _overlap(a1, b1, a2, b2) -> float:
    """The share of the shorter segment the other covers along their common direction."""
    u = _dir(a1, b1)
    t = lambda p: (p[0] - a1[0]) * u[0] + (p[1] - a1[1]) * u[1]     # noqa: E731
    s1 = sorted((t(a1), t(b1)))
    s2 = sorted((t(a2), t(b2)))
    inter = min(s1[1], s2[1]) - max(s1[0], s2[0])
    shorter = min(s1[1] - s1[0], s2[1] - s2[0])
    return max(0.0, inter) / max(shorter, 1e-9)


def pair_walls(walls: list, axis) -> dict:
    """``{wall index: twin index}`` (the module docstring); walls on the axis pair with themselves."""
    out = {}
    for i, w in enumerate(walls):
        if _on_axis(w, axis):
            out[i] = i
            continue
        a, b = _seg(w)
        ma, mb = _mirror(a, axis), _mirror(b, axis)
        # a wall across the axis is its own twin (real09: the 0.46 m wall along the whole back of both flats)
        u0 = _dir(a, b)
        if abs(-(ma[0] - a[0]) * u0[1] + (ma[1] - a[1]) * u0[0]) <= float(w.thickness) / 2.0 \
                and _overlap(a, b, ma, mb) >= PAIR_OVERLAP:
            out[i] = i
            continue
        u = _dir(ma, mb)
        mline = LineString([ma, mb])
        best = None
        for j, v in enumerate(walls):
            if j == i:
                continue
            c, d = _seg(v)
            uv = _dir(c, d)
            if abs(u[0] * uv[1] - u[1] * uv[0]) > PAIR_ANGLE:
                continue
            off = LineString([c, d]).distance(Point((ma[0] + mb[0]) / 2.0, (ma[1] + mb[1]) / 2.0))
            perp = abs(-(c[0] - ma[0]) * u[1] + (c[1] - ma[1]) * u[0])
            if perp > max(float(w.thickness), float(v.thickness)) / 2.0 + 0.05:
                continue
            ov = _overlap(ma, mb, c, d)
            if ov < PAIR_OVERLAP:
                continue
            score = (perp, -ov, off)
            if best is None or score < best[0]:
                best = (score, j)
        if best is not None and mline.length > 0:
            out[i] = best[1]
    return out


def _drawn(item) -> bool:
    ev = item.evidence if isinstance(item.evidence, dict) else {}
    return ev.get("method") in ("vector", "derived") and not getattr(item, "inferred", False)


def _inferred(item) -> bool:
    ev = item.evidence if isinstance(item.evidence, dict) else {}
    return bool(getattr(item, "inferred", False)) or ev.get("method") == "inferred" or \
        getattr(item, "status", "verified") == "unverified" and ev.get("rule") in ("glazed_facade", "wide_gap")


def _on_wall(o, w) -> bool:
    a, b = _seg(w)
    return LineString([a, b]).distance(Point(o.center)) <= float(w.thickness) / 2.0 + 0.05


def core_keep_out(labels: list):
    """The building's core: a disc of ``CORE_KEEP_OUT_M`` around every lift label (3 Nov 2026, real10: the lift and the
    stair are not mirrored), or None."""
    from wenart.sheets import register as RG_
    from wenart.sheets import titles as TI_

    lifts = [Point(b.anchor).buffer(CORE_KEEP_OUT_M) for b in labels or []
             if RG_.LIFT_RE.search(TI_.fold(str(getattr(b, "name", "") or "")))]
    return unary_union(lifts) if lifts else None


def inner_walls(walls: list, openings: list = (), labels: list = (), level_id=None, bw=None) -> list:
    """The walls of the building that stand more than ``INNER_CLEAR_M`` from the building's outline: the layout inside
    the shell. The building walls are ``topology.split_plot``'s, less the walls that bound only an enclosure (a face
    with another face inside its ring: the garden inside a garden wall all round the house, which ``split_plot``
    keeps as building because the house's labels lie inside its ring); the outline is the convex hull of the rest
    (a terrace parapet joined to the house is on it)."""
    from shapely.geometry import Polygon

    if bw is None:
        bw = TP.split_plot(list(walls), list(openings or []), list(labels or []), level_id=level_id)[0] or list(walls)
    faces = TP.faces(bw, list(openings or []))
    rooms = [f for f in faces if not any(Polygon(f.exterior).contains(g.representative_point())
                                         for g in faces if g is not f)]
    if rooms and len(rooms) < len(faces):
        polys = [(w, TP.wall_polygon(w)) for w in bw]
        bw = [w for w, pg in polys if any(pg.distance(f) <= INNER_CLEAR_M for f in rooms)] or bw
    # the convex hull, not the closed outline: early in the reading a flat may still be open to its facade (real09's
    # unlabelled flat before its facade of frames is closed), and its walls would all lie on a closed outline
    outline = unary_union([TP.wall_polygon(w) for w in bw]).convex_hull
    if outline.is_empty:
        return []
    ring = outline.boundary
    return [w for w in bw if TP.wall_polygon(w).distance(ring) > INNER_CLEAR_M]


def mirror_share(walls: list, axis) -> float:
    """The share of the walls' area that overlaps its mirror about ``axis`` (``facade.mirror_axis``'s measure)."""
    from shapely import affinity

    from wenart.ingest.generic import facade as FC

    if not walls:
        return 0.0
    u = unary_union([TP.wall_polygon(w) for w in walls])
    if u.area <= 0:
        return 0.0
    m = affinity.scale(u, xfact=-1.0 if axis[0] == "x" else 1.0, yfact=-1.0 if axis[0] == "y" else 1.0,
                       origin=(axis[1], 0.0) if axis[0] == "x" else (0.0, axis[1]))
    return u.intersection(m.buffer(FC.MIRROR_NEAR_M, join_style=2)).area / u.area


def centre_coverage(w, others: list, axis) -> float:
    """The share of ``w``'s centre line whose mirror about ``axis`` runs on the centre line of another wall of
    ``others``: parallel, within half the thicker wall (+ 0.05 m) of it. Measured on centre lines, not areas, so a wall
    read too thick (a counter fused with it, its centre shifted) still pairs with its twin."""
    a, b = _seg(w)
    ma, mb = _mirror(a, axis), _mirror(b, axis)
    L = math.dist(ma, mb)
    if L <= 1e-9:
        return 0.0
    u = _dir(ma, mb)
    spans = []
    for v in others:
        if v is w:
            continue
        c, d = _seg(v)
        uv = _dir(c, d)
        if abs(u[0] * uv[1] - u[1] * uv[0]) > PAIR_ANGLE:
            continue
        tol = max(float(w.thickness), float(v.thickness)) / 2.0 + 0.05
        if any(abs(-(p[0] - ma[0]) * u[1] + (p[1] - ma[1]) * u[0]) > tol for p in (c, d)):
            continue
        t0, t1 = sorted(((p[0] - ma[0]) * u[0] + (p[1] - ma[1]) * u[1]) for p in (c, d))
        lo, hi = max(t0, 0.0), min(t1, L)
        if hi > lo:
            spans.append((lo, hi))
    covered, cur = 0.0, None
    for lo, hi in sorted(spans):
        if cur is None or lo > cur[1]:
            covered += (cur[1] - cur[0]) if cur else 0.0
            cur = [lo, hi]
        else:
            cur[1] = max(cur[1], hi)
    covered += (cur[1] - cur[0]) if cur else 0.0
    return covered / L


# Room types that may stand for each other in mirrored twins (5 Nov 2026 review: 'Banyo' and 'Banyo / WC', 'Mutfak' and
# 'Salon + Açık Mutfak' are the same rooms of two flats)
ROOM_FAMILIES = {"bathroom": "wet", "wc": "wet", "shower": "wet", "kitchen": "day", "living": "day", "dining": "day"}
LABEL_DISAGREE_MIN = 2          # at least this many mirrored labelled room pairs of different rooms refuse the halves


def label_pairs(walls: list, openings: list, axis, labels: list) -> tuple[int, int]:
    """``(agree, disagree)``: of the faces that pair with the mirror of another face (intersection over union >= 0.9)
    and both hold a room label (``labels``: LabelBlocks; site areas and labels of no room type left out), the pairs
    whose labels share a room family (``ROOM_FAMILIES``: wet rooms one family, kitchen, living and dining another) and
    those whose labels share none. A face that is its own mirror (it straddles the axis) is no pair."""
    from shapely import affinity

    named = [(Point(b.anchor), ROOM_FAMILIES.get(b.room_type, b.room_type)) for b in labels or []
             if not getattr(b, "exterior", False) and getattr(b, "room_type", "other") not in ("other", "unknown")]
    if not named:
        return 0, 0
    faces = TP.faces(walls, openings)
    types = [{t for p, t in named if f.contains(p)} for f in faces]
    agree = disagree = 0
    seen = set()
    for i, f in enumerate(faces):
        if not types[i] or i in seen:
            continue
        m = affinity.scale(f, xfact=-1.0 if axis[0] == "x" else 1.0, yfact=-1.0 if axis[0] == "y" else 1.0,
                           origin=(axis[1], 0.0) if axis[0] == "x" else (0.0, axis[1]))
        for j, g in enumerate(faces):
            u = m.union(g).area
            if u <= 0 or m.intersection(g).area / u < 0.9:
                continue
            if j != i and types[j]:
                seen.update((i, j))
                if types[i] & types[j]:
                    agree += 1
                else:
                    disagree += 1
            break
    return agree, disagree


MISSING_EVIDENCE = 2            # a wall left out of the share as missing needs this many walls that do pair


def halves(walls: list, openings: list = (), labels: list = (), level_id=None,
           min_share: Optional[float] = None) -> dict:
    """The decision whether a plan is two mirrored halves (the one decision every mirror rule of a level uses):
    ``{"axis": (axis, value) or None, "note": why not or None, "share", "walls_inside", "self_mirror", "paired",
    "missing", "labels": [agree, disagree]}``.

    5 Nov 2026 (a single house in a symmetric shell, synthetic-06, -07, -19 and the outline fixture: the outer walls and
    the walls across the whole plan made ``facade.mirror_axis`` overlap ~0.95 on their own, and the mirror fixes copied
    walls, doors and windows of one room into another; review of 5 Nov: a garden wall or a terrace parapet, walls on the
    axis and one defective wall must not decide it). The plan is two mirrored halves when

    1. ``facade.mirror_axis`` of all walls reaches ``min_share`` (``MIRROR_FIX_SHARE``), as before;
    2. the walls inside the building's shell (``inner_walls``: plot walls and the outline left out), away from the core
       (``core_keep_out``) and not their own mirror (``pair_walls`` i -> i: a wall on the axis or across it pairs with
       itself in any layout), pair with a mirror twin: at least ``MISSING_EVIDENCE`` of them, and their centre lines
       (``centre_coverage``) are covered by ``min_share``; up to ``MIRROR_MAX_NEW_WALLS`` walls with no twin (the walls
       the missing step copies) are left out of the share while at least ``MISSING_EVIDENCE`` times as many pair;
    3. the labelled rooms that mirror each other are the same rooms (``label_pairs``): at least ``LABEL_DISAGREE_MIN``
       pairs of different rooms, and more than agree, refuse (synthetic-07's ground floor: a symmetric layout of Banyo
       below and Hol above). Mirrored flats name their twins alike (real02, real10), or one half only (real09)."""
    from wenart.ingest.generic import facade as FC

    share = FC.MIRROR_FIX_SHARE if min_share is None else min_share
    out = {"axis": None, "note": None, "share": None, "walls_inside": 0, "self_mirror": 0, "paired": 0, "missing": 0,
           "labels": None}
    axis = FC.mirror_axis(walls, share)
    if axis is None:
        return out
    keep_out = core_keep_out(labels)
    bw = TP.split_plot(list(walls), list(openings or []), list(labels or []), level_id=level_id)[0] or list(walls)
    inner = [w for w in inner_walls(walls, openings, labels, level_id, bw=bw)
             if keep_out is None or not TP.wall_polygon(w).intersects(keep_out)]
    pairs = pair_walls(inner, axis)
    others = [w for i, w in enumerate(inner) if pairs.get(i) != i]
    cover = [(w, centre_coverage(w, bw, axis), math.dist(*_seg(w))) for w in others]
    paired = [c for c in cover if c[1] >= PAIR_OVERLAP]
    lonely = sorted((c for c in cover if c[1] < PAIR_OVERLAP), key=lambda c: c[1] * c[2] - c[2])
    n_missing = min(MIRROR_MAX_NEW_WALLS, len(lonely), len(paired) // MISSING_EVIDENCE)
    counted = paired + lonely[n_missing:]
    total = sum(c[2] for c in counted)
    got = sum(c[1] * c[2] for c in counted) / total if total > 0 else 0.0
    out.update(share=round(got, 3), walls_inside=len(inner), self_mirror=len(inner) - len(others), paired=len(paired),
               missing=n_missing)
    where = f"{axis[0]} = {axis[1]:.2f}"
    if len(paired) < MISSING_EVIDENCE or got < share:
        out["note"] = (f"the shell is symmetric about {where} but of the {len(inner)} walls inside it "
                       f"({len(inner) - len(others)} their own mirror, left out) {len(paired)} pair with a mirror twin "
                       f"and their centre lines are {got:.0%} covered (< {share:.0%}, {n_missing} missing allowed): one "
                       f"layout, not two mirrored halves")
        return out
    if labels:
        agree, disagree = label_pairs(walls, list(openings or []), axis, labels)
        out["labels"] = [agree, disagree]
        if disagree >= LABEL_DISAGREE_MIN and disagree > agree:
            out["note"] = (f"the layout is symmetric about {where} but {disagree} of its {agree + disagree} mirrored "
                           f"labelled room pairs are different rooms: one dwelling, not two mirrored halves")
            return out
    out["axis"] = axis
    return out


def halves_axis(walls: list, min_share: Optional[float] = None, openings: Optional[list] = None,
                labels: Optional[list] = None, level_id=None) -> tuple[Optional[tuple], Optional[str]]:
    """``(axis, note)`` of ``halves``: the axis of a plan of two mirrored halves, or None with the reason."""
    h = halves(walls, openings or [], labels or [], level_id, min_share)
    return h["axis"], h["note"]


STEPS = ("thickness", "inferred", "missing", "openings")


def _span(host, center, width) -> tuple[float, float]:
    a, b = _seg(host)
    u = _dir(a, b)
    c = (center[0] - a[0]) * u[0] + (center[1] - a[1]) * u[1]
    return c - width / 2.0, c + width / 2.0


def _own_lines(host, strokes: list) -> list:
    """The strokes the host wall was read from (its evidence entity: ``LINE:1A,LINE:1B``, ranges ``path:3-5``)."""
    import re

    ids = set()
    for part in str(host.entity or "").split(","):
        head, _, tail = part.partition(":")
        m = re.fullmatch(r"(\d+)-(\d+)", tail)
        if m:
            ids.update(f"{head}:{k}" for k in range(int(m.group(1)), int(m.group(2)) + 1))
        elif part:
            ids.add(part)
    return [st for st in strokes or [] if str(getattr(st, "id", "")) in ids
            or any(str(getattr(st, "id", "")).startswith(i + sep) for i in ids for sep in ("/", "#"))]


def solid_span(host, center, width, strokes: list) -> bool:
    """True when the drawing has solid wall over the span of an opening of ``width`` at ``center`` on ``host``: the
    lines the wall was read from (``_own_lines``: its drawn face lines, not frames, furniture or hatch of other things)
    run parallel along both of its faces (``FACE_TOL_M``) over ``FACE_COVER`` of the span. A real gap breaks the face
    lines at its jambs; an inferred wall has no drawn lines and is never solid (5 Nov 2026, real11 L-1: a 1.5 m
    opening copied onto the outer wall where the drawing has solid wall)."""
    if _inferred(host):                     # an inferred wall (room outlines name drawn strokes as its entity)
        return False
    strokes = _own_lines(host, strokes)
    if not strokes:
        return False
    a, b = _seg(host)
    u = _dir(a, b)
    n = (-u[1], u[0])
    lo, hi = _span(host, center, width)
    t = float(host.thickness)
    tol = max(FACE_TOL_M, 0.15 * t)
    for side in (-1.0, 1.0):
        off = side * t / 2.0
        spans = []
        for st in strokes or []:
            pts = getattr(st, "pts", None) or []
            for p, q in zip(pts, pts[1:]):
                d = _dir(p, q)
                if abs(u[0] * d[1] - u[1] * d[0]) > PAIR_ANGLE:
                    continue
                if any(abs((r[0] - a[0]) * n[0] + (r[1] - a[1]) * n[1] - off) > tol for r in (p, q)):
                    continue
                s0, s1 = sorted(((r[0] - a[0]) * u[0] + (r[1] - a[1]) * u[1]) for r in (p, q))
                if min(s1, hi) > max(s0, lo):
                    spans.append((max(s0, lo), min(s1, hi)))
        covered, cur = 0.0, None
        for s0, s1 in sorted(spans):
            if cur is None or s0 > cur[1]:
                covered += (cur[1] - cur[0]) if cur else 0.0
                cur = [s0, s1]
            else:
                cur[1] = max(cur[1], s1)
        covered += (cur[1] - cur[0]) if cur else 0.0
        if covered < FACE_COVER * (hi - lo):
            return False
    return True


def consistency(walls: list, openings: list, axis=None, steps=STEPS, keep_out=None,
                strokes: Optional[list] = None) -> Optional[tuple[list, list, list]]:
    """``(walls, openings, log)`` with the mirror fixes (the module docstring) of the given ``steps`` (``STEPS``), or
    None (no mirror axis or nothing to fix). ``keep_out``: a shapely geometry no copied wall or opening may touch (the
    building's core: its lift and stair are not mirrored). ``strokes``: the page's lines; a copied opening never lands
    on drawn solid wall (``solid_span``) nor on a span of its host wall that already holds an opening; each refusal is
    a log line starting with ``refused``. The inputs are not changed."""
    from wenart.ingest.generic import facade as FC
    from wenart.ingest.model import OpeningItem, WallItem

    axis = axis or FC.mirror_axis(walls, FC.MIRROR_FIX_SHARE)
    if axis is None:
        return None
    walls = [copy.copy(w) for w in walls]
    openings = list(openings)
    pairs = pair_walls(walls, axis)
    log: list[str] = []
    drop_openings: set = set()
    # 1. thickness
    for i, j in (pairs.items() if "thickness" in steps else ()):
        if i == j:
            continue
        w, v = walls[i], walls[j]
        tw, tv = float(w.thickness), float(v.thickness)
        if keep_out is not None and (TP.wall_polygon(w).intersects(keep_out) or TP.wall_polygon(v).intersects(keep_out)):
            continue                 # 3 Nov 2026 (real10 L-1): the core (lift and stair) is no mirror of anything
        if tw - tv > THICK_DIFF_M and tw >= THICK_RATIO * tv and _drawn(v):
            ma, mb = _mirror(v.start, axis), _mirror(v.end, axis)
            before = (tuple(w.start), tuple(w.end), tw)
            ev = dict(w.evidence or {})
            ev.update(corrected_by_ai=True, rule=RULE,
                      reason=(f"its mirror twin across the plan's axis ({axis[0]} = {axis[1]:.2f}) is {tv:.2f} m thick: "
                              f"this wall swallowed what stands along it on its side (a counter, a lining)"),
                      before={"start": list(before[0]), "end": list(before[1]), "thickness": round(tw, 3)})
            w.start, w.end, w.thickness, w.evidence = (round(ma[0], 4), round(ma[1], 4)), \
                (round(mb[0], 4), round(mb[1], 4)), tv, ev
            # the openings on it with no twin on the other side were read from that furniture
            for k, o in enumerate(openings):
                if not _on_wall(o, WallItem(start=before[0], end=before[1], thickness=tw, box=[], entity="",
                                            evidence={})):
                    continue
                mc = _mirror(o.center, axis)
                twin = any(_on_wall(p, v) and math.dist(p.center, mc) <= OPENING_TOL_M + o.width / 2.0
                           for p in openings if p is not o)
                if not twin:
                    drop_openings.add(k)
                    log.append(f"{o.kind} {o.entity} ({o.width:.2f} m) on wall {w.entity} dropped: no twin on its mirror "
                               f"twin wall (read from what stood along the wall)")
            log.append(f"wall {w.entity}: {tw:.2f} m -> {tv:.2f} m thick, on the mirror of {v.entity} (its twin)")
    openings = [o for k, o in enumerate(openings) if k not in drop_openings]
    # 1b. an inferred wall whose twin is drawn takes the twin's mirrored line and thickness over its own span (real09:
    # the right kitchen's inferred facade wall stood 0.22 m off the line of the drawn wall its left twin stands on);
    # its openings move onto that line
    for i, j in (pairs.items() if "inferred" in steps else ()):
        if i == j:
            continue
        w, v = walls[i], walls[j]
        if not _inferred(w) or not _drawn(v):
            continue
        if keep_out is not None and (TP.wall_polygon(w).intersects(keep_out) or TP.wall_polygon(v).intersects(keep_out)):
            continue
        ma, mb = _mirror(v.start, axis), _mirror(v.end, axis)
        u = _dir(ma, mb)
        proj = lambda p: (ma[0] + u[0] * ((p[0] - ma[0]) * u[0] + (p[1] - ma[1]) * u[1]),       # noqa: E731
                          ma[1] + u[1] * ((p[0] - ma[0]) * u[0] + (p[1] - ma[1]) * u[1]))
        ns, ne = proj(tuple(w.start)), proj(tuple(w.end))
        shift = math.dist(ns, tuple(w.start))
        if shift <= 0.02 and abs(float(w.thickness) - float(v.thickness)) <= 0.02:
            continue
        old_line = (tuple(w.start), tuple(w.end), float(w.thickness))
        for o in openings:
            if _on_wall(o, w):
                o.center = tuple(round(c, 4) for c in proj(tuple(o.center)))
        ev = dict(w.evidence or {})
        ev.update(rule=RULE, reason=(f"inferred on the line of its drawn mirror twin {v.entity} across the plan's axis "
                                     f"({axis[0]} = {axis[1]:.2f})"))
        w.start, w.end = tuple(round(c, 4) for c in ns), tuple(round(c, 4) for c in ne)
        w.thickness, w.evidence = float(v.thickness), ev
        log.append(f"inferred wall {w.entity}: onto the line of its drawn twin {v.entity} ({shift:.2f} m, "
                   f"{old_line[2]:.2f} -> {float(v.thickness):.2f} m thick)")
    # 2. missing walls
    polys = unary_union([TP.wall_polygon(w) for w in walls])
    added = []
    for i, w in (enumerate(list(walls)) if "missing" in steps else ()):
        if i in pairs or not _drawn(w) or math.dist(w.start, w.end) < MISSING_MIN_M or _on_axis(w, axis):
            continue
        ma, mb = _mirror(w.start, axis), _mirror(w.end, axis)
        m = WallItem(start=(round(ma[0], 4), round(ma[1], 4)), end=(round(mb[0], 4), round(mb[1], 4)),
                     thickness=float(w.thickness), box=list(w.box), entity=f"inferred:{RULE}:{len(added) + 1}",
                     evidence={}, exterior=bool(getattr(w, "exterior", False)), status="unverified", inferred=True)
        mp = TP.wall_polygon(m)
        if keep_out is not None and mp.intersects(keep_out):
            continue                                        # the core (lift and stair) is not mirrored
        if mp.intersection(polys).area >= 0.5 * mp.area:
            continue                                        # it lies in walls already (read in pieces)
        if any(TP.opening_polygon(o, walls) is not None and TP.opening_polygon(o, walls).intersects(mp)
               for o in openings):
            continue                                        # it would close a drawn opening
        ev = dict(w.evidence or {})
        ev.update(method="inferred", confidence=0.6, rule=RULE,
                  reason=f"the mirror twin of wall {w.entity} across the plan's axis ({axis[0]} = {axis[1]:.2f}); "
                         f"the drawing's other half shows it, this half's lines were not read as a wall")
        m.evidence = ev
        added.append(m)
        log.append(f"wall {m.entity} inferred: the mirror of {w.entity} ({math.dist(w.start, w.end):.2f} m)")
    walls += added
    # 3. openings: a drawn opening's twin (step "openings")
    new_open = []
    replace: set = set()
    for o in (openings if "openings" in steps else ()):
        if not _drawn(o) or getattr(o, "virtual", False):
            continue
        mc = _mirror(o.center, axis)
        if math.dist(mc, o.center) <= OPENING_TOL_M + o.width / 2.0:
            continue                                        # it is its own twin (the twin match's radius below)
        if keep_out is not None and keep_out.distance(Point(mc)) <= o.width / 2.0:
            continue                                        # the core (lift and stair) is not mirrored
        host = next((w for w in walls if _on_wall(OpeningItem(kind="", width=0, center=mc, rotation_deg=0, box=[],
                                                               entity="", evidence={}), w)), None)
        if host is None:
            continue
        here = [k for k, p in enumerate(openings) if p is not o and math.dist(p.center, mc) <= OPENING_TOL_M + o.width / 2]
        if any(_drawn(openings[k]) for k in here):
            continue                                        # the twin is drawn: nothing to fix
        if any(openings[k].kind == o.kind for k in here):
            continue                                        # an inferred twin of the same kind
        # 5 Nov 2026 (real11 L-1: a 1.5 m copy over the drawn window of the outer wall and over drawn solid wall)
        lo, hi = _span(host, mc, o.width)

        def overlaps(p):
            plo, phi = _span(host, p.center, p.width)
            return _on_wall(p, host) and min(hi, phi) - max(lo, plo) > SPAN_OVERLAP_M

        # a drawn opening of the host wall over the span refuses the copy; an inferred one there is replaced, as at
        # the centre (real09: the right kitchen's balcony door over the window the facade rule guessed)
        over = [k for k, p in enumerate(openings) if k not in here and p is not o and overlaps(p)]
        clash = next((openings[k] for k in over if _drawn(openings[k])), None)
        clash = clash or next((p for p in new_open if overlaps(p)), None)
        if clash is None:
            here = list(here) + over
        if clash is not None:
            log.append(f"refused: the mirror of {o.kind} {o.entity} ({o.width:.2f} m) would overlap {clash.kind} "
                       f"{clash.entity} ({clash.width:.2f} m) on its wall {host.entity}")
            continue
        if strokes and solid_span(host, mc, o.width, strokes):
            log.append(f"refused: the mirror of {o.kind} {o.entity} ({o.width:.2f} m) would land on drawn solid wall "
                       f"({host.entity}: both faces drawn along the span)")
            continue
        replace.update(here)
        ev = dict(o.evidence or {})
        ev.update(method="inferred", confidence=0.6, rule=RULE,
                  reason=f"the mirror twin of {o.kind} {o.entity} ({o.width:.2f} m) across the plan's axis "
                         f"({axis[0]} = {axis[1]:.2f})" + (" (replaces an inferred opening of an unknown kind)" if here
                                                          else ""))
        rot = (180.0 - o.rotation_deg) if axis[0] == "x" else -o.rotation_deg
        n = copy.copy(o)
        n.center, n.rotation_deg, n.evidence, n.status = (round(mc[0], 4), round(mc[1], 4)), rot, ev, "unverified"
        n.entity = f"inferred:{RULE}:{o.entity}"
        if o.swing_point is not None:
            n.swing_point = _mirror(o.swing_point, axis)
        new_open.append(n)
        log.append(f"{o.kind} {n.entity} ({o.width:.2f} m) inferred: the mirror of {o.entity}"
                   + (f", replacing {len(here)} inferred opening(s)" if here else ""))
    openings = [p for k, p in enumerate(openings) if k not in replace] + new_open
    if not log:
        return None
    return walls, openings, log


def mirrored_face_pairs(walls: list, openings: list, axis) -> int:
    """How many faces of the walls pair with the mirror of another (or their own) face (intersection over union
    >= 0.9): the measure the caller keeps a fix by."""
    from shapely import affinity

    faces = TP.faces(walls, openings)
    n = 0
    for f in faces:
        m = affinity.scale(f, xfact=-1.0 if axis[0] == "x" else 1.0, yfact=-1.0 if axis[0] == "y" else 1.0,
                           origin=(axis[1], 0.0) if axis[0] == "x" else (0.0, axis[1]))
        for g in faces:
            u = m.union(g).area
            if u > 0 and m.intersection(g).area / u >= 0.9:
                n += 1
                break
    return n
