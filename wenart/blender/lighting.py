"""Lighting from the style profile (docs/milestone3.md §3, lighting.py).

- World: HDRI from the assets manifest when available, else a physical sky
  (materials.world_nodes); strength from the mood.
- Sun lamp at the style's elevation / azimuth; colour through the lamp's
  blackbody temperature (SunLight.use_temperature / temperature, Blender 5.2),
  strength in W/m2 from ``sun_strength``.
- One soft area light at the ceiling of every room that has no window on its
  edges, recorded as ``assumed`` in the manifest. Rooms with windows get their
  light from the sun and the sky only (no fill light: per-camera exposure
  makes dark rooms readable, and the documents say nothing about lamps).
- One light portal per window (docs/milestone5.md §2.3): an AREA light,
  shape RECTANGLE, ``size = width - 2 * frame``, ``size_y = height - 2 *
  frame``, centred in the opening just inside the inner wall face, local -Z
  into the room, ``light.cycles.is_portal = True``. A portal emits nothing;
  it tells Cycles where the sky comes in, which cut the noise of the world
  light by 21-46 % at equal samples in the Milestone 5 test room. Manifest
  entry ``kind: light, status: assumed, reason: portal``. Portals are only
  unbiased with the camera-only window glass of materials.py.

Azimuth is compass degrees clockwise from north (+Y); elevation above the
horizon. Blender lamps shine along their local -Z.

Milestone 6 (docs/milestone6.md §5 rows 5 and 6):

- the ceiling light of a room sits at the polygon's pole of inaccessibility
  (``polylabel``, pure Python, 1 cm precision: the inside point farthest
  from the boundary; an L-shaped hall's centroid can lie outside it) and its
  square is at most ``sqrt(2) * distance`` wide, so all of it is inside the
  room (``area_light_plan``);
- dim rooms (window area / floor area < ``DIM_ROOM_RATIO``) get the same
  ceiling light at half the power per m2 (6 W/m2), invisible to the camera,
  recorded ``assumed`` with the ratio as the reason (lighting mood: the
  documents say nothing about lamps).

Milestone 7 (docs/milestone7.md §6.4): the stair openings of a level
(``shell.plan_stairs``) are holes for ``polylabel``, so a ceiling light never
hangs in an opening, among the steps of the last flight.

Milestone 13 (docs/milestone13.md §13.1 track T5, K5; the diagnosis §1.6: the sun was 3.0 W/m² against the
manual's 1000 W/m² clear sky, so every room with a window metered 100x darker than a room lit by the assumed
ceiling light and was pushed +3..+8 EV):

- ``SUN_STRENGTH_WM2`` is the one sun constant (W/m², ``SunLight.energy``; the manual's "Power of Lights" table:
  clear sky 1000, cloudy 500, overcast 200, moonlight 0.001 W/m²). The style's per-mood ``sun_strength`` is a
  relative factor against the warm-daylight value (``SUN_REFERENCE_MOOD_WM2``): overcast keeps a tenth of the
  sun, night none. Round 3 (docs/milestone13.md §14.3, pod P1 of 15 Oct 2026): the constant is the manual's
  clear-sky 1000 W/m²; the same constant drives the exterior sun lamp.
- ``WENART_LIGHT_VARIANT`` (environment) picks the levers of the A/B (``light_levers``): ``m11`` = every lever at
  its Milestone 11 value (sun 3.0 W/m², EV limits -2..+8, no rig, Milestone 11 shell materials: the "before" of
  every sheet); ``base`` = the production defaults (the constant and ``LEVER_DEFAULTS``, what an unset variable
  gives, recorded under its name); ``sun100`` / ``sun300`` / ``sun1000`` = the sun at that many W/m² on the
  Milestone 11 look; ``evcap`` = the EV cap +3 of ``render.EXPOSURE_LIMITS`` with the ``lighting_dark`` finding;
  ``rig`` = the room light rig below; ``shell`` = the shell material table of ``materials.shell_material`` with the
  sheen / coat / bevel / AO / imperfection layers; ``all`` = ``sun300`` + ``evcap`` + ``rig`` + ``shell`` (the P1
  definition, kept so the P1 sheets stay comparable); several names joined by ``,`` or ``+`` combine
  (``sun1000,rig``: the Milestone 11 look plus those levers; ``base,sun300``: production with that sun). An
  unknown name raises (a typo must never run the base silently). Unset = production: the constant, the EV cap, the
  rig and the shell table on (``LEVER_DEFAULTS``, the lead's decisions from P1). The scene manifest's
  ``lighting`` block records the variant, every lever and the sun (constant, mood factor, applied).
- The dim-room rule follows the sun (``fill_light_reason(..., sun_wm2=)``): the window / floor ratio is scaled by
  ``sun / SUN_REFERENCE_MOOD_WM2`` before the ``DIM_ROOM_RATIO`` test, so a 300 W/m² sun through a small window
  no longer asks for the fill light a 3 W/m² sun needed.
- ``room_rig(room_type)`` is the light rig per room type (``ROOM_RIGS``): visible emissive fixtures with real sizes
  and a point or area light inside each, powered from real lumens through the manual's radiant-power table
  (``watts_for_lumens``: 800 lm LED bulb 2.1 W, 1000 lm bulb 2.9 W, 1500 lm floodlight 4 W, 2500 lm tube 4.5 W;
  linear between the rows) times ``RIG_GAIN``; colour from ``rig_temperature_k`` (the style's
  ``lighting.colour_temperature_k`` when it is warmer than ``RIG_WARM_K``, else 2700 K). ``rig_plan`` places
  them (pure): a pendant over the dining table, a ceiling fixture in halls, stairs, kitchens and bathrooms at the
  pole of inaccessibility (one per ``area_light_plans`` point in a long room), bedside lamps on the nightstands
  (else beside the bed head), a strip under the kitchen wall cabinets along the counter run, a mirror light over
  the washbasin; a fixture whose anchor piece is missing is dropped with the reason. With the rig a windowless
  or dim room keeps no invisible area light (the fixtures carry its light, recorded ``assumed``); a room type
  without a rig keeps the Milestone 6 light. Every fixture is ``assumed`` (the documents say nothing about lamps).
- Round 3 (§14.3): ``RIG_GAIN`` is 2.0; the visible shade of a fixture emits at the fixed radiance
  ``SHADE_EMISSION_WM2SR`` (``materials.fixture_material``), no longer tied to the lamp power, so a shade never
  clips at the project EV range; every rig object (the shade mesh and its light) carries ``wenart_rig`` so render.py
  can hide the rig while it meters the project white point on daylight only.
"""
from __future__ import annotations

import heapq
import math
import os

from wenart import geometry as G
from wenart.blender.cameras import room_openings

# The portal sits this far inside the inner wall face (in the reveal, in front of the frame).
PORTAL_INSET_M = 0.01

# --------------------------------------------------------------------------
# Milestone 13: the sun constant and the lever variants (docs/milestone13.md §13.2, §13.3)
# --------------------------------------------------------------------------

# The sun lamp's strength in W/m² (bpy.types.SunLight.energy, "Sunlight strength in watts per meter squared").
# The Blender 5.2 manual (render/lights/light_object.html, "Power of Lights") gives clear sky 1000, cloudy sky 500,
# overcast sky 200, moonlight 0.001 W/m². Milestone 11 rendered with 3.0 (the style's warm-daylight sun_strength,
# vocabulary.LIGHTING). Round 3: the manual's clear-sky value, decided from the P1 lever A/B of 15 Oct 2026
# (docs/milestone13.md §14.3; runs/20261015-165506-m13_p1/results/ab_m13/summary.md): sun1000 reads most natural
# (a real sun patch through the window, clean contrast, warm, no clipping seen); the metered EV of the rooms with
# windows falls to 2.5-4.3 (real02 salon_1 2.46, salon_2 2.54, mutfak_1 4.31, yatak_odasi_1 3.16, e_yatak_odasi_1
# 2.16), where the 3 W/m² sun had lifted the sunless rooms +6..+9 EV (real02 mutfak_1 9.21, yatak_odasi_1 7.42,
# real03 giris_holu_1 7.79). One number to change, recorded in every scene manifest
# (lighting.sun.strength_wm2_constant); the same constant drives the exterior sun lamp.
SUN_STRENGTH_WM2 = 1000.0
# The style's per-mood sun_strength (vocabulary.LIGHTING) is a factor against the warm-daylight value: the lamp
# gets SUN_STRENGTH_WM2 x sun_strength / SUN_REFERENCE_MOOD_WM2 (overcast 0.3 -> a tenth, night 0 -> no sun).
SUN_REFERENCE_MOOD_WM2 = 3.0
SUN_STRENGTH_M11_WM2 = 3.0            # the m11 variant's sun (the Milestone 11 renders of real02 / real03)
LIGHT_VARIANT_ENV = "WENART_LIGHT_VARIANT"
SUN_VARIANT_WM2 = {"sun100": 100.0, "sun300": 300.0, "sun1000": 1000.0}
ALL_VARIANT_SUN = "sun300"            # the sun of the `all` variant (the P1 middle candidate; the P1 sheets compare)
# Round 3 (§14.3): ``m11`` is the Milestone 11 look (the "before" of every A/B sheet: sun 3 W/m², EV limits
# -2..+8, no rig, the Milestone 6-12 materials), ``base`` the production defaults (the constant and
# LEVER_DEFAULTS, what an unset variable gives, recorded under its name). The single levers start from the
# Milestone 11 look as they did in P1, so a P1 sheet and a round-3 sheet of the same name show the same thing.
LIGHT_VARIANTS = ("m11", "base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
M11_LEVERS = {"ev_cap": False, "rig": False, "shell": False}
# Production (no variant): the lead's decisions from P1 (§14.3). The EV cap +3 with the lighting_dark finding (the
# cap alone turned the real02 kitchen black, 9.21 -> 3.0 EV: with the rig it is a finding, not a fix); the room
# light rig (the kitchen strip and pendant took real02 mutfak_1 from +9.21 to +1.02 EV at gain 4); the shell
# material table (ceiling plaster, worktops, fronts, tiles: no harm at 1080p, +35 % render time, 6.4 vs 4.8 s).
# Three flags, recorded in every scene manifest (lighting.levers).
LEVER_DEFAULTS = {"ev_cap": True, "rig": True, "shell": True}


def parse_light_variant(text) -> list[str]:
    """The variant names of a ``WENART_LIGHT_VARIANT`` value (pure): ``"sun300"`` -> ``["sun300"]``,
    ``"sun1000,rig"`` / ``"sun1000+rig"`` -> both; empty / None -> ``[]`` (production). An unknown name raises
    ValueError (a typo must never run the base silently); two sun strengths in one value raise too, as do ``m11``
    and ``base`` together (the Milestone 11 look and the production defaults exclude each other)."""
    if text is None:
        return []
    names = [n.strip().lower() for n in str(text).replace("+", ",").split(",") if n.strip()]
    unknown = [n for n in names if n not in LIGHT_VARIANTS]
    if unknown:
        raise ValueError(f"{LIGHT_VARIANT_ENV}={text!r}: unknown variant {unknown}; one of {list(LIGHT_VARIANTS)}")
    suns = [n for n in names if n in SUN_VARIANT_WM2]
    if len(suns) > 1:
        raise ValueError(f"{LIGHT_VARIANT_ENV}={text!r}: more than one sun strength ({suns})")
    if "m11" in names and "base" in names:
        raise ValueError(f"{LIGHT_VARIANT_ENV}={text!r}: m11 (the Milestone 11 look) and base (production) exclude "
                         f"each other")
    return list(dict.fromkeys(names))


def light_levers(variant=None, env=None) -> dict:
    """The levers of a build or render (pure): ``{"variant": str | None, "names": [...], "sun_wm2", "ev_cap",
    "rig", "shell", "source"}``. ``variant`` (a value as the environment variable would hold it) wins over
    ``env[LIGHT_VARIANT_ENV]`` (``os.environ`` when None). No variant = production: ``SUN_STRENGTH_WM2`` and
    ``LEVER_DEFAULTS``. ``base`` = production under its name; ``m11`` = the Milestone 11 look (``M11_LEVERS``, sun
    ``SUN_STRENGTH_M11_WM2``); every other name starts from the Milestone 11 look (from production when ``base``
    is among the names) and turns the named levers on (never off)."""
    source = "arg"
    if variant is None:
        variant = (os.environ if env is None else env).get(LIGHT_VARIANT_ENV)
        source = "env" if variant not in (None, "") else "default"
    names = parse_light_variant(variant)
    if not names:
        return {"variant": None, "names": [], "sun_wm2": float(SUN_STRENGTH_WM2), "source": source,
                **{k: bool(v) for k, v in LEVER_DEFAULTS.items()}}
    on = set(names)
    if "all" in on:
        on |= {ALL_VARIANT_SUN, "evcap", "rig", "shell"}
    production = "base" in on
    start = LEVER_DEFAULTS if production else M11_LEVERS
    sun = next((SUN_VARIANT_WM2[n] for n in LIGHT_VARIANTS if n in on and n in SUN_VARIANT_WM2),
               SUN_STRENGTH_WM2 if production else SUN_STRENGTH_M11_WM2)
    return {"variant": ",".join(names), "names": names, "sun_wm2": float(sun),
            "ev_cap": bool(start["ev_cap"]) or "evcap" in on, "rig": bool(start["rig"]) or "rig" in on,
            "shell": bool(start["shell"]) or "shell" in on, "source": source}


def sun_strength_wm2(lighting: dict, levers: dict | None = None) -> tuple[float, float]:
    """``(strength W/m², mood_factor)`` of the sun lamp (pure): the levers' ``sun_wm2`` (``light_levers``) times
    the style's ``sun_strength`` over ``SUN_REFERENCE_MOOD_WM2`` (1.0 for warm daylight, 0.1 overcast, 0 night)."""
    levers = levers or light_levers()
    factor = float((lighting or {}).get("sun_strength", SUN_REFERENCE_MOOD_WM2)) / SUN_REFERENCE_MOOD_WM2
    factor = max(0.0, factor)
    return round(float(levers["sun_wm2"]) * factor, 6), round(factor, 6)


def portal_plan(opening: dict, wall: dict, level: dict, levels_above: bool, rooms: list[dict]) -> dict:
    """Where the portal of one window goes (pure; no bpy).

    Returns ``{"center": [x, y, z], "size": [w, h], "inward": [nx, ny],
    "room_id": id | None, "note": str | None}``: the rectangle is the glass
    area (opening minus the frame on every side), centred on the opening
    projected onto the wall centre line and moved ``thickness / 2 -
    PORTAL_INSET_M`` towards the room. ``inward`` points into the room the
    window lights: the side of the wall that lies in a room polygon; when
    both or neither side does (an interior window, a broken plan) the side
    away from the outside of the wall is taken and ``note`` says so."""
    from wenart.blender.shell import DEFAULTS, opening_centre_on_wall, opening_vertical

    bottom, top, _ = opening_vertical(opening, level, levels_above)
    frame = DEFAULTS["frame_width"]
    width = float(opening["width"])
    cx, cy, _shift = opening_centre_on_wall(opening, wall)
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    thickness = float(wall["thickness"])
    reach = thickness / 2.0 + DEFAULTS["face_probe"]
    sides = {}
    for side in (1, -1):
        probe = (cx + side * nx * reach, cy + side * ny * reach)
        sides[side] = next((r for r in rooms if len(r["polygon"]) >= 3 and G.point_in_polygon(probe, r["polygon"])),
                           None)
    note = None
    if (sides[1] is None) != (sides[-1] is None):
        side = 1 if sides[1] is not None else -1
    else:
        side = 1
        note = ("rooms on both sides of the window: portal faces the left side of the wall"
                if sides[1] is not None else "no room on either side of the window: portal faces the left side")
    inward = (side * nx, side * ny)
    depth = thickness / 2.0 - PORTAL_INSET_M
    return {
        "center": [cx + inward[0] * depth, cy + inward[1] * depth, (bottom + top) / 2.0],
        "size": [max(0.01, width - 2.0 * frame), max(0.01, (top - bottom) - 2.0 * frame)],
        "inward": [inward[0], inward[1]],
        "room_id": sides[side]["id"] if sides[side] is not None else None,
        "note": note,
    }

# Area light power scales with the floor area (a fixed 120 W washed out a 3 m2 WC).
AREA_LIGHT_W_PER_M2 = 12.0
AREA_LIGHT_MIN_W = 10.0
AREA_LIGHT_MAX_W = 150.0
AREA_LIGHT_MAX_SIZE = 1.5
AREA_LIGHT_MIN_SIZE = 0.3
AREA_LIGHT_CEILING_GAP = 0.05
# Dim rooms (Milestone 6): window area / floor area below this gets the ceiling light at DIM_POWER_FACTOR.
DIM_ROOM_RATIO = 0.08
DIM_POWER_FACTOR = 0.5
POLYLABEL_PRECISION_M = 0.01
# real03 (10 Oct 2026): a 20 m floor hall under one 150 W light rendered black. A room longer than LONG_ROOM_M and at
# least LONG_ROOM_ASPECT times as long as wide gets one light per LIGHT_SPACING_M of its length, each up to
# AREA_LIGHT_MAX_W; a light stays LIGHT_EDGE_M inside the room.
LONG_ROOM_M = 5.0
LONG_ROOM_ASPECT = 2.0
LIGHT_SPACING_M = 3.0
LIGHT_EDGE_M = 0.2
LIGHT_ACROSS_SAMPLES = 9


# --------------------------------------------------------------------------
# Pole of inaccessibility (pure Python; Blender's Python has no shapely)
# --------------------------------------------------------------------------

def _signed_distance(x: float, y: float, polygon, holes=()) -> float:
    """Distance from (x, y) to the polygon boundary, negative outside.
    ``holes`` (Milestone 7: stair openings in the ceiling) count as outside,
    and their edges as boundary (even-odd over all rings, as Mapbox's polylabel)."""
    inside = False
    best = math.inf
    for ring in (polygon, *holes):
        n = len(ring)
        for i in range(n):
            ax, ay = ring[i]
            bx, by = ring[(i + 1) % n]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                inside = not inside
            dx, dy = bx - ax, by - ay
            length_sq = dx * dx + dy * dy
            t = 0.0 if length_sq == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / length_sq))
            px, py = ax + t * dx - x, ay + t * dy - y
            best = min(best, px * px + py * py)
    d = math.sqrt(best)
    return d if inside else -d


def polylabel(polygon, precision: float = POLYLABEL_PRECISION_M, holes=()) -> tuple[float, float, float]:
    """``(x, y, distance)``: the pole of inaccessibility of a simple polygon,
    the inside point farthest from its boundary, to within ``precision``
    (Mapbox's polylabel: square cells over the bounding box in a priority
    queue by the best distance a cell could still hold; cells that cannot
    beat the best found by more than ``precision`` are dropped). The
    centroid and the bounding-box centre seed the search. Deterministic.
    ``holes``: polygons inside it that are not part of it (each lying
    inside ``polygon`` or beyond its edges; Milestone 7 stair openings)."""
    poly = [(float(p[0]), float(p[1])) for p in polygon]
    if len(poly) > 1 and poly[0] == poly[-1]:
        poly = poly[:-1]
    if len(poly) < 3:
        raise ValueError("polylabel needs a polygon with at least 3 points")
    rings = [[(float(p[0]), float(p[1])) for p in h] for h in holes if len(h) >= 3]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    width, height = x1 - x0, y1 - y0
    cell = min(width, height)
    if cell <= 0:
        return x0, y0, 0.0
    h = cell / 2.0
    queue: list = []
    counter = 0

    def push(cx: float, cy: float, half: float) -> None:
        nonlocal counter
        d = _signed_distance(cx, cy, poly, rings)
        heapq.heappush(queue, (-(d + half * math.sqrt(2.0)), counter, cx, cy, half, d))
        counter += 1

    y = y0
    while y < y1:
        x = x0
        while x < x1:
            push(x + h, y + h, h)
            x += cell
        y += cell
    cx, cy = G.polygon_centroid(poly)
    best = (cx, cy, _signed_distance(cx, cy, poly, rings))
    bx, by = x0 + width / 2.0, y0 + height / 2.0
    d = _signed_distance(bx, by, poly, rings)
    if d > best[2]:
        best = (bx, by, d)
    while queue:
        neg_max, _, cx, cy, half, d = heapq.heappop(queue)
        if d > best[2]:
            best = (cx, cy, d)
        if -neg_max - best[2] <= precision:
            continue
        half /= 2.0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                push(cx + sx * half, cy + sy * half, half)
    return best


def area_light_plan(polygon, holes=()) -> dict:
    """Where a room's square ceiling light goes (pure): ``{"center": [x, y],
    "size", "boundary_distance"}``. Centre = ``polylabel``; size = half the
    smaller bounding-box side, between ``AREA_LIGHT_MIN_SIZE`` and
    ``AREA_LIGHT_MAX_SIZE``, and never above ``sqrt(2) * distance`` so the
    whole square (half-diagonal = size / sqrt(2)) lies inside the room.
    ``holes`` (Milestone 7): the stair openings of the level; the light stays
    under the ceiling that is left, never in an opening."""
    x, y, d = polylabel(polygon, holes=holes)
    d = math.floor(d * 1e4) / 1e4                      # recorded to 0.1 mm, never more than the real distance
    bx0, by0, bx1, by1 = G.bbox(polygon)
    size = min(AREA_LIGHT_MAX_SIZE, max(AREA_LIGHT_MIN_SIZE, min(bx1 - bx0, by1 - by0) * 0.5))
    size = min(size, math.floor(math.sqrt(2.0) * d * 1e4) / 1e4)
    return {"center": [round(x, 4), round(y, 4)], "size": round(size, 4), "boundary_distance": d}


def _long_axis(polygon) -> float:
    """Angle (radians) of the polygon's longest edge: the frame a room's length is measured in (pure)."""
    best, angle = -1.0, 0.0
    n = len(polygon)
    for i in range(n):
        (ax, ay), (bx, by) = polygon[i], polygon[(i + 1) % n]
        length = math.hypot(bx - ax, by - ay)
        if length > best:
            best, angle = length, math.atan2(by - ay, bx - ax)
    return angle


def area_light_plans(polygon, holes=(), spacing: float = LIGHT_SPACING_M) -> list[dict]:
    """The ceiling lights of a room (pure): ``area_light_plan`` for an ordinary room; for a long room (longer than
    ``LONG_ROOM_M`` and ``LONG_ROOM_ASPECT`` x its width, in the frame of its longest edge) one light per
    ``spacing`` of its length, each at the point across the room furthest from the walls, at least ``LIGHT_EDGE_M``
    inside (a stretch where no such point exists gets none). Fewer than two lights found -> the single plan."""
    single = [area_light_plan(polygon, holes=holes)]
    a = _long_axis(polygon)
    ca, sa = math.cos(a), math.sin(a)
    local = [(x * ca + y * sa, -x * sa + y * ca) for x, y in polygon]
    u0, u1 = min(p[0] for p in local), max(p[0] for p in local)
    v0, v1 = min(p[1] for p in local), max(p[1] for p in local)
    length, width = u1 - u0, v1 - v0
    if length <= LONG_ROOM_M or width <= 0 or length < LONG_ROOM_ASPECT * width:
        return single
    n = max(2, math.ceil(length / spacing))
    plans = []
    for i in range(n):
        u = u0 + (i + 0.5) * length / n
        best = None
        for j in range(LIGHT_ACROSS_SAMPLES):
            v = v0 + (j + 0.5) * width / LIGHT_ACROSS_SAMPLES
            x, y = u * ca - v * sa, u * sa + v * ca
            d = _signed_distance(x, y, polygon, holes)
            if best is None or d > best[2]:
                best = (x, y, d)
        if best is None or best[2] < LIGHT_EDGE_M:
            continue
        d = math.floor(best[2] * 1e4) / 1e4
        size = min(AREA_LIGHT_MAX_SIZE, max(AREA_LIGHT_MIN_SIZE, min(width, length / n) * 0.5))
        size = min(size, math.floor(math.sqrt(2.0) * d * 1e4) / 1e4)
        plans.append({"center": [round(best[0], 4), round(best[1], 4)], "size": round(size, 4), "boundary_distance": d})
    return plans if len(plans) >= 2 else single


def light_power(area: float, n_lights: int, dim: bool, factor: float = 1.0) -> tuple[float, float]:
    """``(power per light, w_per_m2)`` (pure): ``AREA_LIGHT_W_PER_M2`` x area (half in a dim room), at most
    ``AREA_LIGHT_MAX_W`` per light, times the agent's ``factor``, at least ``AREA_LIGHT_MIN_W`` per light."""
    per_m2 = AREA_LIGHT_W_PER_M2 * (DIM_POWER_FACTOR if dim else 1.0)
    n = max(1, int(n_lights))
    total = min(AREA_LIGHT_MAX_W * n, per_m2 * float(area)) * float(factor)
    return max(AREA_LIGHT_MIN_W, total / n), per_m2


def daylight_window(opening: dict, walls_by_id: dict, flagged: bool) -> bool:
    """Whether a window brings daylight into its room (pure): one on an outer wall (``exterior``). real03 run 2
    (10 Oct 2026): glazing in the walls between the floor hall, the stairs and the lift lobby counted as daylight,
    so those rooms got no ceiling light and rendered black. A building whose walls carry no ``exterior`` flag at all
    (``flagged`` False) keeps every window."""
    if not flagged:
        return True
    wall = walls_by_id.get(opening.get("wall_id"))
    return wall is None or bool(wall.get("exterior"))


def window_floor_ratio(windows: list[dict], level: dict, levels_above: bool, floor_area: float) -> float:
    """Window opening area (width x height, ``shell.opening_vertical``) over the floor area."""
    from wenart.blender.shell import opening_vertical

    glass = 0.0
    for o in windows:
        bottom, top, _ = opening_vertical(o, level, levels_above)
        glass += float(o["width"]) * max(0.0, top - bottom)
    return glass / max(float(floor_area), 1e-6)


def fill_light_reason(windows: list[dict], ratio: float | None, sun_wm2: float | None = None) -> str | None:
    """Why a room gets the assumed ceiling light, or None: no window, or a
    window area below ``DIM_ROOM_RATIO`` of the floor area.

    Milestone 13: ``sun_wm2`` (the lamp's strength) scales the ratio by ``sun_wm2 / SUN_REFERENCE_MOOD_WM2``
    first: the rule was written for the 3 W/m² sun, and a 300 W/m² sun brings 100x the daylight through the same
    window. None keeps the Milestone 6 rule as it was.

    Round 3, the rule at 1000 W/m² (scale 333, checked on the P1 rows of §14.3): a room with any window counts as
    daylit, so the 12 W/m² fill light never dominates a sunlit room (its 0.5-1.2 incident would be 3-8x the sun's
    0.16 in real02 salon_1); a room without a window still gets "room has no window" and with it the fill light,
    or the rig where its type has one. A room whose window faces away from the sun stays sky-lit as in Milestone
    11 (real03 yasama_6_1: 4.9 EV under sun1000) and ends as a ``lighting_dark`` finding for the lighting tools,
    not as a fill light: the rule cannot tell such a window from a sunlit one."""
    if not windows:
        return "room has no window"
    if ratio is None:
        return None
    scale = 1.0 if sun_wm2 is None else max(float(sun_wm2), 0.0) / SUN_REFERENCE_MOOD_WM2
    effective = ratio * scale
    if effective < DIM_ROOM_RATIO:
        if sun_wm2 is None or abs(scale - 1.0) < 1e-9:
            return f"room has little daylight (window/floor {ratio:.3f} < {DIM_ROOM_RATIO})"
        return (f"room has little daylight (window/floor {ratio:.3f} x sun {float(sun_wm2):g}/"
                f"{SUN_REFERENCE_MOOD_WM2:g} W/m2 = {effective:.3f} < {DIM_ROOM_RATIO})")
    return None


def light_ceiling(ceiling_at, level: dict, center, size: float, ceil_z: float) -> float:
    """The ceiling height a square ceiling light of ``size`` at ``center`` hangs under (pure): the lowest of the
    flat ceiling and the sloped ceiling at its centre and its four corners. Milestone 11 (track C): under a slope
    the centre alone let the downhill half of the square rise through the roof, where it lit the roof's top
    surface (glowing slits on real02's mansard)."""
    h = float(size) / 2.0
    cx, cy = float(center[0]), float(center[1])
    pts = [(cx, cy)] + [(cx + sx * h, cy + sy * h) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    return min([float(ceil_z)] + [float(ceiling_at(level, x, y)) for x, y in pts])


def stair_openings(building: dict, level: dict) -> list[list[tuple[float, float]]]:
    """The ceiling openings of the stairs of a level (pure, ``shell.plan_stairs``): every void loop."""
    from wenart.blender.shell import plan_stairs

    return [loop for s in plan_stairs(building, level) if s["plan"] is not None for loop in s["plan"]["void"]]


def sun_direction(elevation_deg: float, azimuth_deg: float) -> tuple[float, float, float]:
    """Unit vector from the scene towards the sun."""
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    return (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))


def building_azimuth(compass_azimuth_deg: float, north_deg: float = 0.0) -> float:
    """The sun's azimuth in the building frame (clockwise from the building's +Y) of a compass azimuth
    (clockwise from north), when the building's +Y axis points to the compass bearing ``north_deg``
    (``site.north_deg``, Milestone 10; 0 = +Y is north, the M3-M9 convention)."""
    return (float(compass_azimuth_deg) - float(north_deg)) % 360.0


def world_lighting(lighting: dict, azimuth_building_deg: float) -> dict:
    """The style's lighting for ``materials.world_nodes`` with the sun azimuth in the building frame (pure): the
    sky's sun (physical sky) and the HDRI turn now follow the sun lamp, which already uses the building frame
    (``building_azimuth``). Before, a building with a known north got the lamp from one direction and the sky's
    bright side from another."""
    return dict(lighting, sun_azimuth_deg=float(azimuth_building_deg))


# --------------------------------------------------------------------------
# Milestone 13: the light rig per room type (docs/milestone13.md §13.2 room_rig)
# --------------------------------------------------------------------------

# Radiant power per lumen: the Blender 5.2 manual's table (render/lights/light_object.html, "Power of Lights":
# "here is a table of typical power values for point, spot, and area lights"): candle 0.05 W, 800 lm LED bulb 2.1 W,
# 1000 lm light bulb 2.9 W, 1500 lm PAR38 floodlight 4 W, 2500 lm fluorescent tube 4.5 W. watts_for_lumens reads
# the table linearly between the rows and with the last row's ratio beyond it.
LUMEN_WATT_TABLE: tuple[tuple[float, float], ...] = ((0.0, 0.0), (800.0, 2.1), (1000.0, 2.9), (1500.0, 4.0),
                                                     (2500.0, 4.5))
LUMEN_WATT_SOURCE = ("Blender 5.2 manual, render/lights/light_object.html, 'Power of Lights' table "
                     "(800 lm LED bulb 2.1 W, 1000 lm bulb 2.9 W, 1500 lm PAR38 4 W, 2500 lm tube 4.5 W)")
# The manual's radiant powers put a lamp-lit room 4-6 stops under the metering target of the Milestone 11
# convention (a 12 W/m² invisible area light, EV about -0.5); the EV cap of render.EXPOSURE_LIMITS allows +3.
# Round 3 (§14.3, the P1 rig variant at gain 4.0, runs/20261015-165506-m13_p1/results/ab_m13/summary.md): the
# kitchen strip and pendant took real02 mutfak_1 from 9.21 to 1.02 EV (mutfak_2 8.90 -> 1.14) and e_banyo_1 to
# 0.89 EV, but the bedside lamps and the shades blew out white (the 'rig' and 'all' sheets of real02
# yatak_odasi_1). Gain 2.0 (one stop over the table) keeps the kitchen near EV 2 (the estimate from the P1 rows:
# 0.045 daylight at sun 1000 + 0.44 / 2 of rig = 0.27 incident -> +1.8 EV, under the cap) and the bathroom at
# about +1.9; the shade's look is decoupled from the gain below (SHADE_EMISSION_WM2SR). Every fixture records the
# radiometric watts and the applied watts (1.0 = the table as is).
RIG_GAIN = 2.0
# The visible shade or diffuser of a fixture is an Emission surface at this fixed radiance in W/(m²·sr) (for a
# material an Emission Strength of 1.0 renders exactly the Emission Color: the 5.2 manual,
# render/shader_nodes/shader/emission.html), no longer tied to the lamp power (P1: at 6.0 every shade rendered
# pure white at EV 3-5.5, 6 x 2^4.58 = 144 scene-linear in yatak_odasi_1). The bound: the project EV range of
# render.EXPOSURE_LIMITS is -2..+3, the display is AgX with the "AgX - Punchy" look, and a scene-linear value of
# SHADE_EMISSION_CLIP renders as display 255 for a white emitter (measured on bpy 5.2.2 on 15 Oct 2026, an
# emissive plane at EV 0, view AgX, look "AgX - Punchy" read back: display 177 / 202 / 222 / 237 / 249 / 255 for
# 1 / 2 / 4 / 8 / 16 / 32; the 2700 K colour (1.0, 0.65, 0.34) gives 250 / 241 / 232 at 16 and 255 / 252 / 245 at
# 32, its red channel clipping first; the look "None" clips white at 16 already, 255, so the production look is
# the one that matters). At the cap +3 (x 8) a shade of strength S shows 8 S in its red channel, so
# shade_emission_bound() = 32 / 8 = 4.0 is the limit; 2.0 keeps one stop of margin: 16 at +3 (bright, still warm:
# 250 / 241 / 232), 8 at the +2 of a lamp-lit room (239 / 227 / 215), 0.5 at -2 (a soft warm glow). Verified on
# P3 against the P1 'rig' and 'all' sheets of real02 yatak_odasi_1 (the bedside lamp) and mutfak_1 (the strip).
SHADE_EMISSION_WM2SR = 2.0
SHADE_EMISSION_CLIP = 32.0            # scene-linear value that AgX Punchy shows as display 255 (bpy 5.2.2, measured)
SHADE_EV_MAX = 3.0                    # = render.EXPOSURE_LIMITS[1] (pinned equal in tests/test_m13_light.py)


def shade_emission_bound(ev_max: float = SHADE_EV_MAX, clip: float = SHADE_EMISSION_CLIP,
                         channel_max: float = 1.0) -> float:
    """The largest shade radiance (W/(m²·sr)) that stays under the display clip at ``ev_max`` (pure): the shade's
    brightest channel (``channel_max``, 1.0 for the red of a 2700 K blackbody) times 2^ev_max must stay below
    ``clip``, so the bound is ``clip / 2^ev_max / channel_max`` (4.0 for the defaults)."""
    return float(clip) / (2.0 ** float(ev_max)) / max(float(channel_max), 1e-9)
RIG_WARM_K = 2700.0                   # a warm LED bulb; the style's colour_temperature_k wins when it is warmer
RIG_MOUNT_GAP_M = 0.03                # a ceiling fixture hangs this far under the ceiling
RIG_PENDANT_OVER_TABLE_M = 0.75       # the pendant shade's bottom above the table top
RIG_TABLE_TOP_M = 0.75
RIG_WALL_CABINET_BOTTOM_M = 1.45      # the kitchen wall cabinets' bottom (parametric wall_cabinet mount, M10)
RIG_STRIP_SETBACK_M = 0.30            # the under-cabinet strip this far in front of the wall (cabinet depth 0.35)
RIG_MIRROR_LIGHT_Z_M = 1.95           # the bathroom mirror light's centre above the floor
RIG_BEDSIDE_Z_M = 0.60                # a bedside lamp without a nightstand: its base above the floor
RIG_BEDSIDE_OFFSET_M = 0.35           # ... this far beside the bed's head corners
# Sources of the lumen values (real fixtures, the ranges typical of the product class): a 60 W-equivalent LED bulb
# is 800 lm, a 75 W-equivalent 1100 lm (the US FTC lumen labelling rule used by every bulb box: 800 lm ≈ 60 W,
# 1100 lm ≈ 75 W, 1600 lm ≈ 100 W); LED strips 400-600 lm per metre (product class); the manual's own table rows
# (800 / 1000 / 1500 / 2500 lm) anchor the conversion. Flagged as assumed in every manifest entry.
ROOM_RIGS: dict[str, list[dict]] = {
    # kind: pendant | ceiling | bedside | strip | mirror; anchor: the piece type the fixture needs (None = the room);
    # size_m: [w, d, h] of the visible fixture; lumens per fixture (a strip: per metre, length from the counter).
    "dining": [{"kind": "pendant", "anchor": "table_dining", "lumens": 2400.0, "count": 1, "size_m": [0.40, 0.40, 0.14],
                "source": "pendant with 3 x 800 lm LED bulbs"}],
    "living": [{"kind": "pendant", "anchor": "table_dining", "lumens": 2400.0, "count": 1, "size_m": [0.40, 0.40, 0.14],
                "source": "pendant with 3 x 800 lm LED bulbs over the dining table of an open living room",
                "optional": True}],
    "kitchen": [{"kind": "strip", "anchor": "kitchen_counter", "lumens_per_m": 500.0, "count": 1,
                 "size_m": [1.0, 0.02, 0.015], "source": "LED strip under the wall cabinets, 400-600 lm per metre"},
                {"kind": "ceiling", "anchor": None, "lumens": 1600.0, "count": 1, "size_m": [0.30, 0.30, 0.08],
                 "source": "ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb"}],
    "bedroom": [{"kind": "bedside", "anchor": "bed", "lumens": 470.0, "count": 2, "size_m": [0.24, 0.24, 0.42],
                 "source": "two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each"}],
    "bathroom": [{"kind": "mirror", "anchor": "washbasin", "lumens": 1100.0, "count": 1, "size_m": [0.60, 0.04, 0.04],
                  "source": "mirror light bar, 1100 lm (75 W-equivalent)"},
                 {"kind": "ceiling", "anchor": None, "lumens": 1100.0, "count": 1, "size_m": [0.26, 0.26, 0.08],
                  "source": "ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb"}],
    "wc": [{"kind": "mirror", "anchor": "washbasin", "lumens": 800.0, "count": 1, "size_m": [0.50, 0.04, 0.04],
            "source": "mirror light bar, 800 lm (60 W-equivalent)"},
           {"kind": "ceiling", "anchor": None, "lumens": 800.0, "count": 1, "size_m": [0.22, 0.22, 0.08],
            "source": "ceiling fixture with an 800 lm (60 W-equivalent) LED bulb"}],
    "hall": [{"kind": "ceiling", "anchor": None, "lumens": 1100.0, "count": 1, "size_m": [0.30, 0.30, 0.08],
              "source": "ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb, one per 3 m of a long hall"}],
    "stair": [{"kind": "ceiling", "anchor": None, "lumens": 1100.0, "count": 1, "size_m": [0.30, 0.30, 0.08],
               "source": "ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb"}],
}
RIG_KINDS = ("pendant", "ceiling", "bedside", "strip", "mirror")


def watts_for_lumens(lumens: float) -> float:
    """Radiant watts of a light of ``lumens`` (pure): ``LUMEN_WATT_TABLE`` read linearly between its rows, the last
    row's watts per lumen beyond it; 0 for 0 lm."""
    lm = max(0.0, float(lumens))
    rows = LUMEN_WATT_TABLE
    for (l0, w0), (l1, w1) in zip(rows, rows[1:]):
        if lm <= l1:
            return round(w0 + (w1 - w0) * (lm - l0) / (l1 - l0), 4)
    l1, w1 = rows[-1]
    return round(lm * w1 / l1, 4)


def rig_temperature_k(lighting: dict | None) -> float:
    """The fixtures' colour temperature (pure): the style's ``lighting.colour_temperature_k`` when it is warmer than
    ``RIG_WARM_K`` (a golden-evening style keeps its 3200 K sun but its lamps stay at 2700 K: min of the two)."""
    value = (lighting or {}).get("colour_temperature_k")
    try:
        k = float(value)
    except (TypeError, ValueError):
        return RIG_WARM_K
    return min(RIG_WARM_K, k) if k > 0 else RIG_WARM_K


def room_rig(room_type: str | None) -> list[dict]:
    """The light rig of a room type (pure, docs/milestone13.md §13.2): copies of the ``ROOM_RIGS`` fixtures with
    ``watts_radiometric`` (``watts_for_lumens``), ``watts_applied`` (x ``RIG_GAIN``) and their sources; ``[]`` for a
    type without a rig (storage, balcony, shaft, unknown ...: the Milestone 6 light rule stays)."""
    out = []
    for spec in ROOM_RIGS.get(str(room_type or ""), []):
        f = dict(spec)
        if "lumens" in f:
            f["watts_radiometric"] = watts_for_lumens(f["lumens"])
            f["watts_applied"] = round(f["watts_radiometric"] * RIG_GAIN, 4)
        f["gain"] = RIG_GAIN
        f["lumen_watt_source"] = LUMEN_WATT_SOURCE
        out.append(f)
    return out


def _piece_frame(piece: dict) -> tuple[tuple[float, float], tuple[float, float], float, float]:
    """``(centre, front unit vector, width across the front, depth)`` of a piece (pure; ``looks.piece_back_mid``
    convention: the front_deg points out of the front face, else the footprint's -Y side in its frame)."""
    fp = piece["footprint"]
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    rot = float(fp.get("rotation_deg") or 0.0)
    front = piece.get("front_deg")
    if front is None:
        front = rot - 90.0
    fx, fy = math.cos(math.radians(float(front))), math.sin(math.radians(float(front)))
    local = G.normalise_angle(float(front) - rot)
    w, d = float(fp["size"][0]), float(fp["size"][1])
    if min(abs(local - 270.0), abs(local - 90.0)) < 45.0:
        return (cx, cy), (fx, fy), w, d
    return (cx, cy), (fx, fy), d, w


def rig_plan(room: dict, pieces: list[dict], floor_z: float, ceil_z: float, holes=(),
             lighting: dict | None = None, agent_factor: float = 1.0) -> dict:
    """Where the fixtures of ``room_rig(room["room_type"])`` go (pure): ``{"fixtures": [...], "dropped": [...]}``.
    Each fixture: the ``room_rig`` record plus ``name``, ``center`` [x, y, z] (the visible fixture's centre),
    ``light`` {``type`` POINT | AREA, ``center``, ``size_m``, ``direction`` (an area light's -Z), ``energy_w``,
    ``radius_m``}, ``temperature_k``, ``anchor_id`` and ``reason``. ``pieces`` are the room's built pieces
    (``footprint``, ``type``, ``front_deg``); ``holes`` the stair openings of the level (ceiling fixtures stay out
    of them, as the Milestone 6 light does). A fixture whose anchor is missing is listed under ``dropped`` with the
    reason, except ``optional`` ones, which are silently left out."""
    polygon = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
        polygon = polygon[:-1]
    out: dict = {"fixtures": [], "dropped": []}
    if len(polygon) < 3:
        return out
    temperature = rig_temperature_k(lighting)
    by_type: dict[str, list[dict]] = {}
    for p in pieces:
        by_type.setdefault(str(p.get("type")), []).append(p)
    count = 0

    def add(spec: dict, centre, light_centre, light_type: str, energy: float, size, direction=None, anchor=None,
            radius: float = 0.05, reason: str = "") -> None:
        nonlocal count
        count += 1
        f = dict(spec)
        f.update(name=f"rig_{room['id']}_{spec['kind']}_{count}", center=[round(float(v), 4) for v in centre],
                 temperature_k=temperature, anchor_id=anchor, reason=reason,
                 light={"type": light_type, "center": [round(float(v), 4) for v in light_centre],
                        "size_m": [round(float(v), 4) for v in size], "energy_w": round(float(energy) * agent_factor, 4),
                        "radius_m": radius, "direction": [round(float(v), 4) for v in direction] if direction else None})
        out["fixtures"].append(f)

    for spec in room_rig(room.get("room_type")):
        kind = spec["kind"]
        if kind == "pendant":
            tables = by_type.get("table_dining") or []
            if not tables:
                if not spec.get("optional"):
                    out["dropped"].append({"kind": kind, "reason": f"no {spec['anchor']} in {room['id']}: no pendant"})
                continue
            table = max(tables, key=lambda p: float(p["footprint"]["size"][0]) * float(p["footprint"]["size"][1]))
            (cx, cy), _f, _w, _d = _piece_frame(table)
            h = float(spec["size_m"][2])
            z = floor_z + RIG_TABLE_TOP_M + RIG_PENDANT_OVER_TABLE_M + h / 2.0
            z = min(z, ceil_z - RIG_MOUNT_GAP_M - h / 2.0)
            add(spec, (cx, cy, z), (cx, cy, z - h * 0.2), "POINT", spec["watts_applied"], spec["size_m"],
                anchor=table["id"], radius=0.06, reason=f"pendant over the dining table {table['id']}")
        elif kind == "ceiling":
            plans = area_light_plans(polygon, holes=holes) if room.get("room_type") in ("hall", "stair") else \
                [area_light_plan(polygon, holes=holes)]
            h = float(spec["size_m"][2])
            for plan in plans:
                cx, cy = plan["center"]
                z = ceil_z - RIG_MOUNT_GAP_M - h / 2.0
                add(spec, (cx, cy, z), (cx, cy, z - h / 2.0 - 0.02), "POINT", spec["watts_applied"], spec["size_m"],
                    radius=0.08, reason=f"ceiling fixture at the pole of inaccessibility of {room['id']}")
        elif kind == "bedside":
            beds = (by_type.get("bed_double") or []) + (by_type.get("bed") or []) + (by_type.get("bed_single") or [])
            if not beds:
                out["dropped"].append({"kind": kind, "reason": f"no bed in {room['id']}: no bedside lamps"})
                continue
            bed = beds[0]
            (cx, cy), (fx, fy), width, depth = _piece_frame(bed)
            sx, sy = -fy, fx                                           # along the bed head
            hx, hy = cx - fx * depth / 2.0, cy - fy * depth / 2.0      # the head edge's midpoint
            nightstands = by_type.get("nightstand") or []
            h = float(spec["size_m"][2])
            for side in (-1.0, 1.0):
                corner = (hx + sx * side * width / 2.0, hy + sy * side * width / 2.0)
                stand = min(nightstands, key=lambda p: G.distance(p["footprint"]["center"][:2], corner),
                            default=None)
                if stand is not None and G.distance(stand["footprint"]["center"][:2], corner) <= 0.9:
                    from wenart.blender.parametric import piece_bbox
                    top = floor_z + float(piece_bbox(stand)[2])
                    px, py = float(stand["footprint"]["center"][0]), float(stand["footprint"]["center"][1])
                    anchor, why = stand["id"], f"bedside lamp on the nightstand {stand['id']}"
                else:
                    top = floor_z + RIG_BEDSIDE_Z_M
                    px, py = corner[0] + sx * side * RIG_BEDSIDE_OFFSET_M, corner[1] + sy * side * RIG_BEDSIDE_OFFSET_M
                    anchor, why = bed["id"], f"bedside lamp beside the head of the bed {bed['id']} (no nightstand)"
                if not G.point_in_polygon((px, py), polygon):
                    out["dropped"].append({"kind": kind, "reason": f"{why}: the lamp would stand outside the room"})
                    continue
                z = top + h / 2.0
                add(spec, (px, py, z), (px, py, top + h * 0.7), "POINT", spec["watts_applied"], spec["size_m"],
                    anchor=anchor, radius=0.05, reason=why)
        elif kind == "strip":
            counters = by_type.get("kitchen_counter") or []
            if not counters:
                out["dropped"].append({"kind": kind, "reason": f"no kitchen_counter in {room['id']}: no strip"})
                continue
            for counter in counters:
                (cx, cy), (fx, fy), width, depth = _piece_frame(counter)
                length = max(0.3, width - 0.1)
                bx, by = cx - fx * depth / 2.0, cy - fy * depth / 2.0            # the back edge (the wall)
                px, py = bx + fx * RIG_STRIP_SETBACK_M, by + fy * RIG_STRIP_SETBACK_M
                z = floor_z + RIG_WALL_CABINET_BOTTOM_M - float(spec["size_m"][2]) / 2.0
                if z <= floor_z + RIG_TABLE_TOP_M + 0.3:
                    z = floor_z + RIG_WALL_CABINET_BOTTOM_M
                lumens = float(spec["lumens_per_m"]) * length
                watts = round(watts_for_lumens(lumens) * RIG_GAIN, 4)
                f = dict(spec, lumens=round(lumens, 1), watts_radiometric=watts_for_lumens(lumens), watts_applied=watts,
                         length_m=round(length, 3), rotation_deg=round(math.degrees(math.atan2(fy, fx)) + 90.0, 3))
                add(f, (px, py, z), (px, py, z - 0.012), "AREA", watts, [length, 0.02, 0.015], direction=(0.0, 0.0, -1.0),
                    anchor=counter["id"], radius=0.0,
                    reason=f"LED strip under the wall cabinets along the counter {counter['id']}")
        elif kind == "mirror":
            basins = by_type.get("washbasin") or []
            if not basins:
                out["dropped"].append({"kind": kind, "reason": f"no washbasin in {room['id']}: no mirror light"})
                continue
            basin = basins[0]
            (cx, cy), (fx, fy), width, depth = _piece_frame(basin)
            bx, by = cx - fx * depth / 2.0, cy - fy * depth / 2.0
            px, py = bx + fx * 0.04, by + fy * 0.04                       # 4 cm off the wall behind the basin
            z = floor_z + RIG_MIRROR_LIGHT_Z_M
            z = min(z, ceil_z - 0.15)
            f = dict(spec, rotation_deg=round(math.degrees(math.atan2(fy, fx)) + 90.0, 3))
            add(f, (px, py, z), (px + fx * 0.03, py + fy * 0.03, z - 0.03), "AREA", spec["watts_applied"],
                [float(spec["size_m"][0]), 0.04, 0.04], direction=(fx * 0.7, fy * 0.7, -0.7), anchor=basin["id"],
                radius=0.0, reason=f"mirror light over the washbasin {basin['id']}")
    return out


def _fixture_mesh(fixture: dict) -> tuple[list, list]:
    """World-space vertices and faces of a visible fixture (pure, ``geom2d.box``): pendants and ceiling fixtures are
    8-sided drums, bedside lamps a drum shade over a thin stem, strips and mirror lights flat bars."""
    from wenart.blender import geom2d

    cx, cy, cz = fixture["center"]
    w, d, h = [float(v) for v in fixture.get("size_m") or (0.2, 0.2, 0.1)]
    kind = fixture["kind"]
    rot = float(fixture.get("rotation_deg") or 0.0)
    if kind in ("strip", "mirror"):
        size = (float(fixture.get("length_m") or w), d, h)
        return geom2d.box((cx, cy, cz), size, rot)
    r = max(w, d) / 2.0
    n = 8
    z0, z1 = cz - h / 2.0, cz + h / 2.0
    verts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    verts += [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n))[::-1])
    faces.append([n + i for i in range(n)])
    if kind == "bedside":                                             # a stem under the shade
        stem = geom2d.box((cx, cy, z0 - (h * 0.45)), (0.03, 0.03, h * 0.9), 0.0)
        verts2, faces2 = stem
        off = len(verts)
        verts += list(verts2)
        faces += [[off + i for i in f] for f in faces2]
    return verts, faces


def build_room_rig(bpy, common, collection, manifest_objects: list, assumed: list, room: dict, level: dict,
                   plan: dict, fixture_material) -> list:
    """The fixtures of ``rig_plan`` as objects: an emissive mesh (kind ``decor``, status ``assumed``, the camera sees
    it) and a POINT or AREA light inside (``use_temperature``, ``shadow_soft_size``, soft falloff where the light
    type has it: bpy.types.PointLight / SpotLight.use_soft_falloff). Returns the light objects."""
    from mathutils import Vector

    lights = []
    for f in plan["fixtures"]:
        verts, faces = _fixture_mesh(f)
        mat = fixture_material(f["temperature_k"])
        ob = common.new_mesh_object(f["name"], verts, faces, collection=collection, wenart_id=f["name"], kind="decor",
                                    status="assumed", materials=[mat])
        ob["wenart_room"] = room["id"]
        ob["wenart_rig"] = f["kind"]
        manifest_objects.append({
            "name": ob.name, "wenart_id": f["name"], "kind": "decor", "status": "assumed", "level_id": level["id"],
            "element_id": room["id"], "parent": room["id"], "evidence": [], "material": mat.name, "textured": False,
            "pass_index": None, "method": "rig", "type": f"rig_{f['kind']}", "rotation_deg": f.get("rotation_deg") or 0.0,
            "assumed": {"rig": f["kind"], "lumens": f.get("lumens"), "watts_radiometric": f.get("watts_radiometric"),
                        "watts_applied": f["light"]["energy_w"], "gain": f.get("gain"), "temperature_k": f["temperature_k"],
                        "anchor_id": f.get("anchor_id"), "reason": f["reason"], "source": f.get("source"),
                        "lumen_watt_source": f.get("lumen_watt_source"),
                        # round 3: the shade's own radiance, decoupled from the lamp power (never clips at EV <= +3)
                        "shade_emission_wm2sr": float(mat.get("wenart_light") or SHADE_EMISSION_WM2SR)},
        })
        spec = f["light"]
        light = bpy.data.lights.new(f"{f['name']}_light", spec["type"])
        light.energy = float(spec["energy_w"])
        if spec["type"] == "AREA":
            light.shape = "RECTANGLE"
            light.size, light.size_y = float(spec["size_m"][0]), float(spec["size_m"][1])
        else:
            light.shadow_soft_size = float(spec.get("radius_m") or 0.05)
        if hasattr(light, "use_soft_falloff"):
            light.use_soft_falloff = True
        try:
            light.use_temperature = True
            light.temperature = float(f["temperature_k"])
        except AttributeError:
            light.color = _blackbody_rgb(float(f["temperature_k"]))
        lob = bpy.data.objects.new(f"{f['name']}_light", light)
        lob.location = Vector(spec["center"])
        if spec.get("direction"):
            lob.rotation_euler = Vector(spec["direction"]).to_track_quat("-Z", "Y").to_euler()
        lob.visible_camera = False                      # the fixture mesh is what the camera sees
        collection.objects.link(lob)
        common.set_props(lob, wenart_id=lob.name, kind="light", status="assumed")
        lob["wenart_room"] = room["id"]
        lob["wenart_rig"] = f["kind"]      # round 3: render.py hides every rig object for the daylight white point
        manifest_objects.append({
            "name": lob.name, "wenart_id": lob.name, "kind": "light", "status": "assumed", "level_id": level["id"],
            "element_id": room["id"], "parent": room["id"], "evidence": [], "material": None, "textured": False,
            "pass_index": None, "center": spec["center"], "size": spec["size_m"],
            "assumed": {"power_w": spec["energy_w"], "rig": f["kind"], "fixture": f["name"], "temperature_k":
                        f["temperature_k"], "visible_camera": False, "reason": f["reason"], "lumens": f.get("lumens")},
        })
        assumed.append({"object": lob.name, "field": "rig_light", "value": spec["energy_w"],
                        "reason": f"{room['id']}: {f['reason']}; {f.get('lumens') or '?'} lm -> "
                                  f"{f.get('watts_radiometric')} W radiant x gain {f.get('gain')} "
                                  f"({f.get('source')}; the documents say nothing about lamps)",
                        "parent": room["id"], "kind": "rig_light"})
        lights.append(lob)
    for d in plan["dropped"]:
        assumed.append({"object": f"rig_{room['id']}", "field": f"rig_{d['kind']}", "value": None, "reason": d["reason"],
                        "parent": room["id"], "kind": "rig_dropped"})
    return lights


def build_lighting(building: dict, levels: list[dict], style: dict, hdri_path: str | None, collection,
                   manifest_objects: list, assumed: list, north_deg: float | None = None,
                   north_source: str | None = None, ceiling_at=None, exterior: bool = False) -> dict:
    """World + sun + area lights for the windowless rooms of ``levels``.

    Milestone 10: ``north_deg`` (the compass bearing of the building's +Y axis, ``site.north_deg``) turns
    the style's compass sun azimuth into the building frame (``building_azimuth``); ``ceiling_at(level,
    x, y)`` gives the ceiling height of a room under the roof (sloped), so its ceiling light hangs under it.

    Milestone 11 (docs/milestone11.md §1.1 E13): ``exterior`` (a build with exterior views) also makes the
    exterior world (``materials.exterior_world_nodes``: a physical sky whose sun is the lamp's), which render.py
    uses for the exterior cameras; the record is ``world_exterior``."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common
    from wenart.blender.materials import world_nodes

    scene = bpy.context.scene
    lighting = style.get("lighting") or {}
    elevation = float(lighting.get("sun_elevation_deg", 35.0))
    azimuth = float(lighting.get("sun_azimuth_deg", 210.0))
    # Milestone 13: the one constant (or the A/B variant's sun) times the mood factor of the style's sun_strength.
    levers = light_levers()
    strength, mood_factor = sun_strength_wm2(lighting, levers)
    temperature = float(lighting.get("colour_temperature_k", 5200))
    in_building = building_azimuth(azimuth, north_deg or 0.0)
    scene["wenart_light_variant"] = levers["variant"] or ""

    world = world_nodes(scene, world_lighting(lighting, in_building), hdri_path)
    world_exterior = None
    if exterior:
        from wenart.blender.materials import exterior_world_nodes
        # Milestone 13 round 3 (§14.3): a daytime sky whose sun disc only the camera sees (a Light Path 'Is Camera
        # Ray' mix of the sky with and without the disc), so the sun lamp below stays the one direct sun outdoors
        # (P1: the facades were flat and bluish at 3 W/m²; the lamp now carries SUN_STRENGTH_WM2 outside as well).
        world_exterior = exterior_world_nodes(scene, world_lighting(lighting, in_building), sun_disc=True,
                                              sun_elevation_deg=elevation, sun_azimuth_deg=in_building,
                                              sun_wm2=strength)

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = strength
    sun.angle = math.radians(0.53)
    try:
        sun.use_temperature = True
        sun.temperature = temperature
    except AttributeError:  # older API: fall back to a plain colour
        sun.color = _blackbody_rgb(temperature)
    ob = bpy.data.objects.new("sun", sun)
    d = Vector(sun_direction(elevation, in_building))
    ob.location = d * 30.0
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(ob)
    common.set_props(ob, wenart_id="sun", kind="light", status="assumed")
    manifest_objects.append({
        "name": "sun", "wenart_id": "sun", "kind": "light", "status": "assumed", "level_id": None,
        "element_id": None, "evidence": [], "material": None, "textured": False, "pass_index": None,
        "assumed": {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength,
                    "temperature_k": temperature, "strength_wm2_constant": SUN_STRENGTH_WM2,
                    "mood_factor": mood_factor, "variant": levers["variant"]},
    })
    if north_deg is not None:
        manifest_objects[-1]["assumed"].update(azimuth_building_deg=round(in_building, 3), north_deg=north_deg,
                                               north_source=north_source)

    portals = build_portals(building, levels, collection, manifest_objects)

    from wenart.blender.overrides import lighting_of
    from wenart.blender.shell import piece_built

    agent_lights = lighting_of(building)   # the agent's set_lighting (real03 follow-up)
    walls_by_id = {w["id"]: w for w in building.get("walls") or []}
    flagged = any(w.get("exterior") for w in walls_by_id.values())
    area_lights = []
    rig_lights = []
    rig_rooms: dict[str, dict] = {}
    fixture_cache: dict = {}

    def fixture_material(kelvin: float):
        from wenart.blender.materials import fixture_material as _fm
        key = round(float(kelvin))
        if key not in fixture_cache:
            # round 3: the shade's radiance is the fixed SHADE_EMISSION_WM2SR, not a function of the lamp power
            fixture_cache[key] = _fm(f"rig_fixture_{key}K", kelvin, SHADE_EMISSION_WM2SR)
        return fixture_cache[key]

    for level in levels:
        floor_z = float(level["elevation"])
        ceil_z = floor_z + float(level["ceiling_height"])
        levels_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
        voids = stair_openings(building, level)
        for room in building["rooms"]:
            if room["level_id"] != level["id"]:
                continue
            polygon = [tuple(p[:2]) for p in room["polygon"]]
            if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
                polygon = polygon[:-1]
            if len(polygon) < 3:
                continue
            windows = [o for o in room_openings(room, polygon, building) if o["type"] == "window"
                       and daylight_window(o, walls_by_id, flagged)]
            area = G.polygon_area(polygon)
            ratio = window_floor_ratio(windows, level, levels_above, area) if windows else None
            why = fill_light_reason(windows, ratio, sun_wm2=strength)
            agent = agent_lights.get(room["id"])
            factor = float(agent["factor"]) if agent else 1.0
            # Milestone 13: the room's light rig (visible fixtures) where its type has one.
            if levers["rig"] and room_rig(room.get("room_type")):
                room_floor = floor_z + float(room.get("floor_offset_m") or 0.0)
                room_ceil = ceil_z if ceiling_at is None else min(ceil_z, float(ceiling_at(level, *G.polygon_centroid(polygon))))
                pieces = [p for p in building.get("furniture") or [] if p.get("room_id") == room["id"]
                          and p.get("kind") != "decor" and piece_built(p) and p.get("footprint")]
                plan = rig_plan(room, pieces, room_floor, room_ceil, holes=voids, lighting=lighting, agent_factor=factor)
                built = build_room_rig(bpy, common, collection, manifest_objects, assumed, room, level, plan,
                                       fixture_material)
                rig_lights.extend(built)
                rig_rooms[room["id"]] = {"fixtures": [f["name"] for f in plan["fixtures"]],
                                         "dropped": plan["dropped"], "replaces_fill_light": why is not None and bool(built),
                                         "fill_light_reason": why}
                if built and why is not None:
                    assumed.append({"object": f"rig_{room['id']}", "field": "area_light", "value": None,
                                    "reason": f"{room['id']}: {why}; the room's light rig ({len(built)} fixtures) "
                                              f"carries the light instead of the invisible ceiling light",
                                    "parent": room["id"], "kind": "rig_replaces_fill_light"})
                    continue
            if why is None and agent is None:
                continue
            if why is None:
                why = f"agent: {agent.get('reason') or 'room lights'}"
            dim = bool(windows)
            plans = area_light_plans(polygon, holes=voids)
            power, per_m2 = light_power(area, len(plans), dim, factor)
            for k, plan in enumerate(plans):
                name = f"light_{room['id']}" if k == 0 else f"light_{room['id']}_{k + 1}"
                area_lights.append(_room_light(bpy, common, collection, manifest_objects, assumed, room, level, plan,
                                               name, power, per_m2, why, dim, ratio, temperature, ceiling_at, ceil_z,
                                               len(plans), agent))
    sun_info = {"elevation_deg": elevation, "azimuth_deg": azimuth, "strength": strength, "temperature_k": temperature,
                "strength_wm2_constant": SUN_STRENGTH_WM2, "mood_factor": mood_factor,
                "mood_sun_strength": lighting.get("sun_strength"), "variant": levers["variant"],
                "manual_clear_sky_wm2": 1000.0}
    if north_deg is not None:
        sun_info.update(azimuth_building_deg=round(in_building, 3), north_deg=north_deg, north_source=north_source)
    if lighting.get("sun_source"):
        sun_info["source"] = lighting["sun_source"]
    return {"world": world, "world_exterior": world_exterior, "sun": sun_info,
            "area_lights": [o.name for o in area_lights], "portals": [o.name for o in portals],
            # Milestone 13 (docs/milestone13.md §13.3): the variant and every lever, the rig per room
            "variant": levers["variant"], "levers": {k: levers[k] for k in ("sun_wm2", "ev_cap", "rig", "shell", "source")},
            "rig": {"on": bool(levers["rig"]), "gain": RIG_GAIN, "temperature_k": rig_temperature_k(lighting),
                    "shade_emission_wm2sr": SHADE_EMISSION_WM2SR, "shade_emission_bound": shade_emission_bound(),
                    "lumen_watt_source": LUMEN_WATT_SOURCE, "lights": [o.name for o in rig_lights], "rooms": rig_rooms},
            "fill_light": {"dim_room_ratio": DIM_ROOM_RATIO, "sun_scaled_by": round(strength / SUN_REFERENCE_MOOD_WM2, 6)}}



def _room_light(bpy, common, collection, manifest_objects: list, assumed: list, room: dict, level: dict, plan: dict,
                name: str, power: float, per_m2: float, why: str, dim: bool, ratio, temperature: float, ceiling_at,
                ceil_z: float, count: int, agent):
    """One square ceiling light of a room (``build_lighting``)."""
    size = plan["size"]
    light = bpy.data.lights.new(name, "AREA")
    light.shape = "SQUARE"
    light.size = size
    light.energy = power
    try:
        light.use_temperature = True
        light.temperature = temperature
    except AttributeError:
        light.color = _blackbody_rgb(temperature)
    lob = bpy.data.objects.new(name, light)
    # The room's own ceiling at the light (review #28: a sloped ceiling of one room never carries over to
    # the next room of the level).
    room_ceil = ceil_z if ceiling_at is None else light_ceiling(ceiling_at, level, plan["center"], size, ceil_z)
    lob.location = (plan["center"][0], plan["center"][1], room_ceil - AREA_LIGHT_CEILING_GAP)
    lob.visible_camera = False      # lighting mood only: no lamp in the picture
    collection.objects.link(lob)
    common.set_props(lob, wenart_id=name, kind="light", status="assumed")
    lob["wenart_room"] = room["id"]
    kind = "dim_room_light" if dim else "windowless_room_light"
    manifest_objects.append({
        "name": lob.name, "wenart_id": lob.name, "kind": "light", "status": "assumed",
        "level_id": level["id"], "element_id": room["id"], "parent": room["id"], "evidence": [],
        "material": None, "textured": False, "pass_index": None,
        "center": [plan["center"][0], plan["center"][1], round(room_ceil - AREA_LIGHT_CEILING_GAP, 4)],
        "size": size,
        "assumed": {"power_w": power, "w_per_m2": per_m2, "size_m": size,
                    "boundary_distance_m": plan["boundary_distance"], "window_floor_ratio":
                        None if ratio is None else round(ratio, 4), "visible_camera": False, "reason": why,
                    "lights_in_room": count, "agent_factor": agent["factor"] if agent else None},
    })
    assumed.append({"object": lob.name, "field": "area_light", "value": power,
                    "reason": f"{room['id']}: {why}; soft ceiling light added (lighting mood, invisible "
                              f"to the camera)",
                    "parent": room["id"], "kind": kind})
    return lob


def build_portals(building: dict, levels: list[dict], collection, manifest_objects: list) -> list:
    """One portal AREA light per window of ``levels`` (see ``portal_plan``)."""
    import bpy
    from mathutils import Vector

    from wenart.blender import common

    created = []
    for level in levels:
        floor_z = float(level["elevation"])
        levels_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
        walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level["id"]}
        rooms = [r for r in building["rooms"] if r["level_id"] == level["id"]]
        for opening in building["openings"]:
            if opening["level_id"] != level["id"] or opening["type"] != "window":
                continue
            wall = walls.get(opening.get("wall_id"))
            if wall is None:
                continue  # build_openings already warned: no window object either
            plan = portal_plan(opening, wall, level, levels_above, rooms)
            name = f"portal_{opening['id']}"
            light = bpy.data.lights.new(name, "AREA")
            light.shape = "RECTANGLE"
            light.size, light.size_y = plan["size"]
            light.cycles.is_portal = True
            ob = bpy.data.objects.new(name, light)
            ob.location = Vector(plan["center"])
            # Local -Z (the light direction) into the room, local Y up: size along the wall, size_y vertical.
            ob.rotation_euler = Vector((plan["inward"][0], plan["inward"][1], 0.0)).to_track_quat("-Z", "Y").to_euler()
            collection.objects.link(ob)
            common.set_props(ob, wenart_id=name, kind="light", status="assumed")
            ob["wenart_opening"] = opening["id"]
            ob["wenart_room"] = plan["room_id"] or ""
            assumed = {"reason": "portal", "size_m": [round(v, 4) for v in plan["size"]], "faces_room": plan["room_id"]}
            if plan["note"]:
                assumed["note"] = plan["note"]
            manifest_objects.append({
                "name": name, "wenart_id": name, "kind": "light", "status": "assumed", "level_id": level["id"],
                "element_id": opening["id"], "evidence": [], "material": None, "textured": False, "pass_index": None,
                "reason": "portal", "center": [round(v, 4) for v in plan["center"]],
                "size": [round(v, 4) for v in plan["size"]], "inward": [round(v, 4) for v in plan["inward"]],
                "assumed": assumed,
            })
            created.append(ob)
    return created


def _blackbody_rgb(kelvin: float) -> tuple[float, float, float]:
    """Rough blackbody colour (only used when the lamp has no temperature input)."""
    t = kelvin / 100.0
    r = 1.0 if t <= 66 else min(1.0, 1.2929 * (t - 60) ** -0.1332)
    g = min(1.0, 0.3900 * math.log(t) - 0.6318) if t <= 66 else min(1.0, 1.1299 * (t - 60) ** -0.0755)
    b = 1.0 if t >= 66 else (0.0 if t <= 19 else min(1.0, 0.5432 * math.log(t - 10) - 1.1963))
    return (max(0.0, r), max(0.0, g), max(0.0, b))
