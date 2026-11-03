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
AXIS_CLEAR_M = 0.3              # walls on the axis (the party wall) are their own twins
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


STEPS = ("thickness", "inferred", "missing", "openings")


def consistency(walls: list, openings: list, axis=None, steps=STEPS, keep_out=None) -> Optional[tuple[list, list, list]]:
    """``(walls, openings, log)`` with the mirror fixes (the module docstring) of the given ``steps`` (``STEPS``), or
    None (no mirror axis or nothing to fix). ``keep_out``: a shapely geometry no copied wall or opening may touch (the
    building's core: its lift and stair are not mirrored). The inputs are not changed."""
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
