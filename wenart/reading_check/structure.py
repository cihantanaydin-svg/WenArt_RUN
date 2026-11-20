"""RC17, the structural checks of a reading (20 Nov 2026; the user: "focus on real structural problems", "All fixes must
be general not just for these projects, future projects should not be making these mistakes").

What: pure checks on ``building.json`` (and, for the angled walls, the drawn wall strokes the reading check already
reads), each finding ``{"check": "RC17", "rule", "severity", "level_id", "message", "place", "element_ids",
"advisory": true, "structural": true}``:

1. ``door_into_air``: a door in an outer wall of a storey above the ground with nothing outside it to step onto: no
   open-air room or outdoor space (balcony, terrace) of its storey, and not the roof of the storey right under it (a
   roof two storeys down is no landing). The build turns such a door into a window of its width (architect E1,
   ``door_to_window``); here it is named before a pod, because it is usually a sign of a wall or a room the reading
   lost (real20's angled street wall: the hall doors of every upper storey opened into the air).
2. ``slab_beyond_walls``: the floor slab under a storey (the union of its outline and the storey below's, as the build
   makes it) open to the sky inside that storey's own walls: a notch of at least ``NOTCH_MIN_M2`` within the convex
   hull of the storey's walls, covered by no outdoor space of the storey. The slab then sticks out past walls that stop
   short, like an empty frame (a storey wall left out or not closed).
3. ``angled_wall_straight`` (rule R35): drawn wall strokes at an angle off the model's axes (more than
   ``ANGLE_OFF_DEG``), ``ANGLED_MIN_M`` or more of them, that no model wall at their angle follows: the wall was cut
   into axis stubs or left out.

4. ``outdoor_label_lost``: an outdoor-space label (balcony, terrace) placed in no face and no outdoor space of its
   level (inside a wall, beside a tiny room), or a room named by an outdoor word read as an indoor room.

Why: these errors reached the renders of the 20 Nov 2026 structure pod unseen (doors into the air, slab edges
past the walls, a 16-degree facade built in steps); each is a class of error any project can show.

How: geometry only (shapely; the outlines are ``geom2d.wall_outline`` as the build computes them); no AI, no pod.
Advisory like RC14 and RC16, but never demoted: a structural impossibility (``structural: true``).
"""
from __future__ import annotations

import math
from typing import Optional

CHECK = "RC17"
NAME = "structural integrity"
RULES = {
    "door_into_air": "a door in an outer wall above the ground with nothing outside to step onto",
    "slab_beyond_walls": "a storey's floor slab open to the sky inside the storey's own walls",
    "angled_wall_straight": "a drawn wall at an angle that no model wall at its angle follows (R35)",
    "outdoor_label_lost": "an outdoor label in no outdoor space (inside a wall, beside a tiny room) or naming a room",
    "door_without_opening": "a drawn door size tag or door block with no door or opening of the model near it",
}
PROBE_M = 0.3                 # a door's outside is probed this far past its wall's face
GROUND_UP_M = 0.5             # a storey this far above the ground floor is an upper storey
NOTCH_MIN_M2 = 1.0            # a notch of the slab inside a storey's walls this large is a finding
ANGLE_OFF_DEG = 3.0           # a drawn stroke this far off the model's axes is an angled wall
ANGLED_MIN_M = 2.0            # this much angled drawn wall on a level before it is checked
ANGLE_SAME_DEG = 2.0          # a model wall within this angle of a drawn stroke follows it ...
FOLLOW_M = 0.25               # ... when the stroke lies within this distance of its centre line plus half its thickness
FOLLOW_SHARE = 0.5            # under this share of the angled drawn length followed, the finding is written
OPEN_AIR_TYPES = ("balcony", "terrace", "loggia", "deck", "patio", "courtyard", "roof_terrace", "garden")


def _finding(rule: str, severity: str, level: Optional[str], message: str, place=None, element_ids=()) -> dict:
    out = {"check": CHECK, "name": NAME, "rule": rule, "severity": severity, "level_id": level, "message": message,
           "place": None, "element_ids": list(element_ids), "advisory": True, "structural": True}
    if place is not None:
        out["place"] = [round(float(place[0]), 2), round(float(place[1]), 2)]
    return out


def _levels(building: dict) -> list:
    return sorted((lv for lv in building.get("levels") or [] if isinstance(lv, dict) and lv.get("id")),
                  key=lambda lv: float(lv.get("elevation") or 0.0))


def ground_elevation(levels: list) -> float:
    """The ground floor's elevation (the level of order 0, else the lowest at or above -0.5 m, else the lowest)."""
    zero = [lv for lv in levels if lv.get("order") == 0]
    up = [lv for lv in levels if float(lv.get("elevation") or 0.0) >= -0.5]
    pick = (zero or up or levels)
    return float(pick[0].get("elevation") or 0.0) if pick else 0.0


def outlines(building: dict) -> dict:
    """``{level id: outline polygon (shapely) or None}``: the outer outline of each level's walls."""
    from shapely.geometry import Polygon

    from wenart.blender import geom2d

    out = {}
    for lv in _levels(building):
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lv["id"] and w.get("start")
                 and w.get("end")]
        loop, _method = geom2d.wall_outline(walls) if walls else ([], "none")
        poly = Polygon(loop) if len(loop) >= 3 else None
        out[lv["id"]] = poly.buffer(0) if poly is not None and not poly.is_valid else poly
    return out


def _open_air(building: dict, lid: str) -> list:
    """The open-air shapes of a level: its outdoor spaces and its rooms of an open-air type."""
    from shapely.geometry import Polygon

    out = []
    for sp in (building.get("site") or {}).get("outdoor_spaces") or []:
        if isinstance(sp, dict) and sp.get("level_id") == lid and len(sp.get("polygon") or []) >= 3:
            out.append(Polygon(sp["polygon"]).buffer(0.05))
    for r in building.get("rooms") or []:
        if r.get("level_id") == lid and str(r.get("room_type") or "") in OPEN_AIR_TYPES \
                and len(r.get("polygon") or []) >= 3:
            out.append(Polygon(r["polygon"]).buffer(0.05))
    return out


def doors_into_air(building: dict, shapes: Optional[dict] = None) -> list:
    """Rule 1 (the module docstring)."""
    from shapely.geometry import Point

    levels = _levels(building)
    if not levels:
        return []
    shapes = outlines(building) if shapes is None else shapes
    gl = ground_elevation(levels)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id")}
    out = []
    for i, lv in enumerate(levels):
        if float(lv.get("elevation") or 0.0) <= gl + GROUND_UP_M:
            continue
        own = shapes.get(lv["id"])
        if own is None:
            continue
        below = [x for x in levels if float(x.get("elevation") or 0.0) < float(lv.get("elevation") or 0.0) - GROUND_UP_M]
        nxt = shapes.get(below[-1]["id"]) if below else None
        air = _open_air(building, lv["id"])
        for o in building.get("openings") or []:
            if o.get("level_id") != lv["id"] or o.get("type") != "door":
                continue
            w = walls.get(o.get("wall_id"))
            c = o.get("center")
            if w is None or not isinstance(c, (list, tuple)) or len(c) < 2:
                continue
            (x0, y0), (x1, y1) = w["start"], w["end"]
            length = math.hypot(x1 - x0, y1 - y0)
            if length <= 1e-9:
                continue
            nx, ny = -(y1 - y0) / length, (x1 - x0) / length
            reach = float(w.get("thickness") or 0.2) / 2.0 + PROBE_M
            sides = [Point(c[0] + nx * reach, c[1] + ny * reach), Point(c[0] - nx * reach, c[1] - ny * reach)]
            inside = [own.contains(p) for p in sides]
            if inside[0] == inside[1]:
                continue                                        # an inner door (or one in a wall the outline misses)
            p = sides[1] if inside[0] else sides[0]
            if any(a.contains(p) for a in air) or (nxt is not None and nxt.contains(p)):
                continue
            out.append(_finding("door_into_air", "major", lv["id"],
                                f"door {o.get('id')} ({float(o.get('width') or 0):.2f} m) in an outer wall of "
                                f"{lv['id']}, {float(lv.get('elevation') or 0) - gl:.2f} m above the ground floor, has "
                                f"nothing outside to step onto (no balcony or terrace of its storey, not the roof of "
                                f"the storey under it): a wall or a room the reading lost, or a window",
                                place=(p.x, p.y), element_ids=[o.get("id")]))
    return out


def slabs_beyond_walls(building: dict, shapes: Optional[dict] = None) -> list:
    """Rule 2 (the module docstring)."""
    from shapely.geometry import MultiPoint
    from shapely.ops import unary_union

    levels = _levels(building)
    shapes = outlines(building) if shapes is None else shapes
    out = []
    for i in range(1, len(levels)):
        lv, low = levels[i], levels[i - 1]
        own, under = shapes.get(lv["id"]), shapes.get(low["id"])
        if own is None or under is None:
            continue
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lv["id"] and w.get("start")]
        hull = MultiPoint([tuple(w["start"]) for w in walls] + [tuple(w["end"]) for w in walls]).convex_hull
        air = _open_air(building, lv["id"])
        exposed = own.union(under).difference(own)
        if air:
            exposed = exposed.difference(unary_union(air))
        notch = exposed.intersection(hull)
        parts = [g for g in getattr(notch, "geoms", [notch]) if g.geom_type == "Polygon" and g.area >= NOTCH_MIN_M2]
        for g in parts:
            c = g.representative_point()
            out.append(_finding("slab_beyond_walls", "major", lv["id"],
                                f"the floor slab under {lv['id']} is open to the sky inside {lv['id']}'s own walls "
                                f"({g.area:.1f} m2 near ({c.x:.2f}, {c.y:.2f}) m, within the hull of its walls, no "
                                f"balcony or terrace there): its walls stop short and the slab sticks out past them "
                                f"(a storey wall left out or not closed)", place=(c.x, c.y)))
    return out


def angled_walls_straight(segs: list, walls: list, level: str) -> list:
    """Rule 3 (R35) on one level: ``segs`` the drawn wall strokes in building metres (``drawn_wall_segments``),
    ``walls`` the level's model walls."""
    from shapely.geometry import LineString

    model = [w for w in walls if w.get("start") and w.get("end") and math.dist(w["start"], w["end"]) > 1e-6]
    if not model or not segs:
        return []
    bins: dict = {}
    for w in model:
        a = math.degrees(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0])) % 90.0
        k = int(round(a)) % 90
        bins[k] = bins.get(k, 0.0) + math.dist(w["start"], w["end"])
    axis = max(bins, key=bins.get)

    def off(a: float) -> float:
        d = (a - axis) % 90.0
        return min(d, 90.0 - d)

    angled = []
    for a, b in segs:
        length = math.dist(a, b)
        if length < 0.3:
            continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0
        if off(ang) > ANGLE_OFF_DEG:
            angled.append((a, b, ang, length))
    total = sum(s[3] for s in angled)
    if total < ANGLED_MIN_M:
        return []
    followed = 0.0
    for a, b, ang, length in angled:
        line = LineString([a, b])
        for w in model:
            wa = math.degrees(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0])) % 180.0
            d = abs(wa - ang) % 180.0
            if min(d, 180.0 - d) > ANGLE_SAME_DEG:
                continue
            band = LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
                float(w.get("thickness") or 0.2) / 2.0 + FOLLOW_M, cap_style=2)
            if band.intersection(line).length >= 0.5 * length:
                followed += length
                break
    if followed >= FOLLOW_SHARE * total:
        return []
    angs = sorted({round(s[2]) for s in angled})
    return [_finding("angled_wall_straight", "major", level,
                     f"{total:.1f} m of drawn wall at {', '.join(f'{x} deg' for x in angs[:4])} (off the plan's axes) "
                     f"is followed by model walls at its angle for {followed:.1f} m only: the angled wall is built "
                     f"straight (axis stubs) or left out (R35)")]


DOOR_OPENING_REACH_M = 1.2    # rule 5: an opening of the model this near a door tag (plus half its width) ...
DOOR_WIDTH_TOL_M = 0.3        # ... and of about its width is its door
DOOR_BLOCK_REACH_M = 0.3      # an opening this near a door block (plus half its size) is its door


def doors_without_opening(page, tf, building: dict, level: str) -> list:
    """Rule 5 (20 Nov 2026; real20's kitchen-to-balcony door, tagged '120/210', whose gap the wall's cut lines closed):
    a door size tag (W/H with H >= 1.80 m, or the 'K:' form) or a door block insert (``core._door_evidence``) of the
    level's drawing with no door or opening of the model within ``DOOR_OPENING_REACH_M`` plus half its width.
    ``tf`` maps the drawing's units to building metres (``reading_check.level_pages``)."""
    from wenart.ingest.generic import core as GC

    scale = math.sqrt(abs(tf[0] * tf[4] - tf[1] * tf[3])) or 1.0
    opens = [o for o in building.get("openings") or [] if o.get("level_id") == level
             and o.get("type") in ("door", "opening") and isinstance(o.get("center"), (list, tuple))]
    out = []
    for c, width, _h, what, ev in GC._door_evidence(page.texts, page.strokes, unit_m=scale):
        p = (tf[0] * c[0] + tf[1] * c[1] + tf[2], tf[3] * c[0] + tf[4] * c[1] + tf[5])
        if width is not None:
            # a tag's door: an opening of about its width (``DOOR_WIDTH_TOL_M``) within reach of the tag
            near = [o for o in opens if abs(float(o.get("width") or 0) - width) <= DOOR_WIDTH_TOL_M
                    and math.dist(p, o["center"][:2]) <= DOOR_OPENING_REACH_M + float(o.get("width") or 0) / 2.0]
        else:
            w = float(ev.get("size_m") or 0.0)
            near = [o for o in opens if math.dist(p, o["center"][:2]) <= w / 2.0 + DOOR_BLOCK_REACH_M]
        if near:
            continue
        out.append(_finding("door_without_opening", "major", level,
                            f"{what} at ({p[0]:.2f}, {p[1]:.2f}) m has no door or opening of the model within "
                            f"{DOOR_OPENING_REACH_M:.1f} m: a drawn door not read (its gap closed by the wall's lines)",
                            place=p))
    return out


TINY_ROOM_M2 = 1.5           # rule 4: a room this small beside a lost outdoor label is that space read as a room
TINY_REACH_M = 1.0


def outdoor_labels_lost(building: dict) -> list:
    """Rule 4 (20 Nov 2026; real20's north balcony, recessed into its angled facade, became a 1 m2 room behind a 2.5 m
    window with its label inside the facade wall): an outdoor-space label (balcony, terrace ...; ``levels.outdoor``)
    the reading placed in no face and no outdoor space of its level (named with the wall it lies in and a tiny room
    beside it), and a room named by an outdoor word whose type is not open-air."""
    from shapely.geometry import LineString, Point, Polygon

    from wenart.levels import outdoor as OD

    out = []
    for lv in _levels(building):
        lid = lv["id"]
        air = _open_air(building, lid)
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid and w.get("start") and w.get("end")]
        rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid and len(r.get("polygon") or []) >= 3]
        for p in lv.get("reading_places") or []:
            if not isinstance(p, dict) or not OD.space_kind(p.get("text")) or not p.get("at"):
                continue
            pt = Point(float(p["at"][0]), float(p["at"][1]))
            if any(a.buffer(0.3).contains(pt) for a in air):
                continue
            wall = next((w for w in walls if LineString([tuple(w["start"]), tuple(w["end"])]).buffer(
                float(w.get("thickness") or 0.2) / 2.0, cap_style=2).contains(pt)), None)
            tiny = [r for r in rooms if float(r.get("area_computed") or Polygon(r["polygon"]).area) < TINY_ROOM_M2
                    and Polygon(r["polygon"]).distance(pt) <= TINY_REACH_M]
            extra = (f"; it lies inside wall {wall.get('id')}" if wall else "") + \
                (f"; the tiny room(s) {', '.join(r['id'] for r in tiny)} beside it" if tiny else "")
            out.append(_finding("outdoor_label_lost", "major", lid,
                                f"the outdoor label '{p.get('text')}' at ({pt.x:.2f}, {pt.y:.2f}) m is in no outdoor "
                                f"space of {lid}{extra}: the balcony or terrace was lost (a wall across its mouth, its "
                                f"outline not closed)", place=(pt.x, pt.y),
                                element_ids=([wall.get("id")] if wall else []) + [r["id"] for r in tiny]))
        for r in rooms:
            sk = OD.space_kind(r.get("label") or r.get("label_raw"))
            if sk and str(r.get("room_type") or "") not in OPEN_AIR_TYPES:
                c = Polygon(r["polygon"]).representative_point()
                out.append(_finding("outdoor_label_lost", "major", lid,
                                    f"room {r['id']} is named '{r.get('label') or r.get('label_raw')}' (an outdoor "
                                    f"space, {sk['kind']}) but read as an indoor {r.get('room_type')}",
                                    place=(c.x, c.y), element_ids=[r["id"]]))
    return out


def findings(building: dict) -> list:
    """Rules 1, 2 and 4 on a building (pure); rule 3 needs the drawing and runs in ``reading_check.check``."""
    shapes = outlines(building)
    return doors_into_air(building, shapes) + slabs_beyond_walls(building, shapes) + outdoor_labels_lost(building)
