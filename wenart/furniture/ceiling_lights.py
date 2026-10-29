"""Ceiling lights by room type and size (28 Oct 2026, user on real04 run 20261028-005318-full: "More lights from the
ceiling needed").

What the run had: r_L-1_salon, a 50.9 m² living and dining room under a 2.85 m ceiling, one pendant at the middle of
its 3.35 m table and no light over its three seating groups; every bedroom one light; the 11.5-15.3 m² halls none. The
decor stage offered one light slot per dining table, coffee table and bed and one at the room centre
(``decor_ai.ceiling_items``), and the AI or the styling minimum filled one of them: nothing counted the light a room
of its size needs.

What (pure; ``decor_ai.apply`` calls ``add_lights`` after the AI's choice, the twins' copies and the outdoor sets, so
every room is lit whatever the AI chose; the model review's M17 and Argus call ``review``):

1. Zone lights, the task light of every functional group (``zones``): a row of pendants along each dining table and
   kitchen island, one per ``PENDANT_PITCH_M`` of its length less ``PENDANT_END_M`` at each end (at most
   ``PENDANT_MAX``; their bottoms ``PENDANT_OVER_TOP_M`` over the top); a ceiling light over each coffee table (a sofa
   without one: ``SEAT_REACH_M`` in front of it), each bed, each desk's front edge, and over the aisle in front of each
   kitchen counter (one per ``RUN_PITCH_M`` of run). A light the room already has within ``ZONE_MATCH_M`` of a zone's
   spot lights it; a row with fewer pendants than it needs is laid again (the AI's pendant colour kept).
2. Enough light for the area: the lumen method of interior lighting design (CIBSE / IES: N = E x A / (F x UF x MF)
   fixtures for an average illuminance E in lux on a floor of A m², lamps of F lumens, a utilisation factor UF and a
   maintenance factor MF). E is a designer value per room type (``LUX``, assumed and flagged: a calm ambient light,
   the task light comes from the zones, the rig's lamps and strips), scaled by the style's decor density
   (``DENSITY_LUX``: a sparse style fewer fixtures, a layered one more); F = ``LAMP_LUMENS`` (one 75 W-equivalent LED
   bulb, the rig's own fixture, ``lighting.ROOM_RIGS``), UF = ``UTILISATION``, MF = ``MAINTENANCE``. The lights the
   count asks beyond the zones and the room's own lights are spread evenly (``general_spots``: farthest point first,
   then a centroidal Voronoi relaxation on the floor, the even layout of a downlight grid that also fits an L-shaped
   room), never closer than ``MIN_GAP_M`` to another light.
3. Every light is checked where it hangs (``mount``): inside the room ``INSET_M`` from its walls, never over a wall
   cabinet, a tall cabinet, a wardrobe, a fridge, a counter run or a stair (``OVERHEAD_BLOCKERS``), never in a door
   swing; under a sloped ceiling a flush light is mounted on the slope (``slope_mount``: tilted onto the ceiling plane
   over its centre; the builder turns the mesh, ``geom2d.tilt_onto_plane``) and hangs only when its lowest point stays
   ``decor.MIN_LIGHT_BOTTOM_M`` (2.0 m) over the floor and its top inside the ceiling; a pendant keeps a
   ``PENDANT_MIN_DROP_M`` drop (else the flush light). Open-air rooms get none (no ceiling over them).

Why: a room's light is a design rule of its size and its groups, not a decor choice; the vision model may still pick
the look of each light (its colour, the library model the refit gives), never their number.

29 Oct 2026 (user on real06 run 20261028-154514-full: "2 lights together not making sense", lesson UL91; the child's
bedroom r_L1_cocuk_odasi: the AI's woven pendant at the room's centre and the rule's flush light over each of its two
beds 2.0 m from it, seen side by side in cam_r_L1_cocuk_odasi_3; the pendant was 0.8 m from each bed's edge, out of
the 0.9 m reach of the beds' centre spots, so neither bed counted it): the lights of a room are spaced as a designer
spaces them (``plan_room``):

4. **Spacing**: no two ceiling fixtures of a room closer than ``LIGHT_SPACING_M`` (the pendants of one row over a
   table or an island excepted: they are one fixture), and a flush ceiling light never within ``MIXED_SPACING_M`` of a
   free pendant (one that is not in such a row: the room's statement light; a flush light beside it reads as two lights
   together). A zone or general light the rule would hang closer is not hung (the nearer light serves).
5. **One light per zone**: a light over a zone's piece grown by ``ZONE_REACH_M`` lights the zone (the AI's pendant
   counts as the general light of its zone, whatever its slot), and a zone keeps one light: a second one in the same
   zone, or a pair closer than the spacing, is taken out (the rule's own light first, else the one farther from the
   zone's spot; ``remove`` with ``too_close``); the lumen method's general lights hang only outside the lit zones.
6. The review (M17) flags every pair the plan finds too close or in one zone (major, ``rule: spacing``).
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G
from wenart.furniture import decor as D
from wenart.furniture import placer

LIGHT_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light")
RULE = "decor.ceiling_lights"
REVIEW_CHECK = "M17"
# The lumen method (module docstring). Designer values (assumed): the average ambient illuminance of each room type.
LUX: dict[str, float] = {"living": 50.0, "dining": 75.0, "bedroom": 60.0, "child": 75.0, "office": 100.0,
                         "kitchen": 100.0, "hall": 50.0, "bathroom": 100.0, "wc": 100.0, "dressing": 75.0,
                         "laundry": 100.0, "storage": 50.0, "other": 50.0}
LAMP_LUMENS = 1100.0              # one 75 W-equivalent LED bulb (US FTC lumen labelling; lighting.ROOM_RIGS)
UTILISATION = 0.5                 # a room of light walls and ceiling, lit from the ceiling
MAINTENANCE = 0.8
DENSITY_LUX: dict[str, float] = {"sparse": 0.7, "balanced": 1.0, "layered": 1.3}   # = style.density.DENSITY_FACTOR
MIN_ROOM_M2 = 1.5                 # smaller rooms (shafts, niches) get no rule light
# zones
PENDANT_PITCH_M = 0.9             # one pendant per 0.9 m of a dining table or island (balanced style) ...
PENDANT_END_M = 0.3               # ... the row kept this far in from each end
PENDANT_MAX = 4
PENDANT_OVER_TOP_M = 0.75         # = decor_ai.PENDANT_OVER_TABLE_M
PENDANT_MIN_BOTTOM_M = 2.0        # = decor_ai.PENDANT_MIN_BOTTOM_M (a pendant not over a table)
PENDANT_MIN_DROP_M = 0.3          # = decor_ai.PENDANT_MIN_DROP_M
PENDANT_SIZE = (0.45, 0.45)       # = decor_ai.PENDANT_SIZE; a row of 3 or more takes ROW_PENDANT_SIZE
ROW_PENDANT_SIZE = (0.35, 0.35)
CEILING_LIGHT_SIZE = (0.4, 0.4, 0.12)   # = decor_ai.CEILING_LIGHT_SIZE
SEAT_REACH_M = 0.9                # a sofa without a coffee table: the light this far in front of it
COFFEE_REACH_M = 1.5              # a coffee table this close in front of a sofa is its group's
RUN_PITCH_M = 1.8                 # one light per 1.8 m of kitchen counter, ...
RUN_AISLE_M = 0.3                 # ... this far in front of the counter (over the aisle, off the wall cabinets)
ZONE_MATCH_M = 0.9                # a light this close to a zone's spot lights the zone
ROW_MATCH_M = 0.2                 # a light over a table or island (its footprint grown by this) is one of its row
# placement
INSET_M = 0.45                    # a light's centre this far from the walls (narrow rooms: INSET_MIN_M)
INSET_MIN_M = 0.25
# 29 Oct 2026 (UL91): the spacing of a room's lights (module docstring, steps 4-5). A designer spaces ceiling lights
# about their mounting height apart (spacing-to-height ratio near 1 for downlights); 1.2 m keeps two fixtures from
# reading as one pair; a pendant's shade (0.35-0.5 m, hanging to 2.0 m) is the room's statement light: a flush light
# within 2.5 m of it shows beside it in a 16-18 mm interior view (real06: 2.04-2.07 m apart looked side by side).
LIGHT_SPACING_M = 1.2             # no two ceiling fixtures closer (the pendants of one row over a table excepted)
MIXED_SPACING_M = 2.5             # a flush ceiling light from a free pendant (not in a row over a table or island)
ZONE_REACH_M = 0.9                # a light over a zone's piece grown by this lights the zone (= ZONE_MATCH_M)
MIN_GAP_M = LIGHT_SPACING_M       # two lights never closer than this (a row's pendants excepted; was 1.0 m)
RASTER_M = 0.25                   # the floor sample and the candidate spots
LLOYD_STEPS = 12
OVERHEAD_BLOCKERS: tuple[str, ...] = ("wall_cabinet", "tall_cabinet", "wardrobe", "fridge", "kitchen_counter",
                                      "bookshelf", "display_cabinet", "stair")
BLOCKER_MARGIN_M = 0.05
SLOPE_EPS = 1e-4                  # a plane steeper than this is a slope (a flat ceiling plane is (0, 0, z))
SLOPE_TOP_TOL_M = 0.01            # the tilted top's corners stay this close under the ceiling


def _level(building: dict, level_id) -> dict:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})


def _area(room: dict) -> float:
    pts = room.get("polygon") or []
    return abs(G.polygon_area([tuple(p[:2]) for p in pts])) if len(pts) >= 3 else 0.0


def lit_room(room: dict) -> bool:
    """A room the lighting rule lights: one decor dresses (``decor.room_takes_decor``), not open-air (no ceiling) and
    at least ``MIN_ROOM_M2``."""
    from wenart.blender import outdoor as OD

    return D.room_takes_decor(room) and not OD.open_air_room(room) and _area(room) >= MIN_ROOM_M2


def lights_needed(room: dict, density: str = "balanced") -> tuple[int, str]:
    """``(count, why)``: the ceiling lights the lumen method asks for the room's floor (module docstring), at least 1;
    rounded half up."""
    t = str(room.get("room_type") or "other").lower()
    if room.get("room_subtype") == "child":
        t = "child"
    lux = LUX.get(t, LUX["other"]) * DENSITY_LUX.get(str(density), 1.0)
    area = _area(room)
    raw = lux * area / (LAMP_LUMENS * UTILISATION * MAINTENANCE)
    n = max(1, int(math.floor(raw + 0.5)))
    why = (f"lumen method: {lux:g} lx x {area:.1f} m² / ({LAMP_LUMENS:g} lm x {UTILISATION:g} x {MAINTENANCE:g}) = "
           f"{raw:.1f} -> {n} light(s) ({t}, {density} style)")
    return n, why


def pendants_for_length(length: float, density: str = "balanced") -> int:
    """The pendants of a row over a table or island ``length`` m long (module docstring)."""
    pitch = PENDANT_PITCH_M / DENSITY_LUX.get(str(density), 1.0)
    return max(1, min(PENDANT_MAX, int(math.floor(max(0.0, length - 2.0 * PENDANT_END_M) / pitch + 1e-9)) + 1))


# --------------------------------------------------------------------------
# Where a light can hang
# --------------------------------------------------------------------------

def _lowest_plane(planes: list, x: float, y: float):
    from wenart.blender import geom2d

    return min(planes, key=lambda p: geom2d.plane_z(p, x, y))


def slope_mount(planes: list, floor_z: float, centre, size, h: float) -> Optional[dict]:
    """The mount of a flush light under a sloped ceiling plane over its centre (pure): ``{"plane", "tilt_deg",
    "rise_deg", "top_m", "lowest_m", "fits"}`` (heights over the floor: its top centre on the plane, the lowest point
    of the tilted fixture; ``fits`` False when a top corner would cross another ceiling plane, at a ridge); None under
    a flat plane or without planes."""
    if not planes:
        return None
    from wenart.blender import geom2d

    x, y = float(centre[0]), float(centre[1])
    a, b, c = (float(v) for v in _lowest_plane(planes, x, y))
    slope = math.hypot(a, b)
    if slope < SLOPE_EPS:
        return None
    tilt = math.atan(slope)
    top = a * x + b * y + c - floor_z
    w, d = float(size[0]), float(size[1])
    lowest = top - h * math.cos(tilt) - max(w, d) / 2.0 * math.sin(tilt)
    fits = True
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, py = x + sx * w / 2.0, y + sy * d / 2.0
        if a * px + b * py + c > geom2d.surface_z(planes, px, py) + SLOPE_TOP_TOL_M:
            fits = False
    return {"plane": [round(a, 6), round(b, 6), round(c, 6)], "tilt_deg": round(math.degrees(tilt), 3),
            "rise_deg": round(math.degrees(math.atan2(b, a)), 3), "top_m": round(top, 4),
            "lowest_m": round(lowest, 4), "fits": fits}


def mount(building: dict, level_id, planes: list, kind: str, centre, bottom: Optional[float] = None,
          size=None) -> tuple[Optional[dict], str]:
    """``(item fields, why)`` of a light hanging at ``centre`` (pure): ``center`` [x, y, bottom], ``size`` and, under
    a slope, ``slope_mount`` (a flush light). A pendant needs ``PENDANT_MIN_DROP_M`` under the ceiling over it from
    its ``bottom``; a flush light under a slope its lowest point ``decor.MIN_LIGHT_BOTTOM_M`` over the floor and its
    top inside the ceiling. ``(None, why)`` when it cannot hang there."""
    level = _level(building, level_id)
    flat = float(level.get("ceiling_height") or 2.7)
    floor_z = float(level.get("elevation") or 0.0)
    x, y = float(centre[0]), float(centre[1])
    if kind == "pendant_light":
        pw, pd = size or PENDANT_SIZE
        top = D.ceiling_over(building, level_id, (x, y), (pw, pd), planes=planes) if planes else flat
        low = float(bottom if bottom is not None else PENDANT_MIN_BOTTOM_M)
        if top - low < PENDANT_MIN_DROP_M - 1e-9:
            return None, f"a pendant needs {PENDANT_MIN_DROP_M:g} m under the {top:.2f} m ceiling from {low:.2f} m"
        return {"center": [round(x, 3), round(y, 3), round(low, 3)], "size": [pw, pd, round(top - low, 3)]}, "ok"
    w, d, h = CEILING_LIGHT_SIZE
    sm = slope_mount(planes, floor_z, (x, y), (w, d), h)
    if sm is None:
        top = D.ceiling_over(building, level_id, (x, y), (w, d), planes=planes) if planes else flat
        if top < flat - 1e-6 and top - h < D.MIN_LIGHT_BOTTOM_M - 1e-9:
            return None, f"under the sloped ceiling its bottom would be {top - h:.2f} m over the floor"
        return {"center": [round(x, 3), round(y, 3), round(top - h, 3)], "size": [w, d, h]}, "ok"
    if not sm["fits"]:
        return None, "its top would cross the ceiling's ridge"
    if sm["lowest_m"] < D.MIN_LIGHT_BOTTOM_M - 1e-9:
        return None, (f"on the slope ({sm['tilt_deg']:.0f}°) its lowest point would be {sm['lowest_m']:.2f} m over "
                      f"the floor (< {D.MIN_LIGHT_BOTTOM_M:g} m)")
    return {"center": [round(x, 3), round(y, 3), round(sm["top_m"] - h, 3)], "size": [w, d, h],
            "slope_mount": sm}, "ok"


class Room:
    """The geometry a room's lights are checked against (shapely): the inset floor, the blockers overhead, the door
    swings."""

    def __init__(self, building: dict, room: dict, pieces: list[dict]):
        from shapely.geometry import Polygon
        from shapely.ops import unary_union

        self.building, self.room = building, room
        self.poly = Polygon([tuple(p[:2]) for p in room["polygon"]])
        if not self.poly.is_valid:
            self.poly = self.poly.buffer(0)
        inner = self.poly.buffer(-INSET_M, join_style=2)
        if inner.is_empty or inner.area < 0.05:
            inner = self.poly.buffer(-INSET_MIN_M, join_style=2)
        self.inner = inner
        blocks = []
        for p in pieces:
            if p.get("build") is False or str(p.get("type")) not in OVERHEAD_BLOCKERS:
                continue
            try:
                blocks.append(placer.piece_from_furniture(p).polygon().buffer(BLOCKER_MARGIN_M))
            except (KeyError, TypeError, ValueError):
                continue
        self.blockers = unary_union(blocks) if blocks else None
        swings = []
        try:
            ctx = placer.room_context(building, room)
            swings = [dz.swing for dz in ctx.doors if dz.swing is not None and not dz.swing.is_empty]
        except (KeyError, TypeError, ValueError):
            pass
        self.swings = unary_union(swings) if swings else None
        self.planes = D.ceiling_planes(building, room["level_id"])

    def free(self, centre, size=CEILING_LIGHT_SIZE[:2], inside=True) -> tuple[bool, str]:
        """The light's square at ``centre`` is inside the inset floor (``inside``), off the blockers and the swings."""
        from shapely.geometry import box

        x, y = float(centre[0]), float(centre[1])
        sq = box(x - size[0] / 2.0, y - size[1] / 2.0, x + size[0] / 2.0, y + size[1] / 2.0)
        if inside and not self.inner.buffer(1e-6).contains(sq.centroid):
            return False, "too close to a wall"
        if not self.poly.contains(sq):
            return False, "outside the room"
        if self.blockers is not None and sq.intersects(self.blockers):
            return False, "over a cabinet, a wardrobe, a counter or a stair"
        if self.swings is not None and sq.intersects(self.swings):
            return False, "in a door swing"
        return True, "ok"

    def hang(self, kind: str, centre, bottom: Optional[float] = None, size=None,
             inside: bool = True) -> tuple[Optional[dict], str]:
        ok, why = self.free(centre, size or (PENDANT_SIZE if kind == "pendant_light" else CEILING_LIGHT_SIZE[:2]),
                            inside)
        if not ok:
            return None, why
        return mount(self.building, self.room["level_id"], self.planes, kind, centre, bottom, size)


# --------------------------------------------------------------------------
# Zones
# --------------------------------------------------------------------------

def _usable(p: dict) -> bool:
    return D._usable_anchor(p)


def _top(p: dict) -> float:
    return float(D.placer_bbox_height(p))


def zones(pieces: list[dict], density: str = "balanced") -> list[dict]:
    """The functional zones of a room's pieces and the spots of their lights (module docstring, step 1): ``{"id",
    "kind", "spots", "types", "bottom", "row", "why"}``; ``row`` True for a dining table or island (its lights are
    one row)."""
    out: list[dict] = []
    usable = [p for p in pieces if _usable(p)]
    for p in sorted(usable, key=lambda q: q["id"]):
        t = p["type"]
        w, d = (float(v) for v in p["footprint"]["size"][:2])
        if t in ("table_dining", "kitchen_island"):
            length = max(w, d)
            n = pendants_for_length(length, density)
            pitch = (length - 2.0 * PENDANT_END_M) / (n - 1) if n > 1 else 0.0
            offs = [(i - (n - 1) / 2.0) * pitch for i in range(n)]
            spots = [tuple(D._local_to_building(p, o, 0.0) if w >= d else D._local_to_building(p, 0.0, o))
                     for o in offs]
            out.append({"id": p["id"], "kind": "dining" if t == "table_dining" else "island", "spots": spots,
                        "types": ("pendant_light", "ceiling_light"), "bottom": _top(p) + PENDANT_OVER_TOP_M,
                        "row": True, "piece": p,
                        "why": f"{n} pendant(s) along the {length:.2f} m {t.replace('_', ' ')} {p['id']} (one per "
                               f"{PENDANT_PITCH_M / DENSITY_LUX.get(density, 1.0):.2f} m)"})
        elif t == "table_coffee":
            out.append({"id": p["id"], "kind": "seating", "spots": [tuple(p["footprint"]["center"][:2])],
                        "types": ("ceiling_light", "pendant_light"),
                        "bottom": max(PENDANT_MIN_BOTTOM_M, _top(p) + PENDANT_OVER_TOP_M), "row": False, "piece": p,
                        "why": f"over the seating group's coffee table {p['id']}"})
        elif t in ("bed_double", "bed_single"):
            out.append({"id": p["id"], "kind": "bed", "spots": [tuple(p["footprint"]["center"][:2])],
                        "types": ("ceiling_light", "pendant_light"), "bottom": PENDANT_MIN_BOTTOM_M, "row": False,
                        "piece": p, "why": f"over the bed {p['id']}"})
        elif t == "desk":
            out.append({"id": p["id"], "kind": "desk", "spots": [tuple(D._local_to_building(p, 0.0, -d / 2.0))],
                        "types": ("ceiling_light",), "bottom": None, "row": False, "piece": p,
                        "why": f"over the front edge of the desk {p['id']}"})
        elif t == "kitchen_counter":
            n = max(1, int(math.floor(w / RUN_PITCH_M + 0.5)))
            offs = [(i - (n - 1) / 2.0) * (w / n) for i in range(n)]
            out.append({"id": p["id"], "kind": "kitchen_run", "row": False, "piece": p, "types": ("ceiling_light",),
                        "bottom": None,
                        "spots": [tuple(D._local_to_building(p, o, -d / 2.0 - RUN_AISLE_M)) for o in offs],
                        "why": f"over the aisle in front of the counter {p['id']} (one per {RUN_PITCH_M:g} m of run)"})
    tables = [z for z in out if z["kind"] == "seating"]
    for p in sorted((q for q in usable if q["type"] in ("sofa", "sofa_corner")), key=lambda q: q["id"]):
        w, d = (float(v) for v in p["footprint"]["size"][:2])
        front = D._local_to_building(p, 0.0, -d / 2.0 - SEAT_REACH_M)
        if any(G.distance(front, z["spots"][0]) <= COFFEE_REACH_M for z in tables):
            continue
        out.append({"id": p["id"], "kind": "seating", "spots": [tuple(front)], "types": ("ceiling_light",),
                    "bottom": None, "row": False, "piece": p,
                    "why": f"over the seating in front of the sofa {p['id']} (no coffee table)"})
    return out


# --------------------------------------------------------------------------
# The plan of one room
# --------------------------------------------------------------------------

def _light_xy(d: dict) -> tuple[float, float]:
    return float(d["center"][0]), float(d["center"][1])


def _is_rule(d: dict) -> bool:
    return d.get("rule") == RULE


def zone_area(z: dict):
    """The floor a one-spot zone's light hangs over (shapely; module docstring, step 5): its piece grown by
    ``ZONE_REACH_M`` and its spot grown by ``ZONE_MATCH_M``; None for a row or a counter run (its work lights match
    their spots, one per ``RUN_PITCH_M``)."""
    from shapely.geometry import Point

    if z.get("row") or z.get("kind") == "kitchen_run" or len(z.get("spots") or []) != 1:
        return None
    spot = Point(z["spots"][0]).buffer(ZONE_MATCH_M)
    try:
        return placer.piece_from_furniture(z["piece"]).polygon().buffer(ZONE_REACH_M).union(spot)
    except (KeyError, TypeError, ValueError):
        return spot


def clash(p, kind_p: str, pendant_p: bool, q, kind_q: str, pendant_q: bool, task_p: bool = False,
          task_q: bool = False) -> Optional[str]:
    """Why two ceiling fixtures of one room are too close (pure; module docstring, step 4), None when they are not:
    closer than ``LIGHT_SPACING_M``, or a flush light within ``MIXED_SPACING_M`` of a free pendant (``pendant_*``: a
    pendant not in a row over a table or island); a task light (``task_*``: over a kitchen counter run's aisle) is a
    work light, never held to the pendant's spacing."""
    dist = G.distance(tuple(p[:2]), tuple(q[:2]))
    if dist < LIGHT_SPACING_M - 1e-9:
        return f"{dist:.2f} m apart (two ceiling lights keep {LIGHT_SPACING_M:g} m)"
    if dist < MIXED_SPACING_M - 1e-9 and ((pendant_p and kind_q == "ceiling_light" and not task_q)
                                          or (pendant_q and kind_p == "ceiling_light" and not task_p)):
        return (f"a flush ceiling light {dist:.2f} m from a pendant (a flush light keeps {MIXED_SPACING_M:g} m from a "
                "pendant: side by side they read as two lights together)")
    return None


def _hung(x: float, y: float, kind: str, pendant: bool, light_id, row: bool = False, task: bool = False) -> dict:
    return {"xy": (float(x), float(y)), "kind": kind, "pendant": bool(pendant), "id": light_id, "row": row,
            "task": bool(task or row)}


TASK_PENDANT_TYPES: tuple[str, ...] = ("table_dining", "kitchen_island", "table_coffee", "desk")
RUN_TASK_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")


def run_light(d: dict, pieces: list[dict]) -> bool:
    """A light over a kitchen counter run's aisle (the rule's run light names its counter in ``anchor_ids``): a task
    light (step 4)."""
    ids = {f.get("id") for f in pieces if f.get("type") in RUN_TASK_TYPES}
    return bool(ids & set(d.get("anchor_ids") or []))


def task_pendant(d: dict, pieces: list[dict]) -> bool:
    """A pendant over a table, an island, a coffee table or a desk (its footprint grown by ``ROW_MATCH_M``; any piece
    of the room, verified or not): a task light, not the room's free statement pendant (step 4)."""
    from shapely.geometry import Point

    if d.get("type") != "pendant_light":
        return False
    p = Point(_light_xy(d))
    for f in pieces:
        if f.get("type") not in TASK_PENDANT_TYPES or f.get("build") is False or not f.get("footprint"):
            continue
        try:
            if placer.piece_from_furniture(f).polygon().buffer(ROW_MATCH_M).contains(p):
                return True
        except (KeyError, TypeError, ValueError):
            continue
    return False


def plan_room(building: dict, room: dict, pieces: list[dict], existing: list[dict],
              density: str = "balanced") -> dict:
    """The lights the rule adds to one room (pure): ``{"add": [items without ids], "remove": [ids], "needed",
    "have", "zones": [{"id", "kind", "had", "lit"}], "notes": [...], "why", "too_close": [{"ids", "kinds",
    "distance_m", "why", "zone"}]}`` (module docstring; ``had``: the zone had its light before, ``lit``: it has it
    after; ``too_close``: the room's own lights that the spacing or the one-light-per-zone rule takes out, steps 4-5).
    ``existing``: the room's pendant and ceiling light decor items."""
    from shapely.geometry import Point
    from shapely.ops import unary_union

    rec = {"add": [], "remove": [], "needed": 0, "have": len(existing), "zones": [], "notes": [], "why": "",
           "too_close": []}
    if not lit_room(room):
        return rec
    geo = Room(building, room, pieces)
    count, why = lights_needed(room, density)
    rec["why"] = why
    used: set = set()
    adds: list[dict] = []
    hung: list[dict] = []                 # the lights that hang after the plan (``_hung``)
    all_zones = zones(pieces, density)

    def item(fields: dict, kind: str, reason: str, anchor: Optional[str], colour=None) -> dict:
        it = dict({"type": kind, "rotation_deg": 0.0, "reason": reason, "rule": RULE}, **fields)
        if anchor:
            it["anchor_ids"] = [anchor]
        if colour:
            it["colour"] = colour
        return it

    # 1. the rows of pendants over the dining tables and islands
    for z in [z for z in all_zones if z["row"]]:
        fp = placer.piece_from_furniture(z["piece"]).polygon().buffer(ROW_MATCH_M)
        over = [d for d in existing if d.get("id") not in used and fp.contains(Point(_light_xy(d)))]
        if len(over) >= len(z["spots"]):
            used.update(d.get("id") for d in over)
            hung += [_hung(*_light_xy(d), d.get("type"), False, d.get("id"), row=True) for d in over]
            rec["zones"].append({"id": z["id"], "kind": z["kind"], "had": True, "lit": True})
            continue
        size = ROW_PENDANT_SIZE if len(z["spots"]) >= 3 else PENDANT_SIZE
        made, why_not = [], ""
        for s in z["spots"]:
            got, why_not = geo.hang("pendant_light", s, z["bottom"], size, inside=False)
            kind = "pendant_light"
            if got is None:
                got, why_not = geo.hang("ceiling_light", s, inside=False)
                kind = "ceiling_light"
            if got is None:
                made = []
                break
            made.append((got, kind))
        if not made:
            rec["zones"].append({"id": z["id"], "kind": z["kind"], "had": bool(over), "lit": bool(over)})
            rec["notes"].append(f"{z['id']}: no row of lights ({why_not}); {len(over)} light(s) kept")
            used.update(d.get("id") for d in over)
            hung += [_hung(*_light_xy(d), d.get("type"), False, d.get("id"), row=True) for d in over]
            continue
        colour = next((d.get("colour") for d in over if d.get("colour")), None)
        for d in over:
            rec["remove"].append(d.get("id"))
            used.add(d.get("id"))
        for got, kind in made:
            reason = (f"lighting rule: {z['why']}" + (f"; laid again in place of {', '.join(d['id'] for d in over)}"
                                                     f" (its colour kept)" if over else ""))
            adds.append(item(got, kind, reason, z["id"], colour))
            hung.append(_hung(got["center"][0], got["center"][1], kind, False, None, row=True))
        rec["zones"].append({"id": z["id"], "kind": z["kind"], "had": bool(over), "lit": True})
    # 2. the room's other lights, spaced (step 4) and one per zone (step 5): the AI's first, then by id
    singles = [(z, zone_area(z)) for z in all_zones if not z["row"] and len(z["spots"]) == 1]
    for d in sorted((d for d in existing if d.get("id") not in used), key=lambda d: (_is_rule(d), str(d.get("id")))):
        xy, kind = _light_xy(d), d.get("type")
        pend = kind == "pendant_light" and not task_pendant(d, pieces)     # a free pendant: the statement light
        task = run_light(d, pieces)
        out = None                                  # (why, the light it stays with, the zone)
        for h in hung:
            reason = clash(xy, kind, pend, h["xy"], h["kind"], h["pendant"], task, h["task"])
            if reason:
                out = (reason, h, None)
                break
        for z, area in ([] if out else singles):
            if area is None or not area.contains(Point(xy)):
                continue
            first = next((h for h in hung if not h["row"] and area.contains(Point(h["xy"]))), None)
            if first is not None:
                out = (f"a second light over the {z['kind']} zone of {z['id']} (one light per zone)", first, z["id"])
                break
        if out is not None:
            why_out, h, zone_id = out
            rec["remove"].append(d.get("id"))
            used.add(d.get("id"))
            rec["too_close"].append({"ids": [h["id"], d.get("id")], "kinds": [h["kind"], kind],
                                     "distance_m": round(G.distance(xy, h["xy"]), 3), "why": why_out,
                                     "zone": zone_id})
            continue
        hung.append(_hung(*xy, kind, pend, d.get("id"), task=task))
    # 3. the zones: a light over each; a light the room keeps over the zone serves it, a light that a new one would
    # stand too close to serves it too (step 4); else the rule hangs one
    for z in [z for z in all_zones if not z["row"]]:
        area = zone_area(z)
        lit, had = True, True
        ztask = z["kind"] == "kitchen_run"            # the run's lights are work lights (step 4)
        for s in z["spots"]:
            near = next((h for h in hung if G.distance(h["xy"], s) <= ZONE_MATCH_M
                         or (area is not None and area.contains(Point(h["xy"])))), None)
            if near is not None:
                if near["id"] is not None:
                    used.add(near["id"])
                else:
                    had = False                       # lit by a light the rule hangs now (a row's, another zone's)
                continue
            had = False
            got, why_not, kind, blocker = None, "", None, None
            for kind in z["types"]:               # a zone's light hangs over its piece: inside the room is enough
                cand, why_not = geo.hang(kind, s, z["bottom"] if kind == "pendant_light" else None, inside=False)
                if cand is None:
                    continue
                free = kind == "pendant_light" and not task_pendant(cand | {"type": kind}, pieces)
                hit = next((h for h in hung if clash(s, kind, free, h["xy"], h["kind"], h["pendant"], ztask,
                                                     h["task"])), None)
                if hit is not None:
                    blocker = blocker or (hit, kind, free)
                    continue
                got = cand
                break
            if got is None and blocker is not None:
                h, bkind, bfree = blocker
                why_served = clash(s, bkind, bfree, h["xy"], h["kind"], h["pendant"], ztask, h["task"])
                rec["notes"].append(f"{z['id']}: no light of its own {z['why']}: {h['id'] or 'a new light'} "
                                    f"({h['kind']}) lights it, {why_served}")
                continue
            if got is None:
                lit = False
                rec["notes"].append(f"{z['id']}: no light {z['why']} ({why_not})")
                continue
            it = item(got, kind, f"lighting rule: {z['why']}", z["id"])
            adds.append(it)
            hung.append(_hung(got["center"][0], got["center"][1], kind,
                              kind == "pendant_light" and not task_pendant(it, pieces), None, task=ztask))
        rec["zones"].append({"id": z["id"], "kind": z["kind"], "had": had, "lit": lit})
    # 4. the general light the lumen method asks, outside the lit zones, spaced from every light
    rec["needed"] = max(count, len(hung))
    want = count - len(hung)
    if want > 0:
        lit_areas = [area for _z, area in singles if area is not None
                     and any(not h["row"] and area.contains(Point(h["xy"])) for h in hung)]
        blocked = unary_union(lit_areas) if lit_areas else None
        spots, why_left = general_spots(geo, [h["xy"] for h in hung], want,
                                        pendants=[h["xy"] for h in hung if h["pendant"]], blocked=blocked,
                                        areas=[area for _z, area in singles])
        for s in spots:
            got, _w = geo.hang("ceiling_light", s)
            if got is None:
                continue
            adds.append(item(got, "ceiling_light", f"lighting rule: general light for the area ({why})", None))
            hung.append(_hung(got["center"][0], got["center"][1], "ceiling_light", False, None))
        if len(spots) < want:
            rec["notes"].append(f"{want - len(spots)} general light(s) of the {count} the room needs have no place "
                                f"({why_left})")
            rec["needed"] = len(hung)
    rec["add"] = adds
    return rec


def general_spots(geo: Room, fixed: list[tuple[float, float]], want: int, pendants: Optional[list] = None,
                  blocked=None, areas: Optional[list] = None) -> tuple[list[tuple[float, float]], str]:
    """``want`` evenly spread spots (module docstring, step 2) among the room's free candidates (every
    ``RASTER_M`` inside the inset floor where a flush light hangs), at least ``MIN_GAP_M`` from the ``fixed`` lights
    and each other and ``MIXED_SPACING_M`` from the free ``pendants`` (29 Oct 2026, step 4), never in ``blocked`` (the
    lit zones) and at most one in each of the zone ``areas`` (step 5): farthest point first, then ``LLOYD_STEPS`` of
    centroidal Voronoi relaxation over the floor."""
    import numpy as np
    from shapely.geometry import Point

    pend = [tuple(p) for p in pendants or []]
    minx, miny, maxx, maxy = geo.poly.bounds
    xs = np.arange(minx + RASTER_M / 2.0, maxx, RASTER_M)
    ys = np.arange(miny + RASTER_M / 2.0, maxy, RASTER_M)
    outline = [tuple(p[:2]) for p in geo.room["polygon"]]
    floor, cands = [], []
    for y in ys:
        for x in xs:
            if not G.point_in_polygon((float(x), float(y)), outline):
                continue
            floor.append((float(x), float(y)))
            if blocked is not None and blocked.contains(Point(float(x), float(y))):
                continue
            if any(math.hypot(x - p[0], y - p[1]) < MIXED_SPACING_M - 1e-9 for p in pend):
                continue
            if geo.hang("ceiling_light", (float(x), float(y)))[0] is not None:
                cands.append((float(x), float(y)))
    if not cands or not floor:
        return [], ("no free place on the ceiling (walls, cabinets, door swings, a low slope, the lit zones, the "
                    "pendants' spacing)")
    F = np.array(floor)
    Cn = np.array(cands)
    fixed_a = np.array(fixed) if fixed else np.zeros((0, 2))
    zone_polys = [a for a in areas or [] if a is not None]
    member: dict = {}

    def areas_of(p) -> frozenset:
        key = (round(float(p[0]), 4), round(float(p[1]), 4))
        if key not in member:
            member[key] = frozenset(k for k, a in enumerate(zone_polys) if a.contains(Point(key)))
        return member[key]

    def gap_ok(p, others) -> bool:
        if not all(math.hypot(p[0] - o[0], p[1] - o[1]) >= MIN_GAP_M - 1e-9 for o in others):
            return False
        mine = areas_of(p)                     # 29 Oct 2026 (step 5): one light per zone
        return not mine or not any(mine & areas_of(o) for o in others)

    chosen: list[tuple[float, float]] = []
    for _ in range(want):
        pts = np.vstack([fixed_a, np.array(chosen)]) if chosen else fixed_a
        if len(pts):
            dist = np.min(np.hypot(Cn[:, None, 0] - pts[None, :, 0], Cn[:, None, 1] - pts[None, :, 1]), axis=1)
        else:
            cx, cy = F[:, 0].mean(), F[:, 1].mean()
            dist = -np.hypot(Cn[:, 0] - cx, Cn[:, 1] - cy)          # the first light: nearest the floor's middle
        order = np.lexsort((Cn[:, 1], Cn[:, 0], -dist))
        pick = next((tuple(map(float, Cn[i])) for i in order
                     if gap_ok(tuple(Cn[i]), list(map(tuple, pts)) if len(pts) else [])), None)
        if pick is None:
            break
        chosen.append(pick)
    for _ in range(LLOYD_STEPS):
        if not chosen:
            break
        allp = np.vstack([fixed_a, np.array(chosen)]) if len(fixed_a) else np.array(chosen)
        near = np.argmin(np.hypot(F[:, None, 0] - allp[None, :, 0], F[:, None, 1] - allp[None, :, 1]), axis=1)
        moved = False
        for j in range(len(chosen)):
            cells = F[near == len(fixed_a) + j]
            if not len(cells):
                continue
            cx, cy = cells[:, 0].mean(), cells[:, 1].mean()
            others = list(map(tuple, fixed_a)) + [c for k, c in enumerate(chosen) if k != j]
            order = np.argsort(np.hypot(Cn[:, 0] - cx, Cn[:, 1] - cy), kind="stable")
            best = next((tuple(map(float, Cn[i])) for i in order if gap_ok(tuple(Cn[i]), others)), None)
            if best is not None and best != chosen[j]:
                chosen[j] = best
                moved = True
        if not moved:
            break
    return [(round(x, 3), round(y, 3)) for x, y in chosen], "the free places are taken"


# --------------------------------------------------------------------------
# The decor stage and the check
# --------------------------------------------------------------------------

def room_lights(building: dict, room_id: str) -> list[dict]:
    return [d for d in building.get("decor") or [] if isinstance(d, dict) and d.get("room_id") == room_id
            and d.get("type") in LIGHT_TYPES and d.get("center")]


def remount(building: dict, room: dict, lights: list[dict]) -> list[str]:
    """In place: the room's flush ceiling lights under a slope mounted on it (``slope_mount``; their bottom moved to
    the plane over their centre); a light whose mount does not fit hangs level as before. A mount that is not this
    room's (a twin's mirrored copy carries its partner's plane) is made again. Returns the notes."""
    planes = D.ceiling_planes(building, room["level_id"])
    level = _level(building, room["level_id"])
    floor_z = float(level.get("elevation") or 0.0)
    notes = []
    for d in lights:
        if d.get("type") != "ceiling_light":
            continue
        w, dd, h = (float(v) for v in (list(d.get("size") or CEILING_LIGHT_SIZE) + [CEILING_LIGHT_SIZE[2]])[:3])
        sm = slope_mount(planes, floor_z, d["center"], (w, dd), h)
        if sm is not None and sm["fits"] and sm["lowest_m"] >= D.MIN_LIGHT_BOTTOM_M - 1e-9:
            if d.get("slope_mount") != sm:
                d["center"] = [d["center"][0], d["center"][1], round(sm["top_m"] - h, 3)]
                d["slope_mount"] = sm
                notes.append(f"{d.get('id')}: mounted on the sloped ceiling ({sm['tilt_deg']:.0f}°)")
        elif d.get("slope_mount"):
            d.pop("slope_mount")
            top = D.ceiling_over(building, room["level_id"], d["center"][:2], (w, dd), planes=planes) if planes \
                else float(level.get("ceiling_height") or 2.7)
            d["center"] = [d["center"][0], d["center"][1], round(top - h, 3)]
            notes.append(f"{d.get('id')}: hangs level (the slope mount of its copy does not fit here)")
    return notes


def add_lights(building: dict, new_id: Callable[[str], str], density_of: Optional[Callable[[dict], str]] = None,
               skip: Optional[set] = None, only: Optional[set] = None) -> tuple[list[dict], dict[str, list[str]]]:
    """In place: every lit room (``lit_room``; not in ``skip``, in ``only`` when given) gets the lights of its plan
    (``plan_room``; the items it replaces are taken out of ``building["decor"]``); returns ``(new items, {room id:
    notes})``. The decor stage lights the rooms before the twins copy their partner's decor (``skip`` the twins), then
    the twins whose copy lacks lights (``only``)."""
    by_room: dict[str, list[dict]] = {}
    for f in building.get("furniture") or []:
        if f.get("room_id"):
            by_room.setdefault(f["room_id"], []).append(f)
    new: list[dict] = []
    notes: dict[str, list[str]] = {}
    for room in building.get("rooms") or []:
        if not lit_room(room) or room["id"] in (skip or set()) or (only is not None and room["id"] not in only):
            continue
        existing = room_lights(building, room["id"])
        mine = remount(building, room, existing)
        try:
            rec = plan_room(building, room, by_room.get(room["id"], []), existing,
                            density_of(room) if density_of else "balanced")
        except (KeyError, TypeError, ValueError) as exc:
            notes.setdefault(room["id"], []).append(f"lighting rule not applied: {type(exc).__name__}: {exc}")
            continue
        if rec["remove"]:
            gone = set(rec["remove"])
            building["decor"] = [d for d in building.get("decor") or [] if d.get("id") not in gone]
        for it in rec["add"]:
            full = dict({"id": new_id(room["level_id"]), "kind": "decor", "level_id": room["level_id"],
                         "room_id": room["id"], "asset": None, "host_id": None, "source": "added_by_ai",
                         "method": "rule", "confidence": 0.7, "status": "verified"}, **it)
            building.setdefault("decor", []).append(full)
            new.append(full)
        mine += rec["notes"]
        if rec["add"] or rec["remove"]:
            mine.append(f"lighting rule: {rec['have']} -> {rec['have'] - len(rec['remove']) + len(rec['add'])} "
                        f"ceiling light(s) ({rec['why']})")
        if mine:
            notes[room["id"]] = mine
    return new, notes


def review(building: dict, density_of: Optional[Callable[[dict], str]] = None) -> tuple[list[dict], int]:
    """M17 (pure): ``(findings, checked)``: a lit room whose ceiling lights are fewer than the lighting rule hangs
    there (``plan_room`` on the room as built: what it would add or lay again). Major when the room has no light, less
    than half of them, or a dining table or bed without its light; else minor. 29 Oct 2026 (UL91): every pair of the
    room's lights that hangs too close or in one zone (``plan_room``'s ``too_close``) is a major finding of its own
    (``metrics.rule`` ``spacing``), the second light its target."""
    value = ((building.get("project") or {}).get("brief") or {}).get("decor", True)
    if value is False or str(value).strip().lower() in ("false", "off", "none", "no"):
        return [], 0              # the brief turns decor off (= decor_ai.decor_mode "off"): no decor light is asked
    by_room: dict[str, list[dict]] = {}
    for f in building.get("furniture") or []:
        if f.get("room_id"):
            by_room.setdefault(f["room_id"], []).append(f)
    out, n = [], 0
    for room in building.get("rooms") or []:
        if not lit_room(room):
            continue
        n += 1
        have = room_lights(building, room["id"])
        rec = plan_room(building, room, by_room.get(room["id"], []), have,
                        density_of(room) if density_of else "balanced")
        for pair in rec.get("too_close") or []:
            # 29 Oct 2026 (UL91, "2 lights together not making sense"): two lights too close or in one zone
            a, b = pair["ids"]
            out.append({"check": REVIEW_CHECK, "severity": "major", "target": b, "room_id": room["id"],
                        "message": (f"{room['id']}: {b} ({pair['kinds'][1]}) and {a} ({pair['kinds'][0]}) hang "
                                    f"{pair['distance_m']:.2f} m apart: {pair['why']}; the lighting rule takes {b} "
                                    f"out"),
                        "metrics": {"model_review": True, "rule": "spacing", "ids": [a, b],
                                    "distance_m": pair["distance_m"], "zone": pair.get("zone"),
                                    "spacing_m": LIGHT_SPACING_M, "mixed_spacing_m": MIXED_SPACING_M,
                                    "lesson": "UL91"}})
        if not rec["add"]:
            continue
        need = len(have) - len(rec["remove"]) + len(rec["add"])
        unlit = [z for z in rec["zones"] if z["kind"] in ("dining", "bed", "island") and not z["had"] and z["lit"]]
        if need <= len(have) and not unlit:
            continue                  # 29 Oct 2026: the plan moves lights the spacing takes out (found above), no more
        major = not have or len(have) * 2 < need or bool(unlit)
        zones_txt = ", ".join(f"{z['kind']} {z['id']}" for z in unlit)
        msg = (f"{room['id']} ({room.get('room_type')}, {_area(room):.1f} m²) has {len(have)} ceiling light(s) where "
               f"the lighting rule hangs {need}: {rec['why']}" + (f"; unlit: {zones_txt}" if zones_txt else ""))
        out.append({"check": REVIEW_CHECK, "severity": "major" if major else "minor", "target": room["id"],
                    "room_id": room["id"], "message": msg,
                    "metrics": {"model_review": True, "have": len(have), "needed": need,
                                "area_m2": round(_area(room), 2), "add": len(rec["add"]), "relay": len(rec["remove"]),
                                "unlit_zones": [z["id"] for z in unlit], "rule": RULE}})
    return out, n
