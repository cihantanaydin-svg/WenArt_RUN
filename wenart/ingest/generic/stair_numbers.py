"""Stairs read from their numbered treads (3 Nov 2026).

What: ``chains(texts)`` -> the runs of tread numbers a plan writes on a stair (1, 2, 3 ... N; small integer texts,
each the next within ``STEP_M``; one missing number bridged); ``stair_of(chain, strokes)`` -> the stair they describe
(page metres): its straight arms (the runs of numbers in one direction) as flights, measured on the tread lines the
numbers stand on, the turn between two arms as the landing holding the winders (its numbers), the rise from 1 to N
(drawn, not assumed); ``apply(pieces, cands, texts, strokes, ...)`` adds each numbered stair no stair piece already
holds and drops the candidates and pieces inside it (its parts).

Why: real09 (user: "each duplex flat has its inner stair (winders 1-17)"): the duplex flats' U stairs with winders
have four straight treads per arm, fewer than the stair rule's five evenly spaced lines (``symbols.STAIR_MIN_TREADS``);
they were read as two untyped 3.49 x 1.46 m boxes. Their treads are numbered 1-16, which says what they are, how many
risers they have and which way they rise.

How: pure geometry on the page's texts and strokes (page metres). Straight stairs and stairs of two arms (U and L, the
turn between them a landing holding its winders) are built; other shapes are listed (``notes``) and left to the stair
rule.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B

NUMBER_RE = re.compile(r"^\s*(\d{1,2})\s*$")
NUMBER_H_MAX_M = 0.30           # tread numbers are small texts
STEP_M = (0.08, 0.60)           # the next number this far away (a tread's going, a winder's)
TURN_JUMP_M = 3.0               # 4 Nov 2026: across a half landing to the next arm at most this far (it must lead on)
MIN_STEPS = 6                   # a chain of at least this many numbers, the last at least this
ARM_TURN_DEG = 25.0             # numbers in one arm: their steps within this of the arm's first step
ARM_MIN_POINTS = 3              # an arm holds at least this many numbers
TREAD_REACH_M = 0.22            # a tread line passes this close to its number
TREAD_PERP = 0.25               # ... nearly across the arm (|cos| under this)
WIDTH_M = (0.6, 2.0)            # an arm this wide (the median tread line)
WIDTH_DEFAULT_M = 0.9
INSIDE_SHARE = 0.5              # a stair piece holding this share of the numbers already reads the stair


def _numbers(texts: list) -> list[tuple[int, tuple[float, float], object]]:
    out = []
    for t in texts or []:
        m = NUMBER_RE.match(str(getattr(t, "text", "") or ""))
        if not m or float(getattr(t, "height", 0.0) or 0.0) > NUMBER_H_MAX_M:
            continue
        v = int(m.group(1))
        if 1 <= v <= 60:
            out.append((v, ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0), t))
    return out


def chains(texts: list) -> list[list[tuple[int, tuple[float, float], object]]]:
    """The runs of tread numbers (the module docstring), longest first; each number in one run only (pure)."""
    nums = _numbers(texts)
    by_value: dict[int, list[int]] = {}
    for k, (v, _p, _t) in enumerate(nums):
        by_value.setdefault(v, []).append(k)
    found = []
    for start in by_value.get(1, []):
        chain = [start]
        while True:
            v, p, _t = nums[chain[-1]]
            nxt = None

            def leads(k: int, value: int) -> bool:
                # 4 Nov 2026 (real07, user: "Stairs are missing in the project"): a candidate the next number follows
                q = nums[k][1]
                return any(STEP_M[0] <= math.dist(q, nums[j][1]) <= STEP_M[1] for j in by_value.get(value + 1, [])
                           if j not in chain and j != k)

            for skip, (lo, hi) in ((1, STEP_M), (2, (STEP_M[0] * 2, STEP_M[1] * 2))):
                cands = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + skip, [])
                         if k not in chain and lo <= math.dist(p, nums[k][1]) <= hi]
                if cands:
                    # a candidate that leads on wins (the U-stair's step 9 had the wall-thickness text '10' beside it;
                    # its real step 10 lies across the landing)
                    on = [c for c in cands if leads(c[1], v + skip)]
                    nxt = min(on or cands)[1]
                    if not on:
                        far = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + 1, [])
                               if k not in chain and STEP_M[1] < math.dist(p, nums[k][1]) <= TURN_JUMP_M
                               and leads(k, v + 1)]
                        if far:
                            nxt = min(far)[1]
                    break
            if nxt is None:
                # the turn: the next number across the landing, where the next arm starts (it leads on)
                far = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + 1, [])
                       if k not in chain and STEP_M[1] < math.dist(p, nums[k][1]) <= TURN_JUMP_M and leads(k, v + 1)]
                if far:
                    nxt = min(far)[1]
            if nxt is None:
                break
            chain.append(nxt)
        if len(chain) >= MIN_STEPS and nums[chain[-1]][0] >= MIN_STEPS:
            found.append(chain)
    found.sort(key=len, reverse=True)
    used: set = set()
    out = []
    for chain in found:
        if used & set(chain):
            continue
        used |= set(chain)
        out.append([nums[k] for k in chain])
    return out


def _unit(a, b) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _angle(u, v) -> float:
    return math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))


def _arms(points: list) -> list[list[int]]:
    """The arms of a numbered stair: the straight run from the first number (its steps within ``ARM_TURN_DEG`` of the
    first step) and the straight run back from the last; one arm when the first run holds every number. What lies
    between them is the turn (winders or a landing)."""
    def run(idx: list[int]) -> list[int]:
        out = idx[:2]
        ref = _unit(points[idx[0]], points[idx[1]])
        for k in idx[2:]:
            if abs(_angle(ref, _unit(points[out[-1]], points[k]))) > ARM_TURN_DEG:
                break
            out.append(k)
        return out

    n = len(points)
    if n < 2:
        return []
    first = run(list(range(n)))
    if len(first) == n:
        return [first]
    # 4 Nov 2026 (real10's fire escape stair, user: "There should have been fire escape ladders here": its top number
    # 16 stands by the arrow on the landing, off the arm's line, so the run back from it turned at once): an end number
    # off its arm is on the landing; the arm runs from the number next to it
    if len(first) < ARM_MIN_POINTS and n > ARM_MIN_POINTS + 1:
        inner = run(list(range(1, n)))
        if len(inner) >= ARM_MIN_POINTS:
            first = inner
    last = run(list(range(n - 1, -1, -1)))[::-1]
    if len(last) < ARM_MIN_POINTS and n > ARM_MIN_POINTS + 1:
        inner = run(list(range(n - 2, -1, -1)))[::-1]
        if len(inner) >= ARM_MIN_POINTS:
            last = inner
    if set(first) & set(last):
        return [first] if len(first) >= len(last) else [last]
    return [r for r in (first, last) if len(r) >= ARM_MIN_POINTS]


def _treads(points: list, axis, segs: list) -> list[tuple]:
    """The tread lines the numbers of one arm stand on: straight segments nearly across ``axis`` passing within
    ``TREAD_REACH_M`` of a number."""
    out = []
    for p in points:
        best = None
        for a, b, sid in segs:
            u = _unit(a, b)
            if abs(u[0] * axis[0] + u[1] * axis[1]) > TREAD_PERP:
                continue
            d = LineString([a, b]).distance(Point(p))
            if d <= TREAD_REACH_M and (best is None or d < best[0]):
                best = (d, a, b, sid)
        if best is not None:
            out.append(best[1:])
    return out


def stair_of(chain: list, strokes: list) -> Optional[dict]:
    """The stair one chain of numbers describes (the module docstring): ``{"flights", "landing", "winders", "turn",
    "direction", "polygon", "steps", "entities", "reason"}`` (page metres) or ``{"skip": reason}`` (pure)."""
    pts = [c[1] for c in chain]
    values = [c[0] for c in chain]
    arms = _arms(pts)
    if not arms or (len(arms) == 1 and len(arms[0]) < len(pts)):
        return {"skip": f"no two straight arms of {ARM_MIN_POINTS} numbers at the ends of {values[0]}-{values[-1]}"}
    segs = []
    for st in strokes or []:
        if getattr(st, "arc", None):
            continue
        p = [tuple(q) for q in getattr(st, "pts", []) or []]
        for a, b in zip(p[:-1], p[1:]):
            if 0.3 <= math.dist(a, b) <= WIDTH_M[1] + 0.3:
                segs.append((a, b, st.id))
    near = MultiPoint(pts).convex_hull.buffer(WIDTH_M[1])
    segs = [s for s in segs if near.intersects(LineString([s[0], s[1]]))]
    # 3 Nov 2026 (real10's core: the arms read from the numbers lay 2-8 degrees askew, the box tilted and the winders
    # around the eye fell outside it): the arms follow the drawing's main directions (within SNAP_DEG) and the footprint
    # is a rectangle in that frame holding the arms and every number of the turn
    main = _main_angle(segs) if segs else math.degrees(math.atan2(*reversed(_unit(pts[arms[0][0]], pts[arms[0][-1]]))))
    flights, shapes, ids = [], [], set()
    arm_axes = []
    for arm in arms:
        apts = [pts[i] for i in arm]
        axis = _snap(_unit(apts[0], apts[-1]), main)
        normal = (-axis[1], axis[0])
        treads = _treads(apts, axis, segs)
        widths = sorted(math.dist(a, b) for a, b, _ in treads)
        width = widths[len(widths) // 2] if widths else WIDTH_DEFAULT_M
        width = min(max(width, WIDTH_M[0]), WIDTH_M[1])
        if treads:                                             # the arm's centre line: the tread lines' middles
            offs = sorted(((a[0] + b[0]) / 2.0 - p[0]) * normal[0] + ((a[1] + b[1]) / 2.0 - p[1]) * normal[1]
                          for (a, b, _), p in zip(treads, apts))
            off = offs[len(offs) // 2]
        else:
            off = 0.0
        cx = sum(q[0] for q in apts) / len(apts) + normal[0] * off
        cy = sum(q[1] for q in apts) / len(apts) + normal[1] * off
        proj = [(q[0] - cx) * axis[0] + (q[1] - cy) * axis[1] for q in apts]
        s = (cx + axis[0] * proj[0], cy + axis[1] * proj[0])
        e = (cx + axis[0] * proj[-1], cy + axis[1] * proj[-1])
        going = math.dist(s, e) / max(len(apts) - 1, 1)
        ids |= {sid for _, _, sid in treads}
        flights.append({"start": [round(s[0], 4), round(s[1], 4)], "end": [round(e[0], 4), round(e[1], 4)],
                        "width": round(width, 4), "lines": len(apts), "spacing": round(going, 4)})
        half = going / 2.0
        s0 = (s[0] - axis[0] * half, s[1] - axis[1] * half)
        e0 = (e[0] + axis[0] * half, e[1] + axis[1] * half)
        shapes.append(LineString([s0, e0]).buffer(width / 2.0, cap_style=2))
        arm_axes.append(axis)
    in_arms = {i for arm in arms for i in arm}
    turn_pts = [pts[i] for i in range(len(pts)) if i not in in_arms]
    landing = None
    winders = 0
    turn = "straight"
    # the footprint: the arms and the turn's tread lines (the winders run from the eye to the stair's outer edge; without
    # them, each turn number grown by half the widest arm), as a rectangle in the main frame
    wmax = max(f["width"] for f in flights)
    theta = math.radians(main)
    ct, st_ = math.cos(theta), math.sin(theta)
    to_f = lambda q: (q[0] * ct + q[1] * st_, -q[0] * st_ + q[1] * ct)
    from_f = lambda q: (q[0] * ct - q[1] * st_, q[0] * st_ + q[1] * ct)
    cloud = [c for sh in shapes for c in sh.exterior.coords]
    for q in [pts[i] for i in range(len(pts)) if i not in {k for arm in arms for k in arm}]:
        lines = [sg for sg in segs if LineString([sg[0], sg[1]]).distance(Point(q)) <= TREAD_REACH_M
                 and math.dist(sg[0], sg[1]) <= wmax * 1.6]
        if lines:
            cloud += [c for sg in lines for c in (sg[0], sg[1])]
            ids |= {sg[2] for sg in lines}
        else:
            cloud += [(q[0] + dx, q[1] + dy) for dx, dy in ((wmax / 2, 0), (-wmax / 2, 0), (0, wmax / 2),
                                                            (0, -wmax / 2))]
    fx = [to_f(q) for q in cloud]
    bx = (min(q[0] for q in fx), min(q[1] for q in fx), max(q[0] for q in fx), max(q[1] for q in fx))
    poly = Polygon([from_f(q) for q in ((bx[0], bx[1]), (bx[2], bx[1]), (bx[2], bx[3]), (bx[0], bx[3]))])
    if len(arms) == 2:
        a1, a2 = arm_axes
        ang = abs(_angle(a1, a2))
        turn = "U" if ang >= 150.0 else ("L" if 60.0 <= ang <= 120.0 else "other")
        if turn == "other":
            return {"skip": f"two arms {ang:.0f} degrees apart in the numbers {values[0]}-{values[-1]}"}
        if turn == "U":
            # a U stair's turn is the band beyond the arms' far ends, across the whole stair (the eye between the arms
            # is no landing)
            top = max(max(x * a1[0] + y * a1[1] for x, y in sh.exterior.coords) for sh in shapes)
            n1 = (-a1[1], a1[0])
            corners = list(poly.exterior.coords)[:4]
            far = max(x * a1[0] + y * a1[1] for x, y in corners)
            lo = min(x * n1[0] + y * n1[1] for x, y in corners)
            hi = max(x * n1[0] + y * n1[1] for x, y in corners)
            if far - top >= 0.2:
                land = Polygon([(a1[0] * u + n1[0] * v, a1[1] * u + n1[1] * v)
                                for u, v in ((top, lo), (far, lo), (far, hi), (top, hi))])
                landing = {"polygon": [[round(x, 4), round(y, 4)] for x, y in list(land.exterior.coords)[:-1]],
                           "depth": round(far - top, 4)}
        else:
            rest = poly.difference(unary_union(shapes).buffer(0.01))
            if not rest.is_empty:
                part = max(getattr(rest, "geoms", [rest]), key=lambda g: g.area)
                land = part.minimum_rotated_rectangle
                if land.area >= 0.2:
                    lc = list(land.exterior.coords)
                    landing = {"polygon": [[round(x, 4), round(y, 4)] for x, y in lc[:-1]],
                               "depth": round(min(math.dist(lc[0], lc[1]), math.dist(lc[1], lc[2])), 4)}
        winders = len(turn_pts)
    first = flights[0]
    d = _unit(first["start"], first["end"])
    reason = (f"the treads are numbered {values[0]}-{values[-1]} ({len(values)} numbers): "
              f"{len(arms)} straight arm(s) of {', '.join(str(f['lines']) for f in flights)} treads"
              + (f", a {turn} turn with {winders} winder(s)" if len(arms) == 2 else "")
              + f"; it rises from {values[0]} to {values[-1]} (drawn)")
    return {"flights": flights, "landing": landing, "winders": winders, "turn": turn,
            "direction": [round(d[0], 4), round(d[1], 4)], "polygon": poly, "steps": values[-1],
            "entities": sorted({str(c[2].id) for c in chain}) + sorted(ids), "reason": reason}


SNAP_DEG = 15.0                 # an arm within this of the drawing's main directions follows them


def _main_angle(segs: list) -> float:
    """The main direction of the stair's lines (degrees modulo 90): the length-weighted mode in 2 degree bins."""
    bins: dict = {}
    for a, b, _sid in segs:
        L = math.dist(a, b)
        k = int(round((math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0) / 2.0)) % 45
        bins[k] = bins.get(k, 0.0) + L
    return 2.0 * max(bins, key=bins.get) if bins else 0.0


def _snap(u, main: float) -> tuple[float, float]:
    """``u`` turned onto the nearest of the main directions when within ``SNAP_DEG``."""
    ang = math.degrees(math.atan2(u[1], u[0]))
    best = min((main + 90.0 * k for k in range(-4, 5)), key=lambda c: abs((ang - c + 180.0) % 360.0 - 180.0))
    if abs((ang - best + 180.0) % 360.0 - 180.0) <= SNAP_DEG:
        r = math.radians(best)
        return math.cos(r), math.sin(r)
    return u


def _footprint(poly: Polygon, axis) -> tuple[tuple[float, float], tuple[float, float], float]:
    """``(centre, (width, depth), rotation_deg)`` of a rotated rectangle, its local +Y along ``axis``."""
    c = list(poly.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    l1, l2 = math.hypot(*e1), math.hypot(*e2)
    along = e1 if abs(e1[0] * axis[0] + e1[1] * axis[1]) / (l1 or 1) >= \
        abs(e2[0] * axis[0] + e2[1] * axis[1]) / (l2 or 1) else e2
    depth = l1 if along is e1 else l2
    width = l2 if along is e1 else l1
    ang = math.degrees(math.atan2(along[1], along[0])) - 90.0
    ang = (ang + 180.0) % 360.0 - 180.0
    cen = poly.centroid
    return (round(cen.x, 4), round(cen.y, 4)), (round(width, 4), round(depth, 4)), round(ang, 3)


def apply(pieces: list, cands: list, texts: list, strokes: list, units_to_m: float, file_rel: str, page_no: int,
          notes: list) -> tuple[list, list, list]:
    """``(pieces, cands, polygons)`` with the numbered stairs (``stair_of``) no stair piece holds added as stair
    pieces, the candidates and non-stair pieces whose centre stands inside one of them dropped (its parts), and the new
    stairs' footprints (page metres)."""
    from wenart.ingest.model import FurnitureItem

    found = chains(texts)
    if not found:
        return pieces, cands, []
    pieces, cands = list(pieces), list(cands)
    polys: list = []
    for chain in found:
        pts = [Point(c[1]) for c in chain]
        held = False
        for p in pieces:
            if p.type != "stair":
                continue
            fp = _piece_poly(p)
            if fp is not None and sum(1 for q in pts if fp.buffer(0.1).contains(q)) >= INSIDE_SHARE * len(pts):
                held = True
                break
        values = f"{chain[0][0]}-{chain[-1][0]}"
        if held:
            notes.append(f"numbered stair {values}: a stair piece already holds its numbers (the stair rule's reading "
                         f"kept)")
            continue
        st = stair_of(chain, strokes)
        if st is None or st.get("skip"):
            notes.append(f"numbered stair {values}: {st.get('skip') if st else 'not read'}")
            continue
        centre, size, rot = _footprint(st["polygon"], st["direction"])
        inside = st["polygon"].buffer(-0.05)
        dropped = [c for c in cands if inside.contains(Point(c["footprint"]["center"]))]
        cands = [c for c in cands if c not in dropped]
        parts = [p for p in pieces if p.type != "stair" and inside.contains(Point(p.center))]
        pieces = [p for p in pieces if p not in parts]
        xs = [x for x, _ in st["polygon"].exterior.coords]
        ys = [y for _, y in st["polygon"].exterior.coords]
        box = [round(v / units_to_m, 3) for v in (min(xs), min(ys), max(xs), max(ys))] if units_to_m else \
            [min(xs), min(ys), max(xs), max(ys)]
        ev = B.evidence(file_rel, "vector", 0.85, page=page_no, entity=",".join(st["entities"][:40]) or None)
        ev["note"] = f"numbered treads: {st['reason']}"
        ev["rule"] = "numbered_treads"
        details = {"stair": {"flights": st["flights"], "landing": st["landing"], "direction": st["direction"],
                             "direction_assumed": False, "turn": "U" if st["turn"] == "U" else
                             ("straight" if st["turn"] == "straight" else "other"),
                             "turn_assumed": False, "void_assumed": True, "riser_m": None, "riser_source": None,
                             "reason": st["reason"], "steps_drawn": st["steps"]}}
        if st["winders"]:
            details["stair"]["winders"] = st["winders"]
        if st["landing"] is None and len(st["flights"]) >= 2:
            details["stair"]["landing_assumed"] = True
        pieces.append(FurnitureItem(type="stair", type_raw=None, center=centre, size=size, rotation_deg=rot,
                                    front_deg=None, box=box, entity=st["entities"][0], evidence=ev,
                                    status="verified", type_method="rule", details=details))
        polys.append(st["polygon"])
        notes.append(f"numbered stair {values}: {st['reason']}; footprint {size[0]:.2f} x {size[1]:.2f} m"
                     + (f"; {len(dropped) + len(parts)} candidate(s) inside it are its parts" if dropped or parts
                        else ""))
    return pieces, cands, polys


def _piece_poly(p) -> Optional[Polygon]:
    try:
        cx, cy = p.center
        w, d = p.size
        a = math.radians(float(p.rotation_deg or 0.0))
    except (TypeError, ValueError):
        return None
    ca, sa = math.cos(a), math.sin(a)
    return Polygon([(cx + ca * u - sa * v, cy + sa * u + ca * v)
                    for u, v in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])
