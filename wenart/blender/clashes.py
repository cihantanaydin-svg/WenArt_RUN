"""Furniture clashes resolved before the build (user note of 25 Oct 2026: "it's unacceptable to see clashing
furniture at this stage ... fix that one also").

What: ``resolve(building)`` (pure; in place, ``build.prepare`` calls it on the build's building) finds every pair of
built pieces of a level whose plan shapes overlap deeper than ``CLASH_TOL_M`` and whose heights meet, and separates
them. A piece's plan shape is its footprint rectangle, or the two rectangles of an L sofa
(``parametric.l_parts``). Pairs that overlap by design are left: a chair or stool tucked under its table, desk or
counter (up to ``TUCK_SHARE`` of the seat), a kitchen run's members in their counter (the build cuts the sink into
it and stands the hob in a gap), a basin in its vanity, a rug, a wall-hung piece over a floor piece. The piece that
gives way is the lesser one: an accessory (side or coffee table, ottoman, lamp, plant) before seating before an
anchor (bed, sofa, wardrobe, table, counter, bath); then an added piece before a drawn one; then the smaller. It
moves the shortest way out (a separating axis of the two shapes) plus ``GAP_M``, at most ``MAX_MOVE_M`` (drawn) or
``MAX_MOVE_ADDED_M`` (added), and only to a place inside its room, clear of every other piece and of the doorways;
when it has none, the other piece tries; an accessory with no place left is not built. Decor resting on a moved
piece moves with it. Every change keeps ``drawn_footprint`` and is labelled ``adjusted_by_ai`` (by code, the
architect's rule F5) with the reason; ``resolve`` returns ``{"fixed": [...], "left": [...]}``.

27 Oct 2026 (``wenart.furniture.fixture_seat``; user on real06 run 180412: "clashing sink and bath, also bath is not in
proper place"): two drawn fixed pieces (sanitary ware, kitchen appliances standing on their own) that cut each other
are separated first by ``fixture_fix``: the one with the weaker reading slides along its wall to the nearest free place
(at most 0.5 m), else is seated in its drawn outline (a misread or merged outline becomes the real product with its
back on a wall), else the other slides along its wall; the general move below stays the fallback.

Why: the renders and the top-down views of real04 showed a side table standing in the corner sofa's chaise and two
armchairs over their small tables: the mesh check S2 lets a soft seat take 5 cm and its ray test misses open
library meshes, so the clash reached the images. Planning the pieces apart is general and costs nothing at render
time; S2 stays as the measure on the built meshes.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G
from wenart.furniture import fixture_seat as FS

CLASH_TOL_M = 0.03              # a cut under 3 cm is not visible (the S2 class tolerance)
GAP_M = 0.02                    # a separated piece keeps this far from the other
MAX_MOVE_M = 0.50               # CLAUDE.md: a drawn piece moves at most 0.5 m
MAX_MOVE_ADDED_M = 1.00
TUCK_SHARE = 0.55               # a chair may stand this share of its seat under a table
TUCK_DEPTH_M = 0.35
INSIDE_SHARE = 0.97             # a moved piece keeps this share of itself inside its room
DOOR_DEPTH_M = 0.80             # a doorway: the door's width this deep on each side stays free
SEATS = ("chair", "dining_chair", "office_chair", "stool", "bar_stool", "kitchen_stool")
TABLES = ("table_dining", "table", "desk", "kitchen_island", "kitchen_counter", "console_table", "dressing_table",
          "bar_counter", "breakfast_bar")
KITCHEN_RUN = ("kitchen_counter", "kitchen_island")
KITCHEN_MEMBERS = ("sink_kitchen", "stove", "cooktop", "hob", "oven", "dishwasher", "fridge", "washing_machine",
                   "wall_cabinet", "range_hood")
BASINS = (("washbasin", "vanity"), ("washbasin", "bathroom_vanity"), ("tv", "tv_unit"), ("tv", "sideboard"))
FLOOR_ONLY = ("rug", "bath_mat", "carpet", "mat")
SKIP_TYPES = ("unknown", "stair", "stairs")
ANCHORS = ("bed", "bed_double", "bed_single", "bed_bunk", "sofa", "sofa_corner", "wardrobe", "kitchen_counter",
           "kitchen_island", "table_dining", "bathtub", "shower", "toilet", "desk", "bookshelf", "bookcase",
           "dresser", "sideboard", "tv_unit", "fridge", "washbasin", "vanity", "piano")
ACCESSORIES = ("table_coffee", "coffee_table", "side_table", "nightstand", "ottoman", "pouf", "floor_lamp",
               "potted_plant", "plant", "console_table", "shoe_cabinet", "stool", "bench", "laundry_basket")
SOURCE_RANK = {"added_by_ai": 0, "adjusted_by_ai": 1, "inferred": 1, "from_documents": 2}


# --------------------------------------------------------------------------
# Plan shapes (convex parts) and their overlap
# --------------------------------------------------------------------------

def _frame(f: dict):
    fp = f.get("footprint") or {}
    c, s = fp.get("center"), fp.get("size")
    if not c or not s:
        return None
    a = math.radians(float(fp.get("rotation_deg") or 0.0))
    return (float(c[0]), float(c[1])), (float(s[0]), float(s[1])), math.cos(a), math.sin(a)


def shape(f: dict) -> list[list[tuple[float, float]]]:
    """The piece's plan shape as convex parts (world coordinates): the footprint, or an L sofa's two parts."""
    fr = _frame(f)
    if fr is None:
        return []
    (cx, cy), (w, d), ca, sa = fr
    boxes = [(-w / 2.0, w / 2.0, -d / 2.0, d / 2.0)]
    if str(f.get("type")) == "sofa_corner" or f.get("shape") == "L":
        from wenart.blender.parametric import l_parts
        side = f.get("chaise_side") if f.get("chaise_side") in ("left", "right") else "right"
        boxes = l_parts((w, d), side, f.get("chaise_depth"), f.get("seat_depth"), f.get("chaise_width"))
    return [[(cx + ca * x - sa * y, cy + sa * x + ca * y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
            for x0, x1, y0, y1 in boxes]


def _axes(poly):
    out = []
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = x1 - x0, y1 - y0
        n = math.hypot(ex, ey)
        if n > 1e-9:
            out.append((-ey / n, ex / n))
    return out


def _proj(poly, ax):
    vals = [p[0] * ax[0] + p[1] * ax[1] for p in poly]
    return min(vals), max(vals)


def penetration(a: list, b: list) -> tuple[float, list]:
    """``(depth, pushes)`` of two convex polygons: the depth of their overlap along the separating axes (0 when they
    are apart), and every way to push ``a`` out of ``b`` as ``(distance, (dx, dy))`` (unit direction)."""
    depth = math.inf
    pushes = []
    for ax in _axes(a) + _axes(b):
        a0, a1 = _proj(a, ax)
        b0, b1 = _proj(b, ax)
        over = min(a1, b1) - max(a0, b0)
        if over <= 0:
            return 0.0, []
        depth = min(depth, over)
        pushes.append((b1 - a0, ax))                          # a moved along +ax until it clears b
        pushes.append((a1 - b0, (-ax[0], -ax[1])))
    return depth, pushes


def shape_depth(sa: list, sb: list) -> float:
    return max((penetration(p, q)[0] for p in sa for q in sb), default=0.0)


def _area(poly) -> float:
    return abs(0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly))))


def _grid(poly, n: int = 5):
    p0, p1, p2, p3 = poly
    out = []
    for i in range(n):
        s = (i + 0.5) / n
        for j in range(n):
            t = (j + 0.5) / n
            out.append(((1 - s) * (1 - t) * p0[0] + s * (1 - t) * p1[0] + s * t * p2[0] + (1 - s) * t * p3[0],
                        (1 - s) * (1 - t) * p0[1] + s * (1 - t) * p1[1] + s * t * p2[1] + (1 - s) * t * p3[1]))
    return out


def overlap_share(sa: list, sb: list) -> float:
    """The share of shape ``sa`` (sampled) that lies inside shape ``sb``."""
    pts = [p for part in sa for p in _grid(part)]
    if not pts:
        return 0.0
    return sum(1 for p in pts if any(G.point_in_polygon(p, q) for q in sb)) / len(pts)


def inside_share(sa: list, room_poly) -> float:
    pts = [p for part in sa for p in _grid(part)]
    return sum(1 for p in pts if G.point_in_polygon(p, room_poly)) / len(pts) if pts else 0.0


def z_range(f: dict) -> tuple[float, float]:
    bottom = float(f.get("mount_bottom_m") or 0.0)
    h = f.get("height")
    if h is None:
        h = ((f.get("asset") or {}).get("bbox_m") or [0.0, 0.0, 0.8])[2]
    return bottom, bottom + float(h or 0.8)


# --------------------------------------------------------------------------
# Which pairs clash, and who gives way
# --------------------------------------------------------------------------

def by_design(f: dict, g: dict, sf: list, sg: list, depth: float) -> Optional[str]:
    """Why ``f`` and ``g`` may overlap (None when they may not)."""
    tf, tg = str(f.get("type") or ""), str(g.get("type") or "")
    for a, b, sa, sb in ((f, g, sf, sg), (g, f, sg, sf)):
        ta, tb = str(a.get("type") or ""), str(b.get("type") or "")
        if ta in SEATS and tb in TABLES and depth <= TUCK_DEPTH_M and overlap_share(sa, sb) <= TUCK_SHARE:
            return "a seat tucked under its table"
        if ta in KITCHEN_MEMBERS and tb in KITCHEN_RUN:
            return "a member of the kitchen run (built into it)"
        if (ta, tb) in BASINS:
            return "a basin or set on its unit"
    if tf in KITCHEN_RUN and tg in KITCHEN_RUN:
        return "two parts of a kitchen run"
    zf, zg = z_range(f), z_range(g)
    if min(zf[1], zg[1]) - max(zf[0], zg[0]) <= 0.02:
        return "one hangs over the other"
    return None


def _tier(f: dict) -> int:
    t = str(f.get("type") or "")
    return 0 if t in ACCESSORIES else (2 if t in ANCHORS else 1)


def _rank(f: dict) -> tuple:
    sa = shape(f)
    return (_tier(f), SOURCE_RANK.get(str(f.get("source") or ""), 1), sum(_area(p) for p in sa))


def doorways(building: dict, level_id) -> list[list]:
    """The doorway boxes of a level: each door's width, ``DOOR_DEPTH_M`` deep on both sides of its wall."""
    walls = {w["id"]: w for w in building.get("walls") or []}
    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("type") != "door" or o.get("level_id") != level_id or w is None:
            continue
        (ax, ay), (bx, by) = w["start"][:2], w["end"][:2]
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        t = (o["center"][0] - ax) * ux + (o["center"][1] - ay) * uy
        cx, cy = ax + ux * t, ay + uy * t
        h = float(o.get("width") or 0.9) / 2.0
        reach = float(w.get("thickness") or 0.2) / 2.0 + DOOR_DEPTH_M
        nx, ny = -uy, ux
        out.append([(cx - ux * h - nx * reach, cy - uy * h - ny * reach), (cx + ux * h - nx * reach, cy + uy * h - ny * reach),
                    (cx + ux * h + nx * reach, cy + uy * h + ny * reach), (cx - ux * h + nx * reach, cy - uy * h + ny * reach)])
    return out


def _moved(f: dict, dx: float, dy: float) -> dict:
    g = dict(f)
    fp = dict(f["footprint"])
    fp["center"] = [round(float(fp["center"][0]) + dx, 4), round(float(fp["center"][1]) + dy, 4)]
    g["footprint"] = fp
    return g


def clashes_with(f: dict, sf: list, others: list) -> list:
    """The pieces of ``others`` (``[(piece, shape)]``) that ``f`` clashes with."""
    out = []
    for g, sg in others:
        if g is f:
            continue
        d = shape_depth(sf, sg)
        if d > CLASH_TOL_M and by_design(f, g, sf, sg, d) is None:
            out.append(g)
    return out


def find_place(f: dict, other_shape: list, peers: list, room_poly, doors: list) -> Optional[tuple]:
    """The shortest move of ``f`` out of ``other_shape`` to a free place (``(dx, dy, distance)``), or None."""
    return find_unit_place([f], other_shape, peers, {f.get("room_id"): room_poly} if room_poly else {}, doors)


def _limit(members: list) -> float:
    if all(_tier(m) == 0 for m in members):
        return MAX_MOVE_ADDED_M                       # an accessory may go further to find its place
    if all(m.get("source") == "added_by_ai" for m in members):
        return MAX_MOVE_ADDED_M
    return MAX_MOVE_M


def find_unit_place(members: list, other_shape: list, peers: list, room_polys: dict, doors: list,
                    stay: Optional[dict] = None) -> Optional[tuple]:
    """The shortest move of a unit (one piece, or a table with its seats) out of ``other_shape`` to a place where
    every member stays inside its room, clear of every piece outside the unit and of the doorways it was not in:
    ``(dx, dy, distance)`` or None. With ``stay`` (a seat at its own table) the seat may stop where it stands
    tucked under it (``by_design``) instead of all the way out."""
    ids = {m.get("id") for m in members}
    shapes = {m.get("id"): shape(m) for m in members}
    was_in = {m.get("id"): (inside_share(shapes[m.get("id")], room_polys[m.get("room_id")])
                            if room_polys.get(m.get("room_id")) else 1.0) for m in members}
    in_door = {(m.get("id"), k) for m in members for k, d in enumerate(doors)
               if shape_depth(shapes[m.get("id")], [d]) > CLASH_TOL_M}
    outside = [(p, sp) for p, sp in peers if p.get("id") not in ids]
    cands = []
    for m in members:
        for part in shapes[m.get("id")]:
            for q in other_shape:
                depth, pushes = penetration(part, q)
                if depth > 0:
                    cands += [(dist + GAP_M, ax) for dist, ax in pushes]
                    if stay is not None:          # out to a tucked stand: its back at the table's edge
                        cands += [(max(GAP_M, dist - tuck), ax) for dist, ax in pushes
                                  for tuck in (0.30, 0.25, 0.20, 0.15, 0.10)]
    limit = _limit(members)
    seen = set()
    for dist, ax in sorted(cands, key=lambda c: c[0]):
        if dist > limit:
            break
        key = (round(dist, 3), round(ax[0], 3), round(ax[1], 3))
        if key in seen:
            continue
        seen.add(key)
        dx, dy = ax[0] * dist, ax[1] * dist
        ok = True
        for m in members:
            g = _moved(m, dx, dy)
            sg = shape(g)
            room = room_polys.get(m.get("room_id"))
            if room and inside_share(sg, room) + 1e-9 < min(INSIDE_SHARE, was_in[m.get("id")]):
                ok = False
            elif shape_depth(sg, other_shape) > CLASH_TOL_M and (
                    stay is None or by_design(g, stay, sg, other_shape, shape_depth(sg, other_shape)) is None):
                ok = False
            elif clashes_with(g, sg, outside):
                ok = False
            elif any(shape_depth(sg, [d]) > CLASH_TOL_M for k, d in enumerate(doors) if (m.get("id"), k) not in in_door):
                ok = False
            if not ok:
                break
        if ok:
            return dx, dy, dist
    return None


def table_sets(group: list) -> dict:
    """``{piece id: [members]}``: a table (``TABLES``, not a kitchen run) with the seats that stand at it (their
    shape within 0.15 m of it; a seat at two tables goes to the one it overlaps most) moves as one unit."""
    tables = [t for t in group if str(t.get("type")) in TABLES and str(t.get("type")) not in KITCHEN_RUN]
    seats = [s for s in group if str(s.get("type")) in SEATS]
    sets = {t["id"]: [t] for t in tables}
    for s in seats:
        ss = shape(s)
        best = None
        for t in tables:
            st = shape(t)
            near = shape_depth([_grow(p, 0.15) for p in ss], st)
            if near > 0:
                share = overlap_share(ss, st)
                if best is None or share > best[0]:
                    best = (share, t["id"])
        if best is not None:
            sets[best[1]].append(s)
    out = {}
    for members in sets.values():
        for m in members:
            out[m["id"]] = members
    return out


def _grow(poly, d: float):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        vx, vy = x - cx, y - cy
        n = math.hypot(vx, vy) or 1.0
        out.append((x + vx / n * d * 1.42, y + vy / n * d * 1.42))
    return out


FAMILIES = (("wardrobe", "dresser", "cabinet", "bookshelf", "bookcase", "shoe_cabinet", "sideboard", "tv_unit",
             "chest_of_drawers"),
            ("sofa", "sofa_corner", "armchair"), ("bed", "bed_double", "bed_single", "bed_bunk"),
            ("table_dining", "table", "desk", "console_table"), ("toilet",), ("bathtub", "shower"))


def duplicate(f: dict, g: dict, sf: list, sg: list) -> bool:
    """Two drawn pieces of one kind (``FAMILIES``) where the smaller lies at least 60 % inside the larger: one
    object read twice (real04: a cupboard read as its outline and as its "dolap" block)."""
    tf, tg = str(f.get("type") or ""), str(g.get("type") or "")
    if not (tf == tg or any(tf in fam and tg in fam for fam in FAMILIES)):
        return False
    small, big = (sf, sg) if sum(_area(p) for p in sf) <= sum(_area(p) for p in sg) else (sg, sf)
    return overlap_share(small, big) >= 0.6


def _apply_move(members: list, dx: float, dy: float, decor: list, reason: str) -> None:
    for m in members:
        m.setdefault("drawn_footprint", dict(m["footprint"]))
        m["footprint"] = _moved(m, dx, dy)["footprint"]
        m["adjusted_by_ai"] = {"by": "code", "rule": "architect F5", "reason": reason}
        for d in decor:
            if d.get("host_id") == m["id"] and d.get("center"):
                c = list(d["center"])
                c[0], c[1] = round(float(c[0]) + dx, 4), round(float(c[1]) + dy, 4)
                d["center"] = c


def _not_built(p: dict, reason: str) -> None:
    p["build"] = False
    p["not_built_reason"] = reason
    p["adjusted_by_ai"] = {"by": "code", "rule": "architect F5", "reason": reason}


def resolve(building: dict) -> dict:
    """Separate the clashing pieces of ``building`` (module docstring). Returns ``{"fixed": [{"id", "other",
    "action": "moved" | "not_built", "distance_m", "members", "reason"}], "left": [{"id", "other", "depth_m"}]}``.
    Order: a piece read twice is built once; then the seats pushed into their own table are pulled out; then every
    other clash moves the lesser unit (a table set as one)."""
    rooms = {r["id"]: r["polygon"] for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    pieces = [f for f in building.get("furniture") or [] if f.get("build") is not False
              and str(f.get("type") or "") not in SKIP_TYPES + FLOOR_ONLY and _frame(f) is not None]
    decor = [d for d in building.get("decor") or [] if isinstance(d, dict)]
    fixed: list = []
    left: list = []
    by_level: dict = {}
    for f in pieces:
        by_level.setdefault(f.get("level_id"), []).append(f)
    for lid, group in by_level.items():
        doors = doorways(building, lid)
        live = lambda: [p for p in group if p.get("build") is not False]          # noqa: E731
        # 1. one object read twice: the smaller copy is not built
        for i, f in enumerate(group):
            for g in group[i + 1:]:
                if f.get("build") is False or g.get("build") is False:
                    continue
                sf, sg = shape(f), shape(g)
                if shape_depth(sf, sg) > CLASH_TOL_M and duplicate(f, g, sf, sg):
                    small, big = (f, g) if sum(_area(p) for p in sf) <= sum(_area(p) for p in sg) else (g, f)
                    reason = (f"architect F5: {small['id']} ({small.get('type')}) lies inside {big['id']} "
                              f"({big.get('type')}): one object read twice; built once")
                    _not_built(small, reason)
                    fixed.append({"id": small["id"], "other": big["id"], "action": "not_built", "distance_m": None,
                                  "members": [small["id"]], "reason": reason})
        for _round in range(4):
            changed = False
            sets = table_sets(live())
            pieces_now = live()
            for i, f in enumerate(pieces_now):
                for g in pieces_now[i + 1:]:
                    if f.get("build") is False or g.get("build") is False:
                        continue
                    sf, sg = shape(f), shape(g)
                    depth = shape_depth(sf, sg)
                    if depth <= CLASH_TOL_M or by_design(f, g, sf, sg, depth):
                        continue
                    # 27 Oct 2026 (module docstring): two drawn fixtures keep their walls (slide, else seat)
                    if FS.fixture_pair(f, g):
                        hit = fixture_fix(f, g, depth, live(), rooms, doors, decor)
                        if hit is not None:
                            fixed.append(hit)
                            changed = True
                            continue
                    peers = [(p, shape(p)) for p in live()]
                    same_set = sets.get(f["id"]) is not None and sets.get(f["id"]) is sets.get(g["id"])
                    order = sorted((f, g), key=_rank)
                    tries = [order] + ([order[::-1]] if not (_tier(order[1]) == 2 and _tier(order[0]) == 0) else [])
                    done = False
                    for mover, stay in tries:
                        # a seat pulled out of its own table moves alone; otherwise a table set moves as one
                        members = [mover] if same_set else sets.get(mover["id"], [mover])
                        if not same_set and stay in members:
                            members = [mover]
                        spot = find_unit_place(members, shape(stay), peers, rooms, doors,
                                               stay=stay if same_set and str(mover.get("type")) in SEATS else None)
                        if spot is None:
                            continue
                        dx, dy, dist = spot
                        what = (f"{mover['id']} ({mover.get('type')})" if len(members) == 1 else
                                f"the set of {', '.join(m['id'] for m in members)}")
                        reason = (f"architect F5: {mover['id']} ({mover.get('type')}) cut {stay['id']} "
                                  f"({stay.get('type')}) by {depth:.2f} m; {what} moved {dist:.2f} m clear of it "
                                  f"(inside its room, clear of the other pieces and the doorways)")
                        _apply_move(members, dx, dy, decor, reason)
                        fixed.append({"id": mover["id"], "other": stay["id"], "action": "moved",
                                      "distance_m": round(dist, 3), "members": [m["id"] for m in members],
                                      "reason": reason})
                        done = changed = True
                        break
                    if done:
                        continue
                    acc = [p for p in order if _tier(p) == 0]
                    if acc:
                        p = acc[0]
                        other = g if p is f else f
                        reason = (f"architect F5: it cut {other['id']} ({other.get('type')}) by {depth:.2f} m and no "
                                  f"free place lies within {_limit([p]):.1f} m; not built")
                        _not_built(p, reason)
                        fixed.append({"id": p["id"], "other": other["id"], "action": "not_built", "distance_m": None,
                                      "members": [p["id"]], "reason": reason})
                        changed = True
            if not changed:
                break
        left += remaining(group)
    return {"fixed": fixed, "left": left}


def must_clear(f: dict, p: dict) -> bool:
    """``f`` may not stand in ``p``: not built into it (a basin in its vanity, a sink in its counter), their heights
    meet (a wall-hung piece over a floor piece is free), neither lies on the floor (a rug)."""
    if p is f or p.get("build") is False or str(p.get("type") or "") in SKIP_TYPES + FLOOR_ONLY:
        return False
    tf, tp = str(f.get("type") or ""), str(p.get("type") or "")
    if FS.hosted_pair(f, p) or (tf, tp) in BASINS or (tp, tf) in BASINS:
        return False
    if (tf in KITCHEN_MEMBERS and tp in KITCHEN_RUN) or (tp in KITCHEN_MEMBERS and tf in KITCHEN_RUN):
        return False
    zf, zp = z_range(f), z_range(p)
    return min(zf[1], zp[1]) - max(zf[0], zp[0]) > 0.02


def fixture_fix(f: dict, g: dict, depth: float, live: list, rooms: dict, doors: list, decor: list) -> Optional[dict]:
    """27 Oct 2026 (``wenart.furniture.fixture_seat``; user on real06 run 180412: "clashing sink and bath, also bath is
    not in proper place"): two drawn fixed pieces that cut each other. The one with the weaker reading
    (``fixture_seat.gives_way``) slides along its wall to the nearest free place within 0.5 m, else is seated in its
    drawn outline (a misread or merged outline: the real product, its back on a wall and along it); else the other
    slides along its wall. Inside its room, clear of every other piece it may not stand in and of the doorways it was
    not in. Moved in place (``drawn_footprint`` kept, ``adjusted_by_ai`` by code with rule ``architect F5``, decor on it
    follows); returns the ``resolve`` record or None. Why: the general move (``find_unit_place``) pushes a piece out
    along any separating axis, which takes a basin off its wall or leaves the room; real06's bath, read as one turned
    outline with its screen and the vanity's edge, cut its basin 0.33 m and neither found a place."""
    mover = FS.gives_way(f, g)
    stay = g if mover is f else f
    for piece, other, allow_seat in ((mover, stay, True), (stay, mover, False)):
        room = rooms.get(piece.get("room_id"))
        if not room:
            continue
        sp = shape(piece)
        obstacles = [part for p in live if must_clear(piece, p) for part in shape(p)]
        obstacles += [d for d in doors if shape_depth(sp, [d]) <= CLASH_TOL_M]
        fix = FS.free_fixture(piece, room, obstacles, allow_seat=allow_seat)
        if fix is None:
            continue
        reason = (f"architect F5: {piece['id']} ({piece.get('type')}) cut {other['id']} ({other.get('type')}) by "
                  f"{depth:.2f} m; {piece['id']}: {fix['reason']} (inside its room, clear of the other pieces and the "
                  f"doorways)")
        apply_fixture(piece, fix, {"by": "code", "rule": "architect F5", "reason": reason}, decor)
        return {"id": piece["id"], "other": other["id"], "action": "moved" if fix["how"] == "slid" else "seated",
                "distance_m": round(float(fix["distance_m"]), 3), "members": [piece["id"]], "reason": reason}
    return None


def apply_fixture(piece: dict, fix: dict, label: dict, decor: list) -> None:
    """``fixture_seat.free_fixture``'s place carried out on ``piece`` (in place): ``drawn_footprint`` kept, the new
    footprint (and, seated, its front away from its wall), the fitted library record following a new product size
    (``refit_asset``: the build scales the model by the recorded fit), ``label`` as ``adjusted_by_ai`` (an earlier
    record kept under ``previous``), the decor resting on it moved along."""
    old = piece["footprint"]
    dx = float(fix["footprint"]["center"][0]) - float(old["center"][0])
    dy = float(fix["footprint"]["center"][1]) - float(old["center"][1])
    piece.setdefault("drawn_footprint", dict(old))
    piece["footprint"] = dict(fix["footprint"])
    if fix.get("how") == "seated" and fix.get("front_deg") is not None:
        piece["front_deg"] = fix["front_deg"]
    refit_asset(piece, old.get("size"), by=str(label.get("rule") or label.get("by") or "code"))
    label = dict(label)
    if isinstance(piece.get("adjusted_by_ai"), dict):
        label["previous"] = [dict(piece["adjusted_by_ai"])]
    piece["adjusted_by_ai"] = label
    for d in decor:
        if d.get("host_id") == piece["id"] and d.get("center"):
            c = list(d["center"])
            c[0], c[1] = round(float(c[0]) + dx, 4), round(float(c[1]) + dy, 4)
            d["center"] = c


def refit_asset(piece: dict, old_size, by: str = "architect F5") -> None:
    """A fitted library model follows a footprint size the build changed (``apply_fixture``: a fixture seated at
    another product size before the build): the scene builder scales the model by the recorded ``fit_scale``, so a
    uniform fit is scaled by the new width over the fitted width (the fit's rule: the drawn width), a stretched one
    by each side's ratio; ``bbox_m`` follows and ``refit`` records it. Nothing for a module or parametric piece (built
    on the footprint) or an unchanged size."""
    a = piece.get("asset")
    size = (piece.get("footprint") or {}).get("size")
    if not isinstance(a, dict) or a.get("method", "library") != "library" or not a.get("fit_scale") \
            or not old_size or not size:
        return
    w0, d0 = float(old_size[0]), float(old_size[1])
    w1, d1 = float(size[0]), float(size[1])
    if abs(w1 - w0) < 1e-4 and abs(d1 - d0) < 1e-4:
        return
    box = [float(v) for v in a.get("bbox_m") or [w0, d0, 0.0]]
    if a.get("scaling") == "uniform":
        k = w1 / box[0] if box[0] > 1e-9 else w1 / w0
        ks = (k, k, k)
    else:
        ks = (w1 / box[0] if box[0] > 1e-9 else w1 / w0, d1 / box[1] if len(box) > 1 and box[1] > 1e-9 else d1 / d0,
              1.0)
    a["fit_scale"] = [round(float(s) * k, 4) for s, k in zip(list(a["fit_scale"])[:3], ks)]
    a["bbox_m"] = [round(v * k, 4) for v, k in zip(box[:3], ks)]
    a["refit"] = {"by": by, "from_size": [round(w0, 4), round(d0, 4)],
                  "factor": [round(k, 4) for k in ks]}


def remaining(group: list) -> list[dict]:
    """The pairs of ``group`` that still clash: ``[{"id", "other", "depth_m"}]``."""
    out = []
    shapes = [(f, shape(f)) for f in group if f.get("build") is not False]
    for i, (f, sf) in enumerate(shapes):
        for g, sg in shapes[i + 1:]:
            depth = shape_depth(sf, sg)
            if depth > CLASH_TOL_M and by_design(f, g, sf, sg, depth) is None:
                out.append({"id": f["id"], "other": g["id"], "depth_m": round(depth, 3)})
    return out
