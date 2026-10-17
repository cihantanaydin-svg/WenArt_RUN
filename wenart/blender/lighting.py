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

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8; pod P3 rendered real04 with 13 ``lighting_dark``
views):

- A rig replaces the fill light only when it has a ceiling fixture (``rig_replaces_fill``). The windowless bedroom
  r_L0_yatak_odasi_4 got two 470 lm bedside lamps in place of the 150 W fill light and rendered night-dark (+6.1..+6.5
  EV wanted, beyond set_lighting's x3); a rig of bedside lamps or a pendant now adds to the Milestone 6 fill light
  (assumed kind ``rig_adds_to_fill_light``; the lighting block's ``rig.rooms[...].adds_to_fill_light``). Rooms with
  a window are unchanged; real04's L0 yatak_odasi_3/4 and L-1b oda / oda_2 and real02's L0 yatak_odasi_3/4 get the
  fill light back (M12 lit yatak_odasi_4 at -0.17 EV with it).
- The hall and stair ceiling fixtures carry bulbs for ``RIG_CIRCULATION_LUMENS_PER_M2`` (``rig_bulbs``): P3's halls
  had a fifth of the baths' rig power per m² and stayed +3.0..+3.6 EV after the agent's x3 (the constant's comment
  has the numbers). Each fixture records ``bulbs``, ``lumens_per_bulb`` and the fixture's lumens and watts.
- ``RIG_GAIN``, ``RIG_WARM_K``, the other rigs and the walls' ``exterior`` flags are unchanged (the P1 decisions of
  §14.3); render.py corrects the rig's colour per view (``render.mixed_whitepoint``).

Fix round after P4a (17 Oct 2026; pod P4a rendered real02 with the Milestone 11 cameras replayed, look review):

- Bedside lamps never float. P4a: with no nightstand the lamp stood 0.35 m beside the bed head with its base at
  0.60 m and its stem ending 22 cm above the floor (r_L0_yatak_odasi, _3), half inside the head wall; in
  e_yatak_odasi / _2 it stood inside the AI's floor lamps f_L0_031..034. ``rig_plan`` now picks a host per side, in
  this order: (1) a lamp already there (a ``floor_lamp`` / ``table_lamp`` piece, or a built table or floor lamp of the
  decor) within ``RIG_BEDSIDE_HOST_M`` of the head corner: the rig light goes into its shade, no rig mesh
  (``mesh: False``, ``anchor_id`` the lamp; a lamp on a nightstand comes first, so the rig never puts a second lamp
  on it); (2) a nightstand within ``RIG_BEDSIDE_HOST_M``: the lamp stands on its top (stem from the top, shade
  above it); (3) a head edge on the room boundary (its midpoint within ``RIG_HEAD_WALL_M`` of a room edge): a wall
  sconce (``mount: "wall"``, ``RIG_SCONCE_SIZE_M``, centre at ``RIG_SCONCE_Z_M``, ``RIG_SCONCE_BEYOND_M`` beyond the
  corner, back ``RIG_SCONCE_WALL_GAP_M`` off the wall, no stem), unless it would cover a door or window, run past
  the end of the wall, hit a piece or decor or reach the ceiling; (4) else no lamp, with the reason. The floating
  path (``RIG_BEDSIDE_Z_M``) is gone. Names (``rig_<room>_bedside_N``) and anchors stay.
- The mirror light sits above whatever hangs on the wall behind the basin: the basin's own built top (a vanity
  module with its mirror) and every built wall decor (mirror, wall art, clock) whose plan box comes within
  ``RIG_WALL_ITEM_REACH_M`` of the bar's, ``RIG_MIRROR_LIGHT_GAP_M`` above their top; when that leaves less than
  ``RIG_MIRROR_CEILING_CLEAR_M`` under the ceiling the bar is dropped with the reason (P4a: the bar at 1.95 m ran
  across the diamond mirror dec_L1_010 of r_L1_banyo and the top of dec_L0_017 in r_L0_banyo_2).
- A pendant or ceiling fixture whose spot is under a built decor light (``pendant_light`` / ``ceiling_light`` of
  the decor stage) uses that light as its host: no second fixture mesh in the same place (P4a: the rig drum of
  r_L-1_salon at the decor pendant dec_L-1_002, the bathroom rig fixtures at the decor ceiling lights).
- Ceiling fixtures and pendants hang under the ceiling at their own spot (``ceiling_fn``, the sloped ceiling of
  ``build_lighting``'s ``ceiling_at``), not at the room's centroid.
- Every rig shade is ``visible_shadow = False``. The point light of a pendant and of a bedside lamp sits inside its
  closed drum; an Emission-only surface blocks shadow rays, so that light never left the drum (bpy 5.2.2 CPU
  Cycles, 17 Oct 2026: the floor under a closed drum metered the same with the 5 W light on or off, 0.263; +43 %
  with the shade's shadow off, 0.377). The shade is what the camera sees; the light inside now lights the room.
- ``rig_fixture_problems`` (pure) checks every fixture with a mesh: inside the room, no 3D overlap with a piece or a
  built decor item other than its anchor and host, a table lamp's base on its nightstand top (within 0.01 m), a
  sconce's back on a wall face and its bottom above ``RIG_BEDSIDE_MIN_WALL_Z_M``. ``rig_plan`` drops a fixture that
  fails it, with the reason. The manifest records each fixture's box (``center``, ``size``, ``rotation_deg``),
  ``mount``, ``mesh`` and ``host_id``, so a scene check can run the same rule on the built scene.

Fix round after P4b (17 Oct 2026; the review of the P4a fix round and the P4b look review of real03):

- Built decor is keyed by its own id (``decor_own_id``: ``decor_id``, never the host's id that furniture.py writes in
  ``element_id`` / ``wenart_id`` of hosted decor). The P4a round keyed a plant on a nightstand by the nightstand, so
  ``rig_fixture_problems`` skipped it with the nightstand and the rig lamp stood through it unflagged (P3 real04
  r_L0_yatak_odasi / _2: the plants dec_L0_010 and dec_L0_046 on f_L0_050 and f_L0_054); a hosted light named the
  nightstand as its lamp (f_L0_055 for dec_L0_045). Now a table lamp on a nightstand takes a free spot of the top
  (``_stand_spot``) or the side falls through to the wall sconce, else no lamp, with the reason naming the item; the
  nightstand top comes from the piece box only.
- A hosted light reaches the room: under a decor pendant (``RIG_HOSTED_PENDANT_GAP_M``; P4a real02
  rig_r_L-1_salon_2_pendant_1 sat in the closed bulb of abo_B07HKCRWJH and the floor metered the same with it on or
  off), under the shade of a lamp that is no library model (``RIG_HOST_LAMP_BELOW_SHADE_M``, as
  ``furniture.lamp_light_point``: the parametric shades are closed solids), in the shade of a library lamp only; when
  the scene is built, rays check every hosted light against its host's object and step it down out of a closed
  shade or bulb (``light_escapes``, ``free_light_point``; recorded per light as ``escape``, an enclosed light as
  ``rig_light_enclosed``), so each library model is checked, not only the two ABO lamps measured for P4a.
- Fixtures have hardware (the verifier's better fix of the P4b finding "rig fixtures read as primitives": all 6
  pendants of real03's living rooms hung as cordless drums about 1 m under the ceiling, and the bedside stems
  glowed in the nightstands' open shelves): a pendant's cord and canopy up to its ``mount_z`` (the ceiling over it),
  a ceiling fixture's canopy, a table lamp's base disc and stem, all in a non-emissive dark metal
  (``hardware_material``, slot 1; the shade stays the emissive slot 0). ``rig_fixture_problems`` checks a pendant's
  cord like its shade.
- Integration of this round (the verifier's better fix of the P4b interior-glazing finding; render.py's
  ``room_rig_kelvin`` is the render side): the halls, stairs, bathrooms and WCs get a neutral rig of ``RIG_NEUTRAL_K``
  (4000 K, as in offices and apartment blocks), the bedside, living, dining and kitchen rigs stay at
  ``rig_temperature_k`` (2700 K; the kitchen staying warm is a look decision), per room in ``rig_plan``
  (``rig_temperature_for``). The evening rule stays: a style warmer than 2700 K keeps every rig at
  min(style K, 2700). Why: a 2700 K hall seen through interior glazing from a daylight room read amber (R/B 1.8-2.15
  on real03), and no per-view white balance removes two white points in one frame. The manifest's ``lighting.rig``
  block adds ``temperature_k_by_type``.
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
    and their edges as boundary. Fix round after P4a (17 Oct 2026): inside means
    inside the polygon and in no hole. The Mapbox even-odd rule over all rings
    counted a point in a hole beyond the polygon as inside: ``build_lighting``
    passes every stair opening of the level, the search cells reach one cell past
    the room's box, and real02's r_L0_merdiven got its ceiling fixture at
    (8.40, 8.24), in the other stair's opening of r_L0_merdiven_2 (P4a)."""
    best = math.inf
    rings_inside = []
    for ring in (polygon, *holes):
        inside = False
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
        rings_inside.append(inside)
    d = math.sqrt(best)
    return d if rings_inside[0] and not any(rings_inside[1:]) else -d


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
# Integration of the fix round after P4b (module docstring): the neutral rig of the circulation and wet rooms.
RIG_NEUTRAL_K = 4000.0
RIG_NEUTRAL_TYPES = ("hall", "stair", "bathroom", "wc")
RIG_MOUNT_GAP_M = 0.03                # a ceiling fixture hangs this far under the ceiling
RIG_PENDANT_OVER_TABLE_M = 0.75       # the pendant shade's bottom above the table top
RIG_TABLE_TOP_M = 0.75
RIG_WALL_CABINET_BOTTOM_M = 1.45      # the kitchen wall cabinets' bottom (parametric wall_cabinet mount, M10)
RIG_STRIP_SETBACK_M = 0.30            # the under-cabinet strip this far in front of the wall (cabinet depth 0.35)
RIG_MIRROR_LIGHT_Z_M = 1.95           # the bathroom mirror light's centre above the floor (nothing under it)
# Fix round after P4a (17 Oct 2026): the mirror light goes above the wall items behind the basin ...
RIG_MIRROR_LIGHT_GAP_M = 0.05         # its bottom this far above the top of the mirror, art or vanity under it
RIG_MIRROR_CEILING_CLEAR_M = 0.13     # its top at least this far under the ceiling (the old 0.15 m centre cap)
RIG_WALL_ITEM_REACH_M = 0.10          # wall decor whose plan box comes this close to the bar's hangs under it
RIG_WALL_DECOR_TYPES = ("mirror", "wall_art", "clock")
# ... a bedside lamp has a host: a lamp already there, a nightstand, or the head wall (a sconce), never the air.
RIG_BEDSIDE_HOST_M = 0.9              # a lamp or nightstand within this of the bed's head corner hosts the lamp
RIG_HOST_LAMP_TYPES = ("floor_lamp", "table_lamp")
RIG_HOST_LAMP_SHADE_M = 0.15          # a hosted light this far under the host lamp's top (in its shade) ...
RIG_HOST_LAMP_SHADE_SHARE = 0.25      # ... at most this share of the lamp's height
RIG_STAND_STEM_SHARE = 0.4            # a rig table lamp: the stem is the lower 40 % of its height, the shade the rest
RIG_HEAD_WALL_M = 0.10                # the bed head's midpoint within this of a room edge: that edge is the head wall
RIG_HEAD_WALL_PARALLEL_DEG = 10.0     # ... and the edge runs along the head within this angle
RIG_SCONCE_SIZE_M = (0.12, 0.12, 0.20)  # a bedside wall sconce: a drum shade 12 cm across and 20 cm tall
RIG_SCONCE_Z_M = 1.15                 # its centre above the floor (bottom 1.05 m: above a mattress and a nightstand)
RIG_SCONCE_BEYOND_M = 0.20            # its centre this far beyond the bed's head corner, along the head wall
RIG_SCONCE_WALL_GAP_M = 0.005         # its back this far off the wall face
RIG_SCONCE_END_MARGIN_M = 0.02        # it stays this far inside the ends of its wall edge
RIG_SCONCE_LIGHT_FRONT_M = 0.03       # its light this far in front of the shade (outside the shell)
RIG_SCONCE_CEILING_CLEAR_M = 0.10     # its top at least this far under the ceiling
RIG_OPENING_MARGIN_M = 0.05           # a sconce stays this far off a door or window of its wall
RIG_OPENING_WALL_M = 0.35             # an opening whose centre is this close to the head-wall line is on that wall
RIG_BEDSIDE_MIN_WALL_Z_M = 0.9        # a bedside fixture not on a nightstand has its bottom above this
RIG_DECOR_HOST_TYPES = ("pendant_light", "ceiling_light")   # built decor lights that host a pendant or ceiling fixture
RIG_HOSTED_CEILING_GAP_M = 0.02       # a hosted ceiling light this far under its decor fixture
# Fix round after P4b (17 Oct 2026): a hosted pendant light hangs this far under the decor pendant's bottom, as the
# ceiling light does. The old spot (bottom + min(0.12, 0.3 h)) lay inside the model: P4a's dec_L-1_017
# (abo_B07HKCRWJH) has a closed bulb mesh 0.064-0.164 m above its bottom, and the parametric pendant's shade is a closed
# frustum from 0 to 0.3 m; bpy 5.2.2 CPU Cycles, the real GLB at 1:1, 30 W: the floor metered 0.19815 with the light
# on and off, 0.522 with it 5 cm under the model (the review of the P4a fix round).
RIG_HOSTED_PENDANT_GAP_M = 0.03
RIG_HOSTED_MIN_Z_M = 1.2              # a hosted light lower than this above the floor has no host (a pendant
                                      # through a table)
# Fix round after P4b: a light hosted in a lamp that is not a library model (a parametric floor or table lamp, whose
# shade is a closed solid) sits this far under the shade's lowest point (= furniture.lamp_light_point's below_shade);
# only a library lamp keeps the in-shade spot (RIG_HOST_LAMP_SHADE_M), checked per model when the scene is built
# (light_escapes: P4a measured B07HKC3S4T and B075X2NLK5 letting the light out; every other model is checked by rays).
RIG_HOST_LAMP_BELOW_SHADE_M = 0.05
RIG_ESCAPE_STEP_M = 0.05              # a hosted light enclosed by its host goes this far under the host's surface
                                      # straight below it (the bottom of the closed shade or bulb) ...
RIG_ESCAPE_LOW_SHARE = 0.25           # ... never below this share of the host lamp's height above its bottom
RIG_STAND_EDGE_M = 0.01               # a rig table lamp stays this far inside the edge of its nightstand's top
# The fixture hardware (fix round after P4b, the verifier's better fix of the P4b look finding): not emissive, so a
# cord, a canopy, a stem or a base never glows. A pendant hangs from a canopy on the ceiling by a cord; a ceiling
# fixture has a canopy that fills its gap to the ceiling; a table lamp has a base disc on the nightstand and a stem.
RIG_CORD_M = 0.006                    # the pendant cord's width
RIG_CORD_MIN_M = 0.01                 # a shorter cord is left out (the canopy reaches down to the shade instead)
RIG_CANOPY_R_M = 0.05                 # the ceiling canopy: an 8-sided disc of this radius ...
RIG_CANOPY_H_M = 0.025                # ... and this height, its top on the ceiling
RIG_STAND_BASE_R_M = 0.05             # a table lamp's base disc (0.10 m across) ...
RIG_STAND_BASE_H_M = 0.015            # ... this tall, on the nightstand top
RIG_STEM_M = 0.03                     # a table lamp's stem
RIG_HARDWARE_RGB = (0.05, 0.04, 0.03)  # dark bronze ...
RIG_HARDWARE_METALLIC = 0.8           # ... metal
RIG_HARDWARE_ROUGHNESS = 0.4
RIG_COLLISION_TOL_M = 0.005           # boxes that overlap by less than this do not collide (touching is fine)
# Pieces whose box is not their shape: a rug lies on the floor; a stair's box rises to the next floor over the whole
# flight, while a ceiling fixture at the pole stays out of its opening (the holes of polylabel), over the low steps.
RIG_COLLISION_SKIP_TYPES = ("rug", "stair")
RIG_STAND_TOL_M = 0.01                # a table lamp's base within this of its nightstand top
# Sources of the lumen values (real fixtures, the ranges typical of the product class): a 60 W-equivalent LED bulb
# is 800 lm, a 75 W-equivalent 1100 lm (the US FTC lumen labelling rule used by every bulb box: 800 lm ≈ 60 W,
# 1100 lm ≈ 75 W, 1600 lm ≈ 100 W); LED strips 400-600 lm per metre (product class); the manual's own table rows
# (800 / 1000 / 1500 / 2500 lm) anchor the conversion. Flagged as assumed in every manifest entry.
# Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8). What: the hall and stair ceiling fixtures carry as
# many 1100 lm bulbs as give RIG_CIRCULATION_LUMENS_PER_M2 over the room's floor (the spec's ``lumens_per_m2``;
# ``rig_bulbs``). Why: P3's halls had one 1100 lm fixture for 11.9-15.3 m² (72-92 lm/m², 0.4-0.5 W/m² applied) where
# the windowless baths had two for 5 m² (440 lm/m², 2.5 W/m²): the baths metered +1.5..+2.0 EV, the halls +3.0..+3.6
# EV even after the agent's set_lighting x2.8-x3.0 (10 lighting_dark views; without the agent +4.6..+5.1). Per
# applied W/m² the halls metered 0.05-0.09 incident against the baths' 0.07-0.13, so the bath's density brings P3's
# L-1 and L1 halls to about +1.8..+2.8 EV before any agent edit (the L0 hall, metered on its shaded stair side at
# 0.016 per W/m², stays over the cap: a finding for set_lighting). More bulbs, not more lumens per bulb: the manual's
# table gives a 2500 lm tube only 4.5 W against 3.1 W for 1100 lm, so a brighter bulb would add little light. The
# bathroom, wc, kitchen, bedroom and dining rigs keep their lumens (P3: the baths and kitchens metered within the
# cap).
RIG_CIRCULATION_LUMENS_PER_M2 = 450.0
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
              "lumens_per_m2": RIG_CIRCULATION_LUMENS_PER_M2,
              "source": "ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, "
                        "bulbs for 450 lm per m2 of floor"}],
    "stair": [{"kind": "ceiling", "anchor": None, "lumens": 1100.0, "count": 1, "size_m": [0.30, 0.30, 0.08],
               "lumens_per_m2": RIG_CIRCULATION_LUMENS_PER_M2,
               "source": "ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor"}],
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


def rig_temperature_for(room_type: str | None, lighting: dict | None) -> float:
    """The rig's colour temperature in a room of ``room_type`` (pure; integration of the fix round after P4b, module
    docstring): ``RIG_NEUTRAL_K`` for ``RIG_NEUTRAL_TYPES``, ``rig_temperature_k`` for every other type; with a style
    warmer than ``RIG_WARM_K`` (the evening rule) every rig keeps ``rig_temperature_k``."""
    k = rig_temperature_k(lighting)
    if k < RIG_WARM_K - 1e-9:
        return k
    return RIG_NEUTRAL_K if str(room_type or "") in RIG_NEUTRAL_TYPES else k


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


def rig_bulbs(spec: dict, floor_area_m2: float, fixtures: int) -> int:
    """How many bulbs of ``spec["lumens"]`` each of ``fixtures`` ceiling fixtures carries (pure; fix round after P3,
    16-17 Oct 2026): ``ceil(area x lumens_per_m2 / (fixtures x lumens))`` for a spec with ``lumens_per_m2`` (the hall
    and stair rigs: ``RIG_CIRCULATION_LUMENS_PER_M2``), at least 1; 1 for every other spec."""
    density = spec.get("lumens_per_m2")
    lumens = float(spec.get("lumens") or 0.0)
    if not density or lumens <= 0.0 or int(fixtures) < 1:
        return 1
    return max(1, math.ceil(float(floor_area_m2) * float(density) / (int(fixtures) * lumens) - 1e-9))


def rig_replaces_fill(plan: dict, why: str | None) -> bool:
    """Whether a room's rig replaces the Milestone 6 fill light (pure; fix round after P3, 16-17 Oct 2026, verifier of
    the P3 look review). What: only a room that needs the fill light (``why``: no window, or little daylight) and
    whose rig has a ceiling fixture. Why: P3's windowless bedroom r_L0_yatak_odasi_4 got only its two 470 lm bedside
    lamps (4.9 W) in place of the 150 W fill light and rendered night-dark (+6.1..+6.5 EV wanted, x9-x11 the light the
    cap allows, beyond set_lighting's x3); M12 lit it with the fill light at -0.17 EV. How: a rig without a ceiling
    fixture (bedside lamps, a dining pendant) adds to the fill light instead (``build_lighting`` records
    ``rig_adds_to_fill_light``); halls, stairs, kitchens, baths and WCs have a ceiling fixture and keep the round-3
    rule."""
    return why is not None and any(f.get("kind") == "ceiling" for f in plan.get("fixtures") or [])


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


# --------------------------------------------------------------------------
# Fix round after P4a (17 Oct 2026): hosts, boxes and the fixture check (pure)
# --------------------------------------------------------------------------

def _convex_overlap(p, q, tol: float = 0.0) -> bool:
    """Whether two convex polygons overlap by more than ``tol`` on every separating axis (pure; the separating axis
    test, no shapely: this module runs in Blender's Python)."""
    for poly in (p, q):
        n = len(poly)
        for i in range(n):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % n]
            nx, ny = -(by - ay), bx - ax
            ln = math.hypot(nx, ny)
            if ln < 1e-12:
                continue
            nx, ny = nx / ln, ny / ln
            pp = [x * nx + y * ny for x, y in p]
            qq = [x * nx + y * ny for x, y in q]
            if max(pp) <= min(qq) + tol or max(qq) <= min(pp) + tol:
                return False
    return True


def boxes_collide(a: dict, b: dict, tol: float = RIG_COLLISION_TOL_M) -> bool:
    """Whether two boxes ``{"center": [x, y, z_mid], "size": [w, d, h], "rotation_deg"}`` overlap in 3D by more than
    ``tol`` (pure): their height ranges and their rotated plan rectangles."""
    az, ah = float(a["center"][2]), float(a["size"][2])
    bz, bh = float(b["center"][2]), float(b["size"][2])
    if az + ah / 2.0 <= bz - bh / 2.0 + tol or bz + bh / 2.0 <= az - ah / 2.0 + tol:
        return False
    pa = G.rotated_rectangle(a["center"][:2], a["size"][:2], float(a.get("rotation_deg") or 0.0))
    pb = G.rotated_rectangle(b["center"][:2], b["size"][:2], float(b.get("rotation_deg") or 0.0))
    return _convex_overlap(pa, pb, tol)


def piece_box(piece: dict, floor_z: float) -> dict:
    """The built box of a piece (pure): its footprint from the floor up to ``parametric.piece_bbox``'s height (the
    fitted library box, the module plan or the parametric family)."""
    from wenart.blender.parametric import piece_bbox

    fp = piece["footprint"]
    h = float(piece_bbox(piece)[2])
    return {"id": piece.get("id"), "type": piece.get("type"), "center": [float(fp["center"][0]),
            float(fp["center"][1]), float(floor_z) + h / 2.0], "size": [float(fp["size"][0]), float(fp["size"][1]), h],
            "rotation_deg": float(fp.get("rotation_deg") or 0.0)}


def fixture_box(fixture: dict) -> dict:
    """The box a rig fixture's mesh fills (pure): its ``center`` and ``size_m`` (a strip's ``length_m``), turned by
    ``rotation_deg``."""
    w, d, h = (float(v) for v in fixture.get("size_m") or (0.2, 0.2, 0.1))
    if fixture.get("length_m"):
        w = float(fixture["length_m"])
    return {"center": [float(v) for v in fixture["center"]], "size": [w, d, h],
            "rotation_deg": float(fixture.get("rotation_deg") or 0.0)}


def pendant_cord_box(fixture: dict) -> dict | None:
    """The box of a pendant's cord and canopy (pure; fix round after P4b): ``RIG_CORD_M`` wide, from the shade's top up
    to the fixture's ``mount_z`` (the ceiling over it); None for another kind, a fixture without a mesh or a mount, or
    a cord shorter than ``RIG_CORD_MIN_M``."""
    if fixture.get("kind") != "pendant" or fixture.get("mesh") is False or fixture.get("mount_z") is None:
        return None
    cx, cy, cz = (float(v) for v in fixture["center"])
    z1 = cz + float((fixture.get("size_m") or (0.2, 0.2, 0.1))[2]) / 2.0
    z2 = float(fixture["mount_z"])
    if z2 - z1 < RIG_CORD_MIN_M:
        return None
    return {"center": [cx, cy, (z1 + z2) / 2.0], "size": [RIG_CORD_M, RIG_CORD_M, z2 - z1], "rotation_deg": 0.0}


def decor_own_id(entry: dict) -> str | None:
    """The decor item's own id in a scene-manifest decor entry (pure; fix round after P4b, 17 Oct 2026): its
    ``decor_id``, else its ``element_id`` / ``wenart_id`` unless that names its host (furniture.py writes hosted decor
    with ``element_id`` = ``wenart_id`` = the host piece), else its object ``name`` (``decor_<host>_<n>``, unique).
    The P4a fix round keyed hosted decor by the host's id, so a plant on a nightstand looked like the nightstand
    itself: the rig lamp stood through it unflagged (P3 real04 r_L0_yatak_odasi, f_L0_050 / dec_L0_010)."""
    if entry.get("decor_id"):
        return str(entry["decor_id"])
    own = entry.get("element_id") or entry.get("wenart_id")
    if own and own != entry.get("host_id"):
        return str(own)
    return entry.get("name") or own


def built_decor_boxes(manifest_objects: list, room_id: str) -> list[dict]:
    """The built decor of a room as world boxes (pure): ``[{"id", "type", "center" [x, y, z_mid], "size" [w, d, h],
    "rotation_deg", "host_id", "has_light", "name", "method"}]`` from the scene manifest's decor entries (furniture.py
    records the built box: ``center`` and ``size``), the rig's own fixtures left out. ``build_lighting`` runs after
    the furniture, so only what was really built is here (a decor item skipped by the builder hosts nothing). Fix
    round after P4b (17 Oct 2026): ``id`` is the item's own id (``decor_own_id``), never its host's; ``host_id`` keeps
    the host apart; ``name`` is the Blender object, ``method`` how it was built (``library`` or a parametric
    fallback)."""
    out = []
    for o in manifest_objects:
        if o.get("kind") != "decor" or o.get("method") == "rig" or o.get("room_id") != room_id:
            continue
        c, s = o.get("center"), o.get("size")
        if not (isinstance(c, (list, tuple)) and len(c) >= 3 and isinstance(s, (list, tuple)) and len(s) >= 3):
            continue
        out.append({"id": decor_own_id(o), "type": o.get("type"),
                    "center": [float(v) for v in c[:3]], "size": [float(v) for v in s[:3]],
                    "rotation_deg": float(o.get("rotation_deg") or 0.0), "host_id": o.get("host_id"),
                    "has_light": bool(o.get("light")), "name": o.get("name"), "method": o.get("method")})
    return out


def built_piece_methods(manifest_objects: list) -> dict:
    """``{piece id: build method}`` of the built furniture in a scene manifest (pure; fix round after P4b): ``library``,
    ``module`` or ``parametric (fallback: ...)``; a library asset whose file failed is parametric here."""
    return {o.get("wenart_id"): o.get("method") for o in manifest_objects
            if o.get("kind") == "furniture" and o.get("wenart_id")}


def _ceiling_at(ceiling_fn, ceil_z: float, x: float, y: float, half: float = 0.0) -> float:
    """The ceiling over a point (absolute z; pure): ``ceiling_fn(x, y)`` at the point and the corners of a square of
    half side ``half`` when given (the sloped ceiling), else the room's ``ceil_z``."""
    if ceiling_fn is None:
        return float(ceil_z)
    pts = [(x, y)] + ([(x + sx * half, y + sy * half) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)] if half > 0 else [])
    return min(float(ceiling_fn(px, py)) for px, py in pts)


def _head_wall(polygon, head_mid, side) -> dict | None:
    """The room edge the bed head stands against (pure): the edge whose distance to the head edge's midpoint is at most
    ``RIG_HEAD_WALL_M`` and that runs along the head (within ``RIG_HEAD_WALL_PARALLEL_DEG``); ``{"a", "b", "u" (unit
    along the edge), "n" (unit normal into the room), "length"}`` or None."""
    best = None
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-6:
            continue
        dist = G.point_segment_distance(head_mid, a, b)
        if dist > RIG_HEAD_WALL_M:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        cos = abs(ux * side[0] + uy * side[1])
        if cos < math.cos(math.radians(RIG_HEAD_WALL_PARALLEL_DEG)):
            continue
        nx, ny = -uy, ux                                   # the left normal; into the room when inside
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        if not G.point_in_polygon((mx + nx * 0.02, my + ny * 0.02), polygon):
            nx, ny = -nx, -ny
        if best is None or dist < best[0]:
            best = (dist, {"a": tuple(a), "b": tuple(b), "u": (ux, uy), "n": (nx, ny), "length": length})
    return best[1] if best else None


def _opening_on_wall(opening: dict, wall: dict, t0: float, t1: float, z0: float, z1: float, floor_z: float) -> bool:
    """Whether a door or window of the head wall overlaps the span ``t0..t1`` along the wall (from its start ``a``)
    and the height ``z0..z1`` (absolute) of a sconce, ``RIG_OPENING_MARGIN_M`` around it (pure)."""
    c = opening.get("center") or [0.0, 0.0]
    ax, ay = wall["a"]
    ux, uy = wall["u"]
    rx, ry = float(c[0]) - ax, float(c[1]) - ay
    along = rx * ux + ry * uy
    off = abs(-rx * uy + ry * ux)
    if off > RIG_OPENING_WALL_M:
        return False
    half = float(opening.get("width") or 0.0) / 2.0
    if along + half <= t0 - RIG_OPENING_MARGIN_M or along - half >= t1 + RIG_OPENING_MARGIN_M:
        return False
    sill = float(opening.get("sill_height") or 0.0) if opening.get("type") == "window" else 0.0
    top = sill + float(opening.get("height") or 2.1)
    return not (floor_z + top <= z0 - RIG_OPENING_MARGIN_M or floor_z + sill >= z1 + RIG_OPENING_MARGIN_M)


def _host_light_z(kind: str, parts: list, bottom: float, top: float, library: bool) -> tuple[float, str]:
    """``(absolute z, where)`` of a rig light in a host lamp (pure; fix round after P4b): ``in_shade``
    (``RIG_HOST_LAMP_SHADE_M`` under the top, at most ``RIG_HOST_LAMP_SHADE_SHARE`` of the height) for a library
    model, else ``below_shade``: ``RIG_HOST_LAMP_BELOW_SHADE_M`` under the lowest point of the parametric shade
    (``parts``: the lamp's parametric parts, bottom on z = 0), as ``furniture.lamp_light_point`` puts a lamp's own
    light; the shade is a closed solid, so a light in it never reaches the room (the review of the P4a fix round)."""
    height = float(top) - float(bottom)
    if library or not parts:
        return float(top) - min(RIG_HOST_LAMP_SHADE_M, RIG_HOST_LAMP_SHADE_SHARE * height), "in_shade"
    zs = [v[2] for p in parts if p.get("role") == "shade" for v in p["verts"]] or \
        [v[2] for p in parts for v in p["verts"]]
    return float(bottom) + min(zs) - RIG_HOST_LAMP_BELOW_SHADE_M, "below_shade"


def _host_lamps(pieces: list[dict], decor: list[dict], floor_z: float, piece_methods: dict | None = None) -> list[dict]:
    """The lamps already in the room that can carry a bedside light (pure): ``floor_lamp`` / ``table_lamp`` pieces
    (their built height from ``parametric.piece_bbox``) and built decor lamps of those types; ``{"id", "type", "xy",
    "top", "height", "source", "host_id", "library", "light_z", "light_where"}`` (z absolute). Fix round after P4b
    (17 Oct 2026): a decor lamp's ``id`` is its own decor id and ``host_id`` the piece it stands on (P4a's fix round
    named the nightstand as the lamp); ``light_z`` / ``light_where`` from ``_host_light_z``: a piece is a library
    model when its built method (``piece_methods``, from the scene manifest; else its asset) is ``library``, a decor
    lamp when its manifest ``method`` is."""
    from wenart.blender import parametric as P

    out = []
    for p in pieces:
        if p.get("type") in RIG_HOST_LAMP_TYPES and p.get("footprint"):
            bw, bd, h, _src = P.piece_bbox(p)
            method = (piece_methods or {}).get(p["id"]) or (p.get("asset") or {}).get("method")
            library = method == "library"
            parts = []
            if not library:
                try:
                    hp, _ = P.proxy_height(p["type"], p.get("height"))
                    fp = p["footprint"]["size"]
                    parts = P.build_parts(p["type"], float(fp[0]), float(fp[1]), float(hp), piece=p)
                except (KeyError, TypeError, ValueError):
                    parts = []
            z, where = _host_light_z(p["type"], parts, float(floor_z), float(floor_z) + float(h), library)
            out.append({"id": p["id"], "type": p["type"], "xy": (float(p["footprint"]["center"][0]),
                        float(p["footprint"]["center"][1])), "top": float(floor_z) + float(h), "height": float(h),
                        "source": "furniture", "host_id": None, "library": library, "light_z": z,
                        "light_where": where})
    for d in decor:
        if d.get("type") in RIG_HOST_LAMP_TYPES:
            w, dd, h = (float(v) for v in d["size"][:3])
            bottom = float(d["center"][2]) - h / 2.0
            library = d.get("method") == "library"
            parts = []
            if not library:
                try:
                    parts = P.decor_parts(d["type"], w, dd, h)
                except (KeyError, TypeError, ValueError):
                    parts = []
            z, where = _host_light_z(d["type"], parts, bottom, bottom + h, library)
            out.append({"id": d["id"], "type": d["type"], "xy": (float(d["center"][0]), float(d["center"][1])),
                        "top": bottom + h, "height": h, "source": "decor", "host_id": d.get("host_id"),
                        "library": library, "light_z": z, "light_where": where})
    return out


def _decor_light_host(decor: list[dict], x: float, y: float, reach: float) -> dict | None:
    """A built decor pendant or ceiling light whose plan box comes within ``reach`` of ``(x, y)`` (pure): the
    nearest, or None."""
    best = None
    for d in decor:
        if d.get("type") not in RIG_DECOR_HOST_TYPES:
            continue
        rect = G.rotated_rectangle(d["center"][:2], d["size"][:2], float(d.get("rotation_deg") or 0.0))
        inside = G.point_in_polygon((x, y), rect)
        dist = 0.0 if inside else min(G.point_segment_distance((x, y), rect[i], rect[(i + 1) % 4]) for i in range(4))
        if dist <= reach and (best is None or dist < best[0]):
            best = (dist, d)
    return best[1] if best else None


def rig_fixture_problems(fixtures: list[dict], polygon, pieces: list[dict], decor: list[dict], floor_z: float,
                         stand_tops: dict | None = None) -> list[dict]:
    """What is wrong with the built rig fixtures of a room (pure; fix round after P4a, 17 Oct 2026):
    ``[{"name", "kind", "problem"}]``. Every fixture with a mesh: its plan centre in the room, its box (``fixture_box``)
    clear of every piece box (``piece_box``) and every built decor box except its anchor and host; a bedside lamp on a
    nightstand (``mount: "stand"``) has its base on that nightstand's top (``stand_tops`` {id: top z} or the
    nightstand's ``piece_box``, within ``RIG_STAND_TOL_M``); a sconce (``mount: "wall"``) has its back within
    ``RIG_SCONCE_WALL_GAP_M`` + 0.01 m of a room edge and its bottom ``RIG_BEDSIDE_MIN_WALL_Z_M`` above the floor; no
    other bedside fixture has a mesh. A fixture without a mesh (``mesh: False``) needs its ``host_id``.

    Fix round after P4b (17 Oct 2026): decor boxes carry their own ids (``built_decor_boxes``), so the skip covers
    only the anchor and host pieces, never the decor that stands on them (a plant on the lamp's own nightstand is a
    crossing); the nightstand top comes from the piece box only (P4a's fix round let the last decor box on a
    nightstand stand for it); a pendant's cord (``pendant_cord_box``, up to its ``mount_z``) is checked like its
    shade."""
    poly = [tuple(p[:2]) for p in polygon]
    piece_boxes = [piece_box(p, floor_z) for p in pieces if p.get("footprint")]
    boxes = piece_boxes + list(decor or [])
    by_id = {b.get("id"): b for b in piece_boxes}
    out = []
    for f in fixtures:
        name, kind = f.get("name"), f.get("kind")
        if f.get("mesh") is False:
            if not f.get("host_id"):
                out.append({"name": name, "kind": kind, "problem": "no mesh and no host"})
            continue
        box = fixture_box(f)
        cx, cy = box["center"][0], box["center"][1]
        if not G.point_in_polygon((cx, cy), poly):
            out.append({"name": name, "kind": kind, "problem": "outside the room"})
        skip = {f.get("anchor_id"), f.get("host_id")} - {None}
        cord = pendant_cord_box(f)
        for b in boxes:
            if b.get("id") in skip or b.get("type") in RIG_COLLISION_SKIP_TYPES:
                continue
            if boxes_collide(box, b):
                out.append({"name": name, "kind": kind, "problem": f"crosses {b.get('type')} {b.get('id')}"})
            elif cord is not None and boxes_collide(cord, b):
                out.append({"name": name, "kind": kind, "problem": f"cord crosses {b.get('type')} {b.get('id')}"})
        if kind != "bedside":
            continue
        bottom = box["center"][2] - box["size"][2] / 2.0
        mount = f.get("mount")
        if mount == "stand":
            host = f.get("host_id") or f.get("anchor_id")
            top = (stand_tops or {}).get(host)
            if top is None and host in by_id:
                top = by_id[host]["center"][2] + by_id[host]["size"][2] / 2.0
            if top is None or abs(bottom - float(top)) > RIG_STAND_TOL_M:
                out.append({"name": name, "kind": kind, "problem": f"base at {bottom - floor_z:.2f} m is not on the "
                                                                   f"top of its nightstand {host}"})
        elif mount == "wall":
            if bottom < floor_z + RIG_BEDSIDE_MIN_WALL_Z_M - 1e-6:
                out.append({"name": name, "kind": kind, "problem": f"sconce bottom {bottom - floor_z:.2f} m above the "
                                                                   f"floor (< {RIG_BEDSIDE_MIN_WALL_Z_M} m)"})
            rect = G.rotated_rectangle(box["center"][:2], box["size"][:2], box["rotation_deg"])
            gap = min(G.point_segment_distance(c, poly[i], poly[(i + 1) % len(poly)])
                      for c in rect for i in range(len(poly)))
            if gap > RIG_SCONCE_WALL_GAP_M + 0.01:
                out.append({"name": name, "kind": kind, "problem": f"sconce back {gap:.3f} m off every wall"})
        else:
            out.append({"name": name, "kind": kind, "problem": "a bedside lamp with a mesh on no nightstand or wall"})
    return out


def _stand_spot(stand: dict, size_m, top: float, decor: list[dict], corner) -> tuple[tuple | None, dict | None]:
    """Where a rig table lamp of ``size_m`` stands on a nightstand whose top is at ``top`` (pure; fix round after
    P4b, 17 Oct 2026): ``((x, y), None)`` at the centre of the top when no built decor box is in the way; else
    ``((x, y), the item at the centre)`` at the first free spot of the top, its shade ``RIG_STAND_EDGE_M`` inside the
    edge (the middles of the four edges and the four corners of the top, nearest to the bed's head ``corner``
    first); ``(None, the item at the centre)`` when no spot is free (P3's real04: a 0.24 m lamp and a plant cannot
    share a 0.40 m top)."""
    from wenart.blender.parametric import piece_bbox

    fp = stand["footprint"]
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    bw, bd = (float(v) for v in piece_bbox(stand)[:2])
    side = max(float(size_m[0]), float(size_m[1]))
    h = float(size_m[2])
    hx, hy = bw / 2.0 - side / 2.0 - RIG_STAND_EDGE_M, bd / 2.0 - side / 2.0 - RIG_STAND_EDGE_M
    local = [(0.0, 0.0)]
    if hx > 1e-6:
        local += [(-hx, 0.0), (hx, 0.0)]
    if hy > 1e-6:
        local += [(0.0, -hy), (0.0, hy)]
    if hx > 1e-6 and hy > 1e-6:
        local += [(sx * hx, sy * hy) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    spots = [(cx + lx * math.cos(rot) - ly * math.sin(rot), cy + lx * math.sin(rot) + ly * math.cos(rot))
             for lx, ly in local]
    spots = spots[:1] + sorted(spots[1:], key=lambda q: (round(G.distance(q, corner), 6), q))

    def blocker_at(q):
        box = {"center": [q[0], q[1], top + h / 2.0], "size": [side, side, h], "rotation_deg": 0.0}
        return next((d for d in decor if d.get("type") not in RIG_COLLISION_SKIP_TYPES and boxes_collide(box, d)),
                    None)

    first = blocker_at(spots[0])
    if first is None:
        return spots[0], None
    for q in spots[1:]:
        if blocker_at(q) is None:
            return q, first
    return None, first


def rig_plan(room: dict, pieces: list[dict], floor_z: float, ceil_z: float, holes=(),
             lighting: dict | None = None, agent_factor: float = 1.0, decor=(), openings=(),
             ceiling_fn=None, piece_methods: dict | None = None) -> dict:
    """Where the fixtures of ``room_rig(room["room_type"])`` go (pure): ``{"fixtures": [...], "dropped": [...]}``.
    Each fixture: the ``room_rig`` record plus ``name``, ``center`` [x, y, z] (the visible fixture's centre),
    ``light`` {``type`` POINT | AREA, ``center``, ``size_m``, ``direction`` (an area light's -Z), ``energy_w``,
    ``radius_m``}, ``temperature_k``, ``anchor_id`` and ``reason``. ``pieces`` are the room's built pieces
    (``footprint``, ``type``, ``front_deg``); ``holes`` the stair openings of the level (ceiling fixtures stay out
    of them, as the Milestone 6 light does). A fixture whose anchor is missing is listed under ``dropped`` with the
    reason, except ``optional`` ones, which are silently left out. Fix round after P3 (16-17 Oct 2026): a ceiling
    spec with ``lumens_per_m2`` (hall, stair) gives each fixture ``rig_bulbs`` bulbs; the fixture records ``bulbs``,
    ``lumens_per_bulb`` and its own ``lumens`` / ``watts_radiometric`` / ``watts_applied`` (bulbs x the spec's).

    Fix round after P4a (17 Oct 2026): ``decor`` is the room's built decor as world boxes (``built_decor_boxes``),
    ``openings`` its doors and windows (building records), ``ceiling_fn(x, y)`` the ceiling's absolute height at a
    point (the sloped ceiling; ``ceil_z`` without it). Every fixture also records ``mount`` (``ceiling``, ``stand``,
    ``wall``, ``host``), ``mesh`` (False: the light sits in a host lamp, no rig mesh), ``host_id`` and
    ``rotation_deg``. Bedside lamps: a lamp already there, else a nightstand, else a wall sconce on the head wall,
    else none (the module docstring). The mirror light goes above the wall items behind the basin. A pendant or
    ceiling fixture under a built decor light uses it as host. ``rig_fixture_problems`` checks the result; a fixture
    that fails it is dropped with the reason.

    Fix round after P4b (17 Oct 2026): ``piece_methods`` ({piece id: build method}, ``built_piece_methods``) says which
    lamp pieces are library models. A light hosted in a decor pendant hangs ``RIG_HOSTED_PENDANT_GAP_M`` under it; a
    light hosted in a lamp sits in the shade of a library model, else under the shade (``_host_light_z``); a hosted
    fixture records ``light_where`` and ``escape_low_z`` (``build_room_rig`` checks by rays that the light gets out of
    its host and steps it down to that height at most). A table lamp on a nightstand takes a free spot of the top
    when built decor stands at its centre, else the side falls through to the wall sconce (the reason names the
    item); a decor lamp's own id hosts the light and the nightstand it stands on is used. Pendants and ceiling
    fixtures record ``mount_z`` (the ceiling over them), where their cord and canopy end (``_fixture_hardware``)."""
    from wenart.blender.parametric import piece_bbox

    polygon = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
        polygon = polygon[:-1]
    out: dict = {"fixtures": [], "dropped": []}
    if len(polygon) < 3:
        return out
    decor = [d for d in decor or []]
    temperature = rig_temperature_for(room.get("room_type"), lighting)    # integration after P4b: per room type
    by_type: dict[str, list[dict]] = {}
    for p in pieces:
        by_type.setdefault(str(p.get("type")), []).append(p)
    count = 0

    def add(spec: dict, centre, light_centre, light_type: str, energy: float, size, direction=None, anchor=None,
            radius: float = 0.05, reason: str = "", mount: str = "ceiling", mesh: bool = True, host=None,
            rotation=None, mount_z=None, **extra) -> None:
        nonlocal count
        count += 1
        f = dict(spec)
        f.update(name=f"rig_{room['id']}_{spec['kind']}_{count}", center=[round(float(v), 4) for v in centre],
                 temperature_k=temperature, anchor_id=anchor, reason=reason, mount=mount, mesh=bool(mesh),
                 host_id=host,
                 light={"type": light_type, "center": [round(float(v), 4) for v in light_centre],
                        "size_m": [round(float(v), 4) for v in size],
                        "energy_w": round(float(energy) * agent_factor, 4), "radius_m": radius,
                        "direction": [round(float(v), 4) for v in direction] if direction else None})
        if rotation is not None:
            f["rotation_deg"] = round(float(rotation), 3)
        if mount_z is not None:                       # fix round after P4b: where the cord and canopy end
            f["mount_z"] = round(float(mount_z), 4)
        f.update({k: v for k, v in extra.items() if v is not None})
        out["fixtures"].append(f)

    def hosted_z(host: dict) -> float:
        """The light's height under a decor host: under a pendant (fix round after P4b: in its shade it was inside
        the model's closed geometry) or under a ceiling light."""
        bottom = float(host["center"][2]) - float(host["size"][2]) / 2.0
        if host.get("type") == "pendant_light":
            return bottom - RIG_HOSTED_PENDANT_GAP_M
        return bottom - RIG_HOSTED_CEILING_GAP_M

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
            r = max(float(spec["size_m"][0]), float(spec["size_m"][1])) / 2.0
            host = _decor_light_host([d for d in decor if d.get("type") == "pendant_light"], cx, cy, r)
            if host is not None and hosted_z(host) >= floor_z + RIG_HOSTED_MIN_Z_M:
                hx, hy, lz = float(host["center"][0]), float(host["center"][1]), hosted_z(host)
                add(spec, (hx, hy, lz), (hx, hy, lz), "POINT", spec["watts_applied"], spec["size_m"],
                    anchor=table["id"], radius=0.06, mount="host", mesh=False, host=host["id"],
                    light_where="under_host", reason=f"pendant light over the dining table {table['id']} under the "
                                                     f"decor pendant {host['id']}")
                continue
            # fix round after P4b: the ceiling over the shade clamps it; the one over the canopy is where the cord ends
            ceil_here = _ceiling_at(ceiling_fn, ceil_z, cx, cy, r)
            z = floor_z + RIG_TABLE_TOP_M + RIG_PENDANT_OVER_TABLE_M + h / 2.0
            z = min(z, ceil_here - RIG_MOUNT_GAP_M - h / 2.0)
            add(spec, (cx, cy, z), (cx, cy, z - h * 0.2), "POINT", spec["watts_applied"], spec["size_m"],
                anchor=table["id"], radius=0.06, reason=f"pendant over the dining table {table['id']}",
                mount="ceiling", mount_z=_ceiling_at(ceiling_fn, ceil_z, cx, cy, RIG_CANOPY_R_M))
        elif kind == "ceiling":
            plans = area_light_plans(polygon, holes=holes) if room.get("room_type") in ("hall", "stair") else \
                [area_light_plan(polygon, holes=holes)]
            h = float(spec["size_m"][2])
            r = max(float(spec["size_m"][0]), float(spec["size_m"][1])) / 2.0
            # fix round after P3: the hall and stair fixtures carry bulbs for RIG_CIRCULATION_LUMENS_PER_M2
            bulbs = rig_bulbs(spec, G.polygon_area(polygon), len(plans))
            fspec = spec
            reason = f"ceiling fixture at the pole of inaccessibility of {room['id']}"
            if spec.get("lumens_per_m2"):
                fspec = dict(spec, bulbs=bulbs, lumens_per_bulb=spec["lumens"],
                             lumens=round(float(spec["lumens"]) * bulbs, 1),
                             watts_radiometric=round(float(spec["watts_radiometric"]) * bulbs, 4),
                             watts_applied=round(float(spec["watts_applied"]) * bulbs, 4))
                reason += (f", {bulbs} x {float(spec['lumens']):g} lm bulbs for {float(spec['lumens_per_m2']):g} lm/m2 "
                           f"over {G.polygon_area(polygon):.1f} m2 and {len(plans)} fixture(s)")
            for plan in plans:
                cx, cy = plan["center"]
                host = _decor_light_host(decor, cx, cy, r)
                if host is not None and hosted_z(host) >= floor_z + RIG_HOSTED_MIN_Z_M:
                    hx, hy, lz = float(host["center"][0]), float(host["center"][1]), hosted_z(host)
                    add(fspec, (hx, hy, lz), (hx, hy, lz), "POINT", fspec["watts_applied"], spec["size_m"],
                        radius=0.08, mount="host", mesh=False, host=host["id"], light_where="under_host",
                        reason=f"{reason}; its light under the decor {host['type'].replace('_', ' ')} {host['id']}")
                    continue
                z = _ceiling_at(ceiling_fn, ceil_z, cx, cy, r) - RIG_MOUNT_GAP_M - h / 2.0
                add(fspec, (cx, cy, z), (cx, cy, z - h / 2.0 - 0.02), "POINT", fspec["watts_applied"], spec["size_m"],
                    radius=0.08, reason=reason, mount="ceiling",
                    mount_z=_ceiling_at(ceiling_fn, ceil_z, cx, cy, RIG_CANOPY_R_M))
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
            lamps = _host_lamps(pieces, decor, floor_z, piece_methods)
            wall = _head_wall(polygon, (hx, hy), (sx, sy))
            used: set = set()
            h = float(spec["size_m"][2])
            for side in (-1.0, 1.0):
                corner = (hx + sx * side * width / 2.0, hy + sy * side * width / 2.0)
                lamp = min((lp for lp in lamps if lp["id"] not in used), default=None,
                           key=lambda lp: G.distance(lp["xy"], corner))
                stand = min((p for p in nightstands if p["id"] not in used), default=None,
                            key=lambda p: G.distance(p["footprint"]["center"][:2], corner))
                if lamp is not None and G.distance(lamp["xy"], corner) <= RIG_BEDSIDE_HOST_M:
                    # (1) a lamp already there (the AI's floor lamp, a decor lamp on the nightstand): its light only.
                    # Fix round after P4b: a decor lamp is named by its own id, the nightstand under it is used too,
                    # and the light sits under the shade of a lamp that is no library model (_host_light_z).
                    used.add(lamp["id"])
                    if lamp.get("host_id"):
                        used.add(lamp["host_id"])
                    lz = lamp["light_z"]
                    px, py = lamp["xy"]
                    on = f" on {lamp['host_id']}" if lamp.get("host_id") else ""
                    where = "in the shade" if lamp["light_where"] == "in_shade" else "under the shade"
                    add(spec, (px, py, lz), (px, py, lz), "POINT", spec["watts_applied"], spec["size_m"],
                        anchor=lamp["id"], radius=0.05, mount="host", mesh=False, host=lamp["id"],
                        light_where=lamp["light_where"],
                        escape_low_z=round(lamp["top"] - (1.0 - RIG_ESCAPE_LOW_SHARE) * lamp["height"], 4),
                        reason=f"bedside light {where} of the {lamp['type'].replace('_', ' ')} {lamp['id']}{on} "
                               f"beside the bed {bed['id']}")
                    continue
                cause = "no nightstand, no lamp"
                if stand is not None and G.distance(stand["footprint"]["center"][:2], corner) <= RIG_BEDSIDE_HOST_M:
                    # (2) a nightstand: the lamp stands on its top, at a free spot (fix round after P4b: P3's real04
                    # lamps stood through the plant at the centre of f_L0_050 and f_L0_054)
                    used.add(stand["id"])
                    top = floor_z + float(piece_bbox(stand)[2])
                    spot, blocker = _stand_spot(stand, spec["size_m"], top, decor, corner)
                    if spot is not None:
                        px, py = spot
                        moved = "" if blocker is None else (f", beside the {blocker.get('type')} {blocker.get('id')} "
                                                           f"at the centre of its top")
                        add(spec, (px, py, top + h / 2.0), (px, py, top + h * 0.7), "POINT", spec["watts_applied"],
                            spec["size_m"], anchor=stand["id"], radius=0.05, mount="stand", host=stand["id"],
                            reason=f"bedside lamp on the nightstand {stand['id']}{moved}")
                        continue
                    # no free spot: the side falls through to the wall sconce, else no lamp, with the reason
                    cause = (f"the top of the nightstand {stand['id']} is taken by the {blocker.get('type')} "
                             f"{blocker.get('id')}")
                why = f"bedside lamp beside the head of the bed {bed['id']} ({cause})"
                if wall is None:
                    # (4) no host at all: no lamp (P4a: the lamp floated beside the bed with its stem in the air)
                    out["dropped"].append({"kind": kind, "reason": f"{why}: the bed head is not against a wall, so no "
                                                                   f"wall sconce"})
                    continue
                # (3) a wall sconce on the head wall, beside the corner
                sw, sd, sh = (float(v) for v in RIG_SCONCE_SIZE_M)
                ax, ay = wall["a"]
                ux, uy = wall["u"]
                nx, ny = wall["n"]
                qx = corner[0] + sx * side * RIG_SCONCE_BEYOND_M
                qy = corner[1] + sy * side * RIG_SCONCE_BEYOND_M
                t = (qx - ax) * ux + (qy - ay) * uy
                off = sd / 2.0 + RIG_SCONCE_WALL_GAP_M
                px, py = ax + ux * t + nx * off, ay + uy * t + ny * off
                pz = floor_z + RIG_SCONCE_Z_M
                rot = math.degrees(math.atan2(uy, ux))
                sconce = {"center": [px, py, pz], "size": [sw, sd, sh], "rotation_deg": rot}
                problem = None
                if t - sw / 2.0 < RIG_SCONCE_END_MARGIN_M or t + sw / 2.0 > wall["length"] - RIG_SCONCE_END_MARGIN_M:
                    problem = "the wall sconce would run past the end of the head wall"
                elif not G.point_in_polygon((px, py), polygon):
                    problem = "the wall sconce would stand outside the room"
                elif pz + sh / 2.0 > _ceiling_at(ceiling_fn, ceil_z, px, py, sw / 2.0) - RIG_SCONCE_CEILING_CLEAR_M:
                    problem = "the wall sconce would reach the ceiling"
                else:
                    hit = next((o for o in openings or [] if o.get("type") in ("door", "window") and _opening_on_wall(
                        o, wall, t - sw / 2.0, t + sw / 2.0, pz - sh / 2.0, pz + sh / 2.0, floor_z)), None)
                    if hit is not None:
                        problem = f"the wall sconce would cover the {hit.get('type')} {hit.get('id')}"
                    else:
                        boxes = [piece_box(p, floor_z) for p in pieces if p.get("footprint")] + decor
                        crossed = next((b for b in boxes if b.get("type") not in RIG_COLLISION_SKIP_TYPES
                                        and boxes_collide(sconce, b)), None)
                        if crossed is not None:
                            problem = f"the wall sconce would cross the {crossed.get('type')} {crossed.get('id')}"
                if problem:
                    out["dropped"].append({"kind": kind, "reason": f"{why}: {problem}"})
                    continue
                lf = sd / 2.0 + RIG_SCONCE_LIGHT_FRONT_M                        # in front of the shade
                add(dict(spec, size_m=[sw, sd, sh]), (px, py, pz), (px + nx * lf, py + ny * lf, pz), "POINT",
                    spec["watts_applied"], [sw, sd, sh], anchor=bed["id"], radius=0.04, mount="wall", rotation=rot,
                    reason=f"bedside wall sconce on the head wall beside the bed {bed['id']} ({cause})")
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
                add(f, (px, py, z), (px, py, z - 0.012), "AREA", watts, [length, 0.02, 0.015],
                    direction=(0.0, 0.0, -1.0), anchor=counter["id"], radius=0.0, mount="cabinet",
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
            bar_w, bar_d, bar_h = float(spec["size_m"][0]), 0.04, 0.04
            rot = round(math.degrees(math.atan2(fy, fx)) + 90.0, 3)
            # fix round after P4a: above the basin's own top (a vanity module's mirror) and the wall decor behind it
            reach = {"center": [px, py, 0.0], "size": [bar_w + 2 * RIG_WALL_ITEM_REACH_M,
                                                         bar_d + 2 * RIG_WALL_ITEM_REACH_M, 1.0], "rotation_deg": rot}
            under = [(floor_z + float(piece_bbox(basin)[2]), f"the basin {basin['id']}")]
            for d in decor:
                if d.get("type") in RIG_WALL_DECOR_TYPES and _convex_overlap(
                        G.rotated_rectangle(reach["center"][:2], reach["size"][:2], rot),
                        G.rotated_rectangle(d["center"][:2], d["size"][:2], float(d.get("rotation_deg") or 0.0))):
                    under.append((float(d["center"][2]) + float(d["size"][2]) / 2.0,
                                  f"the {d['type'].replace('_', ' ')} {d['id']}"))
            top, top_what = max(under, key=lambda u: u[0])
            z = floor_z + RIG_MIRROR_LIGHT_Z_M
            ceiling = _ceiling_at(ceiling_fn, ceil_z, px, py, bar_w / 2.0)
            low = top + RIG_MIRROR_LIGHT_GAP_M + bar_h / 2.0
            cap = ceiling - RIG_MIRROR_CEILING_CLEAR_M - bar_h / 2.0
            if z < low:
                z = low
            z = min(z, cap)
            if z < low - 1e-6:
                out["dropped"].append({"kind": kind, "reason": f"mirror light over the washbasin {basin['id']}: "
                                       f"{top_what} reaches {top - floor_z:.2f} m and the ceiling is at "
                                       f"{ceiling - floor_z:.2f} m, so the bar would cross it"})
                continue
            moved = f", above {top_what} (top {top - floor_z:.2f} m)" if low > floor_z + RIG_MIRROR_LIGHT_Z_M else ""
            f = dict(spec, rotation_deg=rot)
            add(f, (px, py, z), (px + fx * 0.03, py + fy * 0.03, z - 0.03), "AREA", spec["watts_applied"],
                [bar_w, bar_d, bar_h], direction=(fx * 0.7, fy * 0.7, -0.7), anchor=basin["id"],
                radius=0.0, mount="wall", reason=f"mirror light over the washbasin {basin['id']}{moved}")
    # fix round after P4a: every fixture with a mesh passes the code check, or it is dropped with the reason
    stand_tops = {p["id"]: floor_z + float(piece_bbox(p)[2]) for p in by_type.get("nightstand") or []}
    problems = rig_fixture_problems(out["fixtures"], polygon, pieces, decor, floor_z, stand_tops)
    if problems:
        bad: dict = {}
        for p in problems:
            bad.setdefault(p["name"], []).append(p["problem"])
        keep = []
        for f in out["fixtures"]:
            if f["name"] in bad:
                out["dropped"].append({"kind": f["kind"], "name": f["name"],
                                       "reason": f"{f['reason']}: {'; '.join(bad[f['name']])}"})
            else:
                keep.append(f)
        out["fixtures"] = keep
    return out


def _prism(cx: float, cy: float, z0: float, z1: float, r: float, n: int = 8) -> tuple[list, list]:
    """A closed ``n``-sided prism of circumradius ``r`` from ``z0`` to ``z1`` (pure): 2n vertices, n + 2 faces."""
    verts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    verts += [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n))[::-1])
    faces.append([n + i for i in range(n)])
    return verts, faces


def _fixture_mesh(fixture: dict) -> tuple[list, list]:
    """World-space vertices and faces of a fixture's visible shade (pure, ``geom2d.box``): pendants and ceiling
    fixtures are 8-sided drums, bedside lamps a drum shade, strips and mirror lights flat bars. Fix round after P4a
    (17 Oct 2026): a table lamp's (``mount: "stand"``) shade fills the upper part of its box above
    ``RIG_STAND_STEM_SHARE`` (the P3/P4a stem hung under the base, into the nightstand or the air); a wall sconce
    (``mount: "wall"``) is a drum as deep as its box; a fixture without a mesh (``mesh: False``) has no geometry. Fix
    round after P4b (17 Oct 2026): this is the emissive shade only; the stem, the base, the cord and the canopy are the
    hardware (``_fixture_hardware``, not emissive: P4b's stems glowed in the nightstands' open shelves)."""
    from wenart.blender import geom2d

    if fixture.get("mesh") is False:
        return [], []
    cx, cy, cz = fixture["center"]
    w, d, h = [float(v) for v in fixture.get("size_m") or (0.2, 0.2, 0.1)]
    kind = fixture["kind"]
    rot = float(fixture.get("rotation_deg") or 0.0)
    if kind in ("strip", "mirror"):
        size = (float(fixture.get("length_m") or w), d, h)
        return geom2d.box((cx, cy, cz), size, rot)
    mount = fixture.get("mount")
    r = min(w, d) / 2.0 if mount == "wall" else max(w, d) / 2.0
    z0, z1 = cz - h / 2.0, cz + h / 2.0
    if kind == "bedside" and mount != "wall":                         # the shade over the stem
        z0 = cz - h / 2.0 + h * RIG_STAND_STEM_SHARE
    return _prism(cx, cy, z0, z1, r)


def _fixture_hardware(fixture: dict) -> tuple[list, list]:
    """World-space vertices and faces of a fixture's hardware (pure; fix round after P4b, 17 Oct 2026, the verifier's
    better fix of the P4b look finding "rig fixtures read as primitives": all 6 rig pendants of real03 hung as cordless
    drums about 1 m under the ceiling, the bedside stems glowed): a pendant's cord (``RIG_CORD_M`` wide, from the
    shade's top) and canopy (8-sided, ``RIG_CANOPY_R_M`` x ``RIG_CANOPY_H_M``, its top at the fixture's ``mount_z``;
    a cord under ``RIG_CORD_MIN_M`` is left out and the canopy reaches down to the shade); a ceiling fixture's canopy
    over its gap to the ceiling; a table lamp's base disc (``RIG_STAND_BASE_R_M`` x ``RIG_STAND_BASE_H_M``) on the
    nightstand and its stem (``RIG_STEM_M``) up to the shade. Nothing for strips, mirror lights, sconces and fixtures
    without a mesh or a mount height."""
    from wenart.blender import geom2d

    if fixture.get("mesh") is False:
        return [], []
    kind, mount = fixture.get("kind"), fixture.get("mount")
    cx, cy, cz = (float(v) for v in fixture["center"])
    h = float((fixture.get("size_m") or (0.2, 0.2, 0.1))[2])
    parts: list[tuple[list, list]] = []
    if kind in ("pendant", "ceiling") and fixture.get("mount_z") is not None:
        z1, top = cz + h / 2.0, float(fixture["mount_z"])
        if top - z1 > 1e-4:
            canopy_h = min(RIG_CANOPY_H_M, top - z1)
            if top - canopy_h - z1 < RIG_CORD_MIN_M:
                canopy_h = top - z1                                  # no cord: the canopy reaches the shade
            else:
                cord = geom2d.box((cx, cy, (z1 + top - canopy_h) / 2.0), (RIG_CORD_M, RIG_CORD_M, top - canopy_h - z1),
                                  0.0)
                parts.append((list(cord[0]), list(cord[1])))
            parts.append(_prism(cx, cy, top - canopy_h, top, RIG_CANOPY_R_M))
    elif kind == "bedside" and mount == "stand":
        base = cz - h / 2.0
        shade = base + h * RIG_STAND_STEM_SHARE
        base_h = min(RIG_STAND_BASE_H_M, shade - base)
        parts.append(_prism(cx, cy, base, base + base_h, RIG_STAND_BASE_R_M))
        if shade - base - base_h > 1e-4:
            stem = geom2d.box((cx, cy, (base + base_h + shade) / 2.0), (RIG_STEM_M, RIG_STEM_M, shade - base - base_h),
                              0.0)
            parts.append((list(stem[0]), list(stem[1])))
    verts, faces = [], []
    for pv, pf in parts:
        off = len(verts)
        verts += [tuple(v) for v in pv]
        faces += [[off + i for i in f] for f in pf]
    return verts, faces


def _fixture_geometry(fixture: dict) -> tuple[list, list, list]:
    """``(verts, faces, slots)`` of a fixture's object (pure; fix round after P4b): the shade (``_fixture_mesh``, slot
    0, the emissive material) and the hardware (``_fixture_hardware``, slot 1, the dark metal)."""
    sv, sf = _fixture_mesh(fixture)
    hv, hf = _fixture_hardware(fixture)
    off = len(sv)
    faces = [list(f) for f in sf] + [[off + i for i in f] for f in hf]
    return list(sv) + list(hv), faces, [0] * len(sf) + [1] * len(hf)


def hardware_material(bpy):
    """The fixtures' hardware material (fix round after P4b): a Principled BSDF in dark bronze
    (``RIG_HARDWARE_RGB``, metallic ``RIG_HARDWARE_METALLIC``, roughness ``RIG_HARDWARE_ROUGHNESS``), no emission;
    one per file, cached by name."""
    name = "rig_hardware"
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], mat.node_tree.nodes.get("Material Output").inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*RIG_HARDWARE_RGB, 1.0)
    bsdf.inputs["Metallic"].default_value = RIG_HARDWARE_METALLIC
    bsdf.inputs["Roughness"].default_value = RIG_HARDWARE_ROUGHNESS
    mat.diffuse_color = (*RIG_HARDWARE_RGB, 1.0)
    mat["wenart_rig_hardware"] = True
    return mat


# 26 directions (the 3 x 3 x 3 grid without its centre): a light whose rays all hit its host first is enclosed.
_ESCAPE_DIRECTIONS = [(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]


def _light_origins(point, radius: float) -> list[tuple]:
    """The light's centre and the six points ``radius`` away from it along the axes (pure)."""
    px, py, pz = (float(v) for v in point)
    r = float(radius)
    return [(px, py, pz)] + [(px + dx * r, py + dy * r, pz + dz * r) for dx, dy, dz in
                             ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]


def _host_ray(host, depsgraph, origin, direction):
    """``(hit, world location)`` of a ray from ``origin`` along ``direction`` (world space) on the host object's
    evaluated mesh only (``bpy.types.Object.ray_cast`` works in the object's local space; rays hit front and back
    faces)."""
    from mathutils import Vector

    inv = host.matrix_world.inverted()
    o = inv @ Vector(origin)
    d = (inv.to_3x3() @ Vector(direction)).normalized()
    hit, loc, _n, _i = host.ray_cast(o, d, depsgraph=depsgraph)
    return bool(hit), (host.matrix_world @ loc if hit else None)


def light_escapes(host, depsgraph, point, radius: float) -> bool:
    """Whether a point light at ``point`` (radius ``radius``) gets out of its host object (fix round after P4b, 17 Oct
    2026): some ray of ``_ESCAPE_DIRECTIONS`` from the point, or from the six points ``radius`` away along the axes
    (the light is a sphere: a thin lamp pole through its centre does not trap it), misses the host's mesh. False when
    every ray hits the host: a closed shade or bulb around the light (P4a: dec_L-1_017's closed bulb, abo_B07HKCRWJH;
    the floor metered the same with the light on or off). Checked on the four ABO lamps of the P4a review (bpy 5.2.2,
    the GLBs at their fitted sizes): B07HKC3S4T and B075X2NLK5 in their shades and B07374K537 0.12 m over its bottom
    let the light out, B07HKCRWJH at that spot does not and 0.03 m under its bottom does, as the review metered."""
    for o in _light_origins(point, radius):
        for d in _ESCAPE_DIRECTIONS:
            if not _host_ray(host, depsgraph, o, d)[0]:
                return True
    return False


def free_light_point(host, depsgraph, point, radius: float, low_z: float | None) -> tuple:
    """``(point, escapes, moved_m)`` for a hosted light (fix round after P4b): the point itself when it gets out of its
    host (``light_escapes``); else ``RIG_ESCAPE_STEP_M`` under the lowest surface of the host straight under the light
    (the bottom of its closed shade or bulb: the rays straight down from the light's origins), again until the light
    gets out, never below ``low_z`` (None: no search; a pendant or ceiling host's light is already under it); else the
    point unchanged with ``escapes`` False (recorded, never silent)."""
    px, py, pz = (float(v) for v in point)
    z = pz
    for _ in range(8):
        if light_escapes(host, depsgraph, (px, py, z), radius):
            return (px, py, z), True, round(pz - z, 4)
        if low_z is None:
            break
        hits = [loc[2] for loc in (_host_ray(host, depsgraph, o, (0.0, 0.0, -1.0))[1]
                                   for o in _light_origins((px, py, z), radius)) if loc is not None]
        if not hits or min(hits) - RIG_ESCAPE_STEP_M < float(low_z) - 1e-9:
            break
        z = float(min(hits)) - RIG_ESCAPE_STEP_M
    return (px, py, pz), False, 0.0


def host_object_name(manifest_objects: list, host_id: str | None) -> str | None:
    """The Blender object of a rig light's host (pure; fix round after P4b): the built decor item whose own id
    (``decor_own_id``) is ``host_id``, else the built furniture piece of that id; None when neither was built."""
    if not host_id:
        return None
    for o in manifest_objects:
        if o.get("kind") == "decor" and o.get("method") != "rig" and decor_own_id(o) == host_id:
            return o.get("name")
    for o in manifest_objects:
        if o.get("kind") == "furniture" and o.get("wenart_id") == host_id:
            return o.get("name")
    return None


def build_room_rig(bpy, common, collection, manifest_objects: list, assumed: list, room: dict, level: dict,
                   plan: dict, fixture_material, hardware=None) -> list:
    """The fixtures of ``rig_plan`` as objects: an emissive mesh (kind ``decor``, status ``assumed``, the camera sees
    it) and a POINT or AREA light inside (``use_temperature``, ``shadow_soft_size``, soft falloff where the light
    type has it: bpy.types.PointLight / SpotLight.use_soft_falloff). Returns the light objects. Fix round after P4a
    (17 Oct 2026): a fixture with ``mesh: False`` (its light in a host lamp) gets the light only; every shade is
    ``visible_shadow = False`` (bpy.types.Object.visible_shadow), so the light inside its closed drum reaches the room
    (an Emission-only surface blocks shadow rays: the P3/P4a pendant and bedside lights never left their drums); the
    mesh entry records ``rig_box`` (``fixture_box``) and the fixture's ``mount`` and ``host_id``.

    Fix round after P4b (17 Oct 2026): the object has two material slots, the emissive shade (slot 0) and the
    non-emissive hardware (slot 1, ``hardware`` or ``hardware_material``): a pendant's cord and canopy, a ceiling
    fixture's canopy, a table lamp's base and stem (``_fixture_geometry``); the entry records ``materials`` and
    ``hardware`` (``mount_z``, ``cord_m``). The hardware shares the shade's object, so it casts no shadow either (a
    6 mm cord, a canopy against the ceiling, a 3 cm stem: not visible); a separate object would change the rig's
    object names and counts that the scene tests and render.py's ``wenart_rig`` set rely on. A hosted light
    (``mesh: False``) is checked by rays against its host's object (``host_object_name``, ``free_light_point``): when
    the host's geometry encloses it, it goes under the host's surface below it, not lower than the fixture's
    ``escape_low_z``; the light entry records ``escape`` (``host_object``, ``escapes``, ``moved_m``) and a light still
    enclosed adds an ``assumed`` entry of kind ``rig_light_enclosed``."""
    from mathutils import Vector

    lights = []
    hw_mat = None
    for f in plan["fixtures"]:
        escape = None
        if f.get("mesh") is not False:
            verts, faces, slots = _fixture_geometry(f)
            mat = fixture_material(f["temperature_k"])
            mats = [mat]
            if 1 in slots:
                if hw_mat is None:
                    hw_mat = hardware if hardware is not None else hardware_material(bpy)
                mats.append(hw_mat)
            ob = common.new_mesh_object(f["name"], verts, faces, collection=collection, wenart_id=f["name"],
                                        kind="decor", status="assumed", materials=mats, face_material_indices=slots)
            ob["wenart_room"] = room["id"]
            ob["wenart_rig"] = f["kind"]
            ob.visible_shadow = False             # fix round after P4a: the light inside the shade gets out
            cord = pendant_cord_box(f)
            manifest_objects.append({
                "name": ob.name, "wenart_id": f["name"], "kind": "decor", "status": "assumed", "level_id": level["id"],
                "element_id": room["id"], "parent": room["id"], "evidence": [], "material": mat.name,
                "materials": [m.name for m in mats],
                "textured": False, "pass_index": None, "method": "rig", "type": f"rig_{f['kind']}",
                "rotation_deg": f.get("rotation_deg") or 0.0, "rig_box": fixture_box(f), "visible_shadow": False,
                "hardware": {"mount_z": f.get("mount_z"), "cord_m": round(cord["size"][2], 4) if cord else 0.0,
                             "faces": slots.count(1), "material": hw_mat.name if 1 in slots else None},
                "assumed": {"rig": f["kind"], "lumens": f.get("lumens"), "bulbs": f.get("bulbs", 1),
                            "watts_radiometric": f.get("watts_radiometric"),
                            "watts_applied": f["light"]["energy_w"], "gain": f.get("gain"),
                            "temperature_k": f["temperature_k"], "anchor_id": f.get("anchor_id"),
                            "host_id": f.get("host_id"), "mount": f.get("mount"), "reason": f["reason"],
                            "source": f.get("source"), "lumen_watt_source": f.get("lumen_watt_source"),
                            # round 3: the shade's own radiance, decoupled from the lamp power (never clips at EV <= +3)
                            "shade_emission_wm2sr": float(mat.get("wenart_light") or SHADE_EMISSION_WM2SR)},
            })
        else:
            # fix round after P4b: the hosted light must get out of its host's geometry (checked per model by rays)
            host_name = host_object_name(manifest_objects, f.get("host_id"))
            host_ob = bpy.data.objects.get(host_name) if host_name is not None else None
            if host_ob is not None and host_ob.type == "MESH":
                depsgraph = bpy.context.evaluated_depsgraph_get()
                point, escapes, moved = free_light_point(host_ob, depsgraph, f["light"]["center"],
                                                         float(f["light"].get("radius_m") or 0.05),
                                                         f.get("escape_low_z"))
                f["light"]["center"] = [round(float(v), 4) for v in point]
                escape = {"host_object": host_name, "escapes": bool(escapes), "moved_m": moved}
                if not escapes:
                    assumed.append({"object": f"{f['name']}_light", "field": "rig_light_escape", "value": None,
                                    "reason": f"{room['id']}: the rig light of {f['name']} is enclosed by its host "
                                              f"{f.get('host_id')} ({host_name}): no free point down to "
                                              f"{f.get('escape_low_z')}; check the model",
                                    "parent": room["id"], "kind": "rig_light_enclosed"})
            else:
                escape = {"host_object": None, "escapes": None, "moved_m": 0.0}
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
                        f["temperature_k"], "visible_camera": False, "reason": f["reason"], "lumens": f.get("lumens"),
                        "bulbs": f.get("bulbs", 1), "mesh": f.get("mesh") is not False, "host_id": f.get("host_id"),
                        "mount": f.get("mount"), "light_where": f.get("light_where"), "escape": escape},
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
            openings = room_openings(room, polygon, building)
            windows = [o for o in openings if o["type"] == "window" and daylight_window(o, walls_by_id, flagged)]
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
                # fix round after P4a: the built decor (hosts, the mirror under the mirror light), the doors and
                # windows (no sconce on them) and the sloped ceiling at each fixture
                ceiling_fn = None if ceiling_at is None else (lambda x, y, _lv=level: float(ceiling_at(_lv, x, y)))
                # fix round after P4b: the built method of each piece (a library lamp keeps the light in its shade)
                plan = rig_plan(room, pieces, room_floor, room_ceil, holes=voids, lighting=lighting,
                                agent_factor=factor, decor=built_decor_boxes(manifest_objects, room["id"]),
                                openings=openings, ceiling_fn=ceiling_fn,
                                piece_methods=built_piece_methods(manifest_objects))
                built = build_room_rig(bpy, common, collection, manifest_objects, assumed, room, level, plan,
                                       fixture_material)
                rig_lights.extend(built)
                # fix round after P3: only a rig with a ceiling fixture replaces the fill light (rig_replaces_fill);
                # bedside lamps or a pendant add to it (P3: r_L0_yatak_odasi_4 night-dark under two bedside lamps)
                replaces = bool(built) and rig_replaces_fill(plan, why)
                adds = bool(built) and why is not None and not replaces
                rig_rooms[room["id"]] = {"fixtures": [f["name"] for f in plan["fixtures"]],
                                         "dropped": plan["dropped"], "replaces_fill_light": replaces,
                                         "adds_to_fill_light": adds, "fill_light_reason": why}
                if replaces:
                    assumed.append({"object": f"rig_{room['id']}", "field": "area_light", "value": None,
                                    "reason": f"{room['id']}: {why}; the room's light rig ({len(built)} fixtures) "
                                              f"carries the light instead of the invisible ceiling light",
                                    "parent": room["id"], "kind": "rig_replaces_fill_light"})
                    continue
                if adds:
                    assumed.append({"object": f"rig_{room['id']}", "field": "area_light", "value": None,
                                    "reason": f"{room['id']}: {why}; the room's light rig ({len(built)} fixtures) has "
                                              f"no ceiling fixture, so it adds to the invisible ceiling light",
                                    "parent": room["id"], "kind": "rig_adds_to_fill_light"})
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
                    "temperature_k_by_type": {t: rig_temperature_for(t, lighting) for t in sorted(ROOM_RIGS)},
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
