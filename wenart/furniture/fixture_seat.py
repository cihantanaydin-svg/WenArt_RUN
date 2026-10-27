"""Drawn fixed equipment stands where it is drawn and never through another drawn fixture (27 Oct 2026). Pure Python,
no shapely: the scene build's clash resolver (``wenart.blender.clashes``, which runs where Blender's Python has no
shapely) uses it as well as the reading (``infer.ai_named_members``, ``reading.fix_fixed``), the architect's
``move_piece`` and Argus.

User, on the bathrooms of real06 run 20261027-180412-full: "clashing sink and bath, also bath is not in proper place".
What happened (both bathrooms: the baths f_L0_010 / f_L1_009, the basins f_L0_026 / f_L1_023): the plan draws a corner
bath in the corner beside the window, a vanity with its basin to its left and a curved bath screen. The symbol finder
read the bath, the screen, the vanity's front edge and its taps as one outline, 2.54 x 1.01 m at 161.5 deg (the
smallest box around that cluster), which also holds the basin read on its own. ``infer.ai_named_members`` typed it a
bathtub (the bathroom misses its bath and the AI passes named one) and took the nearest real product inside the
outline, 1.80 x 0.80 m, "centre and rotation kept": a bath turned 18 deg across the room, under the window, 0.33 m
(L1: 0.25 m) into the basin. The reading's fixed-equipment fix moved it 0.21 m out of the wall without looking at the
basin (overlaps were not its business); the build's clash resolver (F5) and Argus's moves found no free place within
0.5 m for either piece, since every move of the basin or of the turned bath out of the other leaves the room. The
library models were not the cause (the bath model is 1.80 x 0.87 m on its 1.80 x 0.80 m footprint, the basin 0.53 x
0.38 m on 0.53 x 0.34 m).

Rules (general, every project; CLAUDE.md: fixed equipment keeps the drawn type, position, orientation and footprint;
only a clear drawing or reading error is fixed, logged ``adjusted_by_ai`` with the reason and the plan crop):

1. ``seat``: a fixed piece whose drawn outline is no product of its type (a misread or merged outline) becomes the
   real product standing where the outline says. Its back is on a wall of its room and it runs along that wall (the
   angle of a merged outline's box is no orientation). It stands inside the room, clear of the other drawn fixed
   pieces and of the door swings, with its centre inside the drawn outline and at least ``MIN_DRAWN_SHARE`` of it on
   the outline. Of these places the one that covers most of the drawn outline wins; a corner or a bay (a second wall
   touched) counts ``CORNER_BONUS_M2`` more; then the larger product; then the place nearer the drawn centre.
2. ``slide``: a drawn fixed piece that stands on a wall moves only along that wall, to the nearest free place within
   ``MOVE_MAX_M``. Moving a fixed piece off its wall fixes nothing.
3. ``gives_way``: of two drawn fixed pieces that cut each other, the one with the weaker reading moves: an added piece
   before a drawn one, unverified before verified, an inferred type before one the AI passes agreed on or the drawing
   names, a size changed from its drawing before one as drawn; on a tie the smaller.
4. ``free_fixture``: a drawn fixed piece that must clear something slides along its wall (2), else it is seated in its
   drawn outline (1).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

from wenart import geometry as G

MIN_DRAWN_SHARE = 0.5        # at least this share of a seated product lies on its drawn outline
CORNER_BONUS_M2 = 0.10       # a corner or a bay (a second wall touched) counts this much drawn area more
WALL_TOL_M = 0.03            # a side this close to the room outline stands on a wall
INSIDE_TOL_M = 0.01          # a piece may touch its walls
CLEAR_M = 0.02               # a piece moved or seated beside an obstacle keeps this gap
STEP_M = 0.05
MOVE_MAX_M = 0.50            # CLAUDE.md: a fixed piece moves at most 0.5 m
CUT_EPS_M = 0.005            # a cut this shallow is touching
CLASH_M = 0.03               # two fixed pieces cutting each other deeper than this clash (clashes.CLASH_TOL_M)
# the fixed pieces that stand on a wall on their own (stairs, counter runs and islands are drawn as runs or blocks)
SEAT_TYPES = ("bathtub", "shower", "washbasin", "toilet", "washing_machine", "fridge", "stove", "sink_kitchen")
TURNABLE = ("shower",)       # a product that stands either way round on its wall
# a piece built into a counter or a vanity overlaps it by design
HOSTED = ("sink_kitchen", "stove", "washing_machine", "washbasin", "dishwasher", "oven", "cooktop", "hob")
HOSTS = ("kitchen_counter", "kitchen_island", "vanity", "bathroom_vanity")
STRONG_METHODS = ("block_name", "name_text", "ai_two_pass")
WEAK_METHODS = ("inferred", "none", "group_member", "zone_label", "ai_member")

Point = tuple[float, float]


# --------------------------------------------------------------------------
# Geometry (convex rectangles against a simple room polygon)
# --------------------------------------------------------------------------

def rect(center, size, rotation_deg: float) -> list[Point]:
    """The footprint rectangle (``geometry.rotated_rectangle``: front edge first, then right, back, left)."""
    return [(float(x), float(y)) for x, y in G.rotated_rectangle((float(center[0]), float(center[1])),
                                                                 (float(size[0]), float(size[1])),
                                                                 float(rotation_deg or 0.0))]


def footprint_rect(fp: dict) -> list[Point]:
    return rect(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))


def ccw(poly) -> list[Point]:
    """The polygon's points counter-clockwise, without a closing point."""
    pts = [(float(p[0]), float(p[1])) for p in poly]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts if G.polygon_signed_area(pts) > 0 else pts[::-1]


def _axes(poly) -> list[Point]:
    out = []
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        n = math.hypot(x1 - x0, y1 - y0)
        if n > 1e-9:
            out.append((-(y1 - y0) / n, (x1 - x0) / n))
    return out


def cut_depth(a, b) -> float:
    """How deep two convex polygons cut each other (the smallest overlap along their separating axes; 0 apart)."""
    depth = math.inf
    for ax in _axes(a) + _axes(b):
        pa = [p[0] * ax[0] + p[1] * ax[1] for p in a]
        pb = [p[0] * ax[0] + p[1] * ax[1] for p in b]
        over = min(max(pa), max(pb)) - max(min(pa), min(pb))
        if over <= 0:
            return 0.0
        depth = min(depth, over)
    return 0.0 if depth == math.inf else depth


def _clip(subject: list[Point], clip: list[Point]) -> list[Point]:
    """Sutherland-Hodgman: ``subject`` clipped by the convex counter-clockwise polygon ``clip``."""
    out = list(subject)
    for i in range(len(clip)):
        if not out:
            break
        a, b = clip[i], clip[(i + 1) % len(clip)]

        def side(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

        src, out = out, []
        for j in range(len(src)):
            p, q = src[j], src[(j + 1) % len(src)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0) and abs(sp - sq) > 1e-15:
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def overlap_area(a, b) -> float:
    """The area two convex polygons share."""
    part = _clip(ccw(a), ccw(b))
    return G.polygon_area(part) if len(part) >= 3 else 0.0


def _cross(p, q, r) -> float:
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def _crosses(p1, p2, q1, q2) -> bool:
    """The two segments cross properly (touching does not count)."""
    d1, d2 = _cross(q1, q2, p1), _cross(q1, q2, p2)
    d3, d4 = _cross(p1, p2, q1), _cross(p1, p2, q2)
    return ((d1 > 1e-12 and d2 < -1e-12) or (d1 < -1e-12 and d2 > 1e-12)) and \
        ((d3 > 1e-12 and d4 < -1e-12) or (d3 < -1e-12 and d4 > 1e-12))


def _shrunk(r: list[Point], tol: float) -> list[Point]:
    out = []
    n = len(r)
    for i in range(n):
        p, nxt, prv = r[i], r[(i + 1) % n], r[i - 1]
        a = G.distance(p, nxt) or 1.0
        b = G.distance(p, prv) or 1.0
        t = min(tol, a / 2.0 - 1e-6, b / 2.0 - 1e-6)
        out.append((p[0] + (nxt[0] - p[0]) / a * t + (prv[0] - p[0]) / b * t,
                    p[1] + (nxt[1] - p[1]) / a * t + (prv[1] - p[1]) / b * t))
    return out


def inside_room(r: list[Point], room: list[Point], tol: float = INSIDE_TOL_M) -> bool:
    """The rectangle lies inside the room (touching its walls within ``tol``): its corners inside and no wall line
    through it (a column or a wall end poking in)."""
    s = _shrunk(r, tol)
    if not all(G.point_in_polygon(p, room) for p in s):
        return False
    for i in range(len(room)):
        a, b = room[i], room[(i + 1) % len(room)]
        for j in range(len(s)):
            if _crosses(a, b, s[j], s[(j + 1) % len(s)]):
                return False
    return True


def _ring_distance(p: Point, room: list[Point]) -> float:
    return min(G.point_segment_distance(p, room[i], room[(i + 1) % len(room)]) for i in range(len(room)))


def wall_sides(r: list[Point], room: list[Point], tol: float = WALL_TOL_M, touch: bool = False) -> set[int]:
    """The sides of the rectangle that stand on a wall of the room (0 front, 1 right, 2 back, 3 left): along their
    length, or (``touch``) somewhere (an end against a column or a wall end)."""
    out = set()
    for k in range(4):
        a, b = r[k], r[(k + 1) % 4]
        near = [_ring_distance((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), room) <= tol
                for t in (0.15, 0.5, 0.85)]
        if any(near) if touch else all(near):
            out.add(k)
    return out


def _proj(poly, origin: Point, u: Point) -> tuple[float, float]:
    vals = [(p[0] - origin[0]) * u[0] + (p[1] - origin[1]) * u[1] for p in poly]
    return min(vals), max(vals)


# --------------------------------------------------------------------------
# Rule 1: seated in its drawn outline
# --------------------------------------------------------------------------

def products_of(ftype: str, current=None) -> list[tuple[float, float]]:
    """The real products (width along the wall, depth) of the type (``sizes.products``; a ``TURNABLE`` product both
    ways round), and the current size when it lies inside the type's ranges."""
    from wenart.furniture import sizes as SZ

    out: list[tuple[float, float]] = []
    cands = [tuple(p[:2]) for p in SZ.products(ftype)]
    if current is not None and SZ.fits(ftype, [float(current[0]), float(current[1])], 0.0):
        cands.insert(0, (float(current[0]), float(current[1])))
    for p in cands:
        w, d = round(float(p[0]), 4), round(float(p[1]), 4)
        for pair in ((w, d), (d, w)) if ftype in TURNABLE else ((w, d),):
            if pair not in out:
                out.append(pair)
    return out


def _starts(length: float, w: float, a: Point, u: Point, obstacles: list, room: list[Point]) -> list[float]:
    """Where a piece of width ``w`` may start along a wall segment (its own coordinate from ``a``): a 5 cm grid over
    the segment, its two ends, flush with each room corner along it and beside each obstacle."""
    out = {0.0, round(length - w, 4)}
    k = int(math.floor((-w + STEP_M) / STEP_M))
    while k * STEP_M <= length - STEP_M:
        out.add(round(k * STEP_M, 4))
        k += 1
    for p in room:
        t = (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]
        out.update((round(t, 4), round(t - w, 4)))
    for o in obstacles:
        lo, hi = _proj(o, a, u)
        out.update((round(hi + CLEAR_M, 4), round(lo - w - CLEAR_M, 4)))
    return sorted(s for s in out if -w < s < length)


def seat(ftype: str, drawn: dict, room, obstacles: Sequence = (), *, blocked: Optional[Callable] = None,
         products: Optional[list] = None) -> Optional[dict]:
    """Rule 1 (module docstring): the real product of ``ftype`` seated in its drawn outline ``drawn`` (a footprint
    dict) in ``room`` (its polygon), clear of ``obstacles`` (convex polygons) and of what ``blocked(rect)`` says (a
    door swing); ``products`` (width along the wall, depth) default to ``products_of``. Returns ``{"footprint":
    {center, size, rotation_deg}, "front_deg", "walls", "drawn_share", "reason"}`` or None when no place qualifies.
    Pure."""
    room_pts = ccw(room)
    if len(room_pts) < 3 or not drawn or not drawn.get("size"):
        return None
    out_line = footprint_rect(drawn)
    dc = (float(drawn["center"][0]), float(drawn["center"][1]))
    prods = [(float(w), float(d)) for w, d in (products if products is not None else products_of(ftype))]
    obs = [ccw(o) for o in obstacles if o is not None and len(o) >= 3]
    best = None
    n = len(room_pts)
    for i in range(n):
        a, b = room_pts[i], room_pts[(i + 1) % n]
        length = G.distance(a, b)
        if length < 0.2:
            continue
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        inward = (-u[1], u[0])                       # the room is counter-clockwise: its inside is on the left
        rot = G.normalise_angle(round(math.degrees(math.atan2(-u[1], -u[0])), 6))   # local +Y (the back) to the wall
        for w, d in prods:
            for s0 in _starts(length, w, a, u, obs, room_pts):
                c = (a[0] + u[0] * (s0 + w / 2.0) + inward[0] * d / 2.0,
                     a[1] + u[1] * (s0 + w / 2.0) + inward[1] * d / 2.0)
                if not G.point_in_polygon(c, out_line):
                    continue
                r = rect(c, (w, d), rot)
                covered = overlap_area(r, out_line)
                if covered < MIN_DRAWN_SHARE * w * d - 1e-9 or not inside_room(r, room_pts):
                    continue
                if any(cut_depth(r, o) > CUT_EPS_M for o in obs) or (blocked is not None and blocked(r)):
                    continue
                walls = wall_sides(r, room_pts, touch=True)
                score = covered + CORNER_BONUS_M2 * max(0, len(walls) - 1)
                key = (round(score, 4), round(w * d, 4), -round(G.distance(c, dc), 4))
                if best is None or key > best[0]:
                    best = (key, c, (w, d), rot, walls, covered)
    if best is None:
        return None
    _key, c, (w, d), rot, walls, covered = best
    share = covered / (w * d)
    where = ", in a corner" if len(walls) == 2 else ", in a bay" if len(walls) >= 3 else ""
    reason = (f"the drawn outline {float(drawn['size'][0]):.2f} x {float(drawn['size'][1]):.2f} m at "
              f"{float(drawn.get('rotation_deg') or 0.0):.1f} deg is no {ftype} where it stands (a misread or merged "
              f"outline): the real product {w:.2f} x {d:.2f} m seated in it, its back on a wall of the room and along "
              f"it{where}, {share:.0%} of it on the drawn outline, clear of the other drawn fixtures and the door "
              f"swings")
    return {"footprint": {"center": [round(c[0], 4), round(c[1], 4)], "size": [round(w, 4), round(d, 4)],
                          "rotation_deg": round(rot, 3)},
            "front_deg": G.front_direction_deg(rot), "walls": sorted(walls), "drawn_share": round(share, 3),
            "reason": reason}


# --------------------------------------------------------------------------
# Rule 2: along its wall
# --------------------------------------------------------------------------

def slide(fp: dict, room, obstacles: Sequence = (), *, blocked: Optional[Callable] = None,
          max_m: float = MOVE_MAX_M) -> Optional[tuple[float, float, float]]:
    """Rule 2 (module docstring): ``(dx, dy, distance)`` of the nearest place along the wall the piece stands on (its
    back or front on a wall: along its width; else a side on a wall: along its depth) within ``max_m``, inside the
    room and clear of ``obstacles`` and ``blocked``; None when it stands on no wall or no such place exists. Pure."""
    room_pts = ccw(room)
    if len(room_pts) < 3:
        return None
    r0 = footprint_rect(fp)
    sides = wall_sides(r0, room_pts)
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    if sides & {0, 2}:
        u = (math.cos(rot), math.sin(rot))
    elif sides & {1, 3}:
        u = (-math.sin(rot), math.cos(rot))
    else:
        return None
    obs = [ccw(o) for o in obstacles if o is not None and len(o) >= 3]
    lo0, hi0 = _proj(r0, (0.0, 0.0), u)
    cands = {round(k * STEP_M, 4) for k in range(-int(max_m / STEP_M), int(max_m / STEP_M) + 1) if k}
    for o in obs:
        lo, hi = _proj(o, (0.0, 0.0), u)
        cands.update((round(hi + CLEAR_M - lo0, 4), round(lo - CLEAR_M - hi0, 4)))
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    size = (float(fp["size"][0]), float(fp["size"][1]))
    for t in sorted((t for t in cands if 1e-6 < abs(t) <= max_m + 1e-9), key=lambda t: (abs(t), t)):
        r = rect((cx + u[0] * t, cy + u[1] * t), size, math.degrees(rot))
        if not inside_room(r, room_pts):
            continue
        if any(cut_depth(r, o) > CUT_EPS_M for o in obs) or (blocked is not None and blocked(r)):
            continue
        return round(u[0] * t, 4), round(u[1] * t, 4), round(abs(t), 4)
    return None


# --------------------------------------------------------------------------
# Rule 3: who gives way; rule 4: the fix
# --------------------------------------------------------------------------

def resized(f: dict) -> bool:
    """The piece's size was changed from its drawing (a drawn outline that was no product)."""
    dfp, fp = f.get("drawn_footprint") or {}, f.get("footprint") or {}
    try:
        return bool(dfp.get("size")) and any(abs(float(a) - float(b)) > 0.01
                                             for a, b in zip(dfp["size"][:2], fp["size"][:2]))
    except (KeyError, TypeError, ValueError):
        return False


def trust(f: dict) -> tuple:
    """How firmly the piece is read (higher stays): drawn, verified, a strong type reading, its drawn size."""
    method = str(f.get("type_method") or "none")
    return (0 if f.get("source") == "added_by_ai" else 1, 1 if f.get("status") == "verified" else 0,
            2 if method in STRONG_METHODS else 0 if method in WEAK_METHODS else 1, 0 if resized(f) else 1)


def _area(f: dict) -> float:
    try:
        return float(f["footprint"]["size"][0]) * float(f["footprint"]["size"][1])
    except (KeyError, TypeError, ValueError, IndexError):
        return 0.0


def gives_way(f: dict, g: dict) -> dict:
    """Rule 3 (module docstring): which of two clashing fixed pieces moves."""
    return f if (trust(f), _area(f), str(f.get("id"))) <= (trust(g), _area(g), str(g.get("id"))) else g


def hosted_pair(f: dict, g: dict) -> bool:
    """A piece built into a counter or a vanity and that host overlap by design."""
    tf, tg = str(f.get("type") or ""), str(g.get("type") or "")
    return (tf in HOSTED and tg in HOSTS) or (tg in HOSTED and tf in HOSTS)


def drawn_fixture(f: dict) -> bool:
    """A drawn fixed piece that stands on its own (``SEAT_TYPES``; not one the AI added)."""
    return str(f.get("type") or "") in SEAT_TYPES and f.get("source") != "added_by_ai"


def fixture_pair(f: dict, g: dict) -> bool:
    """Two drawn fixed pieces that stand on their own (``drawn_fixture``), neither built into the other."""
    return drawn_fixture(f) and drawn_fixture(g) and not hosted_pair(f, g)


def free_fixture(f: dict, room, obstacles: Sequence = (), *, blocked: Optional[Callable] = None,
                 allow_seat: bool = True) -> Optional[dict]:
    """Rule 4 (module docstring): the place of the drawn fixed piece ``f`` clear of ``obstacles`` (what it must clear
    and every other piece, convex polygons) and ``blocked``: slid along its wall (rule 2), else (``allow_seat``) seated
    in its drawn outline (rule 1: ``drawn_footprint``, else its footprint). Returns ``{"footprint", "front_deg",
    "how": "slid" | "seated", "distance_m", "reason"}`` or None. Pure: ``f`` is unchanged."""
    fp = f.get("footprint") or {}
    if not fp.get("center") or not fp.get("size"):
        return None
    moved = slide(fp, room, obstacles, blocked=blocked)
    if moved is not None:
        dx, dy, dist = moved
        new = dict(fp, center=[round(float(fp["center"][0]) + dx, 4), round(float(fp["center"][1]) + dy, 4)])
        return {"footprint": new, "front_deg": f.get("front_deg"), "how": "slid", "distance_m": dist,
                "reason": f"moved {dist:.2f} m along its wall to the nearest free place"}
    if not allow_seat or str(f.get("type") or "") not in SEAT_TYPES:
        return None
    drawn = f.get("drawn_footprint") or fp
    got = seat(str(f["type"]), drawn, room, obstacles, blocked=blocked, products=products_of(
        str(f["type"]), fp.get("size")))
    if got is None:
        return None
    dist = G.distance(tuple(got["footprint"]["center"]), (float(fp["center"][0]), float(fp["center"][1])))
    return {"footprint": got["footprint"], "front_deg": got["front_deg"], "how": "seated", "distance_m": round(dist, 3),
            "reason": got["reason"]}
