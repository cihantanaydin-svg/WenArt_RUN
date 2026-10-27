"""Verandas and terraces furnished like the ones in good photos (27 Oct 2026, lesson UL42; user: "veranda is not like
a veranda"; real06's 22.8 m2 VERANDA was an empty paved slab under a light roof).

What (pure; the decor stage calls ``furnish``):

- ``SPACE_KINDS``: the outdoor spaces (``site.outdoor_spaces`` of ``wenart.levels.outdoor``) that are furnished:
  veranda, porch, terrace, patio, deck, loggia (a balcony is a room of its own: its group comes from the program).
- ``plan_space(space, building, recipe)``: the best placement of the space's set (``SETS``: a lounge of a sofa, a
  coffee table and two armchairs; a compact lounge; a bistro pair), the sofa's back to the house wall (an edge of the
  space on the building's outline), else to another edge: every piece inside the space (``INSET_M`` in), clear of the
  door zones (``DOOR_CLEAR_M`` around each door of the space), the columns and the steps' landing (``STEPS_CLEAR_M``),
  with a ``WALKWAY_M`` path from each door to the steps free; the covered part (the roof) first, then the middle of
  the wall. Then planters (decor ``plant_large``) at the free outer corners and beside the columns (the recipe's count,
  ``PLANTERS_DEFAULT`` without one), an outdoor rug under the lounge and a lantern (a candle) on its table.
- ``furnish(building, recipes)``: the building with the pieces (``source: added_by_ai``, ``outdoor_space``,
  ``open_air`` models first in the fit) and the decor items added, and the notes; a space with furniture already
  (``outdoor_space`` set) is left as it is.

Why: the photos of a veranda all show a place to sit (a lounge or a dining set), plants in big pots, a rug, a
lantern; the pipeline furnished rooms only, so an outdoor space stayed a bare slab.
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

SPACE_KINDS = ("veranda", "porch", "terrace", "patio", "deck", "loggia")
MIN_AREA_M2 = 4.0
INSET_M = 0.05                # every piece this far inside the space's edge
DOOR_CLEAR_M = 1.0            # a door's zone: this radius around its centre stays free
STEPS_CLEAR_M = 1.0           # the steps' landing: this far from the steps' edge stays free
COLUMN_CLEAR_M = 0.15
WALKWAY_M = 0.9               # a path this wide from each door to the steps stays free
WALL_GAP_M = 0.05             # the sofa's back this far from the wall
SLIDE_STEP_M = 0.25           # candidate positions along an edge
WALL_TOUCH_M = 0.45           # an edge within this of the rooms (a wall thickness) is the house wall
PLANTERS_DEFAULT = 3
PLANTER_SIZE_M = 0.55
PLANTER_INSET_M = 0.40
PLANTER_GAP_M = 0.35          # a planter keeps this from the pieces and the other planters
COLUMN_PLANTER_OFF_M = 0.80
RUG_MARGIN_M = 0.30
# set -> [(type, (w, d), (x, y) of the centre in the wall frame: x along the wall, y out from it, front: "out" | "in"
# | "left" | "right")]; the sofa's back at y = WALL_GAP_M
SETS: dict[str, list[tuple[str, tuple[float, float], tuple[float, float], str]]] = {
    "lounge": [("sofa", (2.0, 0.85), (0.0, 0.475), "out"), ("table_coffee", (1.0, 0.55), (0.0, 1.575), "none"),
               ("armchair", (0.75, 0.8), (-0.55, 2.65), "in"), ("armchair", (0.75, 0.8), (0.55, 2.65), "in")],
    "lounge_side": [("sofa", (2.0, 0.85), (0.0, 0.475), "out"), ("table_coffee", (1.0, 0.55), (0.0, 1.575), "none"),
                    ("armchair", (0.75, 0.8), (-1.6, 1.45), "right"), ("armchair", (0.75, 0.8), (1.6, 1.45), "left")],
    "compact": [("sofa", (1.8, 0.8), (0.0, 0.45), "out"), ("table_coffee", (0.9, 0.5), (0.0, 1.5), "none")],
    "bistro": [("armchair", (0.7, 0.75), (-0.55, 0.45), "out"), ("armchair", (0.7, 0.75), (0.55, 0.45), "out"),
               ("table_coffee", (0.6, 0.6), (0.0, 1.15), "none")],
}
SET_ORDER = ("lounge", "lounge_side", "compact", "bistro")


def _poly(points) -> Optional[Polygon]:
    try:
        p = Polygon([tuple(map(float, q[:2])) for q in points or []])
        return p if p.is_valid and p.area > 0 else p.buffer(0)
    except Exception:  # noqa: BLE001
        return None


def _outline(building: dict, level_id: str):
    """The union of the level's rooms (the house's footprint on that level)."""
    polys = [_poly(r.get("polygon")) for r in building.get("rooms") or [] if r.get("level_id") == level_id]
    polys = [p for p in polys if p is not None and not p.is_empty]
    return unary_union(polys) if polys else None


def _door_points(building: dict, space: dict) -> list[tuple[float, float]]:
    ids = set(space.get("doors") or [])
    out = []
    for o in building.get("openings") or []:
        if o.get("id") in ids and o.get("center"):
            out.append((float(o["center"][0]), float(o["center"][1])))
    return out


def _edges(poly: Polygon) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    pts = list(poly.exterior.coords)[:-1]
    if not poly.exterior.is_ccw:
        pts = pts[::-1]
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


HOUSE_SHARE = 0.6             # an edge with this share of its length along the house is a house wall


def _along(house_zone, a, b) -> bool:
    """True when ``HOUSE_SHARE`` of the edge a-b runs within ``WALL_TOUCH_M`` of the house (an edge that only ends at
    the house is not a house wall)."""
    if house_zone is None:
        return False
    line = LineString([a, b])
    return line.length > 0 and line.intersection(house_zone).length >= HOUSE_SHARE * line.length


def _rect(cx, cy, w, d, ang) -> Polygon:
    c, s = math.cos(ang), math.sin(ang)
    pts = []
    for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)):
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return Polygon(pts)


def _front_deg(axis_deg: float, normal_deg: float, front: str) -> Optional[float]:
    return {"out": normal_deg, "in": normal_deg + 180.0, "left": axis_deg + 180.0, "right": axis_deg,
            "none": None}[front]


def _blocked(building: dict, space: dict, poly: Polygon):
    """The zones no piece may cover: doors, columns, the steps' landing, the walkways from the doors to the steps."""
    zones = [Point(p).buffer(DOOR_CLEAR_M) for p in _door_points(building, space)]
    for c in space.get("columns") or []:
        if c.get("center"):
            zones.append(Point(*map(float, c["center"][:2])).buffer(float(c.get("size_m") or 0.4) / 2.0 + COLUMN_CLEAR_M))
    steps = space.get("steps") if isinstance(space.get("steps"), dict) else None
    mid = None
    if steps and steps.get("edge"):
        edge = LineString([tuple(map(float, p[:2])) for p in steps["edge"]])
        zones.append(edge.buffer(STEPS_CLEAR_M))
        mid = edge.interpolate(0.5, normalized=True)
    if mid is not None:
        for p in _door_points(building, space):
            zones.append(LineString([p, (mid.x, mid.y)]).buffer(WALKWAY_M / 2.0))
    return unary_union(zones) if zones else None


def plan_space(space: dict, building: dict, recipe: Optional[dict] = None) -> dict:
    """The set placed on one outdoor space (module docstring): ``{"set", "pieces": [{type, center, size, rotation_deg,
    front_deg}], "planters": [centre], "rug": {center, size, rotation_deg} | None, "edge", "covered", "notes"}``;
    ``pieces`` empty when no set fits (the notes say why)."""
    poly = _poly(space.get("polygon"))
    notes: list[str] = []
    if poly is None or poly.area < MIN_AREA_M2:
        return {"set": None, "pieces": [], "planters": [], "rug": None, "notes": ["too small for a set"]}
    inner = poly.buffer(-INSET_M, join_style=2)
    blocked = _blocked(building, space, poly)
    roof = _poly(((space.get("roof") or {}).get("polygon")))
    house = _outline(building, space.get("level_id"))
    house_zone = house.buffer(WALL_TOUCH_M) if house is not None else None
    order = list(SET_ORDER)
    if recipe and (recipe.get("layers") or {}).get("dining_set", {}).get("share", 0) > \
            (recipe.get("layers") or {}).get("lounge_set", {}).get("share", 0):
        notes.append("the recipe shows dining sets more often than lounges: a lounge is placed (no dining set yet)")
    best = None
    # the house wall first (a sofa backed to it, facing the garden), then the larger set; another edge only when no
    # set fits along the house
    for name in order:
        for (a, b) in _edges(poly):
            ex, ey = b[0] - a[0], b[1] - a[1]
            length = math.hypot(ex, ey)
            if length < 1.0:
                continue
            ux, uy = ex / length, ey / length
            nx, ny = -uy, ux                                  # ccw polygon: the inside is on the left
            on_house = _along(house_zone, a, b)
            axis = math.degrees(math.atan2(uy, ux))
            normal = math.degrees(math.atan2(ny, nx))
            k = 0
            while k * SLIDE_STEP_M <= length:
                t = k * SLIDE_STEP_M
                k += 1
                ox, oy = a[0] + ux * t, a[1] + uy * t
                placed, polys, ok = [], [], True
                for ftype, (w, d), (x, y), front in SETS[name]:
                    cx = ox + ux * x + nx * (y + WALL_GAP_M - 0.02)     # the back 0.03 inside the inset line
                    cy = oy + uy * x + ny * (y + WALL_GAP_M - 0.02)
                    rect = _rect(cx, cy, w, d, math.radians(axis))
                    if not inner.contains(rect) or (blocked is not None and rect.intersects(blocked)):
                        ok = False
                        break
                    fdeg = _front_deg(axis, normal, front)
                    # the builder's frame: a piece's front is its rotation + 270 (the box's local -y)
                    rot = (fdeg + 90.0) if fdeg is not None else (axis + 180.0)
                    placed.append({"type": ftype, "center": [round(cx, 4), round(cy, 4)], "size": [w, d],
                                   "rotation_deg": round(rot % 360.0, 3),
                                   "front_deg": None if fdeg is None else round(fdeg % 360.0, 3)})
                    polys.append(rect)
                if not ok:
                    continue
                group = unary_union(polys)
                covered = group.intersection(roof).area / group.area if roof is not None and group.area else 0.0
                centre = abs(t - length / 2.0)
                score = (0 if on_house else 1, SET_ORDER.index(name), -round(covered, 2), round(centre, 2))
                if best is None or score < best[0]:
                    best = (score, name, placed, group, (a, b), covered, axis)
    if best is None:
        return {"set": None, "pieces": [], "planters": [], "rug": None,
                "notes": notes + ["no set fits clear of the doors, the columns, the steps and the walkway"]}
    _score, name, pieces, group, edge, covered, axis = best
    rug = None
    if name in ("lounge", "lounge_side", "compact"):
        minx, miny, maxx, maxy = _local_bounds(group, edge[0], axis)
        w, d = maxx - minx + 2 * RUG_MARGIN_M - 0.6, maxy - miny + 2 * RUG_MARGIN_M - 0.9
        cx_l, cy_l = (minx + maxx) / 2.0, (miny + maxy) / 2.0 + 0.3
        c, s = math.cos(math.radians(axis)), math.sin(math.radians(axis))
        rug = {"center": [round(edge[0][0] + cx_l * c - cy_l * s, 4), round(edge[0][1] + cx_l * s + cy_l * c, 4)],
               "size": [round(max(1.6, w), 3), round(max(1.2, d), 3)], "rotation_deg": round(axis % 360.0, 3)}
        if not inner.contains(_rect(rug["center"][0], rug["center"][1], rug["size"][0], rug["size"][1],
                                    math.radians(axis))):
            rug = None
            notes.append("no outdoor rug: it would run past the space's edge")
    want = PLANTERS_DEFAULT
    if recipe and "planters" in (recipe.get("layers") or {}):
        want = max(1, int(round(float((recipe["layers"]["planters"] or {}).get("median") or PLANTERS_DEFAULT))))
    planters = _planters(space, building, poly, inner, blocked, group, house, want)
    return {"set": name, "pieces": pieces, "planters": planters, "rug": rug, "edge": [list(edge[0]), list(edge[1])],
            "covered": round(covered, 3), "notes": notes}


def _local_bounds(group, origin, axis_deg):
    c, s = math.cos(math.radians(axis_deg)), math.sin(math.radians(axis_deg))
    xs, ys = [], []
    for x, y in group.convex_hull.exterior.coords:
        dx, dy = x - origin[0], y - origin[1]
        xs.append(dx * c + dy * s)
        ys.append(-dx * s + dy * c)
    return min(xs), min(ys), max(xs), max(ys)


def _planters(space, building, poly, inner, blocked, group, house, want: int) -> list[list[float]]:
    """Up to ``want`` planter centres: the outer corners off the house wall, then beside the columns; each inside the
    space, clear of the blocked zones, the set and the other planters, farthest from the chosen ones first."""
    cands = []
    pts = list(poly.exterior.coords)[:-1]
    centroid = poly.centroid
    for p in pts:
        q = Point(p)
        if house is not None and q.distance(house) <= WALL_TOUCH_M:
            continue
        dx, dy = centroid.x - p[0], centroid.y - p[1]
        dl = math.hypot(dx, dy) or 1.0
        cands.append((p[0] + dx / dl * PLANTER_INSET_M * 1.4, p[1] + dy / dl * PLANTER_INSET_M * 1.4))
    for (a, b) in _edges(poly):                       # then along the open edges (the railing side)
        ln = LineString([a, b])
        if ln.length < PLANTER_SIZE_M or _along(house.buffer(WALL_TOUCH_M) if house is not None else None, a, b):
            continue
        ux, uy = (b[0] - a[0]) / ln.length, (b[1] - a[1]) / ln.length
        n = int(ln.length // 0.5)
        for i in range(1, n):
            t = i * ln.length / n
            cands.append((a[0] + ux * t - uy * PLANTER_INSET_M, a[1] + uy * t + ux * PLANTER_INSET_M))
    for c in space.get("columns") or []:
        if not c.get("center"):
            continue
        cx, cy = map(float, c["center"][:2])
        for ang in range(0, 360, 45):
            cands.append((cx + COLUMN_PLANTER_OFF_M * math.cos(math.radians(ang)),
                          cy + COLUMN_PLANTER_OFF_M * math.sin(math.radians(ang))))
    chosen: list[tuple[float, float]] = []
    half = PLANTER_SIZE_M / 2.0
    for _ in range(want):
        best, best_d = None, -1.0
        for c in cands:
            box = Point(c).buffer(half)
            if not inner.contains(box) or (blocked is not None and box.intersects(blocked)) \
                    or box.distance(group) < PLANTER_GAP_M or any(Point(c).distance(Point(o)) < PLANTER_SIZE_M +
                                                                  PLANTER_GAP_M for o in chosen):
                continue
            d = min([Point(c).distance(Point(o)) for o in chosen] or [99.0])
            if d > best_d + 1e-9:
                best, best_d = c, d
        if best is None:
            break
        chosen.append(best)
    return [[round(x, 4), round(y, 4)] for x, y in chosen]


def _next_furniture_id(building: dict, level_id: str) -> str:
    from wenart.furniture.edit_ops import _next_id

    return _next_id(building, level_id)


def _next_decor_id(building: dict, level_id: str) -> str:
    import re

    pat = re.compile(rf"^dec_{re.escape(level_id)}_(\d+)$")
    nums = [int(m.group(1)) for d in building.get("decor") or [] for m in [pat.match(str(d.get("id") or ""))] if m]
    return f"dec_{level_id}_{max(nums, default=0) + 1:03d}"


def furnish(building: dict, recipes: Optional[dict] = None) -> tuple[dict, list[str]]:
    """The building (a copy) with every unfurnished outdoor space of ``SPACE_KINDS`` furnished (module docstring)."""
    import copy

    from wenart.style import references as RF

    out = copy.deepcopy(building)
    out.setdefault("furniture", [])
    out.setdefault("decor", [])
    notes: list[str] = []
    site = out.get("site") if isinstance(out.get("site"), dict) else {}
    done = {f.get("outdoor_space") for f in out["furniture"] if f.get("outdoor_space")}
    for space in site.get("outdoor_spaces") or []:
        kind = str(space.get("kind") or "").lower()
        if kind not in SPACE_KINDS or space.get("id") in done or not space.get("level_id"):
            continue
        key = RF.space_of(None, outdoor=kind) or "terrace"
        recipe = (recipes or {}).get(key)
        plan = plan_space(space, out, recipe)
        sid, level = space["id"], space["level_id"]
        why = (f"recipe: good {key} photos show a place to sit, plants in big pots, a rug and a lantern "
               f"({'built-in designer defaults' if not recipe or recipe.get('source') == 'default' else str(recipe.get('n')) + ' reference photos'})")
        if not plan["pieces"]:
            notes.append(f"{sid}: no outdoor set: {'; '.join(plan['notes'])}")
            continue
        table = None
        for p in plan["pieces"]:
            fid = _next_furniture_id(out, level)
            item = {"id": fid, "level_id": level, "room_id": None, "type": p["type"], "type_raw": None,
                    "source": "added_by_ai", "outdoor_space": sid, "open_air": True,
                    **({"floor_z": float(space["z"])} if isinstance(space.get("z"), (int, float)) else {}),
                    "footprint": {"center": p["center"], "size": p["size"], "rotation_deg": p["rotation_deg"]},
                    "front_deg": p["front_deg"], "height": None, "status": "verified", "build": True,
                    "evidence": [{"file": "building.json", "method": "inferred", "confidence": 0.7, "text": why}],
                    "inferred": True,
                    "inferred_reason": f"{plan['set']} set of the {kind} {sid} ({why})"}
            out["furniture"].append(item)
            if p["type"] == "table_coffee":
                table = item
        decor = []
        for c in plan["planters"]:
            decor.append({"type": "plant_large", "center": c, "size": [PLANTER_SIZE_M, PLANTER_SIZE_M],
                          "rotation_deg": 0.0, "reason": f"a planter on the {kind} ({why})"})
        if plan["rug"]:
            decor.append(dict(plan["rug"], type="rug", reason=f"an outdoor rug under the {kind}'s lounge ({why})",
                              anchor_ids=[f["id"] for f in out["furniture"] if f.get("outdoor_space") == sid]))
        if table is not None:
            decor.append({"type": "candle", "center": list(table["footprint"]["center"]), "size": [0.2, 0.2],
                          "rotation_deg": 0.0, "host_id": table["id"],
                          "reason": f"a lantern on the {kind}'s table ({why})"})
        for d in decor:
            out["decor"].append(dict({"id": _next_decor_id(out, level), "kind": "decor", "level_id": level,
                                      "room_id": None, "outdoor_space": sid, "asset": None, "source": "added_by_ai",
                                      **({"floor_z": float(space["z"])} if isinstance(space.get("z"), (int, float))
                                         else {}),
                                      "method": "rule", "confidence": 0.7, "status": "verified",
                                      "evidence": [{"file": "building.json", "method": "inferred", "confidence": 0.7,
                                                    "text": why}]}, **d))
        notes.append(f"{sid}: {plan['set']} set ({len(plan['pieces'])} pieces, {plan['covered']:.0%} under the "
                     f"roof), {len(plan['planters'])} planter(s), rug {'yes' if plan['rug'] else 'no'}")
    return out, notes
